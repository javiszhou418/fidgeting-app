#!/bin/zsh
set -euo pipefail

REPO_ROOT="/Users/jiawei.zhou/Documents/Fidgeting app"
UNITY_PROJECT="$REPO_ROOT/unity/FidgetingApp"
UNITY_BIN="/Applications/Unity/Hub/Editor/6000.5.6f1/Unity.app/Contents/MacOS/Unity"
EVIDENCE_ROOT="$UNITY_PROJECT/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/runtime-recovery-build42"
LOCK_DIR="/tmp/fidgeting-app-ios-pipeline.lock"
UNITY_LOCK_DIR="/tmp/fidgeting-app-unity-canonical.lock"
BUNDLE_ID="com.jiaweizhou.fidgetspinner.codex"
REQUESTED_BUILD_NUMBER=42
UNITY_VERSION="6000.5.6f1"
CONFIGURATION="Release"
PROJECT_SETTINGS="$UNITY_PROJECT/ProjectSettings/ProjectSettings.asset"

SOURCE_FILES=(
  "$UNITY_PROJECT/Assets/_EDC/Scenes/MeshyEDC.unity"
  "$UNITY_PROJECT/Assets/_EDC/Runtime/EdcSliderController.cs"
  "$UNITY_PROJECT/Assets/_EDC/Runtime/SharedPresentationGestureController.cs"
  "$UNITY_PROJECT/Assets/_EDC/Runtime/EdcPortraitCameraFramer.cs"
  "$UNITY_PROJECT/Assets/_EDC/Runtime/MagneticSlideDetentAudio.cs"
  "$UNITY_PROJECT/Assets/_EDC/Runtime/MagneticSlideShippingLighting.cs"
  "$UNITY_PROJECT/Assets/_EDC/Audio/MagneticSlide_AlloyClick_766Hz.wav"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/MagneticSlideTileShippingMechanism.cs"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/MagneticSlideTileShippingCoordinator.cs"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/MagneticSlideTileMechanismSettings.cs"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Settings/MagneticSlideTileMechanismSettingsR002.asset"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Prefabs/MagneticSlideTileGate12R002Candidate.prefab"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R013/Generated/MovingTopBody_CapOnly_R013.asset"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R013/Generated/MovingTopBody_TrueLayerBody_R013.asset"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R013/Generated/BottomExterior_CapOnly_R013.asset"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R013/Generated/BottomExterior_TrueLayerBody_R013.asset"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R013/Runtime/MagneticSlideTrueLayerAssembly.cs"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R014/Materials/M_G11R014_UpperRev12DetailSubstrate.mat"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R014/Materials/M_G11R014_UpperRev12DetailMotif.mat"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R014/Materials/M_G11R014_UpperDetailPreservingCrystal.mat"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R014/Materials/M_G11R014_LowerRev12DetailSubstrate.mat"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R014/Materials/M_G11R014_LowerRev12DetailMotif.mat"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R014/Materials/M_G11R014_LowerDetailPreservingCrystal.mat"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R014/Shaders/MagneticSlideHybridSubstrateR014.shader"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R014/Shaders/MagneticSlideHybridMotifR014.shader"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R014/Shaders/MagneticSlideHybridCrystalR014.shader"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R011/Imported/Environment/MagneticSlideTileGate11R011Environment.cubemap"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R011/Imported/Textures/upper-albedo.png"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R011/Imported/Textures/lower-albedo.png"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R011/Imported/Textures/upper-roughness.png"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R011/Imported/Textures/lower-roughness.png"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R011/Imported/Textures/upper-transport-normal-r011.png"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R011/Imported/Textures/lower-transport-normal-r011.png"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R011/Imported/Textures/upper-artwork-mask.png"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R011/Imported/Textures/lower-artwork-mask.png"
  "$UNITY_PROJECT/Assets/_EDC/Candidates/MagneticSlideTileGate11R011/Imported/Textures/top-perimeter-mask.png"
  "$UNITY_PROJECT/Assets/Scripts/Product/FidgetAppCoordinator.cs"
  "$UNITY_PROJECT/Assets/Scripts/FidgetSpinner/IosHaptics.cs"
  "$UNITY_PROJECT/Assets/InputSystem_Actions.inputactions"
  "$UNITY_PROJECT/Assets/Editor/IosBuildPipeline.cs"
  "$PROJECT_SETTINGS"
)

