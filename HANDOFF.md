# HANDOFF
最終更新: 2026-11-08 14:50 JST（11/8 日次）

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

## 今回やったこと（2026-11-08 日次）— 完了

- state/published.json のローカル差分は --status による再生回数・upload_status 更新のみだったので checkout で破棄 → git pull（up to date）
- status: 11/8 07:00 IzKdqd1Js2s 公開済、11/9 18:30 t8Q5wQp7nPQ・11/11 18:30 cvvBcBDKDHk 予約済。11/9 07:00 のショートは0本だった
- 昇格判定（14:22 JST）: **84oRUIoiUoI 2,609回**（11/5 22:00Z 公開・48h 到達済）→ 昇格。QC24A3gd2jc 1,406・2lmeaIMPp-c 1,256 は 1,700 未満。e3PGAJ1kFSs 1,366・IzKdqd1Js2s 1,276 は 48h 未達
- 11/9 ショート recipes/shorts/2026-11-09-am.json → **7XEjK7VKTGI**「【ひろゆき】給料が安くて経済的に自立できない…転職すべき？低賃金なら正社員を目指す理由【切り抜き】」41秒、private→2026-11-08T22:00Z。2zED6c6zgx4 8381.7〜8422.6。冒頭「高いお金を得なくても楽しく仕事ができれば人生幸せ」。フルで見る→kdcGL3JwZSM。仕事・お金系
- 11/13（金）昇格長尺 recipes/2026-11-13-konjou.json → **pSkBQyXIKWo**「【ひろゆき】根性論で練習すれば伸びる？昭和のしごきより「理論が土台」の練習好きが結果を出す理由」5:32、private→2026-11-13T09:30Z。O0YEy2NB3os の cold 362.9〜368.9 / 112.1〜153.9 / 231.4〜284.5 / 325.0〜368.9。サムネ at 120・auto-crop、API 設定成功。アップロード直後のタイトル（「スポーツも勉強も」）は内容と合わないので API で変更済み
- 84oRUIoiUoI のフルで見るを **m4R7_9CT_o4**→pSkBQyXIKWo（変更前は kdcGL3JwZSM ではなく m4R7_9CT_o4 だった）。recipes/shorts/2026-11-06-am.json の parent も更新
- docs/growth-ledger.md: 昇格1行、実験B 2行を追記（昇格表の途中の空行も除去）
- 360-368 の初回取得ファイルに音声ストリームが無かったので削除して 362.9 開始で再取得（再取得分は音声あり）

## 検証済みの事実（API / コマンド出力）

- 7XEjK7VKTGI: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-08T22:00:00Z、PT41S、概要欄1行目の問いかけ、フルで見る→kdcGL3JwZSM
- pSkBQyXIKWo: private、publishAt 2026-11-13T09:30:00Z、PT5M32S、サムネ maxres あり、概要欄1行目の問いかけ、新タイトル反映
- 84oRUIoiUoI: 概要欄のフルで見る→pSkBQyXIKWo（更新後に再取得で確認）
- 0秒目音声: 両本 faster-whisper small で確認（ledger の実験B ログ参照）

## 未検証

- pSkBQyXIKWo / 7XEjK7VKTGI の映像を全編通しでは見ていない（0秒目・数フレームのみ確認）
- 7XEjK7VKTGI の縦型クロップは顔がやや左下寄り（既存処理のまま）

## 次にやること

1. 夕方 11/8: IzKdqd1Js2s 関連→kdcGL3JwZSM・問いかけ固定。夕方 11/9: 7XEjK7VKTGI 関連→t8Q5wQp7nPQ（18:30 公開後）または kdcGL3JwZSM、t8Q5wQp7nPQ の問いかけ固定・終了画面
2. 11/9（月）日次: 11/10 ショート（フルで見る→t8Q5wQp7nPQ、11/9 18:30 公開済み）。長尺は 11/11・11/13 予約済みなので通常枠なし。次の空き枠は 11/16（月）
3. 昇格判定: e3PGAJ1kFSs（48h は 11/9 07:00）、IzKdqd1Js2s（48h は 11/10 07:00）。84oRUIoiUoI・93NkdAOx0uo・qY_hj45hxC0・oUt6kcCwW5c は昇格済
4. 11/11 公開後 93NkdAOx0uo 関連→cvvBcBDKDHk、11/13 公開後 84oRUIoiUoI 関連→pSkBQyXIKWo・終了画面
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 11/11 比較、11/16 15:00 実験B 比較 routine

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
