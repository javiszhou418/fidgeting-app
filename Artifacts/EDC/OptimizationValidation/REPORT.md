# Meshy EDC iPhone 保真与面数下限验证

验证日期：2026-08-05  
源模型：`1,994,857 tris / 1,346,692 vertices`  
验证范围：非破坏性的减面候选、固定 Unity Metal 画面对比、静态内存预算推算，以及真机可用性检查。

## 结论

| 结论 | 档位 | 判定 |
| --- | ---: | --- |
| 正式推荐档 | **750,000 tris** | 与 100 万面档相比，四机位平均 SSIM 为 `0.9457`；Top/Hero 轮廓、六孔、X 框架和开盖结构基本保持。相比源模型减少 `62.4%` 三角面。正式烘焙必须基于新拓扑重算法线和 tangent，并修复少量退化/非流形边。 |
| 视觉保真下限 | **500,000 tris** | 正常 Top/Hero 视角仍可接受，估算原始 GPU mesh buffer 约 `24.55 MiB`；但 Side/Open 微距已出现可辨识的薄壁高光离散和轻微边缘波浪。它是“最低可接受”，不是最高保真首选。 |
| 首个不可接受档 | **350,000 tris** | 薄壁与底壳边缘出现连续锯齿/波浪，Open 视角的底座和导轨附近更明显；继续降至 250k/180k 只会扩大该问题。 |

因此，从纯视觉看，**750k tris** 仍是高保真正式候选，**500k tris** 是视觉底线；但 iPhone
短测表明两档都没有同时通过项目的 GPU 与内存门槛。当前不能把任一档写成“iPhone 可接受的最低
面数”。质量优先的 **416,273 tris** 位于 500k 视觉底线和 350k 首个视觉不合格档之间，是唯一
合理的性能/保真交点候选，需补测后才能最终回答。

## iPhone 15 Pro Max 短时 A/B

测试条件：Release 隔离包；每档 `10 s` 预热 + `60 s` 连续滑盖采样；目标 60 FPS；同一设备、
同一场景/材质/灯光。此短测用于筛选面数交点，不替代 Development GC 审计或 30 分钟 Release
验收。

| 档位 | CPU Main P95 / P99 | GPU median / avg / P95 / P99 | 漏帧 | phys peak | thermal | 短测判定 |
| ---: | ---: | ---: | ---: | ---: | --- | --- |
| 750,000 | 2.070 / 2.209 ms | 11.246 / 10.706 / 12.015 / 12.115 ms | 0.0000% | 371.3 MiB | Nominal | **失败：GPU、内存** |
| 500,000 | 1.818 / 2.028 ms | 9.335 / 9.078 / 10.169 / 10.301 ms | 0.0000% | 354.3 MiB | Nominal | **失败：GPU 平均、内存** |

- 两档均采满 `3,600` 个 timing frame，coverage 通过，连续长帧对均为 0。
- 750k 超过 GPU average `<=8.0 ms`、GPU P95 `<=10.5 ms` 和 `phys_footprint <=350 MiB`。
- 500k 的 GPU P95/P99、CPU、漏帧与 thermal 均通过，但 GPU average 为 `9.078 ms`，且
  `phys_footprint` 超门槛 `4.3 MiB`，所以不能把“接近”写成通过。
- 两档可用内存 headroom 均约 89%，thermal 全程 Nominal；当前失败不是 CPU、热状态或系统
  剩余内存造成。
- `Triangles Count` recorder 有效；`Draw Calls Count` 与 `Gfx Used Memory` recorder 在此
  Release 构建不可用，因此 draw call 与 Metal/Gfx memory 不作实测结论。

## 真机构建与限制

- 检测到设备：iPhone 15 Pro Max，iOS 26.6。
- 先前成功检查时 CoreDevice 为 `tunnelState=connected`、`ddiServicesAvailable=true`，设备也已解锁。
- 已生成隔离的 Release A/B 包，主包为 `com.jiaweizhou.fidgetspinner.codex`、`0.1.1 (1)`，
  `UnityFramework` 为 `com.unity3d.framework`；`codesign --verify --deep --strict` 通过，签名团队为
  `2RJ2CW6NK5`。已验证的正式恢复包仍为 `0.1.0 (1)`。
