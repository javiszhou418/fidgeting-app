#!/bin/zsh
set -euo pipefail

TOOL_DIR="${0:A:h}"
PROJECT_ROOT="${TOOL_DIR:h:h}"
ARTIFACT_DIR="${1:-$PROJECT_ROOT/Artifacts/ProductIdentityNativePreview}"
BUILD_ROOT="$(mktemp -d /tmp/fidget-product-identity-preview.XXXXXX)"
MODULE_CACHE="$BUILD_ROOT/ModuleCache"
APP_DIR="$BUILD_ROOT/ProductIdentityNativePreview.app"
APP_BINARY="$APP_DIR/ProductIdentityNativePreview"
BUNDLE_ID="com.jiaweizhou.fidgetspinner.product-identity-preview"

mkdir -p "$MODULE_CACHE" "$APP_DIR" "$ARTIFACT_DIR"

xcrun --sdk iphonesimulator swiftc \
  -D DEBUG \
  -parse-as-library \
  -target arm64-apple-ios15.0-simulator \
  -module-cache-path "$MODULE_CACHE" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetProductUIComponents.swift" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetComboHalo.swift" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetGachaPackPresentation.swift" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetGachaRiveGateRules.swift" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetGachaRivePresentation.swift" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetStoreKit.swift" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetGachaStore.swift" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetGachaStorefront.swift" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/CodexSwiftUIOverlay.swift" \
  "$TOOL_DIR/ProductIdentityNativePreviewApp.swift" \
  -o "$APP_BINARY"

cp "$TOOL_DIR/Info.plist" "$APP_DIR/Info.plist"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf" \
  "$APP_DIR/Oxanium-VariableFont_wght.ttf"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/SceneWallpapers/scene-wallpaper-adaptive-gold-four-wing.png" \
  "$APP_DIR/product-identity-gold-background.png"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/SceneWallpapers/scene-wallpaper-adaptive-metal-three-blade.png" \
  "$APP_DIR/product-identity-metal-background.png"
for BADGE_ARTWORK in "$PROJECT_ROOT"/Assets/Plugins/iOS/BadgeArtwork/*.png; do
  cp "$BADGE_ARTWORK" "$APP_DIR/${BADGE_ARTWORK:t}"
done
codesign --force --sign - "$APP_DIR" >/dev/null

DEVICE_ID="$(
  xcrun simctl list devices available \
    | sed -nE 's/^[[:space:]]*iPhone[^\(]*\(([0-9A-F-]{36})\).*/\1/p' \
    | head -1
)"
if [[ -z "$DEVICE_ID" ]]; then
  print -u2 "No available iPhone simulator was found."
  exit 68
fi

xcrun simctl boot "$DEVICE_ID" 2>/dev/null || true
xcrun simctl bootstatus "$DEVICE_ID" -b
xcrun simctl uninstall "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true
xcrun simctl install "$DEVICE_ID" "$APP_DIR"

for MODEL in gold metal; do
  xcrun simctl launch --terminate-running-process \
    "$DEVICE_ID" "$BUNDLE_ID" --model="$MODEL" >/dev/null
  sleep 5
  xcrun simctl io "$DEVICE_ID" screenshot \
    "$ARTIFACT_DIR/product-identity-$MODEL.png" >/dev/null
done

ffmpeg -y \
  -i "$ARTIFACT_DIR/product-identity-gold.png" \
  -i "$ARTIFACT_DIR/product-identity-metal.png" \
  -filter_complex "[0:v][1:v]hstack=inputs=2" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/product-identity-library-contact-sheet.png" >/dev/null 2>&1

print "Captured product identity previews in $ARTIFACT_DIR"
