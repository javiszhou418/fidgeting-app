#!/bin/zsh
set -euo pipefail
unsetopt BG_NICE

TOOL_DIR="${0:A:h}"
PROJECT_ROOT="${TOOL_DIR:h:h}"
SOURCE_ROOT="$PROJECT_ROOT/Assets/Plugins/iOS"
ARTIFACT_DIR="$PROJECT_ROOT/Artifacts/GachaRiveShippingPreview"
BUILD_ROOT="$(mktemp -d /tmp/fidget-gacha-rive-preview.XXXXXX)"
BUILD_SOURCES="$BUILD_ROOT/Sources"
MODULE_CACHE="$BUILD_ROOT/ModuleCache"
APP_DIR="$BUILD_ROOT/GachaRiveShippingPreview.app"
APP_BINARY="$APP_DIR/GachaShippingNativePreview"
BUNDLE_ID="com.jiaweizhou.fidgeting.gacha-shipping-preview"

RIVE_VERSION="6.23.1"
RIVE_RELEASE_URL="https://github.com/rive-app/rive-ios/releases/download/$RIVE_VERSION/RiveRuntime.xcframework.zip"
RIVE_RELEASE_SHA256="eaba09813f47bfede2d87b9a8ad436e9e6d155f4f38e3f267360962575fc10b9"
RIVE_ASSET_SHA256="da5ba78f63c09ea538d214f7bcdd520a852fc77232bf47ef31606106136c7717"
RIVE_CACHE_ROOT="${FIDGET_RIVE_PREVIEW_CACHE:-${TMPDIR%/}/fidget-rive-preview-cache/$RIVE_VERSION}"
RIVE_ZIP="$RIVE_CACHE_ROOT/RiveRuntime.xcframework.zip"
RIVE_UNPACK_ROOT="$RIVE_CACHE_ROOT/unpacked"
RIVE_XCFRAMEWORK="$RIVE_UNPACK_ROOT/RiveRuntime.xcframework"
RIVE_SIMULATOR_FRAMEWORK="$RIVE_XCFRAMEWORK/ios-arm64_x86_64-simulator/RiveRuntime.framework"
RIVE_ASSET="$SOURCE_ROOT/Rive/gacha-single-draw-jumbotron.riv"
ORIGINAL_RIVE_ASSET="/Users/jiawei.zhou/Downloads/jumbotron_split_-_mint_slab.riv"

CAPTURE_SECONDS="${GACHA_RIVE_PREVIEW_SECONDS:-26}"
BUILD_ONLY=false
if [[ "${1:-}" == "--build-only" ]]; then
  BUILD_ONLY=true
elif [[ -n "${1:-}" ]]; then
  print -u2 "Usage: ${0:t} [--build-only]"
  exit 64
fi

sha256_file() {
  shasum -a 256 "$1" | awk '{print $1}'
}

require_file_hash() {
  local file_path="$1"
  local expected_hash="$2"
  local description="$3"
  if [[ ! -f "$file_path" ]]; then
    print -u2 "$description is missing: $file_path"
    exit 66
  fi
  local actual_hash
  actual_hash="$(sha256_file "$file_path")"
  if [[ "$actual_hash" != "$expected_hash" ]]; then
    print -u2 "$description hash mismatch. Expected $expected_hash, got $actual_hash"
    exit 65
  fi
}

mkdir -p "$ARTIFACT_DIR" "$BUILD_SOURCES" "$MODULE_CACHE" "$APP_DIR" "$RIVE_CACHE_ROOT"

require_file_hash "$RIVE_ASSET" "$RIVE_ASSET_SHA256" "Canonical gacha Rive asset"
RIVE_USER_SOURCE_MATCH="unavailable"
if [[ -f "$ORIGINAL_RIVE_ASSET" ]]; then
  require_file_hash "$ORIGINAL_RIVE_ASSET" "$RIVE_ASSET_SHA256" "Original supplied Rive asset"
  cmp -s "$ORIGINAL_RIVE_ASSET" "$RIVE_ASSET" || {
    print -u2 "Canonical and original Rive assets are not byte-identical."
    exit 65
  }
  RIVE_USER_SOURCE_MATCH="true"
fi

if [[ ! -f "$RIVE_ZIP" ]]; then
  curl -L --fail --retry 2 --connect-timeout 20 \
    -o "$RIVE_ZIP" "$RIVE_RELEASE_URL"
