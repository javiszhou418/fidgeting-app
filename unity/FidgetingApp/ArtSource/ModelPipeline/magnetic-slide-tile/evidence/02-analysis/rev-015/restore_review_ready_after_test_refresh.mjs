#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../../");
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 150) throw new Error(`Expected revision 150, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
for (const relativePath of [
  "tools/model-provenance-explorer/tests/pipeline-core.test.mjs",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"
]) {
  const asset = manifest.assets.find((candidate) => candidate.path === relativePath);
  if (!asset) continue;
  const absolute = path.join(repoRoot, relativePath);
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
  asset.exists = true;
}
stage.status = "ready_for_review";
stage.staleReason = null;
stage.readiness = { ready: true, blockers: [], note: "Complete twelve CAD checks including analytic minimum-overlap containment. Simulator stays locked." };
stage.outputDigest = crypto.createHash("sha256").update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n")).digest("hex");
const timestamp = new Date().toISOString();
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev15-minimum-overlap-disk-interactive-cad-subapproval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 15 analytic MinimumOverlapDisk CAD is validated and ready for interactive review. Simulator and downstream generation remain locked.";
saveManifest(manifest, {
  id: crypto.randomUUID(), type: "stage-interactive-cad-minimum-overlap-review-ready-restored",
  modelId: manifest.model.id, manifestRevision: manifest.revision, timestamp, stageId: "02-analysis",
  analysisEvidenceRevision: 15, contractHash: stage.analysisSpec.contractSha256,
  cadArtifactHash: manifest.assets.find((asset) => asset.id === stage.analysisSpec.cadArtifactId).sha256,
  previewHash: manifest.assets.find((asset) => asset.id === "slider-analysis-minimum-overlap-disk-cad-preview-r015").sha256,
  simulatorState: "locked-not-generated", blenderUnityBuildInstallPhone: "not-started"
});
console.log(JSON.stringify({ manifestRevision: manifest.revision, stageStatus: stage.status }, null, 2));
