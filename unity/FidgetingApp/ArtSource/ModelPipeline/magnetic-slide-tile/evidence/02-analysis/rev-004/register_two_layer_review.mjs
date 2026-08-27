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
const expectedRevision = 113;
const manifest = loadManifest(modelId);
if (manifest.revision !== expectedRevision) {
  throw new Error(`Expected manifest revision ${expectedRevision}, got ${manifest.revision}.`);
}

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../..");
const resolveRepoPath = (repoPath) => path.join(repoRoot, repoPath);
const toRepoPath = (absolutePath) => path.relative(repoRoot, absolutePath).split(path.sep).join("/");
const digestValues = (values) => crypto.createHash("sha256")
  .update(values.filter(Boolean).sort().join("\n"))
  .digest("hex");
const timestamp = new Date().toISOString();

const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.status !== "ready_for_review" || stage.analysisSpec?.revision !== 3) {
  throw new Error("Gate 02 rev 3 must remain ready_for_review before revision.");
}

const assetIds = new Set(manifest.assets.map((asset) => asset.id));
const addAsset = ({ id, slot, absolutePath, role, contentClass, sourceAssetIds, note, recipe }) => {
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
    producer: {
      name: "fidgeting-model-pipeline",
      version: "1",
      recipe
    },
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

const videoIds = [
  "slider-intake-user-mechanism-video-6022",
  "slider-intake-user-mechanism-video-6023",
  "slider-intake-user-mechanism-video-6024"
];
const internalEvidenceIds = [
  "slider-analysis-frame-survey-report-r003",
  "slider-analysis-mechanism-findings-r003",
  "slider-analysis-img-6022-frame-manifest-json-r003",
  "slider-analysis-img-6023-frame-manifest-json-r003",
  "slider-analysis-img-6024-frame-manifest-json-r003",
  "slider-analysis-audio-contact-sheet-r003",
  "slider-analysis-key-frame-manifest-r003",
  "slider-analysis-validation-report-r003"
];

const conclusionAsset = addAsset({
  id: "slider-analysis-conclusion-review-r004",
  slot: "analysis-board",
  absolutePath: path.join(here, "mechanism-review-conclusions.json"),
  role: "analysis",
  contentClass: "conclusion-first-interactive-review-contract",
  sourceAssetIds: internalEvidenceIds,
  note: "默认用户层只显示六条结论、可信度、未知项、决策问题与交互沙盒边界；不显示截图墙。",
  recipe: "Two-layer Gate 02 review contract"
});
const proportionAsset = addAsset({
  id: "slider-analysis-proportion-analysis-r004",
  slot: "analysis-evidence",
  absolutePath: path.join(here, "normalized-proportion-analysis.json"),
  role: "analysis",
  contentClass: "perspective-corrected-normalized-proportion-analysis",
  sourceAssetIds: videoIds,
  note: "只记录 L/W 和 travel/L 推断范围；实体长宽厚和毫米行程保持 unknown。",
  recipe: "Multi-frame silhouette range with perspective and occlusion uncertainty"
});
const sandboxCoreAsset = addAsset({
  id: "slider-analysis-mechanism-sandbox-core-r004",
  slot: "analysis-evidence",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/mechanism-sandbox-core.mjs"),
  role: "process",
  contentClass: "deterministic-mechanism-sandbox-core",
  sourceAssetIds: [conclusionAsset.id, proportionAsset.id],
  note: "独立于 UI 的确定性滑动、分档、breakaway、阻尼、捕获和止点核心。",
  recipe: "Pure JavaScript state transition core"
});
const sandboxTestAsset = addAsset({
  id: "slider-analysis-mechanism-sandbox-tests-r004",
  slot: "analysis-evidence",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/tests/mechanism-sandbox.test.mjs"),
  role: "validation",
  contentClass: "deterministic-mechanism-sandbox-unit-tests",
  sourceAssetIds: [sandboxCoreAsset.id],
  note: "覆盖 30×12°、零自转、半衰期阻尼、breakaway/capture、单向滑动、关闭、止点、clamp、角度包裹、reset 和参数变化。",
  recipe: "Node test runner"
});
const appAsset = addAsset({
  id: "slider-analysis-mechanism-sandbox-ui-r004",
  slot: "analysis-evidence",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/app.js"),
  role: "process",
  contentClass: "interactive-mechanism-review-ui",
  sourceAssetIds: [sandboxCoreAsset.id, conclusionAsset.id],
  note: "鼠标／pointer 驱动的滑动与旋转沙盒、实时状态、调参、可选声音和折叠技术证据。",
  recipe: "Model Provenance Explorer module UI"
});
const styleAsset = addAsset({
  id: "slider-analysis-mechanism-sandbox-style-r004",
  slot: "analysis-evidence",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/styles.css"),
  role: "process",
  contentClass: "responsive-conclusion-first-review-style",
  sourceAssetIds: [appAsset.id],
  note: "桌面与移动端结论、沙盒、参数区和折叠证据布局。",
  recipe: "Responsive CSS"
});
const registrarAsset = addAsset({
  id: "slider-analysis-two-layer-registrar-r004",
  slot: "analysis-evidence",
  absolutePath: fileURLToPath(import.meta.url),
  role: "process",
  contentClass: "immutable-gate02-review-revision-registrar",
  sourceAssetIds: [conclusionAsset.id, proportionAsset.id, sandboxCoreAsset.id],
  note: "保留 rev 3 内部证据并登记 rev 4 结论优先交互评审。",
  recipe: "Revision-guarded manifest and history update"
});
const newAssetIds = [
  conclusionAsset.id,
  proportionAsset.id,
  sandboxCoreAsset.id,
  sandboxTestAsset.id,
  appAsset.id,
  styleAsset.id,
  registrarAsset.id
];

const priorRev3Claims = manifest.claims.filter(
  (claim) => claim.stageId === "02-analysis"
    && claim.state === "pending-review"
    && claim.id.endsWith("-r003")
);
for (const claim of priorRev3Claims) {
  claim.state = "superseded";
  claim.supersededBy = "two-layer-interactive-review-r004";
  claim.supersededAt = timestamp;
}

const copyRegions = (id) => manifest.claims.find((claim) => claim.id === id)?.sourceRegions || [];
const claimDefinitions = [
  {
    id: "slider-analysis-one-outward-direction-r004",
    category: "motion",
    statement: "从闭合止点只朝一个外向方向打开，并可沿同一路径关闭；负行程和越过闭合止点均不允许。",
    confidence: "high",
    sourceRegions: copyRegions("slider-analysis-one-outward-direction-r003")
  },
  {
    id: "slider-analysis-compound-constraint-r004",
    category: "mechanism",
    statement: "两片受候选点轴与纵向轨迹共同约束；隐藏轴销和槽壁截面仍 unknown。",
    confidence: "high",
    sourceRegions: copyRegions("slider-analysis-compound-axis-track-r003")
  },
  {
    id: "slider-analysis-normalized-travel-r004",
    category: "scale",
    statement: "视频支持行程约 0.38–0.46L、峰值约 0.50L；实体毫米行程 unknown。",
    confidence: "medium",
    sourceRegions: copyRegions("slider-analysis-normalized-travel-r003")
  },
  {
    id: "slider-analysis-detent-map-r004",
    category: "mechanism",
    statement: "旋转强支持 12° 每档、360° 共 30 档；沙盒与后续物理/Haptic 设置必须共用该档位数。",
    confidence: "high",
    sourceRegions: copyRegions("slider-analysis-twelve-degree-detents-r003")
  },
  {
    id: "slider-analysis-rotation-across-slide-r004",
    category: "motion",
    statement: "部分滑开和接近最大滑开状态均观察到旋转；每个精确滑位是否允许旋转 unknown。",
    confidence: "high",
    sourceRegions: copyRegions("slider-analysis-rotation-across-slide-r003")
  },
  {
    id: "slider-analysis-candidate-axis-owner-r004",
    category: "structure",
    statement: "承载片承担固定点是当前中等可信候选，不是已见的隐藏结构事实。",
    confidence: "medium",
    sourceRegions: copyRegions("slider-analysis-carrier-cover-roles-r003")
  },
  {
    id: "slider-analysis-normalized-aspect-r004",
    category: "scale",
    statement: "经多帧透视与遮挡不确定性校正，L/W 推断范围为 1.52–1.62，沙盒使用中值 1.57；实体 L、W、厚度均 unknown。",
    confidence: "medium",
    sourceRegions: [
      {
        assetId: "slider-intake-user-mechanism-video-6023",
        frameIndex: 0,
        ptsSeconds: 0,
        normalizedRect: [0.26, 0.34, 0.58, 0.58]
      },
      {
        assetId: "slider-intake-user-mechanism-video-6023",
        frameIndex: 12,
        ptsSeconds: 0.4,
        normalizedRect: [0.24, 0.3, 0.6, 0.62]
      },
      {
        assetId: "slider-intake-user-mechanism-video-6024",
        frameIndex: 0,
        ptsSeconds: 0,
        normalizedRect: [0.18, 0.3, 0.52, 0.5]
      }
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
    analysisRevision: "007",
    assertedBy: "assistant"
  });
}

stage.priorVideoAnalysisReview = {
  analysisEvidenceRevision: 3,
  stageRevision: stage.revision,
  status: "rejected-requested-revision",
  reason: "User rejected screenshot-heavy review and any diagram that implied unsupported dimensions. Full frame/audio evidence remains valid as internal evidence.",
  artifactIds: [...stage.artifactIds],
  reviewArtifactIds: [...stage.reviewArtifactIds]
};
stage.revision += 1;
stage.status = "ready_for_review";
stage.decision = null;
stage.artifactIds.push(...newAssetIds);
stage.reviewArtifactIds = [conclusionAsset.id];
stage.validations = [
  ...stage.validations.filter((validation) => validation.id !== "browser-desktop-modal-mobile-video-playback"),
  {
    id: "two-layer-reporting-boundary",
    status: "pass",
    evidence: "Default review contains six conclusion cards, unknowns, one decision and an interactive sandbox. Full frame/audio evidence remains collapsed and source-linked."
  },
  {
    id: "normalized-dimension-boundary",
    status: "pass",
    evidence: "Current review uses L/W and travel/L ranges only. Physical length, width, thickness and travel remain unknown with optional empty measurement fields."
  },
  {
    id: "deterministic-sandbox-core-present",
    status: "pass",
    evidence: "UI imports a separate deterministic mechanism core with zero-motion reset, 30×12° mapping, half-life damping, breakaway, capture and bounded one-direction slide."
  }
];
stage.analysisSpec = {
  revision: 4,
  reviewMode: "conclusion-first-interactive-mechanism-sandbox",
  reportingLayers: {
    internal: "full-frame-audio-crop-tracking-calculation-source-validation",
    user: "six-conclusions-unknowns-one-decision-interactive-demo",
    technicalEvidenceCollapsedByDefault: true,
    defaultScreenshotWall: false
  },
  reviewQuestion: "在沙盒里试过后，这个滑动方向、轴心位置和 30 档旋转是否符合实物？",
  userReviewAssetIds: [conclusionAsset.id],
  internalEvidenceAssetIds: internalEvidenceIds,
  sourceVideoAssetIds: videoIds,
  playbackProxyAssetIds: [
    "slider-analysis-img-6022-playback-proxy-r003",
    "slider-analysis-img-6023-playback-proxy-r003",
    "slider-analysis-img-6024-playback-proxy-r003"
  ],
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
    coreAssetId: sandboxCoreAsset.id,
    detentCount: 30,
    detentStepDeg: 12,
    resetAngularVelocityDegPerSecond: 0,
    selfMotion: false,
    pointerDriven: true,
    supportedRotationTravelStates: ["partial", "near-maximum"],
    unsupportedCouplingAssumptionsMarked: true,
    desktopForceClaimed: false,
    phoneHapticClaimed: false
  },
  unknowns: [
    "hidden pin ownership",
    "slot wall cross-section",
    "rotation at every exact travel position",
    "physical dimensions and force",
    "phone Haptic"
  ]
};
stage.inputDigest = digestValues(videoIds.map(
  (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256
));
stage.outputDigest = digestValues(stage.artifactIds.map(
  (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256
));

for (const downstream of manifest.stages.slice(2, 11)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 02 rev 4 replaces unsupported physical dimensions with normalized evidence and requires interactive mechanism approval.";
}
manifest.stages[11].status = "blocked";
manifest.stages[11].staleReason = "Gate 12 rev 1 rejection remains preserved. Gate 02 rev 4 and all downstream gates require approval before shipping review.";

manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev4-interactive-mechanism-review-pending";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis = "Gate 01 remains approved. Gate 02 rev 3 user presentation is rejected/requested revision while its full frame/audio evidence remains internal. Gate 02 rev 4 is ready for review with normalized proportions and a deterministic interactive mechanism sandbox. Gates 03–11 are stale; Gate 12 remains blocked/rejected; no Blender, Unity, build, install or phone work ran.";

saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-two-layer-interactive-review-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 4,
  priorRevisionDisposition: "rev3-user-presentation-rejected-internal-evidence-preserved",
  reviewArtifactIds: stage.reviewArtifactIds,
  internalEvidenceAssetIds: internalEvidenceIds,
  claimIds: claimDefinitions.map((claim) => claim.id),
  normalizedAspectRatioLW: [1.52, 1.62],
  normalizedTravelRangeL: [0.38, 0.46],
  observedPeakTravelL: 0.5,
  detentCount: 30,
  detentStepDeg: 12,
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
