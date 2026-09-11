import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9232";
const baseUrl = process.env.WORKBENCH_URL
  || "http://127.0.0.1:8891/tools/model-provenance-explorer/";
const assetId = "magnetic-slide-tile-unity-playmode-runtime-recording-r004";
const route = `${baseUrl}?model=magnetic-slide-tile&tab=unity&gate=11-unity-parity`;
const deepLink = `${route}&asset=${assetId}`;
const reportPath = path.resolve(
  "../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-004/unity-playmode-preview/browser-playback-validation.json"
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
const navigate = async (url) => {
  await call("Page.navigate", { url });
  await eventually("document.readyState === 'complete'", "navigation");
  await eventually(
    "document.querySelectorAll('[data-workspace-tab]').length === 7",
    "workspace"
  );
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

await call("Runtime.enable");
await call("Page.enable");
await call("Network.enable");
await call("Emulation.setDeviceMetricsOverride", {
  width: 1440, height: 1400, deviceScaleFactor: 1, mobile: false,
});
await navigate(route);
const desktop = await evaluate(`(() => ({
  activeTab: document.querySelector('[data-workspace-tab].is-active')?.dataset.workspaceTab,
  stage: document.querySelector('.gate-roadmap-item.is-viewed')?.dataset.stageId,
  taskText: document.querySelector('#stage-detail')?.textContent,
  videoExists: Boolean(document.querySelector('[data-asset-id="${assetId}"]')),
  approvalControl: Boolean(document.querySelector('[data-approval-action]')),
  overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
}))()`);
assert.equal(desktop.activeTab, "unity");
assert.equal(desktop.stage, "11-unity-parity");
assert.match(desktop.taskText, /Unity-only|PlayMode|不是 iPhone Build/);
assert.equal(desktop.videoExists, true);
assert.equal(desktop.approvalControl, false);
assert.ok(desktop.overflow <= 2);

await click(`.asset-panel [data-asset-id="${assetId}"]`);
const desktopPlayback = await eventually(`(() => {
  const video = document.querySelector('#asset-dialog[open] video');
  if (!video || video.readyState < 1 || Math.abs(video.duration - 15) > 0.05) return null;
  video.muted = true;
  return video.play().then(() => ({
    duration: video.duration,
    dimensions: [video.videoWidth, video.videoHeight],
    playsInline: video.playsInline,
    currentSrc: video.currentSrc
  })).catch(() => null);
})()`, "desktop Unity PlayMode playback", 30000);
assert.deepEqual(desktopPlayback.dimensions, [1920, 1080]);
assert.equal(desktopPlayback.playsInline, true);
assert.match(desktopPlayback.currentSrc, /gate08-r004-unity-playmode-runtime\.mp4/);
await click("#dialog-close");

await call("Emulation.setDeviceMetricsOverride", {
  width: 390, height: 844, deviceScaleFactor: 2, mobile: true,
});
await navigate(deepLink);
const mobilePlayback = await eventually(`(() => {
  const video = document.querySelector('#asset-dialog[open] video');
  if (!video || video.readyState < 1 || Math.abs(video.duration - 15) > 0.05) return null;
  return {
    duration: video.duration,
    dimensions: [video.videoWidth, video.videoHeight],
    playsInline: video.playsInline,
    currentSrc: video.currentSrc,
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
  };
})()`, "mobile Unity PlayMode playback");
assert.deepEqual(mobilePlayback.dimensions, [1920, 1080]);
assert.equal(mobilePlayback.playsInline, true);
assert.ok(mobilePlayback.overflow <= 2);

const report = {
  pass: runtimeExceptions.length === 0 && loadingFailures.length === 0,
  route,
  deepLink,
  desktop,
  desktopPlayback,
  mobilePlayback,
  runtimeExceptionCount: runtimeExceptions.length,
  loadingFailureCount: loadingFailures.length,
};
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
assert.equal(report.pass, true);
socket.close();
console.log(JSON.stringify(report, null, 2));
