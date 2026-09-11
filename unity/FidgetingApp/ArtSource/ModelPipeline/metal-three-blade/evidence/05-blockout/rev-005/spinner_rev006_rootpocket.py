"""
geeone-02 · rev-006 · 叶根凹坑 + 阶梯过渡 + 刀纹
Blender 4.2+ / 5.x · 在 rev-005 的 .blend 里 Run Script（或由 run_rev005_rev006_headless.py 驱动）

按用户 2026-09-07 17:18 的《agent 执行说明》A / B / C 实现。脚本不重建机身、不碰盖体，
只在 P["BODY_NAME"] 上：
  A. 三个叶根凹坑刀体（平面直壁 + 圆锥顶弧，开口伸进盖孔）→ Exact Boolean DIFFERENCE，material TRANSFER
  B. 两级阶梯：Bevel A（weight，45° 平切带）→ 凹坑 → Bevel B（angle，0.2 微圆角）
  C. 刀纹材质（Bump，不建几何）：臂面线性刀纹 / 坑壁等高环纹

说明书未提及但必须处理的 rev-005 遗留：rev-005 的三个凹槽 Bool_SP_cut_pocket_*（尖朝圆心，方向与参考相反）
和 rev-005 的角度 Bevel 会被移除（P["REMOVE_REV005_POCKETS"] / P["REMOVE_REV005_BEVEL"]），否则坑会重叠、倒角会重复。
盖孔 / 轴承孔 Boolean 保留。所有数值由 P 驱动，改 P 重跑，不要手拉顶点。
"""
import bpy, bmesh, math
from mathutils import Vector

# ============================================================ 参数表（说明书 A / B / C）
P = dict(
    BODY_NAME    = "SP_Body",
    BLADE_ANGLES = (90, 210, 330),   # 叶片轴向（与 rev-005 一致）

    # ---- A. 叶根凹坑（局部系：u 沿叶轴指向叶尖，v 切向，z 向上；坑对称于 v=0）
    PK_APEX_U      = 25.0,   # 顶弧圆心到轴心距离 mm；最远点 = PK_APEX_U + PK_APEX_R
    PK_APEX_R      = 2.5,    # 顶弧半径，量在坑口 z = Z_TOP
    PK_HALF_ANGLE  = 26.0,   # 直壁相对叶轴半角 → 坑口顶角 52°
    PK_DEPTH       = 3.2,    # Z_TOP（机身顶面）到坑底的垂直深度
    PK_WALL_DRAFT  = 62.0,   # 直壁与水平面夹角；坑底轮廓比坑口内缩 PK_DEPTH / tan(draft)
    PK_ARC_SEGS    = 24,     # 顶弧分段
    PK_OPEN_INSET  = 3.0,    # 开口端：刀体向轴心伸进盖孔 = R_CAP − 3
    PK_TOP_EXTRA   = 2.0,    # 刀体顶面在坑口上方 2 mm（轮廓按拔模角放大）
    BOOL_SOLVER    = "MANIFOLD",  # 说明书写 Exact；实测 Blender 5.2 的 EXACT 在 Bevel A 之后会留下刀体顶面 + 29 条非流形边，MANIFOLD（4.5+）结果正确。可改回 "EXACT" 复现

    # ---- B. 阶梯过渡
    STEP1_WIDTH  = 1.20,     # 45° 平切带宽（weight 限制，只在机身外轮廓“顶面↔竖壁”上沿）
    STEP1_SEGS   = 1,        # 1 = chamfer，不要改 2+
    STEP2_WIDTH  = 0.20,     # 全局微圆角
    STEP2_SEGS   = 2,
    STEP2_ANGLE  = 35.0,     # 只倒 >35° 的锐边
    TAG_TOP_NZ   = 0.5,      # 打标：一邻面 n.z > 0.5
    TAG_WALL_NZ  = 0.25,     # 另一邻面 |n.z| < 0.25
    TAG_MIN_R    = 0.5,      # 边中点半径需 > R_IN + 0.5（在盖缝之外）

    # ---- C. 刀纹（材质）
    LAY_MODE     = "radial", # "radial"：线平行叶轴（俯视辐条）；"tangential"：同心圆
    LAY_PITCH    = 0.20,     # mm
    LAY_DEPTH    = 0.012,    # Bump distance（mm）
    LAY_R_REF    = 25.0,     # radial 模式下按此半径换算辐条数（节距在此半径上 = LAY_PITCH）
    ROUGH_ARM    = 0.36,
    ROUGH_POCKET = 0.42,
    STEEL_BASE   = (0.78, 0.79, 0.80, 1.0),

    # ---- rev-005 遗留处理
    REMOVE_REV005_POCKETS = True,
    REMOVE_REV005_BEVEL   = True,
)

