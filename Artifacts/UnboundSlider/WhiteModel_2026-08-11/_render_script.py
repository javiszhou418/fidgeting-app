#!/usr/bin/env python3
"""Auto-generated Blender Python script from blender-cli."""

import bpy
import math
import os

# ── Clear Default Scene ──────────────────────────────────────
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ── Scene Settings ──────────────────────────────────────────
scene = bpy.context.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.scale_length = 1.0
scene.frame_start = 1
scene.frame_end = 40
scene.frame_current = 1
scene.render.fps = 24

# ── Render Settings ─────────────────────────────────────────
try:
    scene.render.engine = 'BLENDER_EEVEE_NEXT'
except TypeError:
    scene.render.engine = 'BLENDER_EEVEE'
scene.render.resolution_x = 900
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
if hasattr(scene, 'eevee') and hasattr(scene.eevee, 'taa_render_samples'):
    scene.eevee.taa_render_samples = 64

# ── World Settings ──────────────────────────────────────────
world = bpy.data.worlds.get('World')
if world is None:
    world = bpy.data.worlds.new('World')
    scene.world = world
world.use_nodes = True
bg_node = world.node_tree.nodes.get('Background')
if bg_node:
    bg_node.inputs[0].default_value = (0.05, 0.05, 0.05, 1.0)

# ── Materials ───────────────────────────────────────────────
mat_WhiteMetal = bpy.data.materials.new(name='WhiteMetal')
mat_WhiteMetal.use_nodes = True
bsdf_WhiteMetal = mat_WhiteMetal.node_tree.nodes.get('Principled BSDF')
if bsdf_WhiteMetal:
    bsdf_WhiteMetal.inputs['Base Color'].default_value = (0.12, 0.16, 0.22, 1.0)
    bsdf_WhiteMetal.inputs['Metallic'].default_value = 0.72
    bsdf_WhiteMetal.inputs['Roughness'].default_value = 0.38
    bsdf_WhiteMetal.inputs['Specular IOR Level'].default_value = 0.52
    bsdf_WhiteMetal.inputs['Alpha'].default_value = 1.0

mat_DarkCarrier = bpy.data.materials.new(name='DarkCarrier')
mat_DarkCarrier.use_nodes = True
bsdf_DarkCarrier = mat_DarkCarrier.node_tree.nodes.get('Principled BSDF')
if bsdf_DarkCarrier:
    bsdf_DarkCarrier.inputs['Base Color'].default_value = (0.004, 0.007, 0.012, 1.0)
    bsdf_DarkCarrier.inputs['Metallic'].default_value = 0.02
    bsdf_DarkCarrier.inputs['Roughness'].default_value = 0.76
    bsdf_DarkCarrier.inputs['Specular IOR Level'].default_value = 0.32
    bsdf_DarkCarrier.inputs['Alpha'].default_value = 1.0

mat_MagnetSteel = bpy.data.materials.new(name='MagnetSteel')
mat_MagnetSteel.use_nodes = True
bsdf_MagnetSteel = mat_MagnetSteel.node_tree.nodes.get('Principled BSDF')
if bsdf_MagnetSteel:
    bsdf_MagnetSteel.inputs['Base Color'].default_value = (0.28, 0.34, 0.44, 1.0)
    bsdf_MagnetSteel.inputs['Metallic'].default_value = 0.92
    bsdf_MagnetSteel.inputs['Roughness'].default_value = 0.2
    bsdf_MagnetSteel.inputs['Specular IOR Level'].default_value = 0.58
    bsdf_MagnetSteel.inputs['Alpha'].default_value = 1.0

mat_BrassFork = bpy.data.materials.new(name='BrassFork')
mat_BrassFork.use_nodes = True
bsdf_BrassFork = mat_BrassFork.node_tree.nodes.get('Principled BSDF')
if bsdf_BrassFork:
    bsdf_BrassFork.inputs['Base Color'].default_value = (0.46, 0.22, 0.025, 1.0)
    bsdf_BrassFork.inputs['Metallic'].default_value = 0.84
    bsdf_BrassFork.inputs['Roughness'].default_value = 0.26
    bsdf_BrassFork.inputs['Specular IOR Level'].default_value = 0.5
    bsdf_BrassFork.inputs['Alpha'].default_value = 1.0

mat_ContactLayer = bpy.data.materials.new(name='ContactLayer')
mat_ContactLayer.use_nodes = True
bsdf_ContactLayer = mat_ContactLayer.node_tree.nodes.get('Principled BSDF')
if bsdf_ContactLayer:
    bsdf_ContactLayer.inputs['Base Color'].default_value = (0.008, 0.012, 0.02, 1.0)
    bsdf_ContactLayer.inputs['Metallic'].default_value = 0.0
    bsdf_ContactLayer.inputs['Roughness'].default_value = 0.72
    bsdf_ContactLayer.inputs['Specular IOR Level'].default_value = 0.24
    bsdf_ContactLayer.inputs['Alpha'].default_value = 1.0

mat_StudioFloor = bpy.data.materials.new(name='StudioFloor')
mat_StudioFloor.use_nodes = True
bsdf_StudioFloor = mat_StudioFloor.node_tree.nodes.get('Principled BSDF')
if bsdf_StudioFloor:
    bsdf_StudioFloor.inputs['Base Color'].default_value = (0.012, 0.016, 0.024, 1.0)
    bsdf_StudioFloor.inputs['Metallic'].default_value = 0.05
    bsdf_StudioFloor.inputs['Roughness'].default_value = 0.82
    bsdf_StudioFloor.inputs['Specular IOR Level'].default_value = 0.22
    bsdf_StudioFloor.inputs['Alpha'].default_value = 1.0

mat_PatternSilver = bpy.data.materials.new(name='PatternSilver')
mat_PatternSilver.use_nodes = True
bsdf_PatternSilver = mat_PatternSilver.node_tree.nodes.get('Principled BSDF')
if bsdf_PatternSilver:
    bsdf_PatternSilver.inputs['Base Color'].default_value = (0.012, 0.022, 0.042, 1.0)
    bsdf_PatternSilver.inputs['Metallic'].default_value = 0.32
    bsdf_PatternSilver.inputs['Roughness'].default_value = 0.58
    bsdf_PatternSilver.inputs['Specular IOR Level'].default_value = 0.5
    bsdf_PatternSilver.inputs['Alpha'].default_value = 1.0


# ── Objects ─────────────────────────────────────────────────
# Object: UnboundSlider_Root
bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'UnboundSlider_Root'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)

# Object: TopAssembly_Root
bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'TopAssembly_Root'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)

# Object: BottomAssembly_Root
bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'BottomAssembly_Root'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)

# Object: TopShell_Root
bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'TopShell_Root'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)

# Object: TopCarrier_Root
bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'TopCarrier_Root'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)

# Object: TopMagnets_Root
bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'TopMagnets_Root'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)

# Object: TopForks_Root
bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'TopForks_Root'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)

# Object: TopContact_Root
bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'TopContact_Root'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)

# Object: BottomShell_Root
bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'BottomShell_Root'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)

# Object: BottomCarrier_Root
bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'BottomCarrier_Root'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)

# Object: BottomMagnets_Root
bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'BottomMagnets_Root'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)

# Object: BottomForks_Root
bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'BottomForks_Root'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)

# Object: BottomContact_Root
bpy.ops.object.empty_add(location=(0.0, 0.0, 0.0))
obj = bpy.context.active_object
obj.name = 'BottomContact_Root'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)

