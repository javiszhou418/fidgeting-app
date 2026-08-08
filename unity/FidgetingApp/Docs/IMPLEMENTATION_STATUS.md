# Fidgeting Interaction Integration Status

最后更新：2026-08-07

本文件回答一个问题：规格中的能力是否已经进入可运行代码。状态只按代码、场景接线和测试证据填写，不按聊天结论或文档完成度填写。

状态定义：

- `已集成并有测试`：运行时代码、产品接线和自动化测试齐全。
- `部分集成`：已有部分代码或接线，但还缺语义、生命周期、测试或真机环节。
- `仅规格`：只有设计规格，不能对外称为已实现。
- `待真机验收`：自动化能验证结构，但触感仍必须在 iPhone 上确认。

## Build 21 事故排查与 Build 22 恢复候选（覆盖下方较早的产品目录描述）

> **当前发布门禁：Build 22 已完成隔离 Simulator 验收构建，但尚未构建或安装到 iPhone；必须等待本节真实预览获得用户明确批准。**
> 下方 Build 20/21 与六模型相关条目是对应历史构建时点的记录，不再代表当前 Release 目录。

本次事故不是模型资产被删除，而是四个发布边界同时失效：

1. 仓库此前没有任何 Git commit，Build 21 也没有源码 commit/manifest；相同 build number 曾对应多份
   不同源码，无法可靠回滚或证明“推到手机”的具体内容。
2. 发布脚本直接从持续变化的共享 Unity 工作区导出。排查期间再次实测到另一个 FanCard Unity 任务在
   测试/预览之间改写场景、Build Settings 与资产，证明并发污染不是推测。
3. `ThreeBladeSceneBuilder.InstallDragonScaleRollbackVisuals` 把原三叶场景的 Renderer 禁用后直接插入
   尖三叶模型；产品目录又把该场景标成 `metal-three-blade`，所以新设计覆盖了错误槽位。
4. Build Settings、Swift 枚举和旧选择迁移各自维护顺序。Build 21 还把默认选择强制迁到
   `metal-three-blade`；旧 Unity `MobileCanvas` 与原生 SwiftUI 同时存在，Oxanium 又被全局用于业务 UI，
   因而产生“后几款像消失”“陌生字体/陌生 UI”的组合症状。此前“只剩陀螺”的直接原因则是原生
   overlay 安装依赖旧蓝色场景；应用级 bootstrap 修复仍保留。

Build 22 恢复候选当前固定为五款 Release 产品：尖三叶（替代旧蓝色槽位）、原三叶金属、镜钢四翼、
石墨双叶、磁吸推牌。尖三叶继续使用 `ThreeBladeEDC.unity`；原三叶金属从程序化原始几何独立重建为
`ThreeBladeMetalOriginal.unity`，两者不再共享视觉替换。`ProductCatalog` 成为 C# 场景、Coordinator、
Swift shipping cases、Build Settings 与缩略图白名单的共同来源；旧 `blue-classic` 数据只做一次性、
不覆盖新数据的迁移到 `pointed-three-blade`。FanCard 与旧蓝色源码仍保留，但不进入 Build 22 Release。

UI 恢复候选只允许原生 SwiftUI：五个 shipping scene 的 `MobileCanvas` / `EventSystem` 已移除，场景
builder 中创建旧 HUD 的代码也已删除。Build 23 真机回报确认恢复时把全局西文字体改成系统字体并非目标；
当前修正为全 App 英文与数字使用已置入的 Oxanium，中文继续由 Core Text 自动回退到 iOS 系统中文字体。
Combo 数字尺寸提高到 42 / 47 / 52 / 58 pt，继续使用中性白色；曲线调节工具只在 DEBUG 出现。
修正同时覆盖 SwiftUI `Font.product` 两个入口、根级 `productDesignSystem()` 与 UIKit navigation title；
`Font.combo` 继续保留独立语义但使用同一 Oxanium 资产。iPhone Simulator shipping Swift typecheck 已通过，
专项 `ProductUiUsesOxaniumForLatinAndNumeralsWithSystemChineseFallback` 为 `1/1`。隔离 commit `0e9fed8`
直接编译 shipping `FidgetProductUIComponents.swift`、`FidgetComboHalo.swift` 与 `CodexSwiftUIOverlay.swift`
生成的中英文混排原生预览位于 `Artifacts/TypographyRecoveryV24/oxanium-mixed-script-native.png`；该预览
当前等待用户明确视觉批准，批准前不构建或安装新的 iPhone 包。

Build 23 真机反馈还确认成长解锁 thumbnail 在常驻成长栏和升起的 `成长图鉴` Bottom Sheet 中消失。
资源并未丢失：Build 23 App bundle 内五张 shipping model PNG 与十张三叶皮肤 PNG 均存在；断点是
`NextUnlockSkinThumbnail` 只消费三叶皮肤且无数据时画画笔占位，`ProgressionLevelRow` 则完全改成了
`sparkles` 占位。当前 `ProgressionUnlockThumbnail` 统一恢复两处接线：三叶金属等级按精确 level 使用
对应 `skin-thumbnail-*`，其余模型/缺数据窗口使用当前 `product-thumbnail-*`；未解锁态继续灰化并叠加
锁标。`NativeArtworkLoader` 先走 UIKit named resource，再以 `Bundle.main.url` + `contentsOfFile` 兜底。
shipping Swift Simulator typecheck 与资源/成长 HUD 两项专项测试均通过（`2/2`）。真实原生 HUD 与
Bottom Sheet 预览分别位于 `Artifacts/ProgressionThumbnailRecoveryV24/progression-thumbnail-hud.png`
和 `progression-thumbnail-sheet.png`，当前等待用户视觉批准；批准前不构建或安装新的 iPhone 包。

同一视觉门禁的第二轮按用户反馈重排常驻成长栏：AUTO 移至左侧，下一解锁缩略图移至右侧，右侧只保留
缩略图与等级，不再显示“双列辅助轴承”文案；中央 `ProgressionMilestoneGauge` 从等级目录动态求上一个/
下一个里程碑，并把“上一等级—当前等级—下一等级”和当前区间位置叠在经验轨道上。AUTO 的 `1.0x`–
`3.0x` 动态倍率进入圆环中心，`AutoSpeedRotorAnimator` 只在 Unity 发布真实 rotary motion telemetry 且
角速度大于零时用 `CADisplayLink` 积分旋转，停转、无 rotary telemetry、视图消失或 Reduce Motion 时立即
停止 display link，不创建视觉假转。用户进一步要求图标与文字永不贴合或重叠；
`Docs/LiquidGlassDesignGuideline.md` 现把紧凑 icon-label 最小 `4 pt`、常规 `8 pt`、容器内部图形到边界
最小 `4 pt` 写为硬规则。首版只把 AUTO 圆环与 label 改到 `5 pt`，却仍用 `58 × 52 pt` 固定 frame，
使圆环顶部实际贴住容器；用户截图复核后已移除这个无内边距 frame，改为圆环到容器左右 `14 pt`、
上下 `7 pt` 的显式 padding，圆环与 AUTO label 使用 `6 pt`。用户继续要求更强的上下呼吸感、放大倍率
并使用正方形 icon container；倍率从 `9 pt` 增至 `11 pt`。继续复核后，圆环（含倍率）到 AUTO label 的
间距从 `6 pt` 增至 `10 pt`，容器同步固定为 `80 × 80 pt` 圆角正方形，上下 padding 保持 `10 pt`，
外部以 `84 × 84 pt` 占位防止侵入相邻内容。AUTO 状态不再只靠微弱透明度区分：OFF 使用中性灰环、
灰倍率和中性雾玻璃，ON 使用稳定青绿色状态色（`0.30 / 0.92 / 0.80`）的圆环、倍率与 AUTO label，
容器改为 Opal 式分层半透明材质：`ultraThinMaterial` 毛玻璃、青绿到冷蓝的低透明线性渐变、左上白色
径向柔光与右下冷色反光；不加描边，也不再使用纯色填充或依赖某款模型 accent 是否接近灰白。
Reduce Transparency 会提高渐变不透明度以维持可读性；状态变化以共享
`180 ms` selection duration 过渡；VoiceOver 继续明确读出“已开启/已关闭”。原生预览工具新增 `hud-off`
模式，与 `hud` ON 模式共同作为真机视觉门禁。用户复核后指出左右端点不仅视觉重量失衡，而且整体偏大；
AUTO 可见方形与下一解锁缩略图现共用唯一的 `64 × 64 pt` 尺寸常量，AUTO 内部转盘、间距和内边距同步
按约 `0.8×` 缩小，端点内容高度收至 `76 pt`。中央信息随后收敛为两行：第一行只保留当前等级、称号与
详情入口；第二行把上一里程碑、进度轨道、当前位置圆点与下一里程碑合并。轨道上重复的当前等级胶囊和独立
XP 数字行已移除，XP 仍通过 VoiceOver 与详情页提供。专项回归锁定精简层级及两个端点对共享尺寸的引用。
AUTO 随后从成长 Tabbar 内部移到左侧独立的 Opal 玻璃按钮；AUTO 与右侧 Tabbar 共用 `64 pt` 高度，二者以
`10 pt` 间距并列。Tabbar 内下一解锁缩略图从 `64 pt` 收至 `48 pt`，释放的宽高用于保持中央信息留白。
shipping Swift 原生预览编译通过，成长 HUD 专项回归 `1/1` 通过；
更新后的静态预览、60 fps 动态和接触表位于同一目录的 `progression-thumbnail-hud.png`、
`progression-hud-auto-motion.mp4`、`progression-hud-auto-motion-contact-sheet.png`。本轮仍等待用户明确视觉
批准，未构建或安装新的 iPhone 包。

Simulator 复核还发现两项只在 Release 路径暴露的问题：iOS 26.4 Simulator 的 4× 回缓冲区与项目
2× URP attachment 不匹配会造成黑屏；进阶轴承用 `GameObject.CreatePrimitive(Sphere)` 时又会尝试创建
被 stripping 移除的 `SphereCollider`，触发红色错误覆盖层。导出器现在只在 Simulator BuildPlayer 期间
临时把 URP/Quality MSAA 设为 4×，并在 `finally` 恢复正式 iPhone 的 2× 源值；视觉轴承则改为无碰撞体的
程序网格。两项修复均不改变正式设备的性能预算、物理或交互。

防复发措施：发布脚本现在拒绝脏工作树，Unity 导出前后必须是同一 commit；Release 真机导出必须收到
`FIDGET_SOURCE_COMMIT`，并生成/校验 `FidgetingBuildManifest.json`（bundle、version、build、commit、
场景表）。Build number 提升到 22。恢复前源码已保存为本地基线 commit `917553f`；正式恢复提交只会
选择性纳入本节文件，排除并发 FanCard 修改。

验证证据：恢复专项 EditMode `75/75` 通过，报告为
`Artifacts/RecoveryFocusedEditModeTests.xml`；隔离提交上的恢复/shipping fixture `93/93` 通过，报告为
`Artifacts/RecoveryShippingEditModeTests.xml`。同一隔离提交的全量 EditMode 为 `190/192`，原始报告
`Artifacts/RecoveryFullEditModeTests.xml` 保留两项未 shipping FanCard 基线失败：其旧测试分别期待
材质值 `0.96` 与根姿态 `0°`，基线场景实际为 `0.92` 与 `180°`；本次不通过改测试或改场景掩盖它们。
Simulator 修复后 ProductArchitecture `35/35`、进阶视觉运行时 `35/35` 通过，报告为
`Artifacts/RecoverySimulatorFixTests.xml` 与 `Artifacts/RecoveryProgressionRuntimeTests.xml`；轴承视觉仍为
零生成碰撞体。shipping Swift iPhoneOS 15 全量 typecheck 通过。五款
真实 shipping Unity 场景的 top / authored hero / 左右斜视 / low 共 25 张图及联系表位于
`Artifacts/RecoveryApprovalV22/`，总 Hero 联系表为 `shipping-five-hero-contact.png`。完整 EditMode 与
原生 Simulator Release 候选均从隔离源码生成：Build 22 manifest 固定 commit `8cbfc7b`、五个场景且
`development=false`，Unity 导出与 Xcode Release 均成功；五款分别冷启动后的原生 UI + 3D 联系表为
`Artifacts/RecoveryApprovalV22/Native/build22-five-models-contact.png`，无黑屏、红色错误层或 Developer
Console。当前 iPhone 构建、安装、视觉与动态验收均待用户明确批准后进行。

## 当前绑定矩阵

> 2026-08-07 Build 20 状态覆盖本文件中同日较早的 `approval pending` / `未装机` 描述：用户查看最新正式
> 预览后明确要求“把最新的版本推到我手机上来”。最新源码已重新完成 Unity 导出（`Build Finished,
> Result: Success`）及 Xcode Release 构建（`BUILD SUCCEEDED`），Release `0.1.0 (20)` 已覆盖安装并启动。
> `devicectl` 回读设备安装路径已更新为 `098F4F87-.../FidgetSpinner.app`，当前运行 PID 为 18462。
> 安装和启动仍不记为真机动态视觉/手感验收。

> **2026-08-07 真机回报校正：上述 Build 20 是已知缺陷版本。** 用户确认该包只显示 Unity 陀螺，整套
> 原生 UI 均未出现。根因是首场景从蓝色经典款改为龙鳞三叶后，`IosSwiftUiOverlayController` 仍只序列化
> 在旧蓝色场景，导致启动路径没有调用 `CodexSwiftUiOverlayInstall`。用户随后批准真实冷启动预览并要求推送；
> 修复后的 Release `0.1.0 (21)` 已完成 Unity 导出、Xcode Release 构建、覆盖安装与启动。`devicectl`
> 回读 Build 21，运行 PID 为 18852。Build 20 的“已启动”不能再当作 UI 正常证据，Build 21 的安装与启动
> 也不替代用户对真机完整 UI 的肉眼确认。

