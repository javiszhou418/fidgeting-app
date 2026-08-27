#!/bin/zsh
set -euo pipefail
unsetopt BG_NICE

TOOL_DIR="${0:A:h}"
PROJECT_ROOT="${TOOL_DIR:h:h}"
SOURCE_ROOT="$PROJECT_ROOT/Assets/Plugins/iOS"
HARNESS_SOURCE="$TOOL_DIR/ContinuousMainAppHarness"
ARTIFACT_DIR="$PROJECT_ROOT/Artifacts/GachaPackRiveUnityContinuousPreview"
BUNDLE_ID="com.jiaweizhou.fidgetspinner.codex"
EXPECTED_VIEWPORT="393x852"
EXPECTED_MODEL_ID="metal-three-blade"
EXPECTED_PRIZE_ID="canyon-heir-metal-three-blade"
EXPECTED_PRIZE_KIND="Toy"
EXPECTED_CONTENT_REFERENCE="toy/metal-three-blade"
EXPECTED_RIVE_VERSION="6.23.1"
EXPECTED_RIVE_ASSET_SHA256="da5ba78f63c09ea538d214f7bcdd520a852fc77232bf47ef31606106136c7717"
EXPECTED_PACK_CASE_TRANSITION_SECONDS="0.28"

MODE="prepare"
XCODE_EXPORT="$PROJECT_ROOT/Builds/iOS/FidgetingAppSimulatorDevelopment"
DEVICE_ID=""
PREBUILT_APP=""

usage() {
  print "Usage: ${0:t} --prepare-only [--xcode-export PATH]"
  print "       ${0:t} --capture --udid SIMULATOR_UDID [--xcode-export PATH]"
  print "                 [--prebuilt-app SAME_FROZEN_EXPORT_APP]"
}

while (( $# > 0 )); do
  case "$1" in
    --prepare-only)
      MODE="prepare"
      shift
      ;;
    --capture)
      MODE="capture"
      shift
      ;;
    --xcode-export)
      XCODE_EXPORT="$2"
      shift 2
      ;;
    --udid)
      DEVICE_ID="$2"
      shift 2
      ;;
    --prebuilt-app)
      PREBUILT_APP="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      print -u2 "Unknown argument: $1"
      usage >&2
      exit 64
      ;;
  esac
done

XCODE_EXPORT="${XCODE_EXPORT:A}"

sha256_file() {
  shasum -a 256 "$1" | awk '{print $1}'
}

require_file() {
  if [[ ! -f "$1" ]]; then
    print -u2 "Missing required file: $1"
    exit 66
  fi
}

require_source_marker() {
  local marker="$1"
  local source_file="$2"
  if ! grep -Fq -- "$marker" "$source_file"; then
    print -u2 "Shipping runtime is not ready; missing marker '$marker' in $source_file"
    exit 65
  fi
}

require_once() {
  local marker="$1"
  local log_path="$2"
  local count
  count="$(grep -Fc -- "$marker" "$log_path" || true)"
  if [[ "$count" -ne 1 ]]; then
    print -u2 "Expected exactly one '$marker' event; observed $count."
    exit 65
  fi
}

SHIPPING_SWIFT_FILES=(
  CodexSwiftUIOverlay.swift
  FidgetProductUIComponents.swift
  FidgetGachaPackPresentation.swift
  FidgetGachaRiveGateRules.swift
  FidgetGachaRivePresentation.swift
  FidgetGachaStore.swift
  FidgetGachaStorefront.swift
  FidgetStoreKit.swift
)

UNITY_REVEAL_FILES=(
  Assets/Scripts/Product/FidgetAppCoordinator.cs
  Assets/Scripts/Product/Gacha/GachaCatalog.cs
  Assets/Scripts/Product/Gacha/GachaInventory.cs
  Assets/Scripts/Product/Gacha/GachaPresentationNativeBridge.cs
  Assets/Scripts/Product/Gacha/GachaRevealDirector.cs
  Assets/Scripts/Product/Gacha/GachaRevealRules.cs
  Assets/_DisplayCase/Runtime/PremiumDisplayCase.cs
  Assets/_DisplayCase/Runtime/PremiumDisplayCaseContract.cs
)

