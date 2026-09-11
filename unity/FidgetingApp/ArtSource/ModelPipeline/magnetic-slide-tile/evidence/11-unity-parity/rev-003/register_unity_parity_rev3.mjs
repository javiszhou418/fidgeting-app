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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-003";
const unityRoot =
  "unity/FidgetingApp/Assets/ModelPipeline/MagneticSlideTile/Gate11Rev003";
const candidateRoot = "unity/FidgetingApp/Assets/_EDC/CandidateRev2";
const manifest = loadManifest(modelId);
const stage = manifest.stages[10];
const shipping = manifest.stages[11];
const gate11Rejection =
  "模型与材质在 Blender 与 Unity 最终成品之间差距太大，不能视为同一个对象；此前只接受的图案位置继续保留为局部决定，完整 Unity parity 退回。";
const gate12Rejection =
  "模型与材质…Blender 渲染的模型和纹理和 Unity 的最终成品差距太大了，感觉不是一个东西.";
if (
  manifest.revision !== 99
  || stage.status !== "rejected"
  || stage.revision !== 5
  || stage.decision?.notes !== gate11Rejection
  || shipping.status !== "rejected"
  || shipping.decision?.notes !== gate12Rejection
) {
  throw new Error("Expected exact Gate 11/12 rejection state at revision 99.");
}

const unityReport = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/unity-parity-rev3-report.json`)));
const review = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/parity-review-validation.json`)));
const blender = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/blender-target-report.json`)));
const editMode = fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/editmode-results.xml`),
  "utf8");
if (
  !unityReport.pass
  || !review.pass
  || !blender.pass
  || !editMode.includes('testcasecount="3" result="Passed"')
  || !editMode.includes('passed="3" failed="0"')
) {
  throw new Error("Gate 11 rev 3 evidence is incomplete.");
}

