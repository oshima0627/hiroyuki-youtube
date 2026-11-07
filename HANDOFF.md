# HANDOFF
- 11/7 日次: 11/8 ショート recipes/shorts/2026-11-08-am.json → **IzKdqd1Js2s**「【ひろゆき】国立大学を目指して勉強しても無理？努力しても受からないなら早く働く理由【切り抜き】」38秒（M7KWrHANxHs 8303.7〜8341.7）、private→2026-11-07T22:00Z、フルで見る→kdcGL3JwZSM。冒頭「あなたは国立理系に受かる能力はないです」。仕事・進学系。昇格: 93NkdAOx0uo（3,017→3,108回・48h超）→ 11/11 長尺 recipes/2026-11-11-taibatsu.json → **cvvBcBDKDHk**「【ひろゆき】注意しても止めないなら叩いていい？「相手のため」でも体罰が許されない理由」3:48、private→2026-11-11T09:30Z、cold open「体罰というのが許されるという社会で…」（0YyAgmv5_Yc 7895.2〜）、サムネ API 設定成功（maxres・スパチャ彩度警告あり）。93NkdAOx0uo のフルで見るを m4R7_9CT_o4→cvvBcBDKDHk に変更。11/9 長尺 t8Q5wQp7nPQ は予約済みのため作らない
最終更新: 2026-11-07 14:28 JST（11/7 日次）

## ▶ 最初に実行するコマンド（Linux ボックス）

```bash
cd /workspace/hiroyuki-youtube && PYTHONPATH=. python3 scripts/ops_youtube.py --status
curl -s 127.0.0.1:50021/version   # VOICEVOX 0.25.2（/workspace/voicevox）。返らなければ起動する
```

`.venv` は無い。`yt_dlp` は `/workspace/.ytvenv/bin/python` で `fetch_clips.py` を回す（`sys.executable -m yt_dlp` のため）。faster-whisper は `/workspace/wvenv`。

## いま何をしているのか

ひろゆき切り抜きチャンネル「ひろゆき解説ch【切り抜き】」(UCqK3KYqEeeJiAWr4nSryJYQ) の日次運用。
2026-10-10 から Linux ボックス（/workspace/hiroyuki-youtube）で回している。ASUS_i9 は使わない（fetch 失敗時だけ親が判断）。

## Linux ボックスでの手順

1. `work/` は git 管理外。字幕は work/_cap/*.ja.json3。未使用一覧は work/_unused_1102.py を日付更新して再生成。
2. レシピを recipes/ に作り検証。
3. **クリップ取得**: `PYTHONPATH=. /workspace/.ytvenv/bin/python scripts/fetch_clips.py recipes/<id>.json --browser none`
4. ショート: `PYTHONPATH=. python3 scripts/build_short.py` → `publish_shorts.py`。長尺: `build_episode.py`（`"opening": "cold"`）→ `thumbnail.py` → `upload_youtube.py work/<id> --schedule <UTC>`
5. `ops_youtube.py --status` で確認。サムネは `set_thumbnails.py --only <id> --force`

## 今回やったこと（2026-11-07 14:14 日次）— 完了

- git pull（up to date）。status: 当日ショート e3PGAJ1kFSs 公開済、11/9 長尺 t8Q5wQp7nPQ 予約済。11/8 ショートは 0 本だった
- 昇格判定: **93NkdAOx0uo** は 3,017回・11/5 07:00公開で 11/7 07:00 に48時間到達 → **昇格**（次枠 11/11 水）。QC24A3gd2jc 1,404・2lmeaIMPp-c 1,246・84oRUIoiUoI 1,835（48hは11/8 07:00）は対象外。qY_hj45hxC0 / oUt6kcCwW5c は昇格済
- 11/8 ショート recipes/shorts/2026-11-08-am.json → **IzKdqd1Js2s**「国立大学を目指して勉強しても無理？…」38秒、private→2026-11-07T22:00Z。0秒目「あなたは国立理系に受かる能力はないです」（M7KWrHANxHs 8303.7）。フルで見る→kdcGL3JwZSM。仕事・進学系
- 11/11（水）長尺 recipes/2026-11-11-taibatsu.json → **cvvBcBDKDHk**「注意しても止めないなら叩いていい？…」3:48、private→2026-11-11T09:30Z。0YyAgmv5_Yc 体罰相談の深掘り（cold 7895.2〜7907.5 / 7880〜7895.2 / 7895.2〜7932）。サムネ at 8・crop [0.40,0.05,0.55]、API で maxres。スパチャカードが下端に残るため彩度警告あり
- 93NkdAOx0uo のフルで見るを m4R7_9CT_o4→cvvBcBDKDHk。recipes/shorts/2026-11-05-am.json の parent も更新
- 実験B: 両本とも faster-whisper で0秒目確認。11/9 t8Q5wQp7nPQ は既存のためスキップ

## 次にやること

1. 11/8（日）の日次: 長尺枠なし（次は 11/9・11/11 予約済み、その次 11/13 金）。11/9 ショートを作る（フルで見る→kdcGL3JwZSM、または 11/9 公開後は t8Q5wQp7nPQ）。実験B 継続
2. 夕方 11/7: e3PGAJ1kFSs の関連動画→kdcGL3JwZSM（または公開済み長尺）、問いかけコメント固定。夕方 11/8: IzKdqd1Js2s→kdcGL3JwZSM。11/11 公開後に 93NkdAOx0uo 関連→cvvBcBDKDHk・終了画面
3. 昇格判定: 84oRUIoiUoI は 11/8 07:00 以降に 1,700 超なら候補。e3PGAJ1kFSs も見る
4. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
5. 11/11 比較、11/16 15:00 実験B 比較 routine

## 検証済みの事実

- IzKdqd1Js2s: API で publishAt 2026-11-07T22:00:00Z、フルで見る→kdcGL3JwZSM、概要欄1行目の問いかけを確認
- cvvBcBDKDHk: API で publishAt 2026-11-11T09:30:00Z、概要欄1行目の問いかけ、サムネ maxres、尺 3:48
- 93NkdAOx0uo: フルで見る→cvvBcBDKDHk を API で確認
- fetch は `/workspace/.ytvenv/bin/python`（system python3 には yt_dlp が無い）
- /workspace/wvenv の faster-whisper は wav を numpy で渡す。small で十分なことも

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
