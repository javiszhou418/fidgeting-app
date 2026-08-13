#!/bin/zsh
set -euo pipefail

TOOL_DIR="${0:A:h}"
PROJECT_ROOT="${TOOL_DIR:h:h}"
ARTIFACT_DIR="$PROJECT_ROOT/Artifacts/SingleDrawStoreDemo"
BUILD_ROOT="$(mktemp -d /tmp/fidget-single-draw-demo.XXXXXX)"
MODULE_CACHE="$BUILD_ROOT/ModuleCache"
APP_DIR="$BUILD_ROOT/SingleDrawStoreDemo.app"
BINARY="$APP_DIR/SingleDrawStoreDemo"
BUNDLE_ID="com.jiaweizhou.fidgeting.single-draw-demo"

mkdir -p "$MODULE_CACHE" "$APP_DIR" "$ARTIFACT_DIR"
xcrun --sdk iphonesimulator swiftc \
  -parse-as-library \
  -target arm64-apple-ios16.0-simulator \
  -module-cache-path "$MODULE_CACHE" \
  "$TOOL_DIR/SingleDrawStoreDemo.swift" \
  "$TOOL_DIR/SingleDrawStoreDemoApp.swift" \
  -o "$BINARY"
cp "$TOOL_DIR/Info.plist" "$APP_DIR/Info.plist"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Thumbnails/Models/product-thumbnail-metal-three-blade.png" "$APP_DIR/"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Thumbnails/Models/product-thumbnail-magnetic-slide-tile.png" "$APP_DIR/"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Thumbnails/Models/product-thumbnail-magnetic-fan-card.png" "$APP_DIR/"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Thumbnails/Models/product-thumbnail-gold-four-wing.png" "$APP_DIR/"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Thumbnails/ThreeBladeSkins/skin-thumbnail-night-cyan-index.png" "$APP_DIR/"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Thumbnails/ThreeBladeSkins/skin-thumbnail-tungsten-honeycomb.png" "$APP_DIR/"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Thumbnails/ThreeBladeSkins/skin-thumbnail-blue-damascus.png" "$APP_DIR/"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Thumbnails/ThreeBladeSkins/skin-thumbnail-titanium-heat.png" "$APP_DIR/"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Thumbnails/ThreeBladeSkins/skin-thumbnail-meteor-obsidian.png" "$APP_DIR/"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Thumbnails/ThreeBladeSkins/skin-thumbnail-mirror-aurora.png" "$APP_DIR/"
cp "$PROJECT_ROOT/Artifacts/DisplayCaseRarityRevealPrototype/storyboard/01-back-facing.png" "$APP_DIR/display-case-reveal-01-back-facing.png"
cp "$PROJECT_ROOT/Artifacts/DisplayCaseRarityRevealPrototype/storyboard/02-flip-to-front.png" "$APP_DIR/display-case-reveal-02-flip-to-front.png"
cp "$PROJECT_ROOT/Artifacts/DisplayCaseRarityRevealPrototype/storyboard/03-prize-readable.png" "$APP_DIR/display-case-reveal-03-prize-readable.png"
cp "$PROJECT_ROOT/Artifacts/DisplayCaseRarityRevealPrototype/storyboard/04-parts-exploded.png" "$APP_DIR/display-case-reveal-04-parts-exploded.png"
cp "$PROJECT_ROOT/Artifacts/DisplayCaseRarityRevealPrototype/storyboard/05-prize-only.png" "$APP_DIR/display-case-reveal-05-prize-only.png"
cp "$PROJECT_ROOT/Artifacts/DisplayCaseRarityRevealPrototype/storyboard/06-light-pass-complete.png" "$APP_DIR/display-case-reveal-06-light-pass-complete.png"
codesign --force --sign - "$APP_DIR" >/dev/null

DEVICE_ID="${1:-$(xcrun simctl list devices available | sed -nE 's/^[[:space:]]*iPhone[^\(]*\(([0-9A-F-]{36})\).*/\1/p' | head -1)}"
[[ -n "$DEVICE_ID" ]] || exit 68
xcrun simctl boot "$DEVICE_ID" 2>/dev/null || true
xcrun simctl bootstatus "$DEVICE_ID" -b
xcrun simctl uninstall "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true
xcrun simctl install "$DEVICE_ID" "$APP_DIR"
xcrun simctl launch --terminate-running-process "$DEVICE_ID" "$BUNDLE_ID" >/dev/null
sleep 4.0
xcrun simctl io "$DEVICE_ID" screenshot "$ARTIFACT_DIR/01-draw-and-redeem.png" >/dev/null
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true

