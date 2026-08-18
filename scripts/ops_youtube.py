#!/usr/bin/env python3
"""公開後の運用。状態の同期・再生リスト・回遊導線。

  python scripts/ops_youtube.py --status              # 実状態を見て published.json を直す
  python scripts/ops_youtube.py --playlist            # 再生リストを作って全話を入れる
  python scripts/ops_youtube.py --crosslink           # 概要欄に他の回への導線を足す
  python scripts/ops_youtube.py --status --playlist --crosslink

**published.json は投稿時の申告であって、実状態ではない。**
予約公開が発火しても誰も書き戻さないので、`privacy_status` は private の
まま古くなる（2026-08-17 に実測。EP003・EP004 が public になっていたのに
記録は private のままだった）。運用の判断はこのファイルを見て行うので、
実状態を取りに行って上書きする経路を用意する。

クォータは videos.list が1、videos.update と playlists 系が50。
videos.insert の1,600に比べれば無視できるが、`--crosslink` は本数ぶん
videos.update を撃つので、毎日回すものではない。
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from scripts.upload_youtube import CHANNEL_ID, PUBLISHED, get_service  # noqa: E402

PLAYLIST_TITLE = "ひろゆきの相談まとめ（解説つき）"
PLAYLIST_DESC = ("ひろゆきさんの配信から、テーマごとに相談を集めて解説を付けた回のまとめです。\n"
                 "本チャンネルはガジェット通信クリエイターネットワークに申請済みの"
                 "切り抜きチャンネルです。公式チャンネルではありません。")

CROSSLINK_HEAD = "【このチャンネルの他の回】"


def load_published() -> dict:
    return (json.loads(PUBLISHED.read_text(encoding="utf-8-sig"))
            if PUBLISHED.exists() else {"videos": {}})


def save_published(data: dict) -> None:
    PUBLISHED.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fetch_videos(service, ids: list[str]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for i in range(0, len(ids), 50):
        r = service.videos().list(part="snippet,status,statistics,contentDetails",
                                  id=",".join(ids[i:i + 50])).execute()
        for v in r.get("items", []):
            out[v["id"]] = v
    return out


def cmd_status(service, data: dict) -> dict[str, dict]:
    """実状態を取って published.json を書き戻す。"""
    ids = [e["youtube_video_id"] for e in data["videos"].values()
           if e.get("youtube_video_id")]
    live = fetch_videos(service, ids)

    print(f"{'ID':<12} {'公開状態':<10} {'尺':<8} {'再生':>6}  タイトル")
    for key, e in data["videos"].items():
        vid = e.get("youtube_video_id")
        v = live.get(vid)
        if not v:
            # 15分超で処理中止になった動画は videos.list から消える。
            # 記録だけ残っていても実体が無いので、消えたことを残す
            e["privacy_status"] = "missing"
            print(f"{vid:<12} {'見つからない':<10} {'-':<8} {'-':>6}  {key}")
            continue
        st, sn = v["status"], v["snippet"]
        e["privacy_status"] = st["privacyStatus"]
        e["publish_at"] = st.get("publishAt")
        e["published_at"] = sn["publishedAt"]
        e["upload_status"] = st["uploadStatus"]
        e["view_count"] = int(v.get("statistics", {}).get("viewCount", 0))
        e["duration"] = v["contentDetails"]["duration"]
        e["title"] = sn["title"]
        sched = f"→{st['publishAt'][:16]}" if st.get("publishAt") else ""
        print(f"{vid:<12} {st['privacyStatus'] + sched:<10} "
              f"{e['duration'][2:]:<8} {e['view_count']:>6}  {sn['title'][:40]}")
    save_published(data)
    print(f"\n✓ {PUBLISHED.name} を実状態で更新しました")
    return live


def find_playlist(service, title: str) -> str | None:
    token = None
    while True:
        r = service.playlists().list(part="snippet", mine=True, maxResults=50,
                                     pageToken=token).execute()
        for p in r.get("items", []):
            if p["snippet"]["title"] == title:
                return p["id"]
        token = r.get("nextPageToken")
        if not token:
            return None


def cmd_playlist(service, data: dict) -> None:
    """再生リストを作り、長尺の回を古い順に入れる。

    **ショートは入れない。** ショート面と通常の再生リストは導線が別で、
    混ぜると再生リストの連続再生に縦型が挟まる。
    """
    pid = find_playlist(service, PLAYLIST_TITLE)
    if pid is None:
        pid = service.playlists().insert(part="snippet,status", body={
            "snippet": {"title": PLAYLIST_TITLE, "description": PLAYLIST_DESC,
                        "defaultLanguage": "ja"},
            "status": {"privacyStatus": "public"},
        }).execute()["id"]
        print(f"✓ 再生リストを作成: {pid}")
    else:
        print(f"- 既存の再生リストを使います: {pid}")

    # **作った直後は playlistItems.list が 404 を返す。**
    # 反映まで数秒かかるだけで、リスト自体は存在する（2026-08-17 実測）。
    # 空として扱えば、そのまま追加に進める
    from googleapiclient.errors import HttpError

    have, token = set(), None
    while True:
        try:
            r = service.playlistItems().list(
                part="contentDetails", playlistId=pid,
                maxResults=50, pageToken=token).execute()
        except HttpError as e:
            if e.status_code == 404:
                print("- 作成直後で中身を取れないので、空として扱います")
                break
            raise
        have |= {i["contentDetails"]["videoId"] for i in r.get("items", [])}
        token = r.get("nextPageToken")
        if not token:
            break

    targets = [(k, e) for k, e in data["videos"].items()
               if not k.endswith("-short")
               and e.get("privacy_status") in ("public", "unlisted", "private")
               and e.get("youtube_video_id")]
    targets.sort(key=lambda kv: kv[0])
    for key, e in targets:
        vid = e["youtube_video_id"]
        if vid in have:
            print(f"- {key} は追加済み")
            continue
        service.playlistItems().insert(part="snippet", body={
            "snippet": {"playlistId": pid, "resourceId": {
                "kind": "youtube#video", "videoId": vid}},
        }).execute()
        print(f"✓ {key} を追加")
    print(f"https://www.youtube.com/playlist?list={pid}")


def crosslink_block(data: dict, me: str, playlist_id: str | None = None,
                    limit: int = 4) -> str:
    """自分以外の公開済みの回へのリンク。新しい順。

    再生リストを先頭に置く。**流入はほぼ関連動画で、検索は実測1再生だった**
    （2026-08-01〜14 の Analytics）。外から来た人をチャンネル内に留める導線が
    概要欄しかないので、1本ずつのリンクより連続再生に入れるリンクを上に出す。
    """
    rows = [(k, e) for k, e in data["videos"].items()
            if e.get("youtube_video_id") and e["youtube_video_id"] != me
            and e.get("privacy_status") == "public"]
    rows.sort(key=lambda kv: kv[0], reverse=True)
    lines = [CROSSLINK_HEAD]
    if playlist_id:
        lines += ["すべての回（再生リスト）",
                  f"https://www.youtube.com/playlist?list={playlist_id}", ""]
    for _k, e in rows[:limit]:
        lines += [e["title"], e["url"]]
    return "\n".join(lines)


def cmd_crosslink(service, data: dict, live: dict[str, dict] | None = None) -> None:
    """概要欄の末尾に他の回への導線を差し込む。

    **videos.update は part を丸ごと置き換える。** snippet を送るときは
    title も tags も categoryId も一緒に送らないと消える。現物を読んでから
    description だけ差し替える。
    """
    ids = [e["youtube_video_id"] for e in data["videos"].values()
           if e.get("youtube_video_id") and e.get("privacy_status") == "public"]
    live = live or fetch_videos(service, ids)
    pid = find_playlist(service, PLAYLIST_TITLE)

    for vid in ids:
        v = live.get(vid)
        if not v:
            continue
        sn = v["snippet"]
        body = sn["description"]
        head = body.split(CROSSLINK_HEAD)[0].rstrip()
        block = crosslink_block(data, vid, pid)
        new = f"{head}\n\n{block}\n"
        if new.strip() == body.strip():
            print(f"- {vid} は更新不要")
            continue
        if len(new) > 5000:
            print(f"! {vid} は概要欄が5000字を超えるので飛ばします")
            continue
        service.videos().update(part="snippet", body={
            "id": vid,
            "snippet": {
                "title": sn["title"],
                "description": new,
                "tags": sn.get("tags", []),
                "categoryId": sn["categoryId"],
                "defaultLanguage": sn.get("defaultLanguage", "ja"),
                "defaultAudioLanguage": sn.get("defaultAudioLanguage", "ja"),
            },
        }).execute()
        print(f"✓ {vid} の概要欄に導線を入れました")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--playlist", action="store_true")
    ap.add_argument("--crosslink", action="store_true")
    a = ap.parse_args()
    if not (a.status or a.playlist or a.crosslink):
        ap.error("--status / --playlist / --crosslink のどれかを指定してください")

    service = get_service()
    ch = service.channels().list(part="snippet", mine=True).execute()["items"][0]
    if ch["id"] != CHANNEL_ID:
        raise SystemExit(f"! チャンネルが違います: {ch['snippet']['title']}（{ch['id']}）")

    data = load_published()
    live = None
    if a.status:
        live = cmd_status(service, data)
    if a.playlist:
        cmd_playlist(service, data)
    if a.crosslink:
        cmd_crosslink(service, data, live)


if __name__ == "__main__":
    main()
