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
const repoRoot = path.resolve(here, "../../../../../../../../");
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 123) throw new Error(`Expected revision 123, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 8) throw new Error("Gate 02 rev 8 must be active.");
const timestamp = new Date().toISOString();
const contractId = "slider-analysis-mechanism-evidence-contract-r008";
const addAsset = (id, filename, role, contentClass, note) => {
  const absolutePath = path.join(here, filename);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing ${filename}`);
  const asset = {
    id,
    stageId: "02-analysis",
    slot: "analysis-evidence",
    path: path.relative(repoRoot, absolutePath).split(path.sep).join("/"),
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role,
    producer: {
      name: "fidgeting-model-pipeline",
      version: "1",
      recipe: "Gate 02 rev 8 browser and validation evidence"
    },
    provenance: {
      origin: "repository-generated",
      contentClass,
      assertedBy: "assistant",
      note
    },
    sourceAssetIds: [contractId]
  };
  manifest.assets.push(asset);
  stage.artifactIds.push(asset.id);
  return asset;
};
const preview = addAsset(
  "slider-analysis-reference-application-workbench-r008",
  "workbench-browser.png",
  "analysis",
  "full-size-source-to-constraint-workbench-preview",
  "Shows the compact contract application summary and reference cards with prominent 已应用到 fields."
);
const report = addAsset(
  "slider-analysis-reference-contract-validation-r008",
  "validation-report.json",
  "validation",
  "reference-contract-validation-report",
  "Records schema, source-link, PTS-region, no-drift, browser, mobile, video and pipeline validator results."
);
stage.reviewArtifactIds = [preview.id, contractId];
stage.analysisSpec.previewAssetId = preview.id;
stage.analysisSpec.validationReportAssetId = report.id;
stage.validations.push({
  id: "reference-application-workbench-browser-r008",
  status: "pass",
  evidence: "53/53 reference cards show 已应用到; 12-gate desktop/mobile, modal return and H.264 playback passed."
});
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
manifest.revision += 1;
manifest.updatedAt = timestamp;
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-reference-research-preview-validated",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 8,
  previewAssetId: preview.id,
  validationReportAssetId: report.id,
  browser: "desktop-mobile-reference-card-modal-video-pass",
  gateStatus: stage.status,
  cadLocked: true
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  previewAssetId: preview.id,
  validationReportAssetId: report.id
}, null, 2));
