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
from scripts.recipe import build_description, validate  # noqa: E402
from scripts.telop import render_lower_third  # noqa: E402

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

    png = out_dir / f"telop_{index:02d}.png"
    render_lower_third(clip["title"], clip.get("note"),
                       index=f"{index + 1:02d}").save(png)

    dst = out_dir / f"part_{index:02d}.mp4"
    _run(["ffmpeg", "-y", "-loglevel", "error",
          "-ss", f"{offset}", "-i", str(src),
          "-i", str(png),
          "-t", f"{length}",
          "-filter_complex",
          f"[0:v]scale={W}:{H}:force_original_aspect_ratio=decrease,"
          f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color=black,fps={FPS}[v];"
          f"[v][1:v]overlay=0:0:enable='between(t,0,{TELOP_SEC})'[o]",
          "-map", "[o]", "-map", "0:a",
          "-c:v", "libx264", "-preset", "medium", "-crf", "20",
          "-pix_fmt", "yuv420p",
          "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
          str(dst)])
    return dst


def build(recipe_path: Path, dry_run: bool = False, pad: float = 2.0) -> Path:
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
    parts = [build_clip(c, i, out, pad) for i, c in enumerate(clips)]

    listing = out / "parts.txt"
    listing.write_text(
        "\n".join(f"file '{p.name}'" for p in parts) + "\n", encoding="utf-8")
    video = out / "video.mp4"
    _run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
          "-i", str(listing), "-c", "copy", str(video)])

    actual = probe_duration(video)
    if abs(actual - total) > DUR_TOLERANCE:
        raise SystemExit(f"! 尺が合わない: 期待 {total:.1f}s / 実測 {actual:.1f}s")

    (out / "description.txt").write_text(build_description(recipe), encoding="utf-8")
    (out / "meta.json").write_text(json.dumps({
        "id": recipe["id"],
        "title": recipe["title"],
        "tags": recipe.get("tags") or [],
        "category_id": recipe.get("category_id", "22"),
        "privacy_status": recipe.get("privacy_status", "private"),
        "expected_channel_id": recipe["expected_channel_id"],
        "sources": sorted({c["video_id"] for c in clips}),
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"✓ {video}  {int(actual) // 60}:{int(actual) % 60:02d}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("recipe", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pad", type=float, default=2.0,
                    help="fetch_clips.py で付けた余白と同じ値にすること")
    a = ap.parse_args()
    build(a.recipe, a.dry_run, a.pad)


if __name__ == "__main__":
    main()
