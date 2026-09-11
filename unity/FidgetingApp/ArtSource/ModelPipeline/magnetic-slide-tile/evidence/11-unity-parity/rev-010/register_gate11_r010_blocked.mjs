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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-010";
const candidateRoot =
  "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate11R010";
const manifest = loadManifest(modelId);
const stage = manifest.stages.find((item) => item.id === "11-unity-parity");
const gate12 = manifest.stages.find((item) => item.id === "12-shipping");
if (
  manifest.revision !== 203
  || stage?.revision !== 10
  || stage?.status !== "rejected"
  || stage?.unityParitySpec?.revision !== 9
  || !stage?.decision?.notes?.includes("Internal quality review rejects Gate 11 rev 9")
) {
  throw new Error("Expected pipeline rev 203 with rejected Gate 11 rev 9.");
}

const rev9Assets = stage.artifactIds.map((id) =>
  manifest.assets.find((asset) => asset.id === id));
const mutableHarnessAssets = rev9Assets.filter((asset) => asset?.slot === "test-source");
const immutableRev9Assets = rev9Assets.filter((asset) => asset?.slot !== "test-source");
for (const asset of immutableRev9Assets) {
  if (!asset) throw new Error("Rejected rev 9 asset record is missing.");
  const absolute = resolveRepoPath(asset.path);
  if (!fs.existsSync(absolute) || sha256File(absolute) !== asset.sha256) {
    throw new Error(`Rejected rev 9 changed: ${asset.path}`);
  }
}

const parity = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/full-frame-parity-report.json`)));
const unity = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/unity-import-parity-report.json`)));
const finalValidation = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/final-validation.json`)));
if (parity.pass || !unity.pass || !finalValidation.pass) {
  throw new Error("Rev 10 must validate transport while remaining visually blocked.");
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
];
const definitions = [
  ["registrar", "registration-source", `${evidenceRoot}/register_gate11_r010_blocked.mjs`, "process"],
  ["builder", "unity-builder-source", `${candidateRoot}/Editor/MagneticSlideTileGate11R010Builder.cs`, "process"],
  ["crystal-shader", "shader-source", `${candidateRoot}/Shaders/MagneticSlideTileCrystalR010.shader`, "source-model"],
  ["silver-shader", "shader-source", `${candidateRoot}/Shaders/MagneticSlideTileSilverR010.shader`, "source-model"],
  ["unity-scene", "unity-scene", `${candidateRoot}/Scenes/MagneticSlideTileGate11R010Parity.unity`, "source-model"],
  ["crystal-upper-material", "unity-material", `${candidateRoot}/Materials/M_G11R010_CrystalUpper.mat`, "source-model"],
  ["crystal-lower-material", "unity-material", `${candidateRoot}/Materials/M_G11R010_CrystalLower.mat`, "source-model"],
  ["silver-material", "unity-material", `${candidateRoot}/Materials/M_G11R010_PolishedSilver.mat`, "source-model"],
  ["ground-material", "unity-material", `${candidateRoot}/Materials/M_G11R010_Ground.mat`, "source-model"],
  ["volume-profile", "unity-color-profile", `${candidateRoot}/Materials/Gate11R010ParityVolume.asset`, "source-model"],
  ["full-frame-validator", "validation-source", `${evidenceRoot}/build_full_frame_parity.py`, "process"],
  ["final-validator", "validation-source", `${evidenceRoot}/build_final_validation.py`, "process"],
  ["editmode-test", "test-source", "unity/FidgetingApp/Assets/Tests/Editor/MagneticSlideTileGate11ParityTests.cs", "validation"],
  ["unity-report", "parity-report", `${evidenceRoot}/unity-import-parity-report.json`, "validation"],
  ["full-frame-report", "parity-report", `${evidenceRoot}/full-frame-parity-report.json`, "validation"],
  ["final-validation", "validation-report", `${evidenceRoot}/final-validation.json`, "validation"],
  ["editmode-results", "test-results", `${evidenceRoot}/editmode-results.xml`, "validation"],
  ["editmode-log", "test-log", `${evidenceRoot}/editmode-tests.log`, "validation"],
  ["unity-log", "unity-log", `${evidenceRoot}/unity-build.log`, "validation"],
  ["blender-target", "blender-neutral", `${evidenceRoot}/blender-shipping-closed.png`, "source-model"],
  ["unity-target", "unity-neutral", `${evidenceRoot}/unity-shipping-closed.png`, "unity-render"],
  ["blender-clay", "geometry-comparison", `${evidenceRoot}/blender-clay.png`, "source-model"],
  ["unity-clay", "geometry-comparison", `${evidenceRoot}/unity-clay.png`, "unity-render"],
  ["unity-open", "unity-motion-pose", `${evidenceRoot}/unity-max-open.png`, "unity-render"],
  ["unity-detent-12", "unity-motion-pose", `${evidenceRoot}/unity-detent-12.png`, "unity-render"],
  ["unity-detent-36", "unity-motion-pose", `${evidenceRoot}/unity-detent-36.png`, "unity-render"],
  ["heatmap", "difference-heatmap", `${evidenceRoot}/full-frame-difference-heatmap.png`, "validation"],
  ["interactive-recording", "unity-runtime-recording", `${evidenceRoot}/unity-gate11-r010-interactive-review.mp4`, "unity-render"],
  ["full-frame-board", "parity-review-board", `${evidenceRoot}/gate11-r010-full-frame-board.png`, "unity-render"],
];

const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-unity-parity-${suffix}-r010`,
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
        : "Gate 11 full-frame parity workflow",
      version: "Unity 6000.5.6f1 / URP 17.5 / Python 3",
      recipe: `${candidateRoot}/Editor/MagneticSlideTileGate11R010Builder.cs`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate11Revision: 10,
      mechanismEvidenceContractSha256:
        "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea",
      note: "Isolated full-frame Gate 11 correction. Visual metrics fail closed; no Gate 12 or device work.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
