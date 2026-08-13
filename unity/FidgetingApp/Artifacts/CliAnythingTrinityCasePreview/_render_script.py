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
scene.frame_end = 250
scene.frame_current = 1
scene.render.fps = 24

# ── Render Settings ─────────────────────────────────────────
scene.render.engine = 'CYCLES'
scene.render.resolution_x = 720
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.render.film_transparent = False
scene.cycles.samples = 24
scene.cycles.use_denoising = True

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
mat_AcrylicClear = bpy.data.materials.new(name='AcrylicClear')
mat_AcrylicClear.use_nodes = True
bsdf_AcrylicClear = mat_AcrylicClear.node_tree.nodes.get('Principled BSDF')
if bsdf_AcrylicClear:
    bsdf_AcrylicClear.inputs['Base Color'].default_value = (0.58, 0.82, 1.0, 0.22)
    bsdf_AcrylicClear.inputs['Metallic'].default_value = 0.0
    bsdf_AcrylicClear.inputs['Roughness'].default_value = 0.07
    bsdf_AcrylicClear.inputs['Specular IOR Level'].default_value = 0.65
    bsdf_AcrylicClear.inputs['Alpha'].default_value = 0.22

mat_BlackFoam = bpy.data.materials.new(name='BlackFoam')
mat_BlackFoam.use_nodes = True
bsdf_BlackFoam = mat_BlackFoam.node_tree.nodes.get('Principled BSDF')
if bsdf_BlackFoam:
    bsdf_BlackFoam.inputs['Base Color'].default_value = (0.004, 0.005, 0.007, 1.0)
    bsdf_BlackFoam.inputs['Metallic'].default_value = 0.0
    bsdf_BlackFoam.inputs['Roughness'].default_value = 0.96
    bsdf_BlackFoam.inputs['Specular IOR Level'].default_value = 0.12
    bsdf_BlackFoam.inputs['Alpha'].default_value = 1.0

mat_BlackPolymer = bpy.data.materials.new(name='BlackPolymer')
mat_BlackPolymer.use_nodes = True
bsdf_BlackPolymer = mat_BlackPolymer.node_tree.nodes.get('Principled BSDF')
if bsdf_BlackPolymer:
    bsdf_BlackPolymer.inputs['Base Color'].default_value = (0.012, 0.015, 0.022, 1.0)
    bsdf_BlackPolymer.inputs['Metallic'].default_value = 0.12
    bsdf_BlackPolymer.inputs['Roughness'].default_value = 0.36
    bsdf_BlackPolymer.inputs['Specular IOR Level'].default_value = 0.38
    bsdf_BlackPolymer.inputs['Alpha'].default_value = 1.0

mat_BrushedChrome = bpy.data.materials.new(name='BrushedChrome')
mat_BrushedChrome.use_nodes = True
bsdf_BrushedChrome = mat_BrushedChrome.node_tree.nodes.get('Principled BSDF')
if bsdf_BrushedChrome:
    bsdf_BrushedChrome.inputs['Base Color'].default_value = (0.48, 0.52, 0.58, 1.0)
    bsdf_BrushedChrome.inputs['Metallic'].default_value = 1.0
    bsdf_BrushedChrome.inputs['Roughness'].default_value = 0.16
    bsdf_BrushedChrome.inputs['Specular IOR Level'].default_value = 0.55
    bsdf_BrushedChrome.inputs['Alpha'].default_value = 1.0

mat_GunmetalEtched = bpy.data.materials.new(name='GunmetalEtched')
mat_GunmetalEtched.use_nodes = True
bsdf_GunmetalEtched = mat_GunmetalEtched.node_tree.nodes.get('Principled BSDF')
if bsdf_GunmetalEtched:
    bsdf_GunmetalEtched.inputs['Base Color'].default_value = (0.025, 0.032, 0.045, 1.0)
    bsdf_GunmetalEtched.inputs['Metallic'].default_value = 0.86
    bsdf_GunmetalEtched.inputs['Roughness'].default_value = 0.25
    bsdf_GunmetalEtched.inputs['Specular IOR Level'].default_value = 0.5
    bsdf_GunmetalEtched.inputs['Alpha'].default_value = 1.0

