# Fidgeting 物理交互与 Haptic 系统规格

项目：`Fidget Spinner`  
Bundle ID：`com.jiaweizhou.fidgetspinner.codex`  
版本：Draft 1  
最后更新：2026-08-02

## 1. 目标与边界

这份规格把 Fidgetable 一类数字玩具的设计方式拆成四层：

```text
Touch / Motion / Physics
        ↓
Mechanism（机械模型）
        ↓
Semantic Event（语义事件）
        ↓
Haptic Recipe + Mapping
        ↓
Core Haptics / Taptic Engine
```

核心规则：

1. 输入设备不直接播放 Haptic。输入先驱动物理或机械模型，再由模型发出语义事件。
2. Haptic 跟随真实状态变化，例如实际跨过档位、发生碰撞或完成吸附，而不是只跟随手指移动距离。
3. 每个语义事件拥有独立 `HapticRecipe`。全局设置只作为倍率或偏移，不覆盖 Recipe 的身份。
4. 自由轮、磁吸棘轮、设备旋转和 Shake 是不同 Mechanism，但可以复用相同的 Tick、Snap、Burst 等 Recipe。
5. 三叶金属启动与静止时角速度必须为零。没有手指、设备动作或显式玩法输入时，任何模式都不得自行续转。

Fidgetable 的源码、AHAP 和默认 waveform 没有公开。下面对它的玩法结构属于基于公开交互和 Apple API 的实现拆解；数值是本项目的推荐真机调试基线，不声称是 Fidgetable 的私有数值。

## 2. iOS Haptic 能力与专用名词

### 2.1 三个相关系统

| 系统 | 用途 | 本项目使用原则 |
| --- | --- | --- |
| `UIFeedbackGenerator` | 系统定义的 Selection、Impact、Notification | 用于普通 UI、设置确认和不支持自定义 Haptic 时的 fallback |
| `Core Haptics` | 自定义触觉事件、pattern、动态参数、曲线和音频同步 | 用于所有玩具机械感 |
| `Core Motion` | 姿态、角速度、重力、用户加速度 | 用于 Tilt、Rotate 360、Shake、甩动和设备驱动玩法 |

系统 preset 包括：

- `UISelectionFeedbackGenerator`：选择或档位变化。
- `UIImpactFeedbackGenerator`：Light、Medium、Heavy、Soft、Rigid。
- `UINotificationFeedbackGenerator`：Success、Warning、Error。

这些 preset 有固定语义。玩具内部的 Pop、Snap、Bearing、Magnetic Detent 应优先使用 Core Haptics 自定义 pattern。

### 2.2 Core Haptics 官方对象

| 名称 | 含义 |
| --- | --- |
| `CHHapticEngine` | App 与触觉硬件之间的长期连接；负责创建 player 和播放 pattern |
| `CHHapticPattern` | 一个完整触觉波形，由事件、参数和参数曲线构成 |
| `CHHapticEvent` | Pattern 内的单个触觉或音频事件 |
| `CHHapticPatternPlayer` | 播放、停止 pattern，并发送动态参数或曲线 |
| `CHHapticAdvancedPatternPlayer` | 在普通 player 基础上支持循环、暂停、恢复、seek、播放速率和 completion |
| `CHHapticEventParameter` | 事件创建时的静态参数 |
| `CHHapticDynamicParameter` | 播放过程中立即改变参数 |
| `CHHapticParameterCurve` | 在多个控制点之间线性插值，使参数平滑变化 |
| AHAP | Apple Haptic and Audio Pattern；JSON 兼容的触觉/音频资源文件 |

### 2.3 官方事件与参数

| 参数 | 常用范围 | 含义 |
| --- | ---: | --- |
| `hapticTransient` | 瞬时 | 一个短促冲击；没有可感知的持续时间，适合 Tick、Click、Pop、碰撞 |
| `hapticContinuous` | `duration > 0` | 持续振动，适合 Vibrate、Rumble、Bearing Texture |
| `hapticIntensity` | `0...1` | 事件基础力度；接近振幅概念，但人的感知并非线性 |
| `hapticSharpness` | `0...1` | 触感从圆润、厚重到清脆、机械；不是直接指定马达频率 |
| `relativeTime` | 秒 | 事件相对于 pattern 起点的开始时间 |
| `duration` | 秒 | Continuous 事件持续时间 |
| `attackTime` | `0...1` | Continuous 包络的起振时间调节量；更高会指数式延长，不直接等于秒 |
| `decayTime` | `0...1` | Continuous 包络的衰落时间调节量；`sustained = 0` 时生效 |
| `releaseTime` | `0...1` | Continuous 包络的释振时间调节量 |
| `sustained` | `0 / 1` | `1` 使用 Attack/Release；`0` 使用 Attack/Decay |

动态参数的计算方式：

- `hapticIntensityControl`：`0...1`，与事件基础 intensity 相乘。
- `hapticSharpnessControl`：`-1...1`，与事件基础 sharpness 相加并裁剪。
- Attack、Decay、Release 的动态 control 通常为 `-1...1`，以默认值为中心缩短或延长包络。
- 设备的实际 min、max、default 应通过 `attributes(forDynamicParameter:)` 查询，避免假设所有硬件完全一致。

`CHHapticParameterCurve` 会影响 pattern 中所有相关事件，不能只绑定其中一个 pulse。需要每个 pulse 拥有不同纹理时，应分别创建事件参数或使用专门的 AHAP/Recipe，不要只依赖一条全局曲线。

### 2.4 本项目的语义词，不是 Apple 原生事件类型

| 名词 | 本项目定义 |
| --- | --- |
| `Click` | 按钮闭合或开关完成的一次明确冲击 |
| `Tick` | 轻量、重复、短促的进度/档位提示 |
| `Detent` | 机械档位或稳定点；跨过一个档位通常产生一个 Tick |
| `Snap` | 元件被弹簧或磁力快速吸到稳定位置；通常比 Tick 更重 |
| `Pop` | 形变累积到阈值后突然释放，常用尖锐主脉冲加弱尾脉冲 |
| `Pulse` | 单个可计数触觉单元；可以是 transient，也可以是短 continuous |
| `Burst` | 多个 pulse 在很短时间内组成的爆发序列；不是 Core Haptics enum |
| `Rumble` | 较低 sharpness 的持续、缓慢变化触觉 |
| `Buzz` | 比 Rumble 更集中、更机械的持续触觉 |
| `Hybrid` | 本项目定义的 transient + continuous 叠加，不是 Apple 官方事件类型 |
| `Mapping` | 把速度、碰撞冲量、角度或加速度归一化后映射到 Haptic 参数 |
| `Breakaway` | 输入超过脱档阈值，从锁定档位释放 |
| `Capture` | 低速进入吸附区域并选择最近档位 |
| `Hysteresis` | 进入和退出使用不同阈值，避免状态在边界反复抖动 |
| `Cooldown` | 一次触发后的最短静默时间，避免重复触发或马达饱和 |
| `Rate Limit` | 限制每秒最多播放的触觉事件数 |
| `Dead Zone` | 忽略微小输入的范围 |
| `Jerk` | 加速度的变化率，用于区分快速甩动和缓慢搬动手机 |