for (const record of records) {
  if (manifest.assets.some((asset) => asset.id === record.id)) {
    throw new Error(`Asset already registered: ${record.id}`);
  }
}

stage.historicalRevisions = stage.historicalRevisions || [];
stage.historicalRevisions.push({
  evidenceRevision: 9,
  status: "rejected",
  artifactIds: [...stage.artifactIds],
  reviewArtifactIds: [...stage.reviewArtifactIds],
  validations: structuredClone(stage.validations),
  decision: structuredClone(stage.decision),
  unityParitySpec: structuredClone(stage.unityParitySpec),
  preservedForHistory: true,
  immutableAssetDigest: digestValues(immutableRev9Assets.map((asset) => asset.sha256)),
  immutableAssetCount: immutableRev9Assets.length,
  mutableValidationHarnessAssetIds: mutableHarnessAssets.map((asset) => asset.id),
});
for (const asset of immutableRev9Assets) {
  asset.reviewState = "rejected-history";
  asset.preservedForHistory = true;
  asset.rejectedGate11Revision = 9;
}
for (const asset of mutableHarnessAssets) {
  asset.reviewState = "superseded-validation-harness";
  asset.supersededBy = `${modelId}-unity-parity-editmode-test-r010`;
}
const rev9Claim = manifest.claims.find(
  (claim) => claim.id === "slider-gate11-r009-four-track-parity-r009");
if (rev9Claim) {
  rev9Claim.state = "rejected";
  rev9Claim.decisionState = "rejected-by-full-frame-quality-review";
}

manifest.assets.push(...records);
manifest.claims.push({
  id: "slider-gate11-r010-full-frame-blocker-r010",
  stageId: "11-unity-parity",
  topic: "unity-full-frame-parity",
  statement:
    "Gate 11 rev 10 preserves the approved four-track model and exact raw camera frame, fixes rev 9 exposure, finite-ground, shadow and synthetic-hotspot defects, but remains blocked: full-frame SSIM 0.709, heatmap >24 area 16.1%, hotspot centroid error 48.2 px, hotspot aspect error 129.3%, clay gradient magnitude error 39.2% and contact-shadow error 101.2%.",
  confidence: "verified",
  state: "active",
  assertedBy: "measurement",
  sourceAssetIds: records
    .filter((record) => [
      "parity-report",
      "parity-review-board",
      "difference-heatmap",
      "unity-runtime-recording",
    ].includes(record.slot))
    .map((record) => record.id),
  sourceRegions: [],
  decisionState: "blocked-not-ready-for-review",
  deliveryState: "isolated-unity-candidate-not-shipping-not-device",
});

