---
kind: tool
status: draftable
audience: []
market: []
portfolio_stage: production
updated: 2026-09-10
last_verified: 2026-09-10
---

# TRI-SPINNER SLAB V3：Blender → Unity Agent 实施规范

> 适用模型：`premium-display-case`
>
> 视觉变体：`tri-spinner-slab-v3-cmf`
>
> 当前状态：**概念目标与实施起始参数，不是 Gate 03 已批准的建模合同，也不是制造图。**

**[AI 协作总结]** 本文把用户给出的视觉要求、当前概念图、现有 Fidgeting 模型管线约束和 Blender/Unity 实施参数整理为可执行草案；正式建模数值仍须按 Gate 审核和用户视觉批准更新。

## 0. Agent 必须先理解的结论

本方案的目标不是“给现有厚盒子换一套材质”，而是重做一个更薄、更开放、更精致的展示框系统：透明水晶感外框只建立边界和高光，不在陀螺正面形成完整透明盖板；陀螺允许部分高出框体前表面；内部依靠微喷砂银、缎面拉丝银、窄镜面银、深石墨和少量浅香槟金形成层级；柔焦只作用于高光，不得把轮廓、文字和材质分界整体模糊。

实施时必须遵守以下边界：

1. `premium-display-case` 是盒体模型，陀螺是由调用方挂到 `ContentSlot` 的独立内容物。
2. 不得重建、重拓扑、改比例、改 pivot、改材质或把陀螺合并进盒体 FBX。
3. 产品预览和 Unity UI 中必须始终显示完整组装状态；爆炸图只可作为内部技术证据。
4. 当前 V3 正面图是 `ai-target / concept-only`，只证明视觉方向，不证明真实厚度、装配、公差或制造结构。
5. 旧合同中的 `228 × 304 × 59 mm`、`10 × 9 mm` 连续管框以及旧 ContentSlot 尺寸，不得复制到这个新方案。
6. 所有真实尺寸都必须来自卡尺、正交照片、已有源模型或明确的用户临时授权；Agent 不得“看起来差不多”后写成 measured。

## 1. 机器决策词汇

每个参数必须同时带 `evidence_class` 和 `value_state`。缺少任一字段即视为非法输入。

| `evidence_class` | 含义 | Agent 行为 |
|---|---|---|
| `user_requirement` | 用户明确说出的设计要求 | 不得静默违背；如需改变必须重新确认 |
| `repository_constraint` | 现有工程和管线已经锁定的约束 | 直接遵守；冲突时停止并报告 |
| `measured` | 有卡尺、源模型或可复核证据的真实值 | 可作为几何权威输入 |
| `user_authorized_provisional` | 用户明确允许暂用的临时值 | 可做概念白模；不得升级为 measured |
| `recommended_start` | 根据视觉目标给出的首轮参数 | 允许迭代；不得称为已批准 |
| `unknown` | 当前没有证据 | 保持 `null`，禁止补猜 |
| `derived` | 由已登记参数和公式计算 | 必须记录依赖和公式，禁止手填 |

`value_state` 只能是：

```text
unresolved | provisional | visual_locked | measured | repository_locked | derived | approved
```

Fail-closed 规则：

- `unknown` 或未解决的关键 `measured` 输入不得被默认值偷偷替代。
- 只有 JSON 中存在对应 `provisional_value`，并登记用户授权事件，才可用临时值进入概念白模。
- 临时值生成的任何导出物必须带水印或 manifest 标记：`PROVISIONAL_DIMENSIONS`。
- 制造、公差、碰撞和装配结论不得建立在视觉阴影缝或 AI 图像上。

## 2. 可直接交给实施 Agent 的任务指令

```text
你正在实现 premium-display-case 的 tri-spinner-slab-v3-cmf 变体。

先读取仓库 AGENTS.md、产品 Design Bible、IMPLEMENTATION_STATUS、
premium-display-case/pipeline.json、当前 Gate 03 合同、Gate 04 架构和
ArtSource/MaterialLibrary/materials.json。运行模型管线校验器并从报告中的
earliest_problem 开始。不要跳 Gate，不要修改 shipping asset。

把随附 V3 图片当成 concept-only 视觉目标，不是尺寸或制造真值。
先补齐 Gate 01 来源、哈希与角色，再做新的 Gate 02 分析和 Gate 03 合同。
旧 228×304×59 mm 厚盒合同已不适用于新概念。

建模必须由可重复运行的 bpy builder 生成，参数全部读取
tri-spinner-slab-model-spec.v0.json；不得手拖顶点完成最终模型。保持
PresentationRoot → CaseAssembly → ContentSlot 集成边界。陀螺只作为
锁定的 review input 出现在审查场景，盒体导出中 ContentSlot 保持空。

视觉目标：更薄、部分深度包围、陀螺前部露出；透明框只有克制的边缘
晶体感；内场由微喷砂、缎面拉丝、窄镜面与不连续浅香槟金构成；金色
不能闭合成整圈；中心呼吸区保持安静；灯光中性、彩边极少；柔焦仅用于
最终 Beauty 的高光蒙版，不能模糊文字、轮廓和材质分界。

每一 Gate 输出 manifest、源文件、参数快照、版本、相机 recipe、哈希、
自动检查和可视证据。任一上游源或合同哈希改变时，将本 Gate 及全部下游
标 stale。没有明确视觉批准，不得进入下一 Gate；没有 Gate 12 批准，
不得替换 shipping asset 或安装到手机。
```

