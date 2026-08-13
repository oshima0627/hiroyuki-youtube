#!/usr/bin/env python3
"""解説テロップの描画。tora-kirinuki の cards.py に相当する。

tora は「案件カード（希望金額・事業内容）」「論点カード」「判定カード」という
令和の虎の構造に紐づいた図解だった。ひろゆきにはその構造が無いので作り直した。

代わりに置くのは2層。

  見出し帯   その区間で何の話をしているか（GCDの公式トピック名をそのまま使える）
  解説行     **元の配信に無い情報。** ここが「再利用されたコンテンツ」判定を
             避ける根拠になる。要約や言い換えを書いても付加価値にならない

**元動画は画面下部にテロップを焼き込んでいない**（ひろゆきの配信は素の画面）ので
下に置ける。令和の虎は下に大きなテロップが常時出ていて上に逃がす必要があった。
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from scripts.draw import GOLD, INK, MUTED, RED, WHITE, fit_font, pick_font, wrap

W, H = 1920, 1080

BAR_H = 168           # 見出し帯の高さ
BAR_Y = H - BAR_H - 48
PAD = 64


def render_lower_third(title: str, note: str | None = None,
                       index: str | None = None) -> Image.Image:
    """下三分の一に置く見出し帯。透過PNGを返す（本編に重ねる）。"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    d.rectangle([0, BAR_Y, W, BAR_Y + BAR_H], fill=(*INK, 225))
    d.rectangle([0, BAR_Y, W, BAR_Y + 6], fill=(*RED, 255))

    x = PAD
    if index:
        f = pick_font(40)
        d.text((x, BAR_Y + 30), index, font=f, fill=(*RED, 255))
        x += d.textbbox((0, 0), index, font=f)[2] + 28

    ft = fit_font(d, title, W - x - PAD, 60)
    d.text((x, BAR_Y + 26), title, font=ft, fill=(*WHITE, 255))

    if note:
        fn = pick_font(36)
        lines = wrap(d, note, fn, W - x - PAD)[:1]
        d.text((x, BAR_Y + 100), lines[0], font=fn, fill=(*GOLD, 255))
    return img


def render_note(note: str) -> Image.Image:
    """解説だけを大きく出す板。区間の切れ目に短く挟む用。"""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(*INK, 214))
    d.rectangle([PAD, 300, PAD + 8, 300 + 220], fill=(*RED, 255))

    f = pick_font(54)
    lines = wrap(d, note, f, W - PAD * 2 - 40)[:4]
    y = 300
    for ln in lines:
        d.text((PAD + 40, y), ln, font=f, fill=(*WHITE, 255))
        y += 74

    fs = pick_font(30)
    d.text((PAD + 40, y + 24), "※この解説は編集側による補足です",
           font=fs, fill=(*MUTED, 255))
    return img
