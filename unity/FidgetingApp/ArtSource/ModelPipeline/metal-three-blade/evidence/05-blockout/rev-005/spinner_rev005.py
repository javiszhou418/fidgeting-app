"""
统一三叶陀螺 rev-005 · 参数化重建脚本
Blender 4.2+ / 5.x · 在 Text Editor 里直接 Run Script
单位：mm（脚本会把场景单位设成 mm）

机身重做：不再是三片独立叶片，而是一块圆角等边三角形整体，
  盖嵌在中心圆孔里，三个角顶面各有一个开口朝圆心的三角凹槽。
盖体台面占比 0.70 -> 0.797，其余盖体参数保持 rev-004。

所有可调数值都在 P 里，其余代码不要动。
"""
import bpy, bmesh, math
from mathutils import Vector

# ============================================================ 参数表
P = dict(
    # ---- 整体
    D_TOTAL      = 65.0,     # 外径
    CAP_RATIO    = 0.536,    # 盖直径 / 外径
    GAP          = 0.8,      # 暗缝宽度（盖外沿到叶片内弧）

    # ---- 盖体（rev-004 保留，仅台面占比改 0.797）
    DISC_RATIO   = 0.797,    # 平盘直径 / 盖直径   <-- Gate 02 裁决
    WEDGE_N      = 24,       # 楔数，48 三角
    WEDGE_SLOPE  = 25.0,     # 楔环下斜角，deg
    CAP_ABOVE    = 1.5,      # 平盘高出叶片最高点
    CAP_SEAT_Z   = 7.5,      # 盖底面 / 机身核心顶面高度

    # ---- 机身（一块圆角等边三角形整体，三个角就是“叶片”，不是三片独立叶）
    BODY_H       = 12.0,     # 机身厚度 = 三角顶面高度
    CORNER_R     = 9.0,      # 三角三个角的圆角半径，角顶点落在外径上
    SIDE_SAG     = 1.5,      # 三条边向内凹的弧度（边中点内凹量，mm）；0 = 直边
    BEARING_R    = 6.4,      # 轴承外圈半径（R188 = 12.7/2），穿透孔

    # ---- 角部三角凹槽（每个角顶面一个，开口朝圆心）
    POCKET_WALL  = 2.2,      # 凹槽外壁到机身外缘的壁厚
    POCKET_APEX  = 19.6,     # 凹槽内尖点到圆心的距离（应 > R_IN，否则打穿盖孔）
    POCKET_HALF  = 32.0,     # 凹槽尖角半角，deg
    POCKET_DEPTH = 3.0,      # 凹槽深度
    POCKET_CHAMF = 45.0,     # 凹槽侧壁倾角，deg（45 = 等量斜切）
    POCKET_ROUND = 1.2,      # 凹槽平面轮廓的角圆角

    # ---- 细分（影响面数，不影响形状）
    N_CORNER     = 16,       # 三角圆角段数
    N_SIDE       = 12,       # 三角边段数
    N_BORE       = 96,       # 盖孔 / 轴承孔圆周段数

    # ---- 倒角
    BEVEL_W      = 0.5,
    BEVEL_SEG    = 3,
    BEVEL_ANGLE  = 30.0,     # 角度限制，只倒 >30° 的边

    # ---- 材质
    STEEL_BASE   = (0.78, 0.79, 0.80, 1.0),
    ROUGH_SATIN  = 0.36,     # 叶片 / 楔环 / 侧壁
    ROUGH_DISC   = 0.30,     # 车削平盘
    ANISO_DISC   = 0.70,
    RINGS_SCALE  = 6.0,      # 年轮纹密度，Wave Texture scale（对象坐标 mm）
    RINGS_DISTORT= 0.30,     # 年轮纹径向抖动，去掉 CD 感
    RINGS_BUMP   = 0.02,
)

# ============================================================ 派生量（不要手改，改 P）
R_TOT   = P["D_TOTAL"] / 2
R_CAP   = R_TOT * P["CAP_RATIO"]
R_IN    = R_CAP + P["GAP"]                       # 叶片内凹弧半径 = 暗缝外沿
R_DISC  = R_CAP * P["DISC_RATIO"]
Z_TOP   = P["BODY_H"] + P["CAP_ABOVE"]           # 平盘高度
Z_RIM   = Z_TOP - (R_CAP - R_DISC) * math.tan(math.radians(P["WEDGE_SLOPE"]))

# ============================================================ 工具
def rm_prev():
    for o in list(bpy.data.objects):
        if o.name.startswith("SP_"):
            bpy.data.objects.remove(o, do_unlink=True)
    for m in list(bpy.data.meshes):
        if m.users == 0: bpy.data.meshes.remove(m)

