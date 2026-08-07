#!/bin/zsh
set -euo pipefail

SCRIPT_DIR="${0:A:h}"
REPO_ROOT="${SCRIPT_DIR:h}"
BUNDLE_ID="com.jiaweizhou.fidgetspinner.codex"
AUDIT_ARGUMENT="--fidgeting-performance-audit"
AUDIT_ENVIRONMENT='{"FIDGETING_PERFORMANCE_AUDIT":"1"}'
AUDIT_MODE="release"
AUDIT_TIMEOUT=1840
DEVICE_JSON="/tmp/fidgeting-app-soak-devices.json"
DEVICE_DETAILS_JSON="/tmp/fidgeting-app-soak-device-details.json"
DEVICE_LOCK_JSON="/tmp/fidgeting-app-soak-lock-state.json"
BUILD_ID="$(date '+%Y-%m-%d-%H%M%S')-iphone-soak"
ARTIFACT_DIR="$REPO_ROOT/Artifacts/Performance/$BUILD_ID"
CONSOLE_LOG="$ARTIFACT_DIR/device-console.log"
SUMMARY_JSON="$ARTIFACT_DIR/summary.json"
REPORT_PATH="$ARTIFACT_DIR/REPORT.md"

POSITIONAL_ARGUMENTS=()
for argument in "$@"; do
  case "$argument" in
    --development-gc)
      AUDIT_MODE="development-gc"
      AUDIT_TIMEOUT=340
      AUDIT_ENVIRONMENT='{"FIDGETING_PERFORMANCE_AUDIT":"1","FIDGETING_PERFORMANCE_AUDIT_MODE":"development-gc"}'
      ;;
    --*)
      echo "Usage: ${0:t} [--development-gc] [artifact-directory]" >&2
      exit 64
      ;;
    *)
      POSITIONAL_ARGUMENTS+=("$argument")
      ;;
  esac
