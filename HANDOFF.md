# HANDOFF
最終更新: 2026-11-14 14:40 JST（11/14 日次）

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

## 今回やったこと（2026-11-14 日次）— 完了

- git pull → status: 11/14 07:00 XnpPzG1ERco 公開済、11/16 18:30 S_-Wjubw8sE 予約済。11/15 07:00 のショートは0本
- 昇格判定（14:30 JST）: 新規なし。U0d9D_L-ps4 は48h到達で1,229回→昇格なし。YZVlJgnzMk0（1,122回）は48h未達。施策C③により長尺は作らない
- 11/15 ショート recipes/shorts/2026-11-15-am.json → **Qk1k0JJCyAE**「【ひろゆき】人は自分より頭がいい人を嫌う？好きになるのは「弱み」が見えた時【切り抜き】」35.1秒、private→2026-11-14T22:00Z。0YyAgmv5_Yc クリップ4630〜4720 の 45.15〜80.25秒。冒頭「本質的に、自分より頭がいいやつは人は嫌いなんですよ」（音声一致、faster-whisper 4秒刻み。このクリップは word_timestamps がほぼ壊れたので w3/w4 方式＝work/tmp1114 で区間決め）。フルで見る→pSkBQyXIKWo（直近公開の長尺）。**C①**（恋愛／人間関係観）。crop は自動で顔が枠内
- docs/growth-ledger.md: 実験B 1行・施策C 1行追記

## 検証済みの事実（API / コマンド出力）

- Qk1k0JJCyAE: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-14T22:00:00Z、概要欄1行目の問いかけ、フルで見る→pSkBQyXIKWo。フレーム 0.3/10/20/33.5秒で顔は枠内、最後に問いかけテロップ

## 未検証

- Qk1k0JJCyAE の全編通し視聴はしていない

## 次にやること

1. 夕方 11/14: XnpPzG1ERco 関連→pSkBQyXIKWo・問いかけ固定。夕方 11/15: Qk1k0JJCyAE 関連→pSkBQyXIKWo・問いかけ固定。653l90JxsV4 の関連動画→S_-Wjubw8sE は 11/16 公開後
2. 11/15（日）日次: 11/16 ショートのみ。長尺は昇格があれば次の空き 11/18（水）
3. 昇格判定: YZVlJgnzMk0（48h は 11/15 07:00）、XnpPzG1ERco（11/16 07:00）、Qk1k0JJCyAE（11/17 07:00）
4. 施策C①: 今週（11/13〜）は XnpPzG1ERco・Qk1k0JJCyAE の2本。週3本まで。次はお金・仕事系を優先
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 11/16 15:00 実験B 比較 routine、11/23 09:00 週次レビュー routine

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
