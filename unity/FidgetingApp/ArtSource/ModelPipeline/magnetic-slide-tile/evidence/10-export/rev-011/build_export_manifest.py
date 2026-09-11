#!/usr/bin/env python3
"""Build the immutable Gate 10 rev 11 export manifest."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
PACKAGE = HERE / "package"
MANIFEST = PACKAGE / "export-manifest-r011.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    reports = {
        name: json.loads((HERE / filename).read_text())
        for name, filename in {
            "portableGlbBuild": "portable-glb-build-validation.json",
            "rawGlbAudit": "corrected-glb-audit.json",
            "controlledBlenderComparison": "controlled-blender-comparison-validation.json",
            "visualMetrics": "visual-metrics-validation.json",
            "threeViewer": "threejs-viewer-audit.json",
        }.items()
    }
    if not all(report["pass"] for report in reports.values()):
        raise RuntimeError("Gate 10 rev 11 reports must pass before manifest creation.")
    files = []
    for path in sorted(PACKAGE.rglob("*")):
        if not path.is_file() or path == MANIFEST:
            continue
        files.append({
            "path": str(path.relative_to(PACKAGE)),
            "sha256": sha256(path),
            "sizeBytes": path.stat().st_size,
        })
    build = reports["portableGlbBuild"]
    raw = reports["rawGlbAudit"]
    controlled = reports["controlledBlenderComparison"]
    visual = reports["visualMetrics"]
    viewer = reports["threeViewer"]
    manifest = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 11,
        "status": "validation-pending-registration",
        "rejectedRevision": {
            "revision": 10,
            "glbSha256": build["sourceRejectedGlb"]["sha256"],
            "exactUserWording": "almost entirely white/washed out",
            "evidencePath": "../user-rejection-washed-out-r010.jpg",
            "evidenceSha256": sha256(HERE / "user-rejection-washed-out-r010.jpg"),
            "preservedImmutable": True,
        },
        "rootCause": build["diagnosis"],
        "correction": {
            "scope": "portable GLB PBR transport and neutral review calibration only",
            "authoritativeBlenderPreserved": True,
            "explicitTransportApproximation": True,
            "baseColor": "upper/lower 620x1000 sRGB; deep blood-red, black motif/perimeter",
            "metallicRoughness": "linear glTF data; roughness G; metallic factor 0.08 top",
            "normal": "linear tangent-space; scale 0.35",
            "topSpecularFactor": 0.55,
            "topClearcoat": [0.32, 0.10],
            "topTransmission": 0,
            "sidePbr": {"baseColor": [0.014, 0.016, 0.020, 1], "metallic": 0.20, "roughness": 0.30},
            "rimPbr": {"baseColor": [0.68, 0.66, 0.62, 1], "metallic": 1.0, "roughness": 0.16},
            "alphaMode": "OPAQUE",
            "emissiveFactor": [0, 0, 0],
            "viewer": {
                "environment": "environment/neutral-control-r009.exr",
                "toneMapping": "ACESFilmic",
                "exposure": 0.9,
                "environmentIntensity": 0.42,
                "directLights": {"hemisphere": 0.34, "key": 1.05, "fill": 0.28, "rim": 0.42},
            },
        },
        "preserved": {
            "geometryDigest": build["preserved"]["geometryDigest"],
            "materialStateDigest": build["preserved"]["materialStateDigest"],
            "uvDigest": build["preserved"]["uvDigest"],
            "geometryAccessorBytesMatchRejectedExport": raw["checks"]["geometryAccessorBytesUnchanged"],
            "materialAssignmentsMatchRejectedExport": raw["checks"]["meshMaterialAssignmentsUnchanged"],
            "hierarchyMatchRejectedExport": raw["checks"]["hierarchyUnchanged"],
            "endpointInterlock": raw["checks"]["endpointInterlock"],
            "closedZeroMotion": raw["checks"]["closedZeroMotion"],
        },
        "objectiveVisual": {
            "rejectedWhiteFraction": visual["rejected"]["clippedWhiteFraction"],
            "correctedGlbWhiteFraction": visual["reimport"]["clippedWhiteFraction"],
            "correctedTopRedFraction": visual["topCloseup"]["redFraction"],
            "correctedSideMedianLuminance": visual["sideCloseup"]["luminanceP05P50P95"][1],
            "correctedRimControlledHighlightFraction": visual["rimCloseup"]["controlledSilverFraction"],
            "sourceReimportMeanAbsoluteError": visual["sameCameraSimilarity"]["meanAbsoluteError"],
            "sameCamera": controlled["controlledSetup"]["camera"],
            "sameEnvironment": controlled["controlledSetup"],
            "viewerIndependent": {
                "pass": viewer["pass"],
                "redFraction": viewer["viewerMetrics"]["redFraction"],
                "whiteFraction": viewer["viewerMetrics"]["clippedWhiteFraction"],
                "calibration": viewer["calibration"],
            },
        },
        "validations": {
            name: {"pass": report["pass"], "checks": report.get("checks", {})}
            for name, report in reports.items()
        },
        "files": files,
        "scope": {
            "simulatorUsed": False,
            "unityImportApplied": False,
            "unitySceneModified": False,
            "buildRun": False,
            "installed": False,
            "deviceRun": False,
        },
    }
    MANIFEST.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    validation = {
        "schemaVersion": 1,
        "pass": True,
        "manifest": {"path": str(MANIFEST), "sha256": sha256(MANIFEST)},
        "packageFiles": len(files) + 1,
        "allReportsPass": True,
    }
    (HERE / "export-manifest-validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    main()
