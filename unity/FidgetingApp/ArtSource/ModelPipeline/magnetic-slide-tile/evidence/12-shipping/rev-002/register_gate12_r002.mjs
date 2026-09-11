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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-002";
const candidateRoot =
  "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate12R002";
const manifest = loadManifest(modelId);
const gate11 = manifest.stages.find((stage) => stage.id === "11-unity-parity");
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
if (
  manifest.revision < 257
  || gate11?.status !== "approved"
  || gate11?.revision !== 11
  || !["draft", "ready_for_review"].includes(gate12?.status)
  || gate12?.shippingSpec?.revision !== 2
) {
  throw new Error("Expected Gate 12 rev 2 draft at pipeline revision 257.");
}

const read = (name) => JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/${name}`), "utf8"));
const report = read("gate12-shipping-report.json");
const validation = read("gate12-image-validation.json");
const capture = read("unity-playmode-frames/capture-report.json");
const probe = read("video-probe.json");
const tests = fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/editmode-results.xml`), "utf8");
const shippingScene = resolveRepoPath("unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity");
if (
  !report.pass
  || !validation.pass
  || !capture.unityOnly
  || capture.detentCount !== 30
  || capture.detentStepDegrees !== 12
  || !capture.transitions.includes("slide-locked-until-angle-aligns")
  || probe.streams[0].nb_read_frames !== "240"
  || !tests.includes('result="Passed" total="5" passed="5"')
  || report.shippingSceneSha256 !== sha256File(shippingScene)
) {
  throw new Error("Gate 12 rev 2 validation is incomplete or stale.");
}

const sourceAssetIds = [
  "magnetic-slide-tile-unity-parity-scene-r011",
  "magnetic-slide-tile-unity-parity-render-fbx-r011",
  "magnetic-slide-tile-unity-parity-shader-r011",
  "magnetic-slide-tile-unity-parity-environment-strip-r011",
];
const definitions = [
  ["registrar", "registration-source", `${evidenceRoot}/register_gate12_r002.mjs`, "process"],
  ["starter", "approval-transition-source", `${evidenceRoot}/start_gate12_r002.mjs`, "process"],
  ["review-builder", "review-build-source", `${evidenceRoot}/build_gate12_review.py`, "process"],
  ["unity-builder", "unity-builder-source", `${candidateRoot}/Editor/MagneticSlideTileGate12R002Builder.cs`, "process"],
  ["settings-source", "mechanism-settings-source", `${candidateRoot}/Runtime/MagneticSlideTileMechanismSettings.cs`, "source-model"],
  ["mechanism-source", "runtime-mechanism-source", `${candidateRoot}/Runtime/MagneticSlideTileShippingMechanism.cs`, "source-model"],
  ["coordinator-source", "runtime-coordinator-source", `${candidateRoot}/Runtime/MagneticSlideTileShippingCoordinator.cs`, "source-model"],
  ["capture-source", "runtime-capture-source", `${candidateRoot}/Runtime/MagneticSlideTileGate12PlayModeCapture.cs`, "source-model"],
  ["test-source", "test-source", `${candidateRoot}/Tests/Editor/MagneticSlideTileGate12R002Tests.cs`, "validation"],
  ["node-test-source", "test-source", "tools/model-provenance-explorer/tests/magnetic-slide-gate12-rev2.test.mjs", "validation"],
  ["prefab", "shipping-candidate-prefab", `${candidateRoot}/Prefabs/MagneticSlideTileGate12R002Candidate.prefab`, "source-model"],
  ["settings", "shared-mechanism-settings", `${candidateRoot}/Settings/MagneticSlideTileMechanismSettingsR002.asset`, "source-model"],
  ["shipping-scene", "shipping-scene", "unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity", "source-model"],
  ["report", "shipping-validation-report", `${evidenceRoot}/gate12-shipping-report.json`, "validation"],
  ["image-validation", "shipping-image-validation", `${evidenceRoot}/gate12-image-validation.json`, "validation"],
  ["capture-report", "runtime-validation", `${evidenceRoot}/unity-playmode-frames/capture-report.json`, "validation"],
  ["video-probe", "video-validation", `${evidenceRoot}/video-probe.json`, "validation"],
  ["editmode-results", "test-results", `${evidenceRoot}/editmode-results.xml`, "validation"],
  ["shipping-board", "shipping-review-board", `${evidenceRoot}/gate12-shipping-board.png`, "unity-render"],
  ["motion-board", "motion-review-board", `${evidenceRoot}/gate12-motion-board.png`, "unity-render"],
  ["playmode-video", "unity-runtime-recording", `${evidenceRoot}/magnetic-slide-gate12-r002-unity-playmode.mp4`, "unity-render"],
  ...[
    "library", "hero", "top", "left-oblique", "right-oblique", "low",
    "phone", "max-open", "endpoint-12deg", "endpoint-36deg",
    "endpoint-360deg",
  ].map((view) => [
    `view-${view}`,
    `shipping-view-${view}`,
    `${evidenceRoot}/${view}.png`,
    "unity-render",
  ]),
];

