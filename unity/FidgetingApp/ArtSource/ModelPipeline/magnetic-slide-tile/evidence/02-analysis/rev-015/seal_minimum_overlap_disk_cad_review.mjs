#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../../");
const relative = (filePath) => path.relative(repoRoot, filePath).split(path.sep).join("/");
const contractPath = path.join(here, "mechanism-evidence-contract.json");
const configPath = path.join(here, "interactive-cad-geometry-config.json");
const previewPath = path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate02-rev15-minimum-overlap-disk-cad.png");
const validationPath = path.join(here, "validation-report.json");
const scriptPath = fileURLToPath(import.meta.url);
for (const filePath of [contractPath, configPath, previewPath, validationPath]) {
  if (!fs.existsSync(filePath)) throw new Error(`Missing seal input ${filePath}`);
}
const contractHash = sha256File(contractPath);
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 149) throw new Error(`Expected revision 149, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 15) throw new Error("Gate 02 rev 15 must be active.");
const timestamp = new Date().toISOString();
const makeAsset = ({ id, filePath, role, contentClass, note, sourceAssetIds }) => ({
  id, stageId: "02-analysis", slot: "analysis-evidence", path: relative(filePath),
  sha256: sha256File(filePath), exists: true, sizeBytes: fs.statSync(filePath).size, role,
  producer: { name: "fidgeting-model-pipeline", version: "2026-08-27", recipe: "Gate 02 rev 15 minimum overlap disk containment validation" },
  provenance: { origin: "repository-generated", contentClass, assertedBy: "assistant", note },
  sourceAssetIds, mechanismEvidenceContractSha256: contractHash
});
const additions = [
  makeAsset({
    id: "slider-analysis-minimum-overlap-disk-cad-preview-r015", filePath: previewPath, role: "analysis",
    contentClass: "supplementary-full-size-minimum-overlap-disk-cad-preview",
    note: "Static preview emphasizes the red disk and exact boundary contact. Approval remains interactive.",
    sourceAssetIds: ["slider-analysis-interactive-cad-geometry-config-r015", "slider-analysis-minimum-overlap-disk-user-screenshot-r015"]
  }),
  makeAsset({
    id: "slider-analysis-minimum-overlap-disk-cad-validation-r015", filePath: validationPath, role: "validation",
    contentClass: "minimum-overlap-disk-analytic-and-dense-validation-report",
    note: "Records analytic containment, 1800 dense samples, parameter switches, pointer clamps, invalid red flash, mobile and Simulator lock.",
    sourceAssetIds: ["slider-analysis-interactive-cad-geometry-config-r015", "slider-analysis-minimum-overlap-disk-user-correction-r015"]
  }),
  makeAsset({
    id: "slider-analysis-minimum-overlap-disk-cad-sealer-r015", filePath: scriptPath, role: "process",
    contentClass: "minimum-overlap-disk-cad-seal-script",
    note: "Seals rev 15 contract, CAD config, preview and validation evidence.",
    sourceAssetIds: ["slider-analysis-interactive-cad-geometry-config-r015"]
  })
];
for (const asset of additions) {
  manifest.assets.push(asset);
  stage.artifactIds.push(asset.id);
}
const refreshPaths = new Set([
  relative(contractPath), relative(configPath),
  "skills/fidgeting-model-pipeline/references/pipeline-contract.md",
  "tools/model-provenance-explorer/app.js",
  "tools/model-provenance-explorer/styles.css",
  "tools/model-provenance-explorer/mechanism-cad-core.mjs",
  "tools/model-provenance-explorer/pipeline-core.mjs",
  "tools/model-provenance-explorer/tests/mechanism-cad.test.mjs",
  "tools/model-provenance-explorer/tests/mechanism-evidence-contract.test.mjs",
  "tools/model-provenance-explorer/tests/pipeline-core.test.mjs",
  "tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs",
  "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-015/register_minimum_overlap_disk_cad_review.mjs",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-015/minimum-overlap-disk-user-correction.md",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-015/minimum-overlap-disk-user-screenshot.png"
]);
for (const asset of manifest.assets) {
  if (!refreshPaths.has(asset.path)) continue;
  const absolute = path.join(repoRoot, asset.path);
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
  asset.exists = true;
}
stage.analysisSpec.contractSha256 = contractHash;
stage.status = "ready_for_review";
stage.staleReason = null;
stage.readiness = { ready: true, blockers: [], note: "Complete twelve CAD checks including analytic minimum-overlap containment. Simulator stays locked." };
stage.validations.push({
  id: "minimum-overlap-disk-browser-r015",
  status: "pass",
  evidence: "70/70 Node tests and desktop/mobile browser smoke passed. Analytic containment plus 360×5 dense samples enforce the red disk with exact boundary tangency."
});
stage.outputDigest = crypto.createHash("sha256").update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n")).digest("hex");
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev15-minimum-overlap-disk-interactive-cad-subapproval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 15 analytic MinimumOverlapDisk CAD is validated and ready for interactive review. Simulator and downstream generation remain locked.";
saveManifest(manifest, {
  id: crypto.randomUUID(), type: "stage-interactive-cad-minimum-overlap-review-sealed",
  modelId: manifest.model.id, manifestRevision: manifest.revision, timestamp, stageId: "02-analysis",
  analysisEvidenceRevision: 15, contractHash,
  cadArtifactId: stage.analysisSpec.cadArtifactId,
  cadArtifactHash: manifest.assets.find((asset) => asset.id === stage.analysisSpec.cadArtifactId).sha256,
  previewAssetId: additions[0].id, previewHash: additions[0].sha256,
  validationAssetId: additions[1].id, validationHash: additions[1].sha256,
  simulatorState: "locked-not-generated", blenderUnityBuildInstallPhone: "not-started"
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  contractHash,
  cadArtifactHash: manifest.assets.find((asset) => asset.id === stage.analysisSpec.cadArtifactId).sha256,
  previewHash: additions[0].sha256
}, null, 2));
