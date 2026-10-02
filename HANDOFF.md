# HANDOFF
最終更新: 2026-10-02（日次ops: 長尺「勉強と学び方」を18:30 JST予約・前日ショート導線更新）

---

## ▶ このセッションで最初に実行するコマンド

```bash
cd C:/Users/oshim/Documents/projects/hiroyuki-youtube; python scripts/ops_youtube.py --status
```

本日（2026-10-02）の枠は埋まっている。次の日次制作は 2026-10-03 10:13 JST。関連動画紐づけは夕方ルーチン（18:35）。

---

## いま何をしているのか

ひろゆき切り抜きチャンネル「ひろゆき解説ch【切り抜き】」(`UCqK3KYqEeeJiAWr4nSryJYQ`) の日次運用。

## 今回やったこと（2026-10-02）

1. `python scripts/ops_youtube.py --status` で実状態取得
2. 前日ショート `AFw0cJlMmzY` の「▼この回をフルで見る」を前日長尺 `mUAjW7cCUxY` へ差し替え（APIで確認）
3. 新規ソース `O0YEy2NB3os` / `skPyrH0WTzY` / `g2N-OcbplbA` の字幕・signals を取得
4. 新規長尺 `recipes/2026-10-02-benkyo.json`（勉強と学び方の話5連発）を作成・ビルド・アップロード
5. `8-p8sIG6jZg` を 2026-10-02 18:30 JST（`2026-10-02T09:30:00Z`）に予約。カスタムサムネ API は成功
6. 当日ショートは既存のため作成せず（`FxQT7vKcSZM` 07:00公開済）。Studio関連動画は夕方ルーチン担当のため未実施

## 検証済みの事実

- 当日ショート: `FxQT7vKcSZM`（派遣から正社員になりたい）07:00 JST 公開済（published_at `2026-10-01T22:00:15Z`）
- 当日長尺: `8-p8sIG6jZg` private→2026-10-02T09:30:00Z / 14:16〜14:17 / 冒頭カードあり（thumb.at=160）
- 前日導線: `AFw0cJlMmzY` → `https://www.youtube.com/watch?v=mUAjW7cCUxY` に更新済（APIで確認）
- VOICEVOX 0.25.2 / YouTube auth は稼働
- カスタムサムネ API は今回成功（`thumbnails.set`）。`thumb.png` 生成済

## 未検証のもの

- 通し再生（画・音・解説板）
- 18:30 予約の発火後の再生数
- 自動サムネ候補の品質（Studio目視は任意）

## 次にやること

1. 夕方 18:35 関連動画紐づけ: 当日ショート `FxQT7vKcSZM` ← 当日長尺 `8-p8sIG6jZg`（Studio）
2. 必要なら `8-p8sIG6jZg` の自動サムネ候補を Studio で目視
3. `_plan-kenko/kosodate/kigyo` は使用禁止。海外・恋愛・趣味の `_plan` も埋めない

## 触ってはいけないところ

- 「公式」「公認」と書かない
- 切り抜き禁止: `exnFXUMMLLI` / `q0GyNI3X8cg`
- ゲスト共演回（例: `IXiLxkgHUMM` 石丸氏）は使わない
- 政治的な話題は落とす
- 予約時刻を過ぎた publishAt を渡さない（即時公開になる）
- 15分超は上げない（電話番号未確認）
