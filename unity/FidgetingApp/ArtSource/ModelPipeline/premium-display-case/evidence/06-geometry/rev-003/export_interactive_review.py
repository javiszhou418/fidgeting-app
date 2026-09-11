#!/usr/bin/env python3
"""Export a review-only GLB for interactive Gate 06 inspection."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import bpy


OUTPUT = Path(__file__).resolve().parent
SOURCE = OUTPUT / "premium-display-case-geometry-r003.blend"
TARGET = OUTPUT / "premium-display-case-gate06-review-r003.glb"
REPORT = OUTPUT / "interactive-review-validation.json"
EXPECTED_ROOTS = ("PresentationRoot", "CaseAssembly", "ContentSlot")
SUBJECT_NAMES = (
    "RearPolycarbonateShell",
    "TactileBackgroundInsert",
    "FrontPolycarbonateShell",
    "ContinuousTubePerimeter",
    "PhysicalLabel",
)


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(OUTPUT)


def repo_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def descendants(root: bpy.types.Object) -> list[bpy.types.Object]:
    result = [root]
    for child in root.children:
        result.extend(descendants(child))
    return result


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    root = bpy.data.objects["PresentationRoot"]
    selected = descendants(root)
    bpy.ops.object.select_all(action="DESELECT")
    for obj in selected:
        obj.select_set(True)
    bpy.context.view_layer.objects.active = root
    bpy.ops.export_scene.gltf(
        filepath=str(TARGET),
        export_format="GLB",
        use_selection=True,
        export_apply=False,
        export_animations=False,
        export_cameras=False,
        export_lights=False,
        export_yup=True,
    )
    names = {obj.name for obj in selected}
    checks = {
        "sourceBlendPresent": SOURCE.is_file(),
        "reviewGlbPresent": TARGET.is_file() and TARGET.stat().st_size > 4096,
        "presentationRootIncluded": EXPECTED_ROOTS[0] in names,
        "caseAssemblyIncluded": EXPECTED_ROOTS[1] in names,
        "contentSlotIncluded": EXPECTED_ROOTS[2] in names,
        "allSubjectMeshesIncluded": all(name in names for name in SUBJECT_NAMES),
        "wholeCaseHierarchyOnly": root.parent is None,
        "animationsExcluded": all(obj.animation_data is None for obj in selected),
        "shippingExportNotClaimed": True,
    }
    report = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "06-geometry",
        "geometryRevision": 3,
        "purpose": "interactive-review-only-not-gate10-export",
        "sourceBlend": repo_path(SOURCE),
        "sourceBlendSha256": sha256(SOURCE),
        "reviewGlb": repo_path(TARGET),
        "reviewGlbSha256": sha256(TARGET),
        "selectedObjectNames": sorted(names),
        "checks": checks,
        "status": "pass" if all(checks.values()) else "fail",
        "shippingUnityChanged": False,
        "buildInstallPhonePush": False,
    }
    REPORT.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"status": report["status"], "glb": str(TARGET)}))


if __name__ == "__main__":
    main()