# Object: TopCut_SlotUpper
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -0.0058, 0.0102))
obj = bpy.context.active_object
obj.name = 'TopCut_SlotUpper'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0155, 0.0022, 0.0032)
obj.hide_render = True
obj.hide_viewport = True
mod = obj.modifiers.new(name='SlotUpperRound', type='BEVEL')
mod.width = 0.0024
mod.segments = 6
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: TopCut_SlotLower
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -0.0058, -0.0102))
obj = bpy.context.active_object
obj.name = 'TopCut_SlotLower'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0155, 0.0022, 0.0032)
obj.hide_render = True
obj.hide_viewport = True
mod = obj.modifiers.new(name='SlotLowerRound', type='BEVEL')
mod.width = 0.0024
mod.segments = 6
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: TopCut_BigTL
bpy.ops.mesh.primitive_cylinder_add(radius=0.0047, depth=0.006, vertices=64, location=(-0.019, -0.0058, 0.0102))
obj = bpy.context.active_object
obj.name = 'TopCut_BigTL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopCut_BigTR
bpy.ops.mesh.primitive_cylinder_add(radius=0.0047, depth=0.006, vertices=64, location=(0.019, -0.0058, 0.0102))
obj = bpy.context.active_object
obj.name = 'TopCut_BigTR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopCut_BigBL
bpy.ops.mesh.primitive_cylinder_add(radius=0.0047, depth=0.006, vertices=64, location=(-0.019, -0.0058, -0.0102))
obj = bpy.context.active_object
obj.name = 'TopCut_BigBL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopCut_BigBR
bpy.ops.mesh.primitive_cylinder_add(radius=0.0047, depth=0.006, vertices=64, location=(0.019, -0.0058, -0.0102))
obj = bpy.context.active_object
obj.name = 'TopCut_BigBR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomCut_SlotUpper
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0058, 0.0102))
obj = bpy.context.active_object
obj.name = 'BottomCut_SlotUpper'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0155, 0.0022, 0.0032)
obj.hide_render = True
obj.hide_viewport = True
mod = obj.modifiers.new(name='SlotUpperRound', type='BEVEL')
mod.width = 0.0024
mod.segments = 6
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: BottomCut_SlotLower
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0058, -0.0102))
obj = bpy.context.active_object
obj.name = 'BottomCut_SlotLower'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0155, 0.0022, 0.0032)
obj.hide_render = True
obj.hide_viewport = True
mod = obj.modifiers.new(name='SlotLowerRound', type='BEVEL')
mod.width = 0.0024
mod.segments = 6
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: BottomCut_BigTL
bpy.ops.mesh.primitive_cylinder_add(radius=0.0047, depth=0.006, vertices=64, location=(-0.019, 0.0058, 0.0102))
obj = bpy.context.active_object
obj.name = 'BottomCut_BigTL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomCut_BigTR
bpy.ops.mesh.primitive_cylinder_add(radius=0.0047, depth=0.006, vertices=64, location=(0.019, 0.0058, 0.0102))
obj = bpy.context.active_object
obj.name = 'BottomCut_BigTR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomCut_BigBL
bpy.ops.mesh.primitive_cylinder_add(radius=0.0047, depth=0.006, vertices=64, location=(-0.019, 0.0058, -0.0102))
obj = bpy.context.active_object
obj.name = 'BottomCut_BigBL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomCut_BigBR
bpy.ops.mesh.primitive_cylinder_add(radius=0.0047, depth=0.006, vertices=64, location=(0.019, 0.0058, -0.0102))
obj = bpy.context.active_object
obj.name = 'BottomCut_BigBR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: Top_MetalShell
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -0.0058, 0.0))
obj = bpy.context.active_object
obj.name = 'Top_MetalShell'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.026, 0.0012, 0.018)
obj.hide_render = True
obj.hide_viewport = True
if 'mat_WhiteMetal' in dir():
    obj.data.materials.append(mat_WhiteMetal)
mod = obj.modifiers.new(name='OuterRadius', type='BEVEL')
mod.width = 0.17
mod.segments = 8
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599
mod = obj.modifiers.new(name='Cut_TopDetail_DropLeftBulb', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_DropLeftBulb')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_DropLeftNeck', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_DropLeftNeck')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_DropLeftTip', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_DropLeftTip')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_DropRightBulb', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_DropRightBulb')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_DropRightNeck', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_DropRightNeck')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_DropRightTip', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_DropRightTip')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_SlotURBody', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_SlotURBody')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_SlotUREndA', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_SlotUREndA')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_SlotUREndB', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_SlotUREndB')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_SlotBLBody', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_SlotBLBody')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_SlotBLEndA', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_SlotBLEndA')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_SlotBLEndB', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_SlotBLEndB')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_TriangleTL', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_TriangleTL')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_TriangleBR', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_TriangleBR')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='DetailEdgeSoftness', type='BEVEL')
mod.width = 0.025
mod.segments = 3
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_MetalShell
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0058, 0.0))
obj = bpy.context.active_object
obj.name = 'Bottom_MetalShell'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.026, 0.0012, 0.018)
obj.hide_render = True
obj.hide_viewport = True
if 'mat_WhiteMetal' in dir():
    obj.data.materials.append(mat_WhiteMetal)
mod = obj.modifiers.new(name='OuterRadius', type='BEVEL')
mod.width = 0.17
mod.segments = 8
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599
mod = obj.modifiers.new(name='Cut_BottomDetail_DropLeftBulb', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_DropLeftBulb')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_DropLeftNeck', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_DropLeftNeck')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_DropLeftTip', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_DropLeftTip')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_DropRightBulb', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_DropRightBulb')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_DropRightNeck', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_DropRightNeck')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_DropRightTip', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_DropRightTip')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_SlotURBody', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_SlotURBody')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_SlotUREndA', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_SlotUREndA')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_SlotUREndB', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_SlotUREndB')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_SlotBLBody', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_SlotBLBody')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_SlotBLEndA', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_SlotBLEndA')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_SlotBLEndB', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_SlotBLEndB')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_TriangleTL', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_TriangleTL')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_TriangleBR', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_TriangleBR')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='DetailEdgeSoftness', type='BEVEL')
mod.width = 0.025
mod.segments = 3
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_MagnetCarrier
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -0.0025, 0.0))
obj = bpy.context.active_object
obj.name = 'Top_MagnetCarrier'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0248, 0.0023, 0.0168)
if 'mat_DarkCarrier' in dir():
    obj.data.materials.append(mat_DarkCarrier)
mod = obj.modifiers.new(name='CarrierRadius', type='BEVEL')
mod.width = 0.14
mod.segments = 6
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_MagnetCarrier
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0025, 0.0))
obj = bpy.context.active_object
obj.name = 'Bottom_MagnetCarrier'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0248, 0.0023, 0.0168)
if 'mat_DarkCarrier' in dir():
    obj.data.materials.append(mat_DarkCarrier)
mod = obj.modifiers.new(name='CarrierRadius', type='BEVEL')
mod.width = 0.14
mod.segments = 6
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_LowFrictionContact
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -0.00015, 0.0))
obj = bpy.context.active_object
obj.name = 'Top_LowFrictionContact'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0246, 0.00015, 0.0166)
if 'mat_ContactLayer' in dir():
    obj.data.materials.append(mat_ContactLayer)
mod = obj.modifiers.new(name='ContactRadius', type='BEVEL')
mod.width = 0.002
mod.segments = 5
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_LowFrictionContact
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.00015, 0.0))
obj = bpy.context.active_object
obj.name = 'Bottom_LowFrictionContact'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0246, 0.00015, 0.0166)
if 'mat_ContactLayer' in dir():
    obj.data.materials.append(mat_ContactLayer)
