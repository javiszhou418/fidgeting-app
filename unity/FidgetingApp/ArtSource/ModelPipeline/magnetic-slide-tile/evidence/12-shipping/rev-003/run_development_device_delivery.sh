#!/bin/zsh
set -euo pipefail

REPO_ROOT="/Users/jiawei.zhou/Documents/Fidgeting app"
UNITY_PROJECT="$REPO_ROOT/unity/FidgetingApp"
UNITY_BIN="/Applications/Unity/Hub/Editor/6000.5.6f1/Unity.app/Contents/MacOS/Unity"
EVIDENCE_ROOT="$UNITY_PROJECT/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-003"
LOCK_DIR="/tmp/fidgeting-app-ios-pipeline.lock"
BUNDLE_ID="com.jiaweizhou.fidgetspinner.codex"
UNITY_VERSION="6000.5.6f1"
CONFIGURATION="Release"

source_digest() {
  shasum -a 256 \
    "$UNITY_PROJECT/Assets/_EDC/Scenes/MeshyEDC.unity" \
    "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/MagneticSlideTileShippingMechanism.cs" \
    "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/MagneticSlideTileShippingCoordinator.cs" \
    "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Settings/MagneticSlideTileMechanismSettingsR002.asset" \
    "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Prefabs/MagneticSlideTileGate12R002Candidate.prefab" \
    "$UNITY_PROJECT/Assets/Editor/IosBuildPipeline.cs" \
    "$UNITY_PROJECT/ArtSource/ModelPipeline/magnetic-slide-tile/pipeline.json" \
    | shasum -a 256 | awk '{print $1}'
}

SOURCE_DIGEST="$(source_digest)"
BUILD_KEY="$(printf '%s' "$SOURCE_DIGEST|$UNITY_VERSION|iOS|development|device" \
  | shasum -a 256 | awk '{print $1}')"
JOB_ID="magnetic-slide-g12-r003-$(date -u +%Y%m%dT%H%M%SZ)-${BUILD_KEY[1,8]}"
JOB_ROOT="$EVIDENCE_ROOT/device-delivery/$JOB_ID"
EXPORT_RELATIVE="Builds/iOS/DeviceJobs/$JOB_ID/Export"
EXPORT_PATH="$UNITY_PROJECT/$EXPORT_RELATIVE"
DERIVED_PATH="$UNITY_PROJECT/Builds/iOS/DeviceJobs/$JOB_ID/DerivedData"

mkdir -p "$JOB_ROOT"

acquire_lock() {
  local waited=0
  while ! mkdir "$LOCK_DIR" 2>/dev/null; do
    local active_key=""
    [[ -f "$LOCK_DIR/build-key" ]] \
      && active_key="$(<"$LOCK_DIR/build-key")"
    if [[ "$active_key" == "$BUILD_KEY" ]]; then
      print -r -- "Joining identical active build $BUILD_KEY" \
        | tee -a "$JOB_ROOT/lock.log"
    else
      print -r -- "Waiting for active iOS pipeline lock" \
        | tee -a "$JOB_ROOT/lock.log"
    fi
    sleep 10
    waited=$((waited + 10))
    if (( waited >= 7200 )); then
      print -u2 -- "Timed out waiting for the iOS pipeline lock."
      exit 75
    fi
  done
  print -r -- "$JOB_ID" > "$LOCK_DIR/job-id"
  print -r -- "$BUILD_KEY" > "$LOCK_DIR/build-key"
}

release_lock() {
  rm -f "$LOCK_DIR/job-id" "$LOCK_DIR/build-key"
  rmdir "$LOCK_DIR" 2>/dev/null || true
}

run_devicectl_json() {
  local json_path="$1"
  shift
  : > "$json_path"
  if xcrun devicectl "$@" --json-output "$json_path" > /dev/null; then
    return 0
  fi
  local status="$?"
  local outcome="$(plutil -extract info.outcome raw -o - "$json_path" \
    2>/dev/null || true)"
  if [[ "$outcome" == "success" ]]; then
    print -u2 -- \
      "devicectl returned $status after writing a successful JSON result."
    return 0
  fi
  return "$status"
}

acquire_lock
trap release_lock EXIT INT TERM

print -r -- "jobId=$JOB_ID" > "$JOB_ROOT/job.env"
print -r -- "buildKey=$BUILD_KEY" >> "$JOB_ROOT/job.env"
print -r -- "sourceDigest=$SOURCE_DIGEST" >> "$JOB_ROOT/job.env"
print -r -- "unityVersion=$UNITY_VERSION" >> "$JOB_ROOT/job.env"
print -r -- "configuration=iOS-development-device" >> "$JOB_ROOT/job.env"
print -r -- "exportPath=$EXPORT_PATH" >> "$JOB_ROOT/job.env"
print -r -- "derivedDataPath=$DERIVED_PATH" >> "$JOB_ROOT/job.env"

