# Badge 视觉资产与动效规范

最后更新：2026-08-08

## 视觉目标

Badge 是游戏化收藏物，不是 SF Symbol 外面套一圈玻璃。它必须在 64 pt 下仍能一眼识别类别，在 160 pt 详情页中又能显示实体金属、珐琅和能源层次。主方向为高能科幻徽记，不能复制 Apple Fitness、主机奖杯或现有游戏 IP。

## 概念方向

- A · Arc Reactor Core：`Artifacts/BadgeSpecial/Concepts/direction-a-arc-reactor.png`
- B · Tactical Prism Insignia：`Artifacts/BadgeSpecial/Concepts/direction-b-tactical-prism.png`
- B2 · Soft Rounded Prism：`Artifacts/BadgeSpecial/Concepts/direction-b2-soft-rounded.png`
- B3 · Balanced Rounded Prism：`Artifacts/BadgeSpecial/Concepts/direction-b3-balanced-rounded.png`
- B4 · Semantic Lightweight System：`Artifacts/BadgeSpecial/Concepts/direction-b4-semantic-lightweight.svg` / `.png`
- Rounded Monoline 类别母版：`Artifacts/BadgeSpecial/Concepts/badge-category-glyphs-monoline.svg` / `.png`
- 全量图鉴：`badge-glyph-catalog-toy`、`badge-glyph-catalog-collector`、`badge-glyph-catalog-challenge` 的 `.svg` / `.png`
- B5 · Physical Light Tube：`Artifacts/BadgeSpecial/Concepts/direction-b5-physical-light-tube.svg` / `.png`
- B6.1 · Neo-Organic Symbols：`Artifacts/BadgeSpecial/Concepts/direction-b6-neo-organic-symbols.svg` / `.png`
- B7 · Reference-Faithful Symbol Sheet：`Artifacts/BadgeSpecial/Concepts/direction-b7-reference-faithful-symbols.png`
- B8 · Diffuse Chrome Symbols：`Artifacts/BadgeSpecial/Concepts/direction-b8-diffuse-chrome-symbols.png`
- B8 Typography Lockup：`Artifacts/BadgeSpecial/Concepts/direction-b8-typography-lockup.svg` / `.png`
- B8 Rarity Containers：`Artifacts/BadgeSpecial/Concepts/direction-b8-rarity-containers.svg` / `.png`
- C · Forged Relic：`Artifacts/BadgeSpecial/Concepts/direction-c-forged-relic.png`

这些概念板由内置 ImageGen 生成，只用于材质、轮廓和层级探索。正式资产必须人工重绘为可控几何，不直接裁切概念板投入运行时。

用户选择 B 的棱镜游戏感，但要求削弱“重装钢铁直男风”，增加圆角和轻量质感。B2 验证了更薄框架、留白、圆角端点、钛银和半透明薰衣草珐琅，但整体偏浅；B3 恢复近黑背景与约七成深色对比，只减薄约 20% 装甲质量并收短尖刺。两者都已被后续方向取代，不是当前生产母版。

进一步反馈确认 B3 仍然结构复杂、中心元素细碎，而且第一轮 8 枚图形没有绑定实际成就。B4 改为完全可编辑的矢量语义系统，每枚只保留轻量外框、一个类别锚点和一个主数字或主图形；代表样本明确对应 `100K 操作`、`×50 Combo`、`3.5 km/h`、`10h 专注`、`Perfect`、`12W 节奏`、`LV.100 精通`、`25 外观收藏`。

用户曾确认 Chain Reactor 的圆角连结环语言并要求应用到所有 icon，因此产生了 Rounded Monoline 的 40 枚全量尝试。后续实图复核明确否决了该批次：直接渐变描边缺少实体管径，复杂 glyph 存在生硬拼接与不成立的连接关系，而且全量图鉴错误地把里程碑数字移出 Badge。`Artifacts/BadgeSpecial/VectorGlyphs/` 与三张旧图鉴只能作为被否决的过程记录，禁止进入运行时或宣称为生产资产。

