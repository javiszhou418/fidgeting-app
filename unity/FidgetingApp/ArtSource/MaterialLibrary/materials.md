# Fidgeting 材质库

> 由 `unity/FidgetingApp/ArtSource/MaterialLibrary/materials.json` 生成，不要手改。运行 `node tools/model-provenance-explorer/validate-material-library.mjs --write-md` 重新生成。更新日期 2026-09-11。

## 用法

- 每个材质一个稳定 id。Gate 07 lookdev 脚本、Unity 材质工厂和概念图提示词都引用同一个 id。
- `blender.baseColor` 是线性 RGB，直接写进 Principled BSDF；`unity.baseColorHex` 是 sRGB，与 `.mat` 文件一致。两者不能互相复制。
- `swatchHex` 只是给人看的颜色锚点，由 Blender 线性色换算而来，不是渲染目标。
- 概念图只能用 ChatGPT Image Gen 生成，属于 concept-only 分支，不能晋升为几何或材质真值。

## 固定风格块（概念图）

Premium 3D studio product render of a real manufactured fidget object. Single hero object, centred, floating 2 mm above a matte dark studio floor with a soft contact shadow. Three-light rig: large soft key upper-left, soft fill right, thin top strip for edge sparkle. Neutral colour balance, AgX-like tone mapping, no lens flare, no bloom, no text, no logo, no hands, no background props. Materials exactly as called out; never glossy where the callout says satin or matte.

## 材质一览

- ![steel-satin](spheres/steel-satin.png) `steel-satin` · 拉丝缎面钢 / Satin steel · #E5E6E7 · Gate 07 已批准
- ![steel-turned-disc](spheres/steel-turned-disc.png) `steel-turned-disc` · 车削同心纹钢盘 / Turned steel disc · #E7E8EA · Gate 07 已批准
- ![steel-bearing-dark](spheres/steel-bearing-dark.png) `steel-bearing-dark` · 深色轴承钢 / Dark bearing steel · #454548 · Gate 07 已批准
- ![bearing-steel](spheres/bearing-steel.png) `bearing-steel` · 轴承钢 / Bearing steel · #687077 · Shipping Unity 材质
- ![blade-sandblast](spheres/blade-sandblast.png) `blade-sandblast` · 喷砂叶片钢 / Sandblasted blade steel · #AEB3B6 · Shipping Unity 材质
- ![bevel-polished](spheres/bevel-polished.png) `bevel-polished` · 抛光倒角 / Polished bevel · #D6DADD · Shipping Unity 材质
- ![cap-radial-brushed](spheres/cap-radial-brushed.png) `cap-radial-brushed` · 径向拉丝盖 / Radial brushed cap · #C2C5C7 · Shipping Unity 材质
- ![blade-inset-dark](spheres/blade-inset-dark.png) `blade-inset-dark` · 深色叶片内嵌 / Dark blade inset · #282D32 · Shipping Unity 材质
- ![dark-ring](spheres/dark-ring.png) `dark-ring` · 深色哑光环 / Dark matte ring · #0B0D10 · Shipping Unity 材质
- ![axis-matte](spheres/axis-matte.png) `axis-matte` · 凹陷哑光旋轴 / Recessed matte spindle · #050506 · 合同锁定
- ![gunmetal](spheres/gunmetal.png) `gunmetal` · 枪灰金属 / Gunmetal · #282A2C · Shipping Unity 材质
- ![warm-silver](spheres/warm-silver.png) `warm-silver` · 暖银 / Warm silver · #66625C · Shipping Unity 材质
- ![chrome](spheres/chrome.png) `chrome` · 镀铬 / Chrome · #EDF2FA · Shipping Unity 材质
- ![gold-mesh](spheres/gold-mesh.png) `gold-mesh` · 金色网格 / Gold mesh · #A16118 · Shipping Unity 材质
- ![etched-dark](spheres/etched-dark.png) `etched-dark` · 蚀刻深灰 / Etched dark · #0D0D0E · Shipping Unity 材质
- ![groove-dark](spheres/groove-dark.png) `groove-dark` · 凹槽近黑 / Groove near-black · #050506 · Shipping Unity 材质
- ![studio-floor-matte](spheres/studio-floor-matte.png) `studio-floor-matte` · 影棚哑光地面 / Matte studio floor · #353537 · Gate 07 已批准
- ![clay-control](spheres/clay-control.png) `clay-control` · 中性粘土对照 / Neutral clay control · #C2C7CB · 过期证据
- `case-clear-crystal` · 透明水晶外壳 / Clear crystal shell · #F8FBFF · Gate 07 已批准
- `case-smoke-lilac-liner` · 烟紫内衬 / Smoke-lilac liner · #EEEAF4 · Gate 07 已批准
- `case-dark-sandblast` · 深色喷砂钢 / Dark sandblasted steel · #5C6266 · Gate 07 已批准
- `case-piano-black` · 钢琴黑板 / Piano-black plate · #1C1E22 · Gate 07 已批准
- `case-bright-mirror` · 亮镜面银 / Bright mirror silver · #C9D0D6 · Gate 07 已批准
- `case-champagne-gold-inlay` · 香槟金饰条 / Champagne gold inlay · #C8B48B · Gate 07 已批准
- `case-rose-bronze-tier` · 玫瑰青铜档位金属 / Rose-bronze tier metal · #B39485 · Gate 07 已批准
- `case-grey-blue-titanium-tier` · 灰蓝钛档位金属 / Grey-blue titanium tier metal · #94A1B3 · Gate 07 已批准
- `case-champagne-tier` · 香槟档位金属 / Champagne tier metal · #CCBA99 · Gate 07 已批准

