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

const manifest = loadManifest("magnetic-slide-tile");
const stage = manifest.stages.find((item) => item.id === "11-unity-parity");
const asset = manifest.assets.find(
  (item) => item.id === "magnetic-slide-tile-unity-parity-node-test-r010");
if (manifest.revision !== 205 || stage?.status !== "draft" || !asset) {
  throw new Error("Expected blocked Gate 11 rev 10 at pipeline rev 205.");
}
const absolute = resolveRepoPath(asset.path);
asset.sha256 = sha256File(absolute);
asset.sizeBytes = fs.statSync(absolute).size;

const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map((assetId) =>
    manifest.assets.find((candidate) => candidate.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((claim) => claim.stageId === current.id)
    .map(stableJson);
  current.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claims]);
}
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "asset-hash-refreshed",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  revision: 10,
  assetId: asset.id,
  sha256: asset.sha256,
  status: "draft",
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate11: saved.stages[10].status,
  gate12: saved.stages[11].status,
}, null, 2));
