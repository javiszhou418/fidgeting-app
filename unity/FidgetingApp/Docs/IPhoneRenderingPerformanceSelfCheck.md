# iPhone Unity 渲染、内存与热稳定性自查标准

最后更新：2026-08-03

适用范围：`unity/FidgetingApp` 中所有可交互 3D 陀螺，尤其是
`Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity`。

本文件同时承担三个职责：

1. 解释 Apple 和 Unity 实际允许我们测量什么。
2. 给 Fidgeting App 定义比“看起来不卡”更严格的内部发布门槛。
3. 规定每次模型重建、替换、删减或材质/光效修改后必须重复的检查。

这是一份工程自查标准，不是对所有 iPhone 的温度或内存安全保证。自动化检查通过后，
仍必须在支持范围内的真实 iPhone 上完成耐久测试，才能把对应状态标为真机通过。

## 1. 不能使用一个虚假的“安全百分比”

Apple 没有公开“GPU 低于某个利用率就不会发热”或“内存低于物理 RAM 的某个百分比就
不会被终止”的统一阈值，原因包括：

- GPU occupancy 表示并发执行资源的占用效率，不等于耗电或温度；较高 occupancy 也可能
  是高效执行，温升需要结合 GPU Time、功耗和 thermal state 判断。
- iOS 对进程的内存上限随设备和运行时环境变化，并不等于设备物理 RAM；超过当时上限时
  系统会终止进程，形成 Jetsam，用户看到的效果与闪退相同。
- 设备温度同时受 GPU、CPU、显示亮度、充电状态、环境温度、保护壳和后台任务影响。

因此本项目把“占用比例”仅作为早期规划信号，把以下内容作为发布依据：

- CPU/GPU 每帧实际耗时及分位数。
- Metal HUD 的 Frame Interval、GPU Time、进程/Metal 内存和 Thermal State。
- Instruments Game Performance、Metal System Trace、Allocations 和 Power Profiler。
- Unity Profiler 与 Memory Profiler 在目标 iPhone Player 上的采样。
- 30 分钟持续运行前后是否出现降频、掉帧、内存增长或热状态恶化。

## 2. 本项目的内部发布门槛

以下数值是 Fidgeting App 的保守工程预算，不是 Apple 公布的硬件上限。它们为 Unity、
SwiftUI 外壳、Core Motion、音频和 Core Haptics 保留共同余量。

### 2.1 60 FPS 帧预算

Apple 给 60 FPS 的完整帧时间是 16.67 ms。Fidgeting App 的稳定运行目标如下：

| 指标 | 绿色 | 黄色，需要优化 | 红色，禁止发布 |
| --- | ---: | ---: | ---: |
| GPU Time 平均值 | `<= 8.0 ms`（约 48% 帧预算） | `8.0...10.5 ms` | `> 10.5 ms` |
| GPU Time P95 | `<= 10.5 ms`（约 63%） | `10.5...13.0 ms` | `> 13.0 ms` |
| GPU Time P99 | `<= 13.5 ms`（约 81%） | `13.5...16.67 ms` | `> 16.67 ms` |
| CPU Main Thread P95 | `<= 8.0 ms` | `8.0...12.0 ms` | `> 12.0 ms` |
| CPU Main Thread P99 | `<= 10.0 ms` | `10.0...16.67 ms` | `> 16.67 ms` |
| 稳态漏帧率 | `< 0.1%` | `0.1...0.5%` | `> 0.5%` |
| 连续两帧超过 33.33 ms | `0 次` | 不适用 | 任意一次 |
| 稳态 GC Alloc | `0 B/frame` | 偶发且可解释 | 持续分配 |

说明：这里的 48%、63%、81% 是“GPU Time / 16.67 ms”，不是 GPU occupancy 或芯片总利用率。
场景首次加载单独记录，不能用加载峰值污染稳态统计，也不能用稳态平均值掩盖切换卡顿。

### 2.2 热稳定与功耗

标准测试环境：

