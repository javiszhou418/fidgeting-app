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
const previewRoot = `${evidenceRoot}/unity-playmode-preview`;
const candidateRoot =
  "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate08R004NeutralParity";
const manifest = loadManifest(modelId);
const gate08 = manifest.stages.find((item) => item.id === "08-lighting");
const gate11 = manifest.stages.find((item) => item.id === "11-unity-parity");
if (
  manifest.revision !== 209
  || gate08?.lightingSpec?.revision !== 4
  || gate08.status !== "blocked"
  || gate11?.status !== "stale"
) {
  throw new Error("Expected blocked Gate 08 rev 4 at pipeline revision 209.");
}

const validation = JSON.parse(fs.readFileSync(resolveRepoPath(
  `${previewRoot}/gate08-r004-unity-playmode-validation.json`
)));
const capture = JSON.parse(fs.readFileSync(resolveRepoPath(
  `${previewRoot}/unity-playmode-capture-report.json`
)));
const stream = validation.ffprobe.streams[0];
if (
  !validation.pass
  || stream.codec_name !== "h264"
  || stream.width !== 1920
  || stream.height !== 1080
  || stream.r_frame_rate !== "30/1"
  || stream.nb_read_frames !== "450"
  || Number(validation.ffprobe.format.duration) !== 15
  || capture.evidenceLevel !== "Unity Editor PlayMode"
  || capture.blenderFrameCount !== 0
  || capture.offlineCompositeCount !== 0
  || !capture.perFrameTransformValidation
  || capture.iPhoneBuild
  || capture.shippingSceneModified
) {
  throw new Error("Unity-only PlayMode evidence failed registration.");
}

