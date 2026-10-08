# HANDOFF
????: 2026-10-08???ops: ?????????????????????????????????

---

## ▶ このセッションで最初に実行するコマンド

`ash
cd C:/Users/oshim/Documents/projects/hiroyuki-youtube; python scripts/ops_youtube.py --status
`

10/7・10/8・10/9 の長尺は予約済み（10/7・10/8は既存、10/9は本日作成）。関連動画紐づけは夕方ルーチン（18:35）。10/4・10/5 長尺空白は未補填（過去日付は即時公開になるので埋めない）。

---

## いま何をしているのか

ひろゆき切り抜きチャンネル「ひろゆき解説ch【切り抜き】」(UCqK3KYqEeeJiAWr4nSryJYQ) の日次運用。

## 今回やったこと（2026-10-07）

1. ops_youtube.py --status で実状態取得（API正）
2. 当日ショート V8z1YsBJe3M は既に public（07:00公開済み）→ 作成スキップ
3. 当日長尺 IYcOd70aT_g は private→2026-10-07T09:30:00Z（18:30 JST）予約済み → 作成スキップ
4. 翌日長尺 hFeUyOQ1QO0 も 10/8 18:30 予約済みを確認
5. 在庫補充として新規レシピ 
ecipes/2026-10-09-aijob.json を作成 → fetch → build（8:48）→ upload → 10/9 18:30 予約（718Lsuq9bgE）。サムネ API 成功
6. 当日ショート V8z1YsBJe3M の「フルで見る」を 1Qk53tSphDg → xAHwnOlrbpw（10/6長尺）へ差し替え
7. Studio 関連動画は触っていない

## 予約済み長尺

| 公開 (JST) | レシピ | ID | 尺 | タイトル |
| --- | --- | --- | --- | --- |
| 10/7 18:30 | 2026-10-07-un | IYcOd70aT_g | 13:52 | 【ひろゆき】運と才能の話5連発。運は打席に立った回数です |
| 10/8 18:30 | 2026-10-08-gaman | hFeUyOQ1QO0 | 14:04 | 【ひろゆき】我慢とストレスの話6連発。人は痛みを忘れて我慢してしまいます |
| 10/9 18:30 | 2026-10-09-aijob | 718Lsuq9bgE | 8:48 | 【ひろゆき】AIと仕事の話6連発。デスクワークは機械に勝てません |

公開済み: 10/6 18:30 xAHwnOlrbpw（人間関係）public。

## 検証済みの事実

- status 上 IYcOd70aT_g / hFeUyOQ1QO0 / 718Lsuq9bgE は private→publishAt（09:30Z）
- V8z1YsBJe3M の description「フルで見る」は xAHwnOlrbpw を指す（API更新済み）
- ショート予約在庫は 10/8〜10/16 朝 07:00（API: 10/7〜10/15T22:00Z）まで存在
- サムネ API（thumbnails.set）: 718Lsuq9bgE 成功
- VOICEVOX 0.25.2 稼働

## 未検証のもの

- 新テーマ（AIと仕事）の再生数
- 8:48はやや短め（15分未満はクリア）。次回は本編尺を厚くしてもよい

## 次にやること

1. 夕方 18:35 関連動画紐づけ（夕方ルーチン）
2. 10/10 以降の長尺在庫が薄くなったら新規レシピで追加（過去日付は不可）
3. 必要なら rM4ftL719w4（10/6ショート）のフル導線も見直し（現状は uoU2nsKnMrA のまま）

## 触ってはいけないところ

- 「公式」「公認」と書かない
- 切り抜き禁止: exnFXUMMLLI / q0GyNI3X8cg
- ゲスト共演回（例: IXiLxkgHUMM 石丸氏、naVkgtFmRvg、Sq1YChd0RqQ【ひろゆきと語る夜】）は使わない
- 政治的な話題は落とす
- 予約時刻を過ぎた publishAt を渡さない（即時公開になる）
- 15分超は上げない（電話番号未確認）
- _plan-kenko / _plan-kosodate / _plan-kigyo は使わない
- note 不足の _plan は埋めない（新規 JSON を recipes/ に作る）
- Studio 関連動画は朝ルーチンで触らない
