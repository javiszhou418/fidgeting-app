#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import {
  digestValues,
  loadManifest,
  resolveRepoPath,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-006";
const manifest = loadManifest(modelId);
const stage = manifest.stages[6];
if (manifest.revision !== 61 || stage.status !== "ready_for_review" || stage.materialSpec?.revision !== 6) {
  throw new Error("Expected Gate 07 rev 6 at manifest revision 61.");
}
const sourceAssetIds = [
  "magnetic-slide-tile-geometry-blend-r001",
  "magnetic-slide-tile-motif-mask-r002",
  "slider-intake-haloo-official-04",
  "slider-intake-nxedc-ref-01",
];
const sourceClaimIds = [
  "slider-analysis-claim-material-language",
  "slider-blockout-point-axis-distinction-r003",
  "slider-ratchet-30-detent-requirement-r001",
];
const definitions = [
  ["browser-smoke-validation", "validation-report", "browser-smoke-validation.json"],
  ["browser-workbench", "material-process-board", "gate07-workbench-browser.png"],
];
const records = definitions.map(([suffix, slot, file]) => {
  const path = `${root}/${file}`;
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-${suffix}-r006`,
    stageId: "07-material",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role: "process",
    producer: {
      name: "Chrome CDP browser smoke",
      version: "2026-08-24",
      recipe: "tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      note: "Gate 07 rev 6 real workbench browser evidence; desktop, modal, browser-back, Escape, and 390×844 mobile checks passed.",
      userClaimIds: sourceClaimIds,
      lineageAssetId: "magnetic-slide-tile-motif-mask-r002",
      lineageSha256: stage.materialSpec.artwork.sourceSha256,
      notNewExactTraceClaim: true,
    },
    sourceAssetIds,
    sourceClaimIds,
  };
});
manifest.assets.push(...records);
stage.revision += 1;
stage.artifactIds.push(...records.map((record) => record.id));
stage.validations.push({
  id: "browser-smoke-modal-mobile",
  status: "pass",
  evidence: "Desktop workbench, ten review cards, modal close/Escape/back, 390×844 mobile stack, and real screenshot passed without runtime or loading failures.",
});
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map((assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claimRecords = manifest.claims.filter((claim) => claim.stageId === current.id).map(stableJson);
  current.inputDigest = index === 0 ? digestValues([...hashes, ...claimRecords]) : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claimRecords]);
}
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-evidence-updated",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "07-material",
  materialRevision: 6,
  artifactIds: records.map((record) => record.id),
  browserSmoke: "desktop-modal-mobile-pass",
});
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[6].status,
  materialRevision: saved.stages[6].materialSpec.revision,
  artifacts: saved.stages[6].artifactIds.length,
}, null, 2));
