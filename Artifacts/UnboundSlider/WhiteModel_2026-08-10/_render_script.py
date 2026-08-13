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
if 'mat_WhiteMetal' in dir():
    obj.data.materials.append(mat_WhiteMetal)
mod = obj.modifiers.new(name='OuterRadius', type='BEVEL')
mod.width = 0.17
mod.segments = 8
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599
mod = obj.modifiers.new(name='CutSlotUpper', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopCut_SlotUpper')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='CutSlotLower', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopCut_SlotLower')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='CutBigTL', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopCut_BigTL')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='CutBigTR', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopCut_BigTR')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='CutBigBL', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopCut_BigBL')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='CutBigBR', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopCut_BigBR')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='CutEdgeSoftness', type='BEVEL')
mod.width = 0.00035
mod.segments = 3
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599
mod = obj.modifiers.new(name='CutSideLeft', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopCut_SideLeft')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='CutSideRight', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('TopCut_SideRight')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='SideCutSoftness', type='BEVEL')
mod.width = 0.0003
mod.segments = 3
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Bottom_MetalShell
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.0058, 0.0))
obj = bpy.context.active_object
obj.name = 'Bottom_MetalShell'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.026, 0.0012, 0.018)
if 'mat_WhiteMetal' in dir():
    obj.data.materials.append(mat_WhiteMetal)
mod = obj.modifiers.new(name='OuterRadius', type='BEVEL')
mod.width = 0.17
mod.segments = 8
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599
mod = obj.modifiers.new(name='CutSlotUpper', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomCut_SlotUpper')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='CutSlotLower', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomCut_SlotLower')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='CutBigTL', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomCut_BigTL')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='CutBigTR', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomCut_BigTR')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='CutBigBL', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomCut_BigBL')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='CutBigBR', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomCut_BigBR')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='CutEdgeSoftness', type='BEVEL')
mod.width = 0.00035
mod.segments = 3
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599
mod = obj.modifiers.new(name='CutSideLeft', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomCut_SideLeft')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='CutSideRight', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('BottomCut_SideRight')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='SideCutSoftness', type='BEVEL')
mod.width = 0.0003
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
obj.hide_render = True
obj.hide_viewport = True
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


# ── Cameras ─────────────────────────────────────────────────
cam_data = bpy.data.cameras.new(name='HeroCamera')
cam_data.type = 'PERSP'
cam_data.lens = 58.0
cam_data.sensor_width = 36.0
cam_data.clip_start = 0.1
cam_data.clip_end = 1000.0
cam_obj = bpy.data.objects.new('HeroCamera', cam_data)
bpy.context.collection.objects.link(cam_obj)
cam_obj.location = (0.1, -0.18, -0.035)
cam_obj.rotation_euler = (math.radians(101.0), math.radians(0.0), math.radians(29.0))
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


# ── Render Output ───────────────────────────────────────────
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = r'/tmp/fidgeting_app_cli/Artifacts/UnboundSlider/WhiteModel_2026-08-10/05_LowAngle.png'
scene.frame_set(1)

# Render single frame
bpy.ops.render.render(write_still=True)

print('Render complete: /tmp/fidgeting_app_cli/Artifacts/UnboundSlider/WhiteModel_2026-08-10/05_LowAngle.png')
