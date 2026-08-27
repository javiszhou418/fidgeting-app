#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 173) throw new Error(`Expected pipeline revision 173, got ${manifest.revision}.`);
const gate05 = manifest.stages.find((stage) => stage.id === "05-blockout");
const refresh = new Map([
  ["magnetic-slide-tile-workspace-browser-report-r006", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-006/browser-workspace-validation.json"],
  ["magnetic-slide-tile-workspace-browser-test-r006", "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate05.mjs"],
  ["magnetic-slide-tile-workspace-full-preview-r006", "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev6-persistent-workbench.png"],
  ["magnetic-slide-tile-workspace-focused-preview-r006", "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev6-workbench-focused.png"],
  ["magnetic-slide-tile-gate05-rev6-implementation-status", "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"],
  ["magnetic-slide-tile-gate05-rev6-implementation-status-final", "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"]
]);
for (const [id, relative] of refresh) {
  const asset = manifest.assets.find((candidate) => candidate.id === id);
  if (!asset) throw new Error(`Missing asset ${id}.`);
  const absolute = path.join(repoRoot, relative);
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
}
const appPath = path.join(repoRoot, "tools/model-provenance-explorer/app.js");
const appId = "magnetic-slide-tile-workspace-current-review-copy-r006";
manifest.assets.push({
  id: appId,
  stageId: "05-blockout",
  slot: "workbench-process",
  path: "tools/model-provenance-explorer/app.js",
  sha256: sha256File(appPath),
  exists: true,
  sizeBytes: fs.statSync(appPath).size,
  role: "process",
  producer: {
    name: "model-provenance-explorer",
    version: "persistent-workspace-v2",
    recipe: "Gate 05 rev 6 current review prompt and stable navigation"
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "workbench-process",
    assertedBy: "assistant",
    mechanismEvidenceContractSha256: gate05.blockoutSpec.governingContractSha256,
    simulatorUsed: false,
    unityUsed: false
  },
  sourceAssetIds: [
    "magnetic-slide-tile-blockout-validation-r006",
    "magnetic-slide-tile-workspace-browser-report-r006"
  ],
  sourceClaimIds: []
});
gate05.artifactIds.push(appId);
gate05.validations.push({
  id: "current-review-copy-rev6",
  status: "pass",
  evidence: "The current 白模 page asks only whether BottomExterior is one flat plane with a separate raised boss; no legacy 21 mm or hidden-zone copy remains."
});
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-rev6-current-review-copy-validated",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  appAssetId: appId,
  refreshedAssetIds: [...refresh.keys()],
  visualApprovalPending: true,
  unityChanged: false,
  deviceWork: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate05: saved.stages[4].status,
  appAssetId: appId
}, null, 2));