- 真机、Release/非 Development 构建做最终结论；Development 构建只用于定位。
- 电池供电，不连接充电器；屏幕亮度 50%；环境温度记录在报告中。
- 开始前设备 thermal state 为 `nominal`，先静置至机身恢复常温。
- 使用真实产品 UI、音频、Haptic、Core Motion 和当前模型，不使用空场景代替。
- 连续测试 30 分钟：10 分钟自由轮、10 分钟高速棘轮、5 分钟模型切换与拆解、5 分钟混合操作。

硬门槛：

- `serious` 或 `critical` thermal state：必须为 0 次。
- `fair` 持续超过 2 分钟：触发优化或降级调查，不能直接忽略。
- 最后 5 分钟的 GPU P95、CPU P95 或平均 FPS 相对前 5 分钟恶化超过 10%：失败。
- 用户可察觉的亮度突降、持续帧率档位下降、音频断裂或 Haptic 生命周期错误：失败。
- Xcode Energy/Power 报告出现高能耗诊断：失败，必须定位来源。

若未来加入运行时热降级，只允许降低光效、Render Scale、反射质量或目标帧率，不能改变
机械状态机、档位数、输入语义或 Haptic 语义身份。

### 2.3 内存和闪退防线

内存本身通常不是主要发热源；它首先影响内存压力、切换延迟和 Jetsam 风险。内部标准为：

| 指标 | 绿色 | 黄色 | 红色 |
| --- | ---: | ---: | ---: |
| App `phys_footprint` 峰值 | `<= min(350 MB, 物理 RAM 的 20%)` | `20...25%` 或 `350...450 MB` | `> 25%` 或 `> 450 MB` |
| `os_proc_available_memory` 相对进程可用总量的余量 | `>= 30%` | `20...30%` | `< 20%` |
| 单个三叶模型加载后的增量 | `<= 32 MB` | `32...48 MB` | `> 48 MB` |
| 场景切换瞬时增量 | `<= 64 MB` | `64...96 MB` | `> 96 MB` |
| 50 次模型切换后的净增长 | `<= 5%` 且 `<= 20 MB` | 可解释的一次性缓存 | 持续单调增长 |

`os_proc_available_memory` 只作为当次采样的建议值，不能缓存，也不能为了“用满可用内存”
而扩大资产。出现以下任意情况直接失败：

- Memory Warning、Jetsam、`EXC_RESOURCE / MEMORY`。
- 背景恢复后模型、Shader或音频重复常驻。
- 卸载场景后模型资源无法回落至切换前基线的 10% 以内。
- 连续交互过程中存在可重复的托管堆增长或每帧分配。

### 2.4 三叶模型内容预算

| 项目 | 组装状态 | 拆解状态/上限 |
| --- | ---: | ---: |
| 可见三角面 | `<= 45,000` | `<= 60,000` |
| 单 Mesh 顶点 | `< 65,535`，优先 16-bit index | 同左 |
| Draw Calls | `<= 15` | `<= 20` |
| 独立材质 | `<= 6` | `<= 6` |
| 实时灯 | 1 个主光；其余优先烘入 Cubemap | 最多 2 个无附加阴影灯 |
| 实时反射探针 | 0 | 0 |
| Reflection Cubemap | 1 个，256 边长 | 同左 |
| 模型纹理常驻增量 | `<= 8 MB` | `<= 10 MB` |
| 透明全屏 Pass | 0 | 0 |

默认移动端渲染基线继续使用：

- 60 FPS、0.90 Render Scale、2x MSAA。
- Linear Color Space。
- HDR关闭、全屏Bloom关闭、Camera Post Processing关闭。
- LDR纹理使用iOS ASTC；主要Normal/RMA 1024或2048，共享微细节512。
- 静态Studio Cubemap代替实时Reflection Probe。
- 光晕通过局部Glint/加法小网格实现，透明覆盖面积尽量小于屏幕的15%。

真Bloom只有在所有基线设备的30分钟真机记录证明GPU和热余量充足后才能进入高画质档；
启用时必须同时修改Mobile RPAsset、相机、测试、性能报告和`IMPLEMENTATION_STATUS.md`。

