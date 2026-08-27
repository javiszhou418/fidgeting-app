#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../../");
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 126) throw new Error(`Expected revision 126, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 8) throw new Error("Gate 02 rev 8 must be active.");
const configPath = path.join(here, "interactive-cad-review-config.json");
const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
if (config.contractSha256 !== stage.analysisSpec.contractSha256) throw new Error("Contract hash drift.");
const timestamp = new Date().toISOString();
const asset = {
  id: "slider-analysis-interactive-cad-config-r009",
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
    recipe: "Gate 02 rev 9 contract-driven interactive CAD approval"
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "contract-driven-interactive-cad-simulator-config",
    assertedBy: "assistant",
    note: "Separates review tuning and diagrammatic rail layout from evidence values loaded by contract selector."
  },
  sourceAssetIds: [config.contractAssetId],
  mechanismEvidenceContractSha256: config.contractSha256
};
manifest.assets.push(asset);
stage.artifactIds.push(asset.id);
stage.reviewArtifactIds = [asset.id];
stage.status = "ready_for_review";
stage.readiness = {
  ready: true,
  blockers: [],
  note: "Complete the interactive CAD checklist; text and static screenshots cannot approve Gate 02."
};
stage.analysisSpec = {
  ...stage.analysisSpec,
  revision: 9,
  priorRevisionDisposition: "rev8-text-static-approval-rejected",
  reviewMode: "interactive-cad-primary",
  simulatorArtifactId: asset.id,
  simulatorConfigAssetId: asset.id,
  recordingAssetId: null,
  cadGeneration: {
    locked: false,
    scope: "web-simulator-only-no-blender-unity",
    configSource: asset.id,
    contractSource: config.contractAssetId,
    duplicateDefaultsForbidden: true
  },
  approvalSpec: {
    ...config.approvalRule,
    requiredMilestones: config.approvalChecklist,
    approvalButtonLabel: "确认此 Simulator",
    approvalApiRequired: true
  },
  reviewQuestion: null
};
stage.validations.push({
  id: "interactive-approval-hard-rule-r009",
  status: "pass",
  evidence: "CAD is the default review; approval stays disabled until six interaction milestones complete."
});
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((candidate) => candidate.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev9-interactive-cad-approval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 9 replaces text/static approval with contract-driven interactive CAD. Gate 01 remains approved; Gates 03–11 stale; Gate 12 blocked/rejected. No Blender, Unity, build, install or phone work ran.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-review-ready",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 9,
  priorRevisionDisposition: "rev8-text-static-approval-rejected",
  simulatorArtifactId: asset.id,
  simulatorArtifactHash: asset.sha256,
  contractAssetId: config.contractAssetId,
  contractHash: config.contractSha256,
  requiredMilestones: config.approvalChecklist,
  chatTextApprovalAllowed: false,
  staticScreenshotApprovalAllowed: false,
  blenderUnityBuildInstallPhone: "not-started"
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  stageRevision: stage.analysisSpec.revision,
  simulatorArtifactHash: asset.sha256,
  contractHash: config.contractSha256
}, null, 2));
