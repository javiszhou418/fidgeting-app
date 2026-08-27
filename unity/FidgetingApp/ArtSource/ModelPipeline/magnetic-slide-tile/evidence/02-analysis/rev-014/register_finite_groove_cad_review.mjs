#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../../");
const previousDir = path.join(here, "../rev-013");
const correctionPath = path.join(here, "finite-groove-user-correction.md");
const correctionAssetId = "slider-analysis-finite-groove-user-correction-r014";
const contract = JSON.parse(fs.readFileSync(path.join(previousDir, "mechanism-evidence-contract.json"), "utf8"));
contract.revision = 14;
contract.title = "Gate 02 rev 14 · 有限双槽端点、旋转载体与 360° 包络证据合同";
contract.supersedesContractAssetId = "slider-analysis-mechanism-evidence-contract-r013";
contract.supersededConstraintIds = ["MEC-CLOSED-OVERLAP-HARD-STOP"];
contract.constraints = contract.constraints.filter((item) => !contract.supersededConstraintIds.includes(item.id));
contract.constraints.push({
  id: "MEC-FINITE-GROOVE-ENDPOINT-STOPS",
  value: {
    grooveCount: 2,
    grooveOwner: "TopPlate underside",
    followerOwner: "RotatingCarrier",
    followerCount: 2,
    coordinate: "u along top/carrier local longitudinal axis",
    grooveStartNormalizedFromTopL: 0.32,
    grooveEndNormalizedFromTopL: 0.78,
    grooveLengthNormalizedL: 0.46,
    allowedSlideDerivation: "sMin=0 at follower contact with groove start; sMax=grooveEnd-grooveStart",
    sMin: 0,
    sMaxDerived: 0.46,
    closedEndpoint: {
      followerU: 0.32,
      topBottomSilhouettesAlignedAtTheta0: true
    },
    maximumOpenEndpoint: {
      followerU: 0.78,
      followerEngaged: true,
      fixedAxisCovered: true,
      diagrammaticPivotCoverMarginL: 0.22,
      physicalMinimumCoverMarginL: "unknown"
    },
    endpointBehavior: "hard CAD contact; clamp slide only; rotation remains available",
    physicalMillimetres: "unknown"
  },
  units: "normalized L and local groove coordinate u",
  state: "user-authoritative",
  confidence: "locked",
  sourceAssetIds: [
    correctionAssetId,
    "slider-analysis-user-selected-bottom-base-close-r011",
    "slider-intake-haloo-official-07",
    "slider-intake-nxedc-ref-03",
    "slider-intake-nxedc-ref-04"
  ],
  regions: [
    { assetId: correctionAssetId, note: "Whole correction defines finite endpoints and follower-caused stops." },
    { assetId: "slider-analysis-user-selected-bottom-base-close-r011", note: "Supports the covered carrier/axis region." },
    { assetId: "slider-intake-haloo-official-07", note: "Supports bilateral internal contact regions." },
    { assetId: "slider-intake-nxedc-ref-03", note: "External candidate supports concealed finite internal travel." },
    { assetId: "slider-intake-nxedc-ref-04", note: "External internal candidate supports bilateral groove/follower engagement." }
  ],
  decisionNote: "Stops derive from follower contact with finite top-groove endpoints. Rev 13 numeric-only stop semantics are superseded.",
  downstreamConsumers: ["interactive-cad", "blender", "unity", "haptics", "tests", "shipping-review"]
});
contract.constraints.push({
  id: "MEC-TOP-ABOVE-BOTTOM-SWEPT-ENVELOPE",
  value: {
    angleDomainDeg: [0, 360],
    detentSamples: 30,
    detentStepDeg: 12,
    slideDomain: "finite groove start through finite groove end",
    zOrder: {
      BottomExterior: 0,
      RotatingCarrier: 1,
      TopPlate: 2
    },
    topAlwaysAboveBottom: true,
    legalOverhang: true,
    bottomMayClipMaskContainTop: false,
    requiredEndpointChecks: ["closed overlap", "maximum-open pivot coverage", "follower engagement"]
  },
  units: "CAD layer order and sampled swept envelope",
  state: "user-authoritative",
  confidence: "locked",
  sourceAssetIds: [correctionAssetId],
  regions: [{ assetId: correctionAssetId, note: "Whole correction defines invariant top-above-bottom presentation and 360° sweep." }],
  decisionNote: "All 30 detents and legal slide samples must preserve top z-order, follower engagement and pivot coverage.",
  downstreamConsumers: ["interactive-cad", "blender", "unity", "tests", "shipping-review"]
});
const grooveConstraint = contract.constraints.find((item) => item.id === "MEC-TOP-UNDERSIDE-GROOVES");
grooveConstraint.value = {
  ...grooveConstraint.value,
  finite: true,
  stopCause: "CarrierFollowerLeft/Right contact finite groove endpoints",
  lengthSource: "MEC-FINITE-GROOVE-ENDPOINT-STOPS"
};
grooveConstraint.sourceAssetIds = [...new Set([...grooveConstraint.sourceAssetIds, correctionAssetId])];
grooveConstraint.regions.push({ assetId: correctionAssetId, note: "Confirms that both grooves have finite physical endpoints." });
const coverage = contract.constraints.find((item) => item.id === "MEC-AXIS-COVERAGE-AT-MAX-TRAVEL");
coverage.value = {
  ...coverage.value,
  travelSource: "finite groove maximum-open endpoint",
  followerEngagementRequired: true
};
coverage.sourceAssetIds = [...new Set([...coverage.sourceAssetIds, correctionAssetId])];
coverage.regions.push({ assetId: correctionAssetId, note: "Max-open groove endpoint must preserve pivot cover and engagement." });
contract.conclusions = [
  {
    statement: "双槽具有有限起止点，随动点接触端点形成闭合与最大滑开止点",
    constraintIds: ["MEC-FINITE-GROOVE-ENDPOINT-STOPS", "MEC-TOP-UNDERSIDE-GROOVES"],
    confidence: "locked",
    sourceCount: 5
  },
  {
    statement: "合法行程由 grooveEnd−grooveStart 推导，不再复制独立 magic max",
    constraintIds: ["MEC-FINITE-GROOVE-ENDPOINT-STOPS", "MEC-TRAVEL-NORMALIZED"],
    confidence: "locked",
    sourceCount: 1
  },
  {
    statement: "最大滑开端点保持随动件啮合并覆盖固定轴，真实最小余量仍未知",
    constraintIds: ["MEC-FINITE-GROOVE-ENDPOINT-STOPS", "MEC-AXIS-COVERAGE-AT-MAX-TRAVEL"],
    confidence: "locked",
    sourceCount: 2
  },
  {
    statement: "30 个档位与全行程中顶片层级始终高于底片；允许外伸，禁止底片裁切或遮罩顶片",
    constraintIds: ["MEC-TOP-ABOVE-BOTTOM-SWEPT-ENVELOPE", "MEC-COMPOUND-TRANSFORM"],
    confidence: "locked",
    sourceCount: 1
  },
  ...contract.conclusions.slice(3, 6)
];
contract.coverageMatrix.push({
  topic: "finite groove endpoint stops",
  supports: [correctionAssetId, "slider-intake-haloo-official-07", "slider-intake-nxedc-ref-03", "slider-intake-nxedc-ref-04"],
  conflicts: ["rev 13 numeric-only clamp explanation is superseded"],
  unknowns: ["physical endpoint shape", "engagement depth", "millimetre groove length"]
});
contract.coverageMatrix.push({
  topic: "360-degree top-above-bottom swept envelope",
  supports: [correctionAssetId],
  conflicts: [],
  unknowns: ["physical z separation and minimum cover margin"]
});
contract.unknowns = [...new Set([
  ...contract.unknowns,
  "physical groove start/end millimetres and endpoint shape",
  "follower engagement depth at both endpoints",
  "physical z separation between top and bottom exterior surfaces"
])];
contract.downstreamPolicy.rule = "Every CAD and later artifact must record this rev 14 contract SHA-256. Travel derives from finite groove endpoints; top z-order must remain above bottom through the 360-degree sampled envelope.";
const contractPath = path.join(here, "mechanism-evidence-contract.json");
fs.writeFileSync(contractPath, `${JSON.stringify(contract, null, 2)}\n`);
const contractHash = sha256File(contractPath);
const previousConfig = JSON.parse(fs.readFileSync(path.join(previousDir, "interactive-cad-geometry-config.json"), "utf8"));
const config = {
  ...previousConfig,
  revision: 14,
  contractAssetId: "slider-analysis-mechanism-evidence-contract-r014",
  contractSha256: contractHash,
  evidenceSelectors: {
    ...previousConfig.evidenceSelectors,
    finiteGrooveStops: "MEC-FINITE-GROOVE-ENDPOINT-STOPS.value",
    sweptEnvelope: "MEC-TOP-ABOVE-BOTTOM-SWEPT-ENVELOPE.value"
  },
  diagrammaticGeometry: {
    ...previousConfig.diagrammaticGeometry,
    grooveStartFromTopL: 0.32,
    grooveEndFromTopL: 0.78
  },
  cadApprovalChecklist: [
    "finiteGrooveEndpoints",
    "sweptEnvelope",
    "synchronizedViews",
    ...previousConfig.cadApprovalChecklist.filter((item) => item !== "closedStop")
  ],
  finiteGroove: {
    startFromTopL: 0.32,
    endFromTopL: 0.78,
    maxTravelDerivation: "end-start",
    physicalMillimetres: null
  },
  sweptEnvelope: {
    detentCount: 30,
    slideSampleFractions: [0, 0.25, 0.5, 0.75, 1],
    topZ: 2,
    bottomZ: 0,
    bottomMasksTop: false
  }
};
delete config.closedStop;
const configPath = path.join(here, "interactive-cad-geometry-config.json");
fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`);

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 143) throw new Error(`Expected revision 143, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 13) throw new Error("Gate 02 rev 13 must be active.");
const timestamp = new Date().toISOString();
const addAsset = ({ id, filePath, role, contentClass, note, sourceAssetIds = [] }) => {
  const asset = {
    id,
    stageId: "02-analysis",
    slot: "analysis-evidence",
    path: path.relative(repoRoot, filePath).split(path.sep).join("/"),
    sha256: sha256File(filePath),
    exists: true,
    sizeBytes: fs.statSync(filePath).size,
    role,
    producer: { name: "fidgeting-model-pipeline", version: "2026-08-27", recipe: "Gate 02 rev 14 finite-groove endpoint correction" },
    provenance: { origin: role === "user-input" ? "user-provided" : "repository-generated", contentClass, assertedBy: role === "user-input" ? "user" : "assistant", note },
    sourceAssetIds,
    mechanismEvidenceContractSha256: role === "user-input" ? null : contractHash
  };
  manifest.assets.push(asset);
  stage.artifactIds.push(id);
  return asset;
};
const correctionAsset = addAsset({
  id: correctionAssetId,
  filePath: correctionPath,
  role: "user-input",
  contentClass: "user-authoritative-finite-groove-stop-correction",
  note: "Rejects rev 13 numeric-only stop logic and defines finite groove endpoint stops plus top-above-bottom sweep."
});
const contractAsset = addAsset({
  id: "slider-analysis-mechanism-evidence-contract-r014",
  filePath: contractPath,
  role: "analysis",
  contentClass: "authoritative-machine-readable-mechanism-evidence-contract",
  note: "Derives slide limits from finite groove endpoints and adds the 360-degree top-layer sweep.",
  sourceAssetIds: [correctionAsset.id, "slider-analysis-mechanism-evidence-contract-r013"]
});
const configAsset = addAsset({
  id: "slider-analysis-interactive-cad-geometry-config-r014",
  filePath: configPath,
  role: "analysis",
  contentClass: "contract-driven-interactive-cad-geometry-config",
  note: "CAD-only finite-groove endpoint and swept-envelope configuration.",
  sourceAssetIds: [contractAsset.id]
});
addAsset({
  id: "slider-analysis-finite-groove-cad-registrar-r014",
  filePath: fileURLToPath(import.meta.url),
  role: "process",
  contentClass: "deterministic-finite-groove-contract-and-cad-registrar",
  note: "Builds and registers immutable rev 14.",
  sourceAssetIds: [correctionAsset.id]
});
for (const priorId of ["slider-analysis-mechanism-evidence-contract-r013", "slider-analysis-interactive-cad-geometry-config-r013"]) {
  const prior = manifest.assets.find((asset) => asset.id === priorId);
  prior.provenance = {
    ...prior.provenance,
    disposition: "superseded-internal",
    supersededBy: priorId.includes("contract") ? contractAsset.id : configAsset.id
  };
  stage.internalArtifactIds = [...new Set([...(stage.internalArtifactIds || []), priorId])];
}
const priorClaim = manifest.claims.find((claim) => claim.id === "slider-analysis-hard-closed-stop-r013");
priorClaim.state = "superseded";
priorClaim.decisionState = "rejected-stop-logic";
priorClaim.supersededBy = "slider-analysis-finite-groove-endpoint-stops-r014";
manifest.claims.push({
  id: "slider-analysis-finite-groove-endpoint-stops-r014",
  stageId: "02-analysis",
  category: "mechanism-limit",
  statement: "双槽有限；随动点接触槽端点形成 sMin/sMax。闭合端点轮廓重合，最大端点保持啮合和轴心覆盖；全 360° 顶片层级高于底片。",
  confidence: "locked",
  state: "pending-review",
  decisionState: "pending-review",
  sourceAssetIds: [correctionAsset.id],
  sourceRegions: [{ assetId: correctionAsset.id, note: "Whole correction." }],
  unknowns: ["毫米槽长", "端点形状", "啮合深度", "物理盖轴余量", "z 间距"]
});
stage.reviewArtifactIds = [configAsset.id];
stage.status = "ready_for_review";
stage.staleReason = null;
stage.readiness = { ready: true, blockers: [], note: "Complete eleven CAD checks including finite endpoints, synchronized views and the 360-degree swept envelope. Simulator stays locked." };
stage.analysisSpec = {
  ...stage.analysisSpec,
  revision: 14,
  priorRevisionDisposition: "rev13-stop-logic-rejected-carrier-groove-ownership-retained",
  reviewMode: "interactive-cad-finite-groove-endpoints-360-sweep",
  contractAssetId: contractAsset.id,
  contractSha256: contractHash,
  constraintIds: contract.constraints.map((item) => item.id),
  coverageTopics: contract.coverageMatrix.map((item) => item.topic),
  cadArtifactId: configAsset.id,
  cadConfigAssetId: configAsset.id,
  approvalSpec: {
    ...config.approvalRule,
    requiredMilestones: config.cadApprovalChecklist,
    approvalButtonLabel: "确认交互 CAD",
    approvalApiRequired: true
  },
  simulatorGeneration: { locked: true, unlockRequires: "interactive-cad-subapproval-record", label: "交互 CAD 批准后生成", activeControls: 0 }
};
stage.validations.push({
  id: "finite-groove-endpoint-contract-r014",
  status: "pass",
  evidence: "Rev 14 derives sMin/sMax from finite groove endpoint contact and requires a 30-detent top-above-bottom swept envelope."
});
for (const downstream of manifest.stages.slice(2, 11)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 02 rev 14 finite-groove CAD awaits in-workbench subapproval; separate Simulator has not started.";
}
manifest.stages[11].status = "rejected";
manifest.stages[11].staleReason = "Gate 02 CAD and Simulator approvals are incomplete; shipping remains rejected.";
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev14-finite-groove-interactive-cad-subapproval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 14 derives stops from finite groove endpoints and validates the top-above-bottom 360-degree sweep. Simulator and downstream generation remain locked.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-finite-groove-review-ready",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 14,
  correctionAssetId: correctionAsset.id,
  correctionHash: correctionAsset.sha256,
  contractAssetId: contractAsset.id,
  contractHash,
  cadArtifactId: configAsset.id,
  cadArtifactHash: configAsset.sha256,
  requiredMilestones: config.cadApprovalChecklist,
  simulatorState: "locked-not-generated",
  blenderUnityBuildInstallPhone: "not-started"
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  stageRevision: 14,
  contractHash,
  cadArtifactHash: configAsset.sha256
}, null, 2));