## 拉丝缎面钢 · Satin steel (`steel-satin`, #E5E6E7)

![steel-satin sphere](spheres/steel-satin.png)

状态：Gate 07 已批准 · 家族：钢 / 金属

均匀的缎面不锈钢。高光宽而柔，反射里能看见形体但读不出环境细节。是三叶金属陀螺主体（Rotor_Body）和盖面非车削区域的基础材质。

**边缘 / 厚度行为**：倒角处高光收窄变亮，平面上高光扩散成柔和亮带；不出现镜面式清晰倒影。

**Blender（Principled BSDF，线性）**

- 权威：blender-lookdev · M_Steel_Satin
- Base Color 0.78 / 0.79 / 0.8 · Metallic 1 · Roughness 0.36

**Unity（URP）**

- M_GeeoneSatin · Universal Render Pipeline/Lit
- Base Color #C6C8CA (sRGB) · Metallic 1 · Smoothness 0.64 · 高光 开 · 环境反射 开
- 细节：sandblast detail albedo + normal 0.10

**Blender/Unity 对齐**：Blender linear 0.78 ≈ sRGB #E5E6E7；Unity 存的是 sRGB #C6C8CA（linear ≈ 0.56）。两端数值未对齐，Gate 11 批准的是视觉结果。同名数值被当成不同色彩空间复制，是已知漂移。

**可用短语**

- satin brushed stainless steel
- soft wide specular highlight
- fine uniform micro-grain
- cool neutral grey metal, slightly warm in shadow

**避免**

- mirror polish
- chrome
- sharp environment reflections
- brushed streaks visible from far away
- blue tint

**使用位置**

- metal-three-blade：Rotor_Body、Cap_Top (非车削区)、Cap_Bottom (非车削区)
- premium-display-case：GEO_PDC_HEADER_SATIN_SHELF、GEO_PDC_MAIN_SATIN_SHELF、GEO_PDC_FRAME_BOLT_*

**来源**

- `unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade/evidence/07-material/rev-005/lookdev_geeone.py` — mat_satin()
- `unity/FidgetingApp/Assets/_Fidgeting/Editor/ThreeBladeMaterialFactory.cs` — M_GeeoneSatin

## 车削同心纹钢盘 · Turned steel disc (`steel-turned-disc`, #E7E8EA)

![steel-turned-disc sphere](spheres/steel-turned-disc.png)

状态：Gate 07 已批准 · 家族：钢 / 金属

车床车出的同心圆纹钢面。高光沿径向拉成一条旋转的亮带，14 个平面切分区之间有明显的明暗台阶。只允许出现在盖面圆盘上（用户 2026-09-05）。

**边缘 / 厚度行为**：亮带随视角围绕圆心转动；靛面不能被 sunburst 高光洗白，切分面之间的色阶必须保留。

**Blender（Principled BSDF，线性）**

- 权威：blender-lookdev · M_Disc_Turned
- Base Color 0.8 / 0.81 / 0.82 · Metallic 1 · Roughness 0.3
- Anisotropic 0.4 · Tangent radial Z (ShaderNodeTangent RADIAL)
- Bump：wave rings, 0.12 mm pitch，strength 0.12，distance 0.004

**Unity（URP）**

- M_GeeoneDiscTurned · Universal Render Pipeline/Lit
- Base Color #CCCED0 (sRGB) · Metallic 1 · Smoothness 0.68 · 高光 开 · 环境反射 开
- 细节：radial brush albedo + normal 0.05; URP Lit 无各向异性，靠贴图近似

**Blender/Unity 对齐**：同 steel-satin：Blender linear 0.80 vs Unity sRGB #CCCED0。URP Lit 无各向异性，Unity 用径向法线贴图近似。

**可用短语**

- lathe-turned concentric rings
- radial anisotropic highlight sweeping around the centre
- 14 faint planar sector facets
- satin steel disc

**避免**

- sunburst washout
- flat mirror disc
- random scratches
- brushed linear grain

**限制**

- 各向异性只允许出现在盖面圆盘，不得扩散到主体或轮毂。

**使用位置**

- metal-three-blade：Cap_Top disc sectors、Cap_Bottom disc sectors

**来源**

- `unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade/evidence/07-material/rev-005/lookdev_geeone.py` — mat_disc_turned(); rev-003 把 anisotropic 0.7 降到 0.4
- `unity/FidgetingApp/Assets/_Fidgeting/Editor/ThreeBladeMaterialFactory.cs` — M_GeeoneDiscTurned

## 深色轴承钢 · Dark bearing steel (`steel-bearing-dark`, #454548)

![steel-bearing-dark sphere](spheres/steel-bearing-dark.png)

状态：Gate 07 已批准 · 家族：深色金属

接近黑色的轴承钢，用于轮毂芯和轴承座。金属度满，但因为颜色深，读起来更像深色缎面而不是亮金属；高光是一条窄而干净的冷灰线。

**边缘 / 厚度行为**：只有边缘和曲率最大处出现细亮线；大面保持深灰，不反射环境色。

**Blender（Principled BSDF，线性）**

- 权威：blender-lookdev · M_Hub_Dark
- Base Color 0.06 / 0.06 / 0.065 · Metallic 1 · Roughness 0.45

**Unity（URP）**

- M_GeeoneHubDark · Universal Render Pipeline/Lit
- Base Color #141518 (sRGB) · Metallic 1 · Smoothness 0.55 · 高光 开 · 环境反射 开

**Blender/Unity 对齐**：Blender linear 0.06 ≈ sRGB #434344；Unity sRGB #141518（linear ≈ 0.007）。Unity 明显更黑。

**可用短语**

- dark bearing steel
- near-black satin metal
- thin cool highlight along the rim
- recessed hub

