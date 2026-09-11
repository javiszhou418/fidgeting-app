#!/bin/bash
# Serialize Gate 04 rev 11 Unity batch runs. Two agents sharing this project can
# otherwise corrupt Library/ and produce empty or duplicated build state.
set -u

PROJECT="/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp"
UNITY="/Applications/Unity/Hub/Editor/6000.5.6f1/Unity.app/Contents/MacOS/Unity"
LOCK="$PROJECT/.gate04r011.lock"
SUFFIX="${1:?usage: run-gate04-r011.sh <suffix> <tests|capture>}"
MODE="${2:?usage: run-gate04-r011.sh <suffix> <tests|capture>}"

cd "$PROJECT" || exit 1

if [ -e "$LOCK" ]; then
  holder=$(cat "$LOCK" 2>/dev/null)
  if kill -0 "$holder" 2>/dev/null; then
    echo "LOCK_HELD by pid $holder"
    exit 3
  fi
  echo "clearing stale lock from pid $holder"
  rm -f "$LOCK"
fi

if pgrep -f "Unity.app/Contents/MacOS/Unity" >/dev/null; then
  echo "UNITY_ALREADY_RUNNING"
  exit 3
fi

echo $$ >"$LOCK"
trap 'rm -f "$LOCK"' EXIT

case "$MODE" in
  tests)
    LOG="$PROJECT/Logs/PackOpeningGate04R011Tests-$SUFFIX.log"
    "$UNITY" -batchmode -projectPath "$PROJECT" \
      -runTests -testPlatform EditMode \
      -testFilter "FidgetingApp.DisplayCase.Candidates.Tests.PackOpeningGate04R011Tests" \
      -testResults "$PROJECT/Logs/PackOpeningGate04R011Results-$SUFFIX.xml" \
      -logFile "$LOG" -nographics
    code=$?
    ;;
  capture)
    LOG="$PROJECT/Logs/PackOpeningGate04R011Capture-$SUFFIX.log"
    "$UNITY" -batchmode -projectPath "$PROJECT" \
      -executeMethod FidgetingApp.DisplayCase.Candidates.Editor.PackOpeningGate04R011Builder.BuildAndRunCapture \
      -logFile "$LOG"
    code=$?
    ;;
  *)
    echo "unknown mode $MODE"
    exit 2
    ;;
esac

echo "UNITY_EXIT=$code"
echo "LOG=$LOG"
exit $code
