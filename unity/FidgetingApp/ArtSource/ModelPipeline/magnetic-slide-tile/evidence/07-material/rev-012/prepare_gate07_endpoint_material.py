#!/usr/bin/env python3
"""Reuse approved Gate 07 textures and derive the endpoint-safe builder."""

import hashlib
import json
import shutil
from pathlib import Path


HERE = Path(__file__).resolve().parent
REV11 = HERE.parent / "rev-011"
REV7 = HERE.parent / "rev-007"
REV10 = HERE.parent / "rev-010"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


for name in ("upper-albedo.png", "upper-roughness.png", "lower-albedo.png", "lower-roughness.png"):
    shutil.copyfile(REV11 / name, HERE / name)

lineage = json.loads((REV11 / "texture-lineage.json").read_text(encoding="utf-8"))
lineage["revision"] = 12
lineage["reusedApprovedRevision"] = 11
lineage["governingContractSha256"] = "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571"
lineage["geometryDigest"] = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952"
lineage["appearanceChanged"] = False
lineage["motionEvidenceChanged"] = True
for slot in ("upper", "lower"):
    for key in ("albedo", "roughness"):
        filename = lineage["outputs"][slot][key]
        lineage["outputs"][slot][f"{key}Sha256"] = sha256(HERE / filename)
lineage["pass"] = all([
    lineage["sourceMasks"]["upper"]["sha256"] == sha256(REV7 / "artwork-upper-mask.png"),
    lineage["sourceMasks"]["lower"]["sha256"] == sha256(REV10 / "artwork-lower-mask-r010.png"),
    lineage["sourceMasks"]["border"]["sha256"] == sha256(REV7 / "artwork-top-perimeter-border-mask.png"),
    lineage["outputs"]["upper"]["albedoSha256"] == sha256(REV11 / "upper-albedo.png"),
    lineage["outputs"]["lower"]["albedoSha256"] == sha256(REV11 / "lower-albedo.png"),
])
(HERE / "texture-lineage.json").write_text(json.dumps(lineage, indent=2), encoding="utf-8")

source = (REV11 / "build_gate07_material.py").read_text(encoding="utf-8")
replacements = {
    'rev-004/magnetic-slide-tile-geometry-r004.blend': 'rev-005/magnetic-slide-tile-geometry-r005.blend',
    'rev-016/mechanism-evidence-contract.json': 'rev-017/mechanism-evidence-contract.json',
    'magnetic-slide-tile-material-r011.blend': 'magnetic-slide-tile-material-r012.blend',
    'magnetic-slide-tile-material-r011-lookdev.glb': 'magnetic-slide-tile-material-r012-lookdev.glb',
    '8047be52ce635d9bd18d5f2be3c3e223ac04c3101aec10221849d97b6e867085': 'a2aaf83a8e46b013f0ba2e2d859732f20f29bd8cc1dd032e155269cb19ce0ef4',
    '5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea': '9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571',
    'e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe': '2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952',
    '"FixedAxisBoss"': '"InternalAxisBoss"',
    '"MagneticSlideTile_G05_R006"': '"MagneticSlideTile_G06_R005"',
    'M07R11_': 'M07R12_',
    'material_revision"] = 11': 'material_revision"] = 12',
    'mat["gate07_revision"] = 11': 'mat["gate07_revision"] = 12',
    '"revision": 11': '"revision": 12',
}
for old, new in replacements.items():
    source = source.replace(old, new)

old_digest = '''def geometry_digest():
    depsgraph = bpy.context.evaluated_depsgraph_get()
    digest = hashlib.sha256()
    for name in CORE:
        obj = bpy.data.objects[name]
        evaluated = obj.evaluated_get(depsgraph)
        mesh = evaluated.to_mesh()
        digest.update(name.encode())
        for vertex in mesh.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
            digest.update(b";")
        for polygon in mesh.polygons:
            digest.update(",".join(str(index) for index in polygon.vertices).encode())
            digest.update(b";")
        evaluated.to_mesh_clear()
    return digest.hexdigest()
'''
new_digest = '''def geometry_digest():
    digest = hashlib.sha256()
    for name in sorted(CORE):
        obj = bpy.data.objects[name]
        digest.update(name.encode())
        for vertex in obj.data.vertices:
            digest.update(",".join(f"{value:.9f}" for value in vertex.co).encode())
        for polygon in obj.data.polygons:
            digest.update(",".join(str(index) for index in polygon.vertices).encode())
    return digest.hexdigest()
'''
if old_digest not in source:
    raise RuntimeError("Could not locate legacy geometry digest.")
