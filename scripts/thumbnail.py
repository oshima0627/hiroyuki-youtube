#!/usr/bin/env python3
"""サムネイルを作る。

  python scripts/thumbnail.py recipes/<id>.json
  python scripts/thumbnail.py recipes/<id>.json --at 420 --preview

レシピの thumb ブロックを見る。

  "thumb": {
    "at": 420,              本編の何秒地点のフレームを使うか（連結後の時刻）
    "main": ["その悩み、答えは", "全部同じでした"],
    "sub": "仕事とキャリアの相談10件",
    "crop": [0.30, 0.18, 0.42]      左端・上端・**高さ**（0〜1の割合）
  }

## 本人の顔は使ってよい

一度「本人の肖像を図案に使わない」と書いたが、**過剰な自己規制だった**。
権利者が禁じているのは「公式」「公認」の表記と、名誉・信用を害する編集で、
配信映像そのものは黙認の対象。競合4社もすべて本人の顔をサムネにしている。

## 断定的な一言を「」で囲まない

「本人が直接言及していない具体的なニュースについて、あたかも意見を述べて
いるかのようにミスリードする表現」を権利者が禁じている。鉤括弧で囲むと
発言の引用に見えるので、編集側の言葉は囲まずに書く。
ASR字幕から取った文言も同じ理由で引用として出さない（数値と固有名詞が崩れる）。
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from PIL import Image, ImageDraw, ImageFilter  # noqa: E402

from scripts.draw import GOLD, INK, MUTED, RED, WHITE, pick_font  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / "work"

W, H = 1280, 720
PHOTO_W = 560            # 右側に置く写真の幅
PAD = 56


def grab_frame(video: Path, at: float, out: Path) -> Path:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", str(at),
                    "-i", str(video), "-frames:v", "1", str(out)], check=True)
    return out


def warn_if_card(photo: Image.Image) -> bool:
    """写真の下にスパチャのカードが写り込んでいないか見る。

    クロップを上下に動かすたびに何度も混入させたので、目視だけに頼らない。
    カードは彩度の高い一色（橙・桃・青など）の帯なので、下端の行の彩度が
    高ければ疑う。部屋の背景は白い窓と壁で彩度が低い。
    """
    band = photo.crop((0, int(photo.height * 0.82), photo.width, photo.height))
    sat = band.convert("HSV").split()[1]
    mean = sum(sat.getdata()) / (band.width * band.height)
    if mean > 60:
        print(f"! 写真の下端の彩度が高い（{mean:.0f}）。"
              "スパチャのカードが写り込んでいないか確認してください")
        return True
    return False


def card_top(src: Image.Image) -> int:
    """スパチャのカードの上端。無ければフレーム下端を返す。

    カードは彩度の高い一色の帯なので、上から見て彩度が跳ねる行を探す。
    実測でこのフレームは y=648（高さの0.600）だった（2026-08-14）。
    """
    sat = src.convert("HSV").split()[1]
    w, h = src.size
    base = sum(sat.crop((0, 0, w, 200)).getdata()) / (w * 200)
    for y in range(int(h * 0.35), h, 8):
        band = sat.crop((0, y, w, min(h, y + 8)))
        if sum(band.getdata()) / (w * 8) > base + 35:
            return y
    return h


def head_box(src: Image.Image) -> tuple[int, int, int, int, int]:
    """頭部の外接矩形 (x0, x1, y0, y1) とカードの上端を返す。

    手で係数を動かして何度も外した（カードが入る／頭が切れる／顎が切れる）ので、
    フレームから測って決める。髪と顔は白い窓・壁より暗いので、暗部の
    外接矩形を頭部とみなす。左のランプを拾わないよう範囲を絞る。

    **縦型でも横型でもここを共通で使う。** 別々に計算していたとき、
    ショート側で中心の求め方を間違えて顎が切れた（2026-08-14）。
    """
    w, h = src.size
    limit = card_top(src)
    px = src.load()
    xs, ys = [], []
    for y in range(int(h * 0.18), limit, 3):
        for x in range(int(w * 0.38), int(w * 0.80), 3):
            r, g, b = px[x, y]
            if r + g + b < 300:
                xs.append(x)
                ys.append(y)
    if not xs:
        return (int(w * 0.40), int(w * 0.60), int(h * 0.30), int(h * 0.60), limit)
    return (min(xs), max(xs), min(ys), max(ys), limit)


def face_score(src: Image.Image) -> float:
    """このフレームで顔がどれだけこちらを向いているか。0〜1。

    **頭部検出だけでは向きが分からない。** 暗い画素の外接矩形は髪を拾うので、
    後頭部でも同じように当たる。実際に後頭部のサムネイルができた（2026-08-14）。

    顔が正面を向いていれば、頭部の下半分に肌色が多く出る。
    後ろを向いていればそこも髪になる。肌色の比率で見分ける。
    """
    x0, x1, y0, y1, _ = head_box(src)
    if x1 - x0 < 40 or y1 - y0 < 40:
        return 0.0
    box = src.crop((x0, (y0 + y1) // 2, x1, y1))     # 頭部の下半分
    px = box.load()
    skin = total = 0
    for y in range(0, box.height, 3):
        for x in range(0, box.width, 3):
            r, g, b = px[x, y]
            total += 1
            if r > 95 and g > 40 and b > 20 and r > g > b and r - g > 15:
                skin += 1
    return skin / total if total else 0.0


def pick_frame(video: Path, out_dir: Path, count: int = 9) -> tuple[Path, float, float]:
    """顔がこちらを向いているフレームを選ぶ。(画像, 秒, スコア) を返す。

    候補が9点だと尺13分に対して約80秒おきにしか見ておらず、たまたま全部が
    伏し目のフレームに当たることがある。実際に 8/14・8/15・8/16 の3本が
    下を向いた絵になった（2026-08-25 に確認）。本数が少ないうちは candidates を
    増やして選び直すほうが安い。
    """
    dur = float(subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(video)],
        capture_output=True, text=True, check=True).stdout)
    best: tuple[Path, float, float] | None = None
    for i in range(count):
        at = dur * (i + 1) / (count + 1)
        p = out_dir / f"_cand{i:02d}.png"
        grab_frame(video, at, p)
        s = face_score(Image.open(p).convert("RGB"))
        if best is None or s > best[2]:
            best = (p, at, s)
    return best                                       # type: ignore[return-value]


def auto_crop(src: Image.Image, margin: float = 0.12) -> tuple[float, float, float]:
    """サムネイル用（PHOTO_W:H の比）のクロップを割合で返す。"""
    w, h = src.size
    x0, x1, y0, y1, limit = head_box(src)
    top = max(0, int(y0 - (y1 - y0) * margin))
    bot = min(limit, int(y1 + (y1 - y0) * margin))
    ch = bot - top
    cw = int(ch * PHOTO_W / H)
    left = max(0, min(w - cw, (x0 + x1) // 2 - cw // 2))
    return (left / w, top / h, ch / h)


def compose(frame: Path, main: list[str], sub: str,
            crop: tuple[float, float, float]) -> Image.Image:
    img = Image.new("RGB", (W, H), INK)
    d = ImageDraw.Draw(img)

    # --- 右側の写真 -------------------------------------------------
    src = Image.open(frame).convert("RGB")
    sw, sh = src.size
    # **高さを基準に切る。** 幅基準にしていたら高さが溢れ、画面下の
    # スパチャカードまで写真に入った（2026-08-14）。避けたいものは下にある
    x0 = int(sw * crop[0])
    y0 = int(sh * crop[1])
    ch = int(sh * crop[2])
    cw = int(ch * PHOTO_W / H)
    box = (x0, y0, min(sw, x0 + cw), min(sh, y0 + ch))
    photo = src.crop(box).resize((PHOTO_W, H), Image.LANCZOS)
    # 顔はフレームの一部しか占めないので2倍前後に拡大することになる。
    # 甘くなるぶんを軽く戻す（かけすぎると輪郭が硬くなる）
    photo = photo.filter(ImageFilter.UnsharpMask(radius=2, percent=110, threshold=3))
    warn_if_card(photo)
    img.paste(photo, (W - PHOTO_W, 0))

    # 写真の左端をぼかして地色に馴染ませる。境界が直線だと切り貼りに見える
    edge = img.crop((W - PHOTO_W - 40, 0, W - PHOTO_W + 40, H))
    img.paste(edge.filter(ImageFilter.GaussianBlur(18)), (W - PHOTO_W - 40, 0))

    # --- 左側の文字 -------------------------------------------------
    d.rectangle([0, 0, 10, H], fill=RED)

    f_label = pick_font(30)
    d.text((PAD, 54), "ひろゆき切り抜き＋解説", font=f_label, fill=RED)

    # 主文は幅に収まる最大サイズで揃える。行ごとにサイズが違うと素人臭くなる
    avail = W - PHOTO_W - PAD - 40
    size = 92
    while size > 40:
        f = pick_font(size)
        if all(d.textbbox((0, 0), ln, font=f)[2] <= avail for ln in main):
            break
        size -= 4
    lh = int(size * 1.26)
    y = (H - len(main) * lh) // 2 - 10
    for ln in main:
        d.text((PAD + 4, y + 4), ln, font=f, fill=(0, 0, 0))   # 影で背景から分離
        d.text((PAD, y), ln, font=f, fill=WHITE)
        y += lh

    f_sub = pick_font(38)
    d.text((PAD, y + 18), sub, font=f_sub, fill=GOLD)

    f_note = pick_font(24)
    d.text((PAD, H - 56), "公式チャンネルではありません",
           font=f_note, fill=MUTED)
    return img


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("recipe", type=Path)
    ap.add_argument("--at", type=float, help="レシピの thumb.at を上書きする")
    ap.add_argument("--auto-crop", action="store_true",
                    help="頭部を測ってクロップを決める（手で係数を触らない）")
    ap.add_argument("--candidates", type=int, default=9,
                    help="顔を探すときに見るフレーム数（既定 9）")
    ap.add_argument("--ignore-at", action="store_true",
                    help="レシピの thumb.at を無視してフレームを探し直す")
    a = ap.parse_args()

    recipe = json.loads(a.recipe.read_text(encoding="utf-8"))
    thumb = recipe.get("thumb") or {}
    out_dir = WORK / recipe["id"]
    video = out_dir / "video.mp4"
    if not video.exists():
        raise SystemExit(f"! {video} が無い。先に build_episode.py を実行してください")

    if not a.ignore_at and (a.at is not None or thumb.get("at") is not None):
        at = float(a.at if a.at is not None else thumb["at"])
        frame = grab_frame(video, at, out_dir / "_thumbframe.png")
        print(f"  指定の {at:.0f}秒 を使用（顔スコア "
              f"{face_score(Image.open(frame).convert('RGB')):.3f}）")
    else:
        # **顔がこちらを向いているフレームを選ぶ。** 適当な秒を指定すると
        # 後頭部のサムネイルになる（2026-08-14 に実際になった）
        frame, at, sc = pick_frame(video, out_dir, a.candidates)
        print(f"  {at:.0f}秒 を選択（顔スコア {sc:.3f}／候補 {a.candidates}点）")
        print(f"  レシピに残すなら \"at\": {at:.0f}")

    crop = tuple(thumb.get("crop") or (0.30, 0.25, 0.35))
    if a.auto_crop or not thumb.get("crop"):
        crop = auto_crop(Image.open(frame).convert("RGB"))
        print(f"  auto-crop = [{crop[0]:.3f}, {crop[1]:.3f}, {crop[2]:.3f}]")

    img = compose(
        frame,
        thumb.get("main") or [recipe["title"][:12]],
        thumb.get("sub") or "",
        crop,
    )
    dst = out_dir / "thumb.png"
    img.save(dst)
    print(f"✓ {dst}  {img.size[0]}x{img.size[1]}")


if __name__ == "__main__":
    main()
