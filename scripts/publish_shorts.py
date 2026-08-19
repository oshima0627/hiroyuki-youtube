#!/usr/bin/env python3
"""組んだショートを、それぞれの時刻で予約公開する。

  python scripts/publish_shorts.py --dry-run
  python scripts/publish_shorts.py            # 上限5本まで
  python scripts/publish_shorts.py --limit 6

## クォータの歯止めが本体

`videos.insert` は **1,600ユニット**で、1日の上限は 10,000。つまり**1日6本**しか
上げられない。長尺も同じ枠を食うので、既定は**5本**にしてある。

1日2本を7日ぶん＝14本は、**1日では上げ切れない**。3日に分けて回すこと。
上げ終わったものは `state/published.json` に載るので、翌日そのまま再実行すれば
続きから上がる。

    8/19  python scripts/publish_shorts.py          → 5本（8/20朝〜8/22夜）
    8/20  python scripts/publish_shorts.py          → 5本（8/23朝〜8/25朝）
    8/21  python scripts/publish_shorts.py          → 4本（8/25夜〜8/26夜）

**予約時刻を過ぎたものは上げない。** publishAt に過去を渡すと即時公開になる。
気づかないうちに全部出てしまうので、ここで止める。

アップロードそのものは `upload_youtube.py` に委ねる。チャンネルの取り違え検出も
15分の上限も published.json への記録も、あちらに入っているものをそのまま使う。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SHORTS = ROOT / "recipes" / "shorts"
WORK = ROOT / "work" / "shorts"
PUBLISHED = ROOT / "state" / "published.json"
USED = ROOT / "state" / "used_shorts.json"

# videos.insert 1,600 × 6 = 9,600。10,000 の枠に長尺ぶんを1本残して5本
DEFAULT_LIMIT = 5


def load(path: Path, default):
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else default


def mark_used(recipe: dict) -> None:
    """使った窓を残す。次に plan_shorts.py を回したとき同じ区間を選ばせない。"""
    data = load(USED, {"windows": []})
    clip, short = recipe["clip"], recipe["short"]
    entry = {
        "short_id": recipe["id"],
        "video_id": clip["video_id"],
        "start": round(clip["start"] + short["start"], 2),
        "end": round(clip["start"] + short["end"], 2),
        "hook": short.get("hook", ""),
    }
    if not any(w.get("short_id") == entry["short_id"] for w in data["windows"]):
        data["windows"].append(entry)
    USED.parent.mkdir(parents=True, exist_ok=True)
    USED.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=DEFAULT_LIMIT,
                    help=f"1回に上げる本数の上限（既定 {DEFAULT_LIMIT}。クォータの歯止め）")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    pub = load(PUBLISHED, {"videos": {}}).get("videos", {})
    now = datetime.now(timezone.utc)

    queue, done, skipped = [], [], []
    for path in sorted(SHORTS.glob("*.json")):
        recipe = json.loads(path.read_text(encoding="utf-8"))
        rid = recipe["id"]
        at = datetime.strptime(recipe["publish_at"],
                               "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        if rid in pub:
            done.append(rid)
        elif not (WORK / rid / "video.mp4").exists():
            skipped.append((rid, "video.mp4 が無い。build_short.py を先に"))
        elif at <= now:
            skipped.append((rid, f"予約時刻 {at:%m/%d %H:%M}Z を過ぎている"))
        else:
            queue.append((path, recipe, at))

    print(f"投稿済み {len(done)} / 待ち {len(queue)} / 保留 {len(skipped)}")
    for rid, why in skipped:
        print(f"  保留 {rid}  {why}")

    batch = queue[:a.limit]
    if len(queue) > a.limit:
        print(f"\n! {len(queue) - a.limit}本はクォータのため今回は上げない。"
              "明日そのまま再実行すれば続きから上がる")

    for path, recipe, at in batch:
        rid = recipe["id"]
        jst = at + timedelta(hours=9)
        print(f"\n── {rid}  公開 {jst:%m/%d %H:%M} JST  「{recipe['short']['hook']}」")
        if a.dry_run:
            continue
        cmd = [sys.executable, str(ROOT / "scripts" / "upload_youtube.py"),
               str(WORK / rid), "--schedule", recipe["publish_at"]]
        if subprocess.run(cmd, cwd=ROOT).returncode != 0:
            print(f"✗ {rid} で失敗した。ここで止める（残りは次回）")
            sys.exit(1)
        mark_used(recipe)

    if a.dry_run:
        print(f"\n[dry-run] {len(batch)}本を上げるところだった")


if __name__ == "__main__":
    main()