mod = obj.modifiers.new(name='ContactRadius', type='BEVEL')
mod.width = 0.002
mod.segments = 5
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: TopCut_SideLeft
bpy.ops.mesh.primitive_cylinder_add(radius=0.0044, depth=0.006, vertices=3, location=(-0.019, -0.0058, 0.0))
obj = bpy.context.active_object
obj.name = 'TopCut_SideLeft'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(30.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopCut_SideRight
bpy.ops.mesh.primitive_cylinder_add(radius=0.0044, depth=0.006, vertices=3, location=(0.019, -0.0058, 0.0))
obj = bpy.context.active_object
obj.name = 'TopCut_SideRight'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(-30.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomCut_SideLeft
bpy.ops.mesh.primitive_cylinder_add(radius=0.0044, depth=0.006, vertices=3, location=(-0.019, 0.0058, 0.0))
obj = bpy.context.active_object
obj.name = 'BottomCut_SideLeft'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(30.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomCut_SideRight
bpy.ops.mesh.primitive_cylinder_add(radius=0.0044, depth=0.006, vertices=3, location=(0.019, 0.0058, 0.0))
obj = bpy.context.active_object
obj.name = 'BottomCut_SideRight'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(-30.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: Top_Magnet_R1C1
bpy.ops.mesh.primitive_cylinder_add(radius=0.0042, depth=0.0062, vertices=64, location=(-0.019, -0.0035, 0.0102))
obj = bpy.context.active_object
obj.name = 'Top_Magnet_R1C1'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.0005
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_Magnet_R1C2
bpy.ops.mesh.primitive_cylinder_add(radius=0.00255, depth=0.0062, vertices=64, location=(-0.0095, -0.0035, 0.0102))
obj = bpy.context.active_object
obj.name = 'Top_Magnet_R1C2'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.00035
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_Magnet_R1C3
bpy.ops.mesh.primitive_cylinder_add(radius=0.00255, depth=0.0062, vertices=64, location=(0.0, -0.0035, 0.0102))
obj = bpy.context.active_object
obj.name = 'Top_Magnet_R1C3'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.00035
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_Magnet_R1C4
bpy.ops.mesh.primitive_cylinder_add(radius=0.00255, depth=0.0062, vertices=64, location=(0.0095, -0.0035, 0.0102))
obj = bpy.context.active_object
obj.name = 'Top_Magnet_R1C4'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.00035
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_Magnet_R1C5
bpy.ops.mesh.primitive_cylinder_add(radius=0.0042, depth=0.0062, vertices=64, location=(0.019, -0.0035, 0.0102))
obj = bpy.context.active_object
obj.name = 'Top_Magnet_R1C5'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.0005
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_Magnet_R2C1
bpy.ops.mesh.primitive_cylinder_add(radius=0.0042, depth=0.0062, vertices=64, location=(-0.019, -0.0035, -0.0102))
obj = bpy.context.active_object
obj.name = 'Top_Magnet_R2C1'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.0005
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_Magnet_R2C2
bpy.ops.mesh.primitive_cylinder_add(radius=0.00255, depth=0.0062, vertices=64, location=(-0.0095, -0.0035, -0.0102))
obj = bpy.context.active_object
obj.name = 'Top_Magnet_R2C2'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.00035
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_Magnet_R2C3
bpy.ops.mesh.primitive_cylinder_add(radius=0.00255, depth=0.0062, vertices=64, location=(0.0, -0.0035, -0.0102))
obj = bpy.context.active_object
obj.name = 'Top_Magnet_R2C3'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.00035
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_Magnet_R2C4
bpy.ops.mesh.primitive_cylinder_add(radius=0.00255, depth=0.0062, vertices=64, location=(0.0095, -0.0035, -0.0102))
obj = bpy.context.active_object
obj.name = 'Top_Magnet_R2C4'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.00035
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_Magnet_R2C5
bpy.ops.mesh.primitive_cylinder_add(radius=0.0042, depth=0.0062, vertices=64, location=(0.019, -0.0035, -0.0102))
obj = bpy.context.active_object
obj.name = 'Top_Magnet_R2C5'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.0005
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Magnet_R1C1
bpy.ops.mesh.primitive_cylinder_add(radius=0.0042, depth=0.0062, vertices=64, location=(-0.019, 0.0035, 0.0102))
obj = bpy.context.active_object
obj.name = 'Bottom_Magnet_R1C1'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.0005
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Magnet_R1C2
bpy.ops.mesh.primitive_cylinder_add(radius=0.00255, depth=0.0062, vertices=64, location=(-0.0095, 0.0035, 0.0102))
obj = bpy.context.active_object
obj.name = 'Bottom_Magnet_R1C2'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.00035
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Magnet_R1C3
bpy.ops.mesh.primitive_cylinder_add(radius=0.00255, depth=0.0062, vertices=64, location=(0.0, 0.0035, 0.0102))
obj = bpy.context.active_object
obj.name = 'Bottom_Magnet_R1C3'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.00035
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Magnet_R1C4
bpy.ops.mesh.primitive_cylinder_add(radius=0.00255, depth=0.0062, vertices=64, location=(0.0095, 0.0035, 0.0102))
obj = bpy.context.active_object
obj.name = 'Bottom_Magnet_R1C4'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.00035
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Magnet_R1C5
bpy.ops.mesh.primitive_cylinder_add(radius=0.0042, depth=0.0062, vertices=64, location=(0.019, 0.0035, 0.0102))
obj = bpy.context.active_object
obj.name = 'Bottom_Magnet_R1C5'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.0005
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Magnet_R2C1
bpy.ops.mesh.primitive_cylinder_add(radius=0.0042, depth=0.0062, vertices=64, location=(-0.019, 0.0035, -0.0102))
obj = bpy.context.active_object
obj.name = 'Bottom_Magnet_R2C1'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.0005
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Magnet_R2C2
bpy.ops.mesh.primitive_cylinder_add(radius=0.00255, depth=0.0062, vertices=64, location=(-0.0095, 0.0035, -0.0102))
obj = bpy.context.active_object
obj.name = 'Bottom_Magnet_R2C2'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.00035
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Magnet_R2C3
bpy.ops.mesh.primitive_cylinder_add(radius=0.00255, depth=0.0062, vertices=64, location=(0.0, 0.0035, -0.0102))
obj = bpy.context.active_object
obj.name = 'Bottom_Magnet_R2C3'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.00035
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Magnet_R2C4
bpy.ops.mesh.primitive_cylinder_add(radius=0.00255, depth=0.0062, vertices=64, location=(0.0095, 0.0035, -0.0102))
obj = bpy.context.active_object
obj.name = 'Bottom_Magnet_R2C4'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.00035
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Magnet_R2C5
bpy.ops.mesh.primitive_cylinder_add(radius=0.0042, depth=0.0062, vertices=64, location=(0.019, 0.0035, -0.0102))
obj = bpy.context.active_object
obj.name = 'Bottom_Magnet_R2C5'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)
mod = obj.modifiers.new(name='MagnetEdge', type='BEVEL')
mod.width = 0.0005
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_Fork_Main
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -0.00425, 0.0))
obj = bpy.context.active_object
obj.name = 'Top_Fork_Main'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.015, 0.0003, 0.00055)
if 'mat_BrassFork' in dir():
    obj.data.materials.append(mat_BrassFork)
mod = obj.modifiers.new(name='ForkEdge', type='BEVEL')
mod.width = 0.00025
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_Fork_UpperTine
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.003, -0.00425, 0.0028))
obj = bpy.context.active_object
obj.name = 'Top_Fork_UpperTine'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.011, 0.0003, 0.00045)
if 'mat_BrassFork' in dir():
    obj.data.materials.append(mat_BrassFork)
mod = obj.modifiers.new(name='ForkEdge', type='BEVEL')
mod.width = 0.00025
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_Fork_LowerTine
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.003, -0.00425, -0.0028))
obj = bpy.context.active_object
obj.name = 'Top_Fork_LowerTine'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.011, 0.0003, 0.00045)
if 'mat_BrassFork' in dir():
    obj.data.materials.append(mat_BrassFork)
mod = obj.modifiers.new(name='ForkEdge', type='BEVEL')
mod.width = 0.00025
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_Fork_LeftLink
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.014, -0.00425, 0.0014))
obj = bpy.context.active_object
obj.name = 'Top_Fork_LeftLink'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0005, 0.0003, 0.0014)
if 'mat_BrassFork' in dir():
    obj.data.materials.append(mat_BrassFork)
mod = obj.modifiers.new(name='ForkEdge', type='BEVEL')
mod.width = 0.00025
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_Fork_RightLink
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.014, -0.00425, -0.0014))
obj = bpy.context.active_object
obj.name = 'Top_Fork_RightLink'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0005, 0.0003, 0.0014)
if 'mat_BrassFork' in dir():
    obj.data.materials.append(mat_BrassFork)
mod = obj.modifiers.new(name='ForkEdge', type='BEVEL')
mod.width = 0.00025
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Fork_Main
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.00425, 0.0))
obj = bpy.context.active_object
obj.name = 'Bottom_Fork_Main'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.015, 0.0003, 0.00055)
if 'mat_BrassFork' in dir():
    obj.data.materials.append(mat_BrassFork)
mod = obj.modifiers.new(name='ForkEdge', type='BEVEL')
mod.width = 0.00025
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Fork_UpperTine
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.003, 0.00425, 0.0028))
obj = bpy.context.active_object
obj.name = 'Bottom_Fork_UpperTine'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.011, 0.0003, 0.00045)
if 'mat_BrassFork' in dir():
    obj.data.materials.append(mat_BrassFork)
mod = obj.modifiers.new(name='ForkEdge', type='BEVEL')
mod.width = 0.00025
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Fork_LowerTine
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.003, 0.00425, -0.0028))
obj = bpy.context.active_object
obj.name = 'Bottom_Fork_LowerTine'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.011, 0.0003, 0.00045)
if 'mat_BrassFork' in dir():
    obj.data.materials.append(mat_BrassFork)
mod = obj.modifiers.new(name='ForkEdge', type='BEVEL')
mod.width = 0.00025
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Fork_LeftLink
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.014, 0.00425, 0.0014))
obj = bpy.context.active_object
obj.name = 'Bottom_Fork_LeftLink'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0005, 0.0003, 0.0014)
if 'mat_BrassFork' in dir():
    obj.data.materials.append(mat_BrassFork)
