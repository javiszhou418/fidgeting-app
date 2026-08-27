import {
  createMechanismSandbox
} from "./mechanism-sandbox-core.mjs";
import {
  PHYSICAL_FIELDS,
  cadConfigFromEvidenceContract,
  cadViewportTransform,
  computeCadGeometry,
  computeCadSweepEnvelope,
  computeMinimumOverlapContainmentSweep,
  createCadViewport,
  derivePhysicalDimensions,
  displayDimension,
  inverseCadPoint,
  topLocalPointFromWorld,
  topWorldPointFromLocal,
  panCadViewport,
  refreshCadTravelBounds,
  solveCompoundDragDelta,
  zoomCadViewport
} from "./mechanism-cad-core.mjs";
import {
  MANUFACTURING_LATER_FIELDS,
  OPTIONAL_ENGINEERING_MEASUREMENTS,
  REQUIRED_CORE_MEASUREMENTS,
  validateMeasurementContract
} from "./measurement-contract-core.mjs";
import {
  WORKSPACE_TABS,
  buildWorkspaceRoute,
  parseWorkspaceRoute,
  resolveWorkspaceLocation,
  stageForTab,
  tabForStage,
  workspaceTabStatus
} from "./workspace-navigation-core.mjs";

const state = {
  models: [],
  manifest: null,
  modelingContract: null,
  history: [],
  activeModelId: null,
  activeStageId: null,
  activeTabId: null,
  activeAsset: null,
  annotationRegion: null,
  annotationEnabled: false,
  viewerCleanup: null,
  sandboxCleanup: null,
  mechanismEvidenceContract: null,
  mechanismSimulatorConfig: null,
  workspaceMemory: null
};
const assetDialogHistoryKey = "fidgetingAssetDialog";
const workspaceMemoryPrefix = "fidgeting-model-workspace-v2";

const els = {
  currentModelTitle: document.getElementById("current-model-title"),
  modelNav: document.getElementById("model-nav"),
  stageRail: document.getElementById("stage-rail"),
  taskBanner: document.getElementById("current-task-banner"),
  workspaceTabs: document.getElementById("workspace-tabs"),
  stageDetail: document.getElementById("stage-detail"),
  dialog: document.getElementById("asset-dialog"),
  dialogSlot: document.getElementById("dialog-slot"),
  dialogTitle: document.getElementById("dialog-title"),
  dialogPath: document.getElementById("dialog-path"),
  dialogClose: document.getElementById("dialog-close"),
  assetStage: document.getElementById("asset-stage"),
  annotateButton: document.getElementById("annotate-button"),
  openFile: document.getElementById("open-file"),
  copyPath: document.getElementById("copy-path"),
  issueForm: document.getElementById("issue-form"),
  issueNote: document.getElementById("issue-note"),
  issueSeverity: document.getElementById("issue-severity"),
  issueClaim: document.getElementById("issue-claim"),
  selectionPreview: document.getElementById("selection-preview"),
  toast: document.getElementById("toast")
};

const statusLabels = {
  missing: "缺失",
  blocked: "被上游阻断",
  draft: "待审批",
  ready_for_review: "可审批",
  approved: "已批准",
  rejected: "已拒绝",
  stale: "已过期",
  legacy: "历史未验证"
};

const originLabels = {
  "user-provided": "用户提供",
  "assistant-generated": "助手生成 · 非用户原图",
  external: "外部来源",
  "repository-generated": "仓库生成",
  "unknown-legacy": "历史来源不明"
};

const assetSlotLabels = {
  "original-reference": "原始参考",
  "external-reference": "外部参考",
  "ai-target": "AI 目标图",
  "discovery-log": "搜索记录",
  "analysis-board-source": "分析板（SVG）",
  "analysis-board": "分析板",
  "analysis-evidence": "分析素材",
  "modeling-contract": "建模规格",
  "part-tree": "零件树",
  "exploded-plan": "爆炸规划",
  "blockout-source": "白模源文件",
  "blockout-hero": "白模 Hero",
  "white-model-source": "白模源文件",
  "white-model-hero": "白模 Hero",
  "white-model-support": "辅助姿态",
  "pivot-axis-review": "轴心对照",
  "view-front": "正视",
  "view-back": "背视",
  "view-top": "顶视",
  "view-bottom": "底视",
  "view-left": "左视",
  "view-right": "右视",
  "workbench": "Workbench",
  "dimension-overlay": "尺寸覆盖",
  "pivot-overlay": "轴心覆盖",
  "exploded-geometry": "爆炸几何",
  "material-variant-board": "材质工艺／方案板",
  "material-comparison": "血红来源对比",
  "material-front": "中性正面血红",
  "material-second-light": "第二测试灯晶体响应",
  "material-side-reflection": "侧面直接迎光反射",
  "material-open-artwork": "打开状态下片图案",
  "material-process-board": "可替换图案层流程板",
  "material-board": "中性 PBR 材质板",
  "material-closeup": "材质近景",
  "round-edge-location": "先看检查位置",
  "round-edge-comparison": "再看放大对比",
  "round-edge-wireframe": "最后看圆边细分",
  "parity-review-board": "Blender 与 Unity 总对比",
  "geometry-comparison": "外形差异",
  "artwork-comparison": "图案差异",
  "material-parity-comparison": "材质与反光差异",
  "shipping-review-board": "正式场景多角度",
  "shipping-motion-board": "滑开与旋转姿态",
  "shipping-phone": "手机构图",
  "blender-neutral": "Blender 中性图",
  "unity-neutral": "Unity 中性图",
  "parity-report": "对齐报告",
  "parity-overlay": "轮廓叠加",
  "contact-sheet": "对照总览",
  "export-manifest": "导出清单"
};

const workflowPhases = [
  { id: "interaction", label: "参考 + 交互形式", stageIds: ["01-intake", "02-analysis", "03-contract", "04-architecture"] },
  { id: "blender", label: "Blender 建模 + 贴图", stageIds: ["05-blockout", "06-geometry", "07-material", "08-lighting", "09-environment", "10-export"] },
  { id: "unity", label: "Unity + 场景 + 渲染", stageIds: ["11-unity-parity", "12-shipping"] }
];

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function repoUrl(repoPath) {
  return encodeURI(`/repo/${repoPath}`);
}

function extension(repoPath) {
  return repoPath.split(".").pop().toLowerCase();
}

function isImage(asset) {
  return ["png", "jpg", "jpeg", "webp", "gif", "bmp", "tif", "tiff", "svg"].includes(extension(asset.path));
}

function isVideo(asset) {
  return ["mov", "mp4", "m4v", "webm"].includes(extension(asset.path));
}

function showToast(message) {
  els.toast.textContent = message;
  els.toast.classList.add("is-visible");
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => els.toast.classList.remove("is-visible"), 2400);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    ...options,
    headers: { "content-type": "application/json", ...(options.headers || {}) }
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const detail = Array.isArray(payload.details) && payload.details.length ? ` ${payload.details.join(" ")}` : "";
    throw new Error(`${payload.error || `HTTP ${response.status}`}${detail}`);
  }
  return payload;
}

function currentStage() {
  return state.manifest?.stages.find((stage) => stage.id === state.activeStageId) || state.manifest?.stages[0];
}

function currentStageAssets() {
  return state.manifest.assets.filter((asset) => asset.stageId === state.activeStageId);
}

function currentStageIssues() {
  return (state.manifest.issues || []).filter((issue) => issue.stageId === state.activeStageId && issue.status !== "resolved");
}

function workspaceMemoryKey(modelId = state.activeModelId) {
  return `${workspaceMemoryPrefix}:${modelId}`;
}

function readWorkspaceMemory(modelId) {
  try { return JSON.parse(localStorage.getItem(workspaceMemoryKey(modelId)) || "{}"); }
  catch { return {}; }
}

function writeWorkspaceMemory(patch = {}) {
  if (!state.activeModelId) return;
  state.workspaceMemory = {
    ...(state.workspaceMemory || {}),
    tabId: state.activeTabId,
    stageId: state.activeStageId,
    ...patch
  };
  localStorage.setItem(workspaceMemoryKey(), JSON.stringify(state.workspaceMemory));
}

function replaceWorkspaceRoute({ assetId = state.activeAsset?.id || null } = {}) {
  if (!state.activeModelId || !state.activeStageId || !state.activeTabId) return;
  const url = `${location.pathname}${buildWorkspaceRoute({
    modelId: state.activeModelId,
    tabId: state.activeTabId,
    stageId: state.activeStageId,
    assetId
  })}`;
  history.replaceState({
    ...(history.state || {}),
    modelId: state.activeModelId,
    tabId: state.activeTabId,
    stageId: state.activeStageId,
    assetId
  }, "", url);
}

function pushWorkspaceRoute({ assetId = null } = {}) {
  const url = `${location.pathname}${buildWorkspaceRoute({
    modelId: state.activeModelId,
    tabId: state.activeTabId,
    stageId: state.activeStageId,
    assetId
  })}`;
  history.pushState({
    modelId: state.activeModelId,
    tabId: state.activeTabId,
    stageId: state.activeStageId,
    assetId,
    ...(assetId ? { [assetDialogHistoryKey]: true } : {})
  }, "", url);
}

function restoreWorkspaceView() {
  const memory = state.workspaceMemory || {};
  requestAnimationFrame(() => {
    const subview = state.activeTabId === "cad" ? "cad"
      : state.activeTabId === "analysis" ? "references"
        : memory.subview;
    if (subview) document.querySelector(`[data-review-tab="${CSS.escape(subview)}"]`)?.click();
    window.scrollTo({ top: Number(memory.scrollY) || 0, behavior: "instant" });
  });
}

function isSimpleArchitectureReview() {
  if (state.manifest?.model.id !== "magnetic-slide-tile" || state.activeStageId !== "04-architecture") return false;
  const stage = state.manifest.stages.find((candidate) => candidate.id === "04-architecture");
  return ["exact-source-questions-only", "motion-evidence-mapping", "concealed-circular-overlap"].includes(stage?.architectureSpec?.reviewMode);
}

function isPlainGate10Review() {
  return state.manifest?.model.id === "magnetic-slide-tile" && state.activeStageId === "10-export";
}

function isPlainGate11Review() {
  return state.manifest?.model.id === "magnetic-slide-tile"
    && ["11-unity-parity", "12-shipping"].includes(state.activeStageId);
}

async function loadModels() {
  const payload = await api("/api/models");
  state.models = payload.models;
  const route = parseWorkspaceRoute(location.search);
  const preferred = localStorage.getItem("fidgeting-model-pipeline-selected");
  state.activeModelId = state.models.some((model) => model.id === route.modelId)
    ? route.modelId
    : state.models.some((model) => model.id === preferred) ? preferred : state.models[0]?.id;
  await migrateLegacyDecisions();
  await loadModel(state.activeModelId);
}

async function migrateLegacyDecisions() {
  if (localStorage.getItem("fidgeting-model-provenance-decisions-v1-migrated") === "true") return;
  let legacy = {};
  try { legacy = JSON.parse(localStorage.getItem("fidgeting-model-provenance-decisions-v1") || "{}"); }
  catch { legacy = {}; }
  for (const model of state.models) {
    const old = legacy[model.id];
    if (!old || (!old.decision && !old.notes)) continue;
    try {
      const manifest = await api(`/api/models/${model.id}`);
      await api(`/api/models/${model.id}/legacy-decision`, {
        method: "POST",
        body: JSON.stringify({ expectedRevision: manifest.revision, decision: old.decision, notes: old.notes })
      });
    } catch (error) {
      console.warn("Legacy decision migration skipped", model.id, error);
    }
  }
  localStorage.setItem("fidgeting-model-provenance-decisions-v1-migrated", "true");
}

async function loadModel(modelId, preserveStage = false) {
  state.activeModelId = modelId;
  localStorage.setItem("fidgeting-model-pipeline-selected", modelId);
  const [manifest, history, contractPayload] = await Promise.all([
    api(`/api/models/${modelId}`),
    api(`/api/models/${modelId}/history`),
    api(`/api/models/${modelId}/contract`)
  ]);
  state.manifest = manifest;
  state.history = history.events;
  state.modelingContract = contractPayload.contract;
  const analysisStage = manifest.stages.find((stage) => stage.id === "02-analysis");
  const mechanismContractAsset = manifest.assets.find(
    (asset) => asset.id === analysisStage?.analysisSpec?.contractAssetId
  );
  state.mechanismEvidenceContract = mechanismContractAsset
    ? await fetch(repoUrl(mechanismContractAsset.path)).then((response) => {
      if (!response.ok) throw new Error(`Mechanism evidence contract HTTP ${response.status}`);
      return response.json();
    })
    : null;
  const simulatorConfigAsset = manifest.assets.find(
    (asset) => asset.id === analysisStage?.analysisSpec?.geometryConfigAssetId
  ) || manifest.assets.find((asset) => asset.id === "slider-analysis-interactive-cad-geometry-config-r015");
  state.mechanismSimulatorConfig = simulatorConfigAsset
    ? await fetch(repoUrl(simulatorConfigAsset.path)).then((response) => {
      if (!response.ok) throw new Error(`Mechanism simulator config HTTP ${response.status}`);
      return response.json();
    })
    : null;
  const route = parseWorkspaceRoute(location.search);
  const routeForModel = route.modelId === modelId ? route : {};
  state.workspaceMemory = readWorkspaceMemory(modelId);
  const resolved = preserveStage && state.manifest.stages.some((stage) => stage.id === state.activeStageId)
    ? {
        stageId: state.activeStageId,
        tabId: state.activeTabId || tabForStage(state.activeStageId),
        assetId: state.activeAsset?.id || null,
        scrollY: window.scrollY,
        subview: state.workspaceMemory.subview,
        viewerView: state.workspaceMemory.viewerView
      }
    : resolveWorkspaceLocation({ route: routeForModel, memory: state.workspaceMemory, manifest: state.manifest });
  state.activeStageId = resolved.stageId;
  state.activeTabId = resolved.tabId;
  state.workspaceMemory = { ...state.workspaceMemory, ...resolved };
  render();
  writeWorkspaceMemory({ assetId: resolved.assetId || null });
  replaceWorkspaceRoute({ assetId: resolved.assetId || null });
  restoreWorkspaceView();
  if (resolved.assetId && state.manifest.assets.some((asset) => asset.id === resolved.assetId)) {
    openAsset(resolved.assetId, { pushHistory: false });
  }
}

function modelDisplayName(name) {
  return String(name || "").replace(/\s*·?\s*重建候选$/u, "");
}

function renderNav() {
  els.modelNav.innerHTML = state.models.map((model) => `
    <button type="button" class="model-button ${model.id === state.activeModelId ? "is-active" : ""}" data-model-id="${escapeHtml(model.id)}">
      <span class="model-dot"></span>
      <span class="model-copy"><strong>${escapeHtml(modelDisplayName(model.name))}</strong></span>
    </button>
  `).join("");
  els.modelNav.querySelectorAll("[data-model-id]").forEach((button) => {
    button.addEventListener("click", () => {
      writeWorkspaceMemory({ scrollY: window.scrollY });
      loadModel(button.dataset.modelId).catch(showFatal);
    });
  });
}

const workspaceTabStatusLabels = {
  current: "当前",
  approved: "已批准",
  stale: "过期",
  rejected: "被退回",
  pending: "未开始",
  unstarted: "未开始"
};

function selectWorkspace({ tabId, stageId, pushHistory = true }) {
  state.activeTabId = tabId || tabForStage(stageId);
  state.activeStageId = stageId || stageForTab(state.activeTabId, state.manifest);
  const subview = state.activeTabId === "cad" ? "cad"
    : state.activeTabId === "analysis" ? "references"
      : state.workspaceMemory?.subview;
  writeWorkspaceMemory({ assetId: null, scrollY: 0, subview });
  if (pushHistory) pushWorkspaceRoute();
  render();
  restoreWorkspaceView();
  window.scrollTo({ top: 0, behavior: "instant" });
}

function renderTaskBanner() {
  const workflowStage = state.manifest.stages.find((stage) => stage.id === state.manifest.currentStageId)
    || state.manifest.stages.find((stage) => stage.status !== "approved")
    || state.manifest.stages.at(-1);
  const workflowIndex = state.manifest.stages.indexOf(workflowStage) + 1;
  const reason = state.manifest.currentState?.diagnosis
    || workflowStage.readiness?.note
    || workflowStage.staleReason
    || "当前任务由模型 pipeline 状态决定；历史证据始终保留可查。";
  els.taskBanner.innerHTML = `
    <div>
      <span>当前正在做什么</span>
      <strong>${escapeHtml(state.manifest.model.name)} · Gate ${String(workflowIndex).padStart(2, "0")} · ${escapeHtml(workflowStage.contract.title)}</strong>
    </div>
    <p>${escapeHtml(reason)}</p>
  `;
}

function renderWorkspaceTabs() {
  els.workspaceTabs.innerHTML = WORKSPACE_TABS.map((tab) => {
    const status = workspaceTabStatus(tab, state.manifest);
    return `
      <button type="button" class="workspace-tab ${tab.id === state.activeTabId ? "is-active" : ""}" data-workspace-tab="${tab.id}" data-status="${status}">
        <strong>${escapeHtml(tab.label)}</strong>
        <span>${workspaceTabStatusLabels[status]}</span>
      </button>
    `;
  }).join("");
  els.workspaceTabs.querySelectorAll("[data-workspace-tab]").forEach((button) => {
    button.addEventListener("click", () => selectWorkspace({ tabId: button.dataset.workspaceTab }));
  });
}

function renderStageRail() {
  if (state.manifest.stages.length !== 12) throw new Error(`Canonical pipeline requires 12 gates, got ${state.manifest.stages.length}.`);
  const workflowStage = state.manifest.stages.find((stage) => stage.id === state.manifest.currentStageId)
    || (state.manifest.derived.earliestProblem?.stageId
      ? state.manifest.stages.find((stage) => stage.id === state.manifest.derived.earliestProblem.stageId)
      : state.manifest.stages.at(-1));
  const workflowIndex = state.manifest.stages.indexOf(workflowStage) + 1;
  const approvedCount = state.manifest.stages.filter((stage) => stage.status === "approved").length;
  const phases = workflowPhases.map((phase) => {
    const stages = phase.stageIds.map((stageId) => state.manifest.stages.find((stage) => stage.id === stageId));
    const active = phase.stageIds.includes(state.activeStageId);
    const complete = stages.every((stage) => stage.status === "approved");
    return `
    <button type="button" class="phase-button ${active ? "is-active" : ""}" data-phase-id="${phase.id}" data-status="${complete ? "approved" : active ? "current" : "pending"}">
      <strong>${escapeHtml(phase.label)}</strong>
    </button>
  `;
  }).join("");
  const roadmap = state.manifest.stages.map((stage, index) => `
    <button type="button" class="gate-roadmap-item ${stage.id === workflowStage.id ? "is-workflow-current" : ""} ${stage.id === state.activeStageId ? "is-viewed" : ""}" data-stage-id="${stage.id}" data-status="${stage.status}">
      <span>Gate ${String(index + 1).padStart(2, "0")}</span>
      <strong>${escapeHtml(stage.contract.title)}</strong>
      <small>${escapeHtml(statusLabels[stage.status] || stage.status)}</small>
    </button>
  `).join("");
  els.stageRail.innerHTML = `
    <div class="canonical-progress" data-total-gates="12" data-current-gate="${workflowIndex}" data-approved-count="${approvedCount}">
      <div><span>当前流程</span><strong>当前 Gate ${String(workflowIndex).padStart(2, "0")} / 12</strong></div>
      <div><span>批准进度</span><strong>已批准 ${approvedCount} / 12</strong></div>
      <p>12 个 Gate 固定不变，归为 3 个易懂阶段。历史中的 9/12、6/12 是当时已批准数量，不是总步骤变化。</p>
    </div>
    <div class="phase-grouping" aria-label="12 个 Gate 的 3 个阶段分组">${phases}</div>
    <details class="gate-roadmap" open>
      <summary>展开稳定的 12-Gate 路线图</summary>
      <div class="gate-roadmap-grid">${roadmap}</div>
    </details>
  `;
  els.stageRail.querySelectorAll("[data-phase-id]").forEach((button) => {
    button.addEventListener("click", () => {
      const phase = workflowPhases.find((candidate) => candidate.id === button.dataset.phaseId);
      const stages = phase.stageIds.map((stageId) => state.manifest.stages.find((stage) => stage.id === stageId));
      const target = stages.find((stage) => stage.id === state.manifest.currentStageId)
        || stages.find((stage) => stage.status !== "approved")
        || stages.at(-1);
      selectWorkspace({ tabId: tabForStage(target.id), stageId: target.id });
    });
  });
  els.stageRail.querySelectorAll("[data-stage-id]").forEach((button) => {
    button.addEventListener("click", () => selectWorkspace({ stageId: button.dataset.stageId }));
  });
}

function assetCard(asset) {
  const stageIndex = state.manifest.stages.findIndex((stage) => stage.id === asset.stageId);
  const previousStage = stageIndex > 0 ? state.manifest.stages[stageIndex - 1] : null;
  const previousIds = new Set(previousStage?.artifactIds || []);
  const hasDirectUpstream = !previousStage || asset.sourceAssetIds.some((id) => previousIds.has(id));
  const origin = asset.provenance?.origin;
  const originChip = origin && origin !== "repository-generated"
    ? `<span class="origin-chip" data-origin="${escapeHtml(origin)}">${escapeHtml(originLabels[origin] || origin)}</span>`
    : !origin ? '<span class="origin-chip" data-origin="unknown-legacy">来源未登记</span>' : "";
  const lineageChip = previousStage && !hasDirectUpstream
    ? `<span class="lineage-chip">未直接承接 ${escapeHtml(previousStage.id)}</span>`
    : "";
  const preview = isImage(asset)
    ? `<div class="asset-thumb"><img src="${repoUrl(asset.path)}" alt="${escapeHtml(asset.slot)}" loading="eager" decoding="async"></div>`
    : `<div class="file-thumb">${escapeHtml(extension(asset.path).toUpperCase())}</div>`;
  return `
    <button type="button" class="asset-card" data-asset-id="${escapeHtml(asset.id)}">
      ${preview}
      <span class="asset-info">
        <span class="asset-chips"><span class="asset-slot">${escapeHtml(assetSlotLabels[asset.slot] || asset.slot)}</span>${originChip}${lineageChip}</span>
        <strong>${escapeHtml(assetSlotLabels[asset.slot] || asset.id)}</strong>
      </span>
    </button>
  `;
}

function referenceDiscoveryPanel(stage) {
  const discovery = state.manifest.referenceDiscovery;
  if (!discovery || !["01-intake", "02-analysis"].includes(stage.id)) return "";
  const keywords = discovery.keywords.map((entry) => `<span class="keyword-chip" title="${escapeHtml(entry.kind)}">${escapeHtml(entry.term)}</span>`).join("");
  const queries = discovery.queries.map((entry) => `<li><code>${escapeHtml(entry.query)}</code><span>${escapeHtml(entry.language)} · ${escapeHtml(entry.status)}</span></li>`).join("");
  const candidates = discovery.candidates.map((candidate) => `
    <article class="discovery-candidate">
      <div><strong>${escapeHtml(candidate.title)}</strong><span>${escapeHtml(candidate.studio || "外部候选")} · ${escapeHtml(candidate.matchStatus)}</span></div>
      <p>${escapeHtml(candidate.rationale)}</p>
      ${(candidate.conflicts || []).length ? `<ul>${candidate.conflicts.map((conflict) => `<li>${escapeHtml(conflict)}</li>`).join("")}</ul>` : ""}
      <a href="${escapeHtml(candidate.url)}" target="_blank" rel="noreferrer">查看外部候选来源</a>
    </article>
  `).join("");
  const content = `
    <p class="discovery-guardrail">${escapeHtml(discovery.guardrail)}</p>
    <div class="keyword-list">${keywords}</div>
    <div class="discovery-grid">
      <div><h4>搜索记录</h4><ol class="query-list">${queries}</ol></div>
      <div><h4>同款 / 结构候选</h4><div class="candidate-list">${candidates || '<div class="empty">尚无候选</div>'}</div></div>
    </div>
  `;
  if (stage.id === "02-analysis") {
    return `
      <details class="discovery-panel discovery-panel--compact">
        <summary class="discovery-summary">
          <span><strong>外部检索索引</strong><small>搜索记录 · 默认收起，不重复展示第一关素材</small></span>
          <span class="discovery-summary-meta">${discovery.queries.length} 次搜索 · ${discovery.candidates.length} 个候选 · ${escapeHtml(discovery.status)}</span>
        </summary>
        <div class="discovery-compact-body">${content}</div>
      </details>
    `;
  }
  return `
    <section class="discovery-panel">
      <div class="panel-heading"><h3>关键词与外部参考探索</h3><span>${escapeHtml(discovery.status)}</span></div>
      ${content}
    </section>
  `;
}

function userFacingStageAssets(stage, assets) {
  if (["02-analysis", "04-architecture"].includes(stage.id)) return [];
  const internalExtensions = new Set(["json", "md", "ndjson", "txt"]);
  const currentArtifactIds = new Set(stage.reviewArtifactIds?.length ? stage.reviewArtifactIds : (stage.artifactIds || []));
  const currentRevisionAssets = currentArtifactIds.size
    ? assets.filter((asset) => currentArtifactIds.has(asset.id))
    : assets;
  if (stage.id === "05-blockout") {
    const blockoutSlots = new Set([
      "interactive-model", "blockout-hero", "blockout-closed", "blockout-slide",
      "blockout-spin", "blockout-compound", "blockout-underside",
      "blockout-mechanism-closeup", "blockout-exploded", "pivot-overlay",
      "white-model-hero", "white-model-support", "pivot-axis-review"
    ]);
    return currentRevisionAssets.filter((asset) => blockoutSlots.has(asset.slot));
  }
  if (stage.id === "06-geometry") {
    const userReview = currentRevisionAssets.filter((asset) => asset.slot === "geometry-user-review");
    if (userReview.length) return userReview;
    const geometrySlots = new Set([
      "view-front", "view-back", "view-top", "view-bottom", "view-left", "view-right",
      "workbench", "dimension-overlay", "pivot-overlay", "exploded-geometry"
    ]);
    return currentRevisionAssets.filter((asset) => geometrySlots.has(asset.slot));
  }
  if (stage.id === "07-material" && stage.materialRebuildSpec?.revision === 10) {
    return (stage.reviewArtifactIds || [])
      .map((assetId) => assets.find((asset) => asset.id === assetId))
      .filter(Boolean);
  }
  if (stage.id === "07-material") return currentRevisionAssets.filter((asset) => [
    "source-normalized-crop",
    "blender-normalized-crop",
    "unity-normalized-crop",
    "material-comparison",
    "material-variant-board",
    "material-front",
    "material-board",
    "material-closeup",
    "material-second-light",
    "material-side-reflection",
    "material-open-artwork",
    "material-process-board"
  ].includes(asset.slot));
  return currentRevisionAssets.filter((asset) => !internalExtensions.has(extension(asset.path)));
}

function historicalStageAssets(stage, assets) {
  const currentIds = new Set(stage.artifactIds || []);
  const inspectable = new Set(["png", "jpg", "jpeg", "webp", "gif", "svg", "mov", "mp4", "m4v", "webm", "glb"]);
  return assets.filter((asset) => !currentIds.has(asset.id) && inspectable.has(extension(asset.path)));
}