for source_name in "${SHIPPING_SWIFT_FILES[@]}"; do
  require_file "$SOURCE_ROOT/$source_name"
done
for relative_path in "${UNITY_REVEAL_FILES[@]}"; do
  require_file "$PROJECT_ROOT/$relative_path"
done
require_file "$SOURCE_ROOT/Rive/gacha-single-draw-jumbotron.riv"
require_file "$HARNESS_SOURCE/project.yml"
require_file \
  "$HARNESS_SOURCE/GachaContinuousPreviewUITests/GachaContinuousPreviewUITests.swift"

if [[ "$(sha256_file "$SOURCE_ROOT/Rive/gacha-single-draw-jumbotron.riv")" \
      != "$EXPECTED_RIVE_ASSET_SHA256" ]]; then
  print -u2 "Canonical Rive asset hash changed; update the reviewed evidence contract first."
  exit 65
fi

# These are source-contract gates, not conceptual preview affordances. Capture
# stays disabled until the shipping runtime agent has landed the full sequence.
require_source_marker 'gacha-pack-carousel' "$SOURCE_ROOT/FidgetGachaStorefront.swift"
require_source_marker 'gacha-selection-rive' "$SOURCE_ROOT/FidgetGachaRivePresentation.swift"
require_source_marker 'carousel-visible-hold=2.0' \
  "$HARNESS_SOURCE/GachaContinuousPreviewUITests/GachaContinuousPreviewUITests.swift"
require_source_marker '[GachaSequence] carousel-open' "$SOURCE_ROOT/FidgetGachaStorefront.swift"
require_source_marker 'presentationOnly=true' "$SOURCE_ROOT/FidgetGachaStorefront.swift"
require_source_marker 'selection-rive-completed reason=' "$SOURCE_ROOT/FidgetGachaStorefront.swift"
require_source_marker 'gacha-pack-case-transition' "$SOURCE_ROOT/FidgetGachaStorefront.swift"
require_source_marker 'pack-case-overlap-start request=' "$SOURCE_ROOT/FidgetGachaStorefront.swift"
require_source_marker 'pack-case-overlap-complete request=' "$SOURCE_ROOT/FidgetGachaStorefront.swift"
require_source_marker 'revealSetupSucceeded' "$SOURCE_ROOT/FidgetGachaStorefront.swift"
require_source_marker \
  "packToCaseTransitionSeconds: Double = $EXPECTED_PACK_CASE_TRANSITION_SECONDS" \
  "$SOURCE_ROOT/FidgetGachaRiveGateRules.swift"
require_source_marker 'mutating func markUnityCaseReady(' \
  "$SOURCE_ROOT/FidgetGachaRiveGateRules.swift"
require_source_marker 'ConfirmGachaRevealReadyAfterTwoFrames' \
  "$PROJECT_ROOT/Assets/Scripts/Product/FidgetAppCoordinator.cs"