B5 改用 Physical Light Tube：每根图形由暗侧管壁、实体色管身、偏移高光、外部辉光与圆形端帽构成，不再用单条渐变线冒充材质。B5.1 根据用户参考进一步改为 Diffuse Mist Tube：降低辉光和高光对比，使用雾紫/雾蓝/暖雾金的低对比漫反射材质，并将阴影收敛为短距离微投影；禁止白热内芯和硬质霓虹边。B5.2 统一采用 `128 × 80` icon slot，中心固定为 `(140, 88)`，图形与 Badge 内框保持稳定四向留白；箭头、节奏、Perfect 与精通轮廓改用连续 Bézier 曲线和圆滑转角，不再使用僵硬折线。所有开口都必须是真实端帽；闭环必须完整；多物体交叉只能靠明确的前后层级遮挡，不允许用悬空短段、伪 T 形连接或无来源的拼接。里程碑数字恢复为 Badge 中央主视觉，类别灯管只占上方识别区。B5–B5.2 均已被后续符号母版取代，未扩展为 40 枚生产资产。

B6.1 根据用户提供的黑白符号参考，停止沿用灯管作为主造型，改为 Neo-Organic Symbol：高对比雾白实形、明确正负空间、旋转/镜像秩序、有机曲面与柔性尖角，并叠加克制的白色 bloom 和扫描纹理。八枚符号仍绑定真实语义：重复软脉冲、双环 Combo、三片动势与轨道、四向 Focus、对齐 Perfect、波动网格、三重 Mastery 完成体、六片 Collection 光圈。不得复制参考图的现成符号；数字、安全区和统一排版规则继续保留。B6.1 随后被用户否决，只保留其正负空间探索记录。

用户明确指出 B6.1 仍未忠实抓住参考，原因是继续保留金属 Badge 外框、数字和过小符号，破坏了参考图的无框九宫格、大面积黑白剪影与印刷雾感。B7 因此先只验证 icon 形状语言：无容器、无数字、无标题，九枚符号在等分方格中保持相同光学占比和四向留白；使用温白实形、强正负空间、旋转/镜像秩序、少量细轨道、柔光与黑色织物纹理。B7 PNG 是 ImageGen 风格母版，不是生产资产；确认后必须逐枚人工描成 SVG，再由原生 Badge 组件叠加统一数字层。

用户随后指定新的 Y2K Chrome Shapes 图片作为形状与材质参考母版，并要求保留 B7 的漫反射光感。B8 将两者合并：符号采用镀铬尖瓣、星芒、轨道、旋转完成体和圆润倒角，表面同时具备银色镜面高光、石墨暗反射与克制的雾白 bloom；九宫格的相同光学占比、四向留白、黑色织物背景继续沿用。B8 不使用彩虹铬、厚重装甲、塑料高光或外框。用户已明确认可 B8，并追加生产约束：所有金属倒角必须圆润连续；主体必须轴对称、中心对称或严格旋转对称；色彩限定冷银、石墨黑和低饱和冷白；整体保持科技冷感与肃穆感。B8 PNG 是批准的视觉母版，但仍不是生产资产；数字由后续 Badge 组件独立叠加，正式生产必须人工重绘 SVG/材质分层。

### B8 生产约束

- 倒角：所有外缘与内孔使用连续圆角/圆润倒角；即使剪影有受控尖端，金属截面也不能形成刀刃式硬切面。
- 对称：优先垂直轴对称、中心对称和 3/4/6 向严格旋转对称。任何非对称动势必须来自明确的 Speed/Combo 语义，并保持质量中心居中。
- 冷感：chrome base 使用中性冷银，dark reflection 使用石墨黑，specular 使用低饱和冷白；禁止暖金、铜色、彩虹铬和高饱和彩色光。
- 肃穆：材质对比克制，漫反射雾光范围稳定，镜面高光窄而连续；禁止卡通弹性、俏皮表情、夸张霓虹和随机碎片。

### B8 文字组合

- 3×3 预览中的每格使用同一 icon viewport、水平中心线和固定文本槽位；不根据单枚内容目测移动。
- 主 Token 固定 Oxanium 720 / 40 pt；`100K`、`×50`、`3.5`、`10h`、`PERFECT`、`12W`、`100`、`25`、`4/4` 共用同一基线和字号。
- 单位固定 Oxanium 650 / 14 pt，并占用独立固定行；`KM/H`、`LV`、`CYCLE` 的出现与否不能改变标题位置。
- 英文标题固定 Oxanium 680 / 16 pt；中文条件固定系统字体 13 pt。标题、条件与 icon 均水平居中，三行基线在所有格中完全一致。
- `direction-b8-typography-lockup.svg/.png` 只验证文字层级与对齐，尚不是 native Badge 页面截图。

