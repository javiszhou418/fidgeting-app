#!/bin/zsh
set -euo pipefail

TOOL_DIR="${0:A:h}"
PROJECT_ROOT="${TOOL_DIR:h:h}"
ARTIFACT_DIR="${1:-$PROJECT_ROOT/Artifacts/ProgressionThumbnailRecoveryV24}"
BUILD_ROOT="$(mktemp -d /tmp/fidget-progression-thumbnail-preview.XXXXXX)"
MODULE_CACHE="$BUILD_ROOT/ModuleCache"
APP_DIR="$BUILD_ROOT/ProgressionThumbnailNativePreview.app"
APP_BINARY="$APP_DIR/ProgressionThumbnailNativePreview"
BUNDLE_ID="com.jiaweizhou.fidgetspinner.progression-thumbnail-preview"

mkdir -p "$MODULE_CACHE" "$APP_DIR" "$ARTIFACT_DIR"

xcrun --sdk iphonesimulator swiftc \
  -D DEBUG \
  -parse-as-library \
  -target arm64-apple-ios15.0-simulator \
  -module-cache-path "$MODULE_CACHE" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetProductUIComponents.swift" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetComboHalo.swift" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/CodexSwiftUIOverlay.swift" \
  "$TOOL_DIR/ProgressionThumbnailNativePreviewApp.swift" \
  -o "$APP_BINARY"

cp "$TOOL_DIR/Info.plist" "$APP_DIR/Info.plist"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf" \
  "$APP_DIR/Oxanium-VariableFont_wght.ttf"
for THUMBNAIL in \
  "$PROJECT_ROOT"/Assets/Plugins/iOS/Thumbnails/Models/*.png \
  "$PROJECT_ROOT"/Assets/Plugins/iOS/Thumbnails/ThreeBladeSkins/*.png; do
  cp "$THUMBNAIL" "$APP_DIR/${THUMBNAIL:t}"
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

for MODE in top hud hud-off sheet; do
  xcrun simctl launch --terminate-running-process \
    "$DEVICE_ID" "$BUNDLE_ID" --mode="$MODE" >/dev/null
  sleep 4
  xcrun simctl io "$DEVICE_ID" screenshot \
    "$ARTIFACT_DIR/progression-thumbnail-$MODE.png" >/dev/null
done

ffmpeg -y \
  -i "$ARTIFACT_DIR/progression-thumbnail-top.png" \
  -i "$ARTIFACT_DIR/progression-thumbnail-hud.png" \
  -filter_complex \
  "[0:v]crop=iw:480:0:0[top];[1:v]crop=iw:480:0:ih-600[bottom];[top][bottom]vstack=inputs=2" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/progression-endpoint-top-bottom-contact-sheet.png" >/dev/null 2>&1

xcrun simctl launch --terminate-running-process \
  "$DEVICE_ID" "$BUNDLE_ID" --mode=hud >/dev/null
xcrun simctl io "$DEVICE_ID" recordVideo \
  --codec=h264 "$BUILD_ROOT/progression-hud-motion-raw.mp4" >/dev/null 2>&1 &
RECORD_PID=$!
sleep 3
kill -INT "$RECORD_PID"
wait "$RECORD_PID" || true

ffmpeg -y \
  -i "$BUILD_ROOT/progression-hud-motion-raw.mp4" \
  -vf fps=60 \
  -c:v libx264 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  "$ARTIFACT_DIR/progression-hud-auto-motion.mp4" >/dev/null 2>&1

ffmpeg -y \
  -i "$ARTIFACT_DIR/progression-hud-auto-motion.mp4" \
  -vf "fps=4,scale=241:-1,tile=5x2:padding=6:margin=6" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/progression-hud-auto-motion-contact-sheet.png" >/dev/null 2>&1

print "Captured progression thumbnail previews in $ARTIFACT_DIR"