require_source_marker 'title: "收下"' "$SOURCE_ROOT/CodexSwiftUIOverlay.swift"
require_source_marker 'animationSignal' "$SOURCE_ROOT/FidgetGachaRivePresentation.swift"
require_source_marker 'unity-case-prepare-requested' "$SOURCE_ROOT/FidgetGachaStorefront.swift"
require_source_marker 'canyon-heir-metal-three-blade' "$PROJECT_ROOT/Assets/Scripts/Product/Gacha/GachaCatalog.cs"
require_source_marker 'GachaPrizeKind.Toy' "$PROJECT_ROOT/Assets/Scripts/Product/Gacha/GachaCatalog.cs"
require_source_marker 'toy/metal-three-blade' "$PROJECT_ROOT/Assets/Scripts/Product/Gacha/GachaCatalog.cs"
require_source_marker 'DrawOnceForDevelopmentPreview' "$PROJECT_ROOT/Assets/Scripts/Product/Gacha/GachaInventory.cs"
require_source_marker '--preview-gacha-funding-token=metal-three-blade-v1' "$SOURCE_ROOT/FidgetGachaStore.swift"
require_source_marker 'metal-three-blade-v1' "$PROJECT_ROOT/Assets/Scripts/Product/Gacha/GachaInventory.cs"
require_source_marker '[GachaSequence] preview-funding credited=1' "$PROJECT_ROOT/Assets/Scripts/Product/FidgetAppCoordinator.cs"
require_source_marker 'preview-metal-three-blade' "$PROJECT_ROOT/Assets/Scripts/Product/FidgetAppCoordinator.cs"
require_source_marker '[GachaUnityReveal] started' "$PROJECT_ROOT/Assets/Scripts/Product/FidgetAppCoordinator.cs"
if grep -Fq 'Environment.GetCommandLineArgs' \
    "$PROJECT_ROOT/Assets/Scripts/Product/FidgetAppCoordinator.cs"; then
  print -u2 "Unity iOS preview funding must arrive through the explicit native bridge, not managed argv."
  exit 65
fi
require_source_marker 'DurationSeconds = 2.20f' "$PROJECT_ROOT/Assets/_DisplayCase/Runtime/PremiumDisplayCaseContract.cs"
require_source_marker 'public static void BuildIosSimulatorDevelopmentPreview()' \
  "$PROJECT_ROOT/Assets/Editor/IosBuildPipeline.cs"
require_source_marker 'RelativeSimulatorDevelopmentBuildPath' \
  "$PROJECT_ROOT/Assets/Editor/IosBuildPipeline.cs"
require_source_marker 'SWIFT_ACTIVE_COMPILATION_CONDITIONS' \
  "$PROJECT_ROOT/Assets/Editor/IosBuildPipeline.cs"
for beat in lidLift lidOpen caseRise acrylicVisibility contentVisibility sweep; do
  require_source_marker "float $beat =" \
    "$PROJECT_ROOT/Assets/_DisplayCase/Runtime/PremiumDisplayCaseContract.cs"
done

if grep -Fq 'Color.yellow' "$SOURCE_ROOT/FidgetGachaRivePresentation.swift"; then
  print -u2 "The holder presentation still contains the rejected yellow accent."
  exit 65
fi

if rg -n 'CodexGachaReceiveState|UnitySendMessage|GachaCaseRevealVisual|receipt[[:space:]]*=' \
    "$HARNESS_SOURCE/GachaContinuousPreviewUITests/GachaContinuousPreviewUITests.swift" \
    >/dev/null; then
  print -u2 "The UI evidence harness contains a fake receipt, bridge, or Swift reveal token."
  exit 65
fi

HARNESS_BUILD_ROOT="$(mktemp -d /tmp/fidget-gacha-continuous-harness.XXXXXX)"
ditto "$HARNESS_SOURCE" "$HARNESS_BUILD_ROOT/Harness"
(
  cd "$HARNESS_BUILD_ROOT/Harness"
  xcodegen generate >/dev/null
)
HARNESS_PROJECT="$HARNESS_BUILD_ROOT/Harness/GachaContinuousPreviewHarness.xcodeproj"

if [[ "$MODE" == "prepare" ]]; then
  xcodebuild build-for-testing \
    -project "$HARNESS_PROJECT" \
    -scheme GachaContinuousPreviewUITests \
    -configuration Debug \
    -destination 'generic/platform=iOS Simulator' \
    -derivedDataPath "$HARNESS_BUILD_ROOT/HarnessDerivedData" \
    CODE_SIGNING_ALLOWED=NO \
    >/dev/null
  print "Continuous main-app evidence harness compiled."
  print "Shipping runtime markers, neutral Rive boundaries, and 2.20 s source contract passed."
  print "No main app was built, installed, launched, or recorded."
  exit 0
fi

if [[ -z "$DEVICE_ID" ]]; then
  print -u2 "--capture requires --udid for a dedicated 393x852 Simulator."
  exit 64
