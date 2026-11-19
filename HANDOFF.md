# HANDOFF
最終更新: 2026-11-19 14:45 JST（11/19 日次）

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

## 今回やったこと（2026-11-19 日次）— 完了

- git pull → status: 11/19 07:00 h1i3_HsIsmQ 公開済。11/20 07:00 のショートは0本だった
- 昇格判定（14:20 JST）: 48h超で1,700回超の未処理ショートなし（Z7ZIj6mrBGo 1,104回、OD7nJkdkB0M 1,292回）。今週（11/16〜）の長尺は S_-Wjubw8sE・wpmnSdP8VNQ の2本で上限なので作らず
- 11/20 ショート recipes/shorts/2026-11-20-am.json → **5RekW-bgrB4**「【ひろゆき】タトゥーは通勤中も隠すべき？仕事中だけ隠せばいいと考える理由【切り抜き】」35.9秒、private→2026-11-19T22:00Z。M7KWrHANxHs クリップ7500〜7600 の 32.2〜68.1秒。C①（働き方／身だしなみ観、今週3本目）。フルで見る→wpmnSdP8VNQ（直近の長尺）。crop [690,196,500]＋cover 20（スパチャカード上端698で切る。頭は下向きで顎が切れるフレームあり）
- docs/growth-ledger.md: 実験B 1行、施策C 1行

## 検証済みの事実（API / コマンド出力）

- 5RekW-bgrB4: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-19T22:00:00Z、概要欄1行目は二択の問いかけ、フルで見る→wpmnSdP8VNQ
- 冒頭音声は faster-whisper small で「えっとなんか会社の仕事で隠さなきゃいけない…通勤も出していいんじゃない」、末尾は「マジどうでもよくない」で終わる。コンタクトシート work/tmp1120/sheet2.jpg

## 未検証

- 5RekW-bgrB4 の全編通し視聴はしていない
- pytest は box に pytest が無く未実行

## 次にやること

1. 夕方 11/19: h1i3_HsIsmQ 関連→wpmnSdP8VNQ・問いかけ固定
2. 夕方 11/20: 5RekW-bgrB4 関連→wpmnSdP8VNQ・問いかけ固定
3. 11/20（金）日次: 11/21 ショート。今週の長尺は上限。次の昇格長尺は来週 11/23(月)18:30〜
4. 昇格判定: lIl_deIHrE0（48h は 11/20 07:00）、h1i3_HsIsmQ（11/21 07:00）、5RekW-bgrB4（11/22 07:00）
5. 今週（11/16〜）の C① は Z7ZIj6mrBGo・lIl_deIHrE0・5RekW-bgrB4 で3本＝上限。残り（11/21・11/22 公開分）は C① 以外に。お金/住まい枠は OD7nJkdkB0M・h1i3_HsIsmQ の2本。住まい・家賃系がまだ無い（EXUXJaPlKmE 4827〜4876 の賃貸のカビ・壁紙の原状回復は答えが約27秒で短い）
6. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
7. 11/23 09:00 週次レビュー routine

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
