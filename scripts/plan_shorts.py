#!/usr/bin/env python3
"""長尺の在庫からショートを何本ぶんも組む。1日2本を7日ぶん、が既定。

  python scripts/plan_shorts.py --days 7 --from 2026-08-20
  python scripts/plan_shorts.py --days 7 --from 2026-08-20 --write

出力は recipes/shorts/<日付>-<am|pm>.json。1ファイル＝1本。

## 既存の長尺クリップを横断して選ぶ

`recipes/2026-*.json` の clips を全部ならべて、スコア順に取る。
**1本の長尺から複数本出してよい。** 各長尺から1本ずつだと7本で在庫が尽きて、
毎日出し続けられない（実測で候補は47本ある）。

同じ回ばかりが並ばないよう、親エピソードのラウンドロビンで並べ替える。

## フックは字幕から作らない。クリップの title を使う

**ここは実測で設計を変えた（2026-08-19）。** 当初は窓の中の「断言」文を
拾って言い切りに詰める設計にしていた。実素材で試したら成立しなかった。

`2026-08-19-shigoto2` のクリップ0（62秒）を文に割った実測:

    23字  受け止め方っていうのは結構違うよねっていうね。
    53字  PATMかこ診断済みのため人や責能に強い不安を感じるようになり…
    24字  もしさんが私の立場の振りモ前提で進度考えますか?
    12字  ト別の選択肢が上ました。
   154字  まず、あの、今ITで、あの、まず就職をするってなると最初から振リモート…

自動字幕は**単語が崩れる**（「フルリモート」→「振りモ」「振リモート」、
「他の選択肢が出ました」→「ト別の選択肢が上ました」）。そのうえ、
「断言」語彙に当たる文は 108字・154字で、フィラー（あの、えっと、まあ）
まみれの長文だった。**12文字のフックを機械で削り出せる材料ではない。**

崩れた字幕から作ったフックは、ひろゆき氏が言っていないことを画面に
大きく出すことになる。黙認で成り立っている以上、そこは踏めない。

代わりに **clips[].title を使う。** これは長尺を組んだときに人が書いた
1問1答の見出しで、47件すべて日本語として壊れていない（中央値17文字）。
新しく人手が要るわけではないので「全自動」は保てる。

## フックは実測して1行に収める

`draw.pick_font(76)` で幅968pxに入るのは**12文字まで**（2026-08-19 実測）。
47件の title のうち76pxで1行に入るのは8件しかない。

そこで **56pxまでの縮小を許して1行に収める**（47件中31件が該当）。
入らないものは**捨てる**。14本に対して候補は36本あるので、捨てて困らない。

**文字数で判定してはいけない。** 同じ12文字でも幅は違う。PIL で実際に
測る（既存の EP002 のフック「その給料、転職先では出ません」は14文字で
1064px あり、はみ出して勝手に縮小されていた）。
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.draw import pick_font  # noqa: E402
from scripts.signals import LEXICON  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"
RECIPES = ROOT / "recipes"
SHORTS = RECIPES / "shorts"
PUBLISHED = ROOT / "state" / "published.json"
USED = ROOT / "state" / "used_shorts.json"

CHANNEL_ID = "UCqK3KYqEeeJiAWr4nSryJYQ"

# ── 尺 ────────────────────────────────────────────────────────────
# tora-kirinuki の実測（2026-08-13）。伸びている競合は22〜73秒で、
# 103秒・132秒のものは0〜2再生だった。下限を22ではなく38に上げてあるのは、
# 質問の前提を落とすと回答だけが浮くため
MIN_SEC, MAX_SEC = 38.0, 70.0

# ── フックの見え方 ─────────────────────────────────────────────────
# build_short.render_frame と同じ値。ここを変えるなら向こうも変える
FRAME_W, PAD = 1080, 56
HOOK_MAX_W = FRAME_W - PAD * 2          # 968px
HOOK_START_PX = 76                       # 既定のフォントサイズ
HOOK_MIN_PX = 56                         # これ以上小さくしたら冒頭2秒で読めない

# **末尾を機械で削ってはいけない。** 一度「〜したい」を落とす処理を入れたら
# 「在宅テスターのバイトから抜け出したい」が「在宅テスターのバイトから抜け出」に
# なった（2026-08-19）。動詞の途中で切れた文字列を冒頭2秒に大きく出すことになる。
# 収まらないものは**削らずに捨てる**。14本に対して候補は36本あるので困らない。

# ── スコアの重み ───────────────────────────────────────────────────
# README の長尺側と揃える。音量はショートでは見ない（区間ファイルには
# 音声解析を掛けていないうえ、ひろゆきは怒鳴らないので効かない）
W_COMMENT, W_ASSERT, W_GROUND, W_HEDGE, W_QUESTION = 0.45, 0.40, 0.10, 0.05, -0.30

# 投稿枠。JST は UTC+9
SLOTS = {"am": 7, "pm": 18}


def _draw() -> ImageDraw.ImageDraw:
    return ImageDraw.Draw(Image.new("RGB", (8, 8)))


def hook_px(draw: ImageDraw.ImageDraw, text: str) -> int | None:
    """1行に収まる最大のフォントサイズ。HOOK_MIN_PX でも収まらなければ None。"""
    for size in range(HOOK_START_PX, HOOK_MIN_PX - 1, -2):
        box = draw.textbbox((0, 0), text, font=pick_font(size))
        # **draw.fit_font と同じ測り方をすること。** textlength は左右のベアリングを
        # 含まないので、こちらだけで測ると描画側が1〜2段小さいサイズを選ぶことがある
        if box[2] - box[0] <= HOOK_MAX_W:
            return size
    return None


def make_hook(draw: ImageDraw.ImageDraw, title: str) -> tuple[str, int] | None:
    """クリップの見出しをそのままフックにする。収まらなければ None（＝捨てる）。"""
    text = title.strip("、。 ")
    if len(text) < 6:
        return None
    size = hook_px(draw, text)
    return (text, size) if size else None


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def clip_file(video_id: str, start: float, end: float) -> Path:
    return WORK / "clips" / f"{video_id}_{int(start)}-{int(end)}.mp4"


def in_range(marks: list[dict], lo: float, hi: float) -> list[dict]:
    return [m for m in marks if lo <= float(m.get("seconds", -1)) <= hi]


def window_score(sig: dict, lo: float, hi: float) -> float:
    """窓のスコア。長さで割らずに sqrt で割る（README の実測に合わせる）。"""
    lex = in_range(sig.get("lexical") or [], lo, hi)
    kinds = {k: sum(1 for m in lex if m["kind"] == k) for k in LEXICON}
    comments = sum(int(m.get("count", 1))
                   for m in in_range(sig.get("comment_marks") or [], lo, hi))
    raw = (W_COMMENT * comments
           + W_ASSERT * kinds.get("断言", 0)
           + W_GROUND * kinds.get("根拠", 0)
           + W_HEDGE * kinds.get("留保", 0)
           + W_QUESTION * kinds.get("質問", 0))
    return raw / math.sqrt(max(1.0, hi - lo))


BLOCKING = ("政治", "個人", "センシティブ")     # 雑務は落とす理由にならない


def blocked(sig: dict, lo: float, hi: float) -> str | None:
    for m in in_range(sig.get("avoid") or [], lo, hi):
        if m["kind"] in BLOCKING:
            return f"{m['kind']}:{m['word']}"
    return None


def best_window(cues: list[dict], sig: dict, start: float,
                end: float) -> tuple[float, float, float] | None:
    """字幕行の境界にスナップした最良の窓 (絶対開始, 絶対終了, スコア)。

    **行の途中では切らない。** 縦型は冒頭2秒が勝負なので、言葉の途中から
    始まると何の話か分からないまま2秒が終わる。
    """
    ts = sorted({float(c["t"]) for c in cues if start <= float(c["t"]) <= end})
    if len(ts) < 2:
        return None
    ts.append(end)

    best = None
    for i, lo in enumerate(ts):
        for hi in ts[i + 1:]:
            span = hi - lo
            if span < MIN_SEC:
                continue
            if span > MAX_SEC:
                break
            if blocked(sig, lo, hi):
                continue
            sc = window_score(sig, lo, hi)
            if best is None or sc > best[2]:
                best = (lo, hi, sc)
    return best


def collect(pub: dict, used: list[dict],
            allow_unpublished: bool) -> tuple[list[dict], dict[str, int]]:
    draw = _draw()
    used_keys = {(u["video_id"], round(u["start"]), round(u["end"])) for u in used}
    out, skipped = [], {}

    def skip(reason: str) -> None:
        skipped[reason] = skipped.get(reason, 0) + 1

    for path in sorted(RECIPES.glob("2026-*.json")):
        recipe = load_json(path)
        rid = recipe.get("id")
        if not rid:
            skip("レシピに id が無い")
            continue
        if rid not in pub and not allow_unpublished:
            skip("親の長尺が未投稿")
            continue

        for index, clip in enumerate(recipe.get("clips") or []):
            src = clip_file(clip["video_id"], clip["start"], clip["end"])
            if not src.exists():
                skip("素材ファイルが無い")
                continue
            sig = load_json(WORK / clip["video_id"] / "signals.json", {})
            cues = load_json(WORK / clip["video_id"] / "subs.json", [])
            if not cues:
                skip("字幕が無い")
                continue

            hook = make_hook(draw, clip["title"])
            if hook is None:
                skip("フックが1行に収まらない")
                continue

            win = best_window(cues, sig, float(clip["start"]), float(clip["end"]))
            if win is None:
                skip(f"{MIN_SEC:.0f}〜{MAX_SEC:.0f}秒の窓が取れない")
                continue
            lo, hi, score = win
            if (clip["video_id"], round(lo), round(hi)) in used_keys:
                skip("使用済み")
                continue

            out.append({
                "parent": rid,
                "parent_title": recipe["title"],
                "clip_index": index,
                "clip": clip,
                "abs_start": lo,
                "abs_end": hi,
                "rel_start": lo - float(clip["start"]),
                "rel_end": hi - float(clip["start"]),
                "hook": hook[0],
                "hook_px": hook[1],
                "score": score,
                "tags": recipe.get("tags") or [],
                "category_id": recipe.get("category_id", "22"),
                "expected_channel_id": recipe.get("expected_channel_id", CHANNEL_ID),
            })
    return out, skipped


def interleave(cands: list[dict], count: int) -> list[dict]:
    """スコア順に取りつつ、同じ長尺が続かないよう親でラウンドロビンする。"""
    by_parent: dict[str, list[dict]] = {}
    for c in sorted(cands, key=lambda x: -x["score"]):
        by_parent.setdefault(c["parent"], []).append(c)
    # 良い候補を多く持つ親から回す
    order = sorted(by_parent, key=lambda p: -by_parent[p][0]["score"])

    out = []
    while len(out) < count and any(by_parent.values()):
        for p in order:
            if not by_parent[p]:
                continue
            out.append(by_parent[p].pop(0))
            if len(out) >= count:
                break
    return out


def slot_times(first: datetime, days: int,
               slots: list[str] | None = None) -> list[tuple[str, datetime]]:
    """(スロット名, UTCの公開時刻) を朝→夜の順で days 日ぶん。

    slots で使うスロットを絞れる。1日1本にするときは ["am"]。
    **在庫は有限なので、本数を増やすほど日数が短くなる。** 跳ねるまで
    続けられるかが効くので、1日2本で14日より1日1本で28日を選ぶ場面がある
    （2026-08-26 の兄弟チャンネル比較。docs/superpowers/specs 参照）。
    """
    names = slots or list(SLOTS)
    out = []
    for d in range(days):
        day = first + timedelta(days=d)
        for name in names:
            jst = day.replace(hour=SLOTS[name], minute=0, second=0, microsecond=0)
            out.append((f"{day:%Y-%m-%d}-{name}",
                        (jst - timedelta(hours=9)).replace(tzinfo=timezone.utc)))
    return out


def to_recipe(cand: dict, short_id: str, publish_at: datetime) -> dict:
    clip = cand["clip"]
    theme = re.sub(r"^【ひろゆき】", "", cand["parent_title"]).split("。")[0]
    return {
        "id": short_id,
        "parent": cand["parent"],
        "publish_at": publish_at.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "title": f"【ひろゆき】{cand['hook']}【切り抜き】"[:100],
        "tags": list(cand["tags"]) + ["Shorts"],
        "category_id": cand["category_id"],
        "privacy_status": "private",
        "expected_channel_id": cand["expected_channel_id"],
        "clip": clip,
        "short": {
            "start": round(cand["rel_start"], 2),
            "end": round(cand["rel_end"], 2),
            "hook": cand["hook"],
            "hook_px": cand["hook_px"],
            "footer": f"本編：{theme}",
        },
        "score": round(cand["score"], 4),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--slots", default=",".join(SLOTS),
                    help=f"使うスロット。既定 {','.join(SLOTS)}（1日{len(SLOTS)}本）。"
                         "1日1本にするなら am")
    ap.add_argument("--from", dest="first", help="最初の公開日（既定は明日）")
    ap.add_argument("--write", action="store_true", help="recipes/shorts に書き出す")
    ap.add_argument("--allow-unpublished", action="store_true",
                    help="親の長尺が未投稿でも候補に入れる（導線が張れないので既定は除外）")
    a = ap.parse_args()

    pub = (load_json(PUBLISHED, {"videos": {}}) or {}).get("videos", {})
    used = (load_json(USED, {"windows": []}) or {}).get("windows", [])

    cands, skipped = collect(pub, used, a.allow_unpublished)
    want = [x.strip() for x in a.slots.split(",") if x.strip()]
    bad = [x for x in want if x not in SLOTS]
    if bad or not want:
        sys.exit(f"--slots が不正: {a.slots!r}。使えるのは {','.join(SLOTS)}")
    slots = slot_times(
        datetime.strptime(a.first, "%Y-%m-%d") if a.first
        else datetime.now() + timedelta(days=1), a.days, want)

    print(f"候補 {len(cands)}本 / 必要 {len(slots)}本")
    for reason, n in sorted(skipped.items(), key=lambda x: -x[1]):
        print(f"  除外 {n:3}  {reason}")
    if len(cands) < len(slots):
        print(f"\n! 候補が {len(slots) - len(cands)}本 足りない。"
              "--days を減らすか、長尺を先に増やすこと")

    picked = interleave(cands, len(slots))
    print(f"\n{'公開(JST)':17} {'尺':>4} {'px':>3} {'score':>6}  {'親':22} フック")
    for cand, (sid, at) in zip(picked, slots):
        jst = at + timedelta(hours=9)
        sec = cand["rel_end"] - cand["rel_start"]
        print(f"{jst:%m/%d %H:%M}({sid[-2:]})  {sec:4.0f} {cand['hook_px']:3}"
              f" {cand['score']:6.2f}  {cand['parent']:22} {cand['hook']}")

    if not a.write:
        print("\n（--write で recipes/shorts に書き出す）")
        return

    SHORTS.mkdir(parents=True, exist_ok=True)
    for cand, (sid, at) in zip(picked, slots):
        out = SHORTS / f"{sid}.json"
        out.write_text(json.dumps(to_recipe(cand, sid, at),
                                  ensure_ascii=False, indent=1) + "\n",
                       encoding="utf-8")
    print(f"\n✓ {len(picked)}本を {SHORTS.relative_to(ROOT)} に書き出した")


if __name__ == "__main__":
    main()
