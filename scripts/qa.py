#!/usr/bin/env python3
"""配信を1問1答のブロックに割って、切り抜き候補として並べる。

**tora-kirinuki の moments.py を置き換えたのがここ。**

令和の虎は「持ち込み→詰め→判定」という一本の流れなので、スコアの積分が最大に
なる連続区間をスライディングウィンドウで1つ取る設計でよかった。
ひろゆきは質問と回答の繰り返しなので、同じことをすると**質問の途中で切れる**。

なので先に質問境界でブロックに割り、ブロック単位でスコアを出す。
1本の動画は複数ブロックを束ねて作る（競合上位も全員チャプター5〜8個の構成）。

なお**令和の虎ガイドラインの「分割された本編を連結した投稿の禁止」は、
ひろゆき側の許諾条件には無い。** 混同しないこと。
"""

from __future__ import annotations

import math

# ひろゆきは怒鳴らないので音量は当てにならない。令和の虎の 0.35 から下げた
W_LOUD = 0.15
W_COMMENT = 0.45      # 件数は少ないが精度が高い。ここが主軸
W_HEATMAP = 0.40      # あれば加点。新着には存在しない
W_ASSERT = 0.12       # 言い切り。切り抜きの中身になる
W_EVIDENCE = 0.10     # 根拠・具体例。解説の材料になる

ASSERT_CAP = 10       # 長いブロックが語彙数だけで勝たないように頭を打つ
EVIDENCE_CAP = 6
COMMENT_CAP = 3       # 1箇所あたりの言及数の上限

# 質問文の読み上げにかかる時間。質問語がヒットする時刻は読み上げの**末尾**なので、
# ブロックの頭はそのぶん手前に取る。実素材で20〜30秒だった（2026-08-14 実測）
LEAD_SEC = 28.0

# 同じ質問の読み上げ中に複数の語がヒットするので、この秒数以内は1つに畳む。
# 45秒だと連続する別の質問まで畳んでしまう（実素材で毒親の回答とKADOKAWAの
# 回答が1ブロックに融合した）。18秒に下げて分離した（2026-08-14 実測）
MERGE_GAP = 18.0

# 1問の回答がこれより長いときは切る。雑談に流れているか、質問語を取り逃している
MAX_BLOCK = 300.0
MIN_BLOCK = 40.0


def question_marks(lexical: list[dict]) -> list[float]:
    """質問語のヒットを、質問1つにつき1点に畳んで返す。"""
    times = sorted(m["seconds"] for m in lexical if m["kind"] == "質問")
    merged: list[float] = []
    for t in times:
        if merged and t - merged[-1] <= MERGE_GAP:
            continue
        merged.append(float(t))
    return merged


def snap_to_cues(t: float, cues: list[dict]) -> float:
    """最寄りの字幕キュー境界に寄せる。文の途中で切らないため。"""
    if not cues:
        return t
    return min((c["t"] for c in cues), key=lambda x: abs(x - t))


def _count(marks: list[dict], kind: str, start: float, end: float) -> int:
    return sum(1 for m in marks
               if m["kind"] == kind and start <= m["seconds"] <= end)


def split_blocks(signals: dict, cues: list[dict], duration: int) -> list[dict]:
    """1問1答のブロックに割る。スコアと risk を付けて返す。"""
    lexical = signals.get("lexical") or []
    avoid = signals.get("avoid") or []
    comments = signals.get("comment_marks") or []
    heat = signals.get("heatmap") or []
    loud = signals.get("loudness") or []

    qs = question_marks(lexical)
    if not qs:
        return []

    bounds = [max(0.0, q - LEAD_SEC) for q in qs] + [float(duration)]

    blocks: list[dict] = []
    for i in range(len(bounds) - 1):
        start = snap_to_cues(bounds[i], cues)
        end = snap_to_cues(min(bounds[i + 1], bounds[i] + MAX_BLOCK), cues)
        if end - start < MIN_BLOCK:
            continue

        c_hits = [m for m in comments if start <= m["seconds"] <= end]
        c_score = sum(min(m.get("count", 1), COMMENT_CAP) for m in c_hits)

        h_in = [h for h in heat if start <= (h["start"] + h["end"]) / 2 <= end]
        h_score = max((h["score"] for h in h_in), default=0.0)

        l_score = max((e["score"] for e in loud
                       if start <= e["t"] <= end), default=0.0)

        n_assert = min(_count(lexical, "断言", start, end), ASSERT_CAP)
        n_evid = min(_count(lexical, "根拠", start, end), EVIDENCE_CAP)
        n_hedge = _count(lexical, "留保", start, end)

        risk = sorted({m["kind"] for m in avoid if start <= m["seconds"] <= end})
        risk_words = sorted({m["word"] for m in avoid
                             if start <= m["seconds"] <= end})

        score = (W_COMMENT * c_score + W_HEATMAP * h_score
                 + W_LOUD * l_score + W_ASSERT * n_assert
                 + W_EVIDENCE * n_evid)

        lines = [c["line"] for c in cues if start <= c["t"] <= end]
        blocks.append({
            "start": start,
            "end": end,
            "seconds": round(end - start, 1),
            "score": round(score, 3),
            "signals": {"コメント": c_score, "断言": n_assert, "根拠": n_evid,
                        "留保": n_hedge, "熱": round(h_score, 2),
                        "音量": round(l_score, 2)},
            "risk": risk,
            "risk_words": risk_words,
            "question": "".join(lines[:6])[:120],
            "subtitles": lines,
        })
    return blocks


def bundle(blocks: list[dict], target_sec: float = 900.0,
           max_items: int = 8, allow_risky: bool = False) -> list[dict]:
    """スコアの高いブロックから、合計が target_sec に届くまで束ねる。

    **尺は13〜20分を狙う。** tora-kirinuki の実測で、この市場の検索上位は
    すべて14分以上だった。ひろゆき側の競合上位4本も同様の長尺構成。

    risk が付いたブロックは既定で外す。allow_risky=True で残せるが、
    残すかどうかは人が中身を見て決めること。

    **並べ替えは score をそのまま使わない。** コメント言及は長いブロックほど
    多く入るので、生スコア順にすると長い数本だけで尺が埋まりチャプターが
    4本しか立たない。かといって毎分あたりの密度にすると45秒級の短い
    ブロックばかりが選ばれて合計尺が10分に届かない。
    実素材で比べた結果 sqrt(秒) で割るのが一番釣り合った（2026-08-14 実測）。

      生スコア順   4本 / 17.8分   チャプターが足りない
      密度順       8本 / 10.3分   尺が足りない
      sqrt順       7本 / 18.0分   ← これを採る
    """
    pool = [b for b in blocks if allow_risky or not b["risk"]]
    pool = sorted(pool, key=lambda b: -b["score"] / math.sqrt(max(b["seconds"], 1.0)))

    picked: list[dict] = []
    total = 0.0
    for b in pool:
        if len(picked) >= max_items or total >= target_sec:
            break
        picked.append(b)
        total += b["seconds"]
    return sorted(picked, key=lambda b: b["start"])
