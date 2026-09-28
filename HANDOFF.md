# HANDOFF

最終更新: 2026-09-28（長尺「マナー」回をビルド済み・未アップロード）

---

## ▶ このセッションで最初に実行するコマンド

**長尺 `2026-09-28-manner` はビルド済み。アップロードだけ残っている。**
ユーザー承認後に次を叩く（承認なしでは上げない）:

```bash
cd C:/Users/oshim/Documents/projects/hiroyuki-youtube; python scripts/upload_youtube.py work/2026-09-28-manner
```

private のまま上がる。公開予約するならそのあと Studio か `ops_youtube.py` で日時を付ける。
**カスタムサムネは API が 403 のまま**（アカウント側の機能利用資格）。`thumb.png` は作ってあるが `set_thumbnails.py` は通らない想定。

---

## いま何をしているのか

ひろゆき切り抜きチャンネル「ひろゆき解説ch【切り抜き】」(`UCqK3KYqEeeJiAWr4nSryJYQ` /
`@hiroyuki_kaisetsu`) の運用。

**2026-09-28 に長尺レシピ `recipes/2026-09-28-manner.json`（公共マナー5連発）を承認どおりビルドした。**
アップロード・予約はまだ。

## 今回やったこと（2026-09-28）

1. `python scripts/fetch_clips.py recipes/2026-09-28-manner.json` → 5区間取得成功（1本は取得済み）
2. VOICEVOX 0.25.2 は既に起動中（`http://127.0.0.1:50021`）
3. `python scripts/build_episode.py recipes/2026-09-28-manner.json` → `work/2026-09-28-manner/video.mp4` **14:27**（冒頭カードなし）
4. `contact_sheet.py` で候補を見て `thumb.at` を **60 → 180** に変更（60は横顔・下向き、180は笑顔）
5. `thumbnail.py` → `build_episode.py --concat-only` → 冒頭カード付き **14:30**

## 検証済みの事実

- 出力: `C:\Users\oshim\Documents\projects\hiroyuki-youtube\work\2026-09-28-manner\`
  - `video.mp4` 870.1s（**14:30**） / 約128MB
  - `thumb.png` 1280x720
  - `meta.json` / `description.txt`
- クリップ元: `jHWUy2IiZvs` / `daulqJwmooE` / `5xJ3ZzEnyI8`
- `thumb.at=180` は笑顔だが顔スコア表示は 0.001、下端彩度警告あり（スパチャ帯の名残。目視では顔寄りクロップで概ね問題なし）
- アップロード・予約は**していない**

## 未検証のもの

- 通し再生（画・音・解説板の読み上げ）
- `upload_youtube.py` での本番アップロード
- サムネ API 403 が解けているか（2026-09-10 時点では未解決）

## 次にやること

1. 通しで再生して問題が無いか確認
2. 承認後: `python scripts/upload_youtube.py work/2026-09-28-manner`（private）
3. Studio で機能の利用資格を確認し、カスタムサムネが使えるなら `set_thumbnails.py`
4. 公開日時を決めて予約

## 触ってはいけないところ

- **「公式」「公認」と書かない**
- 黙認の対象は西村博之氏の素材のみ
- 収益化が通ったら必ず <get-clip@razil.jp> へ連絡
- 切り抜き禁止: `exnFXUMMLLI` / `q0GyNI3X8cg`
- **政治的な話題は落とす**
- **カスタムサムネイルは 403 の可能性が高い**（アカウント側）
- **フックを機械で短くしない**
- この回は**まだアップロードしていない**。承認なしで上げない
