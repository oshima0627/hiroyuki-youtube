# HANDOFF
最終更新: 2026-11-11 14:55 JST（11/11 日次）

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

## 今回やったこと（2026-11-11 日次）— 完了

- git pull → status: 11/11 07:00 JqrRXmGjMlk 公開済、11/11 18:30 cvvBcBDKDHk・11/13 18:30 pSkBQyXIKWo 予約済。11/12 07:00 のショートは0本だった
- 昇格判定（14:30 JST）: 7XEjK7VKTGI 1,294回（48h 到達）・e3PGAJ1kFSs 1,366回・IzKdqd1Js2s 1,352回とも 1,700 未満。653l90JxsV4 1,433回・JqrRXmGjMlk 1,124回は 48h 未達。昇格なし
- 長尺: 次の月水金（11/13）は予約済みなので作らない。次の空き枠は 11/16（月）
- 11/12 ショート recipes/shorts/2026-11-12-am.json → **U0d9D_L-ps4**「【ひろゆき】年収450万から楽な年収400万の会社に転職していい？結婚を考えるなら気をつけたい理由【切り抜き】」40秒、private→2026-11-11T22:00Z。0YyAgmv5_Yc クリップ5485〜5560 の 22.45〜62.45秒。冒頭「400万は日本の平均年収よりは低いんですよ」。フルで見る→cvvBcBDKDHk（前日=11/11 公開の長尺）。年収・仕事系
- 注意: クリップの mp4 は whisper 上の時刻と字幕(subs.json)の時刻が約2秒ずれる。short.start はクリップを whisper で測って決めた（最初 24.1 で切ったら「平均」から始まったので 22.45 に修正）
- 顔が左で切れたので short.crop=[690,0,650] を手動指定
- docs/growth-ledger.md 実験B に1行追記

## 検証済みの事実（API / コマンド出力）

- U0d9D_L-ps4: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-11T22:00:00Z、概要欄1行目の問いかけ、フルで見る→cvvBcBDKDHk
- 0秒目音声は faster-whisper small で「400万は日本の平均年収よりは低いんですよ」、末尾 38.9秒「〜可能性あるんじゃないかなと思います」で終わる
- フレーム 0.3/10/20/30/38.5秒を確認（顔は枠内、最後に問いかけテロップ）

## 未検証

- U0d9D_L-ps4 の全編通し視聴はしていない。処理完了後の duration（直後は D）

## 次にやること

1. 夕方 11/11: JqrRXmGjMlk 関連→t8Q5wQp7nPQ（または前日長尺ルールに従い判断）・問いかけ固定、93NkdAOx0uo 関連→cvvBcBDKDHk、cvvBcBDKDHk の問いかけ固定・終了画面。夕方 11/12: U0d9D_L-ps4 関連→cvvBcBDKDHk・問いかけ固定
2. 11/12（木）日次: 11/13 ショート。11/16（月）長尺枠が空き（昇格があれば優先、無ければ note 済み未使用レシピか新規レシピで1〜3問の深掘り）。11/13 日次で 11/16 長尺を作る
3. 昇格判定: 653l90JxsV4（48h は 11/12 07:00）、JqrRXmGjMlk（11/13 07:00）、U0d9D_L-ps4（11/14 07:00）
4. 11/13 公開後 84oRUIoiUoI 関連→pSkBQyXIKWo・終了画面
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 11/11 15:00 成長施策比較、11/16 15:00 実験B 比較 routine

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