- 安装前 CoreDeviceService 连续两次发生 XPC 初始化超时；用户重新连接 iPhone 后又连续两次得到
  相同错误。遵守“不卸载、两次失败即停止”的安全边界，测试包没有安装，正式 `0.1.0 (1)`
  没有被覆盖或卸载。
- CoreDeviceService 在预检期间间歇性发生 XPC 初始化超时；主设备会话恢复后成功覆盖安装并完成
  750k/500k A/B。该错误及失败 JSON 仍保留，不能误写成设备本身性能失败。
- 本报告中的视觉结论来自 Unity 6000.5.6f1、Metal、Apple M4 Max 的固定画面；内存数字是静态
  buffer 估算，不能写成“iPhone 性能通过”。

准确的 CoreDevice 错误为：

```text
Failed to load provisioning paramter list due to error:
XPCError(errorCode: 1001, ... "NSLocalizedDescription": "The connection was invalidated.")
ERROR: Timed out waiting for CoreDeviceService to fully initialize.
(com.apple.coredevice.devicectl error 1 (0x01))
```

下一步先补测 416,273 tris 质量优先交点；任何最终候选仍需完成规定的 Development GC 与
30 分钟 Release 审计。

## 方法

### 主对比梯度

- 算法：`fast-simplification 0.1.9` QEM。
- 固定参数：`aggression=1`。
- 实际档位：1,000,000 / 749,999 / 500,000 / 349,999 / 250,000 / 180,000 tris。
- 所有档位从同一份 `EDC_Full_Source.obj` 独立生成。
- 使用相同 Y 高度规则重新分为 L1/L2/L3/L6/L7；程序生成的导轨、磁铁和螺丝不变。
- UV 按折叠映射保留；验证渲染时按新拓扑执行 `Mesh.RecalculateNormals()` 与
  `Mesh.RecalculateTangents()`。

### 质量优先对照

另测试 `aggression=0`。该参数在实际 `416,273 tris` 处停止，无法达到 350k、250k 或 180k。
它的 500k/750k 画面略平稳，但仍存在相同的薄壁边缘趋势。这说明低于约 500k 后的问题不是
单纯调低 aggression 可以解决；要继续降面，需要显式锁定薄壁/孔洞边界或进行人工重拓扑。

### 固定渲染条件

- Unity `6000.5.6f1`，`Metal / Apple M4 Max`。
- `1200×800`，4× MSAA。
- 同一场景、URP/Lit 材质、贴图、灯光和曝光。
- 固定 `Top`、`Side`、`Hero`、`Open` 四个机位。
- 候选 OBJ 只从 `/tmp/fidgeting_edc_optimization_candidates` 读取；未覆盖源 FBX、正式 OBJ、
  prefab 或 `MeshyEDC.unity`。

## 量化结果

GPU mesh 估算采用 Position + Normal + Tangent + UV0 共 `48 B/vertex`，UInt32 index 共
`12 B/triangle`，不含对齐、驱动开销、纹理或 CPU 侧对象。

| Tris | Vertices | OBJ | 估算 GPU mesh | SSIM 平均（对 1995k） | Silhouette IoU 最低 | Edge F1 平均 |
| ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1,994,857 | 1,346,692 | 250.68 MiB | 84.48 MiB | 1.0000 | 1.0000 | 1.0000 |
| 1,000,000 | 733,297 | 131.89 MiB | 45.01 MiB | 0.7799 | 0.9796 | 0.8205 |
| **749,999** | **572,694** | **100.46 MiB** | **34.80 MiB** | **0.7674** | **0.9787** | **0.8096** |
| **500,000** | **411,300** | **68.92 MiB** | **24.55 MiB** | **0.7575** | **0.9768** | **0.8016** |
| 349,999 | 314,435 | 50.50 MiB | 18.40 MiB | 0.7478 | 0.9740 | 0.7925 |
| 250,000 | 246,911 | 38.03 MiB | 14.16 MiB | 0.7380 | 0.9715 | 0.7817 |
| 180,000 | 200,597 | 29.62 MiB | 11.24 MiB | 0.7296 | 0.9700 | 0.7696 |

