#!/usr/bin/env python3
"""レシピの検証と概要欄の生成。tora-kirinuki からの移植。

**規約担保の中核。** 通らなければ落ちる形にしてある。

tora との違いは2つ。

1. **元動画が複数ある。** ひろゆきは1本の配信からテーマで13〜20分を取れないので
   配信をまたいで束ねる。概要欄には**使った全部の元動画**を並べる。
   ガジェット通信の条件は「概要欄に元動画へのリンクを掲載することを必須とする」で、
   1本だけ書けばよいとは書かれていない。

2. **金額の裏取りチェックが無い。** 令和の虎は金額が命で ASR が崩すため
   cards.brief.amount を必須にしていた。ひろゆきにその構造は無い。
   代わりに**各クリップに解説（note）を必須にする。**
   解説を省くと「再利用されたコンテンツ」で収益化が通らない。
"""

from __future__ import annotations

REQUIRED = ("id", "title", "expected_channel_id")


def clip_notes(clip: dict) -> list[str]:
    """クリップの解説文。`notes`（配列）優先、無ければ `note`（単数）。"""
    notes = clip.get("notes")
    if notes:
        return [str(t).strip() for t in notes if str(t).strip()]
    note = (clip.get("note") or "").strip()
    return [note] if note else []

# 「公認」「公式」とは書かない。権利者は「あくまでご本人は黙認」という立場で、
# 受付メールに「‟公式”や‟公認”という記載はお控えください」と明記されている。
# 申請済みという事実だけを書く。
CREDIT = ("本チャンネルはガジェット通信クリエイターネットワークに"
          "申請済みの切り抜きチャンネルです。公式チャンネルではありません。")

BANNED_IN_TITLE = ("公式", "公認")

# 解説が短すぎると付加価値として弱い。要約や言い換えは付加価値にならないので、
# 最低限の文量を強制する。長さは品質の保証にならないが、空欄の防止にはなる
NOTE_MIN_LEN = 20


def validate(recipe: dict) -> None:
    """不備があれば ValueError。ビルドとアップロードの前に必ず通す。"""
    for key in REQUIRED:
        if not recipe.get(key):
            raise ValueError(f"レシピに {key} が無い（必須）")

    clips = recipe.get("clips") or []
    if not clips:
        raise ValueError("clips が空。1本ぶんの構成にならない")

    for i, c in enumerate(clips):
        for key in ("video_id", "start", "end", "title"):
            if c.get(key) in (None, ""):
                raise ValueError(f"clips[{i}] に {key} が無い")
        if c["end"] <= c["start"]:
            raise ValueError(
                f"clips[{i}] の範囲が不正: start={c['start']} end={c['end']}")

        notes = clip_notes(c)
        if not notes:
            raise ValueError(f"clips[{i}] に note / notes が無い")
        for j, note in enumerate(notes):
            if len(note) < NOTE_MIN_LEN:
                where = f"clips[{i}] の note" if len(notes) == 1 else f"clips[{i}].notes[{j}]"
                raise ValueError(
                    f"{where} が {len(note)}文字。"
                    f"{NOTE_MIN_LEN}文字以上の解説を書くこと。"
                    "解説を省いた切り抜きは「再利用されたコンテンツ」で収益化が通らない")

    # **検索語で束ねる回は解説の比率が効く。**
    # 1問あたりの素材は1分前後しかないので（2026-08-25 実測）、クリップが少ないほど
    # 素材そのままの割合が上がる。3問以下のときは解説板を合計4枚以上求める。
    total_notes = sum(len(clip_notes(c)) for c in clips)
    if len(clips) <= 3 and total_notes < 4:
        raise ValueError(
            f"クリップ {len(clips)}件に対して解説板が {total_notes}枚。"
            "本編の大半が素材そのままになる。notes を増やして合計4枚以上にすること")

    title = recipe["title"]
    hit = next((w for w in BANNED_IN_TITLE if w in title), None)
    if hit:
        raise ValueError(
            f"タイトルに「{hit}」が入っている。権利者が明示的に禁じている表記")


SHORT_MAX_SEC = 180.0
# tora-kirinuki の実測（2026-08-13）。伸びている競合は22〜73秒で、
# 103秒・132秒のものは0〜2再生だった
SHORT_RECOMMENDED_SEC = 75.0


def validate_short(recipe: dict) -> list[str]:
    short = recipe.get("short")
    if not short:
        raise ValueError("レシピに short がない")

    start, end = short.get("start"), short.get("end")
    if start is None or end is None or end <= start:
        raise ValueError(f"short の範囲が不正: start={start} end={end}")
    if end - start > SHORT_MAX_SEC:
        raise ValueError(
            f"short が {end - start:.0f}秒。Shorts の上限 {SHORT_MAX_SEC:.0f}秒を超えている")
    if not (short.get("hook") or "").strip():
        raise ValueError("short.hook が空。縦型は冒頭2秒で離脱が決まる")

    warnings = []
    if end - start > SHORT_RECOMMENDED_SEC:
        warnings.append(
            f"short が {end - start:.0f}秒。伸びている競合は22〜73秒")
    return warnings


def source_list(recipe: dict) -> list[tuple[str, str, str]]:
    """使った元動画を (video_id, タイトル, URL) の重複なしで返す。"""
    seen: dict[str, tuple[str, str, str]] = {}
    for c in recipe.get("clips") or []:
        vid = c["video_id"]
        if vid in seen:
            continue
        seen[vid] = (vid, c.get("video_title") or vid,
                     c.get("video_url") or f"https://www.youtube.com/watch?v={vid}")
    return list(seen.values())


def build_chapters(recipe: dict, offsets: list[float] | None = None) -> list[str]:
    """概要欄の目次。連結後の経過時間で振る。

    **offsets を渡すこと。** 解説板を挟むので、本編の尺を足すだけでは実際の
    再生位置とずれる。ビルド側が各パートの実測尺から積んだ値を持っている。
    """
    out, t = [], 0.0
    for i, c in enumerate(recipe["clips"]):
        at = offsets[i] if offsets and i < len(offsets) else t
        out.append(f"{int(at) // 60:02d}:{int(at) % 60:02d} {c['title']}")
        t += c["end"] - c["start"]
    return out


def build_description(recipe: dict, offsets: list[float] | None = None) -> str:
    """概要欄。元動画のリンクは手書きさせず、ここで必ず全部付ける。"""
    body = (recipe.get("description") or "").strip()
    tags = " ".join(f"#{t}" for t in (recipe.get("tags") or []))

    parts = ["【元動画】"]
    for _vid, title, url in source_list(recipe):
        parts += [title, url, ""]
    parts += ["【本人チャンネル】", "https://www.youtube.com/@hirox246", ""]
    if body:
        parts += [body, ""]
    parts += ["【目次】"] + build_chapters(recipe, offsets) + ["", CREDIT]
    if tags:
        parts += ["", tags]
    return "\n".join(parts).strip() + "\n"
