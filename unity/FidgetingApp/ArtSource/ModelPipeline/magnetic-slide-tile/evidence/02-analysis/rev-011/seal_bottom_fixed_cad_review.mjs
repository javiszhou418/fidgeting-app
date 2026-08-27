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
const relative = (filePath) => path.relative(repoRoot, filePath).split(path.sep).join("/");
const screenshotPath = path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate02-rev11-fixed-bottom-cad.png");
const validationPath = path.join(here, "validation-report.json");
const configPath = path.join(here, "interactive-cad-geometry-config.json");
const registrarPath = path.join(here, "register_bottom_fixed_cad_review.mjs");
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 130) throw new Error(`Expected revision 130, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 11) throw new Error("Gate 02 rev 11 must be active.");
for (const filePath of [screenshotPath, validationPath, configPath, registrarPath]) {
  if (!fs.existsSync(filePath)) throw new Error(`Missing seal input ${filePath}`);
}
const timestamp = new Date().toISOString();
const assetRecord = ({ id, filePath, role, contentClass, note, sourceAssetIds }) => ({
  id,
  stageId: "02-analysis",
  slot: "analysis-evidence",
  path: relative(filePath),
  sha256: sha256File(filePath),
  exists: true,
  sizeBytes: fs.statSync(filePath).size,
  role,
  producer: {
    name: "fidgeting-model-pipeline",
    version: "2026-08-26",
    recipe: "Gate 02 rev 11 fixed-bottom CAD validation and preview"
  },
  provenance: {
    origin: "repository-generated",
    contentClass,
    assertedBy: "assistant",
    note
  },
  sourceAssetIds,
  mechanismEvidenceContractSha256: stage.analysisSpec.contractSha256
});
const additions = [
  assetRecord({
    id: "slider-analysis-bottom-fixed-cad-preview-r011",
    filePath: screenshotPath,
    role: "analysis",
    contentClass: "supplementary-full-size-fixed-bottom-cad-preview",
    note: "Static preview is supplementary only. Approval remains interactive in the workbench.",
    sourceAssetIds: [
      "slider-analysis-interactive-cad-geometry-config-r011",
      "slider-analysis-mechanism-evidence-contract-r011"
    ]
  }),
  assetRecord({
    id: "slider-analysis-bottom-fixed-cad-validation-r011",
    filePath: validationPath,
    role: "validation",
    contentClass: "fixed-bottom-cad-validation-report",
    note: "Records fixed transforms, compound pointer behavior, component layers, source access and Simulator lock evidence.",
    sourceAssetIds: [
      "slider-analysis-interactive-cad-geometry-config-r011",
      "slider-analysis-user-selected-bottom-base-close-r011",
      "slider-analysis-user-selected-bottom-base-context-r011"
    ]
  }),
  assetRecord({
    id: "slider-analysis-bottom-fixed-cad-sealer-r011",
    filePath: fileURLToPath(import.meta.url),
    role: "process",
    contentClass: "fixed-bottom-cad-seal-script",
    note: "Registers validation and preview evidence, then refreshes touched repository artifact hashes.",
    sourceAssetIds: ["slider-analysis-interactive-cad-geometry-config-r011"]
  })
];
for (const asset of additions) {
  manifest.assets.push(asset);
  stage.artifactIds.push(asset.id);
}
const refreshPaths = new Set([
  relative(configPath),
  relative(registrarPath),
  "AGENTS.md",
  "skills/fidgeting-model-pipeline/SKILL.md",
  "skills/fidgeting-model-pipeline/references/pipeline-contract.md",
  "tools/model-provenance-explorer/app.js",
  "tools/model-provenance-explorer/styles.css",
  "tools/model-provenance-explorer/mechanism-cad-core.mjs",
  "tools/model-provenance-explorer/pipeline-core.mjs",
  "tools/model-provenance-explorer/pipeline-contract.mjs",
  "tools/model-provenance-explorer/tests/mechanism-cad.test.mjs",
  "tools/model-provenance-explorer/tests/mechanism-evidence-contract.test.mjs",
  "tools/model-provenance-explorer/tests/pipeline-core.test.mjs",
  "tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs",
  "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"
]);
for (const asset of manifest.assets) {
  if (!refreshPaths.has(asset.path)) continue;
  const absolute = path.join(repoRoot, asset.path);
  if (!fs.existsSync(absolute)) continue;
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
  asset.exists = true;
  if (asset.id === "slider-analysis-interactive-cad-geometry-config-r011") {
    asset.mechanismEvidenceContractSha256 = stage.analysisSpec.contractSha256;
  }
}
stage.validations = stage.validations.filter((validation) => validation.id !== "bottom-fixed-cad-browser-r011");
stage.validations.push({
  id: "bottom-fixed-cad-browser-r011",
  status: "pass",
  evidence: "56/56 Node tests and desktop/mobile real-pointer browser smoke passed. Bottom and axis remained fixed while TopPlate changed s and theta; seven component layers and 18 references were available."
});
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
manifest.revision += 1;
manifest.updatedAt = timestamp;
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-fixed-bottom-review-sealed",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 11,
  contractAssetId: stage.analysisSpec.contractAssetId,
  contractHash: stage.analysisSpec.contractSha256,
  cadArtifactId: stage.analysisSpec.cadArtifactId,
  cadArtifactHash: manifest.assets.find((asset) => asset.id === stage.analysisSpec.cadArtifactId).sha256,
  previewAssetId: additions[0].id,
  previewHash: additions[0].sha256,
  validationAssetId: additions[1].id,
  validationHash: additions[1].sha256,
  simulatorState: "locked-not-generated",
  blenderUnityBuildInstallPhone: "not-started"
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  contractHash: stage.analysisSpec.contractSha256,
  cadArtifactHash: manifest.assets.find((asset) => asset.id === stage.analysisSpec.cadArtifactId).sha256,
  previewHash: additions[0].sha256,
  validationHash: additions[1].sha256
}, null, 2));
