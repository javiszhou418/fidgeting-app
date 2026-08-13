#!/bin/zsh
set -euo pipefail

TOOL_DIR="${0:A:h}"
PROJECT_ROOT="${TOOL_DIR:h:h}"
ARTIFACT_DIR="$PROJECT_ROOT/Artifacts/PremiumDisplayCaseNativePreview"
BUILD_ROOT="$(mktemp -d /tmp/fidget-display-case-preview.XXXXXX)"
MODULE_CACHE="$BUILD_ROOT/ModuleCache"
SOURCE_ROOT="$BUILD_ROOT/Sources"
APP_DIR="$BUILD_ROOT/DisplayCaseNativePreview.app"
APP_BINARY="$APP_DIR/DisplayCaseNativePreview"
BUNDLE_ID="com.jiaweizhou.fidgetspinner.display-case-preview"

mkdir -p "$MODULE_CACHE" "$SOURCE_ROOT" "$APP_DIR" "$ARTIFACT_DIR"

cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetProductUIComponents.swift" \
  "$SOURCE_ROOT/FidgetProductUIComponents.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetComboHalo.swift" \
  "$SOURCE_ROOT/FidgetComboHalo.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetStoreKit.swift" \
  "$SOURCE_ROOT/FidgetStoreKit.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetGachaStore.swift" \
  "$SOURCE_ROOT/FidgetGachaStore.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/CodexSwiftUIOverlay.swift" \
  "$SOURCE_ROOT/CodexSwiftUIOverlay.swift"
cp "$TOOL_DIR/DisplayCaseNativePreviewApp.swift" \
  "$SOURCE_ROOT/DisplayCaseNativePreviewApp.swift"

xcrun --sdk iphonesimulator swiftc \
  -D DEBUG \
  -parse-as-library \
  -target arm64-apple-ios15.0-simulator \
  -module-cache-path "$MODULE_CACHE" \
  "$SOURCE_ROOT/FidgetProductUIComponents.swift" \
  "$SOURCE_ROOT/FidgetComboHalo.swift" \
  "$SOURCE_ROOT/FidgetStoreKit.swift" \
  "$SOURCE_ROOT/FidgetGachaStore.swift" \
  "$SOURCE_ROOT/CodexSwiftUIOverlay.swift" \
  "$SOURCE_ROOT/DisplayCaseNativePreviewApp.swift" \
  -o "$APP_BINARY"

cp "$PROJECT_ROOT/Tools/ComboHaloNativePreview/Info.plist" "$APP_DIR/Info.plist"
plutil -replace CFBundleExecutable -string "DisplayCaseNativePreview" \
  "$APP_DIR/Info.plist"
plutil -replace CFBundleIdentifier -string "$BUNDLE_ID" "$APP_DIR/Info.plist"
plutil -replace CFBundleDisplayName -string "Display Case Preview" \
  "$APP_DIR/Info.plist"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf" \
  "$APP_DIR/Oxanium-VariableFont_wght.ttf"
cp "$PROJECT_ROOT/Artifacts/PremiumDisplayCasePreview/11_phone_hero.png" \
  "$APP_DIR/premium-display-case-unity-hero.png"
codesign --force --sign - "$APP_DIR" >/dev/null

DEVICE_ID="${DISPLAY_CASE_PREVIEW_DEVICE_ID:-}"
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
# A freshly installed SwiftUI-only preview can stay on the system launch screen
# for several seconds while the Simulator creates its first scene. Capturing
# earlier produces a false-success white screenshot even though the process is
# healthy. Keep this deterministic headroom before taking the visual artifact.
sleep 15
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/display-case-native-controls.png" >/dev/null

print "Captured shipping display-case native preview in $ARTIFACT_DIR"