### B8 稀有度容器

- 内底统一使用近黑皮革，仅保留低对比、不规则的细颗粒与浅压纹；不得出现规则波纹、强噪点或抢占信息层级的高光。
- Ignition 使用单层冷银描边圆角矩形；Overdrive 使用双层描边竖向椭圆；Apex 使用圆肩软盾牌与增强边缘高光；Singularity 使用纵向仪式盾牌、双层金属描边和克制冷白雾光。稀有度由轮廓、层数和光学强度共同表达，不能只换颜色。
- 每枚容器最多保留两行文字：第一行是核心 Token/结果，第二行是单个短名称。单位必须并入 Token 同一行；等级名由外框形状表达，不再重复显示。中文条件、详细描述、获得日期和进度全部移到详情页。
- 容器由首版 `250 × 478` 压缩为 `250 × 320`，减少约 33% 的纵向长度；`286 × 340` 局部坐标中，icon viewport 固定为 `156 × 156`、中心 `(143, 117)`，两条文字基线固定为 `226 / 260`。
- 不能把九宫格原图的 cell 几何中心当作 icon 的可见中心。每枚符号需先测量非黑色可见轮廓包围盒，再用独立 viewBox 偏移将该包围盒中心严格映射到统一的 `(143, 110)`；不得共用未经校正的裁切原点。
- 内容统一沿容器几何中心线水平居中；顶部及左右最小安全间距为 24 pt。圆角、椭圆与盾牌不得为了迁就单枚文字而改变内部基线或局部缩放。
- `direction-b8-rarity-containers.svg/.png` 是稀有度、材质和排版的组合预览。用户已于 2026-08-08 明确批准该短版两行方案，可作为全量生产母版；它仍不是 native Badge 页面截图，也不代表运行时已经接入。

### B8.1 原生尺寸与材质修订

- 真实 SwiftUI 使用统一尺寸 token：最近目标 `54 pt`、两列图鉴 `118 pt`、详情页 `154 pt`、1080 分享卡逻辑宽度 `122 pt`，禁止在页面内继续写散落常量。
- 盾形肩部使用连续切线，底部由宽圆弧闭合而非单点尖角；边框依次包含外暗沿、冷银主带、偏置高光、内暗边和内层铬线，以截面层次而不是增加装饰碎片表达稀有度。
- 黑色皮革以内凹微孔为主、极短随机压纹为辅；远看保持肃静近黑，近看才能识别材质。禁止重复波纹、长划痕、规则扫描线和高反差噪点。
- B8.1 于 2026-08-09 被用户明确否决：运行时图标变成偏小、灰暗的扁平 pictogram，边框又叠加了多道工程描线，与已经批准的 B8 Compact Rarity Badges 母版没有保持视觉关系。

### B8.2 Reference Match

- 用户提供的 `codex-clipboard-e3e6b7f9-98e4-4f92-832b-93ff354d0157.png` 是唯一视觉母版。图标必须是容器里最亮、最有体积的主体，不能再使用平面灰填充或小型线性 glyph。
- 内置 ImageGen 只用于生成严格母版回归的材质参考 `Artifacts/BadgeSpecial/Concepts/direction-b8-reference-recovery.png`；正式运行时仍由可控 SVG 与 SwiftUI 重绘。
- 生产 SVG 的 tube、plate、orb 必须真正使用液态银 chrome 渐变，并拥有石墨暗侧、窄白高光、轻微 bloom 和接触阴影。八枚代表语义固定为三弯月 Pulse、双实体环 Chain、三道速度矢量与轨道 Redline、四向轨道球体 Focus、四芒 Perfect、圆润八节点 Rhythm、五叶 Mastery 和有中心开孔的 Vault。
- 原生 icon viewport 固定为容器宽度的 `0.64`；容器只保留主金属外沿和一条内线，不允许恢复第三道轮廓。主数值仍使用统一 Oxanium 基线，`KM/H` 是同一行的小单位。
- 所有稀有度共用同一套双层包边截面：外侧宽铬边为容器宽度的 `3.1%`，外边至内线的净间距为 `1.9%`，内侧细线为 `0.8%`。两层都由同一个 `InsettableShape` 生成真实等距轮廓，禁止使用 `scaleEffect` 模拟缩放内框，也禁止按等级增删轮廓层。Apex 与 Singularity 共用同一条圆肩、连续切线和圆钝底尖的盾牌曲线；等级差异仅来自规定的轮廓类别与克制的亮度，不得改变包边宽度或间距。
- B8.2 于 2026-08-09 被用户明确否决为“好丑”：统一尺寸本身没有解决材质问题，外框仍被看成机械等宽描边，局部明暗又制造了视觉上的假厚薄；该参数组合不得继续作为批准候选。