xcrun simctl launch --terminate-running-process "$DEVICE_ID" "$BUNDLE_ID" --preview-home >/dev/null
sleep 3.0
xcrun simctl io "$DEVICE_ID" screenshot "$ARTIFACT_DIR/02-main-entry.png" >/dev/null
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true

VIDEO="$ARTIFACT_DIR/single-draw-demo.mp4"
rm -f "$VIDEO"
xcrun simctl launch --terminate-running-process "$DEVICE_ID" "$BUNDLE_ID" --auto-demo >/dev/null
sleep 0.45
xcrun simctl io "$DEVICE_ID" recordVideo --codec=h264 "$VIDEO" >/dev/null 2>&1 &
RECORDER_PID=$!
sleep 7.3
kill -INT "$RECORDER_PID" 2>/dev/null || true
wait "$RECORDER_PID" 2>/dev/null || true
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true

xcrun simctl launch --terminate-running-process "$DEVICE_ID" "$BUNDLE_ID" --preview-reveal-back >/dev/null
sleep 1.0
xcrun simctl io "$DEVICE_ID" screenshot "$ARTIFACT_DIR/03-reveal-back-facing.png" >/dev/null
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true

xcrun simctl launch --terminate-running-process "$DEVICE_ID" "$BUNDLE_ID" --preview-reveal-front >/dev/null
sleep 1.0
xcrun simctl io "$DEVICE_ID" screenshot "$ARTIFACT_DIR/04-reveal-prize-readable.png" >/dev/null
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true

xcrun simctl launch --terminate-running-process "$DEVICE_ID" "$BUNDLE_ID" --preview-reveal-exploded >/dev/null
sleep 1.0
xcrun simctl io "$DEVICE_ID" screenshot "$ARTIFACT_DIR/05-reveal-parts-exploded.png" >/dev/null
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true

xcrun simctl launch --terminate-running-process "$DEVICE_ID" "$BUNDLE_ID" --preview-reveal-complete >/dev/null
sleep 1.0
xcrun simctl io "$DEVICE_ID" screenshot "$ARTIFACT_DIR/06-reveal-light-pass-complete.png" >/dev/null
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true

xcrun simctl launch --terminate-running-process "$DEVICE_ID" "$BUNDLE_ID" --preview-collection >/dev/null
sleep 1.0
xcrun simctl io "$DEVICE_ID" screenshot "$ARTIFACT_DIR/07-collection.png" >/dev/null
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true

xcrun simctl launch --terminate-running-process "$DEVICE_ID" "$BUNDLE_ID" --preview-probability >/dev/null
sleep 1.0
xcrun simctl io "$DEVICE_ID" screenshot "$ARTIFACT_DIR/08-probability-detail.png" >/dev/null
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true

ffmpeg -y \
  -i "$ARTIFACT_DIR/01-draw-and-redeem.png" \
  -i "$ARTIFACT_DIR/02-main-entry.png" \
  -i "$ARTIFACT_DIR/03-reveal-back-facing.png" \
  -i "$ARTIFACT_DIR/04-reveal-prize-readable.png" \
  -i "$ARTIFACT_DIR/05-reveal-parts-exploded.png" \
  -i "$ARTIFACT_DIR/06-reveal-light-pass-complete.png" \
  -filter_complex "[0:v]scale=220:-1[a];[1:v]scale=220:-1[b];[2:v]scale=220:-1[c];[3:v]scale=220:-1[d];[4:v]scale=220:-1[e];[5:v]scale=220:-1[f];[a][b][c][d][e][f]hstack=inputs=6[out]" \
  -map "[out]" -frames:v 1 -update 1 \
  "$ARTIFACT_DIR/single-draw-demo-contact-sheet.png" >/dev/null 2>&1

print "Captured isolated single-draw demo in $ARTIFACT_DIR"
