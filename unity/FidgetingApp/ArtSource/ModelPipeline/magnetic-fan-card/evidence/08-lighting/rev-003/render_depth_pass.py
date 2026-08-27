"""Render a real camera-distance diagnostic for Gate 08."""

from pathlib import Path

import bpy


HERE = Path(__file__).resolve().parent
BLEND = HERE / "fan-card-72-segment-lighting.blend"


def main() -> None:
    bpy.ops.wm.open_mainfile(filepath=str(BLEND))
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1179
    scene.render.resolution_y = 654
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    material = bpy.data.materials.new("MAT_Pass_Depth")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    links = material.node_tree.links
    nodes.clear()
    output = nodes.new("ShaderNodeOutputMaterial")
    camera = nodes.new("ShaderNodeCameraData")
    map_range = nodes.new("ShaderNodeMapRange")
    map_range.inputs["From Min"].default_value = 0.18
    map_range.inputs["From Max"].default_value = 0.52
    map_range.inputs["To Min"].default_value = 1.0
    map_range.inputs["To Max"].default_value = 0.0
    map_range.clamp = True
    emission = nodes.new("ShaderNodeEmission")
    emission.inputs["Strength"].default_value = 1.0
    links.new(camera.outputs["View Distance"], map_range.inputs["Value"])
    links.new(map_range.outputs["Result"], emission.inputs["Color"])
    links.new(emission.outputs["Emission"], output.inputs["Surface"])
    scene.view_layers[0].material_override = material
    scene.render.filepath = str(HERE / "pass-depth.png")
    bpy.ops.render.render(write_still=True)


if __name__ == "__main__":
    main()
