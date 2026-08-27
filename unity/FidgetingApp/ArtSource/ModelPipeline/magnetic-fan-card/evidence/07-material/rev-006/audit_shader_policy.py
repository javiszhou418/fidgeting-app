"""Verify the Unity satin shader no longer paints object-space light bands."""

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
SHADER = (
    REPO / "unity/FidgetingApp/Assets/_FanCard/Shaders/"
    "FanCardSatinSilver.shader"
)


def main() -> None:
    source = SHADER.read_text(encoding="utf-8")
    checks = {
        "noSoftPanel": "softPanel" not in source,
        "noReflectedBand": "reflectedBand" not in source,
        "usesMainLight": "GetMainLight" in source,
        "usesSphericalHarmonics": "SampleSH" in source,
        "usesRoughness": "roughness" in source,
        "usesFresnel": "fresnel" in source,
    }
    report = {
        "shader": str(SHADER.relative_to(REPO)),
        "policy": "actual main light + spherical harmonics + rough specular",
        "checks": checks,
        "pass": all(checks.values()),
    }
    (HERE / "shader-policy-report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
