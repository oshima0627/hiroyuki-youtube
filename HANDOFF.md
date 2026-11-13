# HANDOFF
最終更新: 2026-11-13 14:40 JST（11/13 日次）

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

## 今回やったこと（2026-11-13 日次）— 完了

- git pull → status: 11/13 07:00 YZVlJgnzMk0 公開済、11/13 18:30 pSkBQyXIKWo・11/16 18:30 S_-Wjubw8sE 予約済。11/14 07:00 のショートは0本
- 昇格判定（14:25 JST）: 新規なし。1,700回超は 653l90JxsV4・93NkdAOx0uo・84oRUIoiUoI・qY_hj45hxC0・oUt6kcCwW5c でいずれも昇格済み。JqrRXmGjMlk は48h到達で1,363回→昇格なし。施策C③により長尺は作らない
- 11/14 ショート recipes/shorts/2026-11-14-am.json → **XnpPzG1ERco**「【ひろゆき】男子ばかりの高校で恋愛できない…若いうちはモテない方が人生楽しい理由【切り抜き】」35.2秒、private→2026-11-13T22:00Z。daulqJwmooE クリップ5985〜6065 の 21.9〜57.1秒。冒頭「若いうちはモテない方が人生楽しいですよ」（音声と一致、faster-whisper）。答え: モテると異性とのやり取りに人生を使い、それ以外の楽しみ方がなくなる。フルで見る→pSkBQyXIKWo（前日長尺）。**C①**（恋愛観）。crop=[600,0,690] 手動（自動だと顔が左に切れた）
- docs/growth-ledger.md: 実験B 1行・施策C 1行追記

## 検証済みの事実（API / コマンド出力）

- XnpPzG1ERco: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-13T22:00:00Z、概要欄1行目の問いかけ、フルで見る→pSkBQyXIKWo。フレーム 0.3/8/15/22/34.8秒で顔は枠内、最後に問いかけテロップ

## 未検証

- XnpPzG1ERco の全編通し視聴はしていない（API の duration は処理中で P0D）

## 次にやること

1. 夕方 11/13: YZVlJgnzMk0 関連→pSkBQyXIKWo、84oRUIoiUoI 関連→pSkBQyXIKWo、pSkBQyXIKWo の問いかけ固定・終了画面。夕方 11/14: XnpPzG1ERco 関連→pSkBQyXIKWo・問いかけ固定。653l90JxsV4 の関連動画→S_-Wjubw8sE は 11/16 公開後
2. 11/14（土）日次: 11/15 ショートのみ。長尺は昇格があれば次の空き 11/18（水）
3. 昇格判定: U0d9D_L-ps4（48h は 11/14 07:00）、YZVlJgnzMk0（11/15 07:00）、XnpPzG1ERco（11/16 07:00）
4. 施策C①: 今週（11/13〜）は XnpPzG1ERco の1本。週2〜3本まで
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 11/16 15:00 実験B 比較 routine、11/23 09:00 週次レビュー routine

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
