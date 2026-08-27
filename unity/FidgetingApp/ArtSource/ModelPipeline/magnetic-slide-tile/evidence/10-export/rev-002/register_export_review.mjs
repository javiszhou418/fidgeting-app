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
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-002";
const manifest = loadManifest(modelId);
const environmentStage = manifest.stages[8];
const stage = manifest.stages[9];
if (manifest.revision !== 81
  || environmentStage.status !== "approved"
  || environmentStage.decision?.notes !== "可以的，可以的。然后开始继续下一步吧。"
  || stage.status !== "rejected"
  || !stage.decision?.notes?.includes("capsule arcs visibly look faceted")) {
  throw new Error("Expected rejected Gate 10 rev 1 at manifest revision 81.");
}

const reports = Object.fromEntries([
  ["export", "export-manifest.json"],
  ["textures", "texture-manifest.json"],
  ["glb", "glb-structure-validation.json"],
  ["reimport", "reimport-validation.json"],
  ["audit", "blender-export-audit.json"],
  ["normals", "smoothing-normal-validation.json"],
  ["images", "smoothing-image-validation.json"],
  ["collision", "collision-wireframe-validation.json"],
  ["boards", "review-board-validation.json"],
  ["renderRecipe", "smoothing-render-recipe.json"],
].map(([key, file]) => [key, JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/${file}`)))]));
if (!Object.values(reports).every((report) => report.pass)
  || reports.export.authoritativeBlend.totalTriangles !== 4096
  || reports.export.exports.settings.collision.totalTriangles !== 256
  || reports.normals.silhouette.maximumChordDeviationMm > 0.000292
  || reports.images.contourComparison.fbx.maximumSymmetricContourDistancePx !== 0
  || reports.images.contourComparison.glb.maximumSymmetricContourDistancePx !== 0) {
  throw new Error("Gate 10 rev 2 shading/export evidence did not pass.");
}

const sourceAssetIds = [
  "magnetic-slide-tile-open-environment-blend-r002",
  "magnetic-slide-tile-open-style-review-board-r002",
  "magnetic-slide-tile-environment-optimization-decision-r001",
  "magnetic-slide-tile-material-blend-r007",
  "magnetic-slide-tile-geometry-blend-r001",
];
const sourceClaimIds = [
  "slider-model-optimization-r001",
  "slider-unity-scene-reflection-plan-r001",
  "slider-wide-black-border-d65-silver-r007",
  "slider-blockout-point-axis-distinction-r003",
];
const definitions = [
  ["export-review-registrar", "registration-source", "register_export_review.mjs", "process", "register_export_review.mjs"],
  ["export-texture-preparer", "texture-source", "prepare_export_textures.py", "process", "prepare_export_textures.py"],
  ["export-texture-manifest", "texture-manifest", "texture-manifest.json", "validation", "prepare_export_textures.py"],
  ["export-builder", "export-source", "build_export_package.py", "process", "build_export_package.py"],
  ["export-authoritative-blend", "blend-source", "magnetic-slide-tile-authoritative-r002.blend", "source-model", "build_export_package.py"],
  ["export-fbx", "fbx-export", "magnetic-slide-tile-r002.fbx", "export", "build_export_package.py"],
  ["export-glb", "glb-export", "magnetic-slide-tile-r002.glb", "export", "build_export_package.py"],
  ["export-collision-fbx", "collision-export", "magnetic-slide-tile-collision-r002.fbx", "export", "build_export_package.py"],
  ["export-manifest", "export-manifest", "export-manifest.json", "validation", "build_export_package.py"],
  ["glb-inspector-source", "validation-source", "inspect_glb_structure.py", "process", "inspect_glb_structure.py"],
  ["glb-structure-validation", "validation-report", "glb-structure-validation.json", "validation", "inspect_glb_structure.py"],
  ["reimport-validator-source", "validation-source", "validate_reimports.py", "process", "validate_reimports.py"],
  ["reimport-validation", "validation-report", "reimport-validation.json", "validation", "validate_reimports.py"],
  ["export-glb-reimport-workbench", "reimport-review", "glb-reimport-workbench.png", "blender-render", "validate_reimports.py"],
  ["export-fbx-reimport-workbench", "reimport-review", "fbx-reimport-workbench.png", "blender-render", "validate_reimports.py"],
  ["export-collision-reimport-workbench", "collision-review", "collision-reimport-workbench.png", "blender-render", "validate_reimports.py"],
  ["export-blender-audit-source", "validation-source", "audit_export_blender.py", "process", "audit_export_blender.py"],
  ["export-blender-audit", "validation-report", "blender-export-audit.json", "validation", "audit_export_blender.py"],
  ["export-workbench-source", "validation-source", "capture_gate10_workbench.py", "process", "capture_gate10_workbench.py"],
  ["export-workbench", "export-review-board", "gate10-workbench.png", "blender-render", "capture_gate10_workbench.py"],
  ["smoothing-normal-validator", "validation-source", "validate_smoothing_normals.py", "process", "validate_smoothing_normals.py"],
  ["smoothing-normal-validation", "validation-report", "smoothing-normal-validation.json", "validation", "validate_smoothing_normals.py"],
  ["smoothing-renderer", "review-source", "render_smoothing_comparison.py", "process", "render_smoothing_comparison.py"],
  ["smoothing-render-recipe", "validation-report", "smoothing-render-recipe.json", "validation", "render_smoothing_comparison.py"],
  ["arc-closeup-source", "export-review-board", "arc-closeup-source-2560.png", "blender-render", "render_smoothing_comparison.py"],
  ["arc-closeup-rejected-fbx", "export-review-board", "arc-closeup-rev1-fbx-2560.png", "blender-render", "render_smoothing_comparison.py"],
  ["arc-closeup-fbx", "export-review-board", "arc-closeup-rev2-fbx-2560.png", "blender-render", "render_smoothing_comparison.py"],
  ["arc-closeup-glb", "export-review-board", "arc-closeup-rev2-glb-2560.png", "blender-render", "render_smoothing_comparison.py"],
  ["collision-wireframe-renderer", "review-source", "render_collision_wireframe.py", "process", "render_collision_wireframe.py"],
  ["collision-wireframe", "collision-review", "collision-wireframe-only.png", "blender-render", "render_collision_wireframe.py"],
  ["collision-wireframe-validation", "validation-report", "collision-wireframe-validation.json", "validation", "render_collision_wireframe.py"],
  ["smoothing-image-validator", "validation-source", "validate_smoothing_images.py", "process", "validate_smoothing_images.py"],
  ["smoothing-image-validation", "validation-report", "smoothing-image-validation.json", "validation", "validate_smoothing_images.py"],
  ["export-shading-review-board", "export-review-board", "export-shading-review-board.png", "blender-render", "validate_smoothing_images.py"],
  ["arc-contour-overlay", "export-review-board", "arc-contour-overlay-2560.png", "blender-render", "validate_smoothing_images.py"],
  ["collision-non-rendering-panel", "collision-review", "collision-non-rendering-panel.png", "blender-render", "validate_smoothing_images.py"],
  ["export-board-builder", "review-source", "build_export_review_boards.py", "process", "build_export_review_boards.py"],
  ["export-board-validation", "validation-report", "review-board-validation.json", "validation", "build_export_review_boards.py"],
  ["export-texture-channel-board", "export-review-board", "texture-channel-review-board.png", "blender-render", "build_export_review_boards.py"],
  ["export-artwork-upper-mask", "texture-source", "textures/artwork-upper-mask.png", "export", "prepare_export_textures.py"],
  ["export-artwork-lower-mask", "texture-source", "textures/artwork-lower-mask.png", "export", "prepare_export_textures.py"],
  ["export-artwork-border-mask", "texture-source", "textures/artwork-top-perimeter-border-mask.png", "export", "prepare_export_textures.py"],
  ["export-artwork-upper-pack", "texture-pack", "textures/artwork-upper-channel-pack.png", "export", "prepare_export_textures.py"],
  ["export-artwork-lower-pack", "texture-pack", "textures/artwork-lower-channel-pack.png", "export", "prepare_export_textures.py"],
  ["export-upper-transport-basecolor", "transport-texture", "textures/face-upper-transport-basecolor.png", "export", "prepare_export_textures.py"],
  ["export-lower-transport-basecolor", "transport-texture", "textures/face-lower-transport-basecolor.png", "export", "prepare_export_textures.py"],
];
const records = definitions.map(([suffix, slot, file, role, recipe]) => {
  const relativePath = `${root}/${file}`;
  const absolutePath = resolveRepoPath(relativePath);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing ${relativePath}`);
  const rendered = /\.(png|blend|fbx|glb)$/.test(file);
  return {
    id: `${modelId}-${suffix}-r002`,
    stageId: "10-export",
    slot,
    path: relativePath,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role,
    producer: {
      name: rendered ? "Blender/Pillow export pipeline" : "Python/Node.js",
      version: rendered ? reports.audit.blender : "Python 3 / Node.js",
      recipe: `${root}/${recipe}`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      sourceGate09Revision: 2,
      sourceGate10Revision: 1,
      sourceGate10State: "rejected-preserved",
      sourceGeometryDigest: reports.export.sourceGate09.geometryDigest,
      sourceTriangleGeometryDigest: reports.export.exports.smoothing.sourceTriangleGeometryDigest,
      note: "Gate 10 rev 2 corrects export shading metadata and review presentation without changing approved geometry or entering Unity.",
    },
    sourceAssetIds,
    sourceClaimIds,
  };
});
manifest.assets.push(...records);