`pulseCount`、`pulseInterval`、`endIntensity`、`endSharpness`、`Hybrid` 都是本项目的封装参数，不应在代码或 UI 中冒充 Apple 官方参数。

## 3. Fidgetable 玩法的可复用拆解

Fidgetable 的公开页面与 App Store 素材展示了 One Button、Four Buttons、Vibrate、Pop、Snap、Bubble Wrap、Dial、Bounce、Tilt、Shake、Rotate 等玩法，并将 Tap、Swipe、Hold、Shake、Tilt 等输入与 Core Haptics 组合。以下不是对其私有实现的反编译，而是把这些可观察玩法还原为可以在本项目独立实现的机械状态机、语义事件和 Recipe。

### 3.1 Button

**物理隐喻**：弹簧按钮、键盘轴或遥控器按键。

**输入与状态**：

```text
Idle → Pressing → BottomedOut → Releasing → Idle
```

- Touch Down 开始压缩视觉弹簧。
- 位移或时间超过 `actuationThreshold` 时只触发一次 `ButtonActuated`。
- Touch Up 触发 `ButtonReleased`。
- 如果手指没有达到阈值就离开，只回弹，不播放完整 Click。

**推荐 Recipe**：

| 事件 | 类型 | Intensity | Sharpness | 节奏 |
| --- | --- | ---: | ---: | --- |
| `ButtonActuated` | transient | 0.55 | 0.88 | `t=0` |
| `ButtonReleased` | transient | 0.24 | 0.48 | 松手立即 |
| `HeavyButtonActuated` | 2× transient | 0.72 / 0.28 | 0.78 / 0.50 | `0 / 38 ms` |

**封装参数**：

- `mechanism.button.actuationThreshold = 0.62`
- `mechanism.button.travel = 1.0`
- `mechanism.button.springResponse = 18`
- `mechanism.button.releaseResponse = 14`
- `haptic.recipe.buttonPress.*`
- `haptic.recipe.buttonRelease.*`

### 3.2 Vibrate

**物理隐喻**：持续运行的小马达、电动剃须刀或低频振动器。

**输入与状态**：

```text
Idle → Starting → Running → Stopping → Idle
```

- 按住或拖入控制区域时启动一个长期保存的 `CHHapticAdvancedPatternPlayer`。
- 运行期间以 30–60 Hz 读取速度、触点距离或用户滑杆，并发送 dynamic parameters。
- Touch Up、App 进入后台或输入取消时明确停止 player。
- 不要在每帧创建新的短 continuous event 来假装持续振动。

**推荐 Recipe**：

- `eventType = continuous`
- `baseIntensity = 0.22`
- `baseSharpness = 0.24`
- `attackTime = 0.025 s`
- `releaseTime = 0.060 s`
- `loopEnabled = true`
- 动态 intensity 范围 `0.12...0.48`
- 动态 sharpness 范围 `0.12...0.42`

### 3.3 Pop

**物理隐喻**：软膜、吸盘、按压玩具越过屈曲点后突然反转。

**输入与状态**：

```text
Ready → Deforming → Popped → Resetting → Ready
```

- 以按压距离、按压时长或拖拽形变量计算 `deformation01`。
- 当其从阈值下方跨到上方时发出一次 `PopThresholdCrossed`。
- 必须回到 reset threshold 以下后才能再次触发，形成 hysteresis。

**推荐 Recipe**：

```text
t = 0 ms   transient(intensity: 0.72, sharpness: 0.96)
t = 28 ms  transient(intensity: 0.20, sharpness: 0.62)
```

**封装参数**：

- `mechanism.pop.triggerThreshold = 0.68`
- `mechanism.pop.resetThreshold = 0.28`
- `mechanism.pop.minimumPressTime = 0.04 s`
- `mechanism.pop.cooldown = 0.10 s`

### 3.4 Bubble Wrap

**物理隐喻**：独立气泡组成的可破裂网格。

它不是一个“大 Pop”，而是 `PopMechanism` 的多实例版本：

- 每个 Cell 保存 `Ready / Popped / Respawning` 状态。
- Tap 命中一个 Cell；Drag 通过新的 Cell 时逐个触发。
- 同一个 Cell 在复位前不能重复触发。
- 全局使用 `minimumInterPopInterval`，防止快速扫过时重叠到无法分辨。
- 可用轻微随机值避免每个气泡完全相同，但随机范围必须小。

**推荐参数**：

- `grid.rows / columns`：由布局决定。
- `bubble.hitRadius = 0.82 × visualRadius`
- `bubble.respawnDelay = 1.8 s`，或全部完成后批量复位。
- `bubble.minimumInterPopInterval = 0.025 s`
- `bubble.intensityVariation = ±0.06`
- `bubble.sharpnessVariation = ±0.04`

### 3.5 Snap

**物理隐喻**：磁吸滑块、弹簧滑块或多个稳定点之间的快速吸附。

**状态机**：

```text
Captured → Loading → Breakaway → Traveling → Capturing → Captured
```

- Handle 在当前 detent 周围移动时积累位移或输入速度。
- 低于 breakaway threshold 时仍吸附在原档位。
- 超过阈值后进入 Traveling。
- 经过下一个档位的 capture region 时吸附并发出 `DetentCaptured`。
- 进入与退出阈值必须不同，避免边界抖动。

**推荐 Recipe**：

