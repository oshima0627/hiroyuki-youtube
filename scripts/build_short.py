#!/usr/bin/env python3
"""ショート（縦型）をビルドする。長尺と同じレシピから作る。

  python scripts/build_short.py recipes/<id>.json --dry-run
  python scripts/build_short.py recipes/<id>.json

出力は work/<id>-short/ に video.mp4 / description.txt / meta.json。

レシピの short ブロックを見る。

  "short": {
    "clip": 7,                      どのクリップを使うか（長尺の clips の添字）
    "start": 12.0, "end": 74.0,     そのクリップの中での秒。省略すると全体
    "hook": "その給料、転職先では出ません",
    "footer": "本編では仕事の相談9件に答えています"
  }

## tora-kirinuki の実測をそのまま持ち込む

  尺は60〜70秒。伸びている競合は22〜73秒で、103秒・132秒のものは0〜2再生だった
  hook は必須。縦型は冒頭2秒で離脱が決まる
  縦にトリミングして顔を大きくする。映像の占有率は伸びない原因ではなかったが、
  小さい顔で見せる理由も無い

## ひろゆき固有の事情

**画面下のスパチャのカードは切り落とす。** カードには質問文が載っているが、
縦型の小さい画面では読めないし、上下に文字を置く場所を取られる。
hook で何の話かを示すほうが速い。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image, ImageDraw  # noqa: E402

from scripts.build_episode import resolve_source  # noqa: E402
from scripts.draw import GOLD, INK, RED, WHITE, fit_font, pick_font, wrap  # noqa: E402
from scripts.recipe import CREDIT, validate_short  # noqa: E402
from scripts.thumbnail import head_box  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"

W, H, FPS = 1080, 1920, 30
VIDEO_H = 1080           # 中央に置く映像の高さ（正方形に切る）
VIDEO_Y = (H - VIDEO_H) // 2
PAD = 56


def _run(cmd: list[str]) -> None:
    subprocess.run(cmd, check=True, capture_output=True)


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def render_frame(hook: str, footer: str, cover: int = 0) -> Image.Image:
    """上にフック、下に補足を置いた透過PNG。映像の上下に重なる。

    `cover` は映像の下端をさらに何px黒帯で潰すか。スパチャのカードは尺の中で
    上端が動くので（実測で1本の窓の中を 650〜794px）、クロップの幾何だけでは
    毎フレーム外し切れない。**残った侵入ぶんをここで確実に潰す。**
    """
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    bottom = VIDEO_Y + VIDEO_H - cover

    d.rectangle([0, 0, W, VIDEO_Y], fill=(*INK, 255))
    d.rectangle([0, bottom, W, H], fill=(*INK, 255))
    d.rectangle([0, VIDEO_Y - 6, W, VIDEO_Y], fill=(*RED, 255))
    d.rectangle([0, bottom, W, bottom + 6], fill=(*RED, 255))

    f_label = pick_font(34)
    d.text((PAD, 44), "ひろゆき切り抜き＋解説", font=f_label, fill=(*RED, 255))

    # フックは冒頭2秒で読ませる。1行に収まらないなら折る
    # **フックは1行に収める。** 76pxのまま折ったら「ません」だけが2行目に
    # 残った（2026-08-14）。冒頭2秒で読ませる文字が割れては意味がない
    fh = fit_font(d, hook, W - PAD * 2, 76)
    lines = wrap(d, hook, fh, W - PAD * 2)[:2]
    y = VIDEO_Y - 40 - len(lines) * int(fh.size * 1.3)
    for ln in lines:
        d.text((PAD + 3, y + 3), ln, font=fh, fill=(0, 0, 0, 255))
        d.text((PAD, y), ln, font=fh, fill=(*WHITE, 255))
        y += int(fh.size * 1.3)

    if footer:
        ff = pick_font(44)
        fl = wrap(d, footer, ff, W - PAD * 2)[:2]
        y = bottom + 60
        for ln in fl:
            d.text((PAD, y), ln, font=ff, fill=(*GOLD, 255))
            y += 58

    fn = pick_font(28)
    d.text((PAD, H - 90), "公式チャンネルではありません", font=fn, fill=(150, 158, 168, 255))
    return img


# **1フレームで決めてはいけない。** 当初は開始3秒地点の1枚だけを測って
# クロップを固定していた。ひろゆきは前後にかなり動くので、測った瞬間は
# 顔が中央でも2秒後には枠から外れる。14本作って3本（08-20-am / 08-23-pm /
# 08-25-pm）で顔が左端で切れた（2026-08-19、コンタクトシートで確認）。
# 窓の全体を密に見て、頭部の外接矩形の**合併**を取る。
#
# **等間隔の数点では足りない。** 7点にしたらカードの写り込みが1本残った
# （08-22-pm）。この窓のカード上端を21点で測ると 650〜794px を行き来していて、
# 7点はいちばん高い 650 を踏み外していた。スパチャは短時間で差し替わるので、
# 跳ねを取りこぼすと必ずカードが入る。**1回の ffmpeg で SCAN_FPS 刻みに
# 全フレームを出して、全部見る。**
SCAN_FPS = 0.5                  # 2秒に1枚。38〜66秒の窓で19〜33枚
CARD_PAD = 8                    # カード上端からさらに空ける保険

# **縦は合併（最小・最大）で取ってはいけない。** 合併にしたら、頭がいちばん
# 下がったフレームの顎（y=671）とカードがいちばん高いフレームの上端（y=626）が
# 両立せず、14本中7本で口から下が切れた（2026-08-19、コンタクトシートで確認）。
# 一瞬の外れ値まで含めるとどちらも満たせないので、縦だけ分位点で妥協する。
# 横は合併のまま。**顔が左右にはみ出すほうが目立つ。**
P_TOP, P_CHIN, P_CARD = 0.20, 0.80, 0.20

# 分位点で外したぶんは黒帯で潰す。ただし潰しすぎると顔が隠れるので上限を置く
MAX_COVER = int(VIDEO_H * 0.14)


def _pct(values: list[int], q: float) -> int:
    v = sorted(values)
    return v[min(len(v) - 1, max(0, int(round(q * (len(v) - 1)))))]


def scan_head(src: Path, at: float, length: float,
              out: Path) -> tuple[int, int, tuple[int, int, int, int], int, int]:
    """窓全体を測り、(幅, 高さ, 頭部の合併矩形, カード上端) を返す。

    カードの上端はフレームごとに変わる（文面の長さで高さが変わる）ので、
    **一番高い位置**を採る。低いほうに合わせるとカードが写り込む。
    """
    scan = out / "_scan"
    if scan.exists():
        for old in scan.glob("*.png"):
            old.unlink()
    scan.mkdir(parents=True, exist_ok=True)
    _run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{at}", "-t", f"{length}",
          "-i", str(src), "-vf", f"fps={SCAN_FPS}", str(scan / "f%03d.png")])

    xs0, xs1, ys0, ys1, cards = [], [], [], [], []
    size = (0, 0)
    for png in sorted(scan.glob("*.png")):
        frame = Image.open(png).convert("RGB")
        size = frame.size
        hx0, hx1, hy0, hy1, card = head_box(frame)
        xs0.append(hx0), xs1.append(hx1), ys0.append(hy0), ys1.append(hy1)
        cards.append(card)
        png.unlink()
    scan.rmdir()
    if not xs0:
        raise SystemExit(f"! {src.name} からフレームを取れなかった")
    print(f"  走査 {len(cards)}枚 / カード上端 {min(cards)}〜{max(cards)}"
          f"（{int(P_CARD * 100)}%点 {_pct(cards, P_CARD)}）")
    return (size[0], size[1],
            (min(xs0), max(xs1), _pct(ys0, P_TOP), _pct(ys1, P_CHIN)),
            max(0, _pct(cards, P_CARD) - CARD_PAD), min(cards))


def resolve_recipe(recipe: dict) -> tuple[dict, dict, str, str | None, Path]:
    """(クリップ, short, 出力ID, 親の長尺ID, 出力先) を返す。

    形式が2つある。

    1. **単体**（`plan_shorts.py` の出力）。`clip` にクリップが直接入っていて、
       1ファイル＝1本。毎日出すぶんはこちら。
    2. **埋め込み**（従来）。長尺レシピの `short.clip` が `clips` の添字。
       1レシピ1本しか出せない。EP002 がこれで出ているので読めるまま残す。
    """
    short = recipe.get("short") or {}
    if isinstance(recipe.get("clip"), dict):
        rid = recipe["id"]
        return recipe["clip"], short, rid, recipe.get("parent"), WORK / "shorts" / rid
    idx = short.get("clip", 0)
    rid = f"{recipe['id']}-short"
    return recipe["clips"][idx], short, rid, recipe["id"], WORK / rid


def build(recipe_path: Path, dry_run: bool = False, pad: float = 2.0) -> Path:
    recipe = json.loads(recipe_path.read_text(encoding="utf-8"))
    clip, short, rid, parent, out = resolve_recipe(recipe)
    standalone_title = recipe["title"] if isinstance(recipe.get("clip"), dict) else ""

    length_all = clip["end"] - clip["start"]
    s = float(short.get("start", 0.0))
    e = float(short.get("end", length_all))
    # validate_short は絶対時刻を見るので、切り出し後の尺で渡す
    warnings = validate_short({"short": {"start": 0.0, "end": e - s,
                                         "hook": short.get("hook", "")}})
    for w in warnings:
        print(f"! {w}")

    resolved = resolve_source(clip, pad)
    if resolved is None:
        raise SystemExit(f"! {rid} の素材が無い。fetch_clips.py を先に")
    src, offset = resolved

    if dry_run:
        print(f"[dry-run] {rid}")
        print(f"  「{clip['title']}」の {s:.0f}〜{e:.0f}秒")
        print(f"  尺 {e - s:.0f}秒 / フック「{short.get('hook')}」")
        return out

    out.mkdir(parents=True, exist_ok=True)

    fw, fh_, (hx0, hx1, hy0, hy1), card, card_min = scan_head(
        src, offset + s, e - s, out)
    # 頭が収まる正方形を作る。
    # **幅も見る。** 高さだけを1.6倍していたころ、横を向いて頭が横長になった
    # フレームで正方形が頭より狭くなった。長い方の辺に合わせる
    side = int(max(hx1 - hx0, hy1 - hy0) * 1.15)
    # **顎の少し下に下端を置く。** カードの上端に下揃えしていたころ、顎と
    # カードの間が空いているフレームで正方形が上へ伸び、白い天井が
    # 200px 入った（2026-08-19）。カードは越えない
    bottom = min(card, hy1 + int(side * 0.10))
    # **下端が足りないときは正方形を縮める。** y0 を 0 で丸めていたら、
    # 正方形が下へはみ出してカードに食い込んだ（08-22-pm、2026-08-19）。
    # 位置を丸めるのではなく辺を詰めれば、カードを越えないことが構造で決まる
    side = min(side, bottom, fw, fh_)
    # カードがいちばん高く出るフレームでの侵入ぶんを、黒帯で潰す量に直す。
    # **潰す量が大きすぎるときは諦めてクロップを詰める。** 顔の半分を黒で
    # 隠すくらいなら、寄りが強くなるほうがまだ見られる
    over = max(0, bottom - card_min)
    cover = -(-over * VIDEO_H // side)
    if cover > MAX_COVER:
        bottom = card_min
        side = min(side, bottom, fw, fh_)
        cover = 0
    cx = (hx0 + hx1) // 2
    x0 = max(0, min(fw - side, cx - side // 2))
    y0 = max(0, bottom - side)
    cw = ch = side
    print(f"  頭部（合併） x{hx0}-{hx1} y{hy0}-{hy1} / 下端 {bottom}"
          f" / 切り出し {side}x{side} @ ({x0},{y0}) / 拡大 {VIDEO_H / side:.2f}倍"
          f" / 黒帯 {cover}px")

    png = out / "frame.png"
    render_frame(short.get("hook", ""), short.get("footer", ""), cover).save(png)

    video = out / "video.mp4"
    _run(["ffmpeg", "-y", "-loglevel", "error",
          "-ss", f"{offset + s}", "-i", str(src),
          "-i", str(png),
          "-t", f"{e - s}",
          "-filter_complex",
          f"[0:v]crop={cw}:{ch}:{x0}:{y0},scale={W}:{VIDEO_H},"
          f"pad={W}:{H}:0:{VIDEO_Y}:color=0x0E1116,fps={FPS}[v];"
          f"[v][1:v]overlay=0:0[o]",
          "-map", "[o]", "-map", "0:a",
          "-c:v", "libx264", "-preset", "medium", "-crf", "20",
          "-pix_fmt", "yuv420p",
          "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
          str(video)])

    actual = probe_duration(video)
    # plan_shorts.py は既に Shorts を付けて出す。順序を保ったまま重複だけ落とす
    tags = list(dict.fromkeys(list(recipe.get("tags") or []) + ["Shorts"]))
    desc = "\n".join([
        short.get("hook", ""), "",
        "▼この回をフルで見る",
        "（長尺のURLはアップロード時に差し込まれます）", "",
        f"【元動画】{clip.get('video_title', '')}",
        clip.get("video_url", ""), "",
        CREDIT, "",
        " ".join(f"#{t}" for t in tags),
    ]).strip() + "\n"
    (out / "description.txt").write_text(desc, encoding="utf-8")
    (out / "meta.json").write_text(json.dumps({
        "id": rid,
        # **parent を必ず残す。** 概要欄の「▼この回をフルで見る」に長尺のURLを
        # 差し込むのに要る。1つの長尺から複数本出すので、id のサフィックスから
        # 逆算する従来のやり方では親を特定できない
        "parent": parent,
        "publish_at": recipe.get("publish_at"),
        # 埋め込み形式の recipe["title"] は**長尺のタイトル**なので使わない
        "title": (short.get("title") or standalone_title
                  or short.get("hook", ""))[:100],
        "tags": tags,
        "category_id": recipe.get("category_id", "22"),
        "privacy_status": "private",
        "expected_channel_id": recipe["expected_channel_id"],
        "sources": [clip["video_id"]],
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    print(f"✓ {video}  {actual:.0f}秒  {W}x{H}")
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("recipe", type=Path)
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--pad", type=float, default=2.0)
    a = ap.parse_args()
    build(a.recipe, a.dry_run, a.pad)


if __name__ == "__main__":
    main()