const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute))
    throw new Error(`Missing Gate 12 artifact: ${path}`);
  return {
    id: `${modelId}-gate12-${suffix}-r002`,
    stageId: "12-shipping",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: path.includes("/Assets/")
        ? "Unity 6000.5.6f1 URP 17.5"
        : "Gate 12 rev 2 shipping workflow",
      version: "2026-08-31",
      recipe: `${candidateRoot}/Editor/MagneticSlideTileGate12R002Builder.cs`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate12Revision: 2,
      candidatePreviewOnly: true,
      mechanismEvidenceContractSha256:
        "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
      sourceGate11ApprovalExactWording: "可以的，继续",
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

const claim = {
  id: "slider-gate12-r002-shipping-candidate",
  stageId: "12-shipping",
  topic: "shipping-review",
  statement:
    "Gate 12 rev 2 integrates the approved Gate 11 four-track candidate into the canonical MeshyEDC scene behind a disabled-by-default activation. One shared settings asset drives 18.076433 mm travel, 1 µm endpoint tolerance and 30 × 12° physical/Haptic detents.",
  confidence: "verified",
  state: "active",
  assertedBy: "measurement",
  sourceAssetIds: records.map((record) => record.id),
  sourceRegions: [],
  decisionState: "ready-for-user-review",
  deliveryState: "shipping-scene-candidate-preview-only-not-device",
};
const claimIndex = manifest.claims.findIndex((item) => item.id === claim.id);
if (claimIndex >= 0) manifest.claims[claimIndex] = claim;
else manifest.claims.push(claim);

gate12.status = "ready_for_review";
gate12.artifactIds = records.map((record) => record.id);
gate12.reviewArtifactIds = [
  `${modelId}-gate12-playmode-video-r002`,
  `${modelId}-gate12-shipping-board-r002`,
  `${modelId}-gate12-motion-board-r002`,
  `${modelId}-gate12-view-phone-r002`,
];
gate12.validations = [
  {
    id: "canonical-scene-candidate-default",
    status: "pass",
    evidence:
      `Scene ${report.shippingSceneSha256}; old EDC_Root active, Gate 12 candidate inactive by default.`,
  },
  {
    id: "approved-geometry-material-parity",
    status: "pass",
    evidence:
      "Approved Gate 11 source retained: 99,280 triangles, two visible exterior renderers, top-only artwork, dark sides, silver rim and RGBAHalf shared HDR shader.",
  },
  {
    id: "shared-runtime-haptic-settings",
    status: "pass",
    evidence:
      "One ScriptableObject supplies sMax=18.076433 mm, endpoint tolerance=0.001 mm, 30 detents and 12° to the mechanism and semantic Haptic coordinator.",
  },
  {
    id: "endpoint-playmode",
    status: "pass",
    evidence:
      "240-frame Unity-only PlayMode capture covers mid-travel rotation lock, sMax unlock, 30 detents, nonzero-angle return lock, alignment and zero-velocity close.",
  },
  {
    id: "shipping-views",
    status: "pass",
    evidence:
      "Library, hero, top, both obliques, low, phone, max-open, 12°, 36° and endpoint-360 images pass color, geometry and clipping checks.",
  },
  {
    id: "focused-unity-tests",
    status: "pass",
    evidence:
      "Focused Gate 12 EditMode/UnityTest suite passed 5/5; the real-scene PlayMode recording validation also passed.",
  },
];
gate12.shippingSpec = {
  ...gate12.shippingSpec,
  sceneSha256: report.shippingSceneSha256,
  candidatePrefabPath: report.candidatePrefabPath,
  candidateDefaultActive: false,
  oldShippingModelDefaultActive: true,
  sourceGate11GlbSha256: report.sourceGate11GlbSha256,
  maximumTravelMeters: report.maximumTravelMeters,
  endpointToleranceMeters: report.endpointToleranceMeters,
  detentCount: report.detentCount,
  detentStepDegrees: report.detentStepDegrees,
  runtimeInputIntegrated: true,
  hapticsIntegrated: true,
  semanticRoute: report.semanticRoute,
  gate12Approval: "pending",
  deliveryState: "real-shipping-scene-candidate-preview-only",
  deviceHapticAcceptance: "pending",
  buildInstallPhone: false,
};
gate12.readiness = {
  ready: true,
  blockers: [],
  note: "Real shipping-scene evidence is ready for explicit visual approval. Device acceptance remains pending.",
};

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((item) => item.stageId === stage.id)
    .map((item) => JSON.stringify(item));
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
manifest.currentStageId = "12-shipping";
manifest.currentState.visualApproval =
  "gate12-r002-ready-for-review-visual-approval-pending-not-pushed";
manifest.currentState.unityStatus =
  "canonical-scene-candidate-wired-default-disabled";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.deviceStatus = "pending-not-installed";
manifest.currentState.workbench = "persistent-seven-tab-current-gate12-unity";
manifest.currentState.diagnosis =
  "Gate 12 rev 2 is ready for review from the real MeshyEDC shipping scene. The candidate is inactive by default; no build, install, launch or phone push occurred.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate12-r002-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: "12-shipping",
  gateRevision: 2,
  decisionState: "visual-approval-pending",
  deliveryState: "shipping-scene-candidate-preview-only",
  sceneSha256: report.shippingSceneSha256,
  candidateDefaultActive: false,
  oldShippingModelDefaultActive: true,
  reviewedArtifactIds: gate12.reviewArtifactIds,
  contractSha256:
    "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
  buildInstallPhone: false,
  deviceAcceptance: "pending",
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate11: saved.stages[10].status,
  gate12: saved.stages[11].status,
  reviewArtifactIds: saved.stages[11].reviewArtifactIds,
}, null, 2));
