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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-003";
const candidateRoot =
  "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate08R003PortableValidation";
const manifest = loadManifest(modelId);
const stage = manifest.stages.find((item) => item.id === "08-lighting");
if (manifest.revision !== 206 || stage?.status !== "approved") {
  throw new Error("Expected approved Gate 08 at pipeline revision 206.");
}

const report = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/portability-root-cause-report.json`)));
const blender = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/portable-lighting-report.json`)));
if (!report.pass || !blender.pass || report.checks.visualParityReady) {
  throw new Error("Portable evidence must pass diagnosis and remain parity-blocked.");
}

const definitions = [
  ["builder", "blender-builder-source", `${evidenceRoot}/build_portable_lighting.py`, "process"],
  ["auditor", "validation-source", `${evidenceRoot}/build_portability_audit.py`, "process"],
  ["registrar", "registration-source", `${evidenceRoot}/register_portable_gate08_r003.mjs`, "process"],
  ["recipe-report", "lighting-recipe", `${evidenceRoot}/portable-lighting-report.json`, "validation"],
  ["root-cause-report", "portability-report", `${evidenceRoot}/portability-root-cause-report.json`, "validation"],
  ["blend", "source-blend", `${evidenceRoot}/magnetic-slide-tile-lighting-r003-portable.blend`, "source-model"],
  ["environment", "portable-environment", `${evidenceRoot}/portable-studio-r003.exr`, "source-model"],
  ["environment-only", "controlled-render", `${evidenceRoot}/portable-env-only.png`, "source-model"],
  ["blender-beauty", "beauty", `${evidenceRoot}/portable-beauty.png`, "source-model"],
  ["blender-clay", "clay", `${evidenceRoot}/portable-clay.png`, "source-model"],
  ["unity-builder", "unity-builder-source", `${candidateRoot}/Editor/MagneticSlideTilePortableLightingBuilder.cs`, "process"],
  ["unity-shader", "shader-source", `${candidateRoot}/Shaders/MagneticSlideTilePortableCrystal.shader`, "source-model"],
  ["unity-scene", "unity-validation-scene", `${candidateRoot}/Scenes/MagneticSlideTilePortableLightingR003.unity`, "unity-render"],
  ["unity-beauty", "unity-beauty", `${evidenceRoot}/unity-portable-beauty.png`, "unity-render"],
  ["unity-clay", "unity-clay", `${evidenceRoot}/unity-portable-clay.png`, "unity-render"],
  ["unity-log", "unity-log", `${evidenceRoot}/unity-portable-build.log`, "validation"],
  ["heatmap", "difference-heatmap", `${evidenceRoot}/portable-parity-heatmap.png`, "validation"],
  ["board", "portability-review-board", `${evidenceRoot}/gate08-r003-portability-board.png`, "source-model"],
  ["comparison-recording", "lighting-comparison-recording", `${evidenceRoot}/gate08-r003-old-new-unity-review.mp4`, "source-model"],
  ["unity-orbit", "unity-runtime-recording", `${evidenceRoot}/unity-portable-orbit.mp4`, "unity-render"],
];

