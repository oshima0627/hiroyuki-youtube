#!/usr/bin/env python3
"""チャンネルのバナーとアイコンを作る。

  python scripts/brand_art.py --all        # 3案を brand/ に出す
  python scripts/brand_art.py --variant a

## 競合の実測（2026-08-19、YouTube Data API で実物を取得）

| チャンネル | 登録 | バナー | アイコン |
| --- | --- | --- | --- |
| ひろゆけ | 31.3万 | 白帯に黒縁白文字＋本人の写真 | **黒地に白文字4字**「ひろゆけ」2行 |
| ひろゆきまとめ | 9.0万 | **黄一色に黒文字2行** | **黄丸に黒文字4字**「ひろまと」2行 |
| 本人 | 165万 | 海辺の写真 | イラスト（顔ではない） |

**主要な競合はどちらもアイコンに顔を使っていない。** 文字だけ・4字・2行で
揃っている。48〜98pxで表示されるので、それ以上入れても読めないからだと思われる。
本人チャンネルすら顔を使っていない。**顔を使わないことは不利ではない。**

肖像を避けられるなら避けたほうがいい。権利者の立場は黙認であって、
チャンネルの看板に本人を出すのは「公式に見せない」という条件に近づきすぎる。

## 差別化は「解説」に置く

競合2社はどちらも素の切り抜きで、バナーに書いてあるのは「切り抜き」だけ。
こちらは解説板とナレーションを足している（独自性18%）。そこを看板に出す。

## 寸法

バナーは 2048x1152 で作り、**中央 1235x338 の安全域**にだけ文字を置く。
その外はテレビでしか出ない。デスクトップは 2048x423、タブレットは 1855x423。

アイコンは 800x800 だが **YouTube は円に切る。** 内接円からさらに内側に
収める（実効 570x570 程度）。四隅に文字を置くと切られる。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.draw import GOLD, INK, RED, WHITE, pick_font  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "brand"

BW, BH = 2048, 1152
SAFE_W, SAFE_H = 1235, 338
SAFE_X, SAFE_Y = (BW - SAFE_W) // 2, (BH - SAFE_H) // 2
AV = 800

NAME = "ひろゆき解説ch"
SUB = "切り抜き＋解説"
NOTE = "毎日更新／公式チャンネルではありません"


def _center(d, text, font, cx, y, fill, shadow=None):
    w = d.textbbox((0, 0), text, font=font)[2]
    if shadow:
        d.text((cx - w // 2 + 4, y + 4), text, font=font, fill=shadow)
    d.text((cx - w // 2, y), text, font=font, fill=fill)
    return w


def banner(variant: str) -> Image.Image:
    bg, name_c, sub_c, note_c = {
        # 動画と同じ配色。帯・解説行の色をそのまま持ってくる
        "a": (INK, WHITE, GOLD, (150, 158, 168)),
        # ひろゆきまとめと同じ「一色べた」の型。ただし黄は取られているので赤
        "b": (RED, WHITE, (255, 226, 226), (255, 210, 210)),
        # 金地に黒。検索結果でいちばん目を引くが、動画の配色とは離れる
        "c": (GOLD, INK, (90, 60, 0), (120, 95, 30)),
    }[variant]

    img = Image.new("RGB", (BW, BH), bg)
    d = ImageDraw.Draw(img)
    cx = BW // 2

    if variant == "a":
        d.rectangle([0, SAFE_Y - 8, BW, SAFE_Y], fill=RED)
        d.rectangle([0, SAFE_Y + SAFE_H, BW, SAFE_Y + SAFE_H + 8], fill=RED)

    _center(d, NAME, pick_font(150), cx, SAFE_Y + 42, name_c,
            shadow=(0, 0, 0) if variant != "c" else None)
    _center(d, SUB, pick_font(74), cx, SAFE_Y + 208, sub_c)
    _center(d, NOTE, pick_font(34), cx, SAFE_Y + 292, note_c)
    return img


def avatar(variant: str) -> Image.Image:
    bg, fg, ring = {
        "a": (INK, WHITE, RED),
        "b": (RED, WHITE, WHITE),
        "c": (GOLD, INK, INK),
    }[variant]

    img = Image.new("RGB", (AV, AV), bg)
    d = ImageDraw.Draw(img)
    # 円に切られるので、縁は内接円のすぐ内側に置く
    d.ellipse([10, 10, AV - 10, AV - 10], outline=ring, width=12)

    # **文字は円いっぱいまで大きくする。** 最初 250px で作ったら、一覧での
    # 実寸48pxでは1文字20pxしかなく読めなかった（2026-08-19、48pxに縮めて確認）。
    # 競合の「ひろまと」は文字が直径の7割強を占めている。
    #
    # ただし**円は上下ほど狭い。** 弦を超えると角が切られるので、その行が
    # 置かれる高さでの弦を計算して、収まる最大サイズを探す。
    # **2行を同じ大きさにすると、どちらも中途半端になる。** 等サイズで組むと
    # 弦に当たって268pxで頭打ちになり、48pxでは1文字16pxで読めなかった。
    # 円は中央がいちばん広いので、**小さい行を上、大きい行を中央寄り**に置く。
    # 大きくするのは「解説」。競合2社との差はそこにしかない
    r = AV / 2 - 20
    rows = [("ひろゆき", 0.30, 150), ("解説", 0.62, 360)]

    def fit(text: str, cy: float, start: int) -> tuple:
        """その高さの弦に収まる最大サイズ。"""
        for size in range(start, 60, -4):
            f = pick_font(size)
            b = d.textbbox((0, 0), text, font=f)
            w, h = b[2] - b[0], b[3] - b[1]
            top, bot = cy - h / 2, cy + h / 2
            far = max(abs(top - AV / 2), abs(bot - AV / 2))
            chord = 2 * (r ** 2 - far ** 2) ** 0.5 if far < r else 0
            if w <= chord:
                return f, size, (AV - w) / 2 - b[0], top - b[1]
        raise SystemExit(f"! 「{text}」が円に収まらない")

    for text, cyr, start in rows:
        f, size, x, y = fit(text, AV * cyr, start)
        d.text((x, y), text, font=f, fill=fg)
        print(f"  「{text}」{size}px（48px時 {size * 48 / AV:.0f}px）")
    return img


def preview(variant: str) -> Image.Image:
    """実際の見え方。バナーはデスクトップの切り出し、アイコンは円。"""
    b = banner(variant)
    desk = b.crop((0, (BH - 423) // 2, BW, (BH + 423) // 2)).resize((1024, 211))
    a = avatar(variant).resize((160, 160))
    mask = Image.new("L", (160, 160), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, 160, 160], fill=255)

    sheet = Image.new("RGB", (1024, 211 + 190), (18, 18, 18))
    sheet.paste(desk, (0, 0))
    sheet.paste(a, (40, 226), mask)
    small = avatar(variant).resize((48, 48))
    m2 = Image.new("L", (48, 48), 0)
    ImageDraw.Draw(m2).ellipse([0, 0, 48, 48], fill=255)
    sheet.paste(small, (240, 282), m2)
    d = ImageDraw.Draw(sheet)
    d.text((240, 340), "← 48px（一覧での実寸）", font=pick_font(20), fill=(200, 200, 200))
    return sheet


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", default=None)
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()

    OUT.mkdir(exist_ok=True)
    for v in (["a", "b", "c"] if a.all else [a.variant or "a"]):
        banner(v).save(OUT / f"banner_{v}.png")
        avatar(v).save(OUT / f"avatar_{v}.png")
        preview(v).save(OUT / f"preview_{v}.png")
        print(f"✓ brand/banner_{v}.png  {BW}x{BH}")
        print(f"✓ brand/avatar_{v}.png  {AV}x{AV}")


if __name__ == "__main__":
    main()
