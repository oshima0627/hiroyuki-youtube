# HANDOFF
最終更新: 2026-10-15 14:35 JST（日次ops: 10/16 資格とキャリア長尺を18:30予約）

## ▶ 最初に実行するコマンド（Linux ボックス）

```bash
cd /workspace/hiroyuki-youtube && .venv/bin/python scripts/ops_youtube.py --status
curl -s 127.0.0.1:50021/version   # VOICEVOX 0.25.2（/workspace/voicevox）。返らなければ起動する
```

## いま何をしているのか

ひろゆき切り抜きチャンネル「ひろゆき解説ch【切り抜き】」(UCqK3KYqEeeJiAWr4nSryJYQ) の日次運用。
2026-10-10 から Linux ボックス（/workspace/hiroyuki-youtube）で回し始めた。PC（ASUS_i9, C:\Users\oshim\Documents\projects\hiroyuki-youtube）は素材取得だけに使った。

## Linux ボックスでの手順（2026-10-10 実績）

1. `work/` は git 管理外。候補探しに必要な字幕・メタ（work/**/*.json, *.txt, *.py、約5MB zip）は PC から tar で CopyToBox して展開した。新しい配信を候補に足すときは fetch_source.py --subs-only（ボックスで未検証）か PC から再コピー。
2. 未使用ブロック一覧: `work/_unused_1014.py` の出力先を変えて実行 → `work/_unused_1014.txt`（再生成で更新）。
3. レシピを recipes/ に作り `PYTHONPATH=. .venv/bin/python -c "from scripts.recipe import validate ..."` で検証。
4. **クリップ取得はボックスで可（2026-10-12〜）**: `PYTHONPATH=. .venv/bin/python scripts/fetch_clips.py recipes/<id>.json --browser none`。
   cookie 無しだと bestvideo が Premium の HLS（itag 616）を選んで書き出し0のまま止まるため、fetch_clips.py の -f を avc1 の HLS（270/232）+ m4a 優先に変更済み。
   取れなくなったら PC で `python scripts/fetch_clips.py recipes/<id>.json`（Firefox cookie）→ work/clips/*.mp4 を tar → CopyToBox。
5. ボックスで `build_episode.py` → `thumbnail.py` → `build_episode.py --concat-only`（冒頭カード）→ `upload_youtube.py work/<id> --schedule <UTC>`。
6. `ops_youtube.py --status` で private→publishAt を確認。サムネは `set_thumbnails.py --only <id>`（必要なら `--force`）。

## 今回やったこと（2026-10-15 14:13 日次）

- 当日ショート u_vN9xYpzyI（すぐ辞めたくなる性格は直すべきか・公開済）既存スキップ
- 当日長尺 hZCbbUwQVOI（車と移動・10/15 18:30 JST＝09:30Z）既存スキップ
- 翌日ショート 5UDR-8tVjAE（復職に引っ越し・10/16 07:00 JST）既存
- **新規** 翌日長尺 2026-10-16-shikaku → Mw4CM0_gFhw「資格とキャリアの話7連発。エンジニアで優秀なやつは試験を受けません」9:40、18:30 JST（09:30Z）予約、thumbnail_set=true（差分0.8で確認）
- フルで見る: 4CIkzIwtq5M → EY3dsQ3MUPY は既に設定済みのため変更なし
- エンゲージメント: 概要欄1行目・冒頭/終盤テロップは新規長尺に自動入り。Studio関連動画・コメント固定は夕方ルーチン
- 未使用ブロック再生成: work/_unused_1014.txt（852件）

## 前回やったこと（2026-10-15 昼）エンゲージメント施策

- scripts/engagement.py / engage.py、docs/engagement.md、tests/test_engagement.py
- 予約済み2本の概要欄先頭に問いかけ行: hZCbbUwQVOI、5UDR-8tVjAE

## 検証済みの事実

- status（2026-10-15 14:33 JST）: Mw4CM0_gFhw private→2026-10-16T09:30Z 9M40S、hZCbbUwQVOI private→2026-10-15T09:30Z、5UDR-8tVjAE private→2026-10-15T22:00Z
- 4CIkzIwtq5M description が EY3dsQ3MUPY を指す（変更なし）
- cookie 無し fetch_clips 7区間成功（403 再試行ありだが完了）
- ショート予約在庫は 10/16 朝07:00 JST まで。10/17 以降の長尺・ショートは未作成

## 次にやること

1. 10/17 以降の長尺・ショート在庫（候補: ペットと動物、見た目と美容、酒と飲み物。_unused 再生成してから選ぶ）
2. 夕方: hZCbbUwQVOI（10/15 18:30 公開）に `engage.py --post hZCbbUwQVOI` → Studio で固定・終了画面・関連動画（当日ショート u_vN9xYpzyI ← 当日長尺 hZCbbUwQVOI）
3. cookie 無し取得が再び落ちる場合のみ cookies.txt を検討

## 触ってはいけないところ

- 「公式」「公認」と書かない（定型の「公式チャンネルではありません」表記は除く）。政治的な話題は落とす
- 切り抜き禁止: exnFXUMMLLI / q0GyNI3X8cg。ゲスト共演回（IXiLxkgHUMM, naVkgtFmRvg, Sq1YChd0RqQ）は使わない
- 予約時刻を過ぎた publishAt を渡さない。15分以上は上げない
- _plan-kenko / _plan-kosodate / _plan-kigyo は使わない。note は clips[].note（20文字以上）
- Studio 関連動画は朝ルーチンで触らない
- 問いかけ・返信: 攻撃・政治・「公式/公認」・本人なりすまし・自作自演（いいね/登録/別アカウント）・報酬付き依頼は禁止。公開済み動画の概要欄は改変しない（予約済み分のみ可）
