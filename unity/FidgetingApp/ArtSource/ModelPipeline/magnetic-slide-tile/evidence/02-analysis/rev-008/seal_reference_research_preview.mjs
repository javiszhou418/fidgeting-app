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

const here = path.dirname(fileURLToPath(import.meta.url));
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 125) throw new Error(`Expected revision 125, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
const preview = manifest.assets.find((asset) => asset.id === "slider-analysis-reference-application-workbench-r008");
const absolutePath = path.join(here, "workbench-browser.png");
preview.sha256 = sha256File(absolutePath);
preview.sizeBytes = fs.statSync(absolutePath).size;
preview.exists = true;
const report = manifest.assets.find((asset) => asset.id === "slider-analysis-reference-contract-validation-r008");
const reportPath = path.join(here, "validation-report.json");
report.sha256 = sha256File(reportPath);
report.sizeBytes = fs.statSync(reportPath).size;
report.exists = true;
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
const timestamp = new Date().toISOString();
manifest.revision += 1;
manifest.updatedAt = timestamp;
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-reference-research-preview-sealed",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  previewAssetId: preview.id,
  previewSha256: preview.sha256,
  validationReportAssetId: report.id,
  validationReportSha256: report.sha256,
  gateStatus: stage.status
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  previewSha256: preview.sha256,
  validationReportSha256: report.sha256
}, null, 2));