### B8.3 Milled Rim

- 内置 ImageGen 以原始 B8 母版为唯一编辑目标，仅重新探索容器包边和黑色皮革内底，输出 `Artifacts/BadgeSpecial/Concepts/direction-b8-3-milled-rim.png`。图中的宽外框必须被理解为一个连续铣削金属件：暗外缘、柔和银色冠面与内侧压暗属于同一截面，不得拆成三条有间距的工程描线。
- 外侧金属件、空隙与内侧细 keyline 在所有轮廓中分别保持固定宽度；圆角矩形、椭圆、圆肩盾和软盾保留不同剪影，但共用连续切线、对称性与末端微圆角语言。皮革纹理需要在近看可辨、缩略图中退后。
- B8.3 当前只有材质与几何概念图，尚未被精确重绘进 shipping SwiftUI；必须先获得明确视觉批准，再锁定数值并输出新的真实原生截图。批准前不得构建或安装到 iPhone。

### B8.4 Two Shapes / Square

- 用户确认 B8.3 的铣削冷银包边、近黑皮革和液态铬图标质感，轮廓系统进一步收敛为仅两种：圆角矩形与紧凑盾牌。椭圆、胶囊、纵向长矩形和第三种盾形全部移除。
- 全部生产 artwork 与分享/thumbnail 画布固定为 `1:1`；每枚容器放入相同正方形安全区。圆角矩形使用连续中等圆角；盾牌使用浅圆肩、短收腰和微圆盾尖，不能恢复纵向拉长比例。两种轮廓共用相同金属带厚度、外框至内线净距、细 keyline、内部 padding 与水平/垂直中心规则。
- 当前 2×4 方形概念预览为 `Artifacts/BadgeSpecial/Concepts/direction-b8-4-two-shapes-square.png`，1254 × 1254、sRGB。它仍是视觉定稿候选而非 shipping 原生截图；明确批准后才转译为 SVG/SwiftUI 并输出实际页面预览。

### B8.5 Semantic Option Expansion

- 用户提供的 `export.zip` 含 10 张黑白抽象符号参考，已解压到 `Artifacts/BadgeSpecial/References/export-icons/`。这些参考只用于提炼负形星核、连续轨道、闭合回环、切角面和彗星动势，不直接复制现成标志、字母造型、版权符号或水印。
- B8.5 不新增成就规则，而是为现有定义补充 16 个具有明确语义的视觉 option。动力/技巧/Combo/专注板包含 `1K PULSE`、`10K PULSE`、`SPEED CONTROL`、`ENDURE CONTROL`、`×20 CHAIN`、`×50 CHAIN`、`30M FOCUS`、`2H FOCUS`；收藏/挑战板包含 `12W RHYTHM`、`5 EXPLORE`、`LV 100 MASTERY`、`10 VAULT`、`3× REDLINE`、`2×20 REACTOR`、`3 CORE RAID`、`4/4 CYCLE`。
- 所有新增 option 继承 B8.4：只使用 1:1 圆角矩形与紧凑盾牌、同一铣削冷银包边、同一细 keyline、近黑皮革、液态铬图标、固定 icon viewport、两行文字和一致安全区。复杂图形必须使用闭合、可解释的前后遮挡，不得出现悬空拼接。
- 两张 1254 × 1254、sRGB 概念板为 `Artifacts/BadgeSpecial/Concepts/direction-b8-5-motion-focus-options.png` 与 `Artifacts/BadgeSpecial/Concepts/direction-b8-5-collector-challenge-options.png`。它们用于扩大视觉选择范围，尚不是 1024 透明生产资产或真实原生页面截图。

