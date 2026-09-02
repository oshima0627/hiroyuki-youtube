#!/usr/bin/env python3
"""YouTube Analytics API v2 を叩いて、次に何を作るかの材料を出す。

  python scripts/analytics.py                 # 全部（既定）
  python scripts/analytics.py --days 30       # 期間を絞る
  python scripts/analytics.py --retention ID  # 1本の視聴維持率だけ見る

**取れないものがある。** インプレッション数とインプレッションのクリック率
（いわゆるサムネの CTR）は Analytics API に無い。Studio の画面にしか出ない。
「サムネが悪いのか」を API で判定することはできないので、ここでは代わりに
「配信された後どれだけ見られたか」（averageViewPercentage / audienceWatchRatio）
を見る。

クォータは Analytics API の枠で、Data API の 10,000 とは別勘定。
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from scripts.upload_youtube import CHANNEL_ID, get_credentials  # noqa: E402

CHANNEL_OPENED = "2026-08-13"       # ひろゆき解説ch の開設日


def rule(title: str) -> None:
    print("\n" + "=" * 78)
    print(f"### {title}")
    print("=" * 78)


def query(ana, **kw) -> dict | None:
    """1本のレポート。落ちたら理由をそのまま出して None を返す。

    メトリクスの組み合わせによっては 400 が返る。どれが通ってどれが通らないかは
    実際に叩くまで分からないので、1本落ちても後続を止めない。
    """
    from googleapiclient.errors import HttpError
    try:
        return ana.reports().query(**kw).execute()
    except HttpError as e:
        print(f"  ! 取得できず: {e}")
        return None


def table(res: dict | None, limit: int = 100, label: dict | None = None) -> None:
    """reports.query の生レスポンスをそのまま表にする。"""
    if not res:
        return
    heads = [h["name"] for h in res.get("columnHeaders", [])]
    rows = res.get("rows") or []
    if not rows:
        print("  （データ無し）")
        return
    print("  " + " | ".join(heads))
    print("  " + "-" * 74)
    for r in rows[:limit]:
        cells = []
        for h, v in zip(heads, r):
            if label and h == "video":
                v = f"{v}  {label.get(v, '?')}"
            cells.append(str(v))
        print("  " + " | ".join(cells))
    if len(rows) > limit:
        print(f"  ... 他 {len(rows) - limit} 行")


def video_titles(yt, ids: list[str]) -> dict[str, str]:
    """videoId → 「尺 タイトル」。Analytics API は ID しか返さないので引き当てる。"""
    out: dict[str, str] = {}
    for i in range(0, len(ids), 50):
        r = yt.videos().list(part="snippet,contentDetails",
                             id=",".join(ids[i:i + 50])).execute()
        for v in r.get("items", []):
            dur = v["contentDetails"]["duration"].replace("PT", "")
            out[v["id"]] = f"[{dur:>7}] {v['snippet']['title'][:40]}"
    return out


def retention(ana, vid: str, start: str, end: str, name: str = "") -> None:
    """視聴維持率。0.00〜1.00 の区間ごとに、何割の視聴者が残っているか。"""
    print(f"\n-- {vid}  {name}")
    res = query(ana, ids="channel==MINE", startDate=start, endDate=end,
                metrics="audienceWatchRatio,relativeRetentionPerformance",
                dimensions="elapsedVideoTimeRatio", filters=f"video=={vid}")
    if not res:
        res = query(ana, ids="channel==MINE", startDate=start, endDate=end,
                    metrics="audienceWatchRatio",
                    dimensions="elapsedVideoTimeRatio", filters=f"video=={vid}")
    if not res or not res.get("rows"):
        print("  （データ無し。視聴が少ないと維持率は返らない）")
        return
    rows = res["rows"]
    # 見やすさのため 5% 刻みに間引く（API は 1% 刻みで 101 行返す）
    for r in rows:
        ratio = r[0]
        if round(ratio * 100) % 5 and ratio not in (rows[0][0], rows[-1][0]):
            continue
        watch = r[1]
        bar = "#" * int(round(min(watch, 1.5) * 40))
        rel = f"  rel={r[2]:.2f}" if len(r) > 2 and r[2] is not None else ""
        print(f"  {ratio * 100:5.0f}%  {watch:5.2f} {bar}{rel}")


def main() -> None:
    from googleapiclient.discovery import build

    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=0,
                    help="直近N日。既定は開設日から今日まで")
    ap.add_argument("--retention", metavar="VIDEO_ID",
                    help="この動画の視聴維持率だけ出す")
    ap.add_argument("--top", type=int, default=6,
                    help="維持率を出す上位本数（既定6）")
    args = ap.parse_args()

    creds = get_credentials()
    yt = build("youtube", "v3", credentials=creds)
    ana = build("youtubeAnalytics", "v2", credentials=creds)

    end = dt.date.today().isoformat()
    start = ((dt.date.today() - dt.timedelta(days=args.days)).isoformat()
             if args.days else CHANNEL_OPENED)
    print(f"チャンネル {CHANNEL_ID}    期間 {start} 〜 {end}")

    if args.retention:
        titles = video_titles(yt, [args.retention])
        retention(ana, args.retention, start, end,
                  titles.get(args.retention, ""))
        return

    # ---- 1. 日別 ---------------------------------------------------------
    rule("日別（views / 視聴時間 / 平均視聴秒 / 登録増減）")
    table(query(ana, ids="channel==MINE", startDate=start, endDate=end,
                metrics=("views,estimatedMinutesWatched,averageViewDuration,"
                         "subscribersGained,subscribersLost"),
                dimensions="day", sort="day"))

    # ---- 2. 動画別 -------------------------------------------------------
    rule("動画別（views 降順）")
    res = query(ana, ids="channel==MINE", startDate=start, endDate=end,
                metrics=("views,estimatedMinutesWatched,averageViewDuration,"
                         "averageViewPercentage,subscribersGained,likes,"
                         "shares,comments"),
                dimensions="video", sort="-views", maxResults=50)
    ids = [r[0] for r in (res.get("rows") or [])] if res else []
    titles = video_titles(yt, ids) if ids else {}
    table(res, label=titles)

    # ---- 2b. 動画 × 日 ---------------------------------------------------
    # 1本が何日ぶん回り続けるかが分かる。初日で終わるなら毎日出す意味は
    # 「毎日1回抽選を引く」だけだが、数日伸び続けるなら在庫が効いてくる。
    rule("動画 × 日（views 上位8本の日次）")
    # dimensions="day,video" は「サポートされていないクエリ」で 400 が返る
    # （2026-09-02 に実測）。1本ずつ filters=video== で引くしかない。
    top = ids[:8]
    grid: dict[tuple[str, str], int] = {}
    days: set[str] = set()
    for v in top:
        r = query(ana, ids="channel==MINE", startDate=start, endDate=end,
                  metrics="views", dimensions="day", sort="day",
                  filters=f"video=={v}")
        for row in (r.get("rows") or []) if r else []:
            grid[(row[0], v)] = row[1]
            days.add(row[0])
    if grid:
        print("  " + " ".join(f"{v[-4:]:>6}" for v in top) + "   ← videoId 末尾4桁")
        for d in sorted(days):
            line = " ".join(f"{grid.get((d, v), 0):>6}" for v in top)
            print(f"  {line}   {d}")
        for v in top:
            print(f"  ...{v[-4:]} = {v}  {titles.get(v, '')}")

    # ---- 3. 流入元 -------------------------------------------------------
    rule("流入元（どこから見られているか）")
    table(query(ana, ids="channel==MINE", startDate=start, endDate=end,
                metrics="views,estimatedMinutesWatched,averageViewDuration",
                dimensions="insightTrafficSourceType", sort="-views"))

    rule("検索語（YT_SEARCH の内訳）")
    table(query(ana, ids="channel==MINE", startDate=start, endDate=end,
                metrics="views", dimensions="insightTrafficSourceDetail",
                filters="insightTrafficSourceType==YT_SEARCH",
                sort="-views", maxResults=25))

    rule("関連動画の出どころ（RELATED_VIDEO の内訳）")
    table(query(ana, ids="channel==MINE", startDate=start, endDate=end,
                metrics="views", dimensions="insightTrafficSourceDetail",
                filters="insightTrafficSourceType==RELATED_VIDEO",
                sort="-views", maxResults=25))

    # ---- 4. 視聴者 -------------------------------------------------------
    rule("視聴者の年齢・性別（視聴時間に占める割合 %）")
    table(query(ana, ids="channel==MINE", startDate=start, endDate=end,
                metrics="viewerPercentage", dimensions="ageGroup,gender",
                sort="-viewerPercentage"))

    rule("登録者/非登録者")
    table(query(ana, ids="channel==MINE", startDate=start, endDate=end,
                metrics="views,averageViewDuration,averageViewPercentage",
                dimensions="subscribedStatus"))

    rule("端末")
    table(query(ana, ids="channel==MINE", startDate=start, endDate=end,
                metrics="views,averageViewDuration",
                dimensions="deviceType", sort="-views"))

    rule("国")
    table(query(ana, ids="channel==MINE", startDate=start, endDate=end,
                metrics="views,averageViewDuration", dimensions="country",
                sort="-views", maxResults=10))

    # ---- 5. 視聴維持率 ---------------------------------------------------
    rule(f"視聴維持率（views 上位 {args.top} 本）")
    print("audienceWatchRatio: 1.00 = その地点を平均1回見た。冒頭の落ち方が勝負。")
    for vid in ids[:args.top]:
        retention(ana, vid, start, end, titles.get(vid, ""))

    print("\n※ インプレッション数とサムネのクリック率は API では取れない（Studio のみ）")


if __name__ == "__main__":
    main()