# ============================================================ 从场景 / rev-005 读派生量
def _rev005_derived():
    """R_CAP、R_IN、Z_TOP（机身顶面）从 rev-005 对象读取，脚本不依赖 rev-005 的 P。"""
    body = bpy.data.objects[P["BODY_NAME"]]
    zs = [v.co.z for v in body.data.vertices]
    z_top = max(zs)
    bore = bpy.data.objects.get("SP_cut_bore")
    if bore is not None:
        r_in = max(math.hypot(v.co.x, v.co.y) for v in bore.data.vertices)
    else:
        r_in = 18.22
    cap = bpy.data.objects.get("SP_Cap")
    if cap is not None:
        r_cap = max(math.hypot(v.co.x, v.co.y) for v in cap.data.vertices)
    else:
        r_cap = r_in - 0.8
    r_tot = max(math.hypot(v.co.x, v.co.y) for v in body.data.vertices)
    return body, z_top, r_in, r_cap, r_tot


def link(obj):
    bpy.context.scene.collection.objects.link(obj)


# ============================================================ A. 凹坑刀体
def pocket_loop(r_arc, u_open, alpha_deg):
    """局部 (u, v) 轮廓：直壁与圆心 (PK_APEX_U, 0)、半径 r_arc 的圆相切，半角 alpha；开口端在 u_open。
    顶点顺序（CCW）：下壁开口端 → 下切点 → 顶弧（-θ…+θ，经过 0°）→ 上切点 → 上壁开口端。
    同一构造换 r_arc 就是等距偏移的轮廓（切线随圆一起平移），所以各层顶点一一对应。"""
    a = math.radians(alpha_deg)
    cu = P["PK_APEX_U"]
    theta = math.pi / 2 - a  # 切点极角
    # 上切点 T+ = C + r·n，n = (sinα, cosα)；壁方向 d = (−cosα, sinα)（从切点指向轴心）
    tu, tv = cu + r_arc * math.sin(a), r_arc * math.cos(a)
    t_open = (tu - u_open) / math.cos(a)  # 沿壁到开口端
    ou, ov = tu - t_open * math.cos(a), tv + t_open * math.sin(a)
    pts = [(ou, -ov)]  # 下壁开口端
    n = P["PK_ARC_SEGS"]
    for k in range(n + 1):  # 下切点 → 顶弧 → 上切点
        ang = -theta + 2 * theta * k / n
        pts.append((cu + r_arc * math.cos(ang), r_arc * math.sin(ang)))
    pts.append((ou, ov))  # 上壁开口端
    return pts