mat_DeepBlack = bpy.data.materials.new(name='DeepBlack')
mat_DeepBlack.use_nodes = True
bsdf_DeepBlack = mat_DeepBlack.node_tree.nodes.get('Principled BSDF')
if bsdf_DeepBlack:
    bsdf_DeepBlack.inputs['Base Color'].default_value = (0.001, 0.0015, 0.002, 1.0)
    bsdf_DeepBlack.inputs['Metallic'].default_value = 0.25
    bsdf_DeepBlack.inputs['Roughness'].default_value = 0.48
    bsdf_DeepBlack.inputs['Specular IOR Level'].default_value = 0.3
    bsdf_DeepBlack.inputs['Alpha'].default_value = 1.0

mat_NeonMagenta = bpy.data.materials.new(name='NeonMagenta')
mat_NeonMagenta.use_nodes = True
bsdf_NeonMagenta = mat_NeonMagenta.node_tree.nodes.get('Principled BSDF')
if bsdf_NeonMagenta:
    bsdf_NeonMagenta.inputs['Base Color'].default_value = (0.95, 0.004, 0.42, 1.0)
    bsdf_NeonMagenta.inputs['Metallic'].default_value = 0.0
    bsdf_NeonMagenta.inputs['Roughness'].default_value = 0.5
    bsdf_NeonMagenta.inputs['Specular IOR Level'].default_value = 0.2
    bsdf_NeonMagenta.inputs['Alpha'].default_value = 1.0
    bsdf_NeonMagenta.inputs['Emission Color'].default_value = (0.75, 0.0, 0.28, 1.0)
    bsdf_NeonMagenta.inputs['Emission Strength'].default_value = 0.18


# ── Objects ─────────────────────────────────────────────────
# Object: Cut_Front_TL
bpy.ops.mesh.primitive_cylinder_add(radius=0.0065, depth=0.018, vertices=64, location=(-0.079, -0.2, 0.105))
obj = bpy.context.active_object
obj.name = 'Cut_Front_TL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: Cut_Front_TR
bpy.ops.mesh.primitive_cylinder_add(radius=0.0065, depth=0.018, vertices=64, location=(0.079, -0.2, 0.105))
obj = bpy.context.active_object
obj.name = 'Cut_Front_TR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: Cut_Front_BL
bpy.ops.mesh.primitive_cylinder_add(radius=0.0065, depth=0.018, vertices=64, location=(-0.079, -0.2, -0.105))
obj = bpy.context.active_object
obj.name = 'Cut_Front_BL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: Cut_Front_BR
bpy.ops.mesh.primitive_cylinder_add(radius=0.0065, depth=0.018, vertices=64, location=(0.079, -0.2, -0.105))
obj = bpy.context.active_object
obj.name = 'Cut_Front_BR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: Cut_Rear_TL
bpy.ops.mesh.primitive_cylinder_add(radius=0.0065, depth=0.018, vertices=64, location=(-0.079, 0.14, 0.105))
obj = bpy.context.active_object
obj.name = 'Cut_Rear_TL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: Cut_Rear_TR
bpy.ops.mesh.primitive_cylinder_add(radius=0.0065, depth=0.018, vertices=64, location=(0.079, 0.14, 0.105))
obj = bpy.context.active_object
obj.name = 'Cut_Rear_TR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: Cut_Rear_BL
bpy.ops.mesh.primitive_cylinder_add(radius=0.0065, depth=0.018, vertices=64, location=(-0.079, 0.14, -0.105))
obj = bpy.context.active_object
obj.name = 'Cut_Rear_BL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: Cut_Rear_BR
bpy.ops.mesh.primitive_cylinder_add(radius=0.0065, depth=0.018, vertices=64, location=(0.079, 0.14, -0.105))
obj = bpy.context.active_object
obj.name = 'Cut_Rear_BR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: Cut_Foam_Center
bpy.ops.mesh.primitive_cylinder_add(radius=0.059, depth=0.035, vertices=96, location=(0.0, 0.045, 0.018))
obj = bpy.context.active_object
obj.name = 'Cut_Foam_Center'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
obj.hide_render = True
obj.hide_viewport = True

