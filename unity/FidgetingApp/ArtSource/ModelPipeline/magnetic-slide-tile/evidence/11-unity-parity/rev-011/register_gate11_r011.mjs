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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-011";
const candidateRoot =
  "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate11R011";
const manifest = loadManifest(modelId);
const gate10 = manifest.stages.find((stage) => stage.id === "10-export");
const gate11 = manifest.stages.find((stage) => stage.id === "11-unity-parity");
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
if (
  manifest.revision < 253
  || gate10?.exportSpec?.revision !== 11
  || gate10?.status !== "approved"
  || gate11?.revision !== 11
  || !["draft", "ready_for_review"].includes(gate11?.status)
) {
  throw new Error("Expected blocked Gate 11 rev 11 after pipeline rev 253.");
}

const read = (name) => JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/${name}`), "utf8"));
const unity = read("unity-import-parity-report.json");
const parity = read("parity-validation.json");
const capture = read("unity-playmode-frames/unity-playmode-capture-report.json");
const video = read("unity-playmode-video-validation.json");
const tests = fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/editmode-results.xml`), "utf8");
if (
  !unity.pass
  || !parity.pass
  || parity.humanInspection.status !== "complete"
  || capture.frameCount !== 540
  || capture.fullRotationDetents !== 30
  || !tests.includes('result="Passed" total="5" passed="5"')
  || !video.pass
) {
  throw new Error("Gate 11 rev 11 validation is incomplete.");
}