## 3. 当前来源和证据等级

| 来源 | 角色 | 状态 | SHA-256 |
|---|---|---|---|
| `01-front-cmf-gold-silver.png` | V3 干净正面 CMF 目标 | `ai-target / concept-only` | `65d506290af9c0fe73e60a0c0d3eab4420e6b7da60a266be597e34a62a602769` |
| 用户蓝/红框批注图，416×654 px | 指定 header 与 main bay 的修改范围 | `annotated-feedback` | `83acc2eb1ef6e0353222414e09f680a6cdb2a3a146ad5799182fc34072758f50` |
| V2 soft-light 图组 | 光感克制与柔焦方向 | `ai-target / concept-only` | Gate 01 登记时逐文件计算 |
| 真实陀螺源模型 | 几何、pivot、材质权威源 | `caller-owned / immutable` | 当前未登记，必须补齐 |

从带框批注图估算的外框区域约为 `[36,15]–[379,625]`。所有像素比例都必须在无标注 V3/V2 图上复核；批注线本身不可进入轮廓测量。

## 4. 视觉比例：首轮参数，不是实测尺寸

以下值来自当前正面目标的像素关系，统一标记为 `recommended_start`。只有用户在 3D 白模中确认后，才可升级为 `approved`。

| 参数 ID | 起点 | 容差/搜索范围 | 说明 |
|---|---:|---:|---|
| `visual.case_width_over_height` | `0.562` | `±0.006` | 整体比旧 3:4 更修长 |
| `visual.header_split_from_top` | `0.321H` | `±0.006H` | header/main 的水平分界 |
| `visual.frame_band_over_width` | `0.052W` | `±0.006W` | 外框正面视觉带宽 |
| `visual.main_window_side_inset` | `0.052W` | `±0.006W` | 主区域左右 inset |
| `visual.spinner_span_over_width` | `0.762W` | `±0.010W` | 陀螺最大横向 span |
| `visual.spinner_center_x` | `0.500W` | `±0.004W` | 水平居中 |
| `visual.spinner_center_from_top` | `0.650H` | `±0.008H` | 轴承中心纵向位置 |
| `visual.outer_corner_radius` | `0.040W` | `±0.008W` | 外轮廓圆角 |
| `visual.inner_corner_radius` | `0.028W` | `±0.006W` | 内场圆角 |

当前定性要求：

- `front_cover_over_spinner = false`：陀螺正面没有整片透明盖板。
- `enclosure_depth_mode = partial_depth`：框体只覆盖陀螺厚度的一部分。
- `spinner_orientation = one_tip_up`。
- `gold_path = two_discontinuous_segments_plus_one_small_index`，不得闭合为整圈金边。
- `center_breathing_zone = quiet`：陀螺周围不可堆满纹理、线条或发光元素。
- `lighting_style = restrained_neutral_soft`：不允许 RGB 霓虹主导。

以规范化正面坐标左上角 `(0,0)`、右下角 `(1,1)` 表达：

```text
case_width  = spinner.max_span / 0.762
case_height = case_width / 0.562
header_y    = 0.321 × case_height from top
spinner_x   = 0.500 × case_width from left
spinner_y   = 0.650 × case_height from top
```

如果仅为概念白模使用用户曾授权的 `spinner.max_span = 85 mm` 临时值，则预览推导为：

```text
case_width_preview  = 85 / 0.762 = 111.55 mm
case_height_preview = 111.55 / 0.562 = 198.49 mm
header_height       = 63.72 mm
frame_band          = 5.80 mm
spinner_center_y    = -29.77 mm relative to case center, +Y upward
```

这些结果必须显示为 `PROVISIONAL`；正式建模仍需真实陀螺 span 与厚度。

## 5. 厚度策略

用户要求的是“视觉上明显变薄，并让陀螺部分高出框体”，不是简单把所有 Z 轴统一缩放。

### 5.1 必须实测

```text
spinner.max_span_mm       = 真实模型 bounds 或卡尺
spinner.max_thickness_mm  = 包含最高 cap/尖端后的最大厚度
spinner.pivot             = 真实轴承中心
```

当前：

- `spinner.max_span_mm.value = null`
- `spinner.max_span_mm.provisional_value = 85.0`
- `spinner.max_thickness_mm = null`
- `retention.mechanism = null`
- `manufacturing.clearance_mm = null`
- `manufacturing.tolerance_mm = null`
- `manufacturing.draft_angle_deg = null`

### 5.2 首轮结构起点

