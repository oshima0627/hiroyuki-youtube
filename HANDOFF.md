# HANDOFF
最終更新: 2026-10-27 14:55 JST（10/27 14:15 日次: box の cookie 無し取得が全7区間成功 → box だけでビルド・予約まで完了）

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

## 今回やったこと（2026-10-27 14:15 日次）— 完了

- git pull（75b92ab で最新）。.venv・VOICEVOX 0.25.2 は生きていた
- status（14:16 JST）: 当日ショート kyTzNgBqUvQ（07:00 公開済）・当日長尺 rKEhAInsB74（private→2026-10-27T09:30Z、12:49）は既存でスキップ。10/28 分は 0 本だった
- フルで見る: oUt6kcCwW5c（10/26 ショート）を WaXp52ksF50 → QN45yEvHd8s（10/26 長尺）に更新（work/_update_short_full.py、AFTER を API で確認）。kyTzNgBqUvQ は QN45yEvHd8s のまま（確認済み）
- 未使用ブロック一覧 work/_unused_1027.txt（743件、10/28 分を足す前。work/_unused_1027.py）
- 取得: **box の cookie 無し fetch_clips.py が長尺6区間＋ショート1区間すべて成功**（14:17〜14:25 JST、PC 不要）。h264+aac（VYJ-zTB8TVY は 1280x720、他 1920x1080）
- 翌日長尺 recipes/2026-10-28-kagaku.json（新テーマ: 科学と技術）→ **MT7ArIklAm4**「【ひろゆき】科学と技術の話6連発。資源が取れても儲かるとは限らないんです」12:49（ffprobe 769.3秒）、
  private→2026-10-28T09:30Z（10/28 18:30 JST）。thumb.at 60（横向き）→ 45（手を広げて笑うカット）、upload 時に thumbnail_set true（API で maxres あり）。
  問いかけ「「技術があっても採算が合わなければ意味がない」この考え方、アリ？ナシ？」を概要欄1行目で API 確認。冒頭カードと終盤20秒の問いかけボードあり（フレームで確認）。
  レアメタルの回は高市政権・三菱商事の話（Fydc3YFumow 2286 以降の洋上風力）の手前で切った。量子暗号の回（VYJ-zTB8TVY 4133〜）は直前の AI「ミトス」の話を外した。
  冷凍食品の温めムラ（23vSB2fXjc8 2731〜2835）は本人が CM に出た商品の PR なので使わず。物理学の実在の話（M7KWrHANxHs 7191〜7480）は尺のため未使用。
  区間の終わりは無音を測って調整（区間ファイル名は int(start)-int(end) なので、end を変えて名前が変わる VYJ-zTB8TVY_4133-4268.mp4 は 4133-4269 をコピーした）
- 翌日ショート recipes/shorts/2026-10-28-am.json → **CfPbeHlWoP8**「【ひろゆき】投資の収入が給料を超えたら会社を辞めていいのか【切り抜き】」65秒（daulqJwmooE 7159.4〜7224.0）、
  private→2026-10-27T22:00Z（10/28 07:00 JST）。フルで見る→rKEhAInsB74（parent 2026-10-27-sports、API で確認）。hook「仕事は辞めるな」。問いかけ「「お金があっても仕事は続けるべき」この考え方、アリ？ナシ？」。
  先頭の前の回答の「ます」と、終わりの「うん」を無音で外した。顔が左下に寄る（自動クロップのまま）。ショートのサムネは API 未設定（従来どおり）
- 科学の残り: M7KWrHANxHs 7191〜7480（観測と物質・相対性理論）、Fydc3YFumow 2286〜2428（洋上風力は台風で採算が合わない。2428 以降は政権の話なので切る）、23vSB2fXjc8 8745〜（量子コンピューター短い）、Fydc3YFumow 10221〜10450（農業ロボット・ドローン）

## 前回やったこと（2026-10-26 14:16 日次）— 完了

