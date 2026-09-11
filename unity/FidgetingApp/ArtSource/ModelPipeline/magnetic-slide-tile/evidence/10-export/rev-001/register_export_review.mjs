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
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-001";
const manifest = loadManifest(modelId);
const environmentStage = manifest.stages[8];
const stage = manifest.stages[9];
if (manifest.revision !== 75
  || environmentStage.status !== "approved"
  || environmentStage.decision?.notes !== "可以的，可以的。然后开始继续下一步吧。"
  || stage.artifactIds.length !== 0) {
  throw new Error("Expected approved Gate 09 rev 2 and empty Gate 10 at manifest revision 75.");
}

const exportManifest = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/export-manifest.json`)));
const textures = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/texture-manifest.json`)));
const glb = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/glb-structure-validation.json`)));
const reimport = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/reimport-validation.json`)));
const audit = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/blender-export-audit.json`)));
const boards = JSON.parse(fs.readFileSync(resolveRepoPath(`${root}/review-board-validation.json`)));
if (![exportManifest, textures, glb, reimport, audit, boards].every((report) => report.pass)
  || exportManifest.authoritativeBlend.totalTriangles !== 4096
  || exportManifest.exports.settings.collision.totalTriangles !== 256
  || reimport.glb.bounds.sizeMeters[1] < 0.049999
  || reimport.fbx.bounds.sizeMeters[1] < 0.049999) {
  throw new Error("Gate 10 export evidence did not pass.");
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
  ["export-review-registrar", "registration-source", "register_export_review.mjs", "process"],
  ["export-texture-preparer", "texture-source", "prepare_export_textures.py", "process"],
  ["export-texture-manifest", "texture-manifest", "texture-manifest.json", "validation"],
  ["export-builder", "export-source", "build_export_package.py", "process"],
  ["export-authoritative-blend", "blend-source", "magnetic-slide-tile-authoritative.blend", "source-model"],
  ["export-fbx", "fbx-export", "magnetic-slide-tile.fbx", "export"],
  ["export-glb", "glb-export", "magnetic-slide-tile.glb", "export"],
  ["export-collision-fbx", "collision-export", "magnetic-slide-tile-collision.fbx", "export"],
  ["export-manifest", "export-manifest", "export-manifest.json", "validation"],
  ["glb-inspector-source", "validation-source", "inspect_glb_structure.py", "process"],
  ["glb-structure-validation", "validation-report", "glb-structure-validation.json", "validation"],
  ["reimport-validator-source", "validation-source", "validate_reimports.py", "process"],
  ["reimport-validation", "validation-report", "reimport-validation.json", "validation"],
  ["export-blender-audit-source", "validation-source", "audit_export_blender.py", "process"],
  ["export-blender-audit", "validation-report", "blender-export-audit.json", "validation"],
  ["export-workbench-source", "validation-source", "capture_gate10_workbench.py", "process"],
  ["export-workbench", "export-review-board", "gate10-workbench.png", "blender-render"],
  ["export-board-builder", "review-source", "build_export_review_boards.py", "process"],
  ["export-board-validation", "validation-report", "review-board-validation.json", "validation"],
  ["export-package-review-board", "export-review-board", "export-package-review-board.png", "blender-render"],
  ["export-texture-channel-board", "export-review-board", "texture-channel-review-board.png", "blender-render"],
  ["export-glb-reimport-workbench", "reimport-review", "glb-reimport-workbench.png", "blender-render"],
  ["export-fbx-reimport-workbench", "reimport-review", "fbx-reimport-workbench.png", "blender-render"],
  ["export-collision-reimport-workbench", "collision-review", "collision-reimport-workbench.png", "blender-render"],
  ["export-artwork-upper-mask", "texture-source", "textures/artwork-upper-mask.png", "export"],
  ["export-artwork-lower-mask", "texture-source", "textures/artwork-lower-mask.png", "export"],
  ["export-artwork-border-mask", "texture-source", "textures/artwork-top-perimeter-border-mask.png", "export"],
  ["export-artwork-upper-pack", "texture-pack", "textures/artwork-upper-channel-pack.png", "export"],
  ["export-artwork-lower-pack", "texture-pack", "textures/artwork-lower-channel-pack.png", "export"],
  ["export-upper-transport-basecolor", "transport-texture", "textures/face-upper-transport-basecolor.png", "export"],
  ["export-lower-transport-basecolor", "transport-texture", "textures/face-lower-transport-basecolor.png", "export"],
];
const records = definitions.map(([suffix, slot, file, role]) => {
  const relativePath = `${root}/${file}`;
  const absolutePath = resolveRepoPath(relativePath);
  if (!fs.existsSync(absolutePath)) throw new Error(`Missing ${relativePath}`);
  const isImage = file.endsWith(".png");
  const isSource = /\.(py|mjs)$/.test(file);
  return {
    id: `${modelId}-${suffix}-r001`,
    stageId: "10-export",
    slot,
    path: relativePath,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role,
    producer: {
      name: isImage || file.endsWith(".blend") || file.endsWith(".fbx") || file.endsWith(".glb")
        ? "Blender/Pillow export pipeline"
        : "Python/Node.js",
      version: isImage || file.endsWith(".blend") || file.endsWith(".fbx") || file.endsWith(".glb")
        ? audit.blender
        : "Python 3 / Node.js",
      recipe: `${root}/${isSource ? file : file.includes("texture") || file.includes("artwork") || file.includes("basecolor")
        ? "prepare_export_textures.py"
        : "build_export_package.py"}`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: suffix,
      assertedBy: "assistant",
      sourceGate09Revision: 2,
      sourceGate09Approval: "可以的，可以的。然后开始继续下一步吧。",
      sourceGeometryDigest: exportManifest.sourceGate09.geometryDigest,
      sourceLocalMeshHash: exportManifest.sourceGate09.localMeshHash,
      note: "Gate 10 rev 1 derives from the approved Gate 09 rev 2 state, keeps the closed zero-motion default, and does not enter Unity.",
    },
    sourceAssetIds,
    sourceClaimIds,
  };
});
manifest.assets.push(...records);

const exportClaimId = "slider-gate10-export-contract-r001";
manifest.claims.push({
  id: exportClaimId,
  stageId: "10-export",
  topic: "gate10-export-package",
  statement: "Gate 10 导出包必须保持 50×31×12 mm、两片 4,096 triangles、closed zero-motion default、[0,-9.5,0] +Z point axis、独立 +Y 21 mm slide pose、30×12° specified-only、三项材质 slot、上下独立 artwork mask，并单独提供两个 convex capsule collision proxies。不得创建 LOD 或进入 Unity。",
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
  "export-package-review-board",
  "export-texture-channel-board",
  "export-glb",
  "export-workbench",
  "export-collision-reimport-workbench",
].map((suffix) => `${modelId}-${suffix}-r001`);
stage.exportSpec = {
  revision: 1,
  sourceGate09: {
    revision: 2,
    status: "approved",
    approvalWording: "可以的，可以的。然后开始继续下一步吧。",
    blendSha256: exportManifest.sourceGate09.sha256Before,
    geometryDigest: exportManifest.sourceGate09.geometryDigest,
    localMeshHash: exportManifest.sourceGate09.localMeshHash,
  },
  dimensionsMm: [50, 31, 12],
  renderMeshes: 2,
  renderTriangles: 4096,
  defaultPose: "closed-zero-motion",
  separateSlidePose: { axis: "+Y", travelMm: 21, rotationDegrees: 0 },
  pointAxis: { coordinateMm: [0, -9.5, 0], axis: "+Z" },
  detents: { count: 30, stepDegrees: 12, deliveryState: "specified-only" },
  units: exportManifest.authoritativeBlend.sceneUnits,
  hierarchy: {
    root: "MagneticSlideTile_Blockout_R003",
    fixed: "FixedAssembly/LowerBody_Fixed_CleanPlane",
    moving: "UpperTranslation/CentralAxisPivot_Point/UpperCapsule_Moving",
    hiddenMechanism: "ConcealedCircularEnvelope_Metadata EMPTY",
  },
  formats: {
    blend: exportManifest.exports.authoritativeBlend,
    fbx: exportManifest.exports.fbx,
    glb: exportManifest.exports.glb,
    collisionFbx: exportManifest.exports.collisionFbx,
  },
  exportSettings: exportManifest.exports.settings,
  reimport: {
    fbx: reimport.fbx,
    glb: reimport.glb,
    collision: reimport.collision,
  },
  textureMemory: {
    runtimeUncompressedRgba32Bytes: textures.runtimeUncompressedRgba32Bytes,
    runtimePlannedAstcBytes: textures.runtimePlannedAstcBytes,
  },
  astcPlan: exportManifest.textures.gate11IosAstcPlan,
  astcDeliveryState: "specified-only-not-applied",
  optimization: exportManifest.optimization,
  packageDigest: exportManifest.packageDigest,
  unityImportDeliveryState: "not-started-gate11",
};
stage.validations = [
  { id: "gate09-approval-persisted", status: "pass", evidence: "Workflow revision 75 stores the exact approval “可以的，可以的。然后开始继续下一步吧。”" },
  { id: "authoritative-blend-clean", status: "pass", evidence: "Authoritative Blend contains two render meshes, point/motion hierarchy, metadata-only hidden envelope, two hidden collision proxies, no cameras/lights/world/actions/constraints/drivers." },
  { id: "scale-and-bounds", status: "pass", evidence: "FBX and GLB re-import to 0.031×0.050×0.012 m within 0.000002 m tolerance; Blender source remains 31×50×12 mm in XY/Z order." },
  { id: "geometry-and-triangles", status: "pass", evidence: `Local mesh hash ${exportManifest.sourceGate09.localMeshHash}; FBX and GLB each re-import as two meshes and 4,096 triangles.` },
  { id: "hierarchy-pivot-pose", status: "pass", evidence: "Root/fixed/UpperTranslation/point-axis hierarchy survives; default translation and rotation are zero; point pivot remains local [0,-9.5,0]." },
  { id: "normals-tangents-uv", status: "pass", evidence: "GLB JSON primitives include POSITION/NORMAL/TANGENT/TEXCOORD_0; Blender FBX/GLB re-imports retain loop normals and UV layers." },
  { id: "materials-and-artwork", status: "pass", evidence: "Three approved material slot names survive; upper/lower source masks remain independently replaceable with approved SHA-256 and separate RGBA packs." },
  { id: "collision", status: "pass", evidence: "Separate collision FBX contains two watertight convex capsule prisms, 128 triangles each, no materials, within render bounds." },
  { id: "no-motion-or-lod", status: "pass", evidence: "FBX/GLB contain no animation; no idle/self motion, constraints, drivers, high/low pair, Decimate, or visible LOD was added." },
  { id: "hidden-mechanism", status: "pass", evidence: "ConcealedCircularEnvelope_Metadata remains an EMPTY in Blend/FBX/GLB and never becomes visible mesh geometry." },
  { id: "texture-memory", status: "pass", evidence: `Two 620×1000 linear artwork packs total ${textures.runtimeUncompressedRgba32Bytes} bytes RGBA32; planned ASTC 4×4 total ${textures.runtimePlannedAstcBytes} bytes.` },
  { id: "astc-specified-only", status: "pass", evidence: "ASTC 4×4, max 1024, mipmaps on, linear, opaque/reserved alpha is a Gate 11 import plan only; no Unity import setting was applied." },
  { id: "gate10-only", status: "pass", evidence: "No Gate 11, Unity import/modification, Reflection Probe/runtime/Haptic, build, install, or phone push was performed." },
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
manifest.currentState.visualApproval = "gate10-export-rev1-pending";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis = "Gate 09 rev 2 已按用户原文批准。Gate 10 rev 1 已生成 clean authoritative Blend、FBX、GLB、独立 collision FBX、export/texture manifests、Blender re-import 与 GLB structure 验证。FBX/GLB 均为 closed zero-motion default、两片 4,096 triangles、0.050×0.031×0.012 m；上下 artwork 独立，ASTC 仍为 Gate 11 specified-only。当前等待 Gate 10 批准，未进入或修改 Unity，未推送手机。";

const event = {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "10-export",
  exportRevision: 1,
  sourceGate09Revision: 2,
  sourceGate09Approval: "可以的，可以的。然后开始继续下一步吧。",
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  packageDigest: exportManifest.packageDigest,
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
