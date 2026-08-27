export const pipelineConfig = [
  {
    id: "magnetic-slide-tile",
    name: "磁吸推牌",
    productId: "magnetic-slide-tile",
    status: "current",
    statusLabel: "正式模型 · 建议重做外观",
    summary: "输入最完整的一条链：实拍与专利结构 → 参数化六视图/爆炸概念 → Meshy 与 Unity 材质、布光、内部结构验证。",
    diagnosis: "机构资料充足，但现模型的表面语言过于繁杂、磁体暴露感强，亮银高光也容易读成廉价镀铬。重做时应保留六档机构与真实行程，只重做外壳比例、分件、倒角与材质。",
    rebuildFocus: ["先锁定原创轮廓和真实厚度", "保留六档磁吸与 13.6 mm 中心距", "减少装饰槽，明确金属/树脂分区", "从正交图建模，不从透视宣传图量尺寸"],
    stages: {
      input: [
        { label: "推牌实拍、产品与专利参考包", folder: "unity/FidgetingApp/Docs/References/PushCardModeling", recursive: false, kinds: ["image"], note: "22 张关键参考 + 1 张联系表；用于尺度、握持、层级和材质。" },
        { label: "专利拆解线框", folder: "unity/FidgetingApp/Docs/References/PushCardModeling/ExplodedWireframes", kinds: ["image"], note: "9 张结构裁图 + 联系表；只推断层级和爆炸方向。" },
        { label: "早期 EDC 多角度输入", folder: "Artifacts/EDC", recursive: false, kinds: ["image"], match: "^Source_", note: "侧、顶、端面等输入视图。" },
        { label: "KOVO / Matrix / Clean EDC 分析板", folder: "assets/3d-analysis/2026-08-01", recursive: false, kinds: ["image"], match: "^(02|03|04)-", note: "对推滑姿态、形体与材质的研究。" }
      ],
      process: [
        { label: "同源参数化六视图", folder: "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts/02_parametric_consistent_views", kinds: ["image", "document"], note: "爆炸、顶、正、背、左、右由同一确定性几何生成。" },
        { label: "旧 ImageGen 五视图", folder: "unity/FidgetingApp/Docs/References/PushCardModeling/GeneratedConcepts", recursive: false, kinds: ["image", "document"], match: "^01_pushcard", state: "superseded", note: "左右视角和顶板不一致，已被参数化六视图取代。" },
        { label: "磁吸 EDC 爆炸概念 V1–V4", folder: "Artifacts/EDC", recursive: false, kinds: ["image"], match: "^CardMagneticFidget_", note: "从通用卡片结构逐步收敛到三层分件。" },
        { label: "网格减面与法线验证", folder: "Artifacts/EDC/OptimizationValidation", kinds: ["image", "document"], note: "不同三角面预算、Unity 金属材质和重算法线对照。" },
        { label: "实际 3D 源与导出", folder: "unity/FidgetingApp/Assets/_EDC", kinds: ["model"], note: "Meshy 输入、清理网格与优化导出。" }
      ],
      output: [
        { label: "Unity 最终/设备构图帧", folder: "Artifacts/EDC", recursive: false, kinds: ["image"], match: "^Final_", note: "开合、侧面、顶面和 iPhone 纵向构图。" },
        { label: "Unity 材质与布光迭代", folders: ["Artifacts/EDC/DiffusedLighting_2026-08-09", "Artifacts/EDC/PolishedFineMetal_2026-08-09", "Artifacts/EDC/ResinMetalContrast_2026-08-09", "Artifacts/EDC/BroaderSofterHighlights_2026-08-09", "Artifacts/EDC/PreviewSizeAndCaptureFix_2026-08-09"], kinds: ["image"], note: "Library、Hero、左右斜角、Top、Low 和内部打开视角。" },
        { label: "恢复与批准候选", folder: "Artifacts/RecoveryApprovalV22", kinds: ["image"], matchPath: "magnetic-slide", note: "真实 shipping 场景五角度与 Hero 联系表。" },
        { label: "设计圣经批准证据", folder: "unity/FidgetingApp/Docs/DesignBibleAssets", kinds: ["image"], match: "^magnetic-slide", state: "approved", note: "当前只批准对应材质与柔光语言。" },
        { label: "Premium Display Case 中的全部推牌帧", folder: "unity/FidgetingApp/Artifacts", kinds: ["image"], matchPath: "PremiumDisplayCase.*magnetic-slide-tile", note: "展示盒、铭牌、灯光和比例的各轮 Unity 输出。" }
      ]
    }
  },
  {
    id: "magnetic-fan-card",
    name: "磁吸扇牌",
    productId: "magnetic-fan-card",
    status: "current",
    statusLabel: "正式模型 · 结构受 guardrail 锁定",
    summary: "推牌/卡牌机构参考 → 扇牌爆炸概念 → Blender 背面实体轨道与磁体 → Unity 正背面、四档运动和牌面输出。",
    diagnosis: "当前结构数据比外观可靠。重做不能破坏右下轴心、三片尺寸、轨道边界和磁体数量；优先重做牌面比例、边框、金属粗糙度与 artwork。",
    rebuildFocus: ["保留 63.5 × 88.9 × 2.5 mm 单片尺寸", "保留右下轴心与 0/45/90° 展开", "后轨完整外轮廓距牌边 ≥ 6 mm", "正面去掉廉价镜面与多余轴圈"],
    stages: {
      input: [
        { label: "Lautie 三层卡牌与磁体参考", folder: "unity/FidgetingApp/Docs/References/PushCardModeling", recursive: false, kinds: ["image"], match: "^(18|19|20|21)_", note: "三层机身、动作序列、层移除和磁体细节。" },
        { label: "扇牌概念输入", folder: "Artifacts/EDC", recursive: false, kinds: ["image"], match: "FanExploded|ThreeLayerExploded", note: "卡片扇开和三层爆炸的早期视觉目标。" },
        { label: "冻结建模合同", files: ["unity/FidgetingApp/Docs/FanCardModelingGuardrails.md", "unity/FidgetingApp/ArtSource/FanCard/fan_card_guardrails.json"], kinds: ["document"], state: "locked", note: "重做必须从这些尺寸和坐标出发。" }
      ],
      process: [
        { label: "Blender 背面机构预览", folder: "Artifacts/FanCardBlenderPreview", kinds: ["image"], note: "实体网孔、弧形暗槽和磁体可见性。" },
        { label: "几何门禁对照", folder: "Artifacts/FanCardGeometryValidation", kinds: ["image"], note: "低角、侧面和六视图的几何回归证据。" },
        { label: "Blender 源与发布网格", files: ["unity/FidgetingApp/ArtSource/FanCard/FanCardBackMechanism.blend", "unity/FidgetingApp/Assets/_FanCard/Models/FanCardBackMechanism.fbx"], kinds: ["model"], state: "locked", note: "当前可复现源和 Unity 发布网格。" }
      ],
      output: [
        { label: "Unity shipping 多角度/运动/特写", folder: "Artifacts/FanCardMaterialPreview", kinds: ["image"], note: "Top、Hero、左右斜角、Low、Back、Side、0/30/60/90° 与结构特写。" },
        { label: "原生目录页预览", folder: "Artifacts/FanCardNativeCatalogPreview", kinds: ["image"], note: "第六页原生目录中的真实模型。" },
        { label: "设计圣经批准联系表", files: ["unity/FidgetingApp/Docs/DesignBibleAssets/fan-card-approved-contact-sheet.png"], kinds: ["image"], state: "approved", note: "当前批准的呈现证据。" },
        { label: "Premium Display Case 中的全部扇牌帧", folder: "unity/FidgetingApp/Artifacts", kinds: ["image"], matchPath: "PremiumDisplayCase.*magnetic-fan-card", note: "展示盒内六角度及多轮铭牌/灯光输出。" }
      ]
    }
  },
  {
    id: "metal-three-blade",
    name: "三叶金属",
    productId: "metal-three-blade",
    status: "current",
    statusLabel: "正式模型 · 建议重做造型",
    summary: "正交/爆炸参考与材质分析 → Blender 三叶模型及轴心修复 → Unity 柔光、皮肤、贴纸与展示盒多角度。",
    diagnosis: "当前版本经历过多次轴心、轴圈、材质和贴纸修补，说明基础轮廓与中心结构没有一次解决。重做时应先冻结 silhouette、厚度和真实机械轴，再做皮肤。",
    rebuildFocus: ["先重做三叶过渡与中心轴承层级", "所有动态件围绕唯一机械原点", "取消悬浮轴圈与装饰配重", "皮肤只改变表面，不改变几何"],
    stages: {
      input: [
        { label: "三叶 Rotor 五视图与爆炸参考", folder: "unity/FidgetingApp/Docs/ModelingReferences", kinds: ["image"], note: "四套正交/爆炸目标图。" },
        { label: "三叶形体、爆炸与材质分析板", folder: "assets/3d-analysis/2026-08-01", recursive: false, kinds: ["image"], match: "^(01|05|06|07|08|09|10)-", note: "形体、镜头、PBR 分区和棚拍灯光。" }
      ],
      process: [
        { label: "早期 Blender 多角度与爆炸图", folder: "Artifacts", recursive: false, kinds: ["image"], match: "^three-blade-edc", note: "Hero、Top、Side、左右斜角和爆炸。" },
        { label: "Blender 结构预览", folder: "unity/FidgetingApp/Artifacts/BlenderThreeBlade", kinds: ["image"], note: "Blender 生成结果与结构检查。" },
        { label: "转子轴心修复两轮", folders: ["unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisFix", "unity/FidgetingApp/Artifacts/ThreeBladeRotorAxisCenterV2"], kinds: ["image"], note: "修复转子、轴承外圈和固定指盖同轴。" },
        { label: "十档金属皮肤", folder: "Artifacts/ThreeBladeMetalSkins", kinds: ["image"], note: "雾银、枪灰、夜航、钨金、冰银、蓝钢、赤铜、钛虹、黑曜、镜铬。" },
        { label: "三叶 Blender/Unity 模型文件", folders: ["unity/FidgetingApp/ArtSource/ThreeBladeSpinner", "unity/FidgetingApp/Assets/_Fidgeting/Models/BlenderThreeBlade"], kinds: ["model"], note: "可编辑源和 Unity 导出。" }
      ],
      output: [
        { label: "Unity 柔光 shipping 预览", folder: "unity/FidgetingApp/Artifacts/SpinnerSoftLightingPreview", kinds: ["image"], note: "模型在正式场景中的多角度和联系表。" },
        { label: "轴圈移除后的 Unity 预览", folder: "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/metal-three-blade", kinds: ["image"], note: "Hero、Top、左右斜角、Low、Phone。" },
        { label: "恢复批准候选", folder: "Artifacts/RecoveryApprovalV22", kinds: ["image"], matchPath: "metal-three-blade", note: "五角度与 Hero。" },
        { label: "贴纸角度验证 V20/V21", folders: ["unity/FidgetingApp/Artifacts/Stickers/AnglePreviewV20", "unity/FidgetingApp/Artifacts/Stickers/AnglePreviewCenteredV21"], kinds: ["image"], note: "图形、文字、细线贴纸在多角度下的共形表现。" },
        { label: "Premium Display Case 中的全部三叶金属帧", folder: "unity/FidgetingApp/Artifacts", kinds: ["image"], matchPath: "PremiumDisplayCase.*metal-three-blade", note: "展示盒各轮 Unity 输出。" }
      ]
    }
  },
  {
    id: "gold-four-wing",
    name: "镜钢四翼",
    productId: "gold-four-wing",
    status: "current",
    statusLabel: "正式模型 · 输入溯源不足",
    summary: "项目内缺少独立外部参考包；现有链条主要从导入模型直接进入 Unity，再反复修复轴心、轴圈、材质和展示比例。",
    diagnosis: "这是典型的“有结果、缺输入依据”。重新生成前应补齐正交轮廓、侧面厚度、中心机构和真实尺寸参考，否则会继续依赖旧模型修补。",
    rebuildFocus: ["补齐正/背/侧/顶正交参考", "锁定 85 mm 真实直径", "明确四翼而不是三翼的轮廓读法", "控制镜钢高光，避免白色剪切"],
    stages: {
      input: [
        { label: "当前仅存的导入模型 Hero", folder: "Artifacts/ImportedSpinner", kinds: ["image"], note: "没有发现对应的完整外部正交参考包。" },
        { label: "导入模型与纹理", folder: "unity/FidgetingApp/Assets/_ImportedSpinner", kinds: ["model", "image"], note: "现有几何与材质的直接来源。" }
      ],
      process: [
        { label: "恢复批准多角度", folder: "Artifacts/RecoveryApprovalV22", kinds: ["image"], matchPath: "gold-four-wing", note: "Hero、Top、Left、Right、Low 和联系表。" },
        { label: "轴圈移除验证", folder: "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/gold-four-wing", kinds: ["image"], note: "移除额外 crown/bezel 后的 Unity 多视角。" },
        { label: "成长阶段材质图", folder: "Artifacts/ProgressionVisuals", kinds: ["image"], matchPath: "gold-four-wing", note: "等级材质变化，不代表新几何。" }
      ],
      output: [
        { label: "Premium Display Case 中的全部四翼帧", folder: "unity/FidgetingApp/Artifacts", kinds: ["image"], matchPath: "PremiumDisplayCase.*gold-four-wing", note: "各轮 Hero/Top/斜角/Low/Phone 输出。" },
        { label: "批准展示盒材质证据", folder: "unity/FidgetingApp/Docs/DesignBibleAssets", kinds: ["image"], match: "^collector-slab", state: "approved", note: "批准的是展示比例和材质响应，不是新的四翼几何。" }
      ]
    }
  },
  {
    id: "graphite-two-lobe",
    name: "石墨双叶",
    productId: "graphite-two-lobe",
    status: "current",
    statusLabel: "正式模型 · 参考链较清晰",
    summary: "独立结构参考 → 一体转子/凹面指盖/轴承爆炸 → Unity 真实比例与轴圈修复 → 展示盒输出。",
    diagnosis: "现模型的问题主要不是机构，而是过于简单、容易读成普通塑料条。重做应增强精密倒角、侧壁分件和表面细节，同时保持 50 mm 小体量。",
    rebuildFocus: ["保持约 50 × 24 × 18.68 mm", "一体双叶转子与固定指盖同轴", "增加可制造的边缘层次而非装饰圈", "保持石墨/珠砂金属而非纯黑塑料"],
    stages: {
      input: [
        { label: "双叶结构参考五张", folder: "unity/FidgetingApp/Artifacts/TwoLobeBar/ModelReferenceSeparate", kinds: ["image"], note: "装配、转子、指盖、轴承/套筒和完整爆炸。" }
      ],
      process: [
        { label: "结构校正与爆炸概念", folder: "unity/FidgetingApp/Artifacts/TwoLobeBar", recursive: false, kinds: ["image"], note: "校正结构、爆炸图和 Hero。" },
        { label: "真实尺度修复", folder: "unity/FidgetingApp/Artifacts/GraphiteTwoLobePhysicalScaleFix", kinds: ["image"], note: "用 50/85 比例修复 Library/详情 framing。" },
        { label: "轴圈移除验证", folder: "unity/FidgetingApp/Artifacts/SpinnerAxisTrimRemovalPreview/graphite-two-lobe", kinds: ["image"], note: "清除额外可见轴圈后的多视角。" }
      ],
      output: [
        { label: "恢复批准候选", folder: "Artifacts/RecoveryApprovalV22", kinds: ["image"], matchPath: "graphite-two-lobe", note: "Hero、Top、Left、Right、Low 与联系表。" },
        { label: "Premium Display Case 中的全部双叶帧", folder: "unity/FidgetingApp/Artifacts", kinds: ["image"], matchPath: "PremiumDisplayCase.*graphite-two-lobe", note: "展示盒中的多轮真实 Unity 输出。" },
        { label: "批准展示盒材质证据", folder: "unity/FidgetingApp/Docs/DesignBibleAssets", kinds: ["image"], match: "^collector-slab", state: "approved", note: "当前批准的喷砂/磨砂金属响应。" }
      ]
    }
  },
  {
    id: "blue-classic",
    name: "经典蓝色",
    productId: "blue-classic",
    status: "current",
    statusLabel: "正式模型 · 溯源缺口最大",
    summary: "项目中保留正式 Unity 场景、缩略图和成长/环境输出，但没有找到与其他模型同等级的输入参考、爆炸图和 Blender 多角度链。",
    diagnosis: "如果准备重新生成，不能只拿现有缩略图反推。应先补一套真实尺寸、中心轴承、指盖、三叶厚度与背面结构参考。",
    rebuildFocus: ["新增五视图与轴向爆炸输入", "保留最易理解的经典三叶身份", "明确蓝色金属而非蓝色塑料", "与正式触控/轴心系统保持一致"],
    stages: {
      input: [
        { label: "输入参考缺失说明", files: ["unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"], kinds: ["document"], note: "目前主要依赖设计圣经中的产品约束，没有专属图片参考包。" }
      ],
      process: [
        { label: "成长阶段输出", folder: "Artifacts/ProgressionVisuals", kinds: ["image"], matchPath: "blue-classic", note: "不同等级材质/环境呈现。" },
        { label: "旧环境集成图", folder: "Artifacts/EnvironmentIntegration", kinds: ["image"], matchPath: "blue-classic", note: "模型在场景中的构图，不是建模输入。" }
      ],
      output: [
        { label: "原生模型缩略图", folder: "unity/FidgetingApp/Assets/Plugins/iOS/Thumbnails/Models", kinds: ["image"], matchPath: "blue", note: "目录使用的小尺寸输出。" },
        { label: "分模型壁纸与环境输出", folders: ["unity/FidgetingApp/Assets/Plugins/iOS/SceneWallpapers", "unity/FidgetingApp/Artifacts/AdaptiveBackdropPreview"], kinds: ["image"], matchPath: "blue-classic", note: "当前环境中的模型呈现。" }
      ]
    }
  },
  {
    id: "dragon-scale-edc",
    name: "龙鳞 EDC",
    productId: "candidate-dragon-scale",
    status: "candidate",
    statusLabel: "候选模型 · 不应新增第七槽位",
    summary: "Novo 实物视频帧 → 生成四视图 → Rodin 原始网格/Blender cleanup/CLIAnything 重建 → Unity shipping 候选和轴心修复。",
    diagnosis: "这是输入到输出最容易直观看出“形似但不够精密”的一条链。当前生成结果的翼片厚度、中心盖尺度、切面节奏与真实参考仍有明显差异。",
    rebuildFocus: ["以实物视频的掌中尺度和侧厚为主", "同一份 CAD-like 基础生成所有视图", "中心盖不要过大遮住翼片根部", "保留切面语言但减少 AI 融化边缘"],
    stages: {
      input: [
        { label: "Novo Dragon Scale 实物视频帧", folder: "unity/FidgetingApp/Docs/References/NovoDragonScaleVideoFrames", kinds: ["image"], note: "掌中尺度、正面、中心切面、握持、侧面和平衡。" }
      ],
      process: [
        { label: "生成的龙鳞四视图", folder: "Artifacts/龙鳞EDC_四视图", kinds: ["image"], note: "基础灰银与金色点缀两组；作为目标图而非制造图。" },
        { label: "Rodin raw / Blender cleanup 对照", folder: "unity/FidgetingApp/Artifacts/BlenderDragonScale", kinds: ["image"], note: "原始、Blender 和 cleanup 三阶段多角度对照。" },
        { label: "可编辑源与导出", folder: "unity/FidgetingApp/ArtSource/DragonScaleEDC", kinds: ["model"], note: "Rodin、CLIAnything 与手工清理版本。" }
      ],
      output: [
        { label: "CLIAnything 多角度与爆炸", folder: "unity/FidgetingApp/Artifacts/DragonScaleEDC_CLIAnything", kinds: ["image"], note: "Hero、Top、左右斜角、Low、Side、Exploded。" },
        { label: "Unity shipping 候选", folder: "unity/FidgetingApp/Artifacts/DragonScaleCLIShippingPreview", kinds: ["image"], note: "正式场景中的多角度输出。" },
        { label: "轴心居中修复", folder: "unity/FidgetingApp/Artifacts/DragonScaleAxisCenterFix", kinds: ["image"], note: "修复中心 pivot 后的六视角。" }
      ]
    }
  },
  {
    id: "unbound-slider",
    name: "Unbound Slider",
    productId: "rejected-unbound-slider",
    status: "rejected",
    statusLabel: "已拒绝候选 · 可借鉴流程",
    summary: "共享推牌输入 → 两轮白模和细节设计 → CLIAnything 重建 → Unity Round 5；最终 shipping 预览已明确拒绝。",
    diagnosis: "白模阶段暴露了主要问题：两排外露圆件过多、正面像控制面板、层级厚重，缺少真正高级 EDC 的克制与机械可信度。",
    rebuildFocus: ["不要复用 Round 5 外观", "可保留分层/爆炸工作流", "减少外露磁体和装饰孔", "重新定义拇指接触面与滑动方向"],
    stages: {
      input: [
        { label: "共享的 KOVO / Matrix / 专利参考", folder: "unity/FidgetingApp/Docs/References/PushCardModeling", recursive: false, kinds: ["image"], match: "^(01|02|03|04|05|06|07|08|09|10|11|12|13|14|15)_", note: "外轮廓、掌中尺度、层级、轨道与磁体。" }
      ],
      process: [
        { label: "第一轮白模六视图", folder: "Artifacts/UnboundSlider/WhiteModel_2026-08-10", kinds: ["image"], note: "装配、爆炸、正视、斜角、Low、Top。" },
        { label: "第二轮细节白模", folder: "Artifacts/UnboundSlider/WhiteModel_2026-08-11", kinds: ["image"], note: "细节 Hero、正面图案与装饰版本。" },
        { label: "CLIAnything 多角度/爆炸/开合", folder: "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything", recursive: false, kinds: ["image"], note: "重建后的 9 张结构输出。" },
        { label: "Blender/FBX/GLB 源", folder: "unity/FidgetingApp/ArtSource/UnboundSlider/CLIAnything", kinds: ["model", "image"], note: "可编辑源、碰撞和纹理。" }
      ],
      output: [
        { label: "Unity shipping Round 5（已拒绝）", folder: "unity/FidgetingApp/Artifacts/UnboundSliderCLIAnything/UnityShippingRejected_Round5_2026-08-11", kinds: ["image", "document"], state: "rejected", note: "Library、Hero、左右斜角、Top、Low 和内部打开视角。" }
      ]
    }
  },
  {
    id: "pointed-three-blade",
    name: "尖角三叶 / Edge Triad",
    productId: "historical-pointed-three-blade",
    status: "historical",
    statusLabel: "历史 catalog 候选",
    summary: "Meshy/导入模型 → 单张 Hero → Recovery 多角度 → Cyberpunk 与 Premium Display Case 大量实际 Unity 输出。",
    diagnosis: "图像很多，但建模输入很少；尖锐多边形轮廓在小尺寸下显得生硬。它还与设计圣经中的 blue-classic 首槽位存在 catalog 身份混用。",
    rebuildFocus: ["先决定是否保留此 catalog 身份", "不要从场景截图反推网格", "补齐背面、厚度与轴承结构", "若淘汰，应清理展示盒中的历史命名"],
    stages: {
      input: [
        { label: "Meshy 导入资产", folder: "unity/FidgetingApp/Assets/MeshyImports/Faceted Triad Emblem_20260803_213257", kinds: ["image", "model"], note: "当前能追溯到的生成输入/网格和纹理。" }
      ],
      process: [
        { label: "导入模型 Hero", folder: "Artifacts/ImportedSpinner", kinds: ["image"], note: "早期透明背景/独立 Hero。" },
        { label: "Recovery 五角度", folder: "Artifacts/RecoveryApprovalV22", kinds: ["image"], matchPath: "pointed-three-blade", note: "Hero、Top、Left、Right、Low 和联系表。" }
      ],
      output: [
        { label: "Cyberpunk V5–V13 Unity 输出", folder: "unity/FidgetingApp/Artifacts", kinds: ["image"], matchPath: "CyberpunkEnvironmentUnityPreviewV(5|6|7|8|9|10|11|12|13)", note: "九轮场景中的多角度真实模型；主要验证场景，不等于几何批准。" },
        { label: "Premium Display Case 中的全部尖角三叶帧", folder: "unity/FidgetingApp/Artifacts", kinds: ["image"], matchPath: "PremiumDisplayCase.*pointed-three-blade", note: "展示盒各轮 Unity 输出。" },
        { label: "批准展示盒六产品总览中的 Edge Triad", files: ["unity/FidgetingApp/Docs/DesignBibleAssets/collector-slab-six-products-approved.png"], kinds: ["image"], state: "approved", note: "只表示该展示总览曾被批准；catalog 身份仍需与 blue-classic 统一。" }
      ]
    }
  },
  {
    id: "premium-display-case",
    name: "Premium Display Case",
    productId: "premium-display-case",
    status: "current",
    statusLabel: "正式展示容器 · 可独立重做",
    summary: "Blender 展示盒结构 → 爆炸/灯光/材质 → 六款玩具在统一 content slot 中的 Hero、Top、斜角、Low 与 Phone 输出。",
    diagnosis: "它不是玩具本体，但会显著放大模型的丑点。重新做玩具时应保留统一 content slot 和真实 bounds framing，避免为每款模型单独造假尺寸。",
    rebuildFocus: ["保留一个统一 prefab 与 content slot", "模型占可见舱宽约 68–72%", "盒体材质退后，让玩具成为主角", "铭牌与稀有度不能遮挡真实几何"],
    stages: {
      input: [
        { label: "展示盒 Blender 源", folder: "unity/FidgetingApp/ArtSource/DisplayCase", kinds: ["model"], note: "统一展示容器的可编辑源。" },
        { label: "CLI Trinity Case 源", folder: "unity/FidgetingApp/ArtSource/CliAnythingTrinityCase", kinds: ["model", "image"], note: "另一条展示壳体实验链。" }
      ],
      process: [
        { label: "Blender 多角度", folder: "unity/FidgetingApp/Artifacts/PremiumDisplayCaseBlenderPreview", kinds: ["image"], note: "展示盒本体的 Hero、正交和斜角。" },
        { label: "结构爆炸", folder: "unity/FidgetingApp/Artifacts/PremiumDisplayCaseExploded", kinds: ["image"], note: "上盖、铭牌、舱体与底座层级。" },
        { label: "灯光与材质调色板", folder: "unity/FidgetingApp/Artifacts/PremiumDisplayCaseLightingPalettePreview", kinds: ["image"], note: "不同材质与灯光响应。" }
      ],
      output: [
        { label: "全部 Premium Display Case 预览", folder: "unity/FidgetingApp/Artifacts", kinds: ["image"], matchPath: "PremiumDisplayCase", note: "包含全部模型、Badge、Laser、识别、基线一致性和材质迭代。" },
        { label: "设计圣经批准证据", folder: "unity/FidgetingApp/Docs/DesignBibleAssets", kinds: ["image"], match: "^(collector-slab|premium-display-case)", state: "approved", note: "六产品、三款材质和推牌展示盒批准图。" }
      ]
    }
  }
];

export const stageMeta = {
  input: { number: "01", title: "你的 Input", short: "输入", description: "实拍、专利、正交图、视频帧与锁定规格" },
  process: { number: "02", title: "中间 Process", short: "过程", description: "分析板、概念图、爆炸图、Blender/CLI 与验证" },
  output: { number: "03", title: "Unity Output", short: "输出", description: "shipping 场景、材质、构图、批准或拒绝证据" }
};
