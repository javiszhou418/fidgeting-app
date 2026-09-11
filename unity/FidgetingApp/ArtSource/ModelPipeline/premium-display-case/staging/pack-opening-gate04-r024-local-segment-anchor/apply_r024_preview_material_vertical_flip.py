#!/usr/bin/env python3
"""Apply a Blender-only vertical preview mapping to the immutable R024 rig."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import struct
import sys
from pathlib import Path

import bpy


POSE_PROGRESS = (0.0, 0.11, 0.28, 0.50, 0.70, 0.86, 1.0)
POSE_KEYS = (
    "Pose_TabCatch",
    "Pose_Resistance",
    "Pose_TearAdvance",
    "Pose_FormedMouth",
    "Pose_CaseContained",
    "Pose_ContinuousRise",
)
HIDDEN_WHEN_SEALED = (
    "Pack_RearInnerFoil",
    "Pack_InnerFoilMouth",
    "Pack_InnerBackFoilRim",
    "Pack_RolledCrimpLip",
    "Pack_TornContourSweepCarrier",
    "Pack_TearFrontSidewall",
    "Pack_TabSidewall",
    "Pack_ReleasedSealStrip",
    "Pack_TopRightPullTab",
)
EXPECTED_OBJECTS = (
    "Pack_FrontPrintedFoil",
    "Pack_RearInnerFoil",
    "Pack_TopSealRemaining",
    "Pack_InnerFoilMouth",
    "Pack_InnerBackFoilRim",
    "Pack_RolledCrimpLip",
    "Pack_TornContourSweepCarrier",
    "Pack_TearFrontSidewall",
    "Pack_TabSidewall",
    "Pack_ReleasedSealStrip",
    "Pack_TopRightPullTab",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-blend", required=True)
    parser.add_argument("--output-blend", required=True)
    parser.add_argument("--reference-fbx", required=True)
    parser.add_argument("--output-fbx", required=True)
    parser.add_argument("--preview-sealed", required=True)
    parser.add_argument("--preview-050", required=True)
    parser.add_argument("--preview-070", required=True)
    parser.add_argument("--preview-090", required=True)
    parser.add_argument("--report", required=True)
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1 :])


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def add_text(digest: hashlib._hashlib.HASH, value: str) -> None:
    encoded = value.encode("utf-8")
    digest.update(len(encoded).to_bytes(4, "little"))
    digest.update(encoded)


def add_float(digest: hashlib._hashlib.HASH, value: float) -> None:
    digest.update(struct.pack("<d", float(value)))


def uv_stream_digest(objects: tuple[bpy.types.Object, ...]) -> str:
    digest = hashlib.sha256()
    for object_ in objects:
        mesh = object_.data
        add_text(digest, object_.name)
        for layer in mesh.uv_layers:
            add_text(digest, layer.name)
            for coordinate in layer.data:
                add_float(digest, coordinate.uv.x)
                add_float(digest, coordinate.uv.y)
    return digest.hexdigest()


def geometry_stream_digest(objects: tuple[bpy.types.Object, ...]) -> str:
    digest = hashlib.sha256()
    for object_ in objects:
        mesh = object_.data
        add_text(digest, object_.name)
        for vertex in mesh.vertices:
            add_float(digest, vertex.co.x)
            add_float(digest, vertex.co.y)
            add_float(digest, vertex.co.z)
        for polygon in mesh.polygons:
            add_text(digest, ",".join(str(index) for index in polygon.vertices))
        keys = mesh.shape_keys
        if keys:
            for key in keys.key_blocks:
                add_text(digest, key.name)
                for point in key.data:
                    add_float(digest, point.co.x)
                    add_float(digest, point.co.y)
                    add_float(digest, point.co.z)
    return digest.hexdigest()


def rig_objects() -> tuple[bpy.types.Object, ...]:
    objects = tuple(bpy.data.objects[name] for name in EXPECTED_OBJECTS)
    if not all(object_.type == "MESH" for object_ in objects):
        raise RuntimeError("R024 preview source does not contain all Pack meshes.")
    return objects


def set_blend_progress(
    objects: tuple[bpy.types.Object, ...], progress: float
) -> None:
    progress = max(0.0, min(1.0, progress))
    weights = {key: 0.0 for key in POSE_KEYS}
    if progress >= POSE_PROGRESS[-1]:
        weights[POSE_KEYS[-1]] = 1.0
    elif progress > 0.0:
        upper = next(
            index for index, sample in enumerate(POSE_PROGRESS)
            if progress <= sample
        )
        lower_progress = POSE_PROGRESS[upper - 1]
        blend = (progress - lower_progress) / (
            POSE_PROGRESS[upper] - lower_progress
        )
        if upper > 1:
            weights[POSE_KEYS[upper - 2]] = 1.0 - blend
        weights[POSE_KEYS[upper - 1]] = blend
    for object_ in objects:
        key_blocks = object_.data.shape_keys.key_blocks
        for key in POSE_KEYS:
            key_blocks[key].value = weights[key]
        object_.hide_render = object_.name == "Pack_TornContourSweepCarrier"
    if progress <= 0.0:
        for name in HIDDEN_WHEN_SEALED:
            bpy.data.objects[name].hide_render = True
    elif progress <= POSE_PROGRESS[1]:
        bpy.data.objects["Pack_ReleasedSealStrip"].hide_render = True
    bpy.context.view_layer.update()


def smooth01(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3.0 - 2.0 * value)


def timeline_tear_progress(seconds: float) -> float:
    if seconds < 0.14:
        return 0.0
    if seconds < 0.32:
        return 0.11 * smooth01((seconds - 0.14) / 0.18)
    if seconds < 0.50:
        return 0.11 + 0.17 * smooth01((seconds - 0.32) / 0.18)
    if seconds < 0.76:
        return 0.28 + 0.42 * smooth01((seconds - 0.50) / 0.26)
    if seconds < 1.03:
        return 0.70 + 0.16 * smooth01((seconds - 0.76) / 0.27)
    return 0.86 + 0.14 * smooth01((seconds - 1.03) / 0.25)


def render_at_time(
    scene: bpy.types.Scene,
    objects: tuple[bpy.types.Object, ...],
    seconds: float,
    path: Path,
) -> None:
    set_blend_progress(objects, timeline_tear_progress(seconds))
    scene.render.filepath = str(path)
    bpy.ops.render.render(write_still=True)


def add_preview_vertical_flip() -> dict[str, object]:
    material = bpy.data.materials.get("MI_R024_ActualPackArtwork")
    if material is None or not material.use_nodes:
        raise RuntimeError("R024 printed Pack preview material is unavailable.")
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    image_nodes = [
        node for node in nodes
        if node.bl_idname == "ShaderNodeTexImage" and node.image is not None
    ]
    if len(image_nodes) != 1:
        raise RuntimeError("R024 Pack preview material must have one image node.")
    image = image_nodes[0]
    if tuple(image.image.size) != (384, 512):
        raise RuntimeError("R024 Pack preview image is not the authored 384x512 art.")
    if image.inputs["Vector"].is_linked:
        raise RuntimeError("R024 Pack preview image already has coordinate mapping.")
    texcoord = nodes.new("ShaderNodeTexCoord")
    texcoord.name = "R024PreviewOnlyTextureCoordinates"
    mapping = nodes.new("ShaderNodeMapping")
    mapping.name = "R024PreviewOnlyVerticalFlip"
    mapping.vector_type = "POINT"
    mapping.inputs["Location"].default_value = (0.0, 1.0, 0.0)
    mapping.inputs["Scale"].default_value = (1.0, -1.0, 1.0)
    links.new(texcoord.outputs["UV"], mapping.inputs["Vector"])
    links.new(mapping.outputs["Vector"], image.inputs["Vector"])
    material["r024_preview_only"] = True
    material["r024_preview_mapping"] = "source-v -> 1-source-v"
    material["r024_exported_fbx_unchanged"] = True
    return {
        "material": material.name,
        "image": image.image.filepath,
        "imageCanvas": [int(image.image.size[0]), int(image.image.size[1])],
        "mapping": {
            "coordinate": "UV",
            "location": [0.0, 1.0, 0.0],
            "scale": [1.0, -1.0, 1.0],
            "formula": "source-v -> 1-source-v",
        },
    }


def main() -> None:
    args = parse_args()
    input_blend = Path(args.input_blend).resolve()
    output_blend = Path(args.output_blend).resolve()
    reference_fbx = Path(args.reference_fbx).resolve()
    output_fbx = Path(args.output_fbx).resolve()
    report_path = Path(args.report).resolve()
    previews = {
        "sealed": Path(args.preview_sealed).resolve(),
        "tear050": Path(args.preview_050).resolve(),
        "formed070": Path(args.preview_070).resolve(),
        "contained090": Path(args.preview_090).resolve(),
    }
    if not input_blend.is_file() or not reference_fbx.is_file():
        raise RuntimeError("R024 needs the immutable R024 Blend and FBX inputs.")
    if input_blend == output_blend or reference_fbx == output_fbx:
        raise RuntimeError("R024 may not overwrite an immutable R024 input.")
    if any(path.exists() for path in (output_blend, output_fbx, report_path)):
        raise RuntimeError("R024 output already exists and is immutable.")
    for path in (output_blend, output_fbx, report_path, *previews.values()):
        path.parent.mkdir(parents=True, exist_ok=True)

    objects = rig_objects()
    before_uv_digest = uv_stream_digest(objects)
    before_geometry_digest = geometry_stream_digest(objects)
    before_fbx_sha256 = sha256(reference_fbx)
    scene = bpy.context.scene
    if (scene.render.resolution_x, scene.render.resolution_y) != (1206, 2622):
        raise RuntimeError("R024 preview scene must stay at 1206x2622.")

    preview_mapping = add_preview_vertical_flip()
    after_uv_digest = uv_stream_digest(objects)
    after_geometry_digest = geometry_stream_digest(objects)
    if before_uv_digest != after_uv_digest:
        raise RuntimeError("Preview mapping changed the exported UV stream.")
    if before_geometry_digest != after_geometry_digest:
        raise RuntimeError("Preview mapping changed Pack geometry.")

    set_blend_progress(objects, 0.0)
    scene.render.filepath = str(previews["sealed"])
    bpy.ops.render.render(write_still=True)
    render_at_time(scene, objects, 0.50, previews["tear050"])
    render_at_time(scene, objects, 0.70, previews["formed070"])
    render_at_time(scene, objects, 0.90, previews["contained090"])
    set_blend_progress(objects, 0.0)
    bpy.ops.wm.save_as_mainfile(filepath=str(output_blend))
    shutil.copyfile(reference_fbx, output_fbx)
    after_fbx_sha256 = sha256(output_fbx)
    if before_fbx_sha256 != after_fbx_sha256:
        raise RuntimeError("R024 copied FBX does not match immutable R024 export.")

    report = {
        "schema": "premium-display-case-gate04-r024-preview-mapping-proof.v1",
        "repairScope": "Blender preview material mapping only",
        "input": {
            "r024Blend": str(input_blend),
            "r024BlendSha256": sha256(input_blend),
            "r024Fbx": str(reference_fbx),
            "r024FbxSha256": before_fbx_sha256,
        },
        "output": {
            "r024PreviewBlend": str(output_blend),
            "r024PreviewBlendSha256": sha256(output_blend),
            "r024UnityFbx": str(output_fbx),
            "r024UnityFbxSha256": after_fbx_sha256,
        },
        "previewMaterialOnly": preview_mapping,
        "exportInvariants": {
            "exportedFbxByteIdenticalToR024": before_fbx_sha256 == after_fbx_sha256,
            "uvStreamUnchanged": before_uv_digest == after_uv_digest,
            "geometryStreamUnchanged": before_geometry_digest
            == after_geometry_digest,
            "r024PhysicalUToSourceU": "1-to-0",
            "unityMaterialMappingChanged": False,
            "rootCoordinatesChanged": False,
            "artTextureChanged": False,
            "packGeometryChanged": False,
            "tearProgressionChanged": False,
            "caseChanged": False,
        },
        "uvStreamSha256": before_uv_digest,
        "geometryStreamSha256": before_geometry_digest,
        "previews": {
            key: {
                "path": str(path),
                "sha256": sha256(path),
                "dimensions": [scene.render.resolution_x, scene.render.resolution_y],
            }
            for key, path in previews.items()
        },
    }
    report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
