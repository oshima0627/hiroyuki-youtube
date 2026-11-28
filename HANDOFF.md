# HANDOFF
最終更新: 2026-11-28 15:00 JST（11/28 日次）

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

## 今回やったこと（2026-11-28 日次）— 完了

- git pull（変更なし）→ status（14:20 JST）: 11/28 07:00 kEbupEl42lU 公開済、11/28 18:00 6Rw-d__b-Fk は private→2026-11-28T09:00Z で予約済。11/29 の am/pm は0本だった。直近の長尺は wpmnSdP8VNQ（11/18）
- 昇格判定: 48h超で1,700回超の未昇格ショートなし。48h超の未昇格の最大は CfPbeHlWoP8 1,470回、直近週では 6cq_CVu_sz8 1,430回。HYAvZDgu2mI は 1,520回だが 48h 未満（11/29 07:00 で48h）。長尺は作らず
- 11/29 am recipes/shorts/2026-11-29-am.json → **5XVkUCg8T5Y**「【ひろゆき】自己肯定感はどうすれば上がる？「トカゲを捕まえるのがうまい」と思い込める方が自己肯定感は上がる理由【切り抜き】」41.9秒、private→2026-11-28T22:00Z。5wwIeF3KgbU クリップ9340〜9420 の 22.2〜64.1秒（元動画 約9362.3秒〜）。どちらでもない枠。crop [650,90,690]。フルで見る→wpmnSdP8VNQ
- 11/29 pm recipes/shorts/2026-11-29-pm.json → **yinIpQdRK0Q**「【ひろゆき】眠いのに無理して早起きするべき？「無意識の方が賢い」から寝ることを選ぶと考える理由【切り抜き】」40.3秒、private→2026-11-29T09:00Z（18:00 JST）。PQzUcVHWNJ8 クリップ5330〜5420 の 22.1〜62.4秒（元動画 約5352.2秒〜）。どちらでもない枠。crop [820,90,700]。フルで見る→wpmnSdP8VNQ
- 両方とも概要欄2行目に話の範囲を手で補足してからアップ
- docs/growth-ledger.md: 実験B 2行・施策D 1行（pm）。C①なし

## 検証済みの事実（API / コマンド出力）

- 5XVkUCg8T5Y / yinIpQdRK0Q: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-28T22:00:00Z / 2026-11-29T09:00:00Z、概要欄1行目は二択の問いかけ、フルで見る→wpmnSdP8VNQ（API、アップ直後は duration P0D＝処理中）
- 出力音声 faster-whisper: am 冒頭「で僕が自己肯定感が強かった…トカゲを捕まえるのがうまいと思い込んでいることと」末尾「人ってね思い込みなんです」。pm 冒頭「一般の人よりは僕は無意識を尊重してますね」末尾「お風呂入るの面倒くさいからお風呂入らない」。確認画像 work/tmp1129/d_am.png・d_pm.png（3秒ごと）

## 未検証

- 2本とも全編通し視聴はしていない（3秒ごとのコマと音声書き起こしで確認）
- pytest は box に pytest が無く未実行

## 次にやること

1. 夕方 11/28: kEbupEl42lU（am）、7boaNmXZUoQ（前日 pm）。6Rw-d__b-Fk（18:00）は 11/29 夕方
2. 夕方 11/29: 5XVkUCg8T5Y（am）、6Rw-d__b-Fk（前日 pm）。yinIpQdRK0Q（18:00）は 11/30 夕方
3. 11/29（日）日次: 11/30 の am と pm。11/30〜は新しい週（11/30週）で C①・仕事/お金枠の本数はリセット
4. 昇格判定: HYAvZDgu2mI（48h は 11/29 07:00・11/28 時点 1,520回）、7boaNmXZUoQ（11/29 18:00）、kEbupEl42lU（11/30 07:00）、6Rw-d__b-Fk（11/30 18:00）、5XVkUCg8T5Y（12/1 07:00）、yinIpQdRK0Q（12/1 18:00）。次の昇格長尺枠は 11/30(月)18:30（11/29 の日次で判定。過ぎたら次は 12/2(水)）
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 題材探し: work/_kw.py "<正規表現>"、work/_peek.py <動画ID> <開始> <終了>、未使用一覧 `PYTHONPATH=. python3 work/_unused_1102.py`。単語タイムスタンプは `/workspace/wvenv/bin/python work/tmp1108/ww.py <wav> <開始> <終了>`（wav は mp4 から作るので t=0 はクリップ開始の2秒前。short.start = wav秒 − 2）。未使用候補メモ: 0YyAgmv5_Yc 約3420〜3464秒（部下を詰める話し方→仕事枠扱い）、cqCJYrPrdAA 約5108〜5144秒（天才は本人ではなく社会の評価で決まる。一言が答えの末尾にあるので冒頭に置けず今回は見送り、35秒に届くか要確認）、5wwIeF3KgbU 約1436〜1466秒（調べ物は人に聞かず自分で調べる、人もAIも嘘をつく。約30秒で短い）、6Pg_wE6hX7w 約3220〜3262秒（アルコールは毒、百薬の長は嘘。健康の話なので断定に注意）

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