**避免**

- glossy black plastic
- pure black void
- blue chrome
- visible reflections of the room

**使用位置**

- metal-three-blade：Hub_Core、Hub_Seat_Top、Hub_Seat_Bottom

**来源**

- `unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade/evidence/07-material/rev-005/lookdev_geeone.py` — mat_hub_dark()
- `unity/FidgetingApp/Assets/_Fidgeting/Editor/ThreeBladeMaterialFactory.cs` — M_GeeoneHubDark

## 轴承钢 · Bearing steel (`bearing-steel`, #687077)

![bearing-steel sphere](spheres/bearing-steel.png)

状态：Shipping Unity 材质 · 家族：钢 / 金属

中灰色的抛光轴承钢，用于三叶结构里外露的轴承环。比缎面钢更亮、更冷，高光更集中。

**Blender（Principled BSDF，线性）**

- 权威：derived-from-unity
- Base Color 0.1384 / 0.162 / 0.1845 · Metallic 1 · Roughness 0.24
- 推导：baseColor = sRGB→linear(unity.baseColorHex); roughness = 1 − smoothness

**Unity（URP）**

- M_BearingSteel · Universal Render Pipeline/Lit
- Base Color #687077 (sRGB) · Metallic 1 · Smoothness 0.76 · 高光 开 · 环境反射 开

**可用短语**

- polished bearing steel ring
- cool mid-grey metal
- tight specular highlight
- machined edge

**避免**

- chrome mirror
- rust
- warm brass tint

**使用位置**

- metal-three-blade：bearing ring
- premium-display-case：enclosed three-blade toy (caller-owned)

**来源**

- `unity/FidgetingApp/Assets/_Fidgeting/Editor/ThreeBladeMaterialFactory.cs` — M_BearingSteel Color32(0x68,0x70,0x77) metallic 1 smoothness 0.76

## 喷砂叶片钢 · Sandblasted blade steel (`blade-sandblast`, #AEB3B6)

![blade-sandblast sphere](spheres/blade-sandblast.png)

状态：Shipping Unity 材质 · 家族：钢 / 金属

喷砂处理的浅灰钢面，颗粒感均匀，高光比缎面钢更散、更亮。是三叶陀螺叶片大面的 Shipping 材质。

**Blender（Principled BSDF，线性）**

- 权威：derived-from-unity
- Base Color 0.4233 / 0.4508 / 0.4678 · Metallic 1 · Roughness 0.28
- 推导：baseColor = sRGB→linear(unity.baseColorHex); roughness = 1 − smoothness

**Unity（URP）**

- M_BladeSandblast · Universal Render Pipeline/Lit
- Base Color #AEB3B6 (sRGB) · Metallic 1 · Smoothness 0.72 · 高光 开 · 环境反射 开
- 细节：sandblast detail albedo + normal 0.16

**可用短语**

- bead-blasted stainless steel
- even fine grain
- diffuse silvery highlight
- no directional brushing

**避免**

- brushed lines
- mirror
- rough cast texture

**使用位置**

- metal-three-blade：blade faces
- premium-display-case：enclosed three-blade toy (caller-owned)

**来源**

- `unity/FidgetingApp/Assets/_Fidgeting/Editor/ThreeBladeMaterialFactory.cs` — M_BladeSandblast Color32(0xAE,0xB3,0xB6) metallic 1 smoothness 0.72

## 抛光倒角 · Polished bevel (`bevel-polished`, #D6DADD)

![bevel-polished sphere](spheres/bevel-polished.png)

状态：Shipping Unity 材质 · 家族：钢 / 金属

叶片倒角上的高抛光带。用途是切出一条亮边，让喷砂大面和倒角形成明暗对比；面积小，高光锐。

**边缘 / 厚度行为**：只存在于倒角窄带；亮带随视角滑动，是全模型最亮的金属。

**Blender（Principled BSDF，线性）**

- 权威：derived-from-unity
- Base Color 0.6724 / 0.7011 / 0.7231 · Metallic 1 · Roughness 0.1
- 推导：baseColor = sRGB→linear(unity.baseColorHex); roughness = 1 − smoothness

**Unity（URP）**

- M_BevelPolished · Universal Render Pipeline/Lit
- Base Color #D6DADD (sRGB) · Metallic 1 · Smoothness 0.9 · 高光 开 · 环境反射 开

**可用短语**

- mirror-polished chamfer edge
- thin bright bevel line
- high-contrast against bead-blasted face

**避免**

- polish spreading onto the blade face
- soft blurry highlight

**使用位置**

- metal-three-blade：blade chamfers

**来源**

- `unity/FidgetingApp/Assets/_Fidgeting/Editor/ThreeBladeMaterialFactory.cs` — M_BevelPolished Color32(0xD6,0xDA,0xDD) metallic 1 smoothness 0.90

## 径向拉丝盖 · Radial brushed cap (`cap-radial-brushed`, #C2C5C7)

![cap-radial-brushed sphere](spheres/cap-radial-brushed.png)

状态：Shipping Unity 材质 · 家族：钢 / 金属

以圆心为中心的径向拉丝盖面。和车削钢盘同属径向纹理，但拉丝更细更密，没有 14 个切分面。Unity 用自定义 brushed shader 加径向法线贴图实现。

**Blender（Principled BSDF，线性）**

- 权威：derived-from-unity
- Base Color 0.5395 / 0.5583 / 0.5711 · Metallic 1 · Roughness 0.21
- 推导：baseColor = sRGB→linear(unity.baseColorHex); roughness = 1 − smoothness; Blender 各向异性值尚未创作，缩略图不含拉丝

**Unity（URP）**