| 能力 | 状态 | 运行时代码证据 | 测试证据 | 尚缺内容 |
| --- | --- | --- | --- | --- |
| 原生 UI 应用级冷启动引导（修复“只剩陀螺”） | 根因已修复、真实预览已获批准，Release Build 21 已覆盖安装并启动；待用户真机肉眼确认完整 UI | `IosSwiftUiOverlayController.InstallAtApplicationStartup` 使用 `RuntimeInitializeOnLoadMethod(AfterSceneLoad)`，因此启动安装不再依赖旧蓝色场景里序列化的 MonoBehaviour；原有 `Start` / `OnApplicationFocus` 继续作为兼容补充。原生 `CodexSwiftUIOverlayManager.install(retryCount:)` 在 Unity UIWindow 尚未成为 key window 时以 100 ms 间隔最多重试 12 次，避免唯一安装请求被静默丢弃。iOS Simulator 导出固定为 `AppleMobileArchitectureSimulator.ARM64`；真机包号为 21 | 专项 `NativeOverlayInstallIsApplicationBootstrappedAndDoesNotDependOnTheBlueScene` 为 `1/1`，报告 `Logs/NativeOverlayBootstrapRegression.xml`；最新完整 EditMode `189/189` 通过并包含该回归，报告 `Logs/FanCardFullEditModeTests.xml`。shipping iPhoneOS 15 Swift typecheck、Unity Simulator 导出和 arm64 Xcode Debug 构建均通过。真实冷启动截图 `Artifacts/NativeOverlayBootstrapFix/cold-launch-ui-restored-15s.png` 已显示 Fidgeting 顶栏、左右按钮、三叶金属标题、Page Control 与主操作按钮 | 用户批准预览后，Unity 真机导出报告 `Build Finished, Result: Success`，Xcode Release 报告 `BUILD SUCCEEDED`；`0.1.0 (21)` 已覆盖安装到 iPhone `00008130-001A00361EE0001C` 并启动。设备 inventory 与进程回读分别见 `Logs/DeviceBuild21NativeOverlayInstalledApps.json`、`Logs/DeviceBuild21NativeOverlayProcesses.json`，PID 18852。仍需用户在 iPhone 冷启动、退后台/回前台、六模型切换及详情页肉眼确认 UI 持续存在 |
| 第六款三层磁吸扇牌与独立四档阻尼 | 已集成并有测试；待用户视觉批准与 iPhone 手感验收，未构建/未推真机 | 新产品 `magnetic-fan-card` 使用独立场景 `_FanCard/Scenes/MagneticFanCard.unity`、`FanCardDetentProfile`、`FanCardMagneticTrack` 与 `FanCardController`；三张 `52 × 74 × 2.6 mm` 竖牌共享右上圆角圆心轴，底/中层各有一条向左下内缩的 45° 弧轨和 3 枚磁体，中/顶层各有一枚随动球。四档固定为 `0 / 1⁄3 / 2⁄3 / 1`，中片 `45°q`、顶片 `90°q`，并保留批准 demo 的脱档、弹簧、阻尼、摩擦、捕获与 `1/240 s` 子步。Coordinator、场景目录、Build Settings、iOS 枚举、缩略图和共享相机/双指展示手势已接线；语义事件只从机械状态进入 `FidgetHapticRouter`，无新 raw-input→`IosHaptics`。枪黑珠喷框、暖银面、铬件、金色编织轨道、Oxanium A、向下黑桃和蚀刻细线都是独立展示层，没有 Collider/Rigidbody，也不读取或写入前五款调节值。预览曾因共享物理相机的 `36 × 24 mm` Horizontal Gate Fit 与 `900 × 1600` RenderTexture 重复应用竖屏门幅而横向压缩；正式场景现以 `FanCardCameraProjectionGuard` 选择同 50 mm 视角的标准透视，模型仍为原生 `52 × 74 mm`，没有非等比 Transform 补偿；第五款默认物理相机保持不变 | `FanCardAcceptanceTests` 定向 EditMode `9/9` 通过，报告 `Logs/FanCardTests.xml`；新增 1290 × 2796 屏幕投影宽高比必须等于 `52/74`（误差 ≤ 0.01）的回归，并继续覆盖四档参数、阈值仅一次、正反向对称、30/60/120 Hz 同档归零、三层共轴、45°/90°、2 条轨道/6 枚磁体/2 个随动球、材质、Oxanium A、面数预算与无直接 Haptic。完整 EditMode `190/190` 通过，报告 `Logs/FanCardFullEditModeTests.xml`；同一源码的 iPhoneOS 15 Swift typecheck 通过。六张 shipping Unity GPU 预览位于 `Artifacts/FanCardMaterialPreview/`，生成日志为 `Logs/FanCardPreviewGpu.log` | 当前纠正比例后的六视角预览仍待用户明确视觉批准；批准前不执行 iOS build/install。批准后仍需 iPhone 验证四档盲辨、脱档/跨档/捕获、视觉与 Haptic 同帧、双指展示手势、热区和连续往返稳定性 |
| 龙鳞三叶替换首个陀螺 | 已集成、测试、覆盖安装并启动；待真机肉眼验收 | `SpinnerModel.allCases`、`FidgetAppCoordinator.ProductModelIds` 与 `IosBuildPipeline.ProductScenes` 均以 `metal-three-blade` / `ThreeBladeEDC.unity` 为首项；`ProductUiState` 用 `fidgeting.primaryModelCatalogVersion = 1` 把既有安装的一次性默认选择迁移到龙鳞三叶，之后继续尊重用户选择；蓝色经典款保留为第二项。启动与 Reset 仍保持零角速度 | Swift iPhoneOS 15 typecheck；ProductArchitecture `32/32`、完整 EditMode `180/180`，报告 `Artifacts/PrimaryModelFocusedEditModeTests.xml`、`Artifacts/PrimaryModelFullEditModeTests.xml`。Unity 导出日志 `Logs/iOSBuild-DragonScalePrimary-B20.log`；设备回读 `Logs/DeviceBuild20InstalledApps.json` 确认 `com.jiaweizhou.fidgetspinner.codex / 0.1.0 / 20`，`Logs/DeviceBuild20Processes.json` 回读 PID 18095 | 已启动 Build 20；仍需用户在手机上确认第一页和旧选择迁移显示龙鳞三叶，并检查圆件轮廓、金属高光、贴纸、长按与 Combo 动态；启动不替代肉眼验收 |
| 长按模型轻弹、语义 Pop 与 Half Sheet 顺序（覆盖下方外观编辑行的较早直接打开描述） | 待用户预览批准；未构建/未推真机 | 长按成立后立即禁用当前模型交互并经 `FidgetHapticRouter` 发出一次语义 `Pop`；`ProductAppearanceActivationSequence` 以相机 framing 完成 `1.000 → 1.035 → 0.992 → 1.000`、总长 `0.22 s` 的物理中立轻弹，随后才打开现有共享组件 half sheet。三套正式产品相机均接入，未缩放模型 Transform 或修改碰撞体/角速度 | `SpinnerProgressionTests` 定向 `34/34`；完整 EditMode `178/179`，唯一失败是正式三叶场景当前 `48,054` tris 超出既有 `45,000` 预算，与本次入口状态机/相机距离修改无关。报告 `Logs/LongPressActivationEditModeTests.xml`、`Logs/LongPressActivationFullEditModeTests.xml`。五视角四阶段 shipping-scene 联系表与 Hero 动态预览位于 `Artifacts/Appearance/LongPressActivationV1/` | 必须先获得本轮预览的明确视觉批准，再执行 iOS 构建和安装；手机上仍需确认 Pop 强度、轻弹幅度、`0.22 s` 延迟、half sheet 动画与关闭恢复 |
| Combo 里程碑模型平面分层光晕与动画曲线工具（本行覆盖下方“无周圈光环”的旧描述；旧约束仅继续禁止包围 Combo 文字的常驻描边/光环） | 已按参考 2+3 重做、通过真实预览门禁、覆盖安装并启动；待真机肉眼验收 | `Assets/Plugins/iOS/FidgetComboHalo.swift` 是生产反馈层与设置工具的共同原生源码。`SpinnerExperienceFeedbackLayer` 观察真实 `progressionCombo.count`，默认只在跨入 10、20、30…时播放 `ComboCenterHalo`；`ComboHaloProjectionRules` 从活动模型 live bounds/author focus、机械旋转轴或推牌表面法线及 Camera 投影两个平面切向量求中心、椭圆倾角和短轴比，再由原生桥只读发布给 SwiftUI。`ComboCenterHalo` 保持 920 ms / 104% / 34% 推荐值，以 `AnimatablePair` 分别消费第一道环的 cubic Bézier 扩散和独立线性时间。线性时钟驱动五条错拍包络：20% 前结束的核心闪光；0% / 5% / 10% 依次启动、分别于 48% / 64% / 80% 消失的三道 burst ring；以及 1% 启动、10% 达峰并持续到末尾的中心能量雾。`ComboHaloBrokenRing` 把每道环拆成四段不等亮圆弧，并使用不同终点和缺口转角；作用范围按屏幕短边计算，不再扩成上下两条大弧。雾层由两层 `ComboHaloMistCloud` 不规则云轮廓、九个局部湍流雾团和 `ComboHaloMistWisps` 七条旋散丝缕组成，不是模糊完整圆环。所有层分别按 live 模型平面压扁/转向，保持中性白灰、不读取 `combo.accent`、普通 +1 不触发；设置页复用完整渲染器和两个可拖 Bézier 控制点。该表现链不写物理、XP、tier、Haptic、音频或相机 | Swift 门槛/钳制/投影/五层透明度包络规则 `47/47` 通过；shipping Swift iPhoneOS 15 typecheck 与 Simulator DEBUG 编译通过。结构断言锁定 `AnimatablePair` 双进度、三道断裂脉冲环、中心云雾/九个湍流雾团/七条旋散丝缕和四个模型平面压缩值；`SpinnerProgressionTests` 为 `34/34`，完整 EditMode 为 `180/180`，报告 `Logs/ComboHaloReferenceFocusedTests.xml`、`Logs/ComboHaloReferenceFullEditModeTests.xml`。`Tools/ComboHaloNativePreview/capture.sh` 直接编译 shipping SwiftUI 文件并叠加正式 Unity 场景帧：五角度静态帧与 `combo-halo-angle-contact-sheet.png` 展示模型平面压缩，60fps `combo-halo-motion.mp4` 展示完整动态，`combo-halo-burst-contact-sheet.png` 紧凑覆盖三道脉冲环与雾层时间差，曲线工具输出 `combo-halo-curve-tool.png` | 用户查看最新真实预览后明确要求推送，Device visual push gate 已满足。2026-08-07 最新源码重新完成 Unity iOS 导出与 Xcode Release 签名构建，`BUILD SUCCEEDED`；`0.1.0 (20)` 已覆盖安装到 iPhone `00008130-001A00361EE0001C` 并启动，设备回读为 PID 18462，证据见 `Logs/DeviceBuild20LatestComboInstalledApps.json` 与 `Logs/DeviceBuild20LatestComboProcesses.json`。仍需用户在真实 Combo 9→10→20→30、五款模型自由视角、快速合并更新、Reduce Motion / Transparency、VoiceOver 与热功耗下肉眼验收；预览、编译、测试、签名与启动均不能替代真机动态验收 |
| 仪表标题强制可见、Combo 中性文字与真实机械进度计数（本行覆盖下方较早的 18 pt/78% 标签、Combo accent 与仅完整手势 +1 描述） | 已构建安装；待真机肉眼验收 | Speed / Intensity / Frequency 的 `ProductDashboardCaption` 改为纯白 Oxanium bold、固定 20 pt 高、90% 黑色无描边底，加入 `layoutPriority(2)`、独立 compositing group 与 z-index 5；不再使用低透明文字或 10% stroke。`RewardingComboLockup` 的数字渐变、`×`、COMBO、档位、数字残影与火花全部使用中性白色，整个 Combo presentation 不再读取 `combo.accent`。`SpinnerComboRuntime.RecordMechanicalActivity` 在 Combo 已由真实重复手势激活后，将每 120° 的实际旋转或 EDC 行程等效角度转换为一次展示 count；0.16 秒脉冲门限制为最多 6.25 次/秒，当前实际速度低于 4 rad/s 不累计。真实活动脉冲延长可见窗口，但不发 XP、不改变 tier/倍率、不写物理；Coordinator 明确排除 Library 与 `IsAssistantDriveActive()`，AUTO 无法刷数 | Swift iPhoneOS 15 typecheck 通过；`Combo_RealMechanicalTravelAddsFastLegibleCountPulses`、`ComboPresentation_UsesNumberFirstBorderlessRewardLevelsAndIos15Fallback`、`SpeedDashboard_UsesVisibleCaptionsWithoutDecorativeFlames`、`RotarySpeedDashboardAndComboPipelineUseCanonicalSources` 聚焦 `4/4`，完整 EditMode `173/173` 通过，报告 `Logs/ComboCadenceLabelsFocusedTests.xml`、`Logs/ComboCadenceLabelsFullEditModeTests.xml`。测试锁定 119° 不增长、达到 120° 才增长、0.16 秒限流、XP 倍率不变、AUTO 排除、Combo 无 accent，以及三个标题的固定高度/对比度/层级 | 2026-08-07 已重新完成 Unity iOS Release 导出与 Xcode 签名构建，`BUILD SUCCEEDED`；版本 `0.1.0 (19)` 已覆盖安装并由 `devicectl` 成功启动到 iPhone `00008130-001A00361EE0001C`。仍需用户在手机上确认三个标题、白色 Combo、快速旋转/慢推时 count 密度、破连、Reduce Motion、VoiceOver 与性能；构建、安装和自动化通过不替代动态视觉验收 |
| 三叶金属旋转轴锁定屏幕可见中心（本行覆盖上一轮只锁定隐藏中层原点的描述） | 已构建安装；待真机肉眼验收 | 上一轮把 `ThreeBladeEDC_Root.position` 锁到画面中心，只保证隐藏在模型厚度中层的机械原点居中；斜视角下它与用户实际看到的顶盖中心投影不重合。`OrbitPresentationCamera` 现新增并在正式场景显式接线 `focusTarget = HubStatic/TopCap/TopCap_Root/FingerCapTop_BrushedFace`，以该静态顶盖 Renderer 的可见中心同时计算镜头位置与安全 framing distance。该点横向仍与 `RotorDynamic` 物理 Y 轴共线，但位于可见上表面；旋转中的非对称转子 AABB 不再参与焦点，运行时只重放姿态且 zoom 不随转角重算。场景重建器同步写入同一接线；未修改 Rigidbody、角速度、阻力、手势、Haptic 或模型几何 | `VisibleRotorAxisPoint_RemainsAtViewportCenterAcrossRepresentativeAngles` 在正式 `ThreeBladeEDC.unity`、1290×2796 竖屏比例下，对 `0° / 30° / 60° / 90° / 120°` 锁定可见顶盖轴心为 viewport `(0.5, 0.5)`、镜头距离恒定、全部可见 Mesh 顶点不越界，并断言可见焦点与物理轴横向共线。与 24 张贴纸居中审计组成的定向回归 `2/2` 通过，报告 `Logs/AxisStickerCenterFocusedTests.xml`。最新完整 EditMode 为 `172/173`；唯一失败是并发更新的 `DragonScaleEDC.fbx` 直径 `0.0889757 m` 比其既有测试下限 `0.089 m` 小约 `0.024 mm`，与本次三叶相机/贴纸文件无关，报告 `Logs/AxisStickerCenterFullEditModeTests.xml`。正式 Unity Metal 五转角轴心叠加及顶视/Hero/左右斜视/低角预览位于 `Artifacts/ThreeBladeRotorAxisCenterV2/`，日志 `Logs/RotorAxisCenterV2Preview-Metal.log` | 2026-08-07 的 Release `0.1.0 (19)` 已连同当前源码覆盖安装并成功启动；仍需在 iPhone 的 Library、详情、自由轮、棘轮、设备倾斜与捏合缩放中持续旋转，确认顶盖可见中心不漂移、无裁切或 zoom 呼吸。预览、构建和安装均不能替代真机动态验收 |
| 三叶贴纸最上层激光刻痕与素材内容居中（本行覆盖下方较早的接收面及 V20 素材描述） | 待用户预览批准与真机肉眼验收 | `ProductStickerPresenter` 继续把唯一共形刻痕绑定到 `FingerCapTop_BrushedFace`，其投影原点与相机新的可见中心同为该 Renderer 的 `bounds.center`。本轮确认偏移来自 24 张 1024² PNG 内部不一致的透明留白，而不是接收面：旧素材有效图形中心最多偏离画布上百像素。`Tools/recenter_sticker_mask.py` 与 `rebuild_imagegen_sticker_vectors.sh` 现在从 ImageGen master 裁出有效掩膜，将最长边统一为 208/256（PNG 阈值包围框为 836/1024），以偶数尺寸精确居中后同时生成透明 PNG 和 SVG；24/24 有效图形包围框中心现与 `(511.5, 511.5)` 完全一致。Mipmap、Trilinear、aniso 8、iPhone ASTC 4×4、共形 Cutout、无 Quad/Collider/Rigidbody 保持不变 | `DefaultStickerCatalogAndPresenter_ArePersistentVisualOnlyAssets` 新增逐 PNG 解码与 Alpha 包围框检查，锁定 24/24 水平/垂直中心及统一尺寸；它与正式场景轴心测试的定向回归 `2/2` 通过，报告 `Logs/AxisStickerCenterFocusedTests.xml`。图形 `10-meteor`、文字 `08-geeone`、细线 `21-triple-stroke` × 正顶/Hero/左右/低角共 15 张最新 Unity Metal 预览位于 `Artifacts/Stickers/AnglePreviewCenteredV21/`，日志 `Logs/StickerAnglePreviewCenteredV21-Metal.log` | V21 是对用户指出的“不居中”的新修复，先前 V20 的批准和手机上的 Build 19 不能替代本轮批准。需用户明确确认 V21 预览后再构建/安装；随后在 iPhone 上实际切换多张贴纸并旋转/倾斜，确认图形持续位于顶盖中心、无闪烁/穿透，且深浅皮肤均像蚀刻 |
| Combo 数字优先奖励动效（本行覆盖下方较早的 `RewardingComboPill`、22 pt 数字和票券描边描述） | 待真机肉眼验收 | 模型顶部改为无边框、无胶囊容器的 `RewardingComboLockup`。Oxanium Heavy 等宽数字按 2–4 / 5–9 / 10–19 / 20+ 四档使用 38 / 42 / 46 / 50 pt，`COMBO · 顺流/强驱/超频` 降为数字下方的辅助 `subheadline`。普通增长把动效能量集中在数字：45 ms 纵向压缩蓄力、旧数字向上退出、新数字从下方进入、85 ms 冲出及可取消 spring 落定；5 次扫光只穿过数字 mask，10 次使用数字残影与 4 枚短火花，20 次及之后每 10 次使用峰值 1.40 的数字残影与 8 枚短火花。复杂模型背景上只保留无边界径向暗场，不存在 Combo `.stroke`、周圈光环、`.productGlass` 容器或整张胶囊缩放。generation token、20 Hz telemetry 隔离、Reduce Motion 0.11 s 交叉淡化、无展示层直接 Haptic/音频调用保持不变 | Swift iPhoneOS 15 typecheck 通过；`ComboPresentation_UsesNumberFirstBorderlessRewardLevelsAndIos15Fallback` 锁定四档字号/过冲、方向性交接、数字 mask、残影/火花、无描边/无胶囊容器、快速更新取消和 Reduce Motion。研究与实现映射记录在 `Docs/ComboRewardMotionResearch.md` | 仍需在 iPhone 上连续观察 2→5→10→20→30，确认奖励层级、超频文字退位、9→10/99→100 稳定宽度、复杂背景对比、快速连击不落后、Reduce Motion、VoiceOver 与热功耗；编译和静态测试不替代动态肉眼验收 |
| 仪表标签可见性、移除火苗与五模型统一画面边界（本行覆盖下方较早的火苗、112/72 pt 仪表和固定镜头距离描述） | 待真机肉眼验收 | `ProductDashboardFlames` 已从原生组件源码移除；Peak 只保留语义色与局部扫掠光晕。Speed / Intensity / Frequency 统一改用 Oxanium `caption2` bold 的 `ProductDashboardCaption`，标签拥有至少 18 pt 独立高度、78% 黑色胶囊和高不透明白字，不再依赖模型背景或低透明度文字；主表/翼表高度同步调整为 118/78 pt，外层 `SpinnerMetricCluster` 一并更新。`ProductFramingCatalog` 为五个产品定义详情/Library 画面占比边界；三套相机全部从活动 `Renderer.bounds`、当前观察方向和实际 `projectionMatrix` 计算距离，物理相机的 Horizontal gate fit 也不会再被普通 FOV 公式错误放大。经典蓝色、金属三叶、镜钢四翼使用统一圆形边界；石墨双叶与磁吸推牌使用更宽的长形边界；Library 和详情都不再读取每模型固定世界距离或额外 1.28/1.59 倍缩放。该表现链不写 Rigidbody、角速度、滑盖进度或 Haptic | Swift iPhoneOS 15 typecheck 通过。五场景测试在 1290×2796 竖屏比例同时检查详情和 Library：模型不得越过指定宽高边界，且至少填满其中一条边界，防止再次出现一款溢出、另一款过小。ProductArchitecture / SpinnerEnvironment / SpinnerProgression / EDC 相关套件 `75/75` 通过，完整 EditMode `171/171` 通过，报告 `Logs/DashboardFramingFocusedTests.xml`、`Logs/DashboardFramingFullEditModeTests.xml`；完整回归同时覆盖统一的相对捏合缩放边界 `0.72×...1.55×` | 仍需在 iPhone 上逐款肉眼确认经典/金属两款不再过大，石墨双叶/磁吸推牌操作面积足够，镜钢四翼保持合理尺度，横滑与详情过渡中无尺寸跳变；同时确认三个英文标签在亮岩壁、金属高光、Reduce Transparency、320–430 pt 和 Accessibility 字号下持续可见。自动化和编译通过不替代真机视觉验收 |
| 陀螺仪灵敏度低 / 中 / 高三档 | 待真机验收 | 设置页“设备动作”新增统一的“陀螺仪灵敏度”三段选择，并由单一 preset 同步控制五款产品的 `maximumInputAngle / motionResponse / gyroscopeLead / maximumMotionOrbit`。低档为 `18° / 8 / 0.035 / 6.5°`，中档为 `10° / 15 / 0.060 / 11°`，高档为 `7° / 22 / 0.100 / 16°`；Input Angle 因代表达到满响应所需的输入角而随灵敏度升高反向减小。选择按版本化 UserDefaults 持久化，旧版四个离散值首次读取时迁移到最近档位；只有档位实际改变才重置当前持机姿态为新零点，避免切换后模型跳变。`FidgetAppCoordinator.SetMotionSensitivityPresetFromNativeUi` 将同一 profile 应用于经典、三叶、镜钢、石墨与磁吸推牌的 Motion Controller；手动重新校准也覆盖 EDC。该链路不写 Rigidbody、转子角速度、推牌进度或 Haptic 机制状态 | `MotionSensitivityPresetsAreMonotonicSharedAndVisibleInSettings` 锁定四项参数的精确值与单调关系、原生 UI/Unity bridge、五款共享应用、EDC 重校准以及无 Rigidbody 注入；完整 EditMode `169/169` 通过，报告 `Logs/FullEditModeMotionSensitivityPresets.xml`、日志 `Logs/FullEditModeMotionSensitivityPresets.log`。同一 Swift 源码通过 iPhoneOS 15 typecheck。签名 Release arm64 `0.1.0 (17)`、约 295 MB、Bundle ID `com.jiaweizhou.fidgetspinner.codex` 已完成 Unity 导出、Xcode 构建并覆盖安装到配对 iPhone；Unity 构建证据为 `Logs/iOSBuild-MotionSensitivityPresets.log` | 手机安装时处于锁屏状态，使用 no-launch 路径，未把安装误报为启动或手感验收。需在 iPhone 设置 → 设备动作中逐档验证五款模型的倾斜响应幅度、迟滞/抖动、当前持机姿态归零、低中高差异、切换无跳变，以及 Reduce Motion 下的降级行为 |
| 模型 Page Control 与三叶皮肤真实缩略图 | 待真机验收 | 模型库切换已移除五张底部预览图和 `SpinnerLibraryThumbnailTabBar`，改用 SwiftUI `TabView` 自带的 Page Control；横滑仍通过同一个 `SpinnerModel` binding 驱动 Unity 实时预览。三叶金属 Lv.1–100 的十款真实皮肤缩略图仍用于成长详情与下一解锁预览，锁定态、正方形布局和 bundle resource fallback 保持不变 | `NativeUiUsesLivePagedModelsLiquidGlassAndModeTabs` 与 `NativeUiUsesBundledSquareArtworkForModelsSkinsAndStickers` 断言 Page Control 为 always、无旧模型预览 Tab Bar，且皮肤/贴纸资源链仍完整；ProductArchitecture 专项 25/25 通过，报告 `Logs/PageControlTopBarEditModeTests.xml`，同一源码通过 iPhoneOS 15 Swift typecheck | iPhone 上确认五个圆点与横滑/Unity 预览同步、圆点在 320–430 pt 布局和 Reduce Transparency 下可读；真机肉眼确认前不称为验收完成 |
| 顶部导航与模型库无叠层画面 | 待真机肉眼验收 | 模型库主 `ProductPanel` 已移除 `ProductSheetDragHandle`、拖拽关闭手势与顶部黑色半透明渐变，实时 3D 画面不再被 notch 或 titlebar 下方叠层遮住；真正的成长/外观 sheet 仍保留明确的关闭控件。顶部品牌统一为首字母大写 `Fidgeting`，模型库标题继续显示当前模型名和皮肤/等级 | Swift iPhoneOS 15 typecheck 与 ProductArchitecture 25/25 通过；Fidget Spinner 0.1.0 (14)、Bundle ID `com.jiaweizhou.fidgetspinner.codex` 已完成 arm64 签名、覆盖安装，并由 `devicectl device info apps` 在 iPhone「JW」回读确认版本 14。设备因锁屏拒绝启动，因此未把安装误报为视觉验收 | 解锁 iPhone 后启动 build 14，肉眼确认顶部无透明叠层、无主面板 notch、`Fidgeting` 大小写与 Page Control 布局；安装不替代肉眼验收 |
| 模型长按外观编辑、皮肤 Grid 与视觉设计贴纸 | 待真机肉眼验收 | `ProductAppearanceLongPressGesture` 以 `0.55 s / 12 pt` 的确定性规则识别单指静止长按；`FidgetAppCoordinator` 只在详情态、命中当前模型交互面且非多指/拖动时打开编辑器，打开后禁用当前模型手势并隐藏机制栏、底部成长卡和三联反馈，关闭后恢复。长按命中直接复用各机制权威输入范围：经典款 `FidgetSpinnerController.ContainsScreenPoint`、金属旋转款 `MobileGestureController.ClassifyScreenPoint`、磁吸推牌 `EdcSliderController.ContainsScreenPoint`。原生 `ProductAppearanceEditor` 以两列 `LazyVGrid` 显示皮肤及 24 张正式贴纸 thumbnail。2026-08-07 根据真机反馈撤销了悬浮 Quad 方案：`ProductStickerPresenter` 现在为活动产品的每个 `MeshRenderer/MeshFilter` 创建局部变换为零、共享同一原始 Mesh 的共形刻痕接收层；`_ReceiverToProjector` 与 `_ProjectionNormalOS` 通过 `MaterialPropertyBlock` 固定在各接收网格本地坐标，转子旋转时图形随金属一起转。`ProductLaserEngraving.shader` 用 PNG Alpha 生成深石墨刻痕和克制切边，`_SurfaceAlignment = 0.56` 裁掉背面/侧壁，UV 边界裁剪且真实网格孔洞保持为空；仅用深度偏移避免 Z-fighting，不存在独立平面、Collider 或 Rigidbody。“无贴纸”关闭全部刻痕层，选择仍按模型持久化，反馈继续走 `Selection -> FidgetHapticRouter` | `ConformalEngraving_UsesActualMetalRotorMeshesAndLocalMotion` 在真实 `ThreeBladeEDC` 场景逐个锁定 RotorDynamic 接收网格、零局部变换、同一 Mesh、同一旋转层级和零 Collider；共形专项 `2/2` 通过，报告 `Logs/ConformalEngravingMetalSceneTests.xml`。最新完整 EditMode 为 `158/162`；4 个失败来自既有 SwiftUI Combo 文案断言和三叶原始网格几何验收，与共形雕刻无关，证据为 `Logs/ConformalEngravingFullEditModeTests.xml`。Release arm64 `0.1.0 (16)` 在不复制主工程 Library/Temp 的隔离工作区完成 Unity 导出与 Xcode 自动签名，Bundle ID `com.jiaweizhou.fidgetspinner.codex`、Team `2RJ2CW6NK5`、代码签名完整性均通过，并已覆盖安装和启动到 iPhone「JW」；设备回读 PID 15261/后续普通重启成功，短时控制台进入 `applicationDidBecomeActive`、Metal A17 Pro、thermal Nominal，无 Shader/C# 异常或资源缺失。证据为 `Logs/iOSBuild-ConformalEngraving.log` 与 `Logs/XcodeBuild-ConformalEngraving.log` | 在当前 Build 16 上逐款肉眼确认中心盖/叶片/推牌交互面长按、Bottom Sheet 打开/关闭、皮肤与贴纸选择回写、刻痕紧贴曲面并随动、孔洞不被跨越、深浅金属可读性、边缘闪烁/Z-fighting、重启持久化、VoiceOver、Dynamic Type、Reduce Transparency 与纹理内存；安装、启动和日志不替代视觉验收 |
| 藏家等级、主玩加成与跨玩具成就 | 待真机验收 | `CollectorProgressionRuntime` 以独立版本化存档维护 Rank 1–30、有效活跃日、5/7 节奏周、已发现模型、外观收藏、跨玩具等级里程碑和藏家成就；账号等级不与任一玩具 Lv.1–100 混用。`FidgetAppCoordinator` 只把藏家加成接入明确的手动完成交互与真实旋转经验，Combo 与藏家加成相加后由 `SpinnerProgressionRules` 封顶 `1.50×`；离线与 AUTO 不读取该加成。Rank 30 为全局 `+10%`、每日主玩 `+20%`。原生 `CollectorProfile` 以“等级 / 成就 / 收藏”展示权威 payload；详情、藏家和设置页左上统一为 `chevron.left` 返回模型库，解锁成就与升级均有排队提示 | 六项藏家专项与原有架构/成长回归组成的定向 EditMode 45/45、完整 EditMode 147/147 通过，报告 `Logs/CollectorRankEditModeTests.xml`、`Logs/CollectorRankFullEditModeTests.xml`；同一源码完成 Swift iPhoneOS 15 typecheck、Unity Release 导出和 Xcode arm64 签名。Fidget Spinner 0.1.0 (8)、275 MiB、Bundle ID `com.jiaweizhou.fidgetspinner.codex` 已覆盖安装并成功启动到 iPhone「JW」，设备进程回读确认 `FidgetSpinner.app/FidgetSpinner` 正在运行；Unity 证据为 `Logs/iOSBuild-CollectorRank.log` | iPhone 上确认藏家入口、左上返回、三栏目滚动、每日主玩锁定、Rank/成就逐条提示、五款真实互动累计和小屏安全区；安装与启动不替代肉眼验收 |
| 五款统一场景、交互、成长与显式代盘（本行覆盖下方较早的“四款/推牌隐藏 HUD”描述） | 待真机验收 | `SpinnerEnvironmentCatalog` 已包含五个场景，并统一读取获批的 1882 × 3344 峡谷岩面背景；背景中的岩面就是承托场景本体，`SpinnerGroundingStage` 只保留模型 bounds/接触面与环境取色数据，程序石台和圆形支托在 Library 与详情均不再绘制。Library 镜头以接近 90° 的相机展示姿态让五款主体悬在岩面上方，按各材质分别控制展陈灯光/反射强度；模型实时主色驱动中央主体光晕、岩面扁平接触光和两侧岩壁回光。进入详情后恢复原始材质曝光与交互镜头，同时近景岩壁退去，只留模型、远壁与双层动态星空。`EnvironmentStarfield` 用逐星相位/速率的 `_Time.y` 亮度变化实现闪烁。第五款正式场景已重新生成 `EDC_Root`、`EdcSliderController`、`EdcPortraitCameraFramer` 与 `SharedPresentationGestureController`，既保留滑盖操作，也支持双指捏合缩放和空白处拖动视角；其滑动角度/速度仍进入成长、Combo、评价和粒子链，但新的旋转 RPM Hero 仪表只用于四款真实转子，推牌不再把 `ActivitySpeedRadians` 伪装成 RPM。Library/详情面板与 Unity 近景以约 0.3–0.5 秒移动/淡出共同过渡。代盘秘书改为用户显式点击后的慢速运行：四款转子约 2.2 rad/s，第五款缓慢往复；离开详情、切换模型、Reset、失焦、暂停或退出均停止，启动/复位仍为零速度 | `CatalogMapsTheApprovedUnifiedCanyonBackgroundToAllProductScenes`、`EveryProductSceneInstallsItsBackgroundAndHarmonizedModelLights`、`RotarySpeedDashboardAndComboPipelineUseCanonicalSources`、`AssistantDriveIsExplicitSharedAndStopsAtLifecycleBoundaries`、`MagneticSlideTileIsRoutedByTheCanonicalCoordinator` 等；环境专项 5/5、完整 EditMode 118/118 基线通过，报告 `Logs/UnifiedCanyonEnvironmentTests-Final.xml`、`Logs/FullEditModeUnifiedCanyon.xml`；最新 Dashboard 变更随完整 EditMode 138/138 通过，报告 `Logs/SideDashboardFullEditModeTests.xml` | iPhone 上逐款确认岩面接触关系、90°悬浮构图、五种材质曝光与实时色光、Library→详情退景、第五款捏合/视角/滑盖手势仲裁、四款 RPM 仪表与推牌非 RPM 反馈、Combo/粒子、星空闪烁亮度与代盘启停；真机确认前不把视觉和手感标为完成 |
| iOS Release 六层环境加载回归修复 | 待真机肉眼验收 | 真机控制台定位到 `EnvironmentStarfield` 仅由 `Shader.Find` 动态查找、在 Release 构建时被剥离，异常使 `ConfigureDepthLayers` 中断，因而左右前景、石台与环境光没有完成安装。现由 `EnvironmentStarfieldMaterial.mat` 在 `Resources` 中强引用 Shader，运行时从该材质克隆深浅星层；若星空资源意外缺失，只关闭 L0 并继续安装 L1–L5，绝不再阻断主体场景 | 环境专项 5/5、完整 EditMode 117/117 通过；签名 Release arm64 重新导出并覆盖安装到 iPhone「JW」。修复后真机 Release 控制台无 `MissingReferenceException`、无环境资源错误，连续四次模型场景切换正常，设备 thermal state 为 Nominal；证据为 `Logs/SpinnerEnvironmentShaderFixTests.xml`、`Logs/EditModeTests-StarfieldShaderFix.xml`、`Logs/iOSBuild-StarfieldShaderFix.log` | 用户在当前已启动 App 中逐页肉眼确认 L0 星空、L4/L5 前景岩壁、L2/L3 同组视差与环境回光；日志通过不替代视觉验收 |
| 禁止默认自转 | 已集成并有测试 | `RotorRigidbodyController.SetMotorActive` 强制关闭 motor，启动/Reset 归零；`ExplodedViewController` 在零件完全归位前保持运动学状态，恢复物理时再次清零，避免动画搬动动态刚体注入角速度 | `MobilePause_CancelsMotorAndGestureState`、`MobileViewer_EntersPlayModeAndRestoresExplodedPhysics` | 持续保留回归测试 |
| 自由轮 half-life 衰减 | 已集成并有测试 | `FidgetSpinnerMotion.ApplyCoastHalfLife`、`RotorRigidbodyController` | `CoastHalfLife_HalvesSpeedIndependentOfModel`、`CoastHalfLife_NeverCreatesMotionFromRest` | iPhone 手感调参不影响规则完成度 |
| 二维跟手旋转与宽触摸区 | 待真机验收 | 两个模型由唯一 `ResolveTouchResponse(0...1)` 成组派生最大角速、满速手速、加速及制动响应；屏幕速度限制圆心附近角度尖峰，pressure 不参与转速；拖动采用制动快于加速的速度伺服，松手必须满足 28 px / 70 ms / 220 px/s / 62% 同向性且直接设速、不再叠加 impulse；阻力独立映射到 `0.22...12 s` half-life；本次音频改造只记录 release flick force 元数据，未改这些物理/手势参数 | `GestureSpeedMapping_IsDirectionalResponsiveAndClamped`、`TouchResponse_ResolvesOneMonotonicServoProfile`、`ReleaseFling_RequiresDistanceTimeAndConsistentDirection`、`SerializedDefaults_AreDerivedFromTheProductResponseAndResistance`、`BothModelsUseWideTwoDimensionalVelocityResponsiveGestures`；完整 EditMode 92/92 通过 | iPhone 上确认慢拖、小范围输入、快甩、主动减速、方向和阻力两端 |
| 磁吸脱档与低速捕获 | 部分集成 | `RotorRigidbodyController` 的 breakaway、capture、nearest detent snap，并发出 `Breakaway / DetentCrossed / DetentCaptured` | `MagneticBreakaway_UsesAbsoluteFingerVelocity`、`MagneticDetent_RequiresBreakawayAndCapturesAtRest`、`DetentIndex_UsesUnwrappedMechanicalAngle` | 补最终归零/无振荡及语义事件顺序的 PlayMode 测试 |
| 产品总控 + Detent Lab + 逐语义 Core Haptics 编辑器 | 待真机验收 | `DetentTuningPanel` 已从陀螺主界面的独立 `UIHostingController` 与右上角约束中移除，改为设置页内的常驻 Liquid Glass 卡；仍以四个分段按钮热切换 Vault / Camera Dial / Watch Bezel / Silk Ratchet，并显示活动名称、档位/圈、间距和实时 Intensity/Sharpness。日常与高级区明确排除 Detent，避免参数重叠；平滑/棘轮 Tab 仍是唯一机制入口 | `FourDetentPresetsMatchProductTableExactly`、`PresetOverrideChangesOnlyIntensityAndSharpnessAndClamps`、`SettingsPanelSeparatesProductControlsFromSemanticCoreHapticsEditor`、`InteractionTabsResolveToSmoothAndMechanicalPresets`、`RuntimeAndLiquidGlassUi_AreWiredForGrowthAndOfflineReturn`；Swift iPhoneOS typecheck 与完整 EditMode 95/95 通过 | iPhone 确认主界面不再出现 Dent Lab、设置页滚动与四档热切换，并抄回最终滑杆数值；参数曲线尚未进入编辑器 |
| 实时模型横滑选择与方形缩略图 Tab | 待真机验收 | `SpinnerLibrary` 使用分页 `TabView`，滑页通过同一个 `FidgetAppCoordinator` 在经典蓝色、三叶金属、镜钢四翼、石墨双叶与磁吸推牌五个真实 Unity 场景间切换；原页码点已升级为 `SpinnerLibraryThumbnailTabBar`，五个 Tab 都读取对应 Unity Metal 实景渲染的 512 × 512 正方形资源，320–430 pt 宽度下按 44–64 pt 自适应，当前项只用玻璃亮度、柔和投影和底部短条表达，不加周圈描边。触摸 Tab 与横滑继续复用同一 `select(_:)` 路径和 VoiceOver 选择状态。`IosBuildPipeline.ConfigureProductThumbnails` 将资源复制并加入 Xcode 主 target bundle，SwiftUI 以 `UIImage(named:)` 读取，缺图才回退 SF Symbol。推牌详情只隐藏陀螺专属平滑/棘轮模式栏，共享成长与交互反馈仍保留；正式复位按钮静默回到第 3 个中位磁力井 | `NativeUiUsesBundledSquareArtworkForModelTabsAndMetalSkins` 定向 1/1，ProductArchitecture + SpinnerProgression 最终组合回归 51/51，报告 `Logs/SquareThumbnailFocusedTests.xml`、`Logs/SquareThumbnailRegressionTests.xml`；同一源码 Swift iPhoneOS 15 typecheck 通过 | iPhone 上确认五个 1:1 Tab 的实际加载、三叶金属与磁吸推牌缩略图清晰度、320/390/430 pt 间距、横滑/点按同步、VoiceOver、安全区和内存；真机肉眼确认前不称为验收完成 |
| 选择页横滑背景闪动修复 | 部分集成，待自动化与真机验收 | `FidgetAppCoordinator` 不再用 0.16 秒相机投影把模型与统一峡谷背景一起移出屏幕；模型场景改为 `LoadSceneAsync(..., Single)`，旧场景在后台加载期间继续显示，连续快速滑页只保留最后一个 `queuedModelId`，同场景请求也不再重复执行整套 `ConfigureProductScene`。`SpinnerImageBasedLightingController` 按 `BackgroundResourcePath` 缓存背景取色，统一峡谷图每次 App 会话只做一次 GPU `ReadPixels`，避免每次翻页强制同步渲染线程 | `ProductCoordinatorWiresEnvironmentWithoutEnteringInteractionOrHaptics` 已新增异步加载、末次请求合并、禁止同步 `LoadScene`、禁止背景出入场和背景 palette cache 的源级回归断言；Unity 已生成包含 `LoadResolvedModelSceneAsync`、`queuedModelId`、`TryResolvePalette` 与 `CachedBackgroundPalettes` 的 `Assembly-CSharp.dll`。本轮专项 Test Runner 因 Unity 复用失效的 `/tmp/ilpp.sock-82459902276d5e08e7b0a2b4f2bc76a1` 持续等待而中止，未生成 XML，未误报为通过 | 清理或重建受污染的 Unity/Bee 编译状态后重跑环境专项与完整 EditMode；在 iPhone 上连续左右滑动五款模型，确认背景无露黑、无闪动、无明显主线程卡顿且快速连滑最终模型正确 |
| 选择页 ↔ 盘玩页双向连续展示过渡 | 待真机验收 | `SpinnerPresentationTransition` 为五款统一提供 0.42 秒 smoothstep 曲线；`PortraitCameraFramer`、`OrbitPresentationCamera` 与 `EdcPortraitCameraFramer` 都从当前可见姿态捕获起点，同时插值镜头方向/偏航俯仰、距离、缩放和 Core Motion 展示倍率。返回列表时从用户离开盘玩页的最后视角过渡到列表默认构图，进入盘玩页时从列表构图过渡到该模型的详情镜头；若动画中途快速返回或再次进入，新动画直接从当时画面反向，不重跳起点。用户开始捏合或拖动镜头时会接管并终止自动插值。转子/推牌的实际物理停落状态始终保留，系统不写 Rigidbody、角速度、滑盖进度或 Haptic | `ProductCoordinatorWiresEnvironmentWithoutEnteringInteractionOrHaptics` 同时锁定三套相机的同一 API、Slerp/LerpAngle、0.42 秒权威曲线与无 `angularVelocity` 写入；完整 EditMode 123/123 通过，报告 `Logs/FullEditModeLibraryDetailTransition.xml`。同一源码的签名 Release arm64 0.1.0 (6)、274 MiB 已构建、覆盖安装并启动到 iPhone「JW」，Unity 导出证据为 `Logs/iOSBuild-LibraryDetailTransition.log` | 在 iPhone 上逐款确认列表→详情和详情→列表的角度/大小连续性、用户停落姿态衔接、快速反向切页、捏合/拖动接管以及持机倾斜时无跳帧；安装与启动不替代肉眼验收 |
| Quick Start 新手引导、Lv.0–100 成就轨道与 Badge 解锁提示 | 待真机验收 | `ProductUiState` 用版本化 UserDefaults 只在首次进入玩具详情时打开 `SpinnerOnboardingView`，三页覆盖常驻 UI、一指操作/双指捏合/空白拖动、速度力度反馈与停稳约 2 秒评分。底部 LV 卡继续是唯一入口，`ProgressionLevelDetailsSheet` 已拆成“成就 / Badge / 外观”三个栏目：`ProgressionLevelTimeline` 专门显示 Lv.0–100 竖向填充轨道、当前段和向下 shimmer，Badge 图鉴专门显示四类统计与 21 枚徽章，外观栏目专门显示皮肤、配件和贴纸/纹饰。`SpinnerProgressionRules` 仍是四类 21 个 Badge 阈值的唯一权威，动态 payload 同时发布每枚 Badge 的权威解锁位；`ProductUiState` 按模型对已解锁 ID 做持久化差集，多个同时解锁时逐个排队显示全屏 `BadgeUnlockOverlay`，首次升级只建立历史基线而不刷旧提示。`SpinnerProgressionRuntime` 继续按模型持久化 4 cm 外缘最高速度、累计/今日滑动、真实手指接触秒数和累计离线经验 | `BadgeCatalog_UsesIndependentSpeedSwipeTimeAndOfflineMilestones`、`ProgressionRuntime_TracksRealActivityAndDailyGesturesPerModel`、`RuntimeAndLiquidGlassUi_AreWiredForGrowthAndOfflineReturn`；本轮定向 EditMode 17/17、完整 EditMode 123/123 通过，报告 `Logs/BadgeCosmeticsTests.xml`、`Logs/BadgeCosmeticsFullTests.xml`；Swift iPhoneOS 15 typecheck 通过；签名 Release arm64 0.1.0 (4)、274 MiB、Bundle ID `com.jiaweizhou.fidgetspinner.codex` 已覆盖安装到配对 iPhone，构建证据为 `Logs/iOSBuild-BadgeCosmeticsTabs.log`。设备锁屏，按 `--no-launch` 路径安装，未把启动记为成功 | iPhone 解锁后确认三个栏目、成就轨道滚动/shimmer、Badge 点亮/灰态、一次跨多个阈值时逐条提示、离线累计后的新提示、提示安全区与长标题排版；安装不等于视觉验收完成 |
| 三叶金属十档纹路、皮肤、配件与贴纸/纹饰 | 待真机验收 | `ThreeBladeMetalSkinCatalog` 把 Lv.1 / 5 / 10 / 20 / 35 / 50 / 65 / 75 / 90 / 100 映射到雾银喷砂、枪灰拉丝、夜航刻度、钨金蜂巢、冰银回纹、蓝钢大马士革、赤铜电路、钛虹热变、星陨黑曜和镜铬极光十套外观。2026-08-07 根据“主体不变色、只有凸出 element 变色”的真机视觉反馈修正正式绑定：`ThreeBladeMetalSkinProgression` 不再依赖已禁用的旧 `ThreeBladeFrame` 等 Renderer 名称，而是只收集 `RotorDynamic`、`HubStatic` 与 `BearingVisual` 下当前启用的 DragonScale 正式网格，按主体、倒角/轴承、凹槽三个表面角色把 256² Base/Normal 与 URP 金属材质覆盖到转子外壳、三叶、中心盖、轴承、垫圈、倒角和凹槽全部材质槽。旧 Lv.10 凸出刻度、Lv.65 配重块及三叶金属上的通用等级环/轴承球/冠环全部停用；纹样只存在于现有网格的 Base/Normal 表面，不增加任何几何、Collider 或 Rigidbody。Coordinator 按当前等级自动装备最新解锁皮肤；独立 `ProgressionCosmeticsCatalog` 用真实色样分列皮肤、配件、贴纸/纹饰并允许点击已解锁外观。选择写入 PlayerPrefs，锁定项拒绝装备，选择反馈只走 `Selection -> FidgetHapticRouter` 语义链。`HasAppliedSkin` 现在要求每个已绑定的可见 Renderer 材质名都包含活动皮肤 ID，Coordinator 只有整机校验成功才向 SwiftUI 发布 equipped ID；SwiftUI 不乐观改写 equipped ID | 新增 `ThreeBladeMetalSkins_ApplyEveryAuthoredSurfaceWithoutExtraGeometry` 与 `ThreeBladeMetalSkins_TargetEnabledDragonScaleModelInsteadOfHiddenLegacyMeshes`，正式场景定向 EditMode 2/2、SpinnerProgression 30/30、ProductArchitecture + SpinnerProgression 61/61 通过，报告 `Logs/ThreeBladeConformalSkinFocusedTests.xml`、`Logs/ThreeBladeConformalSkinSpinnerProgressionTests.xml` 与 `Logs/ThreeBladeConformalSkinRegressionTests.xml`；同轮 Unity Metal 重绘十张 900 × 1600 预览及十张 512² iOS bundle 缩略图，证据位于 `Artifacts/ThreeBladeMetalSkins` 与 `Assets/Plugins/iOS/Thumbnails/ThreeBladeSkins`。同一源码的签名 Release arm64 `0.1.0 (18)` 已完成 Unity 导出、Xcode 构建、严格签名验证，并覆盖安装和启动到配对 iPhone；设备回读确认 Build 18，20 秒控制台冒烟进入 `applicationDidBecomeActive`、Metal A17 Pro 与 thermal Nominal，无启动异常。证据为 `Logs/iOSBuild-ThreeBladeConformalSkin-B18.log` 与 `Logs/iOSInstall-ThreeBladeConformalSkin-B18.txt` | 在当前已启动的 Build 18 上逐档确认整机而非局部 element 变色、所有表面槽无漏色、旧凸出刻度/配重/等级环/轴承球不再出现、深色皮肤曝光、重启持久化和 Metal 纹理内存；安装和启动不替代真机肉眼验收 |
| 成长等级、AUTO、Combo、旋转评价与离线积累 | 待真机验收 | `SpinnerProgressionRules` 是 Lv.1–100、84,000 XP、主动圈数×滑动力度、5 档装配、9 个小惊喜、16h 离线上限、夜间 25% 和 AUTO 1.0x 的唯一权威；10 段 `SpinnerLevelBand` 同时向 SwiftUI 发布当前称号与等级图鉴。底部成长卡由整块 Button 打开详情，原“标准单列轴承 · 基础合金”单行文案已从所有可见成长界面移除。右侧“代盘秘书”改名 `AUTO` 并使用位于屏幕底部的 SwiftUI `Menu`，系统按可用空间向上展开：1.0x 默认可启动，1.5x 显示 Lv.10 + PRO，2.0x 显示 Lv.20 + PRO，3.0x 显示 PRO；未达到等级时提示等级门槛，达到后仍要求付费凭证。仓库当前没有 StoreKit/IAP 购买与验签链路，因此 PRO 倍率诚实保持锁定，未伪造购买成功或把高倍率接入转子。`SpinnerComboRuntime` 继续以真实角速度、完整滑动力度和独立滑动节奏判级；`SpinnerExperienceFeedbackLayer` 现把轻量 Combo 档位胶囊（含“超频”）独立固定在 3D 模型顶部，紧凑半圆速度 Hero、左右 Intensity / Frequency 从属翼表与 Spin Reward / Peak 反馈留在底部成长卡上方，评价粒子和高速火星继续由 Unity 表达。三表采用 10 pt 间距的同排布局而不重叠；只有主表 Peak 状态变为火红并出现限制在上方弧段的静态火苗轮廓与局部光晕，Peak 反馈不替换主仪表。`SpinnerProgressionRuntime` 仍按模型延迟持久化，Library 预览、无输入运动和 Reset/场景跳变不结算 | 原有成长/Combo 基线为定向 EditMode 17/17、完整 EditMode 123/123，报告 `Logs/NextSkinAutoHudTests.xml`、`Logs/NextSkinAutoHudFullTests.xml`；当前 `SpeedDashboardBands_UseDeterministicFourPercentHysteresis`、`SpeedDashboard_UsesSeparatedCompactHeroSideMetricsAndPeakFlameState` 和 `RotarySpeedDashboardAndComboPipelineUseCanonicalSources` 与 ProductArchitecture / SpinnerProgression 组合 39/39，完整 EditMode 138/138 通过，报告 `Logs/SeparatedFireDashboardEditModeTests.xml`、`Logs/SeparatedFireDashboardFullEditModeTests.xml`；本轮新增静态断言覆盖 Combo 顶部锚点与底部簇移除 Combo 文案，Swift iPhoneOS 15 typecheck 通过。专项 Unity Test Runner 再次被失效的 `/tmp/ilpp.sock-82459902276d5e08e7b0a2b4f2bc76a1` 阻塞，`Logs/ComboTopNavigationFocusedTests.log` 已留证但未生成 XML，未误报为通过 | iPhone 上同时确认 Combo /“超频”位于模型顶部且不碰模式栏、三表不重叠、Peak 火红/火苗/光晕、AUTO 菜单实际向上展开、1.0x 启停、停止项、Lv.10/Lv.20 门槛提示和 PRO 文案；真正出售 1.5x/2.0x/3.0x 前仍需实现 StoreKit 商品、购买、恢复、服务端/本地验签与退款撤销生命周期 |
| Combo 顶部字体增补（本行覆盖上一行的“轻量”字号描述） | 待真机验收 | 模型顶部 `ProductStatusPill` 继续通过 `Font.product` 使用最新置入的 Oxanium，可缩放字号从共享默认 `caption2` 提升为独立 `title3` bold；共享状态 Chip 的其余调用不受影响 | `RuntimeAndLiquidGlassUi_AreWiredForGrowthAndOfflineReturn` 新增 feedback layer 局部字体断言；Swift iPhoneOS 15 typecheck 通过。2026-08-06 同一源码已进入 Release arm64 0.1.0 (13)，Xcode 编译 Swift、签名和 bundle validation 成功，覆盖安装并启动到 iPhone「JW」；随后 `devicectl device info apps` 回读确认设备上的 Bundle ID、版本和 Build 均匹配 | iPhone 上确认中英文级联、Dynamic Type、320–430 pt 屏宽、长 Combo 数字以及与模型/模式栏的间距；安装与启动不替代肉眼验收 |
| Combo 数量分级庆祝与数字跳变（本行覆盖上一行的静态 `ProductStatusPill` 描述） | 待真机验收 | 顶部改用产品专属 `RewardingComboPill`，不改 `SpinnerComboRuntime`、XP、物理、输入或 Haptic 语义。`顺流 / 强驱 / 超频` 继续表示操作质量并控制名称/颜色，count 独立控制 2–4 点燃、5–9 升压、10–19 爆发、20+ 峰值四级演出；普通增长只做 45 ms 蓄力、旧数字上移、新数字从下方进入和 spring 落定，5 次扫光、10 次光环与 4 枚短火花、20 次及之后每 10 次播放 0.32 s 峰值短爆。数字使用固定 52 pt 区、Oxanium Bold 等宽数字，胶囊仅轻微缩放；`ComboPresentationKey(count:tier:)` 保证 20 Hz 转速/强度/频率 telemetry 不会重启动画，generation token 在快速增长时直接追最新值。Reduce Motion 改为 0.11 s 纯交叉淡化并禁用位移、缩放、扫光、光环和火花；断连只做 0.22 s 非惩罚淡出，展示层没有直接 Haptic 或音频调用 | `ComboPresentation_UsesCountLevelsMilestonesAndAccessibleIos15Fallback` 已加入静态验收，锁定门槛、里程碑、缩放、固定数字区、iOS 15 fallback、Reduce Motion、顶部锚点及无直接反馈调用；主代理独立复跑 iPhoneOS 15 `swiftc -typecheck` 通过。Unity 聚焦批处理仍被既有失效 `/tmp/ilpp.sock-82459902276d5e08e7b0a2b4f2bc76a1` 阻塞在导入重试，未进入测试执行且未生成 XML；证据为 `Logs/ComboPresentationFocusedTests.log`，未误报为通过。2026-08-07 同一源码完成 Unity Release 导出、IL2CPP、Xcode arm64 Swift/原生编译、签名与 bundle validation；Fidget Spinner 0.1.0 (16) 已覆盖安装到 iPhone「JW」，本地严格签名验证与设备已安装 App 回读均通过。设备锁屏，按 `--no-launch` 安装，未把安装误报为启动 | 解锁后启动 Build 16，确认 2→5→10→20→30 的层级差、9→10 与 19→20 不抖宽、快速连续增长不落后、tier 升降不重复换数字、火花不遮模型、破连不过度惩罚，以及 Reduce Motion、VoiceOver、320–430 pt 与热功耗；安装不替代真机视觉验收 |
| AUTO 四档真实速度（本行覆盖上方“高倍率锁定/PRO”描述） | 待真机验收 | `AssistantDriveSpeedRules` 成为 1.0x / 1.5x / 2.0x / 3.0x 的唯一倍率与基准速度来源：旋转模型以 1.0x = 2.2 rad/s 得到 2.2 / 3.3 / 4.4 / 6.6 rad/s，磁吸推牌以 1.0x = 0.030 m/s 得到 0.030 / 0.045 / 0.060 / 0.090 m/s。SwiftUI `Menu` 四档均可直接选择，不再显示等级、PRO、StoreKit 或锁图标；倍率字符串经不变区域格式发送到 `FidgetAppCoordinator`，只接受四个明确值，Unity 同时把当前权威倍率随成长状态回传，按钮和勾选状态不依赖单边假状态。经典转子原 6 rad/s 上限与 Rigidbody 转子原 50% 上限已移除，EDC 原硬编码速度改为运行目标；切换倍率只改变当前目标，不重复发放启动经验。停止、进 Library、切模型、失焦、后台和销毁会停止 AUTO 动力并把倍率复位到 1.0x，旋转模型按既有自由滑行阻尼衰减；Reset 仍明确把角速度归零。AUTO 仍不读取藏家手动经验加成，也未新增原始输入到 `IosHaptics` 的调用 | `AssistantDriveMultipliersScaleTheOneXBaseline` 四组参数、`AssistantDriveRejectsUndefinedMultiplier`、`AssistantDriveIsExplicitSharedAndStopsAtLifecycleBoundaries` 与 `RuntimeAndLiquidGlassUi_AreWiredForGrowthAndOfflineReturn` 覆盖倍率计算、非法值、三类机制、双向 native bridge、菜单无锁和生命周期；ProductArchitecture + SpinnerProgression 定向 60/60、完整 EditMode 169/169 通过，报告 `Logs/AutoMultipliersFocusedTests.xml`、`Logs/AutoMultipliersFullEditModeTests.xml`。同一源码通过 iPhoneOS 15 Swift typecheck。测试前按 `recover-unity-builds` 流程隔离失效的生成型 Library/Temp；重建后确认旧 ILPP socket 问题来自受限执行环境，沙箱外 Test Runner 正常生成 XML | 在支持 Core Haptics 的 iPhone 上逐款确认四档均可点、选中倍率回显正确、旋转/推牌速度按比例提升、运行中热切档无停顿、停止后不再持续加速而是自然衰减，以及锁屏/后台/Reset/切模型后不自行恢复；自动化与类型检查不替代真机速度、温升和手感验收 |
| 五款统一峡谷背景、岩面承托、背景驱动环境光与六层视差 | 待真机验收 | 五款场景统一使用 1882 × 3344 低饱和、粗石、浅景深夜景资源，获批背景本身包含与山体连续的岩面承托；程序生成的石台/圆托永久隐藏，避免出现第二种材质。两张 1882 × 3344 透明粗粝岩壁继续与双层动态星空组成 L0–L6 深度结构；主体与锚点仍使用 14 pt 位移，近景岩壁为 22/30 pt，UI 固定屏幕。`SpinnerImageBasedLightingController` 作为独立环境适配层，从统一背景提取低频反射环境，以五款各自的 Library 灯光/反射尺度保留材质颜色，并让模型主色实时驱动中央径向主体光、压扁在岩面上的接触光和两侧岩壁回光；详情页恢复原始曝光。视觉视差继续复用现有 60 Hz Core Motion 生命周期，以进入页面姿态归零，roll 映射水平、pitch 为水平幅度的 60%，±15° 满量程并软钳制，0.045 dead zone、6.32 s⁻¹ 低通平滑；桌面使用鼠标 fallback。原生桥接 `UIAccessibilityIsReduceMotionEnabled`，开启“减弱动态效果”时视觉层归零，只保留克制的呼吸高光；页面失焦或进入后台时既有运动更新会停止。全部视觉层使用 transform，不重绘位图，也不写转子物理、交互或 Haptic | `CatalogMapsTheApprovedUnifiedCanyonBackgroundToAllProductScenes`、`EveryProductSceneInstallsItsBackgroundAndHarmonizedModelLights`、`BackgroundPaletteAndGroundingMesh_AreDeterministicAndMaterialDriven`、`ProductCoordinatorWiresEnvironmentWithoutEnteringInteractionOrHaptics`、`ParallaxMathUsesDeadZoneExponentialSmoothingAndPixelAccurateProjection`；专项 5/5、完整 EditMode 118/118。十张 900 × 1600 Unity Metal 预览保存在 `Artifacts/EnvironmentIntegration`，测试报告为 `Logs/UnifiedCanyonEnvironmentTests-Final.xml`、`Logs/FullEditModeUnifiedCanyon.xml` | iPhone 上逐页确认岩面与模型的距离、近景遮挡、90°构图、2×清晰度、安全区无露边、五款材质曝光、模型色光晕与岩面接触光、Reduce Motion、60 fps、纹理内存和温升；完成真机肉眼与性能检查前不称为验收通过 |
| 三叶金属正式视觉模型、圆帽与连接件 | 待真机验收 | `ProceduralMeshFactory`生成120°七边尖翼、四段倒角、浅三角暗腔、24齿×6采样中心帽、独立上下盖/垫片/轴承内外圈、8球合并Ball Cage与黑色顶部连接环；`RadialBrushedMetal`负责中心盖径向拉丝，`MetalGlintController`只读实际角速度和Breakaway/Capture语义，用MaterialPropertyBlock驱动局部倒角反光；HDR、Bloom、Post Processing和实时Reflection Probe保持关闭 | `TopCap_HasTwentyFourWaveTeethAndUsesSimplifiedCollision`、`MobileMeshes_StayInsideTriangleBudgetAndProvidePbrChannels`、`MobileRenderers_StayInsideDrawCallAndMaterialBudgets`、`ReferenceProportions_CenterCapIsAboutHalfTheFrameWidth`、`MetalGlint_UsesRealSpeedAndResetReturnsToDark`、`BladeGroove_ReusesTheExistingPolishedSubmesh`；静态审计为9,666 tris / 17,044 vertices / 15 estimated draws / 6 materials / 3.34 MiB generated textures；完整EditMode 92/92通过 | 固定Hero/Top/Side/Exploded图已生成；两张贴图无法提供实物尺寸、公差、背面螺纹和材料牌号，需CAD/卡尺数据后才能工业级校准；iPhone上确认拉丝摩尔纹、高光闪烁和曝光 |
| 镜钢四翼第三款 FBX 模型 | 待真机验收 | 用户提供的 114 MiB / 1,496,667 tris FBX 完整保存在 `Assets/_ImportedSpinner/Models/ImportedSpinner.fbx` 作为源文件，但场景依赖明确排除它；运行网格先焊接原 UV 岛造成的重复顶点，再以 8 次保体积 Humphrey smoothing 清除几何高频噪点，得到 180,000 tris / 90,013 vertices / 单 renderer。FBX 内嵌的 4K PBR 贴图继续保留为源资产，但按最新外观规范，运行材质不引用 Base/Normal/Roughness 贴图，也不需要 UV：URP Lit 使用中性冷银灰、Metallic 1.0、统一 Smoothness 0.95；运行网格关闭压缩并使用面积+角度加权法线，避免镜面高光放大顶点量化误差；无噪声冷白 softbox cubemap 改为连续世界方向灯带，避免六个面的重复高光和接缝，同时提供克制反射，无微颗粒、划痕、噪点或局部粗糙度变化。第三场景复用 `RotorRigidbodyController`、`MobileGestureController`、语义 Haptic 和 Core Motion，并隐藏会遮住原模型中心的通用灰色轴承盖。Hero/Library 距离独立设为 0.36 m | `ImportedThirdSpinnerUsesOptimizedRuntimeMeshAndCanonicalInteraction`、`BuildContainsAllFourSpinnerModelsInOneProduct`；自动验证锁定无贴图依赖、无网格压缩、面积+角度加权法线、平滑顶点法线、无 Normal/MetallicGloss 关键字、Metallic/Smoothness、中性颜色和固定 studio reflection；900×1600 Hero 图已重生成；完整 EditMode 92/92、签名 Release arm64 构建与覆盖安装通过 | 仍须在 iPhone 确认镜面反射不过曝、轮廓可读性、触控热区、60 fps、温升和模型切换；真机完成前不称为视觉验收通过 |
| Meshy 七层 EDC 六档双向磁吸推牌 | 待真机验收 | 源 FBX、七层结构、PBR 和 1,994,857 tris 正式网格保持不变。`LinearMagneticDetentProfile` 是六枚磁体、68 mm 总行程、视觉沉降与 Haptic 的唯一来源，档位为 `0/13.6/27.2/40.8/54.4/68.0 mm`，默认停在第 3 档 `27.2 mm` 并映射为零视觉偏移，因此首次触摸即可向左 27.2 mm 或向右 40.8 mm 双向脱档。Reset 静默回到该中位井。`MagneticDetentTrack1D` 以最大 `1/240 s`、每帧最多 8 子步实现 `Captured→Loading→Breakaway→Traveling→Capturing→Captured`；重磁参数升级为 55 g 质量、125 N/m 手指耦合、4.1 Ns/m 手指阻尼、0.62 N 脱档、0.58 N 正弦磁峰值、0.085 N 摩擦和 0.30 Ns/m 轨道阻尼，捕获后位置与速度严格归零。预压从 5% 负载启动，Intensity `0.20→0.54`、Sharpness `0.12→0.28`。每个经过授权的真实 `DetentCrossed` 直接使用与默认 Camera Dial 陀螺完全相同的 `1.00/0.72` isolated transient；旧推牌专用 Pattern、动态输出增益、尾脉冲和冲击叠层全部移除，也不套用旋转高速限流。`MagneticSlideDetentAudio` 继续只消费同一 `DetentCrossed`，通过 6 个预分配 2D 声部播放用户选定的 766 Hz 合金 click（48 kHz mono、0.93 s 容器，主要击发集中在前约 0.14 s）；`Breakaway`/`DetentCaptured` 不补第二声，Library/AUTO/Reset/程序设姿静默，推牌不受旋转 Detent Lab 覆盖。详情相机改为无横向透视压缩的正面 + 30° 顶视，长轴严格水平、目标占屏宽 72%；Library 用独立 `1.59×` zoom 保持预览尺度。随滑盖移动的 raycast 触摸体从 `82 × 20 × 50 mm` 扩为 `94 × 32 × 58 mm`，只承担命中与手势仲裁，不进入质量、磁力或档位积分 | 重磁/Haptic 专项 EditMode 21/21、此前完整 EditMode 147/147 通过，报告 `Logs/MagneticSliderLongThrowHeavyDetentTests.xml`、`Logs/MagneticSliderLongThrowHeavyDetentFullEditMode.xml`；镜头/交互专项 21/21 通过，锁定 68–74% 占屏、水平滑轨和扩大命中体，报告 `Logs/EDCFrontTopExpandedInteractionTests.xml`。本轮换音验收 21/21、完整 EditMode 160/160 通过；`AlloyClick766HzAudio_IsWiredToAuthorizedDetentCrossingsOnly` 与 `AlloyClick766HzAudio_HasOneTransientAndNoSecondClick` 锁定新资源、6 声部、单瞬态和无捕获补音，报告 `Logs/MagneticSlideAlloyClick766Tests.xml`、`Logs/MagneticSlideAlloyClick766FullEditMode.xml`。架构测试继续锁定推牌跨档必须调用 isolated transient 且不得回退到 Pattern。场景重建锁定 6 枚磁体位于 `-34/-20.4/-6.8/6.8/20.4/34 mm` 以及新镜头/触摸体，证据为 `Logs/EDCFrontTopExpandedInteractionRebuild.log`；1290 × 2796 构图验证图为 `Artifacts/EDC/Final_iPhone_Portrait.png`。包含新音效的签名 Release arm64 0.1.0 (15) 已于 2026-08-06 完成 Unity、IL2CPP、Objective-C++、Swift 和 Xcode 编译并覆盖安装到配对 iPhone「JW」；本地签名、包内音效标识与设备 Bundle/Build 查询均通过，构建证据为 `Logs/iOSBuild-MagneticSlideAlloyClick766.log`。设备随后解锁，`devicectl` 已成功启动 Build 15 | 必须在支持 Core Haptics 的 iPhone 对比其他陀螺，确认正面 + 顶视构图、72% 主体尺寸、滑盖边缘外扩命中区、首次按下成功率和水平双向拖动；同时完成双向慢推、快速全程、阈值轻压、松手吸附和连续 20 次往返。13.6 mm 六档盲辨、0.62 N 跨档势垒、单触点力度、766 Hz 合金 click 音量、无双击/漏击、视觉/声音/Haptic 同帧、后台/engine reset 均尚待本版人工验收。正式网格仍超移动端目标，材质统一与 30 分钟性能验收仍待完成 |
| 推牌 Core Haptics 最大参数增补（本行覆盖上一行的 `0.54/0.28` 与 `1.00/0.72` 旧值） | 待真机验收 | `LinearMagneticDetentProfile` 的代码默认、`ApplyHeavyDefaults()` 与已生成 ScriptableObject 同步更新：预压仍从 5% 负载启动并由 `Intensity 0.20 / Sharpness 0.12` 线性升至 Apple 事件参数上限 `1.00 / 1.00`；每次经机制授权的 `DetentCrossed` 继续只发一个 isolated transient，但改为 `Intensity 1.00 / Sharpness 1.00`。没有新增原始输入到 `IosHaptics` 的调用，也没有把 30 次/秒参数更新率伪装成硬件振动 Hz；无 Core Haptics 时既有 UIKit fallback 会以 Heavy + intensity 1.0 输出 | `HeavyProfile_IsTheSingleSixDetent68MillimeterSource`、`MagneticProfile_DefinesSixHeavyDetentsAnd68MillimeterTravel` 已同步锁定四个上限值；Swift iPhoneOS 15 typecheck 通过。Unity Test Runner 仍受本页既有 ILPP socket 阻塞，尚无本轮 XML，不误报为自动化通过 | 必须在支持 Core Haptics 的 iPhone 上确认预压峰值、六个跨档触点、连续快速往返、系统 Haptics 开关、后台/engine reset 与热功耗；`1.00 / 1.00` 是 API 参数上限，不承诺每款 iPhone 的物理位移相同 |
| 推牌预压整体增强（本行覆盖上一行的 `0.20 / 0.12` 起始值） | 待真机验收 | 不改变 5% 负载触发、线性插值、30 次/秒更新、脱档停止和单次最大跨档 transient 的节奏；只把预压整条曲线上抬为 `Intensity 0.45→1.00 / Sharpness 0.30→1.00`，因此轻压与中段更明显，终点仍受 Apple `1.00 / 1.00` 上限约束 | 代码默认、`ApplyHeavyDefaults()`、生成的 `LinearMagneticDetentProfile.asset` 及两项 EDC 接受测试同步更新。2026-08-06 的聚焦 Test Runner 再次被失效的 `/tmp/ilpp.sock-82459902276d5e08e7b0a2b4f2bc76a1` 阻塞，证据为 `Logs/ComboPushHapticsFocusedTests.log`，未生成 XML，未误报为通过；同一源码已完成 Unity Release 导出、IL2CPP、Xcode arm64 签名构建，0.1.0 (13) 覆盖安装并启动到 iPhone「JW」，本地 `codesign --verify --deep --strict` 与设备已安装 App 回读均通过 | iPhone 上比较轻压起振、中段蓄力、脱档停振和跨档“啪”是否保持原节奏，并确认连续往返不会疲劳或发热；安装与启动不替代触感验收 |
| 石墨双叶第四款程序化模型 | 待真机验收 | `TwoLobeBarSpecifications` 是 50 × 18 × 13 mm、3.5 mm 圆边及末端过渡、2.3 mm 端面内缩、3.2 冠形指数、Ø24 mm 中心按钮、1.5 mm 凹碟和 3 mm 凸高的单一尺寸来源；偏角为 0°，`TwoLobeBarMeshFactory.CreateBody` 生成一根连续长条主体，以短卷边末端取代两块分离 stadium 半身。URP Lit 采用 `#3A3D40`、Metallic 1.0、Roughness 0.76（Smoothness 0.24）、各向同性珠砂法线和按钮径向 AO；场景只含一个左上方宽角 soft-shadow key light。`TwoLobeBar.unity` 复用 `RotorRigidbodyController`、`MobileGestureController`、统一语义 Haptic、Reset 与成长装配，初始及复位角速度为零 | `DimensionsAndPbrValues_MatchTheAuthoredSpecification`、`ProceduralMeshes_PreserveContinuousBarAndConcaveDishBounds`、`Scene_HasOneContinuousBarStationaryButtonAndCanonicalInteraction`、`MaterialAndStudio_UseGraphiteBeadBlastAndOneSoftKey`、`ProductRegistrationSources_ContainTheGraphiteModel`、`BuildContainsAllFourSpinnerModelsInOneProduct`；本模型 5/5、完整 EditMode 106/106 通过；Swift iPhoneOS 15 typecheck 通过；签名 Release arm64 已覆盖安装到 iPhone | iPhone 上确认连续长条轮廓、短卷边端面、凹碟与窄边环可读性、较粗珠砂不闪烁、宽柔高光、触控热区、自由轮手感、60 fps 与温升；真机完成前不称为视觉验收通过 |
| 三叶金属物理驱动棘轮音频 | 待真机验收 | 已删除旧单文件和 native `audioCustom`；5 个 mono PCM variant 均为单枚咬合、48.6...51.5 ms、首部活动 <2.3 ms、尾部 padding <3 ms。`RotorRigidbodyController` 逐个枚举同帧跨过的 detent index，并为每个 index 发一次 `RatchetDetentCrossed`；renderer 严格执行一次 `PlayOneShot`。速度音量从慢速 1.0 反向映射到高速 0.34，flick 对前 5 击递减增益；variant round-robin，每击随机 ±1...2 半音并高速上扬 0...1；12 个预分配 2D 声部，无 Update、gate、rate limit、scheduler 或高转速切换 | `RatchetAudioVolume_IsFullAtSlowSpeedAndFallsAtHighSpeed`、`RatchetAudioVariants_RoundRobinWithoutImmediateRepeat`、`RatchetAudioPitch_UsesRandomOneToTwoSemitonesPlusSpeedRise`、`RatchetAudioCrossings_CountEveryDetentInEitherDirection`、`RatchetAudio_UsesFiveAtomicVariantsTwelveVoicesAndOneListener`、`RatchetAudioIsPhysicsDrivenAtomicPolyphonicAndNeverScheduled`；完整 EditMode 92/92 通过 | iPhone 听辨点击密度是否贴合真实减速曲线、每击响度变化、高速自然金属 whir 与媒体音量/静音模式 |
| 平滑 / 棘轮模式 Tab | 待真机验收 | `ProductModeBar` 保留四款陀螺的唯一机制入口与既有 `SetInteractionModeFromNativeUi` → `ResolveInteractionPreset` 链路；第五款 `magnetic-slide-tile` 固定为六档重磁机构，进入详情时只隐藏 mode bar，仍保留共享成长/反馈层，旋转设置不会写入其 Profile | `InteractionTabsResolveToSmoothAndMechanicalPresets`、`SwiftModeFallbacksMatchRuntimePresetSource`、`MagneticSlideUsesMechanismSemanticsAndIndependentNativePreloadPlayer`；Swift iPhoneOS 15 typecheck 与 ProductArchitecture 21/21 通过 | iPhone 上确认四款模式栏行为不变、第五款不显示模式栏且仍能看到共享反馈；经典蓝色真实磁吸运动尚未迁移 |
| Liquid Glass 原生组件规范 | 待真机验收 | 已删除 `ProductBottomBar` 与对应 `bottomController`；`ProductTopBar` 右上角已移除冗余“玩具”列表图标，只保留独立 38 pt “设置”玻璃图标，详情页左上返回仍通过 `showMySpinners()` 回到模型库。顶部不再绘制横贯屏幕的玻璃底色；活动玩具中央按 `LV 当前等级` / 产品名称 / 当前皮肤三行显示，皮肤名称和淡 tint 只读取 Unity Renderer 已确认的 `equippedThreeBladeMetalSkinId` 及目录色，其他模型回退权威阶段材质。`ProductModeBar` 与底部 `SpinnerProgressionHUD` 同样读取当前装备色并显著降低透明度，选中态仍以白色为主；全局固定青/蓝背景光已改为中性黑灰。底部成长卡改贴 `safeAreaLayoutGuide.bottomAnchor`，设置/模型面板占用原底栏空间。iOS 26 继续使用 `glassEffect`，旧系统回退为带低透明度 tint、无周圈描边的 `ultraThinMaterial`；选择态依靠玻璃亮度、tint、tag 与 checkmark 表达，不能再用高饱和线框包围整张卡。Quick Start 文案同步到新导航结构 | `NativeUiUsesLivePagedModelsLiquidGlassAndModeTabs` 已新增 ProductTopBar 局部断言，确保右上“玩具”入口不会回归且设置/返回链路保留；历史 ProductArchitecture 19/19、完整 EditMode 123/123，报告 `Logs/OpalHudProductArchitectureTests.xml`、`Logs/OpalHudFullTests.xml`；本轮 Swift iPhoneOS 15 typecheck 通过。专项 Unity Test Runner 的相同 ILPP 阻塞证据见 `Logs/ComboTopNavigationFocusedTests.log`，未生成 XML，未误报为通过；0.1.0 (7) Release arm64、274 MiB、Bundle ID `com.jiaweizhou.fidgetspinner.codex` 已覆盖安装到配对 iPhone，构建证据 `Logs/iOSBuild-OpalHud.log`；采用 `--no-launch`，安装未记为视觉验收 | iPhone 上确认顶部安全区、标题与右侧设置图标不碰撞、详情页返回路径、Combo /“超频”顶部位置、皮肤名确实随装备即时变色、模式栏宽度、玻璃在五款模型亮度下的低对比可读性，以及底部成长卡不会压住 Home Indicator |
| Opal / Mobbin 研究与可复用原生组件库 | 待真机验收 | Jobs 通过用户已有 Mobbin 登录态交叉检查 Opal 的 208 screens、208 UI elements 和 62 flows，研究证据与 screen URL 记录在 `Docs/OpalMobbinUiResearch.md`。`FidgetProductUIComponents.swift` 是独立、无 `UnityBridge` 的视觉层，除原有 token、背景/玻璃、导航、分段、分页、操作、卡片、sheet、pill、进度和三联仪表外，本轮补齐 `ProductScreenHeading`、`ProductNoticeBanner`、`ProductInlineTag`、`ProductSelectionCard`、`ProductBadgeTile`、`ProductCompactMetric`、`ProductSliderRow`、`ProductToggleRow` 与 `ProductEmptyState`。`CodexSwiftUIOverlay.swift` 已把 Quick Start 页码与主操作、Badge / 藏家通知、模型库与收藏标题、外观/等级选择行、Badge tile、全部设置滑杆/开关、触觉紧凑指标和空状态接到共享组件；业务层只保留状态绑定、Unity 调用和与具体玩具直接相关的专用视觉。字体继续使用默认字距，运行时无 `.tracking` / `.kerning`；未复制 Opal 宝石资产、品牌文案或产品逻辑，也未新增原始输入到 `IosHaptics` 的调用。最新无描边材质修正覆盖全局 `ProductGlassModifier`、`ProductNoticeBanner` 与 `ProductSelectionCard`：iOS 26 使用原生 glass，iOS 15–25 使用带 tint 的 `ultraThinMaterial`，两条路径都不画周圈 stroke | `NativeUiUsesReusableProductComponentLibrary` 等五项专项 5/5、ProductArchitecture + SpinnerProgression 45/45、最新完整 EditMode 147/147 通过，报告 `Logs/UnifiedComponentGaugeFocusedTests.xml`、`Logs/UnifiedComponentGaugeEditModeTests.xml`、`Logs/MagneticSliderLongThrowHeavyDetentFullEditMode.xml`；iPhoneOS 15 Swift typecheck、组件库 JavaScript 语法与 Chromium 760 px 布局截图检查通过 | iPhone 上确认全套组件在模型库、Quick Start、成长详情、Badge、外观、设置、通知与 dashboard 的一致性，以及 38 pt 图标的 44 pt 热区、VoiceOver、Reduce Transparency、bottom sheet 安全区和五款模型明暗背景下的玻璃对比度；尤其检查无描边玻璃在浅色 3D 高光上的边界可读性，真机肉眼完成前不把视觉验收标为完成 |
| Oxanium、Dark Mode 与统一设计系统 | 待真机验收 | Google Fonts 官方 Oxanium 200–800 可变 TTF 与 SIL OFL 已固化到 `Assets/Plugins/iOS/Fonts`，不依赖网络。`ProductTypography` 统一 SwiftUI 语义字号、Dynamic Type、Core Text 注册兜底和 UIKit navigation title；7 个 `UIHostingController` 根层全部应用 `productDesignSystem()`，两个 Swift 文件共 130 个显式 `.font` 均已改走 `Font.product`，无 `.font(.system...)`、`.tracking`、`.kerning` 或固定 `Color.cyan`。共享组件默认中性白色，状态色按当前装备材质或真正语义指标注入。Oxanium 不含中文字形，中文由 Core Text 自动级联 iOS 系统中文字体；拉丁和数字保持 Oxanium。产品通过生成 plist 的 `UIUserInterfaceStyle=Dark`、UIKit Overlay 容器与 SwiftUI `productDesignSystem()` 固定深色，但不再改写 Unity 根 Window / Controller appearance。首页黑屏回归已修复：`ProductPanel` 在模型库分支保持透明，让实时 Unity 模型透出，只在上下保留低透明黑色渐变；设置与藏家页面继续使用完整黑色 `ProductBackdrop`。iOS pipeline 还将同一 TTF 复制到主 target Resources 并写入 `UIAppFonts`。三叶金属与镜钢四翼场景的 12 个 legacy `UnityEngine.UI.Text` 已绑定同一 Font asset，`ThreeBladeSceneBuilder` 重建时也不再回退 `LegacyRuntime.ttf` | `EntireProductUiUsesOxaniumAndTheSharedDesignSystem`、`EntireProductUiDefaultsToDarkAppearance` 与组件库专项纳入完整 EditMode 149/149，报告 `Logs/DarkModeTransparentStageFullEditModeTests.xml`；iPhoneOS 15 Swift typecheck 通过。签名 Release arm64 0.1.0 (11) 已验证 app bundle 内 `UIUserInterfaceStyle=Dark`、`UIAppFonts`、Oxanium TTF 与源文件逐字节一致，Bundle ID 与 Team 签名正确；Unity 导出证据为 `Logs/iOSBuild-DarkModeTransparentStage.log`。修复包已覆盖安装并在配对 iPhone 上启动，Metal A17 Pro、场景激活和资源卸载日志均正常且无启动异常 | iPhone 上肉眼确认首页实时模型、顶部/底部渐变、分页与进入按钮可见；再逐页确认设备 Light Mode 下其余页面保持黑底白字，并检查 Oxanium 字重、Dynamic Type、中英文 fallback、Alert/Menu/Picker、legacy HUD 和 Reduce Transparency。真机肉眼完成前不把视觉验收标为完成 |
| 半圆实时速度仪表盘 | 待真机验收 | `ProductSpeedDashboard` 已进入共享 SwiftUI 组件层，在三表簇中自适应为 124–160 × 112 pt，以真正 180° 圆弧、13/7 根自适应刻度、单层 `ProductDashboardSweepField`、可缩放等宽 headline 和 Reduce Motion / Reduce Transparency 分支显示实时转速。扫掠扇区由左侧零点延伸到当前比例，扇区的终止径向边就是指示位置；同一张 `RadialGradient` 从圆心完全透明连续增强到外缘实色，因此不再叠加活动弧、独立针线或中心针轴。左右各一枚 64–74 × 72 pt `ProductSideMetricDashboard`，三表同排保持 10 pt 间距且不重叠；三枚表都把 headline 数字与单位放在半圆内部，把 Intensity / Speed / Frequency 名称留在各自半圆下方并缩小为 `caption2`。翼表分别显示真实 `combo.intensity` / `combo.frequency`，继承主速度带但降低亮度与字号，不从 RPM 推导。Peak 保持火红；只有主表沿上方弧段生成 5 枚静态火苗轮廓和局部光晕，不使用独立 Timeline 或随机 flicker，Reduce Transparency 下取消 blur / shadow。`SpinnerSpeedDashboardRules` 仍使用 Calm / Flow / Drive / Peak 的 25% / 55% / 80% 确定性进入阈值与 4% 回差；`ProductMotionTelemetryNativeBridge` 从四款旋转机制按既有 `SpinnerComboRules.FullScaleAngularSpeed = 30 rad/s` 归一化并以 20 Hz 只读发布，第一次输入即可更新，Reset / Library / scene destroy 显式清零。磁吸推牌明确不把 `ActivitySpeedRadians` 伪装成 RPM。组件、bridge 和 UI 都不写角速度，也未新增任何直接 Haptic 调用 | `SpeedDashboard_UsesSeparatedCompactHeroSideMetricsAndPeakFlameState`、`RotarySpeedDashboardAndComboPipelineUseCanonicalSources` 已锁定单层扫掠场并禁止 `ProductDashboardNeedle` 与 `.trim` 活动弧回归；ProductArchitecture + SpinnerProgression 定向 52/52、完整 EditMode 160/160 通过，报告 `Logs/RadialSweepDashboardFocusedTests.xml`、`Logs/RadialSweepDashboardFullEditModeTests.xml`；iPhoneOS 15 Swift typecheck 通过。同一源码的 Release arm64 Build 13（0.1.0、303 MiB、Bundle ID `com.jiaweizhou.fidgetspinner.codex`）完成 Unity 导出、Xcode 签名并覆盖安装、启动到 iPhone「JW」，Unity 证据为 `Logs/iOSBuild-RadialSweepDashboard.log`；设备回读 PID 14375 持续运行，短时启动控制台进入 `applicationDidBecomeActive`，无 Swift crash、C# Exception、MissingReference 或资源缺失 | 用户在当前已启动 App 中确认 20 Hz 响应、首次输入、Reset 归零、4% 色带回差、三个指标独立跟随、三表不重叠、中心到外缘无透明/实色分界、扫掠终止边无超调、Peak 火红/静态火苗/光晕、320–430 pt 不遮挡 Hero、VoiceOver、AX 字号、Reduce Motion / Transparency、五款背景对比和热功耗；启动日志中的 `ProductStickerVisual` 凹 MeshCollider 警告与仪表无关，但仍需另行清理；肉眼确认前不把视觉验收标为完成 |
| 独立 Haptic Recipe | 已集成并有测试 | `FidgetHapticRecipeLibrary` 按 Selection、Detent、Breakaway、Capture、Release、Reversal、Reset、Shake、Button、Pop、Collision 分别解析 Recipe；Native UI override 不改变语义身份 | `ProductRhythm_ChangesCadenceWithoutReplacingRecipeIdentity`、`SpeedFollow_OnlyModulatesMappedMechanicalEvents`、`RecommendedMechanicalRecipesAreStrongAndKeepSemanticIdentity` | iPhone 盲测各语义辨识度 |
| Native 按 semantic Recipe 生成不同波形 | 待真机验收 | `CodexIosHaptics.mm` 为 Detent/Inertia 提供 isolated transient；其他语义支持 Transient / Continuous / Hybrid、ADSR、Sustained、五个 Dynamic Controls、pulse 和 layer。一个持久 engine 同时管理互不抢占的旋转高速 `gContinuousPlayer` 与推牌预压 `gMagneticPreloadPlayer`，两者都有独立 start/update/fade-stop/request/generation，并在 active 状态的 reset/stopped 后按请求恢复 | `NativeRendererUsesWaveformEnvelopeAndAllHapticDynamicControls`、`DetentAndInertiaUseIndependentIsolatedTransientChannels`、`MagneticSlideUsesMechanismSemanticsAndIndependentNativePreloadPlayer`；iPhoneOS SDK Objective-C++ syntax check | iPhone 上确认真实输出、两套 continuous 可独立停止、后台/engine reset 恢复、强度、混合和 fallback |
| Detent Haptic 跟随实际转子档位 | 待真机验收 | `DetentFeelConfig { detentsPerRev, intensity, sharpness }` 是唯一活动配置；预设切换同时更新三叶磁性档位、经典档位检测和 Haptic。每次实际跨档只发一个最终值 transient，不再应用全局力度、速度倍率、节奏或 impact layers | `FourDetentPresetsMatchProductTableExactly`、`PresetOverrideChangesOnlyIntensityAndSharpnessAndClamps`、`DetentIndex_UsesUnwrappedMechanicalAngle`、`SpeedTextureLabIsWiredFromActualRotorStateThroughSemanticRouter`、`DetentRateUsesActualAngularSpeedAndSharedDetentCount` | iPhone 确认 Vault/Camera Dial/Watch Bezel/Silk Ratchet 的力度、清晰度与机械间距同步 |
| 转速离散 Detent / 高速 Continuous Blur | 待真机验收 | `HapticSpeedTextureStateMachine` 读取真实角速度与活动 detent count；`>30 detents/s` 只在 Haptic 通道抑制逐档 transient 并驱动唯一循环 `CHHapticAdvancedPatternPlayer`，Intensity Control=`normalizedSpeed × preset intensity`、Sharpness Control=`preset sharpness`；音频事件继续逐档完整输出。单一持久 engine 在场景加载启动，active 状态下 reset/stopped 自动重建 player | `ContinuousCrossoverUsesHysteresisWithoutBoundaryChatter`、`ContinuousBlurUsesPresetValuesAndDenserPresetEntersEarlier`、`NativeHapticLifecyclePreparesReportsAndStopsContinuousPlayer`、`RatchetAudioIsPhysicsDrivenAtomicPolyphonicAndNeverScheduled`；Objective-C++ syntax check 与完整 EditMode 92/92 通过 | iPhone 确认 Haptic 30/s crossover 不会改变音频节拍、engine 恢复、continuous duty cycle 与温升 |
| Core Motion userAcceleration 惯性重量触点 | 待真机验收 | 两个模型读取 native `userAcceleration`；0.30/0.22g 回差、1.50g 满映射、125 ms gate，输出 0.25...0.40 intensity / 0.20...0.35 sharpness 的 isolated transient；不停止或抢占 Detent/continuous。金属原有明确甩动角冲量保持不变 | `InertiaHaptic_UsesPointThreeGThresholdHysteresisAndEightHertzRateLimit`、`DetentAndInertiaUseIndependentIsolatedTransientChannels`、`MobilePerformanceBudgetTests`；完整 EditMode 92/92 与 iPhoneOS native syntax check 通过 | 真机确认拿起/走路误触率、重量感、与棘轮同时发生时的混合效果 |
| 移动端热功耗预算 | 待30分钟真机验收 | 60 fps、2× MSAA、0.90 render scale；HDR/Bloom/Post Processing关闭；1个256 Studio Cubemap、无实时Reflection Probe；正式三叶场景静态审计为12 visible renderers、9,666 tris、15 estimated draws、6 materials、5 textures/3,500,360 bytes。`IPhonePerformanceAudit`仅由显式诊断参数/环境变量启用，只读Frame Timing；`CodexIosPerformanceAudit.mm`每5秒读取phys_footprint、available memory、物理RAM和thermal。`ios_performance_soak.sh`执行实时DDI握手；Release模式完成30分钟控制台落盘并校验包类型、`reason=completed`与可测门槛，Development GC模式隔离构建并运行5分钟，只接受可用counter与`0 B/frame`。普通启动无采样对象。拆解复原和Reset不再向kinematic Rigidbody写速度，消除日志/分配噪声 | `PerformanceAudit_IsExplicitOptInAndCalculatesInterpolatedPercentiles`、`PerformanceAudit_IsReadOnlyAndUsesLiveIosResourceSignals`、`PerformanceBuild_EnablesFrameTimingAndInstallerPerformsLiveDdiHandshake`、`MobilePerformanceBudgetTests`、`MetalGlint_UsesRealSpeedAndResetReturnsToDark`；完整EditMode 92/92通过，iPhoneOS原生syntax check、签名Release arm64构建、安装和启动成功；有效60秒冒烟为3,601帧、phys峰值323.3 MiB、thermal最大Nominal(0)。另一次413帧短测因进入后台明确失败，并确认Unity官方标注的Release GC counter不可用行为；Development GC独立签名构建和覆盖安装成功且`profiler-enable=1`，但设备锁屏拒绝启动，尚无GC样本；最新Release已重新导出并恢复安装 | 60秒只证明采样链路，内存距350 MiB绿线仅26.7 MiB；仍须在非充电、亮度50%、记录环境温度的条件下完成10m自由轮+10m高速棘轮+5m切换拆解+5m混合操作，并补Metal HUD/Power Profiler、available-memory、首末5分钟和Jetsam证据；另须解锁手机完成5分钟Development GC真机交互并保存`gcPassed=true`，Release中的缺失计数既不算通过也不算分配为零 |
| Device Twist 360° | 仅规格 | yaw 已读取但未驱动玩法 | 无 | quaternion/yaw unwrap、detent index、rate limit 和跨 ±180° 测试 |
| 明确甩动驱动三叶物理 | 待真机验收 | `FidgetShakeDetector` 的 thresholdOn/off、jerk、minimumPeak、cooldown 只保留既有三叶角冲量；不再播放会与低锐度惯性通道冲突的明亮 Shake Burst。本次未修改其物理参数 | `ShakeDetector_RequiresJerkAndRearmsAfterCooldownAndHysteresis`、`DetentAndInertiaUseIndependentIsolatedTransientChannels` | iPhone 验证冲量方向；触觉误触率由独立 inertia 行验收 |