def link(obj):
    bpy.context.scene.collection.objects.link(obj)

def circ_inter(c0, r0, c1, r1):
    dx, dy = c1[0]-c0[0], c1[1]-c0[1]
    d = math.hypot(dx, dy)
    a = (r0*r0 - r1*r1 + d*d) / (2*d)
    h = math.sqrt(max(r0*r0 - a*a, 0.0))
    xm, ym = c0[0] + a*dx/d, c0[1] + a*dy/d
    return [(xm + h*dy/d, ym - h*dx/d), (xm - h*dy/d, ym + h*dx/d)]

def arc(c, r, a0, a1, n, skip_first=False, skip_last=False):
    out = []
    for i in range(n+1):
        if (skip_first and i == 0) or (skip_last and i == n): continue
        a = a0 + (a1-a0) * i / n
        out.append((c[0] + r*math.cos(a), c[1] + r*math.sin(a)))
    return out

def add_bevel(obj):
    m = obj.modifiers.new("Bevel", "BEVEL")
    m.width = P["BEVEL_W"]; m.segments = P["BEVEL_SEG"]
    m.limit_method = "ANGLE"; m.angle_limit = math.radians(P["BEVEL_ANGLE"])

# ============================================================ 平面几何工具
def fillet_polygon(pts, r, n):
    """对一个多边形的每个顶点做半径 r 的圆角（顶点数不多时用）。"""
    out = []
    m = len(pts)
    for i in range(m):
        Pp, C, Pn = Vector(pts[i-1]), Vector(pts[i]), Vector(pts[(i+1) % m])
        a = (Pp - C).normalized(); b = (Pn - C).normalized()
        phi = a.angle(b) / 2
        t = r / math.tan(phi)
        center = C + (a + b).normalized() * (r / math.sin(phi))
        p0, p1 = C + a*t, C + b*t
        a0 = math.atan2(p0.y-center.y, p0.x-center.x); a1 = math.atan2(p1.y-center.y, p1.x-center.x)
        d = (a1 - a0 + math.pi) % (2*math.pi) - math.pi
        out += [(center.x + r*math.cos(a0 + d*k/n), center.y + r*math.sin(a0 + d*k/n)) for k in range(n+1)]
    return out

def body_outline():
    """圆角等边三角形，角顶点在 90/210/330°，顶点落在 R_TOT；边可向内微凹。"""
    rc, sag = P["CORNER_R"], P["SIDE_SAG"]
    centers = [Vector((( R_TOT-rc)*math.cos(math.radians(a)), (R_TOT-rc)*math.sin(math.radians(a))))
               for a in (90, 210, 330)]
    pts = []
    for i in range(3):
        c0, c1 = centers[i], centers[(i+1) % 3]
        # 角 i 的圆弧：从与上一条边的切点到与下一条边的切点
        # 切点方向 = 边法线；直边时法线垂直于 c0->c1
        d = (c1 - c0).normalized()
        nrm = Vector((d.y, -d.x))                     # 朝外法线（三角逆时针，外侧在右）
        prev = centers[i-1]
        dp = (c0 - prev).normalized(); nrm_p = Vector((dp.y, -dp.x))
        a0 = math.atan2(nrm_p.y, nrm_p.x); a1 = math.atan2(nrm.y, nrm.x)
        dd = (a1 - a0 + math.pi) % (2*math.pi) - math.pi
        pts += [(c0.x + rc*math.cos(a0 + dd*k/P["N_CORNER"]), c0.y + rc*math.sin(a0 + dd*k/P["N_CORNER"]))
                for k in range(P["N_CORNER"]+1)]
        # 边：从角 i 切点到角 i+1 切点，中点向内凹 sag
        p0 = c0 + nrm*rc; p1 = c1 + nrm*rc
        for k in range(1, P["N_SIDE"]):
            u = k / P["N_SIDE"]
            q = p0.lerp(p1, u) - nrm * (sag * 4*u*(1-u))  # 抛物线内凹
            pts.append((q.x, q.y))
    area = sum(pts[i][0]*pts[(i+1)%len(pts)][1] - pts[(i+1)%len(pts)][0]*pts[i][1] for i in range(len(pts)))
    if area < 0: pts.reverse()
    return pts

