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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-005";
const candidateRoot =
  "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate08R005EndpointLighting";
const manifest = loadManifest(modelId);
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
const stage = manifest.stages.find((item) => item.id === "08-lighting");
if (manifest.revision !== 231 || gate07?.status !== "approved" || stage?.lightingSpec?.revision !== 5) {
  throw new Error("Expected approved Gate 07 rev 12 and draft Gate 08 rev 5 at revision 231.");
}
const blender = JSON.parse(fs.readFileSync(resolveRepoPath(`${evidenceRoot}/blender-lighting-report.json`)));
const unity = JSON.parse(fs.readFileSync(resolveRepoPath(`${evidenceRoot}/neutral-parity-unity-report.json`)));
const audit = JSON.parse(fs.readFileSync(resolveRepoPath(`${evidenceRoot}/lighting-parity-audit.json`)));
const motion = JSON.parse(fs.readFileSync(resolveRepoPath(`${evidenceRoot}/legal-lighting-turntable-report.json`)));
if (!blender.pass || !unity.pass || !audit.pass || !motion.pass) {
  throw new Error("Gate 08 rev 5 evidence is not fully validated.");
}
const definitions = [
  ["starter", "workflow-source", `${evidenceRoot}/start_gate08_endpoint_lighting.mjs`, "process"],
  ["builder", "lighting-builder-source", `${evidenceRoot}/build_gate08_endpoint_lighting.py`, "process"],
  ["display", "display-transform-source", `${evidenceRoot}/apply_shared_display.py`, "process"],
  ["auditor", "validation-source", `${evidenceRoot}/audit_gate08_endpoint_lighting.py`, "process"],
  ["turntable-builder", "recording-source", `${evidenceRoot}/render_legal_lighting_turntable.py`, "process"],
  ["board-builder", "review-builder-source", `${evidenceRoot}/build_lighting_review_board.py`, "process"],
  ["registrar", "registration-source", `${evidenceRoot}/register_gate08_endpoint_review.mjs`, "process"],
  ["blend", "source-blend", `${evidenceRoot}/magnetic-slide-tile-lighting-r005.blend`, "source-model"],
  ["environment", "portable-environment", `${evidenceRoot}/neutral-parity-studio-r005.exr`, "source-model"],
  ["blender-report", "lighting-recipe", `${evidenceRoot}/blender-lighting-report.json`, "validation"],
  ["unity-report", "unity-lighting-report", `${evidenceRoot}/neutral-parity-unity-report.json`, "validation"],
  ["display-report", "display-transform-report", `${evidenceRoot}/shared-display-report.json`, "validation"],
  ["parity-audit", "full-frame-parity-report", `${evidenceRoot}/lighting-parity-audit.json`, "validation"],
  ["motion-audit", "endpoint-motion-report", `${evidenceRoot}/legal-lighting-turntable-report.json`, "validation"],
  ["hero", "hero", `${evidenceRoot}/hero.png`, "blender-render"],
  ["left", "left-oblique", `${evidenceRoot}/left-oblique.png`, "blender-render"],
  ["right", "right-oblique", `${evidenceRoot}/right-oblique.png`, "blender-render"],
  ["low", "low", `${evidenceRoot}/low.png`, "blender-render"],
  ["beauty", "beauty", `${evidenceRoot}/pass-beauty.png`, "blender-render"],
  ["clay", "clay", `${evidenceRoot}/pass-clay.png`, "blender-render"],
  ["normal", "normal", `${evidenceRoot}/pass-normal.png`, "blender-render"],
  ["depth", "depth", `${evidenceRoot}/pass-depth.png`, "blender-render"],
  ["roughness", "roughness", `${evidenceRoot}/pass-roughness.png`, "blender-render"],
  ["mid", "legal-intermediate-slide", `${evidenceRoot}/legal-mid-slide-0.png`, "blender-render"],
  ["max0", "legal-max-open-0", `${evidenceRoot}/legal-max-open-0.png`, "blender-render"],
  ["max12", "legal-max-open-12", `${evidenceRoot}/legal-max-open-12.png`, "blender-render"],
  ["max36", "legal-max-open-36", `${evidenceRoot}/legal-max-open-36.png`, "blender-render"],
  ["board", "lighting-review-board", `${evidenceRoot}/gate08-r005-lighting-review-board.png`, "source-model"],
  ["comparison", "blender-unity-comparison", `${evidenceRoot}/gate08-r005-blender-unity-comparison.png`, "source-model"],
  ["turntable", "lighting-turntable-recording", `${evidenceRoot}/gate08-r005-endpoint-lighting-turntable.mp4`, "source-model"],
  ["blender-full", "blender-portable-display", `${evidenceRoot}/blender-full-model-display.png`, "blender-render"],
  ["unity-full", "unity-portable-display", `${evidenceRoot}/unity-full-model-display.png`, "unity-render"],
  ["heatmap", "difference-heatmap", `${evidenceRoot}/full-model-heatmap.png`, "validation"],
  ["unity-fbx", "isolated-unity-preview-fbx", `${candidateRoot}/Models/magnetic-slide-tile-lighting-r005-unity-preview.fbx`, "source-model"],
  ["unity-builder", "unity-builder-source", `${candidateRoot}/Editor/MagneticSlideTileEndpointLightingBuilder.cs`, "process"],
  ["unity-surface", "unity-shader-source", `${candidateRoot}/Shaders/MagneticSlideTileNeutralSurfaceR005.shader`, "source-model"],
  ["unity-crystal", "unity-shader-source", `${candidateRoot}/Shaders/MagneticSlideTileNeutralCrystalR005.shader`, "source-model"],
  ["unity-scene", "isolated-unity-lighting-scene", `${candidateRoot}/Scenes/MagneticSlideTileNeutralParityR005.unity`, "unity-render"],
  ["unity-cubemap", "unity-portable-environment", `${candidateRoot}/Environment/NeutralParityStudioR005.cubemap`, "unity-render"],
  ["unity-log", "unity-log", `${evidenceRoot}/unity-lighting.log`, "validation"],
];
const sourceAssetIds = [
  "magnetic-slide-tile-material-blend-r012",
  "magnetic-slide-tile-lighting-environment-r004",
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-lighting-${suffix}-r005`,
    stageId: "08-lighting",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: path.includes("/Assets/") ? "Unity 6000.5.6f1 URP 17.5" : "Gate 08 endpoint lighting workflow",
      version: "Blender 5.2.0 / Unity 6000.5.6f1 / Python 3 / Node.js",
      recipe: `${evidenceRoot}/build_gate08_endpoint_lighting.py`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate08Revision: 5,
      sourceGate07Revision: 12,
      sourceMaterialSha256: gate07.materialSpec.authoritativeBlendSha256,
      geometryDigest: gate07.materialSpec.evaluatedGeometryDigest,
      mechanismEvidenceContractSha256: gate07.materialSpec.governingContractSha256,
      note: "Rev 4 portable shared-HDR recipe regenerated on approved rev 12 materials with endpoint-only legal motion. No shipping or device work.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
stage.status = "ready_for_review";
stage.decision = null;
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  `${modelId}-lighting-turntable-r005`,
  `${modelId}-lighting-board-r005`,
  `${modelId}-lighting-comparison-r005`,
  `${modelId}-lighting-hero-r005`,
];
stage.validations = [
  {
    id: "approved-input-hashes",
    status: "pass",
    evidence: `Geometry ${audit.sourceHashes.geometryDigest}; material ${audit.sourceHashes.materialBlend}; contract ${audit.sourceHashes.contract}.`,
  },
  {
    id: "portable-shared-hdr-display",
    status: "pass",
    evidence: `One ${audit.environment.resolution.join("×")} scene-linear HDR source at 0.85 strength; Unity RGBAHalf; neutral-display-v1 in both engines.`,
  },
  {
    id: "required-cameras-and-passes",
    status: "pass",
    evidence: "Hero, left/right oblique, low, Beauty, Clay, camera-space Normal, camera-space Depth and Roughness evidence are registered.",
  },
  {
    id: "full-frame-portable-parity",
    status: "pass",
    evidence: `SSIM ${audit.parity.ssim.toFixed(3)}, silhouette IoU ${audit.parity.alignment.intersectionOverUnion.toFixed(3)}, MAE ${audit.parity.meanAbsoluteError.toFixed(2)} without independent cropping or post-alignment.`,
  },
  {
    id: "source-faithful-appearance",
    status: "pass",
    evidence: `Blood-red fractions Blender/Unity ${(audit.appearance.blenderRedFraction * 100).toFixed(1)}%/${(audit.appearance.unityRedFraction * 100).toFixed(1)}%; dark-pattern fractions ${(audit.appearance.blenderDarkFraction * 100).toFixed(1)}%/${(audit.appearance.unityDarkFraction * 100).toFixed(1)}%; zero emission.`,
  },
  {
    id: "endpoint-interlock-motion",
    status: "pass",
    evidence: `90 real Blender frames: slide at 0°, full 360° only at sMax, return after 360° alignment; fixed-axis variance ${motion.maximumFixedAxisVarianceMm} mm; pitch/roll ${motion.maximumPitchRollRadians} rad.`,
  },
  {
    id: "shipping-and-device-gate",
    status: "pass",
    evidence: "Only an isolated Unity lighting candidate changed. Shipping scene hash stayed unchanged. No Simulator, build, install or phone work occurred.",
  },
];
stage.lightingSpec = {
  ...stage.lightingSpec,
  revision: 5,
  evidenceRevision: 5,
  sourceMaterialRevision: 12,
  sourceMaterialSha256: gate07.materialSpec.authoritativeBlendSha256,
  geometryDigest: gate07.materialSpec.evaluatedGeometryDigest,
  mechanismContractSha256: gate07.materialSpec.governingContractSha256,
  portableRecipe: {
    baseline: "Gate 08 rev 4",
    projection: "equirectangular",
    environmentSha256: audit.sourceHashes.environment,
    resolution: audit.environment.resolution,
    colorSpace: audit.environment.colorSpace,
    strength: audit.environment.strength,
    directLightCount: 0,
    reflectionSourceCount: 1,
    groundCount: 0,
    displayTransform: "neutral-display-v1",
  },
  parityMetrics: audit.parity,
  appearanceMetrics: audit.appearance,
  cameraRecipes: audit.cameraRecipes,
  legalMotionRecording: {
    assetId: `${modelId}-lighting-turntable-r005`,
    sha256: motion.videoSha256,
    durationSeconds: motion.durationSeconds,
    frameCount: motion.frameCount,
  },
  reviewQuestion: "这组共享 HDR 灯光是否同时保留亮银边、血红晶体、黑色纹样，并在合法端点运动中清楚揭示几何？",
  interactiveReviewArtifactId: `${modelId}-lighting-turntable-r005`,
  deliveryState: {
    visualApproval: "pending",
    shippingSceneModified: false,
    gate09Advanced: false,
    gate11Ready: false,
    gate12Started: false,
    buildInstallPhone: false,
  },
};
stage.readiness = {
  ready: true,
  blockers: [],
  note: "Gate 08 rev 5 is ready for visual review. 视觉批准待确认，未推送手机。",
};
delete stage.staleReason;
for (const downstream of manifest.stages.slice(8)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 08 rev 5 awaits visual approval. No downstream shipping evidence is current.";
}
manifest.claims = manifest.claims.filter((claim) => claim.id !== "slider-gate08-r005-endpoint-lighting");
manifest.claims.push({
  id: "slider-gate08-r005-endpoint-lighting",
  stageId: "08-lighting",
  topic: "portable-lighting-endpoint-motion",
  statement: "Approved rev 12 materials retain their geometry and appearance hashes under the rev 4 portable shared-HDR recipe. Current motion evidence rotates only at maximum slide and returns only at 0/360 alignment.",
  confidence: "verified",
  state: "active",
  assertedBy: "measurement",
  sourceAssetIds: [
    `${modelId}-lighting-parity-audit-r005`,
    `${modelId}-lighting-motion-audit-r005`,
    `${modelId}-lighting-turntable-r005`,
  ],
  sourceRegions: [],
  decisionState: "awaiting-gate08-visual-review",
  deliveryState: "not-shipping-not-device",
});
manifest.issues = (manifest.issues || []).filter((issue) => issue.id !== "slider-gate08-r005-review");
manifest.issues.push({
  id: "slider-gate08-r005-review",
  stageId: "08-lighting",
  assetId: `${modelId}-lighting-turntable-r005`,
  severity: "blocker",
  note: "Gate 08 rev 5 visual approval is pending. Gate 09-12 remain stale.",
});
const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims.filter((claim) => claim.stageId === current.id).map(stableJson);
  current.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claims]);
}
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
manifest.currentStageId = "08-lighting";
manifest.currentState.visualApproval = "gate08-rev5-review-pending-not-pushed";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.blenderModelingStatus = "gate08-rev5-ready-for-review";
manifest.currentState.unityStatus = "isolated-portable-lighting-validation-only-old-shipping-default";
manifest.currentState.workbench = "persistent-seven-tab-current-gate08-lighting";
manifest.currentState.diagnosis = "Gate 08 rev 5 regenerates the rev 4 shared-HDR baseline on approved rev 12 geometry/materials and replaces stale simultaneous-motion evidence with endpoint-only legal motion.";
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate08-rev5-endpoint-lighting-ready",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "08-lighting",
  revision: 5,
  status: "ready_for_review",
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  sourceMaterialSha256: gate07.materialSpec.authoritativeBlendSha256,
  geometryDigest: gate07.materialSpec.evaluatedGeometryDigest,
  mechanismContractSha256: gate07.materialSpec.governingContractSha256,
  environmentSha256: audit.sourceHashes.environment,
  parity: audit.parity,
  endpointMotion: {
    videoSha256: motion.videoSha256,
    fixedAxisVarianceMm: motion.maximumFixedAxisVarianceMm,
    maximumPitchRollRadians: motion.maximumPitchRollRadians,
  },
  visualApproval: "pending",
  shippingChanged: false,
  buildInstallPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate07: saved.stages[6].status,
  gate08: saved.stages[7].status,
  downstream: saved.stages.slice(8).map(({ id, status }) => ({ id, status })),
}, null, 2));