# Object: Layer01_AcrylicFrontPlate
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -0.2, 0.0))
obj = bpy.context.active_object
obj.name = 'Layer01_AcrylicFrontPlate'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.094, 0.003, 0.12)
if 'mat_AcrylicClear' in dir():
    obj.data.materials.append(mat_AcrylicClear)
mod = obj.modifiers.new(name='FrontEdgePolish', type='BEVEL')
mod.width = 0.006
mod.segments = 6
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599
mod = obj.modifiers.new(name='FrontHoleTL', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('Cut_Front_TL')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='FrontHoleTR', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('Cut_Front_TR')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='FrontHoleBL', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('Cut_Front_BL')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='FrontHoleBR', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('Cut_Front_BR')
mod.solver = 'EXACT'

# Object: Layer06_AcrylicRearPlate
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.14, 0.0))
obj = bpy.context.active_object
obj.name = 'Layer06_AcrylicRearPlate'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.094, 0.0025, 0.12)
if 'mat_AcrylicClear' in dir():
    obj.data.materials.append(mat_AcrylicClear)
mod = obj.modifiers.new(name='RearEdgePolish', type='BEVEL')
mod.width = 0.006
mod.segments = 6
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599
mod = obj.modifiers.new(name='RearHoleTL', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('Cut_Rear_TL')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='RearHoleTR', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('Cut_Rear_TR')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='RearHoleBL', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('Cut_Rear_BL')
mod.solver = 'EXACT'
mod = obj.modifiers.new(name='RearHoleBR', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('Cut_Rear_BR')
mod.solver = 'EXACT'

# Object: Layer05_BlackFoamInsert
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.045, 0.0))
obj = bpy.context.active_object
obj.name = 'Layer05_BlackFoamInsert'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.085, 0.005, 0.11)
if 'mat_BlackFoam' in dir():
    obj.data.materials.append(mat_BlackFoam)
mod = obj.modifiers.new(name='FoamSoftEdge', type='BEVEL')
mod.width = 0.009
mod.segments = 5
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599
mod = obj.modifiers.new(name='SpinnerAperture', type='BOOLEAN')
mod.operation = 'DIFFERENCE'
mod.object = bpy.data.objects.get('Cut_Foam_Center')
mod.solver = 'EXACT'

# Object: Layer03_AcrylicFrameTop
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -0.105, 0.111))
obj = bpy.context.active_object
obj.name = 'Layer03_AcrylicFrameTop'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.092, 0.004, 0.007)
if 'mat_AcrylicClear' in dir():
    obj.data.materials.append(mat_AcrylicClear)
mod = obj.modifiers.new(name='FrameTopPolish', type='BEVEL')
mod.width = 0.004
mod.segments = 5
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Layer03_AcrylicFrameBottom
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, -0.105, -0.111))
obj = bpy.context.active_object
obj.name = 'Layer03_AcrylicFrameBottom'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.092, 0.004, 0.007)
if 'mat_AcrylicClear' in dir():
    obj.data.materials.append(mat_AcrylicClear)
mod = obj.modifiers.new(name='FrameBottomPolish', type='BEVEL')
mod.width = 0.004
mod.segments = 5
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Layer03_AcrylicFrameLeft
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(-0.085, -0.105, 0.0))
obj = bpy.context.active_object
obj.name = 'Layer03_AcrylicFrameLeft'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.007, 0.004, 0.104)
if 'mat_AcrylicClear' in dir():
    obj.data.materials.append(mat_AcrylicClear)
mod = obj.modifiers.new(name='FrameLeftPolish', type='BEVEL')
mod.width = 0.004
mod.segments = 5
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Layer03_AcrylicFrameRight
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.085, -0.105, 0.0))
obj = bpy.context.active_object
obj.name = 'Layer03_AcrylicFrameRight'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.007, 0.004, 0.104)
if 'mat_AcrylicClear' in dir():
    obj.data.materials.append(mat_AcrylicClear)
