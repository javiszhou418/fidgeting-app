import { loadManifest, saveGenericStageEvidenceRevision } from "../pipeline-core.mjs";

const modelId = "model-hhax";
const base = "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/05-blockout/rev-005";
const upstream = ["model-hhax-measurement-modeling-contract-r001", "model-hhax-part-tree-r001", "model-hhax-exploded-plan-r001", "hhax-gate04-architecture-snapshot-r002"];
const claims = ["hhax-claim-product-envelope-r002", "hhax-claim-mechanical-linkage-r002", "hhax-claim-shell-topology-r002", "hhax-claim-service-topology-r002", "hhax-claim-three-art-surfaces-r002", "hhax-claim-hidden-boundary-r002"];
const records = [
  ["hhax-gate05-underside-preflight-source-r005", "white-model-source", "model-hhax-white.blend", "source-model"],
  ["hhax-gate05-underside-preflight-hero-r005", "white-model-hero", "white-model-hero.png", "blender-render"],
  ["hhax-gate05-underside-preflight-closed-r005", "white-model-closed", "white-model-closed.png", "blender-render"],
  ["hhax-gate05-underside-preflight-open-r005", "white-model-open", "white-model-open.png", "blender-render"],
  ["hhax-gate05-underside-preflight-rotation-r005", "white-model-rotation", "white-model-rotation.png", "blender-render"],
  ["hhax-gate05-underside-preflight-bottom-r005", "white-model-underside", "white-model-underside.png", "blender-render"],
  ["hhax-gate05-underside-preflight-glb-r005", "interactive-white-model", "white-model-interactive.glb", "validation"],
  ["hhax-gate05-underside-preflight-snapshot-r005", "parameter-snapshot", "blockout-parameters.json", "validation"]
].map(([id, slot, file, role]) => ({ id, slot, path: `${base}/${file}`, role, contentClass: "gate05-underside-lighting-preflight", sourceAssetIds: upstream, sourceClaimIds: claims, description: "背面几何层级已拆开，但底面静态审查灯未照亮；保留为失败版本。" }));

const manifest = loadManifest(modelId);
const next = saveGenericStageEvidenceRevision(modelId, "05-blockout", {
  expectedRevision: manifest.revision,
  assets: records,
  validations: [
    { id: "contract-bounds-and-motion", status: "pass", evidence: "输入哈希、30.9 × 50.5 × 13.6 mm 闭合 bounds、18.7 mm 直推与自轴旋转均通过。" },
    { id: "rear-layer-separation", status: "pass", evidence: "背面图案、圆形载体、透明层与方向标记已分层且不再共面。" },
    { id: "underside-review-legibility", status: "fail", evidence: "底面两张静态图缺少下方审查灯，圆形载体与方向标记不可可靠辨认；本版本不批准。" }
  ],
  diagnosis: "背面层级已修正，但底面审查图过暗；保留失败版本并只修审查灯光后重做。",
  recipe: "model-hhax Gate 05 retained underside-lighting preflight"
});
console.log(JSON.stringify({ revision: next.revision, gate05: next.stages[4].status, validations: next.stages[4].validations }, null, 2));