def make_pocket_cutter(idx, angle_deg, z_top, r_cap):
    """三层轮廓：坑底（内缩）、坑口（标称）、坑口上方 2 mm（放大）。壁是平面，顶弧是锥面。"""
    draft = math.radians(P["PK_WALL_DRAFT"])
    inset = P["PK_DEPTH"] / math.tan(draft)            # 坑底比坑口向内缩
    extra = P["PK_TOP_EXTRA"] / math.tan(draft)        # 顶面比坑口向外放大
    u_open = r_cap - P["PK_OPEN_INSET"]
    z_floor = z_top - P["PK_DEPTH"]
    r_floor = P["PK_APEX_R"] - inset
    if r_floor <= 0.05:
        raise ValueError("PK_APEX_R − PK_DEPTH/tan(draft) ≤ 0：顶弧在坑底收成尖，调大 PK_APEX_R 或 PK_WALL_DRAFT")
    # 两层即可：坑底轮廓 + 坑口上方 2 mm 的放大轮廓；壁是平面，坑口 z_top 处的轮廓由拔模角自然给出。
    # （不在 z_top 再放一圈顶点：与机身顶面共面的顶点会让 Exact Boolean 在 Bevel A 之后产生非流形边。）
    loops_2d = [
        (pocket_loop(r_floor, u_open, P["PK_HALF_ANGLE"]), z_floor),
        (pocket_loop(P["PK_APEX_R"] + extra, u_open, P["PK_HALF_ANGLE"]), z_top + P["PK_TOP_EXTRA"]),
    ]
    ax = math.radians(angle_deg)
    ca, sa = math.cos(ax), math.sin(ax)
    bm = bmesh.new()
    loops = []
    for pts, z in loops_2d:
        loops.append([bm.verts.new((u * ca - v * sa, u * sa + v * ca, z)) for u, v in pts])
    n = len(loops[0])
    bm.faces.new(loops[0])                      # 坑底
    bm.faces.new(list(reversed(loops[-1])))     # 顶
    for lo, hi in zip(loops[:-1], loops[1:]):
        for i in range(n):
            j = (i + 1) % n
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    for f in bm.faces:
        f.smooth = False  # 平面壁 / 锥面：不要平滑
    me = bpy.data.meshes.new("SP_cut_rootpocket_%d" % idx)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new("SP_cut_rootpocket_%d" % idx, me)
    link(ob)
    ob.display_type = "WIRE"
    ob.hide_render = True
    return ob, dict(z_floor=z_floor, inset=inset, r_floor=r_floor, u_open=u_open, extra=extra)


# ============================================================ B. 阶梯：weight 打标 + 两个 Bevel
def tag_top_wall_edges(body, r_min):
    """机身外轮廓“顶面 ↔ 竖壁”上沿：一邻面 n.z > TAG_TOP_NZ、另一邻面 |n.z| < TAG_WALL_NZ、且边中点半径 > r_min。"""
    me = body.data
    bm = bmesh.new()
    bm.from_mesh(me)
    bm.edges.ensure_lookup_table()
    layer = bm.edges.layers.float.get("bevel_weight_edge") or bm.edges.layers.float.new("bevel_weight_edge")
    count = 0
    for e in bm.edges:
        e[layer] = 0.0
        if len(e.link_faces) != 2:
            continue
        n0, n1 = e.link_faces[0].normal, e.link_faces[1].normal
        top_wall = (n0.z > P["TAG_TOP_NZ"] and abs(n1.z) < P["TAG_WALL_NZ"]) or (n1.z > P["TAG_TOP_NZ"] and abs(n0.z) < P["TAG_WALL_NZ"])
        mid = (e.verts[0].co + e.verts[1].co) / 2
        if top_wall and math.hypot(mid.x, mid.y) > r_min:
            e[layer] = 1.0
            count += 1
    bm.to_mesh(me)
    bm.free()
    me.update()
    return count


def add_bevel(body, name, width, segments, limit, angle_deg=None):
    m = body.modifiers.new(name, "BEVEL")
    m.width = width
    m.segments = segments
    m.limit_method = limit
    if limit == "ANGLE":
        m.angle_limit = math.radians(angle_deg)
    m.miter_outer = "MITER_ARC" if segments > 1 else "MITER_SHARP"
    return m


# ============================================================ C. 刀纹材质
def _principled(name, rough):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = P["STEEL_BASE"]
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = rough
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    return m, nt, bsdf


def wave_scale_for_pitch(pitch):
    """Blender Wave BANDS：n = 10·coord，value = sin(n·scale)... 周期 = 2π / (10·scale) → scale = 2π / (10·pitch)."""
    return 2 * math.pi / (10.0 * pitch)


