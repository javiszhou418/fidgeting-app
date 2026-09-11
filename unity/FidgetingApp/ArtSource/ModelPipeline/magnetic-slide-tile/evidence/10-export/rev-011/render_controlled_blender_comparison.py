#!/usr/bin/env python3
"""Render authoritative Blender and corrected GLB under one neutral setup."""

from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import bpy
import numpy as np
from mathutils import Vector


HERE = Path(__file__).resolve().parent
PACKAGE = HERE / "package"
GLB = PACKAGE / "magnetic-slide-tile-render-r011.glb"
OUTPUTS = HERE / "controlled-neutral"
REIMPORT_BLEND = PACKAGE / "magnetic-slide-tile-glb-reimport-r011.blend"
CORE = [
    "BottomExterior",
    "InternalAxisBoss",
    "RotatingCarrierBody",
    "CarrierFollowerLeft",
    "CarrierFollowerRight",
    "BallCandidateLeft",
    "BallCandidateRight",
    "MovingTopBody",
]
CAMERAS = {
    "hero": "M08R6_Hero",
    "top-closeup": "M08R6_TopCloseup",
    "side-closeup": "M08R6_SideCloseup",
    "rim-closeup": "M08R6_RimCloseup",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounds(objects: list[bpy.types.Object]) -> tuple[Vector, Vector]:
    points = [obj.matrix_world @ Vector(corner) for obj in objects for corner in obj.bound_box]
    return (
        Vector((min(point.x for point in points), min(point.y for point in points), min(point.z for point in points))),
        Vector((max(point.x for point in points), max(point.y for point in points), max(point.z for point in points))),
    )


def render(path: Path, camera_name: str) -> None:
    scene = bpy.context.scene
    scene.camera = bpy.data.objects[camera_name]
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1000
    scene.render.resolution_y = 620
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGBA"
    scene.render.film_transparent = True
    scene.render.filepath = str(path)
    scene.view_settings.look = "None"
    scene.view_settings.exposure = 0.0
    scene.view_settings.gamma = 1.0
    scene.render.image_settings.color_management = "FOLLOW_SCENE"
    bpy.ops.render.render(write_still=True)


def add_controlled_lights() -> list[dict]:
    records = []
    for name, location, energy, angle in [
        ("G10R11_NeutralKey", (70, -90, 105), 1.4, math.radians(18)),
        ("G10R11_NeutralFill", (-75, -35, 58), 0.35, math.radians(28)),
        ("G10R11_NeutralRim", (32, 72, 68), 0.55, math.radians(12)),
    ]:
        data = bpy.data.lights.new(name, "SUN")
        data.energy = energy
        data.angle = angle
        light = bpy.data.objects.new(name, data)
        bpy.context.scene.collection.objects.link(light)
        light.location = location
        direction = Vector((0, 0, 6)) - light.location
        light.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
        records.append({"name": name, "irradiance": energy, "angleDegrees": math.degrees(angle), "directionAnchor": list(location)})
    return records


def image_metrics(path: Path) -> dict:
    image = bpy.data.images.load(str(path), check_existing=False)
    data = np.empty(len(image.pixels), dtype=np.float32)
    image.pixels.foreach_get(data)
    data = data.reshape((-1, 4))
    rgb = data[:, :3]
    alpha = data[:, 3] > 0.25
    pixels = rgb[alpha]
    luminance = pixels[:, 0] * 0.2126 + pixels[:, 1] * 0.7152 + pixels[:, 2] * 0.0722
    red = (pixels[:, 0] > pixels[:, 1] * 1.35) & (pixels[:, 0] > pixels[:, 2] * 1.20) & (pixels[:, 0] > 0.001)
    return {
        "objectPixelCount": int(alpha.sum()),
        "coverage": float(alpha.mean()),
        "luminanceP05P50P95": [float(np.percentile(luminance, p)) for p in [5, 50, 95]],
        "redFractionOfObject": float(red.mean()),
        "darkFractionOfObject": float((luminance < 0.10).mean()),
        "silverHighlightFractionOfObject": float(((luminance > 0.62) & (luminance < 0.92)).mean()),
        "clippedWhiteFractionOfObject": float((luminance > 0.95).mean()),
    }


def artwork_coverage(objects: list[bpy.types.Object]) -> dict:
    result = {}
    for obj in objects:
        if obj.type != "MESH":
            continue
        mesh = obj.data
        slots = [slot.material.name if slot.material else "<none>" for slot in obj.material_slots]
        semantic_slots = [slot.removesuffix(".001") for slot in slots]
        mesh.calc_loop_triangles()
        counts = [0] * len(slots)
        for triangle in mesh.loop_triangles:
            counts[triangle.material_index] += 1
        result[obj.name] = {
            "slots": slots,
            "triangles": counts,
            "topArtwork": sum(count for slot, count in zip(semantic_slots, counts) if slot.endswith("TopArtwork")),
            "sideArtwork": sum(
                1
                for polygon in mesh.polygons
                if abs(polygon.normal.z) < 0.62
                and semantic_slots[polygon.material_index].endswith("TopArtwork")
            ),
            "undersideArtwork": sum(
                1
                for polygon in mesh.polygons
                if polygon.normal.z < -0.62
                and semantic_slots[polygon.material_index].endswith("TopArtwork")
            ),
        }
    return result


def main() -> None:
    OUTPUTS.mkdir(parents=True, exist_ok=True)
    controlled_lights = add_controlled_lights()
    source_objects = [bpy.data.objects[name] for name in CORE]
    source_min, source_max = bounds(source_objects)
    source_materials = {
        obj.name: [slot.material.name if slot.material else "<none>" for slot in obj.material_slots]
        for obj in source_objects
    }
    source_indices = {
        obj.name: [polygon.material_index for polygon in obj.data.polygons]
        for obj in source_objects
    }
    target_paths = {}
    for view, camera in CAMERAS.items():
        path = OUTPUTS / f"approved-blender-{view}-r011.png"
        render(path, camera)
        target_paths[view] = path

    before_names = set(bpy.data.objects.keys())
    bpy.ops.import_scene.gltf(filepath=str(GLB), import_pack_images=True, merge_vertices=False)
    imported = [obj for name, obj in bpy.data.objects.items() if name not in before_names]
    imported_meshes = [obj for obj in imported if obj.type == "MESH"]
    imported_roots = [obj for obj in imported if obj.parent is None]
    imported_min, imported_max = bounds(imported_meshes)
    source_size = source_max - source_min
    imported_size = imported_max - imported_min
    scale = source_size.length / imported_size.length
    if not (0.999 <= scale <= 1.001):
        raise RuntimeError(f"Unexpected GLB reimport scale factor {scale}.")
    for root in imported_roots:
        root.scale *= scale
    bpy.context.view_layer.update()
    imported_min, imported_max = bounds(imported_meshes)
    imported_center = (imported_min + imported_max) * 0.5
    source_center = (source_min + source_max) * 0.5
    delta = source_center - imported_center
    for root in imported_roots:
        root.location += delta
    bpy.context.view_layer.update()
    for obj in source_objects:
        obj.hide_render = True
    reimport_paths = {}
    for view, camera in CAMERAS.items():
        path = OUTPUTS / f"glb-reimport-{view}-r011.png"
        render(path, camera)
        reimport_paths[view] = path

    image_spaces = {
        image.name: image.colorspace_settings.name
        for image in bpy.data.images
        if any(token in image.name.lower() for token in ["albedo", "roughness", "normal"])
    }
    partition = artwork_coverage(imported_meshes)
    root_matches = [obj for obj in imported if obj.name.startswith("MagneticSlideTile_G06_R005")]
    endpoint = root_matches[0] if root_matches else None
    for obj in source_objects:
        obj.hide_render = False
    for obj in imported:
        if hasattr(obj, "hide_render"):
            obj.hide_render = True
    bpy.ops.wm.save_as_mainfile(filepath=str(REIMPORT_BLEND), compress=True)

    target_metrics = image_metrics(target_paths["hero"])
    reimport_metrics = image_metrics(reimport_paths["hero"])
    target_luminance = target_metrics["luminanceP05P50P95"][1]
    reimport_luminance = reimport_metrics["luminanceP05P50P95"][1]
    checks = {
        "sameCamera": all(bpy.data.objects[name].type == "CAMERA" for name in CAMERAS.values()),
        "sameEnvironment": bpy.context.scene.world is not None
            and sorted(obj.name for obj in bpy.data.objects if obj.type == "LIGHT")
            == sorted(record["name"] for record in controlled_lights),
        "scaleRecovered": math.isclose(scale, 1.0, rel_tol=0.001),
        "boundsMatch": all(abs(a - b) <= 0.002 for a, b in zip(source_size, imported_max - imported_min)),
        "sourceMaterialSlotsUnchanged": all(
            source_materials[obj.name] == [slot.material.name if slot.material else "<none>" for slot in obj.material_slots]
            for obj in source_objects
        ),
        "sourceMaterialIndicesUnchanged": all(
            source_indices[obj.name] == [polygon.material_index for polygon in obj.data.polygons]
            for obj in source_objects
        ),
        "topArtworkPresent": sum(item["topArtwork"] for item in partition.values()) > 0,
        "sideArtworkZero": sum(item["sideArtwork"] for item in partition.values()) == 0,
        "undersideArtworkZero": sum(item["undersideArtwork"] for item in partition.values()) == 0,
        "baseColorSRGB": all(
            value in {"sRGB", "Utility - sRGB - Texture"}
            for key, value in image_spaces.items()
            if "albedo" in key.lower()
        ),
        "dataMapsLinear": all(
            value in {"Non-Color", "Linear Rec.709", "Utility - Linear - sRGB"}
            for key, value in image_spaces.items()
            if "roughness" in key.lower() or "normal" in key.lower()
        ),
        "endpointMetadata": endpoint is not None
            and bool(endpoint.get("rotationLockedBelowSMax"))
            and int(endpoint.get("rotationAtSMaxDegrees")) == 360
            and bool(endpoint.get("slideLockedAtNonzeroAngle"))
            and endpoint.get("returnRule") == "align theta to 0 then close",
        "deepRedTop": reimport_metrics["redFractionOfObject"] >= 0.06,
        "darkBody": reimport_metrics["darkFractionOfObject"] >= 0.20,
        "silverHighlightControlled": 0.001 <= reimport_metrics["silverHighlightFractionOfObject"] <= 0.25,
        "whiteClippingControlled": reimport_metrics["clippedWhiteFractionOfObject"] <= 0.04,
        "luminanceWithinTargetTolerance": abs(reimport_luminance - target_luminance) <= 0.18,
    }
    report = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 11,
        "pass": all(checks.values()),
        "controlledSetup": {
            "camera": "M08R6_Hero",
            "resolution": [1000, 620],
            "renderEngine": "BLENDER_EEVEE",
            "world": bpy.context.scene.world.name,
            "lights": controlled_lights,
            "viewTransform": bpy.context.scene.view_settings.view_transform,
            "look": bpy.context.scene.view_settings.look,
            "exposure": bpy.context.scene.view_settings.exposure,
            "gamma": bpy.context.scene.view_settings.gamma,
        },
        "sourceBoundsMm": {"min": list(source_min), "max": list(source_max), "size": list(source_size)},
        "reimportBoundsMm": {"min": list(imported_min), "max": list(imported_max), "size": list(imported_max - imported_min)},
        "importScaleCorrection": scale,
        "sourceMetrics": target_metrics,
        "reimportMetrics": reimport_metrics,
        "materialPartitions": partition,
        "imageColorSpaces": image_spaces,
        "checks": checks,
        "artifacts": {
            "reimportBlend": {"path": str(REIMPORT_BLEND), "sha256": sha256(REIMPORT_BLEND)},
            "approvedBlender": {view: {"path": str(path), "sha256": sha256(path)} for view, path in target_paths.items()},
            "glbReimport": {view: {"path": str(path), "sha256": sha256(path)} for view, path in reimport_paths.items()},
        },
    }
    (HERE / "controlled-blender-comparison-validation.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, ensure_ascii=False, indent=2))
    print(json.dumps({
        "pass": True,
        "sourceMetrics": target_metrics,
        "reimportMetrics": reimport_metrics,
    }, indent=2))


if __name__ == "__main__":
    main()