fi
if [[ ! -d "$XCODE_EXPORT/Unity-iPhone.xcodeproj" ]]; then
  print -u2 "Fresh Unity Simulator export is missing: $XCODE_EXPORT"
  exit 66
fi
require_file "$XCODE_EXPORT/FidgetingBuildManifest.json"
if [[ "$(plutil -extract sdk raw -o - \
      "$XCODE_EXPORT/FidgetingBuildManifest.json")" != "SimulatorSDK" ]]; then
  print -u2 "Continuous preview requires a SimulatorSDK Unity export."
  exit 65
fi
if ! grep -Fq 'SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG;' \
    "$XCODE_EXPORT/Unity-iPhone.xcodeproj/project.pbxproj"; then
  print -u2 "Development Simulator export is missing the Swift DEBUG condition required by preview-only hooks."
  exit 65
fi
if [[ "$(plutil -extract development raw -o - \
      "$XCODE_EXPORT/FidgetingBuildManifest.json")" != "true" ]]; then
  print -u2 "Continuous preview requires a development=true Simulator export so DEBUG-only preview gates remain unavailable to Release."
  exit 65
fi

GENERATED_SWIFT_ROOT="$XCODE_EXPORT/Libraries/Plugins/iOS"
for source_name in "${SHIPPING_SWIFT_FILES[@]}"; do
  require_file "$GENERATED_SWIFT_ROOT/$source_name"
  if ! cmp -s "$SOURCE_ROOT/$source_name" "$GENERATED_SWIFT_ROOT/$source_name"; then
    print -u2 "Unity export contains stale shipping Swift: $source_name"
    exit 65
  fi
done

SOURCE_SET_SHA256="$({
  for source_name in "${SHIPPING_SWIFT_FILES[@]}"; do
    print "$(sha256_file "$SOURCE_ROOT/$source_name") $source_name"
  done
} | LC_ALL=C sort | shasum -a 256 | awk '{print $1}')"
GENERATED_SOURCE_SET_SHA256="$({
  for source_name in "${SHIPPING_SWIFT_FILES[@]}"; do
    print "$(sha256_file "$GENERATED_SWIFT_ROOT/$source_name") $source_name"
  done
} | LC_ALL=C sort | shasum -a 256 | awk '{print $1}')"
if [[ "$SOURCE_SET_SHA256" != "$GENERATED_SOURCE_SET_SHA256" ]]; then
  print -u2 "Workspace/export source-set mismatch."
  exit 65
fi

UNITY_REVEAL_SOURCE_SET_SHA256="$({
  for relative_path in "${UNITY_REVEAL_FILES[@]}"; do
    print "$(sha256_file "$PROJECT_ROOT/$relative_path") ${relative_path:t}"
  done
} | LC_ALL=C sort | shasum -a 256 | awk '{print $1}')"

MAIN_APP_BUILD_MODE="fresh-xcodebuild-from-frozen-export"
if [[ -n "$PREBUILT_APP" ]]; then
  APP_PATH="${PREBUILT_APP:A}"
  MAIN_APP_BUILD_MODE="same-frozen-export-app-reused-for-harness-only-retry"
else
  MAIN_DERIVED_DATA="$HARNESS_BUILD_ROOT/MainAppDerivedData"
  MAIN_BUILD_LOG="$HARNESS_BUILD_ROOT/main-app-xcodebuild.log"
  xcodebuild build \
    -project "$XCODE_EXPORT/Unity-iPhone.xcodeproj" \
    -scheme Unity-iPhone \
    -configuration Debug \
    -sdk iphonesimulator \
    -destination "id=$DEVICE_ID" \
    -derivedDataPath "$MAIN_DERIVED_DATA" \
    CODE_SIGNING_ALLOWED=NO \
    2>&1 | tee "$MAIN_BUILD_LOG"

  APP_PATH="$(find "$MAIN_DERIVED_DATA/Build/Products" -maxdepth 3 \
    -type d -name '*.app' ! -name '*Tests.app' | head -1)"
fi
if [[ -z "$APP_PATH" || ! -d "$APP_PATH" ]]; then
  print -u2 "Xcode did not produce the main Simulator app."
  exit 74