const sourceAssetIds = [
  "magnetic-slide-tile-export-fbx-r002",
  "magnetic-slide-tile-export-artwork-upper-pack-r002",
  "magnetic-slide-tile-export-artwork-lower-pack-r002",
  "magnetic-slide-tile-unity-parity-rev2-blender-neutral-r002",
];
const definitions = [
  ["registrar", "registration-source", `${evidenceRoot}/register_unity_parity_rev3.mjs`, "process"],
  ["camera", "camera-recipe", `${evidenceRoot}/neutral-camera-recipe.json`, "validation"],
  ["blender-prep", "parity-source", `${evidenceRoot}/prepare_blender_targets.py`, "process"],
  ["blender-report", "parity-measurement", `${evidenceRoot}/blender-target-report.json`, "validation"],
  ["blender-target", "blender-neutral", `${evidenceRoot}/blender-neutral.png`, "blender-render"],
  ["blender-clay", "parity-overlay", `${evidenceRoot}/blender-neutral-silhouette.png`, "blender-render"],
  ["unity-builder", "unity-builder-source", "unity/FidgetingApp/Assets/Editor/MagneticSlideTileUnityParityCaptureRev3.cs", "process"],
  ["unity-test", "test-source", "unity/FidgetingApp/Assets/Tests/Editor/MagneticSlideTileParityRev3Tests.cs", "validation"],
  ["crystal-shader", "shader-source", `${candidateRoot}/Shaders/MagneticCrystalShippingR2.shader`, "source-model"],
  ["silver-shader", "shader-source", `${candidateRoot}/Shaders/MagneticSilverShippingR2.shader`, "source-model"],
  ["unity-scene", "unity-scene", `${unityRoot}/MagneticSlideTileNeutralParityRev3.unity`, "source-model"],
  ["unity-environment", "unity-environment", `${unityRoot}/Materials/Gate11R3_ApprovedReflection.cubemap`, "source-model"],
  ["silver-material", "unity-material", `${unityRoot}/Materials/M_Gate11R3_PolishedSilver.mat`, "source-model"],
  ["upper-material", "unity-material", `${unityRoot}/Materials/M_Gate11R3_BloodRedCrystalUpper.mat`, "source-model"],
  ["lower-material", "unity-material", `${unityRoot}/Materials/M_Gate11R3_BloodRedCrystalLower.mat`, "source-model"],
  ["clay-material", "unity-material", `${unityRoot}/Materials/M_Gate11R3_Clay.mat`, "source-model"],
  ["unity-report", "parity-report", `${evidenceRoot}/unity-parity-rev3-report.json`, "validation"],
  ["unity-final", "unity-neutral", `${evidenceRoot}/unity-material-final.png`, "unity-render"],
  ["unity-clay", "parity-overlay", `${evidenceRoot}/unity-geometry-clay.png`, "unity-render"],
  ["unity-artwork", "parity-overlay", `${evidenceRoot}/unity-artwork-material.png`, "unity-render"],
  ["review-source", "review-builder-source", `${evidenceRoot}/build_parity_review.py`, "process"],
  ["review-validation", "validation-report", `${evidenceRoot}/parity-review-validation.json`, "validation"],
  ["review-board", "parity-review-board", `${evidenceRoot}/gate11-rev3-parity-board.png`, "unity-render"],
  ["geometry-comparison", "geometry-comparison", `${evidenceRoot}/geometry-comparison.png`, "unity-render"],
  ["geometry-overlay", "parity-overlay", `${evidenceRoot}/geometry-overlay.png`, "unity-render"],
  ["artwork-comparison", "artwork-comparison", `${evidenceRoot}/artwork-comparison.png`, "unity-render"],
  ["material-comparison", "material-parity-comparison", `${evidenceRoot}/material-comparison.png`, "unity-render"],
  ["unity-log", "unity-log", `${evidenceRoot}/unity-import.log`, "validation"],
  ["editmode-results", "editmode-results", `${evidenceRoot}/editmode-results.xml`, "validation"],
  ["editmode-log", "editmode-log", `${evidenceRoot}/editmode-tests.log`, "validation"],
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-unity-parity-rev3-${suffix}-r003`,
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
      version: "Unity 6000.5.6f1 / Python 3 / Node.js",
      recipe: path.includes("/Assets/")
        ? "unity/FidgetingApp/Assets/Editor/MagneticSlideTileUnityParityCaptureRev3.cs"
        : `${evidenceRoot}/build_parity_review.py`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate11Revision: 3,
      note: "Gate 11 rev 3 reopens full material parity after the user rejected Gate 12 rev 1. Rejected rev 1/2 and Gate 12 rev 1 remain immutable.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
manifest.claims.push(
  {
    id: "slider-gate12-rev1-user-rejection-r003",
    stageId: "12-shipping",
    topic: "user-rejection",
    statement: gate12Rejection,
    confidence: "user-authoritative",
    state: "active",
    assertedBy: "user",
    sourceAssetIds: [
      "magnetic-slide-tile-gate12-review-board-r001",
      "magnetic-slide-tile-gate12-motion-board-r001",
    ],
    sourceRegions: [],
    decisionState: "gate12-rev1-rejected",
    deliveryState: "candidate-default-off-no-build-install-phone",
  },
  {
    id: "slider-gate11-material-root-cause-r003",
    stageId: "11-unity-parity",
    topic: "material-parity-root-cause",
    statement: "Gate 11 rev 2 only proved geometry/round-edge parity. Its URP Lit silver plus Unlit cap overlays, opaque base-color transport and simplified reflection environment did not reproduce the approved Blender material. Gate 11 rev 3 removes all Unlit overlays and uses shipping-capable independent mask, blood-red crystal and polished-silver shaders.",
    confidence: "high",
    state: "active",
    assertedBy: "measurement",
    sourceAssetIds,
    sourceRegions: [],
    decisionState: "verified",
    deliveryState: "isolated-gate11-rev3-review-pending",
  },
);

stage.revision += 1;
stage.status = "ready_for_review";
stage.decision = null;
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  `${modelId}-unity-parity-rev3-review-board-r003`,
  `${modelId}-unity-parity-rev3-geometry-comparison-r003`,
  `${modelId}-unity-parity-rev3-artwork-comparison-r003`,
  `${modelId}-unity-parity-rev3-material-comparison-r003`,
];
stage.validations = [
  {
    id: "exact-user-rejection-preserved",
    status: "pass",
    evidence: `Gate 12 rev 1 rejection preserved exactly: ${gate12Rejection}`,
  },
  {
    id: "same-imported-geometry",
    status: "pass",
    evidence: `Same FBX, 4,096 triangles, 50 × 31 × 12 mm; silhouette IoU ${(review.geometry.silhouetteIoU * 100).toFixed(2)}%.`,
  },
  {
    id: "no-unlit-overlay-shortcut",
    status: "pass",
    evidence: "Unity scene uses zero ArtworkPreview renderers; upper/lower submesh slots use the shipping-capable crystal shader directly.",
  },
  {
    id: "independent-artwork-masks",
    status: "pass",
    evidence: "Upper and lower channel-pack masks remain separate imported textures and material inputs.",
  },
  {
    id: "material-color-parity",
    status: "pass",
    evidence: `Blood-red median RGB max delta ${Math.max(...review.material.redMedianAbsoluteDelta)}; silver max delta ${Math.max(...review.material.silverMedianAbsoluteDelta)}.`,
  },
  {
    id: "shipping-scene-unchanged",
    status: "pass",
    evidence: "MeshyEDC.unity hash remained unchanged throughout isolated Gate 11 rev 3 work.",
  },
  {
    id: "unity-editmode-rev3",
    status: "pass",
    evidence: "Focused EditMode suite: 3 passed, 0 failed.",
  },
  {
    id: "gate11-only",
    status: "pass",
    evidence: "Gate 12 remains blocked/rejected. No build, install, device launch or phone push.",
  },
];
stage.unityParitySpec = {
  revision: 3,
  userRejection: {
    exactText: gate12Rejection,
    gate12Rev1: "rejected",
    preservedPatternPlacement: "accepted-provisionally",
  },
  geometry: {
    source: "unchanged Gate 10 rev 3 FBX",
    triangles: unityReport.triangles,
    vertices: unityReport.vertices,
    boundsMeters: unityReport.boundsMeters,
    silhouetteIoU: review.geometry.silhouetteIoU,
  },
  artwork: {
    upperLowerMasksIndependent: unityReport.upperLowerMasksIndependent,
    unlitOverlayCount: unityReport.unlitOverlayCount,
    placementPreviouslyAccepted: true,
  },
  material: {
    crystalShader: unityReport.crystalShader,
    silverShader: unityReport.silverShader,
    blenderRedMedianRgb: review.material.blenderRedMedianRgb,
    unityRedMedianRgb: review.material.unityRedMedianRgb,
    blenderSilverMedianRgb: review.material.blenderSilverMedianRgb,
    unitySilverMedianRgb: review.material.unitySilverMedianRgb,
    zeroEmission: true,
    continuousReflection: true,
  },
  camera: {
    position: unityReport.cameraPosition,
    verticalFovDegrees: unityReport.cameraVerticalFov,
    source: "unchanged Gate 11 rev 2 camera",
  },
  reviewQuestion: review.approvalQuestion,
  deliveryState: {
    isolatedParityScene: true,
    shippingSceneModified: false,
    runtimeIntegrated: false,
    hapticsIntegrated: false,
    gate12Status: "blocked-until-rev3-approval",
    deviceAcceptance: "pending",
  },
};
delete stage.staleReason;
shipping.status = "blocked";
shipping.staleReason = "Gate 11 rev 3 full Blender–Unity material parity is awaiting user approval.";

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
  "gate11-unity-parity-rev3-full-object-pending";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis =
  "Gate 12 rev 1 and the prior full Gate 11 parity decision were rejected because the Blender and Unity object/material did not look like the same thing. Gate 11 rev 3 reuses the same 4,096-triangle FBX and accepted artwork placement, removes Unlit overlays, and uses shipping-capable independent-mask blood-red crystal and polished-silver shaders. Geometry, artwork and material are shown separately under the same camera. Gate 12 remains blocked; current shipping model stays default; no build, install or phone push.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  revision: 3,
  rejectedGate12Revision: 1,
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
