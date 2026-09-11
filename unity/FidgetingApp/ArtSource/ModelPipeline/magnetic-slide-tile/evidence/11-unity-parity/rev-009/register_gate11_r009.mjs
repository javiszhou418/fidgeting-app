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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-009";
const candidateRoot =
  "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate11R009";
const manifest = loadManifest(modelId);
const stage = manifest.stages.find((item) => item.id === "11-unity-parity");
const gate10 = manifest.stages.find((item) => item.id === "10-export");
const gate12 = manifest.stages.find((item) => item.id === "12-shipping");
if (
  manifest.revision !== 197
  || gate10?.revision !== 10
  || gate10?.status !== "approved"
  || stage?.revision !== 8
  || stage?.status !== "stale"
) {
  throw new Error("Expected magnetic slide pipeline rev 197 with approved Gate 10 export rev 9/stage rev 10 and stale Gate 11 rev 8.");
}

const unityReport = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/unity-import-parity-report.json`)));
const parity = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/parity-report.json`)));
const validation = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/final-validation.json`)));
if (!unityReport.pass || !parity.pass || !validation.pass) {
  throw new Error("Gate 11 rev 9 validation is incomplete.");
}

const sourceAssetIds = [
  "magnetic-slide-tile-export-fbx-r009",
  "magnetic-slide-tile-export-glb-r009",
  "magnetic-slide-tile-export-collision-r009",
  "magnetic-slide-tile-export-hierarchy-motion-r009",
  "magnetic-slide-tile-export-gate09-contract-r009",
  "magnetic-slide-tile-export-hdri-r009",
  "magnetic-slide-tile-export-upper-mask-r009",
  "magnetic-slide-tile-export-lower-mask-r009",
  "magnetic-slide-tile-export-perimeter-mask-r009",
  "magnetic-slide-tile-export-upper-maskmap-r009",
  "magnetic-slide-tile-export-lower-maskmap-r009",
  "magnetic-slide-tile-export-upper-normal-r009",
  "magnetic-slide-tile-export-lower-normal-r009",
];
const definitions = [
  ["registrar", "registration-source", `${evidenceRoot}/register_gate11_r009.mjs`, "process"],
  ["builder", "unity-builder-source", `${candidateRoot}/Editor/MagneticSlideTileGate11Builder.cs`, "process"],
  ["metadata", "unity-runtime-source", `${candidateRoot}/Runtime/MagneticSlideTileGate11Metadata.cs`, "source-model"],
  ["preview-controller", "unity-runtime-source", `${candidateRoot}/Runtime/MagneticSlideTileGate11PreviewController.cs`, "source-model"],
  ["editmode-test", "test-source", "unity/FidgetingApp/Assets/Tests/Editor/MagneticSlideTileGate11ParityTests.cs", "validation"],
  ["crystal-shader", "shader-source", `${candidateRoot}/Shaders/MagneticSlideTileCrystal.shader`, "source-model"],
  ["silver-shader", "shader-source", `${candidateRoot}/Shaders/MagneticSlideTileSilver.shader`, "source-model"],
  ["render-fbx", "unity-import-source", `${candidateRoot}/Imported/magnetic-slide-tile-render-r009.fbx`, "source-model"],
  ["collision-fbx", "unity-collision-source", `${candidateRoot}/Imported/magnetic-slide-tile-collision-r009.fbx`, "source-model"],
  ["environment-exr", "unity-environment-source", `${candidateRoot}/Imported/Environment/magnetic-slide-tile-shipping-studio-r008.exr`, "source-model"],
  ["environment-cubemap", "unity-environment", `${candidateRoot}/Imported/Environment/MagneticSlideTileGate11R009Environment.cubemap`, "source-model"],
  ["upper-mask", "unity-texture", `${candidateRoot}/Imported/Textures/upperArtworkMask.png`, "source-model"],
  ["lower-mask", "unity-texture", `${candidateRoot}/Imported/Textures/lowerArtworkMask.png`, "source-model"],
  ["perimeter-mask", "unity-texture", `${candidateRoot}/Imported/Textures/perimeterMask.png`, "source-model"],
  ["unity-scene", "unity-scene", `${candidateRoot}/Scenes/MagneticSlideTileGate11R009Parity.unity`, "source-model"],
  ["crystal-upper-material", "unity-material", `${candidateRoot}/Materials/M_G11R009_CrystalUpper.mat`, "source-model"],
  ["crystal-lower-material", "unity-material", `${candidateRoot}/Materials/M_G11R009_CrystalLower.mat`, "source-model"],
  ["silver-material", "unity-material", `${candidateRoot}/Materials/M_G11R009_PolishedSilver.mat`, "source-model"],
  ["dark-material", "unity-material", `${candidateRoot}/Materials/M_G11R009_DarkExterior.mat`, "source-model"],
  ["volume-profile", "unity-color-profile", `${candidateRoot}/Materials/Gate11R009ParityVolume.asset`, "source-model"],
  ["unity-report", "parity-report", `${evidenceRoot}/unity-import-parity-report.json`, "validation"],
  ["parity-builder", "review-builder-source", `${evidenceRoot}/build_parity_review.py`, "process"],
  ["silhouette-builder", "review-builder-source", `${evidenceRoot}/capture_blender_silhouette.py`, "process"],
  ["final-validator", "validation-source", `${evidenceRoot}/build_final_validation.py`, "process"],
  ["parity-report", "validation-report", `${evidenceRoot}/parity-report.json`, "validation"],
  ["final-validation", "validation-report", `${evidenceRoot}/final-validation.json`, "validation"],
  ["editmode-results", "test-results", `${evidenceRoot}/editmode-results.xml`, "validation"],
  ["editmode-log", "test-log", `${evidenceRoot}/editmode-tests.log`, "validation"],
  ["unity-log", "unity-log", `${evidenceRoot}/unity-build.log`, "validation"],
  ["blender-target", "blender-neutral", `${evidenceRoot}/blender-shipping-closed.png`, "source-model"],
  ["unity-target", "unity-neutral", `${evidenceRoot}/unity-shipping-closed.png`, "unity-render"],
  ["blender-clay", "geometry-comparison", `${evidenceRoot}/blender-clay.png`, "source-model"],
  ["unity-clay", "geometry-comparison", `${evidenceRoot}/unity-clay.png`, "unity-render"],
  ["blender-silhouette", "geometry-comparison", `${evidenceRoot}/blender-silhouette.png`, "source-model"],
  ["unity-silhouette", "geometry-comparison", `${evidenceRoot}/unity-silhouette.png`, "unity-render"],
  ["unity-open", "unity-motion-pose", `${evidenceRoot}/unity-max-open.png`, "unity-render"],
  ["unity-detent-12", "unity-motion-pose", `${evidenceRoot}/unity-detent-12.png`, "unity-render"],
  ["unity-detent-36", "unity-motion-pose", `${evidenceRoot}/unity-detent-36.png`, "unity-render"],
  ["interactive-recording", "unity-runtime-recording", `${evidenceRoot}/unity-gate11-r009-interactive-review.mp4`, "unity-render"],
  ["parity-board", "parity-review-board", `${evidenceRoot}/gate11-r009-parity-board.png`, "unity-render"],
];

const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-unity-parity-${suffix}-r009`,
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
        : "Gate 11 parity workflow",
      version: "Unity 6000.5.6f1 / URP 17.5 / Blender 5.2 / Python 3",
      recipe: `${candidateRoot}/Editor/MagneticSlideTileGate11Builder.cs`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate11Revision: 9,
      mechanismEvidenceContractSha256:
        "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea",
      note: "Isolated four-track Gate 11 parity candidate. Old shipping scene remains default and hash-identical.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
