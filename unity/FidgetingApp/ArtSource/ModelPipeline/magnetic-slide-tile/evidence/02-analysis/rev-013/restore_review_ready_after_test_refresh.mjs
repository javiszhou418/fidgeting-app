#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../../");
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 142) throw new Error(`Expected revision 142, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 13) throw new Error("Gate 02 rev 13 must be active.");
const refreshPaths = new Set([
  "tools/model-provenance-explorer/tests/pipeline-core.test.mjs",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md",
  "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate02-rev13-closed-stop-cad.png"
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
const timestamp = new Date().toISOString();
manifest.revision += 1;
manifest.updatedAt = timestamp;
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-hard-closed-stop-test-refresh",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 13,
  contractHash: stage.analysisSpec.contractSha256,
  simulatorState: "locked-not-generated",
  blenderUnityBuildInstallPhone: "not-started"
});
console.log(JSON.stringify({ manifestRevision: manifest.revision, stageStatus: stage.status }, null, 2));
