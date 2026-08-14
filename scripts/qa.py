#!/usr/bin/env python3
"""配信をブロックに割って、切り抜き候補として並べる。

**tora-kirinuki の moments.py を置き換えたのがここ。**

令和の虎は「持ち込み→詰め→判定」という一本の流れなので、スコアの積分が最大に
なる連続区間をスライディングウィンドウで1つ取る設計でよかった。
ひろゆきは話題が次々に変わるので、同じことをすると**話題の途中で切れる**。

## 境界の取り方は2つある

1. **GCD の公式トピック（`topics.json`）。取れるなら必ずこちら。**
   ガジェット通信の切り抜き用データベースが、時刻付きの話題一覧を出している。
   実測（2026-08-14）で手作業の特定結果と完全に一致した。

     手作業 0:52:35 職場に絡んでくる人  →  GCD 0:52:35 職場での無駄な絡みへの対処法
     手作業 1:06:09 毒親と縁を切る      →  GCD 1:06:00 依存症の親との絶縁と住民票の移動

   タイトルが付いているのでチャプター名と要注意判定にそのまま使える。

2. **字幕の質問語からの推定（フォールバック）。**
   GCD に載っていない古い回はこちら。境界は粗く、話題の融合も起きる。
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

# --- 字幕から推定する場合だけ使う定数 ---------------------------------
# 質問文の読み上げにかかる時間。質問語がヒットするのは読み上げの**末尾**
LEAD_SEC = 28.0
# 45秒だと連続する別の質問まで畳んでしまう（毒親の回答とKADOKAWAの回答が
# 1ブロックに融合した）。18秒に下げて分離した（2026-08-14 実測）
MERGE_GAP = 18.0

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


def snap_to_cues(t: float, cues: list[dict], direction: int = 0) -> float:
    """字幕キュー境界に寄せる。文の途中で切らないため。

    **方向を指定できるようにした。** 最寄りへ寄せるだけだと境界が前後どちらにも
    動き、終端が次のトピックの開始を追い越す。実際にそうなって、次の質問の
    冒頭が見出しも解説も無いまま流れ込んだ（2026-08-14）。視聴者からは
    「解説が飛んでいる」ように見える。

      direction < 0  t 以下の最大のキュー（後ろへはみ出さない）
      direction > 0  t 以上の最小のキュー
      direction = 0  最寄り
    """
    if not cues:
        return t
    times = [c["t"] for c in cues]
    if direction < 0:
        cand = [x for x in times if x <= t]
        return max(cand) if cand else min(times)
    if direction > 0:
        cand = [x for x in times if x >= t]
        return min(cand) if cand else max(times)
    return min(times, key=lambda x: abs(x - t))


def _count(marks: list[dict], kind: str, start: float, end: float) -> int:
    return sum(1 for m in marks
               if m["kind"] == kind and start <= m["seconds"] <= end)


def _bounds_from_topics(topics: list[dict], duration: int) -> list[tuple[float, float, str]]:
    """公式トピックを (開始, 終了, タイトル) に変換する。短すぎるものは次と統合。"""
    out: list[tuple[float, float, str]] = []
    for i, tp in enumerate(topics):
        start = float(tp["t"])
        end = float(topics[i + 1]["t"]) if i + 1 < len(topics) else float(duration)
        title = tp["title"]
        if out and end - start < MIN_BLOCK:
            ps, _pe, pt = out[-1]
            out[-1] = (ps, end, f"{pt} / {title}")
            continue
        out.append((start, end, title))
    return out


def _bounds_from_questions(lexical: list[dict], duration: int) -> list[tuple[float, float, str]]:
    qs = question_marks(lexical)
    if not qs:
        return []
    edges = [max(0.0, q - LEAD_SEC) for q in qs] + [float(duration)]
    return [(edges[i], min(edges[i + 1], edges[i] + MAX_BLOCK), "")
            for i in range(len(edges) - 1)]


def split_blocks(signals: dict, cues: list[dict], duration: int,
                 topics: list[dict] | None = None) -> list[dict]:
    """ブロックに割る。スコアと risk を付けて返す。

    topics があればそれを境界にする。無ければ字幕の質問語から推定する。
    """
    comments = signals.get("comment_marks") or []
    heat = signals.get("heatmap") or []
    loud = signals.get("loudness") or []

    # **AVOID はここで毎回計算する。signals.json に焼き込まない。**
    # 焼き込んでいたときに事故った: 語彙を足したあと1本しか probe を回さず、
    # 残り4本は古い判定のまま候補に出た（脅迫性障害・母の虐待が素通りした）。
    # 語彙は実測のたびに増えるので、キャッシュしてよい種類のデータではない。
    # 語彙由来のものは全部ここで計算する。signals.json に残っているのは
    # 再計算が高くつくもの（音量・コメント・熱）だけにする
    from scripts.signals import AVOID, avoid_marks, lexical_marks

    avoid = avoid_marks(cues)
    lexical = lexical_marks(cues)

    # 語彙を出してから境界を決める。**順番が逆だと落ちる。**
    # 質問語からの推定は lexical を使うのに、定義より前で呼んでいた。
    # トピック無しの回をスキップしていたので発現していなかった（2026-08-14）
    if topics:
        bounds = _bounds_from_topics(topics, duration)
        source = "topics"
    else:
        bounds = _bounds_from_questions(lexical, duration)
        source = "subtitles"
    if not bounds:
        return []

    blocks: list[dict] = []
    for start_raw, end_raw, title in bounds:
        # 開始は手前へ、終端も手前へ寄せる。**終端を後ろへ寄せてはいけない。**
        # 次のトピックの開始を越えると、次の質問が見出しも解説も無いまま入る
        start = snap_to_cues(start_raw, cues, -1)
        end = snap_to_cues(end_raw, cues, -1)
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

        risk = {m["kind"] for m in avoid if start <= m["seconds"] <= end}
        words = {m["word"] for m in avoid if start <= m["seconds"] <= end}
        # タイトルがあるときはそこも見る。ASR字幕より綺麗なので精度が高い
        for kind, ws in AVOID.items():
            for w in ws:
                if title and w in title:
                    risk.add(kind)
                    words.add(w)

        score = (W_COMMENT * c_score + W_HEATMAP * h_score
                 + W_LOUD * l_score + W_ASSERT * n_assert
                 + W_EVIDENCE * n_evid)

        lines = [c["line"] for c in cues if start <= c["t"] <= end]
        blocks.append({
            "start": start,
            "end": end,
            "seconds": round(end - start, 1),
            "title": title,
            "source": source,
            "score": round(score, 3),
            "signals": {"コメント": c_score, "断言": n_assert, "根拠": n_evid,
                        "留保": n_hedge, "熱": round(h_score, 2),
                        "音量": round(l_score, 2)},
            "risk": sorted(risk),
            "risk_words": sorted(words),
            "question": title or "".join(lines[:6])[:120],
            # テーマ判定に使う本文。plan_episode は subtitles を捨てるので、
            # 判定に足りるぶんだけ別に持たせる
            "text": "".join(lines)[:1200],
            "subtitles": lines,
        })
    return blocks


# 質問の読み上げはこのくらいの長さ。ここにテーマ語が無ければ主題ではない
HEAD_CHARS = 180


def theme_hits(b: dict, words: list[str]) -> int:
    """このブロックがテーマ語に何回当たるか。

    **タイトルが無いブロックがある。** GCD の公式トピックが付いている回は
    タイトルで判定できるが、字幕から推定した回はタイトルが空になる。
    その場合は字幕本文で数える。本文は長いので、当たった語の種類を数える
    （同じ語が何度出ても1と数える）。
    """
    title = b.get("title") or ""
    if title:
        return sum(1 for w in words if w in title)
    text = b.get("text") or "".join(b.get("subtitles") or [])
    return sum(1 for w in words if w in text)


def by_theme(blocks: list[dict], words: list[str], ratio: float = 0.6) -> list[dict]:
    """テーマ語に合うブロックだけ残す。

    競合上位はどれも1テーマで束ねている（タトゥー／コンビニFC／不幸になる女性）。
    スコア上位を機械的に並べると話題がばらけて、まとめの言葉が書けない。

    **タイトル全体への部分一致では駄目だった。** 短いトピックは前のブロックに
    統合されて「A / B / C」という結合タイトルになる。どれか1つが当たれば通る
    判定にすると、223秒のうち大半が容姿の話のブロックが「起業」で引っかかって
    仕事テーマの回に混ざった（2026-08-14 実測）。

    トピックの過半数が当たることを求める。既定を0.6にしたのは、2トピックの
    結合で片方だけ当たった場合（1/2=0.5）を落とすため。
    """
    if not words:
        return blocks
    out = []
    for b in blocks:
        title = b.get("title") or ""
        if title:
            segs = [s for s in title.split(" / ") if s]
            hit = sum(1 for s in segs if any(w in s for w in words))
            if segs and hit / len(segs) >= ratio:
                out.append(b)
            continue
        # **タイトルが無い回は、質問文にテーマ語があることを求める。**
        # 本文のどこかに1語でもあれば通す判定にしたら、子育ての回に
        # 「フランスにクマ出ますか」「5.1チャンネル音響」が入った（2026-08-14）。
        # ブロックの冒頭は質問の読み上げで、そこが主題を決める。
        # 言及があるだけのブロックと、その話をしているブロックを分ける
        head = (b.get("text") or "")[:HEAD_CHARS]
        if not any(w in head for w in words):
            continue
        if theme_hits(b, words) >= 3:
            out.append(b)
    return out


# 信号がまったく無いブロックを尺合わせのために入れない。テーマ語の部分一致で
# 拾ってしまった無関係な回を落とす役目もある（「酵母の働き」が「働き」に当たった）
MIN_SCORE = 0.5


def bundle(blocks: list[dict], target_sec: float = 900.0,
           max_items: int = 12, allow_risky: bool = False) -> list[dict]:
    """スコアの高いブロックから、合計が target_sec に届くまで束ねる。

    **尺は13〜20分を狙う。** tora-kirinuki の実測で、この市場の検索上位は
    すべて14分以上だった。ひろゆき側の競合上位4本も同様の長尺構成。

    **並べ替えは score をそのまま使わない。** コメント言及は長いブロックほど
    多く入るので、生スコア順にすると長い数本だけで尺が埋まりチャプターが
    4本しか立たない。かといって毎分あたりの密度にすると45秒級の短い
    ブロックばかりが選ばれて合計尺が10分に届かない。
    実素材で比べた結果 sqrt(秒) で割るのが一番釣り合った（2026-08-14 実測）。

      生スコア順   4本 / 17.8分   チャプターが足りない
      密度順       8本 / 10.3分   尺が足りない
      sqrt順       7本 / 18.0分   ← これを採る
    """
    pool = [b for b in blocks
            if (allow_risky or not b["risk"]) and b["score"] >= MIN_SCORE]
    pool = sorted(pool, key=lambda b: -b["score"] / math.sqrt(max(b["seconds"], 1.0)))

    picked: list[dict] = []
    total = 0.0
    for b in pool:
        if len(picked) >= max_items or total >= target_sec:
            break
        picked.append(b)
        total += b["seconds"]
    return sorted(picked, key=lambda b: b["start"])
