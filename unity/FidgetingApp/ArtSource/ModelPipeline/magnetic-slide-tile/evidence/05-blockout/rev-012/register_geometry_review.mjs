#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, repoRoot, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const stage = manifest.stages.find(item => item.id === "05-blockout");
if (manifest.revision !== 212 || stage.revision !== 12 || stage.status !== "draft")
  throw new Error(`Expected pipeline 212 Gate 05 rev 12 draft; got ${manifest.revision}/${stage.revision}/${stage.status}.`);
const here = path.dirname(fileURLToPath(import.meta.url));
const geometry = JSON.parse(fs.readFileSync(path.join(here, "geometry-validation.json"), "utf8"));
const motion = JSON.parse(fs.readFileSync(path.join(here, "unity-preview/motion-video-validation.json"), "utf8"));
const rejection = JSON.parse(fs.readFileSync(path.join(here, "user-rejection-evidence.json"), "utf8"));
if (!geometry.pass || !motion.pass) throw new Error("Corrected geometry evidence failed.");
const sourceAssetIds = [
  "slider-analysis-mechanism-evidence-contract-r016",
  "magnetic-slide-tile-authorized-provisional-contract-r011",
  "magnetic-slide-tile-approved-four-track-architecture-r013",
  "magnetic-slide-tile-geometry-blend-r004",
];
const definitions = [
  ["magnetic-slide-g05-r012-rejection-axis", "user-rejection", "user-rejection-axis-intent.jpg", "user-input"],
  ["magnetic-slide-g05-r012-rejection-penetration", "user-rejection", "user-rejection-penetration-proxy.png", "user-input"],
  ["magnetic-slide-g05-r012-rejection-report", "decision-evidence", "user-rejection-evidence.json", "validation"],
  ["magnetic-slide-g05-r012-builder", "builder", "build_corrected_geometry.py", "process"],
  ["magnetic-slide-g05-r012-archive-script", "archive-script", "archive_rejection.py", "process"],
  ["magnetic-slide-g05-r012-prepare-script", "registration-script", "prepare_geometry_correction.mjs", "process"],
  ["magnetic-slide-g05-r012-register-script", "registration-script", "register_geometry_review.mjs", "process"],
  ["magnetic-slide-g05-r012-validation", "silhouette-validator", "geometry-validation.json", "validation"],
  ["magnetic-slide-g05-r012-blend", "blend", "magnetic-slide-tile-fixed-axis-r012.blend", "source-model"],
  ["magnetic-slide-g05-r012-product-glb", "interactive-model", "magnetic-slide-tile-fixed-axis-product-r012.glb", "export"],
  ["magnetic-slide-g05-r012-technical-glb", "technical-interactive-model", "magnetic-slide-tile-fixed-axis-technical-r012.glb", "export"],
  ["magnetic-slide-g05-r012-fbx", "unity-source-fbx", "magnetic-slide-tile-fixed-axis-r012.fbx", "export"],
  ["magnetic-slide-g05-r012-hero", "blockout-hero", "white-hero.png", "blender-render"],
  ["magnetic-slide-g05-r012-closed", "blockout-closed", "state-closed.png", "blender-render"],
  ["magnetic-slide-g05-r012-open", "blockout-slide", "state-max-open.png", "blender-render"],
  ["magnetic-slide-g05-r012-12deg", "blockout-spin", "state-detent-12.png", "blender-render"],
  ["magnetic-slide-g05-r012-36deg", "blockout-compound", "state-detent-36.png", "blender-render"],
  ["magnetic-slide-g05-r012-combined", "combined-pose", "state-combined.png", "blender-render"],
  ["magnetic-slide-g05-r012-axis-overlay", "pivot-overlay", "fixed-world-axis-overlay.png", "blender-render"],
  ["magnetic-slide-g05-r012-technical-exploded", "blockout-exploded", "technical-internals-exploded.png", "blender-render"],
  ["magnetic-slide-g05-r012-technical-separated", "technical-view", "technical-internals-separated.png", "blender-render"],
  ["magnetic-slide-g05-r012-unity-video", "unity-motion-recording", "unity-preview/gate05-r012-unity-fixed-axis-motion.mp4", "unity-render"],
  ["magnetic-slide-g05-r012-unity-motion-report", "unity-transform-validation", "unity-preview/unity-motion-validation.json", "validation"],
  ["magnetic-slide-g05-r012-video-validation", "motion-video-validation", "unity-preview/motion-video-validation.json", "validation"],
  ["magnetic-slide-g05-r012-unity-log", "unity-log", "unity-preview/unity-capture.log", "validation"],
  ["magnetic-slide-g05-r012-video-validator", "validation-script", "validate_unity_recording.py", "process"],
];
const unityDefinitions = [
  ["magnetic-slide-g05-r012-unity-builder", "unity-builder", "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate05R012Geometry/Editor/MagneticSlideTileGate05R012PreviewBuilder.cs", "process"],
  ["magnetic-slide-g05-r012-unity-import", "unity-import", "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate05R012Geometry/Imported/magnetic-slide-tile-fixed-axis-r012.fbx", "source-model"],
  ["magnetic-slide-g05-r012-unity-scene", "unity-scene", "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate05R012Geometry/MagneticSlideTileGate05R012Preview.unity", "unity-render"],
];
const sourceClaimIds = manifest.claims.filter(claim => claim.stageId === "02-analysis" && !["superseded", "stale"].includes(claim.state)).map(claim => claim.id);
const records = [];
for (const [id, slot, filename, role] of definitions) {
  const absolute = path.join(here, filename);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${filename}`);
  records.push({ id, stageId: "05-blockout", slot, path: path.relative(repoRoot, absolute).split(path.sep).join("/"), sha256: sha256File(absolute), exists: true, sizeBytes: fs.statSync(absolute).size, role,
    producer: { name: filename.endsWith(".py") || filename.endsWith(".mjs") ? "fidgeting-model-pipeline" : filename.endsWith(".mp4") || filename.includes("unity-") ? "Unity 6000.5.6f1" : "Blender", version: "Gate 05 rev 12", recipe: "fixed world pivot, slot-point locking and render-layer correction" },
    provenance: { origin: slot === "user-rejection" ? "user-provided" : "repository-generated", contentClass: slot, assertedBy: slot === "user-rejection" ? "user" : "assistant", mechanismEvidenceContractSha256: geometry.contractSha256, sourceGeometrySha256: geometry.source.sha256, finalMaterialsApplied: false, buildInstallPhone: false },
    sourceAssetIds, sourceClaimIds });
}
for (const [id, slot, relative, role] of unityDefinitions) {
  const absolute = path.join(repoRoot, relative);
  records.push({ id, stageId: "05-blockout", slot, path: relative, sha256: sha256File(absolute), exists: true, sizeBytes: fs.statSync(absolute).size, role,
    producer: { name: "Unity", version: "6000.5.6f1", recipe: "isolated clay geometry preview; no build" },
    provenance: { origin: "repository-generated", contentClass: slot, assertedBy: "assistant", mechanismEvidenceContractSha256: geometry.contractSha256, shippingSceneModified: false, finalMaterialsApplied: false, buildInstallPhone: false },
    sourceAssetIds: ["magnetic-slide-g05-r012-fbx"], sourceClaimIds });
}
const ids = new Set(records.map(record => record.id));
manifest.assets = manifest.assets.filter(asset => !ids.has(asset.id));
manifest.assets.push(...records);
stage.artifactIds = records.map(record => record.id);
stage.reviewArtifactIds = [
  "magnetic-slide-g05-r012-product-glb",
  "magnetic-slide-g05-r012-unity-video",
  "magnetic-slide-g05-r012-axis-overlay",
  "magnetic-slide-g05-r012-open",
  "magnetic-slide-g05-r012-technical-separated",
  "magnetic-slide-g05-r012-technical-glb",
];
stage.status = "ready_for_review";
stage.validations = [
  { id: "fixed-pivot", status: "pass", evidence: `${geometry.denseValidation.samples} Blender samples: P variance ${geometry.denseValidation.maxPivotVarianceMm} mm.` },
  { id: "slot-point-lock", status: "pass", evidence: `Maximum Blender M_top*q(s)-P residual ${geometry.denseValidation.maxResidualMm} mm; Unity ${motion.unityTransformValidation.constraintResidualMeters} m.` },
  { id: "single-pivot", status: "pass", evidence: "Exactly one pivot_id exists: FixedAxis." },
  { id: "actual-mesh-intersections", status: "pass", evidence: "Five legal poses use Blender BVH triangle overlap checks; every internal-to-exterior surface pair is zero." },
  { id: "dense-hidden-envelope", status: "pass", evidence: "All internal mesh vertices remain inside the eroded capsule and below the exterior top across 361 carrier angles." },
  { id: "minimum-disk-coverage", status: "pass", evidence: "64 actual-mesh ray samples at five legal poses cover the non-rendering 15.0 mm disk with zero misses." },
  { id: "flat-bottom", status: "pass", evidence: `BottomExterior top-plane deviation ${geometry.bottomTopPlaneDeviationMm} mm.` },
  { id: "product-renderer-whitelist", status: "pass", evidence: "Blender and Unity product views enable only BottomExterior and MovingTopBody." },
  { id: "unity-motion-video", status: "pass", evidence: "300/300 frames; fixed-axis overlay centroid range 0×0 px; pitch/roll 0°." },
  { id: "scope", status: "pass", evidence: "No final materials, shipping scene, build, install or phone operation." },
];
stage.blockoutSpec.correctedTransform = "M_top(s,theta)=T(P)*Rz(theta)*T(-q(s)); q(s)=(0,-9+s,-3.1875) mm; P=(0,-9,5.875) mm.";
stage.blockoutSpec.geometryDigest = geometry.geometryDigest;
stage.blockoutSpec.denseValidation = geometry.denseValidation;
stage.blockoutSpec.productRendererWhitelist = geometry.renderLayers.productWhitelist;
stage.readiness = { ready: true, blockers: [], note: "Review the interactive product GLB and real Unity fixed-axis recording. Visual approval is pending; nothing was pushed to a phone." };
delete stage.staleReason;
manifest.issues.push(
  { id: crypto.randomUUID(), stageId: "05-blockout", assetId: "magnetic-slide-g05-r012-rejection-axis", severity: "blocker", status: "resolved-in-r012", note: "Axis identity and slot-point locking corrected with one FixedAxis pivot." },
  { id: crypto.randomUUID(), stageId: "05-blockout", assetId: "magnetic-slide-g05-r012-rejection-penetration", severity: "blocker", status: "resolved-in-r012", note: "Internal renderers removed from product whitelist and validated against exterior surfaces." },
);
for (let index = 5; index < manifest.stages.length; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 05 rev 12 corrected pivot ownership, kinematics and render visibility; downstream evidence must be rebuilt after approval.";
}
manifest.currentStageId = "05-blockout";
manifest.currentState.visualApproval = "gate05-rev12-ready-for-review-visual-approval-pending-not-pushed";
manifest.currentState.blenderModelingStatus = "gate05-rev12-fixed-axis-geometry-ready-for-review";
manifest.currentState.unityStatus = "isolated-clay-preview-only-old-shipping-model-default";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-default-gate05-white-model";
manifest.currentState.diagnosis = "Gate 05 rev 12 replaces ambiguous pivot ownership with one fixed world axis, exact slot-point locking and strict exterior/technical render whitelists.";
const appPath = path.join(repoRoot, "tools/model-provenance-explorer/app.js");
for (const asset of manifest.assets.filter(item => item.path === "tools/model-provenance-explorer/app.js")) {
  asset.sha256 = sha256File(appPath);
  asset.sizeBytes = fs.statSync(appPath).size;
}
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(), type: "gate05-fixed-axis-geometry-ready", modelId: "magnetic-slide-tile", manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt, rejection, rootCause: stage.blockoutSpec.rootCause, correction: stage.blockoutSpec.correctedTransform,
  artifactIds: stage.artifactIds, reviewArtifactIds: stage.reviewArtifactIds, denseSamples: geometry.denseValidation.samples,
  unityFrames: motion.frameCount, visualApprovalPending: true, buildInstallPhone: false,
});
console.log(JSON.stringify({ revision: saved.revision, gate05: saved.stages[4].status, artifacts: stage.artifactIds.length }, null, 2));

