"""ショートの窓の取り方。2026-09-10 の実測で見つかった欠陥を固定する。

予約済み30本の冒頭を字幕で当たったところ:
  - 冒頭が前の話題の文の途中から始まるものが並んでいた
    （「ないですか。」「なと思いますけども。はい。」「これさっき読んだやつじゃん。」）
  - 30本中22本は、ひろゆき氏の答えが始まるまでに尺の 7〜80% を相談文の
    読み上げに使っていた

原因は best_window() が**字幕キューの境界**にスナップしていたこと。
自動字幕のキュー境界は2行ローリング表示の都合で決まるもので、文の切れ目ではない。
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.plan_shorts import (  # noqa: E402
    MAX_SEC, MIN_SEC, best_window, is_question_lead, is_used, sentences,
    thin_opening,
)


def test_1文目が相づちや配信の進行なら弱いとみなす():
    """文の頭から始めるだけでは足りない（2026-09-10 実測）。"""
    assert thin_opening("はい。")
    assert thin_opening("えっと、あの、はい。")
    assert thin_opening("失礼しましたというわけで、そろそろ終わらないと厳しい感じなんで")
    assert thin_opening("はい、ありがとうございました。")
    assert thin_opening("[笑い]うん。")


def test_前を受ける接続詞で始まる1文目は弱いとみなす():
    """文の頭ではあるが、指すものが画面に無い（2026-09-10 実測）。"""
    assert thin_opening("ただ基本的にはその、テムとかがやってるのって大量の発注を受けて")
    assert thin_opening("で、あの、大手代理店というのは自分が知らなかったとしても")
    assert thin_opening("ま、あのそのなんかアスリートを熱狂的なファンは別にしてね。")


def test_中身のある1文目は通す():
    assert not thin_opening("僕ね楽器引かないですよね。")
    assert not thin_opening("あの、石は蓄熱するんで、1日2日その40度近くになった日は")
    assert not thin_opening("辞めてから探すと足元を見られるので。")


USED = [{"short_id": "x", "video_id": "AAA", "start": 100.0, "end": 145.0,
         "hook": "簿記1級を取るか税理士を目指すか"}]


def test_窓が数秒ずれても使用済みとみなす():
    """best_window を文境界へ移すと位置が動く。完全一致だと既出が復活する。"""
    assert is_used("AAA", 103.0, 148.0, "別のフック", USED)
    assert is_used("AAA", 96.0, 141.0, "別のフック", USED)


def test_フックが同じなら使用済み():
    assert is_used("AAA", 9000.0, 9040.0, "簿記1級を取るか税理士を目指すか", USED)


def test_別の動画や離れた区間は使用済みではない():
    assert not is_used("BBB", 100.0, 145.0, "別のフック", USED)
    assert not is_used("AAA", 500.0, 545.0, "別のフック", USED)


def cue(t, line):
    return {"t": t, "line": line}


# 自動字幕そのままの形。**キューは文の途中で切れる**
ROLLING = [
    cue(0.0, "いうのをやると、ま、僕1人だったら別に"),
    cue(2.0, "困らないんですよ。で、相談なんですけど"),
    cue(5.0, "、今の職場が合わなくて転職を考えてい"),
    cue(8.0, "ます。どうすればいいですか?"),
    cue(11.0, "えっと、まず選択肢を増やすっていうのが"),
    cue(14.0, "先だと思うんですよね。辞めてから探すと"),
    cue(17.0, "足元を見られるので。だから在職中に動く"),
    cue(20.0, "のが普通に正解です。はい。"),
    cue(23.0, "で、次に年収の話なんですけど、これは"),
    cue(26.0, "上がる人と下がる人がはっきり分かれます"),
    cue(29.0, "。運じゃなくて準備の差です。以上です。"),
    cue(33.0, "はい、ありがとうございました。"),
    cue(36.0, "次の質問いきましょう。どうぞ。"),
    cue(40.0, "はい、では次の方お願いします。"),
    cue(44.0, "よろしくお願いします。はい。"),
    cue(48.0, "ええ、そうですね。はい。"),
]

SIG = {"lexical": [], "comment_marks": [], "avoid": []}


def test_文に組み直すとキュー境界ではなく句点で切れる():
    sents = sentences(ROLLING)
    texts = [t for _, _, t in sents]
    # キュー境界（"別に" / "考えてい"）で切れていないこと
    assert not any(t.endswith("別に") for t in texts)
    assert not any(t.endswith("考えてい") for t in texts)
    # キューを2つまたいで1文になっていること
    assert "いうのをやると、ま、僕1人だったら別に困らないんですよ。" in texts
    assert any(t.endswith("どうすればいいですか?") for t in texts)


def test_文の開始時刻はキューの中でも進む():
    sents = sentences(ROLLING)
    starts = [s for s, _, _ in sents]
    assert starts == sorted(starts)
    # "で、相談なんですけど" はキュー2.0の途中から始まるので 2.0 ちょうどではない
    s = next(s for s, _, t in sents if t.startswith("で、相談"))
    assert 2.0 < s < 5.0


def test_窓は答えの1文目から始まる():
    """質問が 8.64-10.79 にあるので、窓は 11.0 の答えから始まること。"""
    lo, _hi, _ = best_window(ROLLING, SIG, 0.0, 52.0)
    text = next(t for s, _, t in sentences(ROLLING) if s == lo)
    assert text.startswith("えっと、まず選択肢を増やす"), text


def test_相談文を見分ける():
    assert is_question_lead("どうすればいいですか?")
    assert is_question_lead("フランスにも敬語的な言葉あるんでしょうか？")
    assert not is_question_lead("辞めてから探すと足元を見られるので。")


def test_疑問符が無い質問も見分ける():
    """2026-09-10 実測。句点で終わる質問が1本すり抜けた。"""
    assert is_question_lead("30分程点の購入は1年目としてはなかなかいいのでしょうか。")
    assert is_question_lead("これは買ったほうがいいですか。")
    assert not is_question_lead("だから在職中に動くのが普通に正解です。")


def test_窓は文の途中から始まらない():
    win = best_window(ROLLING, SIG, 0.0, 52.0)
    assert win is not None
    lo, hi, _ = win
    starts = {s for s, _, _ in sentences(ROLLING)}
    assert lo in starts, f"lo={lo} が文の開始位置ではない"


def test_窓の冒頭に相談文の読み上げを含めない():
    """これが今回の本題。答えの前に質問を読ませない。"""
    win = best_window(ROLLING, SIG, 0.0, 52.0)
    assert win is not None
    lo, hi, _ = win
    span = hi - lo
    head = [t for s, _, t in sentences(ROLLING) if lo <= s <= lo + span * 0.30]
    assert not any(is_question_lead(t) for t in head), \
        f"冒頭30%に相談文が入っている: {head}"


def test_窓の尺は範囲内():
    win = best_window(ROLLING, SIG, 0.0, 52.0)
    assert win is not None
    lo, hi, _ = win
    assert MIN_SEC <= hi - lo <= MAX_SEC