三联半圆仪表本轮证据（2026-08-06）：ProductArchitecture + SpinnerProgression 定向 39/39、完整
EditMode 138/138 通过，报告为 `Logs/SeparatedFireDashboardEditModeTests.xml` 与
`Logs/SeparatedFireDashboardFullEditModeTests.xml`；同一源码的 Swift iPhoneOS 15 typecheck 通过。自动化证明
三表同排间距、紧凑 Hero / 翼表共享组件、Peak 火红火苗状态、Intensity / Frequency 独立真实数据、只读
20 Hz bridge、4% 回差、四款旋转源与磁吸推牌非 RPM 分支已接线，不替代 iPhone 上对间距、三个指针响应、
火苗/光晕观感、VoiceOver、动态字号、Reduce Motion / Transparency 和功耗的验证。

底部定位补充证据（2026-08-06）：`ProductOverlayLayout` 现在同时向 SwiftUI feedback layer 与 UIKit
成长卡约束提供 96 pt 高度、12 pt safe-area 底部 inset、14 pt 间距和 122 pt clearance；三联
Speed / Intensity / Frequency 仪表簇通过底部 `Spacer(minLength: 0)` 固定在成长卡正上方；Combo 档位文字
已独立锚定到 3D 模型顶部，Spin Reward / Peak 反馈留在仪表上方，避免覆盖 Home Indicator 或挤压实时指标。相关静态断言已并入
`SpeedDashboard_UsesSeparatedCompactHeroSideMetricsAndPeakFlameState`；ProductArchitecture +
SpinnerProgression 定向 39/39、完整 EditMode 138/138 通过，报告为 `Logs/BottomDashboardEditModeTests.xml`
与 `Logs/BottomDashboardFullEditModeTests.xml`，Swift iPhoneOS 15 typecheck 通过。iPhone 上的底部安全区、
成长卡间距和横竖尺寸仍须真机肉眼验收。

