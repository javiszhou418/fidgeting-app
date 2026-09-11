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
const expectedRevision = 121;
const manifest = loadManifest(modelId);
if (manifest.revision !== expectedRevision) {
  throw new Error(`Expected manifest revision ${expectedRevision}, got ${manifest.revision}.`);
}
const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../..");
const toRepoPath = (absolutePath) => path.relative(repoRoot, absolutePath).split(path.sep).join("/");
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.status !== "ready_for_review" || stage.analysisSpec?.revision !== 6) {
  throw new Error("Gate 02 rev 6 must be ready_for_review before rev 7.");
}
const timestamp = new Date().toISOString();
const addAsset = ({ id, absolutePath, role, contentClass, note, sourceAssetIds }) => {
  if (manifest.assets.some((asset) => asset.id === id)) throw new Error(`Duplicate asset ${id}`);
  const asset = {
    id,
    stageId: "02-analysis",
    slot: "analysis-evidence",
    path: toRepoPath(absolutePath),
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role,
    producer: {
      name: "fidgeting-model-pipeline",
      version: "1",
      recipe: "Immutable Gate 02 endpoint-pivot and reference-access revision"
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
  stage.artifactIds.push(asset.id);
  return asset;
};
const contract = addAsset({
  id: "slider-analysis-endpoint-pivot-reference-contract-r007",
  absolutePath: path.join(here, "endpoint-pivot-reference-contract.json"),
  role: "analysis",
  contentClass: "user-authoritative-fixed-endpoint-pivot-and-reference-access-contract",
  note: "轴心固定在底片下端圆帽中心；原图与拆解参考恢复为顶层页签。",
  sourceAssetIds: [
    "slider-intake-user-mechanism-video-6022",
    "slider-intake-user-mechanism-video-6023",
    "slider-intake-user-mechanism-video-6024",
    "slider-intake-haloo-official-05",
    "slider-intake-haloo-official-06",
    "slider-intake-haloo-official-07",
    "slider-intake-haloo-official-08",
    "slider-intake-nxedc-ref-04",
    "slider-intake-nxedc-ref-05",
    "slider-intake-nxedc-ref-06"
  ]
});
const registrar = addAsset({
  id: "slider-analysis-endpoint-pivot-registrar-r007",
  absolutePath: fileURLToPath(import.meta.url),
  role: "process",
  contentClass: "endpoint-pivot-review-registrar",
  note: "登记 rev 6 rejection、rev 7 endpoint pivot、reference tabs 与 downstream stale 状态。",
  sourceAssetIds: [contract.id]
});

const priorAxisClaim = manifest.claims.find((claim) => claim.id === "slider-analysis-axis-attached-to-lower-r006");
if (!priorAxisClaim) throw new Error("Missing rev 6 axis claim.");
priorAxisClaim.state = "superseded";
priorAxisClaim.decisionState = "superseded-by-user-correction";
priorAxisClaim.supersededBy = "slider-analysis-fixed-endpoint-axis-r007";
const endpointClaim = {
  id: "slider-analysis-fixed-endpoint-axis-r007",
  stageId: "02-analysis",
  category: "mechanism",
  statement: "点轴刚性固定在活动底片一个端点，即归一化胶囊下端圆帽中心；axisLocalToLower 恒定，不存在轴心相对底片滑动的第三自由度。",
  confidence: "user-authoritative",
  sourceRegions: priorAxisClaim.sourceRegions,
  sourceAssetIds: [
    ...priorAxisClaim.sourceAssetIds,
    "slider-intake-haloo-official-07",
    "slider-intake-nxedc-ref-04"
  ],
  state: "pending-review",
  decisionState: "pending-user-approval",
  analysisRevision: "010",
  assertedBy: "assistant",
  boundary: "端点位置由 L/W 胶囊相切构造得出，不使用任意像素或已否决毫米值。"
};
manifest.claims.push(endpointClaim);
const carriedClaimIds = stage.analysisSpec.claimIds.filter((id) => id !== priorAxisClaim.id);
stage.analysisSpec = {
  ...stage.analysisSpec,
  revision: 7,
  priorRevisionDisposition: "rev6-rejected-requested-revision",
  reviewMode: "conclusion-first-fixed-endpoint-pivot-cad-with-reference-tabs",
  reviewQuestion: "固定端点轴心与原图参考入口，现在是否符合预期？",
  claimIds: [...carriedClaimIds, endpointClaim.id],
  endpointPivot: {
    owner: "moving-lower-plate",
    attachment: "fixed-bottom-endcap-center",
    derivation: "normalized-capsule-tangency",
    normalizedYFromTopFormula: "1-1/(2*(L/W))",
    axisLocalToLowerInvariant: true,
    axisWorldDeltaEqualsLowerTranslation: true,
    rotationAxisDrift: 0,
    independentAxisDof: false,
    plainLabel: "轴心只随底片整体移动，不在底片上滑动"
  },
  compoundInteraction: {
    ...stage.analysisSpec.compoundInteraction,
    translationDof: "lower-along-fixed-upper-long-axis",
    rotationDof: "lower-about-translated-fixed-endpoint-pivot",
    axisDof: "none"
  },
  referenceAccess: {
    topLevelTabs: ["conclusion", "cad", "references"],
    referenceTabLabel: "原图与拆解参考",
    userVideoCount: 3,
    halooOfficialCount: 4,
    nxedcCount: 4,
    derivedBoardCropCount: 5,
    sourceLabels: ["用户实拍", "官方同款", "外部候选"],
    originalUrls: true,
    repositoryPaths: true,
    openFullSourceActions: true,
    technicalMathCollapsedSeparately: true
  }
};
Object.assign(stage.analysisSpec.mechanismSandbox, {
  axisOwner: "lower-carrier",
  axisAttachment: "fixed-bottom-endcap-center",
  axisLocalToLowerInvariant: true,
  independentAxisDof: false,
  pivotTraversesRailsIndependently: false
});
stage.reviewArtifactIds = [contract.id];
stage.validations.push({
  id: "endpoint-pivot-and-reference-access-contract",
  status: "pass",
  evidence: "Fixed normalized endcap-center axis and top-level original/disassembly reference tab are explicit."
});
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map(
    (id) => manifest.assets.find((asset) => asset.id === id)?.sha256
  ).filter(Boolean).sort().join("\n"))
  .digest("hex");

manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev7-endpoint-pivot-reference-review-pending";
manifest.currentState.diagnosis = "Gate 01 remains approved. Gate 02 rev 6 was rejected; rev 7 is ready for review with a lower-owned fixed bottom-endcap pivot, no independent axis DOF, simultaneous slide+rotation and top-level original/disassembly references. Gates 03–11 remain stale; Gate 12 remains blocked/rejected. No Blender, Unity, build, install or phone work ran.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-endpoint-pivot-reference-review-ready",
  modelId,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 7,
  priorRevisionDisposition: "rev6-rejected-requested-revision",
  userCorrections: [
    "pivot-fixed-at-one-lower-endpoint",
    "restore-top-level-original-and-disassembly-reference-access"
  ],
  endpointClaimId: endpointClaim.id,
  reviewArtifactIds: stage.reviewArtifactIds,
  gateStatus: stage.status,
  downstreamStatus: "gates03-11-stale-gate12-blocked-rejected",
  blenderUnityBuildInstallPhone: "not-started",
  reviewQuestion: stage.analysisSpec.reviewQuestion
});

console.log(JSON.stringify({
  modelId,
  manifestRevision: manifest.revision,
  analysisRevision: stage.analysisSpec.revision,
  status: stage.status,
  reviewQuestion: stage.analysisSpec.reviewQuestion
}, null, 2));
