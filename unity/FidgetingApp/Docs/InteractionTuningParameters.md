# 真机调试参数记录

项目：`Fidget Spinner`  
Bundle ID：`com.jiaweizhou.fidgetspinner.codex`  
最后更新：2026-08-02

> 注意：本文件保留早期真机调参记录，其中部分“自动旋转、UIKit Selection、像素间隔 Haptic”描述已经落后于当前代码。新的物理模型、Haptic 术语、Recipe、Mapping、Shake 与 Device Twist 规格以 `FidgetingInteractionHapticsSystem.md` 为准；本文件后续只记录已在真机验证的具体数值。

## 使用方式

以后调整参数时，只需要提供“参数名称 = 新数值”，例如：

```text
input.spinSensitivity = 0.70
haptic.drag.intensityMax = 0.95
motion.maximumInputAngle = 10
```

修改代码并完成验证后，需要同步更新本文件的“当前代码值”。“建议目标值”表示下一轮调试基线，不代表当前安装版本已经生效。

## 玩法模式快捷预设

进入陀螺后，原生 SwiftUI 导航栏提供“平滑 / 棘轮”两个模式。切换模式会原子地应用以下机制和触感参数；物理段落数与 Haptic 段落数共用同一个 `detentsPerTurn`。

| 参数 | 平滑 | 棘轮 |
| --- | ---: | ---: |
| `mechanism.mode` | `Freewheel` | `MagneticDetent` |
| `input.touchResponse` | `0.55` | `0.48` |
| `physics.spin.resistance` | `0.58` | `0.58` |
| `mechanism.detent.countPerTurn` | 不触发段落 | `24` |
| `mechanism.detent.breakawayAngularSpeed` | 不适用 | `2.2 rad/s` |
| `mechanism.detent.captureAngularSpeed` | 不适用 | `1.2 rad/s` |
| `mechanism.detent.snapResponse` | 不适用 | `16 s⁻¹` |
| `haptic.intensity` | `0.62` | `0.95` |
| `haptic.frequencyFeel` | `0.62` | `0.88` |
| `haptic.speedFollow` | `0.20` | `0.35` |
| `haptic.rhythm` | `Single` | `Single` |

平滑模式不会把拖动距离伪装成机械档位；三叶金属使用自由轮 half-life 衰减，经典蓝色也关闭段落触点。棘轮模式在三叶金属上使用真实磁吸状态机产生 `Breakaway / DetentCrossed / DetentCaptured` 语义事件；经典蓝色保留现有物理自由轮，但 `DetentCrossed` 已改由刚体角速度累计出的实际转子角度跨档产生，不再根据拖动像素间隔伪造。经典蓝色的真实磁吸运动仍属于后续统一机制迁移范围。触感强弱与档位质感仍需 iPhone 真机确认。

## 逐语义 Haptic Recipe 编辑器

SwiftUI 日常设置只保留力度与频率感两个 Haptic 总控；节奏与速度调制移入触觉实验室，并明确只影响 Haptic。实验室允许分别编辑 Selection、Tick、Breakaway、Capture、Release、Reversal、Reset 和 Preview。每一份配方保存到 `UserDefaults`，启动后通过 Coordinator 写入 `FidgetHapticRecipeLibrary`，播放仍严格经过“输入 → 机制状态 → 语义事件 → Recipe → iOS renderer”。

| 分组 | 参数 | 范围 | 性质 |
| --- | --- | ---: | --- |
| Apple 事件 | `hapticIntensity`、`hapticSharpness` | `0...1` | `CHHapticEventParameter` |
| Apple 连续事件 | `duration` | `> 0...30 s` | `CHHapticEvent` 的持续时间；Apple 的单个 continuous event 上限为 30 s，本 App 的 Recipe 编辑器可继续使用更窄范围 |
| Apple 包络 | `attackTime`、`decayTime`、`releaseTime` | `0...1` | 指数式时间调节量，不等于秒 |
| Apple 包络 | `sustained` | `0 / 1` | 为 `0` 时 Decay 才形成衰落段 |
| Apple 动态控制 | `hapticIntensityControl` | `0...1` | `1` 为不衰减 |
| Apple 动态控制 | Sharpness / Attack / Decay / Release control | `-1...1` | `0` 为中性调制 |
| App Recipe | `Hybrid` | Transient + Continuous | 本项目组合类型，不是 Apple event type |
| App Recipe | `endIntensity`、`endSharpness` | `0...1` | 多脉冲序列首尾插值 |
| App Recipe | `pulseCount`、`pulseInterval`、`impactLayers` | 见 UI | 事件编排与冲击叠层 |

