#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const scriptPath = fileURLToPath(import.meta.url);
const here = path.dirname(scriptPath);
const repoRoot = path.resolve(here, "../../../../../../../../");
const relative = (filePath) => path.relative(repoRoot, filePath).split(path.sep).join("/");
const previewPath = path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate02-rev12-carrier-groove-cad.png");
const contractPath = path.join(here, "mechanism-evidence-contract.json");
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 135) throw new Error(`Expected revision 135, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 12) throw new Error("Gate 02 rev 12 must be active.");
const contractHash = sha256File(contractPath);
const preview = manifest.assets.find((asset) => asset.id === "slider-analysis-carrier-groove-cad-preview-r012");
preview.sha256 = sha256File(previewPath);
preview.sizeBytes = fs.statSync(previewPath).size;
preview.exists = true;
const timestamp = new Date().toISOString();
const finalizeAsset = {
  id: "slider-analysis-carrier-groove-cad-finalizer-r012",
  stageId: "02-analysis",
  slot: "analysis-evidence",
  path: relative(scriptPath),
  sha256: sha256File(scriptPath),
  exists: true,
  sizeBytes: fs.statSync(scriptPath).size,
  role: "process",
  producer: { name: "fidgeting-model-pipeline", version: "2026-08-26", recipe: "Finalize Gate 02 rev 12 browser evidence" },
  provenance: {
    origin: "repository-generated",
    contentClass: "carrier-groove-cad-finalizer",
    assertedBy: "assistant",
    note: "Refreshes the final post-hash browser preview and focused-test evidence without changing the contract."
  },
  sourceAssetIds: [
    "slider-analysis-carrier-groove-cad-preview-r012",
    "slider-analysis-carrier-groove-cad-validation-r012"
  ],
  mechanismEvidenceContractSha256: contractHash
};
manifest.assets.push(finalizeAsset);
stage.artifactIds.push(finalizeAsset.id);
const refreshPaths = new Set([
  "tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs",
  "tools/model-provenance-explorer/tests/pipeline-core.test.mjs",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"
]);
for (const asset of manifest.assets) {
  if (!refreshPaths.has(asset.path)) continue;
  const absolute = path.join(repoRoot, asset.path);
  if (!fs.existsSync(absolute)) continue;
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
  asset.exists = true;
}
stage.status = "ready_for_review";
stage.staleReason = null;
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
manifest.revision += 1;
manifest.updatedAt = timestamp;
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-carrier-groove-review-finalized",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 12,
  contractHash,
  previewAssetId: preview.id,
  previewHash: preview.sha256,
  validationAssetId: "slider-analysis-carrier-groove-cad-validation-r012",
  simulatorState: "locked-not-generated",
  blenderUnityBuildInstallPhone: "not-started"
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  contractHash,
  previewHash: preview.sha256,
  previewSizeBytes: preview.sizeBytes
}, null, 2));
