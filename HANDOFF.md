# HANDOFF
最終更新: 2026-10-22 15:00 JST（10/22 14:19 日次: box 取得は 429/bot 判定で全滅 → 全9区間 PC 取得 → box でビルド・予約まで完了）

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

## 今回やったこと（2026-10-22 14:19 日次）— 完了

- status（14:20 JST）: 当日ショート uc6LY1dluHo（07:00 公開済）・当日長尺 RNDHtUShK58（private→2026-10-22T09:30Z、14:03）は既存でスキップ。10/23 分は 0 本だった
- フルで見る: wb3NmCaYikw（10/21 ショート）aM46O8fw5JU → fDO58HAngXo（10/21 長尺）。uc6LY1dluHo（10/22 ショート）fDO58HAngXo → RNDHtUShK58（ユーザー指示で当日長尺へ前倒し。18:30 公開までは非公開リンク）。API で AFTER 確認
- 取得: box の cookie 無し yt-dlp は「HTTP 429 Too Many Requests」＋「Sign in to confirm you're not a bot」で全区間不可 → PC（ASUS_i9）で work/tmp-1023-pc.json（長尺8区間＋ショート1区間）を fetch（Firefox cookie、約7分半）→ CopyToBox。ffprobe で h264+aac（VYJ-zTB8TVY は 1280x720、他 1920x1080）
- 翌日長尺 recipes/2026-10-23-kokoro.json → **rhXUqMbHxMk**「【ひろゆき】幸せと心の話8連発。嫌な記憶は飽きるまで思い出すと平気になります」11:05（PT11M6S）、
  private→2026-10-23T09:30Z（10/23 18:30 JST）。thumb.at 60（頭が切れる）→ 110（カメラ向きの笑顔）、thumbnail_set true。問いかけ「「嫌な記憶は忘れるより飽きるまで思い出す」この考え方、アリ？ナシ？」
  M7KWrHANxHs 1092-1146 は「声がいいおじさん」の悪口部分（1147 以降）の手前で切った
- 翌日ショート recipes/shorts/2026-10-23-am.json → **Nq-n9B5ROuU**「【ひろゆき】手編みと偽ってマフラーを贈る人をどう思うか【切り抜き】」52秒、
  private→2026-10-22T22:00Z（10/23 07:00 JST）。フルで見る→RNDHtUShK58（parent 2026-10-22-doubutsu、API で確認）。問いかけ「「嘘で得した経験が嘘つきを作る」この考え方、アリ？ナシ？」
- 未使用ブロック一覧は work/_unused_1022.txt（793件）。心の話の残り: _Qc2ZF3MLO0 1598-1666（怒りの心理・番組評なので未使用）、4vmH4mejnjI 3972-4128（幸福キャラのタレント・個人名と下ネタで未使用）

## 前回やったこと（2026-10-21 14:17 日次）— 完了

- status（14:18 JST）: 当日ショート wb3NmCaYikw（07:00 公開済、フルで見る→aM46O8fw5JU を API で確認）、当日長尺 fDO58HAngXo
  （private→2026-10-21T09:30Z = 10/21 18:30 JST、14:25）は既存でスキップ。10/22 分は長尺・ショートとも 0 本だった
- フルで見る: -MKj2GDwPzQ（10/20 ショート）を HNNmVJ2MAls → aM46O8fw5JU（10/20 長尺）に更新（work/_update_short_full.py、API で AFTER 確認）。
  wb3NmCaYikw は前日長尺 aM46O8fw5JU を指していて慣例どおりなので変更なし（10/22 の日次で fDO58HAngXo に更新する）
- 取得: box の cookie 無し fetch で 2ol7cHkAOMw 2区間・VYJ-zTB8TVY 233-375・jmADUo9Vcho 4890-5002 は成功（14:22〜14:30）。
  skPyrH0WTzY 1359-1444 で5分以上進まず（以前と同じ bot 判定のリトライとみて停止）→ PC（ASUS_i9）で work/tmp-1022-pc.json
  （skPy・c2X5ZUIpRSk 4478-4526・ショート素材 VYJ-zTB8TVY 6540-6599）を fetch（Firefox cookie、2分40秒）→ CopyToBox。ffprobe で全て h264+aac
