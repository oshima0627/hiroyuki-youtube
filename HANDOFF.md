# HANDOFF
最終更新: 2026-11-04 14:40 JST（11/4 日次: 11/5 ショート 93NkdAOx0uo・11/6 長尺 kdcGL3JwZSM（qY_hj45hxC0 の昇格））

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
5. ボックスで `build_episode.py` → `thumbnail.py` →（**実験B 以降はレシピに `"opening": "cold"` を入れて冒頭カードなし。--concat-only は不要**）→ `upload_youtube.py work/<id> --schedule <UTC>`。
6. `ops_youtube.py --status` で private→publishAt を確認。サムネは `set_thumbnails.py --only <id>`（必要なら `--force`）。

## 前々回（2026-10-30 14:20 日次）— 完了

- git pull（318611f で最新）。.venv・VOICEVOX 0.25.2 は生きていた
- status（14:21 JST）: 当日ショート CMkawWTnuxo（07:00 公開済）・当日長尺 As5R0jCxHoM（private→10/30 18:30）は既存。10/31 ショート・11/2 長尺は 0 本だった
- 昇格判定: 48時間以上たったショートで 1,700 回超は oUt6kcCwW5c（昇格済）だけ。CfPbeHlWoP8 は 1,468 回で対象外 → **昇格なし**
- フルで見る（API で確認）: CMkawWTnuxo rpJy_1MYcHg→**As5R0jCxHoM**、OZnlwCiAMEA MT7ArIklAm4→**rpJy_1MYcHg**
- 未使用ブロック一覧 work/_unused_1030.txt（721件、work/_unused_1030.py）
- 取得: box の cookie 無し fetch_clips.py で長尺4区間＋ショート1区間すべて成功（VYJ-zTB8TVY は元が 720p）
- 11/2（月）長尺 recipes/2026-11-02-tenshoku-handan.json → **5jxVZtOwSnI**「【ひろゆき】転職した方がいい人、しない方がいい人。公務員から民間はやめた方がいい？」7:12、private→2026-11-02T09:30Z。
  新ルール：3問の深掘り（答えが「転職するな／しろ／今のままで」に分かれた理由を解説板9枚＋まとめで整理）。冒頭は冒頭カード→結論の一言（skPyrH0WTzY 4006.3〜4011.0「国家公務員転職しない方がいいと思いますよ」）→予告板。
  素材 skPyrH0WTzY 3978.4〜4091.9 / VYJ-zTB8TVY 7886.5〜7948.0 / 0ojMhUyiHB4 6192.4〜6226.5。*_4006-4011 は *_4004-4009 から ffmpeg -ss 1.9 で作った。thumb.at 225（VYJ の正面顔、105/86 は顔が切れた）。サムネ maxres あり（upload 時に設定）。概要欄1行目の問いかけを API 確認。終盤に問いかけボード＋outro 20秒
- 10/31 ショート recipes/shorts/2026-10-31-am.json → **1aeL1jDjL4o**「【ひろゆき】転職で年収が上がってもボーナス頼みは危ない？中小企業に移る前の注意点【切り抜き】」35.2秒（O0YEy2NB3os 1266.2〜1301.4、「大丈夫じゃないですね」から開始、質問はスパチャカードとフック）、private→2026-10-30T22:00Z。フルで見る→As5R0jCxHoM。仕事・お金の検索語回。概要欄に「給料やボーナスの扱いは会社の規定や雇用契約で違う」注記を API で追加
- **ショートの切り出しやり直し**: 最初に上げた QN24TFpO6jk は自動クロップが狭く（ひろゆきが左右に大きく動く回）顔が外れる場面があったので、build_short.py に `short.crop=[x0,y0,side]` と `short.cover` の手動指定を追加し [553,0,815]・cover 0 で作り直して 1aeL1jDjL4o として上げ直した。**QN24TFpO6jk は予約を外して private のまま残っている（削除は未実施・要ユーザー判断）**
- pytest 36 passed

## 今回やったこと（2026-11-04 14:17 日次）— 完了

