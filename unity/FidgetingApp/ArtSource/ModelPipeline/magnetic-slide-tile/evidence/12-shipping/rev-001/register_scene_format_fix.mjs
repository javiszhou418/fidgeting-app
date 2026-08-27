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
if (manifest.revision !== 95 || stage.status !== "ready_for_review") {
  throw new Error("Expected Gate 12 ready for review at revision 95.");
}
const scene = manifest.assets.find((asset) =>
  asset.id === "magnetic-slide-tile-gate12-shipping-scene-r001");
const sceneAbsolute = resolveRepoPath(scene.path);
scene.sha256 = sha256File(sceneAbsolute);
scene.sizeBytes = fs.statSync(sceneAbsolute).size;
scene.provenance.formatOnlyRevision = "trim-yaml-trailing-whitespace";

const scriptPath = `${root}/register_scene_format_fix.mjs`;
const scriptAbsolute = resolveRepoPath(scriptPath);
const script = {
  id: "magnetic-slide-tile-gate12-scene-format-registrar-r001",
  stageId: "12-shipping",
  slot: "registration-source",
  path: scriptPath,
  sha256: sha256File(scriptAbsolute),
  exists: true,
  sizeBytes: fs.statSync(scriptAbsolute).size,
  role: "process",
  producer: {
    name: "Node.js",
    version: "2026-08-25",
    recipe: scriptPath,
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "format-only-registration",
    assertedBy: "assistant",
    gate12Revision: 1,
  },
  sourceAssetIds: [scene.id],
  sourceClaimIds: ["slider-gate11-rev2-approval-r001"],
};
manifest.assets.push(script);
stage.artifactIds.push(script.id);
stage.validations.push({
  id: "shipping-scene-yaml-format",
  status: "pass",
  evidence: "Trimmed YAML trailing whitespace only; candidate activation, scene objects and serialized values are unchanged.",
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
  type: "stage-evidence-revised",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "12-shipping",
  revision: 1,
  reason: "trim-shipping-scene-yaml-trailing-whitespace",
  geometryChanged: false,
  materialChanged: false,
  activationStateChanged: false,
  artifactIds: [scene.id, script.id],
});
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[11].status,
  artifactIds: saved.stages[11].artifactIds.length,
}, null, 2));
