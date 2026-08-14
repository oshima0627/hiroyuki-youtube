#!/usr/bin/env python3
"""解説テロップの描画。tora-kirinuki の cards.py に相当する。

tora は「案件カード（希望金額・事業内容）」「論点カード」「判定カード」という
令和の虎の構造に紐づいた図解だった。ひろゆきにはその構造が無いので作り直した。

代わりに置くのは2層。

  見出し帯   その区間で何の話をしているか（GCDの公式トピック名をそのまま使える）
  解説行     **元の配信に無い情報。** ここが「再利用されたコンテンツ」判定を
             避ける根拠になる。要約や言い換えを書いても付加価値にならない

## 帯は画面の上に出す

最初に下三分の一に置いたが、実ビルドで確認したら**スパチャのカードと重なった**。
ひろゆきの配信は素の画面だと思い込んでいたのが誤りで、スクリーンショット1枚で
判断していた。実際にはカードが画面下部の2〜3割を占め、回によって高さも違う。

**そのカードには質問文が載っている。** 視聴者が課金して質問し、その本文が
表示される仕組みなので、隠すと何の話か分からなくなる。避けて上に置く。

結果として tora-kirinuki が令和の虎で得た結論と同じになった
（「論点カードは画面の上部に出す。下部に大きなテロップが常時あるとぶつかる」）。
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from scripts.draw import GOLD, INK, MUTED, RED, WHITE, fit_font, pick_font, wrap

W, H = 1920, 1080

BAR_H = 218           # 見出し帯の高さ。解説を2行ぶん入れる
BAR_Y = 40            # **上に置く。** 下はスパチャのカードが占有している
PAD = 64


def render_lower_third(title: str, note: str | None = None,
                       index: str | None = None) -> Image.Image:
    """画面上部に置く見出し帯。透過PNGを返す（本編に重ねる）。"""
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
        # 1行しか描いておらず、実ビルドで解説が途中で切れていた（2026-08-14）。
        # 解説は付加価値の本体なので、途中で切れるのは中身が無いのと同じ
        fn = pick_font(36)
        for i, ln in enumerate(wrap(d, note, fn, W - x - PAD)[:2]):
            d.text((x, BAR_Y + 100 + i * 50), ln, font=fn, fill=(*GOLD, 255))
    return img


MAX_TEXT_H = 720          # 板に使ってよい縦幅


def render_note(note: str) -> Image.Image:
    """解説だけを大きく出す板。区間の切れ目に挟む。

    **文字を切り捨ててはいけない。** ナレーションは全文を読むので、画面だけ
    途中で切れると音と表示がずれる。実際にまとめ（183文字）が4行で切れて
    「相手を変えるのは成功」で止まった（2026-08-14）。
    行数を固定せず、全文が収まるまでフォントを縮める。
    """
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, H], fill=(*INK, 214))

    size = 54
    while size > 24:
        f = pick_font(size)
        lines = wrap(d, note, f, W - PAD * 2 - 40)
        lh = int(size * 1.38)
        if len(lines) * lh <= MAX_TEXT_H:
            break
        size -= 4
    else:
        f, lines, lh = pick_font(24), wrap(d, note, pick_font(24), W - PAD * 2 - 40), 34

    block = len(lines) * lh
    y = top = (H - block) // 2
    d.rectangle([PAD, top, PAD + 8, top + block], fill=(*RED, 255))

    for ln in lines:
        d.text((PAD + 40, y), ln, font=f, fill=(*WHITE, 255))
        y += lh

    fs = pick_font(30)
    d.text((PAD + 40, y + 24), "※この解説は編集側による補足です",
           font=fs, fill=(*MUTED, 255))
    return img
