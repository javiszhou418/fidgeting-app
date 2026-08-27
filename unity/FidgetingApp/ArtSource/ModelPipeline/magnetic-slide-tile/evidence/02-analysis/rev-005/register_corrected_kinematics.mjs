#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const expectedRevision = 116;
const manifest = loadManifest(modelId);
if (manifest.revision !== expectedRevision) {
  throw new Error(`Expected manifest revision ${expectedRevision}, got ${manifest.revision}.`);
}

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../..");
const resolveRepoPath = (repoPath) => path.join(repoRoot, repoPath);
const toRepoPath = (absolutePath) => path.relative(repoRoot, absolutePath).split(path.sep).join("/");
const timestamp = new Date().toISOString();
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.status !== "ready_for_review" || stage.analysisSpec?.revision !== 4) {
  throw new Error("Gate 02 rev 4 must remain ready_for_review before revision.");
}

const assetIds = new Set(manifest.assets.map((asset) => asset.id));
const addAsset = ({ id, slot = "analysis-evidence", absolutePath, role, contentClass, sourceAssetIds, note, recipe }) => {
  if (assetIds.has(id)) throw new Error(`Asset already exists: ${id}`);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing asset: ${absolutePath}`);
  const asset = {
    id,
    stageId: "02-analysis",
    slot,
    path: toRepoPath(absolutePath),
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role,
    producer: { name: "fidgeting-model-pipeline", version: "1", recipe },
    provenance: {
      origin: "repository-generated",
      contentClass,
      assertedBy: "assistant",
      note
    },
    sourceAssetIds
  };
  manifest.assets.push(asset);
  assetIds.add(id);
  return asset;
};

const videos = [
  "slider-intake-user-mechanism-video-6022",
  "slider-intake-user-mechanism-video-6023",
  "slider-intake-user-mechanism-video-6024"
];
const internalEvidence = stage.analysisSpec.internalEvidenceAssetIds;
const conclusion = addAsset({
  id: "slider-analysis-conclusion-review-r005",
  slot: "analysis-board",
  absolutePath: path.join(here, "mechanism-review-conclusions.json"),
  role: "analysis",
  contentClass: "corrected-lower-carrier-kinematics-review-contract",
  sourceAssetIds: internalEvidence,
  note: "用户权威修正：上片固定；下片、轴心和双侧滑轨共同平移；下片绕平移后的轴心旋转。",
  recipe: "Immutable Gate 02 rev 5 corrected-ownership review"
});
const core = addAsset({
  id: "slider-analysis-mechanism-sandbox-core-r005",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/mechanism-sandbox-core.mjs"),
  role: "process",
  contentClass: "deterministic-translated-axis-bilateral-rail-core",
  sourceAssetIds: [conclusion.id],
  note: "确定性 transform 模型锁定固定上片、活动下片、随下片移动的轴心和下片双侧滑轨。",
  recipe: "Pure JavaScript kinematics and mechanism state core"
});
const tests = addAsset({
  id: "slider-analysis-mechanism-sandbox-tests-r005",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/tests/mechanism-sandbox.test.mjs"),
  role: "validation",
  contentClass: "corrected-kinematics-unit-tests",
  sourceAssetIds: [core.id],
  note: "覆盖上片不动、下片与轴心同移、平移轴旋转、双轨归属、0/12/36° 与 +0.21L 分离、零速 reset。",
  recipe: "Node test runner"
});
const app = addAsset({
  id: "slider-analysis-mechanism-sandbox-ui-r005",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/app.js"),
  role: "process",
  contentClass: "semi-transparent-bilateral-rail-interactive-review-ui",
  sourceAssetIds: [core.id, conclusion.id],
  note: "半透明固定上片／活动下片、下片双侧滑轨、随滑动轴心、opacity 控件与实时轴心位置。",
  recipe: "Model Provenance Explorer module UI"
});
const style = addAsset({
  id: "slider-analysis-mechanism-sandbox-style-r005",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/styles.css"),
  role: "process",
  contentClass: "semi-transparent-depth-ordered-mechanism-style",
  sourceAssetIds: [app.id],
  note: "固定上片位于活动机构上方；内部双轨和上片候选接触区按可调 opacity 显示。",
  recipe: "Responsive CSS"
});
const registrar = addAsset({
  id: "slider-analysis-corrected-kinematics-registrar-r005",
  absolutePath: fileURLToPath(import.meta.url),
  role: "process",
  contentClass: "immutable-gate02-corrected-kinematics-registrar",
  sourceAssetIds: [conclusion.id, core.id],
  note: "保留 rev 4 requested revision，并登记用户权威 reference-frame correction。",
  recipe: "Revision-guarded manifest and history update"
});
const newAssetIds = [conclusion.id, core.id, tests.id, app.id, style.id, registrar.id];

for (const claim of manifest.claims.filter(
  (candidate) => candidate.stageId === "02-analysis"
    && candidate.state === "pending-review"
    && candidate.id.endsWith("-r004")
)) {
  claim.state = "superseded";
  claim.supersededBy = "corrected-lower-carrier-kinematics-r005";
  claim.supersededAt = timestamp;
}

const regions = (id) => manifest.claims.find((claim) => claim.id === id)?.sourceRegions || [];
const claimDefinitions = [
  {
    id: "slider-analysis-fixed-upper-moving-lower-r005",
    category: "motion",
    statement: "固定上片 transform 始终为 identity；只有活动下片承担平移和旋转。",
    confidence: "user-authoritative",
    sourceRegions: regions("slider-analysis-carrier-cover-roles-r003")
  },
  {
    id: "slider-analysis-axis-attached-to-lower-r005",
    category: "mechanism",
    statement: "下片轴心固定在活动下片上，轴心世界位移严格等于下片平移；旋转围绕平移后的轴心且 pivot drift 为零。",
    confidence: "user-authoritative",
    sourceRegions: regions("slider-analysis-carrier-cover-roles-r003")
  },
  {
    id: "slider-analysis-bilateral-lower-rails-r005",
    category: "structure",
    statement: "活动下片反面有左右两条纵向滑轨／珠列区域，两条均随下片平移和旋转。",
    confidence: "high",
    sourceRegions: regions("slider-analysis-exterior-reverse-face-r003")
  },
  {
    id: "slider-analysis-one-outward-direction-r005",
    category: "motion",
    statement: "从闭合止点只朝一个外向方向打开，并可沿同一路径关闭；不能越过闭合止点。",
    confidence: "high",
    sourceRegions: regions("slider-analysis-one-outward-direction-r003")
  },
  {
    id: "slider-analysis-normalized-travel-r005",
    category: "scale",
    statement: "视频支持行程约 0.38–0.46L、峰值约 0.50L；实体毫米行程 unknown。",
    confidence: "medium",
    sourceRegions: regions("slider-analysis-normalized-travel-r003")
  },
  {
    id: "slider-analysis-translated-axis-detents-r005",
    category: "mechanism",
    statement: "活动下片绕已平移轴心旋转；强支持 12° 每档、360° 共 30 档。",
    confidence: "high",
    sourceRegions: [
      ...regions("slider-analysis-twelve-degree-detents-r003"),
      ...regions("slider-analysis-rotation-across-slide-r003")
    ]
  }
];
for (const definition of claimDefinitions) {
  manifest.claims.push({
    ...definition,
    stageId: "02-analysis",
    sourceAssetIds: [...new Set(definition.sourceRegions.map((region) => region.assetId))],
    state: "pending-review",
    decisionState: "pending-user-approval",
    analysisRevision: "008",
    assertedBy: "assistant"
  });
}

stage.priorInteractiveReview = {
  analysisEvidenceRevision: 4,
  stageRevision: stage.revision,
  status: "rejected-requested-revision",
  reason: "User corrected fixed/moving ownership, bilateral rails, transparency and axis translation.",
  artifactIds: [...stage.artifactIds],
  reviewArtifactIds: [...stage.reviewArtifactIds]
};
stage.revision += 1;
stage.status = "ready_for_review";
stage.decision = null;
stage.artifactIds.push(...newAssetIds);
stage.reviewArtifactIds = [conclusion.id];
stage.analysisSpec = {
  revision: 5,
  reviewMode: "conclusion-first-semi-transparent-corrected-kinematics-sandbox",
  reportingLayers: {
    internal: "full-frame-audio-crop-tracking-calculation-source-validation",
    user: "six-conclusions-unknowns-one-decision-dynamic-semi-transparent-demo",
    technicalEvidenceCollapsedByDefault: true,
    defaultScreenshotWall: false
  },
  reviewQuestion: "半透明双侧滑轨与随下片移动的轴心，现在是否符合实物？",
  userReviewAssetIds: [conclusion.id],
  internalEvidenceAssetIds: internalEvidence,
  sourceVideoAssetIds: videos,
  playbackProxyAssetIds: stage.priorInteractiveReview.analysisEvidenceRevision === 4
    ? ["slider-analysis-img-6022-playback-proxy-r003", "slider-analysis-img-6023-playback-proxy-r003", "slider-analysis-img-6024-playback-proxy-r003"]
    : [],
  claimIds: claimDefinitions.map((claim) => claim.id),
  dimensionStatus: {
    measured: ["frame-index", "PTS", "audio-impulse-candidates", "silhouette-landmarks"],
    inferredRange: {
      aspectRatioLW: { minimum: 1.52, maximum: 1.62, sandboxDefault: 1.57 },
      travelL: { minimum: 0.38, supportedMaximum: 0.46, observedPeak: 0.5, sandboxDefault: 0.42 }
    },
    unknown: ["physical-length", "physical-width", "physical-thickness", "physical-travel"],
    editablePhysicalMeasurementDefaults: null
  },
  mechanismSandbox: {
    coreAssetId: core.id,
    upperOwner: "fixed",
    movingOwner: "lower-carrier",
    axisOwner: "lower-carrier",
    railOwner: "lower-carrier",
    railCount: 2,
    internalsOpacityDefault: 0.72,
    axisMovesExactlyWithLowerTranslation: true,
    lowerRotatesAroundTranslatedAxis: true,
    pivotDrift: 0,
    detentCount: 30,
    detentStepDeg: 12,
    resetAngularVelocityDegPerSecond: 0,
    selfMotion: false,
    pointerDriven: true,
    supportedRotationTravelStates: ["partial", "near-maximum"],
    unsupportedUpperFollowerGeometryMarked: true,
    desktopForceClaimed: false,
    phoneHapticClaimed: false
  },
  reviewPoses: {
    detents: [
      { travelL: 0, angleDeg: 0 },
      { travelL: 0, angleDeg: 12 },
      { travelL: 0, angleDeg: 36 }
    ],
    slide: { travelL: 0.21, angleDeg: 0 }
  },
  unknowns: [
    "upper follower/contact geometry",
    "slot wall cross-section",
    "rotation at every exact travel position",
    "physical dimensions and force",
    "phone Haptic"
  ]
};
stage.validations = stage.validations.filter((validation) => validation.id !== "browser-pointer-mobile-modal-video");
stage.validations.push(
  {
    id: "corrected-transform-ownership",
    status: "pass",
    evidence: "Deterministic core locks upper identity, lower translation, axis-world equality, translated-axis rotation and zero pivot drift."
  },
  {
    id: "bilateral-rail-ownership",
    status: "pass",
    evidence: "Two local rail regions remain children of the lower carrier under translation and rotation."
  },
  {
    id: "normalized-dimension-boundary-r005",
    status: "pass",
    evidence: "Review uses L/W and travel/L only; physical fields remain optional and empty."
  }
);

for (const downstream of manifest.stages.slice(2, 11)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 02 rev 5 corrects fixed/moving ownership, axis translation and bilateral lower rails.";
}
manifest.stages[11].status = "blocked";
manifest.stages[11].staleReason = "Gate 12 rejection remains preserved. Gate 02 rev 5 and downstream gates require approval.";

const digestValues = (values) => crypto.createHash("sha256")
  .update(values.filter(Boolean).sort().join("\n"))
  .digest("hex");
stage.inputDigest = digestValues(videos.map(
  (id) => manifest.assets.find((asset) => asset.id === id)?.sha256
));
stage.outputDigest = digestValues(stage.artifactIds.map(
  (id) => manifest.assets.find((asset) => asset.id === id)?.sha256
));

manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev5-corrected-kinematics-review-pending";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis = "Gate 01 remains approved. Gate 02 rev 4 is requested revision. Gate 02 rev 5 is ready for review with fixed upper, moving lower, lower-owned moving axis, bilateral lower rails and a semi-transparent sandbox. Gates 03–11 are stale; Gate 12 remains blocked/rejected. No Blender, Unity, build, install or phone work ran.";

saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-corrected-kinematics-review-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 5,
  priorRevisionDisposition: "rev4-requested-revision",
  userCorrection: "fixed-upper-moving-lower-axis-translates-bilateral-lower-rails",
  exactMotionModel: "upper=I; lower=T(s)*R_about(A_lower,theta); A_world=A_lower+T(s); pivotDrift=0",
  reviewArtifactIds: stage.reviewArtifactIds,
  internalEvidenceAssetIds: internalEvidence,
  claimIds: claimDefinitions.map((claim) => claim.id),
  normalizedTravelRangeL: [0.38, 0.46],
  physicalDimensions: "unknown-editable-user-measurement-only",
  downstreamStatus: "gates03-11-stale-gate12-blocked-rejected",
  blenderUnityBuildInstallPhone: "not-started",
  reviewQuestion: stage.analysisSpec.reviewQuestion
});

console.log(JSON.stringify({
  modelId,
  manifestRevision: manifest.revision,
  gate02Revision: stage.revision,
  analysisRevision: stage.analysisSpec.revision,
  status: stage.status,
  reviewQuestion: stage.analysisSpec.reviewQuestion
}, null, 2));