fi
require_file "$APP_PATH/Info.plist"
EXECUTABLE="$(plutil -extract CFBundleExecutable raw -o - "$APP_PATH/Info.plist")"
APP_BINARY="$APP_PATH/$EXECUTABLE"
require_file "$APP_BINARY"
if [[ "$(plutil -extract CFBundleIdentifier raw -o - "$APP_PATH/Info.plist")" \
      != "$BUNDLE_ID" ]]; then
  print -u2 "Built app has the wrong bundle identifier."
  exit 65
fi
if [[ " $(xcrun lipo -archs "$APP_BINARY") " != *' arm64 '* ]]; then
  print -u2 "Built Simulator app does not contain arm64."
  exit 65
fi

RUNTIME_BINARY="$APP_PATH/Frameworks/RiveRuntime.framework/RiveRuntime"
BUNDLED_RIVE_ASSET="$APP_PATH/gacha-single-draw-jumbotron.riv"
require_file "$RUNTIME_BINARY"
require_file "$BUNDLED_RIVE_ASSET"
if [[ "$(sha256_file "$BUNDLED_RIVE_ASSET")" != "$EXPECTED_RIVE_ASSET_SHA256" ]]; then
  print -u2 "Built app Rive asset does not match the canonical file."
  exit 65
fi
if ! otool -L "$APP_BINARY" | grep -Fq '@rpath/RiveRuntime.framework/RiveRuntime'; then
  print -u2 "Main app is not linked to official RiveRuntime."
  exit 65
fi
RUNTIME_VERSION="$(plutil -extract CFBundleShortVersionString raw -o - \
  "$APP_PATH/Frameworks/RiveRuntime.framework/Info.plist")"
if [[ "$RUNTIME_VERSION" != "$EXPECTED_RIVE_VERSION" ]]; then
  print -u2 "Unexpected RiveRuntime version: $RUNTIME_VERSION"
  exit 65
fi

mkdir -p "$ARTIFACT_DIR"
VIDEO_PATH="$ARTIFACT_DIR/gacha-pack-rive-unity-continuous-flow.mp4"
APP_LOG_PATH="$ARTIFACT_DIR/gacha-pack-rive-unity-continuous-flow.log"
XCODE_TEST_LOG="$ARTIFACT_DIR/gacha-pack-rive-unity-continuous-xcuitest.log"
COMBINED_LOG_PATH="$ARTIFACT_DIR/gacha-pack-rive-unity-continuous-combined.log"
RESULT_BUNDLE="$HARNESS_BUILD_ROOT/GachaContinuousPreview.xcresult"

xcrun simctl boot "$DEVICE_ID" >/dev/null 2>&1 || true
xcrun simctl bootstatus "$DEVICE_ID" -b
xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" >/dev/null 2>&1 || true
xcrun simctl uninstall "$DEVICE_ID" "$BUNDLE_ID" >/dev/null 2>&1 || true
xcrun simctl install "$DEVICE_ID" "$APP_PATH"

LOG_PID=""
RECORD_PID=""
stop_background_jobs() {
  if [[ -n "$RECORD_PID" ]]; then
    kill -INT "$RECORD_PID" >/dev/null 2>&1 || true
    wait "$RECORD_PID" >/dev/null 2>&1 || true
    RECORD_PID=""
  fi
  if [[ -n "$LOG_PID" ]]; then
    kill -INT "$LOG_PID" >/dev/null 2>&1 || true
    wait "$LOG_PID" >/dev/null 2>&1 || true
    LOG_PID=""
  fi
}
trap stop_background_jobs EXIT INT TERM

xcrun simctl spawn "$DEVICE_ID" log stream \
  --style compact --level debug \
  --predicate "process == '$EXECUTABLE' AND eventMessage CONTAINS[c] 'Gacha'" \
  >"$APP_LOG_PATH" 2>&1 &
LOG_PID=$!
RECORDING_START_EPOCH="$(date +%s)"
xcrun simctl io "$DEVICE_ID" recordVideo \
  --codec=h264 --force "$VIDEO_PATH" >/dev/null 2>&1 &