旧半圆下置读数补充证据（2026-08-06，现已由半圆内部 headline 方案替代）：`ProductSpeedDashboard` 与 `ProductSideMetricDashboard` 曾拆成
独立的上方 `GeometryReader` 图形区和下方读数区；Speed / Intensity / Frequency 名称、headline 数字和
单位不再使用 `.position` 覆盖圆弧。主表图形区为 68–84 pt、总高 144 pt，翼表图形区为 48–54 pt、
总高 100 pt；数值与单位使用 `.firstTextBaseline`，三枚组件在外层 bottom alignment 下对齐。静态测试
同时禁止旧的圆弧内部 readout 定位；三项直接相关的 Unity 专项测试 3/3 通过，报告为
`Logs/BelowArcDashboardFocusedTests.xml`，Swift iPhoneOS 15 typecheck 与交互式组件库脚本解析/渲染也通过。
同轮较宽的 ProductArchitecture + SpinnerProgression 组合为 43/45，两个失败来自并行开发中的 Collector
Rank 业务断言，与 dashboard 文件及数据管线无关，未将其误报为全量通过。iPhone 上仍须确认不同
Dynamic Type 下读数不会顶回半圆图形。

半圆内部 headline 与全 UI 组件统一补充证据（2026-08-06）：主表 `252 RPM` 与左右百分比重新进入
各自半圆内部，Intensity / Speed / Frequency 名称仍保持左 / 中 / 右的半圆下方位置并统一为
`caption2`。主数值起始字号 25 pt、翼表 17 pt，局部暗色 scrim 只避免指针穿字；组件总高收紧为
112 / 72 pt，外层 10 pt 间距与底部定位不变。共享库新增 heading、notice、inline tag、selection card、
badge tile、compact metric、slider、toggle 与 empty state，并接入 Quick Start、模型库、通知、成长、外观、
Badge、设置和触觉实验室。专项 5/5、ProductArchitecture + SpinnerProgression 45/45、完整 EditMode
147/147 与 Swift iPhoneOS 15 typecheck 通过；报告为 `Logs/UnifiedComponentGaugeFocusedTests.xml`、
`Logs/UnifiedComponentGaugeEditModeTests.xml`、`Logs/UnifiedComponentGaugeFullEditModeTests.xml`。
交互式组件库在真实 Chromium 完成布局截图检查；iPhone 上的 Dynamic Type、VoiceOver、Reduce
Transparency、明暗 3D 背景与 Peak 火焰仍须真机肉眼确认。

