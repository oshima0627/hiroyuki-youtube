# HANDOFF
最終更新: 2026-11-12 15:20 JST（11/12 日次）

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

## 今回やったこと（2026-11-12 日次）— 完了

- git pull → status: 11/12 07:00 U0d9D_L-ps4 公開済、11/13 18:30 pSkBQyXIKWo 予約済。11/13 07:00 のショートは0本、11/16（月）長尺枠は空き
- 昇格判定（14:20 JST）: **653l90JxsV4 1,739回（48h 到達）→ 昇格**。他は 1,700 未満（7XEjK7VKTGI 1,299・IzKdqd1Js2s 1,369・e3PGAJ1kFSs 1,368）、JqrRXmGjMlk 1,307 は 48h 未達（11/13 07:00）
- 11/13 ショート recipes/shorts/2026-11-13-am.json → **YZVlJgnzMk0**「【ひろゆき】結婚はギャンブル？恋人を作らない若者が増えたのは「頭が良くなった」から【切り抜き】」37秒、private→2026-11-12T22:00Z。0YyAgmv5_Yc クリップ4525〜4625 の 28.55〜65.45秒。冒頭「結婚した後に…60年間…分かるわけがないんですよ」、テロップは同じ意味に短縮。フルで見る→cvvBcBDKDHk（前日長尺なし→直近公開の長尺）。恋愛・価値観系（今週はお金・仕事系が4本続いたので外した）。crop=[600,0,760] 手動
- 11/16 昇格長尺 recipes/2026-11-16-tokyo.json → **S_-Wjubw8sE**（5:53、private→2026-11-16T09:30Z、サムネAPI設定成功、thumb.at=85）。2問: 4vmH4mejnjI 8402〜8460（新卒は東京か大阪か）＋ 2zED6c6zgx4 3213.2〜3296（子育て世帯は首都圏か地方か。前半3095〜3160 は 11/3 ショートで使用済みなので後半のみ）。冒頭は 4vmH4mejnjI 8420.6〜8428.55「1回大阪で働いてしまって、そっから東京に上がるのが難しくなる可能性がある」
- 653l90JxsV4 のフルで見る → S_-Wjubw8sE に変更（work/_update_short_full.py）
- IXiLxkgHUMM（20代は東京→地元・資格の相談 4481〜4570）は collab_warning（いずみ氏との共演）があるので使わなかった
- docs/growth-ledger.md: 昇格の記録1行・実験B 2行追記
- 注意: build_short の short.start/end と build_episode のクリップ再生は、区間ファイル（pad 2秒）の 2秒目が recipe の start。faster-whisper はこのショートの完成音声だとほぼ認識しなかったので、素材 wav との包絡相関で開始位置（素材30.55秒）を確認した

## 検証済みの事実（API / コマンド出力）

- YZVlJgnzMk0: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-12T22:00:00Z、概要欄1行目の問いかけ、フルで見る→cvvBcBDKDHk。フレーム 0.3/8/15/25/36.3秒で顔は枠内、最後に問いかけテロップ
- S_-Wjubw8sE: 同チャンネル、private、publishAt 2026-11-16T09:30:00Z、概要欄1行目の問いかけ、サムネ設定 ✓。0秒目音声は faster-whisper で「一回大阪で働いてしまって…」。outro（終了画面用）333.6〜353.6秒

## 未検証

- 両動画の全編通し視聴はしていない。653l90JxsV4 の概要欄変更後の全文は API の AFTER 出力のみ確認

## 次にやること

1. 夕方 11/12: U0d9D_L-ps4 関連→cvvBcBDKDHk・問いかけ固定。夕方 11/13: YZVlJgnzMk0 関連→（前日長尺なし。直近公開の長尺は 11/13 18:30 公開の pSkBQyXIKWo になるので夕方ルールで判断）、84oRUIoiUoI 関連→pSkBQyXIKWo、pSkBQyXIKWo の問いかけ固定・終了画面。653l90JxsV4 の関連動画→S_-Wjubw8sE は 11/16 公開後
2. 11/13（金）日次: 11/14 ショートのみ。長尺は 11/13・11/16 予約済み。次の空きは 11/18（水）
3. 昇格判定: JqrRXmGjMlk（48h は 11/13 07:00）、U0d9D_L-ps4（11/14 07:00）、YZVlJgnzMk0（11/15 07:00）
4. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
5. 11/16 15:00 実験B 比較 routine

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
