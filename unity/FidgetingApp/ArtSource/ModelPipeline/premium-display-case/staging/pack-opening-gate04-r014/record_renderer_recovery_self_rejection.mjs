#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const repo = "/Users/jiawei.zhou/Documents/Fidgeting app";
const isolated = "/tmp/FidgetingApp-PackOpening-R014-Isolated-20260831";
const output = path.join(
  repo,
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-014/renderer-recovery-full-size-self-rejection.json"
);
const frames = [0, 16, 29, 43, 59, 74].map((frame) =>
  path.join(isolated, "Captures/normal/primary", `pose-${String(frame).padStart(3, "0")}.png`)
);
const manifest = path.join(isolated, "isolated-build-manifest.json");

if (fs.existsSync(output)) throw new Error(`Refusing to overwrite: ${output}`);
for (const file of [...frames, manifest]) {
  if (!fs.existsSync(file)) throw new Error(`Missing capture evidence: ${file}`);
}
const sha256 = (file) =>
  crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
fs.writeFileSync(output, `${JSON.stringify({
  schema: "premium-display-case-gate04-r014-isolated-renderer-recovery.v1",
  isolatedUnityCandidate: true,
  shippingIntegration: false,
  shippingReady: false,
  outcome: "self-rejected",
  reviewedAt: new Date().toISOString(),
  rendererRecovery: {
    pipeline: "IsolatedR014URPFixed.asset",
    rendererData: "IsolatedR014Renderer.asset",
    unity: "6000.5.6f1",
    urp: "17.5.0",
    sanityCapture: "passed non-black"
  },
  visualBlocker:
    "At full size, the Pack reads as a thin horizontal planar strip across the case instead of a visible deep pouch mouth, so the case cannot be visually proven contained before emergence.",
  fullSizeFrames: frames.map((file) => ({
    frame: path.basename(file),
    sha256: sha256(file)
  })),
  buildManifestSha256: sha256(manifest),
  approvalRequestAllowed: false,
  captureRetention: "isolated diagnostic only; no primary evidence promoted",
  statusText: "视觉批准待确认，未推送手机"
}, null, 2)}\n`);
console.log(output);
