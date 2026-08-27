import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9223";
const baseUrl = process.env.WORKBENCH_URL || "http://127.0.0.1:8891/tools/model-provenance-explorer/";
const screenshotPath = path.resolve(
  process.env.GATE05_SCREENSHOT || "../../Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev4-workbench.png"
);
const reportPath = path.resolve(
  "../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-004/browser-smoke-validation.json"
);
const targets = await fetch(`${endpoint}/json/list`).then((response) => response.json());
const target = targets.find((candidate) => candidate.type === "page" && candidate.url.startsWith("http"));
assert.ok(target, "Open a CDP browser page before running the Gate 05 smoke test.");
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
const eventually = async (expression, description, timeout = 12000) => {
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
  assert.ok(point, `Missing click target ${selector}.`);
  await call("Input.dispatchMouseEvent", { type: "mousePressed", ...point, button: "left", buttons: 1, clickCount: 1 });
  await call("Input.dispatchMouseEvent", { type: "mouseReleased", ...point, button: "left", buttons: 0, clickCount: 1 });
};
const openGate05 = async () => {
  await eventually(`document.querySelector('[data-model-id="magnetic-slide-tile"]')`, "model navigation");
  await click('[data-model-id="magnetic-slide-tile"]');
  await eventually(`document.querySelector('[data-stage-id="05-blockout"][data-status="ready_for_review"]')`, "Gate 05 roadmap");
  await click('[data-stage-id="05-blockout"]');
  await eventually(`document.querySelector('[data-asset-id="magnetic-slide-tile-blockout-interactive-r004"]')`, "Gate 05 GLB");
};

await call("Runtime.enable");
await call("Page.enable");
await call("Network.enable");
await call("Emulation.setDeviceMetricsOverride", {
  width: 1440, height: 1800, deviceScaleFactor: 1, mobile: false
});
await call("Page.navigate", { url: baseUrl });
await eventually(`document.readyState === "complete"`, "desktop page load");
await openGate05();
const desktop = await evaluate(`(() => ({
  status: document.querySelector('[data-stage-id="05-blockout"]').dataset.status,
  reviewAssetCount: document.querySelectorAll('#stage-detail [data-asset-id]').length,
  hasSimulatorPrerequisite: /Simulator 批准后才允许 Blender|Simulator approval is required before Blender/.test(document.body.innerText),
  bodyOverflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
}))()`);
assert.equal(desktop.status, "ready_for_review");
assert.ok(desktop.reviewAssetCount >= 9);
assert.equal(desktop.hasSimulatorPrerequisite, false);
assert.ok(desktop.bodyOverflow <= 2);

await click('[data-asset-id="magnetic-slide-tile-blockout-interactive-r004"]');
await eventually(`document.querySelector('#asset-dialog[open] .model-viewer canvas')`, "interactive GLB viewer");
await eventually(`document.querySelector('#asset-dialog[open] .viewer-controls [data-view="top"]')`, "viewer controls");
await eventually(
  `performance.getEntriesByType('resource').some((entry) => entry.name.endsWith('magnetic-slide-tile-blockout-r004-review.glb'))`,
  "GLB network load"
);
await click('#asset-dialog .viewer-controls [data-view="top"]');
await click('#asset-dialog .viewer-controls [data-wireframe]');
const viewer = await evaluate(`(() => {
  const canvas = document.querySelector('#asset-dialog[open] .model-viewer canvas');
  const glbRequest = performance.getEntriesByType('resource').find((entry) => entry.name.endsWith('magnetic-slide-tile-blockout-r004-review.glb'));
  return { width: canvas.width, height: canvas.height, glbLoaded: Boolean(glbRequest && glbRequest.duration >= 0) };
})()`);
assert.ok(viewer.width >= 320);
assert.ok(viewer.height > 0);
assert.equal(viewer.glbLoaded, true);
await click("#dialog-close");
await eventually(`!document.querySelector('#asset-dialog').open`, "GLB modal close");

await click('[data-asset-id="magnetic-slide-tile-blockout-hero-r004"]');
await eventually(`document.querySelector('#asset-dialog[open] img')`, "image modal");
await call("Input.dispatchKeyEvent", {
  type: "rawKeyDown", key: "Escape", code: "Escape",
  windowsVirtualKeyCode: 27, nativeVirtualKeyCode: 27
});
await call("Input.dispatchKeyEvent", {
  type: "keyUp", key: "Escape", code: "Escape",
  windowsVirtualKeyCode: 27, nativeVirtualKeyCode: 27
});
await eventually(`!document.querySelector('#asset-dialog').open`, "Escape modal close");

await call("Emulation.setDeviceMetricsOverride", {
  width: 390, height: 844, deviceScaleFactor: 3, mobile: true, screenWidth: 390, screenHeight: 844
});
await call("Page.reload", { ignoreCache: true });
await eventually(`document.readyState === "complete"`, "mobile page load");
await openGate05();
const mobile = await evaluate(`(() => ({
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  gateVisible: Boolean(document.querySelector('[data-stage-id="05-blockout"][data-status="ready_for_review"]')),
  glbButtonVisible: Boolean(document.querySelector('[data-asset-id="magnetic-slide-tile-blockout-interactive-r004"]'))
}))()`);
assert.ok(mobile.overflow <= 2);
assert.equal(mobile.gateVisible, true);
assert.equal(mobile.glbButtonVisible, true);
await click('[data-asset-id="magnetic-slide-tile-blockout-interactive-r004"]');
await eventually(`document.querySelector('#asset-dialog[open] .model-viewer canvas')`, "mobile GLB viewer");
const mobileCanvasWidth = await evaluate(`document.querySelector('#asset-dialog[open] .model-viewer canvas').getBoundingClientRect().width`);
assert.ok(mobileCanvasWidth >= 320 && mobileCanvasWidth <= 390);
await click("#dialog-close");

await call("Emulation.setDeviceMetricsOverride", {
  width: 1440, height: 1800, deviceScaleFactor: 1, mobile: false
});
await call("Page.reload", { ignoreCache: true });
await eventually(`document.readyState === "complete"`, "final desktop page load");
await openGate05();
const metrics = await call("Page.getLayoutMetrics");
const height = Math.ceil(metrics.cssContentSize.height);
const screenshot = await call("Page.captureScreenshot", {
  format: "png",
  captureBeyondViewport: true,
  clip: { x: 0, y: 0, width: 1440, height, scale: 1 }
});
fs.mkdirSync(path.dirname(screenshotPath), { recursive: true });
fs.writeFileSync(screenshotPath, Buffer.from(screenshot.data, "base64"));

assert.deepEqual(runtimeExceptions, []);
assert.deepEqual(loadingFailures.filter((failure) => /magnetic-slide-tile-blockout-r004-review\.glb/.test(failure.blockedReason || failure.errorText || "")), []);
const report = {
  schemaVersion: 1,
  modelId: "magnetic-slide-tile",
  gate: "05-blockout",
  revision: 4,
  desktop,
  viewer,
  mobile: { ...mobile, canvasWidth: mobileCanvasWidth },
  runtimeExceptionCount: runtimeExceptions.length,
  loadingFailureCount: loadingFailures.length,
  screenshot: path.relative(process.cwd(), screenshotPath),
  checks: {
    gate05Ready: true,
    realGlbLoaded: true,
    desktopModalControls: true,
    imageModalEscape: true,
    mobileNoOverflow: true,
    mobileGlbViewer: true,
    noSimulatorPrerequisiteCopy: true
  },
  pass: true
};
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
console.log(JSON.stringify({ screenshot: screenshotPath, report: reportPath, pass: true }, null, 2));
socket.close();
