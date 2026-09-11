import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9257";
const baseUrl = process.env.WORKBENCH_URL
  || "http://127.0.0.1:8891/tools/model-provenance-explorer/";
const route = `${baseUrl}?model=magnetic-slide-tile&tab=materials&gate=09-environment`;
const lookdevId = "magnetic-slide-tile-environment-lookdev-r009";
const videoId = "magnetic-slide-tile-environment-turntable-r009";
const boardId = "magnetic-slide-tile-environment-comparison-board-r009";
const deepLink = `${route}&asset=${lookdevId}`;
const evidence = path.resolve(
  "../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/09-environment/rev-009",
);
const reportPath = path.join(evidence, "browser-validation.json");
const desktopScreenshot = path.join(evidence, "gate09-r009-persistent-workbench.png");
const glbScreenshot = path.join(evidence, "gate09-r009-interactive-lookdev.png");
const mobileScreenshot = path.join(evidence, "gate09-r009-mobile-workbench.png");

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
  if (message.method === "Runtime.exceptionThrown") {
    runtimeExceptions.push(message.params.exceptionDetails);
  }
  if (message.method === "Network.loadingFailed" && !message.params.canceled) {
    loadingFailures.push(message.params);
  }
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
  const response = await call("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (response.exceptionDetails) throw new Error(response.exceptionDetails.text);
  return response.result.value;
};
const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));
const eventually = async (expression, description, timeout = 30000) => {
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
  await call("Input.dispatchMouseEvent", {
    type: "mousePressed", ...point, button: "left", buttons: 1, clickCount: 1,
  });
  await call("Input.dispatchMouseEvent", {
    type: "mouseReleased", ...point, button: "left", buttons: 0, clickCount: 1,
  });
};
const navigate = async (url) => {
  await call("Page.navigate", { url });
  await eventually("document.readyState === 'complete'", "navigation");
  await eventually("document.querySelectorAll('[data-workspace-tab]').length === 7", "workspace");
};
const screenshot = async (output, captureBeyondViewport = false) => {
  const result = await call("Page.captureScreenshot", {
    format: "png",
    fromSurface: true,
    captureBeyondViewport,
  });
  fs.writeFileSync(output, Buffer.from(result.data, "base64"));
};

await call("Runtime.enable");
await call("Page.enable");
await call("Network.enable");
await call("Emulation.setDeviceMetricsOverride", {
  width: 1440,
  height: 1900,
  deviceScaleFactor: 1,
  mobile: false,
});
await navigate(route);
const desktop = await evaluate(`(() => ({
  activeModel: document.querySelector('[data-model-id].is-active')?.dataset.modelId,
  tabLabels: [...document.querySelectorAll('[data-workspace-tab] strong')].map((node) => node.textContent.trim()),
  activeTab: document.querySelector('[data-workspace-tab].is-active')?.dataset.workspaceTab,
  activeTabStatus: document.querySelector('[data-workspace-tab].is-active')?.dataset.status,
  roadmapCount: document.querySelectorAll('.gate-roadmap-item').length,
  viewedGate: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  currentGate: document.querySelector('.canonical-progress')?.dataset.currentGate,
  approvedCount: document.querySelector('.canonical-progress')?.dataset.approvedCount,
  taskText: document.querySelector('#stage-detail')?.textContent,
  lookdev: Boolean(document.querySelector('[data-asset-id="${lookdevId}"]')),
  video: Boolean(document.querySelector('[data-asset-id="${videoId}"]')),
  board: Boolean(document.querySelector('[data-asset-id="${boardId}"]')),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
}))()`);
assert.equal(desktop.activeModel, "magnetic-slide-tile");
assert.deepEqual(desktop.tabLabels, [
  "参考原图",
  "分析（截图/视频）",
  "尺寸",
  "交互 CAD",
  "白模",
  "贴图与材质",
  "Unity 灯光与成品",
]);
assert.equal(desktop.activeTab, "materials");
assert.equal(desktop.activeTabStatus, "current");
assert.equal(desktop.roadmapCount, 12);
assert.equal(desktop.viewedGate, "09-environment");
assert.equal(desktop.currentGate, "9");
assert.equal(desktop.approvedCount, "8");
assert.match(desktop.taskText, /Gate 09 rev 9/);
assert.match(desktop.taskText, /只更换环境纹理/);
assert.match(desktop.taskText, /侧壁／底面 artwork 0/);
assert.equal(desktop.lookdev, true);
assert.equal(desktop.video, true);
assert.equal(desktop.board, true);
assert.ok(desktop.overflow <= 2);
await evaluate("window.scrollTo(0, 0)");
await screenshot(desktopScreenshot, true);