### B8.6 Square Icon Fit / Three-Column Catalog

- 每枚生产图形先在 1024 × 1024 透明画布中测量 `alpha >= 16` 的可见包围盒，再以最长边为唯一缩放基准做等比 `aspect fit`。最长可见边固定为画布的 74%，即目标 `758 px`；另一边只跟随同一缩放系数变化，不允许分别缩放 X/Y。
- 标准化后把可见包围盒中心映射到画布几何中心。横向图形先触达最大允许宽度，高度按原比例收缩；纵向图形先触达最大允许高度，宽度按原比例收缩。标准化脚本必须幂等，重复执行不得继续漂移或失真。
- 所有圆环、圆珠和轨道圆必须以相同直径生成正圆；生产 SVG 禁止 `<ellipse>`，SwiftUI/PNG 也禁止非等比拉伸。规则验证同时检查 40 枚 PNG 的方形尺寸、sRGB、透明通道、最长边和中心误差。
- 运行时 Badge 和 icon slot 都固定为 1:1；icon slot 宽高均为 Badge cell 的 56%。容器只允许圆角矩形和紧凑盾牌两种剪影，Ignition/Overdrive 使用前者，Apex/Singularity 使用后者。
- 图鉴固定为三列。以 375 pt 宽屏幕为基准：左右 margin 各 `20 pt`，两处列间距各 `14 pt`，因此每格宽度为 `(375 - 20 × 2 - 14 × 2) / 3 = 102.33 pt`。更宽或更窄设备保持三列，并由同一公式使用剩余宽度弹性计算，不逐机型写死卡片宽度。
- 实际 shipping SwiftUI 截图为 `Artifacts/BadgeSpecial/NativeB8/badge-native-catalog.png` 与 `badge-native-reference.png`；生产资产总览为 `Artifacts/BadgeSpecial/ProductionB8/badge-b8-catalog-toy.png`。当前等待视觉批准，批准前不得构建或安装到 iPhone。

### B8.7 B8.5 Liquid Chrome Recovery

- B8.6 的 1:1、最长边等比适配和三列布局规则继续保留，但其第一张原生预览误用了旧生产 glyph，用户已明确否决该图形选择。旧的粗黑卡通描边、扁平银色填充和早期语义造型不得再作为批准候选。
- `direction-b8-5-motion-focus-options.png` 现在是图形造型与材质的唯一母版。八枚代表章固定为：三瓣 Pulse 漩涡、双四芒 Pulse、带负形星核的水平 Speed 彗星、正圆 Endurance 轨道、双正圆 Chain、五节点正圆 Chain Reactor、正圆核心 Eye Focus、月牙 Focus。
- ImageGen 仅用于从母版隔离无文字的液态银材质参考，源与透明检查图位于 `Artifacts/BadgeSpecial/References/B85LiquidChrome/`；它们不直接进入 Bundle。shipping 资产仍由 `generate_b8_badges.py` 输出可控 SVG，再渲染为 1024 × 1024 透明 sRGB PNG。
- 全量 40 枚 SVG 统一删除粗黑 cartoon outline，改为平滑液态银、石墨侧面、窄幅柔白高光和克制 bloom。上述八枚代表语义已独立重画；双环和所有轨道只使用 `<circle>` 或等半径圆弧，不允许椭圆或非等比缩放。
- 当前真实原生确认图为 `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png`，标题 `B8.7 · B8.5 VISUAL`。它保留 1:1 slot 和手机三列规则，等待用户视觉批准；批准前不得构建或安装到 iPhone。

### B8.8 Rounded Hexagon / Binary Illumination

