# Badge 视觉方案总表

最后更新：2026-08-09

这份清单列出本专项目前产生过的全部视觉方向、对应文件与当前结论。过程稿保留用于追溯，但只有标记为“生产”的文件可以进入运行时。

| 编号 | 方向 | 主要特征 | 当前结论 | 预览文件 |
|---|---|---|---|---|
| A | Arc Reactor Core | 重型能源核心、装甲框架、高对比发光 | 否决：太重、太游戏装甲 | `Artifacts/BadgeSpecial/Concepts/direction-a-arc-reactor.png` |
| B | Tactical Prism | 紫色棱镜、尖锐战术徽记、黑钢 | 否决：钢铁直男感过强 | `direction-b-tactical-prism.png` |
| C | Forged Relic | 锻造遗物、厚重旧金属、仪式感浮雕 | 否决：复古、厚重，不符合科技冷感 | `direction-c-forged-relic.png` |
| B2 | Soft Rounded Prism | 更薄框架、圆角、浅钛银、半透明紫 | 否决：仍复杂且整体偏浅 | `direction-b2-soft-rounded.png` |
| B3 | Balanced Rounded Prism | 恢复深色对比、减少装甲厚度和尖刺 | 否决：中心仍细碎，语义不足 | `direction-b3-balanced-rounded.png` |
| B4 | Semantic Lightweight | 用真实成就数字和类别锚点建立语义 | 过程稿：语义结构保留，外形不采用 | `direction-b4-semantic-lightweight.svg/.png` |
| Monoline | Rounded Monoline 全量 40 枚 | 紫色圆角连结环语言、统一线性图形 | 明确否决：渐变线冒充管径、拼接关系不成立、数字丢失 | `badge-category-glyphs-monoline`、`badge-glyph-catalog-*`、`VectorGlyphs/` |
| B5 | Physical Light Tube | 实体灯管截面、暗侧壁、圆端帽和外辉光 | 否决：形状仍僵硬，材质像霓虹 | `direction-b5-physical-light-tube.svg/.png` |
| B5.1 | Diffuse Mist Tube | 雾紫/雾蓝漫反射、短距离微投影 | 过程修订：材质原则保留 | 沿用 B5 工作文件，无独立交付图 |
| B5.2 | Centered Tube System | 统一 icon slot、四向留白、物理连接规则 | 过程修订：对齐和连接原则保留 | 沿用 B5 工作文件，无独立交付图 |
| B6 / B6.1 | Neo-Organic Symbols | 黑白正负形、旋转秩序、有机柔性尖角；B6.1 重画类别构成 | 否决：没有忠实达到参考母版 | `direction-b6-neo-organic-symbols.svg/.png` |
| B7 | Reference-Faithful Symbols | 无框九宫格、大剪影、印刷雾感 | 过程母版：形状语言接近，缺少金属材质 | `direction-b7-reference-faithful-symbols.png` |
| B8 Glyph | Diffuse Chrome Symbols | Y2K 冷银铬、雾面高光、几何对称 | 批准：正式符号母版 | `direction-b8-diffuse-chrome-symbols.png` |
| B8 Type | Typography Lockup | Oxanium 数字、统一基线、语义短名 | 批准后压缩：Badge 内最多两行 | `direction-b8-typography-lockup.svg/.png` |
| B8 Container | Rarity Containers | 黑色皮革、冷银包边、圆角矩形/椭圆/双盾牌 | 已批准母版；2026-08-09 正在进行 B8.1 圆润包边、皮革和尺寸修订 | `direction-b8-rarity-containers.svg/.png` |
| Production B8 | 40 枚 SVG/PNG | 21 玩具、13 藏家、4 周挑战、周期总章、Legacy；底图无文字 | 生产资产，运行时使用 | `Assets/Plugins/iOS/BadgeArtwork/` 与 `Artifacts/BadgeSpecial/ProductionB8/` |
| B8.1 Native | Compact Diffuse Chrome | 圆钝盾形、多层冷银包边、微孔黑皮革、统一两行排版；最近目标/图鉴/详情/分享卡宽度分别为 54/118/154/122 pt | 2026-08-09 明确否决：图标扁平、偏小、灰暗，边框工程描线过多，与批准母版失去关系 | 旧版 `Artifacts/BadgeSpecial/NativeB8/` 已被后续截图覆盖 |
| B8.2 Recovery Concept | Reference-Faithful Liquid Chrome | 严格以用户参考为唯一母版，恢复液态银体积、柔光、单主外沿和固定两行比例 | 当前材质纠偏母版；由内置 ImageGen 生成，仅作重绘参考 | `Artifacts/BadgeSpecial/Concepts/direction-b8-reference-recovery.png` |
| B8.2 Native | Reference Match | 40 枚 SVG 使用真实 chrome 渐变、暗反射、窄高光与柔光；八枚关键语义按参考重画；容器曾固定为 3.1% 宽外边、1.9% 净间距、0.8% 细内线 | 2026-08-09 否决：机械等宽描边与假厚薄仍然难看 | `Artifacts/BadgeSpecial/NativeB8/badge-native-rim-experiment-rejected.png` |
| B8.3 Concept | Milled Rim | 单一连续铣削金属外框、固定净间距、克制细 keyline、可辨黑皮革；不同剪影共用连续曲率语言 | 材质获认可；轮廓种类与比例已由 B8.4 收敛 | `Artifacts/BadgeSpecial/Concepts/direction-b8-3-milled-rim.png` |
| B8.4 Concept | Two Shapes / Square | 保留 B8.3 材质，只使用圆角矩形与紧凑盾牌；全部画布和容器安全区按 1:1 规范 | 当前唯一视觉候选，等待明确批准后转译为原生组件 | `Artifacts/BadgeSpecial/Concepts/direction-b8-4-two-shapes-square.png` |
| B8.5 Motion / Focus | Semantic Option Expansion | 8 个现有动力、技巧、Combo 与专注成就的语义图形 option；负形星核、连续回环、彗星动势 | 当前扩展候选，等待选择；未进入生产资产 | `Artifacts/BadgeSpecial/Concepts/direction-b8-5-motion-focus-options.png` |
| B8.5 Collector / Challenge | Semantic Option Expansion | 8 个现有节奏、探索、精通、收藏与周期挑战的语义图形 option；轨道、闭合循环、三核心 | 当前扩展候选，等待选择；未进入生产资产 | `Artifacts/BadgeSpecial/Concepts/direction-b8-5-collector-challenge-options.png` |
| B8.6 Native | Square Fit / Three Columns | 40 枚图形按可见最长边 74% 等比适配并几何居中；正圆禁止拉伸；只保留 1:1 圆角矩形/紧凑盾牌；375 pt 使用 20 pt 侧边距、14 pt 列间距和 102.33 pt 三列卡片 | 布局规则保留；首张预览因误用旧 glyph 被否决 | 旧截图已由 B8.7 覆盖 |
| B8.7 Native | B8.5 Liquid Chrome Recovery | 严格恢复 B8.5 的三瓣漩涡、双星、彗星、正圆轨道、双环、五节点环、眼与月牙；去除粗黑 cartoon outline，保留液态银、柔光和 1:1 三列 | 当前真实原生候选，等待视觉批准；尚未安装到 iPhone | `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png` |
| B8.8 Native | Rounded Hex / Binary Illumination | 全部统一 1:1 圆角六边形；已获得为点亮冷银金属，未获得/进行中/隐藏为黑灰石墨；不生成新 icon | 当前真实原生候选，等待视觉批准；尚未安装到 iPhone | `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png`、`badge-native-states.png` |
| B8.9 Native | Pointed Hex / Larger Safe Area | 左右端点恢复尖角，四个斜角保留圆润；icon slot 从 56% 收到 46%，扩大四向安全留白；明暗状态沿用 B8.8 | 当前真实原生候选，等待视觉批准；尚未安装到 iPhone | `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png`、`badge-native-states.png` |
| B8.10 Native | Vertical Point Hex | 依照参考把六边形旋转为上下圆润尖端、左右竖边；六角统一圆润；沿用 46% icon slot 与 B8.8 明暗状态 | 当前真实原生候选，等待视觉批准；尚未安装到 iPhone | `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png`、`badge-native-states.png` |
| B8.11 Native | External Milestone Metadata | 六边形内仅保留 icon 与核心 Token；里程碑短名移到外部下方，进度条位于短名下面并按三列统一基线 | 当前真实原生候选，等待视觉批准；尚未安装到 iPhone | `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png`、`badge-native-states.png` |
| B8.12 Native | Material Recovery | 全量 Icon 恢复暗侧厚度、冷银强反差、窄高光与漫反射光晕；内底改为手机尺寸可辨的密集黑色粒面皮革；预览强制重建全部 PNG | 当前真实原生候选，等待视觉批准；尚未安装到 iPhone | `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png`、`badge-native-detail.png`、`badge-native-states.png` |
| B8.13 Native | Centered Type | Icon + Token 使用 64% 固定内容高度并强制对齐六边形几何中心；主 Token 降为 12.4%，外部名称统一为 9.5 pt / 13 pt 居中槽 | 当前真实原生候选，等待视觉批准；尚未安装到 iPhone | `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png`、`badge-native-detail.png`、`badge-native-states.png` |

## 当前唯一生产方向

当前不再并行推进 A–B8.3。B8.5 是唯一图形视觉母版，B8.6 保留 1:1 与三列布局规则，B8.7 保留液态银图形，B8.8 保留解锁/未解锁状态，B8.10 保留纵向圆角六边形，B8.11 保留外置名称/进度，B8.12 保留全量五层冷银结构、运行时漫反射光晕和密集黑色粒面皮革；B8.13 是当前 shipping SwiftUI 候选，在上述视觉不变的前提下锁定内容几何居中与缩小字号。A–B8.3、旧 `VectorGlyphs`、B8.6 旧 glyph 预览、B8.8 全圆六角轮廓、B8.9 横向尖角轮廓及任何新 SVG/旧 PNG 混用结果禁止作为批准版本进入发布构建。
