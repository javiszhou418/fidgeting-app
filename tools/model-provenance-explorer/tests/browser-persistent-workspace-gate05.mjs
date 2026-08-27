import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9224";
const baseUrl = process.env.WORKBENCH_URL || "http://127.0.0.1:8891/tools/model-provenance-explorer/";
const route = `${baseUrl}?model=magnetic-slide-tile&tab=blockout&gate=05-blockout`;
const screenshotPath = path.resolve("../../Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev6-persistent-workbench.png");
const focusedScreenshotPath = path.resolve("../../Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev6-workbench-focused.png");
const reportPath = path.resolve("../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-006/browser-workspace-validation.json");

const targets = await fetch(`${endpoint}/json/list`).then((response) => response.json());
const target = targets.find((candidate) => candidate.type === "page" && candidate.url.startsWith("http"));
assert.ok(target, "Missing browser page target.");
const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  socket.addEventListener("open", resolve, { once: true });
  socket.addEventListener("error", reject, { once: true });
});
let sequence = 0;
const pending = new Map();
const runtimeExceptions = [];
const loadingFailures = [];
socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  if (message.method === "Runtime.exceptionThrown") runtimeExceptions.push(message.params.exceptionDetails);
  if (message.method === "Network.loadingFailed" && !message.params.canceled) loadingFailures.push(message.params);
  if (!message.id || !pending.has(message.id)) return;
  const waiter = pending.get(message.id);
  pending.delete(message.id);
  if (message.error) waiter.reject(new Error(message.error.message));
  else waiter.resolve(message.result);
});
const call = (method, params = {}) => new Promise((resolve, reject) => {
  const id = ++sequence;
  pending.set(id, { resolve, reject });
  socket.send(JSON.stringify({ id, method, params }));
});
const evaluate = async (expression) => {
  const response = await call("Runtime.evaluate", { expression, awaitPromise: true, returnByValue: true });
  if (response.exceptionDetails) throw new Error(response.exceptionDetails.text || "Browser evaluation failed.");
  return response.result.value;
};
const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));
const eventually = async (expression, description, timeout = 15000) => {
  const start = Date.now();
  while (Date.now() - start < timeout) {
    const value = await evaluate(expression);
    if (value) return value;
    await delay(100);
  }
  assert.fail(`Timed out waiting for ${description}.`);
};
const click = async (selector) => {
  const point = await evaluate(`(() => {
    const node = document.querySelector(${JSON.stringify(selector)});
    if (!node) return null;
    node.scrollIntoView({ block: "center", behavior: "instant" });
    const rect = node.getBoundingClientRect();
    return { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 };
  })()`);
  assert.ok(point, `Missing ${selector}`);
  await call("Input.dispatchMouseEvent", { type: "mousePressed", ...point, button: "left", buttons: 1, clickCount: 1 });
  await call("Input.dispatchMouseEvent", { type: "mouseReleased", ...point, button: "left", buttons: 0, clickCount: 1 });
};
const navigate = async (url) => {
  await call("Page.navigate", { url });
  await eventually(`location.href === ${JSON.stringify(url)}`, "target URL");
  await eventually(`document.readyState === "complete"`, "navigation");
  await eventually(`document.querySelectorAll('[data-workspace-tab]').length === 7`, "workspace render");
};