RECORD_PID=$!
sleep 0.25

set +e
xcodebuild test \
  -project "$HARNESS_PROJECT" \
  -scheme GachaContinuousPreviewUITests \
  -configuration Debug \
  -destination "id=$DEVICE_ID" \
  -derivedDataPath "$HARNESS_BUILD_ROOT/HarnessDerivedData" \
  -resultBundlePath "$RESULT_BUNDLE" \
  -only-testing:GachaContinuousPreviewUITests/GachaContinuousPreviewUITests/testRecordShippingCarouselRivePackAndRealUnityReveal \
  CODE_SIGNING_ALLOWED=NO \
  2>&1 | tee "$XCODE_TEST_LOG"
TEST_STATUS=$pipestatus[1]
set -e

xcrun simctl terminate "$DEVICE_ID" "$BUNDLE_ID" >/dev/null 2>&1 || true
stop_background_jobs
trap - EXIT INT TERM

{
  print -r -- "--- main app unified log ---"
  sed -n '1,$p' "$APP_LOG_PATH"
  print -r -- "--- XCUITest log ---"
  sed -n '1,$p' "$XCODE_TEST_LOG"
} > "$COMBINED_LOG_PATH"

if [[ "$TEST_STATUS" -ne 0 ]]; then
  print -u2 "Continuous shipping XCUITest failed."
  exit "$TEST_STATUS"
fi
if [[ ! -s "$VIDEO_PATH" ]]; then
  print -u2 "Continuous Simulator recording is empty."
  exit 74
fi

for required_event in \
  '[GachaSequence] carousel-open' \
  '[GachaSequence] pack-selected tier=signature presentationOnly=true' \
  '[GachaSequence] selection-rive-completed reason=animationSignal' \
  '[GachaSequence] unity-case-prepare-requested' \
  '[GachaSequence] unity-case-ready' \
  '[GachaSequence] pack-case-overlap-start' \
  '[GachaSequence] pack-case-overlap-complete' \
  '[GachaSequence] preview-authoritative-prize' \
  '[GachaSequence] preview-funding credited=1 token=metal-three-blade-v1 tickets=1' \
  'prize=canyon-heir-metal-three-blade kind=Toy contentReference=toy/metal-three-blade' \
  '[GachaUnityReveal] started' \
  'contentModel=metal-three-blade real3dRoot=true' \
  '[GachaUnityReveal] completed' \
  'awaitingUserAcceptance=true' \
  '[ContinuousHarness] viewport=393.0x852.0' \
  '[ContinuousHarness] real3dRoot=true model=metal-three-blade prize=canyon-heir-metal-three-blade kind=Toy contentReference=toy/metal-three-blade' \
  '[ContinuousHarness] unity-reveal assembled=true accept-ready=true'; do
  if ! grep -Fq -- "$required_event" "$COMBINED_LOG_PATH"; then
    print -u2 "Required continuous-flow evidence is missing: $required_event"
    exit 65
  fi
done

require_once '[GachaSequence] carousel-open request=' "$APP_LOG_PATH"
require_once '[GachaSequence] draw-requested request=' "$APP_LOG_PATH"
require_once '[GachaSequence] receipt-matched request=' "$APP_LOG_PATH"
require_once '[GachaSequence] tear-rebound' "$APP_LOG_PATH"
require_once '[GachaSequence] tear-commit' "$APP_LOG_PATH"
require_once '[GachaSequence] unity-case-prepare-requested request=' "$APP_LOG_PATH"
require_once '[GachaSequence] unity-case-ready request=' "$APP_LOG_PATH"
require_once '[GachaSequence] pack-case-overlap-start request=' "$APP_LOG_PATH"
require_once '[GachaSequence] pack-case-overlap-complete request=' "$APP_LOG_PATH"
require_once '[GachaSequence] preview-authoritative-prize request=' "$APP_LOG_PATH"
require_once '[GachaSequence] preview-funding credited=1 token=metal-three-blade-v1 tickets=1' "$APP_LOG_PATH"
require_once '[GachaUnityReveal] started request=' "$APP_LOG_PATH"
require_once '[GachaUnityReveal] completed request=' "$APP_LOG_PATH"

