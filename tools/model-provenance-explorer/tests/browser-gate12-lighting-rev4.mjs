import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9264";
const baseUrl = process.env.WORKBENCH_URL
  || "http://127.0.0.1:8891/tools/model-provenance-explorer/";
const videoId =
  "magnetic-slide-tile-gate12-lighting-comparison-video-r004";
const boardId =
  "magnetic-slide-tile-gate12-lighting-comparison-board-r004";
const phoneId =
  "magnetic-slide-tile-gate12-lighting-phone-board-r004";
const route =
  `${baseUrl}?model=magnetic-slide-tile&tab=unity&gate=12-shipping`
  + `&asset=${videoId}`;
const evidence = path.resolve(
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/"
    + "evidence/12-shipping/rev-004-lighting",
);
const reportPath = path.join(
  evidence, "browser-mobile-modal-validation.json");

const targets = await fetch(`${endpoint}/json/list`)
  .then((response) => response.json());
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
  if (response.exceptionDetails)
    throw new Error(response.exceptionDetails.text);
  return response.result.value;
};
const delay = (milliseconds) =>
  new Promise((resolve) => setTimeout(resolve, milliseconds));
const eventually = async (expression, description, timeout = 30000) => {
  const started = Date.now();
  while (Date.now() - started < timeout) {
    const value = await evaluate(expression);
    if (value) return value;
    await delay(100);
  }
  assert.fail(`Timed out waiting for ${description}.`);
};
const click = async (selector) => {
  const rect = await evaluate(`(() => {
    const node = document.querySelector(${JSON.stringify(selector)});
    if (!node) return null;
    node.scrollIntoView({ block: "center", behavior: "instant" });
    const bounds = node.getBoundingClientRect();
    return { x: bounds.x, y: bounds.y, width: bounds.width, height: bounds.height };
  })()`);
  assert.ok(rect, `Missing ${selector}`);
  const point = {
    x: rect.x + rect.width / 2,
    y: rect.y + rect.height / 2,
  };
  await call("Input.dispatchMouseEvent", {
    type: "mousePressed",
    ...point,
    button: "left",
    buttons: 1,
    clickCount: 1,
  });
  await call("Input.dispatchMouseEvent", {
    type: "mouseReleased",
    ...point,
    button: "left",
    buttons: 0,
    clickCount: 1,
  });
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
await call("Page.navigate", { url: route });
await eventually("document.readyState === 'complete'", "navigation");
await eventually(
  "document.querySelectorAll('[data-workspace-tab]').length === 7",
  "persistent workbench",
);
await eventually(
  `document.querySelector('[data-asset-id="${videoId}"]')`,
  "lighting comparison video",
);

const desktop = await evaluate(`(() => ({
  tabs: document.querySelectorAll('[data-workspace-tab]').length,
  roadmap: document.querySelectorAll('.gate-roadmap-item').length,
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  currentGate: document.querySelector('.canonical-progress')?.dataset.currentGate,
  video: Boolean(document.querySelector('[data-asset-id="${videoId}"]')),
  board: Boolean(document.querySelector('[data-asset-id="${boardId}"]')),
  phone: Boolean(document.querySelector('[data-asset-id="${phoneId}"]')),
  approveDisabled: document.querySelector('#approve-stage')?.disabled,
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
}))()`);
assert.equal(desktop.tabs, 7);
assert.equal(desktop.roadmap, 12);
assert.equal(desktop.stage, "12-shipping");
assert.equal(desktop.currentGate, "12");
assert.equal(desktop.video, true);
assert.equal(desktop.board, true);
assert.equal(desktop.phone, true);
assert.ok(desktop.overflow <= 2);

await click(`[data-asset-id="${videoId}"]`);
const video = await eventually(`(() => {
  const media = document.querySelector('#asset-dialog[open] video');
  if (!media) return null;
  media.muted = true;
  return media.play().then(() => ({
    duration: media.duration,
    width: media.videoWidth,
    height: media.videoHeight
  }));
})()`, "video modal playback");
assert.ok(video.duration >= 26 && video.duration <= 27);
assert.equal(video.width, 1920);
assert.equal(video.height, 1080);
await click("#dialog-close");

for (const assetId of [boardId, phoneId]) {
  await click(`[data-asset-id="${assetId}"]`);
  await eventually(
    "document.querySelector('#asset-dialog[open] img')",
    `${assetId} image modal`,
  );
  await click("#dialog-close");
}

await call("Emulation.setDeviceMetricsOverride", {
  width: 390,
  height: 844,
  deviceScaleFactor: 2,
  mobile: true,
});
await delay(250);
const mobile = await evaluate(`(() => ({
  tabs: document.querySelectorAll('[data-workspace-tab]').length,
  roadmap: document.querySelectorAll('.gate-roadmap-item').length,
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  video: Boolean(document.querySelector('[data-asset-id="${videoId}"]')),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  oneColumn: getComputedStyle(document.querySelector('.asset-grid')).gridTemplateColumns.split(' ').length === 1
}))()`);
assert.equal(mobile.tabs, 7);
assert.equal(mobile.roadmap, 12);
assert.equal(mobile.stage, "12-shipping");
assert.equal(mobile.video, true);
assert.ok(mobile.overflow <= 2);
assert.equal(mobile.oneColumn, true);

const report = {
  pass: runtimeExceptions.length === 0 && loadingFailures.length === 0,
  route,
  desktop,
  video,
  mobile,
  modalClose: true,
  runtimeExceptionCount: runtimeExceptions.length,
  loadingFailureCount: loadingFailures.length,
};
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
assert.equal(report.pass, true);
socket.close();
console.log(JSON.stringify(report, null, 2));
