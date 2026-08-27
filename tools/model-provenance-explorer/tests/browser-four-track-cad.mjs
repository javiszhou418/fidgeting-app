import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9224";
const baseUrl = process.env.WORKBENCH_URL || "http://127.0.0.1:8891/tools/model-provenance-explorer/";
const screenshotPath = path.resolve("../../Artifacts/ModelProvenanceExplorer/magnetic-slide-gate03-rev10-four-track-cad.png");
const focusedScreenshotPath = path.resolve("../../Artifacts/ModelProvenanceExplorer/magnetic-slide-gate03-rev10-four-track-cad-focused.png");
const reportPath = path.resolve("../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/03-contract/rev-010/browser-cad-validation.json");
const targets = await fetch(`${endpoint}/json/list`).then((response) => response.json());
const target = targets.find((candidate) => candidate.type === "page" && candidate.url.startsWith("http"));
assert.ok(target);
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
  assert.ok(point, `Missing ${selector}`);
  await call("Input.dispatchMouseEvent", { type: "mousePressed", ...point, button: "left", buttons: 1, clickCount: 1 });
  await call("Input.dispatchMouseEvent", { type: "mouseReleased", ...point, button: "left", buttons: 0, clickCount: 1 });
};

await call("Runtime.enable");
await call("Page.enable");
await call("Network.enable");
await call("Page.addScriptToEvaluateOnNewDocument", {
  source: `localStorage.setItem("fidgeting-model-pipeline-selected", "magnetic-slide-tile")`
});
await call("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1800, deviceScaleFactor: 1, mobile: false });
await call("Page.navigate", { url: baseUrl });
await eventually(`document.readyState === "complete"`, "page load");
await eventually(`document.querySelector('[data-model-id="magnetic-slide-tile"]')`, "model");
await eventually(`document.querySelector('[data-measurement-guide="true"]')`, "model load completion");
await evaluate(`document.querySelector('[data-stage-id="02-analysis"]').click()`);
await eventually(`document.querySelector('#mechanism-sandbox[data-contract-sha256]')`, "four-track CAD");
const desktop = await evaluate(`(() => ({
  contract: document.querySelector('#mechanism-sandbox').dataset.contractSha256,
  tracks: document.querySelectorAll('.cad-top-groove[data-groove-role]').length,
  outer: document.querySelectorAll('.cad-top-groove[data-groove-role="fore-aft-slide"]').length,
  inner: document.querySelectorAll('.cad-top-groove[data-groove-role="central-axis-link"]').length,
  raisedBoss: Boolean(document.querySelector('.cad-axis-boss-raised')),
  cavityText: /凹陷轴座|recessed axis allowed/.test(document.querySelector('#stage-detail').textContent),
  ballRange: document.querySelector('#stage-detail').textContent.includes('2–3 mm'),
  trackMax: /轨宽[^\\n]*3 mm/.test(document.querySelector('#stage-detail').textContent),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
}))()`);
assert.equal(desktop.contract, "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea");
assert.equal(desktop.tracks, 4);
assert.equal(desktop.outer, 2);
assert.equal(desktop.inner, 2);
assert.equal(desktop.raisedBoss, true);
assert.equal(desktop.cavityText, false);
assert.equal(desktop.ballRange, true);
assert.equal(desktop.trackMax, true);
assert.ok(desktop.overflow <= 2);

const drag = await evaluate(`(() => {
  const node = document.querySelector('[data-cad-slide-hit]');
  const rect = node.getBoundingClientRect();
  return { x: rect.x + rect.width * 0.62, y: rect.y + rect.height * 0.44 };
})()`);
await call("Input.dispatchMouseEvent", { type: "mousePressed", ...drag, button: "left", buttons: 1, clickCount: 1 });
await call("Input.dispatchMouseEvent", { type: "mouseMoved", x: drag.x + 48, y: drag.y - 64, button: "left", buttons: 1 });
await call("Input.dispatchMouseEvent", { type: "mouseReleased", x: drag.x + 48, y: drag.y - 64, button: "left", buttons: 0, clickCount: 1 });
const pose = await eventually(`(() => {
  const travel = parseFloat(document.querySelector('#sandbox-live-travel').textContent);
  const angle = parseFloat(document.querySelector('#sandbox-live-angle').textContent);
  return travel > 0 && Math.abs(angle) > 0.1 ? { travel, angle } : null;
})()`, "compound pointer motion");
assert.ok(pose.travel > 0);
assert.ok(Math.abs(pose.angle) > 0.1);

await click('[data-review-tab="references"]');
await eventually(`document.querySelector('[data-review-panel="references"].is-active')`, "reference gallery");
assert.ok(await evaluate(`document.querySelectorAll('[data-review-panel="references"] [data-asset-id]').length >= 10`));
await click('[data-asset-id="slider-analysis-img-6024-playback-proxy-r003"]');
await eventually(`document.querySelector('#asset-dialog[open] video')`, "video source modal");
await click("#dialog-close");
await eventually(`!document.querySelector('#asset-dialog').open`, "modal close");
await click('[data-review-tab="cad"]');

await call("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
const mobile = await evaluate(`(() => ({
  tracks: document.querySelectorAll('.cad-top-groove[data-groove-role]').length,
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
  cadWidth: document.querySelector('.mechanism-sandbox').getBoundingClientRect().width
}))()`);
assert.equal(mobile.tracks, 4);
assert.ok(mobile.overflow <= 2);
assert.ok(mobile.cadWidth <= 390);

await call("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1800, deviceScaleFactor: 1, mobile: false });
const focusedClip = await evaluate(`(() => {
  const node = document.querySelector('.mechanism-sandbox');
  node.scrollIntoView({ block: 'start', behavior: 'instant' });
  const rect = node.getBoundingClientRect();
  return { x: rect.x + scrollX, y: rect.y + scrollY, width: rect.width, height: rect.height };
})()`);
const focusedScreenshot = await call("Page.captureScreenshot", {
  format: "png",
  captureBeyondViewport: true,
  clip: { ...focusedClip, scale: 1 }
});
fs.writeFileSync(focusedScreenshotPath, Buffer.from(focusedScreenshot.data, "base64"));
await evaluate(`window.scrollTo(0, 0)`);
const layout = await call("Page.getLayoutMetrics");
const screenshot = await call("Page.captureScreenshot", {
  format: "png",
  captureBeyondViewport: true,
  clip: { x: 0, y: 0, width: Math.min(1440, Math.ceil(layout.cssContentSize.width)), height: Math.ceil(layout.cssContentSize.height), scale: 1 }
});
fs.mkdirSync(path.dirname(screenshotPath), { recursive: true });
fs.writeFileSync(screenshotPath, Buffer.from(screenshot.data, "base64"));
const report = {
  schemaVersion: 1,
  pass: runtimeExceptions.length === 0 && loadingFailures.length === 0,
  contractSha256: desktop.contract,
  desktop,
  pose,
  mobile,
  referenceGallery: true,
  videoModal: true,
  screenshot: screenshotPath,
  focusedScreenshot: focusedScreenshotPath,
  runtimeExceptionCount: runtimeExceptions.length,
  loadingFailureCount: loadingFailures.length
};
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
assert.equal(report.pass, true);
socket.close();
console.log(JSON.stringify({ screenshot: screenshotPath, focusedScreenshot: focusedScreenshotPath, report: reportPath, pass: true }, null, 2));