## 3. 每次模型迭代必须执行的检查

这里的“迭代”包括重建、替换、删减、合并网格、改贴图、改Shader、改灯光、改光晕、改
拆解层级和修改碰撞体。不能因为只是艺术修改而跳过。

### A. 变更前基线

- 保存同一相机、同一分辨率、同一灯光下的组装与拆解图。
- 记录当前三角面、顶点、Renderer、材质、纹理和Draw Call数量。
- 保存最近一次真机测试的设备型号、iOS版本、构建号和测量日期。

### B. 静态自动检查

- 在 Unity 菜单运行 `Fidgeting/Three-Blade/Log Static iPhone Audit`，或批处理调用
  `ThreeBladeEDC.EditorTools.ThreeBladeStaticAuditReporter.LogStaticAudit`；把日志中的
  `THREE_BLADE_STATIC_AUDIT` JSON 复制进当轮报告。
- 所有可见Mesh具有有效UV、Normal、Tangent和非退化三角形。
- 视觉Mesh与碰撞Mesh分离；复杂齿形和切面不得进入凸碰撞体。
- 旋转Pivot、质心和轴承轴线重合。
- 模型总预算满足2.4；没有运行时生成或复制材质。
- HDR、Render Scale、MSAA和后处理设置与本文件一致。
- 所有推荐调参只存在一个运行时权威值；改值时同步序列化场景和测试。

### C. 机械回归

- 启动、复位、拆解归位后角速度为零。
- 自由轮只接收显式输入并按half-life衰减。
- 磁性档位在breakaway前保持，低速捕获后结束于零角速度。
- Glint/Bloom控制器只读取机制状态或语义事件，不施加力或修改档位。
- 没有新增raw-input到`IosHaptics`的调用。

### D. 参考图差距检查

必须使用固定Top、Side、45° Hero和微距侧面机位，与参考图半透明叠加检查：

- 总宽、中心盖直径、主体厚度和三翼120°关系。
- 翼尖轮廓、内凹三角槽、主架与中心圈的连接方式。
- 中心盖齿形/切面、上下垫片、轴承内外圈及装配间隙。
- 喷砂主体、径向拉丝盖、抛光倒角和黑色聚合物的粗糙度差异。
- 暖色反射是否来自环境光，而不是被画入Base Color。
- 旋转时高光是否连续、无法线跳变、无摩尔纹和亚像素闪烁。

每轮必须列出“已弥合、仍存在、因缺少实测数据无法确认”三类差距，不能只给主观结论。

### E. 真机性能检查

- 先运行Unity `BuildIosPerformanceProject`导出非Development工程；随后用Xcode Release配置
  完成一次arm64无签名编译，证明IL2CPP、Swift、Objective-C++、Shader和链接均可交付。
- 连接、解锁并信任iPhone，确认`devicectl`显示`tunnelState=connected`且
  `ddiServicesAvailable=true`；否则不得把“已配对”误写成“已完成真机验收”。
- 可使用仓库脚本`scripts/ios_build_and_install.sh --install-existing`签名、安装和启动最新导出。
- 手机锁定时可用`--no-launch`仅做恢复性覆盖安装；它不构成“已启动”或任何真机性能证据。
- 安装脚本必须调用`devicectl device info details`进行实时DDI握手；缓存的`list devices`
  `disconnected`状态不能单独作为设备不可用的结论。
- 用Development Player连接Unity Profiler，在目标iPhone采CPU、GPU、Rendering、Memory和GC；
  `GC Allocated In Frame`必须以这份记录判定，不能从Release中的缺失计数推断为零。
- Metal HUD记录FPS、Frame Interval、GPU Time、进程内存、Metal内存和Thermal State。
- Instruments Game Performance/Metal System Trace定位最差的5至10秒片段。
- Allocations/Memory Graph检查50次模型切换与前后台循环。
- Power Profiler或Energy报告检查30分钟持续运行。
- Release构建重复最终30分钟门槛；Development构建数据不能替代它。