fi
require_file_hash "$RIVE_ZIP" "$RIVE_RELEASE_SHA256" "Official RiveRuntime release archive"

if [[ ! -d "$RIVE_SIMULATOR_FRAMEWORK" ]]; then
  mkdir -p "$RIVE_UNPACK_ROOT"
  ditto -x -k "$RIVE_ZIP" "$RIVE_UNPACK_ROOT"
fi
if [[ ! -f "$RIVE_SIMULATOR_FRAMEWORK/RiveRuntime" ]]; then
  print -u2 "Official RiveRuntime simulator framework was not unpacked."
  exit 66
fi
RUNTIME_VERSION="$(plutil -extract CFBundleShortVersionString raw -o - "$RIVE_SIMULATOR_FRAMEWORK/Info.plist")"
if [[ "$RUNTIME_VERSION" != "$RIVE_VERSION" ]]; then
  print -u2 "RiveRuntime version mismatch. Expected $RIVE_VERSION, got $RUNTIME_VERSION"
  exit 65
fi

for source_name in \
  FidgetProductUIComponents.swift \
  FidgetGachaPackPresentation.swift \
  FidgetGachaRiveGateRules.swift \
  FidgetGachaRivePresentation.swift \
  FidgetGachaStore.swift \
  FidgetStoreKit.swift \
  FidgetGachaStorefront.swift; do
  cp "$SOURCE_ROOT/$source_name" "$BUILD_SOURCES/$source_name"
done
cp "$TOOL_DIR/GachaShippingNativePreviewApp.swift" \
  "$BUILD_SOURCES/GachaShippingNativePreviewApp.swift"

xcrun --sdk iphonesimulator swiftc \
  -D DEBUG \
  -warnings-as-errors \
  -parse-as-library \
  -target arm64-apple-ios15.0-simulator \
  -module-cache-path "$MODULE_CACHE" \
  -F "$RIVE_XCFRAMEWORK/ios-arm64_x86_64-simulator" \
  -framework RiveRuntime \
  -Xlinker -rpath \
  -Xlinker @executable_path/Frameworks \
  "$BUILD_SOURCES/FidgetProductUIComponents.swift" \
  "$BUILD_SOURCES/FidgetGachaPackPresentation.swift" \
  "$BUILD_SOURCES/FidgetGachaRiveGateRules.swift" \
  "$BUILD_SOURCES/FidgetGachaRivePresentation.swift" \
  "$BUILD_SOURCES/FidgetGachaStore.swift" \
  "$BUILD_SOURCES/FidgetStoreKit.swift" \
  "$BUILD_SOURCES/FidgetGachaStorefront.swift" \
  "$BUILD_SOURCES/GachaShippingNativePreviewApp.swift" \
  -o "$APP_BINARY"

if ! otool -L "$APP_BINARY" | grep -q '@rpath/RiveRuntime.framework/RiveRuntime'; then
  print -u2 "Preview binary did not link the real RiveRuntime framework."
  exit 65
fi

cp "$TOOL_DIR/Info.plist" "$APP_DIR/Info.plist"
cp "$SOURCE_ROOT/Fonts/Oxanium-VariableFont_wght.ttf" \
  "$APP_DIR/Oxanium-VariableFont_wght.ttf"
cp "$RIVE_ASSET" "$APP_DIR/gacha-single-draw-jumbotron.riv"

for artwork in "$SOURCE_ROOT"/GachaPacks/*.png; do
  cp "$artwork" "$APP_DIR/${artwork:t}"
done
for artwork in "$SOURCE_ROOT"/Thumbnails/**/*.png; do
  cp "$artwork" "$APP_DIR/${artwork:t}"
done

mkdir -p "$APP_DIR/Frameworks"
ditto "$RIVE_SIMULATOR_FRAMEWORK" "$APP_DIR/Frameworks/RiveRuntime.framework"
codesign --force --sign - "$APP_DIR/Frameworks/RiveRuntime.framework" >/dev/null
codesign --force --sign - "$APP_DIR" >/dev/null

require_file_hash \
  "$APP_DIR/gacha-single-draw-jumbotron.riv" \
  "$RIVE_ASSET_SHA256" \
  "Bundled gacha Rive asset"