source = source.replace(old_digest, new_digest)

old_pose = '''def set_pose(travel, angle, lift=0.0):
    bpy.data.objects["RotatingCarrier"].rotation_euler = (0, 0, math.radians(angle))
    bpy.data.objects["MovingTop"].rotation_euler = (0, 0, math.radians(angle))
    bpy.data.objects["TopLocalSlide"].location = (0, -travel, lift)
    bpy.context.view_layer.update()
'''
new_pose = '''MAX_TRAVEL = 18.076433121019107
PIVOT = Vector((0.0, -9.0, 5.875))
ALIGNMENT_TOLERANCE_DEG = 0.001
ENDPOINT_TOLERANCE_MM = 1e-6


def set_pose(travel, angle, lift=0.0):
    normalized = angle % 360.0
    if min(normalized, 360.0 - normalized) <= ALIGNMENT_TOLERANCE_DEG:
        normalized = 0.0
    if travel < MAX_TRAVEL - ENDPOINT_TOLERANCE_MM and normalized != 0.0:
        raise RuntimeError(f"Illegal endpoint-interlock pose: s={travel}, theta={normalized}")
    moving = bpy.data.objects["MovingTop"]
    slide = bpy.data.objects["TopLocalSlide"]
    carrier = bpy.data.objects["RotatingCarrier"]
    moving.location = PIVOT
    moving.rotation_mode = "XYZ"
    moving.rotation_euler = (0.0, 0.0, math.radians(normalized))
    slide.location = (0.0, 9.0 - travel, lift)
    carrier.location = (0.0, 0.0, -0.48)
    carrier.rotation_mode = "XYZ"
    carrier.rotation_euler = (0.0, 0.0, math.radians(normalized))
    bpy.context.view_layer.update()
'''
if old_pose not in source:
    raise RuntimeError("Could not locate legacy pose function.")
source = source.replace(old_pose, new_pose)
source = source.replace('set_pose(12.0, 12.0)', 'set_pose(MAX_TRAVEL, 12.0)')
source = source.replace('set_pose(7.0, angle)', 'set_pose(MAX_TRAVEL, angle)')
source = source.replace('set_pose(4.0, 12.0)', 'set_pose(MAX_TRAVEL, 12.0)')
source = source.replace('set_pose(9.0, 12.0, 10.0)', 'set_pose(MAX_TRAVEL, 12.0, 10.0)')
source = source.replace('set_pose(10.0, 12.0)', 'set_pose(MAX_TRAVEL, 12.0)')
source = source.replace('set_pose(7.0, 12.0)', 'set_pose(MAX_TRAVEL, 12.0)')
source = source.replace('"assembled-open.png"', '"max-open-12.png"')
source = source.replace('"open": geometry_digest()', '"max-open-12": geometry_digest()')
source = source.replace('pose_digests["open"]', 'pose_digests["max-open-12"]')
source = source.replace('f"crystal-angle-{angle:02d}.png"', 'f"max-open-{angle:02d}.png"')
source = source.replace('f"angle-{angle}"', 'f"max-open-{angle}"')
source = source.replace('"crystal-angle-00.png", "crystal-angle-12.png",\n                "crystal-angle-36.png"', '"max-open-00.png", "max-open-12.png",\n                "max-open-36.png"')
source = source.replace('set_pose(18.076433121019107, 0)', 'set_pose(MAX_TRAVEL, 0)')
source = source.replace('set_pose(5.0, 0, 15.0)', 'set_pose(MAX_TRAVEL * 0.5, 0, 15.0)')
source = source.replace('set_pose(0, 0)\n    after_digest', 'set_pose(MAX_TRAVEL, 0)\n    render(scene, cameras["open"], "max-open-0.png")\n    set_pose(MAX_TRAVEL * 0.5, 0)\n    render(scene, cameras["open"], "intermediate-slide-0.png")\n    set_pose(0, 0)\n    after_digest')
source = source.replace('"turntableFrames": 24,', '"turntableFrames": 24,\n            "endpointInterlock": True,')
source = source.replace('"oldShippingUntouched": scene["shipping_unity_changed"] is False,', '"oldShippingUntouched": scene["shipping_unity_changed"] is False,\n        "endpointOnlyRotation": all(key == "closed" or key.startswith("max-open") for key in pose_digests),\n        "midSlideRotationAbsent": "intermediate-slide-0.png" in [p.name for p in HERE.glob("*.png")],\n        "productRendererWhitelist": list(scene["product_renderer_whitelist"]) == ["BottomExterior", "MovingTopBody"],')
source = source.replace('scene["self_motion"] = False', 'scene["self_motion"] = False\n    scene["endpoint_interlock"] = "rotation-only-at-sMax; slide-return-only-at-0-or-360"\n    scene["product_renderer_whitelist"] = ["BottomExterior", "MovingTopBody"]')
(HERE / "build_gate07_endpoint_material.py").write_text(source, encoding="utf-8")