| 事件 | 类型 | Intensity | Sharpness | 说明 |
| --- | --- | ---: | ---: | --- |
| `Breakaway` | transient + impact layers | 0.78 | 0.94 | 脱档的干脆断开感 |
| `DetentCrossed` | 单个 isolated transient | 由活动预设直接给出 | 由活动预设直接给出 | 不叠层、不做速度倍率；音频由独立 physics renderer 消费同一跨档 |
| `DetentCaptured` | Hybrid，2 pulses | 0.95 / 0.42 | 0.90 / 0.58 | `0 / 36 ms` |

第五款磁吸推牌已经把这套状态机实现为 `MagneticDetentTrack1D`。它不是两端补间：六个稳定点为 `0 / 13.6 / 27.2 / 40.8 / 54.4 / 68.0 mm`，默认停在第 3 个真实磁力井 `27.2 mm`；该位置映射为模型零视觉偏移，因此首次触摸即可向左或向右脱档，而不是从单向端点出发。手指位置作为弹簧目标，滑盖由质量、阻尼、摩擦和连续磁势阱共同积分。物理、场景中的六枚磁体和 Haptic 都读取同一 `LinearMagneticDetentProfile`。

替代模型的旋转棘轮模式新增锁定设计要求：完整 `360°`、每 `12°` 一个 detent、每圈恰好 `30` 档。该旋转配置与上述六档线性轨道是两个机制通道；不能把 30 档写回现有线性 `LinearMagneticDetentProfile`。未来实现时，旋转物理与 Haptic 必须读取同一个机制设置。当前 DeliveryState 仅为 `specified-only`；runtime、Haptic、iPhone 触感与整圈计数均未实现或验证。隐藏齿、棘爪、滚珠、弹簧和耦合结构继续 unknown。

磁吸推牌的机械音频由独立 `MagneticSlideDetentAudio` renderer 消费同一条语义事件流，不读取原始手势，也不调用 Haptic renderer。只有经过输入授权的 `DetentCrossed` 会播放用户选定的 766 Hz 合金 click；`Breakaway` 和 `DetentCaptured` 都不发声，避免一次跨档听成“咔—嗒”两段。该资源是 48 kHz mono、0.93 s 容器，主要击发集中在前约 0.14 s；6 个预分配 2D `AudioSource` 保留快速跨档时的自然叠音。renderer 没有 `Update`、timeline、rate limit 或 scheduler。Reset、Library、AUTO 与程序化设姿由既有输入授权门保持静默。

详情交互镜头由 `EdcPortraitCameraFramer` 固定为正面 + 30° 顶视：相机 backward 为 `(0, 0.5, -0.866)`，因此 68 mm 滑轨严格映射到屏幕水平轴，不再被三分之四视角斜向压缩。详情主体目标占屏宽 72%，Library 以独立 `1.59×` zoom 保持原有预览尺度。`InteractionSurface` 随滑盖移动，尺寸为 `94 × 32 × 58 mm`；它只用于 raycast 命中和手势仲裁，不进入 Rigidbody、质量、磁力或档位积分。

Loading 阶段不再启动独立 continuous player，也不按触摸持续时间发声。慢搓只在势垒负载 `0.72 / 0.84 / 0.94` 三个空间里程碑各发一次 16 ms 有限提示，回落到 `0.55` 以下才重置；手指停住保持静默。真实跨档由同一个 `DetentCrossed` 同帧启动视觉衰减轻颤和一个有限三层包（主冲击 + 低锐度重量段 + 收尾触点），旋转高速纹理仍独占唯一循环 `CHHapticAdvancedPatternPlayer`。

第六款三层磁吸扇牌 `magnetic-fan-card` 不复用上述线性单位和六档配置，而是由独立 `FanCardDetentProfile` 在归一化坐标 `q` 上运行同一机械状态语义。四个稳定点为 `0 / 1⁄3 / 2⁄3 / 1`；中片角度=`45°q`，顶片角度=`90°q`，所以相邻层最大相对开合 `45°`、最外层总夹角 `90°`。慢推固定参数为：脱档负载 `0.050`、手指弹簧/阻尼 `96 / 6.0`、磁峰 `6.4`、轨道摩擦 `0.38`、捕获弹簧/阻尼 `118 / 14.2`、脱档冲量 `0.95`、捕获预测 `0.070 s`、可见预压倍率 `0.24`、最高速度 `2.4 s⁻¹`。快速模式在同一状态机内平滑混合到脱档 `0.024`、手指弹簧/阻尼 `220 / 5.2`、磁峰倍率 `0.50`、摩擦 `0.16`、脱档冲量 `1.8` 与最高速度 `5.0 s⁻¹`；两者均使用最大子步 `1/240 s`。

`FanCardController` 只在用户授权且机械状态真实变化时发布 `Breakaway / DetentCrossed / DetentCaptured`，再由 Coordinator 进入现有 `FidgetHapticRouter`；控制器内没有 `IosHaptics` 直连。输入不再要求手指绕右下机械轴画圆，而是把每帧屏幕位移投影到“当前三片整体视觉质心”的运动切线并连续积分。滑动速度 `0.55→1.30 屏宽/秒`、累计滑动距离、可用 pressure 增量和最近有效手势频率共同形成动态权重：慢推目标逐档跟随真实滑动幅度，只有足够快且有足够距离的手势才在松手后授权端点收尾，仍由同一四档状态机逐井越过；反向快速滑动可清脆收回。直接拖动与快速收尾期间暂停 Core Motion，并持续发布冻结的视差样本；完成后以当前设备姿态重新建立参考，避免轴心或视觉质心在手指下漂移。

独立 `FanCardMetalDetentAudio` 只监听同一语义流中的 `DetentCrossed`：一个事件严格对应一个低约 `2.6` 半音的厚合金 `PlayOneShot`，5 个原子变体由 8 个 2D 声部轮转；专属 Haptic renderer 将同一个事件按实际跨档速度映射为主冲击 `Intensity 0.92→1.00 / Sharpness 0.76→0.90`，并叠加 `32 ms` 重量段 `0.64 / 0.24` 和 `t=22 ms` 收尾 `0.56 / 0.42`。`Breakaway`、捕获、Library、AUTO、Reset 和程序设姿不发声或 Haptic。顶片与中片各一条同心内嵌弧轨及 3 枚磁体，中片与底片各一枚随动球，均读取同一全局 `q`；底片禁止滑轨。材质、正面图案、Library 设姿、AUTO、Reset 与 `SetFanProgress()` 不得制造 Haptic 或写回既有旋转/线性调节值；正面共同轴心只允许单枚低矮抛光轴承帽，结构轴标记不得渲染成额外金属环。

