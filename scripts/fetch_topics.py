#!/usr/bin/env python3
"""ガジェ通クリエイターデータベースから公式トピックスを取る。

  python scripts/fetch_topics.py            # 一覧を表示
  python scripts/fetch_topics.py --save     # work/<video_id>/topics.json に保存

<https://gcd.getnews.jp/portfolio/hiroyuki> は権利者（ガジェット通信）が
運営する切り抜き用の素材データベース。元動画の概要欄からリンクされている。

**ここのトピックスは YouTube の概要欄にも yt-dlp のチャプターにも無い。**
実測（2026-08-14）で、単独配信 3本は yt-dlp のチャプターが0件だったのに、
GCD には1本あたり100前後のトピックが時刻付きで整理されていた。

  IXiLxkgHUMM  yt-dlp chapters=0  →  GCD トピックス 109件

字幕のASRから質問境界を推定するより精度が高い。**取れるならこちらを使う。**
サーバー側でHTMLに埋まっているのでブラウザは要らない。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fetch_source import source_dir  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PORTFOLIO = "https://gcd.getnews.jp/portfolio/hiroyuki"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0 Safari/537.36")

# <a href="...watch?v=ID&amp;t=3s" ...> <span>0:03</span> <span>タイトル</span> </a>
# 最初に書いたとき &amp; のエスケープと末尾の s を見落として0件になった
TOPIC_RE = re.compile(
    r'href="https://www\.youtube\.com/watch\?v=([\w-]{11})&(?:amp;)?t=(\d+)s"'
    r'.*?<span[^>]*>\s*([\d:]+)\s*</span>\s*<span[^>]*>(.*?)</span>',
    re.S)
TAG_RE = re.compile(r"<[^>]+>")


def fetch_html(url: str = PORTFOLIO) -> str:
    req = urllib.request.Request(
        url, headers={"User-Agent": UA, "Accept-Language": "ja,en;q=0.9"})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8", "replace")


def parse_topics(html: str) -> dict[str, list[dict]]:
    """{video_id: [{"t": 秒, "title": "..."}, ...]} を返す。"""
    out: dict[str, list[dict]] = {}
    for vid, sec, _label, title in TOPIC_RE.findall(html):
        text = TAG_RE.sub("", title).strip()
        if not text:
            continue
        out.setdefault(vid, []).append({"t": int(sec), "title": text})
    for v in out.values():
        v.sort(key=lambda x: x["t"])
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--save", action="store_true",
                    help="work/<video_id>/topics.json に保存する")
    ap.add_argument("--show", help="この video_id のトピックを全部出す")
    a = ap.parse_args()

    topics = parse_topics(fetch_html())
    if not topics:
        raise SystemExit("! トピックを1件も取れませんでした。ページ構造が変わった可能性があります")

    if a.show:
        for t in topics.get(a.show, []):
            print(f"  {t['t'] // 3600}:{t['t'] % 3600 // 60:02d}:{t['t'] % 60:02d}  {t['title']}")
        return

    for vid, items in topics.items():
        mark = ""
        if a.save:
            d = source_dir(vid)
            d.mkdir(parents=True, exist_ok=True)
            (d / "topics.json").write_text(
                json.dumps(items, ensure_ascii=False, indent=1), encoding="utf-8")
            mark = " → 保存"
        print(f"{vid}  トピック{len(items):>4}件  {items[0]['title'][:34]}{mark}")

    print(f"\n{len(topics)}本ぶん。ページに出ている範囲だけなので、"
          f"古い回は GCD 側のページ送りが要る")


if __name__ == "__main__":
    main()