image_audit = (REV11 / "assemble_and_audit_gate07.py").read_text(encoding="utf-8")
for old, new in {
    "REV 11": "REV 12",
    '"revision": 11': '"revision": 12',
    "assembled-open.png": "max-open-12.png",
    "crystal-angle-00.png": "max-open-00.png",
    "crystal-angle-12.png": "max-open-12.png",
    "crystal-angle-36.png": "max-open-36.png",
    "Rev 11 corrected geometry": "Rev 12 endpoint-safe geometry",
}.items():
    image_audit = image_audit.replace(old, new)
image_audit = image_audit.replace(
    '"side-reflection.png",\n        "max-open-00.png"',
    '"side-reflection.png", "intermediate-slide-0.png", "max-open-0.png",\n        "max-open-00.png"',
)
(HERE / "assemble_and_audit_gate07.py").write_text(image_audit, encoding="utf-8")

blender_audit = (REV11 / "audit_gate07_material.py").read_text(encoding="utf-8")
for old, new in {
    "rev 11": "rev 12",
    "r011-lookdev.glb": "r012-lookdev.glb",
    "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe": "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952",
    "8047be52ce635d9bd18d5f2be3c3e223ac04c3101aec10221849d97b6e867085": "a2aaf83a8e46b013f0ba2e2d859732f20f29bd8cc1dd032e155269cb19ce0ef4",
    "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea": "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
    '"FixedAxisBoss"': '"InternalAxisBoss"',
    "M07R11_": "M07R12_",
    "== 11": "== 12",
    '"revision": 11': '"revision": 12',
}.items():
    blender_audit = blender_audit.replace(old, new)
if old_digest not in blender_audit:
    raise RuntimeError("Could not locate audit geometry digest.")
blender_audit = blender_audit.replace(old_digest, new_digest)
blender_audit = blender_audit.replace(
    '"oldShippingUntouched": scene.get("shipping_unity_changed") is False,',
    '"oldShippingUntouched": scene.get("shipping_unity_changed") is False,\n'
    '        "endpointInterlock": scene.get("endpoint_interlock") == "rotation-only-at-sMax; slide-return-only-at-0-or-360",\n'
    '        "productRendererWhitelist": list(scene.get("product_renderer_whitelist")) == ["BottomExterior", "MovingTopBody"],',
)
(HERE / "audit_gate07_endpoint_material.py").write_text(blender_audit, encoding="utf-8")

register = (REV11 / "register_gate07_review.mjs").read_text(encoding="utf-8")
for old, new in {
    "revision !== 178": "revision !== 227",
    '"那你继续呗"': '"继续，继续"',
    "Gate 06 rev 4 chat approval": "Gate 06 rev 5 chat approval",
    "revision !== 11": "revision !== 12",
    "Gate 07 rev 11": "Gate 07 rev 12",
    "r011": "r012",
    "rev 11": "rev 12",
    "rev-011": "rev-012",
    "prepare_gate07.mjs": "start_gate07_endpoint_material.mjs",
    "prepare_gate07_textures.py": "prepare_gate07_endpoint_material.py",
    "build_gate07_material.py": "build_gate07_endpoint_material.py",
    "audit_gate07_material.py": "audit_gate07_endpoint_material.py",
    "assembled-open.png": "max-open-12.png",
    "crystal-angle-00.png": "max-open-00.png",
    "crystal-angle-12.png": "max-open-12.png",
    "crystal-angle-36.png": "max-open-36.png",
    "slider-analysis-mechanism-evidence-contract-r016": "slider-analysis-mechanism-evidence-contract-r017",
    "magnetic-slide-tile-geometry-blend-r004": "magnetic-slide-tile-geometry-blend-r005",
    "magnetic-slide-tile-geometry-interactive-r004": "magnetic-slide-tile-geometry-interactive-r005",
    "Gate 06 rev 4": "Gate 06 rev 5",
    "那你继续呗": "继续，继续",
    "original-user-blood-red-product-imagery-only": "approved-rev11-source-faithful-materials",
}.items():
    register = register.replace(old, new)