旋转、线性推牌和扇牌在详情 HUD 共享 `Speed / Intensity / Frequency` 三项展示，但单位和来源属于当前产品机制：线性推牌显示 `mm/s`，扇牌显示 `°/s`，旋转产品显示 RPM。推牌与扇牌的 Intensity/Frequency 来自本次用户手势与机械负载，不读取旋转 combo 的替代值；遥测只读机械状态，不参与 Haptic 授权。

### 3.6 Dial

**物理隐喻**：机械旋钮、表冠、相机模式拨盘。

- 使用 unwrapped angle，不能直接依赖会在 `0/360°` 或 `±π` 跳变的 Euler angle。
- `detentIndex = floor((angle + offset) / detentStep)`。
- 只有 `detentIndex` 变化时才产生 Tick。
- 快速跨过多个档位时，可以播放有限数量的 Tick，但要保留最终档位并受 rate limit 控制。
- Dial 可选择直接跟手或带少量惯性；它与 Spinner 的主要区别是档位语义比自由惯性更重要。

**当前产品预设**：

| 预设 | 档位/圈 | 间距 | Intensity | Sharpness |
| --- | ---: | ---: | ---: | ---: |
| Vault | 8 | 45° | 1.00 | 0.55 |
| Camera Dial（默认） | 12 | 30° | 1.00 | 0.72 |
| Watch Bezel | 24 | 15° | 0.85 | 0.90 |
| Silk Ratchet | 36 | 10° | 0.60 | 1.00 |

每次真实跨档只输出一个 transient。低于 `30 detents/s` 时没有持续底噪；超过阈值后停止逐档 transient，并切到单个循环 continuous player。Intensity/Sharpness 的实时覆盖只改活动配置，不产生第二套档位数。

## 4. 可以重组的原子模块

| 模块类别 | 原子模块 | 可组合用途 |
| --- | --- | --- |
| 输入检测 | Press、Hold、Drag、Rotary Drag、Pinch、Tilt、Twist、Shake、Collision | 不直接决定触觉纹理 |
| 机械模型 | Spring Button、Threshold Pop、Grid Cells、Freewheel、Detent Track、Magnetic Capture、Gravity Ball | 负责状态与事件 |
| 语义事件 | Pressed、Released、ThresholdCrossed、DetentCrossed、Breakaway、Captured、Collision、CoastStopped、DirectionReversed | Haptic Recipe 的稳定入口 |
| Haptic Recipe | Click、Tick、Pop、Snap、Burst、Rumble、Brake、Release、Reset | 可以被不同机械模型复用 |
| Mapping | Speed、Angular Speed、Collision Impulse、Acceleration、Jerk、Distance、Deformation、Zoom Scale | 将物理量归一化为 Haptic 参数 |

推荐组合：

```text
Freewheel Spinner
= Rotary Drag + Freewheel + Speed Mapping + Release + optional Bearing Rumble

Magnetic Ratchet Spinner
= Rotary Drag + Magnetic Detent Track + Breakaway + Tick + Capture Snap

Shake To Spin
= Shake Detector + Acceleration Mapping + Burst + Angular Impulse

Device 360 Dial
= Unwrapped Device Rotation + Detent Track + Tick

Tilt Gravity Toy
= Device Gravity + Collision Mechanism + Collision Mapping + Impact

Bubble Wrap
= Drag Hit Testing + Pop Cell Grid + Pop Recipe
```

## 5. Fidgeting App 建议玩法与参数

### 5.1 自由轮 Freewheel

**目标行为**：手指给予角速度，松手后按阻尼自然衰减，最终停住。静止后永不自行启动。

```text
Rest → FingerDriven → Coasting → Rest
```

推荐基线：

| 参数 | 默认值 | 建议范围 |
| --- | ---: | ---: |
| `physics.spin.initialAngularSpeed` | `0 rad/s` | 固定为 0 |
| `input.rotary.touchResponse` | `0.55` | `0...1` |
| `physics.spin.maxAngularSpeed` | 由 touch response 派生，默认约 `29 rad/s` | `12...42` |
| `physics.spin.resistance` | `0.58` | `0...1` |
| `physics.spin.coastHalfLife` | 由 resistance 派生，默认约 `1.18 s` | `0.22...12` |
| `physics.spin.stoppedSpeedThreshold` | `0.08 rad/s` | `0.03...0.15` |
| `input.rotary.sensitivityGain` | 由 touch response 派生 | `0.18...1.65` |
| `input.rotary.dragFollowResponse` | 由 touch response 派生 | `20...46 s⁻¹` |
| `input.rotary.dragBrakeResponse` | 由 touch response 派生 | `46...82 s⁻¹` |
| `input.rotary.screenSpeedForFullSpin` | 由 touch response 派生 | `1800...720 px/s` |
| `input.rotary.fallbackTouchRadius` | `0.36 × shortSide` | `0.32...0.40` |
| `input.rotary.reversalConfirmation` | `18 px` | `12...32 px` |

`coastHalfLife` 的定义：每经过一个 half-life，角速度减半。

```text
ω(t + dt) = ω(t) × 0.5^(dt / coastHalfLife)
```

自由轮默认不应该有明显 Detent。四款旋转模型只保留低噪程序化切风声：`RotorWindAudio` 只读真实绝对角速度，按 2 / 3 / 4 个叶片计算 blade-pass 节奏。主体为低通着色空气流，中频噪声占比不高于 `0.14`、高频 edge 不高于 `0.02`。每次 blade-pass 的首段是占周期 `0.14` 的立方衰减硬碰撞，只承载短促碰撞纹理；主段/尾段以 `3 ms` 完成攻击，最长 `65 ms` 且不超过周期 `0.72`。正式 App 音色采用用户当前选择的“明亮合金 100% / 整体音高 +9 半音”：主层正弦，次层与上层用包含安全三次泛音的三角金属波，混合为 `0.105 / 0.215 / 0.160`，碰撞亮边 `0.34`，四个 shipping scene 及重建器的唯一 `alloyResonance` 均为 `1.0`。固定偏移倍率为 `2^(9/12) ≈ 1.6818`，叠加后 App 三层实际范围为 `1125...1810 / 2588...4161 / 4669...7508 Hz`；250 RPM 验收点为 `1588 / 3651 / 6588 Hz`。三次泛音接近 Nyquist 时会自动退化为纯基频正弦，防止高层折叠失真。金属节奏严格等于 `RPM × bladeCount ÷ 60`；三层模态按真实 `20...400 RPM` 的 `normalizedSpeed^0.78` 同时跟随转速，所以加速会同时增加击发密度并升高材质音高，明亮合金的相对频率、波形、混合与 +9 半音偏移保持不变。120 / 400 RPM 的三叶模型 Click 约 24 / 7 ms，材质鸣响约 65 / 36 ms，因此能辨识材质但不会拖成大金属腔体长鸣，并会在下一片叶片到来前归零。两个包络全部由同一个 `alloyResonance` 控制，不存在第二个明亮强度。低频只提供重量，不承担清脆起音。听感增益使用 `0.62` 指数，`60 RPM` 已清楚起声、运行时约 `286 RPM` 达满幅，静止仍严格为零；网页当前的 250 RPM 只是验收参考，App 不获得固定或初始转速。renderer 在 `OnAudioFilterRead` mixer callback 内生成，参数响应为 `4 ms`，项目 DSP buffer 为 `256 samples`。画面、叶片节奏和金属音高读取同一真实速度，物理减速直接决定声音减速与消散，网页 `2.30 s` 停转模拟不作为独立 App 音尾。该 renderer 不写 Rigidbody，也不进入 Haptic pipeline。

