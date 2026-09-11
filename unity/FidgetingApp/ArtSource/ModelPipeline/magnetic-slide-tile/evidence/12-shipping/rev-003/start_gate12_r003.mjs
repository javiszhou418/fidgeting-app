#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  digestValues,
  loadManifest,
  resolveRepoPath,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-003";
const attachment =
  "/Users/jiawei.zhou/.cursor/projects/Users-jiawei-zhou-Documents-Fidgeting-app/assets/image-e3ced198-7072-4920-b57c-0c3094204595.png";
const archivedScreenshot =
  `${evidenceRoot}/user-feedback-exploded-motion-r002.png`;
const exactFeedback =
  "all other views are correct, but `最大滑开` and `端点 12°` are wrong because top and bottom are shown vertically separated/exploded and rotation is not represented correctly.";

fs.mkdirSync(resolveRepoPath(evidenceRoot), { recursive: true });
fs.copyFileSync(attachment, resolveRepoPath(archivedScreenshot));
const screenshotSha256 = sha256File(resolveRepoPath(archivedScreenshot));
if (screenshotSha256
  !== "d36fb987ee46313fe401337a61552d6e80c3310f9ccdb9852938edee4191015b") {
  throw new Error("User feedback screenshot hash changed.");
}

fs.writeFileSync(
  resolveRepoPath(`${evidenceRoot}/user-feedback.json`),
  `${JSON.stringify({
    schemaVersion: 1,
    modelId,
    gate: "12-shipping",
    rejectedEvidenceRevision: 2,
    exactFeedback,
    screenshotPath: archivedScreenshot,
    screenshotSha256,
    acceptedViews: [
      "library", "hero", "top", "left-oblique",
      "right-oblique", "low", "phone",
    ],
    rejectedViews: [
      "max-open", "endpoint-12deg", "endpoint-36deg",
      "endpoint-360deg", "unity-playmode-video", "shipping-board",
      "motion-board",
    ],
    requiredFix:
      "Keep one connected product. Preserve stack height and use in-plane "
      + "translation plus rotation about the fixed axis.",
    buildInstallPhone: false,
  }, null, 2)}\n`,
);

const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
if (
  gate12?.status !== "ready_for_review"
  || gate12?.shippingSpec?.revision !== 2
) {
  throw new Error("Expected Gate 12 rev 2 ready for review.");
}

const decidedAt = new Date().toISOString();
gate12.historicalRevisions ||= [];
gate12.historicalRevisions.push({
  evidenceRevision: 2,
  stageRevision: gate12.revision,
  status: "partially-approved-revision-requested",
  artifactIds: [...gate12.artifactIds],
  reviewArtifactIds: [...gate12.reviewArtifactIds],
  validations: [...gate12.validations],
  shippingSpec: gate12.shippingSpec,
  decision: {
    action: "partial-approve-and-revise",
    notes: exactFeedback,
    decidedBy: "user",
    decidedAt,
    acceptedViews: [
      "library", "hero", "top", "left-oblique",
      "right-oblique", "low", "phone",
    ],
    rejectedMotionViews: [
      "max-open", "endpoint-12deg", "endpoint-36deg",
      "endpoint-360deg", "unity-playmode-video",
    ],
    screenshotSha256,
  },
  preservedForHistory: true,
});

for (const assetId of gate12.artifactIds) {
  const asset = manifest.assets.find((item) => item.id === assetId);
  if (asset)
    asset.reviewState = assetId.includes("-view-library-")
      || assetId.includes("-view-hero-")
      || assetId.includes("-view-top-")
      || assetId.includes("-view-left-oblique-")
      || assetId.includes("-view-right-oblique-")
      || assetId.includes("-view-low-")
      || assetId.includes("-view-phone-")
      ? "user-accepted-preserved-history"
      : "superseded-motion-review-history";
}

const priorClaim = manifest.claims.find(
  (claim) => claim.id === "slider-gate12-r002-shipping-candidate");
if (priorClaim) {
  priorClaim.state = "partially-approved-superseded";
  priorClaim.decisionState =
    "static-views-approved-motion-views-revision-requested";
}

gate12.revision += 1;
gate12.status = "draft";
gate12.artifactIds = [];
gate12.reviewArtifactIds = [];
gate12.validations = [];
gate12.decision = null;
gate12.shippingSpec = {
  ...gate12.shippingSpec,
  revision: 3,
  sourceEvidenceRevision: 2,
  userFeedbackScreenshotSha256: screenshotSha256,
  acceptedStaticViewsPreserved: true,
  productMotionCorrection:
    "local -Y in-plane slide; local +Z fixed-axis rotation; zero stack lift",
  gate12Approval: "pending",
  buildInstallPhone: false,
  deviceAcceptance: "pending",
};
gate12.readiness = {
  ready: false,
  blockers: [
    "Corrected connected-product motion views, recording and transform tests are pending.",
  ],
  note:
    "Seven Gate 12 static views are accepted. Motion evidence revision 3 is in progress.",
};

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((claim) => claim.stageId === stage.id)
    .map((claim) => JSON.stringify(claim));
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = decidedAt;
manifest.currentStageId = "12-shipping";
manifest.currentState.visualApproval =
  "gate12-r002-static-views-approved-motion-r003-in-progress";
manifest.currentState.unityStatus =
  "gate12-r003-connected-product-motion-fix-in-progress";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.deviceStatus = "pending-not-installed";
manifest.currentState.diagnosis =
  "Gate 12 rev 2 static views are accepted. Product motion used converted "
  + "axes that lifted and tilted the top; rev 3 corrects motion only.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate12-r002-partial-approval-r003-motion-fix-started",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: decidedAt,
  gate: "12-shipping",
  rejectedEvidenceRevision: 2,
  nextEvidenceRevision: 3,
  exactUserWording: exactFeedback,
  screenshotPath: archivedScreenshot,
  screenshotSha256,
  acceptedViews: gate12.historicalRevisions.at(-1).decision.acceptedViews,
  requiredMotion: {
    slide: "s=sMax, theta=0, in-plane only",
    detents: "s=sMax, local +Z fixed-axis rotation",
    stackLiftMeters: 0,
  },
  buildInstallPhone: false,
});

console.log(JSON.stringify({
  revision: saved.revision,
  gate12: saved.stages[11].status,
  evidenceRevision: saved.stages[11].shippingSpec.revision,
  screenshotSha256,
}, null, 2));