mod = obj.modifiers.new(name='ForkEdge', type='BEVEL')
mod.width = 0.00025
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_Fork_RightLink
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.014, 0.00425, -0.0014))
obj = bpy.context.active_object
obj.name = 'Bottom_Fork_RightLink'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0005, 0.0003, 0.0014)
if 'mat_BrassFork' in dir():
    obj.data.materials.append(mat_BrassFork)
mod = obj.modifiers.new(name='ForkEdge', type='BEVEL')
mod.width = 0.00025
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_RidgeUpper
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -0.00725, 0.0042))
obj = bpy.context.active_object
obj.name = 'Top_RidgeUpper'
obj.rotation_euler = (math.radians(0.0), math.radians(-6.0), math.radians(0.0))
obj.scale = (0.016, 0.00035, 0.0011)
obj.hide_render = True
obj.hide_viewport = True
if 'mat_WhiteMetal' in dir():
    obj.data.materials.append(mat_WhiteMetal)
mod = obj.modifiers.new(name='RidgeEdge', type='BEVEL')
mod.width = 0.00055
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Top_RidgeLower
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -0.00725, -0.0042))
obj = bpy.context.active_object
obj.name = 'Top_RidgeLower'
obj.rotation_euler = (math.radians(0.0), math.radians(6.0), math.radians(0.0))
obj.scale = (0.016, 0.00035, 0.0011)
obj.hide_render = True
obj.hide_viewport = True
if 'mat_WhiteMetal' in dir():
    obj.data.materials.append(mat_WhiteMetal)
mod = obj.modifiers.new(name='RidgeEdge', type='BEVEL')
mod.width = 0.00055
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_RidgeUpper
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.00725, 0.0042))
obj = bpy.context.active_object
obj.name = 'Bottom_RidgeUpper'
obj.rotation_euler = (math.radians(0.0), math.radians(-6.0), math.radians(0.0))
obj.scale = (0.016, 0.00035, 0.0011)
obj.hide_render = True
obj.hide_viewport = True
if 'mat_WhiteMetal' in dir():
    obj.data.materials.append(mat_WhiteMetal)
mod = obj.modifiers.new(name='RidgeEdge', type='BEVEL')
mod.width = 0.00055
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_RidgeLower
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.00725, -0.0042))
obj = bpy.context.active_object
obj.name = 'Bottom_RidgeLower'
obj.rotation_euler = (math.radians(0.0), math.radians(6.0), math.radians(0.0))
obj.scale = (0.016, 0.00035, 0.0011)
obj.hide_render = True
obj.hide_viewport = True
if 'mat_WhiteMetal' in dir():
    obj.data.materials.append(mat_WhiteMetal)
mod = obj.modifiers.new(name='RidgeEdge', type='BEVEL')
mod.width = 0.00055
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: StudioGround
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0, -0.045))
obj = bpy.context.active_object
obj.name = 'StudioGround'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.16, 0.16, 0.005)
if 'mat_StudioFloor' in dir():
    obj.data.materials.append(mat_StudioFloor)
mod = obj.modifiers.new(name='GroundEdge', type='BEVEL')
mod.width = 0.008
mod.segments = 5
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: StudioBackWall
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.09, 0.02))
obj = bpy.context.active_object
obj.name = 'StudioBackWall'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.16, 0.006, 0.12)
obj.hide_render = True
obj.hide_viewport = True
if 'mat_StudioFloor' in dir():
    obj.data.materials.append(mat_StudioFloor)
mod = obj.modifiers.new(name='BackdropEdge', type='BEVEL')
mod.width = 0.012
mod.segments = 6
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: TopDetail_DropLeftBulb
bpy.ops.mesh.primitive_cylinder_add(radius=0.0053, depth=0.006, vertices=64, location=(-0.018, -0.0058, -0.0015))
obj = bpy.context.active_object
obj.name = 'TopDetail_DropLeftBulb'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopDetail_DropLeftNeck
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.0125, -0.0058, 0.0024))
obj = bpy.context.active_object
obj.name = 'TopDetail_DropLeftNeck'
obj.rotation_euler = (math.radians(0.0), math.radians(-32.0), math.radians(0.0))
obj.scale = (0.0063, 0.003, 0.0025)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopDetail_DropLeftTip
bpy.ops.mesh.primitive_cylinder_add(radius=0.0028, depth=0.006, vertices=64, location=(-0.007, -0.0058, 0.0062))
obj = bpy.context.active_object
obj.name = 'TopDetail_DropLeftTip'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopDetail_DropRightBulb
bpy.ops.mesh.primitive_cylinder_add(radius=0.0053, depth=0.006, vertices=64, location=(0.018, -0.0058, 0.0015))
obj = bpy.context.active_object
obj.name = 'TopDetail_DropRightBulb'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopDetail_DropRightNeck
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0125, -0.0058, -0.0024))
obj = bpy.context.active_object
obj.name = 'TopDetail_DropRightNeck'
obj.rotation_euler = (math.radians(0.0), math.radians(-32.0), math.radians(0.0))
obj.scale = (0.0063, 0.003, 0.0025)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopDetail_DropRightTip
bpy.ops.mesh.primitive_cylinder_add(radius=0.0028, depth=0.006, vertices=64, location=(0.007, -0.0058, -0.0062))
obj = bpy.context.active_object
obj.name = 'TopDetail_DropRightTip'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopDetail_SlotURBody
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.011, -0.0058, 0.0102))
obj = bpy.context.active_object
obj.name = 'TopDetail_SlotURBody'
obj.rotation_euler = (math.radians(0.0), math.radians(-10.0), math.radians(0.0))
obj.scale = (0.0058, 0.003, 0.0017)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopDetail_SlotUREndA
bpy.ops.mesh.primitive_cylinder_add(radius=0.00172, depth=0.006, vertices=48, location=(0.0053, -0.0058, 0.0092))
obj = bpy.context.active_object
obj.name = 'TopDetail_SlotUREndA'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopDetail_SlotUREndB
bpy.ops.mesh.primitive_cylinder_add(radius=0.00172, depth=0.006, vertices=48, location=(0.0167, -0.0058, 0.0112))
obj = bpy.context.active_object
obj.name = 'TopDetail_SlotUREndB'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopDetail_SlotBLBody
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.011, -0.0058, -0.0102))
obj = bpy.context.active_object
obj.name = 'TopDetail_SlotBLBody'
obj.rotation_euler = (math.radians(0.0), math.radians(-10.0), math.radians(0.0))
obj.scale = (0.0058, 0.003, 0.0017)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopDetail_SlotBLEndA
bpy.ops.mesh.primitive_cylinder_add(radius=0.00172, depth=0.006, vertices=48, location=(-0.0167, -0.0058, -0.0112))
obj = bpy.context.active_object
obj.name = 'TopDetail_SlotBLEndA'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopDetail_SlotBLEndB
bpy.ops.mesh.primitive_cylinder_add(radius=0.00172, depth=0.006, vertices=48, location=(-0.0053, -0.0058, -0.0092))
obj = bpy.context.active_object
obj.name = 'TopDetail_SlotBLEndB'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopDetail_TriangleTL
bpy.ops.mesh.primitive_cylinder_add(radius=0.0038, depth=0.006, vertices=3, location=(-0.019, -0.0058, 0.0105))
obj = bpy.context.active_object
obj.name = 'TopDetail_TriangleTL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(30.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: TopDetail_TriangleBR
bpy.ops.mesh.primitive_cylinder_add(radius=0.0038, depth=0.006, vertices=3, location=(0.019, -0.0058, -0.0105))
obj = bpy.context.active_object
obj.name = 'TopDetail_TriangleBR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(-30.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomDetail_DropLeftBulb
bpy.ops.mesh.primitive_cylinder_add(radius=0.0053, depth=0.006, vertices=64, location=(-0.018, 0.0058, -0.0015))
obj = bpy.context.active_object
obj.name = 'BottomDetail_DropLeftBulb'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomDetail_DropLeftNeck
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.0125, 0.0058, 0.0024))
obj = bpy.context.active_object
obj.name = 'BottomDetail_DropLeftNeck'
obj.rotation_euler = (math.radians(0.0), math.radians(-32.0), math.radians(0.0))
obj.scale = (0.0063, 0.003, 0.0025)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomDetail_DropLeftTip
bpy.ops.mesh.primitive_cylinder_add(radius=0.0028, depth=0.006, vertices=64, location=(-0.007, 0.0058, 0.0062))
obj = bpy.context.active_object
obj.name = 'BottomDetail_DropLeftTip'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomDetail_DropRightBulb
bpy.ops.mesh.primitive_cylinder_add(radius=0.0053, depth=0.006, vertices=64, location=(0.018, 0.0058, 0.0015))
obj = bpy.context.active_object
obj.name = 'BottomDetail_DropRightBulb'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomDetail_DropRightNeck
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0125, 0.0058, -0.0024))
obj = bpy.context.active_object
obj.name = 'BottomDetail_DropRightNeck'
obj.rotation_euler = (math.radians(0.0), math.radians(-32.0), math.radians(0.0))
obj.scale = (0.0063, 0.003, 0.0025)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomDetail_DropRightTip
bpy.ops.mesh.primitive_cylinder_add(radius=0.0028, depth=0.006, vertices=64, location=(0.007, 0.0058, -0.0062))
obj = bpy.context.active_object
obj.name = 'BottomDetail_DropRightTip'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomDetail_SlotURBody
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.011, 0.0058, 0.0102))
obj = bpy.context.active_object
obj.name = 'BottomDetail_SlotURBody'
obj.rotation_euler = (math.radians(0.0), math.radians(-10.0), math.radians(0.0))
obj.scale = (0.0058, 0.003, 0.0017)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomDetail_SlotUREndA
bpy.ops.mesh.primitive_cylinder_add(radius=0.00172, depth=0.006, vertices=48, location=(0.0053, 0.0058, 0.0092))
obj = bpy.context.active_object
obj.name = 'BottomDetail_SlotUREndA'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomDetail_SlotUREndB
bpy.ops.mesh.primitive_cylinder_add(radius=0.00172, depth=0.006, vertices=48, location=(0.0167, 0.0058, 0.0112))
obj = bpy.context.active_object
obj.name = 'BottomDetail_SlotUREndB'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomDetail_SlotBLBody
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.011, 0.0058, -0.0102))
obj = bpy.context.active_object
obj.name = 'BottomDetail_SlotBLBody'
obj.rotation_euler = (math.radians(0.0), math.radians(-10.0), math.radians(0.0))
obj.scale = (0.0058, 0.003, 0.0017)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomDetail_SlotBLEndA
bpy.ops.mesh.primitive_cylinder_add(radius=0.00172, depth=0.006, vertices=48, location=(-0.0167, 0.0058, -0.0112))
obj = bpy.context.active_object
obj.name = 'BottomDetail_SlotBLEndA'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomDetail_SlotBLEndB
bpy.ops.mesh.primitive_cylinder_add(radius=0.00172, depth=0.006, vertices=48, location=(-0.0053, 0.0058, -0.0092))
obj = bpy.context.active_object
obj.name = 'BottomDetail_SlotBLEndB'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomDetail_TriangleTL
bpy.ops.mesh.primitive_cylinder_add(radius=0.0038, depth=0.006, vertices=3, location=(-0.019, 0.0058, 0.0105))
obj = bpy.context.active_object
obj.name = 'BottomDetail_TriangleTL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(30.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: BottomDetail_TriangleBR
bpy.ops.mesh.primitive_cylinder_add(radius=0.0038, depth=0.006, vertices=3, location=(0.019, 0.0058, -0.0105))
obj = bpy.context.active_object
obj.name = 'BottomDetail_TriangleBR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(-30.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: MiddlePatternPlate
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -0.00425, 0.0))
obj = bpy.context.active_object
obj.name = 'MiddlePatternPlate'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0235, 0.00025, 0.0155)
if 'mat_WhiteMetal' in dir():
    obj.data.materials.append(mat_WhiteMetal)
