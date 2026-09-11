import { loadManifest, saveGenericStageEvidenceRevision } from "../pipeline-core.mjs";

const modelId = "model-hhax";
const base = "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/05-blockout/rev-002";
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
  ["hhax-gate05-motion-preflight-source-r002", "white-model-source", "model-hhax-white.blend", "source-model"],
  ["hhax-gate05-motion-preflight-hero-r002", "white-model-hero", "white-model-hero.png", "blender-render"],
  ["hhax-gate05-motion-preflight-closed-r002", "white-model-closed", "white-model-closed.png", "blender-render"],
  ["hhax-gate05-motion-preflight-open-r002", "white-model-open", "white-model-open.png", "blender-render"],
  ["hhax-gate05-motion-preflight-rotation-r002", "white-model-rotation", "white-model-rotation.png", "blender-render"],
  ["hhax-gate05-motion-preflight-glb-r002", "interactive-white-model", "white-model-interactive.glb", "validation"],
  ["hhax-gate05-motion-preflight-snapshot-r002", "parameter-snapshot", "blockout-parameters.json", "validation"]
].map(([id, slot, file, role]) => ({
  id, slot, path: `${base}/${file}`, role,
  contentClass: "gate05-motion-preflight",
  sourceAssetIds: upstream,
  sourceClaimIds: claims,
  description: "第二次白模预检；轮廓和尺寸可读，但静帧渲染被关键帧重新求值，未呈现直推全行程。"
}));

const manifest = loadManifest(modelId);
const next = saveGenericStageEvidenceRevision(modelId, "05-blockout", {
  expectedRevision: manifest.revision,
  assets: records,
  validations: [
    { id: "contract-and-architecture-hash-lock", status: "pass", evidence: "已核对 Gate 03/04 文件哈希并从九项合同取值。" },
    { id: "closed-envelope", status: "pass", evidence: "evaluated bounds 为 30.9 × 50.5 × 13.6 mm。" },
    { id: "white-model-legibility", status: "pass", evidence: "主体、上下壳接缝和胶囊轮廓可读。" },
    { id: "full-motion-range-visible", status: "fail", evidence: "打开静帧未呈现 18.7 mm 位移，不能证明完整运动范围；本版本不得批准。" }
  ],
  diagnosis: "Gate 05 第二次预检暴露静帧关键帧求值问题；保留版本，改用非关键帧增量姿态后重做。",
  recipe: "model-hhax Gate 05 visible-motion preflight retained for audit"
});

console.log(JSON.stringify({ revision: next.revision, gate05: next.stages[4].status, validations: next.stages[4].validations }, null, 2));
