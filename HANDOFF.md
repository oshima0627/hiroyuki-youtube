# HANDOFF
最終更新: 2026-10-14 14:30 JST（日次ops、ボックス単独で10/15長尺を予約）

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

## 今回やったこと（2026-10-14）

- 当日ショート 4CIkzIwtq5M（ゴマすりで上げた給料は実力か・07:00公開済）と当日長尺 EY3dsQ3MUPY（旅行・18:30）は既存のためスキップ
- 10/15 18:30 長尺 2026-10-15-kuruma → hZCbbUwQVOI「車と移動の話6連発。軽自動車は走る棺です」8:21、thumbnail_set=true（thumb.at=50, crop 指定）
- 素材は cookie 無しでボックス取得（6区間）
- フルで見る: 4CIkzIwtq5M ssy9pUfgCNc→EY3dsQ3MUPY（API で取り直して確認）。RMBxw4tSNBY は kMPbU2q7328 のまま
- 未使用ブロック一覧は work/_unused_1014.py → work/_unused_1014.txt（867件、10/14分まで反映）
- 10/16 以降の長尺は未作成。ショート予約在庫は 10/16 朝07:00 JST まで

## 前回やったこと（2026-10-13）

- 10/14 18:30 長尺 2026-10-14-ryokou → EY3dsQ3MUPY「旅行の話7連発。パリに手頃ないいホテルはありません」13:30、thumbnail_set=true（thumb.at=250, crop 指定。自動選択は後頭部になったため）
- 素材は cookie 無しでボックス取得（7区間、403 レート制限で1回再試行のみ）
- フルで見る: RMBxw4tSNBY Di-K-jhqgMg→kMPbU2q7328（API で取り直して確認）。Eiwh5C540IA は eG8IEYEkbTA のまま
- 未使用ブロック一覧は work/_unused_1013.py → work/_unused_1013.txt（868件、10/13分まで反映）。全字幕キーワード検索は work/_kw_scan.py "<正規表現>"（使用済み区間を除外）
- 10/15 以降の長尺は未作成。ショート予約在庫は 10/16 朝07:00 JST まで

## 検証済みの事実

- status: hZCbbUwQVOI private→2026-10-15T09:30Z、EY3dsQ3MUPY private→2026-10-14T09:30Z
- 4CIkzIwtq5M description が EY3dsQ3MUPY を指す（API で取り直して確認）
- ショート予約在庫は 10/16 朝07:00 JST まで

## 未検証のもの

- ボックスで yt-dlp に cookies.txt を渡した場合の取得可否（未試行。cookie 無しで取れたので不要になった）
- ボックスでの fetch_source.py --subs-only

## 次にやること

1. 10/16 以降の長尺レシピ（使用済み: 車・旅行・防犯・食・ガジェット・お金 ほか。候補例: ペットと動物、見た目と美容。_unused_1014.py で再生成してから選ぶ）
2. cookie 無し取得が 403 等で再び落ちる場合のみ cookies.txt を検討（ユーザー判断が必要）
3. 夕方の関連動画紐づけ（Studio）

## 触ってはいけないところ

- 「公式」「公認」と書かない（定型の「公式チャンネルではありません」表記は除く）。政治的な話題は落とす
- 切り抜き禁止: exnFXUMMLLI / q0GyNI3X8cg。ゲスト共演回（IXiLxkgHUMM, naVkgtFmRvg, Sq1YChd0RqQ）は使わない
- 予約時刻を過ぎた publishAt を渡さない。15分以上は上げない
- _plan-kenko / _plan-kosodate / _plan-kigyo は使わない。note は clips[].note（20文字以上）
- Studio 関連動画は朝ルーチンで触らない