const sourceAssetIds = ["magnetic-slide-tile-material-blend-r011"];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-lighting-${suffix}-r003`,
    stageId: "08-lighting",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: path.includes("/Assets/") ? "Unity 6000.5.6f1 URP 17.5" : "Portable Gate 08 workflow",
      version: "Blender 5.2.0 / Unity 6000.5.6f1 / Python 3",
      recipe: `${evidenceRoot}/build_portable_lighting.py`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate08Revision: 3,
      mechanismEvidenceContractSha256:
        "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea",
      note: "Cross-engine lighting portability candidate. Geometry, material and artwork remain unchanged. No shipping or device work.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);

stage.historicalRevisions = stage.historicalRevisions || [];
stage.historicalRevisions.push({
  evidenceRevision: 2,
  status: "approved-then-staled-by-portability-failure",
  artifactIds: [...stage.artifactIds],
  reviewArtifactIds: [...stage.reviewArtifactIds],
  validations: structuredClone(stage.validations),
  decision: structuredClone(stage.decision),
  lightingSpec: structuredClone(stage.lightingSpec),
  preservedForHistory: true,
});
for (const id of stage.artifactIds) {
  const asset = manifest.assets.find((item) => item.id === id);
  if (asset) {
    asset.reviewState = "approved-history-stale";
    asset.preservedForHistory = true;
  }
}

stage.revision = 6;
stage.status = "ready_for_review";
stage.decision = null;
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  `${modelId}-lighting-comparison-recording-r003`,
  `${modelId}-lighting-board-r003`,
  `${modelId}-lighting-blender-beauty-r003`,
  `${modelId}-lighting-unity-beauty-r003`,
  `${modelId}-lighting-unity-orbit-r003`,
];
stage.validations = [
  {
    id: "portable-root-cause",
    status: "pass",
    evidence: "Gate 08 is the earliest portability failure: Blender area lights and hidden reflection cards have no direct mobile URP mapping.",
  },
  {
    id: "approved-exr-rgb-audit",
    status: "pass",
    evidence: "Gate 09 rev 8 EXR RGB is 0 for every pixel; the new EXR has 100% nonzero RGB and a zero seam delta.",
  },
  {
    id: "geometry-material-artwork-preserved",
    status: "pass",
    evidence: "Geometry e2a838c2…, material 366b788b… and all core matrices remain unchanged; emission stays zero.",
  },
  {
    id: "shared-portable-recipe",
    status: "pass",
    evidence: "Both engines use one 2048×1024 linear D65 EXR at rotation 0°/strength 0.125, one D65 directional light, shadow-map contact, no area lights, no cards, no synthetic highlight and an identity display LUT.",
  },
  {
    id: "raw-full-frame-audit",
    status: "pass",
    evidence: `All panels are uncropped 1400×1100. SSIM ${report.fullFrame.ssim.toFixed(3)}, heatmap >24 ${(report.fullFrame.heatmapAreaFractionOver24 * 100).toFixed(2)}%, object DeltaE76 median ${report.fullFrame.regionalDeltaE76.object.median.toFixed(1)}.`,
  },
  {
    id: "renewed-visual-review",
    status: "pass",
    evidence: "The portable target materially changes the approved Blender appearance, so Gate 08 stops for renewed user review.",
  },
  {
    id: "shipping-and-device-gate",
    status: "pass",
    evidence: "Shipping scene is unchanged. Gate 09-12, build, install and phone work did not advance.",
  },
];
stage.lightingSpec = {
  revision: 3,
  sourceMaterialRevision: 11,
  geometryDigest: blender.geometryDigest.after,
  materialDigest: blender.materialDigest.after,
  portableRecipe: blender.portableRecipe,
  portabilityAudit: report,
  reviewQuestion:
    "新的可移植灯光方向是否保留了血红水晶、黑色纹样和银色边缘，同时适合作为 Blender 与 Unity 的共同基准？",
  interactiveReviewArtifactId: `${modelId}-lighting-comparison-recording-r003`,
  unityValidationScene:
    "Assets/_EDC/Candidates/MagneticSlideTileGate08R003PortableValidation/Scenes/MagneticSlideTilePortableLightingR003.unity",
  deliveryState: {
    visualApproval: "pending",
    shippingSceneModified: false,
    gate09Advanced: false,
    gate11Ready: false,
    gate12Started: false,
    buildInstallPhone: false,
  },
};
delete stage.staleReason;

for (const downstream of manifest.stages.slice(8)) {
  downstream.status = "stale";
  downstream.staleReason =
    "Gate 08 rev 3 replaces the non-portable approved lighting target and awaits renewed visual approval. Existing revisions remain preserved.";
}
manifest.claims.push({
  id: "slider-gate08-r003-portability-root-cause",
  stageId: "08-lighting",
  topic: "cross-engine-lighting-portability",
  statement:
    "The earliest parity failure is Gate 08: Blender-only area lights and hidden reflection cards defined the target highlight. Gate 09 then supplied an all-zero RGB EXR, while Gate 11 added synthetic and duplicate reflection terms.",
  confidence: "verified",
  state: "active",
  assertedBy: "measurement",
  sourceAssetIds: records
    .filter((record) => ["portability-report", "lighting-recipe", "portability-review-board"].includes(record.slot))
    .map((record) => record.id),
  sourceRegions: [],
  decisionState: "awaiting-renewed-gate08-visual-review",
  deliveryState: "not-shipping-not-device",
});
manifest.issues = (manifest.issues || []).filter(
  (issue) => !issue.id?.startsWith("slider-gate08-r003"));
manifest.issues.push({
  id: "slider-gate08-r003-renewed-review",
  stageId: "08-lighting",
  assetId: `${modelId}-lighting-board-r003`,
  severity: "blocker",
  note: "The portable target materially changes the approved Blender appearance. Gate 09 and downstream work wait for renewed visual approval.",
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
manifest.currentState.visualApproval =
  "gate08-rev3-portable-lighting-review-pending-not-pushed";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.blenderModelingStatus =
  "gate08-rev3-portable-lighting-ready-for-review";
manifest.currentState.diagnosis =
  "Gate 08 is the earliest portability failure. Rev 3 removes Blender-only area lights and reflection cards, replaces the invalid zero-RGB EXR, and uses one shared environment plus one D65 directional light. The appearance changed materially, so Gate 08 awaits renewed visual review and Gates 09-12 remain stale.";
manifest.currentStageId = "08-lighting";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "upstream-portability-invalidation",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "08-lighting",
  revision: 3,
  status: "ready_for_review",
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  rootCause: report.rootCause,
  downstreamStages: manifest.stages.slice(8).map((item) => ({
    id: item.id,
    status: item.status,
  })),
  visualApproval: "pending",
  buildInstallPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate08: saved.stages[7].status,
  gate09: saved.stages[8].status,
  gate10: saved.stages[9].status,
  gate11: saved.stages[10].status,
  gate12: saved.stages[11].status,
}, null, 2));