const duplicate = records.find((record) =>
  manifest.assets.some((asset) => asset.id === record.id));
if (duplicate) throw new Error(`Asset already registered: ${duplicate.id}`);
manifest.assets.push(...records);

manifest.claims.push(
  {
    id: "slider-gate10-r009-chat-approval-r009",
    stageId: "10-export",
    topic: "user-approval",
    statement: "用户检查 Gate 10 rev 9 导出模型后确认模型没有问题；无法打开和旋转属于查看器问题，不构成模型拒绝。用户原话：“我觉得你可以直接推进 Unity，因为我感觉到 Unity 问题还会比较多.”",
    confidence: "user-authoritative",
    state: "active",
    assertedBy: "user",
    sourceAssetIds: ["magnetic-slide-tile-export-glb-r009"],
    sourceRegions: [],
    decisionState: "gate10-approved",
    deliveryState: "gate11-isolated-parity-started",
  },
  {
    id: "slider-gate11-r009-four-track-parity-r009",
    stageId: "11-unity-parity",
    topic: "unity-parity",
    statement: "Gate 11 rev 9 imports the exact approved four-track FBX into an isolated URP scene, preserves 31×50×12 mm provisional bounds, 8 render meshes, 99,280 triangles, 2×108-triangle collision meshes, fixed axis/four grooves/30×12° metadata, byte-identical masks and EXR, and reaches measured Blender–Unity silhouette/material parity without changing the shipping scene.",
    confidence: "verified",
    state: "active",
    assertedBy: "measurement",
    sourceAssetIds: records
      .filter((record) => [
        "parity-report",
        "validation-report",
        "unity-runtime-recording",
        "unity-scene",
      ].includes(record.slot))
      .map((record) => record.id),
    sourceRegions: [],
    decisionState: "ready-for-user-review",
    deliveryState: "isolated-gate11-not-shipping-not-device",
  },
);

