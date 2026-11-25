# HANDOFF
最終更新: 2026-11-25 15:10 JST（11/25 日次）

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

## 今回やったこと（2026-11-25 日次）— 完了

- git pull（変更なし）→ status（14:20 JST）: 11/25 07:00 6cq_CVu_sz8 公開済、11/25 18:00 Z577uA8RdyY は private→2026-11-25T09:00Z で予約済。11/26 の am/pm は0本だった。直近の長尺は wpmnSdP8VNQ（11/18）
- 昇格判定: 48h超で1,700回超の未昇格ショートなし（1,700回超は oUt6kcCwW5c/qY_hj45hxC0/93NkdAOx0uo/84oRUIoiUoI/653l90JxsV4/XnpPzG1ERco で全部昇格済）。未昇格の最大は CfPbeHlWoP8 1,470回、次いで QC24A3gd2jc 1,423回・IzKdqd1Js2s 1,401回。直近週は Ke2zw5ZPiA0 1,392回・Jy27D8k9HwE 1,367回（48h超）。長尺は作らず（11/25 水 は見送り、次は 11/27 金→昇格なしなら 11/30 月）
- 11/26 am recipes/shorts/2026-11-26-am.json → **Ft6HR0-36rA**「【ひろゆき】育休中に転職活動・副業準備はすべき？年収700万なら大手に残り続けた方がいい理由【切り抜き】」41.1秒、private→2026-11-25T22:00Z。pUsi5NQQgrA クリップ3030〜3100 の 18.5〜59.6秒。仕事/お金枠（11/23週3本目＝上限）。crop [560,0,760]＋自動黒帯145（スパチャカード）。フルで見る→wpmnSdP8VNQ
- 11/26 pm recipes/shorts/2026-11-26-pm.json → **oXeLGa2taWo**「【ひろゆき】挨拶を強要される文化が嫌なら、挨拶しなくていい？ひろゆきが「挨拶ぐらいした方が楽」と考える理由【切り抜き】」41.8秒、private→2026-11-26T09:00Z（18:00 JST）。0YyAgmv5_Yc クリップ2050〜2170 の 52.45〜94.25秒。どちらでもない枠。crop [600,0,800]、cover 0（自動検出が誤検出するので明示）。フルで見る→wpmnSdP8VNQ
- 両方とも概要欄2行目に相談内容を手で補足してからアップ。サムネはショートなので対象外
- docs/growth-ledger.md: 実験B 2行・施策D 適用ログ1行（pm）。C① は作っていないので施策C ログなし
- 11/23週（11/23〜11/29公開）の集計: C① 2本（Jy27D8k9HwE, 6cq_CVu_sz8）＝あと1本、仕事/お金枠 3本（adtWAjiQlnQ, Z577uA8RdyY, Ft6HR0-36rA）＝上限

## 検証済みの事実（API / コマンド出力）

- Ft6HR0-36rA / oXeLGa2taWo: channel UCqK3KYqEeeJiAWr4nSryJYQ、private、publishAt 2026-11-25T22:00:00Z / 2026-11-26T09:00:00Z、概要欄1行目は二択の問いかけ、フルで見る→wpmnSdP8VNQ（API。duration は処理中で P0D）
- 出力音声 faster-whisper: am 冒頭「なので下手に副業準備とか転職活動するより、その大手グループにちゃんと残り続けた方がいいと思いますよ」末尾「大手企業に残り続けた方がいいんじゃないかなと思う」。pm 冒頭「なのでその不便を受け止める覚悟があるんだったら別に挨拶しなくていいと思うんですよ」末尾「挨拶ぐらいした方が楽だよ人生って僕は思いますけどね」。確認画像 work/tmp1126/v2.png

## 未検証

- 2本とも全編通し視聴はしていない
- pytest は box に pytest が無く未実行

## 次にやること

1. 夕方 11/25: 6cq_CVu_sz8（am）、gkdeigFmqug（前日 pm）。Z577uA8RdyY（18:00）は 11/26 夕方
2. 夕方 11/26: Ft6HR0-36rA（am）、Z577uA8RdyY（前日 pm）。oXeLGa2taWo（18:00）は 11/27 夕方
3. 11/26（木）日次: 11/27 の am と pm。今週は仕事/お金枠が上限、C① はあと1本。残りはどちらでもない題材
4. 昇格判定: adtWAjiQlnQ（48h は 11/26 07:00）、gkdeigFmqug（11/26 18:00）、6cq_CVu_sz8（11/27 07:00）、Z577uA8RdyY（11/27 18:00）、Ft6HR0-36rA（11/28 07:00）、oXeLGa2taWo（11/28 18:00）。次の昇格長尺枠は 11/27(金)18:30（11/26 日次で判定）、その次 11/30(月)
5. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
6. 題材探し: work/_kw.py "<正規表現>"、work/_peek.py <動画ID> <開始> <終了>、未使用一覧 `PYTHONPATH=. python3 work/_unused_1102.py`（行頭 R はリスク判定で、政治以外なら使える場合あり。例: 挨拶の回）。単語タイムスタンプは `/workspace/wvenv/bin/python work/tmp1108/ww.py <wav> <開始> <終了>`。未使用候補メモ: EXUXJaPlKmE 約336〜382秒（大人がアニメにハマるのは？教養の話。単独区間だと43秒超で今回見送り）、0YyAgmv5_Yc 約3420〜3532秒（詰める話し方→口頭よりテキスト）、M7KWrHANxHs 約6105〜6145秒（予約が埋まってるなら雑談力はいらない・仕事枠）

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止。過去日時の publishAt 禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
- client_secret.json / token.json はコミットしない
