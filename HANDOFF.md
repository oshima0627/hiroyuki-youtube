# HANDOFF
- 11/6 日次: 11/7 ショート recipes/shorts/2026-11-07-am.json → **e3PGAJ1kFSs**「【ひろゆき】銀行の残高は税務署に筒抜け？マイナポイントより怖い現実【切り抜き】」40秒（0YyAgmv5_Yc 2464.9〜2504.5）、private→2026-11-06T22:00Z、フルで見る→kdcGL3JwZSM（API確認）。crop [730,0,802] cover 119。概要欄に税金・口座の一般論注記をAPI追加。11/9（月）長尺 recipes/2026-11-09-shikaku.json → **t8Q5wQp7nPQ**「【ひろゆき】資格試験は1回で受かる？点数を上げるコツと「範囲を捨てる」技術」6:54、private→2026-11-09T09:30Z、cold open「試験って何回受けてもいいんですよ」（EXUXJaPlKmE 3104.9〜）、サムネ API 設定成功（maxres）。昇格なし（93NkdAOx0uo は11/7 07:00で48時間）。長尺 kdcGL3JwZSM は当日18:30予約済みのため作らない
最終更新: 2026-11-06 14:35 JST（11/6 日次）

## ▶ 最初に実行するコマンド（Linux ボックス）

```bash
cd /workspace/hiroyuki-youtube && .venv/bin/python scripts/ops_youtube.py --status
curl -s 127.0.0.1:50021/version   # VOICEVOX 0.25.2（/workspace/voicevox）。返らなければ起動する
```

## いま何をしているのか

ひろゆき切り抜きチャンネル「ひろゆき解説ch【切り抜き】」(UCqK3KYqEeeJiAWr4nSryJYQ) の日次運用。
2026-10-10 から Linux ボックス（/workspace/hiroyuki-youtube）で回している。ASUS_i9 は使わない（fetch 失敗時だけ親が判断）。

## Linux ボックスでの手順

1. `work/` は git 管理外。字幕は work/_cap/*.ja.json3。未使用一覧は work/_unused_1102.py を日付更新して再生成。
2. レシピを recipes/ に作り検証。
3. **クリップ取得**: `PYTHONPATH=. .venv/bin/python scripts/fetch_clips.py recipes/<id>.json --browser none`
4. ショート: `build_short.py` → `publish_shorts.py`（PYTHONPATH 不要になった）。長尺: `build_episode.py`（`"opening": "cold"`）→ `thumbnail.py` → `upload_youtube.py work/<id> --schedule <UTC>`
5. `ops_youtube.py --status` で確認。サムネは `set_thumbnails.py --only <id> --force`

## 今回やったこと（2026-11-06 14:15 日次）— 完了

- git 最新（8c00319）。status: 当日ショート 84oRUIoiUoI 公開済、当日長尺 kdcGL3JwZSM（private→11/6 18:30）。11/7 ショート・11/9 長尺は 0 本だった
- 昇格判定: 93NkdAOx0uo は 2,059回だが 11/5 07:00 公開で48時間到達は 11/7 07:00 → **昇格なし**。qY_hj45hxC0 / oUt6kcCwW5c は昇格済。QC24A3gd2jc・2lmeaIMPp-c は閾値未満
- 11/7 ショート recipes/shorts/2026-11-07-am.json → **e3PGAJ1kFSs**「銀行の残高は税務署に筒抜け？…」40秒、private→2026-11-06T22:00Z。0秒目「税務署に聞かれたら100%答えます」（0YyAgmv5_Yc 2464.9）。フルで見る→kdcGL3JwZSM。お金系（今週は既に4本あるが検索語として可）。crop [730,0,802] cover 119
- 11/9（月）長尺 recipes/2026-11-09-shikaku.json → **t8Q5wQp7nPQ**「資格試験は1回で受かる？…」6:54、private→2026-11-09T09:30Z。EXUXJaPlKmE 簿記3級相談の深掘り（cold 3104.9〜3111.5 / 3086〜3129.5 / 3129.7〜3190.7 / 3191〜3290）。サムネ at 300・crop [0.40,0.05,0.55]、API で maxres 設定。スパチャカードが下端に残るため彩度警告あり（顔は入っている）
- 実験B: 両本とも faster-whisper で0秒目音声とテロップ一致を確認。長尺の初回切り出しは 3106.4 始まりで「何回〜」からになり不一致→3104.9 に直して再ビルド
- fetch_clips は --browser none で成功（長尺の追加1区間は既存 3086-3129 から pad 付き切り出し）

## 次にやること

1. 11/7（金）の日次: 長尺枠なし（次は 11/9 予約済み、その次 11/11 水）。11/8 ショートを作る（フルで見る→kdcGL3JwZSM または 11/9 長尺 t8Q5wQp7nPQ 公開後はそちら）。実験B 継続
   夕方 11/6: qY_hj45hxC0→kdcGL3JwZSM、84oRUIoiUoI→kdcGL3JwZSM、kdcGL3JwZSM の固定コメント・終了画面。夕方 11/7: e3PGAJ1kFSs の関連動画→kdcGL3JwZSM（または公開済み長尺）
2. 昇格判定: 93NkdAOx0uo は 11/7 07:00 以降に 1,700 回超なら昇格候補。QC24A3gd2jc（11/3）・2lmeaIMPp-c（11/4）も見る
3. 不要な private 動画 QN24TFpO6jk の削除はユーザー確認後
4. 11/11 比較、11/16 15:00 実験B 比較 routine

## 検証済みの事実

- e3PGAJ1kFSs: API で publishAt 2026-11-06T22:00:00Z、フルで見る→kdcGL3JwZSM、概要欄1行目の問いかけと税金注記を確認
- t8Q5wQp7nPQ: API で publishAt 2026-11-09T09:30:00Z、概要欄1行目の問いかけ、サムネ maxres、尺 6:54（ビルド時）
- /workspace/wvenv の faster-whisper は wav を numpy で渡す（av 版ずれ）。large-v3 はメモリ不足になることがある→small で十分なことも

## 触ってはいけないところ

- 禁止プラン: _plan-kenko / _plan-kosodate / _plan-kigyo
- 政治禁止。「公式」「公認」禁止。偽エンゲージメント禁止
- Google からサインアウトしない・Cookie/プロファイルを消さない。セッション切れはユーザーに伝える
- /tmp は他 bot と衝突するので確認画像は work/ 内へ
