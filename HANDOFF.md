# HANDOFF
最終更新: 2026-11-21 14:35 JST（11/21 日次）

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

## 今回やったこと（2026-11-21 日次）— 完了

- git pull → status: 11/21 07:00 3qdS3FVuX_8 公開済。11/22 07:00 のショートは0本だった
- 昇格判定（14:25 JST）: 48h超で1,700回超の未処理ショートなし（最大は 5RekW-bgrB4 1,334回だが48h未満、48h超では OD7nJkdkB0M 1,293回・h1i3_HsIsmQ 1,021回）。1,700回超は 93NkdAOx0uo・84oRUIoiUoI・qY_hj45hxC0・oUt6kcCwW5c・653l90JxsV4・XnpPzG1ERco で全て昇格済み。長尺は作らず
- 11/22 ショート recipes/shorts/2026-11-22-am.json → **Ke2zw5ZPiA0**「【ひろゆき】筋トレはジムに通わないと無理？家の自重トレーニングでも十分筋肉がつく理由【切り抜き】」38.4秒、private→2026-11-21T22:00Z。EXUXJaPlKmE クリップ7110〜7230 の 39.1〜77.5秒。健康・筋トレ題材（お金枠でもC①でもない）。フルで見る→wpmnSdP8VNQ。crop [640,50,640]（自動だと頭が左に切れた）
- docs/growth-ledger.md: 実験B 1行（施策C ログは該当なし）
- 題材探し: work/_kw.py "<正規表現>" で字幕を全文検索（使用済み区間は除外）。work/_peek.py <動画ID> <開始> <終了> で字幕を読む

## 検証済みの事実（API / コマンド出力）

- Ke2zw5ZPiA0: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-21T22:00:00Z、概要欄1行目は二択の問いかけ、フルで見る→wpmnSdP8VNQ（API で確認。duration は処理中で P0D）
- 出力音声を faster-whisper small で確認: 冒頭「あの自重でやるトレーニングでも普通に十分筋肉がつくんですよね」、末尾「お金もったいないでしょって話なんですよ」で終わる（38.06秒）。コンタクトシート work/tmp1122/sheet2.jpg

## 未検証

- Ke2zw5ZPiA0 の全編通し視聴はしていない
- pytest は box に pytest が無く未実行

## 次にやること

1. 夕方 11/21: 3qdS3FVuX_8 関連→wpmnSdP8VNQ・問いかけ固定
2. 夕方 11/22: Ke2zw5ZPiA0 関連→wpmnSdP8VNQ・問いかけ固定
3. 11/22（日）日次: 11/23 ショート（新しい週 11/23〜 なのでお金枠・C① ともに再び可）
4. 昇格判定: 5RekW-bgrB4（48h は 11/22 07:00、11/21 時点 1,334回）、3qdS3FVuX_8（11/23 07:00）、Ke2zw5ZPiA0（11/24 07:00）。次の昇格長尺枠は 11/23(月)18:30（作るなら 11/22 日次で予約）
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 11/23 09:00 週次レビュー routine

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
