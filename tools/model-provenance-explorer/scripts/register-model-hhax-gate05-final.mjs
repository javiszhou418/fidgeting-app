import { loadManifest, saveGenericStageEvidenceRevision } from "../pipeline-core.mjs";

const modelId = "model-hhax";
const base = "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/05-blockout/rev-006";
const upstream = ["model-hhax-measurement-modeling-contract-r001", "model-hhax-part-tree-r001", "model-hhax-exploded-plan-r001", "hhax-gate04-architecture-snapshot-r002"];
const claims = ["hhax-claim-product-envelope-r002", "hhax-claim-mechanical-linkage-r002", "hhax-claim-shell-topology-r002", "hhax-claim-service-topology-r002", "hhax-claim-three-art-surfaces-r002", "hhax-claim-hidden-boundary-r002"];
const records = [
  ["hhax-gate05-white-source-r006", "white-model-source", "model-hhax-white.blend", "source-model", "deterministic-white-model-source"],
  ["hhax-gate05-white-hero-r006", "white-model-hero", "white-model-hero.png", "blender-render", "white-model-open-hero"],
  ["hhax-gate05-white-closed-r006", "white-model-closed", "white-model-closed.png", "blender-render", "white-model-closed-view"],
  ["hhax-gate05-white-open-r006", "white-model-open", "white-model-open.png", "blender-render", "white-model-full-travel-view"],
  ["hhax-gate05-white-rotation-r006", "white-model-rotation", "white-model-rotation.png", "blender-render", "rear-carrier-rotated-view"],
  ["hhax-gate05-white-underside-r006", "white-model-underside", "white-model-underside.png", "blender-render", "rear-carrier-underside-view"],
  ["hhax-gate05-white-glb-r006", "interactive-white-model", "white-model-interactive.glb", "validation", "interactive-white-model"],
  ["hhax-gate05-white-snapshot-r006", "parameter-snapshot", "blockout-parameters.json", "validation", "blockout-parameter-snapshot"]
].map(([id, slot, file, role, contentClass]) => ({ id, slot, path: `${base}/${file}`, role, contentClass, sourceAssetIds: upstream, sourceClaimIds: claims, description: "合同哈希锁定的白模；内部细节仍为可回退数字示意。" }));

const manifest = loadManifest(modelId);
const next = saveGenericStageEvidenceRevision(modelId, "05-blockout", {
  expectedRevision: manifest.revision,
  assets: records,
  reviewArtifactIds: ["hhax-gate05-white-glb-r006", "hhax-gate05-white-hero-r006", "hhax-gate05-white-open-r006", "hhax-gate05-white-rotation-r006", "hhax-gate05-white-underside-r006"],
  validations: [
    { id: "approved-input-hash-lock", status: "pass", evidence: "构建时读取并核对当前批准的尺寸合同与结构快照哈希。" },
    { id: "closed-envelope", status: "pass", evidence: "evaluated world bounds 为 W30.9 × L50.5 × T13.6 mm。" },
    { id: "capsule-and-stack", status: "pass", evidence: "胶囊轮廓连续，上下片各 6.55 mm，闭合缝 0.5 mm。" },
    { id: "full-motion-range", status: "pass", evidence: "上壳仅沿 +Y 从 0 到 18.7 mm；背部载体绕自身 +Z 轴，0°/180°方向标记可辨。" },
    { id: "rear-layer-separation", status: "pass", evidence: "背面图案、圆形载体、透明层与方向标记分层，无共面闪烁。" },
    { id: "review-legibility", status: "pass", evidence: "闭合、全开、背面原位和旋转姿态均可读。" },
    { id: "hidden-boundary", status: "pass", evidence: "内部腔体、轨型、随动数量及耦合保持可回退示意，不作制造声明。" }
  ],
  diagnosis: "Gate 05 白模已通过轮廓、厚度、全行程和背面自轴旋转自检，等待工作台交互复核。",
  recipe: "model-hhax Blender 5.2 Gate 05 final white model after retained visual failures"
});
console.log(JSON.stringify({ revision: next.revision, gate05: next.stages[4].status, artifactIds: next.stages[4].artifactIds }, null, 2));
