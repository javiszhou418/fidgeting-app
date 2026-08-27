#!/bin/zsh
set -euo pipefail

TOOL_DIR="${0:A:h}"
PROJECT_ROOT="${TOOL_DIR:h:h}"
ARTIFACT_DIR="$PROJECT_ROOT/Artifacts/GachaPackShippingNativePreview"
BUILD_ROOT="$(mktemp -d /tmp/fidget-gacha-pack-preview.XXXXXX)"
MODULE_CACHE="$BUILD_ROOT/ModuleCache"
SOURCE_ROOT="$BUILD_ROOT/Sources"
APP_DIR="$BUILD_ROOT/GachaShippingNativePreview.app"
APP_BINARY="$APP_DIR/GachaShippingNativePreview"
BUNDLE_ID="com.jiaweizhou.fidgeting.gacha-shipping-preview"

mkdir -p "$MODULE_CACHE" "$SOURCE_ROOT" "$APP_DIR" "$ARTIFACT_DIR"

for SOURCE in \
  FidgetProductUIComponents.swift \
  FidgetGachaPackPresentation.swift \
  FidgetGachaRiveGateRules.swift \
  FidgetGachaRivePresentation.swift \
  FidgetGachaStore.swift \
  FidgetStoreKit.swift \
  FidgetGachaStorefront.swift; do
  cp "$PROJECT_ROOT/Assets/Plugins/iOS/$SOURCE" "$SOURCE_ROOT/$SOURCE"
done
cp "$TOOL_DIR/GachaShippingNativePreviewApp.swift" \
  "$SOURCE_ROOT/GachaShippingNativePreviewApp.swift"

xcrun --sdk iphonesimulator swiftc \
  -D DEBUG \
  -parse-as-library \
  -target arm64-apple-ios15.0-simulator \
  -module-cache-path "$MODULE_CACHE" \
  "$SOURCE_ROOT/FidgetProductUIComponents.swift" \
  "$SOURCE_ROOT/FidgetGachaPackPresentation.swift" \
  "$SOURCE_ROOT/FidgetGachaRiveGateRules.swift" \
  "$SOURCE_ROOT/FidgetGachaRivePresentation.swift" \
  "$SOURCE_ROOT/FidgetGachaStore.swift" \
  "$SOURCE_ROOT/FidgetStoreKit.swift" \
  "$SOURCE_ROOT/FidgetGachaStorefront.swift" \
  "$SOURCE_ROOT/GachaShippingNativePreviewApp.swift" \
  -o "$APP_BINARY"

cp "$TOOL_DIR/Info.plist" "$APP_DIR/Info.plist"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf" \
  "$APP_DIR/Oxanium-VariableFont_wght.ttf"
for ARTWORK in "$PROJECT_ROOT"/Assets/Plugins/iOS/GachaPacks/*.png; do
  cp "$ARTWORK" "$APP_DIR/${ARTWORK:t}"
done
for ARTWORK in "$PROJECT_ROOT"/Assets/Plugins/iOS/Thumbnails/**/*.png; do
  cp "$ARTWORK" "$APP_DIR/${ARTWORK:t}"
done
for ARTWORK in "$PROJECT_ROOT"/Assets/Plugins/iOS/GachaBanners/*.png; do
  cp "$ARTWORK" "$APP_DIR/${ARTWORK:t}"
done
codesign --force --sign - "$APP_DIR" >/dev/null

DEVICE_ID="${GACHA_PACK_PREVIEW_DEVICE_ID:-}"
if [[ -z "$DEVICE_ID" ]]; then
  DEVICE_ID="$(
    xcrun simctl list devices available \
      | sed -nE 's/^[[:space:]]*iPhone[^\(]*\(([0-9A-F-]{36})\).*/\1/p' \
      | head -1
  )"
fi
if [[ -z "$DEVICE_ID" ]]; then
  print -u2 "No available iPhone simulator was found."
  exit 68
fi

xcrun simctl boot "$DEVICE_ID" 2>/dev/null || true
xcrun simctl bootstatus "$DEVICE_ID" -b
xcrun simctl uninstall "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true
xcrun simctl install "$DEVICE_ID" "$APP_DIR"

xcrun simctl launch --terminate-running-process \
  "$DEVICE_ID" "$BUNDLE_ID" \
  --preview-auto-single-draw --preview-carousel-tier=signature >/dev/null
sleep 2
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/00-pack-carousel-selected-emphasis-outward-arc.png" >/dev/null

xcrun simctl launch --terminate-running-process \
  "$DEVICE_ID" "$BUNDLE_ID" >/dev/null
sleep 5
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/01-storefront-pack-entry.png" >/dev/null

xcrun simctl launch --terminate-running-process \
  "$DEVICE_ID" "$BUNDLE_ID" --preview-reveal >/dev/null
sleep 2
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/02-pack-sealed.png" >/dev/null

xcrun simctl launch --terminate-running-process \
  "$DEVICE_ID" "$BUNDLE_ID" --preview-reveal --preview-pack-progress=0.68 >/dev/null
sleep 2
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/03-pack-tear-68.png" >/dev/null

xcrun simctl launch --terminate-running-process \
  "$DEVICE_ID" "$BUNDLE_ID" --preview-reveal --preview-pack-opened >/dev/null
sleep 2
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/04-after-tear-case-back.png" >/dev/null

xcrun simctl launch --terminate-running-process \
  "$DEVICE_ID" "$BUNDLE_ID" --preview-all-pack-tiers=0 >/dev/null
sleep 2
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/05-six-tier-sealed.png" >/dev/null

xcrun simctl launch --terminate-running-process \
  "$DEVICE_ID" "$BUNDLE_ID" --preview-all-pack-tiers=0.68 >/dev/null
sleep 2
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/06-six-tier-tear-68.png" >/dev/null

ffmpeg -y \
  -i "$ARTIFACT_DIR/01-storefront-pack-entry.png" \
  -i "$ARTIFACT_DIR/02-pack-sealed.png" \
  -i "$ARTIFACT_DIR/03-pack-tear-68.png" \
  -i "$ARTIFACT_DIR/04-after-tear-case-back.png" \
  -filter_complex \
  "[0:v]scale=300:-1[a];[1:v]scale=300:-1[b];[2:v]scale=300:-1[c];[3:v]scale=300:-1[d];[a][b][c][d]hstack=inputs=4[out]" \
  -map "[out]" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/gacha-pack-v7-shipping-contact-sheet.png" >/dev/null 2>&1

ffmpeg -y \
  -i "$ARTIFACT_DIR/05-six-tier-sealed.png" \
  -i "$ARTIFACT_DIR/06-six-tier-tear-68.png" \
  -filter_complex \
  "[0:v]scale=600:-1[a];[1:v]scale=600:-1[b];[a][b]hstack=inputs=2[out]" \
  -map "[out]" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/gacha-pack-six-tier-shipping-contact-sheet.png" >/dev/null 2>&1

sips -g pixelWidth -g pixelHeight \
  "$ARTIFACT_DIR/gacha-pack-v7-shipping-contact-sheet.png" \
  "$ARTIFACT_DIR/gacha-pack-six-tier-shipping-contact-sheet.png"
print "Captured shipping Gacha Pack V7 native previews in $ARTIFACT_DIR"
