#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 128) throw new Error(`Expected revision 128, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
const asset = manifest.assets.find((candidate) => candidate.id === "slider-analysis-interactive-cad-geometry-config-r010");
const configPath = path.join(here, "interactive-cad-geometry-config.json");
const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
asset.sha256 = sha256File(configPath);
asset.sizeBytes = fs.statSync(configPath).size;
stage.analysisSpec.approvalSpec.requiredMilestones = config.cadApprovalChecklist;
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((candidate) => candidate.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "interactive-cad-only-config-sealed",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: stage.id,
  cadArtifactId: asset.id,
  cadArtifactHash: asset.sha256,
  requiredMilestones: config.cadApprovalChecklist
});
console.log(JSON.stringify({ manifestRevision: manifest.revision, cadArtifactHash: asset.sha256 }, null, 2));
