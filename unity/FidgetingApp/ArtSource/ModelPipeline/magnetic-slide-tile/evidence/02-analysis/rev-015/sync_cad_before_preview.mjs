#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../../");
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 148) throw new Error(`Expected revision 148, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
const refreshPaths = new Set([
  "tools/model-provenance-explorer/app.js",
  "tools/model-provenance-explorer/styles.css",
  "tools/model-provenance-explorer/mechanism-cad-core.mjs",
  "tools/model-provenance-explorer/pipeline-core.mjs",
  "tools/model-provenance-explorer/tests/mechanism-cad.test.mjs",
  "tools/model-provenance-explorer/tests/mechanism-evidence-contract.test.mjs",
  "tools/model-provenance-explorer/tests/pipeline-core.test.mjs",
  "tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-015/register_minimum_overlap_disk_cad_review.mjs",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-015/interactive-cad-geometry-config.json"
]);
for (const asset of manifest.assets) {
  if (!refreshPaths.has(asset.path)) continue;
  const absolute = path.join(repoRoot, asset.path);
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
  asset.exists = true;
}
stage.status = "ready_for_review";
stage.staleReason = null;
stage.outputDigest = crypto.createHash("sha256").update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n")).digest("hex");
const timestamp = new Date().toISOString();
manifest.revision += 1;
manifest.updatedAt = timestamp;
saveManifest(manifest, {
  id: crypto.randomUUID(), type: "stage-interactive-cad-minimum-overlap-prepreview-synced",
  modelId: manifest.model.id, manifestRevision: manifest.revision, timestamp, stageId: "02-analysis",
  cadArtifactId: stage.analysisSpec.cadArtifactId,
  cadArtifactHash: manifest.assets.find((asset) => asset.id === stage.analysisSpec.cadArtifactId).sha256
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  cadArtifactHash: manifest.assets.find((asset) => asset.id === stage.analysisSpec.cadArtifactId).sha256
}, null, 2));
