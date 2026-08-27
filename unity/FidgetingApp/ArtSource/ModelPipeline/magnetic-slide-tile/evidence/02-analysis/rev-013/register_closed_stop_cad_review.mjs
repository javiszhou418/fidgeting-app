#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../../");
const previousDir = path.join(here, "../rev-012");
const correctionPath = path.join(here, "closed-stop-user-correction.md");
const correctionAssetId = "slider-analysis-closed-stop-user-correction-r013";
const contract = JSON.parse(fs.readFileSync(path.join(previousDir, "mechanism-evidence-contract.json"), "utf8"));
contract.revision = 13;
contract.title = "Gate 02 rev 13 · 旋转载体、顶片双槽与闭合硬限位证据合同";
contract.supersedesContractAssetId = "slider-analysis-mechanism-evidence-contract-r012";
contract.supersededConstraintIds = [];
contract.constraints.push({
  id: "MEC-CLOSED-OVERLAP-HARD-STOP",
  value: {
    coordinate: "s",
    closedValue: 0,
    allowedRange: { min: 0, maxSelector: "MEC-TRAVEL-NORMALIZED.value.supportedRange.max" },
    negativeTravelForbidden: true,
    closedThetaDeg: 0,
    closedSilhouetteRule: "TopPlate exterior capsule coincides with BottomExterior capsule",
    vectorTolerance: 1e-9,
    inwardPointerAtStop: "translation-clamped-rotation-still-allowed",
    behaviorType: "hard-cad-kinematic-constraint",
    excludedBehavior: ["bounce", "force", "softness", "damping", "friction", "haptic"]
  },
  units: "normalized L and degrees",
  state: "user-authoritative",
  confidence: "locked",
  sourceAssetIds: [correctionAssetId],
  regions: [{ assetId: correctionAssetId, note: "Whole user correction defines the closed overlap plane and hard nonnegative slide domain." }],
  decisionNote: "Rev 12 mechanism ownership is partially accepted. Rev 13 adds an exact closed overlap state and forbids top penetration below the fixed bottom.",
  downstreamConsumers: ["interactive-cad", "blender", "unity", "haptics", "tests", "shipping-review"]
});
const compound = contract.constraints.find((item) => item.id === "MEC-COMPOUND-TRANSFORM");
compound.decisionNote = `${compound.decisionNote} The slide channel is hard-clamped to s>=0; a tangential pointer component may still change theta at the closed stop.`;
compound.sourceAssetIds = [...new Set([...compound.sourceAssetIds, correctionAssetId])];
compound.regions.push({ assetId: correctionAssetId, note: "Compound motion remains valid, but the translation channel cannot cross the closed plane." });
contract.conclusions = [
  {
    statement: "闭合时 s=0、θ=0°，顶片与底片外轮廓精确重合",
    constraintIds: ["MEC-CLOSED-OVERLAP-HARD-STOP", "MEC-SILHOUETTE-ASPECT"],
    confidence: "locked",
    sourceCount: 1
  },
  {
    statement: "所有输入均限制在 0≤s≤sMax，负行程物理禁止",
    constraintIds: ["MEC-CLOSED-OVERLAP-HARD-STOP", "MEC-TRAVEL-NORMALIZED"],
    confidence: "locked",
    sourceCount: 1
  },
  {
    statement: "闭合止点只钳制平移；带切向分量的手势仍可旋转",
    constraintIds: ["MEC-CLOSED-OVERLAP-HARD-STOP", "MEC-COMPOUND-TRANSFORM"],
    confidence: "locked",
    sourceCount: 1
  },
  ...contract.conclusions.slice(0, 4)
];
contract.coverageMatrix.push({
  topic: "closed overlap plane and nonnegative slide",
  supports: [correctionAssetId],
  conflicts: [],
  unknowns: ["physical contact force and stop feel belong to the later Simulator"]
});
contract.unknowns = [...new Set([
  ...contract.unknowns,
  "physical closed-stop force, bounce, compliance and acoustic response"
])];
contract.downstreamPolicy.rule = "Every CAD and later artifact must record this rev 13 contract SHA-256. The hard CAD domain is 0<=s<=sMax. CAD approval unlocks only a separate Simulator.";
const contractPath = path.join(here, "mechanism-evidence-contract.json");
fs.writeFileSync(contractPath, `${JSON.stringify(contract, null, 2)}\n`);
const contractHash = sha256File(contractPath);
const previousConfig = JSON.parse(fs.readFileSync(path.join(previousDir, "interactive-cad-geometry-config.json"), "utf8"));
const config = {
  ...previousConfig,
  revision: 13,
  contractAssetId: "slider-analysis-mechanism-evidence-contract-r013",
  contractSha256: contractHash,
  evidenceSelectors: {
    ...previousConfig.evidenceSelectors,
    closedStop: "MEC-CLOSED-OVERLAP-HARD-STOP.value"
  },
  cadApprovalChecklist: [
    "closedStop",
    ...previousConfig.cadApprovalChecklist
  ],
  closedStop: {
    s: 0,
    thetaDeg: 0,
    negativeTravelForbidden: true,
    vectorTolerance: 1e-9,
    label: "闭合限位：顶片与底片完全重合，不得继续向下"
  }
};
const configPath = path.join(here, "interactive-cad-geometry-config.json");
fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`);

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 136) throw new Error(`Expected revision 136, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 12) throw new Error("Gate 02 rev 12 must be active.");
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
    producer: { name: "fidgeting-model-pipeline", version: "2026-08-26", recipe: "Gate 02 rev 13 hard closed-stop correction" },
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
  contentClass: "user-authoritative-hard-closed-stop-correction",
  note: "Partially accepts rev 12 mechanism principle and adds the exact overlap stop at s=0."
});
const contractAsset = addAsset({
  id: "slider-analysis-mechanism-evidence-contract-r013",
  filePath: contractPath,
  role: "analysis",
  contentClass: "authoritative-machine-readable-mechanism-evidence-contract",
  note: "Adds exact closed overlap and the nonnegative hard CAD slide domain.",
  sourceAssetIds: [correctionAsset.id, "slider-analysis-mechanism-evidence-contract-r012"]
});
const configAsset = addAsset({
  id: "slider-analysis-interactive-cad-geometry-config-r013",
  filePath: configPath,
  role: "analysis",
  contentClass: "contract-driven-interactive-cad-geometry-config",
  note: "CAD-only carrier/groove configuration with an exact s=0 hard closed stop.",
  sourceAssetIds: [contractAsset.id]
});
addAsset({
  id: "slider-analysis-closed-stop-cad-registrar-r013",
  filePath: fileURLToPath(import.meta.url),
  role: "process",
  contentClass: "deterministic-closed-stop-contract-and-cad-registrar",
  note: "Builds and registers immutable rev 13.",
  sourceAssetIds: [correctionAsset.id]
});
for (const priorId of ["slider-analysis-mechanism-evidence-contract-r012", "slider-analysis-interactive-cad-geometry-config-r012"]) {
  const prior = manifest.assets.find((asset) => asset.id === priorId);
  prior.provenance = {
    ...prior.provenance,
    disposition: "superseded-internal",
    supersededBy: priorId.includes("contract")
      ? contractAsset.id
      : configAsset.id
  };
  stage.internalArtifactIds = [...new Set([...(stage.internalArtifactIds || []), priorId])];
}
const priorClaim = manifest.claims.find((claim) => claim.id === "slider-analysis-carrier-groove-ownership-r012");
priorClaim.state = "superseded";
priorClaim.decisionState = "partially-accepted-superseded";
priorClaim.supersededBy = "slider-analysis-hard-closed-stop-r013";
manifest.claims.push({
  id: "slider-analysis-hard-closed-stop-r013",
  stageId: "02-analysis",
  category: "mechanism-limit",
  statement: "s=0 是 θ=0° 下顶片与底片外轮廓精确重合的闭合态；0≤s≤sMax；闭合处向内分量被硬钳制，但切向分量仍可旋转。",
  confidence: "locked",
  state: "pending-review",
  decisionState: "pending-review",
  sourceAssetIds: [correctionAsset.id],
  sourceRegions: [{ assetId: correctionAsset.id, note: "Whole correction." }],
  unknowns: ["物理接触力、弹性、声音和手感属于后续 Simulator"]
});
stage.reviewArtifactIds = [configAsset.id];
stage.status = "ready_for_review";
stage.staleReason = null;
stage.readiness = { ready: true, blockers: [], note: "Complete nine CAD checks including the exact closed hard stop. Simulator stays locked." };
stage.analysisSpec = {
  ...stage.analysisSpec,
  revision: 13,
  priorRevisionDisposition: "rev12-principle-partially-accepted-closed-stop-missing",
  reviewMode: "interactive-cad-carrier-grooves-hard-closed-stop",
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
  id: "hard-closed-stop-contract-r013",
  status: "pass",
  evidence: "Rev 13 defines s=0 as exact aligned overlap and forbids negative CAD travel without adding Simulator behavior."
});
for (const downstream of manifest.stages.slice(2, 11)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 02 rev 13 closed-stop CAD awaits in-workbench subapproval; separate Simulator has not started.";
}
manifest.stages[11].status = "rejected";
manifest.stages[11].staleReason = "Gate 02 CAD and Simulator approvals are incomplete; shipping remains rejected.";
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev13-hard-closed-stop-interactive-cad-subapproval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 13 retains the accepted rev 12 carrier/groove principle and adds the exact s=0 hard closed overlap. Simulator and downstream generation remain locked.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-hard-closed-stop-review-ready",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 13,
  priorDecisionState: "rev12-principle-partially-accepted",
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
  stageRevision: 13,
  contractHash,
  cadArtifactHash: configAsset.sha256
}, null, 2));
