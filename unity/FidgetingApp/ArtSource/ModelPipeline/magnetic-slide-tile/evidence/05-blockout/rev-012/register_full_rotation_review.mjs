#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const stage = manifest.stages.find((item) => item.id === "05-blockout");
if (manifest.revision !== 215 || stage?.revision !== 12 || stage.status !== "ready_for_review")
  throw new Error(`Expected pipeline 215 Gate 05 rev 12 ready_for_review; got ${manifest.revision}/${stage?.revision}/${stage?.status}.`);

const here = path.dirname(fileURLToPath(import.meta.url));
const validation = JSON.parse(fs.readFileSync(path.join(here, "unity-preview/full-rotation-video-validation.json"), "utf8"));
if (!validation.pass) throw new Error("Full-rotation video validation failed.");
const exactUserWording = "current motion principle accepted, evidence incomplete because preview did not demonstrate full 360°.";
const contractSha = stage.blockoutSpec.governingContractSha256;
const sourceAssetIds = [
  "magnetic-slide-g05-r012-fbx",
  "slider-analysis-mechanism-evidence-contract-r016",
  "magnetic-slide-tile-authorized-provisional-contract-r011",
  "magnetic-slide-tile-approved-four-track-architecture-r013",
];
const sourceClaimIds = manifest.claims
  .filter((claim) => claim.stageId === "02-analysis" && !["superseded", "stale"].includes(claim.state))
  .map((claim) => claim.id);