| 参数 | 起点 | 允许搜索范围 | 等级 |
|---|---:|---:|---|
| 后板厚度 | `2.40 mm` | `2.0–2.8 mm` | `recommended_start` |
| 透明框实际壁厚 | `1.50 mm` | `1.3–1.8 mm` | `recommended_start` |
| 烟灰紫 liner 厚度 | `0.85 mm` | `0.7–1.0 mm` | `recommended_start` |
| 框体覆盖陀螺厚度 | `0.58T` | `0.55–0.65T` | `recommended_start` |
| 陀螺高出框体 | `0.42T` | `0.35–0.45T` | `derived` |
| 视觉阴影缝 | `0.20 mm` | `0.15–0.30 mm` | `recommended_start` |
| 透明框主倒角 | `0.45 mm` | `0.35–0.55 mm` | `recommended_start` |
| 内层倒角 | `0.275 mm` | `0.20–0.35 mm` | `recommended_start` |
| header 浅台阶 | `0.30 mm` | `0.25–0.35 mm` | `recommended_start` |
| main bay 浅台阶 | `0.40 mm` | `0.30–0.50 mm`，上限 `0.60 mm` | `recommended_start` |
| 金属周边 shelf | `4.50 mm` | 约 `0.040–0.052W` | `recommended_start` |
| 镜面窄缝 | `0.35 mm` | `0.25–0.45 mm` | `recommended_start` |
| 金色嵌条宽度 | `0.25 mm` | `0.18–0.35 mm` | `recommended_start` |
| 金色凸起 | `0.03 mm` | `0–0.06 mm` | `recommended_start` |

注意：`visual_shadow_gap_mm` 只控制反光断层，不等于制造间隙。

### 5.3 深度公式

规范产品坐标使用 `+Z` 朝正面。builder 可先在“后表面为 `z=0`”的 construction space 生成，再整体平移到 assembled envelope center：

```text
z_rear_outer             = 0
z_backplate_front        = backplate_thickness
z_spinner_back           = z_backplate_front + content_rear_gap
z_spinner_front          = z_spinner_back + spinner_thickness
z_frame_front            = z_spinner_back + frame_coverage × spinner_thickness
spinner_protrusion       = z_spinner_front - z_frame_front
                         = (1 - frame_coverage) × spinner_thickness
assembled_envelope_depth = max(z_spinner_front, z_frame_front) - z_rear_outer
root_recentering_z       = -0.5 × assembled_envelope_depth
```

自动断言：

```text
abs(frame_coverage + protrusion_ratio - 1.0) <= 0.001
abs(frame_front_height + spinner_protrusion - spinner_thickness) <= 0.01 mm
0.35 <= protrusion_ratio <= 0.45
```

## 6. 坐标、单位与轴向转换

为了与现有 `premium-display-case` 管线兼容，合同坐标与 Blender 原生坐标必须明确分开。

### 6.1 Canonical 产品坐标

```text
+X = 右
+Y = 上
+Z = 正面/朝观察者
origin = 完整组装外包围盒中心
unit = millimeter
```

### 6.2 Blender 5.2 原生坐标

```text
Blender +X = Canonical +X
Blender +Z = Canonical +Y
Blender -Y = Canonical +Z
1 BU = 1 meter
mm_to_BU = 0.001
```

Canonical → Blender：

```text
B.x =  C.x
B.y = -C.z
B.z =  C.y
```

### 6.3 Unity 6000.5.6f1 坐标

```text
Unity +X = Canonical +X
Unity +Y = Canonical +Y
Unity +Z = Canonical +Z
1 Unity unit = 1 meter
```

FBX/GLB exporter 必须由一个固定 recipe 完成轴向转换；禁止导入后靠 `Rotation = (90,0,0)` 或负 scale 补救。Unity prefab 根节点必须为：

```text
Position = (0,0,0)
Rotation = (0,0,0)
Scale    = (1,1,1)
```

导出前使用带 `+X/+Y/+Z` 标签的非对称 axis probe 验证，不凭 inspector 看起来“朝向正确”判断。

## 7. 层级、所有权和命名

### 7.1 Unity 导出层级

```text
PresentationRoot                    # 展示动作与整盒 transform owner
└── CaseAssembly                    # 盒体几何
    ├── OuterCrystalFrame
    ├── SmokeInnerLiner
    ├── HeaderCompartment
    │   ├── HeaderGraphitePlane
    │   ├── HeaderSatinShelf
    │   ├── HeaderMirrorBevel
    │   ├── HeaderSilverDatumRail
    │   ├── HeaderGoldInlayL
    │   └── HeaderGoldInlayR
    ├── MainCompartment
    │   ├── MainMicroblastField
    │   ├── MainSatinShelf
    │   ├── MainMirrorSeam
    │   ├── MainBrushedPanelL
    │   ├── MainBrushedPanelR
    │   ├── MainBrushedBandBottom
    │   ├── MainCornerFacets
    │   ├── MainGoldRail00
    │   ├── MainGoldRail01
    │   └── MainGoldIndexTab
    ├── RearPlate
    └── ContentSlot                 # 空 anchor；陀螺由调用方挂载
```

### 7.2 Blender collections

```text
COL_PDC_ROOT
├── COL_PDC_REFERENCE_LOCKED        # 不导出；含 linked review spinner
├── COL_PDC_CUTTERS                 # 不导出
├── COL_PDC_GEOMETRY_STATIC
├── COL_PDC_DECALS
├── COL_PDC_CONTROLS
├── COL_PDC_COLLISION
├── COL_PDC_CAMERAS
├── COL_PDC_LIGHTS_NEUTRAL
├── COL_PDC_LIGHTS_BEAUTY
├── COL_PDC_LOOKDEV
├── COL_PDC_EXPORT
└── COL_PDC_DEBUG                   # 不导出
```