if pgrep -f \
  "/Unity.app/Contents/MacOS/Unity.*$UNITY_PROJECT|xcodebuild.*$UNITY_PROJECT" \
  > /dev/null; then
  print -u2 -- "Another process is already using the canonical Unity project."
  exit 75
fi

run_devicectl_json "$JOB_ROOT/device-list.json" list devices \
  --filter "hardwareProperties.platform == 'iOS'" --timeout 30
DEVICE_ID="$(plutil -extract result.devices.0.identifier raw -o - \
  "$JOB_ROOT/device-list.json" 2>/dev/null || true)"
DEVICE_UDID="$(plutil -extract result.devices.0.hardwareProperties.udid raw -o - \
  "$JOB_ROOT/device-list.json" 2>/dev/null || true)"
if [[ -z "$DEVICE_ID" || -z "$DEVICE_UDID" ]]; then
  print -u2 -- "No paired physical iPhone is available."
  exit 68
fi

run_devicectl_json "$JOB_ROOT/device-details.json" device info details \
  --device "$DEVICE_ID" --timeout 30
DEVICE_UDID="$(plutil -extract result.hardwareProperties.udid raw -o - \
  "$JOB_ROOT/device-details.json" 2>/dev/null || print -r -- "$DEVICE_UDID")"
TUNNEL_STATE="$(plutil -extract result.connectionProperties.tunnelState raw -o - \
  "$JOB_ROOT/device-details.json" 2>/dev/null || true)"
DDI_AVAILABLE="$(plutil -extract result.deviceProperties.ddiServicesAvailable raw -o - \
  "$JOB_ROOT/device-details.json" 2>/dev/null || true)"
if [[ "$TUNNEL_STATE" != "connected" || "$DDI_AVAILABLE" != "true" ]]; then
  print -u2 -- \
    "The iPhone is unavailable (tunnel=$TUNNEL_STATE, DDI=$DDI_AVAILABLE)."
  exit 68
fi

run_devicectl_json "$JOB_ROOT/device-lock.json" device info lockState \
  --device "$DEVICE_ID" --timeout 30
PASSCODE_REQUIRED="$(plutil -extract result.passcodeRequired raw -o - \
  "$JOB_ROOT/device-lock.json" 2>/dev/null || true)"
if [[ "$PASSCODE_REQUIRED" == "true" ]]; then
  print -u2 -- "The paired iPhone is locked."
  exit 68
fi

