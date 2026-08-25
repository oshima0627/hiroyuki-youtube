#!/usr/bin/env python3
"""複数の配信から束ねた1本をビルドする。tora-kirinuki の build_clip.py に相当。

  python scripts/build_episode.py recipes/<id>.json --dry-run
  python scripts/build_episode.py recipes/<id>.json

出力は work/<id>/ に video.mp4 / thumb.png / description.txt / meta.json。

tora は1本の配信から連続した1区間を切るだけだったので、切り出しと
オーバーレイを1回のエンコードで済ませられた。こちらは元動画が複数あるので、
**クリップごとにエンコードしてから concat する。**

tora で学んだことは持ち込んである。

  - カードを前後に連結せず本編に重ねる（冒頭が無音の止め絵になるのを避ける）
  - オーバーレイは1クリップにつき1回のエンコードにまとめる
  - -t は出力側に置く（入力の -i のあいだに書くと後続のPNG入力に掛かる）
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fetch_clips import clip_path  # noqa: E402
from scripts.fetch_source import source_dir  # noqa: E402
from scripts.narration import duration as wav_duration  # noqa: E402
from scripts.narration import synth  # noqa: E402
from scripts.recipe import build_description, validate  # noqa: E402
from scripts.telop import (  # noqa: E402
    render_lower_third, render_note, render_top_bar_slim)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"

W, H, FPS = 1920, 1080, 30
TELOP_SEC = 6.0          # 見出し帯を出しておく秒数
DUR_TOLERANCE = 1.5      # concat の丸めがあるので tora より緩い


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True)


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def resolve_source(clip: dict, pad: float) -> tuple[Path, float] | None:
    """使う素材と、その中での開始位置を返す。

    区間ファイル（fetch_clips.py）があればそれを使う。全編を落とすと
    1本4〜8GBになるので、通常はこちら。**区間ファイルは先頭が0秒**で、
    欲しい区間は pad 秒めから始まる。
    """
    cp = clip_path(clip["video_id"], clip["start"], clip["end"])
    if cp.exists():
        return cp, pad
    full = source_dir(clip["video_id"]) / "source.mp4"
    if full.exists():
        return full, clip["start"]
    return None


def preflight(recipe: dict, pad: float) -> list[str]:
    """素材の実在をまとめて確認する。何が足りないかを先に全部出す。"""
    validate(recipe)

    missing = []
    for i, c in enumerate(recipe["clips"]):
        if resolve_source(c, pad) is None:
            missing.append(
                f"clips[{i}] {c['video_id']} {int(c['start'])}-{int(c['end'])} の素材が無い"
                f"（python scripts/fetch_clips.py <recipe>）")
            continue
        meta = source_dir(c["video_id"]) / "meta.json"
        if meta.exists():
            dur = json.loads(meta.read_text(encoding="utf-8")).get("duration_sec")
            if dur and c["end"] > dur:
                missing.append(
                    f"clips[{i}] end={c['end']} が元動画の尺 {dur} を超えている")
    return missing


def build_clip(clip: dict, index: int, out_dir: Path, pad: float) -> Path:
    """1クリップを切り出して見出し帯を焼き込む。"""
    resolved = resolve_source(clip, pad)
    if resolved is None:
        raise SystemExit(f"! clips[{index}] の素材が無い")
    src, offset = resolved
    length = clip["end"] - clip["start"]

    # 見出し帯には**タイトルだけ**を出す。解説は直後の解説板で読み上げるので、
    # ここにも書くと同じ文が二度出て画面が重くなる
    png = out_dir / f"telop_{index:02d}.png"
    render_lower_third(clip["title"], None, index=f"{index + 1:02d}").save(png)

    # 6秒を過ぎたら細い帯に差し替えて出し続ける。**カスタムサムネイルが
    # 403 で使えないので、本編のフレームがそのままサムネイルになる。**
    # 帯が冒頭だけだと、自動生成の候補に文字が入るかどうかが運になる
    slim = out_dir / f"telopslim_{index:02d}.png"
    render_top_bar_slim(clip["title"], index=f"{index + 1:02d}").save(slim)

    dst = out_dir / f"part_{index:02d}.mp4"
    _run(["ffmpeg", "-y", "-loglevel", "error",
          "-ss", f"{offset}", "-i", str(src),
          "-i", str(png), "-i", str(slim),
          "-t", f"{length}",
          "-filter_complex",
          f"[0:v]scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,fps={FPS}[v];"
          f"[v][1:v]overlay=0:0:enable='between(t,0,{TELOP_SEC})'[o1];"
          f"[o1][2:v]overlay=0:0:enable='gt(t,{TELOP_SEC})'[o]",
          "-map", "[o]", "-map", "0:a",
          "-c:v", "libx264", "-preset", "medium", "-crf", "20",
          "-pix_fmt", "yuv420p",
          "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
          str(dst)])
    return dst


TAIL_SEC = 0.6           # 読み終わってから次のカットに移るまでの間
HEAD_SEC = 2.5           # 冒頭に置くサムネカードの秒数


def build_head(thumb: Path, out_dir: Path) -> Path:
    """サムネイルを冒頭に静止画として置く。

    **これだけでは YouTube の自動サムネイルにはならない。** 自動生成の候補は
    動画のおよそ25%・50%・75%地点から作られるので、0秒地点は選ばれない。
    それでも冒頭に置くのは、視聴者に何の動画かを最初の2秒で示せるから。
    """
    dst = out_dir / "part_head.mp4"
    _run(["ffmpeg", "-y", "-loglevel", "error",
          "-loop", "1", "-i", str(thumb),
          "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
          "-t", f"{HEAD_SEC}",
          "-vf", f"scale={W}:{H}:force_original_aspect_ratio=decrease,"
                 f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=0x0E1116,fps={FPS}",
          "-c:v", "libx264", "-preset", "medium", "-crf", "20",
          "-pix_fmt", "yuv420p",
          "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
          str(dst)])
    return dst


def clip_notes(clip: dict) -> list[str]:
    """クリップの解説文を並べて返す。

    `notes`（配列）があればそれを、無ければ `note`（単数）を1枚として扱う。
    **既存のレシピを壊さないための後方互換。** 総集編のレシピは全部 note 単数で書いてある。
    """
    notes = clip.get("notes")
    if notes:
        return [str(t).strip() for t in notes if str(t).strip()]
    note = (clip.get("note") or "").strip()
    return [note] if note else []


def note_is_current(text: str, index: int, out_dir: Path, kind: str = "note") -> bool:
    """その解説板が今の文章で作られているか。

    **--concat-only が古いパーツを使い回して事故った**（2026-08-14）。
    まとめの文言を直したのに、ファイルが在るというだけで再生成されず、
    古い読み上げのまま連結された。何を元に作ったかを横に置いて突き合わせる。
    """
    mp4 = out_dir / f"{kind}img_{index:02d}.mp4"
    src = out_dir / f"{kind}img_{index:02d}.txt"
    return (mp4.exists() and src.exists()
            and src.read_text(encoding="utf-8") == text.strip())


def build_note(text: str, index: int, out_dir: Path, kind: str = "note") -> Path:
    """解説板を作る。静止画＋VOICEVOX の読み上げ。

    **ここが「再利用されたコンテンツ」対策の本体。** テロップだけだったときは
    独自要素が 873秒中60秒（6.9%）しかなく、審査担当が数カ所サンプリングしたら
    高い確率で素の映像に当たる状態だった。音声解説を独立した区間として挟むと、
    元配信には存在しない区間が構造として分離される。
    """
    wav = synth(text)
    length = wav_duration(wav) + TAIL_SEC

    png = out_dir / f"{kind}_{index:02d}.png"
    render_note(text).save(png)

    dst = out_dir / f"{kind}img_{index:02d}.mp4"
    _run(["ffmpeg", "-y", "-loglevel", "error",
          "-loop", "1", "-i", str(png), "-i", str(wav),
          "-t", f"{length}",
          "-vf", f"scale={W}:{H},fps={FPS}",
          "-c:v", "libx264", "-preset", "medium", "-crf", "20",
          "-pix_fmt", "yuv420p",
          # 本編と同じ音声パラメータにしないと concat -c copy が通らない
          "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
          str(dst)])
    (out_dir / f"{kind}img_{index:02d}.txt").write_text(
        text.strip(), encoding="utf-8")
    return dst


def build(recipe_path: Path, dry_run: bool = False, pad: float = 2.0,
          concat_only: bool = False) -> Path:
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))

    missing = preflight(recipe, pad)
    if missing:
        for m in missing:
            print(f"! {m}")
        raise SystemExit("素材が足りないので中断する")

    clips = recipe["clips"]
    total = sum(c["end"] - c["start"] for c in clips)
    out = WORK / recipe["id"]

    if dry_run:
        print(f"[dry-run] {recipe['id']}  {recipe['title']}")
        srcs = {c["video_id"] for c in clips}
        for i, c in enumerate(clips):
            print(f"  {i + 1:2d}. [{c['video_id']}] "
                  f"{c['start']:.0f}-{c['end']:.0f}s "
                  f"({c['end'] - c['start']:.0f}s)  {c['title'][:44]}")
        print(f"  合計 {int(total) // 60}:{int(total) % 60:02d} / "
              f"元動画 {len(srcs)}本")
        if total < 780:
            print("  ! 13分未満。この市場の相場は13〜20分")
        return out

    out.mkdir(parents=True, exist_ok=True)

    # 本編 → 解説板 → 本編 → 解説板 … の順に並べる。
    # --concat-only は既にあるパーツを使い回して連結だけやり直す。
    # サムネを冒頭に足すためだけに10分以上かけて再エンコードしないため
    parts: list[Path] = []
    for i, c in enumerate(clips):
        pc = out / f"part_{i:02d}.mp4"
        parts.append(pc if (concat_only and pc.exists())
                     else build_clip(c, i, out, pad))
        for j, text in enumerate(clip_notes(c)):
            # 解説板は1クリップに複数枚置ける。**検索語で束ねる回で必要になる。**
            # 1問あたりの素材は1分前後しかないので（2026-08-25 実測、43〜118秒）、
            # 板が1枚だと本編の9割が素材そのままになり、「再利用されたコンテンツ」
            # 判定にとって総集編より悪い比率になる。
            # 添字は 100*i+j。単数 note のときは j=0 なので従来と同じ番号になり、
            # --concat-only の作り置きがそのまま効く。
            idx = i if j == 0 else 100 * (i + 1) + j
            pn = out / f"noteimg_{idx:02d}.mp4"
            parts.append(pn if (concat_only and note_is_current(text, idx, out))
                         else build_note(text, idx, out))
    if recipe.get("summary"):
        ps = out / "summaryimg_99.mp4"
        parts.append(
            ps if (concat_only and note_is_current(recipe["summary"], 99, out, "summary"))
            else build_note(recipe["summary"], 99, out, kind="summary"))

    # サムネイルがあれば冒頭に置く。thumbnail.py は本編から1枚抜くので、
    # 初回ビルドの時点ではまだ無い。作ったあと --concat-only で足す
    thumb = out / "thumb.png"
    if thumb.exists():
        parts.insert(0, build_head(thumb, out))
    else:
        print("- thumb.png がまだ無いので冒頭カードは入れません"
              "（thumbnail.py のあと --concat-only で足せます）")

    listing = out / "parts.txt"
    listing.write_text(
        "\n".join(f"file '{p.name}'" for p in parts) + "\n", encoding="utf-8")
    video = out / "video.mp4"
    _run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
          "-i", str(listing), "-c", "copy", str(video)])

    # 解説板を挟むので、期待尺は本編の合計ではなく各パートの合計で見る
    expected = sum(probe_duration(p) for p in parts)
    actual = probe_duration(video)
    if abs(actual - expected) > DUR_TOLERANCE:
        raise SystemExit(f"! 尺が合わない: 期待 {expected:.1f}s / 実測 {actual:.1f}s")

    # 目次は解説板のぶんもずれるので、実測の尺から積む
    # 冒頭カードがあるぶんだけ本編の位置がずれる
    head = 1 if parts and parts[0].name == "part_head.mp4" else 0
    offsets, t = [], 0.0
    for i, p in enumerate(parts):
        if i >= head and (i - head) % 2 == 0:      # 本編は偶数番
            offsets.append(t)
        t += probe_duration(p)

    (out / "description.txt").write_text(
        build_description(recipe, offsets), encoding="utf-8")
    (out / "meta.json").write_text(json.dumps({
        "id": recipe["id"],
        "title": recipe["title"],
        "tags": recipe.get("tags") or [],
        "category_id": recipe.get("category_id", "22"),
        "privacy_status": recipe.get("privacy_status", "private"),
        "expected_channel_id": recipe["expected_channel_id"],
        "sources": sorted({c["video_id"] for c in clips}),
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    if actual > 15 * 60:
        print(f"! 尺が {int(actual) // 60}:{int(actual) % 60:02d}。"
              "電話番号が未確認のチャンネルは15分超を上げられません（上げると削除されます）")
    print(f"✓ {video}  {int(actual) // 60}:{int(actual) % 60:02d}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("recipe", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pad", type=float, default=2.0,
                    help="fetch_clips.py で付けた余白と同じ値にすること")
    ap.add_argument("--concat-only", action="store_true",
                    help="既存のパーツを使い回して連結だけやり直す")
    a = ap.parse_args()
    build(a.recipe, a.dry_run, a.pad, a.concat_only)


if __name__ == "__main__":
    main()
