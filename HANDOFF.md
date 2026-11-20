# HANDOFF
最終更新: 2026-11-20 14:40 JST（11/20 日次）

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

## 今回やったこと（2026-11-20 日次）— 完了

- git pull → status: 11/20 07:00 5RekW-bgrB4 公開済。11/21 07:00 のショートは0本だった
- 昇格判定（14:20 JST）: 48h超で1,700回超の未処理ショートなし（Z7ZIj6mrBGo 1,109回、lIl_deIHrE0 1,060回、OD7nJkdkB0M 1,293回）。h1i3_HsIsmQ・5RekW-bgrB4 は48h未満。今週（11/16〜）の長尺は上限なので作らず
- 11/21 ショート recipes/shorts/2026-11-21-am.json → **3qdS3FVuX_8**「【ひろゆき】食費を節約するなら自炊？美味しいものは「自分で作るか高い金を払うか」の2択な理由【切り抜き】」40.1秒、private→2026-11-20T22:00Z。a3zM5hCv-Uo クリップ8700〜8790 の 43.2〜83.3秒。お金（節約・食費）の検索語枠（C①ではない）。フルで見る→wpmnSdP8VNQ。crop [600,8,690]（自動だと頭が左に切れた）
- docs/growth-ledger.md: 実験B 1行
- 題材探し: work/_kw.py "<正規表現>" で字幕を全文検索（使用済み区間は除外）。work/_peek.py <動画ID> <開始> <終了> で字幕を読む

## 検証済みの事実（API / コマンド出力）

- 3qdS3FVuX_8: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-20T22:00:00Z、概要欄1行目は二択の問いかけ、フルで見る→wpmnSdP8VNQ
- 出力音声を faster-whisper small で確認: 冒頭「あの人生ってあの美味しいものを食べたいと思った時に自分で作るか高い金を払うか…」、末尾「満足度も上がるんじゃないかなと思います」で終わる。コンタクトシート work/tmp1121/sheet2.jpg

## 未検証

- 3qdS3FVuX_8 の全編通し視聴はしていない
- pytest は box に pytest が無く未実行

## 次にやること

1. 夕方 11/20: 5RekW-bgrB4 関連→wpmnSdP8VNQ・問いかけ固定
2. 夕方 11/21: 3qdS3FVuX_8 関連→wpmnSdP8VNQ・問いかけ固定
3. 11/21（土）日次: 11/22 ショート。今週の C① は上限、お金/仕事枠は OD7nJkdkB0M・h1i3_HsIsmQ・3qdS3FVuX_8 の3本で上限 → 11/22 は C① でもお金枠でもない題材（または来週分として扱えるか確認）
4. 昇格判定: h1i3_HsIsmQ（48h は 11/21 07:00）、5RekW-bgrB4（11/22 07:00）、3qdS3FVuX_8（11/23 07:00）。次の昇格長尺枠は 11/23(月)18:30
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 11/23 09:00 週次レビュー routine

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
