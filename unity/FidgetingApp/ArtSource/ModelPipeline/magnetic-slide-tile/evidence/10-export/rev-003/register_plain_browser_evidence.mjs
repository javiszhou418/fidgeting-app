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
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-003";
const manifest = loadManifest(modelId);
const stage = manifest.stages[9];
if (manifest.revision !== 85
  || stage.status !== "ready_for_review"
  || stage.exportSpec?.reviewRevision !== 3
  || stage.reviewArtifactIds.length !== 2) {
  throw new Error("Expected Gate 10 plain review at manifest revision 85.");
}
const report = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/plain-browser-smoke-validation.json`)));
if (!report.pass
  || !report.checks.onePlainQuestion
  || !report.checks.twoPrimaryImages
  || !report.checks.technicalDetailsCollapsed
  || !report.checks.mobileLayout
  || !report.checks.realGlbViewer) {
  throw new Error("Plain review browser evidence did not pass.");
}

const definitions = [
  ["plain-browser-registrar", "registration-source", "register_plain_browser_evidence.mjs", "process"],
  ["plain-browser-validation", "browser-validation", "plain-browser-smoke-validation.json", "validation"],
  ["plain-browser-screenshot", "browser-workbench", "gate10-plain-workbench-browser.png", "blender-render"],
];
const records = definitions.map(([suffix, slot, file, role]) => {
  const path = `${root}/${file}`;
  const absolutePath = resolveRepoPath(path);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-${suffix}-r003`,
    stageId: "10-export",
    slot,
    path,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role,
    producer: {
      name: file.endsWith(".png") ? "Chrome DevTools Protocol" : "Node.js",
      version: file.endsWith(".png") ? "Google Chrome Headless" : process.version,
      recipe: file.endsWith(".png")
        ? "CDP screenshot after browser-cdp-smoke.mjs"
        : `${root}/register_plain_browser_evidence.mjs`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      reviewRevision: 3,
      note: "Browser verification for the plain-Chinese Gate 10 round-edge review.",
    },
    sourceAssetIds: [
      "magnetic-slide-tile-round-edge-location-r003",
      "magnetic-slide-tile-round-edge-before-after-r003",
      "magnetic-slide-tile-export-glb-r002",
    ],
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
stage.revision += 1;
stage.artifactIds.push(...records.map((record) => record.id));
stage.validations.push(
  { id: "plain-browser-default", status: "pass", evidence: "Default Gate 10 screen shows two primary images, one plain-Chinese question, and no export jargon." },
  { id: "plain-browser-modal", status: "pass", evidence: "Close button, Escape, backdrop, and browser-back all return to the round-edge review." },
  { id: "plain-browser-mobile", status: "pass", evidence: "390×844 layout has one image column and no horizontal overflow." },
  { id: "plain-browser-glb", status: "pass", evidence: "The immutable rev 2 GLB loads in the real viewer from collapsed technical details." },
);
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
  exportRevision: 2,
  reviewRevision: 3,
  artifactIds: records.map((record) => record.id),
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[9].status,
  artifactIds: saved.stages[9].artifactIds.length,
  reviewArtifactIds: saved.stages[9].reviewArtifactIds,
}, null, 2));