音频事件的 Volume、Pitch、Pan、Brightness 及对应动态控制属于 Core Haptics 的音频同步能力；当前 App 只编辑触觉配方，因此不把音频参数混进 Haptic 面板。

当前增强基线以 Tick、Breakaway 和 Capture 为重点：Tick 基础力度 `0.84`、冲击叠层 `1.65×`；Breakaway 基础力度 `0.78`、叠层 `1.55×`；Capture 使用 Hybrid、基础力度 `0.95`、双脉冲和 `1.75×` 叠层。全局棘轮力度为 `0.95`。这些数值已经进入运行时和 UI fallback，但“是否清晰且不沙哑”仍必须在本次安装后的 iPhone 上验收。

## 转速质感与高速轴承纹理

触觉实验室以真实转子角速度和同一份 `detentsPerTurn` 计算机械事件率，单位是“触点/秒”，不是 Taptic Engine Hz。推荐 profile 在低速保留独立 Tick；超过 `30 触点/s` 进入轻量 Bearing Continuous，降到 `24 触点/s` 以下才退出，使用滞回避免边界抖动。Continuous 的强度为 `0.06...0.16`、锐度为 `0.28...0.48`，按 `0.75` 次幂映射并以 `30 Hz` 更新；Core Haptics attack 为 `0.04`（归一化参数），停止淡出为 `0.10 s`。离散 Tick 的速度增益从低速 `1.0` 过渡到高速 `0.42`，进入 Continuous 后会抑制重复 Tick。所有阈值、曲线、A/B 槽和实时 telemetry 都可在设置页调整；真机仍需确认 crossover 是否自然、连续纹理是否会遮住机械段落。

## 单指滑动与旋转

| 参数名称 | 当前代码值 | 建议目标值 | 备注 |
|----------|------------|------------|------|
| `spin.initialSpin` | 0 | 0 | 冷启动和复位必须保持零角速度 |
| `spin.tapImpulse` | 已移除 | 已移除 | 轻点只刹停，不再注入固定转速 |
| `input.touchResponse` | 平滑 `0.55` / 棘轮 `0.48` | 真机待调 | 唯一拖动响应控制；派生以下四项 |
| `input.sensitivityGain` | `0.18...1.65` | 同左 | 0–100 变化超过 9 倍 |
| `spin.screenSpeedForFullSpin` | `1800...720 px/s` | 同左 | 响应越高，达到满速所需手速越低 |
| `spin.fallbackDegreesPerPixel` | 0.55°/px | 0.55°/px | 圆心附近或普通直线滑动的方向/角度换算 |
| `spin.dragFollowResponse` | `20...46 s⁻¹` | 同左 | 拖动加速响应，由 touch response 派生 |
| `spin.dragBrakeResponse` | `46...82 s⁻¹` | 同左 | 手指慢下来时更快制动 |
| `spin.maximumAngularSpeed` | `12...42 rad/s` | 同左 | 由 touch response 派生，不再独立覆盖 |
| `gesture.releaseQualification` | `28 px / 70 ms / 220 px/s / 62%` | 真机待调 | 四项同时满足才进入 fling |
| `gesture.dragActivationDistance` | 2.5 pt（按 DPI 换算） | 2.5 pt（按 DPI 换算） | 降低“已经滑了但尚未抓住”的概率 |
| `gesture.fallbackTouchRadius` | 短边 48% | 短边 48% | 两个模型的有效圆形触摸区 |
| `gesture.reversalConfirmation` | 18 px / 1.5 rad/s | 同左 | 过滤单帧方向噪声，确认后才进入反向制动 |
| `gesture.tapMaximumDuration` | 0.28 s | 0.28 s | 点击的最长持续时间 |

旋转映射同时使用二维切向角度与屏幕速度：圆周拖动会依据相机朝向换算到真实旋转轴，圆心附近和普通横/竖滑动则保持与手指及松手甩动同向。屏幕速度会约束角度估计，避免圆心附近一两个像素被放大成满速；pressure 不再参与转速，避免与 Haptic“力度”及设备能力重叠。拖动使用减速快于加速的速度伺服；合格 fling 直接设定松手速度，不再叠加 impulse。

日常设置提供“拖动响应”和“惯性阻力”两个正交滑杆。SwiftUI 只保存并发送归一化值；所有派生范围都由 `FidgetSpinnerMotion` 负责。阻力经 `ResistanceToCoastHalfLife` 映射：`0% = 12 s`（长滑行），`100% = 0.22 s`（明显制动）。它不改变拖动速度，也不改变单次 Haptic 的 Decay。

## 双指捏合缩放

