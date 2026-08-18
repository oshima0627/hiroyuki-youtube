#!/usr/bin/env python3
"""指定した秒のフレームを抜いて、秒を焼き込んだ一覧画像にする。

  python scripts/contact_sheet.py work/<id>/video.mp4 sheet.png 40 80 110 150

**冒頭カードのフレームを目で選ぶための道具。** `thumbnail.py` の顔スコアに
よる自動選択は外すことがあり、EP006（`Di-K-jhqgMg`）では後頭部のフレームを
選んだ。良い秒をここで読んで、レシピの `thumb.at` に書く。

**`ffmpeg -vf fps=1/N,tile=...` で一覧を作ってはいけない。** タイルの並びと
`drawtext` で焼いた時刻がずれて、実際とは違う秒を読む（2026-08-17 に実際に
二度外した）。`-ss <秒> -i` で1枚ずつ抜けば、その秒のフレームだと確実に言える。
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CW, CH = 480, 270
COLS = 4


def main() -> None:
    if len(sys.argv) < 4:
        raise SystemExit("usage: contact_sheet.py <video> <out.png> <秒> [秒 ...]")
    video, out = sys.argv[1], sys.argv[2]
    times = [float(t) for t in sys.argv[3:]]

    font = ImageFont.truetype("C:/Windows/Fonts/arialbd.ttf", 34)
    tmp = Path(tempfile.mkdtemp())
    tiles = []
    for t in times:
        p = tmp / f"{int(t)}.png"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(t),
                        "-i", video, "-frames:v", "1", str(p)], check=True)
        im = Image.open(p).convert("RGB").resize((CW, CH))
        d = ImageDraw.Draw(im)
        d.rectangle([0, 0, 210, 44], fill=(0, 0, 0))
        d.text((8, 4), f"{int(t) // 60}:{int(t) % 60:02d} ({int(t)}s)",
               font=font, fill=(255, 220, 0))
        tiles.append(im)

    rows = (len(tiles) + COLS - 1) // COLS
    sheet = Image.new("RGB", (CW * COLS, CH * rows), (20, 20, 20))
    for i, im in enumerate(tiles):
        sheet.paste(im, (CW * (i % COLS), CH * (i // COLS)))
    sheet.save(out)
    print(f"✓ {out}  {len(tiles)}枚")


if __name__ == "__main__":
    main()
