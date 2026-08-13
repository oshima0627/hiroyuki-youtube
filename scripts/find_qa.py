#!/usr/bin/env python3
"""配信を1問1答に割って候補を出す。tora-kirinuki の find_moments.py に相当。

  python scripts/find_qa.py <video_id>
  python scripts/find_qa.py <video_id> --target 900 --max-items 8
  python scripts/find_qa.py <video_id> --all          # 束ねずに全ブロックを出す
  python scripts/find_qa.py <video_id> --allow-risky  # 要注意ブロックも含める

出力は work/<video_id>/blocks.json。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fetch_source import source_dir  # noqa: E402
from scripts.qa import bundle, by_theme, split_blocks  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def hms(sec: float) -> str:
    s = int(sec)
    return f"{s // 3600:d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def show(blocks: list[dict], duration: int) -> None:
    for i, b in enumerate(blocks, 1):
        s = b["signals"]
        pos = b["start"] / duration * 100 if duration else 0
        flag = ("  ⚠" + "/".join(b["risk"])) if b["risk"] else ""
        print(f"{i:2d}. {hms(b['start'])}-{hms(b['end'])} "
              f"({b['seconds']:>5.0f}s) {pos:3.0f}%  score={b['score']:5.2f}  "
              f"[コメ{s['コメント']} 断{s['断言']} 根{s['根拠']} 留{s['留保']} "
              f"熱{s['熱']}]{flag}")
        print(f"      {b['question'][:78]}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("video_id")
    # 13〜20分を狙う。tora-kirinuki の実測でこの市場の検索上位はすべて14分以上。
    # ひろゆき側の競合上位4本も同じく長尺・チャプター構成だった（2026-08-14 実測）
    ap.add_argument("--target", type=float, default=900.0,
                    help="束ねたときの目標尺（秒）。相場は13〜20分")
    ap.add_argument("--max-items", type=int, default=12)
    ap.add_argument("--all", action="store_true", help="束ねずに全ブロックを出す")
    ap.add_argument("--allow-risky", action="store_true",
                    help="政治・個人・センシティブに触れるブロックも含める")
    # 競合上位はどれも1テーマで束ねている。スコア順に並べるだけだと話題がばらけて
    # まとめの言葉が書けない（2026-08-14 実測）
    ap.add_argument("--theme", nargs="+", default=[],
                    help="タイトルにこの語を含むブロックだけから選ぶ（例: --theme 仕事 転職 会社）")
    a = ap.parse_args()

    d = source_dir(a.video_id)
    for name in ("signals.json", "subs.json", "meta.json"):
        if not (d / name).exists():
            raise SystemExit(
                f"! {d / name} が無い。fetch_source.py と probe_signals.py を先に実行してください")

    signals = json.loads((d / "signals.json").read_text(encoding="utf-8"))
    cues = json.loads((d / "subs.json").read_text(encoding="utf-8"))
    meta = json.loads((d / "meta.json").read_text(encoding="utf-8"))
    duration = int(meta.get("duration_sec") or 0)

    tp = d / "topics.json"
    topics = json.loads(tp.read_text(encoding="utf-8")) if tp.exists() else None
    if not topics:
        print("- 公式トピックが無いので字幕から推定します（fetch_topics.py --save を試してください）")

    blocks = split_blocks(signals, cues, duration, topics)
    (d / "blocks.json").write_text(
        json.dumps(blocks, ensure_ascii=False, indent=1), encoding="utf-8")

    if not blocks:
        print("! ブロックが0件。signals.json と topics.json を確認してください")
        return

    risky = [b for b in blocks if b["risk"]]
    src = blocks[0].get("source")
    print(f"{len(blocks)}ブロック（うち要注意 {len(risky)}）  尺 {hms(duration)}  境界={src}\n")

    if a.all:
        show(blocks, duration)
    else:
        pool = by_theme(blocks, a.theme)
        if a.theme:
            print(f"テーマ {a.theme} に一致: {len(pool)}ブロック\n")
        picked = bundle(pool, a.target, a.max_items, a.allow_risky)
        total = sum(b["seconds"] for b in picked)
        show(picked, duration)
        print(f"\n束ねた尺: {hms(total)}（目標 {hms(a.target)}）")
        if total < a.target * 0.8:
            print("! 目標に届いていません。--max-items を増やすか、別の配信も併用してください")

    if risky and not a.allow_risky:
        print(f"\n除外した要注意ブロック {len(risky)}件:")
        for b in risky[:8]:
            print(f"  {hms(b['start'])} ⚠{'/'.join(b['risk'])} "
                  f"({', '.join(b['risk_words'][:4])})")


if __name__ == "__main__":
    main()
