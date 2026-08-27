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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-002";
const unityRoot =
  "unity/FidgetingApp/Assets/ModelPipeline/MagneticSlideTile/Gate11Rev002";
const reusedRoot =
  "unity/FidgetingApp/Assets/ModelPipeline/MagneticSlideTile/Gate11Rev001";
const manifest = loadManifest(modelId);
const stage = manifest.stages[10];
const exactDecision =
  "pattern placement accepted; geometry/round-edge parity rejected.";
if (manifest.revision !== 90
  || stage.status !== "rejected"
  || stage.revision !== 2
  || stage.decision?.notes !== exactDecision) {
  throw new Error("Expected exact partial Gate 11 rev 1 rejection at revision 90.");
}
const blender = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/blender-neutral-report.json`)));
const unity = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/unity-import-parity-report.json`)));
const validation = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/unity-round-edge-validation.json`)));
const parity = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/parity-report.json`)));
const editMode = fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/editmode-results.xml`),
  "utf8");
if (!blender.pass
  || !unity.pass
  || !validation.pass
  || !parity.pass
  || !editMode.includes('testcasecount="5" result="Passed"')
  || !editMode.includes('passed="5" failed="0"')) {
  throw new Error("Gate 11 rev 2 evidence is incomplete.");
}

const sources = [
  "magnetic-slide-tile-export-fbx-r002",
  "magnetic-slide-tile-export-collision-fbx-r002",
  "magnetic-slide-tile-export-texture-manifest-r002",
  "magnetic-slide-tile-export-artwork-upper-pack-r002",
  "magnetic-slide-tile-export-artwork-lower-pack-r002",
];
const definitions = [
  ["unity-parity-rev2-registrar", "registration-source", `${evidenceRoot}/register_unity_parity_rev2.mjs`, "process"],
  ["unity-parity-rev2-camera", "camera-recipe", `${evidenceRoot}/neutral-camera-recipe.json`, "validation"],
  ["unity-parity-rev2-blender-source", "parity-source", `${evidenceRoot}/render_blender_neutral_rev2.py`, "process"],
  ["unity-parity-rev2-blender-report", "parity-measurement", `${evidenceRoot}/blender-neutral-report.json`, "validation"],
  ["unity-parity-rev2-blender-neutral", "blender-neutral", `${evidenceRoot}/blender-neutral.png`, "blender-render"],
  ["unity-parity-rev2-blender-silhouette", "parity-overlay", `${evidenceRoot}/blender-neutral-silhouette.png`, "blender-render"],
  ["unity-parity-rev2-unity-source", "parity-source", "unity/FidgetingApp/Assets/Editor/MagneticSlideTileUnityParityCaptureRev2.cs", "process"],
  ["unity-parity-rev2-test-source", "test-source", "unity/FidgetingApp/Assets/Tests/Editor/MagneticSlideTileParityRev2Tests.cs", "process"],
  ["unity-parity-rev2-scene", "unity-scene", `${unityRoot}/MagneticSlideTileNeutralParityRev2.unity`, "process"],
  ["unity-parity-rev2-environment", "unity-environment", `${unityRoot}/Materials/Gate11R2_DirectionContinuousEnvironment.cubemap`, "process"],
  ["unity-parity-rev2-silver-material", "unity-material", `${unityRoot}/Materials/M_Gate11R2_PolishedSilver.mat`, "process"],
  ["unity-parity-rev2-upper-material", "unity-material", `${unityRoot}/Materials/M_Gate11R2_BloodRedUpper.mat`, "process"],
  ["unity-parity-rev2-lower-material", "unity-material", `${unityRoot}/Materials/M_Gate11R2_BloodRedLower.mat`, "process"],
  ["unity-parity-rev2-wire-material", "unity-material", `${unityRoot}/Materials/M_Gate11R2_Wireframe.mat`, "process"],
  ["unity-parity-rev2-reused-fbx", "unity-imported-model", `${reusedRoot}/Imported/magnetic-slide-tile-r002.fbx`, "process"],
  ["unity-parity-rev2-reused-collision", "unity-imported-collision", `${reusedRoot}/Imported/magnetic-slide-tile-collision-r002.fbx`, "process"],
  ["unity-parity-rev2-upper-basecolor", "unity-texture", `${reusedRoot}/Imported/face-upper-transport-basecolor.png`, "process"],
  ["unity-parity-rev2-lower-basecolor", "unity-texture", `${reusedRoot}/Imported/face-lower-transport-basecolor.png`, "process"],
  ["unity-parity-rev2-unity-report", "parity-measurement", `${evidenceRoot}/unity-import-parity-report.json`, "validation"],
  ["unity-parity-rev2-unity-neutral", "unity-neutral", `${evidenceRoot}/unity-neutral.png`, "unity-render"],
  ["unity-parity-rev2-unity-silver", "parity-overlay", `${evidenceRoot}/unity-neutral-all-silver.png`, "unity-render"],
  ["unity-parity-rev2-unity-wireframe", "parity-overlay", `${evidenceRoot}/unity-wireframe.png`, "unity-render"],
  ["unity-parity-rev2-review-source", "parity-source", `${evidenceRoot}/build_round_edge_review.py`, "process"],
  ["unity-parity-rev2-validation", "validation-report", `${evidenceRoot}/unity-round-edge-validation.json`, "validation"],
  ["unity-parity-rev2-parity-report", "parity-report", `${evidenceRoot}/parity-report.json`, "validation"],
  ["unity-parity-rev2-location", "round-edge-location", `${evidenceRoot}/unity-round-edge-location.png`, "unity-render"],
  ["unity-parity-rev2-before-after", "round-edge-comparison", `${evidenceRoot}/unity-round-edge-before-after.png`, "unity-render"],
  ["unity-parity-rev2-wire-proof", "round-edge-wireframe", `${evidenceRoot}/unity-round-edge-wireframe-proof.png`, "unity-render"],
  ["unity-parity-rev2-import-log", "validation-report", `${evidenceRoot}/unity-import.log`, "validation"],
  ["unity-parity-rev2-editmode-results", "test-report", `${evidenceRoot}/editmode-results.xml`, "validation"],
  ["unity-parity-rev2-editmode-log", "validation-report", `${evidenceRoot}/editmode-tests.log`, "validation"],
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-${suffix}-r002`,
    stageId: "11-unity-parity",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: path.includes("Assets/") || path.includes("unity-")
        ? "Unity 6000.5.6f1 URP 17.5"
        : "Blender/Python/Node.js",
      version: "Unity 6000.5.6f1 / Blender 5.2.0 LTS / Python 3 / Node.js",
      recipe: path.includes("Assets/")
        ? "unity/FidgetingApp/Assets/Editor/MagneticSlideTileUnityParityCaptureRev2.cs"
        : `${evidenceRoot}/build_round_edge_review.py`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate11Revision: 2,
      note: "Corrected isolated Gate 11 round-edge evidence. Rev 1 remains immutable.",
    },
    sourceAssetIds: sources,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