await click(`[data-asset-id="${lookdevId}"]`);
await eventually(
  "document.querySelector('#asset-dialog[open] .model-viewer canvas')",
  "interactive environment GLB",
);
await eventually(
  "performance.getEntriesByType('resource').some((entry) => entry.name.includes('magnetic-slide-tile-environment-r009-lookdev.glb'))",
  "environment GLB request",
);
const canvas = await evaluate(`(() => {
  const rect = document.querySelector('.model-viewer canvas').getBoundingClientRect();
  return { x: rect.x, y: rect.y, width: rect.width, height: rect.height };
})()`);
await call("Input.dispatchMouseEvent", {
  type: "mousePressed",
  x: canvas.x + canvas.width / 2,
  y: canvas.y + canvas.height / 2,
  button: "left",
  buttons: 1,
});
await call("Input.dispatchMouseEvent", {
  type: "mouseMoved",
  x: canvas.x + canvas.width / 2 + 100,
  y: canvas.y + canvas.height / 2 + 35,
  button: "left",
  buttons: 1,
});
await call("Input.dispatchMouseEvent", {
  type: "mouseReleased",
  x: canvas.x + canvas.width / 2 + 100,
  y: canvas.y + canvas.height / 2 + 35,
  button: "left",
  buttons: 0,
});
await call("Input.dispatchMouseEvent", {
  type: "mouseWheel",
  x: canvas.x + canvas.width / 2,
  y: canvas.y + canvas.height / 2,
  deltaX: 0,
  deltaY: -180,
});
await delay(500);
await screenshot(glbScreenshot);
const viewer = await evaluate(`(() => ({
  width: document.querySelector('.model-viewer canvas').getBoundingClientRect().width,
  routeAsset: new URL(location.href).searchParams.get('asset'),
  environment: Boolean(document.querySelector('.model-viewer [data-environment]')),
  exposure: Boolean(document.querySelector('.model-viewer [data-exposure]'))
}))()`);
assert.ok(viewer.width > 500);
assert.equal(viewer.routeAsset, lookdevId);
assert.equal(viewer.environment, true);
assert.equal(viewer.exposure, true);
await click("#dialog-close");

await click(`[data-asset-id="${videoId}"]`);
const video = await eventually(`(() => {
  const node = document.querySelector('#asset-dialog[open] video');
  if (!node || node.readyState < 1) return null;
  return { duration: node.duration, width: node.videoWidth, height: node.videoHeight };
})()`, "environment turntable");
assert.ok(Math.abs(video.duration - 5) < 0.05);
assert.equal(video.width, 1600);
assert.equal(video.height, 600);
await click("#dialog-close");

await click(`[data-asset-id="${boardId}"]`);
await eventually(
  "document.querySelector('#asset-dialog[open] img')?.naturalWidth >= 1200",
  "environment comparison modal",
);
await click("#dialog-close");

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
})()`, "workspace reload");
assert.equal(reload.stage, "09-environment");
assert.equal(reload.tab, "materials");
assert.equal(reload.memoryStage, "09-environment");
assert.equal(reload.memoryTab, "materials");

await navigate(deepLink);
await eventually(
  "document.querySelector('#asset-dialog[open] .model-viewer canvas')",
  "direct environment GLB deep link",
);
assert.equal(await evaluate("new URL(location.href).searchParams.get('asset')"), lookdevId);
await click("#dialog-close");

await call("Emulation.setDeviceMetricsOverride", {
  width: 390,
  height: 844,
  deviceScaleFactor: 2,
  mobile: true,
});
await navigate(route);
const mobile = await evaluate(`(() => ({
  tabs: document.querySelectorAll('[data-workspace-tab]').length,
  roadmap: document.querySelectorAll('.gate-roadmap-item').length,
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  lookdev: Boolean(document.querySelector('[data-asset-id="${lookdevId}"]')),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  tabScroller: document.querySelector('.workspace-tabs').scrollWidth
    > document.querySelector('.workspace-tabs').clientWidth
}))()`);
assert.equal(mobile.tabs, 7);
assert.equal(mobile.roadmap, 12);
assert.equal(mobile.stage, "09-environment");
assert.equal(mobile.lookdev, true);
assert.ok(mobile.overflow <= 2);
assert.equal(mobile.tabScroller, true);
await screenshot(mobileScreenshot);

const report = {
  pass: runtimeExceptions.length === 0 && loadingFailures.length === 0,
  route,
  deepLink,
  desktop,
  viewer: { ...viewer, orbit: "pass", zoom: "pass", screenshot: glbScreenshot },
  video,
  imageModal: "pass",
  reload,
  mobile,
  runtimeExceptionCount: runtimeExceptions.length,
  loadingFailureCount: loadingFailures.length,
  screenshots: [desktopScreenshot, glbScreenshot, mobileScreenshot],
};
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
socket.close();
assert.equal(report.pass, true);
console.log(JSON.stringify(report, null, 2));
