#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 187) throw new Error(`Expected pipeline revision 187, got ${manifest.revision}.`);
const gate08 = manifest.stages.find((stage) => stage.id === "08-lighting");
const gate09 = manifest.stages.find((stage) => stage.id === "09-environment");
if (gate08.status !== "approved" || gate08.decision?.notes !== "进行下一步吧") {
  throw new Error("Gate 08 rev 2 exact chat approval is not current.");
}
if (gate09.status !== "draft" || gate09.environmentSpec?.revision !== 8) {
  throw new Error("Gate 09 rev 8 is not the active immutable draft.");
}
const output = path.dirname(fileURLToPath(import.meta.url));
const readJson = (filename) => JSON.parse(fs.readFileSync(path.join(output, filename), "utf8"));
const environment = readJson("environment-validation.json");
const image = readJson("image-environment-audit.json");
const blender = readJson("blender-environment-audit.json");
const portability = readJson("portability-validation.json");
const hdri = readJson("portable-hdri-metadata.json");
const extraction = readJson("portable-texture-extraction.json");
if (![environment, image, blender, portability, extraction].every((report) => report.pass)) {
  throw new Error("Gate 09 environment or portability validation failed.");
}
if (
  environment.sourceGate08.blendSha256 !== gate09.environmentSpec.sourceLightingSha256
  || environment.contractSha256 !== gate09.environmentSpec.governingContractSha256
  || environment.sourceGate08.approvalWording !== "进行下一步吧"
) {
  throw new Error("Gate 09 consumed a stale light, contract or approval.");
}

