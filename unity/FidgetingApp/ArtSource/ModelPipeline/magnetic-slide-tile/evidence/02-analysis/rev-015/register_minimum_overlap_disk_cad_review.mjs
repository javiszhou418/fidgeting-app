#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../../");
const previousDir = path.join(here, "../rev-014");
const sourceScreenshot = "/Users/jiawei.zhou/.cursor/projects/Users-jiawei-zhou-Documents-Fidgeting-app/assets/image-3e67ea32-c358-44a2-93fc-7d7823a4aba5.png";
const archivedScreenshot = path.join(here, "minimum-overlap-disk-user-screenshot.png");
const correctionPath = path.join(here, "minimum-overlap-disk-user-correction.md");
fs.copyFileSync(sourceScreenshot, archivedScreenshot, fs.constants.COPYFILE_EXCL);

const correctionAssetId = "slider-analysis-minimum-overlap-disk-user-correction-r015";
const screenshotAssetId = "slider-analysis-minimum-overlap-disk-user-screenshot-r015";
const contract = JSON.parse(fs.readFileSync(path.join(previousDir, "mechanism-evidence-contract.json"), "utf8"));
contract.revision = 15;
contract.title = "Gate 02 rev 15 · 最小重叠圆盘连续包含约束";
contract.supersedesContractAssetId = "slider-analysis-mechanism-evidence-contract-r014";
contract.supersededConstraintIds = [...new Set([
  ...(contract.supersededConstraintIds || []),
  "MEC-TOP-ABOVE-BOTTOM-SWEPT-ENVELOPE"
])];
contract.constraints = contract.constraints.filter((item) => item.id !== "MEC-TOP-ABOVE-BOTTOM-SWEPT-ENVELOPE");
const aspectRange = contract.constraints.find((item) => item.id === "MEC-SILHOUETTE-ASPECT").value.aspectRatioLW;
const aspectRatioLW = (aspectRange[0] + aspectRange[1]) / 2;
const topHalfWidthL = 1 / (2 * aspectRatioLW);
const axisNormalizedY = 0.32;
const grooveEndpointLimitL = 0.46;
const overlapContainmentLimitL = 1 - axisNormalizedY - topHalfWidthL;
contract.constraints.push({
  id: "MEC-MINIMUM-OVERLAP-DISK",
  value: {
    componentId: "MinimumOverlapDisk",
    owner: "BottomBase",
    center: "FixedAxis",
    radiusNormalizedL: topHalfWidthL,
    radiusDerivation: "reviewed red-circle radius encoded as current normalized TopPlate half-width W/2",
    physicalRadiusMm: "unknown",
    clearanceMm: "unknown",
    distinctFrom: ["FixedAxis point", "BottomExterior outline"],
    containment: "MinimumOverlapDisk subset-of TopPlateFootprint(s,theta)",
    boundaryContact: "legal overlap limit",
    penetrationOrExposure: "invalid"
  },
  units: "normalized L; physical mm unknown",
  state: "user-authoritative",
  confidence: "locked",
  sourceAssetIds: [correctionAssetId, screenshotAssetId],
  regions: [
    { assetId: screenshotAssetId, normalizedRect: [0.16, 0.09, 0.73, 0.81], note: "User identifies the red circle as the mandatory minimum overlap disk." },
    { assetId: correctionAssetId, note: "Whole correction defines ownership, containment and boundary semantics." }
  ],
  decisionNote: "The reviewed red-circle size is encoded as a normalized CAD parameter. Its physical radius remains unknown.",
  downstreamConsumers: ["interactive-cad", "blender", "unity", "tests", "shipping-review"]
});
contract.constraints.push({
  id: "MEC-ACTUAL-TRAVEL-DUAL-BOUND",
  value: {
    grooveEndpointLimitL,
    overlapContainmentLimitL,
    actualSMaxL: Math.min(grooveEndpointLimitL, overlapContainmentLimitL),
    formula: "sMax(theta)=min(grooveEndpointLimit, overlapContainmentLimit(theta))",
    capsuleContainmentFormula: "margin=min(W/(2L)-r, axisY+s-r, 1-axisY-s-r)",
    angleInvariant: true,
    angleInvariantProof: "Apply inverse R_fixedAxis(theta): the axis-centered disk is rotation-invariant and TopPlate becomes an untranslated-orientation capsule shifted only by local s.",
    activeLimit: "MinimumOverlapDisk",
    clampPolicy: "clamp slide before negative margin; retain rotation only while containment remains valid"
  },
  units: "normalized L",
  state: "user-authoritative",
  confidence: "locked",
  sourceAssetIds: [correctionAssetId, screenshotAssetId, "slider-analysis-finite-groove-user-correction-r014"],
  regions: [
    { assetId: screenshotAssetId, normalizedRect: [0.16, 0.09, 0.73, 0.81], note: "Red disk supplies the second geometric travel bound." },
    { assetId: correctionAssetId, note: "Defines min-of-two-bounds travel." },
    { assetId: "slider-analysis-finite-groove-user-correction-r014", note: "Retains finite groove endpoint as the first candidate bound." }
  ],
  decisionNote: "For current normalized values, disk containment limits travel to 0.361529L before the 0.46L groove endpoint.",
  downstreamConsumers: ["interactive-cad", "blender", "unity", "tests", "shipping-review"]
});
contract.constraints.push({
  id: "MEC-CONTINUOUS-OVERLAP-CONTAINMENT",
  value: {
    analyticCheck: true,
    denseSweepDegrees: 1,
    angleSamples: 360,
    continuousTravelBoundaryCheck: true,
    invalidMarginRule: "margin < 0 invalid",
    renderTruthRule: "no SVG clipping, z-order trick, or mask may hide exposed red disk",
    debugInvalidPresentation: "flashing/error red uncovered disk"
  },
  units: "analytic normalized geometry plus dense degrees",
  state: "user-authoritative",
  confidence: "locked",
  sourceAssetIds: [correctionAssetId, screenshotAssetId],
  regions: [
    { assetId: screenshotAssetId, normalizedRect: [0.16, 0.09, 0.73, 0.81], note: "Defines the visible disk whose exposure must remain truthful." },
    { assetId: correctionAssetId, note: "Requires analytic containment plus dense full-360 validation." }
  ],
  decisionNote: "Sparse 30×5 sweep is supplementary only; analytic containment gates every pose.",
  downstreamConsumers: ["interactive-cad", "tests", "shipping-review"]
});
contract.conclusions = [
  {
    statement: "红色 MinimumOverlapDisk 固定属于底座并以固定轴为圆心，必须始终完整包含在顶片足迹内",
    constraintIds: ["MEC-MINIMUM-OVERLAP-DISK"],
    confidence: "locked",
    sourceCount: 2
  },
  {
    statement: "当前 sMax=min(0.46L 双槽端点, 0.361529L 圆盘包含)=0.361529L，由最小重叠圆盘限制",
    constraintIds: ["MEC-ACTUAL-TRAVEL-DUAL-BOUND", "MEC-FINITE-GROOVE-ENDPOINT-STOPS"],
    confidence: "locked",
    sourceCount: 3
  },
  {
    statement: "圆盘以轴心为中心且顶片与局部滑轴共同旋转；逆旋转后包含问题只依赖 s，因此当前限制对 θ 不变",
    constraintIds: ["MEC-ACTUAL-TRAVEL-DUAL-BOUND", "MEC-COMPOUND-TRANSFORM"],
    confidence: "locked",
    sourceCount: 2
  },
  {
    statement: "解析 capsule containment 是主门禁，360 个 1° 样本用于补充验证；负余量姿态禁止进入",
    constraintIds: ["MEC-CONTINUOUS-OVERLAP-CONTAINMENT"],
    confidence: "locked",
    sourceCount: 2
  },
  ...contract.conclusions.slice(0, 3)
];
contract.coverageMatrix.push({
  topic: "minimum overlap disk containment",
  supports: [correctionAssetId, screenshotAssetId],
  conflicts: ["rev 14 pivot-point coverage is insufficient"],
  unknowns: ["physical disk radius", "physical clearance", "physical minimum margin"]
});
contract.coverageMatrix.push({
  topic: "dual-bound angle-invariant travel",
  supports: [correctionAssetId, screenshotAssetId, "slider-analysis-finite-groove-user-correction-r014"],
  conflicts: ["rev 14 groove-only sMax is superseded"],
  unknowns: ["measured groove endpoint", "measured disk radius"]
});
contract.unknowns = [...new Set([
  ...contract.unknowns,
  "physical MinimumOverlapDisk radius and clearance",
  "measured disk-to-top cover margin",
  "whether production disk radius equals normalized W/2 after physical measurement"
])];
contract.downstreamPolicy.rule = "Every later artifact records rev 15 hash and enforces analytic MinimumOverlapDisk containment before rendering or motion.";
const contractPath = path.join(here, "mechanism-evidence-contract.json");
fs.writeFileSync(contractPath, `${JSON.stringify(contract, null, 2)}\n`);
const contractHash = sha256File(contractPath);

