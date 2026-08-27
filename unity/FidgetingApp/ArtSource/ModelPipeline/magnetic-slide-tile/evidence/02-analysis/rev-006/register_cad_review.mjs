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
const expectedRevision = 118;
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
if (stage.status !== "ready_for_review" || stage.analysisSpec?.revision !== 5) {
  throw new Error("Gate 02 rev 5 must remain ready_for_review before revision.");
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

const internalEvidence = stage.analysisSpec.internalEvidenceAssetIds;
const contract = addAsset({
  id: "slider-analysis-cad-review-contract-r006",
  slot: "analysis-board",
  absolutePath: path.join(here, "cad-review-contract.json"),
  role: "analysis",
  contentClass: "interactive-vector-engineering-review-contract",
  sourceAssetIds: internalEvidence,
  note: "记录真实旋转故障、修复边界、同步 CAD 视图、参数状态和唯一评审问题。",
  recipe: "Immutable Gate 02 rev 6 CAD review contract"
});
const cadCore = addAsset({
  id: "slider-analysis-cad-core-r006",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/mechanism-cad-core.mjs"),
  role: "process",
  contentClass: "deterministic-vector-geometry-and-dimension-state-core",
  sourceAssetIds: [contract.id],
  note: "生成胶囊相切点、三视图 transform、zoom/pan 和 unknown-safe 物理尺寸派生。",
  recipe: "Pure JavaScript CAD geometry and dimension state"
});
const mechanismCore = addAsset({
  id: "slider-analysis-mechanism-core-r006",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/mechanism-sandbox-core.mjs"),
  role: "process",
  contentClass: "deterministic-slide-rotation-detent-core",
  sourceAssetIds: [contract.id],
  note: "保留物理状态并增加精确 detent/pose 键盘控制。",
  recipe: "Pure JavaScript mechanism state core"
});
const cadTests = addAsset({
  id: "slider-analysis-cad-tests-r006",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/tests/mechanism-cad.test.mjs"),
  role: "validation",
  contentClass: "cad-tangency-transform-dimension-viewport-tests",
  sourceAssetIds: [cadCore.id],
  note: "覆盖胶囊相切、轴心 transform、双轨、同步视图、unknown/derived dimensions 和 zoom/pan。",
  recipe: "Node test runner"
});
const mechanismTests = addAsset({
  id: "slider-analysis-mechanism-tests-r006",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/tests/mechanism-sandbox.test.mjs"),
  role: "validation",
  contentClass: "mechanism-physics-and-ownership-tests",
  sourceAssetIds: [mechanismCore.id],
  note: "覆盖分档、零自转、阻尼、breakaway、止点、所有权和零速 reset。",
  recipe: "Node test runner"
});
const app = addAsset({
  id: "slider-analysis-cad-ui-r006",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/app.js"),
  role: "process",
  contentClass: "interactive-cad-review-ui",
  sourceAssetIds: [cadCore.id, mechanismCore.id, contract.id],
  note: "同步顶视/侧视/A–A、旋转环、slide/rotate/pan、键盘、zoom、参数和测量清单。",
  recipe: "Model Provenance Explorer module UI"
});
const style = addAsset({
  id: "slider-analysis-cad-style-r006",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/styles.css"),
  role: "process",
  contentClass: "responsive-vector-engineering-drawing-style",
  sourceAssetIds: [app.id],
  note: "短视口、桌面和移动端 CAD 画布、证据颜色、尺寸线、剖面和参数布局。",
  recipe: "Responsive CSS"
});
const registrar = addAsset({
  id: "slider-analysis-cad-registrar-r006",
  absolutePath: fileURLToPath(import.meta.url),
  role: "process",
  contentClass: "immutable-gate02-cad-review-registrar",
  sourceAssetIds: [contract.id, cadCore.id, mechanismCore.id],
  note: "保留 rev 5 rejected/requested revision，并登记 rev 6 工程图评审。",
  recipe: "Revision-guarded manifest and history update"
});
const newAssetIds = [contract.id, cadCore.id, mechanismCore.id, cadTests.id, mechanismTests.id, app.id, style.id, registrar.id];

for (const claim of manifest.claims.filter(
  (candidate) => candidate.stageId === "02-analysis"
    && candidate.state === "pending-review"
    && candidate.id.endsWith("-r005")
)) {
  claim.state = "superseded";
  claim.supersededBy = "interactive-cad-review-r006";
  claim.supersededAt = timestamp;
}
const regions = (id) => manifest.claims.find((claim) => claim.id === id)?.sourceRegions || [];
const claimDefinitions = [
  {
    id: "slider-analysis-fixed-upper-moving-lower-r006",
    category: "motion",
    statement: "固定上片 transform 始终为 identity；活动下片承担外滑、回位和旋转。",
    confidence: "user-authoritative",
    sourceRegions: regions("slider-analysis-fixed-upper-moving-lower-r005")
  },
  {
    id: "slider-analysis-axis-attached-to-lower-r006",
    category: "mechanism",
    statement: "下片轴心随下片等距平移；旋转围绕已平移轴心且 pivot drift 为零。",
    confidence: "user-authoritative",
    sourceRegions: regions("slider-analysis-axis-attached-to-lower-r005")
  },
  {
    id: "slider-analysis-bilateral-lower-rails-r006",
    category: "structure",
    statement: "活动下片反面有左右两条纵向轨道/珠列区，并随下片平移和旋转。",
    confidence: "high",
    sourceRegions: regions("slider-analysis-bilateral-lower-rails-r005")
  },
  {
    id: "slider-analysis-one-outward-direction-r006",
    category: "motion",
    statement: "从闭合止点只朝一个外向方向打开，并可沿同一路径关闭。",
    confidence: "high",
    sourceRegions: regions("slider-analysis-one-outward-direction-r005")
  },
  {
    id: "slider-analysis-normalized-evidence-r006",
    category: "scale",
    statement: "当前只锁定 L/W=1.52–1.62、行程 0.38–0.46L/峰值0.50L；物理尺寸、间隙、余量和公差均待实测。",
    confidence: "medium",
    sourceRegions: regions("slider-analysis-normalized-travel-r005")
  },
  {
    id: "slider-analysis-translated-axis-detents-r006",
    category: "mechanism",
    statement: "活动下片绕已平移轴心旋转，强支持 30×12° 分档。",
    confidence: "high",
    sourceRegions: regions("slider-analysis-translated-axis-detents-r005")
  },
  {
    id: "slider-analysis-hidden-coupling-unknown-r006",
    category: "mechanism",
    statement: "上片随动件、销槽、棘轮截面和制造公差没有拆解证据，工程图只能显示红色虚线候选或未知。",
    confidence: "unknown",
    sourceRegions: regions("slider-analysis-exterior-reverse-face-r003")
  }
];
for (const definition of claimDefinitions) {
  manifest.claims.push({
    ...definition,
    stageId: "02-analysis",
    sourceAssetIds: [...new Set(definition.sourceRegions.map((region) => region.assetId))],
    state: "pending-review",
    decisionState: "pending-user-approval",
    analysisRevision: "009",
    assertedBy: "assistant"
  });
}

stage.priorInteractiveReview = {
  analysisEvidenceRevision: 5,
  stageRevision: stage.revision,
  status: "rejected-requested-revision",
  reason: "Visible-browser rotation failed. The SVG exceeded the short viewport; synthetic tests bypassed real hit testing; no large ring existed.",
  artifactIds: [...stage.artifactIds],
  reviewArtifactIds: [...stage.reviewArtifactIds]
};
stage.revision += 1;
stage.status = "ready_for_review";
stage.decision = null;
stage.artifactIds.push(...newAssetIds);
stage.reviewArtifactIds = [contract.id];
stage.analysisSpec = {
  revision: 6,
  reviewMode: "conclusion-first-interactive-vector-cad-mechanism",
  reportingLayers: {
    internal: "full-frame-audio-crop-tracking-calculation-source-validation",
    user: "six-conclusions-synchronized-cad-unknowns-one-decision",
    technicalEvidenceCollapsedByDefault: true,
    defaultScreenshotWall: false
  },
  reviewQuestion: "现在旋转能正常操作，CAD 机构图是否符合实物？",
  userReviewAssetIds: [contract.id],
  internalEvidenceAssetIds: internalEvidence,
  sourceVideoAssetIds: stage.analysisSpec.sourceVideoAssetIds,
  playbackProxyAssetIds: stage.analysisSpec.playbackProxyAssetIds,
  claimIds: claimDefinitions.map((claim) => claim.id),
  rotationFailure: {
    reproducedWithRealBrowserInput: true,
    viewport: { width: 756, height: 469 },
    priorResult: { travelL: 0, angleDeg: 0 },
    rootCause: "old-560px-svg-and-axis-below-469px-viewport-plus-synthetic-pointer-tests-and-no-ring-hit-area"
  },
  cad: {
    coreAssetId: cadCore.id,
    synchronizedViews: ["top", "side", "section-a-a"],
    optionalComponentTree: true,
    scalableVector: true,
    zoomPan: true,
    rotationRing: true,
    ringTracksTranslatedAxis: true,
    detentTicks: 30,
    capsuleTangencyExplicit: true,
    dimensionsCarryEvidenceStatus: true,
    hiddenGeometryDashedUnknown: true,
    shortViewportSupported: true
  },
  physicalInputs: [
    "overallLength", "overallWidth", "totalThickness", "upperThickness", "lowerThickness",
    "closedGap", "railSpacing", "railWidth", "axisDiameter", "upperStepHeight",
    "lowerStepHeight", "clearance", "manufacturingAllowance", "tolerance", "maxTravelMm"
  ],
  physicalInputDefaults: null,
  derivedValuesRequireCompleteInputs: true,
  evidenceParameters: {
    aspectRatioLW: { status: "video-ratio", range: [1.52, 1.62], default: 1.57 },
    travelL: { status: "video-ratio", range: [0.38, 0.46], peak: 0.5 },
    detents: { status: "observed", count: 30, stepDeg: 12 }
  },
  mechanismSandbox: {
    upperOwner: "fixed",
    movingOwner: "lower-carrier",
    axisOwner: "lower-carrier",
    railOwner: "lower-carrier",
    railCount: 2,
    lowerRotatesAroundTranslatedAxis: true,
    pivotDrift: 0,
    resetAngularVelocityDegPerSecond: 0,
    selfMotion: false,
    mouseTouchPointerDriven: true,
    keyboardAccessible: true
  },
  unknowns: [
    "upper follower/contact geometry",
    "pin-slot-ratchet cross-section",
    "physical thickness-gap-step-clearance-allowance-tolerance",
    "force-magnetism-friction-phone-haptic"
  ]
};
stage.validations = stage.validations.filter((validation) => !validation.id.startsWith("browser-"));
stage.validations.push(
  {
    id: "cad-tangency-transform-dimension-state",
    status: "pass",
    evidence: "Deterministic CAD core covers tangent capsule, translated axis, bilateral rails, synchronized views, unknown-safe derivation and zoom/pan."
  },
  {
    id: "real-browser-rotation-root-cause-reproduced",
    status: "pass",
    evidence: "CDP real mouse input reproduced rev 5 at travel=0 and angle=0 in 756×469 before the new ring/viewport fix."
  }
);
for (const downstream of manifest.stages.slice(2, 11)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 02 rev 6 replaces the inaccessible sandbox with an interactive vector CAD review.";
}
manifest.stages[11].status = "blocked";
manifest.stages[11].staleReason = "Gate 12 rejection remains preserved. Gate 02 rev 6 and downstream gates require approval.";
const digest = (values) => crypto.createHash("sha256").update(values.filter(Boolean).sort().join("\n")).digest("hex");
stage.outputDigest = digest(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256));

manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev6-interactive-cad-review-pending";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis = "Gate 01 remains approved. Gate 02 rev 5 is rejected/requested revision because real-browser rotation was inaccessible. Gate 02 rev 6 is ready for review with real mouse/touch rotation, synchronized vector CAD views and honest unknown dimensions. Gates 03–11 are stale; Gate 12 remains blocked/rejected. No Blender, Unity, build, install or phone work ran.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-review-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 6,
  priorRevisionDisposition: "rev5-rejected-requested-revision",
  rotationRootCause: stage.analysisSpec.rotationFailure.rootCause,
  reviewArtifactIds: stage.reviewArtifactIds,
  cadViews: stage.analysisSpec.cad.synchronizedViews,
  physicalInputCount: stage.analysisSpec.physicalInputs.length,
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
