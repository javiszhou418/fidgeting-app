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
const previewPath = path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate02-rev14-finite-groove-sweep-cad.png");
const validationPath = path.join(here, "validation-report.json");
const registrarPath = path.join(here, "register_finite_groove_cad_review.mjs");
const correctionPath = path.join(here, "finite-groove-user-correction.md");
const scriptPath = fileURLToPath(import.meta.url);
for (const filePath of [contractPath, configPath, previewPath, validationPath, registrarPath, correctionPath]) {
  if (!fs.existsSync(filePath)) throw new Error(`Missing seal input ${filePath}`);
}
const contractHash = sha256File(contractPath);
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 144) throw new Error(`Expected revision 144, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 14) throw new Error("Gate 02 rev 14 must be active.");
stage.analysisSpec.contractSha256 = contractHash;
const timestamp = new Date().toISOString();
const makeAsset = ({ id, filePath, role, contentClass, note, sourceAssetIds }) => ({
  id,
  stageId: "02-analysis",
  slot: "analysis-evidence",
  path: relative(filePath),
  sha256: sha256File(filePath),
  exists: true,
  sizeBytes: fs.statSync(filePath).size,
  role,
  producer: { name: "fidgeting-model-pipeline", version: "2026-08-27", recipe: "Gate 02 rev 14 finite-groove endpoint and swept-envelope validation" },
  provenance: { origin: "repository-generated", contentClass, assertedBy: "assistant", note },
  sourceAssetIds,
  mechanismEvidenceContractSha256: contractHash
});
const additions = [
  makeAsset({
    id: "slider-analysis-finite-groove-sweep-cad-preview-r014",
    filePath: previewPath,
    role: "analysis",
    contentClass: "supplementary-full-size-finite-groove-swept-envelope-cad-preview",
    note: "Static preview shows finite groove endpoints, follower contacts and the 30-detent swept envelope. Approval remains interactive.",
    sourceAssetIds: ["slider-analysis-interactive-cad-geometry-config-r014", "slider-analysis-finite-groove-user-correction-r014"]
  }),
  makeAsset({
    id: "slider-analysis-finite-groove-cad-validation-r014",
    filePath: validationPath,
    role: "validation",
    contentClass: "finite-groove-endpoint-swept-envelope-cad-validation-report",
    note: "Records endpoint derivation, 150 valid sweep samples, z-order, pointer clamps, mobile, zoom/pan, references and Simulator lock.",
    sourceAssetIds: ["slider-analysis-interactive-cad-geometry-config-r014", "slider-analysis-finite-groove-user-correction-r014"]
  }),
  makeAsset({
    id: "slider-analysis-finite-groove-cad-sealer-r014",
    filePath: scriptPath,
    role: "process",
    contentClass: "finite-groove-swept-envelope-cad-seal-script",
    note: "Seals rev 14 contract, config, preview and validation evidence.",
    sourceAssetIds: ["slider-analysis-interactive-cad-geometry-config-r014"]
  })
];
for (const asset of additions) {
  manifest.assets.push(asset);
  stage.artifactIds.push(asset.id);
}
const refreshPaths = new Set([
  relative(contractPath),
  relative(configPath),
  relative(registrarPath),
  relative(correctionPath),
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
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"
]);
for (const asset of manifest.assets) {
  if (refreshPaths.has(asset.path)) {
    const absolute = path.join(repoRoot, asset.path);
    if (fs.existsSync(absolute)) {
      asset.sha256 = sha256File(absolute);
      asset.sizeBytes = fs.statSync(absolute).size;
      asset.exists = true;
    }
  }
  if ([
    "slider-analysis-mechanism-evidence-contract-r014",
    "slider-analysis-interactive-cad-geometry-config-r014",
    "slider-analysis-finite-groove-cad-registrar-r014"
  ].includes(asset.id)) {
    asset.mechanismEvidenceContractSha256 = contractHash;
  }
}
stage.status = "ready_for_review";
stage.staleReason = null;
stage.readiness = { ready: true, blockers: [], note: "Complete eleven CAD checks including finite endpoints, synchronized views and the 360-degree swept envelope. Simulator stays locked." };
stage.validations = stage.validations.filter((item) => item.id !== "finite-groove-sweep-browser-r014");
stage.validations.push({
  id: "finite-groove-sweep-browser-r014",
  status: "pass",
  evidence: "65/65 Node tests and desktop/mobile real-pointer browser smoke passed. All 150 sweep samples preserve follower engagement, axis coverage, top z-order and no bottom masking."
});
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev14-finite-groove-interactive-cad-subapproval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 14 finite-groove endpoint CAD and 360-degree swept envelope are validated and ready for interactive review. Simulator and downstream generation remain locked.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-finite-groove-review-sealed",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 14,
  correctionAssetId: "slider-analysis-finite-groove-user-correction-r014",
  contractAssetId: stage.analysisSpec.contractAssetId,
  contractHash,
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
  contractHash,
  cadArtifactHash: manifest.assets.find((asset) => asset.id === stage.analysisSpec.cadArtifactId).sha256,
  previewHash: additions[0].sha256,
  validationHash: additions[1].sha256
}, null, 2));
