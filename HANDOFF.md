# HANDOFF
最終更新: 2026-10-25 14:50 JST（10/25 14:18 日次: box の cookie 無し取得が全8区間成功 → box だけでビルド・予約まで完了）

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

## 今回やったこと（2026-10-25 14:18 日次）— 完了

- .venv が壊れていた（bin に Activate.ps1 だけ）ので作り直した（requirements.txt、pytest 36 passed）。VOICEVOX 0.25.2 は起動済みだった
- status（14:19 JST）: 当日ショート wbLkK40nUXw（07:00 公開済）・当日長尺 WaXp52ksF50（private→2026-10-25T09:30Z、14:01）は既存でスキップ。10/26 分は 0 本だった
- フルで見る: ravNhkw0Wu4（10/24 ショート）を rhXUqMbHxMk → k9vGnOkWgG4（10/24 長尺）に更新（work/_update_short_full.py、API で再取得して確認）。wbLkK40nUXw は k9vGnOkWgG4 のまま（慣例どおり）
- 取得: **box の cookie 無し fetch_clips.py が長尺7区間＋ショート1区間すべて成功**（14:21〜14:27 JST、PC 不要）。h264+aac（_o8W_QKNHEo と VYJ-zTB8TVY は 1280x720、他 1920x1080）
- 翌日長尺 recipes/2026-10-26-fuufu.json（新テーマ: 結婚と夫婦）→ **QN45yEvHd8s**「【ひろゆき】結婚と夫婦の話7連発。好きな人と結婚するべきというルールが良くないんです」10:07（PT10M8S）、
  private→2026-10-26T09:30Z（10/26 18:30 JST）。thumb.at 60（後ろ向き）→ 330（自分の時間が欲しい妻の回の正面カット）、upload 時に thumbnail_set true。
  問いかけ「「結婚相手は大好きな人じゃなくてもいい」この考え方、アリ？ナシ？」を概要欄1行目で API 確認。冒頭カードと終盤20秒の問いかけボードあり。
  恋愛結婚至上主義の回（O0YEy2NB3os）は相談者の病名部分（3925〜3948）を外して 3948.9 から。直後の元首相事件の話（4017 以降）は入れていない。
  マチアプ33歳の回（0ojMhUyiHB4 6851〜）と「メンヘラと結婚」の回（jHWUy2IiZvs 4400〜）は言い方がきついので使わず
- 翌日ショート recipes/shorts/2026-10-26-am.json → **oUt6kcCwW5c**「【ひろゆき】上司に詰められて辛い…会社を辞めるか迷ったら【切り抜き】」50秒、
  private→2026-10-25T22:00Z（10/26 07:00 JST）。フルで見る→WaXp52ksF50（parent 2026-10-25-eiga、API で確認）。問いかけ「「辞めるなら損をしない辞め方を先に考えるべき」この考え方、アリ？ナシ？」。
  直後の「中道分裂」（4vmH4mejnjI 2559 以降、政治）の手前で切った。顔が左下に寄る（自動クロップのまま）。ショートのサムネは API 未設定（thumbnail_set false、従来どおり）
- 未使用ブロック一覧は work/_unused_1025.txt（764件、10/26 分を足す前）。結婚の残り: _Qc2ZF3MLO0 2771-2816（結婚市場の35歳の壁）、23vSB2fXjc8 9496-9625（妊娠と結婚・割り勘の彼）、daulqJwmooE 11282-11294（年金分割）

## 前回やったこと（2026-10-24 14:25 日次）— 完了

- status（14:25 JST）: 当日ショート ravNhkw0Wu4（07:00 公開済、フルで見る→rhXUqMbHxMk）・当日長尺 k9vGnOkWgG4（private→2026-10-24T09:30Z、13:28）は既存でスキップ。10/25 分は 0 本だった
- フルで見る: Nq-n9B5ROuU は rhXUqMbHxMk を指していて変更なし（API で確認）。ravNhkw0Wu4 も rhXUqMbHxMk のまま（指示どおり触っていない）
- 取得: **box の cookie 無し fetch_clips.py が長尺7区間＋ショート1区間すべて成功**（14:25〜14:34 JST、PC 不要。ASUS_i9 はこの時点でオフライン）。ffprobe で h264+aac（_o8W_QKNHEo の2区間は 1280x720、他 1920x1080）
- 翌日長尺 recipes/2026-10-25-eiga.json（新テーマ: 映画とドラマ）→ **WaXp52ksF50**「【ひろゆき】映画とドラマの話7連発。ガチで面白い作品しか国境を越えてきません」14:00（ffprobe 840.99秒）、
  private→2026-10-25T09:30Z（10/25 18:30 JST）。thumb.at 60（720p でブレ）→ 150（jHWU の笑顔のカット）、upload 時に thumbnail_set true。問いかけ「「外国の映画やドラマの方が当たりが多い」この考え方、アリ？ナシ？」を概要欄1行目で API 確認。
  ガンダムの回（_o8W_QKNHEo 1656-1850）はイスラエル・イランの戦争に触れるので使わず、ペーパーハウスの回は玉木氏の話（2003 以降）の手前で切った。透明人間（2030-2112）は下ネタ寄りなので未使用。『爆弾』の回は VPN の話（6930 以降）の手前で切った
- 翌日ショート recipes/shorts/2026-10-25-am.json → **wbLkK40nUXw**「【ひろゆき】好きな人に仕事メールで「この映画見た？」と聞かれたら【切り抜き】」84秒（競合22〜73秒より長いという警告のみ）、
  private→2026-10-24T22:00Z（10/25 07:00 JST）。フルで見る→k9vGnOkWgG4（parent 2026-10-24-warai、API で確認）。hook「映画の話は脈あり？」（「」や？の途中で折り返すと崩れるので短くした）。問いかけ「「興味があると言うなら少しは調べてから言うべき」この考え方、アリ？ナシ？」。顔が左下に寄る（自動クロップのまま）
