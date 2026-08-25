#!/usr/bin/env python3
"""検索語ごとに1本ぶんの構成案を出す。

  python scripts/plan_keyword.py                          # 候補の検索語を並べる
  python scripts/plan_keyword.py --word NISA              # その語で組んで表示
  python scripts/plan_keyword.py --word NISA --out recipes/2026-08-26-nisa.json

## なぜ「テーマ」ではなく「検索語」で束ねるのか

2026-08-25 の実測で、このチャンネルに配信がほとんど回っていないことが分かった。
8/18 の長尺はインプレッション17、8/19 は6。ショートも最多の1本で
ショートフィードからの流入は11.8%（≒2回）しかなく、残りの **76.5% は YouTube 検索**
だった（検索語: 税理士試験 / 簿記1級 / 日商簿記1級）。

電話番号の確認が上限でカスタムサムネイルが使えず、CTR 側のレバーは閉じている。
**いま操作できるのは検索だけ。** だからタイトルに検索語を置ける単位で束ねる。

「仕事の相談10連発」はどの検索語とも一致しない。「NISA」なら一致する。

## なぜ「1問1本」ではないのか

**1問はそもそも1分前後しかない。** 実測（2026-08-25、work/ の43本・1504ブロック）で、
単一トピックかつ検索語がタイトルに入るブロックは13件、尺は43〜118秒で、
120秒を超えるものは1つも無かった。

2〜4分にするには解説板を10枚近く積むことになり、「1分の素材＋文字スライド」になる。
総集編より悪い。そこで **同じ検索語を共有する2〜4問**を1本にする。
1本が1つの検索意図に対応していれば、タイトルは検索語で書ける。

## 束ねるのはタイトル一致だけ

字幕（ASR）で一度触れただけの語で束ねると主題がずれる。実際に字幕一致で束ねたとき、
「看護師」の回に「サグラダ・ファミリア完成と『未完成のロマン』」が入った（2026-08-25 実測）。
ASR は固有名詞も崩すので、字幕側の一致は語彙を育てる手がかりに留める。

## 複数トピックを結合したブロックは使わない

`split_blocks` は近いトピックを結合するので、タイトルが " / " で連なったブロックができる。
それは中身が小さな総集編で、検索語の数だけは多くなる。語数で並べると上位を占めてしまう。
**単一トピックのブロックだけを候補にする。**
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from scripts.plan_episode import NOTE_SEC, hms, load_all, overlaps, used_ranges  # noqa: E402
from scripts.qa import MIN_SCORE  # noqa: E402

# 完成尺の目安。上限ではなく「これを超えたらクリップを減らす」の目印。
# 15分の制約とは別で、検索から来た人が1つの疑問を解くのに付き合う長さ。
TARGET_SEC = 360.0
MAX_ITEMS = 4


def candidates(exclude: Path | None, allow_used: bool) -> list[dict]:
    """1問1トピックで、検索語を持ち、使えるブロックだけを返す。"""
    used = [] if allow_used else used_ranges(exclude)
    out = []
    for b in load_all():
        title = b.get("title") or ""
        if not title or " / " in title:      # 結合ブロックは小さな総集編
            continue
        if b["risk"] or b["score"] < MIN_SCORE or not b["search_title_words"]:
            continue
        if overlaps(b, used):
            continue
        out.append(b)
    return out


def group(pool: list[dict]) -> dict[str, list[dict]]:
    g: dict[str, list[dict]] = defaultdict(list)
    for b in pool:
        # **タイトル一致だけで束ねる。** 字幕一致は主題の保証にならない
        for w in b["search_title_words"]:
            g[w].append(b)
    return g


def pick(blocks: list[dict], target: float, max_items: int) -> list[dict]:
    """スコアの高い順に、完成尺の目安に収まるだけ取る。"""
    picked: list[dict] = []
    total = 0.0
    for b in sorted(blocks, key=lambda x: -x["score"]):
        if len(picked) >= max_items:
            break
        est = total + b["seconds"] + (len(picked) + 2) * NOTE_SEC
        if picked and est > target:
            continue
        picked.append(b)
        total += b["seconds"]
    picked.sort(key=lambda b: (b["video_id"], b["start"]))
    return picked


def est_sec(picked: list[dict]) -> float:
    return sum(b["seconds"] for b in picked) + (len(picked) + 1) * NOTE_SEC


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--word", help="束ねる検索語。省くと候補を並べるだけ")
    ap.add_argument("--target", type=float, default=TARGET_SEC,
                    help="完成尺の目安（秒）")
    ap.add_argument("--max-items", type=int, default=MAX_ITEMS)
    ap.add_argument("--out", type=Path, help="構成案の保存先 JSON")
    ap.add_argument("--allow-used", action="store_true",
                    help="既に他のレシピで使った区間も候補に含める")
    a = ap.parse_args()

    pool = candidates(a.out, a.allow_used)
    if not pool:
        raise SystemExit("! 候補がありません。fetch_topics.py --save を先に実行してください")
    g = group(pool)

    if not a.word:
        rows = []
        for w, bl in g.items():
            picked = pick(bl, a.target, a.max_items)
            if len(picked) >= 2:
                rows.append((est_sec(picked), len(picked), w))
        rows.sort(key=lambda r: -r[0])
        print(f"候補 {len(pool)}ブロック / 2問以上を組める検索語 {len(rows)}語\n")
        for est, n, w in rows:
            print(f"  {w:<18} {n}問  最短 {hms(est)[2:]}")
        print("（最短＝解説板が1問1枚のとき。notes を増やすぶん実際は伸びます）")
        print("\n--word <語> で組んでください")
        return

    if a.word not in g:
        raise SystemExit(f"! 「{a.word}」の候補がありません。--word 無しで一覧を見てください")

    picked = pick(g[a.word], a.target, a.max_items)
    if len(picked) < 2:
        print(f"! 「{a.word}」は{len(picked)}問しか取れません。1本にするには薄いです")

    print(f"検索語「{a.word}」 {len(picked)}問\n")
    for i, b in enumerate(picked, 1):
        print(f"{i:2d}. [{b['video_id']}] {hms(b['start'])}-{hms(b['end'])} "
              f"({b['seconds']:>4.0f}s) score={b['score']:5.2f}")
        print(f"     {b['title'][:74]}")
        print(f"     語: {'、'.join(b['search_title_words'])}")
    est = est_sec(picked)
    print(f"\n本編 {hms(sum(b['seconds'] for b in picked))} ＋ 解説板 {len(picked) + 1}枚 "
          f"→ 完成は最短 {hms(est)} / "
          f"{len({b['video_id'] for b in picked})}本の配信から")
    print("（板を1問1枚で数えた下限。recipe.py は3問以下のとき板を合計4枚以上求めます）")
    print(f"タイトルには「{a.word}」を必ず入れること。それがこの構成の目的です")

    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps({
            "keyword": a.word,
            "target_sec": a.target,
            "total_sec": round(sum(b["seconds"] for b in picked), 1),
            "clips": picked,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"→ {a.out}")


if __name__ == "__main__":
    main()
