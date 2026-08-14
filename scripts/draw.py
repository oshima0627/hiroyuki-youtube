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


# 行頭に置いてはいけない文字（読点・句点・閉じ括弧・長音・小書き仮名）
NO_START = "、。，．・：；？！）］｝」』〉》〕”’ーぁぃぅぇぉっゃゅょゎヵヶァィゥェォッャュョヮ"
# 行末に置いてはいけない文字（開き括弧）
NO_END = "（［｛「『〈《〔“‘"
# 文の切れ目。ここでは必ず改行する
SENTENCE_END = "。！？"
# 文中で折るときに優先する切れ目
SOFT_BREAK = "、"


def _w(draw: ImageDraw.ImageDraw, s: str, font: ImageFont.FreeTypeFont) -> int:
    b = draw.textbbox((0, 0), s, font=font)
    return b[2] - b[0]


def split_sentences(text: str) -> list[str]:
    """句点で切る。句点そのものは前の文に残す。"""
    out, cur = [], ""
    for ch in text:
        cur += ch
        if ch in SENTENCE_END:
            out.append(cur)
            cur = ""
    if cur.strip():
        out.append(cur)
    return out


def _break_at(s: str, limit: int) -> int:
    """limit 文字までに収まる範囲で、いちばん読みやすい改行位置を返す。

    優先順は 読点の直後 → 閉じ括弧の直後 → 開き括弧の直前 → 幅いっぱい。
    幅いっぱいで折るときも禁則を見る。
    """
    window = max(1, int(limit * 0.45))          # これ以上戻ると行が短くなりすぎる
    for lo in range(limit, limit - window, -1):
        if lo <= 0 or lo >= len(s):
            continue
        if s[lo - 1] in SOFT_BREAK:
            return lo
    for lo in range(limit, limit - window, -1):
        if lo <= 0 or lo >= len(s):
            continue
        if s[lo - 1] in "）」』】":
            return lo
        if s[lo] in NO_END:
            return lo

    cut = min(limit, len(s))
    # 行頭に来てはいけない文字なら1つ後ろへ送り、それでも駄目なら手前で折る
    while cut < len(s) and s[cut] in NO_START:
        cut += 1
    while cut > 1 and s[cut - 1] in NO_END:
        cut -= 1
    return cut


def wrap(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont,
         max_w: int) -> list[str]:
    """日本語として読める位置で折り返す。

    **幅だけで1文字ずつ折ってはいけない。** 実装当初はそうしていて、
    「上司も／、ゴマすりで」「成功／率が低く」のように読点の前や熟語の途中で
    切れていた（2026-08-14）。

      1. 句点では必ず改行する
      2. 文が長いときは読点や括弧の切れ目で折る
      3. どうしても幅で折るときも禁則処理を見る
    """
    lines: list[str] = []
    for sentence in split_sentences(text):
        s = sentence.strip()
        while s:
            if _w(draw, s, font) <= max_w:
                lines.append(s)
                break
            # 幅に収まる最大文字数を求めてから、読みやすい位置へ寄せる
            limit = 1
            while limit < len(s) and _w(draw, s[:limit + 1], font) <= max_w:
                limit += 1
            cut = _break_at(s, limit)
            # 禁則で伸ばした結果はみ出すことがあるので、そこは許容する
            lines.append(s[:cut])
            s = s[cut:].lstrip()
    return lines