function architectureActionPanel() {
  if (state.manifest.model.id !== "magnetic-slide-tile") {
    return `<section class="task-heading"><h2>确认零件树与爆炸方案</h2></section>`;
  }
  const architectureStage = state.manifest.stages.find((stage) => stage.id === "04-architecture");
  const concealedOverlap = architectureStage?.architectureSpec?.reviewMode === "concealed-circular-overlap";
  if (concealedOverlap) {
    const reviewItems = [
      ["magnetic-slide-tile-flat-lower-plane-r010", "外露下层 vs 圆端内部区", "绿色是可见干净平面；蓝色虚线只表示隐藏机构所在区域"],
      ["magnetic-slide-tile-concealed-circular-interface-r010", "隐藏圆形接口与运动", "同一个上件经隐藏接口平移、旋转；内部路径不补画"]
    ];
    const reviewCards = reviewItems.map(([assetId, title, note]) => {
      const asset = state.manifest.assets.find((candidate) => candidate.id === assetId);
      if (!asset) return "";
      return `
        <figure class="mapping-board">
          <button type="button" data-asset-id="${escapeHtml(asset.id)}" aria-label="放大查看${escapeHtml(title)}">
            <object data="${repoUrl(asset.path)}" type="image/svg+xml" tabindex="-1" aria-hidden="true"></object>
          </button>
          <figcaption><strong>${escapeHtml(title)}</strong><span>${escapeHtml(note)}</span></figcaption>
        </figure>
      `;
    }).join("");
    return `
      <section class="simple-review mapping-review concealed-review">
        <header class="simple-task-header">
          <span>这次只确认两件事</span>
          <h2>外露平面和隐藏圆形区，是否标对？</h2>
          <p>实线只描可见外观；蓝色虚线只是隐藏机构的位置范围，不是轨道形状。</p>
        </header>
        <div class="mapping-summary" aria-label="修正后的结构">
          <article><span class="mapping-swatch is-fixed"></span><div><strong>外露下层</strong><p>干净平面，没有外露滑轨或承载轨道代理。</p></div></article>
          <article><span class="mapping-swatch is-hidden"></span><div><strong>隐藏机构</strong><p>全部轨道与内部机制封闭在圆形重叠区。</p></div></article>
          <article><span class="mapping-swatch is-moving"></span><div><strong>上层运动</strong><p>同一个上件通过隐藏接口平移并旋转。</p></div></article>
        </div>
        <div class="mapping-board-grid">${reviewCards}</div>
        <section class="mapping-confirmation">
          <span>请确认</span>
          <p>绿色是否正确表示无外露滑轨的干净下层平面；蓝色虚线是否只圈出全部机构所在的圆形重叠区？</p>
        </section>
        <section class="next-gate-requirement">
          <strong>下一版白模必须改正</strong>
          <p>胶囊边缘须使用高分辨率圆角曲线，并在真实渲染中无锯齿、无分面；本轮不会重建。</p>
        </section>
        <details class="technical-details">
          <summary>技术细节</summary>
          <div class="technical-details-body">
            <p><strong>状态：</strong>Gate 05 rev 1 已拒绝并保留；Gate 04 rev 8 的“暴露轨道承载区”批准已失效。</p>
            <p><strong>直接证据：</strong>用户视频中的可见下层面、滑开后的圆端区，以及 HALOOPLAYER 同款拆开图。</p>
            <p><strong>仍未知：</strong>隐藏轨道路径、耦合、孔深、数量、公差、球簧紧固方式和遮挡几何。</p>
            <p><strong>门禁：</strong>本次结构获批前，不得重建 Gate 05。</p>
          </div>
        </details>
      </section>
    `;
  }
  const evidenceMapping = architectureStage?.architectureSpec?.reviewMode === "motion-evidence-mapping";
  if (evidenceMapping) {
    const reviewItems = [
      ["magnetic-slide-tile-fixed-body-boundary-r008", "固定主体边界", "绿色范围相对手指不动；遮挡处用虚线停止"],
      ["magnetic-slide-tile-slider-travel-sequence-r008", "直线滑动顺序", "42.00–43.50 秒连续帧：上盖沿长轴覆盖固定承载区"],
      ["magnetic-slide-tile-rotating-body-pivot-r008", "旋转件与轴心", "66.00–67.25 秒连续帧：同一上盖绕中央接口转动"],
      ["magnetic-slide-tile-visible-holes-slots-r008", "孔、槽与接触区", "只描可见边缘；H / S / P / C 编号不代表隐藏数量"]
    ];
    const reviewCards = reviewItems.map(([assetId, title, note]) => {
      const asset = state.manifest.assets.find((candidate) => candidate.id === assetId);
      if (!asset) return "";
      return `
        <figure class="mapping-board">
          <button type="button" data-asset-id="${escapeHtml(asset.id)}" aria-label="放大查看${escapeHtml(title)}">
            <object data="${repoUrl(asset.path)}" type="image/svg+xml" tabindex="-1" aria-hidden="true"></object>
          </button>
          <figcaption><strong>${escapeHtml(title)}</strong><span>${escapeHtml(note)}</span></figcaption>
        </figure>
      `;
    }).join("");
    return `
      <section class="simple-review mapping-review">
        <header class="simple-task-header">
          <span>现在只需要确认这份标注</span>
          <h2>固定主体和运动件，是否标对？</h2>
          <p>绿色是相对固定，橙色是运动，黄色是中央接口候选。点图可放大。</p>
        </header>
        <div class="mapping-summary" aria-label="当前运动映射">
          <article><span class="mapping-swatch is-fixed"></span><div><strong>相对固定</strong><p>手里握住的下层主体，以及露出的轨道承载区。</p></div></article>
          <article><span class="mapping-swatch is-moving"></span><div><strong>直线滑动</strong><p>上层装饰胶囊整件沿长轴移动；A/B 两个槽板都可运动。</p></div></article>
          <article><span class="mapping-swatch is-pivot"></span><div><strong>旋转</strong><p>同一个上层装饰胶囊绕中央接口转动。</p></div></article>
        </div>
        <div class="mapping-board-grid">${reviewCards}</div>
        <section class="mapping-confirmation">
          <span>请确认</span>
          <p>绿色固定边界、橙色滑动／旋转边界，以及 P1/P2、H、S、C 的描线是否正确？若有一处不对，只需告诉我编号或边界位置。</p>
        </section>
        <details class="technical-details">
          <summary>技术细节</summary>
          <div class="technical-details-body">
            <p><strong>完整关卡状态：</strong>01–03 已批准；04 等待本次确认；05–12 未开始。</p>
            <p><strong>直接证据：</strong>用户原始 MOV 42.00–43.50 秒和 66.00–67.25 秒连续帧；HALOOPLAYER 官方图 07；NXEDC 打开轨道图。</p>
            <p><strong>用户纠正：</strong>A/B 均可运动，不再把任一个当成永久固定件。</p>
            <p><strong>仍未知：</strong>A/B 中哪一件隐藏连接旋转上盖；遮挡后的边界、孔深、公差、隐藏数量和内部耦合。</p>
            <p><strong>门禁：</strong>没有批准按钮自动通过；本次确认前不得进入白模。</p>
          </div>
        </details>
      </section>
    `;
  }
  const questionOnly = architectureStage?.architectureSpec?.reviewMode === "exact-source-questions-only";
  if (questionOnly) {
    const officialInternal = state.manifest.assets.find((asset) => asset.id === "slider-intake-haloo-official-07");
    const renderCrop = (crop) => officialInternal ? `
      <figure class="simple-source-crop ${crop.className}">
        <button type="button" data-asset-id="${escapeHtml(officialInternal.id)}" aria-label="放大查看 ${escapeHtml(crop.id)}">
          <img src="${repoUrl(officialInternal.path)}" alt="${escapeHtml(crop.label)}" loading="eager" decoding="async">
          <span>${escapeHtml(crop.id)}</span>
        </button>
        <figcaption>${escapeHtml(crop.label)}</figcaption>
      </figure>
    ` : "";
    const sliderCrops = [
      { id: "A", className: "crop-slider-a", label: "零件 A" },
      { id: "B", className: "crop-slider-b", label: "零件 B" }
    ].map(renderCrop).join("");
    const rotaryCrops = [
      { id: "C", className: "crop-rotary-c", label: "零件 C" },
      { id: "D", className: "crop-rotary-d", label: "零件 D" }
    ].map(renderCrop).join("");
    const sliderBoard = state.manifest.assets.find((asset) => asset.id === "magnetic-slide-tile-slider-construction-question-r007");
    const rotaryBoard = state.manifest.assets.find((asset) => asset.id === "magnetic-slide-tile-rotary-construction-question-r007");
    return `
      <section class="simple-review">
        <header class="simple-task-header">
          <span>现在只需要做一件事</span>
          <h2>告诉我：哪一块在动？</h2>
          <p>看下面两组官方图。点图片可以放大。</p>
        </header>
        <div class="simple-question-list">
          <section class="simple-question" data-question="slider">
            <div class="simple-question-copy">
              <span>问题 1 / 2</span>
              <h3>直推时，哪块移动？</h3>
              <p>请回复：<strong>“A 动，B 固定”</strong>、<strong>“B 动，A 固定”</strong>，或者<strong>“都不是”</strong>。</p>
            </div>
            <div class="simple-evidence-pair">${sliderCrops}</div>
          </section>
          <section class="simple-question" data-question="rotary">
            <div class="simple-question-copy">
              <span>问题 2 / 2</span>
              <h3>旋转时，哪块转动？</h3>
              <p>请回复：<strong>“C 转，D 固定”</strong>、<strong>“D 转，C 固定”</strong>，或者<strong>“都不是”</strong>。</p>
            </div>
            <div class="simple-evidence-pair">${rotaryCrops}</div>
          </section>
        </div>
        <p class="simple-photo-note">如果图里都不对，请发一张打开后的内部照片。我不会根据这些图猜结构。</p>
        <details class="technical-details">
          <summary>技术细节</summary>
          <div class="technical-details-body">
            <p><strong>完整关卡状态：</strong>01–03 已批准；04 为草稿；05–12 未开始。</p>
            <p><strong>证据来源：</strong>HALOOPLAYER 同款官方图 07；旧版错误结构已停用。</p>
            <p><strong>验证：</strong>直推与旋转构造仍标记为未知，批准按钮和下一阶段保持锁定。</p>
            <p><strong>测试：</strong>核心测试 12/12；浏览器简洁视图、大图返回、移动端与流水线校验通过。</p>
            <div class="technical-links">
              ${sliderBoard ? `<button type="button" class="button button-secondary" data-asset-id="${escapeHtml(sliderBoard.id)}">查看直推问题板</button>` : ""}
              ${rotaryBoard ? `<button type="button" class="button button-secondary" data-asset-id="${escapeHtml(rotaryBoard.id)}">查看旋转问题板</button>` : ""}
            </div>
          </div>
        </details>
      </section>
    `;
  }
  const reviewItems = [
    {
      assetId: "magnetic-slide-tile-part-tree-r006",
      title: "Part Tree · 对象责任",
      note: "两个外部主壳 + 可见功能模块"
    },
    {
      assetId: "magnetic-slide-tile-exploded-plan-r006",
      title: "Exploded Plan · 装配与运动",
      note: "直推与自由旋转分别受支持"
    }
  ];
  const reviewCards = reviewItems.map((item) => {
    const asset = state.manifest.assets.find((candidate) => candidate.id === item.assetId);
    if (!asset) return "";
    return `<figure class="official-evidence architecture-evidence">
      <button type="button" class="official-evidence-open" data-asset-id="${escapeHtml(asset.id)}">
        <img src="${repoUrl(asset.path)}" alt="${escapeHtml(item.title)}" loading="eager" decoding="async">
        <span class="official-evidence-shade"></span>
        <span class="official-evidence-label"><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.note)}</small></span>
      </button>
      <figcaption>Gate 04 rev 6 · 点击查看完整架构图</figcaption>
    </figure>`;
  }).join("");
  const decisions = [
    {
      tag: "外部装配",
      title: "两个外部主壳",
      body: "UpperShell_Moving 与 LowerShell_Fixed 定义外观承载关系；装饰面不再拆成额外外壳。"
    },
    {
      tag: "可见模块",
      title: "直线 / 旋转 / 调节模块保留",
      body: "双长轨珠槽、圆形珠轨、中央轴区、弹簧与球件作为可见功能模块；不把“两主壳”误写成“严格只有两个对象”。"
    },
    {
      tag: "双玩法",
      title: "直推 + 自由旋转并列",
      body: "直推行程 21 mm 仅为临时数字白模值；自由旋转不声明 90° 上限，也不要求推到末端才解锁。"
    },
    {
      tag: "未知边界",
      title: "耦合与隐藏工程量不猜",
      body: "隐藏件确数、公差、孔深、轨道截面、模块归属及两玩法切换耦合继续保持 unknown。"
    }
  ];
  return `
    <section class="contract-actions contract-actions-locked architecture-actions">
      <div class="action-heading">
        <div><p class="section-label">Gate 04 · 架构方案</p><h2>确认双玩法拆件架构</h2></div>
        <p>这版只确认对象责任、可见模块与运动边界；批准后才允许进入白模。旧五层结构、90° 限位和末端解锁假设均未恢复。</p>
      </div>
      <div class="official-mechanism-grid">${reviewCards}</div>
      <div class="contract-lock-grid">
        ${decisions.map((item) => `<article><span>${escapeHtml(item.tag)}</span><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.body)}</p></article>`).join("")}
      </div>
      <p class="contract-boundary">50 × 31 × 12 mm 与直推 21 mm 仍是用户授权的临时数字白模规格，不是官方或生产尺寸。当前 Unity 模型保持不变；未调用 Blender，未进入 Gate 05，未推送手机。</p>
    </section>
  `;
}

function decisionEvidenceVisual(visual, index) {
  const asset = state.manifest.assets.find((candidate) => candidate.id === visual.assetId);
  if (!asset) return "";
  const [x, y, width, height] = visual.viewBox;
  const markerId = `decision-arrow-${index}`;
  const overlays = {
    silhouette: `
      <rect class="decision-mark decision-mark-dashed" x="160" y="750" width="570" height="590" rx="250" />
      <g class="decision-label"><rect x="105" y="675" width="320" height="68" rx="18"/><text x="130" y="721">胶囊外轮廓</text></g>
      <path class="decision-leader" d="M 330 744 L 365 810" marker-end="url(#${markerId})" />
    `,
    layers: `
      <path class="decision-mark" d="M 310 1050 L 640 1080" />
      <path class="decision-mark decision-mark-secondary" d="M 285 1215 L 615 1240" />
      <g class="decision-label"><rect x="190" y="875" width="170" height="62" rx="17"/><text x="220" y="918">上片</text></g>
      <path class="decision-leader" d="M 350 925 L 500 1050" marker-end="url(#${markerId})" />
      <g class="decision-label"><rect x="190" y="1360" width="170" height="62" rx="17"/><text x="220" y="1403">下片</text></g>
      <path class="decision-leader" d="M 350 1370 L 490 1245" marker-end="url(#${markerId})" />
    `,
    translation: `
      <path class="decision-motion" d="M 505 1090 L 505 505" marker-end="url(#${markerId})" />
      <g class="decision-label"><rect x="185" y="285" width="425" height="72" rx="19"/><text x="215" y="334">沿主体长轴直线滑动</text></g>
    `,
    rotation: `
      <path class="decision-motion decision-motion-curved" d="M 260 730 C 150 535 295 300 535 275" marker-end="url(#${markerId})" />
      <g class="decision-label"><rect x="620" y="92" width="505" height="78" rx="20"/><text x="652" y="145">末段还会转动吗？</text></g>
    `,
    lanes: `
      <path class="decision-lane" d="M 880 510 L 1030 285" />
      <path class="decision-lane decision-lane-secondary" d="M 1000 580 L 1140 390" />
      <g class="decision-label"><rect x="640" y="125" width="250" height="66" rx="18"/><text x="668" y="170">纵向通道 A</text></g>
      <path class="decision-leader" d="M 850 190 L 940 400" marker-end="url(#${markerId})" />
      <g class="decision-label"><rect x="930" y="635" width="250" height="66" rx="18"/><text x="958" y="680">纵向通道 B</text></g>
      <path class="decision-leader" d="M 955 635 L 1040 510" marker-end="url(#${markerId})" />
    `,
    "dimensions-top": `
      <path class="decision-measure" d="M 745 790 L 745 1300" marker-start="url(#${markerId})" marker-end="url(#${markerId})" />
      <g class="decision-label"><rect x="545" y="660" width="300" height="70" rx="18"/><text x="575" y="709">总长度 L</text></g>
      <path class="decision-measure decision-measure-secondary" d="M 185 1240 L 690 1240" marker-start="url(#${markerId})" marker-end="url(#${markerId})" />
      <g class="decision-label"><rect x="145" y="1320" width="300" height="70" rx="18"/><text x="175" y="1369">总宽度 W</text></g>
    `,
    "dimensions-side": `
      <path class="decision-measure" d="M 665 1040 L 665 1255" marker-start="url(#${markerId})" marker-end="url(#${markerId})" />
      <g class="decision-label"><rect x="460" y="865" width="350" height="70" rx="18"/><text x="490" y="914">闭合总厚度 T</text></g>
    `,
    "travel-distance": `
      <path class="decision-measure" d="M 505 1055 L 505 525" marker-start="url(#${markerId})" marker-end="url(#${markerId})" />
      <g class="decision-label"><rect x="180" y="295" width="455" height="72" rx="19"/><text x="210" y="344">完全打开行程 S</text></g>
    `
  };
  return `
    <figure class="decision-evidence">
      <button type="button" class="decision-evidence-open" data-asset-id="${escapeHtml(asset.id)}" aria-label="查看${escapeHtml(visual.caption)}原图">
        <svg viewBox="${x} ${y} ${width} ${height}" role="img" aria-label="${escapeHtml(visual.alt)}">
          <defs>
            <marker id="${markerId}" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto-start-reverse" markerUnits="strokeWidth">
              <path d="M 0 0 L 8 4 L 0 8 z" fill="#67e5ec" />
            </marker>
          </defs>
          <image href="${repoUrl(asset.path)}" x="0" y="0" width="${visual.sourceWidth}" height="${visual.sourceHeight}" preserveAspectRatio="none" />
          <rect class="decision-image-vignette" x="${x}" y="${y}" width="${width}" height="${height}" />
          <g class="decision-annotations">${overlays[visual.annotation] || ""}</g>
        </svg>
      </button>
      <figcaption><span>${escapeHtml(visual.source)}</span>${escapeHtml(visual.caption)} · 点击看原图</figcaption>
    </figure>
  `;
}

