# HANDOFF
最終更新: 2026-10-10 20:10 JST（日次ops、初めて Linux ボックスで実行）

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
4. **クリップ取得（fetch_clips.py）はボックスでは不可**。cookie 無し yt-dlp（deno あり）で試したところ、音声のみ（映像0KB）かつ 2KB/s で11秒に2分。
   → PC で `python scripts/fetch_clips.py recipes/<id>.json`（Firefox cookie）→ work/clips/*.mp4 を tar（1ファイル100MB未満に分割）→ CopyToBox → ボックスの work/clips/ に展開。
5. ボックスで `build_episode.py` → `thumbnail.py` → `build_episode.py --concat-only`（冒頭カード）→ `upload_youtube.py work/<id> --schedule <UTC>`。Linux フォント対応（scripts/draw.py, contact_sheet.py）で問題なくビルドできた。
6. `ops_youtube.py --status` で private→publishAt を確認。

## 今回やったこと（2026-10-10）

- 新規長尺2本を作成・予約（両方ボックスでビルド・アップロード、サムネ API 成功 thumbnail_set=true）

| 公開 (JST) | レシピ | ID | 尺 | タイトル |
| --- | --- | --- | --- | --- |
| 10/10 21:30 | 2026-10-10-okane | A06Ijn-FpMM | 7:53 | 【ひろゆき】お金と投資の話6連発。お金がないなら計算ができていません |
| 10/11 18:30 | 2026-10-11-gadget | hiQQsH2Sf6Q | 14:15 | 【ひろゆき】ガジェットと道具選びの話7連発。スマホが割れるのはケース選びのミスです |

- 当日ショート T9g4Zm8oVeQ の「フルで見る」を f_pERzvz3uA → 718Lsuq9bgE（10/9長尺）へ API 更新
- Studio 関連動画は触っていない

## 検証済みの事実

- status: A06Ijn-FpMM private→2026-10-10T12:30Z、hiQQsH2Sf6Q private→2026-10-11T09:30Z
- T9g4Zm8oVeQ description が 718Lsuq9bgE を指す（API で取り直して確認）
- ショート予約在庫は 10/16 朝07:00 JST まで

## 未検証のもの

- ボックスで yt-dlp に cookies.txt を渡した場合の取得可否（未試行）
- ボックスでの fetch_source.py --subs-only

## 次にやること

1. 10/12 以降の長尺レシピ（未使用テーマ候補: 健康以外の生活ネタ、防犯・治安、食・料理など。_unused_1010.txt を参照）
2. ボックス単独化: YouTube cookie を Netscape 形式 cookies.txt で用意して `fetch_clips.py --cookies` を試す（ユーザー判断が必要）
3. 夕方の関連動画紐づけ（Studio）

## 触ってはいけないところ

- 「公式」「公認」と書かない（定型の「公式チャンネルではありません」表記は除く）。政治的な話題は落とす
- 切り抜き禁止: exnFXUMMLLI / q0GyNI3X8cg。ゲスト共演回（IXiLxkgHUMM, naVkgtFmRvg, Sq1YChd0RqQ）は使わない
- 予約時刻を過ぎた publishAt を渡さない。15分以上は上げない
- _plan-kenko / _plan-kosodate / _plan-kigyo は使わない。note は clips[].note（20文字以上）
- Studio 関連動画は朝ルーチンで触らない