- M_CapRadialBrushed · custom brushed (guid 058030c3abf3944cdbae35ef6b036b76)
- Base Color #C2C5C7 (sRGB) · Metallic 1 · Smoothness 0.79 · 高光 开 · 环境反射 开
- 细节：radial brush albedo + normal 0.10

**可用短语**

- radial brushed steel cap
- fine sunburst grain
- highlight rotating with the viewer
- flat cap

**避免**

- sector facets
- coarse scratches
- linear brushing

**使用位置**

- metal-three-blade：cap

**来源**

- `unity/FidgetingApp/Assets/_Fidgeting/Editor/ThreeBladeMaterialFactory.cs` — M_CapRadialBrushed Color32(0xC2,0xC5,0xC7) metallic 1 smoothness 0.79

## 深色叶片内嵌 · Dark blade inset (`blade-inset-dark`, #282D32)

![blade-inset-dark sphere](spheres/blade-inset-dark.png)

状态：Shipping Unity 材质 · 家族：深色金属

叶片凹槽内的深灰半金属面。比轴承钢更暗、更哑，用来让凹槽退后，突出外圈亮边。

**Blender（Principled BSDF，线性）**

- 权威：derived-from-unity
- Base Color 0.0212 / 0.0262 / 0.0319 · Metallic 0.85 · Roughness 0.52
- 推导：baseColor = sRGB→linear(unity.baseColorHex); roughness = 1 − smoothness

**Unity（URP）**

- M_BladeInset · Universal Render Pipeline/Lit
- Base Color #282D32 (sRGB) · Metallic 0.85 · Smoothness 0.48 · 高光 开 · 环境反射 开
- 细节：sandblast detail albedo + normal 0.08

**可用短语**

- dark graphite-grey recessed inlay
- semi-matte metal
- sits visually behind the bright rim

**避免**

- glossy black
- pure matte plastic look
- colour tint

**使用位置**

- metal-three-blade：blade insets

**来源**

- `unity/FidgetingApp/Assets/_Fidgeting/Editor/ThreeBladeMaterialFactory.cs` — M_BladeInset Color32(0x28,0x2D,0x32) metallic 0.85 smoothness 0.48

## 深色哑光环 · Dark matte ring (`dark-ring`, #0B0D10)

![dark-ring sphere](spheres/dark-ring.png)

状态：Shipping Unity 材质 · 家族：哑光 / 无反射

非金属的近黑色环，微弱高光。用作轴承外围的视觉分隔环，让金属和金属之间有一条不反光的暗缝。

**Blender（Principled BSDF，线性）**

- 权威：derived-from-unity
- Base Color 0.0033 / 0.004 / 0.0052 · Metallic 0 · Roughness 0.55
- 推导：baseColor = sRGB→linear(unity.baseColorHex); roughness = 1 − smoothness

**Unity（URP）**

- M_DarkRing · Universal Render Pipeline/Lit
- Base Color #0B0D10 (sRGB) · Metallic 0 · Smoothness 0.45 · 高光 开 · 环境反射 开
- 细节：sandblast detail albedo + normal 0.08

**可用短语**

- near-black matte ring
- non-metallic
- barely-there soft highlight
- separates the steel parts

**避免**

- rubber sheen
- glossy black
- metallic reflection

**使用位置**

- metal-three-blade：dark ring

**来源**

- `unity/FidgetingApp/Assets/_Fidgeting/Editor/ThreeBladeMaterialFactory.cs` — M_DarkRing Color32(0x0B,0x0D,0x10) metallic 0 smoothness 0.45

## 凹陷哑光旋轴 · Recessed matte spindle (`axis-matte`, #050506)

![axis-matte sphere](spheres/axis-matte.png)

状态：合同锁定 · 家族：哑光 / 无反射

扑克扇牌正面唯一允许的轴心外观：一枚完全不反光的近黑哑光旋轴，半径 2.00 mm，内缩 0.12 mm。它必须读成一个“洞里的哑光点”，而不是任何金属件。

**边缘 / 厚度行为**：没有高光、没有环境反射、没有边缘亮线；只靠内缩产生的阴影表现深度。

**Blender（Principled BSDF，线性）**

- 权威：contract-locked
- Base Color 0.0015 / 0.0015 / 0.0018 · Metallic 0 · Roughness 1
- Specular IOR Level 0
- 推导：Unity 合同：metallic 0、smoothness 0、关闭高光与环境反射 → Blender Principled metallic 0、roughness 1、Specular IOR Level 0

**Unity（URP）**

- M_FanCardAxisMatte · Universal Render Pipeline/Lit
- Base Color #050506 (sRGB) · Metallic 0 · Smoothness 0 · 高光 关 · 环境反射 关

**可用短语**

- tiny recessed matte black spindle
- zero specular
- reads as a soft dark dot inside a shallow hole

**避免**

- chrome bearing cap
- metal disc
- ring
- washer
- ball
- any highlight or reflection on the spindle

**限制**

- 只能用于 CommonAxis_RecessedMatteSpindle，半径 2.00 mm，内缩 0.12 mm。
- 任何 bearing cap / chrome disc / ring / washer / axis seat / cover disc / ball 都是禁止对象，两份 Fan Card FBX 中的休眠网格同样禁止。

**使用位置**

- magnetic-fan-card：CommonAxis_RecessedMatteSpindle

**来源**

- `unity/FidgetingApp/ArtSource/FanCard/fan_card_guardrails.json` — mechanism.front_visible_axis_*
- `unity/FidgetingApp/Docs/FanCardModelingGuardrails.md` — front axis hard rule
- `unity/FidgetingApp/Assets/_FanCard/Generated/Materials/M_FanCardAxisMatte.mat` — _BaseColor 0.018/0.02/0.022, _Metallic 0, _Smoothness 0, _SpecularHighlights 0, _EnvironmentReflections 0