function analysisActionPanel() {
  if (state.manifest.model.id !== "magnetic-slide-tile") return "";
  const analysisStage = state.manifest.stages.find((stage) => stage.id === "02-analysis");
  if (analysisStage?.analysisSpec?.revision === 8) {
    const contract = state.mechanismEvidenceContract;
    if (!contract) return `<section class="analysis-actions"><h2>机构证据合同未载入</h2></section>`;
    const sourceName = (assetId) => {
      if (assetId.includes("6022")) return "IMG_6022";
      if (assetId.includes("6023")) return "IMG_6023";
      if (assetId.includes("6024")) return "IMG_6024";
      if (assetId.includes("haloo")) return "HALOO";
      if (assetId.includes("nxedc")) return "NXEDC";
      if (assetId.includes("obsidian") || assetId.includes("obs-frame")) return "Obsidian";
      if (assetId.includes("supplemental-")) return "Chrome Hearts 补充";
      if (assetId.includes("user-video") || assetId.includes("user-frame")) return "IMG_5961";
      return "既有证据";
    };
    const appliedLabel = (asset) => {
      const direct = contract.constraints.filter((constraint) => constraint.sourceAssetIds.includes(asset.id));
      if (direct.length) return direct.slice(0, 4).map((constraint) => constraint.id.replace("MEC-", "")).join(" · ");
      if (asset.id.startsWith("slider-intake-obs-")) return "外形与不同图案边界";
      if (asset.id.startsWith("slider-intake-user-frame-")) return "外形、上下片与可见面";
      if (asset.id.startsWith("slider-intake-nxedc-")) return "同款候选外形与打开状态";
      if (asset.id.startsWith("slider-intake-haloo-official-")) return "官方同款外形/玩法/内部证据";
      if (asset.id.includes("supplemental-")) return "仅艺术语言补充；禁止作为机构证据";
      return "来源完整性与交叉核对";
    };
    const playbackBySource = {
      "slider-intake-user-mechanism-video-6022": "slider-analysis-img-6022-playback-proxy-r003",
      "slider-intake-user-mechanism-video-6023": "slider-analysis-img-6023-playback-proxy-r003",
      "slider-intake-user-mechanism-video-6024": "slider-analysis-img-6024-playback-proxy-r003"
    };
    const galleryIds = [
      ...contract.sourceInventory.groups.allGate01Intake,
      ...contract.sourceInventory.groups.chromeHeartsSupplementalOnly.filter((id) => id.endsWith("-image-r005")),
      "slider-analysis-official-mechanism-board-r002"
    ];
    const gallery = [...new Set(galleryIds)].map((assetId) => {
      const asset = state.manifest.assets.find((candidate) => candidate.id === assetId);
      if (!asset) return "";
      const openId = playbackBySource[asset.id] || asset.id;
      const preview = isImage(asset)
        ? `<img src="${repoUrl(asset.path)}" alt="${escapeHtml(asset.provenance?.note || asset.id)}" loading="lazy" decoding="async">`
        : isVideo(asset)
          ? `<span class="mechanism-reference-video-icon">▶</span><strong>${escapeHtml(asset.path.split("/").pop())}</strong>`
          : `<strong>${escapeHtml(extension(asset.path).toUpperCase())}</strong>`;
      return `
        <article class="mechanism-reference-card" data-reference-source="${escapeHtml(sourceName(asset.id))}">
          <button type="button" class="mechanism-reference-preview" data-asset-id="${escapeHtml(openId)}">${preview}</button>
          <div>
            <span class="reference-source-label">${escapeHtml(sourceName(asset.id))}</span>
            <h4>${escapeHtml(asset.provenance?.note || asset.id)}</h4>
            <p class="reference-applied-to"><strong>已应用到</strong>${escapeHtml(appliedLabel(asset))}</p>
            <code>${escapeHtml(asset.path)}</code>
            <div class="reference-actions">
              <button type="button" class="button button-secondary" data-asset-id="${escapeHtml(openId)}">打开完整归档</button>
              ${asset.sourceUrl ? `<a class="button button-secondary" href="${escapeHtml(asset.sourceUrl)}" target="_blank" rel="noreferrer">原始 URL</a>` : `<span>仓库原始输入</span>`}
            </div>
          </div>
        </article>
      `;
    }).join("");
    const technicalAssetIds = [
      "slider-analysis-video-timeline-r003",
      "slider-analysis-plate-identity-r003",
      "slider-analysis-one-way-slide-r003",
      "slider-analysis-rotation-audio-r003",
      "slider-analysis-axis-slot-hypothesis-r003",
      "slider-analysis-contradiction-r003",
      "slider-analysis-audio-contact-sheet-r003"
    ];
    return `
      <section class="analysis-actions reference-research-review">
        <header class="mechanism-review-heading">
          <div>
            <p class="section-label">步骤一：参考研究 · Gate 01 + Gate 02</p>
            <h2>先把全部证据变成约束，再生成任何机构</h2>
            <p>Gate 01 已完成输入归档；Gate 02 当前只审批证据结论和机器可读约束。CAD、Blender、Unity 与 Haptics 尚未解锁。</p>
          </div>
          <span class="evidence-basis-badge">${contract.sourceInventory.counts.uniqueAssets} 项来源已核对</span>
        </header>
        <nav class="mechanism-review-tabs" aria-label="步骤一参考研究">
          <button type="button" class="is-active" data-review-tab="conclusion" aria-selected="true">研究结论</button>
          <button type="button" data-review-tab="references" aria-selected="false">全部原图与拆解参考</button>
          <button type="button" data-review-tab="technical" aria-selected="false">内部技术证据</button>
        </nav>
        <section class="mechanism-review-panel is-active" data-review-panel="conclusion">
          <section class="applied-constraints-panel">
            <div class="reference-gallery-heading">
              <div><p class="section-label">结论已如何应用</p><h3>后续生成必须读取同一份证据合同</h3></div>
              <p>状态：等待 Gate 02 批准。所有下游 artifact 必须记录合同 SHA-256；禁止复制常量。</p>
            </div>
            <div class="mechanism-conclusions">
              ${contract.conclusions.map((conclusion, index) => `
                <article>
                  <span class="conclusion-number">${String(index + 1).padStart(2, "0")}</span>
                  <div><h3>${escapeHtml(conclusion.statement)}</h3><p>${escapeHtml(conclusion.constraintIds.join(" · "))} · 已应用到 CAD / Blender / Unity / Haptics / tests</p></div>
                  <strong>${conclusion.confidence} · ${conclusion.sourceCount} 源</strong>
                </article>
              `).join("")}
            </div>
          </section>
          <section class="coverage-matrix-panel">
            <div class="panel-heading"><h3>来源 → 约束覆盖矩阵</h3><span>${contract.coverageMatrix.length} 项</span></div>
            <div class="coverage-matrix">
              ${contract.coverageMatrix.map((row) => `
                <article>
                  <strong>${escapeHtml(row.topic)}</strong>
                  <span>支持：${escapeHtml([...new Set(row.supports.map(sourceName))].join(" / "))}</span>
                  <small>${row.conflicts.length ? `已化解：${escapeHtml(row.conflicts.join("；"))}` : "无当前冲突"}${row.unknowns.length ? ` · 未知：${escapeHtml(row.unknowns.join("、"))}` : ""}</small>
                </article>
              `).join("")}
            </div>
          </section>
          <section class="cad-locked-panel" data-cad-locked="true">
            <strong>交互 CAD：参考研究批准后生成</strong>
            <p>未来 CAD 只读取 <code>mechanism-evidence-contract.json</code>；当前无可操作沙盒，也不允许独立默认值。</p>
          </section>
          <section class="mechanism-unknowns">
            <div><p class="section-label">仍未知</p><h3>证据没有证明的内容</h3></div>
            <ul>${contract.unknowns.map((unknown) => `<li>${escapeHtml(unknown)}</li>`).join("")}</ul>
          </section>
        </section>
        <section class="mechanism-review-panel mechanism-reference-gallery" data-review-panel="references" hidden>
          <div class="reference-gallery-heading">
            <div><p class="section-label">全部原图与拆解参考</p><h3>来源不是展示品；每项标明已应用约束</h3></div>
            <p>用户输入、HALOO 官方同款、NXEDC 候选和 Chrome Hearts 艺术补充保持来源边界。</p>
          </div>
          <section class="applied-constraints-mini">
            <strong>合同应用摘要</strong>
            <span>${contract.conclusions.slice(0, 4).map((conclusion) => escapeHtml(conclusion.statement)).join(" · ")}</span>
            <small>${contract.constraints.length} 条约束等待 Gate 02 批准；CAD 仍锁定。</small>
          </section>
          <div class="mechanism-reference-grid">${gallery}</div>
        </section>
        <section class="mechanism-review-panel" data-review-panel="technical" hidden>
          <details class="technical-details mechanism-evidence-details">
            <summary>完整逐帧 / PTS / 音频 / tracking / 裁切</summary>
            <div class="technical-details-body">
              <p>三段银色同款视频共 ${contract.sourceInventory.counts.silverVideoPtsFrames} 个 PTS 帧；完整 tracking 与音频墙仅在这里展开。</p>
              <div class="technical-links">${technicalAssetIds.map((id) => `<button type="button" class="button button-secondary" data-asset-id="${id}">${escapeHtml(id)}</button>`).join("")}</div>
            </div>
          </details>
        </section>
      </section>
    `;
  }
  if ([4, 5, 6, 7, 9, 10, 11, 12, 13, 14, 15, 16].includes(analysisStage?.analysisSpec?.revision)) {
    const interactiveApproval = [15, 16].includes(analysisStage.analysisSpec.revision);
    const fourTrack = analysisStage.analysisSpec.revision === 16;
    const simulatorConfig = state.mechanismSimulatorConfig;
    if (interactiveApproval && (!state.mechanismEvidenceContract || !simulatorConfig)) {
      return `<section class="analysis-actions"><h2>交互 CAD 合同或配置未载入</h2></section>`;
    }
    const cadConfig = interactiveApproval
      ? cadConfigFromEvidenceContract(state.mechanismEvidenceContract, {
        ...simulatorConfig,
        expectedContractSha256: analysisStage.analysisSpec.contractSha256
      })
      : null;
    const cadInitial = interactiveApproval
      ? computeCadGeometry({}, cadConfig)
      : null;
    const conclusions = fourTrack ? [
      ["用户确认", "顶片背面共有四条有限纵轨", "外侧两轨负责前后直推；内侧两轨连接中心轴载体，禁止退回双槽简化。"],
      ["用户确认", "中心轴座是底壳上的独立凸起模块", "FixedAxisBoss protrusion > 0；不得出现凹坑或把覆盖圆盘实体化。"],
      ["用户确认", "球件沿轨滚动并切换档位", "球直径仅授权 2–3 mm；材料、数量、弹簧和预载仍未知。"],
      ["用户确认", "单轨宽度不超过约 3 mm", "CAD 用 1.8–3.0 mm 估计范围；截面和深度保持未知。"],
      ["用户确认", "底壳外表面仍光滑", "所有轨道与随动接触都隐藏在活动顶片下。"],
      ["用户确认", "顶片保持复合运动", "MovingTop = R_fixedAxis(θ) · T_local(s)，固定轴不平移。"],
      ["解析结果", "覆盖圆盘只用于验证", "MinimumOverlapDisk 不得渲染成凹坑、凸台或 shipping 组件。"]
    ] : [
      ["用户确认", "红色最小重叠圆盘必须始终被顶片完整覆盖", "圆盘固定属于底座并以固定轴为圆心；边界接触是合法极限，任何露出均无效。"],
      ["用户确认", "底部外壳固定且前后光滑", "BottomExterior 恒为 identity；两个外表面都不显示轨道或槽。"],
      ["用户确认", "固定轴心与旋转载体分层", "FixedAxis 局部/世界位置恒定；RotatingCarrier 只绕轴旋转，不平移。"],
      ["用户确认", "双槽位于活动顶片背面", "TopGrooveLeft / Right 是内凹纵向槽；载体两侧随动件与其接触。"],
      ["用户确认", "顶片沿旋转载体局部轴滑动", "Top = R_fixedAxis(θ) · T_local(s)；s 与 θ 可在一次拖动中同时变化。"],
      ["用户确认", "最大行程仍覆盖固定轴心", "CAD 显示覆盖包络；真实最小盖轴余量必须实测，不能猜。"],
      ["解析结果", "当前 sMax=0.361529L，由圆盘包含而非 0.46L 槽端点限制", "逆旋转后包含问题只依赖局部 s，因此当前 normalized capsule 的限制对 θ 不变。"]
    ];
    const technicalAssetIds = [
      "slider-analysis-video-timeline-r003",
      "slider-analysis-plate-identity-r003",
      "slider-analysis-one-way-slide-r003",
      "slider-analysis-rotation-audio-r003",
      "slider-analysis-axis-slot-hypothesis-r003",
      "slider-analysis-contradiction-r003",
      "slider-analysis-audio-contact-sheet-r003",
      "slider-analysis-mechanism-findings-r003",
      "slider-analysis-img-6022-playback-proxy-r003",
      "slider-analysis-img-6023-playback-proxy-r003",
      "slider-analysis-img-6024-playback-proxy-r003",
      "slider-analysis-proportion-analysis-r004"
    ];
    const technicalLinks = technicalAssetIds.map((assetId) => {
      const asset = state.manifest.assets.find((candidate) => candidate.id === assetId);
      if (!asset) return "";
      const label = asset.id.endsWith("proportion-analysis-r004")
        ? "比例校正记录"
        : assetSlotLabels[asset.slot] || "证据";
      return `<button type="button" class="button button-secondary" data-asset-id="${escapeHtml(asset.id)}">${escapeHtml(label)}</button>`;
    }).join("");
    const currentAppliedLabel = (asset) => {
      const direct = (state.mechanismEvidenceContract?.constraints || [])
        .filter((constraint) => constraint.sourceAssetIds.includes(asset.id));
      const currentPriority = [
        "MEC-ROTATING-CARRIER",
        "MEC-TOP-UNDERSIDE-GROOVES",
        "MEC-CARRIER-FOLLOWERS-BILATERAL",
        "MEC-TOP-CARRIER-LOCAL-TRANSLATION",
        "MEC-AXIS-COVERAGE-AT-MAX-TRAVEL",
        "MEC-BOTTOM-EXTERIOR-NO-RAILS"
      ];
      direct.sort((left, right) => {
        const leftIndex = currentPriority.indexOf(left.id);
        const rightIndex = currentPriority.indexOf(right.id);
        return (leftIndex < 0 ? 99 : leftIndex) - (rightIndex < 0 ? 99 : rightIndex);
      });
      if (direct.length) return direct.slice(0, 4).map((constraint) => constraint.id.replace("MEC-", "")).join(" · ");
      if (asset.id.startsWith("slider-intake-nxedc-")) return "同款候选外形与打开状态";
      if (asset.id.startsWith("slider-intake-haloo-official-")) return "官方同款外形、玩法与内部证据";
      if (asset.id.includes("playback-proxy")) return "行程、旋转、轴心与复合运动";
      return "来源完整性与交叉核对";
    };
    const referenceCard = ({ assetId, sourceLabel, title, note, timestamps = "", sourceUrl = null, appliedTo = null }) => {
      const asset = state.manifest.assets.find((candidate) => candidate.id === assetId);
      if (!asset) return "";
      const isVideo = /\.(mp4|mov)$/i.test(asset.path);
      return `
        <article class="mechanism-reference-card" data-reference-source="${escapeHtml(sourceLabel)}">
          <button type="button" class="mechanism-reference-preview" data-asset-id="${escapeHtml(asset.id)}">
            ${isVideo
              ? `<span class="mechanism-reference-video-icon">▶</span><strong>${escapeHtml(title)}</strong>`
              : `<img src="${repoUrl(asset.path)}" alt="${escapeHtml(title)}" loading="lazy" decoding="async">`}
          </button>
          <div>
            <span class="reference-source-label">${escapeHtml(sourceLabel)}</span>
            <h4>${escapeHtml(title)}</h4>
            <p>${escapeHtml(note)}</p>
            <p class="reference-applied-to"><strong>已应用到</strong>${escapeHtml(appliedTo || currentAppliedLabel(asset))}</p>
            ${timestamps ? `<small>关键时间：${escapeHtml(timestamps)}</small>` : ""}
            <code>${escapeHtml(asset.path)}</code>
            <div class="reference-actions">
              <button type="button" class="button button-secondary" data-asset-id="${escapeHtml(asset.id)}">打开完整归档</button>
              ${sourceUrl ? `<a class="button button-secondary" href="${escapeHtml(sourceUrl)}" target="_blank" rel="noreferrer">原始 URL</a>` : `<span>用户实拍无外部 URL</span>`}
            </div>
          </div>
        </article>
      `;
    };
    const userReferences = [
      { assetId: "slider-analysis-minimum-overlap-disk-user-screenshot-r015", sourceLabel: "用户权威标注", title: "红色最小重叠圆盘", note: "用户明确红色圆盘是顶片必须始终完整覆盖的最低重叠区域。", appliedTo: "MinimumOverlapDisk / 解析包含 / 实际 sMax" },
      { assetId: "slider-analysis-user-selected-bottom-base-close-r011", sourceLabel: "用户权威选图", title: "固定底壳、固定轴与旋转载体 · 近景", note: "确认黑色外壳光滑固定；中心轴不动；白银圆形载体为独立旋转内层。", appliedTo: "光滑底壳 / 固定轴 / 旋转载体 / 顶片双槽约束" },
      { assetId: "slider-analysis-user-selected-bottom-base-context-r011", sourceLabel: "用户权威选图", title: "固定底壳与被覆盖轴区 · 环境视图", note: "复核正常操作时顶片覆盖轴心区域，底壳外表面无外露轨道。", appliedTo: "光滑底壳 / 固定轴 / 轴心覆盖包络" },
      { assetId: "slider-analysis-img-6022-playback-proxy-r003", sourceLabel: "用户实拍", title: "IMG_6022 · 滑开与回位", note: "完整 H.264 播放代理；原始 MOV 保持归档。", timestamps: "1.67s / 3.34s / 5.84s / 7.50s / 11.67s" },
      { assetId: "slider-analysis-img-6023-playback-proxy-r003", sourceLabel: "用户实拍", title: "IMG_6023 · 0°↔180° 分档旋转", note: "同一平移登记下的可逆旋转。", timestamps: "0.40s / 1.60s / 3.20s / 6.40s / 8.00s" },
      { assetId: "slider-analysis-img-6024-playback-proxy-r003", sourceLabel: "用户实拍", title: "IMG_6024 · 多滑位复合运动", note: "部分与近最大滑位旋转，并暴露轨道面。", timestamps: "6.10–6.90s / 10.67s / 12.81s / 19.21s / 23.48s" }
    ];
    const halooReferences = [
      ["slider-intake-haloo-official-05", "弹簧与球件调节", "弹簧、钢/陶瓷球和内部模块近照"],
      ["slider-intake-haloo-official-06", "自由旋转玩法", "官方同款 free-spin 展示"],
      ["slider-intake-haloo-official-07", "内部机构与拆解总览", "双直线珠轨、圆形轨和中心轴区"],
      ["slider-intake-haloo-official-08", "直推玩法", "官方同款 straight-push 展示"]
    ].map(([assetId, title, note]) => {
      const asset = state.manifest.assets.find((candidate) => candidate.id === assetId);
      return { assetId, sourceLabel: "官方同款", title, note, sourceUrl: asset?.sourceUrl };
    });
    const nxedcReferences = [
      ["slider-intake-nxedc-contact-sheet", "NXEDC 同款候选总览", "六张已归档候选图；仅用于可见结构对照"],
      ["slider-intake-nxedc-ref-04", "打开斜视", "同款候选打开状态和相对运动"],
      ["slider-intake-nxedc-ref-05", "打开内部近照", "内部区域与端点关系"],
      ["slider-intake-nxedc-ref-06", "多配色打开状态", "跨配色核对共同机构"]
    ].map(([assetId, title, note]) => {
      const asset = state.manifest.assets.find((candidate) => candidate.id === assetId);
      return { assetId, sourceLabel: "外部候选", title, note, sourceUrl: asset?.sourceUrl || "https://nxedc.com/products/chrome-hearts-fidget-slider" };
    });
    const halooPageUrl = state.manifest.assets.find((candidate) => candidate.id === "slider-intake-haloo-official-metadata")?.sourceUrl;
    const halooInternalUrl = state.manifest.assets.find((candidate) => candidate.id === "slider-intake-haloo-official-07")?.sourceUrl;
    const nxedcOpenUrl = state.manifest.assets.find((candidate) => candidate.id === "slider-intake-nxedc-ref-04")?.sourceUrl;
    const derivedReferences = [
      { assetId: "slider-analysis-official-mechanism-board-r002", sourceLabel: "官方同款", title: "官方机构板", note: "既有同款机构汇总板；不替代原图。", sourceUrl: halooPageUrl },
      { assetId: "magnetic-slide-tile-official-rotary-pivot-r008", sourceLabel: "官方同款", title: "官方旋转轴区裁切", note: "既有内部轴区裁切。", sourceUrl: halooInternalUrl },
      { assetId: "magnetic-slide-tile-official-slider-a-r008", sourceLabel: "官方同款", title: "官方直轨裁切 A", note: "既有直推内部裁切。", sourceUrl: halooInternalUrl },
      { assetId: "magnetic-slide-tile-official-slider-b-r008", sourceLabel: "官方同款", title: "官方直轨裁切 B", note: "既有直推内部裁切。", sourceUrl: halooInternalUrl },
      { assetId: "magnetic-slide-tile-nxedc-open-track-r008", sourceLabel: "外部候选", title: "NXEDC 打开轨道裁切", note: "既有 open-track 局部裁切。", sourceUrl: nxedcOpenUrl }
    ];
    const referenceGallery = [...userReferences, ...halooReferences, ...nxedcReferences, ...derivedReferences]
      .map(referenceCard).join("");
    const contractInspector = interactiveApproval
      ? state.mechanismEvidenceContract.constraints.map((constraint) => `
        <article data-constraint-id="${escapeHtml(constraint.id)}">
          <strong>${escapeHtml(constraint.id)}</strong>
          <span>${escapeHtml(constraint.state)} · ${escapeHtml(constraint.confidence)}</span>
          <p>${escapeHtml(constraint.decisionNote)}</p>
          <small>${constraint.sourceAssetIds.length} 个来源 → ${escapeHtml(constraint.downstreamConsumers.join(" / "))}</small>
        </article>
      `).join("")
      : "";
    const cadIsDefault = interactiveApproval;
    return `
      <section class="analysis-actions mechanism-review">
        <header class="mechanism-review-heading">
          <div>
            <p class="section-label">Gate 02 · 可交互审批</p>
            <h2>${interactiveApproval ? "直接操作交互 CAD，再确认结构" : "先核对固定端点轴心，再操作工程图"}</h2>
            <p>${interactiveApproval ? "文字和截图只作补充。完成几何检查清单后，工具才会启用“确认交互 CAD”。" : "结论、交互 CAD 和原图拆解参考并列；逐帧计算仍单独收起。"}</p>
          </div>
          <span class="evidence-basis-badge">${interactiveApproval ? `合同 ${escapeHtml(analysisStage.analysisSpec.contractSha256.slice(0, 12))}…` : "证据约束默认值"}</span>
        </header>
        <nav class="mechanism-review-tabs" aria-label="Gate 02 评审内容">
          <button type="button" class="${cadIsDefault ? "" : "is-active"}" data-review-tab="conclusion" aria-selected="${cadIsDefault ? "false" : "true"}">结论</button>
          <button type="button" class="${cadIsDefault ? "is-active" : ""}" data-review-tab="cad" aria-selected="${cadIsDefault ? "true" : "false"}">交互 CAD</button>
          ${interactiveApproval ? `<button type="button" data-review-tab="next" aria-selected="false">下一步 · 实体尺寸</button>` : ""}
          <button type="button" data-review-tab="references" aria-selected="false">原图与拆解参考</button>
        </nav>

        <section class="mechanism-review-panel ${cadIsDefault ? "" : "is-active"}" data-review-panel="conclusion" ${cadIsDefault ? "hidden" : ""}>
          <details class="technical-details" ${cadIsDefault ? "" : "open"}>
          <summary>补充文字结论</summary>
          <div class="mechanism-conclusions" aria-label="机构结论">
          ${conclusions.map(([confidence, title, implication], index) => `
            <article>
              <span class="conclusion-number">${String(index + 1).padStart(2, "0")}</span>
              <div><h3>${escapeHtml(title)}</h3><p>${escapeHtml(implication)}</p></div>
              <strong data-confidence="${confidence}">${confidence}可信</strong>
            </article>
          `).join("")}
          </div>

          <section class="dimension-status" aria-label="尺寸与比例状态">
          <h3>当前比例边界</h3>
          <div>
            <article><span>实测</span><strong>视频帧、PTS、音频瞬态</strong></article>
            <article><span>推断范围</span><strong>L/W 约 1.52–1.62；沙盒取 1.57</strong></article>
            <article><span>未知</span><strong>真实 L / W / 厚度与毫米行程</strong></article>
          </div>
          <details>
            <summary>可选实体测量在工程图下方录入</summary>
            <small>全部字段默认空白。只有输入足够数据后才计算派生值；缺失值始终显示“待实测”。</small>
          </details>
          </section>
          </details>
        </section>

        <section class="mechanism-review-panel ${cadIsDefault ? "is-active" : ""}" data-review-panel="cad" ${cadIsDefault ? "" : "hidden"}>
        <section class="mechanism-sandbox" id="mechanism-sandbox" data-contract-sha256="${escapeHtml(analysisStage.analysisSpec.contractSha256 || "")}">
          <div class="sandbox-heading">
            <div><p class="section-label">交互 CAD 机构图</p><h3>一次拖动，同时滑动与旋转</h3></div>
            <div class="sandbox-mode" role="group" aria-label="操作模式">
              <button type="button" class="is-active" data-sandbox-mode="compound" aria-pressed="true">2-DOF 联动</button>
              <button type="button" data-sandbox-mode="pan" aria-pressed="false">平移图纸</button>
            </div>
          </div>
          <div class="cad-toolbar" aria-label="工程图工具">
            <div>
              <button type="button" data-cad-zoom="out" aria-label="缩小工程图">−</button>
              <output id="cad-zoom-value">100%</output>
              <button type="button" data-cad-zoom="in" aria-label="放大工程图">＋</button>
              <button type="button" data-cad-zoom="reset">复位视图</button>
              <button type="button" data-cad-sweep-toggle aria-pressed="false">360° 解析包含</button>
              <button type="button" data-cad-overlap-inspect>检查红色圆盘</button>
            </div>
            <div>
              <button type="button" data-detent-preset="0">0°</button>
              <button type="button" data-detent-preset="1">12°</button>
              <button type="button" data-detent-preset="3">36°</button>
              <button type="button" data-detent-step="-1" aria-label="反向一个档位">−12°</button>
              <button type="button" data-detent-step="1" aria-label="正向一个档位">＋12°</button>
            </div>
          </div>
          <div class="cad-view-inspection" aria-label="同步工程视图检查">
            <span>同步视图：</span>
            <button type="button" data-cad-view-inspect="top">已检查顶视</button>
            <button type="button" data-cad-view-inspect="side">已检查侧视</button>
            <button type="button" data-cad-view-inspect="section">已检查 A–A</button>
          </div>
          <div class="sandbox-workspace">
            <div class="sandbox-canvas-wrap">
              <svg class="sandbox-stage cad-stage" viewBox="0 0 1000 740" role="application" tabindex="0" aria-label="可缩放的磁吸推牌交互工程图">
                <defs>
                  <marker id="cad-arrow" markerWidth="7" markerHeight="7" refX="3.5" refY="3.5" orient="auto-start-reverse"><path d="M0 0 L7 3.5 L0 7 Z"/></marker>
                  <pattern id="cad-hatch" width="8" height="8" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="8"/></pattern>
                </defs>
                <g class="cad-viewport">
                  <g class="cad-top-view" data-cad-view="top" tabindex="0">
                    <text x="32" y="34" class="cad-view-title">TOP / 顶视图</text>
                    <text x="32" y="55" class="cad-view-subtitle">轮廓 L/W ${cadConfig.aspectRatioRange[0]}–${cadConfig.aspectRatioRange[1]} · 合同视频比例</text>
                    <path d="M${cadInitial.upper.centerX} 72 V590" class="cad-centerline"/>
                    <path d="M160 72 H500" class="cad-dimension"/>
                    <path d="M${cadInitial.upper.x} 82 V102 M${cadInitial.upper.x + cadInitial.upper.width} 82 V102" class="cad-extension"/>
                    <text id="cad-dimension-width" x="${cadInitial.upper.centerX}" y="66" class="cad-dimension-label">W = ? · 待实测 [未知]</text>
                    <path d="M170 ${cadInitial.upper.y} V${cadInitial.upper.y + cadInitial.upper.length}" class="cad-dimension"/>
                    <path d="M180 ${cadInitial.upper.y} H202 M180 ${cadInitial.upper.y + cadInitial.upper.length} H202" class="cad-extension"/>
                    <text id="cad-dimension-length" x="145" y="${cadInitial.upper.centerY}" class="cad-dimension-label cad-vertical-label">L = ? · 待实测 [未知]</text>
                    <g class="sandbox-fixed-bottom cad-fixed-bottom" data-cad-component="BottomExterior" data-layer-z="0">
                      <path d="${cadInitial.upper.path}" class="cad-upper-shell cad-bottom-base-shell"/>
                      ${cadInitial.upper.tangentPoints.map(([x, y]) => `<circle cx="${x}" cy="${y}" r="4" class="cad-tangent-point"/>`).join("")}
                    </g>
                    <g class="cad-minimum-overlap-disk" data-cad-component="MinimumOverlapDisk" data-layer-z="0.5">
                      <circle cx="${cadInitial.axis.world[0]}" cy="${cadInitial.axis.world[1]}" r="${cadInitial.minimumOverlapDisk.radiusPx}" class="cad-minimum-overlap-fill"/>
                      <circle cx="${cadInitial.axis.world[0]}" cy="${cadInitial.axis.world[1]}" r="${cadInitial.minimumOverlapDisk.radiusPx}" class="cad-minimum-overlap-outline"/>
                      <text x="${cadInitial.axis.world[0] - cadInitial.minimumOverlapDisk.radiusPx}" y="${cadInitial.axis.world[1] - cadInitial.minimumOverlapDisk.radiusPx - 12}" class="cad-minimum-overlap-label">最小重叠圆盘（必须始终被顶片完整覆盖）</text>
                    </g>
                    <g class="cad-rotating-carrier" data-cad-component="RotatingCarrier" data-layer-z="1">
                      <circle cx="${cadInitial.axis.world[0]}" cy="${cadInitial.axis.world[1]}" r="${cadInitial.carrier.radius}" class="cad-carrier-disc"/>
                      <rect x="${cadInitial.axis.world[0] - cadInitial.carrier.radius - 4}" y="${cadInitial.axis.world[1] - cadInitial.carrier.sideCutoutHalfWidth}" width="${cadInitial.carrier.sideCutoutHalfWidth * 1.25}" height="${cadInitial.carrier.sideCutoutHalfWidth * 2}" rx="10" class="cad-carrier-cutout"/>
                      <rect x="${cadInitial.axis.world[0] + cadInitial.carrier.radius - cadInitial.carrier.sideCutoutHalfWidth * 1.25 + 4}" y="${cadInitial.axis.world[1] - cadInitial.carrier.sideCutoutHalfWidth}" width="${cadInitial.carrier.sideCutoutHalfWidth * 1.25}" height="${cadInitial.carrier.sideCutoutHalfWidth * 2}" rx="10" class="cad-carrier-cutout"/>
                      ${cadInitial.followers.local.map((follower) => `<circle cx="${follower.point[0]}" cy="${follower.point[1]}" r="9" class="cad-carrier-follower" data-follower-side="${follower.side}"/>`).join("")}
                    </g>
                    <g class="sandbox-top-motion cad-top-motion" data-cad-component="TopPlate" data-layer-z="2">
                      <path d="${cadInitial.upper.path}" class="cad-lower-shell cad-moving-top-shell"/>
                      <g class="cad-top-grooves">
                        ${cadInitial.grooves.local.map((groove) => `
                          <line x1="${groove.start[0]}" y1="${groove.start[1]}" x2="${groove.end[0]}" y2="${groove.end[1]}" class="cad-top-groove ${groove.role === "fore-aft-slide" ? "is-outer-track" : "is-inner-track"}" data-groove-side="${groove.side}" data-groove-role="${groove.role}"/>
                          <circle cx="${groove.start[0]}" cy="${groove.start[1]}" r="7" class="cad-groove-endpoint is-closed" data-groove-endpoint="closed"/>
                          <circle cx="${groove.end[0]}" cy="${groove.end[1]}" r="7" class="cad-groove-endpoint is-open" data-groove-endpoint="open"/>
                        `).join("")}
                      </g>
                      <g class="cad-top-unknown-contacts">
                        ${cadInitial.grooves.local.map((groove) => `<circle cx="${groove.start[0]}" cy="${cadInitial.axis.local[1]}" r="13" class="cad-hidden-candidate"/>`).join("")}
                      </g>
                      <path d="${cadInitial.upper.path}" class="cad-slide-hit" data-cad-slide-hit/>
                    </g>
                    <g class="cad-sweep-envelope" hidden data-cad-sweep-envelope aria-label="30 档位全行程顶片包络">
                      ${Array.from({ length: cadConfig.detentCount }, (_, index) => {
                        const angle = index * cadConfig.detentStepDeg;
                        return `<path d="${cadInitial.upper.path}" transform="rotate(${angle} ${cadInitial.axis.world[0]} ${cadInitial.axis.world[1]}) translate(0 ${-cadConfig.maxTravelL * cadInitial.upper.length})" class="cad-sweep-outline"/>`;
                      }).join("")}
                      <circle cx="${cadInitial.axis.world[0]}" cy="${cadInitial.axis.world[1]}" r="${Math.max(12, cadInitial.coverage.coverResidualL * cadInitial.upper.length)}" class="cad-pivot-cover-envelope"/>
                    </g>
                    <text x="214" y="96" class="cad-callout cad-user">光滑固定底壳 BottomExterior</text>
                    <text x="360" y="516" class="cad-callout cad-user">活动顶片 TopPlate</text>
                    <text x="215" y="548" class="cad-callout cad-observed">${fourTrack ? "四轨有限长度 · 外轨直推 / 内轨联轴" : "双槽有限长度 · 两端点"}</text>
                    <text x="360" y="566" class="cad-callout cad-unknown">载体左右随动件截面未知</text>
                    <g class="cad-axis-overlay" data-cad-pivot-inspect="true" tabindex="0">
                      <circle cx="${cadInitial.axis.world[0]}" cy="${cadInitial.axis.world[1]}" r="148" class="cad-detent-ring"/>
                      ${Array.from({ length: cadConfig.detentCount }, (_, index) => {
                        const angle = index * cadConfig.detentStepDeg * Math.PI / 180;
                        const inner = index % 5 === 0 ? 132 : 138;
                        const x1 = cadInitial.axis.world[0] + Math.cos(angle) * inner;
                        const y1 = cadInitial.axis.world[1] + Math.sin(angle) * inner;
                        const x2 = cadInitial.axis.world[0] + Math.cos(angle) * 148;
                        const y2 = cadInitial.axis.world[1] + Math.sin(angle) * 148;
                        return `<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="cad-detent-tick ${index % 5 === 0 ? "is-major" : ""}"/>`;
                      }).join("")}
                      <circle cx="${cadInitial.axis.world[0]}" cy="${cadInitial.axis.world[1]}" r="164" class="cad-rotation-ring-hit" data-cad-rotation-ring/>
                      <circle cx="${cadInitial.axis.world[0]}" cy="${cadInitial.axis.world[1]}" r="14" class="sandbox-pivot-point"/>
                      <text x="${cadInitial.axis.world[0] + 20}" y="${cadInitial.axis.world[1] - 18}" class="cad-callout cad-user">FixedAxis 固定中心 [用户输入]</text>
                    </g>
                    <text x="${cadInitial.axis.local[0] - 108}" y="${cadInitial.axis.local[1] + 42}" class="cad-callout cad-user">轴心局部/世界位置恒定；无第三 DOF</text>
                    <path d="${cadInitial.upper.path}" class="cad-actual-max-outline"/>
                    <circle cx="${cadInitial.minimumOverlapDisk.boundaryContactWorld[0]}" cy="${cadInitial.minimumOverlapDisk.boundaryContactWorld[1]}" r="7" class="cad-overlap-contact-point"/>
                    <text x="214" y="590" class="cad-callout cad-video">实际 sMax：顶片边界与最小重叠圆盘相切</text>
                    <path d="M470 520 V360" class="cad-motion-limit"/>
                    <text x="482" y="440" class="cad-callout cad-video">外滑 ${cadConfig.supportedTravelRangeL[0]}–${cadConfig.supportedTravelRangeL[1]}L [合同视频比例]</text>
                    <line x1="${cadInitial.upper.x - 18}" y1="${cadInitial.upper.y + cadInitial.upper.length}" x2="${cadInitial.upper.x + cadInitial.upper.width + 18}" y2="${cadInitial.upper.y + cadInitial.upper.length}" class="cad-closed-stop-line"/>
                    <text x="205" y="${cadInitial.upper.y + cadInitial.upper.length + 22}" class="cad-closed-stop-label">闭合端点：随动点接触槽起点 · 上下轮廓重合</text>
                    <text x="205" y="${cadInitial.upper.y + cadInitial.upper.length + 40}" class="cad-open-stop-label">实际最大滑开：最小重叠圆盘边界相切 · 槽端尚有余量</text>
                    <line x1="185" y1="300" x2="475" y2="300" class="cad-section-line"/>
                    <text x="190" y="291" class="cad-section-label">A</text><text x="462" y="291" class="cad-section-label">A</text>
                    <polyline id="cad-path-trace" class="cad-path-trace" points=""/>
                  </g>

                  <g class="cad-side-view" data-cad-view="side" tabindex="0">
                    <text x="620" y="34" class="cad-view-title">SIDE + EXPLODED / 侧视分层</text>
                    <text x="620" y="55" class="cad-view-subtitle">顶片、隐藏载体、光滑底壳；厚度与间隙待实测</text>
                    <g class="cad-side-top"><rect x="640" y="110" width="285" height="38" class="cad-upper-side"/></g>
                    <g class="cad-side-carrier">
                      ${fourTrack ? `<path d="M${640 + cadInitial.side.axisLocalFraction * 285 - 26} 190 V166 Q${640 + cadInitial.side.axisLocalFraction * 285 - 26} 154 ${640 + cadInitial.side.axisLocalFraction * 285 - 14} 154 H${640 + cadInitial.side.axisLocalFraction * 285 + 14} Q${640 + cadInitial.side.axisLocalFraction * 285 + 26} 154 ${640 + cadInitial.side.axisLocalFraction * 285 + 26} 166 V190" class="cad-axis-boss-raised"/>` : ""}
                      <rect x="704" y="154" width="150" height="22" rx="11" class="cad-carrier-disc"/><circle cx="${640 + cadInitial.side.axisLocalFraction * 285}" cy="165" r="8" class="cad-axis-solid"/>
                    </g>
                    <line x1="${640 + cadInitial.side.axisLocalFraction * 285 - cadInitial.minimumOverlapDisk.radiusL * 285}" y1="181" x2="${640 + cadInitial.side.axisLocalFraction * 285 + cadInitial.minimumOverlapDisk.radiusL * 285}" y2="181" class="cad-minimum-overlap-section"/>
                    <g class="cad-side-bottom"><rect x="640" y="190" width="285" height="38" class="cad-lower-side"/></g>
                    <path d="M640 154 H925" class="cad-gap-line"/>
                    <path d="M947 110 V210" class="cad-dimension"/>
                    <text id="cad-dimension-thickness" x="958" y="165" class="cad-callout cad-unknown">总厚 ? [未知]</text>
                    <text x="652" y="133" class="cad-user">活动顶片 [用户输入]</text>
                    <text x="652" y="170" class="cad-user">${fourTrack ? "旋转载体 + 向上凸起固定轴座" : "旋转载体 + 固定轴"}</text>
                    <text x="652" y="215" class="cad-user">光滑固定底部外壳</text>
                    <text x="652" y="98" class="cad-unknown">顶片槽深 ? · 层间隙 ? [未知]</text>
                    <text x="640" y="238" class="cad-live-pose">θ=<tspan id="cad-side-angle">0.0°</tspan> · s=<tspan id="cad-side-travel">0.000L</tspan></text>
                    <line x1="640" y1="82" x2="640" y2="230" class="cad-closed-stop-line"/>
                    <text x="647" y="82" class="cad-closed-stop-label">闭合端点 · 随动点触槽起点</text>
                    <text x="647" y="258" class="cad-minimum-overlap-label">最大行程：顶片边界接触红色圆盘截面</text>
                  </g>

                  <g class="cad-section-view" data-cad-view="section" tabindex="0">
                    <text x="620" y="300" class="cad-view-title">SECTION A–A / ${fourTrack ? "四轨与凸起轴座" : "顶片双槽与载体随动件"}</text>
                    <text x="620" y="322" class="cad-view-subtitle">实线=可见证据；红虚线=隐藏候选</text>
                    <g class="cad-section-bottom">
                      <rect x="640" y="390" width="285" height="64" class="cad-section-lower"/>
                      <rect x="704" y="374" width="156" height="38" rx="19" class="cad-carrier-disc"/>
                      <circle cx="718" cy="374" r="10" class="cad-carrier-follower"/>
                      <circle cx="846" cy="374" r="10" class="cad-carrier-follower"/>
                      ${fourTrack ? `<path d="M754 422 V376 Q754 360 770 360 H794 Q810 360 810 376 V422 Z" class="cad-axis-boss-raised"/>` : ""}
                      <circle cx="782" cy="${fourTrack ? 370 : 422}" r="18" class="cad-axis-solid"/>
                    </g>
                    <g class="cad-section-top"><rect x="640" y="344" width="285" height="38" class="cad-section-upper"/>
                      ${fourTrack
                        ? `<path d="M674 344 V372 H696 V344" class="cad-top-groove is-outer-track"/><path d="M724 344 V372 H746 V344 M818 344 V372 H840 V344" class="cad-top-groove is-inner-track"/><path d="M868 344 V372 H890 V344" class="cad-top-groove is-outer-track"/>`
                        : `<path d="M700 344 V373 H736 V344 M828 344 V373 H864 V344" class="cad-top-groove"/>`}
                    </g>
                    <rect x="${782 - cadInitial.minimumOverlapDisk.radiusPx * 0.48}" y="382" width="${cadInitial.minimumOverlapDisk.radiusPx * 0.96}" height="14" rx="7" class="cad-minimum-overlap-section"/>
                    <text x="622" y="477" class="cad-observed">${fourTrack ? "四条内凹轨属于顶片背面：青=外轨，紫=内轨" : "两条内凹槽属于顶片背面"} [用户确认]</text>
                    <text x="622" y="497" class="cad-user">载体与顶片共享 θ；底壳/轴不动</text>
                    <text x="622" y="517" class="cad-unknown">随动球/槽截面 ? [未知]</text>
                    <text x="622" y="537" class="cad-unknown">间隙/余量/公差 ? [未知]</text>
                    <text x="622" y="566" class="cad-live-pose">θ=<tspan id="cad-section-angle">0.0°</tspan> · s=<tspan id="cad-section-travel">0.000L</tspan></text>
                    <line x1="640" y1="334" x2="640" y2="461" class="cad-closed-stop-line"/>
                    <text x="647" y="334" class="cad-closed-stop-label">A–A：红色圆盘截面必须完全位于顶片投影内</text>
                  </g>

                  <g class="cad-underside-view" data-cad-view="underside" tabindex="0">
                    <text x="620" y="610" class="cad-view-title">TOP UNDERSIDE / 顶片背面</text>
                    <text x="620" y="630" class="cad-view-subtitle">${fourTrack ? "四纵轨：外二直推，内二联轴" : "双纵向内凹槽"}随顶片执行 R(θ)·T_local(s)</text>
                    <g class="cad-underside-top">
                      <rect x="650" y="646" width="270" height="42" rx="21" class="cad-section-upper"/>
                      ${fourTrack
                        ? `<line x1="682" y1="651" x2="682" y2="683" class="cad-top-groove is-outer-track"/><line x1="748" y1="651" x2="748" y2="683" class="cad-top-groove is-inner-track"/><line x1="822" y1="651" x2="822" y2="683" class="cad-top-groove is-inner-track"/><line x1="888" y1="651" x2="888" y2="683" class="cad-top-groove is-outer-track"/>`
                        : `<line x1="704" y1="651" x2="704" y2="683" class="cad-top-groove"/><line x1="866" y1="651" x2="866" y2="683" class="cad-top-groove"/>`}
                    </g>
                    <text x="620" y="708" class="cad-unknown">槽宽 / 深 / 端形 / 公差 = ? [未知]</text>
                  </g>
                </g>
              </svg>
              <p class="sandbox-gesture-hint" id="sandbox-gesture-hint">抓住顶片直接拖动：顶片跟随指针同向移动，同时求解载体角度 θ 与旋转后的局部槽行程 s。</p>
              <div class="cad-evidence-legend" aria-label="证据状态图例">
                <span class="is-observed">实线绿/青：实测或用户权威</span>
                <span class="is-inferred">琥珀：视频比例或推断范围</span>
                <span class="is-unknown">红虚线：隐藏候选/未知</span>
              </div>
            </div>
            <aside class="sandbox-controls">
              <div class="sandbox-live" aria-live="polite">
                <div><span>顶片局部平移</span><strong id="sandbox-live-travel">+0.000L</strong></div>
                <div><span>轴心在底座局部位置</span><strong id="sandbox-live-axis-local">固定</strong></div>
                <div><span>轴心世界位置</span><strong id="sandbox-live-axis">固定</strong></div>
                <div><span>载体 / 顶片角度</span><strong id="sandbox-live-angle">0.0°</strong></div>
                <div><span>档位</span><strong id="sandbox-live-detent">00 / ${cadConfig.detentCount}</strong></div>
                <div><span>轴心覆盖</span><strong id="sandbox-live-state">已覆盖 · 余量待实测</strong></div>
                <div><span>随动点位置 u</span><strong id="sandbox-live-follower-u">0.320L</strong></div>
                <div><span>距闭合端点</span><strong id="sandbox-live-distance-start">0.000L</strong></div>
                <div><span>距最大端点</span><strong id="sandbox-live-distance-end">${cadConfig.maxTravelL.toFixed(3)}L</strong></div>
                <div><span>最小覆盖余量</span><strong id="sandbox-live-overlap-margin">${cadInitial.minimumOverlapDisk.containment.marginL.toFixed(4)}L</strong></div>
                <div><span>派生 sMax</span><strong id="sandbox-live-derived-smax">${cadConfig.maxTravelL.toFixed(6)}L</strong></div>
                <div><span>当前限制原因</span><strong id="sandbox-live-limit-cause">最小重叠圆盘</strong></div>
                <div><span>端点状态</span><strong id="sandbox-live-closed-stop">闭合端点 · 已啮合</strong></div>
              </div>
              <div class="sandbox-actions">
                <button type="button" class="button button-secondary" data-cad-pose="closed">闭合 0°</button>
                <button type="button" class="button button-secondary" data-cad-pose="open">最大行程</button>
                <button type="button" class="button button-primary" id="cad-reset">重置 CAD 姿态</button>
              </div>
              <div class="sandbox-actions cad-inspection-actions" aria-label="CAD 视图检查">
                <button type="button" class="button button-secondary" data-cad-inspect="fixedAxis">已检查固定轴</button>
                <button type="button" class="button button-secondary" data-cad-inspect="rotatingCarrier">已检查旋转载体</button>
                <button type="button" class="button button-secondary" data-cad-inspect="topUndersideGrooves">已检查顶片双槽</button>
                <button type="button" class="button button-secondary" data-cad-inspect="smoothBottomExterior">已检查光滑底壳</button>
              </div>
              <div class="cad-layer-controls">
                <label>组件分层 <output id="cad-layer-separation-output">0%</output><input id="cad-layer-separation" type="range" min="0" max="1" step="0.05" value="0"></label>
                <label>半透明度 <output id="cad-layer-opacity-output">62%</output><input id="cad-layer-opacity" type="range" min="0.2" max="1" step="0.02" value="0.62"></label>
                <div class="cad-layer-toggle-grid">
                  ${cadConfig.componentLayers.map((layer) => `<button type="button" class="button button-secondary is-active" data-cad-layer-toggle="${layer}">${layer}</button>`).join("")}
                </div>
              </div>
              <div class="cad-component-tree-html">
                <strong>证据零件树</strong>
                <span>BottomExterior</span>
                <span>└ ${fourTrack ? "FixedAxisBoss ↑" : "FixedAxis"}</span>
                <span class="cad-user">└ MinimumOverlapDisk ${fourTrack ? "(仅验证)" : ""}</span>
                <span>└ RotatingCarrier</span>
                <span>　├ CarrierFollowerLeft / Right</span>
                ${fourTrack ? `<span>　├ BallCandidateLeft / Right · 2–3 mm</span><span>MovingTop</span><span class="cad-observed">├ TopOuterGrooveLeft / Right · slide</span><span class="cad-user">├ TopInnerGrooveLeft / Right · axis link</span><span class="cad-unknown">└ Springs / preload / section ?</span>` : `<span>TopPlate</span><span>└ TopGrooveLeft / Right</span><span class="cad-unknown">└ UnknownContacts ?</span>`}
              </div>
              <p class="sandbox-tuning-state">纯运动学直接操控 · 无阻尼、力值、惯性、声音或手感模拟</p>
            </aside>
          </div>
          ${interactiveApproval ? `
          <section class="simulator-approval-progress cad-approval-progress" aria-live="polite">
            <div class="panel-heading"><div><p class="section-label">交互 CAD 审批清单</p><h3>完成 12 项几何检查后才能确认</h3></div><strong id="cad-checklist-count">0 / 12</strong></div>
            <ol id="cad-approval-checklist">
              <li data-milestone="minimumOverlapDisk">检查红色最小重叠圆盘的归属、圆心和边界</li>
              <li data-milestone="robustContainment">检查解析包含与 360×5 稠密验证</li>
              <li data-milestone="finiteGrooveEndpoints">验证${fourTrack ? "四轨" : "双槽"}有限起止点与随动点端部接触</li>
              <li data-milestone="synchronizedViews">检查同步顶视、侧视与 A–A</li>
              <li data-milestone="pointerDirection">验证拖动方向与顶片屏幕运动一致</li>
              <li data-milestone="fixedAxis">检查固定轴局部/世界坐标不变</li>
              <li data-milestone="rotatingCarrier">检查载体只旋转、不平移</li>
              <li data-milestone="topUndersideGrooves">检查顶片背面${fourTrack ? "四轨及外/内职责" : "双内凹槽"}</li>
              <li data-milestone="compoundMotion">一次拖动同时改变 s 与 θ</li>
              <li data-milestone="pivotCoverage">最大行程保持完整圆盘包含且边界相切</li>
              <li data-milestone="smoothBottomExterior">检查底壳前后光滑、无外露轨道</li>
              <li data-milestone="sourceMapping">打开来源→约束面板</li>
            </ol>
            <p id="cad-approval-status">请直接操作 CAD。文字或静态截图不能解锁确认。</p>
          </section>
          <details class="source-constraint-inspector" id="source-constraint-inspector">
            <summary>来源 → 约束检查器 · ${state.mechanismEvidenceContract.constraints.length} 条</summary>
            <div class="source-constraint-inspector-grid">${contractInspector}</div>
          </details>
          <section class="simulator-recording simulator-locked-panel" data-simulator-locked="true">
            <div><p class="section-label">下一步 · Gate 03 建模合同</p><h3>补齐真实物理尺寸后进入 Blender 流程</h3></div>
            <p>当前不生成独立手感 Simulator。旧草稿仅为 internal/superseded。</p>
          </section>
          ` : ""}
          <details class="cad-parameter-panel" open>
            <summary>实体测量与派生尺寸（全部可留空）</summary>
            <div class="cad-parameter-grid cad-normalized-parameters">
              <label>最小重叠圆盘半径<span><input type="number" step="0.001" min="0.05" max="0.40" data-cad-normalized="minimumOverlapDiskRadiusL" value="${cadConfig.minimumOverlapDiskRadiusL.toFixed(6)}"><small>L · 用户确认的 CAD 比例；mm 未知</small></span></label>
              <label>双槽终点<span><input type="number" step="0.001" min="0.4" max="0.95" data-cad-normalized="grooveEndFromTopL" value="${cadConfig.grooveEndFromTopL.toFixed(3)}"><small>from top / L · 视频比例</small></span></label>
              <label>顶片 L/W<span><input type="number" step="0.01" min="1.1" max="2.2" data-cad-normalized="aspectRatioLW" value="${cadConfig.aspectRatioLW.toFixed(2)}"><small>视频比例 · 可校正</small></span></label>
            </div>
            <div class="cad-parameter-grid">
              ${PHYSICAL_FIELDS.map((field) => `
                <label>${field.label}<span><input data-cad-physical="${field.id}" inputmode="decimal" placeholder="待实测"><small>${field.unit} · 用户输入</small></span></label>
              `).join("")}
            </div>
            <div class="cad-derived-values" aria-live="polite">
              <div><span>双槽端点上限</span><strong data-cad-derived="grooveLength">${cadConfig.grooveEndpointLimitL.toFixed(6)}L</strong></div>
              <div><span>圆盘包含上限</span><strong data-cad-derived="overlapLimit">${cadConfig.overlapContainmentLimitL.toFixed(6)}L</strong></div>
              <div><span>实际 sMax</span><strong data-cad-derived="actualSMax">${cadConfig.maxTravelL.toFixed(6)}L · 最小重叠圆盘</strong></div>
              <div><span>物理圆盘半径</span><strong>未知 · 待实测</strong></div>
              <div><span>实测 L/W</span><strong data-cad-derived="aspectRatioLW">? · 待实测</strong></div>
              <div><span>实测行程/L</span><strong data-cad-derived="travelL">? · 待实测</strong></div>
              <div><span>厚度栈余量</span><strong data-cad-derived="stackResidual">? mm · 待实测</strong></div>
              <div><span>轨道边缘余量</span><strong data-cad-derived="railEdgeClearance">? mm · 待实测</strong></div>
            </div>
          </details>
          <details class="cad-measurement-checklist">
            <summary>测量清单：哪些卡尺数据和照片能解锁未知项</summary>
            <ol>
              <li><strong>卡尺正交测量：</strong>总长、总宽、总厚、上下片厚度和闭合缝隙 → 解锁真实比例与厚度栈。</li>
              <li><strong>反面垂直照片 + 标尺：</strong>双轨中心距、轨宽、轴直径 → 解锁顶视和 A–A 剖面尺寸。</li>
              <li><strong>闭合/全开侧面微距：</strong>台阶高度、活动间隙、最大毫米行程 → 解锁止点和闭合余量。</li>
              <li><strong>拆解剖面：</strong>上片随动件、槽壁、棘轮和制造公差 → 才能把红虚线候选改为实线。</li>
            </ol>
          </details>
          <div class="sandbox-boundary">
            <strong>当前未证明的耦合</strong>
            <p>上片接触件、槽壁截面、棘轮结构、真实间隙、余量和制造公差仍未知。没有卡尺或拆解证据时只显示红色虚线候选。</p>
          </div>
          <p class="sandbox-limit-note">本页只验证零件、归属、轴心、轨道、剖面与运动学。阻尼、力感、惯性、声音和 Haptic 留到 CAD 批准后的独立 Simulator。</p>
          <details class="technical-details sandbox-equations">
            <summary>技术方程</summary>
            <div class="technical-details-body">
              <p>运动学状态为 <code>lower = T(s) · R(endpoint, θ)</code>；上片 transform 恒定，端点轴在底片局部坐标中恒定。</p>
              <p>滑动范围固定为合同支持的归一化范围；12° 标线只用于检查几何登记，不模拟档位力感。</p>
            </div>
          </details>
        </section>
        </section>

        ${interactiveApproval ? `
        <section class="mechanism-review-panel simulator-locked-tab" data-review-panel="next" hidden>
          <p class="section-label">Gate 03 · 当前阻塞项</p>
          <h2>需要真实物理尺寸</h2>
          <p>请提供总长、总宽、总厚、顶片厚、底片厚、闭合缝隙、双槽间距与槽宽、轴径、台阶高度、间隙、公差和最大直推行程。补齐后进入 Blender 建模与贴图；不经过独立 Simulator。</p>
        </section>
        ` : ""}

        <section class="mechanism-review-panel mechanism-reference-gallery" data-review-panel="references" hidden>
          <div class="reference-gallery-heading">
            <div><p class="section-label">原图与拆解参考</p><h3>同款原始资料一键打开</h3></div>
            <p>每项显示来源分类、原始 URL 和仓库归档路径。官方同款与外部候选不会覆盖用户实拍。</p>
          </div>
          <div class="mechanism-reference-grid">${referenceGallery}</div>
        </section>

        <section class="mechanism-unknowns">
          <div><p class="section-label">还不知道</p><h3>只剩这些会改变结构的未知项</h3></div>
          <ul>
            <li>上片接触／随动件的真实形状，以及槽壁截面。</li>
            <li>双侧轨道与上片随动件如何形成相对约束；轴心没有独立轨道自由度。</li>
            <li>真实尺寸、力值、磁力、摩擦和 Haptic 手感。</li>
          </ul>
        </section>

        <details class="technical-details mechanism-evidence-details">
          <summary>技术证据 · 逐帧、音频、计算与原图</summary>
          <div class="technical-details-body">
            <p>完整逐帧 manifests、38 张源链接裁切、5 ms RMS 音频候选、帧／PTS 校验和 rev 3 分析板均原样保留。它们不再占据默认评审页。</p>
            <div class="technical-links">${technicalLinks}</div>
          </div>
        </details>
      </section>
    `;
  }
  if (analysisStage?.analysisSpec?.revision === 3) {
    const boards = [
      ["slider-analysis-video-timeline-r003", "三段视频时间线", "按帧索引和 PTS 看完整动作"],
      ["slider-analysis-plate-identity-r003", "两片身份", "机构承载片 M / 活动盖片 C"],
      ["slider-analysis-one-way-slide-r003", "单向打开", "闭合止点 → 打开 → 返回"],
      ["slider-analysis-rotation-audio-r003", "旋转与棘轮", "0° / 12° / 90° / 180°"],
      ["slider-analysis-axis-slot-hypothesis-r003", "轴心 + 纵向轨迹", "实线已见；虚线是假设"],
      ["slider-analysis-contradiction-r003", "消除两组误读", "旋转≠滑移；外观面≠机构面"],
    ].map(([assetId, title, note]) => {
      const asset = state.manifest.assets.find((candidate) => candidate.id === assetId);
      if (!asset) return "";
      return `
        <figure class="video-analysis-board">
          <button type="button" data-asset-id="${escapeHtml(asset.id)}">
            <img src="${repoUrl(asset.path)}" alt="${escapeHtml(title)}" loading="eager" decoding="async">
          </button>
          <figcaption><strong>${escapeHtml(title)}</strong><span>${escapeHtml(note)} · 点击放大</span></figcaption>
        </figure>
      `;
    }).join("");
    const videos = [
      ["slider-analysis-img-6022-playback-proxy-r003", "IMG_6022", "滑开 / 关闭 · 426 帧"],
      ["slider-analysis-img-6023-playback-proxy-r003", "IMG_6023", "0↔180° 旋转 · 480 帧"],
      ["slider-analysis-img-6024-playback-proxy-r003", "IMG_6024", "滑动 + 多滑位旋转 · 821 帧"],
    ].map(([assetId, title, note]) => `
      <button type="button" class="video-source-link" data-asset-id="${assetId}">
        <strong>${title}</strong><span>${note}</span><small>播放完整视频</small>
      </button>
    `).join("");
    return `
      <section class="analysis-actions video-analysis-actions">
        <div class="action-heading">
          <div><p class="section-label">三段同款实拍 · 逐帧复核</p><h2>这个玩法/机构解读是否符合真实玩具？</h2></div>
          <p>先看连续动作，再看两片身份、滑动、旋转和隐藏结构边界。这里只确认玩法与机构理解。</p>
        </div>
        <div class="video-source-links">${videos}</div>
        <div class="video-analysis-grid">${boards}</div>
        <details class="technical-details">
          <summary>技术细节</summary>
          <div class="technical-details-body">
            <p><strong>已见：</strong>沿长轴单向打开并原路返回；0↔180° 分档旋转；部分和近最大滑位均可旋转；M 的反向机构面可见轨道、螺丝和珠列。</p>
            <p><strong>强支持：</strong>12° 一档，360° 共 30 档。完整 360° 来自用户权威陈述；视频直接覆盖到约 170–180°。</p>
            <p><strong>范围：</strong>最大行程约 0.38–0.46L，峰值约 0.50L。21 mm 只与范围相容，不是视频新测值。</p>
            <p><strong>仍未知：</strong>隐藏轴销归属、槽壁截面、耦合、公差，以及每个精确槽位能否旋转。</p>
            <p><strong>流程：</strong>第 3–11 关已因新上游证据过期；第 12 关继续封锁。旧正式模型仍默认；未改 Blender/Unity，未构建或推送手机。</p>
          </div>
        </details>
      </section>
    `;
  }
  const officialBoard = state.manifest.assets.find((asset) => asset.id === "slider-analysis-official-mechanism-board-r002");
  if (officialBoard && state.manifest.stages.find((stage) => stage.id === "02-analysis")?.artifactIds.includes(officialBoard.id)) {
    const visualItems = [
      { assetId: "slider-intake-haloo-official-08", kind: "push", title: "玩法 A · 直推", note: "沿长轴往复" },
      { assetId: "slider-intake-haloo-official-06", kind: "spin", title: "玩法 B · 自由旋转", note: "官方单独展示" },
      { assetId: "slider-intake-haloo-official-07", kind: "inside", title: "内部总览", note: "双直线珠轨 + 圆形珠轨" },
      { assetId: "slider-intake-haloo-official-05", kind: "tuning", title: "手感调节件", note: "弹簧 + 钢 / 陶瓷球" }
    ];
    const visualCards = visualItems.map((item) => {
      const asset = state.manifest.assets.find((candidate) => candidate.id === item.assetId);
      if (!asset) return "";
      return `<figure class="official-evidence official-evidence-${item.kind}">
        <button type="button" class="official-evidence-open" data-asset-id="${escapeHtml(asset.id)}">
          <img src="${repoUrl(asset.path)}" alt="${escapeHtml(item.title)}" loading="eager" decoding="async">
          <span class="official-evidence-shade"></span>
          <span class="official-evidence-label"><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.note)}</small></span>
          <span class="official-visual-marker" aria-hidden="true"></span>
        </button>
        <figcaption>HALOOPLAYER 官方同款图 · 点击看完整图</figcaption>
      </figure>`;
    }).join("");
    const items = [
      {
        title: "两种玩法，不是单一路径",
        body: "同款官方图分别展示直推和自由旋转。现在不再认定必须先推到末端才能旋转。"
      },
      {
        title: "两片外壳，不等于只有两个内部对象",
        body: "你说的两片对应上下两个主壳；官方内部图还显示双直线珠轨、圆形珠轨、中央轴承区、弹簧和球件。"
      },
      {
        title: "这一步暂不猜数量和尺寸",
        body: "本轮只锁定看得见的模块与玩法。滚珠、弹簧确数、孔深、公差和两种玩法如何耦合，仍保留为未知。"
      }
    ];
    return `
      <section class="analysis-actions official-analysis-actions">
        <div class="action-heading">
          <div><p class="section-label">参考研究 · 修正版</p><h2>请只确认：这是同款机构吗？</h2></div>
          <p>我已用同款官方实物图重做标注。确认后才会重写尺寸与运动方案；不会直接进入白模。</p>
        </div>
        <div class="official-mechanism-grid">${visualCards}</div>
        <div class="official-findings">
          ${items.map((item, index) => `<article><span>${String(index + 1).padStart(2, "0")}</span><div><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.body)}</p></div></article>`).join("")}
        </div>
      </section>
    `;
  }
  const items = [
    {
      title: "外形与分层",
      decision: "我会按胶囊形外轮廓，拆成上、下两个主要零件；闭合时两件叠合。是否正确？",
      impact: "确认后写入：白模轮廓 + 两个主要承载件",
      visuals: [
        { assetId: "slider-intake-user-frame-04", sourceWidth: 960, sourceHeight: 1706, viewBox: [80, 650, 760, 820], annotation: "silhouette", source: "你的实拍", caption: "闭合正面", alt: "实拍闭合状态，标出胶囊外轮廓" },
        { assetId: "slider-intake-user-frame-03", sourceWidth: 960, sourceHeight: 1706, viewBox: [180, 850, 560, 650], annotation: "layers", source: "你的实拍", caption: "侧面分层", alt: "实拍侧面状态，标出上片和下片" }
      ]
    },
    {
      title: "主要动作",
      decision: "我会把上片的主要运动定义为沿主体长轴直线滑动。是否正确？",
      impact: "确认后写入：直线滑轨方向 + 运动轴",
      visuals: [
        { assetId: "slider-intake-user-frame-12", sourceWidth: 960, sourceHeight: 1706, viewBox: [150, 250, 700, 1100], annotation: "translation", source: "你的实拍", caption: "打开状态", alt: "实拍打开状态，箭头标出长轴直线滑动方向" }
      ]
    },
    {
      title: "末段动作",
      decision: "打开末段是否还有小角度转动？如果没有，我只建立直线滑轨，不增加旋转关节。",
      impact: "确认后写入：是否存在第二个旋转自由度",
      visuals: [
        { assetId: "slider-intake-nxedc-ref-04", sourceWidth: 1280, sourceHeight: 1280, viewBox: [70, 50, 1140, 1100], annotation: "rotation", source: "外部同款参考", caption: "不同花纹，只看动作", alt: "外部同款打开状态，以弧形箭头询问是否存在末段旋转" }
      ]
    },
    {
      title: "内部结构",
      decision: "图中的两条纵向区域是否是真实工作的双轨？如果只是装饰或遮盖结构，请指出。",
      impact: "确认后写入：单轨、双轨，或仅作为外观结构",
      visuals: [
        { assetId: "slider-intake-nxedc-ref-04", sourceWidth: 1280, sourceHeight: 1280, viewBox: [620, 100, 580, 620], annotation: "lanes", source: "外部同款参考", caption: "内部局部", alt: "外部同款内部局部，标出两条候选纵向工作通道" }
      ]
    }
  ];
  return `
    <section class="analysis-actions">
      <div class="action-heading">
        <div><p class="section-label">当前需要你做的事</p><h2>确认 4 个建模理解</h2></div>
        <p>毫米尺寸、磁铁、钢板和滚珠数量不在这里确认，统一留到下一阶段的尺寸与结构方案。</p>
      </div>
      <div class="decision-grid">
        ${items.map((item, itemIndex) => `
          <article class="decision-card">
            <div class="decision-visuals ${item.visuals.length > 1 ? "decision-visuals-pair" : ""}">
              ${item.visuals.map((visual, visualIndex) => decisionEvidenceVisual(visual, `${itemIndex}-${visualIndex}`)).join("")}
            </div>
            <div class="decision-copy">
              <span>${String(itemIndex + 1).padStart(2, "0")} / 04 · 需要确认</span>
              <h3>${escapeHtml(item.title)}</h3>
              <p>${escapeHtml(item.decision)}</p>
              <small>${escapeHtml(item.impact)}</small>
            </div>
          </article>
        `).join("")}
      </div>
    </section>
  `;
}