def pocket_outline(angle_deg):
    """角部凹槽：尖点朝圆心的三角，外边沿机身圆角弧内缩 POCKET_WALL，再整体圆角。"""
    ax = math.radians(angle_deg)
    apex = (P["POCKET_APEX"]*math.cos(ax), P["POCKET_APEX"]*math.sin(ax))
    rc_c = R_TOT - P["CORNER_R"]                              # 机身圆角圆心距
    cc = (rc_c*math.cos(ax), rc_c*math.sin(ax))
    Ro = P["CORNER_R"] - P["POCKET_WALL"]                     # 凹槽外弧半径（与机身圆角同心）
    h = math.radians(P["POCKET_HALF"])
    def ray_hit(theta):
        dx, dy = math.cos(ax+theta), math.sin(ax+theta)
        ox, oy = apex[0]-cc[0], apex[1]-cc[1]
        b = 2*(ox*dx + oy*dy); c = ox*ox + oy*oy - Ro*Ro
        disc = b*b - 4*c
        if disc < 0: raise ValueError("POCKET_HALF 太大或 POCKET_APEX 太近，侧边射线打不到外弧")
        t = (-b + math.sqrt(disc)) / 2
        return (apex[0] + t*dx, apex[1] + t*dy)
    pR, pL = ray_hit(-h), ray_hit(+h)
    # 外弧上采样几个点，让凹槽外边跟着圆角走
    a0 = math.atan2(pR[1]-cc[1], pR[0]-cc[0]); a1 = math.atan2(pL[1]-cc[1], pL[0]-cc[0])
    d = (a1 - a0 + math.pi) % (2*math.pi) - math.pi
    outer = [(cc[0] + Ro*math.cos(a0 + d*k/6), cc[1] + Ro*math.sin(a0 + d*k/6)) for k in range(7)]
    poly = [apex] + outer
    area = sum(poly[i][0]*poly[(i+1)%len(poly)][1] - poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))
    if area < 0: poly.reverse()
    # 只对三个真正的角做圆角：尖点和外弧两端
    return fillet_polygon(poly, P["POCKET_ROUND"], 6)

# ============================================================ mesh 工具
def prism(name, pts, z0, z1, taper=0.0, z_taper_end=None):
    """由平面轮廓拉伸成棱柱。
    taper>0：底面 z0 处轮廓向内偏移 taper，到 z_taper_end 处恢复原轮廓，再竖直到 z1（斜壁凹槽切刀）。"""
    bm = bmesh.new()
    cx = sum(p[0] for p in pts)/len(pts); cy = sum(p[1] for p in pts)/len(pts)
    rmean = sum(math.hypot(p[0]-cx, p[1]-cy) for p in pts)/len(pts)
    k = max(0.05, 1 - taper/rmean)
    inset = lambda p: (cx + (p[0]-cx)*k, cy + (p[1]-cy)*k)
    n = len(pts)
    loops = []
    if taper > 0:
        loops.append([bm.verts.new((*inset(p), z0)) for p in pts])
        loops.append([bm.verts.new((p[0], p[1], z_taper_end)) for p in pts])
    else:
        loops.append([bm.verts.new((p[0], p[1], z0)) for p in pts])
    loops.append([bm.verts.new((p[0], p[1], z1)) for p in pts])
    bm.faces.new(loops[0]); bm.faces.new(list(reversed(loops[-1])))
    for lo, hi in zip(loops[:-1], loops[1:]):
        for i in range(n):
            j = (i+1) % n
            bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); link(ob)
    return ob

def cylinder(name, r, z0, z1, seg):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=seg, radius1=r, radius2=r, depth=z1-z0)
    for v in bm.verts: v.co.z += (z0+z1)/2
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); link(ob)
    return ob

def cutter(ob):
    ob.display_type = "WIRE"; ob.hide_render = True
    return ob

def boolean(target, tool, op="DIFFERENCE"):
    m = target.modifiers.new("Bool_" + tool.name, "BOOLEAN")
    m.operation = op; m.object = tool; m.solver = "EXACT"

# ============================================================ 机身
def build_body():
    body = prism("SP_Body", body_outline(), 0.0, P["BODY_H"])
    # 盖孔：从盖座面向上打穿
    bore = cutter(cylinder("SP_cut_bore", R_IN, P["CAP_SEAT_Z"], P["BODY_H"] + 5, P["N_BORE"]))
    boolean(body, bore)
    # 轴承孔：穿透
    brg = cutter(cylinder("SP_cut_bearing", P["BEARING_R"], -1, P["BODY_H"] + 5, P["N_BORE"]))
    boolean(body, brg)
    # 三个角部凹槽：斜壁，底面内缩 depth·tan(chamf)
    taper = P["POCKET_DEPTH"] * math.tan(math.radians(90 - P["POCKET_CHAMF"]))
    for a in (90, 210, 330):
        pk = cutter(prism("SP_cut_pocket_%d" % a, pocket_outline(a),
                          P["BODY_H"] - P["POCKET_DEPTH"], P["BODY_H"] + 5,
                          taper=taper, z_taper_end=P["BODY_H"]))
        boolean(body, pk)
    add_bevel(body)
    return body

