export const PIPELINE_SCHEMA_VERSION = 1;

export const STAGES = Object.freeze([
  {
    id: "01-intake",
    number: 1,
    short: "参考",
    title: "原始参考归档",
    description: "保存用户原图、视频帧、来源、原始哈希和联系表；AI 目标图必须单独标记。",
    requiredSlots: ["original-reference"]
  },
  {
    id: "02-analysis",
    number: 2,
    short: "分析",
    title: "参考分析",
    description: "核对全部来源、写入机构证据合同并批准结构交互 CAD。Gate 03–04 与真实物理尺寸完成后进入 Blender；独立手感 Simulator 不是前置门禁。",
    requiredSlots: ["discovery-log", "analysis-board"]
  },
  {
    id: "03-contract",
    number: 3,
    short: "规格",
    title: "建模合同",
    description: "锁定单位、尺寸、bounds、坐标、pivot、运动件、间隙、预算与生成路线。",
    requiredSlots: ["modeling-contract"]
  },
  {
    id: "04-architecture",
    number: 4,
    short: "拆件",
    title: "拆件与爆炸规划",
    description: "确认零件树、装配关系、运动方向、材质分区与爆炸目标。",
    requiredSlots: ["part-tree", "exploded-plan"]
  },
  {
    id: "05-blockout",
    number: 5,
    short: "白模",
    title: "Blender 白模 Blockout",
    description: "由确定性脚本或 CLIAnything 场景生成无材质白模，先确认轮廓、比例和厚度。",
    requiredSlots: ["white-model-source", "white-model-hero"]
  },
  {
    id: "06-geometry",
    number: 6,
    short: "几何",
    title: "几何验收",
    description: "同源六视图、Workbench、尺寸/Pivot 覆盖和爆炸图共同验证几何。",
    requiredSlots: [
      "view-front", "view-back", "view-top", "view-bottom", "view-left", "view-right",
      "workbench", "dimension-overlay", "pivot-overlay", "exploded-geometry"
    ]
  },
  {
    id: "07-material",
    number: 7,
    short: "材质",
    title: "材质 Lookdev",
    description: "在中性灯光下检查 PBR 通道、分件边界与表面近景。",
    requiredSlots: ["material-board", "material-closeup"]
  },
  {
    id: "08-lighting",
    number: 8,
    short: "灯光",
    title: "灯光与渲染层",
    description: "审批 Hero、左右斜视、低角及 Beauty/Clay/Normal/Depth/Roughness 检查层。",
    requiredSlots: [
      "hero", "left-oblique", "right-oblique", "low-angle",
      "pass-beauty", "pass-clay", "pass-normal", "pass-depth", "pass-roughness"
    ]
  },
  {
    id: "09-environment",
    number: 9,
    short: "环境",
    title: "环境合成",
    description: "同相机比较中性场景与目标环境，分离模型问题和环境污染。",
    requiredSlots: ["neutral-environment", "shipping-environment"]
  },
  {
    id: "10-export",
    number: 10,
    short: "导出",
    title: "导出包",
    description: "验证 Blend、FBX、GLB、Collision、单位、层级、材质槽、法线、Pivot 与哈希。",
    requiredSlots: ["blend-source", "fbx-export", "glb-export", "collision-export", "export-manifest"]
  },
  {
    id: "11-unity-parity",
    number: 11,
    short: "对齐",
    title: "Unity 对齐",
    description: "用相同相机比较 Blender 与中性 Unity，验证 bounds、轴心、碰撞、材质和比例。",
    requiredSlots: ["blender-neutral", "unity-neutral", "parity-report"]
  },
  {
    id: "12-shipping",
    number: 12,
    short: "成品",
    title: "真实 Shipping / 手机构图",
    description: "正式场景完成 Library、Hero、Top、左右斜视、Low 与 Phone；批准后才允许安装。",
    requiredSlots: [
      "shipping-library", "shipping-hero", "shipping-top", "shipping-left-oblique",
      "shipping-right-oblique", "shipping-low", "shipping-phone"
    ]
  }
]);

export const STAGE_BY_ID = new Map(STAGES.map((stage) => [stage.id, stage]));
export const ALLOWED_STAGE_STATUSES = new Set([
  "missing", "blocked", "draft", "ready_for_review", "approved", "rejected", "stale", "legacy"
]);
export const ALLOWED_ASSET_ROLES = new Set([
  "user-input", "external-reference", "ai-target", "analysis", "contract", "process", "source-model",
  "export", "blender-render", "unity-render", "shipping-render", "validation", "historical"
]);

export const MODEL_GATE_APPROVAL_REQUIREMENTS = Object.freeze({
  "01-intake": "interactive-source-inspector-or-complete-recording",
  "02-analysis": "reference-research-then-interactive-cad-approval",
  "03-contract": "source-linked-contract-and-explicit-user-decision",
  "04-architecture": "approved-cad-migration-or-interactive-3d",
  "05-blockout": "interactive-3d-or-complete-turntable-recording",
  "06-geometry": "interactive-3d-or-complete-turntable-recording",
  "07-material": "interactive-lookdev-or-real-turntable-recording",
  "08-lighting": "interactive-lookdev-or-real-comparison-recording",
  "09-environment": "interactive-lookdev-or-real-comparison-recording",
  "10-export": "real-glb-interaction",
  "11-unity-parity": "real-unity-runtime-preview-or-complete-recording",
  "12-shipping": "real-unity-runtime-preview-or-complete-recording"
});

export const MECHANICAL_GATE02_SEQUENCE = Object.freeze([
  "reference-research",
  "interactive-structural-cad",
  "interactive-cad-subapproval-record",
  "separate-hand-feel-simulator",
  "interactive-simulator-approval-record",
  "blender-and-later-gates"
]);

export function createEmptyStages() {
  return STAGES.map((stage) => ({
    id: stage.id,
    revision: 1,
    status: stage.number === 1 ? "draft" : "blocked",
    artifactIds: [],
    inputDigest: null,
    outputDigest: null,
    validations: [],
    decision: null,
    approvalRequirement: MODEL_GATE_APPROVAL_REQUIREMENTS[stage.id]
  }));
}
