# HANDOFF
最終更新: 2026-10-06（日次ops朝: 当日ショート確認済み・当日長尺は note 済み在庫不足で未作成）

---

## ▶ このセッションで最初に実行するコマンド

`ash
cd C:/Users/oshim/Documents/projects/hiroyuki-youtube; python scripts/ops_youtube.py --status
`

本日（2026-10-06）ショート枠は埋まっている。長尺は人手で note 済みレシピを用意するまで作れない。関連動画紐づけは夕方ルーチン（18:35）。10/4・10/5 長尺空白は未補填。

---

## いま何をしているのか

ひろゆき切り抜きチャンネル「ひろゆき解説ch【切り抜き】」(UCqK3KYqEeeJiAWr4nSryJYQ) の日次運用。

## 今回やったこと（2026-10-06 朝）

1. ListMachines で ASUS_i9 connected=true を確認
2. python scripts/ops_youtube.py --status で実状態取得（published.json 更新）
3. 当日ショート有無を判定 → 既存のため作成せず
4. 当日長尺を探した → 未予約。note 済み未使用レシピ／上げ済み長尺在庫なし → 作成せずブロッカー報告
5. 前日（10/05）長尺が無いため、前日ショートのフル導線差し替えは未実施
6. Studio 関連動画は触っていない（夕方ルーチン委譲）

## 検証済みの事実

- ASUS_i9 (841edaf-4bae-409d-9c81-4ca261154013) connected=true
- 当日ショート: 
M4ftL719w4（月三十万の積立でFIREできるか）private→2026-10-05T22:00:00Z（= 2026-10-06 07:00 JST）／作成せず
- 当日長尺: 無し（最新公開長尺は DZHevK7l12g／2026-10-03 18:30 JST 公開済）
- note 済み未使用レシピ: 無し（_plan-kenko/kosodate/kigyo 禁止。_plan-kaigai/renai/shumi も note=0 かつ埋めない方針。2026-08-15-ningen も note=0）
- 上げ済み private 長尺在庫: 無し
- サムネ API: 今回アップロード無しのため未実施
- VOICEVOX / YouTube auth: status API は稼働

## 未検証のもの

- 当日 07:00 ショート予約の発火後再生数
- 人手で用意する次の長尺レシピの内容

## 次にやること

1. 人手で note（各 clip ≥20字）済みの長尺レシピを用意し、18:30 JST 予約できる状態にする（または別テーマで plan→note）
2. 夕方 18:35 関連動画紐づけは、当日長尺が出来てから（無ければスキップ判断）
3. 10/4・10/5 長尺空白の穴埋めは本ルーチン対象外（別指示があるまで触らない）

## 触ってはいけないところ

- 「公式」「公認」と書かない
- 切り抜き禁止: exnFXUMMLLI / q0GyNI3X8cg
- ゲスト共演回（例: IXiLxkgHUMM 石丸氏）は使わない
- 政治的な話題は落とす
- 予約時刻を過ぎた publishAt を渡さない（即時公開になる）
- 15分超は上げない（電話番号未確認）
- _plan-kenko / _plan-kosodate / _plan-kigyo は使わない
- note 不足のレシピは作らない
- Studio 関連動画は朝ルーチンで触らない
