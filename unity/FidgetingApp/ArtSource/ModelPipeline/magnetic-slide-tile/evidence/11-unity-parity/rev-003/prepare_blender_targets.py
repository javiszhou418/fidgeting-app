#!/usr/bin/env python3
"""Copy the unchanged approved Blender parity targets into immutable rev 3."""

from __future__ import annotations

import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REV2 = ROOT.parent / "rev-002"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    outputs = {}
    for name in ("blender-neutral.png", "blender-neutral-silhouette.png"):
        source = REV2 / name
        target = ROOT / name
        shutil.copy2(source, target)
        outputs[name] = {
            "source": str(source.relative_to(ROOT.parents[7])),
            "sha256": sha256(target),
            "bytes": target.stat().st_size,
        }
    report = {
        "schemaVersion": 1,
        "gate": "11-unity-parity",
        "revision": 3,
        "materialTarget": "approved Gate 07 rev 7 Blender material",
        "geometryTarget": "approved Gate 10 rev 3 export geometry",
        "cameraTarget": "unchanged Gate 11 rev 2 camera",
        "sourceChanged": False,
        "outputs": outputs,
        "pass": True,
    }
    (ROOT / "blender-target-report.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
