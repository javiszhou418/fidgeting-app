#!/bin/zsh
set -euo pipefail
unsetopt BG_NICE

TOOL_DIR="${0:A:h}"
PROJECT_ROOT="${TOOL_DIR:h:h}"
ARTIFACT_DIR="$PROJECT_ROOT/Artifacts/ComboHaloNativePreview"
BUILD_ROOT="$(mktemp -d /tmp/fidget-combo-halo-preview.XXXXXX)"
MODULE_CACHE="$BUILD_ROOT/ModuleCache"
APP_DIR="$BUILD_ROOT/ComboHaloNativePreview.app"
APP_BINARY="$APP_DIR/ComboHaloNativePreview"
BUNDLE_ID="com.jiaweizhou.fidgetspinner.combo-halo-preview"

cleanup() {
  if [[ -n "${RECORD_PID:-}" ]]; then
    kill -INT "$RECORD_PID" 2>/dev/null || true
  fi
}
trap cleanup EXIT INT TERM

mkdir -p "$MODULE_CACHE" "$APP_DIR" "$ARTIFACT_DIR"
for PREVIOUS_ARTIFACT in \
  combo-halo-effect-38.png \
  combo-halo-effect-hero-38.png \
  combo-halo-effect-top-38.png \
  combo-halo-effect-left-38.png \
  combo-halo-effect-right-38.png \
  combo-halo-effect-low-38.png \
  combo-halo-curve-tool.png \
  combo-halo-motion.mp4 \
  combo-halo-motion-contact-sheet.png \
  combo-halo-burst-contact-sheet.png \
  combo-halo-angle-contact-sheet.png; do
  if [[ -f "$ARTIFACT_DIR/$PREVIOUS_ARTIFACT" ]]; then
    mv "$ARTIFACT_DIR/$PREVIOUS_ARTIFACT" \
      "$BUILD_ROOT/previous-$PREVIOUS_ARTIFACT"
  fi
done

xcrun --sdk iphonesimulator swiftc \
  -D DEBUG \
  -parse-as-library \
  -target arm64-apple-ios15.0-simulator \
  -module-cache-path "$MODULE_CACHE" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetProductUIComponents.swift" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetComboHalo.swift" \
  "$PROJECT_ROOT/Assets/Plugins/iOS/CodexSwiftUIOverlay.swift" \
  "$TOOL_DIR/ComboHaloNativePreviewApp.swift" \
  -o "$APP_BINARY"

cp "$TOOL_DIR/Info.plist" "$APP_DIR/Info.plist"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf" \
  "$APP_DIR/Oxanium-VariableFont_wght.ttf"
cp "$PROJECT_ROOT/Artifacts/ThreeBladeRotorAxisCenterV2/view-hero-42.png" \
  "$APP_DIR/UnityHero.png"
cp "$PROJECT_ROOT/Artifacts/ThreeBladeRotorAxisCenterV2/view-top-89.png" \
  "$APP_DIR/UnityTop.png"
cp "$PROJECT_ROOT/Artifacts/ThreeBladeRotorAxisCenterV2/view-left-oblique-35.png" \
  "$APP_DIR/UnityLeft.png"
cp "$PROJECT_ROOT/Artifacts/ThreeBladeRotorAxisCenterV2/view-right-oblique-35.png" \
  "$APP_DIR/UnityRight.png"
cp "$PROJECT_ROOT/Artifacts/ThreeBladeRotorAxisCenterV2/view-low-15.png" \
  "$APP_DIR/UnityLow.png"
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

xcrun simctl launch --terminate-running-process "$DEVICE_ID" "$BUNDLE_ID" \
  --mode=effect --view=hero --progress=0.38 >/dev/null
sleep 2.5
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/combo-halo-effect-38.png" >/dev/null
cp "$ARTIFACT_DIR/combo-halo-effect-38.png" \
  "$ARTIFACT_DIR/combo-halo-effect-hero-38.png"

for SCENE_VIEW in top left right low; do
  xcrun simctl launch --terminate-running-process "$DEVICE_ID" "$BUNDLE_ID" \
    --mode=effect --view="$SCENE_VIEW" --progress=0.38 >/dev/null
  sleep 1
  xcrun simctl io "$DEVICE_ID" screenshot \
    "$ARTIFACT_DIR/combo-halo-effect-$SCENE_VIEW-38.png" >/dev/null
done

xcrun simctl launch --terminate-running-process "$DEVICE_ID" "$BUNDLE_ID" \
  --mode=tool >/dev/null
sleep 2.5
xcrun simctl io "$DEVICE_ID" screenshot \
  "$ARTIFACT_DIR/combo-halo-curve-tool.png" >/dev/null

xcrun simctl launch --terminate-running-process "$DEVICE_ID" "$BUNDLE_ID" \
  --mode=motion >/dev/null
xcrun simctl io "$DEVICE_ID" recordVideo \
  --codec=h264 "$BUILD_ROOT/combo-halo-motion-raw.mp4" >/dev/null 2>&1 &
RECORD_PID=$!
sleep 5
kill -INT "$RECORD_PID"
wait "$RECORD_PID" || true
RECORD_PID=""

ffmpeg -y \
  -ss 0.35 \
  -i "$BUILD_ROOT/combo-halo-motion-raw.mp4" \
  -vf fps=60 \
  -c:v libx264 \
  -pix_fmt yuv420p \
  -movflags +faststart \
  "$ARTIFACT_DIR/combo-halo-motion.mp4" >/dev/null 2>&1

ffmpeg -y \
  -i "$ARTIFACT_DIR/combo-halo-motion.mp4" \
  -vf "fps=4,scale=302:-1,tile=5x4:padding=6:margin=6" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/combo-halo-motion-contact-sheet.png" >/dev/null 2>&1

# A tight timeline makes the 80 ms core flash, delayed echo and lingering mist
# readable in one QA artifact instead of sampling mostly idle loop frames.
ffmpeg -y \
  -ss 0.88 \
  -t 1.00 \
  -i "$ARTIFACT_DIR/combo-halo-motion.mp4" \
  -vf "fps=12,scale=302:-1,tile=6x2:padding=6:margin=6" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/combo-halo-burst-contact-sheet.png" >/dev/null 2>&1

ffmpeg -y \
  -i "$ARTIFACT_DIR/combo-halo-effect-top-38.png" \
  -i "$ARTIFACT_DIR/combo-halo-effect-hero-38.png" \
  -i "$ARTIFACT_DIR/combo-halo-effect-left-38.png" \
  -i "$ARTIFACT_DIR/combo-halo-effect-right-38.png" \
  -i "$ARTIFACT_DIR/combo-halo-effect-low-38.png" \
  -filter_complex \
  "[0:v]scale=300:-1[top];[1:v]scale=300:-1[hero];[2:v]scale=300:-1[left];[3:v]scale=300:-1[right];[4:v]scale=300:-1[low];[top][hero][left][right][low]xstack=inputs=5:layout=0_0|300_0|600_0|150_652|450_652:fill=black[out]" \
  -map "[out]" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/combo-halo-angle-contact-sheet.png" >/dev/null 2>&1

print "Captured native Combo halo previews in $ARTIFACT_DIR"
