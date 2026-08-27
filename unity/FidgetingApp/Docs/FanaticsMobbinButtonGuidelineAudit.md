# Fanatics Live / Mobbin Button、Chip 与 Spacing 审计

最后核对：2026-08-18

状态：设计规范提案证据；等待用户确认。本文不代表 runtime 已修改、视觉已批准、Build 已生成或 iPhone 已验收。

## 1. 名称与范围定位

- 用户口述中的 “Fantastic” 经现有 Mobbin 页面与页面标题交叉核对，实际对象是 **Fanatics Live — Buy & collect sports cards**，不是 Fantastical Calendar。
- 用户同一句话讨论“主按钮、标签、间距”，仓库与 Downloads 均没有 BitTorrent 产品或 BitTorrent guideline；因此 “BitTorrent guideline” 最合理的解释是语音转写后的 **button guideline**。本文只整理 Button / Chip / Tag / Spacing，不引入下载协议或 BitTorrent 产品语义。
- 当前仓库对应权威入口是 [LiquidGlassDesignGuideline.md](LiquidGlassDesignGuideline.md)，实现入口是 `Assets/Plugins/iOS/FidgetProductUIComponents.swift`。为避免与正在进行的 guideline 合并任务冲突，本文只提供可合并审计，不直接修改上述文件、抽卡 UI 或 Design Bible。
- Downloads 中没有 2026-08-17 的 Fanatics Mobile 图片文件；本轮通过用户现有 Mobbin 登录态重新核对同一 Fanatics Live iOS 集合。若用户昨天给出的截图不是下面这套 `393 × 852` 集合，应以用户重新指定的截图为最终视觉证据。

## 2. Mobbin 证据

集合：

