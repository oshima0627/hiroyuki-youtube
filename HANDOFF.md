# HANDOFF
最終更新: 2026-10-28 14:50 JST（10/28 14:17 日次: box の cookie 無し取得が全8区間成功 → box だけでビルド・予約まで完了）

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
2. 未使用ブロック一覧: `work/_unused_1014.py` の出力先を変えて実行 → `work/_unused_1016.txt`（再生成で更新）。
3. レシピを recipes/ に作り `PYTHONPATH=. .venv/bin/python -c "from scripts.recipe import validate ..."` で検証。
4. **クリップ取得はボックスで可（2026-10-12〜）**: `PYTHONPATH=. .venv/bin/python scripts/fetch_clips.py recipes/<id>.json --browser none`。
   cookie 無しだと bestvideo が Premium の HLS（itag 616）を選んで書き出し0のまま止まるため、fetch_clips.py の -f を avc1 の HLS（270/232）+ m4a 優先に変更済み。
   取れなくなったら PC で `python scripts/fetch_clips.py recipes/<id>.json`（Firefox cookie）→ work/clips/*.mp4 を tar → CopyToBox。
5. ボックスで `build_episode.py` → `thumbnail.py` → `build_episode.py --concat-only`（冒頭カード）→ `upload_youtube.py work/<id> --schedule <UTC>`。
6. `ops_youtube.py --status` で private→publishAt を確認。サムネは `set_thumbnails.py --only <id>`（必要なら `--force`）。

## 今回やったこと（2026-10-28 14:17 日次）— 完了

- git pull（8a3d292 で最新）。.venv・VOICEVOX 0.25.2 は生きていた
- status（14:18 JST）: 当日ショート CfPbeHlWoP8（07:00 公開済）・当日長尺 MT7ArIklAm4（private→2026-10-28T09:30Z、12:50）は既存でスキップ。10/29 分は 0 本だった
- フルで見る: kyTzNgBqUvQ（10/27 ショート）を QN45yEvHd8s → rKEhAInsB74（10/27 長尺）に更新（work/_update_short_full.py、数秒後に API で AFTER 確認。直後の AFTER 表示は古い値が返ることがある）
- 未使用ブロック一覧 work/_unused_1028.txt（733件、10/29 分を足す前。work/_unused_1028.py）
- 取得: **box の cookie 無し fetch_clips.py が長尺7区間＋ショート1区間すべて成功**（14:20〜14:35 JST、PC 不要。Fydc3YFumow で再試行1回あり）
- 翌日長尺 recipes/2026-10-29-game.json（新テーマ: ゲームとアニメ）→ **rpJy_1MYcHg**「【ひろゆき】ゲームとアニメの話7連発。ゲームの主人公が学生ばかりなのは子ども向けだからです」14:20（ffprobe 859.7秒）、
  private→2026-10-29T09:30Z（10/29 18:30 JST）。thumb.at 45（笑顔）、upload 時に thumbnail_set true（API で maxres あり）。
  問いかけ「「ゲームはそもそも子ども向けに作るもの」この考え方、アリ？ナシ？」を概要欄1行目で API 確認。冒頭カードと終盤の問いかけボードあり（フレームで確認）。
  途中に6〜7秒の無音（コメント読み）がある区間は手前で切った: _o8W_QKNHEo 1655.5〜1809.3（ガンダム。1816〜「かっこいいから」・パーフェクトジオングは未使用）、M7KWrHANxHs 8943.5〜8980.6（スト6。8987〜大会賞金の話は未使用）、jHWUy2IiZvs 1036.5〜1076.4（ハンターハンター。1083〜ワンピースの話は未使用）。
  end を変えたものは区間ファイルを新しい名前にコピーした（*_1655-1809, *_8943-8980, *_1036-1076）。VYJ-zTB8TVY は空調ノイズで silencedetect が効かないので RMS を 0.1 秒刻みで見て決めた
- 翌日ショート recipes/shorts/2026-10-29-am.json → **OZnlwCiAMEA**「【ひろゆき】金魚すくいのポイにワセリンを塗ったら破れない？【切り抜き】」53秒（23vSB2fXjc8 10153.1〜10205.1）、
  private→2026-10-28T22:00Z（10/29 07:00 JST）。フルで見る→MT7ArIklAm4（parent 2026-10-28-kagaku、API で確認）。hook「ワセリンは塗るな」。問いかけ「「裏ワザより仕組みを考えた方が得」この考え方、アリ？ナシ？」。サムネ API 未設定（従来どおり）
- publish_shorts.py は `PYTHONPATH=.` を付けないと upload_youtube.py 内の `from scripts.engagement` で ModuleNotFoundError（アップロード前に止まるので害はない）
- ゲームの残り: 23vSB2fXjc8 10213〜10217（悟空が強いのは作者がそう描いたから・短い）、10381〜10414（漫画の吹き出し研究）、_o8W_QKNHEo 2021〜2113（透明人間は目が見えない。「女湯」の冗談あり）、23vSB2fXjc8 8243〜（遊戯王も学生、の続き）

## 前回やったこと（2026-10-27 14:15 日次）— 完了

- 当日 kyTzNgBqUvQ・rKEhAInsB74 はスキップ。oUt6kcCwW5c のフルで見るを QN45yEvHd8s に更新
- 10/28 長尺 MT7ArIklAm4（科学と技術の話6連発・recipes/2026-10-28-kagaku.json）、10/28 ショート CfPbeHlWoP8（recipes/shorts/2026-10-28-am.json、フルで見る→rKEhAInsB74）
- 科学の残り: M7KWrHANxHs 7191〜7480（観測と物質）、Fydc3YFumow 2286〜2428（洋上風力。2428 以降は政権の話なので切る）、Fydc3YFumow 10221〜10450（農業ロボット・ドローン）

## 検証済みの事実

- status（2026-10-16 15:00 JST）: Mw4CM0_gFhw private→2026-10-16T09:30Z 9M40S、id0Ju8MPkBU private→2026-10-17T09:30Z、hxzDGMs-aWE private→2026-10-16T22:00Z（処理中）、5UDR-8tVjAE public
- hxzDGMs-aWE: API で channelId=UCqK3KYqEeeJiAWr4nSryJYQ、publishAt 2026-10-16T22:00:00Z、概要欄1行目の問いかけと Mw4CM0_gFhw へのリンクを確認。フレーム抽出（9点＋終盤）で崩れなし（顔が左端に寄る瞬間はあるが切れていない）、末尾は無音区間で切れている
- u_vN9xYpzyI description が hZCbbUwQVOI を指す
- cookie 無し fetch_clips 7区間成功

## 次にやること

1. 10/29 の日次: 当日ショート OZnlwCiAMEA（07:00）・当日長尺 rpJy_1MYcHg（18:30）は確認してスキップ。前日ショート CfPbeHlWoP8 のフルで見るを前日長尺 MT7ArIklAm4 に更新。10/30 分の長尺・ショートを作る（ショートのフルで見る→rpJy_1MYcHg）
   `.venv/bin/python work/_update_short_full.py <short_id> <long_id>`
2. 夕方 10/28: MT7ArIklAm4 公開後に engage（問いかけコメント・返信）、Studio の関連動画（CfPbeHlWoP8→MT7ArIklAm4）・固定・終了画面
3. box の cookie 無し取得は 10/22・10/23 は不可、10/24〜10/28 は全区間成功。box で数分試して進まなければ PC 取得に切り替える