CORRELATED_REQUEST_IDS="$(grep -E \
  '\[(GachaSequence|GachaUnityReveal)\].*request=' "$APP_LOG_PATH" \
  | sed -E 's/.*request=([^ ]+).*/\1/' | LC_ALL=C sort -u)"
if [[ "$(print -r -- "$CORRELATED_REQUEST_IDS" | sed '/^$/d' | wc -l \
      | tr -d ' ')" -ne 1 ]]; then
  print -u2 "Continuous flow did not preserve one correlated request ID:"
  print -u2 -r -- "$CORRELATED_REQUEST_IDS"
  exit 65
fi

PREPARE_LINE="$(grep -nF \
  '[GachaSequence] unity-case-prepare-requested request=' \
  "$APP_LOG_PATH" | head -1 | cut -d: -f1)"
READY_LINE="$(grep -nF \
  '[GachaSequence] unity-case-ready request=' \
  "$APP_LOG_PATH" | head -1 | cut -d: -f1)"
OVERLAP_START_LINE="$(grep -nF \
  '[GachaSequence] pack-case-overlap-start request=' \
  "$APP_LOG_PATH" | head -1 | cut -d: -f1)"
OVERLAP_COMPLETE_LINE="$(grep -nF \
  '[GachaSequence] pack-case-overlap-complete request=' \
  "$APP_LOG_PATH" | head -1 | cut -d: -f1)"
if ! (( PREPARE_LINE < READY_LINE \
        && READY_LINE < OVERLAP_START_LINE \
        && OVERLAP_START_LINE < OVERLAP_COMPLETE_LINE )); then
  print -u2 "Pack-to-case events are not in the reviewed continuous order."
  print -u2 \
    "Observed lines: prepare=$PREPARE_LINE ready=$READY_LINE start=$OVERLAP_START_LINE complete=$OVERLAP_COMPLETE_LINE"
  exit 65
fi

if grep -Fiq 'watchdog' "$COMBINED_LOG_PATH"; then
  print -u2 "A Rive watchdog path was observed; capture rejected."
  exit 65
fi
if rg -i '(\[GachaRive|\[GachaSequence\].*selection-rive).*rarity' \
    "$COMBINED_LOG_PATH" >/dev/null; then
  print -u2 "Rarity data entered a Rive path; neutral-motion contract failed."
  exit 65
fi

VIDEO_DURATION="$(ffprobe -v error -show_entries format=duration \
  -of default=noprint_wrappers=1:nokey=1 "$VIDEO_PATH")"
VIDEO_STREAM="$(ffprobe -v error -select_streams v:0 \
  -show_entries stream=codec_name,width,height,avg_frame_rate,pix_fmt \
  -of default=noprint_wrappers=1 "$VIDEO_PATH" | tr '\n' ' ')"

for spec in \
  '01-storefront:0.08' \
  '02-carousel:0.24' \
  '03-selection-rive:0.38' \
  '04-pack-rebound:0.52' \
  '05-pack-case-overlap:0.68' \
  '06-real-unity:0.88'; do
  name="${spec%%:*}"
  fraction="${spec##*:}"
  point="$(awk -v duration="$VIDEO_DURATION" -v fraction="$fraction" \
    'BEGIN { printf "%.3f", duration * fraction }')"
  ffmpeg -y -ss "$point" -i "$VIDEO_PATH" -frames:v 1 \
    "$ARTIFACT_DIR/$name.png" >/dev/null 2>&1
done
ffmpeg -y -i "$VIDEO_PATH" \
  -vf "fps=16/$VIDEO_DURATION,scale=240:-1,tile=4x4" \
  -frames:v 1 \
  "$ARTIFACT_DIR/gacha-pack-rive-unity-continuous-contact-sheet.png" \
  >/dev/null 2>&1