### 5.2 磁吸棘轮 Magnetic Detent

**目标行为**：低于脱档力时停在最近档位；超过阈值才跨档；低速后重新捕获；捕获完成后角速度精确归零。

```text
Locked
  ├─ input < breakaway → Locked
  └─ input ≥ breakaway → Traveling
Traveling
  ├─ speed > captureSpeed → Traveling / Coasting
  └─ speed ≤ captureSpeed → Capturing → Locked
```

推荐基线：

| 参数 | 当前基线 | 建议范围 |
| --- | ---: | ---: |
| `mechanism.detent.countPerTurn` | `12`（Camera Dial） | `8 / 12 / 24 / 36` |
| `mechanism.detent.stepDegrees` | `30°` | 由活动预设 count 派生 |
| `mechanism.detent.breakawayAngularSpeed` | `2.2 rad/s` | `0.8...5` |
| `mechanism.detent.captureAngularSpeed` | `1.2 rad/s` | `0.3...2.5` |
| `mechanism.detent.snapResponse` | `16 s⁻¹` | `6...28` |
| `mechanism.detent.lockEpsilon` | `0.12°` | `0.05...0.5°` |
| `mechanism.detent.captureRadius` | `0.45 × step` | `0.25...0.49 × step` |
| `mechanism.detent.relockDelay` | `0.03 s` | `0...0.10 s` |

物理档位数量和 Haptic 档位数量必须读取同一个 `DetentFeelConfig.detentsPerRev`。切换预设时下一次机械跨档和下一次 Haptic 同时采用新值。

四款旋转模型在棘轮模式下都保留同一连续切风层，并在其上叠加只读取真实跨档事件的 click 层；click 与 Haptic renderer 完全分离：

- 物理一帧跨过多个 detent index 时逐个发事件；一个事件严格对应一个 `PlayOneShot`。
- 5 个 variant 都由同一枚咬合裁出，mono PCM、约 `48...52 ms`、无 reverb、首尾无静音 padding。
- variant round-robin，连续两击不得相同；每击再随机 `±1...2` 半音，高速增加 `0...1` 半音上扬。
- 音量使用与 Haptic speed texture 相同的 normalized angular speed 输入，但反向映射：慢速为完整单击，高速每击最低降到 `0.34×`；最近一次明确 flick 对后续 5 击追加递减增益。
- 12 个预分配 AudioSource 形成声部池。没有 rate limit、gate、timeline 或高速模式切换；高 RPM 的棘轮纹理由原子点击自然重叠，切风与合金空气共鸣仍由连续风声层表达。

后续如果要进一步提高物理真实性，应把当前“速度阈值脱档”升级为输入扭矩/切向位移阈值，并使用弹簧阻尼捕获：

```text
error = shortestAngle(targetDetent, angle)
snapTorque = stiffness × error - damping × angularSpeed
```

#### 5.2.1 第五款线性重磁推牌

`magnetic-slide-tile` 已采用力阈值而不是速度阈值：

```text
m·x'' = kh(xfinger-x) - ch·x' + Fmag(x) - crail·x' - Ffriction
Fmag = -Fpeak·sin(2πq)
```

`LinearMagneticDetentProfile` 的发布基线为：

| 参数 | 值 |
| --- | ---: |
| `detentPositions` | `0 / 13.6 / 27.2 / 40.8 / 54.4 / 68.0 mm` |
| `defaultDetent / bidirectionalRange` | `index 2 (27.2 mm) / 左 27.2 mm、右 40.8 mm` |
| `movingMass` | `55 g` |
| `handSpring / handDamping` | `100 N/m / 5.0 Ns/m` |
| `breakawayForce / magneticPeakForce` | `0.44 N / 0.42 N` |
| `railFriction / railDamping` | `0.085 N / 0.30 Ns/m` |
| `captureSpring / captureDamping` | `150 N/m / 5.8 Ns/m` |
| `visiblePreload` | `≤ 0.9 mm` |
| `captureRadius / captureEntrySpeed` | `4.0 mm / 45 mm/s` |
| `lockPosition / lockSpeed` | `< 0.10 mm / < 0.0045 m/s` |
| `integration` | `≤ 1/240 s`，每帧最多 8 子步 |

松手以当前位置加短时速度预测选择最近档位。低于脱档力时逻辑位置保持在当前档，只允许视觉预压；跨越阈值只发一次 Breakaway；每越过一个相邻势垒发一个 DetentCrossed；捕获满足误差和速度条件后把位置对齐档位并把速度严格归零。

推牌 Haptic 完全由空间和机制状态驱动，不由触摸时长驱动。慢搓接近同一势垒时，三个有限边缘提示从 `Intensity 0.20 / Sharpness 0.18` 增至 `0.38 / 0.32`，每个 16 ms 且不循环。线性跨档固定使用一个有限三层包：`t=0 ms` 主 transient `0.98 / 0.78`，同时开始的 `30 ms` 低锐度 continuous 重量段 `0.58 / 0.22`，`t=22 ms` 收尾 transient `0.52 / 0.44`；`Breakaway` 与 `DetentCaptured` 不补额外冲击。该 tuning 不读取旋转 Detent Lab，也不套用旋转高速限流。AUTO、Library、Reset 和 `SetSlideProgress()` 不授权 Haptic。

