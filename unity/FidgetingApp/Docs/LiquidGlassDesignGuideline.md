# Fidget Spinner Liquid Glass Design Guideline

最后更新：2026-08-08

## 设计原则

- 原生组件源码权威为 `Assets/Plugins/iOS/FidgetProductUIComponents.swift`；业务状态和 `UnityBridge` 留在 `CodexSwiftUIOverlay.swift`，视觉组件不得直接调用 Unity 或原始 Haptic。
- 全 App 固定使用 Dark Mode，不跟随设备 Light Mode。iOS `UIUserInterfaceStyle`、UIKit Overlay 容器和 SwiftUI 根环境共同锁定为 dark；产品背景保持中性黑场，主要文字保持白色。禁止使用白色页面背景或会按 Light Mode 解析为浅底的未约束系统材质。不得改写 Unity 根 `Window` / `UIViewController` 的 appearance，以免干扰 Metal 渲染层。
- 全 App 的拉丁字母与数字统一使用 Oxanium 可变字体；`ProductTypography` 是 SwiftUI 语义字号与 UIKit navigation title 的唯一入口，业务页面不得直接使用 `.font(.system...)` 或系统西文字体。Oxanium 不含中文字形，中文由 Core Text 自动级联到 iOS 系统中文字体，避免缺字方框；这不是另一套可选视觉字体。
- 字间距始终使用 Oxanium 或中文级联字体的默认值。禁止用 SwiftUI `tracking` / `kerning` 或其他方式增加字间距；信息层级只通过字号、字重、颜色、透明度和组件间距表达。
- 图标、图标容器与相邻文字之间的留白是硬性约束，不允许例外：紧凑型纵向/横向控件的图标容器与 label 视觉间距不得小于 `4 pt`，常规控件使用 `8 pt`；容器内部的 glyph、倍率数字或状态标记与圆形/圆角边界也必须保留至少 `4 pt` 的视觉安全留白。禁止使用负间距、负 offset 或压缩 frame 让文字贴住、侵入或覆盖图标。小屏、长文案或 Dynamic Type 空间不足时，必须扩大容器、重排、换行或等比缩放内容，不能牺牲这层间距；`44 × 44 pt` 最小点击热区独立计算，不能拿来充当可见间距。
- Metric 中的数字本身是视觉 headline，至少比 label / subhead 高一个语义字号层级；单位、标题和解释退到 `subheadline` / `caption`。优先用字号、字重、对比度和稳定宽度数字突出数值，不增加字间距，也不依赖永久 accent 填色。
- 实时速度只使用一个紧凑半圆 Hero 仪表：大号数字和连续扫掠场读取同一真实 telemetry。Intensity / Frequency 可使用左右从属翼表，但三表必须同排留出明确间距，任何圆弧和数值都不得重叠；翼表各自读取真实数据、继承主速度色带、降低线宽/亮度/字号且不使用 glow。Peak 只增强火红扫掠场和局部光晕，不绘制装饰火苗；主 RPM 与 3D Hero 始终保有视觉中心。
- Speed / Intensity / Frequency 三联仪表簇固定在底部成长卡上方 14 pt；安全区、成长卡 96 pt 高度与 12 pt 底部 inset 由 `ProductOverlayLayout` 统一提供。Combo 使用无票券边框、无胶囊容器的数字优先锁定组合固定在 3D 模型顶部；Spin Reward / Peak 反馈留在仪表上方，不能把实时指标向上顶回 3D Hero 中央区域。
- 模型顶部 Combo 的 Oxanium Heavy 等宽数字是唯一文字 Hero：2–4 / 5–9 / 10–19 / 20+ 分别使用 42 / 47 / 52 / 58 pt；`COMBO · 档位` 使用 17 pt bold 辅助解释。数字、`×`、COMBO 和档位文字全部使用中性白色，不读取模型或 Combo accent；层级只来自字号、字重、透明度、白色辉光与运动。普通增长只作用于数字字形、数字残影、数字内扫光和短火花，不允许通过胶囊缩放、票券描边、包围文字的常驻周圈光环或全屏震动制造奖励感。跨入默认 10、20、30…里程碑时，允许 `ComboCenterHalo` 从模型屏幕中心向四角扩散一次低透明中性白柔光；它不包围 Combo 文字、不常驻，并在 Reduce Motion 下退化为中心闪光。`ComboHaloTuningPanel` 必须复用同一生产组件，但入口只在 DEBUG/独立预览工具中出现，不进入 Release 设置页。Combo 激活后，真实机械累计每 120° 等效活动可产生一次展示 count，最多 6.25 次/秒；该 count 不发 XP，AUTO / Library 不计数。共享 `ProductStatusPill` 的其他调用不受影响。
- 仪表统一使用“headline 数字/单位在半圆内部、指标名称在半圆下方”的结构；Intensity / Speed / Frequency 名称保持左 / 中 / 右位置，使用 Oxanium `caption2` bold，并放在固定 20 pt 高、90% 黑色、无描边的独立胶囊中，使用纯白文字、最高布局优先级与高 z-index，不能再依赖背景对比或低透明度文字。数值不得覆盖弧线或刻度，不通过字间距制造层级。
- 3D 陀螺是主内容。原生 UI 只提供导航、选择和状态，不用插画或 SF Symbol 替代产品模型。
- 模型库的 Unity 实时模型舞台必须保持透明；只允许顶部与底部使用低透明度黑色渐变保证文字对比度。设置、藏家等纯原生页面可以使用完整 `ProductBackdrop`。任何全屏 SwiftUI Overlay 都不得以不透明黑层覆盖 Unity 模型舞台。
- 顶部不绘制横贯屏幕的导航底色；目的地入口使用独立的小尺寸 Liquid Glass 点击面，避免框住标题和 3D 主体。
- 选中状态优先使用白色。只有需要材质呼应时才从当前已装备皮肤读取低透明度 tint，不使用固定青色作为主界面强调色。
- 所有 `UIHostingController` 根视图必须应用 `productDesignSystem()`；共享组件默认使用中性白色，只有装备材质、语义指标或状态确有需要时才显式注入 accent。业务层禁止固定 `Color.cyan` 作为通用选中态。
- Liquid Glass 表面不使用周圈描边或 outline；深度来自系统材质模糊、低透明度 tint、柔和亮度渐变与外投影。选中状态通过玻璃 tint / 亮度、tag 和 checkmark 表达，不能再用高饱和色描边框住整张卡。
- Badge / 成就解锁通知固定使用实心 SF Symbol 与实心完成标记；不使用空心星标、圆环印章或其他描边式徽章图形。
- iOS 26 使用 SwiftUI `glassEffect`。iOS 15–25 使用无周圈描边的 `ultraThinMaterial` fallback，保持同一结构与信息层级。内部 divider、进度轨道、仪表弧线/刻度以及图标自身的线条仍可作为信息几何使用，不能伪装成卡片边框。
- 交互控件使用 `interactive: true`；纯信息卡使用静态玻璃，避免无意义的触摸反馈。
- 背景、材质和模型亮度会变化，主要文字保持白色，次要文字不低于 52% 白色不透明度。
- 任何跨两个以上业务界面重复的 heading、notice、tag、selection card、badge tile、metric、slider、toggle、empty state 必须进入 `FidgetProductUIComponents.swift`。业务层只组合组件、绑定状态并保留与 3D 模型直接相关的专用视觉，不能再次手写一套玻璃材质、tint、圆角和字号规则。

