#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const stagingRoot = "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r025-portrait-projection-repair";
const captureRoot =
  "/tmp/FidgetingApp-PackOpening-R025-PortraitProjection-20260901-r04/Captures/r025-full-proof";
const output = path.join(stagingRoot, "r025-full-proof-full-size-review.json");

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function record(relative) {
  const source = path.join(captureRoot, relative);
  if (!fs.existsSync(source)) {
    throw new Error(`Missing R025 proof artifact: ${relative}`);
  }
  return {
    path: `full-proof/${relative}`,
    sha256: sha256(source),
    sizeBytes: fs.statSync(source).size
  };
}

function probe(relative) {
  const source = path.join(captureRoot, relative);
  return JSON.parse(execFileSync(
    "ffprobe",
    [
      "-v", "error",
      "-show_entries",
      "format=duration:stream=codec_name,profile,width,height,r_frame_rate,nb_frames",
      "-of", "json",
      source
    ],
    { encoding: "utf8" }
  ));
}

if (fs.existsSync(output)) {
  throw new Error(`Refusing to overwrite R025 proof review: ${output}`);
}
const report = JSON.parse(fs.readFileSync(
  path.join(captureRoot, "unity-capture-report.json"),
  "utf8"
));
if (
  report.status !== "structural-pass-awaiting-full-size-visual-inspection"
  || report.width !== 1206
  || report.height !== 2622
  || !report.targetProjectionApplied
  || report.frames !== 96
  || report.durationSeconds < 1.2
  || report.durationSeconds > 1.8
  || report.visualEffectsIntensity !== 0
  || !report.checks.every((check) => check.passed)
) {
  throw new Error("R025 full proof is not eligible for review.");
}
const normal = probe("normal/normal-speed-proof.mp4");
const slow = probe("tear-quarter-speed/tear-quarter-speed-closeup.mp4");
const normalStream = normal.streams?.[0];
const slowStream = slow.streams?.[0];
if (
  normalStream?.codec_name !== "h264"
  || normalStream?.profile !== "High"
  || normalStream?.width !== 1206
  || normalStream?.height !== 2622
  || normalStream?.r_frame_rate !== "60/1"
  || normalStream?.nb_frames !== "96"
  || Number(normal.format?.duration) !== 1.6
  || slowStream?.codec_name !== "h264"
  || slowStream?.profile !== "High"
  || slowStream?.width !== 1206
  || slowStream?.height !== 2622
  || slowStream?.r_frame_rate !== "60/1"
  || slowStream?.nb_frames !== "173"
) {
  throw new Error("R025 proof encodes do not preserve the Unity frame sequence.");
}

const review = {
  schema: "premium-display-case-gate04-r025-full-proof-review.v1",
  reviewedAt: new Date().toISOString(),
  source: "actual isolated Unity 6000.5.6f1 URP PNG frames",
  nativeSize: [1206, 2622],
  reviewMode: "full-size Unity PNG and source-derived H.264 review",
  proof: record("unity-capture-report.json"),
  normalSpeed: {
    recording: record("normal/normal-speed-proof.mp4"),
    contactSheet: record("normal/seven-pose-contact-sheet.png"),
    sampleFrames: [
      record("normal/primary/frame-0038.png"),
      record("normal/primary/frame-0046.png"),
      record("normal/primary/frame-0062.png")
    ],
    probe: normal
  },
  quarterSpeedCloseup: {
    recording: record("tear-quarter-speed/tear-quarter-speed-closeup.mp4"),
    sampleFrames: [
      record("tear-quarter-speed/frames/frame-0000.png"),
      record("tear-quarter-speed/frames/frame-0096.png"),
      record("tear-quarter-speed/frames/frame-0172.png")
    ],
    sourceSpeed: "0.25x",
    probe: slow
  },
  continuity: {
    caseInstances: report.caseInstances,
    caseGeometryBaked: report.caseGeometryBaked,
    maximumProjectedCenterStep: report.maximumProjectedCenterStep,
    maximumProjectedHeightStep: report.maximumProjectedHeightStep,
    maximumRootPositionStepMeters: report.maximumRootPositionStepMeters,
    frameBarrier: [
      report.frameBarrierCaptureCount,
      report.frameBarrierAdvancedCount
    ],
    visualEffectsIntensity: report.visualEffectsIntensity
  },
  verdict: "gate04-candidate-awaiting-user-visual-approval",
  shippingReady: false,
  physicalPhoneInstalled: false,
  statusText: "视觉批准待确认，未推送手机"
};
fs.writeFileSync(output, `${JSON.stringify(review, null, 2)}\n`, {
  flag: "wx"
});
console.log(JSON.stringify({
  output,
  normalFrames: normalStream.nb_frames,
  slowFrames: slowStream.nb_frames,
  verdict: review.verdict
}, null, 2));