manifest.claims.push(
  {
    id: "slider-gate11-partial-decision-r002",
    stageId: "11-unity-parity",
    topic: "partial-user-decision",
    statement: exactDecision,
    confidence: "high",
    state: "active",
    assertedBy: "user",
    sourceAssetIds: ["magnetic-slide-tile-export-fbx-r002"],
    sourceRegions: [],
    sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
    decisionState: "pattern-position-provisionally-accepted-round-edge-rejected",
    deliveryState: "gate11-rev2-review-pending",
  },
  {
    id: "slider-gate11-reflection-root-cause-r002",
    stageId: "11-unity-parity",
    topic: "reflection-band-root-cause",
    statement: "Gate 11 rev 1 的低面数观感来自六个互不连续的 32×32 纯色反射面且无 mipmaps；近镜面银色把方向边界显示为固定宽带。rev 2 保持 4,096 triangles 和 importer normals 不变，改为 256×256 RGBAHalf 方向连续环境、9 级 mip、trilinear，并关闭 box projection。固定亮带评分从 72.0634 降至 7.61893。",
    confidence: "high",
    state: "active",
    assertedBy: "measurement",
    sourceAssetIds: ["magnetic-slide-tile-export-fbx-r002"],
    sourceRegions: [],
    sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
    decisionState: "verified",
    deliveryState: "isolated-gate11-rev2-only",
  },
);