SOURCE_SET_SHA256="$({
  for source_file in "$BUILD_SOURCES"/*.swift; do
    print "$(sha256_file "$source_file") ${source_file:t}"
  done
} | LC_ALL=C sort | shasum -a 256 | awk '{print $1}')"
APP_BINARY_SHA256="$(sha256_file "$APP_BINARY")"
RUNTIME_BINARY_SHA256="$(sha256_file "$APP_DIR/Frameworks/RiveRuntime.framework/RiveRuntime")"
LINKED_RUNTIME="$(otool -L "$APP_BINARY" | awk '/RiveRuntime.framework/ {print $1; exit}')"

{
  print "artifact_kind=shipping-source-rive-simulator-preview-build"
  print "built_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  print "build_root=$BUILD_ROOT"
  print "bundle_id=$BUNDLE_ID"
  print "source_root=$SOURCE_ROOT"
  print "source_set_sha256=$SOURCE_SET_SHA256"
  print "app_binary_sha256=$APP_BINARY_SHA256"
  print "rive_runtime_version=$RUNTIME_VERSION"
  print "rive_runtime_release_url=$RIVE_RELEASE_URL"
  print "rive_runtime_archive_sha256=$RIVE_RELEASE_SHA256"
  print "rive_runtime_binary_sha256=$RUNTIME_BINARY_SHA256"
  print "rive_asset_path=$RIVE_ASSET"
  print "rive_asset_sha256=$RIVE_ASSET_SHA256"
  print "rive_asset_byte_identical_to_user_source=$RIVE_USER_SOURCE_MATCH"
  print "rive_split_artboards=background/mint-slab,foreground/mint-slab"
  print "rive_bindable_artboards=Slab-rotate-v01,Coin_Slab_v09-sm"
  print "rive_animation_type=T2_SPORTS_CARD_JUMBOTRON"
  print "rive_cdn_loading=false"
  print "rive_embedded_image_loader=RiveImageAsset.renderImage(factory.decodeImage(data))"
  print "rive_completion_contract=both-layer-stateMachineCycle"
  print "linked_runtime=$LINKED_RUNTIME"
  print "shipping_source_files=FidgetProductUIComponents.swift,FidgetGachaPackPresentation.swift,FidgetGachaRiveGateRules.swift,FidgetGachaRivePresentation.swift,FidgetGachaStore.swift,FidgetStoreKit.swift,FidgetGachaStorefront.swift"
  print "visual_approval=待确认"
  print "phone_push=未推送手机"
} > "$ARTIFACT_DIR/preview-build-evidence.txt"

if $BUILD_ONLY; then
  print "Real-Rive shipping-source preview build passed."
  print "App: $APP_DIR"
  print "Evidence: $ARTIFACT_DIR/preview-build-evidence.txt"
  exit 0
fi

if ! grep -q -- '--preview-auto-single-draw' "$SOURCE_ROOT/FidgetGachaStorefront.swift"; then
  print -u2 "Shipping storefront does not yet contain the DEBUG auto-single-draw preview hook."
  exit 65
fi
if ! grep -q -- '--preview-auto-open-pack' "$SOURCE_ROOT/FidgetGachaStorefront.swift"; then
  print -u2 "Shipping storefront does not contain the DEBUG auto-open-Pack preview hook."
  exit 65
fi
if ! grep -q -- '--preview-auto-confirm-pack' "$SOURCE_ROOT/FidgetGachaStorefront.swift"; then
  print -u2 "Shipping storefront does not contain the DEBUG auto-confirm-Pack preview hook."
  exit 65
fi

DEVICE_ID="${GACHA_RIVE_PREVIEW_DEVICE_ID:-}"
if [[ -z "$DEVICE_ID" ]]; then
  DEVICE_ID="$(
    xcrun simctl list devices available \
      | sed -nE 's/^[[:space:]]*iPhone[^\(]*\(([0-9A-F-]{36})\).*/\1/p' \
      | head -1
  )"
fi
if [[ -z "$DEVICE_ID" ]]; then
  print -u2 "No available iPhone Simulator was found."
  exit 68
fi

DEVICE_NAME="$(xcrun simctl list devices | awk -v id="$DEVICE_ID" '$0 ~ id {sub(/^[[:space:]]*/, ""); sub(/ \(.*/, ""); print; exit}')"
xcrun simctl boot "$DEVICE_ID" 2>/dev/null || true
xcrun simctl bootstatus "$DEVICE_ID" -b
xcrun simctl uninstall "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true
xcrun simctl install "$DEVICE_ID" "$APP_DIR"

