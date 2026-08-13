#!/usr/bin/env python3
"""描画の共通部品。tora-kirinuki からの移植。

配色だけ差し替えた。tora は白地に赤（令和の虎の意匠を避けるため）だったが、
こちらは元配信が夜の室内で暗いので、暗い帯に白抜きのほうが乗る。

**ひろゆき本人の肖像やロゴを図案に使わない。** 黙認の対象は配信の素材であって、
本人を想起させる意匠を自作してよいという話ではない。図案はすべて文字で作る。
"""

from __future__ import annotations

from pathlib import Path

from PIL import ImageDraw, ImageFont

FONT_SANS = [
    r"C:\Windows\Fonts\YuGothB.ttc",
    r"C:\Windows\Fonts\meiryob.ttc",
    r"C:\Windows\Fonts\msgothic.ttc",
]

INK = (14, 17, 22)          # 帯の地
RED = (226, 60, 60)         # アクセント
GOLD = (255, 211, 77)       # 解説行
WHITE = (255, 255, 255)
MUTED = (154, 163, 174)


def pick_font(size: int) -> ImageFont.FreeTypeFont:
    for p in FONT_SANS:
        if Path(p).exists():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def fit_font(draw: ImageDraw.ImageDraw, text: str, max_w: int,
             start: int) -> ImageFont.FreeTypeFont:
    """幅に収まる最大サイズのフォントを返す。"""
    size = start
    while size > 14:
        f = pick_font(size)
        b = draw.textbbox((0, 0), text, font=f)
        if b[2] - b[0] <= max_w:
            return f
        size -= 2
    return pick_font(14)


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
         max_w: int) -> list[str]:
    """日本語は単語境界が無いので、幅を見て1文字ずつ折り返す。"""
    lines, cur = [], ""
    for ch in text:
        b = draw.textbbox((0, 0), cur + ch, font=font)
        if b[2] - b[0] > max_w and cur:
            lines.append(cur)
            cur = ch
        else:
            cur += ch
    if cur:
        lines.append(cur)
    return lines
