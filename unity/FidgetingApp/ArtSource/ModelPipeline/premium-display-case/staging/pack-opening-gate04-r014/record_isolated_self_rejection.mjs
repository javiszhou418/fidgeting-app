#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const repo = "/Users/jiawei.zhou/Documents/Fidgeting app";
const isolated = "/tmp/FidgetingApp-PackOpening-R014-Isolated-20260831";
const output = path.join(
  repo,
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-014/isolated-unity-self-rejection.json"
);
const blackFrame = path.join(
  isolated,
  "Captures/normal/primary/pose-043.png"
);
const sourceManifest = path.join(isolated, "Assets/Source/isolated-source-manifest.json");

if (fs.existsSync(output)) {
  throw new Error(`Refusing to overwrite immutable self-rejection: ${output}`);
}
for (const file of [blackFrame, sourceManifest]) {
  if (!fs.existsSync(file)) throw new Error(`Missing isolated proof file: ${file}`);
}
const sha256 = (file) =>
  crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
fs.mkdirSync(path.dirname(output), { recursive: true });
fs.writeFileSync(output, `${JSON.stringify({
  schema: "premium-display-case-gate04-r014-isolated-self-rejection.v1",
  isolatedUnityCandidate: true,
  shippingIntegration: false,
  shippingReady: false,
  deviceInstalled: false,
  outcome: "self-rejected",
  reviewedAt: new Date().toISOString(),
  visualBlocker:
    "All 1206×2622 captured Unity frames are black, so the foil tear, pouch cavity, and contained live case are not visually inspectable.",
  correctionPassesUsed: 1,
  correction:
    "Replaced unsupported Camera.Render capture with URP StandardRequest capture; output remained black because the isolated URP asset has no default renderer.",
  nonPromotedCapture: {
    width: 1206,
    height: 2622,
    frameRate: 60,
    durationSeconds: 1.6,
    representativeFrameSha256: sha256(blackFrame),
    sourceImportManifestSha256: sha256(sourceManifest),
    retention: "not promoted as a primary or approval artifact"
  },
  sourceMapping: {
    direct: [
      "R014 Pack-only Blender FBX",
      "384×512 standard Pack artwork",
      "Gate 11 assembled Premium Display Case FBX/prefab with empty caller-owned ContentSlot",
      "Make It Shine CC0 curves and masks"
    ],
    adapted: [
      "R014 sequence capture code adapted into the isolated URP project"
    ],
    rejected: [
      "Make It Shine sample VFX, particles, sample Booster/Card models, and branded artwork"
    ]
  },
  approvalRequestAllowed: false,
  statusText: "视觉批准待确认，未推送手机"
}, null, 2)}\n`);
console.log(output);
