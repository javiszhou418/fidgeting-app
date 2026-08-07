# Three-Blade Visual Build Audit — 2026-08-02

范围：`unity/FidgetingApp/Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity`

结论：本轮桌面侧静态预算与完整自动化通过；最新签名Release已安装到真实iPhone，且
60秒遥测冒烟确认动态采样链路可用。由于尚未完成30分钟分阶段交互、Metal HUD和
Power Profiler，本报告仍不能证明“不会发热”“不会Jetsam”或完成工业级精准复刻。

## 本轮输出

- 正式三翼可视网格：120°合并Renderer；每片保留独立凸碰撞体。
- 七边尖翼、四段倒角、浅三角暗腔、复用现有高光Submesh的抛光槽边和近黑中心承力/装饰环。
- 24齿×6周向采样中心帽，独立32段碰撞网格。
- 中心帽专用径向拉丝Shader；256 Studio Cubemap；无实时Reflection Probe。
- 8颗轴承球合并为一个Ball Cage renderer。
- 局部`MetalGlintController`只读真实速度与语义事件；Reset回到零亮度，不改变物理。
- HDR、Bloom、Camera Post Processing和透明全屏Pass保持关闭。

## 自动化证据

Unity `6000.5.6f1` EditMode：`85/85 passed`，`0 failed`。

iOS交付链路：

- Unity非Development/Release设备工程重新导出成功，包含当前两套产品场景与最新三叶资源。
- Xcode `Release-iphoneos` arm64无签名编译成功；IL2CPP、Swift、Objective-C++、Core Motion、
  Core Haptics、Metal和UnityFramework均通过编译与链接。
- 产物Bundle ID：`com.jiaweizhou.fidgetspinner.codex`；Minimum iOS：`15.0`。
- 无签名`.app`约176 MiB；这是磁盘构建体积，不等于运行时`phys_footprint`。
- Apple Development签名构建成功，并已通过CoreDevice/DDI安装和启动到iPhone 15 Pro Max。
- `IPhonePerformanceAudit`通过显式诊断环境变量启用；普通启动不创建采样器，也不会驱动Rotor。
- 最终诊断源代码重新导出后，Xcode Release签名构建、安装与启动再次成功；完整EditMode仍为
  `85/85 passed`。

静态审计命令：

```text
ThreeBladeEDC.EditorTools.ThreeBladeStaticAuditReporter.LogStaticAudit
```

实际输出：

```json
{
  "visibleRenderers": 12,
  "visibleVertices": 17044,
  "visibleTriangles": 9666,
  "estimatedDrawCalls": 15,
  "distinctMaterials": 6,
  "meshColliders": 4,
  "convexMeshColliders": 4,
  "generatedTextures": 5,
  "generatedTextureBytes": 3500360
}
```

与内部预算比较：

| 指标 | 实际 | 组装预算 | 结果 |
| --- | ---: | ---: | --- |
| 可见三角面 | 9,666 | <=45,000 | 通过 |
| 估算Draw Call | 15 | <=15 | 通过，已到绿色上限 |
| 独立材质 | 6 | <=6 | 通过，已到绿色上限 |
| 生成纹理运行时估算 | 3.34 MiB | <=8 MiB | 通过 |
| 凸MeshCollider | 4/4 | 复杂视觉网格不得用于碰撞 | 通过 |

Draw Call和材质都已到组装预算上限；后续新增连接件必须复用材质，并优先合并到现有
Renderer，否则先优化再加入。

## 固定视图

- `Artifacts/three-blade-edc-preview.png`：45° Hero。
- `Artifacts/three-blade-edc-top.png`：Top比例与120°阵列。
- `Artifacts/three-blade-edc-side.png`：上下盖、垫片、主体和间隙。
- `Artifacts/three-blade-edc-exploded.png`：轴向连接件和Ball Cage。

## 参考图差距

已弥合：

- 圆厚三叶改为尖锐三角翼阵列，中心盖直径/总宽约0.52。
- 中心盖、喷砂翼面、抛光倒角、暗腔和黑色连接环不再共用同一反射响应。
- 上下盖、垫片、轴承内外圈和钢球具有独立装配层级。
- 径向拉丝与局部暖色反光不再依赖全屏Bloom。

仍存在：

