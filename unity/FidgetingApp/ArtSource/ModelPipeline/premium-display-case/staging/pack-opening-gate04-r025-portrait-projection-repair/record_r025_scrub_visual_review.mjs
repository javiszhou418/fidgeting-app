#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const stagingRoot = "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r025-portrait-projection-repair";
const captureRoot =
  "/tmp/FidgetingApp-PackOpening-R025-PortraitProjection-20260901-r04/Captures/r025-scrub";
const output = path.join(stagingRoot, "r025-scrub-full-size-review.json");

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function record(relative) {
  const source = path.join(captureRoot, relative);
  if (!fs.existsSync(source)) {
    throw new Error(`Missing R025 scrub artifact: ${relative}`);
  }
  return {
    path: `scrub/${relative}`,
    sha256: sha256(source),
    sizeBytes: fs.statSync(source).size
  };
}

if (fs.existsSync(output)) {
  throw new Error(`Refusing to overwrite R025 scrub review: ${output}`);
}
const report = JSON.parse(fs.readFileSync(
  path.join(captureRoot, "scrub-report.json"),
  "utf8"
));
if (
  report.status !== "captured-awaiting-full-size-visual-inspection"
  || !report.targetProjectionApplied
  || report.frameCount !== 31
  || !report.sameCaseIdentity
  || !report.noDuplicateCaseRenderers
  || !report.noPackCrossfade
  || !report.noBlankFrame
  || report.checks.some((check) => !check.passed)
) {
  throw new Error("R025 scrub is not eligible for full-size review.");
}

const review = {
  schema: "premium-display-case-gate04-r025-scrub-full-size-review.v1",
  reviewedAt: new Date().toISOString(),
  source: "actual isolated Unity 6000.5.6f1 URP frames",
  nativeSize: [report.width, report.height],
  reviewMode: "native-size Unity PNG inspection without resampling",
  scrub: record("scrub-report.json"),
  results: record("r025-scrub-results.xml"),
  frames: [
    record("frames/frame-0000.png"),
    record("frames/frame-0012.png"),
    record("frames/frame-0026.png")
  ],
  inspectedSeconds: [0.7, 0.9, 1.1333333],
  continuity: {
    sameCaseIdentity: report.sameCaseIdentity,
    noDuplicateCaseRenderers: report.noDuplicateCaseRenderers,
    noPackCrossfade: report.noPackCrossfade,
    noBlankFrame: report.noBlankFrame,
    maximumCaseCenterStep: report.maximumCaseCenterStep,
    maximumCaseHeightStep: report.maximumCaseHeightStep,
    frameBarrier: [
      report.frameBarrierCaptureCount,
      report.frameBarrierAdvancedCount
    ]
  },
  verdict: "pass-for-full-proof",
  nextGate: "capture 1.6 s normal proof and 0.25x closeup",
  shippingReady: false,
  physicalPhoneInstalled: false,
  statusText: "视觉批准待确认，未推送手机"
};
fs.writeFileSync(output, `${JSON.stringify(review, null, 2)}\n`, {
  flag: "wx"
});
console.log(JSON.stringify({
  output,
  verdict: review.verdict,
  frames: review.frames.length
}, null, 2));
