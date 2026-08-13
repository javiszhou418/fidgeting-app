#!/bin/zsh
set -euo pipefail

TOOL_DIR="${0:A:h}"
PROJECT_ROOT="${TOOL_DIR:h:h}"
ARTIFACT_DIR="$PROJECT_ROOT/Artifacts/HapticSettingsSavePreview"
BUILD_ROOT="$(mktemp -d /tmp/fidget-haptic-settings-preview.XXXXXX)"
MODULE_CACHE="$BUILD_ROOT/ModuleCache"
SOURCE_ROOT="$BUILD_ROOT/Sources"
APP_DIR="$BUILD_ROOT/HapticSettingsNativePreview.app"
APP_BINARY="$APP_DIR/HapticSettingsNativePreview"
BUNDLE_ID="com.jiaweizhou.fidgetspinner.haptic-settings-preview"

mkdir -p "$MODULE_CACHE" "$SOURCE_ROOT" "$APP_DIR" "$ARTIFACT_DIR"

# Freeze one immutable source snapshot before compilation. The live Unity
# project can remain open without producing a mixed-source preview binary.
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetProductUIComponents.swift" \
  "$SOURCE_ROOT/FidgetProductUIComponents.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetComboHalo.swift" \
  "$SOURCE_ROOT/FidgetComboHalo.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/CodexSwiftUIOverlay.swift" \
  "$SOURCE_ROOT/CodexSwiftUIOverlay.swift"
cp "$TOOL_DIR/HapticSettingsNativePreviewApp.swift" \
  "$SOURCE_ROOT/HapticSettingsNativePreviewApp.swift"

xcrun --sdk iphonesimulator swiftc \
  -D DEBUG \
  -parse-as-library \
  -target arm64-apple-ios15.0-simulator \
  -module-cache-path "$MODULE_CACHE" \
  "$SOURCE_ROOT/FidgetProductUIComponents.swift" \
  "$SOURCE_ROOT/FidgetComboHalo.swift" \
  "$SOURCE_ROOT/CodexSwiftUIOverlay.swift" \
  "$SOURCE_ROOT/HapticSettingsNativePreviewApp.swift" \
  -o "$APP_BINARY"

cp "$PROJECT_ROOT/Tools/ComboHaloNativePreview/Info.plist" "$APP_DIR/Info.plist"
plutil -replace CFBundleExecutable -string "HapticSettingsNativePreview" \
  "$APP_DIR/Info.plist"
plutil -replace CFBundleIdentifier -string "$BUNDLE_ID" "$APP_DIR/Info.plist"
plutil -replace CFBundleDisplayName -string "Haptic Settings Preview" \
  "$APP_DIR/Info.plist"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf" \
  "$APP_DIR/Oxanium-VariableFont_wght.ttf"
codesign --force --sign - "$APP_DIR" >/dev/null

DEVICE_ID="${HAPTIC_SETTINGS_PREVIEW_DEVICE_ID:-}"
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
xcrun simctl launch --terminate-running-process "$DEVICE_ID" "$BUNDLE_ID" >/dev/null
sleep 2
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/haptic-settings-save-full.png" >/dev/null

ffmpeg -y \
  -i "$ARTIFACT_DIR/haptic-settings-save-full.png" \
  -vf "crop=iw:520:0:0" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/haptic-settings-save-top.png" >/dev/null 2>&1

print "Captured shipping Haptic settings preview in $ARTIFACT_DIR"
