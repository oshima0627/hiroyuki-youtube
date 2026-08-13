#!/usr/bin/env python3
"""切り抜き地点を探すための信号を扱う純粋関数。

tora-kirinuki からの移植。音量・ヒートマップ・コメントの実装はそのまま使えるが、
**語彙は作り直した。** 番組の構造がまるで違う。

  令和の虎    持ち込み → 虎が詰める → 出資判定  という一本の流れ
  ひろゆき    視聴者の質問 → 回答 を延々と繰り返す

そのため信号の効き方も変わる。

  音量      **弱い。** ひろゆきは怒鳴らない。ビールを飲みながら淡々と話す。
            令和の虎では虎が激怒すれば必ず音量に出たが、ここでは当てにならない
  質問語彙  **主軸。** 「教えてください」「どう思いますか」で回答の切れ目が取れる
  コメント  精度が高い。令和の虎と同じく効く
  ヒートマップ 5万回以上かつ3週間以上経過の回にしか無い（tora-kirinuki 実測 30本中7本）。
            新着では使えないので加点扱い
"""

from __future__ import annotations

import re
import statistics

# 前後が数字やコロンでない mm:ss / h:mm:ss だけを拾う
TS_RE = re.compile(r"(?<![\d:])(?:(\d{1,2}):)?(\d{1,2}):(\d{2})(?![\d:])")
SAMPLE_LIMIT = 3


def parse_heatmap(data: dict) -> list[dict]:
    """ytInitialData から Most replayed を [{"start","end","score"}, ...] にする。"""
    out: list[dict] = []

    def walk(o):
        if isinstance(o, list):
            for x in o:
                walk(x)
            return
        if not isinstance(o, dict):
            return
        ml = (o.get("macroMarkersListEntity") or {}).get("markersList")
        if ml and ml.get("markerType") == "MARKER_TYPE_HEATMAP":
            for m in ml.get("markers") or []:
                start = int(m.get("startMillis", 0)) / 1000
                dur = int(m.get("durationMillis", 0)) / 1000
                out.append({
                    "start": start,
                    "end": start + dur,
                    "score": float(m.get("intensityScoreNormalized", 0.0)),
                })
        for v in o.values():
            walk(v)

    walk(data)
    return out


def extract_timestamps(text: str) -> list[int]:
    """コメント本文の mm:ss / h:mm:ss を秒に変換して返す。"""
    return [(int(h) if h else 0) * 3600 + int(m) * 60 + int(s)
            for h, m, s in TS_RE.findall(text or "")]


def aggregate_marks(comments: list[str]) -> list[dict]:
    """秒ごとに言及を集計する。言及数の多い順、同数なら秒の小さい順。"""
    bucket: dict[int, list[str]] = {}
    for c in comments:
        for sec in extract_timestamps(c):
            bucket.setdefault(sec, []).append(c)
    marks = [{"seconds": sec, "count": len(v), "samples": v[:SAMPLE_LIMIT]}
             for sec, v in bucket.items()]
    marks.sort(key=lambda m: (-m["count"], m["seconds"]))
    return marks


# ── 音量 ────────────────────────────────────────────────────────────

ASTATS_T_RE = re.compile(r"pts_time:([\d.]+)")
ASTATS_DB_RE = re.compile(r"lavfi\.astats\.Overall\.RMS_level=(-?[\d.]+|-inf)")