source_digest() {
  shasum -a 256 "${SOURCE_FILES[@]}" | shasum -a 256 | awk '{print $1}'
}

write_source_hashes() {
  shasum -a 256 "${SOURCE_FILES[@]}" > "$1"
}

existing_success() {
  local result existing_key existing_build installed launched
  for result in "$EVIDENCE_ROOT"/device-delivery/*/delivery-result.json(N); do
    existing_key="$(plutil -extract buildKey raw -o - "$result" 2>/dev/null || true)"
    existing_build="$(plutil -extract buildNumber raw -o - "$result" 2>/dev/null || true)"
    installed="$(plutil -extract installed raw -o - "$result" 2>/dev/null || true)"
    launched="$(plutil -extract launched raw -o - "$result" 2>/dev/null || true)"
    if [[ "$existing_key" == "$BUILD_KEY" \
          && "$existing_build" == "$BUILD_NUMBER" \
          && "$installed" == "true" \
          && "$launched" == "true" ]]; then
      print -r -- "REUSED_SUCCEEDED_DELIVERY result=$result"
      return 0
    fi
  done
  return 1
}

acquire_lock_dir() {
  local directory="$1"
  local waited=0
  while ! mkdir "$directory" 2>/dev/null; do
    print -r -- "Waiting for exclusive Unity integration/build writer"
    sleep 10
    waited=$((waited + 10))
    if (( waited >= 7200 )); then
      print -u2 -- "Timed out waiting for the iOS pipeline lock."
      exit 75
    fi
  done
}

acquire_lock() {
  acquire_lock_dir "$LOCK_DIR"
  acquire_lock_dir "$UNITY_LOCK_DIR"
}

record_lock_owner() {
  print -r -- "$JOB_ID" > "$LOCK_DIR/job-id"
  print -r -- "$BUILD_KEY" > "$LOCK_DIR/build-key"
  print -r -- "$JOB_ID" > "$UNITY_LOCK_DIR/job-id"
  print -r -- "$BUILD_KEY" > "$UNITY_LOCK_DIR/build-key"
}

release_lock() {
  rm -f "$LOCK_DIR/job-id" "$LOCK_DIR/build-key"
  rmdir "$LOCK_DIR" 2>/dev/null || true
  rm -f "$UNITY_LOCK_DIR/job-id" "$UNITY_LOCK_DIR/build-key"
  rmdir "$UNITY_LOCK_DIR" 2>/dev/null || true
}

wait_for_canonical_writers() {
  local stable_checks=0
  local waited=0
  while (( stable_checks < 3 )); do
    if pgrep -f \
      "^/Applications/Unity/Hub/Editor/.*/Unity.app/Contents/MacOS/Unity .* -projectPath $UNITY_PROJECT( |$)|^.*xcodebuild .*${UNITY_PROJECT}" \
      > /dev/null; then
      stable_checks=0
    else
      stable_checks=$((stable_checks + 1))
    fi
    (( stable_checks >= 3 )) && break
    sleep 2
    waited=$((waited + 2))
    if (( waited >= 7200 )); then
      print -u2 -- "Timed out waiting for the canonical Unity writer."
      exit 75
    fi
  done
}

