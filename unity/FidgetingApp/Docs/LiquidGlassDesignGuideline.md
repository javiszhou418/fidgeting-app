# Fidget Spinner Liquid Glass Design Guideline

最后更新：2026-08-18

## 设计原则

- 原生组件源码权威为 `Assets/Plugins/iOS/FidgetProductUIComponents.swift`；业务状态和 `UnityBridge` 留在 `CodexSwiftUIOverlay.swift`，视觉组件不得直接调用 Unity 或原始 Haptic。
- 全 App 固定使用 Dark Mode，不跟随设备 Light Mode。iOS `UIUserInterfaceStyle`、UIKit Overlay 容器和 SwiftUI 根环境共同锁定为 dark；产品背景保持中性黑场，主要文字保持白色。禁止使用白色页面背景或会按 Light Mode 解析为浅底的未约束系统材质。不得改写 Unity 根 `Window` / `UIViewController` 的 appearance，以免干扰 Metal 渲染层。
- 全 App 的拉丁字母与数字统一使用 Oxanium 可变字体；`ProductTypography` 是 SwiftUI 语义字号与 UIKit navigation title 的唯一入口，业务页面不得直接使用 `.font(.system...)` 或系统西文字体。Oxanium 不含中文字形，中文由 Core Text 自动级联到 iOS 系统中文字体，避免缺字方框；这不是另一套可选视觉字体。
- 字间距始终使用 Oxanium 或中文级联字体的默认值。禁止用 SwiftUI `tracking` / `kerning` 或其他方式增加字间距；信息层级只通过字号、字重、颜色、透明度和组件间距表达。
- 图标、图标容器与相邻文字之间的留白是硬性约束，不允许例外：紧凑型纵向/横向控件的图标容器与 label 视觉间距不得小于 `4 pt`，常规控件使用 `8 pt`；容器内部的 glyph、倍率数字或状态标记与圆形/圆角边界也必须在上、下、左、右四边分别保留至少 `4 pt` 的视觉安全留白，不能用左右留白抵消顶部或底部的贴边。禁止使用负间距、负 offset 或压缩 frame 让文字贴住、侵入或覆盖图标。小屏、长文案或 Dynamic Type 空间不足时，必须扩大容器、重排、换行或等比缩放内容，不能牺牲这层间距；`44 × 44 pt` 最小点击热区独立计算，不能拿来充当可见间距。
- Metric 中的数字本身是视觉 headline，至少比 label / subhead 高一个语义字号层级；单位、标题和解释退到 `subheadline` / `caption`。优先用字号、字重、对比度和稳定宽度数字突出数值，不增加字间距，也不依赖永久 accent 填色。
- 实时速度只使用一个紧凑半圆 Hero 仪表：大号数字和连续扫掠场读取同一真实 telemetry。Intensity / Frequency 可使用左右从属翼表，但三表必须同排留出明确间距，任何圆弧和数值都不得重叠；翼表各自读取真实数据、继承主速度色带、降低线宽/亮度/字号且不使用 glow。Peak 只增强火红扫掠场和局部光晕，不绘制装饰火苗；主 RPM 与 3D Hero 始终保有视觉中心。
- Speed / Intensity / Frequency 三联仪表簇固定在底部成长卡上方 14 pt；安全区、成长卡 96 pt 高度与 12 pt 底部 inset 由 `ProductOverlayLayout` 统一提供。Combo 使用无票券边框、无胶囊容器的数字优先锁定组合固定在 3D 模型顶部；Spin Reward / Peak 反馈留在仪表上方，不能把实时指标向上顶回 3D Hero 中央区域。
- 模型顶部 Combo 的 Oxanium Heavy 等宽数字是唯一文字 Hero：2–4 / 5–9 / 10–19 / 20+ 分别使用 42 / 47 / 52 / 58 pt；`COMBO · 档位` 使用 17 pt bold 辅助解释。数字、`×`、COMBO 和档位文字全部使用中性白色，不读取模型或 Combo accent；层级只来自字号、字重、透明度、白色辉光与运动。普通增长只作用于数字字形、数字残影、数字内扫光和短火花，不允许通过胶囊缩放、票券描边、包围文字的常驻周圈光环或全屏震动制造奖励感。跨入默认 10、20、30…里程碑时，允许 `ComboCenterHalo` 从模型屏幕中心向四角扩散一次低透明中性白柔光；它不包围 Combo 文字、不常驻，并在 Reduce Motion 下退化为中心闪光。`ComboHaloTuningPanel` 必须复用同一生产组件，但入口只在 DEBUG/独立预览工具中出现，不进入 Release 设置页。Combo 激活后，真实机械累计每 120° 等效活动可产生一次展示 count，最多 6.25 次/秒；该 count 不发 XP，AUTO / Library 不计数。共享 `ProductStatusPill` 的其他调用不受影响。
- 仪表统一使用“headline 数字/单位在半圆内部、指标名称在半圆下方”的结构；Intensity / Speed / Frequency 名称保持左 / 中 / 右位置，使用 Oxanium `caption2` bold，并放在固定 20 pt 高、90% 黑色、无描边的独立胶囊中，使用纯白文字、最高布局优先级与高 z-index，不能再依赖背景对比或低透明度文字。数值不得覆盖弧线或刻度，不通过字间距制造层级。
- 3D 陀螺是主内容。原生 UI 只提供导航、选择和状态，不用插画或 SF Symbol 替代产品模型。
- 模型库的 Unity 实时模型舞台必须保持透明；只允许顶部与底部使用低透明度黑色渐变保证文字对比度。设置、藏家等纯原生页面可以使用完整 `ProductBackdrop`。任何全屏 SwiftUI Overlay 都不得以不透明黑层覆盖 Unity 模型舞台。
- 默认“随形微光”的颜色必须读成从屏幕上方入射的纵向光场：顶部较窄且保留受控色相／明度，向下逐渐展开，同时连续降低饱和度与明度，底部回到近黑。禁止在模型中部生成径向圆晕；Library 横滑只让旧／新产品色在水平方向交接，不改变从上向下的光源方向。
- 顶部不绘制横贯屏幕的导航底色；目的地入口使用独立的小尺寸 Liquid Glass 点击面，避免框住标题和 3D 主体。
- 选中状态优先使用白色。只有需要材质呼应时才从当前已装备皮肤读取低透明度 tint，不使用固定青色作为主界面强调色。
- 所有 `UIHostingController` 根视图必须应用 `productDesignSystem()`；共享组件默认使用中性白色，只有装备材质、语义指标或状态确有需要时才显式注入 accent。业务层禁止固定 `Color.cyan` 作为通用选中态。
- Liquid Glass 表面不使用周圈描边或 outline；深度来自系统材质模糊、低透明度 tint、柔和亮度渐变与外投影。选中状态通过玻璃 tint / 亮度、tag 和 checkmark 表达，不能再用高饱和色描边框住整张卡。
- Badge 解锁通知、图鉴、详情和分享卡必须渲染同一个 `ProductRarityBadge`，读取同一份 `ProductBadgeDetail`、正式 artwork、Token、短名和状态；不得用通用 SF Symbol、星标、奖杯、圆环印章或另一套“成就”图形替代 Badge。SF Symbol 只可作为 XP、碎片等辅助奖励语义，不得充当 Badge 本体。
- Library 选择陀螺页的身份层级固定拆成两套：顶部 `CollectorProfileAvatar` 只读取全局 Collector Rank，不得继承当前玩具等级或材质 accent；轮播标题区的 `ProductToyIdentityLockup` 把 Lv.1–100 单品等级环、玩具名与下移后的材质／皮肤名编成一组。当前 Toy Badge 入口只出现在 Library 轮播，不得放进详情模式栏；最多三枚正式 `ProductRarityBadge` 在模型下方直接横向排列，每枚保留图标下一行短名，禁止“单品成就”、已获得/总数或承载整组的大横卡。横排整体可点击进入同一 Badge 图鉴，不另建等级、门槛或奖励；当前使用 TabView 底部 `60 pt` inset，比上一版上移 `16 pt`，必须位于分页点上方并避开底部两个 CTA。
- iOS 26 使用 SwiftUI `glassEffect`。iOS 15–25 使用无周圈描边的 `ultraThinMaterial` fallback，保持同一结构与信息层级。内部 divider、进度轨道、仪表弧线/刻度以及图标自身的线条仍可作为信息几何使用，不能伪装成卡片边框。
- 交互控件使用 `interactive: true`；纯信息卡使用静态玻璃，避免无意义的触摸反馈。
- 产品级文字 CTA 永久只显示动作文字，不附加装饰性 SF Symbol；方向、确认、盒子等装饰图标不得与“进入模型”“查看收藏盒”“下一步/开始玩”等主操作文案并排。导航返回、设置等 icon-only 工具按钮，以及非 CTA 的真实状态/奖励语义不受此规则影响。
- 背景、材质和模型亮度会变化，主要文字保持白色，次要文字不低于 52% 白色不透明度。
- 任何跨两个以上业务界面重复的 heading、notice、tag、selection card、badge tile、metric、slider、toggle、empty state 必须进入 `FidgetProductUIComponents.swift`。业务层只组合组件、绑定状态并保留与 3D 模型直接相关的专用视觉，不能再次手写一套玻璃材质、tint、圆角和字号规则。
- 任何新增或修改的 shipping UI 都受组件库硬门禁约束，不以“只用一次”为由手写 Primary／Secondary、heading、tag、glass、card、spacing、typography、pressed motion 或 action state。缺少 primitive 时先补组件库和测试，再改业务 View。

