"""折り返し位置のテスト。

このリポジトリには従来テストが無かったので、今回の変更を守るぶんだけ置く。
`wrap()` は 2026-08-14 に「読点や括弧の切れ目で折る」まで直してあったが、
**数値＋単位と、助詞・送りがなの扱いが無かった**（「231万5」／「000円」、
「公表している公」／「約です」に割れていた）。
"""
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.draw import pick_font, wrap      # noqa: E402


def _wrap(text: str, max_w: int) -> list[str]:
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    return wrap(d, text, pick_font(66), max_w)


def test_数値と単位は行をまたがない():
    for line in _wrap("ひとりあたり県民所得231万5000円を、500万円にふやします。", 900):
        assert not line.endswith(("231万5", "231万", "500")), line


def test_送りがなの途中で割らない():
    lines = _wrap("沖縄県知事選挙に立候補している古謝玄太氏が、公式サイトで公表している公約です。", 1200)
    for line in lines:
        assert not line.endswith("公"), lines


def test_括弧の中では折らない():
    # 2026-08-14 に直した挙動。今回の変更で壊していないことを押さえる。
    lines = _wrap("返ってくるのは「場所を変えるか、順序を変えるか」でした。", 1200)
    assert lines[0].endswith("順序") or lines[0].endswith("のは"), lines


def test_句点では必ず改行する():
    lines = _wrap("これは一文目です。これは二文目です。", 5000)
    assert len(lines) == 2