## 枪灰金属 · Gunmetal (`gunmetal`, #282A2C)

![gunmetal sphere](spheres/gunmetal.png)

状态：Shipping Unity 材质 · 家族：深色金属

深枪灰色的半哑金属，用于扇牌后侧机构件。比轴承钢暗、比哑光旋轴亮，高光宽而钝。

**Blender（Principled BSDF，线性）**

- 权威：derived-from-unity
- Base Color 0.0212 / 0.0232 / 0.0252 · Metallic 0.9 · Roughness 0.72
- 推导：baseColor = sRGB→linear(unity.baseColorHex); roughness = 1 − smoothness

**Unity（URP）**

- M_FanCardGunmetal · custom (guid fe0a39ea0875648c2a4eabd8959710f0)
- Base Color #282A2C (sRGB) · Metallic 0.9 · Smoothness 0.28 · 高光 开 · 环境反射 开

**可用短语**

- gunmetal grey
- semi-matte dark alloy
- broad dull highlight
- machined bracket

**避免**

- black chrome
- blue steel
- glossy paint

**使用位置**

- magnetic-fan-card：back mechanism

**来源**

- `unity/FidgetingApp/Assets/_FanCard/Editor/FanCardSceneBuilder.cs` — M_FanCardGunmetal

## 暖银 · Warm silver (`warm-silver`, #66625C)

![warm-silver sphere](spheres/warm-silver.png)

状态：Shipping Unity 材质 · 家族：钢 / 金属

带一点暖调的哑银，用于扇牌金属边和后轨。金属度满但粗糙度高，读成磨砂银而不是抛光银。

**Blender（Principled BSDF，线性）**

- 权威：derived-from-unity
- Base Color 0.1329 / 0.1221 / 0.107 · Metallic 1 · Roughness 0.76
- 推导：baseColor = sRGB→linear(unity.baseColorHex); roughness = 1 − smoothness

**Unity（URP）**

- M_FanCardWarmSilver · custom (guid 81a18724176f14d63ab26231b599f47d)
- Base Color #66625C (sRGB) · Metallic 1 · Smoothness 0.24 · 高光 开 · 环境反射 开

**可用短语**

- warm satin silver
- matte brushed nickel feel
- slightly warm grey
- soft broad highlight

**避免**

- cold blue silver
- mirror
- yellow gold

**使用位置**

- magnetic-fan-card：metal edge、back track

**来源**

- `unity/FidgetingApp/Assets/_FanCard/Editor/FanCardSceneBuilder.cs` — M_FanCardWarmSilver

## 镀铬 · Chrome (`chrome`, #EDF2FA)

![chrome sphere](spheres/chrome.png)

状态：Shipping Unity 材质 · 家族：钢 / 金属

高亮镀铬。清晰反射环境，是全库最亮、最镜面的材质。只能出现在允许的后侧或装饰位置。

**Blender（Principled BSDF，线性）**

- 权威：derived-from-unity
- Base Color 0.8469 / 0.8879 / 0.956 · Metallic 1 · Roughness 0.22
- 推导：baseColor = sRGB→linear(unity.baseColorHex); roughness = 1 − smoothness

**Unity（URP）**

- M_FanCardChrome · custom (guid 04a8dff4a76454c6a88db88065e9d423)
- Base Color #EDF2FA (sRGB) · Metallic 1 · Smoothness 0.78 · 高光 开 · 环境反射 开

**可用短语**

- bright chrome plating
- crisp environment reflections
- near-white specular

**避免**

- on any front-facing axis part
- haze
- warm tint

**限制**

- 扇牌正面公共轴上禁止出现任何镀铬件（fan-card-axis-no-ring 规则）。

**使用位置**

- magnetic-fan-card：FanCardSceneBuilder chrome slots

**来源**

- `unity/FidgetingApp/Assets/_FanCard/Editor/FanCardSceneBuilder.cs` — M_FanCardChrome

## 金色网格 · Gold mesh (`gold-mesh`, #A16118)

![gold-mesh sphere](spheres/gold-mesh.png)

状态：Shipping Unity 材质 · 家族：金色

偏铜的暗金，粗糙度高，用于扇牌后侧格栅金属丝网。远看是一层暖金色雾，近看是细丝。

**Blender（Principled BSDF，线性）**

- 权威：derived-from-unity
- Base Color 0.3564 / 0.1195 / 0.0091 · Metallic 0.82 · Roughness 0.78
- 推导：baseColor = sRGB→linear(unity.baseColorHex); roughness = 1 − smoothness

**Unity（URP）**

- M_FanCardGoldMesh · Universal Render Pipeline/Lit
- Base Color #A16118 (sRGB) · Metallic 0.82 · Smoothness 0.22 · 高光 开 · 环境反射 开

**可用短语**

- dull antique gold wire mesh
- warm copper-gold
- matte, no mirror
- fine woven grille

**避免**

- shiny yellow gold
- brass bling
- smooth solid gold surface

**使用位置**

- magnetic-fan-card：back grille wires

**来源**

- `unity/FidgetingApp/Assets/_FanCard/Editor/FanCardSceneBuilder.cs` — M_FanCardGoldMesh (line ~96)

## 蚀刻深灰 · Etched dark (`etched-dark`, #0D0D0E)

![etched-dark sphere](spheres/etched-dark.png)

状态：Shipping Unity 材质 · 家族：深色金属

蚀刻纹样的深灰金属面，用于扇牌面上的蚀刻标记层。粗糙度高，高光几乎不成形，只提供和主面之间的明度差。

