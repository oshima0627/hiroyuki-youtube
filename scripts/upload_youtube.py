#!/usr/bin/env python3
"""ビルドした切り抜きを YouTube に上げる。tora-kirinuki からの移植。

  python scripts/upload_youtube.py --auth-only          # 初回の認証だけ
  python scripts/upload_youtube.py work/<id>            # private で投稿
  python scripts/upload_youtube.py work/<id> --publish  # 内容確認後に公開へ
  python scripts/upload_youtube.py work/<id> --schedule "2026-08-15T03:00:00Z"

**Google Cloud プロジェクトは tora-kirinuki と分ける。**
YouTube Data API のクォータ 10,000ユニット/日は**プロジェクト単位**で、
`videos.insert` が 1,600 なので実質1日6本。プロジェクトを共有すると
3チャンネル合わせて6本になる。tora-kirinuki では実際に使い切っている
（2026-08-13、10本上げて 403 quotaExceeded。videos.list の1ユニットすら
通らなくなり、確認すらできなくなった。回復は太平洋時間の0時＝JST 16〜17時）。

同意画面では必ず「ひろゆき解説ch」を選ぶこと。**同じ Google アカウント
（orfevre6.27@gmail.com）には他に3チャンネルある**ので、アカウントを
選んだだけでは足りない。表示チャンネル名を必ず確認する。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
CLIENT_SECRET = ROOT / "client_secret.json"
TOKEN = ROOT / "token.json"
PUBLISHED = ROOT / "state" / "published.json"

CHANNEL_ID = "UCqK3KYqEeeJiAWr4nSryJYQ"      # ひろゆき解説ch【切り抜き】

# videos.insert → upload / channels.list → readonly（取り違え検出に必須）
# videos.update → force-ssl（公開設定の変更に狭いスコープが無い）
# reports.query → yt-analytics.readonly（実数の確認）
SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/youtube.force-ssl",
    "https://www.googleapis.com/auth/yt-analytics.readonly",
]


def die(msg: str) -> None:
    print(f"✗ {msg}", file=sys.stderr)
    sys.exit(1)


def get_service():
    try:
        from google.auth.transport.requests import Request
        from google.oauth2.credentials import Credentials
        from google_auth_oauthlib.flow import InstalledAppFlow
        from googleapiclient.discovery import build
    except ImportError:
        die("依存が足りません。"
            "`pip install google-api-python-client google-auth-oauthlib`")

    creds = None
    if TOKEN.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN), SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    if not creds or not creds.valid:
        if not CLIENT_SECRET.exists():
            die(f"{CLIENT_SECRET.name} がありません。\n"
                "  Google Cloud で**このチャンネル専用の**プロジェクトを作り、\n"
                "  YouTube Data API v3 を有効化し、\n"
                "  OAuth クライアント（デスクトップアプリ）を作成して配置してください。\n"
                "  tora-kirinuki のものを流用するとクォータを食い合います。")
        # 初回のみブラウザが開く。以降は token.json の refresh_token で無人化される
        creds = InstalledAppFlow.from_client_secrets_file(
            str(CLIENT_SECRET), SCOPES).run_local_server(port=0)
        TOKEN.write_text(creds.to_json(), encoding="utf-8")
        print(f"✓ 認証情報を保存しました: {TOKEN.name}（コミットしないこと）")

    return build("youtube", "v3", credentials=creds)


def current_channel(service) -> dict | None:
    from googleapiclient.errors import HttpError
    try:
        items = service.channels().list(
            part="snippet", mine=True).execute().get("items", [])
    except HttpError as e:
        print(f"! チャンネルを確認できませんでした: {e}")
        return None
    return {"id": items[0]["id"], "title": items[0]["snippet"]["title"]} if items else None


def assert_expected_channel(service, meta: dict) -> dict | None:
    """expected_channel_id と一致しない限りアップロードしない。

    ブランドアカウントを持つと同意画面はアカウントを選ぶだけで、API は
    既定チャンネルに上げる。tora-kirinuki では実際に意図しないチャンネルへ
    入った。上げてから消すより、上げる前に止めるほうが安い。
    """
    ch = current_channel(service)
    expected = meta.get("expected_channel_id") or CHANNEL_ID
    if ch is None or ch["id"] != expected:
        got = f"{ch['title']}（{ch['id']}）" if ch else "取得できず"
        die("アップロード先のチャンネルが指定と一致しません。\n"
            f"  期待: {expected}\n"
            f"  実際: {got}\n"
            f"  {TOKEN.name} を削除し、同意画面で「ひろゆき解説ch」を選び直してください。")
    return ch


# **電話番号が未確認のチャンネルは15分を超える動画を上げられない。**
# API 呼び出しは成功するが、処理が中止される（2026-08-14 に16分36秒で発生）。
# Studio には「処理を中止しました／動画が長すぎます」と残って削除ボタンが出る。
# 一方 videos.list には出てこなくなるので、API だけ見ていると消えたように見える。
# https://support.google.com/youtube/answer/171664
UNVERIFIED_MAX_SEC = 15 * 60


def probe_seconds(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def upload(service, workdir: Path, meta: dict, description: str, privacy: str,
           allow_long: bool = False) -> str:
    from googleapiclient.http import MediaFileUpload

    video = workdir / "video.mp4"
    if not video.exists():
        die(f"{video} がありません。先に build_episode.py を実行してください")

    sec = probe_seconds(video)
    if sec > UNVERIFIED_MAX_SEC and not allow_long:
        die(f"尺が {int(sec) // 60}:{int(sec) % 60:02d} で15分を超えています。\n"
            "  電話番号が未確認のチャンネルは15分超の動画を上げられません。\n"
            "  上げても処理の途中で削除されます（実際に消えました）。\n"
            "  15分未満に詰めるか、https://www.youtube.com/verify で確認を済ませてから\n"
            "  --allow-long を付けて再実行してください。")

    # 言語は必ず明示する。省略すると YouTube が推測し、日本語の動画が
    # en と判定されることがある（tora-kirinuki の元になった BGM チャンネルで
    # 9本中8本が en 判定になった）
    body = {
        "snippet": {
            "title": meta["title"][:100],
            "description": description[:5000],
            "tags": meta.get("tags", []),
            "categoryId": meta.get("category_id", "22"),
            "defaultLanguage": "ja",
            "defaultAudioLanguage": "ja",
        },
        "status": {"privacyStatus": privacy, "selfDeclaredMadeForKids": False},
    }

    media = MediaFileUpload(str(video), chunksize=8 * 1024 * 1024,
                            resumable=True, mimetype="video/mp4")
    request = service.videos().insert(part="snippet,status", body=body,
                                      media_body=media)
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"  アップロード {int(status.progress() * 100)}%")
    return response["id"]


def set_thumbnail(service, video_id: str, workdir: Path) -> bool:
    """サムネイルを設定する。失敗しても動画は既に上がっているので止めない。"""
    from googleapiclient.errors import HttpError
    from googleapiclient.http import MediaFileUpload

    thumb = workdir / "thumb.png"
    if not thumb.exists():
        print("! thumb.png が無いのでサムネイル設定をスキップします")
        return False
    try:
        service.thumbnails().set(
            videoId=video_id, media_body=MediaFileUpload(str(thumb))).execute()
        return True
    except HttpError as e:
        print(f"! サムネイル設定に失敗しました: {e}")
        if getattr(e, "status_code", None) == 429 or "429" in str(e):
            # 短時間に何度も差し替えると弾かれる。クォータ超過ではないので待てば通る
            print("  差し替えの回数制限です。時間を置いて再実行してください")
        else:
            print("  チャンネルの電話番号確認が済んでいるか確認してください")
        return False


def set_privacy(service, video_id: str, privacy: str,
                publish_at: str | None = None) -> None:
    """公開設定を変更する。

    videos.update は部分更新ではなく part を丸ごと置き換える。status だけを渡すと
    selfDeclaredMadeForKids などが既定値に戻る恐れがあるため、現在の status を
    読んでから必要な項目だけ差し替えて送る。

    publish_at を渡すと privacyStatus は private のまま publishAt を仕込む。
    public と同時に送ると無視されて即時公開になる。
    """
    items = service.videos().list(part="status", id=video_id).execute().get("items", [])
    if not items:
        die(f"動画が見つかりません: {video_id}")
    cur = items[0]["status"]
    writable = ("license", "embeddable", "publicStatsViewable",
                "selfDeclaredMadeForKids")
    status = {k: cur[k] for k in writable if k in cur}
    if publish_at:
        status["privacyStatus"] = "private"
        status["publishAt"] = publish_at
    else:
        status["privacyStatus"] = privacy
    service.videos().update(part="status",
                            body={"id": video_id, "status": status}).execute()


def record(meta: dict, video_id: str, privacy: str, thumb_ok: bool,
           ch: dict | None) -> None:
    PUBLISHED.parent.mkdir(parents=True, exist_ok=True)
    data = (json.loads(PUBLISHED.read_text(encoding="utf-8-sig"))
            if PUBLISHED.exists() else {"videos": {}})
    data["videos"][meta["id"]] = {
        "youtube_video_id": video_id,
        "url": f"https://www.youtube.com/watch?v={video_id}",
        "title": meta["title"],
        "privacy_status": privacy,
        # どのチャンネルに上がったかを必ず残す。追跡できないと取り違えに気づけない
        "channel_id": (ch or {}).get("id"),
        "channel_title": (ch or {}).get("title"),
        "thumbnail_set": thumb_ok,
        "sources": meta.get("sources") or [],
    }
    PUBLISHED.write_text(
        json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("workdir", nargs="?", type=Path)
    ap.add_argument("--auth-only", action="store_true",
                    help="認証だけ行い、紐づくチャンネルを表示する")
    ap.add_argument("--publish", action="store_true", help="public にする")
    ap.add_argument("--schedule", help="予約公開の時刻（例 2026-08-15T03:00:00Z）")
    ap.add_argument("--allow-long", action="store_true",
                    help="15分超を許可する。電話番号の確認が済んでいる場合のみ")
    a = ap.parse_args()

    service = get_service()

    if a.auth_only:
        ch = current_channel(service)
        if not ch:
            die("チャンネルを取得できませんでした")
        mark = "✓ 一致" if ch["id"] == CHANNEL_ID else "✗ 想定と違う"
        print(f"{mark}  {ch['title']}（{ch['id']}）")
        if ch["id"] != CHANNEL_ID:
            print(f"  期待: {CHANNEL_ID}（ひろゆき解説ch）")
            print(f"  {TOKEN.name} を消して、同意画面で選び直してください")
        return

    if not a.workdir:
        die("workdir を指定してください（例: work/2026-08-14-shigoto）")

    meta = json.loads((a.workdir / "meta.json").read_text(encoding="utf-8"))
    description = (a.workdir / "description.txt").read_text(encoding="utf-8")

    ch = assert_expected_channel(service, meta)
    privacy = "public" if a.publish else meta.get("privacy_status", "private")
    if a.schedule:
        privacy = "private"

    print(f"→ {ch['title']} に {privacy} で投稿します")
    video_id = upload(service, a.workdir, meta, description, privacy,
                      a.allow_long)
    print(f"✓ https://www.youtube.com/watch?v={video_id}")

    thumb_ok = set_thumbnail(service, video_id, a.workdir)
    if a.schedule:
        set_privacy(service, video_id, privacy, a.schedule)
        print(f"✓ {a.schedule} に予約しました")
    record(meta, video_id, privacy, thumb_ok, ch)


if __name__ == "__main__":
    main()
