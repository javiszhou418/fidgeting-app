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
const previewPath = path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate02-rev13-closed-stop-cad.png");
const validationPath = path.join(here, "validation-report.json");
const registrarPath = path.join(here, "register_closed_stop_cad_review.mjs");
const correctionPath = path.join(here, "closed-stop-user-correction.md");
const scriptPath = fileURLToPath(import.meta.url);
for (const filePath of [contractPath, configPath, previewPath, validationPath, registrarPath, correctionPath]) {
  if (!fs.existsSync(filePath)) throw new Error(`Missing seal input ${filePath}`);
}
const contractHash = sha256File(contractPath);
const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
config.contractSha256 = contractHash;
fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`);
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 137) throw new Error(`Expected revision 137, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 13) throw new Error("Gate 02 rev 13 must be active.");
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
  producer: { name: "fidgeting-model-pipeline", version: "2026-08-26", recipe: "Gate 02 rev 13 hard closed-stop validation" },
  provenance: { origin: "repository-generated", contentClass, assertedBy: "assistant", note },
  sourceAssetIds,
  mechanismEvidenceContractSha256: contractHash
});
const additions = [
  makeAsset({
    id: "slider-analysis-closed-stop-cad-preview-r013",
    filePath: previewPath,
    role: "analysis",
    contentClass: "supplementary-full-size-hard-closed-stop-cad-preview",
    note: "Static preview shows exact closed overlap, closed-stop lines and the clamped live indicator. Approval remains interactive.",
    sourceAssetIds: ["slider-analysis-interactive-cad-geometry-config-r013", "slider-analysis-closed-stop-user-correction-r013"]
  }),
  makeAsset({
    id: "slider-analysis-closed-stop-cad-validation-r013",
    filePath: validationPath,
    role: "validation",
    contentClass: "hard-closed-stop-cad-validation-report",
    note: "Records exact overlap, API/keyboard/pointer clamps, tangential rotation, mobile, zoom/pan and Simulator lock evidence.",
    sourceAssetIds: ["slider-analysis-interactive-cad-geometry-config-r013", "slider-analysis-closed-stop-user-correction-r013"]
  }),
  makeAsset({
    id: "slider-analysis-closed-stop-cad-sealer-r013",
    filePath: scriptPath,
    role: "process",
    contentClass: "hard-closed-stop-cad-seal-script",
    note: "Seals the final rev 13 contract hash, CAD config, preview and validation evidence.",
    sourceAssetIds: ["slider-analysis-interactive-cad-geometry-config-r013"]
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
    "slider-analysis-mechanism-evidence-contract-r013",
    "slider-analysis-interactive-cad-geometry-config-r013",
    "slider-analysis-closed-stop-cad-registrar-r013"
  ].includes(asset.id)) {
    asset.mechanismEvidenceContractSha256 = contractHash;
  }
}
stage.status = "ready_for_review";
stage.staleReason = null;
stage.readiness = { ready: true, blockers: [], note: "Complete nine CAD checks including the exact closed hard stop. Simulator stays locked." };
stage.validations = stage.validations.filter((item) => item.id !== "hard-closed-stop-browser-r013");
stage.validations.push({
  id: "hard-closed-stop-browser-r013",
  status: "pass",
  evidence: "61/61 Node tests and desktop/mobile real-pointer browser smoke passed. Negative API, ArrowDown, repeated inward pointer and near-stop diagonal inputs stopped at exact s=0 while tangential rotation remained available."
});
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev13-hard-closed-stop-interactive-cad-subapproval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 13 hard closed-stop CAD is validated and ready for interactive review. Simulator and all downstream generation remain locked.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-hard-closed-stop-review-sealed",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 13,
  correctionAssetId: "slider-analysis-closed-stop-user-correction-r013",
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