function contractValue(path, fallback = "") {
  const value = path.reduce((current, key) => current?.[key], state.modelingContract);
  return value === null || value === undefined ? fallback : value;
}

function selectedContractValue(path, option) {
  return contractValue(path, "unknown") === option ? "selected" : "";
}

function measurementGuidePanel() {
  const contract = state.modelingContract?.schemaVersion === 2 ? state.modelingContract : null;
  const required = contract?.measurements?.required || {};
  const optional = contract?.measurements?.optional || {};
  const analysisStage = state.manifest.stages.find((stage) => stage.id === "02-analysis");
  const actualSMaxL = analysisStage.analysisSpec?.finalApproval?.geometryParameterSnapshot?.actualSMaxL;
  const validation = validateMeasurementContract({
    requiredMeasurements: required,
    optionalMeasurements: optional,
    cadConfig: { actualSMaxL }
  });
  const entry = (collection, id) => collection[id] || {};
  const sourceOptions = (selected) => ["", "卡尺", "毫米尺照片", "估算"].map((source) => (
    `<option value="${source}" ${selected === source ? "selected" : ""}>${source || "选择来源"}</option>`
  )).join("");
  const requiredFields = REQUIRED_CORE_MEASUREMENTS.map((definition, index) => {
    const current = entry(required, definition.id);
    return `
      <article class="measurement-field-card" data-measurement-field="${definition.id}">
        <header><span>${String(index + 1).padStart(2, "0")}</span><div><strong>${escapeHtml(definition.label)}</strong><small>必填 · mm</small></div></header>
        <div class="measurement-entry-row">
          <label><span>数值</span><input name="${definition.id}ValueMm" type="number" min="0.001" step="0.001" inputmode="decimal" value="${escapeHtml(current.valueMm ?? "")}" placeholder="待实测"></label>
          <label><span>± 不确定度</span><input name="${definition.id}UncertaintyMm" type="number" min="0" step="0.001" inputmode="decimal" value="${escapeHtml(current.uncertaintyMm ?? "")}" placeholder="例如 0.1"></label>
          <label><span>来源</span><select name="${definition.id}Source">${sourceOptions(current.source)}</select></label>
        </div>
        <p>${escapeHtml(definition.method)}</p>
        <input type="hidden" name="${definition.id}Method" value="${escapeHtml(definition.method)}">
        <div class="measurement-photo-row">
          <label><span>测量照片</span><input type="file" accept="image/png,image/jpeg,image/webp" data-measurement-photo="${definition.id}"></label>
          <label><span>或引用素材 ID / 路径</span><input name="${definition.id}PhotoReference" value="${escapeHtml((current.photoAssetIds || []).join(", "))}" placeholder="可稍后补充"></label>
          <small data-photo-status="${definition.id}">未关联照片</small>
        </div>
      </article>
    `;
  }).join("");
  const optionalFields = OPTIONAL_ENGINEERING_MEASUREMENTS.map((definition) => {
    const current = entry(optional, definition.id);
    return `
      <label class="optional-measurement-field">
        <span>${escapeHtml(definition.label)} <small>可选</small></span>
        <div><input name="${definition.id}ValueMm" type="number" min="0.001" step="0.001" inputmode="decimal" value="${escapeHtml(current.valueMm ?? "")}" placeholder="未知">
        <input name="${definition.id}UncertaintyMm" type="number" min="0" step="0.001" inputmode="decimal" value="${escapeHtml(current.uncertaintyMm ?? "")}" placeholder="± mm">
        <select name="${definition.id}Source">${sourceOptions(current.source)}</select></div>
      </label>
    `;
  }).join("");
  const guideDiagrams = [
    {
      title: "俯视正交 · L / W",
      note: "相机垂直产品；毫米尺与产品同平面，避免透视。",
      svg: `<svg viewBox="0 0 320 170" role="img" aria-label="闭合胶囊俯视长度和宽度测量图"><rect x="82" y="25" width="156" height="120" rx="60"/><path d="M82 12v146M238 12v146M68 25h184M68 145h184"/><text x="155" y="164">L</text><text x="252" y="90">W</text></svg>`
    },
    {
      title: "侧视正交 · T / 片厚 / 缝",
      note: "镜头与侧面平行；分别测顶片、底片、闭合缝和总厚。",
      svg: `<svg viewBox="0 0 320 170" role="img" aria-label="侧视厚度堆叠测量图"><rect x="38" y="38" width="240" height="37" rx="7"/><rect x="38" y="91" width="240" height="43" rx="7"/><path d="M22 38v96M15 38h14M15 134h14"/><path d="M38 82h240" stroke-dasharray="5 4"/><text x="8" y="88">T</text><text x="130" y="87">闭合缝</text></svg>`
    },
    {
      title: "同机位闭合 / 全开 · 行程",
      note: "固定相机与尺；以固定底片端点为基准比较顶片位移。",
      svg: `<svg viewBox="0 0 320 170" role="img" aria-label="闭合与全开同机位行程测量图"><rect x="45" y="29" width="126" height="54" rx="27"/><rect x="45" y="99" width="126" height="54" rx="27"/><rect x="116" y="99" width="126" height="54" rx="27" class="moving"/><path d="M116 89h126" marker-end="url(#arrow)"/><text x="171" y="85">最大行程</text></svg>`
    },
    {
      title: "内部俯视 · 轴距 / 载体直径",
      note: "圆端外缘到轴心中心；载体测最大外径，不测轴帽。",
      svg: `<svg viewBox="0 0 320 170" role="img" aria-label="轴心偏移和旋转载体直径测量图"><rect x="42" y="23" width="236" height="124" rx="62"/><circle cx="105" cy="85" r="42"/><circle cx="105" cy="85" r="5"/><path d="M42 158h63M63 153v10M105 153v10"/><path d="M105 43v84M96 43h18M96 127h18"/><text x="54" y="150">轴距</text><text x="114" y="88">载体 Ø</text></svg>`
    }
  ];
  return `
    <section class="measurement-guide" data-measurement-guide="true">
      <header class="measurement-guide-heading">
        <div><p class="section-label">Gate 03 · 引导测量</p><h2>先完成 9 项核心实测</h2></div>
        <div class="measurement-progress"><strong id="measurement-progress">${validation.progress.complete}/9</strong><span>一致性通过后才解锁建模合同</span></div>
      </header>
      <p class="measurement-guide-intro">不再要求从完整装配体无法可靠测量的加工余量或制造公差。所有核心值都记录毫米数、来源、方法和不确定度。</p>
      <div class="measurement-diagram-grid">${guideDiagrams.map((guide) => `<article><h3>${guide.title}</h3>${guide.svg}<p>${guide.note}</p></article>`).join("")}</div>
      <form id="modeling-contract-form" class="contract-form measurement-contract-form">
        <input type="hidden" name="measurementSchemaVersion" value="2">
        <section class="required-measurement-list">
          <div class="measurement-section-heading"><h3>必填核心尺寸</h3><span>9 项全部通过才进入评审</span></div>
          ${requiredFields}
        </section>
        <details class="optional-measurements">
          <summary>可选工程细节 · 不阻塞初始 Blender 白模</summary>
          <div class="optional-measurement-grid">${optionalFields}</div>
          <p>隐藏槽深、随动件和接触尺寸看不到时保持未知，不要猜。</p>
        </details>
        <section class="manufacturing-later">
          <h3>制造阶段再确定 · 当前不阻塞</h3>
          <div>${MANUFACTURING_LATER_FIELDS.map(({ label }) => `<span>${escapeHtml(label)} · 未知</span>`).join("")}</div>
          <p>工作间隙、加工余量和制造公差需要拆机、卡尺、生产意图或试制验证。</p>
        </section>
        <section class="measurement-consistency" id="measurement-consistency">
          <h3>一致性检查</h3>
          <ul><li>片厚 + 片厚 + 缝 ≈ 总厚</li><li>轴心与载体必须放得进底片轮廓</li><li>最大行程满足有限槽与最小重叠圆盘</li><li>L/W 只与视频范围比较并提示，不覆盖实测</li></ul>
          <p id="measurement-validation-state">等待 9 项核心测量。</p>
        </section>
        <div class="contract-save-row">
          <p class="contract-state">保存会创建不可变 Gate 03 测量合同 revision；Blender 仍保持锁定。</p>
          <button type="submit" class="button button-primary">保存测量进度</button>
        </div>
      </form>
    </section>
  `;
}

