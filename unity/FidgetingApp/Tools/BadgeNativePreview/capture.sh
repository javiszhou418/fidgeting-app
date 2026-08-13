#!/bin/zsh
set -euo pipefail

TOOL_DIR="${0:A:h}"
PROJECT_ROOT="${TOOL_DIR:h:h}"
ARTIFACT_DIR="$PROJECT_ROOT/Artifacts/BadgeSpecial/NativeB8"
BUILD_ROOT="$(mktemp -d /tmp/fidget-badge-native-preview.XXXXXX)"
MODULE_CACHE="$BUILD_ROOT/ModuleCache"
APP_DIR="$BUILD_ROOT/BadgeNativePreview.app"
APP_BINARY="$APP_DIR/BadgeNativePreview"
SOURCE_SNAPSHOT_DIR="$BUILD_ROOT/Sources"
BUNDLE_ID="com.jiaweizhou.fidgetspinner.badge-native-preview"

mkdir -p "$MODULE_CACHE" "$APP_DIR" "$ARTIFACT_DIR" "$SOURCE_SNAPSHOT_DIR"

# The preview is a release gate, so it must never package stale PNGs left from
# an earlier SVG iteration. Rebuild and validate the complete asset bundle first.
zsh "$PROJECT_ROOT/Tools/BadgeAssetGenerator/build_b8_assets.sh"

# Compile an immutable point-in-time copy. The canonical Unity project may be
# open while visual work continues, and swiftc rejects an input whose mtime
# changes during compilation. Snapshotting also guarantees that every image in
# one contact sheet comes from the exact same source revision.
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetProductUIComponents.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetProductUIComponents.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetComboHalo.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetComboHalo.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/CodexSwiftUIOverlay.swift" \
  "$SOURCE_SNAPSHOT_DIR/CodexSwiftUIOverlay.swift"

xcrun --sdk iphonesimulator swiftc \
  -D DEBUG \
  -parse-as-library \
  -target arm64-apple-ios15.0-simulator \
  -module-cache-path "$MODULE_CACHE" \
  "$SOURCE_SNAPSHOT_DIR/FidgetProductUIComponents.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetComboHalo.swift" \
  "$SOURCE_SNAPSHOT_DIR/CodexSwiftUIOverlay.swift" \
  "$TOOL_DIR/BadgeNativePreviewApp.swift" \
  -o "$APP_BINARY"

cp "$TOOL_DIR/Info.plist" "$APP_DIR/Info.plist"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf" \
  "$APP_DIR/Oxanium-VariableFont_wght.ttf"
for ARTWORK in "$PROJECT_ROOT"/Assets/Plugins/iOS/BadgeArtwork/*.png; do
  cp "$ARTWORK" "$APP_DIR/${ARTWORK:t}"
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

for MODE in catalog detail states unlock share reference; do
  xcrun simctl launch --terminate-running-process \
    "$DEVICE_ID" "$BUNDLE_ID" --mode="$MODE" >/dev/null
  if [[ "$MODE" == "catalog" ]]; then
    sleep 5
  else
    sleep 2
  fi
  xcrun simctl io "$DEVICE_ID" screenshot \
    "$ARTIFACT_DIR/badge-native-$MODE.png" >/dev/null
done

DATA_CONTAINER="$(xcrun simctl get_app_container "$DEVICE_ID" "$BUNDLE_ID" data)"
cp "$DATA_CONTAINER/Documents/badge-share-card-1080.png" \
  "$ARTIFACT_DIR/badge-share-card-1080.png"

ffmpeg -y \
  -i "$ARTIFACT_DIR/badge-native-catalog.png" \
  -i "$ARTIFACT_DIR/badge-native-detail.png" \
  -i "$ARTIFACT_DIR/badge-native-states.png" \
  -i "$ARTIFACT_DIR/badge-native-unlock.png" \
  -filter_complex \
  "[0:v]scale=280:-1[catalog];[1:v]scale=280:-1[detail];[2:v]scale=280:-1[states];[3:v]scale=280:-1[unlock];[catalog][detail][states][unlock]hstack=inputs=4[out]" \
  -map "[out]" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/badge-native-contact-sheet.png" >/dev/null 2>&1

sips -g pixelWidth -g pixelHeight \
  "$ARTIFACT_DIR/badge-share-card-1080.png"
print "Captured shipping native Badge previews in $ARTIFACT_DIR"
