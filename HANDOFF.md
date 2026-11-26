# HANDOFF
最終更新: 2026-11-26 15:00 JST（11/26 日次）

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

## 今回やったこと（2026-11-26 日次）— 完了

- git pull（変更なし）→ status（14:20 JST）: 11/26 07:00 Ft6HR0-36rA 公開済、11/26 18:00 oXeLGa2taWo は private→2026-11-26T09:00Z で予約済。11/27 の am/pm は0本だった。直近の長尺は wpmnSdP8VNQ（11/18）
- 昇格判定: 48h超で1,700回超の未昇格ショートなし（1,700回超は oUt6kcCwW5c/qY_hj45hxC0/93NkdAOx0uo/84oRUIoiUoI/653l90JxsV4/XnpPzG1ERco で全部昇格済）。未昇格の最大は CfPbeHlWoP8 1,470回、次いで QC24A3gd2jc 1,423回・IzKdqd1Js2s 1,403回。直近週は Ke2zw5ZPiA0 1,398回・6cq_CVu_sz8 1,393回・Jy27D8k9HwE 1,379回。11/27(金)の長尺は作らず。次の枠は 11/30(月)
- 11/27 am recipes/shorts/2026-11-27-am.json → **HYAvZDgu2mI**「【ひろゆき】子供を作ることと育てることは分けていい？育てられないなら養子・里親に回した方がいいと考える理由【切り抜き】」41.3秒、private→2026-11-26T22:00Z。a3zM5hCv-Uo クリップ560〜680 の 29.75〜71.0秒。C①（11/23週3本目＝上限）。crop [650,40,690]。フルで見る→wpmnSdP8VNQ
- 11/27 pm recipes/shorts/2026-11-27-pm.json → **7boaNmXZUoQ**「【ひろゆき】暗記力は社会に出たらいらない？受験勉強の「覚える力」より検索で答えを出す力が大事な理由【切り抜き】」39.5秒、private→2026-11-27T09:00Z（18:00 JST）。6Pg_wE6hX7w クリップ1640〜1730 の 30.15〜69.6秒。どちらでもない枠（勉強・学び方）。crop [700,100,800]＋自動黒帯151。フルで見る→wpmnSdP8VNQ
- 両方とも概要欄2行目に相談内容・話の範囲を手で補足してからアップ。サムネはショートなので対象外
- docs/growth-ledger.md: 実験B 2行・施策C 1行（C①）・施策D 1行（pm）
- 11/23週（11/23〜11/29公開）の集計: C① 3本（Jy27D8k9HwE, 6cq_CVu_sz8, HYAvZDgu2mI）＝上限、仕事/お金枠 3本（adtWAjiQlnQ, Z577uA8RdyY, Ft6HR0-36rA）＝上限 → 11/28・11/29 公開分はどちらでもない題材だけ

## 検証済みの事実（API / コマンド出力）

- HYAvZDgu2mI / 7boaNmXZUoQ: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-26T22:00:00Z / 2026-11-27T09:00:00Z、概要欄1行目は二択の問いかけ、フルで見る→wpmnSdP8VNQ（API）
- 出力音声 faster-whisper: am 冒頭「なので僕はあの子どもを作ることと育てることというのは分離しちゃっていいと思ってるんですよね」末尾「あんまりなんか社会はそういう方向に動いてないですよね」。pm 冒頭「ただ、暗記能力っていうのは、社会に出るとなくても全く困んないって」末尾「これまじで誤解なんですよ」。確認画像 work/tmp1127/d_am.png・d_pm.png（3秒ごと）

## 未検証

- 2本とも全編通し視聴はしていない（3秒ごとのコマと音声書き起こしで確認）
- pytest は box に pytest が無く未実行

## 次にやること

1. 夕方 11/26: Ft6HR0-36rA（am）、Z577uA8RdyY（前日 pm）。oXeLGa2taWo（18:00）は 11/27 夕方
2. 夕方 11/27: HYAvZDgu2mI（am）、oXeLGa2taWo（前日 pm）。7boaNmXZUoQ（18:00）は 11/28 夕方
3. 11/27（金）日次: 11/28 の am と pm。今週は C①・仕事/お金枠とも上限。どちらでもない題材のみ
4. 昇格判定: 6cq_CVu_sz8（48h は 11/27 07:00）、Z577uA8RdyY（11/27 18:00）、Ft6HR0-36rA（11/28 07:00）、oXeLGa2taWo（11/28 18:00）、HYAvZDgu2mI（11/29 07:00）、7boaNmXZUoQ（11/29 18:00）。次の昇格長尺枠は 11/30(月)18:30（11/27〜11/29 の日次で判定）
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 題材探し: work/_kw.py "<正規表現>"、work/_peek.py <動画ID> <開始> <終了>、未使用一覧 `PYTHONPATH=. python3 work/_unused_1102.py`。単語タイムスタンプは `/workspace/wvenv/bin/python work/tmp1108/ww.py <wav> <開始> <終了>`。未使用候補メモ: EXUXJaPlKmE 約6809〜6896秒（集中力を上げる方法？「ないです」→目的のために仕方なくやる。連続区間だと50秒超で今回見送り。クリップ work/clips/EXUXJaPlKmE_6790-6910.mp4 取得済み）、0YyAgmv5_Yc 約3420〜3532秒（詰める話し方→口頭よりテキスト）、ISHh67atXTI 約7441〜7555秒（仲良くないグループに入らなくていい・ぼっちで良くない？）

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