allocate_build_number() {
  local next="$REQUESTED_BUILD_NUMBER"
  local result existing
  for result in "$EVIDENCE_ROOT"/device-delivery/*/delivery-result.json(N); do
    existing="$(plutil -extract buildNumber raw -o - "$result" 2>/dev/null || true)"
    if [[ "$existing" == <-> && "$existing" -ge "$next" ]]; then
      next=$((existing + 1))
    fi
  done
  local configured="$(awk '
    /buildNumber:/ { in_build_number=1; next }
    in_build_number && /iPhone:/ { print $2; exit }
  ' "$PROJECT_SETTINGS")"
  if [[ "$configured" == <-> && "$configured" -gt "$next" ]]; then
    next="$configured"
  fi
  print -r -- "$next"
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
    return 0
  fi
  return "$status"
}

trap release_lock EXIT INT TERM
acquire_lock

wait_for_canonical_writers
BUILD_NUMBER="$(allocate_build_number)"
JOB_ID="magnetic-slide-build${BUILD_NUMBER}-$(date -u +%Y%m%dT%H%M%SZ)-snapshot"
JOB_ROOT="$EVIDENCE_ROOT/device-delivery/$JOB_ID"
mkdir -p "$JOB_ROOT"

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

node "$REPO_ROOT/skills/fidgeting-model-pipeline/scripts/validate_model_pipeline.mjs" \
  magnetic-slide-tile > "$JOB_ROOT/model-pipeline-preflight.json"
if ! rg -q '"approved": "12/12"' \
  "$JOB_ROOT/model-pipeline-preflight.json"; then
  print -u2 -- "Magnetic slide pipeline preflight is not 12/12 approved."
  exit 67
fi

"$UNITY_BIN" -batchmode -projectPath "$UNITY_PROJECT" \
  -runTests -testPlatform EditMode \
  -testFilter "FidgetingApp.EDC.Tests" \
  -testResults "$JOB_ROOT/unity-editmode-results.xml" \
  -logFile "$JOB_ROOT/unity-editmode.log"
"$UNITY_BIN" -batchmode -projectPath "$UNITY_PROJECT" \
  -runTests -testPlatform PlayMode \
  -testFilter \
  "FidgetingApp.MagneticSlide.PlayModeTests.MagneticSlideTileInputPlayModeTests" \
  -testResults "$JOB_ROOT/unity-playmode-results.xml" \
  -logFile "$JOB_ROOT/unity-playmode.log"
python3 - \
  "$JOB_ROOT/unity-editmode-results.xml" \
  "$JOB_ROOT/unity-playmode-results.xml" <<'PY'
import sys
import xml.etree.ElementTree as ET

for path in sys.argv[1:]:
    root = ET.parse(path).getroot()
    if root.attrib.get("result") != "Passed" or root.attrib.get("failed") != "0":
        raise SystemExit(f"Unity preflight failed: {path}")
    print(
        f"{path}: {root.attrib.get('passed')}/{root.attrib.get('total')} passed"
    )
PY

PROJECT_SETTINGS_HASH_BEFORE="$(
  shasum -a 256 "$PROJECT_SETTINGS" | awk '{print $1}')"
PROJECT_SETTINGS_MTIME_BEFORE="$(
  stat -f '%Sm' -t '%Y-%m-%dT%H:%M:%SZ' "$PROJECT_SETTINGS")"
FIDGET_IOS_BUILD_NUMBER="$BUILD_NUMBER" \
  "$UNITY_BIN" -batchmode -quit -projectPath "$UNITY_PROJECT" \
  -executeMethod \
  CodexUnityLabEditor.IosBuildPipeline.PrepareUniqueIosDevelopmentSnapshot \
  -logFile "$JOB_ROOT/unity-prepare-snapshot.log"
if ! rg -q \
  "iOS immutable snapshot prepared for Build $BUILD_NUMBER" \
  "$JOB_ROOT/unity-prepare-snapshot.log"; then
  print -u2 -- "Unity did not confirm immutable snapshot preparation."
  exit 67
fi

PROJECT_SETTINGS_HASH_SNAPSHOT="$(
  shasum -a 256 "$PROJECT_SETTINGS" | awk '{print $1}')"
PROJECT_SETTINGS_MTIME_SNAPSHOT="$(
  stat -f '%Sm' -t '%Y-%m-%dT%H:%M:%SZ' "$PROJECT_SETTINGS")"
sleep 5
PROJECT_SETTINGS_HASH_STABLE="$(
  shasum -a 256 "$PROJECT_SETTINGS" | awk '{print $1}')"
if [[ "$PROJECT_SETTINGS_HASH_STABLE" != "$PROJECT_SETTINGS_HASH_SNAPSHOT" ]]; then
  print -u2 -- "ProjectSettings.asset changed during the stability interval."
  exit 74
fi

write_source_hashes "$JOB_ROOT/source-hashes-snapshot.txt"
SOURCE_DIGEST="$(source_digest)"
sleep 3
if [[ "$(source_digest)" != "$SOURCE_DIGEST" ]]; then
  print -u2 -- "Shipping source changed during the snapshot stability interval."
  exit 74
fi

BUILD_KEY="$(printf '%s' \
  "$SOURCE_DIGEST|$UNITY_VERSION|iOS|development|device|$BUILD_NUMBER" \
  | shasum -a 256 | awk '{print $1}')"
EXPORT_RELATIVE="Builds/iOS/DeviceJobs/$JOB_ID/Export"
EXPORT_PATH="$UNITY_PROJECT/$EXPORT_RELATIVE"
DERIVED_PATH="$UNITY_PROJECT/Builds/iOS/DeviceJobs/$JOB_ID/DerivedData"
record_lock_owner

print -r -- "jobId=$JOB_ID" > "$JOB_ROOT/job.env"
print -r -- "buildKey=$BUILD_KEY" >> "$JOB_ROOT/job.env"
print -r -- "sourceDigest=$SOURCE_DIGEST" >> "$JOB_ROOT/job.env"
print -r -- "buildNumber=$BUILD_NUMBER" >> "$JOB_ROOT/job.env"
print -r -- "unityVersion=$UNITY_VERSION" >> "$JOB_ROOT/job.env"
print -r -- "configuration=iOS-development-device" >> "$JOB_ROOT/job.env"
print -r -- "projectSettingsHashBefore=$PROJECT_SETTINGS_HASH_BEFORE" \
  >> "$JOB_ROOT/job.env"
print -r -- "projectSettingsMtimeBefore=$PROJECT_SETTINGS_MTIME_BEFORE" \
  >> "$JOB_ROOT/job.env"
print -r -- "projectSettingsHashSnapshot=$PROJECT_SETTINGS_HASH_SNAPSHOT" \
  >> "$JOB_ROOT/job.env"
print -r -- "projectSettingsMtimeSnapshot=$PROJECT_SETTINGS_MTIME_SNAPSHOT" \
  >> "$JOB_ROOT/job.env"
print -r -- "projectSettingsStableIntervalSeconds=5" \
  >> "$JOB_ROOT/job.env"
print -r -- "sourceStableIntervalSeconds=3" >> "$JOB_ROOT/job.env"
print -r -- "exportPath=$EXPORT_PATH" >> "$JOB_ROOT/job.env"
print -r -- "derivedDataPath=$DERIVED_PATH" >> "$JOB_ROOT/job.env"

if existing_success; then
  exit 0
fi

SOURCE_COMMIT="$(git -C "$REPO_ROOT" rev-parse HEAD)"
FIDGET_SOURCE_COMMIT="$SOURCE_COMMIT" \
FIDGET_IOS_BUILD_NUMBER="$BUILD_NUMBER" \
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
write_source_hashes "$JOB_ROOT/source-hashes-after-export.txt"
if ! cmp -s \
  "$JOB_ROOT/source-hashes-snapshot.txt" \
  "$JOB_ROOT/source-hashes-after-export.txt"; then
  python3 - \
    "$JOB_ROOT/source-hashes-snapshot.txt" \
    "$JOB_ROOT/source-hashes-after-export.txt" \
    "$JOB_ROOT/source-mutation.json" <<'PY'
import json
import sys

def read_hashes(path):
    values = {}
    with open(path, encoding="utf-8") as stream:
        for line in stream:
            digest, file_path = line.rstrip().split("  ", 1)
            values[file_path] = digest
    return values

before = read_hashes(sys.argv[1])
after = read_hashes(sys.argv[2])
changes = [
    {
        "path": path,
        "beforeSha256": before.get(path),
        "afterSha256": after.get(path),
    }
    for path in sorted(set(before) | set(after))
    if before.get(path) != after.get(path)
]
with open(sys.argv[3], "w", encoding="utf-8") as stream:
    json.dump({"schemaVersion": 1, "changes": changes}, stream, indent=2)
    stream.write("\n")
print(", ".join(change["path"] for change in changes))
PY
  print -u2 -- \
    "Shipping source changed during Unity export; see source-mutation.json."
  exit 74
fi

MANIFEST_BUILD="$(plutil -extract buildNumber raw -o - "$BUILD_MANIFEST")"
MANIFEST_BUNDLE_ID="$(plutil -extract bundleIdentifier raw -o - \
  "$BUILD_MANIFEST")"
MANIFEST_DEVELOPMENT="$(plutil -extract development raw -o - \
  "$BUILD_MANIFEST")"
if [[ "$MANIFEST_BUILD" != "$BUILD_NUMBER" \
      || "$MANIFEST_BUNDLE_ID" != "$BUNDLE_ID" \
      || "$MANIFEST_DEVELOPMENT" != "true" ]]; then
  print -u2 -- "Unity build manifest identity is wrong."
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
      || "$BUILT_BUILD" != "$BUILD_NUMBER" ]]; then
  print -u2 -- "Signed app identity does not match Build $BUILD_NUMBER."
  exit 70
fi

run_devicectl_json "$JOB_ROOT/install.json" device install app \
  --device "$DEVICE_UDID" "$APP_PATH" --timeout 60
run_devicectl_json "$JOB_ROOT/launch.json" device process launch \
  --device "$DEVICE_UDID" --terminate-existing "$BUNDLE_ID" --timeout 30

python3 - "$DEVICE_UDID" "$BUNDLE_ID" "$JOB_ROOT/runtime-console.log" <<'PY'
import signal
import subprocess
import sys

device, bundle, output = sys.argv[1:]
command = [
    "xcrun", "devicectl", "device", "process", "launch",
    "--device", device, "--terminate-existing", "--console", bundle,
]
with open(output, "w", encoding="utf-8") as stream:
    process = subprocess.Popen(
        command,
        stdin=subprocess.DEVNULL,
        stdout=stream,
        stderr=subprocess.STDOUT,
        text=True,
    )
    try:
        process.wait(timeout=18)
    except subprocess.TimeoutExpired:
        process.send_signal(signal.SIGINT)
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
PY

run_devicectl_json "$JOB_ROOT/relaunch-after-console.json" \
  device process launch \
  --device "$DEVICE_UDID" --terminate-existing "$BUNDLE_ID" --timeout 30
sleep 5

run_devicectl_json "$JOB_ROOT/processes.json" device info processes \
  --device "$DEVICE_ID" --timeout 30
APP_PID="$(python3 - "$JOB_ROOT/processes.json" <<'PY'
import json
import sys

with open(sys.argv[1], encoding="utf-8") as stream:
    payload = json.load(stream)
matches = [
    item["processIdentifier"]
    for item in payload.get("result", {}).get("runningProcesses", [])
    if "/FidgetSpinner.app/FidgetSpinner" in item.get("executable", "")
]
if len(matches) != 1:
    raise SystemExit(f"expected one running app process, found {len(matches)}")
print(matches[0])
PY
)"

RUNTIME_MARKERS=false
if rg -q \
  "\\[MagneticSlideRuntime\\] (shipping-coordinator-ready|input-ready|audio-ready)" \
  "$JOB_ROOT/runtime-console.log"; then
  RUNTIME_MARKERS=true
fi

cat > "$JOB_ROOT/delivery-result.json" <<EOF
{
  "schemaVersion": 1,
  "jobId": "$JOB_ID",
  "buildKey": "$BUILD_KEY",
  "sourceDigest": "$SOURCE_DIGEST",
  "sourceCommit": "$SOURCE_COMMIT",
  "unityVersion": "$UNITY_VERSION",
  "configuration": "iOS development device",
  "exportPath": "$EXPORT_PATH",
  "derivedDataPath": "$DERIVED_PATH",
  "appPath": "$APP_PATH",
  "bundleIdentifier": "$BUILT_BUNDLE_ID",
  "version": "$BUILT_VERSION",
  "buildNumber": "$BUILT_BUILD",
  "deviceCoreIdentifier": "$DEVICE_ID",
  "deviceUdid": "$DEVICE_UDID",
  "unityExportSucceeded": true,
  "xcodeBuildSucceeded": true,
  "signed": true,
  "installed": true,
  "launched": true,
  "launchedProcessIdentifier": $APP_PID,
  "runtimeStartupMarkersCaptured": $RUNTIME_MARKERS,
  "appStoreSubmitted": false,
  "deviceAcceptance": "pending-user-validation"
}
EOF

print -r -- \
  "DELIVERY_SUCCEEDED job=$JOB_ID bundle=$BUILT_BUNDLE_ID version=$BUILT_VERSION build=$BUILT_BUILD pid=$APP_PID runtimeMarkers=$RUNTIME_MARKERS"
