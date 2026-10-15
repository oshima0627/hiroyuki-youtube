# エンゲージメント施策の運用（2026-10-15〜）

コメント・視聴継続を増やすための仕組み。ユーザー承認済み（2026-10-15）。

## 何が入っているか

| 場所 | 中身 | 実装 |
|---|---|---|
| 長尺の冒頭 | 冒頭カード（サムネ静止画、3.5秒）に問いかけ帯 | build_episode.py `build_head` |
| 長尺の終盤 | 最後に「最後にひとつ質問です」板（読み上げ＋無音で **20秒**）。下 6 割は終了画面の要素用に空けてある | build_episode.py `build_outro` / telop.py `render_outro` |
| ショートの最後 | 最後の 3.5 秒、下の補足欄を問いかけに差し替え | build_short.py `render_end_line` |
| 概要欄の1行目 | `<問いかけ> あなたの反論をコメントで👇` | upload_youtube.py `with_engagement_line`（publish_shorts も経由） |
| 公開後のコメント | チャンネル（運営者）として問いかけコメントを1件 | scripts/engage.py `--post` |
| 返信 | 未返信の視聴者コメントへ 1〜2 文 | engage.py `--list-unreplied` → `--reply-to` |

**切り抜き本編の映像には何も重ねない。** 冒頭カード・終盤の板・ショートの下の黒帯だけ。

尺: 終盤の板を足しても **15分未満（14:55 まで）** に収まるよう `outro_seconds` が板を最短10秒まで縮める。
それでも超えるならビルドが止まる（クリップを減らす）。

## 問いかけ文

レシピの任意フィールド。省略するとタイトル（ショートは hook）から作る。

```json
"engagement": {
  "question": "「軽自動車は走る棺です」この考え方、アリ？ナシ？",
  "comment": "公開後のコメント本文（省略可）",
  "enabled": false
}
```

埋め込み形式のショート（長尺レシピの short）は `short.engagement` を見る。

既定文の例:
- 「軽自動車は走る棺です」これ、納得できる？できない？
- 「パリに手頃ないいホテルはありません」この考え方、アリ？ナシ？
- 「復職に引っ越し。大手を辞めるか」イエス？ノー？

既定コメント: `切り抜き運営者です。<問いかけ>` ＋「どっち派か、理由もひとこと…ひろゆきさんへの反論も大歓迎です。」

### 文体ルール（scripts/engagement.py の check_own_text で機械的にも止める）

- 議論が起きる二択。「あなたの反論をコメントで」
- 人を攻撃・侮辱する煽りは禁止。政治は禁止
- 「公式」「公認」と書かない。本人になりすまさない（一人称は運営者）
- 返信は 1〜2 文、丁寧だがツッコミ元気に。URL は入れない
- 攻撃的・スパム・政治・個人情報を含むコメントには返信しない（`flags` が付いたものは `--reply-to` が拒否する。読んで誤検出と判断したときだけ `--flags-ok`）
- **禁止**: 自分や別アカウントでのいいね・登録・自作自演コメント、報酬付きの依頼

## 日次ルーチン

### 朝（ビルド・予約）

いつもどおり build_episode → thumbnail → `--concat-only` → upload_youtube、ショートは build_short → publish_shorts。
テロップ・終盤の板・概要欄1行目は自動で入る。確認:

```bash
PYTHONPATH=. .venv/bin/python scripts/build_episode.py recipes/<id>.json --dry-run   # 問いかけ文が出る
```

既に予約済みで問いかけ行が無い動画（未来公開分のみ。公開済みは触らない）:

```bash
.venv/bin/python scripts/engage.py --update-scheduled-descriptions --dry-run
.venv/bin/python scripts/engage.py --update-scheduled-descriptions
```

### 夕方（公開後。長尺は 18:30 JST 公開）

1. 問いかけコメントを投稿（公開済みの動画のみ通る。二重投稿は state/engagement.json と API の両方で防ぐ）
   ```bash
   .venv/bin/python scripts/ops_youtube.py --status
   .venv/bin/python scripts/engage.py --post <videoId> --dry-run
   .venv/bin/python scripts/engage.py --post <videoId>
   ```
2. Studio 手作業（API では不可）
   ```bash
   .venv/bin/python scripts/engage.py --todo
   ```
   - コメント固定: Studio → コメント → 運営者コメントの「︙」→ 固定 → `--done <videoId> pin`
   - 終了画面（長尺）: 最後の 20 秒（「最後にひとつ質問です」の板）に登録ボタン＋動画2本（最新のアップロード／視聴者に適したコンテンツ）。文字は上部にあるので要素は中段〜下段に置く → `--done <videoId> endscreen`
   - 関連動画（ショート）: 同じ回の長尺を設定 → `--done <videoId> related`
3. 返信
   ```bash
   .venv/bin/python scripts/engage.py --list-unreplied            # 直近14日に公開した動画の、直近7日のコメント
   .venv/bin/python scripts/engage.py --reply-to <commentId> --text "1〜2文" --dry-run
   .venv/bin/python scripts/engage.py --reply-to <commentId> --text "1〜2文"
   ```
   `--list-unreplied` は読み取り専用（JSON）。自分のコメントは除外、返信済みも除外。
   運営者コメントへの視聴者の返信（kind=reply_to_our_comment）も出る。返信すると `@相手` が先頭に付く。

## クォータ

| 操作 | ユニット |
|---|---|
| commentThreads.insert / comments.insert | 50 |
| videos.update | 50 |
| *.list | 1 |

上限: 返信 **20件/日**、投稿 10件/日（太平洋時間の日付で数える）。返信 20 件で 1,000 ユニット。
videos.insert（1,600）と同じ 10,000 の枠なので、アップロードを先に済ませてから回す。

## 記録

`state/engagement.json`

- `posted[videoId]` 問いかけコメント（comment_id, text, at）
- `replied[commentId]` 返信（reply_id, video_id, text, at）
- `studio_todo[videoId]` pin / endscreen / related の済み・未済
- `description_updated[videoId]` 予約済み動画の概要欄に足した行
