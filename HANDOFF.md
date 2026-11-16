# HANDOFF
最終更新: 2026-11-16 15:05 JST（11/16 日次）

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

## 今回やったこと（2026-11-16 日次）— 完了

- git pull → status: 11/16 07:00 OD7nJkdkB0M 公開済、11/16 18:30 S_-Wjubw8sE 予約済。11/17 07:00 のショートは0本
- 昇格判定（14:19 JST）: **XnpPzG1ERco が 1,741回（48h超）で昇格**。Qk1k0JJCyAE（1,142回）・OD7nJkdkB0M は48h未達
- 11/17 ショート recipes/shorts/2026-11-17-am.json → **Z7ZIj6mrBGo**「【ひろゆき】結婚は何歳までに考えるべき？35歳を超えると結婚市場で人気がなくなる理由【切り抜き】」35.2秒、private→2026-11-16T22:00Z。_Qc2ZF3MLO0 クリップ2765〜2835 の 18.4〜53.6秒。冒頭テロップ「35歳を超えると結婚市場で人気がなくなる」。C①（結婚観）。フルで見る→S_-Wjubw8sE（前日長尺）。crop は自動（素材 1280x720）
- 昇格長尺 recipes/2026-11-18-motenai.json → **wpmnSdP8VNQ**「【ひろゆき】男子ばかりの高校で恋愛できないのは損？若いうちはモテない方が人生が楽しくなる理由」5:55、private→2026-11-18T09:30Z（11/18 18:30 JST）。daulqJwmooE の1問を4区間で深掘り（元動画再生 約156秒）。冒頭「若いうちはモテない方が人生楽しいですよ」（6006.8秒〜）。サムネ API 設定成功（thumb.at=70、前半はスパチャカードが映るので避けた）。「女性芸人は不細工」「モテる女はつまらん」の部分は人を攻撃する表現なので使っていない
- XnpPzG1ERco のフルで見る → wpmnSdP8VNQ（_update_short_full.py）
- クリップ区間の微調整は既存の work/clips/daulqJwmooE_5985-6065.mp4 などから ffmpeg で切り出して `<id>_<int(start)>-<int(end)>.mp4`（先頭 = start−2秒）を作った（再取得を省略）
- docs/growth-ledger.md: 昇格1行、実験B 2行、施策C 2行（Z7ZIj6mrBGo C①、wpmnSdP8VNQ C③）

## 検証済みの事実（API / コマンド出力）

- Z7ZIj6mrBGo・wpmnSdP8VNQ: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt はそれぞれ 2026-11-16T22:00:00Z / 2026-11-18T09:30:00Z、概要欄1行目は二択の問いかけ
- 概要欄のフルで見る: Z7ZIj6mrBGo→S_-Wjubw8sE、XnpPzG1ERco→wpmnSdP8VNQ
- 冒頭音声は両方 faster-whisper small で確認。Z7ZIj6mrBGo のフレーム 0.3/10/20/30/34.8秒で顔は枠内、最後に問いかけテロップ

## 未検証

- Z7ZIj6mrBGo・wpmnSdP8VNQ の全編通し視聴はしていない

## 次にやること

1. 夕方 11/16: OD7nJkdkB0M 関連→S_-Wjubw8sE・問いかけ固定、S_-Wjubw8sE の問いかけ固定と終了画面、653l90JxsV4 の関連→S_-Wjubw8sE、C②（653l90JxsV4 概要欄・固定コメントに S_-Wjubw8sE）
2. 夕方 11/17: Z7ZIj6mrBGo 関連→S_-Wjubw8sE・問いかけ固定。夕方 11/18: XnpPzG1ERco 関連→wpmnSdP8VNQ、C②（XnpPzG1ERco 概要欄2行目・固定コメントに wpmnSdP8VNQ）、wpmnSdP8VNQ の問いかけ固定と終了画面
3. 11/17（火）日次: 11/18 ショート。今週（11/16〜）の長尺は S_-Wjubw8sE・wpmnSdP8VNQ で2本＝上限。次の昇格は来週（11/23〜）の月水金
4. 昇格判定: Qk1k0JJCyAE（48h は 11/17 07:00）、OD7nJkdkB0M（11/18 07:00）、Z7ZIj6mrBGo（11/19 07:00）
5. 施策C①: 今週（11/16〜）は Z7ZIj6mrBGo の1本。週2〜3本。直近は恋愛・結婚が続いたので、次のC①は働き方・学歴などに振る
6. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
7. 11/16 15:00 実験B 比較 routine、11/23 09:00 週次レビュー routine

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