function contractActionPanel() {
  if (state.manifest.model.id !== "magnetic-slide-tile") return `<section class="task-heading"><h2>尺寸与运动方案</h2></section>`;
  return measurementGuidePanel();
  /*
  const complete = Boolean(state.modelingContract?.completeness?.complete);
  const missing = state.modelingContract?.completeness?.missing || [];
  const secondaryMotion = contractValue(["mechanism", "secondaryMotion"], "unknown");
  const hardwareMode = contractValue(["mechanism", "internalHardwareMode"], "unknown");
  const dimensionBasis = contractValue(["dimensionBasis", "type"], "user-measured");
  const estimated = dimensionBasis === "anthropometric-estimate";
  const officialOnly = dimensionBasis === "official-only";
  const provisional = dimensionBasis === "user-authorized-provisional";
  const rangeText = (field) => {
    const range = contractValue(["dimensionEstimateRangesMm", field], null);
    return range ? `估算范围 ${range.min}–${range.max} mm` : "可按手感微调";
  };
  if (officialOnly || provisional) {
    const officialVisualItems = [
      { assetId: "slider-intake-haloo-official-08", kind: "push", title: "玩法 A · 直推", note: "HALOOPLAYER 同款官方图" },
      { assetId: "slider-intake-haloo-official-06", kind: "spin", title: "玩法 B · 自由旋转", note: "HALOOPLAYER 同款官方图" },
      { assetId: "slider-intake-haloo-official-07", kind: "inside", title: "内部结构", note: "双直线珠轨 + 圆形珠轨" },
      { assetId: "slider-intake-haloo-official-05", kind: "tuning", title: "调节件", note: "弹簧 + 钢 / 陶瓷球" }
    ];
    const officialVisualCards = officialVisualItems.map((item) => {
      const asset = state.manifest.assets.find((candidate) => candidate.id === item.assetId);
      if (!asset) return "";
      return `<figure class="official-evidence official-evidence-${item.kind}">
        <button type="button" class="official-evidence-open" data-asset-id="${escapeHtml(asset.id)}">
          <img src="${repoUrl(asset.path)}" alt="${escapeHtml(item.title)}" loading="eager" decoding="async">
          <span class="official-evidence-shade"></span>
          <span class="official-evidence-label"><strong>${escapeHtml(item.title)}</strong><small>${escapeHtml(item.note)}</small></span>
          <span class="official-visual-marker" aria-hidden="true"></span>
        </button>
        <figcaption>结构证据 · 点击看官方原图</figcaption>
      </figure>`;
    }).join("");
    const contractItems = provisional ? [
      {
        tag: "临时白模规格",
        title: `${contractValue(["dimensions", "overallLengthMm"])} × ${contractValue(["dimensions", "overallWidthMm"])} × ${contractValue(["dimensions", "totalThicknessMm"])} mm`,
        body: `直推行程 ${contractValue(["dimensions", "linearTravelMm"])} mm；只用于下一阶段的数字白模比例与运动占位。`
      },
      {
        tag: "来源边界",
        title: "用户授权的临时数字",
        body: "用户明确取消 official-only 限制并直接授权本组数值；它们不是 HALOOPLAYER / NXEDC 发布值、不是生产实测，也不是从视频静默推断。"
      },
      {
        tag: "结构来源",
        title: "官方同款机构证据继续有效",
        body: "直推、自由旋转、两个外部主壳，以及可见直线／旋转／弹簧／球件模块继续承接 HALOOPLAYER / NXEDC 同款资料。"
      },
      {
        tag: "仍然未知",
        title: "生产尺寸与隐藏确数未锁定",
        body: "精确生产尺寸、公差、孔深、内部件数量及两种玩法的耦合仍未知；后续获得实物或官方数据时必须重开上游 revision。"
      }
    ] : [
      {
        tag: "结构来源",
        title: "NXEDC / HALOOPLAYER 同款资料",
        body: "直推、自由旋转、两个外部主壳和可见内部模块继续以同款商品资料为准，不从用户视频反推结构。"
      },
      {
        tag: "尺寸状态",
        title: "L / W / T / S 暂时未知",
        body: "同款官方页面和 NXEDC 当前资料没有发布完整长、宽、厚与直推行程，不能把相似产品尺寸当成这款。"
      },
      {
        tag: "已排除",
        title: "删除视频比例估算",
        body: "此前的 50 × 31 × 12 mm 与 21 mm 不再作为建模合同；你的实拍只保留为原始输入，不是本关尺寸证据。"
      },
      {
        tag: "下一步",
        title: "等待同款公开尺寸",
        body: "在 HALOOPLAYER 或 NXEDC 找到可核验的同款数值前，Gate 03 保持草稿，不生成拆件图或 Blender 白模。"
      }
    ];
    return `
      <section class="contract-actions contract-actions-locked">
        <div class="action-heading">
          <div><p class="section-label">Gate 03 · 建模规格</p><h2>${provisional ? "确认临时数字白模规格" : "官方结构已锁定，尺寸仍缺来源"}</h2></div>
          <p>${provisional ? "这版只把你授权的临时数值作为数字白模合同，同时保留同款官方结构证据与生产尺寸未知边界；批准后才可进入拆件方案。" : "你选择只接受同款官方或 NXEDC 发布的尺寸。现有页面没有完整 L / W / T / S，因此本关不会显示可批准的估算值。"}</p>
        </div>
        <div class="official-mechanism-grid">${officialVisualCards}</div>
        <div class="contract-lock-grid">
          ${contractItems.map((item) => `<article><span>${escapeHtml(item.tag)}</span><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.body)}</p></article>`).join("")}
        </div>
        <p class="contract-boundary">${provisional ? "本关批准的是临时数字白模规格，不是生产尺寸或官方尺寸。当前 Unity 模型保持不变；未调用 Blender，未进入 Gate 04，未推送手机。" : "当前 Unity 模型保持不变；未调用 Blender，未进入 Gate 04，未推送手机。"}</p>
      </section>
    `;
  }
  const visuals = [
    { assetId: "slider-intake-user-frame-04", sourceWidth: 960, sourceHeight: 1706, viewBox: [80, 650, 760, 820], annotation: "dimensions-top", source: "你的实拍", caption: "闭合状态：测 L / W", alt: "实拍闭合状态，标出闭合总长度与总宽度" },
    { assetId: "slider-intake-user-frame-03", sourceWidth: 960, sourceHeight: 1706, viewBox: [180, 850, 560, 650], annotation: "dimensions-side", source: "你的实拍", caption: "侧面状态：测 T", alt: "实拍侧面状态，标出闭合总厚度" },
    { assetId: "slider-intake-user-frame-12", sourceWidth: 960, sourceHeight: 1706, viewBox: [150, 250, 700, 1100], annotation: "travel-distance", source: "你的实拍", caption: "完全打开：测 S", alt: "实拍打开状态，标出直线行程" }
  ];
  if (secondaryMotion === "dual-mode-free-spin") {
    const dimensions = contractValue(["dimensions"], {});
    const ranges = contractValue(["dimensionEstimateRangesMm"], {});
    const range = (field) => ranges?.[field] ? `${ranges[field].min}–${ranges[field].max} mm` : "待实测";
    const contractItems = [
      {
        tag: "尺寸",
        title: `${dimensions.overallLengthMm} × ${dimensions.overallWidthMm} × ${dimensions.totalThicknessMm} mm`,
        body: `继续沿用成人手指与用户视频估算；L ${range("overallLengthMm")}，W ${range("overallWidthMm")}，T ${range("totalThicknessMm")}。`
      },
      {
        tag: "行程",
        title: `直推 ${dimensions.linearTravelMm} mm`,
        body: `估算范围 ${range("linearTravelMm")}；直推与自由旋转作为两种玩法，不再写成“推到底才旋转”。`
      },
      {
        tag: "结构",
        title: "两个外部主壳 + 可见内部模块",
        body: "保留双长轨珠槽、圆形珠轨、中央轴区、弹簧与球件；装饰面不是额外外壳。"
      },
      {
        tag: "未知",
        title: "不锁定确数与耦合",
        body: "滚珠、弹簧、磁件确数、孔深、公差，以及直推和旋转模块如何耦合，留到有实物证据时再决定。"
      }
    ];
    return `
      <section class="contract-actions contract-actions-locked">
        <div class="action-heading">
          <div><p class="section-label">Gate 03 · 建模规格</p><h2>确认尺寸与双玩法合同</h2></div>
          <p>尺寸沿用你此前接受的人体比例估算；机构部分已按刚批准的官方同款证据纠正。确认后才会重新画拆件图。</p>
        </div>
        <div class="contract-visual-grid">
          ${visuals.map((visual, index) => decisionEvidenceVisual(visual, `contract-dual-${index}`)).join("")}
        </div>
        <div class="contract-lock-grid">
          ${contractItems.map((item) => `<article><span>${escapeHtml(item.tag)}</span><h3>${escapeHtml(item.title)}</h3><p>${escapeHtml(item.body)}</p></article>`).join("")}
        </div>
        <p class="contract-boundary">本关批准的是数字白模规格，不是生产尺寸，也不代表内部拆机工程结构已经证实。</p>
      </section>
    `;
  }
  return `
    <section class="contract-actions">
      <div class="action-heading">
        <div><p class="section-label">Gate 03 · 当前需要你做的事</p><h2>确认尺寸建议与运动</h2></div>
        <p>${estimated ? "我已按视频中同景深的成人手指比例给出建议值。你不必报精确毫米，只需看整体是偏大、偏小，还是合适。" : "确认实物尺寸与运动选择；保存完整后，才会出现本关的“确认，继续”。"}</p>
      </div>
      <div class="contract-visual-grid">
        ${visuals.map((visual, index) => decisionEvidenceVisual(visual, `contract-${index}`)).join("")}
      </div>
      <form id="modeling-contract-form" class="contract-form">
        ${estimated ? `<section class="estimate-summary">
          <div><span>闭合建议</span><strong>${escapeHtml(contractValue(["dimensions", "overallLengthMm"]))} × ${escapeHtml(contractValue(["dimensions", "overallWidthMm"]))} × ${escapeHtml(contractValue(["dimensions", "totalThicknessMm"]))} mm</strong></div>
          <div><span>直线行程</span><strong>${escapeHtml(contractValue(["dimensions", "linearTravelMm"]))} mm</strong></div>
          <p>这是视频比例估算，不是生产实测；输入框仍可直接改。误差范围已经跟随每个字段保存。</p>
        </section>` : ""}
        <input type="hidden" name="dimensionBasisType" value="${escapeHtml(dimensionBasis)}">
        <fieldset>
          <legend>${estimated ? "建议尺寸" : "实测尺寸"} · mm</legend>
          <p class="field-help">L / W / T 是闭合状态；S 是上片从闭合到完全打开的直线位移。</p>
          <div class="measurement-grid">
            <label><span>总长度 L</span><input name="overallLengthMm" type="number" min="0.01" step="0.01" inputmode="decimal" value="${escapeHtml(contractValue(["dimensions", "overallLengthMm"]))}" placeholder="例如 50"><small>${estimated ? rangeText("overallLengthMm") : "闭合后最上端到最下端"}</small></label>
            <label><span>总宽度 W</span><input name="overallWidthMm" type="number" min="0.01" step="0.01" inputmode="decimal" value="${escapeHtml(contractValue(["dimensions", "overallWidthMm"]))}" placeholder="例如 31"><small>${estimated ? rangeText("overallWidthMm") : "闭合后最宽处"}</small></label>
            <label><span>总厚度 T</span><input name="totalThicknessMm" type="number" min="0.01" step="0.01" inputmode="decimal" value="${escapeHtml(contractValue(["dimensions", "totalThicknessMm"]))}" placeholder="例如 12"><small>${estimated ? rangeText("totalThicknessMm") : "上下两片闭合后的总厚度"}</small></label>
            <label><span>直线行程 S</span><input name="linearTravelMm" type="number" min="0.01" step="0.01" inputmode="decimal" value="${escapeHtml(contractValue(["dimensions", "linearTravelMm"]))}" placeholder="例如 21"><small>${estimated ? rangeText("linearTravelMm") : "闭合到完全打开的位移"}</small></label>
            <label><span>白模接缝</span><input name="seamClearanceMm" type="number" min="0.01" step="0.01" inputmode="decimal" value="${escapeHtml(contractValue(["dimensions", "seamClearanceMm"]))}" placeholder="建议 0.25"><small>数字模型的可见分件间隙；不是实物测量</small></label>
          </div>
        </fieldset>
        <fieldset>
          <legend>运动与内部结构</legend>
          <div class="contract-choice-grid">
            <label><span>末段动作</span><select name="secondaryMotion">
              <option value="unknown" ${selectedContractValue(["mechanism", "secondaryMotion"], "unknown")}>请选择</option>
              <option value="translation-only" ${selectedContractValue(["mechanism", "secondaryMotion"], "translation-only")}>只有直线滑动，没有旋转</option>
              <option value="translation-plus-rotation" ${selectedContractValue(["mechanism", "secondaryMotion"], "translation-plus-rotation")}>直线滑动后还有小角度旋转</option>
              <option value="dual-mode-free-spin" ${selectedContractValue(["mechanism", "secondaryMotion"], "dual-mode-free-spin")}>直推 + 自由旋转，两种玩法</option>
            </select><small>这会决定是否建立第二个旋转关节</small></label>
            <label id="rotation-angle-field" ${secondaryMotion === "translation-plus-rotation" ? "" : "hidden"}><span>最大旋转角度</span><input name="maxRotationDeg" type="number" min="0.01" step="0.1" inputmode="decimal" value="${escapeHtml(contractValue(["mechanism", "maxRotationDeg"]))}" placeholder="角度"><small>从直线方向偏转的最大角度</small></label>
            <label><span>两条纵向区域</span><select name="laneMode">
              <option value="unknown" ${selectedContractValue(["mechanism", "laneMode"], "unknown")}>请选择</option>
              <option value="dual-working-lanes" ${selectedContractValue(["mechanism", "laneMode"], "dual-working-lanes")}>两条都是真实工作通道</option>
              <option value="visual-only" ${selectedContractValue(["mechanism", "laneMode"], "visual-only")}>只按可见外观表现，不认定为双轨</option>
            </select><small>这会直接改变第四关的零件与轨道方案</small></label>
            <label><span>内部还原深度</span><select name="internalHardwareMode">
              <option value="unknown" ${selectedContractValue(["mechanism", "internalHardwareMode"], "unknown")}>请选择</option>
              <option value="visual-mechanism-proxy" ${selectedContractValue(["mechanism", "internalHardwareMode"], "visual-mechanism-proxy")}>只准确还原可见机构</option>
              <option value="physical-teardown-replica" ${selectedContractValue(["mechanism", "internalHardwareMode"], "physical-teardown-replica")}>按拆机结构做工程复刻</option>
            </select><small>没有拆机证据时，第一项不会虚构隐藏零件</small></label>
          </div>
          <div id="hardware-counts" class="hardware-counts" ${hardwareMode === "physical-teardown-replica" ? "" : "hidden"}>
            <p>工程复刻需要你给出实物拆机数量。</p>
            <label><span>磁铁</span><input name="magnetCount" type="number" min="0" step="1" inputmode="numeric" value="${escapeHtml(contractValue(["mechanism", "magnetCount"]))}"></label>
            <label><span>滚珠</span><input name="ballCount" type="number" min="0" step="1" inputmode="numeric" value="${escapeHtml(contractValue(["mechanism", "ballCount"]))}"></label>
            <label><span>钢板</span><input name="steelPlateCount" type="number" min="0" step="1" inputmode="numeric" value="${escapeHtml(contractValue(["mechanism", "steelPlateCount"]))}"></label>
          </div>
        </fieldset>
        <div class="contract-save-row">
          <p class="contract-state ${complete ? "is-complete" : ""}">${complete ? "这版规格已填写完整，请保存后审批。" : `还需要：${escapeHtml(missing.join("、") || "填写并保存尺寸与机构选择")}`}</p>
          <button type="submit" class="button button-primary">保存这版规格</button>
        </div>
      </form>
    </section>
  `;
  */
}

function mountMechanismSandbox() {
  const root = document.getElementById("mechanism-sandbox");
  if (!root) return;
  if (state.sandboxCleanup) state.sandboxCleanup();

  const analysisStage = state.manifest.stages.find((candidate) => candidate.id === "02-analysis");
  const simulatorConfig = state.mechanismSimulatorConfig;
  if (!state.mechanismEvidenceContract || !simulatorConfig) {
    root.dataset.ready = "false";
    return;
  }
  const cadConfig = cadConfigFromEvidenceContract(state.mechanismEvidenceContract, {
    ...simulatorConfig,
    expectedContractSha256: analysisStage.analysisSpec.contractSha256
  });
  const sandbox = createMechanismSandbox(state.mechanismEvidenceContract, {
    ...simulatorConfig.reviewTuning,
    maxTravelL: cadConfig.maxTravelL
  });
  const stage = root.querySelector(".sandbox-stage");
  const lowerTranslation = root.querySelector(".sandbox-lower-translation");
  const lowerRotation = root.querySelector(".sandbox-lower-rotation");
  const fixedUpper = root.querySelector(".sandbox-fixed-upper");
  const cadViewportGroup = root.querySelector(".cad-viewport");
  const axisOverlay = root.querySelector(".cad-axis-overlay");
  const sideLower = root.querySelector(".cad-side-lower");
  const sectionMoving = root.querySelector(".cad-section-moving");
  const pathTrace = root.querySelector("#cad-path-trace");
  const modeButtons = [...root.querySelectorAll("[data-sandbox-mode]")];
  const controls = [...root.querySelectorAll('.sandbox-sliders input:not([name="internalsOpacity"])')];
  const internalsOpacity = root.querySelector("#sandbox-internals-opacity");
  const soundToggle = root.querySelector("#sandbox-sound");
  const hint = root.querySelector("#sandbox-gesture-hint");
  const tuningState = root.querySelector("#sandbox-tuning-state");
  let mode = "compound";
  let drag = null;
  let animationFrame = 0;
  let previousTimestamp = performance.now();
  let previousDetent = 0;
  let audioContext = null;
  let cadViewport = createCadViewport();
  let tracePoints = [];
  const milestoneKeys = ["outwardSlide", "closedReturn", "compoundGesture", "threeDetents", "maxTravel", "sourceMapping"];
  const milestoneStorageKey = `magnetic-slide-tile-simulator-milestones:${analysisStage.analysisSpec.contractSha256}`;
  const storedMilestones = JSON.parse(localStorage.getItem(milestoneStorageKey) || "{}");
  const milestones = Object.fromEntries(milestoneKeys.map((key) => [key, Boolean(storedMilestones[key])]));
  let detentTransitions = Number(storedMilestones.detentTransitions) || 0;
  let lastRenderedTravel = 0;

  const stateLabels = {
    reset: "闭合 · 已捕获",
    closed: "闭合",
    sliding: "滑动中",
    "closed-stop": "闭合止点",
    "open-stop": "打开止点",
    "compound-motion": "滑动 + 旋转",
    held: "保持",
    "held-below-breakaway": "未越过起步门槛",
    breakaway: "已突破起步门槛",
    rotating: "旋转中",
    released: "惯性减速",
    capture: "已吸附",
    pose: "精确姿态",
    parameters: "参数已更新"
  };

  const emitClick = () => {
    if (!soundToggle.checked) return;
    audioContext ||= new AudioContext();
    const oscillator = audioContext.createOscillator();
    const gain = audioContext.createGain();
    oscillator.frequency.value = 766;
    gain.gain.setValueAtTime(0.045, audioContext.currentTime);
    gain.gain.exponentialRampToValueAtTime(0.0001, audioContext.currentTime + 0.035);
    oscillator.connect(gain).connect(audioContext.destination);
    oscillator.start();
    oscillator.stop(audioContext.currentTime + 0.04);
  };

  const renderSandbox = (snapshot = sandbox.snapshot()) => {
    const geometry = computeCadGeometry({
      travelL: snapshot.travelL,
      angleDeg: snapshot.angleDeg
    }, cadConfig);
    lowerTranslation.setAttribute("transform", `translate(0 ${geometry.lower.translation[1].toFixed(4)})`);
    lowerRotation.setAttribute(
      "transform",
      `rotate(${snapshot.angleDeg.toFixed(4)} ${geometry.axis.local[0]} ${geometry.axis.local[1]})`
    );
    fixedUpper.setAttribute("transform", "translate(0 0)");
    axisOverlay.setAttribute("transform", `translate(0 ${geometry.lower.translation[1].toFixed(4)})`);
    sideLower.setAttribute("transform", `translate(${geometry.side.lowerTranslationX.toFixed(4)} 0)`);
    sectionMoving.setAttribute("transform", `translate(${geometry.section.axisTranslationX.toFixed(4)} 0)`);
    cadViewportGroup.setAttribute("transform", cadViewportTransform(cadViewport));
    root.querySelector("#cad-zoom-value").textContent = `${Math.round(cadViewport.zoom * 100)}%`;
    root.querySelector("#cad-side-angle").textContent = `${snapshot.angleDeg.toFixed(1)}°`;
    root.querySelector("#cad-side-travel").textContent = `${snapshot.travelL.toFixed(3)}L`;
    root.querySelector("#cad-section-angle").textContent = `${snapshot.angleDeg.toFixed(1)}°`;
    root.querySelector("#cad-section-travel").textContent = `${snapshot.travelL.toFixed(3)}L`;
    pathTrace.setAttribute("points", tracePoints.map((point) => `${point[0].toFixed(2)},${point[1].toFixed(2)}`).join(" "));
    root.querySelector("#sandbox-live-travel").textContent = `+${snapshot.travelL.toFixed(3)}L`;
    root.querySelector("#sandbox-live-axis-local").textContent = `固定 · [0,+${snapshot.transforms.axis.localL[1].toFixed(3)}L] · 下端圆帽中心`;
    root.querySelector("#sandbox-live-axis").textContent = `A=[0,+${snapshot.transforms.axis.worldL[1].toFixed(3)}L] · 整体 Δ=+${snapshot.travelL.toFixed(3)}L`;
    root.querySelector("#sandbox-live-angle").textContent = `${snapshot.angleDeg.toFixed(1)}°`;
    root.querySelector("#sandbox-live-detent").textContent = `${String(snapshot.detentIndex).padStart(2, "0")} / ${cadConfig.detentCount}`;
    root.querySelector("#sandbox-live-state").textContent = stateLabels[snapshot.lastEvent] || snapshot.lastEvent;
    tuningState.textContent = snapshot.userTuned ? "用户调节值 · 未获实物验证" : "合同值 + Simulator 调校（非实物力值）";
    tuningState.classList.toggle("is-user-tuned", snapshot.userTuned);
    if (snapshot.detentIndex !== previousDetent) {
      detentTransitions += 1;
      if (snapshot.captured) emitClick();
    }
    previousDetent = snapshot.detentIndex;
    if (snapshot.travelL >= 0.03) milestones.outwardSlide = true;
    if (milestones.outwardSlide && lastRenderedTravel >= 0.03 && snapshot.travelL <= 0.005) milestones.closedReturn = true;
    if (snapshot.travelL >= snapshot.parameters.maxTravelL - 0.005) milestones.maxTravel = true;
    lastRenderedTravel = snapshot.travelL;
    root.dataset.angleDeg = snapshot.angleDeg.toFixed(3);
    root.dataset.travelL = snapshot.travelL.toFixed(3);
    updateApprovalProgress();
  };

  const persistMilestones = () => localStorage.setItem(milestoneStorageKey, JSON.stringify({
    ...milestones,
    detentTransitions
  }));

  const updateApprovalProgress = () => {
    milestones.threeDetents = detentTransitions >= 3;
    persistMilestones();
    const completed = milestoneKeys.filter((key) => milestones[key]).length;
    root.querySelectorAll("[data-milestone]").forEach((item) => {
      item.classList.toggle("is-complete", milestones[item.dataset.milestone]);
    });
    const counter = root.querySelector("#simulator-checklist-count");
    if (counter) counter.textContent = `${completed} / ${milestoneKeys.length}`;
    const status = root.querySelector("#simulator-approval-status");
    if (status) status.textContent = completed === milestoneKeys.length
      ? "交互清单已完成。现在可以确认此 Simulator。"
      : `还需完成 ${milestoneKeys.length - completed} 项。`;
    const approve = document.getElementById("approve-stage");
    if (approve) {
      approve.disabled = completed !== milestoneKeys.length;
      approve.setAttribute("aria-disabled", String(approve.disabled));
    }
    root.dataset.approvalReady = String(completed === milestoneKeys.length);
  };

  const syncControls = (snapshot) => {
    for (const input of controls) {
      input.value = snapshot.parameters[input.name];
      const output = root.querySelector(`[data-output-for="${input.name}"]`);
      if (!output) continue;
      const value = Number(input.value);
      output.textContent = input.name === "maxTravelL" || input.name === "endStopSoftness"
        ? `${value.toFixed(2)}L`
        : input.name === "inertiaHalfLife"
          ? `${value.toFixed(2)}s`
          : `${Math.round(value * 100)}%`;
    }
  };

  const animate = (timestamp) => {
    const deltaSeconds = Math.min(0.05, Math.max(0, (timestamp - previousTimestamp) / 1000));
    previousTimestamp = timestamp;
    const snapshot = sandbox.step(deltaSeconds);
    renderSandbox(snapshot);
    animationFrame = snapshot.captured ? 0 : requestAnimationFrame(animate);
  };

  const ensureAnimation = () => {
    if (animationFrame) return;
    previousTimestamp = performance.now();
    animationFrame = requestAnimationFrame(animate);
  };

  const pointInStage = (event, { applyViewport = true } = {}) => {
    const point = stage.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    const stagePoint = point.matrixTransform(stage.getScreenCTM().inverse());
    const result = applyViewport
      ? inverseCadPoint([stagePoint.x, stagePoint.y], cadViewport)
      : [stagePoint.x, stagePoint.y];
    return { x: result[0], y: result[1] };
  };

  const pointerDown = (event) => {
    if (event.button !== undefined && event.button !== 0) return;
    event.preventDefault();
    try { stage.setPointerCapture(event.pointerId); }
    catch { /* Synthetic browser checks have no native active pointer. */ }
    const point = pointInStage(event);
    const rawPoint = pointInStage(event, { applyViewport: false });
    const snapshot = sandbox.snapshot();
    const geometry = computeCadGeometry({
      travelL: snapshot.travelL,
      angleDeg: snapshot.angleDeg
    }, cadConfig);
    const ringHit = event.target.closest?.("[data-cad-rotation-ring]");
    const interaction = ringHit ? "rotate" : mode;
    const grabbedLocalPoint = lowerLocalPointFromWorld([point.x, point.y], geometry);
    drag = {
      pointerId: event.pointerId,
      interaction,
      point,
      rawPoint,
      travelL: snapshot.travelL,
      grabbedLocalPoint,
      axis: { x: geometry.axis.world[0], y: geometry.axis.world[1] },
      angle: Math.atan2(point.y - geometry.axis.world[1], point.x - geometry.axis.world[0]) * 180 / Math.PI
    };
    if (interaction === "compound") {
      tracePoints = [[point.x, point.y]];
      renderSandbox(snapshot);
    }
    root.dataset.activeInteraction = interaction;
  };

  const pointerMove = (event) => {
    if (!drag || drag.pointerId !== event.pointerId) return;
    event.preventDefault();
    const point = pointInStage(event);
    if (drag.interaction === "pan") {
      const rawPoint = pointInStage(event, { applyViewport: false });
      cadViewport = panCadViewport(
        cadViewport,
        rawPoint.x - drag.rawPoint.x,
        rawPoint.y - drag.rawPoint.y
      );
      drag.rawPoint = rawPoint;
      renderSandbox();
      return;
    }
    if (drag.interaction === "compound") {
      const current = sandbox.snapshot();
      const solved = solveCompoundDragDelta({
        previousPointer: [drag.point.x, drag.point.y],
        currentPointer: [point.x, point.y],
        travelL: current.travelL,
        angleDeg: current.angleDeg,
        grabbedLocalPoint: drag.grabbedLocalPoint,
        config: cadConfig
      });
      const lag = 1 - current.parameters.slideResistance * 0.65;
      const snapshot = sandbox.applyCompoundPointer({
        slideDeltaL: solved.slideDeltaL * lag,
        angleDeltaDeg: solved.angleDeltaDeg,
        effort: Math.max(0.65, Math.min(1, Math.abs(solved.angleDeltaDeg) / 4)),
        deltaSeconds: 1 / 60
      });
      if (Math.abs(solved.slideDeltaL) > 0.002 && Math.abs(solved.angleDeltaDeg) > 0.5) {
        milestones.compoundGesture = true;
      }
      drag.point = point;
      tracePoints.push([point.x, point.y]);
      if (tracePoints.length > 80) tracePoints.shift();
      renderSandbox(snapshot);
      return;
    }
    const currentAngle = Math.atan2(point.y - drag.axis.y, point.x - drag.axis.x) * 180 / Math.PI;
    const delta = ((currentAngle - drag.angle + 540) % 360) - 180;
    drag.angle = currentAngle;
    const effort = Math.min(1, Math.abs(delta) / 4);
    renderSandbox(sandbox.rotateByPointer(delta, effort, 1 / 60));
  };

  const pointerUp = (event) => {
    if (!drag || drag.pointerId !== event.pointerId) return;
    const interaction = drag.interaction;
    drag = null;
    root.dataset.activeInteraction = "";
    if (interaction === "rotate") {
      renderSandbox(sandbox.releaseRotation());
      ensureAnimation();
    } else if (interaction === "compound") {
      renderSandbox(sandbox.releaseCompound());
      ensureAnimation();
    }
  };

  stage.addEventListener("pointerdown", pointerDown);
  stage.addEventListener("pointermove", pointerMove);
  stage.addEventListener("pointerup", pointerUp);
  stage.addEventListener("pointercancel", pointerUp);

  for (const button of modeButtons) {
    button.addEventListener("click", () => {
      mode = button.dataset.sandboxMode;
      modeButtons.forEach((candidate) => candidate.classList.toggle("is-active", candidate === button));
      modeButtons.forEach((candidate) => candidate.setAttribute("aria-pressed", String(candidate === button)));
      hint.textContent = mode === "compound"
        ? "联动操作：直接拖动活动下片，纵向分量改变 s，切向分量同时改变 θ。"
        : "平移图纸：拖动画布；滚轮或工具栏缩放，不改变机构姿态。";
      root.dataset.mode = mode;
    });
  }

  for (const button of root.querySelectorAll("[data-cad-zoom]")) {
    button.addEventListener("click", () => {
      const action = button.dataset.cadZoom;
      cadViewport = action === "reset"
        ? createCadViewport()
        : zoomCadViewport(cadViewport, action === "in" ? 1.2 : 1 / 1.2);
      renderSandbox();
    });
  }
  stage.addEventListener("wheel", (event) => {
    event.preventDefault();
    const point = pointInStage(event, { applyViewport: false });
    cadViewport = zoomCadViewport(cadViewport, event.deltaY < 0 ? 1.12 : 1 / 1.12, [point.x, point.y]);
    renderSandbox();
  }, { passive: false });

  const setDetent = (index) => {
    if (animationFrame) cancelAnimationFrame(animationFrame);
    animationFrame = 0;
    renderSandbox(sandbox.setDetentIndex(index));
  };
  for (const button of root.querySelectorAll("[data-detent-preset]")) {
    button.addEventListener("click", () => setDetent(Number(button.dataset.detentPreset)));
  }
  for (const button of root.querySelectorAll("[data-detent-step]")) {
    button.addEventListener("click", () => {
      const snapshot = sandbox.snapshot();
      setDetent(snapshot.detentIndex + Number(button.dataset.detentStep));
    });
  }
  for (const button of root.querySelectorAll("[data-sandbox-pose]")) {
    button.addEventListener("click", () => {
      const pose = button.dataset.sandboxPose === "slide"
        ? { travelL: cadConfig.maxTravelL / 2, angleDeg: 0 }
        : { travelL: 0, angleDeg: 0 };
      renderSandbox(sandbox.setPose(pose));
    });
  }
  stage.addEventListener("keydown", (event) => {
    const snapshot = sandbox.snapshot();
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      setDetent(snapshot.detentIndex + (event.key === "ArrowRight" ? 1 : -1));
    }
    if (event.key === "ArrowUp" || event.key === "ArrowDown") {
      event.preventDefault();
      const direction = event.key === "ArrowUp" ? 1 : -1;
      renderSandbox(sandbox.setSlideTravel(snapshot.travelL + direction * 0.02));
    }
    if (event.key === "0" || event.key === "Home") {
      event.preventDefault();
      renderSandbox(sandbox.setPose({ travelL: 0, angleDeg: 0 }));
    }
  });

  for (const input of controls) {
    input.addEventListener("input", () => {
      const snapshot = sandbox.setParameters({ [input.name]: Number(input.value) });
      syncControls(snapshot);
      renderSandbox(snapshot);
    });
  }
  internalsOpacity.addEventListener("input", () => {
    const value = Number(internalsOpacity.value);
    root.style.setProperty("--sandbox-internals-opacity", value.toFixed(2));
    root.querySelector('[data-output-for="internalsOpacity"]').textContent = `${Math.round(value * 100)}%`;
    root.dataset.internalsOpacity = value.toFixed(2);
  });

  root.querySelector("#sandbox-reset").addEventListener("click", () => {
    if (animationFrame) cancelAnimationFrame(animationFrame);
    animationFrame = 0;
    tracePoints = [];
    renderSandbox(sandbox.reset());
  });
  root.querySelector("#sandbox-defaults").addEventListener("click", () => {
    if (animationFrame) cancelAnimationFrame(animationFrame);
    animationFrame = 0;
    tracePoints = [];
    const snapshot = sandbox.restoreEvidenceDefaults();
    internalsOpacity.value = "0.72";
    internalsOpacity.dispatchEvent(new Event("input", { bubbles: true }));
    syncControls(snapshot);
    renderSandbox(snapshot);
  });

  const measurementKey = "magnetic-slide-tile-physical-measurements";
  const measurementInputs = [...root.querySelectorAll("[data-cad-physical]")];
  const renderDimensions = () => {
    const values = Object.fromEntries(measurementInputs.map((input) => [
      input.dataset.cadPhysical,
      input.value.trim()
    ]));
    const dimensionState = derivePhysicalDimensions(values);
    const derived = dimensionState.derived;
    root.querySelector('[data-cad-derived="aspectRatioLW"]').textContent = derived.aspectRatioLW
      ? `${derived.aspectRatioLW.value.toFixed(3)} L/W · 用户输入`
      : "? · 待实测";
    root.querySelector('[data-cad-derived="travelL"]').textContent = derived.travelL
      ? `${derived.travelL.value.toFixed(3)}L · 用户输入`
      : "? · 待实测";
    root.querySelector('[data-cad-derived="stackResidual"]').textContent = derived.stackResidual
      ? displayDimension(derived.stackResidual.value, "mm", "user")
      : "? mm · 待实测";
    root.querySelector('[data-cad-derived="railEdgeClearance"]').textContent = derived.railEdgeClearance
      ? displayDimension(derived.railEdgeClearance.value, "mm", "user")
      : "? mm · 待实测";
    root.querySelector("#cad-dimension-length").textContent = dimensionState.inputs.overallLength
      ? `L = ${dimensionState.inputs.overallLength.toFixed(2)} mm [用户输入]`
      : "L = ? · 待实测 [未知]";
    root.querySelector("#cad-dimension-width").textContent = dimensionState.inputs.overallWidth
      ? `W = ${dimensionState.inputs.overallWidth.toFixed(2)} mm [用户输入]`
      : "W = ? · 待实测 [未知]";
    root.querySelector("#cad-dimension-thickness").textContent = dimensionState.inputs.totalThickness
      ? `总厚 ${dimensionState.inputs.totalThickness.toFixed(2)} mm [用户输入]`
      : "总厚 ? [未知]";
    root.dataset.physicalInputCount = String(Object.values(dimensionState.inputs).filter(Boolean).length);
  };
  try {
    const saved = JSON.parse(localStorage.getItem(measurementKey) || "{}");
    for (const input of measurementInputs) {
      if (saved[input.dataset.cadPhysical] !== undefined) {
        input.value = saved[input.dataset.cadPhysical];
      }
    }
  } catch {
    localStorage.removeItem(measurementKey);
  }
  for (const input of measurementInputs) {
    input.addEventListener("input", () => {
      localStorage.setItem(measurementKey, JSON.stringify(Object.fromEntries(
        measurementInputs.map((candidate) => [candidate.dataset.cadPhysical, candidate.value.trim()])
      )));
      renderDimensions();
    });
  }
  const inspector = root.querySelector("#source-constraint-inspector");
  inspector?.addEventListener("toggle", () => {
    if (inspector.open) {
      milestones.sourceMapping = true;
      updateApprovalProgress();
    }
  });
  const recording = root.querySelector("#simulator-recording-video");
  const interactionUnavailable = root.querySelector("#simulator-interaction-unavailable");
  recording?.addEventListener("ended", () => {
    if (!interactionUnavailable?.checked) return;
    for (const key of milestoneKeys) milestones[key] = true;
    updateApprovalProgress();
  });

  root.dataset.mode = mode;
  syncControls(sandbox.snapshot());
  internalsOpacity.dispatchEvent(new Event("input", { bubbles: true }));
  renderDimensions();
  renderSandbox();
  root.dataset.ready = "true";
  window.__mechanismSandbox = sandbox;
  window.__mechanismCad = {
    viewport: () => ({ ...cadViewport }),
    geometry: () => computeCadGeometry(sandbox.snapshot(), cadConfig),
    dimensions: () => derivePhysicalDimensions(Object.fromEntries(
      measurementInputs.map((input) => [input.dataset.cadPhysical, input.value.trim()])
    ))
  };
  window.__mechanismApproval = {
    milestones: () => ({ ...milestones, detentTransitions }),
    markSourceMappingOpened: () => {
      milestones.sourceMapping = true;
      updateApprovalProgress();
    },
    createPayload: () => {
      const snapshot = sandbox.snapshot();
      const simulatorAsset = state.manifest.assets.find(
        (asset) => asset.id === analysisStage.analysisSpec.simulatorArtifactId
      );
      return {
        mode: interactionUnavailable?.checked ? "recording-fallback" : "interactive-cad",
        artifactId: simulatorAsset?.id,
        artifactHash: simulatorAsset?.sha256,
        contractAssetId: analysisStage.analysisSpec.contractAssetId,
        contractHash: analysisStage.analysisSpec.contractSha256,
        parameterSnapshot: {
          ...snapshot.parameters,
          normalizedTravelL: snapshot.travelL,
          angleDeg: snapshot.angleDeg,
          endpointPivotLocalL: snapshot.transforms.axis.localToLowerL,
          endpointPivotAttachment: snapshot.transforms.axis.attachment,
          internalsOpacity: Number(internalsOpacity.value),
          physicalInputs: Object.fromEntries(
            measurementInputs.map((input) => [input.dataset.cadPhysical, input.value.trim() || null])
          )
        },
        milestones: { ...milestones, detentTransitions },
        completedInteractionChecklist: milestoneKeys.filter((key) => milestones[key]),
        browserTimestamp: new Date().toISOString()
      };
    }
  };
  updateApprovalProgress();
  state.sandboxCleanup = () => {
    if (animationFrame) cancelAnimationFrame(animationFrame);
    stage.removeEventListener("pointerdown", pointerDown);
    stage.removeEventListener("pointermove", pointerMove);
    stage.removeEventListener("pointerup", pointerUp);
    stage.removeEventListener("pointercancel", pointerUp);
    audioContext?.close();
    delete window.__mechanismSandbox;
    delete window.__mechanismCad;
    delete window.__mechanismApproval;
  };
}

