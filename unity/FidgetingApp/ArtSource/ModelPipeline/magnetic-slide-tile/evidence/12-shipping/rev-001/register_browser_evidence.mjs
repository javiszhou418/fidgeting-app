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
const root =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-001";
const manifest = loadManifest(modelId);
const stage = manifest.stages[11];
if (manifest.revision !== 94
  || stage.status !== "ready_for_review"
  || stage.shippingSpec?.revision !== 1) {
  throw new Error("Expected Gate 12 rev 1 ready for review at revision 94.");
}
const definitions = [
  ["magnetic-slide-tile-gate12-browser-registrar-r001", "registration-source", `${root}/register_browser_evidence.mjs`, "process"],
  ["magnetic-slide-tile-gate12-browser-validation-r001", "browser-validation", `${root}/browser-smoke-validation.json`, "validation"],
  ["magnetic-slide-tile-gate12-browser-screenshot-r001", "browser-screenshot", `${root}/gate12-workbench-browser.png`, "unity-render"],
];
const records = definitions.map(([id, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id,
    stageId: "12-shipping",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Chrome CDP / Node.js",
      version: "2026-08-25",
      recipe: "tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate12Revision: 1,
    },
    sourceAssetIds: stage.reviewArtifactIds,
    sourceClaimIds: ["slider-gate11-rev2-approval-r001"],
  };
});
manifest.assets.push(...records);
stage.artifactIds.push(...records.map((record) => record.id));
stage.validations.push({
  id: "browser-desktop-modal-mobile-gate12",
  status: "pass",
  evidence: "Plain Chinese review, three current assets, collapsed details, image modal close paths, real GLB viewer and 390×844 single-column mobile passed.",
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
  const hashes = current.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((claim) => claim.stageId === current.id)
    .map(stableJson);
  current.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claims]);
}
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "browser-evidence-registered",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "12-shipping",
  revision: 1,
  artifactIds: records.map((record) => record.id),
});
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[11].status,
  artifactIds: saved.stages[11].artifactIds.length,
}, null, 2));
