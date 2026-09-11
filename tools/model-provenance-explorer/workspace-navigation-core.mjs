export const WORKSPACE_TABS = Object.freeze([
  { id: "references", label: "参考原图", stageIds: ["01-intake"] },
  { id: "analysis", label: "分析（截图/视频）", stageIds: ["02-analysis"] },
  { id: "dimensions", label: "尺寸", stageIds: ["03-contract"] },
  { id: "cad", label: "交互 CAD", stageIds: ["02-analysis", "04-architecture"] },
  { id: "blockout", label: "白模", stageIds: ["05-blockout", "06-geometry"] },
  { id: "materials", label: "贴图与材质", stageIds: ["07-material", "08-lighting", "09-environment", "10-export"] },
  { id: "unity", label: "Unity 灯光与成品", stageIds: ["11-unity-parity", "12-shipping"] }
]);

const TAB_IDS = new Set(WORKSPACE_TABS.map((tab) => tab.id));

export function tabForStage(stageId) {
  return WORKSPACE_TABS.find((tab) => tab.stageIds.includes(stageId))?.id || "references";
}

export function stageForTab(tabId, manifest) {
  const tab = WORKSPACE_TABS.find((candidate) => candidate.id === tabId) || WORKSPACE_TABS[0];
  const current = manifest.stages.find((stage) => stage.id === manifest.currentStageId);
  if (current && tab.stageIds.includes(current.id)) return current.id;
  return tab.stageIds.find((stageId) => manifest.stages.some((stage) => stage.id === stageId))
    || manifest.stages[0].id;
}

export function workspaceTabStatus(tab, manifest) {
  const stages = tab.stageIds
    .map((stageId) => manifest.stages.find((stage) => stage.id === stageId))
    .filter(Boolean);
  if (stages.some((stage) => stage.id === manifest.currentStageId)) return "current";
  if (stages.some((stage) => stage.status === "rejected")) return "rejected";
  if (stages.some((stage) => stage.status === "stale")) return "stale";
  if (stages.length && stages.every((stage) => stage.status === "approved")) return "approved";
  if (stages.some((stage) => ["ready_for_review", "draft", "blocked"].includes(stage.status))) return "pending";
  return "unstarted";
}

export function parseWorkspaceRoute(search) {
  const query = new URLSearchParams(search || "");
  return {
    modelId: query.get("model"),
    tabId: query.get("tab"),
    stageId: query.get("gate"),
    assetId: query.get("asset")
  };
}

export function resolveWorkspaceLocation({ route = {}, memory = {}, manifest }) {
  const validStage = (stageId) => manifest.stages.some((stage) => stage.id === stageId);
  const explicitStageId = validStage(route.stageId) ? route.stageId : null;
  const explicitTabId = TAB_IDS.has(route.tabId) ? route.tabId : null;
  const memoryStageId = validStage(memory.stageId) ? memory.stageId : null;
  const memoryTabId = TAB_IDS.has(memory.tabId) ? memory.tabId : null;
  const stageId = explicitStageId
    || (explicitTabId ? stageForTab(explicitTabId, manifest) : null)
    || memoryStageId
    || (memoryTabId ? stageForTab(memoryTabId, manifest) : null)
    || (validStage(manifest.currentStageId) ? manifest.currentStageId : null)
    || manifest.stages[0].id;
  return {
    stageId,
    tabId: explicitTabId || (explicitStageId ? tabForStage(explicitStageId) : null) || memoryTabId || tabForStage(stageId),
    assetId: route.assetId || memory.assetId || null,
    scrollY: Number.isFinite(Number(memory.scrollY)) ? Math.max(0, Number(memory.scrollY)) : 0,
    subview: memory.subview || null,
    viewerView: memory.viewerView || "hero",
    explicit: Boolean(explicitStageId || explicitTabId)
  };
}

export function buildWorkspaceRoute({ modelId, tabId, stageId, assetId = null }) {
  const query = new URLSearchParams();
  query.set("model", modelId);
  query.set("tab", tabId);
  query.set("gate", stageId);
  if (assetId) query.set("asset", assetId);
  return `?${query.toString()}`;
}

