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


# **VOICEVOX は漢字を読み間違える。** 実測（2026-08-14）で
#   未達 → ヒツジタチ（正: ミタツ）
# が出た。意味が通らない音になるので、聞いた人には解説が壊れて聞こえる。
#
# 対策は2段構え。
#   1. ここに読みを登録して VOICEVOX のユーザー辞書へ入れる
#   2. `--kana <recipe>` で全文の読みを出し、公開前に目で確認する
#
# **辞書で直せないものが2種類ある。原稿の言い回しを変えるしかない。**
#   連濁     「上司の引き」が「ビキ」になる（文脈で決まる）
#   活用形   「並べて」が古語の「なべて」になる。ユーザー辞書に "並べて" を
#            登録しても効かない。形態素解析が 並べ+て に割るため
# どちらも実測で確認した（2026-08-14）。
READINGS: dict[str, tuple[str, int]] = {
    # 表記: (カタカナ読み, アクセント核の位置。0は平板)
    "未達": ("ミタツ", 0),
    "切り抜き": ("キリヌキ", 0),
    "元動画": ("モトドウガ", 0),
    "概要欄": ("ガイヨウラン", 0),
    "登録者": ("トウロクシャ", 3),
}


def register_readings() -> int:
    """READINGS を VOICEVOX のユーザー辞書へ入れる。既にあるものは飛ばす。"""
    try:
        cur = json.load(urllib.request.urlopen(f"{HOST}/user_dict", timeout=30))
    except Exception as e:                                  # noqa: BLE001
        print(f"! ユーザー辞書を読めません（{str(e)[:50]}）")
        return 0
    have = {w.get("surface") for w in cur.values()}
    n = 0
    for surface, (pron, accent) in READINGS.items():
        if surface in have:
            continue
        try:
            _post("/user_dict_word", {"surface": surface, "pronunciation": pron,
                                      "accent_type": accent})
            n += 1
        except Exception as e:                              # noqa: BLE001
            print(f"! {surface} を登録できません: {str(e)[:60]}")
    return n


def kana_of(text: str, speaker: int = SPEAKER) -> str:
    """読み仮名を返す。合成せずに読みだけ確認できる。"""
    q = json.loads(_post("/audio_query", {"text": text, "speaker": speaker}))
    return q.get("kana", "")


def speakers() -> list[dict]:
    return json.load(urllib.request.urlopen(f"{HOST}/speakers", timeout=30))


_DICT_DONE = False


def _ensure_dict() -> None:
    """合成の前に一度だけ辞書を入れる。入れ忘れると誤読のまま焼き込まれる。"""
    global _DICT_DONE
    if not _DICT_DONE:
        register_readings()
        _DICT_DONE = True


def synth(text: str, speaker: int = SPEAKER, force: bool = False) -> Path:
    """テキストを WAV にして返す。同じ文は作り直さない。"""
    text = text.strip()
    if not text:
        raise ValueError("空のテキストは合成できない")

    _ensure_dict()
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
    ap.add_argument("--kana", type=Path,
                    help="レシピの解説とまとめの読み仮名を全部出す（公開前の確認用）")
    ap.add_argument("--register", action="store_true",
                    help="READINGS を VOICEVOX のユーザー辞書へ登録する")
    a = ap.parse_args()

    if a.register:
        print(f"✓ {register_readings()}語を登録しました")
        return

    if a.kana:
        import json as _json
        r = _json.loads(a.kana.read_text(encoding="utf-8"))
        register_readings()
        for i, c in enumerate(r["clips"]):
            print(f"■{i} {c['note']}")
            print(f"  →{kana_of(c['note'])}\n")
        if r.get("summary"):
            print(f"■まとめ {r['summary']}")
            print(f"  →{kana_of(r['summary'])}")
        return

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
