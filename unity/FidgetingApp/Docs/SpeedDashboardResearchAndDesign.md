# 半圆速度仪表盘：体验研究与设计规格

最后更新：2026-08-06

## 目标

仪表盘的目标不是用随机奖励延长使用时长，而是让用户清楚感到“这是我亲手把真实速度推上去的”。体验由连续因果反馈、确定性速度带、稀缺峰值反馈和平静收尾组成；指针、数字、弧线、声音与触感都不得夸大或制造不存在的速度。

## 研究依据

- [Ryan 与 Deci 的自我决定理论](https://www.selfdeterminationtheory.org/SDT/documents/2000_RyanDeci_SDT.pdf)：清晰能力反馈和自主感有利于内在动机。
- [Burgers 等人的游戏反馈实验](https://doi.org/10.1016/j.chb.2015.01.038)：反馈应描述玩家自己的表现，不用他人比较或羞辱性低分驱动继续体验。
- [Juiciness 大型实验](https://doi.org/10.1016/j.entcom.2020.100359)：无反馈和极端 feedback 都不是最佳点；本产品采用中等、确定性的强化。
- [Kivetz、Urminsky、Zheng 的 goal-gradient 研究](https://www.columbia.edu/~rk566/Session4/Goal-Gradient_Illusionary_Goal_Progress.pdf)：清晰目标可以增强投入，但本产品只显示真实速度和公开阈值，禁止伪造初始进度。
- [美国交通部 Volpe 动态显示人因指南](https://www.volpe.dot.gov/sites/volpe.dot.gov/files/docs/Human_Factors_Considerations_in_the_Design_and_Evaluation_of_Flight_Deck_Displays_and_Controls_V2.pdf)：动态符号应保持足够更新率，并用无超调 smoothing / hysteresis 降低抖动。
- [Di Luca 等人的视觉—触觉同步实验](https://massimilianodiluca.info/publication/di-luca-2019/)：视觉与触觉事件应尽量同时开始；本产品把跨区语义事件的音画触启动差目标设为 50 ms 内。
- [Apple Color HIG](https://developer.apple.com/design/human-interface-guidelines/color) 与 [Apple Haptics HIG](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)：状态不能只靠颜色表达，触感必须简短、同步、可关闭并避免过度使用。
- [Need for Speed Unbound 官方视觉系统说明](https://www.ea.com/news/under-the-hood-show-up-and-show-off)：强度与玩家真实行为确定性绑定，并允许使用更克制的视觉/声音选项。
- [变量奖励与数字行为成瘾风险综述](https://pubmed.ncbi.nlm.nih.gov/36701907/) 与 [WHO 游戏障碍说明](https://www.who.int/news-room/questions-and-answers/item/addictive-behaviours-gaming-disorder)：禁止隐藏概率、随机高价值反馈、FOMO、streak 损失和“差一点再来一次”。

## 体验规则

1. 连续扫掠场的终止边表达方向与速度变化，大号等宽数字表达精确值；二者必须来自同一真实 telemetry。
2. 速度带固定为 Calm `0...25%`、Flow `25...55%`、Drive `55...80%`、Peak `80...100%`，退出阈值比进入阈值低 4%，防止边界颜色抖动。
3. 数据按现有 20 Hz HUD 节奏只读发布；扫掠场使用 100 ms ease-out，无 overshoot，不创建 60 Hz 独立 Timeline。
4. 色带用 180 ms crossfade。数字只做稳定的等宽替换，不缩放、不弹跳、不增加字间距。
5. 只有扫掠场和少量状态文字变色；数字、刻度、背景与导航保持中性。两个翼表继承主表当前色带但降低不透明度，不能建立独立色彩状态或 glow。主表在 Peak 状态只增强局部光晕，不显示火苗或其他装饰图形。
6. Flow 使用青绿、Drive 使用橙色、Peak 使用火红。火红表达已定义的最高速度表现态，不代表机械故障或安全报警；未来若引入真正警告，必须同时使用不同图标、文案和语义，不能只靠同一红色。
7. 强度、节奏使用主表左右两侧的从属翼表；三表在同一水平簇中保持 10 pt 明确间距，任何圆弧、扫掠场、数字和点击/可访问区域都不得重叠。它们分别读取真实 `combo.intensity` / `combo.frequency`，不得从 RPM 推导或互相绑定。速度数字仍是唯一大号 Hero headline，翼表不得与 3D 主体或主表争夺中心。
8. 跨速度带若未来增加音效或触感，必须由领域层发出一次 `SpeedBandEntered` 语义事件，再进入既有 `semantic event → Haptic recipe → iOS renderer`；组件不得直接调用 Haptic。
9. 停止后保持 `0` 的 dormant 仪表，不用 idle animation、虚假余速、引擎循环声、倒计时或“再试一次”文案。
10. Speed / Intensity / Frequency 作为一个整体固定在盘玩界面最下方的成长卡上方；Combo 档位文字固定在 3D 模型顶部，Spin Reward / Peak 反馈位于仪表簇上方。底部定位不得覆盖 Home Indicator、96 pt 成长卡或其 12 pt 外边距。
11. 每枚仪表的 headline 数字与单位位于半圆内部，Intensity / Speed / Frequency 名称位于各自半圆正下方并保持左 / 中 / 右位置不变；名称使用 Oxanium `caption2` bold、固定 20 pt 高的 90% 黑色无描边胶囊、纯白字、最高布局优先级与高 z-index，以独立层保证明暗背景下都可见，内部读数不得遮挡圆弧或刻度。

## `ProductSpeedDashboard` 规格

- 在 320 pt 宽三表簇中自适应为 124–160 pt 宽；常规总高度 118 pt，Accessibility 字号总高度 148 pt，其中半圆图形区域自适应为 68–84 pt，并为标签保留不可压缩的独立高度。
- 真正的 180° 圆弧，轨道 2.5 pt、活动弧 5 pt，圆头。
- 常规 13 根刻度，其中 5 根主刻度；Accessibility 字号收敛到 7 根。
- 指针长度为半径的 72%，线宽 2 pt；中心轴外圈 11 pt、内芯 4 pt。
- 不显示刻度数字；半圆内部的速度读数是唯一 headline，使用 `@ScaledMetric(relativeTo: .title2)` 和 25 pt 起始系统等宽数字。
- Speed / 状态名称使用 `caption2` 并位于半圆下方；25 pt 数值与 `caption2` 单位在半圆内部使用同一首行基线，数字仍明显高于名称但不遮挡指针。
- 不加 `tracking` / `kerning`，首版不打包外部赛车字体。
- 默认使用局部径向 legibility scrim；Reduce Transparency 使用 82% 黑色、22 pt 圆角实体背景。
- Peak 使用火红扫掠场和局部光晕，不生成火苗轮廓或其他装饰图形。
- Reduce Motion 仍显示真实扫掠终止位置，但取消非必要的 spring、scale 和循环动效；Reduce Transparency 取消 blur / shadow，保留实体扫掠场与高对比标签胶囊。
- 外层合并为一个 accessibility element，例如“转速，186 RPM，DRIVE”；20 Hz 数值更新不得每次主动播报。

## `ProductSideMetricDashboard` 规格

- 左右各一枚 64–74 × 78 pt 从属翼表，常规 7 根刻度；Accessibility 字号总高度可扩到 98 pt，其中半圆图形区域为 48–54 pt，并为标签保留不可压缩的独立高度。
- 轨道 2 pt、活动弧 3.5 pt、指针 1.6 pt；不使用 shadow / glow，色彩取自主速度带并降低不透明度。
- 数字以 `@ScaledMetric(relativeTo: .headline)` 的 17 pt 起始字号显示在半圆内部，名称和单位使用 `caption2`；Intensity / Frequency 名称位于半圆下方，数值与单位首行基线对齐，主 RPM 仍保持更强层级。
- Intensity 与 Frequency 各自独立读取 `ProgressionComboState`，三个指针可以独立移动；翼表只复用主表视觉语言，不暗示三个数据互相派生。
- 不加 `tracking` / `kerning`，Reduce Motion 取消非必要动画，Reduce Transparency 使用局部实体底色；每个翼表分别合并为一个 accessibility element。

## 数据和组件边界

```text
rotor angular speed
→ SpinnerComboRules.NormalizeSpeed（30 rad/s 满量程）
→ SpinnerSpeedDashboardRules（确定性速度带 + 4% 回差）
→ ProductMotionTelemetryNativeBridge（20 Hz，只读）
→ ProductMotionTelemetryState
→ SpinnerMetricCluster
→ ProductSpeedDashboard（Hero RPM）
  + ProductSideMetricDashboard（真实 Intensity）
  + ProductSideMetricDashboard（真实 Frequency）
```

- `ProductSpeedDashboard` 与 `ProductSideMetricDashboard` 只接收表现数据，不引用 `UnityBridge`、模型 enum、Haptic API、物理或 progression 写操作。
- 四款旋转玩具显示真实 RPM；30 rad/s 对应约 286 RPM。
- 磁吸推牌的 `ActivitySpeedRadians` 不是旋转 RPM，因此不显示这个组件。未来若定义真实线性/节奏单位，可以复用视觉组件，但必须由领域层提供正确语义。
- Reset、进入 Library、场景销毁显式发送零或 unavailable；任何仪表逻辑都不得写 Rigidbody 或制造自转。
- `ProductOverlayLayout` 统一定义 96 pt 成长卡高度、12 pt safe-area 底部 inset 与 14 pt 仪表间距；`SpinnerExperienceFeedbackLayer` 使用 `safeAreaInsets.bottom + 122 pt` 将三联仪表簇锚定在成长卡正上方，UIKit 约束复用同一组常量，禁止两处默认值漂移。

## 待真机验证

- 320 / 375 / 393 / 430 pt 竖屏下，三表之间保持可见间距，两个翼表不截断、不压住主 RPM headline，也不遮挡 3D Hero。
- 三联仪表簇在四种屏宽下都位于成长卡上方 14 pt，且不进入 Home Indicator；Combo 档位文字使用 safe-area-aware 顶部锚点并保持在模型顶部，Spin Reward / Peak 反馈出现时只能从仪表上方生长。
- 三枚 headline 数字与单位完整位于各自半圆内部，Intensity / Speed / Frequency 高对比胶囊名称完整位于半圆下方；读数不覆盖刻度或扫掠场。
- 首次有效输入立即出现 RPM 变化；Reset 精确回到 0；扫掠终止边无超调。
- Flow / Drive / Peak 边界在 4% 回差内不闪烁。
- Reduce Motion、Reduce Transparency、Accessibility 字号和 VoiceOver。
- 20 Hz SwiftUI 更新不产生明显 Unity 帧耗、GPU、温升或电池回归。
- 明暗五款环境下的数字、刻度、扫掠场和三个标签胶囊对比度。
- Intensity / Frequency 独立变化时，翼表扫掠场和值正确跟随且只继承主表颜色。
- Peak 进入/退出时火红和光晕与 4% 回差一致，且不出现火苗；Reduce Transparency 下无 blur / shadow。
