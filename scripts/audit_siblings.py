#!/usr/bin/env python3
"""同一 Google アカウント配下の4チャンネルを横並びで測る。
公開データなので、どのトークンでも取れる。"""
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from scripts.upload_youtube import get_service  # noqa: E402

yt = get_service()

HANDLES = ["@hiroyuki_kaisetsu", "@com.-meibamen",
           "@reiwanotora-second2", "@日本の最新ニュースまるわかり"]

for h in HANDLES:
    r = yt.channels().list(part="snippet,statistics,contentDetails,status",
                           forHandle=h).execute()
    it = r.get("items")
    if not it:
        print(f"\n### {h}: 取得できず")
        continue
    ch = it[0]
    st, s = ch["status"], ch["statistics"]
    print("\n" + "=" * 72)
    print(f"### {ch['snippet']['title']}  ({ch['id']})  {h}")
    print(f"開設 {ch['snippet']['publishedAt'][:10]}  登録 {s.get('subscriberCount')}  "
          f"公開本数 {s.get('videoCount')}  総視聴 {s.get('viewCount')}")
    print(f"longUploadsStatus={st.get('longUploadsStatus')}  "
          f"monetization={st.get('isChannelMonetizationEnabled')}")
    print("=" * 72)

    up = ch["contentDetails"]["relatedPlaylists"]["uploads"]
    vids, tok = [], None
    while True:
        p = yt.playlistItems().list(part="contentDetails", playlistId=up,
                                    maxResults=50, pageToken=tok).execute()
        vids += [i["contentDetails"]["videoId"] for i in p.get("items", [])]
        tok = p.get("nextPageToken")
        if not tok or len(vids) >= 250:
            break

    rows = []
    for i in range(0, len(vids), 50):
        d = yt.videos().list(part="snippet,statistics,contentDetails",
                             id=",".join(vids[i:i + 50])).execute()
        for v in d.get("items", []):
            rows.append((v["snippet"]["publishedAt"][:10],
                         v["contentDetails"]["duration"],
                         int(v["statistics"].get("viewCount", 0)),
                         v["snippet"]["title"][:38]))
    rows.sort(reverse=True)
    print(f"{'公開日':<12}{'尺':<10}{'視聴':>7}  タイトル")
    for d, dur, vc, t in rows[:40]:
        print(f"{d:<12}{dur:<10}{vc:>7}  {t}")
    if len(rows) > 40:
        print(f"... 他 {len(rows) - 40} 本")
