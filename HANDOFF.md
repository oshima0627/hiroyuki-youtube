# HANDOFF
最終更新: 2026-11-09 14:45 JST（11/9 日次）

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

## 今回やったこと（2026-11-09 日次）— 完了

- git pull（up to date）→ status: 11/9 07:00 7XEjK7VKTGI 公開済、11/9 t8Q5wQp7nPQ・11/11 cvvBcBDKDHk・11/13 pSkBQyXIKWo 予約済。11/10 07:00 のショートは0本
- 昇格判定（14:20 JST）: e3PGAJ1kFSs 1,366回（48h 到達）は 1,700 未満。IzKdqd1Js2s 1,306回は 48h 未達（11/10 07:00）。昇格なし
- 長尺: 次の月水金（11/11・11/13）は予約済みなので作らない。次の空き枠は 11/16（月）
- 11/10 ショート recipes/shorts/2026-11-10-am.json → **653l90JxsV4**「【ひろゆき】新卒は年収の高い東京か、暮らしやすい大阪か？先に東京で働いた方がいい理由【切り抜き】」39秒、private→2026-11-09T22:00Z。4vmH4mejnjI 8421.0〜8460.4。冒頭「一回大阪で働いてしまって、そこから東京に上がるのが難しくなる可能性がある」。フルで見る→t8Q5wQp7nPQ（11/9 18:30 公開）。仕事・年収系
- 初回取得の区間ファイルに音声が無かった（2回目）→ 削除して再取得で解決。取得後は ffprobe で audio ストリームを確認すること
- docs/growth-ledger.md 実験B に1行追記

## 検証済みの事実（API / コマンド出力）

- 653l90JxsV4: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-09T22:00:00Z、概要欄1行目の問いかけ、フルで見る→t8Q5wQp7nPQ
- 0秒目音声: faster-whisper small で「一回大阪で働いてしまって…」を確認

## 未検証

- 653l90JxsV4 の映像を全編通しでは見ていない（0.3/20/38秒のフレームのみ）。縦型クロップは顔がやや下寄り（既存処理のまま）
- 653l90JxsV4 の処理完了後の duration（アップロード直後は P0D）

## 次にやること

1. 夕方 11/9: 7XEjK7VKTGI 関連→t8Q5wQp7nPQ（18:30 公開後）、t8Q5wQp7nPQ の問いかけ固定・終了画面。夕方 11/10: 653l90JxsV4 関連→t8Q5wQp7nPQ・問いかけ固定
2. 11/10（火）日次: 11/11 ショート。長尺は通常枠なし（11/16 月は 11/11 以降の日次で作るか、昇格があれば優先）
3. 昇格判定: IzKdqd1Js2s（48h は 11/10 07:00）、7XEjK7VKTGI（11/11 07:00）、653l90JxsV4（11/12 07:00）
4. 11/11 公開後 93NkdAOx0uo 関連→cvvBcBDKDHk、11/13 公開後 84oRUIoiUoI 関連→pSkBQyXIKWo・終了画面
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 11/11 比較、11/16 15:00 実験B 比較 routine

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