- 用户指定 Apple Fitness 奖章页作为状态与容器参考。所有等级统一使用一个 1:1 圆角六边形，不再以圆角矩形、盾牌或等级差异改变外部剪影；稀有度信息留在详情数据，不通过容器变形表达。
- 六边形使用水平上下边、左右中点和六个连续二次曲线圆角，六个顶点与圆角比例由同一 `InsettableShape` 计算；外框、留缝和内线均复用同一等距几何，不逐枚调整。
- 状态只使用两组明确材质：`Unlocked` 为点亮的冷银铣削边、完整液态银 icon、柔白高光和可辨皮革；`Locked / InProgress / Hidden` 为黑灰石墨边、深黑内底、低亮灰色 icon/文字且无白色 glow。进行中允许保留一条克制灰色进度线，但不能让未获得章看起来已经点亮。
- icon 造型继续沿用 B8.5，不生成新图形。1:1 最长边适配、375 pt 三列公式和动态两行文字规则保持不变；本轮只改变容器与状态渲染。
- 当前真实预览为 `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png`，状态对照为 `badge-native-states.png`，标题 `B8.8 · HEX STATES`。等待用户视觉批准，批准前不得构建或安装到 iPhone。

### B8.9 Pointed Hex / Larger Safe Area

- B8.8 将六个顶点全部圆化，导致参考中应当清晰的左右两端变钝；icon slot 又占 Badge 宽度 56%，四向留白不足。该组合由 B8.9 覆盖，不再作为批准候选。
- 当前横向六边形保留左右两个精确尖点，只对左上、右上、右下、左下四个斜角使用连续二次曲线圆角。外框与内线仍由同一个 `InsettableShape` 计算，不允许内外轮廓端点角度漂移。
- icon slot 从 56% 缩小到 46%，仍为严格正方形并执行最长边等比适配；Token、短名和状态进度的基线不变，因此新增空间全部成为 icon 与边框之间的真实安全留白。
- 已获得冷银点亮、未获得黑灰石墨的 B8.8 状态规则保持不变，也不生成或修改任何 icon。当前真实图鉴为 `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png`，状态对照为 `badge-native-states.png`，标题 `B8.9 · POINTED HEX`。

### B8.10 Vertical Point Hex

- B8.9 对“尖端”方向理解错误，把端点放在左右并形成水平上下边；该横向轮廓由 B8.10 覆盖，不再作为批准候选。
- 当前轮廓按参考旋转为纵向六边形：顶部与底部为圆润尖端，左右各保留一段竖直边，六个转角全部使用相同的 16% 连续二次曲线圆角。外框、间隙与内线仍复用同一个 `InsettableShape`，不得分别手调。
- icon slot 继续固定为 46%，三列布局、最长边等比适配、点亮冷银与未点亮石墨状态均不改变；本轮只纠正容器方向，不生成或修改 icon。

### B8.11 External Milestone Metadata

- 六边形严格保持 1:1 金属物件，只容纳 icon 与核心数字/Token；`PULSE / CONTROL / CHAIN / FOCUS` 等里程碑短名移到六边形下方。
- 进行中进度条位于短名下方，不再遮挡皮革内底或占用 icon 安全区。非进行中状态保留等高的透明进度槽，使三列网格每一行的名称与后续内容保持同一基线。
- 纵向六边形、46% icon slot、液态银图形和解锁/未解锁材质状态全部沿用 B8.10；外置信息的布局变更本身不重绘 icon。
- 后续针对 `SPEED` 图形的定向修正不改变整体图形语言：上下翼共用一组 Bézier 控制点，下翼的最终坐标严格通过 `y = 160 - y` 计算生成，中央负形四角星锁定在 `(80,80)`；禁止再用两条独立手绘曲线近似对称，也不依赖渲染器执行镜像 transform。

### B8.12 Material Recovery

- 全量 40 枚 SVG 统一恢复五层实体金属结构：宽柔光、深色背衬、暗侧厚度、强反差冷银主体和窄白高光。Tube 使用 21/18/13.8 pt 的 bloom/dark/body 管径与独立暗侧、高光；Plate 增加 `plateDepth`，不再只靠一层渐变填充表现材质。
- shipping SwiftUI 对已解锁 artwork 叠加一层 3.2% Badge 宽度的模糊 screen bloom，并保留窄白高光与 5.2% 冷色外晕；Locked/InProgress/Hidden 不启用该光晕。
- 六边形内底使用密集不规则粒面皮革：约 118–290 个微型 pebble、细孔和极短折痕共同构成，三列尺寸只形成低对比细纹，详情尺寸可辨认，不允许退回稀疏椭圆气泡或不可见的纯黑底。
- `build_b8_assets.sh` 成为唯一正式资产流水线：每次预览前强制执行 SVG 生成、40 枚 PNG 重渲染、74% 最长边归一化和静态验证。`capture.sh` 直接调用该流水线，禁止再以新 SVG 搭配旧 PNG 输出截图。