### F. 可重复的30分钟机器可读遥测

最新版Release包含默认关闭的`IPhonePerformanceAudit`。它只能由启动参数
`--fidgeting-performance-audit`或环境变量`FIDGETING_PERFORMANCE_AUDIT=1`启用；普通用户
启动时不创建采样对象。采样器只读`FrameTimingManager`与系统资源，不引用Rotor、不写
角速度、不合成触摸，也不调用Haptic。

每轮模型修改后的完整执行顺序：

```zsh
./scripts/ios_build_and_install.sh --development
./scripts/ios_performance_soak.sh --development-gc
./scripts/ios_build_and_install.sh
FIDGET_AUDIT_ENVIRONMENT_C=24 \
FIDGET_AUDIT_BRIGHTNESS_PERCENT=50 \
FIDGET_AUDIT_POWER_STATE=unplugged \
  ./scripts/ios_performance_soak.sh
```

前两条安装带Profiler counter的Development Player，并完成5分钟GC检查。测试者须在这5分钟
内覆盖自由轮、高速棘轮、模型切换、拆解/复原和混合操作；只有汇总同时满足
`mode="developmentGc"`、`developmentBuild=true`、`gcCounterAvailable=true`、
`gcPassed=true`和`passed=true`才通过。Development模式只判定持续时间、正确构建类型和稳态
GC，不拿它的CPU/GPU数据代替Release性能结论。

第三条会用同一Bundle ID重新覆盖安装非Development Release；第四条主动建立CoreDevice/DDI
连接、以前台Release重新启动唯一Bundle，并把控制台
证据写入`Artifacts/Performance/<timestamp>-iphone-soak/device-console.log`。审计期间临时
禁用自动锁屏，完成、进入后台或退出时恢复原设置。仍须由测试人员按真实产品方式操作：

- 预热10秒，不计入稳态统计。
- 10分钟自由轮。
- 10分钟高速棘轮。
- 5分钟模型切换与拆解。
- 5分钟混合操作。

Release命令强制要求声明环境温度、屏幕亮度和供电状态；亮度只接受45%至55%，供电只接受
`unplugged`。环境温度只能由测试人员声明；诊断运行会另外读取iOS实际电池状态、电量和
`UIScreen.brightness`交叉验证后两项。任何采样为充电/满电接电状态，或实际亮度离开45%至
55%，都会令Release `environmentPassed=false`与总`passed=false`。
成功后脚本同时生成原始`device-console.log`、可解析的`summary.json`和预填充`REPORT.md`；
Metal HUD、Power Profiler、亮度突降、音频/Haptic与Jetsam观察仍须人工补齐。

每帧记录CPU Main、GPU和Frame Interval；每5秒读取`TASK_VM_INFO.phys_footprint`、
`os_proc_available_memory()`、物理RAM、Unity allocated memory和
`ProcessInfo.thermalState`，同时记录电池状态/电量与屏幕实际亮度。电池状态数字映射为
0 Unknown、1 Unplugged、2 Charging、3 Full；诊断仅在显式审计期间临时启用battery monitoring，
退出、进入后台或完成时恢复此前设置。每分钟输出`FIDGET_PERF_PROGRESS`，结束输出单行
`FIDGET_PERF_SUMMARY`，包含门槛布尔值、P95/P99、漏帧、首末5分钟衰减、内存余量、
thermal持续时间、GC Alloc/frame平均/峰值/非零帧比例和GC collection计数。thermal数字映射为0 Nominal、1 Fair、2 Serious、
3 Critical。

Unity官方的Profiler counter表明确标注：`GC Allocated In Frame`在Release（非Development）
Player中不可用。因此Release汇总遇到该情况会输出`gcCounterAvailable=false`、
`externalGcCheckRequired=true`和`gcAllocatedNonzeroPercent=-1`；`-1`表示未测量，绝不表示
`0 B/frame`。Release的`passed`只评价它能可靠测量的时序、帧、内存、thermal和首末稳定性；
如果Development构建中计数器可用，任何非零稳态分配仍会让`passed=false`。