## 组件清单

| 组件 | SwiftUI 实现 | 规格 |
| --- | --- | --- |
| 设计 token | `FidgetUITokens` | 44 pt 最小热区、38 pt 紧凑图标、52 pt 主操作、16/22/26 pt 圆角、4/8/15 pt 间距；图标容器与文字紧凑态至少 4 pt、常规态 8 pt，容器内部图形与边界至少 4 pt；180 ms 选择动效 |
| 全局字体 | `ProductTypography` / `Font.product` / `Font.combo` / `productDesignSystem` | Oxanium 200–800 可变字重；语义字号支持 Dynamic Type；拉丁与数字使用 Oxanium，中文自动系统级联；保持默认字距 |
| 玻璃与背景 | `ProductBackdrop` / `ProductGlassModifier` / `productGlass` | plist、UIKit Overlay、SwiftUI 三层固定 Dark Mode；设置/藏家使用中性黑场，模型库中央保持透明以显示 Unity；iOS 26 原生 glass，旧系统使用深色环境下无周圈描边的 `ultraThinMaterial` |
| 顶部身份 | `ProductTopBar` | 无整栏背景；活动玩具按“当前等级 / 名称 / 当前皮肤”三行排列，皮肤文字使用对应装备色 |
| 紧凑图标按钮 | `ProductIconButton` | 顶部复位、说明、玩具库与设置共用；视觉直径 38 pt，布局热区不小于 44 pt；出现文字 label 时与图标容器至少间隔 4 pt，内部 glyph 不得贴边 |
| 模型选择器 | `SpinnerLibrary` | 分页 `TabView`；直接显示 Unity 实时模型；选择页使用 45° Hero 机位 |
| Page control | `ProductPageIndicator` | 每个模型一个点；当前页 18×6 pt，其他页 6×6 pt；同一 items 集合生成视觉与 VoiceOver 计数 |
| 主操作 | `ProductPrimaryActionLabel` | 52 pt 高、26 pt 圆角、材质色轻 tint；进入后才开放模型手势 |
| 模式切换 | `ProductIconSegmentedControl` + `ProductModeBar` | 两枚 44 × 40 pt 纯图标；连续旋转 / 机械齿轮语义；玻璃宽度严格随内容，选中只用低透明白色 |
| 底部成长 | `SpinnerProgressionHUD` | 底部产品导航已移除；成长卡贴合 safe area，材质 tint 跟随当前皮肤 |
| 设置卡 | `ProductSectionCard` | 22 pt 圆角静态玻璃；系统 Slider、Toggle、Picker 保留原生可访问性行为 |
| 页面标题 | `ProductScreenHeading` | 标题 / 副标题 / 可选 SF Symbol 共用同一字号、透明度与 VoiceOver 合并规则；可选择左对齐或居中 |
| 通知与状态 | `ProductNoticeBanner` / `ProductInlineTag` | Badge 与藏家通知共用 48 pt 无描边玻璃图标、实心 symbol、实心完成标记、22 pt 表面和 Reduce Transparency 分支；EQUIPPED / CURRENT / LIVE 共用紧凑 tag |
| 选择与 Badge | `ProductSelectionCard` / `ProductBadgeTile` | 皮肤行、等级行、Badge 卡统一使用玻璃 tint / 亮度、tag / checkmark 表达选中态，并统一禁用透明度、圆角和可访问性状态；无卡片周圈描边 |
| 设置输入 | `ProductSliderRow` / `ProductToggleRow` | 所有产品级滑杆与开关统一 label、稳定宽度数值、accent 和原生可访问性控件 |
| 辅助状态 | `ProductCompactMetric` / `ProductEmptyState` | 触觉实验室实时值与未开放内容使用同一紧凑指标和空状态层级 |
| 次级操作 | `ProductActionLabel` | 44 pt 高、16 pt 圆角、交互式玻璃 |
| 指标卡 | `ProductMetricCard` | 数值使用 `title3` 稳定宽度粗体作为视觉 headline，标题退到 `caption`；业务层只为 SF Symbol 注入语义 accent |
| Bottom sheet | `ProductBottomSheetShell` | 统一标题、关闭操作、中性背景与深色导航容器；业务内容通过 builder 注入 |
| 状态 Chip | `ProductStatusPill` | 24–28 pt 可见 pill；若包装为按钮，外层热区仍须扩到 44 pt |
| 进度 | `ProductProgressGauge` | 5 pt 线性轨道、0...1 显示夹取、180 ms ease-out 和组合 VoiceOver 数值 |
| 实时速度 | `ProductSpeedDashboard` | 124–160 × 118 pt，68–84 pt 的 180° 半圆内显示 25 pt 起始等宽 RPM headline/单位和 13 根刻度，Speed / 状态名称使用独立高对比胶囊固定在半圆下方；20 Hz telemetry、100 ms 无超调跟随、4% 色带回差；Peak 只保留火红扫掠场/光晕；磁吸推牌不显示 RPM |
| 从属实时指标 | `ProductSideMetricDashboard` | 64–74 × 78 pt，48–54 pt 半圆内显示 17 pt 起始数值/单位，Intensity / Frequency 名称使用独立高对比胶囊固定在半圆下方；7 根刻度；与主表同排保持 10 pt 间距，各自读取真实 Combo 数据，只继承主表色带并降低视觉权重 |

