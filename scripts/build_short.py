#!/usr/bin/env python3
"""ショート（縦型）をビルドする。長尺と同じレシピから作る。

  python scripts/build_short.py recipes/<id>.json --dry-run
  python scripts/build_short.py recipes/<id>.json

出力は work/<id>-short/ に video.mp4 / description.txt / meta.json。

レシピの short ブロックを見る。

  "short": {
    "clip": 7,                      どのクリップを使うか（長尺の clips の添字）
    "start": 12.0, "end": 74.0,     そのクリップの中での秒。省略すると全体
    "hook": "その給料、転職先では出ません",
    "footer": "本編では仕事の相談9件に答えています"
  }

## tora-kirinuki の実測をそのまま持ち込む

  尺は60〜70秒。伸びている競合は22〜73秒で、103秒・132秒のものは0〜2再生だった
  hook は必須。縦型は冒頭2秒で離脱が決まる
  縦にトリミングして顔を大きくする。映像の占有率は伸びない原因ではなかったが、
  小さい顔で見せる理由も無い

## ひろゆき固有の事情

**画面下のスパチャのカードは切り落とす。** カードには質問文が載っているが、
縦型の小さい画面では読めないし、上下に文字を置く場所を取られる。
hook で何の話かを示すほうが速い。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.build_episode import resolve_source  # noqa: E402
from scripts.draw import GOLD, INK, RED, WHITE, fit_font, pick_font, wrap  # noqa: E402
from scripts.recipe import CREDIT, validate_short  # noqa: E402
from scripts.thumbnail import auto_crop  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"

W, H, FPS = 1080, 1920, 30
VIDEO_H = 1080           # 中央に置く映像の高さ（正方形に切る）
VIDEO_Y = (H - VIDEO_H) // 2
PAD = 56


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True)


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def render_frame(hook: str, footer: str) -> Image.Image:
    """上にフック、下に補足を置いた透過PNG。映像の上下に重なる。"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    d.rectangle([0, 0, W, VIDEO_Y], fill=(*INK, 255))
    d.rectangle([0, VIDEO_Y + VIDEO_H, W, H], fill=(*INK, 255))
    d.rectangle([0, VIDEO_Y - 6, W, VIDEO_Y], fill=(*RED, 255))
    d.rectangle([0, VIDEO_Y + VIDEO_H, W, VIDEO_Y + VIDEO_H + 6], fill=(*RED, 255))

    f_label = pick_font(34)
    d.text((PAD, 44), "ひろゆき切り抜き＋解説", font=f_label, fill=(*RED, 255))

    # フックは冒頭2秒で読ませる。1行に収まらないなら折る
    fh = pick_font(76)
    lines = wrap(d, hook, fh, W - PAD * 2)[:3]
    if len(lines) > 2:
        fh = pick_font(62)
        lines = wrap(d, hook, fh, W - PAD * 2)[:3]
    y = VIDEO_Y - 40 - len(lines) * int(fh.size * 1.3)
    for ln in lines:
        d.text((PAD + 3, y + 3), ln, font=fh, fill=(0, 0, 0, 255))
        d.text((PAD, y), ln, font=fh, fill=(*WHITE, 255))
        y += int(fh.size * 1.3)

    if footer:
        ff = pick_font(44)
        fl = wrap(d, footer, ff, W - PAD * 2)[:2]
        y = VIDEO_Y + VIDEO_H + 60
        for ln in fl:
            d.text((PAD, y), ln, font=ff, fill=(*GOLD, 255))
            y += 58

    fn = pick_font(28)
    d.text((PAD, H - 90), "公式チャンネルではありません", font=fn, fill=(150, 158, 168, 255))
    return img


def build(recipe_path: Path, dry_run: bool = False, pad: float = 2.0) -> Path:
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    short = recipe.get("short") or {}
    idx = short.get("clip", 0)
    clip = recipe["clips"][idx]

    length_all = clip["end"] - clip["start"]
    s = float(short.get("start", 0.0))
    e = float(short.get("end", length_all))
    # validate_short は絶対時刻を見るので、切り出し後の尺で渡す
    warnings = validate_short({"short": {"start": 0.0, "end": e - s,
                                         "hook": short.get("hook", "")}})
    for w in warnings:
        print(f"! {w}")

    resolved = resolve_source(clip, pad)
    if resolved is None:
        raise SystemExit(f"! clips[{idx}] の素材が無い。fetch_clips.py を先に")
    src, offset = resolved

    out = WORK / f"{recipe['id']}-short"
    if dry_run:
        print(f"[dry-run] {recipe['id']}-short")
        print(f"  クリップ{idx}「{clip['title']}」の {s:.0f}〜{e:.0f}秒")
        print(f"  尺 {e - s:.0f}秒 / フック「{short.get('hook')}」")
        return out

    out.mkdir(parents=True, exist_ok=True)

    # 顔の位置を測って正方形に切る。手で係数を触ると必ずずれる
    probe_png = out / "_probe.png"
    _run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{offset + s + 3}",
          "-i", str(src), "-frames:v", "1", str(probe_png)])
    frame = Image.open(probe_png).convert("RGB")
    fw, fh_ = frame.size
    cl, ct, chh = auto_crop(frame, margin=0.35)
    ch = int(fh_ * chh)
    cw = ch                                    # 正方形
    cx = int(fw * cl) + int(ch * 560 / 720) // 2
    x0 = max(0, min(fw - cw, cx - cw // 2))
    y0 = max(0, min(fh_ - ch, int(fh_ * ct)))
    print(f"  切り出し {cw}x{ch} @ ({x0},{y0}) / 拡大 {VIDEO_H / ch:.2f}倍")

    png = out / "frame.png"
    render_frame(short.get("hook", ""), short.get("footer", "")).save(png)

    video = out / "video.mp4"
    _run(["ffmpeg", "-y", "-loglevel", "error",
          "-ss", f"{offset + s}", "-i", str(src),
          "-i", str(png),
          "-t", f"{e - s}",
          "-filter_complex",
          f"[0:v]crop={cw}:{ch}:{x0}:{y0},scale={W}:{VIDEO_H},"
          f"pad={W}:{H}:0:{VIDEO_Y}:color=0x0E1116,fps={FPS}[v];"
          f"[v][1:v]overlay=0:0[o]",
          "-map", "[o]", "-map", "0:a",
          "-c:v", "libx264", "-preset", "medium", "-crf", "20",
          "-pix_fmt", "yuv420p",
          "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
          str(video)])

    actual = probe_duration(video)
    tags = list(recipe.get("tags") or []) + ["Shorts"]
    desc = "\n".join([
        short.get("hook", ""), "",
        "▼この回をフルで見る",
        "（長尺のURLはアップロード時に差し込まれます）", "",
        f"【元動画】{clip.get('video_title', '')}",
        clip.get("video_url", ""), "",
        CREDIT, "",
        " ".join(f"#{t}" for t in tags),
    ]).strip() + "\n"
    (out / "description.txt").write_text(desc, encoding="utf-8")
    (out / "meta.json").write_text(json.dumps({
        "id": f"{recipe['id']}-short",
        "title": short.get("title") or short.get("hook", "")[:100],
        "tags": tags,
        "category_id": recipe.get("category_id", "22"),
        "privacy_status": "private",
        "expected_channel_id": recipe["expected_channel_id"],
        "sources": [clip["video_id"]],
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"✓ {video}  {actual:.0f}秒  {W}x{H}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("recipe", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pad", type=float, default=2.0)
    a = ap.parse_args()
    build(a.recipe, a.dry_run, a.pad)


if __name__ == "__main__":
    main()