register = register.replace(
    '["magnetic-slide-tile-material-audit-script-r012", "audit-script", local("audit_gate07_endpoint_material.py"), "process"],',
    '["magnetic-slide-tile-material-audit-script-r012", "audit-script", local("audit_gate07_endpoint_material.py"), "process"],\n'
    '  ["magnetic-slide-tile-material-motion-audit-script-r012", "motion-audit-script", local("audit_endpoint_material_motion.py"), "process"],\n'
    '  ["magnetic-slide-tile-material-motion-audit-r012", "motion-audit", local("endpoint-material-motion-audit.json"), "validation"],',
)
register = register.replace(
    '["magnetic-slide-tile-material-open-r012", "material-open-artwork", local("max-open-12.png"), "blender-render"],',
    '["magnetic-slide-tile-material-intermediate-r012", "material-intermediate", local("intermediate-slide-0.png"), "blender-render"],\n'
    '  ["magnetic-slide-tile-material-max-open-0-r012", "material-endpoint-0", local("max-open-0.png"), "blender-render"],\n'
    '  ["magnetic-slide-tile-material-open-r012", "material-open-artwork", local("max-open-12.png"), "blender-render"],',
)
register = register.replace(
    '"magnetic-slide-tile-material-open-r012",',
    '"magnetic-slide-tile-material-intermediate-r012",\n'
    '  "magnetic-slide-tile-material-max-open-0-r012",\n'
    '  "magnetic-slide-tile-material-open-r012",',
    1,
)
register = register.replace(
    'const audit = JSON.parse(fs.readFileSync(path.join(output, "blender-material-audit.json"), "utf8"));',
    'const audit = JSON.parse(fs.readFileSync(path.join(output, "blender-material-audit.json"), "utf8"));\n'
    'const motion = JSON.parse(fs.readFileSync(path.join(output, "endpoint-material-motion-audit.json"), "utf8"));',
)
register = register.replace(
    '[material, texture, image, audit]',
    '[material, texture, image, audit, motion]',
)
register = register.replace(
    '{ id: "interactive-and-recording"',
    '{ id: "endpoint-interlock-motion", status: "pass", evidence: `Dense ${motion.denseSamples} samples; rotation blocks ${motion.blockedRotationAttempts}; slide blocks ${motion.blockedSlideAttempts}; pivot variance ${motion.maxPivotVarianceMm} mm; penetration ${motion.maximumSurfaceIntersectionCount}.` },\n'
    '  { id: "interactive-and-recording"',
)
register = register.replace(
    'for (let index = 7; index < 11; index += 1)',
    'for (let index = 7; index < 12; index += 1)',
)
register = register.replace('manifest.stages[11].status = "rejected";', '')
register = register.replace(
    '"Gate 07 rev 12 reapplies source-backed blood-red, black, silver and dark-side materials to the unchanged geometry."',
    '"Gate 07 rev 12 reuses approved rev 11 appearance unchanged and permits rotation only at the maximum slide endpoint."',
)
(HERE / "register_gate07_endpoint_review.mjs").write_text(register, encoding="utf-8")

browser_source = REV11.parents[7] / "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate07.mjs"
browser = browser_source.read_text(encoding="utf-8")
for old, new in {
    "9226": "9242",
    "rev11": "rev12",
    "rev-011": "rev-012",
    "r011": "r012",
    "Gate 07 rev 11": "Gate 07 rev 12",
    "assembled-open": "max-open-12",
}.items():
    browser = browser.replace(old, new)
browser = browser.replace(
    'path.resolve("../../Artifacts/ModelProvenanceExplorer/magnetic-slide-gate07-rev12-persistent-workbench.png")',
    'path.resolve("../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-012/gate07-r012-persistent-workbench.png")',
)
browser = browser.replace(
    'path.resolve("../../Artifacts/ModelProvenanceExplorer/magnetic-slide-gate07-rev12-workbench-focused.png")',
    'path.resolve("../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-012/gate07-r012-workbench-focused.png")',
)
browser_output = REV11.parents[7] / "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate07-r012.mjs"
browser_output.write_text(browser, encoding="utf-8")
print(json.dumps({
    "pass": lineage["pass"],
    "builder": str(HERE / "build_gate07_endpoint_material.py"),
    "textureHashes": {
        slot: {
            key: lineage["outputs"][slot][f"{key}Sha256"]
            for key in ("albedo", "roughness")
        } for slot in ("upper", "lower")
    },
}, indent=2))