一体化半圆扫掠渐变补充证据（2026-08-06）：共享组件用可动画的
`ProductDashboardSweepField` 直接画从零点到当前 fraction 的半圆扇区，扇区终止径向边承担指示器语义；
同一 `RadialGradient` 以实际表盘圆心为中心，由 0 opacity 连续过渡到外缘实色。原先独立的
`ProductDashboardNeedle`、`.trim` 活动弧和中心针轴已删除，避免出现透明填充与实色指针的拼接分界。
Speed、Intensity 与 Frequency 复用同一实现，仍读取各自权威数据；Peak 火焰只是外缘奖励装饰，不改变
扫掠值。Swift iPhoneOS 15 typecheck、ProductArchitecture + SpinnerProgression 52/52 与完整 EditMode
160/160 通过，证据为 `Logs/RadialSweepDashboardFocusedTests.xml` 与
`Logs/RadialSweepDashboardFullEditModeTests.xml`。Release arm64 Build 13 已签名、覆盖安装并启动到
iPhone「JW」，设备进程 PID 14375 持续运行；短时控制台确认 Unity/Metal/PhysX 初始化并进入 active，
无 Swift crash、C# Exception、MissingReference 或资源缺失。安装与启动仍不替代用户对真机动态渐变
连续性、三表间距、Peak 光晕和 Reduce Transparency 的肉眼验收。

