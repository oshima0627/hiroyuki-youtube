#!/usr/bin/env python3
"""複数の配信をまたいでテーマで束ね、1本ぶんの構成案を出す。

  python scripts/plan_episode.py --theme 仕事 転職 会社 --target 1000
  python scripts/plan_episode.py --theme 恋愛 結婚 --out recipes/ep002.json

**1本の配信だけでは13〜20分に届かない。** 実測（2026-08-14）で
`23vSB2fXjc8`（3時間23分）から仕事テーマで拾えたのは11分56秒だった。
話題が毎回散らばるので、テーマを絞るほど1本あたりの収量は落ちる。

ひろゆき側の許諾条件には、令和の虎ガイドラインにある
「分割された本編を連結した投稿の禁止」に当たるものが無い。
競合（きりゆき等）も配信をまたいで束ねている。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fetch_source import WORK  # noqa: E402
from scripts.qa import MIN_SCORE, by_theme, split_blocks  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def hms(sec: float) -> str:
    s = int(sec)
    return f"{s // 3600:d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def load_all() -> list[dict]:
    """work/ 配下の全動画からブロックを集める。"""
    out: list[dict] = []
    for d in sorted(WORK.iterdir()) if WORK.exists() else []:
        need = [d / n for n in ("signals.json", "subs.json", "meta.json")]
        if not all(p.exists() for p in need):
            continue
        signals, cues, meta = (json.loads(p.read_text(encoding="utf-8")) for p in need)
        tp = d / "topics.json"
        topics = json.loads(tp.read_text(encoding="utf-8")) if tp.exists() else None
        if not topics:
            continue                       # 公式トピックが無い回はここでは使わない
        for b in split_blocks(signals, cues, int(meta.get("duration_sec") or 0), topics):
            b["video_id"] = meta["video_id"]
            b["video_title"] = meta.get("title") or ""
            b["video_url"] = meta.get("url") or ""
            b["subtitles"] = []            # 構成案には要らない。ファイルが太るだけ
            out.append(b)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", nargs="+", required=True)
    ap.add_argument("--target", type=float, default=1000.0,
                    help="目標尺（秒）。相場は13〜20分なので既定は約17分")
    ap.add_argument("--max-items", type=int, default=12)
    ap.add_argument("--allow-risky", action="store_true")
    ap.add_argument("--out", type=Path, help="構成案の保存先 JSON")
    a = ap.parse_args()

    blocks = load_all()
    if not blocks:
        raise SystemExit("! ブロックがありません。fetch_topics.py --save を先に実行してください")

    vids = {b["video_id"] for b in blocks}
    pool = [b for b in by_theme(blocks, a.theme)
            if (a.allow_risky or not b["risk"]) and b["score"] >= MIN_SCORE]

    # 同じ配信ばかりにならないよう、動画ごとに1本ずつ拾ってから2周目に入る。
    # 1本に偏ると「元動画へのリンク」が実質1本になり、束ねる意味が薄れる
    ranked = sorted(pool, key=lambda b: -b["score"] / max(b["seconds"], 1) ** 0.5)
    picked: list[dict] = []
    total = 0.0
    seen: set[str] = set()
    for rnd in range(4):
        for b in ranked:
            if b in picked:
                continue
            if rnd == 0 and b["video_id"] in seen:
                continue
            if len(picked) >= a.max_items or total >= a.target:
                break
            picked.append(b)
            seen.add(b["video_id"])
            total += b["seconds"]
        if len(picked) >= a.max_items or total >= a.target:
            break

    picked.sort(key=lambda b: (b["video_id"], b["start"]))

    print(f"{len(blocks)}ブロック / {len(vids)}本の配信から、"
          f"テーマ {a.theme} に一致 {len(pool)}\n")
    for i, b in enumerate(picked, 1):
        print(f"{i:2d}. [{b['video_id']}] {hms(b['start'])}-{hms(b['end'])} "
              f"({b['seconds']:>4.0f}s) score={b['score']:5.2f}")
        print(f"     {b['title'][:74]}")
    print(f"\n合計 {hms(total)}（目標 {hms(a.target)}） / "
          f"{len({b['video_id'] for b in picked})}本の配信から")
    if total < a.target * 0.8:
        print("! 届いていません。テーマ語を広げるか、配信をもっと取り込んでください")

    if a.out:
        a.out.parent.mkdir(parents=True, exist_ok=True)
        a.out.write_text(json.dumps({
            "theme": a.theme,
            "target_sec": a.target,
            "total_sec": round(total, 1),
            "clips": picked,
        }, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"→ {a.out}")


if __name__ == "__main__":
    main()
