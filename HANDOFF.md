# HANDOFF
最終更新: 2026-09-29（日次ops: 長尺YouTube回を12:00 JST予約・前日ショート導線更新）

---

## ▶ このセッションで最初に実行するコマンド

```bash
cd C:/Users/oshim/Documents/projects/hiroyuki-youtube; python scripts/ops_youtube.py --status
```

本日（2026-09-29）の枠は埋まっている。次の日次は 2026-09-30 10:00 JST。

---

## いま何をしているのか

ひろゆき切り抜きチャンネル「ひろゆき解説ch【切り抜き】」(`UCqK3KYqEeeJiAWr4nSryJYQ`) の日次運用。

## 今回やったこと（2026-09-29）

1. `python scripts/ops_youtube.py --status` で実状態取得
2. 前日ショート `Wye2vEUDOz0` の「▼この回をフルで見る」を前日長尺 `pt6OrlocARY` へ差し替え
3. 新規長尺 `recipes/2026-09-29-youtube.json`（YouTubeの話5連発）を作成・ビルド・アップロード
4. `smoNVDDOI6M` を 2026-09-29 12:00 JST（`2026-09-29T03:00:00Z`）に予約

## 検証済みの事実

- 当日ショート: `V0rWOURVbo8`（資産四千六百万でサイドFIREしたい）07:00 JST 公開済
- 当日長尺: `smoNVDDOI6M` private→2026-09-29T03:00:00Z / 14:56 / 冒頭カードなし（15分上限のため）
- 前日導線: `Wye2vEUDOz0` → `https://www.youtube.com/watch?v=pt6OrlocARY` に更新済（APIで確認）
- VOICEVOX 0.25.2 / YouTube auth は稼働
- カスタムサムネ API は従来どおりアカウント側403想定。今回は thumb.png 未生成

## 未検証のもの

- 通し再生（画・音・解説板）
- 12:00 予約の発火後の再生数
- 冒頭カード無しでの自動サムネ品質

## 次にやること

1. 2026-09-30 日次: ops status → 当日短長枠 → 前日（9/29）ショートへ前日長尺 `smoNVDDOI6M` を導線付け
2. 必要なら `smoNVDDOI6M` に Studio で自動サムネ候補を目視確認
3. `_plan-kenko/kosodate/kigyo` は使用禁止。海外・恋愛・趣味の `_plan` も埋めない

## 触ってはいけないところ

- 「公式」「公認」と書かない
- 切り抜き禁止: `exnFXUMMLLI` / `q0GyNI3X8cg`
- 政治的な話題は落とす
- 予約時刻を過ぎた publishAt を渡さない（即時公開になる）
- 15分超は上げない（電話番号未確認）