### 5.3 手指拖拽与 Flick

| 参数 | 默认值 | 建议范围 |
| --- | ---: | ---: |
| `input.drag.activationDistance` | `6 pt` | `4...10 pt` |
| `input.rotary.minimumScreenDelta` | `0.75 px` | `0.5...2 px` |
| `input.rotary.maximumSampleAngle` | `24°/frame` | `12...30°` |
| `input.rotary.fallbackTouchRadius` | `0.36 × shortSide` | `0.32...0.40` |
| `input.rotary.minimumWorldRadius` | `0.008` | 模型尺寸相关 |
| `haptic.detent.minimumInterval` | `0.025 s` | `0.020...0.050 s` |

离散区不再用速度修改单次触点；其 Intensity/Sharpness 必须精确等于活动预设。高速区的唯一 Mapping 为：

```text
clickRate = abs(angularSpeed) / (2π) × detentsPerRev
continuousIntensityControl = normalizedSpeed × preset.intensity
continuousSharpnessControl = preset.sharpness
```

`clickRate > 30/s` 进入 continuous；衰减回 `27...30/s` 的回差带时恢复离散触点，同时把残余 continuous 限制在 `≤ 0.05`，随后完全停止。

### 5.4 设备倾斜 Tilt / Gyroscope

当前项目使用 60 Hz Device Motion、相对姿态和 rotation-rate lead。建议保留以下基线：

| 参数 | 默认值 | 建议目标 |
| --- | ---: | ---: |
| `motion.sampleRate` | `60 Hz` | `60 Hz` |
| `motion.maximumInputAngle` | `18°` | `12...18°` |
| `motion.response` | `8 s⁻¹` | `10...14 s⁻¹` |
| `motion.gyroscopeLead` | `0.035` | `0.04...0.08` |
| `motion.maximumOrbit` | `6.5°` | `6...10°` |
| `motion.deadZone` | `0.8°` | `0.5...1.2°` |
| `motion.weightWhileDragging` | `0.35` | `0.2...0.5` |
| `motion.weightWhilePinching` | `0.15` | `0...0.25` |
| `motion.restoreDuration` | `0.25 s` | `0.15...0.4 s` |

当前整场景视差实现复用同一份过滤后 tilt，不启动第二个传感器：

```text
CMMotionManager / Input System
        ↓
DeviceMotionController / MetalDeviceMotionController
        ↓
SceneParallaxInput
        ↓
SpinnerSceneParallaxController
        ├─ 相机投影 / 前景模型：±20 px
        ├─ 羽化平台中景：±12 px
        └─ 远景背景：±6 px
```

- 视差只修改相机投影和相机子节点的背景板，不修改 Rotor Transform、Rigidbody、角速度或 Haptic。
- 使用 `0.045` 归一化径向 dead zone 与 `11 s⁻¹` 帧率无关指数平滑；设备 tilt 已在输入控制器内做第一层平滑。
- 桌面/Editor 没有近期传感器样本时，以鼠标相对视口中心的位置作为 fallback；batch test 保持静止。
- iOS 原生产品使用 `CMMotionManager.startDeviceMotionUpdates`，不是 Safari/WKWebView 的 `DeviceOrientationEvent`，因此不实现 iOS 13 网页专用的 `requestPermission()` 点击授权流程。

Tilt 有两种不同玩法，不能混为一谈：

1. `Camera Parallax`：只移动观察视角，不向陀螺物理体施加力。
2. `Gravity Drive`：将设备重力投影为物理力或转矩，适合 Bounce/Tilt 玩具。

### 5.5 手机 360° 旋转 Device Twist

用途：将手机本体视为一个无限 Dial，或让用户转动手机来驱动模型和 Detent。

- 使用 quaternion 相对姿态或对 yaw 做 unwrap。
- 不可直接相减两个 Euler yaw；跨过 `±180°` 时会产生假跳变。
- 也可以积分指定轴的 `rotationRate × dt`，再用姿态数据缓慢校正漂移。

推荐基线：

- `twist.detentsPerTurn = 24`
- `twist.deadZone = 1.0°`
- `twist.rateForFullIntensity = 5 rad/s`
- `twist.minimumTickInterval = 0.030 s`
- `twist.recenterOnActivate = true`
- `twist.accumulatedAngle` 使用 `Double` 或周期性安全归一化。

### 5.6 Pinch Zoom

Pinch 主要是视觉/操作能力，不宜每帧振动。建议只在这些事件触发：

- 开始缩放：非常轻的 Selection。
- 跨过离散 zoom stop：Tick。
- 到达最小/最大边界：Rigid Edge Tick。
- 松手并吸附到标准倍率：Snap。

推荐 zoom stop：`0.75× / 1.0× / 1.25× / 1.5× / 2.0×`。

### 5.7 设备惯性触点与快速甩动

iOS bridge 已输出 `CMDeviceMotion.userAcceleration`。触觉重量感与原有“甩动驱动陀螺”物理规则是两个独立通道：前者只播放 Haptic，后者保持既有物理阈值和角冲量。

惯性触点基线：

| 参数 | 当前值 |
| --- | ---: |
| `inertia.thresholdOn` | `0.30 g` |
| `inertia.thresholdOff` | `0.22 g` |
| `inertia.maximumAccelForMapping` | `1.50 g` |
| `inertia.maximumRate` | `8/s`（125 ms gate） |
| `inertia.intensity` | `0.25...0.40` |
| `inertia.sharpness` | `0.20...0.35` |

惯性触点使用独立 isolated transient player，不停止 continuous texture，也不抢占或中断 detent transient。以下 Shake 状态机只描述保留的物理甩动输入：

状态机：

```text
Armed → ThresholdCrossed → Triggered → Cooldown → Armed
```

推荐检测：

```text
accelMagnitude = length(userAcceleration)       // 单位约为 g
jerk = abs(accelMagnitude - previous) / dt

trigger when:
accelMagnitude >= thresholdOn
and jerk >= jerkThreshold
and cooldown finished

re-arm when:
accelMagnitude <= thresholdOff
```

推荐基线：

