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
if (manifest.revision !== 207 || stage?.lightingSpec?.revision !== 3) {
  throw new Error("Expected Gate 08 rev 3 at pipeline revision 207.");
}

const audit = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/neutral-parity-audit.json`)));
const blender = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/neutral-parity-blender-report.json`)));
const unity = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/neutral-parity-unity-report.json`)));
if (
  !blender.pass ||
  !unity.pass ||
  !audit.humanVisualGate.reviewable ||
  audit.humanVisualGate.approved
) {
  throw new Error("Rev 4 must be reviewable, validated and not approved.");
}

const definitions = [
  ["builder", "blender-builder-source", `${evidenceRoot}/build_neutral_parity.py`, "process"],
  ["display", "display-transform-source", `${evidenceRoot}/apply_shared_display.py`, "process"],
  ["auditor", "validation-source", `${evidenceRoot}/audit_neutral_parity.py`, "process"],
  ["review-builder", "review-builder-source", `${evidenceRoot}/build_review_assets.py`, "process"],
  ["direction-probe", "orientation-validation-source", `${evidenceRoot}/probe_blender_environment.py`, "process"],
  ["registrar", "registration-source", `${evidenceRoot}/register_neutral_gate08_r004.mjs`, "process"],
  ["blender-report", "lighting-recipe", `${evidenceRoot}/neutral-parity-blender-report.json`, "validation"],
  ["unity-report", "unity-parity-report", `${evidenceRoot}/neutral-parity-unity-report.json`, "validation"],
  ["audit-report", "full-frame-parity-report", `${evidenceRoot}/neutral-parity-audit.json`, "validation"],
  ["display-report", "display-transform-report", `${evidenceRoot}/shared-display-report.json`, "validation"],
  ["orientation-report", "orientation-validation", `${evidenceRoot}/blender-environment-direction-probe.json`, "validation"],
  ["blend", "source-blend", `${evidenceRoot}/magnetic-slide-tile-lighting-r004-neutral-parity.blend`, "source-model"],
  ["environment", "portable-environment", `${evidenceRoot}/neutral-parity-studio-r004.exr`, "source-model"],
  ["board", "neutral-parity-review-board", `${evidenceRoot}/gate08-r004-neutral-parity-board.png`, "source-model"],
  ["comparison-recording", "lighting-comparison-recording", `${evidenceRoot}/gate08-r004-neutral-parity-review.mp4`, "source-model"],
  ["blender-full", "blender-beauty", `${evidenceRoot}/blender-full-model-display.png`, "source-model"],
  ["unity-full", "unity-beauty", `${evidenceRoot}/unity-full-model-display.png`, "unity-render"],
  ["full-heatmap", "difference-heatmap", `${evidenceRoot}/full-model-heatmap.png`, "validation"],
  ["blender-reflection", "reflection-diagnostic", `${evidenceRoot}/blender-reflection-only-display.png`, "source-model"],
  ["unity-reflection", "reflection-diagnostic", `${evidenceRoot}/unity-reflection-only-display.png`, "unity-render"],
  ["blender-clay", "clay", `${evidenceRoot}/blender-clay-display.png`, "source-model"],
  ["unity-clay", "clay", `${evidenceRoot}/unity-clay-display.png`, "unity-render"],
  ["blender-silver", "silver-diagnostic", `${evidenceRoot}/blender-silver-display.png`, "source-model"],
  ["unity-silver", "silver-diagnostic", `${evidenceRoot}/unity-silver-display.png`, "unity-render"],
  ["blender-crystal", "crystal-diagnostic", `${evidenceRoot}/blender-crystal-display.png`, "source-model"],
  ["unity-crystal", "crystal-diagnostic", `${evidenceRoot}/unity-crystal-display.png`, "unity-render"],
  ["unity-log", "unity-log", `${evidenceRoot}/unity-builder.log`, "validation"],
  ["unity-builder", "unity-builder-source", `${candidateRoot}/Editor/MagneticSlideTileNeutralParityBuilder.cs`, "process"],
  ["unity-surface-shader", "shader-source", `${candidateRoot}/Shaders/MagneticSlideTileNeutralSurfaceR004.shader`, "source-model"],
  ["unity-crystal-shader", "shader-source", `${candidateRoot}/Shaders/MagneticSlideTileNeutralCrystalR004.shader`, "source-model"],
  ["unity-scene", "unity-validation-scene", `${candidateRoot}/Scenes/MagneticSlideTileNeutralParityR004.unity`, "unity-render"],
  ["unity-cubemap", "unity-environment", `${candidateRoot}/Environment/NeutralParityStudioR004.cubemap`, "unity-render"],
  ["unity-test", "test-source", "unity/FidgetingApp/Assets/Tests/Editor/MagneticSlideTileNeutralParityTests.cs", "validation"],
];

const sourceAssetIds = ["magnetic-slide-tile-material-blend-r011"];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-lighting-${suffix}-r004`,
    stageId: "08-lighting",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: path.includes("/Assets/")
        ? "Unity 6000.5.6f1 URP 17.5"
        : "Gate 08 neutral parity workflow",
      version: "Blender 5.2.0 / Unity 6000.5.6f1 / Python 3",
      recipe: `${evidenceRoot}/build_neutral_parity.py`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate08Revision: 4,
      mechanismEvidenceContractSha256:
        "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea",
      note: "Single-HDR-environment neutral parity candidate. No ground, direct light, shipping or device work.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);

