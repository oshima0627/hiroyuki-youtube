#!/usr/bin/env python3
"""アカウント側の事実を API から取る。推測しない。取れたものだけ出す。"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from scripts.upload_youtube import CHANNEL_ID, get_service  # noqa: E402

yt = get_service()

print("=" * 70)
print("1. チャンネル本体 channels.list(mine=true)")
print("=" * 70)
r = yt.channels().list(
    part="snippet,status,statistics,contentDetails,brandingSettings,topicDetails",
    mine=True).execute()
for ch in r.get("items", []):
    print(json.dumps(ch, ensure_ascii=False, indent=2))

items = r.get("items", [])
if not items:
    print("!! チャンネルが取れない")
    sys.exit(1)
ch = items[0]
print(f"\n--- 要点 ---")
print(f"id                     : {ch['id']}  (期待 {CHANNEL_ID})")
st = ch.get("status", {})
print(f"privacyStatus          : {st.get('privacyStatus')}")
print(f"isLinked               : {st.get('isLinked')}")
print(f"longUploadsStatus      : {st.get('longUploadsStatus')}   # allowed=電話確認済 / eligible=未実行 / disallowed")
print(f"madeForKids            : {st.get('madeForKids')}")
print(f"selfDeclaredMadeForKids: {st.get('selfDeclaredMadeForKids')}")
bs = ch.get("brandingSettings", {}).get("channel", {})
print(f"country                : {bs.get('country')}")
print(f"defaultLanguage        : {bs.get('defaultLanguage')}")
print(f"keywords               : {bs.get('keywords')}")
print(f"statistics             : {ch.get('statistics')}")

uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]

print()
print("=" * 70)
print("2. 全アップロード動画の status / contentDetails")
print("=" * 70)
vids, token = [], None
while True:
    p = yt.playlistItems().list(part="contentDetails", playlistId=uploads,
                                maxResults=50, pageToken=token).execute()
    vids += [i["contentDetails"]["videoId"] for i in p.get("items", [])]
    token = p.get("nextPageToken")
    if not token:
        break
print(f"アップロード playlist の本数: {len(vids)}")

detail = []
for i in range(0, len(vids), 50):
    d = yt.videos().list(part="snippet,status,statistics,contentDetails",
                         id=",".join(vids[i:i + 50])).execute()
    detail += d.get("items", [])

for v in detail:
    s, sn, cd = v["status"], v["snippet"], v["contentDetails"]
    print(f"\n[{v['id']}] {sn['title'][:44]}")
    print(f"  publishedAt {sn['publishedAt']}  尺 {cd.get('duration')}  cat {sn.get('categoryId')}")
    print(f"  uploadStatus={s.get('uploadStatus')} privacy={s.get('privacyStatus')} "
          f"license={s.get('license')} embeddable={s.get('embeddable')}")
    print(f"  madeForKids={s.get('madeForKids')} selfDeclared={s.get('selfDeclaredMadeForKids')}")
    if s.get("failureReason") or s.get("rejectionReason"):
        print(f"  !! failureReason={s.get('failureReason')} rejectionReason={s.get('rejectionReason')}")
    if cd.get("regionRestriction"):
        print(f"  !! regionRestriction={cd['regionRestriction']}")
    if cd.get("contentRating"):
        print(f"  !! contentRating={cd['contentRating']}")
    print(f"  licensedContent={cd.get('licensedContent')}  defaultAudioLanguage={sn.get('defaultAudioLanguage')}")
    print(f"  tags={ (sn.get('tags') or [])[:8] }")
    print(f"  stats={v.get('statistics')}")