- 未使用ブロック一覧は work/_unused_1024.txt（773件、10/25 分を足す前）。映画の残り: jHWUy2IiZvs 1036-1115（ハンターハンター新刊を忘れる）、jHWUy2IiZvs 5065-5267（映画で各国の常識が分かる）、skPyrH0WTzY 3898-3950（日本映画は過去の人気作頼み）

## 過去（2026-10-23 14:19 日次）— 完了

- status（14:20 JST）: 当日ショート Nq-n9B5ROuU（07:00 公開済）・当日長尺 rhXUqMbHxMk（private→2026-10-23T09:30Z、11:06）は既存でスキップ。10/24 分は 0 本だった
- フルで見る: uc6LY1dluHo は RNDHtUShK58 を指していて変更なし。Nq-n9B5ROuU を RNDHtUShK58 → rhXUqMbHxMk（当日長尺、18:30 公開までは非公開リンク）に更新（work/_update_short_full.py、API で AFTER 確認）
- 取得: box の cookie 無し fetch は約4分で1区間も完了せず（.part が増えない）→ 停止して PC（ASUS_i9）で work/tmp-1024-pc.json（長尺7区間＋ショート1区間）を fetch（Firefox cookie、約9分）→ tar で CopyToBox。ffprobe で h264+aac（_o8W_QKNHEo と VYJ-zTB8TVY は 1280x720、他 1920x1080）
- 翌日長尺 recipes/2026-10-24-warai.json（新テーマ: 笑いとトーク）→ **k9vGnOkWgG4**「【ひろゆき】笑いとトークの話7連発。面白い人はみんな性格が悪いです」13:27（PT13M28S）、
  private→2026-10-24T09:30Z（10/24 18:30 JST）。thumb.at 60（笑顔）、upload 時に thumbnail_set true。問いかけ「「面白い人はみんな性格が悪い」この考え方、アリ？ナシ？」を概要欄1行目で API 確認。
  性格の回（skPyrH0WTzY 6401-6542）は芸人個人名を挙げて性格が悪いと言う部分（6543 以降）の手前で切った。タモリさんの回は「放送できないこと」（_o8W_QKNHEo 5737 以降）の手前で切った
- 翌日ショート recipes/shorts/2026-10-24-am.json → **ravNhkw0Wu4**「【ひろゆき】「あの人は腹黒い」と言う人の正体【切り抜き】」42秒、
  private→2026-10-23T22:00Z（10/24 07:00 JST）。フルで見る→rhXUqMbHxMk（parent 2026-10-23-kokoro、API で確認）。問いかけ「「証拠のない悪口は相手にするだけ時間の無駄」この考え方、アリ？ナシ？」。冒頭は顔が左下に寄る（自動クロップのまま）
- 未使用ブロック一覧は work/_unused_1023.txt（781件、10/24 分を足す前）。笑いの残り: daulqJwmooE 568-673（水曜日のダウンタウン未放送回）、_o8W_QKNHEo 5551-5596（気まずい相手との生放送）

## 過去（2026-10-21 14:17 日次）— 完了

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

## 検証済みの事実

- status（2026-10-16 15:00 JST）: Mw4CM0_gFhw private→2026-10-16T09:30Z 9M40S、id0Ju8MPkBU private→2026-10-17T09:30Z、hxzDGMs-aWE private→2026-10-16T22:00Z（処理中）、5UDR-8tVjAE public
- hxzDGMs-aWE: API で channelId=UCqK3KYqEeeJiAWr4nSryJYQ、publishAt 2026-10-16T22:00:00Z、概要欄1行目の問いかけと Mw4CM0_gFhw へのリンクを確認。フレーム抽出（9点＋終盤）で崩れなし（顔が左端に寄る瞬間はあるが切れていない）、末尾は無音区間で切れている
- u_vN9xYpzyI description が hZCbbUwQVOI を指す
- cookie 無し fetch_clips 7区間成功

## 次にやること

1. 10/26 の日次: 当日ショート oUt6kcCwW5c（07:00）・当日長尺 QN45yEvHd8s（18:30）は確認してスキップ。前日ショート wbLkK40nUXw のフルで見るを前日長尺 WaXp52ksF50 に更新するか確認。10/27 分の長尺・ショートを作る
   `.venv/bin/python work/_update_short_full.py <short_id> <long_id>`
2. 夕方 10/25: WaXp52ksF50 公開後に engage（問いかけコメント・返信）、Studio の関連動画・固定・終了画面
3. box の cookie 無し取得は 10/22・10/23 は不可、10/24・10/25 は全区間成功と日によって違う。box で数分試して進まなければ PC 取得に切り替える
4. box の .venv はたびたび壊れる/消える。import できなければ `rm -rf .venv && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt`

## 触ってはいけないところ

- 「公式」「公認」と書かない（定型の「公式チャンネルではありません」表記は除く）。政治的な話題は落とす
- 切り抜き禁止: exnFXUMMLLI / q0GyNI3X8cg。ゲスト共演回（IXiLxkgHUMM, naVkgtFmRvg, Sq1YChd0RqQ）は使わない
- 予約時刻を過ぎた publishAt を渡さない。15分以上は上げない
- _plan-kenko / _plan-kosodate / _plan-kigyo は使わない。note は clips[].note（20文字以上）
- Studio 関連動画は朝ルーチンで触らない
- 問いかけ・返信: 攻撃・政治・「公式/公認」・本人なりすまし・自作自演（いいね/登録/別アカウント）・報酬付き依頼は禁止。公開済み動画の概要欄は改変しない（予約済み分のみ可）
