import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9258";
const baseUrl = process.env.WORKBENCH_URL || "http://127.0.0.1:8891/tools/model-provenance-explorer/";
const route = `${baseUrl}?model=magnetic-slide-tile&tab=materials&gate=10-export`;
const glbId = "magnetic-slide-tile-export-glb-r011";
const comparisonId = "magnetic-slide-tile-export-comparison-r011";
const closeupsId = "magnetic-slide-tile-export-closeups-r011";
const evidence = path.resolve("../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-011");
const frames = path.join(evidence, "viewer-turntable-frames");
const desktopScreenshot = path.join(evidence, "gate10-r011-persistent-workbench.png");
const viewerScreenshot = path.join(evidence, "gate10-r011-threejs-neutral-hero.png");
const mobileScreenshot = path.join(evidence, "gate10-r011-mobile-workbench.png");
const videoPath = path.join(evidence, "gate10-r011-real-glb-orbit.mp4");
const reportPath = path.join(evidence, "browser-viewer-validation.json");
fs.rmSync(frames, { recursive: true, force: true });
fs.mkdirSync(frames, { recursive: true });

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
  if (response.exceptionDetails) throw new Error(response.exceptionDetails.text);
  return response.result.value;
};
const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));
const eventually = async (expression, description, timeout = 30000) => {
  const started = Date.now();
  while (Date.now() - started < timeout) {
    const value = await evaluate(expression);
    if (value) return value;
    await delay(100);
  }
  assert.fail(`Timed out waiting for ${description}.`);
};
const navigate = async (url) => {
  await call("Page.navigate", { url });
  await eventually("document.readyState === 'complete'", "navigation");
  await eventually("document.querySelectorAll('[data-workspace-tab]').length === 7", "workspace");
};
const rectFor = (selector) => evaluate(`(() => {
  const rect = document.querySelector(${JSON.stringify(selector)})?.getBoundingClientRect();
  return rect ? { x: rect.x, y: rect.y, width: rect.width, height: rect.height } : null;
})()`);
const click = async (selector) => {
  const rect = await evaluate(`(() => {
    const node = document.querySelector(${JSON.stringify(selector)});
    if (!node) return null;
    node.scrollIntoView({ block: "center", behavior: "instant" });
    const bounds = node.getBoundingClientRect();
    return { x: bounds.x, y: bounds.y, width: bounds.width, height: bounds.height };
  })()`);
  assert.ok(rect, `Missing ${selector}`);
  const point = { x: rect.x + rect.width / 2, y: rect.y + rect.height / 2 };
  await call("Input.dispatchMouseEvent", { type: "mousePressed", ...point, button: "left", buttons: 1, clickCount: 1 });
  await call("Input.dispatchMouseEvent", { type: "mouseReleased", ...point, button: "left", buttons: 0, clickCount: 1 });
};
const screenshot = async (output, clip = undefined, captureBeyondViewport = false) => {
  const result = await call("Page.captureScreenshot", { format: "png", fromSurface: true, clip, captureBeyondViewport });
  fs.writeFileSync(output, Buffer.from(result.data, "base64"));
};

