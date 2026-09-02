#!/usr/bin/env python3
"""描画の共通部品。tora-kirinuki からの移植。

配色だけ差し替えた。tora は白地に赤（令和の虎の意匠を避けるため）だったが、
こちらは元配信が夜の室内で暗いので、暗い帯に白抜きのほうが乗る。

**ひろゆき本人の肖像やロゴを図案に使わない。** 黙認の対象は配信の素材であって、
本人を想起させる意匠を自作してよいという話ではない。図案はすべて文字で作る。
"""

from __future__ import annotations

import re
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


OPEN_BRACKETS = "（［｛「『〈《〔"
CLOSE_BRACKETS = "）］｝」』〉》〕"

# 助詞の直後は語の切れ目であることが多い。読点も括弧も無い長い文で、
# 「立候補して」／「いる」のように活用語尾で割れるのを防ぐ。
PARTICLES = "はがをにへとでもやのかねよ"
_HIRAGANA = re.compile(r"[ぁ-ゟ]")

# 数値と単位はひとかたまり。途中で折ると行をまたいだ数字が別の額に読める
# （実測で「231万5」／「000円」に割れていた）。
_NUM = r"[0-9A-Za-z][0-9A-Za-z.,]*"
_UNIT = (r"パーセント|ポイント|項目|時間|キロ|メートル|トン|ドル|"
         r"[%％万億兆円年月日人名件回倍割歳個台本社校票席分秒]")
_NUM_TOKEN_RE = re.compile(rf"(?:{_NUM}(?:{_UNIT})*)+")


def _number_interiors(s: str) -> set[int]:
    """数値＋単位の途中にあたる位置。ここでは折らない。"""
    inside: set[int] = set()
    for m in _NUM_TOKEN_RE.finditer(s):
        inside.update(range(m.start() + 1, m.end()))
    return inside


def _depths(s: str) -> list[int]:
    """各文字の括弧の深さ。開き括弧の位置は0（＝その手前で折れる）。"""
    out, depth = [], 0
    for ch in s:
        if ch in OPEN_BRACKETS:
            out.append(depth)
            depth += 1
        elif ch in CLOSE_BRACKETS:
            depth = max(0, depth - 1)
            out.append(depth)
        else:
            out.append(depth)
    return out


def _break_at(s: str, limit: int) -> int:
    """limit 文字までに収まる範囲で、いちばん読みやすい改行位置を返す。

    **括弧の中では折らない。** 引用は1つのまとまりなので、途中で切ると
    読み手が繋ぎ直すことになる。実際に

      …返ってくるのは「場所を変えるか、
      順序を変えるか」でした。

    と割れていた（2026-08-14）。括弧の手前で折れば

      …返ってくるのは
      「場所を変えるか、順序を変えるか」でした。

    になる。優先順は 括弧外の読点の直後 → 開き括弧の直前 →
    閉じ括弧の直後 → 幅いっぱい。
    """
    d = _depths(s)
    inside = _number_interiors(s)
    window = max(1, int(limit * 0.45))          # これ以上戻ると行が短くなりすぎる
    lows = [lo for lo in range(limit, max(0, limit - window), -1)
            if 0 < lo < len(s) and lo not in inside]

    # 括弧の外にある読点
    for lo in lows:
        if s[lo - 1] in SOFT_BREAK and d[lo - 1] == 0:
            return lo
    # 開き括弧の直前。引用まるごとを次の行に送る
    for lo in lows:
        if s[lo] in OPEN_BRACKETS and d[lo] == 0:
            return lo
    # 閉じ括弧の直後
    for lo in lows:
        if s[lo - 1] in CLOSE_BRACKETS and d[lo - 1] == 0:
            return lo
    # 助詞の直後。読点も括弧も無い長い文はここで切ると語の途中を避けられる
    for lo in lows:
        if s[lo - 1] in PARTICLES and d[lo - 1] == 0 and s[lo] not in NO_START:
            return lo
    # ひらがな → 漢字・カタカナ の変わり目。送りがなの途中を避ける
    for lo in lows:
        if (d[lo] == 0 and s[lo] not in NO_START
                and _HIRAGANA.match(s[lo - 1]) and not _HIRAGANA.match(s[lo])):
            return lo
    # 括弧の外なら、どこでもいいので括弧を割らない位置
    for lo in lows:
        if d[lo] == 0 and s[lo] not in NO_START:
            return lo

    cut = min(limit, len(s))
    while cut in inside and cut > 1:            # 数値の途中で折らない
        cut -= 1
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
