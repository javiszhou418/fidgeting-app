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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-001";
const unityRoot =
  "unity/FidgetingApp/Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001";
const manifest = loadManifest(modelId);
const gate10 = manifest.stages[9];
const stage = manifest.stages[10];
if (manifest.revision !== 87
  || gate10.status !== "approved"
  || gate10.decision?.notes !== "继续吧"
  || !["blocked", "missing", "draft"].includes(stage.status)) {
  throw new Error("Expected exact Gate 10 approval at manifest revision 87.");
}
const blender = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/blender-neutral-report.json`)));
const unity = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/unity-import-parity-report.json`)));
const parity = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/parity-report.json`)));
const editMode = fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/editmode-results.xml`),
  "utf8");
if (!blender.pass
  || !unity.pass
  || !parity.pass
  || !editMode.includes('testcasecount="6" result="Passed"')
  || !editMode.includes('passed="6" failed="0"')) {
  throw new Error("Gate 11 validation evidence is incomplete.");
}

const gate10Sources = [
  "magnetic-slide-tile-export-fbx-r002",
  "magnetic-slide-tile-export-collision-fbx-r002",
  "magnetic-slide-tile-export-texture-manifest-r002",
  "magnetic-slide-tile-export-artwork-upper-pack-r002",
  "magnetic-slide-tile-export-artwork-lower-pack-r002",
];
const definitions = [
  ["unity-parity-registrar", "registration-source", `${evidenceRoot}/register_unity_parity_review.mjs`, "process"],
  ["unity-parity-camera", "camera-recipe", `${evidenceRoot}/neutral-camera-recipe.json`, "validation"],
  ["unity-parity-blender-source", "parity-source", `${evidenceRoot}/render_blender_neutral.py`, "process"],
  ["unity-parity-blender-report", "parity-measurement", `${evidenceRoot}/blender-neutral-report.json`, "validation"],
  ["unity-parity-blender-neutral", "blender-neutral", `${evidenceRoot}/blender-neutral.png`, "blender-render"],
  ["unity-parity-blender-silhouette", "parity-overlay", `${evidenceRoot}/blender-neutral-silhouette.png`, "blender-render"],
  ["unity-parity-unity-source", "parity-source", "unity/FidgetingApp/Assets/Editor/MagneticSlideTileUnityParityCapture.cs", "process"],
  ["unity-parity-test-source", "test-source", "unity/FidgetingApp/Assets/Tests/Editor/MagneticSlideTileParityTests.cs", "process"],
  ["unity-parity-metadata-source", "unity-metadata", `${unityRoot}/MagneticSlideTileParityMetadata.cs`, "process"],
  ["unity-parity-unity-report", "parity-measurement", `${evidenceRoot}/unity-import-parity-report.json`, "validation"],
  ["unity-parity-unity-neutral", "unity-neutral", `${evidenceRoot}/unity-neutral.png`, "unity-render"],
  ["unity-parity-unity-silhouette", "parity-overlay", `${evidenceRoot}/unity-neutral-all-silver-diagnostic.png`, "unity-render"],
  ["unity-parity-compare-source", "parity-source", `${evidenceRoot}/validate_gate11_parity.py`, "process"],
  ["unity-parity-overlay", "parity-overlay", `${evidenceRoot}/silhouette-overlay.png`, "process"],
  ["unity-parity-report", "parity-report", `${evidenceRoot}/parity-report.json`, "validation"],
  ["unity-parity-review-board", "contact-sheet", `${evidenceRoot}/gate11-parity-board.png`, "process"],
  ["unity-parity-import-log", "validation-report", `${evidenceRoot}/unity-import.log`, "validation"],
  ["unity-parity-editmode-results", "test-report", `${evidenceRoot}/editmode-results.xml`, "validation"],
  ["unity-parity-editmode-log", "validation-report", `${evidenceRoot}/editmode-tests.log`, "validation"],
  ["unity-parity-isolated-scene", "unity-scene", `${unityRoot}/MagneticSlideTileNeutralParity.unity`, "process"],
  ["unity-parity-isolated-fbx", "unity-imported-model", `${unityRoot}/Imported/magnetic-slide-tile-r002.fbx`, "process"],
  ["unity-parity-isolated-collision", "unity-imported-collision", `${unityRoot}/Imported/magnetic-slide-tile-collision-r002.fbx`, "process"],
  ["unity-parity-upper-pack", "unity-texture", `${unityRoot}/Imported/artwork-upper-channel-pack.png`, "process"],
  ["unity-parity-lower-pack", "unity-texture", `${unityRoot}/Imported/artwork-lower-channel-pack.png`, "process"],
  ["unity-parity-upper-mask", "unity-texture-source", `${unityRoot}/Imported/artwork-upper-mask.png`, "process"],
  ["unity-parity-lower-mask", "unity-texture-source", `${unityRoot}/Imported/artwork-lower-mask.png`, "process"],
  ["unity-parity-border-mask", "unity-texture-source", `${unityRoot}/Imported/artwork-top-perimeter-border-mask.png`, "process"],
  ["unity-parity-upper-basecolor", "unity-texture", `${unityRoot}/Imported/face-upper-transport-basecolor.png`, "process"],
  ["unity-parity-lower-basecolor", "unity-texture", `${unityRoot}/Imported/face-lower-transport-basecolor.png`, "process"],
  ["unity-parity-silver-material", "unity-material", `${unityRoot}/Materials/M_Gate11_PolishedSilver.mat`, "process"],
  ["unity-parity-upper-material", "unity-material", `${unityRoot}/Materials/M_Gate11_BloodRedUpper.mat`, "process"],
  ["unity-parity-lower-material", "unity-material", `${unityRoot}/Materials/M_Gate11_BloodRedLower.mat`, "process"],
  ["unity-parity-reflection-cubemap", "unity-environment", `${unityRoot}/Materials/Gate11_NeutralReflection.cubemap`, "process"],
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-${suffix}-r001`,
    stageId: "11-unity-parity",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: path.endsWith(".png")
        ? path.includes("unity-") ? "Unity 6000.5.6f1 URP 17.5" : "Blender/Pillow"
        : path.endsWith(".unity") || path.includes("/Assets/")
          ? "Unity 6000.5.6f1"
          : "Python/Node.js",
      version: path.includes("Unity") || path.includes("/Assets/")
        ? "Unity 6000.5.6f1"
        : "Blender 5.2.0 LTS / Python 3 / Node.js",
      recipe: path.includes("/Assets/")
        ? "unity/FidgetingApp/Assets/Editor/MagneticSlideTileUnityParityCapture.cs"
        : `${evidenceRoot}/validate_gate11_parity.py`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      gate10ExportRevision: 2,
      gate10ReviewRevision: 3,
      gate11Revision: 1,
      note: "Isolated Gate 11 parity evidence. Shipping scene/model remain unchanged.",
    },
    sourceAssetIds: gate10Sources,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
manifest.claims.push(
  {
    id: "slider-gate11-import-parity-r001",
    stageId: "11-unity-parity",
    topic: "unity-import-parity",
    statement: "Unity 6000.5.6f1 / URP 17.5 隔离导入保持 0.050×0.031×0.012 m、两片 render mesh、4,096 triangles、两片各 128 triangles collision、闭合零运动、UV／normal／tangent 与两材质 slots；shipping scene hash 未变化。",
    confidence: "high",
    state: "active",
    assertedBy: "measurement",
    sourceAssetIds: ["magnetic-slide-tile-export-fbx-r002", "magnetic-slide-tile-export-collision-fbx-r002"],
    sourceRegions: [],
    sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
    decisionState: "measured",
    deliveryState: "isolated-gate11-parity-only",
  },
  {
    id: "slider-gate11-material-gap-r001",
    stageId: "11-unity-parity",
    topic: "urp-material-approximation",
    statement: "同机位 silhouette IoU 0.987161、bbox IoU 0.990887、contour P95 4.10788 px。URP 水晶仍缺 Blender thin-film／transmission；银色使用静态 cubemap/local probe；cap-only artwork overlay 只属于隔离 parity scene，不是 shipping integration。",
    confidence: "high",
    state: "active",
    assertedBy: "measurement",
    sourceAssetIds: ["magnetic-slide-tile-export-fbx-r002"],
    sourceRegions: [],
    sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
    decisionState: "measured-with-known-gaps",
    deliveryState: "gate11-review-pending-gate12-not-started",
  },
);

stage.revision = 1;
stage.status = "ready_for_review";
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = ["magnetic-slide-tile-unity-parity-review-board-r001"];
stage.validations = [
  { id: "gate10-approved-exact", status: "pass", evidence: "Workflow revision 87 records exact Gate 10 approval text “继续吧”." },
  { id: "unity-import-geometry", status: "pass", evidence: "Bounds relative error 4.65661e-7; 2 render meshes; 4,096 triangles; UV0/normals/tangents valid." },
  { id: "unity-import-smoothing", status: "pass", evidence: "Curved-side duplicate normal angle 0°; cap-side hard boundary 90°." },
  { id: "unity-import-collision", status: "pass", evidence: "Two inactive convex collision proxies remain 128 triangles each." },
  { id: "unity-import-motion", status: "pass", evidence: "Closed position/rotation are zero; no Animation/Animator. +21 mm slide, point axis and 30×12° remain specified-only metadata." },
  { id: "unity-import-textures", status: "pass", evidence: "Independent upper/lower channel packs use iPhone ASTC 4×4, max 1024, linear, alpha input, and mipmaps." },
  { id: "unity-editmode", status: "pass", evidence: "Focused EditMode suite: 6 passed, 0 failed." },
  { id: "unity-neutral-parity", status: "pass", evidence: "Same camera/FOV; silhouette IoU 0.987161; bbox IoU 0.990887; contour P95 4.10788 px." },
  { id: "shipping-scene-unchanged", status: "pass", evidence: "MeshyEDC.unity SHA-256 is unchanged before/after parity generation." },
  { id: "gate11-only", status: "pass", evidence: "Isolated scene only; no Gate 12, runtime, Haptic, app build, install, or phone push." },
];
stage.unityParitySpec = {
  revision: 1,
  unityVersion: unity.unityVersion,
  urpVersion: unity.urpVersion,
  productAssetPath: unity.productAssetPath,
  collisionAssetPath: unity.collisionAssetPath,
  parityScenePath: unity.parityScenePath,
  geometry: {
    boundsMeters: unity.sortedBoundsMeters,
    boundsRelativeError: unity.boundsRelativeError,
    renderMeshes: unity.renderMeshes,
    vertices: unity.vertices,
    triangles: unity.triangles,
    collisionTriangles: unity.collisionTriangles,
    normalMetrics: unity.normalMetrics,
  },
  motion: {
    closedPosition: [0, 0, 0],
    closedRotation: [0, 0, 0],
    pointAxisUnityMeters: [0, 0, 0.0095],
    pointAxisDirection: "+Y",
    slideDirection: "-Z",
    slideTravelMeters: 0.021,
    detents: { count: 30, stepDegrees: 12, deliveryState: "specified-only-not-runtime-integrated" },
  },
  textureImports: unity.textures,
  textureMemory: {
    editorRuntimeMeasuredBytes: unity.textures.reduce((sum, texture) => sum + texture.editorRuntimeMemoryBytes, 0),
    iosEstimatedBytes: unity.textures.reduce((sum, texture) => sum + texture.iosEstimatedTextureBytes, 0),
    deviceMemoryMeasured: false,
  },
  visual: parity.visual,
  materialGaps: parity.materialGaps,
  reflection: unity.reflection,
  artworkPreview: {
    independentPacks: unity.upperLowerArtworkIndependent,
    overlayMeshes: unity.previewArtworkOverlayMeshes,
    state: unity.previewArtworkOverlayState,
  },
  deliveryState: parity.deliveryState,
};
stage.decision = null;
delete stage.staleReason;

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
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
manifest.currentState.visualApproval = "gate11-unity-parity-rev1-pending";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis = "Gate 10 rev 3 已按用户原文“继续吧”批准。Gate 11 rev 1 在独立 Unity folder/scene 完成真实导入与同机位 parity：bounds 0.050×0.031×0.012 m、4,096 triangles、两片 128-triangle collision、smooth side 0°／hard seam 90°、独立 ASTC 4×4 artwork packs 与 6/6 EditMode tests 均通过。silhouette IoU 0.987161。URP 水晶 thin-film/transmission 与静态 cubemap reflection 仍是明确 approximation；shipping scene hash 未变。Gate 12、runtime、Haptic、build/install/phone 均未开始。视觉批准待确认，未推送手机。";
const event = {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  revision: 1,
  gate10Approval: "继续吧",
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[10].status,
  artifactIds: saved.stages[10].artifactIds.length,
  reviewArtifactIds: saved.stages[10].reviewArtifactIds,
}, null, 2));