- 翌日長尺 recipes/2026-10-22-doubutsu.json → **RNDHtUShK58**「【ひろゆき】動物とペットの話6連発。人間は牛に使われているのかもしれません」14:03（PT14M3S）、
  private→2026-10-22T09:30Z（10/22 18:30 JST）。thumb.at 60、thumbnail_set true。問いかけ「「ペットを飼うなら犬税くらい払うべき」この考え方、アリ？ナシ？」。
  犬税の回は自民党総裁選の話（jmADUo9Vcho 5005 以降）の手前で切った。生体販売の回（5016〜5260）はドンキ店舗名と総裁選が絡むので使わず。
  少子化とペットの回は「政治家がやる気がない」（c2X5ZUIpRSk 4552 以降）の手前で切った
- 翌日ショート recipes/shorts/2026-10-22-am.json → **uc6LY1dluHo**「【ひろゆき】向かいの家の犬がほったらかしにされていたら【切り抜き】」59秒、
  private→2026-10-21T22:00Z（10/22 07:00 JST）。フルで見る→fDO58HAngXo（parent 2026-10-21-machi、API で確認）。
  問いかけ「「人に頼まず自分で解決するか諦めるかの2択」この考え方、アリ？ナシ？」。顔が左に寄る瞬間あり（自動クロップのまま）
- 未使用ブロック一覧は work/_unused_1021.txt（797件）。字幕から拾う補助 work/_sub.py <video_id> <start> <end>
- 動物ネタの残り: 2ol7cHkAOMw 1080-1230（山猫も北アフリカDNA）、jmADUo9Vcho 5324-5476（坂上忍さんのレンタル保護犬猫）、
  O0YEy2NB3os 2606-2678（保護猫カフェ）、VYJ-zTB8TVY 5478-5510 / O0YEy2NB3os 6664-6692（34歳の猫）

## 過去（2026-10-20 14:13 日次）— 素材は PC 取得で補完して完了

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

## 過去（2026-10-19 14:13 日次）

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

1. 10/23 の日次: uc6LY1dluHo は既に RNDHtUShK58 を指す（更新不要）。Nq-n9B5ROuU は 10/23 長尺 rhXUqMbHxMk へ 10/24 の日次で更新する慣例
1e. 夕方 10/23: rhXUqMbHxMk 公開後に engage・Studio、当日ショート Nq-n9B5ROuU ← rhXUqMbHxMk の関連動画
1b. 夕方 10/21: fDO58HAngXo 公開後に engage・Studio（固定・終了画面）、当日ショート wb3NmCaYikw ← fDO58HAngXo の関連動画
1c. 10/18〜10/20 の Studio 作業は box Chrome の Google ログイン切れで未実施のまま（ユーザーの再ログイン待ち）
1d. 夕方 10/22: RNDHtUShK58 公開後に engage・Studio、当日ショート uc6LY1dluHo ← RNDHtUShK58 の関連動画
2. box の cookie 無し取得は 10/22 は 429＋bot 判定で全滅。まず box で試し、失敗区間を PC 取得で補完する運用

## 触ってはいけないところ

- 「公式」「公認」と書かない（定型の「公式チャンネルではありません」表記は除く）。政治的な話題は落とす
- 切り抜き禁止: exnFXUMMLLI / q0GyNI3X8cg。ゲスト共演回（IXiLxkgHUMM, naVkgtFmRvg, Sq1YChd0RqQ）は使わない
- 予約時刻を過ぎた publishAt を渡さない。15分以上は上げない
- _plan-kenko / _plan-kosodate / _plan-kigyo は使わない。note は clips[].note（20文字以上）
- Studio 関連動画は朝ルーチンで触らない
- 問いかけ・返信: 攻撃・政治・「公式/公認」・本人なりすまし・自作自演（いいね/登録/別アカウント）・報酬付き依頼は禁止。公開済み動画の概要欄は改変しない（予約済み分のみ可）