stage.revision += 1;
stage.status = "ready_for_review";
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  "magnetic-slide-tile-unity-parity-rev2-location-r002",
  "magnetic-slide-tile-unity-parity-rev2-before-after-r002",
  "magnetic-slide-tile-unity-parity-rev2-wire-proof-r002",
];
stage.validations = [
  { id: "gate11-rev1-partial-decision", status: "pass", evidence: `Exact decision preserved: ${exactDecision}` },
  { id: "reflection-root-cause", status: "pass", evidence: "Old six-face solid 32×32/no-mip environment produced broad direction bands; geometry and importer normals remained unchanged." },
  { id: "continuous-environment", status: "pass", evidence: "256×256 RGBAHalf direction-continuous environment, 9 mips, trilinear filtering, analytic seam delta 1.42455e-5." },
  { id: "box-projection-disabled", status: "pass", evidence: "Centered small-object probe uses custom static reflection with boxProjection=false." },
  { id: "geometry-unchanged", status: "pass", evidence: "Bounds relative error 4.65661e-7; two meshes; 4,096 triangles; no render geometry inflation." },
  { id: "arc-normal-progression", status: "pass", evidence: "Adjacent side-normal median 0.703043°, p95 0.703600°, max 0.877819°; expected 256-segment step 0.703125°." },
  { id: "hard-cap-side-boundary", status: "pass", evidence: "2,076 coincident cap/side pairs; minimum angle 90°." },
  { id: "highlight-continuity", status: "pass", evidence: "Smooth-gradient coverage 3.0641%→8.9136%; fixed-band score 72.0634→7.61893." },
  { id: "wireframe-density", status: "pass", evidence: "Real Unity wireframe contains 124,454 cyan evidence pixels and preserves 256 segments per semicircle." },
  { id: "blender-unity-silhouette", status: "pass", evidence: "Silhouette IoU 0.986902; bbox IoU 0.991814; contour P95 4.10788 px." },
  { id: "unity-editmode-rev2", status: "pass", evidence: "Focused EditMode suite: 5 passed, 0 failed." },
  { id: "shipping-scene-unchanged", status: "pass", evidence: "MeshyEDC.unity SHA-256 remains 99083a32...850d." },
  { id: "gate11-only", status: "pass", evidence: "No Gate 12, shipping integration, runtime, Haptic, build, install, or phone push." },
];
stage.unityParitySpec = {
  revision: 2,
  partialDecision: parity.partialDecision,
  rootCause: validation.rootCause,
  geometry: {
    boundsMeters: unity.boundsMeters,
    boundsRelativeError: unity.boundsRelativeError,
    renderMeshes: unity.renderMeshes,
    vertices: unity.vertices,
    triangles: unity.triangles,
    collisionTriangles: unity.collisionTriangles,
    changed: unity.geometryChanged,
    inflated: unity.renderGeometryInflated,
  },
  arcNormals: unity.arcNormals,
  capSideBoundary: unity.capSideBoundary,
  environment: unity.environment,
  highlightContinuity: {
    old: validation.old,
    corrected: validation.new,
  },
  visual: validation.visual,
  importerNormalsChanged: unity.importerNormalsChanged,
  camera: unity.camera,
  patternPlacement: "accepted-provisionally-not-under-review",
  reviewQuestion: "修正后的 Unity 圆边现在看起来是否连续？",
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
manifest.currentState.visualApproval = "gate11-unity-parity-rev2-round-edge-pending-pattern-position-accepted";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis = "Gate 11 rev 1 已按用户精确部分决定保留：pattern placement accepted; geometry/round-edge parity rejected. 根因验证为 rev 1 六个独立纯色、无 mip 反射面在近镜银色上形成固定宽带，并非 4,096-triangle geometry 或 imported normals 退化。rev 2 保持 bounds/triangles/importer normals 不变，改用 256×256 RGBAHalf 方向连续环境、9 mips、trilinear、box projection off。相邻圆弧 normal 中位 0.703043°，与 256 段预期 0.703125°一致；固定亮带评分 72.0634→7.61893。Gate 11 rev 2 等待圆边视觉确认。Gate 12、shipping、runtime、Haptic、build/install/phone 均未开始。视觉批准待确认，未推送手机。";
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  revision: 2,
  partialDecision: exactDecision,
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
});
console.log(JSON.stringify({
  revision: saved.revision,
  status: saved.stages[10].status,
  stageRevision: saved.stages[10].revision,
  artifactIds: saved.stages[10].artifactIds.length,
  reviewArtifactIds: saved.stages[10].reviewArtifactIds,
}, null, 2));
