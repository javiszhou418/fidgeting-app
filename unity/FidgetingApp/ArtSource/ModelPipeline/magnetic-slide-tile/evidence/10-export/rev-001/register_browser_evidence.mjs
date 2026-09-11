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
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-001";
const manifest = loadManifest(modelId);
const stage = manifest.stages[9];
if (manifest.revision !== 77 || stage.status !== "ready_for_review" || stage.artifactIds.length !== 31) {
  throw new Error("Expected Gate 10 rev 1 registered at manifest revision 77.");
}
const validation = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/browser-smoke-validation.json`)));
if (!validation.pass || !validation.checks.gate10GlbViewer || !validation.checks.mobile390x844) {
  throw new Error("Gate 10 browser validation failed.");
}
const sourceAssetIds = [
  "magnetic-slide-tile-export-glb-r001",
  "magnetic-slide-tile-export-package-review-board-r001",
  "magnetic-slide-tile-export-texture-channel-board-r001",
];
const definitions = [
  ["browser-export-smoke-validation", "browser-validation", "browser-smoke-validation.json", "validation"],
  ["browser-export-workbench", "browser-workbench", "gate10-workbench-browser.png", "blender-render"],
];
const records = definitions.map(([suffix, slot, file, role]) => {
  const path = `${root}/${file}`;
  const absolutePath = resolveRepoPath(path);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-${suffix}-r001`,
    stageId: "10-export",
    slot,
    path,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role,
    producer: {
      name: file.endsWith(".png") ? "Chrome CDP" : "Node.js",
      version: "Chrome headless / Node.js",
      recipe: "tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      note: "Gate 10 desktop/modal/mobile smoke and interactive GLB viewer evidence.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
stage.artifactIds.push(...records.map((record) => record.id));
stage.validations.push({
  id: "browser-desktop-modal-mobile-glb",
  status: "pass",
  evidence: "Five Gate 10 review cards, modal close/Escape/backdrop/browser-back, the real magnetic-slide-tile GLB viewer, generic GLB regression, and 390×844 mobile all pass.",
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
  const claims = manifest.claims.filter((claim) => claim.stageId === current.id).map(stableJson);
  current.inputDigest = index === 0 ? digestValues([...hashes, ...claims]) : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claims]);
}
const event = {
  id: crypto.randomUUID(),
  type: "stage-browser-evidence-added",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "10-export",
  exportRevision: 1,
  artifactIds: records.map((record) => record.id),
  gate10GlbViewer: true,
  mobileViewport: [390, 844],
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[9].status,
  artifacts: saved.stages[9].artifactIds.length,
  reviewArtifacts: saved.stages[9].reviewArtifactIds.length,
}, null, 2));
