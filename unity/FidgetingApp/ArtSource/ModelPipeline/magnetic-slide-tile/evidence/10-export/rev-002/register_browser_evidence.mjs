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
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-002";
const manifest = loadManifest(modelId);
const stage = manifest.stages[9];
if (manifest.revision !== 82 || stage.status !== "ready_for_review" || stage.exportSpec?.revision !== 2) {
  throw new Error("Expected Gate 10 rev 2 review at manifest revision 82.");
}
const report = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/browser-smoke-validation.json`)));
if (!report.pass || !report.checks.realGlbViewer || !report.checks.mobile) {
  throw new Error("Gate 10 rev 2 browser evidence failed.");
}
const definitions = [
  ["browser-export-registrar", "registration-source", "register_browser_evidence.mjs", "process"],
  ["browser-export-smoke-validation", "validation-report", "browser-smoke-validation.json", "validation"],
  ["browser-export-workbench", "browser-review", "gate10-workbench-browser.png", "blender-render"],
];
const sourceAssetIds = [
  "magnetic-slide-tile-export-glb-r002",
  "magnetic-slide-tile-export-shading-review-board-r002",
  "magnetic-slide-tile-collision-non-rendering-panel-r002",
];
const records = definitions.map(([suffix, slot, file, role]) => {
  const path = `${root}/${file}`;
  const absolutePath = resolveRepoPath(path);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-${suffix}-r002`,
    stageId: "10-export",
    slot,
    path,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role,
    producer: {
      name: file.endsWith(".png") ? "Chrome CDP" : "Node.js",
      version: file.endsWith(".png") ? "Google Chrome headless" : "Node.js",
      recipe: file.endsWith(".png")
        ? "tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs"
        : `${root}/${file.endsWith(".mjs") ? file : "register_browser_evidence.mjs"}`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      exportRevision: 2,
      note: "Desktop modal, mobile layout, and real GLB viewer evidence for Gate 10 rev 2.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
stage.artifactIds.push(...records.map((record) => record.id));
stage.validations.push({
  id: "browser-modal-mobile-glb",
  status: "pass",
  evidence: "Desktop evidence cards and modal controls passed; 390×844 layout has one asset column and no horizontal overflow; real GLB viewer loaded with six camera controls.",
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
manifest.currentState.diagnosis += " Desktop/modal/mobile/real-GLB browser smoke 已通过。";
const event = {
  id: crypto.randomUUID(),
  type: "stage-browser-evidence-added",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "10-export",
  exportRevision: 2,
  artifactIds: records.map((record) => record.id),
  gate10GlbViewer: true,
  mobileViewport: [390, 844],
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[9].status,
  artifacts: saved.stages[9].artifactIds.length,
}, null, 2));
