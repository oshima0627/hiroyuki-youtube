#!/usr/bin/env python3
"""VOICEVOX で解説ナレーションを合成する。

  python scripts/narration.py --speakers          # 話者一覧
  python scripts/narration.py --say "テスト文"     # 単発で試す

**VOICEVOX の起動が前提。** エンジンは既定で http://127.0.0.1:50021 に立つ。
アプリを起動していれば一緒に立ち上がる。

なぜ音声を入れるか。YouTube の「再利用されたコンテンツ」判定に対して、
音声解説はいちばん強い付加価値の証拠になる。テロップだけだと、
実測で独自要素が 873秒中60秒（6.9%）しかなかった。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import time
import sys
import urllib.parse
import urllib.request
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "work" / "narration"

HOST = "http://127.0.0.1:50021"
SPEAKER = 13          # 青山龍星 ノーマル

# 解説は淡々と読ませる。配信本編が雑談口調なので、抑揚を付けすぎると浮く
SPEED = 1.05
PITCH = 0.0
INTONATION = 1.0


def _post(path: str, params: dict, body: bytes | None = None) -> bytes:
    url = f"{HOST}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(
        url, data=body if body is not None else b"", method="POST",
        headers={"Content-Type": "application/json"})
    return urllib.request.urlopen(req, timeout=120).read()


def speakers() -> list[dict]:
    return json.load(urllib.request.urlopen(f"{HOST}/speakers", timeout=30))


def synth(text: str, speaker: int = SPEAKER, force: bool = False) -> Path:
    """テキストを WAV にして返す。同じ文は作り直さない。"""
    text = text.strip()
    if not text:
        raise ValueError("空のテキストは合成できない")

    key = hashlib.sha1(
        f"{speaker}:{SPEED}:{PITCH}:{INTONATION}:{text}".encode()).hexdigest()[:16]
    out = CACHE / f"{key}.wav"
    if out.exists() and not force:
        return out
    CACHE.mkdir(parents=True, exist_ok=True)

    # 長い文でエンジンが詰まって recv がタイムアウトすることがある。
    # ビルド全体が落ちると10分ぶんのエンコードをやり直すので、ここで粘る
    q = None
    for attempt in range(3):
        try:
            q = json.loads(_post("/audio_query", {"text": text, "speaker": speaker}))
            break
        except Exception as e:                              # noqa: BLE001
            if attempt == 2:
                raise SystemExit(
                    f"! VOICEVOX に接続できません（{HOST}）: {str(e)[:80]}\n"
                    "  VOICEVOX を起動してから再実行してください") from e
            print(f"  VOICEVOX 再試行 {attempt + 1}/2（{str(e)[:40]}）")
            time.sleep(5)

    q["speedScale"] = SPEED
    q["pitchScale"] = PITCH
    q["intonationScale"] = INTONATION
    # 前後の無音。詰めすぎると前のカットの語尾に食い込む
    q["prePhonemeLength"] = 0.3
    q["postPhonemeLength"] = 0.5

    wav = _post("/synthesis", {"speaker": speaker},
                json.dumps(q, ensure_ascii=False).encode("utf-8"))
    out.write_bytes(wav)
    return out


def duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True)
    return float(out.stdout.strip())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--speakers", action="store_true")
    ap.add_argument("--say")
    ap.add_argument("--speaker", type=int, default=SPEAKER)
    a = ap.parse_args()

    if a.speakers:
        for s in speakers():
            styles = " ".join(f"{st['id']}:{st['name']}" for st in s["styles"])
            print(f"{s['name']}  {styles}")
        return

    if a.say:
        p = synth(a.say, a.speaker)
        print(f"✓ {p}  {duration(p):.2f}s")
        return

    ap.print_help()


if __name__ == "__main__":
    main()
