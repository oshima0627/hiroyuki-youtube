# HANDOFF
最終更新: 2026-10-15 12:20 JST（エンゲージメント施策を実装。手順は docs/engagement.md）

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
2. 未使用ブロック一覧: `work/_unused_1006.py` の出力先を変えて実行 → `work/_unused_1010.txt`（908件）。
3. レシピを recipes/ に作り `PYTHONPATH=. .venv/bin/python -c "from scripts.recipe import validate ..."` で検証。
4. **クリップ取得はボックスで可（2026-10-12〜）**: `PYTHONPATH=. .venv/bin/python scripts/fetch_clips.py recipes/<id>.json --browser none`。
   cookie 無しだと bestvideo が Premium の HLS（itag 616）を選んで書き出し0のまま止まるため、fetch_clips.py の -f を avc1 の HLS（270/232）+ m4a 優先に変更済み。6区間10分が約5分・1080p映像付きで取れた。
   取れなくなったら PC で `python scripts/fetch_clips.py recipes/<id>.json`（Firefox cookie）→ work/clips/*.mp4 を tar → CopyToBox。
5. ボックスで `build_episode.py` → `thumbnail.py` → `build_episode.py --concat-only`（冒頭カード）→ `upload_youtube.py work/<id> --schedule <UTC>`。Linux フォント対応（scripts/draw.py, contact_sheet.py）で問題なくビルドできた。
6. `ops_youtube.py --status` で private→publishAt を確認。

## 今回やったこと（2026-10-15）エンゲージメント施策（ユーザー承認済み）

- 新規: scripts/engagement.py（問いかけ文・禁止語・見送り目安）、scripts/engage.py（コメント投稿・返信・Studio 手作業記録）、docs/engagement.md、tests/test_engagement.py
- build_episode.py: 冒頭カードに問いかけ帯（3.5秒）、最後に終了画面用の板 outroimg.mp4（20秒、15分未満を守るため最短10秒まで縮む）。meta.json に engagement_question
- build_short.py: 最後の3.5秒に問いかけテロップ（下の黒帯のみ）
- upload_youtube.py: 概要欄の先頭行に問いかけ（publish_shorts も経由）。recipe.py: 任意フィールド engagement の検証
- 予約済み2本の概要欄先頭に問いかけ行を追加（engage.py --update-scheduled-descriptions）: hZCbbUwQVOI（10/15 18:30）、5UDR-8tVjAE（10/16 07:00）。公開状態・publishAt は不変を API で確認
- 既存動画へのコメント投稿は**していない**（夕方ルーチンから開始）。--list-unreplied は読み取りで動作確認（直近14日は0件、120日では4件）

## 日次ルーチン（追加分。詳細は docs/engagement.md）

- 朝: いつものビルド・予約でテロップ・終盤の板・概要欄1行目は自動。予約済みで行が無いものは `engage.py --update-scheduled-descriptions`
- 夕方: `engage.py --post <videoId>`（公開済みのみ）→ `engage.py --todo` を見て Studio で固定・終了画面（最後20秒）・ショートの関連動画 → `--done <id> pin|endscreen|related` → `engage.py --list-unreplied` を読んで `--reply-to <commentId> --text "1〜2文"`（20件/日まで）

## 前回やったこと（2026-10-14）

- 10/15 18:30 長尺 2026-10-15-kuruma → hZCbbUwQVOI「車と移動の話6連発。軽自動車は走る棺です」8:21、thumbnail_set=true
- フルで見る: 4CIkzIwtq5M → EY3dsQ3MUPY。未使用ブロック一覧は work/_unused_1014.txt（867件）
- 10/16 以降の長尺は未作成。ショート予約在庫は 10/16 朝07:00 JST まで

## 検証済みの事実

- pytest 36 passed（既存18＋新規18）
- status（2026-10-15 12:10 JST）: hZCbbUwQVOI private→2026-10-15T09:30Z、EY3dsQ3MUPY public
- 予約済み2本の概要欄先頭行を API で取り直して確認。hZCbbUwQVOI の最後 19.2 秒はまとめ板（終了画面用の余白板は無い。再アップロードはしない）
- ショートの最後テロップの ffmpeg フィルタは合成映像で確認。長尺の outroimg / 冒頭帯は kuruma の素材で /tmp に単体生成して目視
- 4CIkzIwtq5M description が EY3dsQ3MUPY を指す（API で取り直して確認）
- ショート予約在庫は 10/16 朝07:00 JST まで

## 未検証のもの

- 実レシピでの長尺・ショートのフルビルド（問いかけ入り）。次の長尺で初めて通る
- engage.py --post / --reply-to の実投稿（dry-run のみ）。commentThreads.insert の 403（コメント無効など）時の挙動

- ボックスで yt-dlp に cookies.txt を渡した場合の取得可否（未試行。cookie 無しで取れたので不要になった）
- ボックスでの fetch_source.py --subs-only

## 次にやること

1. 10/16 以降の長尺レシピ（使用済み: 車・旅行・防犯・食・ガジェット・お金 ほか。候補例: ペットと動物、見た目と美容。_unused_1014.py で再生成してから選ぶ）
2. cookie 無し取得が 403 等で再び落ちる場合のみ cookies.txt を検討（ユーザー判断が必要）
3. 夕方: hZCbbUwQVOI（10/15 18:30 公開）に `engage.py --post hZCbbUwQVOI` → Studio で固定。終了画面は最後のまとめ板に被るので要素を下段に小さめに置く
4. 夕方の関連動画紐づけ（Studio）。`engage.py --todo` に残りが出る

## 触ってはいけないところ

- 「公式」「公認」と書かない（定型の「公式チャンネルではありません」表記は除く）。政治的な話題は落とす
- 切り抜き禁止: exnFXUMMLLI / q0GyNI3X8cg。ゲスト共演回（IXiLxkgHUMM, naVkgtFmRvg, Sq1YChd0RqQ）は使わない
- 予約時刻を過ぎた publishAt を渡さない。15分以上は上げない
- _plan-kenko / _plan-kosodate / _plan-kigyo は使わない。note は clips[].note（20文字以上）
- Studio 関連動画は朝ルーチンで触らない
- 問いかけ・返信: 攻撃・政治・「公式/公認」・本人なりすまし・自作自演（いいね/登録/別アカウント）・報酬付き依頼は禁止。公開済み動画の概要欄は改変しない（予約済み分のみ可）