无描边 Liquid Glass 补充证据（2026-08-06）：`ProductGlassModifier` 已移除旧系统 fallback 的
0.7 pt 白色周圈 stroke；iOS 15–25 改为低透明度 tint 叠加 `ultraThinMaterial`，iOS 26 继续使用
原生 `glassEffect`。Badge 通知图标和卡片、外观选择卡、Badge tile、藏家成就行与外观缩略图不再
绘制 accent / 白色外框，选中态只使用材质亮度、低比例 tint、filled tag 与 checkmark。交互式组件库同时删除所有玻璃表面的 inset outline，
并以模糊、饱和度、柔和渐变和外投影表达层次；仪表弧线、刻度、进度轨道、divider 和图标自身
线条仍保留为信息几何。Badge / 成就解锁通知进一步改用 `star.fill` / `trophy.fill` 与实心
`checkmark.circle.fill`，不再显示空心星标或圆环印章。iPhoneOS 15 Swift typecheck、组件库
JavaScript 语法、Chromium 760 px 视觉检查、实心 Badge 规则专项 1/1 和最新完整 EditMode
147/147 通过；报告为 `Logs/SolidBadgeLiquidGlassFocusedTests.xml`、
`Logs/MagneticSliderLongThrowHeavyDetentFullEditMode.xml`。iPhone 上的原生材质折射、Reduce
Transparency 与浅色 3D 高光背景可读性仍待真机肉眼确认。

