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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-004";
const unityRoot =
  "unity/FidgetingApp/Assets/ModelPipeline/MagneticSlideTile/Gate11Rev004";
const candidateRoot = "unity/FidgetingApp/Assets/_EDC/CandidateRev2";
const manifest = loadManifest(modelId);
const stage = manifest.stages[10];
const shipping = manifest.stages[11];
const rejection =
  "Gate 11 rev 3 整体视觉仍未对齐：图案位置保留；Unity 正面过粉过亮、银色像灰白塑料、晶体缺少深度与克制虹彩、黑色外圈过厚且死黑。";
if (
  manifest.revision !== 102
  || stage.revision !== 7
  || stage.status !== "rejected"
  || stage.decision?.notes !== rejection
  || shipping.status !== "blocked"
) {
  throw new Error("Expected exact rejected Gate 11 rev 3 state at revision 102.");
}

const unityReport = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/unity-parity-rev4-report.json`)));
const review = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/parity-review-validation-rev4.json`)));
const masks = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/artwork-mask-preparation.json`)));
const tests = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/test-results-summary.json`)));
if (!unityReport.pass || !review.checks.pass || !masks.pass || !tests.pass) {
  throw new Error("Gate 11 rev 4 evidence is incomplete.");
}

const sourceAssetIds = [
  "magnetic-slide-tile-export-fbx-r002",
  "magnetic-slide-tile-material-board-r007",
  "magnetic-slide-tile-artwork-upper-mask-r007",
  "magnetic-slide-tile-artwork-lower-mask-r007",
  "magnetic-slide-tile-unity-parity-rev3-blender-target-r003",
  "magnetic-slide-tile-unity-parity-rev3-blender-clay-r003",
];
const definitions = [
  ["registrar", "registration-source", `${evidenceRoot}/register_unity_parity_rev4.mjs`, "process"],
  ["mask-preparer", "artwork-source", `${evidenceRoot}/prepare_artwork_masks.py`, "process"],
  ["upper-mask", "artwork-mask", `${evidenceRoot}/artwork-upper-channel-pack-r004.png`, "source-model"],
  ["lower-mask", "artwork-mask", `${evidenceRoot}/artwork-lower-channel-pack-r004.png`, "source-model"],
  ["upper-border", "artwork-mask", `${evidenceRoot}/artwork-upper-border-r004.png`, "source-model"],
  ["lower-border", "artwork-mask", `${evidenceRoot}/artwork-lower-border-r004.png`, "source-model"],
  ["mask-report", "validation-report", `${evidenceRoot}/artwork-mask-preparation.json`, "validation"],
  ["unity-builder", "unity-builder-source", "unity/FidgetingApp/Assets/Editor/MagneticSlideTileUnityParityCaptureRev4.cs", "process"],
  ["editmode-test", "test-source", "unity/FidgetingApp/Assets/Tests/Editor/MagneticSlideTileParityRev4Tests.cs", "validation"],
  ["playmode-test", "test-source", "unity/FidgetingApp/Assets/Tests/PlayMode/MagneticSlideTileParityRev4PlayModeTests.cs", "validation"],
  ["playmode-asmdef", "test-config", "unity/FidgetingApp/Assets/Tests/PlayMode/FidgetingApp.Gate11Rev4.PlayModeTests.asmdef", "validation"],
  ["crystal-shader", "shader-source", `${candidateRoot}/Shaders/MagneticCrystalShippingR3.shader`, "source-model"],
  ["silver-shader", "shader-source", `${candidateRoot}/Shaders/MagneticSilverShippingR3.shader`, "source-model"],
  ["unity-scene", "unity-scene", `${unityRoot}/MagneticSlideTileNeutralParityRev4.unity`, "source-model"],
  ["unity-environment", "unity-environment", `${unityRoot}/Materials/Gate11R4_NeutralLayeredReflection.cubemap`, "source-model"],
  ["color-profile", "unity-color-profile", `${unityRoot}/Materials/Gate11R4_ColorManagement.asset`, "source-model"],
  ["silver-material", "unity-material", `${unityRoot}/Materials/M_Gate11R4_PolishedSilver.mat`, "source-model"],
  ["upper-material", "unity-material", `${unityRoot}/Materials/M_Gate11R4_BloodRedCrystalUpper.mat`, "source-model"],
  ["lower-material", "unity-material", `${unityRoot}/Materials/M_Gate11R4_BloodRedCrystalLower.mat`, "source-model"],
  ["clay-material", "unity-material", `${unityRoot}/Materials/M_Gate11R4_Clay.mat`, "source-model"],
  ["artwork-upper-material", "unity-material", `${unityRoot}/Materials/M_Gate11R4_ArtworkUpper.mat`, "source-model"],
  ["artwork-lower-material", "unity-material", `${unityRoot}/Materials/M_Gate11R4_ArtworkLower.mat`, "source-model"],
  ["imported-upper-mask", "unity-texture", `${unityRoot}/Imported/artwork-upper-channel-pack-r004.png`, "source-model"],
  ["imported-lower-mask", "unity-texture", `${unityRoot}/Imported/artwork-lower-channel-pack-r004.png`, "source-model"],
  ["unity-report", "parity-report", `${evidenceRoot}/unity-parity-rev4-report.json`, "validation"],
  ["unity-final", "unity-neutral", `${evidenceRoot}/unity-final-object.png`, "unity-render"],
  ["unity-clay", "parity-overlay", `${evidenceRoot}/unity-geometry-clay.png`, "unity-render"],
  ["unity-artwork", "parity-overlay", `${evidenceRoot}/unity-artwork-placement.png`, "unity-render"],
  ["unity-material", "unity-neutral", `${evidenceRoot}/unity-material-reflection.png`, "unity-render"],
  ["unity-angle", "material-angle-diagnostic", `${evidenceRoot}/unity-crystal-angle-diagnostic.png`, "unity-render"],
  ["review-builder", "review-builder-source", `${evidenceRoot}/build_parity_review_rev4.py`, "process"],
  ["review-validation", "validation-report", `${evidenceRoot}/parity-review-validation-rev4.json`, "validation"],
  ["test-summary", "test-results", `${evidenceRoot}/test-results-summary.json`, "validation"],
  ["geometry-board", "geometry-comparison", `${evidenceRoot}/gate11-rev4-geometry-board.png`, "unity-render"],
  ["artwork-board", "artwork-comparison", `${evidenceRoot}/gate11-rev4-artwork-board.png`, "unity-render"],
  ["material-board", "material-parity-comparison", `${evidenceRoot}/gate11-rev4-material-board.png`, "unity-render"],
  ["final-board", "parity-review-board", `${evidenceRoot}/gate11-rev4-final-board.png`, "unity-render"],
  ["heatmap", "difference-heatmap", `${evidenceRoot}/gate11-rev4-difference-heatmap.png`, "validation"],
  ["review-board", "contact-sheet", `${evidenceRoot}/gate11-rev4-review.png`, "unity-render"],
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-unity-parity-rev4-${suffix}-r004`,
    stageId: "11-unity-parity",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: path.includes("/Assets/")
        ? "Unity 6000.5.6f1 URP 17.5"
        : "Python/Node.js parity workflow",
      version: "Unity 6000.5.6f1 / URP 17.5 / Python 3 / Node.js",
      recipe: path.includes("/Assets/")
        ? "unity/FidgetingApp/Assets/Editor/MagneticSlideTileUnityParityCaptureRev4.cs"
        : `${evidenceRoot}/build_parity_review_rev4.py`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate11Revision: 4,
      note: "Gate 11 rev 4 preserves geometry, UVs and accepted motif placement while replacing rev 3 material response. Gate 12 remains blocked.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
manifest.claims.push(
  {
    id: "slider-gate11-rev3-user-rejection-r004",
    stageId: "11-unity-parity",
    topic: "user-rejection",
    statement: rejection,
    confidence: "user-authoritative",
    state: "active",
    assertedBy: "user",
    sourceAssetIds: [
      "magnetic-slide-tile-unity-parity-rev3-review-board-r003",
      "magnetic-slide-tile-unity-parity-rev3-material-comparison-r003",
    ],
    sourceRegions: [],
    decisionState: "gate11-rev3-rejected",
    deliveryState: "gate12-blocked-old-shipping-default",
  },
  {
    id: "slider-gate11-material-root-fix-r004",
    stageId: "11-unity-parity",
    topic: "material-parity-root-fix",
    statement: "Rev 4 removes the white-plastic silver lift, uses a conductor-only layered neutral reflection response, adds opaque mobile clearcoat/Fresnel/refraction-cue crystal depth with restrained thin-film color, narrows the border from 64 px to 42 px without moving its outer edge, and keeps zero emission.",
    confidence: "verified",
    state: "active",
    assertedBy: "measurement",
    sourceAssetIds: records
      .filter((record) => ["shader-source", "unity-neutral", "validation-report"].includes(record.slot))
      .map((record) => record.id),
    sourceRegions: [],
    decisionState: "ready-for-user-review",
    deliveryState: "isolated-gate11-rev4-not-integrated",
  },
  {
    id: "slider-gate11-artwork-placement-held-r004",
    stageId: "11-unity-parity",
    topic: "artwork-placement",
    statement: "The accepted motif R channel, mesh UVs, artwork transforms and face count are unchanged. Only the editable inner perimeter width changed; its outer boundary remains fixed.",
    confidence: "verified",
    state: "active",
    assertedBy: "measurement",
    sourceAssetIds: [
      `${modelId}-unity-parity-rev4-mask-report-r004`,
      `${modelId}-unity-parity-rev4-unity-report-r004`,
    ],
    sourceRegions: [],
    decisionState: "accepted-placement-preserved",
    deliveryState: "isolated-gate11-rev4-not-integrated",
  },
);

const checks = review.checks;
stage.revision += 1;
stage.status = "ready_for_review";
stage.decision = null;
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  `${modelId}-unity-parity-rev4-geometry-board-r004`,
  `${modelId}-unity-parity-rev4-artwork-board-r004`,
  `${modelId}-unity-parity-rev4-material-board-r004`,
  `${modelId}-unity-parity-rev4-final-board-r004`,
];
stage.validations = [
  {
    id: "rev3-rejection-preserved",
    status: "pass",
    evidence: rejection,
  },
  {
    id: "geometry-uv-face-count-unchanged",
    status: "pass",
    evidence: `4,096 triangles, 4,124 vertices, mesh ${unityReport.meshDigest}, UV ${unityReport.uvDigest}; clay silhouette IoU ${(checks.geometrySilhouetteIou * 100).toFixed(2)}%.`,
  },
  {
    id: "artwork-placement-preserved-border-adjusted",
    status: "pass",
    evidence: "Motif R channel is byte-identical; independent masks remain; outer edge is fixed; editable inner border width changed from 64 px to 42 px.",
  },
  {
    id: "mobile-shader-material-validation",
    status: "pass",
    evidence: "URP target 3.0 crystal and silver shaders compiled; PlayMode rendered both without fallback; zero emission; iPhone masks use ASTC 6×6.",
  },
  {
    id: "blood-red-and-crystal-response",
    status: "pass",
    evidence: `Blender median RGB ${checks.bloodRed.blenderMedianRgb.join("/")}; Unity ${checks.bloodRed.unityMedianRgb.join("/")}; DeltaE76 ${checks.bloodRed.deltaE76}; 7° view response DeltaE76 ${checks.crystalViewResponse.deltaE76}.`,
  },
  {
    id: "silver-conductor-reflection",
    status: "pass",
    evidence: `Metallic 1.0, roughness 0.03, reflection-only diffuse lift 0.015; continuous gradient ratio ${checks.silver.gradientRatio}; max environment neighbor delta ${unityReport.maxEnvironmentNeighborDelta.toFixed(4)}.`,
  },
  {
    id: "camera-color-management-identity",
    status: "pass",
    evidence: `Camera position/FOV unchanged; Neutral tone mapping is calibrated to the Blender AgX target; post exposure ${unityReport.postExposure} EV.`,
  },
  {
    id: "perceptual-and-clipping-checks",
    status: "pass",
    evidence: `Object SSIM ${checks.objectSsim}; silhouette IoU ${(checks.materialSilhouetteIou * 100).toFixed(2)}%; zero clipped object pixels; separate geometry, artwork, material and final boards plus heatmap generated.`,
  },
  {
    id: "unity-editmode-playmode-rev4",
    status: "pass",
    evidence: "Focused EditMode 4/4 and PlayMode 1/1 passed.",
  },
  {
    id: "shipping-scene-and-gate12-blocked",
    status: "pass",
    evidence: "MeshyEDC.unity hash unchanged. Old shipping model stays default. Gate 12 remains blocked; no build, install or phone push.",
  },
];
stage.unityParitySpec = {
  revision: 4,
  rejectedRevision: {
    revision: 3,
    notes: rejection,
  },
  geometry: {
    source: "unchanged Gate 10 rev 3 FBX",
    triangles: unityReport.triangles,
    vertices: unityReport.vertices,
    boundsMeters: unityReport.boundsMeters,
    meshDigest: unityReport.meshDigest,
    uvDigest: unityReport.uvDigest,
    silhouetteIoU: checks.geometrySilhouetteIou,
  },
  artwork: {
    placementPreviouslyAccepted: true,
    motifRChannelByteIdentical: checks.motifRChannelByteIdentical,
    upperLowerMasksIndependent: unityReport.upperLowerMasksIndependent,
    borderWidthPixels: checks.borderWidthPixels,
    outerBoundaryInsetPixels: 0,
  },
  material: {
    crystalShader: unityReport.crystalShader,
    silverShader: unityReport.silverShader,
    silver: {
      baseColor: unityReport.silverBaseColor,
      metallic: unityReport.silverMetallic,
      roughness: unityReport.silverRoughness,
      reflectionStrength: unityReport.silverReflectionStrength,
      diffuseLift: 0.015,
    },
    crystal: {
      color: unityReport.crystalColor,
      roughness: unityReport.crystalRoughness,
      clearCoat: unityReport.crystalClearCoat,
      clearCoatRoughness: unityReport.crystalClearCoatRoughness,
      iridescence: unityReport.crystalIridescence,
      refractionCue: unityReport.crystalRefractionCue,
      depthVariation: 0.26,
    },
    bloodRed: checks.bloodRed,
    silverMetrics: checks.silver,
    crystalViewResponse: checks.crystalViewResponse,
    zeroEmission: unityReport.noEmission,
  },
  camera: {
    position: unityReport.cameraPosition,
    rotation: unityReport.cameraRotation,
    verticalFovDegrees: unityReport.cameraVerticalFov,
    toneMapping: unityReport.toneMapping,
    postExposure: unityReport.postExposure,
  },
  perceptual: {
    objectSsim: checks.objectSsim,
    objectMedianDeltaE76: checks.objectMedianDeltaE76,
    silhouetteIoU: checks.materialSilhouetteIou,
    clippedObjectPixels: checks.clippedObjectPixels,
  },
  reviewQuestion: "修正后的 Unity 物体现在是否像同机位的 Blender 目标？",
  deliveryState: {
    isolatedParityScene: true,
    shippingSceneModified: false,
    runtimeIntegrated: false,
    gate12Status: "blocked-until-rev4-approval",
    oldShippingModelDefault: true,
    buildInstallPhonePush: "not-started",
    deviceAcceptance: "pending",
  },
};
delete stage.staleReason;
shipping.status = "blocked";
shipping.staleReason = "Gate 11 rev 4 full Blender–Unity parity is awaiting user visual approval.";

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
  "gate11-unity-parity-rev4-full-object-pending";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis =
  "Gate 11 rev 3 is rejected. Rev 4 holds geometry, UVs, face count and accepted artwork placement constant, then replaces the pink/flat response with deeper blood red crystal, layered neutral conductor reflection, restrained view-dependent thin-film color and a narrower reflective perimeter. Gate 12 stays blocked; the old shipping model remains default; no build, install or phone push.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  revision: 4,
  rejectedRevision: 3,
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  gate12Status: shipping.status,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate11: saved.stages[10].status,
  gate11StageRevision: saved.stages[10].revision,
  gate12: saved.stages[11].status,
  reviewArtifactIds: saved.stages[10].reviewArtifactIds,
}, null, 2));