| 参数 | 默认值 | 建议范围 |
| --- | ---: | ---: |
| `shake.thresholdOn` | `1.55 g` | `1.2...2.2 g` |
| `shake.thresholdOff` | `0.65 g` | `0.4...0.9 g` |
| `shake.jerkThreshold` | `8 g/s` | `5...14 g/s` |
| `shake.minimumPeakDuration` | `0.025 s` | `0.015...0.06 s` |
| `shake.cooldown` | `0.14 s` | `0.10...0.25 s` |
| `shake.maximumAccelForMapping` | `3.0 g` | `2.5...4 g` |
| `shake.spinImpulseMax` | `10 rad/s` | `4...18 rad/s` |

当前产品不再由 Shake detector 播放明亮 Burst；达到 0.3g 的动作由低锐度 inertia channel 反馈，明确甩动仍可按既有方向给三叶陀螺角冲量。

## 6. 推荐 Haptic Recipe Library

| Recipe ID | 类型 | 起始 I / S | 其他事件或终点 | 主要用途 |
| --- | --- | ---: | --- | --- |
| `tick.light` | transient | `0.30 / 0.84` | 无 | Dial、轻档位 |
| `detent.activePreset` | 单个 isolated transient | 活动 `DetentFeelConfig` | Intensity/Sharpness 为最终值；不承载音频 | Spinner、Dial |
| `button.press` | transient | `0.55 / 0.88` | 无 | Button |
| `button.release` | transient | `0.24 / 0.48` | 无 | Button 回弹 |
| `pop.membrane` | 2× transient | `0.72 / 0.96` | `28 ms: 0.20 / 0.62` | Pop、Bubble Wrap |
| `snap.breakaway` | transient | `0.78 / 0.94` | 冲击叠层 `1.55×` | 磁吸脱档 |
| `snap.capture` | hybrid，2 pulses | `0.95 / 0.90` | `36 ms: 0.42 / 0.58`，叠层 `1.75×` | 吸附落位 |
| `detent.highSpeedBlur` | continuous loop | `normalizedSpeed × preset I / preset S` | `>30 detents/s`，回差带底噪 `≤0.05` | 高速棘轮纹理 |
| `vibrate.motor` | continuous loop | `0.12...0.48 / 0.12...0.42` | Attack 25 ms，Release 60 ms | 按住振动 |
| `inertia.massShift` | isolated transient | `0.25...0.40 / 0.20...0.35` | `≥0.3g`，最大 `8/s` | 设备重量感 |
| `collision.impact` | transient | `0.25...0.90 / 0.45...0.82` | 碰撞冲量 Mapping | Bounce、落地 |
| `brake.reversal` | 3× transient | `0.82 / 0.82` | 45 ms 间隔递减，叠层 `1.55×` | 反向制动 |
| `reset.confirm` | 2× transient | `0.84 / 0.94` | `32 ms: 0.22 / 1.0`，叠层 `1.45×` | 复位确认 |

## 7. 参数命名与数据结构

推荐将配置拆成四个对象，而不是一个全局 Haptic 面板控制全部事件。

### 7.1 `HapticRecipe`

```text
id
eventType                 transient | continuous | hybrid(app wrapper)
events[]                  每个事件自己的 relativeTime / intensity / sharpness
durationSeconds
attackTimeAdjuster        0...1, not seconds
decayTimeAdjuster         0...1, sustained must be false
releaseTimeAdjuster       0...1, not seconds
sustained
dynamicIntensityControl   0...1
dynamicSharpnessControl   -1...1
dynamicAttackControl      -1...1
dynamicDecayControl       -1...1
dynamicReleaseControl     -1...1
loopEnabled
cooldownSeconds
allowLayering
priority
fallbackPreset
```

### 7.2 `InputMapping`

```text
source                    speed | angularSpeed | acceleration | jerk |
                          collisionImpulse | distance | deformation
sourceMin
sourceMax
deadZone
curve                     linear | power | smoothstep
curveExponent
outputMin
outputMax
smoothing
hysteresis
```

### 7.3 `MechanismProfile`

```text
id
mechanismType             freewheel | magneticDetent | button |
                          pop | dial | gravityBall
physicsParameters
inputBindings
semanticEventBindings
```

### 7.4 `FidgetProfile`

```text
id
displayName
mechanismProfile
hapticRecipeOverrides
visualProfile
soundProfile
userAdjustableParameters
```

命名层次统一为：

```text
haptic.global.masterIntensity
haptic.global.sharpnessOffset
haptic.recipe.<recipeId>.<parameter>
mapping.<mappingId>.<parameter>
mechanism.<mechanismId>.<parameter>
input.<inputId>.<parameter>
```

## 8. 产品设置与开发者调参应分层

普通用户日常只需要互不覆盖的产品控制：

- 启用触感。
- 其他事件力度/锐度：调节 UI、脱档、吸附等非跨档语义，不覆盖 Detent preset。
- 拖动响应：只控制按住拖动时的速度伺服，并成组派生最大速度、满速手速和加/减速响应。
- 惯性阻力：只控制松手后的 half-life，不与 Haptic Decay 或拖动响应混为一谈。
- `DETENT LAB`：详情页右上角用四个分段按钮选择共享 detent count，并实时覆盖最终 Intensity/Sharpness；活动名称和数值持续显示。
- 棘轮咬合：只在棘轮模式显示，轻/机械/重一次选择映射 breakaway、capture 和 snap response；“自由轮”只能由平滑 Tab 选择。

脉冲节奏与速度调制移动到触觉实验室。它们只修改 Haptic Recipe/Mapping，不允许改变转速、惯性阻力、Shake 阈值或机制模式。

当前 SwiftUI 高级配方编辑器已开放：

- 每个 Recipe 的 event list。
- Transient / Continuous。
- Intensity / Sharpness。
- Attack / Decay / Release / Sustained。
- 五个 Haptic Dynamic Controls；参数曲线仍保留为后续独立能力。
- Pulse 数量、间隔和 layering。
- Mapping 输入范围、曲线指数、dead zone、hysteresis。
- Core Motion 原始值监视器。

不建议用一个全局 waveform 选择器覆盖所有 Recipe。用户把全局类型切成 Continuous 后，Button、Tick、Reset 都会失去自己的机械身份。

## 9. 当前项目已有能力与缺口

### 已有

