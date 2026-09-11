import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9242";
const baseUrl = process.env.WORKBENCH_URL || "http://127.0.0.1:8891/tools/model-provenance-explorer/";
const route = `${baseUrl}?model=magnetic-slide-tile&tab=materials&gate=07-material`;
const screenshotPath = path.resolve("../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-012/gate07-r012-persistent-workbench.png");
const focusedScreenshotPath = path.resolve("../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-012/gate07-r012-workbench-focused.png");
const reportPath = path.resolve("../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-012/browser-workspace-validation.json");

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
const eventually = async (expression, description, timeout = 20000) => {
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
  await eventually(`document.readyState === "complete"`, "navigation");
  await eventually(`document.querySelectorAll('[data-workspace-tab]').length === 7`, "workspace render");
};

await call("Runtime.enable");
await call("Page.enable");
await call("Network.enable");
await call("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1900, deviceScaleFactor: 1, mobile: false });
await navigate(route);
console.log("gate07-browser: desktop loaded");
const desktop = await evaluate(`(() => ({
  activeModel: document.querySelector('[data-model-id].is-active')?.dataset.modelId,
  tabLabels: [...document.querySelectorAll('[data-workspace-tab] strong')].map((node) => node.textContent.trim()),
  activeTab: document.querySelector('[data-workspace-tab].is-active')?.dataset.workspaceTab,
  activeTabStatus: document.querySelector('[data-workspace-tab].is-active')?.dataset.status,
  roadmapCount: document.querySelectorAll('.gate-roadmap-item').length,
  viewedGate: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  currentGate: document.querySelector('.canonical-progress').dataset.currentGate,
  approvedCount: document.querySelector('.canonical-progress').dataset.approvedCount,
  taskText: document.querySelector('#stage-detail').textContent,
  glb: Boolean(document.querySelector('[data-asset-id="magnetic-slide-tile-material-lookdev-r012"]')),
  turntable: Boolean(document.querySelector('[data-asset-id="magnetic-slide-tile-material-turntable-r012"]')),
  source: Boolean(document.querySelector('[data-asset-id="magnetic-slide-tile-material-source-comparison-r012"]')),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
}))()`);
assert.equal(desktop.activeModel, "magnetic-slide-tile");
assert.deepEqual(desktop.tabLabels, [
  "参考原图", "分析（截图/视频）", "尺寸", "交互 CAD", "白模", "贴图与材质", "Unity 灯光与成品"
]);
assert.equal(desktop.activeTab, "materials");
assert.equal(desktop.activeTabStatus, "current");
assert.equal(desktop.roadmapCount, 12);
assert.equal(desktop.viewedGate, "07-material");
assert.equal(desktop.currentGate, "7");
assert.equal(desktop.approvedCount, "6");
assert.match(desktop.taskText, /Gate 07 rev 12/);
assert.equal(desktop.glb, true);
assert.equal(desktop.turntable, true);
assert.equal(desktop.source, true);
assert.ok(desktop.overflow <= 2);
console.log("gate07-browser: desktop validated");

await click('[data-asset-id="magnetic-slide-tile-material-lookdev-r012"]');
await eventually(`document.querySelector('#asset-dialog[open] .model-viewer canvas')`, "Gate 07 material GLB viewer");
await eventually(`performance.getEntriesByType('resource').some((entry) => entry.name.includes('magnetic-slide-tile-material-r012-lookdev.glb'))`, "Gate 07 GLB request");
await click('.model-viewer [data-view="top"]');
await evaluate(`(() => {
  const environment = document.querySelector('.model-viewer [data-environment]');
  environment.checked = false;
  environment.dispatchEvent(new Event('change', { bubbles: true }));
  const exposure = document.querySelector('.model-viewer [data-exposure]');
  exposure.value = '1.6';
  exposure.dispatchEvent(new Event('input', { bubbles: true }));
})()`);
const viewer = await evaluate(`(() => ({
  width: document.querySelector('.model-viewer canvas').getBoundingClientRect().width,
  environmentControl: Boolean(document.querySelector('.model-viewer [data-environment]')),
  exposureControl: Boolean(document.querySelector('.model-viewer [data-exposure]')),
  memory: JSON.parse(localStorage.getItem('fidgeting-model-workspace-v2:magnetic-slide-tile'))
}))()`);
assert.ok(viewer.width > 500);
assert.equal(viewer.environmentControl, true);
assert.equal(viewer.exposureControl, true);
assert.equal(viewer.memory.viewerEnvironment, false);
assert.equal(viewer.memory.viewerExposure, 1.6);
assert.equal(viewer.memory.viewerView, "top");
console.log("gate07-browser: viewer validated");
await click("#dialog-close");

await click('[data-asset-id="magnetic-slide-tile-material-turntable-r012"]');
await eventually(`document.querySelector('#asset-dialog[open] video')`, "real Blender turntable playback");
await click("#dialog-close");
console.log("gate07-browser: turntable validated");

await call("Page.reload", { ignoreCache: true });
const reload = await eventually(`(() => {
  const viewed = document.querySelector('.gate-roadmap-item.is-viewed');
  const memory = JSON.parse(localStorage.getItem('fidgeting-model-workspace-v2:magnetic-slide-tile'));
  return viewed ? {
    stage: viewed.dataset.stageId,
    tab: document.querySelector('[data-workspace-tab].is-active').dataset.workspaceTab,
    memoryStage: memory.stageId,
    memoryTab: memory.tabId
  } : null;
})()`, "material workspace reload");
assert.equal(reload.stage, "07-material");
assert.equal(reload.tab, "materials");
assert.equal(reload.memoryStage, "07-material");
assert.equal(reload.memoryTab, "materials");
console.log("gate07-browser: reload validated");

await call("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
await navigate(route);
const mobile = await evaluate(`(() => ({
  tabs: document.querySelectorAll('[data-workspace-tab]').length,
  roadmap: document.querySelectorAll('.gate-roadmap-item').length,
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  glb: Boolean(document.querySelector('[data-asset-id="magnetic-slide-tile-material-lookdev-r012"]')),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  tabScroller: document.querySelector('.workspace-tabs').scrollWidth > document.querySelector('.workspace-tabs').clientWidth
}))()`);
assert.equal(mobile.tabs, 7);
assert.equal(mobile.roadmap, 12);
assert.equal(mobile.stage, "07-material");
assert.equal(mobile.glb, true);
assert.ok(mobile.overflow <= 2);
assert.equal(mobile.tabScroller, true);
console.log("gate07-browser: mobile validated");

await call("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1900, deviceScaleFactor: 1, mobile: false });
await navigate(route);
await evaluate(`window.scrollTo(0, 0)`);
const screenshot = await call("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
fs.mkdirSync(path.dirname(screenshotPath), { recursive: true });
fs.writeFileSync(screenshotPath, Buffer.from(screenshot.data, "base64"));
const focused = await call("Page.captureScreenshot", {
  format: "png",
  clip: { x: 250, y: 0, width: 1190, height: 1400, scale: 1 },
  captureBeyondViewport: true
});
fs.writeFileSync(focusedScreenshotPath, Buffer.from(focused.data, "base64"));
const report = {
  pass: runtimeExceptions.length === 0 && loadingFailures.length === 0,
  desktop,
  viewer: {
    width: viewer.width,
    environmentControl: viewer.environmentControl,
    exposureControl: viewer.exposureControl,
    persistedEnvironment: viewer.memory.viewerEnvironment,
    persistedExposure: viewer.memory.viewerExposure,
  },
  reload,
  mobile,
  turntablePlayback: true,
  sourcePlayback: "out-of-scope-prior-evidence",
  runtimeExceptionCount: runtimeExceptions.length,
  loadingFailureCount: loadingFailures.length,
  screenshotPath,
  focusedScreenshotPath,
};
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
assert.equal(report.pass, true);
socket.close();
console.log(JSON.stringify(report, null, 2));

