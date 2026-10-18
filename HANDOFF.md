# HANDOFF
最終更新: 2026-10-18 19:20 JST（10/18 14:13 日次の続き: 10/19 長尺と 10/19 07:00 ショートを作成・予約）

## ▶ 最初に実行するコマンド（Linux ボックス）

```bash
cd /workspace/hiroyuki-youtube && .venv/bin/python scripts/ops_youtube.py --status
curl -s 127.0.0.1:50021/version   # VOICEVOX 0.25.2（/workspace/voicevox）。返らなければ起動する
```

## いま何をしているのか

ひろゆき切り抜きチャンネル「ひろゆき解説ch【切り抜き】」(UCqK3KYqEeeJiAWr4nSryJYQ) の日次運用。
2026-10-10 から Linux ボックス（/workspace/hiroyuki-youtube）で回し始めた。PC（ASUS_i9, C:\Users\oshim\Documents\projects\hiroyuki-youtube）は素材取得だけに使った。

## Linux ボックスでの手順（2026-10-10 実績）

1. `work/` は git 管理外。候補探しに必要な字幕・メタ（work/**/*.json, *.txt, *.py、約5MB zip）は PC から tar で CopyToBox して展開した。新しい配信を候補に足すときは fetch_source.py --subs-only（ボックスで未検証）か PC から再コピー。
2. 未使用ブロック一覧: `work/_unused_1014.py` の出力先を変えて実行 → `work/_unused_1016.txt`（再生成で更新）。
3. レシピを recipes/ に作り `PYTHONPATH=. .venv/bin/python -c "from scripts.recipe import validate ..."` で検証。
4. **クリップ取得はボックスで可（2026-10-12〜）**: `PYTHONPATH=. .venv/bin/python scripts/fetch_clips.py recipes/<id>.json --browser none`。
   cookie 無しだと bestvideo が Premium の HLS（itag 616）を選んで書き出し0のまま止まるため、fetch_clips.py の -f を avc1 の HLS（270/232）+ m4a 優先に変更済み。
   取れなくなったら PC で `python scripts/fetch_clips.py recipes/<id>.json`（Firefox cookie）→ work/clips/*.mp4 を tar → CopyToBox。
5. ボックスで `build_episode.py` → `thumbnail.py` → `build_episode.py --concat-only`（冒頭カード）→ `upload_youtube.py work/<id> --schedule <UTC>`。
6. `ops_youtube.py --status` で private→publishAt を確認。サムネは `set_thumbnails.py --only <id>`（必要なら `--force`）。

## 今回やったこと（2026-10-18 14:13 日次 → 途中停止 → 19:00 に再開して完了）

- 止まった原因: 14:18〜15:02 の fetch_clips.py（cookie 無し）で jmADUo9Vcho 162-286 / jPOui7xHeOw 4585-4642 が
  「ログインして bot ではないことを確認してください」（YouTube の bot 判定）で3回リトライ後に失敗し exit 1。
  1回目は 25 分の timeout で Terminated(143)。ショート素材 4vmH4mejnjI 4413-4471 も未取得のまま止まった。
  18:50 の再実行でも同じ bot 判定。player_client=web_embedded はフォーマット0、android_vr は 360p のみ
- 対処: PC（ASUS_i9）で `python scripts\fetch_clips.py work\tmp-1019-fetch.json`（Firefox cookie、未取得3区間だけの一時レシピ）→ CopyToBox で work/clips へ（1080p）
- 翌日長尺 recipes/2026-10-19-suimin.json → **HNNmVJ2MAls**「睡眠の話7連発。目覚ましで起きる人は睡眠が足りていません」13:18、private→2026-10-19T09:30Z（10/19 18:30 JST）。
  thumb.at は 15（冒頭カード追加前の時刻で顔が崩れた）→ 90 に変更（腕時計を見るカット）。サムネ API 反映を差分 0.85 で確認
- 翌日ショート recipes/shorts/2026-10-19-am.json → **ERaQcCP2p2I**「会社のカードを私用した部長が逃げたら」56秒、private→2026-10-18T22:00Z（10/19 07:00 JST）。
  フルで見る→k5hQ5NpJHQU（parent 2026-10-18-mitame、10/18 18:30 公開済み）。問いかけ「「回収できないなら泣き寝入りも合理的」この考え方、アリ？ナシ？」
  冒頭〜15秒はスパチャを読んで下を向くので顔の下半分が黒帯側に切れる（build_short の自動クロップのまま）
- hxzDGMs-aWE のフルで見るは既に id0Ju8MPkBU（更新不要、API で確認）
- 未使用ブロック一覧は work/_unused_1018.txt

## 前回やったこと（2026-10-17 14:13 日次）

- 当日ショート hxzDGMs-aWE（07:00 公開済）・当日長尺 id0Ju8MPkBU（18:30 予約済）は既存でスキップ
- 翌日長尺 recipes/2026-10-18-mitame.json → **k5hQ5NpJHQU**「見た目とブランドの話7連発。ジム通いはブランド消費です」11:20、private→2026-10-18T09:30Z（10/18 18:30 JST）、サムネ API 設定済み。未使用ブロック一覧は work/_unused_1017.txt
- 翌日ショート recipes/shorts/2026-10-18-am.json → **UlaZRnjIeXA**「結露の壁紙で16万円請求されたら」65秒、private→2026-10-17T22:00Z（10/18 07:00 JST）。フルで見る→id0Ju8MPkBU（parent 2026-10-17-sake）
  - ショート単体レシピは fetch_clips.py が拾わない（0区間）。clips:[clip] の一時レシピを作って fetch した
- フルで見る: 5UDR-8tVjAE → Mw4CM0_gFhw に更新（API で確認）

## 過去（2026-10-16 15:00 ショート補充）

- 予約済みショート在庫が 10/16 07:00 分で切れていたため、10/17 07:00 JST 分を1本作成
- 素材: 未使用ブロック再生成 work/_unused_1016b.txt（840件）から 4vmH4mejnjI 7755.2-7831.6（映画館で子どもが前の席を蹴って注意された相談。政治なし）
- recipes/shorts/2026-10-17-am.json → build_short.py → `PYTHONPATH=. .venv/bin/python scripts/publish_shorts.py`
  → **hxzDGMs-aWE**「【ひろゆき】子どもが映画館で前の席を蹴ったら【切り抜き】」76秒、private→2026-10-16T22:00Z（10/17 07:00 JST）
- 問いかけ（テロップ最後3.5秒＋概要欄1行目）:「謝ったらさっさとその場を離れる」この考え方、アリ？ナシ？
- フルで見る: parent=2026-10-16-shikaku → Mw4CM0_gFhw（10/16 18:30 JST 公開）。footer は「長尺の解説動画は概要欄から」（親と題材が違うため本編名を書かない）
- 注意: publish_shorts.py は **PYTHONPATH=. 無しだと** upload_youtube.with_engagement_line の `from scripts.engagement` で ModuleNotFoundError（アップロード前に止まる）。PYTHONPATH=. を付けて実行する

## 過去（2026-10-16 14:13 日次）

- 当日ショート 5UDR-8tVjAE・当日長尺 Mw4CM0_gFhw は既存スキップ
- 翌日長尺 2026-10-17-sake → id0Ju8MPkBU「酒と飲み物の話7連発」18:30 JST（09:30Z）予約
- フルで見る: u_vN9xYpzyI → hZCbbUwQVOI

## 検証済みの事実

- status（2026-10-16 15:00 JST）: Mw4CM0_gFhw private→2026-10-16T09:30Z 9M40S、id0Ju8MPkBU private→2026-10-17T09:30Z、hxzDGMs-aWE private→2026-10-16T22:00Z（処理中）、5UDR-8tVjAE public
- hxzDGMs-aWE: API で channelId=UCqK3KYqEeeJiAWr4nSryJYQ、publishAt 2026-10-16T22:00:00Z、概要欄1行目の問いかけと Mw4CM0_gFhw へのリンクを確認。フレーム抽出（9点＋終盤）で崩れなし（顔が左端に寄る瞬間はあるが切れていない）、末尾は無音区間で切れている
- u_vN9xYpzyI description が hZCbbUwQVOI を指す
- cookie 無し fetch_clips 7区間成功

## 次にやること

1. 10/20 以降の長尺・ショートは未作成（次の日次で作る）。cookie 無し取得が bot 判定で落ちたら最初から PC 取得に切り替える
1b. 10/19 の日次で UlaZRnjIeXA（10/18 ショート）の「フルで見る」を 10/18 長尺 k5hQ5NpJHQU に更新するか確認（work/_update_short_full.py UlaZRnjIeXA k5hQ5NpJHQU）
1c. 夕方 10/19: HNNmVJ2MAls 公開後に engage・Studio（固定・終了画面）、ショート ERaQcCP2p2I ← k5hQ5NpJHQU の関連動画
2. 夕方: Mw4CM0_gFhw（10/16 18:30 公開）に `engage.py --post Mw4CM0_gFhw` → Studio で固定・終了画面・関連動画（当日ショート 5UDR-8tVjAE ← 当日長尺 Mw4CM0_gFhw）
3. cookie 無し取得が再び落ちる場合のみ cookies.txt を検討

## 触ってはいけないところ

- 「公式」「公認」と書かない（定型の「公式チャンネルではありません」表記は除く）。政治的な話題は落とす
- 切り抜き禁止: exnFXUMMLLI / q0GyNI3X8cg。ゲスト共演回（IXiLxkgHUMM, naVkgtFmRvg, Sq1YChd0RqQ）は使わない
- 予約時刻を過ぎた publishAt を渡さない。15分以上は上げない
- _plan-kenko / _plan-kosodate / _plan-kigyo は使わない。note は clips[].note（20文字以上）
- Studio 関連動画は朝ルーチンで触らない
- 問いかけ・返信: 攻撃・政治・「公式/公認」・本人なりすまし・自作自演（いいね/登録/別アカウント）・報酬付き依頼は禁止。公開済み動画の概要欄は改変しない（予約済み分のみ可）
