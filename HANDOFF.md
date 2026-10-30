# HANDOFF
最終更新: 2026-10-30 15:15 JST（10/30 日次: 11/2 長尺 5jxVZtOwSnI・10/31 ショート 1aeL1jDjL4o）

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

## 今回やったこと（2026-10-30 14:20 日次）— 完了

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

## 次にやること

1. 10/31 の日次: 当日ショート 1aeL1jDjL4o はスキップ。前日ショート CMkawWTnuxo のフルで見るは As5R0jCxHoM 済み。11/1 のショートを作る（長尺は作らない。11/2 長尺 5jxVZtOwSnI は予約済み、次の長尺枠は 11/4（水））
2. 夕方 10/30: 関連動画 CMkawWTnuxo→As5R0jCxHoM、昇格元 oUt6kcCwW5c の関連動画も As5R0jCxHoM。As5R0jCxHoM の固定コメント・終了画面
3. 昇格判定: CfPbeHlWoP8（10/28）・OZnlwCiAMEA（10/29）・CMkawWTnuxo（10/30）が48時間を過ぎたら 1,700 回超か見る
4. 不要な private 動画 QN24TFpO6jk（10/31 ショートの旧版）の削除はユーザー確認後

## 前回やったこと（2026-10-29 14:15 日次）— 完了

- 昇格: oUt6kcCwW5c（1,900回）→ 10/30 長尺 As5R0jCxHoM（recipes/2026-10-30-tsumerare.json、3問深掘り 7:01）。台帳記録済み
- 10/30 ショート CMkawWTnuxo（recipes/shorts/2026-10-30-am.json、NISA・36秒）

## 検証済みの事実

- status（2026-10-16 15:00 JST）: Mw4CM0_gFhw private→2026-10-16T09:30Z 9M40S、id0Ju8MPkBU private→2026-10-17T09:30Z、hxzDGMs-aWE private→2026-10-16T22:00Z（処理中）、5UDR-8tVjAE public
- hxzDGMs-aWE: API で channelId=UCqK3KYqEeeJiAWr4nSryJYQ、publishAt 2026-10-16T22:00:00Z、概要欄1行目の問いかけと Mw4CM0_gFhw へのリンクを確認。フレーム抽出（9点＋終盤）で崩れなし（顔が左端に寄る瞬間はあるが切れていない）、末尾は無音区間で切れている
- u_vN9xYpzyI description が hZCbbUwQVOI を指す
- cookie 無し fetch_clips 7区間成功
