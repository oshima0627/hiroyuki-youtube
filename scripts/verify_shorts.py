#!/usr/bin/env python3
"""ビルドしたショートを、レシピと突き合わせて検証する。**投稿の前に必ず通す。**

  python scripts/verify_shorts.py                    # 未投稿のぶんを全部
  python scripts/verify_shorts.py 2026-10-01-am ...  # 指定したものだけ
  python scripts/verify_shorts.py --all              # 投稿済みも含めて全部

## なぜ要るか

**ビルド成果物は「あれば正しい」とは限らない。** 2026-08-26 に、日付の振り直しで
`shutil.move(src, dst)` を使ったところ dst が既存ディレクトリで、9本が
「古い成果物が親、正しい成果物が入れ子」という状態になった。さらに3本は
古い `video.mp4` が居座ったせいでビルドがスキップされ、**別の動画が上がる直前**だった。

気づけたのは ffprobe の尺と md5 を突き合わせたから。手でやると次に忘れるので、
コマンドにしてある。

見るもの: 尺（レシピの short.end - short.start と一致するか）/ 解像度 /
md5 の重複 / meta.json の id・title・publish_at がレシピと一致するか。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SHORTS = ROOT / "recipes" / "shorts"
WORK = ROOT / "work" / "shorts"
PUBLISHED = ROOT / "state" / "published.json"

# ffmpeg はキーフレーム境界で切るので、指定と実尺は完全には一致しない
TOLERANCE_SEC = 0.6
EXPECTED_RES = "1080x1920"


def probe(mp4: Path, args: list[str]) -> str:
    return subprocess.run(["ffprobe", "-v", "error", *args, str(mp4)],
                          capture_output=True, text=True).stdout.strip()


def load(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8-sig"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("ids", nargs="*", help="省略すると未投稿のぶんを全部")
    ap.add_argument("--all", action="store_true", help="投稿済みも含めて全部")
    a = ap.parse_args()

    published = (load(PUBLISHED, {"videos": {}}) or {}).get("videos", {})
    ids = a.ids or sorted(p.stem for p in SHORTS.glob("*.json")
                          if a.all or p.stem not in published)
    if not ids:
        print("対象なし（未投稿のショートは無い）")
        return

    seen: dict[str, str] = {}
    bad = 0
    print(f"{'id':16} {'実尺':>7} {'レシピ':>7} {'差':>6} {'解像度':11} "
          f"{'publish_at':21} title")
    for rid in ids:
        recipe = load(SHORTS / f"{rid}.json")
        out = WORK / rid
        mp4, metaf = out / "video.mp4", out / "meta.json"
        if recipe is None or not mp4.exists() or not metaf.exists():
            print(f"{rid:16} ✗ レシピか成果物が無い"
                  f"（recipe={'有' if recipe else '無'} "
                  f"video={'有' if mp4.exists() else '無'}）")
            bad += 1
            continue

        meta = load(metaf)
        want = float(recipe["short"]["end"]) - float(recipe["short"]["start"])
        got = float(probe(mp4, ["-show_entries", "format=duration",
                                "-of", "csv=p=0"]))
        res = probe(mp4, ["-select_streams", "v:0", "-show_entries",
                          "stream=width,height", "-of", "csv=p=0:s=x"])
        md5 = hashlib.md5(mp4.read_bytes()).hexdigest()

        flags = []
        if abs(got - want) > TOLERANCE_SEC:
            flags.append(f"尺ズレ {got - want:+.2f}秒")
        if res != EXPECTED_RES:
            flags.append(f"解像度 {res}")
        if md5 in seen:
            flags.append(f"md5 が {seen[md5]} と同一")
        seen[md5] = rid
        if meta.get("id") != rid:
            flags.append(f"meta.id={meta.get('id')}")
        if meta.get("title") != recipe.get("title"):
            flags.append("title がレシピと違う")
        if meta.get("publish_at") != recipe.get("publish_at"):
            flags.append("publish_at がレシピと違う")

        print(f"{rid:16} {got:7.2f} {want:7.2f} {got - want:+6.2f} {res:11} "
              f"{str(meta.get('publish_at')):21} {meta.get('title', '')}")
        if flags:
            bad += 1
            print(f"{'':16} ✗ " + " / ".join(flags))

    print(f"\n{len(ids)}本 / 異常 {bad}本")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
