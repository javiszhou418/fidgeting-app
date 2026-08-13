#!/bin/zsh
set -euo pipefail

TOOL_DIR="${0:A:h}"
PROJECT_ROOT="${TOOL_DIR:h:h}"
ARTIFACT_DIR="$PROJECT_ROOT/Artifacts/ProgressionCelebrationNativePreview"
BUILD_ROOT="$(mktemp -d /tmp/fidget-progression-celebration-preview.XXXXXX)"
MODULE_CACHE="$BUILD_ROOT/ModuleCache"
APP_DIR="$BUILD_ROOT/ProgressionCelebrationNativePreview.app"
APP_BINARY="$APP_DIR/ProgressionCelebrationNativePreview"
SOURCE_SNAPSHOT_DIR="$BUILD_ROOT/Sources"
BUNDLE_ID="com.jiaweizhou.fidgetspinner.progression-celebration-preview"

mkdir -p "$MODULE_CACHE" "$APP_DIR" "$ARTIFACT_DIR" "$SOURCE_SNAPSHOT_DIR"

for SOURCE in \
  FidgetProductUIComponents.swift \
  FidgetComboHalo.swift \
  FidgetStoreKit.swift \
  FidgetGachaStore.swift \
  CodexSwiftUIOverlay.swift; do
  cp "$PROJECT_ROOT/Assets/Plugins/iOS/$SOURCE" "$SOURCE_SNAPSHOT_DIR/$SOURCE"
done

xcrun --sdk iphonesimulator swiftc \
  -D DEBUG \
  -parse-as-library \
  -target arm64-apple-ios15.0-simulator \
  -module-cache-path "$MODULE_CACHE" \
  "$SOURCE_SNAPSHOT_DIR/FidgetProductUIComponents.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetComboHalo.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetStoreKit.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetGachaStore.swift" \
  "$SOURCE_SNAPSHOT_DIR/CodexSwiftUIOverlay.swift" \
  "$TOOL_DIR/ProgressionCelebrationNativePreviewApp.swift" \
  -o "$APP_BINARY"

cp "$TOOL_DIR/Info.plist" "$APP_DIR/Info.plist"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf" \
  "$APP_DIR/Oxanium-VariableFont_wght.ttf"
codesign --force --sign - "$APP_DIR" >/dev/null

DEVICE_ID="${1:-$(
  xcrun simctl list devices available \
    | sed -nE 's/^[[:space:]]*iPhone[^\(]*\(([0-9A-F-]{36})\).*/\1/p' \
    | head -1
)}"
if [[ -z "$DEVICE_ID" ]]; then
  print -u2 "No available iPhone simulator was found."
  exit 68
fi

xcrun simctl boot "$DEVICE_ID" 2>/dev/null || true
xcrun simctl bootstatus "$DEVICE_ID" -b
xcrun simctl uninstall "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true
xcrun simctl install "$DEVICE_ID" "$APP_DIR"

# Prewarm the freshly installed SwiftUI app so the captured sequence begins at
# the real bottom-sheet animation rather than the Simulator launch screen.
xcrun simctl launch --terminate-running-process \
  "$DEVICE_ID" "$BUNDLE_ID" --mode=offlineNoLevel >/dev/null
sleep 5.0
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID"
sleep 0.25

VIDEO_PATH="$ARTIFACT_DIR/offline-growth-page-flight.mp4"
rm -f "$VIDEO_PATH"
xcrun simctl launch --terminate-running-process \
  "$DEVICE_ID" "$BUNDLE_ID" --mode=offlineNoLevel >/dev/null
sleep 0.45
xcrun simctl io "$DEVICE_ID" recordVideo --codec=h264 "$VIDEO_PATH" >/dev/null 2>&1 &
RECORDER_PID=$!
sleep 1.10
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/offline-sheet-active.png" >/dev/null
sleep 1.72
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/offline-sheet-dismissed-page-restored.png" >/dev/null
sleep 0.78
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/offline-page-xp-flight.png" >/dev/null
sleep 1.25
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/offline-top-avatar-updated.png" >/dev/null
kill -INT "$RECORDER_PID" 2>/dev/null || true
wait "$RECORDER_PID" 2>/dev/null || true
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true
sleep 0.45

xcrun simctl launch --terminate-running-process \
  "$DEVICE_ID" "$BUNDLE_ID" --mode=offline >/dev/null
sleep 2.55
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/offline-level-up.png" >/dev/null
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true
sleep 0.45

xcrun simctl launch --terminate-running-process \
  "$DEVICE_ID" "$BUNDLE_ID" --mode=live >/dev/null
sleep 2.45
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/live-level-up.png" >/dev/null
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true
sleep 0.35

xcrun simctl launch --terminate-running-process \
  "$DEVICE_ID" "$BUNDLE_ID" --mode=offlineNoLevel --reduce-motion >/dev/null
sleep 2.80
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/offline-reduce-motion-top-avatar.png" >/dev/null
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true

ffmpeg -y \
  -i "$ARTIFACT_DIR/offline-sheet-active.png" \
  -i "$ARTIFACT_DIR/offline-sheet-dismissed-page-restored.png" \
  -i "$ARTIFACT_DIR/offline-page-xp-flight.png" \
  -i "$ARTIFACT_DIR/offline-top-avatar-updated.png" \
  -filter_complex \
  "[0:v]scale=260:-1[sheet];[1:v]scale=260:-1[restored];[2:v]scale=260:-1[flight];[3:v]scale=260:-1[avatar];[sheet][restored][flight][avatar]hstack=inputs=4[out]" \
  -map "[out]" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/progression-celebration-contact-sheet.png" >/dev/null 2>&1

ffmpeg -y \
  -i "$ARTIFACT_DIR/offline-level-up.png" \
  -i "$ARTIFACT_DIR/live-level-up.png" \
  -filter_complex \
  "[0:v]scale=360:-1[offline];[1:v]scale=360:-1[live];[offline][live]hstack=inputs=2[out]" \
  -map "[out]" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/progression-level-up-contact-sheet.png" >/dev/null 2>&1

sips -g pixelWidth -g pixelHeight \
  "$ARTIFACT_DIR/progression-celebration-contact-sheet.png"
print "Captured shipping progression celebration previews in $ARTIFACT_DIR"
