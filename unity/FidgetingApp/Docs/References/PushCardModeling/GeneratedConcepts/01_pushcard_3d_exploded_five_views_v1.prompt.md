# 推牌 3D 拆解五视图 - 生成记录

成品：[01_pushcard_3d_exploded_five_views_v1.png](01_pushcard_3d_exploded_five_views_v1.png)

> 状态：已被 [同源参数化六视图校正版](02_parametric_consistent_views/README.md) 取代。此图的 LEFT/RIGHT 错用了长边视图，且 TOP 顶板与 EXPLODED 的 L1 不是同一造型，因此不可继续作为正交建模基准。

## 定位

- 图像生成方式：Codex 内置 ImageGen。
- 用途：Unity/Blender 建模前的结构解释与美术方向参考。
- 状态：概念级，不是制造 CAD，也不包含可靠尺寸、公差或磁极定义。
- 结构来源：[拆解线框包](../ExplodedWireframes/README.md)。
- 历史修正结果：磁体数量曾尝试统一为 6 个位置，但视角、顶板和孔阵列仍存在不可可靠消除的生成漂移；校正版因此改用一份参数化主几何渲染全部视图。

## 最终结构理解

1. 可替换镂空顶板。
2. 喷砂钛合金上部结构壳。
3. 深色 POM/PEEK 耐磨隔板。
4. 两个深色金属滑块及平行导轨。
5. 6 颗镀镍圆形磁铁与对应定位阵列。
6. 下部结构板。
7. 钛合金下壳/背盖。

## 基础生成提示词

```text
Use case: infographic-diagram
Asset type: high-resolution 16:9 industrial-design presentation board for future Unity/Blender 3D modeling.

Interpret the supplied structural linework references into one coherent ORIGINAL compact rounded-rectangle magnetic fidget-slider design. Preserve the layered shell logic, long guide rails, circular magnet positions, replaceable openwork panel and axial separation concept, without copying logos or ornamental patterns.

Create a large central axial exploded isometric render containing: replaceable openwork top panel; sandblasted titanium upper structural shell; thin dark POM/PEEK wear plate; two dark gunmetal sliding carriers and parallel guide rails; circular nickel-plated magnets with locating/stopping features; lower structural plate; machined titanium lower shell/back cover; and four small locating fasteners where plausible. All layers must align perfectly when assembled, with real wall thickness, bevels, recesses and no floating/intersecting parts.

Arrange five true orthographic views around the central render. Render each label exactly once: "顶视图 / TOP", "正视图 / FRONT", "背面 / REAR", "左侧 / LEFT", "右侧 / RIGHT", and label the central view "轴向拆解 / EXPLODED". Use the exact same geometry and proportions in every panel.

Use premium PBR industrial visualization: dark graphite technical-grid backdrop, restrained slate panel borders, thin cyan labels, warm orange leader lines, sandblasted silver titanium, polished bevel highlights, dark POM/PEEK, gunmetal rails and nickel-plated magnets. Light with a large soft 5000K key, cool fill and narrow 3200K rim. Warm orange comes only from rim lighting. No logos, people, hands, packaging, watermark, fake dimensions or triangular spinner geometry.
```

## 一致性修正提示词

```text
Fix only the magnet-array mechanical inconsistency. Use exactly SIX nickel-plated circular magnets, exactly six matching circular recesses/holes in every relevant exploded layer, and exactly six matching positions in the top view. Align all six one-to-one along the same centerline. Magnets must sit recessed inside the mechanism when assembled and must not protrude as exterior buttons.

Preserve the exact board layout, cameras, exploded spacing, seven numbered callouts, rounded-rectangle geometry, openwork panel, materials, lighting, background, accents, five orthographic views and all six bilingual labels. Do not change anything else or add dimensions, logos, people, hands, watermarks or extra parts.
```

## 建模注意

本图只保留为 ImageGen 构思记录，不应再用于测量或正交比对。具体磁极、磁铁尺寸、导轨截面、摩擦片厚度和行程仍必须在进入运行时模型前另行定义；建模视角与相互比例以同目录下的参数化校正版为准。
