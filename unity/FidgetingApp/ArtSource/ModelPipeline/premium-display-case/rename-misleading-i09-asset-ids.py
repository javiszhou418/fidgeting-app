#!/usr/bin/env python3
"""Rename two Gate 04 asset ids that claim iteration 09 but point elsewhere.

`premium-display-case-gate04-r011-i09-self-rejection` points at
iteration-08/self-rejection.json and `...-i09-EVIDENCE-LOSS` points at
iteration-02/EVIDENCE-LOSS.json. Paths and hashes are correct; only the ids
mislead. Renaming keeps the ids honest about which iteration they describe.
"""

import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
PIPELINE = ROOT / "pipeline.json"
HISTORY = ROOT / "history.ndjson"

RENAMES = {
    "premium-display-case-gate04-r011-i09-self-rejection":
        "premium-display-case-gate04-r011-iteration08-self-rejection",
    "premium-display-case-gate04-r011-i09-EVIDENCE-LOSS":
        "premium-display-case-gate04-r011-iteration02-evidence-loss",
}

EXPECTED_PATH_FRAGMENT = {
    "premium-display-case-gate04-r011-iteration08-self-rejection":
        "iterations/iteration-08/self-rejection.json",
    "premium-display-case-gate04-r011-iteration02-evidence-loss":
        "iterations/iteration-02/EVIDENCE-LOSS.json",
}


def rename_in(value):
    """Recursively rewrite any renamed id found in strings or containers."""
    if isinstance(value, str):
        return RENAMES.get(value, value)
    if isinstance(value, list):
        return [rename_in(item) for item in value]
    if isinstance(value, dict):
        return {key: rename_in(item) for key, item in value.items()}
    return value


pipeline = json.loads(PIPELINE.read_text())

present = {a["id"] for a in pipeline["assets"]}
missing = [old for old in RENAMES if old not in present]
if missing:
    raise SystemExit(f"Nothing to rename; ids absent: {missing}")
collisions = [new for new in RENAMES.values() if new in present]
if collisions:
    raise SystemExit(f"Target ids already exist: {collisions}")

pipeline = rename_in(pipeline)

for asset in pipeline["assets"]:
    fragment = EXPECTED_PATH_FRAGMENT.get(asset["id"])
    if fragment and not asset["path"].endswith(fragment):
        raise SystemExit(
            f"{asset['id']} does not point at {fragment}: {asset['path']}")

PIPELINE.write_text(json.dumps(pipeline, indent=2, ensure_ascii=False) + "\n")

# History is append-only, so past events keep their original wording. Only the
# live manifest is renamed; the rename itself is recorded as a new event by the
# caller.
lines = HISTORY.read_text().splitlines()
print(f"renamed {len(RENAMES)} asset ids in pipeline.json")
print(f"history left untouched at {len(lines)} records (append-only)")
for old, new in RENAMES.items():
    print(f"  {old}\n    -> {new}")
