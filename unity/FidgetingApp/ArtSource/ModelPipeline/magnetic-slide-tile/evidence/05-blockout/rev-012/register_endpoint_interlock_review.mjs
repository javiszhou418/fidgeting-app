#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate02 = manifest.stages.find((item) => item.id === "02-analysis");
const gate03 = manifest.stages.find((item) => item.id === "03-contract");
const gate04 = manifest.stages.find((item) => item.id === "04-architecture");
const gate05 = manifest.stages.find((item) => item.id === "05-blockout");
if (manifest.revision < 218 || gate05?.revision !== 12 || gate05.status !== "ready_for_review")
  throw new Error(`Unexpected pipeline state ${manifest.revision}/${gate05?.revision}/${gate05?.status}.`);
const here = path.dirname(fileURLToPath(import.meta.url));
const validation = JSON.parse(fs.readFileSync(
  path.join(here, "unity-preview/endpoint-interlock-video-validation.json"), "utf8"));
if (!validation.pass) throw new Error("Endpoint interlock recording validation failed.");
const exactUserWording = "上片只有在推到顶部的时候，才可以进行360度旋转";
const contractSha = validation.contractSha256;
const contractAssetId = "slider-analysis-mechanism-evidence-contract-r017";
const sourceGeometryIds = [
  "magnetic-slide-g05-r012-fbx",
  "magnetic-slide-g05-r012-product-glb",
];
const definitions = [
  ["slider-analysis-endpoint-rotation-correction-r017", "02-analysis", "user-correction", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-017/user-endpoint-rotation-correction.json", "user-input"],
  [contractAssetId, "02-analysis", "mechanism-evidence-contract", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-017/mechanism-evidence-contract.json", "contract"],
  ["slider-analysis-interactive-cad-geometry-config-r017", "02-analysis", "interactive-cad-config", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-017/interactive-cad-geometry-config.json", "contract"],
  ["slider-analysis-endpoint-interlock-builder-r017", "02-analysis", "contract-builder", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-017/build_endpoint_interlock_contract.mjs", "process"],
  ["slider-analysis-endpoint-interlock-validation-r017", "02-analysis", "contract-validation", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-017/endpoint-interlock-contract-validation.json", "validation"],
  ["magnetic-slide-tile-endpoint-interlock-contract-amendment-r011", "03-contract", "contract-amendment", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/03-contract/rev-011/endpoint-interlock-amendment.json", "contract"],
  ["magnetic-slide-tile-endpoint-interlock-architecture-r014", "04-architecture", "architecture-contract", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/04-architecture/rev-014/endpoint-rotation-interlock-architecture.json", "contract"],
  ["magnetic-slide-tile-endpoint-interlock-state-machine-r014", "04-architecture", "interactive-architecture", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/04-architecture/rev-014/endpoint-rotation-interlock-state-machine.svg", "contract"],
  ["magnetic-slide-g05-r012-endpoint-interlock-video", "05-blockout", "unity-motion-recording", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/unity-preview/gate05-r012-endpoint-interlock-motion.mp4", "unity-render"],
  ["magnetic-slide-g05-r012-endpoint-interlock-transform", "05-blockout", "unity-transform-validation", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/unity-preview/unity-endpoint-interlock-validation.json", "validation"],
  ["magnetic-slide-g05-r012-endpoint-interlock-validation", "05-blockout", "motion-video-validation", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/unity-preview/endpoint-interlock-video-validation.json", "validation"],
  ["magnetic-slide-g05-r012-endpoint-interlock-builder", "05-blockout", "unity-builder", "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate05R012Geometry/Editor/MagneticSlideTileGate05R012EndpointInterlockBuilder.cs", "process"],
  ["magnetic-slide-g05-r012-endpoint-interlock-scene", "05-blockout", "unity-scene", "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate05R012Geometry/MagneticSlideTileGate05R012EndpointInterlockPreview.unity", "unity-render"],
  ["magnetic-slide-g05-r012-endpoint-interlock-validator", "05-blockout", "validation-script", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/validate_endpoint_interlock_recording.py", "process"],
  ["magnetic-slide-g05-r012-endpoint-interlock-register", "05-blockout", "registration-script", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/register_endpoint_interlock_review.mjs", "process"],
];
const definitionIds = new Set(definitions.map(([id]) => id));
manifest.assets = manifest.assets.filter((asset) => !definitionIds.has(asset.id));
for (const [id, stageId, slot, relative, role] of definitions) {
  const absolute = path.join(repoRoot, relative);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${relative}`);
  manifest.assets.push({
    id,
    stageId,
    slot,
    path: relative,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: relative.endsWith(".cs") || relative.endsWith(".unity") || relative.endsWith(".mp4")
        ? "Unity 6000.5.6f1" : "fidgeting-model-pipeline",
      version: "endpoint-interlock-2026-08-28",
      recipe: "latest user-authoritative sMax-only rotation interlock",
    },
    provenance: {
      origin: role === "user-input" ? "user-provided" : "repository-generated",
      contentClass: slot,
      assertedBy: role === "user-input" ? "user" : "assistant",
      exactUserWording: role === "user-input" ? exactUserWording : undefined,
      mechanismEvidenceContractSha256: contractSha,
      sourceGeometryChanged: false,
      finalMaterialsApplied: false,
      shippingSceneModified: false,
      buildInstallPhone: false,
    },
    sourceAssetIds: id === "slider-analysis-endpoint-rotation-correction-r017"
      ? [] : ["slider-analysis-endpoint-rotation-correction-r017", ...sourceGeometryIds],
    sourceClaimIds: [],
  });
}

for (const stage of [gate02, gate03, gate04, gate05]) {
  stage.artifactIds.push(...definitions
    .filter(([, stageId]) => stageId === stage.id)
    .map(([id]) => id)
    .filter((id) => !stage.artifactIds.includes(id)));
}
gate02.revision = 17;
gate02.status = "approved";
gate02.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt: new Date().toISOString(),
  scope: "endpoint-only-rotation-interlock",
};
gate02.reviewArtifactIds = ["slider-analysis-interactive-cad-geometry-config-r017"];
gate02.analysisSpec.revision = 17;
gate02.analysisSpec.reviewMode = "interactive-cad-endpoint-rotation-interlock";
gate02.analysisSpec.contractAssetId = contractAssetId;
gate02.analysisSpec.contractSha256 = contractSha;
gate02.analysisSpec.geometryConfigAssetId = "slider-analysis-interactive-cad-geometry-config-r017";
gate02.analysisSpec.cadArtifactId = "slider-analysis-interactive-cad-geometry-config-r017";
gate02.analysisSpec.cadConfigAssetId = "slider-analysis-interactive-cad-geometry-config-r017";
gate02.analysisSpec.constraintIds = [
  ...new Set([...gate02.analysisSpec.constraintIds, "MEC-ENDPOINT-ROTATION-INTERLOCK"]),
];
gate02.analysisSpec.coverageTopics = gate02.analysisSpec.coverageTopics
  .map((topic) => topic === "simultaneous slide+rotation" ? "maximum-endpoint rotation interlock" : topic);
gate02.analysisSpec.conclusions = [
  {
    statement: "0≤s<sMax 时只可直推，θ=0°",
    constraintIds: ["MEC-ENDPOINT-ROTATION-INTERLOCK", "MEC-ROTATION-DURING-SLIDE"],
    confidence: "locked",
    sourceCount: 1,
  },
  {
    statement: "仅 s=sMax 解锁 360° 与 30×12° 卡位",
    constraintIds: ["MEC-ENDPOINT-ROTATION-INTERLOCK", "MEC-ROTATION-RANGE", "MEC-DETENTS"],
    confidence: "locked",
    sourceCount: 1,
  },
  {
    statement: "非零角锁住行程；0°/360° 对齐后回推",
    constraintIds: ["MEC-ENDPOINT-ROTATION-INTERLOCK", "MEC-COMPOUND-TRANSFORM"],
    confidence: "locked",
    sourceCount: 1,
  },
];
gate02.analysisSpec.approvalSpec.requiredMilestones = [
  "minimumOverlapDisk", "robustContainment", "finiteGrooveEndpoints", "synchronizedViews",
  "pointerDirection", "fixedAxis", "rotatingCarrier", "topUndersideGrooves",
  "midTravelRotationBlocked", "endpointRotationUnlock", "nonzeroAngleSlideLock",
  "alignedReturn", "pivotCoverage", "smoothBottomExterior", "sourceMapping",
];
gate02.validations = [
  { id: "endpoint-interlock-contract", status: "pass", evidence: `Rev 17 contract ${contractSha}; exact user wording persisted.` },
  { id: "all-position-rotation-superseded", status: "pass", evidence: "All-position and simultaneous 2-DOF claims are historical only." },
  { id: "geometry-unchanged", status: "pass", evidence: "Interlock changes legal transforms, not geometry." },
];

gate03.status = "approved";
gate03.contractSpec = {
  ...gate03.contractSpec,
  mechanismEvidenceContractAssetId: contractAssetId,
  mechanismEvidenceContractSha256: contractSha,
  endpointInterlockAmendmentAssetId: "magnetic-slide-tile-endpoint-interlock-contract-amendment-r011",
  dimensionsChanged: false,
};
gate04.revision = 14;
gate04.status = "approved";
gate04.reviewArtifactIds = ["magnetic-slide-tile-endpoint-interlock-state-machine-r014"];
gate04.architectureSpec = {
  ...gate04.architectureSpec,
  mechanismEvidenceContractAssetId: contractAssetId,
  mechanismEvidenceContractSha256: contractSha,
  endpointInterlockAssetId: "magnetic-slide-tile-endpoint-interlock-architecture-r014",
  stateMachineAssetId: "magnetic-slide-tile-endpoint-interlock-state-machine-r014",
  geometryChanged: false,
  hiddenLatchGeometry: "unknown-not-modeled",
};
gate04.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt: new Date().toISOString(),
  scope: "serial-slide-endpoint-rotation-architecture",
};

const rejectedVideo = manifest.assets.find((asset) => asset.id === "magnetic-slide-g05-r012-unity-full360-video");
if (!rejectedVideo) throw new Error("Missing rejected 50%-rotation video.");
rejectedVideo.provenance = {
  ...rejectedVideo.provenance,
  evidenceStatus: "rejected-invalid-partial-slide-rotation",
  rejectionReason: exactUserWording,
  supersededBy: "magnetic-slide-g05-r012-endpoint-interlock-video",
};
for (const assetId of sourceGeometryIds) {
  const asset = manifest.assets.find((item) => item.id === assetId);
  asset.provenance = {
    ...asset.provenance,
    mechanismEvidenceContractSha256: contractSha,
    endpointInterlockMetadata: "sMax-only-rotation",
    geometryChanged: false,
  };
}
for (const asset of manifest.assets.filter((item) =>
  ["03-contract", "04-architecture", "05-blockout"].includes(item.stageId))) {
  asset.provenance = {
    ...asset.provenance,
    mechanismEvidenceContractSha256: contractSha,
  };
}
gate05.reviewArtifactIds = [
  "magnetic-slide-g05-r012-endpoint-interlock-video",
  "magnetic-slide-g05-r012-product-glb",
  "magnetic-slide-g05-r012-axis-overlay",
  "magnetic-slide-g05-r012-open",
  "magnetic-slide-g05-r012-technical-separated",
  "magnetic-slide-g05-r012-technical-glb",
];
gate05.blockoutSpec.governingContractAssetId = contractAssetId;
gate05.blockoutSpec.governingContractSha256 = contractSha;
gate05.blockoutSpec.fullRotationReview = {
  ...gate05.blockoutSpec.fullRotationReview,
  decisionState: "rejected-invalid-partial-slide-rotation",
  rejectedByExactUserWording: exactUserWording,
  videoAssetId: "magnetic-slide-g05-r012-unity-full360-video",
  historicalOnly: true,
};
gate05.blockoutSpec.endpointInterlockReview = {
  decisionState: "latest-user-authoritative-rule-implemented",
  exactUserWording,
  sourceGeometryChanged: false,
  contractAssetId,
  contractSha256: contractSha,
  architectureAssetId: "magnetic-slide-tile-endpoint-interlock-architecture-r014",
  videoAssetId: "magnetic-slide-g05-r012-endpoint-interlock-video",
  frameCount: validation.frameCount,
  fps: validation.video.frameRate,
  durationSeconds: validation.video.durationSeconds,
  dimensions: [validation.video.width, validation.video.height],
  visitedDetentIndices: validation.unityTransformValidation.visitedDetentIndices,
  visualApprovalPending: true,
};
gate05.validations = gate05.validations.filter((item) => !item.id.includes("full-rotation"));
gate05.validations.push(
  { id: "endpoint-rotation-interlock", status: "pass", evidence: "1000 CAD samples below sMax block rotation; only sMax unlocks." },
  { id: "endpoint-thirty-detents", status: "pass", evidence: "30×12° detents visited only at sMax; 360° closure error 0°." },
  { id: "rotated-slide-lock", status: "pass", evidence: "30 visible nonzero-angle slide-attempt frames remain fixed at sMax." },
  { id: "serial-motion-per-frame", status: "pass", evidence: "450 Unity frames; simultaneous slide/angular velocity violations=0." },
  { id: "endpoint-video-playback", status: "pass", evidence: "H.264 High 1920×1080, 30 fps, 15 s; AVFoundation decoded 450/450." },
);
gate05.status = "ready_for_review";
gate05.readiness = {
  ready: true,
  blockers: [],
  note: "Review the endpoint-interlock white-model video. Visual approval pending; no material, shipping, build, install or phone work.",
};
for (let index = 5; index < manifest.stages.length; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 05 endpoint-only rotation review is pending; all downstream evidence is blocked.";
}
for (const claim of manifest.claims) {
  if (/simultaneous|all.position|任意.*旋转|滑动与旋转可同时/.test(`${claim.id} ${claim.statement}`)) {
    claim.state = "superseded";
    claim.decisionState = "superseded-by-latest-endpoint-interlock-correction";
  }
}
manifest.claims = manifest.claims.filter((claim) => claim.id !== "slider-endpoint-rotation-interlock-r017");
manifest.claims.push({
  id: "slider-endpoint-rotation-interlock-r017",
  stageId: "02-analysis",
  topic: "endpoint-rotation-interlock",
  statement: exactUserWording,
  confidence: "user-authoritative",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: ["slider-analysis-endpoint-rotation-correction-r017"],
  sourceRegions: [],
  decisionState: "locked",
  deliveryState: "gate05-white-model-evidence-ready",
});
manifest.currentStageId = "05-blockout";
manifest.currentState.visualApproval = "gate05-rev12-endpoint-interlock-ready-visual-approval-pending-not-pushed";
manifest.currentState.blenderModelingStatus = "gate05-rev12-geometry-unchanged-endpoint-interlock-evidence-ready";
manifest.currentState.unityStatus = "isolated-clay-endpoint-interlock-preview-only-old-shipping-model-default";
manifest.currentState.workbench = "persistent-seven-tab-default-gate05-white-model-endpoint-interlock";
manifest.currentState.diagnosis = exactUserWording;
manifest.issues = manifest.issues.filter((issue) =>
  issue.assetId !== "magnetic-slide-g05-r012-unity-full360-video"
  || issue.status !== "rejected-preserved-history");
manifest.issues.push({
  id: crypto.randomUUID(),
  stageId: "05-blockout",
  assetId: "magnetic-slide-g05-r012-unity-full360-video",
  severity: "critical",
  status: "rejected-preserved-history",
  note: "Invalid evidence: rotates at 50% travel. " + exactUserWording,
});
for (const relative of [
  "tools/model-provenance-explorer/app.js",
  "tools/model-provenance-explorer/mechanism-cad-core.mjs",
  "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate05-r012.mjs",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/browser-workspace-validation.json",
  "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev12-persistent-workbench.png",
  "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev12-workbench-focused.png",
  "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md",
]) {
  const absolute = path.join(repoRoot, relative);
  for (const asset of manifest.assets.filter((item) => item.path === relative)) {
    asset.sha256 = sha256File(absolute);
    asset.sizeBytes = fs.statSync(absolute).size;
  }
}
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "endpoint-rotation-interlock-evidence-ready",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  exactUserWording,
  contractSha256: contractSha,
  earliestAffectedGate: "02-analysis",
  architectureRevision: 14,
  geometryChanged: false,
  rejectedAssetId: "magnetic-slide-g05-r012-unity-full360-video",
  replacementVideoAssetId: "magnetic-slide-g05-r012-endpoint-interlock-video",
  visualApprovalPending: true,
  buildInstallPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  contractSha256: contractSha,
  gate02: saved.stages[1].status,
  gate04: saved.stages[3].status,
  gate05: saved.stages[4].status,
  video: validation.video,
}, null, 2));
