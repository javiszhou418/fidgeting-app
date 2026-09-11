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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-001";
const manifest = loadManifest(modelId);
const stage = manifest.stages[10];
if (manifest.revision !== 88
  || stage.status !== "ready_for_review"
  || stage.revision !== 1) {
  throw new Error("Expected Gate 11 rev 1 at manifest revision 88.");
}
const validation = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${root}/browser-smoke-validation.json`)));
if (!validation.pass) throw new Error("Browser smoke validation failed.");
const definitions = [
  ["magnetic-slide-tile-unity-parity-browser-registrar-r001", "registration-source", `${root}/register_browser_evidence.mjs`, "process"],
  ["magnetic-slide-tile-unity-parity-browser-validation-r001", "browser-validation", `${root}/browser-smoke-validation.json`, "validation"],
  ["magnetic-slide-tile-unity-parity-browser-screenshot-r001", "browser-screenshot", `${root}/gate11-workbench-browser.png`, "blender-render"],
];
const sourceAssetIds = [
  "magnetic-slide-tile-export-fbx-r002",
  "magnetic-slide-tile-export-glb-r002",
];
const records = definitions.map(([id, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  return {
    id,
    stageId: "11-unity-parity",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: path.endsWith(".png") ? "Chrome CDP" : "Node.js",
      version: "Chrome headless / Node.js",
      recipe: "tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate11Revision: 1,
      note: "Real desktop/modal/mobile/GLB browser smoke for Gate 11.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
stage.artifactIds.push(...records.map((record) => record.id));
stage.validations.push({
  id: "gate11-browser-smoke",
  status: "pass",
  evidence: "Desktop one-board review, modal close/Escape/backdrop/browser-back, collapsed technical details, real GLB viewer, and 390×844 single-column mobile passed.",
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
manifest.currentState.diagnosis = manifest.currentState.diagnosis.replace(
  "Gate 12、runtime、Haptic、build/install/phone 均未开始。",
  "Gate 11 desktop/modal/mobile/real-GLB browser smoke 通过。Gate 12、runtime、Haptic、build/install/phone 均未开始。");
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-evidence-revised",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  revision: 1,
  reason: "register-real-browser-smoke",
  artifactIds: records.map((record) => record.id),
});
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[10].status,
  artifactIds: saved.stages[10].artifactIds.length,
}, null, 2));