const definitions = [
  ["magnetic-slide-g05-r012-unity-full360-video", "unity-motion-recording", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/unity-preview/gate05-r012-unity-full-360-motion.mp4", "unity-render"],
  ["magnetic-slide-g05-r012-unity-full360-transform", "unity-transform-validation", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/unity-preview/unity-full-rotation-validation.json", "validation"],
  ["magnetic-slide-g05-r012-unity-full360-validation", "motion-video-validation", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/unity-preview/full-rotation-video-validation.json", "validation"],
  ["magnetic-slide-g05-r012-unity-full360-builder", "unity-builder", "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate05R012Geometry/Editor/MagneticSlideTileGate05R012FullRotationBuilder.cs", "process"],
  ["magnetic-slide-g05-r012-unity-full360-scene", "unity-scene", "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate05R012Geometry/MagneticSlideTileGate05R012FullRotationPreview.unity", "unity-render"],
  ["magnetic-slide-g05-r012-unity-full360-validator", "validation-script", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/validate_full_rotation_recording.py", "process"],
  ["magnetic-slide-g05-r012-unity-full360-quicktime-validator", "validation-script", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/validate_quicktime_playback.swift", "process"],
  ["magnetic-slide-g05-r012-unity-full360-register", "registration-script", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/register_full_rotation_review.mjs", "process"],
];
const ids = new Set(definitions.map(([id]) => id));
manifest.assets = manifest.assets.filter((asset) => !ids.has(asset.id));
for (const [id, slot, relative, role] of definitions) {
  const absolute = path.join(repoRoot, relative);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${relative}`);
  manifest.assets.push({
    id,
    stageId: "05-blockout",
    slot,
    path: relative,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: relative.endsWith(".cs") || relative.endsWith(".unity") || relative.endsWith(".mp4")
        ? "Unity 6000.5.6f1"
        : "fidgeting-model-pipeline",
      version: "Gate 05 rev 12 full-rotation supplement",
      recipe: "fixed camera, white clay, 50% and maximum-slide 0-360 rotations, 30 detents at 12 degrees",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractSha,
      sourceGeometrySha256: validation.sourceGeometry.sha256,
      sourceGeometryChanged: false,
      finalMaterialsApplied: false,
      shippingSceneModified: false,
      buildInstallPhone: false,
    },
    sourceAssetIds,
    sourceClaimIds,
  });
}

const prior = manifest.assets.find((asset) => asset.id === "magnetic-slide-g05-r012-unity-video");
if (!prior) throw new Error("Missing prior partial Unity recording.");
prior.provenance = {
  ...prior.provenance,
  evidenceStatus: "valid-partial-evidence-superseded-for-full-rotation-approval",
  supersededForFullRotationBy: "magnetic-slide-g05-r012-unity-full360-video",
};
stage.artifactIds.push(...definitions.map(([id]) => id).filter((id) => !stage.artifactIds.includes(id)));
stage.reviewArtifactIds = [
  "magnetic-slide-g05-r012-unity-full360-video",
  "magnetic-slide-g05-r012-product-glb",
  "magnetic-slide-g05-r012-axis-overlay",
  "magnetic-slide-g05-r012-open",
  "magnetic-slide-g05-r012-technical-separated",
  "magnetic-slide-g05-r012-technical-glb",
];
stage.blockoutSpec.fullRotationReview = {
  decisionState: "motion-principle-accepted-evidence-incomplete",
  exactUserWording,
  sourceGeometryChanged: false,
  videoAssetId: "magnetic-slide-g05-r012-unity-full360-video",
  priorVideoAssetId: "magnetic-slide-g05-r012-unity-video",
  priorVideoStatus: "valid-partial-evidence-superseded-for-full-rotation-approval",
  frameCount: validation.frameCount,
  fps: validation.video.frameRate,
  durationSeconds: validation.video.durationSeconds,
  dimensions: [validation.video.width, validation.video.height],
  partialSlideMeters: validation.unityTransformValidation.partialSlideMeters,
  maximumSlideMeters: validation.unityTransformValidation.maximumSlideMeters,
  visitedDetentIndices: validation.unityTransformValidation.visitedDetentIndices,
  finalOrientationClosureDegrees: validation.unityTransformValidation.finalOrientationClosureDegrees,
  visualApprovalPending: true,
};
stage.validations = stage.validations.filter((item) => ![
  "unity-full-rotation",
  "unity-thirty-detents",
  "unity-final-orientation-closure",
  "unity-full-rotation-playback",
].includes(item.id));
stage.validations.push(
  {
    id: "unity-full-rotation",
    status: "pass",
    evidence: "570/570 real Unity Camera frames; 0→360° at 50% and maximum legal slide; fixed-axis and bottom transform variance 0.",
  },
  {
    id: "unity-thirty-detents",
    status: "pass",
    evidence: "All 30 unique detent indices at exact 12° intervals are present in both complete revolutions.",
  },
  {
    id: "unity-final-orientation-closure",
    status: "pass",
    evidence: `Partial, maximum and final 360° orientation closure error ${validation.unityTransformValidation.finalOrientationClosureDegrees}°; model ROI max raster delta ${validation.closureModelRoiMaxPixelDelta}.`,
  },
  {
    id: "unity-full-rotation-playback",
    status: "pass",
    evidence: "H.264 High/yuv420p 1920×1080, 30 fps, 19.0 s; ffprobe and macOS AVFoundation decoded 570/570 frames.",
  },
);
stage.status = "ready_for_review";
stage.readiness = {
  ready: true,
  blockers: [],
  note: "Motion principle accepted. Review the new full 360° Unity white-model recording; Gate 05 visual approval remains pending and nothing was pushed to a phone.",
};
manifest.currentStageId = "05-blockout";
manifest.currentState.visualApproval = "gate05-rev12-full360-evidence-ready-visual-approval-pending-not-pushed";
manifest.currentState.blenderModelingStatus = "gate05-rev12-geometry-unchanged-full360-evidence-ready";
manifest.currentState.unityStatus = "isolated-clay-full360-preview-only-old-shipping-model-default";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-default-gate05-white-model-full360";
manifest.currentState.diagnosis = exactUserWording;
manifest.issues.push({
  id: crypto.randomUUID(),
  stageId: "05-blockout",
  assetId: "magnetic-slide-g05-r012-unity-full360-video",
  severity: "major",
  status: "resolved-by-full360-supplement",
  note: exactUserWording,
});
for (const relative of [
  "tools/model-provenance-explorer/app.js",
  "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md",
]) {
  const absolute = path.join(repoRoot, relative);
  for (const asset of manifest.assets.filter((item) => item.path === relative)) {
    asset.sha256 = sha256File(absolute);
    asset.sizeBytes = fs.statSync(absolute).size;
  }
}
for (let index = 5; index < manifest.stages.length; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 05 rev 12 remains under geometry and full-rotation review; downstream evidence cannot advance.";
}
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-full-rotation-evidence-ready",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  exactUserWording,
  decisionState: "motion-principle-accepted-evidence-incomplete",
  sourceGeometryChanged: false,
  videoAssetId: "magnetic-slide-g05-r012-unity-full360-video",
  priorVideoStatus: "valid-partial-evidence-superseded-for-full-rotation-approval",
  visualApprovalPending: true,
  buildInstallPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate05: saved.stages[4].status,
  video: validation.video,
  exactUserWording,
}, null, 2));
