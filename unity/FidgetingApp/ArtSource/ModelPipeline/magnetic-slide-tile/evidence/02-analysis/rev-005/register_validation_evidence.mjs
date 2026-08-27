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
const expectedRevision = 117;
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
if (stage.status !== "ready_for_review" || stage.analysisSpec?.revision !== 5) {
  throw new Error("Gate 02 rev 5 must be ready_for_review.");
}

const assetIds = new Set(manifest.assets.map((asset) => asset.id));
const addAsset = ({ id, absolutePath, role, contentClass, sourceAssetIds, note, recipe }) => {
  if (assetIds.has(id)) throw new Error(`Asset already exists: ${id}`);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing asset: ${absolutePath}`);
  const asset = {
    id,
    stageId: "02-analysis",
    slot: "analysis-evidence",
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

const conclusionId = "slider-analysis-conclusion-review-r005";
const coreId = "slider-analysis-mechanism-sandbox-core-r005";
const screenshot = addAsset({
  id: "slider-analysis-workbench-browser-r005",
  absolutePath: path.join(here, "workbench-browser.png"),
  role: "validation",
  contentClass: "full-page-translated-axis-bilateral-rail-preview",
  sourceAssetIds: [conclusionId, coreId],
  note: "1440×2720 真实全页工作台；下片已滑开，固定上片、双轨和随下片移动的轴心可见。",
  recipe: "Chrome CDP desktop capture after desktop/mobile smoke checks"
});
const validation = addAsset({
  id: "slider-analysis-validation-r005",
  absolutePath: path.join(here, "validation-report.json"),
  role: "validation",
  contentClass: "corrected-kinematics-validation-report",
  sourceAssetIds: [screenshot.id, coreId],
  note: "汇总机构核心、pointer、opacity、移动端、modal、视频与 pipeline 验证。",
  recipe: "Focused validation summary"
});
const browserTests = addAsset({
  id: "slider-analysis-browser-tests-r005",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs"),
  role: "validation",
  contentClass: "desktop-mobile-pointer-opacity-modal-video-browser-tests",
  sourceAssetIds: [screenshot.id, coreId],
  note: "覆盖固定上片、活动下片、移动轴心、双轨、opacity、pointer、mobile、modal 和视频回归。",
  recipe: "Chrome DevTools Protocol browser smoke test"
});
const pipelineGuidance = addAsset({
  id: "slider-analysis-pipeline-guidance-r005",
  absolutePath: resolveRepoPath("skills/fidgeting-model-pipeline/references/pipeline-contract.md"),
  role: "contract",
  contentClass: "mechanical-transform-ownership-review-guidance",
  sourceAssetIds: [conclusionId, coreId],
  note: "机械 Gate 必须显式编码 fixed/moving/axis/rail 所有权，并围绕平移后轴心旋转。",
  recipe: "Repository model pipeline contract update"
});
const designBible = addAsset({
  id: "slider-analysis-design-bible-r005",
  absolutePath: resolveRepoPath("unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"),
  role: "contract",
  contentClass: "canonical-user-correction-record",
  sourceAssetIds: [conclusionId],
  note: "FDB-SLD-026 记录用户权威 reference-frame correction、DecisionState 与 DeliveryState。",
  recipe: "Canonical design decision update"
});
const implementationStatus = addAsset({
  id: "slider-analysis-implementation-status-r005",
  absolutePath: resolveRepoPath("unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"),
  role: "contract",
  contentClass: "delivery-state-and-validation-record",
  sourceAssetIds: [validation.id, screenshot.id],
  note: "记录测试、预览、未编辑 Blender/Unity、视觉批准待确认和未推送手机。",
  recipe: "Implementation status evidence update"
});
const registrar = addAsset({
  id: "slider-analysis-validation-registrar-r005",
  absolutePath: fileURLToPath(import.meta.url),
  role: "process",
  contentClass: "browser-validation-and-preview-registrar",
  sourceAssetIds: [validation.id, screenshot.id],
  note: "登记 rev 5 全量验证与真实全页预览。",
  recipe: "Revision-guarded validation evidence registration"
});
const newAssetIds = [
  screenshot.id,
  validation.id,
  browserTests.id,
  pipelineGuidance.id,
  designBible.id,
  implementationStatus.id,
  registrar.id
];
stage.artifactIds.push(...newAssetIds);
stage.validations.push({
  id: "browser-corrected-ownership-pointer-opacity-mobile-modal-video",
  status: "pass",
  evidence: "Fixed upper, moving lower/axis, bilateral rails, opacity, pointer slide/rotate, reset, 390x844, modal return and H.264 playback passed."
});
stage.analysisSpec.validationAssetIds = [validation.id, screenshot.id, browserTests.id];
stage.analysisSpec.previewPath = screenshot.path;
stage.analysisSpec.previewDimensions = { width: 1440, height: 2720 };
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map(
    (id) => manifest.assets.find((asset) => asset.id === id)?.sha256
  ).filter(Boolean).sort().join("\n"))
  .digest("hex");

manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev5-corrected-kinematics-review-pending";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-corrected-kinematics-validation-registered",
  modelId,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 5,
  artifactIds: newAssetIds,
  deterministicMechanismTests: "13/13-pass",
  workbenchTests: "28/28-pass",
  browserDesktopPointerOpacity: "pass",
  browserMobile390x844: "pass",
  modalReturn: "pass",
  videoPlayback: "pass",
  screenshot: { width: 1440, height: 2720, artifactId: screenshot.id },
  gateStatus: stage.status,
  visualApproval: "pending",
  phonePush: "not-started"
});

console.log(JSON.stringify({
  modelId,
  manifestRevision: manifest.revision,
  stageStatus: stage.status,
  previewPath: screenshot.path,
  previewDimensions: stage.analysisSpec.previewDimensions
}, null, 2));