- git pull（436f7bc で最新）。status: 11/4 ショート 2lmeaIMPp-c 公開済、11/4 長尺 m4R7_9CT_o4（private→11/4 18:30）。11/5 ショート・11/6 長尺は 0 本だった
- **昇格**: qY_hj45hxC0（11/2 07:00 公開・2,253回）→ 11/6 長尺。ledger の昇格の記録に追記。qY_hj45hxC0 のフルで見るを API で 5jxVZtOwSnI→kdcGL3JwZSM に変更・確認（11/6 18:30 までは非公開動画へのリンク）。recipes/shorts/2026-11-02-am.json の parent も変更
- 11/6（金）長尺 recipes/2026-11-06-gakureki.json → **kdcGL3JwZSM**「【ひろゆき】学歴で年収は決まる？20代でお金を使うなら学歴よりスキルと経験」6:40、private→2026-11-06T09:30Z、サムネ API 設定成功。Fydc3YFumow 4961.8〜4970.3（cold open）/4901.1〜4961.5/4952.3〜5014.0/5051.2〜5081.3。5015〜5050 の「頭の悪い方には申し訳ない」以降は人を下げる言い方なので使わなかった
- 11/5 ショート recipes/shorts/2026-11-05-am.json → **93NkdAOx0uo**「【ひろゆき】注意しても止めないなら叩いていい？「相手のため」でも体罰が許されない理由【切り抜き】」37秒（0YyAgmv5_Yc 7895.2〜7931.95）、private→2026-11-04T22:00Z、フルで見る→m4R7_9CT_o4（API 確認）。今週はお金系が3本続いたので非お金。crop [640,0,800]（自動は顔が切れた。下端にスパチャカードの上端が細く入る）
- 実験B: 0秒目の音声を faster-whisper（/workspace/wvenv、small/large-v3）で書き起こしてテロップと照合。ショートのテロップは聞き取りが割れた動詞を避け「体罰というのが許されるという社会で…」
- publish_shorts.py: upload_youtube.py を呼ぶとき PYTHONPATH に ROOT を渡すよう修正（PYTHONPATH 無しで成功を確認）
- fetch_clips は --browser none で成功。json3 字幕 0YyAgmv5_Yc / Fydc3YFumow を work/_cap に追加
- pytest 36 passed

## 前回やったこと（2026-11-02 14:22 日次）— 完了