**Blender（Principled BSDF，线性）**

- 权威：derived-from-unity
- Base Color 0.004 / 0.004 / 0.0044 · Metallic 0.76 · Roughness 0.77
- 推导：baseColor = sRGB→linear(unity.baseColorHex); roughness = 1 − smoothness

**Unity（URP）**

- M_FanCardEtching · Universal Render Pipeline/Lit
- Base Color #0D0D0E (sRGB) · Metallic 0.76 · Smoothness 0.23 · 高光 开 · 环境反射 开

**可用短语**

- dark etched metal marking
- matte graphite grey
- recessed engraving
- no sheen

**避免**

- paint fill
- glossy ink
- raised emboss

**使用位置**

- magnetic-fan-card：etching layer

**来源**

- `unity/FidgetingApp/Assets/_FanCard/Editor/FanCardSceneBuilder.cs` — M_FanCardEtching (line ~77)

## 凹槽近黑 · Groove near-black (`groove-dark`, #050506)

![groove-dark sphere](spheres/groove-dark.png)

状态：Shipping Unity 材质 · 家族：深色金属

扇牌后侧凹槽底部的近黑材质。和哑光旋轴同一个基色，但保留少量金属度和高光，让槽底在低角度能被读出深度。

**Blender（Principled BSDF，线性）**

- 权威：derived-from-unity
- Base Color 0.0015 / 0.0015 / 0.0018 · Metallic 0.64 · Roughness 0.84
- 推导：baseColor = sRGB→linear(unity.baseColorHex); roughness = 1 − smoothness

**Unity（URP）**

- M_FanCardGroove · Universal Render Pipeline/Lit
- Base Color #050506 (sRGB) · Metallic 0.64 · Smoothness 0.16 · 高光 开 · 环境反射 开

**可用短语**

- deep near-black groove floor
- faint metallic sheen at grazing angle
- reads as depth not paint

**避免**

- flat black fill
- chrome groove
- visible reflections

**使用位置**

- magnetic-fan-card：back track groove

**来源**

- `unity/FidgetingApp/Assets/_FanCard/Editor/FanCardSceneBuilder.cs` — M_FanCardGroove (line ~86)

## 影棚哑光地面 · Matte studio floor (`studio-floor-matte`, #353537)

![studio-floor-matte sphere](spheres/studio-floor-matte.png)

状态：Gate 07 已批准 · 家族：环境

Gate 09 中性环境的地面：近黑哑光，只承接柔和接触阴影，不反射产品。产品悬浮 2 mm，阴影边缘软。

**Blender（Principled BSDF，线性）**

- 权威：blender-lookdev · M_Studio_Floor
- Base Color 0.035 / 0.035 / 0.038 · Metallic 0 · Roughness 0.85

**Unity（URP）**

- M_StudioFloor · Universal Render Pipeline/Lit
- Base Color #010203 (sRGB) · Metallic 0 · Smoothness 0.08 · 高光 开 · 环境反射 开

**Blender/Unity 对齐**：Blender linear 0.035 ≈ sRGB #333335；Unity sRGB #010203。Unity 地面几乎纯黑。

**可用短语**

- matte near-black studio floor
- soft contact shadow
- no reflection of the product
- seamless dark backdrop

**避免**

- glossy floor reflection
- visible horizon line
- coloured gradient backdrop

**使用位置**

- metal-three-blade：studio floor (Gate 09)

**来源**

- `unity/FidgetingApp/ArtSource/ModelPipeline/metal-three-blade/evidence/07-material/rev-005/lookdev_geeone.py` — mat_floor()
- `unity/FidgetingApp/Assets/_Fidgeting/Editor/ThreeBladeMaterialFactory.cs` — M_StudioFloor

## 中性粘土对照 · Neutral clay control (`clay-control`, #C2C7CB)

![clay-control sphere](spheres/clay-control.png)

状态：过期证据 · 家族：对照

Gate 05–06 白模与 Gate 07 对照渲染用的中性灰粘土。非金属、中等粗糙，只用来看形体和光照，不代表任何成品外观。

**Blender（Principled BSDF，线性）**

- 权威：blender-lookdev · MAT_M07_ClayControl
- Base Color 0.54 / 0.57 / 0.6 · Metallic 0 · Roughness 0.62

**Unity（URP）**

- 无 Unity 对应材质。

**可用短语**

- neutral grey clay render
- matte, non-metallic
- form study

**避免**

- any colour
- specular sparkle
- texture

**使用位置**

- premium-display-case：clay-vs-pbr control

**来源**

- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/07-material/rev-001/build_material_lookdev.py` — MAT_M07_ClayControl；display case pipeline 当前全部 stale

## 透明水晶外壳 · Clear crystal shell (`case-clear-crystal`, #F8FBFF)

状态：Gate 07 已批准 · 家族：透明 / 半透明

展示盒最外层的透明聚碳酸酯水晶框：IOR 1.49，极低粗糙度，薄清漆层，整片 300–650 nm 薄膜虹彩让边缘在彩色边光下泛出青/品红。

**Blender（Principled BSDF，线性）**

- 权威：blender-lookdev · M_PDC_ClearCrystal
- Base Color 0.9387 / 0.9647 / 1 · Metallic 0 · Roughness 0.035

**Unity（URP）**

- 无 Unity 对应材质。

**可用短语**

- clear polycarbonate crystal frame
- thin-film iridescent edge sheen
- sharp glass-like bevels
- IOR 1.49 transmission

**避免**

- frosted glass
- tinted acrylic
- rainbow across flat faces under neutral light

**使用位置**

- premium-display-case：GEO_PDC_OUTER_CRYSTAL_FRAME、GEO_PDC_POCKET_CLIP_*

**来源**

- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/07-material/rev-003/lookdev_tri_spinner_slab_materials.r003.py` — Gate 07 rev-003 lookdev, user approval “确认” 2026-09-11T15:26:00+08:00
- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/03-contract/rev-013/modeling-contract.json` — contract rev-013 materials / cmf.scheme A / cmf.rarity_tier_map

## 烟紫内衬 · Smoke-lilac liner (`case-smoke-lilac-liner`, #EEEAF4)

状态：Gate 07 已批准 · 家族：透明 / 半透明

盒体内圈与凹槽壁的半透明烟紫内衬：透射 0.775，带体积吸收，随稀有度档位微调基色。

**Blender（Principled BSDF，线性）**

- 权威：blender-lookdev · M_PDC_SmokeLiner
- Base Color 0.855 / 0.8228 / 0.9047 · Metallic 0 · Roughness 0.15

**Unity（URP）**

- 无 Unity 对应材质。

**可用短语**

- smoked lilac translucent liner
- soft volumetric absorption
- matte-satin translucency

**避免**

- clear glass
- opaque plastic
- saturated purple

**使用位置**

- premium-display-case：GEO_PDC_SMOKE_INNER_LINER、GEO_PDC_POCKET_SMOKE_WALL

**来源**

- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/07-material/rev-003/lookdev_tri_spinner_slab_materials.r003.py` — Gate 07 rev-003 lookdev, user approval “确认” 2026-09-11T15:26:00+08:00
- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/03-contract/rev-013/modeling-contract.json` — contract rev-013 materials / cmf.scheme A / cmf.rarity_tier_map

## 深色喷砂钢 · Dark sandblasted steel (`case-dark-sandblast`, #5C6266)

状态：Gate 07 已批准 · 家族：深色金属

主舱 field 与后板的深灰喷砂钢面：scheme A 用 #5C6266 取代规格 #AEB3B6，微凸粒度 0.13 mm、高度 0.0105 mm，粗糙度 0.45±0.03。

**Blender（Principled BSDF，线性）**

- 权威：blender-lookdev · M_PDC_DarkSandblast
- Base Color 0.107 / 0.1221 / 0.1329 · Metallic 1 · Roughness 0.45

**Unity（URP）**

- 无 Unity 对应材质。

**可用短语**

- dark bead-blasted steel
- fine even micro-grain
- low diffuse sheen
- no directional brushing

**避免**

- brushed lines
- mirror
- light silver sandblast

**使用位置**

- premium-display-case：GEO_PDC_MAIN_MICROBLAST_FIELD、GEO_PDC_REAR_PLATE

**来源**

- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/07-material/rev-003/lookdev_tri_spinner_slab_materials.r003.py` — Gate 07 rev-003 lookdev, user approval “确认” 2026-09-11T15:26:00+08:00
- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/03-contract/rev-013/modeling-contract.json` — contract rev-013 materials / cmf.scheme A / cmf.rarity_tier_map

## 钢琴黑板 · Piano-black plate (`case-piano-black`, #1C1E22)

状态：Gate 07 已批准 · 家族：深色金属

header 石墨板、数值板与凹槽底的钢琴黑：深炭底色加满强清漆（coat 1.0 / 0.03），基础粗糙度 0.25；header 板叠印刷标签（油墨粗糙度 0.55）。

**Blender（Principled BSDF，线性）**

- 权威：blender-lookdev · M_PDC_PianoBlack
- Base Color 0.0116 / 0.013 / 0.016 · Metallic 0.05 · Roughness 0.25

**Unity（URP）**

- 无 Unity 对应材质。

**可用短语**

- piano black lacquer
- deep gloss clear coat
- crisp reflections
- near-black charcoal base

**避免**

- matte black
- plastic sheen
- dust or fingerprints

**使用位置**

- premium-display-case：GEO_PDC_HEADER_GRAPHITE_PLANE (+ label decal)、GEO_PDC_MAIN_TRAIT_PLAQUE、GEO_PDC_POCKET_GRAPHITE_FLOOR

**来源**

- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/07-material/rev-003/lookdev_tri_spinner_slab_materials.r003.py` — Gate 07 rev-003 lookdev, user approval “确认” 2026-09-11T15:26:00+08:00
- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/03-contract/rev-013/modeling-contract.json` — contract rev-013 materials / cmf.scheme A / cmf.rarity_tier_map

## 亮镜面银 · Bright mirror silver (`case-bright-mirror`, #C9D0D6)

状态：Gate 07 已批准 · 家族：钢 / 金属

斜边、凹槽抛光唇等凸起抛光件的亮镜面：scheme A 以 #C9D0D6、粗糙度 0.04 取代规格烟色镜面 #667078；宽口径下随稀有度换金属。

**Blender（Principled BSDF，线性）**

- 权威：blender-lookdev · M_PDC_Mirror
- Base Color 0.5841 / 0.6308 / 0.6724 · Metallic 1 · Roughness 0.04

**Unity（URP）**

- 无 Unity 对应材质。

**可用短语**

- bright mirror-polished steel
- razor-sharp reflections
- narrow polished bevels

**避免**

- smoked mirror
- brushed
- visible grain

**使用位置**

- premium-display-case：GEO_PDC_HEADER_MIRROR_BEVEL、GEO_PDC_MAIN_MIRROR_SEAM、GEO_PDC_POCKET_POLISHED_LIP

**来源**

- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/07-material/rev-003/lookdev_tri_spinner_slab_materials.r003.py` — Gate 07 rev-003 lookdev, user approval “确认” 2026-09-11T15:26:00+08:00
- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/03-contract/rev-013/modeling-contract.json` — contract rev-013 materials / cmf.scheme A / cmf.rarity_tier_map

## 香槟金饰条 · Champagne gold inlay (`case-champagne-gold-inlay`, #C8B48B)

状态：Gate 07 已批准 · 家族：金色

Standard 档的金色饰条、竖轨与索引块：#C8B48B，各向异性 0.15，沿饰条长轴拉丝，永不成闭环。

**Blender（Principled BSDF，线性）**

- 权威：blender-lookdev · M_PDC_AccentMetal
- Base Color 0.5776 / 0.4564 / 0.2582 · Metallic 1 · Roughness 0.26
- Anisotropic 0.15 · Tangent —

**Unity（URP）**

- 无 Unity 对应材质。

**可用短语**

- champagne gold inlay
- fine directional brushing along the inlay
- restrained warm metal

**避免**

- yellow gold
- mirror gold
- closed gold loop

**使用位置**

- premium-display-case：GEO_PDC_*GOLD*

**来源**

- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/07-material/rev-003/lookdev_tri_spinner_slab_materials.r003.py` — Gate 07 rev-003 lookdev, user approval “确认” 2026-09-11T15:26:00+08:00
- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/03-contract/rev-013/modeling-contract.json` — contract rev-013 materials / cmf.scheme A / cmf.rarity_tier_map

## 玫瑰青铜档位金属 · Rose-bronze tier metal (`case-rose-bronze-tier`, #B39485)

状态：Gate 07 已批准 · 家族：金色

Refined 档（宽口径）：边框、抛光件与饰条整体换为低饱和玫瑰青铜，sRGB 0.70/0.58/0.52，饱和度约为原铜色 40%。

**Blender（Principled BSDF，线性）**

- 权威：blender-lookdev · M_PDC_BrushedSteel_copper
- Base Color 0.448 / 0.2957 / 0.233 · Metallic 1 · Roughness 0.3

**Unity（URP）**

- 无 Unity 对应材质。

**可用短语**

- muted rose bronze
- low-saturation warm metal
- brushed on frames, polished on bevels

**避免**

- orange copper
- saturated bronze
- rose gold jewelry pink

**使用位置**

- premium-display-case：bezels (5)、polished parts (6)、accents (7)、liner tint (2)

**来源**

- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/07-material/rev-003/lookdev_tri_spinner_slab_materials.r003.py` — Gate 07 rev-003 lookdev, user approval “确认” 2026-09-11T15:26:00+08:00
- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/03-contract/rev-013/modeling-contract.json` — contract rev-013 materials / cmf.scheme A / cmf.rarity_tier_map

## 灰蓝钛档位金属 · Grey-blue titanium tier metal (`case-grey-blue-titanium-tier`, #94A1B3)

状态：Gate 07 已批准 · 家族：钢 / 金属

Signature 档（宽口径）：灰蓝钛，sRGB 0.58/0.63/0.70，与 Standard 冷钢的差别只在偏蓝色相。

**Blender（Principled BSDF，线性）**

- 权威：blender-lookdev · M_PDC_BrushedSteel_titanium
- Base Color 0.2957 / 0.3547 / 0.448 · Metallic 1 · Roughness 0.3

**Unity（URP）**

- 无 Unity 对应材质。

**可用短语**

- grey-blue titanium PVD
- cool desaturated metal
- brushed frames, polished bevels

**避免**

- saturated blue
- cobalt
- chrome blue

**使用位置**

- premium-display-case：bezels (5)、polished parts (6)、accents (7)、liner tint (2)

**来源**

- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/07-material/rev-003/lookdev_tri_spinner_slab_materials.r003.py` — Gate 07 rev-003 lookdev, user approval “确认” 2026-09-11T15:26:00+08:00
- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/03-contract/rev-013/modeling-contract.json` — contract rev-013 materials / cmf.scheme A / cmf.rarity_tier_map

## 香槟档位金属 · Champagne tier metal (`case-champagne-tier`, #CCBA99)

状态：Gate 07 已批准 · 家族：金色

Heirloom 档（宽口径）：香槟色，sRGB 0.80/0.73/0.60，取代饱和黄金。

**Blender（Principled BSDF，线性）**

- 权威：blender-lookdev · M_PDC_BrushedSteel_gold
- Base Color 0.6038 / 0.4919 / 0.3185 · Metallic 1 · Roughness 0.3

**Unity（URP）**

- 无 Unity 对应材质。

**可用短语**

- pale champagne metal
- warm desaturated gold
- brushed frames, polished bevels

**避免**

- yellow gold
- brass
- saturated gold

**使用位置**

- premium-display-case：bezels (5)、polished parts (6)、accents (7)、liner tint (2)

**来源**

- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/07-material/rev-003/lookdev_tri_spinner_slab_materials.r003.py` — Gate 07 rev-003 lookdev, user approval “确认” 2026-09-11T15:26:00+08:00
- `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/03-contract/rev-013/modeling-contract.json` — contract rev-013 materials / cmf.scheme A / cmf.rarity_tier_map

## 待收录

- `blood-red-crystal`（magnetic-slide-tile）：基色由 albedo 贴图驱动，没有常数色；rev-013 参数：metallic 0.08、IOR 1.52、Specular IOR Level 0.58、Coat 0.48/0.035、Transmission 0.08、Thin Film IOR 1.38。pipeline 全部 stale，待 Gate 07 重新批准后收录。 来源 `unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-013/build_gate07_side_partition_fix.py`。
- `matte-friction-plastic`（premium-display-case）：MAT_M07_ContinuousNeutralFriction 基色由 noise ramp 驱动；Gate 04 被退回，材质证据 stale。 来源 `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/07-material/rev-001/build_material_lookdev.py`。
