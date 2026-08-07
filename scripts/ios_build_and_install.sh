#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
REPO_ROOT="${SCRIPT_DIR:h}"
UNITY_PROJECT="${FIDGET_UNITY_PROJECT:-$REPO_ROOT/unity/FidgetingApp}"
UNITY_BIN="/Applications/Unity/Hub/Editor/6000.5.6f1/Unity.app/Contents/MacOS/Unity"
LOG_PATH="/tmp/fidgeting-app-ios-export.log"
DEVICE_JSON="/tmp/fidgeting-app-ios-devices.json"
DEVICE_DETAILS_JSON="/tmp/fidgeting-app-ios-device-details.json"
DEVICE_LOCK_JSON="/tmp/fidgeting-app-ios-lock-state.json"
LOCK_DIR="/tmp/fidgeting-app-ios-pipeline.lock"
BUNDLE_ID="com.jiaweizhou.fidgetspinner.codex"
BUILD_MANIFEST_NAME="FidgetingBuildManifest.json"
BUILD_CONFIGURATION="Release"
SKIP_UNITY_EXPORT=0
BUILD_MODE="release"
LAUNCH_AFTER_INSTALL=1

for argument in "$@"; do
  case "$argument" in
    --install-existing)
      SKIP_UNITY_EXPORT=1
      ;;
    --development)
      BUILD_MODE="development"
      ;;
    --no-launch)
      LAUNCH_AFTER_INSTALL=0
      ;;
    *)
      echo "Usage: ${0:t} [--development] [--install-existing] [--no-launch]" >&2
      exit 64
      ;;
  esac
done

if [[ "$BUILD_MODE" == "development" ]]; then
  EXPORT_PATH="$UNITY_PROJECT/Builds/iOS/FidgetingAppDevelopment"
  DERIVED_PATH="$UNITY_PROJECT/Builds/iOS/DerivedDataDevelopment"
  UNITY_BUILD_METHOD="CodexUnityLabEditor.IosBuildPipeline.BuildIosDevelopmentProject"
else
  EXPORT_PATH="$UNITY_PROJECT/Builds/iOS/FidgetingApp"
  DERIVED_PATH="$UNITY_PROJECT/Builds/iOS/DerivedData"
  UNITY_BUILD_METHOD="CodexUnityLabEditor.IosBuildPipeline.BuildIosPerformanceProject"
fi

if ! mkdir "$LOCK_DIR" 2>/dev/null; then
  echo "Another Fidget Spinner Unity/Xcode pipeline is already running." >&2
  exit 75
fi
trap 'rmdir "$LOCK_DIR" 2>/dev/null || true' EXIT INT TERM

# Resolve live device, DDI and lock state before starting an expensive Unity or
# Xcode build. `list devices` is cached; `info details` performs the real tunnel
# handshake, while `info lockState` prevents a predictable launch failure.
xcrun devicectl list devices \
  --filter "hardwareProperties.platform == 'iOS'" \
  --timeout 30 \
  --json-output "$DEVICE_JSON" >/dev/null
DEVICE_ID="$(plutil -extract result.devices.0.identifier raw -o - "$DEVICE_JSON" 2>/dev/null || true)"
DEVICE_UDID="$(plutil -extract result.devices.0.hardwareProperties.udid raw -o - "$DEVICE_JSON" 2>/dev/null || true)"
if [[ -z "$DEVICE_ID" || -z "$DEVICE_UDID" ]]; then
  echo "No paired iPhone was found. Connect, unlock and trust this Mac, then rerun." >&2
  exit 68
fi

xcrun devicectl device info details \
  --device "$DEVICE_ID" \
  --timeout 30 \
  --json-output "$DEVICE_DETAILS_JSON" >/dev/null
DEVICE_UDID="$(plutil -extract result.hardwareProperties.udid raw -o - "$DEVICE_DETAILS_JSON" 2>/dev/null || print -r -- "$DEVICE_UDID")"
TUNNEL_STATE="$(plutil -extract result.connectionProperties.tunnelState raw -o - "$DEVICE_DETAILS_JSON" 2>/dev/null || true)"
DDI_AVAILABLE="$(plutil -extract result.deviceProperties.ddiServicesAvailable raw -o - "$DEVICE_DETAILS_JSON" 2>/dev/null || true)"
if [[ "$TUNNEL_STATE" != "connected" || "$DDI_AVAILABLE" != "true" ]]; then
  echo "The paired iPhone is offline (tunnel=$TUNNEL_STATE, DDI=$DDI_AVAILABLE)." >&2
  echo "Reconnect its data cable and accept any Trust/Allow Access prompt, then rerun." >&2
  exit 68
fi

xcrun devicectl device info lockState \
  --device "$DEVICE_ID" \
  --timeout 30 \
  --json-output "$DEVICE_LOCK_JSON" >/dev/null
PASSCODE_REQUIRED="$(plutil -extract result.passcodeRequired raw -o - "$DEVICE_LOCK_JSON" 2>/dev/null || true)"
if (( LAUNCH_AFTER_INSTALL )) && [[ "$PASSCODE_REQUIRED" == "true" ]]; then
  echo "The paired iPhone is locked. Unlock it before building and launching, or use --no-launch for recovery installation only." >&2
  exit 68
fi