stage.historicalRevisions = stage.historicalRevisions || [];
stage.historicalRevisions.push({
  evidenceRevision: 3,
  status: "superseded-not-visually-acceptable",
  artifactIds: [...stage.artifactIds],
  reviewArtifactIds: [...stage.reviewArtifactIds],
  validations: structuredClone(stage.validations),
  lightingSpec: structuredClone(stage.lightingSpec),
  preservedForHistory: true,
  userDecision:
    "Continue correcting Gate 08 portability; the current rev 3 is informative but not visually acceptable and must not be presented for approval. Preserve rev 3. Do not advance Gate 09/11/12.",
});
for (const id of stage.artifactIds) {
  const asset = manifest.assets.find((item) => item.id === id);
  if (asset) {
    asset.reviewState = "superseded-not-visually-acceptable";
    asset.preservedForHistory = true;
  }
}

stage.revision = 7;
stage.status = "ready_for_review";
stage.decision = null;
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  `${modelId}-lighting-comparison-recording-r004`,
  `${modelId}-lighting-board-r004`,
  `${modelId}-lighting-blender-full-r004`,
  `${modelId}-lighting-unity-full-r004`,
];
stage.validations = [
  {
    id: "single-hdr-reflection-source",
    status: "pass",
    evidence:
      "One nonzero 2048×1024 RGBAHalf EXR/cubemap is the only reflection source. Direct lights, ground, probes, SH, reflection cards and synthetic highlights are absent.",
  },
  {
    id: "hdr-import-and-orientation",
    status: "pass",
    evidence:
      `Unity source format ${unity.environment.sourceTextureFormat}, source max ${unity.environment.sourceMaximum.toFixed(3)}, cubemap max ${unity.environment.cubemapMaximum.toFixed(3)}, direction-marker max delta ${unity.environment.directionMarkerMaxAbsoluteDelta.toFixed(6)}.`,
  },
  {
    id: "geometry-material-artwork-preserved",
    status: "pass",
    evidence:
      "Geometry e2a838c2…, material 366b788b…, core matrices, artwork and zero emission remain unchanged.",
  },
  {
    id: "shared-linear-display",
    status: "pass",
    evidence:
      "Both engines emit scene-linear Rec.709/D65 HDR EXR and use the same neutral-display-v1 transform after render.",
  },
  {
    id: "controlled-full-frame-diagnostics",
    status: "pass",
    evidence:
      "Reflection, clay, silver, crystal and full-model pairs use uncropped 1400×1100 frames with an identical flat background and no contact shadow.",
  },
  {
    id: "full-model-parity",
    status: "pass",
    evidence:
      `SSIM ${audit.diagnostics["full-model"].fullFrame.ssim.toFixed(3)}, heatmap >24 ${(audit.diagnostics["full-model"].fullFrame.heatmapAreaFractionOver24 * 100).toFixed(2)}%, object DeltaE76 median ${audit.diagnostics["full-model"].fullFrame.deltaE76.median.toFixed(1)}.`,
  },
  {
    id: "silver-parity",
    status: "pass",
    evidence:
      `Silver SSIM ${audit.diagnostics.silver.fullFrame.ssim.toFixed(3)}, DeltaE76 median ${audit.diagnostics.silver.fullFrame.deltaE76.median.toFixed(2)}, clipping Blender/Unity ${(audit.diagnostics.silver.clipping.blender * 100).toFixed(3)}%/${(audit.diagnostics.silver.clipping.unity * 100).toFixed(3)}%.`,
  },
  {
    id: "human-visual-gate",
    status: "pass",
    evidence:
      "Direct board inspection found a bright neutral silver response, visible deep blood red, crisp motif and no dark-object, background, ground or duplicate-highlight failure.",
  },
  {
    id: "shipping-and-device-gate",
    status: "pass",
    evidence:
      "Shipping scene hash is unchanged. Gate 09-12, build, install and phone work did not advance.",
  },
];
stage.lightingSpec = {
  revision: 4,
  sourceMaterialRevision: 11,
  geometryDigest: blender.geometryDigest.after,
  materialDigest: blender.materialDigest.after,
  portableRecipe: blender.portableRecipe,
  parityAudit: audit,
  reviewQuestion:
    "这个无地面、单 HDR 环境的共同基准，是否在 Blender 与 Unity 中都准确呈现亮银、血红晶体和黑色纹样？",
  interactiveReviewArtifactId: `${modelId}-lighting-comparison-recording-r004`,
  unityValidationScene:
    "Assets/_EDC/Candidates/MagneticSlideTileGate08R004NeutralParity/Scenes/MagneticSlideTileNeutralParityR004.unity",
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
    "Gate 08 rev 4 replaces the rejected rev 3 target and awaits visual approval. Existing revisions remain preserved.";
}
for (const claim of manifest.claims) {
  if (claim.id === "slider-gate08-r003-portability-root-cause") {
    claim.state = "superseded-by-gate08-r004";
  }
}
manifest.claims.push({
  id: "slider-gate08-r004-neutral-parity",
  stageId: "08-lighting",
  topic: "cross-engine-neutral-lighting-parity",
  statement:
    "The reviewable portable baseline uses one HDR environment, no direct light, no ground and one post-render display transform. Unity must import the EXR as RGBAHalf and map Blender environment axes explicitly.",
  confidence: "verified",
  state: "active",
  assertedBy: "measurement",
  sourceAssetIds: records
    .filter((record) =>
      ["full-frame-parity-report", "neutral-parity-review-board", "lighting-recipe"].includes(record.slot))
    .map((record) => record.id),
  sourceRegions: [],
  decisionState: "awaiting-renewed-gate08-visual-review",
  deliveryState: "not-shipping-not-device",
});
manifest.issues = (manifest.issues || []).filter(
  (issue) => !issue.id?.startsWith("slider-gate08-r003"));
manifest.issues.push({
  id: "slider-gate08-r004-renewed-review",
  stageId: "08-lighting",
  assetId: `${modelId}-lighting-board-r004`,
  severity: "blocker",
  note: "Gate 08 rev 4 is reviewable but not approved. Gate 09-12 remain stale.",
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
  "gate08-rev4-neutral-parity-review-pending-not-pushed";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.blenderModelingStatus =
  "gate08-rev4-neutral-parity-ready-for-review";
manifest.currentState.diagnosis =
  "Gate 08 rev 3 was too dark and is superseded history. Rev 4 fixes Unity HDR clipping and equirectangular orientation, then isolates one shared HDR reflection source on a flat background with no direct light or ground. Gate 08 awaits visual review; Gates 09-12 remain stale.";
manifest.currentStageId = "08-lighting";

const userDecisionExact =
  "Continue correcting Gate 08 portability; the current rev 3 is informative but not visually acceptable and must not be presented for approval. Preserve rev 3. Do not advance Gate 09/11/12.";
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate08-neutral-parity-revision",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "08-lighting",
  revision: 4,
  status: "ready_for_review",
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  userDecisionExact,
  metrics: audit.diagnostics["full-model"].fullFrame,
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
