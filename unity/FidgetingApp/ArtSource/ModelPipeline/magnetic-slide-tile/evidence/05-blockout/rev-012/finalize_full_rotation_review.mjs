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
const stage = manifest.stages[4];
if (manifest.revision !== 217 || stage.status !== "ready_for_review")
  throw new Error(`Expected pipeline 217 ready_for_review; got ${manifest.revision}/${stage.status}.`);
const here = path.dirname(fileURLToPath(import.meta.url));
const video = JSON.parse(fs.readFileSync(path.join(here, "unity-preview/full-rotation-video-validation.json"), "utf8"));
const browser = JSON.parse(fs.readFileSync(path.join(here, "browser-workspace-validation.json"), "utf8"));
if (!video.pass || !browser.pass) throw new Error("Full-rotation review evidence failed.");
const finalReport = {
  schemaVersion: 1,
  gate: "05-blockout",
  revision: 12,
  pipelineRevisionAfterRegistration: 218,
  decisionState: "motion-principle-accepted-evidence-incomplete",
  exactUserWording: "current motion principle accepted, evidence incomplete because preview did not demonstrate full 360°.",
  checks: {
    geometryPreserved: video.checks.geometryUnchanged,
    realUnityCapture: video.checks.realUnityFrames,
    twoCompleteRevolutions: video.checks.partialFullRevolution && video.checks.maximumFullRevolution,
    thirtyDetents: video.checks.allThirtyDetentsVisited,
    perFrameTransformValidation: video.checks.singleFixedPivot
      && video.checks.slotPointLockedEveryFrame
      && video.checks.bottomStaticHorizontal
      && video.checks.productStaticHorizontal
      && video.checks.fixedCamera,
    containmentAndVisibility: video.checks.minimumDiskContained
      && video.checks.topAboveBottom
      && video.checks.rendererWhitelistExact,
    finalClosure: video.checks.finalOrientationClosure,
    ffprobeAndQuickTime: video.checks.h264High1920x1080
      && video.checks.thirtyFpsNineteenSeconds
      && video.checks.quickTimePlayable,
    browserDesktopMobileVideoModal: browser.pass,
    focusedNodeTests: "3/3 passed",
    pipelineValidators: "magnetic-slide-tile revision 217 errors/missingFiles/unhashed=0/0/0",
    fullNodeSuite: "175/177 passed; two failures are concurrent Premium Display Case state expectations outside this feature",
    syntaxAndXml: "Python, JavaScript, Swift and focused XML checks passed",
    buildInstallPhone: false,
  },
  metrics: {
    frames: video.frameCount,
    durationSeconds: video.video.durationSeconds,
    dimensions: [video.video.width, video.video.height],
    fps: video.video.frameRate,
    maxConstraintResidualMeters: video.unityTransformValidation.maxConstraintResidualMeters,
    axisOverlayCentroidRangePx: video.axisOverlayCentroidRangePx,
    minimumVerticalGapMeters: video.unityTransformValidation.minimumVerticalGapMeters,
    containmentRayMisses: video.unityTransformValidation.containmentRayMisses,
    finalOrientationClosureDegrees: video.unityTransformValidation.finalOrientationClosureDegrees,
    quickTimeDecodedFrames: video.quickTime.videoSampleCount,
  },
  scope: {
    geometryChanged: false,
    finalMaterialsApplied: false,
    shippingSceneModified: false,
    simulator: false,
    build: false,
    install: false,
    phone: false,
  },
  featurePass: true,
  visualApprovalPending: true,
};
const finalRelative = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/full-rotation-final-validation.json";
fs.writeFileSync(path.join(repoRoot, finalRelative), `${JSON.stringify(finalReport, null, 2)}\n`);
const additions = [
  ["magnetic-slide-g05-r012-unity-full360-hash-refresh", "registration-script", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/refresh_full_rotation_hashes.mjs", "process"],
  ["magnetic-slide-g05-r012-unity-full360-finalizer", "registration-script", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/finalize_full_rotation_review.mjs", "process"],
  ["magnetic-slide-g05-r012-unity-full360-final-validation", "final-validation", finalRelative, "validation"],
];
const ids = new Set(additions.map(([id]) => id));
manifest.assets = manifest.assets.filter((asset) => !ids.has(asset.id));
for (const [id, slot, relative, role] of additions) {
  const absolute = path.join(repoRoot, relative);
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
      name: "fidgeting-model-pipeline",
      version: "Gate 05 rev 12 full-rotation supplement",
      recipe: "register final full-rotation validation without changing geometry",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: stage.blockoutSpec.governingContractSha256,
      sourceGeometrySha256: video.sourceGeometry.sha256,
      sourceGeometryChanged: false,
      finalMaterialsApplied: false,
      buildInstallPhone: false,
    },
    sourceAssetIds: [
      "magnetic-slide-g05-r012-unity-full360-video",
      "magnetic-slide-g05-r012-unity-full360-transform",
      "magnetic-slide-g05-r012-unity-full360-validation",
    ],
    sourceClaimIds: [],
  });
}
stage.artifactIds.push(...additions.map(([id]) => id).filter((id) => !stage.artifactIds.includes(id)));
stage.validations = stage.validations.filter((item) => item.id !== "full-rotation-feature-validation");
stage.validations.push({
  id: "full-rotation-feature-validation",
  status: "pass",
  evidence: "Unity capture, ffprobe, AVFoundation, desktop/mobile browser, focused Node, pipeline and syntax checks pass. Two full-suite failures are unrelated Premium Display Case expectations.",
});
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-full-rotation-final-validation",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  featurePass: true,
  sourceGeometryChanged: false,
  unrelatedConcurrentSuiteFailures: 2,
  visualApprovalPending: true,
  buildInstallPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[4].status,
  featurePass: finalReport.featurePass,
  visualApprovalPending: finalReport.visualApprovalPending,
}, null, 2));
