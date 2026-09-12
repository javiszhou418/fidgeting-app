#!/bin/zsh
set -eu
REAL=/Applications/Xcode.app/Contents/Developer/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang
probe=false
has_e=false
has_dm=false
for argument in "$@"; do
  [[ "$argument" == "-E" ]] && has_e=true
  [[ "$argument" == "-dM" ]] && has_dm=true
done
[[ "$has_e" == true && "$has_dm" == true ]] && probe=true
if [[ "$probe" == true ]]; then
  typeset -a filtered
  for argument in "$@"; do
    [[ "$argument" == "-v" ]] || filtered+=("$argument")
  done
  exec "$REAL" "${filtered[@]}"
fi
exec "$REAL" "$@"