stage.revision = 9;
stage.status = "ready_for_review";
stage.decision = null;
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  `${modelId}-unity-parity-interactive-recording-r009`,
  `${modelId}-unity-parity-parity-board-r009`,
  `${modelId}-unity-parity-unity-target-r009`,
  `${modelId}-unity-parity-unity-open-r009`,
];
stage.validations = [
  {
    id: "gate10-r009-chat-approval",
    status: "pass",
    evidence: "User inspected the export, treated the open/rotate failure as a viewer issue, and explicitly authorized direct Unity progression.",
  },
  {
    id: "exact-gate10-import",
    status: "pass",
    evidence: "FBX d15e5c94…2179, collision b14ea11d…851b, EXR 7f1c9fde…e6ab and all artwork masks remain byte-identical.",
  },
  {
    id: "bounds-hierarchy-topology",
    status: "pass",
    evidence: "0.031×0.012×0.050 m Unity bounds; 8 render meshes, 80,102 vertices, 99,280 triangles; 2 collision meshes with 108 triangles each.",
  },
  {
    id: "four-track-mechanism",
    status: "pass",
    evidence: "Fixed smooth bottom, raised axis, rotating carrier, two followers, ball candidates, moving top and four finite underside grooves are present. Maximum travel 18.076433 mm and 30×12° metadata remain isolated and zero-motion by default.",
  },
  {
    id: "npot-artwork-identity",
    status: "pass",
    evidence: "All 11 parity textures retain 620×1000 NPOT None. Upper/lower/perimeter mask SHA-256 values match Gate 10 exactly.",
  },
  {
    id: "urp-material-environment",
    status: "pass",
    evidence: "Custom URP crystal/silver shaders use direct mask integration, continuous EXR-derived cubemap reflection, Fresnel/clearcoat, restrained iridescence and zero emission. No Unlit artwork overlay or flat six-face cubemap is used.",
  },
  {
    id: "matched-camera-parity",
    status: "pass",
    evidence: `Silhouette IoU ${(parity.visual.silhouetteIoU * 100).toFixed(3)}%, SSIM ${parity.visual.silhouetteSsim.toFixed(6)}, edge max ${parity.visual.edgeDistancePixels.max.toFixed(3)} px; blood-red ΔE00 ${parity.material.bloodRed.deltaE2000.toFixed(2)}, bright reflection ΔE00 ${parity.material.brightReflection.deltaE2000.toFixed(2)}, black ΔE00 ${parity.material.black.deltaE2000.toFixed(2)}.`,
  },
  {
    id: "runtime-recording",
    status: "pass",
    evidence: "Real Unity URP recording is 960×720, 72 frames, 6.0 s and covers orbit plus closed, max-open, 12° compound and 36° poses. The scene also supports orbit/zoom and direct pose keys in Play Mode.",
  },
  {
    id: "focused-unity-tests",
    status: "pass",
    evidence: "Focused EditMode 6/6 passed: import hierarchy, normals/tangents/UV, NPOT, isolated scene, collision, reports and compound pose/reset.",
  },
  {
    id: "shipping-gate",
    status: "pass",
    evidence: `MeshyEDC.unity hash stayed ${unityReport.shippingSceneHashBefore}; old shipping model remains default. Gate 12, build, install and phone run did not start.`,
  },
];
stage.unityParitySpec = {
  revision: 9,
  sourceGate10Revision: 9,
  sourceGate10ApprovalQuote:
    "我觉得你可以直接推进 Unity，因为我感觉到 Unity 问题还会比较多.",
  sourceFbxSha256:
    "d15e5c944e10ac61d466668309a2ae3f1069870d3c690b67bfd5595af5e32179",
  geometryDigest:
    "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe",
  portabilityContractSha256:
    "fce83a968df4f978e84ffbab7f026c57d7b60e762d70f7cdb2f2a1aa5cf22134",
  boundsMeters: unityReport.sortedBoundsMeters,
  renderMeshCount: unityReport.renderMeshCount,
  renderVertexCount: unityReport.renderVertexCount,
  renderTriangleCount: unityReport.renderTriangleCount,
  collisionTriangleCounts: unityReport.collisionTriangleCounts,
  materialParity: parity.material,
  silhouetteParity: parity.visual,
  interactiveReviewArtifactId:
    `${modelId}-unity-parity-interactive-recording-r009`,
  playModeScene:
    "Assets/_EDC/Candidates/MagneticSlideTileGate11R009/Scenes/MagneticSlideTileGate11R009Parity.unity",
  reviewQuestion: "这个 Unity 四轨候选现在是否与已批准的 Blender 目标一致？",
  deliveryState: {
    isolatedParityScene: true,
    shippingSceneModified: false,
    oldShippingModelDefault: true,
    gate12Started: false,
    buildInstallPhoneRun: false,
    visualApproval: "pending",
    deviceAcceptance: "pending",
  },
};
delete stage.staleReason;
gate12.staleReason =
  "Gate 11 rev 9 is ready for visual review. The prior Gate 12 rejection remains preserved; no new Gate 12 work starts before explicit approval.";

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
  "gate11-rev9-ready-for-review-visual-approval-pending-not-pushed";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.diagnosis =
  "Gate 10 rev 9 is approved by chat. Gate 11 rev 9 imports the corrected four-track package into an isolated URP scene and passes exact transport, hierarchy, NPOT, shader, camera, silhouette, color-patch, interaction recording and focused Unity tests. Visual approval is pending; Gate 12, shipping scene integration, build, install and phone run have not started.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  revision: 9,
  sourceGate10Revision: 9,
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  gate12Status: gate12.status,
  visualApproval: manifest.currentState.visualApproval,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate10: saved.stages[9].status,
  gate11: saved.stages[10].status,
  gate11Revision: saved.stages[10].revision,
  gate12: saved.stages[11].status,
  reviewArtifactIds: saved.stages[10].reviewArtifactIds,
}, null, 2));
