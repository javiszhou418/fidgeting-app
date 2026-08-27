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
const expectedRevision = 114;
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
if (stage.analysisSpec?.revision !== 4 || stage.status !== "ready_for_review") {
  throw new Error("Gate 02 rev 4 must be ready_for_review.");
}

const refreshRegisteredAsset = (id) => {
  const asset = manifest.assets.find((candidate) => candidate.id === id);
  if (!asset) throw new Error(`Missing registered asset: ${id}`);
  const absolutePath = resolveRepoPath(asset.path);
  asset.sha256 = sha256File(absolutePath);
  asset.sizeBytes = fs.statSync(absolutePath).size;
  asset.exists = true;
};
refreshRegisteredAsset("slider-analysis-mechanism-sandbox-ui-r004");
refreshRegisteredAsset("slider-analysis-mechanism-sandbox-style-r004");

const assetIds = new Set(manifest.assets.map((asset) => asset.id));
const addAsset = ({ id, slot, absolutePath, role, contentClass, sourceAssetIds, note, recipe }) => {
  if (assetIds.has(id)) throw new Error(`Asset already exists: ${id}`);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing asset: ${absolutePath}`);
  const asset = {
    id,
    stageId: "02-analysis",
    slot,
    path: toRepoPath(absolutePath),
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role,
    producer: { name: "fidgeting-model-pipeline", version: "1", recipe },
    provenance: {
      origin: "repository-generated",
      contentClass,
      assertedBy: "assistant",
      note
    },
    sourceAssetIds
  };
  manifest.assets.push(asset);
  assetIds.add(id);
  return asset;
};

const conclusionId = "slider-analysis-conclusion-review-r004";
const coreId = "slider-analysis-mechanism-sandbox-core-r004";
const screenshot = addAsset({
  id: "slider-analysis-workbench-browser-r004",
  slot: "analysis-evidence",
  absolutePath: path.join(here, "workbench-browser.png"),
  role: "validation",
  contentClass: "full-page-conclusion-and-interactive-sandbox-preview",
  sourceAssetIds: [conclusionId, coreId],
  note: "真实桌面工作台全页截图；默认显示六条结论、比例边界与机构手感沙盒，技术证据收起。",
  recipe: "Chrome CDP full-page screenshot after desktop and mobile smoke checks"
});
const validation = addAsset({
  id: "slider-analysis-validation-r004",
  slot: "analysis-evidence",
  absolutePath: path.join(here, "validation-report.json"),
  role: "validation",
  contentClass: "gate02-interactive-review-validation-report",
  sourceAssetIds: [screenshot.id, coreId],
  note: "汇总确定性物理、浏览器 pointer、移动端、modal、视频和 pipeline 验证。",
  recipe: "Focused validation summary"
});
const browserTests = addAsset({
  id: "slider-analysis-browser-tests-r004",
  slot: "analysis-evidence",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs"),
  role: "validation",
  contentClass: "desktop-mobile-pointer-modal-video-browser-tests",
  sourceAssetIds: [screenshot.id, coreId],
  note: "覆盖 pointer 滑动／旋转、实时值、reset、控件、移动布局、modal 返回和视频播放。",
  recipe: "Chrome DevTools Protocol browser smoke test"
});
const pipelineGuidance = addAsset({
  id: "slider-analysis-pipeline-guidance-r004",
  slot: "analysis-evidence",
  absolutePath: resolveRepoPath("skills/fidgeting-model-pipeline/references/pipeline-contract.md"),
  role: "contract",
  contentClass: "future-mechanical-gate-two-layer-review-guidance",
  sourceAssetIds: [conclusionId, coreId],
  note: "未来机械 Gate 采用双层结论式报告、归一化比例和交互沙盒边界。",
  recipe: "Repository model pipeline contract update"
});
const workbenchContract = addAsset({
  id: "slider-analysis-workbench-contract-r004",
  slot: "analysis-evidence",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/pipeline-contract.mjs"),
  role: "contract",
  contentClass: "workbench-stage-two-layer-guidance",
  sourceAssetIds: [pipelineGuidance.id],
  note: "工作台 Gate 02 描述同步结论式用户层和完整内部证据层。",
  recipe: "Workbench pipeline stage contract update"
});
const registrar = addAsset({
  id: "slider-analysis-validation-registrar-r004",
  slot: "analysis-evidence",
  absolutePath: fileURLToPath(import.meta.url),
  role: "process",
  contentClass: "browser-validation-and-hash-sync-registrar",
  sourceAssetIds: [validation.id, screenshot.id],
  note: "登记验证证据，并同步最终 app/style 哈希。",
  recipe: "Revision-guarded validation evidence registration"
});

stage.artifactIds.push(
  screenshot.id,
  validation.id,
  browserTests.id,
  pipelineGuidance.id,
  workbenchContract.id,
  registrar.id
);
stage.validations.push({
  id: "browser-pointer-mobile-modal-video",
  status: "pass",
  evidence: "Pointer slide/rotate, live values, controls, reset, 390x844 layout, close/Escape/backdrop/browser-back and H.264 playback passed."
});
stage.analysisSpec.validationAssetIds = [validation.id, screenshot.id, browserTests.id];
stage.analysisSpec.previewPath = screenshot.path;
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256
  ).filter(Boolean).sort().join("\n"))
  .digest("hex");

manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev4-interactive-mechanism-review-pending";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-review-validation-registered",
  modelId,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 4,
  artifactIds: [
    screenshot.id,
    validation.id,
    browserTests.id,
    pipelineGuidance.id,
    workbenchContract.id,
    registrar.id
  ],
  deterministicMechanismTests: "8/8-pass",
  workbenchTests: "23/23-pass",
  browserDesktopPointer: "pass",
  browserMobile390x844: "pass",
  modalReturn: "pass",
  videoPlayback: "pass",
  gateStatus: stage.status,
  visualApproval: "pending",
  phonePush: "not-started"
});

console.log(JSON.stringify({
  modelId,
  manifestRevision: manifest.revision,
  stageStatus: stage.status,
  previewPath: screenshot.path
}, null, 2));