Release脚本只有在`mode="release"`、`developmentBuild=false`、`reason="completed"`且
`passed=true`时成功；进入后台、提前终止、用错包、门槛
失败、缺失Frame Timing或采样覆盖不足都会失败。但这仍不是完整发布结论：每轮模型修改还
必须同时保留前述Development GC日志；需要定位分配来源时再连接Unity Profiler并开启
GC.Alloc call stacks。两份机器日志合并后才证明稳态`GC Alloc=0 B/frame`与Release热/帧门槛。
诊断模式预分配约2.5 MiB帧样本数组，该开销保留在`phys_footprint`
结果中，不从门槛中扣除。汇总不能替代Metal HUD的Metal allocated，也不能替代Power
Profiler/Energy报告与人工观察到的亮度、音频和Haptic异常。

## 4. 当前三叶模型相对目标的首次审计与首轮构建结果

审计日期：2026-08-02。证据来自当前代码、序列化场景、生成资产、四视图、静态审计器和
完整 EditMode 测试和真实iPhone 60秒遥测冒烟；尚无本轮30分钟Power/Metal记录。

| 项目 | 当前状态 | 与目标差距 | 本轮处理方向 |
| --- | --- | --- | --- |
| 物理层级 | 通过 | `HubStatic/RotorDynamic`、轴承内外圈关系已建立 | 保留，不重写 |
| 零自转规则 | 通过自动化 | 仍需随真机休眠/恢复继续回归 | `MetalGlintController`只读实际速度与语义事件，Reset归零 |
| 三角面预算 | 通过静态审计 | 组装 `9,666` tris、`17,044` vertices、15 estimated draws | 保持组装45K/15 draw门槛 |
| 主架轮廓 | 首轮已弥合 | 已改为120°尖锐七边三角翼、四段倒角、小型暗腔和抛光槽边；贴图截图不能提供真实圆角半径 | 等实物尺寸或CAD后校准外轮廓/圆角 |
| 中心盖 | 首轮已弥合 | 24齿×6采样、径向扇区、高光倒角完成；真实齿深未知 | 当前齿深0.12 mm为视觉推定，待实测 |
| 轴承拆解 | 首轮已弥合 | 8颗球已合并为单一Ball Cage renderer；真实轴承型号/游隙未知 | 保持连接层级，拿到实测后改内外径 |
| 主体材质 | 首轮已弥合 | 喷砂主体、暗腔、抛光倒角、黑色聚合物已分层；尚未做实物色卡匹配 | 真机/实物并排校准粗糙度与曝光 |
| 径向拉丝 | 已实现 | 轻量专用Cap Shader、Base/Normal径向纹理完成；不是Apple定义的硬件各向异性材料 | 真机观察旋转时摩尔纹与闪烁 |
| 反射 | 已实现静态方案 | 256 LDR Studio Cubemap、无实时Reflection Probe | 真机确认宽条高光连续性 |
| 光晕 | 已实现并有测试 | 局部MaterialPropertyBlock Glint，无HDR/Bloom；视觉强度仍需真机校准 | 保留全屏Bloom关闭 |
| 纹理占用 | 通过静态预算 | 5个生成纹理运行时估算 `3,500,360 bytes`（约3.34 MiB） | iOS Player中确认ASTC与实际Metal allocated |
| 真机热稳定 | 链路冒烟通过，结论待定 | 60秒/3,601帧、phys峰值323.3 MiB、thermal保持Nominal；未覆盖完整交互与首末衰减 | 最终必须完成30分钟记录与Power/Metal检查 |

首轮自动化结果更新为：Unity EditMode `85/85` 通过；可见Renderer `12`、独立材质 `6`、凸
MeshCollider `4/4`。固定Hero、Top、Side、Exploded四图已生成到仓库根目录`Artifacts/`。