- [Fanatics Live iOS / UI Elements](https://mobbin.com/apps/fanatics-live-ios-34e5e6ff-a25d-4bef-9e7b-dc94e94f64ba/6a068836-0def-43a8-9a10-787dbd40e0f6/ui-elements)
- 核对时 Mobbin 显示 `221 UI elements`；Button 筛选为 `5 UI elements`，Chip 筛选为 `1 UI element`。
- 所有代表屏均标注 `iOS (393x852)`。

| Mobbin screen | 可验证观察 | 对 Fidgeting App 的可迁移原则 |
| --- | --- | --- |
| [868f12c0-e11a-4bc3-9017-5ad456512a20](https://mobbin.com/screens/868f12c0-e11a-4bc3-9017-5ad456512a20) | Onboarding 底部一组等宽 pill：高对比实心主操作 `Create Fanatics ID`，其下为 outline 次操作 `Log in`。 | 同一决策区只保留一个实心主操作；次操作降一级但保持同宽、同对齐与稳定间距。 |
| [09cb884b-e129-4565-8b97-e3d5d61749c6](https://mobbin.com/screens/09cb884b-e129-4565-8b97-e3d5d61749c6) | Home 顶部为可横向浏览的分类 chips；Hero 底部并列 `Watch live` 实心按钮和 `Quick shop` 次级按钮。 | 主／次层级由填充、文字对比和位置表达；不要让两个相邻操作都成为同权重主 CTA。 |
| [e88ef2dd-8bac-4dd0-9223-a767fc32a12a](https://mobbin.com/screens/e88ef2dd-8bac-4dd0-9223-a767fc32a12a) | Checkout 底部固定 `Slide to pay`，使用手势确认而不是普通点击。 | 高风险动作可以升级确认机制；普通“单抽”不应模仿支付滑动手势。 |
| [5e619e18-9190-49ca-8e6f-e35f09c7e4d5](https://mobbin.com/screens/5e619e18-9190-49ca-8e6f-e35f09c7e4d5) | 商品页使用单一高对比、满宽 `Buy now`；下面两个 outline 信息操作明显降级。 | 购买／抽取主操作贴近价格或消耗信息，但按钮本体保持单行动词，不塞入第二行解释。 |
| [a5bdb78d-ce91-4563-afff-d11410cd1fc7](https://mobbin.com/screens/a5bdb78d-ce91-4563-afff-d11410cd1fc7) | 收藏活动页以藏品为 Hero；状态 `UNCLAIMED` 是紧凑标签，不伪装成满宽按钮。 | 状态 label 与可点击 CTA 必须在形态、热区、动效和无障碍 trait 上分离。 |
| [d58baf4a-3df7-48b3-9942-564bd457236b](https://mobbin.com/screens/d58baf4a-3df7-48b3-9942-564bd457236b) | Sort & Filter 中，未选 chip 为中性暗填充；已选 `Under $100` 为蓝色实心并带 `×`；底部单一 `Show 208 results` 应用操作。 | Chip 只改变局部筛选状态；完成／应用由独立主 CTA 承担。已选态必须同时具备颜色以外的标记。 |

上述页面支持结构和层级判断。下面的 pt 数值是结合 `393 × 852` 画面比例、iPhone 可达性和当前 Fidget token 得出的**产品建议值**，不是对 Fanatics 内部设计 token 的反向声明。

## 3. 建议合并的 Button guideline

### 3.1 层级

1. 每个可见决策区最多一个 Primary Action。抽卡页的主要决策是“单抽”；概率、公示、规则、返回、收藏入口均降为 secondary / tertiary。
2. Primary Action 使用满可用宽度、高对比实心表面。Fidgeting App 暗色原生页面建议白色 `92–100%` 填充配黑色 `86–92%` 文本；不要依赖 `accent.opacity(0.16)` 让用户猜主操作。
3. Unity 透明模型舞台若实心按钮会遮挡 Hero，可保留高对比玻璃变体，但必须与普通卡片拉开至少一个明确层级：更高亮度、更高文字对比、固定底部 action region；不能只是另一张可点击玻璃卡。
4. Primary 文案只保留动词或“动词 + 直接对象”，例如“单抽”“查看结果”。消耗 `1 张抽取券`、余额不足原因和概率说明放在按钮外的邻近 metadata，不放进按钮第二行。
5. Secondary Action 与主操作同对齐、可同宽，但使用中性 tonal/glass 表面。Fanatics 的 outline 可作为层级证据，不能直接覆盖当前 `FDB-UI-004` 的“默认不加描边”锁定规则；是否允许 `1 pt` 次按钮边界必须由用户明确批准。
6. Tertiary Action 使用文字或 icon-only 工具按钮，仅用于低风险导航／辅助动作，不与主要完成操作争夺底部位置。

### 3.2 建议尺寸

| Token / 组件 | 建议值 | 说明 |
| --- | ---: | --- |
| Primary 高度 | `52 pt` | 保留当前 Fidget 高度；高于最小热区且接近 Fanatics 的底部 pill 比例。 |
| Primary 圆角 | `26 pt` | 完整 pill；与当前 `FidgetUITokens.Radius.pill` 一致。 |
| Primary 水平 inset | screen `20 pt`；sheet/card `16 pt` | 393 pt 宽设备仍保留明确边界；内部容器不能重复再加 screen inset。 |
| Primary label | Oxanium `17 pt semibold` | 单行、原生字距；中文由系统级联。 |
| Full-width secondary 高度 | `48–52 pt` | 与 primary 同组时优先等高；独立次操作可用 48 pt。 |
| Compact action 可见高度 | `40–44 pt` | 外层点击热区始终不小于 `44 × 44 pt`。 |
| 同组按钮间距 | `8 pt` | Onboarding 主／次操作或垂直 action stack。 |
| 按钮与说明 metadata | `8 pt` | metadata 属于按钮外部，不塞入 label。 |
| 底部 safe-area 前留白 | `12–16 pt` | CTA 不贴 home indicator；由统一 action dock 计算。 |

### 3.3 状态矩阵

| 状态 | 视觉 | 行为／无障碍 |
| --- | --- | --- |
| Rest | 高对比实心 Primary；单行动词 | `.isButton`，明确 accessibility label。 |
| Pressed | 建议 `0.98` scale + 亮度轻降，`100–140 ms` | 不改变布局，不触发模型自旋。 |
| Loading / in flight | 宽高和 label 区域不跳动；可用紧凑 spinner 替换或邻接 label | 禁止重复提交；朗读“处理中”。 |
| Disabled | 中性表面、低对比文字；建议整体视觉不透明度约 `0.36–0.44` | 真正 `.disabled(true)`；必须提供可理解原因，不能只变灰。 |
| Success | 导航到下一真实状态或短暂确认后进入 reveal | 不把 Success 色常驻成另一个按钮主题。 |
| Error | 保持可重试主操作；错误原因在按钮附近独立呈现 | 不让错误文案替换动作，VoiceOver 能读出原因。 |

## 4. 建议合并的 Chip / Tag guideline

### 4.1 语义拆分

- **Filter Chip**：可交互，改变筛选／排序；具备 rest、selected、pressed、disabled，外层热区至少 `44 pt`。
- **Status Tag**：只读，例如 `OWNED`、`NEW`、`UNCLAIMED`；不得使用 Button trait、interactive glass、chevron 或按压反馈。
- **Category Chip**：若可切换则属于 Filter Chip；若只是分类说明则属于 Status Tag。业务层不得只凭胶囊外观决定交互。

### 4.2 建议尺寸与状态

| 属性 | Filter Chip | Status Tag |
| --- | ---: | ---: |
| 可见高度 | `32 pt` | `24–28 pt` |
| 水平 padding | `12 pt` | `8–10 pt` |
| label / icon gap | `4 pt` | `4 pt` |
| 相邻间距 | `8 pt` | `6–8 pt` |
| 圆角 | 高度的一半 | 高度的一半 |
| 点击热区 | 最小 `44 × 44 pt` | 无点击热区；只按内容尺寸 |
| 未选 | 白色 `8–10%` 中性填充 | 语义 tint `6–10%` 或中性填充 |
| 已选 | 白色 `16–20%` 或有明确语义的 accent；附 `checkmark` / `×` | 不使用 selected；状态由文字和语义图形表达 |

Fanatics 的已选 chip 使用蓝色填充，但 Fidgeting App 不应把蓝色复制为全局选择色。默认选中态继续使用白色层级；rarity、库存、错误等确有语义时才使用对应局部 accent，并同时提供 `checkmark`、`×` 或明确文字，不能只靠颜色。

## 5. 建议合并的 Spacing guideline

建议把当前 `4 / 8 / 15` 改为规则化的 4 pt 网格；`15 pt` 在用户批准后统一迁移为 `16 pt`，避免业务页面继续出现 13、15、18 等近似值。

| 层级 | Token | 使用场景 |
| --- | ---: | --- |
| `xxs` | `4 pt` | icon-label 紧凑间距、chip 内 icon gap |
| `xs` | `8 pt` | 同组控件、按钮与 metadata、相邻 chips |
| `sm` | `12 pt` | 卡内相关内容、底部 CTA 与 safe area |
| `md` | `16 pt` | card padding、sheet inset、相关内容组 |
| `screen` | `20 pt` | 纯原生满屏页面左右边距 |
| `lg` | `24 pt` | section 间距、Hero 与信息区 |
| `xl` | `32 pt` | 主要阶段／页面区块切换 |

规则：嵌套容器只在自己的语义层级加一次 inset；screen `20 pt` 内的 card 已有 `16 pt` padding 时，业务内容不得再叠一层 `16–18 pt` 造成过度缩窄。

## 6. 现有实现差距

### 6.1 共享组件

| 位置 | 当前状态 | 差距 / 建议 |
| --- | --- | --- |
| `FidgetUITokens.Spacing.section = 15` | 不在 4 pt 网格 | 用户批准后改为 `16`，同步 runtime、guideline 和测试。 |
| `ProductPrimaryActionLabel` | `52 pt` / `26 pt` 已符合尺寸；始终白字 + `accent.opacity(0.16)` interactive glass | 缺少明确高对比实心变体、loading、disabled reason、pressed style；建议升级成承载状态的 `ProductPrimaryActionButton`，或新增 style 而非让业务页重复实现。 |
| `ProductActionLabel` | `44 pt`、16 pt radius，强制 `Label(title, systemImage:)` | 与“产品级文字 CTA 不加装饰 icon”存在潜在冲突；应把 text secondary 与 semantic-icon utility action 分成两个 API。 |
| `ProductStatusPill` / `ProductInlineTag` | 只读胶囊已有，但没有交互 Filter Chip | 新增 `ProductFilterChip`，不要用 `Button { ProductStatusPill(...) }` 临时拼装。 |

### 6.2 抽卡页面

| 位置 | 当前证据 | 差距 / 风险 |
| --- | --- | --- |
| `FidgetGachaStorefront.drawDock` | 单抽为 62 pt 高、19 pt radius、两行 label、18 pt page inset；十抽静态块占 116 pt | 与建议的 52/26、单行动词、20 pt screen inset不一致；静态“十抽／后续开放”仍像不可点按钮，违反交互诚实性。 |
| `FidgetGachaStore.drawButtons` | 同时绘制单抽与十连；16 pt radius；存在硬编码系统字体 | 与 Design Bible “首批只开放单抽”及全局 Oxanium 规则不一致；需确认 shipping 路径后删除或迁移 legacy，而不是两套一起改。 |
| 两份 Gacha UI | Button、font、inset、radius 各自手写 | 同一功能存在重复视觉默认值；用户批准后应统一收口共享组件，避免 Rive 接入后的抽取状态再漂移。 |

## 7. 合并门禁与推荐顺序

1. 先让用户确认本文中的 Primary / Secondary、Filter Chip / Status Tag、4 pt spacing grid，以及“Fanatics outline 是否只作参考、不直接复制”的冲突处理。
2. 获批后，在 Design Bible 新增或更新稳定 `FDB-UI-*` 要求，记录当前 task/thread、2026-08-18 approval round、`DecisionState` 和独立 `DeliveryState`。
3. 同一实现任务更新 `LiquidGlassDesignGuideline.md`、`FidgetUITokens`、共享 Button / Chip 组件及验收测试；不得只改文档或单个抽卡页面。
4. 再用批准后的组件重构完整抽卡 UI；Rive 播放状态和抽取结果状态只组合共享组件，不另造按钮。
5. 生成真实 shipping Simulator 预览，等待用户视觉批准；批准前状态必须写“视觉批准待确认，未推送手机”。
6. 视觉批准后才合成 Build；iPhone 安装与 Device Accepted 仍是独立门禁。

## 8. 本轮明确未做

- 未修改 `LiquidGlassDesignGuideline.md`、`FidgetingAppProductDesignBible.md`、SwiftUI runtime 或抽卡 UI。
- 未生成 Build，未安装手机，未声称 Fanatics 的内部 token 数值。
- 未把 Mobbin 外部参考当作用户视觉批准证据。
