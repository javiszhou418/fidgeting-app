# 推牌 3D 建模参考包

本目录收录 22 张为后续推牌、磁吸滑块与复合转子建模筛选的关键参考图，并附一张总览。图片来自 2026-08-01 同步到本地 Obsidian 的实拍帖子、公开专利原图和厂商公开产品页。

这是一套视觉与结构研究资料，不是制造级 CAD。照片透视、宣传渲染和专利外观图都不能替代卡尺测量、公差设计或机构验证。

## 快速使用

- 先看 **08–15**：确定轮廓、厚度、前后关系、轨道、磁铁和爆炸层级。
- 再看 **03–05、17、19**：校准手掌尺度、拇指接触区、有效滑动行程和操作姿态。
- 用 **16、18、20、21**：研究磁铁间距、三层堆叠、可拆中层和磁铁模块。
- 用 **02、06、07、17、22**：建立喷砂、抛光倒角、深色金属、透明壳体和复合材质的 PBR 分区。
- 需要直接搭建 3D 爆炸层级时，使用 [ExplodedWireframes 拆解线框包](ExplodedWireframes/README.md)。
- 需要查看基于线框理解生成的 3D 概念图时，优先使用 [同源参数化六视图校正版](GeneratedConcepts/02_parametric_consistent_views/README.md)；[六图总览](GeneratedConcepts/02_parametric_consistent_views/00_contact_sheet.png) 与爆炸、顶、正、背、左、右六张独立 PNG 均由同一份确定性几何生成。旧版 [ImageGen 五视图](GeneratedConcepts/01_pushcard_3d_exploded_five_views_v1.png) 仅保留为构思记录，已因左右视角及顶板造型不一致而被校正版取代。
- [00_contact_sheet.jpg](00_contact_sheet.jpg) 从左上到右下按 01–22 排列，空白格表示没有为凑数保留低价值图片。

## 图片索引

| 编号 | 文件 | 主要建模用途 | 来源 |
| --- | --- | --- | --- |
| 01 | [KOVO 透明壳正面](01_kovo_transparent_internal_front.jpg) | 外轮廓、透明壳厚度、内部件位置和掌中比例 | L1 |
| 02 | [KOVO 烟灰壳轨道近景](02_kovo_smoke_internal_track_closeup.jpg) | 导轨、内槽、嵌套壳体、半透明材质与内部阴影 | L1 |
| 03 | [KOVO 拇指握持](03_kovo_thumb_grip.jpg) | 拇指接触面、圆角安全区、单手操作尺度 | L1 |
| 04 | [Matrix Limite 推滑姿态](04_matrix_limite_slide_grip.jpg) | 推力方向、侧边抓握、滑动面暴露量 | L2 |
| 05 | [Matrix Limite 掌中尺度](05_matrix_limite_palm_scale.jpg) | 整机长宽比例、掌中视觉体量 | L2 |
| 06 | [Matrix Limite 双盖板](06_matrix_limite_dual_backplate.jpg) | 前后盖分件、接缝、双层板与边缘倒角 | L2 |
| 07 | [Tita Pro 层叠金属机身](07_tita_pro_layered_body.jpg) | 金属板层级、轮廓切面、装饰槽和材质分区 | L3 |
| 08 | [USD1020916 透视图](08_usd1020916_perspective.png) | 整体体块、圆角半径趋势、双圆机构布局 | P1 |
| 09 | [USD1020916 正视图](09_usd1020916_front.png) | 对称轴、孔位、两组主机构的平面比例 | P1 |
| 10 | [USD1020916 背视图](10_usd1020916_rear.png) | 后盖轮廓、背面简化关系 | P1 |
| 11 | [USD1020916 侧视图](11_usd1020916_side.png) | 总厚度分配、盖板外鼓与中层接缝 | P1 |
| 12 | [USD1020916 正向爆炸图](12_usd1020916_exploded_front.png) | 前后总成、内部滑块与层级关系 | P1 |
| 13 | [USD1020916 透视爆炸图](13_usd1020916_exploded_perspective.png) | 组件堆叠顺序、拆装方向、内部容积 | P1 |
| 14 | [CN218011061 内部轨道与磁铁](14_cn218011061_internal_tracks_magnets.png) | 长槽导轨、止挡、磁铁阵列和壳体配合 | P2 |
| 15 | [CN218011061 可替换面板](15_cn218011061_replaceable_panel.png) | 可拆外盖、磁吸面板与模块化壳体 | P2 |
| 16 | [Magnus 磁铁间距示意](16_magnus_magnet_spacing_layout.png) | 等距/非等距磁铁阵列对比、段落位置规划 | W1 |
| 17 | [Magnus V8 材质与掌中尺度](17_magnus_v8_material_palm_scale.jpg) | 黑色金属、钢/黄铜对比、磁铁孔、边缘倒角和尺度 | W2 |
| 18 | [Lautie Shuffle V3 三层机身](18_lautie_shuffle_v3_three_layer.jpg) | 三层卡身结构、层间缝隙、表面装饰分区 | W3 |
| 19 | [Lautie Shuffle V3 动作序列](19_lautie_shuffle_v3_action_sequence.jpg) | 滑动行程、手指轨迹、动作关键帧 | W3 |
| 20 | [Lautie Shuffle V3 中层拆除](20_lautie_shuffle_v3_layer_removal.jpg) | 两层/三层切换、可拆中层与装配方向 | W3 |
| 21 | [Lautie Shuffle V3 磁铁细节](21_lautie_shuffle_v3_magnet_detail.jpg) | 圆片磁铁、定位孔、背板与层间接触面 | W3 |
| 22 | [EDCELL TapeDrive 双转子表面](22_edcell_tapedrive_rotor_surface.jpg) | 双偏心转子、透明复合壳、金属与聚合物同机 PBR | W4 |

