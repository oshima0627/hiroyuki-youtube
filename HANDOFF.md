# HANDOFF
最終更新: 2026-10-06（日次ops: 新規レシピで長尺3本を作成し 10/6・10/7・10/8 18:30 JST に予約）

---

## ▶ このセッションで最初に実行するコマンド

```bash
cd C:/Users/oshim/Documents/projects/hiroyuki-youtube; python scripts/ops_youtube.py --status
```

10/6・10/7・10/8 の長尺は予約済み。次に作るのは 10/9 以降の長尺。関連動画紐づけは夕方ルーチン（18:35）。10/4・10/5 長尺空白は未補填（過去日付は即時公開になるので埋めない）。

---

## いま何をしているのか

ひろゆき切り抜きチャンネル「ひろゆき解説ch【切り抜き】」(UCqK3KYqEeeJiAWr4nSryJYQ) の日次運用。

## 今回やったこと（2026-10-06）

1. `ops_youtube.py --status` で実状態取得
2. 未取得だった配信 2本（0ojMhUyiHB4 / 4vmH4mejnjI）の字幕・signals を取得（`fetch_source.py --subs-only` → `probe_signals.py --no-audio`）
3. `plan_episode.py --theme` はタイトル冒頭一致が狭く在庫が少なく見えたので、未使用ブロック一覧（`work/_unused_1006.py` → `work/_unused_1006.txt`、使用済み区間・ショート窓・共演回を除外）から字幕を読んで手で構成
4. 新規レシピ3本を作成（note は全クリップ 90字以上、summary/title/thumb あり）
5. fetch_clips → build_episode → contact_sheet で thumb.at を目視決定 → thumbnail → build --concat-only → upload（--schedule）
6. 前日（10/05）長尺が無いため、前日ショートのフル導線差し替えは未実施
7. Studio 関連動画は触っていない

## 予約済み長尺

| 公開 (JST) | レシピ | ID | 尺 | タイトル |
| --- | --- | --- | --- | --- |
| 10/6 18:30 | 2026-10-06-ningen | `xAHwnOlrbpw` | 12:59 | 【ひろゆき】人間関係の相談6連発。マウントは取り返しても得をしません |
| 10/7 18:30 | 2026-10-07-un | `IYcOd70aT_g` | 13:52 | 【ひろゆき】運と才能の話5連発。運は打席に立った回数です |
| 10/8 18:30 | 2026-10-08-gaman | `hFeUyOQ1QO0` | 14:03 | 【ひろゆき】我慢とストレスの話6連発。人は痛みを忘れて我慢してしまいます |

サムネ API（thumbnails.set）: 3本とも成功（published.json thumbnail_set=true）。

## 検証済みの事実

- 3本とも API 上 private→publishAt（2026-10-06/07/08T09:30:00Z）
- 当日ショート rM4ftL719w4 は既存・public（触っていない）
- 0ojMhUyiHB4 / 4vmH4mejnjI は collab_warning=null（単独配信）
- VOICEVOX 0.25.2 稼働
- 3本とも処理完了（API duration: 13M / 13M52S / 14M4S）

## 未検証のもの

- 新テーマ（人間関係／運と才能／我慢とストレス）の再生数

## 次にやること

1. 10/9 以降の長尺: `work/_unused_1006.txt` の残りから新テーマで構成（今回使った区間は recipes/ に入ったので used_ranges で自動除外される）
2. 10/7 朝: 前日（10/6）長尺 xAHwnOlrbpw ができたので、10/7 当日ショート（V8z1YsBJe3M）の「フルで見る」導線を差し替え可
3. 夕方 18:35 関連動画紐づけ（夕方ルーチン）

## 触ってはいけないところ

- 「公式」「公認」と書かない
- 切り抜き禁止: exnFXUMMLLI / q0GyNI3X8cg
- ゲスト共演回（例: IXiLxkgHUMM 石丸氏、naVkgtFmRvg、Sq1YChd0RqQ【ひろゆきと語る夜】）は使わない
- 政治的な話題は落とす
- 予約時刻を過ぎた publishAt を渡さない（即時公開になる）
- 15分超は上げない（電話番号未確認）
- _plan-kenko / _plan-kosodate / _plan-kigyo は使わない
- note 不足の _plan は埋めない（新規 JSON を recipes/ に作る）
- Studio 関連動画は朝ルーチンで触らない
