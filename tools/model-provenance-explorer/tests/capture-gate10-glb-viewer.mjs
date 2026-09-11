import fs from "node:fs";
import path from "node:path";
import WebSocket from "ws";

const endpoint = process.env.CDP_ENDPOINT || "http://127.0.0.1:9227";
const url = "http://127.0.0.1:8891/tools/model-provenance-explorer/?model=magnetic-slide-tile&tab=materials&gate=10-export&asset=magnetic-slide-tile-export-glb-r009";
const output = path.resolve("../../Artifacts/ModelProvenanceExplorer/magnetic-slide-gate10-rev9-glb-viewer.png");
const targets = await fetch(`${endpoint}/json/list`).then((response) => response.json());
const target = targets.find((candidate) => candidate.type === "page");
const socket = new WebSocket(target.webSocketDebuggerUrl);
await new Promise((resolve, reject) => {
  socket.addEventListener("open", resolve, { once: true });
  socket.addEventListener("error", reject, { once: true });
});
let sequence = 0;
const pending = new Map();
socket.addEventListener("message", (event) => {
  const message = JSON.parse(event.data);
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
const evaluate = async (expression) => (await call("Runtime.evaluate", { expression, returnByValue: true })).result.value;
await call("Page.enable");
await call("Emulation.setDeviceMetricsOverride", { width: 1440, height: 1000, deviceScaleFactor: 1, mobile: false });
await call("Page.navigate", { url });
for (let attempt = 0; attempt < 300; attempt += 1) {
  if (await evaluate(`Boolean(document.querySelector('#asset-dialog[open] .model-viewer canvas'))`)) break;
  await new Promise((resolve) => setTimeout(resolve, 100));
}
await new Promise((resolve) => setTimeout(resolve, 1200));
const screenshot = await call("Page.captureScreenshot", { format: "png", fromSurface: true });
fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, Buffer.from(screenshot.data, "base64"));
socket.close();
console.log(output);

