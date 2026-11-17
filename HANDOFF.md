# HANDOFF
最終更新: 2026-11-17 14:45 JST（11/17 日次）

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

## 今回やったこと（2026-11-17 日次）— 完了

- git pull → status: 11/17 07:00 Z7ZIj6mrBGo 公開済、11/18 18:30 wpmnSdP8VNQ 予約済。11/18 07:00 のショートは0本
- 昇格判定（14:20 JST）: Qk1k0JJCyAE 1,157回（48h超）で昇格なし。OD7nJkdkB0M・Z7ZIj6mrBGo は48h未達。今週（11/16〜）の長尺は2本で上限なので長尺は作らず
- 11/18 ショート recipes/shorts/2026-11-18-am.json → **lIl_deIHrE0**「【ひろゆき】24歳フリーターから大学に行くのは遅い？29歳卒業でも大卒なら就職できる理由【切り抜き】」37.4秒、private→2026-11-17T22:00Z。pUsi5NQQgrA クリップ5675〜5760 の 13.1〜50.5秒。冒頭テロップ「29歳卒業でも大卒なら就職できる」。C①（学歴・働き方観）。フルで見る→S_-Wjubw8sE（前日長尺なし→直近公開の長尺）。crop [650,170,520]＋cover 115（スパチャカード隠し。後半の松山市長選のスパチャは枠外）
- docs/growth-ledger.md: 実験B 1行、施策C 1行

## 検証済みの事実（API / コマンド出力）

- lIl_deIHrE0: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-17T22:00:00Z、概要欄1行目は二択の問いかけ、フルで見る→S_-Wjubw8sE
- 冒頭音声は faster-whisper small で「今24だから29卒業でも…何の問題もなく就職できる」、最後に問いかけテロップ

## 未検証

- lIl_deIHrE0 の全編通し視聴はしていない（3秒付近で顔が右端に寄る瞬間あり）

## 次にやること

1. 夕方 11/17: Z7ZIj6mrBGo 関連→S_-Wjubw8sE・問いかけ固定。夕方 11/18: lIl_deIHrE0 関連→S_-Wjubw8sE・問いかけ固定、XnpPzG1ERco 関連→wpmnSdP8VNQ、C②（XnpPzG1ERco 概要欄2行目・固定コメントに wpmnSdP8VNQ）、wpmnSdP8VNQ の問いかけ固定と終了画面
2. 11/18（水）日次: 11/19 ショート。今週の長尺は上限。次の昇格長尺は来週（11/23〜）の月水金
3. 昇格判定: OD7nJkdkB0M（48h は 11/18 07:00）、Z7ZIj6mrBGo（11/19 07:00）、lIl_deIHrE0（11/20 07:00）
4. 施策C①: 今週（11/16〜）は Z7ZIj6mrBGo・lIl_deIHrE0 の2本。今週あと0〜1本。お金・住まい系の検索語ショートも今週は OD7nJkdkB0M（仕事）以外まだ少ないので、11/19〜は お金/住まい を優先
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 11/23 09:00 週次レビュー routine

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
