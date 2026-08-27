#!/usr/bin/env python3
"""Install a non-destructive symlink from the personal Codex skill directory to this repo skill."""

from pathlib import Path
import sys

source = Path(__file__).resolve().parents[1]
target = Path.home() / ".codex" / "skills" / source.name
target.parent.mkdir(parents=True, exist_ok=True)
if target.exists() or target.is_symlink():
    if target.is_symlink() and target.resolve() == source:
        print(target)
        raise SystemExit(0)
    print(f"Refusing to replace existing path: {target}", file=sys.stderr)
    raise SystemExit(1)
target.symlink_to(source, target_is_directory=True)
print(target)
