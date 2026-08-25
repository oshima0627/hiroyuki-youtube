#!/usr/bin/env python3
"""公開済みの動画にサムネイルを後から設定する。

  python scripts/set_thumbnails.py --dry-run          # 対象を並べるだけ
  python scripts/set_thumbnails.py --only <id>        # 1本だけ
  python scripts/set_thumbnails.py                    # 未設定のものを全部

**アップロード時に設定できなかったぶんを埋めるための経路。**
`upload_youtube.py` の `set_thumbnail()` は失敗しても動画を止めない作りなので、
`thumbnail_set: false` のまま公開まで進む。実際に8本すべてが false のまま
自動生成フレームで公開されていた（2026-08-25 に Studio で確認）。
そのぶん本編とサムネイルが噛み合わず、8/15 の回は 1.7万インプレッションに
対して CTR 1.5% だった。

## 設定できたかどうかを API の戻り値だけで判断しない

`thumbnails().set()` は例外を投げなければ成功に見えるが、それは
「リクエストが通った」だけで、実際に差し替わったかは別。ここでは設定後に
`videos.list` からサムネイル画像を取り直し、手元の thumb.png と
画素で突き合わせて差分を出す。**差分が小さいことをもって設定済みと呼ぶ。**

## 電話番号が未確認だとカスタムサムネイルは使えない

15分超のアップロードと同じ制限。403 が返るので、そのときは何本流しても
通らない。1本目で止めて、確認を促す。
https://support.google.com/youtube/answer/9795415
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import time
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from scripts.upload_youtube import (  # noqa: E402
    PUBLISHED, ROOT, assert_expected_channel, get_service,
)

WORK = ROOT / "work"
SLEEP_SEC = 3.0          # 連続で差し替えると 429 が返るので間を置く


def load() -> dict:
    return (json.loads(PUBLISHED.read_text(encoding="utf-8-sig"))
            if PUBLISHED.exists() else {"videos": {}})


def save(data: dict) -> None:
    PUBLISHED.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def targets(data: dict, only: str | None, force: bool) -> list[tuple[str, dict, Path]]:
    out = []
    for vid_key, rec in data.get("videos", {}).items():
        if only and vid_key != only:
            continue
        if not rec.get("youtube_video_id"):
            continue
        if rec.get("thumbnail_set") and not force:
            continue
        thumb = WORK / vid_key / "thumb.png"
        if not thumb.exists():
            print(f"- {vid_key}: thumb.png が無いので飛ばす")
            continue
        out.append((vid_key, rec, thumb))
    return out


def verify(service, video_id: str, local: Path) -> float | None:
    """設定後のサムネイルを取り直して手元の画像と突き合わせ、平均差分を返す。

    0 に近いほど手元の thumb.png が反映されている。JPEG 圧縮と縮小が挟まるので
    完全一致にはならない。実測では同一画像で 5 前後、別画像で 40 以上になる。
    """
    from PIL import Image, ImageChops, ImageStat

    r = service.videos().list(part="snippet", id=video_id).execute()
    items = r.get("items") or []
    if not items:
        return None
    thumbs = items[0]["snippet"]["thumbnails"]
    url = (thumbs.get("maxres") or thumbs.get("standard")
           or thumbs.get("high"))["url"]
    with urllib.request.urlopen(url, timeout=30) as fh:
        remote = Image.open(io.BytesIO(fh.read())).convert("RGB")
    mine = Image.open(local).convert("RGB").resize(remote.size, Image.LANCZOS)
    diff = ImageChops.difference(remote, mine)
    return sum(ImageStat.Stat(diff).mean) / 3


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", help="published.json のキー（例 2026-08-18-france）")
    ap.add_argument("--force", action="store_true",
                    help="thumbnail_set が true でも設定し直す")
    ap.add_argument("--dry-run", action="store_true", help="対象を並べるだけ")
    a = ap.parse_args()

    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    data = load()
    todo = targets(data, a.only, a.force)
    if not todo:
        print("対象がありません")
        return

    print(f"対象 {len(todo)} 本:")
    for key, rec, thumb in todo:
        print(f"  {key}  {rec['youtube_video_id']}  {rec['title']}")
    if a.dry_run:
        return

    service = get_service()
    assert_expected_channel(service, {})

    ok = 0
    for i, (key, rec, thumb) in enumerate(todo):
        vid = rec["youtube_video_id"]
        print(f"\n== {key} ({vid})")
        try:
            service.thumbnails().set(
                videoId=vid, media_body=MediaFileUpload(str(thumb))).execute()
        except HttpError as e:
            print(f"  ✗ 設定できません: {e}")
            if "403" in str(e):
                print("  電話番号の確認が済んでいない可能性があります。"
                      "確認せずに続けても他の動画でも通りません。ここで止めます。")
                break
            if "429" in str(e):
                print("  差し替えの回数制限です。時間を置いて再実行してください。")
                break
            continue

        d = verify(service, vid, thumb)
        if d is None:
            print("  ! 反映を確認できませんでした（videos.list が空）")
            continue
        print(f"  平均差分 {d:.1f}")
        if d > 25:
            print("  ! 差分が大きい。反映が遅れているか別の画像です")
            continue
        rec["thumbnail_set"] = True
        ok += 1
        print("  ✓ 設定しました")
        if i < len(todo) - 1:
            time.sleep(SLEEP_SEC)

    save(data)
    print(f"\n{ok}/{len(todo)} 本を設定しました")


if __name__ == "__main__":
    main()
