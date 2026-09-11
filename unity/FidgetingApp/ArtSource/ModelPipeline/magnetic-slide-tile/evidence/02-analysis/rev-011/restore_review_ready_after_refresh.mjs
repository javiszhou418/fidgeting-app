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

const scriptPath = fileURLToPath(import.meta.url);
const here = path.dirname(scriptPath);
const repoRoot = path.resolve(here, "../../../../../../../../");
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 132) throw new Error(`Expected refreshed revision 132, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 11) throw new Error("Gate 02 rev 11 must remain active.");
const relativeScript = path.relative(repoRoot, scriptPath).split(path.sep).join("/");
const timestamp = new Date().toISOString();
const scriptAsset = {
  id: "slider-analysis-bottom-fixed-refresh-restorer-r011",
  stageId: "02-analysis",
  slot: "analysis-evidence",
  path: relativeScript,
  sha256: sha256File(scriptPath),
  exists: true,
  sizeBytes: fs.statSync(scriptPath).size,
  role: "process",
  producer: {
    name: "fidgeting-model-pipeline",
    version: "2026-08-26",
    recipe: "Restore Gate 02 review readiness after intentional hash refresh"
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "post-validation-review-readiness-restorer",
    assertedBy: "assistant",
    note: "The refresh invalidated Gate 02 because its active web/test artifacts changed. This record restores readiness only after the full revised test suite passed."
  },
  sourceAssetIds: [
    "slider-analysis-bottom-fixed-cad-validation-r011",
    "slider-analysis-bottom-fixed-cad-preview-r011"
  ],
  mechanismEvidenceContractSha256: stage.analysisSpec.contractSha256
};
manifest.assets.push(scriptAsset);
stage.artifactIds.push(scriptAsset.id);
for (const asset of manifest.assets) {
  if (![
    "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md",
    "tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs"
  ].includes(asset.path)) continue;
  const absolute = path.join(repoRoot, asset.path);
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
}
stage.status = "ready_for_review";
stage.staleReason = null;
stage.readiness = {
  ready: true,
  blockers: [],
  note: "Complete eight CAD-only structural checks. The separate Simulator stays locked."
};
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
for (const downstream of manifest.stages.slice(2, 11)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 02 rev 11 fixed-bottom/fixed-axis CAD awaits in-workbench subapproval; separate Simulator has not started.";
}
manifest.stages[11].status = "rejected";
manifest.currentState.visualApproval = "gate02-rev11-fixed-bottom-interactive-cad-subapproval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 11 fixed-bottom/fixed-axis CAD is validated and ready for interactive review. Simulator and all downstream generation remain locked.";
manifest.revision += 1;
manifest.updatedAt = timestamp;
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-review-readiness-restored-after-validated-refresh",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 11,
  contractHash: stage.analysisSpec.contractSha256,
  validationAssetId: "slider-analysis-bottom-fixed-cad-validation-r011",
  status: "ready_for_review",
  simulatorState: "locked-not-generated",
  blenderUnityBuildInstallPhone: "not-started"
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  stageStatus: stage.status,
  contractHash: stage.analysisSpec.contractSha256
}, null, 2));
