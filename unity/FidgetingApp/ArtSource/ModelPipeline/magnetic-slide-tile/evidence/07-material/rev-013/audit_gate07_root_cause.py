#!/usr/bin/env python3
"""Prove where Gate 07 face-material partitions were lost."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
MODEL_ROOT = HERE.parent.parent.parent
REPO_ROOT = MODEL_ROOT.parents[4]
BLENDER = Path("/Applications/Blender.app/Contents/MacOS/Blender")
GATE07_BLEND = HERE.parent / "rev-012/magnetic-slide-tile-material-r012.blend"
GATE08_BLEND = MODEL_ROOT / "evidence/08-lighting/rev-005/magnetic-slide-tile-lighting-r005.blend"
GATE08_BUILDER = MODEL_ROOT / "evidence/08-lighting/rev-005/build_gate08_endpoint_lighting.py"
REPORT = HERE / "root-cause-report.json"
PRODUCT = ("BottomExterior", "MovingTopBody")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def inspect_blend(path: Path) -> dict:
    expression = """
import bpy,json
names=("BottomExterior","MovingTopBody")
out={}
for name in names:
    obj=bpy.data.objects[name]
    out[name]={
        "polygonCount":len(obj.data.polygons),
        "slotNames":[material.name for material in obj.data.materials],
        "materialIndexCounts":{
            str(index):sum(1 for polygon in obj.data.polygons if polygon.material_index==index)
            for index in range(len(obj.data.materials))
        },
        "materialNameCounts":{
            material.name:sum(1 for polygon in obj.data.polygons if polygon.material_index==index)
            for index,material in enumerate(obj.data.materials)
        },
    }
print("MATERIAL_AUDIT="+json.dumps(out,sort_keys=True))
""".strip()
    completed = subprocess.run(
        [
            str(BLENDER),
            "--background",
            str(path),
            "--python-expr",
            expression,
        ],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    line = next(
        value
        for value in completed.stdout.splitlines()
        if value.startswith("MATERIAL_AUDIT=")
    )
    return json.loads(line.split("=", 1)[1])


def find_function_lines(source: list[str], function_name: str) -> tuple[int, int]:
    start = next(
        index
        for index, line in enumerate(source)
        if line.startswith(f"def {function_name}(")
    )
    end = next(
        index
        for index in range(start + 1, len(source))
        if source[index].startswith("def ")
    )
    return start + 1, end


def main() -> None:
    gate07 = inspect_blend(GATE07_BLEND)
    gate08 = inspect_blend(GATE08_BLEND)
    source_lines = GATE08_BUILDER.read_text(encoding="utf-8").splitlines()
    start, end = find_function_lines(source_lines, "render_roughness")
    roughness_source = source_lines[start - 1:end]
    destructive_lines = [
        start + index
        for index, line in enumerate(roughness_source)
        if ".data.materials.clear()" in line
    ]
    index_restore_lines = [
        start + index
        for index, line in enumerate(roughness_source)
        if "material_index" in line
    ]
    before_partitioned = all(
        len([
            count
            for count in gate07[name]["materialIndexCounts"].values()
            if count > 0
        ]) == 4
        for name in PRODUCT
    )
    after_all_zero = all(
        gate08[name]["materialIndexCounts"].get("0") == gate08[name]["polygonCount"]
        and all(
            count == 0
            for index, count in gate08[name]["materialIndexCounts"].items()
            if index != "0"
        )
        for name in PRODUCT
    )
    same_slots = all(
        [
            value.replace("M07R12_", "")
            for value in gate07[name]["slotNames"]
        ] == [
            value.replace("M07R12_", "")
            for value in gate08[name]["slotNames"]
        ]
        for name in PRODUCT
    )
    checks = {
        "gate07SourceHadFourLivePartitions": before_partitioned,
        "gate08SavedBlendCollapsedEveryFaceToSlotZero": after_all_zero,
        "materialSlotsWereReattachedButFaceIndicesWereNot": same_slots,
        "roughnessPassClearsMaterialSlots": len(destructive_lines) == 2,
        "roughnessPassDoesNotRestorePolygonMaterialIndices": not index_restore_lines,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "07-material",
        "revision": 13,
        "rootCause": {
            "category": "Blender per-polygon material-index mutation",
            "exact": (
                "Gate 07 rev 12 stored correct face assignments. Gate 08 rev 5 "
                "render_roughness() cleared each product mesh's material slots. "
                "Blender reset every polygon.material_index to 0. The function "
                "reattached the four materials but never restored the saved face "
                "indices, then saved the lighting Blend. Slot 0 was the upper or "
                "lower artwork material, so cap, side, rim, and underside all "
                "sampled artwork in the later turntable."
            ),
            "sourcePath": str(GATE08_BUILDER.relative_to(REPO_ROOT)),
            "function": "render_roughness",
            "lineRange": [start, end],
            "destructiveClearLines": destructive_lines,
            "polygonIndexRestoreLines": index_restore_lines,
            "notUvRootCause": (
                "Gate 07 side faces had the solid dark slot before the destructive "
                "pass. UVs became visible only after those faces were reassigned "
                "to artwork slot 0."
            ),
            "notExporterRootCause": (
                "The corrupt Gate 08 Blend already had all faces on slot 0 before "
                "any later review render. GLB/FBX transport can preserve the new "
                "rev 13 partition and is audited independently."
            ),
        },
        "historicalEvidence": {
            "gate07Blend": {
                "path": str(GATE07_BLEND.relative_to(REPO_ROOT)),
                "sha256": sha256(GATE07_BLEND),
                "objects": gate07,
            },
            "gate08Blend": {
                "path": str(GATE08_BLEND.relative_to(REPO_ROOT)),
                "sha256": sha256(GATE08_BLEND),
                "objects": gate08,
            },
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps({
        "pass": report["pass"],
        "rootCause": report["rootCause"]["category"],
        "destructiveClearLines": destructive_lines,
        "gate08SlotZeroFaces": {
            name: gate08[name]["materialIndexCounts"]["0"]
            for name in PRODUCT
        },
    }, indent=2))


if __name__ == "__main__":
    main()
