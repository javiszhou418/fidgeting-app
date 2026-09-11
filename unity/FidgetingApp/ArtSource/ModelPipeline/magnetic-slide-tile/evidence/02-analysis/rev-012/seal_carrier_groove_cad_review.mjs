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
const previewPath = path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate02-rev12-carrier-groove-cad.png");
const validationPath = path.join(here, "validation-report.json");
const registrarPath = path.join(here, "register_carrier_groove_cad_review.mjs");
const scriptPath = fileURLToPath(import.meta.url);
for (const filePath of [contractPath, configPath, previewPath, validationPath, registrarPath]) {
  if (!fs.existsSync(filePath)) throw new Error(`Missing seal input ${filePath}`);
}
const contractHash = sha256File(contractPath);
const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
config.contractSha256 = contractHash;
fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`);
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 134) throw new Error(`Expected revision 134, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 12) throw new Error("Gate 02 rev 12 must be active.");
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
  producer: { name: "fidgeting-model-pipeline", version: "2026-08-26", recipe: "Gate 02 rev 12 carrier/groove CAD validation" },
  provenance: { origin: "repository-generated", contentClass, assertedBy: "assistant", note },
  sourceAssetIds,
  mechanismEvidenceContractSha256: contractHash
});
const additions = [
  makeAsset({
    id: "slider-analysis-carrier-groove-cad-preview-r012",
    filePath: previewPath,
    role: "analysis",
    contentClass: "supplementary-full-size-carrier-groove-cad-preview",
    note: "Static preview shows the rotating carrier, top underside grooves and fixed covered axis. Approval remains interactive.",
    sourceAssetIds: ["slider-analysis-interactive-cad-geometry-config-r012", "slider-analysis-mechanism-evidence-contract-r012"]
  }),
  makeAsset({
    id: "slider-analysis-carrier-groove-cad-validation-r012",
    filePath: validationPath,
    role: "validation",
    contentClass: "carrier-groove-cad-validation-report",
    note: "Records transforms, coverage, alignment, cardinal pointer direction, mobile and Simulator lock evidence.",
    sourceAssetIds: [
      "slider-analysis-interactive-cad-geometry-config-r012",
      "slider-analysis-user-selected-bottom-base-close-r011",
      "slider-intake-haloo-official-07",
      "slider-intake-nxedc-ref-03",
      "slider-intake-nxedc-ref-04"
    ]
  }),
  makeAsset({
    id: "slider-analysis-carrier-groove-cad-sealer-r012",
    filePath: scriptPath,
    role: "process",
    contentClass: "carrier-groove-cad-seal-script",
    note: "Seals the rev 12 contract hash, CAD config, preview and validation evidence.",
    sourceAssetIds: ["slider-analysis-interactive-cad-geometry-config-r012"]
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
    "slider-analysis-mechanism-evidence-contract-r012",
    "slider-analysis-interactive-cad-geometry-config-r012",
    "slider-analysis-carrier-groove-cad-registrar-r012"
  ].includes(asset.id)) {
    asset.mechanismEvidenceContractSha256 = contractHash;
  }
}
stage.status = "ready_for_review";
stage.staleReason = null;
stage.readiness = { ready: true, blockers: [], note: "Complete eight carrier/groove CAD checks. Simulator stays locked." };
stage.validations = stage.validations.filter((item) => item.id !== "carrier-groove-cad-browser-r012");
stage.validations.push({
  id: "carrier-groove-cad-browser-r012",
  status: "pass",
  evidence: "56/56 Node tests and desktop/mobile real-pointer browser smoke passed. Bottom and fixed axis remained static; carrier and top shared theta; top grooves stayed aligned; max travel covered the axis."
});
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev12-carrier-groove-interactive-cad-subapproval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 12 carrier/groove CAD is validated and ready for interactive review. Simulator and all downstream generation remain locked.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-carrier-groove-review-sealed",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 12,
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