function mountCadInspection() {
  const root = document.getElementById("mechanism-sandbox");
  if (!root) return;
  const analysisStage = state.manifest.stages.find((candidate) => candidate.id === "02-analysis");
  const geometryConfig = state.mechanismSimulatorConfig;
  if (!state.mechanismEvidenceContract || !geometryConfig) return;
  const config = cadConfigFromEvidenceContract(state.mechanismEvidenceContract, {
    ...geometryConfig,
    expectedContractSha256: analysisStage.analysisSpec.contractSha256
  });
  const svg = root.querySelector(".cad-stage");
  const viewportGroup = root.querySelector(".cad-viewport");
  let viewport = createCadViewport();
  let pose = { travelL: 0, angleDeg: 0 };
  let closedLimitActive = false;
  let activeEndpoint = null;
  let sweepVisible = false;
  let debugAllowInvalid = false;
  const endpointVisits = new Set();
  const inspectedViews = new Set();
  let containmentSweep = computeMinimumOverlapContainmentSweep(config);
  let mode = "compound";
  let drag = null;
  let tracePoints = [];
  let layerSeparation = 0;
  let layerOpacity = 0.62;
  const rotationTravelBuckets = new Set();
  const milestones = {
    minimumOverlapDisk: false,
    robustContainment: false,
    finiteGrooveEndpoints: false,
    synchronizedViews: false,
    pointerDirection: false,
    fixedAxis: false,
    rotatingCarrier: false,
    topUndersideGrooves: false,
    compoundMotion: false,
    pivotCoverage: false,
    smoothBottomExterior: false,
    sourceMapping: false
  };
  const requiredKeys = Object.keys(milestones);
  const pointInSvg = (event, applyViewport = true) => {
    const point = svg.createSVGPoint();
    point.x = event.clientX;
    point.y = event.clientY;
    const local = point.matrixTransform(svg.getScreenCTM().inverse());
    const result = applyViewport ? inverseCadPoint([local.x, local.y], viewport) : [local.x, local.y];
    return { x: result[0], y: result[1] };
  };
  const normalizedAngle = (value) => ((value % 360) + 360) % 360;
  const geometry = () => computeCadGeometry({ ...pose, debugAllowInvalid }, config);
  const updateChecklist = () => {
    const completed = requiredKeys.filter((key) => milestones[key]).length;
    root.querySelectorAll("[data-milestone]").forEach((item) => {
      item.classList.toggle("is-complete", milestones[item.dataset.milestone]);
    });
    root.querySelector("#cad-checklist-count").textContent = `${completed} / ${requiredKeys.length}`;
    root.querySelector("#cad-approval-status").textContent = completed === requiredKeys.length
      ? "CAD 几何检查完成。现在可以确认交互 CAD。"
      : `还需完成 ${requiredKeys.length - completed} 项 CAD 检查。`;
    const approve = document.getElementById("approve-stage");
    if (approve) {
      approve.disabled = completed !== requiredKeys.length;
      approve.setAttribute("aria-disabled", String(approve.disabled));
    }
    root.dataset.approvalReady = String(completed === requiredKeys.length);
  };
  const render = () => {
    const current = geometry();
    root.querySelectorAll(".cad-bottom-base-shell, .cad-moving-top-shell, .cad-slide-hit, .cad-actual-max-outline").forEach((path) => {
      path.setAttribute("d", current.upper.path);
    });
    root.querySelectorAll(".cad-sweep-outline").forEach((path, index) => {
      path.setAttribute("d", current.upper.path);
      path.setAttribute("transform", `rotate(${index * config.detentStepDeg} ${current.axis.world[0]} ${current.axis.world[1]}) translate(0 ${-config.maxTravelL * current.upper.length})`);
    });
    root.querySelector(".sandbox-top-motion").setAttribute(
      "transform",
      `translate(${(layerSeparation * 72).toFixed(2)} 0) ${current.top.transform}`
    );
    root.querySelector(".sandbox-top-motion").setAttribute("opacity", layerOpacity.toFixed(2));
    root.querySelector(".sandbox-fixed-bottom").setAttribute("transform", "translate(0 0)");
    root.querySelector(".cad-rotating-carrier").setAttribute("transform", current.carrier.transform);
    root.querySelector(".cad-axis-overlay").setAttribute("transform", "translate(0 0)");
    root.querySelector(".cad-actual-max-outline").setAttribute(
      "transform",
      `rotate(${pose.angleDeg.toFixed(4)} ${current.axis.world[0]} ${current.axis.world[1]}) translate(0 ${(-config.maxTravelL * current.upper.length).toFixed(4)})`
    );
    root.querySelector(".cad-side-top").setAttribute("transform", `translate(${current.side.topTranslationX.toFixed(4)} ${(-layerSeparation * 24).toFixed(2)})`);
    root.querySelector(".cad-side-bottom").setAttribute("transform", "translate(0 0)");
    root.querySelector(".cad-side-carrier").setAttribute("transform", `translate(0 ${(-layerSeparation * 12).toFixed(2)})`);
    root.querySelector(".cad-section-top").setAttribute("transform", `translate(${current.section.topTranslationX.toFixed(4)} ${(-layerSeparation * 24).toFixed(2)})`);
    root.querySelector(".cad-section-bottom").setAttribute("transform", "translate(0 0)");
    root.querySelector(".cad-underside-top").setAttribute("transform", `translate(${(pose.travelL * 120).toFixed(3)} 0)`);
    viewportGroup.setAttribute("transform", cadViewportTransform(viewport));
    root.querySelector("#cad-zoom-value").textContent = `${Math.round(viewport.zoom * 100)}%`;
    root.querySelector("#cad-side-angle").textContent = `${pose.angleDeg.toFixed(1)}°`;
    root.querySelector("#cad-side-travel").textContent = `${pose.travelL.toFixed(3)}L`;
    root.querySelector("#cad-section-angle").textContent = `${pose.angleDeg.toFixed(1)}°`;
    root.querySelector("#cad-section-travel").textContent = `${pose.travelL.toFixed(3)}L`;
    root.querySelector("#cad-path-trace").setAttribute("points", tracePoints.map((point) => `${point[0].toFixed(2)},${point[1].toFixed(2)}`).join(" "));
    root.querySelector("#sandbox-live-travel").textContent = `+${pose.travelL.toFixed(3)}L`;
    root.querySelector("#sandbox-live-axis-local").textContent = `固定 · [0,+${((current.axis.local[1] - current.upper.y) / current.upper.length).toFixed(3)}L] [图像比例]`;
    root.querySelector("#sandbox-live-axis").textContent = "固定 · Δ=(0,0)";
    root.querySelector("#sandbox-live-angle").textContent = `${pose.angleDeg.toFixed(1)}°`;
    root.querySelector("#sandbox-live-detent").textContent = `${String(Math.round(pose.angleDeg / config.detentStepDeg) % config.detentCount).padStart(2, "0")} / ${config.detentCount}`;
    root.querySelector("#sandbox-live-state").textContent = current.coverage.axisCovered
      ? `已覆盖 · 图示余量 ${current.coverage.coverResidualL.toFixed(3)}L`
      : "错误：轴心外露";
    const closedStopReadout = root.querySelector("#sandbox-live-closed-stop");
    root.querySelector("#sandbox-live-follower-u").textContent = `${current.followers.uFromTopL.toFixed(3)}L`;
    root.querySelector("#sandbox-live-distance-start").textContent = `${Math.max(0, current.followers.distanceToStartL).toFixed(3)}L`;
    root.querySelector("#sandbox-live-distance-end").textContent = `${Math.max(0, current.followers.distanceToEndL).toFixed(3)}L`;
    if (current.followers.atClosedEndpoint) endpointVisits.add("closed");
    closedStopReadout.textContent = activeEndpoint === "closed"
      ? "闭合端点 · 随动点触槽起点"
      : activeEndpoint === "open"
        ? current.minimumOverlapDisk.activeLimitingCause === "MinimumOverlapDisk"
          ? "实际最大滑开 · 圆盘边界相切"
          : "最大滑开 · 随动点触槽终点"
      : current.minimumOverlapDisk.boundaryContact && pose.travelL > 0
        ? "最小重叠圆盘 · 边界相切"
        : current.followers.atClosedEndpoint
          ? "闭合端点 · 已啮合"
          : current.followers.atOpenEndpoint
            ? "最大滑开端点 · 已啮合"
            : "槽内滑动 · 双侧啮合";
    closedStopReadout.classList.toggle("is-limit-active", Boolean(activeEndpoint));
    root.dataset.closedStopActive = String(current.closedStop.atStop);
    root.dataset.closedStopClamped = String(closedLimitActive);
    root.dataset.activeGrooveEndpoint = activeEndpoint || "";
    root.dataset.followerEngaged = String(current.followers.engaged);
    root.dataset.topAboveBottom = String(current.layerOrder.topAboveBottom);
    root.dataset.bottomMasksTop = String(current.layerOrder.bottomMasksTop);
    root.dataset.minimumOverlapCovered = String(current.minimumOverlapDisk.fullyCovered);
    root.dataset.overlapMarginL = String(current.minimumOverlapDisk.containment.marginL);
    root.dataset.activeLimitCause = current.minimumOverlapDisk.activeLimitingCause;
    root.querySelector("#sandbox-live-overlap-margin").textContent = `${current.minimumOverlapDisk.containment.marginL.toFixed(6)}L`;
    root.querySelector("#sandbox-live-derived-smax").textContent = `${current.minimumOverlapDisk.derivedSMaxL.toFixed(6)}L`;
    root.querySelector("#sandbox-live-limit-cause").textContent = current.minimumOverlapDisk.activeLimitingCause === "MinimumOverlapDisk"
      ? "最小重叠圆盘"
      : current.minimumOverlapDisk.activeLimitingCause === "FiniteGrooveEndpoint"
        ? "双槽端点"
        : "双槽端点 + 最小重叠圆盘";
    root.querySelector(".cad-minimum-overlap-disk").classList.toggle("is-invalid", !current.minimumOverlapDisk.requestedContainment.valid);
    root.querySelectorAll(".cad-minimum-overlap-fill, .cad-minimum-overlap-outline").forEach((circle) => {
      circle.setAttribute("cx", current.minimumOverlapDisk.center[0]);
      circle.setAttribute("cy", current.minimumOverlapDisk.center[1]);
      circle.setAttribute("r", current.minimumOverlapDisk.radiusPx);
    });
    root.querySelector(".cad-overlap-contact-point").setAttribute("cx", current.minimumOverlapDisk.boundaryContactWorld[0]);
    root.querySelector(".cad-overlap-contact-point").setAttribute("cy", current.minimumOverlapDisk.boundaryContactWorld[1]);
    root.dataset.travelL = pose.travelL.toFixed(3);
    root.dataset.angleDeg = pose.angleDeg.toFixed(3);
    if (
      pose.travelL >= config.maxTravelL - 0.005
      && current.minimumOverlapDisk.fullyCovered
      && current.minimumOverlapDisk.boundaryContact
    ) milestones.pivotCoverage = true;
    updateChecklist();
  };
  const pointerDown = (event) => {
    debugAllowInvalid = false;
    if (event.button !== undefined && event.button !== 0) return;
    event.preventDefault();
    try { svg.setPointerCapture(event.pointerId); } catch {}
    const point = pointInSvg(event);
    const raw = pointInSvg(event, false);
    const current = geometry();
    const ring = event.target.closest?.("[data-cad-rotation-ring]");
    const grabbedLocalPoint = topLocalPointFromWorld([point.x, point.y], current);
    drag = {
      id: event.pointerId,
      interaction: ring ? "rotate" : mode,
      point,
      raw,
      axis: current.axis.world,
      angle: Math.atan2(point.y - current.axis.world[1], point.x - current.axis.world[0]) * 180 / Math.PI,
      grabbedLocalPoint,
      grabbedWorld: topWorldPointFromLocal(grabbedLocalPoint, pose, config),
      closedStopLocked: false,
      openStopLocked: false
    };
    if (drag.interaction === "compound") tracePoints = [[point.x, point.y]];
  };
  const pointerMove = (event) => {
    if (!drag || drag.id !== event.pointerId) return;
    event.preventDefault();
    const point = pointInSvg(event);
    if (drag.interaction === "pan") {
      const raw = pointInSvg(event, false);
      viewport = panCadViewport(viewport, raw.x - drag.raw.x, raw.y - drag.raw.y);
      drag.raw = raw;
      render();
      return;
    }
    if (drag.interaction === "rotate") {
      closedLimitActive = false;
      activeEndpoint = null;
      const current = geometry();
      const angle = Math.atan2(point.y - current.axis.world[1], point.x - current.axis.world[0]) * 180 / Math.PI;
      pose.angleDeg = normalizedAngle(pose.angleDeg + (((angle - drag.angle + 540) % 360) - 180));
      drag.angle = angle;
      rotationTravelBuckets.add(Math.round(pose.travelL * 10) / 10);
    } else {
      const previousPose = { ...pose };
      const pointerDelta = [point.x - drag.point.x, point.y - drag.point.y];
      const solved = solveCompoundDragDelta({
        previousPointer: [drag.point.x, drag.point.y],
        currentPointer: [point.x, point.y],
        travelL: pose.travelL,
        angleDeg: pose.angleDeg,
        grabbedLocalPoint: drag.grabbedLocalPoint,
        config
      });
      if (!drag.openStopLocked && solved.closedClamped) drag.closedStopLocked = true;
      if (!drag.closedStopLocked && solved.openClamped) drag.openStopLocked = true;
      if (drag.closedStopLocked) solved.nextTravelL = 0;
      else if (drag.openStopLocked) solved.nextTravelL = config.maxTravelL;
      pose.travelL = solved.nextTravelL;
      pose.angleDeg = solved.nextAngleDeg;
      closedLimitActive = drag.closedStopLocked;
      activeEndpoint = drag.closedStopLocked ? "closed" : drag.openStopLocked ? "open" : null;
      if (Math.abs(solved.angleDeltaDeg) > 0.5) rotationTravelBuckets.add(Math.round(pose.travelL * 10) / 10);
      const grabbedWorld = topWorldPointFromLocal(drag.grabbedLocalPoint, pose, config);
      const actualDelta = [grabbedWorld[0] - drag.grabbedWorld[0], grabbedWorld[1] - drag.grabbedWorld[1]];
      const pointerLength = Math.hypot(...pointerDelta);
      const actualLength = Math.hypot(...actualDelta);
      const directionAgreement = pointerLength > 1 && actualLength > 1
        ? (pointerDelta[0] * actualDelta[0] + pointerDelta[1] * actualDelta[1]) / (pointerLength * actualLength)
        : 0;
      if (directionAgreement > 0.8 && solved.residualPx < 3) milestones.pointerDirection = true;
      if (
        Math.abs(pose.travelL - previousPose.travelL) > 0.005
        && Math.abs(solved.angleDeltaDeg) > 0.75
      ) milestones.compoundMotion = true;
      drag.grabbedWorld = grabbedWorld;
      drag.point = point;
      tracePoints.push([point.x, point.y]);
    }
    render();
  };
  const pointerUp = (event) => {
    if (drag?.id === event.pointerId) drag = null;
  };
  svg.addEventListener("pointerdown", pointerDown);
  svg.addEventListener("pointermove", pointerMove);
  svg.addEventListener("pointerup", pointerUp);
  svg.addEventListener("pointercancel", pointerUp);
  svg.addEventListener("keydown", (event) => {
    if (!["ArrowUp", "ArrowDown", "Home", "0"].includes(event.key)) return;
    event.preventDefault();
    if (event.key === "Home" || event.key === "0") {
      pose = { travelL: 0, angleDeg: 0 };
      closedLimitActive = false;
      activeEndpoint = null;
    } else {
      const delta = event.key === "ArrowUp" ? 0.02 : -0.02;
      const requested = pose.travelL + delta;
      pose.travelL = Math.min(config.maxTravelL, Math.max(0, requested));
      closedLimitActive = requested < 0 || (event.key === "ArrowDown" && pose.travelL === 0);
      activeEndpoint = closedLimitActive ? "closed" : requested > config.maxTravelL ? "open" : null;
    }
    render();
  });
  root.querySelectorAll("[data-sandbox-mode]").forEach((button) => button.addEventListener("click", () => {
    mode = button.dataset.sandboxMode;
    root.querySelectorAll("[data-sandbox-mode]").forEach((candidate) => candidate.classList.toggle("is-active", candidate === button));
  }));
  root.querySelectorAll("[data-cad-zoom]").forEach((button) => button.addEventListener("click", () => {
    viewport = button.dataset.cadZoom === "reset"
      ? createCadViewport()
      : zoomCadViewport(viewport, button.dataset.cadZoom === "in" ? 1.2 : 1 / 1.2);
    render();
  }));
  root.querySelector("[data-cad-sweep-toggle]")?.addEventListener("click", (event) => {
    sweepVisible = !sweepVisible;
    event.currentTarget.setAttribute("aria-pressed", String(sweepVisible));
    event.currentTarget.classList.toggle("is-active", sweepVisible);
    root.querySelector("[data-cad-sweep-envelope]")?.toggleAttribute("hidden", !sweepVisible);
    containmentSweep = computeMinimumOverlapContainmentSweep(config);
    if (
      sweepVisible
      && containmentSweep.allValid
      && containmentSweep.sampleCount === 1800
      && containmentSweep.analyticContinuous
      && containmentSweep.exactBoundaryTangency
      && containmentSweep.beyondBoundaryInvalid
    ) {
      milestones.robustContainment = true;
    }
    updateChecklist();
  });
  root.querySelector("[data-cad-overlap-inspect]")?.addEventListener("click", (event) => {
    milestones.minimumOverlapDisk = true;
    event.currentTarget.classList.add("is-active");
    updateChecklist();
  });
  root.querySelectorAll("[data-cad-view-inspect]").forEach((button) => button.addEventListener("click", () => {
    inspectedViews.add(button.dataset.cadViewInspect);
    button.classList.add("is-active");
    milestones.synchronizedViews = ["top", "side", "section"].every((view) => inspectedViews.has(view));
    updateChecklist();
  }));
  root.querySelectorAll("[data-cad-normalized]").forEach((input) => input.addEventListener("input", () => {
    const value = Number(input.value);
    if (!Number.isFinite(value)) return;
    if (input.dataset.cadNormalized === "minimumOverlapDiskRadiusL") {
      config.minimumOverlapDiskRadiusL = value;
      milestones.minimumOverlapDisk = true;
    } else if (input.dataset.cadNormalized === "grooveEndFromTopL") {
      config.grooveEndFromTopL = value;
      config.grooveLengthL = value - config.grooveStartFromTopL;
      config.grooveEndpointLimitL = config.grooveLengthL;
    } else if (input.dataset.cadNormalized === "aspectRatioLW") {
      config.aspectRatioLW = value;
    }
    refreshCadTravelBounds(config);
    pose.travelL = Math.min(pose.travelL, config.maxTravelL);
    containmentSweep = computeMinimumOverlapContainmentSweep(config);
    milestones.robustContainment = false;
    root.querySelector('[data-cad-derived="grooveLength"]').textContent = `${config.grooveEndpointLimitL.toFixed(6)}L`;
    root.querySelector('[data-cad-derived="overlapLimit"]').textContent = `${config.overlapContainmentLimitL.toFixed(6)}L`;
    root.querySelector('[data-cad-derived="actualSMax"]').textContent = `${config.maxTravelL.toFixed(6)}L · ${
      config.limitingCause === "MinimumOverlapDisk" ? "最小重叠圆盘" : config.limitingCause === "FiniteGrooveEndpoint" ? "双槽端点" : "共同限制"
    }`;
    render();
    updateChecklist();
  }));
  root.querySelectorAll("[data-detent-preset]").forEach((button) => button.addEventListener("click", () => {
    closedLimitActive = false;
    activeEndpoint = null;
    pose.angleDeg = Number(button.dataset.detentPreset) * config.detentStepDeg;
    rotationTravelBuckets.add(Math.round(pose.travelL * 10) / 10);
    render();
  }));
  root.querySelectorAll("[data-detent-step]").forEach((button) => button.addEventListener("click", () => {
    closedLimitActive = false;
    activeEndpoint = null;
    pose.angleDeg = normalizedAngle(pose.angleDeg + Number(button.dataset.detentStep) * config.detentStepDeg);
    rotationTravelBuckets.add(Math.round(pose.travelL * 10) / 10);
    render();
  }));
  root.querySelectorAll("[data-cad-pose]").forEach((button) => button.addEventListener("click", () => {
    pose = button.dataset.cadPose === "open" ? { travelL: config.maxTravelL, angleDeg: pose.angleDeg } : { travelL: 0, angleDeg: 0 };
    closedLimitActive = false;
    activeEndpoint = button.dataset.cadPose === "open" ? "open" : "closed";
    render();
  }));
  root.querySelector("#cad-reset").addEventListener("click", () => {
    pose = { travelL: 0, angleDeg: 0 };
    debugAllowInvalid = false;
    closedLimitActive = false;
    activeEndpoint = null;
    tracePoints = [];
    render();
  });
  root.querySelectorAll("[data-cad-view]").forEach((view) => {
    const mark = () => {
      milestones[`${view.dataset.cadView}View`] = true;
      updateChecklist();
    };
    view.addEventListener("click", mark);
    view.addEventListener("focus", mark);
  });
  root.querySelectorAll("[data-cad-inspect]").forEach((button) => button.addEventListener("click", () => {
    milestones[button.dataset.cadInspect] = true;
    if (button.dataset.cadInspect === "topUndersideGrooves") milestones.finiteGrooveEndpoints = true;
    button.classList.add("is-complete");
    updateChecklist();
  }));
  const separationInput = root.querySelector("#cad-layer-separation");
  const opacityInput = root.querySelector("#cad-layer-opacity");
  separationInput.addEventListener("input", () => {
    layerSeparation = Number(separationInput.value);
    root.querySelector("#cad-layer-separation-output").textContent = `${Math.round(layerSeparation * 100)}%`;
    milestones.rotatingCarrier = true;
    milestones.topUndersideGrooves = true;
    render();
  });
  opacityInput.addEventListener("input", () => {
    layerOpacity = Number(opacityInput.value);
    root.querySelector("#cad-layer-opacity-output").textContent = `${Math.round(layerOpacity * 100)}%`;
    milestones.rotatingCarrier = true;
    milestones.topUndersideGrooves = true;
    render();
  });
  const layerSelectors = {
    BottomExterior: ".cad-bottom-base-shell, .cad-lower-side, .cad-section-lower",
    FixedAxis: ".cad-axis-overlay, .cad-axis-solid, .cad-axis-bearing",
    MinimumOverlapDisk: ".cad-minimum-overlap-disk, .cad-minimum-overlap-section",
    RotatingCarrier: ".cad-rotating-carrier, .cad-side-carrier, .cad-carrier-disc",
    CarrierFollowerLeft: '[data-follower-side="left"]',
    CarrierFollowerRight: '[data-follower-side="right"]',
    TopPlate: ".sandbox-top-motion, .cad-side-top, .cad-section-top",
    TopGrooveLeft: '[data-groove-side="left"], .cad-top-groove',
    TopGrooveRight: '[data-groove-side="right"], .cad-top-groove',
    UnknownContacts: ".cad-top-unknown-contacts, .cad-hidden-candidate"
  };
  root.querySelectorAll("[data-cad-layer-toggle]").forEach((button) => button.addEventListener("click", () => {
    button.classList.toggle("is-active");
    const visible = button.classList.contains("is-active");
    root.querySelectorAll(layerSelectors[button.dataset.cadLayerToggle] || "").forEach((node) => {
      node.style.visibility = visible ? "visible" : "hidden";
    });
    if (button.dataset.cadLayerToggle === "RotatingCarrier") milestones.rotatingCarrier = true;
    if (button.dataset.cadLayerToggle.startsWith("TopGroove")) milestones.topUndersideGrooves = true;
    updateChecklist();
  }));
  const pivot = root.querySelector("[data-cad-pivot-inspect]");
  const markPivot = () => {
    milestones.fixedAxis = true;
    updateChecklist();
  };
  pivot.addEventListener("click", markPivot);
  pivot.addEventListener("focus", markPivot);
  root.querySelector(".cad-minimum-overlap-disk")?.addEventListener("click", () => {
    milestones.minimumOverlapDisk = true;
    updateChecklist();
  });
  const inspector = root.querySelector("#source-constraint-inspector");
  inspector.addEventListener("toggle", () => {
    if (inspector.open) {
      milestones.sourceMapping = true;
      updateChecklist();
    }
  });
  window.__mechanismCad = {
    viewport: () => ({ ...viewport }),
    geometry,
    pose: () => ({ ...pose }),
    setPose: (next) => {
      debugAllowInvalid = false;
      const requestedTravelL = Number(next.travelL);
      closedLimitActive = Number.isFinite(requestedTravelL) && requestedTravelL < 0;
      activeEndpoint = closedLimitActive
        ? "closed"
        : requestedTravelL > config.maxTravelL
          ? "open"
          : null;
      pose = {
        travelL: Math.min(config.maxTravelL, Math.max(0, requestedTravelL || 0)),
        angleDeg: normalizedAngle(Number(next.angleDeg) || 0)
      };
      render();
      return { ...pose };
    },
    forceDebugInvalidPose: (next = {}) => {
      debugAllowInvalid = true;
      pose = {
        travelL: Number.isFinite(Number(next.travelL)) ? Number(next.travelL) : config.maxTravelL + 0.03,
        angleDeg: normalizedAngle(Number(next.angleDeg) || 0)
      };
      render();
      return { ...pose, invalid: !geometry().minimumOverlapDisk.fullyCovered };
    },
    updateNormalizedParameters: (next = {}) => {
      for (const [key, value] of Object.entries(next)) {
        if (["minimumOverlapDiskRadiusL", "grooveEndFromTopL", "aspectRatioLW"].includes(key) && Number.isFinite(Number(value))) {
          config[key] = Number(value);
        }
      }
      config.grooveLengthL = config.grooveEndFromTopL - config.grooveStartFromTopL;
      config.grooveEndpointLimitL = config.grooveLengthL;
      refreshCadTravelBounds(config);
      pose.travelL = Math.min(pose.travelL, config.maxTravelL);
      debugAllowInvalid = false;
      render();
      return {
        maxTravelL: config.maxTravelL,
        limitingCause: config.limitingCause,
        overlapContainmentLimitL: config.overlapContainmentLimitL,
        grooveEndpointLimitL: config.grooveEndpointLimitL
      };
    }
  };
  window.__cadApproval = {
    milestones: () => ({ ...milestones, rotationTravelPositions: [...rotationTravelBuckets] }),
    createPayload: () => {
      const artifact = state.manifest.assets.find((asset) => asset.id === analysisStage.analysisSpec.cadArtifactId);
      const current = geometry();
      return {
        mode: "interactive-cad",
        artifactId: artifact.id,
        artifactHash: artifact.sha256,
        contractAssetId: analysisStage.analysisSpec.contractAssetId,
        contractHash: analysisStage.analysisSpec.contractSha256,
        geometryParameterSnapshot: {
          aspectRatioLW: config.aspectRatioLW,
          supportedTravelRangeL: config.supportedTravelRangeL,
          configuredMaxTravelL: config.maxTravelL,
          detentCount: config.detentCount,
          detentStepDeg: config.detentStepDeg,
          pose: { ...pose },
          fixedAxisBottomLocal: current.axis.localToBottom,
          fixedAxisWorld: current.axis.world,
          fixedAxisAttachment: current.axis.attachment,
          carrierTransform: current.carrier.transform,
          carrierTranslation: current.carrier.translation,
          followerCount: current.followers.count,
          grooveCount: current.grooves.count,
          grooveOwner: current.grooves.owner,
          groovesParallelToFollowers: current.grooves.parallelToFollowers,
          smoothBottomExterior: current.bottom.exposedRailCount === 0 && current.bottom.exposedGrooveCount === 0,
          axisCoveredAtCurrentPose: current.coverage.axisCovered,
          coverResidualL: current.coverage.coverResidualL,
          exactPhysicalCoverMarginKnown: current.coverage.exactPhysicalMarginKnown,
          closedStopL: current.closedStop.valueL,
          closedStopHard: current.closedStop.type === "hard-cad-kinematic",
          negativeTravelForbidden: current.closedStop.negativeTravelForbidden,
          closedSilhouetteCoincident: computeCadGeometry({ travelL: 0, angleDeg: 0 }, config).closedStop.silhouettesCoincident,
          closedStopPenetrationL: current.closedStop.penetrationL,
          grooveStartFromTopL: config.grooveStartFromTopL,
          grooveEndFromTopL: config.grooveEndFromTopL,
          grooveLengthL: config.grooveLengthL,
          grooveEndpointLimitL: config.grooveEndpointLimitL,
          overlapContainmentLimitL: config.overlapContainmentLimitL,
          actualSMaxL: config.maxTravelL,
          actualSMaxFormula: "min(grooveEndpointLimitL, overlapContainmentLimitL)",
          activeLimitingCause: config.limitingCause,
          maxTravelDerivedFromGrooveEndpoints: Math.abs(config.maxTravelL - config.grooveEndpointLimitL) < 1e-12,
          minimumOverlapDiskOwner: current.minimumOverlapDisk.owner,
          minimumOverlapDiskCenter: current.minimumOverlapDisk.center,
          minimumOverlapDiskRadiusL: current.minimumOverlapDisk.radiusL,
          minimumOverlapDiskPhysicalMm: null,
          minimumOverlapFullyCovered: current.minimumOverlapDisk.fullyCovered,
          minimumOverlapMarginL: current.minimumOverlapDisk.containment.marginL,
          overlapAngleInvariant: current.minimumOverlapDisk.angleInvariant,
          followerEngagedAtClosed: computeCadGeometry({ travelL: 0, angleDeg: 0 }, config).followers.engaged,
          followerEngagedAtOpen: computeCadGeometry({ travelL: config.maxTravelL, angleDeg: 0 }, config).followers.engaged,
          axisCoveredAtOpen: computeCadGeometry({ travelL: config.maxTravelL, angleDeg: 0 }, config).coverage.axisCovered,
          sweptEnvelopeSampleCount: containmentSweep.sampleCount,
          sweptEnvelopeAllValid: containmentSweep.allValid,
          analyticContainmentContinuous: containmentSweep.analyticContinuous,
          denseAngleSampleCount: containmentSweep.angleSampleCount,
          exactBoundaryTangency: containmentSweep.exactBoundaryTangency,
          beyondBoundaryInvalid: containmentSweep.beyondBoundaryInvalid,
          topZ: current.layerOrder.topZ,
          bottomZ: current.layerOrder.bottomZ,
          bottomMasksTop: current.layerOrder.bottomMasksTop,
          componentLayers: current.componentLayers,
          layerPresentation: { separation: layerSeparation, opacity: layerOpacity },
          physicalInputs: Object.fromEntries(
            [...root.querySelectorAll("[data-cad-physical]")].map((input) => [input.dataset.cadPhysical, input.value.trim() || null])
          )
        },
        viewsInspected: ["top", "side", "section"].filter((view) => inspectedViews.has(view)),
        milestones: { ...milestones, rotationTravelPositions: [...rotationTravelBuckets] },
        completedInteractionChecklist: requiredKeys.filter((key) => milestones[key]),
        browserTimestamp: new Date().toISOString()
      };
    }
  };
  render();
  root.dataset.ready = "true";
  root.dataset.cadOnly = "true";
  state.sandboxCleanup = () => {
    svg.removeEventListener("pointerdown", pointerDown);
    svg.removeEventListener("pointermove", pointerMove);
    svg.removeEventListener("pointerup", pointerUp);
    svg.removeEventListener("pointercancel", pointerUp);
    delete window.__mechanismCad;
    delete window.__cadApproval;
  };
}

