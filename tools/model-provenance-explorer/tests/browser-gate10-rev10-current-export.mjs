import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9258";
const baseUrl = process.env.WORKBENCH_URL
  || "http://127.0.0.1:8891/tools/model-provenance-explorer/";
const route = `${baseUrl}?model=magnetic-slide-tile&tab=materials&gate=10-export`;
const glbId = "magnetic-slide-tile-export-glb-r010";
const boardId = "magnetic-slide-tile-export-review-board-r010";
const evidence = path.resolve(
  "../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-010",
);
const reportPath = path.join(evidence, "browser-validation.json");
const desktopScreenshot = path.join(evidence, "gate10-r010-persistent-workbench.png");
const glbScreenshot = path.join(evidence, "gate10-r010-interactive-glb.png");
const mobileScreenshot = path.join(evidence, "gate10-r010-mobile-workbench.png");

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
await evaluate("localStorage.removeItem('magnetic-slide-tile-gate10-r010-glb-checklist')");
await call("Page.reload", { ignoreCache: true });
await eventually(
  "document.querySelectorAll('[data-workspace-tab]').length === 7 && document.querySelector('#stage-detail')?.textContent.includes('Gate 10 rev 10')",
  "clean reload",
);
const desktop = await evaluate(`(() => ({
  tabs: [...document.querySelectorAll('[data-workspace-tab] strong')].map((node) => node.textContent.trim()),
  roadmap: document.querySelectorAll('.gate-roadmap-item').length,
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  currentGate: document.querySelector('.canonical-progress')?.dataset.currentGate,
  approvedCount: document.querySelector('.canonical-progress')?.dataset.approvedCount,
  text: document.querySelector('#stage-detail')?.textContent,
  glb: Boolean(document.querySelector('[data-asset-id="${glbId}"]')),
  board: Boolean(document.querySelector('[data-asset-id="${boardId}"]')),
  approveDisabled: document.querySelector('#approve-stage')?.disabled,
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
}))()`);
assert.deepEqual(desktop.tabs, [
  "参考原图", "分析（截图/视频）", "尺寸", "交互 CAD", "白模", "贴图与材质", "Unity 灯光与成品",
]);
assert.equal(desktop.roadmap, 12);
assert.equal(desktop.stage, "10-export");
assert.equal(desktop.currentGate, "10");
assert.equal(desktop.approvedCount, "9");
assert.match(desktop.text, /Gate 10 rev 10/);
assert.match(desktop.text, /侧壁／底面 artwork 0/);
assert.equal(desktop.glb, true);
assert.equal(desktop.board, true);
assert.equal(desktop.approveDisabled, true);
assert.ok(desktop.overflow <= 2);
await screenshot(desktopScreenshot, true);

await click(`[data-asset-id="${glbId}"]`);
await eventually("document.querySelector('#asset-dialog[open] .model-viewer canvas')", "export GLB viewer");
await eventually(
  "performance.getEntriesByType('resource').some((entry) => entry.name.includes('magnetic-slide-tile-render-r010.glb'))",
  "export GLB request",
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
const viewer = await eventually(`(() => {
  const checklist = JSON.parse(localStorage.getItem('magnetic-slide-tile-gate10-r010-glb-checklist') || '{}');
  return checklist.loaded && checklist.orbit && checklist.zoom ? {
    checklist,
    approveDisabled: document.querySelector('#approve-stage')?.disabled,
    payload: window.__exportApproval?.createPayload(),
    canvasWidth: document.querySelector('.model-viewer canvas').getBoundingClientRect().width
  } : null;
})()`, "GLB load orbit zoom checklist");
assert.equal(viewer.approveDisabled, false);
assert.equal(viewer.payload.reviewedArtifactId, glbId);
assert.deepEqual(viewer.payload.completedInteractionChecklist.sort(), ["loaded", "orbit", "zoom"]);
assert.ok(viewer.canvasWidth > 500);
await screenshot(glbScreenshot);
await click("#dialog-close");

await click(`[data-asset-id="${boardId}"]`);
await eventually("document.querySelector('#asset-dialog[open] img')", "review board modal");
await evaluate("document.querySelector('#asset-dialog').dispatchEvent(new Event('cancel', { cancelable: true }))");
await eventually("!document.querySelector('#asset-dialog[open]')", "board modal close");
await call("Page.reload", { ignoreCache: true });
const reload = await eventually(`(() => {
  const viewed = document.querySelector('.gate-roadmap-item.is-viewed');
  return viewed ? {
    stage: viewed.dataset.stageId,
    enabled: !document.querySelector('#approve-stage')?.disabled,
  } : null;
})()`, "Gate 10 reload");
assert.equal(reload.stage, "10-export");
assert.equal(reload.enabled, true);

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
  glb: Boolean(document.querySelector('[data-asset-id="${glbId}"]')),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  oneColumn: getComputedStyle(document.querySelector('.asset-grid')).gridTemplateColumns.split(' ').length === 1
}))()`);
assert.equal(mobile.tabs, 7);
assert.equal(mobile.roadmap, 12);
assert.equal(mobile.stage, "10-export");
assert.equal(mobile.glb, true);
assert.ok(mobile.overflow <= 2);
assert.equal(mobile.oneColumn, true);
await screenshot(mobileScreenshot);

await call("Emulation.setDeviceMetricsOverride", {
  width: 1440,
  height: 1900,
  deviceScaleFactor: 1,
  mobile: false,
});
await navigate(`${route}&asset=${glbId}`);
await eventually("document.querySelector('#asset-dialog[open] .model-viewer canvas')", "deep-linked GLB");
const deepLinkAsset = await evaluate("new URL(location.href).searchParams.get('asset')");
assert.equal(deepLinkAsset, glbId);
await click("#dialog-close");
const report = {
  pass: runtimeExceptions.length === 0 && loadingFailures.length === 0,
  desktop,
  viewer,
  reload,
  mobile,
  deepLinkAsset,
  runtimeExceptionCount: runtimeExceptions.length,
  runtimeExceptions,
  loadingFailureCount: loadingFailures.length,
  loadingFailures,
  desktopScreenshot,
  glbScreenshot,
  mobileScreenshot,
};
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
assert.equal(report.pass, true);
socket.close();
console.log(JSON.stringify(report, null, 2));