await call("Runtime.enable");
await call("Page.enable");
await call("Network.enable");
await call("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1800, deviceScaleFactor: 1, mobile: false });
await navigate(route);

const desktop = await evaluate(`(() => ({
  modelButtons: document.querySelectorAll('[data-model-id]').length,
  activeModel: document.querySelector('[data-model-id].is-active')?.dataset.modelId,
  tabLabels: [...document.querySelectorAll('[data-workspace-tab] strong')].map((node) => node.textContent.trim()),
  activeTab: document.querySelector('[data-workspace-tab].is-active')?.dataset.workspaceTab,
  activeTabStatus: document.querySelector('[data-workspace-tab].is-active')?.dataset.status,
  roadmapCount: document.querySelectorAll('.gate-roadmap-item').length,
  viewedGate: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  currentGate: document.querySelector('.canonical-progress').dataset.currentGate,
  approvedCount: document.querySelector('.canonical-progress').dataset.approvedCount,
  taskBanner: document.querySelector('#current-task-banner').textContent,
  oldRejectedVisible: Boolean(document.querySelector('[data-asset-id="magnetic-slide-tile-blockout-interactive-r004"]')),
  priorGlbVisible: Boolean(document.querySelector('[data-asset-id="magnetic-slide-tile-blockout-interactive-r005"]')),
  newGlbVisible: Boolean(document.querySelector('[data-asset-id="magnetic-slide-tile-blockout-interactive-r006"]')),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
}))()`);
assert.ok(desktop.modelButtons >= 7);
assert.equal(desktop.activeModel, "magnetic-slide-tile");
assert.deepEqual(desktop.tabLabels, [
  "参考原图",
  "分析（截图/视频）",
  "尺寸",
  "交互 CAD",
  "白模",
  "贴图与材质",
  "Unity 灯光与成品"
]);
assert.equal(desktop.activeTab, "blockout");
assert.equal(desktop.activeTabStatus, "current");
assert.equal(desktop.roadmapCount, 12);
assert.equal(desktop.viewedGate, "05-blockout");
assert.equal(desktop.currentGate, "5");
assert.equal(desktop.approvedCount, "4");
assert.match(desktop.taskBanner, /Gate 05/);
assert.equal(desktop.oldRejectedVisible, true);
assert.equal(desktop.newGlbVisible, true);
assert.equal(desktop.priorGlbVisible, true);
assert.ok(desktop.overflow <= 2);

await click('[data-asset-id="magnetic-slide-tile-blockout-interactive-r006"]');
await eventually(`document.querySelector('#asset-dialog[open] .model-viewer canvas')`, "GLB viewer canvas");
await eventually(`performance.getEntriesByType('resource').some((entry) => entry.name.includes('magnetic-slide-tile-blockout-r006-review.glb'))`, "GLB request");
await click('.model-viewer [data-view="top"]');
const viewer = await evaluate(`(() => ({
  open: document.querySelector('#asset-dialog').open,
  canvasWidth: document.querySelector('.model-viewer canvas').getBoundingClientRect().width,
  routeHasAsset: new URL(location.href).searchParams.get('asset') === 'magnetic-slide-tile-blockout-interactive-r006',
  memoryAsset: JSON.parse(localStorage.getItem('fidgeting-model-workspace-v2:magnetic-slide-tile')).assetId,
  viewerView: JSON.parse(localStorage.getItem('fidgeting-model-workspace-v2:magnetic-slide-tile')).viewerView
}))()`);
assert.equal(viewer.open, true);
assert.ok(viewer.canvasWidth > 500);
assert.equal(viewer.routeHasAsset, true);
assert.equal(viewer.memoryAsset, "magnetic-slide-tile-blockout-interactive-r006");
assert.equal(viewer.viewerView, "top");
await click("#dialog-close");
await eventually(`!document.querySelector('#asset-dialog').open`, "GLB modal close");

await click('[data-workspace-tab="materials"]');
await eventually(`document.querySelector('[data-workspace-tab="materials"].is-active')`, "stale material tab");
const staleHistory = await evaluate(`(() => ({
  status: document.querySelector('[data-workspace-tab="materials"]').dataset.status,
  stage: document.querySelector('.gate-roadmap-item.is-viewed').dataset.stageId,
  historicalAssets: document.querySelectorAll('#stage-detail [data-asset-id]').length,
  activeTabText: document.querySelector('[data-workspace-tab="materials"] span').textContent
}))()`);
assert.equal(staleHistory.status, "stale");
assert.equal(staleHistory.stage, "07-material");
assert.ok(staleHistory.historicalAssets > 0);
assert.equal(staleHistory.activeTabText, "过期");
await call("Page.getNavigationHistory").then(async (navigation) => {
  assert.ok(navigation.entries.length >= 2);
  await call("Page.navigateToHistoryEntry", { entryId: navigation.entries[navigation.currentIndex - 1].id });
});
await eventually(`document.querySelector('[data-workspace-tab="blockout"].is-active')`, "history restoration");

await evaluate(`window.scrollTo(0, Math.min(620, document.documentElement.scrollHeight - innerHeight))`);
await delay(250);
const savedScroll = await evaluate(`JSON.parse(localStorage.getItem('fidgeting-model-workspace-v2:magnetic-slide-tile')).scrollY`);
assert.ok(savedScroll > 0);
await call("Page.reload", { ignoreCache: true });
await eventually(`document.querySelector('[data-workspace-tab="blockout"].is-active')`, "reload state");
const reload = await eventually(`(() => {
  const memory = JSON.parse(localStorage.getItem('fidgeting-model-workspace-v2:magnetic-slide-tile'));
  return document.readyState === 'complete' ? {
    tab: document.querySelector('[data-workspace-tab].is-active')?.dataset.workspaceTab,
    stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
    memoryStage: memory.stageId,
    memoryTab: memory.tabId,
    scrollY
  } : null;
})()`, "reload memory");
assert.equal(reload.tab, "blockout");
assert.equal(reload.stage, "05-blockout");
assert.equal(reload.memoryStage, "05-blockout");
assert.equal(reload.memoryTab, "blockout");
assert.ok(reload.scrollY >= savedScroll - 10);

await navigate(`${baseUrl}?model=magnetic-slide-tile&tab=unity&gate=12-shipping`);
const deepLink = await evaluate(`(() => ({
  tab: document.querySelector('[data-workspace-tab].is-active')?.dataset.workspaceTab,
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  status: document.querySelector('[data-workspace-tab="unity"]').dataset.status,
  historicalAssets: document.querySelectorAll('#stage-detail [data-asset-id]').length,
  routeGate: new URL(location.href).searchParams.get('gate')
}))()`);
assert.equal(deepLink.tab, "unity");
assert.equal(deepLink.stage, "12-shipping");
assert.equal(deepLink.status, "rejected");
assert.ok(deepLink.historicalAssets > 0);
assert.equal(deepLink.routeGate, "12-shipping");

await navigate(`${baseUrl}?model=magnetic-slide-tile&tab=analysis&gate=02-analysis`);
await eventually(`document.querySelector('[data-review-panel="references"].is-active')`, "analysis source view");
await click('[data-asset-id="slider-analysis-img-6024-playback-proxy-r003"]');
await eventually(`document.querySelector('#asset-dialog[open] video')`, "source video playback");
await click("#dialog-close");
await eventually(`!document.querySelector('#asset-dialog').open`, "video modal close");

await call("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
await navigate(route);
const mobile = await evaluate(`(() => ({
  tabs: document.querySelectorAll('[data-workspace-tab]').length,
  modelButtons: document.querySelectorAll('[data-model-id]').length,
  roadmap: document.querySelectorAll('.gate-roadmap-item').length,
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  tabScroller: document.querySelector('.workspace-tabs').scrollWidth > document.querySelector('.workspace-tabs').clientWidth,
  taskBannerWidth: document.querySelector('#current-task-banner').getBoundingClientRect().width
}))()`);
assert.equal(mobile.tabs, 7);
assert.ok(mobile.modelButtons >= 7);
assert.equal(mobile.roadmap, 12);
assert.ok(mobile.overflow <= 2);
assert.equal(mobile.tabScroller, true);
assert.ok(mobile.taskBannerWidth <= 390);

await call("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1800, deviceScaleFactor: 1, mobile: false });
await navigate(route);
await evaluate(`window.scrollTo(0, 0)`);
const layout = await call("Page.getLayoutMetrics");
const screenshot = await call("Page.captureScreenshot", {
  format: "png",
  captureBeyondViewport: true,
  clip: {
    x: 0,
    y: 0,
    width: Math.min(1440, Math.ceil(layout.cssContentSize.width)),
    height: Math.ceil(layout.cssContentSize.height),
    scale: 1
  }
});
fs.mkdirSync(path.dirname(screenshotPath), { recursive: true });
fs.writeFileSync(screenshotPath, Buffer.from(screenshot.data, "base64"));
const focused = await evaluate(`(() => {
  const node = document.querySelector('#current-task-banner');
  const tabs = document.querySelector('#workspace-tabs');
  const detail = document.querySelector('#stage-detail');
  const top = node.getBoundingClientRect().top + scrollY;
  const bottom = Math.min(detail.getBoundingClientRect().top + scrollY + 900, document.documentElement.scrollHeight);
  return { x: 0, y: top, width: 1440, height: bottom - top };
})()`);
const focusedShot = await call("Page.captureScreenshot", {
  format: "png",
  captureBeyondViewport: true,
  clip: { ...focused, scale: 1 }
});
fs.writeFileSync(focusedScreenshotPath, Buffer.from(focusedShot.data, "base64"));

const report = {
  schemaVersion: 1,
  pass: runtimeExceptions.length === 0 && loadingFailures.length === 0,
  route,
  desktop,
  viewer,
  staleHistory,
  reload,
  deepLink,
  mobile,
  sourcePlayback: true,
  screenshot: screenshotPath,
  focusedScreenshot: focusedScreenshotPath,
  runtimeExceptionCount: runtimeExceptions.length,
  loadingFailureCount: loadingFailures.length
};
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
assert.equal(report.pass, true);
socket.close();
console.log(JSON.stringify({
  pass: true,
  screenshot: screenshotPath,
  focusedScreenshot: focusedScreenshotPath,
  report: reportPath
}, null, 2));

