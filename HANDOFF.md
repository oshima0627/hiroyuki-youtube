# HANDOFF
最終更新: 2026-10-20 15:00 JST（10/20 14:13 日次: 素材を PC で取得 → box でビルド・予約まで完了）

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

## 今回やったこと（2026-10-20 14:13 日次）— 素材は PC 取得で補完して完了

- status（14:22 JST）: 当日ショート -MKj2GDwPzQ（07:00 公開済・フルで見る→HNNmVJ2MAls を API で確認）、当日長尺 aM46O8fw5JU
  （private→2026-10-20T09:30Z = 10/20 18:30 JST、14:10）は既存でスキップ。10/21 分は長尺・ショートとも 0 本だった
- フルで見る: ERaQcCP2p2I（10/19 ショート）を k5hQ5NpJHQU → HNNmVJ2MAls（10/19 長尺）に更新（work/_update_short_full.py、API で AFTER 確認）
- 取得: 14:25〜14:29 JST、cookie 無しの box fetch で Fydc3YFumow / VYJ-zTB8TVY / 4vmH4mejnjI / O0YEy2NB3os の
  すべてが「Sign in to confirm you’re not a bot」。player_client=tv / tv_simply / mweb・web_safari も不可
  → PC（ASUS_i9）で fetch_clips.py（Firefox cookie）→ 8ファイルを CopyToBox で work/clips へ（14:40）。
  ffprobe で全て h264+aac・長さ正常を確認（VYJ-zTB8TVY の4区間は 1280x720、他は 1920x1080）。
  PC のローカルリポジトリには git pull のローカル merge commit があるが push しない（PC からは push しない）
- 翌日長尺 recipes/2026-10-21-machi.json → **fDO58HAngXo**「【ひろゆき】街の話7連発。エリートが街を作ると個性が消えます」14:25（PT14M25S）、
  private→2026-10-21T09:30Z（10/21 18:30 JST）。thumb.at 60 → 55（60 は手で顔が隠れ目を閉じていた。55 はカメラ目線）。
  set_thumbnails.py --only 2026-10-21-machi --force で平均差分 0.8 を確認。終了ボード 20 秒・冒頭カードと終盤に問いかけ＋CTA。
  概要欄1行目「「再開発で街はつまらなくなる」この考え方、アリ？ナシ？ あなたの反論をコメントで👇」を API で確認。
  お台場の回は東京都知事批判（Fydc3YFumow 962 以降）を政治寄りとして切った。秋葉原の回はメイドカフェ違法の断定（7523 以降）の手前で切った
- 翌日ショート recipes/shorts/2026-10-21-am.json → **wb3NmCaYikw**「【ひろゆき】運動会の徒競走で1位を取る裏ワザ【切り抜き】」70秒、
  private→2026-10-20T22:00Z（10/21 07:00 JST）。フルで見る→aM46O8fw5JU（parent 2026-10-20-uchu、API で確認）。
  問いかけ「「1位を取るより自分の能力を上げる方が大事」この考え方、アリ？ナシ？」、終盤に CTA テロップ。
  冒頭1秒あたりは顔が左下に寄る（build_short の自動クロップのまま）
- scripts/fetch_clips.py: ショート単体レシピ（clip キー）も1区間として拾うよう修正（一時レシピ不要に）。pytest 36 passed
- 未使用ブロック一覧は work/_unused_1020.txt（811件）

## 前回やったこと（2026-10-19 14:13 日次）

- 当日ショート ERaQcCP2p2I（07:00 公開済）・当日長尺 HNNmVJ2MAls（18:30 予約済）は既存でスキップ
- フルで見る: UlaZRnjIeXA（10/18 ショート）を id0Ju8MPkBU → k5hQ5NpJHQU（10/18 長尺）に更新（API で確認）
- 取得: cookie 無しの box fetch で 0ojMhUyiHB4 5区間と O0YEy2NB3os 1区間は成功、M7KWrHANxHs 4665-4846 / skPyrH0WTzY 5617-5658 は
  bot 判定で失敗 → PC（ASUS_i9）で work/tmp-1020-pc.json を fetch（Firefox cookie）→ CopyToBox
- 翌日長尺 recipes/2026-10-20-uchu.json → **aM46O8fw5JU**「宇宙とAIの話7連発。宇宙人が見つからないのは文明が自滅したからかも」14:10、
  private→2026-10-20T09:30Z（10/20 18:30 JST）。thumb.at=60（ピースのカット）、thumbnail_set true。
  問いかけ「「AIに禁止ルールは教え込めない」この考え方、アリ？ナシ？」。武漢の研究所の話（0ojMhUyiHB4 4333以降）は政治寄りなので切った
