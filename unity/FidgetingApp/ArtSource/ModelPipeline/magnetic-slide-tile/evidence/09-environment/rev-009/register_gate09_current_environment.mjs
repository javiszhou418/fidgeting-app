#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  digestValues,
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const manifest = loadManifest(modelId);
const gate08 = manifest.stages.find((stage) => stage.id === "08-lighting");
const stage = manifest.stages.find((item) => item.id === "09-environment");
if (manifest.revision !== 241
  || gate08?.status !== "approved"
  || gate08?.decision?.notes !== "你开始吧"
  || stage?.status !== "draft"
  || stage?.environmentSpec?.revision !== 9) {
  throw new Error("Expected approved Gate 08 rev 6 and draft Gate 09 rev 9 at revision 241.");
}
const output = path.dirname(fileURLToPath(import.meta.url));
const readJson = (filename) => JSON.parse(fs.readFileSync(path.join(output, filename), "utf8"));
const build = readJson("environment-build-validation.json");
const blender = readJson("blender-environment-audit.json");
const images = readJson("image-environment-audit.json");
const motion = readJson("environment-turntable-validation.json");
const portability = readJson("portability-validation.json");
if (![build, blender, images, motion, portability].every((report) => report.pass)) {
  throw new Error("Gate 09 rev 9 evidence is not fully validated.");
}
if (
  build.source.sha256 !== stage.environmentSpec.sourceLightingSha256
  || build.source.materialSha256 !== stage.environmentSpec.sourceMaterialSha256
  || build.source.geometryDigest !== stage.environmentSpec.sourceGeometryDigest
  || build.source.mechanismContractSha256 !== stage.environmentSpec.governingContractSha256
  || build.source.approvalExactWording !== "你开始吧"
) {
  throw new Error("Gate 09 consumed stale inputs.");
}

