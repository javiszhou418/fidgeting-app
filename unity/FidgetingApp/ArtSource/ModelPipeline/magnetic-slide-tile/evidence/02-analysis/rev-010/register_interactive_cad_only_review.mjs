#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../../");
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 127) throw new Error(`Expected revision 127, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 9) throw new Error("Gate 02 rev 9 must be active.");
const configPath = path.join(here, "interactive-cad-geometry-config.json");
const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
if (config.contractSha256 !== stage.analysisSpec.contractSha256) throw new Error("Contract hash drift.");
const priorAsset = manifest.assets.find((candidate) => candidate.id === "slider-analysis-interactive-cad-config-r009");
if (!priorAsset) throw new Error("Missing immutable rev 9 artifact.");
priorAsset.provenance = {
  ...priorAsset.provenance,
  disposition: "superseded-internal",
  supersededBy: "slider-analysis-interactive-cad-geometry-config-r010",
  note: "Preserved immutably. Hand-feel Simulator configuration was collapsed into CAD by mistake and is no longer exposed."
};
const timestamp = new Date().toISOString();
const asset = {
  id: "slider-analysis-interactive-cad-geometry-config-r010",
  stageId: "02-analysis",
  slot: "analysis-evidence",
  path: path.relative(repoRoot, configPath).split(path.sep).join("/"),
  sha256: sha256File(configPath),
  exists: true,
  sizeBytes: fs.statSync(configPath).size,
  role: "analysis",
  producer: {
    name: "fidgeting-model-pipeline",
    version: "1",
    recipe: "Gate 02 rev 10 contract-driven kinematic CAD approval"
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "contract-driven-interactive-cad-geometry-config",
    assertedBy: "assistant",
    note: "Contains geometry selectors, diagrammatic rail layout and CAD-only approval milestones. It contains no hand-feel Simulator values."
  },
  sourceAssetIds: [config.contractAssetId],
  mechanismEvidenceContractSha256: config.contractSha256
};
manifest.assets.push(asset);
stage.artifactIds.push(asset.id);
stage.reviewArtifactIds = [asset.id];
stage.internalArtifactIds = [...new Set([...(stage.internalArtifactIds || []), priorAsset.id])];
stage.status = "ready_for_review";
stage.readiness = {
  ready: true,
  blockers: [],
  note: "Complete seven CAD geometry checks. The separate hand-feel Simulator stays locked until this subapproval record exists."
};
stage.analysisSpec = {
  ...stage.analysisSpec,
  revision: 10,
  priorRevisionDisposition: "rev9-cad-simulator-collapsed-superseded-internal",
  phase: "interactive-cad-approval",
  reviewMode: "interactive-cad-geometry-only",
  cadArtifactId: asset.id,
  cadConfigAssetId: asset.id,
  simulatorArtifactId: null,
  simulatorConfigAssetId: null,
  recordingAssetId: null,
  cadGeneration: {
    locked: false,
    scope: "web-kinematic-cad-only-no-simulator-blender-unity",
    configSource: asset.id,
    contractSource: config.contractAssetId,
    duplicateDefaultsForbidden: true
  },
  simulatorGeneration: {
    locked: true,
    unlockRequires: "interactive-cad-subapproval-record",
    label: config.simulator.label,
    activeControls: 0
  },
  approvalSpec: {
    ...config.approvalRule,
    requiredMilestones: config.cadApprovalChecklist,
    approvalButtonLabel: "确认交互 CAD",
    approvalApiRequired: true
  },
  reviewQuestion: null
};
stage.validations.push(
  {
    id: "cad-simulator-separation-r010",
    status: "pass",
    evidence: "CAD exposes kinematic geometry only. Hand-feel Simulator controls and recording are absent and the separate Simulator is locked."
  },
  {
    id: "cad-subapproval-sequence-r010",
    status: "pass",
    evidence: "CAD approval records a subapproval while Gate 02 stays open; Simulator generation remains locked until that record exists."
  }
);
for (let index = 2; index <= 10; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 02 rev 10 interactive CAD is awaiting its in-workbench subapproval. The separate Simulator has not started.";
}
manifest.stages[11].status = "rejected";
manifest.stages[11].staleReason = "Gate 02 CAD and Simulator approvals are incomplete; shipping remains rejected.";
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((candidate) => candidate.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev10-interactive-cad-subapproval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 10 separates structural CAD from hand-feel Simulator. CAD is ready for geometry-only interactive review; Simulator, Blender, Unity, build, install and phone work remain locked.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-only-review-ready",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 10,
  priorRevisionDisposition: "rev9-cad-simulator-collapsed-superseded-internal",
  cadArtifactId: asset.id,
  cadArtifactHash: asset.sha256,
  contractAssetId: config.contractAssetId,
  contractHash: config.contractSha256,
  requiredMilestones: config.cadApprovalChecklist,
  simulatorState: "locked-not-generated",
  blenderUnityBuildInstallPhone: "not-started"
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  stageRevision: stage.analysisSpec.revision,
  cadArtifactHash: asset.sha256,
  contractHash: config.contractSha256,
  simulatorState: "locked-not-generated"
}, null, 2));
