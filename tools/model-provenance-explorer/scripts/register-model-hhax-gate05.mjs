import { loadManifest, saveGenericStageEvidenceRevision } from "../pipeline-core.mjs";

const modelId = "model-hhax";
const base = "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/05-blockout/rev-003";
const upstream = [
  "model-hhax-measurement-modeling-contract-r001",
  "model-hhax-part-tree-r001",
  "model-hhax-exploded-plan-r001",
  "hhax-gate04-architecture-snapshot-r002"
];
const claims = [
  "hhax-claim-product-envelope-r002", "hhax-claim-mechanical-linkage-r002",
  "hhax-claim-shell-topology-r002", "hhax-claim-service-topology-r002",
  "hhax-claim-three-art-surfaces-r002", "hhax-claim-hidden-boundary-r002"
];
const records = [
  ["hhax-gate05-white-source-r003", "white-model-source", "model-hhax-white.blend", "source-model", "deterministic-white-model-source"],
  ["hhax-gate05-white-hero-r003", "white-model-hero", "white-model-hero.png", "blender-render", "white-model-open-hero"],
  ["hhax-gate05-white-closed-r003", "white-model-closed", "white-model-closed.png", "blender-render", "white-model-closed-view"],
  ["hhax-gate05-white-open-r003", "white-model-open", "white-model-open.png", "blender-render", "white-model-full-travel-view"],
  ["hhax-gate05-white-rotation-r003", "white-model-rotation", "white-model-rotation.png", "blender-render", "white-model-rear-carrier-pose"],
  ["hhax-gate05-white-glb-r003", "interactive-white-model", "white-model-interactive.glb", "validation", "interactive-white-model"],
  ["hhax-gate05-white-snapshot-r003", "parameter-snapshot", "blockout-parameters.json", "validation", "blockout-parameter-snapshot"]
].map(([id, slot, file, role, contentClass]) => ({
  id, slot, path: `${base}/${file}`, role, contentClass,
  sourceAssetIds: upstream,
  sourceClaimIds: claims,
  description: "基于已批准尺寸与拆件关系生成；内部细节维持可回退的数字复原边界。"
}));

const manifest = loadManifest(modelId);
const next = saveGenericStageEvidenceRevision(modelId, "05-blockout", {
  expectedRevision: manifest.revision,
  assets: records,
  reviewArtifactIds: ["hhax-gate05-white-hero-r003", "hhax-gate05-white-open-r003", "hhax-gate05-white-glb-r003"],
  validations: [
    { id: "approved-input-hash-lock", status: "pass", evidence: "生成器逐次读取并核对当前批准 Gate 03 建模合同与 Gate 04 架构快照 SHA-256。" },
    { id: "closed-envelope", status: "pass", evidence: "Blender evaluated world bounds 精确为 W30.9 × L50.5 × T13.6 mm。" },
    { id: "capsule-silhouette", status: "pass", evidence: "闭合轮廓为平行直边和连续半圆端的双层胶囊体，无第三主壳。" },
    { id: "two-shell-proportion", status: "pass", evidence: "上下两片数字目标均为 6.55 mm，闭合可见缝为 0.5 mm。" },
    { id: "full-motion-range", status: "pass", evidence: "静帧与 GLB 明确覆盖上壳 0–18.7 mm 纯 +Y 直推；背部载体绕自身 +Z 轴。" },
    { id: "hidden-boundary", status: "pass", evidence: "内腔、轨型、随动数量和联动曲线标记为可回退示意，不作实测、物理或制造声明。" },
    { id: "white-model-legibility", status: "pass", evidence: "闭合、打开、运动姿态的轮廓与接缝均可可靠分辨。" }
  ],
  diagnosis: "Gate 05 合格白模与真实交互 GLB 已生成，等待在工作台完成旋转、缩放和全行程复核。",
  recipe: "model-hhax deterministic Blender 5.2 source-linked white model"
});

console.log(JSON.stringify({ revision: next.revision, gate05: next.stages[4].status, artifactIds: next.stages[4].artifactIds }, null, 2));