## 媒体比例、色彩与交互诚实性

- 所有 raster 图片、视频画面和 3D 渲染截图必须始终保持源素材宽高比，绝不允许非等比拉伸、独立改变 X/Y 缩放或用变形填满容器。实现和预览必须能验证媒体内容使用统一等比缩放。
- `9:16`、`16:9` 等固定比例媒体容器必须由媒体本身按明确设计意图使用 `aspectFill` 或 `aspectFit`：`aspectFill` 只能做可预期的等比裁切，`aspectFit` 用于完整保留内容。禁止用“外层容器背景 + 内嵌媒体背景”叠层假装填满，也禁止意外留白、黑边或 letterbox。选择 `aspectFit` 产生的留白必须在设计说明中明确定义留白的颜色、用途和构图，不得将框架默认行为当作设计。
- Demo / prototype 默认使用中性、低彩度色彩基线；除非有明确的产品语义、品牌 token 或用户批准的视觉方向，不得随意增加大面积装饰色、多色环境染色或 AI 式高饱和渐变。最小主观验收为：去除语义 accent 后，信息层级仍然完整可读。
- rarity 色只允许用于徽标、细线、状态 tag、小面积辉光等局部语义载体，不得成为大面积页面背景或容器主色，也不得让多个稀有度颜色在同一页面同时主导视觉。页面主导色仍必须是中性黑、白、灰与低彩度材质色。
- 不可交互的分类、标签、占位动作或未开放商品必须表现为静态标题、静态信息卡或明确的“未开放”状态；禁止套用 Button 外观、主 CTA 轮廓、`interactive: true` 玻璃、chevron、按压反馈或“立即购买”等伪交互文案。只有实际绑定可达操作与完整状态生命周期的控件才能表现为可点击；产品级文字 CTA 继续遵守“只显示动作文字、不附加装饰 icon”的永久规则。