mod = obj.modifiers.new(name='FrameRightPolish', type='BEVEL')
mod.width = 0.004
mod.segments = 5
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Layer07_BlackRearShell
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.255, 0.0))
obj = bpy.context.active_object
obj.name = 'Layer07_BlackRearShell'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.11, 0.012, 0.145)
if 'mat_BlackPolymer' in dir():
    obj.data.materials.append(mat_BlackPolymer)
mod = obj.modifiers.new(name='ShellEdgeRadius', type='BEVEL')
mod.width = 0.01
mod.segments = 8
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Layer07_RearShellInset
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.238, 0.0))
obj = bpy.context.active_object
obj.name = 'Layer07_RearShellInset'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.095, 0.004, 0.126)
if 'mat_DeepBlack' in dir():
    obj.data.materials.append(mat_DeepBlack)
mod = obj.modifiers.new(name='InsetSoftEdge', type='BEVEL')
mod.width = 0.006
mod.segments = 6
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: RearCounterboreTL
bpy.ops.mesh.primitive_cylinder_add(radius=0.009, depth=0.004, vertices=64, location=(-0.085, 0.226, 0.112))
obj = bpy.context.active_object
obj.name = 'RearCounterboreTL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_DeepBlack' in dir():
    obj.data.materials.append(mat_DeepBlack)

# Object: RearCounterboreTR
bpy.ops.mesh.primitive_cylinder_add(radius=0.009, depth=0.004, vertices=64, location=(0.085, 0.226, 0.112))
obj = bpy.context.active_object
obj.name = 'RearCounterboreTR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_DeepBlack' in dir():
    obj.data.materials.append(mat_DeepBlack)

# Object: RearCounterboreBL
bpy.ops.mesh.primitive_cylinder_add(radius=0.009, depth=0.004, vertices=64, location=(-0.085, 0.226, -0.112))
obj = bpy.context.active_object
obj.name = 'RearCounterboreBL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_DeepBlack' in dir():
    obj.data.materials.append(mat_DeepBlack)

# Object: RearCounterboreBR
bpy.ops.mesh.primitive_cylinder_add(radius=0.009, depth=0.004, vertices=64, location=(0.085, 0.226, -0.112))
obj = bpy.context.active_object
obj.name = 'RearCounterboreBR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_DeepBlack' in dir():
    obj.data.materials.append(mat_DeepBlack)

# Object: Layer04_SpinnerCore
bpy.ops.mesh.primitive_cylinder_add(radius=0.038, depth=0.01, vertices=96, location=(0.0, -0.015, 0.018))
obj = bpy.context.active_object
obj.name = 'Layer04_SpinnerCore'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_GunmetalEtched' in dir():
    obj.data.materials.append(mat_GunmetalEtched)
mod = obj.modifiers.new(name='CoreEdge', type='BEVEL')
mod.width = 0.002
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Layer04_CenterFace
bpy.ops.mesh.primitive_cylinder_add(radius=0.026, depth=0.012, vertices=96, location=(0.0, -0.025, 0.018))
obj = bpy.context.active_object
obj.name = 'Layer04_CenterFace'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_DeepBlack' in dir():
    obj.data.materials.append(mat_DeepBlack)
mod = obj.modifiers.new(name='FaceEdge', type='BEVEL')
mod.width = 0.0018
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Layer04_BearingRing
bpy.ops.mesh.primitive_torus_add(major_radius=0.029, minor_radius=0.0032, major_segments=96, minor_segments=18, location=(0.0, -0.033, 0.018))
obj = bpy.context.active_object
obj.name = 'Layer04_BearingRing'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_BrushedChrome' in dir():
    obj.data.materials.append(mat_BrushedChrome)

# Object: Layer04_LobeTop
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.01, vertices=96, location=(0.0, -0.015, 0.048))
obj = bpy.context.active_object
obj.name = 'Layer04_LobeTop'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_GunmetalEtched' in dir():
    obj.data.materials.append(mat_GunmetalEtched)