| 参数名称 | 当前代码值 | 建议目标值 | 备注 |
|----------|------------|------------|------|
| `pinch.inputBackend` | Enhanced Touch | Enhanced Touch | 使用 `Touch.activeTouches`；已应用 |
| `pinch.activationDistance` | 6 pt（按 DPI 换算） | 6 pt（按 DPI 换算） | 两指距离变化超过阈值后开始缩放；已应用 |
| `pinch.zoomSensitivity` | 0.0040 | 0.0040 | 两指距离变化对相机距离的影响；已应用 |
| `pinch.minimumZoomScale` | 0.58 | 0.58 | 最近缩放距离倍率；已应用 |
| `pinch.maximumZoomScale` | 2.0 | 2.0 | 最远缩放距离倍率；已应用 |
| `pinch.smoothingTime` | 0.06 s | 0.06 s | 缩放跟随的平滑时间；已应用 |
| `pinch.motionWeightWhilePinching` | 100% | 15% | 需和陀螺仪一起真机调试 |

## 滑动 Haptic（真机待调）

| 参数名称 | 当前代码值 | 建议目标值 | 备注 |
|----------|------------|------------|------|
| `haptic.backend` | `UISelectionFeedbackGenerator` | `CHHapticEngine` | 需在真机上实现与调试 |
| `haptic.drag.spacing` | 34 px | Core Haptics 连续反馈 | 旧的像素间隔触发方式 |
| `haptic.drag.minimumInterval` | 0.055 s | 0.033 s 动态参数更新 | 对应约 30 Hz 更新率 |
| `haptic.drag.intensityMin` | 系统固定 | 0.28 | 需在真机上调试 |
| `haptic.drag.intensityMax` | 系统固定 | 0.90 | 需在真机上调试 |
| `haptic.drag.sharpnessMin` | 系统固定 | 0.45 | 需在真机上调试 |
| `haptic.drag.sharpnessMax` | 系统固定 | 0.90 | 需在真机上调试 |
| `haptic.drag.pulseFrequencyMin` | 约 18 Hz 上限 | 18 Hz | 低速滑动的颗粒频率 |
| `haptic.drag.pulseFrequencyMax` | 约 18 Hz 上限 | 45 Hz | 高速滑动的颗粒频率 |
| `haptic.tap.intensity` | Light 样式 | 0.55 | 需在真机上调试 |
| `haptic.tap.sharpness` | 系统固定 | 0.65 | 需在真机上调试 |
| `haptic.fling.intensity` | Medium 样式 | 0.85 | 建议范围 0.75–0.95 |
| `haptic.fling.sharpness` | 系统固定 | 0.80 | 需在真机上调试 |

建议的滑动强度映射：

```text
speed01 = clamp(abs(horizontalVelocity) / 1050, 0, 1)
intensity = 0.28 + 0.62 * pow(speed01, 0.65)
sharpness = 0.45 + 0.45 * speed01
```

## 陀螺仪与镜头体感（真机待调）

| 参数名称 | 当前代码值 | 建议目标值 | 备注 |
|----------|------------|------------|------|
| `motion.sampleRate` | 60 Hz | 60 Hz | Core Motion 更新频率 |
| `motion.maximumInputAngle` | 18° | 12° | 达到最大镜头偏移所需的手机倾斜角 |
| `motion.response` | 8 | 13 | 镜头跟随响应速度 |
| `motion.gyroscopeLead` | 0.035 | 0.070 | 角速度前馈量 |
| `motion.maximumOrbitDegrees` | 6.5° | 9° | 镜头最大环绕角度 |
| `motion.deadZone` | 视差层 0.045 归一化（18° 输入约 0.8°） | 0.5...1.2° | 只过滤视觉视差的手持微抖，不改变 Shake/Inertia |
| `motion.horizontalGain` | 1.0 | 1.0 | 横向体感增益 |
| `motion.verticalGain` | 1.0 | 0.85 | 纵向体感增益 |
| `motion.parallaxFarPixels` | 6 px | 4...8 px | 远景背景最大屏幕位移 |
| `motion.parallaxMidPixels` | 12 px | 8...15 px | 羽化平台中景最大屏幕位移 |
| `motion.parallaxForegroundPixels` | 20 px | 14...24 px | 相机投影/模型最大屏幕位移 |
| `motion.parallaxResponse` | 11 s⁻¹ | 8...14 s⁻¹ | 帧率无关指数平滑；叠加在输入控制器已有平滑之后 |
| `motion.weightWhileDragging` | 100% | 35% | 手指滑动期间降低镜头干扰 |
| `motion.weightWhilePinching` | 100% | 15% | 捏合期间降低镜头干扰 |
| `motion.restoreDuration` | 无 | 0.25 s | 手势结束后恢复完整体感的时间 |
| `motion.attitudeRepresentation` | Euler roll/pitch | 相对 quaternion | 需修改原生桥接并在真机验证坐标轴 |

