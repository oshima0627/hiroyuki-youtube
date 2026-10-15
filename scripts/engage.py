#!/usr/bin/env python3
"""公開後のエンゲージメント運用。問いかけコメント・返信・Studio 手作業の記録。

  # 夕方: 公開済みの動画に、チャンネルとして問いかけコメントを1件投稿する
  python scripts/engage.py --post <videoId> [--text "..."] [--dry-run]

  # 返信: 未返信の視聴者コメントを JSON で出す（読み取り専用）
  python scripts/engage.py --list-unreplied [videoId ...] [--days 14] [--since-days 7]
  # 読んで返信文を決めたら1件ずつ投稿する（1〜2文）
  python scripts/engage.py --reply-to <commentId> --text "..." [--dry-run]

  # Studio 手作業（固定・終了画面・関連動画）の残りを見る / 済みにする
  python scripts/engage.py --todo
  python scripts/engage.py --done <videoId> pin|endscreen|related

  # 予約済み（未来公開）の動画の概要欄の先頭に問いかけ行を足す（それ以外は触らない）
  python scripts/engage.py --update-scheduled-descriptions [--dry-run]

記録は state/engagement.json。**同じ動画に2回投稿しない・同じコメントに2回返信しない**
のはここで担保する（API 側でも自分のコメントの有無を見る）。

## API でできないこと（Studio 手作業）

- コメントの固定（pin）。Data API に固定の操作が無い
- 終了画面（登録ボタン・関連動画2本）。長尺は最後の 20 秒を空けてある（outroimg）
- ショートの関連動画（長尺へのリンク）

## クォータ

commentThreads.insert / comments.insert は 50、list は 1、videos.update は 50。
1日（太平洋時間）あたり返信 REPLY_DAILY_LIMIT 件・投稿 POST_DAILY_LIMIT 件で止める。
返信 20 件で 1,000 ユニット。videos.insert（1,600）と同じ 10,000 の枠を食うので
アップロードより後（夕方）に回す。

## やらないこと

自分や別アカウントでのいいね・登録・自作自演コメント、報酬付きの依頼。
攻撃的・スパム・政治・個人情報を含むコメントには返信しない（flags が付いたものは拒否）。
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.engagement import (  # noqa: E402
    COMMENT_MAX, QUESTION_MAX, check_own_text, check_reply_text, comment_flags,
    comment_text, default_question, prepend_description, question_for,
    short_question)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "engagement.json"
PUBLISHED = ROOT / "state" / "published.json"
CHANNEL_ID = "UCqK3KYqEeeJiAWr4nSryJYQ"      # ひろゆき解説ch【切り抜き】

REPLY_DAILY_LIMIT = 20
POST_DAILY_LIMIT = 10
SHORT_MAX_SEC = 180
PT = ZoneInfo("America/Los_Angeles")         # クォータは太平洋時間の0時で戻る
TASKS = ("pin", "endscreen", "related")


# ---------------------------------------------------------------- 記録

def load_state(path: Path = STATE) -> dict:
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    data.setdefault("posted", {})
    data.setdefault("replied", {})
    data.setdefault("studio_todo", {})
    data.setdefault("description_updated", {})
    return data


def save_state(data: dict, path: Path = STATE) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n",
                    encoding="utf-8")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def quota_day(ts: str | datetime) -> str:
    dt = datetime.fromisoformat(ts.replace("Z", "+00:00")) if isinstance(ts, str) else ts
    return dt.astimezone(PT).strftime("%Y-%m-%d")


def count_today(entries: dict, now: datetime | None = None) -> int:
    today = quota_day(now or now_utc())
    return sum(1 for e in entries.values() if e.get("at") and quota_day(e["at"]) == today)


def studio_tasks(is_short: bool) -> dict:
    """API でできないので Studio で手作業にするもの。"""
    t = {"pin": False}
    if is_short:
        t["related"] = False          # ショートの関連動画（長尺へ）
    else:
        t["endscreen"] = False        # 最後の20秒に登録ボタン＋動画2本
    return t


# ---------------------------------------------------------------- 文言

def load_published() -> dict:
    return (json.loads(PUBLISHED.read_text(encoding="utf-8-sig"))
            if PUBLISHED.exists() else {"videos": {}})


def key_for(video_id: str, pub: dict) -> str | None:
    for k, e in pub.get("videos", {}).items():
        if e.get("youtube_video_id") == video_id:
            return k
    return None


def question_for_video(video_id: str, title: str, pub: dict | None = None) -> tuple[str | None, dict | None]:
    """(問いかけ文, レシピ) を返す。meta.json → レシピ → タイトルの順に見る。"""
    pub = pub if pub is not None else load_published()
    key = key_for(video_id, pub)
    recipe = None
    if key:
        for meta in (ROOT / "work" / key / "meta.json",
                     ROOT / "work" / "shorts" / key / "meta.json"):
            if meta.exists():
                m = json.loads(meta.read_text(encoding="utf-8"))
                if "engagement_question" in m:
                    rp = _recipe_path(key)
                    recipe = json.loads(rp.read_text(encoding="utf-8")) if rp else None
                    return m["engagement_question"], recipe
        rp = _recipe_path(key)
        if rp:
            recipe = json.loads(rp.read_text(encoding="utf-8"))
            if isinstance(recipe.get("clip"), dict):
                return short_question(recipe), recipe
            return question_for(recipe), recipe
    return default_question(title, key or video_id), None


def _recipe_path(key: str) -> Path | None:
    for p in (ROOT / "recipes" / f"{key}.json", ROOT / "recipes" / "shorts" / f"{key}.json"):
        if p.exists():
            return p
    return None


def parse_duration(iso: str) -> int:
    """PT8M22S → 502"""
    import re
    m = re.fullmatch(r"P(?:(\d+)D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    d, h, mi, s = (int(x or 0) for x in m.groups())
    return ((d * 24 + h) * 60 + mi) * 60 + s


# ---------------------------------------------------------------- API

def service():
    from scripts.upload_youtube import get_service
    return get_service()


def get_video(svc, video_id: str) -> dict | None:
    items = svc.videos().list(part="snippet,status,contentDetails",
                              id=video_id).execute().get("items", [])
    return items[0] if items else None


def own_threads(svc, video_id: str, pages: int = 1) -> list[dict]:
    """その動画に、このチャンネル自身が書いたトップレベルコメント。"""
    out, token = [], None
    for _ in range(pages):
        r = svc.commentThreads().list(part="snippet", videoId=video_id, order="time",
                                      maxResults=100, textFormat="plainText",
                                      pageToken=token).execute()
        for t in r.get("items", []):
            top = t["snippet"]["topLevelComment"]["snippet"]
            if top.get("authorChannelId", {}).get("value") == CHANNEL_ID:
                out.append(t)
        token = r.get("nextPageToken")
        if not token:
            break
    return out


def cmd_post(svc, video_id: str, text: str | None, dry: bool) -> int:
    state = load_state()
    if video_id in state["posted"]:
        e = state["posted"][video_id]
        print(f"- {video_id} には投稿済み（{e.get('at')} / {e.get('comment_id')}）。二重投稿しない")
        return 0
    if count_today(state["posted"]) >= POST_DAILY_LIMIT:
        print(f"✗ 今日（PT）の投稿上限 {POST_DAILY_LIMIT} 件に達している")
        return 1

    v = get_video(svc, video_id)
    if not v:
        print(f"✗ 動画が見つからない: {video_id}")
        return 1
    if v["snippet"]["channelId"] != CHANNEL_ID:
        print(f"✗ このチャンネルの動画ではない: {v['snippet']['channelId']}")
        return 1
    st = v["status"]
    if st.get("privacyStatus") != "public":
        print(f"✗ 公開済みではない（{st.get('privacyStatus')}"
              f"{' → ' + st['publishAt'] if st.get('publishAt') else ''}）。公開後に投稿する")
        return 1

    title = v["snippet"]["title"]
    q, recipe = question_for_video(video_id, title)
    body = (text or comment_text(recipe, q or default_question(title, video_id))).strip()
    errs = check_own_text(body, COMMENT_MAX, "問いかけコメント")
    if errs:
        print("✗ " + " / ".join(errs))
        return 1

    mine = own_threads(svc, video_id)
    is_short = parse_duration(v["contentDetails"]["duration"]) <= SHORT_MAX_SEC
    if mine:
        t = mine[0]
        print(f"- {video_id} には既にチャンネルのコメントがある（{t['id']}）。記録だけして投稿しない")
        if not dry:
            state["posted"][video_id] = {
                "comment_id": t["id"], "text": t["snippet"]["topLevelComment"]["snippet"]["textDisplay"],
                "at": t["snippet"]["topLevelComment"]["snippet"]["publishedAt"],
                "title": title, "found_existing": True}
            state["studio_todo"].setdefault(video_id, {"title": title, **studio_tasks(is_short)})
            save_state(state)
        return 0

    print(f"→ {video_id}「{title}」に投稿:\n{body}")
    if dry:
        print("[dry-run] 投稿しない")
        return 0
    r = svc.commentThreads().insert(part="snippet", body={"snippet": {
        "channelId": CHANNEL_ID, "videoId": video_id,
        "topLevelComment": {"snippet": {"textOriginal": body}}}}).execute()
    state["posted"][video_id] = {"comment_id": r["id"], "text": body,
                                 "at": now_utc().strftime("%Y-%m-%dT%H:%M:%SZ"),
                                 "title": title}
    state["studio_todo"][video_id] = {"title": title, **studio_tasks(is_short)}
    save_state(state)
    print(f"✓ 投稿 {r['id']}。固定は Studio で手作業（--todo）")
    return 0


def _replies(svc, thread: dict) -> list[dict]:
    got = (thread.get("replies") or {}).get("comments", [])
    if thread["snippet"].get("totalReplyCount", 0) > len(got):
        got = svc.comments().list(part="snippet", parentId=thread["id"], maxResults=100,
                                  textFormat="plainText").execute().get("items", [])
    return got


def unreplied_from_threads(threads: list[dict], replies_of, state: dict,
                           since: datetime, video_title: str = "") -> list[dict]:
    """スレッド一覧から、返信すべき候補を取り出す（API を呼ばない部分。テスト用に分けた）。

    - 視聴者のトップレベルコメントで、チャンネルの返信がまだ無いもの
    - チャンネル自身の問いかけコメントへの視聴者の返信で、未返信のもの
    自分のコメントと、state に返信済みとして載っているものは出さない。
    """
    out = []
    for t in threads:
        top = t["snippet"]["topLevelComment"]
        ts = top["snippet"]
        vid = t["snippet"].get("videoId") or ts.get("videoId")
        author = ts.get("authorChannelId", {}).get("value")
        reps = replies_of(t)
        mine = [r for r in reps if r["snippet"].get("authorChannelId", {}).get("value") == CHANNEL_ID]
        if author != CHANNEL_ID:
            if mine or top["id"] in state["replied"]:
                continue
            cands = [(top, "top", None)]
        else:
            cands = []
            for r in reps:
                rs = r["snippet"]
                if rs.get("authorChannelId", {}).get("value") == CHANNEL_ID:
                    continue
                if r["id"] in state["replied"]:
                    continue
                name = rs.get("authorDisplayName", "")
                answered = any(m["snippet"].get("publishedAt", "") > rs.get("publishedAt", "")
                               and name and name in m["snippet"].get("textOriginal",
                                                                     m["snippet"].get("textDisplay", ""))
                               for m in mine)
                if not answered:
                    cands.append((r, "reply_to_our_comment", ts.get("textOriginal") or ts.get("textDisplay")))
        for c, kind, context in cands:
            cs = c["snippet"]
            at = datetime.fromisoformat(cs["publishedAt"].replace("Z", "+00:00"))
            if at < since:
                continue
            text = cs.get("textOriginal") or cs.get("textDisplay", "")
            flags = comment_flags(text)
            out.append({
                "comment_id": c["id"], "thread_id": t["id"], "video_id": vid,
                "video_title": video_title, "kind": kind,
                "author": cs.get("authorDisplayName"), "text": text,
                "published_at": cs["publishedAt"], "like_count": cs.get("likeCount", 0),
                "flags": flags, "skip_suggested": bool(flags),
                **({"our_comment": context} if context else {}),
            })
    return out


def target_videos(pub: dict, days: int) -> list[tuple[str, str]]:
    since = now_utc() - timedelta(days=days)
    out = []
    for e in pub.get("videos", {}).values():
        vid = e.get("youtube_video_id")
        if not vid or e.get("privacy_status") != "public":
            continue
        at = e.get("publish_at") or e.get("published_at")
        if at and datetime.fromisoformat(at.replace("Z", "+00:00")) < since:
            continue
        out.append((vid, e.get("title", "")))
    return out


def cmd_list_unreplied(svc, ids: list[str], days: int, since_days: int, pages: int) -> int:
    from googleapiclient.errors import HttpError
    state = load_state()
    pub = load_published()
    titles = {e.get("youtube_video_id"): e.get("title", "") for e in pub.get("videos", {}).values()}
    videos = [(v, titles.get(v, "")) for v in ids] if ids else target_videos(pub, days)
    since = now_utc() - timedelta(days=since_days)
    items, errors = [], []
    for vid, title in videos:
        threads, token = [], None
        try:
            for _ in range(pages):
                r = svc.commentThreads().list(part="snippet,replies", videoId=vid, order="time",
                                              maxResults=100, textFormat="plainText",
                                              pageToken=token).execute()
                threads += r.get("items", [])
                token = r.get("nextPageToken")
                if not token:
                    break
        except HttpError as e:
            errors.append({"video_id": vid, "error": str(e)[:200]})
            continue
        items += unreplied_from_threads(threads, lambda t: _replies(svc, t), state, since, title)
    items.sort(key=lambda x: x["published_at"], reverse=True)
    print(json.dumps({
        "checked_videos": len(videos),
        "replies_today": count_today(state["replied"]),
        "reply_daily_limit": REPLY_DAILY_LIMIT,
        "remaining_today": max(0, REPLY_DAILY_LIMIT - count_today(state["replied"])),
        "unreplied": items,
        "errors": errors,
    }, ensure_ascii=False, indent=1))
    return 0


def cmd_reply_to(svc, comment_id: str, text: str, dry: bool, flags_ok: bool) -> int:
    state = load_state()
    if comment_id in state["replied"]:
        print(f"- {comment_id} には返信済み（{state['replied'][comment_id].get('at')}）。二重返信しない")
        return 0
    if count_today(state["replied"]) >= REPLY_DAILY_LIMIT:
        print(f"✗ 今日（PT）の返信上限 {REPLY_DAILY_LIMIT} 件に達している。続きは明日")
        return 1
    errs = check_reply_text(text)
    if errs:
        print("✗ " + " / ".join(errs))
        return 1

    items = svc.comments().list(part="snippet", id=comment_id,
                                textFormat="plainText").execute().get("items", [])
    if not items:
        print(f"✗ コメントが見つからない: {comment_id}")
        return 1
    c = items[0]["snippet"]
    if c.get("authorChannelId", {}).get("value") == CHANNEL_ID:
        print("✗ 自分のコメントには返信しない")
        return 1
    flags = comment_flags(c.get("textOriginal") or c.get("textDisplay", ""))
    if flags and not flags_ok:
        print(f"✗ 見送り対象の目安に当たった: {flags}。読んで誤検出なら --flags-ok")
        return 1
    parent = c.get("parentId") or comment_id
    th = svc.commentThreads().list(part="snippet", id=parent).execute().get("items", [])
    if not th or th[0]["snippet"].get("channelId", CHANNEL_ID) != CHANNEL_ID:
        print("✗ このチャンネルの動画のコメントではない")
        return 1
    video_id = th[0]["snippet"].get("videoId")
    body = text.strip()
    name = c.get("authorDisplayName", "")
    if c.get("parentId") and name.startswith("@") and not body.startswith(name):
        body = f"{name} {body}"          # 返信への返信は相手を明示する

    print(f"→ {video_id} の {comment_id}（{name}）へ返信:\n  {body}")
    if dry:
        print("[dry-run] 投稿しない")
        return 0
    r = svc.comments().insert(part="snippet", body={"snippet": {
        "parentId": parent, "textOriginal": body}}).execute()
    state["replied"][comment_id] = {"reply_id": r["id"], "video_id": video_id,
                                    "text": body, "at": now_utc().strftime("%Y-%m-%dT%H:%M:%SZ")}
    save_state(state)
    print(f"✓ 返信 {r['id']}（今日 {count_today(state['replied'])}/{REPLY_DAILY_LIMIT}）")
    return 0


def cmd_todo() -> int:
    state = load_state()
    left = {v: t for v, t in state["studio_todo"].items()
            if any(t.get(k) is False for k in TASKS)}
    if not left:
        print("Studio 手作業の残りは無い")
        return 0
    names = {"pin": "コメント固定", "endscreen": "終了画面（最後20秒・登録＋動画2本）",
             "related": "関連動画（長尺へ）"}
    for v, t in left.items():
        todo = [names[k] for k in TASKS if t.get(k) is False]
        print(f"{v}  {t.get('title', '')[:40]}\n  https://studio.youtube.com/video/{v}/edit"
              f"\n  残り: {' / '.join(todo)}")
    return 0


def cmd_done(video_id: str, task: str) -> int:
    state = load_state()
    t = state["studio_todo"].setdefault(video_id, {})
    t[task] = True
    save_state(state)
    print(f"✓ {video_id} の {task} を済みにした")
    return 0


def cmd_update_scheduled(svc, dry: bool) -> int:
    """予約済み（private かつ publishAt が未来）の動画だけ、概要欄の先頭に問いかけ行を足す。"""
    pub = load_published()
    state = load_state()
    ids = [e["youtube_video_id"] for e in pub["videos"].values() if e.get("youtube_video_id")]
    now = now_utc()
    changed = 0
    for i in range(0, len(ids), 50):
        r = svc.videos().list(part="snippet,status", id=",".join(ids[i:i + 50])).execute()
        for v in r.get("items", []):
            st, sn = v["status"], v["snippet"]
            pa = st.get("publishAt")
            if st.get("privacyStatus") != "private" or not pa:
                continue
            if datetime.fromisoformat(pa.replace("Z", "+00:00")) <= now:
                continue
            q, _ = question_for_video(v["id"], sn["title"], pub)
            if not q:
                continue
            errs = check_own_text(q, QUESTION_MAX, "問いかけ文")
            if errs:
                print(f"! {v['id']} スキップ: {' / '.join(errs)}")
                continue
            desc = sn.get("description", "")
            new = prepend_description(desc, q)
            if new == desc:
                print(f"- {v['id']} は既に問いかけ行あり")
                continue
            print(f"→ {v['id']}（{pa}）「{sn['title'][:30]}」先頭行: {new.split(chr(10), 1)[0]}")
            if dry:
                continue
            snippet = {k: sn[k] for k in ("title", "categoryId", "tags", "defaultLanguage",
                                          "defaultAudioLanguage") if k in sn}
            snippet["description"] = new[:5000]
            svc.videos().update(part="snippet", body={"id": v["id"], "snippet": snippet}).execute()
            state["description_updated"][v["id"]] = {"at": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
                                                     "line": new.split("\n", 1)[0]}
            changed += 1
    if not dry:
        save_state(state)
    print(f"✓ 更新 {changed} 件" + ("（dry-run）" if dry else ""))
    return 0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--post", metavar="VIDEO_ID")
    ap.add_argument("--list-unreplied", nargs="*", metavar="VIDEO_ID")
    ap.add_argument("--reply-to", metavar="COMMENT_ID")
    ap.add_argument("--text")
    ap.add_argument("--todo", action="store_true")
    ap.add_argument("--done", nargs=2, metavar=("VIDEO_ID", "TASK"))
    ap.add_argument("--update-scheduled-descriptions", action="store_true")
    ap.add_argument("--days", type=int, default=14, help="対象にする公開済み動画（直近N日）")
    ap.add_argument("--since-days", type=int, default=7, help="対象にするコメント（直近N日）")
    ap.add_argument("--pages", type=int, default=1, help="1動画あたり読むページ数（100件/ページ）")
    ap.add_argument("--flags-ok", action="store_true",
                    help="見送り目安の誤検出と読んで判断したときだけ付ける")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    if a.todo:
        sys.exit(cmd_todo())
    if a.done:
        if a.done[1] not in TASKS:
            sys.exit(f"TASK は {'/'.join(TASKS)}")
        sys.exit(cmd_done(*a.done))
    if a.reply_to and not a.text:
        sys.exit("--reply-to には --text が要る")
    if not (a.post or a.reply_to or a.list_unreplied is not None
            or a.update_scheduled_descriptions):
        ap.print_help()
        sys.exit(2)

    svc = service()
    if a.post:
        sys.exit(cmd_post(svc, a.post, a.text, a.dry_run))
    if a.list_unreplied is not None:
        sys.exit(cmd_list_unreplied(svc, a.list_unreplied, a.days, a.since_days, a.pages))
    if a.reply_to:
        sys.exit(cmd_reply_to(svc, a.reply_to, a.text, a.dry_run, a.flags_ok))
    if a.update_scheduled_descriptions:
        sys.exit(cmd_update_scheduled(svc, a.dry_run))


if __name__ == "__main__":
    main()
