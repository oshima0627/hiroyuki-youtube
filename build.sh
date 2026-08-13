#!/usr/bin/env bash
# EP001 ビルドスクリプト
#
# 前提: source.mp4 に元配信（23vSB2fXjc8 / 3:23:01）を置くこと。
#       narration/01.wav 〜 06.wav にナレーション音声を置くこと（ep001-narration.md 参照）。
#
# 使い方:
#   ./build.sh cut     … 元配信から4本の切り抜きを書き出す
#   ./build.sh assemble … 切り抜き＋ナレーションを結合して完成品を出す
#   ./build.sh          … cut → assemble を通しで実行

set -euo pipefail
cd "$(dirname "$0")"

SRC=source.mp4
W=1920; H=1080; FPS=30
FONT_B='C\:/Windows/Fonts/meiryob.ttc'
FONT_R='C\:/Windows/Fonts/meiryo.ttc'

# name  start      end        telop
SEGMENTS=(
  "01|0:52:35|0:53:20|職場に無駄に絡んでくる人への対処法"
  "02|1:06:09|1:06:40|毒親と縁を切りたい"
  "03|2:14:04|2:14:55|手取り15万から転職したい"
  "04|2:41:50|2:43:20|22歳・実家の農家でフリーランス"
)

secs() { awk -F: '{n=NF; s=0; for(i=1;i<=n;i++) s=s*60+$i; print s}' <<<"$1"; }

cut_clips() {
  [ -f "$SRC" ] || { echo "ERROR: $SRC がありません。元配信を置いてください。" >&2; exit 1; }
  mkdir -p clips
  for row in "${SEGMENTS[@]}"; do
    IFS='|' read -r name st en telop <<<"$row"
    a=$(secs "$st"); b=$(secs "$en"); d=$((b-a))
    echo "== clip $name  $st→$en (${d}s)  $telop"
    # -ss を -i の前に置くと高速シーク、後ろの -ss で精密補正
    ffmpeg -y -hide_banner -loglevel error \
      -ss "$a" -i "$SRC" -t "$d" \
      -vf "scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:color=black,fps=${FPS},\
drawbox=x=0:y=${H}-150:w=${W}:h=110:color=0x0E1116@0.82:t=fill,\
drawtext=fontfile='${FONT_B}':text='${telop}':fontcolor=white:fontsize=52:x=70:y=${H}-122,\
drawbox=x=0:y=${H}-152:w=${W}:h=5:color=0xE23C3C@1:t=fill" \
      -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
      -c:a aac -b:a 192k -ar 48000 -ac 2 \
      "clips/${name}.mp4"
  done
  echo "OK: clips/ に4本書き出しました"
}

# ナレーション区間は静止画（直前クリップの最終フレーム）＋音声で生成する
make_narration_video() {
  local idx=$1 still=$2 wav=$3 out=$4
  local dur; dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$wav")
  ffmpeg -y -hide_banner -loglevel error \
    -loop 1 -i "$still" -i "$wav" \
    -vf "scale=${W}:${H},fps=${FPS},boxblur=12:2,\
drawbox=x=0:y=0:w=${W}:h=${H}:color=0x0E1116@0.55:t=fill,\
drawtext=fontfile='${FONT_R}':text='解説':fontcolor=0xFFD34D:fontsize=44:x=70:y=70" \
    -t "$dur" -c:v libx264 -preset medium -crf 20 -pix_fmt yuv420p \
    -c:a aac -b:a 192k -ar 48000 -ac 2 -shortest "$out"
}

assemble() {
  mkdir -p parts still
  local missing=0
  for i in 01 02 03 04 05 06; do
    [ -f "narration/${i}.wav" ] || { echo "MISSING: narration/${i}.wav"; missing=1; }
  done
  [ "$missing" -eq 0 ] || { echo "ナレーション音声が足りません。ep001-narration.md の6ブロックを録音してください。" >&2; exit 1; }

  # 導入（01）は clip01 の先頭フレームを使う
  ffmpeg -y -hide_banner -loglevel error -i clips/01.mp4 -frames:v 1 still/intro.png
  make_narration_video 01 still/intro.png narration/01.wav parts/00-intro.mp4

  local n=1
  for row in "${SEGMENTS[@]}"; do
    IFS='|' read -r name st en telop <<<"$row"
    cp "clips/${name}.mp4" "parts/$(printf '%02d' $((n*2-1)))-clip${name}.mp4"
    ffmpeg -y -hide_banner -loglevel error -sseof -1 -i "clips/${name}.mp4" -frames:v 1 "still/${name}.png"
    make_narration_video "$name" "still/${name}.png" "narration/0$((n+1)).wav" \
      "parts/$(printf '%02d' $((n*2)))-kaisetsu${name}.mp4"
    n=$((n+1))
  done

  # まとめ（06）
  make_narration_video 06 still/04.png narration/06.wav parts/99-outro.mp4

  ls parts/*.mp4 | sort | sed "s|^|file '|; s|$|'|" > parts/list.txt
  ffmpeg -y -hide_banner -loglevel error -f concat -safe 0 -i parts/list.txt -c copy ep001.mp4

  echo "=== 完成: ep001.mp4"
  ffprobe -v error -show_entries format=duration -of csv=p=0 ep001.mp4 \
    | awk '{printf "尺: %d:%02d\n", $1/60, $1%60}'
}

case "${1:-all}" in
  cut) cut_clips ;;
  assemble) assemble ;;
  all) cut_clips; assemble ;;
  *) echo "usage: $0 [cut|assemble]" >&2; exit 1 ;;
esac