技术对象使用：

```text
^(COL|ROOT|GEO|CUT|PIVOT|COLLIDER|CAM|LGT|DECAL|MAT|NG|TEX)_PDC_[A-Z0-9_]+$
```

发现 `.001`、重复 material slot 或自动生成名称时验证直接失败。

每个对象必须写入 custom properties：

```text
asset_id
variant_id
contract_sha256
geometry_source
evidence_class
export_role
immutable_geometry
cmf_zone_id
softfocus_eligible
```

锁定陀螺 review object 必须保存源 mesh SHA-256；它不属于 `COL_PDC_EXPORT`。

## 8. Blender 几何 builder

最终源模型必须由确定性 `bpy` 脚本重建。所有数值来自 JSON，不允许脚本中再藏一套 magic numbers。

### 8.1 推荐 modifier 顺序

```text
010_MIRROR_X                   # 只有确实采用半模时
020_BOOLEAN_MAIN_CUT_EXACT     # 能解析建面则省略
021_BOOLEAN_HEADER_CUT_EXACT
022_BOOLEAN_DETAIL_CUT_EXACT
030_BEVEL_PRIMARY
040_BEVEL_MICRO
050_WEIGHTED_NORMAL
060_WRITE_FACE_ATTRIBUTES
090_TRIANGULATE_EXPORT         # 源模型关闭，仅 export duplicate 开启
```

### 8.2 硬规则

- 外框、liner 和所有浅台阶都必须为 watertight solid；透明框禁止用单面壳加 Alpha 冒充厚度。
- 透明嵌套面之间不得共面；渲染分离最小 `0.02 mm`，装配间隙另行定义。
- 能用解析 rounded-rectangle topology 时不用 Boolean；必须使用 Boolean 时 solver 为 `EXACT`，cutter 保留并稳定命名。
- 不使用 Subdivision Surface 改变设计尺寸。
- `0.20 mm` 以上结构断层使用真实几何；小于 `0.20 mm` 的喷砂、拉丝和微纹理使用 normal/roughness。
- Bevel `profile = 0.5`，Clamp Overlap 开；宽度不得超过局部最小壁厚或台阶宽度的 `35%`。
- 外框主倒角 4 segments，内层 3，微倒角 2；最终视距不够时才可在 Gate 06 调整。
- Weighted Normal 位于全部 Bevel 之后；Smooth by Angle 起点 `30°`。
- `edge_iridescence_mask` 必须由 builder 写入显式 attribute，不使用会随拓扑变化的 Pointiness。
- 金色几何只允许 `Rail00`、`Rail01` 和小型 `IndexTab`；不得生成闭合金边。
- header/main 的断层是浅台阶与反光关系，不是厚重的多层积木。

### 8.3 顶点数据通道

```text
COLOR0.r = edge_thickness_mask
COLOR0.g = edge_iridescence_mask
COLOR0.b = finish_mix_mask
COLOR0.a = 1.0
UV2.x    = brushing_angle_normalized
UV2.y    = cmf_zone_id / 255.0
```

导出验证必须确认这些通道在 Unity 中数值不漂移。

## 9. CMF 分区与材质参数

### 9.1 面积与层级

以 header + main bay 的可见内部区域为分母：

```text
浅香槟金：5–8%，硬上限 8%
冷银 + 石墨：92–95%
微喷砂：55–60%
缎面/线性拉丝：25–30%
窄镜面：12–15%，极限不超过 18%
```

中心陀螺周围至少保留一个不被金线、文字或高反细节切穿的安静区域。金色负责“索引与节奏”，不是装饰性包边。

### 9.2 材质槽预算

盒体最多 7 个材质槽：

1. `case-clear-crystal`（新材质，待 Material Library 批准）
2. `case-smoke-lilac-liner`（新材质，待批准）
3. `case-backplate-microblast`（新材质或由 `blade-sandblast` 派生，待批准）
4. `case-header-graphite`（新材质，待批准）
5. `steel-satin`（优先复用现有库）
6. `case-smoked-mirror-silver`（新材质，待批准）
7. `case-champagne-gold-inlay`（新材质，待批准）

陀螺是独立 prefab，使用它自己的已登记材质；不得为凑效果覆盖。现有 `gold-mesh` 偏橙、偏粗糙且用途不同，不得直接当作浅香槟金。

### 9.3 Blender Principled BSDF 起点

所有颜色必须记录色彩空间。Unity Hex 是 sRGB；Blender 数值使用 scene-linear。转换公式：

```text
if srgb <= 0.04045: linear = srgb / 12.92
else:               linear = ((srgb + 0.055) / 1.055) ^ 2.4
```

