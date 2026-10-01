# HANDOFF
最終更新: 2026-10-01（日次ops: 長尺「住まいと家賃」を18:30 JST予約・前日ショート導線更新）

---

## ▶ このセッションで最初に実行するコマンド

```bash
cd C:/Users/oshim/Documents/projects/hiroyuki-youtube; python scripts/ops_youtube.py --status
```

本日（2026-10-01）の枠は埋まっている。次の日次制作は 2026-10-02 10:13 JST。関連動画紐づけは夕方ルーチン（18:35）。

---

## いま何をしているのか

ひろゆき切り抜きチャンネル「ひろゆき解説ch【切り抜き】」(`UCqK3KYqEeeJiAWr4nSryJYQ`) の日次運用。

## 今回やったこと（2026-10-01）

1. `python scripts/ops_youtube.py --status` で実状態取得
2. 前日ショート `fs9CywDsa4I` の「▼この回をフルで見る」を前日長尺 `zKKJ1kktGIs` へ差し替え（APIで確認）
3. 新規長尺 `recipes/2026-10-01-sumai.json`（住まいと家賃の話5連発）を作成・ビルド・アップロード
4. `mUAjW7cCUxY` を 2026-10-01 18:30 JST（`2026-10-01T09:30:00Z`）に予約
5. 当日ショートは既存のため作成せず（`AFw0cJlMmzY` 07:00公開済）。Studio関連動画は夕方ルーチン担当のため未実施

## 検証済みの事実

- 当日ショート: `AFw0cJlMmzY`（コミ障だが大学事務職を目指す）07:00 JST 公開済（published_at `2026-09-30T22:00:07Z`）
- 当日長尺: `mUAjW7cCUxY` private→2026-10-01T09:30:00Z / 13:20 / 冒頭カードあり（thumb.at=120）
- 前日導線: `fs9CywDsa4I` → `https://www.youtube.com/watch?v=zKKJ1kktGIs` に更新済（APIで確認）
- VOICEVOX 0.25.2 / YouTube auth は稼働
- カスタムサムネ API は従来どおりアカウント側403想定。`thumb.png` は生成済（Studio目視用）

## 未検証のもの

- 通し再生（画・音・解説板）
- 18:30 予約の発火後の再生数
- 自動サムネ候補の品質（Studio目視）

## 次にやること

1. 夕方 18:35 関連動画紐づけ: 当日ショート `AFw0cJlMmzY` ← 当日長尺 `mUAjW7cCUxY`（Studio）
2. 必要なら `mUAjW7cCUxY` の自動サムネ候補を Studio で目視
3. `_plan-kenko/kosodate/kigyo` は使用禁止。海外・恋愛・趣味の `_plan` も埋めない

## 触ってはいけないところ

- 「公式」「公認」と書かない
- 切り抜き禁止: `exnFXUMMLLI` / `q0GyNI3X8cg`
- ゲスト共演回（例: `IXiLxkgHUMM` 石丸氏）は使わない
- 政治的な話題は落とす
- 予約時刻を過ぎた publishAt を渡さない（即時公開になる）
- 15分超は上げない（電話番号未確認）
