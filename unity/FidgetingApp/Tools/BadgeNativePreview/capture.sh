#!/bin/zsh
set -euo pipefail

TOOL_DIR="${0:A:h}"
PROJECT_ROOT="${TOOL_DIR:h:h}"
ARTIFACT_DIR="$PROJECT_ROOT/Artifacts/BadgeSpecial/NativeB10"
BUILD_ROOT="$(mktemp -d /tmp/fidget-badge-native-preview.XXXXXX)"
MODULE_CACHE="$BUILD_ROOT/ModuleCache"
APP_DIR="$BUILD_ROOT/BadgeNativePreview.app"
APP_BINARY="$APP_DIR/BadgeNativePreview"
SOURCE_SNAPSHOT_DIR="$BUILD_ROOT/Sources"
BUNDLE_ID="com.jiaweizhou.fidgetspinner.badge-native-preview"

mkdir -p "$MODULE_CACHE" "$APP_DIR" "$ARTIFACT_DIR" "$SOURCE_SNAPSHOT_DIR"

# The b10 Challenge+Legacy master artwork is a fixed, user-approved handoff
# (ArtSource/BadgeSystem/ChallengeLegacyApproved20260821/); this preview must
# never regenerate or otherwise mutate it. Re-verify the shipping bundle
# against the approved manifest instead of rebuilding assets.
python3 "$PROJECT_ROOT/Tools/BadgeAssetGenerator/import_b10_shipping_assets.py"

# Compile an immutable point-in-time copy. The canonical Unity project may be
# open while visual work continues, and swiftc rejects an input whose mtime
# changes during compilation. Snapshotting also guarantees that every image in
# one contact sheet comes from the exact same source revision.
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetProductUIComponents.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetProductUIComponents.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetComboHalo.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetComboHalo.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetGachaStore.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetGachaStore.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetGachaPackPresentation.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetGachaPackPresentation.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetGachaRiveGateRules.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetGachaRiveGateRules.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetGachaRivePresentation.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetGachaRivePresentation.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetGachaStorefront.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetGachaStorefront.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/FidgetStoreKit.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetStoreKit.swift"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/CodexSwiftUIOverlay.swift" \
  "$SOURCE_SNAPSHOT_DIR/CodexSwiftUIOverlay.swift"

xcrun --sdk iphonesimulator swiftc \
  -D DEBUG \
  -parse-as-library \
  -target arm64-apple-ios15.0-simulator \
  -module-cache-path "$MODULE_CACHE" \
  "$SOURCE_SNAPSHOT_DIR/FidgetProductUIComponents.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetComboHalo.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetGachaStore.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetGachaPackPresentation.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetGachaRiveGateRules.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetGachaRivePresentation.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetGachaStorefront.swift" \
  "$SOURCE_SNAPSHOT_DIR/FidgetStoreKit.swift" \
  "$SOURCE_SNAPSHOT_DIR/CodexSwiftUIOverlay.swift" \
  "$TOOL_DIR/BadgeNativePreviewApp.swift" \
  -o "$APP_BINARY"

cp "$TOOL_DIR/Info.plist" "$APP_DIR/Info.plist"
cp "$PROJECT_ROOT/Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf" \
  "$APP_DIR/Oxanium-VariableFont_wght.ttf"
for ARTWORK in "$PROJECT_ROOT"/Assets/Plugins/iOS/BadgeArtwork/*.png; do
  cp "$ARTWORK" "$APP_DIR/${ARTWORK:t}"
done
cp "$PROJECT_ROOT/Assets/Plugins/iOS/BadgeArtwork/badge-b10-manifest.json" \
  "$APP_DIR/badge-b10-manifest.json"
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

for MODE in \
  catalog \
  detail \
  states \
  unlock \
  share \
  reference \
  thumbnailPower \
  thumbnailPulse \
  thumbnailTechnique \
  thumbnailCombo \
  thumbnailFocus \
  thumbnailCollectorFoundation \
  thumbnailCollectorCollection \
  thumbnailChallengeLegacy; do
  xcrun simctl launch --terminate-running-process \
    "$DEVICE_ID" "$BUNDLE_ID" --mode="$MODE" >/dev/null
  if [[ "$MODE" == "catalog" ]]; then
    sleep 5
  elif [[ "$MODE" == thumbnail* ]]; then
    sleep 3
  else
    sleep 2
  fi
  xcrun simctl io "$DEVICE_ID" screenshot \
    "$ARTIFACT_DIR/badge-native-$MODE.png" >/dev/null
done

DATA_CONTAINER="$(xcrun simctl get_app_container "$DEVICE_ID" "$BUNDLE_ID" data)"
cp "$DATA_CONTAINER/Documents/badge-share-card-1080.png" \
  "$ARTIFACT_DIR/badge-share-card-1080.png"
THUMBNAIL_MODES=(
  thumbnailPower
  thumbnailPulse
  thumbnailTechnique
  thumbnailCombo
  thumbnailFocus
  thumbnailCollectorFoundation
  thumbnailCollectorCollection
  thumbnailChallengeLegacy
)
for MODE in "${THUMBNAIL_MODES[@]}"; do
  CROP_HEIGHT=1450
  if [[ "$MODE" == "thumbnailCollectorCollection" ]]; then
    # Seven badges occupy a third row; retain its label and lower spacing.
    CROP_HEIGHT=1700
  fi
  ffmpeg -y \
    -i "$ARTIFACT_DIR/badge-native-$MODE.png" \
    -vf "crop=1206:${CROP_HEIGHT}:0:135" \
    -frames:v 1 \
    -update 1 \
    "$ARTIFACT_DIR/badge-thumbnails-$MODE.png" >/dev/null 2>&1
done

ffmpeg -y \
  -i "$ARTIFACT_DIR/badge-thumbnails-thumbnailPower.png" \
  -i "$ARTIFACT_DIR/badge-thumbnails-thumbnailPulse.png" \
  -i "$ARTIFACT_DIR/badge-thumbnails-thumbnailTechnique.png" \
  -i "$ARTIFACT_DIR/badge-thumbnails-thumbnailCombo.png" \
  -i "$ARTIFACT_DIR/badge-thumbnails-thumbnailFocus.png" \
  -filter_complex "[0:v][1:v][2:v][3:v][4:v]vstack=inputs=5[out]" \
  -map "[out]" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/badge-thumbnails-toy.png" >/dev/null 2>&1

ffmpeg -y \
  -i "$ARTIFACT_DIR/badge-thumbnails-thumbnailCollectorFoundation.png" \
  -i "$ARTIFACT_DIR/badge-thumbnails-thumbnailCollectorCollection.png" \
  -filter_complex "[0:v][1:v]vstack=inputs=2[out]" \
  -map "[out]" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/badge-thumbnails-collector.png" >/dev/null 2>&1

cp "$ARTIFACT_DIR/badge-thumbnails-thumbnailChallengeLegacy.png" \
  "$ARTIFACT_DIR/badge-thumbnails-challenge-legacy.png"

ffmpeg -y \
  -i "$ARTIFACT_DIR/badge-thumbnails-toy.png" \
  -i "$ARTIFACT_DIR/badge-thumbnails-collector.png" \
  -i "$ARTIFACT_DIR/badge-thumbnails-challenge-legacy.png" \
  -filter_complex "[0:v][1:v][2:v]vstack=inputs=3[out]" \
  -map "[out]" \
  -frames:v 1 \
  -update 1 \
  "$ARTIFACT_DIR/badge-thumbnails-all.png" >/dev/null 2>&1

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