五款统一场景与交互本轮证据（2026-08-05）：完整 EditMode 118/118 通过；签名 Release arm64
构建成功并覆盖安装、启动到 iPhone「JW」。包内 `globalgamemanagers` 回读包含五个正式场景，
设备进程回读确认 `FidgetSpinner.app/FidgetSpinner` 正在运行；20 秒 Release 控制台无 C# 异常、
无缺失环境资源或 Shader 错误，thermal state 为 Nominal。证据为
`Logs/FullEditModeUnifiedFiveProducts.xml`、`Logs/iOSBuild-UnifiedFiveProducts.log`、
`Logs/iPhoneConsole-UnifiedFiveProducts.log`。安装与启动仍不替代石台融合、详情退景、第五款手势、
四款 RPM 仪表、推牌非 RPM 反馈、Combo、星空闪烁与显式代盘手感的人工验收。

统一峡谷岩面背景真机补充证据（2026-08-05）：五个正式产品场景均读取
`EnvironmentBackgrounds/canyon-unified-ledgestone-v1-2x`（1882 × 3344）；程序生成的圆台、方台和
支托不再渲染，Library 只以相机展示姿态让模型接近 90° 竖立于背景自带岩面上方，且不改写转子物理
姿态。模型主色实时驱动主体光晕、扁平接触光和岩壁回光，进入详情后恢复完整材质曝光与既有交互镜头。
环境专项 5/5 与完整 EditMode 118/118 通过，证据为
`Logs/UnifiedCanyonEnvironmentTests-Final.xml`、`Logs/FullEditModeUnifiedCanyon.xml`；同一源码的签名
Release arm64（Fidget Spinner 0.1.0 (2)，Bundle ID `com.jiaweizhou.fidgetspinner.codex`）已成功构建、
覆盖安装并启动到 iPhone「JW」，Unity 导出证据为 `Logs/iOSBuild-UnifiedCanyon.log`。安装和启动证明
运行链路已到真机，但五款构图、着地/悬浮距离、光晕强度与材质曝光仍明确等待用户逐页肉眼验收。

选择页动态展陈补充证据（2026-08-05）：第五款现由 `EdcDeviceMotionController` 复用同一
`IosDeviceMotion` 60 Hz 生命周期并发布 `SceneParallaxInput`，因此五款都以进入页面姿态归零并响应
roll/pitch；选择页主体锚点由 14 px 提升到 20 px，三类展示镜头只在 Library 将设备轨道响应放大
1.25 倍，详情页仍读取原设置。悬浮完全由相机投影完成，不写模型 Transform 或刚体：基础 3.5 px、
振幅 2.5 px、0.42 Hz；背景层补偿该垂直位移，背景石面保持静止。`EnvironmentParallaxUnlit` 在背景
岩面顶缘绘制独立的窄椭圆接触投影，悬浮升高时投影变宽/变淡、下降时收紧/加深；主体、接触光及
左右岩壁回光同步增强。原 Library 翻页曾在切换场景前用 0.16 秒把当前模型和背景岩面移出约 1.08 个
视口；该做法已因真机横滑出现背景露黑/闪动，于 2026-08-06 由下方“选择页横滑背景闪动修复”取代。
当前翻页不再驱动背景出入场，改由异步 Single scene load 保留旧画面至新场景就绪，并缓存统一背景的
GPU 取色结果。该系统只写视觉展示状态，不写角速度、滑盖进度、成长、Combo 或 Haptic。
环境专项 5/5、完整 EditMode 123/123 通过，证据为
`Logs/LibrarySelectionMotionEnvironmentTests.xml`、`Logs/FullEditModeLibrarySelectionMotion.xml`；五款
Unity Metal 实际渲染保存在 `Artifacts/EnvironmentIntegration`。真机设备角度映射、动态阴影、悬浮
节奏及连续快速左右滑动仍待肉眼验收。同一源码的签名 Release arm64（Fidget Spinner 0.1.0 (2)，
274 MiB，Bundle ID `com.jiaweizhou.fidgetspinner.codex`）已完成 Unity 导出、Xcode 构建、覆盖安装并
成功启动到 iPhone「JW」，构建证据为 `Logs/iOSBuild-LibrarySelectionMotion.log`；安装/启动只证明
真机运行链路，不替代用户手持倾斜与连续滑页的视觉验收。

选择页滑动方向修复（2026-08-05）：`SpinnerSceneParallaxController` 现在显式把逻辑页位移转换为
透视投影的反向矩阵符号，修正此前手指左滑而场景视觉右移的问题；左滑下一款时旧场景向左退出、
新场景从右侧进入，右滑严格镜像。仅改分页投影符号，不改模型旋转、捏合、Core Motion、刚体或
Haptic。完整 EditMode 123/123 通过，证据为 `Logs/FullEditModeLibrarySwipeDirection.xml`。该分页投影
路径已于 2026-08-06 停止由 `FidgetAppCoordinator` 调用；方向数学仍保留为历史代码，但不再参与当前
Library 横滑，避免统一背景随页移动。
同一源码的签名 Release arm64 已构建成功并覆盖安装到 iPhone「JW」；因设备当时锁屏，按发布脚本
`--no-launch` 路径完成安装而未把启动记为成功，构建证据为 `Logs/iOSBuild-LibrarySwipeDirection.log`。

五模型正式产品补充证据（2026-08-05）：`BuildContainsAllFiveFidgetModelsInOneProduct`、
`BuildContainsAllFourSpinnerModelsInOneProduct` 与
`MagneticSlideTileIsRoutedByTheCanonicalCoordinator` 同时锁定 5 个正式场景、原 4 款不丢失、
推牌原生目录/场景路由/Reset 闭合链路；最新完整 EditMode 117/117 与 Swift iPhoneOS 15
typecheck 通过。独立 EDC 优化构建已固定使用 `.edcopt` Bundle ID，不得再覆盖正式 App。
同日完整 Release arm64 构建成功：签名 `.app` 为 272 MiB，Bundle ID
`com.jiaweizhou.fidgetspinner.codex`，包内 `globalgamemanagers` 逐项读回原 4 款场景与
`Assets/_EDC/Scenes/MeshyEDC.unity` 共 5 个场景；已覆盖安装并成功启动到 iPhone「JW」，
2026-08-05 完成竖屏 58% 屏宽取景、同向拖拽与随动触控面修复后，正式五场景包重新导出、
签名、覆盖安装并启动；设备回读为 Fidget Spinner 0.1.0 (2)。安装/启动只证明集成链路，不等同于第 5 页材质、
拖拽磁吸手感或 2M 三角正式场景性能验收。

旧三等权仪表补充证据（2026-08-04，已由 2026-08-06 Hero + 从属翼表方案替代）：当时的
`ThreeGaugeComboPipelineIsSharedByAllFourProductModels` 曾逐场景验证经典蓝色的
`FidgetSpinnerController`，以及三叶金属、镜钢四翼、石墨双叶共享的
`MobileGestureController` / `RotorRigidbodyController` 进入同一 `SpinnerMetricCluster`；该历史专项
1/1、完整 EditMode 107/107 通过。当前 UI 不再使用三个同权仪表，新的权威断言为
`RotarySpeedDashboardAndComboPipelineUseCanonicalSources`、
`SpeedDashboard_UsesSeparatedCompactHeroSideMetricsAndPeakFlameState`，历史报告只保留为对应构建时点证据。

性能验收脚本补充证据（2026-08-03）：安装和审计都会在昂贵构建/计时前读取CoreDevice
`lockState`；锁定真机实测分别约1.8秒和0.6秒失败退出。Release运行还强制声明环境温度、
45%至55%亮度与`unplugged`供电，并在机器门槛通过后生成`device-console.log`、`summary.json`
和待补Metal/Power/人工观察的`REPORT.md`。显式Release审计还通过原生桥读取电池状态/电量
和`UIScreen.brightness`交叉验证声明，诊断结束时恢复此前battery monitoring设置；真机输出
仍待解锁后验证。包含该桥的最新Release已完成iPhoneOS语法检查、签名构建和锁屏恢复安装，
未把未启动状态记作验证通过。

## Blender 三叶模型资产管线（2026-08-06）

- 已通过 ahujasid `blender-mcp` 的 `execute_blender_code` 生成参数化三叶金属 EDC；MCP 仅监听
  `localhost:9876`，Codex 以 Python 3.11 的 `uvx blender-mcp` 连接，并通过
  `DISABLE_TELEMETRY=true` 关闭遥测。
- DCC 源文件为 `ArtSource/ThreeBladeSpinner/ThreeBladeSpinner.blend`；Unity 正式交换资产为
  `Assets/_Fidgeting/Models/BlenderThreeBlade/ThreeBladeSpinner.fbx`，另提供 GLB 和独立碰撞 FBX。
  Blender 场景含 44 个对象、6 个材质；视觉资产为 30 个 Mesh、约 24,952 tris，真实包围盒约
  87.4 mm × 87.4 mm × 15.94 mm，三叶、固定指帽、轴承保持架和碰撞层级相互分离。
- Unity 6000.5.6f1 已实际导入两个 FBX；`BlenderThreeBladeModelImporter` 固定 1:1 米制、保留层级，
  并关闭动画、BlendShape、相机、灯光和可见性导入。`BlenderThreeBladeAssetTests` 验证层级、尺寸、
  10 枚轴承球、三叶碰撞网格和导入设置；2026-08-06 定向 EditMode 运行结果为 3/3 通过，证据见
  `Logs/BlenderThreeBladeAssetTests.xml` 和 `Logs/BlenderThreeBladeAssetTests.log`。