结论：正式视觉构建已经开始并完成首轮可运行接线，轮廓、中心盖、连接环、轴承、材质和
局部反光已进入产品场景，不再只是文档或Mockup。但两张参考图不能给出真实尺寸、背面螺纹、
公差和材料牌号，因此不能称为工业级精准复刻；也不能在没有真实 iPhone 30分钟记录时声称
“不会发热/不会闪退”。全屏HDR/Bloom继续关闭。

## 5. 测试记录模板

每次真机记录复制以下表格到`Artifacts/Performance/<build-id>/REPORT.md`：

```text
构建号：
Git/工作区标识：
设备型号：
iOS版本：
电池健康/电量：
充电状态：
环境温度与亮度：
测试场景与持续时间：

GPU avg / P95 / P99：
CPU Main avg / P95 / P99：
Frame Interval P95 / P99：
漏帧率与最长帧：
App phys_footprint peak：
Metal allocated peak：
os_proc_available_memory最低值：
GC Alloc/frame：
Thermal state变化：
首5分钟与末5分钟差异：
Jetsam / Memory Warning / EXC_RESOURCE：
结论：通过 / 不通过 / 数据不足
未通过项与下一步：
```

## 6. 官方资料依据

- Apple：[Metal帧率最佳实践](https://developer.apple.com/library/archive/documentation/3DDrawing/Conceptual/MTLBestPracticesGuide/FrameRate.html)——60 FPS完整帧预算为16.67 ms，无法稳定完成时应减少工作量或选择稳定的较低档位。
- Apple：[分析Metal App性能](https://developer.apple.com/documentation/xcode/analyzing-the-performance-of-your-metal-app/)——使用Game Performance和Metal System Trace结合帧、GPU活动与热状态定位问题。
- Apple：[Metal Performance HUD指标](https://developer.apple.com/documentation/xcode/understanding-metal-performance-hud-metrics)及[监控Metal图形性能](https://developer.apple.com/documentation/xcode/monitoring-your-metal-apps-graphics-performance/)——可记录FPS、Frame Interval、GPU Time、进程/Metal内存和Thermal State。
- Apple：[降低App内存使用](https://developer.apple.com/documentation/xcode/reducing-your-app-s-memory-use)及[Jetsam报告](https://developer.apple.com/documentation/xcode/identifying-high-memory-use-with-jetsam-event-reports)——进程内存上限依设备和环境变化，超限会被系统终止。
- Apple：[`os_proc_available_memory`](https://developer.apple.com/documentation/os/os_proc_available_memory)——返回当前进程距离当时内存上限的建议余量，不能缓存或用于把内存用满。
- Apple：[分析电池使用](https://developer.apple.com/documentation/xcode/analyzing-your-app-s-battery-use)——结合Xcode、MetricKit和Instruments观察GPU Time、热状态和功耗。
- Apple：[`ProcessInfo.thermalState`](https://developer.apple.com/documentation/foundation/processinfo/thermalstate-swift.property)——热状态升高时应用应降低系统资源使用。
- Unity：[在目标平台分析应用](https://docs.unity3d.com/2022.2/Documentation/Manual/profiler-profiling-applications.html)——Editor数据只适合迭代，最终时序必须来自目标设备Player。
- Unity：[Profiler Highlights](https://docs.unity3d.com/2023.2/Documentation/Manual/ProfilerHighlights.html)——CPU和GPU分别需要保持在目标帧时间以下。
- Unity：[Profiler counter参考](https://docs.unity3d.com/6000.0/Documentation/Manual/profiler-counters-reference.html)——逐项列出Release Player可用性；`GC Allocated In Frame`在非Development Player中不可用。
- Unity：[iOS/tvOS纹理格式](https://docs.unity3d.com/6000.0/Documentation/Manual/texture-choose-format-by-platform.html)——A8及以上Apple设备推荐ASTC。
- Unity：[Memory Profiler概览](https://docs.unity3d.com/6000.0/Documentation/Manual/profiler-memory-introduction.html)——使用目标Player的内存计数和快照定位分配、泄漏与碎片。