const local = (filename) => path.join(output, filename);
const definitions = [
  ["starter", "approval-transition", local("start_gate09_current_environment.mjs"), "process"],
  ["builder", "environment-builder", local("build_gate09_current_environment.py"), "process"],
  ["turntable-builder", "comparison-recording-builder", local("render_environment_comparison_turntable.py"), "process"],
  ["auditor", "environment-glb-auditor", local("audit_gate09_current_environment.py"), "process"],
  ["board-builder", "review-board-builder", local("build_environment_review_boards.py"), "process"],
  ["portability-builder", "unity-portability-builder", local("build_unity_portability_contract.py"), "process"],
  ["registrar", "registration-source", local("register_gate09_current_environment.mjs"), "process"],
  ["build-validation", "environment-build-validation", local("environment-build-validation.json"), "validation"],
  ["turntable-validation", "environment-turntable-validation", local("environment-turntable-validation.json"), "validation"],
  ["blender-audit", "blender-environment-audit", local("blender-environment-audit.json"), "validation"],
  ["image-audit", "image-environment-audit", local("image-environment-audit.json"), "validation"],
  ["portability-validation", "unity-portability-validation", local("portability-validation.json"), "validation"],
  ["portability-contract", "unity-portability-contract", local("unity-portability-contract-r009.json"), "contract"],
  ["blend", "source-blend", local("magnetic-slide-tile-environment-r009.blend"), "source-model"],
  ["lookdev", "interactive-environment-lookdev", local("magnetic-slide-tile-environment-r009-lookdev.glb"), "source-model"],
  ["neutral-hdr", "neutral-control-hdr", local("neutral-control-r009.exr"), "source-model"],
  ["target-hdr", "target-shipping-hdr", local("target-shipping-studio-r009.exr"), "source-model"],
  ["target-hdr-preview", "target-hdr-preview", local("target-shipping-studio-r009-preview.png"), "analysis"],
  ["cubemap-contract", "cubemap-orientation-contract", local("cubemap-r009/cubemap-contract.json"), "contract"],
  ["cubemap-positive-x", "cubemap-positive-x", local("cubemap-r009/positive-x.exr"), "source-model"],
  ["cubemap-negative-x", "cubemap-negative-x", local("cubemap-r009/negative-x.exr"), "source-model"],
  ["cubemap-positive-y", "cubemap-positive-y", local("cubemap-r009/positive-y.exr"), "source-model"],
  ["cubemap-negative-y", "cubemap-negative-y", local("cubemap-r009/negative-y.exr"), "source-model"],
  ["cubemap-positive-z", "cubemap-positive-z", local("cubemap-r009/positive-z.exr"), "source-model"],
  ["cubemap-negative-z", "cubemap-negative-z", local("cubemap-r009/negative-z.exr"), "source-model"],
  ["turntable", "environment-comparison-turntable", local("gate09-r009-neutral-target-turntable.mp4"), "blender-render"],
  ["turntable-poster", "environment-turntable-poster", local("environment-turntable-poster.png"), "analysis"],
  ["comparison-board", "environment-comparison-board", local("environment-comparison-board.png"), "analysis"],
  ["motion-board", "environment-motion-board", local("environment-motion-board.png"), "analysis"],
  ["reflection-board", "environment-reflection-board", local("environment-reflection-board.png"), "analysis"],
  ["portability-board", "environment-portability-board", local("environment-portability-board.png"), "analysis"],
  ["neutral-closed", "neutral-closed", local("neutral-closed.png"), "blender-render"],
  ["target-closed", "target-closed", local("target-closed.png"), "blender-render"],
  ["neutral-max0", "neutral-max-open-0", local("neutral-max0.png"), "blender-render"],
  ["target-max0", "target-max-open-0", local("target-max0.png"), "blender-render"],
  ["neutral-side", "neutral-side-reflection", local("neutral-side-reflection.png"), "blender-render"],
  ["target-side", "target-side-reflection", local("target-side-reflection.png"), "blender-render"],
  ["target-max12", "target-max-open-12", local("target-max12.png"), "blender-render"],
  ["target-max36", "target-max-open-36", local("target-max36.png"), "blender-render"],
  ["target-max360", "target-max-open-360", local("target-max360.png"), "blender-render"],
  ["target-rim", "target-rim-reflection", local("target-rim-reflection.png"), "blender-render"],
  ["target-dark-side", "target-dark-side-zero-artwork", local("target-dark-side-closeup.png"), "blender-render"],
];
const sourceAssetIds = [
  "slider-analysis-mechanism-evidence-contract-r017",
  "magnetic-slide-tile-geometry-blend-r005",
  "magnetic-slide-tile-material-blend-r013",
  "magnetic-slide-tile-material-lookdev-r013",
  "magnetic-slide-tile-lighting-blend-r006",
  "magnetic-slide-tile-lighting-lookdev-r006",
  "magnetic-slide-tile-lighting-environment-r006",
];
const records = definitions.map(([suffix, slot, absolute, role]) => {
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${absolute}`);
  return {
    id: `${modelId}-environment-${suffix}-r009`,
    stageId: "09-environment",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Gate 09 current environment workflow",
      version: "Blender 5.2.0 LTS / Python 3 / Node.js / FFmpeg",
      recipe: local("build_gate09_current_environment.py"),
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate09Revision: 9,
      sourceGate08Revision: 6,
      approvedGate08Wording: "你开始吧",
      sourceLightingSha256: build.source.sha256,
      sourceMaterialSha256: build.source.materialSha256,
      geometryDigest: build.source.geometryDigest,
      mechanismEvidenceContractSha256: build.source.mechanismContractSha256,
      neutralEnvironmentSha256: build.neutral.sha256,
      targetEnvironmentSha256: build.target.sha256,
      portabilityContractSha256: portability.contractSha256,
      note: "Fresh Gate 09 environment evidence. Old Gate 09 rev 8 assets remain stale history.",
      simulatorUsed: false,
      unityUsed: false,
      shippingChanged: false,
      deviceWork: false,
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);

stage.status = "ready_for_review";
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  `${modelId}-environment-lookdev-r009`,
  `${modelId}-environment-turntable-r009`,
  `${modelId}-environment-comparison-board-r009`,
  `${modelId}-environment-motion-board-r009`,
  `${modelId}-environment-reflection-board-r009`,
  `${modelId}-environment-portability-board-r009`,
  `${modelId}-environment-target-closed-r009`,
  `${modelId}-environment-target-max12-r009`,
  `${modelId}-environment-target-max36-r009`,
];
stage.inputDigest = digestValues([
  build.source.sha256,
  build.source.materialSha256,
  build.source.geometryDigest,
  build.source.mechanismContractSha256,
  build.neutral.sha256,
]);
stage.outputDigest = digestValues([
  build.output.blendSha256,
  build.target.sha256,
  portability.contractSha256,
  motion.videoSha256,
]);
stage.validations = [
  {
    id: "gate08-rev6-exact-approval",
    status: "pass",
    evidence: `Exact wording “你开始吧”; source lighting ${build.source.sha256}.`,
  },
  {
    id: "current-input-hashes",
    status: "pass",
    evidence: `Geometry ${build.source.geometryDigest}; material ${build.source.materialSha256}; mechanism ${build.source.mechanismContractSha256}.`,
  },
  {
    id: "environment-only-matched-pairs",
    status: "pass",
    evidence: "Closed, max-open 0°, and side-reflection pairs have identical camera, pose, material, light, display, and exposure state. Only the environment texture changes.",
  },
  {
    id: "portable-hdr-and-cubemap",
    status: "pass",
    evidence: `Target ${build.target.resolution.join("×")} scene-linear EXR has RGB nonzero ${build.target.nonzeroRgbFraction}, seam ${build.target.seamMaximumLinearDelta}, range ${build.target.dynamicRangeStopsP01P99.toFixed(3)} stops; six 512² EXR cubemap faces have ${build.cubemap.brightestDirectionAngularErrorDegrees.toFixed(3)}° orientation error.`,
  },
  {
    id: "corrected-material-partitions",
    status: "pass",
    evidence: "Blend and GLB preserve exact cap/side/rim/underside zones; side and underside artwork triangles are 0; cap artwork and bright silver rim remain present.",
  },
  {
    id: "target-color-reflection-clipping",
    status: "pass",
    evidence: `Blood-red, dark side, and silver-rim image checks pass. Standard clipping ≤0.1%; reflection closeups ≤0.2%.`,
  },
  {
    id: "endpoint-interlock-comparison",
    status: "pass",
    evidence: `${motion.sourceFrameCountPerEnvironment} real frames per environment: slide at 0°, full 360° only at sMax, aligned return; fixed-axis variance ${motion.maximumFixedAxisVarianceMm} mm and pitch/roll ${motion.maximumPitchRollRadians} rad.`,
  },
  {
    id: "unity-portability-contract",
    status: "pass",
    evidence: `Contract ${portability.contractSha256} locks current hashes, four material zones, shared HDR, cubemap mapping, display mapping, motion, tolerances, and downstream import requirements.`,
  },
  {
    id: "scope-gate",
    status: "pass",
    evidence: "No Simulator, Gate 10 export, Unity import, final Unity, shipping scene, build, install, or phone work occurred.",
  },
];
stage.environmentSpec = {
  ...stage.environmentSpec,
  revision: 9,
  evidenceRevision: 9,
  sourceLightingRevision: 6,
  sourceLightingSha256: build.source.sha256,
  sourceMaterialRevision: 13,
  sourceMaterialSha256: build.source.materialSha256,
  sourceGeometryDigest: build.source.geometryDigest,
  governingContractSha256: build.source.mechanismContractSha256,
  sourceLightingApprovalWording: "你开始吧",
  authoritativeBlendSha256: build.output.blendSha256,
  interactiveGlbSha256: build.output.glbSha256,
  comparisonTurntableSha256: motion.videoSha256,
  neutralEnvironment: build.neutral,
  targetEnvironment: build.target,
  unityCubemap: build.cubemap,
  materialPartitions: build.materialPartitions.objects,
  matchedPairs: build.pairs,
  imageMetrics: images.metrics,
  motionValidation: {
    frameCountPerEnvironment: motion.sourceFrameCountPerEnvironment,
    durationSeconds: motion.durationSeconds,
    maximumFixedAxisVarianceMm: motion.maximumFixedAxisVarianceMm,
    maximumPitchRollRadians: motion.maximumPitchRollRadians,
    checks: motion.checks,
  },
  portabilityContractSha256: portability.contractSha256,
  displayMapping: "neutral-display-v1",
  oldEnvironmentPolicy: "rev 8 and older remain immutable stale history; none is a current target input",
  reviewQuestion: "这个目标环境是否只改变环境反射，并正确保留顶面血红图案、纯深色侧壁和亮银细边？",
  interactiveReviewArtifactId: `${modelId}-environment-lookdev-r009`,
  deliveryState: {
    visualApproval: "pending",
    simulatorUsed: false,
    unityUsed: false,
    shippingSceneModified: false,
    gate10Advanced: false,
    gate11Advanced: false,
    gate12Started: false,
    buildInstallPhone: false,
    deviceAcceptance: "pending",
  },
};
stage.readiness = {
  ready: true,
  blockers: [],
  note: "Gate 09 rev 9 awaits environment visual approval. 视觉批准待确认，未推送手机。",
};
for (const downstream of manifest.stages.slice(9)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 09 rev 9 awaits visual approval. No downstream evidence is current.";
}
manifest.issues = manifest.issues || [];
for (const issue of manifest.issues) {
  if (issue.id === "slider-gate08-r006-review") issue.status = "resolved-by-chat-approval";
}
manifest.issues.push({
  id: "slider-gate09-r009-review",
  stageId: "09-environment",
  assetId: `${modelId}-environment-turntable-r009`,
  severity: "blocker",
  note: "Gate 09 rev 9 passed environment validation and awaits visual approval.",
  status: "awaiting-user-visual-review",
});
manifest.claims = manifest.claims.filter((claim) => claim.id !== "slider-gate09-r009-current-environment");
manifest.claims.push({
  id: "slider-gate09-r009-current-environment",
  stageId: "09-environment",
  statement: "Gate 09 rev 9 changes only the environment texture input while preserving current geometry, corrected four-zone materials, portable lighting, display mapping, and legal endpoint motion.",
  state: "validated",
  confidence: 1,
  sourceAssetIds: stage.reviewArtifactIds,
  sourceClaimIds: [],
});
manifest.currentStageId = "09-environment";
manifest.currentState.visualApproval = "gate09-rev9-review-pending-not-pushed";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.blenderModelingStatus = "gate09-rev9-ready-for-review";
manifest.currentState.unityStatus = "not-used-old-shipping-default";
manifest.currentState.simulatorStatus = "not-used";
manifest.currentState.workbench = "persistent-seven-tab-current-gate09-environment";
manifest.currentState.diagnosis = "Gate 09 rev 9 provides a fresh, environment-only neutral/target comparison and Unity-portable HDR/cubemap contract from approved Gate 08 rev 6.";
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate09-rev9-current-environment-ready",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "09-environment",
  revision: 9,
  status: "ready_for_review",
  gate08ApprovalExactWording: "你开始吧",
  sourceLightingSha256: build.source.sha256,
  sourceMaterialSha256: build.source.materialSha256,
  geometryDigest: build.source.geometryDigest,
  neutralEnvironmentSha256: build.neutral.sha256,
  targetEnvironmentSha256: build.target.sha256,
  cubemapOrientationErrorDegrees: build.cubemap.brightestDirectionAngularErrorDegrees,
  portabilityContractSha256: portability.contractSha256,
  comparisonTurntableSha256: motion.videoSha256,
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  validation: {
    environmentBuild: "pass",
    blenderHdrCubemapGlb: "pass",
    imageColorReflectionClipping: "pass",
    endpointMotion: "pass",
    portabilityContract: "pass",
  },
  visualApproval: "pending",
  simulatorUsed: false,
  unityUsed: false,
  shippingChanged: false,
  deviceWork: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate08: "approved",
  gate09: "ready_for_review",
  targetEnvironmentSha256: build.target.sha256,
  portabilityContractSha256: portability.contractSha256,
}, null, 2));
