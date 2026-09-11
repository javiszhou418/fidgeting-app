import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9227";
const baseUrl = process.env.MODEL_EXPLORER_BASE_URL || "http://127.0.0.1:8891";
const screenshot = process.env.BROWSER_SMOKE_SCREENSHOT
  || "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate11-r010-blocked-workbench.png";
const validationPath = process.env.BROWSER_VALIDATION
  || "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-010/browser-validation.json";
const assetId = "magnetic-slide-tile-unity-parity-interactive-recording-r010";
const reviewUrl = `${baseUrl}/tools/model-provenance-explorer/?model=magnetic-slide-tile&tab=unity&gate=11-unity-parity&asset=${assetId}`;

const targets = await fetch(`${endpoint}/json/list`).then((response) => response.json());
const target = targets.find((candidate) => candidate.type === "page");
assert.ok(target, "Open a CDP browser page before running this test.");
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
  const timeout = setTimeout(() => {
    pending.delete(id);
    reject(new Error(`Timed out waiting for CDP ${method}.`));
  }, 15000);
  pending.set(id, {
    resolve: (value) => {
      clearTimeout(timeout);
      resolve(value);
    },
    reject: (error) => {
      clearTimeout(timeout);
      reject(error);
    },
  });
  socket.send(JSON.stringify({ id, method, params }));
});
const evaluate = async (expression) => {
  const response = await call("Runtime.evaluate", {
    expression,
    awaitPromise: true,
    returnByValue: true,
  });
  if (response.exceptionDetails) throw new Error("Browser evaluation failed.");
  return response.result.value;
};
const delay = (milliseconds) => new Promise((resolve) => setTimeout(resolve, milliseconds));
const eventually = async (expression, description, timeout = 10000) => {
  const started = Date.now();
  while (Date.now() - started < timeout) {
    const value = await evaluate(expression);
    if (value) return value;
    await delay(100);
  }
  assert.fail(`Timed out waiting for ${description}.`);
};

try {
  await call("Runtime.enable");
  await call("Page.enable");
  await call("Network.enable");
  await call("Network.setCacheDisabled", { cacheDisabled: true });
  await call("Emulation.setDeviceMetricsOverride", {
    width: 1440,
    height: 1000,
    deviceScaleFactor: 1,
    mobile: false,
  });
  await call("Page.navigate", { url: reviewUrl });
  await eventually(`document.readyState === "complete"`, "Gate 11 navigation");
  const desktop = await eventually(`(() => {
    const progress = document.querySelector(".canonical-progress");
    const recording = document.querySelector('[data-asset-id="${assetId}"]');
    const dialogVideo = document.querySelector("dialog[open] video");
    const issues = [...document.querySelectorAll(".issue-list .issue")];
    if (!progress || !recording || !dialogVideo || issues.length !== 3) return null;
    return {
      currentGate: progress.dataset.currentGate,
      approved: progress.dataset.approvedCount,
      roadmap: document.querySelectorAll(".gate-roadmap-item").length,
      workspaceTabs: document.querySelectorAll("[data-workspace-tab]").length,
      unityActive: document.querySelector('[data-workspace-tab="unity"]')
        ?.classList.contains("is-active"),
      gate11Status: document.querySelector(
        '.gate-roadmap-item[data-stage-id="11-unity-parity"]'
      )?.dataset.status,
      visibleAssets: document.querySelectorAll(".asset-panel [data-asset-id]").length,
      issueCount: issues.length,
      issueText: issues.map((issue) => issue.textContent),
      approvalAbsent: !document.getElementById("approve-stage"),
      modalVideoSource: dialogVideo.currentSrc || dialogVideo.src,
      route: location.search,
    };
  })()`, "blocked Gate 11 recording");
  assert.equal(desktop.currentGate, "11");
  assert.equal(desktop.approved, "10");
  assert.equal(desktop.roadmap, 12);
  assert.equal(desktop.workspaceTabs, 7);
  assert.equal(desktop.unityActive, true);
  assert.equal(desktop.gate11Status, "draft");
  assert.equal(desktop.visibleAssets, 4);
  assert.equal(desktop.issueCount, 3);
  assert.equal(desktop.approvalAbsent, true);
  assert.match(desktop.modalVideoSource, /unity-gate11-r010-interactive-review\.mp4/);
  assert.match(desktop.route, new RegExp(`asset=${assetId}`));

  const capture = await call("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: false,
  });
  fs.mkdirSync(path.dirname(screenshot), { recursive: true });
  fs.writeFileSync(screenshot, Buffer.from(capture.data, "base64"));

  await evaluate(`document.getElementById("dialog-close").click()`);
  await eventually(`!document.querySelector("dialog[open]")`, "modal close");
  const restored = await eventually(`(() => {
    const progress = document.querySelector(".canonical-progress");
    if (!progress) return null;
    return {
      gate: progress.dataset.currentGate,
      unityActive: document.querySelector('[data-workspace-tab="unity"]')
        ?.classList.contains("is-active"),
      approvalAbsent: !document.getElementById("approve-stage"),
      route: location.search,
    };
  })()`, "stable Gate 11 workbench");
  assert.equal(restored.gate, "11");
  assert.equal(restored.unityActive, true);
  assert.equal(restored.approvalAbsent, true);
  assert.doesNotMatch(restored.route, /asset=/);

  await call("Emulation.setDeviceMetricsOverride", {
    width: 390,
    height: 844,
    deviceScaleFactor: 1,
    mobile: true,
  });
  await call("Page.reload", { ignoreCache: true });
  const mobile = await eventually(`(() => {
    const progress = document.querySelector(".canonical-progress");
    if (!progress) return null;
    return {
      currentGate: progress.dataset.currentGate,
      roadmap: document.querySelectorAll(".gate-roadmap-item").length,
      bodyWidth: document.body.scrollWidth,
      viewportWidth: innerWidth,
      approvalAbsent: !document.getElementById("approve-stage"),
    };
  })()`, "mobile blocked Gate 11");
  assert.equal(mobile.currentGate, "11");
  assert.equal(mobile.roadmap, 12);
  assert.ok(mobile.bodyWidth <= mobile.viewportWidth + 1);
  assert.equal(mobile.approvalAbsent, true);
  assert.deepEqual(runtimeExceptions, []);
  assert.deepEqual(loadingFailures, []);

  const report = {
    schemaVersion: 1,
    gate: "11-unity-parity",
    revision: 10,
    status: "blocked-not-ready-for-review",
    reviewUrl,
    desktop,
    restored,
    mobile,
    screenshot,
    runtimeExceptionCount: runtimeExceptions.length,
    loadingFailureCount: loadingFailures.length,
    pass: true,
  };
  fs.mkdirSync(path.dirname(validationPath), { recursive: true });
  fs.writeFileSync(validationPath, JSON.stringify(report, null, 2) + "\n");
  console.log(JSON.stringify(report, null, 2));
} finally {
  socket.close();
}