- **当前状态是“模型文件已产出并通过导入验收”，不是“正式场景已替换”。**
  `Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity` 仍使用既有程序生成模型和既有交互 wiring；把新 FBX
  替换进 `RotorDynamic`、`HubStatic`、`BearingVisual` 并通过完整场景/交互测试后，才能标记运行时集成。
  iPhone 上的金属反射、轮廓、触控命中和旋转性能仍明确待真机验收。

## Blender 龙鳞 EDC 一体转子圆润修正版（2026-08-07，已接正式场景）

- 参数化源为 `tools/blender/generate_dragon_scale_edc.py`，DCC 源文件为
  `ArtSource/DragonScaleEDC/DragonScaleEDC.blend`。用户在 2026-08-06 以保留的正视/爆炸截图明确选择
  这一版回退，并取代之后错误的粗糙外扩叶片版本。2026-08-07 又针对“叶片和主体过硬、边缘折面”
  完成同一结构内的曲面修正；版本选择和编辑器预览都不替代真机视觉验收。
- 初版曾错误简化为三块分离盾形叶片；该几何已被废弃并覆盖。当前版本严格按爆炸图输出单一
  `RotorBody_OnePiece` shipping Mesh：中央承力环与三枚封闭的龙鳞箭头叶片共用一个 Renderer、转子
  Transform 和 Rigidbody owner。2026-08-07 的去毛边修正把三枚叶根与承力环从“相交封闭体 Join”
  改为带 0.5 mm 厚度穿透的 Exact Boolean 真正并集，删除会在 Unity 金属高光下形成碎黑边的内部相交面。
  叶片不再是椭圆桨叶或细长三角框，而是宽肩包住中心环、径向短身、
  圆头内收的厚金属框；较小的三角凹腔、两侧斜面和抬高机械折脊都由本体拓扑表达，不再用表面徽章
  模拟。上指帽、上垫片、独立轴承、一体转子、下垫片和下指帽均有独立爆炸层级。
- Unity 交换资产位于 `Assets/_Fidgeting/Models/BlenderDragonScale/`，包括视觉 FBX、GLB 和独立碰撞
  FBX。2026-08-07 的圆件精修版仍为 29 个 Mesh、约 36,028 tris，真实平面直径约 84.04 mm、总厚度约
  16.88 mm；正式场景继续满足既有 `≤45k` iPhone 总三角面预算。主指帽、拉丝面与转子冠环使用 128
  个真实圆周采样，细装饰环使用 96，屏幕占比较小的轴承/垫片使用 72；指帽为 4 段倒角、主承力环为
  3 段倒角，避免再次退回 64 边指帽和 2 段主倒角的可见折线。
  三枚叶片每半侧使用 40 采样连续轮廓；外肩半宽大于 19 mm 指帽半径，因此根部仍能在中心环两侧显示，
  径向尖端从上一候选的 51 mm 收到 48 mm，三角凹腔同步缩短和收窄。外缘、内腔和底缘不再依赖会
  在汇聚尖端留下开口的通用 Bevel modifier，而是使用显式嵌套圆角环形成圆润过渡，并把抬高折脊
  保留为硬边。导出前用 bmesh 焊接、折叠数值碎面、三角化、重算法线，再对全部可见圆件统一执行
  smooth-by-angle 与面积加权法线；Unity 指帽径向拉丝 Normal 强度从 `0.18` 降到 `0.10`，减少近景金属
  高光的细碎闪烁。
  Unity importer 固定 1:1 米制、保留层级、导入法线并生成 MikkTSpace 切线，避免布尔三角面在金属
  高光中形成放射折痕。最终 `RotorBody_OnePiece` 审计为 0 boundary edges、0 non-manifold edges、
  0 zero-area faces，证据为仓库根目录 `Artifacts/DragonScaleArrowFrameGeometryAudit.txt`。
- `ThreeBladeSceneBuilder` 现将该 FBX 解包并按物理职责接到正式 `ThreeBladeEDC.unity`：
  `Rotor_Root` 归 `RotorDynamic`，固定指帽/垫片归 `HubStatic`，轴承总成归 `BearingVisual`，轴承保持架
  继续由 `BearingCageVisualSync` 驱动。旧程序模型的 Renderer 关闭但其既有 Rigidbody、碰撞体、手势、
  物理、成长、音频与 Haptic 接线保留；10 枚导入球关闭，继续显示单一批处理球笼以控制 draw call。
  FBX 坐标转换后在 Unity +Y 旋转轴上补偿 180°，正式顶视恢复参考图的一叶朝上、两叶向下构图。
- 爆炸顺序已固定为上指帽 `+43 mm` → 上垫片 `+24 mm` → 独立轴承 `+10 mm` → 一体转子
  `0 mm` → 下垫片 `-16 mm` → 下指帽 `-36 mm`。`BlenderDragonScaleAssetTests` 同时锁定正式场景
  使用 `RotorBody_OnePiece`、旧视觉隐藏、六段爆炸顺序、轴承批处理和转子初始零角速度；测试还禁止
  重新出现三个 `DragonBlade_*` 分离盾形 Mesh。
- Unity 6000.5.6f1 圆件精修版完整 EditMode 回归 `179/179` 通过；新增
  `VisibleCircularParts_UseRetinaReadySilhouettesAndCalmCapNormals` 锁定 128/72 级可见圆周密度与 `0.10`
  指帽 Normal 强度，既有 `MobileMeshes_StayInsideTriangleBudgetAndProvidePbrChannels` 同轮通过；证据为
  仓库根目录 `Artifacts/DragonScaleCirclePolishFullEditModeTests.xml`。Blender 审计后的
  `RotorBody_OnePiece` 为 0 boundary edges、0 non-manifold edges、0 zero-area faces，明细更新于
  `Artifacts/DragonScaleArrowFrameGeometryAudit.txt`。
- 设备视觉推送门禁所需的圆件精修版正式 Unity Metal 场景图已重新输出：顶视、authored Hero、左/右斜视、低角和爆炸图分别为
  仓库根目录 `Artifacts/three-blade-edc-top.png`、`three-blade-edc-preview.png`、
  `three-blade-edc-left-oblique.png`、`three-blade-edc-right-oblique.png`、`three-blade-edc-side.png` 与
  `three-blade-edc-exploded.png`。用户在同日查看本组预览及同时入包的 V21 贴纸、长按轻弹、Combo
  分层光晕后明确回复“确认全部预览并推送”，设备视觉门禁已满足。
- Release 签名 arm64 `0.1.0 (20)`、Bundle ID `com.jiaweizhou.fidgetspinner.codex` 已完成 Unity 导出、
  Xcode Release 编译与严格 codesign 校验；本地 App 为 319 MiB。`devicectl` 已覆盖安装到 iPhone
  `00008130-001A00361EE0001C`，设备 inventory 回读确认 Build 20。初次安装时手机锁屏，采用
  `--no-launch`；随后手机解锁并成功启动，设备回读 PID 18095。证据为
  `Logs/iOSBuild-DragonScalePrimary-B20.log`、`Logs/DeviceBuild20InstalledApps.json` 与
  `Logs/DeviceBuild20Processes.json`。
- **当前状态是“圆件精修版已成为首个产品、自动化通过并已安装 Build 20”。** 仍需解锁后在 iPhone 肉眼确认
  金属反射、真实深腔、边缘抗锯齿、上下指帽厚度、触控命中和旋转性能；安装/启动本身不等于视觉
  验收完成。

### Rodin 多视图候选（2026-08-06，待人工视觉复核）

- 已启用 Blender MCP 内置的 Hyper3D Rodin `MAIN_SITE / free_trial`，并只提交四张单体正/侧参考图；
  动作分镜和爆炸拼图没有作为生成输入，避免多人手、多物体画面污染重建。Rodin 任务
  `1f9b6041-cb03-4573-bbf6-80cb0a924417` 的六个阶段均返回 `Done`；原始下载物保存在
  `Artifacts/BlenderDragonScale/Rodin/raw/`。
- Blender MCP 的大尺寸 base64 调用触发 180 秒 socket 超时，因此本次对同一 Rodin API 使用
  `tools/blender/submit_rodin_direct.py` 和 `tools/blender/check_rodin_task.py` 完成一次压缩四视图提交、
  轮询和下载；API 密钥只从已安装的 Blender MCP add-on 读取，不写入仓库或日志文件。
- 清理脚本 `tools/blender/cleanup_rodin_dragonscale.py` 保留 Rodin 的弯曲三叶外壳和三处凹槽，将外壳
  归一化为约 `65.0 × 64.79 × 7.10 mm`，并重建独立的上指帽、上垫片、608 轴承、转子/轮毂、
  下垫片和下指帽层级。候选源文件为
  `ArtSource/DragonScaleEDC/Rodin/DragonScaleEDC_Rodin_Cleanup.blend`，同层级交换文件为
  `ArtSource/DragonScaleEDC/Rodin/DragonScaleEDC_Rodin_Cleanup.glb`；正视、侧视、斜视和爆炸检查图
  位于 `Artifacts/BlenderDragonScale/Rodin/Cleanup/`。
- **当前状态是“Rodin 清理候选已产出，人工视觉复核待完成”，不是 Unity 集成。** 该 GLB 尚未复制到
  `Assets/`、没有替换正式场景、没有新增 Unity 通过结论；只有用户确认轮廓、中心盖比例、侧面厚度和
  爆炸层级后，才进入 Unity 导入、碰撞体、交互和性能测试。

### 高清矢量贴纸与最上层金属面激光刻痕（2026-08-07，Build 19 已推真机）

- 24 张灰色背板白色图形已通过 ImageGen 以 `6 × 4` 高对比母版重建，随后用确定性二值化与
  Potrace 曲线描摹生成独立矢量文件。运行时 PNG 位于
  `Assets/Resources/ProductStickers/BackdropWhite/`，全部为带透明通道的 `1024 × 1024` 方图；
  对应白色闭合路径 SVG 位于 `Assets/Art/ProductStickers/Vector/`，全部使用方形
  `viewBox="0 0 256.000000 256.000000"`。母版、黑底检查图和可复现脚本分别为
  `Artifacts/Stickers/StickerAtlasImageGenMaster.png`、
  `Artifacts/Stickers/StickerAtlasVectorPreview.png` 与
  `Tools/rebuild_imagegen_sticker_vectors.sh`。
- 多角度排查确认导入指帽存在两层独立网格：`FingerCap_Top` 是下层结构壳，真正可见的
  `FingerCapTop_BrushedFace` 在模型局部 Z 方向高出 `2.08 mm`。旧实现复制结构壳，因此正顶视角被
  BrushedFace 完全遮挡、斜视角只能看见壳体露出的部分。`ProductStickerPresenter` 现在仍只接受
  `enabled && activeInHierarchy` 的 Renderer，但按明确优先级选择
  `HubStatic/TopCap/TopCap_Root/FingerCapTop_BrushedFace` 作为唯一接收面；`FingerCap_Top` 只作为
  缺少正式面时的回退，AccentLine 不会抢占接收面。刻痕复制最上层金属面的原 Mesh、零局部变换且
  无 Collider/Rigidbody；已禁用的旧程序化 `HubStatic/TopCap` 不可能被误选。
- 斜角消失的第二个原因是贴纸纹理原先使用普通 mipmap、未保留 Alpha 覆盖且各向异性仅为 1。
  `ProductStickerArtworkImporter` 现在统一配置 24 张资源为 Kaiser mipmap、Alpha coverage `0.10`、
  mip bias `-0.50`、Trilinear、aniso `8`；iPhone 固定 `1024² / ASTC 4×4 / quality 100`。
  Shader 改为 `TransparentCutout / AlphaTest+25`、`ZWrite On`、`Cull Back`、`Offset -4,-4`、
  `AlphaToMask On`，沿接收面法线抬升 `0.18 mm`，并用 `fwidth` 生成随屏幕像素宽度稳定的银色加工内缘；
  深色面读取亮切边，亮色面读取深石墨刻痕。投影 X 轴的镜像符号也已修正，文字不再反向。
- `DefaultStickerCatalogAndPresenter_ArePersistentVisualOnlyAssets` 现在逐一锁定 24 张 PNG 的
  `1024 × 1024` 尺寸以及 24 份 SVG 的方形 viewBox/白色路径；
  `ConformalEngraving_UsesActualMetalTopCapAndStaysVisible` 在真实 `ThreeBladeEDC` 场景锁定唯一
  BrushedFace 接收面确实高于结构壳、共享同一 Mesh、零 Collider 和正确父层级；资源测试同时锁定
  24 张 PNG/SVG、mipmap coverage、aniso 与 iPhone ASTC 设置。最新定向 EditMode 为 `2/2`，证据为
  `Logs/TopmostStickerReceiverTests.xml`；此前长按选择回写的组合回归继续由既有报告证明。
- `ProductStickerAnglePreviewRenderer` 从正式 `ThreeBladeEDC.unity`、正式材质和实际 Metal 渲染路径产出
  15 张 `640 × 640` 预览：图形、文字、细线各覆盖正顶 `89°`、Hero `42°`、左 `35°`、右 `35°`、
  低角 `15°`。原始图和 `5 × 3` 审批联系表位于 `Artifacts/Stickers/AnglePreviewV20/`，渲染日志为
  `Logs/StickerAnglePreviewV20-Metal.log`。预览每次渲染显式清空颜色/深度，避免手工 RenderTexture
  在跨视角时残留深度造成假阴影或假遮挡。
- 用户已明确批准 V20 联系表后才开始构建。签名 Release arm64 `0.1.0 (19)` 随后在隔离工程完成
  Unity 导出与 Xcode 编译，Unity 明确 `Build Finished, Result: Success`，Xcode 明确
  `BUILD SUCCEEDED`；本地 Bundle ID/版本回读为 `com.jiaweizhou.fidgetspinner.codex / 0.1.0 / 19`，
  严格 codesign 验证通过，24 张正式贴纸在 App bundle 中 `24/24` 齐全。Build 19 已覆盖安装并启动到
  iPhone，设备 inventory 回读 Build 19，最终运行 PID 16545。20 秒启动控制台进入
  `applicationDidBecomeActive`、Metal A17 Pro，未出现 Shader/C#/MissingReference/资源缺失错误；
  设备当时 thermal state 为 `Serious`，所以该次只算启动冒烟，不算性能/温控验收。证据为
  `Logs/iOSBuild-StickerTopFace-B19.log`、`Logs/iOSInstall-StickerTopFace-B19.txt`、
  `Logs/DeviceBuild19InstalledApps.json` 与 `Logs/DeviceBuild19Processes.json`。今后仍执行仓库级
  Device visual push gate；本次安装/启动不替代用户在手机上旋转观察后的最终视觉验收。

### 长按模型轻弹、语义 Pop 与 Half Sheet 顺序（2026-08-07，预览待用户批准，未构建/未推真机）

- `ProductAppearanceActivationSequence` 新增独立于帧率的 `0.22 s` 入口时间轴：初始
  `1.000×`，`0.075 s` 到 `1.035×` 峰值，`0.150 s` 回落到 `0.992×`，`0.220 s`
  恢复 `1.000×` 并只发出一次 half-sheet-ready 信号。`FidgetAppCoordinator` 在长按成立时先禁用
  当前模型交互、停止连续触感纹理并通过 `FidgetHapticRouter.Emit(FidgetSemanticEvent.Pop)` 发出一次
  语义触感；只有 ready 信号到达后才调用现有 `ProductAppearanceNativeBridge.SetPresented(true)`。
- 三套正式模型相机 `PortraitCameraFramer`、`OrbitPresentationCamera` 与
  `EdcPortraitCameraFramer` 都只把 apparent scale 除进镜头距离；没有缩放产品 Transform、修改
  Collider、质量、惯量或角速度。应用失焦、暂停、场景切换、原生关闭和 Coordinator 销毁都会取消
  未完成序列、把 framing 恢复到 `1.000×`，避免卡在放大态。原生 `ProductAppearanceEditor` 的
  half sheet 布局保持不变，继续只组合既有 `FidgetProductUIComponents.swift` 组件。
- `AppearanceActivation_PopsThenPresentsHalfSheetExactlyOnce` 锁定四个时刻、重复 Begin 拒绝及 ready
  one-shot；`LongPressAppearanceEditor_UsesSharedUiAndConfirmedUnitySelections` 同时锁定三套相机接入、
  `Pop -> FidgetHapticRouter` 与现有共享 UI。`SpinnerProgressionTests` 定向 EditMode `34/34` 通过，
  报告 `Logs/LongPressActivationEditModeTests.xml`。完整 EditMode `178/179`：唯一失败是正式三叶场景
  当前可见网格 `48,054` tris 超出既有 `45,000` 静态预算，与本次只修改相机距离/入口状态机的文件
  无关；报告 `Logs/LongPressActivationFullEditModeTests.xml`，不把该失败误报为全绿。
- `ProductStickerAnglePreviewRenderer.RenderLongPressActivationApprovalPreview` 从 shipping
  `Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity` 与正式 Metal 路径生成正顶、authored Hero、左/右斜视、
  低角五个视角 × 静止/峰值/回落/sheet-ready 四阶段联系表，并生成 Hero 动态帧。审批素材位于
  `Artifacts/Appearance/LongPressActivationV1/`，渲染日志为
  `Logs/LongPressActivationPreview-Metal.log`。当前明确处于“等待用户视觉批准”状态；仓库视觉门禁要求
  获得批准后才能构建或安装，因此本轮尚未把该视觉变化推到 iPhone。

## 每次合入的检查方式

1. 在本矩阵中选择目标行；任务开始时不能把 `仅规格` 当作已有能力。
2. 实现代码时让参数只有一个权威来源；其他层读取或由测试验证一致。
3. 为机械状态机写纯函数/Editor tests，为场景连接写 PlayMode 或静态验收测试。
4. iOS native 功能同时检查 capability、engine reset、App 后台、start/update/stop。
5. 自动化通过后更新本矩阵；触感相关项目仍标记 `待真机验收`，直到在支持 Core Haptics 的 iPhone 上完成体验验收。