const definitions = [
  [
    "runtime-recording",
    "unity-runtime-recording",
    `${previewRoot}/gate08-r004-unity-playmode-runtime.mp4`,
    "unity-render",
  ],
  [
    "runtime-poster",
    "unity-runtime-poster",
    `${previewRoot}/gate08-r004-unity-playmode-runtime-poster.png`,
    "unity-render",
  ],
  [
    "runtime-validation",
    "playback-and-frame-validation",
    `${previewRoot}/gate08-r004-unity-playmode-validation.json`,
    "validation",
  ],
  [
    "capture-report",
    "playmode-transform-metadata",
    `${previewRoot}/unity-playmode-capture-report.json`,
    "validation",
  ],
  [
    "capture-scene",
    "unity-playmode-scene",
    `${candidateRoot}/Scenes/MagneticSlideTileUnityOnlyPlayModePreview.unity`,
    "unity-render",
  ],
  [
    "capture-runtime-source",
    "unity-playmode-capture-source",
    `${candidateRoot}/Runtime/MagneticSlideTileUnityOnlyPlayModeCapture.cs`,
    "process",
  ],
  [
    "capture-builder-source",
    "unity-playmode-builder-source",
    `${candidateRoot}/Editor/MagneticSlideTileUnityOnlyPlayModeCaptureBuilder.cs`,
    "process",
  ],
  [
    "encoder-source",
    "recording-encoder-source",
    `${evidenceRoot}/build_unity_playmode_preview.py`,
    "process",
  ],
  [
    "capture-log",
    "unity-playmode-capture-log",
    "unity/FidgetingApp/Logs/MagneticSlideTileUnityOnlyPlayModeCapture.log",
    "validation",
  ],
  [
    "browser-test",
    "browser-playback-test-source",
    "tools/model-provenance-explorer/tests/browser-gate08-r004-unity-playmode.mjs",
    "process",
  ],
  [
    "registrar",
    "registration-source",
    `${evidenceRoot}/register_unity_playmode_preview.mjs`,
    "process",
  ],
];
const sourceAssetIds = [
  "magnetic-slide-tile-export-fbx-r009",
  "magnetic-slide-tile-lighting-environment-r004",
  "magnetic-slide-tile-lighting-unity-scene-r004",
];
const records = definitions.map(([suffix, slot, assetPath, role]) => {
  const absolute = resolveRepoPath(assetPath);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${assetPath}`);
  return {
    id: `${modelId}-unity-playmode-${suffix}-r004`,
    stageId: "11-unity-parity",
    slot,
    path: assetPath,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    reviewState: "supplemental-runtime-evidence-not-approval",
    producer: {
      name: "Gate 08 rev 4 Unity-only PlayMode capture",
      version: "Unity 6000.5.6f1 / URP Mobile_RPAsset / ffmpeg 8.1.1",
      recipe: `${evidenceRoot}/build_unity_playmode_preview.py`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate08Revision: 4,
      gate11Revision: "supplemental-stale",
      note:
        "Actual Unity Editor PlayMode Camera output. No Blender imagery, offline composite, iPhone build, shipping promotion or device install.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
const duplicate = records.find((record) =>
  manifest.assets.some((asset) => asset.id === record.id)
);
if (duplicate) throw new Error(`Asset already registered: ${duplicate.id}`);
manifest.assets.push(...records);

const id = (suffix) => `${modelId}-unity-playmode-${suffix}-r004`;
gate11.artifactIds = [...gate11.artifactIds, ...records.map((record) => record.id)];
gate11.reviewArtifactIds = [
  id("runtime-recording"),
  id("runtime-poster"),
  id("runtime-validation"),
  id("capture-report"),
  ...gate11.reviewArtifactIds,
];
gate11.validations = gate11.validations.filter(
  (item) => item.id !== "gate08-r004-unity-only-playmode"
);
gate11.validations.push({
  id: "gate08-r004-unity-only-playmode",
  status: "pass",
  evidence:
    "Actual Unity Editor PlayMode rendered 450 Camera frames at 1920×1080/30 fps. "
    + "Every frame passed fixed base/axis, legal top motion, positive scale and zero camera roll checks. "
    + "Blender frames and offline composites: 0.",
});
gate11.unityParitySpec.supplementalUnityRuntime = {
  approvalEffect: "none",
  gate08Revision: 4,
  evidenceLevel: capture.evidenceLevel,
  disclosure: capture.onScreenDisclosure,
  unityVersion: capture.unityVersion,
  renderPipeline: capture.renderPipeline,
  scene: capture.scene,
  camera: capture.camera,
  resolution: capture.dimensions,
  frameRate: capture.frameRate,
  frameCount: capture.frameCount,
  durationSeconds: capture.durationSeconds,
  importedFbxSha256: capture.importedFbxSha256,
  sharedEnvironmentExrSha256: capture.sharedEnvironmentExrSha256,
  geometryDigest: capture.geometryDigest,
  perFrameTransformValidation: true,
  blenderFrameCount: 0,
  offlineCompositeCount: 0,
  iPhoneBuild: false,
  shippingSceneModified: false,
  videoAssetId: id("runtime-recording"),
};
gate08.lightingSpec.unityOnlyRuntimeEvidence = {
  status: "supplemental-ready-for-review",
  approvalEffect: "none",
  assetId: id("runtime-recording"),
  evidenceLevel: "Unity Editor PlayMode",
  blenderFrameCount: 0,
  offlineCompositeCount: 0,
};

manifest.claims.push({
  id: "slider-gate08-r004-unity-only-playmode",
  stageId: "11-unity-parity",
  topic: "supplemental-unity-runtime-evidence",
  statement:
    "The 15-second H.264 is actual Unity URP Editor PlayMode Camera output from the current four-track FBX and Gate 08 rev 4 HDR environment. It contains no Blender imagery or offline composite.",
  confidence: "verified",
  state: "active",
  assertedBy: "measurement",
  sourceAssetIds: [
    id("runtime-recording"),
    id("runtime-validation"),
    id("capture-report"),
  ],
  sourceRegions: [],
  decisionState: "supplemental-evidence-awaiting-visual-review",
  deliveryState: "not-shipping-not-device",
});

const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`
    ).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256
  );
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
manifest.currentStageId = "08-lighting";
manifest.currentState.visualApproval =
  "gate08-rev4-unity-playmode-review-pending-not-pushed";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.blenderModelingStatus =
  "gate08-rev4-blocked-pending-unity-playmode-review";
manifest.currentState.diagnosis =
  "A 15-second Unity-only URP Editor PlayMode recording now shows the current four-track FBX under the Gate 08 rev 4 shared HDR environment. It contains no Blender frames or offline composite. Gate 08 remains blocked pending visual review; Gates 09-12 remain stale.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate08-unity-only-playmode-supplement",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  gate08Revision: 4,
  status: "supplemental-runtime-ready-no-approval-effect",
  artifactIds: records.map((record) => record.id),
  reviewArtifactIds: gate11.reviewArtifactIds,
  evidenceLevel: capture.evidenceLevel,
  frameCount: capture.frameCount,
  video: validation.video,
  blenderFrameCount: 0,
  offlineCompositeCount: 0,
  gate08Status: gate08.status,
  gate11Status: gate11.status,
  gate12Status: manifest.stages[11].status,
  buildInstallPhone: false,
  userRequestExact:
    "The user wants to see Unity’s actual rendering, not another Blender comparison.",
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate08: saved.stages[7].status,
  gate11: saved.stages[10].status,
  gate12: saved.stages[11].status,
  reviewArtifactId: id("runtime-recording"),
}, null, 2));