# ============================================================ 盖体
def build_cap():
    N = P["WEDGE_N"]
    bm = bmesh.new()
    inner = [bm.verts.new((R_DISC*math.cos(a), R_DISC*math.sin(a), Z_TOP))
             for a in (math.radians(360*k/N + 180/N) for k in range(N))]
    outer = [bm.verts.new((R_CAP*math.cos(a), R_CAP*math.sin(a), Z_RIM))
             for a in (math.radians(360*k/N) for k in range(N))]
    base  = [bm.verts.new((R_CAP*math.cos(a), R_CAP*math.sin(a), P["CAP_SEAT_Z"]))
             for a in (math.radians(360*k/N) for k in range(N))]

    disc = bm.faces.new(inner); disc.material_index = 1        # 车削平盘
    for k in range(N):                                        # 48 三角楔，锯齿脊线
        k1 = (k+1) % N
        bm.faces.new((outer[k], outer[k1], inner[k]))         # 尖朝内
        bm.faces.new((inner[k], outer[k1], inner[k1]))        # 尖朝外
    for k in range(N):                                        # 侧壁
        k1 = (k+1) % N
        bm.faces.new((base[k], base[k1], outer[k1], outer[k]))
    bm.faces.new(list(reversed(base)))                        # 底面
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    me = bpy.data.meshes.new("SP_Cap"); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("SP_Cap", me); link(ob); add_bevel(ob)
    return ob

# ============================================================ 材质
def mat_steel(name, rough, disc=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = P["STEEL_BASE"]
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = rough
    nt.links.new(bsdf.outputs[0], out.inputs[0])
    if disc:
        bsdf.inputs["Anisotropic"].default_value = P["ANISO_DISC"]
        tan = nt.nodes.new("ShaderNodeTangent"); tan.direction_type = "RADIAL"; tan.axis = "Z"
        nt.links.new(tan.outputs[0], bsdf.inputs["Tangent"])
        coord = nt.nodes.new("ShaderNodeTexCoord")
        wave = nt.nodes.new("ShaderNodeTexWave")
        wave.wave_type = "RINGS"; wave.rings_direction = "Z"
        wave.inputs["Scale"].default_value = P["RINGS_SCALE"]
        wave.inputs["Distortion"].default_value = P["RINGS_DISTORT"]
        wave.inputs["Detail"].default_value = 2.0
        bump = nt.nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = P["RINGS_BUMP"]
        bump.inputs["Distance"].default_value = 0.01
        nt.links.new(coord.outputs["Object"], wave.inputs["Vector"])
        nt.links.new(wave.outputs["Fac"], bump.inputs["Height"])
        nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return m

def mat_dark():
    m = bpy.data.materials.new("SP_Dark"); m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.02, 0.02, 0.02, 1)
    b.inputs["Metallic"].default_value = 1.0; b.inputs["Roughness"].default_value = 0.5
    return m

# ============================================================ 主流程
def main():
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"; sc.unit_settings.scale_length = 0.001
    sc.unit_settings.length_unit = "MILLIMETERS"
    rm_prev()

    satin = mat_steel("SP_Steel_Satin", P["ROUGH_SATIN"])
    disc  = mat_steel("SP_Steel_Turned", P["ROUGH_DISC"], disc=True)

    body = build_body(); body.data.materials.append(satin)
    cap = build_cap(); cap.data.materials.append(satin); cap.data.materials.append(disc)

    print("---- rev-005 derived ----")
    print("R_TOT %.2f  R_CAP %.2f  R_IN %.2f  R_DISC %.2f" % (R_TOT, R_CAP, R_IN, R_DISC))
    print("Z_TOP %.2f  Z_RIM %.2f  (body top %.2f, rim %+.2f vs body)" %
          (Z_TOP, Z_RIM, P["BODY_H"], Z_RIM - P["BODY_H"]))
    inr = (R_TOT - P["CORNER_R"])/2 + P["CORNER_R"] - P["SIDE_SAG"]
    print("side midpoint radius %.2f  -> wall to bore %.2f mm (must be > 1.0)" % (inr, inr - R_IN))
    print("pocket apex %.2f  -> wall to bore %.2f mm (must be > 1.0)" % (P["POCKET_APEX"], P["POCKET_APEX"] - R_IN))

main()