绝对 SSIM 同时受到“源网格导入法线”和“新拓扑重算法线”的高光差异影响，因此还以 1M
重算法线档作为内部参照：750k 四视图平均 `0.9457`，500k 为 `0.9053`，350k 为
`0.8873`。Side 是最敏感机位：750k `0.8898`，500k `0.8400`，350k `0.8141`。

## 视觉检查

- Silhouette：到 500k 为止，Top/Hero 外轮廓与圆角总体稳定；350k 开始在 Side 的长薄边上
  出现连续波浪。
- 孔洞与薄壁：六个圆孔到 500k 仍可识别且基本圆整；500k 的侧壁高光已出现离散，350k
  进一步变成结构性锯齿。
- UV seam：未发现大片纹理错岛；直接转移旧法线会制造严重三角形反光，因此不能作为正式
  判定流程。
- 法线反光：1M 与 750k 在重算法线后显著接近基准；500k 在微距侧视可察觉，350k 不可接受。
- 磁铁/螺丝：它们是独立程序网格，没有参与本次减面，轮廓保持不变。
- Open 状态：500k 的底座边缘开始出现轻微波纹；350k 及以下在底壳和导轨邻近区域更明显。

## 拓扑风险

主梯度候选由通用 QEM 自动生成，并非最终可交付网格。750k 档检测到 2 个近零面积三角形和
67 条非流形边；质量优先的 aggression=0 版本为 1 个近零面积三角形和 53 条非流形边。
正式替换资产前必须清理这些拓扑问题并重新跑四机位对比。所有候选 UV/Normal 数值均为有限值，
基准网格没有检测到退化三角形或非流形边。

## 产物

- `ContactSheet_RecomputedNormals.png`：六档四机位总览。
- `Closeups_RecomputedNormals.png`：孔洞、薄壁、Open 底座局部放大。
- `QualityFirst_A0_vs_A1.png`：quality-first 与主梯度的对照。
- `NormalsExperiment_1M.png`：旧法线转移与新拓扑重算法线的因果对照。
- `metrics.json` / `metrics.csv`：逐机位 SSIM、PSNR、MAE、轮廓 IoU 和边缘 F1。
- `geometry-metrics.json`：面数、顶点、文件体积、buffer 估算与拓扑统计。
- `UnityMetal_RecomputedNormals/`：基准及六档的原始 Top/Side/Hero/Open PNG。

## 实际验证命令

Unity 固定机位捕获：

```zsh
EDC_OPT_CANDIDATES=/tmp/fidgeting_edc_optimization_candidates \
EDC_OPT_RECALCULATE_NORMALS=1 \
EDC_OPT_OUTPUT="$PWD/Artifacts/EDC/OptimizationValidation/UnityMetal_RecomputedNormals" \
'/Applications/Unity/Hub/Editor/6000.5.6f1/Unity.app/Contents/MacOS/Unity' \
  -batchmode -quit \
  -projectPath "$PWD/unity/FidgetingApp" \
  -executeMethod FidgetingApp.EDC.Tests.Editor.EdcOptimizationVisualValidator.CaptureAll \
  -logFile /tmp/woz-edc-opt-recalc-all.log
```

iPhone 状态检查：

```zsh
xcrun devicectl list devices --filter "hardwareProperties.platform == 'iOS'" --timeout 30
xcrun devicectl device info details --device 556E86BF-7295-5622-AA58-02DF84A8E93F --timeout 30
xcrun devicectl device info lockState --device 556E86BF-7295-5622-AA58-02DF84A8E93F --timeout 30
```

设备解锁后，正式候选接入隔离构建再执行：

```zsh
./scripts/ios_build_and_install.sh --development
./scripts/ios_performance_soak.sh --development-gc
./scripts/ios_build_and_install.sh
FIDGET_AUDIT_ENVIRONMENT_C=24 \
FIDGET_AUDIT_BRIGHTNESS_PERCENT=50 \
FIDGET_AUDIT_POWER_STATE=unplugged \
  ./scripts/ios_performance_soak.sh
```
