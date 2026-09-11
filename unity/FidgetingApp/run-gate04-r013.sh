#!/bin/bash
set -u

PROJECT="/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp"
UNITY="/Applications/Unity/Hub/Editor/6000.5.6f1/Unity.app/Contents/MacOS/Unity"
LOCK="$PROJECT/.gate04r013.lock"
SUFFIX="${1:?usage: run-gate04-r013.sh <suffix> <build|tests|capture>}"
MODE="${2:?usage: run-gate04-r013.sh <suffix> <build|tests|capture>}"

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
  build)
    LOG="$PROJECT/Logs/PackOpeningGate04R013Build-$SUFFIX.log"
    "$UNITY" -batchmode -nographics -quit -projectPath "$PROJECT" \
      -executeMethod FidgetingApp.DisplayCase.Candidates.Editor.PackOpeningGate04R013Builder.BuildSceneOnly \
      -logFile "$LOG"
    code=$?
    ;;
  tests)
    BUILD_LOG="$PROJECT/Logs/PackOpeningGate04R013Build-$SUFFIX.log"
    "$UNITY" -batchmode -nographics -quit -projectPath "$PROJECT" \
      -executeMethod FidgetingApp.DisplayCase.Candidates.Editor.PackOpeningGate04R013Builder.BuildSceneOnly \
      -logFile "$BUILD_LOG"
    build_code=$?
    if [ "$build_code" -ne 0 ]; then
      echo "UNITY_BUILD_EXIT=$build_code"
      exit "$build_code"
    fi
    LOG="$PROJECT/Logs/PackOpeningGate04R013Tests-$SUFFIX.log"
    "$UNITY" -batchmode -nographics -projectPath "$PROJECT" \
      -runTests -testPlatform EditMode \
      -testFilter "FidgetingApp.DisplayCase.Candidates.Tests.PackOpeningGate04R013Tests" \
      -testResults "$PROJECT/Logs/PackOpeningGate04R013Results-$SUFFIX.xml" \
      -logFile "$LOG"
    code=$?
    ;;
  capture)
    LOG="$PROJECT/Logs/PackOpeningGate04R013Capture-$SUFFIX.log"
    "$UNITY" -batchmode -projectPath "$PROJECT" \
      -executeMethod FidgetingApp.DisplayCase.Candidates.Editor.PackOpeningGate04R013Builder.BuildAndRunCapture \
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
exit "$code"