def parse_astats(text: str, bin_sec: float = 1.0) -> list[dict]:
    """ffmpeg の astats 出力を、秒ごとの平均dBにまとめる。"""
    bins: dict[float, list[float]] = {}
    cur_t: float | None = None
    for line in text.splitlines():
        m = ASTATS_T_RE.search(line)
        if m:
            cur_t = float(m.group(1))
            continue
        m = ASTATS_DB_RE.search(line)
        if m and cur_t is not None:
            if m.group(1) == "-inf":
                continue
            bins.setdefault((cur_t // bin_sec) * bin_sec, []).append(float(m.group(1)))
    return [{"t": t, "db": statistics.fmean(v)} for t, v in sorted(bins.items())]


def loudness_scores(env: list[dict], baseline_sec: float = 120.0) -> list[dict]:
    """局所的な基準からどれだけ跳ねたかを 0..1 で返す。"""
    if not env:
        return []
    half = max(1, int(baseline_sec / 2))
    out = []
    for i, e in enumerate(env):
        lo, hi = max(0, i - half), min(len(env), i + half + 1)
        base = statistics.median(x["db"] for x in env[lo:hi])
        out.append({"t": e["t"], "db": e["db"], "over": e["db"] - base})

    peak = max((o["over"] for o in out), default=0.0)
    if peak <= 0:
        return [{"t": o["t"], "score": 0.0} for o in out]
    return [{"t": o["t"], "score": max(0.0, o["over"]) / peak} for o in out]


# ── 字幕の語彙 ──────────────────────────────────────────────────────

# 「質問」は回答の切れ目を取るための境界語。ひろゆきは視聴者の質問文を
# 読み上げてから答えるので、この語で1問1答のブロックに割れる。
# 実素材 23vSB2fXjc8（3時間23分）で12問が取れた（2026-08-14 実測）。
#
# 「断言」は切り抜きの中身になる言い切り。ひろゆきの回答は結論が先に来る。
# 「留保」は断定を弱める言い回しで、**あるほど安全**。ミスリード扱いされにくい。
LEXICON: dict[str, tuple[str, ...]] = {
    "質問": ("教えてください", "どう思いますか", "どうすればいい", "どうしたらいい",
             "でしょうか", "ますか?", "ますか？", "ですか?", "ですか？",
             "いかがでしょう", "アドバイス", "相談"),
    "断言": ("と思います", "じゃないですかね", "無理だと思います", "意味がない",
             "やめた方がいい", "頭が悪い", "そもそも", "要するに", "逆に言うと",
             "普通に", "別に"),
    "根拠": ("によると", "データ", "統計", "論文", "調査", "実際に", "例えば",
             "フランス", "海外では", "制度"),
    "留保": ("かもしれない", "場合による", "人によります", "知らないですけど",
             "分からないですけど", "個人的には"),
}

# 切り抜きに使ってはいけない話題。当たったブロックは候補から落とす。
# 権利者ガイドラインとYouTubeポリシーの両方に効く。
#   - 特定個人・企業の信用に関わる話（名誉毀損）
#   - 政治・選挙（ミスリード扱いされやすい／収益化にも不利）
#   - 自傷・性・未成年（センシティブ）
AVOID: dict[str, tuple[str, ...]] = {
    # 「辺野古」「山本太郎氏のスピード違反」が素通りして候補に入った。
    # 短いトピックは前のブロックに統合されるので、1つでも政治の話題が
    # 混ざると束全体が政治動画になる（2026-08-14 実測）
    "政治": ("選挙", "総裁選", "自民党", "立憲", "議員", "総理", "首相", "内閣",
             "消費税", "増税", "改憲", "侵攻", "戦争", "辺野古", "沖縄", "知事",
             "大統領", "政党", "政治家", "維新", "参政党", "防衛", "基地"),
    # 「氏」はトピックタイトルではほぼ確実に実名の公人を指す
    "個人": ("社長", "会長", "氏", "さんは無能", "退任", "決算", "不祥事", "逮捕"),
    # 死刑・女子トイレ侵入は実測で取りこぼして候補に選ばれてしまった。
    # 取りこぼしは「選ばれる側」なので危険度が高い。疑わしければ入れる
    "センシティブ": ("自殺", "死にたい", "性病", "セックス", "風俗", "レイプ",
                     "未成年", "小学生", "中学生", "うつ", "薬物", "休学",
                     "死刑", "殺人", "虐待", "ネグレクト", "いじめ", "差別", "宗教",
                     "障害", "浮気", "不倫", "生活保護",
                     "トイレ侵入", "女子トイレ", "わいせつ", "痴漢", "停学", "退学"),
    # 中身が無い運営ブロック。挨拶・機材調整・配信の締めなど。
    # 実測で「配信終了と今後のコミュニティ形成」がコメント言及13件で
    # 1位になった。配信の最後は「面白かった」コメントが集まるので数字が出る
    "雑務": ("挨拶", "乾杯", "マイク", "ノイズ", "音声トラブル", "配信開始",
             "配信終了", "放送開始", "ラグ", "接続", "告知", "ビールの感想",
             "ビールの紹介", "ビールの準備", "宅配便"),
}


def _flatten(cues: list[dict]) -> tuple[str, list[tuple[int, float, str]]]:
    """全キューを1本の文字列に繋ぎ、(開始位置, 時刻, 元の行) の索引を返す。

    **行ごとに検索してはいけない。** 自動字幕は任意の位置で行が割れるので、
    「生活保護」が「…生活」「保護取った方が…」に分断されると、行単位の
    `in` 判定はどの行にも当たらない。実際にこれで安全フィルタが黙って
    素通りした（2026-08-14）。2文字の分断で検出が消える設計は使えない。
    """
    parts, index, pos = [], [], 0
    for c in cues:
        line = c.get("line") or ""
        index.append((pos, float(c.get("t") or 0), line))
        parts.append(line)
        pos += len(line)
    return "".join(parts), index


def _time_at(index: list[tuple[int, float, str]], i: int) -> tuple[float, str]:
    lo, hi, r = 0, len(index) - 1, 0
    while lo <= hi:
        mid = (lo + hi) // 2
        if index[mid][0] <= i:
            r, lo = mid, mid + 1
        else:
            hi = mid - 1
    return index[r][1], index[r][2]


def _scan(cues: list[dict], table: dict[str, tuple[str, ...]]) -> list[dict]:
    text, index = _flatten(cues)
    out = []
    for kind, words in table.items():
        for w in words:
            i = text.find(w)
            while i >= 0:
                # 時刻は float のまま持つ。int で切り捨てると 6561.4 が 6561 になり、
                # ブロック開始 6561.4 の直前に落ちて範囲外と判定される（2026-08-14）
                t, line = _time_at(index, i)
                out.append({"seconds": t, "kind": kind, "word": w, "line": line})
                i = text.find(w, i + 1)
    out.sort(key=lambda m: m["seconds"])
    return out


def lexical_marks(cues: list[dict]) -> list[dict]:
    """字幕から定型語彙を拾う。[{"seconds","kind","word","line"}, ...]"""
    return _scan(cues, LEXICON)


def avoid_marks(cues: list[dict]) -> list[dict]:
    """使ってはいけない話題の出現位置。[{"seconds","kind","word","line"}, ...]"""
    return _scan(cues, AVOID)
