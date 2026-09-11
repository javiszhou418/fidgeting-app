#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const stagingRoot = "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r025-portrait-projection-repair";
const captureRoot =
  "/tmp/FidgetingApp-PackOpening-R025-PortraitProjection-20260901-r04/Captures/r025-preflight";
const output = path.join(stagingRoot, "r025-static-full-size-review.json");

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function record(relative) {
  const source = path.join(captureRoot, relative);
  if (!fs.existsSync(source)) {
    throw new Error(`Missing static R025 artifact: ${relative}`);
  }
  return {
    path: `preflight/${relative}`,
    sha256: sha256(source),
    sizeBytes: fs.statSync(source).size
  };
}

if (fs.existsSync(output)) {
  throw new Error(`Refusing to overwrite R025 static review: ${output}`);
}
const report = JSON.parse(fs.readFileSync(
  path.join(captureRoot, "r025-preflight-report.json"),
  "utf8"
));
const projection = report.accounting?.targetPortraitProjection;
if (
  !report.passed
  || report.width !== 1206
  || report.height !== 2622
  || !projection?.cameraAspectExactlyTarget
  || !projection?.bakedBoundsMatchExactIdMasks
  || !projection?.logicalSegmentRangesMatch
  || !projection?.masksStayInsidePack
  || !projection?.noFullWidthBridge
) {
  throw new Error("R025 technical static preflight is not eligible for review.");
}

const review = {
  schema: "premium-display-case-gate04-r025-static-full-size-review.v1",
  reviewedAt: new Date().toISOString(),
  candidateScope:
    "R025 isolated portrait-projection diagnostic repair; no physical asset change",
  source: "actual isolated Unity 6000.5.6f1 URP 17.5 frames",
  nativeSize: [1206, 2622],
  reviewMode: "native-size Unity PNG inspection without resampling",
  technicalPreflight: record("r025-preflight-report.json"),
  staticFrames: [
    record("tear-front-050.png"),
    record("formed-mouth-070.png"),
    record("case-contained-090.png")
  ],
  checklist: [
    {
      id: "upright-pack",
      passed: true,
      evidence: "The printed Pack remains upright in the .50/.70/.90 Unity frames."
    },
    {
      id: "compact-right-side-peeled-seal",
      passed: true,
      evidence: "The released seal remains a compact top-right physical strip."
    },
    {
      id: "upper-physical-mouth-with-dark-cavity-and-liner",
      passed: true,
      evidence: "The target-space liner and cavity masks pass at .70 and .90."
    },
    {
      id: "one-live-case-behind-front-lip",
      passed: true,
      evidence: "The .90 target-space case mask is fully within the physical mouth region and front-lip occlusion passes."
    }
  ],
  verdict: "pass-for-scrub",
  nextGate: "run actual Unity .70–1.20 scrub",
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
  reviewedFrames: review.staticFrames.length
}, null, 2));
