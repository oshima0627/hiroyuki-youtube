#!/usr/bin/env python3
"""ひろゆき本人チャンネルの配信アーカイブを取得する。

  python scripts/fetch_source.py --latest 10 --list
  python scripts/fetch_source.py <URL> [<URL>...]
  python scripts/fetch_source.py --latest 5 --force

出力は work/<video_id>/ に source.mp4 / subs.json / meta.json。

tora-kirinuki からの移植。相違点は2つ。

1. **既定の一覧は /streams（ライブ配信アーカイブ）を見る。** 切り抜ける素材は
   ほぼ生配信のアーカイブにあり、/videos にはクラロワ実況やパリの風景など
   切り抜きに使えない古い動画が多い（2026-08-14 実測）。

2. **共演者のいる回を警告する。** 権利者が黙認しているのは西村博之氏の素材だけで、
   共演者の権利は対象外（ガジェット通信の受付メールに明記）。yt-dlp のメタから
   共同投稿を検出して警告を出す。検出できない共演もあるので最終判断は人。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.subtitles import parse_vtt  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"

CHANNEL_ID = "UC0yQ2h4gQXmVUFWZSqlMVOA"
OWN_NAME = "ひろゆき, hiroyuki"      # チャンネル名にカンマが入っている。共演判定で注意
STREAMS_URL = "https://www.youtube.com/@hirox246/streams"
VIDEOS_URL = "https://www.youtube.com/@hirox246/videos"

# 切り抜き禁止（ガジェット通信の受付メールで名指しでブロック指定）
BLOCKED = {"exnFXUMMLLI", "q0GyNI3X8cg"}

# lang=ja を付けないと、タイトル・チャプター名が自動翻訳で英語になる
JA = {"youtube": {"lang": ["ja"]}}


def source_dir(video_id: str) -> Path:
    return WORK / video_id


def pick_ja_vtt(info: dict) -> tuple[str | None, str | None, str | None]:
    """日本語字幕のVTT URLを返す。手動字幕を優先し、無ければ自動生成。"""
    for store, kind in ((info.get("subtitles") or {}, "manual"),
                        (info.get("automatic_captions") or {}, "auto")):
        for lang in ("ja", "ja-orig", "ja-JP"):
            for track in store.get(lang) or []:
                if track.get("ext") == "vtt":
                    return track["url"], kind, lang
    return None, None, None


# 共演の痕跡。**yt-dlp の uploader / channel では検出できない。**
# 実測（2026-08-14）で、共演回 naVkgtFmRvg も単独回 23vSB2fXjc8 も
# uploader は等しく "ひろゆき, hiroyuki" だった。共演者の名前が出るのは
# 概要欄とチャプターの中（「ゲスト紹介：実業家 桑田龍征」など）。
GUEST_MARKERS = ("ゲスト紹介", "ゲスト：", "ゲスト:", "出演：", "出演:", "共演")
TITLE_MARKERS = ("HIKAKIN", "ヒカキン", "コラボ", "対談", "VS", "参戦",
                 "ひろゆきと語る夜", "＆", "&")


def collab_warning(info: dict) -> str | None:
    """共演者がいそうなら警告文を返す。無ければ None。

    **完全ではない。最終判断は人がする。** 黙認されているのは西村博之氏の
    素材だけで、共演者の権利は対象外（ガジェット通信の受付メールに明記）。
    """
    desc = info.get("description") or ""
    for mark in GUEST_MARKERS:
        if mark in desc:
            line = next((l.strip() for l in desc.splitlines() if mark in l), mark)
            return f"概要欄にゲストの記載: {line[:50]}"

    chapters = " ".join((c.get("title") or "") for c in (info.get("chapters") or []))
    for mark in GUEST_MARKERS:
        if mark in chapters:
            return f"チャプターにゲストの記載: {mark}"

    title = info.get("title") or ""
    for name in TITLE_MARKERS:
        if name in title:
            return f"タイトルに共演を示す語: {name}"
    return None


def list_channel(limit: int, tab: str = "streams") -> list[dict]:
    from yt_dlp import YoutubeDL

    url = STREAMS_URL if tab == "streams" else VIDEOS_URL
    opts = {"quiet": True, "no_warnings": True, "skip_download": True,
            "extract_flat": "in_playlist", "playlistend": limit,
            "extractor_args": JA}
    with YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return [{"id": e.get("id"), "title": e.get("title") or "",
             "duration": e.get("duration"),
             "view_count": e.get("view_count"),
             "url": f"https://www.youtube.com/watch?v={e.get('id')}"}
            for e in (info.get("entries") or [])]


def fetch_one(url: str, force: bool = False, subs_only: bool = False) -> Path:
    from yt_dlp import YoutubeDL

    with YoutubeDL({"quiet": True, "no_warnings": True, "skip_download": True,
                    "extractor_args": JA}) as ydl:
        info = ydl.extract_info(url, download=False)
        vid = info["id"]

        if vid in BLOCKED:
            raise SystemExit(
                f"! {vid} は権利者がブロック指定した動画。切り抜き不可。")

        warn = collab_warning(info)
        if warn:
            print(f"! {vid}: 共演者がいる可能性（{warn}）")
            print("  黙認されているのは西村博之氏の素材だけです。使う前に確認してください。")

        out = source_dir(vid)
        if subs_only and (out / "subs.json").exists() and not force:
            print(f"- {vid} の字幕は取得済み（--force で再取得）")
            return out
        if not subs_only and (out / "source.mp4").exists() and not force:
            print(f"- {vid} は取得済み（--force で再取得）")
            return out
        out.mkdir(parents=True, exist_ok=True)

        sub_url, kind, lang = pick_ja_vtt(info)
        if not sub_url:
            raise SystemExit(
                f"! {vid}: 日本語字幕が無い。切り抜き地点を出せないので中断する")
        with ydl.urlopen(sub_url) as r:
            cues = parse_vtt(r.read().decode("utf-8", "replace"))

    (out / "subs.json").write_text(
        json.dumps([{"t": t, "line": l} for t, l in cues],
                   ensure_ascii=False, indent=1), encoding="utf-8")
    (out / "meta.json").write_text(json.dumps({
        "video_id": info["id"],
        "url": info.get("webpage_url"),
        "title": info.get("title"),
        "duration_sec": info.get("duration"),
        "upload_date": info.get("upload_date"),
        "view_count": info.get("view_count"),
        "chapters": info.get("chapters") or [],
        "subtitle_kind": kind,
        "subtitle_lang": lang,
        "collab_warning": warn,
        "fetched_at": datetime.now(timezone.utc).astimezone().isoformat(
            timespec="seconds"),
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    if subs_only:
        print(f"✓ {info['id']}  {info.get('title')}  字幕{len(cues)}行（本編は未取得）")
        return out

    with YoutubeDL({"quiet": True, "no_warnings": True, "extractor_args": JA,
                    "format": "bestvideo[height<=1080]+bestaudio/best",
                    "merge_output_format": "mp4",
                    "outtmpl": str(out / "source.%(ext)s")}) as ydl:
        ydl.download([url])

    print(f"✓ {info['id']}  {info.get('title')}  字幕{len(cues)}行")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("urls", nargs="*")
    ap.add_argument("--latest", type=int)
    ap.add_argument("--tab", choices=("streams", "videos"), default="streams",
                    help="既定は streams。切り抜ける素材はほぼ配信アーカイブにある")
    ap.add_argument("--list", action="store_true", help="取得せず一覧だけ表示")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--subs-only", action="store_true",
                    help="本編を落とさず字幕とメタだけ取る。候補の検討はこれで足りる")
    a = ap.parse_args()

    urls = list(a.urls)
    if a.latest:
        items = list_channel(a.latest, a.tab)
        if a.list:
            for it in items:
                mark = " [ブロック指定]" if it["id"] in BLOCKED else ""
                dur = it.get("duration") or 0
                views = it.get("view_count")
                vs = f"{views:,}回" if views else "-"
                print(f"{it['id']}  {dur // 3600}:{dur % 3600 // 60:02d}  "
                      f"{vs:>10}  {it['title'][:52]}{mark}")
            return
        urls += [it["url"] for it in items if it["id"] not in BLOCKED]
    if not urls:
        raise SystemExit("URL か --latest を指定してください")
    for u in urls:
        fetch_one(u, a.force, a.subs_only)


if __name__ == "__main__":
    main()