- status（14:17 JST）: 当日ショート oUt6kcCwW5c（07:00 公開済）・当日長尺 QN45yEvHd8s（private→2026-10-26T09:30Z、10:08）は既存でスキップ。10/27 分は 0 本だった。.venv・VOICEVOX は生きていた
- フルで見る: wbLkK40nUXw（10/25 ショート）を k9vGnOkWgG4 → WaXp52ksF50（10/25 長尺）に更新（work/_update_short_full.py、AFTER を API で確認）。oUt6kcCwW5c は WaXp52ksF50 のまま（慣例どおり）
- 未使用ブロック一覧 work/_unused_1026.txt（751件、10/27 分を足す前。work/_unused_1026.py）
- 取得: **box の cookie 無し fetch_clips.py が長尺6区間＋ショート1区間すべて成功**（14:18〜14:27 JST、PC 不要）
- 翌日長尺 recipes/2026-10-27-sports.json（新テーマ: スポーツと格闘技）→ **rKEhAInsB74**「【ひろゆき】スポーツと格闘技の話6連発。根性論より理論でやる人の方が伸びるんです」12:48（PT12M49S）、
  private→2026-10-27T09:30Z（10/27 18:30 JST）。thumb.at 60 は注釈カードに当たった → 45（笑顔で手振りのカット）、upload 時に thumbnail_set true。
  問いかけ「「スポーツは根性より理論で伸びる」この考え方、アリ？ナシ？」を概要欄1行目で API 確認。
  根性論の回（O0YEy2NB3os）は暴力指導のプロレスラー個人の話（105〜231）を外し、231.4〜284.5 のみ。ボディビルダー対格闘家（daulqJwmooE 3119〜3245）は尺（15分超え）のため未使用
- 翌日ショート recipes/shorts/2026-10-27-am.json → **kyTzNgBqUvQ**「【ひろゆき】結婚相手を年収と顔で選ぶと失敗する理由【切り抜き】」40秒（Fydc3YFumow 8133.7〜8174.1）、
  private→2026-10-26T22:00Z（10/27 07:00 JST）。フルで見る→QN45yEvHd8s（parent 2026-10-26-fuufu、API で確認）。hook「美人は3日で飽きる」。問いかけ「「結婚相手は顔より生活力で選ぶべき」この考え方、アリ？ナシ？」。
  直後の「やってすればいい」（下ネタ寄り）の手前、「美人は3日で飽きますよ」直後の無音で切った。顔が左下に寄る（自動クロップのまま）。サムネ API 未設定（従来どおり）
- スポーツの残り: daulqJwmooE 2948〜3119（男女の筋肉量・木村モナさん）、3119〜3245（ルール次第・ボディビルダー）、M7KWrHANxHs 7607〜7637（有馬記念）、O0YEy2NB3os 285〜368（のびのび系が増えた）

## 検証済みの事実

- status（2026-10-16 15:00 JST）: Mw4CM0_gFhw private→2026-10-16T09:30Z 9M40S、id0Ju8MPkBU private→2026-10-17T09:30Z、hxzDGMs-aWE private→2026-10-16T22:00Z（処理中）、5UDR-8tVjAE public
- hxzDGMs-aWE: API で channelId=UCqK3KYqEeeJiAWr4nSryJYQ、publishAt 2026-10-16T22:00:00Z、概要欄1行目の問いかけと Mw4CM0_gFhw へのリンクを確認。フレーム抽出（9点＋終盤）で崩れなし（顔が左端に寄る瞬間はあるが切れていない）、末尾は無音区間で切れている
- u_vN9xYpzyI description が hZCbbUwQVOI を指す
- cookie 無し fetch_clips 7区間成功

## 次にやること

1. 10/28 の日次: 当日ショート CfPbeHlWoP8（07:00）・当日長尺 MT7ArIklAm4（18:30）は確認してスキップ。前日ショート kyTzNgBqUvQ のフルで見るを前日長尺 rKEhAInsB74 に更新。10/29 分の長尺・ショートを作る（ショートのフルで見る→MT7ArIklAm4）
   `.venv/bin/python work/_update_short_full.py <short_id> <long_id>`
2. 夕方 10/27: rKEhAInsB74 公開後に engage（問いかけコメント・返信）、Studio の関連動画（kyTzNgBqUvQ→rKEhAInsB74）・固定・終了画面
3. box の cookie 無し取得は 10/22・10/23 は不可、10/24〜10/27 は全区間成功。box で数分試して進まなければ PC 取得に切り替える