done
if (( ${#POSITIONAL_ARGUMENTS[@]} > 1 )); then
  echo "Usage: ${0:t} [--development-gc] [artifact-directory]" >&2
  exit 64
fi
if (( ${#POSITIONAL_ARGUMENTS[@]} == 1 )); then
  ARTIFACT_DIR="${POSITIONAL_ARGUMENTS[1]:A}"
  CONSOLE_LOG="$ARTIFACT_DIR/device-console.log"
  SUMMARY_JSON="$ARTIFACT_DIR/summary.json"
  REPORT_PATH="$ARTIFACT_DIR/REPORT.md"
fi

ENVIRONMENT_C="${FIDGET_AUDIT_ENVIRONMENT_C:-}"
BRIGHTNESS_PERCENT="${FIDGET_AUDIT_BRIGHTNESS_PERCENT:-}"
POWER_STATE="${FIDGET_AUDIT_POWER_STATE:-}"
if [[ "$AUDIT_MODE" == "release" ]]; then
  if [[ -z "$ENVIRONMENT_C" || -z "$BRIGHTNESS_PERCENT" || -z "$POWER_STATE" ]]; then
    echo "Release audit requires FIDGET_AUDIT_ENVIRONMENT_C, FIDGET_AUDIT_BRIGHTNESS_PERCENT and FIDGET_AUDIT_POWER_STATE=unplugged." >&2
    exit 64
  fi
  if [[ "$ENVIRONMENT_C" != <->(|.<->) || "$BRIGHTNESS_PERCENT" != <-> ]]; then
    echo "Environment temperature and brightness must be numeric values." >&2
    exit 64
  fi
  if [[ "$POWER_STATE" != "unplugged" ]]; then
    echo "Release audit requires battery power: FIDGET_AUDIT_POWER_STATE=unplugged." >&2
    exit 64
  fi
  if (( BRIGHTNESS_PERCENT < 45 || BRIGHTNESS_PERCENT > 55 )); then
    echo "Release audit brightness must be declared between 45% and 55%." >&2
    exit 64
  fi
else
  ENVIRONMENT_C="not-required-for-gc"
  BRIGHTNESS_PERCENT="not-required-for-gc"
  POWER_STATE="not-required-for-gc"
fi

mkdir -p "$ARTIFACT_DIR"

xcrun devicectl list devices \
  --filter "hardwareProperties.platform == 'iOS'" \
  --timeout 30 \
  --json-output "$DEVICE_JSON" >/dev/null
DEVICE_ID="$(plutil -extract result.devices.0.identifier raw -o - "$DEVICE_JSON" 2>/dev/null || true)"
if [[ -z "$DEVICE_ID" ]]; then
  echo "No paired iPhone was found. Connect, unlock and trust this Mac." >&2
  exit 68
fi

xcrun devicectl device info details \
  --device "$DEVICE_ID" \
  --timeout 30 \
  --json-output "$DEVICE_DETAILS_JSON" >/dev/null
TUNNEL_STATE="$(plutil -extract result.connectionProperties.tunnelState raw -o - "$DEVICE_DETAILS_JSON" 2>/dev/null || true)"
DDI_AVAILABLE="$(plutil -extract result.deviceProperties.ddiServicesAvailable raw -o - "$DEVICE_DETAILS_JSON" 2>/dev/null || true)"
if [[ "$TUNNEL_STATE" != "connected" || "$DDI_AVAILABLE" != "true" ]]; then
  echo "The paired iPhone is offline (tunnel=$TUNNEL_STATE, DDI=$DDI_AVAILABLE)." >&2
  exit 68
fi

xcrun devicectl device info lockState \
  --device "$DEVICE_ID" \
  --timeout 30 \
  --json-output "$DEVICE_LOCK_JSON" >/dev/null
PASSCODE_REQUIRED="$(plutil -extract result.passcodeRequired raw -o - "$DEVICE_LOCK_JSON" 2>/dev/null || true)"
if [[ "$PASSCODE_REQUIRED" == "true" ]]; then
  echo "The paired iPhone is locked. Unlock it and keep it foregrounded before starting the audit." >&2
  exit 68
fi

if [[ "$AUDIT_MODE" == "development-gc" ]]; then
  echo "Starting the 5-minute Development Player GC audit."
  echo "Exercise freewheel, high-speed ratchet, model switching, explode/restore and mixed interaction throughout the run."
else
  echo "Starting the 30-minute read-only Release performance audit."
  echo "Operate the real product in four phases: 10m freewheel, 10m high-speed ratchet, 5m switch/explode, 5m mixed."
fi
echo "Keep the app foregrounded. Do not charge the phone during the measured run."
echo "Console evidence: $CONSOLE_LOG"

set +e
xcrun devicectl device process launch \
  --device "$DEVICE_ID" \
  --environment-variables "$AUDIT_ENVIRONMENT" \
  --terminate-existing \
  --console \
  --timeout "$AUDIT_TIMEOUT" \
  "$BUNDLE_ID" \
  "$AUDIT_ARGUMENT" 2>&1 | tee "$CONSOLE_LOG"
LAUNCH_RESULT=${pipestatus[1]}
set -e

SUMMARY_LINE="$(rg 'FIDGET_PERF_SUMMARY ' "$CONSOLE_LOG" | tail -1 || true)"
if [[ -z "$SUMMARY_LINE" ]]; then
  echo "The audit ended without a FIDGET_PERF_SUMMARY record." >&2
  exit 71
fi

print -r -- "$SUMMARY_LINE"
if [[ "$SUMMARY_LINE" != *'"reason":"completed"'* ]]; then
  echo "The app did not remain foregrounded for the complete measured duration." >&2
  exit 72
fi
if [[ "$SUMMARY_LINE" != *'"passed":true'* ]]; then
  echo "The telemetry completed, but one or more required gates failed." >&2
  exit 73
fi
if [[ "$AUDIT_MODE" == "development-gc" ]]; then
  if [[ "$SUMMARY_LINE" != *'"mode":"developmentGc"'* ||
        "$SUMMARY_LINE" != *'"developmentBuild":true'* ||
        "$SUMMARY_LINE" != *'"gcCounterAvailable":true'* ||
        "$SUMMARY_LINE" != *'"gcPassed":true'* ]]; then
    echo "The five-minute run did not prove zero-allocation Development Player GC behavior." >&2
    exit 74
  fi
elif [[ "$SUMMARY_LINE" != *'"mode":"release"'* ||
        "$SUMMARY_LINE" != *'"developmentBuild":false'* ||
        "$SUMMARY_LINE" != *'"environmentPassed":true'* ]]; then
  echo "The 30-minute Release audit used the wrong player/mode or failed the measured battery/brightness gate." >&2
  exit 74
fi
if (( LAUNCH_RESULT != 0 )); then
  echo "devicectl exited with status $LAUNCH_RESULT after the summary was captured." >&2
fi

SUMMARY_PAYLOAD="${SUMMARY_LINE#*FIDGET_PERF_SUMMARY }"
SUMMARY_PAYLOAD="${SUMMARY_PAYLOAD%$'\r'}"
print -r -- "$SUMMARY_PAYLOAD" > "$SUMMARY_JSON"
if ! plutil -lint "$SUMMARY_JSON" >/dev/null; then
  echo "The captured summary is not valid JSON." >&2
  exit 75
fi

DEVICE_MODEL="$(plutil -extract result.hardwareProperties.marketingName raw -o - "$DEVICE_DETAILS_JSON" 2>/dev/null || true)"
DEVICE_OS="$(plutil -extract result.deviceProperties.osVersionNumber raw -o - "$DEVICE_DETAILS_JSON" 2>/dev/null || true)"
{
  print -r -- "# iPhone ${AUDIT_MODE}审计 — $(date '+%Y-%m-%d %H:%M:%S %Z')"
  print -r -- ""
  print -r -- "机器遥测结论：通过。完整发布结论仍须结合Metal HUD、Power Profiler和人工触感/音频观察。"
  print -r -- ""
  print -r -- "- 模式：${AUDIT_MODE}"
  print -r -- "- 设备：${DEVICE_MODEL}"
  print -r -- "- iOS：${DEVICE_OS}"
  print -r -- "- 环境温度：${ENVIRONMENT_C} °C"
  print -r -- "- 声明屏幕亮度：${BRIGHTNESS_PERCENT}%"
  print -r -- "- 声明供电状态：${POWER_STATE}"
  print -r -- "- 原始控制台：device-console.log"
  print -r -- "- 结构化汇总：summary.json"
  print -r -- ""
  print -r -- "## 机器汇总"
  print -r -- ""
  print -r -- '```json'
  print -r -- "$SUMMARY_PAYLOAD"
  print -r -- '```'
  print -r -- ""
  print -r -- "## 仍需人工/外部工具填写"
  print -r -- ""
  print -r -- "- Metal allocated peak：待填"
  print -r -- "- Metal HUD最差片段：待填"
  print -r -- "- Power Profiler/Energy：待填"
  print -r -- "- 亮度突降、音频断裂、Haptic生命周期异常：待填"
  print -r -- "- Jetsam / Memory Warning / EXC_RESOURCE：待填"
} > "$REPORT_PATH"

echo "Audit evidence captured at $CONSOLE_LOG"
echo "Structured summary: $SUMMARY_JSON"
echo "Report template: $REPORT_PATH"
