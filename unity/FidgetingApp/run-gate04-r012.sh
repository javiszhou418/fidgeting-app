#!/bin/bash
set -u

PROJECT="/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp"
UNITY="/Applications/Unity/Hub/Editor/6000.5.6f1/Unity.app/Contents/MacOS/Unity"
LOCK="$PROJECT/.gate04r012.lock"
SUFFIX="${1:?usage: run-gate04-r012.sh <suffix> <tests|capture>}"
MODE="${2:?usage: run-gate04-r012.sh <suffix> <tests|capture>}"

cd "$PROJECT" || exit 1

if [ -e "$LOCK" ]; then
  holder=$(<"$LOCK")
  if kill -0 "$holder" 2>/dev/null; then
    echo "LOCK_HELD by pid $holder"
    exit 3
  fi
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
    LOG="$PROJECT/Logs/PackOpeningGate04R012Tests-$SUFFIX.log"
    "$UNITY" -batchmode -projectPath "$PROJECT" \
      -runTests -testPlatform EditMode \
      -testFilter "FidgetingApp.DisplayCase.Candidates.Tests.PackOpeningGate04R012Tests" \
      -testResults "$PROJECT/Logs/PackOpeningGate04R012Results-$SUFFIX.xml" \
      -logFile "$LOG" -nographics
    code=$?
    ;;
  capture)
    LOG="$PROJECT/Logs/PackOpeningGate04R012Capture-$SUFFIX.log"
    "$UNITY" -batchmode -projectPath "$PROJECT" \
      -executeMethod FidgetingApp.DisplayCase.Candidates.Editor.PackOpeningGate04R012Builder.BuildAndRunCapture \
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