| 材质 ID | sRGB 起点 | Metallic | Roughness | IOR | Transmission | 关键参数 |
|---|---|---:|---:|---:|---:|---|
| `case-clear-crystal` | `#F8FBFF` | `0` | `0.025–0.045` | `1.49` | `1.0` | Coat `0.08`，Coat Roughness `0.03`，真实厚度，无 emission |
| `case-smoke-lilac-liner` | `#EEEAF4`，极低饱和 | `0` | `0.12–0.18` | `1.49` | `0.70–0.85` | 用 Volume Absorption 控透过率，不把烟色烘进阴影 |
| `case-backplate-microblast` | `#AEB3B6` | `1` | `0.40–0.50` | — | `0` | 颗粒 `0.08–0.18 mm`，bump `0.006–0.015 mm`，roughness ±`0.03` |
| `case-header-graphite` | `#1C1E22` | `0.05` | `0.38–0.48` | `1.50` | `0` | 低对比微颗粒，禁止纯黑塑料感 |
| `steel-satin` | 使用 Material Library 原值 | `1` | `0.32–0.38` | — | `0` | Anisotropy `0.20–0.30`，拉丝 pitch `0.04–0.08 mm` |
| `case-smoked-mirror-silver` | `#667078` 起点 | `1` | `0.06–0.10` | — | `0` | 仅窄缝/倒角，无可见颗粒 |
| `case-champagne-gold-inlay` | `#C8B48B` | `1` | `0.22–0.30` | — | `0` | Anisotropy `0.10–0.20`，不发光、不偏橙 |

薄膜彩边只在 `edge_iridescence_mask` 内：

```text
Thin Film Thickness = 280–380 nm
Thin Film IOR       = 1.33–1.38
mask visible area   < 8% of outer-frame pixels
```

不得给整片透明材质添加强 rainbow。Blender 5.2 socket 必须按名称查找，避免版本索引漂移：

```python
transmission = bsdf.inputs.get("Transmission Weight") or bsdf.inputs.get("Transmission")
coat = bsdf.inputs.get("Coat Weight") or bsdf.inputs.get("Clearcoat")
anisotropy = bsdf.inputs.get("Anisotropic IOR Level") or bsdf.inputs.get("Anisotropic")
```

程序微纹理必须在 manifest 存储：

```text
feature_mm
height_um
roughness_delta
seed
mapping_axis
```

频率换算：`cycles_per_meter = 1000 / feature_mm`；bump distance：`height_um × 1e-6 meter`。

## 10. Blender 灯光与渲染

### 10.1 中性验证灯：Gate 07

```text
Key   5600 K  relative 1.00
Fill  5600 K  relative 0.25
Rear  5600 K  relative 0.18
Background #050608–#0A0B0D
Bloom off
DOF off
彩灯 off
高反地面 off
```

先用 18% Lambert 灰卡校准 Key + Fill，使 scene-linear `Y = 0.18 ± 0.02`；将得到的实际灯光功率写入 manifest。不要在规范里把瓦数写死，因为模型尺度和 Cycles 设备会影响可比性。

### 10.2 Beauty 灯光：Gate 08

以下位置在 hero-camera local space 中表示，`P` 为产品中心，`B` 为组装包围盒对角线：

| 灯 | Position × B | Size × B | 色温/颜色 | 相对 Key |
|---|---|---|---|---:|
| Soft Key | `[-0.70,+0.72,+0.80]` | `0.85×0.40` | `5600 K` | `1.00` |
| Right Strip | `[+0.72,+0.12,+0.55]` | `0.055×0.95` | `6500 K` | `0.35–0.45` |
| Top Rail | `[-0.05,+0.88,+0.15]` | `0.58×0.045` | `5000 K` | `0.12–0.18` |
| Cool rim，可选 | `[-0.50,+0.10,-0.48]` | `0.045×0.58` | `#77D8FF` | `≤0.05` |
| Lilac rim，可选 | `[+0.48,-0.02,-0.52]` | `0.045×0.50` | `#C9A7FF` | `≤0.03` |
| Front Fill | `[0,-0.28,+1.05]` | `0.95×0.60` | `6000 K` | `0.05–0.08` |

彩色灯合计能量不超过白光的 `8%`，只允许触及边缘、倒角和窄接缝。目标是比早期 neon 方案减少 `70–85%` 的可见彩色光。

每盏灯单独 Light Group。迭代顺序固定为：

```text
1 exposure → 2 material roughness → 3 light position/size → 4 soft-focus
```

禁止四项同时调整，否则 Agent 无法判断改善来自哪里。

### 10.3 Cycles 5.2 LTS

| 项目 | 六面/材质板 | Hero | Turntable |
|---|---:|---:|---:|
| Samples | `512` | `1024`，最终可升 `2048` | `1024` |
| Adaptive threshold | `0.005` | `0.0025` | `0.004` |
| Min samples | `64` | `128` | `64` |
| Denoiser | OIDN Albedo + Normal | 同左 | 同左 |

共同设置：

```text
Light Tree          On
Total Bounces       20
Diffuse             4
Glossy              8
Transmission        16
Transparent         16
Volume              2
Minimum Bounces     3
Reflective Caustics On for beauty; parity set must record state
Refractive Caustics On for beauty; parity set must record state
Clamp Direct        0
Clamp Indirect      8–10
Filter Glossy       0.20–0.30
Pixel Filter        Blackman-Harris, 1.0 px
Motion Blur         Off
DOF                 Off for all validation views
Animated Seed       Off
```

