# Fidgeting 产品手感准则

## 目标

通过可信金属视觉、输入预压、脱档、跨档、吸附和质量沉降的同步反馈，让移动端无限接近实体高级指尖玩具令人反复把玩的手感。

屏幕不能向手指施加真实反向力，因此“阻力”必须由三条同步通道共同建立：视觉上的弹性滞后、机械状态中的势垒与快速吸附、Taptic Engine 的预压与触点。任何单独的震动或补间动画都不能称为机械手感。

## 不可破坏的链路

```text
输入 → 机械状态 → 语义事件 → Haptic Recipe → iOS Renderer
```

- Touch、Mouse、Core Motion 只提供输入，不得直接调用 `IosHaptics`。
- 机械模型是位置、速度、档位、脱档、捕获和停止状态的唯一权威。
- `Breakaway`、`DetentCrossed`、`DetentCaptured` 等事件只在相应物理状态真实发生时发出。
- 可见磁体、物理档位和 Haptic 档位必须读取同一个 Profile，禁止维护三份相似数组。
- Library、AUTO、场景构建、Reset 和程序化设姿可以复用视觉物理，但不得伪造用户触感。

## 磁吸推牌基线

第五款 `magnetic-slide-tile` 的唯一配置是 `LinearMagneticDetentProfile`：

| 项目 | 重磁默认值 |
| --- | ---: |
| 稳定档位 | 6；默认第 3 档，左右均有真实磁力井 |
| 磁体中心距 | 13.6 mm |
| 有效行程 | 68 mm |
| 默认双向范围 | 左 27.2 mm / 右 40.8 mm |
| 移动质量 | 55 g |
| 手指耦合 / 阻尼 | 125 N/m / 4.1 Ns/m |
| 脱档力 / 磁力峰值 | 0.62 N / 0.58 N |
| 轨道摩擦 / 阻尼 | 0.085 N / 0.30 Ns/m |
| 捕获弹簧 / 阻尼 | 220 N/m / 3.8 Ns/m |
| 最大可见预压 | 1.4 mm |
| 捕获半径 | 5.8 mm |
| 精确锁定 | 误差 < 0.10 mm 且速度 < 0.0045 m/s |

状态顺序固定为：

```text
Captured → Loading → Breakaway → Traveling → Capturing → Captured
```

相邻档位使用连续磁势阱：

```text
Fmag = -Fpeak × sin(2πq)
```

手指不是滑盖位置，而是弹簧目标：

```text
m·x'' = kh(xfinger-x) - ch·x' + Fmag(x) - crail·x' - Ffriction
```

最大积分子步为 `1/240 s`，每帧最多 8 个子步。捕获完成必须把速度严格清零；边界不能回弹自振；Reset 必须静默、归零并回到第 3 个真实磁力井，而不是单向端点。

## 三层磁吸扇牌基线

第六款 `magnetic-fan-card` 使用独立 `FanCardDetentProfile`，不得继承或改写第五款线性推牌、四款旋转机构及设置面板中的调节状态：

| 项目 | 固定值 |
| --- | ---: |
| 全局稳定档位 | `q = 0 / 1⁄3 / 2⁄3 / 1` |
| 中片 / 顶片角度 | `45°q / 90°q` |
| 相邻层 / 最外层最大夹角 | `45° / 90°` |
| 归一化脱档负载 | `0.067` |
| 手指弹簧 / 阻尼 | `52 / 8.7` |
| 磁峰 / 轨道摩擦 | `7.8 / 0.72` |
| 捕获弹簧 / 阻尼 | `92 / 13.6` |
| 脱档冲量 / 松手预测 | `0.72 / 0.055 s` |
| 可见预压倍率 | `0.28` |
| 最大积分子步 / 帧步 | `1/240 s / 1/20 s` |

底片和中片各提供一条以共同轴心为圆心、向左下内缩的 45° 圆弧轨道及 3 枚磁体；中片和顶片各提供一枚随动轴承球。机械坐标只有一个 `q`，模型角度、档位语义和 Haptic 都从该坐标与同一 Profile 读取。只有明确用户拖动可以授权 `Breakaway`、`DetentCrossed`、`DetentCaptured`；Reset、Library、AUTO 和程序化 `SetFanProgress()` 必须静默。

本款的材质语言与机械配置严格解耦。枪黑珠喷框、暖银金属面、铬轴承、金色编织轨道、Oxanium `A`、向下极简黑桃、细线与三点蚀刻均为无碰撞展示层；更换颜色、粗糙度、法线或正面图案不得改变四档、45°/90°、阻尼、交互热区或 Haptic 配方。

## 视觉与触觉同步

- Loading：滑盖保持在档位，显示最多 1.4 mm 的预压滞后；负载达到 5% 后启动低锐度磁力 continuous。
- Breakaway：只发一次 `0.78 / 0.94` 冲击，停止预压 continuous，并释放视觉储能。
- DetentCrossed：每跨一个真实势垒发一次 Core Haptics 事件参数上限 `1.00 / 1.00` 的 isolated transient；不补尾脉冲、不做冲击叠层，六档事件不得套用旋转高速限流。这里的第二项是 sharpness（触感锐度），不是开发者可指定的马达 Hz。
- DetentCaptured：强主脉冲加 36 ms 弱尾脉冲；视觉最多 0.45 mm 过冲，并有 0.18 mm / 0.30° 的短促沉降。
- 视觉沉降 half-life 为 45 ms，120 ms 内强制回零；微回震只作用于 Renderer 子层，不移动 Collider。
- 磁力预压使用独立 `CHHapticAdvancedPatternPlayer`，保持既有轻压→继续加力→脱档节奏，但把整条线性曲线抬高为 Intensity `0.45→1.00`、Sharpness `0.30→1.00`，最多 30 次/秒更新；它不能抢占旋转高速纹理 player。30 次/秒只是参数更新上限，不是 Taptic Engine 的振动频率。跨档触点直接走经过验证的 isolated transient 路径，不再维护另一套多脉冲 Pattern。

## 生命周期与验收

- Haptic 关闭、手指释放、进入 Library/AUTO、Reset、App 后台、切场景和对象禁用时，磁力预压 player 必须立即停止或按 Profile 淡出。
- Core Haptics engine reset/stopped 后，只恢复仍被请求且 App 处于 active 的 player。
- 自动测试负责确定性、事件计数、单一配置来源、生命周期连接和无原始 Haptic 调用。
- 触感强弱、六档盲辨、视觉与触觉是否同帧，以及连续 20 次往返是否漏击/双击，只能在支持 Core Haptics 的 iPhone 上最终验收。
- 机械点击音频只消费同一条经过输入授权的 `DetentCrossed` 语义事件；不得另建时间轴，也不得从触摸回调直接发声。

## 后续机构复用

`MagneticDetentTrack1D` 接受任意单调一维档位。线性机构使用米和质量；旋转适配器可把坐标换成弧度、质量换成转动惯量，但必须保留相同状态机、语义事件和生命周期。本轮不迁移既有四款陀螺。