IDENTITIES="$(security find-identity -v -p codesigning)"
IDENTITY_NAMES=("${(@f)$(print -r -- "$IDENTITIES" | sed -nE 's/.*"(Apple Development:[^"]+)".*/\1/p')}")
if (( ${#IDENTITY_NAMES[@]} != 1 )); then
  echo "Expected exactly one valid Apple Development identity; found ${#IDENTITY_NAMES[@]}." >&2
  exit 66
fi
CERTIFICATE_SUBJECT="$(security find-certificate -c "$IDENTITY_NAMES[1]" -p | openssl x509 -noout -subject)"
TEAM_IDS=("${(@f)$(print -r -- "$CERTIFICATE_SUBJECT" | sed -nE 's/.*OU[ =]+([A-Z0-9]{10}).*/\1/p' | sort -u)}")
if (( ${#TEAM_IDS[@]} != 1 )); then
  echo "The unique development certificate does not contain exactly one 10-character Team ID (OU)." >&2
  exit 66
fi
TEAM_ID="$TEAM_IDS[1]"

if (( ! SKIP_UNITY_EXPORT )); then
  SOURCE_ROOT="$(git -C "$UNITY_PROJECT" rev-parse --show-toplevel)"
  SOURCE_COMMIT="$(git -C "$SOURCE_ROOT" rev-parse HEAD)"
  if [[ -n "$(git -C "$SOURCE_ROOT" status --porcelain --untracked-files=all)" ]]; then
    echo "Refusing to build from a mutable working tree. Commit the exact approved source first." >&2
    exit 74
  fi

  FIDGET_SOURCE_COMMIT="$SOURCE_COMMIT" "$UNITY_BIN" \
    -batchmode \
    -quit \
    -projectPath "$UNITY_PROJECT" \
    -executeMethod "$UNITY_BUILD_METHOD" \
    -logFile "$LOG_PATH"

  if [[ "$(git -C "$SOURCE_ROOT" rev-parse HEAD)" != "$SOURCE_COMMIT" ]] \
      || [[ -n "$(git -C "$SOURCE_ROOT" status --porcelain --untracked-files=all)" ]]; then
    echo "Source changed during Unity export; refusing to sign or install this artifact." >&2
    exit 74
  fi
fi

PROJECT_FILE="$EXPORT_PATH/Unity-iPhone.xcodeproj/project.pbxproj"
INFO_PLIST="$EXPORT_PATH/Info.plist"
BUILD_MANIFEST="$EXPORT_PATH/$BUILD_MANIFEST_NAME"
if [[ ! -f "$PROJECT_FILE" || ! -f "$INFO_PLIST" || ! -f "$BUILD_MANIFEST" ]]; then
  echo "Unity export did not produce a complete Xcode project." >&2
  exit 67
fi

MANIFEST_BUNDLE_ID="$(plutil -extract bundleIdentifier raw -o - "$BUILD_MANIFEST" 2>/dev/null || true)"
MANIFEST_BUILD_NUMBER="$(plutil -extract buildNumber raw -o - "$BUILD_MANIFEST" 2>/dev/null || true)"
MANIFEST_SOURCE_COMMIT="$(plutil -extract sourceCommit raw -o - "$BUILD_MANIFEST" 2>/dev/null || true)"
if [[ "$MANIFEST_BUNDLE_ID" != "$BUNDLE_ID" || -z "$MANIFEST_BUILD_NUMBER" \
      || -z "$MANIFEST_SOURCE_COMMIT" || "$MANIFEST_SOURCE_COMMIT" == "local-preview" ]]; then
  echo "Refusing to install an untraceable or mismatched Unity export." >&2
  exit 70
fi

xcodebuild \
  -project "$EXPORT_PATH/Unity-iPhone.xcodeproj" \
  -scheme Unity-iPhone \
  -configuration "$BUILD_CONFIGURATION" \
  -destination "platform=iOS,id=$DEVICE_UDID" \
  -derivedDataPath "$DERIVED_PATH" \
  -allowProvisioningUpdates \
  DEVELOPMENT_TEAM="$TEAM_ID" \
  CODE_SIGN_STYLE=Automatic \
  build

APP_PATH="$(find "$DERIVED_PATH/Build/Products/$BUILD_CONFIGURATION-iphoneos" -maxdepth 1 -name '*.app' -print -quit)"
if [[ -z "$APP_PATH" || ! -d "$APP_PATH" ]]; then
  echo "Xcode succeeded but the signed .app could not be found." >&2
  exit 69
fi

BUILT_BUNDLE_ID="$(plutil -extract CFBundleIdentifier raw -o - "$APP_PATH/Info.plist" 2>/dev/null || true)"
if [[ "$BUILT_BUNDLE_ID" != "$BUNDLE_ID" ]]; then
  echo "Refusing to install a second app identity: expected $BUNDLE_ID, found $BUILT_BUNDLE_ID." >&2
  exit 70
fi
BUILT_BUILD_NUMBER="$(plutil -extract CFBundleVersion raw -o - "$APP_PATH/Info.plist" 2>/dev/null || true)"
if [[ "$BUILT_BUILD_NUMBER" != "$MANIFEST_BUILD_NUMBER" ]]; then
  echo "Refusing to install: app build $BUILT_BUILD_NUMBER does not match manifest $MANIFEST_BUILD_NUMBER." >&2
  exit 70
fi

xcrun devicectl device install app --device "$DEVICE_UDID" "$APP_PATH" --timeout 60
if (( LAUNCH_AFTER_INSTALL )); then
  xcrun devicectl device process launch \
    --device "$DEVICE_UDID" \
    --terminate-existing \
    "$BUNDLE_ID" \
    --timeout 30
  echo "Installed and launched $BUILD_MODE $BUNDLE_ID on $DEVICE_UDID"
else
  echo "Installed $BUILD_MODE $BUNDLE_ID without launching it on $DEVICE_UDID"
fi