色彩管理起点：`AgX / Medium High Contrast / Exposure -0.25 EV`。这是 `recommended_start`，跨引擎比较的权威是 scene-linear EXR，不是两个引擎各自 tone-mapped 后的 PNG。

输出：

```text
32-bit multilayer OpenEXR ZIP, scene-linear
16-bit PNG review copies
Combined raw + denoised
Diffuse / Glossy / Transmission
Normal / Depth / Position
Cryptomatte Object + Material
AOV: Roughness / Metallic / IridescenceMask / CMFZoneID
```

微距必须同时保留 raw 和 OIDN 版本，防止 denoiser 抹掉喷砂颗粒。

## 11. Highlight-only 柔焦

柔焦只属于最终 Beauty 合成。六面图、Clay、Normal、Depth、Roughness、材质验证和 Unity parity 全部绕过。

在 scene-linear 空间：

```text
Y = 0.2126R + 0.7152G + 0.0722B
Hmask = smoothstep(0.90, 1.80, Y)
ObjectMask = max(
  CM_outer_crystal,
  CM_mirror_bevel,
  CM_spinner_facets
)
H = Beauty × Hmask × ObjectMask

r1 = 0.0025 × image_long_edge
r2 = 0.0100 × image_long_edge

FinalRGB = Beauty
         + 0.08–0.12 × GaussianBlur(H, r1)
         + 0.02–0.03 × GaussianBlur(H, r2)
FinalAlpha = BeautyAlpha
```

硬规则：

- 只 blur `H`，不 blur Beauty、Alpha、文字、背板或大面积浅色面。
- 不允许全局 Gaussian、Mist、Lens Distortion 或 Chromatic Aberration。
- 必须同时输出 `beauty-clean` 和 `beauty-soft`。
- 若 `beauty-soft` 的非高光区域相对 clean 出现可见清晰度下降，柔焦测试失败。

## 12. 相机与测试视图

### 12.1 六面正交相机

相机 recipe 以 Canonical 坐标保存：

| ID | camera-to-target direction | image up |
|---|---|---|
| `front` | `[0,0,-1]` | `[0,+1,0]` |
| `back` | `[0,0,+1]` | `[0,+1,0]` |
| `left` | `[+1,0,0]` | `[0,+1,0]` |
| `right` | `[-1,0,0]` | `[0,+1,0]` |
| `top` | `[0,-1,0]` | `[0,0,-1]` |
| `bottom` | `[0,+1,0]` | `[0,0,+1]` |

统一规则：

```text
projection = orthographic
resolution = 2048 × 2048
margin_each_side = 6%
DOF = off
motion_blur = off
camera_target = render_bounds_center
camera_distance = 2.5 × max_render_bound
near = max(0.1 mm, 0.001 × max_render_bound)
far = 10 × max_render_bound
```

`ortho_scale`：

```text
max(projected_vertical_extent,
    projected_horizontal_extent / aspect)
÷ (1 - 2 × 0.06)
```

fit bounds 只包含 render mesh，不得包含灯、地面、cutter、debug 或不可见 reference。

### 12.2 Hero 与斜视相机

```text
sensor = 36 × 24 mm
focal_length = 85 mm
hero yaw = 25°
hero elevation = 5°
roll = 0°
frame margin = 8%
DOF = off for parity
```

Beauty 最终图在几何和 parity 通过后，才可试用约 `f/8` 的极轻 DOF；不能用景深掩盖坏边缘。

### 12.3 必交视图

1. `front/back/top/bottom/left/right` 六面正交图。
2. `hero`、`left-oblique`、`right-oblique`、`low-oblique` 四张组装图。
3. 侧面厚度 macro：清楚展示框体覆盖与陀螺 protrusion。
4. header 台阶 macro、main bay CMF macro、透明框倒角 macro。
5. Neutral material board 与 Beauty 对照。
6. Clay、wireframe、normal、depth、roughness、transmission、material ID。
7. `beauty-clean` 与 `beauty-soft` 同构图 A/B。
8. 固定相机与灯、只旋转 `PresentationRoot` 的 360° turntable：144 帧、每帧 `2.5°`、24 fps、6 秒。
9. 静帧角度：`0° / 25° / 90° / 200° / 335°`。

背面固定结构当前为 `unknown`。Agent 仍须输出 back/bottom 测试相机，但不得为了画面丰富而发明卡扣、螺丝或磁铁。

## 13. Unity 6000.5.6f1 / URP 17.5.0

### 13.1 工程规则

- 读取 `ProjectVersion.txt` 与 `Packages/manifest.json`，不得升级 Unity 或 URP。
- 一米对应一 Unity unit；不允许导入后非均匀缩放。
- object name、material slot、pivot 和层级必须与 Blender export manifest 一致。
- 盒体 FBX 中 `ContentSlot` 为空；运行时实例化调用方拥有的 spinner prefab。
- opaque 先渲染，烟灰 liner 后渲染，clear crystal 最后渲染。

### 13.2 渲染队列

```text
Opaque metal / graphite / rear plate = 2000
Smoke liner                           = 2990
Clear crystal                         = 3000
```

