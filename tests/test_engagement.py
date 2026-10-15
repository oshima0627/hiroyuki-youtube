"""エンゲージメント施策（2026-10-15）。文言の既定・禁止事項・二重投稿/二重返信の防止。"""
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.engagement import (  # noqa: E402
    CTA, check_own_text, check_reply_text, comment_flags, comment_text,
    default_question, prepend_description, punchline, question_for,
    short_question, split_question)


def test_タイトルの最後の一言を二択で聞く():
    q = default_question("【ひろゆき】車と移動の話6連発。軽自動車は走る棺です", "x")
    assert q.startswith("「軽自動車は走る棺です」")
    assert any(w in q for w in ("アリ？ナシ？", "賛成？反対？", "納得できる？"))


def test_最後の一言が短ければ全体を使う():
    assert punchline("【ひろゆき】復職に引っ越し。大手を辞めるか【切り抜き】") == "復職に引っ越し。大手を辞めるか"


def test_疑問形のタイトルは疑問形の二択にする():
    q = default_question("ゴマすりで上げた給料は実力か", "y")
    assert q.endswith(("どっち派？", "イエス？ノー？"))


def test_同じidなら毎回同じ文():
    t = "【ひろゆき】旅行の話7連発。パリに手頃ないいホテルはありません"
    assert default_question(t, "a") == default_question(t, "a")


def test_既定文は文体ルールを通る():
    for t in ("【ひろゆき】車と移動の話6連発。軽自動車は走る棺です",
              "【ひろゆき】復職に引っ越し。大手を辞めるか【切り抜き】", ""):
        q = default_question(t, t)
        assert check_own_text(q, 60) == []
        assert check_own_text(comment_text(None, q), 300) == []


def test_レシピのquestionが優先():
    r = {"id": "r", "title": "【ひろゆき】A。B", "engagement": {"question": "この考え方、アリ？ナシ？"}}
    assert question_for(r) == "この考え方、アリ？ナシ？"


def test_ショートはhookから作り無効化もできる():
    r = {"id": "s", "title": "長いタイトル", "clip": {}, "short": {"hook": "その給料、転職先では出ません"}}
    assert "その給料、転職先では出ません" in short_question(r)
    r["engagement"] = {"enabled": False}
    assert short_question(r) is None


def test_公式公認_攻撃_政治_なりすまし_自作自演は通さない():
    assert check_own_text("公式の切り抜きです", 60)
    assert check_own_text("こんなこと言う人はバカ", 60)
    assert check_own_text("選挙どうする？", 60)
    assert check_own_text("ひろゆきです。どう思う？", 60)
    assert check_own_text("高評価お願いします", 60)


def test_返信は2文まで_URLなし():
    assert check_reply_text("ありがとうございます！その視点は鋭いですね。") == []
    assert check_reply_text("一。二。三。")
    assert check_reply_text("こちら https://example.com")


def test_見送りの目安():
    assert "spam" in comment_flags("副業で稼げます。プロフ見て")
    assert "politics" in comment_flags("これは政権のせい")
    assert "personal_info" in comment_flags("連絡は abc@example.com まで")
    assert "aggressive" in comment_flags("お前バカだろ")
    assert comment_flags("軽自動車は乗ってるけど怖くないです") == []


def test_概要欄の先頭行は冪等():
    q = "「X」この考え方、アリ？ナシ？"
    d1 = prepend_description("【元動画】\n...", q)
    assert d1.split("\n", 1)[0] == f"{q} {CTA}👇"
    assert prepend_description(d1, q) == d1


def test_問いかけと二択を別行に():
    assert split_question("「A」この考え方、アリ？ナシ？") == ["「A」", "この考え方、アリ？ナシ？"]


def test_upload_の概要欄に問いかけ行が入る():
    from scripts.upload_youtube import with_engagement_line
    d = with_engagement_line({"id": "x", "title": "【ひろゆき】A。軽自動車は走る棺です"}, "本文\n")
    assert d.startswith("「軽自動車は走る棺です」")
    assert with_engagement_line({"id": "x", "engagement_question": None}, "本文\n") == "本文\n"


def test_終了画面の余白は15分未満に収める():
    from scripts.build_episode import MAX_TOTAL_SEC, OUTRO_SEC, outro_seconds
    assert outro_seconds(500) == OUTRO_SEC
    assert 500 + outro_seconds(500) < 15 * 60
    assert outro_seconds(880) + 880 <= MAX_TOTAL_SEC
    with pytest.raises(SystemExit):
        outro_seconds(895)


def test_レシピのengagementを検証する():
    from scripts.recipe import validate_engagement
    validate_engagement({"engagement": {"question": "この考え方、アリ？ナシ？"}})
    with pytest.raises(ValueError):
        validate_engagement({"engagement": {"question": "公認チャンネルです"}})


# ---- engage.py（API を呼ばない部分）

ME = "UCqK3KYqEeeJiAWr4nSryJYQ"


def _c(cid, author, text, at, parent=None):
    sn = {"authorChannelId": {"value": author}, "authorDisplayName": f"@{author}",
          "textOriginal": text, "publishedAt": at, "likeCount": 0}
    if parent:
        sn["parentId"] = parent
    return {"id": cid, "snippet": sn}


def _t(top, replies=()):
    return {"id": top["id"], "snippet": {"videoId": "v1", "topLevelComment": top,
                                         "totalReplyCount": len(replies)},
            "replies": {"comments": list(replies)}}


def test_未返信の抽出():
    from scripts.engage import unreplied_from_threads
    now = datetime.now(timezone.utc)
    iso = lambda d: (now - timedelta(days=d)).strftime("%Y-%m-%dT%H:%M:%SZ")  # noqa: E731
    threads = [
        _t(_c("a", "viewer1", "なるほど", iso(1))),                                  # 未返信 → 出す
        _t(_c("b", "viewer2", "反論です", iso(1)), [_c("b.r", ME, "ありがとう", iso(0))]),  # 返信済み
        _t(_c("c", ME, "問いかけ", iso(2)), [_c("c.1", "viewer3", "アリ派", iso(1), "c"),   # 自分のスレへの返信
                                             _c("c.2", ME, "@viewer4 どうも", iso(0), "c"),
                                             _c("c.3", "viewer4", "ナシ派", iso(1), "c")]),
        _t(_c("d", "viewer5", "古い", iso(30))),                                     # 古いので出さない
        _t(_c("e", "viewer6", "記録済み", iso(1))),                                  # state に返信済み
    ]
    state = {"replied": {"e": {}}}
    out = unreplied_from_threads(threads, lambda t: t["replies"]["comments"], state,
                                 now - timedelta(days=7))
    ids = [x["comment_id"] for x in out]
    assert ids == ["a", "c.1"]
    assert all(x["author"] != f"@{ME}" for x in out)
    assert out[1]["kind"] == "reply_to_our_comment"


def test_1日の上限は太平洋時間で数える():
    from scripts.engage import count_today
    now = datetime(2026, 10, 15, 3, 0, tzinfo=timezone.utc)   # PT 10/14 20:00
    e = {"x": {"at": "2026-10-14T20:00:00Z"}, "y": {"at": "2026-10-14T06:00:00Z"}}
    assert count_today(e, now) == 1


def test_durationの解釈():
    from scripts.engage import parse_duration
    assert parse_duration("PT8M22S") == 502
    assert parse_duration("PT41S") == 41
