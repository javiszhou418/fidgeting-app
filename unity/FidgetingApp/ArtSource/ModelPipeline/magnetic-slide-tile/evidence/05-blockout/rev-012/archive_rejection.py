#!/usr/bin/env python3
"""Archive the user's Gate 08 Unity-only geometry rejection."""

import hashlib
import json
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCES = [
    Path("/Users/jiawei.zhou/.cursor/projects/Users-jiawei-zhou-Documents-Fidgeting-app/assets/image-e6b20dea-b1b3-4176-a4c2-d0e0ac426f40.jpg"),
    Path("/Users/jiawei.zhou/.cursor/projects/Users-jiawei-zhou-Documents-Fidgeting-app/assets/image-f2b1eb0c-5f24-42a4-a742-d182a5c61bb5.png"),
]
OUTPUTS = [HERE / "user-rejection-axis-intent.jpg", HERE / "user-rejection-penetration-proxy.png"]


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


for source, output in zip(SOURCES, OUTPUTS):
    shutil.copyfile(source, output)

report = {
    "schemaVersion": 1,
    "gate": "05-blockout",
    "revision": 12,
    "decision": "reject",
    "sourceReview": "Gate 08 rev 4 Unity-only PlayMode preview",
    "files": [
        {"path": output.name, "sha256": sha256(output), "bytes": output.stat().st_size, "sourcePath": str(source)}
        for source, output in zip(SOURCES, OUTPUTS)
    ],
    "userConfirmedFailures": [
        {
            "id": "axis-drift-jump",
            "severity": "blocker",
            "decision": "Exactly one physical fixed axis exists at one BottomBase endpoint and never changes world position.",
        },
        {
            "id": "hidden-mechanism-penetration",
            "severity": "blocker",
            "decision": "Carrier, followers, balls and rails may not protrude through the shell in any legal pose.",
        },
        {
            "id": "spurious-visible-plate",
            "severity": "blocker",
            "decision": "MinimumOverlapDisk is non-rendering metadata; BottomExterior remains a clean plane and TopPlate covers the axis region.",
        },
    ],
    "earliestAffectedGate": "05-blockout",
    "reason": "The approved mechanical intent already required one fixed axis and concealed internals. Gate 05 encoded ambiguous pivot ownership and product visibility; later gates propagated it.",
    "scope": {"build": False, "install": False, "phone": False},
}
(HERE / "user-rejection-evidence.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
print(json.dumps(report, indent=2))