mod = obj.modifiers.new(name='TopLobeEdge', type='BEVEL')
mod.width = 0.002
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Layer04_LobeLeft
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.01, vertices=96, location=(-0.026, -0.015, 0.003))
obj = bpy.context.active_object
obj.name = 'Layer04_LobeLeft'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_GunmetalEtched' in dir():
    obj.data.materials.append(mat_GunmetalEtched)
mod = obj.modifiers.new(name='LeftLobeEdge', type='BEVEL')
mod.width = 0.002
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Layer04_LobeRight
bpy.ops.mesh.primitive_cylinder_add(radius=0.025, depth=0.01, vertices=96, location=(0.026, -0.015, 0.003))
obj = bpy.context.active_object
obj.name = 'Layer04_LobeRight'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_GunmetalEtched' in dir():
    obj.data.materials.append(mat_GunmetalEtched)
mod = obj.modifiers.new(name='RightLobeEdge', type='BEVEL')
mod.width = 0.002
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: EtchRingTop
bpy.ops.mesh.primitive_torus_add(major_radius=0.013, minor_radius=0.0014, major_segments=72, minor_segments=12, location=(0.0, -0.022, 0.048))
obj = bpy.context.active_object
obj.name = 'EtchRingTop'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_BrushedChrome' in dir():
    obj.data.materials.append(mat_BrushedChrome)

# Object: EtchRingLeft
bpy.ops.mesh.primitive_torus_add(major_radius=0.013, minor_radius=0.0014, major_segments=72, minor_segments=12, location=(-0.026, -0.022, 0.003))
obj = bpy.context.active_object
obj.name = 'EtchRingLeft'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_BrushedChrome' in dir():
    obj.data.materials.append(mat_BrushedChrome)

# Object: EtchRingRight
bpy.ops.mesh.primitive_torus_add(major_radius=0.013, minor_radius=0.0014, major_segments=72, minor_segments=12, location=(0.026, -0.022, 0.003))
obj = bpy.context.active_object
obj.name = 'EtchRingRight'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_BrushedChrome' in dir():
    obj.data.materials.append(mat_BrushedChrome)

# Object: BearingCap
bpy.ops.mesh.primitive_cylinder_add(radius=0.012, depth=0.016, vertices=96, location=(0.0, -0.039, 0.018))
obj = bpy.context.active_object
obj.name = 'BearingCap'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_BrushedChrome' in dir():
    obj.data.materials.append(mat_BrushedChrome)
mod = obj.modifiers.new(name='BearingCapEdge', type='BEVEL')
mod.width = 0.0018
mod.segments = 5
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Layer02_ClearRotorWindow
bpy.ops.mesh.primitive_cylinder_add(radius=0.057, depth=0.0035, vertices=96, location=(0.0, -0.078, 0.018))
obj = bpy.context.active_object
obj.name = 'Layer02_ClearRotorWindow'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_AcrylicClear' in dir():
    obj.data.materials.append(mat_AcrylicClear)
mod = obj.modifiers.new(name='WindowEdge', type='BEVEL')
mod.width = 0.0012
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Layer02_ClearWindowRing
bpy.ops.mesh.primitive_torus_add(major_radius=0.048, minor_radius=0.003, major_segments=96, minor_segments=18, location=(0.0, -0.083, 0.018))
obj = bpy.context.active_object
obj.name = 'Layer02_ClearWindowRing'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_AcrylicClear' in dir():
    obj.data.materials.append(mat_AcrylicClear)

# Object: Layer02_FastenerTL
bpy.ops.mesh.primitive_cylinder_add(radius=0.0085, depth=0.022, vertices=64, location=(-0.079, -0.255, 0.105))
obj = bpy.context.active_object
obj.name = 'Layer02_FastenerTL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_BrushedChrome' in dir():
    obj.data.materials.append(mat_BrushedChrome)
mod = obj.modifiers.new(name='FastenerTLEdge', type='BEVEL')
mod.width = 0.0014
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Layer02_FastenerTR
bpy.ops.mesh.primitive_cylinder_add(radius=0.0085, depth=0.022, vertices=64, location=(0.079, -0.255, 0.105))
obj = bpy.context.active_object
obj.name = 'Layer02_FastenerTR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_BrushedChrome' in dir():
    obj.data.materials.append(mat_BrushedChrome)