const sourceAssetIds = [
  "magnetic-slide-tile-export-glb-r011",
  "magnetic-slide-tile-export-fbx-r011",
  "magnetic-slide-tile-export-collision-r011",
  "magnetic-slide-tile-export-blend-r011",
];
const definitions = [
  ["registrar", "registration-source", `${evidenceRoot}/register_gate11_r011.mjs`, "process"],
  ["environment-builder", "environment-build-source", `${evidenceRoot}/build_unity_specular_strip.py`, "process"],
  ["parity-builder", "parity-build-source", `${evidenceRoot}/build_parity_evidence.py`, "process"],
  ["blender-renderer", "parity-render-source", `${evidenceRoot}/render_blender_glb_parity.py`, "process"],
  ["environment-report", "environment-validation", `${evidenceRoot}/unity-specular-strip-report.json`, "validation"],
  ["environment-strip", "prefilter-input", `${evidenceRoot}/unity-specular-strip-r011.exr`, "unity-render"],
  ["video-builder", "video-build-source", `${evidenceRoot}/build_playmode_video.py`, "process"],
  ["builder", "unity-builder-source", `${candidateRoot}/Editor/MagneticSlideTileGate11R011Builder.cs`, "process"],
  ["controller", "unity-runtime-source", `${candidateRoot}/Runtime/MagneticSlideTileEndpointInterlockController.cs`, "source-model"],
  ["capture-source", "unity-runtime-source", `${candidateRoot}/Runtime/MagneticSlideTileGate11R011PlayModeCapture.cs`, "source-model"],
  ["metadata", "unity-runtime-source", `${candidateRoot}/Runtime/MagneticSlideTileGate11R011Metadata.cs`, "source-model"],
  ["shader", "shader-source", `${candidateRoot}/Shaders/MagneticSlideTilePortablePBRR011.shader`, "source-model"],
  ["scene", "unity-scene", `${candidateRoot}/Scenes/MagneticSlideTileGate11R011Parity.unity`, "source-model"],
  ["render-fbx", "unity-import-source", `${candidateRoot}/Imported/magnetic-slide-tile-render-r011.fbx`, "source-model"],
  ["test-source", "test-source", "unity/FidgetingApp/Assets/Tests/Editor/MagneticSlideTileGate11R011Tests.cs", "validation"],
  ["unity-report", "validation-report", `${evidenceRoot}/unity-import-parity-report.json`, "validation"],
  ["parity-report", "validation-report", `${evidenceRoot}/parity-validation.json`, "validation"],
  ["capture-report", "runtime-validation", `${evidenceRoot}/unity-playmode-frames/unity-playmode-capture-report.json`, "validation"],
  ["video-validation", "video-validation", `${evidenceRoot}/unity-playmode-video-validation.json`, "validation"],
  ["editmode-results", "test-results", `${evidenceRoot}/editmode-results.xml`, "validation"],
  ["geometry-board", "geometry-review-board", `${evidenceRoot}/gate11-r011-geometry-comparison.png`, "unity-render"],
  ["partition-board", "material-review-board", `${evidenceRoot}/gate11-r011-material-partition-comparison.png`, "unity-render"],
  ["appearance-board", "appearance-review-board", `${evidenceRoot}/gate11-r011-full-appearance-comparison.png`, "unity-render"],
  ["silver-board", "material-diagnostic-board", `${evidenceRoot}/gate11-r011-isolated-silver-comparison.png`, "unity-render"],
  ["blood-red-board", "material-diagnostic-board", `${evidenceRoot}/gate11-r011-isolated-blood-red-comparison.png`, "unity-render"],
  ["heatmap", "parity-heatmap", `${evidenceRoot}/unity-glb-full-frame-heatmap.png`, "unity-render"],
  ["playmode-video", "unity-runtime-recording", `${evidenceRoot}/magnetic-slide-tile-gate11-r011-unity-playmode.mp4`, "unity-render"],
];
const records = definitions.map(([suffix, slot, assetPath, role]) => {
  const absolute = resolveRepoPath(assetPath);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${assetPath}`);
  return {
    id: `${modelId}-unity-parity-${suffix}-r011`,
    stageId: "11-unity-parity",
    slot,
    path: assetPath,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: assetPath.includes("/Assets/")
        ? "Unity 6000.5.6f1 URP 17.5"
        : "Gate 11 rev 11 parity workflow",
      version: "Unity 6000.5.6f1 / URP 17.5 / Blender 5.2 / Python 3",
      recipe: `${candidateRoot}/Editor/MagneticSlideTileGate11R011Builder.cs`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate11Revision: 11,
      mechanismEvidenceContractSha256:
        "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
      sourceGate10ApprovalExactWording: "继续",
      note: "Isolated Gate 11 parity evidence. Shipping scene remains hash-identical.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
for (const record of records) {
  const index = manifest.assets.findIndex((asset) => asset.id === record.id);
  if (index >= 0) manifest.assets[index] = record;
  else manifest.assets.push(record);
}

const parityClaim = {
  id: "slider-gate11-r011-unity-parity",
  stageId: "11-unity-parity",
  topic: "unity-parity",
  statement:
    "Gate 11 rev 11 imports the approved Gate 10 rev 11 package into an isolated URP scene. Exact geometry, endpoint interlock, material partitions, shared HDR response, same-camera parity, and Unity-only PlayMode evidence pass without shipping promotion.",
  confidence: "verified",
  state: "active",
  assertedBy: "measurement",
  sourceAssetIds: records.map((record) => record.id),
  sourceRegions: [],
  decisionState: "ready-for-user-review",
  deliveryState: "isolated-gate11-not-shipping-not-device",
};
const parityClaimIndex = manifest.claims.findIndex(
  (claim) => claim.id === parityClaim.id);
if (parityClaimIndex >= 0) manifest.claims[parityClaimIndex] = parityClaim;
else manifest.claims.push(parityClaim);

gate11.status = "ready_for_review";
gate11.decision = null;
gate11.artifactIds = records.map((record) => record.id);
gate11.reviewArtifactIds = [
  `${modelId}-unity-parity-playmode-video-r011`,
  `${modelId}-unity-parity-geometry-board-r011`,
  `${modelId}-unity-parity-partition-board-r011`,
  `${modelId}-unity-parity-appearance-board-r011`,
  `${modelId}-unity-parity-silver-board-r011`,
  `${modelId}-unity-parity-blood-red-board-r011`,
  `${modelId}-unity-parity-capture-report-r011`,
];
gate11.validations = [
  {
    id: "import-geometry",
    status: "pass",
    evidence:
      "8 meshes, 100,896 vertices, 99,280 triangles, 31×12×50 mm bounds, one fixed axis, four grooves, no cavity or proxy.",
  },
  {
    id: "material-environment",
    status: "pass",
    evidence:
      "Top-only artwork, independent masks, one RGBAHalf specular cubemap, exact 0.85 environment intensity, zero lights/probes.",
  },
  {
    id: "same-camera-parity",
    status: "pass",
    evidence:
      `IoU ${(parity.geometry.glbUnitySilhouetteIou * 100).toFixed(4)}%, full SSIM ${parity.fullFrame.glbUnitySsim.toFixed(6)}, object SSIM ${parity.fullFrame.glbUnityObjectSsim.toFixed(6)}, silver median ΔE76 ${parity.regionalDeltaE76.silver.median.toFixed(3)}.`,
  },
  {
    id: "endpoint-playmode",
    status: "pass",
    evidence:
      "18.0 s, 540-frame Unity PlayMode recording covers closed, mid-travel lock, sMax unlock, 30×12° detents, return lock, align, and close.",
  },
  {
    id: "focused-tests",
    status: "pass",
    evidence: "Focused Unity EditMode/UnityTest suite passed 5/5.",
  },
  {
    id: "shipping-gate",
    status: "pass",
    evidence:
      `Shipping scene stayed ${unity.shippingSceneHashBefore}; Gate 12, build, install, and phone run did not start.`,
  },
];
gate11.unityParitySpec = {
  ...gate11.unityParitySpec,
  reviewStatus: "ready-for-review",
  reviewQuestion: "Gate 11 rev 11 的 Unity URP 外观与交互是否可批准？",
  boundsMeters: unity.boundsSize,
  renderMeshCount: unity.renderMeshCount,
  renderVertexCount: unity.renderVertexCount,
  renderTriangleCount: unity.renderTriangleCount,
  parityMetrics: parity,
  playModeScene: unity.scenePath,
  interactiveDeepLink:
    "?model=magnetic-slide-tile&tab=unity&gate=11-unity-parity&asset=magnetic-slide-tile-unity-parity-playmode-video-r011",
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
gate11.readiness = {
  ready: true,
  blockers: [],
  note: "Gate 11 rev 11 is ready for explicit visual and interaction review.",
};
delete gate11.staleReason;

gate12.status = "blocked";
gate12.decision = null;
gate12.staleReason =
  "Gate 11 rev 11 awaits explicit approval. Prior Gate 12 rejection remains preserved; no Gate 12 work started.";

const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`
    ).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((claim) => claim.stageId === stage.id)
    .map(stableJson);
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
manifest.currentStageId = "11-unity-parity";
manifest.currentState.visualApproval =
  "gate11-rev11-ready-for-review-visual-approval-pending-not-pushed";
manifest.currentState.unityStatus = "gate11-rev11-ready-for-review";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.workbench = "persistent-seven-tab-current-gate11-unity";
manifest.currentState.diagnosis =
  "Gate 11 rev 11 passes isolated Unity import, same-camera URP parity, endpoint interlock recording, and focused tests. Visual approval is pending; Gate 12 remains blocked. No shipping promotion, build, install, or phone run occurred.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  revision: 11,
  sourceGate10Revision: 11,
  sourceGate10ApprovalExactWording: "继续",
  artifactIds: gate11.artifactIds,
  reviewArtifactIds: gate11.reviewArtifactIds,
  gate12Status: gate12.status,
  buildInstallPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate11: saved.stages[10].status,
  gate12: saved.stages[11].status,
  reviewArtifactIds: saved.stages[10].reviewArtifactIds,
}, null, 2));