- Core Haptics capability 检测、场景加载时启动的唯一持久 engine、reset/stopped 自动恢复，以及 UIKit fallback。
- 按语义解析的 Haptic Recipe Library，以及全局力度、频率感、节奏和速度跟随修饰。
- 每个 transient pulse 独立的 intensity/sharpness；Pop、Capture、Reset、Shake 等拥有不同节奏。
- 唯一循环 `CHHapticAdvancedPatternPlayer` 只承担高速旋转纹理；推牌类使用空间边缘提示与有限三层跨档包，不存在 sustained/looping preload player。
- 自由轮指数 half-life 衰减。
- 磁吸档位的 breakaway、capture、snap 和基于实际 unwrapped angle 的 `DetentCrossed`。
- 第五款推牌的六档 68 mm 力模型、可见预压、慢搓边缘限速、空间提示、势垒跨越、预测捕获和跨档同步视觉轻颤。
- 产品构建中禁用了历史自动 motor；启动和 reset 角速度为零。
- 四个正式旋转场景都接入只读真实角速度的低噪、低延迟程序化风声与 12 声部棘轮 click；平滑模式只有风声，棘轮模式为两层叠加。
- 第六款磁吸扇牌接入 5 个厚合金 click 与 8 声部池，只在用户授权的真实 `DetentCrossed` 上逐档播放一次。
- 单指真实旋转角度、Pinch、相机 Orbit。
- Core Motion 60 Hz 的 attitude、rotation rate、gravity 与 userAcceleration。
- `userAcceleration` 的 0.30/0.22g 回差惯性触点、8/s 限流；金属模型原有明确甩动角冲量保持不变。
- SwiftUI `DETENT LAB` 热切换四个预设并显示实时值；日常/高级设置不再重复暴露 Detent 参数。

### 需要重构或新增

1. 经典蓝色模型的 Detent 仍由拖拽累计产生；需要像三叶金属一样迁移到实际转子 unwrapped angle。
2. 高速 Detent 已连接 continuous advanced player；仍需在 iPhone 验收 30/s crossover、engine 恢复与温升。
3. 现有控制器读取 yaw 但没有使用；Device Twist 需要 yaw unwrap 或 quaternion/rotation-rate 累计。
4. 当前 Router 只对高频 Detent 做 rate limit；后续还需加入跨语义优先级、抢占与更完整的 layering policy。
5. Gravity 已输出但尚未连接 Gravity Drive 玩法。
6. `InteractionTuningParameters.md` 仍包含历史调参记录，不能再作为当前 Haptic 架构的唯一事实来源。

## 10. 验收标准

### 自由轮

- 冷启动、复位、手指抬起后的最终静止状态都不会自行产生角速度。
- 同一个初速度在不同帧率下具有近似相同的 half-life。
- 自由轮默认没有明显机械档位。
- 风声随真实角速度增强，并随同一物理 half-life 减速、降频和消散；启动与 Reset 不得留下音尾或自行制造运动。

### 磁吸棘轮

- 低于 breakaway threshold 时不跨档。
- 超过 threshold 后跨档，实际跨过一个 detent 只产生一次 Tick。
- 旋转机制每次 `DetentCrossed` 只产生一个 transient；Intensity/Sharpness 精确等于活动预设，不受全局力度、速度倍率或多层冲击覆盖。推牌类独立使用专用有限三层包，不继承旋转预设。
- 四款旋转模型均由 `RatchetDetentCrossed` 逐档驱动 5 个原子 PCM variant 和 12 声部 `PlayOneShot` 池，并与连续风声叠加；Core Haptics pattern 不再承载任何 `audioCustom`。
- 第六款磁吸扇牌每个用户授权的 `DetentCrossed` 只执行一个金属 `PlayOneShot`；自动演示、Reset、程序设姿、Breakaway 和 Capture 均不得制造 click。
- 高于 `30 detents/s` 时停止逐档 transient 并进入单个 continuous loop；回落后离散节奏随惯性自然变疏。
- 低速进入 capture 后吸到最近档位并发出一次 Capture Snap。
- Capture 完成后角速度为零，不发生小幅来回振荡或继续旋转。
- 线性推牌在 30/60/120 Hz 下必须落入同一档，停止位置误差不超过 0.2 mm，且最后速度严格为零。
- 推牌从默认第 3 档首次触摸即可向左或向右脱档；六档可在 iPhone 盲辨，慢推、快速全程推和连续 20 次往返均不得漏档。每次真实跨档必须只有规定的 `0 ms` 主冲击/30 ms 重量段与 `22 ms` 收尾所组成的单个有限包，停手不得持续输出，视觉轻颤与主冲击同帧。

### Device Twist

- 穿越 `-180° / +180°` 时累计角度连续。
- 手机完整旋转 360° 后 detent 数量与配置一致。
- 快速旋转受 rate limit 控制，但最终 detent index 正确。

### 设备惯性

- `<0.30g` 不触发；回落到 `≤0.22g` 后解除 active。
- 输出为 `0.25...0.40 / 0.20...0.35` 的沉、软 isolated transient，每秒不超过 8 次。
- 惯性通道与 Detent、高速 continuous 同时混合，不调用 stop，不抢占任何棘轮事件。

### Haptic

- 必须在支持 Taptic Engine 的 iPhone 真机验收；Simulator 不能判断触感。
- Button、Pop、Detent、Snap、Shake 和 Reset 在盲测时应能被区分。
- 高频 Detent 不得出现明显排队、延迟或持续麻木感。
- 关闭 Haptic 后所有玩法仍可通过视觉和声音理解。

## 11. 参考资料

### 11.1 Fidgetable 公开资料

- [Fidgetable — App Store](https://apps.apple.com/us/app/fidgetable-haptic-fidget-toy/id6503308266)
- [Fidgetable 官方网站](https://www.fidgetable.app/)
- [Fidgetable Changelog](https://www.fidgetable.app/changelog)

### 11.2 Apple 官方资料

- [Core Haptics](https://developer.apple.com/documentation/corehaptics)
- [Preparing your app to play haptics](https://developer.apple.com/documentation/corehaptics/preparing-your-app-to-play-haptics)
- [Updating continuous and transient parameters in real time](https://developer.apple.com/documentation/corehaptics/updating-continuous-and-transient-haptic-parameters-in-real-time)
- [Playing collision-based haptic patterns](https://developer.apple.com/documentation/corehaptics/playing-collision-based-haptic-patterns)
- [Playing a custom haptic pattern from a file](https://developer.apple.com/documentation/corehaptics/playing-a-custom-haptic-pattern-from-a-file)
- [Playing haptics — Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/playing-haptics)
- [CMMotionManager](https://developer.apple.com/documentation/coremotion/cmmotionmanager)
