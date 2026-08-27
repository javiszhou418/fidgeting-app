import assert from "node:assert/strict";
import fs from "node:fs";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9223";
const output = process.env.MEASUREMENT_GUIDE_SCREENSHOT
  || "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate03-measurement-guide.png";
const targets = await fetch(`${endpoint}/json/list`).then((response) => response.json());
const target = targets.find((candidate) => candidate.type === "page");
assert.ok(target, "Open a CDP browser page before running this smoke test.");
const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  socket.addEventListener("open", resolve, { once: true });
  socket.addEventListener("error", reject, { once: true });
});
let sequence = 0;
const pending = new Map();
const exceptions = [];
socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
  if (message.method === "Runtime.exceptionThrown") exceptions.push(message.params.exceptionDetails);
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
const eventually = async (expression, timeout = 8000) => {
  const started = Date.now();
  while (Date.now() - started < timeout) {
    const value = await evaluate(expression);
    if (value) return value;
    await new Promise((resolve) => setTimeout(resolve, 80));
  }
  assert.fail("Timed out waiting for measurement guide.");
};

try {
  await call("Runtime.enable");
  await call("Page.enable");
  await call("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1100, deviceScaleFactor: 1, mobile: false });
  await call("Page.navigate", { url: "http://127.0.0.1:8891/tools/model-provenance-explorer/" });
  await eventually(`document.readyState === "complete"`);
  await evaluate(`localStorage.setItem("fidgeting-model-pipeline-selected", "magnetic-slide-tile")`);
  await call("Page.reload", { ignoreCache: true });
  const desktop = await eventually(`(() => {
    const guide = document.querySelector("[data-measurement-guide]");
    if (!guide) return null;
    return {
      progress: document.getElementById("measurement-progress")?.textContent,
      fields: guide.querySelectorAll("[data-measurement-field]").length,
      diagrams: guide.querySelectorAll(".measurement-diagram-grid article").length,
      uploads: guide.querySelectorAll("[data-measurement-photo]").length,
      optional: guide.querySelectorAll(".optional-measurement-field").length,
      copy: guide.textContent
    };
  })()`);
  assert.equal(desktop.progress, "0/9");
  assert.equal(desktop.fields, 9);
  assert.equal(desktop.diagrams, 4);
  assert.equal(desktop.uploads, 9);
  assert.equal(desktop.optional, 7);
  assert.match(desktop.copy, /轴心距最近圆端/);
  assert.match(desktop.copy, /旋转载体直径/);
  assert.match(desktop.copy, /加工余量 · 未知/);
  assert.doesNotMatch(desktop.copy, /50 × 31 × 12|直推 21/);

  const metrics = await call("Page.getLayoutMetrics");
  const width = Math.ceil(metrics.cssContentSize.width);
  const height = Math.ceil(metrics.cssContentSize.height);
  const screenshot = await call("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: true,
    clip: { x: 0, y: 0, width, height, scale: 1 }
  });
  fs.mkdirSync(new URL("../../../Artifacts/ModelProvenanceExplorer/", import.meta.url), { recursive: true });
  fs.writeFileSync(new URL(`../../../${output}`, import.meta.url), Buffer.from(screenshot.data, "base64"));

  await call("Emulation.setDeviceMetricsOverride", { width: 390, height: 844, deviceScaleFactor: 1, mobile: true });
  const mobile = await eventually(`(() => {
    const guide = document.querySelector("[data-measurement-guide]");
    if (!guide) return null;
    const card = guide.querySelector(".measurement-field-card");
    const diagram = guide.querySelector(".measurement-diagram-grid");
    return {
      fields: guide.querySelectorAll("[data-measurement-field]").length,
      cardColumns: getComputedStyle(card).gridTemplateColumns.split(" ").length,
      diagramColumns: getComputedStyle(diagram).gridTemplateColumns.split(" ").length,
      bodyWidth: document.body.scrollWidth,
      viewport: innerWidth
    };
  })()`);
  assert.equal(mobile.fields, 9);
  assert.equal(mobile.cardColumns, 1);
  assert.equal(mobile.diagramColumns, 1);
  assert.ok(mobile.bodyWidth <= mobile.viewport + 1);
  assert.deepEqual(exceptions, []);
  console.log(JSON.stringify({ desktop, mobile, screenshot: output }, null, 2));
} finally {
  socket.close();
}
