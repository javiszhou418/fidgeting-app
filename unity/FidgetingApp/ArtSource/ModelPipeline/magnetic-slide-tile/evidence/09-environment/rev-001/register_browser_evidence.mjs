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
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/09-environment/rev-001";
const manifest = loadManifest(modelId);
const stage = manifest.stages[8];
if (manifest.revision !== 70 || stage.status !== "ready_for_review" || stage.environmentSpec?.revision !== 1) {
  throw new Error("Expected Gate 09 rev 1 at manifest revision 70.");
}
const browser = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/browser-smoke-validation.json`)));
if (!browser.pass) throw new Error("Browser evidence did not pass.");
const sourceAssetIds = [
  "magnetic-slide-tile-environment-blend-r001",
  "magnetic-slide-tile-environment-comparison-board-r001",
  "magnetic-slide-tile-reflection-closeup-comparison-r001",
];
const sourceClaimIds = [
  "slider-gate08-r001-user-approval-r001",
];
const definitions = [
  ["browser-environment-smoke-validation", "validation-report", "browser-smoke-validation.json"],
  ["browser-environment-workbench", "environment-review-board", "gate09-workbench-browser.png"],
];
const records = definitions.map(([suffix, slot, file]) => {
  const path = `${root}/${file}`;
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-${suffix}-r001`,
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
      note: "Gate 09 rev 1 desktop, modal, browser-back, Escape, GLB viewer, and 390×844 mobile workbench checks passed.",
      approvedGate08Decision: "可以吧，然后你继续",
      sourceGeometryDigest: stage.environmentSpec.sourceGeometryDigest,
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
  evidence: "Desktop workbench, eight review cards, modal close/Escape/back, GLB viewer, 390×844 mobile stack, and screenshot passed without runtime or loading failures.",
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
  environmentRevision: 1,
  artifactIds: records.map((record) => record.id),
  browserSmoke: "desktop-modal-mobile-pass",
});
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[8].status,
  environmentRevision: saved.stages[8].environmentSpec.revision,
  artifacts: saved.stages[8].artifactIds.length,
}, null, 2));
