# HANDOFF
最終更新: 2026-11-22 14:55 JST（11/22 日次）

## ▶ 最初に実行するコマンド（Linux ボックス）

```bash
cd /workspace/hiroyuki-youtube && PYTHONPATH=. python3 scripts/ops_youtube.py --status
curl -s 127.0.0.1:50021/version   # VOICEVOX（/workspace/voicevox）。返らなければ起動する（話者13）
```

`.venv` は無い。`yt_dlp` は `/workspace/.ytvenv/bin/python` で `fetch_clips.py` を回す（`sys.executable -m yt_dlp` のため）。faster-whisper は `/workspace/wvenv`（wav を numpy で渡す。small で十分。work/tmp1108/ww.py に単語タイムスタンプ版あり）。

## いま何をしているのか

ひろゆき切り抜きチャンネル「ひろゆき解説ch【切り抜き】」(UCqK3KYqEeeJiAWr4nSryJYQ) の日次運用。Linux ボックス（/workspace/hiroyuki-youtube）で回す。ASUS_i9 は使わない（fetch 失敗時だけ親が判断）。

## Linux ボックスでの手順

1. `work/` は git 管理外。字幕は work/<動画ID>/subs.json（work/_cap/*.ja.json3 は一部のみ）。未使用一覧は `python3 work/_unused_1102.py` → work/_unused_1102.txt
2. レシピを recipes/ に作る。**クリップ取得**: `PYTHONPATH=. /workspace/.ytvenv/bin/python scripts/fetch_clips.py recipes/<id>.json --browser none`
3. ショート: `build_short.py <recipe>` → `publish_shorts.py`（予約まで）。ショートは thumb.png が無いので set_thumbnails 対象外
4. 長尺: `build_episode.py`（`"opening": "cold"`）→ `thumbnail.py`（thumb.at は連結後の秒。note 画面に当たらないよう parts.txt の part_* 区間を選ぶ）→ `upload_youtube.py work/<id> --schedule <UTC>` → `set_thumbnails.py --only <published.jsonのキー> --force`
5. ショートのフルで見る変更: `PYTHONPATH=. python3 work/_update_short_full.py <ショートID> <長尺ID>`

## 今回やったこと（2026-11-22 日次）— 完了

- git pull → status（14:25 JST）: 11/22 07:00 Ke2zw5ZPiA0 公開済。11/23 07:00 のショートは0本だった
- 昇格判定: 48h超で1,700回超の未処理ショートなし（最大は 5RekW-bgrB4 1,349回＝11/22 07:00 で48h到達、OD7nJkdkB0M 1,297回、Ke2zw5ZPiA0・3qdS3FVuX_8 は48h未満）。1,700回超は 93NkdAOx0uo・84oRUIoiUoI・qY_hj45hxC0・oUt6kcCwW5c・653l90JxsV4・XnpPzG1ERco で全て昇格済み。長尺は作らず
- 11/23 ショート recipes/shorts/2026-11-23-am.json → **Jy27D8k9HwE**「【ひろゆき】中学受験で有名校に行けば人生有利？有名高校に行かなかった人も結局いい大学に入る理由【切り抜き】」41.0秒、private→2026-11-22T22:00Z。jPOui7xHeOw クリップ1150〜1250 の 43.98〜84.95秒。C①（子育て・教育観）。フルで見る→wpmnSdP8VNQ。crop [650,30,780]（スパチャカード上端818の上）。概要欄2行目に研究の前提（同じ学力の受験生をくじ引きで分けた研究）を手で補足してからアップ
- docs/growth-ledger.md: 実験B 1行・施策C 1行（C①、新しい週 11/23〜の1本目）
- 題材探し: work/_kw.py "<正規表現>" で字幕を全文検索（使用済み区間は除外）。work/_peek.py <動画ID> <開始> <終了> で字幕を読む。jPOui7xHeOw 1237〜1320 は「私立一貫校に意味があるパターン」の続き（言い方がきついので使うなら要注意）

## 検証済みの事実（API / コマンド出力）

- Jy27D8k9HwE: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-22T22:00:00Z、概要欄1行目は二択の問いかけ、フルで見る→wpmnSdP8VNQ（API で確認。duration は処理中で P0D）
- 出力音声を faster-whisper small で確認: 冒頭「有名高校に行かなかった人たちも結局あの普通の公立高校でもいい大学入るんですよ」、末尾「優秀じゃないやつはどこに行ってもダメだよねっていう話なんですよ」で終わる（41.0秒）。コンタクトシート work/tmp1123/sheet3.jpg

## 未検証

- Jy27D8k9HwE の全編通し視聴はしていない
- pytest は box に pytest が無く未実行

## 次にやること

1. 夕方 11/22: Ke2zw5ZPiA0 関連→wpmnSdP8VNQ・問いかけ固定
2. 夕方 11/23: Jy27D8k9HwE 関連→wpmnSdP8VNQ・問いかけ固定
3. 11/23（月）日次: **11/24 は am（07:00）と pm（18:00）の2本**（施策D、11/23 週次レビューで開始。docs/growth-ledger.md の「施策D」節）。recipes/shorts/2026-11-24-am.json と -pm.json。C①・お金枠は週合計2〜3本ずつのまま、増えた分はそれ以外の題材。作りきれない日は pm を休んで施策D 適用ログに書く（今週 11/23〜 はC①1本済み、お金枠0本）
   - 夕方: pm ショート（18:00公開）の関連動画・問いかけ固定は、公開後に。夕方が18:00前なら翌日の夕方で am と前日 pm の2本をまとめて
4. 昇格判定: 3qdS3FVuX_8（48h は 11/23 07:00）、Ke2zw5ZPiA0（11/24 07:00）、Jy27D8k9HwE（11/25 07:00）。次の昇格長尺枠は 11/25(水)18:30（11/23 枠は今日候補なしで見送り）
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 11/23 09:00 週次レビュー routine: 済み（実験B 続ける・施策D 開始。Studio のインプレッション/CTR/視聴継続も台帳の週次節に追記済み。Studio「過去7日」は 11/15〜11/21 で Analytics と1日ずれる）

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