mod = obj.modifiers.new(name='PatternPlateRadius', type='BEVEL')
mod.width = 0.14
mod.segments = 7
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: PatternScrewCap
bpy.ops.mesh.primitive_cylinder_add(radius=0.0022, depth=0.0005, vertices=64, location=(0.0, -0.00472, 0.0))
obj = bpy.context.active_object
obj.name = 'PatternScrewCap'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_MagnetSteel' in dir():
    obj.data.materials.append(mat_MagnetSteel)

# Object: PatternScrewInset
bpy.ops.mesh.primitive_cylinder_add(radius=0.00072, depth=0.0002, vertices=32, location=(0.0, -0.00502, 0.0))
obj = bpy.context.active_object
obj.name = 'PatternScrewInset'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_DarkCarrier' in dir():
    obj.data.materials.append(mat_DarkCarrier)

# Object: PatternGroove_TL0_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.0175, -0.00505, 0.004))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TL0_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TL0_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.009, -0.00505, 0.0034))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TL0_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(6.842773412630941), math.radians(0.0))
obj.scale = (0.0050359, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TR0_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.009, -0.00505, 0.0034))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TR0_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(-6.842773412630941), math.radians(0.0))
obj.scale = (0.0050359, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TR0_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0175, -0.00505, 0.004))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TR0_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BL0_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.0175, -0.00505, -0.004))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BL0_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BL0_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.009, -0.00505, -0.0034))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BL0_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(-6.842773412630941), math.radians(0.0))
obj.scale = (0.0050359, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BR0_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.009, -0.00505, -0.0034))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BR0_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(6.842773412630941), math.radians(0.0))
obj.scale = (0.0050359, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BR0_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0175, -0.00505, -0.004))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BR0_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TL1_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.0175, -0.00505, 0.006))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TL1_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TL1_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.009, -0.00505, 0.004975))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TL1_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(11.585126224855046), math.radians(0.0))
obj.scale = (0.005104, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TR1_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.009, -0.00505, 0.004975))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TR1_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(-11.585126224855046), math.radians(0.0))
obj.scale = (0.005104, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TR1_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0175, -0.00505, 0.006))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TR1_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BL1_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.0175, -0.00505, -0.006))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BL1_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BL1_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.009, -0.00505, -0.004975))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BL1_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(-11.585126224855046), math.radians(0.0))
obj.scale = (0.005104, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BR1_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.009, -0.00505, -0.004975))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BR1_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(11.585126224855046), math.radians(0.0))
obj.scale = (0.005104, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BR1_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0175, -0.00505, -0.006))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BR1_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TL2_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.0175, -0.00505, 0.008))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TL2_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TL2_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.009, -0.00505, 0.00655))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TL2_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(16.17215901578255), math.radians(0.0))
obj.scale = (0.005206, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TR2_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.009, -0.00505, 0.00655))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TR2_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(-16.17215901578255), math.radians(0.0))
obj.scale = (0.005206, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TR2_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0175, -0.00505, 0.008))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TR2_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BL2_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.0175, -0.00505, -0.008))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BL2_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BL2_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.009, -0.00505, -0.00655))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BL2_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(-16.17215901578255), math.radians(0.0))
obj.scale = (0.005206, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BR2_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.009, -0.00505, -0.00655))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BR2_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(16.17215901578255), math.radians(0.0))
obj.scale = (0.005206, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BR2_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0175, -0.00505, -0.008))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BR2_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TL3_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.0175, -0.00505, 0.01))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TL3_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TL3_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.009, -0.00505, 0.008125))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TL3_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(20.556045219583464), math.radians(0.0))
obj.scale = (0.00534, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TR3_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.009, -0.00505, 0.008125))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TR3_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(-20.556045219583464), math.radians(0.0))
obj.scale = (0.00534, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TR3_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0175, -0.00505, 0.01))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TR3_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BL3_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.0175, -0.00505, -0.01))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BL3_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BL3_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.009, -0.00505, -0.008125))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BL3_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(-20.556045219583464), math.radians(0.0))
obj.scale = (0.00534, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BR3_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.009, -0.00505, -0.008125))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BR3_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(20.556045219583464), math.radians(0.0))
obj.scale = (0.00534, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BR3_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0175, -0.00505, -0.01))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BR3_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TL4_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.0175, -0.00505, 0.012))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TL4_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TL4_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.009, -0.00505, 0.0097))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TL4_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(24.70243022777131), math.radians(0.0))
obj.scale = (0.0055036, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TR4_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.009, -0.00505, 0.0097))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TR4_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(-24.70243022777131), math.radians(0.0))
obj.scale = (0.0055036, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TR4_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0175, -0.00505, 0.012))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TR4_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BL4_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.0175, -0.00505, -0.012))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BL4_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BL4_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.009, -0.00505, -0.0097))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BL4_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(-24.70243022777131), math.radians(0.0))
obj.scale = (0.0055036, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BR4_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.009, -0.00505, -0.0097))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BR4_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(24.70243022777131), math.radians(0.0))
obj.scale = (0.0055036, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BR4_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0175, -0.00505, -0.012))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BR4_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TL5_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.0175, -0.00505, 0.014))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TL5_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TL5_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.009, -0.00505, 0.011275))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TL5_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(28.5903840607906), math.radians(0.0))
obj.scale = (0.0056944, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TR5_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.009, -0.00505, 0.011275))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TR5_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(-28.5903840607906), math.radians(0.0))
obj.scale = (0.0056944, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_TR5_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0175, -0.00505, 0.014))
obj = bpy.context.active_object
obj.name = 'PatternGroove_TR5_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BL5_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.0175, -0.00505, -0.014))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BL5_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BL5_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.009, -0.00505, -0.011275))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BL5_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(-28.5903840607906), math.radians(0.0))
obj.scale = (0.0056944, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BR5_Diag
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.009, -0.00505, -0.011275))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BR5_Diag'
obj.rotation_euler = (math.radians(0.0), math.radians(28.5903840607906), math.radians(0.0))
obj.scale = (0.0056944, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: PatternGroove_BR5_Outer
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0175, -0.00505, -0.014))
obj = bpy.context.active_object
obj.name = 'PatternGroove_BR5_Outer'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.0035, 0.00018, 0.00028)
if 'mat_PatternSilver' in dir():
    obj.data.materials.append(mat_PatternSilver)

