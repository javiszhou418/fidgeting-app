#!/bin/zsh

set -euo pipefail

project_root="${0:A:h:h}"
recenter_helper="${0:A:h}/recenter_sticker_mask.py"
master_path="${1:-${project_root}/Artifacts/Stickers/StickerAtlasImageGenMaster.png}"
png_root="${project_root}/Assets/Resources/ProductStickers/BackdropWhite"
svg_root="${project_root}/Assets/Art/ProductStickers/Vector"

if [[ ! -f "${master_path}" ]]; then
    print -u2 "Missing ImageGen master: ${master_path}"
    exit 1
fi

dimensions="$(ffprobe -v error -select_streams v:0 \
    -show_entries stream=width,height -of csv=s=x:p=0 "${master_path}")"
if [[ "${dimensions}" != "1536x1024" ]]; then
    print -u2 "Expected a 1536x1024 6x4 master, got ${dimensions}"
    exit 1
fi

mkdir -p "${png_root}" "${svg_root}"
work_root="$(mktemp -d "${TMPDIR:-/tmp}/fidget-sticker-vector.XXXXXX")"
trap 'rm -rf "${work_root}"' EXIT

names=(
    01-polygon-cube
    02-hw-studio
    03-top-right-monogram
    04-rabbit-hand
    05-wawu-word
    06-round-mascot
    07-nck-word
    08-geeone
    09-tiger-head
    10-meteor
    11-mackie
    12-turci-word
    13-astronaut
    14-target
    15-knot
    16-flame-leaf
    17-chemy-word
    18-emoji-face
    19-box-t
    20-warning-triangle
    21-triple-stroke
    22-section-s
    23-fierce-head
    24-round-chinese
)

for index in {1..24}; do
    zero_index=$((index - 1))
    column=$((zero_index % 6))
    row=$((zero_index / 6))
    crop_x=$((column * 256))
    crop_y=$((row * 256))
    name="${names[index]}"
    mask_path="${work_root}/${name}.pgm"
    centered_mask_path="${work_root}/${name}-centered.pgm"

    ffmpeg -hide_banner -loglevel error -i "${master_path}" \
        -vf "crop=256:256:${crop_x}:${crop_y},format=gray,lut=y='if(gte(val,96),255,0)',negate" \
        -frames:v 1 -y "${mask_path}"

    python3 "${recenter_helper}" \
        --source "${mask_path}" \
        --trace-mask "${centered_mask_path}" \
        --png "${png_root}/${name}.png"

    potrace -s -C '#FFFFFF' --turdsize 3 --alphamax 1.0 \
        --opttolerance 0.16 -o "${svg_root}/${name}.svg" "${centered_mask_path}"
done

print "Rebuilt and centered ${#names} SVG masters and transparent 1024x1024 PNG assets."
