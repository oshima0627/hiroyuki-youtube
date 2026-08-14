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

from scripts.fetch_source import ROOT, WORK  # noqa: E402
from scripts.qa import MIN_SCORE, by_theme, split_blocks  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


# **電話番号が未確認のチャンネルは15分を超える動画を上げられない。**
# 超えると処理の途中で削除される。900秒ぴったりを狙うと編集の誤差で割るので、
# 30秒の余裕を見る（2026-08-14 に16:36を上げて消された）
MAX_EPISODE_SEC = 870.0

# 解説板1枚あたりの実測平均。11枚で123秒だった（2026-08-14）
NOTE_SEC = 11.5


def hms(sec: float) -> str:
    s = int(sec)
    return f"{s // 3600:d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def used_ranges(exclude: Path | None) -> list[tuple[str, float, float]]:
    """既にレシピで使った区間を集める。

    **同じ話を2本目に入れない。** テーマを変えても素材は同じ5配信なので、
    「上司」「職場」のような語はどのテーマからも引ける。気づかずに前回と
    同じブロックを入れると、視聴者には使い回しに見える。
    """
    out: list[tuple[str, float, float]] = []
    for p in sorted((ROOT / "recipes").glob("*.json")):
        if exclude and p.resolve() == exclude.resolve():
            continue
        try:
            r = json.loads(p.read_text(encoding="utf-8"))
        except Exception:                                   # noqa: BLE001
            continue
        for c in r.get("clips") or []:
            if c.get("video_id") and c.get("start") is not None:
                out.append((c["video_id"], float(c["start"]), float(c["end"])))
    return out


def overlaps(b: dict, used: list[tuple[str, float, float]]) -> bool:
    return any(v == b["video_id"] and b["start"] < e and s < b["end"]
               for v, s, e in used)


def load_all() -> list[dict]:
    """work/ 配下の全動画からブロックを集める。"""
    out: list[dict] = []
    for d in sorted(WORK.iterdir()) if WORK.exists() else []:
        need = [d / n for n in ("signals.json", "subs.json", "meta.json")]
        if not all(p.exists() for p in need):
            continue
        signals, cues, meta = (json.loads(p.read_text(encoding="utf-8")) for p in need)
        # **公式トピックが無い回も使う。** GCD に載っているのは12本だけで
        # （ページ送りも無い、2026-08-14 実測）、共演2本を除くと10本しか
        # 使えない。一週間分に届かないので、字幕から推定した回も混ぜる。
        # ただし境界は粗く、見出しは自分で書くことになる
        tp = d / "topics.json"
        topics = json.loads(tp.read_text(encoding="utf-8")) if tp.exists() else None
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
    # **これは完成尺。本編の合計ではない。**
    # 解説板が後から乗るので、本編の合計で指定すると必ず超過する。
    # 実際に本編16:40のつもりが完成19分になり、15分の上限に引っかかって
    # YouTube に削除された（2026-08-14）
    ap.add_argument("--target", type=float, default=MAX_EPISODE_SEC,
                    help="**完成尺**（秒）。既定は15分の上限に対する安全側")
    ap.add_argument("--max-items", type=int, default=12)
    ap.add_argument("--allow-risky", action="store_true")
    ap.add_argument("--out", type=Path, help="構成案の保存先 JSON")
    ap.add_argument("--allow-used", action="store_true",
                    help="既に他のレシピで使った区間も候補に含める")
    a = ap.parse_args()

    blocks = load_all()
    if not blocks:
        raise SystemExit("! ブロックがありません。fetch_topics.py --save を先に実行してください")

    vids = {b["video_id"] for b in blocks}
    used = [] if a.allow_used else used_ranges(a.out)
    pool = [b for b in by_theme(blocks, a.theme)
            if (a.allow_risky or not b["risk"]) and b["score"] >= MIN_SCORE
            and not overlaps(b, used)]
    if used:
        print(f"（既に使った {len(used)}区間を除外）")

    # 同じ配信ばかりにならないよう、動画ごとに1本ずつ拾ってから2周目に入る。
    # 1本に偏ると「元動画へのリンク」が実質1本になり、束ねる意味が薄れる
    # 完成尺から解説板のぶんを引いて、本編に使える尺を出す。
    # 解説板はクリップ数＋まとめの1枚
    def clip_budget(n: int) -> float:
        return a.target - (n + 1) * NOTE_SEC

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
            if len(picked) >= a.max_items:
                break
            if total + b["seconds"] > clip_budget(len(picked) + 1):
                continue
            picked.append(b)
            seen.add(b["video_id"])
            total += b["seconds"]
        if len(picked) >= a.max_items:
            break

    picked.sort(key=lambda b: (b["video_id"], b["start"]))

    print(f"{len(blocks)}ブロック / {len(vids)}本の配信から、"
          f"テーマ {a.theme} に一致 {len(pool)}\n")
    for i, b in enumerate(picked, 1):
        print(f"{i:2d}. [{b['video_id']}] {hms(b['start'])}-{hms(b['end'])} "
              f"({b['seconds']:>4.0f}s) score={b['score']:5.2f}")
        print(f"     {b['title'][:74]}")
    est = total + (len(picked) + 1) * NOTE_SEC
    print(f"\n本編 {hms(total)} ＋ 解説板 {len(picked) + 1}枚 "
          f"→ 完成の見込み {hms(est)}（上限 {hms(MAX_EPISODE_SEC)}） / "
          f"{len({b['video_id'] for b in picked})}本の配信から")
    if est > MAX_EPISODE_SEC:
        print("! 15分の上限に近い。クリップを減らしてください")
    elif est < MAX_EPISODE_SEC * 0.85:
        print("! 短い。テーマ語を広げるか、配信をもっと取り込んでください")

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
