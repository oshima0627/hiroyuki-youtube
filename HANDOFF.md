# HANDOFF
最終更新: 2026-11-24 15:30 JST（11/24 日次）

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

## 今回やったこと（2026-11-24 日次）— 完了

- git pull → status（14:20 JST）: 11/24 07:00 adtWAjiQlnQ 公開済、11/24 18:00 gkdeigFmqug は private→2026-11-24T09:00Z で予約済を確認。11/25 の am/pm は0本だった。直近の長尺は wpmnSdP8VNQ（11/18）
- 昇格判定: 48h超で1,700回超の未昇格ショートなし。48h超の未昇格で最大は CfPbeHlWoP8 1,470回、直近週では Ke2zw5ZPiA0 1,378回・5RekW-bgrB4 1,344回（Jy27D8k9HwE 1,336回・adtWAjiQlnQ 1,273回は48h未満）。長尺は作らず（11/25 水 枠は見送り、次は 11/27 金）
- 11/25 am recipes/shorts/2026-11-25-am.json → **6cq_CVu_sz8**「【ひろゆき】38歳でモテたい…女性は結婚相手の見た目をそこまで重視しない？見慣れると気にならなくなる理由【切り抜き】」35.6秒、private→2026-11-24T22:00Z。pUsi5NQQgrA クリップ2390〜2490 の 24.8〜60.4秒。C①（11/23週2本目）。crop [700,150,720]（元動画のコメント表示を外す）。フルで見る→wpmnSdP8VNQ
- 11/25 pm recipes/shorts/2026-11-25-pm.json → **Z577uA8RdyY**「【ひろゆき】1年目からボーナスが出る職場か、資格が取れる職場か？若いうちの給料の差は「マジ誤差」な理由【切り抜き】」35.6秒、private→2026-11-25T09:00Z（18:00 JST）。2zED6c6zgx4 クリップ8640〜8740 の 35.92〜71.5秒。仕事/お金枠（11/23週2本目）。crop [690,180,540]＋cover 230（スパチャカード）。フルで見る→wpmnSdP8VNQ
- 両方とも概要欄2行目に相談内容を手で補足してからアップ。サムネはショートなので対象外
- docs/growth-ledger.md: 実験B 2行・施策C C① 1行（am）・施策D 適用ログ1行（pm）
- 11/23週（11/23〜11/29）の集計: C① 2本（Jy27D8k9HwE, 6cq_CVu_sz8）、仕事/お金枠 2本（adtWAjiQlnQ, Z577uA8RdyY）。どちらもあと1本まで

## 検証済みの事実（API / コマンド出力）

- 6cq_CVu_sz8 / Z577uA8RdyY: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-24T22:00:00Z / 2026-11-25T09:00:00Z、概要欄1行目は二択の問いかけ、フルで見る→wpmnSdP8VNQ（API。duration は処理中で P0D）
- 出力音声 faster-whisper: am 冒頭「男の人は女の人が綺麗かどうか結構重要なんですけど」末尾「女性はあるっぽいんですよね」。pm 冒頭「なりたいんだったら放課後デイサービスでいいんじゃないですか」→約4秒目「若いうちに給料が多少高いかどうかってマジ誤差ですよ」末尾「その資格が取れる方に行った方がいいんじゃないかなと思います」＋約2秒無音。確認画像 work/tmp1125/v_am.png, v_pm2.png

## 未検証

- 2本とも全編通し視聴はしていない
- pytest は box に pytest が無く未実行

## 次にやること

1. 夕方 11/24: adtWAjiQlnQ（am）の関連動画・問いかけ固定。gkdeigFmqug（18:00公開）は夕方が18:00前なら 11/25 夕方に回す
2. 夕方 11/25: 6cq_CVu_sz8（am）、gkdeigFmqug（前日 pm）。Z577uA8RdyY（18:00）は 11/26 夕方
3. 11/25（水）日次: 11/26 の am と pm。今週は C① 2本・仕事/お金枠 2本なので、どちらもあと1本まで。残りはどちらでもない題材
4. 昇格判定: Jy27D8k9HwE（48h は 11/25 07:00）、adtWAjiQlnQ（11/26 07:00）、gkdeigFmqug（11/26 18:00）、6cq_CVu_sz8（11/27 07:00）、Z577uA8RdyY（11/27 18:00）。次の昇格長尺枠は 11/27(金)18:30、その次 11/30(月)
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 題材探し: work/_kw.py "<正規表現>"、work/_peek.py <動画ID> <開始> <終了>、未使用一覧 `PYTHONPATH=. python3 work/_unused_1102.py`。単語タイムスタンプは `/workspace/wvenv/bin/python work/tmp1108/ww.py <wav> <開始> <終了>`。35秒に届かない良い一言が多いので、0秒目に一言を置ける区間は早めに確保する

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
