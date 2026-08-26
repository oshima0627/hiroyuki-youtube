#!/usr/bin/env python3
"""組んだショートを、それぞれの時刻で予約公開する。

  python scripts/publish_shorts.py --dry-run
  python scripts/publish_shorts.py            # 上限5本まで
  python scripts/publish_shorts.py --limit 6

## 効く上限は API クォータではない（2026-08-26 に実測して前提を訂正）

**当初ここには「videos.insert は 1,600 ユニット、1日の枠 10,000 なので1日6本が上限」と
書いていた。実測すると違った。**

同じクォータ日（PT の 0:00 を跨いでいないことを確認済み）に **22本が通り、23本目で落ちた。**
落ち方は 400 で、内容は:

    uploadLimitExceeded / "The user has exceeded the number of videos they may upload."

これは **YouTube 側の「1日にアップロードできる本数」**の上限で、API クォータとは別物。
電話番号が未確認のチャンネルは本数が絞られる。**実測値は 22本/日**（変動しうる）。

前提が6本だったせいで既定が5本になり、「毎日回さないとキューが排けない」運用になっていた。
**それが 2026-08-25 に投稿が途切れた原因。** 14本ビルドして5本しか上がっていなかった。

上げ終わったものは `state/published.json` に載る。上限に当たったら 400 で綺麗に止まるので、
そのまま再実行すれば続きから上がる。

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

# 実測の上限は 22本/日（2026-08-26）。変動しうるので手前で止める。
# 足りなければ --limit で上げる。当たっても 400 で綺麗に止まるので損はしない
DEFAULT_LIMIT = 15


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
        print(f"\n! {len(queue) - a.limit}本は --limit のため今回は上げない。"
              "そのまま再実行すれば続きから上がる")

    for path, recipe, at in batch:
        rid = recipe["id"]
        jst = at + timedelta(hours=9)
        print(f"\n── {rid}  公開 {jst:%m/%d %H:%M} JST  「{recipe['short']['hook']}」")
        if a.dry_run:
            continue
        cmd = [sys.executable, str(ROOT / "scripts" / "upload_youtube.py"),
               str(WORK / rid), "--schedule", recipe["publish_at"]]
        if subprocess.run(cmd, cwd=ROOT).returncode != 0:
            print(f"✗ {rid} で失敗した。ここで止める（残りは次回）\n"
                  "  uploadLimitExceeded なら YouTube 側の1日の本数上限。"
                  "翌日そのまま再実行すれば続きから上がる")
            sys.exit(1)
        mark_used(recipe)

    if a.dry_run:
        print(f"\n[dry-run] {len(batch)}本を上げるところだった")


if __name__ == "__main__":
    main()