# Object: Top_OrnamentalShell
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -0.0058, 0.0))
obj = bpy.context.active_object
obj.name = 'Top_OrnamentalShell'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.026, 0.0012, 0.018)
if 'mat_WhiteMetal' in dir():
    obj.data.materials.append(mat_WhiteMetal)
mod = obj.modifiers.new(name='OuterRadius', type='BEVEL')
mod.width = 0.17
mod.segments = 8
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599
mod = obj.modifiers.new(name='Cut_TopDetail_DropLeftBulb', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_DropLeftBulb')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_DropLeftNeck', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_DropLeftNeck')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_DropLeftTip', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_DropLeftTip')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_DropRightBulb', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_DropRightBulb')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_DropRightNeck', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_DropRightNeck')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_DropRightTip', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_DropRightTip')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_SlotURBody', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_SlotURBody')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_SlotUREndA', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_SlotUREndA')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_SlotUREndB', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_SlotUREndB')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_SlotBLBody', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_SlotBLBody')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_SlotBLEndA', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_SlotBLEndA')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_SlotBLEndB', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_SlotBLEndB')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_TriangleTL', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_TriangleTL')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_TopDetail_TriangleBR', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopDetail_TriangleBR')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='DetailEdgeSoftness', type='BEVEL')
mod.width = 0.025
mod.segments = 3
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_OrnamentalShell
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0058, 0.0))
obj = bpy.context.active_object
obj.name = 'Bottom_OrnamentalShell'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.026, 0.0012, 0.018)
if 'mat_WhiteMetal' in dir():
    obj.data.materials.append(mat_WhiteMetal)
mod = obj.modifiers.new(name='OuterRadius', type='BEVEL')
mod.width = 0.17
mod.segments = 8
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599
mod = obj.modifiers.new(name='Cut_BottomDetail_DropLeftBulb', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_DropLeftBulb')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_DropLeftNeck', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_DropLeftNeck')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_DropLeftTip', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_DropLeftTip')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_DropRightBulb', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_DropRightBulb')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_DropRightNeck', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_DropRightNeck')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_DropRightTip', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_DropRightTip')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_SlotURBody', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_SlotURBody')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_SlotUREndA', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_SlotUREndA')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_SlotUREndB', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_SlotUREndB')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_SlotBLBody', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_SlotBLBody')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_SlotBLEndA', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_SlotBLEndA')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_SlotBLEndB', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_SlotBLEndB')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_TriangleTL', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_TriangleTL')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='Cut_BottomDetail_TriangleBR', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomDetail_TriangleBR')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='DetailEdgeSoftness', type='BEVEL')
mod.width = 0.025
mod.segments = 3
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599


# ── Cameras ─────────────────────────────────────────────────
cam_data = bpy.data.cameras.new(name='HeroCamera')
cam_data.type = 'PERSP'
cam_data.lens = 58.0
cam_data.sensor_width = 36.0
cam_data.clip_start = 0.1
cam_data.clip_end = 1000.0
cam_obj = bpy.data.objects.new('HeroCamera', cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (0.14, -0.28, 0.07)
cam_obj.rotation_euler = (math.radians(76.0), math.radians(0.0), math.radians(27.0))
scene.camera = cam_obj


# ── Lights ──────────────────────────────────────────────────
light_data = bpy.data.lights.new(name='KeySoftbox', type='AREA')
light_data.energy = 7.0
light_data.color = (1.0, 0.86, 0.74)
light_data.size = 0.12
light_data.size_y = 0.09
light_data.shape = 'RECTANGLE'
light_obj = bpy.data.objects.new('KeySoftbox', light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (-0.075, -0.105, 0.138)
light_obj.rotation_euler = (math.radians(48.0), math.radians(0.0), math.radians(-32.0))

light_data = bpy.data.lights.new(name='FillSoftbox', type='AREA')
light_data.energy = 2.5
light_data.color = (0.55, 0.72, 1.0)
light_data.size = 0.1
light_data.size_y = 0.08
light_data.shape = 'RECTANGLE'
light_obj = bpy.data.objects.new('FillSoftbox', light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (0.105, -0.063, 0.025)
light_obj.rotation_euler = (math.radians(82.0), math.radians(0.0), math.radians(58.0))

light_data = bpy.data.lights.new(name='RimSoftbox', type='AREA')
light_data.energy = 4.5
light_data.color = (1.0, 0.72, 0.46)
light_data.size = 0.1
light_data.size_y = 0.08
light_data.shape = 'RECTANGLE'
light_obj = bpy.data.objects.new('RimSoftbox', light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (-0.055, 0.025, 0.12)
light_obj.rotation_euler = (math.radians(35.0), math.radians(0.0), math.radians(-18.0))


# ── Keyframes ───────────────────────────────────────────────
obj = bpy.data.objects.get('TopShell_Root')
if obj:
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopCarrier_Root')
if obj:
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopMagnets_Root')
if obj:
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopForks_Root')
if obj:
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopContact_Root')
if obj:
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomShell_Root')
if obj:
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomCarrier_Root')
if obj:
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomMagnets_Root')
if obj:
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomForks_Root')
if obj:
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomContact_Root')
if obj:
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0, 0.0, 0.0)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopCut_SlotUpper')
if obj:
    obj.location = (0.0, -0.0058, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.04, -0.0458, 0.0452)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopCut_SlotLower')
if obj:
    obj.location = (0.0, -0.0058, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.04, -0.0458, 0.0248)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopCut_BigTL')
if obj:
    obj.location = (-0.019, -0.0058, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.059, -0.0458, 0.0452)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopCut_BigTR')
if obj:
    obj.location = (0.019, -0.0058, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.021, -0.0458, 0.0452)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopCut_BigBL')
if obj:
    obj.location = (-0.019, -0.0058, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.059, -0.0458, 0.0248)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopCut_BigBR')
if obj:
    obj.location = (0.019, -0.0058, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.021, -0.0458, 0.0248)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomCut_SlotUpper')
if obj:
    obj.location = (0.0, 0.0058, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.04, 0.0458, -0.0248)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomCut_SlotLower')
if obj:
    obj.location = (0.0, 0.0058, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.04, 0.0458, -0.0452)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomCut_BigTL')
if obj:
    obj.location = (-0.019, 0.0058, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.021, 0.0458, -0.0248)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomCut_BigTR')
if obj:
    obj.location = (0.019, 0.0058, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.059, 0.0458, -0.0248)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomCut_BigBL')
if obj:
    obj.location = (-0.019, 0.0058, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.021, 0.0458, -0.0452)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomCut_BigBR')
if obj:
    obj.location = (0.019, 0.0058, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.059, 0.0458, -0.0452)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_MetalShell')
if obj:
    obj.location = (0.0, -0.0058, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.04, -0.0458, 0.035)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_MetalShell')
if obj:
    obj.location = (0.0, 0.0058, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.04, 0.0458, -0.035)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_MagnetCarrier')
if obj:
    obj.location = (0.0, -0.0025, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.012, -0.0165, 0.008)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_MagnetCarrier')
if obj:
    obj.location = (0.0, 0.0025, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.012, 0.0165, -0.008)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_LowFrictionContact')
if obj:
    obj.location = (0.0, -0.00015, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.005, -0.00615, 0.003)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_LowFrictionContact')
if obj:
    obj.location = (0.0, 0.00015, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.005, 0.00615, -0.003)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopCut_SideLeft')
if obj:
    obj.location = (-0.019, -0.0058, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.059, -0.0458, 0.035)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopCut_SideRight')
if obj:
    obj.location = (0.019, -0.0058, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.021, -0.0458, 0.035)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomCut_SideLeft')
if obj:
    obj.location = (-0.019, 0.0058, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.021, 0.0458, -0.035)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomCut_SideRight')
if obj:
    obj.location = (0.019, 0.0058, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.059, 0.0458, -0.035)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Magnet_R1C1')
if obj:
    obj.location = (-0.019, -0.0035, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.049, -0.0335, 0.0352)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Magnet_R1C2')
if obj:
    obj.location = (-0.0095, -0.0035, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0395, -0.0335, 0.0352)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Magnet_R1C3')
if obj:
    obj.location = (0.0, -0.0035, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.03, -0.0335, 0.0352)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Magnet_R1C4')
if obj:
    obj.location = (0.0095, -0.0035, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0205, -0.0335, 0.0352)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Magnet_R1C5')
if obj:
    obj.location = (0.019, -0.0035, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.011, -0.0335, 0.0352)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Magnet_R2C1')
if obj:
    obj.location = (-0.019, -0.0035, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.049, -0.0335, 0.0148)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Magnet_R2C2')
if obj:
    obj.location = (-0.0095, -0.0035, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0395, -0.0335, 0.0148)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Magnet_R2C3')
if obj:
    obj.location = (0.0, -0.0035, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.03, -0.0335, 0.0148)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Magnet_R2C4')
if obj:
    obj.location = (0.0095, -0.0035, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0205, -0.0335, 0.0148)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Magnet_R2C5')
if obj:
    obj.location = (0.019, -0.0035, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.011, -0.0335, 0.0148)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Magnet_R1C1')
if obj:
    obj.location = (-0.019, 0.0035, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.011, 0.0335, -0.0148)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Magnet_R1C2')
if obj:
    obj.location = (-0.0095, 0.0035, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0205, 0.0335, -0.0148)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Magnet_R1C3')
if obj:
    obj.location = (0.0, 0.0035, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.03, 0.0335, -0.0148)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Magnet_R1C4')
if obj:
    obj.location = (0.0095, 0.0035, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0395, 0.0335, -0.0148)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Magnet_R1C5')
if obj:
    obj.location = (0.019, 0.0035, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.049, 0.0335, -0.0148)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Magnet_R2C1')
if obj:
    obj.location = (-0.019, 0.0035, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.011, 0.0335, -0.0352)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Magnet_R2C2')
if obj:
    obj.location = (-0.0095, 0.0035, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0205, 0.0335, -0.0352)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Magnet_R2C3')
if obj:
    obj.location = (0.0, 0.0035, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.03, 0.0335, -0.0352)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Magnet_R2C4')
if obj:
    obj.location = (0.0095, 0.0035, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0395, 0.0335, -0.0352)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Magnet_R2C5')
if obj:
    obj.location = (0.019, 0.0035, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.049, 0.0335, -0.0352)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Fork_Main')
if obj:
    obj.location = (0.0, -0.00425, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.02, -0.02625, 0.015)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Fork_UpperTine')
if obj:
    obj.location = (-0.003, -0.00425, 0.0028)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.023, -0.02625, 0.0178)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Fork_LowerTine')
if obj:
    obj.location = (0.003, -0.00425, -0.0028)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.017, -0.02625, 0.0122)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Fork_LeftLink')
if obj:
    obj.location = (-0.014, -0.00425, 0.0014)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.034, -0.02625, 0.0164)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_Fork_RightLink')
