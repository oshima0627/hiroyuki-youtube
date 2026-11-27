# HANDOFF
最終更新: 2026-11-27 15:00 JST（11/27 日次）

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

## 今回やったこと（2026-11-27 日次）— 完了

- git pull（変更なし）→ status（14:20 JST）: 11/27 07:00 HYAvZDgu2mI 公開済、11/27 18:00 7boaNmXZUoQ は private→2026-11-27T09:00Z で予約済。11/28 の am/pm は0本だった。直近の長尺は wpmnSdP8VNQ（11/18）
- 昇格判定: 48h超で1,700回超の未昇格ショートなし。未昇格の最大は CfPbeHlWoP8 1,470回（変わらず）。直近週の48h超は 6cq_CVu_sz8 1,414回が最大。長尺は作らず。次の枠は 11/30(月)18:30
- 11/28 am recipes/shorts/2026-11-28-am.json → **kEbupEl42lU**「【ひろゆき】集中力を上げる方法はある？49歳のひろゆきが「テクニックはない、興味がないと続かない」と言い切る理由【切り抜き】」37.8秒、private→2026-11-27T22:00Z。EXUXJaPlKmE クリップ6790〜6910 の 18.85〜56.6秒（元動画 約6808.9秒〜）。どちらでもない枠。crop [600,100,640]＋自動黒帯151（スパチャの質問文＝ADHD・服薬の話を隠す）。フルで見る→wpmnSdP8VNQ
- 11/28 pm recipes/shorts/2026-11-28-pm.json → **6Rw-d__b-Fk**「【ひろゆき】仲良くない友達グループに合わせるべき？嫌な人と付き合わなくていい、「別にぼっちで良くない？」と考える理由【切り抜き】」41.7秒、private→2026-11-28T09:00Z（18:00 JST）。ISHh67atXTI クリップ7430〜7500 の 5.6〜47.3秒（元動画 約7435.7秒〜）。どちらでもない枠。crop [600,120,680]。フルで見る→wpmnSdP8VNQ
- 両方とも概要欄2行目に話の範囲を手で補足してからアップ。フックは1行（または2行）に収まる長さにしないと3行目が消える（render_frame は2行まで）
- docs/growth-ledger.md: 実験B 2行・施策D 1行（pm）。C①なし

## 検証済みの事実（API / コマンド出力）

- kEbupEl42lU / 6Rw-d__b-Fk: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-27T22:00:00Z / 2026-11-28T09:00:00Z、概要欄1行目は二択の問いかけ、フルで見る→wpmnSdP8VNQ（API）
- 出力音声 faster-whisper: am 冒頭「集中力を上げる…ないでしょうか ないです あの僕も未だにありません」末尾「テクニック…あるんだったらいいんですけどないです」。pm 冒頭「嫌な奴と付き合わなければいけないっていう呪いは…」末尾「いや別にぼっちでよくない」。確認画像 work/tmp1128/d_am.png・d_pm.png（3秒ごと）

## 未検証

- 2本とも全編通し視聴はしていない（3秒ごとのコマと音声書き起こしで確認）
- pytest は box に pytest が無く未実行

## 次にやること

1. 夕方 11/27: HYAvZDgu2mI（am）、oXeLGa2taWo（前日 pm）。7boaNmXZUoQ（18:00）は 11/28 夕方
2. 夕方 11/28: kEbupEl42lU（am）、7boaNmXZUoQ（前日 pm）。6Rw-d__b-Fk（18:00）は 11/29 夕方
3. 11/28（土）日次: 11/29 の am と pm。11/23週は C①・仕事/お金枠とも上限なので 11/29 公開分もどちらでもない題材のみ。11/30〜は新しい週（11/30週）でリセット
4. 昇格判定: Z577uA8RdyY（48h は 11/27 18:00）、Ft6HR0-36rA（11/28 07:00）、oXeLGa2taWo（11/28 18:00）、HYAvZDgu2mI（11/29 07:00）、7boaNmXZUoQ（11/29 18:00）、kEbupEl42lU（11/30 07:00）、6Rw-d__b-Fk（11/30 18:00）。次の昇格長尺枠は 11/30(月)18:30（11/28〜11/29 の日次で判定。11/29 を過ぎたら次は 12/2(水)）
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 題材探し: work/_kw.py "<正規表現>"、work/_peek.py <動画ID> <開始> <終了>、未使用一覧 `PYTHONPATH=. python3 work/_unused_1102.py`。単語タイムスタンプは `/workspace/wvenv/bin/python work/tmp1108/ww.py <wav> <開始> <終了>`（wav は mp4 から作るので t=0 はクリップ開始の2秒前。short.start = wav秒 − 2）。未使用候補メモ: 0YyAgmv5_Yc 約3420〜3464秒（部下を詰める話し方→口頭よりテキストで。職場の話なので仕事枠扱いが無難）、EXUXJaPlKmE 約6836〜6896秒（勉強は「目的のために仕方なくやる」の続き。今回の kEbupEl42lU の直後なので別疑問として使うなら間隔をあける）

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