const local = (filename) => path.join(output, filename);
const definitions = [
  ["magnetic-slide-tile-environment-prepare-r008", "approval-transition", local("prepare_gate09.mjs"), "process"],
  ["magnetic-slide-tile-environment-builder-r008", "environment-builder", local("build_gate09_environment.py"), "process"],
  ["magnetic-slide-tile-environment-texture-extractor-r008", "texture-extractor", local("extract_portable_textures.py"), "process"],
  ["magnetic-slide-tile-environment-portability-builder-r008", "portability-builder", local("build_unity_portability_contract.py"), "process"],
  ["magnetic-slide-tile-environment-image-audit-script-r008", "image-audit-script", local("assemble_and_audit_gate09.py"), "process"],
  ["magnetic-slide-tile-environment-blender-audit-script-r008", "blender-audit-script", local("audit_gate09_blender.py"), "process"],
  ["magnetic-slide-tile-environment-register-r008", "registration-script", local("register_gate09_review.mjs"), "process"],
  ["magnetic-slide-tile-environment-validation-r008", "environment-validation", local("environment-validation.json"), "validation"],
  ["magnetic-slide-tile-environment-image-audit-r008", "image-environment-audit", local("image-environment-audit.json"), "validation"],
  ["magnetic-slide-tile-environment-blender-audit-r008", "blender-environment-audit", local("blender-environment-audit.json"), "validation"],
  ["magnetic-slide-tile-environment-hdri-metadata-r008", "environment-metadata", local("portable-hdri-metadata.json"), "validation"],
  ["magnetic-slide-tile-environment-texture-extraction-r008", "texture-extraction", local("portable-texture-extraction.json"), "validation"],
  ["magnetic-slide-tile-unity-portability-contract-r008", "unity-portability-contract", local("unity-portability-contract.json"), "contract"],
  ["magnetic-slide-tile-unity-portability-validation-r008", "unity-portability-validation", local("portability-validation.json"), "validation"],
  ["magnetic-slide-tile-environment-blend-r008", "blend", local("magnetic-slide-tile-environment-r008.blend"), "source-model"],
  ["magnetic-slide-tile-environment-lookdev-r008", "interactive-environment-lookdev", local("magnetic-slide-tile-environment-r008-lookdev.glb"), "export"],
  ["magnetic-slide-tile-environment-hdri-r008", "portable-equirectangular-hdri", local("magnetic-slide-tile-shipping-studio-r008.exr"), "analysis"],
  ["magnetic-slide-tile-environment-hdri-preview-r008", "portable-hdri-preview", local("magnetic-slide-tile-shipping-studio-r008-preview.png"), "analysis"],
  ["magnetic-slide-tile-environment-turntable-r008", "environment-comparison-turntable", local("magnetic-slide-tile-environment-comparison-r008.mp4"), "blender-render"],
  ["magnetic-slide-tile-environment-comparison-board-r008", "environment-comparison-board", local("environment-comparison-board.png"), "analysis"],
  ["magnetic-slide-tile-environment-shipping-views-r008", "shipping-environment-views", local("shipping-environment-views-board.png"), "analysis"],
  ["magnetic-slide-tile-environment-reflection-board-r008", "reflection-comparison-board", local("reflection-comparison-board.png"), "analysis"],
  ["magnetic-slide-tile-environment-mechanical-board-r008", "mechanical-readability-board", local("mechanical-readability-board.png"), "analysis"],
  ["magnetic-slide-tile-environment-portable-board-r008", "portable-environment-board", local("portable-environment-board.png"), "analysis"],
  ["magnetic-slide-tile-environment-neutral-closed-r008", "neutral-environment", local("neutral-closed-hero.png"), "blender-render"],
  ["magnetic-slide-tile-environment-shipping-closed-r008", "shipping-environment", local("shipping-closed-hero.png"), "blender-render"],
  ["magnetic-slide-tile-environment-neutral-open-r008", "neutral-environment", local("neutral-max-open.png"), "blender-render"],
  ["magnetic-slide-tile-environment-shipping-open-r008", "shipping-environment", local("shipping-max-open.png"), "blender-render"],
  ["magnetic-slide-tile-environment-shipping-detent12-r008", "shipping-detent", local("shipping-detent-12.png"), "blender-render"],
  ["magnetic-slide-tile-environment-shipping-detent36-r008", "shipping-detent", local("shipping-detent-36.png"), "blender-render"],
  ["magnetic-slide-tile-environment-neutral-reflection-r008", "neutral-reflection-closeup", local("neutral-reflection-closeup.png"), "blender-render"],
  ["magnetic-slide-tile-environment-shipping-reflection-r008", "shipping-reflection-closeup", local("shipping-reflection-closeup.png"), "blender-render"],
  ["magnetic-slide-tile-environment-shipping-flat-axis-r008", "shipping-mechanical", local("shipping-flat-plane-raised-axis.png"), "blender-render"],
  ["magnetic-slide-tile-environment-shipping-underside-r008", "shipping-mechanical", local("shipping-underside-grooves.png"), "blender-render"],
  ["magnetic-slide-tile-environment-shipping-carrier-r008", "shipping-mechanical", local("shipping-carrier-clearance.png"), "blender-render"],
  ["magnetic-slide-tile-environment-upper-albedo-r008", "portable-upper-albedo", local("portable-textures/upper-albedo.png"), "analysis"],
  ["magnetic-slide-tile-environment-upper-roughness-r008", "portable-upper-roughness", local("portable-textures/upper-roughness.png"), "analysis"],
  ["magnetic-slide-tile-environment-lower-albedo-r008", "portable-lower-albedo", local("portable-textures/lower-albedo.png"), "analysis"],
  ["magnetic-slide-tile-environment-lower-roughness-r008", "portable-lower-roughness", local("portable-textures/lower-roughness.png"), "analysis"],
  ["magnetic-slide-tile-environment-workbench-r008", "workbench-source", path.join(repoRoot, "tools/model-provenance-explorer/app.js"), "process"],
  ["magnetic-slide-tile-environment-node-test-r008", "node-test", path.join(repoRoot, "tools/model-provenance-explorer/tests/magnetic-slide-gate09-rev8.test.mjs"), "process"],
];
const sourceAssetIds = [
  "slider-analysis-mechanism-evidence-contract-r016",
  "magnetic-slide-tile-geometry-blend-r004",
  "magnetic-slide-tile-material-blend-r011",
  "magnetic-slide-tile-material-texture-lineage-r011",
  "magnetic-slide-tile-lighting-blend-r002",
  "magnetic-slide-tile-lighting-lookdev-r002",
  "magnetic-slide-tile-lighting-turntable-r002",
];
const portabilityContractSha256 = portability.contractSha256;
for (const [id, slot, absolute, role] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing Gate 09 output ${absolute}.`);
  manifest.assets.push({
    id,
    stageId: "09-environment",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: absolute.endsWith(".py") || absolute.endsWith(".mjs")
        ? "fidgeting-model-pipeline"
        : "Blender/Pillow/FFmpeg",
      version: absolute.endsWith(".py") || absolute.endsWith(".mjs") ? "2" : "Blender 5.2.0 LTS",
      recipe: "Gate 09 rev 8 matched neutral/portable shipping environment on approved Gate 08 lighting",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: environment.contractSha256,
      gate08SourceSha256: environment.sourceGate08.blendSha256,
      approvedGate08Wording: "进行下一步吧",
      finalGoal: "transfer to Unity with no avoidable loss and run on iPhone",
      geometryDigest: environment.geometry.after,
      materialDigest: environment.materials.approvedSemanticDigest,
      lightDigest: environment.lighting.after,
      cameraDigest: environment.cameras.after,
      environmentSha256: hdri.sha256,
      portabilityContractSha256,
      simulatorUsed: false,
      unityImportApplied: false,
      deviceWork: false,
    },
    sourceAssetIds,
    sourceClaimIds: [],
  });
}

gate09.status = "ready_for_review";
gate09.artifactIds = definitions.map(([id]) => id);
gate09.reviewArtifactIds = [
  "magnetic-slide-tile-environment-lookdev-r008",
  "magnetic-slide-tile-environment-turntable-r008",
  "magnetic-slide-tile-environment-comparison-board-r008",
  "magnetic-slide-tile-environment-reflection-board-r008",
  "magnetic-slide-tile-environment-shipping-views-r008",
  "magnetic-slide-tile-environment-mechanical-board-r008",
  "magnetic-slide-tile-environment-portable-board-r008",
  "magnetic-slide-tile-environment-shipping-closed-r008",
  "magnetic-slide-tile-environment-shipping-open-r008",
  "magnetic-slide-tile-environment-shipping-detent12-r008",
  "magnetic-slide-tile-environment-shipping-detent36-r008",
];
gate09.inputDigest = environment.sourceGate08.blendSha256;
gate09.outputDigest = sha256File(local("magnetic-slide-tile-environment-r008.blend"));
gate09.validations = [
  { id: "gate08-r002-exact-approval", status: "pass", evidence: `Gate 08 rev 2 approved with exact wording 进行下一步吧; source blend SHA-256 ${environment.sourceGate08.blendSha256}.` },
  { id: "geometry-material-light-camera-unchanged", status: "pass", evidence: `Geometry ${environment.geometry.after}, approved material ${environment.materials.approvedSemanticDigest}, light ${environment.lighting.after}, camera ${environment.cameras.after}; all unchanged across neutral/shipping.` },
  { id: "portable-linear-environment", status: "pass", evidence: `OpenEXR ${hdri.resolutionPx.join("×")} scene-linear Rec.709/D65, seam ${hdri.seamMaxAbsoluteLinearDelta}, ${hdri.dynamicRangeStopsP01ToP99.toFixed(3)} stops, SHA-256 ${hdri.sha256}.` },
  { id: "matched-neutral-shipping-pairs", status: "pass", evidence: "Closed, maximum-open and reflection closeups share camera, pose, lights and exposure. Only world/reflection/background/ground change." },
  { id: "target-motion-views", status: "pass", evidence: "Target environment includes closed, maximum-open, 12° and 36° views plus flat plane/raised axis, four grooves and carrier/follower clearance." },
  { id: "color-reflection-clipping", status: "pass", evidence: `Blood-red median hue ${image.aggregate.targetRedMedianHueRange.join("…")}°, crystal variation ≥${image.aggregate.minimumCrystalVariation.toFixed(3)}, clipping ≤${image.aggregate.maximumClippedFraction}.` },
  { id: "motion-containment", status: "pass", evidence: `${environment.motionContainment.denseSweepSamples} samples at ${environment.motionContainment.angularStepDegrees}° preserve minimum-overlap containment; no animation or self-motion.` },
  { id: "unity-portability-contract", status: "pass", evidence: `Hash-locked portability contract SHA-256 ${portabilityContractSha256} records geometry/hierarchy/pivot/UV/masks, PBR packing, URP material targets, probe, tone-map plan and explicit tolerances.` },
  { id: "truthful-lossless-boundary", status: "pass", evidence: "Geometry/hierarchy/pivot/UV/masks require exact deterministic preservation. Procedural material, lighting and color management require measured parity because Blender nodes and AgX cannot transfer byte-identically to URP." },
  { id: "interactive-and-recording", status: "pass", evidence: "Interactive GLB supports orbit/zoom and Neutral/Shipping environment response; 24-frame matched real Blender comparison turntable MP4 is present." },
  { id: "scope", status: "pass", evidence: "No Simulator, Unity import settings, build, install or device work occurred; old shipping model remains default and iPhone acceptance follows Gate 12 approval." },
];
gate09.environmentSpec = {
  ...gate09.environmentSpec,
  authoritativeBlendSha256: gate09.outputDigest,
  interactiveGlbSha256: sha256File(local("magnetic-slide-tile-environment-r008-lookdev.glb")),
  comparisonTurntableSha256: sha256File(local("magnetic-slide-tile-environment-comparison-r008.mp4")),
  environmentAsset: {
    path: "magnetic-slide-tile-shipping-studio-r008.exr",
    sha256: hdri.sha256,
    resolutionPx: hdri.resolutionPx,
    projection: hdri.projection,
    colorPrimaries: hdri.colorPrimaries,
    transfer: hdri.transfer,
    whitePoint: hdri.whitePoint,
    seamMaxAbsoluteLinearDelta: hdri.seamMaxAbsoluteLinearDelta,
    dynamicRangeStopsP01ToP99: hdri.dynamicRangeStopsP01ToP99,
    worldStrength: 0.65,
    rotationDegrees: 0,
  },
  portabilityContractSha256,
  geometryDigestAfter: environment.geometry.after,
  uvDigestAfter: environment.uv.after,
  materialDigestAfter: environment.materials.approvedSemanticDigest,
  lightDigestAfter: environment.lighting.after,
  cameraDigestAfter: environment.cameras.after,
  imageMetrics: image.aggregate,
  blenderAudit: blender.checks,
};
gate09.readiness = {
  ready: true,
  blockers: [],
  note: "Review the interactive Neutral/Shipping GLB first, then the matched real-render turntable, reflection pair, motion views, mechanical board and portable EXR board. Visual approval is pending; nothing was pushed to a phone.",
};
delete gate09.staleReason;
for (let index = 9; index < 11; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 09 rev 8 awaits environment approval.";
}
manifest.stages[11].status = "rejected";
manifest.currentStageId = "09-environment";
manifest.currentState.visualApproval = "gate09-rev8-ready-for-review-visual-approval-pending-not-pushed";
manifest.currentState.blenderModelingStatus = "gate09-portable-environment-ready-for-review";
manifest.currentState.simulatorStatus = "internal-superseded-not-current";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default-portability-contract-only";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-default-gate09-environment";
manifest.currentState.diagnosis = "Gate 08 rev 2 is approved. Gate 09 rev 8 changes only portable world/reflection/background/ground inputs and records measured Unity parity requirements.";
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate09-portable-environment-ready",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate08ApprovalWording: "进行下一步吧",
  finalGoal: "transfer to Unity with no avoidable loss and run on iPhone",
  gate08SourceSha256: environment.sourceGate08.blendSha256,
  contractSha256: environment.contractSha256,
  geometryDigest: environment.geometry.after,
  materialDigest: environment.materials.approvedSemanticDigest,
  lightDigest: environment.lighting.after,
  cameraDigest: environment.cameras.after,
  environmentSha256: hdri.sha256,
  portabilityContractSha256,
  artifactIds: gate09.artifactIds,
  reviewArtifactIds: gate09.reviewArtifactIds,
  environmentModes: ["neutral", "shipping"],
  visualApprovalPending: true,
  simulatorUsed: false,
  unityImportApplied: false,
  buildInstallOrDevice: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate08: saved.stages[7].status,
  gate09: saved.stages[8].status,
  artifactCount: gate09.artifactIds.length,
  reviewArtifactCount: gate09.reviewArtifactIds.length,
  environmentSha256: hdri.sha256,
  portabilityContractSha256,
}, null, 2));

