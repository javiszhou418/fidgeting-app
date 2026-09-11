import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9226";
const baseUrl = process.env.WORKBENCH_URL || "http://127.0.0.1:8891/tools/model-provenance-explorer/";
const route = `${baseUrl}?model=magnetic-slide-tile&tab=materials&gate=09-environment`;
const screenshotPath = path.resolve("../../Artifacts/ModelProvenanceExplorer/magnetic-slide-gate09-rev8-persistent-workbench.png");
const focusedScreenshotPath = path.resolve("../../Artifacts/ModelProvenanceExplorer/magnetic-slide-gate09-rev8-workbench-focused.png");
const reportPath = path.resolve("../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/09-environment/rev-008/browser-workspace-validation.json");

const targets = await fetch(`${endpoint}/json/list`).then((response) => response.json());
const target = targets.find((candidate) => candidate.type === "page");
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
const eventually = async (expression, description, timeout = 25000) => {
  const started = Date.now();
  while (Date.now() - started < timeout) {
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
const desktop = await evaluate(`(() => ({
  activeModel: document.querySelector('[data-model-id].is-active')?.dataset.modelId,
  tabs: [...document.querySelectorAll('[data-workspace-tab] strong')].map((node) => node.textContent.trim()),
  tab: document.querySelector('[data-workspace-tab].is-active')?.dataset.workspaceTab,
  tabStatus: document.querySelector('[data-workspace-tab].is-active')?.dataset.status,
  roadmap: document.querySelectorAll('.gate-roadmap-item').length,
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  currentGate: document.querySelector('.canonical-progress')?.dataset.currentGate,
  approvedCount: document.querySelector('.canonical-progress')?.dataset.approvedCount,
  text: document.querySelector('#stage-detail')?.textContent,
  glb: Boolean(document.querySelector('[data-asset-id="magnetic-slide-tile-environment-lookdev-r008"]')),
  turntable: Boolean(document.querySelector('[data-asset-id="magnetic-slide-tile-environment-turntable-r008"]')),
  comparison: Boolean(document.querySelector('[data-asset-id="magnetic-slide-tile-environment-comparison-board-r008"]')),
  reflection: Boolean(document.querySelector('[data-asset-id="magnetic-slide-tile-environment-reflection-board-r008"]')),
  portable: Boolean(document.querySelector('[data-asset-id="magnetic-slide-tile-environment-portable-board-r008"]')),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
}))()`);
assert.equal(desktop.activeModel, "magnetic-slide-tile");
assert.deepEqual(desktop.tabs, ["参考原图", "分析（截图/视频）", "尺寸", "交互 CAD", "白模", "贴图与材质", "Unity 灯光与成品"]);
assert.equal(desktop.tab, "materials");
assert.equal(desktop.tabStatus, "current");
assert.equal(desktop.roadmap, 12);
assert.equal(desktop.stage, "09-environment");
assert.equal(desktop.currentGate, "9");
assert.equal(desktop.approvedCount, "8");
assert.match(desktop.text, /Gate 09 rev 8/);
assert.match(desktop.text, /Unity URP/);
assert.equal(desktop.glb, true);
assert.equal(desktop.turntable, true);
assert.equal(desktop.comparison, true);
assert.equal(desktop.reflection, true);
assert.equal(desktop.portable, true);
assert.ok(desktop.overflow <= 2);

await click('[data-asset-id="magnetic-slide-tile-environment-lookdev-r008"]');
await eventually(`document.querySelector('#asset-dialog[open] .model-viewer canvas')`, "Gate 09 environment GLB viewer");
await eventually(`performance.getEntriesByType('resource').some((entry) => entry.name.includes('magnetic-slide-tile-environment-r008-lookdev.glb'))`, "Gate 09 GLB request");
await click('.model-viewer [data-view="top"]');
await evaluate(`(() => {
  const mode = document.querySelector('.model-viewer [data-lighting-mode]');
  mode.value = 'shipping';
  mode.dispatchEvent(new Event('change', { bubbles: true }));
  const environment = document.querySelector('.model-viewer [data-environment]');
  environment.checked = true;
  environment.dispatchEvent(new Event('change', { bubbles: true }));
  const exposure = document.querySelector('.model-viewer [data-exposure]');
  exposure.value = '1.3';
  exposure.dispatchEvent(new Event('input', { bubbles: true }));
})()`);
const viewer = await evaluate(`(() => ({
  width: document.querySelector('.model-viewer canvas').getBoundingClientRect().width,
  modes: [...document.querySelectorAll('.model-viewer [data-lighting-mode] option')].map((option) => option.value),
  environment: Boolean(document.querySelector('.model-viewer [data-environment]')),
  exposure: Boolean(document.querySelector('.model-viewer [data-exposure]')),
  memory: JSON.parse(localStorage.getItem('fidgeting-model-workspace-v2:magnetic-slide-tile'))
}))()`);
assert.ok(viewer.width > 500);
assert.deepEqual(viewer.modes, ["neutral", "shipping"]);
assert.equal(viewer.environment, true);
assert.equal(viewer.exposure, true);
assert.equal(viewer.memory.viewerLightingMode, "shipping");
assert.equal(viewer.memory.viewerEnvironment, true);
assert.equal(viewer.memory.viewerExposure, 1.3);
assert.equal(viewer.memory.viewerView, "top");
await click("#dialog-close");
await eventually(`!document.querySelector('#asset-dialog[open]')`, "GLB modal close");

await click('[data-asset-id="magnetic-slide-tile-environment-turntable-r008"]');
await eventually(`document.querySelector('#asset-dialog[open] video')`, "real Blender environment comparison playback");
await eventually(`document.querySelector('#asset-dialog[open] video').readyState >= 1`, "turntable metadata");
const turntable = await evaluate(`(() => {
  const video = document.querySelector('#asset-dialog[open] video');
  return { duration: video.duration, width: video.videoWidth, height: video.videoHeight };
})()`);
assert.ok(turntable.duration >= 2.9);
assert.equal(turntable.width, 1440);
assert.equal(turntable.height, 590);
await evaluate(`document.querySelector('#asset-dialog').dispatchEvent(new Event('cancel', { cancelable: true }))`);
await eventually(`!document.querySelector('#asset-dialog[open]')`, "turntable modal close");

await click('[data-asset-id="magnetic-slide-tile-environment-comparison-board-r008"]');
await eventually(`document.querySelector('#asset-dialog[open] img')`, "comparison image");
await evaluate(`document.querySelector('#asset-dialog').dispatchEvent(new Event('cancel', { cancelable: true }))`);
await eventually(`!document.querySelector('#asset-dialog[open]')`, "comparison modal close");

await call("Page.reload", { ignoreCache: true });
const reload = await eventually(`(() => {
  const viewed = document.querySelector('.gate-roadmap-item.is-viewed');
  const memory = JSON.parse(localStorage.getItem('fidgeting-model-workspace-v2:magnetic-slide-tile'));
  return viewed ? {
    stage: viewed.dataset.stageId,
    tab: document.querySelector('[data-workspace-tab].is-active')?.dataset.workspaceTab,
    memoryStage: memory.stageId,
    viewerMode: memory.viewerLightingMode
  } : null;
})()`, "environment workspace reload");
assert.equal(reload.stage, "09-environment");
assert.equal(reload.tab, "materials");
assert.equal(reload.memoryStage, "09-environment");
assert.equal(reload.viewerMode, "shipping");

await call("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
await navigate(route);
const mobile = await evaluate(`(() => ({
  tabs: document.querySelectorAll('[data-workspace-tab]').length,
  roadmap: document.querySelectorAll('.gate-roadmap-item').length,
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  glb: Boolean(document.querySelector('[data-asset-id="magnetic-slide-tile-environment-lookdev-r008"]')),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  tabScroller: document.querySelector('.workspace-tabs').scrollWidth > document.querySelector('.workspace-tabs').clientWidth
}))()`);
assert.equal(mobile.tabs, 7);
assert.equal(mobile.roadmap, 12);
assert.equal(mobile.stage, "09-environment");
assert.equal(mobile.glb, true);
assert.ok(mobile.overflow <= 2);
assert.equal(mobile.tabScroller, true);

await call("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1900, deviceScaleFactor: 1, mobile: false });
await navigate(route);
await evaluate(`window.scrollTo(0, 0)`);
const screenshot = await call("Page.captureScreenshot", { format: "png", captureBeyondViewport: true });
fs.mkdirSync(path.dirname(screenshotPath), { recursive: true });
fs.writeFileSync(screenshotPath, Buffer.from(screenshot.data, "base64"));
const focused = await call("Page.captureScreenshot", {
  format: "png",
  clip: { x: 250, y: 0, width: 1190, height: 1450, scale: 1 },
  captureBeyondViewport: true
});
fs.writeFileSync(focusedScreenshotPath, Buffer.from(focused.data, "base64"));
const report = {
  pass: runtimeExceptions.length === 0 && loadingFailures.length === 0,
  desktop,
  viewer: {
    width: viewer.width,
    environmentModes: viewer.modes,
    persistedEnvironmentMode: viewer.memory.viewerLightingMode,
    persistedEnvironment: viewer.memory.viewerEnvironment,
    persistedExposure: viewer.memory.viewerExposure,
  },
  turntable,
  reload,
  mobile,
  comparisonModalClose: true,
  runtimeExceptionCount: runtimeExceptions.length,
  runtimeExceptions,
  loadingFailureCount: loadingFailures.length,
  loadingFailures,
  screenshotPath,
  focusedScreenshotPath,
};
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
assert.equal(report.pass, true);
socket.close();
console.log(JSON.stringify(report, null, 2));