mod = obj.modifiers.new(name='FastenerTREdge', type='BEVEL')
mod.width = 0.0014
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Layer02_FastenerBL
bpy.ops.mesh.primitive_cylinder_add(radius=0.0085, depth=0.022, vertices=64, location=(-0.079, -0.255, -0.105))
obj = bpy.context.active_object
obj.name = 'Layer02_FastenerBL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_BrushedChrome' in dir():
    obj.data.materials.append(mat_BrushedChrome)
mod = obj.modifiers.new(name='FastenerBLEdge', type='BEVEL')
mod.width = 0.0014
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: Layer02_FastenerBR
bpy.ops.mesh.primitive_cylinder_add(radius=0.0085, depth=0.022, vertices=64, location=(0.079, -0.255, -0.105))
obj = bpy.context.active_object
obj.name = 'Layer02_FastenerBR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_BrushedChrome' in dir():
    obj.data.materials.append(mat_BrushedChrome)
mod = obj.modifiers.new(name='FastenerBREdge', type='BEVEL')
mod.width = 0.0014
mod.segments = 4
mod.limit_method = 'ANGLE'
mod.angle_limit = 0.523599

# Object: FrontCollarTL
bpy.ops.mesh.primitive_torus_add(major_radius=0.0065, minor_radius=0.0015, major_segments=64, minor_segments=12, location=(-0.079, -0.205, 0.105))
obj = bpy.context.active_object
obj.name = 'FrontCollarTL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_BrushedChrome' in dir():
    obj.data.materials.append(mat_BrushedChrome)

# Object: FrontCollarTR
bpy.ops.mesh.primitive_torus_add(major_radius=0.0065, minor_radius=0.0015, major_segments=64, minor_segments=12, location=(0.079, -0.205, 0.105))
obj = bpy.context.active_object
obj.name = 'FrontCollarTR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_BrushedChrome' in dir():
    obj.data.materials.append(mat_BrushedChrome)

# Object: FrontCollarBL
bpy.ops.mesh.primitive_torus_add(major_radius=0.0065, minor_radius=0.0015, major_segments=64, minor_segments=12, location=(-0.079, -0.205, -0.105))
obj = bpy.context.active_object
obj.name = 'FrontCollarBL'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_BrushedChrome' in dir():
    obj.data.materials.append(mat_BrushedChrome)

# Object: FrontCollarBR
bpy.ops.mesh.primitive_torus_add(major_radius=0.0065, minor_radius=0.0015, major_segments=64, minor_segments=12, location=(0.079, -0.205, -0.105))
obj = bpy.context.active_object
obj.name = 'FrontCollarBR'
obj.rotation_euler = (math.radians(90.0), math.radians(0.0), math.radians(0.0))
obj.scale = (1.0, 1.0, 1.0)
if 'mat_BrushedChrome' in dir():
    obj.data.materials.append(mat_BrushedChrome)

# Object: StudioBackdrop
bpy.ops.mesh.primitive_cube_add(size=2.0, location=(0.0, 0.4, 0.02))
obj = bpy.context.active_object
obj.name = 'StudioBackdrop'
obj.rotation_euler = (math.radians(0.0), math.radians(0.0), math.radians(0.0))
obj.scale = (0.65, 0.015, 0.65)
if 'mat_NeonMagenta' in dir():
    obj.data.materials.append(mat_NeonMagenta)
mod = obj.modifiers.new(name='BackdropEdge', type='BEVEL')
mod.width = 0.05
mod.segments = 4
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
cam_obj.location = (0.38, -0.7, 0.35)
cam_obj.rotation_euler = (math.radians(65.0), math.radians(0.0), math.radians(29.0))
scene.camera = cam_obj


