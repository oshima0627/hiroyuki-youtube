# HANDOFF
最終更新: 2026-11-23 15:00 JST（11/23 日次）

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

## 今回やったこと（2026-11-23 日次）— 完了

- git pull → status（14:20 JST）: 11/23 07:00 Jy27D8k9HwE 公開済。11/24 の am/pm は0本だった
- 昇格判定: 48h超で1,700回超の未処理ショートなし（48h超の未昇格で最大は CfPbeHlWoP8 1,470回（旧）、直近週では 5RekW-bgrB4 1,343回・3qdS3FVuX_8 1,233回。Ke2zw5ZPiA0 1,352回・Jy27D8k9HwE 1,290回は48h未満）。長尺は作らず（11/23 枠は見送り、次は 11/25 水）
- 11/24 am recipes/shorts/2026-11-24-am.json → **adtWAjiQlnQ**「【ひろゆき】仕事がきつくてすぐ転職したい…21歳で転職回数が多いと不利？正社員で2〜3年続けた方がいい理由【切り抜き】」40.2秒、private→2026-11-23T22:00Z。g2N-OcbplbA クリップ2300〜2390 の 41.0〜81.2秒。仕事/お金枠（11/23週1本目）。crop [540,70,676]＋自動黒帯39px。フルで見る→wpmnSdP8VNQ
- 11/24 pm recipes/shorts/2026-11-24-pm.json → **gkdeigFmqug**「【ひろゆき】「その考えは良くない」と決めつける人にどう言い返す？批判する側も決めつけている理由【切り抜き】」38.0秒、private→2026-11-24T09:00Z（18:00 JST）。0ojMhUyiHB4 クリップ5890〜5990 の 36.6〜74.6秒。どちらでもない枠。crop [600,0,700]＋自動黒帯151px（スパチャカード上端602）。フルで見る→wpmnSdP8VNQ
- 両方とも概要欄2行目に相談内容を手で補足してからアップ
- docs/growth-ledger.md: 実験B 2行・施策D 適用ログ1行（pm）。C①は今回なし
- 11/23週（11/23〜11/29）の集計: C① 1本（Jy27D8k9HwE）、仕事/お金枠 1本（adtWAjiQlnQ）

## 検証済みの事実（API / コマンド出力）

- adtWAjiQlnQ / gkdeigFmqug: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-23T22:00:00Z / 2026-11-24T09:00:00Z、概要欄1行目は二択の問いかけ、フルで見る→wpmnSdP8VNQ（API。duration は処理中で P0D）
- 出力音声を faster-whisper small で確認: am 冒頭「21歳で転職歴が多いと履歴書的にも厳しいと思うので」末尾「転職はしやすいんじゃないかなと思います」。pm 冒頭「その質問者さんも人間中心の考えは良くないと勝手に決めつけてるんですよ」末尾「そうじゃない考え方も認めた方がいいんじゃないですか」。コンタクトシート work/tmp1124/out_am.jpg, out_pm3.jpg

## 未検証

- 2本とも全編通し視聴はしていない
- pytest は box に pytest が無く未実行

## 次にやること

1. 夕方 11/23: Jy27D8k9HwE 関連→wpmnSdP8VNQ・問いかけ固定
2. 夕方 11/24: adtWAjiQlnQ（am）の関連動画・問いかけ固定。gkdeigFmqug（pm 18:00公開）は夕方が18:00前なら 11/25 夕方に回す
3. 11/24（火）日次: 11/25 の am（07:00）と pm（18:00）。今週 11/23〜 は C①1本・仕事/お金枠1本なので、どちらもあと1〜2本まで。残りはどちらでもない題材
4. 昇格判定: Ke2zw5ZPiA0（48h は 11/24 07:00）、Jy27D8k9HwE（11/25 07:00）、adtWAjiQlnQ（11/26 07:00）、gkdeigFmqug（11/26 18:00）。次の昇格長尺枠は 11/25(水)18:30、その次 11/27(金)
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 題材探し: work/_kw.py "<正規表現>"、work/_peek.py <動画ID> <開始> <終了>、未使用一覧 `PYTHONPATH=. python3 work/_unused_1102.py`。単語タイムスタンプは `/workspace/wvenv/bin/python work/tmp1108/ww.py <wav> <開始> <終了>`

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
