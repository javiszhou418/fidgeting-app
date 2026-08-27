#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const manifest = loadManifest(modelId);
if (manifest.revision !== 111) throw new Error(`Expected manifest revision 111, got ${manifest.revision}.`);
const stage = manifest.stages[1];
if (stage.status !== "ready_for_review" || stage.analysisSpec?.revision !== 3) {
  throw new Error("Gate 02 rev 3 is not the active review.");
}

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../..");
const toRepoPath = (absolute) => path.relative(repoRoot, absolute).split(path.sep).join("/");
const makeAsset = (id, slot, absolute, role, contentClass, sourceAssetIds, note, recipe) => ({
  id,
  stageId: "02-analysis",
  slot,
  path: toRepoPath(absolute),
  sha256: sha256File(absolute),
  exists: true,
  sizeBytes: fs.statSync(absolute).size,
  role,
  producer: { name: "fidgeting-model-pipeline", version: "1", recipe },
  provenance: {
    origin: "repository-generated",
    contentClass,
    assertedBy: "assistant",
    note,
  },
  sourceAssetIds,
});
const screenshotPath = path.join(here, "workbench-browser.png");
const scriptPath = fileURLToPath(import.meta.url);
if (!fs.existsSync(screenshotPath)) throw new Error("Missing browser screenshot.");
const screenshotId = "slider-analysis-video-workbench-browser-r003";
const scriptId = "slider-analysis-video-browser-registrar-r003";
if (manifest.assets.some((asset) => [screenshotId, scriptId].includes(asset.id))) {
  throw new Error("Browser evidence is already registered.");
}
const reviewArtifactIds = [...stage.reviewArtifactIds];
manifest.assets.push(
  makeAsset(
    screenshotId,
    "analysis-evidence",
    screenshotPath,
    "validation",
    "desktop-browser-workbench-smoke",
    reviewArtifactIds,
    "真实工作台截图；默认中文问题、六张板、技术细节收起。浏览器同时验证 390×844 单列布局与 H.264 视频元数据播放。",
    "Headless Chrome CDP desktop, modal, Escape, backdrop, browser-back, mobile and video playback smoke"),
  makeAsset(
    scriptId,
    "analysis-evidence",
    scriptPath,
    "process",
    "browser-evidence-registration-script",
    [screenshotId],
    "将工作台截图和浏览器验证结果登记到 Gate 02 rev 3。",
    "Revision-guarded pipeline browser evidence registration"),
);
stage.artifactIds.push(screenshotId, scriptId);
stage.validations.push({
  id: "browser-desktop-modal-mobile-video-playback",
  status: "pass",
  evidence: "Desktop rendered six boards and three video links; image modal close/Escape/backdrop/browser-back passed; 390×844 used one column with no overflow; H.264 proxy loaded 720×1280 metadata and duration 14.214 s without error.",
});
stage.analysisSpec.supportingAssetIds.push(screenshotId);

const digestValues = (values) => crypto.createHash("sha256").update(
  values.filter(Boolean).sort().join("\n")).digest("hex");
const stableJson = (value) => {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
};
for (let index = 0; index < manifest.stages.length; index += 1) {
  const candidate = manifest.stages[index];
  const hashes = candidate.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims.filter((claim) => claim.stageId === candidate.id).map(stableJson);
  candidate.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  candidate.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const event = {
  id: crypto.randomUUID(),
  type: "stage-video-mechanism-browser-evidence-registered",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "02-analysis",
  analysisEvidenceRevision: 3,
  artifactId: screenshotId,
  desktopModalChecks: "pass",
  mobile390x844: "pass",
  h264PlaybackMetadata: "pass",
  reviewCardCount: 6,
  sourceVideoLinkCount: 3,
  technicalDetailsCollapsed: true,
  gateStatus: stage.status,
};
saveManifest(manifest, event);
console.log(JSON.stringify(event, null, 2));
