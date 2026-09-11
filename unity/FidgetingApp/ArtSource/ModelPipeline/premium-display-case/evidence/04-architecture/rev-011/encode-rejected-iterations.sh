#!/bin/bash
# Encode rejected-iteration Unity PNG frames to inspectable video, then drop the
# PNG sets. Keeps every rejected iteration inspectable as labeled history while
# releasing the disk the next real capture needs.
set -u
cd "$(dirname "$0")/iterations" || exit 1

for i in 01 03 04 05 06 07; do
  d="iteration-$i"
  [ -d "$d/frames" ] || { echo "skip $d (no frames)"; continue; }
  count=$(ls "$d"/frames/frame-*.png 2>/dev/null | wc -l | tr -d ' ')
  echo "encoding $d ($count frames)"
  if ffmpeg -y -loglevel error -framerate 60 \
      -i "$d/frames/frame-%04d.png" \
      -c:v libx264 -crf 16 -pix_fmt yuv420p -movflags +faststart \
      "$d/normal-speed-sequence.mp4"; then
    rm -rf "$d/frames"
    echo "ok $d -> $(du -h "$d/normal-speed-sequence.mp4" | cut -f1)"
  else
    echo "FAILED $d (frames kept)"
  fi
done

echo "ENCODE_DONE"
du -sh ..
df -h /Users/jiawei.zhou/Documents | tail -1