# ── Lights ──────────────────────────────────────────────────
light_data = bpy.data.lights.new(name='KeySoftbox', type='AREA')
light_data.energy = 780.0
light_data.color = (1.0, 0.82, 0.72)
light_data.size = 1.0
light_data.size_y = 1.0
light_data.shape = 'RECTANGLE'
light_obj = bpy.data.objects.new('KeySoftbox', light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (-0.3, -0.42, 0.55)
light_obj.rotation_euler = (math.radians(48.0), math.radians(0.0), math.radians(-32.0))

light_data = bpy.data.lights.new(name='FillSoftbox', type='AREA')
light_data.energy = 420.0
light_data.color = (0.45, 0.68, 1.0)
light_data.size = 1.0
light_data.size_y = 1.0
light_data.shape = 'RECTANGLE'
light_obj = bpy.data.objects.new('FillSoftbox', light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (0.42, -0.25, 0.1)
light_obj.rotation_euler = (math.radians(82.0), math.radians(0.0), math.radians(58.0))

light_data = bpy.data.lights.new(name='RimSoftbox', type='AREA')
light_data.energy = 620.0
light_data.color = (1.0, 0.22, 0.72)
light_data.size = 1.0
light_data.size_y = 1.0
light_data.shape = 'RECTANGLE'
light_obj = bpy.data.objects.new('RimSoftbox', light_data)
bpy.context.collection.objects.link(light_obj)
light_obj.location = (-0.22, 0.1, 0.48)
light_obj.rotation_euler = (math.radians(35.0), math.radians(0.0), math.radians(-18.0))


# ── Keyframes ───────────────────────────────────────────────
# (none)

# ── Blender 5.2 compatibility and material finishing ───────
# The geometry, materials, camera, and lights above are generated from the
# cli-anything-blender scene state.  This final pass supplies features that
# version 1.0.0 does not expose as CLI commands.
from mathutils import Vector


def point_at(scene_object, target):
    direction = Vector(target) - scene_object.location
    scene_object.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()


# Apply authored dimensions before evaluating bevels and booleans.  The CLI
# stores rectangular dimensions as non-uniform object scales.
bpy.ops.object.select_all(action='DESELECT')
for scene_object in list(bpy.context.scene.objects):
    if scene_object.type != 'MESH':
        continue
    bpy.context.view_layer.objects.active = scene_object
    scene_object.select_set(True)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    scene_object.select_set(False)

# Physically transparent acrylic instead of alpha-only transparency.
acrylic = bpy.data.materials.get('AcrylicClear')
if acrylic and acrylic.use_nodes:
    acrylic_bsdf = acrylic.node_tree.nodes.get('Principled BSDF')
    if acrylic_bsdf:
        acrylic_bsdf.inputs['Base Color'].default_value = (0.54, 0.78, 0.94, 1.0)
        acrylic_bsdf.inputs['Roughness'].default_value = 0.035
        acrylic_bsdf.inputs['Metallic'].default_value = 0.0
        acrylic_bsdf.inputs['IOR'].default_value = 1.49
        acrylic_bsdf.inputs['Transmission Weight'].default_value = 0.97
        acrylic_bsdf.inputs['Alpha'].default_value = 1.0

clear_window = bpy.data.objects.get('Layer02_ClearRotorWindow')
if clear_window:
    clear_window.hide_render = True
    clear_window.hide_viewport = True

gunmetal = bpy.data.materials.get('GunmetalEtched')
if gunmetal and gunmetal.use_nodes:
    gunmetal_bsdf = gunmetal.node_tree.nodes.get('Principled BSDF')
    if gunmetal_bsdf:
        gunmetal_bsdf.inputs['Base Color'].default_value = (0.28, 0.33, 0.42, 1.0)
        gunmetal_bsdf.inputs['Metallic'].default_value = 0.92
        gunmetal_bsdf.inputs['Roughness'].default_value = 0.23

# Procedural micro-surface for the black foam insert; no UV dependency.
foam = bpy.data.materials.get('BlackFoam')
if foam and foam.use_nodes:
    nodes = foam.node_tree.nodes
    links = foam.node_tree.links
    foam_bsdf = nodes.get('Principled BSDF')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 420.0
    noise.inputs['Detail'].default_value = 2.5
    noise.inputs['Roughness'].default_value = 0.72
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.22
    bump.inputs['Distance'].default_value = 0.00035
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    if foam_bsdf:
        links.new(bump.outputs['Normal'], foam_bsdf.inputs['Normal'])

# Subtle brushed breakup for metal highlights.
chrome = bpy.data.materials.get('BrushedChrome')
if chrome and chrome.use_nodes:
    nodes = chrome.node_tree.nodes
    links = chrome.node_tree.links
    chrome_bsdf = nodes.get('Principled BSDF')
    noise = nodes.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 165.0
    noise.inputs['Detail'].default_value = 1.2
    bump = nodes.new('ShaderNodeBump')
    bump.inputs['Strength'].default_value = 0.08
    bump.inputs['Distance'].default_value = 0.00012
    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    if chrome_bsdf:
        links.new(bump.outputs['Normal'], chrome_bsdf.inputs['Normal'])

smooth_prefixes = (
    'Layer02_Fastener', 'Layer04_', 'EtchRing', 'BearingCap',
    'FrontCollar', 'RearCounterbore',
)
for scene_object in bpy.context.scene.objects:
    if scene_object.type == 'MESH' and scene_object.name.startswith(smooth_prefixes):
        for polygon in scene_object.data.polygons:
            polygon.use_smooth = True

hero_camera = bpy.data.objects.get('HeroCamera')
if hero_camera:
    hero_camera.location = (0.46, -0.94, 0.43)
    hero_camera.data.lens = 56.0
    hero_camera.data.clip_start = 0.01
    point_at(hero_camera, (0.0, 0.015, 0.012))

light_targets = {
    'KeySoftbox': (0.0, -0.02, 0.02),
    'FillSoftbox': (0.0, 0.02, 0.0),
    'RimSoftbox': (0.0, 0.08, 0.03),
}
for light_name, target in light_targets.items():
    light_object = bpy.data.objects.get(light_name)
    if light_object:
        point_at(light_object, target)
        light_object.data.size = 0.28
        light_object.data.size_y = 0.28

light_energy = {
    'KeySoftbox': 75.0,
    'FillSoftbox': 24.0,
    'RimSoftbox': 48.0,
}
for light_name, energy in light_energy.items():
    light_object = bpy.data.objects.get(light_name)
    if light_object:
        light_object.data.energy = energy

magenta = bpy.data.materials.get('NeonMagenta')
if magenta and magenta.use_nodes:
    magenta_bsdf = magenta.node_tree.nodes.get('Principled BSDF')
    if magenta_bsdf:
        magenta_bsdf.inputs['Base Color'].default_value = (0.46, 0.002, 0.14, 1.0)
        magenta_bsdf.inputs['Roughness'].default_value = 0.62
        magenta_bsdf.inputs['Emission Color'].default_value = (0.34, 0.0, 0.08, 1.0)
        magenta_bsdf.inputs['Emission Strength'].default_value = 0.035

world = bpy.context.scene.world
if world and world.use_nodes:
    background = world.node_tree.nodes.get('Background')
    if background:
        background.inputs['Color'].default_value = (0.008, 0.004, 0.012, 1.0)
        background.inputs['Strength'].default_value = 0.055

scene.cycles.use_adaptive_sampling = True
scene.cycles.adaptive_threshold = 0.03
scene.cycles.max_bounces = 8
scene.cycles.transmission_bounces = 8
scene.cycles.transparent_max_bounces = 8
scene.render.image_settings.color_mode = 'RGBA'
scene.render.resolution_percentage = 100
try:
    scene.view_settings.look = 'AgX - Medium High Contrast'
except TypeError:
    pass
scene.view_settings.exposure = -1.1

bpy.ops.wm.save_as_mainfile(
    filepath=r'/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/CliAnythingTrinityCase/TrinityCaseCLI.blend',
    check_existing=False,
)

# ── Render Output ───────────────────────────────────────────
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = r'/private/tmp/fidgeting_app_cli/unity/FidgetingApp/Artifacts/CliAnythingTrinityCasePreview/hero.png'
scene.frame_set(1)

# Render single frame
bpy.ops.render.render(write_still=True)

print('Render complete: /private/tmp/fidgeting_app_cli/unity/FidgetingApp/Artifacts/CliAnythingTrinityCasePreview/hero.png')