不得用逐相机临时 `sortingOrder` 修补。360° 出现排序 pop 时，优先检查 watertight、face winding、共面、front/back shell 拆分和 depth strategy。

### 13.3 Clear Crystal Shader

使用自定义 URP Shader Graph/HLSL，不使用普通透明 Lit 直接调低 Alpha：

```text
Surface            Transparent
Blend              Premultiplied (One, OneMinusSrcAlpha)
ZWrite color pass  Off
Cull               Back，除非 watertight 双面需求已被证据证明
IOR                1.49
F0                 ((1.49-1)/(1.49+1))² = 0.0387
Smoothness         0.96–0.98
Broad-plane alpha  0.08–0.16
Edge alpha         0.20–0.32 via COLOR0.r
Reflection weight  0.75–1.00
Emission           0
```

若使用 `_CameraOpaqueTexture` 做屏幕空间折射：

```text
refraction_offset = 0.003–0.010 × view_normal × thickness_mask
```

需要在 URP asset 打开 Opaque Texture；该方法不能正确折射同一透明队列中的物体，因此本方案不在陀螺正面设置整片透明盖板，边框折射保持局部。Depth/Normals prepass 只有在证明不隐藏后层透明面时才启用。

### 13.4 Smoke Liner Shader

```text
Surface     Transparent Premultiply
Queue       2990
Base sRGB   #D8D2E0 起点，低饱和
Alpha       0.25–0.45
Smoothness  0.80–0.88
Emission    0
```

### 13.5 金属映射起点

`Unity smoothness = 1 - Blender roughness` 只作为首轮映射；最终以同相机、同环境的视觉 parity 为准。

| 区域 | Unity sRGB | Metallic | Smoothness |
|---|---|---:|---:|
| Main microblast | `#AEB3B6` | `1` | `0.50–0.60` |
| Satin silver | `#C6C8CA` | `1` | `0.62–0.68` |
| Smoked mirror | `#667078` | `1` | `0.90–0.94` |
| Champagne gold | `#C8B48B` | `1` | `0.70–0.78` |
| Header graphite | `#1C1E22` | `0.05` | `0.52–0.62` |

拉丝方向读取 `UV2.x`，finish mix 读取 `COLOR0.b`。不得把 Blender 的高光或彩边烘进 Base Color。

### 13.6 URP Asset、相机和反射环境

```text
HDR                On
Opaque Texture     On only if refraction is enabled
Depth Texture      On
MSAA               4× starting point for target iPhone
Render Scale       1.0
Camera sensor      36 × 24 mm
Camera focal       85 mm for hero
```

Blender 和 Unity 使用同一相机 recipe、同一中性 studio reflection card/cubemap。URP 中金属上“软箱灯的形状”主要由反射环境建立，不能假设实时 Area Light 会与 Cycles 完全相同。

### 13.7 后处理

验证场景：全部关闭。Beauty 场景起点：

```text
Bloom threshold        1.1–1.4
Bloom intensity        0.05–0.12
Bloom scatter          0.45–0.55
Bloom clamp            8–12
Lens Dirt              0
Vignette intensity     0.08–0.12
Vignette smoothness    0.25–0.35
Chromatic Aberration   0
Film Grain             0–0.02
```

若要精确实现柔焦，使用自定义 `ScriptableRendererFeature` 做 highlight-only pass，遵守第 11 节蒙版；不要对全屏做 blur。Tone mapping 使用工程已有设置，并通过校准 LUT 逼近 Blender AgX；不得声称两个 tone mapper 数值等价。

## 14. 性能预算

沿用当前 Gate 03 性能上限，除非新合同另行批准：

```text
case triangles                 <= 120,000
case material slots            <= 7 (hard project ceiling remains 8)
additional realtime lights     <= 3 in shipping runtime
CPU incremental cost           <= 0.2 ms
GPU incremental cost           <= 1.5 ms on target iPhone Release build
managed allocations            = 0 bytes/frame
target                         60 fps
```

Beauty 离线灯光数量不等于 runtime 灯光预算。Unity shipping 使用 reflection probe、烘焙环境和最多三盏必要实时灯复现层次。Simulator 不能通过 GPU 性能 Gate。

## 15. Blender ↔ Unity parity 验收

### 15.1 几何

```text
imported bounds delta                <= 0.1%
front silhouette IoU                 >= 0.995
anchor delta at 2048 px              <= 2 px
root position/rotation               exactly zero within importer tolerance
root scale                           (1,1,1)
negative scale                       forbidden
spinner pivot delta                  <= 0.1 mm
spinner protrusion error             <= 0.25 mm
normals/tangents                     valid, no flipped islands
```

### 15.2 材质与光

```text
transparent mean transmission luma delta   <= 5%
bevel highlight center drift                <= 1% of product width
gold visible-area ratio                     5–8%
iridescent edge visible-area ratio          < 8%
360° transparent sorting pop                0
co-planar transparent overlaps              0
emissive case pixels                        0
```

### 15.3 柔焦

- `beauty-clean` 必须存在并可单独通过审核。
- 柔焦只在已登记的高光/object mask 内产生差异。
- typography、silhouette edge、main bay 纹理的 clean/soft 对比不得出现可见清晰度损失。
- 不允许用 Bloom 或柔焦掩盖透明排序、低面数轮廓或错误法线。