const stageTaskLabels = {
  "01-intake": "参考素材",
  "03-contract": "尺寸与运动方案",
  "04-architecture": "拆件方案",
  "05-blockout": "白模",
  "06-geometry": "几何检查",
  "07-material": "材质",
  "08-lighting": "灯光与视角",
  "09-environment": "环境效果",
  "10-export": "3D 文件",
  "11-unity-parity": "Unity 对齐",
  "12-shipping": "手机成品画面"
};

function stageTaskHeader(stage) {
  if (stage.id === "02-analysis") return analysisActionPanel();
  if (stage.id === "03-contract") return contractActionPanel();
  if (stage.id === "04-architecture") return architectureActionPanel();
  if (stage.id === "05-blockout" && state.manifest.model.id === "magnetic-slide-tile") {
    if (stage.blockoutSpec?.revision === 6) {
      return `
        <section class="task-heading blockout-task-heading">
          <span>Gate 05 rev 6 · 底片连续平面修订</span>
          <h2>底片顶面现在是否是一整块平面，且只有独立轴座凸起？</h2>
          <p>先旋转真实 GLB，再看最大打开、平面近照、轴座低角度、四槽底面、分层结构和重叠圆盘。</p>
          <div class="blockout-scope">
            <strong>本轮只确认</strong>
            <span>完整连续 BottomExterior 顶面</span><span>无凹坑／圆碗／内陷</span><span>独立凸起 FixedAxisBoss</span><span>载体隐藏在平面下</span>
          </div>
          <small>rev 5 hierarchy 与运动学已被用户确认正确；本轮只修正底片顶皮。平面 Z=5.875 mm，1218 点最大偏差 0.000 mm。顶片四槽、18.076 mm 行程和复合运动保持不变。未进入材质、Simulator、Unity、构建或手机。</small>
        </section>
      `;
    }
    if (stage.blockoutSpec?.revision === 5) {
      return `
        <section class="task-heading blockout-task-heading">
          <span>Gate 05 rev 5 · 四轨 + 凸起轴座白模</span>
          <h2>四条底面槽、凸起轴座与旋转载体是否清楚？</h2>
          <p>先旋转真实 GLB，再看闭合、最大打开、12°、36°、四槽底面、轴座近照、分层结构和重叠圆盘。</p>
          <div class="blockout-scope">
            <strong>本轮只确认</strong>
            <span>光滑无外露轨道的 BottomExterior</span><span>凸起 FixedAxisBoss</span><span>圆形双侧开口载体</span><span>外二直推／内二轴联动</span>
          </div>
          <small>50 × 31 × 12 mm、18.076 mm 行程、2.5 mm 球候选和 2.4 mm 槽宽均为用户授权临时建模值，不是生产实测。球材质／数量、弹簧、预载、槽截面与公差仍未知。当前仅白／灰 clay；未进入材质、Unity、构建或手机。</small>
        </section>
      `;
    }
    if (stage.blockoutSpec?.revision === 4) {
      return `
        <section class="task-heading blockout-task-heading">
          <span>Gate 05 · 新 CAD 白模</span>
          <h2>白模的结构和运动方式现在对吗？</h2>
          <p>先旋转查看真实 GLB，再看闭合、最大打开、12°、36°、顶片背面双槽、分层结构和最小重叠圆盘。</p>
          <div class="blockout-scope">
            <strong>本轮只确认</strong>
            <span>固定光滑底壳</span><span>固定轴与旋转载体</span><span>顶片局部直推 + 同时旋转</span><span>18.076 mm 最大行程</span>
          </div>
          <small>50 × 31 × 12 mm 与内部数值均为用户授权临时建模值，不是生产实测。材质、图案和灯光配方已保留到后续 Gate；当前只显示白/灰 clay。Simulator、Unity 和手机均未启动。</small>
        </section>
      `;
    }
    return `
      <section class="task-heading blockout-task-heading">
        <span>现在只看白模</span>
        <h2>黄色单点轴与蓝色隐藏区，是否分清？</h2>
        <p>闭合尺寸 50 × 31 × 12 mm。直推是 +Y 21 mm／0°；旋转是 0 mm／45°，两种姿态不混用。</p>
        <div class="blockout-scope">
          <strong>本轮只确认</strong>
          <span>干净固定下层</span><span>黄色 +Z 单点轴</span><span>蓝色固定隐藏区</span><span>直推／旋转分姿态</span>
        </div>
        <small>闭合装配中心为 [0,0,0]；黄色轴点为圆端中心 [0,-9.5,0]。蓝色虚线只是固定、不渲染、无几何的 enclosure，不是旋转盘。隐藏路径与最终材质仍未建模。</small>
      </section>
    `;
  }
  if (stage.id === "06-geometry" && state.manifest.model.id === "magnetic-slide-tile") {
    return `
      <section class="task-heading geometry-task-heading">
        <span>现在只看同源几何</span>
        <h2>六视图、尺寸、单点轴和两外壳爆炸是否一致？</h2>
        <p>六个正交视图都使用同一 evaluated geometry digest；闭合 bounds 为 50 × 31 × 12 mm。</p>
        <div class="blockout-scope geometry-scope">
          <strong>本轮只确认</strong>
          <span>六个正交视图</span><span>Workbench 与尺寸</span><span>[0,-9.5,0] 单点轴</span><span>仅两外壳爆炸</span>
        </div>
        <small>两片 mesh 均为 watertight：nonmanifold edge 0、invalid normal 0；z=0 seam gap 与 volume overlap depth 都为 0 mm。隐藏 enclosure 不渲染，未新增内部零件。</small>
      </section>
    `;
  }
  if (stage.id === "07-material" && state.manifest.model.id === "magnetic-slide-tile") {
    if (stage.materialRebuildSpec?.revision === 10) {
      return `
        <section class="task-heading material-task-heading plain-unity-parity-heading">
          <span>原图对照 · Gate 07 rev 10</span>
          <h2>现在这个 Blender 材质和下片图案像原来的实物吗？</h2>
          <p>先看大幅原图对照、晶体与银边近照，再看 0°／12°／36° 轴心旋转和独立 +21 mm 滑开姿态。</p>
          <small>rev 9 只有临时视觉确认，不是正式过关。本轮仍只评审材质与图案；角度图用于把已锁定轴心一并展示清楚。</small>
          <details class="technical-details">
            <summary>技术细节</summary>
            <div class="technical-details-body">
              <p><strong>下片图案：</strong>实拍直见区与遮挡重建区分色标注；上下 Mask 的 SHA-256 不同且可独立替换。</p>
              <p><strong>红晶：</strong>深血红底、局部亮暗红晶片、颗粒微闪、透明盖层与克制角度色；Emission 与 Bloom 均为 0。</p>
              <p><strong>轴心：</strong>[0,-9.5,0] mm、+Z；0°／12°／36° 均为 12° 棘轮整数档，360° / 12° = 30。旋转平移与轴漂移均为 0 mm；45° 未作主姿态。</p>
              <p><strong>流程：</strong>第 8–11 关仍过期；第 12 关继续封锁；未运行 Unity、构建、安装或推送手机。</p>
              <div class="technical-links">
                <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-material-rev10-source-review-r010">查看原图大幅对照</button>
                <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-material-rev10-closeups-r010">查看材质近照</button>
                <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-material-rev10-axis-r010">查看轴心角度</button>
                <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-material-rev10-lower-provenance-r010">查看下片来源拆分</button>
                <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-material-rev10-validation-r010">查看验证报告</button>
              </div>
            </div>
          </details>
        </section>
      `;
    }
    if (stage.materialRebuildSpec?.revision === 9) {
      return `
        <section class="task-heading material-task-heading plain-unity-parity-heading">
          <span>原图对照 · Gate 07</span>
          <h2>现在 Blender 看起来像原来的实物了吗？</h2>
          <p>先看原图与 Blender 正面、斜面和打开状态，再看晶体、银边和黑色外圈近景。</p>
          <small>这次只重做 Blender 材质。几何、面数、尺寸、轴心、滑动方式和图案位置均未改变。</small>
          <details class="technical-details">
            <summary>技术细节</summary>
            <div class="technical-details-body">
              <p><strong>原图优先：</strong>用户实拍 01／05／10 为主标准，官方同款图只辅助判断反光行为。</p>
              <p><strong>本轮材质：</strong>深血红分层晶体、局部碎晶高光、亮暗银反射、可反光完整黑边；Emission 为 0。</p>
              <p><strong>保持锁定：</strong>几何 digest、物体矩阵、上下外部 Mask 和图案位置不变。</p>
              <p><strong>流程状态：</strong>第 8–11 关仍过期；第 12 关继续封锁；旧正式模型继续默认；未运行 Unity、构建、安装或推送手机。</p>
              <div class="technical-links">
                <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-material-original-authority-rev9-front-r009">查看 Blender 正面原图</button>
                <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-material-original-authority-rev9-crystal-r009">查看晶体原图</button>
                <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-material-original-authority-rev9-silver-r009">查看银边原图</button>
                <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-material-original-authority-rev9-fidelity-report-r009">查看验证报告</button>
              </div>
            </div>
          </details>
        </section>
      `;
    }
    if (stage.authorityAuditSpec?.revision === 8) {
      return `
        <section class="task-heading material-task-heading plain-unity-parity-heading">
          <span>先纠正外观标准</span>
          <h2>是否同意退回第 7 关，以原图为标准重做 Blender 材质？</h2>
          <p>请只看“原图标准 / Blender 当前 / Unity 当前”。现在确认的是哪一关先错，不是在批准新材质。</p>
          <small>结论：Blender 在第 7 关已把晶体层次和银色反光做平；Unity 只是继续追随了错误目标。</small>
          <details class="technical-details">
            <summary>技术细节</summary>
            <div class="technical-details-body">
              <p><strong>保持不动：</strong>外形、面数、轴心、滑动方式、图案位置和上下图案独立替换。</p>
              <p><strong>需要重做：</strong>血红晶体的亮暗碎裂与深度、亮银环境反射、黑边材质分离。</p>
              <p><strong>流程状态：</strong>第 8–11 关已过期；第 12 关继续封锁；旧正式模型继续默认。</p>
              <div class="technical-links">
                <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-material-authority-audit-rev8-original-r008">查看原图裁切</button>
                <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-material-authority-audit-rev8-blender-r008">查看 Blender 裁切</button>
                <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-material-authority-audit-rev8-unity-r008">查看 Unity 裁切</button>
                <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-material-authority-audit-rev8-report-r008">查看测量报告</button>
              </div>
            </div>
          </details>
        </section>
      `;
    }
    return `
      <section class="task-heading material-task-heading">
        <span>Gate 07 rev 7 · 全外周黑边与 D65 银白诊断</span>
        <h2>这个全外周黑色顶面边框和日光银白效果是否正确？</h2>
        <p>rev 6 已按黑边未到外周、silver 偏灰蓝的反馈不可变保留。rev 7 用独立 64 px mask 将黑边延伸到顶面 0 px 外周；结构 side/rim 保持 silver。neutral studio 与 D65 6504 K 诊断均为 Gate 7，不是 Gate 8 lighting。</p>
        <div class="blockout-scope material-scope">
          <strong>本轮只确认</strong>
          <span>全外周黑色顶面边框</span><span>黑色顶面 / silver side-rim 边界</span><span>血红而非粉红</span><span>D65 明亮中性银白</span>
        </div>
        <small>border 64 px / 10.32% / 约 3.2 mm，四边 outer inset 0 px；rev 2／3 motif SHA 8250df70…1c36 不变。D65 hero L*/C*/b* = 73.33/1/1，side = 67.45/1/1，clipping ≤0.011%。blood-red hue -6.34°，pink 0。Geometry digest 仍为 85bd7dd…bd90f；30 档保持 specified-only，Gate 8 继续阻塞。</small>
      </section>
    `;
  }
  if (stage.id === "08-lighting" && state.manifest.model.id === "magnetic-slide-tile") {
    return `
      <section class="task-heading material-task-heading">
        <span>Gate 08 rev 1 · 受控灯光与渲染层</span>
        <h2>这套灯光是否清楚展示了银色、血红晶体和结构接缝？</h2>
        <p>Gate 7 rev 7 已以原文“可以”批准。本轮只改变 Blender 灯光和相机：四灯 neutral rig、fixed EV 0、6504 K white balance 与 camera-hidden reflection cards；geometry 和获批材质不变，Gate 9 environment 尚未开始。</p>
        <div class="blockout-scope material-scope">
          <strong>本轮只确认</strong>
          <span>Hero 与左右斜视</span><span>低角和 silver side reflection</span><span>血红、黑边与 motif</span><span>Beauty / Clay / Normal / Depth / Roughness</span>
        </div>
        <small>Hero silver highlight L*/C*/b* = 77.25/0/0，left = 83.92/1/1；整图 clipping ≤0.0275%。Hero blood-red hue -2.5°，pink 0。Geometry digest 仍为 85bd7dd…bd90f。Unity reflection 仅 specified-only：URP 17.5 local probes + skybox/HDRI，非 true mirror；Gate 9/11 与真机待验。</small>
      </section>
    `;
  }
  if (stage.id === "09-environment" && state.manifest.model.id === "magnetic-slide-tile") {
    return `
      <section class="task-heading material-task-heading">
        <span>Gate 09 rev 2 · +21 mm Slide-Open</span>
        <h2>这个 +21 mm slide-open 外观是否正确？</h2>
        <p>rev 1 因“never showed the slide-open appearance”已标记 incomplete/rejected 并不可变保留。rev 2 只把上片沿 +Y 移动 21 mm，rotation 保持 0°；下片、geometry、material、Gate 8 灯光与 Gate 9 环境均不变。</p>
        <div class="blockout-scope material-scope">
          <strong>本轮只确认</strong>
          <span>neutral / shipping 同机位 open 对比</span><span>shipping open Hero / oblique</span><span>下片完整可审 motif</span><span>双片 silver reflection 与 closed→open sequence</span>
        </div>
        <small>Open pose = [0,+21,0] mm / 0°；下片 matrix 固定。下片 ROI artwork 91,714 px，contrast 1.587，Laplacian 221.65；open artwork 比 closed 多 31.2%。Hero silver L*/C*/b* = 60.39/1/0，bright reflection L* = 84.31；blood-red hue -7.5°，pink 0；clipping 0.0067%。机构继续隐藏，Gate 10 继续阻塞。</small>
      </section>
    `;
  }
  if (stage.id === "10-export" && state.manifest.model.id === "magnetic-slide-tile") {
    return `
      <section class="task-heading material-task-heading plain-round-edge-heading">
        <span>只看圆边</span>
        <h2>圆弧看起来还会不会一节一节？</h2>
        <p>先看第一张橙框找到位置，再看第二张右边的放大图。</p>
        <small>实际前后差别很小。之前明显分段的是另一张非外观图，已经从主评审移除。</small>
        <details class="technical-details">
          <summary>技术细节</summary>
          <div class="technical-details-body">
            <p>Gate 10 rev 2 的 export 文件和验证保持不变。本轮只重做评审表达。</p>
            <p>FBX 使用 FACE smoothing；source／FBX／GLB 的 side normal discontinuity 为 0°，同机位 contour delta 为 0 px。</p>
            <p>顶／底盖保持 flat；曲面侧壁保持 smooth。两个 128-triangle collision capsules 不渲染。</p>
            <div class="technical-links">
              <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-export-shading-review-board-r002">查看原技术对照</button>
              <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-arc-contour-overlay-r002">查看轮廓验证</button>
              <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-collision-non-rendering-panel-r002">查看非外观碰撞图</button>
              <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-export-glb-r002">查看 3D 文件</button>
            </div>
          </div>
        </details>
      </section>
    `;
  }
  if (stage.id === "11-unity-parity" && state.manifest.model.id === "magnetic-slide-tile") {
    return `
      <section class="task-heading material-task-heading plain-unity-parity-heading">
        <span>重新检查 Blender 与 Unity 是否像同一个物体</span>
        <h2>修正后的 Unity 现在是否像 Blender 目标？</h2>
        <p>请分开看外形、图案、银色反光和血红晶体。左边始终是 Blender，右边始终是 Unity。</p>
        <small>Gate 11 rev 3 已退回。rev 4 只改材质与黑边内宽；Gate 12 仍封锁，正式模型保持默认。</small>
        <details class="technical-details">
          <summary>技术细节</summary>
          <div class="technical-details-body">
            <p><strong>外形：</strong>同一份 4,096-triangle FBX、mesh／UV digest 与面数均未改；同机位外形重合 98.60%。</p>
            <p><strong>图案：</strong>已接受的位置和 R 通道逐字节不变。只把 Unity 黑边内宽从 64 px 缩至 42 px；外边界未移动。</p>
            <p><strong>材质：</strong>血红 Blender／Unity 中值为 124/71/73 与 109/55/57；银色改为导体环境反射；晶体加入 clearcoat、深度、折射线索和克制视角虹彩；zero emission／clipping。</p>
            <p><strong>状态：</strong>Gate 11 rev 3 与 Gate 12 rev 1 均已退回；rev 4 等待视觉确认。shipping scene、build、install、phone push 均未推进。</p>
            <div class="technical-links">
              <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-unity-parity-rev3-blender-target-r003">查看 Blender 原图</button>
              <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-unity-parity-rev4-unity-final-r004">查看 Unity 原图</button>
              <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-unity-parity-rev4-heatmap-r004">查看差异热图</button>
              <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-unity-parity-rev4-review-validation-r004">查看分项报告</button>
              <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-unity-parity-rev4-unity-report-r004">查看 Unity 报告</button>
              <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-export-glb-r002">查看导入前 3D 文件</button>
            </div>
          </div>
        </details>
      </section>
    `;
  }
  if (stage.id === "12-shipping" && state.manifest.model.id === "magnetic-slide-tile") {
    return `
      <section class="task-heading material-task-heading plain-unity-parity-heading">
        <span>最后只看真实正式场景</span>
        <h2>这套磁吸推牌外观可以作为新的正式模型吗？</h2>
        <p>请依次看多角度、滑开与旋转、手机构图。当前正式模型仍默认启用，候选模型只在受控预览开关中出现。</p>
        <small>这是真实 MeshyEDC 场景、正式相机与灯光的 Unity 图片。视觉批准待确认，未构建或推送手机。</small>
        <details class="technical-details">
          <summary>技术细节</summary>
          <div class="technical-details-body">
            <p><strong>模型：</strong>50 × 31 × 12 mm、两片 render mesh、4,096 triangles；21 mm 滑开和 30 × 12° 设置来自同一候选 settings asset。</p>
            <p><strong>安全开关：</strong>MeshyEDC.unity 内现有 EDC_Root 默认 active；Gate12Candidate 默认 inactive。图片生成后再次恢复默认状态。</p>
            <p><strong>材质：</strong>亮银使用 URP Lit + 方向连续 9-mip reflection probe；水晶用 mobile custom opaque approximation，模拟 clearcoat、背光 transmission 与 Fresnel iridescence。没有 emission。</p>
            <p><strong>未集成：</strong>候选模型尚未接入手势输入或 Haptic。当前 shipping 六档线性机制未改。iPhone HDR、性能、内存和触感均未验收。</p>
            <div class="technical-links">
              <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-gate12-report-r001">查看完整报告</button>
              <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-gate12-image-validation-r001">查看图像检查</button>
              <button type="button" class="button button-secondary" data-asset-id="magnetic-slide-tile-export-glb-r002">查看 3D 文件</button>
            </div>
          </div>
        </details>
      </section>
    `;
  }
  return `<section class="task-heading"><h2>${escapeHtml(stageTaskLabels[stage.id] || stage.contract.title)}</h2></section>`;
}

