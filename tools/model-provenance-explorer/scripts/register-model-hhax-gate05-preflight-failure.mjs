import { loadManifest, saveGenericStageEvidenceRevision } from "../pipeline-core.mjs";

const modelId = "model-hhax";
const base = "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/05-blockout/rev-001";
const upstream = [
  "model-hhax-measurement-modeling-contract-r001",
  "model-hhax-part-tree-r001",
  "model-hhax-exploded-plan-r001",
  "hhax-gate04-architecture-snapshot-r002"
];
const claims = [
  "hhax-claim-product-envelope-r002",
  "hhax-claim-mechanical-linkage-r002",
  "hhax-claim-shell-topology-r002",
  "hhax-claim-service-topology-r002",
  "hhax-claim-three-art-surfaces-r002",
  "hhax-claim-hidden-boundary-r002"
];
const records = [
  ["hhax-gate05-preflight-source-r001", "white-model-source", "model-hhax-white.blend", "source-model", "preflight-white-blend"],
  ["hhax-gate05-preflight-hero-r001", "white-model-hero", "white-model-hero.png", "blender-render", "preflight-white-render"],
  ["hhax-gate05-preflight-closed-r001", "white-model-closed", "white-model-closed.png", "blender-render", "preflight-white-render"],
  ["hhax-gate05-preflight-open-r001", "white-model-open", "white-model-open.png", "blender-render", "preflight-white-render"],
  ["hhax-gate05-preflight-rotation-r001", "white-model-rotation", "white-model-rotation.png", "blender-render", "preflight-white-render"],
  ["hhax-gate05-preflight-glb-r001", "interactive-white-model", "white-model-interactive.glb", "validation", "preflight-interactive-white-model"],
  ["hhax-gate05-preflight-snapshot-r001", "parameter-snapshot", "blockout-parameters.json", "validation", "preflight-parameter-snapshot"]
].map(([id, slot, file, role, contentClass]) => ({
  id, slot, path: `${base}/${file}`, role, contentClass,
  sourceAssetIds: upstream,
  sourceClaimIds: claims,
  description: "白模预检产物；几何与尺寸检查通过，但渲染曝光导致主体不可读，明确不允许进入交互批准。"
}));

const manifest = loadManifest(modelId);
const next = saveGenericStageEvidenceRevision(modelId, "05-blockout", {
  expectedRevision: manifest.revision,
  assets: records,
  validations: [
    { id: "contract-and-architecture-hash-lock", status: "pass", evidence: "生成器读取并核对已批准 Gate 03/04 文件 SHA-256。" },
    { id: "closed-envelope", status: "pass", evidence: "Blender evaluated bounds 为 30.9 × 50.5 × 13.6 mm。" },
    { id: "motion-ownership", status: "pass", evidence: "上壳仅 +Y 直推，背部载体绕自身 +Z 轴旋转。" },
    { id: "white-model-legibility", status: "fail", evidence: "四张白模渲染曝光过高，主体与背景无法可靠分辨；本版本不得审查或批准。" }
  ],
  diagnosis: "Gate 05 首次白模预检的几何通过，但画面不可读；保留失败版本并制作新的不覆盖版本。",
  recipe: "model-hhax Blender 5.2 Gate 05 preflight failure retained for audit"
});

console.log(JSON.stringify({ revision: next.revision, gate05: next.stages[4].status, validations: next.stages[4].validations }, null, 2));