## 字体资产与构建

- 字体资产固定为 `Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf`，许可证保存在同目录 `OFL.txt`；来源为 Google Fonts 官方 `ofl/oxanium` 目录。
- iOS 构建必须把字体复制进主 target 的 Resources，并通过 `UIAppFonts` 注册；运行时以 Core Text 做缺失注册兜底，不能依赖网络字体。
- 发布场景不得包含 legacy `MobileCanvas`、`EventSystem` 或 `UnityEngine.UI.Text` HUD；所有可见业务 UI 由原生产品壳统一负责。

## 交互与动效

- 模型选择只使用水平分页手势；页面落定后加载对应 Unity 场景，页码点和名称同步更新。
- “进入”是从选择态到操作态的明确边界。选择态拦截模型手势；进入后移除面板并显示模式切换栏。
- 详情页模型长按由 Unity 命中测试确认后，先做一次 `0.22 s` 相机 framing 轻弹并同步路由语义 `Pop` 触感，回到 `1.000×` 静止态后才打开原生 `ProductAppearanceEditor`；轻弹不得缩放模型 Transform 或改变碰撞体、质量、角速度。编辑态隐藏底部成长卡、三联仪表和机制栏，关闭后恢复。面板必须复用 `ProductSheetDragHandle`、`ProductScreenHeading`、`ProductIconButton`、`ProductIconSegmentedControl`、`ProductStatusPill`、`ProductSelectionCard` 与 `ProductEmptyState`，业务层只组合两列 `LazyVGrid` 和模型专属预览，不另造圆角、玻璃、字体或选中态。贴纸卡片必须以 `scaledToFit` 显示 `Assets/Resources/ProductStickers/BackdropWhite` 的真实透明 PNG，完整保留图形和安全边距；SF Symbol 仅用于资源缺失兜底。
- 模式 Tab 切换使用系统 UI impact 作为选择确认；玩具触感仍必须经过 `input → mechanism → semantic event → recipe → iOS renderer`。
- 状态动画使用 180–200 ms ease-out。不要给真实模型添加自动旋转来暗示可交互性。

## 可访问性与适配

- 可点击区域不小于 44×44 pt。
- Page control 合并为一个可访问性元素，朗读“第 N 个，共 M 个陀螺”。
- SF Symbols 仅用于导航和模式语义，不用于替代模型缩略图。
- 所有玻璃组件必须在深色模型、浅色高光和 Reduce Transparency 环境下检查文字对比度。
- iPhone 真机仍需确认安全区、滑页场景切换、Liquid Glass 对比度和 Taptic Engine 手感。