def mat_arm_lay():
    m, nt, bsdf = _principled("SP_Steel_ArmLay", P["ROUGH_ARM"])
    coord = nt.nodes.new("ShaderNodeTexCoord")
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.inputs["Scale"].default_value = wave_scale_for_pitch(P["LAY_PITCH"])
    wave.inputs["Distortion"].default_value = 0.0
    wave.inputs["Detail"].default_value = 0.0
    if P["LAY_MODE"] == "tangential":
        wave.wave_type = "RINGS"
        wave.rings_direction = "Z"
        nt.links.new(coord.outputs["Object"], wave.inputs["Vector"])
    else:  # radial：俯视辐条 = 极角 × 参考半径 作为带坐标
        wave.wave_type = "BANDS"
        wave.bands_direction = "X"
        sep = nt.nodes.new("ShaderNodeSeparateXYZ")
        atan = nt.nodes.new("ShaderNodeMath")
        atan.operation = "ARCTAN2"
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MULTIPLY"
        mul.inputs[1].default_value = P["LAY_R_REF"]  # 弧长 = 角 × R_ref
        comb = nt.nodes.new("ShaderNodeCombineXYZ")
        nt.links.new(coord.outputs["Object"], sep.inputs[0])
        nt.links.new(sep.outputs["Y"], atan.inputs[0])
        nt.links.new(sep.outputs["X"], atan.inputs[1])
        nt.links.new(atan.outputs[0], mul.inputs[0])
        nt.links.new(mul.outputs[0], comb.inputs["X"])
        nt.links.new(comb.outputs[0], wave.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 1.0
    bump.inputs["Distance"].default_value = P["LAY_DEPTH"]
    nt.links.new(wave.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def mat_pocket_lay():
    """等高环纹：沿 z 堆叠的水平刀痕（顶弧处一圈圈细环）。"""
    m, nt, bsdf = _principled("SP_Steel_PocketLay", P["ROUGH_POCKET"])
    coord = nt.nodes.new("ShaderNodeTexCoord")
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type = "BANDS"
    wave.bands_direction = "Z"
    wave.inputs["Scale"].default_value = wave_scale_for_pitch(P["LAY_PITCH"])
    wave.inputs["Distortion"].default_value = 0.0
    wave.inputs["Detail"].default_value = 0.0
    nt.links.new(coord.outputs["Object"], wave.inputs["Vector"])
    bump = nt.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value = 1.0
    bump.inputs["Distance"].default_value = P["LAY_DEPTH"]
    nt.links.new(wave.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m


# ============================================================ 主流程
def main():
    body, z_top, r_in, r_cap, r_tot = _rev005_derived()

    # rev-005 遗留：移除方向相反的旧凹槽与旧角度倒角；清掉本脚本上一次的产物
    for m in list(body.modifiers):
        if m.name.startswith("R6_") or (P["REMOVE_REV005_POCKETS"] and m.name.startswith("Bool_SP_cut_pocket")) or (P["REMOVE_REV005_BEVEL"] and m.type == "BEVEL" and not m.name.startswith("R6_")):
            body.modifiers.remove(m)
    for o in list(bpy.data.objects):
        if o.name.startswith("SP_cut_rootpocket") or (P["REMOVE_REV005_POCKETS"] and o.name.startswith("SP_cut_pocket")):
            bpy.data.objects.remove(o, do_unlink=True)
    for mat_name in ("SP_Steel_ArmLay", "SP_Steel_PocketLay"):
        old = bpy.data.materials.get(mat_name)
        if old is not None:
            bpy.data.materials.remove(old)

    # C. 材质
    arm = mat_arm_lay()
    pocket_mat = mat_pocket_lay()
    if body.data.materials:
        body.data.materials[0] = arm  # slot 0：臂面 / 顶面
    else:
        body.data.materials.append(arm)

    # B-1. Bevel A：weight 打标 + 45° 平切带（在凹坑之前）
    n_tagged = tag_top_wall_edges(body, r_in + P["TAG_MIN_R"])
    add_bevel(body, "R6_StepA_45chamfer", P["STEP1_WIDTH"], P["STEP1_SEGS"], "WEIGHT")

    # A. 三个凹坑：Exact Boolean，材质 TRANSFER（坑壁拿到 SP_Steel_PocketLay）
    info = None
    for i, ang in enumerate(P["BLADE_ANGLES"]):
        cut, info = make_pocket_cutter(i, ang, z_top, r_cap)
        cut.data.materials.append(pocket_mat)
        m = body.modifiers.new("R6_Pocket_%d" % i, "BOOLEAN")
        m.operation = "DIFFERENCE"
        m.object = cut
        m.solver = P["BOOL_SOLVER"]
        m.material_mode = "TRANSFER"

    # B-2. Bevel B：全局微圆角，最后
    add_bevel(body, "R6_StepB_break", P["STEP2_WIDTH"], P["STEP2_SEGS"], "ANGLE", P["STEP2_ANGLE"])

    tipmost = P["PK_APEX_U"] + P["PK_APEX_R"]
    print("[rev006] pocket : apex_u %.2f  apex_R %.2f  -> tip-most %.2f, clearance to tip %.2f mm; half-angle %.0f° (mouth apex %.0f°)"
          % (P["PK_APEX_U"], P["PK_APEX_R"], tipmost, r_tot - tipmost, P["PK_HALF_ANGLE"], 2 * P["PK_HALF_ANGLE"]))
    print("[rev006] pocket : depth %.2f -> floor z %.2f (body top %.2f, cap seat/bore from %.2f); draft %.0f° -> floor inset %.2f, floor apex R %.2f; open end u %.2f (R_CAP %.2f − %.1f)"
          % (P["PK_DEPTH"], info["z_floor"], z_top, 7.5, P["PK_WALL_DRAFT"], info["inset"], info["r_floor"], info["u_open"], r_cap, P["PK_OPEN_INSET"]))
    print("[rev006] steps  : A weight-bevel %.2f × %d seg on %d tagged top/wall edges (r > %.2f); B angle-bevel %.2f × %d seg @ %.0f°"
          % (P["STEP1_WIDTH"], P["STEP1_SEGS"], n_tagged, r_in + P["TAG_MIN_R"], P["STEP2_WIDTH"], P["STEP2_SEGS"], P["STEP2_ANGLE"]))
    print("[rev006] lay    : mode %s  pitch %.2f mm  depth %.3f mm  wave scale %.3f  rough arm %.2f / pocket %.2f"
          % (P["LAY_MODE"], P["LAY_PITCH"], P["LAY_DEPTH"], wave_scale_for_pitch(P["LAY_PITCH"]), P["ROUGH_ARM"], P["ROUGH_POCKET"]))
    print("[rev006] modifiers on %s: %s  (pocket solver %s)" % (body.name, " -> ".join(m.name for m in body.modifiers), P["BOOL_SOLVER"]))
    # 自检：求值后凹坑足迹内不得有高于机身顶面的顶点（EXACT 失败的症状），且无非流形边
    dg = bpy.context.evaluated_depsgraph_get()
    me = body.evaluated_get(dg).to_mesh()
    bm = bmesh.new()
    bm.from_mesh(me)
    nonman = sum(1 for e in bm.edges if not e.is_manifold)
    bm.free()
    a0 = math.radians(P["BLADE_ANGLES"][0])
    zs = [v.co.z for v in me.vertices if 19 < (v.co.x * math.cos(a0) + v.co.y * math.sin(a0)) < tipmost and abs(-v.co.x * math.sin(a0) + v.co.y * math.cos(a0)) < 5]
    print("[rev006] selfcheck: evaluated verts %d, non-manifold edges %d, pocket footprint z %.2f..%.2f (must be <= body top %.2f)"
          % (len(me.vertices), nonman, min(zs), max(zs), z_top))
    body.evaluated_get(dg).to_mesh_clear()


main()
