#!/usr/bin/env python3
"""視聴者に問いかける文言を作る。テロップ・概要欄・コメントの共通部品。

レシピの任意フィールド:

  "engagement": {
    "question": "「軽自動車は走る棺です」この考え方、アリ？ナシ？",   省略可
    "comment":  "公開後にチャンネルとして投稿する問いかけコメント",     省略可
    "enabled":  false                                                   省略可（既定 true）
  }

question を省くとタイトルから既定文を作る（default_question）。

## 文体のルール（2026-10-15 ユーザー承認）

- 議論が起きる二択で聞く（「アリ？ナシ？」「賛成？反対？」「あなたの反論をコメントで」）
- **人を攻撃・侮辱する煽りは書かない。政治の話題は出さない。**
- 「公式」「公認」と書かない（本人の公式チャンネルと誤認させない）
- 本人になりすまさない。一人称は**切り抜きの運営者**
- いいね・登録の自作自演、別アカウントでのコメント、報酬付きの依頼はしない
"""

from __future__ import annotations

import hashlib
import re

CTA = "あなたの反論をコメントで"

# 二択の型。どれを使うかは id から決める（同じ動画で毎回同じ文になるように）
STATEMENT_FORMS = (
    "この考え方、アリ？ナシ？",
    "あなたは賛成？反対？",
    "これ、納得できる？できない？",
)
QUESTION_FORMS = (
    "あなたはどっち派？",
    "イエス？ノー？",
)

PUNCH_MAX = 26            # 「」の中に入れる長さ。テロップ1〜2行に収める
QUESTION_MAX = 60
COMMENT_MAX = 300
REPLY_MAX = 120

# 本人の公式と誤認させる表記
BANNED_WORDS = ("公式", "公認")
# 人を攻撃する煽り。自分の文章に入っていたら止める
INSULT_WORDS = ("バカ", "馬鹿", "アホ", "クズ", "死ね", "低能",
                "情弱", "底辺", "ガイジ", "キモ", "黙れ")
# 政治の話題。自分の文章では使わず、視聴者のコメントなら返信を見送る目安にする
POLITICS_WORDS = ("政治", "政党", "選挙", "自民", "立憲", "維新", "共産党", "公明",
                  "れいわ", "参政党", "国民民主", "首相", "総理", "岸田", "石破", "高市",
                  "安倍", "国会", "議員", "改憲", "憲法改正", "右翼", "左翼", "ネトウヨ",
                  "パヨク", "与党", "野党", "政権")
# 本人になりすます一人称
IMPERSONATION = ("ひろゆきです", "西村博之です", "ひろゆき本人", "本人です")
# 自作自演・報酬付き依頼
SPAMMY_OWN = ("いいねお願いします", "高評価お願いします", "登録お願いします",
              "チャンネル登録して", "プレゼント", "抽選", "謝礼")

_BRACKETS = re.compile(r"【[^】]*】")


def _pick(seq: tuple[str, ...], key: str) -> str:
    h = int(hashlib.sha1(key.encode("utf-8")).hexdigest(), 16)
    return seq[h % len(seq)]


def punchline(title: str) -> str:
    """タイトルから「」に入れる一言を取る。

    長尺は「車と移動の話6連発。軽自動車は走る棺です」の形なので、最後の文が
    いちばん議論になる一言。短すぎる（8文字未満）なら全体を使う。
    """
    t = _BRACKETS.sub("", title or "").strip()
    parts = [p.strip() for p in re.split(r"[。]", t) if p.strip()]
    if not parts:
        return ""
    last = parts[-1]
    text = last if len(last) >= 8 or len(parts) == 1 else "。".join(parts)
    if len(text) > PUNCH_MAX:
        text = text[:PUNCH_MAX - 1] + "…"
    return text


def default_question(title: str, key: str = "") -> str:
    p = punchline(title)
    if not p:
        return "この考え方、アリ？ナシ？"
    is_q = p.endswith(("か", "？", "?", "か？", "の？"))
    form = _pick(QUESTION_FORMS if is_q else STATEMENT_FORMS, key or p)
    return f"「{p.rstrip('？?')}」{form}"


def enabled(recipe: dict) -> bool:
    eng = recipe.get("engagement") or {}
    return eng.get("enabled", True) is not False


def question_for(recipe: dict, title: str | None = None) -> str:
    """レシピから問いかけ文を決める。engagement.question 優先、無ければ既定文。

    ショート（単体レシピ）は short.hook のほうが短く具体的なので、そちらから作る。
    """
    eng = recipe.get("engagement") or {}
    q = (eng.get("question") or "").strip()
    if q:
        return q
    if title is None:
        short = recipe.get("short") or {}
        title = (short.get("hook") if isinstance(recipe.get("clip"), dict) else None) \
            or recipe.get("title") or ""
    return default_question(title, recipe.get("id", ""))


