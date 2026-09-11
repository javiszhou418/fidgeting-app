#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import {
  digestValues,
  loadManifest,
  resolveRepoPath,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-004";
const candidateRoot =
  "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate08R004NeutralParity";
const manifest = loadManifest(modelId);
const stage = manifest.stages.find((item) => item.id === "08-lighting");
if (manifest.revision !== 208 || stage?.lightingSpec?.revision !== 4) {
  throw new Error("Expected Gate 08 rev 4 at pipeline revision 208.");
}

const report = JSON.parse(
  fs.readFileSync(resolveRepoPath(
    `${evidenceRoot}/gate08-r004-synchronized-preview-report.json`
  ))
);
const rejection = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/preview-flip-rejection.json`))
);
if (
  report.video.codec !== "h264"
  || report.video.durationSeconds !== 12
  || report.video.frameCount !== 360
  || report.alignment.minimumSilhouetteIoU < 0.999
  || !report.alignment.transformValidatorsPassedEveryFrame
  || rejection.attemptedVideo.registered
) {
  throw new Error("Corrected preview or rejection record failed registration.");
}

const definitions = [
  [
    "corrected-synchronized-preview",
    "lighting-comparison-recording",
    `${evidenceRoot}/gate08-r004-synchronized-portable-parity.mp4`,
    "source-model",
  ],
  [
    "corrected-synchronized-poster",
    "lighting-comparison-poster",
    `${evidenceRoot}/gate08-r004-synchronized-portable-parity-poster.png`,
    "source-model",
  ],
  [
    "corrected-synchronized-report",
    "playback-and-transform-validation",
    `${evidenceRoot}/gate08-r004-synchronized-preview-report.json`,
    "validation",
  ],
  [
    "corrected-synchronized-blender-renderer",
    "recording-source",
    `${evidenceRoot}/render_synchronized_preview_blender.py`,
    "process",
  ],
  [
    "corrected-synchronized-unity-renderer",
    "recording-source",
    `${candidateRoot}/Editor/MagneticSlideTileNeutralParityPreviewBuilder.cs`,
    "process",
  ],
  [
    "corrected-synchronized-builder",
    "recording-source",
    `${evidenceRoot}/build_synchronized_preview.py`,
    "process",
  ],
  [
    "invalid-flip-feedback",
    "user-feedback",
    `${evidenceRoot}/user-feedback-invalid-vertical-flip.png`,
    "validation",
  ],
  [
    "invalid-flip-rejection",
    "decision-history",
    `${evidenceRoot}/preview-flip-rejection.json`,
    "validation",
  ],
  [
    "invalid-flip-archiver",
    "registration-source",
    `${evidenceRoot}/archive_preview_flip_rejection.mjs`,
    "process",
  ],
  [
    "corrected-preview-registrar",
    "registration-source",
    `${evidenceRoot}/register_corrected_preview.mjs`,
    "process",
  ],
];
const sourceAssetIds = [
  "magnetic-slide-tile-lighting-blend-r004",
  "magnetic-slide-tile-lighting-environment-r004",
  "magnetic-slide-tile-lighting-unity-scene-r004",
];
const records = definitions.map(([suffix, slot, assetPath, role]) => {
  const absolute = resolveRepoPath(assetPath);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${assetPath}`);
  const internal = suffix.startsWith("invalid-flip");
  return {
    id: `${modelId}-lighting-${suffix}-r004`,
    stageId: "08-lighting",
    slot,
    path: assetPath,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    reviewState: internal ? "rejected-internal" : "corrected-review",
    producer: {
      name: "Gate 08 corrected synchronized preview workflow",
      version: "Blender 5.2.0 / Unity 6000.5.6f1 / Python 3 / ffmpeg 8.1.1",
      recipe: `${evidenceRoot}/build_synchronized_preview.py`,
    },
    provenance: {
      origin: suffix === "invalid-flip-feedback"
        ? "user-provided"
        : "repository-generated",
      contentClass: slot,
      assertedBy: suffix === "invalid-flip-feedback" ? "user" : "assistant",
      gate08Revision: 4,
      note: internal
        ? "Rejected impossible-flip attempt. Internal history only."
        : "Corrected upright preview. No shipping, build, install or phone work.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);

const id = (suffix) => `${modelId}-lighting-${suffix}-r004`;
const oldRecording = manifest.assets.find(
  (asset) => asset.id === "magnetic-slide-tile-lighting-comparison-recording-r004"
);
if (oldRecording) {
  oldRecording.reviewState = "superseded-by-corrected-motion-safe-recording";
  oldRecording.preservedForHistory = true;
}
stage.historicalRevisions = stage.historicalRevisions || [];
stage.historicalRevisions.push({
  evidenceRevision: "4-invalid-preview-attempt-1",
  status: "rejected-internal-impossible-vertical-flip",
  artifactIds: [
    id("invalid-flip-feedback"),
    id("invalid-flip-rejection"),
    id("invalid-flip-archiver"),
  ],
  reviewArtifactIds: [],
  preservedForHistory: true,
  userDecision: rejection.userFeedbackExact,
});

stage.status = "blocked";
stage.decision = null;
stage.artifactIds = [
  ...stage.artifactIds,
  ...records.map((record) => record.id),
];
stage.reviewArtifactIds = [
  id("corrected-synchronized-preview"),
  id("corrected-synchronized-poster"),
  "magnetic-slide-tile-lighting-board-r004",
  "magnetic-slide-tile-lighting-blender-full-r004",
  "magnetic-slide-tile-lighting-unity-full-r004",
];
stage.validations = stage.validations.filter(
  (item) => item.id !== "motion-safe-synchronized-recording"
);
stage.validations.push({
  id: "motion-safe-synchronized-recording",
  status: "pass",
  evidence:
    `All 180 source frames passed transform checks; 165 rendered pairs ` +
    `reached silhouette IoU >=${report.alignment.minimumSilhouetteIoU.toFixed(6)} ` +
    `and centroid delta <=${report.alignment.maximumCentroidDeltaPixels.toFixed(3)} px. ` +
    "Camera orbit is horizontal, ±35°, constant-elevation and zero-roll.",
});
stage.lightingSpec.interactiveReviewArtifactId =
  id("corrected-synchronized-preview");
stage.lightingSpec.correctedRecording = report;
stage.lightingSpec.motionInvariant = {
  fixed: ["BottomBase", "whole assembly", "world-up", "fixed bottom axis"],
  movingTop: {
    pitchRollDegrees: [0, 0],
    yawAxis: "+Z only",
    translation: "approved local groove axis only",
  },
  carrier: "fixed +Z axis only",
  camera: "horizontal orbit, constant elevation, zero roll, stable world-up",
  negativeScaleOrInversion: false,
};
stage.lightingSpec.deliveryState.visualApproval = "pending-corrected-recording";

for (const downstream of manifest.stages.slice(8)) {
  downstream.status = "stale";
  downstream.staleReason =
    "Gate 08 rev 4 corrected recording awaits explicit visual approval.";
}
manifest.claims.push({
  id: "slider-gate08-r004-motion-safe-recording",
  stageId: "08-lighting",
  topic: "preview-motion-invariant",
  statement:
    "Bottom and world-up remain fixed. The top uses local-axis slide and +Z yaw only. Camera orbit has constant elevation and zero roll.",
  confidence: "verified",
  state: "active",
  assertedBy: "measurement",
  sourceAssetIds: [
    id("corrected-synchronized-preview"),
    id("corrected-synchronized-report"),
    id("invalid-flip-rejection"),
  ],
  sourceRegions: [],
  decisionState: "awaiting-corrected-recording-review",
  deliveryState: "not-shipping-not-device",
});
manifest.issues = (manifest.issues || []).filter(
  (issue) => issue.id !== "slider-gate08-r004-renewed-review"
);
manifest.issues.push({
  id: "slider-gate08-r004-corrected-recording-review",
  stageId: "08-lighting",
  assetId: id("corrected-synchronized-preview"),
  severity: "blocker",
  note:
    "Corrected upright recording is ready. Gate 08 remains blocked pending explicit visual approval.",
});

const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`
    ).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256
  );
  const claims = manifest.claims
    .filter((claim) => claim.stageId === current.id)
    .map(stableJson);
  current.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
manifest.currentStageId = "08-lighting";
manifest.currentState.visualApproval =
  "gate08-rev4-corrected-recording-pending-not-pushed";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.blenderModelingStatus =
  "gate08-rev4-blocked-pending-corrected-recording-review";
manifest.currentState.diagnosis =
  "The first supplemental recording attempt was rejected for an impossible vertical flip. The corrected 12-second Blender/Unity recording enforces fixed world-up, +Z-only top rotation, legal slide and horizontal camera orbit. Gate 08 remains blocked pending review; Gates 09-12 remain stale.";

const userDecisionExact =
  "The user rejects the preview video because it introduces an impossible vertical/card flip. Interrupt the active recording task. Mark the current invalid video as rejected/internal and do not register or present it as approval evidence.";
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate08-corrected-preview-recording",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "08-lighting",
  revision: 4,
  status: "blocked-pending-corrected-visual-review",
  artifactIds: records.map((record) => record.id),
  reviewArtifactIds: stage.reviewArtifactIds,
  rejectedArtifactIds: [
    id("invalid-flip-feedback"),
    id("invalid-flip-rejection"),
  ],
  userDecisionExact,
  video: report.video,
  alignment: report.alignment,
  visualApproval: "pending",
  buildInstallPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate08: saved.stages[7].status,
  gate09: saved.stages[8].status,
  gate11: saved.stages[10].status,
  gate12: saved.stages[11].status,
  reviewArtifactId: saved.stages[7].reviewArtifactIds[0],
}, null, 2));
