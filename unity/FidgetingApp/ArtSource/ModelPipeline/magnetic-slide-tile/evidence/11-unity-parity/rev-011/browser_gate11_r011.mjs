import assert from "node:assert/strict";
import fs from "node:fs";
import WebSocket from "../../../../../../../../tools/model-provenance-explorer/node_modules/ws/wrapper.mjs";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9223";
const baseUrl =
  "http://127.0.0.1:8891/tools/model-provenance-explorer/";
const videoId = "magnetic-slide-tile-unity-parity-playmode-video-r011";
const boardId = "magnetic-slide-tile-unity-parity-appearance-board-r011";
const route =
  `${baseUrl}?model=magnetic-slide-tile&tab=unity&gate=11-unity-parity`;
const targets = await fetch(`${endpoint}/json/list`).then((response) => response.json());
const target = targets.find((candidate) => candidate.type === "page");
assert.ok(target);
const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  socket.addEventListener("open", resolve, { once: true });
  socket.addEventListener("error", reject, { once: true });
});

let id = 0;
const pending = new Map();
const runtimeExceptions = [];
const loadingFailures = [];
socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  if (message.method === "Runtime.exceptionThrown")
    runtimeExceptions.push(message.params.exceptionDetails);
  if (message.method === "Network.loadingFailed" && !message.params.canceled)
    loadingFailures.push(message.params);
  if (!message.id || !pending.has(message.id)) return;
  const waiter = pending.get(message.id);
  pending.delete(message.id);
  if (message.error) waiter.reject(new Error(message.error.message));
  else waiter.resolve(message.result);
});
const call = (method, params = {}) => new Promise((resolve, reject) => {
  const requestId = ++id;
  pending.set(requestId, { resolve, reject });
  socket.send(JSON.stringify({ id: requestId, method, params }));
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
const eventually = async (expression, label, timeout = 20000) => {
  const started = Date.now();
  while (Date.now() - started < timeout) {
    const value = await evaluate(expression);
    if (value) return value;
    await delay(100);
  }
  assert.fail(`Timed out waiting for ${label}.`);
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
  await eventually(
    "document.querySelectorAll('[data-workspace-tab]').length === 7",
    "workbench");
};
const screenshot = async (path) => {
  const image = await call("Page.captureScreenshot", {
    format: "png", fromSurface: true, captureBeyondViewport: true,
  });
  fs.writeFileSync(path, Buffer.from(image.data, "base64"));
};

await call("Runtime.enable");
await call("Page.enable");
await call("Network.enable");
await call("Emulation.setDeviceMetricsOverride", {
  width: 1440, height: 1200, deviceScaleFactor: 1, mobile: false,
});
await navigate(route);
const desktop = await evaluate(`(() => ({
  model: document.querySelector('[data-model-id].is-active')?.dataset.modelId,
  tabs: document.querySelectorAll('[data-workspace-tab]').length,
  roadmap: document.querySelectorAll('.gate-roadmap-item').length,
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  status: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.status,
  video: Boolean(document.querySelector('[data-asset-id="${videoId}"]')),
  board: Boolean(document.querySelector('[data-asset-id="${boardId}"]')),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
}))()`);
assert.deepEqual(desktop, {
  model: "magnetic-slide-tile",
  tabs: 7,
  roadmap: 12,
  stage: "11-unity-parity",
  status: "ready_for_review",
  video: true,
  board: true,
  overflow: 0,
});
await screenshot("gate11-r011-workbench-desktop.png");

await click(`[data-asset-id="${videoId}"]`);
const video = await eventually(`(() => {
  const node = document.querySelector('#asset-dialog[open] video');
  if (!node || node.readyState < 1) return null;
  return { duration: node.duration, width: node.videoWidth, height: node.videoHeight };
})()`, "Unity video modal");
assert.ok(Math.abs(video.duration - 18) < 0.05);
assert.equal(video.width, 1920);
assert.equal(video.height, 1080);
await click("#dialog-close");

await click(`[data-asset-id="${boardId}"]`);
await eventually(
  "document.querySelector('#asset-dialog[open] img')?.naturalWidth >= 1000",
  "appearance board modal");
await click("#dialog-close");

await navigate(`${route}&asset=${videoId}`);
await eventually(
  "document.querySelector('#asset-dialog[open] video')?.readyState >= 1",
  "video deep link");
await click("#dialog-close");

await call("Emulation.setDeviceMetricsOverride", {
  width: 390, height: 844, deviceScaleFactor: 2, mobile: true,
});
await navigate(route);
const mobile = await evaluate(`(() => ({
  tabs: document.querySelectorAll('[data-workspace-tab]').length,
  roadmap: document.querySelectorAll('.gate-roadmap-item').length,
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  video: Boolean(document.querySelector('[data-asset-id="${videoId}"]')),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
}))()`);
assert.equal(mobile.tabs, 7);
assert.equal(mobile.roadmap, 12);
assert.equal(mobile.stage, "11-unity-parity");
assert.equal(mobile.video, true);
assert.ok(mobile.overflow <= 2);
await screenshot("gate11-r011-workbench-mobile.png");

const report = {
  pass: runtimeExceptions.length === 0 && loadingFailures.length === 0,
  route,
  deepLink: `${route}&asset=${videoId}`,
  desktop,
  video,
  imageModal: "pass",
  mobile,
  runtimeExceptionCount: runtimeExceptions.length,
  loadingFailureCount: loadingFailures.length,
};
fs.writeFileSync("browser-validation.json", `${JSON.stringify(report, null, 2)}\n`);
assert.equal(report.pass, true);
socket.close();