def short_question(recipe: dict) -> str | None:
    """ショートの問いかけ文。

    単体レシピは recipe.engagement.question、埋め込み形式は short.engagement.question
    （長尺側の engagement は長尺用なので見ない）。無ければ hook から既定文を作る。
    """
    if not enabled(recipe):
        return None
    short = recipe.get("short") or {}
    standalone = isinstance(recipe.get("clip"), dict)
    eng = (recipe.get("engagement") if standalone else short.get("engagement")) or {}
    if eng.get("enabled") is False:
        return None
    q = (eng.get("question") or "").strip()
    rid = recipe.get("id", "")
    return q or default_question(short.get("hook") or recipe.get("title", ""), rid)


def split_question(question: str) -> list[str]:
    """テロップで折るときの塊。「…」と二択を別の行にする（「アリ？/ナシ？」で割れないように）。"""
    if "」" in question and not question.endswith("」"):
        head, tail = question.rsplit("」", 1)
        return [head + "」", tail]
    return [question]


def description_line(question: str) -> str:
    """概要欄の1行目。検索結果と動画下の2行に出る。"""
    return f"{question} {CTA}👇"


def prepend_description(description: str, question: str) -> str:
    """概要欄の先頭に問いかけ行を足す。既に入っていれば何もしない（冪等）。"""
    line = description_line(question)
    if description.startswith(line) or question in description.split("\n", 1)[0]:
        return description
    return f"{line}\n\n{description.lstrip()}"


def comment_text(recipe_or_none: dict | None, question: str) -> str:
    """公開後にチャンネルとして投稿する問いかけコメント。運営者の一人称で書く。"""
    eng = (recipe_or_none or {}).get("engagement") or {}
    c = (eng.get("comment") or "").strip()
    if c:
        return c
    return (f"切り抜き運営者です。{question}\n"
            "どっち派か、理由もひとこと添えてもらえると嬉しいです。"
            "ひろゆきさんへの反論も大歓迎です。")


def check_own_text(text: str, max_len: int, what: str = "文") -> list[str]:
    """自分（チャンネル）が出す文の禁止事項。空リストなら通ってよい。"""
    errs = []
    t = text or ""
    if not t.strip():
        errs.append(f"{what}が空")
    if len(t) > max_len:
        errs.append(f"{what}が {len(t)}文字（上限 {max_len}）")
    for group, label in ((BANNED_WORDS, "「公式」「公認」"),
                         (INSULT_WORDS, "攻撃的な語"),
                         (POLITICS_WORDS, "政治の話題"),
                         (IMPERSONATION, "本人なりすまし"),
                         (SPAMMY_OWN, "自作自演・報酬付き依頼")):
        hit = [w for w in group if w in t]
        if hit:
            errs.append(f"{what}に{label}が入っている: {'・'.join(hit)}")
    return errs


def check_reply_text(text: str) -> list[str]:
    errs = check_own_text(text, REPLY_MAX, "返信")
    sentences = [s for s in re.split(r"[。！？!?]+", text or "") if s.strip()]
    if len(sentences) > 2:
        errs.append(f"返信が {len(sentences)}文。1〜2文にする")
    if re.search(r"https?://", text or ""):
        errs.append("返信に URL を入れない")
    return errs


_URL = re.compile(r"https?://|www\.|\.com\b|\.jp\b|t\.me/|line\.me", re.I)
_EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
_PHONE = re.compile(r"0\d{1,4}[-ー−]?\d{1,4}[-ー−]?\d{3,4}")
_SPAM = ("稼げ", "副業", "儲か", "LINE追加", "ライン追加", "プロフ見て", "プロフィール見て",
         "無料で", "フォローして", "チャンネル見て", "相互登録", "仮想通貨", "投資案件")


def comment_flags(text: str) -> list[str]:
    """視聴者コメントの見送り目安。**判定ではなく目安。** 最後は読んで決める。

    返信しないもの: 攻撃的・スパム・政治・個人情報を含むもの。
    """
    t = text or ""
    flags = []
    if any(w in t for w in INSULT_WORDS):
        flags.append("aggressive")
    if _URL.search(t) or any(w in t for w in _SPAM):
        flags.append("spam")
    if any(w in t for w in POLITICS_WORDS):
        flags.append("politics")
    if _EMAIL.search(t) or _PHONE.search(t):
        flags.append("personal_info")
    return flags