## Fanatics Live / Mobbin Button、Chip 与 Spacing 提案（待用户确认）

> **决策状态：`Current Request / Pending Approval`。** 本节是 2026-08-18 的待确认规范。用户已要求先把效果做成动画预览，因此 token、共享组件与抽卡 storefront 现有一套完全按本节实现的 shipping-source 候选；这只代表“可供真实预览”，不代表规范已获视觉批准。用户确认预览前不得把本节写成 `Approved`、`Locked` 或 `Installed`，也不得 Build／推送手机。

### 参考边界

- 用户口述中的 “Fantastic MCP” 经 Mobbin 页面标题与 App 名称核对，本轮按 **Fanatics Live iOS** 处理；“BitTorrent guideline”结合上下文按 **button guideline** 处理。若用户昨天的 Mobile 截图不是下列 `393 × 852` Fanatics Live 集合，应以用户重新指定的截图为准。
- 参考证据来自 [Fanatics Live iOS / UI Elements](https://mobbin.com/apps/fanatics-live-ios-34e5e6ff-a25d-4bef-9e7b-dc94e94f64ba/6a068836-0def-43a8-9a10-787dbd40e0f6/ui-elements)：Onboarding 的双 CTA、Home 的 `Watch live / Quick shop`、Product 的 `Buy now`、Checkout 的 `Slide to pay`，以及 Sort & Filter 的 chip。详细页面 ID、冲突和现状差距见 [FanaticsMobbinButtonGuidelineAudit.md](FanaticsMobbinButtonGuidelineAudit.md)。
- Fanatics 只提供层级、对齐、节奏和状态组织证据；以下 pt 数值是结合 Fidget 当前 token、iPhone 热区与 `393 × 852` 画面比例形成的产品建议，不宣称是 Fanatics 的内部 token，也不复制其品牌蓝色、商品视觉或 outline 风格。
- 参考不得覆盖已锁定的 Fidget 规则：Dark Mode、Oxanium、默认字距、文字 CTA 无装饰 icon、无默认周圈描边、rarity 色只作局部语义、真实 3D 产品优先，全部继续有效。

### Button 层级与几何

| 级别 | 用途 | 待确认规格 |
| --- | --- | --- |
| Primary Action | 当前决策区唯一的下一步，如“单抽”“进入模型”“保存” | 同一决策区最多一个实心主操作；`52 pt` 可见高度、`26 pt` 连续圆角；页面左右 inset `20 pt`，sheet 内 `16 pt`；默认使用高对比中性实心表面，深色页面上建议 `92–100%` 白色填充、`86–92%` 黑色文字；label 使用 Oxanium／中文级联 `17 pt semibold`，只写动词或“动词 + 直接对象”。 |
| Secondary Action | 可逆、替代或低一级操作，如取消、稍后、查看规则 | 与 Primary 对齐，可同宽，`48–52 pt` 高；使用中性 tonal / Liquid Glass 表面，不与 Primary 竞争。Fanatics 的 outline 仅作层级证据，不直接覆盖 `FDB-UI-004` 的默认无描边规则。 |
| Compact / Tertiary | 工具、筛选、局部操作 | 可见高度 `40–44 pt`，实际点击热区始终不小于 `44 × 44 pt`；优先文字或语义明确的原生 icon-only 工具按钮，不把它伪装成第二个 Primary。 |
| Unavailable / Coming Soon | 未开放能力或解释性占位 | 使用静态 label、tag 或信息卡；不得套用 Button role、按压态、chevron 或交互式玻璃。 |

- Button stack 的相邻间距固定为 `8 pt`；主操作与说明／价格／票券 metadata 间隔 `8–12 pt`。metadata 放在按钮外，不把价格、票数、稀有度或状态塞进两行 CTA label。
- 页面底部操作距 safe area `12–16 pt`；键盘、Home Indicator 与 sheet grabber 出现时以系统 safe area 为准，不通过负 offset 抢空间。
- Primary 和 Secondary 在同一行时，只有信息密度低且两者权重确实不同才允许；移动端默认纵向同宽排列。长文案优先换成更短动作，而不是压缩字体、减小热区或破坏左右 inset。

### Button 状态合同

| 状态 | 视觉与行为 |
| --- | --- |
| Rest | 保持稳定尺寸、对齐和 label；只有 Primary 使用最高表面对比度。 |
| Pressed | `scale 0.98`，`100–140 ms ease-out`；不改变布局，不加入高饱和 glow。选择切换和页面状态过渡仍使用现有 `180 ms` 节奏。 |
| Loading / Pending | 立即禁止重复提交，保留原 frame；显示原生进度反馈和可理解的等待文案。抽卡 pending 不重新 roll、不重复扣券。 |
| Disabled | 不可点击且从 VoiceOver 操作中正确暴露禁用状态；整体 opacity 建议 `0.36–0.44`，但不可用功能优先改成静态信息，不能长期伪装成灰色按钮。 |
| Success / Error | 只在动作确实完成／失败后进入；成功不提前替代权威回执，错误提供明确恢复路径，不用纯颜色表达。 |

### Filter Chip 与 Status Tag

| 类型 | 语义 | 待确认规格 |
| --- | --- | --- |
| Filter Chip | 可交互的筛选、排序或多选条件 | `32 pt` 可见高度、`16 pt` 连续圆角、水平 padding `12 pt`、相邻间距 `8 pt`；外层热区扩到至少 `44 pt`。选中态同时使用中性 fill／透明度变化和 checkmark／明确文字，不只靠颜色。 |
| Status Tag | 静态的 `NEW / OWNED / EQUIPPED / LIVE`、rarity 或数量状态 | `24–28 pt` 可见高度、水平 padding `8–10 pt`、相邻间距 `6–8 pt`；不得有 Button role、按压态、chevron 或 `interactive: true`。 |

- Fanatics 的蓝色 selected chip 不复制为全局选择色。Fidget 默认继续用白色层级；rarity、库存、错误等确有语义时才使用局部 accent，并同时提供图形或文字冗余。
- Chip 是操作，Tag 是信息。业务页面不得因为两者外形都接近 pill 就复用同一可访问性 role 或状态机。

### 4 pt Spacing Grid

| Token | 用途 |
| --- | --- |
| `4 pt` | glyph 内部安全留白、极紧凑关联 |
| `8 pt` | Button stack、Chip 间距、常规图标与文字 |
| `12 pt` | label 与 metadata、底部 safe-area 最小 inset |
| `16 pt` | sheet 内容 inset、常规组件内边距、目标 section 小间距 |
| `20 pt` | iPhone 页面左右主 inset |
| `24 pt` | section 之间的标准间隔 |
| `32 pt` | major group／页面大段落分隔 |

- 当前预览候选已把 `FidgetUITokens.Spacing.section` 从 `15` 统一迁移到 `16 pt`，并由同一 token 提供 `20 pt` page inset 与 `24 pt` section group；这仍是待视觉批准的 shipping-source 候选，不得把代码存在误写为设计已批准。对应结构测试与 Swift warnings-as-errors 编译已完成，不存在只改文档的漂移。
- 所有业务间距优先落在上述网格；`6 pt`、`10 pt` 只保留给小型 Tag／仪表等已有精细内部结构，不扩散成页面布局 token。

### 抽卡界面与 Pack／Rive 揭晓编排

1. 底部决策区只保留一个高对比 `单抽` Primary；按钮 label 单行，票券成本和剩余数量移到按钮外的 metadata。目标几何为 `52 pt` 高、`26 pt` 圆角、页面左右 `20 pt` inset、底部 safe area `12–16 pt`。
2. `十抽 / 后续开放` 改为静态说明或 Tag，不再呈现为长期 disabled 的第二个按钮。
3. `概率与保底`、筛选和收藏分类按 Compact／Filter Chip 处理；rarity、`NEW`、`OWNED` 等只用 Status Tag，不能互换角色。
4. 用户已确认保留当前抽卡页面的信息架构与命名；点击底部“单抽”后，揭晓顺序固定为：**Pack carousel → 选中 Pack 的 Rive 反馈 → 撕包 → 真实 Unity Collector Slab 从 Pack 内出现 → 单次高光 → 悬浮等待“收下”**。Magnetic holder 中转、盒体爆炸、只留奖品与重新装配均已被替代，不得恢复。
5. 上述顺序属于已确认的产品编排，但下列尺寸、遮挡、节奏与最终品牌处理仍须由真实 shipping-source 连续视频批准。预览批准前不得把视觉 DeliveryState 写成 `Visual Approved`／`Installed`，不得 Build 或推送手机。

#### 资产与语义边界

- 半圆 carousel 直接复用正式 `GachaPacks` 六档资产：`STANDARD / REFINED / SIGNATURE / CHASE / GRAIL / 1 OF 1`；每档均由 `384 × 512`、原始 `3:4` 比例的独立 `body + flap` PNG 组成。任何 carousel、放大或撕包阶段都只能等比 `fit`，不得把 Pack 拉伸成统一宽高。
- 六档 Pack 当前仍是展示层资产。用户选中某个 Pack 只选择本轮 presentation，不得在没有独立经济决策、价格和概率合同的情况下暗改 Unity 权威 rarity、概率、保底或奖品。所选 Pack 也不得由已经返回的隐藏 rarity 自动替换，以免提前泄露结果。
- Rive 只负责 Pack 选中反馈。`background/mint-slab` 可作为无品牌的 completion cue；`foreground/mint-slab`、`Slab-rotate-v01`、`Coin_Slab_v09-sm` 和 product-owned magnetic holder 不再是当前可见产品流。
- Pack 选中反馈必须留在选中 Pack 后方，不得提前显示收藏盒或奖品。撕包 commit 后由 Unity 权威 receipt 和真实 3D ready callback 接管，不使用固定延时冒充完成。
- 当前连续预览的权威奖品目标是 shipping `metal-three-blade`／“三叶金属”；Rive 不接收 receipt、prize、kind 或 rarity，最终产品必须来自真实 Unity 模型，不用 Rive 圆窗里的 2D 图替代。

#### `393 × 852 pt` 纵向布局基线

- 抽卡页面以 `0.92–0.96` 黑色遮罩退到背景，保留当前页面身份但禁用底层点击和可访问性。carousel 的极坐标中心为 `(196.5, 492 pt)`、半径 `232 pt`；当前项位于圆弧顶点，左右各显示两档，更多项目通过水平拖动进入。
- 选中 Pack 宽 `168 pt`、高 `224 pt`；相邻项为 `0.78× / 72%` opacity，外侧项为 `0.62× / 38%` opacity。选中项保持 `0°`，相邻与外侧最多分别沿圆弧倾斜 `±6° / ±10°`；可读文字不得因透视、模糊或遮挡失真。所有项共享同一 `z` 规则：选中项最高，相邻项其次，外侧项最低。
- 窄于 `393 pt` 时保持 `20 pt` 页面 inset，carousel 半径缩为 `min(232 pt, availableWidth × 0.59)`，选中 Pack 最小宽 `152 pt`；不得为塞入六包而破坏比例。横向 VoiceOver 顺序始终跟随 `STANDARD → 1 OF 1` 的稳定目录顺序，每一项热区至少 `44 × 44 pt`。
- Pack 确认后，选中项从 carousel 顶点等比放大到现有撕包舞台的 `244 × 326 pt`，其余 Pack 向圆弧下方淡出。标题、说明与主 CTA 保持当前命名；画面内不得同时堆叠“单抽揭晓”“COLLECTION DROP”“正在开启收藏”三套同级标题。

#### 层级与遮挡

| 阶段 | 从后到前的固定层级 |
| --- | --- |
| Pack 选择 | 黑色页面遮罩 → 非选中 Pack → `background/mint-slab` 中性 selection feedback → 选中 Pack → 标题／操作说明 |
| 撕包／等待 | 黑底 → 已准备但不可见的 Unity 盒 → selected Pack body → 可拖动 flap → 手势说明／状态文案 |
| 真盒出场 | 真实 Unity 环境 → assembled Premium Display Case → Pack body 前景下退 → 原生状态文案 |
| 产品揭晓 | 黑底／真实 Unity 环境 → Premium Display Case → 真实三叶金属 → 原生结果 metadata／唯一“收下”Primary |

- 撕包 commit 后，Pack body 必须保持前景，直到同 request 的 Unity receipt、真实盒、奖品和相机连续两帧 ready。随后 Pack 在 `0.28 s` 内下退，assembled 真盒从其后方出现；不得先清 gate、先 dismiss、插入纯黑空帧或用另一个 holder 替换对象。
- 真实盒从首个可见帧到“收下”保持同一实例。完成入场后只播放一次窄高光，再由 case root 做低频轻悬浮；奖品不得 idle 自转。

#### 动画时序与门控

| 节点 | 目标节奏 | 完成条件 |
| --- | --- | --- |
| 页面 → carousel | `180 ms ease-out` | 底层操作与可访问性已隔离 |
| carousel settle | `220 ms`，可中断 | Pack 中心索引稳定；未确认时不扣券 |
| 选中反馈 | `520–620 ms` | selection Rive cue 完成；不得显示完整 holder |
| 选中 Pack 进入撕包舞台 | `320 ms ease-in-out` | `244 × 326 pt` 舞台位置稳定 |
| 撕包拖动 | 用户驱动；`220 pt` 完整行程、`0.62` commit | 阈值下 `180 ms` 回弹；阈值上 exact-once commit |
| Unity 盒准备 | 无可见固定时长 | receipt 匹配；盒、奖品、相机连续两个 end-of-frame 稳定 |
| Pack → 真盒 | `280 ms ease-out` | 真盒 ready 后才下退 Pack；全程至少一个真实对象可见 |
| 高光 | 单次窄 sweep，目标 `500–800 ms` | 不改变盒体层级或奖品物理 |
| 悬浮／确认 | 低频轻位移，持续到用户操作 | 唯一“收下”Primary 可用；Reduce Motion 为静态终态 |

- “单抽”只负责进入 Pack 选择；用户确认 Pack 后才允许 exact-once 发起 Unity 权威 draw，避免未选中或关闭 carousel 已扣券。若既有交易恢复要求必须更早创建 pending transaction，则关闭／后台恢复必须回到同一 request ID 与同一 Pack 选择，不得重抽。
- 进入真实产品揭晓的硬门为 `packSelected && tearCommitted && authoritativeReceiptArrived && unityCaseStableForTwoFrames`。receipt 提前到达只缓冲；receipt 较慢时保持已撕开的同一 Pack，不重复请求、不播放假奖品。
- Reduce Motion 保留相同因果顺序：carousel 使用无旋转水平选择，选中反馈缩为 `120 ms` 淡化，真盒 ready 后 Pack 短淡出并直接显示 assembled 静态终态；不得跳过 receipt 或 Unity ready gate。

#### 品牌与预览门禁

- 历史 WHATNOT／product-owned holder 均不得重新进入可见流程。评级、编号、名称、日期和 rarity 只从真实 Collector Slab 的权威实体标签读取。
- 最终连续预览至少覆盖：六档 Pack、选中反馈、`<0.62` 回弹、`≥0.62` commit、receipt 延迟、Unity 两帧 ready、Pack／真盒交叠、单次高光、悬浮、唯一“收下”与 exact-once ACK。截图拼接、独立 mockup 或只到 handoff 占位屏均不能替代连续 shipping 证据。

## 组件清单

| 组件 | SwiftUI 实现 | 规格 |
| --- | --- | --- |
| 设计 token | `FidgetUITokens` | 44 pt 最小热区、38 pt 紧凑图标、52 pt 主操作、32 pt Filter Chip、26 pt Status Tag、16/22/26 pt 圆角、4/8/12/16/20/24/32 pt 间距；图标容器与文字紧凑态至少 4 pt、常规态 8 pt，容器内部图形与边界至少 4 pt；120 ms pressed 与 180 ms 选择动效 |
| 全局字体 | `ProductTypography` / `Font.product` / `Font.combo` / `productDesignSystem` | Oxanium 200–800 可变字重；语义字号支持 Dynamic Type；拉丁与数字使用 Oxanium，中文自动系统级联；保持默认字距 |
| 玻璃与背景 | `ProductBackdrop` / `ProductGlassModifier` / `productGlass` | plist、UIKit Overlay、SwiftUI 三层固定 Dark Mode；设置/藏家使用中性黑场，模型库中央保持透明以显示 Unity；iOS 26 原生 glass，旧系统使用深色环境下无周圈描边的 `ultraThinMaterial` |
| 藏家 Profile | `CollectorProfileAvatar` + `ProductTopBar` | 左上固定显示全局 Collector Rank 1–30 与全局进度；不随当前玩具等级、皮肤或 accent 改变，点击进入藏家档案 |
| 单品身份 | `ProductToyIdentityLockup` + `ProductProgressionTopAvatar` | Library 轮播标题区把单品 Lv.1–100 圆环与玩具名称组成同一身份组；材质／皮肤名下移 4 pt，单品成长值飞行只锚定这枚等级环 |
| 紧凑图标按钮 | `ProductIconButton` | 顶部复位、说明、玩具库与设置共用；视觉直径 38 pt，布局热区不小于 44 pt；出现文字 label 时与图标容器至少间隔 4 pt，内部 glyph 不得贴边 |
| 模型选择器 | `SpinnerLibrary` | 分页 `TabView`；直接显示 Unity 实时模型；选择页使用 45° Hero 机位 |
| Page control | `ProductPageIndicator` | 每个模型一个点；当前页 18×6 pt，其他页 6×6 pt；同一 items 集合生成视觉与 VoiceOver 计数 |
| 主操作 | `ProductPrimaryActionLabel` / `ProductPrimaryActionButton` | 52 pt 高、26 pt 圆角、中性白高对比实心表面；永久只显示动作文字、不接受装饰 icon；具备 rest / pressed / loading / disabled / success / error 状态，disabled 可携带可理解原因并进入 VoiceOver value，进入后才开放模型手势 |
| Library 单品勋章入口 | `LibraryToyBadgeRow` + `ProductRarityBadge` | 只在选择陀螺轮播的模型下方、分页点上方直接横排最多 3 枚正式 Badge 与各自下方短名；无标题、无数量、无大卡，点击直达同一 Badge 图鉴的玩具页 |
| 模式切换 | `ProductIconSegmentedControl` + `ProductModeBar` | 详情页仅保留两枚 44 × 40 pt 纯图标；连续旋转 / 机械齿轮语义；玻璃宽度严格随内容，选中只用低透明白色；不得混入 Library Badge 入口 |
| 底部成长 | `SpinnerProgressionHUD` | 底部产品导航已移除；成长卡贴合 safe area，材质 tint 跟随当前皮肤 |
| 设置卡 | `ProductSectionCard` | 22 pt 圆角静态玻璃；系统 Slider、Toggle、Picker 保留原生可访问性行为 |
| 页面标题 | `ProductScreenHeading` | 标题 / 副标题 / 可选 SF Symbol 共用同一字号、透明度与 VoiceOver 合并规则；可选择左对齐或居中 |
| 通知与状态 | `ProductBadgeUnlockBanner` / `ProductNoticeBanner` / `ProductInlineTag` | Badge 解锁必须复用正式 `ProductRarityBadge`；普通通知才使用 SF Symbol。两者共用 22 pt 玻璃表面与 Reduce Transparency 分支；EQUIPPED / CURRENT / LIVE 共用紧凑 tag |
| 选择与 Badge | `ProductSelectionCard` / `ProductBadgeTile` / `ProductRarityBadge` | 图鉴、详情、解锁和分享只保留一套 Badge 本体；皮肤行、等级行与状态卡统一使用玻璃 tint / 亮度、tag / checkmark 表达状态，并统一禁用透明度、圆角和可访问性状态；无卡片周圈描边 |
| 设置输入 | `ProductSliderRow` / `ProductToggleRow` | 所有产品级滑杆与开关统一 label、稳定宽度数值、accent 和原生可访问性控件 |
| 辅助状态 | `ProductCompactMetric` / `ProductEmptyState` | 触觉实验室实时值与未开放内容使用同一紧凑指标和空状态层级 |
| 次级操作 | `ProductActionLabel` / `ProductSecondaryActionButton` | 52 pt 高、16 pt 圆角、中性 tonal／交互式玻璃；文字 CTA 不显示装饰 icon。完整 Button wrapper 与 Primary 共用 `0.98 / 120 ms` pressed、loading 禁重入、disabled reason、success 禁用和 error 可重试合同；`ProductActionLabel` 只保留给 `Menu` 等需要自带容器的 label 场景 |
| 指标卡 | `ProductMetricCard` | 数值使用 `title3` 稳定宽度粗体作为视觉 headline，标题退到 `caption`；业务层只为 SF Symbol 注入语义 accent |
| Bottom sheet | `ProductBottomSheetShell` | 统一标题、关闭操作、中性背景与深色导航容器；业务内容通过 builder 注入 |
| 筛选 Chip | `ProductFilterChip` | 32 pt 可见 pill、至少 44 pt 热区；选中态同时使用 checkmark 与中性表面变化 |
| 状态 Tag | `ProductStatusTag` / `ProductStatusPill` | 26 pt 静态信息 pill，无 Button role、pressed 或 interactive glass；兼容旧 `ProductStatusPill` 调用但不得把 Tag 包装成伪操作 |
| 进度 | `ProductProgressGauge` | 5 pt 线性轨道、0...1 显示夹取、180 ms ease-out 和组合 VoiceOver 数值 |
| 里程碑进度 | `ProductMilestoneProgressGauge` | 复用 `ProductProgressGauge`；两端等级统一使用 `caption2` bold（默认 11 pt）Oxanium 等宽数字，最小行高 16 pt，禁止业务页面回退到 7–9 pt 微型字号 |
| 成长结算与升级 | `ProgressionRewardCelebrationView` / `ProgressionPageRewardFlightView` | 底部透明 overlay 保留 Unity 与详情界面上下文并覆盖底部操作区；sheet 内头像环读取权威单品等级进度但不承载粒子；sheet 完整移除后，页面级 `+XP` 飞向顶部单品身份组的真实等级环锚点并更新该环；不得飞向左上藏家 Profile；Reduce Motion 只更新/高亮单品等级环 |
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
- 离线成长与实时升级统一使用透明原生 overlay 承载 `ProgressionRewardCelebrationView`，保留结算发生前的 Unity 与 SwiftUI 详情界面作为可见上下文，不再使用不透明 `fullScreenCover` 或文本 Alert。离线结算是从底部弹起的 sheet，并在显示期间覆盖且屏蔽模型库底部“查看收藏盒”和“进入模型”操作区；自动关闭后必须恢复底层交互。离线结算同时显示格式化离线时长、实际成长值、每小时平均成长速度和来源状态；sheet 内当前用户以 `person.crop.circle` 头像表达，头像外圆弧读取 Unity 本次 reward snapshot 的旧/新单品等级内进度。数字从 0 动画到真实值，但 SwiftUI 不得重算或再次发放 XP。只有 `newLevel > previousLevel` 才显示 LEVEL UP 高光、真实等级跃迁和跨级数量；未升级时使用当前头像、所属等级与环形进度。离线结算不提供领取 CTA，sheet 内永久不执行 XP 粒子回收；顺序固定为“结算层关闭 → 页面级 +XP 飞行 → 单品身份等级环更新”。只有确认 UIKit 已移除 sheet controller 且底层 Library 恢复后，`ProgressionPageRewardFlightView` 才能启动。飞行终点必须来自共享 `ProductTopBar` 中 `ProductProgressionTopAvatar` 的真实 window frame anchor，不得按设备尺寸硬编码坐标，也不得使用左上全局 `CollectorProfileAvatar`。飞行到达后才提交该 reward 的新等级/新 fraction 并脉冲单品等级环。Reduce Motion 跳过粒子飞行，sheet 关闭后只更新并短暂高亮单品等级环。高光以中性白、石墨和当前模型低饱和 accent 为限，不使用周圈描边卡、彩虹粒子或伪 Badge。

## 可访问性与适配

- 可点击区域不小于 44×44 pt。
- Page control 合并为一个可访问性元素，朗读“第 N 个，共 M 个陀螺”。
- SF Symbols 仅用于导航和模式语义，不用于替代模型缩略图。
- 所有玻璃组件必须在深色模型、浅色高光和 Reduce Transparency 环境下检查文字对比度。
- iPhone 真机仍需确认安全区、滑页场景切换、Liquid Glass 对比度和 Taptic Engine 手感。
