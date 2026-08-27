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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-002";
const manifest = loadManifest(modelId);
const stage = manifest.stages[10];
if (manifest.revision !== 91
  || stage.status !== "ready_for_review"
  || stage.unityParitySpec?.revision !== 2) {
  throw new Error("Expected Gate 11 rev 2 ready for review at revision 91.");
}
const definitions = [
  ["magnetic-slide-tile-unity-parity-rev2-browser-registrar-r002", "registration-source", `${root}/register_browser_evidence.mjs`, "process"],
  ["magnetic-slide-tile-unity-parity-rev2-browser-validation-r002", "browser-validation", `${root}/browser-smoke-validation.json`, "validation"],
  ["magnetic-slide-tile-unity-parity-rev2-browser-screenshot-r002", "browser-screenshot", `${root}/gate11-rev2-workbench-browser.png`, "unity-render"],
];
const sources = [
  "magnetic-slide-tile-export-fbx-r002",
  "magnetic-slide-tile-unity-parity-rev2-location-r002",
  "magnetic-slide-tile-unity-parity-rev2-before-after-r002",
  "magnetic-slide-tile-unity-parity-rev2-wire-proof-r002",
];
const records = definitions.map(([id, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
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
      name: "Chrome CDP / Node.js",
      version: "2026-08-25",
      recipe: "tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate11Revision: 2,
    },
    sourceAssetIds: sources,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
stage.artifactIds.push(...records.map((record) => record.id));
stage.validations.push({
  id: "browser-desktop-modal-mobile-rev2",
  status: "pass",
  evidence: "Plain Chinese three-image review, collapsed technical details, image modal close paths, real GLB viewer, and 390×844 single-column mobile passed.",
});
stage.unityParitySpec.unityVersion = "6000.5.6f1";
stage.unityParitySpec.urpVersion = "17.5.0";
stage.unityParitySpec.motion = {
  pointAxisMeters: [0, 0, 0.0095],
  slideDirection: [0, 0, -1],
  slideTravelMeters: 0.021,
  detents: {
    count: 30,
    stepDegrees: 12,
    deliveryState: "specified-only-not-runtime-integrated",
  },
};
stage.unityParitySpec.textureImports = {
  preservedFromRev1: true,
  upperLowerArtworkIndependent: true,
  iosChannelPacks: "ASTC_4x4 / max 1024 / linear / alpha input / mipmaps on",
  deviceMemoryMeasured: false,
};

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
  stageId: "11-unity-parity",
  revision: 2,
  artifactIds: records.map((record) => record.id),
});
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[10].status,
  artifactIds: saved.stages[10].artifactIds.length,
}, null, 2));
