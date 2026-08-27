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
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/09-environment/rev-002";
const manifest = loadManifest(modelId);
const stage = manifest.stages[8];
if (manifest.revision !== 73 || stage.status !== "ready_for_review" || stage.environmentSpec?.revision !== 2) {
  throw new Error("Expected Gate 09 rev 2 at manifest revision 73.");
}
const browser = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/browser-smoke-validation.json`)));
if (!browser.pass || !Object.values(browser.checks).every(Boolean)) {
  throw new Error("Gate 09 rev 2 browser evidence did not pass.");
}
const sourceAssetIds = [
  "magnetic-slide-tile-open-environment-blend-r002",
  "magnetic-slide-tile-open-environment-comparison-board-r002",
  "magnetic-slide-tile-open-style-review-board-r002",
  "magnetic-slide-tile-closed-open-sequence-board-r002",
];
const sourceClaimIds = [
  "slider-gate08-r001-user-approval-r001",
];
const definitions = [
  ["browser-open-environment-smoke-validation", "validation-report", "browser-smoke-validation.json"],
  ["browser-open-environment-workbench", "environment-review-board", "gate09-open-workbench-browser.png"],
];
const records = definitions.map(([suffix, slot, file]) => {
  const path = `${root}/${file}`;
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-${suffix}-r002`,
    stageId: "09-environment",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role: "process",
    producer: {
      name: "Chrome CDP browser smoke",
      version: "2026-08-25",
      recipe: "tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      note: "Gate 09 rev 2 desktop review, eight current cards, modal close/Escape/back, GLB viewer, and 390×844 mobile checks passed.",
      sourceGeometryDigest: stage.environmentSpec.sourceGeometryDigest,
      openTravelMm: 21,
      openRotationDegrees: 0,
    },
    sourceAssetIds,
    sourceClaimIds,
  };
});
manifest.assets.push(...records);
stage.revision += 1;
stage.artifactIds.push(...records.map((record) => record.id));
stage.validations.push({
  id: "browser-open-smoke-modal-mobile",
  status: "pass",
  evidence: "Desktop open review, eight current cards, modal close/Escape/back, GLB viewer, 390×844 mobile stack, and screenshot passed without runtime or loading failures.",
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
  stageId: "09-environment",
  environmentRevision: 2,
  artifactIds: records.map((record) => record.id),
  browserSmoke: "desktop-modal-mobile-pass",
});
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[8].status,
  environmentRevision: saved.stages[8].environmentSpec.revision,
  artifacts: saved.stages[8].artifactIds.length,
  reviewArtifacts: saved.stages[8].reviewArtifactIds.length,
}, null, 2));