APP_BINARY_SHA256="$(sha256_file "$APP_BINARY")"
RUNTIME_BINARY_SHA256="$(sha256_file "$RUNTIME_BINARY")"
VIDEO_SHA256="$(sha256_file "$VIDEO_PATH")"
BUILD_MANIFEST_SHA256="$(sha256_file "$XCODE_EXPORT/FidgetingBuildManifest.json")"
DEVICE_NAME="$(xcrun simctl list devices | awk -v id="$DEVICE_ID" \
  '$0 ~ id {sub(/^[[:space:]]*/, ""); sub(/ \(.*/, ""); print; exit}')"

# The canonical .riv remains hash locked for the Pack selection cue only.
# Visual approval remains pending until the user reviews this continuous run.
{
  print "artifact_kind=shipping-source-main-app-continuous-gacha-preview"
  print "captured_at_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  print "device_name=$DEVICE_NAME"
  print "device_udid=$DEVICE_ID"
  print "logical_viewport=$EXPECTED_VIEWPORT"
  print "bundle_id=$BUNDLE_ID"
  print "main_app_build_mode=$MAIN_APP_BUILD_MODE"
  print "source_set_sha256=$SOURCE_SET_SHA256"
  print "generated_source_set_sha256=$GENERATED_SOURCE_SET_SHA256"
  print "unity_reveal_source_set_sha256=$UNITY_REVEAL_SOURCE_SET_SHA256"
  print "unity_build_manifest_sha256=$BUILD_MANIFEST_SHA256"
  print "unity_simulator_development_preview=true"
  print "swift_preview_compilation_condition=DEBUG"
  print "app_binary_sha256=$APP_BINARY_SHA256"
  print "rive_runtime_version=$RUNTIME_VERSION"
  print "rive_runtime_binary_sha256=$RUNTIME_BINARY_SHA256"
  print "rive_asset_sha256=$EXPECTED_RIVE_ASSET_SHA256"
  print "video_sha256=$VIDEO_SHA256"
  print "video_duration_seconds=$VIDEO_DURATION"
  print "video_stream=$VIDEO_STREAM"
  print "pack_carousel_tier_count=6"
  print "selected_pack_tier=signature"
  print "selected_pack_tier_presentation_only=true"
  print "tear_rebound_below_threshold_exactly_once=true"
  print "tear_commit_above_threshold_exactly_once=true"
  print "pack_case_shared_stage=true"
  print "pack_case_transition_seconds=$EXPECTED_PACK_CASE_TRANSITION_SECONDS"
  print "pack_case_event_order=prepare_then_ready_then_overlap_start_then_overlap_complete"
  print "rive_completion_signal=animationSignal"
  print "rive_watchdog_observed=false"
  print "rarity_data_sent_to_rive=false"
  print "unity_case_setup_exactly_once=true"
  print "real3d_root_present=true"
  print "real3d_model_id=$EXPECTED_MODEL_ID"
  print "authoritative_prize_id=$EXPECTED_PRIZE_ID"
  print "authoritative_prize_kind=$EXPECTED_PRIZE_KIND"
  print "authoritative_prize_content_reference=$EXPECTED_CONTENT_REFERENCE"
  print "development_preview_funding_token=metal-three-blade-v1"
  print "development_preview_ticket_credit_exactly_once=true"
  print "authoritative_receipt_acknowledged_after_user_accept=true"
  print "unity_reveal_assembled_only=true"
  print "unity_reveal_exploded_stage_present=false"
  print "correlated_request_id=$CORRELATED_REQUEST_IDS"
  print "intermediate_holder_visible=false"
  print "visual_approval=pending-user-confirmation"
  print "formal_release_build=false"
  print "phone_install=false"
  print "phone_push=false"
} > "$ARTIFACT_DIR/continuous-preview-evidence.txt"

print "Captured one continuous shipping main-app Simulator preview."
print "Video: $VIDEO_PATH"
print "Evidence: $ARTIFACT_DIR/continuous-preview-evidence.txt"
print "Visual approval remains pending for the Pack-to-real-case transition."
print "No formal release build, signed archive, iPhone install, or phone push occurred."