function approvalPanel(stage) {
  if (stage.status === "approved" || !stage.readiness.ready) return "";
  if (
    stage.id === "02-analysis"
    && state.manifest.model.id === "magnetic-slide-tile"
    && [9, 10, 11].includes(stage.analysisSpec?.revision)
  ) {
    const cadOnly = stage.analysisSpec.revision >= 10;
    return `
      <section class="approval-panel simulator-approval-panel">
        <h3>${cadOnly ? "只接受工作台内完成的交互 CAD 审批" : "只接受 Simulator 内完成的交互审批"}</h3>
        <p>文字、聊天确认和静态截图都不能批准本关。完成 ${cadOnly ? `${stage.analysisSpec.approvalSpec.requiredMilestones.length} 项几何检查` : "6 项清单"}后，按钮自动启用。</p>
        <button type="button" class="button button-primary" id="approve-stage" disabled aria-disabled="true">${cadOnly ? "确认交互 CAD" : "确认此 Simulator"}</button>
      </section>
    `;
  }
  if (
    stage.id === "02-analysis"
    && state.manifest.model.id === "magnetic-slide-tile"
    && [3, 4, 5, 6, 7, 8].includes(stage.analysisSpec?.revision)
  ) {
    const interactive = stage.analysisSpec.revision >= 4;
    const correctedOwnership = stage.analysisSpec.revision === 5;
    const endpointCadReview = stage.analysisSpec.revision === 7;
    const cadReview = stage.analysisSpec.revision === 6;
    const referenceResearchReview = stage.analysisSpec.revision === 8;
    return `
      <section class="approval-panel plain-unity-parity-approval">
        <h3>${referenceResearchReview ? "这些证据推导出的机构约束是否正确，足以解锁交互 CAD？" : endpointCadReview ? "固定端点轴心与原图参考入口，现在是否符合预期？" : cadReview ? "现在旋转能正常操作，CAD 机构图是否符合实物？" : correctedOwnership ? "半透明双侧滑轨与随下片移动的轴心，现在是否符合实物？" : interactive ? "在沙盒里试过后，这个滑动方向、轴心位置和 30 档旋转是否符合实物？" : "这个玩法/机构解读是否符合真实玩具？"}</h3>
        <label>${referenceResearchReview ? "如不正确，请指出哪条约束或来源映射需要改" : interactive ? "如不符合，只需指出滑动、轴心或旋转哪一项" : "如果不符合，请指出哪张板或哪个动作"}<textarea id="decision-notes" rows="3" placeholder="${referenceResearchReview ? "例如：IMG_6024 不足以支持近最大行程旋转；端点轴归属仍需改。" : interactive ? "例如：轴心应再靠近底端；接近最大滑位不能旋转。" : "例如：M/C 身份相反；闭合止点理解不对；旋转不能在这个滑位发生。"}"></textarea></label>
        <button type="button" class="button button-reject" id="reject-stage">${referenceResearchReview ? "约束或来源映射不正确" : interactive ? "沙盒与实物不符" : "不符合，退回修改"}</button>
        <button type="button" class="button button-primary" id="approve-stage">${referenceResearchReview ? "约束正确，解锁交互 CAD" : interactive ? "方向、轴心和旋转符合" : "符合真实玩具"}</button>
      </section>
    `;
  }
  if (
    stage.id === "07-material"
    && state.manifest.model.id === "magnetic-slide-tile"
    && stage.materialRebuildSpec?.revision === 10
  ) {
    return `
      <section class="approval-panel plain-unity-parity-approval">
        <h3>现在这个 Blender 材质和下片图案像原来的实物吗？</h3>
        <label>如果还不像，请直接指出原图对照中的位置<textarea id="decision-notes" rows="3" placeholder="例如：红晶微闪仍不够；下片图案右侧不像；银边太亮。"></textarea></label>
        <button type="button" class="button button-reject" id="reject-stage">还不像原来的实物</button>
        <button type="button" class="button button-primary" id="approve-stage">材质和图案像原来的实物</button>
      </section>
    `;
  }
  if (
    stage.id === "07-material"
    && state.manifest.model.id === "magnetic-slide-tile"
    && stage.materialRebuildSpec?.revision === 9
  ) {
    return `
      <section class="approval-panel plain-unity-parity-approval">
        <h3>现在 Blender 看起来像原来的实物了吗？</h3>
        <label>如果还不像，请直接指出晶体、银边、黑边或打开状态的问题<textarea id="decision-notes" rows="3" placeholder="例如：晶体还是太灰；银边亮带太硬；黑边不够有层次。"></textarea></label>
        <button type="button" class="button button-reject" id="reject-stage">还不像原来的实物</button>
        <button type="button" class="button button-primary" id="approve-stage">看起来像原来的实物</button>
      </section>
    `;
  }
  if (
    stage.id === "07-material"
    && state.manifest.model.id === "magnetic-slide-tile"
    && stage.authorityAuditSpec?.revision === 8
  ) {
    return `
      <section class="approval-panel plain-unity-parity-approval">
        <h3>是否同意退回第 7 关，以原图为标准重做 Blender 材质？</h3>
        <label>如果判断不对，请指出原图、Blender 或 Unity 的哪一处<textarea id="decision-notes" rows="3" placeholder="例如：原图银边不是这个区域；Blender 血红效果其实已经正确。"></textarea></label>
        <button type="button" class="button button-reject" id="reject-stage">这个判断不对</button>
        <button type="button" class="button button-primary" id="approve-stage">同意退回第 7 关重做</button>
      </section>
    `;
  }
  if (stage.id === "10-export" && state.manifest.model.id === "magnetic-slide-tile") {
    return `
      <section class="approval-panel plain-round-edge-approval">
        <h3>右边修复后的圆边是否连续、没有一节一节的棱角？</h3>
        <label>如果还有棱角，请指出位置<textarea id="decision-notes" rows="3" placeholder="例如：右图圆边中间还有一段折线。"></textarea></label>
        <button type="button" class="button button-reject" id="reject-stage">右边还有棱角</button>
        <button type="button" class="button button-primary" id="approve-stage">右边圆边连续</button>
      </section>
    `;
  }
  if (stage.id === "11-unity-parity" && state.manifest.model.id === "magnetic-slide-tile") {
    return `
      <section class="approval-panel plain-unity-parity-approval">
        <h3>修正后的 Unity 物体现在是否像同机位的 Blender 目标？</h3>
        <label>如果仍不像，请指出外形、图案或材质哪一项<textarea id="decision-notes" rows="3" placeholder="例如：Unity 的银色仍太暗；Unity 的上下片接缝比 Blender 粗。"></textarea></label>
        <button type="button" class="button button-reject" id="reject-stage">仍然不像同一个物体</button>
        <button type="button" class="button button-primary" id="approve-stage">现在像同一个物体</button>
      </section>
    `;
  }
  if (stage.id === "12-shipping" && state.manifest.model.id === "magnetic-slide-tile") {
    return `
      <section class="approval-panel plain-unity-parity-approval">
        <h3>这套磁吸推牌外观可以作为新的正式模型吗？</h3>
        <label>如需调整，请指出哪张图和哪个位置<textarea id="decision-notes" rows="3" placeholder="例如：低角度里银色太灰；滑开后下片图案不够清楚。"></textarea></label>
        <button type="button" class="button button-reject" id="reject-stage">还需要修改</button>
        <button type="button" class="button button-primary" id="approve-stage">外观可以作为正式模型</button>
      </section>
    `;
  }
  if (stage.id === "04-architecture" && ["motion-evidence-mapping", "concealed-circular-overlap"].includes(stage.architectureSpec?.reviewMode)) return "";
  const analysis = stage.id === "02-analysis";
  const officialAnalysis = analysis && stage.artifactIds.includes("slider-analysis-official-mechanism-board-r002");
  return `
    <section class="approval-panel">
      <label>${officialAnalysis ? "如果不是同款，请写出不同之处" : analysis ? "如有错误，请写卡片编号" : "需要修改的地方"}<textarea id="decision-notes" rows="3" placeholder="${officialAnalysis ? "例如：我的实物没有自由旋转；内部轨道与官方图不同。" : analysis ? "例如：03 没有旋转；04 两条不是滑轨。" : "写下需要保留或修改的具体内容。"}">${escapeHtml(stage.decision?.notes || "")}</textarea></label>
      <button type="button" class="button button-reject" id="reject-stage">有错误，退回修改</button>
      <button type="button" class="button button-primary" id="approve-stage">${officialAnalysis ? "是同款，按这个继续" : analysis ? "这 4 项理解正确，继续" : "确认，继续"}</button>
    </section>
  `;
}

function renderStageDetail() {
  if (state.sandboxCleanup) {
    state.sandboxCleanup();
    state.sandboxCleanup = null;
  }
  const stage = currentStage();
  const assets = currentStageAssets();
  const visibleAssets = userFacingStageAssets(stage, assets);
  const historicalAssets = historicalStageAssets(stage, assets);
  const issues = currentStageIssues().filter((issue) => issue.severity === "blocker");
  els.stageDetail.innerHTML = `
    ${stageTaskHeader(stage)}
    ${stage.id === "01-intake" ? referenceDiscoveryPanel(stage) : ""}
    ${visibleAssets.length ? `
      <section class="panel asset-panel">
        <div class="panel-heading"><h3>${[9, 10].includes(stage.materialRebuildSpec?.revision) ? "先看原图与 Blender" : stage.authorityAuditSpec?.revision === 8 ? "先看这张三方对照" : isPlainGate10Review() ? "看这两张图" : isPlainGate11Review() ? "按顺序看四张图" : "素材"}</h3><span>${visibleAssets.length} 项</span></div>
        <div class="asset-grid">${visibleAssets.map(assetCard).join("")}</div>
      </section>
    ` : ""}
    ${historicalAssets.length ? `
      <details class="panel historical-evidence" data-historical-evidence>
        <summary>历史／过期／被退回证据 · ${historicalAssets.length} 项</summary>
        <p>这些文件保留用于追溯，不代表当前方案。当前 revision 的素材在上方。</p>
        <div class="asset-grid">${historicalAssets.map(assetCard).join("")}</div>
      </details>
    ` : ""}
    ${issues.length ? `
      <section class="panel issue-panel">
        <div class="panel-heading"><h3>需要你处理</h3><span>${issues.length}</span></div>
        <div class="issue-list">${issues.map((issue) => `<article class="issue"><strong>${escapeHtml(issue.severity)} · ${escapeHtml(issue.assetId)}</strong><p>${escapeHtml(issue.note)}</p></article>`).join("")}</div>
      </section>
    ` : ""}
    ${approvalPanel(stage)}
  `;
  els.stageDetail.querySelectorAll("[data-asset-id]").forEach((button) => button.addEventListener("click", () => openAsset(button.dataset.assetId)));
  els.stageDetail.querySelectorAll("[data-review-tab]").forEach((button) => button.addEventListener("click", () => {
    const selected = button.dataset.reviewTab;
    els.stageDetail.querySelectorAll("[data-review-tab]").forEach((candidate) => {
      const active = candidate.dataset.reviewTab === selected;
      candidate.classList.toggle("is-active", active);
      candidate.setAttribute("aria-selected", String(active));
    });
    els.stageDetail.querySelectorAll("[data-review-panel]").forEach((panel) => {
      const active = panel.dataset.reviewPanel === selected;
      panel.hidden = !active;
      panel.classList.toggle("is-active", active);
    });
  }));
  document.getElementById("approve-stage")?.addEventListener("click", () => submitDecision("approve"));
  document.getElementById("reject-stage")?.addEventListener("click", () => submitDecision("reject"));
  document.getElementById("modeling-contract-form")?.addEventListener("submit", submitModelingContract);
  if (document.querySelector("[data-measurement-guide]")) bindMeasurementGuide();
  document.querySelector('[name="secondaryMotion"]')?.addEventListener("change", (event) => {
    document.getElementById("rotation-angle-field").hidden = event.target.value !== "translation-plus-rotation";
  });
  document.querySelector('[name="internalHardwareMode"]')?.addEventListener("change", (event) => {
    document.getElementById("hardware-counts").hidden = event.target.value !== "physical-teardown-replica";
  });
  if ([15, 16].includes(stage?.analysisSpec?.revision)) mountCadInspection();
  else mountMechanismSandbox();
}

function nullableFormValue(formData, name) {
  const value = String(formData.get(name) || "").trim();
  return value === "" ? null : Number(value);
}

function measurementPayloadFromForm(form) {
  const formData = new FormData(form);
  const makeEntry = (id, method = null) => ({
    valueMm: nullableFormValue(formData, `${id}ValueMm`),
    uncertaintyMm: nullableFormValue(formData, `${id}UncertaintyMm`),
    source: String(formData.get(`${id}Source`) || ""),
    method: method || String(formData.get(`${id}Method`) || ""),
    photoAssetIds: String(formData.get(`${id}PhotoReference`) || "")
      .split(",")
      .map((value) => value.trim())
      .filter(Boolean)
  });
  return {
    measurementSchemaVersion: 2,
    expectedRevision: state.manifest.revision,
    requiredMeasurements: Object.fromEntries(REQUIRED_CORE_MEASUREMENTS.map((definition) => [
      definition.id,
      makeEntry(definition.id, definition.method)
    ])),
    optionalMeasurements: Object.fromEntries(OPTIONAL_ENGINEERING_MEASUREMENTS.map((definition) => [
      definition.id,
      makeEntry(definition.id, "best-effort visible engineering measurement")
    ]))
  };
}

function bindMeasurementGuide() {
  const form = document.getElementById("modeling-contract-form");
  if (!form) return;
  const update = () => {
    const payload = measurementPayloadFromForm(form);
    const analysisStage = state.manifest.stages.find((stage) => stage.id === "02-analysis");
    const validation = validateMeasurementContract({
      requiredMeasurements: payload.requiredMeasurements,
      optionalMeasurements: payload.optionalMeasurements,
      cadConfig: {
        actualSMaxL: analysisStage.analysisSpec?.finalApproval?.geometryParameterSnapshot?.actualSMaxL
      }
    });
    const progress = document.getElementById("measurement-progress");
    if (progress) progress.textContent = `${validation.progress.complete}/9`;
    for (const { id } of REQUIRED_CORE_MEASUREMENTS) {
      form.querySelector(`[data-measurement-field="${id}"]`)?.classList.toggle("is-complete", !validation.fieldErrors[id]);
    }
    const stateLine = document.getElementById("measurement-validation-state");
    if (stateLine) {
      stateLine.className = validation.readyForModelingContractReview ? "is-valid" : "";
      stateLine.textContent = validation.errors.length
        ? validation.errors.map(({ message }) => message).join(" ")
        : validation.warnings.length
          ? validation.warnings.map(({ message }) => message).join(" ")
          : validation.progress.complete === 9
            ? "9/9 完成，一致性检查通过。"
            : `已完成 ${validation.progress.complete}/9；其余字段保持待实测。`;
    }
  };
  form.addEventListener("input", update);
  form.querySelectorAll("[data-measurement-photo]").forEach((input) => input.addEventListener("change", async () => {
    const file = input.files?.[0];
    if (!file) return;
    const fieldId = input.dataset.measurementPhoto;
    const status = form.querySelector(`[data-photo-status="${fieldId}"]`);
    if (status) status.textContent = "上传中…";
    try {
      const dataBase64 = await new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(String(reader.result).split(",")[1]);
        reader.onerror = () => reject(reader.error);
        reader.readAsDataURL(file);
      });
      const result = await api(`/api/models/${state.activeModelId}/measurement-photo`, {
        method: "POST",
        body: JSON.stringify({
          expectedRevision: state.manifest.revision,
          fieldId,
          filename: file.name,
          mimeType: file.type,
          dataBase64
        })
      });
      state.manifest = result.manifest;
      const reference = form.elements[`${fieldId}PhotoReference`];
      reference.value = [reference.value, result.assetId].filter(Boolean).join(", ");
      if (status) status.textContent = `已关联 ${result.assetId}`;
      update();
    } catch (error) {
      if (status) status.textContent = error.message;
    }
  }));
  update();
}

async function submitModelingContract(event) {
  event.preventDefault();
  if (event.currentTarget.elements.measurementSchemaVersion?.value === "2") {
    const payload = measurementPayloadFromForm(event.currentTarget);
    try {
      const result = await api(`/api/models/${state.activeModelId}/contract`, {
        method: "POST",
        body: JSON.stringify(payload)
      });
      state.manifest = result.manifest;
      state.modelingContract = result.contract;
      state.history = (await api(`/api/models/${state.activeModelId}/history`)).events;
      await refreshModelSummaries();
      render();
      showToast(result.contract.completeness.complete
        ? "9/9 与一致性检查通过；Gate 03 可进入评审"
        : `已保存 ${result.contract.completeness.requiredComplete}/9`);
    } catch (error) { showToast(error.message); }
    return;
  }
  const formData = new FormData(event.currentTarget);
  const payload = {
    expectedRevision: state.manifest.revision,
    dimensionBasisType: formData.get("dimensionBasisType"),
    overallLengthMm: nullableFormValue(formData, "overallLengthMm"),
    overallWidthMm: nullableFormValue(formData, "overallWidthMm"),
    totalThicknessMm: nullableFormValue(formData, "totalThicknessMm"),
    linearTravelMm: nullableFormValue(formData, "linearTravelMm"),
    seamClearanceMm: nullableFormValue(formData, "seamClearanceMm"),
    secondaryMotion: formData.get("secondaryMotion"),
    maxRotationDeg: nullableFormValue(formData, "maxRotationDeg"),
    laneMode: formData.get("laneMode"),
    internalHardwareMode: formData.get("internalHardwareMode"),
    magnetCount: nullableFormValue(formData, "magnetCount"),
    ballCount: nullableFormValue(formData, "ballCount"),
    steelPlateCount: nullableFormValue(formData, "steelPlateCount")
  };
  try {
    const result = await api(`/api/models/${state.activeModelId}/contract`, { method: "POST", body: JSON.stringify(payload) });
    state.manifest = result.manifest;
    state.modelingContract = result.contract;
    state.history = (await api(`/api/models/${state.activeModelId}/history`)).events;
    await refreshModelSummaries();
    render();
    showToast(result.contract.completeness.complete ? "规格已保存，可以审批这一关" : "已保存；请补齐页面标出的项目");
  } catch (error) { showToast(error.message); }
}

async function submitDecision(action) {
  const notes = document.getElementById("decision-notes")?.value.trim()
    || (action === "approve" ? "Interactive CAD geometry checklist completed." : "");
  const approvalEvidence = action === "approve"
    ? (window.__cadApproval || window.__mechanismApproval)?.createPayload()
    : null;
  try {
    state.manifest = await api(`/api/models/${state.activeModelId}/stages/${state.activeStageId}/decision`, {
      method: "POST",
      body: JSON.stringify({ expectedRevision: state.manifest.revision, action, notes, approvalEvidence })
    });
    showToast(action === "approve" ? "本关已批准" : "本关已拒绝；下游已标记过期");
    state.history = (await api(`/api/models/${state.activeModelId}/history`)).events;
    await refreshModelSummaries();
    render();
  } catch (error) { showToast(error.message); }
}

async function refreshModelSummaries() {
  const payload = await api("/api/models");
  state.models = payload.models;
}

function render() {
  document.body.classList.remove("simple-review-mode");
  document.body.classList.toggle("plain-gate10-review", isPlainGate10Review());
  document.body.classList.toggle("plain-gate11-review", isPlainGate11Review());
  els.currentModelTitle.textContent = modelDisplayName(state.manifest.model.name);
  renderNav();
  renderTaskBanner();
  renderStageRail();
  renderWorkspaceTabs();
  renderStageDetail();
  document.querySelectorAll("[data-review-tab]").forEach((button) => {
    button.addEventListener("click", () => writeWorkspaceMemory({ subview: button.dataset.reviewTab }));
  });
}

function openAsset(assetId, { pushHistory = true } = {}) {
  const asset = state.manifest.assets.find((candidate) => candidate.id === assetId);
  if (!asset) return;
  state.activeAsset = asset;
  state.annotationRegion = null;
  state.annotationEnabled = false;
  if (state.viewerCleanup) state.viewerCleanup();
  state.viewerCleanup = null;
  els.dialogSlot.textContent = asset.slot;
  els.dialogTitle.textContent = asset.id;
  els.dialogPath.textContent = asset.path;
  els.openFile.href = repoUrl(asset.path);
  els.issueForm.hidden = true;
  els.issueForm.reset();
  populateIssueClaims();
  // SVG review boards may contain linked source photos. Rendering them as an
  // <object> keeps those source photos visible; annotation remains available
  // on raster evidence where image-space coordinates are unambiguous.
  els.annotateButton.hidden = !isImage(asset) || extension(asset.path) === "svg";
  els.annotateButton.textContent = "框选问题";
  els.assetStage.innerHTML = "";
  const ext = extension(asset.path);
  if (isImage(asset)) openImageAsset(asset);
  else if (isVideo(asset)) openVideoAsset(asset);
  else if (ext === "glb") openGlbAsset(asset).catch((error) => {
    els.assetStage.innerHTML = `<div class="file-inspector"><strong>GLB 载入失败</strong><span>${escapeHtml(error.message)}</span></div>`;
  });
  else els.assetStage.innerHTML = `<div class="file-inspector"><strong>${escapeHtml(ext.toUpperCase())}</strong><span>${escapeHtml(asset.path)}</span><span>SHA-256 · ${escapeHtml(asset.sha256 || "尚未刷新")}</span></div>`;
  els.dialog.showModal();
  writeWorkspaceMemory({ assetId });
  if (pushHistory) {
    pushWorkspaceRoute({ assetId });
  }
}

function openVideoAsset(asset) {
  const video = document.createElement("video");
  video.src = repoUrl(asset.path);
  video.controls = true;
  video.preload = "metadata";
  video.playsInline = true;
  video.setAttribute("aria-label", asset.id);
  els.assetStage.appendChild(video);
}

function populateIssueClaims() {
  const claims = state.manifest.claims;
  els.issueClaim.innerHTML = '<option value="">不关联</option>' + claims.map((claim) => `<option value="${escapeHtml(claim.id)}">${escapeHtml(claim.id)} · ${escapeHtml(claim.statement)}</option>`).join("");
}

function openImageAsset(asset) {
  if (extension(asset.path) === "svg") {
    const object = document.createElement("object");
    object.data = repoUrl(asset.path);
    object.type = "image/svg+xml";
    object.setAttribute("aria-label", asset.id);
    object.innerHTML = `<a href="${repoUrl(asset.path)}" target="_blank" rel="noreferrer">打开 SVG 图</a>`;
    els.assetStage.appendChild(object);
    return;
  }
  const image = document.createElement("img");
  image.src = repoUrl(asset.path);
  image.alt = asset.id;
  image.draggable = false;
  els.assetStage.appendChild(image);
  image.addEventListener("load", () => renderIssueBoxes(image));
  let dragStart = null;
  image.addEventListener("pointerdown", (event) => {
    if (!state.annotationEnabled) return;
    event.preventDefault();
    image.setPointerCapture(event.pointerId);
    dragStart = pointInImage(event, image);
    state.annotationRegion = null;
    updateSelectionBox(image, dragStart, dragStart);
  });
  image.addEventListener("pointermove", (event) => {
    if (!dragStart || !state.annotationEnabled) return;
    updateSelectionBox(image, dragStart, pointInImage(event, image));
  });
  image.addEventListener("pointerup", (event) => {
    if (!dragStart || !state.annotationEnabled) return;
    updateSelectionBox(image, dragStart, pointInImage(event, image), true);
    dragStart = null;
  });
}

function pointInImage(event, image) {
  const rect = image.getBoundingClientRect();
  return {
    x: Math.min(1, Math.max(0, (event.clientX - rect.left) / rect.width)),
    y: Math.min(1, Math.max(0, (event.clientY - rect.top) / rect.height))
  };
}

function updateSelectionBox(image, start, end, commit = false) {
  const x = Math.min(start.x, end.x);
  const y = Math.min(start.y, end.y);
  const width = Math.abs(end.x - start.x);
  const height = Math.abs(end.y - start.y);
  let box = els.assetStage.querySelector(".annotation-box.is-current");
  if (!box) {
    box = document.createElement("div");
    box.className = "annotation-box is-current";
    els.assetStage.appendChild(box);
  }
  positionBox(box, image, { x, y, width, height });
  if (commit && width > .005 && height > .005) {
    state.annotationRegion = { x, y, width, height };
    els.selectionPreview.textContent = `已框选：x ${x.toFixed(3)} · y ${y.toFixed(3)} · w ${width.toFixed(3)} · h ${height.toFixed(3)}`;
  }
}

function positionBox(box, image, region) {
  const imageRect = image.getBoundingClientRect();
  const stageRect = els.assetStage.getBoundingClientRect();
  box.style.left = `${imageRect.left - stageRect.left + region.x * imageRect.width + els.assetStage.scrollLeft}px`;
  box.style.top = `${imageRect.top - stageRect.top + region.y * imageRect.height + els.assetStage.scrollTop}px`;
  box.style.width = `${region.width * imageRect.width}px`;
  box.style.height = `${region.height * imageRect.height}px`;
}

function renderIssueBoxes(image) {
  for (const issue of state.manifest.issues || []) {
    if (issue.assetId !== state.activeAsset.id || !issue.region || issue.status === "resolved") continue;
    const box = document.createElement("div");
    box.className = "annotation-box";
    box.title = issue.note;
    positionBox(box, image, issue.region);
    els.assetStage.appendChild(box);
  }
}

async function openGlbAsset(asset) {
  const THREE = await import("three");
  const loaderModule = await import("/vendor/three-examples/loaders/GLTFLoader.js");
  const controlsModule = await import("/vendor/three-examples/controls/OrbitControls.js");
  const { GLTFLoader } = loaderModule;
  const { OrbitControls } = controlsModule;
  const root = document.createElement("div");
  root.className = "model-viewer";
  root.innerHTML = `<div class="viewer-controls"><button type="button" data-view="front">正</button><button type="button" data-view="back">背</button><button type="button" data-view="top">上</button><button type="button" data-view="left">左</button><button type="button" data-view="right">右</button><button type="button" data-view="hero">Hero</button><label><input type="checkbox" data-wireframe> 线框</label></div>`;
  els.assetStage.appendChild(root);
  const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: false });
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
  renderer.setClearColor(0x05070a, 1);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  root.prepend(renderer.domElement);
  const scene = new THREE.Scene();
  const camera = new THREE.PerspectiveCamera(35, 1, .001, 1000);
  const controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  scene.add(new THREE.HemisphereLight(0xffffff, 0x223344, 2.2));
  const key = new THREE.DirectionalLight(0xffffff, 3.2);
  key.position.set(3, 4, 5);
  scene.add(key);
  let model = null;
  let center = new THREE.Vector3();
  let radius = 1;
  let frame = 0;
  const resize = () => {
    const width = Math.max(320, root.clientWidth);
    const height = 560;
    renderer.setSize(width, height, false);
    camera.aspect = width / height;
    camera.updateProjectionMatrix();
  };
  const placeCamera = (view) => {
    const distance = radius * 3.1;
    const directions = {
      front: [0, 0, 1], back: [0, 0, -1], top: [0, 1, .001],
      left: [-1, 0, 0], right: [1, 0, 0], hero: [1.2, .9, 1.4]
    };
    const direction = new THREE.Vector3(...(directions[view] || directions.hero)).normalize();
    camera.position.copy(center).addScaledVector(direction, distance);
    camera.near = Math.max(.001, distance / 1000);
    camera.far = distance * 20;
    camera.updateProjectionMatrix();
    controls.target.copy(center);
    controls.update();
  };
  root.querySelectorAll("[data-view]").forEach((button) => button.addEventListener("click", () => {
    placeCamera(button.dataset.view);
    writeWorkspaceMemory({ viewerView: button.dataset.view });
  }));
  root.querySelector("[data-wireframe]").addEventListener("change", (event) => {
    model?.traverse((node) => {
      if (!node.isMesh) return;
      const materials = Array.isArray(node.material) ? node.material : [node.material];
      materials.forEach((material) => { material.wireframe = event.target.checked; material.needsUpdate = true; });
    });
  });
  const observer = new ResizeObserver(resize);
  observer.observe(root);
  resize();
  new GLTFLoader().load(repoUrl(asset.path), (gltf) => {
    model = gltf.scene;
    scene.add(model);
    const box = new THREE.Box3().setFromObject(model);
    box.getCenter(center);
    radius = Math.max(box.getSize(new THREE.Vector3()).length() / 2, .001);
    placeCamera(state.workspaceMemory?.viewerView || "hero");
  }, undefined, (error) => showToast(`GLB 载入失败：${error.message}`));
  const animate = () => {
    controls.update();
    renderer.render(scene, camera);
    frame = requestAnimationFrame(animate);
  };
  animate();
  state.viewerCleanup = () => {
    cancelAnimationFrame(frame);
    observer.disconnect();
    controls.dispose();
    renderer.dispose();
    model?.traverse((node) => {
      node.geometry?.dispose?.();
      const materials = Array.isArray(node.material) ? node.material : [node.material];
      materials.filter(Boolean).forEach((material) => material.dispose?.());
    });
  };
}

async function copyText(text) {
  try { await navigator.clipboard.writeText(text); }
  catch {
    const area = document.createElement("textarea");
    area.value = text;
    document.body.appendChild(area);
    area.select();
    document.execCommand("copy");
    area.remove();
  }
}

function dismissDialog({ clearMemory = true } = {}) {
  if (state.viewerCleanup) state.viewerCleanup();
  state.viewerCleanup = null;
  state.activeAsset = null;
  state.annotationRegion = null;
  state.annotationEnabled = false;
  if (els.dialog.open) els.dialog.close();
  if (clearMemory) {
    writeWorkspaceMemory({ assetId: null });
    replaceWorkspaceRoute({ assetId: null });
  }
}

function closeDialog() {
  if (history.state?.[assetDialogHistoryKey]) {
    history.back();
    return;
  }
  dismissDialog();
}

async function submitIssue(event) {
  event.preventDefault();
  if (isImage(state.activeAsset) && !state.annotationRegion) return showToast("请先在图片上框选问题区域");
  try {
    state.manifest = await api(`/api/models/${state.activeModelId}/issues`, {
      method: "POST",
      body: JSON.stringify({
        expectedRevision: state.manifest.revision,
        stageId: state.activeAsset.stageId,
        assetId: state.activeAsset.id,
        claimIds: els.issueClaim.value ? [els.issueClaim.value] : [],
        severity: els.issueSeverity.value,
        note: els.issueNote.value,
        region: state.annotationRegion
      })
    });
    showToast("问题已保存；相关下游状态已重新计算");
    closeDialog();
    state.history = (await api(`/api/models/${state.activeModelId}/history`)).events;
    await refreshModelSummaries();
    render();
  } catch (error) { showToast(error.message); }
}

function showFatal(error) {
  document.body.innerHTML = `<main class="fatal"><h1>工作台无法连接</h1><p>${escapeHtml(error.message)}</p><p>请在仓库中运行 <code>npm --prefix tools/model-provenance-explorer start</code>，然后重新打开当前地址。</p></main>`;
}

els.dialogClose.addEventListener("click", closeDialog);
els.dialog.addEventListener("cancel", (event) => {
  event.preventDefault();
  closeDialog();
});
els.dialog.addEventListener("click", (event) => {
  if (event.target !== els.dialog) return;
  const rect = els.dialog.getBoundingClientRect();
  const outside = event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom;
  if (outside) closeDialog();
});
window.addEventListener("popstate", () => {
  const route = parseWorkspaceRoute(location.search);
  if (route.modelId && route.modelId !== state.activeModelId) {
    loadModel(route.modelId).catch(showFatal);
    return;
  }
  if (route.stageId && state.manifest?.stages.some((stage) => stage.id === route.stageId)) {
    state.activeStageId = route.stageId;
    state.activeTabId = route.tabId || tabForStage(route.stageId);
    writeWorkspaceMemory({ assetId: route.assetId || null });
    render();
  }
  if (route.assetId) openAsset(route.assetId, { pushHistory: false });
  else dismissDialog({ clearMemory: false });
});
els.copyPath.addEventListener("click", () => copyText(state.activeAsset.path).then(() => showToast("仓库路径已复制")));
els.annotateButton.addEventListener("click", () => {
  state.annotationEnabled = !state.annotationEnabled;
  els.issueForm.hidden = !state.annotationEnabled;
  els.annotateButton.textContent = state.annotationEnabled ? "取消框选" : "框选问题";
  els.selectionPreview.textContent = state.annotationEnabled ? "请在图片上拖拽框选问题区域" : "";
  if (!state.annotationEnabled) {
    state.annotationRegion = null;
    els.assetStage.querySelector(".annotation-box.is-current")?.remove();
  }
});
els.issueForm.addEventListener("submit", submitIssue);

let workspaceScrollTimer = null;
window.addEventListener("scroll", () => {
  window.clearTimeout(workspaceScrollTimer);
  workspaceScrollTimer = window.setTimeout(() => writeWorkspaceMemory({ scrollY: window.scrollY }), 120);
}, { passive: true });
window.addEventListener("beforeunload", () => writeWorkspaceMemory({ scrollY: window.scrollY }));

loadModels().catch(showFatal);
