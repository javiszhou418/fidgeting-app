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
const manifest = loadManifest(modelId);
if (manifest.revision !== 109) {
  throw new Error(`Expected manifest revision 109, got ${manifest.revision}.`);
}
const stage = manifest.stages[6];
if (stage.status !== "ready_for_review" || stage.materialRebuildSpec?.revision !== 10) {
  throw new Error("Gate 07 rev 10 is not ready for browser evidence.");
}
const path =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-010/workbench-browser.png";
const absolute = resolveRepoPath(path);
if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
const id = `${modelId}-material-rev10-workbench-browser-r010`;
manifest.assets.push({
  id,
  stageId: "07-material",
  slot: "workbench",
  path,
  sha256: sha256File(absolute),
  exists: true,
  sizeBytes: fs.statSync(absolute).size,
  role: "validation",
  producer: {
    name: "Chrome headless CDP browser smoke",
    version: "2026-08-26",
    recipe: "tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs",
  },
  provenance: {
    origin: "repository-generated",
    assertedBy: "assistant",
    contentClass: "browser-workbench",
    gate07Revision: 10,
    unityTouched: false,
  },
  sourceAssetIds: stage.reviewArtifactIds,
  sourceClaimIds: [],
});
stage.artifactIds.push(id);
stage.validations.push({
  id: "browser-modal-mobile-axis-review",
  status: "pass",
  evidence: "Four review cards render in order; modal close/Escape/backdrop/browser Back pass; GLB viewer loads; 390×844 uses one asset column without overflow; technical details default closed.",
});

function stableJson(value) {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}
for (let index = 0; index < manifest.stages.length; index += 1) {
  const candidate = manifest.stages[index];
  const assetHashes = candidate.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claimRecords = manifest.claims
    .filter((claim) => claim.stageId === candidate.id)
    .map(stableJson);
  candidate.inputDigest = index === 0
    ? digestValues([...assetHashes, ...claimRecords])
    : manifest.stages[index - 1].outputDigest;
  candidate.outputDigest = digestValues([...assetHashes, ...claimRecords]);
}
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const event = {
  id: crypto.randomUUID(),
  type: "stage-browser-evidence-registered",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "07-material",
  revision: 10,
  artifactId: id,
  desktopModalChecks: "pass",
  mobile390x844: "pass",
  reviewCardCount: 4,
  technicalDetailsCollapsed: true,
  gateStatus: stage.status,
};
saveManifest(manifest, event);
console.log(JSON.stringify(event, null, 2));