VIDEO_PATH="$ARTIFACT_DIR/gacha-rive-shipping-flow.mp4"
APP_LOG_PATH="$ARTIFACT_DIR/gacha-rive-shipping-flow.log"

xcrun simctl io "$DEVICE_ID" recordVideo \
  --codec=h264 --force "$VIDEO_PATH" >/dev/null 2>&1 &
RECORD_PID=$!
# Keep only a short recorder warm-up so the first evidence keyframe lands on
# the redesigned storefront before its 0.8 s production auto-draw hook.
sleep 0.15

SIMCTL_CHILD_NSUnbufferedIO=YES xcrun simctl launch \
  --console \
  "$DEVICE_ID" \
  "$BUNDLE_ID" \
  --preview-auto-single-draw \
  --preview-carousel-tier=signature \
  --preview-auto-confirm-pack \
  --preview-authoritative-receipt \
  --preview-auto-open-pack \
  > "$APP_LOG_PATH" 2>&1 &
APP_LOG_PID=$!

sleep "$CAPTURE_SECONDS"
kill -INT "$RECORD_PID" 2>/dev/null || true
wait "$RECORD_PID" || true
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" 2>/dev/null || true
wait "$APP_LOG_PID" || true

if [[ ! -s "$VIDEO_PATH" ]]; then
  print -u2 "Simulator recording did not produce a video."
  exit 74
fi
if grep -Fq '[GachaRiveGate] completed via watchdog' "$APP_LOG_PATH"; then
  print -u2 "Rive watchdog completion was observed; fallback recordings are rejected."
  exit 65
fi
for required_runtime_event in \
  '[GachaRiveRuntime] first-frame artboard=background/mint-slab' \
  '[GachaRiveRuntime] first-frame artboard=foreground/mint-slab' \
  '[GachaRiveRuntime] layer-completed artboard=background/mint-slab source=stateMachineCycle' \
  '[GachaRiveRuntime] layer-completed artboard=foreground/mint-slab source=stateMachineCycle' \
  '[GachaSequence] selection-rive-completed reason=animationSignal' \
  '[GachaSequence] holder-rive-completed reason=animationSignal' \
  '[GachaPreview] authoritative-receipt request='; do
  if ! grep -Fq "$required_runtime_event" "$APP_LOG_PATH"; then
    print -u2 "Required real-Rive runtime event was not observed: $required_runtime_event"
    exit 65
  fi
done
if [[ "$(grep -Fc '[GachaRiveRuntime] purchase-trigger synchronizedLayers=2' "$APP_LOG_PATH")" -ne 2 ]]; then
  print -u2 "Expected exactly two synchronized two-layer Rive triggers."
  exit 65
fi
if ! grep -Fq '[GachaPreview] premium-handoff prize=' "$APP_LOG_PATH"; then
  print -u2 "Pack did not reach the real PremiumDisplayCase continuation boundary."
  exit 65
fi

VIDEO_DURATION="$(ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "$VIDEO_PATH")"
TAILPOINT="$(awk -v duration="$VIDEO_DURATION" 'BEGIN { point = duration - 1; if (point < 0) point = 0; printf "%.3f", point }')"

# The app's first cold-launch frames are the white UIKit launch surface; 1.3 s
# reliably captures the redesigned storefront before the Rive gate overlays it.
ffmpeg -y -ss 1.300 -i "$VIDEO_PATH" -frames:v 1 \
  "$ARTIFACT_DIR/01-keyframe-first.png" >/dev/null 2>&1
# The Rive state-machine cycle is visibly active around 4.5 s. Do not use the
# container midpoint: Simulator VFR duration includes a variable static tail.
ffmpeg -y -ss 4.500 -i "$VIDEO_PATH" -frames:v 1 \
  "$ARTIFACT_DIR/02-keyframe-middle.png" >/dev/null 2>&1
cp "$ARTIFACT_DIR/02-keyframe-middle.png" \
  "$ARTIFACT_DIR/02-keyframe-rive-visible.png"
ffmpeg -y -ss "$TAILPOINT" -i "$VIDEO_PATH" -frames:v 1 \
  "$ARTIFACT_DIR/03-keyframe-tail.png" >/dev/null 2>&1