if obj:
    obj.location = (0.014, -0.00425, -0.0014)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.006, -0.02625, 0.0136)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Fork_Main')
if obj:
    obj.location = (0.0, 0.00425, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.02, 0.02625, -0.015)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Fork_UpperTine')
if obj:
    obj.location = (-0.003, 0.00425, 0.0028)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.017, 0.02625, -0.0122)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Fork_LowerTine')
if obj:
    obj.location = (0.003, 0.00425, -0.0028)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.023, 0.02625, -0.0178)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Fork_LeftLink')
if obj:
    obj.location = (-0.014, 0.00425, 0.0014)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.006, 0.02625, -0.0136)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_Fork_RightLink')
if obj:
    obj.location = (0.014, 0.00425, -0.0014)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.034, 0.02625, -0.0164)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_RidgeUpper')
if obj:
    obj.location = (0.0, -0.00725, 0.0042)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.04, -0.04725, 0.0392)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_RidgeLower')
if obj:
    obj.location = (0.0, -0.00725, -0.0042)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.04, -0.04725, 0.0308)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_RidgeUpper')
if obj:
    obj.location = (0.0, 0.00725, 0.0042)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.04, 0.04725, -0.0308)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_RidgeLower')
if obj:
    obj.location = (0.0, 0.00725, -0.0042)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.04, 0.04725, -0.0392)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopDetail_DropLeftBulb')
if obj:
    obj.location = (-0.018, -0.0058, -0.0015)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.058, -0.0458, 0.0335)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopDetail_DropLeftNeck')
if obj:
    obj.location = (-0.0125, -0.0058, 0.0024)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0525, -0.0458, 0.0374)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopDetail_DropLeftTip')
if obj:
    obj.location = (-0.007, -0.0058, 0.0062)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.047, -0.0458, 0.0412)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopDetail_DropRightBulb')
if obj:
    obj.location = (0.018, -0.0058, 0.0015)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.022, -0.0458, 0.0365)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopDetail_DropRightNeck')
if obj:
    obj.location = (0.0125, -0.0058, -0.0024)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0275, -0.0458, 0.0326)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopDetail_DropRightTip')
if obj:
    obj.location = (0.007, -0.0058, -0.0062)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.033, -0.0458, 0.0288)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopDetail_SlotURBody')
if obj:
    obj.location = (0.011, -0.0058, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.029, -0.0458, 0.0452)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopDetail_SlotUREndA')
if obj:
    obj.location = (0.0053, -0.0058, 0.0092)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0347, -0.0458, 0.0442)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopDetail_SlotUREndB')
if obj:
    obj.location = (0.0167, -0.0058, 0.0112)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0233, -0.0458, 0.0462)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopDetail_SlotBLBody')
if obj:
    obj.location = (-0.011, -0.0058, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.051, -0.0458, 0.0248)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopDetail_SlotBLEndA')
if obj:
    obj.location = (-0.0167, -0.0058, -0.0112)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0567, -0.0458, 0.0238)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopDetail_SlotBLEndB')
if obj:
    obj.location = (-0.0053, -0.0058, -0.0092)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0453, -0.0458, 0.0258)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopDetail_TriangleTL')
if obj:
    obj.location = (-0.019, -0.0058, 0.0105)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.059, -0.0458, 0.0455)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('TopDetail_TriangleBR')
if obj:
    obj.location = (0.019, -0.0058, -0.0105)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.021, -0.0458, 0.0245)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomDetail_DropLeftBulb')
if obj:
    obj.location = (-0.018, 0.0058, -0.0015)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.022, 0.0458, -0.0365)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomDetail_DropLeftNeck')
if obj:
    obj.location = (-0.0125, 0.0058, 0.0024)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0275, 0.0458, -0.0326)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomDetail_DropLeftTip')
if obj:
    obj.location = (-0.007, 0.0058, 0.0062)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.033, 0.0458, -0.0288)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomDetail_DropRightBulb')
if obj:
    obj.location = (0.018, 0.0058, 0.0015)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.058, 0.0458, -0.0335)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomDetail_DropRightNeck')
if obj:
    obj.location = (0.0125, 0.0058, -0.0024)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0525, 0.0458, -0.0374)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomDetail_DropRightTip')
if obj:
    obj.location = (0.007, 0.0058, -0.0062)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.047, 0.0458, -0.0412)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomDetail_SlotURBody')
if obj:
    obj.location = (0.011, 0.0058, 0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.051, 0.0458, -0.0248)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomDetail_SlotUREndA')
if obj:
    obj.location = (0.0053, 0.0058, 0.0092)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0453, 0.0458, -0.0258)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomDetail_SlotUREndB')
if obj:
    obj.location = (0.0167, 0.0058, 0.0112)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0567, 0.0458, -0.0238)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomDetail_SlotBLBody')