### B8.13 Centered Type

- Icon 与核心 Token 组成高度固定为 Badge 宽度 `64%` 的内容组，它的中心点强制定位在六边形 `(50%, 50%)`；不再让不同 glyph 可见边界或字体升部改变垂直位置。
- 主 Token 从 Badge 宽度 `14.0%` 降为 `12.4%`，`KM/H` 单位从 `5.6%` 降为 `4.8%`；在 375 pt 三列的 102.33 pt 单格上，主字约缩小 `1.6 pt`。
- 外部里程碑名称统一为 `9.5 pt` Oxanium Bold，使用 `13 pt` 固定高度和几何居中；进度条位置、六边形、46% icon slot、金属、光晕与皮革材质不变。

## 构图规则

- 母版画布固定 1024 × 1024、sRGB、1:1；运行时输出透明 PNG。
- 生产图形按 B8.6 固定最长可见边 74%，视觉包围盒中心位于几何中心；概念稿中的 74%–82% 光学范围不得覆盖这项生产规则。
- 禁止把标题、描述、数字或单位烘焙进 AI/PNG 底图；品牌 Logo 和水印始终禁止。里程碑数字允许作为 Badge 主视觉，但必须由 SwiftUI 使用 Oxanium 动态排版，以保证 `50`、`100K`、`3.5` 等内容准确、可缩放、可本地化并支持无障碍。
- 每枚永久 Badge 必须拥有独立中心符号；同一系列可以共享框架语法，但不能只换色。
- 单枚结构最多三层：`frame`、`categoryAnchor`、`milestoneToken / glyph`。删除装饰性碎片、铆钉、重复小棱镜和无语义尖刺；64 pt 时最细有效线宽不低于 2 pt。
- B5.1 灯管统一为四层截面：低透明雾状色晕、18 单位暗侧管壁、14 单位低对比漫反射管身、4 单位模糊偏移高光；所有层共享同一路径和圆头/圆角。高光只表达管径，不能形成白色内芯或沿路径任意换色。
- B5.2 所有类别图形必须在同一 `128 × 80` slot 内水平、垂直居中；不得逐枚目测偏移。图形＋Token 的总视觉包围盒与 Badge 内框中心对齐，最长 Token `100K` 也必须保留双侧真实留白。数字统一使用 58 pt Oxanium 720，技巧语义 Token 统一使用 38 pt，不得按单枚内容临时缩放。
- 不允许不成立的几何连接。允许的结构只有单根连续开口管、完整闭环、彼此分离的多根管，以及通过绘制顺序形成清楚前后遮挡的独立闭环；任何分叉、悬空补段或看不出前后关系的交叉都要重画。
- 生产母版使用 SVG；材质光效只能作为轻量 `energy` 层，不得改变数字和类别锚点的清晰度。

## 数字与语义组合

| 分类 | 类别锚点 | 运行时主 Token |
|---|---|---|
| 动力 | 单一推进箭头 | `1.0` / `2.0` / `3.5` / `4.5`，单位 `KM/H` 次级显示 |
| 累计操作 | 双脉冲弧 | `100` / `1K` / `10K` / `100K` |
| 技巧 | 对准星与稳定核心 | 不放数字；显示 Clean / Power / Speed / Endurance / Perfect 对应独立 glyph |
| Combo | 两个圆角连结环 | `×5` / `×10` / `×20` / `×50` |
| 专注 | 稳定场环 | `5m` / `30m` / `2h` / `10h` |
| 节奏 | 单条节奏波形 | `1W` / `4W` / `12W` |
| 探索 | 模型轨道点 | `2` / `3` / `5` |
| 精通 | 完成体六角核心 | `LV.20` / `LV.100`；多模型要求用次级 `×3` 标记 |
| 外观收藏 | 两张圆角叠片 | `5` / `10` / `25` |
| 周挑战 | 单一循环箭头 | 当前挑战专用短 token；周期总章不放数字 |