# Simulator screen recording is variable-frame-rate and may omit a long static
# tail. Sample meaningful flow milestones so the sheet reproducibly covers the
# storefront, active Rive cycle, sealed/opening Pack, and Unity handoff.
CONTACT_FRAME_DIR="$BUILD_ROOT/ContactFrames"
mkdir -p "$CONTACT_FRAME_DIR"
CONTACT_POINTS=(1.300 1.800 2.500 3.500 4.500 5.700 6.500 7.400 8.200 9.200 11.000 12.800)
CONTACT_INPUTS=()
CONTACT_INDEX=1
for POINT in "${CONTACT_POINTS[@]}"; do
  FRAME_PATH="$(printf '%s/frame-%02d.png' "$CONTACT_FRAME_DIR" "$CONTACT_INDEX")"
  ffmpeg -y -ss "$POINT" -i "$VIDEO_PATH" -frames:v 1 \
    "$FRAME_PATH" >/dev/null 2>&1
  CONTACT_INPUTS+=(-i "$FRAME_PATH")
  (( CONTACT_INDEX += 1 ))
done
ffmpeg -y "${CONTACT_INPUTS[@]}" \
  -filter_complex \
  '[0:v]scale=240:-1[a0];[1:v]scale=240:-1[a1];[2:v]scale=240:-1[a2];[3:v]scale=240:-1[a3];[4:v]scale=240:-1[a4];[5:v]scale=240:-1[a5];[6:v]scale=240:-1[a6];[7:v]scale=240:-1[a7];[8:v]scale=240:-1[a8];[9:v]scale=240:-1[a9];[10:v]scale=240:-1[a10];[11:v]scale=240:-1[a11];[a0][a1][a2][a3]hstack=inputs=4[r0];[a4][a5][a6][a7]hstack=inputs=4[r1];[a8][a9][a10][a11]hstack=inputs=4[r2];[r0][r1][r2]vstack=inputs=3[out]' \
  -map '[out]' -frames:v 1 \
  "$ARTIFACT_DIR/gacha-rive-shipping-flow-contact-sheet.png" >/dev/null 2>&1

VIDEO_SHA256="$(sha256_file "$VIDEO_PATH")"
VIDEO_STREAM="$(ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,avg_frame_rate,pix_fmt \
  -of default=noprint_wrappers=1 "$VIDEO_PATH" | tr '\n' ' ')"

{
  print "artifact_kind=shipping-source-rive-simulator-preview-video"
  print "captured_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  print "device_name=$DEVICE_NAME"
  print "device_udid=$DEVICE_ID"
  print "capture_seconds_requested=$CAPTURE_SECONDS"
  print "video_duration_seconds=$VIDEO_DURATION"
  print "video_stream=$VIDEO_STREAM"
  print "video_sha256=$VIDEO_SHA256"
  print "source_set_sha256=$SOURCE_SET_SHA256"
  print "app_binary_sha256=$APP_BINARY_SHA256"
  print "rive_runtime_version=$RUNTIME_VERSION"
  print "rive_runtime_archive_sha256=$RIVE_RELEASE_SHA256"
  print "rive_runtime_binary_sha256=$RUNTIME_BINARY_SHA256"
  print "rive_asset_sha256=$RIVE_ASSET_SHA256"
  print "rive_split_artboards=background/mint-slab,foreground/mint-slab"
  print "rive_bindable_artboards=Slab-rotate-v01,Coin_Slab_v09-sm"
  print "rive_animation_type=T2_SPORTS_CARD_JUMBOTRON"
  print "rive_cdn_loading=false"
  print "rive_completion_signal=animationSignal"
  print "rive_completion_source=both-layer-stateMachineCycle"
  print "rive_watchdog_observed=false"
  print "rive_visible_keyframe=02-keyframe-rive-visible.png"
  print "launch_arguments=--preview-auto-single-draw --preview-carousel-tier=signature --preview-auto-confirm-pack --preview-authoritative-receipt --preview-auto-open-pack"
  print "preview_host=Tools/GachaShippingNativePreview/GachaShippingNativePreviewApp.swift"
  print "visual_approval=待确认"
  print "phone_push=未推送手机"
} > "$ARTIFACT_DIR/preview-video-evidence.txt"

print "Captured real-Rive shipping-source Simulator preview."
print "Video: $VIDEO_PATH"
print "Contact sheet: $ARTIFACT_DIR/gacha-rive-shipping-flow-contact-sheet.png"
print "Evidence: $ARTIFACT_DIR/preview-video-evidence.txt"