await call("Runtime.enable");
await call("Page.enable");
await call("Network.enable");
await call("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1900, deviceScaleFactor: 1, mobile: false });
await navigate(route);
await evaluate(`localStorage.removeItem('magnetic-slide-tile-gate10-r011-glb-checklist');
  localStorage.setItem('fidgeting-model-workspace-v2:magnetic-slide-tile', JSON.stringify({ tabId: 'materials', stageId: '10-export', viewerExposure: 2, viewerLightingMode: 'daylight', viewerEnvironment: false }));`);
await call("Page.reload", { ignoreCache: true });
await eventually(
  "document.querySelector('#stage-detail')?.textContent.includes('Gate 10 rev 11') && document.querySelectorAll('[data-workspace-tab] strong').length === 7",
  "Gate 10 rev 11",
);
await delay(500);
const desktop = await evaluate(`(() => ({
  tabs: [...document.querySelectorAll('[data-workspace-tab] strong')].map((node) => node.textContent.trim()),
  tabsCount: document.querySelectorAll('[data-workspace-tab]').length,
  roadmap: document.querySelectorAll('.gate-roadmap-item').length,
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  currentGate: document.querySelector('.canonical-progress')?.dataset.currentGate,
  approvedCount: document.querySelector('.canonical-progress')?.dataset.approvedCount,
  text: document.querySelector('#stage-detail')?.textContent,
  glb: Boolean(document.querySelector('[data-asset-id="${glbId}"]')),
  comparison: Boolean(document.querySelector('[data-asset-id="${comparisonId}"]')),
  closeups: Boolean(document.querySelector('[data-asset-id="${closeupsId}"]')),
  approveDisabled: document.querySelector('#approve-stage')?.disabled,
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
}))()`);
assert.equal(desktop.tabsCount, 7);
assert.equal(desktop.roadmap, 12);
assert.equal(desktop.stage, "10-export");
assert.equal(desktop.currentGate, "10");
assert.equal(desktop.approvedCount, "9");
assert.match(desktop.text, /GLB 白化修正/);
assert.match(desktop.text, /中性 HDR \+ ACES 曝光 0.9/);
assert.equal(desktop.glb, true);
assert.equal(desktop.comparison, true);
assert.equal(desktop.closeups, true);
assert.equal(desktop.approveDisabled, true);
assert.ok(desktop.overflow <= 2);
await screenshot(desktopScreenshot, undefined, true);

await click(`[data-asset-id="${glbId}"]`);
await eventually("document.querySelector('#asset-dialog[open] .model-viewer canvas')", "corrected GLB viewer");
const calibration = await eventually(`window.__modelViewerCalibration?.ready ? {
  ...window.__modelViewerCalibration,
  exposureControl: Number(document.querySelector('[data-exposure]').value),
  exposureMin: Number(document.querySelector('[data-exposure]').min),
  exposureMax: Number(document.querySelector('[data-exposure]').max),
  environmentChecked: document.querySelector('[data-environment]').checked
} : null`, "neutral HDR calibration");
assert.equal(calibration.assetId, glbId);
assert.equal(calibration.outputColorSpace, "SRGBColorSpace");
assert.equal(calibration.toneMapping, "ACESFilmicToneMapping");
assert.equal(calibration.exposure, 0.9);
assert.equal(calibration.exposureControl, 0.9);
assert.equal(calibration.exposureMin, 0.7);
assert.equal(calibration.exposureMax, 1.1);
assert.equal(calibration.environmentIntensity, 0.58);
assert.equal(calibration.environmentChecked, true);
assert.match(calibration.environment, /neutral-control-r009\.exr$/);
await eventually(
  "performance.getEntriesByType('resource').some((entry) => entry.name.includes('magnetic-slide-tile-render-r011.glb'))",
  "corrected GLB request",
);
await eventually(
  "performance.getEntriesByType('resource').some((entry) => entry.name.includes('neutral-control-r009.exr'))",
  "neutral HDR request",
);
await eventually(
  "JSON.parse(localStorage.getItem('magnetic-slide-tile-gate10-r011-glb-checklist') || '{}').loaded",
  "corrected GLB loaded",
);
await call("Emulation.setDeviceMetricsOverride", { width: 1200, height: 900, deviceScaleFactor: 1, mobile: false });
await delay(250);
const canvas = await rectFor(".model-viewer canvas");
assert.ok(canvas.width > 500 && canvas.height === 560);
await screenshot(viewerScreenshot);
for (let frame = 0; frame < 24; frame += 1) {
  const start = { x: canvas.x + canvas.width * 0.52, y: canvas.y + canvas.height * 0.52 };
  await call("Input.dispatchMouseEvent", { type: "mousePressed", ...start, button: "left", buttons: 1 });
  await call("Input.dispatchMouseEvent", {
    type: "mouseMoved",
    x: start.x + 18,
    y: start.y + Math.sin(frame / 4) * 3,
    button: "left",
    buttons: 1,
  });
  await call("Input.dispatchMouseEvent", { type: "mouseReleased", x: start.x + 18, y: start.y, button: "left", buttons: 0 });
  if (frame === 0) {
    await call("Input.dispatchMouseEvent", { type: "mouseWheel", x: start.x, y: start.y, deltaX: 0, deltaY: -80 });
  }
  await delay(50);
  await screenshot(path.join(frames, `frame-${String(frame).padStart(3, "0")}.png`));
}
const viewer = await eventually(`(() => {
  const checklist = JSON.parse(localStorage.getItem('magnetic-slide-tile-gate10-r011-glb-checklist') || '{}');
  return checklist.loaded && checklist.orbit && checklist.zoom ? {
    checklist,
    approveDisabled: document.querySelector('#approve-stage')?.disabled,
    payload: window.__exportApproval?.createPayload()
  } : null;
})()`, "corrected GLB interaction checklist");
assert.equal(viewer.approveDisabled, false);
assert.equal(viewer.payload.reviewedArtifactId, glbId);
assert.deepEqual(viewer.payload.completedInteractionChecklist.sort(), ["loaded", "orbit", "zoom"]);
await click("#dialog-close");

for (const assetId of [comparisonId, closeupsId]) {
  await click(`[data-asset-id="${assetId}"]`);
  await eventually("document.querySelector('#asset-dialog[open] img')", `${assetId} modal`);
  await click("#dialog-close");
}
const reload = await evaluate(`(() => ({
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  enabled: !document.querySelector('#approve-stage')?.disabled,
  persistedChecklist: JSON.parse(localStorage.getItem('magnetic-slide-tile-gate10-r011-glb-checklist') || '{}')
}))()`);
assert.equal(reload.stage, "10-export");
assert.equal(reload.enabled, true);
assert.deepEqual(Object.keys(reload.persistedChecklist).sort(), ["loaded", "orbit", "zoom"]);

await call("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
await delay(200);
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

execFileSync("ffmpeg", [
  "-y", "-framerate", "12", "-i", path.join(frames, "frame-%03d.png"),
  "-vf", "format=yuv420p", "-c:v", "libx264", "-crf", "18", "-movflags", "+faststart", videoPath,
], { stdio: "pipe" });
const report = {
  pass: runtimeExceptions.length === 0 && loadingFailures.length === 0,
  desktop,
  calibration,
  viewer,
  reload,
  mobile,
  screenshots: { desktopScreenshot, viewerScreenshot, mobileScreenshot },
  video: { path: videoPath, sizeBytes: fs.statSync(videoPath).size },
  runtimeExceptionCount: runtimeExceptions.length,
  runtimeExceptions,
  loadingFailureCount: loadingFailures.length,
  loadingFailures,
};
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
assert.equal(report.pass, true);
socket.close();
console.log(JSON.stringify(report, null, 2));