## 来源

### 本地 Obsidian 实拍

- **L1**：`/Users/jiawei.zhou/Documents/Obsidian Vault/笔记同步助手/2026-08-01/手感巴适，声音得劲~【浮光-KOVO】.md`
- **L2**：`/Users/jiawei.zhou/Documents/Obsidian Vault/笔记同步助手/2026-08-01/无限旋转的解压玩具？.md`
- **L3**：`/Users/jiawei.zhou/Documents/Obsidian Vault/笔记同步助手/2026-08-01/2026 广州硬核装备展览会逛展攻略.md`

### 专利与公开产品页

- **P1**：[USD1020916S1 — Fidget toy](https://patents.google.com/patent/USD1020916S1/en)。本包图片从专利原始 PDF 以 300 dpi 渲染，不使用网页 120 px 缩略图。
- **P2**：[CN218011061U — 一种可拆卸拼接的磁力推牌](https://patents.google.com/patent/CN218011061U/zh)。本包保留内部导轨、磁铁和可替换面板图。
- **W1**：[Magnus — New Designs and Equidistant Magnets](https://magnusfidgets.com/blogs/blog/new-designs-and-equidistant-magnets)。
- **W2**：[Magnus V8 3-Click Titanium Slider](https://magnusfidgets.com/products/v8-3-click-titanium-slider)。页面标称 48 × 30 × 16 mm、2 × 4 磁铁布局；这些只作为比例提示。
- **W3**：[Lautie Shuffle V3](https://lautie.com/product/shuffle-v3-fidget-slider/)。
- **W4**：[EDCELL TapeDrive](https://nxedc.com/products/tapedrive)。页面标称 42 × 24 × 13 mm；这些只作为比例提示。

## 建模边界与建议

1. 先建立原创的中性结构：外盖、结构板、低摩擦接触层、磁铁模块、导向/止挡，以及可选的转子模块。
2. 正交和爆炸图用于推断拓扑与装配关系；实拍图用于校正体量、手指可达性和高光走向。
3. 参考图片中的商标、图案和装饰性外观不应直接复制到最终产品；优先抽象机械原则并重新设计轮廓语言。
4. 进入生产或 3D 打印前，必须用实体测量与机构样件重新确认尺寸、磁铁极性、间隙和公差。

## 筛选规则与版权

- 已排除严重失焦、高速动态模糊、纯包装、空场景、重复角度和对结构无帮助的氛围图。
- 第三方图片只作为项目内部研究与建模参考；权利归原作者、专利权人或页面发布方所有。不要将它们直接作为游戏纹理、宣传素材或重新分发。