IDENTITIES="$(security find-identity -v -p codesigning)"
IDENTITY_NAMES=("${(@f)$(print -r -- "$IDENTITIES" \
  | sed -nE 's/.*"(Apple Development:[^"]+)".*/\1/p')}")
if (( ${#IDENTITY_NAMES[@]} != 1 )); then
  print -u2 -- \
    "Expected one Apple Development identity; found ${#IDENTITY_NAMES[@]}."
  exit 66
fi
CERTIFICATE_SUBJECT="$(security find-certificate -c "$IDENTITY_NAMES[1]" -p \
  | openssl x509 -noout -subject)"
TEAM_IDS=("${(@f)$(print -r -- "$CERTIFICATE_SUBJECT" \
  | sed -nE 's/.*OU[ =]+([A-Z0-9]{10}).*/\1/p' | sort -u)}")
if (( ${#TEAM_IDS[@]} != 1 )); then
  print -u2 -- "The development certificate Team ID is ambiguous."
  exit 66
fi
TEAM_ID="$TEAM_IDS[1]"

SOURCE_COMMIT="$(git -C "$REPO_ROOT" rev-parse HEAD)"
FIDGET_SOURCE_COMMIT="$SOURCE_COMMIT" \
FIDGET_IOS_EXPORT_RELATIVE_PATH="$EXPORT_RELATIVE" \
  "$UNITY_BIN" -batchmode -quit -projectPath "$UNITY_PROJECT" \
  -executeMethod \
  CodexUnityLabEditor.IosBuildPipeline.BuildUniqueIosDevelopmentProject \
  -logFile "$JOB_ROOT/unity-export.log"

PROJECT_FILE="$EXPORT_PATH/Unity-iPhone.xcodeproj/project.pbxproj"
INFO_PLIST="$EXPORT_PATH/Info.plist"
BUILD_MANIFEST="$EXPORT_PATH/FidgetingBuildManifest.json"
if [[ ! -f "$PROJECT_FILE" || ! -f "$INFO_PLIST" \
      || ! -f "$BUILD_MANIFEST" ]]; then
  print -u2 -- "Unity export did not produce complete Xcode markers."
  exit 67
fi
if ! rg -q \
  "iOS Device Xcode project created|Build completed with a result of 'Succeeded'" \
  "$JOB_ROOT/unity-export.log"; then
  print -u2 -- "Unity export lacks a success marker."
  exit 67
fi
if [[ "$(source_digest)" != "$SOURCE_DIGEST" ]]; then
  print -u2 -- "Approved source changed during Unity export."
  exit 74
fi

MANIFEST_BUNDLE_ID="$(plutil -extract bundleIdentifier raw -o - \
  "$BUILD_MANIFEST")"
MANIFEST_VERSION="$(plutil -extract version raw -o - "$BUILD_MANIFEST")"
MANIFEST_BUILD="$(plutil -extract buildNumber raw -o - "$BUILD_MANIFEST")"
MANIFEST_DEVELOPMENT="$(plutil -extract development raw -o - \
  "$BUILD_MANIFEST")"
if [[ "$MANIFEST_BUNDLE_ID" != "$BUNDLE_ID" \
      || "$MANIFEST_DEVELOPMENT" != "true" ]]; then
  print -u2 -- "Unity build manifest identity or configuration is wrong."
  exit 70
fi

xcodebuild \
  -project "$EXPORT_PATH/Unity-iPhone.xcodeproj" \
  -scheme Unity-iPhone \
  -configuration "$CONFIGURATION" \
  -destination "platform=iOS,id=$DEVICE_UDID" \
  -derivedDataPath "$DERIVED_PATH" \
  -allowProvisioningUpdates \
  DEVELOPMENT_TEAM="$TEAM_ID" \
  CODE_SIGN_STYLE=Automatic \
  build > "$JOB_ROOT/xcode-build.log" 2>&1

APP_CANDIDATES=("$DERIVED_PATH/Build/Products/Release-iphoneos"/*.app(N))
if (( ${#APP_CANDIDATES[@]} != 1 )); then
  print -u2 -- "Expected one signed app; found ${#APP_CANDIDATES[@]}."
  exit 69
fi
APP_PATH="$APP_CANDIDATES[1]"
BUILT_BUNDLE_ID="$(plutil -extract CFBundleIdentifier raw -o - \
  "$APP_PATH/Info.plist")"
BUILT_VERSION="$(plutil -extract CFBundleShortVersionString raw -o - \
  "$APP_PATH/Info.plist")"
BUILT_BUILD="$(plutil -extract CFBundleVersion raw -o - \
  "$APP_PATH/Info.plist")"
if [[ "$BUILT_BUNDLE_ID" != "$BUNDLE_ID" \
      || "$BUILT_BUILD" != "$MANIFEST_BUILD" ]]; then
  print -u2 -- "Signed app identity does not match the Unity manifest."
  exit 70
fi

run_devicectl_json "$JOB_ROOT/install.json" device install app \
  --device "$DEVICE_UDID" "$APP_PATH" --timeout 60
run_devicectl_json "$JOB_ROOT/launch.json" device process launch \
  --device "$DEVICE_UDID" --terminate-existing "$BUNDLE_ID" --timeout 30

cat > "$JOB_ROOT/delivery-result.json" <<EOF
{
  "schemaVersion": 1,
  "jobId": "$JOB_ID",
  "buildKey": "$BUILD_KEY",
  "sourceDigest": "$SOURCE_DIGEST",
  "sourceCommit": "$SOURCE_COMMIT",
  "unityVersion": "$UNITY_VERSION",
  "xcodeVersion": "26.4 (17E192)",
  "configuration": "iOS development device",
  "exportPath": "$EXPORT_PATH",
  "derivedDataPath": "$DERIVED_PATH",
  "appPath": "$APP_PATH",
  "bundleIdentifier": "$BUILT_BUNDLE_ID",
  "version": "$BUILT_VERSION",
  "buildNumber": "$BUILT_BUILD",
  "manifestVersion": "$MANIFEST_VERSION",
  "manifestBuildNumber": "$MANIFEST_BUILD",
  "deviceCoreIdentifier": "$DEVICE_ID",
  "deviceUdid": "$DEVICE_UDID",
  "unityExportSucceeded": true,
  "xcodeBuildSucceeded": true,
  "signed": true,
  "installed": true,
  "launched": true,
  "appStoreSubmitted": false,
  "deviceAcceptance": "pending-user-validation"
}
EOF

print -r -- \
  "DELIVERY_SUCCEEDED job=$JOB_ID bundle=$BUILT_BUNDLE_ID version=$BUILT_VERSION build=$BUILT_BUILD"
