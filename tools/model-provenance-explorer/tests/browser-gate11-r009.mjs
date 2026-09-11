import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9223";
const baseUrl = process.env.MODEL_EXPLORER_BASE_URL || "http://127.0.0.1:8891";
const screenshot = process.env.BROWSER_SMOKE_SCREENSHOT
  || "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate11-r009-workbench.png";
const validationPath = process.env.BROWSER_VALIDATION
  || "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-009/browser-validation.json";
const reviewUrl = `${baseUrl}/tools/model-provenance-explorer/?model=magnetic-slide-tile&tab=unity&gate=11-unity-parity`;

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
  if (response.exceptionDetails) {
    throw new Error(response.exceptionDetails.text || "Browser evaluation failed.");
  }
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
  await evaluate(`(() => {
    localStorage.removeItem("fidgeting-model-workspace-v2:magnetic-slide-tile");
    localStorage.removeItem(
      "magnetic-slide-tile-gate11-r009-recording-complete"
    );
    return true;
  })()`);
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
    const unityTab = document.querySelector('[data-workspace-tab="unity"]');
    const heading = document.querySelector(".plain-unity-parity-heading h2");
    const recording = document.querySelector(
      '[data-asset-id="magnetic-slide-tile-unity-parity-interactive-recording-r009"]'
    );
    const board = document.querySelector(
      '[data-asset-id="magnetic-slide-tile-unity-parity-parity-board-r009"]'
    );
    const approve = document.getElementById("approve-stage");
    if (!progress || !unityTab || !heading || !recording || !board || !approve) return null;
    return {
      currentGate: progress.dataset.currentGate,
      approved: progress.dataset.approvedCount,
      roadmap: document.querySelectorAll(".gate-roadmap-item").length,
      workspaceTabs: document.querySelectorAll("[data-workspace-tab]").length,
      unityActive: unityTab.classList.contains("is-active"),
      gate11Current: document.querySelector(
        '.gate-roadmap-item[data-stage-id="11-unity-parity"]'
      )?.dataset.status,
      heading: heading.textContent,
      visibleAssets: document.querySelectorAll(".asset-panel [data-asset-id]").length,
      approvalDisabled: approve.disabled,
      recordingStatus: document.querySelector(
        "[data-gate11-recording-status]"
      )?.textContent,
      bodyClass: document.body.classList.contains("plain-gate11-review"),
    };
  })()`, "Gate 11 review content");

  assert.equal(desktop.currentGate, "11");
  assert.equal(desktop.approved, "10");
  assert.equal(desktop.roadmap, 12);
  assert.equal(desktop.workspaceTabs, 7);
  assert.equal(desktop.unityActive, true);
  assert.equal(desktop.gate11Current, "ready_for_review");
  assert.match(desktop.heading, /Unity 四轨候选/);
  assert.equal(desktop.visibleAssets, 4);
  assert.equal(desktop.approvalDisabled, true);
  assert.match(desktop.recordingStatus, /请先完整播放/);
  assert.equal(desktop.bodyClass, true);

  const capture = await call("Page.captureScreenshot", {
    format: "png",
    captureBeyondViewport: false,
  });
  fs.mkdirSync(path.dirname(screenshot), { recursive: true });
  fs.writeFileSync(screenshot, Buffer.from(capture.data, "base64"));

  await evaluate(`document.querySelector(
    '[data-asset-id="magnetic-slide-tile-unity-parity-interactive-recording-r009"]'
  ).click()`);
  await eventually(`document.querySelector("dialog[open] video")`, "Unity recording modal");
  await evaluate(`(() => {
    const video = document.querySelector("dialog[open] video");
    video.dispatchEvent(new Event("ended"));
    return true;
  })()`);
  const unlocked = await evaluate(`(() => ({
    stored: localStorage.getItem(
      "magnetic-slide-tile-gate11-r009-recording-complete"
    ),
    approvalDisabled: document.getElementById("approve-stage").disabled,
    status: document.querySelector("[data-gate11-recording-status]").textContent,
    modalVideo: Boolean(document.querySelector("dialog[open] video")),
  }))()`);
  assert.equal(unlocked.stored, "true");
  assert.equal(unlocked.approvalDisabled, false);
  assert.match(unlocked.status, /可以确认/);
  assert.equal(unlocked.modalVideo, true);

  await evaluate(`document.getElementById("dialog-close").click()`);
  await eventually(`document.readyState === "complete"`, "return to workbench");
  await eventually(`!document.querySelector("dialog[open]")`, "closed Unity recording");
  await call("Page.reload", { ignoreCache: true });
  const restored = await eventually(`(() => {
    const approve = document.getElementById("approve-stage");
    if (!approve) return null;
    return {
      gate: document.querySelector(".canonical-progress")?.dataset.currentGate,
      unityActive: document.querySelector(
        '[data-workspace-tab="unity"]'
      )?.classList.contains("is-active"),
      approvalDisabled: approve.disabled,
      route: location.search,
    };
  })()`, "Gate 11 route restoration");
  assert.equal(restored.gate, "11");
  assert.equal(restored.unityActive, true);
  assert.equal(restored.approvalDisabled, false);
  assert.match(restored.route, /gate=11-unity-parity/);

  await call("Emulation.setDeviceMetricsOverride", {
    width: 390,
    height: 844,
    deviceScaleFactor: 1,
    mobile: true,
  });
  await call("Page.reload", { ignoreCache: true });
  const mobile = await eventually(`(() => {
    const progress = document.querySelector(".canonical-progress");
    const heading = document.querySelector(".plain-unity-parity-heading h2");
    if (!progress || !heading) return null;
    return {
      currentGate: progress.dataset.currentGate,
      roadmap: document.querySelectorAll(".gate-roadmap-item").length,
      unityActive: document.querySelector(
        '[data-workspace-tab="unity"]'
      )?.classList.contains("is-active"),
      bodyWidth: document.body.scrollWidth,
      viewportWidth: innerWidth,
      runtimeText: heading.textContent,
    };
  })()`, "mobile Gate 11 review");
  assert.equal(mobile.currentGate, "11");
  assert.equal(mobile.roadmap, 12);
  assert.equal(mobile.unityActive, true);
  assert.ok(mobile.bodyWidth <= mobile.viewportWidth + 1);
  assert.match(mobile.runtimeText, /Unity 四轨候选/);
  assert.deepEqual(runtimeExceptions, []);
  assert.deepEqual(loadingFailures, []);

  const report = {
    schemaVersion: 1,
    gate: "11-unity-parity",
    revision: 9,
    reviewUrl,
    desktop,
    unlocked,
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
