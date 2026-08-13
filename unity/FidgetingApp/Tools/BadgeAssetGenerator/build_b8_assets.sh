#!/bin/zsh
set -euo pipefail

TOOL_DIR="${0:A:h}"
PROJECT_ROOT="${TOOL_DIR:h:h}"
ASSET_DIR="$PROJECT_ROOT/Assets/Plugins/iOS/BadgeArtwork"
MODULE_CACHE="$(mktemp -d /tmp/fidget-badge-asset-cache.XXXXXX)"

python3 "$TOOL_DIR/generate_b8_badges.py"

SVG_FILES=("$ASSET_DIR"/badge-b8-*.svg)
if (( ${#SVG_FILES[@]} != 40 )); then
  print -u2 "Expected 40 B8 SVG files, found ${#SVG_FILES[@]}."
  exit 65
fi

xcrun swift \
  -module-cache-path "$MODULE_CACHE" \
  "$TOOL_DIR/render_svg.swift" \
  "$ASSET_DIR" \
  "${SVG_FILES[@]}"

python3 "$TOOL_DIR/normalize_badge_artwork.py" \
  --directory "$ASSET_DIR"
python3 "$TOOL_DIR/validate_b8_assets.py"

print "Built, normalized and validated 40 B8 SVG/PNG assets."