- git pull（最新）。status: 当日ショート qY_hj45hxC0（07:00 公開済・1,239回）、当日長尺 5jxVZtOwSnI（private→11/2 18:30）はスキップ。11/3 ショート・11/4 長尺は 0 本だった
- 昇格判定: 48時間以上で 1,700 回超は oUt6kcCwW5c（1,975回・昇格済）だけ → **昇格なし**。次点 CfPbeHlWoP8 1,468、wbLkK40nUXw 1,334、CMkawWTnuxo 1,325、1aeL1jDjL4o 1,301
- お金・住まいの未使用素材が減っていたので新しい配信 4本（2zED6c6zgx4, pUsi5NQQgrA, 0YyAgmv5_Yc, EXUXJaPlKmE）を fetch_source --subs-only / fetch_topics --save / probe_signals --no-audio で取り込み。R9fFru7ST-o（新党の話・共演者あり）も取り込んだが政治なので使わない。未使用一覧 work/_unused_1102.txt（1,119件）
- 語単位の時刻は yt-dlp の json3 自動字幕（work/_cap/*.ja.json3、work/_words.py）が音声とよく合う。切れ目は ffmpeg の音量包絡で決めた
- **実験B（冒頭のインパクト）を開始**。適用ログは docs/growth-ledger.md「実験B 適用ログ」
  - build_episode.py: レシピの `"opening": "cold"` で冒頭カード（サムネ静止画）を入れず 0 秒目から本編。問いかけ帯（head_question.png）は最初の解説板の最後 4.5 秒（BAND_SEC）にだけ重ねる。帯で解説の最後の行が隠れたので telop.render_note に bottom 引数を追加し、帯を重ねる板は文字を帯より上に収める。outro の thumb_sec は cold のとき 0。dry-run の表示文言「冒頭カードに帯」は直していない（表示だけ）
- 11/3 ショート recipes/shorts/2026-11-03-am.json → **QC24A3gd2jc**「【ひろゆき】住むマンションに資産性はある？「資産になるから買う」が間違いな理由【切り抜き】」42秒、private→2026-11-02T22:00Z。2zED6c6zgx4 3108.55〜3150.45（0秒目「まず資産性というのは間違いです」＝3108.6秒、「下がるわけですよね」まで）。住まい・お金の検索語回（今週2本目）。crop [585,0,830]・cover 160（自動は顔が切れた）。フルで見る→5jxVZtOwSnI。概要欄に「買うか借りるかは人それぞれ、特定の物件の購入を勧めたり否定したりしない」注記を API で追加・確認
- 11/4（水）長尺 recipes/2026-11-04-hachijikan.json → **m4R7_9CT_o4**「【ひろゆき】1日8時間労働は無理ゲー？会社員と個人事業主、向いている人の違い」8:24、private→2026-11-04T09:30Z。EXUXJaPlKmE の1相談を深掘り（8021.8〜8318.6 を4区間）。0秒目は「会社員の上に経営者っていう…ランクアップがあるって誤解してるって人が多い…」（8180.5〜8195.1）、次の解説板で答えの予告＋問いかけ帯、終盤に問いかけボード＋outro 20秒。thumb.at 13・crop [0.45,0.135,0.8]（自動は顔が下向き・テロップが写った）。サムネ maxres あり（upload 時に設定）。概要欄1行目の問いかけを API 確認
- pytest 36 passed

## 前回やったこと（2026-11-01 14:17 日次）— 完了

- git pull（c53e09e で最新）。status: 当日ショート VDVWT-rGlgc（07:00 公開済・フルで見る→As5R0jCxHoM を API で確認）、11/2 長尺 5jxVZtOwSnI（private→11/2 18:30）。11/2 ショートは 0 本だった
- 長尺は作らない（日曜。11/2 は予約済み、次の枠 11/4（水）は 11/2 か 11/3 の日次で作る）
- 昇格判定: 48時間以上たったショートで 1,700 回超は oUt6kcCwW5c（1,967回・昇格済）だけ → **昇格なし**。次点 CfPbeHlWoP8 1,469回、wbLkK40nUXw 1,333回、CMkawWTnuxo 1,323回
- 11/2 ショート recipes/shorts/2026-11-02-am.json → **qY_hj45hxC0**「【ひろゆき】学歴で年収は決まる？東大・早慶卒でも年収400万円が珍しくない理由【切り抜き】」38秒（Fydc3YFumow 4953.4〜4990.65、「で、この年収300万から1500万コースっていうのが昔は学歴に比例してた」から「いい給料をもらえる人が多いは多いんですよ」まで）、private→2026-11-01T22:00Z。仕事・お金（学歴×年収）の検索語回。フルで見る→5jxVZtOwSnI（11/2 長尺）。crop [600,10,790]・cover 0（自動クロップ 570 は左右に動く顔が切れた）。work/shorts/2026-11-02-am/chk/dense.png で1秒ごとに顔が収まっているのを確認。概要欄に「年収は業界・職種・地域で違う、特定の大学や進路を否定・推奨しない」注記を API で追加
- 素材は box の cookie 無し fetch_clips.py で取得。未使用一覧 work/_unused_1101.txt（715件）
- pytest 36 passed

## 前回やったこと（2026-10-31 14:20 日次）— 完了

- git pull（7294323 で最新）。status: 当日ショート 1aeL1jDjL4o（07:00 公開済・フルで見る→As5R0jCxHoM 確認）、11/2 長尺 5jxVZtOwSnI（private→11/2 18:30）。11/1 ショートは 0 本だった
- 長尺は作らない（土曜。次の枠 11/2 は予約済み、その次は 11/4（水））
- 昇格判定: 48時間以上たったショートで 1,700 回超は oUt6kcCwW5c（昇格済）だけ → **昇格なし**。CMkawWTnuxo（10/30・1,320回）は 11/1 07:00 で48時間
- 11/1 ショート recipes/shorts/2026-11-01-am.json → **VDVWT-rGlgc**「【ひろゆき】年収1億円でも家賃は20万円でいい？高い家賃が危ない理由【切り抜き】」37秒（jHWUy2IiZvs 5568.8〜5605.35、「で、これが年収1億円なんだから家賃も200万円…」から「4000万円ぐらい手に残る」まで）、private→2026-10-31T22:00Z。住まい・お金の検索語回。フルで見る→As5R0jCxHoM（前日10/31の長尺なし→直近公開の長尺）。crop [600,10,790]・cover 0（自動クロップは顔が下に寄って切れた）。概要欄に「家賃や住まいの目安は人それぞれ」注記を API で追加
- 素材は box の cookie 無し fetch_clips.py で取得

## 次にやること

1. 11/5（木）の日次: 長尺の枠なし（11/6 は kdcGL3JwZSM 予約済み、次は 11/9（月））。11/6 ショートを作る（フルで見る→m4R7_9CT_o4）。実験B 継続
   夕方 11/4: 2lmeaIMPp-c の関連動画→m4R7_9CT_o4、m4R7_9CT_o4 の固定コメント・終了画面。夕方 11/5: 93NkdAOx0uo の関連動画→m4R7_9CT_o4。夕方 11/6: qY_hj45hxC0 の関連動画→kdcGL3JwZSM、kdcGL3JwZSM の固定コメント・終了画面
2. 昇格判定: QC24A3gd2jc（11/3）・2lmeaIMPp-c（11/4）が48時間を過ぎたら 1,700 回超か見る
3. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
4. 11/11 比較、11/16 15:00 実験B 比較 routine

## 前回やったこと（2026-10-29 14:15 日次）— 完了

- 昇格: oUt6kcCwW5c（1,900回）→ 10/30 長尺 As5R0jCxHoM（recipes/2026-10-30-tsumerare.json、3問深掘り 7:01）。台帳記録済み
- 10/30 ショート CMkawWTnuxo（recipes/shorts/2026-10-30-am.json、NISA・36秒）

## 検証済みの事実

- status（2026-10-16 15:00 JST）: Mw4CM0_gFhw private→2026-10-16T09:30Z 9M40S、id0Ju8MPkBU private→2026-10-17T09:30Z、hxzDGMs-aWE private→2026-10-16T22:00Z（処理中）、5UDR-8tVjAE public
- hxzDGMs-aWE: API で channelId=UCqK3KYqEeeJiAWr4nSryJYQ、publishAt 2026-10-16T22:00:00Z、概要欄1行目の問いかけと Mw4CM0_gFhw へのリンクを確認。フレーム抽出（9点＋終盤）で崩れなし（顔が左端に寄る瞬間はあるが切れていない）、末尾は無音区間で切れている
- u_vN9xYpzyI description が hZCbbUwQVOI を指す
- cookie 無し fetch_clips 7区間成功