const exportClaimId = "slider-gate10-export-shading-r002";
manifest.claims.push({
  id: exportClaimId,
  stageId: "10-export",
  topic: "gate10-export-shading",
  statement: "Gate 10 rev 2 保持 4,096-triangle render geometry 不变；侧壁 smooth，顶/底盖 flat，cap-side seam hard；FBX 使用 FACE smoothing，GLB 传输 NORMAL/TANGENT。两个 128-triangle 碰撞胶囊仅用于碰撞，不渲染且不影响外观。",
  confidence: "high",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: ["magnetic-slide-tile-open-environment-blend-r002"],
  sourceRegions: [],
  sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
  decisionState: "requested-and-executed",
  deliveryState: "gate10-ready-for-review-gate11-not-started",
});

stage.revision += 1;
stage.status = "ready_for_review";
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  "export-shading-review-board",
  "arc-contour-overlay",
  "collision-non-rendering-panel",
  "export-texture-channel-board",
  "export-glb",
  "export-workbench",
].map((suffix) => `${modelId}-${suffix}-r002`);
stage.exportSpec = {
  revision: 2,
  rejectedRevision: { revision: 1, status: "rejected-preserved", notes: stage.decision.notes },
  sourceGate09: {
    revision: 2,
    status: "approved",
    approvalWording: "可以的，可以的。然后开始继续下一步吧。",
    geometryDigest: reports.export.sourceGate09.geometryDigest,
    localMeshHash: reports.export.sourceGate09.localMeshHash,
  },
  rootCause: reports.export.rootCause,
  dimensionsMm: [50, 31, 12],
  renderMeshes: 2,
  renderTriangles: 4096,
  silhouette: reports.normals.silhouette,
  smoothing: {
    sourceAndExportTriangleDigest: reports.export.exports.smoothing.sourceTriangleGeometryDigest,
    fbxtype: "FACE",
    sideNormalDiscontinuityDegrees: 0,
    capSideNormalAngleDegrees: [89.9995, 90.0025],
    normalInversions: 0,
    fbxContourDistancePx: reports.images.contourComparison.fbx.maximumSymmetricContourDistancePx,
    glbContourDistancePx: reports.images.contourComparison.glb.maximumSymmetricContourDistancePx,
  },
  defaultPose: "closed-zero-motion",
  separateSlidePose: { axis: "+Y", travelMm: 21, rotationDegrees: 0 },
  pointAxis: { coordinateMm: [0, -9.5, 0], axis: "+Z" },
  detents: { count: 30, stepDegrees: 12, deliveryState: "specified-only" },
  formats: {
    blend: reports.export.exports.authoritativeBlend,
    fbx: reports.export.exports.fbx,
    glb: reports.export.exports.glb,
    collisionFbx: reports.export.exports.collisionFbx,
  },
  exportSettings: reports.export.exports.settings,
  reimport: {
    fbx: reports.reimport.fbx,
    glb: reports.reimport.glb,
    collision: reports.reimport.collision,
  },
  astcPlan: reports.export.textures.gate11IosAstcPlan,
  astcDeliveryState: "specified-only-not-applied",
  optimization: reports.export.optimization,
  packageDigest: reports.export.packageDigest,
  unityImportDeliveryState: "not-started-gate11",
};
stage.validations = [
  { id: "rev1-rejection-preserved", status: "pass", evidence: "Gate 10 rev 1 remains registered and rejected at workflow revision 81." },
  { id: "geometry-unchanged", status: "pass", evidence: `Source/export triangle digest ${reports.export.exports.smoothing.sourceTriangleGeometryDigest}; 4,096 triangles; 256 segments per semicircle; 0.0002918 mm chord error.` },
  { id: "explicit-smoothing", status: "pass", evidence: "Each source body has 513 smooth side faces, two flat caps, and 1,026 sharp cap-side edges. Triangulated export flags are reset explicitly." },
  { id: "fbx-glb-normal-transport", status: "pass", evidence: "FBX uses mesh_smooth_type=FACE. FBX/GLB side corner normal discontinuity is 0.000°; cap-side discontinuity remains about 90°; GLB has NORMAL/TANGENT/TEXCOORD_0." },
  { id: "same-camera-highlight-continuity", status: "pass", evidence: `FBX/GLB p99 RGB delta from source is ${reports.images.sameCameraImageDifference.fbx.p99AbsoluteRgbDifference}/${reports.images.sameCameraImageDifference.glb.p99AbsoluteRgbDifference}; contour distance is 0 px.` },
  { id: "collision-separated", status: "pass", evidence: "Collision is shown only in a separate bilingual wireframe panel. Each non-rendering capsule is 128 triangles and does not affect appearance." },
  { id: "scale-hierarchy-pivot", status: "pass", evidence: "FBX/GLB re-import at 0.031×0.050×0.012 m with closed zero-motion default and [0,-9.5,0] +Z point pivot." },
  { id: "materials-artwork-astc", status: "pass", evidence: "Approved slots and separate upper/lower artwork packs remain unchanged. ASTC 4×4 remains Gate 11 specified-only." },
  { id: "gate10-only", status: "pass", evidence: "No Gate 11, Unity import/modification, runtime/Haptic, build, install, or phone push occurred." },
];
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
  const hashes = current.artifactIds.map((assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claimRecords = manifest.claims.filter((claim) => claim.stageId === current.id).map(stableJson);
  current.inputDigest = index === 0 ? digestValues([...hashes, ...claimRecords]) : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claimRecords]);
}
manifest.currentState.visualApproval = "gate10-export-rev2-pending";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis = "Gate 10 rev 1 已保留为 rejected。rev 2 未增加 render geometry 面数：圆弧仍为每半圆 256 段、4,096 triangles、0.0002918 mm 最大弦误差。FBX smoothing 改为 FACE，侧壁连续法线 0.000°，顶/底盖与侧壁保持约 90° 硬边；FBX/GLB 与 source 同相机轮廓差 0 px。128-triangle 碰撞胶囊已移到独立双语 wireframe panel，明确不渲染、不影响外观。等待 Gate 10 rev 2 视觉批准，未进入 Unity 或推送手机。";

const event = {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "10-export",
  exportRevision: 2,
  rejectedRevisionPreserved: 1,
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  packageDigest: reports.export.packageDigest,
  smoothing: stage.exportSpec.smoothing,
  renderTriangles: 4096,
  collisionTriangles: 256,
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  stageRevision: saved.stages[9].revision,
  status: saved.stages[9].status,
  artifacts: saved.stages[9].artifactIds.length,
  reviewArtifacts: saved.stages[9].reviewArtifactIds.length,
  exportClaimId,
}, null, 2));