- 翌日ショート recipes/shorts/2026-10-20-am.json → **-MKj2GDwPzQ**「かまってちゃんの夫にもう疲れたら」67秒、private→2026-10-19T22:00Z（10/20 07:00 JST）。
  フルで見る→HNNmVJ2MAls（parent 2026-10-19-suimin）。問いかけ「「夫を説得せず自分の悩みとして相談に誘う」この考え方、アリ？ナシ？」
  冒頭の相談読み上げ中はうつむくので顔が下に切れる（元配信のカードの位置で直せない）
- 未使用ブロック一覧は work/_unused_1019.txt

## 過去（2026-10-18 14:13 日次 → 途中停止 → 19:00 に再開して完了）

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

## 過去（2026-10-17 14:13 日次）

- 当日ショート hxzDGMs-aWE（07:00 公開済）・当日長尺 id0Ju8MPkBU（18:30 予約済）は既存でスキップ
- 翌日長尺 recipes/2026-10-18-mitame.json → **k5hQ5NpJHQU**「見た目とブランドの話7連発。ジム通いはブランド消費です」11:20、private→2026-10-18T09:30Z（10/18 18:30 JST）、サムネ API 設定済み。未使用ブロック一覧は work/_unused_1017.txt
- 翌日ショート recipes/shorts/2026-10-18-am.json → **UlaZRnjIeXA**「結露の壁紙で16万円請求されたら」65秒、private→2026-10-17T22:00Z（10/18 07:00 JST）。フルで見る→id0Ju8MPkBU（parent 2026-10-17-sake）
  - ショート単体レシピは fetch_clips.py が拾わない（0区間）。clips:[clip] の一時レシピを作って fetch した
- フルで見る: 5UDR-8tVjAE → Mw4CM0_gFhw に更新（API で確認）

- ショート単体の publish_shorts.py は **PYTHONPATH=. 必須**（無いと upload_youtube.with_engagement_line の import で止まる）

## 検証済みの事実

- status（2026-10-16 15:00 JST）: Mw4CM0_gFhw private→2026-10-16T09:30Z 9M40S、id0Ju8MPkBU private→2026-10-17T09:30Z、hxzDGMs-aWE private→2026-10-16T22:00Z（処理中）、5UDR-8tVjAE public
- hxzDGMs-aWE: API で channelId=UCqK3KYqEeeJiAWr4nSryJYQ、publishAt 2026-10-16T22:00:00Z、概要欄1行目の問いかけと Mw4CM0_gFhw へのリンクを確認。フレーム抽出（9点＋終盤）で崩れなし（顔が左端に寄る瞬間はあるが切れていない）、末尾は無音区間で切れている
- u_vN9xYpzyI description が hZCbbUwQVOI を指す
- cookie 無し fetch_clips 7区間成功

## 次にやること

1. 10/21 の日次で -MKj2GDwPzQ（10/20 ショート）の「フルで見る」を 10/20 長尺 aM46O8fw5JU に更新（work/_update_short_full.py -MKj2GDwPzQ aM46O8fw5JU）
1b. 夕方 10/20: aM46O8fw5JU 公開後に engage・Studio（固定・終了画面）、当日ショート -MKj2GDwPzQ ← aM46O8fw5JU の関連動画
1c. 10/18・10/19 の Studio 作業は box Chrome の Google ログイン切れで未実施のまま（ユーザーの再ログイン待ち）
1d. 夕方 10/21: fDO58HAngXo 公開後に engage・Studio（固定・終了画面）、当日ショート wb3NmCaYikw ← fDO58HAngXo の関連動画
2. box の cookie 無し取得は 10/20 に全動画で bot 判定（PC 取得で補完）。続くようなら cookies.txt（ユーザー判断）か PC 取得を常用にする

## 触ってはいけないところ

- 「公式」「公認」と書かない（定型の「公式チャンネルではありません」表記は除く）。政治的な話題は落とす
- 切り抜き禁止: exnFXUMMLLI / q0GyNI3X8cg。ゲスト共演回（IXiLxkgHUMM, naVkgtFmRvg, Sq1YChd0RqQ）は使わない
- 予約時刻を過ぎた publishAt を渡さない。15分以上は上げない
- _plan-kenko / _plan-kosodate / _plan-kigyo は使わない。note は clips[].note（20文字以上）
- Studio 関連動画は朝ルーチンで触らない
- 問いかけ・返信: 攻撃・政治・「公式/公認」・本人なりすまし・自作自演（いいね/登録/別アカウント）・報酬付き依頼は禁止。公開済み動画の概要欄は改変しない（予約済み分のみ可）
