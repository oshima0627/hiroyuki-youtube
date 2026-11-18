# HANDOFF
最終更新: 2026-11-18 14:55 JST（11/18 日次）

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

## 今回やったこと（2026-11-18 日次）— 完了

- git pull → status: 11/18 07:00 lIl_deIHrE0 公開済、11/18 18:30 wpmnSdP8VNQ 予約済。11/19 07:00 のショートは0本
- 昇格判定（14:25 JST）: 48h超で1,700回超の未処理ショートなし。48h超の最多は OD7nJkdkB0M 1,281回（11/18 07:00 で48h）。Z7ZIj6mrBGo（1,096回）・lIl_deIHrE0 は48h未達。今週の長尺は上限なので作らず
- 11/19 ショート recipes/shorts/2026-11-19-am.json → **h1i3_HsIsmQ**「【ひろゆき】医療保険・生命保険はいらない？高額療養費制度がある日本で民間保険に入る理由が少ないワケ【切り抜き】」35.2秒、private→2026-11-18T22:00Z。O0YEy2NB3os クリップ4120〜4200 の 35.3〜70.5秒。冒頭テロップ「医療のために保険でお金を貯めるのはあんまり意味ない」。お金の検索語枠（C①ではない）。フルで見る→wpmnSdP8VNQ（前日長尺）。crop [500,150,580]＋cover 75＋end_cover 140
- scripts/build_short.py: short.end_cover を追加（最後の問いかけテロップ3.5秒だけ黒帯を広げる。終盤に次のスパチャカードが下から出る回用）。70.5秒付近（クリップ mp4 71.75秒）から黄色カードが出るため
- docs/growth-ledger.md: 実験B 1行（施策Cは該当なし）

## 検証済みの事実（API / コマンド出力）

- h1i3_HsIsmQ: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-18T22:00:00Z、概要欄1行目は二択の問いかけ、フルで見る→wpmnSdP8VNQ
- 冒頭音声は faster-whisper small で「あの日本の場合は高額医療制度があるので…」、最後に問いかけテロップ。コンタクトシートで黄色カードが映らないことを確認（work/tmp1119/grid3.jpg）

## 未検証

- h1i3_HsIsmQ の全編通し視聴はしていない（顎が黒帯にかかるフレームあり）
- pytest は box に pytest が無く未実行

## 次にやること

1. 夕方 11/18: lIl_deIHrE0 関連→S_-Wjubw8sE（または wpmnSdP8VNQ）・問いかけ固定、XnpPzG1ERco 関連→wpmnSdP8VNQ、C②（XnpPzG1ERco 概要欄2行目・固定コメントに wpmnSdP8VNQ）、wpmnSdP8VNQ の問いかけ固定と終了画面
2. 夕方 11/19: h1i3_HsIsmQ 関連→wpmnSdP8VNQ・問いかけ固定
3. 11/19（木）日次: 11/20 ショート。今週の長尺は上限。次の昇格長尺は来週 11/23(月)18:30〜
4. 昇格判定: Z7ZIj6mrBGo（48h は 11/19 07:00）、lIl_deIHrE0（11/20 07:00）、h1i3_HsIsmQ（11/21 07:00）
5. 施策C①: 今週（11/16〜）は Z7ZIj6mrBGo・lIl_deIHrE0 の2本で下限達成。お金/住まい枠は OD7nJkdkB0M（仕事）・h1i3_HsIsmQ（保険）。住まい・家賃系がまだ無い
6. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
7. 11/23 09:00 週次レビュー routine

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
