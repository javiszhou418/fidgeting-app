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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-006";
const manifest = loadManifest(modelId);
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
const stage = manifest.stages.find((item) => item.id === "08-lighting");
if (manifest.revision !== 238
  || gate07?.status !== "approved"
  || gate07?.decision?.notes !== "通过"
  || stage?.status !== "draft"
  || stage?.lightingSpec?.revision !== 6) {
  throw new Error("Expected approved Gate 07 rev 13 and draft Gate 08 rev 6 at revision 238.");
}

const blender = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/blender-lighting-report.json`),
));
const audit = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/lighting-material-audit.json`),
));
const motion = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/legal-lighting-turntable-report.json`),
));
const frames = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/frame-partition-audit.json`),
));
const boards = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/review-board-report.json`),
));
if (!blender.pass || !audit.pass || !motion.pass || !frames.pass || !boards.pass) {
  throw new Error("Gate 08 rev 6 evidence is not fully validated.");
}

const definitions = [
  ["starter", "workflow-source", `${evidenceRoot}/start_gate08_partition_safe_lighting.mjs`, "process"],
  ["builder", "lighting-builder-source", `${evidenceRoot}/build_gate08_partition_safe_lighting.py`, "process"],
  ["auditor", "validation-source", `${evidenceRoot}/audit_gate08_partition_safe_lighting.py`, "process"],
  ["turntable-builder", "recording-source", `${evidenceRoot}/render_legal_lighting_turntable.py`, "process"],
  ["board-builder", "review-builder-source", `${evidenceRoot}/build_lighting_review_boards.py`, "process"],
  ["registrar", "registration-source", `${evidenceRoot}/register_gate08_partition_safe_review.mjs`, "process"],
  ["blend", "source-blend", `${evidenceRoot}/magnetic-slide-tile-lighting-r006.blend`, "source-model"],
  ["lookdev", "interactive-lighting-lookdev", `${evidenceRoot}/magnetic-slide-tile-lighting-lookdev-r006.glb`, "source-model"],
  ["environment", "portable-environment", `${evidenceRoot}/neutral-parity-studio-r006.exr`, "source-model"],
  ["blender-report", "lighting-recipe", `${evidenceRoot}/blender-lighting-report.json`, "validation"],
  ["material-audit", "lighting-material-audit", `${evidenceRoot}/lighting-material-audit.json`, "validation"],
  ["frame-audit", "frame-partition-audit", `${evidenceRoot}/frame-partition-audit.json`, "validation"],
  ["motion-audit", "endpoint-motion-report", `${evidenceRoot}/legal-lighting-turntable-report.json`, "validation"],
  ["board-report", "review-board-report", `${evidenceRoot}/review-board-report.json`, "validation"],
  ["hero", "hero", `${evidenceRoot}/hero.png`, "blender-render"],
  ["left", "left-oblique", `${evidenceRoot}/left-oblique.png`, "blender-render"],
  ["right", "right-oblique", `${evidenceRoot}/right-oblique.png`, "blender-render"],
  ["low", "low", `${evidenceRoot}/low.png`, "blender-render"],
  ["beauty", "beauty", `${evidenceRoot}/pass-beauty.png`, "blender-render"],
  ["clay", "clay", `${evidenceRoot}/pass-clay.png`, "blender-render"],
  ["normal", "normal", `${evidenceRoot}/pass-normal.png`, "blender-render"],
  ["depth", "depth", `${evidenceRoot}/pass-depth.png`, "blender-render"],
  ["roughness", "roughness", `${evidenceRoot}/pass-roughness.png`, "blender-render"],
  ["top-closeup", "top-closeup", `${evidenceRoot}/closeup-top.png`, "blender-render"],
  ["side-closeup", "side-closeup-zero-artwork", `${evidenceRoot}/closeup-side.png`, "blender-render"],
  ["rim-closeup", "rim-closeup-silver", `${evidenceRoot}/closeup-rim.png`, "blender-render"],
  ["mid", "legal-intermediate-slide", `${evidenceRoot}/legal-mid-slide-0.png`, "blender-render"],
  ["max0", "legal-max-open-0", `${evidenceRoot}/legal-max-open-0.png`, "blender-render"],
  ["max12", "legal-max-open-12", `${evidenceRoot}/legal-max-open-12.png`, "blender-render"],
  ["max36", "legal-max-open-36", `${evidenceRoot}/legal-max-open-36.png`, "blender-render"],
  ["max360", "legal-max-open-360", `${evidenceRoot}/legal-max-open-360.png`, "blender-render"],
  ["lighting-board", "lighting-review-board", `${evidenceRoot}/gate08-r006-lighting-review-board.png`, "source-model"],
  ["partition-board", "partition-closeup-board", `${evidenceRoot}/gate08-r006-partition-closeups.png`, "source-model"],
  ["turntable", "lighting-turntable-recording", `${evidenceRoot}/gate08-r006-endpoint-lighting-turntable.mp4`, "source-model"],
];
const sourceAssetIds = [
  "magnetic-slide-tile-material-blend-r013",
  "magnetic-slide-tile-material-lookdev-r013",
  "magnetic-slide-tile-lighting-environment-r004",
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-lighting-${suffix}-r006`,
    stageId: "08-lighting",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Gate 08 partition-safe lighting workflow",
      version: "Blender 5.2.0 LTS / Python 3 / Node.js",
      recipe: `${evidenceRoot}/build_gate08_partition_safe_lighting.py`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate08Revision: 6,
      sourceGate07Revision: 13,
      sourceMaterialSha256: gate07.materialSpec.authoritativeBlendSha256,
      geometryDigest: gate07.materialSpec.evaluatedGeometryDigest,
      mechanismEvidenceContractSha256: gate07.materialSpec.governingContractSha256,
      materialPartitionDigests: Object.fromEntries(
        Object.entries(gate07.materialSpec.partitions)
          .map(([name, values]) => [name, values.partitionDigest]),
      ),
      diagnosticPassPolicy: "duplicate scene, object, and mesh data",
      note: "Portable shared-HDR lighting regenerated from approved rev 13 partitions. No Simulator, Unity, shipping, build, install, or device work.",
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
  `${modelId}-lighting-lookdev-r006`,
  `${modelId}-lighting-turntable-r006`,
  `${modelId}-lighting-lighting-board-r006`,
  `${modelId}-lighting-partition-board-r006`,
  `${modelId}-lighting-hero-r006`,
];
stage.validations = [
  {
    id: "approved-input-hashes",
    status: "pass",
    evidence: `Gate 07 approval “通过”; geometry ${audit.sourceHashes.geometryDigest}; material ${audit.sourceHashes.materialBlend}; contract ${audit.sourceHashes.contract}.`,
  },
  {
    id: "portable-shared-hdr-display",
    status: "pass",
    evidence: `Regenerated ${audit.environment.resolution.join("×")} scene-linear HDR matches portable rev 4 hash ${audit.sourceHashes.environment}; neutral-display-v1; zero direct lights.`,
  },
  {
    id: "non-destructive-diagnostic-passes",
    status: "pass",
    evidence: "Clay, Normal, Depth and Roughness used duplicate scenes, objects and mesh datablocks. Material slots, polygon indices, UVs, geometry and zone attributes remained byte/element identical.",
  },
  {
    id: "corrected-material-partitions",
    status: "pass",
    evidence: "Every render/export check kept side and underside artwork at 0, cap artwork present, silver rim present, fixed slot order, and approved partition digests.",
  },
  {
    id: "required-cameras-passes-closeups",
    status: "pass",
    evidence: "Hero, left/right oblique, low, Beauty, Clay, Normal, Depth, Roughness, top, side and rim closeups are registered.",
  },
  {
    id: "glb-transport-and-lookdev",
    status: "pass",
    evidence: "Interactive GLB re-import preserves both four-zone partitions, bounded cap UVs and CLAMP_TO_EDGE samplers.",
  },
  {
    id: "endpoint-interlock-motion",
    status: "pass",
    evidence: `${motion.frameCount} real Blender frames: slide at 0°, full 360° only at sMax, return after 360° alignment; fixed-axis variance ${motion.maximumFixedAxisVarianceMm} mm; pitch/roll ${motion.maximumPitchRollRadians} rad.`,
  },
  {
    id: "scope-gate",
    status: "pass",
    evidence: "No Simulator, Unity, shipping scene, build, install or device work occurred. Gates 09–12 remain stale.",
  },
];
stage.lightingSpec = {
  ...stage.lightingSpec,
  revision: 6,
  evidenceRevision: 6,
  sourceMaterialRevision: 13,
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
  immutableSourceSnapshot: {
    before: blender.meshSnapshotBefore,
    after: blender.meshSnapshotAfter,
    byteElementIdentical: blender.sourceMeshDataElementIdentical,
  },
  diagnosticPasses: blender.diagnosticPasses,
  materialTransport: audit.importedGlb,
  cameraRecipes: audit.cameraRecipes,
  imageMetrics: audit.imageMetrics,
  interactiveLookdev: {
    assetId: `${modelId}-lighting-lookdev-r006`,
    sha256: audit.sourceHashes.interactiveGlb,
  },
  legalMotionRecording: {
    assetId: `${modelId}-lighting-turntable-r006`,
    sha256: motion.videoSha256,
    durationSeconds: motion.durationSeconds,
    frameCount: motion.frameCount,
  },
  reviewQuestion: "这组灯光是否清楚保留顶面血红图案、纯深色侧壁和亮银细边，并揭示几何而不隐藏边界？",
  interactiveReviewArtifactId: `${modelId}-lighting-lookdev-r006`,
  deliveryState: {
    visualApproval: "pending",
    simulatorUsed: false,
    unityUsed: false,
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
  note: "Gate 08 rev 6 is ready for visual review. 视觉批准待确认，未推送手机。",
};
delete stage.staleReason;
for (const downstream of manifest.stages.slice(8)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 08 rev 6 awaits visual approval. No downstream evidence is current.";
}

manifest.claims = manifest.claims.filter(
  (claim) => claim.id !== "slider-gate08-r006-partition-safe-lighting",
);
manifest.claims.push({
  id: "slider-gate08-r006-partition-safe-lighting",
  stageId: "08-lighting",
  topic: "partition-safe-portable-lighting",
  statement: "Gate 08 rev 6 preserves approved rev 13 cap/side/rim/underside partitions through duplicate-only diagnostic passes, GLB export, and endpoint-only motion.",
  confidence: "verified",
  state: "active",
  assertedBy: "measurement",
  sourceAssetIds: [
    `${modelId}-lighting-material-audit-r006`,
    `${modelId}-lighting-motion-audit-r006`,
    `${modelId}-lighting-lookdev-r006`,
  ],
  sourceRegions: [],
  decisionState: "awaiting-gate08-visual-review",
  deliveryState: "not-shipping-not-device",
});
manifest.issues = (manifest.issues || []).filter(
  (issue) => ![
    "slider-gate07-r013-side-partition-review",
    "slider-gate08-r005-review",
    "slider-gate08-r006-review",
  ].includes(issue.id),
);
manifest.issues.push({
  id: "slider-gate08-r006-review",
  stageId: "08-lighting",
  assetId: `${modelId}-lighting-lookdev-r006`,
  severity: "blocker",
  note: "Gate 08 rev 6 passed Blender/material/motion validation and awaits visual approval. Gates 09–12 remain stale.",
  status: "awaiting-user-visual-review",
});

const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`,
    ).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256,
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
manifest.currentState.visualApproval = "gate08-rev6-review-pending-not-pushed";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.blenderModelingStatus = "gate08-rev6-ready-for-review";
manifest.currentState.unityStatus = "not-used-old-shipping-default";
manifest.currentState.simulatorStatus = "not-used";
manifest.currentState.workbench = "persistent-seven-tab-current-gate08-lighting";
manifest.currentState.diagnosis = "Gate 08 rev 6 regenerated portable shared-HDR evidence from approved Gate 07 rev 13 partitions. Duplicate-only diagnostics preserve source slots, indices, UVs and geometry.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate08-rev6-partition-safe-lighting-ready",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "08-lighting",
  revision: 6,
  status: "ready_for_review",
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  gate07ApprovalWording: gate07.decision.notes,
  sourceMaterialSha256: gate07.materialSpec.authoritativeBlendSha256,
  geometryDigest: gate07.materialSpec.evaluatedGeometryDigest,
  mechanismContractSha256: gate07.materialSpec.governingContractSha256,
  environmentSha256: audit.sourceHashes.environment,
  nonDestructiveDiagnostics: true,
  sourceSnapshotElementIdentical: blender.sourceMeshDataElementIdentical,
  sideWallArtwork: 0,
  undersideArtwork: 0,
  endpointMotion: {
    videoSha256: motion.videoSha256,
    fixedAxisVarianceMm: motion.maximumFixedAxisVarianceMm,
    maximumPitchRollRadians: motion.maximumPitchRollRadians,
  },
  visualApproval: "pending",
  simulatorUsed: false,
  unityUsed: false,
  shippingChanged: false,
  buildInstallPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate07: saved.stages[6].status,
  gate08: saved.stages[7].status,
  downstream: saved.stages.slice(8).map(({ id, status }) => ({ id, status })),
}, null, 2));
