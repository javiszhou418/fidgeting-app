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
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-001";
const manifest = loadManifest(modelId);
const stage = manifest.stages[7];
if (manifest.revision !== 67 || stage.status !== "ready_for_review" || stage.lightingSpec?.revision !== 1) {
  throw new Error("Expected Gate 08 rev 1 at manifest revision 67.");
}
const browser = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/browser-smoke-validation.json`)));
if (!browser.pass) throw new Error("Browser evidence did not pass.");
const sourceAssetIds = [
  "magnetic-slide-tile-lighting-blend-r001",
  "magnetic-slide-tile-lighting-view-board-r001",
  "magnetic-slide-tile-lighting-pass-board-r001",
];
const sourceClaimIds = [
  "slider-gate07-r007-user-approval-r001",
];
const definitions = [
  ["browser-smoke-validation", "validation-report", "browser-smoke-validation.json"],
  ["browser-workbench", "lighting-review-board", "gate08-workbench-browser.png"],
];
const records = definitions.map(([suffix, slot, file]) => {
  const path = `${root}/${file}`;
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-${suffix}-r001`,
    stageId: "08-lighting",
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
      note: "Gate 08 rev 1 workbench browser evidence; desktop, modal, browser-back, Escape, GLB viewer, and 390×844 mobile checks passed.",
      approvedGate07Decision: "可以",
      sourceGeometryDigest: stage.lightingSpec.sourceGeometryDigest,
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
  evidence: "Desktop workbench, thirteen review cards, modal close/Escape/back, GLB viewer, 390×844 mobile stack, and screenshot passed without runtime or loading failures.",
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
  stageId: "08-lighting",
  lightingRevision: 1,
  artifactIds: records.map((record) => record.id),
  browserSmoke: "desktop-modal-mobile-pass",
});
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[7].status,
  lightingRevision: saved.stages[7].lightingSpec.revision,
  artifacts: saved.stages[7].artifactIds.length,
}, null, 2));
