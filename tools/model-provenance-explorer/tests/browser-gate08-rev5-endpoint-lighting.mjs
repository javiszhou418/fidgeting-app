import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9243";
const baseUrl = process.env.WORKBENCH_URL
  || "http://127.0.0.1:8891/tools/model-provenance-explorer/";
const route = `${baseUrl}?model=magnetic-slide-tile&tab=materials&gate=08-lighting`;
const deepLink = `${route}&asset=magnetic-slide-tile-lighting-turntable-r005`;
const screenshotPath = path.resolve(
  "../../Artifacts/ModelProvenanceExplorer/magnetic-slide-gate08-rev5-lighting.png",
);
const reportPath = path.resolve(
  "../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-005/browser-validation.json",
);

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
  const response = await call("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (response.exceptionDetails) throw new Error(response.exceptionDetails.text);
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

await call("Runtime.enable");
await call("Page.enable");
await call("Network.enable");
await call("Emulation.setDeviceMetricsOverride", {
  width: 1440, height: 1900, deviceScaleFactor: 1, mobile: false,
});
await navigate(route);
const desktop = await evaluate(`(() => ({
  activeModel: document.querySelector('[data-model-id].is-active')?.dataset.modelId,
  activeTab: document.querySelector('[data-workspace-tab].is-active')?.dataset.workspaceTab,
  activeTabStatus: document.querySelector('[data-workspace-tab].is-active')?.dataset.status,
  viewedGate: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  currentGate: document.querySelector('.canonical-progress')?.dataset.currentGate,
  approvedCount: document.querySelector('.canonical-progress')?.dataset.approvedCount,
  taskText: document.querySelector('#stage-detail')?.textContent,
  reviewAssets: [
    'magnetic-slide-tile-lighting-turntable-r005',
    'magnetic-slide-tile-lighting-board-r005',
    'magnetic-slide-tile-lighting-comparison-r005',
    'magnetic-slide-tile-lighting-hero-r005'
  ].every((id) => document.querySelector('[data-asset-id="' + id + '"]')),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
}))()`);
assert.equal(desktop.activeModel, "magnetic-slide-tile");
assert.equal(desktop.activeTab, "materials");
assert.equal(desktop.activeTabStatus, "current");
assert.equal(desktop.viewedGate, "08-lighting");
assert.equal(desktop.currentGate, "8");
assert.equal(desktop.approvedCount, "7");
assert.match(desktop.taskText, /端点互锁|最大行程|360°|共享 HDR/);
assert.equal(desktop.reviewAssets, true);
assert.ok(desktop.overflow <= 2);

await click('[data-asset-id="magnetic-slide-tile-lighting-turntable-r005"]');
const desktopPlayback = await eventually(`(() => {
  const video = document.querySelector('#asset-dialog[open] video');
  if (!video || video.readyState < 1 || Math.abs(video.duration - 6) > 0.05) return null;
  video.currentTime = 1;
  return video.play().then(() => ({
    duration: video.duration,
    dimensions: [video.videoWidth, video.videoHeight],
    playsInline: video.playsInline,
    currentSrc: video.currentSrc
  })).catch(() => null);
})()`, "desktop endpoint turntable");
assert.deepEqual(desktopPlayback.dimensions, [960, 720]);
assert.equal(desktopPlayback.playsInline, true);
assert.match(desktopPlayback.currentSrc, /gate08-r005-endpoint-lighting-turntable\.mp4/);
await click("#dialog-close");
await eventually("!document.querySelector('#asset-dialog[open]')", "video close");
await click('[data-asset-id="magnetic-slide-tile-lighting-comparison-r005"]');
await eventually("document.querySelector('#asset-dialog[open] img')", "comparison image");
await click("#dialog-close");

await call("Emulation.setDeviceMetricsOverride", {
  width: 390, height: 844, deviceScaleFactor: 2, mobile: true,
});
await navigate(route);
const mobile = await evaluate(`(() => ({
  tabs: document.querySelectorAll('[data-workspace-tab]').length,
  roadmap: document.querySelectorAll('.gate-roadmap-item').length,
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  review: Boolean(document.querySelector(
    '[data-asset-id="magnetic-slide-tile-lighting-turntable-r005"]'
  )),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  tabScroller: document.querySelector('.workspace-tabs').scrollWidth
    > document.querySelector('.workspace-tabs').clientWidth
}))()`);
assert.equal(mobile.tabs, 7);
assert.equal(mobile.roadmap, 12);
assert.equal(mobile.stage, "08-lighting");
assert.equal(mobile.review, true);
assert.ok(mobile.overflow <= 2);
assert.equal(mobile.tabScroller, true);
await click('[data-asset-id="magnetic-slide-tile-lighting-turntable-r005"]');
const mobilePlayback = await eventually(`(() => {
  const video = document.querySelector('#asset-dialog[open] video');
  if (!video || video.readyState < 1 || Math.abs(video.duration - 6) > 0.05) return null;
  return {
    dimensions: [video.videoWidth, video.videoHeight],
    playsInline: video.playsInline
  };
})()`, "mobile endpoint turntable");
assert.deepEqual(mobilePlayback.dimensions, [960, 720]);
assert.equal(mobilePlayback.playsInline, true);
await click("#dialog-close");

await call("Emulation.setDeviceMetricsOverride", {
  width: 1440, height: 1900, deviceScaleFactor: 1, mobile: false,
});
await navigate(deepLink);
await eventually(
  `document.querySelector('#asset-dialog[open] video[src*="gate08-r005-endpoint-lighting-turntable.mp4"]')`,
  "lighting turntable deep link",
);
await click("#dialog-close");
const screenshot = await call("Page.captureScreenshot", {
  format: "png",
  captureBeyondViewport: true,
});
fs.mkdirSync(path.dirname(screenshotPath), { recursive: true });
fs.writeFileSync(screenshotPath, Buffer.from(screenshot.data, "base64"));
const report = {
  pass: runtimeExceptions.length === 0 && loadingFailures.length === 0,
  route,
  deepLink,
  desktop,
  desktopPlayback,
  mobile,
  mobilePlayback,
  runtimeExceptionCount: runtimeExceptions.length,
  loadingFailureCount: loadingFailures.length,
  screenshotPath,
};
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
socket.close();
if (!report.pass) throw new Error(JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
