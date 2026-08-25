#!/usr/bin/env python3
"""レシピが使う区間だけを落とす。

  python scripts/fetch_clips.py recipes/<id>.json
  python scripts/fetch_clips.py recipes/<id>.json --pad 3

出力は work/clips/<video_id>_<start>-<end>.mp4。

**全編を落とす必要はない。** ひろゆきの配信は1本2〜6時間あり、1080pだと
1本4〜8GB になる。5本使う構成なら20〜40GB。実際に必要なのは合計17分ほど。

yt-dlp の --download-sections で範囲だけ取れば300MB程度で済む。
`--force-keyframes-at-cuts` を付けないと、キーフレーム境界の都合で
指定より前から始まったり、冒頭が壊れたりする。

出てくるファイルは**先頭が0秒**になる。元動画の時刻ではないので、
build_episode.py 側はこのファイルを使うときクリップの start を0として扱う。
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from scripts.fetch_source import BLOCKED, WORK  # noqa: E402

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CLIPS = WORK / "clips"

RETRIES = 4          # 403 が出たら間隔を倍にして待ち直す
BACKOFF_SEC = 30

# **cookie 無しでは1本目の直後から 403 が続く**（2026-08-14 実測）。
# プレーヤークライアントもコーデックも変えたが抜けられず、cookie で解決した。
#
# **Chrome と Edge からは cookie を取れない。** 2026-08-18 の実測:
#   起動中の Chrome        Could not copy Chrome cookie database（DBロック）
#   閉じている Profile 1   Failed to decrypt with DPAPI（アプリバウンド暗号化）
#   Edge                   Failed to decrypt with DPAPI
# ロックを外しても復号で落ちるので、**Chrome を閉じても解決しない**。
# Firefox は暗号化方式が違うので起動していても読める。ただし
# プロファイルにログイン済みの cookie が無ければ 0件になる（2026-08-18 に遭遇。
# cookies.sqlite が1年前から更新されておらず、全区間が 403 になった）。
#
# ブラウザから取れないときは Netscape 形式の cookies.txt を --cookies で渡す。
DEFAULT_BROWSER = "firefox"



# **yt-dlp は JS ランタイムが無いと動画フォーマットを1つも返さない。**
# 2026-08-25 に全区間が "Requested format is not available" で落ちた。Cookie は通っていて、
# --list-formats がストーリーボード（sb0..sb3）しか返さない状態だった。原因は
# YouTube の n チャレンジで、yt-dlp 2026.08.19 は js_runtimes の既定が deno だけ。
# この環境に deno は無く、Node v24.1.0 はあるのに使われていなかった。
# 明示的に渡さないと毎回同じ所で落ちるので、使えるものを探して渡す。
JS_RUNTIMES = ("deno", "node", "bun")


def available_js_runtime() -> str | None:
    """yt-dlp に渡せる JS ランタイム名。無ければ None。"""
    for name in JS_RUNTIMES:
        if shutil.which(name):
            return name
    return None


def clip_path(video_id: str, start: float, end: float) -> Path:
    return CLIPS / f"{video_id}_{int(start)}-{int(end)}.mp4"


def fetch(video_id: str, start: float, end: float, pad: float = 2.0,
          force: bool = False, browser: str | None = DEFAULT_BROWSER,
          cookies: Path | None = None) -> Path:
    """指定区間を落とす。前後に pad 秒の余白を付ける。

    余白は編集で頭とお尻を詰められるようにするため。キーフレーム境界の
    ずれも吸収する。
    """
    if video_id in BLOCKED:
        raise SystemExit(f"! {video_id} は権利者がブロック指定した動画")

    out = clip_path(video_id, start, end)
    if out.exists() and not force:
        print(f"- {out.name} は取得済み")
        return out
    CLIPS.mkdir(parents=True, exist_ok=True)

    a = max(0.0, start - pad)
    b = end + pad
    cmd = [sys.executable, "-m", "yt_dlp",
           "--no-warnings"]
    # cookies.txt があればそちらを優先する。ブラウザから取れない環境用
    if cookies:
        cmd += ["--cookies", str(cookies)]
    elif browser:
        cmd += ["--cookies-from-browser", browser]
    runtime = available_js_runtime()
    if runtime:
        cmd += ["--js-runtimes", runtime]
    else:
        print("! JS ランタイム（deno / node / bun）が見つかりません。"
              "動画フォーマットが1つも返らずに落ちる可能性があります")
    cmd += [
           "--extractor-args", "youtube:lang=ja",
           "--download-sections", f"*{a:.2f}-{b:.2f}",
           "--force-keyframes-at-cuts",
           "-f", "bestvideo[height<=1080]+bestaudio/best",
           "--merge-output-format", "mp4",
           "-o", str(out),
           f"https://www.youtube.com/watch?v={video_id}"]

    # 実測（2026-08-14）で1本目の直後から連続して 403 Forbidden になった。
    # 動画やコーデックを変えても再現したので、YouTube 側のレート制限。
    # プレーヤークライアントを変えても抜けられなかったので、素直に待つ。
    for attempt in range(RETRIES):
        r = subprocess.run(cmd, capture_output=True, text=True)
        if r.returncode == 0 and out.exists():
            size = out.stat().st_size / 1e6
            print(f"✓ {out.name}  {b - a:.0f}s  {size:.0f}MB")
            return out
        out.unlink(missing_ok=True)
        blocked = "403" in (r.stderr or "") or "Forbidden" in (r.stderr or "")
        if attempt == RETRIES - 1:
            tail = (r.stderr or "").strip().splitlines()[-1:] or ["(出力なし)"]
            raise SystemExit(
                f"! {video_id} {int(start)}-{int(end)} を取得できません: {tail[0][:120]}\n"
                "  403 が続く場合は時間を置いてください（レート制限）。"
                "  途中まで取れたぶんは work/clips/ に残るので再開できます。")
        wait = BACKOFF_SEC * (2 ** attempt)
        print(f"  再試行 {attempt + 1}/{RETRIES - 1}"
              f"（{'403 レート制限' if blocked else 'エラー'}／{wait}秒待つ）")
        time.sleep(wait)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("recipe", type=Path)
    ap.add_argument("--pad", type=float, default=2.0)
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--browser", default=DEFAULT_BROWSER,
                    help="cookie を読むブラウザ。none で cookie 無し")
    ap.add_argument("--cookies", type=Path,
                    help="Netscape 形式の cookies.txt。指定すると --browser より優先")
    a = ap.parse_args()

    if a.cookies and not a.cookies.exists():
        raise SystemExit(f"! {a.cookies} がありません")

    recipe = json.loads(a.recipe.read_text(encoding="utf-8"))
    clips = recipe.get("clips") or recipe.get("clips", [])
    total = sum(c["end"] - c["start"] for c in clips)
    print(f"{len(clips)}区間 / 合計 {int(total) // 60}:{int(total) % 60:02d}\n")

    # **1本失敗しても残りを続ける。** 途中で止めると、後ろのぶんを取り直すために
    # また全部を舐め直すことになる。403 は区間ごとに出たり出なかったりする
    failed = []
    for c in clips:
        try:
            fetch(c["video_id"], c["start"], c["end"], a.pad, a.force,
                  None if a.browser == "none" else a.browser, a.cookies)
        except SystemExit as e:
            print(str(e).splitlines()[0])
            failed.append((c["video_id"], int(c["start"]), int(c["end"])))
    if failed:
        print(f"\n! {len(failed)}区間が未取得。時間を置いて同じコマンドを再実行してください")
        for v, s_, e_ in failed:
            print(f"  {v} {s_}-{e_}")
        # **未取得を残したまま成功で終わらない。** 一覧は出していたのに
        # チェーン実行の中で流れてしまい、2回続けてビルドまで進めた
        # （2026-08-14）。止まるべきところで止める
        raise SystemExit(1)

    got = list(CLIPS.glob("*.mp4"))
    print(f"\n{len(got)}ファイル / "
          f"{sum(p.stat().st_size for p in got) / 1e6:.0f}MB")


if __name__ == "__main__":
    main()
