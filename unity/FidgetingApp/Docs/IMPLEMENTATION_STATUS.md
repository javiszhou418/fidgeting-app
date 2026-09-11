# Fidgeting Interaction Integration Status

最后更新：2026-09-11

本文件回答一个问题：规格中的能力是否已经进入可运行代码。状态只按代码、场景接线和测试证据填写，不按聊天结论或文档完成度填写。

状态定义：

- `已集成并有测试`：运行时代码、产品接线和自动化测试齐全。
- `部分集成`：已有部分代码或接线，但还缺语义、生命周期、测试或真机环节。
- `仅规格`：只有设计规格，不能对外称为已实现。
- `待真机验收`：自动化能验证结构，但触感仍必须在 iPhone 上确认。

## 2026-09-11 GitHub 私有镜像（仓库备份，非产品交付）

> **状态：用户授权「推」后已完成首次上传。产品视觉/真机仍按各 feature 条目的「视觉批准待确认，未推送手机」；本段只记录 git/LFS 镜像证据。**

- 远程：**私有** [jiaweizhou0418/fidgeting-app](https://github.com/jiaweizhou0418/fidgeting-app)，默认分支 `main`，`main` tip `e1bcd782f`（含本段镜像记录）。
- LFS：`git lfs push origin --all` 上传 **18030** 对象、约 **12 GB**（日志 `/tmp/fidget-github-push-20260911.log`）；GitHub 曾提示 GH010 抽样校验 10000/18030，属大推送常见警告。
- 分支：**15** 条 `refs/heads/*`（`main`、`codex/gacha-build42`、`recovery/*`、`wip/stash-*`）。`refs/stash` 未推送（仍含历史 Builds 大 blob，仅本地）。
- 设备 IPA：**不进 git**；Release [device-ipas-20260911](https://github.com/jiaweizhou0418/fidgeting-app/releases/tag/device-ipas-20260911) 含 build **44×2、45、46、47** 五个 `.ipa`（源备份 `~/Documents/FidgetingApp-git-backup-20260911/ipa/`）。
- 本地 APFS 备份：`.git` 快照 `~/Documents/FidgetingApp-git-backup-20260911/dot-git-before-lfs-migrate/`（迁移前 `62d8bcd` 时代）。

## 2026-09-11 22:5x Premium Display Case · tri-spinner-slab-v3-cmf R009 退回 → R010 内容 fit + rarity CMF 候选

> **状态：用户 22:25 明确退回 R009 的偏心 pocket macro 与四产品乱序矩阵。R010 已用真实 shipping renderer 重做四款内容与四档 CMF，构建报告 pass，定向 EditMode 75/75，Fan Card 完整门禁 pass。该轮是静态构图、朝向、比例与材质变化，因此按录屏规则使用真实 Unity 静态截图；没有动画变化，无需录屏。视觉批准待确认，未推送手机。**

- R009 退回证据：`ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/v3-rev-009/rejected-20260911T222500+0800/`。确认根因：斜视 macro 的凸出视差被误当作居中证明；R004 ±90° 与 V3 −90° 重复旋转；来源产品场景未在 capture 前关闭；单一厚度 fit 把真实玩具缩小。旧图保留为 rejected history，不得进入 `reviewArtifactIds`。
- R010 runtime：`PremiumDisplayCaseV3PocketProfiles` 为四个 shipping model 定义 V3 本地朝向与 anchor；`AttachContentToCircularPocket` 用真实 mesh 顶点做径向 fit。三叶对齐机械轴心；双叶／推牌／扇牌对齐可见中心。四款中心误差 `≤0.00002 mm`、正视屏幕误差 `≤0.0003 px`；圆井占比依次 `90.2% / 79.3% / 100.0% / 100.0%`，均匀缩放，无来源场景几何混入。
- R010 rarity：`PremiumDisplayCaseV3RarityCmf` 由 `SetLabel` 的 rarity 驱动。zone 2/5/6/7 依锁定 muted 表切换冷钢／玫瑰青铜／灰蓝钛／香槟；header 仅用近黑同色相底色提案，几何、玩具比例、灯光和机制不变。候选 prefab：`Assets/Resources/Gacha/PremiumDisplayCaseGate12R010/PresentationRoot.prefab`；场景：`Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R010.unity`。
- 真 Unity 证据：`ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/v3-rev-010/`。审阅图：`Artifacts/TriSpinnerSlab/gate12-r010/gate12-r010-content-phone-matrix-20260911T145551Z.png`、`gate12-r010-content-center-proof-20260911T145551Z.png`、`gate12-r010-content-quarter-matrix-20260911T145551Z.png`、`gate12-r010-rarity-cmf-matrix-20260911T145551Z.png`；自动图像审查：`gate12-r010-review-audit-20260911T145551Z.json`。
- 验证：`PremiumDisplayCaseGate12R010Tests` 6/6；连同 R009、Gate11 parity、既有 DisplayCase、Gate12、Gacha choreography 共 75/75（`~/Library/Caches/fidgeting-renders/gate12-r010-prep/unity-r010-tests-20260911T145422Z.xml`）。`validate_fan_card_guardrails.py` 完整门禁 pass，轨道净距 `7.590 mm`；Fan Card 几何、轴心、三层、正背面 artwork 和机构未改。
- 仍未实现：contract Gate 08 可见档 soft-focus renderer feature；R010 只沿用现有 Bloom/Neutral/Vignette。不得把本轮截图说成柔焦已完成。
- 发布门禁：`PremiumDisplayCaseShippingFactory.ResourcesPath` 仍为 `Gacha/PremiumDisplayCaseGate12R004/PresentationRoot`；R010 未 build/install/launch。视觉批准前不得切换或推手机。

## 2026-09-11 21:0x Premium Display Case · tri-spinner-slab-v3-cmf Gate 12 R009 Unity shipping 候选预览（manifest rev 138，stage 12 draft）

> **状态：R009 构建报告曾为 `pass`，但用户 22:25 的直接视觉检查推翻该技术结论。偏心 macro 与四产品矩阵已明确 `Rejected` 并由 R010 取代；不得再请求批准或推送手机。**

- 候选资源：`Assets/Resources/Gacha/PremiumDisplayCaseGate12R009/`（`PresentationRoot.prefab`、`Gate12R009BeautyVolume.asset`、header TextMesh 深度测试材质/着色器）；场景 `Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R009.unity`。Gate 11 FBX 哈希 `51bdbd4a…` 未动；38 件 GEO、无 explode；口袋 `ContentFit` 65.4×65.4×14.5 mm、三叶奖品 62.9×59.8×14.5 mm、凸出 6.09 mm；运行时 receipt 驱动 Oxanium 顶栏（`LabelTextDepthTested` 修复背面透字）。
- 预览证据（整盒 only）：`ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/v3-rev-009/` — `shipping-hero.png`、六向标准视角、`phone-rest-{front,rear,quarter}.png`、`app-rig-current-yaw*` vs `app-rig-gate09-yaw*`（真 App 场景 `ThreeBladeMetalOriginal` 内 A=现有三盏方向光 / B=Gate09 棚灯+美化 Volume）、`turntable-frames/`（72f）、`app-turntable-frames/`（48f）、`gate12-r009-report.json`。本地对照拼图：`~/Library/Caches/fidgeting-renders/gate12-r009-review/{hero-4way,phone-3way,app-rig-ab}.png`。`Artifacts/TriSpinnerSlab/gate12-r009/*.mp4` 尚未 encode。
- 测试：`PremiumDisplayCaseGate12R009Tests`（候选 prefab、口袋 fit、标签、Beauty Volume 合约范围、工厂仍 R004、报告 pass）；与 Gate11 parity / 既有 Gate12 / Gacha choreography 同批回归见 `~/Library/Caches/fidgeting-renders/gate12-r009-prep/latest-test-results.txt`。
- 已知局限：URP Lit 代替 crystal/薄膜；无 soft-focus renderer feature；Neutral tonemap vs Blender AgX；正面手机构图可见 header 板柔光反射；Unity 无 Blender 反射地板。
- **轨道 A 真机推送路径（交付子任务 [Map Unity display-case delivery path](c736cc69-dbf9-44d2-acba-2b2f2c3ada93) 结论）**：用户明确批准 Gate 12 预览后，一步改 `PremiumDisplayCaseShippingFactory.ResourcesPath` → `Gacha/PremiumDisplayCaseGate12R009/PresentationRoot`（及可选：Gacha 灯组 A vs B）；再按 `scripts/device_delivery_geeone_tri_spinner.sh` / `device_delivery_gyro_haptics.sh` 同一套流程（Unity `6000.5.6f1`、`/tmp/fidgeting-app-ios-pipeline.lock` + `/tmp/fidgeting-app-unity-canonical.lock`、唯一 `Builds/iOS/DeviceJobs/<job>/`、单调 build 号、`delivery-result.json`）。仓库尚无专用 `premium-display-case` delivery 脚本——需在批准后新建或复制上述脚本并收窄 `SOURCE_FILES` 到 R009 候选 + 工厂 + Gacha 揭示接线。Gate 10 产物仍只留在 evidence；勿在未批准时覆盖 shipping `PremiumDisplayCaseGate12R004` 或 legacy `Assets/Resources/Gacha/PremiumDisplayCase.prefab`。
- 待定：用户 Gate 12 视觉批准；App 内灯组选 A 或 B；pipeline stage 12 `ready_for_review` 登记；`Artifacts/` 录屏；Track B（header 稀有度色 + 可换凹槽内容）。

## 2026-09-11 18:0x Premium Display Case · tri-spinner-slab-v3-cmf Gate 10 rev-003 重打包 + Gate 11 rev-004 Unity parity（manifest rev 138，Gate 12 draft）

> **状态：Gate 10 r5 / Gate 11 r4 按用户 16:3x 批量授权（原话「批准 09，并授权 10–11 校验通过就自动继续，到 Gate 12 Unity 预览再停下来给我看（推荐）」）在全部校验通过后记为 approved。Gate 12 r9 已开 draft。批量授权到此为止：真实 Unity shipping 预览待用户明确视觉批准；未构建、未推送手机。视觉批准待确认，未推送手机。**

- Gate 10 rev-003（stage r5，evidence `evidence/10-export/rev-003/`）：rev-002 FBX 把 Blender 空间变换烘在 `ROOT_PDC_PRESENTATION`（-90° X，×100），Unity 导入后根节点非 identity，被 Gate 11 `root_rotation_zero / root_scale_one` 拒。r5 只改 FBX 打包（`use_space_transform=False, axis_forward=Y, axis_up=Z, apply_unit_scale=True, FBX_SCALE_UNITS`），几何/材质/GLB/贴花与 rev-002 逐字节同源；往返校验、三角 91 008、无陀螺、碰撞策略全部 pass。r4 入 `historicalRevisions`。
- Gate 11 rev-004（stage r4，evidence `evidence/11-unity-parity/rev-004/`）：`Assets/_DisplayCase/Candidates/TriSpinnerSlabGate11R004/`（FBX 逐字节 = Gate 10 r5，`Editor/TriSpinnerSlabGate11ParityBuilder.cs`，`Reference/blender-parity-reference.json` 由 Blender 提取的 41 件 / 6 机位 / 18+3 面光表）。Unity 6000.5.6f1 URP batchmode：导入 `useFileScale + bakeAxisConversion` → 全节点 identity、Blender (x,y,z)→Unity (x,z,y)；7 区 URP Lit 材质（透明预乘 crystal α0.08 q3000 / liner α0.25 q2990，`_QueueOffset`）+ 标签贴花；面光 → 程序化 HDR 反射 cubemap（256，clamp 40）+ 1 主方向光 + 3 补光（预算 3/3）；相机按 Blender 物理参数（85 mm，36×24，front 正交 0.1952）。指标：逐件包围盒 Δ 0.000 mm、盒体尺寸 Δ 0.0 %、正面剪影 IoU **0.99795**（bbox Δ 1 px，对 Gate 09 `env-shipping-front.png`；Gate 06 Workbench 0.970 仅参考）；亮度列仅参考（Blender AgX vs Unity 线性）。EditMode `TriSpinnerSlabGate11ParityTests` 7/7（字节一致、shipping 资产哈希未动、identity/pivot、材质槽 7/7、透明排序、包围盒、报告 pass）。已知局限：URP Lit 代替 crystal 折射/薄膜、拉丝各向异性、钢琴黑清漆；无 tonemapping；螺栓孔 1 px 空洞。
- 证据/录屏：`Artifacts/TriSpinnerSlab/gate11-r004/gate11-r004-unity-parity-turntable-clear.mp4`（48f @24，真实 Unity 出货灯组，无后处理）+ `…-frame012.png`/`…-frame036.png`；`gate11-r004-blender-vs-unity-shipping-hero.png`、`gate11-r004-blender-vs-unity-front-and-silhouette.png`、`gate11-r004-blender-vs-unity-neutral.png`、`gate11-r004-unity-standard-views-sheet.png`（hero/top/left/right/low）。
- 登记：`tools/model-provenance-explorer/register_tri_spinner_slab_v3_gate10_rev005_gate11_rev004.py`（manifest rev 138；stage 11/12 legacy r3/r8 入历史；`currentState.batchAuthorization.consumed = [10, 11]`）；validate premium-display-case 0 error，11/12 approved，earliestProblem = 12-shipping draft「等待用户审批」。
- 未改动：`Assets/Resources/Gacha/PremiumDisplayCase.prefab`、`Assets/_DisplayCase/Scenes/PremiumDisplayCase.unity`、`Assets/_DisplayCase/Models/PremiumDisplayCase.fbx`、`PremiumDisplayCaseShippingFactory.ResourcesPath`（仍 Gate12R004）。轨道 A 的 iOS 构建/安装只能在 Gate 12 预览批准后进行。

## 2026-09-11 16:14 Premium Display Case · tri-spinner-slab-v3-cmf Gate 08 批准 + 两条轨道 → Gate 09 rev-004 环境（manifest rev 135，ready_for_review）

> **状态：用户 16:14「可以」批准 Gate 08 r5（rev 134，原话含两条未来变更说明），并要求分两条轨道：A = 把现有 slab 推到手机预览；B = 落实 header 背景色随稀有度 + 凹槽内容可替换。Gate 09 环境 rev-004 已出并登记 `ready_for_review`。Gate 10–12 与真机推送尚未开始；未推送手机。**

- 用户两点回答：① 陀螺**没有**合成进盒体网格或法线贴图——它是 `PIVOT_PDC_CONTENT_SLOT` 上的 caller-owned 内容，盒体导出不含它，凹槽是 Ø71.5 mm 通用圆井（按最大玩具 65 mm 定）；替换为石墨双叶 / 磁吸推牌 / 扑克牌 / EDC 属于 Unity 侧 content-fit 表 + slot 接线，不动盒体几何。② header 板背景色随稀有度 = zone 4 材质层面的每档基色（几何不变），需 contract rev 增加 `cmf.header_plate_rarity_map` 并重验 Gate 07。两项记入 `currentState.plannedChanges.trackB`；实施会重开 Gate 03/07，因此安排在轨道 A 手机预览之后。
- Gate 09 rev-004（`tools/blender/environment_tri_spinner_slab.py`）：同机位（hero/front/low）三种环境——NEUTRAL（Gate 07 中性灯）、REVIEW（Gate 08 灯组 + 审阅补光/灰世界）、SHIPPING（同灯组去审阅辅助 + 合约世界 `#000103`）。差异指标写入 `environment-report.json`（hero：review vs shipping 43.4% 像素 >8、neutral vs shipping 30.6%）。结论：Unity parity 目标是 SHIPPING 集，不是 REVIEW 集。合成表 `Artifacts/TriSpinnerSlab/gate09-r004/gate09-r004-environment-compare.png`。登记 stage 09 r4（legacy r3 入历史），13 资产，validate 无 error。
- 轨道 A 路线：Gate 09 批准 → Gate 10 导出 → Gate 11 parity → Gate 12 Unity 预览 → 用户明确视觉批准 → iOS 构建/安装。按 AGENTS 规则，未经 Gate 12 预览批准不得安装。交付工具链见上文 2026-09-11 21:0x 节（子任务 [Map Unity display-case delivery path](c736cc69-dbf9-44d2-acba-2b2f2c3ada93)）。
- 待定：Gate 09 批准；是否授权 Gate 10–11 通过校验即自动继续、只在 Gate 12 Unity 预览处停下来审批。
- **16:3x 用户选「批准 09，并授权 10–11 校验通过就自动继续，到 Gate 12 Unity 预览再停下来给我看」**（rev 136，`currentState.batchAuthorization`）。Gate 10 rev-002（`tools/blender/export_tri_spinner_slab_package.py`）：从批准的 Gate 07 blend 剥离灯/相机/地板/陀螺/切刀，38 件 + 3 个 empty，简化导出材质（Gate 07 每区常数 PBR，命名 `M_PDC_Export_*`），FBX（-Z/Y，FBX_SCALE_NONE，三角化，custom props）+ GLB（Y-up，COLOR_0=COLOR0，TEXCOORD_0=UV2）+ 标签 decal PNG/JSON + `export-manifest.json`（哈希、上游批准原话、合约 sha）+ `collision-policy.json`（Unity BoxCollider，无网格碰撞）；FBX/GLB 新场景往返校验全部通过（网格数、三角 91 008、外形 0.5 mm 内、根/slot 存在）；`export-review-glb-roundtrip.png`。按授权记为 approved（rev 137），Gate 11 开为 draft，导入目标 `Assets/_DisplayCase/Candidates/TriSpinnerSlabGate11R002/`。

## 2026-09-11 15:26 Premium Display Case · tri-spinner-slab-v3-cmf Gate 07 批准 + 材质库注册 → Gate 08 rev-005 灯光（manifest rev 133，ready_for_review）

> **状态：用户 15:26「确认」（IDE 打开 `gate07-r003-material-id-vs-render.png`）→ Gate 07 r6 `approved`（rev 132，原话 + 审阅资产 SHA + 合约 SHA + 清单）。按合约要求批准后把 9 条材质写入 `MaterialLibrary/materials.json`（`approved-gate07`），`materials.md` 重新生成，`validate-material-library` ok（27 材质）。Gate 08 灯光 rev-005 已在批准材质上出证据并登记 `ready_for_review`。未构建、未推送手机。**

- 材质库新增：`case-clear-crystal`、`case-smoke-lilac-liner`（新 family `glass`）、`case-dark-sandblast`（scheme A `#5C6266` 取代规格 `#AEB3B6`）、`case-piano-black`、`case-bright-mirror`（取代烟色镜面 `#667078`）、`case-champagne-gold-inlay`、三档稀有度金属 `case-rose-bronze-tier` / `case-grey-blue-titanium-tier` / `case-champagne-tier`；`steel-satin` 增加本变体 usedBy（各向异性 0.8）。均 `unity: null`（Gate 10/11 再补 Unity 块）；球体缩略图未渲染。
- Gate 08 脚本 `tools/blender/light_tri_spinner_slab_beauty.py`：核对 `pdc-v3-g07-material-blend` SHA；删除中性灯；以 `render_tri_spinner_slab_cmf_preview.py`（main 已加 `__main__` 守卫，可 import）构建合约 rev-013 `lighting.beauty` 灯组（主光/条光/顶轨/冷紫 rim 30/26%/四条彩色边光/8 颗 sparkle/前补/审阅补光，glossy filter 0），p97 校准到 0.86（0.2535×14.69 → 0.7922×1.198）；所有灯 `Object.visible_camera=False`（低角机位曾直接看到底部粉色边光成一大块品红，修正后重渲三张斜/低视图；低角机位在 lookdev 地板之下，该视图隐藏地板）。输出：`beauty-hero-{clean,soft}.png`（合约 soft_focus：阈值 0.7–1.5、模糊 15/61 px、混合 0.30/0.075，3.44% 像素）、`beauty-{left,right,low}-oblique.png`、诊断通道 `pass-{clay,normal,depth,roughness}-hero.png`（clay 材质覆盖；normal 世界空间；depth 用 mist 覆盖盒体范围；roughness 为每个材质写入的 AOV，陀螺无 AOV 为黑）、四档 clean+soft、144 帧 beauty 转台（合约 2.5°/帧）与 0/25/90/200/335° 静帧。
- 事故：两次局部重渲覆盖了完整跑的 `lighting-report.json`；已用最终局部跑的 hero/soft/passes 数据 + 完整跑的转台目录重组报告并注明；脚本改为局部运行写 `lighting-report-partial.json`、不再覆盖 blend。
- 证据/录屏：`evidence/08-lighting/rev-005/`；`Artifacts/TriSpinnerSlab/gate08-r005/gate08-r005-beauty-turntable-clear.mp4`（144f 1440×960）+ 五个角度静帧；`gate08-r005-beauty-board.png`、`gate08-r005-diagnostic-passes.png`、`gate08-r005-rarity-muted-tiers-beauty.png`。
- 登记：`register_tri_spinner_slab_v3_gate07_approval.py`（rev 132）、`register_tri_spinner_slab_v3_gate08_rev005.py`（rev 133，stage 08 r5，legacy r4 入历史，34 资产、14 review）。validate 无 error。
- 待定：Gate 08 rev-005 用户批准（beauty 板 + 转台 + 诊断通道）；之后 Gate 09 环境（中性 vs shipping 环境同机位对比）。

## 2026-09-11 14:45 Premium Display Case · tri-spinner-slab-v3-cmf Gate 03–06 批准 → Gate 07 rev-003 材质（manifest rev 131，ready_for_review）

> **状态：用户 14:45「批准」（回应「认可就说“批准 03–06”」，IDE 打开 `gate06-r011-geometry-turntable-clear.mp4`）→ Gate 03 r17 / 04 r44 / 05 r17 / 06 r11 `approved`（rev 130，`register_tri_spinner_slab_v3_rev013_approval.py`，原话 + 审阅资产 SHA + 合约 SHA + 清单）。Gate 07 材质 rev-003 已在批准几何上出证据并登记 `ready_for_review`。材质库未写入，未构建、未推送手机。**

- 脚本：`tools/blender/make_tri_spinner_slab_label_decal.py`（Pillow + `Oxanium-VariableFont_wght.ttf`：标题 SemiBold 7.4 mm、系列行 Medium 3.6 mm、0.18 mm 横线、两栏规格 2.6 mm，原生字距无 tracking，遵循 FDB-GAC-009 字体规则；文案为 V3 概念占位，运行时由 App 填真实值）与 `tools/blender/lookdev_tri_spinner_slab_materials.py`（快照入 evidence）。后者先核对 `pdc-v3-g06-geometry-blend` SHA，再在不改几何的前提下建七区材质：zone 5 拉丝钢（材质库 `steel-satin` 数值 + scheme A 各向异性 0.8、UV2.x 方向细纹 ±0.015 粗糙度/0.0015 mm 微凸，按库「远看不见拉丝纹」的要求压低）、zone 3 深喷砂（scheme A `#5C6266`，合约 feature 0.13 mm / bump 0.0105 mm / 粗糙度 0.45±0.03）、zone 6 亮镜面 `#C9D0D6` 0.04、zone 4 钢琴黑清漆（coat 1.0/0.03）、zone 7 香槟金各向异性沿饰条长轴、zone 1 整片薄膜 300–650 nm、zone 2 烟色内衬吸收；header 板 = 钢琴黑 + 标签 decal（平面映射到板面范围，油墨粗糙度 0.55）；数值板留白不画任何占位 UI。
- 灯光：合约 `lighting.neutral`（key/fill/rear 5600 K，1.0/0.25/0.18，黑背景，无彩色无 bloom），按 `lighting.calibration` 用 18% 灰卡校准到 0.18 场景线性（两轮，最终 0.1749×1.029）。fill 放在相机后方大面积，让正面拉丝平面反射灰场而不是黑世界。
- 证据：`evidence/07-material/rev-003/`：`material-{hero,front,header-macro,main-cmf-macro,crystal-bevel-macro,pocket-rim-macro}.png`、`material-id-{hero,front}.png`、`material-hero-tier-{steel,copper,titanium,gold}.png`、`header-label-decal.{png,json}`、`material-revalidation*.json`、`tri-spinner-slab-material-r003.blend`。录屏：`Artifacts/TriSpinnerSlab/gate07-r003/gate07-r003-material-neutral-turntable-clear.mp4`（72f）+ frame；合成表 `gate07-r003-material-board.png`、`gate07-r003-material-id-vs-render.png`、`gate07-r003-rarity-muted-tiers-neutral.png`。
- 登记：`register_tri_spinner_slab_v3_gate07_rev003.py` → manifest rev 131，stage 07 r6（legacy r5 入历史），27 资产、11 review；validate `errors: []`。材质库注册提案 7 条写在 revalidation（批准后再写 `materials.json`）。
- 已知限制：标签文案占位；拉丝/喷砂为程序纹理，Gate 10 需烘或改 URP detail；薄膜在 URP Lit 无对应项，Gate 11 需自定义 shader 或近似；中性板比 Gate 05 美术预览更暗（设计如此）。
- 待定：Gate 07 rev-003 用户批准（材质板 + 中性转台 + 分区图）；批准后写材质库并进 Gate 08 灯光（rev-013 合约灯光方向正式校准）。

## 2026-09-11 09:20 Premium Display Case · tri-spinner-slab-v3-cmf 缝透底 → Gate 03–05 rev-013 + Gate 06 rev-011（manifest rev 129）

> **状态：用户 09:20 在 Gate 06 rev-010 尺寸图上框出两岛之间的抛光条：「这个地方没有这个条，是透底的」。rev-012 的抛光平齐缝被否；rev-013 退役 `GEO_PDC_COMPARTMENT_SEAM`，2.4 mm 缝直通后板（zone 3 喷砂）。其余与 rev-012 相同。Gate 03–05 rev-013、Gate 06 rev-011 `ready_for_review`；已批准的 rev-012 记入历史。未推送手机。**

- contract rev-013（sha `e9a6f14a61e8…`，35/35）：新增 `interior.seam_open_to_backplate=true`，退役 `interior.seam_cmf_zone` / `interior.seam_flush_with_shelf`；原话入 `sources`（`src.user_gate06_rev010_seam_feedback_20260911`）。builder 断言 `seam-open-to-backplate-rev013`（无缝物体）；architecture rev-035 32 核心件 `core_match`；blockout 37/37；Gate 06 rev-011 16/16，38 件全部水密，91 008 三角。
- 事故：10:11 Mac 重启打断首轮渲染（stills 09:40–09:46 完成，转台未完成；`/tmp` 中的帧与日志随重启丢失）。三个脚本的转台帧目录改到 `~/Library/Caches/fidgeting-renders/`（不随重启清空），10:40 起重跑白模转台、CMF 全套、四档、柔光对、Gate 06。用户 10:38 问「卡死了吗」——不是卡死，是重启。
- 证据/录屏：`Artifacts/TriSpinnerSlab/gate05-r013/gate05-r013-cmf-preview-turntable-clear.mp4`、`gate05-r013-blockout-turntable-clear.mp4`、`gate05-r013-vs-r012-front.png`、`gate05-r013-seam-open-vs-r012-front-crop.png`、`gate05-r013-rarity-muted-tiers-hero.png`；`Artifacts/TriSpinnerSlab/gate06-r011/gate06-r011-geometry-turntable-clear.mp4`、`gate06-r011-six-ortho-views.png`、`gate06-r011-dimension-overlay-{front,left}.png`；固定机位包 10/10；柔光 clean/soft 3.9% 像素。
- 登记：`register_tri_spinner_slab_v3_rev013.py`（rev 128，stage 03 r17 / 04 r44 / 05 r17；rev-012 批准决定入 `historicalRevisions`/`historicalDecisions`）、`register_tri_spinner_slab_v3_gate06_rev011.py`（rev 129，stage 06 r11，rev-010 记 `revised`）。validate 无 error。
- 设计圣经：`FDB-DSP-062` ③ 改为「缝透底」。
- 待定：Gate 03–06 rev-013/011 逐 gate 批准；之后 Gate 07 材质。

## 2026-09-11 07:57 Premium Display Case · tri-spinner-slab-v3-cmf Gate 06 rev-009 精修 → Gate 03–05 rev-012 + Gate 06 rev-010（manifest rev 125）

> **状态：用户 07:50 误以为 Gate 06 技术图是质感倒退（已补同材质校验图与说明表，manifest rev 123）；07:57 提出五项几何精修并在追问中选定幅度（2.8 mm 边框 / 3.5 mm 切角 / 保留短金线）。contract rev-012、architecture rev-034、blockout rev-012、Gate 06 rev-010 已重建、渲染、录屏、登记；Gate 03–06 `ready_for_review`，已批准的 rev-011 与 rev-009 记入历史（`revised`）。未构建、未推送手机。**

- 用户原话（07:57）已逐字入 contract `sources`（`src.user_gate06_rev009_feedback_20260911`）与 history。五项对应：① header 镜面分隔线退役（参考图那条横线是印刷标签的一部分 → Gate 07 decal）；② 数值板保持平面（`trait.carve_tracks=false`、`trait.render_mode=runtime-ui-overlay`），不雕槽/刻度/填充，TRAIT PROFILE 由运行时按 `ToyTalentCatalog` 绘制；③ 两岛之间的缝改为 zone 6 高亮抛光并与台面平齐（`interior.seam_cmf_zone=6`、`interior.seam_flush_with_shelf=true`）；④ 边框 `main.perimeter_shelf_over_width` 0.045→0.0276（4.56→2.80 mm），外壳保持已批准 101.28 × 171.78 mm，省下的宽度给 field（`main.field_side_margin_mm` 3.0→4.76）；⑤ 两岛切角 8.0→3.5 mm（field 切角 1.86 mm）。配套：`main.field_outline_groove_inset_mm` 1.6→1.0、`interior.junction_fillet_min_mm` 0.8→0.3（否则最内圈刻线自交），builder 新增布尔后 0.03 mm 去重/去退化（field 3467→3368 顶点），否则 field 留 3–9 条开放边。凹槽中心 −20.68 mm 基本不动。
- 幅度确认：先出 3.24 mm / 4.5 mm 提案对比（`Artifacts/TriSpinnerSlab/gate05-r012-proposal/`），用户选「再窄一点 2.8 mm」「更尖 3.5 mm」「保留短线」，随后重解合约。
- 验证：contract 35/35（新增 `frame-bands-thinner-than-rev011`、`island-chamfer-sharper-than-rev011`、`approved-envelope-kept`、`trait-plaque-not-carved`、`seam-polished-flush`）；builder 37/37（新增 `seam-polished-flush-rev012`、`no-header-divider-line-rev012`、`trait-plaque-flat-reserved-rev012`）；architecture `core_match`（33 核心件）；Gate 06 rev-010 16/16，39 件全部水密，91 964 三角。
- 证据/录屏：`Artifacts/TriSpinnerSlab/gate05-r012/gate05-r012-cmf-preview-turntable-clear.mp4`、`gate05-r012-blockout-turntable-clear.mp4`、`gate05-r012-vs-r011-{front,hero}.png`、`gate05-r012-rarity-muted-tiers-hero.png`；`Artifacts/TriSpinnerSlab/gate06-r010/gate06-r010-geometry-turntable-clear.mp4`、`gate06-r010-six-ortho-views.png`、`gate06-r010-dimension-overlay-{front,left}.png`；固定机位包 10/10；柔光 clean/soft 4.19% 像素。
- 登记：`register_tri_spinner_slab_v3_rev012.py`（manifest rev 124，stage 03 r16 / 04 r43 / 05 r16；rev-011 的批准决定保存在 `historicalRevisions` 与 `historicalDecisions`）、`register_tri_spinner_slab_v3_gate06_rev010.py`（rev 125，stage 06 r10，rev-009 记 `revised`）。validate 无 error。
- 设计圣经：新增 `FDB-DSP-062`（五项精修 + 幅度选择，Locked；`FDB-DSP-053` 的数值板呈现方式在本变体改为运行时 UI）。
- 待定：Gate 03–06 rev-012/010 逐 gate 批准；之后 Gate 07 材质（含 header 印刷 decal、拉丝/喷砂贴图）。
- **08:56–09:0x**：用户「继续」；追问「继续是否=批准 03–06」，用户选「批准 03–05（设计），06 精模我还要再看」→ Gate 03 r16 / 04 r43 / 05 r16 `approved`（`register_tri_spinner_slab_v3_rev012_approval.py`，manifest rev 126，选项原文 + 前一句「继续」入 decision），Gate 06 r10 保持 `ready_for_review`。为用户自审补 Gate 06 rev-010 同材质校验图 `cmf-check-hero.png` 与审阅包 `Artifacts/TriSpinnerSlab/gate06-r010/gate06-r010-review-pack.png`（manifest rev 127）。Gate 07 未开始（等 06 批准）。未推送手机。

## 2026-09-10 22:33 Premium Display Case · tri-spinner-slab-v3-cmf Gate 06 rev-009 精模（manifest rev 122，ready_for_review）

> **状态：用户 22:33「继续」→ 从已批准的 Gate 05 rev-011 白模出 Gate 06 静态几何。设计不变：只应用修改器、1 µm 去重/去退化、烘顶点通道、验证、出图。16/16 检查通过；Gate 06 `ready_for_review`，Gate 07–12 stale。未构建、未推送手机。**

- 脚本 `tools/blender/refine_tri_spinner_slab_geometry.py`（快照 `evidence/06-geometry/rev-009/refine_tri_spinner_slab_geometry.r009.py`）：先核对 `pdc-v3-blockout-blend` 的 SHA（`73cb942defae…`）再打开；对 43 个 `GEO_PDC_*` 主体网格按合约顺序应用全部修改器（bevel / weighted normal）；`remove_doubles 1e-6 m + dissolve_degenerate`（只动了 6 颗螺栓头 4944→4920 顶点、水晶框 2930→2926，来自 bevel/boolean 碎片）；删除 `CUT_PDC_*` 与 preview-only 物体；审阅陀螺（caller-owned）留在 `COL_PDC_REFERENCE_LOCKED` 并隐藏。
- 顶点通道（合约 `vertex_channels`）：`COLOR0` 为 CORNER 域 byte colour——r/g = 边缘 mask（面积 < 2.5 mm² 的 bevel/fillet 条带 = 1，平面与侧壁 = 0；g 仅 zone 1 水晶，边缘面积占比 1.92%），b = finish_mix（zone 6 镜面 = 1），a = 1；`UV2.x` 拉丝方向（边框水平 0，金饰随长轴 0 / 0.5），`UV2.y` = zone/255。
- 完整性：43 件全部水密（0 非流形、0 边界边）、0 退化、0 重复顶点、体积为正；三角 96 134 / 预算 120 000（六颗螺栓头各 9 888，占 59 k——Gate 10 导出时减面候选）；材质 slot 7 / 7。尺寸 W 101.29 × H 171.79 × 结构 D 10.96 mm 与合约一致；`PIVOT_PDC_CONTENT_SLOT` 于 canonical (0, −20.69, −1.275) mm。身份 digest：顶点 `ebae61e1968b…`、矩阵 `94ed5e865413…`、拓扑 `0bfc578cb0fe…`。
- 证据：`tri-spinner-slab-geometry-r009.blend`、审阅 GLB `tri-spinner-slab-gate06-review-r009.glb`（非 Gate 10 导出）、`geometry-revalidation.json`、六向正交 `ortho-{front,back,top,bottom,left,right}.png`（首版 front/back 相机方向反了，已修正重出）、`geometry-workbench-hero.png`、`dimension-overlay-{front,left}.png`、`fixed-views/`（`capture_standard_views.py` 10/10）、`internal-exploded-zstack.png`（internalOnly，不进 review）。录屏：`Artifacts/TriSpinnerSlab/gate06-r009/gate06-r009-geometry-turntable-clear.mp4`（72f 1440×960 h264）+ `…-frame-036.png`；`gate06-r009-six-ortho-views.png`。
- 登记：`register_tri_spinner_slab_v3_gate06_rev009.py` → manifest rev 122；stage 06 r9（legacy R003 r8 连原批准入 `historicalRevisions`），29 资产、16 review 资产（含交互 GLB 与完整转台）；审阅 GLB role 首次误写 `review-export`，改为 `export` + contentClass 标注非 shipping 导出。`validate-pipelines.mjs` / `validate_model_pipeline.mjs` 无 error（后者仅提示 1 个未 hash 的旧 DesignBibleAssets 图）。
- `npm test`（model-provenance-explorer）：`pipeline-core` 4 失败 + magnetic-slide 多项失败，均为旧状态断言（如 PDC Gate 02 `analysisSpec.revision === 6`，而 v3 重建 09:49 已开 rev 16；magnetic-slide 测试指向其他模型）。与本步无关、早于本步存在；未在本任务改测试。
- 待定：Gate 06 rev-009 用户批准（交互 GLB / 完整转台 / 六视图）。之后 Gate 07 材质（neutral PBR board + closeup，按合约 rev-011 材质与 muted 色板）。

## 2026-09-10 21:17 Premium Display Case · tri-spinner-slab-v3-cmf Gate 03–05 rev-011 用户批准（manifest rev 120）

> **状态：用户 21:17 原话「这版通过了」（IDE 中打开着 `gate05-r011-cmf-preview-turntable-clear.mp4`），对应 18:15 回复请求的「批准 Gate 03/04/05」。Gate 03 r15 / 04 r42 / 05 r15 记为 `approved`；Gate 01–02 仍 `ready_for_review`，待用户确认是否一并通过；Gate 06 尚未开（需 01–05 全部批准）。这是 blockout 级批准，不是 shipping 预览批准：未构建、未推送手机，`DesignBibleAssets/` 未复制任何图。**

- 批准记录（`register_tri_spinner_slab_v3_rev011_approval.py`）：每个 stage 的 `decision` 含原话、决定时间、渠道 chat、审阅资产列表及 SHA-256、合约 SHA `f102ac87fbcc…`、参数快照（`resolved_key_values_mm`）、查看清单、交互方式（Gate 05：完整转台录像 + 静帧在 IDE 查看；Gate 03/04：文档与看板）。`history.ndjson` 三条 `user-approval` 事件。`currentState.contractApproval / architectureApproval / blockoutApproval` 更新。validate `errors: []`。
- 批准范围：rev-011 几何（无翼板、等宽边框、8 mm 岛倒角、Ø71.5 通用圆井、数值板）、CMF scheme A 分区、稀有度宽口径 + muted 色板、灯光方向「对标参考图」、柔光提案档（仅 Gate 08 输出）。
- 下一步：用户确认 Gate 01–02 后以 `--include-gates-01-02` 重跑批准脚本开 Gate 06（精模：倒角/圆角保真、COLOR0.g 边缘虹彩 mask 烘焙、UV2 拉丝方向、水密导出准备）。
- **21:2x 追问结果**：用户选「一并通过，开 Gate 06（推荐）」→ Gate 01 r7 / 02 r16 记为 `approved`（原话 + 前置原话「这版通过了」、`src.user_gate01_02_approval_20260910`），Gate 06 开为 `draft`（`activeStageId = 06-geometry`），manifest rev 121，validate `errors: []`。Gate 07–12 仍 stale。仍未构建、未推送手机。

## 2026-09-10 18:15 Premium Display Case · tri-spinner-slab-v3-cmf 灯光方向 + muted 色板决定 → Gate 03–05 rev-011（几何 = rev-009，manifest rev 119）

> **状态：用户 16:5x 选定灯光「③ 对标参考图」与 muted 色板。contract rev-011 写入两者；architecture rev-033、blockout rev-011 按新 hash 重出；CMF 预览脚本改为从合约读灯组、薄膜与色板。Gate 03–05 `ready_for_review`。视觉批准待确认，未推送手机。**

- contract rev-011（sha `f102ac87fbcc…`，30/30 断言）：`lighting.beauty` 新增 4 条背侧掠射彩色边光 `LGT_PDC_EDGE_{L_CYAN,T_BLUE,R_MAGENTA,B_PINK}`（1.3/0.9/1.2/0.8× 主光，y = −0.22 在盒体后方）、`sparkle_group`（8 颗 0.03B 方形小硬光，青/白/品红循环，0.16× 各）、rim 上限 0.05/0.03 → 0.30/0.26、彩色灯上限 8% → 300%（旧值存 `…_superseded`，注明 FDB-DSP-061 仅限本变体）、`render_glossy_filter 0`、`review_fill`（顶补光 0.25、中性暗世界）。`materials[1]` 薄膜改整片水晶 300–650 nm（旧 `COLOR0.g` 280–380 存 superseded；COLOR0.g 变为可选边缘增强，Gate 06 烘）。`cmf.rarity_tier_map` 改 muted：铜 `0.70/0.58/0.52`、烧钛蓝 `0.58/0.63/0.70`、金 `0.80/0.73/0.60`，钢不变；rev-010 饱和值记在 note。新增 `render.lighting_direction = reference-bling`。来源：两条反馈原话 + 决定选项原文。
- 预览脚本：`CONTRACT_TIER_MAP` / `render.lighting_direction` 驱动默认（`--bling contract-rig`），边光从 `lighting.beauty.lights` 建、sparkle 从 `sparkle_group` 展开、薄膜从 `materials[1]` 读；`--bling contract|reference`、`--muted` 仅作旧合约回退。rev-011 hero 19 灯，report `within_contract_lighting: true`。
- 渲染：stills 5 张 + CMF 转台 72f + 四档 muted（hero+front）+ 柔光 clean/soft（3.91% 像素）。Workbench 白模 36/36，architecture `core_match`。全套 17:07–17:28 完成；shell 在完成后挂起约 70 min（用户中断），非渲染问题。`run` 重试循环因 Blender 返回码非零多跑了两遍全套（三个转台目录，取最后一个 `…T170554`）。
- 录屏：`Artifacts/TriSpinnerSlab/gate05-r011/gate05-r011-cmf-preview-turntable-clear.mp4`、`gate05-r011-blockout-turntable-clear.mp4`（各 72f，h264）+ `…-frame-036.png`；合成表 `gate05-r011-rarity-muted-tiers-hero.png`、`gate05-r011-reference-vs-hero.png`、`gate05-r011-softfocus-contract-ab-hero.png`。
- 登记：`register_tri_spinner_slab_v3_rev011.py` → manifest rev 119；stage 03 r15 / 04 r42 / 05 r15；rev-010 决定 `state: revised`（两项反馈 + 选项原文）；validate `errors: []`。
- 设计圣经：`FDB-DSP-061` 转 Locked；`FDB-DSP-059` 色板值更新为 muted。
- 待定：Gate 03–05 rev-011 逐 gate 批准原话；Gate 11 parity 需用 URP 灯/反射探针复现边光与 sparkle。

## 2026-09-10 16:45 Premium Display Case · tri-spinner-slab-v3-cmf rev-010 灯光「bling」与 muted 色板研究（manifest rev 118，几何/合约不变）

> **状态：用户 16:27「光源是可以调整的吧？…不管是从光源还是光的颜色色相上面，好像我们这个都有点单一，就是没有那种布灵布灵闪闪发光、光泽感的效果」；16:31「这几个颜色饱和度都有点高，感觉土土的。觉得土豪的感觉」。两项均以提案渲染附在 Gate 05 rev-010（stage r14 不变）；合约灯组、`cmf.rarity_tier_map`、几何未改。待用户选。视觉批准待确认，未推送手机。**

- 灯光现状原因：合约 `lighting.beauty` 是单一 5600K 大主光 + 6500K 条光 + 5000K 顶轨，彩色 rim 上限 8%，世界近黑；审阅时又加了灰世界大补光，所以反射平、色相单一。`materials[1]` 里本来就写了水晶薄膜虹彩（`thin_film_mask COLOR0.g`、280–380 nm、IOR 1.33–1.38），但预览脚本此前未实现，builder 也未写 COLOR0.g。
- `render_tri_spinner_slab_cmf_preview.py` 新增 `--bling contract|reference`：② 合约内 = 薄膜（合约范围，Pointiness+Facing 暂代 COLOR0.g，Gate 06 再烘 mask）+ 彩色 rim 顶到 8% + 8 颗小硬光（sparkle）+ `blur_glossy 0`；③ 对标参考图 = ② + 四条背侧掠射边光（左青 #4FD2FF 1.3×、顶蓝 0.9×、右品红 #FF5FD6 1.2×、底粉 0.8×，相对主光）+ rim 30%/26% + 整片水晶薄膜 300–650 nm + 青/白/品红小硬光 + 顶补光减半、世界减半。③ 超出合约 8% 彩色上限与薄膜范围，stamp 标 `BLING LOOKDEV PROPOSAL`。第一版③用青/品红环境渐变把整个画面染蓝，内部否决，改为中性暗世界（`cmf-preview-hero-bling-reference.png` 被第二版覆盖，未登记过）。
- 色板：`--muted` 提案，同色相、饱和度降到约 40%、明度贴近钢底：铜 `(0.80,0.50,0.30)→(0.70,0.58,0.52)` 玫瑰青铜；烧钛蓝 `(0.58,0.66,0.80)→(0.58,0.63,0.70)` 灰蓝钛；金 `(0.96,0.78,0.38)→(0.80,0.73,0.60)` 香槟；钢不变。HLS 饱和度 0.56/0.35/0.88 → 0.23/0.17/0.33。
- 证据：`Artifacts/TriSpinnerSlab/gate05-r010/gate05-r010-bling-lighting-proposal-v3-hero.png`（参考图 / 现状 / ② / ③）、`gate05-r010-bling-reference-front-macro.png`、`gate05-r010-rarity-palette-saturated-vs-muted.png`；rev-010 evidence 下 `cmf-preview-{hero,front}-bling-{contract,reference}.png`、`cmf-preview-pocket-rim-macro-bling-reference.png`、`cmf-preview-hero-tier-{copper,titanium,gold}-bold-muted.png`。静态提案，无动画，只出静帧。
- 登记：`register_tri_spinner_slab_v3_rev010_lookdev_study.py` → manifest rev 118（11 资产，`blockoutSpec.lookdevStudy`），两条 `user-feedback` 事件；validate `errors: []`。Cycles Metal 内核编译偶发崩溃（`MetalKernelPipeline::compile` NSURL nil，exit 134）两次，重跑即过。
- 待定：灯光取 ②/③（③ 需改合约 `lighting.beauty` 彩色上限与灯组，并把薄膜范围写进 `materials[1]`）；色板是否采用 muted（改 `cmf.rarity_tier_map`）。两者一起进 contract rev-011。

## 2026-09-10 16:30 Premium Display Case · tri-spinner-slab-v3-cmf 柔光档位决定 → Gate 03–05 rev-010（仅 soft_focus，几何 = rev-009，manifest rev 117）

> **状态：用户在四档研究中选「③ 提案可见档：阈值 0.7–1.5，半径 ×3，混合 ×3（改合约 soft_focus 范围）」。contract rev-010 只改 `soft_focus` 与来源；几何、全部参数与 rev-009 相同。按 rev-010 hash 重新出 architecture rev-032、blockout rev-010（Workbench + Cycles 录屏、四档稀有度、clean/soft 对）。Gate 03–05 `ready_for_review`。视觉批准待确认，未推送手机。**

- contract rev-010（sha `f6efa458dc89…`，28/28 断言，新增 `soft-focus-user-visible-level`）：`soft_focus.highlight_smoothstep` `[0.9,1.8]→[0.7,1.5]`，`blur_radius_relative_to_long_edge` `[0.0025,0.01]→[0.0075,0.03]`，`blur_mix_weight_ranges` `[[0.08,0.12],[0.02,0.03]]→[[0.24,0.36],[0.06,0.09]]`；遮罩（crystal/mirror/spinner）、排除项、`enabled_only_for_final_beauty`、`global_blur_forbidden` 不变；`spec_ranges_superseded` 保留原值。来源 `src.user_gate05_rev009_softfocus_decision_20260910`（选项原文）。`render.soft_focus_stage` 仍 `gate-08-final-beauty-only`。
- 验证：`--soft-focus`（合约中值）在 rev-010 hero 上 4.83% 像素变化 > 8/255，与研究中的③一致；审阅图（stills、转台、四档）全部 clean。builder 36/36，architecture `core_match: true`，几何与 rev-009 逐项一致。
- 录屏：`Artifacts/TriSpinnerSlab/gate05-r010/gate05-r010-blockout-turntable-clear.mp4`、`gate05-r010-cmf-preview-turntable-clear.mp4`（各 72f，h264 yuv420p）+ `…-frame-036.png`；`gate05-r010-softfocus-contract-ab-hero.png`（clean vs 新合约 soft）；`gate05-r010-rarity-bold-tiers-hero.png`。
- 登记：`register_tri_spinner_slab_v3_rev010.py` → manifest rev 117；stage 03 r14 / 04 r41 / 05 r14；rev-009 决定 `state: revised`（柔光选项原文）。`validate-pipelines.mjs` `errors: []`。copper 档首次渲染 Blender 异常退出（exit 134，无错误文本），重跑成功。
- 设计圣经：`FDB-DSP-060` ② 转 Locked（所选档位与合约值）。
- 待定：Gate 03–05 rev-010 逐 gate 批准原话；Unity URP 侧 bloom 与该合约值的对应（Gate 11 parity）。

## 2026-09-10 16:05 Premium Display Case · tri-spinner-slab-v3-cmf Gate 05 rev-008 精修 → Gate 03–05 rev-009（去翼板 + 柔光可见性研究，manifest rev 116）

> **状态：用户 15:19 原话「把这四个角去掉吧，有点太复杂了，然后柔光效果还是没看到」（红箭头指四片翼板）。rev-008 记为 `revised`（非驳回），contract rev-009 / architecture rev-031 / blockout rev-009 已重建、渲染、录屏并登记；Gate 03–05 `ready_for_review`。视觉批准待确认，未推送手机。**

- 几何：`main.wing_count` 4 → 0，`GEO_PDC_MAIN_WING_{TL,TR,BL,BR}` 退役；翼板五个输入与 `main.wing_half_span_mm` 退役。凹槽中心通过新增 `main.pocket_top_clearance_mm = 4.14`（= 原 0.94 缝 + 3.2 翼板偏移）保持 rev-008 位置（y = −20.69 mm，contract 断言 `pocket-centre-unchanged-from-rev008`）。其余几何、边框等宽、金饰镜像、数值板不变。contract 27/27 断言通过，sha `22c31ce550c5…`；builder 36/36 检查通过（新增 `no-wings-rev009`）；architecture `core_match: true`（34 核心件）。
- contract 同时记录稀有度决定：`cmf.rarity_aperture = bold`、`cmf.rarity_tier_map`（Standard 钢 / Refined 铜 / Signature 烧钛蓝 / Heirloom 金，预览值，Gate 07 定最终粗糙度/各向异性）、`render.soft_focus_stage = gate-08-final-beauty-only`。来源 `src.user_gate05_rev008_feedback_20260910` 与 `src.user_gate05_rev008_variation_decisions_20260910` 原话入 `sources`。
- 柔光可见性研究（用户「还是没看到」）：`render_tri_spinner_slab_cmf_preview.py` 新增 `--soft-level mid|max`、`--soft-gain`、`--soft-radius-scale`、`--soft-threshold`；在 rev-009 hero 上出 clean / 合约中值 / 合约上限 / 提案×3 / 演示×6 五档。像素变化（>8/255）：中值 1.36%、上限 1.49%、提案（阈值 0.7–1.5、半径 ×3、混合 ×3）4.83%、演示 ×6 11.65%。结论：合约 `soft_focus` 范围内只是高光细晕，肉眼几乎不可见；要「看得见」必须放宽合约范围（提案档），这是设计决定，待用户选。审阅图仍 clean（用户 15:0x 选 Gate 08）。超出合约的两档在 stamp 上标 `SOFT-FOCUS DEMO OUT OF CONTRACT`。
- 录屏：`Artifacts/TriSpinnerSlab/gate05-r009/gate05-r009-blockout-turntable-clear.mp4`（Workbench 分区色，72f 1440×960）与 `gate05-r009-cmf-preview-turntable-clear.mp4`（Cycles CMF，72f 1280×852），各附 `…-frame-036.png`；h264 yuv420p faststart，raw 帧留在 `/tmp`。合成表：`gate05-r009-wings-removed-compare-hero.png`、`gate05-r009-rarity-bold-tiers-hero.png`、`gate05-r009-softfocus-4way-hero.png`。
- 登记：`register_tri_spinner_slab_v3_rev009.py` → manifest rev 116；stage 03 r13 / 04 r40 / 05 r13；rev-008 决定 `state: revised` 原话保存；Gate 06–12 stale。`validate-pipelines.mjs` `errors: []`。
- 设计圣经：`FDB-DSP-059` 追加 rev-009 说明；新增 `FDB-DSP-060`（去翼板 + 柔光可见性结论，待用户选柔光档）。
- 待定：柔光取「合约现状（几乎不可见）」「提案可见档（改合约 soft_focus 范围）」或「不要柔光」；Gate 03–05 rev-009 逐 gate 批准原话。

## 2026-09-10 15:20 Premium Display Case · tri-spinner-slab-v3-cmf rev-008 稀有度变体研究 + 柔光 A/B（manifest rev 114，几何不变）

> **状态：用户 14:33 认可 rev-008 的结构、材质、细节方向（非逐 gate 批准），要求按抽取稀有度做颜色与金银铜变体，并问柔光是否该在此步加。已在 rev-008 白模上渲染 3 口径 × 4 档矩阵 + Signature 烧钛蓝备选 + 柔光 A/B，作为 Gate 05 rev-008 的补充研究资产登记（stage rev 12 不变）。几何、contract 未改；材质值仍属 Gate 07；口径、Signature 颜色、柔光时机待用户选择。视觉批准待确认，未推送手机。** 原话写入 `history.ndjson`（event `c99e66db`，type `user-variation-request`）与 `blockoutSpec.rarityVariationStudy`。

- 档位映射：沿用 shipping 的 `PremiumDisplayCaseFoilTier` 顺序 Steel / Copper / Silver / Gold（`PremiumDisplayCaseLabelPlate.foilByTier` 颜色）对应 `GachaRarity` Standard / Refined / Signature / Heirloom；内衬缝色按 `FDB-DSP-014`（低阶冷银、中阶蓝钛／香槟、高阶烟紫）。未在 contract、场景或 prefab 另设数值。
- 三种口径（`render_tri_spinner_slab_cmf_preview.py` 新增 `--tier`、`--medium`、`--bold`）：窄——只有金饰条／轨／索引块／数值填充 + 内衬缝色变（FDB-DSP-014 现行规则，读感偏弱）；中——抛光件（凹槽唇、45° 斜边、翼板、分隔线，zone 6）也换稀有度金属，边框仍拉丝钢；宽——边框（zone 5）也换，需推翻 FDB-DSP-014「禁止大面积」。Standard 与 Signature 在钢底上区分弱，故加渲染 Signature 烧钛蓝备选（`--tier titanium`）。
- 柔光：contract `soft_focus.enabled_only_for_final_beauty=true`，属 Gate 08 最终 beauty 输出，不在 Gate 05 审阅图上启用。为便于决定，按 contract 参数用 Blender 5.2 compositor node group 实现（`--soft-focus`：object index 遮罩 crystal/mirror/spinner，亮度 smoothstep 0.9–1.8，高斯 5／20 px，混合 0.10／0.025，beauty 不直接模糊），输出 `beauty-clean` + `beauty-soft`；金档 hero 上仅 1.07% 像素变化 > 8/255。
- 证据：`evidence/05-blockout/rev-008/cmf-preview-{hero,front}-tier-{steel,copper,silver,gold}[-medium|-bold].png`、`cmf-preview-{hero,front}-tier-titanium-medium.png`、`cmf-preview-hero-tier-gold-{clean,soft}.png`、`cmf-preview-report-tier-*.json`。合成表：`Artifacts/TriSpinnerSlab/gate05-r008-variants/gate05-r008-variants-matrix-front.png`、`…-medium-tiers-hero.png`、`…-accent-tiers-hero.png`、`…-bold-compare-front.png`、`…-signature-silver-vs-titanium.png`、`gate05-r008-softfocus-ab-gold-hero.png`。静态材质变体，无动画，故只出静帧（未录转台），已明示。
- 登记：`register_tri_spinner_slab_v3_rev008_variants.py` → `pipeline.json` rev 114（32 个 study 资产，`studyOnly=true`），validations 增 `rarity-variation-study-attached`、`soft-focus-deferred-to-gate-08`。`validate-pipelines.mjs` premium-display-case `errors: []`。
- 设计圣经：新增 `FDB-DSP-059`（变体请求原话、档位映射、三口径、柔光结论，`DecisionState` 待选）。
- 待定：口径（窄／中／宽）、Signature 亮银或烧钛蓝、柔光留 Gate 08 或另议；Gate 03–05 rev-008 仍需逐 gate 明确批准原话。
- **15:4x 用户决定（选项原文）**：口径「宽：边框也换（推翻 FDB-DSP-014 禁止大面积）」；Signature「烧钛蓝（与 Standard 冷钢区分明显）」；柔光「留到 Gate 08 灯光定稿时再开，Gate 05–07 审阅图保持 clean」。已补渲染 titanium-bold 与 steel/copper bold hero，合成 `gate05-r008-variants-final-bold-{front,hero}.png`；`register_tri_spinner_slab_v3_rev008_variant_decisions.py` → manifest rev 115（10 资产，`blockoutSpec.rarityVariationStudy.decisionState=user-decided`，history `user-decision` 事件），validate `errors: []`。设计圣经 `FDB-DSP-059` 转 Locked，`FDB-DSP-014` 标注仅在 v3 slab 变体范围内被取代。稀有度材质映射（zone 5/6/7 + zone 2 缝色随档）待并入下一版 modeling contract（Gate 07 材质合约）；rev-008 几何与 contract 未改。视觉批准待确认，未推送手机。

## 2026-09-10 14:25 Premium Display Case · tri-spinner-slab-v3-cmf Gate 05 rev-007 被驳回 → 参考研究 → Gate 03–05 rev-008（manifest rev 113）

> **状态：用户 13:39 驳回 rev-007（边框长宽倒角不平行、三种圆角、翼板不对称、整体像一块铝板），要求先找参考、说明理解再动手。参考板 + 几何示意呈现后，用户三项决定：等宽等距优先 / 四角各一片翼板 / CMF 方案 A。contract rev-008 / architecture rev-030 / blockout rev-008 已登记 `ready_for_review`，Gate 01–02 不变，Gate 06–12 仍 `stale`。Blender 白模 + 指示性 Cycles CMF 预览，未进 Unity，无 shipping 视觉变化，视觉批准待确认，未推送手机。** 驳回原话与三项选择的原文标签写入 `history.ndjson`（event `6c6d91fe`，type `user-rejection`，含 `decisions`）与 Gate 05 `historicalDecisions`（rev 11 → `rejected`）；contract 以 `src.user_gate05_rev007_feedback_20260910` 与 `src.user_gate05_rev007_decisions_20260910` 引用。

- 问题量化（rev-007）：主舱同一圈边框三种宽度——侧 4.56 / 顶 6.86 / 对角 10.55 mm，因外框倒角 4.5 与 field 倒角 8.0 各自独立；圆角三种（外框 R1.5、刻线 R0.8、翼板 R1.0）；翼板左低右高。标注图 `Artifacts/TriSpinnerSlab/gate05-r008/gate05-r008-rev007-issue-annotated.png`。
- 参考：Pinterest 页面为纯 JS 无法抓取，改用 Wikimedia Commons 的 Royal Oak 15202 / 25721 实物照（CC BY-SA）+ AP Chronicles 文字（表圈"顶面拉丝、40° 斜边抛光、斜边全程等宽、外八角与内圈为同形等距偏移"），与用户 V3 概念图局部并排：`gate05-r008-reference-board.png`；现状 vs 提议示意：`gate05-r008-geometry-diagram.png`。三者已登记为 Gate 05 `review-research` 资产。
- 几何（决定 1「等宽等距」）：两块钢岛共用一个四角倒角 `interior.island_corner_chamfer_mm = 8.0`（header 与 main 相同，assertion `island-chamfers-equal`）；main field = 主 bezel 精确内偏移 4.56（不再有独立 field 倒角，`main.field_corner_chamfer_mm` 派生 5.33），刻线、翼板外缘继续精确偏移；实测四向边框 side/top/bottom/diagonal 全部 4.56 mm（check `frame-bands-uniform`）。退役 `main.field_top_chamfer_mm`、`main.field_bottom_chamfer_mm`、`header.plate_bottom_chamfer_mm`、`main.pocket_vertical_margin_split`；`main.field_top_y_mm` 改由 header 高度 + 缝 + shelf 派生（`visual.main_bay_start_from_top` 仅存档）。代价：参考图的宽顶条消失，多出的高度并入 field。
- 对称（决定 2「四角翼板」）：`GEO_PDC_MAIN_WING_{TL,TR,BL,BR}` 由 TL 一片关于凹槽中心 x/y 镜像生成（check `four-wings-mirrored` 逐顶点比对 ±0.02 mm）；外缘 = field 偏移 3.2，内缘 = 凹槽等距弧（2.2），两端 3.0 mm 平头，远端为水平切线 |y−cy| = 36.96（`main.wing_half_span_mm`，取上下最小值并停在 field 倒角区之下，故四片同形）。凹槽中心改为"翼板偏移顶边与数值板顶边的中点"派生（hub 0.620H，图读 0.637H，容差内）。金饰镜像：四条倒角金条（中线内缩 2.6，位于刻线与翼板之间，不再压在刻线上）、左右竖轨以 cy 为中心、左右两枚索引块；数值板居中。
- CMF（决定 3「方案 A」）：分区归属改动——翼板 → zone 6 镜面，数值板 → zone 4 钢琴黑；contract 新增 `cmf_scheme_a_zone_map` 与规则"凸起抛光、平面拉丝、凹陷喷砂，表面在几何边界相接"。预览脚本 SCHEME-A 覆盖（已在 report 标注为提案，不改 contract 材质值，Gate 07 定）：field 深色喷砂 `#5C6266` 粗糙 0.55、bezel 拉丝各向异性 0.8、镜面 `#C9D0D6` 粗糙 0.04、钢琴黑 coat 0.35。
- Gate 04 architecture rev-030：38 核心件 + 6 螺栓 socket + 3 TraitFill，`core_object_list_matches_contract=true`；Unity 路径 `MainCompartment/Wings/Wing{TL,TR,BL,BR}`、`MainCompartment/Gold/*`。
- Gate 05 blockout rev-008：38 项几何检查全 `pass`（新增 `frame-bands-uniform`、`island-chamfers-equal`、`four-wings-mirrored`、`gold-mirrored`、`cmf-scheme-a-zones`），每件 `non_manifold_edges=0`，评估三角 103,582（预算 120,000），clamped corners 0。contract SHA-256 `6219e6936624e1cce743eb63ef6248571edb90138007e15c35703c4913a041b6`。
- 证据：`evidence/05-blockout/rev-008/zone-model-*.png`（11 视角）+ `blockout-turntable.mp4`（144 帧）；`cmf-preview-{hero,front,low-oblique,corner-macro,pocket-rim-macro}.png` + `cmf-preview-report.json`（Cycles 96 spp，REVIEW-BRIGHT + SCHEME-A）。录像：`Artifacts/TriSpinnerSlab/gate05-r008/gate05-r008-cmf-preview-turntable-clear.mp4`（72 帧，h264 yuv420p 1280×852，抽帧 frame018／frame054）与 `gate05-r008-zone-model-turntable-clear.mp4`（144 帧，抽帧 frame030）。新时间戳 `/tmp` 帧目录、`ffmpeg -n`、`cp -n`，未删除、未覆盖、未 commit／push。无 SwiftUI／Unity shipping 变化，故无 Simulator 录屏。
- 登记：`register_tri_spinner_slab_v3_rev008.py` → `pipeline.json` rev 113、events `6c6d91fe`（user-rejection + decisions）、`fe2212c9`／`cd900431`／`f8af343e`（stage-revised 03/04/05）。`validate-pipelines.mjs` premium-display-case `errors: []`；`npm test` 282 项 241 通过 / 41 失败，失败集合与改动前逐项相同。
- 设计圣经：新增 `FDB-DSP-058`（驳回原话、三项决定原文、等距偏移规则、四翼镜像、CMF A 分区）；`FDB-DSP-057` 交付列更新；附录增 rev-007 驳回行。
- 待定：用户逐 gate 批准；仍开放：8.0 mm 岛倒角大小、外壳 101 mm 宽、井 Ø67.4／1.2 clearance、6 螺栓 + 3 卡扣、数值板版式、SCHEME-A 材质值（Gate 07）。

## 2026-09-10 12:50 Premium Display Case · tri-spinner-slab-v3-cmf Gate 05 rev-006「感觉差不多吧」→ Gate 03–05 rev-007（manifest rev 112）

> **状态：用户 12:22/12:23 认可 rev-006 方向（“感觉差不多吧”），提出三项修改：预览太黑、红圈处过渡生硬要倒圆角、底部横带要预留动态三条数值（对话 `d0029833-…`，即 `FDB-DSP-053` TRAIT PROFILE）。contract rev-007 / architecture rev-029 / blockout rev-007 已登记 `ready_for_review`，Gate 01–02 不变，Gate 06–12 仍 `stale`。Blender 白模 + 指示性 Cycles CMF 预览，未进 Unity，无 shipping 视觉变化，视觉批准待确认，未推送手机。** 两条原话逐字写入 `history.ndjson`（event `1ed8fa53`，type `user-revision-request`）与 Gate 05 `historicalDecisions`（rev 10 → `revise`，非 rejected）；contract 以 `src.user_gate05_rev006_feedback_fillets_20260910` 与 `src.user_gate05_rev006_feedback_trait_plaque_20260910` 引用。

- 圆角：`Outline` 的 chamfer 角新增 `fillet`，每个 45° 倒角与直边的接点做 R1.5 圆角（外层轮廓），嵌套内层保留 ≥ 0.8 mm（`interior.junction_fillet_min_mm`，是对精确等距偏移规则唯一放行的偏差，只作用于接点圆角，主圆角弧仍精确同心，32 处已记录）；每个角仍输出 seg+1 点（圆角–斜边–圆角按弧长重采样），嵌套轮廓继续 1:1 桥接。共 46 处接点圆角：header bezel 四角链（bezel→inner→mirror→graphite）、main bezel 顶角、field 四角链（field→mirror seam→surface→刻线内外）。翼板顶点用 `fillet_polygon` 圆角 R1.0。
- TRAIT PROFILE 板（替换底部拉丝带）：`GEO_PDC_MAIN_TRAIT_PLAQUE` 66.6 × 10 mm 抬高 0.6，环绕刻线；三条轨 41 × 1.2 mm、槽深 0.35（BOOLEAN EXACT），自上而下 SPIN / FEEL / CRAFT，左 14 mm 标签列、右 9 mm 数值列留给贴花；每轨 25/50/75% 四分刻度切口；`GEO_PDC_TRAIT_FILL_00–02` 为独立对象（`export_role=runtime-dynamic-fill`，zone 7 占位），预览按 `ToyTalentCatalog` metal-three-blade 88/36/86 取长，运行时由 trait block 按目录缩放，contract 不持有数值。为腾出空间凹槽上移：`main.pocket_vertical_margin_split` 0.30 → 0.22（hub 0.615H，图读 0.637H，warn 阈值内）。
- 提亮：`render_tri_spinner_slab_cmf_preview.py` 新增 REVIEW-BRIGHT（默认开，`--no-review-bright` 关）：中性灰环境 0.05、顶部 2.2× 对角线柔光板（相对功率 0.45）、p97 目标 0.80 → 0.86；stamp 标注 REVIEW-BRIGHT。仅为审阅辅助，contract beauty rig 未改，Gate 08 灯光另议。
- 修过一处：凹槽上移后右翼板内端的等距弧高于翼板顶边，多边形自交出现黑色细缝；改为按弧线到达（顶边 − 1.5 mm）处求 x（`arc_x_at`），左翼同理，重建后消失。
- Gate 03 contract rev-007：新增输入 `interior.junction_fillet_mm` 1.5、`interior.junction_fillet_min_mm` 0.8、`main.wing_corner_fillet_mm` 1.0、`trait.*`（plaque 10.0、pitch 3.0、track 1.2、depth 0.35、label 14、value 9、tick 0.3、fill inset 0.1、preview_values [88,36,86]）；新 assertion `room-below-pocket-for-trait-plaque`、`trait-rows-fit-plaque`、`trait-preview-budget`（=210）、`junction-fillet-fits-chamfer`，全部通过。外壳 `101.29 × 171.79 × 10.96 mm` 不变。contract SHA-256 `e5f1cf1fc2d103a6152ce15263f120ba856c0c42857622b54060bc8cbd964ed5`。
- Gate 04 architecture rev-029：32 核心件 + 6 螺栓 socket 子件 + 3 个 `TraitFill*`（owner `runtime-trait-block`，parent `TraitPlaque`），`core_object_list_matches_contract=true`。
- Gate 05 blockout rev-007：`blockout-validation.json` 33 项全 `pass`（新增 `chamfer-junctions-filleted`、`trait-plaque-three-tracks`、`trait-fills-preview-lengths`），每件 `non_manifold_edges=0`，评估三角 113,502（预算 120,000）。
- 证据：`evidence/05-blockout/rev-007/zone-model-*.png`（11 视角）+ `blockout-turntable.mp4`（144 帧）；`cmf-preview-{hero,front,low-oblique,corner-macro,pocket-rim-macro}.png` + `cmf-preview-report.json`（Cycles 96 spp，REVIEW-BRIGHT，p97 0.267→0.785→0.86）。录像：`Artifacts/TriSpinnerSlab/gate05-r007/gate05-r007-cmf-preview-turntable-clear.mp4`（72 帧，h264 yuv420p 1280×852，抽帧 frame018／frame054）与 `gate05-r007-zone-model-turntable-clear.mp4`（144 帧，抽帧 frame030）。全新时间戳 `/tmp` 帧目录、`ffmpeg -n`、`cp -n`，未删除、未覆盖、未 commit／push。无 SwiftUI／Unity shipping 变化，故无 Simulator 录屏。
- 登记：`register_tri_spinner_slab_v3_rev007.py` → `pipeline.json` rev 112、events `1ed8fa53`（user-revision-request）、`f51d97cf`／`56c37518`／`8d9ac50c`（stage-revised 03/04/05）。`validate-pipelines.mjs` premium-display-case `errors: []`；`npm test` 282 项 241 通过 / 41 失败，失败集合与改动前逐项相同。
- 设计圣经：新增 `FDB-DSP-057`（两条原话 + rev-007 方向，关联 `FDB-DSP-053`）；`FDB-DSP-056` 交付列更新；附录增 rev-006 superseded 行。
- 待定：用户逐 gate 批准；仍开放：外壳 101 mm 宽、Ø67.4 井／1.2 clearance、6 螺栓 + 3 卡扣、2.4 mm 缝、TRAIT 板版式（列宽、行距）。运行时 trait block 接线（把 Gate 12 rev-019 的 `PremiumDisplayCaseTraitBlock` 接到 `TraitFill*`）属 Gate 11/12，尚未做。

## 2026-09-10 11:45 Premium Display Case · tri-spinner-slab-v3-cmf Gate 05 rev-005 反馈 → Gate 03–05 rev-006（manifest rev 111）

> **状态：用户 11:15 反馈 rev-005 太扁平、层级台阶与笔触不足、蓝框银色横带参考图没有（两板断开）、承载区细节缺；contract rev-006 / architecture rev-028 / blockout rev-006 已登记 `ready_for_review`，Gate 01–02 不变，Gate 06–12 仍 `stale`。Blender 白模 + 指示性 Cycles CMF 预览，未进 Unity，无 shipping 视觉变化，视觉批准待确认，未推送手机。** 反馈原话逐字写入 `history.ndjson`（event `e04b20c5`，type `user-rejection`）与 Gate 05 `historicalDecisions`（rev 9 → `rejected`）；contract 以 `src.user_gate05_rev005_feedback_20260910` 引用。用户提到的彩色 arrow 标注未随图收到，本轮按参考原图裁切（接缝、左缘、凹槽唇、卡扣、底带、header 角）逐区对照。

- 反馈 → rev-006 对策：蓝框银色横带 → 删除 `GEO_PDC_HEADER_SILVER_DATUM_RAIL`，header 与 main 成两块独立钢岛，中间 2.4 mm 烟色缝 `GEO_PDC_COMPARTMENT_SEAM`（缝底 z=5.56），main bezel 顶条加宽为 6.6 mm 拉丝条；层级台阶 → 水晶框内侧台阶（0.9 宽 × 0.8 落差，单一流形 stepped ring，按边权重倒角：外唇 1.0×、台阶 0.25×、内缘 0.4×）、header bezel 四角 45° 倒角 4.5 mm、main bezel 顶角倒角；笔触／描边 → 3 条刻线均为几何（BOOLEAN EXACT 切入 field，0.4 宽 × 0.3 深）：field 外轮廓刻线（内缩 1.6）、底带环绕刻线、凹槽唇脚刻线；承载区 → 凸起抛光唇（宽 1.8、高 +0.6、外倒角 0.5、内斜面 0.6 宽 × 1.2 落差）→ 烟色井壁 → 石墨井底，唇上 3 个透明卡扣（4.0 × 3.2 × 2.4，90°/210°/330°，仅视觉，`retention.mechanism` 仍为 null）；拉丝翼板改为贴凹槽的斜切多边形（左下、右上，内缘按 2.2 mm 等距折线），金色 L 形（TL 斜条 + 左竖条）；header 石墨板加镜面分隔线。
- 层级（距背面 z，mm）：shelf 7.96 → 镜面斜边底 7.04 → field 6.36 → 刻线底 6.06 → 翼板／底带顶 6.96 → 唇顶 6.96 → 唇内斜面底 5.16 → 井底 2.70；卡扣顶 8.81；缝底 5.56；header 板 6.76；水晶框台阶 10.16 → 前面 10.96。
- Gate 03 contract rev-006：`main.pocket_diameter = well + 2×(wall 0.85 + slope 0.6 + lip 1.8)` = Ø73.9（井 Ø67.4 不变，clearance 1.2 不变），field 79.9，外壳 `101.29 × 171.79 × 10.96 mm`（rev-005 为 98.31 × 166.74；W/H 不变）。退役 `interior.datum_rail_lift_mm`、`main.pocket_rim_width_mm`。新 assertion：`header-chamfer-chain-never-clamps`、`seam-gap-inside-rail-band`、`frame-ledge-clears-counterbore`、`no-datum-rail`；全部通过。contract SHA-256 `cac2c7c2d66061a1924269e72e07a4285e68ee281bae32750d46f515e9041559`。
- Gate 04 architecture rev-028：32 核心件 + 6 螺栓 socket 子件，`core_object_list_matches_contract=true`；新增 Unity 路径 `CompartmentSeam`、`HeaderCompartment/HeaderDividerLine`、`MainCompartment/Pocket/PocketPolishedLip`、`PocketClip00–02`。
- Gate 05 blockout rev-006：builder 新增 `profile_ring`（多环截面、等顶点数桥接，用于台阶框与唇）、`register_cut`、`frame_edge_weights`、`rotated_rounded_rect`、`arc_points`；`blockout-validation.json` 30 项全 `pass`（新增 `no-datum-rail`、`header-bezel-four-chamfers`、`frame-ledge-step`、`pocket-lip-raised`、`three-clips`、`engraved-grooves-are-cuts`、`wings-clear-of-pocket`），每件 `non_manifold_edges=0`，clamped corners 0，评估三角 107,684（预算 120,000）。
- 证据：`evidence/05-blockout/rev-006/zone-model-*.png`（11 视角）+ `blockout-turntable.mp4`（144 帧）；`cmf-preview-{hero,front,low-oblique,corner-macro,pocket-rim-macro}.png` + `cmf-preview-report.json`（Cycles 96 spp，p97 校准 0.294→0.746→0.80）。录像：`Artifacts/TriSpinnerSlab/gate05-r006/gate05-r006-cmf-preview-turntable-clear.mp4`（72 帧，h264 yuv420p 1280×852，抽帧 frame018／frame054）与 `gate05-r006-zone-model-turntable-clear.mp4`（144 帧，抽帧 frame030）。按用户要求：全新 `/tmp` 帧目录（带时间戳）、`ffmpeg -n`、`cp -n`，未删除任何临时帧，未 commit／push。无 SwiftUI／Unity shipping 变化，故无 Simulator 录屏。
- 登记：`register_tri_spinner_slab_v3_rev006.py` → `pipeline.json` rev 111、events `e04b20c5`（user-rejection）、`d7fc95a1`／`146e563f`／`f1c98ab8`（stage-revised 03/04/05）。`validate-pipelines.mjs` premium-display-case `errors: []`；`npm test` 282 项 241 通过 / 41 失败，失败集合与登记前逐项相同（magnetic-slide 历史断言）。
- 设计圣经：新增 `FDB-DSP-056`（反馈原话 + rev-006 方向）与决策附录驳回行；`FDB-DSP-055` 交付列更新。
- 待定：用户逐 gate 批准；仍开放的决定：外壳 101 mm 宽、Ø67.4 井／1.2 clearance、6 螺栓 + 3 卡扣布局、2.4 mm 缝。若用户原本的 arrow 标注指向别处，需要重新发图。

## 2026-09-10 10:55 Premium Display Case · tri-spinner-slab-v3-cmf Gate 05 rev-004 被驳回 → Gate 03–05 rev-005（manifest rev 110）

> **状态：用户 10:01 驳回 Gate 05 rev-004；contract rev-005 / architecture rev-027 / blockout rev-005 已登记 `ready_for_review`，Gate 01–02 不变，Gate 06–12 仍 `stale`。Blender 白模 + 指示性 Cycles CMF 预览，未进 Unity，无 shipping 视觉变化，视觉批准待确认，未推送手机。** 驳回原话已逐字写入 `history.ndjson`（event `18d13c84`，type `user-rejection`）与 Gate 05 `historicalDecisions`（rev 8 → `rejected`），contract 以 `src.user_gate05_rev004_rejection_20260910` 引用。

- 驳回要点 → rev-005 对策：雕刻深度太浅 → header 凹 1.2 / 主舱凹 1.6 / 部件抬 0.6 / 镜面斜边 0.9 / 外框倒角 1.0 mm，全部为几何；看不到材质分区 → Workbench 按 `cmf_zone_id` 着色 + Cycles CMF 预览；三角凹槽不通用 → 圆形井 Ø71.5 mm（井 Ø67.4 = 65 mm 叶尖圆 + 2×1.2 clearance，外加 0.85 壁 + 1.2 镜面 rim），井深 3.66 mm，任何陀螺都能放；厚度／倒角／打孔丢失 → 6 颗沉头螺栓（头 Ø2.6、沉孔 Ø3.0×1.0、六角 socket）落在水晶带中线；圆角非同心 → `Outline.inset` 等距内偏移，`case.outer_corner_radius = band + inner_r` 派生，`blockout-validation.json` 9 组嵌套轮廓 `concentric=true`。
- Gate 03 contract rev-005：`resolve_contract.py` 增加 `nested_offset_rule`、`bolt_construction`、通用凹槽输入（`content.design_toy_diameter_mm`、`content.fit_clearance_mm`、`main.pocket_*`）、硬件输入（`hardware.*`）、`interior.bezel_corner_radius_mm=6.0`；退役 `GEO_PDC_MAIN_CORNER_FACETS`，新增 `GEO_PDC_POCKET_{MIRROR_RIM,SMOKE_WALL,GRAPHITE_FLOOR}`、`GEO_PDC_MAIN_GOLD_CHAMFER_TL`、`GEO_PDC_FRAME_BOLT_00–05`。解析值：case `98.31 × 166.74 × 10.96 mm`、envelope 深 17.05、前突 6.09。contract SHA-256 `15a1c25922c6691e4e930db340121f5f01580f0623a3042a1edda3c057bd20e6`。全部 assertion 通过。
- Gate 04 architecture rev-027：`generate_architecture.py` 读 rev-005 contract + rev-005 hierarchy；zone id 直接取 builder 写入的自定义属性，不再维护第二张表；28 核心件 + 6 个 `*_SOCKET_FLOOR` 子件（`parent_part`），`core_object_list_matches_contract=true`；exploded 仍 internal-only。
- Gate 05 blockout rev-005：`tools/blender/build_tri_spinner_slab.py`（快照 `build_tri_spinner_slab.r005.py`）重写：`Outline` dataclass（圆角／倒角，`inset` 保同心）、`sloped_ring`、`prism`、按精确顶点角度采样的 `radial_pair`；螺栓沉孔用 BOOLEAN EXACT 先切再倒角。修过一处流形失败：角部螺栓与被夹到 0.4 mm 的水晶框角冲突 → 外角半径改派生、bezel 半径独立、螺栓移到带中线 45° 弧点后 `non_manifold_edges=0`。`blockout-validation.json` 22 项全 `pass`（含 `pocket-is-generic-circle`、`nested-outlines-concentric`、`six-bolts`、`relief-is-geometry`）；评估三角 99,824。
- CMF 预览（补充证据，非 Gate 07 lookdev）：`tools/blender/render_tri_spinner_slab_cmf_preview.py`（快照 `.r005.py`）按 contract 7 区材质 + beauty rig，Cycles Metal 96 spp。曝光校准两次迭代失败后定案：先按 `relative_power × 面积` 设功率，再以低分辨率 hero 帧物体像素第 97 百分位显示亮度 = 0.80 统一缩放（两轮，p97 0.294→0.759）；均值／中位数法被高光带偏，`P = L·π·A` 常数与 Blender 面光单位不符（暗 ~50×）。灯位以物体中心为锚、相机局部轴偏移，rim 才落在边缘。
- 证据：`evidence/05-blockout/rev-005/zone-model-{front,back,top,left,hero,left-oblique,right-oblique,low-oblique,corner-macro,pocket-rim-macro,side-thickness-macro}.png` + `blockout-turntable.mp4`（Workbench 分区色，1440×960，144 帧）；`cmf-preview-{hero,front,low-oblique,corner-macro,pocket-rim-macro}.png` + `cmf-preview-report.json`。录像：`Artifacts/TriSpinnerSlab/gate05-r005/gate05-r005-cmf-preview-turntable-clear.mp4`（h264 yuv420p 1280×852，72 帧，抽帧 frame018／frame054）与 `gate05-r005-zone-model-turntable-clear.mp4`（144 帧，抽帧 frame030）；静帧副本同目录。本轮无 SwiftUI／Unity shipping 变化，故无 Simulator 录屏。
- 登记：`tools/model-provenance-explorer/register_tri_spinner_slab_v3_rev005.py` → `pipeline.json` rev 110、events `18d13c84`（user-rejection）、`4bccc040`／`3b9b6880`／`af267d91`（stage-revised 03/04/05）。`node validate-pipelines.mjs`：premium-display-case `errors: []`，唯一 missing 为已知丢失基线 PNG。`npm test` 278 项 237 通过 / 41 失败，失败集合与登记前逐项相同（均为 magnetic-slide 历史 gate 断言，与本次改动无关）。
- 设计圣经：`FDB-DSP-054` 交付列更新；新增 `FDB-DSP-055`（驳回原话 + rev-005 方向）与决策附录驳回行。
- 待定：用户逐 gate 批准 01–05（重点：外壳放大到 98 mm 宽是否接受、Ø71.5 圆井与 1.2 mm clearance、6 颗螺栓布局）；Gate 06 起才进入细几何与正式 lookdev。已知限制：header 镜面／石墨底部 45° 倒角被夹到 0.05 mm（4 角已记录）；金色可见面积 0.274%，spec 5–8% 目标与 0.25–0.35 mm inlay 仍冲突。

## 2026-09-10 09:50 Premium Display Case · tri-spinner-slab-v3-cmf 重建 Gate 01–05（Blender 白模，manifest rev 109）

> **状态：Gate 01–05 已登记为 `ready_for_review`，Gate 06–12 标记 `stale`；Blender 只到白模，未进 Unity，无 shipping 视觉变化，未推送手机。** 用户 08:37 指定两份源文件：`tri-spinner-slab-model-spec.v0.json` 与 `tri-spinner-slab-agent-handoff-spec.md`（知识库 `40-视觉资产/tri-spinner-slab-concept-v3-cmf/`）。按 handoff 要求从 Gate 01 重开，`bpy` 确定性 builder 读取解析后的 contract 生成几何。每个 gate 仍需用户逐一批准。

- Gate 01 intake rev-004：V3 正面净图（1000×1573）、用户聊天图（650×1024）、三视图、spec JSON、handoff MD 及 `UnifiedTriSpinner.glb` 登记为源；历史基线 `collector-slab-six-products-approved.png` 文件已丢失，保留为 issue `pdc-lost-baseline-collector-slab-six-products`（asset `display-case-approved-shipping-baseline`），不再作为当前视觉依据。
- Gate 02 analysis rev-007：`measure_spinner_source.py` 在 Blender 内实测 `UnifiedTriSpinner.glb`（叶尖圆 65.0 mm、厚 8.20 mm→spec 用 `spinner.max_thickness_mm`）；`measure_v3_proportions.py` 用亮度行程 + 按图高缩放的 run-length 检测 header 底轨／暗缝／银 datum 轨／主舱起点，两张图 header 缝一致（0.313 H）。结论：图上陀螺中心 0.637 H 与真实 65 mm 叶尖圆不兼容（会顶进 header 轨），故 `spinner.center_y_mm` 改为派生值，原图读数保留为 `visual.spinner_center_from_top_image_reading`。
- Gate 03 contract rev-004：`resolve_contract.py` 合并 spec、实测与图像比例，公式按类型化 AST 求值，全部 assertion 通过。解析值：case `74.23 × 125.90 × 10.96 mm`（含陀螺 envelope 深 17.05）、header 高 39.65、frame band 3.86、外角 R2.97、陀螺中心 `y=-28.0 mm`、前突 6.09 mm。所有尺寸标 `PROVISIONAL_DIMENSIONS`，非 `measured`。contract SHA-256 `916e863c0e8559189898f8c4597603756f646f56822ab6e57d1a9138779fe39b`。
- Gate 04 architecture rev-026：`generate_architecture.py` 输出 `part-tree.json`／`exploded-plan.json`／`architecture-board.png`；Unity 路径 `PresentationRoot/CaseAssembly/...`，陀螺为 caller-owned `contentSlot` 内容，不属本任务。exploded 仅内部证据，不进 review。
- Gate 05 blockout rev-004：`tools/blender/build_tri_spinner_slab.py`（快照 `build_tri_spinner_slab.r004.py`）生成 `tri-spinner-slab-blockout-r004.blend`；`blockout-validation.json` 全部 `pass`（尺寸／深度／居中／流形，每件 `non_manifold_edges=0`）。修过三处：glTF 导入陀螺 Y-up→Z-up 与 90° X 旋转要用矩阵复合而非覆盖 euler；平板改角度阈值平滑（`set_sharp_from_angle`）去掉波纹渐变；矩形→三叶 pocket 桥接改按极角配对（`radial_pair`），消除陀螺旁的暗色扭面。
- 证据：`ArtSource/ModelPipeline/premium-display-case/evidence/05-blockout/rev-004/white-model-{front,back,top,left,hero,left-oblique,right-oblique,low-oblique,side-thickness-macro}.png` + `blockout-turntable.mp4`（Workbench，1440×960，24 fps，144 帧 / 2.5°）。录像副本 `Artifacts/TriSpinnerSlab/gate05-r004/gate05-r004-blockout-turntable-clear.mp4`（h264 yuv420p，抽帧 frame030／frame090，hero 静帧同目录）。本轮不涉及 SwiftUI／Unity shipping 场景，故无 Simulator 录屏。
- 登记：`tools/model-provenance-explorer/register_tri_spinner_slab_v3_gates01_05.py` 写入 `pipeline.json`（rev 109）与 `history.ndjson`（events `07502540`… user-request、`1438c25b`／`7b715b49`／`4e6ae98f`／`3771f157`／`3d31fffc` stage-revised 01–05、`5e1e31fd`… `22b2a7fe` stage-stale 06–12）。`node validate-pipelines.mjs` 无 error；唯一 warning 为已知丢失的基线 PNG。
- 待定：用户逐 gate 批准 01–05；Gate 06 起才进入细几何与 Cycles 材质；Unity 场景／shipping factory 未改，`FDB-DSP-*` 现行要求不变。

## 2026-09-10 07:30 Premium Display Case Gate 12 R008（PSA 对照 lookdev：透明亚克力 + 闪粉底 + 边缘色散，rev-021）

> **状态：候选已构建、Gate12 定向 EditMode 41/41 通过、真实 lookdev 场景标准视角 + 300 帧转台录像已生成；视觉批准待确认，未推送手机。** R008 叠在 R006-A（黑绒）上，只改壳层与背板 lookdev。shipping factory 仍指向 R004。原任务 `dc778beb-9b98-45a0-8e27-817283f019b0` 在拉远相机后被中断；本轮完成 1.22 m 构图、转台编码与测试/文档收尾。

- 新增 shader `FidgetingApp/Gate12R008ClearAcrylic`（几何法线来自 `ddx/ddy`，避免导入壳网格的平滑顶点法线把整面刷成色散）与 `FidgetingApp/Gate12R008GlitterHolo`（银闪粉 + 跨面彩虹渐变，避免整面随视角变粉）。
- `PremiumDisplayCaseGate12R008Builder`：prefab `Assets/Resources/Gacha/PremiumDisplayCaseGate12R008/PresentationRoot.prefab`，场景 `Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R008.unity`。前/后壳透明亚克力、侧壁裙封闭 R004 双壳空隙、标签井与陀螺背板换闪粉、HDR + Bloom + ACES、单盏暖主光 + 冷补光。相机 `z = -1.22 m`、FOV 20°、1080×1440，留黑边给光晕。
- 证据：`ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/rev-021/{hero,top,left-oblique,right-oblique,low,front,glitter-backing-macro,edge-dispersion-macro,turntable-yaw-000/025/090/200/335}.png`。转台录像 `Artifacts/DisplayCaseSlabMaterials/gate12-r008/gate12-r008-reference-match-turntable-clear.mp4`（1080×1440，30 fps，300 帧 / 10 s，抽帧 frame-021 / 075 / 279）。对照条 `gate12-r008-reference-vs-r008.png`。history 事件 `ee6e9d2a-8871-46ce-b052-d32f6c6b6c06`（stageRevision 14 / evidenceRevision 21）。
- 测试：`Assets/Tests/Editor/PremiumDisplayCaseGate12R008Tests.cs`（闪粉/亚克力接线、裙边 Back cull、无 explode、factory 仍 R004、相机 z −1.22）。`R008 + R007 + R006 + R005 + Gate12Tests` 41/41 通过（`Logs/Gate12R008Tests.xml`）。
- 已知与待定：factory 未切 R008；未装机。用户批准后再切 factory、更新 design bible、Simulator / iPhone。

## 2026-09-09 23:15 Premium Display Case Gate 12 R007 A/B（等级标签改为喷砂金箔压铸徽章，rev-020）

> **状态：两版候选已构建、Gate12 定向 EditMode 39/39 通过、真实 shipping 场景标准视角 + 材质转台录像已生成；视觉批准待确认，未推送手机。** R007 是 R006-A（黑绒）的 prefab variant；shipping factory 仍指向 R004。用户 21:58 给出一张喷砂金属徽章照片（磨砂金底 + 抛光浮雕字 + 底部暗槽），要求右侧等级标签（emblem + `HEIRLOOM`）做出「金箔纸」质感。

- 新增 shader `FidgetingApp/Gate12R007SandblastFoil`（`Assets/_DisplayCase/Shaders/PremiumDisplayCaseGate12R007SandblastFoil.shader`）：alpha 遮罩即浮雕。用屏幕导数解出「沿世界 R/U 方向走 `_BevelWidth` 米」的 uv 步长，对遮罩取 ±步长梯度当作斜面法线（与 quad、字库图集、emblem PNG 的朝向/翻转无关）；斜面区抛光（`pow 160` 高光、去颗粒），面内 `_FaceGloss` 可切换抛光/喷砂；喷砂颗粒来自程序生成的可平铺 tilt+speckle 贴图（`Gate12R007SandblastGrain.png` 512²，30 tiles/m ≈ 0.07 mm/texel，按表面坐标采样、随机器旋转且靠 mipmap 抗闪）；`_FoilColor` 派生顶部香槟浅金→底部深琥珀渐变（object-space Y）；浮雕外 1–2 个斜面宽度内画暗槽（`_RecessReach`）。透明队列、`Cull Off`、无法线的 TextMesh 网格回退为 -Z 法线并按视线翻面。
- 新增 `PremiumDisplayCaseGate12R007Builder.cs`：菜单 `Gate 12/R007 Build Candidates (A plaque, B relief)`、`R007 Capture Standard Views`、`R007 Capture Turntable Frames`，batch 入口 `CaptureAll`。A：`Assets/Resources/Gacha/PremiumDisplayCaseGate12R007/PresentationRoot.prefab` + `Scenes/PremiumDisplayCaseGate12R007.unity`，在标签右块加 `RarityBadgePlaque` 40×40 mm、R4 mm 圆角喷砂金牌（遮罩 `Gate12R007PlaqueMask.png`，0.5 mm 暗槽边距，前浮 0.06 mm）；B：`…Gate12R007Relief/…` + `…R007Relief.unity`，不加金牌，浮雕直接压在镭射板上。两版共有：`RarityEmblem` 改 22 mm、z −6 mm、材质 `Gate12R007BadgeEmblem`（抛光面、斜面 0.32 mm、暗槽 0.9）；`AuthoritativeRarityLevel` 字号 0.0000085→0.0000105、z +14 mm、材质 `Gate12R007BadgeTier`（斜面 0.12 mm、`_RecessReach 1`，避免采样跨过字库图集 1 texel padding 出现方形鬼影——rev-020 首轮出现过，已修）；金牌 + 等级词加入 plate foil 集，随 tier 变色（A 8 个 / B 7 个 foil 渲染器）。
- `PremiumDisplayCaseLabelPlate` 运行时新增：`TierWordUsesFoil`（等级词渲染器在 foil 集内时成立）、`ApplyTier` 末尾把 `tierLabel.font.material.mainTexture` 以 `_MainTex` 写入等级词的 MaterialPropertyBlock（动态字库图集是运行时贴图，不能序列化进材质），`OnEnable/OnDisable` 订阅 `Font.textureRebuilt` 重推；`TierWordAtlas` 供测试/报告读取。R004/R005/R006 的等级词仍用字体材质，不在 foil 集内，行为不变。
- 证据（真实 shipping 场景，Unity 6000.5.6f1 batchmode）：`ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/rev-020/{a-plaque,b-relief}/{hero,top,left-oblique,right-oblique,low,front,label-macro,badge-macro,badge-macro-low}.png` + `shipping-capture-report.json`（`plateTier Gold`、`tierWordAtlasBound true`）；可读对比 `Artifacts/DisplayCaseSlabMaterials/gate12-r007/gate12-r007-badge-vs-reference.png`（参考照片｜A｜B）、`gate12-r007-badge-low-angle.png`、`gate12-r007-label-context.png`；材质转台录像 `gate12-r007-{a-plaque,b-relief}-turntable-clear.mp4`（1400×1000，30 fps，120 帧，相机 ±26° yaw 同步喂 R053 倾斜驱动；frame030/090 已抽帧）。history.ndjson 追加 `stage-ready-for-review` 事件 `39d864e4-3e8b-4ac8-9d34-574dc2672b5c`（stageRevision 13 / evidenceRevision 20；rev-018 为 R007 首轮粗颗粒调参，作历史保留）。
- 测试：新增 `Assets/Tests/Editor/PremiumDisplayCaseGate12R007Tests.cs`（两版浮雕材质/贴图/斜面参数/版面、只有 A 有金牌且尺寸与渲染队列正确、plate 接线与 foil 计数、HEIRLOOM 时三处 `_FoilColor` 同为金且等级词绑定实时字库图集、SIGNATURE 切银、R004/R005/R006 未被触碰）。`R007 + R006 + R005 + Gate12Tests` 39/39 通过（`Logs/Gate12R007Tests.xml`）。
- 已知与待定：喷砂颗粒只在法线/亮度层近似，无位移；固定虚拟主光，无反射探针；未录 iOS Simulator 视频，因 shipping factory 未切到 R007（材质门用 Unity 真实渲染转台代替）。用户批准 A 或 B 后再做：factory 切换、design bible `FDB-GAC-*` 更新、Simulator 录屏、iPhone 安装。

## 2026-09-09 22:40 Collector Slab 证书纸 TRAIT PROFILE（三条 0–100 天赋条，rev-019）

> **状态：候选已构建、定向 EditMode 43/44 通过、真实 shipping 场景预览已生成；视觉批准待确认，未推送手机。** 只改 R006 变体 B（证书纸）；变体 A 与 shipping factory（仍指向 R004）不变。用户 22:00 提出「3 个小横条，就从 0 到 100……根据不同的陀螺的倾向会有不同的天赋点的区别」，并在同一轮明确选定三轴、版面位置与固定预算。

- 数据权威：新增 `Assets/Scripts/Product/ToyTalentCatalog.cs`（`FidgetingApp.Product`）。三轴 `SPIN / FEEL / CRAFT`，每款固定 `210 / 300`。首发 `metal-three-blade 88/36/86`、`graphite-two-lobe 84/60/66`、`magnetic-slide-tile 24/96/90`、`magnetic-fan-card 46/88/76`；退役两款仅供旧存档迁移。`ResolveFromContentReference` 从 `GachaPrizeDefinition.ContentReference`（`toy/…`）解析，印在卡上的属性与实际封入的玩具无法脱钩。
- 渲染：新增 `Assets/_DisplayCase/Runtime/PremiumDisplayCaseTraitBlock.cs`。三行按 100% 宽度 authored，组件按数值缩短 fill 并写数字，一套版面服务所有玩具。`PremiumDisplayCaseGate12R006Builder.BuildTraitBlock` 生成 `TRAIT PROFILE` / `210 / 300` 表头、分隔细线、每行「轴名 + 压痕灰空槽 + 四分位刻度 + tier foil 已填段 + 数字」。已填段加入标签 plate 的 foil 集合（纸卡变体 foil renderer 由 6 增至 9），随 rarity 变色。
- 取代内容：原 `Body1/Body2/Fine1/Fine2` 四行不可读小字删除；`CONGRATULATIONS!` 黑带从 y `-0.064` 上移到 `-0.060`、高度 `0.012→0.010` 让出版面。
- 证据：`evidence/12-shipping/rev-019/{a-flocking,b-paper}/`，新增视角 `trait-macro.png`（1640×1200，整块属性区含轴名与数字）。history event `891831b5-ce57-4683-ae29-621581168060`（manifestRevision 110 / stageRevision 12 / evidenceRevision 19；109 与 11 留给同期并行的 R007 badge 轮次）。
- 测试：新增 `ToyTalentCatalogTests`（固定预算不变式、无重复 build、退役存档可解析、从 prize contentReference 解析、rarity 无法买到数值优势）与 `PremiumDisplayCaseGate12R006Tests` 两条新断言（条长与印刷数字一致、整块落在黑带与底部 keyline 之间且不越过侧边 keyline）。`ToyTalentCatalog + R006 + R005 + R007 + Gate12Tests` 43 通过 / 1 失败（`Logs/TraitProfileEditModeTests.xml`）。唯一失败为并行 R007 轮次自带的 `HeirloomBindsGoldFoilAndFontAtlasToTheTierWord` 颜色相等断言（期望值与实际值打印完全一致，属该轮浮点精度问题），与本轮改动无关。
- **未做**：runtime 尚未按当前封入玩具动态写入属性——预览在构建期用 `canyon-heir-metal-three-blade` 的 contentReference 解析并 `Apply`。逐 draw／逐玩具的运行时接线、Swift 侧展示与真机验收都还没有。

## 2026-09-09 21:55 Premium Display Case Gate 12 R006 A/B（PSA 实物细节 + 底板黑绒 vs 证书纸）

> **状态：两版候选已构建、EditMode 33/33 通过、真实 shipping 场景预览已生成；视觉批准待确认，未推送手机。** R006 是 R005 的 prefab variant；shipping factory 仍指向 R004。用户 21:41 “按照你的理解，把这个 slab 细节丰富一下”，依据两张 PSA 正/背面参考的分析。

- 新增 `PremiumDisplayCaseGate12R006Builder.cs`：菜单 `Gate 12/R006 Build Candidates (A flocking, B paper)` 与 `R006 Capture Standard Views`。A：`Assets/Resources/Gacha/PremiumDisplayCaseGate12R006/PresentationRoot.prefab` + `Scenes/PremiumDisplayCaseGate12R006.unity`；B：`…Gate12R006Paper/…` + `…R006Paper.unity`。材质/贴图在 `Generated/Gate12R006/`。
- 共有细节（世界坐标，基于 R004 几何）：`LabelWellFloor` 200×70 mm 浅磨砂井底（z −0.0166，`_Frost 0.62 / _Opacity 0.42`）；`BridgeBar` 204×9×15 mm 磨砂横梁（y 0.0665，盖住标签井与内腔接缝）；`RimEdgeHighlight` 0.7 mm 外亮边 + `WeldSeam` 0.4 mm 焊缝线（内缩 4 mm，Sprite-Unlit 顶点色环）；`ChamberGap` 3 mm 深色缝隙环（插件边外 1.5 mm）+ `ChamberWellShadow` 7 mm 内阴影渐变环；`CornerMark` 右下角蚀刻 `FIDGETING · SLAB`（Oxanium 1.7 mm，alpha 0.42）；标签顶部 1.4 mm tier 色 keyline，经 `PremiumDisplayCaseLabelPlate.AddFoilRenderer` 随 tier 变色（foil 渲染器 6 个）。
- B 变体 `CertificateCard`：184×204 mm 米白证书卡贴在黑绒上（比插件小 3 mm 露黑缝），URP Lit + 程序纸纹（颤动颗粒 + 纤维 + 斑驳，sRGB），墨色 keyline 框、顶部 `SERIES 01`（金墨）/ `LAUNCH`、发丝线、`FIDGETING COLLECTIBLE / SEALED DISPLAY CASE`、通栏黑带 `CONGRATULATIONS!`、两行正文、两行小字；印刷内容全部为静态系列文案，不含 collectible id（R053）。`ToyContactShadow` 130 mm 径向接触阴影（alpha 0.62）。文字 fontSize 128 + 半 characterSize 提升小字锐度。
- 证据：`evidence/12-shipping/rev-017/{a-flocking,b-paper}/{hero,top,left-oblique,right-oblique,low,front,label-macro,bridge-macro,lower-chamber-macro,corner-macro}.png`；对比图 `Artifacts/DisplayCaseSlabMaterials/gate12-r006/gate12-r006-ab-hero-front.png`、`gate12-r006-detail-macros.png`。
- 测试：新增 `PremiumDisplayCaseGate12R006Tests`（两版共有细节齐全、只有 B 有卡、无 explode 控件、keyline 入 foil 集、角标位置/alpha、B 卡尺寸/贴面/无 id、R004 不含任何 R006 细节）。`R006 + R005 + Gate12Tests` 33/33 通过（`Logs/Gate12R006Tests.xml`）。
- 待定：A 的缝隙/内阴影环在黑绒上几乎不可见（预期）；B 的纸在前壳雾化下偏灰米，若选 B 需再提亮或降前壳 `_Frost`；Pinterest 参考（PSA 转台渲染）提示第三方向 C：闪粉镭射背板 + 壳边色散 + bloom，尚未做。

## 2026-09-09 21:30 Premium Display Case Gate 12 R005 候选（磨砂壳 + 镭射石墨标签 + tier 箔 + 压印）

> **状态：候选已构建、EditMode 30/30 通过、真实 shipping 场景预览与转台录像已生成；视觉批准待确认，未推送手机。** shipping factory 仍指向已批准的 R004 prefab；R005 是 R004 的 prefab variant，不改 R004 资产。用户 2026-09-09 20:5x 的要求：整体加磨砂、底部字母雕刻、边框描边拉层次、标签金属感和镭射感拉满、文字精简换英文左对齐、右侧 pack icon + tier 小字、金/银/铜箔随 tier 变化。追加参考：PSA 评级 slab（左三行 / 右评级块 / 内腔框线）。

- 新增 `Assets/_DisplayCase/Editor/PremiumDisplayCaseGate12R005Builder.cs`：菜单 `Fidgeting/Display Case/Gate 12/R005 Build Candidate | Capture Standard Views | Capture Turntable Frames`。输出 prefab `Assets/Resources/Gacha/PremiumDisplayCaseGate12R005/PresentationRoot.prefab`、场景 `Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R005.unity`、材质 `Assets/_DisplayCase/Generated/Gate12R005/`。
- 新增 shader `Gate12R005MeshClippedFrosted`（R004 frosted + `_Frost/_FrostColor/_FrostGrain` 珠光喷砂扩散）与 `Gate12R005FoilLabel`（Kajiya-Kay 拉丝高光 + 视角依赖衍射彩带 + 可选 guilloche 印花 + `_FoilColor` 箔色 + emblem alpha clip）。`_SheenPhase` 保留，R053 的 `PremiumDisplayCaseLabelFoil` 倾斜驱动继续作用于 R005 标签。
- 新增运行时组件 `PremiumDisplayCaseLabelPlate`（挂在 `PhysicalLabel`）：`ResolveTier` 固定映射 HEIRLOOM→Gold、SIGNATURE→Silver、REFINED→Copper、其余→Steel；`Apply` 在 `SetLabel` 之后把左列每行宽度收进 116 mm、tier 词收进 38 mm，超宽按比例缩字号且不粘滞；箔色和 emblem 通过 MaterialPropertyBlock 写入框线、分隔线、emblem，tier 词墨色同步为箔色；`appliedTier` 序列化以在场景重载后恢复。`PremiumDisplayCaseShippingPresentation.SetLabel` 末尾新增可选转发（R004 无此组件则跳过）。
- 标签版式（184×58 mm 板）：左列 `GEEONE TRI-SPINNER`（Bold 0.000019）/ `SATIN STEEL · DRAGON SCALE` / `ACQUIRED 2026-09-09`，x = −84 mm；x = +40 mm 分隔线；右块 26 mm pack emblem（`Assets/Plugins/iOS/GachaPacks/*-emblem.png`，按 tier 选 standard/refined/signature/grail）+ `HEIRLOOM` 居中；3.5 mm 内缩直角箔框 0.7 mm。collectible id 继续不上板（R053）。
- 壳体：前壳 `_Frost 0.035`（保住陀螺清晰），后壳 `0.22`，周边管 `0.55`；新增 `ChamberBezel` 圆角环（插件边内缩 2 mm、前浮 0.8 mm、线宽 1.2 mm、`_Frost 0.62`）；底边管中心 `y −0.147` 加 `F I D G E T I N G` 压印（亮面 + 暗偏移阴影两层 TextMesh，5 mm 字高，sortingOrder 48/50）。
- 证据（真实 shipping 场景，Unity 6000.5.6f1 batchmode）：`ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/rev-016/{hero,top,left-oblique,right-oblique,low,front,label-macro,label-macro-left,brand-mark-macro}.png` + `shipping-capture-report.json`（`plateTier: Gold`）；可读合成 `Artifacts/DisplayCaseSlabMaterials/gate12-r005/gate12-r005-standard-views-sheet.png`、`gate12-r005-label-and-brand-mark-readable.png`；材质转台录像 `Artifacts/DisplayCaseSlabMaterials/gate12-r005/gate12-r005-holo-turntable-clear.mp4`（120 帧 30 fps，相机 ±26° 摆动并同步喂 R053 倾斜驱动，frame030/090 已抽帧）。history.ndjson 已追加 `stage-ready-for-review` 事件 `8cb8a008-b498-46a4-89e3-869fa66f1799`（stageRevision 9 / evidenceRevision 16，rev-009…015 属并行 gacha reveal v2 任务，未触碰）。
- 测试：新增 `Assets/Tests/Editor/PremiumDisplayCaseGate12R005Tests.cs`（tier 映射 8 例、shipping factory 仍指向 R004 且 R004 无 plate 组件、R005 prefab 接线/无 explode 控件/`_SheenPhase` 可达/emblem alpha clip/压印位于底管范围、长名缩字并恢复、HEIRLOOM 金墨与 emblem 贴图）。`PremiumDisplayCaseGate12R005Tests + PremiumDisplayCaseGate12Tests` 30/30 通过（`Logs/Gate12R005Tests.xml`）。
- 已知与待定：`Gate12R005FoilLabel` 使用固定虚拟主光，无反射探针；tube 表面仍带 R004 既有网格纹；本轮未录 iOS Simulator 视频，因 shipping factory 未切到 R005，Simulator 仍显示 R004（材质门用 Unity 真实渲染转台代替，符合“材质/灯光门可用 real render turntable”）。用户批准后再做：factory 切换 R005、design bible `FDB-GAC-*` 更新、Simulator 录屏、iPhone 安装。

## 2026-09-09 收藏 Slab 标签与背板材质候选 r001（只读预览，不改 shipping 材质）

> **状态：Editor 捕获工具 + 六套真实 shipping 场景预览已完成；视觉批准待确认，未推送手机。** 本轮不改任何 shipping 材质、prefab、场景或 Swift，只新增一个只读 Editor 捕获器。变化是静态外观对比，非动画，因此以静帧而非录屏作为证据。

用户指令：先用「Material consistency」skill 的写法产出 slab 标签与承载陀螺背板的质感选项概念图，随后要求“都做个预览图我看看”，即六套都要真实 Gate 12 R004 场景预览而不是概念渲染。

### 已完成

- **只读捕获器**：`Assets/_DisplayCase/Editor/SlabLabelBackplatePreviewCapture.cs`，`-executeMethod FidgetingApp.DisplayCase.Editor.SlabLabelBackplatePreviewCapture.CaptureAll`。打开已批准的 `PremiumDisplayCaseGate12R004.unity`，只在内存里替换 `PhysicalLabel` 与 `TactileBackgroundInsert` 的材质实例与 `TextMesh` 墨色，每套候选前重开场景防串味。**不调用 `PremiumDisplayCaseGate12Builder`、不保存场景、不写 `.mat`**，因此不会像 `CaptureStandardViews` 那样把 Gate12 材质从 Gate11 源刷回。捕获前后 SHA-256 比对确认 `Gate12R004RuntimeLabel.mat`、`Gate12R004BlackFlocking.mat` 与场景文件均未变。
- **机位**：五个标准视角（`hero`／`top`／`left-oblique`／`right-oblique`／`low`）数值复制自 Gate 12 R004 `CaptureStandardViews`，与 rev-004 已批准证据同框。新增 `label-macro` 由 `PhysicalLabel` 的 `renderer.bounds` 计算，标签移动或改尺寸时仍然框准。
- **六套候选**（`00-current` 为对照，无任何覆盖）：`a-archive-paper-flocking`、`b-graphite-deboss-microsuede`、`c-narrow-foil-ink-flocking`、`d-stone-paper-graphite-felt`、`e-anodized-plate-velvet`。纸类沿用 shipping 的 URP Unlit，石墨与阳极氧化铝改 URP Lit。斑点与箔带只在 albedo 近似（`patternApproximatedInAlbedoOnly=true`），真实浮雕需要 Gate 07 授权 base／normal map。

### 证据与实测

- 预览：`Artifacts/DisplayCaseSlabMaterials/slab-label-backplate-r001/`，30 张 `820 × 1000` 标准视角 + 6 张 `1640 × 2000` `label-macro` + 六张 `sheet-<view>.png` 横向对比（列序 `00-current`、A、B、C、D、E）+ `slab-material-options-report.json`。用户反馈六列对比图缩放后看不清，故由 `compose_readable_sheets.py` 另出带中文标注的大图：`readable-label-stack-1.png`／`-2.png`（每套占满宽度的标签特写）与 `readable-hero-grid.png`／`readable-low-grid.png`（3 × 2）。
- 标签特写放大后新增三项可读性发现：`00-current` 的浅色墨在棕色标签上对比极低，`ACQUIRED` 与 collectible id 两行几乎不可读，这是当前 shipping 的既有问题；B 的白墨配石墨是六套里层级最清晰的；C 的箔带与 D 的斑点在 Unlit 下几乎读不出来（C 的浅箔压在浅纸上没有金属响应，D 的斑点在本轮调细后过弱），两者的表面特征尚未被有效验证。
- 标签落地色实测（`label-macro` 右侧无字区均值，与授权值对比）：`00-current` 与 A 在 Unlit 下精确落在 `#423B33`／`#BDB8AD`；D 为 `(226,222,213)`，比 `#E4E0D8` 低 `2.3` 级（斑点拉低）；C 纸面精确、取样框跨过箔带故读数偏低 `18.9` 级。
- **两项阻塞发现**：B 的石墨 `#0E0F11` 在 URP Lit 下被 flat ambient `(0.28,0.30,0.34)` 抬到 `(48,51,55)`，高出授权值约 `36` 级并带蓝味，深黑标签在这套已批准灯光里无法落到授权值。E 的阳极氧化铝 `#6E7378` 渲染为 `(80,87,96)`，低 `27` 级，因为场景没有反射探针，金属只能反射 flat ambient；仅 `low` 视角能看出拉丝扫光。若选 B 或 E，必须先决定是压暗授权基色还是改 Gate 12 已批准灯光。
- E 另需先改设计圣经：金属铭牌与墨绿丝绒同时偏离 `FDB-DSP-011`（顶部实体纸标签）与 `FDB-DSP-014`（黑植绒）。本轮未改任何 `FDB-*`。

### 尚未做

- 未选定方向，未改 `MAT_LabelPaper`／`MAT_BlackFlocking`／Gate 07 `pipeline.json`，未新建 Gate 07 revision，未跑 Blender 重建，未构建或安装。设计与交付状态均未推进。

## 2026-09-09 模型工作台 Studio 三栏换皮 + 材质库 v1（工具，不进手机）

> **状态：工具代码 + Node 测试 + CDP 录屏已完成；视觉批准待确认。** 本轮只改 `tools/model-provenance-explorer` 与 `ArtSource/MaterialLibrary`，不改任何 shipping Unity 场景、材质或 Swift；无需推送手机。

用户指令（thread `abe4b59b-34b2-414f-ad0e-46ce03de7d0c`）：参照 Studio 工作台的三栏布局与材质卡片，“可以先做一、二”；“我们没有 Gemini Nano……只有 ChatGPT 的 Image Gen 模型”，因此不做 AI model 选择器。

### 已集成并有测试

- **三栏 Studio 外壳**（`index.html`、`styles.css`、`app.js`）：左栏 = 模型选择 + 七个固定工作区 tab（顺序与标签不变，改为纵向列表）；中栏 = `当前正在做什么` banner、`当前 Gate NN/12`／`已批准 X/12`、三阶段分组、12-Gate 单行路线图、点阵画布 `#stage-detail`；右栏 = `决策`（批准／退回按钮从画布移入，`#approve-stage`/`#reject-stage` id 不变）、`材质库`、`路线`／`导出`／`成品预览` 卡片。顶栏新增 `Gate NN/12`、`已批准 X/12` 两枚 chip。信息架构未变：`workspace-navigation-core.mjs` 未改，`WORKSPACE_TABS` 测试照旧。超长 diagnosis 文本改为可展开（之前把整个视口顶满）。Gate 07 用户可见 slot 新增 `material-preview`，GEEONE 的 lookdev board／kinematic board／旋转 MP4 现在能在画布里看到。
- **材质库 v1**：`ArtSource/MaterialLibrary/materials.json`（权威，18 项）→ `materials.md`（生成，不手改）+ `spheres/<id>.png`（Blender 5.2 Cycles 校准球，三灯 rig 同 GEEONE Gate 08）。每项：`id`、中英名、家族、状态（`approved-gate07`／`contract-locked`／`shipping-unity`／`stale`）、描述、边缘行为、ChatGPT Image Gen 可用短语／避免短语、Blender Principled 线性值、Unity URP sRGB 值、使用位置、仓库来源路径、缩略图 SHA-256。数值全部来自 `lookdev_geeone.py` rev-005、`ThreeBladeMaterialFactory.cs`、`FanCardSceneBuilder.cs`、`fan_card_guardrails.json`；`derived-from-unity` 条目由校验器强制 `baseColor = sRGB→linear(hex)`、`roughness = 1 − smoothness`。发现并记录（未修）：GEEONE 三材质 Blender 线性 0.78 被当成 sRGB 复制进 Unity（#C6C8CA ≈ linear 0.56），`parityNote` 已标明。`blood-red-crystal`、`matte-friction-plastic` 因基色由贴图／noise 驱动且 pipeline stale，列入 `pendingEntries`。
- **接口与校验**：`GET /api/material-library`；`material-library-core.mjs`（load／validate／derive／markdown）；`validate-material-library.mjs [--refresh] [--write-md]`；`npm run validate:materials`、`npm run materials:spheres`。右栏材质卡按 `usedBy` 高亮本模型，点击打开材质详情 dialog（球、双端数值、短语、来源链接）。
- **测试**：新增 `tests/material-library.test.mjs`（7 项：校验通过、md 同步、色彩换算、派生字段、axis-matte 合同锁定、错误注入、缩略图 hash 漂移）与 `tests/studio-shell.test.mjs`（4 项：IA 元素与顺序、右栏面板、三栏 CSS、无 Gemini／model-select）。`node --test tests/material-library.test.mjs tests/studio-shell.test.mjs tests/workspace-navigation.test.mjs` = 16/16。全量 `npm test` = 212/253，41 个失败全部是 magnetic-slide／premium-display-case 既有 manifest 状态断言（改动前同样失败），本轮未改。

### 证据

- CDP 录屏 [V14]：`Artifacts/ModelProvenanceExplorer/studio-shell-r001/studio-shell-r001-three-column-clear.mp4`（25 s，1440×900：GEEONE Gate 07 → 材质详情 → Unity tab → 成品预览 dialog → 白模 tab → Gate 03 → 切到磁吸推牌 → 交互 CAD）。帧：`studio-shell-r001-metal-three-blade-gate07.png`、`-material-dialog.png`、`-metal-three-blade-gate12.png`、`-magnetic-slide-gate12.png`、`-magnetic-slide-cad.png`、`-mobile-390.png`；改动前对照 `studio-shell-r001-before-metal-three-blade-gate07.png`。桌面与 390×844 横向溢出均为 0，运行时异常 0。
- 已知阻塞（改动前已存在）：`magnetic-fan-card` 的 `evidence/03-contract/*/modeling-contract.json` 不在磁盘上，`/api/models/magnetic-fan-card/contract` 返回 500，整个工作台对该模型显示“工作台无法连接”。本轮未修。

### 2026-09-09 18:08 追加：r002 减法重做（用户 17:46 “又复杂又土”）

用户选择：强调色柠檬绿（照参考图）；画布默认放大当前 Gate 的一个主产物。改动仍只在 `tools/model-provenance-explorer`，不推手机。

- 画布：`assetHeroPanel` 取代素材网格。主产物（图／视频内联／GLB 打开按钮）占满，下方一条底部工具条（名称、`n / N`、‹ ›、放大）和缩略图条；`visualFirst` 让图片、视频排在 GLB 与其他文件前。`userFacingStageAssets` 新增过滤 `cs/unity/xml/py/sh/js/mjs/meta/asset/log/env/csv`。Gate 10／11 带引导文案的对照页仍用原网格（browser 测试依赖单列 `.asset-grid`）。通用 `task-heading`（只重复关名）已删除。
- 中栏顶部：banner 一行（kicker + Gate 标题 + 截断原因 + 「详情」展开）；`canonical-progress` 变成 `Gate NN 标题` 大字 + 一行数字；12-Gate 路线图改成三组 26 px 圆点（已批准=柠檬绿实心、当前流程=白描边、正在看=白外圈），阶段名做成圆点下方小字。`data-current-gate` / `data-approved-count` / `.gate-roadmap-item.is-viewed[data-stage-id]` / `[data-workspace-tab] strong` 选择器不变。画布顶边从 ~430 px 提到 175 px。
- 左栏：模型与七个步骤同一种行样式，激活行左侧 3 px 柠檬绿；状态文字改为 7 px 圆点（`title` / `aria-label` 保留文字）。
- 右栏：`决策` = 状态一词 + 一句原因（三行截断）+ 表单，主按钮柠檬绿满宽；`材质` = 44 px 球 + 一个词，去 hex，本模型材质常亮、其余 70% 透明度折叠在「更多」；`导出` = 一排文件类型 chip + 一颗「↓ 下载 GLB」（只在 glb/fbx/blend 存在时出现）+ 6 张成品缩略图。路线卡（Blender／Rodin）、`shippingReady` 提示、`material-preview` 之类 slot 标签全部移出界面；`assetLabel()` 统一人话（`shipping-view-left-oblique` → 左斜视，`跨关引用` 代替 `未直接承接 06-geometry`）。
- 色板：`--accent #c8f04a`，其余灰阶（`#0d0d0e / #141416 / #1a1a1d`）；`--cyan/--green` 别名到 accent，`--purple/--blue` 别名到 muted，50 处蓝灰面板 hex 映射为中性灰，31 处 `rgb(95 214 223 /…)` 映射为 accent。基础字号 13→14 px，标题 22 px。
- 验证：`node --check`；`material-library` + `studio-shell` + `workspace-navigation` = 16/16；CDP 探针 desktop 1440×900 与 390×844 横向溢出 0、运行时异常 0、七 tab／12 gate／18 材质／10 本模型材质／5 导出 chip 均在。
- 证据 [V15]：`Artifacts/ModelProvenanceExplorer/studio-shell-r002/studio-shell-r002-distilled-clear.mp4`（25.8 s：Gate 07 hero 切图 → 材质详情 → Unity tab hero 翻页 → 白模 → Gate 03 → 磁吸推牌 → 交互 CAD）；帧 `-metal-three-blade-gate07.png`、`-material-dialog.png`、`-metal-three-blade-gate12.png`、`-magnetic-slide-cad.png`、`-mobile-390.png`。r001 帧保留作对照。

### 2026-09-09 18:51 追加：r003 收敛强调色（用户 18:19 “中间的那个可以试试删了…绿色只作为最主要的 primary action”）

用户指令逐条落地：

- “中间的那个删了”：中栏 12 圆点路线图 + 三阶段小字 + `Gate NN 标题` 大字整行删除（`renderStageRail` 只剩计数，`#stage-rail` 置 `hidden`）。12 个 Gate 改为行嵌在左栏所属 tab 下，只展开激活 tab（`02-analysis` 只列在「分析」下，`交互 CAD` 下只剩 04，避免重复）。`当前 Gate / 已批准` 只在顶栏保留一处，`data-current-gate` / `data-approved-count` 挪到 `#studio-header-meta.canonical-progress`；`.gate-roadmap-item.is-viewed[data-stage-id]` 选择器不变，browser 测试探针照旧。
- “绿色的点不要加”：左栏 7 px 状态圆点删除；未开始／待办的 tab 用 50% 文字灰表示，只有 `stale`／`rejected` 保留一颗琥珀／红点。
- “不要滥用绿色”：`var(--accent)` 在 CSS 里只剩 `.button-primary`；`button-primary` 在 JS/HTML 里只剩 `#approve-stage`（`复制路径`、`保存问题`、`重置 CAD 姿态`、`保存测量进度`、`保存这版规格` 降为普通按钮）。激活行去掉 3 px 绿条，只用 `--panel-2` 填充；缩略图选中态白描边；focus 白描边；品牌第二词、banner「详情」、已批准状态、材质链接、`user-provided` chip 全部改灰阶；`--cyan/--green` 别名改 `#d8d8dd`，31 处 `rgb(200 240 74 /…)` 改白色透明度。测试 `green is reserved for the approve action` 锁死。
- “3D 模型能拖吗”：能。`openGlbAsset` 增加 `container / height / setCleanup` 参数，`visualFirst` 把 GLB 排第一，画布主位直接内联 three.js OrbitControls（拖动旋转、滚轮缩放，视角／线框／灯光工具条悬停才显示），`state.heroViewerCleanup` 在切图或切 Gate 时释放 WebGL。dialog 版 GLB 查看器不变。
- 验证：`node --check`；`studio-shell` + `material-library` + `workspace-navigation` = 19/19（新增 3 条守卫）。全量 `npm test` 222 pass / 42 fail，42 条失败在改动前同样失败（`git stash` 对照），全是 `magnetic-slide-tile` 清单状态断言，与本轮无关。CDP 探针：7 tab、12 gate（可见 4）、`#stage-rail hidden=true`、Gate 10 hero `canvas` 已挂载（521 px 高）、`.button-primary` 在已批准 Gate 为 0、横向溢出 0、异常 0。
- 证据 [V16]：`Artifacts/ModelProvenanceExplorer/studio-shell-r003/studio-shell-r003-quiet-accent-clear.mp4`（28 s，1440×900：Gate 07 hero 切图 → 左栏点 `10 导出包` → GLB 内联拖动两次 → 材质详情 → Unity tab → 白模 → 磁吸推牌 → 交互 CAD）；帧 `-metal-three-blade-gate07.png`、`-metal-three-blade-gate10-glb.png`、`-metal-three-blade-gate12.png`、`-magnetic-slide-cad.png`。
- 未做：磁吸推牌 Gate 02–04 的定制 CAD 面板（合同 hash 胶囊、四个大 tab、`可交互审批` 卡）仍是旧结构，本轮只把它们的青色换成灰阶。

### 2026-09-09 19:10 追加：r004 提亮 + 少量绿色 + 左栏缩小（用户 19:00 “又太黑了…在按钮和关键选项上加绿…左边字体小一点…还是那么复杂”）

- 色板整体提亮两档：`--bg #0d0d0e → #222227`，`--panel #141416 → #2c2c32`，`--panel-2 → #36363d`，线条 `#46464e`，文字灰 `#b4b4bb / #82828a`；画布与缩略图底 `#080809 → #1a1a1e`。
- 绿色回到关键位置（CSS 测试维护一份允许清单）：`#approve-stage` 实心；`↓ GLB` 下载改为绿描边 `.button-accent`；激活 tab 文字、正在看的 Gate 行文字、当前 hero 缩略图描边、`已批准` 状态字、顶栏当前 Gate 数字为绿；材质球 / 成品缩略图 / 导出链接 hover 绿描边。模型行仍是灰填充，避免和步骤争层级。
- 左栏：模型与 tab 行 38→30 px、字 13→12 px；Gate 行 26 px、11.5 px；`模型 / 步骤` 小标题 11 px 灰。
- 减法：banner 的「当前正在做什么」kicker 改 `visually-hidden`；右栏材质从 3 列「球 + 名字」卡片改成一排 36 px 球（名字在 `title` / `aria-label` 和详情弹窗），去掉「本模型 10」计数；导出从 5 颗 chip + 满宽按钮改为一颗绿描边 `↓ GLB` + 一行文字链接（Blend FBX 碰撞 清单）；「成品」缩略图折进 `成品 · N` 折叠，只在 Unity tab 默认展开。画布内所有定制 h2 统一 16 px（此前 `clamp(20px, 2.2vw, 30px)`）、eyebrow 11 px，磁吸推牌 Gate 02–05 的大问题标题随之收敛。
- 验证：`studio-shell` 7/7（`green marks the approve action and a short allowlist of key options` 改为允许清单断言）；CDP 探针 18 材质球、4 导出链接、`↓ GLB`、3 成品、横向溢出 0、异常 0；已批准 Gate 上 `.button-primary` 为 0。
- 证据 [V17]：`Artifacts/ModelProvenanceExplorer/studio-shell-r004/studio-shell-r004-lifted-palette-clear.mp4`（25 s，1440×900，同 r003 路径含 GLB 拖动）；帧 `-metal-three-blade-gate07.png`、`-metal-three-blade-gate10-glb.png`、`-metal-three-blade-gate12.png`、`-magnetic-slide-gate05-glb.png`、`-magnetic-slide-cad.png`。

### 2026-09-09 21:55 追加：r005 折叠定制关卡文案（用户 21:40 “这些文字能简短吗，或者去掉吧，能视觉化的话就视觉化，不能就尽量隐藏或者收起”）

- 32 处手写的关卡简报（`.task-heading` / `.simple-task-header` / `.mechanism-review-heading` / 带 `h2` 的 `header`）原本是 eyebrow + 大问题 + 说明段 + 「本轮只确认」chip + 小字。新增 `compactBriefs(els.stageDetail)` 在每次画布渲染后跑一遍：只留问题一行（16 px），其余节点连同紧跟其后的 `p/small` 一起搬进一个 `<details class="brief-more"><summary>说明</summary>`，默认收起。节点是移动不是重建，绑定的事件与 browser 测试选择器（`.mechanism-review-heading h2`、`.evidence-basis-badge` 等）仍在 DOM。
- 顶部 banner 只剩 `Gate NN · 标题` + 「详情」，截断原因不再显示在行内（展开仍有全文）。
- 画布内所有 `clamp()` 大标题（26–64 px）统一 16 px：`blockout/geometry/material-task-heading`、`simple-review-mode h1`、`simple-question-copy h3`、`plain-gate10/11 heading`、`action-heading`、`mapping-confirmation p`（28→13 px）、`sandbox-heading h3`、`mechanism-unknowns h3`。金色 eyebrow（`#b9a780`）改灰；`请确认` / `下一版白模必须改正` 块的外边距减半。
- 验证：`studio-shell` 8/8（新增 `bespoke gate briefs fold to one question line`，断言画布 CSS 里没有 `h2 { … clamp( … }`）；三套 UI 测试 20/20。CDP 探针：磁吸推牌 Gate 05 `[data-compact]` 1、`.brief-more` 1、GLB 画布顶边从 ~235 px 提到 172 px；Gate 02 CAD、Gate 03、Gate 04、Gate 07 横向溢出 0、异常 0。
- 证据 [V18]：`Artifacts/ModelProvenanceExplorer/studio-shell-r005/studio-shell-r005-folded-briefs-clear.mp4`（22.5 s，1440×900：GEEONE Gate 07 → Gate 10 GLB 拖动 → 材质球 → Unity → 磁吸推牌 CAD 展开「说明」→ 白模 Gate 05 展开「说明」→ 拖动 GLB）；帧 `-magnetic-slide-gate05.png` / `-gate05-open.png` / `-gate04.png` / `-gate03.png` / `-cad.png`、`-metal-three-blade-gate07/10-glb/12.png`。
- 未做：问题句本身（如「顶片是否只在推到最大端点后解锁 360°，并在对齐后才能回推？」）没有改写；Gate 03 的 9 项测量表单、Gate 04 的三色结构图例仍完整显示，因为它们是交互或视觉本体。

### 2026-09-10 08:50 追加：r006 页面内新建模型 + Gate 01 上传（用户 07:46 “既然我都有前台页面了，我就不需要去那个 terminal 里面跑了吧？”）

- 后端：`pipeline-core.mjs` 新增 `createModelPipeline({ id, name, mechanism })`（与 `init_model_pipeline.mjs` 共用，脚本改为薄封装，新增 `--mechanism`）和 `addIntakeFile(modelId, { filename, bytes, note })`：字节写入 `evidence/01-intake/rev-NNN/`（同名自动 `-2`），按扩展名分 `user-photo` / `user-video` / `user-document`，注册为 `slot original-reference`、`role user-input`、`provenance.origin user-provided`，Gate 01 置 `ready_for_review`，`reviewArtifactIds` 排除文档；Gate 01 已批准时再上传会 `revision+1` 并把下游 `stale`。`server.mjs`：`POST /api/models`（JSON）、`POST /api/models/:id/intake-file`（`application/octet-stream` + `x-filename`，上限 512 MB，绕开 16 MB JSON 限制），`GET /api/models` 附带 `mechanisms`。
- 前端：左栏模型列表下 `＋ 新建模型`（虚线，hover 变绿），`<dialog>` 内名称 / ID（自动 slug，中文名回退 `model-<base36>`）/ 机构 / 拖放区 + 文件列表 / 状态行 / 取消 + 唯一 Primary「创建并进入 Gate 01」。提交后顺序上传、刷新模型列表、`loadModel(id)`、切到 `参考原图 / 01`，toast「已创建「…」，N 个参考待确认」。Gate 01 画布：无素材时整块拖放区，有素材时底部 44 px「＋ 再加参考」条。
- 验证：新增 `tests/model-intake.test.mjs` 3/3（建模型/重复 409/非法 ID/非法机构；三文件上传后 `ready_for_review`、同名不覆盖、PDF 不进 review、非法类型与空文件拒绝；已批准 Gate 01 再上传开 rev-002 且 Gate 02 `stale`），用完即删临时模型；`studio-shell` 9/9（Primary 允许列表加 `new-model-submit`，绿色允许列表加 `.model-add:hover` / `.intake-drop` 悬停 / 表单 focus）。全套 231/272，41 项失败为既有 manifest 状态漂移测试，与本轮无关（基线同为 41）。CDP 端到端：输入「黄铜陀螺」→ `brass-spinner` → 选 2 张 jpg + 1 个 78.6 MB MOV → 创建，Gate 01 出现 3 个缩略图、`#approve-stage` 可用、异常 0；演示模型录完已删除。
- 证据 [V19]：`Artifacts/ModelProvenanceExplorer/studio-shell-r006/studio-shell-r006-new-model-clear.mp4`（18.8 s，1440×900）；帧 `-new-model-dialog-empty.png` / `-dialog-filled.png` / `-gate01-after-create.png` / `-gate01-video.png`。
- 未做：拖放尚不支持整目录；HEIC 会归档但浏览器不预览；Gate 01 审批文案仍是通用「确认，继续」。

### 2026-09-10 10:05 追加：r007 新建模型改 Primary 置底 + 步骤连线（用户 09:58 “这个新建模型做成 primary button 的样式，然后放在最底部……这个黄点是什么意思呀？能不能在步骤前面都加一些 line，能够标识出当前我在哪一步了？”）

- 黄点解释：原 `.workspace-tab[data-status="stale"]::after` 的琥珀色小点 = 上游改动后该步「过期」，红点 = 「被退回」。两处点状标记均删除。
- 左栏：`＋ 新建模型` 从模型列表下的虚线行改为 `.button.button-primary`，放进 `.sidebar-foot`（`position: sticky; bottom: 0`，渐变遮底），永远在左栏最底部；`.sidebar` 改 flex column。
- 步骤：`.workspace-group::before` 一条 1 px 竖线贯穿 7 个步骤，首尾只画半段；每个 `.workspace-tab::before` 一个 7 px 节点。`data-step` 由 `renderWorkspaceTabs` 写出：`current`（= `workflowStageOf` 所在步，永远且只有一个；绿点 + `--accent-soft` 光晕）、`done`（实心 `--muted`，其上方竖线同步变亮，done→非 done 段用 15 px 渐变收尾）、`todo`（空心 `--dim`）、`stale`（空心琥珀环）、`rejected`（实心红）。12 关子行里过期/退回改为右侧 `<em>过期</em>` / `<em>退回</em>` 文字。
- 验证：`studio-shell` 10/10（绿色允许列表换成 `.workspace-group[data-step="current"] .workspace-tab::before`，静态 Primary 允许 `new-model-button` + `new-model-submit`；新增「steps read as one stepper line; new model is pinned at the sidebar foot」）。全套 232/273，41 项失败为既有 manifest 漂移测试（基线相同）。CDP 探针：三叶金属 `steps = done×6 + current:Unity 灯光与成品`，按钮 `y=812–852 / vh=900`；异常 0。
- 证据 [V20]：`Artifacts/ModelProvenanceExplorer/studio-shell-r007/studio-shell-r007-stepper-and-new-model-clear.mp4`（17.2 s，1440×900：磁吸推牌全过期视图 → 切参考/白模 → 打开新建模型对话框 → 三叶金属 6 done + 1 current）；帧 `-magnetic-slide-stepper.png` / `-metal-three-blade-stepper.png` / `-new-model-dialog.png` / `-stepper-crop.png`（两模型左栏放大对照）。
- 备注：磁吸推牌 6 步全显琥珀环是 manifest 真实状态（Gate 12 current、其余 stale），不是 UI 缺陷。本轮未 commit / push。

### 2026-09-10 10:50 追加：r008 模型缩略图 3×3 + 全局字号 −1~2 px + Obsidian 链接建模（用户 10:35 “上边那个模型能用预览图吗？缩略图，用 3x3 的这种 grid，不要都显示文字……整体字号能再缩小 1 到 2 pt”；10:38 “通过 Obsidian 的那个笔记的链接来创建……把名称、结构以及参考图片和视频都上传”）

- 模型列表：`listModelSummaries` 新增 `thumbnail`（`modelThumbnail`：从 Gate 12 往前找第一张磁盘上存在、名字含 hero/front/beauty/turntable-frame/render 的图，排除 sheet/contact/silhouette/options/grid；没有 hero 类则退回最新关卡任一图）。左栏改 `grid-template-columns: repeat(3, 1fr)` 方形瓦片（64 px），名字只留 `title` / `aria-label` / 视觉隐藏的 `<strong>`；未选中 0.72 透明度，选中 1 px `--text` 描边，无绿色。磁吸扇牌 manifest 引用的 304 张图在磁盘上一张都不存在，显示首字「磁」占位。
- 字号：`styles.css` 内所有 ≥11 px 的 `font-size` 统一下调（11→10.5，12/13→11/12，≥14 −2），<11 px 的微字不动；CDP 实测 tab 11 px、banner 12 px，横向溢出 0。
- Obsidian：新增 `obsidian-intake.mjs`（解析 `obsidian://open?vault&file` / `obsidian://vault/...` / 绝对路径 / 库内相对路径；库位置来自 `~/Library/Application Support/obsidian/obsidian.json` 或 `FIDGET_OBSIDIAN_VAULT`；路径越界 403、笔记不存在 404；frontmatter、H1 标题去 `#tag`、`![[...]]` 与 `![](...)` 嵌入按库相对 / 笔记相对 / 全库同名三级解析；`guessMechanism` 关键词猜机构；`publicPreview` 不泄露绝对路径）。`GET /api/obsidian/preview?link=`；`POST /api/models/:id/intake-from-obsidian` → `importObsidianNote`：笔记原文存 `obsidian-note.md`（`external-reference-document`，不进 review），每个本地图/视频经 `addIntakeFile(source: obsidian)` 存 `evidence/01-intake/rev-NNN/`，`role external-reference`、`origin external`、`contentClass external-reference-photo/video`、`sourceLocator` / `sourceUrl` / `vaultPath` 全记录。对话框首行「Obsidian 链接」粘贴即预览（350 ms 防抖）：一行摘要「「标题」· N 张图 · N 个视频」，自动填名称、ID、机构猜测；提交顺序：建模型 → 导入笔记 → 上传本地文件。
- 验证：`obsidian-intake.test.mjs` 4/4（临时库，不读真实笔记）、`model-intake` 3/3、`studio-shell` 11/11；全套 237/278，41 项失败为既有 manifest 漂移（基线相同）。CDP 端到端用真实笔记 `笔记同步助手/2026-08-20/#edc 解压玩具`：预览 10 张图、标题「edc 解压玩具」、机构猜 other → 创建 `edc-slide-demo`，Gate 01 出现 10 张缩略图与可批按钮，toast「11 个参考待确认」（10 图 + 1 笔记），异常 0。
- 证据 [V21]：`Artifacts/ModelProvenanceExplorer/studio-shell-r008/studio-shell-r008-grid-obsidian-import-clear.mp4`（11.0 s，1440×900）；帧 `studio-shell-r009-grid-and-type.png`（3×3 缩略图 + 新字号）、`-obsidian-prefilled.png`、`-gate01-from-obsidian.png`。
- 备注：按用户要求本轮未执行任何删除，演示模型 `edc-slide-demo` 仍在 `ArtSource/ModelPipeline/`，等用户决定保留或删除。未 commit / push。

### 2026-09-10 11:25 追加：r010 Gate 02+ 的 CTA 与进度 / 批准后自动进下一关 / 扇牌可打开 / 缩略图用 app 成品图（用户 11:05 “点到某一个模型的话，它就会显示‘工作台无法链接’……策略图应该显示你在最终 app 里面调的那个”；11:17 “上传完了之后没有开始分析，或者没有一个明确的 CTA 或者是进度指示”）

- 根因：用户从 Obsidian 建了 `model-hhax`「视频号笔记」并批准 Gate 01 后，画布仍停在 Gate 01 的参考图，右栏只写“已批准”，Gate 02 画布是一句“本关还没有可看的素材”。分析本身不是工作台能执行的：Gate 02–12 的产出（发现记录、分析板、建模合同、白模……）由 agent 任务生成，工作台只是状态与批准面。
- 修复 1（CTA + 进度）：`agentStepPanel(stage)` 替代空态。空闲：一句“看参考图和视频，判断这是什么机构、怎么玩”+ 产出说明 + 唯一 Primary「开始分析」（每关文案 `agentStepCopy` 02–12）。点击 `POST /api/models/:id/stages/:stageId/work-request`（`requestStageWork`：写 `currentState.workRequests[stageId] = {status: requested, requestedAt, deliverables}`、`diagnosis` 改为“已请求 agent 开始，等待产出：…”、history `stage-work-requested`；409 修订冲突；Gate 01 / 已批准关 422）。已请求：绿点脉冲 + “已请求 11:23 · agent 正在处理，产出后这里会出现：发现记录、分析板” + 次级「撤回请求」（`stage-work-withdrawn`）。上一关未批准：灰色说明，无按钮。请求不改变关卡状态（测试断言仍为 blocked），不假装执行。
- 修复 2（批准后去哪）：`submitDecision` 批准成功后 `selectWorkspace({ stageId: next.id })`，toast「「原始参考归档」已确认 → 下一步：参考分析」。默认批注由错误的 “Interactive CAD geometry checklist completed.” 改为 `在工作台确认「<关名>」。`。
- 修复 3（无法连接）：`GET /api/models/:id/contract` 对“合同文件在磁盘上缺失”返回 200 `{contract: null, warning}` 而非 500；前端 toast 提示。磁吸扇牌 manifest 528 个资产仅 9 个存在于磁盘（rev-007 `modeling-contract.json` 也不在），现在能打开，但预览为断图；这是仓库文件缺失，不是工作台 bug。
- 修复 4（缩略图）：`modelThumbnail` 优先 `Assets/Plugins/iOS/Thumbnails/Models/product-thumbnail-<id>.png`（app 内实际使用的成品图），7 个 shipping 模型全部命中；无 app 图的（`premium-display-case`、Obsidian 新模型）退回原逻辑。
- 右栏原因文案 `humanizeSlots`：`discovery-log、analysis-board` → “发现记录、分析板”（`slotLabels` 覆盖 12 关全部必需槽）。`styles.css` 去掉重复的 `.visually-hidden`。
- 验证：`model-intake` 5/5（新增 work request 状态机 + 缩略图优先级）、`studio-shell` 13/13（agent-step 结构、绿色 allowlist 加 `.agent-pulse`、批准后跳转）、`obsidian-intake` 4/4；全套 240/281，41 项失败为既有 manifest 漂移（基线相同）。CDP：`model-hhax` Gate 02 出现「开始分析」→ 点击后进入已请求态（真实写入该模型 manifest rev 11 与 history）→ 切换磁吸扇牌无“无法连接”→ 切换三叶金属正常；缩略图 src 7 个为 `product-thumbnail-*.png`。
- 证据 [V21]：`Artifacts/ModelProvenanceExplorer/studio-shell-r010/studio-shell-r010-agent-step-cta-clear.mp4`（27.8 s，1440×900）；帧 `studio-shell-r010-hhax-gate02-cta.png`、`-hhax-gate02-requested.png`、`-fan-card-opens.png`。
- 未做：工作台不会自动启动 agent 任务；`workRequests` 只是给 agent 看的排队状态。`model-hhax` 的 Gate 02 分析仍需一个按 `fidgeting-model-pipeline` skill 走的独立任务。视觉批准待确认，未推送手机；未 commit / push。

### 2026-09-10 15:40 追加：r011「开始分析」真的启动 agent（用户 15:24 “现在流程是不通的呀……我现在没法进行到下一步”）

- 根因：r010 的按钮只写请求状态，没有任何进程接活，Gate 02 成死路。
- 修复：新增 `agent-runner.mjs`。`POST …/work-request {action: request}` → `startStageRun`：先 `requestStageWork` 记状态，再 `spawn("agent", ["-p","--trust","--force","--output-format","stream-json","--workspace",<repo>, prompt])`（Cursor CLI，`~/.local/bin/agent` 2026.04.17；可用 `FIDGET_AGENT_BIN` 覆盖），detached，stdout 落 `ArtSource/ModelPipeline/<id>/agent-runs/<stage>-<ts>.ndjson`、stderr `.stderr.log`、prompt `.prompt.md`，运行登记在 `agent-runs/index.json`（在 manifest 之外，因为 agent 自己要写 manifest）。`buildStagePrompt`：点名模型/机构/关卡、要求先读 skill 与 `pipeline-contract.md`、素材与 manifest 路径、必需槽位与对应保存函数（02 `saveAnalysisResearchRevision`、03 `saveModelingContract`、04 `saveArchitecturePlan`、05/06/07 对应 review 函数）、禁止批准 / commit / 构建 / 装机 / 动其他模型、结束 5 句中文总结。`GET …/work-request` 返回 `{request, run, revision}`；`run.lastActivity` 从 stream-json 抽最近一句助手文本或工具名，`finalText` 取 result；进程死了但没 exit 钩子（服务器重启）标 `ended`；stderr 含 “Authentication required” → `needsLogin`。`withdraw` → `stopStageRun`：SIGTERM 进程组 + 撤回请求。`POST /api/agent/login` 启动 `agent login`，把它打印的一次性授权 URL 交给前端；`GET /api/agent/auth` 用一条 “Reply OK” 探测登录态。
- 前端：`agent-step` 面板四态。idle：一句说明 + Primary「开始分析」；running：绿点脉冲「agent 正在做 · 已运行 mm:ss」+ 等宽 `agent-activity` 最近动作 + 「停止」，每 3 s 轮询，manifest revision 变化就 `loadModel` 重载（agent 登记产出后自动出现资产与批准按钮，toast「agent 做完了，请检查产出并确认」）；finished（结束但槽位仍缺）：显示 agent 最后一段话 + 「再试一次」；failed/needsLogin：「登录 Cursor agent」Primary → 新标签页打开授权 URL。
- 验证：`agent-runner.test.mjs` 3/3（假 `agent` 二进制：prompt 内容、running→done 与 finalText、未登录→`needsLogin` + 停止清请求）；`studio-shell` 13/13；`model-intake` 5/5。真机：API 触发 `model-hhax` Gate 02 → 5.1 s 后 `failed / needsLogin: true`（本机 Cursor CLI 未登录）；CDP：面板显示「还没登录 Cursor agent，跑不起来」+ 登录按钮，点击后服务器返回授权 URL，`agent login` 进程确认会等待浏览器授权（15 s 仍存活），异常 0。
- 证据 [V21]：`Artifacts/ModelProvenanceExplorer/studio-shell-r011/studio-shell-r011-agent-launch-needs-login-clear.mp4`；帧 `studio-shell-r011-gate02-needs-login.png`、`-gate02-login-clicked.png`。
- 阻塞：Cursor CLI 需用户在浏览器完成一次 `agent login`；完成前任何关卡都跑不起来。完成后 `model-hhax` Gate 02 首跑尚未验证（真实 agent 能否按 prompt 走完 `saveAnalysisResearchRevision` 待观察）。视觉批准待确认，未推送手机；未 commit / push。

### 2026-09-10 16:30 追加：r012 `model-hhax`「视频号笔记」Gate 02 分析已交付；登录不再是前置条件（用户 16:02 “我为啥要登录 Cursor Agent 的呀？我是要上传图片之后，然后你开始分析嘛？你分析完了之后，我要确认嘛？”）

- 用户预期：上传 → agent 分析 → 用户确认。登录 Cursor CLI 只是“工作台自动派活”的可选加速，不应挡在流程上。`agent-step` 面板新增 `handoff` 态：CLI 未登录时显示绿点“已交给 agent · 做完后这里会出现 发现记录、分析板”，登录按钮降为次级文案「想让工作台自己跑？登录 Cursor agent」；Primary 只剩「开始分析」/「再试一次」。
- Gate 02 交付（本对话 agent 按 `fidgeting-model-pipeline` skill 执行）：读 7 张用户静帧 + Obsidian 笔记，未做联网检索、未推断任何 mm。产出 `evidence/02-analysis/rev-001/analysis-board.png`（2600×1900：7 帧标注 A–G、推开方向箭头、5 条结论带置信、4 条未知）与 `discovery-log.json`（笔记/图像关键词、逐帧观察、机构结论、未知、建议）。经 `saveAnalysisResearchRevision` 登记：2 资产、6 条 claim（机构=线性磁吸推牌 置信中、胶囊轮廓目测 1.6:1、三层结构、材质、正/背面图案、尺寸与旋转未知），3 项 validation（仅用用户来源 / 无尺寸推断 / 未知保留），Gate 02 → `ready_for_review`，manifest rev 13，`workRequests["02-analysis"].status = delivered`。`validate_model_pipeline.mjs model-hhax`：errors 0、missingFiles 0。
- 通用化修复：`saveAnalysisResearchRevision` 原本把 slide-tile 的 4 条 validation、diagnosis、staleReason、recipe 写死，现改为 `payload.validations / diagnosis / staleReason / recipe` 可覆盖，默认值不变。`userFacingStageAssets` 对 02/04 原本一律返回空（slide-tile 有专用审阅组件），现只在 `analysisSpec / architectureSpec` 存在时返回空，普通模型显示 `reviewArtifactIds` 里的图像。批准按钮由写死的“这 4 项理解正确”改为按活动 claim 数“这 N 条判断正确，继续”；文本框提示改为“如有错误，指出哪一条”。
- 验证：全套 244/285（41 项既有 manifest 漂移，基线相同）；CDP：`model-hhax` Gate 02 画布显示分析板，右栏「可审批」+「这 6 条判断正确，继续」可点，异常 0。
- 证据 [V21]：`Artifacts/ModelProvenanceExplorer/studio-shell-r012/studio-shell-r012-hhax-gate02-board-clear.mp4`；帧 `studio-shell-r012-hhax-gate02-board-ready.png`；分析板副本 `model-hhax-gate02-analysis-board-rev001.png`。
- 等待用户：在工作台确认或退回 Gate 02；确认后 Gate 03 需用户提供实物尺寸（建议把机构从「其他」改为「磁吸推牌」并复用九项核心尺寸清单）。视觉批准待确认，未推送手机；未 commit / push。

### 2026-09-11 07:52 追加：r013 普通新模型打通 Gate 02–04 + `model-hhax` 九项实测面板

- 当前决定：`model-hhax` Gate 02 仍为 `ready_for_review`、6 条活动判断、manifest rev 13；用户尚未确认或退回，机构仍为 `other`，Gate 03 仍 blocked。本轮没有替用户批准、没有推断毫米数、没有创建 Blender 白模，也没有改动其他模型证据。
- 通用 Gate 02–04：普通模型现在会显示本关一句用途、当前模型自己的可视产出、唯一 Primary 与退回入口；02/04 只在确有专用 `analysisSpec` / `architectureSpec` 时隐藏通用资产。批准普通 Gate 02 后，若已确认的机构 claim 明确写为线性磁吸推牌，前端通过新的安全 `PATCH /api/models/:id/mechanism` 把 `other` 改为 `linear-magnetic-slider`；后端要求 Gate 02 已批准、有可追溯机构判断且 Gate 03 以后尚无证据/决定/进展，拒绝越级或覆盖已有工作。
- Gate 03 填数：`linear-magnetic-slider` 按机构类型复用九项核心尺寸，不再依赖固定模型 ID：闭合 L/W/T、顶片厚、底片厚、最大直推行程、轴心距最近圆端、旋转载体直径、闭合接缝/间隙。每项要求 mm、来源、不确定度与测量方法，可上传对应测量照片；可显式勾「不知道」并保存，但仍计为未完成，9/9 与一致性检查通过前不得进入评审。普通新模型不提供「我估的」来源；没有数值默认值。
- Gate 04 与 agent：普通线性推牌可用自己的 Gate 02 来源与 Gate 03 合同生成自己的零件树、结构方案和检查结果，移除 `magnetic-slide-tile` 的固定角度、固定素材 ID 等专用假设。agent 面板保留 idle / running / handoff / finished / failed 五态；「登录 Cursor agent（可选）」保持次级，Primary 只用于开始、再试或用户批准；技术日志折叠，业务界面不再显示素材 ID。
- 验证：聚焦普通模型端到端、九项尺寸、intake、agent runner、studio shell 34/34；全套 `node --test tests/*.test.mjs` 为 250/291 pass、41 fail，41 项均为既有 manifest 漂移，数量未增加（带引号的字面 glob 在当前 Node 20 不展开，随后以等价 shell glob 实跑）；`validate_model_pipeline.mjs model-hhax`：errors 0、missingFiles 0、unhashed 0，仍为 1/12、等待 Gate 02 用户决定。真实浏览器探针：用途、分析板、「这 6 条判断正确，继续」、退回入口均出现，运行时异常 0。
- 证据 [V22]：`Artifacts/ModelProvenanceExplorer/studio-shell-r013/model-hhax-gate02-walkthrough.mp4`（H.264 / libx264 / CRF 17 / yuv420p，1440×1000）；PNG `model-hhax-gate02-overview.png`、`model-hhax-gate02-review.png`，并保留本轮录屏帧。等待用户：在工作台确认这 6 条判断，或写明错误后退回；确认后页面直接进入九项尺寸填写，未知项可先标记但不会解锁下一步。视觉批准待确认，未推送手机；未 commit / push。

### 待办

- 用户视觉批准 r005–r008 外壳；决定 `edc-slide-demo` 去留（已在 Cursor 内置浏览器打开 `http://127.0.0.1:8891/tools/model-provenance-explorer/`）；决定是否把 Gate 07 lookdev 脚本改为按 `materialLibraryIds` 引用并由 validator 强制。
- 第三步（Blender/CLI 一键重跑）与第四步（ChatGPT Image Gen 概念分支）未开始。

## 2026-09-09 四款 catalog 收敛、成长圆环删除、库／详情同一套光照与倍率、GEEONE 光照预设 A/B/C/D、四场景共用 +0.15 EV、Mobile 管线 HDR

> **状态：代码 + EditMode 测试 + 模拟器录屏已完成；视觉批准待确认，未推送手机。** GEEONE 光照预设等待用户在 A/B/C/D 中选择，出货仍为 A（Studio Bright）。

用户指令（thread `c22de829-ed8e-43df-af2e-695615b0c261`）：09-08 19:28“主场景里面的那个光照和点击‘进入详情’把玩的这个光照，感觉用的不是一套”；19:40“每一个模型上面都有一个奇怪的圆环……去掉”“推牌……在列表场景的时候，它的尺寸过大了”“内外一定要一致……不要顺跳，要过渡”；09-09 08:31“前两张图的陀螺去掉……第三张的陀螺是不是光照太强了，有没有柔和的一点的灯光设置”。

### 已集成并有测试

- **Catalog 收敛（`FDB-PREF-032`）**：`ProductCatalog.shippingEntries` 只余 `metal-three-blade`（`DefaultModelId`）/ `graphite-two-lobe` / `magnetic-slide-tile` / `magnetic-fan-card`；`RetiredModelIds = {pointed-three-blade, gold-four-wing}`。`ProductCatalogMigration` `CurrentMigrationVersion = 2`，链式执行 v1→v2，把两旧 ID 的成长 / 收藏 / 皮肤 / 已选模型迁入 GEEONE，数值字段取最大值（`MergeMaximumNumericString` / `MergeMaximumInteger`）。`EditorBuildSettings` 移除 `ThreeBladeEDC.unity`、`ImportedSpinner.unity`；`PremiumDisplayCaseProductPresentation.profiles` 4 款；`FidgetAppCoordinator.ModelIdForScene` 退役场景回落默认模型。Swift `CodexSwiftUIOverlay.swift`：`shippingCases` 4 款，`retiredCases` + `resolveShipping` 迁移持久化选择，默认 `metalThreeBlade`。测试：`SpinnerProgressionTests.CatalogMigrationConsolidatesRetiredRotorsIntoGeeoneWithoutLosingState` / `CatalogMigrationVersionTwoUpgradesAnExistingVersionOneInstall`；`ProductArchitectureTests.ReleaseBuildContainsOnlyTheFourApprovedProductScenes` / `RetiredThreeBladeRotorsConsolidateIntoGeeoneWithoutLosingState`；`PremiumDisplayCaseTests` 4 款。
- **成长圆环删除（`FDB-PREF-034`，`FDB-TRI-005`）**：根因是 `SpinnerProgressionVisuals` 在每个 rotor 上生成 `StageMaterialCollar` 圆环。删除 `SpinnerProgressionVisuals.cs`、`ProgressionVisualPreviewCapture.cs`；`FidgetAppCoordinator.ConfigureProgressionVisuals` 改为 `RemoveLegacyProgressionRingRoot`（`LegacyProgressionRingRootName`）；`ThreeBladeMetalSkinProgression` 改引用该常量。测试：`SpinnerProgressionTests.ThreeBladeMetalSkinSelection_IsPersistedAndBridgedWithoutRawHaptics` 断言不再 `AddComponent<SpinnerProgressionVisuals>`。
- **库／详情同一套光照 + 过渡（`FDB-PREF-035`）**：`SpinnerEnvironmentCatalog` `metal-three-blade` `LibraryLightScale = LibraryReflectionScale = 1.00`；`SpinnerImageBasedLightingController` GEEONE 库／详情共用 `GeeoneLightingPresetCatalog.Active`，`PresentationLightingState` 在共享 presentation 曲线上插值；`SpinnerEnvironmentPresenter.SetLibraryPreviewActive` 透传 `immediate`，`SetDetailEntranceProgressForPreview` 同步灯光进度。测试：`SpinnerEnvironmentTests.GeeoneLightsIdenticallyInLibraryAndDetail`、`LibraryDetailLightingSwitchTweensOnTheSharedPresentationCurve`、`SoftLightingPolicy_ReducesEnergyAndCapsReflectionWithoutHueShift`（GEEONE trim = 1）。
- **推牌列表倍率（`FDB-PREF-035`）**：`EdcPortraitCameraFramer` 新增 `LibraryDistanceScale` / `LibrarySafetyFraction`，列表距离由 `ResolveAuthoredPoseDistance` 按 authored 详情距离缩放，`transitionProgress` tween；不再按视口占比放大。测试：`SpinnerEnvironmentTests.AllSixProductsUseLiveBoundsAndViewportOccupancyBoundaries`（`magnetic-slide-tile` 改验 authored 距离与倍率）。
- **GEEONE 光照预设（`FDB-PREF-036`，Proposed）**：新增 `GeeoneLightingPresetCatalog`（`Shipping` / `SoftStudio` / `Overcast` / `LowKey`），字段：Key / WarmRim / CoolFill 最终强度、`VisibilityFillIntensity`、`AmbientBoost`、`StudioSoftboxIntensity`。`SpinnerImageBasedLightingController`：GEEONE 三盏 authored 聚光直接取预设强度（不再是 floor，否则柔预设降不下去）；`BuildReflectionCubemap` 对 GEEONE 按 `StudioSoftboxIntensity` 叠加推牌同款宽面柔光箱 + 中性底（峡谷调色板接近全黑，钢面原本几乎没有环境反射）。出货 `Shipping` 数值 = 原 floor，渲染不变。测试：`SpinnerEnvironmentTests.GeeoneLightingPresets_ShipStudioBrightAndOfferOnlySofterAlternatives`。诊断（消融）：关全部灯 → 全黑；关反射／环境 → 无变化；聚光 ×0.4 仍大面积贴 LUT 上限（≈208），说明白钢“过曝”来自聚光镜面叶 + LDR 无 tonemapping 剪切，不来自环境光。

### 证据

- EditMode 聚焦套件（`SpinnerEnvironmentTests|SpinnerProgressionTests|ProductArchitectureTests|PremiumDisplayCaseTests`）119 项：113 通过，6 失败与本任务无关且在本任务开始前（08:47 结果）已存在：`CollectorRankIsCrossToyManualOnlyAndUsesARealBackButton`、`MagneticSlideUsesSpatialEdgeCuesAndFiniteCrossingTremor`、`RuntimeAndLiquidGlassUi_AreWiredForGrowthAndOfflineReturn`（Swift 源字符串断言，工作区已有未提交 Swift 改动）、`RatchetAudioIsPhysicsDrivenAtomicPolyphonicAndNeverScheduled`、`EveryProductSceneInstallsItsBackgroundAndHarmonizedModelLights`（ledge glow 2.8 vs 1.08）、`ParallaxMathUsesDeadZoneExponentialSmoothingAndPixelAccurateProjection`。
- 模拟器录屏 [V12]：Unity `BuildIosSimulatorProject` → `xcodebuild` Release-iphonesimulator（`Builds/iOS/Logs/consolidation-r001-simulator-export.log`、`consolidation-r001-xcodebuild.log`）→ `Tools/LibraryDetailConsistency/capture_library_detail_simulator.py --round r002`（iPhone 17 Pro `5BF378DF`，app sha256 见 `r002-simulator-capture.json`）→ `compose_library_detail_sheet.py`。产物：`Artifacts/LibraryDetailConsistency/r002/r002-library-detail-sheet.png`、四段 `r002-<model>-library-to-detail-clear.mp4`。列表分页点 4 个，四款均无圆环，推牌库／详情倍率一致，GEEONE 库／详情同亮度。
- GEEONE 光照预设对比 [V13]：`Assets/Editor/GeeoneLightingOptionsPreviewCapture.cs`（`Tools/Codex/Capture GEEONE Lighting Options`）→ `Artifacts/GeeoneLighting/r001/r001-geeone-lighting-options-sheet.png` + `presets.json`。静态渲染，因为只比较灯光配方；用户选定后重录模拟器。

### 2026-09-09 15:04 追加：四场景共用 +0.15 EV 相机分级、推牌背景对齐（`FDB-PREF-037`）

用户 10:51“为什么感觉磁吸推牌的背景更亮一些”；14:57“把其他三款也加 +0.55 EV。这个EV是什么单位，能不能加的非常subtle”；15:04“可以”。

- **根因（三层，均已量化）**：
  1. 推牌 `MagneticSlideShippingLightingController` 独有 `postExposure +0.55 EV`（×1.46）作用于整帧，其余三场景无 Volume → 岩壁 31.8 vs 16.5 灰阶。
  2. 推牌不在 `UsesSoftSpinnerLighting` 名单，`SpinnerImageBasedLightingController` 背景光晕倍率走 `1.0`，三款陀螺走 `SoftEnvironmentGlowScale 0.38`；运行期探针 `_GlowColorA` 推牌 0.84 vs GEEONE 0.097 → 模型下方的大片灰绿雾团（详情 haze 145 vs 63）。
  3. `SpinnerAdaptiveBackdropRules.Restrain` 只限 HSV V，青色 accent 的线性亮度比粉／石墨高 22%。
- **实现**：新增 `SpinnerSharedPresentationGrading`（`PostExposureEv = 0.15`（×1.11）、Neutral tonemap、单个 camera Volume priority 50），`SpinnerEnvironmentPresenter.Install` 对四场景统一安装；`MagneticSlideShippingLighting` Balanced 改为 rev 5：`PostExposureEv = SpinnerSharedPresentationGrading.PostExposureEv`，Key 0.68→0.90、Fill 0.54→0.71（补回 0.40 EV = ×1.32，只落在模型灯），`EnsureVolume` 复用共享 Volume；`MeshyEDC.unity` 序列化灯强度同步。`ResolveEnvironmentGlowScale(modelId)`：推牌与陀螺同为 0.38，扇牌保留 pedestal 路径。`Restrain` 追加 `MaximumLuminance 0.50`。
- **测试**：`SpinnerEnvironmentTests.EveryProductSceneSharesOneSubtleCameraGrading`（四场景 HDR/后处理开、Volume 唯一、EV/tonemap 相等、光晕倍率相等、accent 亮度差 <0.01）；`MagneticSlideLightingRevisionTests.BalancedLighting_HasNeutralToneMapAndMeasuredLift` 改验 rev 5 值与 ×1.32 关系。聚焦套件 104 项 97 通过，7 失败均为既有／环境（Swift 字符串断言 3、`Ratchet…`、`ParallaxMath…`、`EveryProductSceneInstallsIts…` 2.8 vs 1.08、MCP WebSocket 日志）。
- **证据 [V14]**：模拟器 r005 `Artifacts/LibraryDetailConsistency/r005/r005-library-detail-sheet.png` + 四段 `*-library-to-detail-clear.mp4`；背景灰阶（library 岩壁 / 台面；detail 台面）：GEEONE 17.8/50.1/93.4，石墨 17.3/49.9/93.3，推牌 17.5/50.1/93.4，扇牌 17.1/49.6/101.1（r002 推牌为 31.8/81.3/139.6）。导出／构建日志 `Builds/iOS/Logs/grading-r005-*.log`。
- **GEEONE 高光“死白”的真正原因（供用户决策，未改）**：`Assets/_Fidgeting/Generated/ThreeBladeVolume.asset` 三个组件为 null（`ThreeBladeSceneBuilder.ConfigureVolume` 用 `profile.Add<T>()` 但未 `AddObjectToAsset`，从未持久化），且 iPhone 走 `Mobile_RPAsset`：`m_SupportsHDR: 0`、`m_ColorGradingMode: 0 (LDR)` → 渲染目标在后处理前就钳到 1.0，任何 tonemapper 都无法压回高光。因此“柔”只能靠减灯（`FDB-PREF-036` B/C/D），或另立决策把 Mobile 管线切到 HDR + HDR 分级（影响四款外观、需重新批准）。
- 推牌 Gate 12 灯光值从 rev 4 变为 rev 5，属已批准模型的可见改动：**视觉批准待确认，未推送手机**。

### 2026-09-09 16:42 追加：Mobile 管线切 HDR（`FDB-PREF-038`），GEEONE 预设需在 HDR 下重选

用户 16:42“切吧”。

- **改动**：`Assets/Settings/Mobile_RPAsset.asset` `m_SupportsHDR 0→1`（`m_HDRColorBufferPrecision 0` = R11G11B10，32 bit，带宽与旧 RGBA8 相同）、`m_ColorGradingMode 0→1 (HDR)`；`PC_RPAsset.asset` 分级同步为 HDR。`MobilePerformanceBudgetTests.MobilePipeline_PreservesSixtyFpsHeadroomWithCheapHdrBuffer` 改验 HDR 开、32 bit、HDR 分级。60 fps 真机预算未重测。
- **影响实测（模拟器 r006，与 r005 同镜头）**：石墨／推牌／扇牌 p99 不变（170 / 96 / 194），背景 +0.5 灰阶；GEEONE 明显变化：rev-007 的直射 ×3.10 等补偿是为 LDR 钳位调的，HDR 下同一配方过曝（详情 ≥245 白像素 0→5.1%，列表 0→9.9%，p99 212→253）。
- **编辑器预览路径不可用于 HDR 调光**：`GeeoneLightingOptionsPreviewCapture`（`SubmitRenderRequest` 到 ARGB32 RT）在 LDR/HDR 分级下输出逐像素相同（max 214），与真机不符；GEEONE 灯光 A/B 必须在真实 app 里做。
- **新增运行期预览钩子**（与 Swift `--fidgeting-preview-enter-detail-after=` 同族）：`-fidgeting.preview.geeoneLighting <id>`、`-fidgeting.preview.geeoneDirectScale <f>`（iOS 走 NSUserDefaults→PlayerPrefs；编辑器／macOS 用 `--fidgeting-preview-geeone-lighting=` / `--fidgeting-preview-geeone-direct-scale=`）。`GeeoneLightingPresetCatalog.ResolveLaunchPreset` 只缩放四盏直射灯，不动柔光箱／环境；测试 `SpinnerEnvironmentTests.GeeoneLightingPreset_LaunchArgumentsSelectPresetAndScaleOnlyDirectLights`。
- **HDR 下四预设 + A×0.5 / A×0.3 模拟器真实截图 [V15]**：`Artifacts/GeeoneLighting/r004-hdr/r004-hdr-geeone-lighting-options-simulator.png`（列表卡 + 详情各 6 列）、单图 `<label>-{library,detail}.png`、`results.json`。A×1.0 列表卡几乎一片白；A×0.3 / B / C / D 刻面可读、高光有形状。出货仍为 A×1.0，等用户选。
- 待用户选定后：把该预设（含缩放）写成新的 `Shipping` 常量、重录四款、更新 `FDB-PREF-036` 为 Locked。**视觉批准待确认，未推送手机。**

### 2026-09-09 18:07 追加：用户选定 B 柔光棚为 GEEONE 出货光照（`FDB-PREF-036` Locked）

- 用户原话“我感觉柔光棚好看一点”（对 [V15] HDR 对比表）。
- **改动**：`GeeoneLightingPresetCatalog`：`ShippingId = SoftStudioId`，`Shipping` 为 `SoftStudio` 别名（聚光 0.30/0.22/0.18、相机补光 0.26、环境 ×3.20、环境底 ×0.95、柔光箱 0.42，直射总能量 0.96）；旧 rev-007 配方改名 `StudioBright`（`studio-bright`），仅保留在 `All` 供 A/B 对照，不出货。`SpinnerImageBasedLightingController` 的 `Geeone*` 镜像常量同步（新增 `GeeoneAmbientFloorScale`、`GeeoneStudioSoftboxIntensity`）。`GeeoneShippingPreviewCapture` 与运行时同读 `Shipping`，无需改动。
- **测试**：`SpinnerEnvironmentTests.GeeoneLightingPresets_ShipSoftStudioAndKeepStudioBrightOnlyForReview`（出货 = soft-studio、常量镜像一致、旧配方直射 >2.5× 且无柔光箱、Overcast/LowKey 仍更暗）、`GeeoneLightsIdenticallyInLibraryAndDetail` 环境底改按 `GeeoneAmbientFloorScale` 校验。聚焦套件（SpinnerEnvironment / MobilePerformanceBudget / ProductArchitecture）62 项 57 通过，5 失败均为既有（Swift 字符串断言 2、`Ratchet…`、`ParallaxMath…`、`EveryProductSceneInstallsIts…` 2.8 vs 1.08）。
- **模拟器录屏 [V16]**：`BuildIosSimulatorProject`（`Builds/iOS/Logs/softstudio-r007-simulator-export.log`）→ `xcodebuild` Release-iphonesimulator（`softstudio-r007-xcodebuild.log`）→ `capture_library_detail_simulator.py --round r007`（iPhone 17 Pro `5BF378DF`，app sha256 见 `r007-simulator-capture.json`）→ `compose_library_detail_sheet.py`。产物：`Artifacts/LibraryDetailConsistency/r007/r007-library-detail-sheet.png`、四段 `r007-<model>-library-to-detail-clear.mp4`、`r007-<model>-{library,mid,detail}.png`。
- **实测（r006 Studio Bright → r007 Soft Studio，模型区亮度 >60 像素）**：列表卡 ≥250 白像素 10.8%→6.3%、均值 156→140；详情 10.9%→4.9%、均值 140→124。其余三款与 r006 逐帧一致（未改）。
- **视觉批准待确认，未推送手机。** 60 fps 真机预算（HDR）未重测。

### 待办

- 用户对 [V16] r007 四款给出视觉批准 → 手机构建（Build 48）→ 真机验收；`FDB-PREF-036` DeliveryState 仍为 Integrated & Tested。
- 视觉批准前不推送手机；`pointed-three-blade` / `gold-four-wing` 场景资产保留作 rollback。

## 2026-09-08 Gacha carousel R051：切档拖影、镭射同步、星芒粒子、六档配色、slab 图案

> **当前状态：用户 12:16 反馈 R050「太有漂浮感」「镭射亮片和包装动画不同步、横滑时有拖影」「粒子原色实心点密集恐惧，要星芒或软发光，不要大圆套小圆，速度也要随档位加快」「六档包装颜色太相近，拉不开价格」；12:23 追加「包装图案太抽象、圆滚滚，和开包出现的 slab 形状比例不符，静态图案要再改几版」。五项已改完并录屏。12:55 用户看三版候选后指 `outline` 版「这版好一点，但是饱和度可以降低一点」——已把 `outline` 装入 shipping 资源并降饱和重录（R051b）；13:20 追问「能不能用贵金属色在后面几个 pack 增加高级感，中间这个黑块是什么」——黑块是回填算法缺陷已修，高档位徽记与印字改为贵金属箔（R051c）；13:28「比例能再加大一点吗」——slab 徽记 170 → 184 px（R051d）；13:33「特别糊」——光栅改为 768×1024 二倍输出、旧徽记残影改用平铺颗粒回填、预览改为全分辨率录屏（R051e）；13:51「所有字和图案都看不清，需要重新做……pack 再扁平一些，更贴合 slab 形状」——弃用 384 px 照片源，袋体、封口、颗粒、徽记、文字全部程序化绘制，袋形改为 280×375 扁平袋（R051f）；14:55「完全没有厚度了……上下边缘加一点锯齿，暗示可撕开」——加回枕形鼓度、内容物凸起、封口褶皱，顶/底封口边缘锯齿化（R051g）；15:03「风格越改越土，铝箔纸的高级感完全没了，像破纸片」——放弃纯程序化哑光表面，铝箔回到照片源（2×、回填、压窄），程序化只负责起伏、锯齿、徽记与文字（R051h）；15:28「占比大一些」——舞台 Pack 244→280 pt、选中 scale 1.0、选包页间距收紧（R051i）；15:43 选包页文案改版：标题=档位名、副标题=奖池说明、底部=人民币价格、白底购买按钮（R051j）；15:53 去掉右上「选择 PACK」标签、统一 Oxanium（R051k）；15:58 价格白色、标题 title2／说明 footnote、下移 16 pt、加 page control、购买文字单色、不做 dock（R051l）；17:10「中间这个图案还是不太好看，有没有陀螺相关的，极简一点的，有漂亮的曲率和粗细线条的对比」——出六版候选，18:33 用户「这两个通过」批准 A 指尖陀螺轮廓 + C 陀螺仪环（R051m，已装入 shipping 光栅）。徽记图案已获用户批准；选包页 UI 与整体视觉批准待确认，未推送手机。**

- 拖影根因（`PackCarousel`）：`ProductMatchedGeometry` 的 `if let id` 与 `ProductPackIdleFloat` 的 `if let sheenMaskAssetName` 都是按「是否选中」切换的 `@ViewBuilder` 分支。选中变化时整只 Pack 视图身份改变，SwiftUI 在 snap 弹簧期间对新旧两份做默认淡入淡出，于是出现两只半透明 REFINED 重叠滑动（`Artifacts/PackTearNativeCandidate/r051-foil-sync/r050-ghost-before.png` 第 4–7 帧）。
  - 修复：`ProductMatchedGeometry` 单分支，未选中用 `fallbackID: "gacha-pack-slot-<i>"` + `isSource: false`；镭射 overlay 对六只 Pack 常驻（未选中为 rest pose，opacity 0.30）。修后 30 fps 抽帧 `snap-frames-30fps.png` 每帧每只 Pack 只出现一次。
- 镭射同步（`GachaPackHolographicSheenRules.carouselOffset`）：光源固定于屏幕，Pack 每向右滑一格，亮片在印刷上反向移 `0.45` 包宽，clamp ±0.90；`ProductPackIdleFloat` 改为 `Animatable`，`carouselPosition` 与 offset 走同一根 snap 弹簧，不再在选中索引跳变时突跳。Reduce Motion 下保留（它跟随用户已做的滑动，不是自发运动）。
- 漂浮感：`idleFloatAmplitudePoints 6 → 3`、`idleYawDegrees 4 → 2`，周期 2.4/3.2 → 3.0/3.6 s；生命感交给档位敲击与镭射视差。
- 粒子（`GachaPackBackdropAmbienceRules` + `ProductPackBackdropAmbience`）：全部改为径向渐变软发光（核心 35% 内实、其后衰减到 0，无硬边）；最近一层（depth > 0.8）画四角星芒（spike = 3.2 × 半径 × twinkle，腰 0.45 pt），删除 2.8× 光晕圆盘。上升速度 `riseSpeedScale` STANDARD 1× → 1.25/1.55/1.9/2.3 → 1 OF 1 2.8×；视图在 `onChange(of: tier)` 用 `travel(travelAtChange:secondsSinceChange:tier:)` 累积行程，切档只改斜率不改位置；sway/twinkle 仍走时钟，与档位无关。1:1 裁切 `motes-one-of-one-closeup.png`。
- 六档配色：`storefrontAccentRGB` 改为 银 (0.58,0.60,0.64) / 蓝宝石 (0.30,0.55,0.85) / 玫瑰金 (0.88,0.40,0.42) / 香槟金 (0.90,0.74,0.28) / 紫晶 (0.56,0.36,0.86) / 黑曜石+全光谱→玫红 (0.86,0.46,0.80)，与 `GachaPackArcBackdropRules.Colourway` 同一套；harness 断言任意两个彩色档色相差 ≥ 40°、RGB 距离 ≥ 0.30。
- 包装光栅（新工具 `Tools/GachaPackArtwork/build_pack_artwork.py`）：中性源图保存在 `ArtSource/GachaPacks/Neutral/`（原六张 body/flap 此前只存在于 `Assets/Plugins/iOS/GachaPacks/`，未入库；STANDARD body SHA-256 `ebc17bb2…4681d6`）。流程：① 用面板自身高频纹理回填旧浮雕徽记（中值滤波掉轮廓像素，低频取周围面板）；② 按亮度做三色调（shadow/mid/high）分级，中间调向灰回拉 22–34% 保持金属感，1 OF 1 黑曜石叠对角全光谱（仅亮褶带色）；③ 浮雕 slab 徽记：展示盒真实比例 188:240，高 170 px 居中面板，顶部标签板 8.5%–31% H、圆形凹槽直径 84/188 W 居 64% H，顶左键光浮雕，档位色描边；④ 输出 body / flap / foil（foil = slab 外壳 ∪ 原文字掩膜，复用 `build_pack_foil_masks.text_mask`）。三版：`outline`（只描边）、`plate`（实体外壳+标签板+凹槽）、`toy`（凹槽内加三叶陀螺剪影）。候选联系表 `Artifacts/PackTearNativeCandidate/r051-pack-artwork/pack-artwork-variants-sheet.png`。
  - R051b（用户 12:55 选 `outline`、要求降饱和）：脚本默认 `--variant outline`；`DESATURATE` 中间调向灰回拉 REFINED 0.55 / SIGNATURE 0.46 / CHASE 0.44 / GRAIL 0.60（原 0.34/0.24/0.22/0.32），1 OF 1 光谱强度 0.40 → 0.30。六张 body 并排 `r051-pack-artwork/outline-desat-six.png`；Simulator 录屏 `Artifacts/PackTearNativeCandidate/r051b-outline-desat/r051b-outline-desat.mp4`（20.5 s 六档往返，540 宽）+ `strip.png`。Swift 预览重新 `BUILD SUCCEEDED`（`/tmp/r051/swift-build2.log`）；规则代码未改，harness 结论不变。
  - R051c（用户 13:20）：① 「黑块」根因——`inpaint_emblem` 用归一化高斯（σ 22、默认 4σ 截断）从洞外取低频，洞中心 ≥ 4σ 处权重被 1e-4 下限截住，除出一块偏黑的矩形，正好落在凹槽圆环内。改为 `distance_transform_edt` 让洞内每像素先取最近洞外像素再模糊；纹理高通 σ 6 → 3，旧徽记残影同时减弱。② 贵金属箔 `METALS`：REFINED 银、SIGNATURE 玫瑰金、CHASE 黄金、GRAIL 紫晶配黄金、1 OF 1 铂金；STANDARD 保持平涂灰。`metal_ink` 为对角明暗 + 高光带，用于徽记描边与印字（`metallize_text` 复用 foil 文字掩膜）。描边宽度与浮雕深度按 `STROKE_SCALE` 1.0/1.0/1.15/1.3/1.3/1.45 递增。六张并排 `Artifacts/PackTearNativeCandidate/r051c-metal-foil/metal-six.png`（下排为面板 1:1 放大）；录屏 `r051c-metal-foil/r051c-metal-foil.mp4`（20.5 s）+ `strip.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build3.log`）。
  - R051d（用户 13:28）：`SLAB_HEIGHT` 170 → 184（面板内高 194 px，上下各留 5 px），宽随 188:240 变为 144 px。六张并排 `Artifacts/PackTearNativeCandidate/r051d-slab-184/slab-184-six.png`；录屏 `r051d-slab-184/r051d-slab-184.mp4`（20.5 s）+ `strip.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build4.log`）。
  - R051e（用户 13:33「特别糊」）：两个成因。① 资源分辨率：舞台 Pack 244 pt = 3× 屏 732 px，而光栅只有 384 px，运行时放大 1.9×。现在 `build_pack_artwork.py` 以 `S = 2` 输出 768×1024（源图 Lanczos 放大 + UnsharpMask r2/60%，徽记、金属箔、印字全部在 2× 上绘制；所有像素常量按 S 缩放，文字掩膜在 384 画布检测后 zoom 到 2×）。Swift 只用画布比例分数（`authoredCanvasWidth/Height` 384/512 仅作比例），文件名不变，不需改代码。② 预览视频此前缩到 540 宽，本身就糊；R051e 起交付全分辨率 1206×2622 crf 17。另：旧徽记的软阴影比任何中值窗都宽，改为把整个面板洞的高频颗粒替换成印字上方素面（384 画布 96–122 行）的镜像平铺（确定性 seed 7），残影消失。证据：设备像素尺度六档 `Artifacts/PackTearNativeCandidate/r051e-hires/hires-six-device-scale.png`（下排 1:1 裁切）、全分辨率抽帧 `chase-frame-fullres.png`、录屏 `r051e-hires/r051e-hires-clear.mp4`（20.6 s）；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build5.log`）。生成耗时 ≈ 30 s/六档。
  - R051f（用户 13:51）：`build_pack_artwork.py` 重写为纯程序化。① 袋形：384×512 画布不变（Swift 只用比例分数），袋体列 52–332、fin 行 45–92（flap 光栅 45–101 重复袋体顶行）、袋底 467，袋面 280×335 ≈ 0.84，接近 slab 188:240；顶/底封口 3 px 波纹压痕、7 px 侧封、5 px 圆角、边缘 7 px 卷边压暗、单条柔和斜向光带、细颗粒 ±0.022 + 斑驳 ±0.007，整体平坦无鼓包。② 徽记：slab 高 212（居袋面），描边 2.4/1.3/1.3/1.7 px × `STROKE_SCALE`，4× 超采样矢量描边，右下 0.9 px 硬阴影 + 左上 0.6 px 亮唇，贵金属 ink 不变。③ 文字：DIN Condensed Bold（macOS Supplemental 系统字体，光栅化进资源，字体文件不入包）14 px「FIDGET ARCHIVE / SERIES 01」+ 22 px 档位名，字距 0.06 em，同一 ink 压印。④ foil 掩膜 = 徽记 ∪ 文字精确 alpha，不再检测。⑤ 1 OF 1 光谱改跟随模糊后的光场，去掉彩色噪点。Swift 同步：`openingInsetFraction` 0.05 → 48/384、`authoredFlapSpanFraction` 24–360 → 52–332、`authoredPackInteriorWidthFraction` 0.875 → 280/384；harness 新增 Python/Swift 常量一致断言，`PASS 239/239`。`ArtSource/GachaPacks/Neutral/` 与 `Tools/GachaPackFoilMask/` 不再参与生成，保留为历史。证据：六档 `Artifacts/PackTearNativeCandidate/r051f-flat-pouch/flat-pouch-six.png`、设备尺度 GRAIL `grail-device-scale.png`、全分辨率抽帧 `frame-fullres.png`、撕包近景 `tear-closeup.png`（fin 整条剥离、无 crimp ears）、录屏 `r051f-flat-pouch-clear.mp4`（22.5 s 六档 + 3.2 s `--pack-tear-candidate-preview` 撕包）；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build6.log`）。生成耗时 ≈ 12 s/六档。
  - R051g（用户 14:55）：① 厚度——袋面枕形鼓度 `PILLOW_GAIN` 0.17（中央亮、四边暗，椭圆平方根轮廓）；内部 slab 顶起铝箔的软凸起 `CONTENT_BULGE` 0.085（徽记外扩 6 px 圆角矩形，σ 9 px）+ 右下 `CONTENT_SHADOW` 0.11；上下封口与袋面交界处聚拢褶皱 `CREASE_GAIN` 0.08（暗谷 3 px + 亮脊 8 px，沿 x 11 px 周期起伏）；卷边压暗 0.22 → 0.28。② 锯齿——`serrated_band()` 在 fin 顶边（行 45）与袋底边（行 467）切出 8 px 间距、4.5 px 深的三角齿，齿向内切，外沿行号不变，Swift `authoredPackTopYFraction` 等常量不受影响；卷边压暗跟随齿形，齿有立体感。证据：六档 `Artifacts/PackTearNativeCandidate/r051g-volume-serration/six.png`、设备尺度+齿边放大 `six-device-scale-detail.png`、全分辨率抽帧 `frame-fullres.png`、撕包近景 `tear-closeup.png`、录屏 `r051g-volume-serration-clear.mp4`（20.5 s 六档 + 3.6 s 撕包）；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build7.log`）；规则代码未改，harness 239/239 结论不变。
  - R051h（用户 15:03）：混合管线。铝箔来自 `ArtSource/GachaPacks/Neutral/` STANDARD body+flap 合成照片：Lanczos 2× + UnsharpMask r2/60%；`inpaint()` 回填旧徽记（行 188–380、列 94–294）与烘入文字（SERIES 行 120–176、档位名行 386–422）——低频取最近未动像素（σ 14），高频用 fin 下方素面（行 104–120、列 60–324，避开侧封边缘）镜像平铺、幅度夹 ±0.05；列 24–360 压到 52–332（行不动）。光场 = (照片亮度 / 0.42)^0.9 × 程序化起伏（枕形 0.10、内容凸起 0.085、褶皱 0.04、卷边 0.20、锯齿），再走档位双色调；程序化颗粒/压痕降到 0.006/0.05 避免与照片重复。slab 徽记回到照片浮雕框内（高 188，顶 186）。第一版颗粒库含 fin 底边（行 96–101）与侧封边缘，平铺后在面板里出现周期性「蝴蝶」痕，已换行/列范围修掉。证据：六档 `Artifacts/PackTearNativeCandidate/r051h-foil-hybrid/six.png`、设备尺度 CHASE/GRAIL/1 OF 1 `six-device-scale-detail.png`、全分辨率抽帧 `frame-fullres.png`、撕包 `tear-closeup.png`、录屏 `r051h-foil-hybrid-clear.mp4`（20.5 s 六档 + 3.2 s 撕包）；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build8.log`）；规则代码未改。R051f/g 的纯程序化表面记为 superseded。
  - R051i（用户 15:28「让这些包裹在屏幕中的这个占比大一些」）：`GachaPackOpeningRules.artworkWidthPoints` 244 → 280（选中 carousel ≈ 237 pt ≈ 屏宽 60%，原 178 pt ≈ 45%）；`tearTravelPoints` 158 → 181（commit 仍落在包宽 40%）；`GachaPackCarouselRules.selectedPackScale` 0.86 → 1.0、`unselectedPackScale` 0.56 → 0.62；选包页 `VStack` 间距 15 → 8 pt、标题/档位说明各减 4 pt 留白。证据：`Artifacts/PackTearNativeCandidate/r051i-larger-pack/frame-fullres.png`、`r051i-larger-pack-clear.mp4`（20.5 s）；harness `PASS 239/239`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build9.log`）。
  - R051j（用户 15:43）：`GachaPackTier.storefrontCashPriceCNY` 6/12/24/32/64/128（SIGNATURE 24 为推断，用户只给了 6/12/32/64/128），`storefrontPriceLabel` = `¥{n}`；`storefrontOddsLine` 改为奖池说明，删除「四档奖品池不变」；`ProductScreenHeading` 标题=`tier.title`；`ProductPackTierCaption.title` 显示价格；`ProductPrimaryActionButton` 新增 `surface: .filledWhite` 与 `titleGradient`。harness 新增价格标签与文案断言 `PASS 245/245`；录屏 `Artifacts/PackTearNativeCandidate/r051j-storefront-copy/r051j-storefront-copy-clear.mp4`。
  - R051k（用户 15:53）：右上 `ProductStatusTag("选择 PACK")` 为旧占位，删除，仅失败提示时显示；`productDesignSystem()` 与预览 App 启动时注册 Oxanium（预览曾回退系统字体）；`ProductBottomActionDock` 加 `tint` 参数。录屏 `r051k-bottom-dock/r051k-bottom-dock-clear.mp4`（dock 版随后被用户 15:58 取消）。
  - R051l（用户 15:58）：价格 `accent: .white`；`ProductScreenHeading` 新增 `subtitleStyle`，选包页标题 `.title2`／说明 `.footnote`、整块下移 16 pt；`ProductPageIndicator(items: GachaPackTier.allCases)` 置于价格上方（选中白色胶囊 18 pt、未选 6 pt 圆点，随 `selectedPack` 切换）；购买文字去渐变改单色 accent；不用 dock。录屏 `r051l-page-control/r051l-page-control-clear.mp4`；harness `245/245`；Swift 预览 `BUILD SUCCEEDED`。
  - R051m（用户 17:10 / 18:33）：`build_pack_artwork.py` 徽记改为局部 8 px/单位 SDF 光栅（`_EmblemRaster`：布尔形状 → 有向距离 → 精确宽度描边，圆角并集用高斯阈值做 fillet，变宽笔画用扫掠多边形）。六版候选 A 指尖陀螺轮廓／B 陀螺侧影／C 陀螺仪环／D 轴承+甩动弧／E 实心陀螺／F 陀螺+轨道（`r051m-emblem-gyro/emblem-candidates-sheet.png`、`zoom-grid-A-E.png`、`full-packs-A-E.png`），用户批准 A + C。`EMBLEMS`：STANDARD/REFINED/SIGNATURE = spinner（hub r40 + 三叶 r33 距 46、fillet 9、粗 3.2 描边；轴承环 r15 与叶环 r15 细 0.9；轴心实点 r4.5），CHASE/GRAIL/1 OF 1 = gyro（外环 r70 粗 3.2；万向椭圆 66×22 倾 −28° 细 0.9；轴半长 76 由中间 0.9 向两端 0.35 收细；轴心实点 r5.5）；粗细均 × `STROKE_SCALE`。旧 slab 徽记代码删除，`slab_geometry()` 只保留供内容凸起用。foil 掩膜自动跟随。证据：六档 `r051m-emblem-gyro/six.png`、徽记 1:1 `six-emblem-1to1.png`、录屏 `r051m-emblem-gyro-clear.mp4`（20.5 s）、抽帧 `frame-chase.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build11.log`）；harness `245/245`。B/D/E/F 记为 superseded 候选。
  - R051n（用户 18:48 四点）：① 「动画卡、不跟手」——`GachaPackCarouselRules.detentHoldGain` 0.7 → 0.92（单档规则已由 release 保证，不再靠压位移），`PackCarousel` 拖动 `minimumDistance` 12 → 6 pt，`ProductPackIdleFloat` 新增 `suspended`：拖动期间暂停镭射 TimelineView（body 已按触点重算，双重刷新只增渲染负担）；真机帧率仍待装机验证。② 图标参考（四张锐角星芒/收尾 swoosh 参考图）——新出六版候选 G 轨道 swoosh+星／H 星芒陀螺仪／I 交叉 swoosh／J 实心三叶+星芒镂空／K 三段 swoosh／L 双轨道陀螺仪，星芒用 n=0.55 超椭圆（凹边、真尖角），swoosh 用变宽扫掠（尖头→粗腰→尖尾）；`Artifacts/PackTearNativeCandidate/r051n-emblem-swoosh/zoom-grid-G-L.png`、`full-packs-G-L.png`。19:39 用户「icon 都没替换」——装入 K（STANDARD/REFINED/SIGNATURE：三段变宽 swoosh r70 跨 100°、峰值 0.28、最宽 9 × `STROKE_SCALE`，四芒星 r30 转 15°）+ H（CHASE/GRAIL/1 OF 1：78×27 细轨道 1.2×0.9、竖向星芒 22×86、横向星芒 52×10），`_EmblemRaster` 新增 `star4`／`crescent`；旧 spinner/gyro 常量删除。六档 `six.png`、徽记 1:1 `six-emblem-1to1.png`、录屏 `r051n-emblem-swoosh-clear.mp4`（21.9 s）、抽帧 `frame-grail.png`/`frame-refined.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build13.log`）。20:01 用户「每个 pack 有一个自己的图标」→ R051o：`EMBLEMS` 六档各一：STANDARD K 三段 swoosh／REFINED J 实心三叶+星芒镂空／SIGNATURE G 倾斜变宽轨道+星／CHASE I 交叉 swoosh+长星芒／GRAIL L 双轨道+两段粗弧／1 OF 1 H 星芒陀螺仪；`_EmblemRaster` 新增 `tapered_ring`（闭合变宽环 = 内外两多边形 XOR）。六档 `r051o-emblem-per-tier/six.png`、徽记 1:1 `six-emblem-1to1.png`、录屏 `r051o-emblem-per-tier-clear.mp4` + `strip.png`、抽帧 `frame-grail.png`/`frame-refined.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build14.log`）。22:21 用户「整体色相饱和度过高，像零食，不够高级」→ R051p 全链路降饱和：① 袋体 `GRADES` 中间调改为哑光金属（REFINED 钢蓝 (0.22,0.32,0.46)／SIGNATURE 灰玫瑰铜 (0.52,0.32,0.30)／CHASE 古铜金 (0.58,0.47,0.24)／GRAIL 茄紫 (0.34,0.24,0.44)），`DESATURATE` 0.35/0.35/0.35/0.40，`METALS` 高光压低，1 OF 1 光谱 0.22 → 0.16；② Swift `storefrontAccentRGB` 同步为 (0.40,0.52,0.68)/(0.70,0.42,0.44)/(0.76,0.64,0.40)/(0.50,0.40,0.64)/(0.68,0.50,0.64)；③ `GachaPackStorefrontBackdropRules` 底部光晕 `saturationBoost` 2.4 → 1.3、`maximumSaturation` 0.85 → 0.55、`minimumValue` 0.62 → 0.52；④ `GachaPackArcBackdropRules.Colourway` 五套弧带色全部改为哑光金属（蓝宝石 → 钢蓝 2A4A72/3E6A96、玫瑰金 → 82482E/B8735E、香槟金 → 8C7440/BC9E4E、紫晶 → 4A3468/7B5E9E + 金心 C9A85A、银 6F7A88/B4BCC6）。harness 阈值随之调整：accent 两两 RGB 距离 ≥ 0.30 → ≥ 0.15（色相 ≥ 40° 不变）、弧带两两 ≥ 0.25 → ≥ 0.15、玫瑰金 glow 红通道 > 0.9 → > 0.6、香槟中心 > 0.95 → > 0.9；`246/246`。证据：六档 `r051p-muted-metals/six.png`、录屏 `r051p-muted-metals-clear.mp4` + `strip.png`、抽帧 `frame-chase.png`/`frame-grail.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build15.log`）。音效候选：`Artifacts/GachaSfxCandidates/kenney-cc0/`（Kenney CC0，71 条，按 01 切档吸附／02 购买确认／03 撕包／04 盒子滑出／05 落地翻面／06 稀有度提示／07 失败返回 分组，ogg + m4a），未接入运行时。 ③ 购买按钮——`ProductPrimaryActionLabel.titleOpacity`：`.filledWhite` 底板在 disabled/loading 下保持纯白，只淡化文字（原来整块 0.42 透明发灰）；`.glass` 行为不变。「点不动」代码上唯一路径是 `ProductActionState.disabled`（券 0 且硬币 < 160，价格行显示缺口）或 `loading`（Unity 目录未到达）；Simulator 预置资金无法复现，需用户确认真机钱包/构建版本。④ 「返回后首页进入按钮消失」——`CodexSwiftUIOverlayManager.setGachaPresentationActive(true)` 把 `panelController.view.isHidden = true`，回到 false 时只调 `selectTab` → `showPanel()`，而 `showPanel` 在 panel 已存在时直接 return，面板永久隐藏。修复：恢复前显式 `panelController?.view.isHidden = false`；`GachaStorefrontIntegrationTests` 新增字符串断言。证据：harness `246/246`（新增 hold gain ≥ 0.9 / 0.1 间距处 ≥ 0.09 断言）；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build12.log`）；Simulator 截图 `r051n-storefront.png`；录屏 `r051n-emblem-swoosh/r051n-tracking-clear.mp4`（22.4 s 六档往返，1206×2622 crf 17）+ 抽帧 `frame-grail.png`。Unity EditMode 未重跑（仅新增字符串断言）。视觉批准待确认，未推送手机。
  - R051q（用户 22:31 六点）：① 「硬挺感、降饱和、金属感」——`build_pack_artwork.py`：`PILLOW_GAIN` 0.10 → 0.06（袋面更平）、`CREASE_GAIN` 0.04 → 0.06、`CONTENT_SHADOW` 0.11 → 0.13、新增窄高光条 `SPECULAR_GAIN`/`SPECULAR_WIDTH` 0.20/0.045 叠在软 sheen 上、光场绕 1.0 拉伸 `METAL_CONTRAST` 1.30、照片褶皱 `PHOTO_GAMMA` 0.9 → 1.15、`DESATURATE` 0.45/0.45/0.42/0.48。② 标题上方反白小徽记——脚本新增导出 `gacha-pack-<tier>-emblem.png`（400 × 400 白底透明，裁 `EMBLEM_BOX`）+ Unity `.meta` + Xcode 预览工程资源；`GachaPackTier.emblemAssetName`；`ProductScreenHeading.emblemAssetName` 以 `FidgetUITokens.Size.headingEmblem` 28 pt、0.92 不透明置于标题上方；storefront 传 `selectedPack.emblemAssetName`。③ page control 上移 16 pt（指示器 `.padding(.bottom, 16)`）。④ 描述文案移到价格下——heading `subtitle` 置空；`ProductPackTierCaption` 新增第三行 `footnote`（footnote 字号、tertiaryText 0.42），现在为 `¥32` → 概率描述 → `一张抽取券 · 余 8 张`。⑤ 圆形渐变同步——`GachaPackBackdropRippleRules.seconds` 1.3 → 0.7、`backdropFollowDelaySeconds` 0.55 → 0.12、`backdropFollowSeconds` 0.6 → 0.5。⑥ 跟手与 snap 阻尼——`detentHoldGain` 0.92 → 1.0（完全 1:1）、拖动 `minimumDistance` 6 → 3 pt、`snapStiffness` 420 → 300 / `snapDamping` 38 → 40（ζ ≈ 1.15 略过阻尼、更沉）；真机手感仍需装机验证。harness 新增 3 条（1:1 + ζ ≥ 1.05 + k ≤ 320；光晕 ≤ 0.8 s / 延迟 ≤ 0.15 s；六档 `emblemAssetName`），`0.2 间距处 <` 改为 `<=`；`PASS 249/249`。`GachaStorefrontIntegrationTests` 新增六档 emblem 文件与字符串断言（Unity EditMode 未重跑）。证据：六档接触表 `Artifacts/PackTearNativeCandidate/r051q-metal-heading/six.png`、录屏 `r051q-metal-heading-clear.mp4`（22.5 s）+ `strip.png`、抽帧 `frame-chase.png`/`frame-grail.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build16.log`）。视觉批准待确认，未推送手机。
  - R051r（用户 22:43「褶皱感再弱一点，金属感和硬挺感再强一些，icon 适当放大」）：`build_pack_artwork.py` 照片亮度先高斯 `PHOTO_SMOOTH` 1.4 px 抹平细褶，`PHOTO_RELIEF` 0.85 → 0.60、`PHOTO_GAMMA` 1.15 → 1.0（不再放大褶皱），对比改由 `METAL_CONTRAST` 1.30 → 1.55 与高光条 `SPECULAR_GAIN` 0.20 → 0.30 提供；`PILLOW_GAIN` 0.06 → 0.03、`CREASE_GAIN` 0.06 → 0.03、`GRAIN_FINE` 0.006 → 0.004。标题徽记 `FidgetUITokens.Size.headingEmblem` 28 → 36 pt（袋面徽记未动）。harness 不受影响（`249/249`）。证据：`Artifacts/PackTearNativeCandidate/r051r-stiff-metal/six.png`、录屏 `r051r-stiff-metal-clear.mp4`（22.5 s）+ `strip.png`、抽帧 `frame-chase.png`/`frame-grail.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build17.log`）。视觉批准待确认，未推送手机。
  - R051s（用户 2026-09-09 08:02「icon 的圆角矩形内再加一层淡淡的背景，随镭射光反射变化」）：`build_pack_artwork.py` 新增 `plate_mask(shell)`（压花面板内缩 3、圆角 10、边缘 σ 1.2 px 柔化）；袋体在面板内向 tier 高光色（半去饱和）混 `PLATE_TINT` 0.10 × 对角渐变 0.55–1.0，读作一层淡膜；foil 掩膜 `PLATE_FOIL_ALPHA` 0.22 叠入面板（徽记/文字仍 1.0），`ProductPackHolographicSheen` 以 alpha 遮罩 → 镭射光带扫过面板时淡淡带亮。这修正了 2026-09-07 17:22「foil 只在徽记与文字」的约束：面板以 0.22 弱强度参与，属用户本轮明确要求。证据：`Artifacts/PackTearNativeCandidate/r051s-panel-film/six.png`、录屏 `r051s-panel-film-clear.mp4`（22.5 s）+ `strip.png`、抽帧 `frame-chase.png`/`frame-grail.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build18.log`）。harness/EditMode 无规则改动。视觉批准待确认，未推送手机。
  - R051t（用户 09-09 08:28「膜延展到四个角的对焦框；表面更平整，不然破破烂烂」）：`plate_mask` 由 shell 内缩 3 改为外扩 6、圆角 12，与照片压花面板的四角对齐（同 `light_field` 的 `inner`）；`PHOTO_RELIEF` 0.60 → 0.35、`PHOTO_SMOOTH` 1.4 → 2.6 px、`GRAIN_FINE` 0.004 → 0.002，只保留大褶。证据：`Artifacts/PackTearNativeCandidate/r051t-flat-panel/six.png`、录屏 `r051t-flat-panel-clear.mp4`（22.5 s）+ `strip.png`、抽帧 `frame-chase.png`/`frame-grail.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build19.log`）。视觉批准待确认，未推送手机。
  - R051u（用户 09-09 08:32 圈出左上大折光「把这个熨平」）：根因是 `light = (photo/0.42)^γ × (...) × relief` 里照片亮度始终全强度相乘，`PHOTO_RELIEF` 只调过程性浮雕的占比，所以前几轮降 relief/加模糊都压不住照片本身的左上高光褶。改为 `photo_term = 1 + ((photo/0.42)^γ − 1) × PHOTO_RELIEF`，再乘过程性 relief；0.35 权重下左上区域基本平整，金属感由 `METAL_CONTRAST`/高光条维持。证据：`Artifacts/PackTearNativeCandidate/r051u-ironed/six.png`、录屏 `r051u-ironed-clear.mp4`（22.5 s）+ `strip.png`、抽帧 `frame-chase.png`/`frame-grail.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build20.log`）。视觉批准待确认，未推送手机。
  - R051v（用户 09-09 08:39「面板膜去掉，有点丑；或整个 pack 都过光、icon 更亮；饱和度大幅降低」）：① R051s/t 面板膜 rejected——`plate_mask`、`PLATE_TINT`、`PLATE_FOIL_ALPHA` 删除，袋体不再烘焙面板底色；foil 掩膜改为整个袋体 `BODY_FOIL_ALPHA` 0.18 + 徽记/文字 1.0，镭射光带扫过整袋、经过徽记时全亮。② 袋体 `DESATURATE` 0.45 → 0.72/0.72/0.70/0.74；金属 ink 新增 `INK_DESATURATE` 0.30（金/玫瑰金/银向灰拉 30%）。③ Swift `storefrontAccentRGB` 再向自身亮度拉 ~35%：REFINED (0.44,0.52,0.62)／SIGNATURE (0.63,0.45,0.46)／CHASE (0.73,0.65,0.49)／GRAIL (0.48,0.42,0.57)／1 OF 1 (0.66,0.51,0.62)；`GachaPackStorefrontBackdropRules.saturationBoost` 1.3 → 1.1、`maximumSaturation` 0.55 → 0.38。harness accent 两两 RGB 距离 ≥ 0.15 → ≥ 0.10（色相 ≥ 40° 不变；REFINED–GRAIL 现为 0.12），`PASS 249/249`。证据：`Artifacts/PackTearNativeCandidate/r051v-whole-sheen-muted/six.png`、录屏 `r051v-whole-sheen-muted-clear.mp4`（22.5 s）+ `strip.png`、抽帧 `frame-chase.png`/`frame-grail.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build21.log`）。视觉批准待确认，未推送手机。
  - R051w（用户 09-09 08:48 圈出六袋左上斜向亮痕「褶皱太强，大幅降低这个 dent」）：亮痕 = `SPECULAR` 窄高光条叠在照片残余折光上。`SPECULAR_GAIN/WIDTH` 0.30/0.05 → 0.08/0.10（变成宽而淡的渐变），`PHOTO_RELIEF` 0.35 → 0.15。金属感现在主要由运行时镭射光带（整袋 0.18 + 徽记 1.0）提供。证据：`Artifacts/PackTearNativeCandidate/r051w-flat-dent/six.png`、录屏 `r051w-flat-dent-clear.mp4`（22.5 s）+ `strip.png`、抽帧 `frame-chase.png`/`frame-grail.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build22.log`）。视觉批准待确认，未推送手机。
  - R051x（用户 09-09 08:54「白色羽化模糊背景去掉；整包太哑光，镭射感更强；学习 https://github.com/LerSent001/holo-card」）：① `CONTENT_BULGE`/`CONTENT_SHADOW` 0.085/0.13 → 0，徽记后的浮起面板光与投影删除。② 学习 holo-card `renderer.js` 的光栅模型并移植到 `ProductPackHolographicSheen`：余弦调色板光谱 `.52+.48·cos(2π(t+(0,⅓,⅔)))`、相位随视角（band offset）滑动（`spectrumPhaseGain` 1.9、`spectrumCycles` 2.4、`spectrumOpacity` 0.62）、光带包络在上、白色激光芯保留、26 个固定位置的四角星 glint 只在光带内闪（`glintEnvelope` = (1−2|d|)²）；`restOpacity` 0.30 → 0.45、`sweepOpacity` 0.78 → 0.95；foil 掩膜整袋份额 `BODY_FOIL_ALPHA` 0.18 → 0.30（0.40 试过，把 tier 色淹没）。skill 已安装到 `~/.codex/skills/holo-card`（其分层 parallax/contour glow 面向网页卡，本项目只借用光栅着色模型）。harness 新增 4 条（光谱有界且到达红/蓝、倾斜改变颜色、glint 位置/包络、rest<sweep≤1），`PASS 253/253`。证据：`Artifacts/PackTearNativeCandidate/r051x-holo-sheen/six.png`、录屏 `r051x-holo-sheen-clear.mp4`（21.7 s）+ `strip.png`、抽帧 `frame-chase.png`/`frame-grail.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build24.log`）。视觉批准待确认，未推送手机。
  - R051y（用户 09-09 09:06「holo card 里有更多陀螺仪 feature 和卡片 frame design，学 https://x.com/LerSentAI/status/2097006824318738660」；09:17 附 AI 光晕参考图「这种级别的光晕可以考虑加上」）：抽帧分析该推文两段视频（`viewer.js` 陀螺仪：相对基准的 β/γ×0.85、夹 ±28°、按屏幕方向旋转、0.115 lerp；`renderer.js`：前景按 `view·0.08·depth` 视差、背景反向、随视角的 `glare`、轮廓 bloom、金色同心卡框吃光谱）。移植：① 印层分离——`build_pack_artwork.py` 新增 `print_layer()`，徽记/字样/面板细框（`FRAME_GROW/RADIUS/STROKE` 6/12/0.8，holo-card 卡框的小袋版）导出为独立 `gacha-pack-<tier>-print.png`（每档 5 文件），body/flap 只留裸箔；`GachaPackTier.printAssetName`、`ProductPackPrintLayer` 按 `printParallax`（满偏 3.5% 宽，竖向 ×`verticalTiltWeight`）相对箔面移动，`ProductPackSealedArtwork`/`ProductPackTearRevealLayer`/预览 App 全部接线。② 陀螺仪倾角 9/6 °/g → 34/22 °/g（gravity≈sin θ，近 1:1），新增夹角 `tiltYawClampDegrees` 22 / `tiltPitchClampDegrees` 14。③ `ProductPackGlare`（仅选中包）：随视角的白色热芯 0.9/半径 5%、光谱色边 0.35、宽 halo 0.18、水平镜头光条 0.4（长 2.0 宽、厚 2%），sweep 时整体 ×1.35。④ `ProductPackContourGlow`（选中包/撕包待机）：袋形剪影模糊 18 pt，白色 rim 0.8 + 光谱 0.45，rest 0.55 → sweep 0.95，缩放 1.04。第一版光条为十字且画在每个包上，被自审为「瞄准镜」，改为仅选中包 + 单向光条。harness 更新倾角断言并新增 print 视差/glare/contour 断言，`PASS 257/257`；Unity `GachaStorefrontIntegrationTests` 新增 print.png 存在与接线断言（未在本轮运行 Unity EditMode）。证据：`Artifacts/PackTearNativeCandidate/r051y-holo-depth/r051y-holo-depth-clear.mp4`（22.5 s，scripted tilt）+ `frame-4s.png`/`frame-12s.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build26.log`）。真机陀螺仪耦合仍待 iPhone 验证。视觉批准待确认，未推送手机。
  - R051z（用户 09-09 09:58「光晕很假，高光点要有强反光材质承载；雾面不会有横线高光；三处在晃；镭射光带与图形彼此独立；扩散再宽；drop shadow 按 tier 色更深更扩散、subtle；四边缘要显出里面 slab 轮廓」）：① `build_pack_artwork.py` 新增 `rim_mask()`：袋形轮廓内 0.8 单位起 3.2 单位宽的金属边（tier 金属油墨，压印深度 0.35，进 print 层与 foil 掩膜 1.0），高光有了落点；`BODY_FOIL_ALPHA` 0.30 → 0.16，雾面袋身只吃宽而弱的过光。② slab 边缘：`SLAB_RIDGE_GAIN` 0.09（宽 2.2）+ 外侧阴影 0.07（偏 4、宽 5）+ 平台抬升 0.02，用有符号距离场沿面板轮廓做出厚度感，与印层细框重合。③ `ProductPackGlare` 去掉横向光条、halo；只剩一枚宽软高光（半径 16% 宽、0.55）+ 微弱光谱边 0.22，掩膜改为 print 层（金属才有高光）。④ 白色 contour glow 删除，改为 `ProductPackTintedShadow`：tier accent ×0.7 的袋形剪影，模糊 36 pt、缩放 1.08、下落 12 pt、rest 0.62 → sweep 0.85，普通混合。⑤ 光带 `bandWidthFraction` 0.55 → 0.85，激光芯 0.28 → 0.18 带宽；印层视差 0.035 → 0.02，减少「第三个在晃的东西」。harness 更新高光/阴影/带宽断言，`PASS 258/258`。证据：`Artifacts/PackTearNativeCandidate/r051z-metal-rim/r051z-metal-rim-clear.mp4`（22.5 s）+ `frame-5s.png`/`frame-13s.png`；Swift 预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build27.log`）。视觉批准待确认，未推送手机。
  - R052a（用户 09-09 10:15「围绕 icon 的金边加到蓝框位置，把内容都框进来，加点小修饰花纹，只用圆角有点普通」）：`frame_mask()` 重写为整面装饰框 `FRAME_BOX`（侧封内 4 单位、y 104–421，位于 flap 行 92–101 之下），直边 0.9 + 6 单位切角、每角内藏一枚 3 单位四角星（与徽记同一超椭圆族）、内侧 3.2 单位 0.45 细线在角部收口、四边中点各一枚 2.4 单位菱形并断线 4 单位。徽记外的小面板框取消（slab 边缘起伏保留作厚度）。字样内移：HEADLINE 108/126 → 118/136，TITLE_TOP 392 → 382。框、星、菱形全部进 print 层与 foil 掩膜，随倾斜吃高光。无 Swift 改动；预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build28.log`）。证据：`Artifacts/PackTearNativeCandidate/r052a-ornate-frame/r052a-ornate-frame-clear.mp4`（22.4 s）+ `frame-5s.png`/`frame-13s.png`。视觉批准待确认，未推送手机。
  - R052b（用户 09-09 10:54「把 slab 凸起轮廓和内细描线合成同一个框、一样大小；slab 外边缘倒角缓和；文字内移让内外两条线拉开间距」）：新增 `INNER_BOX` = `FRAME_BOX` 内缩 11 单位、圆角 9，同时驱动印层内细线（连续圆角环，0.45）与箔面 slab 起伏（脊光 0.08/宽 3.2，外侧阴影 0.06/偏 5/宽 7，更缓）；原按 `slab_geometry()` 的 188:240 小面板起伏取消。角星仍藏在外框切角与内框圆角之间。字样内移：`TEXT_X` 76 → 84，HEADLINE 118/136 → 124/142，TITLE_TOP 382 → 376。无 Swift 改动；预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build29.log`）。证据：`Artifacts/PackTearNativeCandidate/r052b-slab-frame/r052b-slab-frame-clear.mp4`（22.5 s）+ `frame-5s.png`/`frame-13s.png`。视觉批准待确认，未推送手机。
  - R052c（用户 09-09 15:02「内圈 slab 描边和外延间距还是过近，再向内收；改完连同撕包装一起录屏」）：`FRAME_INNER_INSET` 11 → 18（内框/slab 起伏与外框金线净距 18 单位 ≈ 13 pt@280 pt），圆角 9 不变；徽记框 `EMBLEM_BOX` 上移 8（172–372，中心 272）让 1 OF 1 星底与档位名保持 ≥ 10 单位；字样随内框内移：`TEXT_X` 84 → 91，HEADLINE 124/142 → 131/149，TITLE_TOP 376 → 369。无 Swift 改动；预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build30.log`）。证据：`Artifacts/PackTearNativeCandidate/r052c-inner-frame-tear/r052c-inner-frame-tear-clear.mp4`（14.2 s：前 10.9 s `--premium-display-case-gate12-preview` 一镜到底 STANDARD→REFINED→STANDARD→选包→摇晃过光→0.32 s 撕开→白闪交接；后 3.3 s `--pack-tear-candidate-preview` 慢速撕包近景）+ `frame-stage.png`/`frame-tear.png`/`frame-slowtear.png`。视觉批准待确认，未推送手机。
  - R052d（用户 09-09 15:23「撕开时有一块黑色不明物体；撕开后锯齿的银色描边依然存在，不符合定理」）：① 银边残留——运行时印层 `print.png` 与镭射掩膜 `foil.png` 都不参与撕裂，此前却覆盖 fin 行 45–92，撕开后金属边和过光仍留在原位。`build_pack_artwork.py` 把印层与 foil 全部裁到 seam 行 92 以下；fin 那段锯齿银边烘进 `flap.png`，随盖片一起飞走（sealed 外观不变，合成图仍完整）。② 黑块——是 R033 契约里的开口内腔 `ProductPackSlitCavity`（近黑 0.04–0.075 渐变），在白闪浅底上读成黑条。新增 `GachaPackOpeningRules.interiorLipScale/MidScale/DepthScale` = 0.55/0.36/0.26 × tier accent：内腔变成从内侧看到的本袋铝箔（上唇受光、向下变深），`ProductPackTearRevealLayer.interiorTier` → `ProductTearablePackArtwork.interiorTier` 传入；店面与预览 app 均传当前 tier，nil 时保持旧中性色。harness 新增内腔明度阶梯断言，`PASS 259/259`；预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build31.log`）。证据：`Artifacts/PackTearNativeCandidate/r052d-tear-mouth/r052d-tear-mouth-clear.mp4`（18.2 s：gate12 一镜到底 + 慢速撕包）+ `frame-stage.png`/`frame-lid.png`（盖片带锯齿银边飞离）/`frame-flash.png`（白闪底上无银边残留、无过光鬼影，内腔为灰色铝箔内侧）。视觉批准待确认，未推送手机。
  - R052e（用户 09-09 16:24/16:25「这个黑块是什么」「撕开的边缘感觉比卡包靠后，不在一个 Z 轴」）：黑块 = R033 开口内腔 `ProductPackSlitCavity`，10 pt 深色带在白闪浅底上读成黑块，且袋身顶边只是裸切口、后面是暗腔，所以撕口像凹在包装后面。改法：① 袋体金边改按 `body` 而非 `pouch` 计算（`rim_mask(body)`），印层金边沿 seam 行 92 闭合——密封时是 fin 下一条压边线，撕开后袋口是同平面的带边箔口；fin 自己的锯齿边仍烘进 `flap.png`。② `maximumOpeningHeightPoints` 10 → 5（开口是两层箔之间的缝，不是腔），`openingHeightPoints(0.4)` 6.45 → 3.23；③ 内腔色阶 `interiorLip/Mid/DepthScale` 0.55/0.36/0.26 → 1.0/0.84/0.7 × tier accent，成为受光的箔内侧浅灰唇。harness 与 `GachaNativeHybridCandidateTests` 常量字符串同步（`= 5`），harness `PASS 259/259`；预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build32.log`）。证据：`Artifacts/PackTearNativeCandidate/r052e-mouth-plane/r052e-mouth-plane-clear.mp4`（15.7 s：gate12 一镜到底 + 慢速撕包）+ `frame-stage.png`/`frame-lid.png`/`frame-flash.png`。视觉批准待确认，未推送手机。
  - R052f（用户 09-09 17:09「四块边和 front 面没接上、线是断的；撕开后的灰块两角超出 front 面，穿帮」）：① 线断——袋身顶角原为 5 单位圆角，与 fin 的直边在 seam 处形成缺口，金边到角上断开。`pouch_masks()` 把袋身顶角改为直角（与 fin 一致，袋形轮廓在 seam 无缺口），`rim = rim_mask(body)` 后顶边金边与两侧金边成 T 形接合，fin 侧边金边直通 seam。② 灰块穿帮——开口 sliver 用的是撕裂 inset `openingInsetFraction` 48/384（袋外 4 单位，为让盖片带走整条 fin），所以比 front 面宽。新增 `GachaPackOpeningRules.mouthInsetFraction` = 59/384（袋边 52 + 侧封 7）：开口只在两条焊死的侧封之间，`ProductPackMouthMask`/`ProductPackTearPath`/`openingMaskAreaSquarePoints`/`GachaPackMouthRingRules` 改用它；撕裂/盖片仍用 48。灰块本身 = 从开口看到的后片箔内侧（R052e 起为浅灰，非黑），两端按 `openingEndTaper` 收窄，现落在 front 面内。harness 新增 mouthInset 断言，`PASS 260/260`；预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build33.log`）。证据：`Artifacts/PackTearNativeCandidate/r052f-seam-join/r052f-seam-join-clear.mp4`（14.0 s：gate12 一镜到底 + 慢速撕包）+ `frame-stage/lid/flash.png` + `corner-detail.png`（密封/撕开的 seam 角 3× 放大）。视觉批准待确认，未推送手机。
  - R052g（用户 09-09 17:52「加点质感和纵深的阴影/高光，现在太平了」+ 17:53「外框切角能用圆角过渡吗」）：① 袋口箔面 `ProductPackSlitCavity`（仅 tier 非 nil 时）叠四层：`ProductPackFoilGrain`（Canvas 逐行确定性明暗细纹，`interiorGrainOpacity` 0.16）、左→中一道宽光泽（`interiorGlossOpacity` 0.22）、前片撕边投到后片上的阴影（底部 40%→100% 渐深，`interiorEdgeShadowOpacity` 0.45）、后片折边受光细线 `ProductPackMouthLipEdge`（沿开口上沿描 1 pt，`interiorLipHighlightOpacity` 0.8）。仍不透明，符合 R033。② 外框四角 `FRAME_CHAMFER` 6 直切改为 `FRAME_ARC_R` 8 四分之一圆弧，与边相切；角星位置不变，仍藏在弧内。harness 新增质感常量区间断言，`PASS 261/261`；预览 `BUILD SUCCEEDED`（`/tmp/r051/swift-build34.log`）。证据：`Artifacts/PackTearNativeCandidate/r052g-mouth-foil/r052g-mouth-foil-clear.mp4`（14.2 s：gate12 一镜到底 + 慢速撕包）+ `frame-stage/lid/flash.png` + `mouth-detail.png`（撕开后袋口 3×）+ `frame-corner.png`（圆角 3×）。备注：首次录制时另一进程在同一 Simulator 上启动了完整 Unity app（`com.jiaweizhou.fidgetspinner.codex`）抢占前台，已重录。视觉批准待确认，未推送手机。
  - R052g 批准 + 整体录屏（用户 09-09 18:12「可以了，然后加上那个 slab 出现那个动画一起，总体录个屏」）：R052g 视觉获用户明确批准，设计圣经新增 `FDB-GAC-040`（DecisionState User Approved），批准资产复制到 `Docs/DesignBibleAssets/gacha-pack-r052g-*.png`。整体录屏用完整 Unity Simulator app（复用另一任务 18:15 的 `Builds/iOS/FidgetingAppSimulator` export → `/tmp/grading-sim-build` Release build，Swift/PNG 与 workspace 逐字节一致；等待其 Simulator 录制结束后再录）：`xcrun simctl launch … --premium-display-case-gate12-preview`，`Artifacts/PackTearNativeCandidate/r052g-mouth-foil/r052g-full-flow-clear.mp4`（30 s：Unity 启动 → STANDARD/REFINED carousel → 选包 → 摇晃过光 → 撕开 → slab 从袋口升起、Pack 下退 → 三叶金属陀螺 3D 揭晓）+ `full-flow-frame-case-rise.png`/`full-flow-frame-reveal.png`/`full-flow-handoff-sheet.png`。DeliveryState：Simulator 预览已批准，未推送手机、真机验收待定。
  - R053（用户 09-09 18:58：背板丑/材质怪、撕开瞬间渐变与粒子消失、标签配色丑改英文单字体去 LEVEL/FDT、展示改龙鳞模型、镭射效果加到标签与 bottom sheet）：① 背景连续：`FidgetAppCoordinator.HandleGachaShippingFrontRevealed` 向 Swift 发 `front-revealed`，`GachaPackPresentationRules.ambienceVisibility` 让粒子留到舞台亮起后按 `ambienceFadeSeconds` 淡出；交接快照含 `ProductPackBottomGlowGrowth(settled: true)` 的底部光晕。② 奖品：`PremiumDisplayCaseSceneBuilder.BuildThreeBladeDisplayPrize` 改为直接实例化 `GeeoneTriSpinner.fbx`（`Rotor_Root`→`RotorVisual`，`Cap_Top/Cap_Bottom/Hub_Core`→`HubVisual`，材质 `M_GeeoneSatin/M_GeeoneDiscTurned/M_GeeoneHubDark`，无碰撞体，localRotation Euler(0,0,180) 使 Cap_Top 朝观众、12 点叶片朝上，不再挂 ReflectionProbe）；`GachaShippingRevealDirector.GeeoneBodyEmissiveScale` 0.12 只给 `Rotor_Body` 微量稀有度自发光，避免白团。③ 标签：`GachaPrizeDefinition` 新增 `plateName/plateEdition`（GEEONE TRI-SPINNER / SATIN STEEL · DRAGON SCALE），`GachaShippingLabelAuthority` 去掉 `LEVEL n`，`ShowsCollectibleIdOnPlate = false`；新 shader `PremiumDisplayCaseLabelHoloFoil`（拉丝金属 + 视角/倾斜光谱带）+ `PremiumDisplayCaseLabelFoil` 倾斜驱动 `_SheenPhase`，`PremiumDisplayCaseGate12LabelRestyle.Apply` 把 Gate12 R004 prefab 文字换成 Oxanium 深墨、左对齐。④ 结果页：`GachaNativeBridge.ReceiptPayload` 交易回执追加 plateName/plateEdition（14 格，非交易回执仍 10 格），`GachaReceiptRow.resultTitle`/`GachaRarityTier.plateTitle`，`GachaRevealResultCopy` 只出英文（标签 `IN COLLECTION`，副标题 `HEIRLOOM · SATIN STEEL · DRAGON SCALE`）；`ProductPackHolographicSheen` 抽出共享 `ProductHoloFoilBand`，新增 `ProductHoloFoilSheen`（`surfaceStrength` 0.7）/`ProductHoloFoilText`（0.9），`ProductStatusTag`、`ProductBottomActionDock`、`ProductScreenHeading` 接受 `sheenPose`；`packMotionPhase` 在 `.handoff/.complete` 继续喂设备姿态。`ProductPackMouthLipEdge` 改名 `ProductPackInteriorFoldEdge`（袋内后片折边，非 R032 外唇线）。证据：EditMode `PremiumDisplayCaseGate12Tests|PremiumDisplayCaseTests|GachaNativeBridgeTests|GachaNativeHybridCandidateTests` 64 通过 / 2 ignored / 0 失败（`/tmp/r053/editmode.xml`）；`CodexUnityLabEditor.IosBuildPipeline.BuildIosSimulatorProject` export 12:52Z + `xcodebuild` Release `BUILD SUCCEEDED`（`/tmp/r053/sim-build`）；卸载重装后 `xcrun simctl launch … --premium-display-case-gate12-preview` 录屏 `Artifacts/PackTearNativeCandidate/r053-heirloom-reveal/r053-full-flow-clear.mp4`（44 s：Unity 启动 → STANDARD/REFINED carousel → 摇晃过光 → 撕开时粒子与底部光晕保留 → slab 升起 → 峡谷舞台 GEEONE 龙鳞陀螺 + 英文箔面标签 → 结果页 tag/标题/dock 随倾斜过光）+ `full-flow-frame-{carousel,case-rise,reveal,result-sheet}.png`。备注：首次录制沿用了前一次被中断启动留下的待处理交易，App 直接进入 `.handoff` 且舞台全黑，卸载重装后正常；该恢复路径下舞台不渲染为待查问题。背板形状/材质（R005/R006 slab 方向）由并行任务处理，见上文 Gate12 R005 条目。视觉批准待确认，未推送手机。
- 证据：Swift 规则 harness `PASS 238/238`（新增 carousel 视差、Reduce Motion 视差保留、idle ≤ 3 pt/2°、riseSpeedScale 单调且 ≤ 3×、行程连续、星芒仅最近层、色相分离）；Swift 预览 `xcodebuild` `BUILD SUCCEEDED`（`/tmp/r051/swift-build.log`）；Simulator 录屏 `Artifacts/PackTearNativeCandidate/r051-foil-sync/r051-foil-sync-clear.mp4`（24.9 s：实速六档往返 + STANDARD→REFINED、GRAIL→1 OF 1 两段 0.35× 慢放；904×1966 crf 17），`contact-sheet.png` 每 1.5 s 一帧。
- 未做：Unity EditMode 未重跑（本轮无 C# 改动）；图案版本待用户从三版中选定；真机验收待视觉批准后装机。

## 2026-09-07/08 Gacha carousel R049–R050：背景粒子、底部渐变生长、单档吸附、开包失败即回退

> **当前状态：用户 19:39 提出四点——背景要有效果（粒子/过光）、真机一开包就卡住、切档时底部渐变要有从下向上的入场、snap 太弱容易滑两档；22:41 反馈 R049「粒子太大、整屏斜向过光假、没看到 ripple」。R050 已按反馈改完并录屏（本条由接管线程完成，原线程 `2e7782a0` 因上下文过大、多次被新消息中断而停摆）。视觉批准待确认，未推送手机。**

- 真机「一开包就卡住」根因：`GachaInventory.PrepareDraw` 在 0 张抽取券时返回 `insufficient-tickets` 失败收据，Unity 写回 `lastFailureReason`，但 shipping storefront 从不读取它，只等 20 s 收据超时，期间状态文字被隐藏 → 用户看到撕开的包停在原地。Simulator 有 preview token 预置 8 张券，所以从未复现。
  - 修复（`GachaPackPaymentRules`）：付费方式 `tickets ≥ 1 → 券`，否则 `coins ≥ 160 → 硬币`（`singleDrawCoinCost` 与 C# `GachaEconomyRules.SingleDrawCoinCost` 由 EditMode 断言保持一致），两者都不足则 CTA 置 disabled、价格行显示「抽取券不足 · 硬币 N/160」。
  - `onChange(of: model.lastFailureReason)` → `handleDrawFailure`：立即 `gate.reset()`、撕口/鼓口/退场归零、退出 gacha stage、恢复渐变底，`ProductStatusTag` 显示原因 3.2 s。20 s 超时路径保留为真正无响应时的兜底。
  - 新增 `--gacha-no-funds-preview` 启动参数：不预置资金，Simulator 可复现空钱包路径。
- 单档吸附（`GachaPackCarouselRules`）：拖动映射改为磁性 detent 曲线（`detentHoldGain 0.7`，过 42% 间距前压住位移），提交条件 `|Δ| ≥ 0.42 × 间距` 或预测终点 `≥ 140 pt` 快甩，每次释放最多 ±1 档；落位弹簧 `k 420 / c 38`（近临界阻尼）。
- 背景（`GachaPackBackdropAmbienceRules`）：R050 首版细尘 `0.11–1.04 pt`、alpha 0.13–0.34 在 3× 屏与 h264 下完全消失（用户 09-08 07:13「粒子效果又没了」）。改为按深度分布：半径 `0.8 + 1.8·depth^2.4`（大多数 0.8–1.3 pt 细尘，最近 ~20% 为 2.0–2.6 pt 白芯 bokeh 带 2.8× 光晕），alpha `tier(0.72→1.0) × (0.38 + 0.5·depth) × twinkle`，数量 36→84；颜色用档位色向白提 45%（`dustRGB`，否则 STANDARD 银灰在黑底上不可见）；深度与横向位置按黄金比分层，低档较少的粒子也覆盖全深度。R049 的整屏斜向过光已删除（用户：假）。
- 底部渐变生长（`GachaPackBackdropRippleRules` + `ProductPackBottomGlowGrowth`）：每次切档在 `.id(tier)` 上重建，所选色从底部 `0.96 H` 一条小种子（x 0.16 / y 0.035）线性 1.3 s 按 ease-out³ 长成 `1.6 W × 0.8 H` 椭圆，峰值 0.92 → 稳态 0.46，跟随一圈 1.2 pt 回声弧；上方色相底与弧带延迟 `0.55 s` 再用 `0.6 s` 跟上，保证颜色先在底部出现再向上铺开。R049 版是整屏圆形遮罩且渐变中心落在屏外 25%，肉眼几乎不可见——这是用户「没看到 ripple」的直接原因。
- 证据：Swift 规则 harness `PASS 220/220`；Swift 预览 `xcodebuild` `BUILD SUCCEEDED`（`r051e-swift-build.log`）；Unity EditMode 聚焦 `26/26`（`editmode-v2s.xml`；`GachaStorefrontIntegrationTests.ShippingStorefrontKeepsNavigationTicketEconomyAndRevealWiring` 改为断言 `GachaPackPaymentRules.priceLine(` / `handleDrawFailure` 接线，旧 `storefrontPriceLabel` 断言过期）；Simulator 录屏 `Artifacts/PackTearNativeCandidate/r050-backdrop-growth/r050-backdrop-growth-clear.mp4`（实速 17.4 s 六档往返 + REFINED→SIGNATURE、GRAIL→1 OF 1 两段 0.35× 慢放），10 fps 抽帧 `growth-strip-10fps.png` 可见 0.2–0.6 s 内暖色从底部升起、上方仍为蓝色；`motes-standard.png` / `motes-top-tier.png` 为 STANDARD 与 1 OF 1 的 1:1 像素裁切，细尘与 bokeh 均可见。
- 未做：真机复现「开包卡住」修复（需装机，待视觉批准）。

## 2026-09-07 Gacha carousel R048：档位阶梯——越贵的 Pack 越「迫不及待」

> **当前状态：用户 18:54 要求「除了背景以外，carousel 越往后滑、越贵的 pack 越 be more ready，从浮动节奏上有 wriggling / shaking、迫不及待想破壳而出的感觉」。已实现并录屏。视觉批准待确认，未推送手机。**

- 规则（`GachaPackTierLadder`，`FidgetGachaPackPresentation.swift`）：六档单调递增。
  - 敲击脉冲：STANDARD 无；REFINED→1 OF 1 间隔 4.2/3.2/2.4/1.8/1.3 s，脉冲时长 0.55→0.85 s，横向 1.2→6.0 pt，滚转 0.8→5.0°，鼓胀 0.4%→2%，11 Hz 衰减正弦 × 正弦包络；脉冲之间完全静止；相邻档相位错开 0.37 s。
  - 到位：往贵的方向翻页时新 Pack 先升 3→8 pt 再落回（0.55 s）；往便宜方向只平滑滑入。
  - 触感：翻页 snap 走语义管线 `EmitGachaCarouselSnapFromNativeUi(signal)` → `FidgetHapticRouter.Emit(DetentCaptured, 0.30→1.0)`，不新增 raw `IosHaptics` 调用。
  - 撕封前的舞台 Pack 沿用同档的敲击（`ProductPackTearRevealLayer.idleWriggle*`），撕开即停。
  - Reduce Motion：无敲击、无升落。
- 预览：`--gacha-carousel-ladder-preview`（与 gate12 参数并用）自动 STANDARD→1 OF 1 每档停 2.6 s，再退一档；不抽卡。
- 证据：Swift 规则 `202/202`；Unity EditMode 聚焦 `26/26`；Gate 12 Simulator 录屏 `Artifacts/PackTearNativeCandidate/r048-gacha-carousel-tier-ladder/r048-gacha-carousel-tier-ladder-clear.mp4`（实速 15 s + GRAIL、1 OF 1 敲击 0.3× 慢放），30 fps 抽帧 `grail-knock-burst-30fps.png`。像素测量：CHASE 敲击 ±1.5 pt、GRAIL ±2.9 pt、1 OF 1 ±2.9 pt（包络峰）；脉冲间 < 0.3 pt。
- 未做：材质/花纹/文字层级阶梯（用户说背景已够）；真机触感权重待 iPhone 验收。

## 2026-09-07 Gacha reveal v2 R047：渐变底保持到翻转，翻过来那一刻再切到当前场景

> **当前状态：用户要求"选中 Pack 后、卡片出现之前场景都不要换，保持渐变底；直到卡片啪转过来那一刻再切到当前场景"。已实现并重录（pipeline `evidence/12-shipping/rev-015/`）。视觉批准待确认，未推送手机。**

- 做法：Unity 收藏盒在 native 层之下，native 渐变底不能一直盖着，所以在选中 Pack 时 storefront 把当前 native 舞台底（`ProductPackArcBandsBackdrop`，所选 colourway）用 `ImageRenderer`（iOS 15 回退 `UIHostingController` 快照）渲染成 1× PNG，路径随 `EnterGachaStageFromNativeUi` 载荷（`r,g,b,strength|path`）传给 Unity；`GachaRevealStageFX.TrySetBackdropImage` 把它贴在贴合屏幕的 quad 上挡住环境。native 层在 handoff 淡出时下面是同一张图，衔接看不出。过 90° 那帧 quad 在 `StageLightUpSeconds 0.35 s` 内淡出（藏在 flash 后面），露出用户当前的环境场景。
- 渲染顺序修正：洞穴前景岩层 `sortingOrder 1000/1001` 且 `ZTest Always`，而 Unity 透明排序中 sortingOrder 优先于 renderQueue——舞台 quad 提到 1002+，收藏盒所有 Renderer 提到 1010（磨砂壳仍叠在底上），flash 2000。quad 尺寸改用 `Camera.CalculateFrustumCorners`：HeroCamera 的 `fieldOfView` 不是竖直轴，旧的 `2·d·tan(fov/2)` 只覆盖中间一条（这也是此前 75% 压暗从未盖满全屏的原因）。
- `GachaShippingRevealDirector.Begin` 不再 dispose 从 storefront 接管的 stage FX（之前 case 首帧会把底/色相一起丢掉）。
- 验证：Unity EditMode 26 passed（Gate12 + Storefront + Choreography，新增 `TrySetBackdropImage`/`SetStageStrength` 接线断言、`StageLightUpSeconds 0.35`）；Swift harness 138/138；export `gate12-export18.log` Success；`xcodebuild` Release Success（`gate12-xcodebuild21.log`）。录屏 `Artifacts/PackTearNativeCandidate/r047-gacha-reveal-v2-scene-at-flip/r047-gacha-reveal-v2-scene-at-flip-clear.mp4`、`r047-before-after-flip.png`、`r047-sheet.png`；history event `61e9f093-7303-4996-b219-8c12fc03f1f9`。
- 并行线程冲突：本线程曾把文件误写进 `evidence/12-shipping/rev-010`（colourway/镭射线程所有），两支被覆盖的视频已按 hash 从 `Artifacts/PackTearNativeCandidate/r042-gacha-reveal-v2-timeline-canvas` 恢复，本轮改用 rev-015。
- 同轮其他改动（已随 R041 记录）：抽取券在 tier 名上方且字号更小、按钮「购买 {tier}」、抽出 0.78 s / 落位 0.24 s、时间线 canvas `gacha-reveal-timeline.canvas.tsx`（圆角色块、按阶段配色、slider 同色）。

## 2026-09-07 陀螺仪 → 机构 → Haptic 联动：转子框架耦合、Device Twist 拨盘、推牌／扇牌重力与 flick 驱动、甩动 ShakeBurst

> **当前状态：已集成并有测试 · Build 45（0.1.0/45，development）已安装并启动到 iPhone 15 Pro Max · 待真机验收。** 用户指出“陀螺仪和 haptic 并没有产生联动”，对评估给出的四个方向原话“都要”，随后要求“先把这个 haptic 应用到所有的陀螺上面，就把版本推到我手机上，先感觉一下”。设计圣经 `FDB-INT-015`—`FDB-INT-019`、`FDB-HAP-011` 已锁定（source thread `e24a8eac-4683-4277-bb36-d40dbd46a796`，[T32]）。没有新增任何 raw input → `IosHaptics` 或 raw input → router 的 Haptic 调用；全部新触觉由机构语义事件产生。视觉无变化，不涉及模型外观门禁；Build 45 同时携带工作树中其他任务尚未批准的未提交改动（tracked dirty=79，含 Swift overlay、扇牌 lookdev、Gacha），安装不等于这些改动获批。
>
> **Build 45 交付**：job `gyro-haptic-linkage-build45-20260907T111808Z-snapshot`，buildKey `a825eb5f…6a0768`，source digest `cada67dc…4b6b83`，HEAD `62d8bcd`。脚本 `scripts/device_delivery_gyro_haptics.sh`（沿用 Build 42/44 的单写者 snapshot 流程：双锁、受保护源哈希、唯一 `Builds/iOS/DeviceJobs/<job>/Export`、单调 Build 号、签名、安装、启动、console 捕获、`delivery-result.json`）。预检 EditMode 147/147 首轮通过；`PrepareUniqueIosDevelopmentSnapshot` 确认 Build 45；Unity `iOS Device Xcode project created`，export 前后受保护源哈希一致；`xcodebuild` Release `BUILD SUCCEEDED`；`devicectl` install + launch 成功，pid `40947`，console 见 `MagneticSlideDetentAudio.ReportAudioReady` 与 `MagneticSlideTileShippingCoordinator.Awake`。证据目录 `Artifacts/DeviceDelivery/gyro-haptic-linkage/device-delivery/gyro-haptic-linkage-build45-20260907T111808Z-snapshot/`（同目录下两个 `111522Z`／`111638Z` job 为预检被 Unity AI Assistant WebSocket 日志误判打断的失败记录，未消费 Build 号）。无 App Store submission。
>
> **蓝色经典补齐**（本轮）：`FidgetSpinnerController` 新增 `SetDeviceFrameRotationRate / ClearDeviceFrameRotation / ApplyDeviceShakeImpulse`，FixedUpdate 内以 `ApplyDeviceFrameCoupling(magneticMode: false)` 耦合自由轮；甩动冲量成功后由该机构自身 `FidgetHapticRouter.Emit(ShakeBurst)`（与其既有 DetentCrossed／Released 同一路径）。`DeviceMotionController` 新增 `FidgetShakeDetector`，用 `PortraitCameraFramer` 基底与 `Vector3.up` 轴推送框架转速并施加甩动，运动控制器本身不发 ShakeBurst。五款旋转玩具现在全部具备框架耦合 + 拨盘 + 甩动。

- **共享映射** `Assets/Scripts/Product/DeviceMotionMechanismCoupling.cs`：Core Motion 右手系 → Unity 左手系。rotation rate（伪向量）按相机基底映射为 `(−rx, −ry, +rz)`，gravity／userAcceleration（真向量）为 `(gx, gy, −gz)`；`0.06 rad/s` 陀螺死区、`12 rad/s` 限幅、`0.06` 重力力矩死区；`ResolveGravityTorqueNormalized` 给出绕机构轴的归一化力矩，正向等于 Unity 正旋转。
- **B 转子框架耦合**（4 个金属场景）：`FidgetSpinnerMotion.ApplyDeviceFrameCoupling` 纯函数；`RotorRigidbodyController.SetDeviceFrameRotationRate / ClearDeviceFrameRotation`，FixedUpdate 内 `ω_rel −= Δω_phone`，磁吸锁定时随机身共转，`|ω_phone| ≥ magneticBreakawaySpeed (2.2 rad/s)` 才脱档并发 `Breakaway`，脱档瞬间滞后为零，手机仍 ≥ breakaway 时 `_deviceFrameInhibitsCapture` 阻止 capture；手指、AUTO、反向刹车、翻转、kinematic 期间只跟踪不累积。`MetalDeviceMotionController` 每帧用相机基底与 `rotor.SpinAxisWorld` 计算轴向转速并推送。Haptic 只来自转子既有 `Breakaway / DetentCrossed / DetentCaptured` 与高速纹理。
- **A Device Twist 拨盘**（5 个旋转场景）：`Assets/Scripts/Product/DeviceTwistDial.cs` 积分 `rotationRate.z`，24 档／圈、边界 `±1.0°` 迟滞、`30 ms` tick 限流（只丢弃 tick，索引永不延迟）、`5 rad/s` 满强度、double 累计与安全归一化。`MetalDeviceMotionController` 与 `DeviceMotionController` 以 `SemanticEventRaised(TwistDetentCrossed)` 发出机构事件；`FidgetAppCoordinator.ConfigureProductScene` 订阅两者并转交 `FidgetHapticRouter`。让位规则：`rotor.IsDetentTravelActive`（金属）或 `spinner.IsFingerControlling`（蓝色）时不发 tick。`FidgetSemanticEvent.TwistDetentCrossed = 16` 新增，router `Emit` 走独立 isolated transient（`DeviceTwistHapticRecipe` intensity `0.34…0.62`、sharpness `0.56`），不共用转子 Detent 门。
- **D 甩动确认**：`RotorRigidbodyController.ApplyDeviceShakeImpulse(delta, strength)` 取代运动控制器直接 `AddFlickVelocity`；手指／AUTO／翻转／刹车期间忽略；磁吸锁定时按同一 breakaway 速度判定；成功改变状态才由转子 `EmitSemantic(ShakeBurst)`。`FidgetShakeDetector` 阈值不变（`1.55 / 0.65 g`、jerk `8 g/s`、`0.14 s`）。`InertiaShift` 通道不变。
- **C 推牌／扇牌设备驱动**：`EdcDeviceMotionController` 改读 4 参数 `IosDeviceMotion.TryRead`，把世界系 gravity／acceleration／phone angular velocity 推给 `EdcSliderController.SetDeviceMotionSample` 与 `FanCardController.SetDeviceGravity`；手指持有、Library 浏览、离屏时推送“不可用”。它仍不写机构状态、不调用 Haptic。
  - 扇牌：`FanCardMagneticTrack.Step(..., deviceLoad)` 新增设备档；`deviceLoad = 0` 时与批准原型逐位一致（回归测试比对）。锁定井内 `load = deviceLoad` 形成可见预压，`|load| ≥ 0.050` 且 dwell ≥ `0.12 s` 才一次脱一档并把 `captureTarget` 设为相邻井，由既有 release-capture 弹簧送达并以零速度捕获；端点不再脱档。`FanCardController` 用两片活动牌质心（`ResolveMovingCentroidLocal`）与 `transform.up` 求力矩，`FanCardSpecifications.DeviceGravityLoadScale = 0.18`、死区 `0.06`；设备驱动的跨档视为 user-authorized，进入既有 `EmitFanCard` 与金属 click 音频；`deviceTravelActive` 保证放平手机后的收尾跨档仍授权。
  - 推牌（shipping Gate12R002 机构）：新增纯类 `MagneticSlideTileDeviceDrive` + `MagneticSlideFlickDetector`（`Assets/_EDC/Candidates/MagneticSlideTileGate12R002/Runtime/`）。最大行程处顶片为 30 档重力摆（breakaway 力矩 `0.30`、`720 °/s²`／单位力矩、阻尼 `2.2 s⁻¹`、`< 90 °/s` 且落在 `5.4°` 捕获半径且力矩 `< 0.30` 才捕获）并叠加框架耦合（`≥ 2.2 rad/s` 脱档）；角度对齐且静止时沿轨 flick（`1.10 / 0.45 g`、jerk `9 g/s`、`0.25 s` cooldown，方向与加速度相反）以 `0.16…0.32 m/s` 滑到远端。控制器把命令翻译为 `TryBeginRotation / TrySetAngle / TryCaptureNearestDetent / TrySetTravel(…, userAuthorized: true)`，互锁、边缘提示、端点 `Breakaway / DetentCaptured` 与 `DetentCrossed` 全部沿用机构原有语义 → `EmitMagneticSlider`。`MagneticSlideTileShippingMechanism` 暴露 `RotationBrokenAway / IsAngleAligned / RotationAxisWorld / SlideDirectionWorld / ResolveMovingTopLeverWorld()`（renderer 缓存，无 per-frame allocation）。手指开始拖动时 `deviceDrive.Cancel()`。旧 `MagneticDetentTrack1D` 直线路径未接入（非 shipping 场景）。
- **Library／离屏／Reset**：`ApplyLibraryPreviewPose` 对三个运动控制器调用 `SetMechanismDriveEnabled(!libraryPreviewActive)`；`ResetReference`／`SuspendMotion` 清空转子样本、拨盘累计角与 EDC 样本。进度／经济遥测未改：设备驱动不计入 `accumulatedActivityDegrees` 或成长。
- **测试**：新增 `Assets/Tests/Editor/DeviceMotionMechanismCouplingTests.cs` 26/26 Passed（映射符号与死区、拨盘静置 60 s 零 tick／360° = 24 档／迟滞无抖动／限流不延迟索引、框架耦合往返净零与 breakaway／capture 抑制、扇牌零载荷逐位一致／次阈值只预压／持续倾斜逐档到端点／30·60·120 Hz 同档／手指优先、flick 迟滞与方向、滑片到端点、未对齐忽略、重力摆脱档—摆动—零速捕获、次阈值保持、扭转脱档滞后、样本映射、架构字符串门禁）。回归：`ProductArchitectureTests`／`SpinnerEnvironmentTests`／`MobilePerformanceBudgetTests`／`HapticSpeedTextureTests` 中与本改动相关的全部通过；`FanCardAcceptanceTests 23/23`、`EdcSliderAcceptanceTests 9/9`、`MagneticDetentTrack1DTests 16/16`、`MagneticSlideTileGate12R002Tests 8/8`、`FidgetSpinnerMotionTests 38/38`。同一工作树上 5 个与本改动无关的既有失败（Swift overlay 字符串 ×2、`Assets/StreamingAssets` 存在、推牌 framing、灯光数值）来自其他进行中的任务，未处理。
- **仍待**：用户在 Build 45 上真机验证（a）手机绕转子轴转动时转子滞后方向与预期一致——若相反只需翻转 `ResolvePhoneAngularVelocityWorld` 的 z 项；（b）拨盘 tick 与转子棘轮可盲辨；（c）扇牌 `0.18` 与推牌 `0.30` 倾斜阈值、flick 阈值的误触率；（d）静置桌面 60 s 零自运动、零 tick；（e）Library 横滑期间无机构驱动。视觉无变化，无需外观预览批准。Device Acceptance=`pending-user-validation`。

## 2026-09-07 Gacha Pack 镭射箔面 R045→R046：陀螺仪倾斜随动 + 摇一摇镭射过光，镭射只在图案与文字（FDB-GAC-036）

> **当前状态：用户 16:57 问「设备陀螺仪能不能和这个 pack 进行联动，在监测到陀螺仪有晃动的时候，会有镭射的过光效果」并给出 LerSentAI 视差镭射卡参考（R045，rev-013）；17:22 看过整袋镭射后修订「应该只有在中间的图案部分和文字部分做镭射效果」（R046，rev-014）。两轮都已在 shipping storefront 落地并重录 Gate 12。Simulator 没有陀螺仪，录屏用脚本手势跑同一套管线；真机倾斜／摇一摇灵敏度待 iPhone 验收。视觉批准待确认，未推送手机。**

- **R046 foil mask**（17:22 修订）：sheen 的 mask 由整个袋身改为每档 `Assets/Plugins/iOS/GachaPacks/gacha-pack-<tier>-foil.png`（384×512，白色 + alpha）。生成器 `Tools/GachaPackFoilMask/build_pack_foil_masks.py`：emblem 取压印轮廓段（高通 > 14、去 < 20 px 碎片）的凸包（外轮廓为凸形，凸包即完整剪影；模板六档相同，只从 STANDARD 取一次并内缩 1 px）；档位文字取 y 390–418 带内高通 > 22；「FIDGET ARCHIVE／SERIES 01」为暗印，取高通 < −9；均去碎片、膨胀 1 px、0.8 px 软边。重跑逐字节一致。`GachaPackTier.foilAssetName`；`ProductPackHolographicSheen(maskAssetName:)`；`ProductPackIdleFloat.sheenMaskAssetName`；`ProductPackTearRevealLayer.sheenMaskAssetName`（缺省回退袋身）。Xcode export 与预览工具的 `GachaPacks/*.png` 通配自动带上六张 mask。验证：harness 193/193；Unity EditMode 48 passed / 2 skipped（新增六张 foil PNG 与生成器存在性、mask 接线字符串）；export `gate12-export17.log`、`xcodebuild` `gate12-xcodebuild20.log` Success。证据：`Artifacts/PackTearNativeCandidate/r046-pack-holographic-foil-emblem/`（`-clear.mp4`、`r046-stage-sweep-10fps.png`、`r046-six-packs-foil-rest.png`、`r046-foil-mask-overlay.png`）；pipeline `evidence/12-shipping/rev-014/`，history events rev-013 用户意见 + rev-014 ready。录屏实测 T0 ≈ 13.13，reveal 15.9（T0+2.77）。

- **规则**（`GachaPackHolographicSheenRules`，纯函数）：倾斜 → 光带位移 `tiltOffset`（gravity 相对静止姿态的偏移 × 1.6，夹在 ±0.60 袋宽，纵向权重 0.35）与 Pack 随手倾斜（yaw ±9°、pitch ±6°）；无运动时光带随待机 yaw 时钟（±0.22 袋宽）；摇一摇 → `GachaPackShakeDetector`（userAcceleration 模长 ≥ 0.55 g 触发、< 0.18 g 重新武装、1.2 s 冷却——只用 user acceleration + 滞回 + 冷却，符合仓库 shake 约束）→ 一次 0.85 s 镭射过光（`sweepOffset` −1.25 → +1.25 袋宽 easeInOut，`sweepOpacity` 0.30 → 0.78 峰值在 22% → 回落）。`pose(...)` 汇总 idle + tilt + sweep + Reduce Motion（RM：光带静止、Pack 不倾斜、摇一摇只做亮度脉冲）。
- **运动源**（`FidgetGachaPackMotionFeed.swift`，新文件）：`GachaPackMotionFeed` 拉式采样——由 Pack 的 `TimelineView` 每帧调用 `sample(at:)`，无 timer、无每帧 `@Published`；通过 `@_silgen_name` 调 `CodexIosDeviceMotionNativeUiStart/Stop/Read` 复用 Unity 陀螺控制器的同一个 `CMMotionManager`。`CodexIosDeviceMotion.mm` 新增双客户端仲裁（Unity 与 native UI 各一标志，两者都离开才 `stopDeviceMotionUpdates`），任一方离开不会切断另一方。100 ms 低通 + 3 s 基线回中（手停下时光带回到中位）。生命周期：Pack 在屏（choosingPack…preparingCase）start，handoff／complete／receiptRecovery 与 `onDisappear` stop。Simulator `deviceMotionAvailable == false` 时，Gate 12 预览改用脚本手势（3.6 s／5.3 s 正弦倾斜 + `simulateShake()`）。
- **组件**：`ProductPackHolographicSheen`（青→白→品红→金宽柔光带 + 细白激光芯，−26°，`plusLighter`，以袋身 raster 作 mask；封条不受影响，避免飞出后的封条区域被涂亮）；`ProductPackIdleFloat` 新增 `motion / sheenBodyAssetName / reduceMotion`（carousel 只给选中 Pack）；`ProductPackTearRevealLayer` 新增 `idlePitchDegrees / sheenPose`；撕封开始后 sheen 冻结。
- **预览脚本**（仅 Gate 12）：carousel 每档停留时 `simulateShake()` 一次；选中后台上停 1.8 s 并摇一次再撕封，T0 相应后移，拍点相对 T0 不变。预览工具补 `@_cdecl` 桩（无 .mm），`project.yml` 加入新文件并 `xcodegen generate`。
- **验证**：Swift harness 192/192（新增 13 条：位移夹取、倾斜角、待机相位、低通权重、sweep 进度／位移／不透明度、pose 四态、shake 滞回与冷却、脚本手势幅度）；Unity EditMode 48 passed / 2 skipped（新增 `PackHolographicSheenFollowsDeviceMotionWithShakeSweep`，含 `.mm` 仲裁、feed 无自建 `CMMotionManager`、storefront 生命周期；`SpinnerEnvironmentTests.ProductCoordinatorWiresEnvironmentWithoutEnteringInteractionOrHaptics` 通过）；`GachaShippingNativePreview` BUILD SUCCEEDED；export `gate12-export16.log` Success；`xcodebuild` Release Success（`gate12-xcodebuild19.log`）。同轮全量 `SpinnerEnvironmentTests` 另有 2 个与本改动无关的既有失败（magnetic-slide-tile 取景 0.38、ledge 光池 1.08），未处理。
- **证据**：`Artifacts/PackTearNativeCandidate/r045-pack-holographic-sheen-motion/r045-pack-holographic-sheen-clear.mp4`（实速 + 0.5×）、`r045-stage-sweep-10fps.png`、`r045-carousel-sweep-10fps.png`、参考 `r045-reference-lersentai-contact-sheet.png`；pipeline `evidence/12-shipping/rev-013/`，history event `8ff73b93-…`。录屏实测：carousel 过光 ≈ 5.8／8.5 s，台上过光 11.7–12.6 s，T0 ≈ 13.43，reveal 16.2（T0+2.77）。
- **仍待**：真机上倾斜增益／摇一摇阈值的手感校准；rest 态光带不透明度 0.30 是否偏强待用户判断；封条是否也要吃 sheen（现为袋身 only）。

## 2026-09-07 Gacha Pack 撕包背景 R044：六档金属 colourway（银／蓝宝石／玫瑰金／香槟金／紫晶金心／全光谱）

> **当前状态：用户看过 rev-011 六档色相旋转图后指出「几个颜色都太相近了，应该可以增加一些金银这种表示 luxury、premium 的感觉」。已改为每档一套显式金属 palette 并重录（`evidence/12-shipping/rev-012/`）。视觉批准待确认，未推送手机。**

- **规则**（`GachaPackArcBackdropRules.Colourway`，取代 R043 的 `HueTransform`）：`forTier` 映射 STANDARD→`silver`、REFINED→`sapphire`、SIGNATURE→`roseGold`、CHASE→`champagneGold`、GRAIL→`amethystGold`、1 OF 1→`source`（源 sky／teal／amber／rose 原封不动）。`primaryStops(for:)`／`softStops(for:)` 只替换四个颜色 stop（soft 层向白提 22%），位置与 alpha 形状沿用源；`alphaScale` 按档位提亮（银 1.8、蓝宝石 1.2、玫瑰金 1.25、香槟金 1.25、紫晶 1.2、源 1.0）——午夜底偏蓝黑，低 alpha 的金属色会糊成橄榄／灰，银没有色相可依托所以提得最多。每套都是双色调金属（亮心／饱和中环／深色带）。
- **第一版金属色的教训**：淡色（银 #B3C1D3、香槟 #F3C75B）在源 alpha 下混进午夜底变成灰雾与橄榄色，与 R041 被否的「灰阶」同病；改为高饱和金属色 + alpha 提亮后才读得出金属感。harness 强制任意两档在色带与 glow 两环上 RGB 距离 ≥ 0.25（曾捕获源 vs 玫瑰金、源 vs 香槟金、蓝宝石 vs 紫晶三次过近）。
- **接线**：`ProductPackArcBandsBackdrop(intensity:colourway:)`，storefront 传 `Colourway.forTier(selectedPack)`，`.id(selectedPack)` + `.transition(.opacity)` crossfade；`usesPackArcBackdrop` 含 `.choosingPack`；`visibility(tearProgress:stageEligible:)` 只随封条退出归零。预览工具 `--pack-arc-bands-tier=<rawValue>` 渲染任一档底色；`--pack-arc-bands-pack=<rawValue>` 渲染「该档卡包 + 文案 + 底色」（撕封台位置与尺寸）；`--pack-arc-bands-source-only` 仍渲染源 palette。
- **验证**：Swift harness 179/179；Unity EditMode 46 passed / 2 skipped（`GachaStorefrontIntegrationTests` 断言 `Colourway.forTier(selectedPack)`、`case .oneOfOne: return .source`、无 receipt 输入）；`GachaShippingNativePreview` BUILD SUCCEEDED；export `gate12-export15.log` Success；`xcodebuild` Release Success（`gate12-xcodebuild18.log`）。录屏实测 T0 ≈ 9.73 s：翻页 5.7／7.7 s 银 ↔ 蓝宝石；reveal 12.5（T0+2.77）、标签 13.7（T0+3.96）。
- **证据**：`Artifacts/PackTearNativeCandidate/r044-arc-bands-metallic-colourways/r044-gacha-arc-metallic-clear.mp4`（实速 + 0.5×）、`r044-tier-colourways.png`、`r044-arc-tier-*.png`（六张全尺寸）、`r044-pack-with-colourway-sheet.png` / `-strip.png` / `-<tier>.png`（六档卡包 + 对应底色，2026-09-07 14:22 用户索取）、`r044-carousel-switch.png`、`r044-contact-sheet-5fps.png`；pipeline `evidence/12-shipping/rev-012/`，history events `0c295217-…`（rev-011 用户意见）、`8bdd6fa3-…`（rev-012 ready）。
- **仍待**：FDB-GAC-035 第二阶段（午夜底与 dim cave 合成透明度）未做；各档具体色值待用户视觉批准后再锁定。

## 2026-09-07 Gacha Pack 撕包背景 R043：arc 渐变底进入 carousel，随所选 Pack 变色（colourway 方案已被 R044 取代）

> **当前状态：用户看过 rev-010 录屏后要求「这个渐变色的背景在carousel的时候也要出现，在切换不同pack的时候要有变化」。已按此修订 `FDB-GAC-035` 并落地：arc-bands 从 carousel 阶段起就是背景，切 Pack 时 colourway 随 tier 变化；Gate 12 Simulator 重新导出并录屏（`evidence/12-shipping/rev-011/`）。R043 的色相旋转 colourway 被用户评为「太相近」，已由 R044 的显式金属 palette 取代；carousel 接线与 visibility 规则沿用。**

- **规则**（`GachaPackArcBackdropRules`）：`hueTransform(packAccentRGB:)` / `colourway(_:transform:)` 把源 palette 整体做色相变换，使最宽的 rose 色带落在所选 tier accent 的色相上；默认旋转，若旋转让可见环落入 60°–170° 绿色区更多（`greenLoad`：amber glow ×2、中心两环 ×1）则改为绕色带镜像。结果：STANDARD／1 OF 1 中性（饱和度 < 0.2）= 源 palette；REFINED 旋转（蓝带／紫 glow／金心）；SIGNATURE 镜像（铜带／粉 glow／青心）；CHASE 镜像（金带／红 glow／青心）；GRAIL 镜像（紫带／天蓝 glow／金心）。alpha、位置、三组椭圆、blur、lift、点阵、午夜底全部不变；不读取 receipt／rarity。
- **接线**：`usesPackArcBackdrop` 加入 `.choosingPack`；`visibility(tearProgress:stageEligible:)` 去掉选中后的 crossfade-in，只随封条退出归零；`ProductPackArcBandsBackdrop(intensity:packAccentRGB:)`，storefront 传 `selectedPack.storefrontAccentRGB`，用 `.id(selectedPack)` + `.transition(.opacity)` 在 `selectionDuration` 内 crossfade。`ProductPackHueBackdrop` 仍在其下（不透明 arc 完全覆盖，待 FDB-GAC-035 第二阶段 cave 合成时再一并处理）。预览工具新增 `--pack-arc-bands-tier=<rawValue>`。
- **验证**：Swift harness 168/168（新增：各档色带色相 = accent、glow 不落绿区、rotate/mirror 取绿量更小者、alpha／位置不变、相邻 Pack 色带 ≥ 15°、中性档保持源 palette）；Unity EditMode 46 passed / 2 skipped（`GachaStorefrontIntegrationTests` 改为断言 carousel phase、`packAccentRGB: selectedPack`、无 receipt 输入、新 visibility）；`GachaShippingNativePreview` BUILD SUCCEEDED；export `gate12-export14.log` Success；`xcodebuild` Release Success（`gate12-xcodebuild17.log`）。
- **证据**：`Artifacts/PackTearNativeCandidate/r043-arc-bands-carousel-colourway/r043-gacha-arc-carousel-clear.mp4`（实速 + 0.5×）、`r043-tier-colourways.png`（六档，shipping 组件渲染）、`r043-carousel-switch.png`（STANDARD → REFINED → STANDARD → 选中 → 撕封）、`r043-contact-sheet-5fps.png`；pipeline `evidence/12-shipping/rev-011/`，history events `8e495fc0-…`（rev-010 用户修订）、`2f55a752-…`（rev-011 ready）。录屏实测 T0 ≈ 9.53 s：翻页 5.5／7.5 s 处 arc 变色，reveal 12.3（T0+2.77）、标签 13.5（T0+3.96）。
- **仍待**：FDB-GAC-035 第二阶段（午夜底与 dim cave 的 full-hybrid 合成透明度）未做；SIGNATURE 与 CHASE 的 accent 只差 18°，两档 colourway 相近（铜／粉 vs 金／红），如需更大区分需用户决定。

## 2026-09-07 Gacha Pack 撕包背景 R042：OpenSourceUI source-faithful native baseline

> **当前状态：R041 灰阶重设计被用户否决后，R042 已逐值恢复 OpenSourceUI `DarkArcBandsBackground` 的固定 sky／teal／amber／rose 色相、两组连续 RGBA stops、三组椭圆裁切、`40/64 px` blur、`0.08` white lift、`4 px` 周期／`1 px` 半径点阵与不透明午夜底。该层不再接收 Pack tier、receipt 或 rarity。source-only 原生渲染与同尺寸 browser reference 已通过像素及人工对照，Pack 四态预览已生成。当前仍是视觉候选：不透明 source base 在真实 shipping flow 会遮住 `FDB-GAC-033` 的 dim Unity cave，full-hybrid base 合成尚未校准，所以 Not Shipping Ready。视觉批准待确认，未推送手机；真机验收未执行。**

- **实现**：`GachaPackArcBackdropRules` 以公开 source stop 数据锁定原始 RGBA 与几何；`ProductPackArcBandsBackdrop` 删除 `accentRGB`／`tonalColor`／人工暗谷和 `.linear` drawing group，恢复 source dot 的 `.70 × .04` 两级透明度；storefront 只传 phase visibility，保留 carousel crossfade、commit hold 与 whole-case 前归零时序。`--pack-arc-bands-source-only` 使用同一 shipping 组件做 isolated reference render。
- **视觉证据**：`Artifacts/PackTearNativeCandidate/r042-source-faithful/r042-source-vs-native.png` 左为 browser reference、右为 native（相同顶部裁切），SHA-256=`cfc0587e064b725eb6468c17ce70b74ff7abcb9e221495ecf229e936d04e803b`；状态栏以下全画面平均绝对误差 `R=1.323 / G=1.246 / B=1.871`、合计 `1.48 RGB`、P95=`5 RGB`。Pack 四态联系表 `r042-dark-arc-pack-contact-sheet.png` SHA-256=`f0a7853cc9d8862e9a25cbcd09d8edfe753cd2fdc01a5d14ec0e6b1d81d2f822`，顺序为 sealed／partial／commit／faded；最后一态验证 overlay 已归零。
- **验证**：fresh Swift rules harness `141/141 PASS`；Unity 6000.5.6f1 focused `GachaStorefrontIntegrationTests`=`2/2 passed`、0 failed/skipped/inconclusive，XML `r042-source-faithful-unity-editmode-results.xml` SHA-256=`ada1515fb63f2734676df4e4176104b7405a9643fbf3ccf5371e4d00245ac30f`；iOS Simulator Debug 编译／链接 `BUILD SUCCEEDED`，iPhone 17 Pro Simulator 生成全部 `1206×2622` PNG。另一 Unity task 的既有 lock 被原样等待，没有删除 lock 或终止进程；最终测试已释放项目 lock。
- **下一门禁**：用户先确认 R042 是否忠实保持原设计；若批准，再仅校准午夜 base 与真实 dim cave 的合成透明度，彩色 arc／点阵不得改色或削弱，并生成 cave＋Pack＋whole-case 的 full-hybrid shipping preview。完成该视觉门禁前不得 build／install 到手机。

## 2026-09-07 Gacha Pack 撕包背景 R041：OpenSourceUI Dark Arc Bands 灰阶候选（用户已拒绝）

> **当前状态：R041 shipping native 灰阶候选已接入并完成技术验证，但用户明确否决其视觉，原话为“你这个 background 可以说和他原来的这个设计是一点关系都没有啊？你自己就是连色相、包括细节、质感全都不对”。审计确认该版主动把源 sky／teal／amber／rose 连续色带改成 STANDARD 单色灰阶、插入人工明暗谷、削弱 lift／soft／点阵并把午夜底半透明化；因此它不是 faithful port，不能继续作为批准候选。代码和证据仅作 rejected history；下一版按 `FDB-GAC-035` 先逐值复现源视觉，再做 full-hybrid 合成。未推送手机；真机验收未执行。**

- **来源与许可证**：实现审计并固定 OpenSourceUI `DarkArcBandsBackground` commit `d239c3463c984a099dd2cb67817a41fc0bcc876f`、Git blob `b13404dd73e02a4267b48ff1136aa3c1b2205827`、MIT / Copyright © 2026 Bidyut Kundu。原 React／Tailwind runtime 未引入；完整 notice 在 `Docs/OpenSourceUI-DarkArcBands-MIT.md`，并由 `Assets/StreamingAssets/ThirdPartyNotices/OpenSourceUI-DarkArcBands-MIT.txt` 随 app bundle 出货。
- **shipping 实现**：`FidgetGachaPackPresentation.swift` 新增 `GachaPackArcBackdropRules`，保存三层椭圆的宽高、独立 X/Y radial 比例、模糊、圆点密度、透明度与确定性 visibility；`FidgetProductUIComponents.swift` 新增 `ProductPackArcBandsBackdrop`，只用 Pack display-tier tonal variants，不读 receipt rarity，STANDARD 保持银灰中性，静态圆点、无 hit testing、对 accessibility 隐藏，并处理 Reduce Transparency；`FidgetGachaShippingStorefront.swift` 在 `.selectionRive/.tearPack/.waitingForReceipt/.preparingCase` 接线，`(1-selectionBackdropOpacity) × sealExitOpacity` 让其在 `tearProgress=1` 与 `.handoff` 前为 0。底层 alpha=`0.58`（Reduce Transparency=`0.86`），避免覆盖 `FDB-GAC-033` 的 dim cave；旧亮 donut／generic shockwave 未恢复。
- **测试与构建**：Swift rules harness `138/138 PASS`（source pin、stop arrays 等长／有序／范围、120%/88% 与 110%/80% 椭圆、carousel crossfade、commit hold、seal midpoint 0.5、progress 1 与 phase gate 归零）；Unity 6000.5.6f1 focused EditMode `GachaStorefrontIntegrationTests`=`2/2 passed`、0 failed/skipped/inconclusive，结果 `Artifacts/PackTearNativeCandidate/r041-dark-arc-bands/unity-editmode-results.xml` SHA-256=`9e2353091b98a94dd3280bc5866cd33fd10871540f328b0e15fc6fa414b31597`；`GachaShippingNativePreview` iOS Simulator Debug 编译／链接 `BUILD SUCCEEDED`，部署目标 iOS 15.0，随后安装并启动于 iPhone 17 Pro Simulator。Unity 退出后项目 lock 已释放。
- **shipping-source 视觉证据**：四态联系表 `Artifacts/PackTearNativeCandidate/r041-dark-arc-bands/r041-dark-arc-bands-contact-sheet.png`（左上 sealed、右上 partial、左下 commit、右下 faded；SHA-256=`0a24e4791f9910e83b87633a9ff98dcc7cf899d47a76e23d957d8ba722d42f8d`）；真实 Simulator H.264 `r041-dark-arc-bands-tear-preview.mp4`（`1206×2622`、30 fps、1.60 s、SHA-256=`802c712ddccfe80dbb3c25afa83184be2901322e251020e7a226d45f9b99e416`）。faded 帧验证 native arc 为 0；该 host 的底层是纯黑，仅为 component/Pack 时序证据，不能替代真实 Unity cave／whole-case 合成验收。
- **否决与下一步**：当前联系表／短片已被用户拒绝，不再等待批准，也不得复制到 `Docs/DesignBibleAssets/`。下一版必须先逐值恢复源四色 stops、alpha、lift、点阵与不透明午夜 baseline，并以同尺寸 browser reference／isolated native render 做并排和像素校准；只有 source fidelity 成立后，才进入真实 Unity dim cave＋Pack＋whole-case full-hybrid 合成并校准 base 透明度。现阶段不得 build／install。当前不改 Unity 3D scene、case、toy、奖品材质、物理或 Haptics。

## 2026-09-05 → 09-08 龙鳞三叶（GEEONE，`metal-three-blade`）：源视频 intake → 12 Gate 全部批准 → Build 47 真机验收通过

> **当前状态（2026-09-08）：12/12 approved（pipeline.json rev 66）。Gate 12 rev-007（光照提亮）由用户 18:36“推到手机上吧”chat 批准；Build 47 安装启动；用户随后确认“Build 47 已装到手机，用户真机验收通过”。DecisionState 与 DeliveryState 均已闭合：出货场景 `ThreeBladeMetalOriginal.unity`，材质 `M_GeeoneSatin / M_GeeoneDiscTurned / M_GeeoneHubDark`，`SpinnerImageBasedLightingController` GEEONE 详情提亮。所有 mm 仍为 85 mm user-authorized-provisional。剩余待用户决定：`FDB-PREF-032` 的 catalog 收敛（`gold-four-wing` / `pointed-three-blade` 旧条目），本轮未动。下方按时间保留完整决策链。**
>
> 历史起点（09-05 晚）：用户 22:22/23:07 否决 rev-004/rev-005 几何（叶尖弧度、楔形过渡、凸凹细节不符，要求逐帧对比），22:31 要求完整跑 Obsidian 剪藏对应的视频。已用 yt-dlp 下载小红书源视频（36.6 s，720×1280），ffmpeg 10 fps 抽帧 366 张，完成 Gate 01 rev-003 与 Gate 02 rev-006。

- Gate 01 rev-003：`evidence/01-intake/rev-003/obsidian-geeone-video/geeone-source.mp4`（sha256 记录于 `intake-record.json`，含 yt-dlp 版本、format、URL）、25 张关键帧（逐张哈希）、7 张 10 fps 缩略表 + 2 fps 总览；rev-002 的 7 张剪藏截图重新关联。44 个 artifacts。
- Gate 02 rev-006：`measure_geeone_video_frames.py` 对桌面平放段 f0077/f0078 剪影做椭圆→圆倾斜校正后量测：盖/外接圆 0.485±0.009（照片 0.536）、平盘/盖 0.80、叶尖角 67°±3、叶尖圆角 ≈0.045 R、每缺口露盖弧 ≈56°（透视未校正，36–71°）。12 条 source-linked claims（`claims-rev6.json`），15 条旧 claim superseded；**65 mm → 85 mm user-authorized-provisional（追加式 supersession，65 mm 历史保留；适用范围仅未来 Gate 03–05；不得标 measured）**。参考 CAD `reference-cad-from-video.{png,pdf}`（顶视 + 剖面示意，比例单位 R）；`frame-vs-rev004-comparison.png` 四组逐帧对比；`frame-zooms/` 细节放大。
- 视频揭示、与此前指示冲突、待用户裁决的四项：盖侧（冠环+裙）露出≈0.14 R≈0.8×机身厚（vs“高出 1.5 mm”）；每片叶根有开口朝盖的三角凹坑、外壁斜切（vs“实心”）；盖/外接圆 0.485（vs 0.536）；平盘/盖 0.80（vs 0.70）。另：倒角带内 3–4 个平面（“楔形过渡”/龙鳞），冠环下裙为多边形分面。
- 未知项保持 unknown：全部绝对 mm、凹坑深度/通孔、倒角各面角度、缝宽、轴承型号、楔数精确值（24±2）、材质牌号。
- 验证：`validate_model_pipeline.mjs metal-three-blade`（只读）0 errors、0 missing（rev 29）；未运行 `--refresh`；无 git 操作；无安装。
- 2026-09-06 07:27 用户要求“把表面的细节再还原一下，确保带入 Blender 建模”。Gate 02 rev-006 追加（仍 ready_for_review）：`surface-detail-atlas.png`（8 帧 2–4× 放大，D01–D10 标注）；`surface-detail-spec.json`（10 项 `mustBeGeometry` 细节：D01 平盘、D02 冠环三角 24±2、D03 盖裙第二排 ≈24 平面、D04 平台、D05 叶边倒角鳞面带每边 5–7 平面倾角交替、D06 竖壁 ≈0.45×厚、D07 叶尖 67°/圆角 0.045R/脊、D08 叶根三角凹坑、D09 暗缝与缺口露盖、D10 底面镜像），每项含来源帧、置信度、Gate 06 检查项与 Blender 构建要求；`check_surface_detail_coverage.py` 门禁：builder 必须逐项 `# detail: UTS-Dxx` 标记，缺一项即 exit 1，Gate 05/06 登记脚本以此阻断——对历史 rev-005 builder 实测 0/10（`detail-coverage-current-builder.json`）。Gate 01 补入 6 张被引用关键帧（rev 31，validator 0 errors）。
- 2026-09-06 07:53 用户“再生成一版”：`reference-cad-from-video-v2.{png,pdf}`（`draw_geeone_reference_cad_v2.py`）在 v1 轮廓上加入 D01–D10：顶视画出鳞面带分界（每边 6 面）、平台边、叶尖脊、凹坑与斜切内三角、冠环三角与 24 边形盖裙；A-A 加凹坑占位（深度未知，橙虚线）与盖侧两排；C-C 示意相邻鳞面倾角交替；Detail D/E 为鳞面带与盖侧两排刻面展开。v1 保留为历史。validator 0 errors（rev 32）。
- 2026-09-06 07:59 用户：“三个叶片的比例好像要更大一点，边缘都是弧形，把叶面内部的细节还原到 CAD 图上”。在校正剪影上直接量叶片半宽曲线（x/R 0.50→半宽 0.399 … 0.90→0.146 … 1.00→0.031，3 叶平均）：叶根接盖于极角 ±39°、缺口两侧径向直边、肩 r≈0.64 R 处最宽 ≈0.80 R（≈0.82×盖径）、边缘为凸弧、叶尖圆角 ≈0.085 R（推翻此前 67° 直边/0.045 R 读数，claim `tri-r6b-blade-planform` 取代 `tri-r6-blade-outline-teardrop`）。`reference-cad-from-video-v3.{png,pdf}` 由该曲线直接绘出，并画出叶面内部：平台边界、鳞面带 6 面分界、叶尖脊、铣削平底三角凹坑（圆角 0.025 R、边沿倒角、底边半宽 0.135 R、尖端 0.70 R）、过凹坑横剖 C-C。`surface-detail-spec.json` 同步 D07/D08 与 `planformProfile`。validator 0 errors（rev 33）。
- 2026-09-06 08:10 用户：“尖角没有那么尖锐，应该几乎是圆的半径的弧度；三角下方两个叶片的底边几乎近似平行”。把实测半宽曲线（x 0.50–0.85）拟合为**圆角等边三角 + 三个径向缺口**：直边与叶轴成 30°、距中心 0.606 R（虚拟顶点 1.212 R），叶尖为 R≈0.212 R（≈9 mm @85 provisional）跨 120° 的大圆弧、顶点在外接圆上，相邻两叶底边共线；缺口为 42° 径向扇形切到盖圈，肩 0.64 R。残差 ±0.02 R；x≥0.90 实测偏窄系叶尖暗色倒角低于剪影阈值。`reference-cad-from-video-v4.{png,pdf}` 由该模型绘出（叶面内部细节同 v3），claim `tri-r6c-blade-planform-triangle` 取代 `tri-r6b`。validator 0 errors（rev 34）。
- 2026-09-06 20:41 用户截图批注“这个尖角没有那么突出”（v4 肩部）：肩部改为 ≈0.09 R 圆角平滑过渡（`planformProfile.parametric.shoulderFilletRadiusToR`），`reference-cad-from-video-v5.{png,pdf}`，claim `tri-r6d-shoulder-fillet`，用户截图存为 user-input 资产。validator 0 errors（rev 35）。
- 2026-09-06 20:46 用户两张截图（f0148/f0134 红圈、f0077 盖）：“过渡应贴圆心、下层拐角几乎是锐角、斜切线有弧度，你做成了钝角拐角”；“中间凹下去、切成约 14 片、放拇指”。`trace_geeone_blade_root.py` 逐叶在校正剪影上描迹（`frame-zooms/blade-root-traces.png`）：叶边是**凸圆弧**而非直边——4 条干净边圆弧拟合 rms 0.0006–0.0010 R（直线 0.011–0.015 R），R_s≈1.37 R、圆心在叶轴垂线上距盖心 0.92 R，弧直接扫到盖圈，**无肩角**；相邻两弧在角平分线交于 r≈0.49 R（距盖圈 ≈0.005 R ≈0.2 mm @85），弧与盖圈交角 ≈18°（锐角新月尖）；叶尖两弧夹 ≈90° + 0.03 R 圆角（“三个尖角不够尖锐”与本读数一致，v4/v5 的 0.21 R 大圆弧作废）。盖：展开图 + FFT 计数冠环 **14±1 楔 = 28 三角**（24 作废），盖裙 14 鳞 ×2 排（f0200/f0208），盘 0.82×盖（0.80–0.85）；f0077 远侧冠环被压缩到侧向 1/3 ⇒ 冠环由盘缘向外向下（盘缘为最高圈）；盘内凹面拇指位按用户口述登记为 user-stated（f0204/f0208 锥形放射明暗 + 同心车纹支持“车削浅锥/碟”，凹深 unknown，CAD 6° 占位）。`reference-cad-from-video-v6.{png,pdf}`（顶视 + A-A + Detail D 缺口对比 v5 + Detail E 盖顶 E1/E2 二选一 + 拟合表）；`planform-v6-on-frames.png` 把 v6 轮廓反投影到原帧 f0077/f0078；`cap-evidence-v6.png` 盖证据板。claims `tri-r6e-*` 5 条新增，`tri-r6c/tri-r6d/cap-crown/table-ratio/seam/unknowns` superseded；Gate 01 rev-003 补入 f0192/f0200/f0208。validator 0 errors、0 missing（rev 37）。
- 2026-09-07 07:53 用户对 v6 缺口处红箭头：“这个部分是有些间隔的，不需要连接在一起”。根部描迹复核（4 条干净边）：叶边都在 x≈0.31 R 到达盖圈（极角 51–53°），随后剪影沿盖圈延伸到 ≥62°——相邻叶片不相接，每缺口露盖 ≈16°；单一大圆弧无法同时贴合叶边中段与该根部点（残差 −0.025 R），故 v7 = 大凸弧（R≈1.37 R）→ 自 x≈0.40 R 起 R≈0.15 R 内收圆弧 → 止于盖圈极角 52°，与盖圈切线夹 ≈60°。`reference-cad-from-video-v7.{png,pdf}`（Detail D 对比 v6 的 V 交点），`planform-v7-on-frames.png` 反投影叠加，`blade-root-traces.png` 重出（v6 vs v7）。claim `tri-r6f-blade-planform-gap` 取代 `tri-r6e-blade-planform-arcs`/`tri-r6e-notch-exposure`；D07/D09 与 `planformProfile.parametric.rootBlend` 同步；用户截图与原话存为 user-input 资产。validator 0 errors、0 missing（rev 38）。
- 2026-09-07 08:25 用户对盖部截图：“这个圆应该以圆心为中心，作为中心点，然后被切分成14片。均分”。f0077 校正后对盘做角向高通展开（`disc-unwrap-f0077-highpass.png`）：受光半周每 ≈26° 一条扇区亮度阶跃，6× 高通图 14 辐条（相位 ≈16°）与分界吻合（`disc-sectors-f0077.png`）——D01 由“车削平盘/浅碟”改为**以圆心为顶点均分的 14 个平面扇区组成的凹 14 棱锥拇指位**，盘缘 14 边形（0.82×盖）顶点与冠环内顶点重合，盘/冠环/裙共用一套 14 等分；凹深仍未知（顶点透视位移 ±2 px → 视频上限 ≈2°，CAD 3° 占位）。`reference-cad-from-video-v8.{png,pdf}`（叶片同 v7），claim `tri-r6f-disc-14-sectors` 取代 `tri-r6e-cap-dish-user-stated`；用户截图与原话存为 user-input 资产。validator 0 errors、0 missing（rev 39）。
- 2026-09-07 08:39 用户在 CAD v8 上手绘红色 Y：“就是有一个这样的凸起的弧度，然后中间红色的部分就是它的隆起”。D04 由“平台为平面”改为 **Y 形隆起脊线**：主脊沿叶轴从叶尖到 x≈0.72 R（凹坑尖端外），两臂沿凹坑两侧外凸弧线（“叉臂”）到盖圈极角 ±38°，顶面自脊线向外落到鳞面带、向内落到凹坑边；f0108/f0132 主脊与两臂亮带环抱凹坑、f0156 斜视大斜面软脊与此一致（`blade-top-y-ridge-f0108-f0132-f0156.png`）。脊高未测（CAD 以 0.025 R 占位）。`reference-cad-from-video-v9.{png,pdf}`：顶视加紫色点划脊线，A-A 沿主脊，新增 C-C（x 0.58，两臂隆起 + 凹坑）与 F-F（x 0.85，单脊）。claim `tri-r6f-blade-top-y-ridge` 取代 `tri-r6-blade-top-structure`；Gate 01 补入 f0108/f0132/f0156；用户手绘与原话存为 user-input 资产。validator 0 errors、0 missing（rev 40）。
- 2026-09-07 09:36 用户两张图：C—C v9 截图“这个我看不懂”；源帧局部蓝/红/绿三色圈图“通过三层过渡完成了从平面到垂直面的变化”。（1）可读性：v9 顶视没有剖切线、C—C 里上下两坑让切面像哑铃且各面无标注——`reference-cad-from-video-v10.{png,pdf}` 在顶视右下叶标出 A—A / C—C / F—F 剖切线（圆圈字母），C—C/F—F 逐面标注（顶面/Y 臂脊/鳞面带/竖壁/凹坑），凹坑占位深度改 25%/侧，并出 `section-cc-reading-guide.png`。（2）三色圈图用归一化互相关模板匹配定位到 **f0132 (336,524)+181×168，NCC 0.92（`cap-edge-three-tier-evidence.png`）——位于盖缘，不是叶边**：绿 = 冠环楔（贴 14 边形盘缘，最缓）、红 = 盖裙上排、蓝 = 盖裙下排（最陡近竖直），f0128–f0140 8× 盘缘外依次为亮排→纹理中排→暗陡排。D02/D03 改为**盖缘三层逐层变陡的过渡**（冠环外顶点到 ≈0.92×盖而非盖圆；裙两排各有径向宽而非竖直），其下一小段竖直 14 边形侧壁接暗缝；各层径向宽/斜度 0.10/0.06/0.02×盖径、20°/45°/75° 为占位，14 等分与盘 0.82×盖不变。新增 Detail G 盖缘 4:1 半剖，A-A/Detail E 同步三层。曾短暂把三层写入叶边 D05，定位后撤回，D05/D06 恢复原值。claim `tri-r6f-cap-edge-three-tiers` 取代 `tri-r6e-cap-crown-14`；Gate 01 补入 f0128/f0136/f0140；用户两张截图与原话存为 user-input 资产。validator 0 errors、0 missing（rev 41）。
- 2026-09-07 10:08 用户：“用 shadow 的亮度和明度表示什么地方凹、什么地方凸”。`shade_geeone_reference_v10.py` 用 CAD v10 同一参数生成 2.5D 高度图（叶片 Y 隆起 + 鳞面带 + 凹坑、盘 14 扇区凹棱锥、盖缘三层、暗缝），输出 `shaded-relief-v10.png`：主光左上 38° 与低角度侧光左 18° 两种阴影（高度夸张 3×）、相对各自主面高度的红/蓝凹凸图（红 = 高于主面、蓝 = 低于主面）、凸/凹标定球、盖与右下叶放大。只是分析插图，不是 Blender 白模或渲染；脊高/盘凹/坑深/三层角度均为占位，鳞面带内各面倾角交替未表现。validator 0 errors、0 missing（rev 43）。
- 2026-09-07 10:40 用户对阴影图叶边局部：“这个地方的过渡不对，叶面从平面过渡到垂直面需要有多层龙鳞纹过渡；截图里有个不明的凹痕”。（1）D05 由单排倒角带改为**多排龙鳞刻面**逐排变陡到竖壁，与盖缘三层同一构造：排数 3 为占位（f0128–f0140 5× 至少可见 2 排），每排每边 6±1 鳞、错半鳞、相邻一亮一暗，占位 0.030/0.022/0.018 R、15°/38°/62°；D06 竖壁 0.30×厚占位（原 0.45）。09:36 曾把三层写到叶边后撤回，此次按用户明确指令重新登记。`reference-cad-from-video-v11.{png,pdf}`：C-C/F-F 叶边三排上色，新增 Detail H（叶边多层鳞 4:1 + 俯视错半鳞示意），拟合表移出（v6–v10 保留）。（2）“不明凹痕”查明为 v10 阴影图中栅格距离场（EDT）对数字化边界的 ≈0.0002 R 周期误差，被 3× 夸张 + 18° 侧光放大成条纹，不是几何；`shade_geeone_reference_v11.py` 改用 2400 点样条边界 + KD-tree 精确距离/弧长，叶边带做成显式平面鳞排（三角波起伏 0.004 R、鳞长 0.11 R 占位），`shaded-relief-v11.png` 条纹消失、鳞排一亮一暗可见。claim `tri-r6f-blade-edge-scale-rows`（refines `tri-r6-surface-detail-spec`）；用户截图与原话存为 user-input 资产。validator 0 errors、0 missing（rev 44）。
- 2026-09-07 10:55 用户：“原图的龙鳞纹要比你做的每一片面积要大一些”。核对 f0148/f0154（叶片捏在手指间、边缘正对相机）：顶面到中面之间 **2 排大鳞**（下半镜像），沿一条叶边 4–5 片、每片 ≈0.18 R 长，排间错半鳞。D05 由 3 排 × 每边 6 片改为 2 排 × 每边 4–5 大鳞（排宽 0.040/0.030 R、斜 22°/55° 占位），D06 竖壁 ≈0.31×厚。`reference-cad-from-video-v12.{png,pdf}`（Detail H 两排 + 错半鳞展开），`shaded-relief-v12.png`（相邻鳞 ±7° 交替倾角，读作一片片大平面）。claim `tri-r6f-blade-edge-large-scales` 取代 `tri-r6f-blade-edge-scale-rows`；用户截图与原话存为 user-input 资产。validator 0 errors、0 missing（rev 46）。
- 同日 v13（f0148/f0150/f0154 7× 复核）：叶片捏在手指间、相机在上方时，侧面最宽处（中面）成为剪影，可见的恰是上半——**2 排大鳞从顶面直落到中面**，第 1 排中等斜度、第 2 排更陡、锯齿分界、错半鳞；两排径向 ≈0.07 R（与 f0077 顶视一致）、竖向 ≈0.085 R = 半厚，占位 35°/62°。**没有独立竖直圆柱壁**：D06 由 0.45→0.30→≈0（f0226 侧视读数很可能就是陡排），用户所说“垂直面”= 陡的第 2 排。`reference-cad-from-video-v13.{png,pdf}`、`shaded-relief-v13.png`、`blade-edge-large-scales-evidence.png`；claim `tri-r6f-blade-side-two-rows-to-midplane` 取代 `tri-r6f-blade-edge-large-scales`；Gate 01 补入 f0150。validator 0 errors、0 missing（rev 47）。
- 2026-09-07 11:10 用户：“每片鳞片的过渡太平滑了，应该硬朗一点”。v13 的鳞面是三角波起伏 + 排中线扭转的连续面；`shade_geeone_reference_v14.py` 改为**每片鳞一个独立平面**（相邻鳞斜度 ±5°、扭转 ±3° 交替，占位）、排界 V 形锯齿（±0.005 R 占位）、鳞间硬折边、着色前不模糊。`shaded-relief-v14.png`、`blade-scale-hardness-v13-vs-v14.png`（f0148 vs v13 vs v14）。spec D05 增加 `facetStyle`（planar, hardCreases）与 Gate 06 检查“每片鳞单一平面、锐折边、无平滑过渡”。CAD v13 几何不变。validator 0 errors、0 missing（rev 48）。
- 2026-09-07 11:47 用户在阴影图 v14 右下叶圈出 Y 交点两侧两处：“这两个地方凹下去了。然后鳞片的细节还是不对，你再仔细对照图片看一下。”（1）凹陷是 v9–v14 顶面模型的产物：z = 脊高·d_low/(d_low+d_crest) 让柄与两臂三条脊线之间形成谷。D04 改为 **Y 形平顶隆起**：顶区平、四周直斜裙（≈0.09 R 占位）落到鳞带边与坑边，柄臂之间保持高位、无谷；Gate 06 检查改为“顶面无局部极小”。（2）f0148/f0150/f0152 10× 复核鳞片形状：叶侧不是两排叠放的浅锯齿，而是**一道深锯齿咬合**——亮“鸢形”自顶面边下垂（顶边宽、V 尖到带宽 ≈85%，较缓 ≈42° 占位）与暗“Λ 形”自中面上升（底边在中面、尖到 ≈25%，较陡 ≈56° 占位）沿边交替、共用斜折边，每边 4–5 片鸢形、节距 ≈0.18 R，每片独立平面、硬折边；v13/v14 的“2 排”其实是这两族。D05 增加 `facetFamilies`/`zigzagBoundary`，D06 措辞同步。`reference-cad-from-video-v14.{png,pdf}`（Detail H 改为鸢形/Λ 剖面 + 侧视展开示意，顶视/剖面 D04/D05 标注同步）、`shade_geeone_reference_v15.py` → `shaded-relief-v15.png`（鸢形/Λ 独立平面 + 平顶隆起）、`blade-scale-shape-v14-vs-v15.png`（f0148 10× vs v14 vs v15）。claims `tri-r6f-blade-top-y-mesa` 取代 `tri-r6f-blade-top-y-ridge`、`tri-r6f-blade-side-kite-lambda-interlock` 取代 `tri-r6f-blade-side-two-rows-to-midplane`；Gate 01 补入 f0152；用户截图与原话存为 user-input 资产。validator 0 errors、0 missing（rev 49）。
- 2026-09-07 13:27 用户在 f0132 上叶根部（`frame-zooms/blade-top-y-ridge-f0108-f0132-f0156.png` ③）手绘绿/蓝/红线：“这个细节图能帮助你理解吗”。归一化互相关定位到 f0132 (287,396) 2.4×（NCC 0.92）。读法：绿 = 坑尖以上的主脊折边并沿凹坑右缘继续（**坑缘 = 坑侧面的上边 = 最高线**，臂不是独立隆起）；蓝框 = 叶尖面 T，一块大平面；红 = 平面之间的直折边（坑角 → K → T 面角；K → 根部边缘）；右蓝 = 根角面 C。D04 由“平顶隆起 + 直斜裙”改为**几块大平面硬切的凸包络**：每半叶 T（含主脊，向叶尖下落 0.025 R 占位）/ F（上边 = 水平坑缘）/ C（自坑角与 K 落到根部边缘）三平面取最低值，折边 = 平面交线（直线），无谷；K ≈ 坑角外 0.07×0.07 R、落差 0.015 R 占位。`draw_geeone_reference_cad_v15.py`（`facetPlanes` 读自 spec；`top_z`/`crease_segments` 由平面交线算出折边；顶视紫线改为折边 + T/F/C 标注；A-A 主脊下落；C-C/F-F 顶面按 `top_z` 采样）→ `reference-cad-from-video-v15.{png,pdf}`；`shade_geeone_reference_v16.py` → `shaded-relief-v16.png`（叶顶取平面最低值，鳞带自实际顶面边高度下垂）；`blade-top-facets-user-1327-vs-v16.png`（用户描线定位 + 读法 vs v16）。claim `tri-r6f-blade-top-hard-cut-facets` 取代 `tri-r6f-blade-top-y-mesa`；用户手绘与原话存为 user-input 资产。validator 0 errors、0 missing（rev 50）。
- 2026-09-07 14:01 用户在阴影图 v16 上标红圈 / 蓝线 / 黄线：“红色部分要用圆角过渡…内凹的台阶要更深一些…蓝色部分有一个斜面过渡，你现在只是向内收了，应该向外扩展，深度也要更深…黄色部分是用不同的梯度来进行平面和垂直面的过渡，你现在只是轻轻地在上面做了一层雕刻”。（1）D08 凹坑改为**斜面漏斗 + 深台阶 + 圆角**：口沿在顶视描迹线外 0.03 R、平底在内 0.03 R（壁 ≈47°），平底深 38% 厚/侧（原 25%，仍 unknown），口/底圆角 0.04/0.025 R；f0116/f0120/f0124/f0128 6× 可见圆角尖、亮口沿斜带、暗深腔。（2）D05 改为**宽多梯度过渡** 0.14 R：T/F/C ≈15° → A 层大斜面 0.07 R@22°（每边 3 片、错半片）→ 鸢形 38° / Λ 53° 到中面（f0148–f0152 读法保留为最后两级）；f0116/f0124 3× 叶顶大刻面；叶尖 x>0.85 R 整个顶面都是过渡刻面。`draw_geeone_reference_cad_v16.py`（口/底双轮廓、A-A/C-C 漏斗剖面、三层叶边剖面按到中面归一、Detail H 三层、顶视 A 层分格线）→ `reference-cad-from-video-v16.{png,pdf}`；`shade_geeone_reference_v17.py` → `shaded-relief-v17.png`（A 层错位大平面 + 鸢形/Λ、漏斗坑高度场）；`edge-gradient-pocket-funnel-user-1401-vs-v17.png`。claims `tri-r6f-blade-edge-wide-gradient-transition` 取代 `tri-r6f-blade-side-kite-lambda-interlock`、`tri-r6f-pocket-funnel-step-rounded` 取代 `tri-r6-root-pocket`；Gate 01 补入 f0116/f0124；用户标注与原话存为 user-input 资产。validator 0 errors、0 missing（rev 51）。
- 2026-09-07 14:25 用户：“你是不会用圆角吗”。v17 首版的凹坑“圆角”只是直线切角。改为**真圆角**：`round_polygon` 重写为相切圆弧（顶视口 R0.05、底 R0.03 占位）；新增 `funnel_profile`，剖面口沿凸圆角 R0.03（顶面→斜壁）、平底边凹圆角 R0.03（斜壁→平底），A-A/C-C 剖面与阴影图 v17 高度场（口沿外圈、斜壁、平底边三段圆弧）同步；spec D08 增加 `edgeFilletTopToR/edgeFilletFloorToR`；claim `tri-r6f-pocket-funnel-step-rounded` 修订；证据板重做。validator 0 errors、0 missing（rev 52）。
- 2026-09-07 17:18 用户粘贴《geeone-02 · rev-006 · 叶根凹坑 + 阶梯过渡 + 刀纹 —— agent 执行说明》（原文存 `evidence/05-blockout/rev-005/rev006-agent-instructions-user-2026-09-07-1718.md`），要求在“rev-005 的 .blend”上 Run `spinner_rev006_rootpocket.py`。现状：该脚本磁盘上不存在，rev-005 只有外部 agent 的 `~/Downloads/spinner_rev005.py`（09-05 23:05，65 mm、圆角等边三角整体机身 + 中心盖孔 + 尖朝圆心的旧凹槽）。处理：按 A/B/C 表写出 `spinner_rev006_rootpocket.py`（P 字典驱动：凹坑刀体 = 坑底轮廓 + 坑口上方 2 mm 放大轮廓两层桥接，平面直壁 62°、锥顶弧 R2.5、开口伸进盖孔 R_CAP−3；Bevel A weight 1.2×1 按法向打标 84 条顶面↔竖壁边；Bevel B angle 0.2×2@35°；SP_Steel_ArmLay 辐条/同心刀纹 Bump、SP_Steel_PocketLay 等高环纹，Boolean TRANSFER），`run_rev005_rev006_headless.py` 在 Blender 5.2 headless 跑 rev005 → rev006，产出 `geeone-blockout-r005.blend`、`geeone-blockout-r005-rev006-rootpocket.blend`、`checks/` 六张 Workbench 视图、`fixed-views/` 固定相机包（verified）。**D 验收**：D1 圆顶等腰三角/尖朝叶尖/开口进盖孔 ✓、D2 坑尖到叶尖 5.00 mm ✓、D3 直壁整块平面 ✓、D5 两条折线 + 1.2 带 ✓、D6 `[rev006]` 四行 ✓；**D4 ✗**：坑底 z 8.80（BODY_H 12.0 − 3.2）高于 rev-005 盖座 7.50 且盖体填在孔内，透过坑看到的是盖侧壁不是黑腔——说明书“坑底 9.8 低于盖体下沿”与 rev-005 数值不自洽。**偏差**：Exact Boolean 在 Bevel A 之后失败（刀体顶面残留、29 非流形边），改 MANIFOLD 求解器后 selfcheck 0 非流形；rev-005 反向凹槽与旧角度倒角已移除（说明书未提）。**与 Gate 02 冲突（列为 warn，待用户裁决）**：65 vs 85 mm；圆角三角整体机身 + 1.03 mm 连续薄壁 vs 叶片分离露盖 16°（用户 07:53）；45°×1.2 平切带 + 竖壁两级 vs 宽多梯度 + 鸢形/Λ 龙鳞（D05 v17）；平面直壁 62° 打穿 vs 47° 漏斗 + 深台阶 + 真圆角（D08 v17）。登记为 Gate 05 rev-005 `draft`（`upstream-gates-pending` warn），Gate 01/02 仍 ready_for_review，无任何批准，Cycles 未开，未进 Unity；视觉批准待确认，未推送手机。validator 0 errors、0 missing（rev 53）。
- 2026-09-07 17:50 用户：“我觉得不对，还是按照你之前的那一版来做吧。”→ Gate 05 rev-005（外部脚本 + rev-006 执行说明）记为 **rejected**（原话入 historicalDecisions），白模改按仓库自己的 Gate 02 rev-006 分析重建为 **Gate 05 rev-006**：`export_geeone_gate02_geometry.py` 从 CAD v16 模块导出几何合同 `geeone-gate02-geometry-contract.json`（R 单位；全转子外轮廓 / A 层边 / 顶面边三条 r(θ) 表来自 EDT 等距轮廓；六平面；坑口/底真圆角多边形；盖参数；哈希链到 spec v17），`build_geeone_gate02_blockout.py`（bpy，D01–D10 全部 `# detail:` 标记，coverage 10/10）生成：凸弧三叶 + 尖叶尖 + 缺口露盖（D07/D09），T/F/C 六平面精确裁剪的硬切顶（D04，按扇区 + 半平面裁剪，T 形接头已缝合），A 层 0.07 R@22° + 鸢形 38°/Λ 53° 咬合到中面（D05/D06，三环按极角拉链缝合，节距 0.18 R → 33 片/圈），漏斗坑（D08：口外扩 0.03 / 底内收 0.03 R、深 38% t、顶视真圆角、底边凹圆角 4 段弧、开口进盖座；口沿凸圆角留待 Gate 06 边倒角），盖座 Boolean 压平毂顶，上下镜像（D10），盖：14 扇 3° 凹盘 + 14 楔 28 三角冠环 + 14×2 裙 + 14 边竖壁 + 暗缝环（D01–D03/D09）。Blender 5.2 headless：基础面片 0 非流形，盖座 + 6 坑 MANIFOLD Boolean 后 2125 顶点 / 2012 面 / 0 非流形；`checks/` 十张 Workbench 白模视图、`fixed-views/` 固定相机包（verified）。2R = 85 mm 仍 provisional。Gate 05 rev-006 `ready_for_review`；Gate 01/02 仍 ready_for_review（17:50 原话是方向选择，不是 Gate 批准）；Cycles/材质/Unity 未做；视觉批准待确认，未推送手机。validator 0 errors、0 missing（rev 55）。
- 2026-09-07 18:33 用户在 rev-006 白模缺口特写上标黄弧 / 绿框：“黄色的部分，它的圆圈的半径应该是大于内部的这个轴心的转动的承托的…绿色的应该是往内收。它的这个圆环是要往内收，然后上下内凹的这个圆盘要稍微盖住中间的一点点。”→ 盖缘（盘 + 冠环 + 裙）下面不是与盖同径的竖壁，而是**内收的毂座**（轴心转动的承托）：spec D03/D09 v18（`capOverhangToR` 0.03、`hubSeatRadiusToR` 0.455、`hubSeatHeightToR` 0.057，均占位；暗缝 = 外悬下阴影），CAD v17（A-A / Detail G 画出外悬缘 + 毂座），claim `tri-r6f-cap-overhang-hub-seat`（refines cap-edge-three-tiers）。白模 **Gate 05 rev-007**：盖裙底边即盖下缘（无竖壁），`Hub_Seat_Top/Bottom` 暗材质圆柱接盖与转子，上下镜像；rev-006 记 rejected（原话入 historicalDecisions）。coverage 10/10、0 非流形、Workbench 十视图 + 评审板 + 固定相机包（verified）。Gate 05 rev-007 ready_for_review；Gate 01/02 仍 ready_for_review；视觉批准待确认，未推送手机。validator 0 errors、0 missing（rev 57）。
- 2026-09-07 18:52 用户对 rev-007 评审板：“可以，继续推进吧”。按原话登记为 chat 批准（证据模式：Workbench 静态视图 + 固定相机包，无交互式查看器，已在各 Gate validations 标 warn）：**Gate 01 rev-003、Gate 02 rev-006、Gate 03 rev-005（`modeling-contract.md` + 几何合同 JSON，全部 R 比例、mm 仅 85 provisional）、Gate 04 rev-005（`architecture.md`：Rotor_Body 旋转 / Cap_Top·Bottom + Hub_Seat 静止；Unity `Fixed_Root` / `Rotor` 挂点）、Gate 05 rev-007 → approved（5/12）**。此前五项冲突按 Gate 02 现值收口且全 provisional（盖侧高 0.14 R、漏斗坑、盖 0.485、平盘 0.82、盖顶 E1）。随后推进：**Gate 06 rev-005**（`finalize_geeone_geometry.py`：apply Boolean → 坑口沿凸圆角 R0.03 R 权重倒角 6 段（30 边）→ 0.15 mm 微倒角 >40° → `gate06-checks.json` 7 项全过：顶面无谷、刻面平面度 2e-6 R、口沿圆角、上下镜像、14 扇区、盖缘 > 毂座、倒角后 0 非流形；3393 顶点 / 3208 面）ready_for_review；**Gate 07/08/09 rev-002**（`lookdev_geeone.py`，同一 `geeone-lookdev-r002.blend`：satin 钢 roughness 0.36 metallic 1、盘 anisotropic 0.7 径向 + 0.12 mm 同心 bump、毂座暗钢；Key/Fill/Rim 三面光（mm 场景功率 ×250）+ 渐变天空；哑光深灰地面 + 接触阴影；Cycles 96 spp 六视图 + `lookdev-review-board.png` + 36 帧转台 mp4/gif）ready_for_review。未导出、未进 Unity、未 build、未安装；视觉批准待确认，未推送手机。validator 0 errors、0 missing（rev 58）。
- 2026-09-07 19:42 用户对 lookdev rev-002：“质感挺漂亮的，但是中间你那个切分的细节又丢了。就是从圆心，大概就是像切披萨一样切成了14片，这个细节又没有了，而且它是应该是向内凹一点的。”（原话存 `evidence/02-analysis/rev-006/user-instructions-2026-09-07-1942.md`，资产 `tri-r6-user-instructions-1942`）。材质方向被认可；唯一修改点是 D01 中央盘的**可见性**（几何定义 08:25 起就是 14 等分凹棱锥）。根因：盘凹 3° → 相邻扇区法线只差 ≈1.3°；盘面各向异性 0.7 + 同心 bump 0.25 盖过刻面色调；没有参考截图角度的视图。修正：**spec D01 v19**（`dishSlopeDegProvisional` 3→5，凹深 ≈0.035 R ≈ 1.48 mm@85 provisional；`sectorAltTiltDegProvisional` 0.5 = 相邻扇区绕角平分线反向倾 ±0.5°，顶视等分不变，占位可设 0；`sectorCreaseHighlightBevelMm` 0 —— 首次 rev-006 试过 0.12 mm 后放弃，倒角把 2° 折边摊平反而看不见），合同在 `06-geometry/rev-006/` 重新导出（spec v19 哈希链）。**Gate 06 rev-006**：`finalize_geeone_geometry.py` 盖从合同重建（14 平面扇区 + 锯齿盘缘 ±0.033 mm，冠环/裙层直接从盘缘长出；首版用独立水平环 + `holes_fill` 留下 28 边界边，已改），Cap_Top/Bottom 57 顶点 / 99 面 / 0 非流形；`gate06-checks.json` 9 项全过（新增 `D01 dish visibly concave (>= 4 deg)`、`D01 caps manifold`）。**Gate 07/08/09 rev-003**（`geeone-lookdev-r003.blend`，几何 rev-006）：盘 anisotropic 0.7→0.4、同心 bump 0.25→0.12 无扭曲，灯光/天空/地面不变；新增 `disc-macro`（复现用户 08:25 参考截图角度）；Cycles 96 spp 七视图 + `lookdev-review-board.png` + `cap-14-slices-review-board.png`（参考截图 vs rev-002 vs rev-003）+ 36 帧转台。disc-macro / cap-macro 中 14 个扇区有明暗台阶、硬折边、盘凹可见。Gate 02/03/05 保持 approved，各加 warn `d01-amended-1942` / `cap-block-amended-1942` / `cap-dish-amended-1942`（用户未要求重出白模）。未导出、未进 Unity、未 build、未安装；视觉批准待确认，未推送手机。validator 0 errors、0 missing（rev 59）。
- 2026-09-07 22:51 用户对 lookdev rev-003 顶视（红箭头指盘外盖缘带）：“就这个 bevel 可以再厚一点。就是这两片龙鳞的这个高度可以再高，然后中间的那个内凹的效果感觉还是不够明显。”（原话 + 截图存 `evidence/02-analysis/rev-006/user-instructions-2026-09-07-2251.md` / `user-markup-2026-09-07-2251-cap-bevel.png`）。**spec v20**：D01 盘凹 5°→8°（凹深 1.48→2.32 mm@85）、盘径 0.82→0.80 盖（实测区间 0.80–0.85 下限，盖缘带 0.18→0.20 盖宽）；D02 冠环 0.10@20°→0.09@18°；D03 裙两排 0.06@45°/0.02@75° → 0.07@50°/0.04@72°（两排高 2.78→4.26 mm，+54 %）、盖侧高 0.14→0.16 R（原读数 f0226 单帧 ±20 %，+14 % 在区间内）；D09 毂座/暗缝高 = 盖侧 − 三层落差 = 0.0456 R（2.42→1.94 mm）。全部 provisional。`export_geeone_gate02_geometry.py` 增加 `--out`，合同导出到 `06-geometry/rev-007/`。**Gate 06 rev-007**：`finalize_geeone_geometry.py` 盖重建 + 新增 `rebuild_hub_seat`（毂座随盖唇高度重建），Cap 57/99/0 非流形，Rotor 3393/3208/0；`gate06-checks.json` 11 项全过（新增 `D02/D03 each tier steeper`、`D03 tiers drop <= side height`）。**Gate 07/08/09 rev-004**：材质/灯光/环境与 rev-003 完全相同，在几何 rev-007 上重渲七视图 + 36 帧转台；`cap-tiers-before-after-board.png`（rev-003 vs rev-004：顶视盖局部 / cap-macro / disc-macro / low）、`cap-section-v19-vs-v20.png`（合同直接生成的盖 A–A 剖面，标注凹深/两排鳞高/盖侧/毂座 mm）。Gate 02/03/05 保持 approved，各加 warn `cap-amended-2251` / `cap-block-amended-2251`；`reference-cad-from-video-v17.png` 仍是 v18 层值（图未重画，spec 为机器可读权威）。未导出、未进 Unity、未 build、未安装；视觉批准待确认，未推送手机。validator 0 errors、0 missing（rev 60）。
- 2026-09-08 07:13 用户：“OK还有一点就是这个陀螺的三个页面是可以转的，你确保在结构上是正确的，没问题的话你可以推进下一步。”→ 按原话登记 **Gate 07/08/09 rev-004 approved**（chat；证据 = 评审板 + 36 帧转台 mp4，用户 IDE 中打开）；结构条件转入运动学检查。13:21 用户附转台低角度帧：“这个不是一体的，叶片是分开转的。”→ **Gate 06 rev-007 rejected**（原话入 historicalDecisions；毂座坐在实心转子上，盖 / 毂 / 叶片读成一体）。修正 **spec v21**（D03/D09）：转子中心通孔 R0.425 R（18.1 mm）；毂改为一根**静止** `Hub_Core` R0.41 R（17.4 mm）从下盖唇穿过转子到上盖唇（两端埋入盖体 0.002 R）；径向间隙 0.015 R = 0.64 mm；盖缘外悬毂 0.075 R（受盖下连接环 ≥ 2.5 mm 约束，18:33 的“稍微盖住”量为占位）。**Gate 04 rev-006**（`architecture.md`：Fixed_Root = Cap_Top + Cap_Bottom + Hub_Core；Rotor_Root = Rotor_Body，绕 Blender Z / Unity Y）ready_for_review，rev-005 批准保留为历史。**Gate 06 rev-008**：`finalize_geeone_geometry.py` + `cut_rotor_bore`（EXACT，192 段）+ `rebuild_hub_core` + `kinematic_checks`（射线实测缺口连接环 2.97 mm；盖足迹内转子最高点到盖唇 0.52 mm；转子质心离轴 7e-5 R；|Ixz|,|Iyz|/Izz < 1e-6；Izz/Ixx 1.98）+ 半剖 Workbench 渲染（静止件蓝 / 转子灰）；`gate06-checks.json` 20 项全过（12 几何 + 8 运动学）；Rotor 4737/4316/0 非流形。**Gate 07/08/09 rev-005**：材质 / 灯光 / 地面与已批准 rev-004 完全一致，在 rev-008 上重渲；新增 Cycles 半剖两视图 + 交界特写 + **转子单独旋转 24 帧**（`spin/geeone-rotor-spin.mp4`，盖与毂芯静止）+ 36 帧转台；`kinematic-review-board.png`、`lookdev-review-board.png`。Gate 02/03/05 保持 approved 并标 warn。未导出、未进 Unity、未 build、未安装；视觉批准待确认，未推送手机。validator 0 errors、0 missing（rev 61）。
- 2026-09-08 13:55 用户：“继续吧”→ 按原话登记 **Gate 04 rev-006 / 06 rev-008 / 07/08/09 rev-005 approved**（chat；半剖 + 转子单独旋转录像 + 转台）→ 9/12。随后推进：**Gate 10 rev-002**（`evidence/10-export/rev-002/export_geeone_gate10.py`：只保留 Rotor_Body / Cap_Top / Cap_Bottom / Hub_Core，apply 倒角，mm→m（2R = 0.085 m provisional），层级 `GEEONE_TriSpinner/Rotor_Root[Rotor_Body]` + `Fixed_Root[Cap_Top, Cap_Bottom, Hub_Core]`，材质按名 `M_Geeone_Satin / M_Geeone_DiscTurned / M_Geeone_HubDark`；FBX（-Z/Y，FBX_SCALE_UNITS）+ GLB + collision FBX（转子凸包 + 盖径圆柱）；GLB/FBX 往返 9 项检查全过：外接圆 0.085 m、厚 10.07 mm、通孔 18.06 mm 居中、四网格、归属、材质；`export-manifest.json` 全哈希；Workbench 回读 hero/low/top + 24 帧 orbit）。**Gate 11 rev-002**：`Assets/_Fidgeting/Models/GeeoneTriSpinner/GeeoneTriSpinner.fbx`（+ `_Collision.fbx`）；`ThreeBladeSceneBuilder.InstallGeeoneVisuals`（替代 DragonScale rollback：Rotor_Root → RotorDynamic，Cap_Top/Cap_Bottom → TopCap/BottomCap，Hub_Core → HubStatic，180° yaw，隐藏 procedural + BearingBalls，orbit 焦点 Cap_Top）；`ThreeBladeMaterialFactory` 新增 `M_GeeoneSatin` 0.64 / `M_GeeoneDiscTurned` 0.68（URP Lit——径向 brushed shader 会把 14 扇区抹平，已弃）/ `M_GeeoneHubDark` 0.55；`ProductAppearanceCustomization` 贴纸接收面加 `Cap_Top`；编辑器预览工具路径回退到 `HubStatic/TopCap/Cap_Top`；`GeeoneShippingPreviewCapture.CaptureAll`（batchmode）输出中性轮廓 + `unity-import-parity-report.json`；`build_geeone_parity_report.py`：轮廓 IoU 顶视 **0.998** / hero **0.995**，平面外接 1.7327 R 两侧一致，三角数一致，转子转 / 盖 + 毂芯静，零初速，yaw 180 → `parity-report.json` PASS。**Gate 12 rev-006**：`ThreeBladeMetalOriginal.unity` 已 batchmode 重建；出货预览 phone / hero / top / 左右 oblique / low / library（`shipping-review-contact-sheet.png`），library 缩略图写入 `Assets/Plugins/iOS/Thumbnails/Models/product-thumbnail-metal-three-blade.png`（被驳回则 git 还原）。测试：`GeeoneTriSpinnerAssetTests`（新，资产两组 + 场景归属 / 85 mm / 材质 / 隐藏件 / 爆炸顺序 / 零角速度 / 无 DragonScale 依赖）；`BlenderDragonScaleAssetTests` 移除场景用例（FBX 资产用例保留为 rollback）；`ProductArchitectureTests` / `SpinnerProgressionTests` 改为 `Cap_Top` / `Rotor_Root/Rotor_Body`（皮肤 ≥ 4 个渲染器）。EditMode 相关套件 **121/122**，唯一失败 `RuntimeAndLiquidGlassUi_AreWiredForGrowthAndOfflineReturn`（Swift `Label(` 文案检查）与模型无关；首轮全量里另有 8 个失败均为其他在途任务（Swift 文案、Build Settings 缺 MagneticFanCard、slide-tile 取景、环境 `_GlowScaleB`、`Assets/StreamingAssets` 存在），与本模型无关。**未 build、未安装；视觉批准待确认，未推送手机。** validator 0 errors、0 missing（rev 63）。
- 2026-09-08 14:56 用户：“这些预览图好像被拉伸了。”→ 确认：出货预览纵向拉伸 ≈1.8×。根因：`SpinnerEnvironmentPresenter.Install` 装的 `SpinnerSceneParallaxController.Configure` 把当时（batchmode 4:3）的投影矩阵存为 baseline 并显式写回 `camera.projectionMatrix`，之后改 `camera.aspect` 不再生效，渲进 720×1280 目标即被拉伸；`SpinnerEnvironmentPreviewCapture` 早已用 `ResetProjectionMatrix()` 规避，`RecoveryApprovalPreviewCapture`（RecoveryApprovalV22 旧图）与首版 `GeeoneShippingPreviewCapture` 没有。修复：`GeeoneShippingPreviewCapture.PortraitProjection()` 每次渲染前 `ResetProjectionMatrix` + 设 aspect；重拍 phone / hero / top / 左右 / low / library（顶视 h/w 0.885，理论 0.907@89°）。Gate 12 rev-006 资产哈希刷新，validator 0 errors（rev 64）。仍 ready_for_review；视觉批准待确认，未推送手机。
- 2026-09-08 15:45 用户：“感觉挺好的，但是为什么光照感觉特别暗，特别黑？”→ 根因：metal-three-blade 共用 `SpinnerImageBasedLightingController` 的 soft-metal 策略（直射 ×0.36、环境 ×0.42、反射 ×0.35，再乘 trim）是为峡谷 library 卡防过曝；出货详情页黑底无环境反弹，硬切面缎面钢高光极亮、背光面仍近黑。修复：`SpinnerImageBasedLightingController` 新增 GEEONE 详情提亮（详情模式抬高 key/fill/visibility fill 下限、环境光 floor、反射 boost）；`ThreeBladeSceneBuilder` 启用 HDR + ACES、`postExposure` +0.75、对比度 4、场景灯加强；`GeeoneShippingPreviewCapture` rev-007 捕获前强制详情灯光配方并重拍七视图。中心 hero 区 mean 0.199→0.246、P90 0.317→0.762（rev-006 vs rev-007）。Gate 12 rev-007 ready_for_review；视觉批准待确认，未推送手机。
- 2026-09-08 18:36 用户：“推到手机上吧”→ chat 视觉批准 + 真机推送。**Build 47**（`geeone-tri-spinner-build47-20260908T103620Z-snapshot`）：EditMode 预检 152/152；`com.jiaweizhou.fidgetspinner.codex` v0.1.0 已安装并启动（`installed=true launched=true pid=45090`）。证据：`evidence/12-shipping/rev-007/device-delivery/geeone-tri-spinner-build47-20260908T103620Z-snapshot/delivery-result.json`。真机交互验收当时待用户确认。
- 2026-09-08 18:5x 用户（新线程）：“GEEONE 龙鳞三叶（metal-three-blade）12 Gate 已完成，Build 47 已装到手机，用户真机验收通过。”→ **真机验收通过**。登记（`register_geeone_gate12_r007_device_accepted.py`，pipeline.json rev 65→66）：Gate 12 由 rev-006 升为 **rev-007 approved**（18:36 原话“推到手机上吧”，evidenceMode = 七张重拍出货视图 + 随后的设备 build；rev-006 记 superseded，其 15:11 批准保留为历史，15:45 光照反馈原话入 historicalDecisions）；rev-007 资产 21 项全哈希：场景、`SpinnerImageBasedLightingController.cs`、`ThreeBladeSceneBuilder.cs`、`GeeoneShippingPreviewCapture.cs`、七视图 + 新拼 `shipping-review-contact-sheet.png`（`build_geeone_shipping_contact_sheet.py`，仅排版）、library 缩略图（与出货 `product-thumbnail-metal-three-blade.png` 同字节）、Build 47 快照 `delivery-result.json` / `unity-editmode-results.xml`（152/152）/ `install.json` / `launch.json` / `source-hashes-after-export.txt`、18:34 预检快照、以及新写的 `device-acceptance.json`（用户原话 + delivery-result 哈希；不改动不可变快照）。validations：`device-build` pass、`device-acceptance` pass、`approval-evidence-mode` warn（chat 批准，无交互式 Unity 运行会话）。`currentState.deviceStatus = build-47-installed-launched-user-device-accepted-2026-09-08`，`rebuildRequested=false`，`model.status = shipping-current-geeone-device-accepted`，`model.scenePath` 改为 `ThreeBladeMetalOriginal.unity`（原 `ThreeBladeEDC.unity` 是 `pointed-three-blade` 的场景）。history.ndjson 追加 4 条（revised / approved / delivery / device-accepted）。`validate_model_pipeline.mjs metal-three-blade`：12/12、0 errors、0 missing（rev 66）；`validate-pipelines.mjs`（只读）metal-three-blade 0 errors，未运行 `--refresh`（避免改动其他模型清单）。`tests/pipeline-core.test.mjs` 的 readiness 期望同步为 metal-three-blade `shippingReady=true / rebuildRequested=false`；`npm test` 213/253，40 个失败与改动前逐条相同（magnetic-slide-tile / premium-display-case 既有漂移，本轮未处理）。设计圣经 `FDB-PREF-032/033` DeliveryState 同步为 device accepted，rev-007 七视图复制到 `Docs/DesignBibleAssets/geeone-tri-spinner-shipping-*-20260908.png`。
- 下一步（待用户决定，本轮未动）：`FDB-PREF-032` 的 catalog 收敛——`gold-four-wing`（`ImportedSpinner.unity`）与 `pointed-three-blade`（`ThreeBladeEDC.unity`）两条旧 Rotor 条目是否下线、并入 `metal-three-blade`，涉及 `SpinnerModel.allCases` / `ProductCatalog` / `ProductCatalogMigration`（已有选择迁移）/ 成长与皮肤存档 key / Gacha 奖品目录 / Build Settings 场景表 / `ProductArchitectureTests` 场景断言 / library 缩略图。属于产品决策，需用户明确指令后另开 feature task；任何 catalog 变更前不得再 build / 安装。85 mm 及其他 provisional 尺寸若要转 measured，需要用户提供实测卡尺值并新开 Gate 03 修订。

## 2026-09-05 统一三叶陀螺：rev-003 三点驳回 → rev-004 圆锥锯齿楔环 + 泪滴厚叶片（Blender Cycles，未进 Unity）— 已被视频 intake 取代，保留为历史

> **当前状态：rev-003 被用户 19:43 三点驳回（楔环成“城墙”、叶片成扇形桨露机身、叶片太薄）。rev-004 已按驳回重建并登记为 Gate 02 rev-005、Gate 03–06 rev-004，全部 `draft` 等待用户批准。出货 Unity 资产、场景、catalog 未改动；未构建、未安装、未推手机。视觉批准待确认，未推送手机。**

- 驳回原文完整存 `evidence/06-geometry/rev-003/user-rejection-2026-09-05-b.md`（user-input 资产 `tri-r5-user-rejection`）。2 条 rev-4 claim superseded，7 条 rev-5 claim 新增；修正表 `evidence/02-analysis/rev-005/analysis-corrections-rev5.json`。
- 盖：平盘 Ø24.4 z=7.25 是最高点；楔环为 25° 圆锥，内环 24 点在盘边、外环 24 点错半步且 ±0.55 mm 锯齿 → 48 个三角平面，尖端向内 24 / 向外 24，相邻法线 9.3–16.1°，单面斜 19.5–29.3°（均值 24.4°）；外沿均值 z=4.81，低于叶面 0.94 mm；暗裙至 z=2.5。暗缝 0.8 mm（沉孔 Ø36.44 vs 盖 Ø34.84）。
- 叶片：泪滴轮廓——缺口 V 60° 起于暗缝边（apex r=18.22–18.55）、凸 Bezier 侧边、R12 外弧占 ±60°、最大半宽 16.4 mm；厚 11.5 mm；顶面 = 2 个 10.2° 屋脊面 + 1 个 32° 端面斜切（每叶 3 大平面 + 镜像），竖直侧壁最宽处 5.6 mm；0.5 mm 两段倒角在凸包阶段施加；侧壁作为连续曲面 smooth，其余全部 flat。毂领删除：三叶根部在暗缝边相接，`hubVisibleInTopView=false`。机身 = 三个各自沉孔切割的凸包叶片 + Ø35.8 暗色轴承座环 join；每壳 manifold（0/0/0），三角 5864。
- 渲染：Cycles/Metal 96 spp denoise（Eevee 不出各向异性；平盘径向各向异性 0.85 + 同心 Bump 0.09 现已可见）；白模仍 Workbench。新增 `cap-profile`、`notch-macro` 机位。
- 用户指令内部矛盾的处理（`tri-r5-notch-interpretation`）：“两侧向内收成约 60° 夹角”按“相邻叶片间 V 缺口 60°”解释——若按单片泪滴切线夹 60° 字面构造，R12 切线在 r≈18 处相距 49°，机身必外露，与“机身被完全包住”矛盾。评审板已标注，待用户裁决。
- 新悬案：台面 0.70（用户）+ 25° 斜 ⇒ 楔环外沿低于叶面 0.94 mm，暗缝看起来比 0.8 mm 深；照片值 0.797 ⇒ 外沿与叶面齐平（0.15 mm）。已出同机位对比 `evidence/06-geometry/rev-004-variant-table-0797/`（仅对比、未导出、不是 revision）。
- Obsidian vault 复扫（`evidence/02-analysis/rev-005/discovery-log-rev5.json`）：22 条相关笔记 / 40 张图，本产品只有 Gate 01 已归档的 7 张 GEEONE 实拍；TW 玲珑云三叶、钛 storm 三叶为同类不同款，仅作语境。
- 证据：`evidence/05-blockout/rev-004/`（clay 6 视 + `builder-snapshot-rev-004.py`）；`evidence/06-geometry/rev-004/` 六正交、workbench、hero、双斜视、low、cap-macro、cap-profile、notch-macro、exploded、`review-board.png`、`dimension-overlay.png`、`pivot-overlay.png`、`geometry-validation.json`。rev-003 证据与 builder 快照保留为驳回历史。导出 `ArtSource/UnifiedTriSpinner/UnifiedTriSpinner.{blend,fbx,glb}` 与 `_Collision.fbx` 已随构建更新，尚未登记 Gate 10，也未导入 Unity。
- 验证：`validate-pipelines.mjs --refresh` 与 `validate_model_pipeline.mjs metal-three-blade` 均 0 errors（rev 24）；Gate 06 十项验证全部 pass；Gate 01–03 仅剩“无实测 mm”一项 fail。登记脚本现同步 `pipeline-core` 的 stage digest，refresh 不再把自身登记误判为过期；Gate 01 因此从误标 stale 恢复 draft。
- 2D CAD（用户 22:00 要求“先出平面图 CAD 图”）：`tools/blender/export_unified_tri_spinner_cad.py` 在 Blender 内 import builder 导出 `evidence/06-geometry/rev-004/cad-geometry.json`（轮廓、屋脊高、缺口尖点、盖剖面、楔环顶点，全部来自 builder 函数，不另行推导）；`tools/model-provenance-explorer/draw_unified_tri_spinner_cad.py` 由该 JSON 出 `cad-sheet-1-plan-sections.{png,pdf}`（顶视 + 过叶片轴剖面 A-A + 最宽处横剖 C-C + 楔环展开 detail B/B'）与 `cad-sheet-2-decision-overlays.{png,pdf}`（台面 0.70/0.797、缺口解释 ①/② 叠加）。已登记为 Gate 04 rev-004 `structural-cad` 资产（`tri-r5-cad-*`），验证项 `structural-cad-present`。
- 工作台修正：`pipeline-core.mjs refreshManifest` 现只让“仍在某阶段 artifactIds 中”的资产触发 stale；孤儿资产（如早期指向活文档设计圣经的 `tri-contract-design-bible`）只刷新哈希，不再在每次改文档时把 Gate 03–12 标过期。`npm test` 213/253，40 个失败在改动前后完全一致（magnetic-slide／premium-display-case 既有清单漂移），本轮未处理。
- 待办：用户批准 Gate 02–06（并裁决台面 0.70/0.797、缺口解释、叶根暗三角）后进入 Gate 07 材质（圆盘各向异性在 URP 需烘法线）、Gate 08 灯光、Gate 10 导出登记、Gate 11 Unity 对齐、Gate 12 shipping 预览；三个旧 catalog 条目在 Gate 12 批准后再收敛。

## 2026-09-05 统一三叶陀螺：rev-002 五点驳回 → rev-003 两层盖 + 实心硬切叶片（Blender，未进 Unity）— 已被 rev-004 取代

> **当前状态：用户要求把三款三叶 Rotor 合成一款“结构正确、细节到位、光感质感拉满”的模型（`FDB-PREF-032`）。第一版几何（rev-002）被用户五点驳回，rev-003 已按驳回逐点重建，Gate 02 rev-004、Gate 03–06 rev-003 全部 `draft` 等待用户批准。出货 Unity 资产、场景、catalog 未改动；未构建、未安装、未推手机。视觉批准待确认。**

- 驳回链：Gate 02 rev-002（GEEONE 53.6% 大盖 + 规则梯形冠环）被“看到了，但是完全不对啊”驳回 → rev-003 把放射楔放到台面、冠环做成不规则鳞片 → 用户再次驳回（原文存 `evidence/06-geometry/rev-002/user-rejection-2026-09-05.md`，user-input 资产 `tri-r4-user-rejection`）：① 盖应为平车削盘（≈0.70 盖径）+ 外圈规则向下楔面，无随机鳞片；② 盖只高出叶面 1–2 mm、黑线约 1 mm；③ 叶片实心、向中心收窄、外端大圆角平面、4–5 大平面硬切、竖直侧壁；④ satin 非镜面，各向异性只给圆盘；⑤ 倒角 0.5 mm 2–3 段。5 条旧 claim superseded，5 条 rev-4 claim 新增（`evidence/02-analysis/rev-004/analysis-corrections-rev4.json`）。
- rev-003 构建（`tools/blender/build_unified_tri_spinner.py`，确定性 bpy，无随机抖动，Blender 5.2）：盖 = 平台面 Ø24.4（0.70×Ø34.8）z=6.5（高出叶面 1.5 mm）+ 24 楔 48 平面（每半面为 48 边棱台面绕自身中线 ±11° 旋转，精确平面；楔面平面与水平台面相交形成细锯齿边界，台面倾斜 0.0°；外缘沿 r=17.4 圆柱脊谷 ±0.22 mm；相邻法线 18.7–25.0°）+ 楔环外缘 z=4.1 沉入缝内（斜 25°）+ 暗裙。缝 = 沉孔 Ø36.8 与盖 Ø34.8 之间 1.0 mm，毂领改为机身亮金属，只有沉孔壁／底暗。叶片 = 确定性控制点凸包：根部半宽 12.0 mm、外端沿外接圆大弧、顶面每叶 7 个大平面（脊线 + 侧切 + 端切）、竖直侧壁 3.8 mm、0.5 mm 2 段倒角、无口袋；叶根在 r=18.5 mm 切除；叶厚 9.9 vs 毂 10.0。材质 body 0.36 / wedge 0.34 / table 0.32（仅台面径向各向异性 0.7 + 同心 bump）；key 光 55 mm。旋转体 manifold（0/0/0），三角 5432。
- 照片 vs 用户指示的两处差异已登记为 claim 待裁决：台面比 0.797（照片）vs 0.70（用户，本轮采用）；geeone-01 每个叶根紧贴盖处的暗色三角凹陷（照片）vs 实心（用户，本轮采用）。
- 证据：`evidence/05-blockout/rev-003/`（clay）；`evidence/06-geometry/rev-003/` 六正交、workbench、hero、双斜视、low、cap-macro、exploded、`dimension-overlay.png`、`pivot-overlay.png`、`geometry-validation.json`。rev-002 证据完整保留为驳回历史。导出 `ArtSource/UnifiedTriSpinner/UnifiedTriSpinner.{blend,fbx,glb}` 与 `_Collision.fbx` 已随构建更新，尚未登记 Gate 10，也未导入 Unity。
- 验证：`validate-pipelines.mjs --refresh` 与 `validate_model_pipeline.mjs metal-three-blade` 均 0 errors（rev 20）。`npm test` 253/238；15 个失败全部为 magnetic-slide-tile／premium-display-case 既有状态漂移，与本模型无关，本轮未处理。
- 待办：用户批准 Gate 02–06 后进入 Gate 07 材质（圆盘各向异性在 URP 需烘法线）、Gate 08 灯光、Gate 10 导出登记、Gate 11 Unity 对齐、Gate 12 shipping 预览；三个旧 catalog 条目在 Gate 12 批准后再收敛。

## 2026-09-07 Gacha reveal v2 打磨五（R042）：canvas 时间线落码——Pack 下落 0.58 s、抽出提前、标签 3.26 s

> **当前状态：用户在 `gacha-reveal-timeline` canvas 上调整三段时长并一键应用，常量已落码、测试同步、Gate 12 Simulator 重新导出并录屏（`evidence/12-shipping/rev-010/`）。视觉批准待确认，未推送手机。**

- 常量：`nativeHybridPackDepartureDurationSeconds 1.0 → 0.58`（曲线、50% 舞台位移、14°、78% 起淡出不变）；`PullStartSeconds 0.35 → 0.24`；`LabelSeconds 3.37 → 3.26`（回弹后 0.80 s 间隔不变）。其余 17 个 canvas 参数与源码原值一致，未改。
- 新拍点（case play 为零点）：抽出 0.24–1.02 → 落位 1.26 → 停顿 1.66 → 预备 1.86 → 翻转 2.28（过 90° ≈ 2.07）→ 回弹 2.46 → 标签 3.26；T0 相对：reveal T0+2.77、complete T0+3.96、面板 T0+4.26。
- 测试：`GachaShippingRevealChoreographyTests.TimelineMatchesTheSpecBeats` 全部拍点改为新值并新增「标签 − 回弹结束 = 0.80 s」断言；Swift harness「Pack falls 0.58 s」。canvas `DEFAULTS` 同步为 `packLead 240 / packFall 580`，保持「默认值 = 当前源码」。
- 验证：Unity EditMode 46 passed / 2 skipped；Swift harness 141/141；`GachaShippingNativePreview` BUILD SUCCEEDED；export `gate12-export13.log` Success；`xcodebuild` Release Success（`gate12-xcodebuild16.log`）。录屏实测（raw，T0 ≈ 9.75 s）：case play 10.45、Pack 落 10.45–11.03、reveal 闪光 12.5（T0+2.77）、标签 13.7（T0+3.96）、面板 14.1–14.4，与新常量一致。录屏 `Artifacts/PackTearNativeCandidate/r042-gacha-reveal-v2-timeline-canvas/r042-gacha-reveal-v2-clear.mp4`（实速 + 0.5×）、`r042-pack-fall-20fps.png`、`r042-standard-refined-end.png`、`r042-contact-sheet-5fps.png`；pipeline `evidence/12-shipping/rev-010/`，history events `15d8c7a2-…`（rev-009 经 canvas 调整）、`51e64c5f-…`（rev-010 ready）。
- 录屏注意：9.0–10.4 s 的选中／撕封阶段带有并行任务 FDB-GAC-035 R042 arc-bands 背景（`GachaPackArcBackdropRules.baseOpacity 1.0`，不透明午夜底 + 四色带），是同一工作树中另一任务的进行中改动，不属于本 rev；评审本 rev 请只看时间线拍点。

## 2026-09-07 Gacha reveal v2 打磨四（R041）：文案顺序、购买按钮、抽出提速、可交互时间线

> **当前状态：用户三项打磨 + 一项工具需求已落地并重录（`evidence/12-shipping/rev-009/`）。视觉批准待确认，未推送手机。**

- `ProductPackTierCaption`：「1 张抽取券／包」移到 tier 名上方、字号 footnote；tier 名 title2；说明在下；整体左对齐。中性档（STANDARD）底色 glow 强度 ×0.55（`neutralGlowStrength`），避免提饱和后的灰雾。
- CTA 文案：`购买 \(selectedPack.title)`（购买 STANDARD / 购买 REFINED …）。
- 抽出→落位提速：`PullSeconds 0.90 → 0.78`、`SettleSeconds 0.30 → 0.24`，`LabelSeconds 3.55 → 3.37`（回弹后的间隔不变）；下游拍点整体 −0.18 s。
- 可交互时间线：canvas `gacha-reveal-timeline.canvas.tsx`——每段一个 slider（Swift 与 Unity 两栏），实时重算 T0 相对时间线（Gantt + 关键节点）、翻转前静止是否 ≥ 400 ms、导出 `GachaShippingRevealChoreography.cs` / `FidgetGachaPackPresentation.swift` 常量，并可一键让 agent 应用。默认值 = 当前源码。
- 验证：Swift harness 138/138；Unity EditMode 46 passed / 2 skipped；export `gate12-export12.log` Success；`xcodebuild` Release Success（`gate12-xcodebuild15.log`）。录屏 `Artifacts/PackTearNativeCandidate/r041-gacha-reveal-v2-caption-timeline/r041-gacha-reveal-v2-clear.mp4`、`r041-standard-refined-end.png`。

## 2026-09-07 Gacha reveal v2 打磨三（R040）：STANDARD 舞台不再发蓝

> **当前状态：用户指出 rev-007 中 STANDARD Pack 的舞台被染成钢蓝（"这个蓝色哪来的，不对"）。根因是 `backdropRGB` 强制最低饱和度 0.45，把中性银灰 accent（0.58, 0.60, 0.64）造出了蓝色，并经 `EnterGachaStageFromNativeUi` 传给 Unity dimmer。已修并重录（`evidence/12-shipping/rev-008/`）。视觉批准待确认，未推送手机。**

- 规则：accent 饱和度 < 0.2（`neutralSaturationThreshold`）视为中性档，保持原色相/饱和度不动；只有彩色档（钢蓝、氧化铜、香槟金…）做 ×2.4 提饱和（上限 0.85）。Unity `GachaRevealStageFX.SetDimTint` 的明度按饱和度从 0.08（中性）插值到 0.30（全饱和），STANDARD 舞台回到近黑压暗，REFINED 等保留自身色相。
- 验证：Swift harness 130/130（新增「STANDARD backdrop 保持银灰，不发蓝」断言）；Unity export `gate12-export11.log` Success；`xcodebuild` Release Success（`gate12-xcodebuild13.log`）。录屏 `Artifacts/PackTearNativeCandidate/r040-gacha-reveal-v2-neutral-stage/r040-gacha-reveal-v2-neutral-stage-clear.mp4`、`r040-carousel-stage-hold.png`；pipeline `evidence/12-shipping/rev-008/`。

## 2026-09-06 Gacha reveal v2 打磨二（R039）：Pack 落到底再淡出、粒子加强、舞台色相、左对齐、无底 CTA

> **当前状态：用户看过 rev-006 录屏后提出五项打磨，已全部落地并重录（`evidence/12-shipping/rev-007/`）。视觉批准待确认，未推送手机。**

- **Pack 下落**：位移改为舞台高度的 50%（中心 44% → 94%），1.0 s `cubic-bezier(0.33,0,0.2,1)`，后仰 14°；不透明度在前 78% 保持 1，只在最后 22% 淡出（`packDepartureDropFraction 0.5`、`packDepartureFadeStartProgress 0.78`）。`ProductPackTearLayout.frame` 改为按舞台高度取位移，`packDepartureDropPoints` 删除。
- **粒子**：数量 ×2（heirloom 240 / signature 96 / refined 56 / standard 0），尺寸 7–15 px，初速 260–560 px/s，重力 −60 px/s²，寿命 0.9–1.6 s，颜色向白色偏 45%，改用 32 px 径向软圆 sprite（原为默认方块），沿盒体轮廓 0.82–1.12 抖动生成并前移 3 cm 免被透明外壳遮挡。
- **舞台色相**：native 底色 opacity 0.42/0.16/0.24/0.12，并用 HSV 提饱和的 tier accent（`GachaPackStorefrontBackdropRules.backdropRGB`：饱和度 ×2.4 夹在 0.45–0.85，明度 ≥ 0.62；`GachaPackTier.storefrontBackdropRGB`）；Unity 舞台 dimmer 用同一 accent 着色（`EnterGachaStageFromNativeUi` 载荷 `r,g,b`，`GachaRevealStageFX.SetDimTint`，HSV 明度 0.30）。修了一个会吃掉色相的 bug：`GachaShippingRevealDirector.Begin` 先调 `Dismiss()`，把从 storefront 接管的 stage FX 一起 dispose 了，导致 case 首帧蓝色 wash 消失——现在 Begin 会保住已接管的 FX。
- **文案与 CTA**：`ProductPackTierCaption` 新增 `alignment`（默认 `.leading`），标题/价格/概率左对齐；「选择此 Pack」直接用 `ProductPrimaryActionButton`，去掉外层 `ProductBottomActionDock` 底板（handoff/receiptRecovery 的 dock 保留）。
- 验证：Unity EditMode Gacha* + Gate12 45 passed / 2 skipped；Swift harness 129/129（新增 backdrop 饱和度、下落参数、淡出起点断言）；`GachaShippingNativePreview` BUILD SUCCEEDED；Unity export `gate12-export10.log` Success，`xcodebuild` Release Success（`gate12-xcodebuild11.log`）。录屏 `Artifacts/PackTearNativeCandidate/r039-gacha-reveal-v2-polish2/r039-gacha-reveal-v2-polish2-clear.mp4`（实速 + 0.5×）、`-sheet.png`、`r039-reveal-burst-10fps.png`、`r039-carousel-stage-end.png`；pipeline `evidence/12-shipping/rev-007/`，history events `ba0aba2d-…`（rev-006 用户意见）、`9ba49460-…`（rev-007 ready）。
- 仍未做：§8 卡面资产、洞穴 saturation 曲线（现以着色 dimmer 近似）、逐叶点亮、撕纸音效。

## 2026-09-06 Gacha reveal v2 打磨（R038）：单陀螺、Pack 先出场、下落放慢、carousel 悬浮

> **当前状态：用户看过 rev-005 录屏，"整体来说是 OK 的"，提出四项打磨。已全部落地并用 Gate 12 Simulator 工程重录（`evidence/12-shipping/rev-006/`）。视觉批准待确认，未推送手机。**

- **"卡里有两个陀螺"**：竖起来的那个不是奖品，是 Library 当前展示的三叶陀螺本体——位于场景原点，对 reveal 相机正好是侧面（一条横杠 + 轴承块），透过收藏盒透明外壳漏出；卡片翻转时它不动，所以两面都在同一处。修复：`FidgetAppCoordinator.HideLibraryProductForGacha()` 在 `AcquireGachaCamera` 时关闭产品根下的 Renderer（跳过挂在相机／`SpinnerEnvironmentPresenter` 下的洞穴图层，否则背景会一起变黑——rev-006 首次录屏就踩到了这一点），`RestoreLibraryProductAfterGacha()` 随相机恢复。另在 `PremiumDisplayCaseShippingPresentation.AttachContent` 隐藏 ContentFit 下的任何 authored 占位物（`Resources/Gacha/PremiumDisplayCase.prefab` 带开发用 `DevelopmentPlaceholder_Coin`；shipping 用的 Gate12 R004 prefab 没有），并加 `ContentFitHoldsOnlyAttachedContent` 断言。
- **Pack 先出场、卡后入场**：Unity `HasCrossedPackLip` 在 case play 首帧即为真 → native Pack 立即开始下落；收藏盒起始位置改为顶边低于袋口 12 pt（`PullStartPeekPoints -12`，完全被袋身挡住），`PullStartSeconds 0.35` 后才开始抽出，所以先是 Pack 的下落把卡露出来，再是卡上升。下游拍点整体 +0.10 s（`LabelSeconds 3.55`，reveal ≈ 2.36 s）。
- **Pack 速度**：`nativeHybridPackDepartureDurationSeconds 0.42 → 0.80`，`cubic-bezier(0.33,0,0.2,1)`；前 35% 保持实体，之后 smoothstep 淡出（`packDepartureOpacity`）。淡出整形必须逐帧按 retreat 求值，因此新增 `ProductPackDepartureEffect: ViewModifier, Animatable`（`animatableData = retreat`），否则 SwiftUI 只会把最终 opacity 线性插值，实体段丢失。
- **carousel 悬浮**：`ProductPackIdleFloat`（`GachaPackIdleMotion`：Y ±6 pt / 2.4 s、yaw ±4° / 3.2 s、换页停稳后 ramp-in、拖动中暂停、Reduce Motion 关闭）挂在 carousel 选中 Pack 上；Gate 12 自动预览新增一次 STANDARD → REFINED → STANDARD 换页演示。
- 验证：Unity EditMode Gacha* + Gate12 45 passed / 2 skipped（新增 `HideLibraryProductForGacha`/`RestoreLibraryProductAfterGacha` 接线断言、`ContentFitHoldsOnlyAttachedContent`）；Swift harness 123/123；`GachaShippingNativePreview` BUILD SUCCEEDED；Unity export `Builds/iOS/Logs/gate12-export8.log` Success，`xcodebuild` Release Success（`gate12-xcodebuild9.log`）。录屏 `Artifacts/PackTearNativeCandidate/r038-gacha-reveal-v2-polish/r038-gacha-reveal-v2-polish-clear.mp4`（实速 + 0.5×）、`-sheet.png`、原始 `-raw.mp4`；pipeline `evidence/12-shipping/rev-006/`（含 20 fps Pack-先落 strip 与正反面全尺寸裁切），history events `a3358c6c-…`（rev-005 用户打磨意见）、`3df370ff-…`（rev-006 ready）。
- 运行环境备注：昨晚 Unity batchmode 卡住 28 min 是 Licensing Client 断连循环（`Channel LicenseClient-… doesn't exist` / `Timed-out after 60.00s`），杀掉残留 `Unity.Licensing.Client` 后恢复；本轮所有 Unity 调用加了 60 s 级 watchdog。
- 仍未做：§8 卡面资产、洞穴 saturation、逐叶点亮、撕纸音效（同 R037 偏差列表）。

## 2026-09-05 Gacha reveal v2（R037）：单条 timeline——撕封 → 抽出 → 卡背停顿 → 翻转 → 稀有度光效 → 结果面板

> **当前状态：用户驳回 Gate 12 rev-004 并给出「Gacha reveal v2 · agent spec」（`FDB-GAC-033`）。Unity + Swift shipping 路径已按 §1–§7 接线并在 Gate 12 Simulator 工程中完整录屏（`ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/rev-005/`）。§8 卡面资产、洞穴饱和度、逐叶点亮、撕纸音效未做（见「偏差」）。视觉批准待确认，未推送手机。**

- 时间轴（T0 = 撕封触发；Unity 侧 `GachaShippingRevealChoreography` 以 case play = T0+0.70 s 为零点）：选中 600 ms `cubic-bezier(0.16,1,0.3,1)` 居中放大 1.18×（carousel Pack 改为 244/1.18 pt，matchedGeometry 进入 244 pt 撕封 Pack），其余元素与 Pack 色相底 250 ms 淡出；Unity `EnterGachaStageFromNativeUi` 在选中时关闭 spinner 相机、把主相机移到 reveal 位、挂 `GachaRevealStageFX` 把洞穴压到 25%（dim 0.75），不再有纯黑态。待机 `TimelineView`：Y ±6 pt/2.4 s、yaw ±4°/3.2 s、封条 8 pt 高光每 1.8 s 扫 0.7 s；封条 72 pt 命中区，横拖 ≥40% 卡宽（`tearTravelPoints 158`，commit 0.62 ≈ 98 pt）或长按 450 ms 自动撕。撕封 320 ms `cubic-bezier(0.83,0,0.17,1)`，撕裂前沿 2 pt 亚光白 `ProductPackTearFrontEdge`；commit 时 `EmitGachaTearSnapFromNativeUi → FidgetHapticRouter.Emit(Pop, 0.7)`（medium）、袋口 `scaleY 1→1.06` 180 ms `cubic-bezier(0.34,1.56,0.64,1)`、封条 480 ms EASE_OUT（rotZ 14°、Y −90 pt、X +60 pt 顺撕向、全程淡出，不悬停）；commit 后隐藏「沿封边撕开」，`progressChrome` 不再显示任何内部状态字（仅保留 `receiptRecovery` 的「等待权威结果」与「跳过展示」）。R036 的 commit 闪白与放射线按 spec 移除（`releaseFlashPeakOpacity 0`、`releaseBurstStreakCount 0`）。
- 抽出：draw 在 commit 发出（`drawAfterLidClearNanoseconds 0`），`startReveal` 不早于 commit+380 ms（`caseReadyMinimumAfterCommitNanoseconds`，即 T0+700）。收藏盒以背面朝前生成在 Pack 内（顶边露出 20 pt：`MouthViewportYFraction 0.68` 对应 44% 居中 Pack 的袋身顶边），`PullProgress` 用 `cubic-bezier(0.2,0,0.1,1)` 900 ms 抽到 apex（中心距顶 28%），settle 300 ms 落到 44%；抽出中 rotX −6°、scale 0.72→1。因盒体比 Pack 矮，直接抽到 44% 会全程被 Pack 遮住，apex 是为让抽出可读的实现决定。抽到 60%（0.54 s）发布 `case-crossing-pack-lip`，native Pack 420 ms EASE_OUT：+120 pt、rotX +10°（`rotation3DEffect` 底边锚点）、opacity→0；盒体 opacity 全程 1。
- 停顿与翻转：卡背停 400 ms，边缘 glow 0→0.5×`glowIntensity`（frosted shell `_RimColor/_RimStrength` 经 `PremiumDisplayCaseDirectedPose.RimColor/RimGlow`）；预备 yaw +12°（背面侧）、scale 0.97、200 ms `cubic-bezier(0.36,0,0.66,−0.56)`；翻转 192°→0° 420 ms `cubic-bezier(0.83,0,0.17,1)`；回弹 −4° 180 ms 正弦；`RevealSeconds` 由 yaw 过 90° 那帧二分解出（≈2.01 s，即 T0+2.71 s）。
- 揭晓光效（过 90° 帧起）：`GachaRevealRarityStyle` 按 rarity 查表——Standard `#9AA3AD`/0.35/flash 0/0 粒子/Pop 0.35；Refined `#5FB8FF`/0.5/0.25/24/Pop 0.55；Signature `#5FB8FF`/0.6/0.4/40/Pop 0.7；Heirloom `#C8F2C0`/1.0/0.85/120/`BadgeUnlocked`。全屏 flash 260 ms（60 ms 线性升、200 ms EASE_OUT 降）、glow 0.5→1.0（120 ms）→0.6（1200 ms）常亮、`ThreeBladeInsets` `_EmissionColor` 220 ms 点亮、Shuriken 粒子从盒体轮廓外扩（寿命 0.8–1.4 s、初速 120–260 px/s 折算世界单位、重力 −40 px/s²、alpha 线性衰减）、洞穴 dim 0.75→0 800 ms、盒后径向光晕 0→0.35（半径 = 盒宽 × 1.6）。标签 T0+3900 淡入 300 ms；Unity 同帧发布 `complete`，native 结果面板延 300 ms（T0+4200）自底 `.move(edge: .bottom)` 420 ms EASE_OUT 滑入；之后盒体 yaw ±3°/4 s 待机（`Tick` 完成后继续驱动）。
- 代码：`GachaShippingRevealChoreography.cs`（`GachaCubicBezier` 二分求解 CSS 曲线、timeline、`GachaRevealRarityStyle`、`GachaRevealStageFX` dimmer/flash/halo/particles）、`GachaShippingRevealDirector.cs`（`PrepareShippingChoreography`/`ApplyShippingChoreography`/`MeasureShippingOffsets`/`ShrinkStartUntilInsidePack`/`EmitRevealBurst`/`PrepareBladeEmissive`/`AdoptStageFX`）、`PremiumDisplayCaseDirectedPose`（新增 `RimColor/RimGlow`）与 `PremiumDisplayCaseShippingPresentation.ApplyRimGlow`、`FidgetAppCoordinator`（`EnterGachaStageFromNativeUi`/`LeaveGachaStageFromNativeUi`/`EmitGachaTearSnapFromNativeUi`、`AcquireGachaCamera` 幂等、`RestoreGachaCamera`、`HandleGachaShippingFrontRevealed` 按 rarity 发语义 Haptic）；Swift：`FidgetGachaPackPresentation.swift` 新常量、`FidgetProductUIComponents.swift`（`ProductPackSealSweep`、`ProductPackTearFrontEdge`、袋口 gape、下退 tilt/fade、`sealHitRect`）、`FidgetGachaShippingStorefront.swift`（`PackTearStage` TimelineView 待机、封条手势、`visibleStatusTitle`、`enterGachaStage/leaveGachaStage/emitTearSnap`）。
- 验证：Unity EditMode `GachaShippingRevealChoreographyTests`（曲线、拍点、yaw、60% 下退、rarity 光效、接线字符串）+ `GachaNativeHybridCandidateTests` + `PremiumDisplayCaseGate12Tests` + `GachaStorefrontIntegrationTests` + `GachaRevealTests`：45 passed / 2 skipped；Swift harness `GachaGate12RulesHarness` 121/121；`GachaShippingNativePreview` BUILD SUCCEEDED；Gate 12 Simulator export `Builds/iOS/Logs/gate12-export4.log` Success，`xcodebuild` Release Success；完整录屏 `Artifacts/PackTearNativeCandidate/r037-gacha-reveal-v2/r037-gacha-reveal-v2-clear.mp4`（实速 + 0.5×）、`r037-gacha-reveal-v2-sheet.png`、原始 `r037-gacha-reveal-v2-raw.mp4`，同步至 pipeline `evidence/12-shipping/rev-005/`（history event `bf33dd8b-77d4-44e3-8f7d-e0ede3fec250`；驳回 rev-004 event `a936294b-73d5-4d8a-bf1b-c204de832cf3`）。
- 偏差 / 待办：① 洞穴 saturation 0.6→1.0 未做（仅 brightness，dimmer quad 无法去饱和；需 URP Volume ColorAdjustments）。② 叶片点亮为 `ThreeBladeInsets` 单网格一次 220 ms，非三叶 0/90/180 ms 交错。③ §8 卡面资产（完整陀螺渲染 + rarity emissive 边光、卡背 roughness 0.35）未开始；prize prefab 本身含 RotorCore/HubVisual/TopCap，"缺盖体" 是暗材质在盒内读不出，属材质/灯光工作。④ 撕纸音效：产品尚无 gacha 音频通道。⑤ 命名：gacha 流程内名称均来自 receipt（`三叶金属陀螺`），「三叶尖金属」是 Library 当前模型标题，抽卡期间顶栏已隐藏，需用户在录屏中确认无残留。⑥ Simulator 中 Unity 首帧仍偶有短暂掉帧，真机待验。

## 2026-09-05 Pack tear R036 release-beat：对齐 Sweeps 的 commit 拍点（闪白 + 放射线），并列对比（已被 R037 v2 取代：commit 闪白/放射线移至揭晓帧）

> **当前状态：用户指出与 Sweeps 现有实现仍有差距。逐帧对比 `Artifacts/SweepsReference/videos/section-2.mp4` 后，native 侧可补的已补：commit 时全屏闪白（峰值 0.82、约 0.45 s 内衰减）+ 44 条从袋口向外射出的放射线（0.60 s），封条飞出更高更快（抬升 176 pt、旋转 22°）。其余差距在 Unity／产品层，需要决策（见下）。视觉批准待确认，未推送手机。**

- Sweeps 拍点（60 fps 逐帧）：剪断 1.43 s → 同帧全屏闪白 + 放射线，封条 0.2 s 飞出；Pack 在剪断同一拍立即下落（约 0.35 s），卡牌随 Pack 下落露出，再下沉到屏幕中央并放大回弹；背景保持暖色 wash，随后转为稀有度色并淡入名称／SAVE。剪断→稳定约 1.2 s，无空拍。
- R036 native 侧改动：`ProductPackReleaseBurst`（全舞台闪白 + `ProductPackBurstStreaks` 确定性放射线，绕 `ProductPackTearLayout.seamCenter` 发射，不随下退移动）取代原 7 条小射线；`releasePulseDurationSeconds 0.26→0.60`、rise `0.04`、peak `0.06`、`releaseFlashOpacity = 0.82·s^2.4`；`sealExitLiftPoints 132→176`、`exitRotationDegrees 14→22`、`exitDriftPoints -10→-16`。`nativeHybridContainmentHoldNanoseconds` 试过 40 ms：Simulator 下收藏盒首帧仍阻塞主线程，Pack 下退变成硬切，已回到 120 ms。
- 仍存在的差距（不是 native 层能单独解决的）：① Pack 下落与剪断同拍——我们的 draw／receipt／isolation／case setup 只能在 commit 之后发生，R030 门禁要求收藏盒 ready 才允许 Pack 下退，因此下退比 Sweeps 晚约 0.3 s（Simulator 约 0.5 s）；要同拍需在 commit 前预实例化收藏盒并在 receipt 到达后再挂 prize（Unity 架构 + 门禁变更）。② 舞台颜色——R030 isolation 把相机清屏为纯黑，Sweeps 全程暖色 wash；改相机清屏色为 Pack 色相是 C# 改动，且属设计圣经层决策。③ 收藏盒出场——Unity 起始 Y 偏移夹在 `[-0.20, -0.04] m`、缩放 `0.94→1`，几乎看不到升起；Sweeps 卡牌大幅位移 + 放大 + 回弹，需要改 `GachaNativeHybridCandidateMotion` 常量并重新 export Simulator 工程。④ Pack 底座——Sweeps 的 Pack 留在屏幕底部作底座，我们的滑出屏幕（`departureDistance ≥ 72% 屏高`）。⑤ 结果信息／CTA 淡入属 reveal 完成态，不在撕包范围。
- 并行任务冲突：R030 export 的 `FidgetGachaShippingStorefront.swift`／`FidgetGachaNativeHybridR030Candidate.swift` 副本在 14:54／15:00 被另一任务写入了 `ProductPackReleaseFlash`／`nativeHybridStageDim*` 实现（源码在 15:03 已不含这些改动），导致 export 编译失败；本任务已用源码覆盖 export 副本（旧副本备份在 `/tmp/pack-tear-redo/foreign-export-copies/`）。同一 feature 请只保留一个执行任务。
- 验证：rules harness `117/117`（hold／drawAfterLidClear／flash 衰减断言已更新）；GachaShippingNativePreview 与 R030 export Xcode `BUILD SUCCEEDED`；EditMode 三个测试类 `30 passed / 2 ignored / 0 failed`；R030 trace F1–F4 齐全。
- 预览：`Artifacts/PackTearNativeCandidate/r036-sweeps-release-beat/r036-vs-sweeps-side-by-side.mp4`（左 Sweeps、右 R036，以剪断／commit 对齐，实速 + 0.4×）、`r036-release-beat-hybrid-clear.mp4`、`r036-vs-sweeps-sheet.png`、`r036-release-beat-hybrid-sheet.png`、原始录屏 `r036-hybrid-raw.mp4`。

## 2026-09-05 Pack tear R035 seal-fin：静态 Pack 补全、封条即顶盖、去描边、动作连贯

> **当前状态：用户对 R034 提出三点：静态 Pack 素材不完整、动作不连贯、封口出现不明物体。R035 已修：Pack 恢复为 body + flap（封条）合成；顶盖改为 authored 封条本体，沿袋身顶边（row 92）撕下，袋身永不裁切；删除亮色撕边描边与腔体描边；修掉三处让动画掉帧的主线程阻塞。R030 Simulator hybrid 全程重录。视觉批准待确认，未推送手机。**

- 根因①「素材不完整」：`gacha-pack-*-flap.png` 是 Pack 顶部封条（rows 45–101，锯齿顶边），`-body.png` 从 row 92 起、顶边平切；二者叠加才是完整 Pack。R034 停止绘制 flap，静态 Pack 因此顶部被削平。现 `ProductPackSealedArtwork` 统一渲染 body + flap，撕包层、carousel `PackArtwork`、预览工具同源。
- 根因②「不明物体」：R034 在袋口画了一个带亮色渐变描边（`Color.white 0.82`）的深色腔体 slab，isolation 黑底上读成一块悬浮的板。现 `ProductPackMouthLip`／`ProductPackTornEdge` 已删除；腔体为不透明深色 sliver（R033 `opaqueLocalCavity` 合同），紧贴袋身顶边、两端 `openingEndTaperFraction=0.07` 收进袋肩、无描边，黑底上自然消失。
- 根因③「动作不连贯」（Simulator 实测帧间隔）：a) `GachaNativeHybridR030Diagnostics.capture` 在每个 layer-update／F1／F2 做 3× 全屏 `layer.render` + PNG 编码 + 落盘，主线程卡 100–300 ms，撕开首 0.25 s 与顶盖飞出全程只剩 ~10 fps；现仅 checkpoint 运行保留像素捕获，全程模式只写 trace。b) commit 同帧发起 draw → receipt → isolation → case setup，Simulator 主线程阻塞 ~0.28 s，顶盖飞出被冻结再跳变；现 `GachaPackHandoffRules.drawAfterLidClearNanoseconds`（= flapExit 0.30 s）之后才 `model.draw`，storefront 与 R030 同步（Reduce Motion／checkpoint 模式仍立即 draw）。c) 顶盖飞出改为 `.linear` 驱动（pose 内部已 smoothstep，叠加 easeOut 读成跳切）；Pack 下退改 `.easeIn`。
- 几何：`authoredSeamYFraction 120/512→92/512`（= body 顶边 = 封条／袋身分界）；新增 `authoredPackTopYFraction=45/512`（封条顶）、`authoredFlapSpanFraction=24/384…360/384`；`peelHingeDegrees 4.5→3.5`（封条 47 行高，顶边错位 <2 pt）；`compactTopAreaBottomFraction 0.26→0.21`。lid 由 flap raster 按 `ProductPackTornAwayTopShape`（inset→撕裂前沿列，顶到 seam+1.6 pt 纹理）裁出，铰链在前沿；未撕部分由 `ProductPackSlitBodyMask` 显式补集遮罩保留——原 even-odd 减法在此处让整段未撕封条消失，已改为 `FillStyle(eoFill: false)` 的三块多边形。
- Simulator 实测帧节律（`hybrid11`，60 fps 采样）：撕开 4.53–4.87 s 连续；顶盖飞出 4.93–5.13 s 连续；isolation 切黑 5.47 s（静止画面上，不可见卡顿）；Pack 下退 + 收藏盒升起 5.65–6.28 s 连续。
- 验证：Swift rules harness `117/117 PASS`（新增封条几何、end taper、lid 上下边 4 项）；GachaShippingNativePreview Xcode `BUILD SUCCEEDED`；R030 export 增量 Xcode `BUILD SUCCEEDED`；EditMode `GachaNativeHybridCandidateTests`+`PremiumDisplayCaseGate12Tests`+`GachaStorefrontIntegrationTests`=`30 passed / 2 ignored / 0 failed`（含 GPU 光效测试，有图形运行）；R030 trace F1–F4 齐全。字符串测试已同步：lid 资产改为 `flapAssetName`、`ProductPackSealedArtwork`、无 `ProductPackMouthLip`／`ProductPackTornEdge`、seam `92.0 / 512.0`。
- 预览：`Artifacts/PackTearNativeCandidate/r035-seal-fin-hybrid/r035-seal-fin-hybrid-clear.mp4`（1206×2622、60 fps、16.9 s：实速 → 0.4× → 封口特写 0.33×）、`r035-seal-fin-hybrid-sheet.png`、原始录屏 `r035-hybrid-raw.mp4`。R034 预览目录保留为历史。
- 已知限制：`verify_hybrid_r029.py` 的静态 F0–F4 overlay 校验未在本轮重跑（几何已变，需重采 checkpoint 捕获）；Simulator 下 Unity 主线程仍比真机慢，真机节律待验证；Unity 收藏盒起始 Y 偏移夹在 `[-0.20, -0.04] m`，升起位移短。

## 2026-09-05 Pack tear R034 whole-lid：Sweeps 节奏、整块顶盖、hybrid 全程预览（已被 R035 取代）

> **当前状态：用户拒绝 R033 分段封条（"碎纸片"）。R034 改为单块刚性顶盖：撕开时沿撕裂前沿铰链抬起 `4.5°`，commit 后整块以 `14°` 旋转、`132 pt` 抬升、`0.30 s` 飞出并在越过袋口后淡出；无剪刀元素。R030 Simulator hybrid 全程（native 撕包 → 顶盖飞出 → 隔离 → 真实 Unity 收藏盒从袋口升起、Pack 下退）已录屏。视觉批准待确认，未推送手机。**

- 节奏（源自 `section-2.mp4` 分析，无剪刀）：lead-in `80 ms` → 撕开 `0.36 s`（左→右）→ commit：顶盖 `0.30 s` 飞出 + 爆点 `0.26 s`（7 条上半球射线，避开标题文字）→ receipt／Unity 两帧稳定 → 停顿 `120 ms` → Pack `0.24 s` 下退，同时收藏盒 `0.64 s` 升起（`0.94→1.0` 缩放）。
- 几何：`authoredPackFaceTopYFraction`／`authoredSeamYFraction` 按 `gacha-pack-standard-body.png` 像素重新定位到 crimp／面板边界；`openingInsetFraction 0.09→0.05` 去掉两侧 crimp 耳；`maximumOpeningHeightPoints 34→10` 保持窄缝；顶盖由 body raster 遮罩切出，飞出的像素与被移除的像素一致。
- 本轮修复的两处运行时缺陷：① `GachaNativeHybridR030CandidateView` 全程模式此前把 `tearProgress` 停在 commit=`0.62`，顶盖永不飞出、无爆点；现 `playLidRelease()` 复用 shipping commit 拍点（capture checkpoint F0–F4 仍停在 commit，不改既有 overlay 证据）。② R030 与 `GachaStoreView` 的 `packRetreatProgress` 在 `withAnimation` 中作为 model 值立即变 1，`if` 分支同帧卸载 Pack，下退动画从未渲染；现以 `packDeparted` 在时长结束后才卸载。`ProductLiveUnityPackRevealLayer` 新增默认 `0` 的 `releasePulseStrength`。
- 验证：Swift rules harness `113/113 PASS`；R030 Simulator export 增量 Xcode `BUILD SUCCEEDED`；EditMode `GachaNativeHybridCandidateTests`+`PremiumDisplayCaseGate12Tests`=`28 passed / 2 ignored(R031、R032 superseded) / 0 failed`（GPU 光效测试在 `-nographics` 下不可运行，单独有图形运行为 `1/1`）。`PremiumDisplayCaseGate12Tests.NativePackTearUsesRealLayersMaskAndReadyGatedCoverage` 的过期字符串（`0.48/0.68` 排练、`OuterFoilMask`、`MouthCavity`、flap offset helpers）已改为当前 R033/R034 实现。R030 trace：F1–F4 齐全、`callbackResult=accepted`、F4 `packForeground=false`、`nativeHybridProgress=1`。
- 预览证据（真实 shipping Swift 源 + R030 Simulator export，iPhone 17 Pro Simulator `5BF378DF-…`）：`Artifacts/PackTearNativeCandidate/r034-whole-lid-hybrid/r034-whole-lid-hybrid-preview.mp4`（`3.2 s` 实速）、`…-preview-slow.mp4`（`0.4×`）、`…-closeup-slow.mp4`（袋口特写 `0.33×`）、`r034-whole-lid-hybrid-sheet.png`、原始录屏 `r034-hybrid-raw.mp4`／`r034-native-raw.mp4`。
- 已知限制：Unity 收藏盒起始 Y 偏移被夹在 `[-0.20, -0.04] m`，升起位移本身很短，可见的"升起"主要由 Pack 下退揭开；R030 export 内 `FidgetGachaShippingStorefront.swift` 此前为旧版，本轮已同步补丁，但 `GachaStoreView` 的 candidate 分支在 handoff 阶段仍绘制 `Color.black`，非 R030 路径下 Unity 收藏盒不可见（既有状态，未在本轮改动）。

## 2026-09-04 Build 44 provisioning refresh installed, launch blocked on device trust

> **当前状态：Build 44（0.1.0/44）已用新的 7 天 Team profile 重签并覆盖安装到 iPhone 15 Pro Max。启动被系统拒绝：开发者证书尚未被用户明确信任。未改 Unity 源码、未升 Build 号、未 App Store submission。**

- 根因：旧 profile `47873acc-04e8-4f0a-bbd1-7996c45c9109` 于 `2026-09-03T06:47:45Z` 过期。Mac 上 codesign 仍通过，但设备拒绝启动。
- 新 profile UUID=`199b8813-919d-49c3-b7ed-9e82c88d4c49`，创建 `2026-09-04T03:39:25Z`，到期 `2026-09-11T03:39:25Z`。`codesign --verify --deep --strict` 通过；Xcode `BUILD SUCCEEDED`。
- 设备库存回读=`com.jiaweizhou.fidgetspinner.codex 0.1.0 (44)`。`devicectl` launch 报 `FBSOpenApplicationErrorDomain` Security：profile 未被用户明确信任。
- 证据：`evidence/12-shipping/runtime-recovery-build42/device-delivery/magnetic-slide-build44-resign-20260904/`。Device Acceptance 仍待用户信任后打开 App。

## 2026-09-03 Magnetic Fan Card front-axis no-ring hard rule

> **当前状态：旧 `CommonAxis_BearingCap_Chrome` 已从 Blender、两个 Fan Card FBX、shipping Unity scene 和重建入口移除。正面只保留下沉 `M_FanCardAxisMatte` 哑光轴芯。视觉批准待确认，未推送手机。**

- 根因：旧合同和测试强制保留低矮铬帽。峡谷顶光使帽体中心接近牌面颜色，边缘产生蓝白 Fresnel，因此读成银色圆环；旧测试只验证名字和尺寸，反而锁住缺陷。
- 权威合同现只允许 `CommonAxis_RecessedMatteSpindle`：半径 `2.00 mm`、下沉 `0.12 mm`、metallic／smoothness=`0`，specular highlights／environment reflections 均关闭。`BearingCap`、`Ring`、`Washer`、`AxisSeat`、`CoverDisc`、`ChromeBall`、`BallSeat` 在场景与 dormant FBX mesh 中均阻断。
- `fan_card_guardrails.json`、Blender builder、export、C# 规格、Unity scene builder、geometry validator、acceptance tests、AGENTS、Cursor hard rule、专项门禁和设计圣经已同步。未改变 `63.5 × 88.9 × 3.5 mm` 牌身、`1.0 mm` 层隙、共同轴心、Bottom/Middle/Top 运动归属、正背面隔离、角标父子关系、Collider、四档物理、音频或 Haptic。
- 2026-09-03 重建验证：source/full Fan Card guardrail=`ALL PASS`，完整轨道外轮廓净距=`7.590 mm`；`CardGeometryValidator`=`ALL PASS`，三张牌均 `open/nonmanifold=0, degenerate=0`；`FanCardAcceptanceTests=23/23`。
- 真实 shipping Unity scene 刷新 27 张 Canyon 视图，路径为 `Artifacts/EnvironmentIntegration/magnetic-fan-card-canyon-multiangle-r011-matte-axis/`，覆盖 top、hero、左右斜视、low、back、track closeup 和轴心特写。当前 Gate 12=`stale`、`11/12`；等待当前 shipping 视觉明确批准。未 build、install、launch 或操作物理 iPhone。
- Fan Card pipeline validator=`errors/missingFiles/unhashed 0/0/0`。Model Provenance Explorer 全量测试仍被并行 Magnetic Slide 与 Premium Display Case 的历史状态断言阻塞；本任务未修改或放宽这些测试。

## 2026-09-03 Magnetic Slide Tile Build 44 installed

> **当前状态：Build 44（0.1.0/44）已 export、签名、安装并启动到 iPhone 15 Pro Max。包含 Gate 11 rev 14 hybrid 材质、Variant B 灯光、旋转方向修复与完整 production interaction stack。真机验收待用户确认。**

- Job=`magnetic-slide-build44-20260903T003750Z-snapshot`；buildKey=`7c4bc41cef913c799797b32d0a195e6da07d84d750a5a095c360a67bf63310b4`；source digest 在 snapshot 与 export 后一致。
- Preflight：pipeline=`12/12`；EditMode=`43/43`；PlayMode=`5/5`；无 App Store submission。
- Device：wired tunnel、DDI 可用、Developer Mode=`enabled`、passcodeRequired=`false`；UDID=`00008130-001A00361EE0001C`。
- Unity export 成功；Xcode `BUILD SUCCEEDED`；install/launch 成功；进程 PID=`16125` 在 delivery 后仍存活。
- 设备 console 捕获 Unity/Metal/Input System 初始化，但未在 18s 窗口内捕获 `[MagneticSlideRuntime]` interaction/audio markers；`runtimeStartupMarkersCaptured=false`。
- 证据目录：`evidence/12-shipping/runtime-recovery-build42/device-delivery/magnetic-slide-build44-20260903T003750Z-snapshot/`。pipeline rev=`309`。

## 2026-09-03 Magnetic Slide Tile rev 14 approval and Build 44 block

> **历史：用户以原话“批准 rev 14，构建并安装 Build 44”批准 Gate 11 rev 14。此前因 CoreDevice provider 不可用而阻塞；该阻塞已在 wired 重连后解除。**

- Rev 14 shipping source 组合 rev 12 的 authored RGB、`28/85` mica/microflake、上下 albedo／roughness／normal／motif detail，与 rev 13 的 `0.28/0.14/0.00 mm` substrate／motif／crystal 三层结构。晶体 IOR=`1.52`、transmission=`0.985`、refraction=`0.35 px`。
- Shipping scene 上下各三张 cap-only renderer 已绑定 `M_G11R014_*` 六个材质；dark side 无图案、silver rim、外部 bounds、collider、固定轴、端点互锁、clockwise/counterclockwise 修复、Pinch/Orbit、audio/Haptic 与 Variant B 灯光保持。
- Approval 进入 pipeline rev=`305` 与 `history.ndjson`；DecisionState=`Gate 11 rev 14 approved`。DeliveryState=`Build 44 authorized but not started`；Device Acceptance=`pending-build44-install-and-user-validation`。
- 构建前检查：本机可用空间=`159 GiB`，无 Unity/Xcode writer。`devicectl` 返回 iPhone 15 Pro Max=`paired/unavailable`。依用户的设备阻塞规则，未启动 Unity preflight、PlayerSettings 归一化、source snapshot、export、Xcode、签名、安装或启动；无 App Store submission。
- 2026-09-03 解锁后重试仍被连接层阻塞：physical iPhone 15 Pro Max、UDID=`00008130-001A00361EE0001C`、pairing=`paired`、Developer Mode=`enabled`，但 tunnel=`unavailable`、DDI=`false`，`device info details` 报 `CoreDeviceError 1002: No provider was found`。最后连接时间为 `2026-09-02T08:37:00Z`；因设备不可达，`passcodeRequired=false` 无法查询。pipeline rev=`306`。Build 44 编号未消费，未创建 export。
- 2026-09-03 08:18 再次连接重试结果不变：CoreDevice provider 仍不存在，tunnel=`unavailable`、DDI=`false`，最后连接时间未更新；本机可用空间=`157 GiB`，无 Unity/Xcode writer。pipeline rev=`307`；Build 44 仍未消费，未获取构建锁、未运行 Unity preflight 或创建任何新 export。
- 2026-09-03 08:23 用户报告有线连接后，本机实时复核仍返回 `CoreDeviceError 1002: No provider was found`；lock-state 查询另报 `CoreDeviceError 1011`，无法匹配 `ecid_7318581840707612`。本机 `devicectl` 状态仍为 pairing=`paired`、Developer Mode=`enabled`、tunnel=`unavailable`、DDI=`false`。pipeline rev=`308`；Build 44 仍未消费，未获取锁、未运行 preflight/export/Xcode/sign/install/launch。

## 2026-09-02 Magnetic Slide Tile layered material correction

> **当前状态：Build 42 因红面材质被压平而判定视觉验收失败。Gate 11 rev 12 分层材质已生成真实 shipping 预览，等待视觉批准；Build 44 未构建、未安装。**

- 根因：Gate 10/11 的 `PortablePBRR011` 为 OPAQUE、transmission=`0`，把 base color、单一 roughness/normal 和弱 clearcoat 合并进同一 BRDF。它避免了白化，却丢失了 Blender 获批材质的基底、黑图案和清漆独立响应。
- 修复采用单 pass 自定义 URP shader，不增加透明 shell、renderer、draw call、overdraw 或 bounds。血红基底使用原贴图、`28/85` 两级 mica/microflake、roughness `0.022–0.11` 和强度 `0.12` 的角度色移；黑图案使用上下独立 mask、roughness `0.18`、metallic `0.24`、UV relief `0.0012`；清漆使用 IOR `1.52`、roughness `0.035`、strength `0.78`、depth cue `0.0016`。Emission=`0`。
- 真实 `MeshyEDC.unity` 同机位包含 Front、Hero、左右斜视、Grazing、Low、Phone 和 max-open。6 秒 `1280×720@30 fps` 录屏展示相机移动时的颗粒、角度色移和清漆反射。四方权威对照包含原始产品、Blender、当前平涂 Unity 和修正 Unity。
- 图像门禁：对象 P50 `0.135→0.217`；红区饱和度 `0.393→0.500`；红区局部变化 P90 `0.0133→0.0322`；黑区中位亮度 `0.110`；clipping=`0%`。
- 七个 interaction/mechanism/settings/prefab/audio/Haptic 文件、mesh identity、renderer count、material slot count 和 bounds 均未改变。dark side、silver rim、underside 与 top-only artwork 分区保持。
- 验证：Metal shader target `3.5` 编译无 error/warning；SRP Batcher 使用单一 `UnityPerMaterial` CBUFFER。Focused EditMode=`3/3`；真实 shipping Input System PlayMode=`5/5`。
- 证据位于 `evidence/11-unity-parity/rev-012-layered-material/`。视觉批准待确认，未推送手机。Build 42 保持 rejected；Build 44 的 export、签名、安装、启动和 App Store submission 均未执行。

## 2026-09-01 Magnetic Slide Tile Build 42 rotation-direction rejection

> **当前状态：Build 42 真机验收因“现在旋转方向是反的”失败。方向修复已通过 Unity 测试；Build 43 仍永久不可复用。Build 44 未构建，等待 iPhone 重新连接。**

- 根因：`EdcSliderController` 把屏幕 `atan2` 的正角直接用于模型 local `+Z`。shipping 相机从轴线另一侧观察，因此手指与 `TopPlate` 的视觉方向相反。
- 修复：触点先由 screen ray 投到固定轴交互平面，再围绕 `RotatingCarrier` 的有向 world `+Z` 用 `Vector3.SignedAngle` 累计。该映射不依赖固定屏幕符号，并跨 `0/360°` 连续。
- 仲裁：端点手势以切向弧长和径向位移判定旋转或闭合直推。Slide 方向、空白区右拖 Orbit 正 yaw、Pinch、端点互锁、Variant B 灯光和音频／Haptic recipe 未改。
- 方向语义：每次 `DetentCrossed` 记录 signed direction 和 unwrapped detent index；同一同步事件把该元数据送到音频 renderer 与 Haptic router telemetry。
- 验证：focused EditMode=`37/37`；真实 Input System PlayMode=`4/4`。真实 touch arc 覆盖 authored camera 顺时针 `12°`、Orbit 后逆时针 `36°`、Pinch 后顺时针完整 `360°`、30 个 `12°` detent 顺序、音频／Haptic 方向和 index、闭合对齐、无自运动及 Pinch／Orbit 仲裁。
- Pipeline rev=`293`；证据位于 `evidence/12-shipping/runtime-recovery-rotation-direction/`。本机可用空间=`57 GiB`；iPhone=`paired/disconnected`。未执行 Build 44 export、Xcode、签名、安装、启动或 App Store submission。Device Acceptance=`pending-build44-install-and-user-validation`。

## 2026-09-01 Magnetic Slide Tile Build 42 lighting rejection and Gate 12 rev 4

> **当前状态：Build 42 交互为 partial device success，但暗灯光被拒绝。Gate 12 lighting rev 4 Variant B 已获 review UI 视觉批准并进入 shipping source。Build 43 Unity export 成功，但 Xcode 因本机磁盘只剩 `119 MiB` 失败；未签名、安装或启动。真机验收待执行。**

- Build 42 使用 `MainCamera HDR=false`，没有 URP Volume、曝光或 tone map。场景 key/fill=`0.54/0.42`，reflection=`0.56`；近黑环境与未校准的设备亮度/HDR 假设使暗侧和血红中间调在 iPhone 上不足。贴图、材质和 emission 不是根因。
- A 保留 Build 42：`0 EV`、HDR off、无 tone map、ambient `1.00×`、reflection/key/fill=`0.56/0.54/0.42`。
- B 已获 shipping 视觉批准：`+0.55 EV`、HDR on、Neutral tone map、ambient `1.25×`、reflection/key/fill=`0.70/0.68/0.54`、white balance `0/0`。模型 P50 提升 `27.8%`，黑色细节 P25 提升 `38.9%`，红色饱和保留 `94.7%`，测得 clipping=`0%`。
- C 为更亮 D65：`+2.35 EV`、HDR on、ACES、ambient `1.80×`、reflection/key/fill=`1.00/1.08/0.86`、white balance `0/0`。模型 P50 提升 `31.8%`，黑色细节 P25 提升 `3.7%`，测得 clipping=`0%`。
- 真实 `MeshyEDC.unity` 同机位生成 A/B/C 的 Library、Hero、Top、左右斜视、Low、Phone、max-open 和 endpoint-36°。比较板、phone 板、histogram 与 `26.6 s` Unity-only 视频位于 `evidence/12-shipping/rev-004-lighting/`。
- 七个 input/mechanism/settings/prefab/audio/Haptic source hash 与 Build 42 后状态一致。geometry、material、artwork、camera recipe、endpoint interlock、gesture、audio 和 Haptics 均未改。
- 验证：Unity focused EDC EditMode=`37/37`；真实 Input System PlayMode=`3/3`；magnetic-slide provenance=`168/168`；图像质量门禁通过。七个 protected runtime/model source 与 Build 42 snapshot SHA-256 逐文件一致。
- `MeshyEDC.unity` 已保存 `MagneticSlideShippingLightingController.variant=BalancedBrighter`、key/fill=`0.68/0.54`，approved magnetic-slide model 仍默认 active，fallback 仍 disabled。批准记录为 `variant-b-shipping-approval.json`；pipeline rev=`289`，`12/12 approved`。
- Build 43 job=`magnetic-slide-build43-20260901T075038Z-snapshot`，build key=`431edcc2…3365`，source digest=`7a3d4875…1e74`。ProjectSettings 与 source 分别稳定 `5 s/3 s`；Unity BuildReport=`Success`，export 后 protected hashes 完全一致。
- Xcode 在 `GenerateDSYMFile` 报 `LLVM ERROR: No space left on device`，随后 `build.db: database or disk is full`；当时本机仅余 `119 MiB`。未产生有效 `.app`，所以 sign/install/launch/runtime logs 均未发生。Build 43 job 永久 `reusable=false`；下一次必须为 Build 44 或更高的新目录。
- Build 43 preflight 时 `passcodeRequired=false`、tunnel=`connected`、transport=`localNetwork`；失败后设备状态变为 paired/disconnected。无 App Store submission。Device Acceptance=`pending-valid-build-install-and-user-validation`。

## 2026-09-01 Magnetic Slide Tile Build 41 rejection and Build 42 recovery

> **当前状态：Gate 12 rev 3 视觉批准不变；Build 41=`rejected-low-fi-noninteractive`。运行时修复当前复测 EditMode `33/33`、真实 PlayMode Input System touch `3/3`、build-number/compile `1/1`。Build 42 已完成稳定 source snapshot、Unity export、Xcode build/sign、安装与启动；真机日志已捕获 production input、Orbit、Slide 和语义音频播放。Device Acceptance 待用户验收。**

- Build 41 仅直推可用；端点旋转、Pinch、空白区拖动 Orbit／重定位和声音均失效。该 build 保留为已导出、签名、安装、启动但用户拒绝的历史，绝不复用。
- 根因一：旧 `ShippingInteractionSurface` 属于 `MovingTop`，没有随 `TopLocalSlide` 的直推 transform 移动；顶片到达端点后，屏幕可见顶片与命中体分离。
- 根因二：`EdcPortraitCameraFramer.target` 仍指向 inactive fallback `EDC_Root`。bounds 查询失败，因此 `SharedPresentationGestureController` 收到 Pinch／Orbit 后无法更新有效相机姿态。
- 根因三：候选没有 active `MagneticSlideDetentAudio`；旧音频仍在 inactive fallback。机制语义又绕过 `EdcSliderController` 直达 generic Router，导致 production `FidgetAppCoordinator.EmitMagneticSlider` 与音频订阅都收不到同一事件流。
- 根因四：Build 41 测试用 mouse state、`SendMessage("Update")` 和直接 controller API，未覆盖真实 PlayMode touch、双指 Pinch、手势竞争、AudioSource 或 App coordinator。
- 修复复用 shipping 组件：`EdcSliderController` 负责玩具触控；`SharedPresentationGestureController` 负责空白区 Orbit 与双指 Pinch；`EdcPortraitCameraFramer` 绑定 active candidate 与稳定闭合 bounds；`MagneticSlideDetentAudio` 使用 6 个 active 2D `AudioSource`；`FidgetAppCoordinator` 消费同一语义流并进入 `FidgetHapticRouter.EmitMagneticSlider`。没有 raw input→`IosHaptics`。
- 手势映射：单指命中顶片=`Slide`；只有 `sMax/0°` 才按切向拖动进入 `Rotate`；非零角保持 `sMax`；回到 `0°/360°` 后向内拖动闭合。单指从模型外开始=`Orbit/reposition`；双指=`Pinch`；Pinch 后必须全部抬起才允许新玩具手势。
- 机制使用 unwrapped angle，完整一圈严格产生 `30 × 12°`；4 个空间 slide step、endpoint unlock、旋转 detent 与 lock 共享机制事件。PlayMode 日志记录 touch receipt、zoom、angle、audio-ready 与 `PlayOneShot`。
- 场景证据：`MeshyEDC.unity` SHA-256=`b6452b14…6bebfd`；活动 collider 唯一且父级=`TopLocalSlide`；hidden/debug enabled colliders=`0`；active audio voices=`6`；相机 target=`MagneticSlideTileGate12R002Candidate`，并保留 Build 41 默认相机 pose。geometry／materials／默认构图未改。
- 验证：focused EditMode=`33/33`；dedicated PlayMode=`3/3`；Build 42 number/compile=`1/1`。覆盖 hit/layer/Input actions/no EventSystem blocker、直推、禁转、端点 360°、闭合互锁、Pinch、Orbit、仲裁、音频事件计数、Haptic telemetry、reload/reset/no-self-motion 与默认 scene registry。
- 首次 Build 42 delivery job=`magnetic-slide-build42-20260901T034218Z-380ac0e4`：paired=`true`、Developer Mode=`enabled`、tunnel=`connected`、DDI=`true`、transport=`wired`、`passcodeRequired=false`。Unity BuildReport=`Success`，并生成完整 Xcode project、`Info.plist` 与 `FidgetingBuildManifest.json`。根因不是并发 writer：export log 明确显示 coordinator 在 snapshot 后调用 `ConfigureIosBuild → PlayerSettings.SetGraphicsAPIs → SaveAssets`；`ProjectSettings.asset` mtime 随该 Unity PID 更新。
- snapshot 语义已改：外层同时持有 iOS pipeline 与 canonical Unity writer 锁；等待 canonical writer 连续三次为空；先集中分配并写入 Build 42、切换 iOS、保存／同步刷新，再计算 build key。snapshot 前后记录逐文件 hash；`ProjectSettings.asset` 必须稳定 5 秒，全 source digest 必须稳定 3 秒；export 路径只验证准备值，不再调用 coordinator setter。
- 第二次 job=`magnetic-slide-build42-20260901T035013Z-snapshot`：`ProjectSettings.asset` 准备前 hash=`c49f391e…`，snapshot hash=`fc6985e3…`；5 秒与 3 秒稳定窗口均通过。无其他 canonical Unity／Xcode writer。Unity BuildReport 与 Xcode markers 再次成功，但 export 后 hash=`1ba80562…`。逐文件比较只发现 `ProjectSettings.asset`；重现实验证明唯一字段是 `m_BuildTargetGraphicsAPIs[iOSSupport].m_Automatic: 0 → 1`。第二次 export log 没有 `ConfigureIosBuild` setter 调用，因此 writer 是 Unity BuildPipeline 的 graphics API 归一化，不是并发任务。
- 前两个 Xcode export 均永久标记 `reusable=false`。稳定方案沿用项目自 Build 21／40 的成功约定：`m_Automatic=1`，Unity 6 iOS default/automatic graphics APIs 只解析出 Metal；snapshot 验证 `GetUseDefaultGraphicsAPIs=true` 且唯一 API=`GraphicsDeviceType.Metal`，不放宽 post-snapshot source guard。
- 成功 job=`magnetic-slide-build42-20260901T035903Z-snapshot`，build key=`97e42cf2…a59b25d`，source digest=`471b633c…1b9aa`。`ProjectSettings.asset` snapshot hash=`1ba80562…`，5 秒稳定；全 protected source 3 秒稳定，export 后逐文件 hash 完全一致。Unity BuildReport=`Success`，Xcode project／plist／manifest 完整。
- Xcode Release=`BUILD SUCCEEDED`；Apple Development 签名与 provisioning profile 生效，`codesign --verify --deep --strict` 通过。设备 install receipt 成功，inventory 回读=`com.jiaweizhou.fidgetspinner.codex 0.1.0 (42)`。
- 首轮 console collector 结束时的 SIGINT 同时终止 attached app，因此旧 liveness check 得到 0 个进程；这不是 app crash。runner 已在 console capture 后显式 relaunch。最终 launch receipt 成功，5 秒后 PID=`7593` 仍在运行。
- 真机 console 捕获 `audio-ready`（6 voices、24 kHz、1024×4）、`shipping-coordinator-ready candidate=True fallback=False`、`input-ready`、touch receipt、空白区 Orbit、顶片 Slide，以及 `MagneticEdgeProbe`／`Breakaway`／`DetentCaptured` 的 audible `audio-play`。Device Acceptance 仍待用户确认完整 360°／30 档、闭合互锁、Pinch、Haptic 与静置零自运动。
- 最终 relaunch 后 5 秒进程回读确认 PID=`7593`；稍后的再次确认时设备仍在 paired inventory，但 tunnel 已变为 `unavailable`，因此不能继续声称当前在线。已完成的 install／launch／runtime log 证据不受影响；后续真机验收需重新连接设备。
- 未执行 commit／push、archive、App Store upload 或 submission。

## 2026-08-31 Magnetic Slide Tile Gate 12 rev 3 connected motion correction

> **当前状态：Gate 12 rev 2 的七个静态视图已获确认。rev 3 只修正 max-open／端点／录屏运动，现为 `ready_for_review`，未批准。视觉批准待确认，未推送手机。**

- 用户反馈截图已归档为 `evidence/12-shipping/rev-003/user-feedback-exploded-motion-r002.png`，SHA-256=`d36fb987…1015b`。rev 2 的 Library／Hero／Top／左右斜视／Low／Phone 原图逐字节复制，七组 SHA-256 全部一致。
- 根因是坐标转换后轴向错误：旧 runtime 用 local `+Z` 平移，实际映射为 world-up；又用 local `Y` 旋转，实际成为离面旋转。当前改为 `TopLocalSlide local -Y` 平面滑动，以及 `MovingTop`／`RotatingCarrier local +Z` 固定轴旋转。没有 explode／lift 参数。
- 240 帧实测最大顶片高度残差=`2.7939677e-9 m`，离面 slide residual=`0 m`，固定轴 matrix residual=`0`；renderer 每帧保持连接。max-open 为 `sMax/0°`，12°／36°／360° 与全部 30 档均保持 `s=sMax`。
- 非法中段旋转、非零角回推、对齐后闭合、零初始／reset 速度、无 pitch／roll／flip 和 Haptic 共享 settings 均保持。Unity focused EditMode／UnityTest=`6/6`；motion image／transform／video validator=`pass`。Gate 12 deep link 在 `390×844 @3x` mobile viewport 恢复正确，asset modal 打开且横向 overflow=`0`。
- 新评审板为 `gate12-shipping-board-r003.png` 与 `gate12-motion-board-r003.png`；Unity-only 录屏为 `magnetic-slide-gate12-r003-unity-playmode.mp4`，H.264 `640×360 / 30 fps / 240 frames / 8.0 s`。
- DecisionState：rev 2 static views=`Approved`，rev 2 motion=`Revision Requested`，rev 3 motion=`Ready for Review / Approval Pending`。DeliveryState：`Real Shipping Scene Candidate Preview Only`。旧 `EDC_Root` 默认 active；候选默认 inactive。没有 build、archive、install、launch 或 phone push；Device Haptic Acceptance pending。

## 2026-08-31 Magnetic Slide Tile Gate 12 rev 2 shipping review

> **当前状态：用户以原话“可以的，继续”批准 Gate 11 rev 11。Gate 12 rev 2=`ready_for_review`，未批准。视觉批准待确认，未推送手机。**

- `Assets/_EDC/Scenes/MeshyEDC.unity` 已接入新建 `MagneticSlideTileGate12R002` 候选。保存场景 SHA-256=`b73676a2…17c`；旧 `EDC_Root` 默认 active，候选默认 inactive。
- 候选直接继承 Gate 11 rev 11 的 `99,280` triangles、固定底片／单轴／旋转载体／四槽、top-only artwork、dark side、silver rim、blood-red crystal、`RGBAHalf` HDR 和 corrected URP decode。没有复用已拒绝 Gate 12 rev 1 几何或材质。
- 唯一 `MagneticSlideTileMechanismSettingsR002.asset` 同时提供 `sMax=18.076433 mm`、endpoint tolerance=`0.001 mm`、`30` detents 和 `12°`。输入经 mechanism state 产生 `FidgetSemanticEvent`，再由 `FidgetHapticRouter` 交给 iOS renderer；新增代码没有直接调用 `IosHaptics`。
- 端点状态机覆盖闭合／重置零线速度和零角速度、中段禁止旋转、sMax 解锁、breakaway、最近档 capture、非零角禁止回推、对齐后闭合。固定底片和轴 matrix 不变，整机 pitch／roll／flip=`0`。
- 真实 shipping scene 生成 Library、Hero、Top、左右斜视、Low、Phone、max-open、`12°`、`36°` 和 endpoint `360°`。Unity-only PlayMode 为 H.264 `640×360 / 30 fps / 240 frames / 8.0 s`，覆盖完整 `30×12°` 与非法输入。
- 验证：focused Unity EditMode／UnityTest=`5/5`；shipping image／color／geometry／video checks=`pass`；pipeline rev=`258`。iOS Haptic 仅完成架构与自动化验证，真机触感验收 pending。
- DecisionState：Gate 11 rev 11 `Approved`；Gate 12 rev 2 `Ready for Review / Approval Pending`。DeliveryState：`Real Shipping Scene Candidate Preview Only`。没有 app build、archive、install、launch 或 phone push。

## 2026-08-31 Magnetic Slide Tile Gate 11 rev 11 Unity parity

> **当前状态：用户以原话“可以的，继续”批准 Gate 11 rev 11。该批准已进入 Gate 12 rev 2；未推送手机。**

- 新隔离候选位于 `Assets/_EDC/Candidates/MagneticSlideTileGate11R011/`。源 GLB／FBX SHA-256=`e9f90e9e…c2ca / 816ac0a2…1222`；旧 shipping scene SHA-256 前后均为 `99083a32…850d`。
- Unity 6000.5.6f1 URP 导入为 `8` meshes、`100,896` vertices、`99,280` triangles；bounds=`31×12×50 mm`。唯一固定轴、四槽、平底、无 cavity／proxy、端点互锁与闭合零速度均通过。
- 材质保持 top-only artwork，side／underside artwork triangles=`0/0`，上下 mask 独立。六张已定向 EXR 打包后由 Unity 导入为 `512² RGBAHalf` specular cubemap；强度=`0.85`，零 light、零 reflection probe、零重复反射。修正了旧路径的重复坐标翻转、box mip 和 metallic IBL 能量不足；新 strip 首次导入时的 `RGB24` 截断被验证器拦截并改为 `RGBAHalf`。
- `1000×620` 同相机原始整帧：Blender／GLB silhouette IoU=`1.0`；GLB／Unity IoU=`0.999924`；full-frame SSIM=`0.944199 > 0.90`；object SSIM=`0.926276 > 0.80`；silver median DeltaE76=`7.21 < 12`；hotspot area error=`2.42%`、centroid error=`9.44 px`。隔离 silver SSIM=`0.98049`／median DeltaE76=`5.10`；隔离 blood-red SSIM=`0.80790`／median DeltaE76=`5.66`。人工整板检查通过。
- Unity-only PlayMode 录屏为 H.264 High／yuv420p、`1920×1080`、`30 fps`、`18.0 s`、`540` frames。它覆盖闭合、中段旋转锁定、sMax 解锁、`30×12°` 全周、非零角回推锁定、对齐与闭合；整机 pitch／roll／flip=`0`。
- Focused Unity EditMode／UnityTest=`5/5 passed`，覆盖 HDR `RGBAHalf`、linear import、shader、零 emission 与端点互锁。Gate 11 已获批准。
- 该轮没有 Simulator、shipping promotion、build、install、launch 或 phone。后续 Gate 12 rev 2 仍保持旧 shipping 模型默认；Device Accepted pending。

## 2026-08-31 Magnetic Slide Tile Gate 10 rev 11 GLB 白化修正

> **当前状态：Gate 10 rev 10 已拒绝并不可变保留。用户以原话“继续”批准 Gate 10 rev 11；该包已被 Gate 11 rev 11 消费。未推送手机。**

- 拒绝图归档 SHA-256=`4f13f111…ac6`。根因同时来自 GLB transport 与预览：rev 10 顶面 `specularColorFactor=1.16`、transmission=`0.08`；重导板用约 `0.10 m` 近场 `75 W + 42 W`；查看器可继承 exposure=`2.0` 且未载入批准 HDR。原深红 baseColor、roughness G、geometry、UV、分区和 emission=`0` 均不是根因。
- Rev 11 GLB SHA-256=`e9f90e9e…c2ca`。顶面显式使用 `620×1000` sRGB baseColor、linear roughness G、linear tangent normal scale=`0.35`、metallic=`0.08`、specular=`0.55`、clearcoat=`0.32/0.10`、transmission=`0`。side=`[0.014,0.016,0.020] / 0.20 / 0.30`；rim=`[0.68,0.66,0.62] / 1.0 / 0.16`。全部 OPAQUE、emission=`0`。
- 几何 accessor bytes、primitive material IDs、node transforms、geometry digest=`2fcf6d2b…1952`、UV digest=`c1c00c09…d9df` 与 rev 10 一致。上下 cap 贴图保持独立；side／underside artwork=`0`；唯一 FixedAxis、四槽、非渲染 MinimumOverlapDisk、闭合零速度和端点互锁不变。
- 受控 Blender／GLB 同机位 MAE=`0.0043`。拒绝图白区=`15.83%`，GLB 重导=`0.25%`，真实 Three.js GLB=`0.09%`；查看器红色占比=`39.72%`，银色受控高亮=`2.36%`。Three.js 固定 neutral HDR、sRGB output、ACES、exposure=`0.9`，并隔离旧 exposure。
- 真实 GLB 已完成 load／orbit／zoom；桌面、`390×844` 移动、图片 modal、24 帧 H.264 录屏、runtime/loading=`0/0` 均通过。导出与查看器独立 audit 均通过。Focused Node=`149/149`；全量 Node=`225/226`，唯一失败是并行 Premium Display Case 仍断言旧 Gate 12 approved；pipeline、Python／JavaScript syntax、H.264 全解码与 focused diff=`pass`。
- Unity import／ASTC 计划更新为 `package/unity-import-contract-r011.json`，但未应用。没有 Simulator、Unity scene、Build、安装或 phone 操作。

## 2026-08-30 Magnetic Slide Tile Gate 09 rev 9 当前环境

> **批准状态：Gate 09 rev 9 已由用户以原话“继续”批准，并被 Gate 10 rev 10 消费。旧 shipping 模型仍为默认，未推送手机。**

- 本轮只消费 Gate 08 rev 6 Blend SHA-256=`897484bd…80fe`、Gate 07 rev 13 material SHA-256=`8538b414…b10c`、geometry digest=`2fcf6d2b…1952` 与机制合同 SHA-256=`9cd7a08f…ea571`。
- 中性／目标闭合、最大打开 0° 与侧面反射三组对比保持 camera、pose、material、light、Raw display、`neutral-display-v1`、exposure 和背景相同；只更换环境纹理。源材质槽、逐面 index、UV、geometry 与 zone attribute 前后逐元素一致。
- 目标 `2048×1024` OpenEXR 为 scene-linear Rec.709／D65，SHA-256=`2fe029be…3d13`，RGB nonzero=`100%`、seam=`0`、P01–P99 dynamic range=`5.766 stops`。六张 `512×512` Unity cubemap EXR 全部 RGB nonzero；Blender `(X,Y,Z)`→Unity `(X,Z,-Y)` 最亮方向误差=`0.063°`。
- Blend／GLB 重导继续保持两片 side artwork triangles=`0`、underside artwork triangles=`0`、每片 cap artwork=`511 triangles`，亮银 rim 存在，sampler=`CLAMP_TO_EDGE`，emission=`0`。
- 已生成 closed、max-open 0°／12°／36°／360°、侧面／银边近照、环境对比板、运动板、反射板、可移植板和真实 Blender 双环境端点转台。转台每个环境 `60` 个源帧，H.264 High、`1600×600`、30 fps、150 encoded frames、5.0 s，SHA-256=`3a8e8aec…6369`。
- Unity portability contract SHA-256=`d172c64c…fd13` 锁定当前 geometry、四个材质分区、neutral／target HDR、cubemap 朝向、display mapping、端点互锁、导入规则与容差。Gate 10 才允许生成正式导出纹理和导入包。
- 验证：Blender environment/HDR/cubemap/GLB、图像／色彩／反射／clipping、端点运动、portability contract=`pass`；focused Node=`15/15`；全量 Node=`219/220`，唯一失败为并行 Premium Display Case 当前 Gate 04=`draft` 的既有断言；browser desktop/mobile/GLB orbit+zoom/video/image modal/reload/direct deep link=`pass`，runtime/loading failures=`0/0`；Python／JavaScript syntax、JUnit XML、H.264 全解码与单模型／全模型 pipeline validator=`pass`。
- 本轮没有 Simulator、Gate 10、Unity import、最终 Unity、shipping scene、build、install 或 phone 操作。

## 2026-08-30 Magnetic Slide Tile Gate 08 rev 6 分区安全灯光

> **批准状态：Gate 08 rev 6 已由用户以原话“你开始吧”批准，并被 Gate 09 rev 9 消费。旧 shipping 模型仍为默认，未推送手机。**

- 当前轮只消费 Gate 07 rev 13 Blend SHA-256=`8538b414…b10c`、geometry digest=`2fcf6d2b…1952` 与机制合同 SHA-256=`9cd7a08f…ea571`。
- 复用 portable rev 4 shared-HDR 与 `neutral-display-v1` 配方，但从已纠正的 cap／side／rim／underside 分区重新生成全部灯光证据。
- Clay／Normal／Depth／Roughness 诊断必须在复制 scene、object 与 mesh data 上运行。源材质槽、逐面 `material_index`、UV、几何与分区 hash 前后必须逐元素一致。
- `blender-lighting-report.json` 证明四个诊断 pass 均使用复制 scene／object／mesh data；源材质槽、polygon indices、UV、zone attribute 与 geometry 的 before／after digest 全部一致。
- `lighting-material-audit.json` 证明 Blend 与 GLB 侧壁／底面 artwork 都为 `0`，两片 cap artwork 与亮银 rim 均存在；GLB sampler 为 `CLAMP_TO_EDGE`；shared HDR SHA-256=`a5b310c8…a872`。
- 已生成 Hero／左右斜视／低角、Beauty／Clay／Normal／Depth／Roughness、top／side／rim closeup、交互 GLB 与 90 源帧合法端点转台。MP4 为 H.264 High、`960×720`、30 fps、180 encoded frames、6.0 s，SHA-256=`4092e07a…0f25`。
- 验证：focused Node=`7/7`；全量 Node=`211/212`，唯一失败来自并行 Premium Display Case Gate 12 当前为 draft 的既有断言，与本 feature 无关；单模型与全模型 pipeline validator 均为 errors/missing/unhashed=`0/0/0`；browser desktop/mobile/GLB orbit+zoom/video/image modal/reload/direct deep link=`pass`，runtime/loading failures=`0/0`；Python／JavaScript syntax、JUnit XML、H.264 全解码=`pass`。
- 本轮禁止 Simulator、Unity、shipping scene、build、install 与手机操作。

## 2026-08-30 Magnetic Slide Tile Gate 07 rev 13 侧壁图案归零

> **批准状态：Gate 07 rev 13 已由用户以原话“通过”批准。pipeline rev=`238` 后进入 Gate 08 rev 6；旧 shipping 模型仍为默认，未推送手机。**

- 用户拒绝证据按原字节归档为 `evidence/07-material/rev-013/user-rejection-side-artwork-wrap.png`，SHA-256=`a7859940ee1d956755c07a810bc5aeccee75136da092cb8f1891bf9fe6dc8b1b`，原话“边缘没有图案填充”。
- 根因不是 Gate 07 原始 UV 或 GLB exporter。Gate 07 rev 12 Blend 的两片仍各有四个有效分区；Gate 08 rev 5 `render_roughness()` 在 `build_gate08_endpoint_lighting.py:304/310` 清空材质槽。Blender 将全部 polygon `material_index` 重置为 `0`；代码只挂回四个材质，没有恢复逐面索引，然后保存 Blend。slot 0 正是上下 artwork，故 `BottomExterior 8,723` 面与 `MovingTopBody 10,783` 面全部采样图案。报告：`root-cause-report.json`。
- rev 13 固定 slot ID：`0=top artwork`、`1=solid dark side`、`2=polished bright silver rim`、`3=neutral underside`。Blender 原面数：Bottom=`1 / 3,078 / 2,052 / 3,592`；MovingTop=`1 / 5,130 / 2,052 / 3,600`。每面另存 `M07R13_MaterialZone`，分区 digest 分别为 `91fecf38…2e26`、`e256f01a…bb12`。
- 上下 cap 使用独立 `ArtworkUV` 与独立材质／贴图。cap UV 范围共同为 `U 0.014516–0.985484 / V 0.009000–0.991000`；非 cap loop 写入 `(-1,-1)`。图像节点使用 `EXTEND`；GLB sampler `wrapS=wrapT=33071`，即 `CLAMP_TO_EDGE`／no-wrap。深色 side、银 rim 与 neutral underside 都没有 image node。
- Blend、GLB 重导、FBX 重导对两片均为 side artwork faces=`0`、underside artwork faces=`0`、non-cap textured faces=`0`。GLB 与 FBX 的每片 top artwork 都为 `511` triangles，且各分区 triangle counts 逐项一致。GLB 为 `2 meshes / 5 materials / 8 primitives / 4 embedded images`；每片固定四个 material primitive。报告：`material-transport-audit.json`。
- 上下 albedo／roughness 与已批准 rev 12 逐字节相同；upper/lower mask SHA-256=`8250df70…1c36 / 7bf5921f…a7c2`，继续独立替换。图案只在平面顶面；竖直侧壁为深色实体，细 bevel 为亮银；底面与隐藏技术件无图案。
- 几何 digest 在材质前后保持 `2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952`。固定轴方差=`0 mm`，底片顶面偏差=`0 mm`，轴座凸出=`0.2 mm`，四条顶片底槽保留；密集状态=`4,359`，拦截中段旋转=`4,000`、非零角回推=`359`，最小覆盖漏点／穿透／flip／同时速度违规=`0/0/0/0`。
- 真实 Blender 合法运动成片为 `gate07-r013-legal-motion-turntable.mp4`：`960×720 / 30 fps / 180 encoded frames / 6.0 s`；先在 `θ=0°` 推到 `sMax`，只在端点转满 360°，回到对齐后才回推。交互主资产为 `magnetic-slide-tile-material-r013-lookdev.glb`。
- 评审：`gate07-r013-material-review-board.png`、`gate07-r013-top-side-rim-closeups.png`、`gate07-r013-rejection-correction.png`。工作台深链：`?model=magnetic-slide-tile&tab=materials&gate=07-material&asset=magnetic-slide-tile-material-lookdev-r013`。
- 验证：Gate 07 focused Node=`6/6`；全 Model Provenance Explorer=`204/205`，唯一失败为并发 Premium Display Case 测试仍期待 Gate 12 approved，而当前该模型 Gate 04 rev 23=`draft`，本任务未改其测试。model／全 pipeline validators 对 magnetic slide 均为 errors／missingFiles／unhashed=`0/0/0`。桌面、`390×844` 移动、GLB load/orbit/zoom、6 秒视频、图片 modal、reload 和 direct deep link 均通过，runtime／loading failure=`0/0`。Blender／GLB／FBX、material／UV／sampler／video、Python／JavaScript／XML 和 focused diff 均通过。
- DeliveryState：仅完成 Gate 07 材质候选及审批证据。未进入 Gate 08、Simulator、最终 Unity、shipping build、安装、启动或物理手机；Device Accepted pending。

## 2026-09-01 Pack Opening Gate 04 R025 technical visual rejection

> **当前状态：pipeline rev=`102`。Gate 01–03=`approved`；Gate 04 stage rev=`34`=`draft` / `technical-visual-rejected`；R025=`isolated technical candidate, rejected`；`approvalRequestAllowed=false`；primary review artifacts=`[]`；Gate 05–12=`stale`；`shippingReady=false`；未 build／install／launch／测试物理手机。**

- 技术视觉否决，不是用户否决：直接全尺寸审查优先于候选的投影、ID/bounds 与测试断言。
- `full-proof/normal/seven-pose-contact-sheet.png`（SHA-256=`d7410b46a3f1f311db496b319fca38267b7103d0ac601b533d462db1161e22ff`）显示平坦 Pack 正面和大斜切，不是窄的实体 foil mouth；真实 case 读成宽大的深色矩形后板，而不是在 front lip／inner liner 后方被容纳的对象。
- 主要帧仍有 rail/strip-like artifacts，未建立 outer foil → inner liner/cavity → contained case 的因果。`r025-full-proof-full-size-review.json`（SHA-256=`b83be1faf77e8ad6965c81e4822b1539e5ba789022ad7668648bad2af2c477b4`）与 normal proof（SHA-256=`e4f0fddd6d39565a655f87c59082388f11fe1474f9b745fe9af1df497d7c0376`）作为 immutable rejected history 保留。
- 验证与视觉结论分开：target-aspect preflight=`23/23`、isolated structural checks=`7/7`、filtered EditMode=`17/17`、scrub=`11/11` 均通过；这些实现检查不能推翻直接全尺寸视觉失败。
- 保留 prior ready event=`2682f14a-2bd6-44ad-8ad1-31f9bf1a55aa`；rejection event=`20a6deb0-4981-44c0-8256-de79ae23c7db`，issue=`6b530dff-1861-49b2-900a-6159f726be4e`。R025 未获批准、未进入 shipping、未做 device test。
- 未改 Pack、Case、Toy、FBX、Blender、shader、Unity runtime/candidate、`contentSlot`、FanCard、packages、build artifacts 或用户资产；没有 build、install、commit、push、delete 或新视觉 iteration。

## 2026-08-31 Pack Opening Gate 04 R015 isolated candidate 自我拒绝

> **当前状态：pipeline rev=`94`。Gate 01–03=`approved`；Gate 04 stage rev=`26`=`draft`；R015=`self-rejected`；`approvalRequestAllowed=false`；Gate 05–12=`stale`；approved count=`3/12`；`shippingReady=false`。视觉批准待确认，未推送手机。**

- 用户已批准的 motion/reference 选择“卡包的容纳／抽出因果＋箔层双层剥离”已记录。三个外部 URL 仅作动作参考；未导入视频帧、图像、模型、音频或品牌资产。
- R015 是隔离 Unity `6000.5.6f1 / URP 17.5.0` candidate：Pack-only Blender FBX 有 `49` 个手作 guide stations、`11` 个 Pack mesh、六个 blend shape；真实 `384×512` body/flap 未改。场景只预实例化一个不变的 assembled case，caller-owned `ContentSlot` 未改，没有 case bake、swap、proxy、particles、VFX Graph、CTA、Haptic 或 shipping wiring。
- 实际 Unity Camera capture 为 `1206×2622 / 60 fps / 96 frames / 1.60 s`。首次 capture 的 Pack edge-on；唯一允许的 root-orientation micro-polish 后 Pack 正面可见但 artwork 倒置，frames `14–68` 仍是密封矩形，没有可读 tear、袋口、容纳或连续抽出。case 只在 Pack 消失后可读，故该候选不符合中性评审者因果判断。两个 attempt 和七张 full-size pose 均保存在 `evidence/04-architecture/rev-015/`；没有生成待审批 MP4。
- 验证：isolated emitted C# checks=`5/5 pass`（`isolated-r015-check-results.xml`）；capture structural checks=`25/25`，仅证明同一 case ID、constant scale、状态／反向回弹和 zero-VFX 路径，不能替代视觉验收。Premium Display Case 与 all-pipeline provenance validators 均为 errors／missingFiles／unhashed=`0/0/0`，最早问题保持 Gate 04=`draft`且有一个视觉失败。Model Provenance Explorer full test=`197/226 pass`、`29` fail；失败属于并行 magnetic-slide / historical-stage assertions，本任务未修改或修复。
- Gate 04 rev `8–14` rejected evidence 保持 immutable。R015 self-rejection event=`c657b24f-183c-4236-a756-dbd21e38289a`；source mapping、runtime representation 和 concise verdict 均在 rev-015。未修改 Fan Card、canonical shipping prefab／coordinator、native UI、receipt/ACK、skip、interruption 或任何物理设备。

## 2026-08-30 Pack Opening Gate 04 rev 13 Pack-only Blender 自我拒绝

> **当前状态：pipeline rev=`93`。Gate 01–03=`approved`；Gate 04 stage rev=`25`=`draft`；R013 iteration 11=`self-rejected`；`approvalRequestAllowed=false`；Gate 05–12=`stale`；approved count=`3/12`；`shippingReady=false`。未 build／install／launch 物理设备。视觉批准待确认，未推送手机。**

- R013 选择首选运行时表示：真实 `384×512` Pack artwork 的 Blender Pack-only FBX，相对 blend shape `0/0.15/0.35/0.55/0.75/1.0` 由 normalized drag 成对插值；`96` 条纵向撕裂列。FBX 不含 case 几何或烘焙 case 图像。Unity 只预实例化一个不变的 assembled Premium Display Case，capture 保留同一 root/renderer ID、constant scale、mouth containment、physical crossing、无 early travel／black／white frame／bounds jump。
- 实际 Unity PlayMode Camera 证据为 `1206×2622 / 60 fps / 210 frames / 3.50 s`。主图和技术媒体分别归档在 `evidence/04-architecture/rev-013/iterations/iteration-11-full-size-self-rejection/primary-contact-sheet.png`、`continuity-contact-sheet.png`、`technical-continuity-sheet.svg`、`source-target-side-by-side.png` 和 `runtime-footprint-editor-estimate.json`。Blender closed/open rig render 及 build report 保留在 rev-013 根目录。
- CC0 mapping 保留 source commit `88842be0063b5b0b75e82ed6572752a37a13c82b`、CC0-1.0、Timeline／`Booster_Discarded.anim`／`SG_BoosterPack`／`SG_Title_Kyle`／`SG_LightingStrike`／flare／noise 的 direct-copy、adapted、rejected SHA-256 记录：`iterations/iteration-11-full-size-self-rejection/source-to-canonical-mapping.json`。R013 没有 VFX Graph、sample Pack、sample case 或 Python/PIL 合成帧。
- 全尺寸视觉检查拒绝：`frames/frame-0065.png` 的 strip/lip 读成刚性蓝色 U 形轨条；`frame-0083.png`／`0100.png` 的开口读成硬边 scallop；tear close-up 的 CC0 Shuriken 读成叠加红色矩形，而非窄暖中性 torn-contour sweep。技术连续性通过不能替代这三项视觉失败。记录：`self-rejection.json`。
- 编码与测试受存储阻塞：本机仅余 `119 MiB`，ffmpeg 无法创建 MP4；所有真实 Unity PNG 序列仍已归档。为避免 Unity reimport／log 写满卷并污染项目，R013 focused EditMode 未重跑，不能声称其通过。后续必须先获得可用存储，再重做物理 lip/strip 与 source particle layout 并 capture/test。
- 资产完整性验证通过：`validate_model_pipeline.mjs premium-display-case` 与全 `validate-pipelines.mjs` 均为 errors／missingFiles／unhashed=`0/0/0`；最早问题正确保持 Gate 04=`draft`，有 `4` 项失败验证。history event=`0990cc21-5336-46ce-93f2-a104fff8c08b`；R013 主媒体不在 `reviewArtifactIds`。
- 未接 shipping prefab／coordinator／native UI；未改 case prefab、`contentSlot` toy、semantic Haptic、receipt/ACK、stale request、skip、interruption restoration 或 Reduce Motion。

## 2026-08-30 Pack Opening Gate 04 rev 12 物理撕口自我拒绝

> **当前状态：pipeline rev=`92`。Gate 01–03=`approved`；Gate 04 stage rev=`24`=`draft`；R012=`self-rejected`；`approvalRequestAllowed=false`；Gate 05–12=`stale`；approved count=`3/12`；`shippingReady=false`。物理 iPhone／Android 未 build／install／launch。视觉批准待确认，未推送手机。**

- R012 是一次真实 Unity Mesh API 架构重做：真实 `384×512` Pack、`128` 个纵向撕裂段、前／后封层、前唇／后缘／侧壁／后壁、窄双面 foil strip、一个预实例化 assembled case 与不变的 caller-owned `contentSlot`。未改 shipping prefab、toy、semantic Haptic、receipt/ACK、stale-request、interruption、skip、Reduce Motion 或 native CTA。
- CC0 原始 Timeline、discard curve、`SG_BoosterPack`、`SG_Title_Kyle`、`SG_LightingStrike`、flare/noise 均以 hash 保留。R012 只适配 torn-contour discard 与 Shuriken sphere-mask sweep；不使用 VFX Graph、像素噪点 dissolve、紫雾、圆环或合成帧。映射：`evidence/04-architecture/rev-012/source-to-canonical-mapping.json`。
- 全尺寸检查拒绝：`frame-0055`–`0103` 的后壁和侧壁读成刚性盒盖；`frame-0062`–`0096` 的 case 未在穿出前清晰占据袋口；`frame-0050`–`0103` 的自由 strip 读成平直长带；source flare/sweep 被暗腔体压没。记录：`evidence/04-architecture/rev-012/self-rejection.json`。该媒体不进入 `reviewArtifactIds`，未向用户请求批准。
- 实际 Unity PlayMode 证据：`1206×2622 / 60 fps / 216 frames / 3.60 s`；0.25× tear=`250` 帧、impact=`202` 帧，均由 Unity PNG 编码。capture report 的单 case ID、constant scale、连续 bounds、`0.002382` 最大白像素比例、无黑帧与 source comparison 均通过，但不替代视觉结论。
- 验证：focused EditMode=`12/12 pass`（`Logs/PackOpeningGate04R012Results-r012final.xml`）。history self-rejection event=`5b8ea86e-496e-4c2d-8035-c489f4c8b3e5`；state normalization event 追加 Gate 05–12 全部 stale。下一步必须先重定袋口占位／后壁策略；不得进入 Gate 05、shipping wiring、build 或物理手机。

## 2026-08-30 Pack Opening Gate 04 rev 11 iterations 11–12 自我拒绝

> **当前状态：pipeline rev=`90`。Gate 01–03=`approved`；Gate 04 stage rev=`23`=`draft`；iteration 11 与单次 correction iteration 12=`self-rejected`；`approvalRequestAllowed=false`；Gate 05–12=`stale`；approved count=`3/12`；`shippingReady=false`。物理 iPhone／Android 未 build／install／launch。视觉批准待确认，未推送手机。**

- iteration 11 全尺寸检查：袋口变成宽平矩形切口，释放 foil 是硬暗三角楔；盒体身份连续，但读成在被切开的面板后方。记录：`ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-011/iterations/iteration-11/self-rejection.json`。
- iteration 12 是唯一执行的 corrective pass。真实 `384×512` Pack、同一 preloaded assembled case、CC0 source Timeline／discard curve／`SG_BoosterPack` edge math／`SG_LightingStrike` mask and flare atlas 保留；只收窄袋口、限制侧壁并改变 foil mesh/material。未改 shipping prefab、`contentSlot` toy、semantic Haptic、receipt/ACK、stale rejection、skip、interruption restore、Reduce Motion 或原生 CTA。
- iteration 12 全尺寸检查仍不合格：袋口只剩暗缝，无法作为有内壁／接触遮挡的成形开口；foil 从刀片变为重复阶梯边，仍非可读卷箔；source flare/streak 有粒子计数却在 impact 帧不可辨。记录：`ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-011/iterations/iteration-12/self-rejection.json`。
- 实际 Unity PlayMode 证据：`1206×2622 / 60 fps / 207 frames / 3.45 s`；normal、tear `0.25×` 和 impact `0.25×` 视频均只由相应 Unity PNG 编码。primary sheets：`iterations/iteration-12/tear-contact-sheet.png`、`source-impact-contact-sheet.png`、`continuity-contact-sheet.png`、`source-target-side-by-side.png`；诊断独立于主图：`technical-continuity-sheet.svg`。capture report 的单 case ID、constant scale、bounds continuity、no-black／no-white、no rarity leak 与 no placeholder checks 均通过，但不替代视觉验收。
- 验证：首次 `i12` focused EditMode=`35/36`，任务造成的 cavity back-wall normal discontinuity=`16.13°` 已以平滑 hidden support wall 修正；复跑=`36/36 pass`（`Logs/PackOpeningGate04R011Results-i12fix.xml`）。Premium Display Case 与全 pipeline validators 均为 errors／missingFiles／unhashed=`0/0/0`，最早问题正确为 Gate 04=`draft` 且有 `2` 项视觉 self-rejection validation fail。
- pipeline history event=`93f096c8-a6d6-4456-98e4-62f4ef189ab5`，保留 rev 8／rev 9、iteration 01–10 和 iteration 11／12 全部记录；iteration 11／12 primary media 不在 `reviewArtifactIds`。
- 下一门禁：等待新的用户视觉方向后才允许再做 Gate 04 iteration。不得进入 Gate 05、shipping wiring、build 或物理手机。

## 历史：2026-08-28 Pack Opening Gate 04 rev 11 iteration 10 CC0 复用重定向

> **历史状态：pipeline rev=`89`。Gate 04 iteration 10 曾为 `ready_for_review`，后由 iteration 11／12 self-rejection 取代。未获得用户视觉批准、未进入 Gate 05、未 build／install／launch 物理设备。**

- 本轮修的是 parent 指出的最高优先缺陷：**Pack 从未真正打开**。iteration 09 确实让前面板轮廓下退了，但**袋子没有内部**——没有背壁、没有侧壁、没有撕裂前沿横壁、没有边缘厚度。前面板让开的区域直接露出背景，所以剪影只是"变矮"，读起来像盒子从一个完好袋子**后面**滑上来。空腔当时只是一条贴着下退边缘移动的 `19 mm` 细带，而不是被那条边缘揭开的体积。
- ① 可见开口（已修）：空腔改为真实袋口。背壁置于 `InteriorBackWallZ=0.082`，在被藏起的盒子（`z=0.060`）之后，所以盒子在升起之前**确实在腔体之内**；撕裂前沿加横壁封住未撕开的一侧；释放端加侧壁保住袋口边缘；撕裂前缘加 `TornEdgeLipDepth=0.0115` / `TornEdgeLipDrop=0.0042` 的内折唇给出箔材厚度。另设独立 submesh 的接触遮挡带（`ContactBandFraction=0.34`，材质 `0.014`）覆盖唇口正后方，其上背壁按 `InteriorRimTilt=0.018` 向袋口倾斜以获得光照梯度。证据：`frames/frame-0060.png` 左半仍密封在原袋口高度、右半已开且内部有遮挡；`frame-0084.png` 全宽袋口下唇口后方为暗接触带，盒子的 `TactileBackgroundInsert` 竖纹与外壳轮廓在腔内可见；`tear-contact-sheet.png` 显示开口自右向左推进且每一步都在剪影中可读。
- ② 撕裂期的源 edge sweep（已修）：前面板新增 uv2 承载 **torn-contour 空间**——`x` 为该列到撕裂顶边的归一化深度、`y` 为到撕裂前沿的接近度；发光带改在 `uv2.x` 上求值，因此几何上不可能退化为全宽横矩形，且在任意 tear progress 都紧贴撕裂线。强度由 `TearSweepStrength(tearProgress)` 驱动并以"已开度"门控，未撕开的封边不会发光。`_EdgeWidth` 回到 `0.022`，discard 边界改由 uv3 逐列抖动（`_DissolveJitter=0.052`）以不规则撕开。证据：`frame-0060`／`frame-0084` 中 `packDissolve` 仍为 `0.00`、`STANDARD` 全不透明时暖色带已沿不规则撕裂轮廓点亮；`frame-0136` 为锯齿状轮廓相关边，**两条奶油色横矩形已消失**。
- ③ 箔材而非刀片（已修，有残留）：带宽 `0.026`→`0.045 m`；正面 metallic `0.72`→`0.28`、smoothness `0.58`→`0.24`；内侧基值 `0.105`→`0.068`；卷曲 bezier 改为在 Pack 自身宽度内翻卷而不再伸出右缘；逐列宽度缩放与三个非公倍项的表面波纹打断自由边；`GenerateTearOffsets` 新增未平滑的 micro 项（3-tap 平滑权重 `0.235`→`0.170`），使撕裂边在列尺度上反向。残留：卷曲末端仍读成一块硬的暗色楔形。
- ④ 去除彩色 sparkle（已修）：两个独立成因，且各自的第一次修法都是错的。洋红来自源 lifetime gradient 在 `0.333` 的紫键与 `0.667` 的饱和青键——**打散发射只能让它出现在更少粒子上**，本轮直接把这两个色键从 gradient 中排除，同时保留源的键位与暖→冷走向。字形则来自 flare 材质**完全没有 atlas 平铺**，每个 billboard 同时采样四格（含右上四角星）；修好平铺后字形仍在，因为 `rotationOverLifetime` 把剩下那格转过了读成对称星形的角度；而且**源 atlas 没有任何一格是纯水平条纹**。最终：所有 flare 端口经材质平铺各自只寻址一格、flare 与 activation 用水平主导格、旋转仅保留给径向光晕端口、flare billboard 压扁为 `1.55 × 0.16` 让未修改的源贴图读成条纹。证据：`frame-0114` 的 2× 最近邻放大只见两道干净水平条纹（一暖一中性），无四臂字形、无洋红与青色。
- 连续性未退化（并有一处改进）：207 帧仅一个 `caseRootId`；case 投影高度 `0.4369`→`0.5545`，相邻帧最大步进 `0.00384`。**如实说明**：最小步进为 `-0.0026`，负步进只出现在收尾 settle 的既定 overshoot 松弛段，撕裂／dissolve／reveal 全程单调；该数值与 iteration 09 完全相同，非本轮引入。改进项：主体可见性原先由 `PackRetreat` 门控，会在 `packDissolve=0.9984` 就关掉 renderer；现改由 discard 曲线门控，`packVisible` 只可能在 `packDissolve=1.0` 时（frame `152`）翻为 `false`。
- 自检（作为证据，不代表通过视觉验收）：capture report `status=pass`，`26/26` check 全通过。真实 Unity capture：`1206×2622 / 60 fps / 207 frames`。ffmpeg 只编码真实 Unity PNG；无 Python／PIL 合成帧。
- 逐帧全尺寸自检结论：四项优先缺陷均判定为已修，故本轮**请求**用户视觉批准。同时如实披露四项 polish 级残留（不破坏因果读法）：袋口上缘是近直线而非压花封边轮廓，开口略显矩形；释放端侧壁在 `frame-0084` 露出一条位于前面板剪影外的细条；卷曲末端读成硬楔形；条纹粒子在联系表缩略尺度下像小斑点（全尺寸下是干净条纹）。记录见 `iterations/iteration-10/self-review.json`。
- **证据丢失（如实记录）**：iteration 09 的像素证据（207 帧、四张联系表、capture report、三段 mp4）在本轮 capture 与重新编码中被覆盖，因为它此前**从未**归档到 `iterations/iteration-09/`，而 capture 入口就地重写 live 目录；git 对该证据目录未跟踪，无法恢复。其**书面结论完整存活**于 `iterations/iteration-09/self-rejection.json`，iteration 10 正是依据它推进的。记录见 `iterations/iteration-09/EVIDENCE-LOSS.json`。为防复发，iteration 10 的证据已在本任务内立即归档到 `iterations/iteration-10/`；但 capture 入口仍无逐 iteration 输出槽、也不会在 live 目录存在未归档证据时拒绝运行，归档仍是可被后续 agent 跳过的手工步骤。
- asset id 命名已修：`…-i09-self-rejection`→`…-iteration08-self-rejection`、`…-i09-EVIDENCE-LOSS`→`…-iteration02-evidence-loss`，与其实际指向的 iteration-08／iteration-02 文件一致。history 为 append-only，旧事件原文保留。
- 验证：focused Unity EditMode=`34/34 pass`（`Logs/PackOpeningGate04R011Results-r24.xml`），新增 `Pack_VisiblyOpensInsteadOfBeingSlicedShort`、`CaseIsConcealedInsideTheCavityNotBehindTheBag`、`SourceEdgeSweep_IsLitWhileThePackIsStillFullyOpaque`、`TornEdge_IsIrregularRatherThanASmoothCurve`、`PackStaysVisibleUntilTheDiscardCurveReachesOne` 五项回归；`Scene_UsesSourceShurikenCapacitiesAndNoGenericRing` 中"sheet animation 必须开启"的断言已改为"每个端口只寻址单格 atlas + 仅径向光晕可旋转 + flare 必须压扁"，以匹配新的机制。`node skills/fidgeting-model-pipeline/scripts/validate_model_pipeline.mjs premium-display-case` 与 `node tools/model-provenance-explorer/validate-pipelines.mjs` 全部 7 个 model 均为 errors／missingFiles／unhashed=`0/0/0`；earliest problem 正确指向 Gate 04 `ready_for_review` / “等待用户审批。”。无并发失败需要单独报告（除 Unity Hub 外无 Unity／Xcode 进程，批处理沿用 `run-gate04-r011.sh` 锁）。
- 当前仍是 candidate：代码、场景、材质、mesh、profile、shader 与 review media 全在 `Assets/_DisplayCase/Candidates/PackOpeningGate04R011/` 与 Gate 04 rev-011 evidence 路径。未接 shipping prefab／coordinator／native UI；整盒／`contentSlot` toy、语义 Haptic、`FidgetProductUIComponents.swift` 原生 CTA 归属、exact-once receipt/ACK、stale-request 拒绝、中断恢复、skip 与 Reduce Motion 边界均未改，enclosed toy 未编辑，shipping case prefab 未编辑（腔内可见的竖纹是该 prefab 自带的 `TactileBackgroundInsert`，因内部足够暗才显现）。
- 残余 gap：重定向配色仍比源偏冷，因为源的暖色主导来自 rarity card emissive，而它不得在权威 receipt 之前出现；这一约束正确，不得通过泄漏 rarity 解决。
- 下一门禁：等待用户对 iteration 10 的明确视觉批准。获批后才处理最早 stale Gate 05。当前不进入 CTA、四 rarity tier、shipping wiring、build 或物理手机。

<details>
<summary>历史：2026-08-28 Pack Opening Gate 04 rev 11 iteration 09 已自我拒绝</summary>

> **历史状态：pipeline rev=`88` 时 Gate 04 stage rev=`21`／evidence rev 11 iteration 09=`draft · 自我拒绝`，`approvalRequestAllowed=false`，从未向用户请求视觉批准；其后由 iteration 10 取代。其像素证据已被覆盖丢失，见 `iterations/iteration-09/EVIDENCE-LOSS.json`；书面结论保留于 `iterations/iteration-09/self-rejection.json`。**

- 自我拒绝结论：iteration 09 在逐帧全尺寸检查后不合格，需要 iteration 10。它没有、也不得被送去请求用户视觉批准。记录见 `iteration-09-self-rejection.json`；self-rejection event=`507f03a4-51d4-43d2-a26b-e08adf3de2a9`。

- 方向纠正：用户以原话“你之前做过的这个，从 GitHub 上找到的这些 example，你不能直接用吗？你为什么要重新做一个转场的光效呢？”否决了从零重画转场光效。本轮不再自研光效，改为直接复用已审计 CC0 Make It Shine 示例（commit `88842be0063b5b0b75e82ed6572752a37a13c82b`，CC0-1.0），只写 URP `17.5.0` / Unity `6000.5.6f1`、portrait、真实对象绑定与 VFX Graph→Shuriken 的最小适配层。见 `FDB-GAC-028`。
- 复用账目（`source-to-canonical-mapping.json`，25 条，逐条带 source／destination SHA-256）：`direct-copy=13`、`adapted=6`、`rejected=6`。direct-copy 含 `Booster to Card Timeline.playable`（`baec0abc…9b086`）、`Booster_Discarded.anim` 归一化 discard 曲线、`SG_BoosterPack` / `SG_LightingStrike` / `SG_Title_Kyle` / `SG_SelectedBooster` / `CardMask` 图与源贴图 `TX_Flare_2x2_M.png`、`TX_Noise_M.tga`，全部按字节存入 `source-raw/`。
- adapted 6 项及原因：Timeline→`MakeItShineRetargetedR011.playable`（保留源 effect 顺序与 matched timestamp，产品对象只剩 Pack 与一枚预实例化真盒）；`SG_LightingStrike`→`MakeItShineCc0PortR011.shader`（VFX-targeted 图不能直接绑 Shuriken，保留 Reveal/Erode/Speed 契约与源 flare 贴图）；`SG_BoosterPack`→`MakeItShineCc0PackR011.shader`（源图依赖源 mesh 顶点色／UV，改为在真实 `384×512` Pack 上承载 discard 曲线与 emissive torn-edge sweep）；`VFX_BoosterActivation`／`VFXG_LightingStrike`／`VFX_BoosterExplosion`→Shuriken 端口（VFX Graph 被禁，沿用源 curve、gradient family 与贴图）。
- rejected 6 项及原因：`Opening_Booster.prefab`（含 sample Booster、fracture 模型与 object-swap 归属）、`BoosterFractured_B.fbx`（sample 几何与 fracture swap 被禁）、`Spawn Cards Timeline.playable`（三卡 proxy 交接由同一枚真盒取代）、`M_BoosterPack.mat`／`MV_Pack_A.mat`／`TX_Title_Kyle.png`（绑定 sample 贴图与 sample 标题美术，不导入、不显示）。`vfxGraphDependency=false`、`sampleModelsImported=false`、`sampleArtworkImported=false`。
- 自我拒绝 iteration 01–08 全部保留为 immutable labeled history（`iterations/iteration-01 … iteration-08`）。主线为：01 Pack 退场摊成平面大片、flare 变洋红团；02 源 noise 贴图暴露像素孔洞违反 no-pixel-noise；03 wipe 修好但 flare 仍同步走 atlas；04 源 atlas 出现但被柔性 dust 压过；05 源图正确但原始尺度让 trail 铺满视口；06 aperture 绑定修好但 512 spark 变亮方块 confetti；07 25 条 trail 的 billboard head 仍是白方块；08 曝光不匹配（Pack unlit 对真盒 URP Lit）、freed foil 因 `UpdateStripMesh` 局部偏移而脱离、`168°` 扭转让 foil 读成宽平板。iteration-02 的像素 artifact 曾被误覆盖，损失已在 `iterations/iteration-02/EVIDENCE-LOSS.json` 如实记录，其 `self-rejection.json` 与 mapping 保留。
- iteration 09 修复：Pack 主材 `_EdgeWidth`／`_EdgeStrength` 提高并改暖近白 `_EdgeColor`，让获批 discard edge sweep 成为转场身份主载体；directional light 与 ambient sky／equator／ground、reflection intensity 整体提高以消除 Pack 与真盒的曝光断层；flare 起始色改白热、由源 lifetime gradient 驱动色相，并把发射拆成多次 burst、加大 shape radius 与 `radiusThickness=1`，消除同步造成的洋红团；spark 改 `velocityScale`／`lengthScale` 读成细长条纹而非箭头字形；cavity 材质提亮以在 0.25× 特写下给出内部深度；freed foil 局部偏移下调避免脱离，最大扭转由 `168°` 降到 `94°`；pack retreat 位移设 `MaximumPackRetreatTravelMeters` 上限，让退场由 dissolve 而非平移完成；`GenerateTearOffsets` 降低确定性正弦项并叠加两个非公倍低频项、加大幅度，得到非锯齿不规则撕裂边。
- 真实 Unity capture（`PackOpeningGate04R011.unity` PlayMode + Camera，非离线合成）：normal=`normal-speed-sequence.mp4`，H.264 `1206×2622 / 60 fps / 207 frames / 3.45 s`；tear 特写=`tear-quarter-speed-closeup.mp4`，`0.25×`、`1206×2622 / 60 fps / 197 frames`；impact/reveal=`impact-reveal-quarter-speed.mp4`，`0.25×`、`1206×2622 / 60 fps / 187 frames`。三段均为 `1206×2622` shipping portrait。ffmpeg 只编码并用 ffprobe 测量 Unity PNG；无 Python／PIL 合成帧。
- 联系表：`tear-contact-sheet.png`（撕裂剪影）、`source-impact-contact-sheet.png`（impact 连续性）、`continuity-contact-sheet.png`、`source-target-side-by-side.png`（源与重定向在 `matched-timestamps.json` 对齐时间戳并排）。
- 自我拒绝的四项根因（criterion 编号对应用户验收标准）：①criterion 4 失败——获批的 Make It Shine discard edge sweep 在撕裂阶段不可读：frames `54–96` 的 `packDissolve=0.00`，emissive edge 只在 `108–150` 的 dissolve 斜坡上被驱动，所以本轮唯一存在理由的源身份在撕裂主体阶段毫无贡献（见 `frames/frame-0114.png`，Pack 全不透明、`STANDARD` 清晰、torn 轮廓无发光）。②criterion 2 失败——freed foil 读成一把刚性镀铬刀片／鞋拔：长而光滑、硬边、镜面条纹、轮廓平直，没有内侧、厚度与不规则撕裂边；根因是 strip 过于 smooth／metallic，且 `GenerateTearOffsets` 的偏移仍是平滑 C1 曲线，缺高频微观细节与逐列深度变化。③criterion 5 失败——aperture 内仍有四角星 sparkle 字形与残留洋红污点：加大 lifetime 离散与 burst 只是让洋红一次出现在更少粒子上，并未从源 gradient 中排除洋红段，且 2×2 atlas 仍以对称星形帧为主。④criterion 5 在 dissolve 中段失败——加宽的暖近白 edge band 退化成两条与 torn 轮廓无关的横向奶油色矩形（见 `frames/frame-0136.png`）。另有 major 项：成形空腔在 `0.25×` 下仍是细暗带而非有遮挡的内部体积，根因是空腔缺内侧壁与接触遮挡，提亮只是抬高平带亮度。
- 非拒绝项说明：真盒渲染为半透明烟灰亚克力、可透视看到退场的 Pack，这来自未修改的 shipping prefab `PresentationRoot.prefab`，对亚克力展示盒是正确的，不计入拒绝原因，prefab 未编辑。但它确实让低对比交接更难读，应通过盒后 key 分离而非改 prefab 解决。
- iteration 09 确有的真实进步：Pack 与真盒的曝光断层已消除；freed foil 不再脱离 `packRoot`，最大扭转由 `168°` 降到 `94°`；pack retreat 变为有界 settle，退场由 `packDissolve` 而非平移完成；连续性是真实而非模拟——207 帧只有一个 `caseRootId`，case 投影高度由 `0.4369` 单调增至 `0.5545`、相邻帧最大步进 `0.0038`，`packVisible` 仅在 `packDissolve` 达 `1.0` 后翻为 `false`，无 hard pop、黑帧、白帧、identity swap 或 bounds jump；iteration 05–07 的 512 spark 与铺满视口 streak 继续被抑制。
- iteration 10 必做项：让获批 discard edge sweep 由 `tearProgress` 沿 torn 轮廓驱动，使源身份在 frames `54–96` 就存在；把 emissive edge band 与 torn 轮廓相关联，使其在 dissolve 中段不可能退化为全宽横矩形；降低 strip smoothness／metallic 并加入高频逐列微偏移；从源 lifetime gradient 中排除洋红段并优先使用源水平条纹 atlas 帧而非对称星形帧；给空腔加内侧壁与接触遮挡。
- 自检（作为证据，不代表通过视觉验收）：capture report `status=pass`，`26/26` 结构／来源／禁用项 check 通过，含 `realUnityPlayModeCapture`、`shippingPortrait1206x2622`、`exact60Fps`、`sameCaseIdentityEveryFrame`、`sameCaseScaleEveryFrame`、`sameCaseVisibleThroughAperture`、`sameCaseCrossesPhysicalPack`、`sourceShurikenCapacitiesExact`、`sourceDiscardCurveDrivesPack`、`aheadOfTearFrontRemainsWelded`、`noBlankWhiteFrame`、`noBlackFrame`、`noPlaceholderRingWashOrSampleEntity`、`noReceiptRarityLeak`、`reduceMotionPreservesCausality`、`shippingReadyFalse`、`physicalPhoneInstalledFalse`。度量：flash 后 maximum white fraction=`0.002928`；minimum visible fraction=`0.851821`；maximum projected center step=`0.002438`；maximum projected height step=`0.003838`；maximum root position step=`0.00946 m`；maximum ahead-of-front separation=`0.0 m`。这些数值只作证据，不替代视觉判断——本轮正是 `26/26` 全通过但逐帧检查仍不合格的例子，度量通过不等于视觉合格。
- 残余 gap：重定向配色仍比源偏冷，因为源的暖色主导来自 rarity card emissive，而它不得在权威 receipt 之前出现；这一约束正确，不得通过泄漏 rarity 解决。
- 当前仍是 candidate：代码、场景、材质、mesh、profile、shader 与 review media 全在 `Assets/_DisplayCase/Candidates/PackOpeningGate04R011/` 与 Gate 04 rev-011 evidence 路径。未接 shipping prefab／coordinator／native UI；整盒／`contentSlot` toy、语义 Haptic、`FidgetProductUIComponents.swift` 原生 CTA 归属、exact-once receipt/ACK、stale-request 拒绝、中断恢复、skip 与 Reduce Motion 边界均未改，enclosed toy 未编辑。
- 验证：focused Unity EditMode=`29/29 pass`（`Logs/PackOpeningGate04R011Results-r11.xml`），新增 `PackRetreat_StaysASettleAndLetsTheDiscardCurveRemoveThePack` 与 `FreedFoil_CurlsWithoutPresentingItsWidthToCamera` 两项回归。`node skills/fidgeting-model-pipeline/scripts/validate_model_pipeline.mjs premium-display-case` 与 `node tools/model-provenance-explorer/validate-pipelines.mjs` 全部 7 个 model 均为 errors／missingFiles／unhashed=`0/0/0`。两者 earliest problem 均正确指向 Gate 04 `draft` / “仍有 3 项验证未通过。”，即上述三项 blocking 视觉验证被如实记为 `fail`，未被掩盖。无并发失败需要单独报告。
- pipeline：先由 realignment event=`162af5ae-7904-4646-b18c-c3eb718e6a11` 把 Gate 04 从残留的 rev-9 `rejected` 状态与 iteration-09 证据对齐（stage rev `20`），并把 rev-9 拒绝决定完整存入 `historicalDecisions`／`historicalRevisions`；随后 self-rejection event=`507f03a4-51d4-43d2-a26b-e08adf3de2a9` 把 stage 降为 rev `21` `draft`、`approvalRequestAllowed=false`、`reviewArtifactIds=[]`，避免把自我拒绝的证据挂成待审批。pipeline rev `86`→`87`→`88`。iteration-09 原 ready 记录 event=`6452e421-7f75-45e8-8544-cd7e832808cc` 保留为历史。
- 已知登记瑕疵（不影响 validator）：`premium-display-case-gate04-r011-i09-self-rejection` 与 `…-i09-EVIDENCE-LOSS` 两个 asset id 带 `i09` 前缀，但实际指向 `iterations/iteration-08/self-rejection.json` 与 `iterations/iteration-02/EVIDENCE-LOSS.json`。路径与 hash 正确，仅命名易误读；iteration 09 自身的记录是 `iteration-09-self-rejection.json`。（已在 iteration 10 更名修复，见上文。）
- 下一门禁：iteration 10 先修上述四项 blocking 根因并重新 capture、重新逐帧全尺寸自检；只有自检合格后才向用户请求视觉批准，只有获得明确视觉批准后才能处理最早 stale Gate 05。当前不进入 CTA、四 rarity tier、shipping wiring、build 或物理手机。

</details>

## 历史：2026-08-28 Pack Opening Gate 04 rev 9 已技术拒绝

> **历史状态：pipeline rev=`84` 时 Gate 04 rev 9=`ready_for_review`；其后被 parent 视觉检查技术拒绝，并由 rev 11 iteration 09 的 CC0 复用重定向取代（`FDB-GAC-028`）。物理手机从未 build／install／launch。**

- 技术拒绝根因四项：顶封仍读成一整块刚性盖子飘走，不是渐进 tear front；body 边缘是均匀卡通锯齿，缺厚度、内侧、折叠张力与接触阴影；袋内小盒变成全尺寸盒存在视觉断裂，连续性是模拟而非真实；背景与 impact 语言浑浊无力，整体像技术 demo 而非高级 gacha 序列。
- rev 9 全部 artifact、hash、录屏与逐帧图保持 immutable rejected history，不得恢复为当前要求，也不得再送审批。rejection event=`794facd7-3c15-4c6c-bc32-4617cf4de882`；原 ready event=`53979405-e1c6-4cd5-b132-b1e25eaf1474`。
- DecisionState：`Technically Rejected / Superseded by FDB-GAC-028`。DeliveryState：`Immutable Rejected Evidence`。

<details>
<summary>历史 rev 9 原始条目（保留原文）</summary>

> **历史状态：pipeline rev=`84`。Gate 01–03=`approved`；Gate 04 rev 9=`ready_for_review`；Gate 05–12=`stale`；approved count=`3/12`；`shippingReady=false`。物理 iPhone／Android 未 build／install／launch。**

- 用户连续两次以原文“纯纯垃圾。”明确拒绝 rev 8。pipeline rev 83 / event=`f32ea87c-9bc2-4911-b796-dfe6e72e4fee` 记录 `rejectionCount=2` 与两个 exact quote；rev 8 全部 artifact/hash 保持 immutable rejected history。
- rev 8 根因固定为五项：Pack 变成噪点／dither 矩形；impact 是长时间平面淡紫洗屏与通用同心环；“九层同时运动”代替了视觉层级；白帧后盒体 hard pop；整体像 debug/procedural placeholder，不是 shipping animation。
- 当前实际 Unity：`Assets/_DisplayCase/Candidates/PackOpeningGate04R009/Scenes/PackOpeningGate04R009.unity` 在 Unity `6000.5.6f1` + URP `17.5.0` PlayMode 运行。`PackOpeningGate04R009Controller`、profile、三个 URP shader、三个 Shuriken system、真实场景和 Camera capture 均已生成；没有 Python／PIL／Canvas／ffmpeg frame synthesis、VFX Graph、PrimeTween 或 DOTween。
- 当前仍是 candidate：代码、场景、材质、mesh、profile 与 review media 全在 immutable Gate 04 rev 9 candidate/evidence 路径。未接 shipping prefab／coordinator／native UI；CTA、四 rarity tier、receipt、award、ACK、skip 与产品发布路径未改。
- 源素材：Standard Pack body／flap 使用原始 `384×512` canvas，SHA-256=`ebc17bb2…4681d6 / b031fc5c…b33d49`。真实 assembled case prefab SHA-256=`7a96aae6…c6a67e2c`；真实 caller-owned `ThreeBladeDisplayPrize` SHA-256=`d68f51b0…9395a8e1`，toy geometry/material/art/pivot/physics/Haptics/mechanism 均未编辑。
- 撕裂：top-trailing 接触点沿封边从右向左推进；front 前方保持连接。连续 foil mesh 按列产生 bend/curl/fold highlight；`650–950 ms` resistance 后用 `950–1000 ms` 的 `50 ms` snap，再到 `1750 ms` 完成。body shader 从 torn edge 形成有厚度的非规则开口与 coherent retreat，不使用 noise dissolve 或 opacity crossfade。
- Impact：`1750–1930 ms` 固定 `180 ms`。能量从开口内产生；近白 flash 只占 Unity frame `105 / 1750 ms`，随后立即清除。产品后方只有一枚细、快 shockwave；Shuriken 只发少量三角 foil shard、warm glint 与定向 violet streak。无紫雾、full-screen lavender fill、ring stack、starfield、随机 confetti、Bloom、CA 或 lens distortion。
- 连续性：dark mineral environment 从 frame 0 预载。开口先露环境深度，真实盒在 `1480 ms` 已从同 aperture 进入，Pack 在 `1600–2180 ms` 从 torn edge 退场；两者只做遮挡 handoff。每帧保留 Pack 或 whole-case hero；无 black frame、blank white frame 或 case replacement。
- Reveal：同一 assembled case 只做一次约 `-25°→0°` settle；release 快、deceleration 受控，`2420 ms` 到 authored pose。case sweep 只在 `1930–2140 ms` 出现一次。相机只有 anticipation push、短 impact kick 与立即恢复；没有持续 shake 或 back-facing turntable。
- Reduce Motion／Sensory Effects 保持相同撕裂→impact→reveal 因果；关闭 kick、shockwave、streak/particle，缩小单帧 flash 并缩短 case rotation。Haptic 只定义 `TearResistance / TearSnap / Impact / CaseSettled` semantic event；没有 raw `IosHaptics` 或 native bridge 调用。
- 真实 Unity capture：normal=`gate04-r009-full-signature-60fps.mp4`，H.264 `804×1748 / 60 fps / 186 frames / 3.10 s`；tear close-up=`gate04-r009-tear-closeup-quarter-speed.mp4`，`15 fps / 67 frames / 4.466667 s`；impact close-up=`gate04-r009-impact-1700-1950ms-quarter-speed.mp4`，`15 fps / 16 frames / 1.066667 s`。ffmpeg 只编码并用 ffprobe 测量 Unity PNG。
- 联系表：`tear-silhouette-contact-sheet.png` 使用 Unity frames `39/54/57/58/60/75/90/104`；`impact-continuity-contact-sheet.png` 使用 `102/104/105/106/108/111/114/117`。每格由 Unity compositor 写入真实 `F### / T####MS`，画面无 debug layer-count bar。
- 自检：`35/35` 架构／来源／视觉禁用项通过。单帧 flash=`1`；flash 后 maximum white fraction=`0.005439`；maximum lavender fraction=`0.001360`；minimum hero fraction after flash=`0.921946`；maximum consecutive case-entry step=`0.075797`。这些数值只作证据，不替代视觉判断。
- 验证：focused Unity EditMode=`18/18 pass`；capture report=`pass`；三段视频 metadata 与 source frame count 精确匹配；Premium Display Case validator 与 all-pipeline validator 均为 errors／missing／unhashed=`0/0/0`。Model Provenance Explorer 全量为 `180/183`；两项失败仍断言旧 Gate 04／Gate 12 状态，一项读取并发 magnetic-slide 旧 snapshot，未修改该并发 test 文件。rev 9 ready event=`53979405-e1c6-4cd5-b132-b1e25eaf1474`。
- 下一门禁：用户先评审真实 Unity normal/slow-motion media。只有 Gate 04 rev 9 获得明确视觉批准后，才能处理最早 stale Gate 05；当前不进入 CTA、四 rarity tier、shipping wiring 或物理手机。

</details>

## 历史：2026-08-28 Pack Opening Gate 04 rev 8 已明确拒绝

> **历史状态：pipeline rev=`82` 时 Gate 04 rev 8=`ready_for_review`；rev 83 已保存两次 exact rejection，rev 84 已以真实 Unity rev 9 取代当前候选。物理手机从未 build／install／launch。**

- rev 8 的 `720×1280 / 60 fps / 186 frames` 录屏由 `generate_epic_timing_prototype.py` 离线合成；它不是实际运行的 Unity scene/Game view。
- `candidate-texture-manifest.json` 的 noise dissolve、rarity ramp、soft-disc particle、radial line 与 shockwave 素材全部保持 `finalMaterialDelivery=false`，不得进入 rev 9 或 shipping。
- 原 `13/13` EditMode 只验证 timing profile，不证明视觉质量。“九层同时运动”与 signalstats 是已否决 measurement，不得恢复为完成标准。
- DecisionState：`Rejected Twice / Superseded by Gate 04 Rev 9`。DeliveryState：`Immutable Rejected Evidence`。

## 历史：2026-08-28 Premium Display Case Gate 12 rev 4 已拒绝

> **历史状态：pipeline rev=`80` 时 Gate 01–11=`approved`，Gate 12 rev 4=`ready_for_review`。pipeline rev 81 已将该候选记录为 rejected/superseded history。物理 iPhone 从未 build／install／launch。**

- 用户拒绝 rev 3 的精确选择为 Pack tear“撕包仍然有问题”、light“仍然太弱”、gacha energy“仍需加强蓄力与冲击”；rejection event=`580beed5-ae76-41e0-b800-601cf505bb93`。rev 1–3 全部证据保留；Gate 01–11 未失效。
- rev 3 根因：整条 seal 以刚性 lid 方式竖移；cut seam 与锚点路径不匹配；合成 contact label 比首个真实变化早 `0.203 s`；commit 时 opacity＋裁切只剩 partial flap 面积 `4.4%`。arrival 是透明 wash，rotation rim 是静态 virtual-light；无 release pulse；sheen 对 hold mean absolute=`7.84/255`。
- Pack rev 4：组件库 `ProductTearablePackArtwork` 使用真实 `384×512` body/flap、full-width 比例与最后可用 shipping Pack 的 `topTrailing` 变换依据。`<0.62` 有可见水平跟手、lift、3D bend、progressive opening/seam 和回弹；`≥0.62` exact-once。可见 opening 先于 case；一次 `0.18 s` neutral pulse 只在 opening/interior。
- 交接：Pack 保持前景，直到同 request receipt 与真实 case/prize/camera 连续两帧 ready。当前下退候选=`0.14 s`；transition minimum foreground fraction=`0.3853`，case-before-opening fraction=`0`，无黑／空帧或对象替换。
- 盒体 rev 4：one arrival rim、two object-bound rotation-rim passes、one crossing sheen、zero persistent light。三个 shell renderer 只使用 mesh fragment；所有 isolated cue external pixels=`0`。无 halo、rarity color、Bloom dependency、particle、VFX Graph、shake、loop、explode、assembly 或第二盒。
- 当前 timing 候选：handoff／entry／first 360／second 360／overlap／arrival／sheen／hold=`0.14/0.56/0.50/1.10/0.18/0.28/0.34/0.62 s`；profile=`2.94 s`。两圈平均=`720/327.27°/s`，速度比=`2.2×`；边界前后保持正角速度，无 hard stop。全部仍可编辑，未锁定为获批视觉值。
- Pack 视觉测量：full-width fraction=`0.9361`，partial flap horizontal travel=`146.75 px`，partial／commit opening gap=`13/105 px`，rebound MAD=`0.948/255`；seam p95−median=`166/255`，release mean／p95 delta=`105.32/123/255`。
- 盒体 isolated GPU cue mean delta：arrival／first rim／second rim／sheen=`8.13/13.39/9.23/18.16/255`；p95=`20.07/36.77/25.35/173.94/255`。实际成片 final sheen 对 hold mean absolute=`39.92/255`、p95=`161/255`；hold 后 residual mean／p95=`1.17/5/255`。
- 回归：Unity EditMode=`53/53`；Swift exact-once/rules=`42/42`；六份 touched shipping Swift 通过 `arm64-apple-ios15.0-simulator -warnings-as-errors -typecheck`。全局 Xcode `-Werror` 会把 Unity 6000.5 自动生成 umbrella header 的四项非模块化 warning 升级为错误，因此只对 touched Swift 严格门禁；canonical Release Simulator Xcode 正常构建=`BUILD SUCCEEDED`。
- 来源：只继续已批准的 `MakeItShineCc0EffectCurves.cs`、`MakeItShineCc0Masks.hlsl`、contract 与 notice；source commit=`88842be0063b5b0b75e82ed6572752a37a13c82b`。外部 FBX/prefab/Timeline/VFX/three-card/sample material 仍未导入。
- 证据：`ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/rev-004/app-simulator-pack-to-case-r4.mp4` 为 H.264 `1206×2622 / 60 fps / 339 frames / 5.65 s`。同目录 `app-simulator-contact-sheet.png`、`pack-tear-rebound-contact-sheet.png`、`pack-seam-release-contact-sheet.png`、`case-cue-contact-sheet.png`、`standard-views-contact-sheet.png` 与 `visual-regression-report.json` 提供标签和阈值。ready event=`efb848ba-7aac-4707-8902-0dd14bcb525d`。
- DecisionState：whole-case、因果接力、exact-once、有限 mesh-clipped cue 与全部禁止项保持 locked；rev 4 timing/light amplitude 为 `Decision Pending`。DeliveryState：`Integrated & Tested · Release Simulator Rev 4 Ready for Review`；不是 physical-phone `Installed` 或 `Device Accepted`。

## 历史：2026-08-27 Premium Display Case Gate 12 rev 3 已拒绝

> **历史状态：pipeline rev=`78` 时 Gate 12 rev 3=`ready_for_review`。用户随后以三项精确选择拒绝该轮；pipeline rev=`79` 将其保存为 rejected history。物理 iPhone 未 build／install／launch。**

- 用户反馈：精确保留“光效在哪里啊，完全没有实现啊，然后pack撕开的效果又坏了”。rev 2 rejection 和全部证据保持 immutable history；rev 3 event=`651f8bed-ae06-4bca-93f3-8c63b81c8384`。这是 Gate 12 implementation defect revision，不改变 Gates 01–11。
- 光效根因：rev 2 测试只验证 source 曲线非零和 shader 文本存在，未验证 prefab renderer、material property、MaterialPropertyBlock 或真实 GPU 像素。`FidgetingCc0DiagonalBand` 又做一次 reveal threshold，透明 alpha 再压低 `0.10` arrival 与 `0.18` sheen，最终几乎不可见；两圈也没有独立 `_RotationRimStrength`。
- Pack 根因：真实 flap 是 `400×512` 透明 canvas，却被放进 `238×82` frame，实际撕条被缩窄；body 没有随 progress 打开的遮罩，也没有 seam light。Rive 只负责选择反馈，不是撕包层。
- Runtime 修复：`PremiumDisplayCaseGate12R003` 使用三个真实 shell renderer；profile/runtime/shader 共同验证 CC0 曲线、property support 和 MPB 写入。arrival=`0.68`、rotation rim=`0.52`、sheen width/intensity/falloff=`0.10/0.78/0.42`；GPU 回归要求三类盒体 cue 都产生可读差值且 case fragment 外变化像素=`0`。无 Point Light、Bloom、particle、VFX Graph、rarity flash、shake、外扩 halo 或 loop。
- Pack 修复：业务 View 只组合组件库 `ProductTearablePackArtwork`。同 tier body/flap 使用同一 `238×350` canvas；`<0.62` flap/opening/seam 连续跟手并回弹，`≥0.62` exact-once commit。receipt 等待时 seam 不常亮；真实 case/prize/camera 连续两帧 ready 后，Pack 才按 `0.18 s` 下退并启动同 request Unity reveal。
- 节奏未改：handoff `0.18 s`、entry `0.82 s`、第一圈 `360° / 0.72 s`、第二圈 `360° / 1.18 s`、overlap `0.22 s`、sheen `0.42 s`、hold `0.68 s`、Y `-0.18 m`、camera-depth Z `0.11 m`、profile `3.60 s`。两圈边界角速度连续；第一／第二圈平均=`500 / 305.08°/s`。这些值与新光强都仍待视觉批准。
- 回归：相关 Unity EditMode=`53/53`；其中真实 GPU arrival／rotation-rim／sheen 可见性与 fragment 外 `0 px`、module/prefab/material wiring、Pack source/mask、premature dismissal、no-empty-frame、same-instance、Reduce Motion、中断恢复和 stale request 全部通过。Swift gate=`37/37`；六份 touched shipping Swift `arm64-apple-ios15.0-simulator -warnings-as-errors -typecheck` 通过。Model Provenance Explorer=`165/165`；all/model pipeline validators errors／missingFiles／unhashed=`0/0/0`。
- Release Simulator：canonical bundle=`com.jiaweizhou.fidgetspinner.codex`，`development=false`，Xcode=`BUILD SUCCEEDED`。R003 prefab SHA-256=`ca7d6d1f…6919c`，profile=`75536764…8378`，shader=`40a4d225…023c`，Gate 10 FBX 仍为 `21c9db68…47ae`。外部 CC0 源 commit 及三份 source hash 匹配；excluded FBX/prefab/Timeline/VFX/three-card assets 仍为 `0` 导入。
- 证据：连续视频=`ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/rev-003/app-simulator-pack-to-case-r3.mp4`，H.264 `1206×2622 / 60 fps / 504 frames / 8.4 s`，SHA-256=`1153f2d4…39c3`，无空帧。总联系表=`app-simulator-contact-sheet.png`；Pack 近景=`pack-tear-contact-sheet.png`；光效近景=`light-closeup-contact-sheet.png`；标准视角=`standard-views-contact-sheet.png`。完整 hash 见 `asset-hash-manifest.json` 与 `gate12-evidence-report.json`。
- 历史 DecisionState：whole-case、两圈、因果接力与零外扩 halo 边界继续有效；rev 3 tear/light/energy visual 已拒绝。DeliveryState：`Integrated & Tested Simulator Candidate · Rejected for Shipping Visual`；不是 physical-phone `Installed` 或 `Device Accepted`。

## 历史：2026-08-27 Premium Display Case Gate 12 rev 2 已拒绝

> **历史状态：pipeline rev=`77`。Gate 12 rev 2=`rejected / revision-requested`。后续具体缺陷反馈与 rev 3 已替代“等待具体反馈”状态；本节只保留 rev 2 快照。物理 iPhone 从未 build／install／launch。**

- 拒绝事件：workflow event=`decc3d37-68df-40fc-bc6c-3c0f9e472566`，用户原话为“节奏或光效仍需修改”。后续问卷被取消；事件明确记录 `parameterAttribution=unspecified-do-not-infer` 与 `nextState=awaiting-specific-user-feedback`。不得判断是哪一项 timing/light 参数有误。
- 影响范围：最早受影响门禁仍为 Gate 04 presentation architecture。Gate 05–11 的 geometry、material、lighting、environment、export、FBX 与 Unity parity 均未改变，继续有效。Gate 12 rev 1 approval event=`8754e752-90ca-4b53-b4ff-0df6bbdae478` 及原证据保留为 superseded history。
- 被拒绝的 rev 2 快照：handoff `0.18 s`、entry `0.82 s`、第一圈 `360° / 0.72 s`、第二圈 `360° / 1.18 s`、entry/first-spin overlap `0.22 s`、sheen `0.42 s`、hold `0.68 s`、Y `-0.18 m`、camera-depth Z `0.11 m`。profile 总长=`3.60 s`；第一／第二圈平均角速度=`500 / 305.08°/s`。这些值只用于保存 rev 2 历史，不是获批默认值。
- 交接：receipt、same-request、stale rejection、interruption restore、exact-once ACK 和真实 case／prize／camera 连续两帧 ready 不变。两帧 ready 后，Unity 把 profile 的 handoff 时长传给 Swift；Swift 开始隐包时再以同 request exact-once 调用 `StartGachaRevealFromNativeUi`。这避免 Swift MainActor 调度让 Pack 遮住前半段 Unity 动画。
- CC0 提取：源固定为 `remi-chapelain/Unite2025-MakeItShine-Release@88842be0063b5b0b75e82ed6572752a37a13c82b`，license=`CC0-1.0`。模块 `Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/` 只含 `MakeItShineCc0EffectCurves.cs`、`MakeItShineCc0Masks.hlsl`、`SOURCE_CONTRACT.json` 与 `CC0-NOTICE.md`。提取内容仅为 `Booster_Discarded.anim` dissolve 曲线、`SG_Title_Kyle` Sphere Mask 思路和 `SG_LightingStrike._Reveal` 数学。
- 排除项：未导入 Booster/Card FBX、Pack/Card prefab、三卡布局、品牌 artwork、完整 Timeline、sample material、fracture/explosion、VFX Graph、Cinemachine、额外 mask camera、RenderTexture 或 particle。光效只由 MaterialPropertyBlock 驱动 object-local mesh mask；outside-mesh pixels／Point Light／full-screen flash／rarity cue／persistent loop=`0`。
- Runtime／场景：代码中仍保留 `Assets/Resources/Gacha/PremiumDisplayCaseGate12R002/PresentationRoot.prefab` 与 `PremiumDisplayCaseGate12R002Profile.asset`，但该组合已被拒绝为当前 shipping 视觉。本次只持久化决定；未改 runtime、未回退参数、未生成 rev 3。盒体、真实三叶奖品、标签内容、静态相机／背景和 Gate 10 FBX SHA-256=`21c9db68…47ae` 未变。
- 自动验证：相关 Unity EditMode=`50/50`，包含 Reduce Motion 因果静态路径；Swift exact-once gate=`25/25`；十份 shipping Swift `arm64-apple-ios15.0-simulator -warnings-as-errors -typecheck` 通过；Xcode Release Simulator=`BUILD SUCCEEDED`。evidence validator=`20/20 checks pass`；source commit／三份原文件 SHA-256／excluded-assets contract 均通过；Premium Display Case model validator=`11/12`、errors／missingFiles／unhashed=`0/0/0`。validation refresh event=`5ee11660-92a8-4141-b9ce-bc2015e9c9cf`；六张 Unity motion samples registration event=`341c1adc-7778-4a6b-90db-48ec8f249374`。
- Simulator：canonical bundle=`com.jiaweizhou.fidgetspinner.codex` 曾仅安装并启动于 iPhone 17 Pro Simulator。rev 2 评审视频与联系表继续作为 rejected revision 证据保存在 `evidence/12-shipping/rev-002/`。本次未重新构建或启动 Simulator。
- 工具验证：Gate 12 rev 2 current-state + rejection workflow focused Node=`2/2`；Premium Display Case model validator rev=`77`、approved=`11/12`、earliest=`12-shipping rejected`、errors／missingFiles／unhashed=`0/0/0`；all-pipeline validator 对全部模型均为零 schema、missing-file 或 unhashed 错误。全 Model Provenance Explorer=`151/160`；`9` 项既有失败均来自并发 Magnetic Slide 已推进到 rev `197`，而旧测试仍期待较早 `ready_for_review` 状态。本任务未改该 feature。
- DecisionState：whole-case、mesh-clipped、no-external-entity 和因果接力边界继续锁定；Gate 12 rev 2 visual=`Rejected / Revision Requested`。拒绝原因只记录为“节奏或光效仍需修改”，未归因到具体参数。DeliveryState：`Integrated & Tested Simulator Candidate · Rejected for Shipping Visual · Awaiting Specific User Feedback`；不是 physical-phone `Installed` 或 `Device Accepted`。

## 历史：2026-08-27 Premium Display Case Gate 12 rev 1 视觉批准

> **历史状态：pipeline rev=`73`。Gate 01–12=`approved`；`shippingReady=true`。该视觉随后被 rev 2 节奏请求替代；批准事件与证据保留，但不再代表当前 shipping 视觉。物理 iPhone 从未 build／install／launch，Device Accepted pending。**

- Gate 11：用户选择“一致，批准并生成 App 预览（推荐）”，approval event=`c14b967f-6399-4cff-8baa-78a0eb6169dc`。Gate 10 FBX SHA-256=`21c9db68723f0006d7c6bfec5280cafe55c16cf5392ff97c365c966e91f847ae` 继续是 Unity authority。
- Gate 12：ready event=`ec5f162a-ebbe-4c33-aa4c-d485044c95a3`；approval event=`8754e752-90ca-4b53-b4ff-0df6bbdae478`。用户原话“视觉批准，但暂不推手机（推荐）”已通过 workflow 持久化。canonical App 使用 `Assets/Resources/Gacha/PremiumDisplayCaseGate12R001/PresentationRoot.prefab`；旧 `Assets/Resources/Gacha/PremiumDisplayCase.prefab` 保留为 rollback。
- Runtime：`GachaShippingRevealDirector` 保持同一 assembled case 和 caller-owned Toy；`FidgetAppCoordinator` 在真实 case／prize／camera 连续两个 `WaitForEndOfFrame` 后才交接。durable receipt、same-request gate、stale rejection、exact-once ACK 与 interruption restore 保留。
- 动效：`PremiumDisplayCaseGate12R001Profile` 是可调 ScriptableObject + AnimationCurve。获批 rev 1 视觉快照为 entry `1.30 s`、rotation `2.10 s`、overlap `0.28 s`、sheen `0.58 s`、hold `0.90 s`、Y `-0.22 m`、camera-depth Z `0.16 m`、local-Y `360°`、sheen `0.055/0.20/0.34`。这些值只随当前 shipping 视觉修订获批；未来 tuning 必须形成新修订并重新审批。
- 光效：Gate 12 shader 按每个 mesh 的 object-local bounds 归一化，使用 MaterialPropertyBlock 驱动一次有限 sheen。Point Light、外部 halo、Bloom、粒子、VFX Graph 与持续循环均为 `0`。
- 标签：产品名、edition／finish、acquired date、rarity／level 与 `FDT-*` collectible ID 来自 catalog、progression 和 durable pending receipt；shipping preview 无 placeholder 文字。结果 UI 只组合 `ProductScreenHeading`、`ProductStatusTag`、`ProductBottomActionDock` 与唯一 `ProductPrimaryActionButton("收下")`。
- 自动验证：focused Unity EditMode=`63/63`；Swift gate harness=`23/23`；shipping Swift `-warnings-as-errors -typecheck` 通过；Xcode Release Simulator=`BUILD SUCCEEDED`；evidence validator=`pass`；model validator rev `73`、errors／missingFiles／unhashed=`0/0/0`。
- Simulator：bundle=`com.jiaweizhou.fidgetspinner.codex`，只安装／启动于 iPhone 17 Pro Simulator。preview token 只为 Simulator 提供一张真实 durable draw；receipt、ownership 与 ACK 仍走生产事务代码。它不是 StoreKit sandbox purchase，也不证明 iPhone 性能、Haptic 或 Device Accepted。
- 证据：完整 App Simulator 录屏、handoff／standard 联系表、Phone 与原始 Gate 12 报告继续保存在 `ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/rev-001/`。rev 1 已是 superseded history，不再复制到当前 DesignBible approved asset set。
- 当时验证：Model Provenance Explorer=`144/144`；Premium Display Case model validator=`12/12`、`shippingReady=true`；全 pipeline validator 的 schema／missing file／unhashed 均为 `0`。这些数值只描述 rev 73 历史快照。
- 历史 DecisionState：Gate 11 parity=`Approved`；Gate 12 rev 1 visual=`Approved then superseded`。DeliveryState 不是 physical-phone `Installed` 或 `Device Accepted`。

## 2026-08-27 环境光与陀螺仪响应收束到中间档

> **当前状态：`FDB-SCN-011`。用户要求按 GitHub 产品灯光／reference-calibration 流程实测。Canyon 静止态现使用中性顶光、低能量岩壁反弹和低频环境反射；已移除无对应光源的前缘白色三角亮点及 2D glow。视觉批准待确认，未推送手机。Device Accepted 仍为 pending。**

- 推牌 `M_EDC_Meshy_URP_Lit` 打开实时高光；环境反射保持开启。原先 `_SPECULARHIGHLIGHTS_OFF` 让陀螺仪 view-highlight 无法在金属上移动。Library 灯光尺度 `0.20→0.48`。
- 扇牌 Satin／Gunmetal／Chrome 增加 `_ADDITIONAL_LIGHTS` 与 cubemap 采样，固定 studio 假光减弱。
- 转子：ambient 去饱和保留亮度、环境染色 `0.34→0.14`、亮金属 albedo 缩放 `0.68→0.90`，高光偏中性白。未改转子 `SoftBrightMetalAlbedoScale` 或 `EnvironmentColorCoupling`。
- 扇牌库页几乎正对扇面，旧反射 `0.28 × 0.40` 加恒定 fill 让银面像贴图。扇牌反射 `0.42`、库页反射尺度 `0.80`、库页灯光 `0.70`。Editor PC 为 Forward+，扇牌 shader 含 `_CLUSTER_LIGHT_LOOP`。几何与珠喷 smoothness `0.24` 未改。
- 扇牌峡谷侧向耦合（2026-08-28 早，已否决）：Satin 曾加 `satinBand`，主光对准视口 `(0.72, 0.82)`，接触阴影偏到 `0.412`，背景 glow radius `0.24`／intensity `0.42`，前景左右墙 glow `0.32`。用户否决后不再作为当前方向。
- 扇牌峡谷首轮顶光（2026-08-28，已被 audit r001 替代）：去掉 `satinBand`，但仍保留石台点光；其前缘白三角在用户截图中被识别为无来源高光。
- GPU Editor 捕获（无 `-nographics`，`CaptureFanCardAppScene` 后 `ApplyTheme(CanyonId)`，Unity `6000.5.6f1`，双 `SubmitRenderRequest`，mtime 2026-08-28 10:37）。路径：`Artifacts/EnvironmentIntegration/magnetic-fan-card-canyon-library.png`（1,798,102）、`magnetic-fan-card-canyon-detail.png`（1,733,912）、`magnetic-fan-card-canyon-library-ibl-left.png`（1,797,666）、`magnetic-fan-card-canyon-library-ibl-right.png`（1,796,481）、`magnetic-fan-card-canyon-detail-ibl-left.png`（1,736,837）、`magnetic-fan-card-shipping-scene-sheet.png`（1,587,216）。视觉批准待确认，未推送手机。Device Accepted 仍为 pending。
- 定向 EditMode：`25` 例中 `24` 通过，报告 `Logs/FanCardCanyonTopKeyTests.xml`。唯一失败为既有 `ShippingGeometryPassesTheFrozenStructuralGate`（BottomCard／MiddleCard watertight degenerate=1512），本轮未改几何。`ShippingMaterialsUseIndependentBeadBlastedMetalAndReadableFaceMarks` 与 `SoftLightingPolicy` 通过。
- GitHub 方法实测（2026-08-28）：使用 [RobLe3/cc-blender-skill](https://github.com/RobLe3/cc-blender-skill) 的 `blender-lighting`／`reference-look-calibration` 原则，但没有导入 Blender 脚本。先拆分 key、fill、环境反射、相机侧点光、石台点光和 2D glow，再以真实 Unity 静帧比较。
- 光源隔离证据：关顶光、关反射、关岩壁反弹和关背景后，白三角仍在；全部灯光关闭时消失；只开 `SpinnerModelColorBounce` 时复现。因此它来自石台位置的 Unity 点光，不是背景、顶光或 cubemap。扇牌现禁用 `SpinnerModelColorBounce` 与 `SpinnerViewResponsiveHighlight`；姿态只以 `0.10 / 0.07 rad` 小幅旋转低频 reflection sample，不改 albedo。
- 当前静止 rig：`CanyonTopKey`=`(0.92,0.95,1.00) @ 0.92`、`CanyonRockBounce`=`(1.00,0.82,0.64) @ 0.18`；`FanCardReflectionBaseScale=0.72`、peak=`0.58`、key/fill=`0.14/0.06`，不使用合成 panel／strip、前景／背景 glow 或 camera-side fill。Satin 保持 smoothness=`0.24`；直接高光=`0.22`、环境高光=`0.42` 上限。接触阴影仅保留小范围 `0.46` 遮罩。转子未改。
- GPU Editor captures（无 `-nographics`，Canyon `ApplyTheme`，双 `SubmitRenderRequest`，mtime 2026-08-28 16:10）：`Artifacts/EnvironmentIntegration/magnetic-fan-card-canyon-toplight-audit-r002-library.png`（1,796,074 B）、`...-detail.png`（1,731,887 B）、`...-sheet.png`（1,002,214 B）。三角和前景色洗已消失；Canyon 仍是 2.5D unlit plate，静帧不能证明真实体积遮挡或陀螺仪效果。
- 验证：source/full guardrail=`ALL PASS (7.590 mm)`；`FanCardAcceptanceTests`=`22/23`。已改光相关的 materials、shader、scene tests 均通过；仅既有 `ShippingGeometryPassesTheFrozenStructuralGate` 失败（3 张牌各 `degenerate=1512`），本轮未改几何。`ArtSource/ModelPipeline/.../10-export/rev-003/magnetic-fan-card.fbx` 缺失，故完整 `BuildScene()` 无法重建权威 FBX；本轮只对已导入的 shipping scene 应用灯光迁移，未将其报为几何重建或可推机。

## 2026-08-28 扇牌峡谷顶光 audit r008 多光源重排

> **当前状态：`FDB-SCN-011`。顶光改为离轴上左方向，加入三向可解释光源（顶光／冷天光／暖岩壁反弹）。视觉批准待确认，未推送手机。Device Accepted 仍为 pending。**

- 问题：r002 之前顶光 yaw span 只有 `8°`，且 `FanCardVisibleKeyViewportX=0.50`，实际 yaw=`0°`。顶光几乎正对镜头轴，银面上既无方向性高光带，也无与之对应的可见投影方向。用户反馈“完全看不出来有顶光”由此而来。
- 本轮 rig（`ApplyCanyonTopLightRig`，未调用 `BuildScene`，未重建几何）：
  - `CanyonTopKey`：Directional，`(0.95,0.97,1.00)`，intensity `1.10→1.55`，rotation `Euler(57.6, 19.2, 0)`（`FanCardKeyPitchMin/Max=52/58`、`FanCardKeyYawSpan=8→60`、`FanCardVisibleKeyViewportX=0.50→0.34`）。Soft shadow 保留。
  - `CanyonSkyFill`：Directional，`(0.62,0.74,1.00)`，intensity `0.20→0.34`，rotation `Euler(72, -60, 0)`（`FanCardSkyFillPitch=58→72`、`FanCardSkyFillYaw=-24→-60`）。
  - `CanyonRockBounce`：Directional，`(1.00,0.82,0.64)`，intensity `0.14→0.18`，rotation `Euler(45.6, -84.8, 0)`。yaw 偏移由 `+168°` 改为 `-104°`，让暖反弹从顶光对侧进入正面，而不是打在卡背形成 rim。
  - `CanyonApertureTopLight`：Spot，`0.04` 保持不变。r001 隔离对比（`0.04/0.08/0.12`）显示它只整体抬亮、不产生方向性顶光读数，提高只会让银面更平，因此不上调。
  - `SoftFrontLift` 保持 `0` 并 disabled；`SpinnerViewResponsiveHighlight` 与 `SpinnerModelColorBounce` 在扇牌路径继续禁用。
- Satin shader：`_Smoothness` 仍为 `0.24`，albedo 未改。降低平坦底光 `ambientIrradiance 0.68→0.46`、`hemisphere 0.16→0.17`；宽 lobe 改 `lerp(2.0, 9.0, _Smoothness)` 系数 `lerp(0.10, 0.30, _Metallic)`；新增窄带 `bandSpecular=lerp(9.0, 34.0, _Smoothness)` 系数 `lerp(0.12, 0.62, _Metallic)` 以形成可读缎面高光带。环境高光上限 `lerp(0.12, 0.42, _Metallic)` 未改，未恢复 reflection `0.82`／SH floor／`softPanel`。
- 耦合：`FanCardEnvironmentColorCoupling 0.22→0.26`、`FanCardCubemapKeyScale 0.25→0.34`。暖冷仍只经 SH／cubemap 宽渐变进入，不做岩壁镜像反射。
- 背景 glow 仍为 `FanCardPedestalGlowIntensity=0`、`FanCardForegroundGlowIntensity=0`，前景两根近景石柱无泛光洗白。接触阴影 `FanCardContactShadowStrength=0.46`，`ResolveFanCardContactShadowCenterX(0.34, 0.94)=0.564`，随顶光偏左而向右偏移，方向与顶光一致。
- GPU Editor captures（Unity `6000.5.6f1`，无 `-nographics`，Canyon `ApplyTheme`，双 `SubmitRenderRequest`，mtime 2026-08-28 17:5x）。首次带 `-nographics` 的一轮产出 5 张完全相同的空白灰图（各 `28,214 B`，同一 SHA-256），已作废并重跑：
  - `Artifacts/EnvironmentIntegration/magnetic-fan-card-canyon-toplight-audit-r008-library.png`（1,845,501 B）
  - `...-r008-library-ibl-left.png`（1,845,565 B）
  - `...-r008-library-ibl-right.png`（1,845,725 B）
  - `...-r008-detail.png`（1,755,551 B）
  - `...-r008-detail-ibl-left.png`（1,755,611 B）
  - `...-r008-sheet.png`（1,036,221 B）
- 实际看图结论（未获批准）：库页视图现有从左上到右下的可读柔和方向性渐变，方向与顶光一致，接触阴影偏向右侧一致；三角形无源高光在五张图中均已消失；背景泛光仍限制在中央石台缝隙，未洗白近景石柱。仍不足：亮度差仍偏大，银面整体比岩石亮；detail（近乎水平小面）视图仍接近均匀，方向性读数弱；暖冷分割在银面上仍偏弱。Canyon 依旧是 2.5D unlit plate，静帧无法证明真实体积遮挡或陀螺仪响应。
- 验证：`python3 unity/FidgetingApp/ArtSource/FanCard/validate_fan_card_guardrails.py`=`ALL PASS (7.590 mm)`。`FanCardAcceptanceTests`=`22/23`，唯一失败为既有 `ShippingGeometryPassesTheFrozenStructuralGate`（BottomCard／MiddleCard／TopCard 各 `open/nonmanifold=0, degenerate=1512`），本轮未改任何 mesh asset，几何缺陷早于本轮且需 Blender 重建与缺失 FBX 才能修。
- `SpinnerEnvironmentTests`=`9/10`。已同步两处过期断言：`_ShadowStrength` 允许扇牌石台值 `FanCardContactShadowStrength`；`FanCardEnvironmentColorCoupling` 范围由 `0.34–0.50` 改为 `0.20–0.34`（旧范围属被否决的 digital-IBL 档）。剩余失败 `EveryProductSceneInstallsItsBackgroundAndHarmonizedModelLights` 断言 `_GlowScaleB.y=2.8`，而 adaptive backdrop 在 HEAD 即写入 `1.08`，属既有 adaptive-backdrop 断言漂移，与扇牌灯光无关。
- `ArtSource/ModelPipeline/magnetic-fan-card/evidence/10-export/rev-003/magnetic-fan-card.fbx` 仍缺失，`BuildScene()` 无法运行；本轮只对已导入 shipping scene 应用灯光迁移，未报为几何重建或可推机。

## 2026-08-30 扇牌峡谷 audit r009 多机位补拍

> **当前状态：用户指出 r008 只有两个真实机位，角度不足。当前 shipping Unity 场景补拍 27 张 Canyon 图后，用户以原话“通过”批准 r009 静态视觉。未构建、未安装、未推送手机；Gate 12 仍为 stale，Device Accepted 仍为 pending。**

- `FanCardSceneBuilder.CaptureFaceReflectionAngles()` 现明确应用 Canyon theme，并只在未保存的 Editor 会话内移动相机。shipping 相机、模型 Transform、材质、灯光、Collider、四档机械、音频和 Haptic 均未改。
- 核心八机位总览：`Artifacts/EnvironmentIntegration/magnetic-fan-card-canyon-multiangle-r009/r009-core-angle-sheet.png`。
- 核心原图：`fanned-overhead.png`、`fanned-hero.png`、`fanned-left-38.png`、`fanned-right-38.png`、`fanned-low-left.png`、`fanned-low-right.png`、`fanned-back.png`、`fanned-track-closeup.png`。同目录另含 high／grazing、正面局部、左右 `42°`、IBL 左右偏转及闭合状态，共 27 张。
- 逐图检查：顶视、hero、左右斜视和左右低机位均完整构图；低机位可见三片真实厚度及两道空气间隙；正面看不到背轨或背面角标。背面和轨道特写明显过暗，说明当前顶光 rig 只适合正面 shipping 构图，不能把背面图当作灯光通过证据。
- 不变门禁：轨道外轮廓净距、`3.5 mm` 单片厚度、`1.0 mm` 层间隙、共同轴心、底片固定／中顶片运动、正背面可见性和角标父子关系均未改。source-only 与 full guardrail 均为 `ALL PASS (7.590 mm)`。
- Unity `6000.5.6f1` batch capture 编译并执行成功。`FanCardAcceptanceTests`=`22/23`；唯一失败仍是既有三张 body 各 `degenerate=1512` 的 structural gate，本轮未改任何 mesh asset。
- 单模型 pipeline validator=`11/12`，Gate 12 继续为 stale。Model Provenance Explorer=`199/205`；6 项失败均指向并行中的 Magnetic Slide／Premium Display Case 状态断言，没有 Fan Card 失败。
- 2026-08-30 r009 approval：用户原话“通过”。批准总览已复制为 `Docs/DesignBibleAssets/fan-card-canyon-r009-approved.png`，SHA-256=`f7173b900cb6e238714b08468c611110511f31cf9798b16eaab4d7ab5a4297a7`；对应 `FDB-SCN-012`／`V10`。该批准仅覆盖静态视觉，不替代 Gate 12 交互证据、安装、陀螺仪或 iPhone 验收。
- iPhone Simulator：真实 App 已在 iOS `26.4` 的 iPhone 17 Pro Simulator（UDID `8E396082-0B97-4484-A30B-4DD125318319`）完成 Unity export、Xcode Release build、安装与启动。Bundle=`com.jiaweizhou.fidgetspinner.codex`，Build=`40`，manifest sdk=`SimulatorSDK`、source=`local-preview`、`physicalPhoneInstallAuthorized=false`。通过 launch arguments 进入 `magnetic-fan-card`／`canyon`；运行截图为 `Artifacts/EnvironmentIntegration/fan-card-gate12-r009-simulator-launch.png`。
- 首次 export 因磁盘仅余 `117 MB` 在 IL2CPP 阶段报 `No space left on device`。用户明确选择清理后，仅删除 5 个可重建的旧 Xcode DerivedData 缓存，释放约 `15 GB`；未删除源码、预览或 Xcode export。重跑日志 `Logs/FanCardGate12R009SimulatorExport.log` 明确为 `Build Finished, Result: Success`。
- Simulator 已打开供交互检查；用户交互验收、Core Motion 陀螺仪和物理 iPhone Device Accepted 仍未完成。

## 2026-08-28 Magnetic Slide Tile Gate 08 rev 5 端点互锁灯光复核

> **当前状态：pipeline rev=`232`。Gate 07 rev 12 已由用户以原话“继续”批准；Gate 08 rev 5=`ready_for_review`；Gate 09–12=`stale/blocked`。旧 shipping 模型仍为默认。视觉批准待确认，未推送手机。**

- 本轮直接消费 Gate 07 rev 12 blend SHA-256=`95392904…588`、geometry digest=`2fcf6d2b…1952` 和机制合同 rev 17 SHA-256=`9cd7a08f…ea571`。几何与材质快照在全部 Blender 灯光渲染前后不变。
- 灯光沿用 portable rev 4 recipe：单张 `2048×1024` scene-linear Rec.709/D65 equirectangular HDR，strength=`0.85`、rotation=`0°`、seam delta=`0`、radiance max=`5.6643`、动态范围=`5.2105 stops`。两端零 direct light、ground、probe、reflection card 和 synthetic highlight。
- Blender 与隔离 Unity URP 都输出 `1400×1100` scene-linear HDR EXR，再共同应用 `neutral-display-v1`。Unity 以 `R16G16B16A16_SFloat` 导入同一 EXR；source max=`5.6641`、cubemap max=`4.8164`。
- 必需证据包含 Hero、left/right oblique、low、Beauty、Clay、camera-space Normal、camera-space Depth 和 Roughness。完整整帧不裁切、不独立对齐：SSIM=`0.9241`、silhouette IoU=`0.8641`、MAE=`4.46/255`。
- 外观检查：Blender／Unity blood-red fraction=`18.17% / 10.61%`；dark-pattern fraction=`59.03% / 74.83%`；Unity display clipping=`0`，批准材质 emission=`0`。该跨引擎候选只验证共享 HDR 可移植性，不是 Gate 11 parity 或 shipping 资产。
- 真实 Blender 转台为 `90` 个源帧、H.264 `960×720 / 30 fps / 6.0 s`。前 15 帧只在 `θ=0°` 推至 `sMax`；60 帧只在 `sMax` 完成 `0°→360°`；最后 15 帧只在 `360°` 对齐后回推。固定轴方差=`0 mm`，pitch/roll=`0 rad`，非法中段旋转帧=`0`。
- 隔离 Unity candidate 位于 `Assets/_EDC/Candidates/MagneticSlideTileGate08R005EndpointLighting/`。shipping scene SHA 前后均为 `99083a32…850d`；未运行 Simulator、shipping build、安装或手机。
- 评审证据：`gate08-r005-endpoint-lighting-turntable.mp4`、`gate08-r005-lighting-review-board.png`、`gate08-r005-blender-unity-comparison.png`。DecisionState=`Gate 08 Review Pending`；DeliveryState=`Validated Isolated Lighting Candidate · Not Shipping · Not Device Accepted`。

## 2026-08-28 Magnetic Slide Tile Gate 07 rev 12 端点互锁材质复核

> **历史状态：Gate 06 rev 5 已由用户以原话“继续，继续”批准；Gate 07 rev 12 后由用户以原话“继续”批准，并被 Gate 08 rev 5 消费。**

- 本轮直接消费 Gate 06 rev 5 blend SHA-256=`a2aaf83a…0ef4`、geometry digest=`2fcf6d2b…1952` 和机制合同 rev 17 SHA-256=`9cd7a08f…ea571`。材质前后及全部合法姿态 geometry digest 不变。
- rev 11 四张 `620×1000` 贴图逐字节复用：upper albedo／roughness=`c0e9305d…453a5 / 854f1dbc…df6a`；lower=`968c1e87…0eb / ca269756…8245`。上／下 mask=`8250df70…1c36 / 7bf5921f…a7c2`，64 px 黑边 mask=`2179bf26…4fc`。
- 材质值保持：银边 metallic=`1`、roughness=`0.075`；晶体 IOR=`1.52`、coat=`0.48 @ 0.035`、granular=`28`、microflake=`85`；深色侧壁 metallic=`0.24`、roughness=`0.18`；全部 emission=`0`。球材料继续为 unknown。
- 当前证据只含闭合、中段 `0°`、最大打开端点 `0°/12°/36°` 和端点 12° 转台。密集状态审计=`4,359` 样本，其中中段旋转拦截=`4,000`、非零角回推拦截=`359`；固定轴方差=`0 mm`，最大槽点残差=`0.000002884 mm`，覆盖漏点／表面交叉=`0/0`。
- 真实 Blender 材质板、原图对照、晶体／图案／银边／四槽／内部近照、交互 GLB 与 24 帧 H.264 转台均已生成。交互 GLB 是主评审资产；静态图只作补充。
- DeliveryState：只完成 Gate 07 材质评审证据。未运行 Simulator、最终 Unity、Build、安装或手机；Device Accepted pending。

## 2026-08-28 Magnetic Slide Tile Gate 06 rev 5 端点互锁同源几何

> **当前状态：Gate 05 rev 12 已由用户以原话“可以，可以继续推进。”批准；Gate 06 rev 5=`ready_for_review`；Gate 07–12=`stale`。旧 shipping 模型仍为默认。视觉批准待确认，未推送手机。**

- 本轮从 Gate 05 rev 12 blend SHA-256=`f587be80…1a2` 重建几何证据，机制合同固定为 rev 17 SHA-256=`9cd7a08f…ea571`。网格未改，canonical geometry digest 仍为 `2fcf6d2b…1952`。
- 六正交、Workbench、尺寸／固定轴叠图、A–A 剖面、爆炸、四槽底面、平底凸轴近照、闭合、最大打开 `0°/12°/36°/360°` 与中段旋转禁用图均来自同一 Blender 5.2 scene。交互 GLB 为主要审批资产。
- 密集验证覆盖 `1,362` 个合法姿态、`4,000` 次中段旋转请求和 `359` 次非零角回推请求。固定轴方差=`0 mm`，最大 `M_top·q(s)=P` 残差=`0.000002884 mm`，最小重叠圆盘实际网格射线漏点=`0`，完整 360° 闭合矩阵误差≤`1e-9`。
- 六个内部件对 `BottomExterior`／`MovingTopBody` 的代表姿态 BVH 表面交叉均为 `0`。产品 renderer whitelist 仍仅含 `BottomExterior` 与 `MovingTopBody`；`MinimumOverlapDisk` 为非渲染 Empty；中段禁用图只渲染解析后的 `θ=0°` 合法姿态，不含 50% 行程旋转。
- 闭合暂定 bounds=`31×50×12 mm`；底片顶面最大偏差=`0 mm`；轴座凸出=`0.2 mm`；四槽宽度和球候选继续保持用户授权范围 `1.8–3.0 mm`／`2–3 mm`。八个核心 mesh 的 nonmanifold edge 与 invalid polygon normal 均为 `0`。
- 验证：Gate 06 定向 Node=`14/14`；全量 Node=`186/188`，两项失败均为并行 Premium Display Case 旧状态断言；model／全 pipeline errors、missingFiles、unhashed=`0/0/0`。桌面、`390×844` 移动、GLB、图片 modal、历史恢复通过，runtime／loading failure=`0/0`。标准视图 wrapper 使用 Blender bpy fallback，missing views=`0`；端点互锁视频 QuickTime 解码=`450/450`。
- DeliveryState：Gate 06 几何评审证据已生成并验证。未推进材质、Simulator、最终 Unity、Build、安装或手机。

## 2026-08-28 Magnetic Slide Tile Gate 05 rev 12 固定轴／遮挡纠正

> **当前状态：Gate 05 rev 12=`ready_for_review`；Gate 06–12=`stale`。旧 shipping 模型仍为默认。视觉批准待确认，未推送手机。**

- 用户否决 Gate 08 rev 4 Unity-only 录屏中的轴位跳变、内部件穿壳和底片顶面圆盘。两张原图按原字节归档，SHA-256=`d2222151…dfe3`、`57c1efc2…14cd`。
- 最早失效实现是 Gate 05。旧层级同时使用 `FixedAxisBoss` 与 `FixedAxis` 表达轴，产品渲染又包含内部 mesh；旧验证没有检查槽点锁轴方程。
- 修正版只有一个 pivot ID：`FixedAxis`，固定世界点 `P=(0,-9,5.875) mm`。顶片满足 `M_top=T(P)·Rz(θ)·T(-q(s))`，`q(s)=(0,-9+s,-3.1875) mm`。
- `MinimumOverlapDisk` 是半径 `15.0 mm` 的非渲染 Empty。产品 renderer whitelist 只有 `BottomExterior` 与 `MovingTopBody`；轴座、载体、followers 和球只在技术层显示。
- Blender 共验证 `13,357` 个 `s×θ` 样本：`P` 方差=`0`，最大锁轴残差=`0.000000954 mm`。五个代表姿态的真实网格表面交叉=`0`，最小覆盖圆 `64×5` 个实际顶片射线检查零漏点；底片顶面偏差=`0 mm`。
- 隔离 Unity `6000.5.6f1` 白模录屏共 `300` 帧／`10 s`。固定轴方差=`0 m`，最大槽点残差=`5.11e-9 m`，pitch／roll=`0°`；红色世界轴在全部帧的屏幕 centroid 范围=`0×0 px`。没有 final material、shipping scene、Build、安装或手机操作。
- 用户最新原话：“上片只有在推到顶部的时候，才可以进行360度旋转”。合同 rev 17 SHA-256=`9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571` 将机构改为串行状态机：`θ=0` 时直推；仅 `s=sMax` 旋转；非零角锁住行程；对齐后回推。Gate 04 rev 14 只标注端点／槽对齐，不臆造隐藏锁扣。几何未变。
- 旧 `570` 帧录屏因在 50% 行程旋转被判定为 rejected invalid evidence，只保留历史。新隔离 Unity 白模录屏为 `450` 帧／`15 s`／`1920×1080`／`30 fps`：闭合、直推、中途旋转失败、端点解锁、30 档整周、非零角回推失败、对齐后闭合均有中文标注。
- 新逐帧验证：固定轴屏幕 centroid 范围=`0×0 px`；BottomExterior／整机 transform 方差=`0`；槽点残差≤`1e-7 m`；`1000` 个 CAD 中途位置旋转均被锁定；30 档仅在 `sMax`；非零角回推和同时速度违规均为 `0`；最小圆盘漏点、相机移动、隐藏 renderer、pitch／roll 均为 `0`；整周闭合误差=`0°`，首末模型 ROI 最大像素差=`1`。ffprobe 与 macOS AVFoundation `450/450` 帧解码通过。

## 2026-08-28 Magnetic Slide Tile Gate 08 rev 4 中性跨引擎基准

> **当前状态：pipeline rev=`211`。Gate 01–07=`approved`；Gate 08 rev 4=`blocked`，等待 Unity-only PlayMode 录屏视觉确认；rev 3=`superseded history`；Gate 09–12=`stale`。视觉批准待确认，未推送手机。**

- 用户明确判定 rev 3 信息有用但视觉不可接受，禁止继续作为批准候选。rev 3 文件与哈希完整保留，只从当前评审清单移除。
- 用户否决首次补充录屏中的不可能竖直／卡片翻转。任务在编码前中断；反馈截图 SHA-256=`556c91e8…0609` 与拒绝记录只作为 internal history，未注册成批准视频。
- 修正版硬约束：底座、底轴和整机固定且 world-up；产品 pitch／roll=`0°`；顶片只沿局部槽轴平移并作 `+Z` yaw；carrier 只绕 `+Z`；相机只作 `±35°` 水平环绕，恒 elevation、zero roll、稳定 up；禁止负 scale／倒置。Blender／Unity 每帧编码前都验证这些约束。
- 新确认的传输错误：Unity 曾把线性 EXR 导入为 `R8G8B8A8_UNorm`，把 HDR `>1` 值截断；equirectangular→cubemap 还缺少 Blender `(X,Y,Z)`→Unity `(X,Z,Y)` 的完整横向符号与纵向翻转。
- rev 4 只使用一个 `2048×1024` seamless scene-linear Rec.709/D65 EXR。Unity 固定 `R16G16B16A16_SFloat`；source max=`5.664`、cubemap max=`4.816`、方向 marker 最大误差=`0.000171`、seam=`0`。
- 两端均为零 direct light、零 ground、零 contact shadow、零 reflection probe、零 SH、零 reflection card 和零 synthetic highlight。唯一环境同时提供 diffuse／glossy PBR 响应，不存在第二反射源。
- Blender 与 Unity 都输出线性 HDR EXR，再共同应用 `neutral-display-v1`：exposure multiplier=`1`、shoulder=`x/(1+0.18x)`、IEC 61966-2-1 sRGB。没有 Blender AgX 对 Unity ACES／Neutral 的混比。
- 相机固定为 `1400×1100`、76 mm、36 mm 横向 sensor、同一 transform。五组 A/B 为 reflection sphere/strip、无地面 clay、silver、blood-red crystal 和 full model；每格保留原始整帧，无 crop／resize／post-align，背景像素完全一致。
- 指标：silver SSIM=`0.9890`、DeltaE76 median=`2.24`、heatmap >24=`0.20%`；crystal SSIM=`0.9563`、median=`11.0`；full-model SSIM=`0.9510`、MAE=`2.54`、heatmap >24=`4.56%`、median=`12.04`。display clipping：full Blender=`0.279%`、Unity=`0.278%`。
- 人工并排检查确认 rev 3 的整体过暗、背景／接触阴影和重复高光失败已移除；亮银、深血红与黑纹可读。该判断仅允许发起 Gate 08 复审，不等于用户批准。
- 修正版录屏：`gate08-r004-synchronized-portable-parity.mp4`，H.264 High／yuv420p、`2800×1180`、`30 fps`、`12.0 s`、`360` frames、fast-start。165 对渲染帧 silhouette IoU 最低=`0.999902`，centroid delta 最大=`0.019 px`；`180/180` source frames 通过 transform validator。
- Unity-only 补充录屏：`unity-playmode-preview/gate08-r004-unity-playmode-runtime.mp4`。Unity `6000.5.6f1`、URP `Mobile_RPAsset`、隔离 PlayMode scene `MagneticSlideTileUnityOnlyPlayModePreview.unity`、Camera `CAM_Gate08R004NeutralParity`；使用四轨 FBX `d15e5c94…2179`、geometry digest `e2a838c2…02fe` 和共享 HDR EXR `e0a2d012…3d90`。H.264 High／yuv420p=`1920×1080`、`30 fps`、`15.0 s`、`450` frames；画面内标注 `Unity URP PlayMode · 不是 iPhone Build`。
- Unity-only 验证：`450/450` 帧通过固定底座／固定轴、无整机 pitch-roll／翻转、合法直推／12°／36°、正 scale 与 camera roll=`0`。Blender frame=`0`、offline composite=`0`；非切点相邻帧最大 MAE=`2.492`。ffprobe、macOS AVFoundation、Spotlight metadata、桌面和 `390×844` 移动浏览器播放均为 `15.0 s / 1920×1080 / 30 fps`，runtime/loading failure=`0/0`。
- 验证：`MagneticSlideTileNeutralParityTests`=`4/4 passed`；Gate 08 focused Node=`2/2`；pipeline validator 对 magnetic-slide-tile 为 revision `211`、errors／missing／unhashed=`0/0/0`；全 Node suite=`174/174 passed`。
- 当前评审证据：Unity-only PlayMode 录屏与 poster、修正版同步录屏、`gate08-r004-neutral-parity-board.png`、Blender／Unity full frame；旧 `gate08-r004-neutral-parity-review.mp4` 保留但不再是当前录屏入口。审计为 `neutral-parity-audit.json`。
- 未修改 `Assets/_EDC/Scenes/MeshyEDC.unity`，未推进 Gate 09／11／12，未 promotion、build、install、launch 或 phone。Device Accepted pending。

## 2026-08-28 Magnetic Slide Tile Gate 08 rev 3 跨引擎灯光可移植性纠正（已被 rev 4 取代）

> **历史状态：pipeline rev=`207`。用户已明确判定该轮视觉不可接受；只保留为 superseded history，不得再请求批准。**

- 最早根因在 Gate 08：rev 2 使用四个 `18–32 mm`、`16–50 kW` Blender AREA 灯和四张隐藏 reflection card。它们定义的高光形状、面积和功率没有移动 URP 的直接映射。
- Gate 09 rev 8 的获批 EXR 经 Blender 5.2 重读确认 RGB 全零，仅 alpha=`1`。旧 metadata 声称的亮度范围来自生成数组，不是写盘后像素。Gate 11 因此用 global cubemap、local probe、analytic panel 和 world-space broad-softbox 重造高光，又与 direct specular 重叠。
- 色彩链也未落地：Gate 09 只计划在 ACES 失败后拟合 AgX LUT；Gate 11 rev 10 直接使用 ACES，未生成或应用 LUT。Blender Eevee ground/shadow 也被 Unity ground fill 与不同 shadow response 取代。
- rev 3 保持 geometry digest=`e2a838c2…02fe`、material digest=`366b788b…9aa8`、core matrices、血红／黑纹／银边、mask 与 emission=`0` 不变。新 recipe 只含一个 `2048×1024` scene-linear Rec.709/D65 EXR、rotation=`0°`、strength=`0.125`、一个 D65 directional light、shadow-map contact、零 AREA light、零 reflection card、零 synthetic highlight 和 identity display LUT。
- 新 EXR 用 OpenImageIO 写盘并回读：RGB nonzero=`100%`、range=`0.0170–1.1377`、seam delta=`0`。Blender 与 Unity 都使用同一 EXR hash、方向、强度、76 mm／36 mm 横向 sensor、相同物体 transform 和原始 `1400×1100` 整帧。
- 当前整帧指标：SSIM=`0.7807`；MAE=`11.46`；background MAE=`13.85`；heatmap >24=`2.24%`；object DeltaE76 median=`3.0`、p95=`18.71`；blood-red median=`8.31`；Clay gradient magnitude error=`4.58%`；Blender clipping=`0`、Unity=`0.0043%`。Unity 接触阴影方向和背景仍可见不同，因此未声明 Gate 11 parity。
- 评审证据：`evidence/08-lighting/rev-003/gate08-r003-portability-board.png` 保持每格原始 `1400×1100`，无独立 crop／resize；`gate08-r003-old-new-unity-review.mp4` 依次比较旧获批 Blender、新 portable Blender 和同合同 Unity；`unity-portable-orbit.mp4` 为隔离 Unity 轨道录屏。
- 工作台深链：`?model=magnetic-slide-tile&tab=materials&gate=08-lighting&asset=magnetic-slide-tile-lighting-comparison-recording-r003`。本轮只请求重新确认共同灯光方向；不自动批准 Gate 08，不推进 Gate 09、Gate 11 或 Gate 12。
- 未修改 `Assets/_EDC/Scenes/MeshyEDC.unity`，未 promotion、build、install、launch 或 phone。Device Accepted pending。
- 验证：Blender 5.2 重开确认 `1` 个 SUN、零 AREA、Standard／None、`1400×1100`；portable Unity EditMode=`4/4`；Node／pipeline=`173/173`；model 与全 pipeline validator errors／missingFiles／unhashed=`0/0/0`；桌面、`390×844` 移动、三个评审 modal 和深链 runtime／loading failure=`0/0`；Python／JavaScript／XML syntax 与 focused diff 通过。全 Unity EditMode=`352/356`，四个失败属于既有 Fan Card geometry、native copy、shipping environment 和 progression UI，不涉及此隔离候选。

## 2026-08-28 Magnetic Slide Tile Gate 11 rev 10 整帧质量阻塞

> **当前状态：pipeline rev=`206`。Gate 01–10=`approved`；Gate 11 rev 9=`rejected history`；Gate 11 rev 10=`draft / blocked-not-ready-for-review`；Gate 12=`stale / not started`。不请求视觉批准，未推送手机。**

- rev 9 拒绝：旧 silhouette／局部色差报告通过，但整帧仍有过曝白斑、构图／背景偏差、扁平 Clay、弱接触阴影和大面积 heatmap。44 个 rev 9 scene／render／report／recording／process 文件继续匹配原 SHA-256 并保留为 rejected history；共享 EditMode 源是后续修订使用的 mutable harness。
- 根因：rev 9 将环境反射又叠加为世界空间 synthetic softbox，形成双重白斑；Unity point-light 功率未按 Blender W→Unity intensity 校准；point shadow 被禁用；ground 过大且 flat ambient 过强；ACES／post exposure 与 Blender AgX 不同；相机轴映射、sensor fit 和板图独立裁剪隐藏了整帧误差。
- rev 10 修复：继续使用 Gate 10 rev 9 原四轨 FBX、collision、mask、EXR、geometry digest 和 artwork placement。候选只在 `Assets/_EDC/Candidates/MagneticSlideTileGate11R010/`。相机固定 `1400×1100`、76 mm、36 mm sensor width；输出禁止独立 crop／post-align。ground 改为有限 0.22 m 接收面；启用阴影，降低 ambient／EXR／post exposure；重新标定 key／fill／rim；降低晶体 reflection／clearcoat／smoothness，降低银色 direct specular，并缩小 synthetic hotspot。
- 原始同帧几何：silhouette IoU=`0.999069`、bbox centroid error=`0.02 px`、bbox scale relative error=`0.041%`，camera matrix、object transform／bounds 在报告中保存。Unity transport、8 render meshes、80,102 vertices、99,280 triangles、两份 108-triangle collision、`18.076433 mm` 和 `30×12°` 全通过；shipping scene SHA-256 仍为 `99083a32…850d`。
- 整帧结果：SSIM=`0.7088`（门限 `≥0.78`）；perceptual proxy=`0.0722`（`≤0.065`）；MAE=`15.88`；background MAE=`11.10`；heatmap >24 area=`16.10%`（`≤12%`）。区域 DeltaE76、完整 heatmap 和相同尺寸原图记录在 `full-frame-parity-report.json`。
- 仍阻塞：hotspot area error=`9.87%`、centroid error=`48.21 px`、aspect error=`129.31%`；Clay gradient direction cosine=`0.949`，但 magnitude error=`39.17%`；contact-shadow error=`101.23%`。因此没有把 rev 10 标为 `ready_for_review`。
- 交互证据：`unity-gate11-r010-interactive-review.mp4` 是真实 Unity H.264 `960×720`、72 帧、6 秒录屏，含 matched camera、orbit、closed、max-open、12°与36°姿态。整帧板为 `gate11-r010-full-frame-board.png`；默认不独立裁剪。
- 工作台：深链 `?model=magnetic-slide-tile&tab=unity&gate=11-unity-parity&asset=magnetic-slide-tile-unity-parity-interactive-recording-r010` 直接打开真实录屏。桌面 `1440×1000`、移动 `390×844`、modal 返回、12 Gates、七页签、三个 blocker、无批准控件均通过；runtime/loading failure=`0/0`。截图：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate11-r010-blocked-workbench.png`。
- 验证：focused Unity EditMode=`7/7`；full-frame validator 与 final blocked-state validator 通过；Model Provenance Explorer=`171/171`；browser desktop/mobile/modal=`pass`。视觉批准待确认状态不适用：本轮明确阻塞且未请求批准。未进入 Gate 12、shipping promotion、build、install、launch 或 phone；Device Accepted pending。

## 2026-08-27 Magnetic Slide Tile Gate 10 rev 9 导出包

> **历史状态：Gate 09 rev 8 已由用户以原话“你给我看一下最终在 Unity 里边的呈现吧。”批准。Gate 10 rev 9 后由用户明确批准并被 Gate 11 rev 9 消费。**

- Gate 10 只导出批准的四轨模型。geometry digest=`e2a838c2…02fe`、material digest=`366b788b…9aa8`、UV digest=`48fe1836…f062`、机制合同=`5aee7181…7ea`、Gate 09 portability contract=`fce83a96…2134` 均锁定。
- 闭合 bounds=`31×50×12 mm`，仍为 `user-authorized-provisional`。平底顶面=`5.875 mm`、凸轴=`0.2 mm`；固定底片／轴、旋转载体、followers、球候选、移动顶片和四条顶片底槽保持命名 hierarchy。
- 导出包包含 authoritative Blend、FBX、GLB、独立 collision FBX、21 个纹理／环境／合同／metadata 文件。FBX／GLB 独立 re-import 均为 `0.031×0.050×0.012 m`；GLB=`20 nodes / 8 meshes / 7 materials / 4 embedded images / 0 animations`。
- FBX 使用 `mesh_smooth_type=FACE`。导出前临时三角化，不改权威源拓扑；GLB 含 NORMAL／TANGENT／TEXCOORD_0。侧壁平滑、平面 cap 硬边；没有 `mesh_smooth_type=OFF`、旧双壳 cavity、reflection-band 环境或未批准 LOD／高低模对。
- collision 只存在于单独 FBX，含 `COL_BottomExterior` 与 `COL_MovingTop`，无材质且 `rendering=false`。它不出现在 authoritative Blend 或产品 GLB 中。
- 上下图案 mask hash 分别为 `8250df70…1c36` 与 `7bf5921f…a7c2`。BaseColor 保持 sRGB；MaskMap／Normal／artwork mask 为 linear。原生 `620×1000` 使用 NPOT `None`，禁止缩放或拉伸为 `512×1024`。ASTC 只在 Gate 11 对比后应用。
- `unity-export-manifest.json` SHA-256=`d56b2e41a3156ffe8cd1a358892d1aaff0ec56dee6364e3c8a4dd909b9952152`。它固定坐标轴／单位、pivot 两套坐标空间、transforms、30×12°、最大行程、有限端点／最小覆盖、PBR mapping、AgX→ACES 校准和 Gate 09 parity 容差。
- 验证：authoritative Blend audit、FBX／GLB／collision re-import、GLB header／embedded images／split normals／tangents／UV、纹理 hash／NPOT、EXR byte hash 和 export manifest 均通过。默认闭合，线速度／角速度=`0`，无 action、driver、animation 或 self-motion。Node=`159/159`；all/model pipeline、Python／JavaScript／五个 XML、focused diff 通过。final validation SHA-256=`1b1b1502…9fd8`。
- 主批准证据为 `package/magnetic-slide-tile-render-r009.glb`；`export-review-summary.png` 只作摘要。工作台在桌面 `1440 px` 与移动 `390 px` 通过；真实 GLB `load/orbit/zoom` 后才解锁批准，reload 保留进度，runtime/loading failure=`0/0`。真实 GLB 预览：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate10-rev9-glb-viewer.png`；工作台：`magnetic-slide-gate10-rev9-persistent-workbench.png`。
- DeliveryState：没有 Unity import settings、URP scene、Build、安装或 iPhone 运行；旧 shipping Unity 模型仍为默认。Gate 11 只在 Gate 10 明确批准后开始。

## 2026-08-27 Magnetic Slide Tile Gate 09 rev 8 环境与 Unity 可移植合同

> **历史状态：Gate 08 rev 2 已由用户以原话“进行下一步吧”批准。Gate 09 rev 8 后由用户以原话“你给我看一下最终在 Unity 里边的呈现吧。”批准，并被 Gate 10 rev 9 消费。**

- 用户锁定最终目标：`transfer to Unity with no avoidable loss and run on iPhone`。这里的 `lossless` 分两类：几何、层级、轴心、UV、上下图案 mask 必须确定性精确保留；Blender 程序材质节点不能逐节点转成 URP，因此材质、灯光和色彩管理用量化视觉一致验收，不虚称 shader graph 字节一致。
- Gate 09 直接消费批准 Gate 08 blend `547055f5…21b1`、geometry digest `e2a838c2…02fe`、material digest `366b788b…9aa8`、light digest `890e1f12…a36c`、camera digest `916c5b3b…0259` 和机制合同 `5aee7181…7ea`。neutral／shipping 前后 geometry、UV、hierarchy、material、light、source camera 均一致；7 个批准材质 emission=`0`。
- Shipping 环境是确定性生成的 `2048×1024` equirectangular OpenEXR：scene-linear Rec.709、D65、SHA-256=`7f1c9fded84c453efbc5300a6a71fe2948534055d3f4ae5052696909f30be6ab`，seam max linear delta=`0`，P01–P99 dynamic range=`6.21756 stops`。World strength=`0.65`、rotation=`0°`；只使用 Environment Texture → Background → World Output，无 Blender-only 程序 world 节点。
- Ground 为 `[0.018,0.016,0.017] linear`、metallic=`0`、roughness=`0.42`。neutral／shipping 对比保持同机位、姿态、四灯和 exposure=`-0.35 EV`，只允许 world／reflection／background／ground 变化。闭合、最大打开及反射近照 changed-pixel fraction 分别为 `0.02408/0.10357/0.20429`。
- 目标环境证据覆盖闭合、最大打开、12°、36°、左右斜视、低角度、平底凸轴、四槽底面和载体／followers／球候选。血红中位 hue=`0–2.61°`，关键视图 crystal variation `≥15.226`，最大 clipped fraction=`0.00040195`。`3600` 个包含样本继续通过，无 action、driver 或 self-motion。
- `unity-portability-contract.json` SHA-256=`fce83a968df4f978e84ffbab7f026c57d7b60e762d70f7cdb2f2a1aa5cf22134`。它记录 14 个源资产 hash、精确 hierarchy／pivot／UV／mask、上下独立 artwork、PBR `BaseMap + MaskMap(R metallic/G AO/B detail/A smoothness) + Normal + 独立 ArtworkMask`、silver／black／blood-red／thin-film Fresnel 参数、box-projected Reflection Probe 预期，以及 Blender AgX 和 Unity ACES 的 matched-camera 线性 EXR／24 色块／可选 32³ LUT 校准计划。
- 下游容差：closed bounds max error=`0.001 mm`；vertex/index、hierarchy、artwork mask hash exact；pivot=`0.001 mm`；UV=`1e-6`；silhouette SSIM=`≥0.995` 且 1400×1100 边缘误差=`≤1 px`；median ΔE2000 silver／blood-red／black=`≤3/4/2.5`；P95=`≤6`；reflection highlight centroid=`≤2 px`、亮度相对误差=`≤5%`；clipping=`≤0.001`。
- 交互 GLB 支持 orbit、zoom、中性／Shipping 环境响应与曝光。24 帧 matched neutral/shipping 真实 Blender 双画面转台为完整 fallback recording；静态 board 只作补充。
- 验证：Blender environment、EXR seam／dynamic range／color space、图像、motion containment、GLB、portable texture byte hashes 和 contract asset hashes 已通过。上下 albedo／roughness 从批准 blend 按原始 packed bytes 提取，四个 SHA 与 Gate 07 完全一致。
- 最终验证：Node=`152/152`；model/all-pipeline、Python／JavaScript syntax、五个 XML、focused diff 通过。桌面 `1440 px`、移动 `390 px`、Neutral／Shipping 持久化、GLB、24 帧 H.264 转台、modal、reload、deep-link 均通过，runtime/loading failure=`0/0`。final validation SHA-256=`d120eaa8…1d75`。
- 工作台预览：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate09-rev8-persistent-workbench.png`；聚焦预览：`magnetic-slide-gate09-rev8-workbench-focused.png`。
- DeliveryState：只完成 Gate 09 Blender 环境和 Unity 可移植规格。没有 Unity 导入设置、Build、安装或 iPhone 运行；旧 shipping Unity 模型仍为默认。iPhone 性能与 Device Accepted 在 Gate 12 视觉批准后执行。

## 2026-08-27 Magnetic Slide Tile Gate 08 rev 2 灯光

> **历史状态：Gate 07 rev 11 已由用户以原话“继续”批准。Gate 08 rev 2 后由用户以原话“进行下一步吧”批准，并被 Gate 09 rev 8 消费。**

- Gate 08 直接消费批准 Gate 07 blend `fdf6e962…d274` 与机制合同 `5aee7181…7ea`。灯光前后 geometry digest=`e2a838c2…02fe`，material digest=`366b788b…9aa8`；核心矩阵恢复一致，7 个批准材质 emission 均为 `0`。
- 四灯：Key `(58,-72,96) mm`、`20 mm`、Neutral/Studio/Daylight=`42/48/44 kW`、`6504/5600/6504 K`；Fill `(-54,-12,58) mm`、`32 mm`、`24/26/34 kW`、`6504/7000/7500 K`；Rim `(44,70,62) mm`、`18 mm`、`42/50/39 kW`、`6504 K`；Mechanism Reveal `(-26,20,28) mm`、`18 mm`、`16/22/20 kW`、`5600/5200/6504 K`。
- World 为中性均匀色，Neutral/Studio/Daylight strength=`0.35/0.18/0.65`；HDRI=`null`。四张 camera-hidden 反射卡独立记录。AgX Medium High Contrast、exposure=`-0.35 EV`、gamma=`1`、white balance=`6504 K`、tint=`10`。
- 真实 Blender 证据：Hero、左右斜视、低角度、三灯光同机位对比、闭合／最大打开／12°／36°、平底凸轴、四槽底面、载体与 follower clearance。Beauty／Clay／World Normal／View Depth／Roughness 共用 Hero 相机与闭合姿态。
- 交互 GLB 支持 orbit、zoom、中性／影棚／日光切换、环境开关与曝光；24 帧真实 Blender 转台为补充证据。工作台仍使用固定七页签、12 Gate、持久路由与历史。
- 图像 audit：最大 Beauty clipped fraction=`0.00003831`；血红中位 hue=`0–6°`；magenta fraction=`0–0.0073`；中性高光 chroma=`1–8`；blue-gray fraction=`0`。Clay／Normal／Depth／Roughness 均有独立 hash 和有效动态范围。
- 验证：Node=`144/144`；pipeline/model、Blender reopen、GLB、turntable、Python/JavaScript/XML syntax 与 focused diff 通过。桌面 `1440 px`、移动 `390 px`、三灯光持久化、modal、reload、deep-link 均通过，runtime/loading failure=`0/0`。
- 工作台预览：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate08-rev2-persistent-workbench.png`；聚焦预览：`magnetic-slide-gate08-rev2-workbench-focused.png`。
- DeliveryState：仅完成 Gate 08 Blender 灯光评审证据。未运行 Simulator、Unity、build、install 或 device；旧 shipping Unity 模型仍为默认。

## 2026-08-27 Magnetic Slide Tile Gate 07 rev 11 材质

> **历史状态：Gate 06 rev 4 已由用户以原话“那你继续呗”批准。Gate 07 rev 11 已由用户以原话“继续”批准并被 Gate 08 rev 2 消费。**

- 唯一外观权威仍为用户血红实拍。复用上片 mask `8250df70…1c36`、下片 direct/reconstructed mask `7bf5921f…a7c2`、完整黑边 mask `2179bf26…4fc` 和 rev 10 中性材质配方；上下图案保持独立可替换。
- Gate 07 直接消费 Gate 06 blend `8047be52…7085` 和机制合同 `5aee7181…7ea`。材质前、材质后、闭合／打开／0°／12°／36°的 evaluated geometry digest 均为 `e2a838c2…02fe`。
- 晶体：IOR=`1.52`、coat=`0.48/0.035`、transmission=`0.08`、thin film=`1.38/410 nm`、granular scale=`28`、microflake scale=`85`、emission=`0`。银边：metallic=`1`、roughness=`0.075`、anisotropy=`0.16`。深色侧壁：metallic=`0.24`、roughness=`0.18`、coat=`0.55`。
- `BottomExterior` 与 `MovingTopBody` 各有独立 artwork top cap、深色侧壁、细银边和中性底面 slot。轴座／载体为银白技术区；四槽、followers 与 2–3 mm 球候选只显示中性技术材质，球准确材质仍标 `unknown`。
- 纹理为 `620×1000 px`，打包进 blend 和 GLB。上下 albedo SHA 分别为 `c0e9305d…53a5`、`968c1e87…50eb`；上下 red σ=`40.39/41.06`，microflake pixels=`1589/1685`；黑边 mask 内黑色比例=`1/1`。
- 真实 Blender 证据：neutral PBR board、source comparison、闭合／打开、下片 artwork、银边反射、四槽底面、内部材料隔离、0°／12°／36°晶体和 microflake closeup。完整 24 帧真实渲染转台已编码为 MP4。
- 独立 Blender 5.2 audit 通过：6 个必需材质存在，4 张纹理均内嵌 GLB，8 个 mesh、7 个 GLB 材质、无 animation/driver/self-motion。图像 audit 通过；最大 clipped fraction=`0.0005266`，无可见材质 clipping。
- 验证：Node=`136/136`；pipeline/model validator、Python/JavaScript/XML syntax 通过。桌面 `1440 px`、移动 `390 px`、GLB orbit/zoom、环境／曝光状态、真实转台、modal、reload、deep-link 和来源视频通过，runtime/loading failure=`0/0`。
- 工作台预览：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate07-rev11-persistent-workbench.png`；聚焦预览：`magnetic-slide-gate07-rev11-workbench-focused.png`。
- DeliveryState：仅完成 Gate 07 材质评审证据。未运行 Simulator、Unity、build、install 或 device；旧 shipping Unity 模型仍为默认。

## 2026-08-27 Magnetic Slide Tile Gate 06 rev 4 同源几何

> **历史状态：Gate 05 rev 6 已由用户以原话“可以的”批准；Gate 06 rev 4 后由用户以原话“那你继续呗”批准并被 Gate 07 rev 11 消费。**

- Gate 06 消费机制合同 `5aee7181…7ea` 和已批准 Gate 05 blend `fc067610…f7b`。核心 evaluated geometry digest 为 `e2a838c2…02fe`，全部视图与姿态一致。
- 闭合 bounds=`50×31×12 mm`，仍是用户授权暂定值。厚度栈=`5.875 + 0.25 + 5.875 = 12 mm`；底片顶面 Z=`5.875 mm`，最大偏差=`0 mm`；凸轴=`0.2 mm`；carrier 净藏深度=`0.049999714 mm`。
- 四条有限槽保持外二直推、内二轴联动；球候选=`2–3 mm`，槽宽=`1.8–3.0 mm`。左右 follower 的 X 对齐误差=`0 mm`；`3600/3600` 个 0.5°／五行程包含样本通过。
- Blender 5.2 独立 audit：8 个核心 mesh nonmanifold edges=`0`、invalid normals=`0`、均有 UV；无 action、driver 或 self-motion。极细三角形的 Blender MikkTSpace 有 12 个退化 loop，几何 longest-edge tangent audit 为 `0` 失败，未修改已批准 topology。
- 证据：六视图、Workbench、尺寸／轴心／切线叠图、爆炸、四槽底面、平面凸轴、A–A 剖面、闭合／最大行程／12°／36°、authoritative blend 和交互 GLB，均位于 `evidence/06-geometry/rev-004/`。
- 验证：Node=`128/128`；pipeline/model validator、GLB、Python/JavaScript/HTML syntax 通过。桌面 `1440 px`、移动 `390 px`、七页签、12 Gate、modal、reload、deep-link、history、过期材质和原视频播放通过，runtime/loading failure=`0/0`。
- 工作台预览：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate06-rev4-persistent-workbench.png`；聚焦预览：`magnetic-slide-gate06-rev4-workbench-focused.png`。
- DeliveryState：仅完成 Gate 06 几何评审证据。未推进材质、Simulator、Unity、build、install 或 device；旧 shipping Unity 模型仍为默认。

## 2026-08-27 Magnetic Slide Tile Gate 05 rev 6 平底片顶面

> **当前状态：pipeline rev=`174`。Gate 01–04=`approved`；Gate 05 rev 6=`ready_for_review`；Gate 06–11=`stale`；Gate 12=`rejected`。视觉批准待确认，未推送手机。**

- 用户部分批准 rev 5 的 hierarchy 与运动学，只否决底片顶面的环形内凹。rev 5 证据保留为历史；rev 6 只替换 `BottomExterior` 顶皮并删除 `_BottomExteriorUpperRim`。
- rev 6 顶面是 Z=`5.875 mm` 的连续平面。1 mm 网格、轴座占地外 `1218` 点的 min/max 均为 `5.875 mm`，最大偏差=`0.000 mm`，门限=`0.001 mm`；513 个上表面顶点也全部为 `5.875 mm`。
- `BottomExterior` 无 Boolean/recess modifier、负深度、凹坑或圆形内陷。独立 `FixedAxisBoss` 高于平面 `0.2 mm`；carrier、followers 和 balls 最高 Z=`5.825000286 mm`，至少藏于平面下 `0.049999714 mm`。
- 独立 rev 5/6 blend fingerprint 比较确认 `MovingTopBody`、轴座、载体、左右 follower 和球形状不变。四条顶片背面槽、闭合／最大行程／12°／36°、复合 transform 和 3600 个 0.5°/五行程包含样本均保持通过。
- 输出：`evidence/05-blockout/rev-006/magnetic-slide-tile-blockout-r006.blend`、交互 GLB、hero、closed、max-open、12°／36°、平面近照、凸起轴座近照、四槽底面、分层和 overlap overlay。
- 验证：Blender 5.2 重开 audit 通过，32 objects，8 个关键 mesh nonmanifold edges=`0`，无 animation/self-motion；Node=`121/121`；工作台桌面/移动、rev 6 GLB、modal、reload、deep-link、history、历史 rev 4/5、视频来源播放通过，runtime/loading failure=`0/0`。
- 预览：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev6-persistent-workbench.png`。DeliveryState：只完成 Gate 05 白模评审修订；未推进材质、Simulator、Unity、build、install 或 device。旧 shipping Unity 模型仍为默认。

## 2026-08-27 Magnetic Slide Tile Gate 05 rev 5 + 持久工作台

> **历史状态：pipeline rev=`170`。rev 5 hierarchy/kinematics 后获部分批准，但底片顶面内凹被否决；当前入口见 rev 6。**

- 用户把四轨、凸起轴座、球候选、载体和轨宽纠正定义为白模反馈，并明确要求不再回到 CAD／尺寸审批。Gate 03 rev 11 与 Gate 04 rev 13 已按聊天最终权限消费合同 `5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea`。
- rev 5 Blender 白模包含光滑无外露轨道的 `BottomExterior`、正凸起 `FixedAxisBoss`、带双侧开口的圆形 `RotatingCarrier`、`CarrierFollowerLeft/Right`、2.5 mm 球候选及 `MovingTop` 背面四条真实有限凹槽。外二直推，内二轴联动。
- 临时建模值：L=`50 mm`（估计范围 `46.8–57.8`）、W=`31 mm`（`30.8–35.7`）、T=`12 mm`（低置信）、行程=`18.076433121 mm`、轴偏移=`16 mm`、载体=`23 mm`、球候选=`2–3 mm`、槽宽=`1.8–3.0 mm`。全部是 `user-authorized-provisional`，不是生产实测。
- Blender 输出：`evidence/05-blockout/rev-005/magnetic-slide-tile-blockout-r005.blend`、交互 GLB、closed／max-open／12°／36°、四槽底面、凸起轴座近照、分层和 overlap overlay。`3600/3600` 个 0.5°／五行程包含样本通过；独立 Blender 5.2 audit 重开 blend 后确认 32 objects、关键 mesh nonmanifold edges=`0`、无 action、driver、keyframe 或 self-motion。
- reuse plan 保留 256 段胶囊外形、normal 审计、上下图案 mask、血红晶体／黑边／银色配方及灯光／环境经验。rev 4 凹坑、双槽及旧 hierarchy 明确不复用。
- 工作台改为仓库级单一持久入口。左侧模型、当前任务、`当前 Gate 05/12`、`已批准 4/12`、完整路线图和七个固定页签始终可见；过期／被退回证据在历史区可查。model/tab/gate/scroll/view/asset 支持 localStorage、reload、Back/Forward 及查询参数深链。
- 验证：Node=`113/113`；pipeline/model validator 通过；真实 GLB、桌面 `1440 px`、移动 `390 px`、七页签、12 Gate、历史证据、reload、deep-link、browser history、视频 modal 均通过；runtime/loading failure=`0/0`。预览：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev5-persistent-workbench.png`。
- DeliveryState：Gate 05 白模已生成并等待视觉批准。未推进材质、Simulator、Unity、build、install 或 device；旧 shipping Unity 模型仍为默认。

## 2026-08-27 Magnetic Slide Tile 四轨 + 凸起轴座 CAD 纠正

> **当前状态：pipeline rev=`165`。Gate 01–02=`approved`；Gate 03 rev 10=`ready_for_review`；Gate 04=`stale`；Gate 05 rev 4=`rejected`；Gate 06–11=`stale`；Gate 12=`rejected`。视觉批准待确认，未推送手机。**

- 用户否决 Gate 05 rev 4：`MinimumOverlapDisk` 被错误做成可见圆形凹坑，且 Blender builder 未消费最新机械组件合同。rev 4 全部证据保留，但不得复用其机构几何。
- Gate 02 rev 16 合同 SHA-256=`5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea`。顶片背面固定为四条有限纵轨：外二负责直推，内二连接中心轴载体。底壳外表面光滑；`FixedAxisBoss` 必须正向凸起，禁止 recessed-axis geometry。
- 球件候选直径=`2–3 mm`，单轨宽度估计=`1.8–3.0 mm` 且未经新批准不得超过 `3 mm`。材料、数量、弹簧布局、槽截面/深度、预载、工作间隙、余量和公差保持 unknown。
- Gate 03 rev 10 使用 OpenCV 对相邻同深度手掌帧做人工复核 landmark/minAreaRect 比例分析，并拒绝严重透视/运动模糊帧。AIST 日本成人手宽 B03 P25–P75=`75.3–83.8 mm` 仅作先验。外形估计 L=`46.8–57.8 mm`、W=`30.8–35.7 mm`；`50×31 mm` 在范围内。厚度仍为低置信临时值，不称生产实测。
- 新 CAD 显示 `BottomExterior`、凸起 `FixedAxisBoss`、`RotatingCarrier`、左右 followers、球件候选、`MovingTop`、四条分色轨道与 unknown springs/preload。`MinimumOverlapDisk` 只作连续包含验证，不是实体。
- 生成门禁会拒绝：轨数不等于 4、缺少外/内职责、轴座凸起 `≤0`、recessed-axis flag、球径超出 `2–3 mm`、轨宽 `>3 mm` 或合同 hash 未消费。
- 验证：Node/pipeline tests=`102/102`；连续包含 sweep=`1800/1800`；桌面 `1440 px`、移动 `390 px`、复合 pointer、modal、视频和来源图库均通过，runtime/loading failure=`0/0`。预览：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate03-rev10-four-track-cad-focused.png`。
- DeliveryState：只更新 CAD、合同、证据和工作台。未重建 Blender；未触碰 Simulator、Unity、build、install、phone。旧 shipping 模型继续默认。

## 2026-08-27 Magnetic Fan Card 材质批准并推进 App

> **当前状态：用户原话“可以，然后看看能不能推进 app 里面吧。”视觉已批准。Release 已安装到已连接 iPhone（JW，Build 40，source `62d8bcd`）。自动启动被系统拒绝：开发者证书尚未在设备上信任。Device Accepted 仍待用户在手机上确认。**

- 批准对象：2026-08-27 14:03 shipping 预览（hero/top/left/right/low/back/track）。几何、72 段 FBX、弱反射 `0.28`、暖银 smoothness `0.24`。
- 批准预览副本：`Docs/DesignBibleAssets/fan-card-shipping-hero-20260827.png` 等 7 张。
- 安装证据：`scripts/ios_build_and_install.sh` Unity 导出 + Xcode Release `BUILD SUCCEEDED`；`devicectl` install `info.outcome=success`，bundle `com.jiaweizhou.fidgetspinner.codex`，设备 `00008130-001A00361EE0001C`。Launch 失败：`FBSOpenApplicationErrorDomain` Security，profile 未显式信任。
- DecisionState：`FDB-FAN-018/019/020/021` locked and visually approved。DeliveryState：Installed。不等于 Device Accepted。
- 验证：guardrail=`ALL PASS (7.590 mm)`；`FanCardAcceptanceTests`=`23/23`。

## 2026-08-27 Magnetic Fan Card 材质／反射去数字感

> **历史状态：去数字反光后过暗，已提亮并由用户以“可以”批准；当前入口见上一节。**

- 用户原话：“这几个图都挺好的呀…太“digital”的感觉，太强了。”随后：“这个在真实场景中也是这样的吗？会不会有点太暗了呀？”预览来自 shipping `MagneticFanCard.unity` 详情页灯光，不是画布压缩；第一轮把反射从 `0.82` 收到 `0.28` 时把暖银曝光一起压成炭灰。
- 本轮只抬金属可读性：key `0.72→0.92`，fill `0.16→0.28`，暖银基底填光 `0.20→0.42`。反射仍为 `0.28`，smoothness 仍为 `0.24`，不恢复 SH `0.30` 地板和假 studio 高光。几何、FBX、滑轨、四档和 Haptic 未改。
- 暖银：去掉 SH `0.30` 地板和 `0.34` 无光抬亮；smoothness `0.36→0.24`；珠喷 bump `0.060→0.13`；IBL 只保留粗糙宽高光。
- 枪色：删除 `studioForward`／`studioSheen` 和侧壁 `0.58` 假高光；改走主光 + SH + 弱环境。
- 铬帽：程序 softbox `0.94→0.42`；smoothness `0.92→0.78`。金边 metallic `0.82`、smoothness `0.22`。
- 环境：反射 `0.82→0.28`；key `0.96→0.72`；fill `0.34→0.16`；fan-card cubemap panel `0.86→0.22`。
- 验证：source + full guardrail=`ALL PASS (7.590 mm)`；`FanCardAcceptanceTests`=`23/23`（含 `CardGeometryValidator`）。shipping 预览：`../../../Artifacts/FanCardMaterialPreview/fan-card-hero.png`、`fan-card-top.png`、`fan-card-left.png`、`fan-card-right.png`、`fan-card-low.png`、`fan-card-back.png`、`fan-card-back-track-closeup.png`。
- DecisionState：`FDB-FAN-018` locked，shipping 配方重新校准。DeliveryState：场景已重建，视觉批准待确认。没有 Build、没有安装、没有推送手机。

## 2026-08-27 Magnetic Fan Card 用权威 FBX 替换 app 内玩具

> **历史状态：pipeline rev=`136`。Gate 01–10=`approved`；Gate 11 Unity parity=`ready_for_review`；Gate 12=`stale`。用户随后确认几何可用，但要求降低材质数字感；当前入口见上一节。**

- 用户原话要求用重建模型替换 app 里的 fan toy。该玩具就是 Library／详情页场景 `Assets/_FanCard/Scenes/MagneticFanCard.unity`；runtime、四档磁轨、Haptic 和 AAA／QKA 未改。
- Gate 10 已批准：70,530 三角形、32 meshes、5 materials、碰撞仍为 8 段。Gate 11 同相机 silhouette IoU=`0.9914715`，bounds 误差 `0.00001117%`。
- `FanCardSceneBuilder.BuildScene()` 从 `MagneticFanCardVisual.fbx` 导入牌身／金边／银面，不再在 BuildScene 里调用 `CreateRoundedBoxMesh`／`CreateRoundedSurfaceMesh`。`FanCardSatinSilver.shader` 不含 `softPanel`／`reflectedBand`。
- 验证：source + full guardrail=`ALL PASS (7.590 mm)`；`CardGeometryValidator`=`ALL PASS`；`FanCardAcceptanceTests`=`23/23`。shipping 预览：`../../../Artifacts/FanCardMaterialPreview/fan-card-hero.png`、`fan-card-top.png`、`fan-card-left.png`、`fan-card-right.png`、`fan-card-low.png`、`fan-card-back.png`、`fan-card-back-track-closeup.png`。
- DecisionState：`FDB-FAN-021` locked。DeliveryState：shipping 场景已换模型，Gate 12 视觉批准未确认。没有 Build、没有安装、没有推送手机。

## 2026-08-27 Premium Display Case Gate 10 批准／Gate 11 rev 1 待审批

> **当前状态：pipeline rev=`70`。Gate 01–10=`approved`；Gate 11 Unity parity rev 1=`ready_for_review`；Gate 12=`blocked`；approved count=`10/12`。视觉批准待确认，未推送手机。**

- 用户选择“正确，批准并导入 Unity（推荐）”已由 Gate 10 approval event=`2aa2212a-7c62-4357-8539-46cef2b84955` 持久化。FBX SHA-256=`21c9db68723f0006d7c6bfec5280cafe55c16cf5392ff97c365c966e91f847ae` 是 Unity authority；GLB SHA-256=`fb22fc333c0c5fbc715385ca510dbf0ee4a18b9847f64764b4511e0278ba4df8` 只作 portable validation evidence。
- Gate 11 event=`dce81b8b-061e-493d-a44b-14c50a4784cd`。获批 FBX 以 byte-identical 副本导入独立 `Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001/`；candidate prefab=`Prefabs/PresentationRoot.prefab`，neutral parity scene=`Scenes/PremiumDisplayCaseGate11Parity.unity`。未替换 `Assets/Resources/Gacha/PremiumDisplayCase.prefab` 或 shipping scene／coordinator wiring。
- candidate 保持 `PresentationRoot → CaseAssembly`、空 `ContentSlot`、`12` nodes、`5` meshes、`100,016` triangles、`0.228 × 0.304 × 0.059 m` bounds、origin pivot、connected tube、blank runtime label zones 与材质 assignment。未捆绑 toy/prize、proxy、explode、Collider、动画、timing 或文字。
- FBX↔Unity 五个 mesh 顶点映射为双射；authority digest 与 Unity matched digest 均为 `4cffa449d4ed129cedd4575a9a33ec0e2ab76790d73807d9688522fc796d1e58`，最大 vertex error=`0.000096222 mm`。Unity geometry digest=`222a9ab01cd51fd7293664ed8b3b55778f26745ec8b8df2c570f547dfb0205e2`；bounds、triangle count、normals／winding 与透明排序通过。
- frosted shells／connected tube 使用 candidate-only `Gate11MeshClippedFrosted` mesh fragment shader；label 保持 blank runtime zone。Point Light=`0`、external halo=`0`、silhouette 外 sheen pixels=`0`。三盏中性 Directional Light 只服务 parity scene，不是 shipping timing／light constants。
- 真实 Unity neutral=`ArtSource/ModelPipeline/premium-display-case/evidence/11-unity-parity/rev-001/unity-neutral.png`；Blender 对照=`blender-vs-unity-neutral.png`；完整 Unity inspection recording=`unity-orbit-review.mp4`（H.264、`820 × 1000`、`48` frames、`4.0 s`、inspection-only）。hierarchy／pivot／material、bounds／digest 与总 parity 报告在同目录。
- Unity 6000.5.6f1 完成编译；`PremiumDisplayCaseGate11ParityTests`=`8/8 passed`。Blender 5.2.0 FBX↔Unity correspondence=`pass`；Model Provenance Explorer=`128/128 passed`；model validator rev=`70`、approved=`10/12`、earliest=`11-unity-parity ready_for_review`、errors／missingFiles／unhashed=`0/0/0`；全 pipeline validator 零 schema、missing file 或 unhashed 错误。
- shipping prefab／scene／旧 model SHA-256 仍为 `88cf4f4a...`／`f83df832...`／`41c71ffc...`。Gate 11 只到 `ready_for_review`；Gate 12、shipping replacement、final animation timing、build、install、launch 和 phone 全部未开始。视觉批准待确认，未推送手机。

## 历史／已拒绝：2026-08-27 Magnetic Slide Tile Gate 05 rev 4 CAD 白模

> **历史状态：pipeline rev=`162` 时曾为 `ready_for_review`；用户随后明确拒绝可见圆形凹坑。该轮只保留失败证据，不得恢复。**

- 用户原话“你直接来吧…leverage 我们之前所有做过的工作，包括图案，材质，灯光和细节调整.” 已作为 Gate 03–05 的当前授权来源；不把任何复用数值称为生产实测。
- Gate 03 rev 9 临时合同：`50×31×12 mm`；上下片各 `5.875 mm`；接缝 `0.25 mm`；轴心距最近圆端 `16 mm`；载体直径 `23 mm`；最大行程 `0.3615286624L=18.076433121 mm`。旧 `21 mm` 已移出当前合同。槽宽/深、随动件尺寸、轴径、接触截面、工作间隙、加工余量和公差保持 unknown。
- Gate 04 rev 11 只迁移已批准 Gate 02 rev 15 合同/hash。新 hierarchy 为固定光滑 `BottomExterior`、不漂移 `FixedAxis`、只绕轴旋转的 `RotatingCarrier`、载体 followers、执行 `R_fixedAxis(θ)·T_local(s)` 的 `TopPlate`、有限双槽 centerline metadata 与不渲染 `UnknownContacts`。
- `reuse-plan.json` 哈希关联 9 项旧工作：rev 3 高精度解析胶囊 builder、rev 2 normal audit、独立上/下 artwork mask、rev 10 血红晶体/黑边/抛光银 recipe、Gate 08 lighting、Gate 09 environment、Gate 02 CAD 合同与交互资产。旧 Gate 05–11 geometry/Blend/exports 均明确 stale，不直接复用。
- Blender 5.2.0 LTS 生成 authoritative `magnetic-slide-tile-blockout-r004.blend`、交互 review GLB、Hero/闭合/最大打开/12°/36°/顶片背面双槽/分层 hierarchy/重叠盘 overlay 共 8 张 `1200×1200` 图。
- 临时 `50×31` 宽度比 CAD midpoint 略窄；物理 overlay 半径安全取 `min(0.318471L,W/2)=15.5 mm`，仍保留更保守的 `18.076433121 mm` 行程。360 个 1° 角度 × 5 行程共 `1800/1800` 样本通过；纵向最大行程余量 `0.423566879 mm`，侧向边界相切。
- Blender audit：固定轴 drift=`0`，顶片始终高于底片，胶囊每半圆 `256` 段、bevel `8` 段，三个实体 mesh 均 closed/manifold 且正体积；无 action/keyframe/driver、自转或可渲染 unknown proxy。
- 交互评审：`ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-004/magnetic-slide-tile-blockout-r004-review.glb`。报告：同目录 `blockout-validation.json`。
- 浏览器：真实 Three.js GLB 加载、正/背/上/左/右/Hero、wireframe、图片 modal/Escape、桌面和 `390 px` 移动端无横向溢出均通过；运行时 exception=`0`。完整工作台：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev4-workbench.png`；报告：同目录 `browser-smoke-validation.json`。
- DeliveryState：仅 Blender Gate 05 白模与 pipeline evidence。独立 Simulator 保持 internal/superseded；Unity、build、install、phone 未触碰，旧 shipping 模型继续默认。

## 历史：2026-08-27 Magnetic Slide Tile Gate 02 rev 15 最小重叠圆盘解析包含 CAD

> **当前状态：pipeline rev=`159`。Gate 01–02=`approved`，Gate 03 measurement contract rev 8=`blocked · 0/9`，Gate 04–11=`stale/blocked`，Gate 12=`rejected`，approved count=`2/12`。旧 Simulator 草稿为 internal/superseded；Blender、Unity、build、install 和 phone 均未开始。**

- 用户否决 rev 14 的 groove-only 最大行程。用户标注截图已按原始字节不可变归档，并定义固定属于 `BottomBase`、以 `FixedAxis` 为圆心的 `MinimumOverlapDisk`。
- 每个合法姿态都满足 `MinimumOverlapDisk ⊆ TopPlateFootprint(s,θ)`。边界接触是合法极限；用户指针/API 不能进入负余量。内部强制无效姿态真实显示闪红，不使用 SVG clip、mask 或层级隐藏露出。
- 当前红圆半径编码为 reviewed-CAD normalized `W/2=0.318471L`；物理 mm 与真实 clearance unknown。槽端候选上限为 `0.46L`，圆盘包含上限为 `1−0.32−0.318471=0.361529L`，实际 `sMax=0.361529L`，限制来源为最小重叠圆盘。
- 角度不变量已经解析证明：对整套姿态应用 `R_fixedAxis(θ)⁻¹` 后，轴心圆盘不变，顶片只剩局部 s 平移。因此当前 capsule 的包含上限不依赖 θ。
- 自动化使用解析 capsule/disk margin 作为连续门禁，并补充 360 个 1° 角度 × 5 行程位置，共 1800 个有效样本。边界余量精确为 0；越界 `1e-6L` 为 invalid。
- 工作台显示红色圆盘、相切点、最小覆盖余量、槽端距离、实际限制原因和派生 sMax；圆盘半径、槽终点和 L/W 修改后实时重算。同步顶视、侧视、A–A 和 reference mapping 保留。
- 合同：`evidence/02-analysis/rev-015/mechanism-evidence-contract.json`，SHA-256=`b4318452f163ef7c105c826d4466a739a1dd0d942d4d74d921c29c39e02a84f2`。
- CAD-only 预览：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate02-rev15-minimum-overlap-disk-cad.png`。用户在完成交互证据后以聊天原话“对了”批准 Gate 02；合同 hash 与几何参数快照已写入 workflow history。最终批准可来自工作台或聊天，以用户最新明确聊天指令为准。
- 当前固定三阶段：参考 + 交互形式（Gate 01–04）→ Blender 建模 + 贴图（Gate 05–10）→ Unity + 场景 + 渲染（Gate 11–12）。Gate 定义和总数仍为 12。
- Gate 03 原 15 项 blocker 已废止。现在仅 9 项核心实测阻塞：闭合总长 L、总宽 W、闭合总厚 T、顶片厚、底片厚、最大直推行程、固定轴心距最近圆端、旋转载体直径、闭合接缝/间隙；每项记录 mm、来源/方法和不确定度。
- 双槽中心距/宽/深、固定轴径、上下台阶高、可见随动/接触尺寸为可选；隐藏时保持 unknown。工作间隙、加工余量、制造公差属于制造阶段，不阻塞初始 Blender。
- 工作台新增四张简明 CAD 测量图、9 项表单、`0/9` 进度、照片上传/素材引用和实时一致性检查。总厚堆叠、轴/载体包络、行程包含为硬检查；L/W 相对 `1.52–1.62` 只警告，不覆盖实测。
- Simulator 在中断前仅写入未注册草稿：`tools/model-provenance-explorer/mechanism-feel-simulator-core.mjs`、对应测试和 `evidence/03-contract/simulator-rev-001/hand-feel-simulator-config.json`。三者均为 internal/superseded，未接入工作台、未注册为 pipeline asset、未生成预览或录屏。独立 Simulator 不再是 Blender 前置条件；只有用户后续要求时才可作为 Unity 交互验证工具。
- Gate 03 当前合同：`evidence/03-contract/rev-008/measurement-modeling-contract.json`。不含旧 `50×31×12/21` 默认值；所有 9 项初始为空。
- 工作台预览：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate03-measurement-guide.png`，SHA-256=`325fb58c1274fc8ae84b9c329fd233cf587ff576daff855cf2862759a4dc0b81`。桌面 1440 px 与移动端 390 px 均通过；移动端无横向溢出。
- 验证：Node tests=`90/90 passed`；pipeline validators=`errors/missingFiles/unhashed 0/0/0`；浏览器桌面/移动专项通过；Node syntax checks 通过。
- DecisionState：Gate 02 rev 15 approved；Gate 03 blocked on physical dimensions。DeliveryState：未开始 Blender/Unity/runtime/Haptic/build/install/device acceptance，旧 shipping 模型继续为默认，未推送手机。

## 历史：2026-08-27 Magnetic Slide Tile Gate 02 rev 14 有限双槽端点／360° 包络交互 CAD

> **历史状态：pipeline rev=`147` 时 Gate 02 rev 14=`ready_for_review`。用户随后否决 groove-only 最大行程；rev 14 当前为 superseded/internal。**

## 历史：2026-08-26 Magnetic Slide Tile Gate 02 rev 13 闭合重合硬限位交互 CAD

> **历史状态：pipeline rev=`143` 时 Gate 02 rev 13=`ready_for_review`。用户随后否决 numeric-only stop 解释；rev 13 当前为 superseded/internal。**

## 历史：2026-08-26 Magnetic Slide Tile Gate 02 rev 12 旋转载体／顶片双槽交互 CAD

> **历史状态：pipeline rev=`136` 时 Gate 02 rev 12=`ready_for_review`。用户部分接受结构原理，并要求 rev 13 增加闭合硬限位。**

- 用户否决 rev 11 的底座双轨归属。当前合同改为光滑固定 `BottomExterior`、固定 `FixedAxis`、只绕轴旋转的内部 `RotatingCarrier`、左右 `CarrierFollower`、活动 `TopPlate` 及其背面两条内凹 `TopGroove`。
- 当前运动学为 `RotatingCarrier=R_fixedAxis(θ)`、`TopPlate=R_fixedAxis(θ)·T_local(s)`。顶片与载体共享 θ，局部滑动轴随 θ 旋转；固定轴与底壳不平移。
- 鼠标/触摸改为保留顶片局部抓取点并同时求解 θ 与 s。真实 pointer 测试覆盖 0° 向上、90° 向右、180° 向下、270° 向左，以及 zoom/pan 后和移动端方向一致性。
- 顶片最大合同视频行程仍覆盖固定轴。图示轮廓残余为 `0.22L`，仅用于 CAD 包络检查；真实最小盖轴余量、槽宽深、随动件截面、侧避空、厚度、间隙和公差继续为 unknown。
- 工作台同步显示顶视、侧视分层、A–A、顶片背面视图、九层组件树和半透明/爆炸控制。底壳外表面无轨道；HALOO 07 与 NXEDC 03/04 显式映射到旋转载体、顶片槽和随动件约束。
- CAD-only 审批清单为：pointer direction、fixed axis、rotating carrier、top underside grooves、compound motion、pivot coverage、smooth bottom exterior、source mapping。Simulator 页签仍为“交互 CAD 批准后生成”，active controls=`0`。
- 合同：`evidence/02-analysis/rev-012/mechanism-evidence-contract.json`，SHA-256=`9b9a4905a895ba102939f8f405ae17fae89a31159ef8f799b86219bead4a0f38`。
- CAD-only 预览：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate02-rev12-carrier-groove-cad.png`。DecisionState：等待工作台内 CAD 交互批准。DeliveryState：仅 web CAD 与测试；视觉批准待确认，未推送手机。

## 历史：2026-08-26 Magnetic Slide Tile Gate 02 rev 11 固定底座／固定轴交互 CAD

> **历史状态：pipeline rev=`133` 时 Gate 02 rev 11=`ready_for_review`。用户随后否决底座双轨归属；rev 11 当前为 superseded/internal。**

- 两张用户权威选图已不可变归档：`user-selected-bottom-base-close.png` SHA-256=`49d68c8ecfc52f3dce1cd74fe0e9ffc9483fe33929f73bb9b843f344b69a0b91`；`user-selected-bottom-base-context.png` SHA-256=`5b2f438cc748bba43ccb61a7eec5618f3632198455965bef63cce241ed67ec03`。
- 新合同：`ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-011/mechanism-evidence-contract.json`，SHA-256=`2f685c464db042392f4535fb5705f404e4c6e746adb590b9c020849f7a3cf40a`。rev 8 合同与 rev 10 CAD 配置保留为 internal/superseded。
- 当前层级：`BottomBase=identity`；`AxisModule`、`LeftRail`、`RightRail` 为 BottomBase 固定子件；`TopPlate=T(s)*R(axisFixed,θ)`；`UnknownTopUndersideContacts` 只作红虚线候选。轴心局部/世界位置均恒定，没有路径或第三 DOF。
- 工作台默认进入 CAD-only。顶/侧/A–A、七层组件树、半透明/分层控制、固定轴读数、空白实体尺寸字段和 18 项参考同步；`AxisCarrierCandidate` 单列为 unknown，两张新图显示“已应用到：底片主体 / 轴心模块 / 左右双轨”。Simulator 页签继续显示“交互 CAD 批准后生成”，active controls=`0`。
- 浏览器证据：真实 pointer 手势得到 `s=0.389L, θ=222.4°`，同时 BottomBase transform=`identity`、axis local==world、railOwner=`BottomBase`；8/8 CAD 清单解锁。desktop/mobile、zoom/pan/reset、layer controls、图片 modal、IMG_6022 playback 与 source mapping 均通过。
- CAD-only 预览：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate02-rev11-fixed-bottom-cad.png`。DecisionState：等待工作台内 CAD 交互批准。DeliveryState：仅 web CAD 与测试；视觉批准待确认，未推送手机。

## 历史：2026-08-26 Magnetic Slide Tile Gate 02 rev 10 结构交互 CAD

> **历史状态：pipeline rev=`129` 时 Gate 02 rev 10=`ready_for_review`。用户随后以两张权威选图否决其固定上片／活动底片／移动世界轴模型；rev 10 当前为 superseded/internal。**

- 固定顺序已写入 AGENTS、pipeline skill/contract 和程序合同：参考研究 → 结构交互 CAD → CAD 子批准 → 独立手感 Simulator → Simulator 批准 → Blender 与后续 Gates。
- CAD 配置：`ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-010/interactive-cad-geometry-config.json`，SHA-256=`a8507071180684e05e33ee22c59a94c3ec56a8f29d6622a62e2b1033383d1e99`。它读取 evidence contract SHA-256=`3b3f494805b2241f865bfdad5ec32a64ea95d03165714b55a272d81f0c1437a2`，不含手感参数。
- 工作台默认打开交互 CAD。它显示固定上片、活动底片、底片下端圆帽中心固定轴、双侧轨道、候选接触区、顶视/侧视/A–A、相切、中心线、开闭限位、归一化尺寸和空白实体测量字段。直接拖动可同时改变 `s+θ`；该交互是纯运动学，不运行阻尼、力感、档位强度、惯性、声音或止点手感。
- CAD 审批只要求检查顶视、侧视、A–A、完整行程、多滑位旋转、固定端点轴和来源→约束映射。批准事件记录 CAD hash、合同 hash、几何参数快照、已检查视图、清单和浏览器时间戳。CAD 批准只解锁独立 Simulator 生成，不批准 Gate 02，不解锁 Blender。
- `Simulator · 锁定` 顶层页签显示“交互 CAD 批准后生成”，无 active controls。rev 9 合并的 CAD/Simulator 配置保留为 internal/superseded，不再暴露；未生成 Simulator 录屏。
- 验证：Node/mechanism/pipeline tests=`55/55`；全 pipeline validator=`errors/missingFiles/unhashed 0/0/0`；真实 desktop pointer 复合拖动得到 `s=0.389L, θ=46.4°`，7/7 CAD 清单解锁，zoom/pan/reset、16 项参考、图片 modal、IMG_6022 playback、390×844 mobile/touch layout 均通过。CAD-only 预览：`Artifacts/ModelProvenanceExplorer/magnetic-slide-gate02-rev10-cad-only.png`。
- DecisionState：等待用户在工作台内完成 CAD 几何检查。DeliveryState：CAD-only web workbench ready；Simulator/Blender/Unity/runtime/Haptic/build/install/device acceptance 均未开始。视觉批准待确认，未推送手机。

## 历史：2026-08-26 Magnetic Slide Tile Gate 02 rev 8 可执行参考约束合同

> **当前状态：pipeline rev=`126`。Gate 01=`approved`，Gate 02 rev 8=`ready_for_review`，Gate 03–11=`stale`，Gate 12=`blocked/rejected`，approved count=`1/12`。Gate 02 批准前锁定交互 CAD。未编辑 Blender/Unity runtime，未构建、安装或推送手机。**

- 新权威合同：`ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-008/mechanism-evidence-contract.json`，SHA-256=`3b3f494805b2241f865bfdad5ec32a64ea95d03165714b55a272d81f0c1437a2`。
- 合同从 `131` 项哈希来源生成：Gate 01 全部 `49` 项、IMG_5961 与 12 张派生帧、10 张 Obsidian 帧、6 张 NXEDC 图、8 张 HALOO 官方图、三段银色同款视频共 `1727` 个 PTS 帧、rev 3 逐帧／tracking／音频证据，以及 Chrome Hearts 艺术补充。Chrome Hearts 明确只作艺术语言补充，不作机构证据。
- `15` 条 schema-backed 约束均包含 value/range、单位、evidence state、可信度、source asset IDs、frame/PTS regions、decision note 和 downstream consumers。`13` 项覆盖矩阵明确支持、已化解冲突和 unknown。
- 当前待批准约束：固定上片；活动底片；端点轴刚性属于底片且不局部滑动；同时 `s+θ`；底片反面双侧轨道；单向外开并原路关闭；`0.38–0.46L`、峰值 `0.50L`；360° 用户权威；`30×12°`；部分与近最大滑位视频支持。隐藏耦合、实体尺寸、力值和公差仍 unknown。
- 工作台默认显示“结论已如何应用”和来源→约束覆盖矩阵。全部原图与拆解参考保持顶层一键可达；每张卡显示 `已应用到`。逐帧／音频技术证据单独收起，无默认截图墙。
- 交互 CAD 当前为 locked。未来 CAD、Blender、Unity、Haptics、tests 和 shipping review 必须读取该合同并携带其 SHA-256。`mechanism-sandbox-core.mjs` 已删除证据硬编码，要求合同配置和显式测试／用户 tuning；duplicate-default drift 会失败。
- DecisionState：等待用户确认这些来源推导约束是否足以解锁 CAD。DeliveryState：仅参考合同、工作台与测试；CAD／Blender／Unity／runtime／Haptic／build／install／device acceptance 均未开始。视觉批准待确认，未推送手机。

## 历史：2026-08-26 Magnetic Slide Tile Gate 02 rev 7 固定端点轴与原图入口

> **当前状态：pipeline rev=`123`。Gate 01=`approved`，Gate 02 rev 7=`ready_for_review`，Gate 03–11=`stale`，Gate 12=`blocked/rejected`，approved count=`1/12`。rev 6 因轴心看似可在底片内滑动且原始同款参考入口不清楚而退回。未编辑 Blender 或 Unity，未构建、安装或推送手机。**

- 轴心局部位置改为归一化胶囊下端圆帽中心：`[centerX,bottomY-radius]`。其纵向位置为 `1-1/(2*(L/W))`，在 `L/W=1.52–1.62` 时距顶端约 `0.671–0.691L`；默认 `1.57` 为 `0.682L`。未使用任意像素或已否决毫米值。
- `axisLocalToLower` 在所有姿态中恒定。底片整体平移时 `axisWorld delta == lower translation`；底片旋转时 axis drift=`0`。不存在独立 axis DOF。CAD 明示“轴心只随底片整体移动，不在底片上滑动”。
- simultaneous 2-DOF 保留：固定上片不动；活动底片沿固定上片长轴平移，并绕已平移的固定端点轴旋转。同一次 mouse/touch drag 仍可同时改变 `s/θ`。
- 双侧轨道继续作为两片间相对约束。轴心、双轨、侧视和 A–A 均保持底片局部附着；固定上片坐标系中的虚线路径只表示整个底片的 translation path。
- 顶层新增 `结论 / 交互 CAD / 原图与拆解参考` 三页签。参考页含 `16` 项：三段用户视频及关键时间、HALOOPLAYER 官方弹簧球件／自由旋转／内部拆解／直推图、NXEDC 候选总览／打开斜视／内部近照／多配色打开图、官方机构板和五项既有内部裁切。每项显示来源分类、原始 URL、仓库路径和完整归档动作。
- 验证：CAD/机构 deterministic tests=`30/30`，完整 Node=`45/45`；桌面和 390×844 真实 pointer/touch compound、端点轴局部不变量、world delta、零轴漂移、无 axis DOF、reference tab/source modal/video playback/mobile/modal return 和 pipeline validators 均通过。
- 预览：`ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-007/workbench-browser.png`。DecisionState：等待用户确认固定端点轴与参考入口。DeliveryState：仅分析工作台和测试；Blender／Unity／runtime／Haptic／build／install／device acceptance 均未开始。视觉批准待确认，未推送手机。

## 历史：2026-08-26 Magnetic Slide Tile Gate 02 rev 6 交互 CAD 机构图

> **当前状态：pipeline rev=`121`。Gate 01=`approved`，Gate 02 rev 6=`ready_for_review`，Gate 03–11=`stale`，Gate 12=`blocked/rejected`，approved count=`1/12`。rev 5 因真实旋转不可用而退回。未编辑 Blender 或 Unity，未构建、安装或推送手机。**

- 故障根因已用真实 Chrome mouse input 复现：`756×469` viewport 中旧 SVG 高 `560 px`，拖拽起点／轴心可落在可视区外；旧 browser test 直接向节点派发合成 PointerEvent，绕过 viewport hit testing；旧图也没有独立旋转环。复现结果为 `travel=0`、`angle=0`。
- rev 6 使用短视口自适应矢量 CAD。顶视、侧视、A–A 双轨／轴心剖面和证据组件树共享同一 `upper=I`、`lower=T(s)·R(A,θ)`、`A_world=A_lower+T(s)` transform。
- 默认机构操控为 2-DOF 联动，不再拆分滑动／旋转模式。同一次下片 body drag 保留抓取局部点：纵向分量改变 `s`，切向分量同时改变 `θ`；大圆环只作精确旋转副手柄。所有用户授权滑位可转是用户权威规则；视频分别只证明部分／近最大滑位。
- 线性速度与角速度并行。角度 detent capture 不阻止滑动；行程 clamp 不阻止旋转。支持平移图纸、wheel/button zoom、pointer capture、键盘 `0°→12°→36°`、反向分档和双速度归零 reset；顶视显示实时 2-DOF path trace。
- CAD 标出胶囊相切点／弧、中心线、双轨、轴心、30 档环、行程限制、闭合缝隙、层厚、台阶和隐藏候选。绿/青实线=`实测/用户输入`，琥珀=`视频比例`，红虚线=`未知候选`。
- 15 个物理输入默认空白：总长宽厚、上下片厚度、闭合缝隙、轨距、轨宽、轴径、上下台阶、间隙、加工余量、公差和毫米行程。缺值显示 `? / 待实测`；只有完整输入才派生 L/W、行程/L、厚度栈余量和轨道边缘余量。
- 验证：CAD/机构 deterministic tests=`27/27`，完整 Node=`42/42`；真实桌面单次斜向 mouse drag 同时改变 `s/θ`，并完成 zoom→pan→非零滑位 ring 旋转；partial/max compound、边关闭边反向旋转、滑动中 detent capture、translation-only clamp、双速度 reset 均通过；390×844 单次 touch compound 和 ring rotation 通过。opacity、参数 unknown/derived、modal return、H.264 视频和 pipeline validators 全部通过。
- 预览：`ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-006/workbench-browser.png`（`1440×3281`）。技术截图／视频墙继续收起。
- DecisionState：等待用户确认旋转是否可用及 CAD 机构是否符合实物。DeliveryState：仅分析工作台和测试；Blender／Unity／runtime／Haptic／build／install／device acceptance 均未开始。视觉批准待确认，未推送手机。

## 历史：2026-08-26 Magnetic Slide Tile Gate 02 rev 5 机构所有权修正

> **历史状态：pipeline rev=`118` 时 Gate 02 rev 5=`ready_for_review`。用户随后因真实浏览器不能可靠旋转而退回；机构所有权结论继续沿用。**

- 精确运动模型：固定上片 `M_upper=I`；活动下片 `M_lower=T(s)·R(A_lower,θ)`；轴心世界位置 `A_world=A_lower+T(s)`。轴心与下片平移严格相等，rotation pivot=`A_world`，pivot drift=`0`。
- 下片反面显示左右两条纵向滑轨／珠列区。双轨、轴心和下片共同平移、旋转；上片只显示半透明虚线“接触候选区”，不虚构隐藏随动件。
- 工作台默认内部 opacity=`0.72`，可调 `0.15–1.00`。实时值包含下片平移、轴心世界位置、角度、档位和状态。尺寸只用 `L/W=1.52–1.62`、行程 `0.38–0.46L`／峰值 `0.50L`；可选实测字段保持空白。
- 分档姿态 `0°/12°/36°` 保持 `travel=0`；滑动检查姿态为 `+0.21L/0°`，不把历史 `21 mm` 当作当前事实。
- 验证：机构核心 `13/13`；完整 Node `28/28`；pipeline 与单模型 validator 均为 `errors/missingFiles/unhashed=0/0/0`。浏览器 pointer 滑动／旋转、上片 transform 恒定、轴心位移、双轨归属、opacity、reset、390×844、modal 返回、H.264 播放均通过。
- 全页预览：`ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-005/workbench-browser.png`（`1440×2720`）。默认无截图墙；完整逐帧／音频证据收起。
- DecisionState：等待用户确认半透明双轨和移动轴心是否符合实物。DeliveryState：仅分析工具与测试；Blender／Unity／runtime／Haptic／build／install／device acceptance 均未开始。视觉批准待确认，未推送手机。

## 历史：2026-08-26 Magnetic Slide Tile Gate 02 rev 4 结论式机构沙盒

> **历史状态：pipeline rev=`116` 时 Gate 02 rev 4=`ready_for_review`。用户随后退回固定／活动片所有权、中央单轨和不随下片移动的轴心表达；逐帧／音频证据继续保留。**

- 用户评审改为双层。默认层只显示 6 条结论、可信度、单行影响、3 项未知和 1 个决定；截图、完整视频、逐帧板和音频图位于收起的“技术证据”。
- 比例修正：当前只使用 `L/W=1.52–1.62`、沙盒中值 `1.57`、行程 `0.38–0.46L` 和峰值 `0.50L`。实体长、宽、厚和毫米行程均为 unknown；可选测量字段默认空白。
- `tools/model-provenance-explorer/mechanism-sandbox-core.mjs` 是独立确定性物理核心。它实现 `30 × 12°`、零自转、半衰期阻尼、breakaway、detent capture、单向外滑、原路关闭、软／硬止点、行程 clamp、角度 wrap 和零角速度 reset。
- 工作台“机构手感沙盒”支持 pointer 滑动／旋转、部分与近最大滑位旋转、实时行程／角度／档位／状态、滑动／旋转阻力、档位吸附、起步门槛、阻尼、惯性半衰期、行程、止点柔和度和可选声音。
- 边界：沙盒未证明每个精确滑位均可旋转，也未定义隐藏轴销、槽壁或耦合。桌面只模拟动作滞后、吸附和声音；真实受力、磁力和手机 Haptic 仍须设备验证。
- 验证：确定性机构测试 `8/8`、完整 Node 测试 `23/23`。桌面 pointer 滑动／旋转、实时值、reset、控件、390×844 单列、modal 关闭／Escape／backdrop／browser Back、H.264 `720×1280 / 14.214 s / error=null` 均通过。pipeline validators 为零 schema error、missing file 或 unhashed asset。
- 全页工作台预览：`ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-004/workbench-browser.png`（`1440×2606`）。技术验证：同目录 `validation-report.json`。
- DecisionState：Gate 02 rev 4 等待用户试用后确认滑动方向、轴心位置和 30 档旋转。DeliveryState：分析工具已实现并通过独立单元测试；产品 Blender／Unity／runtime／Haptic／build／install／device acceptance 均未开始。视觉批准待确认，未推送手机。

## 历史：2026-08-26 Magnetic Slide Tile Gate 02 rev 3 逐帧机构评审

> **历史状态：pipeline rev=`113` 时 Gate 02 rev 3=`ready_for_review`。用户随后退回其截图墙式表达和会暗示精确尺寸的示意图；完整逐帧／音频证据继续作为 rev 4 内部层保留。**

- 用户输入分类已批准并逐字记录：“三段视频拍摄的是与目标完全相同的产品，仅花纹和纹路不同。视频用于逐帧确认轴心、滑轨、单向推动、最大行程、任意角度旋转和棘轮玩法。”
- 原始 MOV 保持不变：IMG_6022 SHA-256=`4b6afee0737f4ea1988870de2da721e0487531e20422cae89045da10b0b3ebfe`／426 帧／14.2067 s；IMG_6023=`e10ba02fe9fecf46b2acee7b32a1658135b22f9e06b166902460c45609c8a92c`／480 帧／16.0083 s；IMG_6024=`dd92dc36a5fe36137e43aff1cb4d5b8f3c81721b2d4258395d29702a6defa6b5`／821 帧／27.3817 s。三段均为 1920×1080 HEVC、`-90°` display rotation、约 29.97 fps、AAC stereo 48 kHz。
- 永久证据：每段视频均有逐帧 JSON/CSV PTS 清单、全片帧调查板、5 ms RMS 音频候选 CSV/图、720×1280 H.264/AAC 浏览器代理；另有 `38` 张带 frame index、PTS 和 SHA-256 的紧裁关键帧。
- 主评审板：`evidence/02-analysis/rev-003/three-video-timeline-board.png`、`plate-identity-board.png`、`one-way-slide-sequence-board.png`、`rotation-and-audio-board.png`、`axis-slot-hypothesis-board.png`、`contradiction-board.png`。默认只问“这个玩法/机构解读是否符合真实玩具？”，技术细节收起，完整视频可播放。
- 当前解释：两片受复合轴心／纵向轨迹约束；`M` 是机构承载片，`C` 是活动盖片；从闭合止点只朝一个外向方向打开并可原路返回；行程约 `0.38–0.46L`、峰值约 `0.50L`；12° 每档／30 档每圈获强支持；部分与近最大滑位均见旋转；反向滑回成功，未证明机械卡死。
- 边界：现有 `21 mm` 只与视频归一化范围相容，不是新毫米测量。视频直接覆盖可逆 `0↔180°` 和约 `170°`；完整 `360°` 仍为用户权威陈述。隐藏轴销归属、槽壁截面、耦合、公差和每个精确槽位的旋转可达性继续 unknown。
- 面别冲突已拆开：`M` 的正常外观面可保持干净；其反向／机构面可暴露两颗 Torx、轨道和珠列。旧“干净面”不能再扩写为“零件没有可暴露的机构面”。
- 验证：Model Provenance Explorer tests=`15/15 passed`；model validator 返回 revision=`113`、approved=`1/12`、errors/missingFiles/unhashed=`0/0/0`；全 pipeline validator 对该模型同样为零错误。Python `py_compile`、Node syntax checks 全部通过。
- 浏览器：桌面六张评审板、三条视频入口、图片 modal、关闭／Escape／backdrop／browser back 全部通过；390×844 单列无横向溢出；IMG_6022 H.264 代理读取 `720×1280 / 14.214 s` 且 `video.error=null`。截图：`evidence/02-analysis/rev-003/workbench-browser.png`。
- DecisionState：Gate 01 同款机构／仅外观差异分类已锁定；Gate 02 机构解释等待用户确认。DeliveryState：仅证据与规格，Blender／Unity／build／install／device acceptance 均未开始；视觉批准待确认，未推送手机。

## 历史：2026-08-26 Premium Display Case Gate 05 批准／Gate 06 rev 3 待审批

> **当前状态：pipeline rev=`60`。Gate 01–05=`approved`；Gate 06 geometry rev 3=`ready_for_review`；Gate 07–08=`stale`，Gate 09+=`blocked`；approved count=`5/12`。视觉批准待确认，未推送手机。**

- 用户选择“正确，批准并继续（推荐）”。Gate 05 approval event=`6c6e15cb-1479-40ae-9e4e-baa4c62199b2` 锁定现有 `228 × 304 × 59 mm` 白模、闭环管、label Y=`99 mm`、三组同心圆角、PresentationRoot identity pivot／root hierarchy 与 caller-owned 空 `ContentSlot`。
- Gate 05 批准不授权 light／VFX／proxy／toy geometry。Blender 只拥有 geometry、pivot、UV 与 material zones；Unity `PresentationRoot` 继续拥有 runtime motion。shipping Unity、Simulator、build、install 与 phone 均未触碰。
- Gate 06 rev 3 event=`571968fc-16cc-4232-ba03-9ad8c9860036`。真实 Blender 5.2.0 LTS 从获批 Gate 05 rev 3 blend 原样重验；source geometry digest=`6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f`。只重放既有闭环管 face-winding correction，evaluated digest=`a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951`；vertex 与 silhouette digest 均保持不变。
- 六张 Workbench 正交视图、标准 10 视图 capture、真实 Workbench、尺寸 overlay、PresentationRoot ownership overlay 与 review-only interactive GLB 均从同一保存 blend 生成。主评审板和全部 `reviewArtifactIds` 只显示 assembled whole case。
- 五个 subject mesh 的 signed volume 均为正；闭环管净 signed volume=`52932.982745 mm³`，outer normals 朝材料外，inner normals 朝 lumen。开放／non-manifold／self-intersection／degenerate=`0/0/0/0`；connected tube flood-fill=`384/384`；corner-center drift=`0.000 mm`。
- Gate 04 rev 7 ownership 复核通过：Unity 只能移动 `PresentationRoot`；`CaseAssembly` 与 `ContentSlot` 保持 rigid、same-instance、whole-case，Blender 无 baked runtime animation。本 Gate 不含 animation timing、light tuning、material 或 shipping implementation。
- 历史 `premium-display-case-geometry-exploded-r002` 仅保留为内部技术 `artifactId`，不在 `reviewArtifactIds` 或主板。review exploded part count=`0`。
- 评审：`ArtSource/ModelPipeline/premium-display-case/evidence/06-geometry/rev-003/premium-display-case-gate06-review-r003.glb`、`geometry-presentation-review.png`、`geometry-workbench.png`、`dimension-overlay.png`、`pivot-presentation-root-overlay.png`。
- 验证：Gate 06 source/render/review validator 全 pass；focused Premium Display Case test=`1/1 passed`；model validator rev=`60`、approved=`5/12`、earliest=`06-geometry ready_for_review`、errors／missingFiles／unhashed=`0/0/0`；全 pipeline validator 对该模型同样零错误；Python／Node syntax 与 task-scoped diff check 通过。
- Model Provenance Explorer 全套=`55/56 passed`。唯一失败属于并发 magnetic-slide：`mechanism-evidence-contract.test.mjs` 仍期待 contract SHA `9b9a…`，实际为 `563b…`；本任务未修改该 feature。
- DeliveryState：Gate 05 白模兼容关系已锁定；Gate 06 仅完成 geometry／presentation 复核并等待用户交互视觉批准。Gate 07+ 保持 stale/blocked。视觉批准待确认，未推送手机。

## 历史：2026-08-26 Premium Display Case Gate 04 rev 6 平滑交接

> **历史状态：pipeline rev=`53` 时 Gate 04 rev 6=`ready_for_review`。用户随后保留 bounded overlap，但否决超出盒体 silhouette 的过光；该版本现为 rejected/superseded。**

- 用户原话“对，然后也不用完全停完再原地转一圈。”已通过 workflow API 记录。rev 5 的同一真盒、Pack／Toy／LightController ownership 与四段有限光效继续有效；仅“translation 完全归零后才旋转”的硬边界被拒绝并保留为历史。
- rev 6 只允许一个 controlled overlap window：盒体必须先明显越过 Pack，Y+camera-depth-Z 入场进入减速尾段后，才可开始早期 local-Y `360°`。overlap 结束后 translation 锁定；入场仍是主动作。
- overlap start threshold、duration 与 rotation-onset curve 均保持 null／待调。评审示意使用 `entry progress=0.82`、`0.16 s`，只用于看清交接，不产生批准效力。
- X drift、roll、pitch、独立 scale、相机／背景／toy motion、无界多轴同时运动、proxy、split、explode、粒子与 persistent light loop 均为零／禁止。Toy 仍由调用方拥有、通过 ContentSlot 附着、独立角速度为 `0`。
- 光效 ownership 不变：entry 期间 seam leak；入场／旋转交接附近 arrival rim；旋转期间 object-bound rim；最终一次 sheen + 短 halo 后全部归零。
- 用户评审只包含整盒 board、GIF 与 contact sheet。rev 5 part tree／exploded plan 继续作为 internal `artifactIds`，不进入 `reviewArtifactIds`。
- 验证：确定性 generator 复跑通过；Node tooling tests=`45/45`；单模型与全 pipeline validators 均为 `errors/missingFiles/unhashed=0/0/0`。未编辑 shipping Unity，未构建 Simulator，未安装或推送手机。
- 预览：`ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-006/whole-case-overlap-architecture-review.png`、`whole-case-overlap-motion.gif`、`whole-case-overlap-contact-sheet.png`。
- DecisionState：其 bounded overlap 关系由 rev 7 保留；外扩 halo 被否决。DeliveryState：历史 Gate 04 架构评审证据；未推送手机。

## 历史：2026-08-26 Premium Display Case Gate 04 rev 5 架构

> **历史状态：pipeline rev=`51` 时 Gate 04 rev 5=`ready_for_review`。用户随后保留 ownership 与 light relationships，但否决“完全停稳后才旋转”的 hard pause；该版本现为 rejected/superseded。**

- Gate 03：用户选择“批准合同并继续（推荐）”。event=`ce83f60e-e315-42e8-b89b-82d4c5a02461` 锁定同一 assembled 真盒、Y+camera-depth-Z 入场、完全停稳、translation-locked local-Y `360°`、克制因果光效与静止 hold。`3.4 s` 仍只是评审 placeholder；shipping duration、easing、Y/Z distance、light tuning 与 camera 保持 unknown。
- Ownership：`PresentationRoot` 独占盒体 motion；`CaseAssembly` 从首个可见帧到 ACK 始终为同一 rigid assembled instance；Pack 前景／tear／handoff 由外部 `NativePackOwner` 拥有，不创建 case proxy；`ContentSlot`／Toy 继续由调用方拥有，独立角速度=`0`。
- 串行阶段：prepare → Y+Z entry（rotation=`0`）→ settle（translation/rotation velocity=`0`）→ translation-locked local-Y `360°` → final light → static hold。entry 与 showcase 不重叠。
- 光效：`RestrainedLightController` 恰好拥有四个 finite cues：Pack seam、arrival rim、object-bound rotation rim、final sheen + short halo。particle emitter count=`0`；VFX Graph、persistent loop、rarity color、flash、shake 与大 bloom 继续禁止。
- 用户评审：`ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-005/whole-case-architecture-review.png`（`3200 × 3900`）是唯一 `reviewArtifactId`，只显示 assembled case、ownership 与 phase arrows。
- 内部证据：`part-tree-internal.svg` 与 `exploded-plan-internal.svg` 只在 `artifactIds`，明确 `reviewEligible=false`／`productAnimationEligible=false`，不得进入产品路径或用户主评审。
- 可复现源：同目录 `generate_serial_architecture_review.py`、`architecture.json`、`architecture-validation.json`、`gate03-approval-scope.md`。event=`8b5bc452-b5c5-4f48-a0a4-66df8d49e9c2` 登记 Gate 04 review；历史 Gate 04 rev 1–4 原样保留为 stale。
- 验证：generator 二次运行 SHA-256 完全一致；Python `py_compile` 与 Node syntax check 通过；Model Provenance Explorer tests=`28/28 passed`；model validator rev=`51`、approved=`3/12`、earliest=`04-architecture ready_for_review`、errors/missingFiles/unhashed=`0/0/0`；全 pipeline validator 无错误；本任务文件 `git diff --check` 通过。仓库全局 diff check 仅命中本任务外既有 prefab／scene 尾空格。
- DeliveryState：仅合同／架构证据；未修改 Blender、shipping Unity、Simulator、build、install 或 phone。Gate 05 在明确批准 Gate 04 前保持 blocked。视觉批准待确认，未推送手机。

## 历史节点：2026-08-26 Premium Display Case Gate 02 rev 6 动效与光效批准

> **历史状态：用户选择“批准这版动效与光效（推荐）”。pipeline approval event=`2954e46c-c428-465a-9e4d-a0f602f75c96`；该方向现由 Gate 03 rev 3 合同消费。shipping-source 预览与设备验收仍未批准，未推送手机。**

- 用户原话：“对，就是这个意思。节奏上面，你再加一些我之前让你做的游戏调研上的这种光效变化，结合一下就好了。”
- Motion 保持 rev 5：入场 screen Y + camera-depth Z；停稳后一次 local-Y 360°；translation/rotation overlap frames=`0`；最终一次 sheen 与静态 hold。
- 光效因果链：Pack 开口一次窄中性漏光 → 真盒越过 Pack 时一次小型 arrival rim → 360° 期间仅 object-bound turning-surface rim → 最终一次斜向窄 sheen + 最大 alpha=`0.094118` 的中性 settle halo → 全部归零。
- 色彩与焦点：所有光色 maximum RGB chroma=`25`，不传递 rarity；focal subject count=`1`。无 rainbow、rarity 色、全屏 flash、大 bloom、粒子、VFX Graph、额外相机、RenderTexture、screen-space post、爆炸、闪电、CRT noise、confetti、screen shake 或 persistent loop。
- 评审证据：`ArtSource/ModelPipeline/premium-display-case/evidence/02-analysis/rev-006/restrained-light-evolution-analysis-board.png`、`balanced-motion-restrained-light.gif`、`balanced-motion-restrained-light-contact-sheet.png`。
- 自动验证：one subject、serial phases、one 360、zero simultaneous translation/rotation、no replacement、no toy motion、neutral color bound、one seam／arrival／surface-rim／sheen／halo、final cue values=`0` 全部通过。Model Provenance Explorer tests=`15/15`；model-specific validator rev=`46`、approved=`2/12`、earliest=`03-contract stale`、errors/missingFiles/unhashed=`0/0/0`；全 pipeline validator 无错误。
- 批准范围：`rev5-serial-motion-structure`、`rev6-restrained-causal-light`、Y+camera-depth-Z 入场、停稳后一次 local-Y 360°、object-bound rotation rim、一次 final sheen／短 halo，以及既有禁止项继续生效。
- 时长边界：`3.4 s` 只批准为 Gate 02 评审节奏；`shippingDurationApproved=false`。最终 easing、运行时参数和 shipping 总时长仍需 Gate 03+ 合同与真实实现预览。
- 粒子边界：本次明确未批准粒子。rarity color、rainbow、large bloom、particles、VFX Graph、full-screen flash、explosion、screen shake 与 persistent loop 继续禁止；若以后增加粒子，必须重新走视觉审批。
- DeliveryState：这是已批准的分析／设计方向，不是 shipping-source preview、Simulator 验收或 iPhone device acceptance。后续 Gate 03 rev 3 已生成并等待审批。

## 历史：2026-08-26 Premium Display Case Gate 02 rev 5 中间平衡候选

> **历史状态：rev 5 motion structure 先获用户方向确认；rev 6 保持动作结构不变，只增加克制、因果明确的光效处理。用户随后批准 rev 6，Gate 02 当前已完成。**

- 用户原话：“那你这个也太简单了……没有 Z 轴的这种移转，也没有 360° 翻转……不能说找一个中间的平衡吗？”
- rev 5 串行节奏：① assembled 真盒沿 screen Y + camera-depth Z 从 Pack 后方入场，入场 rotation=`0`；② 完全停稳后 translation 锁定，只做一次 local-Y `360°` 刚性展示；③ 一次窄高光并静止 hold。
- 明确禁止：X drift、roll、pitch、独立 model scale 动画、相机／背景／toy motion、平移旋转同时发生、split、explode、proxy 与对象替换。
- `3.4 s` 只用于当前节奏评审，不锁 shipping 总时长，不恢复 rev 3 的 `4.520833 s`。
- 评审证据：`ArtSource/ModelPipeline/premium-display-case/evidence/02-analysis/rev-005/balanced-entry-showcase-analysis-board.png`、`balanced-entry-showcase-motion.gif`、`balanced-entry-showcase-contact-sheet.png`。
- 自动验证：entry axes=`screen-y,camera-depth-z`；entry rotation keys=`0`；360 showcase count=`1`；translation/rotation overlap frames=`0`；X/roll/pitch=`0`；model scale=`1`；highlight count=`1`；object replacement／toy motion=`0`。全 pipeline validator 无 schema、缺文件或 hash 错误。
- Gate 03 rev 2 rigid best-fit 合同保留为历史 artifact，但因消费 rev 3 claims 已 stale；Gate 02 rev 6 已批准，下一步需要生成消费当前 10 条 active claims 的新 Gate 03 合同。

## 历史：2026-08-26 Premium Display Case Gate 03 刚体运动合同 rev 2

> **历史状态：pipeline rev=`42` 时 Gate 03 contract rev 2 曾为 `ready_for_review`；用户随后要求 Z-depth 入场与一次 360° 的中间平衡，rev 2 当前已 stale。该合同未获用户批准，未修改 Blender geometry/material、shipping Unity、构建、安装或手机。**

- Gate 02 API 决策：rev 40 保存“只纠正动画；静态结构保留”“整盒刚性；用 pitch/yaw/roll 复合翻转”与“继续”；event=`5793f64f-b182-49a7-87b0-b5d590591077`。rev 41 批准 Gate 02 rev 3 measured-motion evidence；event=`ab12f5c4-453b-4ad0-8871-41e4eb9393bc`。批准不包含物理 Y/X 单轴、任何 single-axis claim、Rive mesh deformation、explode 或 Toy 变更。
- Gate 03 API 事件：rev 42 event=`2b7cc0b2-da1f-41e7-8731-e4464bcb0f56`。合同消费全部 `11` 条 active Gate 02 rev 3 claims；Gate 03 未自动批准，Gate 04 未进入。
- 静态值按用户 motion-only 选择保留：`228 × 304 × 59 mm`、Portrait=`0.75`、闭环管 `10 × 9 mm`、通道 `6 × 5 mm`、壁厚 `2 mm`、R20、标签 `184 × 58 mm @ Y=99 mm`、`ContentSlot 180 × 198 × 48 mm`、三组解析同心圆角与既有 PBR 范围。Toy／prize 继续由调用方通过 `ContentSlot` 提供，geometry、material、artwork、pivot、physics、Haptic 和 mechanism 均未改。
- 刚体 fit：九个真实 Rive 样本分别输出 normalized WXYZ quaternion、同一 cuboid origin 的 camera-space translation、`uniformScale=1`、framing 与逐角 residual。全 `36` 个角点 mean／RMSE／max=`6.780574 / 11.241096 / 38.343513 px`；未裁切样本 mean／max=`2.938339 / 8.840549 px`。最大误差来自上沿裁切的 `QUARTER`；合同明确为 best-fit，不声称 exact。
- 相机假设：固定 pinhole、`968 × 660`、principal point=`(484,330)`、square pixels、零畸变；全样本 least-squares grid 得到 diagnostic vFOV=`71.75°`。该值只用于 Rive quad 拟合，不是 shipping 相机；历史 shipping `27–31°` 范围仍待后续重验证。
- 时序：canonical Rive root=`210f @ 60fps = 3.500000 s`；只做统一 time-scale `1.291666571429`，总时长精确为 `4.520833 s`。entry、front-to-edge、edge-to-reverse、reverse-to-front、单次高光窗口与 hold 保持来源顺序和相对时序；不新增停顿或第二次高光。高光与完成后悬浮仍是下游验证段；奖品独立角速度为零。
- 主评审：`ArtSource/ModelPipeline/premium-display-case/evidence/03-contract/rev-002/contract-preview.png`，`3200 × 4300`，只显示 assembled whole case。技术证据为 `rigid-pose-contact-sheet.png`、`rigid-motion-curves.png`、`rigid-motion-fit.json`、`rigid-motion-fit-validation.json` 与 `modeling-contract.json`。
- CV validation=`pass`：pose 数=`9`、quaternion normalization、正深度、scale=`1`、残差复算、clipped-source 标记、no-axis-overclaim、mesh-deformation exclusion、whole-case/no-explode、exact duration、claim consumption、图片尺寸／非空均通过。
- 自动验证：Model Provenance Explorer core tests=`15/15 passed`；model-specific validator 返回 revision=`42`、approved=`2/12`、errors／missingFiles／unhashed=`0/0/0`；全模型 pipeline validator 对 Premium Display Case 同样为零错误。三张 PNG 已人工检查：中文可读、overlay 图例与 residual 可见、主预览无 explode。
- 单一审批问题：是否批准 Gate 03 rev 2 的静态保留值与有明确 residual 的整盒 rigid quaternion best-fit，从而允许下一轮进入 Gate 04？当前答案仍待用户确认。

## 历史：2026-08-26 Premium Display Case Gate 02 入场聚焦候选

> **历史状态：rev 4 曾把 screen-Y-only 入场登记为 `ready_for_review`。用户随后明确选择 rev 3 measured-motion 的整盒刚体复合翻转并回复“继续”；pipeline rev 40 已将 rev 4 assets／claims 标为 superseded history。**

- 用户反馈原文：“节奏感不对，然后感觉XYZ轴运动过多，过于复杂，我觉得主体是要表达入场，现在增加了过多的动销元素，让人感觉抓不住重点”。
- rev 4 候选只保留 screen-Y 入场、固定正面与 `2.2 s` 节奏；这些不再是当前合同。
- 评审证据：`ArtSource/ModelPipeline/premium-display-case/evidence/02-analysis/rev-004/entry-only-analysis-board.png`、`entry-only-motion.gif`、`entry-only-contact-sheet.png`。
- 自动验证：primary motion count=`1`；moving axes=`screen-y`；rotation keys=`0`；scale keys=`0`；highlight count=`1`；object replacement count=`0`；whole-case/no-explode 通过。全 pipeline validator 无 schema、缺文件或 hash 错误。
- 外部 CC0 Make It Shine iOS Simulator 研究包仍只作参考：其碎裂、爆炸、替身 Pack 与三卡代理切换不进入 Fidgeting shipping 流程。

## 2026-08-25 Premium Display Case Gate 02 真实 Rive 运动证据（现为 rev 41 批准来源）

> **当前处置：旧纯竖直 Y 轴解释继续 rejected。Gate 02 rev 3 measured evidence 已由 rev 41 API 决策批准；目标映射由 Gate 03 rev 2 限定为整盒刚体 best-fit，不把源 mesh deformation 或 Euler 分解升级为物理轴。**

- 决策历史：rejection event=`a73ca503-5b92-4a99-89b2-fe69f7f053d4`；Gate 02 rev 3 event=`cfc5020b-71fc-4582-8d91-b722cfa4a976`。旧 motion claim `display-case-analysis-flow-r002` 与五项 pure-Y artifact 已标记 rejected/superseded；Gate 03–08 文件与 hash 全部保留，只降为历史／待重验证。
- 真实 binding：shipping Swift 的 outer artboards 为 `background/mint-slab`／`foreground/mint-slab`，state machine=`Main`；bindable children 为 `Slab-rotate-v01` 与实际 `Coin_Slab_v09-sm`，child state machine=`State Machine 1`。此前 artifact 名称中的 “v15” 不是真实 child artboard version。
- Authored motion：root `in`=`210f @ 60fps = 3.500 s`。`0→29f` 两层从 screen X `−137.5 / 520` 汇入 `187.5`，screen roll 从 `−16.6517° / +26.8579°` 收敛到 `0°`，并带独立 scale、translation 与 cubic easing。`Slab-rotate-v01`=`60f / 1.000 s / ping-pong`，两条 side-sprite X track 均为 `1154.5→103.5`。
- Mesh deformation：`Coin_Slab_v09-sm` Timeline 1 包含 `456` 条 X/Y mesh track 与 `816` 个 keyframe；`89` 条 track 在 frame `0→60` 改变数值。目标覆盖 `350` 条 `MeshVertex` track 与 `106` 条 `ContourMeshVertex` track。这些是 2D mesh／sprite deformation，不是 3D Euler channel。
- 轴向结论：roll=`confirmed`；yaw=`apparent-pseudo-yaw`，只说明 front→edge→reverse→front 的视觉翻面；pitch=`unknown`；physical 3D axis／degrees／sign=`unknown`；X-axis replacement=`not-claimed`。用户截图四角测得 screen roll=`+19.8436°`、top/bottom=`1.322603`、left/right=`0.933310`；真实 Rive `200 ms` 是最近 landmark signature，但不是同 artwork 的 exact match。
- 时长边界：authored `3.500 s`、main App wall-time=`3.617 s`、standalone=`3.805 s` 继续分开记录。用户现已锁定总时长 `4.520833 s`；Gate 03 rev 2 使用 authored root 的统一 time-scale `1.291666571429`，不恢复旧 pure-Y frames。
- 评审证据：真实 Rive contact sheet=`ArtSource/ModelPipeline/premium-display-case/evidence/02-analysis/rev-003/real-rive-motion-contact-sheet.png`；大字 axis／perspective 板=`motion-axis-perspective-analysis-board.png`；测量 JSON=`real-rive-motion-measurements.json`；neutral whole-case GIF=`whole-case-measured-motion-schematic.gif`；schematic contact=`whole-case-schematic-contact-sheet.png`。
- Animation quality gate：`animation-quality-report.json`=`pass`。neutral schematic 为单一 connected whole case；最窄 edge=`43 px`；hold difference=`0`；yellow fraction=`0`；生成 `109` samples，GIF 合并 identical hold 后为 `22` encoded frames／`4,520 ms`。无 split、explode、reassembly、flicker、WHATNOT、黄色、笑脸、条码或样例编号。
- 本 task 的范围只包含收藏盒盒体与 presentation。`contentSlot` 中的 toy／prize 为调用方拥有内容；其 geometry、material、artwork、pivot、physics、Haptic 和 mechanism 均未获本 task 修改授权，也不得借展示盒修复顺带更改。
- 下一门禁：Gate 03 rev 2 只等待一个合同审批问题；未批准前不得进入 Gate 04。视觉批准待确认，未推送手机。

## 历史：2026-08-25 启动、抽卡连续性与展示盒 Gate 08 灯光评审证据（现因上游 motion correction stale）

> **历史状态：冷启动、Pack-to-case 因果交接和“收下”ACK 仍保持已集成与 focused tests 状态。以下 Gate 05–08 证据与批准记录继续不可变保留；pipeline rev 42 保持 Gates 04–08 stale。展示盒 motion、灯光隔离和相机调校仍未进入 shipping 代码。**

- 启动：`beginLibraryPreview()` 只启用 Library preview，不再发送 `SelectModelFromNativeUi`；首个 Unity progression payload 把 native selection 对齐真实已加载场景，且不会覆盖用户已开始的选择。`SpinnerProgression.Resume()` 在没有暂停键时不执行 `PlayerPrefs.Save()`；环境相同则跳过 `ApplyTheme`／IBL 重建；Gacha 只在已有 runtime 或已完成 rhythm week 时初始化。
- 抽卡：`GachaSingleDrawGateState` 当前阶段为 `choosingPack → selectionRive → tearPack → waitingForReceipt/preparingCase → handoff`。Pack commit、receipt、Unity setup 和 handoff 各为 exact-once；旧 callback 不能推进新 request。`ConfirmGachaRevealReadyAfterTwoFrames` 在真实 case、prize 和 camera 连续两个 end-of-frame 存在后才通知 Swift。
- 结果 UI：`PremiumDisplayCaseExperienceView` 的 Gacha 模式只组合 `ProductBottomActionDock`、`ProductScreenHeading`、`ProductStatusTag` 和 `ProductPrimaryActionButton`；root 应用 `productDesignSystem()`。loading 防重入后才发送同 request ACK。`AGENTS.md` 已加入 always-on shipping UI component-library gate。
- 自动验证：既有启动、Gacha bridge／gate、组件库结果 UI 与 Display Case source contract 组合 EditMode `24/24 Passed`（`/tmp/fidget-unified-focused-rerun.xml`）；新增 whole-case source contract EditMode `1/1 Passed`（`Logs/PremiumDisplayCaseWholeCaseSourceContract.xml`）。Swift gate harness `77/77 Passed`；九份 shipping Swift 以 iPhone 15 Simulator target 和 `-warnings-as-errors -typecheck` 通过；连续 capture script `zsh -n` 通过。Shipping 连续预览仍须在视觉 gate 后补证。
- 已知范围边界：当前 catalog 九个奖品中，真实 3D resolver 只支持 `canyon-heir-metal-three-blade`。其余奖品现在会保持 Pack 和 pending receipt，并收到明确 `unsupported-prize-content` setup failure，不再先清 native UI 后黑屏；在每个内容都有经批准的真实展示资产前，不得伪装成三叶金属或静默改概率。
- Gate 01 rev 1／2 评审图只保留拒绝历史。rev 3 目标图为 `ArtSource/ModelPipeline/premium-display-case/evidence/01-intake/rev-003/gate-01-target-preview.png`：明确拒绝四条独立 bar，要求一根 closed tubular loop、四角相切连续、单一 connected manifold、零开放边和任意入口可遍历完整通道的 flood-fill。该范围已获批准；没有因此修改当前 shipping 资产。
- Gate 02 rev 2 证据位于 `evidence/02-analysis/rev-002/`：`analysis-board.png`、`portrait-y-turn-preview.gif`、`portrait-y-turn-contact-sheet.png` 与 `motion-validation.json`。该轮 pure-Y 解释现已被用户明确否决；五项 motion artifact 保留原文件／hash 并标记 `reviewState=rejected`、`rejectionScope=pure-y-axis-360-turntable-motion-interpretation`，不得恢复。约 `3:4` Portrait、whole-case/no-explode、闭环管、磨砂背景和可读标签已在 rev 3 重新声明，不依赖被否决的 Y-axis claim。
- Gate 03 rev 1 合同为 `ArtSource/ModelPipeline/premium-display-case/evidence/03-contract/rev-001/modeling-contract.json`，SHA-256 `0f098fb78639fb2aa7c5cff6d8521a93a6944eb898c7c502738893a0be83e526`；大字评审图 SHA-256=`d995d5b3fe545a4d04dec74af8a4ce375e9776dd734a7b42d1136ba5fefea8bd`。该 immutable 合同继续保留为 stale history；其 `1.8 s` Y-turn、`0.55 s` 高光与悬浮 motion clause 已 rejected。当前 Gate 03 rev 2 不覆盖或删除这些文件。
- Gate 04 rev 1 位于 `ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-001/`：`part-tree.svg` SHA-256 `390162f3e2b2dd26c2ff820bfcc306fd7143f0dfa27413c111b877477a5d1a05`；`exploded-plan.svg` SHA-256 `729bc25e140ab868cfd72761d82349751c23f151e7ffa9bb18cfee618f9ccd6d`。两者继续保存真实父子树、单一 connected perimeter、`ContentSlot → PrizeContent` 与零奖品自主角速度；pipeline rev 21 继续写入 `internal-production-and-website-structure-only`、`productAnimationEligible=false`，不得进入产品动画。
- Gate 04 evidence rev 2 位于 `evidence/04-architecture/rev-002/`。被否决 GIF SHA-256 `c96feb8193a8348ef3cec3fa12dbb7022e00aefc8e76f4bc2a58ea75c26e75bb`；contact sheet SHA-256 `c7fd6c10e1018a4aeadf9a29a041768acd6025bc0f2887f031d09e6e6a24b4f6`；renderer SHA-256 `65027997a7c464f5004a2b1af1116caf0c1a7d43280e6e840fc5b5c7e11fcb00`；旧质量报告 SHA-256 `8dd454a99850a5004899a636b509314c751e35cb6d4a66252f579dee184f8f73`。用户明确拒绝该轮依次分离、停留和重组的审批表达；pipeline API 保留原文件与 hash，并将 4 项 artifact 标记 rejected/superseded，不得恢复为当前证据。
- Gate 04 evidence rev 3 位于 `evidence/04-architecture/rev-003/`。其 GIF 为 `3,620 ms`，MP4 为 `217 frames / 60 fps / 3,616.667 ms`。该轮最初只因速度被否决；当前上游 motion rejection 又使其 Y-axis frame path 成为 superseded historical evidence。renderer、timing report、GIF、MP4、contact sheet 与 quality report 保留原 hash，不得作为新路径来源。
- Gate 04 evidence rev 4 位于 `evidence/04-architecture/rev-004/`。`whole-case-only-1.25x-slower.gif`、`4,520.833 ms` MP4、contact sheet、renderer、timing report 与 quality report 全部保留原 hash；但其 cosine-width Y-turn 代理帧序已失效。`4.520833 s` 只保留为 slow-envelope candidate，不再代表 motion sequence 批准。
- Rive 时序现可区分 authored 与 runtime：authored root=`210f / 60fps = 3,500 ms`，authored `×1.25=4,375 ms`；main App wall-time=`3,617 ms`，standalone=`3,805 ms`。`4,520.833 ms` 来自旧 runtime-envelope 慢放编码。exact 2D keyframe／cubic easing 已在 rev 3 extract 中记录；physical pitch/yaw/3D axis/degrees/sign 仍 unknown。
- Gate 04 历史决定：用户原话“行，就照这个时间吧”只继续支撑 timing candidate。Pipeline rev 37 已将 Gate 04 标为 stale；rev 2 拆层／重组、rev 3 速度和 rev 4 pure-Y path 均只作不可变历史，不得恢复或覆盖 Gate 02 rev 3。
- Gate 05 rev 1 位于 `evidence/05-blockout/rev-001/`。用户查看后要求标签纸再下移，并把所有嵌套轮廓改为同心圆角。pipeline API rev 24 将该轮标为 rejected；文件与 hash 全部保留，作为 rev 2 的不可变 before 证据。Gate 03 只锁 `184 × 58 mm` 标签尺寸、外包络、管截面与 R20 外角，未锁标签中心 Y 或嵌套圆心；Gate 04 只锁 part tree、assembled/no-explode 和运动所有权，因此 earliest-gate 仍为 Gate 05。
- Gate 05 rev 2 位于 `evidence/05-blockout/rev-002/`。`build_blockout.py` 是确定性 Blender 源，`validate_blockout.py` 是独立验证器，`premium-display-case-blockout.blend` 是 Blender `5.2.0 LTS` 白模。pipeline API rev 27 保存用户原话“可以，继续推进”，并锁定标签中心从历史 Y=`105 mm` 下移 `6 mm` 到 Y=`99 mm`、三组解析式同心圆角和当前白模。标签框到展示舱和闭环管内轮廓的最小间距分别为 `7.313280 mm` 与 `12.591362 mm`。
- 同心圆角：盒体／闭环管／front-rear shell 共享 `(±94, ±132) mm` corner centers；主展示舱 rim／insert 共享 `(±75, 43/-127) mm`；标签框／透明盖轮廓／标签纸共享 `(±86, 122/76) mm`。三组均由解析 radius offset 生成，没有 subject `BEVEL` modifier；最大 drift `0.000 mm`，容差 `0.010 mm`。TransparentCover 厚度仍无上游批准，只登记 `186 × 60 mm / R7` 同心轮廓并保持 Empty；现有 part tree 和 `180 × 198 × 48 mm` ContentSlot 未变。
- 几何预检与 Gate 06 evaluated-mesh 验证：bounds 为 `228 × 304 × 59 mm`，宽高比 `0.75`。`ContinuousTubePerimeter` 为一个 cyclic hollow mesh object 和一个 connected material body；外截面 `10 × 9 mm`、通道 `6 × 5 mm`、壁厚 `2 mm`、外／中心线／内角半径 `20/15/10 mm`。BVH 截面射线和 3D cyclic flood-fill 访问 `384/384` 采样。完整 FBX／GLB 导出仍属于 Gate 10，不在本轮范围。
- 真实评审证据：`blockout-before-after.png`、`blockout-hero.png`、`blockout-top.png`、`blockout-oblique.png`、`blockout-side.png`、`blockout-concentric-centers.png` 与 `blockout-contact-sheet.png` 均由同一 Blender 源生成。圆心图用大字和十字直接标注三组共同圆心。`capture_standard_views.py` 探测到 `cli-anything-blender` 已安装但无 preview 子命令，按 skill 合同回落到真实 Blender bpy capture；10 个标准视图全部生成，`verified_capture=true`、`missing_views=[]`。
- 正式材质补充诊断位于 `evidence/05-blockout/rev-002/material-diagnostic/`。材质只来自现有 `ArtSource/DisplayCase/PremiumDisplayCase.blend` 和 `build_premium_display_case.py`：壳体／透明盖使用 `MAT_FrostedPolycarbonate`，闭环管使用 `MAT_FrostedPolycarbonateEdge`，内托使用 `MAT_BlackFlocking`，标签使用 `MAT_LabelPaper`／`MAT_LabelGraphite`，窄边使用 `MAT_RarityFoilSilver`。正式 Blender source 没有 image-texture node；本轮没有伪造 bitmap、Logo、achievement、黄色标签、笑脸、条码或样例编号。
- `TransparentCover` 和 `NarrowFoil` 的 Gate 05 source 节点仍分别保持 Empty／material zone；诊断 `.blend` 只增加零厚度、排除于 Gate 05 geometry digest 的可视代理面。标签两端只显示中性占位区。Hero、left/right oblique、low、side、标签近景、同心圆角近景、材质 contact sheet 和白模／PBR 同机位对照均以大字标记 `DIAGNOSTIC MATERIAL PROXY · NOT GATE 07 APPROVAL`。
- 材质诊断验证：Blender `5.2.0 LTS` Cycles `96 samples`、OpenImageDenoise、AgX；中性 key/fill/rim 为 `2.118:1:0.647`，rim/key=`0.306`，无宽范围青绿 rarity light。背景四个采样区亮度范围仅 `0.001862`，局部噪斑 outlier=`0`；标签 P10/P90 对比 `117.417213`，透明盖后 blackout fraction=`0`。subject geometry digest 在贴材质前／后／渲染后均为 `6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f`；bounds、Y=`99 mm`、同心误差 `0.000 mm`、开放／non-manifold 边 `0/0`、flood-fill `384/384` 均不变。
- Gate 06 rev 1 位于 `evidence/06-geometry/rev-001/`。其 audit 明确记录 `ContinuousTubePerimeter signedVolumeMm3=-52932.982745`，但旧 validator 只用 finite／contiguous normals 判 pass。透明／折射闭环管不能接受该方向错误；pipeline rev 29 将 rev 1 标为 technical rejection/superseded，42 项原文件、路径与 hash 全部保留。
- Earliest-gate 判定：Gate 03/05 锁定尺寸、截面、壁厚、圆角、标签、层级与白模，不锁 face winding。rev 2 不修改任何 Gate 05 文件、vertex coordinate、object matrix、bounds、管截面、壁厚、标签、同心圆角、part hierarchy 或 silhouette，因此不回退 Gate 05，最早受影响关卡仍为 Gate 06。
- Gate 06 rev 2 位于 `evidence/06-geometry/rev-002/`。只对 `ContinuousTubePerimeter` 的 outer／inner boundary faces 反转绕序：outer signed volume=`81983.867936 mm³` 且法线朝材料外；inner signed volume=`-29050.885191 mm³` 且法线朝 lumen；净 material signed volume=`52932.982745 mm³`。全部五个 subject 的净 signed material volume 均为正。
- Identity 证据：Gate 05 source full geometry digest 仍为 `6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f`；vertex-position digest `ced0edf95f8fa6416c5a0e33ebf8dc99fdafcdb3beceac85ee2970bbb2a7682c`、object-matrix digest `34d52e8980dbbffc5573523b80de9a47d145a49bb22ae95f8d7c1b38e393d588` 与 six-view silhouette digest `81615c0e5afd59b634dfa2e85040b31b30b9d5ef0ddc9e12462f1b3d1c59f6b4` 前后相同；仅 tube topology/winding digest 从 `14e4e74d73784314d0411b3e9ee70f06ca115954ef0450dbada10e8fa0837137` 变为 `c29bc1dd8c0f0c52fd4c70d102bcfc2b4007e579795b605adeb21611a3bf7c79`。
- 既有指标继续通过：bounds=`228 × 304 × 59 mm`、Portrait=`0.75`、标签 Y=`99 mm`、R20、concentric drift=`0.000 mm`；开放／non-manifold／bad-contiguous／self-intersection／degenerate=`0`；flood-fill=`384/384`；wall min/max=`1.995617/1.995784 mm`。`ContentSlot`、PresentationRoot、always-assembled hierarchy、internal-only exploded 和零自主角速度均未变。
- 内部技术证据：`geometry-review.png`、`geometry-review-contact-sheet.png` 与 `exploded-geometry.png` 保留原路径和 hash，只满足 Gate 06 pipeline technical contract。它们继续位于 `artifactIds`，不再进入 `reviewArtifactIds` 或主 UI。43 项 Gate 06 rev 2 既有 artifact hash 全部复核不变。
- 用户评审入口：`evidence/06-geometry/rev-002/gate06-whole-case-review-r003.png` 为 `4800×4000`，SHA-256 `1b8ab2787d2faf7ff479de653da6dc662b0763c71d7f4ccdefd92991b2f35362`。大字固定为 `WHOLE CASE ONLY · NO EXPLODE IN APP OR REVIEW`；只含 front／back／top／side、Workbench、dimensions、pivot、concentric、closed-loop、flood-fill 与 normal validation。图片校验报告为相邻 `gate06-whole-case-review-validation-r003.json`，禁止图源列表为空。CDP browser smoke 只渲染该一个 `reviewArtifactId`，图片实载 `4800×4000`；旧 review、contact sheet 与 exploded artifact 均未出现在主 UI。
- Shipping source contract：扫描 `Assets/Scripts`、`Assets/Plugins/iOS` 和 `Assets/_DisplayCase/Runtime`，排除保留的 authoring controller 声明后，没有 `SetDisplayCaseExplodedProgress`、`PlayAssembly`、`PlayExplode` 或自动 `SetExplodedProgress(1)` 调用；prefab `explodedProgress: 0`。内部 controller 继续作为制作工具保留。
- Gate 06 决定：pipeline decision event `35a4c71f-5668-4788-8935-0d34d1c549e2` 保存用户原话“可以啊，没问题，你继续吧”，approval scope 为 `current-gate06-geometry-rev2 / whole-case-only / no-explode`。该决定只批准 normals-corrected 几何；不批准 Gate 07 材质、Gate 08 灯光、shipping Unity、构建、安装或手机推送。
- Gate 07 rev 1 位于 `ArtSource/ModelPipeline/premium-display-case/evidence/07-material/rev-001/`。`material-board.png` 是整盒主评审；`material-closeup.png` 覆盖连续管角高光、实体标签／透明盖／窄银箔和触感内板；另有 Hero、left/right、side/back、clay-vs-PBR 同机位、0/90/180/270/360 grain stability 与大字参数板。所有用户证据为 assembled whole case；无 exploded artifact 进入 `reviewArtifactIds`。
- 材质来源只使用现有 `ArtSource/DisplayCase/PremiumDisplayCase.blend` 和 `build_premium_display_case.py`。壳体 `MAT_FrostedPolycarbonate` 为 `IOR 1.585 / roughness 0.22 / transmission 0.92`；连续管边缘为 `1.585 / 0.18 / 0.78`；黑色触感内板 roughness=`0.91`；实体标签纸 roughness=`0.73`；窄中性银箔 `metallic=0.96 / roughness=0.30`。Logo／achievement 只保留中性占位，正式 artwork deferred。
- `Coin_Slab_v15` 只支持材质分层与连续高光参考。Blender scene、文本和图像检查均未复制 WHATNOT、黄色、笑脸、条码、样例编号或圆形 coin window。标签 yellow-reference fraction=`0`。
- 微颗粒全部使用 `Texture Coordinate:Object`；0/90/180/270/360 local-coordinate recovery 最大误差 `<0.00001 mm`。0°／360° 图像 mean absolute channel delta=`0.0012736206`、max=`2`；无 world-space grain 游动。透明排序初检通过，label blackout fraction=`0`。
- 中性背景 roughness=`0.84`、局部 noise mask=`0`、径向晕=`false`、固定绿偏=`false`。四个背景采样区 luma range=`6.068977`、最大 channel chroma=`0.00763102`、局部噪斑 outlier=`0`。本关灯光只评估材质，不构成最终灯光批准。
- Gate 07 几何回归：full geometry digest=`a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951`、vertex-position=`ced0edf95f8fa6416c5a0e33ebf8dc99fdafcdb3beceac85ee2970bbb2a7682c`、winding=`c29bc1dd8c0f0c52fd4c70d102bcfc2b4007e579795b605adeb21611a3bf7c79` 全程不变。bounds=`228 × 304 × 59 mm`、标签 Y=`99 mm`、concentric drift=`0.000 mm`、开放／non-manifold=`0/0`、signed material volume=`52932.982745 mm³`、flood-fill=`384/384` 均通过。
- Blender audit、closed-surface coverage、asset optimization 与 QA 已通过；subject=`100,016` triangles，低于 `120,000` budget。三份 Gate 07 Python 证据脚本编译通过；Model Provenance Explorer、model-specific validator 与全 pipeline validator 通过。QA verdict 为 `READY_FOR_MATERIAL_REVIEW_NOT_SHIPPING`。
- Gate 07 决定：用户查看 `material-board.png` 后原话“挺好的”。pipeline API rev 34 已将 Gate 07 rev 1 标为 `approved`；decision event=`70dd6a17-7845-4b23-bcdc-a8f56819cb3b`。批准只锁定当前材质响应和分区，不批准 Gate 08 灯光、shipping Unity、构建、安装或手机推送。
- Gate 08 rev 1 位于 `ArtSource/ModelPipeline/premium-display-case/evidence/08-lighting/rev-001/`。主评审为 `lighting-review.png`；`lighting-details-contact-sheet.png` 覆盖标签、闭环管角连续高光和黑色内板；`lighting-passes-contact-sheet.png` 覆盖 Beauty／Clay／Normal／Depth／Roughness；`lighting-parameters-board.png` 以大字区分 Blender lookdev 与 Unity runtime。所有用户证据为 assembled whole case，没有 explode、拆层或重组。
- 灯光：key/fill/rim=`1.00/0.30/0.40`，能量=`2400000/720000/960000`，色温=`5000/6200/5600 K`。没有 rarity light 或固定绿偏。Hero 相机为 `60 mm`、sensor=`36 × 32 mm`、vFOV=`29.862834°`、无 DoF；AgX Medium High Contrast、exposure=`+0.55 EV`。shutter／ISO 未设置；这些值不是当前 Unity runtime 参数。
- 不变量：Gate 06 geometry digest=`a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951`；Gate 07 material digest=`8358cfdb12e49f87adbbafd96f33f2beb3415f9b920cb62732c73173c7799210`。两者在 Beauty 和全部临时技术 pass 前后不变；获批材质 assignment 在保存前恢复。grain 0/90/180/270/360 与透明排序初检通过。
- 图像验收：所有主图 highlight clipping=`0 < 0.5%`；标签／背景平均亮度差=`102.394073`；黑色内板 median=`21.153601`、`≤4` crush fraction=`0`；Hero mean green excess=`0.99042827`、`>8` fraction=`0`。Hero／左右斜视／低角最小边距分别为 `16.04% / 15.94% / 15.94% / 14.46%`，均未裁切。闭环管角最大连续亮部覆盖宽／高=`50.67% / 55.83%`。
- Gate 08 验证：Blender `5.2.0 LTS`、Cycles `96 samples`、Metal、OpenImageDenoise；build、Blender audit、pass/image checks 与 QA 全部通过。QA=`READY_FOR_LIGHTING_REVIEW_NOT_SHIPPING`。pipeline rev=`35`、`7/12`、Gate 08=`ready_for_review`、Gate 09=`blocked`、`shippingReady=false`。视觉批准待确认，未推送手机。

## 历史：磁吸扇牌抽卡主推 Banner（Gate 12 rev 2 已否决；已被 2026-08-27 单一 FBX 替换）

> **历史状态：2026-08-26，用户否决 Gate 12 rev 2：72 段后圆角过渡仍生硬，Unity 暖银出现不自然竖光，且与 Blender 审批截图的材质光感不一致。pipeline rev 117 将 Gate 12 标记 `rejected`。当前入口见上文 2026-08-27 权威 FBX 替换。**

- shipping `FidgetGachaStorefront.featuredBanner` 继续引用稳定资源名 `product-banner-magnetic-fan-card`，其文件内容已替换为 rev 7 clean `20 mm`／72 段 raster。业务 View 继续使用 `scaledToFit`、原始 `1179:654` 比例和无重复文字覆盖规则；本轮仍未进入任何 Build。
- 参考匹配工具链已安装并验证：124 个 Cursor Blender Skill、Blender MCP、fSpy 1.0.3、BlenderProc 2.8.0，以及 DiffusionLight-Turbo 源码和 MPS 隔离环境。DiffusionLight 上游推理仍硬编码 CUDA，未下载权重、未伪报本机 HDR 推理通过；完整版本和路径见 `tools/reference-scene-toolchain/README.md`。
- 72 段几何、尺寸、机制与导出数值继续作为有效结构输入，但当前 Blender source 的 polygon `use_smooth`／custom normal 为空，不能作为曲面视觉完成证据。下一版必须对 side／bevel 平滑、cap 保持硬边，并从 FBX 带入 Unity。
- Gate 08 rev 3 的 Cycles 截图只能证明 Blender lookdev，不能再替代 Unity material parity。Unity 暖银 shader 必须删除 object-space 假面板光；新 Gate 11 需同时比较 normal、roughness、specular direction 和同相机 beauty，而不只比较 silhouette IoU。
- Gate 09 rev 2／rev 3、rev 4 Card Rain、rev 5 14 mm、rev 6 含歧义道具版本与旧 Gate 12 证据均按 revision 保留。当前入口为 `ArtSource/ModelPipeline/magnetic-fan-card/evidence/12-shipping/rev-002/shipping-review-contact-sheet.png`；背轨入口为同目录 `shipping-mechanism-contact-sheet.png`。
- 已检查专用 `banner-design`、`banner-maker` 和 `ad-creative-generation` 方法；本轮采用现有 `frontend-design`、`bolder`、`genre-card-party-idle`、`scene-assembly`、`camera-cinematography`、`lighting`、`reference-look-calibration`、`vfx-fx` 与 `rendering` 的组合，不使用会重画真实产品的生成式广告图。
- 结构／自动化结果仍为：Gate 10 FBX／GLB=`70,548 tris / 32 meshes / 5 materials`、Gate 11 silhouette IoU=`0.9914715`、guardrail=`ALL PASS (7.590 mm)`、FanCardAcceptanceTests=`22/22`、CardGeometryValidator=`ALL PASS`、Gacha tests=`3/3`。这些检查没有捕获 shading parity，因此不能推翻用户视觉否决。pipeline rev 117 当前 `11/12`，Gate 12=`rejected`，`shippingReady=false`。

## Slab 定制款与收藏级产品线（仅规格；未开发、未预览、未推送手机）

> **当前状态：2026-08-21，用户新增“Slab 也可以出定制款和收藏级”的产品决定；`FDB-DSP-016—020` 已写入产品设计圣经。现有六款 Collector Slab 资产、运行时、交易链和获批 shipping 视觉不等于这两条新产品线已经实现。本轮没有修改模型、材质、UI、经济、entitlement、provenance schema 或 StoreKit，也没有生成新预览、构建或安装手机。**

- `Collector Slab` 现在定义为展示盒家族：`Standard Slab`、所见即所得的 `Custom Slab`，以及拥有官方固定版次与来源记录的 `Collector Edition Slab`。Slab class 与玩具 rarity、等级、Pack tier 和抽取概率保持独立，换盒不改变玩具物理、Haptic、XP 或收藏身份。
- 定制款目标允许选择已批准的壳体 finish、内衬、窄箔、标签版式和个人铭文；用户文字只能进入 `CUSTOM` 字段，不能伪造官方 rarity、日期、编号、限量数量或 `1 OF 1`。指定组合原则上走明确直购／定制解锁，不以盲抽追逐确定配置；首发项目和价格仍待决定。
- 收藏级目标使用不可自由改写的 authored edition、finish、系列／来源和真实首次获得时间。长期挑战、活动、付费套装或独立 Slab 奖池都只是候选发行渠道，需逐条决定；没有权威库存或服务端分配时不得显示虚假限量、序号和剩余量。
- 连续 30 个有效日的 `30 DAY` Slab 被记录为首个确定性收藏级候选：exact-once 写入真实达成日期，允许改装到已拥有玩具且不销毁 entitlement，同款不再作为普通直购或随机复制品。铭牌文案与外观仍须真实 shipping 预览批准。
- 下一步若实现，需要先锁定首发配置、价格与获得渠道，再建立独立 `slabId`／class／ownership／editable configuration／provenance schema、幂等铸造与迁移、Unity 权威数据、SwiftUI 编辑／装配 UI 和自动化。任何新材质、标签、几何、相机或 UI 必须先走真实 shipping 预览批准；当前视觉批准待确认，未推送手机。

## 30 日留存、首局节奏、Streak 与免费抽取恢复（仅规格；未开发、未预览、未推送手机）

> **当前状态：2026-08-21，用户要求把收敛后的首局与 30 日留存方案写入权威 Markdown；`FDB-RET-001—008` 已加入产品设计圣经。本轮没有修改 Unity／Swift 运行时、场景、UI、成长常量、抽取库存、StoreKit 或持久化 schema，没有生成 shipping 预览，也没有构建或安装手机。**

- 规格把奖励链固定为：机械视听触即时反馈 → 速度／峰值／Combo／Perfect／个人纪录 → XP／等级 → 外观／首抽 → 连续有效日／节奏周／30 日收藏身份。首局目标为 10 秒内完成核心手感认知、约 1 分钟到 Lv.5 并开放外观编辑／第一贴纸／第二 Rotor、真实盘玩 3 分钟开放 exact-once 保证新奖品首抽、5 分钟获得第一款确定性皮肤；该节奏尚未接入当前 `84,000 XP` 曲线。
- 现有“真实触摸 ≥60 秒且交互 ≥3 次”的有效日与任意 7 日完成 5 天的节奏周继续作为唯一基础；新增连续有效日展示、最多一次断签保护以及 D3／D7／D14／D30 确定性奖励目前都只是规格。任何缺少服务端真实 cohort、样本和反作弊的“超过 98% 玩家”均被禁止；首版只允许固定难度等级、个人最佳和明确写作个人历史的百分位。
- 免费抽取收敛为：首日真实盘玩满 3 分钟赠送一次保证新奖品单抽；其后每 24 小时恢复 1 张现有券、最多 3 张，当日完成有效日后才能使用；5/7 节奏周额外发 1 张同类型券。旧讨论中的 10 分钟一抽和每小时直接一抽／最多十抽不进入产品规格。
- 玩具访问收敛为：全部玩具 Day 0 可见；未拥有玩具有一次 20–30 秒不计成长的真实机制试用；入门 Rotor 永久可用，约 Lv.5 永久开放第二 Rotor，Day 2 开放磁吸推牌 24 小时完整试用。推牌永久拥有的直购／Collector Edition／同款 10/10 蓝图三条路径尚未实现，蓝图经济仍须与现有合金屑关系一起完成端到端产品与交易验收。
- 下一步若进入实现，必须先建立可测试的首局状态机、真实前台活跃计时、奖励幂等键、每日券恢复与上限、试用 entitlement／到期恢复、连续有效日／断签保护 schema 及迁移，再同步 Unity 权威数据、SwiftUI 展示和自动化。涉及皮肤、贴纸、Slab 铭牌或新 UI 的 shipping 视觉必须先预览并获批；真机安装与 Device Accepted 均未开始。

## Badge 40 枚 Challenge + Legacy 母版重画（已接入真实 shipping SwiftUI 与 Unity；shipping 预览待用户视觉批准，未推送手机）

> **当前状态：2026-08-21，Claude Code 已按 `badge-asset-manifest.json` 把 40 枚 Unlocked PNG 接入现有 Badge ID，替换 `Assets/Plugins/iOS/BadgeArtwork/` 中全部 b8 生成的 SVG/PNG 与旧 manifest；C# `BadgeCatalogV2.AssetName` 与 Collector Slab 3D 展示舱的 `PremiumDisplayCase` prefab／场景均已同步重建。没有重新设计任何图标、没有猜测 ID、没有修改成就门槛、奖励或 Badge 目录本身。真实 shipping SwiftUI 的三列图鉴、详情、Locked/InProgress/Hidden/Unlocked 四状态与 1080×1080 分享卡预览已在 Simulator 生成；未构建或安装手机，等待用户看过这些真实预览后明确批准。**

- 绑定方式：`BadgeSystem.cs` 的 `AssetName(id)` 由 `"badge-b8-" + id` 改为 `"badge-b10-" + id`，与 `Tools/BadgeAssetGenerator/import_b10_shipping_assets.py` 直接从 `ArtSource/BadgeSystem/ChallengeLegacyApproved20260821/badge-asset-manifest.json` 校验 SHA-256 后原样导入的 40 张 `png-1024/unlocked/badge-b10-*.png` 文件名一致；40 个 `badge_id` 逐一映射、无重复、无新增/删减 Badge。未获得态沿用既有做法——由同一张 Unlocked PNG 在运行时经饱和度/亮度/对比度/透明度派生（`ProductBadgeArtworkLayer`），approved 的 `png-1024/locked/` 仅作为参考，未被使用。
- 目录/详情沿用既有三列 `LazyVGrid`（`ProductBadgeLayoutTokens`，1:1 artwork、统一 padding）与 milestone token/short name 常驻章外两行 + 进度条在下方（`ProductRarityBadge`）；未改版式布局。
- **修复一个真实的“框里面套框子”渲染 bug（由用户在 Simulator 实机预览中发现）**：`ProductRarityBadge` 沿用 b8 时代的做法，先用 SwiftUI 渐变自绘一整套珍珠银六边形外框／凹腔／皮革内底（`ProductBadgeShellShape` + frame/well/panel 三层），再把“图标”缩到 48%（`iconSlotFraction`）嵌进这层自绘壳体正中。但 b10 approved 母版的每张 PNG 本身就已经把整套六边形外框／凹腔／bevel 连同图标烧录在一张图里（与 approved 概念联系表逐像素一致）；两者叠加后变成外框内又套一层缩小的完整徽章图像，产生肉眼可见的双重（乃至三重）嵌套边框。修复为：非 Hidden 状态直接用 approved PNG 边到边铺满整个 cell（`ProductBadgeArtworkLayer(...).frame(width: width, height: width)`），不再额外自绘外框／凹腔／皮革纹理／等级偏光层；`ProductBadgeArtworkLayer` 既有的整图饱和度/亮度/对比度/透明度状态派生逻辑保持不变，现在同时作用于连框带图标的整张母版图，与设计圣经“未获得态整体压为黑灰”的措辞更吻合。Hidden 状态没有真实图标可显示，改为一个简化的纯色深色六边形占位（复用同一 `ProductBadgeShellShape`）承载“?”符号。已删除随之变为死代码的 `iconSlotFraction`／`frameDepthOffsetFraction`／`outerEdgeFraction`／`frameFaceInsetFraction`／`wellInsetFraction`／`panelInsetFraction`／`gradeTint`。已用 approved 概念联系表（`contact-sheets/badge-system-full-05-vault-challenge-legacy-20260821.png`）与修复后的 Simulator 缩略墙逐张目视比对，六款 Challenge+Legacy 参考徽章外观一致。
- 修复一个既有 bug：1080×1080 分享卡渲染器（`ProductBadgeShareRenderer.render`）此前会在图标异步解码完成前截图，捕获到空占位符；已改为先用新增的 `ProductRarityBadge.prewarmFullArtwork` 把图标强制解码进缓存，再执行截图，`badge-share-card-1080.png` 现在正确显示真实图标。
- 新增一处无障碍修复：`BadgeUnlockOverlay` 的解锁弹出动画此前未响应 Reduce Motion；已加 `accessibilityReduceMotion` 环境读取，开启后跳过 spring 动画。
- Collector Slab 3D 展示舱：`PremiumDisplayCaseSceneBuilder.LoadToyBadgeArtwork()` 按 `BadgeCatalogV2.ToyDefinitions[].AssetName` 从 `BadgeArtwork/` 动态加载 Texture2D 并烘焙进 `PremiumDisplayCase.prefab` 的 `featuredBadgeArtwork` 绑定数组；仅改 AssetName 前缀而不重建该 prefab 会导致绑定仍指向已删除的 b8 贴图、`SetFeaturedBadge` 找不到匹配、`HasFeaturedBadge` 变为 false。已执行 `Tools/Codex/…` 同源的 `PremiumDisplayCaseSceneBuilder.BuildPrefabAndScene()` 重新烘焙 `Assets/Resources/Gacha/PremiumDisplayCase.prefab`、`Assets/_DisplayCase/Scenes/PremiumDisplayCase.unity` 与 `Generated/Materials/*`；未改任何 3D 模型、材质配方或该 prefab 之外的资产。
- 测试：`BadgeSystemTests`／`PremiumDisplayCaseTests`／`ProductArchitectureTests`／`SpinnerProgressionTests` 聚焦回归 `113/117 Passed`（`Logs/BadgeB10Import/BadgeB10ArtworkFix.xml`，含双重嵌套边框与图源缺陷两轮修复后的重跑）。`ShippingArtworkIsCompleteSquareTransparentSrgbAndTextFree` 因新母版不再随附 SVG、改用 PNG 内嵌 `iCCP` sRGB profile（而非旧的 `sRGB` chunk）、且视觉安全区从旧 74% 改为约 76–77%（40 枚实测 780–791 px 长边、居中偏差 ≤2.5 px），已相应更新断言以匹配新母版真实几何，而非放宽或跳过检查；`NativeUiUsesReusableProductComponentLibrary` 已同步更新为断言新的整图铺满写法、并显式 `DoesNotContain` 已删除的 `iconSlotFraction`/`frameFaceShape`/`wellShape`/`panelShape`，防止双重嵌套边框回归。剩余 4 项失败均与 Badge 无关、且均在本轮改动前已存在于工作区未提交状态：`NativeBridge_ExposesDragPinchScrubReplayAndCloseLifecycle`（`FidgetAppCoordinator.cs` 早已调用 `ThreeBladeDisplayPrizeFactory.Instantiate()`）、两项藏家 Profile／等级文案断言、`badge-leather-texture.png` 尺寸 512 vs 384；均未修复，不属于本次改动范围。
- **修复一个真实的图源缺陷（同样由用户在 Simulator 实机预览中发现，非运行时问题）**：approved `png-1024/unlocked/` 里 6 枚图标（`toy_technique_clean/power/speed/endurance/perfect`、`toy_combo_5`，均来自 `badge-system-full-02-technique-combo-20260821.png` 联系表第 1、2 行）实际只剩顶部一圈珍珠银细环，凹腔与图标本体完全缺失、透明见底，与已批准联系表逐像素比对确认是残缺文件而非设计意图。根因定位在 `Tools/BadgeAssetGenerator/package_approved_badge_concepts.py` 的 `_largest_badge_contour`：五张联系表并非用完全相同的行列网格生成，第 2 张联系表前两行真实徽章中心比假定网格中心低约 30–37px，而该函数为了避开徽章下方的运行时文字标签，搜索窗口刻意收得很紧，真实徽章一旦超出这个偏移量，六边形圆环就会被搜索框硬生生切开、不再闭合，导致后续按外轮廓填充内部时只填出细环、凹腔与图标区域判定为"环外"而丢失。修复方式是新增一次粗定位（`_recentered_on_true_badge`，用大搜索窗先找到真实轮廓质心），再用原有的窄搜索窗以真实质心为中心做第二次精定位，不改变／不猜测任何图标设计。已用该修复重跑 `package_approved_badge_concepts.py`：40/40 校验通过，40 枚均无残缺（脚本自带的连通分量与像素校验全部通过，另加一道"中心区域透明占比"检测脚本人工复核），并已用 `import_b10_shipping_assets.py` 把修复后的 6 张文件（新 SHA-256）重新导入 shipping 目录、`badge-asset-manifest.json`／`validation-report.json` 已随生成脚本自动重写。
- 新增一处布局调整（用户要求）：Badge 目录页把原本各自独立卡片的 "BADGES" 标题头与"最近目标"合并为同一张 `productGlass` 卡片（中间加一条 `Divider`），整体放在 Segmented Picker 之上的页面头部，不再是两张分离的卡片；未改动其余版式或数据来源。
- Swift 侧 `arm64-apple-ios15.0-simulator -warnings-as-errors -typecheck` 通过（`FidgetProductUIComponents.swift`／`CodexSwiftUIOverlay.swift` 等九个 shipping 文件）。
- Shipping 预览：`Tools/BadgeNativePreview/capture.sh` 已改为直接校验并复用 approved 的 b10 资产（不再调用旧的 `build_b8_assets.sh` 重新生成图标），编译真实 shipping Swift 源码并在 iPhone 17 Pro Simulator 生成完整证据，位于 `Artifacts/BadgeSpecial/NativeB10/`：`badge-native-catalog.png`（三列图鉴）、`badge-native-detail.png`（详情）、`badge-native-states.png`（Locked/InProgress/Hidden/Unlocked 四状态同屏）、`badge-native-unlock.png`、`badge-share-card-1080.png`（1080×1080，已验证像素尺寸）、`badge-native-reference.png`、8 张按类别的 3 列缩略墙（`badge-native-thumbnail*.png`）及其拼接总图 `badge-thumbnails-all.png`、`badge-native-contact-sheet.png`。
- 下一门禁：用户查看上述真实 Simulator 预览并明确视觉批准后，才可构建或安装到 iPhone；批准前不得推送手机。

## 标准化 3D 建模溯源流水线（工具已集成；磁吸推牌退回 Gate 7 原图权威复核；未推送手机）

> **当前状态：2026-08-26，用户只临时确认 rev 9 外观，并要求下一次评审带上轴心旋转角度；该决定不是 Gate 7 正式批准。workflow rev 108 纠正了 rev 107 的自动 `stage-approved`，rev 109 将 Gate 7 rev 10 设为 `ready_for_review`，rev 110 登记桌面／移动工作台证据。rev 10 修正独立下片图案和血红晶体颗粒／微闪，并展示 `[0,-9.5,0] mm` `+Z` 轴的 `0°/12°/36°` spin 及独立 `[0,+21,0] mm / 0°` slide。Gate 8–11 全部 `stale`，Gate 12 保持 `blocked/rejected`；旧 `EDC_Root` 仍默认 active。视觉批准待确认，未运行 Unity、构建、安装或推送手机。**

- Gate 6 批准范围：六正交、Workbench、`50 × 31 × 12 mm`、`[0,-9.5,0]` 单点 `+Z` 轴和仅两外壳爆炸图。Gate 6 blend 的 SHA-256 在 Gate 7 生成前后均为 `dae227b2810e4c264b856bd4539e10d6a96d807e8ec68ca9b0a8e371d1be72ae`。
- rev 9 决定状态：用户原文“我暂时确认了 rev 9，但是我希望你下一次再找我确认的时候，能把轴心旋转的角度也带上.” 只构成 provisional visual acceptance。Gate 7 继续 pending；不得推进下游。
- rev 10 下片图案：frame 03／05／10 的实拍直见区与官方同款图辅助重建的遮挡区分开保存。上片 Mask SHA-256=`8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36`，下片=`7bf5921f469a217b850ff2ea94dc5ae6c251091b8de60f7d12da7721822`，binary difference=`0.382127`；两者可独立替换。遮挡区明确为 reconstruction，不是 exact trace。
- rev 10 晶体：deep blood red 保持；roughness=`0.022–0.11`、coat=`0.48 @ 0.035`、transmission=`0.05–0.30`、granular variation=`28 scale / 0.68 mix`、microflake=`85 scale / 0.72–0.79 threshold / 0.70 mix`。macro microflake 检出 `1049 px`，四象限均有分布；Emission=`0`、Bloom=`false`、无高光剪白。
- rev 10 轴心证据：世界轴点 `[0,-9.5,0] mm`、方向 `+Z`；`0°/12°/36°` 对应 detent `0/1/3`，`360° / 12° = 30`。三张 spin 均保持 translation=`0 mm`、pivot drift=`0 mm`；`45°` 未作为主姿态。slide-open 单独为 `[0,+21,0] mm / 0°`。
- rev 10 几何保持：生成前后 evaluated geometry digest 均为 `85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f`，base object matrices 不变。主评审位于 `evidence/07-material/rev-010/source-fidelity-review-board.png`、`material-closeups-board.png`、`axis-angle-evidence-board.png` 与 `lower-artwork-direct-vs-reconstructed.png`。
- 新机制 DecisionState：旋转棘轮覆盖完整 `360°`，每 `12°` 一个 detent，因此每圈恰好 `30` 档；物理与 Haptic 最终必须读取同一机制设置。DeliveryState 仍为 `specified-only-runtime-and-hardware-validation-pending`。当前 shipping 六档线性推牌未被修改；runtime、Haptic、iPhone 整圈计数和触感均未实现或验证。
- 隐藏机构边界：30 档要求不改变 exterior geometry。隐藏齿、棘爪、滚珠、弹簧和耦合继续 unknown；Gate 7 没有添加 hidden mechanism mesh。
- Gate 7 rev 3 几何保持：材质分配前、分配后和 Blender render 后 evaluated geometry digest 都是 `85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f`。Bounds、point axis、lower／upper／enclosure matrices、256 段半圆轮廓与两片 exterior mesh 均未变化；artwork geometry count 为 `0`。
- Motif provenance：`source-derived-motif-visual-trace.png` 从 `slider-intake-nxedc-ref-01` 的 normalized crop `[0.2890625,0.142578125,0.7109375,0.8369140625]` 以确定性 Pillow recipe 派生；mask SHA-256 为 `8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36`。它明确标为 `visual-trace-not-production-vector`。Shader 只用 base-color mix 与 inverted bump 模拟凹蚀：strength `0.24`、depth illusion `0.06 mm`，没有 mesh displacement。
- rev 3 精确值：镜银外体保持 `baseColor [0.72,0.78,0.86] / metallic 1.0 / roughness 0.095 / IOR 1.50 / coat 0.32@0.055`。晶体 face 从 rev 2 的 `roughness 0.075 / IOR 1.46 / specular 0.50 / transmission 0.48 / coat 0.88@0.035 / thin film 1.38@520 nm / motif mix 0.94 / emission 0.22` 调为 `roughness 0.028 / IOR 1.52 / specular 0.58 / substrate transmission 0.15 / clear-cap coat 1.00@0.010 / thin film 1.42@545 nm / motif mix 0.98 / emission 0`。微面 sparkle 为 scale `130`、strength `0.035`、distance illusion `0.012 mm`；substrate saturation/value 为 `1.30/1.15`。降低 substrate transmission 是 Eevee 单表面能量保留措施；透明 cap 由满权重低粗糙度 Coat lobe 表示。
- 制造证据：准确 HALOOPLAYER 页面只确认 `Material: Steel`。窄镜面高光支持 polished metal 外观；opaque motif 的清楚边缘支持 blackened／etched-and-filled／laser-cut layer 候选；purple-blue-green 角度变化与有机 patch 同时符合 nacre/abalone、dichroic multilayer film 或 interference pigment；oblique edge stacking 支持 clear protective cap，但 clear resin、polymer lens 或 glass/crystal 均未获产品来源确认。除 Steel 外都保持 provisional。
- 真实 Blender 证据位于 `evidence/07-material/rev-003/same-camera-crystal-comparison.png`、`neutral-pbr-material-board.png` 与 `neutral-pbr-material-closeup.png`。rev 2／rev 3 closeup 共用 `(58,-72,58) → (0,-1,3.2)`、`78 mm` 相机和四盏完全相同 neutral reveal area light；world strength `0.9`，不进入 Gate 8。
- 图像验证：同机位 ROI 平均亮度 `76.3027 → 76.3875`；`≥230` 高光占比 `0.000891 → 0.001094`，相对 `+22.7834%`；RGB chroma `+3.3045`；face P90-P10 contrast `121 → 131`；`≥250` clipping `0.000258`，hard-255 `0.000084`。没有 emission、bloom、曝光补偿或 Gate 8 灯光。
- rev 6 motif lineage：`Artwork_Upper` 与 `Artwork_Lower` 使用两个独立外部路径和 node group，但初始文件都是 rev 2 `magnetic-slide-tile-motif-mask-r002` 的逐字节无损副本；三者 SHA-256 均为 `8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36`。rev 3 也登记了同一 hash。该来源明确标为 `user-authorized-prior-material-design-reuse` 与 `notNewExactTraceClaim=true`，不再把它冒充新 exact-product trace。mask 使用 `Closest` 采样；打开 `+21 mm` 后下片继续显示完整图案。
- rev 6 silver target：准确页面的生产材料 claim 仍是 `Steel`；pure silver 只是用户授权的外观目标。`M07R6_PolishedPureSilver_VisualTarget` 为 neutral base `0.94/0.94/0.92`、metallic `1`、roughness `0.045`、IOR `1.45`、anisotropy `0.22 @ 0.08`、coat `0.12 @ 0.025`，并使用 scale `380`、strength `0.032`、distance `0.006 mm` 的微划痕 bump；emission 为 `0`。
- rev 6 真实 Blender 证据位于 `evidence/07-material/rev-006/`：`mask-comparison-same-camera.png`、`silver-comparison-same-camera.png`、`neutral-front-blood-red.png`、`diagnostic-side-white-card-reflection.png`、`diagnostic-silver-reflection-cards.png`、`open-slide-lower-artwork.png`、`editable-artwork-layer-board.png`、`neutral-pbr-material-board.png`、`neutral-pbr-material-closeup.png` 与 `gate07-workbench.png`。另有十张 `fixed-views/` 标准视图。白／18% 灰／黑卡只用于 Gate 7 材质诊断，不是 Gate 8 灯光。
- rev 6 定量验证：同机位 motif Laplacian variance `68.626554 → 132.947196`，Canny edges `2447 → 5658`；纯银中性像素 median luma `54.2338 → 73.949`，mean chroma `9.779689`，P90 `238.2126`，`≥250` clipping `0.0005354`。白／灰／黑卡 luma 为 `180.813583 / 94.479438 / 10.492865`；侧面白卡反射跨度 `630 px / 0.45`。blood-red hue `-10.243902°`，pink fraction `0.00000622`，blood-red fraction `0.99999378`，整图 clipping `0.00005175`。打开下片 Laplacian `134.834799`。Gate 6 digest 仍为 `85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f`；隐藏机构与 30-detent specified-only 状态未变。
- rev 7 border：`artwork-top-perimeter-border-mask.png` 是第三个外部可替换 mask；`border-settings.json` 暴露 `64 px`、minor axis `10.322581%`、约 `3.2 mm`、outer inset `0 px`。它与上下 clean motif 用 `MAXIMUM` 合成，只覆盖 decorative top face。结构 vertical side wall 和 visible rim 仍使用 silver。上下 motif 文件仍是 rev 2／3 clean mask 的无损副本，SHA-256 为 `8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36`。
- rev 7 silver/daylight：`M07R7_DaylightNeutralPolishedSilver` 使用 base `0.97/0.965/0.94`、metallic `1`、roughness `0.03`、anisotropy `0.14 @ 0.08`、coat `0.06 @ 0.02`、零 emission 与 scale `420`／strength `0.022`／distance `0.004 mm` 微划痕。rev 6 蓝偏诊断为 mirror metal 反射 blue-tinted studio world；rev 7 studio world 改为 neutral `0.105/0.105/0.105`。D65 diagnostic 使用 `6504 K`、Sun energy `3.2`／angle `0.53°`、neutral overcast fill `28000 W`／size `60`、world `0.72`／strength `0.75`、ground `0.55`、white balance `6504 K`／tint `10`、AgX Medium High、fixed `EV 0`。
- rev 7 定量验证：rendered dark top-face fraction `0.20443017 → 0.2748419`；border mask 四边 `0 px` 到界。rev 6 blue-biased pixel fraction 为 `0.13119597`，rev 7 neutral studio median `b*=0`、`C*=0`。D65 hero silver median `L*=73.333333 / C*=1 / b*=1`，side direct 为 `67.45098 / 1 / 1`，P90 `79.215686`；hero／side clipping 为 `0.0000625 / 0.0001096`。reference cards luma 为 `197.360614 / 120.377141 / 29.350328`。blood-red hue `-6.335404°`、pink `0`、blood-red fraction `1`；打开下片 Laplacian `150.152264`。Gate 6 digest、hidden mechanism、30-detent specified-only 均未变。
- rev 7 真实证据位于 `evidence/07-material/rev-007/`：`black-border-comparison-same-camera.png`、`top-face-boundary-diagram.png`、`silver-environment-diagnosis-same-camera.png`、`neutral-studio-silver-comparison.png`、`outdoor-d65-hero-neutral-card.png`、`outdoor-d65-silver-side-direct.png`、`blood-red-closeup.png`、`open-slide-lower-artwork.png`、`editable-artwork-layer-board.png`、`neutral-pbr-material-board.png`、`neutral-pbr-material-closeup.png`、`gate07-workbench.png` 与十张 `fixed-views/`。全部是 Gate 7 material diagnostics，不是 Gate 8 lighting。
- Gate 8 rev 1 灯光配方：D65 key `(54,-72,98) mm / 62000 W / 52 mm / 6504 K`；neutral fill `(-62,-22,62) / 30000 W / 46 mm / 5600 K`；silver rim `(34,72,68) / 48000 W / 38 mm / 6400 K`；face reveal `(-12,-28,112) / 23000 W / 30 mm / 5900 K`。world 为 uniform neutral `0.24/0.24/0.24 @ 0.85`，无 HDRI；EV `0`、white balance `6504 K`／tint `10`、AgX Medium High。三张白卡与一张黑卡只参与反射且 camera-hidden；Gate 9 环境合成未开始。
- Gate 8 真实 Blender 证据位于 `evidence/08-lighting/rev-001/`：`hero.png`、`left-oblique.png`、`right-oblique.png`、`low-angle.png`、`pass-beauty.png`、`pass-clay.png`、`pass-normal.png`、`pass-depth.png`、`pass-roughness.png`、`open-side-reflection.png`、`lighting-view-board.png`、`lighting-pass-board.png` 与 `gate08-workbench.png`。源 Gate 7 blend 哈希前后均为 `dc34da323813f103c90efa0c6f21142b68b741e1093b205eb04c091c28a7db2e`；geometry digest 仍为 `85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f`。
- Gate 8 图像验证：hero／left／right／low／beauty neutral silver highlight median `L* = 77.25 / 83.92 / 75.69 / 82.35 / 76.08`，`C* ≤ 1`、`b* = 0–1`；整图 `≥250` clipping 最大 `0.027429%`。Hero blood-red hue `-2.5°`、pink `0`、blood-red fraction `1`；Hero motif/seam Laplacian `212.73`、Canny `11744`。Clay／Normal／Depth／Roughness pass range 与 channel checks 全部通过；shipping material emission 均为 `0`，unlit 仅用于隔离的 technical pass override。
- Unity 反射答案登记于 `unity-reflection-plan.json`：`Packages/manifest.json` 与 lock 均确认 URP `17.5.0`；`Mobile_RPAsset.asset` 已启用 reflection-probe blending、box projection 与 atlas。后续路线是 local reflection probes + skybox/HDRI，realtime probe 只在需要时更新，不每帧更新；它是 approximate cubemap reflection，不是 ray-traced／per-pixel true mirror。水晶 transmission／iridescence 需 Shader Graph 或 custom approximation。该项 `specified-only-not-integrated`，Gate 9/11 与 device acceptance pending。
- Gate 8 批准：workflow history 已保存用户原文“可以吧，然后你继续”；Gate 8 rev 1 为 `approved`。该批准不代表 Unity reflection、Shader Graph 或真机已交付。
- 优化 DecisionState 为 `locked-user-approved`：当前两片 exterior mesh 各 `2,048` triangles，总计 `4,096`，继续作为唯一近景模型；不创建 high/low 或 LOD。上下 artwork mask 保持独立替换。简化 Library 模型只有在 Unity 多模型同屏 profiling 证明必要时才创建；未来 high-poly 只用于 bake 且永不 shipping。DeliveryState：当前单模型与 Blender mask pipeline 已保留；Library 简化模型未创建；ASTC/channel packing 仍为 Gate 10／Unity import specified-only，尚未交付。
- Gate 9 配方：neutral control 沿用 Gate 8 uniform world `0.24/0.24/0.24 @ 0.85` 与 ground `0.08 / roughness 0.46`。shipping-like preview 沿用 `FDB-SCN-001/002` 与 `MeshyEDC.unity`，使用 near-black／low-saturation directional world：vertical stops `0.0=[0.008,0.012,0.018]`、`0.46=[0.022,0.030,0.039]`、`0.76=[0.34,0.36,0.37]`、`1.0=[0.085,0.100,0.108]`，strength `0.85`；固定 fine grain `0.012 / scale 120 / detail 2`；ground `[0.018,0.024,0.032] / roughness 0.48`。无 HDRI；原三白一黑 reflection-card transforms 不变。
- Gate 9 隔离证据：`neutral-environment.png` 与 Gate 8 `pass-beauty.png` 像素完全一致，`max channel delta = 0`。neutral／shipping 的 geometry digest、object matrices、Beauty 与 right-oblique camera transforms/lenses、三项 shipping material hashes／assignments、closed pose、四灯 rig、EV `0`、white balance `6504 K / tint 10` 与 reflection-card transforms 完全一致；只有 world、ground 和环境反射输入变化。
- Gate 9 图像验证：shipping silver body `L*=61.176 / C*=1 / b*=0`，bright reflection `L*=84.314`；right-oblique bright reflection `L*=80.392`。整图 clipping `0.00014531`；blood-red hue `-9°`、pink `0`、blood-red fraction `1`；motif contrast ratio `1.854`、Laplacian `214.286`、Canny `7609`。neutral→shipping matched-camera mean absolute channel delta `38.707`；side reflection ROI delta `38.516`，证明 polished silver 的环境响应可见。shipping emission 继续为 `0`。
- Gate 9 真实证据位于 `evidence/09-environment/rev-001/`：`environment-comparison-board.png`、`neutral-environment.png`、`shipping-environment.png`、`reflection-closeup-comparison.png`、`neutral-side-reflection.png`、`shipping-side-reflection.png`、`environment-difference-map.png`、`gate09-workbench.png`、derived Blender scene 与四份验证／决策报告。Blender world reflection 明确是 preview-only，不是 Unity Reflection Probe 集成。
- Gate 9 rev 1 结论：用户指出它没有任何 slide-open appearance，因此 pipeline revision 72 已保存精确 rejection note；rev 1 的 21 个 artifacts、hashes、环境 recipe 与优化决定继续不可变保留，不再作为当前 review artifacts。
- Gate 9 rev 2 open pose：`UpperTranslation=[0,+21,0] mm`，upper world Y=`21 mm`；UpperTranslation、point pivot 与 upper mesh rotation 均为 `0°`。下片 matrix 在 closed／7／14／21 mm 全程保持 `[0,0,-3] mm`，point axis 从 closed local `[0,-9.5,0]` 随上片平移到 open world `[0,11.5,0]`。Local mesh hash 前后均为 `50b1f913f8b94a1428af404478cb5169d7e142b765955d224125108de463d5d0`，两片总计仍为 `4,096` triangles；无 LOD／Decimate。
- Rev 2 不变量：三项 shipping material hashes／assignments、四灯 rig、reflection-card matrices、shipping world hash、ground material、emission `0` 与上下独立 external artwork paths 全部不变。上下 mask SHA-256 均为 `8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36`，但继续由独立 `Artwork_Upper`／`Artwork_Lower` node groups 消费。隐藏 mechanism 仍只有 camera-hidden EMPTY metadata，未渲染内部 mesh。
- Rev 2 图像验证：near-top lower ROI 有 `91,714` 个 red artwork pixels、contrast `1.58651`、Laplacian `221.645`、Canny `24,264`；21 mm open frame 的 red artwork pixels 为 `41,984`，比 closed `31,999` 多 `31.2041%`。Hero silver body `L*/C*/b*=60.392/1/0`、bright reflection `L*=84.314`；blood-red hue `-7.5°`、pink `0`、blood-red fraction `1`；Hero clipping `0.00006615`。neutral→shipping open Hero mean delta `36.547`，layer closeup delta `42.679`。
- Rev 2 真实证据位于 `evidence/09-environment/rev-002/`：`open-environment-comparison-board.png`、`open-style-review-board.png`、`closed-open-sequence-board.png`、`lower-artwork-visibility-board.png`、`open-reflection-closeup-board.png`、open neutral／shipping Hero、shipping oblique／near-top、neutral／shipping layer closeup、四张 sequence、derived Blender scene、Workbench 与三份验证报告。
- Gate 9 rev 2 批准：workflow revision `75` 保存用户原文“可以的，可以的。然后开始继续下一步吧。”；Gate 9 当前为 `approved`。该批准不代表 Unity reflection、Shader Graph 或真机已交付。
- Gate 10 rev 1：`evidence/10-export/rev-001/` 全部文件与 hash 保持不变。用户指出评审图中的胶囊圆弧看似分面。检查发现 rev 1 review board 把两个各 `128` triangles 的非渲染 collision capsules 以 shaded surface 与 shipping mesh 并排展示，形成主要视觉混淆；FBX 设置还是 `mesh_smooth_type=OFF`。Blender rev 1 FBX 重导实际仍恢复连续 custom side normals，因此不能把分面感归因于 geometry 面数不足。
- Gate 10 rev 2 package：`evidence/10-export/rev-002/` 包含 `magnetic-slide-tile-authoritative-r002.blend`、`magnetic-slide-tile-r002.fbx`、`magnetic-slide-tile-r002.glb`、`magnetic-slide-tile-collision-r002.fbx` 与 manifests。source／triangulated export 的 triangle geometry digest 均为 `9f7606754c8faf4dbf6e95c473f2ae8ee720ee3f3854fecd96345e5cc64a97bb`；可见 geometry 仍为 `4,096` triangles。authoritative mesh 每片锁定 `513` 个 smooth side faces、`2` 个 flat caps 与 `1,026` 条 sharp cap-side edges。FBX 使用 `FACE` smoothing；GLB 四个 primitives 均含 `POSITION/NORMAL/TANGENT/TEXCOORD_0`。
- Shading metrics：source／FBX／GLB side corner-normal discontinuity 均为 `0.000°`，无 normal inversion；cap-side angle 为 `89.9995–90.0025°`。2560 px 同机位 polished-silver closeup 中，FBX／GLB 相对 source 的 p99 RGB delta 均为 `0.333` level，轮廓 max delta 均为 `0 px`，没有 export-added periodic facet bands。`arc-contour-overlay-2560.png` 记录 analytic chord error `0.0002918 mm`，不支持重开 Gate 6 或增加 tessellation。
- Collision：独立 FBX 仍为两个 `30.6 × 49.6 × 5.8 mm` convex capsule prisms，各 `128` triangles、总计 `256`。`collision-non-rendering-panel.png` 只用 wireframe 并明确标注“仅碰撞，不会显示 / NON-RENDERING COLLISION”；它们不影响 silver 外观或圆弧顺滑度。可见 render geometry、hierarchy、LOD policy 与 metadata-only hidden enclosure 未变。
- Artwork／memory：upper／lower source mask 与 channel pack 保持独立路径。Unity 实际导入后的两张 runtime pack 均为 `512 × 1024`、linear、alpha input、mipmaps on，iPhone override 为 `ASTC_4x4 / max 1024`；Editor 实测 runtime memory 各 `1,399,184 bytes`，iOS texture payload 估算各 `699,072 bytes`（含 mip）。这不是设备内存；真机内存仍未测。两张 transport basecolor 为 `ASTC_6x6`，source-only masks 不设 iPhone override。
- Gate 10 rev 2 技术验证：`export-manifest.json`、`texture-manifest.json`、`glb-structure-validation.json`、`reimport-validation.json`、`blender-export-audit.json`、`smoothing-normal-validation.json` 与 `smoothing-image-validation.json` 全部 pass。该 revision 的 export 文件未被 rev 3 修改。
- Gate 10 rev 3 评审：`evidence/10-export/rev-003/round-edge-location.png` 在完整模型上用单一橙框和箭头标出前端圆弧侧边。`round-edge-before-after.png` 使用 source pixel ROI `[540,1040,1200,1700]`，在默认板上放大超过 `3×`；两张源图均为 `3200×1800`，相机、灯光、曝光和 crop 完全一致。实际 ROI mean／p99 差异为 `0.01173 / 0.333333 RGB level`，视觉差异不明显；评审板明确说明这一点，没有伪造“修复前一格一格”。
- Gate 10 rev 3 browser：默认 2 张 review cards；技术细节保持收起且主界面不显示 export 术语。modal close／Escape／backdrop／browser-back、collapsed-details 内真实 GLB viewer 和 `390×844` 单列 mobile 均通过；真实截图为 `evidence/10-export/rev-003/gate10-plain-workbench-browser.png`。
- Gate 11 rev 1 部分决定：workflow revision `90` 精确保存“pattern placement accepted; geometry/round-edge parity rejected.”。图案位置暂定接受，不是 rev 2 的问题范围。rev 1 的 scene、renders、report 与 hashes 不覆盖；Gate 11 没有获批。
- Gate 11 rev 2 根因：rev 1 使用六个互不连续的 `32 × 32` 纯色 cubemap faces，且没有 mipmaps。近镜面银色把 face 交界显示为固定宽直亮带，视觉上像低面数。rev 2 使用 `256 × 256 RGBAHalf` 方向连续函数、`9` mips、trilinear filtering，关闭 box projection；analytic seam delta 为 `0.0000142455`。相机、灯光、曝光与银色材质值保持受控。
- Gate 11 rev 2 geometry/normals：bounds 仍为 `0.012000006 × 0.031000001 × 0.049999997 m`，相对误差 `4.65661e-7`；两片 render mesh 仍共 `4,096` triangles，两个 collision proxy 各 `128`。实际 side-wall 相邻 vertex-normal 变化中位 `0.703043°`、P95 `0.703600°`、最大 `0.877819°`，匹配每半圆 `256` 段的 `0.703125°` 预期；cap-side minimum 为 `90°`。没有改 export/import normal path，也没有加面。
- Gate 11 rev 2 image：固定亮带评分 `72.0634 → 7.61893`，平滑变化覆盖 `3.0641% → 8.9136%`。Blender／Unity silhouette IoU `0.986902`、bbox IoU `0.991814`、contour P95 `4.10788 px`。真实 Unity wireframe 保留密集圆弧线。URP 水晶 thin-film/transmission 与 cap-only artwork overlay 限制不变。
- Gate 11 rev 2 文件与测试：隔离 scene 为 `Assets/ModelPipeline/MagneticSlideTile/Gate11Rev002/MagneticSlideTileNeutralParityRev2.unity`；核心报告为 `evidence/11-unity-parity/rev-002/parity-report.json`。主评审为 `unity-round-edge-location.png`、`unity-round-edge-before-after.png`、`unity-round-edge-wireframe-proof.png`；真实 workbench 截图为 `gate11-rev2-workbench-browser.png`。`MagneticSlideTileParityRev2Tests` 为 `5 passed / 0 failed`；desktop/modal/Escape/backdrop/browser-back/real-GLB/`390×844` mobile 均通过。
- Gate 11 rev 2 批准：workflow revision `93` 精确保存用户原文“确认”。Gate 11 DecisionState 为 approved；它不批准 Gate 12 外观、runtime、Haptic、构建、安装或设备验收。
- Gate 12 安全接线：`Assets/_EDC/Scenes/MeshyEDC.unity` 新增 `MagneticSlideTile_CandidateSwitch` 和候选 prefab 引用。保存状态固定为现有 `EDC_Root` active、候选 inactive。`MagneticSlideTileCandidateActivation` 只为 editor capture 显式切换；每次捕获后重新打开场景并比对 hash，防止预览状态写回默认。
- Gate 12 候选资产：prefab 位于 `Assets/_EDC/Candidate/Prefabs/MagneticSlideTileCandidate.prefab`。`MagneticSlideTileCandidateSettings.asset` 是候选 21 mm travel、30 detents 与 12° step 的唯一设置源。`MagneticSlideTileCandidateController` 只提供显式 slide／detent review pose，初始与 reset 速度均为 0，不含 Update 自驱。它没有手势输入，也没有 Haptic renderer 接线；`RuntimeInputIntegrated=false`、`HapticsIntegrated=false`。
- Gate 12 材质：银色为 URP Lit `0.97/0.965/0.94`、metallic `1`、smoothness `0.97`，使用从 Gate 11 连续环境复制的 `256 × 256 RGBAHalf / 9 mips / trilinear / box projection off` local Reflection Probe。上下水晶各有独立 material 和 artwork texture path。`MagneticCrystalMobile.shader` 以单次 opaque pass 近似 clearcoat、背光 transmission 与 Fresnel iridescence，emission 为 0；不实现物理 refraction、volume absorption 或 Blender thin-film spectral transport。
- Gate 12 真实证据：`evidence/12-shipping/rev-001/` 包含 `library.png`、`hero.png`、`top.png`、左右斜视、`low.png`、`phone.png`、`slide-open.png`、`ratchet-60deg.png`、`gate12-shipping-board.png`、`gate12-motion-board.png`、`gate12-shipping-report.json` 和 `gate12-image-validation.json`。图片来自真实 `MeshyEDC.unity` 的相机、灯光和候选开关，不是概念图或隔离 parity scene。
- Gate 12 验证：`MagneticSlideTileGate12Tests` 为 `7/7`；PlayMode `CandidateResetLeavesNoSelfMotion` 为 `1/1`。报告确认两片 render mesh、`4,096` triangles、bounds `0.050 × 0.031 × 0.012 m`、独立 artwork、zero emission、filtered reflection 和默认关闭候选。iPhone HDR、性能、内存与 Haptic 仍未测。
- Gate 12 workbench：默认只显示 `gate12-shipping-board.png`、`gate12-motion-board.png` 和 `phone.png`。技术细节默认收起；图片 modal 的返回、Escape、backdrop、browser Back、真实 GLB viewer 与 `390 × 844` 单列布局通过。真实截图为 `gate12-workbench-browser.png`。
- 当前只问：“这套磁吸推牌外观可以作为新的正式模型吗？”批准前不得启用候选默认值、实现 runtime/Haptic、构建、安装或推送手机。视觉批准待确认，未推送手机。
- Gate 12 rev 1 后续否决：用户明确指出 Blender 与 Unity 的模型／纹理／最终成品差距过大。workflow rev 99 先退回 Gate 11 完整 parity，再保留 Gate 12 rev 1 的精确拒绝原文；Gate 12 当前 blocked，旧 shipping 模型继续默认启用。rev 1 场景、prefab、shader、九张图片、报告与 hash 均保留为 rejected evidence，没有删除或覆盖。
- Gate 11 rev 3 根因：rev 2 只修正圆边反射宽带并复用了 Unlit cap overlay，因此没有真正验证获批 Blender 材质。rev 3 继续使用完全相同的 `4,096`-triangle FBX 和已暂定接受的图案位置，删除所有 `ArtworkPreview` renderer；上下片分别读取独立 channel-pack mask。`MagneticCrystalShippingR2.shader` 直接组合 blood-red crystal、黑色 motif／perimeter、clearcoat／Fresnel／restrained iridescence 与连续环境反射；`MagneticSilverShippingR2.shader` 提供连续银色反射和可见接缝，均为 zero emission。
- Gate 11 rev 3 对齐结果：同机位 silhouette IoU=`0.98585328`；Blender／Unity blood-red median RGB=`123/67/69` 与 `128/60/64`，最大逐通道差=`7`；silver=`130/132/131` 与 `125/124/122`，最大差=`9`。三份主图 `geometry-comparison.png`、`artwork-comparison.png`、`material-comparison.png` 与总板 `gate11-rev3-parity-board.png` 分开显示“外形差异／图案差异／材质与反光差异”，不再以 bbox 总分代替用户视觉判断。
- Gate 11 rev 3 验证：Unity shipping-capable shader 编译与真实 capture 通过；`MagneticSlideTileParityRev3Tests`=`3/3`；`parity-review-validation.json` 通过几何、颜色、独立 mask、zero Unlit overlay 与 zero emission 检查。`MeshyEDC.unity` 在 rev 3 前后 SHA-256 不变；runtime、Haptic、build、install、device acceptance 均未开始。视觉批准待确认，未推送手机。
- Gate 11 rev 3 后续否决：用户接受 parent 的完整视觉诊断并明确要求整体 parity 不批准。外形／silhouette 足够接近并保持不动；图案位置继续接受；Unity face 过粉过亮、银色像灰白塑料、晶体平且不透明、黑边过厚且死黑。workflow rev 102 将 rev 3 标记 rejected；Gate 12 保持 blocked，旧 shipping model 继续默认。
- Gate 11 rev 4 几何／图案保持：仍为 `4,096` triangles、`4,124` vertices、bounds `0.050 × 0.031 × 0.012 m`；mesh digest=`c4c135c0d5ef1016bb7dd4b401a2aa0402332191d3797a7fc840ceafce26d834`，UV digest=`bb184ed4e9f6700c08bfba1e79f9a8f41c3f40ef69930e3b7e29911a62341733`。上下 motif R 通道逐字节不变，transform 不变；只把 Unity editable perimeter 内宽从 `64 px` 缩为 `42 px`，外边界 `0 px` inset，iPhone import 为 linear mipmapped `ASTC_6x6`。
- Gate 11 rev 4 材质：`MagneticSilverShippingR3.shader` 使用 `0.97/0.965/0.94` conductor tint、metallic `1`、roughness `0.03`、reflection strength `0.98`、reflection contrast `1.10`、diffuse lift `0.015`、neutral continuous cubemap + finite-softbox gradient、zero emission。`MagneticCrystalShippingR3.shader` 使用 `0.72/0.46/0.47` blood-red substrate、roughness `0.20`、clearcoat `0.92 @ 0.055`、iridescence `0.20`、depth variation `0.26`、refraction cue `0.12`、motif/border reflectance `0.36/0.44`、zero emission；它是 mobile opaque approximation，不宣称物理体积折射。
- Gate 11 rev 4 图像验证：clay silhouette IoU=`0.9860`、material silhouette IoU=`0.9869`、object SSIM=`0.7190`；Blender／Unity blood-red median RGB=`124/71/73` 与 `109/55/57`，DeltaE76=`16.06`；silver gradient ratio=`0.627`；7° crystal view response DeltaE76=`1.0`；clipped object pixels=`0`。`evidence/11-unity-parity/rev-004/` 提供 `gate11-rev4-geometry-board.png`、`gate11-rev4-artwork-board.png`、`gate11-rev4-material-board.png`、`gate11-rev4-final-board.png` 与差异热图。
- Gate 11 rev 4 验证：Unity 6000.5.6f1 / URP 17.5 target 3.0 shader 编译通过；focused EditMode=`4/4`，PlayMode=`1/1`；真实 capture report、mask report、perceptual report 全部 pass。`MeshyEDC.unity` capture 前后 hash=`c87e269f9f44f254797294444c0a2e64dd037177a2fa4e29d1bc1f9a530068fb`。当前只问“修正后的 Unity 物体现在是否像同机位的 Blender 目标？”视觉批准待确认，未构建、未安装、未推送手机。
- Gate 7 rev 8 权威链纠正：`evidence/07-material/rev-008/gate07-rev8-three-way-authority-audit.png` 以大图并排“原图标准 / Blender 当前 / Unity 当前”，标出血红晶体／图案与银色／黑边区域。原图只作材质线索，不与不同镜头做 silhouette 像素差；Blender 与 Unity 同机位继续只判断导入差异。报告记录全部 source asset ID、原始像素区域、归一化裁切 hash 和白平衡来源。
- Gate 7 rev 8 根因：旧 Gate 7–9 的数值检查证明“没有粉色、银色中性、没有剪白”，但只验证了 Blender 是否符合自身设定，未验证是否保留原图晶体的高频亮暗、透明深度、局部虹彩与银边分层反射。Blender red region luma std=`4.744`，而原图同类裁切为 `60.555`；该数值只作区域纹理提示，不冒充同镜头像素 parity。Gate 11 继续调 Unity 会稳定复现错误 Blender 目标，因此已停止。
- Gate 7 rev 8 DeliveryState：只创建审计板和报告，没有新 Blender 材质、没有 Unity 修改，也没有 gate approval。Gate 8–11 历史资产全部保留但标记 stale；Gate 12 rev 1 rejection 保留且继续 blocked。下一问题只有“是否同意退回第 7 关，以原图为标准重做 Blender 材质？”。视觉批准待确认，未推送手机。
- Gate 7 rev 9 回退决定：workflow/history/design bible 均逐字记录“退回，我们要优先保证模型的质量”。该决定只批准回退和重做，不是新材质视觉批准。
- Gate 7 rev 9 Blender：`evidence/07-material/rev-009/magnetic-slide-tile-material-r009.blend` 使用 polished silver `0.78/0.77/0.74`、metallic `1`、roughness `0.075`；deep blood red `0.18/0.003/0.008`、roughness `0.028–0.085`、IOR `1.52`、coat `0.35 @ 0.05`、transmission `0.07–0.24`、thin film `365–455 nm @ IOR 1.38`、mosaic scale `18`／detail `74`；完整黑边 `0.018/0.020/0.024`、metallic `0.24`、roughness `0.18`、coat `0.55`。所有模型材质 emission=`0`，无 bloom 或 exposure trick。
- Gate 7 rev 9 保持项：evaluated geometry digest 前后均为 `85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f`；物体矩阵、`4,096` triangles、尺寸、轴心及图案位置不变。上／下／外圈继续使用独立外部 Mask；打开状态下片图案仍可读。
- Gate 7 rev 9 来源与验证：用户 frame 01／05／10 为主标准，官方同款图只辅助判断材质行为。`source-fidelity-validation.json` 记录每张实拍的 steel sample 像素区域、neutral-pixel 筛选、样本量和 RGB channel scale；不声明未知生产化学。银色、晶体局部变化／角度色、黑边反射、图案锐度、打开状态可读性、零 emission／clipping、同相机灯光 recipe 和 mask identity 全部通过。
- Gate 7 rev 9 评审：主图为 `gate07-rev9-source-fidelity-review.png`，细节图为 `gate07-rev9-material-closeups.png`，可替换层为 `gate07-rev9-editable-layer-board.png`；`gate07-rev9-supporting-heatmap.png` 只作辅助，不是批准依据。当前只问“现在 Blender 看起来像原来的实物了吗？”。视觉批准待确认，未推送手机。
- 石墨双叶来源／结构复审：用户明确否决把五张助手生成目标图登记为 `user-reference`／`external-reference`，并指出历史第 4→5 关没有保持零件、角度和细节一致。`pipeline.json` 已将五图改为 `ai-target + assistant-generated`，将 Stage 1 设为 `missing`，把历史尺寸 claim 降为 `unknown`，记录 Stage 4、5、6 blocker 与 Stage 5 rejection；Stage 6 仍缺同源六视图、Workbench、尺寸、Pivot 和爆炸图。工具新增来源身份与“未直接承接上一关”红色提示。当前等待用户补回／重新指定石墨双叶真实权威输入；视觉批准待确认，未推送手机。

## Build 42：Collector Slab 合并进真实交易/揭晓链路 + 首个全流程验收视频（独立 worktree 分支 `codex/gacha-build42`；未合并 main，未构建或安装手机）

> **当前状态：2026-08-19，本 task 在独立 `codex/gacha-build42` worktree（非本仓库 `main`）完成：把已获批准的 Collector Slab 六款收藏盒资产与 P0 运行时定点合并进 Build 42 自己的权威 Gacha 交易链与六阶段揭晓（Build 42 与本仓库 `main` 的经济/交易模型不同，是受控 hunk 合并，不是整文件覆盖）；新增 acquisition-date schema；并在 iPhone 17 Pro Simulator 上用真实主 App + 官方 XCUITest 录出第一条完整「首页→抽卡商店→单抽→Pack→magnetic holder→真实 Unity 3D 揭晓→收下→回商店」连续视频，owned/draws 各验证从 0→1。全部为 Simulator 证据；未合并回 `main`、未构建、未安装手机，视觉批准继续 pending。**

- `PremiumDisplayCaseCapsulePreset.CollectorSlabLarge`（180×198×48 mm，圆角 16 mm）在 Build 42 的 `GachaRevealRules` / `PremiumDisplayCaseProductPresentation` 中替换旧 `RoundedSquareDeep`；30% 内容留白只对该 preset 生效（新增 `PremiumDisplayCaseCapsuleDimensions.ContentPaddingFraction` 按 preset 携带默认值），不影响其余 preset 原有 8% 留白契约。标签/银箔字段（edition、acquired date、collectible id、rarity 银箔）接入 `SetCollectorLabel`；tier 显式由 `GachaCollectorLabelRules.CollectorTier` 从奖品 rarity 映射，不使用等级猜测；collectible id 在没有权威编号时保持空，不伪造编号。
- 新增 acquisition-date schema：`GachaInventoryRuntime`（schema 1→2）新增按 prizeId 持久化的 `FirstObtainedAtUtc`；`GachaTransactionCodec`（2→3）新增 `StoredRow.firstObtainedAtUtc`，旧 payload 缺字段按空值兼容。`PrepareDraw` 只把新奖真实 UTC `O` 格式时间写入 durable pending row，不写 owned/pity/draw；重复 request 幂等返回同一时间；`AcknowledgePending` 在同一次 `Persist()` 内把 owned 与该时间一起提交；Build 41 遗留 v1 owned 记录没有该字段，读出为空并显示未知，不回填今天日期。该日期经 `GachaRevealDirector.Prepare(outcome, firstObtainedAtUtc)` 新增重载、`GachaRevealSession.TryCreate` 新增重载，一路传到 `GachaCollectorLabelRules.Create`，最终显示在真实 3D 揭晓标签上。
- Collector Slab 的 P0 资产（`PremiumDisplayCase.prefab` / `.fbx`、`BrushedMetal` / `LiquidGlass` / `LiquidGlassEdge` / 新增 `CollectorLabelPaper` 材质、shader、`PremiumDisplayCase.unity` 场景）已从本仓库 `main` 当前 shipping 版本整体复制到 Build 42 worktree，保留 Build 42 原有 GUID/`.meta`，只有真正新增的 `CollectorLabelPaper.mat` 带上新 `.meta`。合并过程中发现并修正了旧 partial merge 遗留的问题：`ContentPaddingFraction` 曾被错误地整体从 8% 改成 30%（影响全部 6 个 capsule preset，不止 Collector Slab）、`FeaturedBadge` 与 Collector 标签的若干坐标/材质命名断言仍停留在旧 `RoundedRecessWall/Fastener_/ChromeCollar_` 命名（新资产已改为 `Collector_ChamberRim_*` / `Polycarbonate_FrontShell` 等），均已按新资产真实结构修正而非放宽断言。
- 验证：Build 42 worktree 的 Unity EditMode 全量回归 `393/393 Passed`（含新增的 acquisition-date 幂等/恢复/ACK 单写/旧 schema 迁移专项测试），`git diff --check` 干净；已提交一个 clean commit `2deb6b27541a9e6e6ce2c242aa587302a16baa38`（分支 `codex/gacha-build42`，未合并、未 push）。以该 commit 为 `FIDGET_SOURCE_COMMIT` 做了 fresh Unity iOS Simulator 导出（manifest 精确为 Build 42 / `internalUnlimited` / `SimulatorSDK` / 该 commit），随后 `xcodebuild` 编译出可运行 `.app`（`BUILD SUCCEEDED`）。
- 官方 XCUITest（`FullAcceptanceRoundTripUITests/testLibraryToAcceptedPrizeRoundTrip`）在 iPhone 17 Pro Simulator（UDID `5BF378DF-5EAB-4885-87E1-2838F6DA6E46`）上对同一 shipping `.app` 连续跑了 8 次才通过；前 7 次都卡在同一个「磁吸收藏夹播放状态」无障碍断言上，但每次截帧与 UI 层级快照都证明 App 本身已正确完成撕包→收藏卡→真实 Unity 3D 揭晓→sheen 全流程（含标签正确显示 `ACQUIRED 2026-08-18` 当天真实日期）。定位到真实根因：Pack→Holder 交叠窗口只有 `packToHolderTransitionSeconds = 0.28 s`，测试脚本原用的 `XCTNSPredicateExpectation`（KVO）偶发来不及捕捉这个瞬时值；这是本仓库 `main` 当天新写、此前从未跑通过的测试基础设施缺陷，与 Collector Slab 改动无关。已把测试脚本里这一处改为可靠的直接轮询（该 XCUITest harness 位于 `/private/tmp`，不受版本控制，此修复不影响任何 shipping 代码）。第 8 次完整通过：`owned` 与 `draws` 各从 0→1，`status=idle`，phase history 精确为 `back|front|readable|exploded|prizeOnly|sheen|complete`，单抽按钮 ACK 后重新可用。
- 最终交付：`Artifacts/GachaPackShippingNativePreview/gacha-pack-build42-main-app-full-acceptance-roundtrip.mp4`（53.57 s，从第一帧干净 Library 画面剪到 ACK 后稳定的 Store 尾帧）、同目录 `-contact-sheet.png`（8 帧覆盖 Library/Store/Pack/Holder/3D 揭晓/收下/回商店）与 `-validation.json`（记录 source commit、EditMode 结果、XCUITest 8 次尝试与根因、owned/draws 前后值）。这是真实主 App Simulator + 权威 Unity/Swift receipt 链路的证据；没有 fake receipt、没有 standalone preview、没有空 `UnitySendMessage`。未合并回本仓库 `main`，未构建或安装到 iPhone，视觉批准继续 pending。

## 藏家 Profile / Library 单品身份 / 底部横排 Badge 入口（shipping 原生实现与自动化已通过；视觉批准待确认，未推送手机）

> **当前状态：2026-08-18，紧凑 Badge 入口只在 `isLibraryVisible=true` 的陀螺选择／轮播页。按用户最新反馈，左上 Profile 已移除头像、圆环和进度轨道，只显示一个 Collector Rank 数字；当前陀螺的 Lv.1–100 等级环缩为 `32 pt`，与名称、材质／皮肤名继续在 Library 标题区组成单品身份组。最多三枚正式 Badge 位于模型下方、分页点上方直接横向排列。新的真实全屏 shipping SwiftUI + Unity 场景预览与回归验证均已完成；视觉批准待确认，未构建或安装手机。**

- `CollectorProfileAvatar` 现在只绑定并显示 `collectorRank`：单个 `17 pt` 等宽数字、无头像、无 Circle、无 AngularGradient，也不再读取 `collectorFraction`；视觉虽精简，仍保留 `44 × 44 pt` 点击热区、既有藏家档案入口和 VoiceOver 等级语义。`ProductProgressionTopAvatar` 继续绑定当前玩具的权威等级／fraction，但可见尺寸由 `40 pt / 3 pt` 缩为 `32 pt / 2 pt`；离线成长页面级 XP 飞行仍读取其真实 window frame 锚点。成长值只飞向产品名旁的单品等级环，不飞向全局藏家 Profile。
- `ProductToyIdentityLockup` 组合单品等级环、产品名和材质／皮肤名，并放在 Library 选择页的轮播标题层级；镜钢四翼预览显示 `LV.27 / 镜钢四翼 / 基础合金`，三叶金属预览显示 `LV.39 / 三叶金属 / 冰银回纹 · 冷银镍铬`。`LibraryToyBadgeRow` 从当前模型 `toyBadgeCatalog` 选择最多三枚已获得／最近目标，以 `HStack` 在模型下方直接横排正式 `ProductRarityBadge` artwork 与短名，不包 card、不显示标题或完成数；本轮将 TabView bottom padding 从 `44` 调至 `60 pt`，整体上移 `16 pt` 并保持在分页点上方。点击使用同一 `ProgressionLevelDetailsSheet(initialSection: 1)`，没有第二套门槛、奖励或假完成度。
- Library 原有 `TabView` carousel、high-priority swipe、长按预览、页码、`查看收藏盒` 与 `进入…` 主 CTA 均保留；详情页 `ProductModeBar` 恢复为只承载既有模式切换，不再包含 Badge 入口。两套等级的运行时关系没有被重写：单品 Lv.1–100 和藏家 Rank 1–30 继续独立持久化；现有 `CollectorProgressionRuntime.RecordToyLevel` 在单品跨越权威里程碑时幂等贡献藏家经验。
- Unity 6000.5.6f1 中，更新后的 UI/source contract `RuntimeAndLiquidGlassUi_AreWiredForGrowthAndOfflineReturn` 为 `1/1 Passed`；除了原有 Library-only Badge 与双 CTA 契约，新增锁定 Profile 无 `collectorFraction / Circle / person.crop.circle / AngularGradient`、`17 pt` 数字与 `44 pt` 热区，以及单品等级环 `32 pt / 2 pt`。报告为 `Logs/CompactLevelUiFocusedTests.xml`，日志为 `Logs/CompactLevelUiFocusedTests.log`。首轮运行发现一个零字节 Burst 生成哈希缓存并在确认无活跃 Unity/Bee 进程后隔离；重新编译、重建缓存并正式运行后干净通过，未清空整个 Library 或任何源码。
- Badge 上移后的同一定向 UI/source contract 再次为 `1/1 Passed`，显式锁定 `.padding(.bottom, 60)`、模型下方横排、图鉴入口、轮播标识与双 CTA；报告为 `Logs/ProductIdentity/library-badge-raised-ui-results.xml`。当前九份 shipping Swift 源同时通过 `arm64-apple-ios15.0` iPhoneOS type-check。
- 同一生产源码在 iPhone 17 Pro Simulator 成功加载正式 Oxanium、Badge artwork 与本轮 top-down adaptive Unity 壁纸。镜钢四翼、三叶金属完整原图及全屏并排预览位于 `Artifacts/ProductIdentityNativePreview/`，确认文件为 `product-identity-library-contact-sheet.png`；它保留完整 Library 上下文，不是详情页裁切或概念 mockup。捕捉工具的首帧等待由 `3 s` 延长为 `5 s`，一次白屏首帧已被作废并重抓，不作为视觉证据。
- 差异审计：本 feature 只修改原生 Library 标题／Badge 入口组合、恢复详情模式栏原结构、对应 source-contract 测试、Design Bible／Liquid Glass guideline 和专用 Simulator 预览工具；没有修改 Unity 3D 模型、场景、物理、Haptic、XP 数值、Badge catalog、收藏盒、Gacha、Build 号或设备内容。被否决的详情页横卡与右侧竖排预览不再作为当前证据。下一门禁是用户确认当前真实全屏预览；批准后只交给总控纳入唯一 Build，安装后仍需验收安全区、轮播滑动、点击横排 Badge 进入图鉴、Collector Profile 跳转和成长值飞行终点。当前视觉批准待确认，未推送手机。

## Pack Carousel 同规格、选中态轻放大、浅倾斜与固定阈值吸附（shipping 原生实现与自动化已通过；视觉批准待确认，未推送手机）

> **当前状态：2026-08-18，用户已确认 `160 pt` 间距、中心最高和左右外倾方向，并进一步要求当前选中档稍微放大。六档继续共用相同 authored Pack 规格；当前 shipping 候选只把选中档 scale 从未选中的 `0.66` 提到 `0.70`（约 `+6.1%`）。每次 release 最多切换相邻一档；只有实际拖动位移达到固定 `56 pt` 才提交，未达到则吸附回当前档。变化已进入正式 `GachaSingleDrawSequenceOverlay`，不修改 Pack 资产、抽取概率、保底、票券、receipt、Rive 或 Unity 3D 揭晓。当前静态图及点击“选择 SIGNATURE”后的连续视频均来自 shipping 原生源码；新的选中尺度与后续动画视觉批准待确认，未构建或安装到手机。**

- `GachaPackCarouselRules` 是 layout、焦点 scale 与 release 判定的唯一 source of truth：已确认水平间距 `160 pt`；未选中 `0.66`、选中 `0.70`；中心落差为 `0`，第一／第二相邻档分别下落 `8 / 16 pt`；左侧最大 `-3.5°`、右侧最大 `+3.5°`，统一向外展开；commit 阈值 `56 pt`、spring `0.28 s / 0.82 damping`。中心和侧项共用同一个 `244 × 326` Pack visual 与 `166 × 226` presentation frame；放大只表达当前焦点，不改变 tier 资产规格。
- 拖动过程用连续 position 驱动水平位移、线性浅落差与有限倾角；release 只读取 `value.translation.width`，不读取 `predictedEndTranslation`，因此短促甩动不会越过固定门槛。`nextIndex` 只返回 `-1 / 0 / +1` 对应的相邻档并在首尾 clamp；低于阈值时 selected tier 不变，carouselDrag 通过同一 spring 回零。
- 验证：七份 shipping Swift 在 iPhone 15 Simulator target 下 DEBUG／Release 均以 `-warnings-as-errors -typecheck` 通过；同一源码再链接官方 RiveRuntime `6.23.1` 完成真实 shipping-source build。纯 Swift `GachaPackRulesHarness` 为 `25/25 Passed`，覆盖 `0.70 / 0.66` 焦点 scale、`160 pt` 间距、中心／第一／第二相邻档 `0/8/16 pt` 落差、左右向外倾角、`55.999 / 56 pt` 边界、一次一档与首尾 clamp；Unity EditMode `PackCarouselUsesSelectedEmphasisShallowOutwardArcAndFixedReleaseThreshold` 为 `1/1 Passed`，XML 为 `Artifacts/GachaPackShippingNativePreview/pack-carousel-editmode-tests.xml`。
- 当前 shipping 静态预览为 `Artifacts/GachaPackShippingNativePreview/00-pack-carousel-selected-emphasis-outward-arc.png`。以官方 RiveRuntime `6.23.1` 运行的点击后连续视频为 `Artifacts/GachaRiveShippingPreview/gacha-rive-shipping-flow.mp4`：H.264、`1206 × 2622`、`13.112 s`；联系表为同目录 `gacha-rive-shipping-flow-contact-sheet.png`。同一 request `8b2ca4e4-e0c3-4517-8b5e-264218790f9d` 贯穿 SIGNATURE selection、draw、DEBUG 权威 receipt、selection `animationSignal`、`0.55` 撕包回弹、`0.75` commit、空包退出、holder `animationSignal` 与 Premium Display Case handoff；两个 Rive 阶段均无 watchdog。
- 独立 preview host 只在 `--preview-authoritative-receipt` DEBUG 参数下从真实 `DrawGachaFromNativeUi` payload 取回 request ID，并把同 ID 的测试 receipt 送入生产 `GachaStoreModel.ingest`；它不复制抽取状态机、不修改 Release，也不把 standalone SwiftUI 画面冒充 Unity 3D。上述 `13.112 s` 视频仍可证明旧 request／Rive completion 链，但其中 Pack 完全退出后才硬切 holder、并继续显示旧 WHATNOT 品牌外观，已被本轮用户决策替代，不能作为当前视觉批准证据。
- 本轮 shipping `GachaSingleDrawSequenceOverlay` 已把 `.tearPack / .holderRive` 合并为同一个 `gacha-pack-holder-transition` 舞台：`0.62` commit 当帧 exact-once 进入 holder gate，Pack 以 `0.34 s` 下退并在 `0.28 s` 内淡出，holder 从后方同时淡入；约 `0.38 s` 后才记录 `pack-exit-complete / pack-holder-overlap-complete`。Rive 允许不可见预热首帧，但 `playbackEnabled` 只有在 gate 进入 `.holderRive` 后才触发；Reduce Motion 仍保持 commit → 静态 holder → receipt 双门的相同因果顺序。
- 旧 Rive magnetic-holder 画面现在固定为 `opacity 0.001`，只保留真实 `animationSignal`／watchdog completion clock，不再参与可见输出。唯一可见 holder 是完整的 `GachaProductOwnedMagneticHolderSurface`：透明石墨／银 slab、真实 `product-thumbnail-metal-three-blade` 主圆窗、`METAL THREE-BLADE / GEM/MINT 10 / #00000001`，整块 holder 共同完成位移、缩放与 3D 倾斜；不存在屏幕固定的 identity overlay，holder 退出后也不会留下悬浮标签。AX 保持 `gacha-holder-product-identity`。该固定 toy emblem 是 presentation-only 身份，不随 receipt 变化，Rive 仍不接收 prize、kind、rarity 或 receipt。
- 早期 Unity source contract `GachaRiveIntegrationTests` 为 `7/7 Passed`（`Logs/GachaHolderTransitionIdentityContracts.xml`），它验证连续舞台和身份门禁，但早于最终完整 holder surface。最终源码在官方 RiveRuntime `6.23.1` 下 iPhoneOS arm64 iOS 15 DEBUG／Release `-warnings-as-errors -typecheck` 通过；Swift Gate `77/77`、Pack rules `25/25`，最终 Roslyn source contract `30/30`，明确锁定双 Rive 层不可见、唯一完整 product-owned holder、无旧固定 overlay、`0.28 s` 交叠和 exact-once completion。
- 当前真实 shipping-source Simulator 视频为 `Artifacts/GachaRiveShippingPreview/gacha-pack-to-product-holder-transition.mp4`：H.264、`1206 × 2622`、60 fps、`7.25 s`，SHA-256 `64ad68f0bfc3cdbe52d1f3101e6a53704e95848f12ec653778cf1738934497ab`；联系表为同目录 `gacha-pack-to-product-holder-transition-contact-sheet.png`。逐帧可见 Pack 与 holder 同屏交叠后 Pack 退出，holder 保留评级／编号、显示三叶陀螺且无 WHATNOT／W／黄绿色。该证据是直接编译 shipping Swift + 官方 RiveRuntime 的 Simulator 视觉候选，不冒充 main App Unity receipt 端到端；后者继续由既有真实 storefront／Unity XCUITest 证明。当前等待用户对新转场与 holder 的视觉批准，未推送手机；`56 pt` 阈值与误触仍需真机接受。

## 单抽 Pack carousel → Rive → 撕包 → magnetic holder → 真实 Toy（历史端到端链路与新 holder Simulator 候选均已生成；视觉待确认，未推送手机）

> **当前状态：2026-08-18，本轮 shipping runtime 已按用户确认顺序改为：点击“单抽”只进入六档近直线浅倾斜 Pack carousel；Pack tier 仅为 presentation metadata，不进入 draw payload；确认 Pack 后才以稳定 request ID exactly-once 请求 Unity 权威抽取，并依次播放 selected-Pack 中性 Rive cue、`0.62` 门槛撕包及 Pack 下退、可见 product-owned magnetic holder，最后只把同一 receipt 中的真实 Toy 交给 Unity 3D reveal。Swift 不再在 handoff 后立即清 receipt；只有 Unity `GachaRevealDirector.revealCompleted` 才按同 request ID acknowledge。Canonical 奖品为 `canyon-heir-metal-three-blade / 三叶金属陀螺 / Toy / toy/metal-three-blade`，ownership、receipt 与 3D content 一致；任意 sticker／skin／其他 prize 会保留 pending 并被明确拒绝，不能借该模型假展示。此前 fresh Development Simulator export、main App Xcode Debug 与真实 storefront XCUITest 已证明同 request、Rive completion、无 watchdog 和真实 `metal-three-blade` Unity reveal；selection cue 继续使用无品牌的 `rotate-line` child artboard。用户指出旧视频从 Pack 到 holder 缺少 transition，并明确要求保留评级／编号但移除 WHATNOT Logo 与黄绿色、换成一款陀螺。本轮已经以同舞台 `0.28 s` Pack／holder 可见交叠、完整三叶金属 holder surface 和中性石墨／银替代旧画面；真实 shipping-source Simulator H.264 与联系表已生成，逐帧未见硬切、旧 Logo 或悬浮标签。尚未构建、安装或推送手机；新视觉批准待确认。**

- 本段覆盖本节下方旧的“tap 后立即前置 Rive／本地 UUID 未进入 Unity payload”描述。`GachaSingleDrawGateState` 当前阶段为 `choosingPack → selectionRive → tearPack → holderRive → waitingForReceipt → handoff`；20 秒 receipt timeout 只置 recovery 标志并保留原视觉 phase，迟到 receipt 不会把 selection／tear／holder 卡在不存在的 recovery 画面。Pack carousel、六档 tier、`gacha-pack-state=sealed/committed/exited`、0.55 回弹与 0.75 commit 预览路径均复用 shipping 阈值和一次性 commit gate；Rive 从未接收 rarity、prize 或 receipt。
- `GachaInventoryRuntime.DrawOnce` 把库存变更与 durable pending receipt 在一次 `PlayerPrefs.Save()` 中提交；同 request 重送／重载返回同 receipt，另一 request 在 ack 前拒绝。Development Simulator 预览资金入口必须同时满足 Swift DEBUG launch arg `--preview-gacha-funding-token=metal-three-blade-v1` 与 Unity `Debug.isDebugBuild`：Swift 只在 exact argument 匹配时把 `metal-three-blade-v1` 作为 `RequestGachaStateFromNativeUi` payload 显式桥接，C# 不依赖 iOS managed argv，inventory 再校验 exact token 后持久化赠送一次真实单抽券；错误 token、Release 或重启重复调用都拒绝，且后续仍由正常支付、pity、ownership 与 receipt 事务扣券。DEBUG-only `--preview-authoritative-metal-three-blade` 只控制真实 catalog Toy 结果，不允许 presentation tier 改经济结果。`PresentGachaPrizeFromNativeUi` 同时校验 receipt prize ID、`Kind == Toy` 与 `contentReference == toy/metal-three-blade` 后才实例化 `ThreeBladeDisplayPrizeFactory`。
- 本轮冻结验证：官方 RiveRuntime 6.23.1 下七份 shipping Swift 以 `arm64-apple-ios15.0-simulator -warnings-as-errors -typecheck` 通过；纯 Swift gate harness 为 `63/63 Passed`（覆盖 selection／tear／holder／waiting 四个 timeout/late-receipt 表项）；Unity 6000.5.6f1 本轮组合 XML `Logs/GachaPackRiveRuntimeFocused-Initial.xml` 为 `26/28`，其中 inventory `11/11`、native bridge `3/3`、真实 3D reveal `8/8` 均通过，两个失败仅为已过时的 source-text 断言。修正断言后，`GachaRiveIntegrationTests + GachaStorefrontIntegrationTests` 为 `7/7 Passed`，证据 `Logs/GachaPackRiveSourceContracts.xml`。最后一次重复 inventory runner 停在 Unity PerformanceTesting prebuild、未产生新 XML，已安全终止且未误报；不再启动长跑。
- Development 预览资金入口新增后，Unity source-contract 定向回归 `5/5 Passed`（`Logs/GachaPreviewFundingSourceContracts.xml`）；一次性资金行为定向测试 `DevelopmentPreviewTicketFundingIsDebugTokenGatedAndPersistentOneShot` 为 `1/1 Passed`（`Logs/GachaPreviewFundingBehavior.xml`），覆盖 Release flag 拒绝、错误 token 拒绝、正确 token 只赠一次以及重载后不重复叠加。生命周期与 bundle lookup 的最终 source-contract 为 `7/7 Passed`（`Logs/GachaRiveLifecycleSourceContracts.xml`）；fresh Development Simulator export 成功，证据为 `Logs/GachaRiveLifecycleSimulatorExport.log`，且导出的 Rive／Storefront Swift 与 workspace source 逐字节一致。main App Xcode Debug build 为 `BUILD SUCCEEDED`，真实 XCUITest `testRecordShippingCarouselRivePackAndRealUnityReveal` 为 `1/1 Passed`（41.719 秒），最后可访问性根为 `model=metal-three-blade / prize=canyon-heir-metal-three-blade / kind=Toy / contentReference=toy/metal-three-blade`。连续视频与统一日志位于 `Artifacts/GachaPackRiveUnityContinuousPreview/gacha-pack-rive-unity-continuous-flow.mp4` 和同名 `.log`：selection 与 holder 各自的 background／foreground 均完成 asset resolve、四张 embedded image decode、首帧、同步 trigger、`Idle → in → Idle`，各恰好一次 `completed reason=animationSignal`，watchdog 为零；holder 完成与 Unity handoff 使用同一 request `fd8838bf-cb74-404f-bced-8b848ef6c6c0`。外层 capture wrapper 因其统一日志谓词未收到 Unity `Debug.Log` 的 preview-authoritative marker 而返回 65，未误报为 wrapper 全绿；内部 XCUITest 与运行时门禁本身通过。仅安装专用 Simulator，未触碰手机。
- 最终视觉候选的官方 RiveRuntime 6.23.1 Swift DEBUG／Release `-warnings-as-errors -typecheck` 均通过，Swift gate harness `63/63 Passed`；Pack rules 的旧基线为 `9/9 Passed`，当前等尺寸／浅倾斜／固定阈值版本已提升为上节 `19/19 Passed`；最终 Unity source-contract `7/7 Passed`（`Logs/GachaRiveHaloFinalSourceContracts.xml`）。fresh Development Simulator export 为 `Build Finished, Result: Success`（`Logs/GachaRiveHaloFinalSimulatorExport.log`），导出的 Rive／Storefront source 与 workspace 逐字节一致；main App Xcode Debug 为 `BUILD SUCCEEDED`。真实 XCUITest `testRecordShippingCarouselRivePackAndRealUnityReveal` 为 `1/1 Passed`（59.255 秒），最终 request `4b8af88a-de79-4356-b22e-0db08065a00f` 从 draw、receipt、selection、tear、holder、handoff 到 Unity reveal 保持一致，最终 root 为 `model=metal-three-blade / prize=canyon-heir-metal-three-blade / kind=Toy / contentReference=toy/metal-three-blade`。`99.178333 s` 连续视频、统一日志与六帧联系表分别为 `Artifacts/GachaPackRiveUnityContinuousPreview/gacha-pack-rive-unity-continuous-flow.mp4`、同名 `.log`、`gacha-pack-rive-unity-final-candidate-contact-sheet.png`；日志证明 selection halo 首帧与 holder 双层均以 `animationSignal` 完成且无 watchdog。联系表逐帧确认 carousel 中心与左右 Pack、前景 Pack 后方的可见 halo、撕包下退、完整 holder 与真实 Unity 3D 连续性。外层 capture wrapper 仍因 Simulator unified log 不包含 Unity `Debug.Log` 的 preview-authoritative marker 返回 65，因此未误报 wrapper 全绿；内部 XCUITest、运行时门禁、录屏与日志完整通过。仅安装专用 `393 × 852` Simulator，未触碰手机。

- Canonical Rive 资源仍为 `Assets/Plugins/iOS/Rive/gacha-single-draw-jumbotron.riv`，`357120 bytes`，SHA-256 `da5ba78f63c09ea538d214f7bcdd520a852fc77232bf47ef31606106136c7717`；已与用户原文件逐字节 `cmp` 一致。该资源在 holder 阶段只承担不可见的 completion clock，旧 holder 矢量与 embedded Logo 不再成为可见成品。可见 holder 直接从 App bundle 读取正式 `product-thumbnail-metal-three-blade.png`，缺失时不回退旧品牌图；整个流程不依赖 CDN 或运行时网络。
- `IosBuildPipeline.ConfigureGachaRiveRuntime` 在每次 Unity iOS export 时复验上述 hash、把 `.riv` 复制到 App main bundle，并通过 Unity 6 `PBXProject` 添加官方 `https://github.com/rive-app/rive-ios` SwiftPM 版本范围 `6.23.1 ..< 6.24.0`。`RiveRuntime` 同时连接 `UnityFramework`（Swift source import）与 main app target（动态 framework embed consumer）；官方 6.23.1 release tag `4b1f435c...` 的真实 Simulator XCFramework 已用于编译验证。
- `FidgetGachaRivePresentation.swift` 不再依赖错误的 default artboard。它仍以 `375:812` contain 比例加载 `background/mint-slab` 与 `foreground/mint-slab` 两个 `Main` state machine，供预热、状态机周期与 completion 使用；commit 前不播放，commit 后才同步触发，但 magnetic-holder 阶段两层均固定 `opacity 0.001`。可见输出由同文件的 `GachaProductOwnedMagneticHolderSurface` 独立负责，真实三叶 thumbnail、评级和编号与 holder 使用同一 Transform／alpha／退出生命周期，不存在屏幕固定盖层。Rive 层仍没有 `GachaReceiptRow`、prize id、kind、rarity 或 receipt 输入，不会二次 roll、改概率、改 receipt，也不替代 Pack 或真实 3D 奖品。Latin／数字复用 ProductTypography/Oxanium，无 tracking／kerning。
- `FidgetGachaRiveGateRules.swift` 是确定性双门状态机：tap 时先创建本地 transaction gate 再调用一次 `model.draw`；receipt-first 与 animation-first 都保持等待，只有两者齐备才进入原揭晓。`markHolderAnimationFinished` 在 `.tearPack` 前严格拒绝，`packToHolderTransitionSeconds = 0.28` 是当前 shipping 交叠调校。split export 的 root `animationEnded` listener 继续保留，但真实 6.23.1 runtime 中该 root trigger 不会从两个子状态机回传；因此 shipping completion 同时接受 asset 自身每层实测的 `Idle -> in -> Idle` 周期，并且只有背景和前景都在见过 `in` 后返回 `Idle` 才发出 `.animationSignal`。12 秒 watchdog 只作为失联安全出口，Simulator shipping smoke 明确拒绝任何 watchdog 完成。Reduce Motion 使用 120 ms 无奖品中性过渡。后台暂停 Rive，恢复到 active 才允许揭晓；视图关闭会移除 trigger listener、关闭 auto-bind 并暂停 runtime。
- Fanatics／Mobbin 候选已落入共享 token 和正式 storefront：Primary 固定中性白 `52 pt` 高／`26 pt` 圆角并使用 Oxanium 单行动作文字，票券消耗和余额移到按钮外；“十抽后续开放”为 `26 pt` 静态 Status Tag，不再伪装成 disabled Button；页内 Filter Chip 为 `32 pt` 可见／至少 `44 pt` 热区。间距使用同一 `4 pt` 网格 source of truth（`16 pt` section、`20 pt` page inset、`24 pt` section group）；Primary／Secondary 具备 rest、`0.98 / 120 ms` pressed、loading、disabled、success、error 合同，Primary 永远使用中性白表面，不把业务 accent 扩成大面积品牌色。所有 shipping Gacha Swift 已清除 `.font(.system...)`、tracking 与 kerning；Rive／恢复／揭晓覆盖层会从 VoiceOver 隐藏底层 storefront 并标记 modal，Rive surface 保持原始 `375:812` 全幅 contain，在窄屏按容器收缩而不裁切。
- 视频自动化只存在于 `#if DEBUG`：`--preview-auto-single-draw` 等待页面和 catalog 后只调用一次 production `startSingleDraw(series)`；`--preview-auto-open-pack` 先保留约 `1.2 s` sealed Pack，再调用 production `commitPackOpen()`。两条 hook 都不复制 gate、经济或 receipt 逻辑，Release 编译完全无行为。
- receipt 等待 20 秒超时后不清除事务，也不允许再抽：timeout 只置 recovery 标志并保留当时的 selection／tear／holder／waiting 视觉 phase；迟到单条 receipt 仍回到同一 gate，无 gate 的单条 receipt 不再误走多抽 sheet。稳定 request ID 已显式进入 Unity payload，并贯穿 draw、receipt、handoff、reveal completion 与 acknowledge；当前证据覆盖同进程及 view 恢复，process-kill 后完整 UI 重建仍作为 `FDB-GAC-008` 的 Device Accepted 边界保留，不误报为真机验收。
- 历史验证：纯 Swift gate harness 旧基线为 `63/63 Passed`；此前 shipping Swift 已用官方 RiveRuntime 6.23.1 `arm64-apple-ios15.0-simulator` DEBUG／Release type-check，并完成 fresh Unity Development export、真实 main App XCUITest 与 `Artifacts/GachaPackRiveUnityContinuousPreview/` 连续录屏。那些证据继续证明经济、request、Rive lifecycle 与 Unity handoff，但其视觉内容早于本轮连续交叠／中性 holder 修订，只能作为历史链路证据。最终当前源码验证为 Gate `77/77`、Pack `25/25`、Roslyn source contract `30/30`，以及直接编译 shipping Swift + 官方 RiveRuntime 的 `gacha-pack-to-product-holder-transition.mp4`／联系表；该新视频证明视觉修订，但不冒充 main App Unity receipt 端到端。
- 下一门禁：用户确认当前新 H.264 中 Pack／holder 可见交叠、三叶 holder、评级／编号和中性调色。明确视觉批准后再由总控纳入唯一 build；随后 fresh main App Simulator 回归同 request 日志顺序 `pack-holder-overlap-start < pack-exit-complete / pack-holder-overlap-complete < holder-rive-completed`、无 watchdog，再进行安装、启动、背景恢复和 iPhone Device Accepted 验收。视觉批准待确认，未推送手机。

## Collector Slab 六款真实收藏盒与三款磨砂金属材质（shipping 视觉已批准；未构建、未安装手机）

> **当前发布状态：2026-08-18，用户在当前 task 表示“这效果还可以”，并在总控明确确认“这个 collector 是可以的”，构成 Collector Slab 最终真实 shipping 视觉批准。真实 Blender／Unity 实现、日期 schema、六款模型与三款表面材质保持前述测试状态；两张获批 shipping 联系表已登记为 Design Bible [V08][V09]。本轮仍未构建、未安装手机，Device Accepted 与真机材质／可读性／性能验收继续 pending。**

- `CollectorSlabLarge` 现在是统一纵向收藏盒：Unity 展示舱 `180 × 198 × 48 mm`、圆角 `16 mm`；Blender 壳体 `216 × 304 × 59 mm`，共 `25 meshes / 8 layers`。外观为双层阶梯磨砂聚碳酸酯、顶部实体标签、黑色植绒内托与单条稀有度窄金属箔；旧四角黑扣与抢占主体的中央小胶囊已移除。Blender validator 已通过，证据为 `Artifacts/PremiumDisplayCaseValidation/blender_validation.json`。
- 六款均使用 renderer-only 的真实 shipping 产品快照；case 不改奖品 mesh、pivot、parent、collider、机制状态或交互。内容 fit 只按显示平面的 XY bounds 等比缩放到限制维度 `70%`，Z 只用于居中、不再因 90° 展示姿态错误缩小平面型产品；没有拉伸。六款 profile 均关闭自主 idle，保留各自权威正面朝向。
- 顶部实体标签显示真实产品英文名、edition／finish、rarity／level、最高 Badge 和首次获得日期。Gacha acquisition 与 Collector discovery 已升级为 versioned date schema；新记录只写第一次时间，旧 v1 拥有记录安全迁移为未知并显示 `ACQUIRED —`。稳定 collectible ID 仅在存在权威值时显示，不用样例号或当前日期伪造。
- 三款真实产品只改变材质 source of truth：三叶金属使用细腻喷砂钛响应，镜钢四翼使用克制的缎面钢／径向高光，石墨双叶保持 `#3A3D40`、metallic `1`、roughness `0.76` 的各向同性磨砂。没有修改它们的几何、轴心、层级、碰撞、物理或 Haptic；其余三款保留既有批准材质。
- Blender／Unity 聚焦回归证据：Collector Slab、日期迁移、Gacha、材质与架构组合测试 `92/92 Passed`，报告为 `Logs/CollectorSlabFocusedEditMode.xml`；最终 XY fit、prefab、profile、shader、标签、尺寸和首帧 settled capture 门禁 `30/30 Passed`，报告为 `Logs/CollectorSlabDisplayCaseFinalEditMode.xml`。首轮完整 EditMode 为 `319/324`，其中四项本 feature 旧断言已修复；剩余一项为并行 SwiftUI 收藏标题断言，不作为本 feature 的通过证据，未误报完整回归全绿。
- 真实 GPU shipping Unity 已输出六款各 `hero / top / left / right / low / phone`，共 36 张 PNG，位于 `Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/`；最终总览 `collector-slab-all-products-shipping-final.png` 与三款材质 hero／左斜视 `collector-slab-material-shipping-final.png` 已在 2026-08-18 获明确视觉批准。稳定副本为 `Docs/DesignBibleAssets/collector-slab-six-products-approved.png`（[V08]）与 `collector-slab-materials-approved.png`（[V09]），已逐字节 `cmp` 并登记像素／SHA-256。下一步由总控纳入唯一 Build；当前没有单独构建或安装手机，iPhone 玻璃透射、比例、文字可读性与性能仍待 Device Accepted。

## Build 39 正式单 App 已覆盖安装（商店 + Library 手势；待用户真机手感验收）

> **发布结论：用户明确拒绝独立 Demo 与正式 Fidget Spinner 双 App 并存，要求把商店并入 `com.jiaweizhou.fidgetspinner.codex`，并同时带上 Library 左右切换手势修复。唯一正式 Build 39 已完成 Unity DeviceSDK 导出、Xcode Release 编译、签名校验、Simulator 连续左右滑验证、CoreDevice 覆盖安装、启动和设备库存回读；独立 `com.jiaweizhou.fidgeting.single-draw-demo` 已从 iPhone 删除。手机当前只保留并运行 `Fidget Spinner 0.1.0 (39)`。**

- 新的 shipping `GachaStoreView` 继续消费真实 `GachaStoreModel`、Unity catalog、票券/齿轮币/保底/拥有状态与 receipt，不移植独立 Demo 的假 catalog 或本地抽取序列。顶部提供纯文字“返回主页”；“抽取 / 兑换”和“收藏”为真实页面；单抽固定只发送 `count=1, useCoins=false`，十抽为不可交互的“后续开放”，进入页面不初始化 StoreKit coin shop。
- 主 Banner 与三张皮肤卡使用随包真实图片，统一等比 `scaledToFill + clipped`；页面保持中性黑灰，蓝/绿/紫/金只用于稀有度短线/小面积状态语义。已删除不可点的“可购买商品”伪按钮；概率、保底与重复兑换规则统一进入二级 sheet；产品级文字 CTA 不包含装饰 icon。
- 单条真实 receipt 触发背面收藏盒、翻正、奖品可读、盒体散开、仅奖品、过光与完成七个内部状态（对外为六拍叙事），完成后才出现纯文字“收下”。多条 receipt 继续使用结果列表；动画不重算概率、不二次扣券、不伪造 StoreKit 购买结果。
- Library 手势使用明确 swipe session：`Begin / Progress / Commit / End`，Swift 逐帧以 `translation.width` 原符号驱动 Unity；达到阈值先提交再切模型，取消/边界才回弹；C# gate 拒绝过期 End。左滑旧模型同向左退、新模型从右进入，右滑镜像，不再依赖旧版固定 `0.08 s` 猜测窗口。
- 当前六个 shipping Swift 文件以 `arm64-apple-ios15.0` type-check 通过。隔离 Unity 6000.5.6f1 聚焦回归为 `13/13 Passed`：`GachaStorefrontIntegrationTests 1/1`、`GachaNativeBridgeTests 2/2`、`SpinnerEnvironmentTests 10/10`。最终正式源码的 Simulator Release build-for-testing 为 0 errors；XCUITest `testFastLeftRightLibraryRoundTripWithoutRebound` 为 `1/1 Passed`，真实 page 1→2→1 左右往返无提交回摆，证据位于 `Artifacts/LibrarySwipeLatestCandidate/` 与 `Logs/LibrarySwipeLatestCandidate/`。
- DeviceSDK Release App 为 `com.jiaweizhou.fidgetspinner.codex`、`0.1.0 (39)`，签名 Team `2RJ2CW6NK5`；`codesign --verify --deep --strict` 通过，签名包约 `390 MiB`。CoreDevice 于 2026-08-13 覆盖安装成功，设备库存回读只显示 `Fidget Spinner 0.1.0 (39)`，独立 Demo 不再存在；正式进程 PID `12512` 正在运行。
- 正式 native 实现的 Simulator 首屏为 `Artifacts/GachaShippingNativePreview/01-storefront.png`；单抽六阶段联系表与完整录屏为同目录 `gacha-reveal-contact-sheet.png`、`single-draw-reveal.mp4`。下一步由用户直接在 Build 39 真机验收 Library 触摸延迟/连续往返、返回主页、单抽防重复扣券和真实 receipt 揭晓；安装成功不替代这些人工手感与端到端业务验收。

## 独立 Single Draw 商店 Demo 已退役并从 iPhone 删除（历史记录）

> **历史结论：该独立 Demo 曾用于手机视觉审核，但用户明确要求停止双 App 交付。其商店信息架构已接入唯一正式 Fidget Spinner Build 39；`com.jiaweizhou.fidgeting.single-draw-demo` 已于 2026-08-13 通过 CoreDevice 卸载，设备库存复核确认不再存在。**

- Demo 包含纯文字“返回主页面 / 进入机巧工坊”、中性黑灰商店首屏、等比 `aspectFill` 主 Banner、已删除的不可点“可购买商品”伪按钮，以及背面、翻正、奖品可读、盒体散开、仅奖品保留、过光完成六阶段单抽演示；它不连接 StoreKit、正式 Gacha 数据或 Unity bridge。
- `xcodebuild` iPhoneOS Release 以 `** BUILD SUCCEEDED **` 完成；独立 Team provisioning profile 为 `com.jiaweizhou.fidgeting.single-draw-demo`，`codesign --verify --deep --strict` 通过，签名 App 为 `4.4 MiB`，并包含六张规范化命名的揭晓资源。
- 历史上 iPhone 15 Pro Max `JW` 曾同时存在 `SingleDrawStoreDemo 1.0 (1)` 与正式 `Fidget Spinner 0.1.0 (38)`；该双 App 状态现已终止，不得再作为发布方案复用。
- Demo 的假 catalog、本地抽取序列与无 StoreKit 隔离实现没有进入 shipping；Build 39 正式商店继续消费 Unity 权威数据链。独立 Demo 目录仅保留为历史视觉证据，不再安装或启动。

## Build 37 已覆盖安装到 iPhone（统一候选；待用户解锁后真机体验验收）

> **发布结论：用户于 2026-08-11 对正在进行的候选给予统一发布授权，不再要求逐项确认。总控等待相关任务收口后，从不可变发布快照 `016909f0bca810460aec8dec734179050a31e096` 生成唯一 Build 37；Unity DeviceSDK 导出、全量回归、Swift iPhoneOS 类型检查、Xcode Release、签名校验、CoreDevice 覆盖安装和设备库存回读均已完成。手机实际库存确认为 `Fidget Spinner 0.1.0 (37)`。设备在安装后处于锁屏状态，因此没有误报自动启动或真机视觉/触感验收。**

- 本次包含：收藏盒六款磁吸推牌基准一致性、场景壁纸有限双页与单一 CTA、离线成长结算/升级高光、磁吸扇牌完整卡角/低矮轴承帽/双层背轨/整体质心手势、Dragon Scale EDC 对 `gold-four-wing` 槽位的限定替换。无界推牌 goggle 开孔候选因 Unity shipping Round 5 视觉门禁失败，已从共享接入和 Build 37 快照排除。
- 发布集成阶段首先捕获 Fan Card 详情视口占比 `0.5959 < 0.6000` 的真实回归；最终只为相机引入 `0.992` 的 sweep bounds 缩放，物理/碰撞范围不变。重建 shipping 场景后，Fan Card 与环境专项 `30/30` 通过；完整 fan-card guardrail 继续确认背轨外轮廓最小净空 `7.590 mm`。
- 最终 iPhone target 定义下的完整 EditMode 回归为 `306/306 Passed`；在 iOS 序列化前后和最终符号状态分别重复验证，最终报告为 `Logs/Build37Evidence/FinalIosTargetFullEditModeTests.xml`。五个 shipping Swift 文件以 `arm64-apple-ios15.0` type-check 通过。Unity manifest 锁定 Bundle `com.jiaweizhou.fidgetspinner.codex`、版本 `0.1.0 (37)`、DeviceSDK、非 Development 和六个 shipping 场景。
- Xcode Release 日志以 `** BUILD SUCCEEDED **` 结束；签名包约 `382 MiB`，`codesign --verify --deep --strict` 通过，Team 为 `2RJ2CW6NK5`。设备安装结果为 success，新容器 `C2C5B2E0-B9D4-4EDF-B7A2-7597D5C62E0F`；安装后库存回读确认版本/Build `0.1.0 (37)`。完整证据归档于 `Logs/Build37Evidence/`。
- iPhone 15 Pro Max `JW` 安装后回读 `passcodeRequired=true`，所以本轮没有强行启动。下一步仅需用户解锁后自行打开 App，验收动画节奏、有限双页滑动、六款收藏盒、扇牌指尖/Haptic 和 Dragon Scale 真机材质/性能；安装完成不替代这些人工验收。

## 镜钢四翼机械轴心与石墨双叶真实比例（实现与隔离验证完成；视觉批准待确认，未推送手机）

> **当前发布状态：Build 37 中 `gold-four-wing` 的 Dragon Scale 可见主体、轴承外圈与固定指盖整体偏离真实旋转轴 `9.081 mm`，造成旋转时偏心；`graphite-two-lobe` 的实体仍是正确的 `50 × 24 × 18.68 mm`，但详情与 Library 相机曾把它独立放大到接近 `85 mm` 圆形陀螺的画面占比。当前候选已分别修正机械原点和产品间真实比例；视觉批准待确认，尚未进入新 Build，未推送手机。**

- Dragon Scale 场景构建不再用非对称三翼外包围盒中心平移模型，而是保留 Blender/FBX 的机械原点，仅将主体等比缩放到目录统一的 `85 mm` 参考直径。shipping 场景中 `Rotor_Root`、`BearingOuterRace`、`Fixed_Root` 与真实 `RotorDynamic` 轴心的平面偏移均从 `9.081 mm` 收敛到 `0.000 mm`；旋转层、轴承层和固定指盖层继续保持原有父子关系，未改 Rigidbody、碰撞、角速度或 Haptic。
- 石墨双叶的模型网格、碰撞和场景 Transform 没有被错误放大，根节点 world scale 仍为 `1`。`ProductFramingCatalog` 现以唯一 `50 / 85` 物理尺寸比派生详情与 Library 取景：详情占屏从 `73.30%` 降到 `35.64% × 17.44%`，Library 从 `57.79% × 55.26%` 降到 `33.21% × 31.82%`，不再与更大的圆形产品被归一到同等视觉尺寸。
- 当前主工作区精确同步到独立 Unity 6000.5.6f1 验证副本后，聚焦 EditMode 回归 `52/52 Passed`：`ProductArchitectureTests 39/39`、`SpinnerEnvironmentTests 8/8`、`TwoLobeBarStaticAcceptanceTests 5/5`；报告为 `Logs/ModelingAxisScale/ModelingAxisScaleEditModeTests.xml`。几何审计前后证据为同目录的 `model-geometry-audit-before.json` 与 `model-geometry-audit-after.json`，相关文本差异 `git diff --check` 通过。
- 真实 GPU shipping Unity 五视角预览已生成并人工核对：Dragon Scale 的 authored hero / top / 左右斜视 / low-angle 与联系表位于 `Artifacts/DragonScaleAxisCenterFix/`；石墨双叶对应五视角与联系表位于 `Artifacts/GraphiteTwoLobePhysicalScaleFix/`。下一步等待视觉批准后由总控纳入独立快速 Build；安装后仍需 iPhone 真机验收旋转同心性与跨产品尺度感，当前未构建、未安装、未真机验收。

## 四款旋转模型额外轴心钢圈移除（实现、DCC 重建与 shipping 预览完成；视觉批准待确认，未推送手机）

> **当前发布状态：Build 37 四款旋转玩具在真实指盖/轴承之外又叠加了装饰圈，分别来自 `RotorCoreTopTrim`、`RotorCrownTrim`、`AccentLine`、`PolishedBezel`、`ShadowGap` 和 `UndercutShadowGap`。当前候选已移除这些非机械必需的可见圆环，保留真实固定指盖、轴、轴承内/外圈、垫片、旋转层与碰撞；视觉批准待确认，尚未进入新 Build，未推送手机。**

- pointed three-blade 不再生成 `RotorCoreTopTrim`，且将动态承载盘收入 34.4 mm 指盖的投影内；metal three-blade 的 Blender 源移除 `RotorCrownTrim` 与上/下 `AccentLine`，转子承载体收入 38.0 mm 指盖，顶/底面改为单一连续的真实指盖表面。
- gold four-wing CLI Anything/Blender 源移除 `RotorCrownTrim`、上/下 `PolishedBezel` 与上/下 `ShadowGap`，转子承载体收入 44.2 mm 指盖投影，并以单一径向拉丝面取代原先宽圈。重建产物为 85.000 × 17.000 mm、28 meshes / 21,324 tris；可见装饰轴圈计数为 `0`，转子拓扑为 `0 boundary / 0 non-manifold / 0 zero-area`。
- graphite two-lobe 移除上/下 `UndercutShadowGap`，保留实体 50.000 × 18.680 mm 和真实上/下指盖。四款 shipping 场景审计的平面尺寸依次为 `66.684 / 84.038 / 85.000 / 50.000 mm`；四款转子到固定轴心的平面偏移均为 `0.000 mm`，上述 9 类禁用装饰圈节点均为 `0`。审计前/后 JSON 位于 `Logs/SpinnerAxisTrimRemoval/`。
- 首轮删除命名圆环后，人工 shipping 门禁发现指盖下方的宽承载盘仍会被视读为钢圈，因此未误报完成；Round 2 进一步收进承载体并扩展单一指盖面后，聚焦 EditMode 门禁 `53/53 Passed`，报告为 `Logs/SpinnerAxisTrimRemoval/SpinnerAxisTrimTests-round2.xml`。
- 四款均已从保存的 shipping Unity 场景生成 authored hero / top / 左右斜视 / low-angle 五视角，共20张 PNG 及分款/总联系表位于 `Artifacts/SpinnerAxisTrimRemovalPreview/`。下一步等待用户确认应保留的真实指盖与轴承视觉；批准后由总控纳入下一个独立快速 Build，安装后仍需 iPhone 真机验收旋转视觉、物理与 Haptic。

## 离线成长 bottom sheet 后页面级 XP 回收（实现与本地验证完成；视觉批准待确认，未推送手机）

> **当前发布状态：Build 38 的结算层已是保留原页面上下文、自动关闭的 bottom sheet，但 `+XP` 光点仍在 sheet 内回收到 sheet 自身头像。下一版候选保持结算内容不变，先完整移除 sheet、恢复 Library，再从原页面飞向左上角真实成长头像并更新头像环；视觉批准待确认，未进入新 Build，未推送手机。**

- `ProgressionRewardCelebrationView` 只负责 bottom sheet 内的离线时长、成长值、每小时速度、AUTO 来源、头像等级与环形进度，不再创建任何 XP 粒子。离线结算没有领取 CTA；全屏透明 hosting 层在 sheet 活跃时继续阻止底部“查看收藏盒 / 进入模型”穿透，自动结算后先 `removeFromSuperview()`、移除 controller 并恢复页面，再延迟启动独立的 `ProgressionPageRewardFlightView`。
- `ProductTopBar` 新增复用 `person.crop.circle` 语义的常驻左上成长头像与环形进度；详情页同时保留返回按钮和头像。sheet 头像与左上头像都由 `ProductWindowFrameReader` 将真实 shipping view 转换到同一 window 坐标，页面级 `+XP` 与九枚光点使用这两个实际 frame 做贝塞尔飞行，不以机型相关的硬编码屏幕坐标猜目标。页面飞行 hosting view 明确不可交互且从可访问性树隐藏。
- 左上头像在结算期间暂存旧等级/旧 fraction；只有页面级飞行抵达时才用此次 `SpinnerOfflineReward.NewLevelProgress` 快照提交新等级与环进度并触发短脉冲。Unity XP 在原生展示前已经持久化，SwiftUI 不重算、不再次发 XP；真实跨级仍只由 `newLevel > previousLevel` 触发，旧等级环走满后再切到真实新等级与新 fraction。若实际 frame 暂时不可用，运行时只提交/高亮权威快照，不猜坐标飞行。
- Reduce Motion 下 sheet 静态显示最终头像环与等级并自动关闭；页面恢复后仅提交和短暂高亮左上头像，不显示粒子飞行。原生预览用独立的 environment override 覆盖同一生产分支，shipping 默认仍由系统 `accessibilityReduceMotion` 决定。
- 产品级文字 CTA 继续永久只显示动作文字；`ProductPrimaryActionLabel`、“进入模型”、onboarding“下一步 / 开始玩”、场景选择主 CTA 与“查看收藏盒”均没有装饰 icon；导航返回、设置等 icon-only 工具操作和非 CTA 的奖励语义图标不受影响。
- 当前 shipping 五个 Swift 原生文件通过 `arm64-apple-ios15.0` iPhoneOS type-check。在独立 Unity 6000.5.6f1 副本中，`RuntimeAndLiquidGlassUi_AreWiredForGrowthAndOfflineReturn` 为 `1/1 Passed`（0.162610 秒），报告与日志位于 `Logs/ProgressionPageFlight/`；断言锁定 sheet 无粒子、真实 window anchor、先移除 sheet 再展示页面飞行、左上头像提交、Reduce Motion、无离线 CTA、旧/新 fraction 数据链及 XP 不二次发放。
- iPhone 17 Pro / iOS 26.3 独立 Simulator 以当前 shipping SwiftUI 冷启动验证：sheet 活跃时 `preview-display-case-action` 与 `preview-enter-model-action` 均不在可访问性树中；无需点击，sheet 和页面飞行动画完成后两个底层按钮恢复且可访问，左上头像读为“成长头像，等级 42，本级进度 62%”。记录为 `Artifacts/ProgressionCelebrationNativePreview/automatic-dismiss-verification.txt`。
- 当前源码真实四阶段联系表为 `Artifacts/ProgressionCelebrationNativePreview/progression-celebration-contact-sheet.png`（1040 × 565），从左到右为 sheet 活跃、sheet 已关闭且页面恢复、XP 飞向左上头像、头像环更新完成；H.264 动画 `offline-growth-page-flight.mp4` 为 1206 × 2622、5.173 秒。Reduce Motion 终态为同目录 `offline-reduce-motion-top-avatar.png`；跨级与实时升级补充联系表为 `progression-level-up-contact-sheet.png`。
- 本轮差异集中于 `Assets/Plugins/iOS/CodexSwiftUIOverlay.swift`、`Assets/Tests/Editor/SpinnerProgressionTests.cs`、`Docs/LiquidGlassDesignGuideline.md`、原生预览工具与证据；未修改冻结 Build 38、3D、场景、收藏盒、陀螺物理、Haptic 语义链、XP 规则或 Build 编号。下一步等待用户确认四阶段联系表与飞行节奏；视觉批准后由总控纳入下一次快速 Build，iPhone 真机安全区、动画节奏、Reduce Motion 与底层操作恢复仍待安装后验收。

## Library 陀螺仪翻面与模型横向切换修复（实现与隔离验证完成；视觉批准待确认，未推送手机）

> **当前发布状态：Build 37 的 Library 相机在接近 89° 顶视时仍用固定 `Vector3.up` 执行 `LookAt`；设备轨道跨过世界竖直极点时，相机 up 会突然切换半球，表现为叶片瞬间上下翻面。模型选择虽然由原生 `TabView` 连续滑页，但 Unity 端只在异步场景加载完成后瞬切，没有为旧/新 shipping 场景执行对应的退出与入场。当前候选已修正两条运行时链路；尚未进入新 Build，未推送手机。**

- `DeviceMotionOrbitMapping.ResolveStableLookRotation()` 用同一 orbit 同时旋转 authored forward 与 authored up；`OrbitPresentationCamera`、`PortraitCameraFramer` 和 `EdcPortraitCameraFramer` 共用该解算，因此穿过 90° 极点时继续沿上一朝向旋转，不再由固定世界 up 触发 180° 翻面。该变化只写展示相机 pose，不写转子 Transform、Rigidbody、角速度、机制状态或 Haptic。
- `FidgetAppCoordinator` 在 Library 模型变化时保持异步 Single scene load，旧场景立即按模型序号方向开始横移；加载达到可激活状态且最短退出引导达到 `0.12 s` 后才激活新场景，新场景从镜像一侧进入。Reduce Motion 继续直接切换；连续快速选择仍只保留最新排队 model id。方向由 `ResolveLibraryPageDirection()` 从 canonical `ProductModelIds` 计算，不增加重复模型目录。
- 隔离在干净 Build 37 快照后覆盖当前运行时与测试源码，`SpinnerEnvironmentTests` 聚焦 `8/8 Passed`；断言覆盖 89.9°→90.1° 极点的旋转差 `<0.25°`、screen-up 点积 `>0.999`、前后模型方向、异步 activation 门控、退出/入场接线和 Reduce Motion 分支。报告为 `Logs/LibraryMotionContinuity/SpinnerEnvironmentMotionTests.xml`。
- 真实 GPU shipping Unity 场景预览位于 `Artifacts/LibraryMotionContinuityPreview/`：联系表上排依次为第一款居中、向右退出、第二款从左进入、第二款居中；下排为设备轨道跨原翻面阈值的前后两帧。首轮误用 `-nographics` 只得到清屏色，已判定门禁失败且未展示；预览工具现会在 RenderTexture 创建失败时直接报错，最终联系表由 Mac 图形设备重新渲染并人工核对。
- 下一步等待用户确认横移方向/幅度及跨阈值朝向；批准后纳入第一批独立快速 Build。安装后仍需 iPhone 真机验收连续快速左右滑、加载较慢时的保持策略、Core Motion 灵敏度和 Reduce Motion；当前未构建、未安装、未真机验收。

## 收藏盒 P0 运行时快照、透明内框与同向跟手修复（实现与隔离验证完成；视觉批准待确认，未推送手机）

> **当前发布状态：Build 37 的收藏盒快照把 renderer 的 world position / rotation / lossyScale 直接固化，会把产品进入收藏盒前的详情缩放、设备 orbit 和当前姿态再次叠加到统一 profile 与 fit，导致除基准款外尺寸、方向和内容混乱。翻转时出现的透明浮框来自收藏盒自身的 `RoundedRecessWall / RoundedRecessBack` 误用 Acrylic，而不是产品场景夹带的额外物体。当前候选已修复快照、内槽材质与横向拖动方向；视觉批准待确认，尚未进入新 Build，未推送手机。**

- `PremiumDisplayCaseProductPresentation` 现以每个 profile 的权威 `SceneRootName` 为 source root，按 source-root-relative matrix 重建可见 renderer，再执行收藏盒统一 orientation / fit；不再烘焙当前 presentation scale、Core Motion orbit 或交互中的临时姿态。磁吸扇牌保留其专属 `-90°` 正面规则，A/Q/K 面朝用户。
- snapshot 继续过滤 Camera、ParticleSystem、LineRenderer 与 grounding stage；逐款 shipping 根审计确认 TwoLobe 背景位于 Camera 子树并会被过滤，原产品根在 snapshot 后隐藏，没有其他场景 renderer 混入。中央 rounded capsule 的墙体/背板分别改为不透明 NeutralGraphite / BlackVelvet，仅保留细金属边；外层收藏盒透明壳不变。
- 原生 `PremiumDisplayCaseExperienceView` 的横向 orbit 改为 `orbitStart.width - translation.width` 的同向表面映射，使收藏盒可见表面随手指左右移动；纵向原本已符合跟手方向而保持不变。变化只控制展示相机/收藏盒 presentation，不写奖品刚体、机制位置、速度或 Haptic。
- 基于干净发布基线的隔离 Unity 6000.5.6f1 重建 shipping prefab/scene 后，`PremiumDisplayCaseTests 27/27 Passed`，报告为 `Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/DisplayCaseBatchA-Tests-shipping-final.xml`；五个 shipping Swift 文件以 `arm64-apple-ios15.0` 完整 type-check 通过。主工程 runtime / builder / tests / prefab / scene 与验证副本逐文件一致。
- 六款共 36 张真实 GPU shipping 图位于 `Artifacts/PremiumDisplayCaseBatchARuntimeFixPreview/`，每款覆盖 hero / top / 左右斜视 / low / phone hero；正面与三角度联系表为 `batch-a-phone-contact-sheet.png`、`batch-a-angle-contact-sheet.png`。下一步等待用户批准后纳入快速 Build，并在 iPhone 逐款翻转、缩放和同向拖动验收；灯光颜色选择器与全局陀螺降曝明确作为独立批次 B，不与本 P0 堆包。

## 收藏盒四色灯光与旋转陀螺柔和降曝（实现、完整回归与 shipping 预览完成；视觉批准待确认，未推送手机）

> **当前发布状态：收藏盒现可即时切换柔白、玫瑰、琥珀、冷雾四套灯光并持久化；四款旋转陀螺已使用独立的柔和环境光、反射峰值和高亮金属响应，解决部分角度叶片/中心盖剪成纯白的问题。真实 shipping GPU 预览与完整自动化均已通过内部门禁，但仍等待用户明确视觉批准；本候选尚未进入新 Build，未推送手机。**

- `PremiumDisplayCaseLightingCatalog` 是四套灯光颜色、强度和持久化键的唯一权威来源；原生收藏盒页的 `LIGHT COLOR` 四色选择器通过 `SetDisplayCaseLightingFromNativeUi` 即时驱动当前收藏盒，并由 SwiftUI `AppStorage` 与 Unity `PlayerPrefs` 使用同一键恢复上次选择。切换只改 `CaseLight_Key / Fill / Rim` 的颜色和强度，不写奖品物理、轨道、姿态或 Haptic。
- `SpinnerImageBasedLightingController` 只对 pointed / metal / gold / graphite 四款真实转子启用柔和策略：环境、直射、反射、补光、主体回光与局部 subject glow 分层降低，并按四款材质基线施加有限 exposure trim；高亮金属只通过运行时 `MaterialPropertyBlock` 将底色乘 `0.68`、光滑度限制为 `0.70`，保留色相且不修改共享材质资产、模型几何、碰撞或旋转物理。magnetic slide / fan card 明确绕过该策略。
- 以同一裁切区域统计任一 RGB 通道 `>=250` 的近白像素，neutral / parallax 从 pointed `2.738% / 4.817%` 降至 `0.005% / 0.006%`，metal `3.628% / 3.649%` 降至 `0.023% / 0.027%`，gold `4.893% / 4.891%` 降至 `0.073% / 0.078%`，graphite `7.289% / 2.366%` 降至 `0% / 0%`；磁吸推牌和扇牌的既有 clipping 指标保持不变。
- 最终隔离 Unity 6000.5.6f1 完整 EditMode 为 `315/315 Passed`，报告与日志位于 `Artifacts/LightingBatchBValidation/LightingBatchB-FullEditModeTests-final.xml` 和同目录 `.log`；收藏盒专项 `29/29 Passed`，四款曝光/环境专项 `9/9 Passed`。当前主工程五个 shipping Swift 文件再次通过 `arm64-apple-ios15.0` type-check；灯光核心 runtime / builder / tests 与最终验证副本逐文件一致，未用隔离 Swift 覆盖并行的离线成长点击修复。
- 收藏盒四档 × 左/手机正视/右共 12 张原图及联系表位于 `Artifacts/PremiumDisplayCaseLightingPalettePreview/`；六款 neutral / parallax 共 12 张原图及最终联系表位于 `Artifacts/SpinnerSoftLightingPreview/`。下一步等待用户确认颜色差异、模型亮度和材质层次；批准后才由总控构建并覆盖安装，iPhone 上仍需验收颜色切换持久化、真实屏幕曝光、Core Motion 角度和温升。

## Build 36 已安装并启动到 iPhone（收藏盒激光名、等级与最高 Badge；待真机视觉验收）

> **发布结论：用户于 2026-08-11 明确批准 `PremiumDisplayCaseLaserBadgeCompactPreview`，要求推到手机。Build 36 已从隔离、不可变发布快照完成 Unity DeviceSDK 导出、Xcode Release 编译、签名验证、iPhone 覆盖安装和启动；设备库存与运行进程均已回读。用户随后逐款检查并明确反馈：只有磁吸推牌的收藏盒尺寸与 3D 视角符合预期，其余五款一致性验收失败。六款统一修复候选现已获得本轮统一视觉授权，等待总控与其他已批准改动合入唯一后续 Build；本 task 未单独构建或安装。**

- 发布快照提交为 `d2325b1bf3b4b457ff1841fe0f1658fa59abd0a1`，只冻结 Build 35 已批准基线、当前玩具激光英文名/等级、最高 Toy Badge 选择、灰银物理蚀刻 shader、紧凑 Badge 布局和唯一 Build 号 `36`；没有合入主工作区其他未批准视觉改动。
- 发布前 `PremiumDisplayCaseTests 25/25`、`BadgeSystemTests 10/10`、`ProductArchitectureTests 38/38`，合计 `73/73` 通过，报告为 `Logs/Build36Evidence/ReleaseFocusedEditModeTests.xml`。紧凑版锁定 Artwork `0.031 m`、图文 X=`±0.014 m` 和组合 Y=`0.081 m`。
- Unity 日志明确记录 `Build Finished, Result: Success`，manifest 为 `com.jiaweizhou.fidgetspinner.codex / 0.1.0 (36)`、DeviceSDK、非 Development；Xcode 日志以 `** BUILD SUCCEEDED **` 结束。签名 App 为约 `386 MB`，`codesign --verify --deep --strict` 通过，Team 为 `2RJ2CW6NK5`。证据归档于 `Logs/Build36Evidence/`。
- 安装前 CoreDevice 一度将 iPhone 15 Pro Max `JW` / `00008130-001A00361EE0001C` 标记为 `unavailable`，当时没有误报安装；用户重新连接后设备恢复 `connected`，锁屏回读为无需密码且开机后已解锁。`devicectl` 随后成功覆盖安装，新容器为 `454DDFC3-B4DA-4283-8C72-7FFC5B622D3A`，库存回读确认 `0.1.0 (36)`；应用启动 PID `34011`，5 秒后的完整进程列表仍能找到同一新容器中的 `FidgetSpinner`。设备证据为 `device-lock-before-install.json`、`device-install.json`、`device-app-inventory.json`、`device-launch.json` 与 `device-processes.json`。

## Build 35 已安装并启动到 iPhone（六款收藏盒绑定修复；待真机验收）

> **发布结论：用户确认六款 shipping Unity 联系表后明确要求“先把已经改好的推到手机”。Build 35 以 Build 34 的隔离发布快照为基线，只加入当前玩具可见快照、六款内舱/fit profile 和对应测试；后续英文激光名、等级字标与顶部最高已获得 Badge 都不在该安装包内。**

- 隔离发布源提交为 `5eb193910de5a1f7dde6af6195dc117850eb90ad`，版本号的运行管线、序列化 `ProjectSettings.asset` 和架构验收断言同步为 `35`。发布前同一收藏盒源码的 `PremiumDisplayCaseTests` 实跑 `23/23` 通过；进一步批处理架构过滤因当前 Unity 许可不含 `com.unity.editor.headless` 而未进入 Test Runner，不伪报。
- Unity DeviceSDK 导出、Xcode Release 构建、自动签名与 App Validate 成功；manifest 与签名 App 均为 `com.jiaweizhou.fidgetspinner.codex` / `0.1.0 (35)`，`codesign --verify --deep --strict` 通过，App 约 `372 MB`。
- 设备当时使用 `localNetwork` 无线 tunnel，60 秒和 180 秒两次安装超时后都回读为 Build 34，未伪报成功；同一签名 App 在 600 秒容限下约 154 秒完成覆盖安装。最终设备库存回读 Build `35`，自动启动 PID `33221`，5 秒后完整进程清单仍能找到该可执行路径。证据归档于 `Logs/Build35Evidence/`。

## Build 34 已安装并启动到 iPhone（Premium Display Case 严格正视图；上一版）

> **发布结论：用户指出收藏盒应反过来正对用户、采用正视图；查看更新后的 shipping Unity Hero 与手机竖屏预览后，明确要求“推到手机上”。Build 34 以已安装的 Build 33 隔离发布快照为基线，只加入 Premium Display Case 严格正视相机规则及对应防回归测试，并同步唯一 build number，没有混入主工作区后续未批准内容。**

- App 默认、Hero 与手机竖屏相机统一为 `position=(0, 0.006, -0.72)`、`lookAt=(0, 0.006, 0.008)`；相机和目标点 X 完全居中，Y 高度一致，因此不再带俯视、仰视或左右透视偏移。左右斜视、顶部与低角度仍只用于资产检查，不进入 App 默认展示。
- 隔离发布提交为 `9ca718da12a6fdaef1e739cafe745f58a627e6da`。`PremiumDisplayCaseTests` 实跑 `21/21`，新增断言锁定默认相机严格沿 +Z 正视；build number 与架构专项 `ProductArchitectureTests` 实跑 `38/38`。报告和日志归档于 `Logs/Build34Evidence/`。
- Unity DeviceSDK 导出和 Xcode Release 编译成功；manifest、签名 App 与设备库存回读一致为 `com.jiaweizhou.fidgetspinner.codex`、`0.1.0 (34)`，`codesign --verify --deep --strict` 通过。签名 App 为 `372 MB`，Team `2RJ2CW6NK5`。
- 2026-08-10 22:43 CST，Build 34 已覆盖安装到 iPhone 15 Pro Max `JW` 并自动启动。设备库存回读确认 Build `34`；启动 PID 为 `32253`，随后完整进程清单仍能按可执行路径确认该 PID 在运行。安装、启动、版本与进程证据为 `Logs/Build34Evidence/device-install-final.json`、`device-launch.json`、`device-app-inventory.json` 与 `device-process-all.json`。安装和启动不替代人工验收：收藏盒是否达到期望的正视构图、透明材质和手机端动态观感仍需用户在真机确认。

## Build 33 已安装并启动到 iPhone（上一版整包；展示盒与全量交互待真机验收）

> **发布结论：用户查看了参考图版本展示盒的 shipping Unity 多角度预览，并于 2026-08-10 明确回复“先推上来看看”。本轮不再从 Build 31/32 的旧冻结基线挑选变更，而是把当时主工作区 `Assets / Packages / ProjectSettings` 的全部最新状态冻结为隔离 Release 快照；发现历史 Badge 专项已经占用 Build 32 后，最终包升级为唯一可辨认的 `0.1.0 (33)`。**

- 发布前在主 Unity 6000.5.6f1 中完整 EditMode 回归 `298/298` 通过。该回归首轮捕获并修复了两项真实问题：`GachaRevealDirector.Dismiss()` 在 EditMode `DestroyImmediate` 时会连带销毁调用方奖品节点，现于销毁盒体前显式归还内容；Haptic 设置的 Swift 调试预览重复写死 `Camera Dial`，现改为非目录占位文本，shipping 名称仍只读取 managed runtime catalog。Build 号升至 33 后，隔离快照的 `ProductArchitectureTests` 再跑 `38/38` 通过，报告为 `Logs/Build33Evidence/ProductArchitectureTests.xml`。
- Premium Display Case 的 Blender 报告、FBX、prefab、shipping 场景和正视/顶部/左右斜视/低角/手机/拆解预览均来自当前参考图实现；专项测试全绿。Fan Card 在安装前重建 Blender 与 shipping Unity 场景，Unity 几何验证为 `ALL PASS`，FanCard 测试 `24/24`，完整 guardrail 再次确认整条 rear-track 外轮廓距圆角牌边最小 `7.590 mm`。
- 隔离发布快照提交为 `ca687b8fbd78a4d8bd23cca7cb4ae817245daf3f`。首次 Unity 导入发现 URP Global Settings 会确定性删除一条失效 runtime-resource 引用，发布门禁按设计拒绝签名；该迁移同步回主工作区并纳入快照后重新完整导出，没有绕过“源码变化即拒绝安装”的校验。
- Unity DeviceSDK 导出、Xcode Release 编译、自动签名、`codesign --verify --deep --strict` 和 App Validate 均成功。签名 App 为 `372 MB`，manifest 与 App 的 Bundle ID / 版本一致为 `com.jiaweizhou.fidgetspinner.codex`、`0.1.0 (33)`，Team `2RJ2CW6NK5`。
- 2026-08-10 21:50 CST，已解锁 iPhone 15 Pro Max `JW` 通过有线 tunnel 覆盖安装并自动启动。设备库存回读确认 Build `33`；21:51 CST 再次查询时进程 PID `32107` 仍在运行。发布、签名、安装、启动与设备回读证据归档于 `Logs/Build33Evidence/`。安装/启动不替代人工验收：展示盒液态玻璃、陀螺仪视差、动画帧率、不同奖品 fit、Fan Card 动态层间距、实际 Haptic 与温升仍需用户在手机上确认。

## 盲盒抽取经济内核（部分集成；运行时与测试代码完成并经独立 harness 验证，Unity EditMode 回归待编辑器空闲后补跑）

> **当前状态：抽取系统 P1 经济内核已进入 `Assets/Scripts/Product/Gacha/`：`GachaCatalog`（系列/奖池/概率/保底的唯一数据源，TSV `CatalogPayload()` 供原生概率公示）、`GachaDrawEngine`（确定性 SplitMix64、软保底线性爬坡、51 抽 Signature / 90 抽 Heirloom 硬保底、10 连保 Refined）、`GachaInventoryRuntime`（券/币/屑/pity/已拥有，PlayerPrefs `fidgeting.gacha.v1.*` 带 schema version，重复奖品转合金屑、兑换所规则）。奖池只含外观/收藏物，经济层不产出任何 XP、物理或成长加成；尚未接入 coordinator、揭晓流程或原生 UI。**

- 测试代码为 `Assets/Tests/Editor/GachaDrawEngineTests.cs`（10 例：概率归一与全稀有度奖池、TSV 概率公示、20 万次分布收敛、软保底单调爬坡、两级硬保底、Heirloom 连带清零 Signature 计数、10 连保底触发与失效、固定种子重放）与 `GachaInventoryTests.cs`（6 例：资金/未知系列/非法次数拒绝、券币成本、重复转屑守恒、兑换所四类拒绝与成功路径、同前缀重载持久化往返、快照 payload 结构）。
- 主工程被已打开的 Unity Editor 锁定，本轮无法执行官方 EditMode 回归（与成长图鉴、Build 31 轮次的先例相同，不伪报通过）。过渡验证：真实源文件与真实测试文件在 Unity 自带 .NET 8 SDK 的独立 NUnit harness 中原样编译运行（仅以内存字典 stub `UnityEngine.PlayerPrefs`），结果 `16/16` 通过；当前 Unity Editor 对这批脚本的导入编译无任何 `error CS`。
- harness 首轮抓出一个真实缺陷并已修复：软保底爬坡抬高 Signature 概率后未重新归一化，Refined 区间溢出导致最坏运气 roll 在第 49 抽落 Refined 而非 Standard；现按 Refined/Standard 基础比例分摊剩余概率质量，无爬坡时与原行为数学上完全一致（见 `GachaDrawEngine.DrawInternal`）。
- 编辑器空闲后必须补跑完整 EditMode 回归（基线 236/236 + 新增 16 例）并归档 XML 报告，本节才可升级为“已集成并有测试”。

## 盲盒揭晓 Director（部分集成；运行时与测试代码完成并通过真实 UnityEngine 程序集编译校验，EditMode 回归与预览待编辑器空闲）

> **当前状态：`Assets/Scripts/Product/Gacha/GachaRevealRules.cs` 与 `GachaRevealDirector.cs` 把 P1 抽取结果接到已冻结的 `PremiumDisplayCase` 契约上。稀有度签名不修改展示盒 2.20 s 时间轴（该契约有 11/11 专项测试锁定），而是以 play() 前的悬念保持段（Signature +0.6 s / Heirloom +1.2 s）、按奖品类型选择胶囊 preset、以及 director 自有的稀有度 accent 点光（深灰/钢蓝/暖铜/极光四色内衬色语言，包络在盒盖阶段全暗、内容显影段正弦上扬、完成后保留低位持续）表达。Director 不写 Rigidbody、不直接调用 Haptic，销毁展示盒时按契约归还奖品节点的原 parent/pose。**

- 测试代码为 `Assets/Tests/Editor/GachaRevealTests.cs`（8 例：签名随稀有度单调升级且内衬色两两互异、总时长=悬念+冻结时间轴、全奖品类型的 preset 映射、accent 包络分段、Heirloom 悬念期不播放、Standard 立即播放、完成回调恰好一次+accent 随包络点亮、Dismiss 归还奖品并清空全部生成物）。
- 主工程仍被已打开的 Unity Editor 锁定。过渡验证：P1+P2 全部运行时与测试源码（含 `_DisplayCase/Runtime` 契约文件）在 Unity 自带 .NET 8 SDK 下对 iOS il2cpp 的真实 `UnityEngine.CoreModule/PhysicsModule/AudioModule` 与 Unity 自带 nunit.framework 编译通过、0 警告。行为断言仍需编辑器空闲后跑 EditMode 回归。
- gacha 试点皮肤资产（三叶金属四稀有度材质线）与揭晓流程 contact sheet 按计划归入 P6 内容阶段；按视觉推送门禁，出图并获用户明确批准前不构建或安装。

## 抽卡 Pack 六档金属／镭射视觉方向（V7 shipping native 实现与测试完成；shipping 视觉批准待确认，未推送手机）

> **当前状态：2026-08-17 用户已明确批准 V7 作为后续设计方向；正式 SwiftUI 抽取入口、可分层 foil Pack 和撕包状态现已实现并通过相关回归。批准范围仍是 V3 的短宽包装比例、柔和膜面起伏、圆角方盒四角暗示、连续流体三角环描线、低对比烟熏灰银与克制镭射，以及 App 随包 Oxanium 的放大文字。V6 的平整硬盒／实际三叶产品重画方向继续保持 Superseded。V7 概念联系表只锁定方向；本轮新的 Simulator 四阶段图片才是当前 shipping native 实现预览，但尚未获得用户视觉批准，因此不得构建或安装到手机。**

- 当前 V7 联系表归档为 `Artifacts/GachaPackConcept/pack-tier-contact-sheet-v7.png`（`1536 × 1024`，SHA-256 `fe8634a6cffa18fc2c3673bade212c52a2115a141fc0cb3d94bac076e973ae27`），属于已批准的概念方向证据，但不是 shipping 视觉证据，因此不复制进 `Docs/DesignBibleAssets/`。`render_oxanium_overlay.swift` 的 `v7` 布局在 V3 原文字锚点使用实际随包字体，并保留低饱和 tier 点缀色。V4–V6 只保留为被替代历史。
- `Tools/GachaPackConcept/export_pack_layers.swift` 从批准联系表确定性导出六档各 `body + flap` 两层，共 12 张 `384 × 512` 透明 PNG，归档在 `Assets/Plugins/iOS/GachaPacks/`；重新导出到独立目录后逐文件 `cmp` 一致。`FidgetGachaPackPresentation.swift` 提供六档稳定 asset name 与独立 Pack tier 语义；它不引用 `GachaRarityTier`，`launch-series` 和未知 series 均安全使用 Standard，因此封包不会泄露 receipt rarity，也未改变概率、保底、catalog、StoreKit、券消耗或奖品揭晓。
- `FidgetGachaStorefront.swift` 在正式 `GachaStoreView` 首屏加入 Pack 入口卡；真实单抽 receipt 到达后先呈现封包，顶部封边支持向右拖动，`220 pt` 为完整行程、`0.62` 为提交门槛，未达到时回弹，达到后只移动 `flap` 并继续既有六拍收藏盒揭晓；同时提供可访问的“撕开包装”按钮与 Reduce Motion 退化。该层没有写物理、没有从 rarity 决定 Pack、没有新增原始输入直连 Haptic。`IosBuildPipeline.ConfigureProductThumbnails` 已将 `GachaPacks` 纳入正式 Xcode resource copy。
- 验证：`GachaPackRulesHarness` 为 `9/9`；五份相关 shipping Swift 以 `arm64-apple-ios15.0` typecheck 通过；`GachaStorefrontIntegrationTests` 为 `2/2`；完整相关 Gacha EditMode（经济抽取、库存、bridge、Pack、盘盒、收藏盒 reveal）为 `41/41`，报告 `Logs/GachaPackV7RelatedEditMode.xml`。当前真实 shipping native 联系表为 `Artifacts/GachaPackShippingNativePreview/gacha-pack-v7-shipping-contact-sheet.png`（`1200 × 652`，SHA-256 `f96ce7a8a703418e7064cf8371d090d0a5772b82e5a3ffadb0793c5c4dead263`），依次显示抽取入口、完整封包、68% 撕包和进入收藏盒；它由正式 SwiftUI 源码及正式资源在 iPhone 17 Pro Simulator 渲染，不是概念 mockup。
- 下一门禁：用户明确批准当前 shipping SwiftUI 联系表后，才能构建或安装到手机；在此之前状态固定为“shipping 视觉批准待确认，未推送手机”。

## 盲盒盘盒交互状态机（部分集成；纯逻辑运行时与测试完成并在独立 harness 全绿，场景/输入接线待后续阶段）

> **当前状态：`Assets/_GachaBox/Runtime/` 提供揭晓前的"盘盒"三幕机制：摇盒听声（`userAcceleration ≥ 0.30g` 进入、`0.18g` 迟滞退出、`0.35s` 冷却，符合仓库 Shake 规则）、按稀有度输出可听辨的 rattle 脉冲列（标准单响 0.35 / 精制双响 0.55+0.50@70ms / 臻藏重响+惯性尾 0.85+0.30@110ms / 传世三连沉响 0.95+0.80+0.90@90ms，全部在 `GachaBoxProfile` 单一数据源）、搓盒预热（约三整圈弧长满值，空闲按 1.2s 半衰期衰减）、开盖预压→`0.44` 归一化脱档→`0.18s` 后弹开。`GachaBoxInteractionMachine` 为零 UnityEngine 依赖的确定性状态机，只经 `Tick` 推进时间，零输入永不产生事件（无自转不变量的盒子版）。`GachaBoxHapticAdapter` 把盒子语义事件映射到共享 `FidgetHapticRouter.Emit`（RattleImpulse→Collision、Warmed→Pop、LidBreakaway→Breakaway、LidOpened→Released），跳过键的 LidOpened 权重为 0 并保持静默，符合"程序化设姿不播放反馈"的产品规则；没有任何原始输入直连 `IosHaptics`。**

- 测试代码为 `Assets/Tests/Editor/GachaBoxInteractionTests.cs`（10 例：零输入永久静默、低于阈值不响、稀有度脉冲列权重与间距、持续加速度只触发单次 burst、迟滞+冷却门控、预热恰好一次、半衰期衰减、未预热/预压区静默、Breakaway 单次+延时弹开、跳过静默且幂等）。
- 纯逻辑部分（Profile + Machine + 测试）已在独立 .NET 8 NUnit harness 中原样运行，连同 P1 经济内核共 `26/26` 通过。`GachaBoxHapticAdapter` 引用 shipping `CodexUnityLab.FidgetHapticRouter.Emit(FidgetSemanticEvent, float)`（签名与枚举成员已核对），其编译与行为断言随 EditMode 回归补跑。
- 触摸输入采集（搓盒弧长、盖体拖动）、Core Motion 接入、程序化 rattle 音频与盒体 3D 资产尚未接线；这些属于后续阶段，本节不声称完成。

## 盲盒原生商店与桥接（部分集成；Unity 桥接、SwiftUI 商店模块与 Swift 类型检查完成，overlay 入口与视觉批准待预览轮）

> **当前状态：Unity→native 桥接为 `Assets/Scripts/Product/Gacha/GachaNativeBridge.cs`（`CodexGachaReceiveState(catalog, snapshot, receipt)` 三段 TSV，模式对齐既有 `Codex*ReceiveState` 桥）。`FidgetAppCoordinator` 新增 `RequestGachaStateFromNativeUi` / `DrawGachaFromNativeUi("seriesId|count|ticket/coin")` / `RedeemGachaShardsFromNativeUi(prizeId)` / `CreditGachaFundsFromNativeUi("coins|N"/"tickets|N")` 四个入口，`GachaInventoryRuntime` 懒加载持有，每次状态变化即回推快照。SwiftUI 侧为自包含 `Assets/Plugins/iOS/FidgetGachaStore.swift`：钱包、系列 banner、单抽/十连（券不足自动用币）、双保底进度、完整概率公示 sheet（App Store loot-box 披露）、兑换所、收藏库网格、结算面板（NEW/转屑/保底与十连保障标注）。**

- 收据 payload 纯函数有 `Assets/Tests/Editor/GachaNativeBridgeTests.cs`（2 例）；连同 P1/P3 纯逻辑测试在独立 harness 共 `28/28` 通过，编译校验（真实 UnityEngine iOS 程序集）含桥接文件继续 0 错误。`FidgetGachaStore.swift` 通过 `arm64-apple-ios15.0-simulator` 完整 typecheck。
- 商店入口已挂载：`ProductTopBar`（模型库页）右上角新增 `shippingbox` 图标按钮，以 sheet 呈现 `GachaStoreView`；仅在库页显示，不占用详情页返回位与设置勾选位。币包/月卡区块（`GachaCoinShopView`）内嵌在抽取页中。五份 shipping Swift（Overlay、Components、ComboHalo、GachaStore、StoreKit）已作为同一 module 通过 `arm64-apple-ios15.0-simulator` 完整 typecheck。按视觉推送门禁，Simulator 预览获用户批准前不构建或安装。
- 免费券正式发放已接线：`GachaInventoryRuntime.SyncRhythmTickets(completedRhythmWeeks)` 以持久化的已发券周数计数器保证幂等（重复发布、计数回退、重载均不重复发券），coordinator 在发布藏家状态时同步，每完成一个 7 日节奏周发 1 张抽取券；对应测试 `RhythmTicketsGrantOncePerCompletedWeekAndSurviveReload` 已入 `GachaInventoryTests`，独立 harness 全量 `29/29` 通过。

## 盲盒付费链路 StoreKit 2（部分集成；Swift 运行时与类型检查完成，App Store Connect 配置与 sandbox 验证待真机轮）

> **当前状态：`Assets/Plugins/iOS/FidgetStoreKit.swift` 是仓库第一段 IAP 代码：StoreKit 2 商品加载、购买、`Transaction.updates` 后台监听、`currentEntitlements` 恢复、revocation 处理。三档消耗型币包（480/1640/3360 齿轮币）+ 藏家月卡（自动续订，每自然日 1 张抽取券，按本地日期幂等，明确不加任何盘玩收益）。只有验证通过的交易才经 `CreditGachaFundsFromNativeUi` 入账，随后立即 `finish()` 防重放。`GachaCoinShopView` 提供币包/月卡/恢复购买 UI。**

- 商品 ID 清单（App Store Connect 需注册）：`com.jiaweizhou.fidgetspinner.codex.coins.small/.medium/.large`（消耗型）与 `...pass.monthly`（自动续订订阅）。通过 `arm64-apple-ios15.0-simulator` 完整 typecheck（`StoreKit.Transaction` 已消除与 SwiftUI.Transaction 的歧义）。
- 待办：App Store Connect 商品配置、StoreKit Configuration 文件 + sandbox 全流程（购买/中断/恢复/退款撤销）、月卡券与 Unity 端库存的对账真机验收。凭证为客户端 StoreKit 2 本地验证，当前产品无服务端，接受该模型并在上架前复审。

+## Build 31 Badge 图鉴滚动专项修复（代码、Swift 编译与原生预览完成；待视觉批准，未安装）

> **当前门禁：Build 30 已解决 Sheet 根部重复毛玻璃和 20 Hz 状态重绘，但真机反馈 Badge 页仍卡。本轮继续处理 Badge cell 自身的主线程绘制与图片解码；真实 shipping SwiftUI 预览已生成，用户明确批准预览前不构建或安装 Build 31。**

- 根因定位到每个 Badge cell 都会通过 `Canvas` 重建 26–58 条折痕、最多 290 个皮革颗粒和 620 个毛孔；同时 40 张
  `1024 × 1024` PNG 会在滚动路径加载完整尺寸，catalog cell 还重复绘制 artwork、blur、blend 与多层 shadow。即使
  Sheet 只保留一层真实毛玻璃，这些 cell 内部工作仍会集中占用主线程和 GPU。
- 皮革纹理现由确定性脚本 `Tools/generate_badge_leather_texture.py` 生成一次 `384 × 384` 透明 PNG；运行时
  `ProductBadgeLeatherTexture` 只缩放该静态纹理，不再创建逐 cell `Canvas`。Badge artwork 改为串行后台 ImageIO
  downsample：catalog 最长边 `256 px`、详情 `512 px`，解码后立即缓存；缓存限制为 64 项 / 24 MB，并在打开图鉴时
  预热当前 Badge catalog。
- `ProductRarityBadge` 分成 `.catalog` 与 `.full` 两种渲染路径。列表只保留一层 artwork，移除重复模糊副本和 artwork
  多层阴影，并把稳定的 badge shell 合成为单层；详情和分享页继续使用完整效果。Badge 卡和外观卡仍是静态 surface，
  只有 Sheet 根背景保留真实毛玻璃。
- shipping 三份 Swift 已通过 `arm64-apple-ios15.0` 类型检查，`git diff --check` 通过。专项 Unity EditMode 测试已增加
  对静态皮革、ImageIO 降采样尺寸、24 MB 缓存、catalog 路径和预热的防回归断言；本轮尚不声明该测试通过，因为
  当前打开的 Unity Editor 占用许可证，隔离批处理在测试执行前因缺少 `com.unity.editor.headless` entitlement 退出。
- 真实原生 Badge 页预览为
  `Artifacts/Build31BadgePerformance/progression-thumbnail-sheet-badge.png`。该图直接运行 shipping SwiftUI，验证单层
  Sheet 毛玻璃、静态子卡以及已获得 / 当前 / 未获得 Badge 状态；Build 31 尚未改号、构建或安装，等待明确视觉批准。

## Premium Gacha 展示盒与当前玩具 content slot（六款统一候选已进入并安装 Build 37）

> **当前状态：当前玩具绑定、激光英文名/等级和最高 Toy Badge 已随 Build 36 安装，但用户真机确认只有磁吸推牌的盒体规格与 3D 视角正确。现已把磁吸推牌设为六款唯一包装基准，并统一预览/运行时模型根节点解析；新 shipping 预览与专项测试完成。总控已取得用户对本轮候选的统一视觉授权，本候选已进入并安装 Build 37；六款真机视觉验收待用户解锁后进行。**

- `FidgetAppCoordinator.PresentDisplayCaseExperience()` 不再调用固定的 `ThreeBladeDisplayPrizeFactory`；它根据当前 `modelId` 快照可见模型并交给展示盒。Build 36 的 shipping 预览按场景根节点抓完整模型，但手机运行时仍按 Controller 层级猜根节点，两条路径并非同一数据源。修复候选把六款权威场景根名纳入 `PremiumDisplayCaseProductProfile.SceneRootName`，预览和运行时共同解析该字段；找不到权威根时才记录 warning 并回退旧 Controller 路径。快照仍只保留 Renderer，不携带 Collider、Rigidbody、Camera、Audio 或交互脚本，关闭展示盒后恢复原玩具。
- Build 36 的六款 profile 故意使用了不同内舱、初始偏航和慢转周期，这与用户要求的一致包装相冲突。修复候选把磁吸推牌设为唯一基准：六款全部使用 `RoundedSquareDeep`、`initialEuler=(90,-8,0)`、`idlePeriod=6s`，共享同一外盒 prefab、严格正视相机、内舱尺寸与 fit 规则；仅当前产品模型、英文名、等级与最高 Badge 随 `modelId` 变化。
- `PremiumDisplayCaseTests` 已从 21 例增加到 23 例，新增覆盖六个 shipping `modelId` 的 profile 完整性、磁吸陀螺基准不回归、当前玩具可见快照和禁止固定三叶奖品等约束。Unity 6000.5.6f1 隔离 Test Runner 实跑 `23/23` 通过，报告为 `Logs/DisplayCaseCurrentProductEditModeTests.xml`；额外 `ProductArchitectureTests` 本轮在进入 Test Runner 前因当前 Unity 许可不含 `com.unity.editor.headless` 而退出，不伪报通过或失败。
- 六款绑定批准图位于 `Artifacts/PremiumDisplayCaseAllProductsPreview/`，已用于 Build 35 的视觉门禁。新激光字标使用 shipping Oxanium 字体，上行 `LEVEL N`、下行英文产品名，两行 X=0 居中；运行时从当前产品 `SpinnerProgressionSnapshot.Level` 读取 1–100 级，预览中的 7/24/42/58/73/91 只用于检查一到三位数排版。六款各 6 视图位于 `Artifacts/PremiumDisplayCaseLaserIdentificationPreview/`，联系表为 `all-products-phone-contact-sheet.png` 和 `all-products-angle-contact-sheet.png`。
- 新字标专项把 `PremiumDisplayCaseTests` 扩展至 `24/24`，实跑全通过：覆盖六款英文名唯一且大写、磁吸陀螺 `MAGNETIC TRINITY` 基准、两个 TextMesh 的 Oxanium 字体和水平居中、等级 1–100 夹取及当前玩具绑定。报告为 `Logs/Build35Evidence/LaserIdentificationPremiumDisplayCaseTests.xml`，新字标未安装。
- 顶部 Badge 只从当前 `modelId` 的 21 枚 Toy Badge 中选择已解锁项，不会读取 Collector、Challenge、Legacy 或其他玩具。比较顺序为 `Singularity > Apex > Overdrive > Ignition`，同等级再比较机制换算后的数值门槛，仍并列才按目录顺序稳定选择；当前玩具一枚都未获得时顶部为空，不显示占位章。图形直接复用 `Assets/Plugins/iOS/BadgeArtwork/` 的正式 1024 透明 PNG，右侧用清晰的两行 `displayToken / shortName`，没有复制第二套 Badge 定义。
- 首轮 `Artifacts/PremiumDisplayCaseBadgeIdentificationPreview/` 直接显示正式 Badge PNG 内的铬面渐变并按等级给文字染金/蓝/紫；用户于 2026-08-11 明确否决该表现，认为它像数字 UI 投射、没有落在真实物理物体上的印刷/刻印质感，因此该目录不再是批准候选。当前 `PremiumBadgeArtwork.shader` 只使用正式图稿的 Alpha 与少量明度结构，移除原图颜色、独立高光与光晕，统一输出低饱和灰银蚀刻层；轻微激光颗粒、主光/环境光与观察角共同影响亮度，数字和短名也取消等级染色，颜色与下方 Oxanium 激光字标一致。
- 上一版灰银激光六款 shipping Unity 预览位于 `Artifacts/PremiumDisplayCaseLaserBadgePreview/`；在保持该物理蚀刻材质的基础上，用户继续要求缩小图标、收紧图文间距并整体下移，因此该目录保留为版式对照，不再是当前批准候选。
- Build 36 使用的紧凑灰银版位于 `Artifacts/PremiumDisplayCaseLaserBadgeCompactPreview/`：Artwork quad 从 `0.038 m` 缩到 `0.031 m`，图标/文字中心横向间距从 `0.038 m` 收紧到 `0.028 m`，整组 Y 从 `0.087 m` 下移至 `0.081 m`。预览 Badge 是用于覆盖数字与文字形态的版式样本；App 运行时按该玩具真实进度重新选择。
- 新一致性候选位于 `Artifacts/PremiumDisplayCaseMagneticSlideBaselineConsistencyPreview/`，共 38 张 PNG：每款正视 Hero、顶部、左/右斜视、低角和 942×2048 手机正视，另含六款手机与 30 张多角度联系表。磁吸推牌新旧六视角经逐文件 `cmp` 完全一致，证明权威基准没有被改动；其他五款已切换到同一深方舱与展示角。首轮隔离编译因 `StringComparison` 缺少命名空间限定而停止，未误报测试结果；改为 `System.StringComparison.Ordinal` 后，`PremiumDisplayCaseTests 25/25` 全通过，报告为 `Logs/DisplayCaseConsistency/PremiumDisplayCaseConsistencyTests-v2.xml`。本候选已纳入用户统一批准范围并随 Build 37 覆盖安装；真机视觉验收仍待进行。
- `BadgeSystemTests` 新增最高档/同档最高数字/零获得空状态规则后实跑 `10/10`；灰银材质后的 `PremiumDisplayCaseTests` 实跑 `25/25`，继续锁定 21/21 正式图稿绑定、两行排版、未知图稿安全隐藏，并新增“不同等级不再改变灰银文字色”和专用激光 shader 断言。Build 36 发布门禁进一步与 `ProductArchitectureTests 38/38` 合并实跑 `73/73`，锁定 `0.031 m` Artwork 尺寸、`±0.014 m` 图文位置、`0.081 m` 组合高度和唯一 Build 号；报告为 `Logs/Build36Evidence/ReleaseFocusedEditModeTests.xml`。这些测试、预览、构建与安装来自 `recover-unity-builds` 单写者规则下的隔离发布工程。

- 可编辑源为 `ArtSource/DisplayCase/PremiumDisplayCase.blend`，确定性生成脚本导出
  `Assets/_DisplayCase/Models/PremiumDisplayCase.fbx`。FBX 含前透明板、四颗端帽、四颗金属垫圈、透明间隔框、中央透明舱、开孔石墨
  内衬、后透明板和背部透明加强框 8 个稳定层；Unity 解包后显式执行 `Blender +Z -> Unity +Y`、
  `Blender -Y -> Unity -Z` 轴向映射。Blender 验证报告为
  `Artifacts/PremiumDisplayCaseValidation/blender_validation.json`：8/8 层、23 个网格、4/4 端帽、4/4 金属垫圈、
  188×55×240 mm、`style=clear-acrylic-four-fastener`、`hasOpaqueOuterBox=false`、
  `containsPrizeGeometry=false`，全部通过。
- shipping 入口为 `Assets/Resources/Gacha/PremiumDisplayCase.prefab` 与
  `PremiumDisplayCaseFactory.Instantiate(parent)`。抽取结果调用方传入已经导入并实例化的 glTF 根节点；展示盒不绑定 URL 下载
  或某一个 glTF importer。对外契约为 `setContent(gltfNode, options)`、`setCapsulePreset(...)`、`play()` 与
  `onRevealComplete`。当前 library 可打开交互式展示盒体验，但正式抽取结果把具体奖品节点交给该契约的业务接线仍属于 gacha
  coordinator，不伪报已经完成。
- 唯一锚点 `contentSlot` 下分离 reveal、idle orbit 与 fit 三层。Renderer / Collider bounds 按胶囊直径／深度统一缩放、三轴
  居中并保留固定 8% 留白；默认每 4 秒慢转一圈，可逐件关闭。外部奖品原 parent、local pose/scale 与 active 状态在关闭前恢复。
  8 层拆解使用 1.35 秒确定性错峰曲线，内容槽与第 4 层中性胶囊共享完全相同位移。
- `PremiumAcrylicLiquidGlass.shader` 是无纹理依赖的中性色透明 shader。盒体、亚克力、内衬与内容槽读取同一
  `SceneParallaxInput`，adapter 不调用 `IosDeviceMotion.Start/Stop`。SwiftUI 已接入左上返回、拖拽 orbit、双指 pinch、拆解 slider、
  装配重播、展开和视角复位；关闭时恢复原产品与相机。shipping 三份 Swift 已通过 `arm64-apple-ios15.0` typecheck，原生截图位于
  `Artifacts/PremiumDisplayCaseNativePreview/display-case-native-controls.png`。
- 预览参考构图为 1200×1600 / 29°；运行时使用“锁定水平构图、按当前设备 aspect 反算垂直 FOV”，避免超长 iPhone 裁掉两侧。
  App 默认、Hero 与手机竖屏相机统一为严格正视：相机和目标点 X 均为 0、Y 均为 6 mm，不带俯视或左右透视偏移；
  左右斜视、顶部和低角度只作为模型检查图，不进入默认展示。
  shipping Unity 新预览为 `Artifacts/PremiumDisplayCaseThreeBladePreview/01_hero.png`、`02_top.png`、
  `03_left_oblique.png`、`04_right_oblique.png`、`05_low_angle.png`、`06_phone_hero.png` 与 `07_exploded.png`。通用占位内容的
  942×2048 手机构图为 `Artifacts/PremiumDisplayCasePreview/11_phone_hero.png`；shipping Unity 重新导出的 1800×1800 RGBA
  透明底拆解图为 `Artifacts/PremiumDisplayCaseExploded/acrylic-case-exploded-transparent.png`，图中内容为开发用 coin primitive，
  不再由导图命令临时注入任何特定奖品。本轮视觉批准联系表为
  `Artifacts/PremiumDisplayCasePreview/display-case-approval-contact-sheet.png`（hero / top / left / right / low / exploded）与
  `display-case-reveal-contact-sheet.png`（closed / mid / revealed）。
- `PremiumDisplayCaseTests.cs` 当前 21 例，覆盖 Blender FBX 来源、4 颗端帽与 4 颗金属垫圈、禁止旧不透明外壳、84 mm 中央舱、
  manifest 样式约束、8 层拆解、内容跟随、原生桥接生命周期、手机相机构图，以及默认相机必须严格沿 +Z 正视的约束。
  2026-08-10 在当前 Unity 6000.5.6f1 Test Runner 中实跑 `21/21` 通过；本轮结果为
  `Logs/DisplayCaseFrontViewEditModeTests.txt`，此前 XML 证据为
  `Artifacts/PremiumDisplayCaseValidation/premium_display_case_editmode_tests.xml`。首轮捕获并修正一处已经落后于权威
  Three-Blade 测试的顶盖 mesh 名称断言后重跑全绿。
- 当前 Unity 实图为 `Artifacts/PremiumDisplayCaseThreeBladePreview/01_hero.png` 至 `07_exploded.png`；Blender DCC 对照图为
  `Artifacts/PremiumDisplayCaseBlenderPreview/blender-assembled-hero.png` 与带 alpha 的
  `blender-exploded-transparent.png`。原生 Simulator 壳已从 2 秒固定延迟改为等待 15 秒后取图，消除首装 SwiftUI 场景尚未
  ready 时产生的白屏假成功；最新真实原生控件图仍为
  `Artifacts/PremiumDisplayCaseNativePreview/display-case-native-controls.png`。严格正视实现已进入并安装 Build 34；液态玻璃在
  真机 GPU、陀螺仪幅度、动画帧率与不同实际 glTF 奖品的 fit 仍待用户在手机上验收。

## Build 31 已安装并启动到 iPhone（Haptic 保存修复；待真机交互验收）

> **发布结论：用户查看了真实 shipping SwiftUI 设置页预览，并连续回复“继续”，批准本次原生设置交互。Build 31 从已安装的 Build 30 冻结基线只加入 Haptic 保存/返回当前玩具修复，没有混入主工作区其他尚未批准的模型、场景或交互变化。**

- 设置页右上角勾选会显式执行 `applyAndPersist()`，然后通过 `dismissPanelToSelectedModel()` 回到当前玩具；Detent preset、Intensity 与 Sharpness 会保存到 `UserDefaults` 并在 Overlay 安装时恢复。
- 真实 native 预览为 `Artifacts/HapticSettingsSavePreview/haptic-settings-save-full.png`；用户查看后明确要求继续推送。发布源已通过 iPhoneOS 15 arm64 Swift typecheck，签名 App 通过 `codesign --verify --deep --strict`。
- 2026-08-10，隔离 Xcode Release 构建成功，App、build manifest 与签名信息一致为 `com.jiaweizhou.fidgetspinner.codex`、`0.1.0 (31)`、Team `2RJ2CW6NK5`。构建结果、设备状态和 manifest 归档于 `Logs/Build31Evidence/`。
- 2026-08-10 15:49 CST，iPhone 15 Pro Max `JW` 恢复有线连接，实时握手确认 `tunnelState=connected`、`ddiServicesAvailable=true`、`passcodeRequired=false`。同一签名 App 随后覆盖安装成功；设备库存回读为 `com.jiaweizhou.fidgetspinner.codex`、`0.1.0 (31)`，自动启动成功，5 秒后进程 PID `30101` 仍在运行。证据为 `Logs/Build31Evidence/device-install-success.json`、`device-app-inventory.json`、`device-launch-success.json` 与 `device-processes-success.json`。安装和启动不替代人工验收：仍需逐款确认设置保存、返回当前玩具、重启恢复与实际 Haptic 手感。

## Build 30 已安装并启动到 iPhone（成长图鉴性能待真机验收）

> **发布结论：用户查看了真实 shipping SwiftUI 单层毛玻璃预览，并于 2026-08-10 明确要求“推到手机上”及“继续”。Build 30 只从已安装的 Build 29 冻结基线加入成长图鉴性能修复，没有混入主工作区其他尚未批准的模型、场景或交互变化。**

- 打开图鉴时只捕获一次不可变 `ProgressionCatalogSnapshot`；`ProgressionLevelDetailsSheet` 不再观察以 20 Hz 发布运动遥测的整个 `ProductUiState`，并使用一次性 `UUID` 做 O(1) Equatable 身份比较。
- 整个 Sheet 根背景保留唯一一层真实 `ultraThinMaterial` 毛玻璃；等级、Badge、外观卡及 Badge 内圈均在图鉴中使用静态 surface，不再逐卡创建 `glassEffect` 或独立 material。Sheet 打开期间同时暂停被遮挡的 AUTO `CADisplayLink` 与成长缩略图 shimmer，关闭后恢复。
- 冻结发布提交为 `7a0dc098f5bd133df0809ee9eb187b2855f6b932`。iPhoneOS 15 arm64 Swift 类型检查通过；成长图鉴专项 `1/1`、build number / 原生启动架构专项 `1/1`、完整 Unity EditMode `236/236` 均通过。
- 2026-08-10 12:04 CST，Unity DeviceSDK 导出、Xcode Release 编译和自动签名成功，恢复安装回执成功；12:25 CST 在已解锁 iPhone 15 Pro Max 上启动成功，5 秒后进程仍存在。签名 App、build manifest 与设备库存回读一致为 `com.jiaweizhou.fidgetspinner.codex`、`0.1.0 (30)`。
- 完整证据归档于 `Logs/Build30Evidence/`。安装和启动只证明交付链路完成；仍需在真机分别从 Profile 与陀螺页打开图鉴，连续滚动三类 Tab，并观察短时温升后才能关闭性能验收项。

## Build 29 已安装到 iPhone（待解锁启动与真机验收）

> **发布门禁：用户于 2026-08-09 19:58 CST 查看并明确回复“全部确认，推送”，批准首批六组真实 shipping Unity / native 预览；在补看 Badge B8.13 与 Combo ×30 / ×50 咬合圆环预览后，于 20:03 CST 回复“继续推送”。本轮八组视觉变化均已明确批准。批准范围冻结为 19:58 CST 的当前源码快照；后续出现的新改动不进入 Build 29。安装成功只证明运行链路到达设备，磁吸推牌、磁吸扇牌、详情推镜、场景切换、成长图鉴性能及触感仍需 iPhone 真机验收。**

- 批准的原生界面预览：`Artifacts/ProgressEndpointTypographyNativePreview/progression-endpoint-top-bottom-contact-sheet.png`、
  `Artifacts/ProgressionCatalogFrostedSheet/progression-thumbnail-sheet.png` 与
  `Artifacts/EnvironmentWallpaperPickerNativePreview/environment-picker-contact-sheet.png`。
- 批准的 shipping Unity 环境 / 模型预览：`Artifacts/DetailEntranceTransition/detail-entrance-contact-sheet.png`、
  `../../../Artifacts/EDC/BroaderSofterHighlights_2026-08-09/00_ContactSheet.png`、
  `../../../Artifacts/FanCardMaterialPreview/fan-card-adaptive-contact-sheet.png`、
  `fan-card-back-track-closeup.png` 与 `fan-card-motion-90-to-00-contact-sheet.png`。
- 补充批准的原生视觉预览：`Artifacts/BadgeSpecial/NativeB8/badge-native-contact-sheet.png`、
  `Artifacts/ComboHaloNativePreview/combo-halo-tier-contact-sheet.png`、`combo-halo-angle-contact-sheet.png` 与
  `combo-halo-orbit-motion-comparison.png`。
- 磁吸扇牌 source-only 与完整门禁在冻结快照均通过；完整轨道外轮廓距牌身边缘最小 `7.590 mm`，底片固定、中片
  `45°q`、顶片 `90°q`，每个 Oxanium 700 A 直属自己的刚性牌片，背面无 A。`FanCardAcceptanceTests` 为
  `20/20`，shipping 场景几何验证为 `ALL PASS`。
- 冻结快照的完整 Unity EditMode 回归为 `236/236`；原生 `ComboHaloRuleTests` 为 `83/83`；
  `FidgetProductUIComponents.swift`、`FidgetComboHalo.swift` 与 `CodexSwiftUIOverlay.swift` 通过
  `arm64-apple-ios15.0` 类型检查。以上仅验证确定性规则、结构与编译，不能替代 iPhone 手感与视觉验收。
- iOS build number 已在 `Assets/Editor/IosBuildPipeline.cs`、序列化 `ProjectSettings.asset` 与
  `ProductArchitectureTests` 同步为 `29`，不会复用已安装的 Build 28。
- 2026-08-09 20:32 CST，仓库唯一的 `scripts/ios_build_and_install.sh --no-launch` 从冻结发布提交
  `745a56620d15940437c907d98e94cefd1c48c70e` 完成 Unity DeviceSDK 导出、Xcode Release 编译、自动签名与安装；
  manifest、签名 App 与设备库存回读一致为 `com.jiaweizhou.fidgetspinner.codex`、`0.1.0 (29)`。发布前 Unity
  首次导出产生的 URP 运行时资源列表与 Sentis 编译符号序列化已先纳入提交，再重跑完整 `236/236`，没有绕过
  “源码变化即拒绝签名/安装”的发布门禁。
- 设备在线、tunnel `connected`、DDI 可用，安装回执与 app inventory 回读均成功；安装时手机
  `passcodeRequired=true`，因此本轮按 `--no-launch` 安装，没有伪报自动启动。用户解锁后可直接点开
  **Fidget Spinner**。完整证据归档于 `Logs/Build29Evidence/`，其中包含发布流水线、Unity 导出、测试 XML、
  build manifest、安装回执和设备端版本回读。
- 本节是 Build 29 的当前发布结论；下方各专项中“待视觉批准／未推送”等字样记录的是门禁批准前的阶段状态，
  现已由本节的八组批准与安装证据取代。安装不等于真机验收：磁吸推牌、磁吸扇牌、详情推镜、场景切换、成长图鉴
  性能、Combo 动画与触感仍需在已解锁 iPhone 上逐项确认。

## 顶部与成长 Tab Bar 进度数字可读性（代码、测试和原生预览已完成；待视觉批准，未推送）

> **当前视觉门禁：页面顶部等级数字与成长 Tab Bar 进度条两端等级已放大，并由真实 shipping SwiftUI 组件输出同屏对照；用户明确批准本轮字号前不构建或安装到 iPhone。**

- 顶部产品身份的 `LV` 数字从业务层硬编码 `9 pt semibold` 提升为共享 `ProductTypography` 的
  `caption bold`（默认 `12 pt`），继续使用 Oxanium 等宽数字和 Dynamic Type。成长进度条原先把左右里程碑
  硬编码为 `7 pt`；现在迁入组件库的 `ProductMilestoneProgressGauge`，统一使用 `caption2 bold`
  （默认 `11 pt`），并把最小行高提高到 `16 pt`，避免三位数或放大字体时裁切。业务层只传入上一等级、
  当前等级、下一等级和进度，不再自行绘制端点字号、轨道或当前位置圆点。
- shipping `FidgetProductUIComponents.swift`、`FidgetComboHalo.swift`、`CodexSwiftUIOverlay.swift` 与原生预览 App
  已通过 iPhone Simulator arm64 / iOS 15 Swift typecheck。隔离 Unity EditMode 专项回归 `2/2` 通过，覆盖顶部
  不得回退到 `9 pt`、端点不得回退到 `7 pt`、共享组件调用、`11 pt` 语义字号与 `16 pt` 防裁切行高；报告为
  `Artifacts/ProgressEndpointTypographyNativePreview/progress-endpoint-focused-tests.xml`。
- 真实原生顶部和成长 Tab Bar 分别渲染后合成的视觉验收图为
  `Artifacts/ProgressEndpointTypographyNativePreview/progression-endpoint-top-bottom-contact-sheet.png`；原始全屏图
  `progression-thumbnail-top.png` 与 `progression-thumbnail-hud.png` 保留在同目录。预览使用 shipping 组件库与
  `ProductUiState`，不是概念稿。当前只完成代码、测试和 Simulator 视觉门禁，没有生成或安装新的 iPhone build。

## 选择页进入详情的由外到内推镜（运行时、测试与 Unity 预览完成；待视觉批准，未推送）

> **当前视觉门禁：选择页进入详情不再只切换模型姿态。模型相机、背景、中景、双层星空、左右近景与承托共用 `0.68 s` 时间轴；峡谷岩壁／赛博建筑向两侧退场，远景分层放大，形成从入口向内部推进的空间感。真实 shipping Unity 场景已输出峡谷和赛博两套 0 / 33 / 67 / 100% 检查帧；用户明确批准预览前不构建或安装到 iPhone。**

- `SpinnerPresentationTransition.DurationSeconds` 由 `0.42 s` 调整为 `0.68 s`，三类 shipping 相机
  `PortraitCameraFramer / OrbitPresentationCamera / EdcPortraitCameraFramer` 继续在同一曲线上插值列表终态与详情初态，
  没有用黑场、跳切或第二套模型替身。`SpinnerEnvironmentPresenter` 与 `SpinnerGroundingStage` 改用相同的确定性
  smoothstep 时间轴，支持中途反向；快速返回列表时从当前插值位置反向，而不是重新从端点闪跳。
- 详情推进期间背景放大到 `1.16×`、中景 `1.20×`、深／近星空分别 `1.035× / 1.075×`、前景 `1.10×`；
  左右近景同时向屏幕外移动；独立生成的临时承托沿时间轴退去，背景中与场景一体化的承托仍随远景推进保留。全部使用
  Transform，不逐帧重绘位图，也不改变转子刚体、角速度、
  手势或 Haptic 管线。详情 UI 不再抢在空间推进前出现：原生列表卡片以轻微放大淡出，控制条延迟 `0.48 s` 显示，
  onboarding 延迟到完整 `0.68 s` 后显示，避免 SwiftUI 覆盖层把 Unity 的推镜遮掉。
- `SpinnerEnvironmentTests` 在 Unity Test Runner 为 `8/8` 通过；新增断言覆盖共享时长、深度缩放端点／中点、
  三套相机预览时间点、环境精确时间轴以及原生 UI 延迟。`CodexSwiftUIOverlay.swift` 另经 `xcrun swiftc -parse`
  通过。真实场景联系表位于
  `Artifacts/DetailEntranceTransition/detail-entrance-contact-sheet.png`，上排为星岩峡谷、下排为霓虹都市，
  每排从左到右是 `0 / 33 / 67 / 100%`。iPhone 上的实际帧率、手持观感与 Reduce Motion 行为仍待真机验收。

## 磁吸扇牌 Blender 实体网轨、AAA/QKA 随机牌面、刚性分层与防回归门禁（源模型、shipping 场景、测试和预览已完成；待视觉批准，未推送）

> **当前视觉门禁：背部轨道已从 Unity 程序平面/纹理表现替换为 Blender 制作的实体暗槽、圆丝金属网和三枚独立磁体，并向牌身内部移动；完整滑轨外轮廓实测距圆角牌身最小 `7.590 mm`，高于锁定的 `6.0 mm`。A/Q/K 使用 App Oxanium 700 字形的 Blender 实体网格，每片正面保留左上直立与右下 `180°` 两组 `rank + 小黑桃` 对角索引；背面不复制角标。每次由 Library 进入详情页时只在整组 `AAA` 与底/中/顶 `Q/K/A` 之间 50/50 选择，不逐层乱抽。控制器保持底片固定、中片 45°、顶片 90°。shipping Unity 场景已经重建并输出 AAA/QKA 与原有全套多视角；四档、阻尼、触摸、Haptic 与音频参数未变。用户明确批准预览前不构建或安装到 iPhone。**

- Blender 可复现源为 `ArtSource/FanCard/FanCardBackMechanism.blend`，构建脚本为
  `ArtSource/FanCard/build_fan_card_back_mechanism.py`，发布网格导出到
  `Assets/_FanCard/Models/FanCardBackMechanism.fbx`。`Track_Undercut` 是带倒角的实体下沉弧槽；
  `Track_Grille` 由 9 条纵向弧丝、72 条横向圆丝构成，丝径 `0.11 mm`，没有封闭底面或透明假孔；
  `Magnet_01...03` 是三枚独立倒角磁体；`Ace_A_Oxanium`、`Queen_Q_Oxanium` 与 `King_K_Oxanium`
  从 App 同一 Oxanium variable font 静态实例化为 700 weight，再转换为统一 `6.40 × 0.15 mm`
  高度/厚度的封闭 relief mesh。机械弧仍为 `45°`，两端各约
  `3.083°` 只用于圆头包边和最后一枚磁体的视觉留量，不进入 `FanCardDetentProfile`。
- `FanCardSceneBuilder` 固定 ModelImporter 的比例、轴向、材质和网格压缩规则，再按名称装配上述四类 FBX
  Mesh。金属网材质不再绑定 BaseMap/MainTex，因此孔洞来自真实拓扑；网格位于磁体外侧，低角度和背视图中
  可以直接看到其下三枚金色磁体。Unity 导入结果为 `4095 vertices / 6048 triangles`，源 Blender 网格为
  `3510 vertices / 6048 triangles`；没有给模型增加 Collider、Rigidbody 或质量。
- `fan-card-modeling-guardrails` 已作为仓库 skill 和本机 Codex skill 安装；仓库级 `AGENTS.md` 强制所有扇牌几何、
  滑轨、磁体、字形和装配任务先使用该 skill。`Docs/FanCardModelingGuardrails.md` 记录不可回归项，
  `ArtSource/FanCard/fan_card_guardrails.json` 是尺寸与坐标的唯一数据源，`validate_fan_card_guardrails.py` 同时核对
  JSON、Blender 脚本、C# 规格、shipping scene、测试源码和 Blender 构建报告。当前随动点为
  `(-49, -27) mm`，整条下沉槽外轮廓的最小边距为 `7.590 mm`；低于 `6.0 mm` 会直接失败。
- 冻结 `CardGeometryValidator` 在重建后的 shipping scene 输出 `=== VALIDATION: ALL PASS ===`，继续覆盖三张
  刚性实体牌、`2.5 mm` 厚度、`1.0 mm` 空气间隙、真实轴孔、无牌片/轴承穿模和封闭拓扑。
  `FanCardAcceptanceTests` 为 `20/20`，最新报告为 `Logs/FanCardModelingGuardrailsTests.xml`；新增断言锁定
  FBX 网格面数、真实圆丝厚度与法线、无贴图假孔、背面层级、网格在磁体外侧、每层三枚磁体以及四档/45°
  物理配置不变，并逐点采样滑轨两侧外轮廓和圆头，确保边距门槛不会因后续变量修改而回退。
- 原构建器把 `middle + bottom` 交给 Controller，导致手指操作时底片也跟着旋转；现在序列化运动层为
  `MiddleCard + TopCard`，因此 `BottomCard` 始终保持 `0°`，中片/顶片分别为 `45°q / 90°q`。每片正面只装配
  两个直接子级 `RankGlyph_TopLeft` 与 `RankGlyph_BottomRight`，两组同样各有一个 `CornerSpade`；右下 rank
  与黑桃共同旋转 `180°`。`FanCardFaceRankPresenter` 只替换这六个 MeshFilter 的 `sharedMesh`：`AAA` 为三层 A，
  `QKA` 为底层 Q、中层 K、顶层 A，同一牌片两角始终同字。所有角标直属所属刚性牌片；`BackFaceArtwork`
  和背面角标保持移除。A/Q/K 不使用 TextMesh，因此没有字形图集裁边、Z-fighting、叠层 Renderer 或跨牌片父级问题。
- 本轮 `FanCardAcceptanceTests` 为 `21/21`，报告为 `Logs/FanCardAaaQkaTests.xml`；除原有
  物理、网轨和几何断言外，断言锁定底片静止、中片 45°、顶片 90°、每片两组对角索引、右下 `180°`、
  同组 rank/黑桃同向、直接父级、无任何 TextMesh/背面角标，以及 A/Q/K 的完整高度、厚度和三角面；新增测试还锁定
  `0.5` 随机阈值、Q/K/A 层序、同牌双角共用网格，以及切换牌面不改变 Transform、进度或发出语义事件。
  冻结几何门禁报告 `Logs/FanCardAaaQkaGeometryValidation.log` 仍输出 `=== VALIDATION: ALL PASS ===`。
- Blender 独立几何检查与三张源预览位于 `../../../Artifacts/FanCardBlenderPreview/`，结构报告为
  `fan-card-back-mechanism-report.json`。shipping Unity 预览位于
  `../../../Artifacts/FanCardMaterialPreview/`，其中 `fan-card-back-track-closeup.png` 清楚展示网孔和三枚磁体，
  `fan-card-back.png` 展示展开后的背部装配，`fan-card-ace-closeup.png` 展示左上角标，
  `fan-card-corner-index-bottom-right-closeup.png` 展示旋转 `180°` 的右下角标；top、authored hero、left/right
  oblique 与 low-angle 也已同步重渲染。新增 `fan-card-aaa-hero.png`、`fan-card-aaa-top.png`、
  `fan-card-qka-hero.png` 与 `fan-card-qka-top.png` 分别证明两套合法整组状态。当前等待用户确认 Q/K/A 字形、
  层序、双角标位置与朝向；未推送真机。

## 成长图鉴滚动掉帧与空闲逐帧刷新修复（Build 30 已安装并启动；待真机性能验收）

> **当前状态：Profile 与陀螺页打开的是同一个 `ProgressionLevelDetailsSheet`，因此两处同时卡顿的根因在共享图鉴滚动树，而不是入口跳转。Build 30 已切断 20 Hz 运动遥测对图鉴的无关重绘，压平逐卡毛玻璃层，并在 Sheet 覆盖期间暂停后台逐帧动画；已安装和启动到 iPhone，真机滚动帧率和温升仍待用户验收。**

- `ProductUiState.motionTelemetry` 最快每 `0.05 s` 发布一次。原图鉴的等级、Badge 和外观三个滚动页都直接
  `@ObservedObject` 同一个总状态，所以即使图鉴不显示角速度，每次遥测也会重新求值整棵列表。现在入口在打开
  Sheet 前捕获一次 `ProgressionCatalogSnapshot`；Sheet 本身不再订阅 `ProductUiState`，并以 session `UUID` 做 O(1)
  Equatable 比较。图鉴内容在一次打开会话内保持一致，关闭后再次打开会重新取得最新等级、外观与 Badge 数据。
- 等级页外层由 eager `VStack` 改为 `LazyVStack`。`ProgressionLevelDetailsSheet` 不再套用带独立 navigation title
  与完成键的 `ProductBottomSheetShell`；新的 `ProgressionCatalogHeader` 把“成长图鉴”、完成键与“成就 / Badge /
  外观”分段控件装入同一个 24 pt 圆角玻璃容器，下面的三类内容共享这一固定头部。结构只参考用户提供的 Opal
  层级，没有复制其素材、文案或业务导航。
- Sheet 根背景不再使用完全不透明的 `ProductBackdrop`。正常模式只建立一个覆盖全页的
  `ultraThinMaterial` 系统模糊层以 `78%` 强度覆盖，再叠 `24%` 黑色与轻微纵向暗角；iOS 16.4+ 的
  presentation 容器显式设为透明，
  因而能把下方 Unity / Profile 场景的色彩柔和地带进图鉴。图鉴根部启用 `productStaticSurfaceMode`，等级、Badge、
  外观卡和 Badge 内圈都只做静态透明填充，不再进入 iOS 26 `glassEffect` 或为每个 cell 建立独立 material。开启系统
  “降低透明度”时自动切换为 `94%` 黑色静态底，保持文字可读性；iOS 15 保留兼容编译路径，不伪报透明
  presentation 支持。
- 旧的 `5 pt` 轨道、`11 pt` 圆点和 `CAGradientLayer / CAKeyframeAnimation` 过光已全部删除。
  `ProgressionVerticalRail` 现在由完成、当前、未来三段静态 `3 pt` Capsule 组成，透明度分别为 `42% / 92% /
  10%`，段间固定 `4 pt` 断点；三段宽度完全相同，只用不透明度表达状态。等级行的已完成和当前圆点也都固定
  `7 pt`，只用 `22% / 88%` 透明度区分；`CURRENT` 胶囊和当前卡片强调色玻璃保持移除。外观页仍以本地
  `equippedSkinId` 立即反馈点击，再把选择发送给 Unity。
- `NativeArtworkLoader` 和 Badge artwork loader 各使用有上限的 `NSCache<NSString, UIImage>`；Bundle PNG 不再在
  SwiftUI `body` 重算或 cell 复用时重复同步解码。每枚 Badge 的程序化皮革 `Canvas` 保持原 non-linear 色彩空间，
  但启用 `rendersAsynchronously: true`，避免数百条 pore / crease path 集中阻塞主线程滚动。
- `AutoSpeedRotorAnimator.update` 新增 `active` 门禁；AUTO 关闭、Reduce Motion、速度归零或图鉴 Sheet 正在覆盖
  任一条件成立都会 invalidate `CADisplayLink`。成长缩略图的 repeat-forever shimmer 也在 Sheet 打开时停止、关闭后
  恢复。这些门禁没有改变转子物理或 Haptic 语义。
- `ProgressionCatalogScrollPath_DoesNotTrackMotionOrDecodeArtworkPerFrame` 已更新，锁定快照不含运动遥测、重列表
  Equatable 边界、LazyVStack、顶部单一容器、两处图片缓存、异步 Canvas、三段同宽静态轨道、4 pt 断点、
  圆点同尺寸透明度状态语言、唯一根毛玻璃、静态子卡、无旧 sheen / 粗圆点以及覆盖期间的动画停止条件。三份
  shipping Swift 通过 iPhoneOS 15 arm64 类型检查；成长图鉴专项 `1/1`、架构专项 `1/1`、完整 Unity EditMode
  `236/236` 全部通过，报告已归档于 `Logs/Build30Evidence/`。
- 获准安装的真实原生预览位于 `Artifacts/ProgressionCatalogSingleBlurPerformance/`。默认等级页为
  `progression-thumbnail-sheet.png`，HUD on/off 与 AUTO 动画检查文件也保存在同目录。等级页尺寸为
  `1206 × 2622`；其背后的青色 / 暖橙场景代理仅用于清楚展示 shipping Sheet 的透色与模糊程度，Sheet、标题、
  Tab、轨道和列表本身均直接来自 shipping SwiftUI。可直接检查顶部一体容器、3 pt rail、4 pt 断点、同尺寸状态
  圆点和整页毛玻璃；较早 `Artifacts/ProgressionCatalogOpalHeader/` 与 `Artifacts/PerformanceFixScroll/` 已被本轮
  方案覆盖，不再作为批准候选。用户查看该预览后明确要求推送；Build 30 已完成签名、安装和启动。

## 随形微光默认环境与四主题选择器（运行时已集成并测试；视觉批准待确认，未推送手机）

> **当前视觉门禁：默认环境继续为“随形微光”，星岩峡谷与霓虹都市继续保留；第四个有限选项“矿脊台座”已再次按用户反馈重做。俯视黑色低多边形与写实近景自然矿石均已被后续意见替代；当前候选是下方约三分之一的远景 digital collage 矿脊，以真实岩纹片段、雕塑几何切面、抠图边、错版阴影和静态细颗粒组合，shipping 玩具落在窄峰顶。真实 shipping Unity 六款壁纸与完整四页选择器已重新生成。用户明确批准这些预览前不得构建或安装到 iPhone。视觉批准待确认，未推送手机。**

- 参考为用户提供的 [Mobbin Oura Meals 横滑录屏](https://mobbin.com/screens/85d08d6d-c2c6-44e2-9117-f3276492ae90)。原视频为 `720 × 1560`、`60 fps`、约 `6.17 s`：近黑底不做整屏换色，而是旧页的大半径低饱和色场随页面退出，新页色场从相反方向进入；手指拖动直接跟随，松手后约 `0.22–0.28 s` 落稳。采样色域覆盖粉灰、青绿、橄榄、暖中性与蓝灰，但黑位、暗角和低频柔光保持一致。本实现复用原生分页现有 `0.22 s easeOut`，不另造与模型分页竞争的计时器。
- `SpinnerEnvironmentThemeCatalog` 现在按 `adaptive / canyon / cyberpunk / mineral-ridge` 排列，未知或首次安装回落 `adaptive`。`FidgetAppCoordinator` 和 Swift `ProductUiState` 的持久化默认值均同步为 `adaptive`；原生环境选择器继续有限、不循环、单 CTA，只把主题数量扩为四项。
- `mineral-ridge` 不读取当前玩具色相：当前 `941 × 1672` 资源 `Assets/Resources/EnvironmentBackgrounds/mineral-ridge-digital-collage-v3.png` 使用单色梯度和远景拼贴载体，只在有限区域保留真实岩层纹理，其余由安静的雕塑平面、切纸／半透明切面、抠图边、错版阴影和细颗粒构成；由内置 imagegen 同时参考用户截图的远景构图与被否决摄影版的岩纹生成，未复制金融卡片、文字、UI、花草或品牌。Unity importer 固定 sRGB、无 mip、Clamp、NPOT None 与 iPhone ASTC 8×8。
- 首轮 `64 × 128` 程序渐变 + 24 段 flat-shaded 黑色矿石和第二轮写实近景自然矿石均已被用户后续意见替代；`SpinnerGroundingStage` 保持 baked-support metadata，不为该主题绘制额外程序台座。当前拼贴底板直接提供载体，运行时以 `_BaseMap_ST.w=-0.034` 精确校准峰顶与 shipping 玩具的接触点；底板同时供 IBL 采样，彩色 subject glow 关闭，只保留 `0.42` 强度的中性窄接触阴影。该链不新增 Collider／Rigidbody，也不写产品 Transform、角速度、机构、输入、音频或 Haptic。
- `EnvironmentParallaxUnlit.shader` 的 adaptive 分支用近黑纵向底色、`0.18` 暗角与 `0.012` 静态屏幕颗粒建立质感，颗粒强度是上一轮 `0.006` 的两倍。噪点只读取 `floor(input.positionHCS.xy)`，不读取 `_Time`，所以横滑与静止都不会产生 temporal shimmer。运行时 `SpinnerAdaptiveBackdropRules.GrainIntensity`、Shader 默认值、`SpinnerEnvironmentAssetBuilder` 与序列化 `EnvironmentParallaxMaterial.mat` 已同步，避免兜底值漂移。顶部光束继续以 `input.uv.y` 建立：顶部宽度系数 `0.52`，向下展开至 `0.92`；`TopLightFalloff=1.25`，底部明度 `0.08`、色彩保留 `0.18`。signed page offset 仍只控制旧／新色场的水平中心与权重；该链只改 presentation shader/property block，不写 Rigidbody、机构状态或 Haptic。
- 第二轮克制参数已经统一进入运行时 source of truth：所有产品身份色先经 HSV 限制 `S ≤ 0.20 / V ≤ 0.58`，主柔光强度从 `0.38` 降为 `0.26`，稳定副色权重从 `0.24` 降为 `0.16`，真实 renderer 采样影响从 `0.30` 降为 `0.18`；近黑顶色同步压至 `(0.024, 0.026, 0.031)`。SwiftUI 无壁纸 fallback 的产品色 opacity 同步降为 `0.16`，避免运行时与原生兜底漂移。
- 六款 `900 × 1600` 原生选择器壁纸已由 `EnvironmentWallpaperAssetCapture.CaptureAdaptiveOnly` 从各自 shipping Unity scene、冻结的 library framing 与相机构图重新生成到 `Assets/Plugins/iOS/SceneWallpapers/scene-wallpaper-adaptive-*.png`。本轮六款顶部光场联系表为 `Artifacts/AdaptiveBackdropPreview/adaptive-top-down-six-models-contact-sheet.png`，成功日志为 `Logs/ProductIdentity/top-down-adaptive-wallpaper-capture.log`；旧的模型中部径向版本不再作为当前视觉证据。
- 金属页滑向镜钢四翼的 `0 / -0.25 / -0.50 / -0.75 / -1.0` 与新场景进入帧也已由 shipping Unity 场景重新捕捉，联系表为 `Artifacts/AdaptiveBackdropPreview/Transition/adaptive-top-down-transition-contact-sheet.png`，日志为 `Logs/ProductIdentity/top-down-adaptive-transition-capture.log`；六帧保持固定的顶部入射方向，只横向交换产品色场。
- 四态原生选择器预览位于 `Artifacts/EnvironmentWallpaperPickerNativePreview/environment-picker-adaptive.png`、`environment-picker-canyon.png`、`environment-picker-cyberpunk.png`、`environment-picker-mineral-ridge.png` 及联系表 `environment-picker-contact-sheet.png`。预览工具使用当前 shipping Swift 全量依赖在 iPhone 17 Pro Simulator、`arm64-apple-ios15.0-simulator` 下编译并运行成功；四页分别正确显示“随形微光 / 星岩峡谷 / 霓虹都市 / 矿脊台座”，边界不循环。
- 六款 `900 × 1600` 远景拼贴矿脊壁纸由 `EnvironmentWallpaperAssetCapture.CaptureMineralRidgeOnly` 从 shipping Unity scene、真实材质、冻结 Library framing 与相机直接渲染到 `Assets/Plugins/iOS/SceneWallpapers/scene-wallpaper-mineral-ridge-*.png`；联系表为 `Artifacts/MineralRidgeDigitalCollagePreview/mineral-ridge-digital-collage-shipping-contact-sheet.png`，成功日志为 `Logs/MineralRidgeDigitalCollageWallpaperCapture.log`。这些是已校准峰顶落点的 shipping 实现合成，不是被否决的黑色低多边形或写实近景概念图。
- 上一轮顶部光场的完整 Library UI 预览由 `Tools/ProductIdentityNativePreview/capture.sh` 直接编译当前 shipping Swift 全量依赖，并把真实 top-down adaptive Unity 壁纸作为背景；金属与镜钢四翼截图及联系表位于 `Artifacts/ProductIdentityNativePreview/product-identity-gold.png`、`product-identity-metal.png`、`product-identity-library-contact-sheet.png`。该预览包含状态栏、顶部身份区、等级、模型、上移后的 Badge、分页点和双 CTA，不是无 UI 的概念合成；当前审批应以下一条颗粒增强预览为准。
- 颗粒增强后的当前完整 Library UI 预览位于 `Artifacts/AdaptiveBackdropPreview/WithUIGrain/product-identity-gold.png`、`product-identity-metal.png` 与 `product-identity-library-contact-sheet.png`；六款壁纸联系表更新为 `Artifacts/AdaptiveBackdropPreview/adaptive-six-models-contact-sheet.png`，横滑帧为 `Artifacts/AdaptiveBackdropPreview/Transition/adaptive-transition-contact-sheet.png`。成功日志为 `Logs/AdaptiveBackdropGrainWallpaperCapture.log` 与 `Logs/AdaptiveBackdropGrainTransitionCapture.log`。
- 最新 `SpinnerEnvironmentTests` 为 `13/13 Passed`，报告 `Logs/MineralRidgeDigitalCollageEnvironmentTests.xml`、日志 `Logs/MineralRidgeDigitalCollageEnvironmentTests.log`；覆盖顶部光场 shader 契约、四主题、`941 × 1672` digital-collage 底板资源、`-0.034` 精确纹理偏移、单色背景关闭产品 glow、接触阴影、baked stage 不重复绘制、主题切换不新增 Collider／Rigidbody 或注入角速度、横滑色相交接、新场景进场防回闪及峡谷／赛博回归。原生选择器／24 张壁纸 source contract 为 `1/1 Passed`，报告 `Logs/MineralRidgeDigitalCollagePickerArchitectureTests.xml`；shipping Swift 全量依赖再次在 iPhone 17 Pro Simulator 编译、运行并截图成功，矿脊副标题为“远景拼贴 · 不规则矿脊承托”。
- 颗粒专项 `PresenterSwitchesThemesWithoutTouchingTheModelMechanism` 为 `1/1 Passed`，报告 `Logs/AdaptiveBackdropGrainFocusedTests.xml`、日志 `Logs/AdaptiveBackdropGrainFocusedTests.log`；显式锁定运行时颗粒值为 `0.012`、可见质感范围 `0.010–0.014`、静态屏幕像素采样且 Shader 无 `_Time`，同时确认主题切换不向 Rigidbody 注入运动。首次原生预览编译因并行任务同时改写另一份 shipping Swift 文件而中止；文件稳定后原样重跑成功，不覆盖该并行改动，也不将中止计为通过。
- 本轮只新增远景 digital-collage 环境底板、主题资源接线、纹理落点偏移、中性接触阴影与原生第四页文案，没有修改任何产品几何、产品材质、贴纸、Collider、Rigidbody、输入、音频或 Haptic；没有执行 iOS build、签名、真机安装或设备启动。下一门禁是用户对上述真实 shipping 预览的明确视觉批准；批准后才可由总控纳入手机构建，Device Accepted 仍需目标 iPhone 验收矿脊接触感、灰阶明度、横滑节奏、Reduce Motion 与连续快速翻页。

## 磁吸推牌柔光棚拍布光（运行时与场景已更新，预览待视觉批准；未推送）

> **当前视觉门禁：磁吸推牌已从偏硬的单侧高亮改为主光压低、对侧补光抬高、反射软箱加宽的柔光棚拍结构。真实 shipping Unity 场景已输出 Library、hero、top、left/right oblique、low-angle 和两张 open-interior 预览；用户明确批准预览前不构建或安装到 iPhone。**

- 场景并非单灯：原结构是左上 `Key_UpperLeft`、对侧 `CoolFill`，再叠加运行时合成的反射软箱、对侧反光条、镜头侧可见性补光与很弱的视角高光。原先主灯 `0.88` 明显高于补灯 `0.32`，而主灯方向又与反射软箱方向重合，所以视觉上会像一盏过强硬灯。
- 当前 EDC 专属主灯为 `0.54`、补灯为 `0.42`；反射软箱峰值由 `0.42` 降到 `0.26`，对侧反光条由 `0.12` 提到 `0.18`。软箱横向羽化区扩大为 `0.22→0.88`，纵向为 `0.18→0.78`。银色材质的 GlossMapScale 从 `0.86` 收到 `0.68`、Normal scale 从 `0.38` 收到 `0.28`，并关闭直射方向光的 `_SpecularHighlights`、保留 `_EnvironmentReflections`；因此正视亮面由窄白线变为宽灰银渐变，斜视仍保留受控亮边。深色树脂仍能看到轮廓和层次。`EdcSceneBuilder` 的备用生成参数与 `MeshyEDC.unity` 序列化灯光已同步，避免运行时和场景文件漂移。
- 没有启用真正的体积雾或全屏雾化。雾会同时降低树脂 / 金属的局部对比并抬灰黑位；这里使用更大的虚拟发光面和更均衡的 fill ratio 来模拟柔光布，而不是把整个画面蒙白。扇牌的反射软箱参数保持原值，不受本轮 EDC 调光影响。
- 最新原始 `1290 × 2796` 预览位于 `../../../Artifacts/EDC/BroaderSofterHighlights_2026-08-09/`，总览为 `00_ContactSheet.png`；上一版 / 当前 hero 与 top 对照为 `00_Previous_Current_Comparison.png`（左旧、右新）。EDC 聚焦 EditMode `25/25` 通过，报告为 `Artifacts/EDCBroaderSofterHighlightsEditModeTests.xml`；断言覆盖场景序列化灯值、软箱峰值与横纵羽化范围、材质 Gloss / Normal 参数、直射高光关闭、环境反射保留及树脂 / 金属分工。环境测试此前 `8/8` 通过，报告为 `Artifacts/EDCDiffusedLightingEnvironmentTests.xml`。iPhone 仍停留在旧 Build 28。

## 历史 Build 37：双主题长按场景壁纸选择器（已被三主题默认方案覆盖）

> **历史状态：Build 37 证明长按、屏幕中心缩放、有限轮播、邻页露边与单 CTA 已进入手机；它当时只有峡谷／赛博两个主题。2026-08-18 的“随形微光默认 + 峡谷／赛博备选”已覆盖其当前主题数量与默认项，旧 Build 37 不得冒充本轮三主题视觉已安装或已获批准。以下内容仅保留原双主题实现与证据。**

- `SpinnerLibrary` 的实时模型分页使用 `LongPressGesture(minimumDuration: 0.55, maximumDistance: 14)` 与
  `simultaneousGesture` 接入，不抢走既有横向模型翻页。进入时先捕获当前 Unity + 原生 UI 的完整屏幕，并同时冻结当时的
  `capturedTheme`；该主题的卡片始终读取 `UIImage` 快照，即使滑到另一场景后再滑回，也不会退回中性姿态的壁纸资源。
  快照卡片使用完整屏幕大小的固定画布，仅通过 `scaleEffect(..., anchor: .center)` 在 `0.52 s` 内缩至 `0.66`，frame
  不参与动画、过程中不淡出。透明 `UIHostingController` 在 UIKit 完成首帧 layout 后才显式开始缩放，保持一张连续表面原地收拢。
  Reduce Motion 下直接到终态。
- 选择器不再使用会裁掉相邻页的全宽 `PageTabViewController`。运行时按 `EnvironmentTheme.allCases` 只渲染两张真实主题卡，
  以有限索引计算相对位置，卡片中心距为 `屏宽 × 0.66 + 22 pt`；第一页只在右侧露出第二页，第二页只在左侧露出第一页，
  边界方向的拖动被锁住，不循环、不复制。横向拖动只更新 transform；跨过阈值后先把当前卡片和相邻卡片一起滑到目标位置，
  再无动画重置索引，避免内容跳变。顶部标题、底部分页点和唯一主 CTA 锚定屏幕，不随卡片移动；
  卡片点击不再承担确认，只有 CTA 会调用 `onSelect(state.environmentThemePreview)`。关闭叉号仍不出现。
- 终态读取当前 key window 的真实 `safeAreaInsets`，以完整的 `bottom - top` 抵消 SwiftUI 安全区造成的物理中心偏差；底层模糊
  背景的横向 bleed 只通过 `scaleEffect` 产生，layout frame 宽度严格等于屏幕，不会再次把所有居中内容右移。左右卡片和快照均
  共用同一套固定全屏画布、圆角、阴影和 66% 缩放规则。
- `ProductUiState` 使用 `fidgeting.environment.theme.v1` 持久化选择，并通过
  `SetEnvironmentThemeFromNativeUi` 发给唯一 `FidgetAppCoordinator`。Coordinator 在每个 shipping 模型场景加载时
  读取同一键；因此六款陀螺共享一个场景选择，不会在模型切换后退回峡谷，也没有触碰转子角速度、阻力、磁吸状态机或
  Haptic 路由。
- `SpinnerEnvironmentThemeCatalog / SpinnerEnvironmentPresenter.ApplyTheme` 已把主题资源、饱和度、中景开关、双层动态星空、
  前景层和 IBL 环境采样收拢为独立运行时接口。峡谷继续使用原 L0–L5 前景资源；赛博候选打开独立中景和动态星空，
  当前因 V13 近景仍烘焙在合成图内而不复用峡谷左右岩壁。切换会重建环境反射和模型 bounce light，但不修改产品物理。
- iOS 构建管线当前会复制 `Assets/Plugins/iOS/SceneWallpapers/`；运行时实际使用的是六款产品 × 两个主题的十二张
  `900 × 1600` 分模型预览。目录中另有 `scene-wallpaper-canyon.png` / `scene-wallpaper-cyberpunk.png` 两张旧通用图，
  当前 SwiftUI 不再请求它们，因此文件总数是 14 而用户可选主题仍只有 2；这两张旧资源列为后续减包清理项。
  `EnvironmentWallpaperAssetCapture` 对六款 shipping 产品各生成峡谷／赛博一对图，并在同一对图之间冻结模型姿态、
  Camera Transform、Projection Matrix、library framing 和输出尺寸。原先峡谷使用实时／旧捕捉而赛博使用另一相机捕捉，
  是同一陀螺在两页大小不一致的根因；现在选择器以 `theme + modelId` 取图，不再跨模型或跨相机构图复用缩略素材。赛博 Unity
  候选纹理关闭 mipmap、使用 Clamp、保留 NPOT 原尺寸并在 iOS 使用 ASTC 8×8，避免额外缩放插值。它仍未达到最终
  `1882 × 3344` 生产分辨率，不能把当前候选资源宣称为 2x/3x 最终美术。
- 真实原生预览位于 `Artifacts/EnvironmentWallpaperPickerNativePreview/`：
  `environment-picker-canyon.png`、`environment-picker-cyberpunk.png` 和
  `environment-picker-contact-sheet.png`。本轮已由两次独立 Simulator app 构建覆盖：峡谷居中时只在右侧露出赛博卡片，
  赛博居中时只在左侧露出峡谷卡片，不再把唯一邻页复制到左右两侧；
  两种状态均显示唯一的“选择当前场景”CTA，卡片中心线和模型占屏尺寸一致。完整 shipping Swift（含 StoreKit / Gacha 依赖）在
  iPhone Simulator arm64、iOS 15 target 下编译并运行成功，`CodexSwiftUIOverlay.swift` 与依赖文件也通过 `xcrun swiftc -parse`。
  架构回归锁定：快照按 `capturedTheme` 留在轮播、每个真实主题只渲染一次、有限索引不循环、边界拖动锁住、单 CTA 确认、
  无关闭按钮、固定全屏画布与中心缩放锚点、宿主不做黑场 alpha dissolve。主工程被现有 Unity 实例占用后，本轮在隔离快照中运行
  `LibraryLongPressOpensTheWallpaperStyleEnvironmentPicker`，结果 `1/1` 通过（用例 `0.085 s`，报告为
  `Artifacts/EnvironmentWallpaperPickerNativePreview/editmode-results.xml`）。本轮统一发布授权已经确认；本 feature 已随 Build 37
  覆盖安装，并将在 iPhone 上验收真实长按缩放、快照持续性、有限双页滑动手感与 CTA 点击。

## 三层磁吸扇牌双响应手感、触摸优先级与异常轴环清理（运行时、场景与预览已完成；待视觉批准和真机验收）

> **当前状态：运行时、Profile asset、shipping scene、语义 Haptic 路由和预览生成器已经同步；可见 Unity Editor 内的扇牌专项回归 `18/18` 通过并导出 XML。此后新增的“连续三次跨档不得继承旋转限流”用例已被 Editor 编译并发现为第 19 项，但 Mac 锁屏前未完成补跑，因此不把它误报为已通过。真实 shipping 场景已生成必需多视角；视觉改动尚未获得用户批准，本轮没有构建或安装新包，所有 iPhone 触感仍待真机验收。**

- `FanCardDetentProfile` 现在同时定义慢推和快速穿越两套端点，并由连续 `traversalAuthority` 在同一个
  `FanCardMagneticTrack` 内混合。慢推为脱档 `0.050`、手指弹簧/阻尼 `96 / 6.0`、磁峰/摩擦
  `6.4 / 0.38`、最高速度 `2.4 s⁻¹`；快速路径为脱档 `0.024`、弹簧/阻尼 `220 / 5.2`、磁峰倍率/摩擦
  `0.50 / 0.16`、最高速度 `5.0 s⁻¹`。Profile asset 与 `ApplyReferenceDefaults()` 已同步，未制造第二套隐式默认值。
- `FanCardController` 使用屏幕滑动速度 `0.55→1.30 屏宽/秒` 为主要分类输入；设备确实提供有效
  pressure 增量时才把它作为辅助输入。慢推继续把手指圆弧幅度映射为连续目标，保留预压、脱档和逐档阻尼；
  快速手势锁定当前方向端点，松手后由同一物理轨道逐档完成，反向快速手势可切换端点。它没有绕开
  `Breakaway / DetentCrossed / DetentCaptured`，最终捕获仍精确归档并把速度清零。
- `EdcDeviceMotionController` 在扇牌直接拖动及已授权的快速收尾期间停止 `IosDeviceMotion`，同时每帧重发
  冻结的 `SceneParallaxInput` 样本，避免场景视差因样本过期自动回零、让轴心从手指下漂走。结束时重新启动
  Core Motion 并以当前设备姿态建立参考，不把拖动期间累计的陀螺仪变化突然补回画面。
- 扇牌 `DetentCrossed` 由 Coordinator 进入专属 `FidgetHapticRouter.EmitFanCard`：实际跨档速度映射到
  Intensity `0.76→1.00`、Sharpness `0.78→0.96`；机械音频仍只消费同一语义事件，5 个原子 click 通过
  8 个预分配声部播放。Controller 内没有新增原始触摸到 `IosHaptics` 或 AudioSource 的直连。
- `FanCardSceneBuilder` 不再为 `CommonAxis_ShadowSleeve` 创建可见圆柱；重建后的 shipping scene 只保留一个
  仅含 Transform 的结构标记，没有 MeshFilter 或 Renderer。牌片本身的真实倒角轴孔不变，因此正面不再出现
  来源不明的悬浮金属环。Unity 6 Metal 已输出 top、authored hero、left/right oblique、low-angle、back、closed
  和四个档位帧，位于 `../../../Artifacts/FanCardMaterialPreview/`，总览为
  `fan-card-adaptive-contact-sheet.png`；本节的视觉批准仍待用户明确确认。
- `FanCardAcceptanceTests` 已新增慢/快速手势分类、30/60/120 Hz 快速全档穿越、单次脱档、最终零速度、
  Core Motion 触摸互斥、冻结视差、专属 Haptic 路由及轴标记无 Renderer 的回归断言。测试代码存在不等于
  全部测试已执行：当前报告 `Logs/FanCardAdaptiveInteractionTests.xml` 为 `18/18`，覆盖本轮物理、帧率、场景、
  输入互斥和架构回归；随后追加的无旋转限流用例因 Mac 锁屏仍待补跑。iPhone 上的慢推逐档辨识、快推全开/全收、
  声触同帧和连续往返稳定性全部保持待真机验收。

## 磁吸推牌深色树脂 / 亮银金属分层与内部细面（代码、场景、测试和预览已完成；待视觉批准，未推送）

> **当前视觉门禁：本轮把原先几乎全部共用金属材质的五层模型拆成深色树脂主体与亮银金属件，修复推开后内部粗糙和斜角过曝；真实 shipping Unity 场景已经生成必需六视角，并额外生成两张完全推开内部视角。Build 28 仍是上一版全金属预览包，不包含本节改动；用户明确批准本轮预览前不构建或安装新包。**

- `L1_TopFrame` 使用亮银 PBR 金属；`L2_UpperShell`、`L3_Gasket`、两条导轨、`L6_InnerFrame` 与
  `L7_BottomShell` 使用深石墨树脂；六枚磁体和四枚螺钉改为独立亮银金属。该分工已经由
  `EdcSceneBuilder` 写入 shipping scene 与 `EDC_Root.prefab`，不是只改 Inspector 临时预览。
- 亮银材质仍为 Metallic `1.00`，但 Base tint 固定为 `0.66 / 0.70 / 0.72`、GlossMapScale `0.68`、
  roughness influence `0.58`、Normal scale `0.28`；源 emission 贴图从运行时材质移除并关闭 `_EMISSION`，
  同时关闭直射 `_SpecularHighlights`、保留 `_EnvironmentReflections`，
  金属不再像自发光白灯带。深色树脂为 Base `0.020 / 0.026 / 0.032`、Metallic `0.03`、Smoothness
  `0.52`，不使用 Normal 或 metallic/gloss 贴图，因此推开后内框和底壳呈细腻注塑哑光面，而不是继承 Meshy
  金属法线形成砂砾感。
- 磁吸推牌专属环境 ReflectionIntensity 从 `0.72` 收到 `0.56`、Library reflection scale 从 `0.32`
  收到 `0.28`；柔光化后宽面 softbox 峰值为 `0.26`、对侧条光为 `0.18`、基础反射场缩放为 `1.00`。扇牌继续使用
  原先 `0.86 / 0.24 / 1.28`，所以本轮控曝没有改变其他产品。高光保留为辨识金属所需的窄光带，但各角度
  的树脂轮廓、圆形磁体和外框不再被整片白场吞没。
- shipping Unity / Metal 原始 `1290 × 2796` Library、authored hero、top、left/right oblique、low-angle
  六视角及两张 open-interior 视角位于 `../../../Artifacts/EDC/ResinMetalContrast_2026-08-09/`，总览为
  `00_ContactSheet.png`。EDC 聚焦 EditMode `25/25` 通过，报告为
  `Artifacts/EDCResinMetalContrastEditModeTests.xml`；断言覆盖五层与导轨材质分工、树脂无法线、磁体/螺钉
  高金属度与亮度、金属无 emission、粗糙度/法线/光泽参数及产品专属反射强度。

## 磁吸推牌细腻高反射金属材质（Build 28 已覆盖安装；待解锁启动与真机肉眼验收）

> **当前状态：本轮只调整磁吸推牌的 PBR 材质采样、表面微法线和该产品的反射环境，没有改模型轮廓、推牌机构、磁吸状态机或 Haptic。用户查看真实 shipping Unity 六视角后明确要求“推到手机上看看”，视觉门禁已满足；Development 预览 Build 28 已覆盖安装到 iPhone，自动启动被设备锁屏拒绝，尚不能把安装误报为真机肉眼验收。**

- 当前资产不是 Blender 离线渲染：源文件为 Meshy AI 导出的
  `Assets/_EDC/Source/Meshy_AI_Futuristic_Top_View_C_0804153834_texture.fbx`，由
  `EdcImportPipeline` 切分为五个运行时 OBJ 层，最终由 Unity 6 URP 在 Metal/iPhone 上实时渲染。
  源网格为 `1,323,175` 顶点、`1,994,857` 三角面；五个运行时层合计仍为 `1,994,857` 三角面，OBJ
  面审计全部为三角面、没有四边面。该数量忠实保留源资产，但明确尚未完成移动端 retopology / LOD 优化。
- 粗糙度不再原样反转为强颗粒 smoothness：packed metallic/smoothness 的运行时 source-of-truth 使用
  `smoothness = 1 - roughness × 0.78`，法线强度从 `1.00` 降到 `0.70`，既压低旧贴图的砂砾状高光又保留边缘细节。
  Base / Metallic / Roughness / Normal / Emission 五张 `2048 × 2048` PBR 贴图统一使用 trilinear、`4×`
  anisotropic、`-0.25` mip bias、最高压缩质量；材质锁定 Metallic / Smoothness / GlossMapScale 为 `1`，
  保持 URP environment reflections 和 specular highlights 开启。
- `SpinnerEnvironmentPresenter` 的 EDC profile 反射强度从 `0.66` 调到 `0.72`，Library 反射缩放从
  `0.30` 调到 `0.32`；`SpinnerImageBasedLightingController` 为磁吸推牌接入宽面 softbox 与较暗的对侧条形光，
  让高反射读成连续金属光带，而不是点光源造成的零散白斑。此项只改变环境采样，不新增模型几何或碰撞体。
- shipping 场景原始 `1290 × 2796` Library / authored hero / top / left / right / low-angle 预览位于
  `../../../Artifacts/EDC/PolishedFineMetal_2026-08-09/`，六视角总览为 `00_ContactSheet.png`。EDC 专项
  EditMode `25/25` 通过，报告为 `Artifacts/EDCPolishedFineMetalEditModeTests.xml`；其中现有材质验收已加入
  Metallic、Smoothness、GlossMapScale、Normal scale、roughness influence 和产品反射 profile 的断言。
  用户已批准该预览；iPhone 真机曝光、动态反射、功耗与帧率仍需打开 Build 28 后肉眼验收。
- iOS build number 已在 `IosBuildPipeline.cs`、序列化 `ProjectSettings.asset` 与
  `ProductArchitectureTests` 同步为 `28`。当前工作树包含多项并行中的未提交改动，因此没有伪造干净 release
  commit；本轮使用 Unity Development 真机导出作为视觉查看包，manifest 明确标记 `development: true` 和
  `sourceCommit: local-preview`。Unity Editor 日志明确记录 `Build Finished, Result: Success`，完整 Xcode 工程为
  `Builds/iOS/FidgetingAppDevelopment/`；Xcode `Release-iphoneos` arm64 编译、自动签名和 validation 成功，
  `Logs/Build28.xcresult` 以 `** BUILD SUCCEEDED **` 结束。351 MiB App 的 bundle
  `com.jiaweizhou.fidgetspinner.codex`、版本 `0.1.0 (28)` 与 manifest 一致，严格 codesign 校验通过。
- `devicectl` 已覆盖安装到 iPhone `00008130-001A00361EE0001C`；设备 inventory 回读确认
  `Fidget Spinner / 0.1.0 / 28`，证据为 `Logs/DeviceBuild28Install.json` 与
  `Logs/DeviceBuild28InstalledApps.json`。安装后自动启动被 SpringBoard 以设备锁屏拒绝，原始错误保存在
  `Logs/DeviceBuild28Launch.json`，锁状态证据为 `Logs/DeviceBuild28LockStateAfterInstall.json`；需解锁后手动
  打开或重新执行启动并补进程回读。

## 三层磁吸扇牌预览居中、正面误出圆件与层距修复（代码、场景和预览已完成；待视觉批准）

> **当前门禁：本节只修正第六款三层扇牌的预览构图与可见机构，没有改四档磁吸、阻尼、输入状态机、语义事件、Haptic recipe 或音频。真实 shipping Unity 场景预览已经生成；在用户明确批准前不构建或安装到 iPhone。**

- 共轴根节点继续位于右下轴孔，只负责真实旋转，不能改成牌面中心；Library 静态预览现在改用闭合状态的实时
  Renderer bounds 计算画面中心，因此不会再把边角轴心或不对称的 `0–90°` 扫掠包围盒当成缩略图中心。
  详情交互仍使用完整稳定扫掠包围盒，拖动时相机不会追随三片运动而跳动。
- 删除正面错误可见的 `CommonAxis_ChromeBall`、`CommonAxis_BallSeat` 和三层实心 `AxisSeat_*` 圆片；轴位保留
  真实贯穿孔、孔口 bevel 与孔内深色 `CommonAxis_ShadowSleeve`。中层和顶层的随动球缩为 `1.0 mm` 半径并
  完全收回背面机构，不再穿出 `2.5 mm` 厚的正面形成来源不明的圆圈。
- 三张实体刚性牌厚度仍为 `2.5 mm`，层中心距由 `6.25 mm` 收紧为 `3.5 mm`，对应两道一致的
  `1.0 mm` 净空；冻结几何验证确认三张牌均为封闭流形、真实轴孔净空 `0.212 mm`、层间无相交。
  场景生成器、运行时规格、验证器和接受测试读取同一 `LayerAirGap / LayerPitch`，没有保留旧层距 fallback。
- 默认 Library 展示不再使用闭合、水平的平铺姿态：`FanCardController` 仅在 Library 视觉层把中片显示为
  `30°`、外片显示为 `60°`，即从闭合位置跨过两个档位间隔；`EdcPortraitCameraFramer` 同时加入产品专属
  `45°` 画面滚转，构成自然对角线。该覆盖不写 `FanCardMagneticTrack`，进入前的真实 Position、Captured
  Detent 与速度均保留；离开 Library 后恢复真实视觉姿态，过程中不发 `SemanticEventRaised`、音频或 Haptic。
  Coordinator 先应用扇牌展示姿态再按实时 Renderer bounds 居中，因此倾斜展开后也不会重新以角落轴心取景。
- FanCard 专项 EditMode `14/14` 通过，报告 `Logs/FanCardCenterSpacing-Focused.xml`；冻结几何报告
  `Logs/FanCardCenterSpacing-GeometryValidation.log` 以 `=== VALIDATION: ALL PASS ===` 结束。GPU shipping
  预览位于 `../../Artifacts/FanCardMaterialPreview/`，其中 `fan-card-library-centered.png`、
  `fan-card-front-closed.png`、`fan-card-low.png` 和 `fan-card-side-profile.png` 的总览为
  `fan-card-center-hole-spacing-approval.png`；渲染日志为 `Logs/FanCardCenterSpacing-Capture-GPU.log`。
  当前只等待用户确认居中、轴孔表现和紧凑层距，尚未推送手机。
- 新默认姿态专项继续为 `14/14`，共享六产品相机边界回归 `6/6`，报告为
  `Logs/FanCardDefaultPreview-Focused.xml` 与 `Logs/FanCardDefaultPreview-Environment.xml`；Library、top、
  authored hero、左右斜视和低角 GPU 总览为
  `../../Artifacts/FanCardMaterialPreview/fan-card-default-two-step-45deg-approval.png`。静态 512×512 原生目录
  缩略图也由同一 `2/3` 进度与 `45°` 构图重渲染。此轮仍等待新的视觉批准，未构建或安装手机包。

## 磁吸推牌预览尺寸与详情拖动卡死修复（代码和预览已完成；待视觉批准，未推送）

> **当前门禁：磁吸推牌 Library 预览尺寸已缩小，详情页拖动失控状态机已修复并通过专项测试；真实 shipping Unity 场景的六视角预览已经生成。视觉改动必须先取得用户明确批准，当前没有构建或安装到 iPhone。**

- Library 预览占屏边界从 `0.80 × 0.56` 调整为 `0.68 × 0.48`，横向和纵向可见占用分别降低约
  `15% / 14%`；详情页 `0.86 × 0.60` 交互取景保持不变。该值来自
  `ProductFramingCatalog`，由 `EdcPortraitCameraFramer.ConfigureFraming()` 运行时接入，没有另设 native
  或场景 fallback；`EdcSliderAcceptanceTests.LibraryPreview_UsesReducedMagneticSlideOccupancy` 锁定新值。
- 卡死根因位于 `MagneticDetentTrack1D.Capturing`：旧实现进入磁吸收敛后完全忽略仍然有效的手指目标，同时
  静摩擦平衡点可能大于 `0.10 mm` 锁定误差，导致状态永久停留在 `Capturing`。现在手指在吸附过程中继续施力并
  跨过同一 `0.44 N` breakaway 阈值时会在当前 substep 立即回到 `Traveling`；捕获收敛容差由本地磁力刚度、
  capture spring 和 rail friction 推导，满足后仍把位置精确吸附到 detent、速度归零。没有新增动画回放、
  sustained Haptic、raw-input-to-`IosHaptics` 或额外语义事件。
- 新回归 `ManualPullPastCapturingDetent_ImmediatelyReturnsControlToFinger` 直接覆盖持续手势夺回控制；原有
  powered traversal、release capture、帧率一致性、正反向对称和最终精确静止继续覆盖收敛规则。EDC 专项
  EditMode `25/25` 通过，报告为 `Artifacts/EDCPreviewFreezeFixEditModeTests.xml`。当前完整 EditMode
  `220/221`；唯一失败来自并行中的 FanCard scene `LayerPitch 0.00625` 与 source-of-truth `0.00350` 不一致，
  与本次 EDC 改动无关，报告为 `Artifacts/EDCPreviewFreezeFixFullEditModeTests.xml`。
- shipping 场景原始 `1290 × 2796` Library / authored hero / top / left / right / low-angle 预览位于
  `../../../Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09/`，六视角总览为
  `ApprovalContactSheet.png`。预览已确认使用 Metal/URP 真正渲染；第一次 `-nographics` 灰屏输出已被同路径
  正确 GPU 帧覆盖，不能作为审批证据。当前等待用户确认新的 Library 尺寸与构图；真机连续慢搓、反向拉回、
  端点往返和触觉同步仍明确标记为下一版 iPhone 硬件验收项。

## 磁吸推牌跨档增强（已进入 Build 27；待真机触感验收）

- `LinearMagneticDetentProfile` 的代码默认、`ApplyHeavyDefaults()` 和 shipping ScriptableObject 已同步把三个空间边缘提示设为 Intensity `0.14→0.28`、Sharpness `0.18→0.34`，仍然每个只有 `12 ms`、同一次接近各发一次且回落至 `0.55` 以下才重置。真实 `DetentCrossed` 的两枚 finite transient 提高为 `t=0 ms: 0.82 / 0.76`、`t=30 ms: 0.38 / 0.48`；主脉冲为默认 Camera Dial 陀螺峰值的 82%，并越过 native UIKit fallback 的 Heavy 门槛。触摸时长不参与输出，停手静默，仍不存在推牌 sustained/looping player；`Breakaway` 与 `DetentCaptured` 不补额外冲击。
- `EdcSliderController -> SemanticEventRaised -> FidgetAppCoordinator -> FidgetHapticRouter.EmitMagneticSlider -> CodexIosHapticsPlayMagnetic*` 的既有语义接线不变，Profile 值原样进入 native finite Pattern，不读取旋转 Detent Lab，也不新增 raw-input-to-`IosHaptics` 调用。运行时机械参数、慢搓限速、30 ms 脉冲间隔和跨档同步视觉轻颤均未改变。
- EDC Profile/场景验收 `23/23`、磁吸语义与原生有限 Pattern 架构回归 `1/1`、完整 EditMode `213/213` 通过，报告为 `Logs/MagneticHapticAggressiveFocusedTests.xml`、`Logs/MagneticHapticAggressiveArchitectureTest.xml`、`Logs/MagneticHapticAggressiveFullEditMode.xml`；同一 `CodexIosHaptics.mm` 通过 iPhoneOS 15 Objective-C++ syntax check。
- 冻结 Build 27 发布提交 `93d52926ecb7211cfdbaf114de8ec7fe868c98bc` 已包含上述 runtime、序列化 Profile、native fallback 与验收测试；设备 inventory 回读为 `0.1.0 (27)`。覆盖安装只证明增强值已进入手机包，不替代用户对单档峰值、连续往返疲劳度、边缘提示可辨识度、系统 Haptics 开关和后台恢复的真机触感确认。

## Build 27 最终合并候选（已覆盖安装；自动启动待解锁）

> **当前发布状态：用户已于 2026-08-09 查看本节列出的真实 shipping/native 预览并明确回复“推吧”，Build 27 的 Device visual push gate 已满足。Release `0.1.0 (27)` 已按单写者流程完成 Unity 导出、Xcode 签名构建、严格 codesign 校验和 iPhone 覆盖安装；设备 inventory 已回读 Build 27。自动启动被 iPhone 锁屏明确拒绝，尚无运行进程回读，不把安装误报为已启动或真机动态验收。**

- iOS build number 已在 `Assets/Editor/IosBuildPipeline.cs`、序列化
  `ProjectSettings/ProjectSettings.asset` 与 `ProductArchitectureTests` 同步为 `27`，不会复用已安装过的
  Build 26。
- 最新 shipping FanCard 多角度帧按 top / authored hero / left / right / low / back / side 顺序合成为
  `Artifacts/Build27VisualApproval/fan-card-shipping-multi-angle.png`；同一固定完整行程取景下的
  `90° / 60° / 30° / 0°` 联系表为
  `../../Artifacts/FanCardMaterialPreview/fan-card-stable-interaction-contact-sheet.png`。
- 原生 Badge 图鉴、详情及 Locked / InProgress / Hidden / Unlocked 状态联系表为
  `Artifacts/BadgeSpecial/NativeB8/badge-native-contact-sheet.png`；长按轻弹的五角度四阶段联系表为
  `Artifacts/Appearance/LongPressActivationV1/long-press-activation-contact-v1.png`。
- Oxanium 中英文混排、成长 HUD 与 AUTO 动态证据分别为
  `../../Artifacts/TypographyRecoveryV24/oxanium-mixed-script-native.png`、
  `Artifacts/ProgressionThumbnailRecoveryV24/progression-thumbnail-hud.png` 和
  `progression-hud-auto-motion-contact-sheet.png`。
- Combo `×10 / ×30 / ×50` 分档、五角度模型平面投影和 12 帧爆发联系表分别为
  `Artifacts/ComboHaloNativePreview/combo-halo-tier-contact-sheet.png`、
  `combo-halo-angle-contact-sheet.png` 与 `combo-halo-burst-contact-sheet.png`；动态证据为
  `combo-halo-motion.mp4`。
- 当前完整 Unity EditMode 为 `213/213`，报告 `Logs/Build27EditModeTests.xml`；原生 Combo 确定性规则
  `57/57` 通过，三份 shipping Swift 在 `arm64-apple-ios15.0` 目标下通过 typecheck。第一次带 `-quit`
  的批处理只完成编译且没有 XML，未被计为测试通过。
- 冻结发布提交为 `93d52926ecb7211cfdbaf114de8ec7fe868c98bc`。Unity 日志明确记录
  `Build Finished, Result: Success`，Xcode 日志记录 `BUILD SUCCEEDED`；324 MiB Release App 的 bundle
  `com.jiaweizhou.fidgetspinner.codex`、版本 `0.1.0 (27)` 与 manifest 一致，严格 codesign 校验通过。
  证据为 `Logs/iOSBuild-Build27.log`、`Logs/XcodeBuild-Build27.log` 与 `Logs/Build27Manifest.json`。
- `devicectl` 已覆盖安装到 iPhone `00008130-001A00361EE0001C`；设备 inventory 回读
  `Fidget Spinner / 0.1.0 / 27`，证据为 `Logs/DeviceBuild27Install.json` 与
  `Logs/DeviceBuild27InstalledApps.json`。随后自动启动被 SpringBoard 以设备锁屏拒绝，原始错误保存在
  `Logs/DeviceBuild27Launch.json`；需解锁后启动并补进程回读。
- Build 27 当时的霓虹都市 V13 仍是 Editor-only 概念合成，未进入该安装包。当前工作树后来新增的候选主题运行时与
  壁纸选择器同样没有构建或安装，不能把后续代码误报为 Build 27 已推送功能。

## 霓虹都市峡谷 2.5D 场景（候选合成图已接主题切换；生产分层仍待批准）

> **当前视觉门禁：V13 候选合成图已经作为可切换主题接入当前工作树，用来验证选择器、IBL 与整体构图；它仍不是最终生产分层资源。L0–L5 独立图片、bleed、2x/3x 清晰度与真实近景差速尚未完成，且本轮没有构建或安装。必须先获得用户明确视觉批准。**

- 2026-08-08 使用现有统一峡谷图作为构图与透视参考，通过内置 ImageGen 生成第一版
  `941 × 1672` RGB 概念图：约 75% 深色粗粝岩体、青蓝主光、少量洋红、虚化远处霓虹都市、可见夜空，
  并保留与峡谷同材质的一体化底部承托。预览位于
  `Artifacts/CyberpunkEnvironmentPreview/cyber-neon-canyon-composite-v1.png`。
- 根据“近景不再使用石头”的反馈生成第二版 `941 × 1672` RGB 概念图：左右近景改为贴近镜头的深色科技建筑立面，
  底部承托改为与建筑连续的一体化屋顶／设备甲板；保留远处虚化霓虹都市、可见夜空、中央主体留白与克制的青蓝主光。
  预览位于 `Artifacts/CyberpunkEnvironmentPreview/cyber-neon-architecture-composite-v2.png`。
- 第三版设备货箱预览 `cyber-neon-equipment-stage-composite-v3.png` 因顶面相对既有承托高度发生漂移而被否决，
  不得作为生产参考。修正版同时以第二版赛博场景作为编辑目标、正式 `canyon-unified-ledgestone-v1-2x.png`
  作为几何参考，将设备模块顶面锁回原承托约 66%–67% 画面高度、原占宽和透视轮廓；科技模块替换原承托体积，
  不能作为第二个箱体叠在屋顶上。`941 × 1672` 修正预览位于
  `Artifacts/CyberpunkEnvironmentPreview/cyber-neon-height-locked-equipment-stage-v5.png`。
- 2026-08-08 将修正背景作为 `Assets/Editor` 下的预览专用纹理加载进当前 shipping
  `Assets/_Fidgeting/Scenes/ThreeBladeEDC.unity`，由真实模型、相机与图像采样环境反射输出六视角。
  V8 台面保持锁定高度，模型 Transform／Rigidbody 不改；仅用预览相机构图让可见模型底沿位于台面上方约 18 px。
  该版八角、厚倒角与浮雕台面被用户判定为偏中式传统，且模型与台面的高度关系不足，因此
  `Artifacts/CyberpunkEnvironmentUnityPreviewV8/` 仅保留为被替代的过程证据，不得作为生产参考。
- V9 将承托重做为低矮、宽幅、直线型的磁悬浮设备坞：石墨金属／碳纤维复合材质、烟熏玻璃面板、连续青色能量缝与
  底部悬浮阴影，明确移除八角轮廓、厚凸边、石雕纹样和传统装饰；着地点仍锁定在画面约 66%–67% 高度，未破坏既定场景结构。
  shipping 场景预览依据新台面可见边缘重新测量构图，使模型底沿约悬停 12 px；产品 Transform、Rigidbody 与物理参数均未修改。
  Library Hero、42° Hero、89° 顶视、左右 35° 斜视与 15° 低角预览及联系表位于
  `Artifacts/CyberpunkEnvironmentUnityPreviewV9/`，Unity batchmode 成功日志为
  `Logs/CyberpunkEnvironmentPreviewV9.log`。该 Editor 预览不改变 shipping 环境目录或 Player 资源。
- 根据用户进一步提出的“台子可以更高”，V10 保留 V9 的直线型设备坞语言和横向宽度，但把可用台面提升到画面约
  59%–61% 高度，并向下补齐与地面相连的石墨设备基座、前立面和克制青色能量缝。shipping 模型仍不修改 Transform、
  Rigidbody 或物理参数；预览相机按新台面重新测量，使模型底沿约悬停 10 px，并对六个角度分别重新对齐。
  新底图位于 `Artifacts/CyberpunkEnvironmentPreview/cyber-neon-raised-docking-plinth-v10.png`；真实场景六视角和联系表位于
  `Artifacts/CyberpunkEnvironmentUnityPreviewV10/`，成功日志为 `Logs/CyberpunkEnvironmentPreviewV10.log`。V10 仍待用户视觉批准。
- V11 保持 V10 的台面高度、宽度和透视不变，仅把基座下部改为开启中的内凹动力舱：中央约半宽的装甲向两侧／下方收回，
  露出有纵深的机械内腔与克制青白能量核心。光只向下、向前投射到地面并勾亮底缘，不把整个台体做成发光盒，也不改变主体区曝光。
  底图位于 `Artifacts/CyberpunkEnvironmentPreview/cyber-neon-open-energy-bay-v11.png`；真实 shipping 场景六视角与联系表位于
  `Artifacts/CyberpunkEnvironmentUnityPreviewV11/`，Unity batchmode 成功日志为 `Logs/CyberpunkEnvironmentPreviewV11.log`。
  模型仍由预览相机对齐在台面上方约 10 px，产品 Transform、Rigidbody、材质和物理均未修改；V11 待用户视觉批准。
- V12 针对“背景细节是否抢主体”建立明确景深层级：远城改为低对比、低饱和的模糊竖向光块，左右建筑只保留暗色大轮廓和少量边缘光，
  星空减少为稀疏星点，前景地面与动力舱光强同步降低；台面保留中等清晰度并在模型后方形成安静的深色负空间。
  同时修正此前按台面后沿对齐造成的视觉悬空：V12 改用每个 shipping 模型 Renderer 的独立可见边界，并把落点锁到台面中央透视接触平面，
  六个角度均保持约 4 px 轻触／微悬浮距离。底图位于 `Artifacts/CyberpunkEnvironmentPreview/cyber-neon-subject-focus-v12.png`；
  真实场景六视角和联系表位于 `Artifacts/CyberpunkEnvironmentUnityPreviewV12/`，成功日志为 `Logs/CyberpunkEnvironmentPreviewV12.log`。
  该修正只影响 Editor 预览相机和预览底图，产品 Transform、Rigidbody、材质、运行时场景和物理均未修改。用户判定 V12 的整体虚化让近景、远城和星空退成同一平面，
  因而不得作为生产层级参考；其中 Renderer 独立边界与台面中央接触平面的定位修正继续沿用。
- V13 回到固定 L0–L6 空间契约：双层星空保持最远小尺度星点，远城保留低亮可识别天际线，设备坞与模型构成同位移中景，
  右侧建筑和左侧最近建筑用不同遮挡尺度、暗部细节和锐利大轮廓形成两个近景层。焦点改由亮度、局部对比和遮挡控制，不再把所有背景统一模糊。
  底图位于 `Artifacts/CyberpunkEnvironmentPreview/cyber-neon-parallax-depth-v13.png`；真实 shipping 场景六视角与联系表位于
  `Artifacts/CyberpunkEnvironmentUnityPreviewV13/`，Unity batchmode 成功日志为 `Logs/CyberpunkEnvironmentPreviewV13.log`。
  固定层级、位移、构图锚点、清晰度规则、bleed 和视觉验收已记录在 `Docs/CyberpunkEnvironmentLayerSpecification.md`；V13 待用户视觉批准。
- V13 当前以单张候选资源进入主题运行时，主题入口、全局持久化、模型环境反射和基础回归已经实施；但单张图只验证整体
  构图，不能声称完成 L0/L1 星空、L2 远景、L3 真实承托、L4/L5 透明近景的生产拆分。推镜动画、各层独立 bleed、
  `1882 × 3344` 生产资产和切换后的六模型 shipping 多角度预览仍待完成；本轮原生选择器预览的批准不自动等于这些
  后续生产美术通过门禁。

## 磁吸扇牌实体拓扑与交互修复（新交互预览待用户批准，尚未推送）

> **当前门禁：实体拓扑、背面轨道与逆时针收合版本已在用户视觉批准后作为 Build 26 安装到 iPhone。用户真机反馈其闭合取景过大、展开时不跟手且 Core Motion 与拖动冲突；下述交互修正已经生成新的 shipping Unity 预览，但尚未构建或安装。必须再次取得明确视觉批准后才能推送下一版。**

- 2026-08-08 真机交互修正不改变四档位置、磁吸势阱、breakaway/capture、阻尼或 Haptic recipe：
  `FanCardSpecifications.VisualSweepBounds` 固定覆盖完整 `0–90°` 扇形行程，`EdcPortraitCameraFramer` 使用该
  root-local bounds 取景，不再随实时 Renderer AABB 改变中心和距离；详情取景由闭合牌面的 `0.84/0.78`
  改为完整行程的 `0.72/0.72`。交互 Collider 从固定顶牌迁移到共同 root，并以额外 `10 mm` 平面容差覆盖
  顶/中/底三层的全部可见扫掠区域。指针角采用逐帧解包和 `1.25×` 手势增益，重磁物理参数仍保持原值。
- `EdcDeviceMotionController` 现在在扇牌或直线推牌直接拖动期间冻结 Core Motion 相机姿态，并在松手时以当前
  设备姿态重新建立参考，避免轴心在手指下方漂移或释放瞬间跳变。FanCard 控制器执行顺序提前到相机运动之前，
  但未新增任何 raw-input-to-Haptic 调用。定向 EditMode `13/13` 通过，报告为
  `Logs/FanCardInteractionTests.xml`。随后完整 EditMode 在编译阶段被本轮范围外的
  `Assets/Tests/Editor/BadgeSystemTests.cs(164)`（`Is.AnyOf` 不受当前 NUnit 支持）阻塞，未将该并发用户改动纳入
  本轮修复。
- 新视觉证据来自 shipping 场景：`Artifacts/FanCardMaterialPreview/fan-card-motion-90.png`、
  `fan-card-motion-60.png`、`fan-card-motion-30.png`、`fan-card-motion-00.png` 使用同一固定相机包围盒和 shipping
  `0.72/0.72` 取景；联系表为 `fan-card-stable-interaction-contact-sheet.png`。顶视、Hero、左右斜视、低角和
  背面图也已由 `Logs/FanCardInteractionPreview.log` 同步重渲染。当前等待用户确认尺寸和构图，真机跟手性与
  Haptic 同步仍明确标记为待下一版硬件验收。

- 2026-08-08 按最新反馈保留三张 `2.5 mm` 刚性厚度和全部四档磁吸/Haptic 参数，只改机构层级、轨道表面与
  有符号运动方向：顶层作为固定 `0°` 参考，中层展开到 `+45°`，底层展开到 `+90°`；从完全展开收回时，
  底层在正面俯视平面严格以 `+90°` 有符号夹角逆时针回到 `0°`。运行时仍沿用同一个
  `FanCardMagneticTrack`，没有反播动画或另建视觉进度。
- 底层和中层的 `CurvedTrack_Undercut / CurvedTrack_GoldWoven` 及六枚磁点已全部移到各自刚性卡片背面，
  法线朝向背侧；轨道起点和 `+45°` 扫掠同步镜像，完整投影必须落在收缩 `0.5 mm` 的卡片圆角轮廓内。
  第一轮 GPU 预览曾发现 180° 翻面会同时镜像轨道平面、导致弧带越界并从正面露出；实现已改为直接生成
  背向三角形绕序，不再通过 Transform 翻转。新增自动化同时锁定轨道/磁点背面高度、背向法线、完整轮廓、
  顶/中/底 `0/45/90°` 层级及 `90→0` 的 `+90°` 逆时针路径。
- 最新 FanCard 定向 EditMode `11/11` 通过，报告为 `Logs/FanCardBackTrack-EditModeTests.xml`；场景构建与 GPU
  预览日志分别为 `Logs/FanCardBackTrack-BuildScene.log`、`Logs/FanCardBackTrack-Previews.log`。视觉证据位于
  `Artifacts/FanCardMaterialPreview/fan-card-motion-90.png`、`fan-card-motion-60.png`、
  `fan-card-motion-30.png`、`fan-card-motion-00.png`、`fan-card-back.png` 与 `fan-card-low.png`。四张正面帧均
  无轨道或磁点露出；背面帧可见两条内嵌轨道。四帧方向总览为
  `Artifacts/FanCardMaterialPreview/fan-card-motion-90-to-00-contact-sheet.png`。当前等待用户明确视觉批准，
  尚未构建或安装新的 iPhone 包。

- 严格执行 `card-geometry-fix-prompt.md` 的“先验证、后改网格、固定低侧角复核”流程。新增冻结验证器
  `Assets/Editor/CardGeometryValidator.cs`，实际 shipping 层名为 `BottomCard / MiddleCard / TopCard`，并按项目米制
  单位锁定 `2.500 mm` 厚度、`3.750 mm` 最小层间净空和 `0.100 mm` 最小轴间隙。验证器没有沿用原文的
  世界 X/Z AABB 相交判断，因为扇形展开本来就在平面投影上重叠；它改为沿共同轴心 Y 测量净空，并直接锁定
  `GunmetalFrame`，检查焊接后的封闭流形边、正反面三角形朝向、圆角面板越界、真实上下通孔及轴净空。
- 修复前基线完整保存在 `Logs/CardGeometryValidation-Baseline.log`：三张主体各有 `256` 条开放/非流形边；每个
  暖银正反面各有 `102` 个反向三角形和 `51` 个越界顶点，共 `21` 项失败。根因是旧放射式剖分以角落轴孔为
  起点重新采样外边界，但采样点没有与侧壁环一一对应；暖银面板的完整圆孔又大于该圆角位置可容纳的边界，
  因而生成折返三角形，低角时表现为向下卷曲的灰片和穿模。
- `FanCardSceneBuilder` 现在用同一组 `96` 段径向参数生成底环、直壁、倒角环、顶环和孔壁，顶/底盖与对应
  外环、孔环逐点连接；三张主体均为 `1152` 顶点的封闭刚性实体。暖银面不再强行放置越界的完整孔环，而是
  计算圆与圆角边界的两个真实交点，并沿面板内部圆弧生成开口缺口后再三角剖分。没有改动牌宽高厚度、层距、
  轴承/垫圈/球头、材质、灯光、四档状态机、阻尼、输入或 Haptic 参数。
- 修复后冻结报告 `Logs/CardGeometryValidation-Loop1-Final.log` 为
  `=== VALIDATION: ALL PASS ===`：三张主体全部 `open/nonmanifold=0`、`degenerate=0`，正反面均
  `inverted=0`、越界顶点 `0`，上下真实轴孔通过，主体间净空保持 `3.750 / 3.750 mm`。同一验证入口已经接入
  `FanCardAcceptanceTests.ShippingGeometryPassesTheFrozenStructuralGate`；FanCard 定向 EditMode `11/11`
  通过，报告 `Logs/FanCardGeometry-Loop1-EditModeTests.xml`。
- GPU 预览来自 shipping 场景而非概念图，位于 `Artifacts/FanCardMaterialPreview/`：
  `fan-card-top.png`、`fan-card-hero.png`、`fan-card-left.png`、`fan-card-right.png`、`fan-card-low.png`、
  `fan-card-front-closed.png`、`fan-card-side-profile.png` 与 `fan-card-bearing-closeup.png`；生成日志为
  `Logs/FanCardGeometry-Loop1-BuildCapture-GPU.log`。低侧角可见三条连续刚性侧壁与两道完整空气间隙，旧灰色
  折片已消失。Build 25 修复前低角、Loop 1 修复后同类低角和闭合侧剖另存为
  `Artifacts/FanCardGeometryValidation/before-build25-low.png`、`after-loop1-low.png` 与
  `after-loop1-side-profile.png`，六视角总览为 `after-loop1-six-view.png`，便于同机位人工复核。当前仍明确
  等待用户肉眼批准，不能以验证器绿色或测试通过替代视觉门禁。

## 全 App 统一 Badge 奖励系统（Build 32 已覆盖安装并启动；真机视觉与触感待用户验收）

> **当前发布状态：单玩具与收藏者的目录、详情、解锁通知、XP、碎片和触感已收敛到同一套 Badge v2；用户查看真实 shipping SwiftUI 的列表、详情、四状态和统一解锁通知预览后，于 2026-08-10 明确要求“这版推送到手机上”。Release `0.1.0 (32)` 已从 Build 31 冻结基线的隔离源码完成构建、签名、覆盖安装、设备版本回读与启动存活验证；Premium Display Case、Gacha、壁纸过渡和主工作区其他实验没有进入该安装包。**

- 竞品与论据、34 枚永久章/4 个循环挑战/奖励经济/迁移规则、1024 方形资产和四状态动效规范分别记录在
  `Docs/BadgeCompetitiveResearch.md`、`Docs/BadgeSystemSpecification.md`、`Docs/BadgeVisualSystem.md`；全部视觉
  方向、文件与去留结论统一列在 `Docs/BadgeVisualInventory.md`。
- 内置 ImageGen 只用于三套子方向的材料与轮廓探索：A `Arc Reactor Core`、B `Tactical Prism Insignia`、
  C `Forged Relic`。三张 1254 × 1254 sRGB 概念板位于 `Artifacts/BadgeSpecial/Concepts/`；它们不是生产
  资产，正式 Badge 必须重新绘制可控 SVG frame/core/glyph 并导出 1024 × 1024 透明 PNG。
- 用户随后选择 B 的棱镜游戏感，但要求降低厚重黑钢、尖刺和装甲感，并适当增加圆角与轻量质感。新增
  `direction-b2-soft-rounded.png` 与 `direction-b3-balanced-rounded.png`：B2 是更浅、更珠宝化的边界样本；
  B3 保留近黑背景和游戏等级对比，只把框架减薄约 20%、缩短尖刺并使用圆角端点；它随后因复杂和语义不足被否决。
  用户继续指出 B3 仍过度复杂且图形没有对应真实成就；因此新增完全矢量的
  `direction-b4-semantic-lightweight.svg/.png`，用轻量框架、单一类别锚点和 Oxanium 动态里程碑 Token 展示
  `100K`、`×50`、`3.5 KM/H`、`10h`、Perfect、`12W`、`LV.100`、`25` 八个真实样本。根据后续反馈，B4 的
  所有数字已统一为同一 Oxanium 720 字号和中心基线，`KM/H`、`LV` 使用同一固定第二行槽位；不再按字符
  数量逐枚放大、缩小或改变位置。
- 2026-08-08 用户明确确认 Chain Reactor 的圆角连结环风格并要求迁移到全部 icon。新增统一的十类别母版
  `badge-category-glyphs-monoline.svg/.png`，以及 21 枚单玩具、13 枚收藏者、4 枚循环挑战、1 枚周期总章、
  1 枚 Legacy 共 40 枚独立矢量 glyph。源文件和 1024 × 1024 透明 sRGB PNG 位于
  `Artifacts/BadgeSpecial/VectorGlyphs/`；三张 1:1 全量检查图为 `badge-glyph-catalog-toy.png`、
  `badge-glyph-catalog-collector.png`、`badge-glyph-catalog-challenge.png`。生成器和 manifest 分别为
  `Tools/BadgeAssetGenerator/generate_badge_glyphs.py` 与 `badge-glyph-manifest.json`。静态检查确认 40/40 SVG
  XML 有效、40/40 PNG 为 1024 方形、透明并带 sRGB profile。
- 随后的全量图鉴视觉复核中，用户明确否决该批次：直接渐变描边没有实体灯管管径，部分复杂 glyph 是
  不成立的生硬拼接，并且图鉴把里程碑数字移出了 Badge。上述 40 枚资产即使静态格式检查通过，也只能
  作为 rejected iteration，不能进入 iOS Bundle 或替换现有占位图。
- 新增 `direction-b5-physical-light-tube.svg/.png` 八枚修正样章。灯管使用暗侧管壁、实体色管身、偏移高光、
  外部辉光和圆形端帽；两个 Chain Reactor 闭环只通过绘制层级产生前后遮挡，没有悬空补段。`100K`、
  `×50`、`3.5 KM/H`、`10h`、`12W`、`LV 100`、`25` 已恢复到 Badge 内，使用统一 Oxanium 主字号与基线；
  技巧章使用同一位置的 `PERFECT` 语义 Token。B5 后续已被否决，未扩展全量或接入运行时。
- 根据用户提供的 Chain Reactor 参考，B5.1 将强霓虹材质改为雾紫主导的漫反射管身、低透明色晕、模糊
  单侧高光和短距离微投影；雾蓝与暖雾金只保留低饱和类别差异。三套管身渐变改用统一画布坐标，避免
  水平灯管因零高度 object bounding box 丢失材质。数字、物理闭环和遮挡规则保持不变；本版后续由 B8 取代。
- B5.2 将所有灯管图形限制在统一 `128 × 80` 安全区并锁定中心 `(140, 88)`；图形与内框保留四向间距，
  icon + Token 总包围盒重新对齐内框中心。动力箭头改为曲线动势和独立箭头管，节奏改为连续 Bézier 波形，
  Perfect 使用柔和闪光轮廓，精通六边核心增加转角过渡。所有数字统一降至 58 pt，`100K` 仍保留真实双侧
  留白；技巧语义 Token 固定 38 pt。B5.2 后续已被否决并由 B8 取代，未进入运行时。
- 用户随后要求改为其提供的黑白符号页风格。新增 `direction-b6-neo-organic-symbols.svg/.png`：八枚原创符号
  使用雾白实形、正负空间、旋转/镜像构成、有机曲面、柔性尖角、克制 bloom 和细扫描纹理；不复制参考图
  的九枚现成符号。B6.1 进一步避免同一花瓣结构重复：Speed 使用三片动势与双轨道，Rhythm 使用有负形
  核心的波动网格，Mastery 使用三重旋转完成体，Collection 使用六片卡片式光圈。统一 `128 × 80` 安全区、
  58 pt 数字、38 pt 技巧 Token 与真实成就映射保持不变。B6.1 后续已被否决，未扩展全量或接入运行时。
- 用户明确指出 B6.1 即使参考仍画偏：外框与数字挤占 icon 面积，符号不够大、不够直接。新增 ImageGen
  风格母版 `direction-b7-reference-faithful-symbols.png`，严格回到无框 3×3 网格、62%–68% 光学占比、等距
  四向留白、温白实形、黑底、强正负空间、轻 bloom 和织物扫描纹理。九枚分别探索 Pulse、Combo、Speed、
  Focus、Perfect、Rhythm、Mastery、Collection、Challenge 的原创构成；无文字、数字、外框或伪 UI。该 PNG
  只用于方向确认，不能进入 Bundle；确认后才人工描 SVG，并由 native Badge 组件恢复独立数字层。
- 用户随后指定新的 Y2K Chrome Shapes 图片作为参考母版，要求保留 B7 的漫反射光感并加入金属效果。
  新增 `direction-b8-diffuse-chrome-symbols.png`：九枚原创符号使用银色镜面高光、石墨暗反射、圆润倒角、
  尖瓣/星芒/轨道/旋转结构和克制的雾白 bloom；继续使用无框 3×3 网格、相同光学占比、等距四向留白
  与黑色织物背景。B8 是 ImageGen 材质母版，不是生产资产；确认后才人工描成 SVG 并分离 chrome base、
  dark reflection、specular、diffuse bloom 四层，数字仍由 native Badge 组件独立叠加。
- 用户已明确回复 B8 “可以”，并追加四项生产约束：所有金属倒角圆润连续；构图使用轴对称、中心对称或
  严格旋转对称；调色限定冷银/石墨黑/低饱和冷白；整体保持科技冷感与肃穆感。该确认只批准视觉母版，
  不等于 40 枚正式资产、Badge v2、native 页面或解锁动效已集成。下一阶段是按该规则人工重绘全量 SVG/
  材质，并从真实 native 组件输出含数字的图鉴与状态截图。
- 新增 `direction-b8-typography-lockup.svg/.png` 作为文字组合预览。九格直接使用批准的 B8 图形母版，并将
  icon viewport、主 Token、单位、英文标题和中文条件分别锁在固定中心线与基线。主 Token 统一 Oxanium
  720 / 40 pt，`PERFECT` 不单独缩小；单位固定 14 pt 独立行，`KM/H`、`LV`、`CYCLE` 不推动标题；标题
  16 pt、条件 13 pt。该图只验证排版，不是 shipping native 截图；随后已按用户要求收敛为两行生产排版。
- 新增 `direction-b8-rarity-containers.svg/.png`，把批准的 B8 icon 与文字层装入统一黑色皮革内底和冷银金属
  包边。Ignition 固定为单层圆角矩形、Overdrive 为双层竖向椭圆、Apex 为圆肩软盾牌、Singularity 为双层
  仪式盾牌并增加克制冷白雾光；稀有度不再只靠换色。八枚样章的 icon、Token、单位、标题、条件和等级均
  被容器完整包住，统一几何中心线、固定文本基线以及顶部/左右至少 24 pt 安全间距。嵌入 B8 位图使用 screen
  合成消除了原图黑色裁切方块，皮革纹理也已收敛为不规则低对比细纹。该图仍是组合预览而非 native 截图，
  用户随后批准短版母版，并继续提出 B8.1 原生尺寸与材质修订。
- 第一版容器被复核为纵向过长，且九宫格源图中每枚符号在各自 cell 内并不处于相同可见中心。修正版将
  外框由 `250 × 478` 压缩为 `250 × 320`，纵向减少约 33%；同时测量每枚 icon 的亮部轮廓包围盒，用独立
  viewBox 偏移把八枚可见中心统一映射到固定 `156 × 156` icon slot 中心，而不是继续复用未经校正的 cell
  原点。根据后续“最多两行”反馈，每枚章只保留核心 Token 和一个短名称：单位并入 Token 同行，等级名由
  外框形状表达，中文条件、详细标题和等级文字全部移除。两条文字基线固定为 `226 / 260`；用户已于
  2026-08-08 明确回复“可以”，该修正版正式通过母版视觉门禁；下一步按此规则制作
  全量生产 SVG/材质并接入真实 native Badge 页面。
- 被否决的 B8.1 曾接入真实 native Badge 组件：`ProductBadgeLayoutTokens` 将最近目标、两列图鉴、详情和分享卡徽章宽度
  统一为 `54 / 118 / 154 / 122 pt`；`ProductBadgeShellShape` 使用连续肩部曲线与圆钝盾尖；包边由外部暗沿、
  冷银主带、偏置高光、内侧暗边和内层铬线共同构成立体截面。`ProductBadgeLeatherTexture` 改为高密度微孔
  加极短随机压纹，避免规则横线或长划痕。运行时文字继续只保留 Token 与短名称两行，均在统一中心槽内。
- B8.2 使用用户原参考作为唯一母版，并由内置 ImageGen 生成材质纠偏图
  `Artifacts/BadgeSpecial/Concepts/direction-b8-reference-recovery.png`。该位图只约束液态银体积、柔光、容器层级
  和比例，不直接进入 Bundle。生产 SVG 已把此前未实际使用的 `chrome` 渐变接到 tube/plate/orb，并加入暗侧
  截面、窄白高光与柔光；Pulse、Chain、Redline、Focus、Perfect、Rhythm、Mastery、Vault 八个关键语义按参考
  重画。原生 icon viewport 从 `0.51` 提升到 `0.64`，删除第三道内圈，`KM/H` 改为与主数字同基线的小单位。
- 用户继续指出不同轮廓的锐利度、圆润度、双层包边宽度和层间距不一致。B8.2 现已删除通过 `scaleEffect`
  缩放得到的伪内框，`ProductBadgeShellShape` 改为真实 `InsettableShape`；所有等级固定使用一条宽外铬边、一个
  等距留缝和一条细内线，三项尺寸分别为容器宽度的 `3.1% / 1.9% / 0.8%`，不再按等级增删层数。Apex 与
  Singularity 使用完全相同的连续圆肩盾牌曲线和圆钝盾尖；圆角矩形的角半径也统一收敛到宽度的 `20.5%`。
  shipping SwiftUI 复核图已覆盖输出到 `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png`，当前仍等待
  本轮边缘与包边的明确视觉批准。用户随后明确评价该版“好丑”，因此该视觉方案已被否决，实验截图另存为
  `Artifacts/BadgeSpecial/NativeB8/badge-native-rim-experiment-rejected.png`，不得作为批准候选。
- 新增 B8.3 `Artifacts/BadgeSpecial/Concepts/direction-b8-3-milled-rim.png`。该图由内置 ImageGen 严格编辑原始
  2×4 母版，只探索一个连续铣削金属外框、固定净间距、单条内侧 keyline 与更可辨的近黑皮革；保留八枚
  成就语义、数字与两行层级。它当前只作为视觉方向图，尚未精确转译为 SwiftUI/生产 SVG。必须先获得用户
  对该方向的明确视觉批准，再重绘并输出新的真实原生图鉴、详情、状态与分享截图。
- 用户确认 B8.3 的材质质感后，将轮廓规范收敛为仅两种：圆角矩形与紧凑盾牌；全部 artwork、thumbnail 与
  分享画布固定为 `1:1`，容器也进入相同正方形安全区。内置 ImageGen 生成的 B8.4 方形对照图位于
  `Artifacts/BadgeSpecial/Concepts/direction-b8-4-two-shapes-square.png`，尺寸 1254 × 1254、sRGB。椭圆、胶囊、
  纵向长矩形和长盾牌不得进入后续生产转译。该图当前等待明确视觉批准，尚未作为真实原生页面实现。
- 用户随后提供 `export.zip`，其中 10 张抽象黑白图形已解压到 `Artifacts/BadgeSpecial/References/export-icons/`；
  它们只作为负形星核、连续轨道、闭合回环、切角和彗星动势的构成灵感。内置 ImageGen 依据 B8.4 母版生成
  两张 B8.5 扩展板：`direction-b8-5-motion-focus-options.png` 覆盖 8 个动力/技巧/Combo/专注成就，
  `direction-b8-5-collector-challenge-options.png` 覆盖 8 个节奏/探索/精通/收藏/周期挑战；两图均为
  1254 × 1254、sRGB。16 个 option 都映射现有 Badge 定义，没有借扩图形之名新增无规则、无奖励的成就。
  当前仍需用户选择视觉方案；批准后才重绘 1024 透明 SVG/PNG 并接入真实原生页面。
- B8.6 已把尺寸规则从概念描述落实为确定性生产流程。`normalize_badge_artwork.py` 测量每张 PNG 中
  `alpha >= 16` 的可见包围盒，以 1024 画布的 74%（目标 758 px）作为最长边，使用同一 X/Y 比例缩放并把
  可见中心映射到 `(512, 512)`；重复执行前后文件哈希一致。`validate_b8_assets.py` 和
  `BadgeSystemTests.ShippingArtworkIsCompleteSquareTransparentSrgbAndTextFree` 同时锁定最长边、中心误差、透明
  sRGB、1:1 尺寸，并禁止生产 SVG 使用 `<ellipse>`，避免正圆被拉成椭圆。
- shipping `ProductBadgeLayoutTokens` 固定三列、20 pt 水平边距、14 pt 列间距、16 pt 行距和 56% 正方形
  icon slot；`catalogCellWidth` 按可用宽度计算，所以 375 pt 屏幕每格为 `(375 - 40 - 28) / 3 = 102.33 pt`。
  `ProductRarityBadge` 固定 `.aspectRatio(1, contentMode: .fit)`，Ignition/Overdrive 共用圆角矩形，
  Apex/Singularity 共用紧凑盾牌，不再出现胶囊或椭圆容器。
- 当前 shipping 原生预览为 `Artifacts/BadgeSpecial/NativeB8/badge-native-catalog.png` 与
  `badge-native-reference.png`，生产图形总览为 `Artifacts/BadgeSpecial/ProductionB8/badge-b8-catalog-toy.png`。
  iPhoneOS 15 Swift typecheck 与 40 枚静态资产验证通过；本轮 Unity 定向回归因同一工程已有 Unity 实例打开而
  未能启动，必须在工程空闲后复跑，不能沿用旧的 `42/42` 结果冒充本轮通过。
- 用户指出 B8.6 首张原生图鉴虽然尺寸正确，却重新使用了旧的扁平生产 glyph。B8.7 已将
  `direction-b8-5-motion-focus-options.png` 锁定为唯一图形母版：代表样章改为 `1K / 10K / SPEED / ENDURE /
  ×20 / ×50 / 30M / 2H`，分别使用三瓣漩涡、双星、负形彗星、正圆轨道、双圆环、五节点圆环、眼形和月牙。
  ImageGen 隔离出的无文字材质参考保存在 `Artifacts/BadgeSpecial/References/B85LiquidChrome/`，只用于人工
  重绘校准，不直接进入 Bundle。
- `generate_b8_badges.py` 已把全量 40 枚资产的粗黑 cartoon outline 收敛为平滑液态银、石墨侧面、窄柔白
  高光与克制 bloom，并为上述八枚语义独立重画 SVG。当前真实三列确认图为
  `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png`（`B8.7 · B8.5 VISUAL`）；40/40 SVG/PNG 已通过
  1024 方形、透明、sRGB、无文字、最长边等比适配和禁用 `<ellipse>` 的静态验证。尚未推送真机。
- B8.8 不生成或修改 icon 造型，只重构容器和状态。`ProductBadgeShellShape` 删除按 grade 切换的圆角矩形与
  盾牌，改为一个六顶点、连续二次曲线圆角的 `roundedHexagonPath`；所有 grade 复用同一 1:1 几何。
  `Unlocked` 使用高亮冷银外沿、完整 artwork、柔白 glow 与可辨皮革，`Locked / InProgress / Hidden` 使用
  黑灰外沿、深黑内底、24% 低亮 artwork 和低对比文字；进行中只保留灰色细进度线。内部 Token 高度、短名
  字号和整体偏移已重新压入六边形安全区。
- B8.8 真实 shipping SwiftUI 图鉴为 `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png`，四状态对照为
  `badge-native-states.png`；生产 manifest 的唯一 `frameShapes` 值为 `roundedHexagon`。iPhoneOS Swift 编译与
  40/40 静态资产验证在本轮最终截图后通过，本次改动文件的 `git diff --check` 通过。Unity Badge 定向回归
  因同一工程已有 Unity 实例打开而无法启动，必须在工程空闲后复跑；真机安装仍被视觉批准门禁阻止。
- B8.9 将 `roundedHexagonPath` 的左右中点设为不参与圆角插值的精确顶点，仅四个斜角保留 16% 连续圆角；
  `generate_b8_badges.py` 使用相同顶点与曲线规则，manifest 唯一轮廓更新为 `pointedRoundedHexagon`。
  `ProductBadgeLayoutTokens.iconSlotFraction` 从 `0.56` 调整为 `0.46`，生产 contact sheet 同步使用 46% slot。
  最新 shipping SwiftUI 截图覆盖输出至 `badge-native-reference.png` 与 `badge-native-states.png`；当前仍未安装真机。
- B8.10 覆盖 B8.9 的横向尖角轮廓：六边形顶点顺序旋转为顶部尖端、右上、右下、底部尖端、左下、左上；
  所有六个顶点恢复统一 16% 连续圆角，因此上下端既保持方向性又不出现硬切锐角。manifest 唯一轮廓更新为
  `verticalPointRoundedHexagon`，46% icon slot、三列布局、液态银图形与明暗状态均保持不变。最新 shipping
  SwiftUI 已重新输出 `badge-native-reference.png` 与 `badge-native-states.png`，40/40 资源检查和 iPhoneOS 15
  typecheck 通过；当前仍未安装真机，继续等待本轮视觉批准。
- B8.11 将 `ProductRarityBadge` 拆为严格 1:1 的金属六边形和外部 metadata 两层：内部 VStack 删除短名和
  `InProgress` 进度条，只保留 icon 与核心 Token；外部固定显示里程碑短名，并在其下方显示 72% 卡片宽度的
  进度条。非进行中状态保留透明等高槽，确保三列名称与行高一致。最近目标、图鉴、详情和分享卡继续复用
  同一组件，因此不会出现某个入口仍把名称或进度塞回六边形的分叉实现；当前仍未安装真机。
- 用户指出 `SPEED` 双翼图形上下不对称。`speed_comet()` 已改为只维护一组上翼 Bézier 控制点，下翼在生成时
  把每个坐标计算为 `y = 160 - y` 并展开为最终路径，避免 SVG transform 对内部阴影造成视觉偏移；中央负形星
  也从偏右位置回到 `(80,80)`。验证器新增上下翼最终坐标与中心坐标断言，避免后续资产重生成时退回两条
  独立、歪斜的曲线。最新 shipping
  SwiftUI 已重新覆盖 `badge-native-reference.png` 与 `badge-native-states.png`；40/40 资源验证、iPhoneOS 15
  typecheck 和本次涉及文件的 `git diff --check` 均通过，当前仍等待视觉批准，尚未安装真机。
- B8.12 针对用户指出的扁平、金属弱、光晕消失和皮革缺失完成全链路修复。`generate_b8_badges.py` 的 Tube
  统一使用 bloom/dark/body/shade/light 五层管径，Plate 新增 `plateDepth` 暗侧厚度并提高冷银反差与窄高光；
  `ProductRarityBadge` 对已解锁 artwork 增加独立的模糊 screen bloom 和双层白/冷色外晕。内底 Canvas 改为
  118–290 个微型不规则 pebble、细孔和短折痕，替代不可见细线或稀疏椭圆。新增
  `Tools/BadgeAssetGenerator/build_b8_assets.sh`，`capture.sh` 每次截图前强制执行 40 SVG 生成、40 PNG 重渲染、
  74% 归一化和验证，关闭 SVG/PNG 版本漂移入口。最新真实截图为 `badge-native-reference.png`、
  `badge-native-detail.png` 与 `badge-native-states.png`；40/40 资源验证、iPhoneOS 15 typecheck、两条 shell
  脚本语法检查和本轮文件 `git diff --check` 均通过。`Temp/UnityLockfile` 仍存在，因此未强退用户 Editor、
  未冒充本轮 Unity EditMode 已重跑；仍未安装真机。
- B8.13 只收紧排版，不改动 B8.12 已确立的图形、金属、光晕、皮革、六边形或进度条。`ProductRarityBadge`
  把 Icon + Token 固定为 Badge 宽度 64% 高的组，并显式 `.position(x: width * 0.5, y: width * 0.5)`
  对齐几何中心；主 Token 从 14.0% 缩至 12.4%，单位从 5.6% 缩至 4.8%，外部名称改为
  9.5 pt Oxanium Bold 与 13 pt 固定居中槽。图鉴、详情、状态和分享仍共用同一个组件；真机门禁保持不变。
  `capture.sh` 现会在构建目录中快照三个 shipping Swift 源文件，确保同一套截图使用完全一致的源码时点。本轮已从
  实际组件重拍 `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png`、`badge-native-detail.png` 和
  `badge-native-states.png`；iPhoneOS 15 Swift typecheck、40/40 SVG/PNG 资产验证、两条 shell 语法检查与定向
  `git diff --check` 均通过。`Temp/UnityLockfile` 仍存在，因此未强退用户 Editor、未声称 Unity EditMode 已重跑。
- 2026-08-18 B9.2 按用户提供的 `CHALLENGE + LEGACY` 母版完成归一化逐像素复核，并明确覆盖 B9.0/B9.1
  的松散通用六边形与偏扁平图标方向；B9.0/B9.1 只保留为否决历史，不再是批准候选。shipping
  `ProductRarityBadge` 现在统一为尖端朝上的圆角六边形：外层为宽幅冷色
  缎面金属框，中层为连续深色斜面，内层为带微孔／短折痕的下沉黑色皮革；40 枚章内只绘制居中的独立图标。
  生产 SVG 图标统一使用珍珠银面、深薰衣草色侧壁、宽软 bevel、左上 softbox 窄高光和克制投影，禁止随机镜面
  渐变或无物理依据的连接。等级只在外框加入薄荷、冰蓝、淡紫或中性银的低饱和偏光，不改变容器几何。
  短名与里程碑数字合并为章外最多两行，进度条继续在文字下方；三列布局与 1:1 artwork 规则不变。
  `Tools/BadgeAssetGenerator/build_b8_assets.sh` 已重建全部 40 枚 SVG/PNG；验证结果为 40/40、1024 × 1024、
  透明、sRGB、无烘焙文字且最长边等比适配。`Tools/BadgeNativePreview/capture.sh` 通过真实 shipping SwiftUI
  重新生成八个分类页、全量缩略图、详情、四状态、解锁和 1080 × 1080 分享卡；核心证据为
  `Artifacts/BadgeSpecial/NativeB8/badge-native-reference.png`、`badge-native-states.png`、
  `badge-native-thumbnailChallengeLegacy.png` 与 `badge-thumbnails-all.png`。iPhoneOS Swift 编译随截图流程通过，
  `NativeUiUsesReusableProductComponentLibrary` 定向 EditMode 回归 1/1 通过，报告为
  `Artifacts/BadgeSpecial/B92ProductBadgeFocusedTests.xml`。母版／shipping Chain 归一化对照位于
  `Artifacts/BadgeSpecial/B92ReferenceAudit/final-shipping/chain-pixel-comparison.png`：外框亮面宽度均为 `9.96%`，
  shipping 图标中心偏差为横向 `-0.2%`、纵向 `+0.1%`，图标占比为 `30.86% × 31.05%`，保留比母版
  `32.42% × 33.79%` 略大的安全留白。生成／截图脚本语法、Python 编译与目标文件 `git diff --check` 通过。
  当前视觉批准待确认，未构建或推送手机。
- 2026-08-17 已把当前 40 枚 shipping Badge 按真实 native 三列组件整理为可直接查看的 thumbnail 图鉴：
  `Artifacts/BadgeSpecial/NativeB8/badge-thumbnails-toy.png`（单玩具 21 枚）、
  `badge-thumbnails-collector.png`（收藏者 13 枚）、`badge-thumbnails-challenge-legacy.png`（挑战 5 枚 +
  Legacy 1 枚）以及 `badge-thumbnails-all.png`（全量纵向总览）。八张分类页由
  `ProductBadgeThumbnailCategoryPage` 读取同一个 `badge-b8-manifest.json` 并复用 shipping
  `ProductRarityBadge` 生成，不是概念稿；`capture.sh` 已覆盖全部分类并为 7 枚的收藏页保留完整第三行。
  40/40 SVG/PNG 再验证为透明 1024 × 1024、sRGB、无烘焙文字且最长边等比适配；截图流程实跑成功，
  shell 语法检查和涉及文件的 `git diff --check` 通过。当前视觉批准待确认，未推送手机。
- 40 枚生产 glyph 已由 `Tools/BadgeAssetGenerator/validate_b8_assets.py` 重新验证为 40/40 SVG/透明 1024 PNG、
  sRGB、无烘焙文字。`Tools/BadgeNativePreview/capture.sh` 直接编译当前 shipping SwiftUI，输出真实图鉴、详情、
  四状态、分享界面、八枚参考对照和精确 1080 × 1080 卡片至 `Artifacts/BadgeSpecial/NativeB8/`；其中
  `badge-native-reference.png` 是本轮直接对照用户母版的实际原生截图。iPhoneOS 15 Swift typecheck
  通过，Badge/进度/原生组件定向 EditMode 回归 `42/42` 通过，报告为
  `Logs/BadgeSystemTargetedRegressionTests.xml`。
- 2026-08-10 完成运行时收敛：`BadgeRewardLedger` 作为单玩具与收藏者共享的唯一奖励账本，以稳定 claim key
  幂等发放 XP 与全局徽记碎片，并把真实 `rewardClaimed`、`unlockedAtUtc` 和 `shardBalance` 发布给原生层。
  `SpinnerProgressionRuntime` 与 `CollectorProgressionRuntime` 都直接评估 `BadgeCatalogV2`；旧 Collector
  achievement 只作为迁移输入并调用 `MarkClaimed`，不会重复发奖励。解锁后由 coordinator 发送
  `BadgeUnlocked` 语义事件，再进入独立三脉冲 Haptic recipe，没有新增 raw-input-to-`IosHaptics` 调用。
- 原生层已删除 `ProgressionAchievementDetail`、`CollectorAchievementDetail`、独立
  `CollectorUnlockOverlay` 和两套 seen queue。单玩具与收藏者统一使用 `ProductBadgeDetail`、
  `ProductBadgeUnlockEvent`、`ProductBadgeUnlockBanner` 与 `fidgeting.badges.seen.v2.<context>`；解锁 Banner
  直接复用图鉴/详情的 `ProductRarityBadge`，同时显示实际 XP 与碎片，不再用通用星标或奖杯代替。
- 最新真实 shipping SwiftUI 预览为 `Artifacts/BadgeSpecial/NativeB8/badge-native-contact-sheet.png`、
  `badge-native-detail.png` 与 `badge-native-unlock.png`。截图流程重新生成并验证 40/40 正式 SVG/PNG，随后编译
  当前 shipping SwiftUI 并从 iPhone 17 Pro Simulator 截图；详情页、图鉴、状态和通知显示同一枚 `100K PULSE`。
- 隔离 Unity EditMode 专项 `BadgeSystemTests` 最终为 `9/9` 通过，报告为
  `Artifacts/BadgeSpecial/BadgeSystemEditModeTests.xml`；覆盖 34 枚永久章与 6 枚特殊章、阈值/奖励、JSON v2、
  40 枚正式图稿、账本持久化与重复领取防护、单玩具与收藏者运行时 XP/碎片发放，以及收藏者重启后的幂等性。
  当前打开的主 Unity Editor 未被关闭或修改。本轮统一 Badge 架构与共享原生组件两个专项分别 `1/1` 通过，报告为
  `Artifacts/BadgeSpecial/BadgeArchitectureFocusedTests.xml` 与 `BadgeNativeComponentFocusedTests.xml`，锁定共享账本、
  统一组件、seen key、真实皮革纹理和语义触感。同步隔离依赖后的完整 `ProductArchitectureTests` 实跑 `37/38`；
  唯一失败是本轮之外的 DEBUG Haptic 设置预览为了展示而写入 `Camera Dial`，与旧测试“整个 Swift 文件不得出现该
  字符串”的宽泛断言冲突。该失败不是 Badge 回归，但在旧测试收窄到 shipping 范围前也不能把完整架构组写成全绿。
- `SpinnerProgressionTests` 首轮实跑 `35/36`；唯一失败是旧断言仍要求成长图鉴第一栏为“成就”，而统一信息架构已
  将其改为“等级”并把 `Badge` 独立为第二栏。断言同步后，Build 32 隔离源码复跑为 `36/36`；同一冻结源码的
  `BadgeSystemTests` 为 `9/9`，shipping SwiftUI 也通过 iPhoneOS `swiftc` type-check。报告归档在
  `Logs/Build32Evidence/BadgeSystemTests.xml` 与 `SpinnerProgressionTests.xml`。
- 周期挑战的目录与 claim key 已纳入同一模型，但挑战推进 coordinator 仍未接入 shipping runtime；在该入口真正
  接线并补齐确定性测试前继续保持未开放，不能把静态定义误报为已集成。
- Build 32 发布源为隔离提交 `ce6b4f742d029c3e75ef06aead9837535e62324a`；Manifest、签名 App Info、安装、启动、
  设备 App 清单与启动后进程存活证据归档在 `Logs/Build32Evidence/`。设备回读为
  `com.jiaweizhou.fidgetspinner.codex`、`0.1.0 (32)`，启动后完整进程列表仍包含 `FidgetSpinner`。自动化和启动
  证据不替代用户在 iPhone 上对通知安全区、动态字体、VoiceOver、Badge 视觉以及 Taptic 手感的最终验收。

## Build 25 磁吸扇牌第六分页恢复（当前 Release，已安装启动）

> **当前发布状态：Build 24 已证明六个 Unity 场景都进入 App，但 iOS 原生模型库只显示前五款。缺失入口已修复；用户已于 2026-08-08 明确确认 shipping native 第六分页预览。Release `0.1.0 (25)` 已从隔离、不可变源码完成构建、签名、覆盖安装并启动到 iPhone；仍待用户在真机模型库和详情页肉眼确认。**

- 根因是 `SpinnerModel` 已定义 `magneticFanCard`，C# `ProductCatalog` 与 iOS Build Settings 也均包含六款，
  但原生 `SpinnerModel.shippingCases` 数组只列到 `.magneticSlideTile`。因此包、场景和控制器均存在，模型库
  的 `TabView`、收藏列表与选择入口却统一把第六款过滤掉。
- `shippingCases` 现显式追加 `.magneticFanCard`；新增架构断言锁定最后两项必须是
  `.magneticSlideTile, .magneticFanCard`，防止以后只保留 enum case 却再次漏掉 shipping 页面。专项 EditMode
  `1/1` 通过，报告为 `Logs/FanCardNativeCatalogFocused.xml`；三个 shipping Swift 文件的
  `arm64-apple-ios15.0-simulator` 全量 typecheck 通过。
- 直接编译当前 shipping `FidgetProductUIComponents.swift`、`FidgetComboHalo.swift` 与
  `CodexSwiftUIOverlay.swift` 后，叠加已批准的 Unity FanCard Hero 帧生成原生第六分页预览：
  `Artifacts/FanCardNativeCatalogPreview/fan-card-sixth-page.png`。预览明确显示第六个 Page Control 圆点、
  `磁吸扇牌` 标题与 `进入 磁吸扇牌` 操作；用户已明确确认该预览。
- Build 25 候选从 Build 24 已验证提交创建隔离 worktree，只应用第六分页、回归断言及 build number 同步，
  固化为 detached commit `4035ba84c582be1ef054346f219b79ceef1c7eb6`。完整 EditMode `194/194`
  通过，报告为 `Logs/Build25EditModeTests.xml`；测试产生的 URP/Standalone define 序列化副作用已恢复，
  Unity 导出前工作树保持干净。
- Unity 导出明确 `Build Finished, Result: Success`，manifest 回读 bundle
  `com.jiaweizhou.fidgetspinner.codex`、version `0.1.0`、build `25`、`development=false`、上述 commit 和六个
  shipping 场景，证据为 `Logs/iOSBuild-FanCardNativeCatalog-B25.log`。首次 Xcode 编译因磁盘耗尽中止；确认
  无活动进程后仅删除可重建的旧 Build 24 临时 worktree，释放约 12 GB，再从同一 manifest 增量续编，最终
  `BUILD SUCCEEDED`。319 MiB App 的 `codesign --verify --deep --strict` 通过。
- `devicectl` 已覆盖安装并启动同一 bundle 到 iPhone `00008130-001A00361EE0001C`；设备 inventory 回读
  `Fidget Spinner / 0.1.0 / 25`，运行进程 PID 20291。证据为 `Logs/DeviceBuild25InstalledApps.json` 与
  `Logs/DeviceBuild25Processes.json`。安装和启动只证明部署成功，仍需用户确认第六个圆点、进入按钮、三层
  刚性厚度、无穿模、四档吸附与 Haptic 同步。

## Build 24 三层刚性扇牌真机发布（上一版 Release）

> **发布结果：用户查看八视角 shipping Unity 预览后明确要求推送；Release `0.1.0 (24)` 已从隔离、不可变源码完成 Unity 导出、Xcode Release 签名构建并覆盖安装到 iPhone。解锁后已由 `devicectl` 成功启动并回读运行进程；随后用户确认原生模型库仍没有第六款入口，根因与 Build 25 修复记录见上方。**

- 三层卡片刚性实体、`2.5 mm` 厚度、`3.75 mm` 层间净空、真实共轴通孔及正反贴面详见本文件末尾
  “扇牌尺寸与厚度校正”。用户已明确批准低角、闭合侧剖、顶视等 shipping Unity 预览，设备视觉门禁满足。
- 发布前完整 EditMode `194/194` 通过，报告为 `Logs/Build24EditModeTests.xml`。iOS build number 的运行时
  设置、序列化 `ProjectSettings` 和架构验收测试均同步为 `24`，没有继续复用 Build 23。
- 因主工作区包含并发任务文件，本次没有清理、stash 或提交用户工作区；批准的 shipping 源码被复制到隔离
  worktree 并固化为 detached commit `1a0d2119df49cbafbf0a0c68d3db5df13fb24832`。两轮预导出分别捕获并
  拒绝了 Unity 对 build number 与 iOS player define 的确定性序列化漂移，第三轮导出前后工作树完全一致。
- manifest 回读为 bundle `com.jiaweizhou.fidgetspinner.codex`、version `0.1.0`、build `24`、
  `development=false`、六个正式场景及上述 source commit。Unity 明确 `Build Finished, Result: Success`，
  Xcode 明确 `BUILD SUCCEEDED`，319 MiB App 的严格 `codesign --verify --deep --strict` 通过；Unity 导出证据为
  `Logs/iOSBuild-FanCardRigidSlabs-B24.log`。
- `devicectl` 已把同一 bundle 覆盖安装到 iPhone `00008130-001A00361EE0001C`，设备 inventory 回读
  `Fidget Spinner / 0.1.0 / 24`，证据为 `Logs/DeviceBuild24InstalledApps.json`。首次安装时设备锁屏，所以当时
  没有把“已安装”误报为“已启动”；用户解锁后重新启动成功并回读进程 PID 20173。由于 native
  `shippingCases` 漏项，第六款当时无法从模型库进入，不能把 Build 24 记为 FanCard 真机视觉或动态验收。

## Build 21 事故排查与 Build 23 恢复发布（历史记录）

> **截至 Build 23 的状态：用户已批准纠正后的 shipping Unity 预览；Release Build 23 已从隔离、不可变源码完成构建，覆盖安装并启动到 iPhone。该状态现已被上方 Build 24 覆盖。**
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
石墨双叶、磁吸推牌。2026-08-08 依据用户提供的旧版真机截图复核后确认，前一轮恢复把两套三叶视觉
归属接反：长水滴叶片的 `DragonScaleEDC` 才是用户截图中的原三叶金属，应由
`ThreeBladeMetalOriginal.unity` / `metal-three-blade` 承载，继续消费原等级、皮肤与贴纸；程序化尖三叶才应
留在 `ThreeBladeEDC.unity` / `pointed-three-blade` 并替代旧蓝色槽位。场景 builder、两张 shipping scene、
皮肤/贴纸预览入口和对应架构测试已同步交换，模型 ID 与历史存档键未改。`ProductCatalog` 成为 C# 场景、Coordinator、
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
模型展示交互同步收紧：iOS 两套触摸仲裁仍只在检测到第二个按下触点时进入 Pinch 并调用 `ZoomByScale`；
旋转类模型的单指 `OrbitByPixels` 不再按新视角重算 camera distance，因而单指只改变 yaw/pitch，不会产生
看似缩放的构图跳动。双指捏合仍使用原缩放边界；推牌/扇牌相机本就保持固定 framing distance。
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
场景表）。Build 22 恢复候选之后，本次正式推送把 build number 提升到 23。恢复前源码已保存为本地基线 commit `917553f`；正式恢复提交只会
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
Console。该联系表中的白色三叶视觉现已被 2026-08-08 的用户截图证据推翻，不能再作为安装批准。

纠正后的原三叶金属直接从 shipping `ThreeBladeMetalOriginal.unity` 实渲：夜航刻度分别覆盖方块
pictogram、HW text、细线 mark 的 top / hero / 左右斜视 / low 共 15 帧，联系表为
`Artifacts/OriginalMetalRecoveryV23/night-cyan-three-sticker-contact.png`；冰银回纹 + 方块 pictogram 的
五视角联系表为 `Artifacts/OriginalMetalRecoveryV23/ice-guilloche-five-angle-contact.png`。隔离工作树全量
EditMode 为 `190/193`；本次三叶场景归属、DragonScale、程序化尖三叶、皮肤、贴纸与零初速回归全部通过，
3 项失败均为未进入本次改动的 FanCard/其第六场景基线（材质 0.92 vs 旧期望 0.96、根姿态 180° vs
旧期望 0°、隔离基线 Build Settings 仍为五场景）。用户随后明确批准上述纠正预览并要求推送。正式
Release Build 23 从隔离 commit `8340cdd`（视觉恢复 commit `ed59715` 加唯一包号变更）生成；manifest 回读为
bundle `com.jiaweizhou.fidgetspinner.codex`、version `0.1.0`、build `23`、`development=false`、五个正式场景、
source commit `8340cddbecdd486f337f8956b306b90e9af8f675`。Unity 导出、Xcode Release 与严格 codesign 校验均成功；
`devicectl` 设备 inventory 确认同一 bundle 已覆盖为 `0.1.0 (23)`，随后成功启动并回读运行进程 PID `19345`。安装与启动不替代用户对
原三叶金属、尖三叶槽位、完整 UI、皮肤/贴纸、Combo 动态及零初速的真机肉眼验收。

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
| 第六款三层磁吸扇牌与独立四档阻尼 | 音频已集成并有定向测试；待 iPhone 听感验收，既有层距场景漂移待视觉流程处理 | 新产品 `magnetic-fan-card` 使用独立场景 `_FanCard/Scenes/MagneticFanCard.unity`、`FanCardDetentProfile`、`FanCardMagneticTrack` 与 `FanCardController`；三张 `52 × 74 × 3.2 mm` 竖牌共享圆角圆心轴，层中心距为 `4.2 mm`，底/中层各有一条向左下内缩的 45° 弧轨和 3 枚磁体，中/顶层各有一枚随动球。四档固定为 `0 / 1⁄3 / 2⁄3 / 1`，中片 `45°q`、顶片 `90°q`，并保留批准 demo 的脱档、弹簧、阻尼、摩擦、捕获与 `1/240 s` 子步。展示根节点现统一绕 Y 轴旋转 `180°`，因此展开交互主视图中的共轴孔/铬球位于前景顶片右下角；模型仍为原生 `52 × 74 mm` 平面比例，没有非等比 Transform 补偿。Coordinator、正式六产品 `ProductCatalog`、Build Settings、iOS 枚举、缩略图和共享相机/双指展示手势已接线；Build Settings 由唯一产品目录生成，首场景仍为尖角三叶，第六款扇牌位于末位。语义事件只从机械状态进入 `FidgetHapticRouter`，无新 raw-input→`IosHaptics`。2026-08-09 新增 `FanCardMetalDetentAudio`：只消费用户授权的真实 `DetentCrossed`，每档一次低约 `2.6` 半音的厚合金 `PlayOneShot`；5 个原子变体和 8 个 2D 声部已经写入 shipping 场景及场景生成器，Breakaway、Capture、Library、AUTO、Reset 和程序设姿静默。视觉仅改展示层：外框使用 `FidgetingApp/FanCardGunmetal`，参数为 metallic `0.90` / smoothness `0.34`，`0.48 mm` 上下倒角保留约 `2.24 mm` 连续直壁，以细颗粒 BaseMap、法线和受控侧壁高光表现珠喷哑光；暖银面使用 `FidgetingApp/FanCardSatinSilver`、smoothness `0.36`，用大面积对角软箱亮带形成明确明暗反差；直径 `5.3 mm` 的共轴球使用 `FidgetingApp/FanCardChrome`、smoothness `0.92`、深色球座和程序化暖白软箱/冷色侧条，球体下半部保持深灰。金色编织轨道、Oxanium A、向下黑桃和蚀刻细线仍是独立无物理展示层，不读取或写入前五款调节值；第五款默认物理相机保持不变 | 新增 `FanCardMetalDetentAudioTests` 定向 EditMode `3/3` 通过，报告 `Logs/FanCardMetalDetentAudioTests.xml`，覆盖厚合金音高/音量、事件门禁、严格单次 `PlayOneShot`、5 变体、8 声部和 shipping 场景接线。音频接线器编译并执行成功，日志为 `Logs/FanCardAudioSceneIntegrator.log`。同轮既有 `FanCardAcceptanceTests` 为 `13/14`：唯一失败是当前源码/测试 `LayerPitch = 3.5 mm`，shipping 场景仍为 `6.25 mm`；报告 `Logs/FanCardAudioRegressionTests.xml`，与新增音频无关，且因会改变视觉层距未在本轮擅自重建场景 | 尚未为本轮音频构建或安装新 iPhone 包；需在 iPhone 扬声器上验证金属 click 的厚度、清脆度、音量、跨档同步、快速跨档叠音；层距漂移需另行生成 shipping 视觉预览并经用户批准后才能改场景/推机 |
| 龙鳞三叶替换首个陀螺 | 已集成、测试、覆盖安装并启动；待真机肉眼验收 | `SpinnerModel.allCases`、`FidgetAppCoordinator.ProductModelIds` 与 `IosBuildPipeline.ProductScenes` 均以 `metal-three-blade` / `ThreeBladeEDC.unity` 为首项；`ProductUiState` 用 `fidgeting.primaryModelCatalogVersion = 1` 把既有安装的一次性默认选择迁移到龙鳞三叶，之后继续尊重用户选择；蓝色经典款保留为第二项。启动与 Reset 仍保持零角速度 | Swift iPhoneOS 15 typecheck；ProductArchitecture `32/32`、完整 EditMode `180/180`，报告 `Artifacts/PrimaryModelFocusedEditModeTests.xml`、`Artifacts/PrimaryModelFullEditModeTests.xml`。Unity 导出日志 `Logs/iOSBuild-DragonScalePrimary-B20.log`；设备回读 `Logs/DeviceBuild20InstalledApps.json` 确认 `com.jiaweizhou.fidgetspinner.codex / 0.1.0 / 20`，`Logs/DeviceBuild20Processes.json` 回读 PID 18095 | 已启动 Build 20；仍需用户在手机上确认第一页和旧选择迁移显示龙鳞三叶，并检查圆件轮廓、金属高光、贴纸、长按与 Combo 动态；启动不替代肉眼验收 |
| 长按模型轻弹、语义 Pop 与 Half Sheet 顺序（覆盖下方外观编辑行的较早直接打开描述） | 待用户预览批准；未构建/未推真机 | 长按成立后立即禁用当前模型交互并经 `FidgetHapticRouter` 发出一次语义 `Pop`；`ProductAppearanceActivationSequence` 以相机 framing 完成 `1.000 → 1.035 → 0.992 → 1.000`、总长 `0.22 s` 的物理中立轻弹，随后才打开现有共享组件 half sheet。三套正式产品相机均接入，未缩放模型 Transform 或修改碰撞体/角速度 | `SpinnerProgressionTests` 定向 `34/34`；完整 EditMode `178/179`，唯一失败是正式三叶场景当前 `48,054` tris 超出既有 `45,000` 预算，与本次入口状态机/相机距离修改无关。报告 `Logs/LongPressActivationEditModeTests.xml`、`Logs/LongPressActivationFullEditModeTests.xml`。五视角四阶段 shipping-scene 联系表与 Hero 动态预览位于 `Artifacts/Appearance/LongPressActivationV1/` | 必须先获得本轮预览的明确视觉批准，再执行 iOS 构建和安装；手机上仍需确认 Pop 强度、轻弹幅度、`0.22 s` 延迟、half sheet 动画与关闭恢复 |
| Combo ×30 / ×50 咬合轨道圆环分档（放射线降为辅助） | 已接入 shipping 原生反馈层，并按“继续精进圆环、不能只依靠发散激光”的反馈完成第三版真实预览；待用户视觉批准，未构建或推送手机 | `ComboHaloMilestoneStyle` 仍只从实际跨越的 Combo 数字选择展示档：×10/×20 为 `standard`，×30–×49 为 `overdrive`，×50+ 为 `apex`。高阶视觉主角改为 `ComboHaloInterlockRing`：×30 使用 6 段外环、3 段内轨、3 枚锁定刻度和一次顺向沿环扫光；×50 使用 8 段外环、5 段反向内轨、4 枚锁定刻度，并增加第二道反向扫光。相邻弧段分别从环内/环外和相反角度进入，经 `orbitLockPhase` 收拢到同一模型平面轨道，锁定后由 `orbitReleasePhase` 统一轻微外释；原有三道断环也加入不同方向的缺口转动，作为更低亮的余波。径向线缩减为 4 / 6 条，峰值仅为主 opacity 的 `0.24 / 0.34`，只在前 30% 时段短促出现；主轨道保持到 94%，因此层级不再依赖激光。所有圆环继续读取 live 模型中心、倾角和短轴比，使用中性白灰；不修改相机、材质、Combo 计数、XP、物理或 Haptic。Reduce Motion 完全关闭高阶轨道与放射辅助，只保留原有短淡化 | 原生确定性规则扩展为 `83/83` 并通过，覆盖 4/6 条辅助线、6/8 外弧、3/5 内轨、3/4 刻度、收拢/释放/扫光时序；shipping Swift 在 `arm64-apple-ios15.0-simulator` 全量 typecheck 通过。Unity 结构断言已更新为咬合轨道规则，但 `Temp/UnityLockfile` 显示当前 Unity Editor 仍占用 canonical 工程，因此未强退、未清缓存，也未误报本轮 Unity 重跑通过；旧速度版本的 `1/1` 报告仅保留为历史证据。隔离模拟器预览直接编译当前 shipping SwiftUI，×30 / ×50 动态均为 60 fps；证据位于 `Artifacts/ComboHaloNativePreview/combo-halo-motion.mp4`、`combo-halo-apex-motion.mp4`、`combo-halo-orbit-motion-comparison.png`、`combo-halo-tier-contact-sheet.png` 与 `combo-halo-angle-contact-sheet.png` | 第三版仍是新的 native UI 视觉变化，旧版批准不能沿用。需用户明确批准本轮真实预览、且 Unity Editor 释放工程后补跑定向回归，才能执行 iPhone 构建/安装；真机仍需确认 ×29→30、×49→50、快速触发、五模型自由视角、Reduce Motion / Transparency、VoiceOver 和热功耗 |
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
| 四款旋转模型真实转速风声与棘轮双层音频（本行覆盖原“三叶金属物理驱动棘轮音频”范围） | 运行时与网页已更新；最新小声腔回归待项目锁释放；待 iPhone 听感验收 | `RotorWindAudio` 已接入尖三叶、原三叶金属、镜钢四翼与石墨双叶四个正式场景，分别按 3 / 3 / 4 / 2 个叶片从 `RotorRigidbodyController.AngularSpeedRadians` 计算 blade-pass。主体 / 中频 / 高频 edge 混合为 `0.86 / 0.14 / 0.018`，使用 `OnAudioFilterRead`、`4 ms` 响应和 `256 samples` DSP buffer。根据“材质之间没有区别、只听见 Click、主段未放入”的反馈，首段与主段保持两条独立包络：首段只承载碰撞纹理，以周期 `0.14` 的立方衰减硬起音；主段/尾段只承载三层材质模态。再根据“金属腔体听起来太大、实物小于手掌、频率可以更高”的反馈，声腔改按类似厚重 Zippo 的精密件标定：主段 `3 ms` 攻击、最长 `65 ms` 且不超过周期 `0.72`；Unity 三层模态提高到 `620...920 / 1350...1900 / 2400...3600 Hz`，碰撞带提高到 `2.0...7.5 kHz`。三叶模型在 120 / 400 RPM 的 Click 约 24 / 7 ms，材质鸣响约 65 / 36 ms，能辨识材质但不会拖成大腔体长鸣。两条包络仍全部经过同一个 `alloyResonance`。网页保留“金属材质”选择 + 唯一“金属共鸣”：产品合金、厚壁合金、精密钢、温润合金和明亮合金五个 profile 分别固定频率比例、振荡波形、音高、三层模态混合与碰撞亮边；在 120 RPM / 厚重感 72% 时对应主段频率分别为 `683/1454/2594`、`580/1079/1769`、`785/1868/3336`、`648/1245/2075`、`771/1774/3201 Hz`。共鸣 `0...100%` 线性控制当前 profile 的首、主、尾整套声部；0% 明确显示“纯风（当前材质已静音）”。网页转速上限为 `600 RPM`，常用档为 `120 / 250 / 400 RPM`；Unity 静止严格为零，只读真实速度，Reset 清空滤波与音尾，不写角速度且不进入 Haptic。平滑模式只有风声；棘轮模式叠加原子 click | 上一轮唯一共鸣版本的 `RotorWindAudioTests` 定向 EditMode `14/14` 通过，报告 `Logs/RotorWindAudioLowLatencyTests.xml`。本轮新增按实际秒数计算 `ResolveMetalRing` 的 `3 ms` 攻击、`65 ms` 绝对上限、`0.72` 高速上限、主段有效长度与共享共鸣源码断言；开放中的 Unity Editor 已自动编译本轮 runtime/test 源码，两个 ScriptAssemblies 时间戳晚于对应源码，当前 Editor 日志无编译错误。因交互式 Editor 持有 `Temp/UnityLockfile`，遵守单写者约束不并发启动 Test Runner，故不能把旧 `14/14` 报告冒充本轮结果。网页 `node --check`、HTTP 200 通过；浏览器已在 120 RPM / 厚重感 72% 下循环五个 profile，核对上述五组三层读数，并将可试听状态停留在明亮合金、共鸣 100% | 关闭当前 Unity Editor 后重跑 `RotorWindAudioTests`，取得小声腔版本的干净结果；尚未构建或安装新 iPhone 包；需试听五种材质主段辨识度、首段/主段衔接、0% / 30% / 60% / 100% 共鸣过渡、低频重量、真实停转尾音及 CPU/温升 |
| 金属共振随真实转速变调（本行覆盖上一行的三层频率范围与 120 RPM 网页读数） | 运行时与网页已更新；最新回归待项目锁释放；待 iPhone 听感验收 | `RotorWindAudioModel` 从同一真实归一化角速度计算 `resonancePitchTracking = normalizedSpeed^0.78`，把三层模态范围扩为 `620...1050 / 1350...2350 / 2400...4400 Hz`；blade-pass 仍严格为 `RPM × bladeCount ÷ 60`。因此转速上升时 Click/鸣响事件变密，三层材质鸣响与碰撞带也实时升调，而每个材质 profile 的频率比例、波形、混合和唯一 `alloyResonance` 强度保持不变。网页用同一个 `0.78` 曲线驱动实际振荡器与可见读数：120 RPM / 厚重感 72% 的五种材质为 `719/1532/2732`、`611/1137/1864`、`827/1968/3514`、`683/1312/2186`、`813/1869/3372 Hz`；明亮合金在 120 / 250 / 400 RPM 分别为 `813/1869/3372`、`944/2171/3917`、`1076/2474/4464 Hz`。该链只读速度，不写 Rigidbody，也不进入 Haptic pipeline | 新增 `WindModel_MetalCadenceAndPitchBothFollowMeasuredSpeed`，锁定三叶 120 / 400 RPM 的 `6 / 20 Hz` blade-pass、主频升幅大于 20%、三层单调升调与 `0.78` 曲线；当前 Unity Editor 已自动编译 runtime/test 源码且无编译错误，但仍持有 `Temp/UnityLockfile`，未并发启动 Test Runner。网页 `node --check`、HTTP 200 通过；浏览器已在播放中实际切换 120→400→120 RPM，状态与上述明亮合金读数同步变化 | 关闭当前 Unity Editor 后运行最新 `RotorWindAudioTests`；iPhone 上确认加速/减速时音高连续、无阶跃或延迟，低于 400 RPM 仍清楚，材质可辨且不会因高转速变尖薄；尚未构建或安装本轮版本 |
| 网页定稿明亮合金音色接入正式 App（本行覆盖上两行的通用模态混合、频率端点与 32% 场景共鸣） | 运行时和四个 shipping scene 已接入；Unity Test Runner 受许可证阻塞；待 iPhone 听感验收 | `RotorWindAudioModel` 正式固定当前网页的明亮合金 profile：主层正弦，次层/上层由 `ResolveBrightAlloyTriangle` 生成基频 + 安全三次泛音，混合 `0.105 / 0.215 / 0.160`，碰撞亮边 `0.34`；真实 20→400 RPM 的三层端点为 `669→1076 / 1539→2474 / 2776→4464 Hz`。`resonanceDrive` 改为与网页一致的线性共鸣量，空气层使用同一 `1 - 0.88 × resonance^0.85` 曲线并保留 12% 下限。`DefaultAlloyResonance = 1.0` 同时进入运行时字段、`Configure()`、`ThreeBladeSceneBuilder`、`RotorAudioSceneIntegrator` 与尖三叶/原三叶/镜钢四翼/石墨双叶四个场景序列化值；重建不会退回旧 32%。该 renderer 仍只读 `AngularSpeedRadians`，Reset 归零音尾，不写 Rigidbody、不新增 Haptic 调用 | `RotorWindAudioTests` 已增加网页 120 / 400 RPM 六个频率值、三层 mix、三角泛音峰值、碰撞量和四场景 `1.0` 共鸣断言。场景文本审计确认四处均为 `alloyResonance: 1`，没有旧 `0.32`；使用 Unity 随附 Roslyn 和当前 Unity reference assemblies 对最新 runtime 源码独立编译成功，只有因同时引用旧 `Assembly-CSharp.dll` 而产生的预期同名类型警告，无编译错误。Unity headless 与常规 `-runTests` 均因当前 Licensing Client 无可用 entitlement 提前退出，`Logs/RotorWindAudioBrightAlloyAppTests.log` 未生成 XML，因此不误报测试通过 | 恢复 Unity 许可证后运行 `RotorWindAudioTests` 并保存 XML；尚未构建或安装本轮 iPhone 包。真机需确认四款模型平滑模式只有该风声、棘轮模式叠加 click，120→400 RPM 升降调连续，100% 明亮合金不会过响、削波或遮蔽空气层，Reset/后台切换无残尾 |
| Alloy Tone Lab 当前金属材质“脆↔闷 / 低↔高”手动试听 | 网页研究工具已实现；不自动改写 App | 金属材质选择器下方新增当前材质专属微调区。`metalBrightness 0...100` 同时控制金属总线低通 `900...7800 Hz`、高层/上层模态、碰撞亮边和低模态补偿，0% 为沉闷少泛音，100% 精确保留选中材质原始明亮配比；`metalPitchSemitones -12...+12` 对低/中/上三层与碰撞带作共同移调，仍叠加真实 RPM 的 `0.78` 跟随曲线。界面显示当前主音音名、八度、音分和三层实际 Hz，并提供低八度/低五度/原调/高五度/高八度快捷档。拖动脆闷或音高时会直接启动/更新试听，状态保存到现有 wind local storage；材质、共鸣量和转速仍为独立控制 | `node --check`、HTTP 200、`git diff --check` 通过；浏览器已验证明亮合金 120 RPM 在 `0% / -12` 时为 `406 / 934 / 1686 Hz`、`100% / +12` 时为 `1625 / 3738 / 6744 Hz`，低五度快捷档为 `542 / 1247 / 2251 Hz`，恢复原调后为 `813 / 1869 / 3372 Hz`，页面保持 120 RPM、共鸣 100%、明亮合金、100% 明亮度、原调并运行 | 该实验参数不会直接写入 Unity；用户确定喜欢的明暗百分比与半音偏移后，再同步到 `RotorWindAudioModel`、四个场景、测试和 iPhone 构建。需人工听辨极暗档是否仍保留足够金属身份、极高档是否刺耳，以及移动端滑杆触控空间 |
| 用户当前 +9 半音明亮合金设置固化到 App（本行覆盖上三行的原调频率与网页默认） | 运行时与网页默认已更新；Unity Test Runner 受许可证阻塞；待 iPhone 听感验收 | 从当前 Alloy Tone Lab 可见状态读取并固化：250 RPM、厚重感 72%、切风清晰度 100%、叶片脉动 100%、明亮合金、金属明暗 100%、整体音高 `+9` 半音、金属共鸣 100%、网页停转模拟 `2.30 s`。`RotorWindAudioModel` 新增正式偏移 `FinalMetalPitchSemitones = 9`，以 `2^(9/12) ≈ 1.6818` 同时移调三层金属模态与短碰撞带；App 的真实 20→400 RPM 范围为 `1125→1810 / 2588→4161 / 4669→7508 Hz`，250 RPM 验收点为网页当前显示的 `1588 / 3651 / 6588 Hz`。次层与上层三角金属波的三次泛音在接近 Nyquist 时自动退化为纯基频正弦，避免高音折叠失真。四个 shipping scene 的 `alloyResonance` 仍为 `1.0`；空气清晰度、叶片脉动和厚重感沿用当前正式风声混合。250 RPM 仅作为音色验收参考，App 仍从零角速度启动并只读真实速度；网页 `2.30 s` 只控制实验室停转模拟，不复制为独立 App 音尾，App 消散继续由真实 half-life 物理减速决定。未新增原始输入到 `IosHaptics` 的调用 | `WindModel_MetalCadenceAndPitchBothFollowMeasuredSpeed` 已增加 250 / 400 RPM 精确频率、`+9` 半音偏移和三层随速断言；三角波测试增加 44.1 kHz 下的 Nyquist 安全退化。四场景文本审计仍为 `alloyResonance: 1`。使用 Unity 随附 Roslyn 与当前 Unity reference assemblies 对最新 runtime 源码独立编译成功，只有同时引用旧 `Assembly-CSharp.dll` 造成的预期同名类型警告，无编译错误；当前 Licensing Client 无可用 entitlement，故本轮仍没有 Test Runner XML，不误报为自动化通过 | 恢复 Unity 许可证后运行最新 `RotorWindAudioTests` 并保存 XML；尚未构建或安装本轮 iPhone 包。真机需确认四款旋转模型在主要低于 400 RPM 的使用区间仍清脆、+9 半音不刺耳、高层无 aliasing、平滑模式只有风声、棘轮模式正确叠加 click，以及真实减速、Reset 与后台切换无残尾 |
| Alloy Tone Lab 第 15 条“精密按压回弹”双触点音效 | 网页研究工具已实现；未接入 App | 音效库增加独立 `precision-press-rebound` preset，前 14 条继续保持单次 Click。完整播放由三段组成：68 ms、`-0.6` 半音的厚实按压 Click；680 Hz、26% 的短促机构回响；0.36 s 后触发由独立 `button-single` 素材生成的较小、较亮回弹 Click。回弹端从当前按压参数派生 `+3.8` 半音、`0.60×` 长度、`0.66×` 厚重、`+18` 清脆度和 `0.76×` 峰值，因此不是第一声的简单延迟复制。选择该 preset 后，拆分标题改为“按压 → 机构行程 → 回弹”，尾段卡和 transport 可单独试听回弹，原“消散时长”滑杆改为“按压到回弹间隔”；选择其他 14 条时所有文案与单击规则自动恢复。WAV / JSON 导出、A/B 保存、停止 future-scheduled node 与波形第二瞬态均支持该双触点字段 | `node --check`、HTTP 200 与相关 `git diff --check` 通过。浏览器刷新后确认 15 张音效卡；选择第 15 条后可见 68 ms 按压、680 Hz 机构回响、0.36 s 后 `+3.2` 半音回弹（`-0.6 + 3.8`），完整播放和“只听回弹”均到达“试听完成”，控制台无 error | 当前只加入本地研究工具，不视为 Unity 集成，也未构建或安装 iPhone。需用户试听决定按压重量、回弹亮度、两声比例和 0.36 s 默认间隔；若选定具体产品动作，再按语义事件分别接线并补运行时、场景、测试与真机验收 |
| Alloy Tone Lab 第 16 条“罐头币按压 · 视频原声” | R1/R2 错误动作已废弃；网页 R3 已实现；未接入 App | 用户指出此前音效与视频按压完全无关。重新逐帧确认后，目标动作是视频 `21.815...23.380 s` 的一次连续压入，而不是 33 秒附近的单击，也不是滚珠匀速越齿。R3 直接提取这 1.565 s 原始动作时序：`0...0.250 s` 为开始受力，`0.250...1.240 s` 为金属片密集翻转/塌陷，`1.240...1.565 s` 为触底收住；不再循环单个 Click，不叠加合成共鸣。完整原视频/音轨不入库，只保存该短动作；用按压前 `21.650...21.780 s` 估计底噪，执行温和 `0.52×` 频谱扣除、82 Hz 高通、18.5 kHz 低通、4/65 ms 首尾淡化和 `-1.5 dBFS` 归一化。三段可独立试听；为避免再次偏离参考，素材、分段边界、主段音色和尾段时长默认锁定，仅允许整体音高、厚重、清脆和输出音量微调 | 新资产 `tools/alloy-sound-lab/assets/audio/exciters/xhs-can-coin-reference-press.wav` 为 48 kHz stereo、1.565 s；提取方法为 `tools/alloy-sound-lab/scripts/extract_can_coin_press.py`。`node --check`、脚本 `py_compile`、相关 `git diff --check`、主页与 WAV HTTP 200 均通过；浏览器显示第 16 条为“开始受力 → 金属片连续翻转 → 触底收住”，完整、首段、主段、触底四种播放均到达“试听完成”，错误日志为空 | 本轮只纠正网页研究工具，不视为 Unity/App 集成，也不构建或安装 iPhone。该片段仍来自平台压缩和视频混音，用户确认动作与听感后，正式发行前应完成素材权利确认或重录/全合成替代 |
| Alloy Tone Lab 第 17 条“罐头币按压 + 回弹 · 纯净提取” | 用户指出 R4 缺少回弹；网页 R5 已纠正；未接入 App | R4 只保留 `22.14220 s` 按压并误将整个尾段禁用。R5 从同一次视频动作的 `23.25553 s` 另外提取手指松开时的真实回弹，绝不复制或移调按压声：按压长 116 ms，回弹长 94 ms，原视频两端间隔 `1.11333 s`。两声各自用无撞击窗口估计持续背景谱，以时间/频率双向中值滤波区分音乐横向谱线与机械纵向瞬态，再执行自适应频谱扣除、155 Hz 高通、18 kHz 低通和短噪声门；首 18 ms 仅恢复受门控的真实 280–2600 Hz 冲击体，避免强降噪削薄且不让持续音乐进入尾部。网页第 17 条改为“按压 Click → 按住静音 → 回弹 Click”：首段和尾段可独立试听，主段只表示已去除背景的按住静音，间隔滑杆可调；素材、长度、共鸣与噪声门继续锁定 | `xhs-can-coin-pure-click.wav` 与 `xhs-can-coin-pure-rebound.wav` 都是 48 kHz stereo、各只有一个主瞬态、峰值 `-1.50 dBFS`、零削波；按压谱心约 `4454 Hz`、280–2200 / 2200–15000 Hz 占比 `37.98% / 57.50%`，回弹谱心约 `3995 Hz`、相应占比 `45.10% / 33.26%`，证明回弹保留自己的较短、较暖频谱而非按压复制。`scripts/extract_can_coin_pure_click.py --event press|rebound` 可从本地解码源重建两份资产。`node --check`、隔离 pycache 的 `py_compile`、相关 `git diff --check` 与两份资产 HTTP 200 均通过；浏览器显示第 17 条双触点与可调 `1.11 s` 间隔，完整播放和“只听回弹”都到达“试听完成”，控制台无 error | 这是本地研究工具，不视为 Unity/App 集成，也不构建或安装 iPhone。受源视频混音与平台压缩限制，“去背景”是强瞬态分离而非多轨母带级无损分离；需用户试听确认回弹音量、音色和真实间隔，发行前仍需权利确认或重录/全合成替代 |
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

## CLI Anything Blender 龙鳞 EDC 85 mm（2026-08-10，已接镜钢四翼槽位并安装 Build 37）

- 本轮按用户指定的 `cli-anything-blender` skill 建立了有状态工程
  `ArtSource/DragonScaleEDC/CLIAnything/DragonScaleEDC_CLI.blend-cli.json`。CLI REPL 已持久化
  10 个机械层级节点和 5 组 PBR 材质参数；精确 loft、轴承、径向拉丝面、导出与真实渲染由
  `tools/blender/build_dragon_scale_cli.py` 在 Blender 5.2 LTS 中完成。当前安装的 CLI 1.0.0 没有技能文档所列
  `preview` 命令组，因此没有用 primitive/workbench 假预览代替；七张验收图均来自候选 `.blend` 的真实 Eevee
  渲染。
- 尺寸只采用标注参考中可核验的硬约束：总宽 `85.0 mm`、中心指盖直径 `0.52W = 44.2 mm`、主体总厚
  `0.09W = 7.65 mm`、装配总厚 `0.20W = 17.0 mm`，三翼为 `90° / 210° / 330°`，间隔严格 `120°`；
  轴承按爆炸结构使用 `22 × 8 × 7 mm` 的 608 级尺寸。最终源场景实测为总宽 `84.999993 mm`、指盖直径
  `44.199999 mm`、主体厚 `7.650000 mm`、总厚 `17.000001 mm`、轴承外径 `22.000000 mm`。参考图没有
  内部公差、质量、紧固和真实加工图，因此本候选不能表述为量产 CAD 或机械公差 100% 复刻。
- DCC 源和交换资产位于 `ArtSource/DragonScaleEDC/CLIAnything/`：
  `DragonScaleEDC_CLI_85mm.blend`、视觉 FBX、GLB 和独立碰撞 FBX。视觉资产包含上/下 24 面切削指盖、
  24 扇区真实径向拉丝面、POM 上下垫片、钢制外圈/内圈/屏蔽片/10 球轴承、固定轴和三翼一体机械 Mesh。
  主体为喷砂钛 `metallic 1.0 / roughness 0.28 / micro normal 0.12`；指盖为
  `metallic 1.0 / roughness 0.19 / anisotropy 0.55`；抛光边 `roughness 0.10`；POM 为
  `metallic 0 / roughness 0.42 / IOR 1.48`。
- `Artifacts/DragonScaleEDC_CLIAnything/dragon-scale-cli-validation.json` 记录 33 个可视 Mesh、约
  `25,164` tris 和 `RotorBody_OnePiece` 的 `0 boundary / 0 non-manifold / 0 zero-area` 审计。清空 Blender
  factory 默认物体后重新导入 FBX 与 GLB，两者均回读为 33 个 Mesh、包围盒
  `84.999997 × 77.434635 × 17.000001 mm`，并保留 Rotor / Fixed / Bearing / Cap / Washer 层级；碰撞 FBX
  回读为 4 个 Mesh、厚 `7.650013 mm`。Unity 导入保持米制、层级和 FBX 法线，关闭动画、灯光、相机、
  BlendShape 与网格压缩；运行场景继续由 `RotorRigidbodyController` 在启动与 Reset 时把角速度归零。
- 真实预览位于 `Artifacts/DragonScaleEDC_CLIAnything/`，覆盖 top、authored hero、left/right oblique、
  low、side 和 exploded 七个视角。交换 FBX 另复制到
  `Assets/_ImportedSpinner/Models/DragonScaleCLI/`，只替换稳定产品 ID `gold-four-wing` 所属的
  `Assets/_ImportedSpinner/Scenes/ImportedSpinner.unity`；`pointed-three-blade` 与 `metal-three-blade` 的
  Scene 路径、Catalog ID、资源依赖和场景文件均未改动，两个受保护 Scene 的文件时间仍停在
  `2026-08-09 14:53`。场景将 Rotor / Fixed / Bearing / Cap / Washer 分层接到 `RotorDynamic`、
  `HubStatic` 与半速轴承保持架；主体风声叶数从旧四翼语义校正为 `3`，棘轮音效、语义 Haptic、Core Motion、
  手势和零初速规则继续复用既有正式链路。
- 正式 Unity 场景五视图位于 `Artifacts/DragonScaleCLIShippingPreview/`，覆盖 authored hero、top、左右斜视与
  low angle；测试证据为同目录 `EditModeTests.xml`，结果 `300/300` 通过，其中
  `ProductArchitectureTests 39/39`、`RotorWindAudioTests 15/15`。自动化还锁定 Unity 实测
  `85.0 × 17.0 mm`、约 `25k tris`、8 类独立 PBR 材质、旋转外圈/固定内圈和新 FBX 不得进入两个三叶 Scene。
  用户已对本轮统一发布给予授权，该候选随 Build 37 完成 Xcode Release、签名和覆盖安装；手机安装后处于锁屏，
  因此仍不把自动化通过或安装成功误报为 Dragon Scale 真机视觉/性能验收。

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

## 2026-08-08 扇牌尺寸与厚度校正

- 本节覆盖上表扇牌行中的旧尺寸与构图数据。每张卡现在是独立闭合的
  `63.5 × 88.9 × 2.5 mm` 刚性圆角矩形实体，没有 bend、vertex offset、cloth 或软体组件；
  四角半径为卡宽的 `6% = 3.81 mm`，外缘倒角为厚度的 `15% = 0.375 mm`。银色正反面和
  现有 A/黑桃/细线图案改为贴合实体表面的共面投影，不再以第二个薄盒产生卷边侧壁；唯一可见厚度
  来自哑光枪灰色主体的连续直壁。层中心距为 `6.25 mm`，所以相邻实体面之间保持均匀
  `3.75 mm` 空气间隙，正好是单层厚度的 `1.5×`；三层 Y 轴 AABB 不重叠。
- 三张主体均生成真实 `Ø4.30 mm` 共轴通孔和 `0.22 mm` 孔口倒角。轴套直径为
  `3.876 mm`，因此单边径向间隙约 `0.212 mm`；卡片绕轴旋转而不与轴相交。主体外壁、孔壁、
  顶面和底面均为闭合实体几何，正反面图案分别朝外，无背面剔除缺面。随动球仍只在原暗色轴承座中
  露出 `0.7 mm` 球冠，轴、垫圈、球头、四档交互、阻尼、Haptic、纹理和场景灯光均未改动。
- `ProductFramingCatalog` 的详情占屏宽/高为 `0.84 / 0.78`，Library 为
  `0.79 / 0.73`；`FanCardSceneBuilder` 读取同一 Profile，shipping 场景序列化值已同步为
  `0.84 / 0.78`。低角预览为 `1200 × 900` 近距离横构图，并新增闭合侧剖图。四档、45°/90°、轨道、
  阻尼、Haptic 和前五款产品均未修改。
- `ReferenceGeometryKeepsFullCardSizeThickSidewallsAndExpandedFraming` 锁定上述几何与构图；
  `FanCardAcceptanceTests` `10/10` 通过，报告 `Logs/FanCardTests.xml`。完整 EditMode
  在 build number、序列化 ProjectSettings 和架构测试同步为 Build 24 后为 `194/194`，报告
  `Logs/Build24EditModeTests.xml`。
- 八张最新 shipping Unity GPU 预览位于 `Artifacts/FanCardMaterialPreview/`，生成日志为
  `Logs/FanCardPreviewGpu.log`。用户已明确视觉批准；Release `0.1.0 (24)` 已覆盖安装到 iPhone，设备锁屏，
  未自动启动，真机肉眼与动态手感仍待验收。

## 2026-08-09 旋转热区收紧与 Orbit 手势恢复

- 根因是四款旋转模型共用的屏幕兜底旋转半径为短边 `48%`，而圆形模型详情构图的可见直径为短边
  `64%`、可见半径约 `32%`；因此屏幕每侧只剩约 `2%` 的区域不会被 Spin 抢走，用户很难从模型外侧
  开始拖动观察角度。真实叶片、中心盖和模型 Collider 并非根因，仍保留最高命中优先级。
- `FidgetSpinnerMotion.DefaultFallbackTouchRadiusFraction` 现在是唯一权威值 `0.36`，并提供纯函数
  `IsWithinFallbackSpinTouchRegion`。这在可见轮廓外保留约 `4%` 短边的触摸容错，同时把每侧可靠
  Orbit 区恢复到约 `14%`。`MobileGestureController` 与 `FidgetSpinnerController` 共用该规则；正式
  `ThreeBladeEDC`、`ThreeBladeMetalOriginal`、`ImportedSpinner`、`TwoLobeBar`、经典场景和 prefab 的
  序列化值都已同步为 `0.36`。没有修改角速度、阻力、Collider 尺寸、Haptic 或相机响应曲线。
- 新增 `FallbackSpinTouchRegion_PreservesAUsableOuterOrbitBand`，并扩展正式场景
  `MobileGestures_OrbitKeepsScaleAndPinchZoomClamps`：模型中心仍分类为 Spin，旧 `48%` 会吞掉的短边
  `42%` 位置现在明确分类为 Orbit。纯规则、五场景序列化、正式三叶运行场景与架构定向回归
  `93/93` 通过，报告 `Logs/CompactSpinTouchRegionFocusedTests.xml`。
- 因正式工程当前由用户的 Unity Editor 独占，且工作区已有早于本次修改的扇牌测试编译错误（测试引用
  三个尚不存在的 `FanCardSpecifications` 常量），本轮按 `recover-unity-builds` 单写入规则在不复制
  `Library/Temp`、排除该既有故障测试目录的 `/tmp` 隔离快照验证。完整隔离 EditMode 为 `212/213`；
  唯一失败是性能架构测试按正式仓库相对路径读取 `scripts/ios_build_and_install.sh`，隔离工程位于
  `/private/tmp` 导致路径不存在，并非产品运行或热区断言失败。报告
  `Logs/CompactSpinTouchRegionFullEditModeTests.xml`。当前状态为“代码/场景/定向测试完成，待真机构建与手感验收”。

## 2026-08-09 推牌类加重 Haptic

- 本节覆盖上表推牌的单个 `1.00 / 1.00` transient、旧双脉冲以及扇牌单冲击描述。线性磁吸推牌和三层扇牌均从机制授权的 `DetentCrossed` 进入 `FidgetHapticRouter`，再调用新的有限 `CodexIosHapticsPlayPushDetentPacket`；没有新增原始输入到 `IosHaptics` 的直连。
- 线性跨档为主冲击 `0.98 / 0.78` + `30 ms` 低锐度重量段 `0.58 / 0.22` + `22 ms` 收尾 `0.52 / 0.44`；扇牌主冲击随速度为 `0.92→1.00 / 0.76→0.90`，叠加 `32 ms` 重量段 `0.64 / 0.24` 和 `22 ms` 收尾 `0.56 / 0.42`。两者的 Breakaway/Capture 仍保留为机制语义，但不再叠加额外震动。包内 continuous 只有 `30–32 ms` 定长，不是常驻/循环 player；AUTO、Library、Reset、停指和程序设姿保持静默。
- `MagneticDetentTrack1DTests`、`EdcSliderAcceptanceTests`、`FanCardAcceptanceTests` 与 `ProductArchitectureTests` 已同步新参数、三层结构、非限流跨档和 Breakaway/Capture 抑制断言。核心 C# 源码已通过 Unity 6000.5.6f1 Roslyn 独立编译；`CodexIosHaptics.mm` 已通过 iPhoneOS 15 arm64 Objective-C++ syntax check。因正式工程的 Unity Editor 持有 `Temp/UnityLockfile`，按 `recover-unity-builds` 单写者规则只复制 `Assets / Packages / ProjectSettings` 到本地临时隔离工程，不复制或清理正式 `Library / Temp`。聚焦 EditMode 实测 `46/46` 通过，报告为 `Logs/PushCardWeightedHapticsFocusedTests.xml`，完整日志为 `Logs/PushCardWeightedHapticsFocusedTests.log`。
- 状态：运行时、场景/Coordinator 路由、原生 renderer 和聚焦自动化已完成；仍待支持 Core Haptics 的 iPhone 触感验收。真机需对比旧版的慢搓边缘、单档重量、快速连续跨档、无重复触点、停指静默、后台/engine reset 和温升；编译与自动化不替代真机手感。

## 2026-08-10 Haptic 设置保存并返回当前玩具

- 根因有两层：`ProductTopBar` 在设置页仍把唯一可见退出动作固定到 `showMySpinners()`，所以只能回模型库；同时 `DETENT LAB` 的预设、Intensity 与 Sharpness 只发给 Unity 运行时，没有进入原生 `UserDefaults`，重启后会回到默认值。
- 设置页右上角现在把已选中的齿轮替换为明确的勾选操作，先调用 `ProductUiState.applyAndPersist()`，再经现有 `dismissPanelToSelectedModel()` 回到当前选中的玩具。左上返回模型库的路径保持不变；没有新增原始输入到 `IosHaptics` 的调用。
- `DETENT LAB` 三项新增独立持久化键；运行时回传的最终配置、预设切换和两条覆盖滑杆都会自动保存。原生 Overlay 安装时先恢复已保存的预设，再按顺序恢复 Intensity / Sharpness，最后向 Unity 请求权威状态，保证物理档位数和 Haptic 仍读取同一 `DetentFeelRuntime.ActiveConfig`。
- `SettingsPanelSeparatesProductControlsFromSemanticCoreHapticsEditor` 已增加保存入口、当前玩具返回链路、三项持久化键和启动恢复的源级回归断言；当前 shipping SwiftUI 已通过 iPhoneOS 15 arm64 typecheck。正式工程被正在运行的 Unity Editor 独占，隔离副本又因当前账号缺少 `com.unity.editor.headless` entitlement 无法启动 Test Runner，因此本轮未生成新的 Unity XML，也不误报专项通过。仍需编辑器释放后补跑该测试，并在 iPhone 上确认六款玩具的保存返回、重启恢复与实际触感。

## 2026-08-10 无界推牌 CLI Anything Blender（Unity Round 5 视觉失败，未集成/不发布）

- 已复核 Obsidian `无界♾️` 视频：`5.55–6.10 s` 是两个半体锁定为一个刚体后绕指尖支点旋转，不是上半体相对下半体连续转 `360°`。纠正版交互平面 Demo 把“内部相对 `X/Z` 推滑”和“整机绕指旋转”拆成互斥模式，用户已确认按该理解继续。
- `unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything/UnboundSliderWhiteModel.blend-cli.json` 是当前可回退的 CLI 场景源：`52 × 36 × 14 mm` 白模起点、两个圆角金属半壳、两个载板、两个接触层、20 颗磁体和两组黄铜音叉组件；第 `1/40` 帧分别是装配态/工程爆炸态。
- Blender 真实渲染位于 `Artifacts/UnboundSlider/WhiteModel_2026-08-10/`，包含 authored hero、正视总平面、左/右斜视、顶角、低角和爆炸图。当前只达到“Blender 白模待视觉批准”；没有导出或接入 Unity，没有修改 shipping `MeshyEDC.unity`，没有替换 `magnetic-slide-tile`，也没有构建或安装到设备。
- `2026-08-11` 用户否决初版细节完整性，指出中间纹路和外表镂空均未呈现。修订场景现以 `28` 个布尔切割体重建上下装饰壳的水滴孔、圆端长窗与三角孔，并以 `48` 段有厚度折线和中心螺钉重建独立中间板。修订真实渲染位于 `Artifacts/UnboundSlider/WhiteModel_2026-08-11/`：外壳正视 `10_OrnamentalFront.png`、中层独立正视 `09_MiddlePatternFront.png`、装配 Hero `07_DetailHero.png` 与爆炸图 `08_DetailExploded.png`。修订仍待用户视觉确认，旧批准状态不能沿用。
- 下一门禁：用户批准白模比例、圆角、磁阵、层厚和爆炸顺序后，才进入 PBR 材质/贴图与 Unity 原型。Unity 变化还必须从 shipping 场景重新生成 top / hero / 左右斜视 / 低角预览，并再次取得视觉批准后才能构建或安装。
- `2026-08-11` 已把用户最终确认的开孔方向收敛为上下两组严格镜像的 goggle：每组由两个完整
  `R4.2 mm` 等圆和 `3.5 mm` 直腰连接；圆心为 `X=±18.0 mm / Z=±6.8 mm`，左右三角在中线对齐，
  上下梯形窗与 goggle 保持 `1.2 mm` 最小间隙。确定性 CLI/Blender 源现包含真实通孔、独立中层
  `24` 条 chevron 纹、中心螺钉、每半体 `6` 个可视磁位和爆炸/打开态；名义包络
  `52 × 36 × 14 mm`，最终 DCC 审计为 `36,112 tris`，上下金色外壳均
  `boundary/non-manifold/zero-area = 0/0/0`。验证文件为
  `Artifacts/UnboundSliderCLIAnything/unbound-slider-cli-validation.json`。
- 为避免薄板的平面圆角被三维 Bevel 吃穿，外壳、金边和中层已改成二维圆角轮廓挤出后只施加微倒角；
  所有带孔凹面在 Blender 内确定性三角化，避免 FBX/Unity 自行跨孔洞连接。九张真实 DCC 预览位于
  `Artifacts/UnboundSliderCLIAnything/`，可复现工具为 `tools/blender/build_unbound_slider_cli.py`。
- `/tmp` 隔离 Unity 候选曾完成轴向校正、`39,384`-triangle 场景接入并通过
  `EdcSliderAcceptanceTests 10/10`；但真实 shipping scene 第五轮预览虽已消除跨孔洞三角伪影，
  右半金属面仍发生高光剪切，金色表面与中层细节不可稳定读取，因此视觉门禁失败。拒绝预览、日志和
  当轮测试 XML 保存在
  `Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11/`。
- **最终收口：未完成，不进入本次统一发布。** 隔离工程生成的 scene/prefab/material 没有同步到共享
  主工程；`MeshyEDC.unity` 和 `EDC_Root.prefab` 仍保持本任务开始前状态，没有替换
  `magnetic-slide-tile`，没有构建或安装手机。主工程只保留 ArtSource、DCC 交换资产、源贴图、构建工具、
  拒绝预览和测试证据；后续若重启此 feature，有限下一步是继续收敛无界局部材质响应，而不是扩展交互范围。

## 2026-08-11 磁吸扇牌完整轴角、双层背轨与动态指尖驱动

- 本节覆盖此前扇牌缺角、轴位圆环、底片滑轨、固定轴角手势与旧构图描述。三张
  `63.5 × 88.9 × 2.5 mm` 刚性牌的暖银面现在在右下共同轴孔外保持完整封闭圆角；轴内为
  `2.00 mm` 下沉哑光轴芯，正面只覆盖一枚 Blender 输出的 `2.07 mm × 0.65 mm` 低矮抛光
  `CommonAxis_BearingCap_Chrome`，不再透出夜景亮斑或形成多层同心悬浮圆环。结构校验轴标记继续
  无 Renderer。背轨装配锁定为 TopCard + MiddleCard，BottomCard 无轨；随动件锁定为
  MiddleCard + BottomCard。轨道、网格、三枚磁体、轴承帽和 A/Q/K relief 均由同一 Blender 源重建，
  完整 `6.2 mm` 外轮廓最小边缘净空实测 `7.590 mm`。
- `FanCardController` 的直接输入已由“围绕右下角轴孔计算 pointer angle”改成“把屏幕位移投影到当前
  三卡整体视觉质心的运动切线”。慢推连续累计距离并逐档跟手；Speed、累计 Distance、可用 pressure
  与 Frequency 共同决定 Intensity/快速权重，只有快速且达到最小距离的手势才在松手后授权端点收尾，
  不再把每次手势降级为均速开/关。机械层仍严格绕真实共同轴旋转。详情交互和快速收尾期间继续暂停
  Core Motion，`FanCardPresentationCenter` 同时作为取景/Orbit/陀螺仪视觉焦点，避免用某个牌角旋转
  整个排面。详情/Library 构图占屏参数同步为 `0.80 / 0.80` 与 `0.72 / 0.72`。
- 线性推牌与扇牌现向原生 HUD 发布各自真实 `Speed / Intensity / Frequency`：线性速度为 `mm/s`，扇牌
  为 `°/s`，旋转产品仍为 RPM。遥测不直接触发 Haptic；扇牌仍按
  `input → mechanism state → semantic event → Haptic recipe → iOS renderer` 逐档输出既有重磁包，
  `Breakaway/Capture/Library/AUTO/Reset` 静默。
- 重建与验证证据：Blender 5.2 源、FBX 与 `Artifacts/FanCardBlenderPreview/` 已重建；主工作区完整
  `validate_fan_card_guardrails.py` 全通过，净空 `7.590 mm`。隔离 Unity 6000.5.6f1 shipping scene
  编译/重建成功，`CardGeometryValidator` 全通过；`FanCardAcceptanceTests` `22/22`，报告
  `Logs/FanCardDynamicGestureEditModeTests.xml`；共享遥测 `SpinnerProgressionTests` `36/36`，报告
  `Logs/FanCardDynamicGestureTelemetryTests.xml`；原生 Swift 覆盖层 `swiftc -parse` 通过。同步后的主场景
  SHA-256 与隔离验证场景一致。
- shipping-scene 人工预览已检查 top / authored hero / left / right / low / back、轴位特写、独立顶片背轨、
  AAA/QKA 与 0/30/60/90° 状态，文件位于 `Artifacts/FanCardMaterialPreview/`。总控已转达本批在完成真实
  shipping 预览后无需逐项等待视觉确认；当前不是“视觉批准待确认”。本 feature 已随总控唯一 Build 37
  覆盖安装；iPhone 上的质心跟手、快慢手势、音效/Haptic 同帧与实际尺寸仍待真机验收。

## 2026-08-12 Library 左右滑动方向与实时跟手（视觉批准待确认，未推手机）

- 根因是模型顺序方向与投影方向混用了同一符号：切到下一款时，旧模型曾向右退出、新模型从左进入；
  原生 `TabView` 还只在分页提交后通知 Unity，因此拖动中看起来有延迟。现在 SwiftUI 的真实横向
  `translation.width` 会经 `SetLibrarySwipeProgressFromNativeUi` 实时传入
  `SpinnerSceneParallaxController.SetLibraryPageDragProgress`；左滑时当前模型随手指向左移动，右滑镜像。
  提交到下一页后 `FidgetAppCoordinator` 让旧模型继续向左退出，并让新模型从右侧进入；返回上一页反向。
  模型顺序、物理、抽卡和收藏盒配色均未修改，Reduce Motion 继续跳过模型位移动画。
- 精确 Unity shipping 接线专项
  `ProductCoordinatorWiresEnvironmentWithoutEnteringInteractionOrHaptics` 为 `1/1 Passed`，报告为
  `Logs/LibrarySwipeDirectionFix/LibrarySwipeDirectionFocused.xml`。真实 shipping Unity 场景联系表为
  `Artifacts/LibrarySwipeDirectionFix/library-swipe-direction-contact-sheet.png`，逐帧锁定旧模型左退、
  新模型右入；原始关键帧位于同目录 `frames/`。相关差异 `git diff --check` 通过。
- 隔离 iOS Simulator shipping export 与 Xcode IL2CPP Release 构建成功；临时 XCUITest bundle 在
  iPhone 17 Pro / iOS 26.3.1 Simulator 上对真实 `library-model-carousel` 执行完整左滑、右滑，并以
  `PageIndicator` 断言 `page 1 of 6 → page 2 of 6 → page 1 of 6`，最终 `1/1 Passed`、`0 failures`、
  运行 `19.335 s`。摘要、逐测试结果和临时 harness 分别归档为
  `Logs/LibrarySwipeDirectionFix/LibrarySwipeDirectionXcuiTest-summary.json`、
  `LibrarySwipeDirectionXcuiTest-tests.json` 与 `LibrarySwipeDirectionXcuiTest.m`；裁剪后的 8.52 秒实机
  Simulator 录屏和联系表为
  `Artifacts/LibrarySwipeDirectionFix/library-swipe-left-right-simulator.mp4` 与
  `library-swipe-left-right-simulator-contact-sheet.jpg`。
- P0 延迟收口已把原生手势结束后的固定 `0.08 s` 猜测窗口替换为明确的
  `Begin / Commit / End` swipe session。Swift 在同一个 session 内逐帧发送位移，达到提交阈值时先标记
  commit 再请求目标模型；只有未提交的取消/边界 session 才回弹。Unity 的
  `LibrarySwipeSessionGate` 会拒绝旧 session 的 progress、commit 和迟到 End，已提交页不会先回摆再退出。
  模型顺序、物理、Haptic、抽卡和收藏盒没有变化。
- P0 确定性状态机与 shipping 接线专项 `2/2 Passed`，完整 `SpinnerEnvironmentTests` 为
  `10/10 Passed`，分别归档于 `Logs/LibrarySwipeSessionP0/LibrarySwipeSessionFocused.xml` 与
  `SpinnerEnvironmentTests-final.xml`；五个 shipping Swift 文件的 arm64 iPhoneOS 15 type-check 通过，
  日志为 `iPhoneOS-Swift-typecheck.log`。重新导出的 shipping Simulator 工程与 Xcode Release
  build-for-testing 均成功。
- iPhone 17 Pro / iOS 26.3.1 Simulator 对真实 `library-model-carousel` 完成快速左滑、右滑往返，
  `page 1 of 6 → page 2 of 6 → page 1 of 6` 为 `1/1 Passed`、`0 failures`。手势结束到 PageIndicator
  提交的轮询值为左 `0.0135 s`、右 `0.0140 s`；这证明原生提交链不再等待旧 `0.08 s` 定时器，
  不等同于真机触摸硬件延迟。摘要、原始日志、临时 harness、5.91 秒 shipping Simulator 录屏和逐帧表位于
  `Logs/LibrarySwipeSessionP0/` 与 `Artifacts/LibrarySwipeSessionP0/`。
- 当前状态：shipping runtime、本地自动化、真实 shipping GPU 预览和 Simulator 连续手势验收完成；
  仍处于“视觉批准待确认，未推送手机”。只有用户批准本组真实预览/录屏后，才进入统一 iPhone Build；
  真机触摸延迟、跟手性与连续快速往返仍需在手机上验收。

## 2026-09-02 磁吸推牌细节／层距 hybrid rev 14（视觉批准待确认，未推送手机）

- 用户以原话“我感觉明显还是rev 12细节更多吧”否决 Gate 11 rev 13 的表面细节。判断正确：
  rev 13 将 rev 12 authored RGB 压为单一 luminance，改动 mica/microflake 与 roughness 范围，
  motif 层未采样 roughness/normal；透明 cap 以 `2.8 px` 重采样 scene color，进一步压低高频细节。
  rev 12／13 证据均保留为 immutable history。
- rev 14 保留 rev 13 的真实层距：substrate=`-0.28 mm`、motif=`-0.14 mm`、crystal=`0 mm`，
  cap 光学厚度=`0.28 mm`、IOR=`1.52`。上下 albedo、roughness、normal、motif mask 与 perimeter
  mask 直接引用 rev 12 同一 Unity asset；没有复制或重采样。九个 SHA-256 见
  `rev-014-detail-depth-hybrid/unity-hybrid-report.json`。
- substrate 恢复 rev 12 的 authored RGB、mica=`28`、microflake=`85/0.16`、
  roughness=`0.022–0.11`、normal=`0.32`、iridescence=`0.12`。motif 使用独立 LOD0 mask，
  并采样 rev 12 roughness/normal。crystal transmission=`0.985`、refraction=`0.35 px`，
  防止 broad white wash 和 mip blur。
- 同机位 macro 的 hybrid/rev12 对齐红区比值：Laplacian mean=`1.022`、
  local variance=`1.268`、edge density=`0.972`；门限均为 `>=0.95`。rev 13 相同区域
  Laplacian mean 仅为 rev 12 的 `0.535`。clipped fraction=`0.0000444`；microflake
  local difference P90=`0.0123`。
- 15°、`1280×960` macro 投影视差=`4.21 px`，高于 rev 13 `~2.1 px` 目标。外部 bounds
  center/size delta=`0/0 m`；collider identity、protected mechanism/gesture/audio/Haptic hash
  不变；endpoint interlock 合法；side/underside artwork triangles=`0/0`；emission=`0`。
- 移动对照为真实 Unity 各 `150` 帧，组合后 H.264 High、`1920×400`、30 fps、5 s。
  相对 rev 12 仍约增加 `4` draw calls 和一层透明 overdraw；没有手机 GPU timing。
  orbit 的最大逐帧红区覆盖跳变 `<0.02`，没有空白、白化、sorting 或 z-fighting 跳帧。
- 验证：Unity EditMode=`3/3`、PlayMode=`5/5`；focused Node=`1/1`；browser desktop/mobile、
  video/image modal、H.264 全解码、Python/Node syntax、JUnit XML、单模型与全模型 pipeline
  errors/missing/unhashed=`0/0/0`。当前仅为 Gate 11 rev 14 `ready_for_review`。
  Build 44 继续禁止 build／install／phone／App Store。

## 历史：2026-09-02 磁吸推牌真实三层红面 rev 13

- 用户以原话“我还是没看出层次感”否决 Gate 11 rev 12。根因是 rev 12 仍只有一个 opaque surface；
  UV relief、Fresnel 和 BRDF 混合没有真实层距、透明晶体 renderer 或屏幕视差。rev 12 现为 rejected
  history。Build 42 视觉验收失败继续保留，Build 44 仍禁止 build／install。
- rev 13 在上下装饰面各生成三张 cap-only 网格。血红基底内嵌 `0.28 mm`；黑图案内嵌 `0.14 mm`，
  图案视觉厚度暂定 `0.05 mm`；透明晶体 cap 位于原外边界，光学厚度暂定 `0.28 mm`、IOR `1.52`。
  这些数值是 visual estimate，不是生产实测。基底、图案、晶体分别使用独立 URP shader 和 renderer。
- 基底使用上下独立贴图、mica/microflake、roughness/normal 变化和克制角度色移；图案使用独立 mask、
  alpha-test queue `2480` 与 ZWrite；晶体使用 queue `3090`、DepthOnly prepass、透明 forward、
  Fresnel、环境反射和受控屏幕折射。Emission=`0`。上下 cap 的 15° macro 几何投影视差为 `2.10 px`。
- 每个可见面新增 substrate、motif、crystal 三次绘制。相对 rev 12 估算增加约 `4` draw calls，
  并增加一层透明 cap overdraw；未取得 iPhone GPU timing。shader target `3.5`，三个 shader 均无
  compiler error。外部 bounds center/size delta=`0`，collider identity 与 protected runtime hash
  不变；侧壁／底面仍无 artwork。
- 真实 `MeshyEDC.unity` 已输出同机位 rev 12／13、front、15°／30°／60°、side macro、closed、
  max-open、上下 artwork 和 phone 视图。8 秒 H.264 反射移动录屏位于
  `evidence/11-unity-parity/rev-013-true-layers/magnetic-slide-true-layer-reflection-r013.mp4`。
  当前仅为 Gate 11 rev 13 `ready_for_review`；没有 build、sign、install、phone 或 App Store 操作。

## 每次合入的检查方式

1. 在本矩阵中选择目标行；任务开始时不能把 `仅规格` 当作已有能力。
2. 实现代码时让参数只有一个权威来源；其他层读取或由测试验证一致。
3. 为机械状态机写纯函数/Editor tests，为场景连接写 PlayMode 或静态验收测试。
4. iOS native 功能同时检查 capability、engine reset、App 后台、start/update/stop。
5. 自动化通过后更新本矩阵；触感相关项目仍标记 `待真机验收`，直到在支持 Core Haptics 的 iPhone 上完成体验验收。
