#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const expectedRevision = 115;
const manifest = loadManifest(modelId);
if (manifest.revision !== expectedRevision) {
  throw new Error(`Expected manifest revision ${expectedRevision}, got ${manifest.revision}.`);
}

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../..");
const resolveRepoPath = (repoPath) => path.join(repoRoot, repoPath);
const toRepoPath = (absolutePath) => path.relative(repoRoot, absolutePath).split(path.sep).join("/");
const timestamp = new Date().toISOString();
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");

for (const id of [
  "slider-analysis-workbench-browser-r004",
  "slider-analysis-browser-tests-r004"
]) {
  const asset = manifest.assets.find((candidate) => candidate.id === id);
  if (!asset) throw new Error(`Missing asset: ${id}`);
  const absolutePath = resolveRepoPath(asset.path);
  asset.sha256 = sha256File(absolutePath);
  asset.sizeBytes = fs.statSync(absolutePath).size;
}

const id = "slider-analysis-full-size-preview-registrar-r004";
const absolutePath = fileURLToPath(import.meta.url);
const asset = {
  id,
  stageId: "02-analysis",
  slot: "analysis-evidence",
  path: toRepoPath(absolutePath),
  sha256: sha256File(absolutePath),
  exists: true,
  sizeBytes: fs.statSync(absolutePath).size,
  role: "process",
  producer: {
    name: "fidgeting-model-pipeline",
    version: "1",
    recipe: "Revision-guarded screenshot and browser test hash sync"
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "full-size-preview-hash-sync",
    assertedBy: "assistant",
    note: "最终桌面全页预览为 1440×2606；同步截图与浏览器测试哈希。"
  },
  sourceAssetIds: [
    "slider-analysis-workbench-browser-r004",
    "slider-analysis-browser-tests-r004"
  ]
};
manifest.assets.push(asset);
stage.artifactIds.push(id);
stage.analysisSpec.previewDimensions = { width: 1440, height: 2606 };
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map(
    (assetId) => manifest.assets.find((candidate) => candidate.id === assetId)?.sha256
  ).filter(Boolean).sort().join("\n"))
  .digest("hex");

manifest.revision += 1;
manifest.updatedAt = timestamp;
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-full-size-workbench-preview-registered",
  modelId,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 4,
  artifactId: "slider-analysis-workbench-browser-r004",
  width: 1440,
  height: 2606,
  conclusionCount: 6,
  screenshotWallCount: 0,
  technicalEvidenceCollapsed: true,
  gateStatus: stage.status
});

console.log(JSON.stringify({
  modelId,
  manifestRevision: manifest.revision,
  preview: "1440x2606",
  status: stage.status
}, null, 2));