stage.revision = 10;
stage.status = "draft";
stage.decision = null;
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  `${modelId}-unity-parity-interactive-recording-r010`,
  `${modelId}-unity-parity-full-frame-board-r010`,
  `${modelId}-unity-parity-unity-target-r010`,
  `${modelId}-unity-parity-heatmap-r010`,
];
stage.validations = [
  {
    id: "rev9-immutable-rejection",
    status: "pass",
    evidence: `All ${immutableRev9Assets.length} rev 9 scene, render, report, recording and process files match their recorded SHA-256 values. The shared EditMode source is a mutable harness and is superseded by rev 10.`,
  },
  {
    id: "exact-gate10-transport",
    status: "pass",
    evidence: "The exact Gate 10 four-track FBX, collision, masks and EXR remain the inputs. Geometry and artwork were not changed.",
  },
  {
    id: "camera-bbox-raw-frame",
    status: "pass",
    evidence: `Raw 1400×1100 frames use no crop or post-alignment. Silhouette IoU ${(parity.cameraAndObjectBeforeAlignment.silhouetteIou * 100).toFixed(3)}%; bbox centroid error ${parity.cameraAndObjectBeforeAlignment.centroidErrorPixels.toFixed(2)} px.`,
  },
  {
    id: "full-frame-visual-parity",
    status: "fail",
    evidence: `SSIM ${parity.fullFrame.globalSsim.toFixed(3)} < 0.78; perceptual proxy ${parity.fullFrame.perceptualProxy.combined.toFixed(3)} > 0.065; heatmap >24 area ${(parity.fullFrame.heatmapAreaFractionOver24 * 100).toFixed(1)}% > 12%.`,
  },
  {
    id: "hotspot-shape",
    status: "fail",
    evidence: `Area error ${(parity.hotspot.relativeAreaError * 100).toFixed(1)}%, centroid ${parity.hotspot.centroidErrorPixels.toFixed(1)} px and aspect error ${(parity.hotspot.aspectRelativeError * 100).toFixed(1)}%.`,
  },
  {
    id: "clay-volume-contact-shadow",
    status: "fail",
    evidence: `Gradient direction cosine ${parity.clay.gradientDirectionCosine.toFixed(3)}, magnitude error ${(parity.clay.gradientMagnitudeRelativeError * 100).toFixed(1)}% and contact-shadow error ${(parity.clay.contactShadowRelativeError * 100).toFixed(1)}%.`,
  },
  {
    id: "focused-unity-tests",
    status: "pass",
    evidence: "Focused EditMode 7/7 passed, including fail-closed full-frame validation.",
  },
  {
    id: "runtime-recording",
    status: "pass",
    evidence: "Real Unity H.264 recording is 960×720, 72 frames and 6.0 seconds with orbit and mechanism poses.",
  },
  {
    id: "shipping-gate",
    status: "pass",
    evidence: `MeshyEDC.unity remains ${unity.shippingSceneHashBefore}; Gate 12, build, install and phone work did not start.`,
  },
];
stage.unityParitySpec = {
  revision: 10,
  sourceGate10Revision: 9,
  sourceFbxSha256:
    "d15e5c944e10ac61d466668309a2ae3f1069870d3c690b67bfd5595af5e32179",
  geometryDigest:
    "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe",
  alignmentPolicy: parity.alignmentPolicy,
  cameraAndObjectBeforeAlignment: parity.cameraAndObjectBeforeAlignment,
  fullFrame: parity.fullFrame,
  hotspot: parity.hotspot,
  clay: parity.clay,
  reviewStatus: "blocked-not-ready-for-review",
  interactiveReviewArtifactId:
    `${modelId}-unity-parity-interactive-recording-r010`,
  playModeScene:
    "Assets/_EDC/Candidates/MagneticSlideTileGate11R010/Scenes/MagneticSlideTileGate11R010Parity.unity",
  reviewQuestion: null,
  deliveryState: {
    isolatedParityScene: true,
    shippingSceneModified: false,
    oldShippingModelDefault: true,
    gate12Started: false,
    buildInstallPhoneRun: false,
    visualApproval: "blocked-not-requested",
    deviceAcceptance: "pending",
  },
};
stage.readiness = {
  ready: false,
  blockers: [
    "Full-frame SSIM is 0.709; minimum is 0.78.",
    "Hotspot centroid and shape do not match the Blender target.",
    "Clay luminance gradient and contact shadow do not match the Blender target.",
  ],
  note: "Do not request approval. Continue Gate 11 revision work only.",
};
delete stage.staleReason;

manifest.issues = (manifest.issues || []).filter(
  (issue) => issue.stageId !== "11-unity-parity" || !issue.id?.startsWith("slider-gate11-r010"));
manifest.issues.push(
  {
    id: "slider-gate11-r010-full-frame-similarity",
    stageId: "11-unity-parity",
    assetId: `${modelId}-unity-parity-full-frame-board-r010`,
    severity: "blocker",
    note: "Full-frame SSIM, perceptual proxy and heatmap area still fail.",
  },
  {
    id: "slider-gate11-r010-hotspot",
    stageId: "11-unity-parity",
    assetId: `${modelId}-unity-parity-heatmap-r010`,
    severity: "blocker",
    note: "The Unity hotspot remains too wide and 48.2 px from the Blender centroid.",
  },
  {
    id: "slider-gate11-r010-clay",
    stageId: "11-unity-parity",
    assetId: `${modelId}-unity-parity-unity-clay-r010`,
    severity: "blocker",
    note: "Clay gradient magnitude and contact shadow remain too weak.",
  },
);
gate12.staleReason =
  "Gate 11 rev 10 is blocked by full-frame parity. Gate 12 rejection history remains preserved; no new Gate 12 work starts.";

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
  "gate11-rev10-blocked-not-ready-no-approval-request-not-pushed";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.diagnosis =
  "Gate 11 rev 9 is rejected and immutable. Rev 10 fixes the validation design and improves full-frame parity, but the real Unity render still fails hotspot shape, clay gradient/contact shadow and full-frame similarity. Gate 11 remains draft and blocked. Gate 12, build, install and phone work have not started.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-draft-blocked",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  revision: 10,
  status: "draft",
  artifactIds: stage.artifactIds,
  reviewArtifactIds: stage.reviewArtifactIds,
  blockers: stage.readiness.blockers,
  rev9ImmutableAssetDigest:
    stage.historicalRevisions.at(-1).immutableAssetDigest,
  gate12Status: gate12.status,
  buildInstallPhoneRun: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate11: saved.stages[10].status,
  gate11Revision: saved.stages[10].revision,
  gate11Ready: saved.stages[10].readiness.ready,
  gate12: saved.stages[11].status,
  blockers: saved.stages[10].readiness.blockers,
}, null, 2));
