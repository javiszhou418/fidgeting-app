import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9231";
const baseUrl = process.env.WORKBENCH_URL
  || "http://127.0.0.1:8891/tools/model-provenance-explorer/";
const route = `${baseUrl}?model=magnetic-slide-tile&tab=materials&gate=08-lighting`;
const deepLink = `${route}&asset=magnetic-slide-tile-lighting-corrected-synchronized-preview-r004`;
const screenshotPath = path.resolve(
  "../../Artifacts/ModelProvenanceExplorer/magnetic-slide-gate08-rev4-neutral-parity.png"
);
const reportPath = path.resolve(
  "../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-004/browser-validation.json"
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
    "workspace"
  );
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
    'magnetic-slide-tile-lighting-corrected-synchronized-preview-r004',
    'magnetic-slide-tile-lighting-corrected-synchronized-poster-r004',
    'magnetic-slide-tile-lighting-board-r004',
    'magnetic-slide-tile-lighting-blender-full-r004',
    'magnetic-slide-tile-lighting-unity-full-r004'
  ].every((id) => document.querySelector('[data-asset-id="' + id + '"]')),
  oldCandidateHidden: !document.querySelector(
    '.asset-panel [data-asset-id="magnetic-slide-tile-lighting-comparison-recording-r003"]'
  ),
  oldCandidatePreserved: Boolean(document.querySelector(
    '.historical-evidence [data-asset-id="magnetic-slide-tile-lighting-comparison-recording-r003"]'
  )),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
}))()`);
assert.equal(desktop.activeModel, "magnetic-slide-tile");
assert.equal(desktop.activeTab, "materials");
assert.equal(desktop.activeTabStatus, "current");
assert.equal(desktop.viewedGate, "08-lighting");
assert.equal(desktop.currentGate, "8");
assert.equal(desktop.approvedCount, "7");
assert.match(desktop.taskText, /修正版|竖直|vertical|\+Z|zero roll/i);
assert.equal(desktop.reviewAssets, true);
assert.equal(desktop.oldCandidateHidden, true);
assert.equal(desktop.oldCandidatePreserved, true);
assert.ok(desktop.overflow <= 2);

await click('[data-asset-id="magnetic-slide-tile-lighting-corrected-synchronized-preview-r004"]');
await eventually("document.querySelector('#asset-dialog[open] video')", "comparison video");
const desktopPlayback = await eventually(`(() => {
  const video = document.querySelector('#asset-dialog[open] video');
  if (!video || video.readyState < 1 || Math.abs(video.duration - 12) > 0.05) return null;
  video.currentTime = 1;
  return video.play().then(() => ({
    duration: video.duration,
    dimensions: [video.videoWidth, video.videoHeight],
    playsInline: video.playsInline,
    currentSrc: video.currentSrc
  })).catch(() => null);
})()`, "desktop H.264 playback");
assert.deepEqual(desktopPlayback.dimensions, [2800, 1180]);
assert.equal(desktopPlayback.playsInline, true);
assert.match(desktopPlayback.currentSrc, /gate08-r004-synchronized-portable-parity\.mp4/);
await click("#dialog-close");
await eventually("!document.querySelector('#asset-dialog[open]')", "video close");
await click('[data-asset-id="magnetic-slide-tile-lighting-board-r004"]');
await eventually("document.querySelector('#asset-dialog[open] img')", "review board");
await evaluate(
  "document.querySelector('#asset-dialog').dispatchEvent(new Event('cancel', { cancelable: true }))"
);
await eventually("!document.querySelector('#asset-dialog[open]')", "board close");

await call("Emulation.setDeviceMetricsOverride", {
  width: 390, height: 844, deviceScaleFactor: 2, mobile: true,
});
await navigate(route);
const mobile = await evaluate(`(() => ({
  tabs: document.querySelectorAll('[data-workspace-tab]').length,
  roadmap: document.querySelectorAll('.gate-roadmap-item').length,
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  review: Boolean(document.querySelector(
    '[data-asset-id="magnetic-slide-tile-lighting-corrected-synchronized-preview-r004"]'
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
await click('[data-asset-id="magnetic-slide-tile-lighting-corrected-synchronized-preview-r004"]');
const mobilePlayback = await eventually(`(() => {
  const video = document.querySelector('#asset-dialog[open] video');
  if (!video || video.readyState < 1 || Math.abs(video.duration - 12) > 0.05) return null;
  return {
    duration: video.duration,
    dimensions: [video.videoWidth, video.videoHeight],
    playsInline: video.playsInline,
    currentSrc: video.currentSrc
  };
})()`, "mobile H.264 playback");
assert.deepEqual(mobilePlayback.dimensions, [2800, 1180]);
assert.equal(mobilePlayback.playsInline, true);
await click("#dialog-close");

await call("Emulation.setDeviceMetricsOverride", {
  width: 1440, height: 1900, deviceScaleFactor: 1, mobile: false,
});
await navigate(route);
await navigate(deepLink);
await eventually(
  `document.querySelector(
    '#asset-dialog[open] video[src*="gate08-r004-synchronized-portable-parity.mp4"]'
  )`,
  "corrected preview deep link",
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
  deepLinkRestore: true,
  desktop,
  mobile,
  comparisonVideoModal: true,
  desktopPlayback,
  mobilePlayback,
  reviewBoardModal: true,
  runtimeExceptionCount: runtimeExceptions.length,
  loadingFailureCount: loadingFailures.length,
  screenshotPath,
};
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
assert.equal(report.pass, true);
socket.close();
console.log(JSON.stringify(report, null, 2));