const previousConfig = JSON.parse(fs.readFileSync(path.join(previousDir, "interactive-cad-geometry-config.json"), "utf8"));
const config = {
  ...previousConfig,
  revision: 15,
  contractAssetId: "slider-analysis-mechanism-evidence-contract-r015",
  contractSha256: contractHash,
  evidenceSelectors: {
    ...previousConfig.evidenceSelectors,
    minimumOverlapDisk: "MEC-MINIMUM-OVERLAP-DISK.value",
    actualTravelDualBound: "MEC-ACTUAL-TRAVEL-DUAL-BOUND.value",
    continuousContainment: "MEC-CONTINUOUS-OVERLAP-CONTAINMENT.value"
  },
  diagrammaticGeometry: {
    ...previousConfig.diagrammaticGeometry,
    minimumOverlapDiskRadiusL: topHalfWidthL
  },
  componentLayers: [
    ...previousConfig.componentLayers.slice(0, 2),
    "MinimumOverlapDisk",
    ...previousConfig.componentLayers.slice(2)
  ],
  cadApprovalChecklist: [
    "minimumOverlapDisk",
    "robustContainment",
    ...previousConfig.cadApprovalChecklist.filter((item) => item !== "sweptEnvelope")
  ],
  overlapDisk: {
    radiusNormalizedL: topHalfWidthL,
    physicalRadiusMm: null,
    sourceStatus: "用户输入 · reviewed CAD normalized",
    denseSweepDegrees: 1
  }
};
const configPath = path.join(here, "interactive-cad-geometry-config.json");
fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`);

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 147) throw new Error(`Expected revision 147, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 14) throw new Error("Gate 02 rev 14 must be active.");
const timestamp = new Date().toISOString();
const addAsset = ({ id, filePath, role, contentClass, note, sourceAssetIds = [] }) => {
  const asset = {
    id, stageId: "02-analysis", slot: "analysis-evidence",
    path: path.relative(repoRoot, filePath).split(path.sep).join("/"),
    sha256: sha256File(filePath), exists: true, sizeBytes: fs.statSync(filePath).size,
    role,
    producer: { name: "fidgeting-model-pipeline", version: "2026-08-27", recipe: "Gate 02 rev 15 minimum overlap disk" },
    provenance: { origin: role === "user-input" ? "user-provided" : "repository-generated", contentClass, assertedBy: role === "user-input" ? "user" : "assistant", note },
    sourceAssetIds,
    mechanismEvidenceContractSha256: role === "user-input" ? null : contractHash
  };
  manifest.assets.push(asset);
  stage.artifactIds.push(id);
  return asset;
};
const screenshotAsset = addAsset({
  id: screenshotAssetId, filePath: archivedScreenshot, role: "user-input",
  contentClass: "user-annotated-minimum-overlap-disk-cad-screenshot",
  note: "User identifies the red circle as the mandatory minimum overlap disk."
});
const correctionAsset = addAsset({
  id: correctionAssetId, filePath: correctionPath, role: "user-input",
  contentClass: "user-authoritative-minimum-overlap-disk-correction",
  note: "Rejects rev 14 groove-only travel and defines continuous disk containment.",
  sourceAssetIds: [screenshotAsset.id]
});
const contractAsset = addAsset({
  id: "slider-analysis-mechanism-evidence-contract-r015", filePath: contractPath, role: "analysis",
  contentClass: "authoritative-machine-readable-mechanism-evidence-contract",
  note: "Adds MinimumOverlapDisk and dual-bound analytic travel.",
  sourceAssetIds: [correctionAsset.id, screenshotAsset.id, "slider-analysis-mechanism-evidence-contract-r014"]
});
const configAsset = addAsset({
  id: "slider-analysis-interactive-cad-geometry-config-r015", filePath: configPath, role: "analysis",
  contentClass: "contract-driven-interactive-cad-geometry-config",
  note: "CAD-only minimum overlap disk and continuous containment config.",
  sourceAssetIds: [contractAsset.id]
});
addAsset({
  id: "slider-analysis-minimum-overlap-disk-cad-registrar-r015", filePath: fileURLToPath(import.meta.url), role: "process",
  contentClass: "deterministic-minimum-overlap-disk-registrar",
  note: "Archives the user screenshot and registers immutable rev 15.",
  sourceAssetIds: [correctionAsset.id, screenshotAsset.id]
});
for (const priorId of ["slider-analysis-mechanism-evidence-contract-r014", "slider-analysis-interactive-cad-geometry-config-r014"]) {
  const prior = manifest.assets.find((asset) => asset.id === priorId);
  prior.provenance = { ...prior.provenance, disposition: "superseded-internal", supersededBy: priorId.includes("contract") ? contractAsset.id : configAsset.id };
  stage.internalArtifactIds = [...new Set([...(stage.internalArtifactIds || []), priorId])];
}
const priorClaim = manifest.claims.find((claim) => claim.id === "slider-analysis-finite-groove-endpoint-stops-r014");
priorClaim.state = "superseded";
priorClaim.decisionState = "rejected-groove-only-maximum";
priorClaim.supersededBy = "slider-analysis-minimum-overlap-disk-r015";
manifest.claims.push({
  id: "slider-analysis-minimum-overlap-disk-r015", stageId: "02-analysis", category: "mechanism-limit",
  statement: "MinimumOverlapDisk 必须在每个合法姿态完整包含于顶片；实际 sMax 是槽端点与圆盘包含上限的较小值。",
  confidence: "locked", state: "pending-review", decisionState: "pending-review",
  sourceAssetIds: [correctionAsset.id, screenshotAsset.id],
  sourceRegions: [{ assetId: screenshotAsset.id, normalizedRect: [0.16, 0.09, 0.73, 0.81], note: "Red disk." }],
  unknowns: ["物理圆盘半径", "毫米间隙", "真实最小余量"]
});
stage.reviewArtifactIds = [configAsset.id];
stage.status = "ready_for_review";
stage.staleReason = null;
stage.readiness = { ready: true, blockers: [], note: "Complete twelve CAD checks including analytic overlap containment. Simulator stays locked." };
stage.analysisSpec = {
  ...stage.analysisSpec,
  revision: 15,
  priorRevisionDisposition: "rev14-groove-only-maximum-rejected-finite-groove-retained-as-candidate-bound",
  reviewMode: "interactive-cad-minimum-overlap-disk-containment",
  contractAssetId: contractAsset.id,
  contractSha256: contractHash,
  constraintIds: contract.constraints.map((item) => item.id),
  coverageTopics: contract.coverageMatrix.map((item) => item.topic),
  cadArtifactId: configAsset.id,
  cadConfigAssetId: configAsset.id,
  approvalSpec: { ...config.approvalRule, requiredMilestones: config.cadApprovalChecklist, approvalButtonLabel: "确认交互 CAD", approvalApiRequired: true },
  simulatorGeneration: { locked: true, unlockRequires: "interactive-cad-subapproval-record", label: "交互 CAD 批准后生成", activeControls: 0 }
};
stage.validations.push({ id: "minimum-overlap-disk-contract-r015", status: "pass", evidence: "Rev 15 encodes analytic disk containment and min-of-two-bounds travel." });
for (const downstream of manifest.stages.slice(2, 11)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 02 rev 15 minimum-overlap CAD awaits in-workbench subapproval; Simulator has not started.";
}
manifest.stages[11].status = "rejected";
manifest.stages[11].staleReason = "Gate 02 CAD and Simulator approvals are incomplete.";
stage.outputDigest = crypto.createHash("sha256").update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n")).digest("hex");
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev15-minimum-overlap-disk-interactive-cad-subapproval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 15 adds analytic MinimumOverlapDisk containment and dual-bound travel. Simulator and downstream generation remain locked.";
saveManifest(manifest, {
  id: crypto.randomUUID(), type: "stage-interactive-cad-minimum-overlap-review-ready",
  modelId: manifest.model.id, manifestRevision: manifest.revision, timestamp, stageId: "02-analysis",
  analysisEvidenceRevision: 15, screenshotAssetId: screenshotAsset.id, screenshotHash: screenshotAsset.sha256,
  correctionAssetId: correctionAsset.id, contractAssetId: contractAsset.id, contractHash,
  cadArtifactId: configAsset.id, cadArtifactHash: configAsset.sha256,
  requiredMilestones: config.cadApprovalChecklist,
  simulatorState: "locked-not-generated", blenderUnityBuildInstallPhone: "not-started"
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  stageRevision: 15,
  contractHash,
  cadArtifactHash: configAsset.sha256,
  minimumOverlapDiskRadiusL: topHalfWidthL,
  overlapContainmentLimitL,
  actualSMaxL: Math.min(grooveEndpointLimitL, overlapContainmentLimitL)
}, null, 2));
