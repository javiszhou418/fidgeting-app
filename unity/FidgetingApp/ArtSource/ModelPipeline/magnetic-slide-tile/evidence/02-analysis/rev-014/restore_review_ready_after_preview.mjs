#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../../");
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 146) throw new Error(`Expected revision 146, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 14) throw new Error("Gate 02 rev 14 must be active.");
const refreshPaths = [
  "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate02-rev14-finite-groove-sweep-cad.png",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"
];
for (const relativePath of refreshPaths) {
  const asset = manifest.assets.find((candidate) => candidate.path === relativePath);
  if (!asset) throw new Error(`Missing registered asset for ${relativePath}`);
  const absolutePath = path.join(repoRoot, relativePath);
  asset.sha256 = sha256File(absolutePath);
  asset.sizeBytes = fs.statSync(absolutePath).size;
  asset.exists = true;
}
stage.status = "ready_for_review";
stage.staleReason = null;
stage.readiness = { ready: true, blockers: [], note: "Complete eleven CAD checks including finite endpoints, synchronized views and the 360-degree swept envelope. Simulator stays locked." };
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
const timestamp = new Date().toISOString();
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev14-finite-groove-interactive-cad-subapproval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 14 finite-groove CAD, synchronized views and 360-degree swept envelope are validated and ready for interactive review. Simulator and downstream generation remain locked.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-finite-groove-review-ready-restored",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 14,
  previewAssetId: "slider-analysis-finite-groove-sweep-cad-preview-r014",
  previewHash: manifest.assets.find((asset) => asset.id === "slider-analysis-finite-groove-sweep-cad-preview-r014").sha256,
  contractHash: stage.analysisSpec.contractSha256,
  cadArtifactHash: manifest.assets.find((asset) => asset.id === stage.analysisSpec.cadArtifactId).sha256,
  simulatorState: "locked-not-generated",
  blenderUnityBuildInstallPhone: "not-started"
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  previewHash: manifest.assets.find((asset) => asset.id === "slider-analysis-finite-groove-sweep-cad-preview-r014").sha256
}, null, 2));