数字占 Badge 中心视觉面积约 42%–52%，单位不超过主数字高度的 28%。完整标题、条件和进度仍位于卡片或详情页，不能继续往 Badge 内塞小字。

所有数字 Badge 必须复用唯一的 `BadgeMilestoneToken` 排版组件：Oxanium 720、统一字号与中心基线，不允许按 `25`、`×50`、`100K` 的字符数量逐枚调整字号或纵向位置。单位/前缀使用统一第二行槽位和字号，例如主行 `3.5` + 次行 `KM/H`、主行 `100` + 次行 `LV`；没有单位时第二行留空。技巧类 Badge 不使用数字组件，只使用单一 glyph。

## 类别语法

| 类别 | 核心图形语义 | 禁止替代 |
|---|---|---|
| 动力 | 推进矢量、转子切线、爆发核心 | 速度表 SF Symbol |
| 累计操作 | 脉冲阵列、重复轨迹、机械循环 | 手指图标 |
| 技巧 | 对准环、平衡轴、精确接触点 | 奖杯或星形通用符号 |
| Combo | 连接链、同步节点、级联能量 | 单纯写 `×20` |
| 专注 | 稳定场、锁定核心、长时间波形 | 人物冥想剪影 |
| 收藏者 | 多核心聚合、棱镜库、完成体 | 王冠或传统盾徽 |
| 周挑战 | 可循环箭头与明确的 Raid 核心 | 日历图标 |

## 四级材料

| 等级 | 框架 | 能源色 | 动效 |
|---|---|---|---|
| Ignition | 枪灰喷砂钢 | 冷青 | 单次短扫光 |
| Overdrive | 钛银 + 深色 PVD | 青紫 | 双层扫光 |
| Apex | 黑铬 + 棱镜边 | 紫/品红 | 核心脉冲与边缘爆光 |
| Singularity | 镜银 + 白金镶边 | 白热金 | 分层揭晓、短粒子爆发 |

等级代表难度，类别由中心符号表达；不能仅通过颜色区分类别或状态。

## 状态

- Locked：保留可辨识框架，整体亮度约 35%，中心 glyph 不发光，显示锁定遮罩。
- InProgress：框架局部点亮；UI 外层绘制真实进度环，不能把进度烘焙进 PNG。
- Hidden：使用统一加密核心，不泄露 glyph、标题和达成条件。
- Unlocked：显示完整材质、获得日期和等级；卡片只在悬停/入场时播放一次扫光。

## 原生 UI 与动效

- Badge 页面分为“玩具 / 藏家 / 挑战 / Legacy”；默认展示当前玩具。
- 顶部只推荐一个最近可达目标，避免多个进度条竞争模型焦点。
- 两列图鉴卡保留标题、等级和进度；详情 Sheet 使用 160 pt Badge、条件、奖励、获得时间和分享按钮。
- Ignition/Overdrive 使用短通知；Apex/Singularity 等模型停稳后再显示 0.9–1.2 秒揭晓动画。
- Reduce Motion 下移除缩放、粒子和旋转，只保留 180 ms 淡入及静态高光。
- Reduce Transparency 下使用不透明深灰卡片；VoiceOver 必须读出标题、状态、当前值、目标值和奖励。

## 分享卡与贴花

- 分享卡固定 1080 × 1080、sRGB PNG；包含 Badge、玩具名、达成条件、日期和 Fidgeting 产品标识，不含用户身份。
- 四枚碎片奖励贴花使用 Badge 中心 glyph 的单色蚀刻版本，不复制完整金属框架。
- 贴花必须沿现有投影/激光蚀刻管线贴合模型表面，不新增悬浮几何或改变 Collider。
- 涉及贴花的 shipping Unity 预览必须覆盖 top、hero、左右斜视、low，并额外验证 pictogram、text mark 和 thin-line mark。

## 质量门禁

- 资产检查：1024 方形、sRGB、透明角、无伪字、无锯齿、文件名与目录 ID 一致。
- 小尺寸检查：46、64、96、160 pt 四档；46 pt 仍能区分类别和大致等级。
- 原生截图：图鉴、详情、Locked、InProgress、Hidden、Unlocked、挑战到期、分享卡。
- 未经用户对真实 native 预览和模型多角度预览明确批准，不构建或安装包含 Badge 视觉变化的 iPhone 包。
