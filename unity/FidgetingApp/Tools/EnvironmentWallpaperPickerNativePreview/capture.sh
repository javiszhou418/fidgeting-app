#!/bin/zsh
set -euo pipefail

TOOL_DIR="${0:A:h}"
PROJECT_ROOT="${TOOL_DIR:h:h}"
ARTIFACT_DIR="$PROJECT_ROOT/Artifacts/EnvironmentWallpaperPickerNativePreview"
BUILD_ROOT="$(mktemp -d /tmp/fidget-environment-picker-preview.XXXXXX)"
MODULE_CACHE="$BUILD_ROOT/ModuleCache"
APP_DIR="$BUILD_ROOT/EnvironmentWallpaperPickerNativePreview.app"
APP_BINARY="$APP_DIR/EnvironmentWallpaperPickerNativePreview"
BUNDLE_ID="com.jiaweizhou.fidgetspinner.environment-picker-preview"

mkdir -p "$MODULE_CACHE" "$APP_DIR" "$ARTIFACT_DIR"

build_preview() {
  local mode="$1"
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
    "$TOOL_DIR/EnvironmentWallpaperPickerNativePreviewApp.swift" \
    -o "$APP_BINARY"
}

cp "$TOOL_DIR/Info.plist" "$APP_DIR/Info.plist"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf" \
  "$APP_DIR/Oxanium-VariableFont_wght.ttf"
for WALLPAPER in "$PROJECT_ROOT"/Assets/Plugins/iOS/SceneWallpapers/*.png; do
  cp "$WALLPAPER" "$APP_DIR/${WALLPAPER:t}"
done

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

for MODE in adaptive canyon cyberpunk mineral-ridge; do
  MODE_BUNDLE_ID="$BUNDLE_ID.$MODE"
  build_preview "$MODE"
  cp "$TOOL_DIR/Info.plist" "$APP_DIR/Info.plist"
  plutil -replace CFBundleIdentifier -string "$MODE_BUNDLE_ID" \
    "$APP_DIR/Info.plist"
  codesign --force --sign - "$APP_DIR" >/dev/null
  xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID.canyon" 2>/dev/null || true
  xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID.cyberpunk" 2>/dev/null || true
  xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID.adaptive" 2>/dev/null || true
  xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID.mineral-ridge" 2>/dev/null || true
  xcrun simctl terminate "$DEVICE_ID" "$MODE_BUNDLE_ID" 2>/dev/null || true
  xcrun simctl uninstall "$DEVICE_ID" "$MODE_BUNDLE_ID" 2>/dev/null || true
  xcrun simctl install "$DEVICE_ID" "$APP_DIR"
  xcrun simctl launch --terminate-running-process \
    "$DEVICE_ID" "$MODE_BUNDLE_ID" --mode="$MODE" >/dev/null
  sleep 7
  xcrun simctl io "$DEVICE_ID" screenshot \
    "$ARTIFACT_DIR/environment-picker-$MODE.png" >/dev/null
done

ffmpeg -y \
  -i "$ARTIFACT_DIR/environment-picker-adaptive.png" \
  -i "$ARTIFACT_DIR/environment-picker-canyon.png" \
  -i "$ARTIFACT_DIR/environment-picker-cyberpunk.png" \
  -i "$ARTIFACT_DIR/environment-picker-mineral-ridge.png" \
  -filter_complex "[0:v]scale=300:-1[a];[1:v]scale=300:-1[b];[2:v]scale=300:-1[c];[3:v]scale=300:-1[d];[a][b][c][d]hstack=inputs=4" \
  -frames:v 1 \
  "$ARTIFACT_DIR/environment-picker-contact-sheet.png" >/dev/null 2>&1

print "Captured environment picker previews in $ARTIFACT_DIR"
