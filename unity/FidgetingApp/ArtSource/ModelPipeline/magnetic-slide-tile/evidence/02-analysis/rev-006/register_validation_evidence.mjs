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
const expectedRevision = 120;
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
if (stage.status !== "ready_for_review" || stage.analysisSpec?.revision !== 6) {
  throw new Error("Gate 02 rev 6 must be ready_for_review.");
}

const refreshIds = [
  "slider-analysis-cad-review-contract-r006",
  "slider-analysis-cad-core-r006",
  "slider-analysis-mechanism-core-r006",
  "slider-analysis-cad-tests-r006",
  "slider-analysis-mechanism-tests-r006",
  "slider-analysis-cad-ui-r006",
  "slider-analysis-cad-style-r006"
];
for (const id of refreshIds) {
  const asset = manifest.assets.find((candidate) => candidate.id === id);
  if (!asset) throw new Error(`Missing asset: ${id}`);
  const absolutePath = resolveRepoPath(asset.path);
  asset.sha256 = sha256File(absolutePath);
  asset.sizeBytes = fs.statSync(absolutePath).size;
  asset.exists = true;
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

const contractId = "slider-analysis-cad-review-contract-r006";
const screenshot = addAsset({
  id: "slider-analysis-workbench-browser-r006",
  absolutePath: path.join(here, "workbench-browser.png"),
  role: "validation",
  contentClass: "full-page-compound-cad-review-preview",
  sourceAssetIds: [contractId, "slider-analysis-cad-core-r006", "slider-analysis-mechanism-core-r006"],
  note: "1440×3281 全页工作台；+0.21L/36° 复合姿态、同步 CAD、未知尺寸和 2-DOF path trace 可见。",
  recipe: "Chrome CDP full-page capture after real desktop/mobile interaction tests"
});
const validation = addAsset({
  id: "slider-analysis-validation-r006",
  absolutePath: path.join(here, "validation-report.json"),
  role: "validation",
  contentClass: "compound-cad-browser-and-pipeline-validation-report",
  sourceAssetIds: [screenshot.id, contractId],
  note: "汇总故障根因、deterministic CAD/physics、真实 mouse/touch、参数、modal、视频和 pipeline 验证。",
  recipe: "Focused validation summary"
});
const browserTests = addAsset({
  id: "slider-analysis-browser-tests-r006",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs"),
  role: "validation",
  contentClass: "real-mouse-touch-compound-cad-browser-tests",
  sourceAssetIds: [screenshot.id, contractId],
  note: "真实坐标覆盖单次 2-DOF drag、ring、zoom/pan、键盘、mobile touch、参数派生、modal 和视频。",
  recipe: "Chrome DevTools Protocol browser smoke test"
});
const pipelineGuidance = addAsset({
  id: "slider-analysis-pipeline-guidance-r006",
  absolutePath: resolveRepoPath("skills/fidgeting-model-pipeline/references/pipeline-contract.md"),
  role: "contract",
  contentClass: "vector-cad-and-honest-dimension-review-guidance",
  sourceAssetIds: [contractId],
  note: "机械 Gate 强制同步矢量工程图、真实 pointer、dimension status 和 unknown-safe derivation。",
  recipe: "Repository pipeline contract update"
});
const workbenchGuidance = addAsset({
  id: "slider-analysis-workbench-guidance-r006",
  absolutePath: resolveRepoPath("tools/model-provenance-explorer/pipeline-contract.mjs"),
  role: "contract",
  contentClass: "workbench-cad-review-guidance",
  sourceAssetIds: [pipelineGuidance.id],
  note: "工作台 Gate 02 描述同步 CAD、zoom/pan、键盘和尺寸证据状态。",
  recipe: "Workbench stage contract update"
});
const designBible = addAsset({
  id: "slider-analysis-design-bible-r006",
  absolutePath: resolveRepoPath("unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"),
  role: "contract",
  contentClass: "canonical-rev6-and-compound-correction-record",
  sourceAssetIds: [contractId],
  note: "FDB-SLD-027/028 记录旋转故障、CAD 要求和 simultaneous 2-DOF 用户修正。",
  recipe: "Canonical design decision update"
});
const implementation = addAsset({
  id: "slider-analysis-implementation-status-r006",
  absolutePath: resolveRepoPath("unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"),
  role: "contract",
  contentClass: "delivery-state-and-validation-record",
  sourceAssetIds: [validation.id, screenshot.id],
  note: "记录 rev 6 测试、预览、待批准和未运行 Blender/Unity/build/install/phone。",
  recipe: "Implementation status evidence update"
});
const registrar = addAsset({
  id: "slider-analysis-validation-registrar-r006",
  absolutePath: fileURLToPath(import.meta.url),
  role: "process",
  contentClass: "compound-cad-validation-registrar",
  sourceAssetIds: [validation.id, screenshot.id],
  note: "登记 rev 6 全量验证并同步已注册源码哈希。",
  recipe: "Revision-guarded validation registration"
});
const newAssetIds = [
  screenshot.id,
  validation.id,
  browserTests.id,
  pipelineGuidance.id,
  workbenchGuidance.id,
  designBible.id,
  implementation.id,
  registrar.id
];
stage.artifactIds.push(...newAssetIds);
stage.validations.push({
  id: "real-mouse-touch-compound-cad-regressions",
  status: "pass",
  evidence: "One desktop and mobile body drag changes s+theta; ring works after slide/zoom/pan; keyboard, reset, dimensions, modal and video pass."
});
stage.analysisSpec.validationAssetIds = [validation.id, screenshot.id, browserTests.id];
stage.analysisSpec.previewPath = screenshot.path;
stage.analysisSpec.previewDimensions = { width: 1440, height: 3281 };
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map(
    (id) => manifest.assets.find((asset) => asset.id === id)?.sha256
  ).filter(Boolean).sort().join("\n"))
  .digest("hex");

manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev6-compound-cad-review-pending";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-compound-cad-validation-registered",
  modelId,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 6,
  artifactIds: newAssetIds,
  deterministicCadMechanismTests: "27/27-pass",
  fullNodeTests: "42/42-pass",
  realDesktopCompoundPointer: "pass",
  realDesktopRingAfterSlideZoomPan: "pass",
  mobileTouchCompoundAndRing: "pass",
  keyboardDetentsAndReverse: "pass",
  dimensionUnknownAndDerivedStates: "pass",
  modalReturn: "pass",
  videoPlayback: "pass",
  screenshot: { width: 1440, height: 3281, artifactId: screenshot.id },
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