if obj:
    obj.location = (-0.011, 0.0058, -0.0102)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.029, 0.0458, -0.0452)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomDetail_SlotBLEndA')
if obj:
    obj.location = (-0.0167, 0.0058, -0.0112)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0233, 0.0458, -0.0462)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomDetail_SlotBLEndB')
if obj:
    obj.location = (-0.0053, 0.0058, -0.0092)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.0347, 0.0458, -0.0442)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomDetail_TriangleTL')
if obj:
    obj.location = (-0.019, 0.0058, 0.0105)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.021, 0.0458, -0.0245)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('BottomDetail_TriangleBR')
if obj:
    obj.location = (0.019, 0.0058, -0.0105)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.059, 0.0458, -0.0455)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('MiddlePatternPlate')
if obj:
    obj.location = (0.0, -0.00425, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.024, -0.03025, 0.019)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternScrewCap')
if obj:
    obj.location = (0.0, -0.00472, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.024, -0.03072, 0.019)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternScrewInset')
if obj:
    obj.location = (0.0, -0.00502, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.024, -0.03102, 0.019)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TL0_Outer')
if obj:
    obj.location = (-0.0175, -0.00505, 0.004)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0415, -0.03105, 0.023)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TL0_Diag')
if obj:
    obj.location = (-0.009, -0.00505, 0.0034)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.033, -0.03105, 0.0224)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TR0_Diag')
if obj:
    obj.location = (0.009, -0.00505, 0.0034)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.015, -0.03105, 0.0224)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TR0_Outer')
if obj:
    obj.location = (0.0175, -0.00505, 0.004)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0065, -0.03105, 0.023)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BL0_Outer')
if obj:
    obj.location = (-0.0175, -0.00505, -0.004)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0415, -0.03105, 0.015)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BL0_Diag')
if obj:
    obj.location = (-0.009, -0.00505, -0.0034)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.033, -0.03105, 0.0156)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BR0_Diag')
if obj:
    obj.location = (0.009, -0.00505, -0.0034)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.015, -0.03105, 0.0156)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BR0_Outer')
if obj:
    obj.location = (0.0175, -0.00505, -0.004)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0065, -0.03105, 0.015)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TL1_Outer')
if obj:
    obj.location = (-0.0175, -0.00505, 0.006)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0415, -0.03105, 0.025)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TL1_Diag')
if obj:
    obj.location = (-0.009, -0.00505, 0.004975)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.033, -0.03105, 0.023975)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TR1_Diag')
if obj:
    obj.location = (0.009, -0.00505, 0.004975)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.015, -0.03105, 0.023975)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TR1_Outer')
if obj:
    obj.location = (0.0175, -0.00505, 0.006)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0065, -0.03105, 0.025)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BL1_Outer')
if obj:
    obj.location = (-0.0175, -0.00505, -0.006)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0415, -0.03105, 0.013)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BL1_Diag')
if obj:
    obj.location = (-0.009, -0.00505, -0.004975)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.033, -0.03105, 0.014025)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BR1_Diag')
if obj:
    obj.location = (0.009, -0.00505, -0.004975)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.015, -0.03105, 0.014025)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BR1_Outer')
if obj:
    obj.location = (0.0175, -0.00505, -0.006)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0065, -0.03105, 0.013)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TL2_Outer')
if obj:
    obj.location = (-0.0175, -0.00505, 0.008)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0415, -0.03105, 0.027)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TL2_Diag')
if obj:
    obj.location = (-0.009, -0.00505, 0.00655)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.033, -0.03105, 0.02555)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TR2_Diag')
if obj:
    obj.location = (0.009, -0.00505, 0.00655)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.015, -0.03105, 0.02555)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TR2_Outer')
if obj:
    obj.location = (0.0175, -0.00505, 0.008)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0065, -0.03105, 0.027)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BL2_Outer')
if obj:
    obj.location = (-0.0175, -0.00505, -0.008)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0415, -0.03105, 0.011)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BL2_Diag')
if obj:
    obj.location = (-0.009, -0.00505, -0.00655)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.033, -0.03105, 0.01245)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BR2_Diag')
if obj:
    obj.location = (0.009, -0.00505, -0.00655)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.015, -0.03105, 0.01245)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BR2_Outer')
if obj:
    obj.location = (0.0175, -0.00505, -0.008)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0065, -0.03105, 0.011)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TL3_Outer')
if obj:
    obj.location = (-0.0175, -0.00505, 0.01)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0415, -0.03105, 0.029)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TL3_Diag')
if obj:
    obj.location = (-0.009, -0.00505, 0.008125)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.033, -0.03105, 0.027125)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TR3_Diag')
if obj:
    obj.location = (0.009, -0.00505, 0.008125)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.015, -0.03105, 0.027125)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TR3_Outer')
if obj:
    obj.location = (0.0175, -0.00505, 0.01)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0065, -0.03105, 0.029)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BL3_Outer')
if obj:
    obj.location = (-0.0175, -0.00505, -0.01)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0415, -0.03105, 0.009)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BL3_Diag')
if obj:
    obj.location = (-0.009, -0.00505, -0.008125)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.033, -0.03105, 0.010875)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BR3_Diag')
if obj:
    obj.location = (0.009, -0.00505, -0.008125)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.015, -0.03105, 0.010875)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BR3_Outer')
if obj:
    obj.location = (0.0175, -0.00505, -0.01)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0065, -0.03105, 0.009)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TL4_Outer')
if obj:
    obj.location = (-0.0175, -0.00505, 0.012)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0415, -0.03105, 0.031)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TL4_Diag')
if obj:
    obj.location = (-0.009, -0.00505, 0.0097)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.033, -0.03105, 0.0287)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TR4_Diag')
if obj:
    obj.location = (0.009, -0.00505, 0.0097)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.015, -0.03105, 0.0287)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TR4_Outer')
if obj:
    obj.location = (0.0175, -0.00505, 0.012)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0065, -0.03105, 0.031)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BL4_Outer')
if obj:
    obj.location = (-0.0175, -0.00505, -0.012)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0415, -0.03105, 0.007)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BL4_Diag')
if obj:
    obj.location = (-0.009, -0.00505, -0.0097)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.033, -0.03105, 0.0093)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BR4_Diag')
if obj:
    obj.location = (0.009, -0.00505, -0.0097)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.015, -0.03105, 0.0093)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BR4_Outer')
if obj:
    obj.location = (0.0175, -0.00505, -0.012)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0065, -0.03105, 0.007)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TL5_Outer')
if obj:
    obj.location = (-0.0175, -0.00505, 0.014)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0415, -0.03105, 0.033)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TL5_Diag')
if obj:
    obj.location = (-0.009, -0.00505, 0.011275)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.033, -0.03105, 0.030275)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TR5_Diag')
if obj:
    obj.location = (0.009, -0.00505, 0.011275)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.015, -0.03105, 0.030275)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_TR5_Outer')
if obj:
    obj.location = (0.0175, -0.00505, 0.014)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0065, -0.03105, 0.033)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BL5_Outer')
if obj:
    obj.location = (-0.0175, -0.00505, -0.014)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0415, -0.03105, 0.005)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BL5_Diag')
if obj:
    obj.location = (-0.009, -0.00505, -0.011275)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.033, -0.03105, 0.007725)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BR5_Diag')
if obj:
    obj.location = (0.009, -0.00505, -0.011275)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.015, -0.03105, 0.007725)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('PatternGroove_BR5_Outer')
if obj:
    obj.location = (0.0175, -0.00505, -0.014)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.0065, -0.03105, 0.005)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Top_OrnamentalShell')
if obj:
    obj.location = (0.0, -0.0058, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (-0.04, -0.0458, 0.035)
    obj.keyframe_insert(data_path='location', frame=40)

obj = bpy.data.objects.get('Bottom_OrnamentalShell')
if obj:
    obj.location = (0.0, 0.0058, 0.0)
    obj.keyframe_insert(data_path='location', frame=1)
    obj.location = (0.04, 0.0458, -0.035)
    obj.keyframe_insert(data_path='location', frame=40)


# ── Render Output ───────────────────────────────────────────
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = r'/tmp/fidgeting_app_cli/Artifacts/UnboundSlider/WhiteModel_2026-08-11/08_DetailExploded.png'
scene.frame_set(40)

# Render single frame
bpy.ops.render.render(write_still=True)

print('Render complete: /tmp/fidgeting_app_cli/Artifacts/UnboundSlider/WhiteModel_2026-08-11/08_DetailExploded.png')