- 参考截图的翼尖与内槽具有更复杂的铸造/切削圆角，本轮为移动端程序网格近似。
- 当前Hero灯光仍比参考摄影棚更硬，个别角度左翼接近过曝；需在真机色域/亮度下校准。
- 中心帽径向扇区是视觉推定，真实拉丝方向、齿深和刀纹尺度未知。

缺少实测数据，无法确认：

- 总宽W、中心直径、主体厚度和所有装配间隙的真实毫米值；参考图中的50/70/85/90 mm是镜头焦段，不是产品尺寸。
- 背面螺纹、紧固方式、轴承型号、材料牌号、喷砂粒径和表面处理。
- iPhone完整30分钟GPU/CPU分位数、available-memory余量、Metal内存、功耗与热稳定性；
  当前只有60秒冒烟的`phys_footprint`与thermal证据。

## 真机验收（已完成链路冒烟，30分钟待执行）

设备型号：iPhone 15 Pro Max（已配对、签名安装和启动成功）

iOS版本：26.6

构建号：1；非Development、IL2CPP、Release

环境温度/屏幕亮度/电池与充电状态：冒烟未记录，正式30分钟测试前必须填写

动态遥测冒烟：60秒、3,601帧；`phys_footprint`峰值323.3 MiB；thermal起始与最大均为
`Nominal(0)`。证据：`Artifacts/Performance/2026-08-02-iphone-audit-smoke-env/`。

冒烟结论：采样链路通过；内存低于350 MiB绿线但只剩26.7 MiB余量，须在完整交互和
模型切换期间重点观察。测试被主动中止，因此没有`reason=completed`汇总，不能计为发布通过。

补充GC链路短测：另一次预热后取得413帧时应用进入后台，汇总明确为
`reason=backgrounded`、`passed=false`；短样本phys峰值320.1 MiB、thermal为Nominal。该次
同时确认Unity官方标注的行为：非Development Release中`GC Allocated In Frame`不可用。
最终审计代码把此状态输出为`externalGcCheckRequired=true`和“未测量”哨兵值`-1`，Release不再
把未知解释为`0 B/frame`；稳态GC必须由目标iPhone Development Player连接Unity Profiler
另行证明。证据：`Artifacts/Performance/2026-08-02-iphone-audit-smoke-gc/`。

仓库现已提供独立的5分钟Development GC模式：`ios_build_and_install.sh --development`
导出到隔离的Development Xcode/DerivedData目录，`ios_performance_soak.sh --development-gc`
会拒绝Release包、不可用计数器或任意稳态分配。该模式尚未执行，因此当前GC栏仍为待填；
完成后必须重新安装Release再跑30分钟，不能把Development时序当成发布性能。

2026-08-03链路复核：Development IL2CPP工程、Xcode Release配置签名构建和覆盖安装成功，
其`Data/boot.config`包含`profiler-enable=1`；设备随后锁屏，SpringBoard以`Locked`拒绝启动，
因此没有GC progress/summary。随后重新导出当前非Development Release，`BUILD SUCCEEDED`并
通过`--no-launch`覆盖安装成功；这个恢复安装不算启动或性能通过。详见
`Artifacts/Performance/2026-08-03-development-gc-pipeline/REPORT.md`。

同日脚本继续补强：CoreDevice `lockState`现在位于Unity/Xcode和计时之前，锁定时立即失败；
Release命令强制声明环境温度、45%至55%亮度和`unplugged`供电。机器门槛通过后自动保存
`summary.json`并生成`REPORT.md`，但不会把仍待填写的Metal HUD、Power Profiler、Jetsam、
音频或Haptic观察伪装成已通过。

最终环境门槛不只信任声明：原生诊断会在显式审计期间读取电池状态/电量和
`UIScreen.brightness`，任意采样为非Unplugged或实际亮度超出45%至55%都会失败；退出时恢复
此前battery monitoring设置。该字段尚待解锁后的当前Release真机运行验证。

30分钟GPU avg/P95/P99：待填

CPU Main P95/P99：待填

App phys_footprint peak：待填

Metal allocated peak：待填

`os_proc_available_memory`最低余量：待填

Thermal state时间线：待填

首5分钟与末5分钟差异：待填

Jetsam / Memory Warning / EXC_RESOURCE：待填

Development Player稳态GC Alloc：待填（要求`0 B/frame`）

最终结论：`数据不足（真实iPhone链路已通，等待30分钟分阶段交互与Power/Metal记录）`
