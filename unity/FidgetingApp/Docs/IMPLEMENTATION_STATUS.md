# Fidgeting Interaction Integration Status

最后更新：2026-08-27

本文件回答一个问题：规格中的能力是否已经进入可运行代码。状态只按代码、场景接线和测试证据填写，不按聊天结论或文档完成度填写。

状态定义：

- `已集成并有测试`：运行时代码、产品接线和自动化测试齐全。
- `部分集成`：已有部分代码或接线，但还缺语义、生命周期、测试或真机环节。
- `仅规格`：只有设计规格，不能对外称为已实现。
- `待真机验收`：自动化能验证结构，但触感仍必须在 iPhone 上确认。

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

> **当前状态：用户原话“可以，然后看看能不能推进 app 里面吧。”视觉已批准。shipping 场景已是这版材质。正在签名安装到已连接 iPhone。真机手感／外观验收仍待用户在手机上确认。**

- 批准对象：2026-08-27 14:03 shipping 预览（hero/top/left/right/low/back/track）。几何、72 段 FBX、弱反射 `0.28`、暖银 smoothness `0.24`。
- 批准预览副本：`Docs/DesignBibleAssets/fan-card-shipping-hero-20260827.png` 等 7 张。
- DecisionState：`FDB-FAN-018/019/020/021` locked and visually approved。DeliveryState：安装进行中；安装成功后为 Installed，不等于 Device Accepted。
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

## 2026-08-27 Premium Display Case Gate 09 批准／Gate 10 rev 1 待审批

> **当前状态：pipeline rev=`68`。Gate 01–09=`approved`；Gate 10 export rev 1=`ready_for_review`；Gate 11+=`blocked`；approved count=`9/12`。视觉批准待确认，未推送手机。**

- 用户选择“环境正确，批准并继续（推荐）”已由 approval event=`04560468-01da-4a1f-8bc8-a324966490d6` 持久化。批准只锁定静态低细节环境方向；无 color cast、detached halo、bright blob、background motion、particle 或 competing detail。Blender 值不自动成为 Unity runtime constants。
- Gate 10 rev 1 event=`d93631b1-61dc-4f8f-8ee5-24e61d38a790`。product-only Blender、Unity-ready FBX 和 portable GLB 保持 `228 × 304 × 59 mm`、Y=`99 mm` 标签、同心圆角、connected tube、`PresentationRoot`／`CaseAssembly`／空 `ContentSlot` hierarchy 与材质 assignment。
- 包含 `12` nodes、`5` meshes、`100,016` triangles。approved Blender geometry digest=`a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951`；round-trip canonical digest=`c4a8e0dbf0bc5825ebc1fe283d2f069ff63826e16a738fdf875a952e8317ee8b`。
- 文件 SHA-256：Blend=`453874ba2edf75fb90449702ef9b50fb059010ee6eefcc2c4e603f034fd0c0eb`；FBX=`21c9db68723f0006d7c6bfec5280cafe55c16cf5392ff97c365c966e91f847ae`；GLB=`fb22fc333c0c5fbc715385ca510dbf0ee4a18b9847f64764b4511e0278ba4df8`。
- Fresh-scene round-trip：FBX／GLB 最大 vertex error=`0.000041788 / 0.000017166 mm`；bounds、hierarchy、material slots、triangle count 与 canonical geometry digest 一致。五个 mesh 的 signed material volume 保持正；FBX／GLB triangulated surface 与 winding digest 一致。
- blank `PhysicalLabel` 保留 `LabelUV 0–1`、paper geometry、transparent-cover／foil contour metadata。placeholder text、fake ID、toy/prize、proxy、exploded、light、halo、particle、VFX、camera、background、runtime timing/easing/Y-Z path/360°/light cues 均未打包。
- 没有已批准 collision／selection proxy，因此未新造碰撞；`collision-policy.json` 明确记录 not applicable。`100,016` triangles 不在 Gate 10 擅自 decimate；Gate 11 Unity profiling 必须验证 60 FPS。
- 评审：`ArtSource/ModelPipeline/premium-display-case/evidence/10-export/rev-001/premium-display-case-product-r001.glb` 与 `export-review.png`。manifest／validation links：同目录 `export-manifest.json`、`validation-links.json`、`export-roundtrip-validation.json`。
- 验证：Blender 5.2.0 LTS build、FBX/GLB fresh-scene round-trip、GLB structure、三格式整盒 render、QA、Python/Node syntax、focused Premium Display Case test=`1/1 passed`。Model validator rev=`68`、approved=`9/12`、earliest=`10-export ready_for_review`、errors／missingFiles／unhashed=`0/0/0`；全 pipeline validator无 schema、missing file 或 unhashed 错误。
- 全 Model Provenance Explorer=`112/113 passed`。唯一失败属于并发 Magnetic Slide Tile fixture：测试期待 artifact count `63`，live state 为 `64`；本任务未修改该模型。
- DeliveryState：Gate 09 决策和 Gate 10 export evidence 已完成；Gate 10 尚未视觉批准。shipping Unity、Simulator、build、install 和 phone 均未触碰。视觉批准待确认，未推送手机。

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

## 每次合入的检查方式

1. 在本矩阵中选择目标行；任务开始时不能把 `仅规格` 当作已有能力。
2. 实现代码时让参数只有一个权威来源；其他层读取或由测试验证一致。
3. 为机械状态机写纯函数/Editor tests，为场景连接写 PlayMode 或静态验收测试。
4. iOS native 功能同时检查 capability、engine reset、App 后台、start/update/stop。
5. 自动化通过后更新本矩阵；触感相关项目仍标记 `待真机验收`，直到在支持 Core Haptics 的 iPhone 上完成体验验收。