自动指标通过仍不等于视觉批准。透明亮晶晶感、材质层级、厚度精致感和中心留白必须由用户看真实 3D turntable 后确认。

## 16. 12-Gate 执行顺序

当前实际管线校验结果：`premium-display-case` 的最早问题是 **Gate 01 stale**，原因是已登记的 approved baseline PNG 缺失或哈希无法解析。实施 Agent 必须从这里开始。

| Gate | 必做输出 | 本方案特别检查 |
|---|---|---|
| 01 Intake | 来源、角色、路径、SHA-256 | 登记 V2/V3、批注图、真实陀螺源；恢复/处理缺失 baseline |
| 02 Analysis | 比例、材质、厚度、未知项分析 | 分离视觉推断与实测；明确旧合同失效范围 |
| 03 Contract | 新合同 revision 与用户批准 | 锁定尺寸、深度、CMF、相机、预算；未批准不得建最终白模 |
| 04 Architecture | hierarchy、owner、pivot、命名 | 保留 `PresentationRoot/CaseAssembly/ContentSlot`；陀螺 caller-owned |
| 05 Blockout | 交互式白模/完整录屏 | 先批整体比例和厚度，不先做材质 |
| 06 Geometry | 干净几何、六面、wireframe | watertight、无共面、真实浅台阶、protrusion |
| 07 Material | 中性灯材质板/turntable | 金银面积、喷砂/拉丝/镜面分区，不看 Bloom |
| 08 Lighting | 中性与 Beauty rig | 降低彩光，避免廉价霓虹 |
| 09 Environment | 背景、反射卡、柔焦 A/B | 柔焦只能作用高光；clean 必须独立成立 |
| 10 Export | 真实 FBX/GLB、manifest、axis probe | 根变换、单位、vertex channels、空 ContentSlot |
| 11 Unity parity | 真实 URP runtime 与录屏 | 同相机/环境、透明排序、移动端性能 |
| 12 Shipping | 最终视觉批准与发布证据 | 批准前不替换 shipping asset、不安装手机 |

如果 Gate 03 后任一上游尺寸、材料架构或参考图哈希改变，必须将责任 Gate 和所有下游标记为 `stale`。静态截图不能批准 Gate 05–06 几何；材质和透明排序必须看真实 turntable；Unity parity 必须来自真实 Unity runtime。

## 17. 交付目录建议

```text
ArtSource/ModelPipeline/premium-display-case/
├── pipeline.json
├── evidence/
│   ├── 01-intake/rev-XXX/
│   ├── 02-analysis/rev-XXX/
│   ├── 03-contract/rev-XXX/
│   ├── 04-architecture/rev-XXX/
│   ├── 05-blockout/rev-XXX/
│   ├── 06-geometry/rev-XXX/
│   ├── 07-material/rev-XXX/
│   ├── 08-lighting/rev-XXX/
│   ├── 09-environment/rev-XXX/
│   ├── 10-export/rev-XXX/
│   ├── 11-unity-parity/rev-XXX/
│   └── 12-shipping/rev-XXX/
└── staging/tri-spinner-slab-v3-cmf-rXXX/
```

每个 artifact manifest 至少记录：

```text
artifact_id
gate
slot
role
repository_relative_path
producer
producer_version
recipe
camera_id
render_pass
sha256
byte_size
input_contract_sha256
status
```

## 18. 自动验证清单

1. JSON schema 与 typed formula AST 通过；禁止 `eval`。
2. `must_measure/unknown` 在 blocking Gate 前 fail closed。
3. 真实陀螺缺路径或 SHA-256 时，不得批准 Gate 04 integration proof。
4. 六面相机 ID 必须恰好为 `front/back/top/bottom/left/right`。
5. collection、object、material 和 camera 名称唯一；禁止 `.001`。
6. 透明 mesh watertight；法线朝外；无共面双壳。
7. `frame_coverage + protrusion_ratio = 1`。
8. spinner pivot 与源模型轴承中心偏差 `≤0.1 mm`。
9. export root rotation 为零、scale 为一，无负 scale。
10. 金色可见面积 `5–8%`，不连续且不闭环。
11. 彩边只存在于 `edge_iridescence_mask`，面积 `<8%`。
12. soft-focus 只允许作用于 Beauty，并同时存在 clean 对照。
13. Blender/Unity 共用相机 recipe；不允许分别手调构图。
14. 360° 中透明排序无跳变、消失或错误遮挡。
15. 任一 source/contract hash 改变，当前 Gate 和所有下游变为 `stale`。
16. 产品预览始终是完整盒体；不得把技术爆炸图送进 shipping UI。

## 19. 人工批准节点

Agent 不得把“自动测试通过”解释为“用户已批准”。至少需要四次明确视觉批准：

1. 白模比例与厚度：正面 + 侧面 + 360°。
2. 几何细节：header/main 分层、圆角、断层和 protrusion。
3. 中性光材质：喷砂、拉丝、镜面和金色比例。
4. Unity 真机/目标设备：透明排序、反光、柔焦和性能。

只有第 4 项和 Gate 12 同时通过，才可替换 shipping asset。