## App 内体感仪表盘

底部导航栏选择“体感”后，会显示 SwiftUI 调参面板。滑杆调整会通过 `UnitySendMessage` 在 `Main Camera` 上实时预览，但不会立即覆盖已保存配置；点击“确认”后才写入 iOS `UserDefaults`，App 下次启动时自动恢复并重新应用。

| 仪表盘参数 | 默认值 | 可调范围 | 步进 |
|------------|--------|----------|------|
| `motion.maximumInputAngle` | 18° | 4–30° | 1° |
| `motion.response` | 8 | 1–24 | 1 |
| `motion.gyroscopeLead` | 0.035 | 0–0.15 | 0.005 |
| `motion.maximumOrbitDegrees` | 6.5° | 0–24° | 0.5° |

仪表盘另外提供：

- “复位”：把四个草稿参数恢复到以上默认值并立即预览，不自动保存或关闭。
- “确认”：持久保存当前草稿值、将当前手机姿态设为新的中心参考，并关闭面板返回“陀螺”。
- 未点击“确认”而直接离开“体感”时，放弃草稿并重新应用上一次已保存的值。

## Unity 构建 duplication 预检

每次 iOS / Simulator 导出前，`IosBuildPipeline` 会自动执行生成缓存预检：

1. 先扫描 `Assets` 中的 `.cs/.swift/.m/.mm/.h/.hpp/.cpp`。发现 `文件名 2.swift` 这类有正式同名文件的源代码副本时，立即阻止构建并列出冲突，不自动修改源文件。
2. 再扫描 `Library/Bee/artifacts`（Unity 可重建缓存），识别存在正式同名 DLL 的数字后缀副本，例如 `Assembly-CSharp 3.dll`。
3. 少于 20 个缓存冲突时，旧副本移入 `/tmp/CodexUnityGeneratedDuplicates/<时间戳>`；若副本较新，则保留较新内容为正式文件并隔离旧正式文件。
4. 达到 20 个缓存冲突时，将整个可重建缓存同卷原子重命名为 `Library/Bee/artifacts.codex-quarantine-<时间戳>`，避免 iCloud 跨卷移动失败、逐文件处理和残留污染。
5. 全部预检通过后才进入 IL2CPP / Xcode 导出，并在 Unity Console 记录隔离数量与路径。

也可从 Unity 菜单手动执行 `Tools > Codex > Clean Generated Cache Duplicates`。

## 纯 3D 场景基线

| 场景参数 | 当前值 | 备注 |
|----------|--------|------|
| `scene.floor` | 已移除 | 不再创建 `StudioFloor` 平面 |
| `scene.pedestal` | 已移除 | 不创建 `DisplayPedestal`、托盘或任何承托几何体 |
| `scene.motionSpace` | `GyroAlignedSpace` | 仅作为不可见的体感坐标系，原点悬置陀螺 |
| `scene.cameraRig` | `GyroCameraRig` | 以虚空中的陀螺原点为体感运动轴心 |
| `scene.cameraPosition` | `(0, 10.4, -3.8)` | 约 20° 斜视角，显示模型厚度且不暗示支撑平面 |
| `scene.cameraFov` | 39° | 透视相机 |
| `scene.background` | Procedural Skybox | 全屏渲染的三维空间环境，不使用背景平面或图片 |
| `scene.visibleGeometry` | 仅 `FidgetSpinner` | 灯光、相机和体感坐标系均不可见 |

## 验收记录

| 项目 | 状态 | 备注 |
|------|------|------|
| 单指慢滑与快滑有明显速度差 | 待验证 | 可先在 Unity 编辑器与触摸模拟中验证 |
| 松手甩动惯性自然 | 待验证 | 可先开发，最终需真机确认 |
| 双指张开放大、合拢缩小 | 待验证 | 必须在中间 Unity 内容区域支持两点触控 |
| Haptic 强度和频率随滑速变化 | 真机待调 | Simulator 不支持真实触感验收 |
| 手机倾斜产生稳定镜头视差 | 真机待调 | 需检查 Portrait 坐标映射与参考姿态 |

## 参数所在代码

- `Assets/Scripts/FidgetSpinner/FidgetSpinnerController.cs`
- `Assets/Scripts/FidgetSpinner/PortraitCameraFramer.cs`
- `Assets/Scripts/FidgetSpinner/DeviceMotionController.cs`
- `Assets/Scripts/FidgetSpinner/IosHaptics.cs`
- `Assets/Plugins/iOS/CodexIosHaptics.mm`
- `Assets/Plugins/iOS/CodexIosDeviceMotion.mm`
