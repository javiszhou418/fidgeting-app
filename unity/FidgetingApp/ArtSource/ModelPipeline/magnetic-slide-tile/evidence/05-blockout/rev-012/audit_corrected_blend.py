import bpy
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
BLEND = HERE / "magnetic-slide-tile-fixed-axis-r012.blend"
REPORT = HERE / "blender-audit.json"
bpy.ops.wm.open_mainfile(filepath=str(BLEND))
scene = bpy.context.scene
product_meshes = sorted(
    obj.name for obj in bpy.data.objects
    if obj.type == "MESH" and obj.get("product_render") is True
)
internal_meshes = sorted(
    obj.name for obj in bpy.data.objects
    if obj.type == "MESH" and obj.get("technical_render") is True
)
pivots = [obj.name for obj in bpy.data.objects if obj.get("pivot_id")]
disk = bpy.data.objects["MinimumOverlapDisk"]
bottom = bpy.data.objects["BottomExterior"]
top_z = [
    (bottom.matrix_world @ bottom.data.vertices[index].co).z
    for polygon in bottom.data.polygons if polygon.normal.z > 0.999999
    for index in polygon.vertices
]
animations = [
    obj.name for obj in bpy.data.objects
    if obj.animation_data and (obj.animation_data.action or obj.animation_data.drivers)
]
checks = {
    "sceneIdentity": scene.get("gate") == "05-blockout" and scene.get("revision") == 12,
    "contractHash": scene.get("mechanism_contract_sha256") == "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea",
    "exactTransformRecorded": scene.get("exact_top_transform") == "T(P)*Rz(theta)*T(-q(s)); q(s)=(0,-9+s,-3.1875)",
    "singlePivot": pivots == ["FixedAxis"],
    "fixedPivotParent": bpy.data.objects["FixedAxis"].parent == bottom,
    "carrierOwnsNoTranslation": bpy.data.objects["RotatingCarrier"].parent == bpy.data.objects["FixedAxis"] and bpy.data.objects["RotatingCarrier"].get("translation_dof") is False,
    "productWhitelist": product_meshes == ["BottomExterior", "MovingTopBody"],
    "internalTechnicalOnly": internal_meshes == ["BallCandidateLeft", "BallCandidateRight", "CarrierFollowerLeft", "CarrierFollowerRight", "InternalAxisBoss", "RotatingCarrierBody"],
    "minimumDiskMetadataOnly": disk.type == "EMPTY" and disk.hide_render and disk.get("render_geometry") is False,
    "bottomPlane": max(top_z) - min(top_z) <= 0.001,
    "noAnimations": not animations and scene.get("self_motion") is False,
    "clayOnly": all(all("G05R12_" in material.name for material in obj.data.materials) for obj in bpy.data.objects if obj.type == "MESH"),
}
report = {
    "schemaVersion": 1,
    "gate": "05-blockout",
    "revision": 12,
    "blendSha256": hashlib.sha256(BLEND.read_bytes()).hexdigest(),
    "productMeshes": product_meshes,
    "technicalMeshes": internal_meshes,
    "pivotObjects": pivots,
    "bottomTopPlaneDeviationMm": max(top_z) - min(top_z),
    "animations": animations,
    "checks": checks,
    "pass": all(checks.values()),
}
REPORT.write_text(json.dumps(report, indent=2))
if not report["pass"]:
    raise RuntimeError(json.dumps(report, indent=2))
print(json.dumps(report, indent=2))

