import crypto from "node:crypto";
import fs from "node:fs";
import {
  digestValues,
  loadManifest,
  normalizeRepoPath,
  resolveRepoPath,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "premium-display-case";
const expectedRevision = Number(process.argv[2]);
const projectRoot = "unity/FidgetingApp";
const evidenceRoot =
  `${projectRoot}/ArtSource/ModelPipeline/${modelId}/evidence/04-architecture/rev-009`;
const candidateRoot =
  `${projectRoot}/Assets/_DisplayCase/Candidates/PackOpeningGate04R009`;
const manifest = loadManifest(modelId);
const gate04 = manifest.stages[3];

if (
  !Number.isInteger(expectedRevision)
  || expectedRevision !== manifest.revision
  || gate04.status !== "rejected"
  || gate04.architectureSpec?.rejectedEvidenceRevision !== 8
  || gate04.decision?.rejectionCount !== 2
  || gate04.decision?.exactUserQuotes?.some(
    (quote) => quote !== "纯纯垃圾。"
  )
) {
  throw new Error(
    `Gate 04 rev 9 registration state mismatch. Expected manifest ${expectedRevision}, actual ${manifest.revision}.`
  );
}

const architecture = readJson(`${evidenceRoot}/architecture.json`);
const validation = readJson(`${evidenceRoot}/architecture-validation.json`);
const capture = readJson(`${evidenceRoot}/unity-capture-report.json`);
const media = readJson(`${evidenceRoot}/review-media-manifest.json`);
const candidateAssets = readJson(
  `${evidenceRoot}/candidate-asset-manifest.json`
);
const testXml = fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/unity-focused-results.xml`),
  "utf8"
);
if (
  architecture.status !== "ready_for_review"
  || architecture.architectureRevision !== 5
  || architecture.evidenceRevision !== 9
  || validation.status !== "pass"
  || Object.values(validation.checks).some((value) => value !== true)
  || capture.status !== "pass"
  || capture.source !== "actual running Unity PlayMode scene and Camera output"
  || !testXml.includes('testcasecount="18"')
  || !testXml.includes('passed="18"')
  || !testXml.includes('failed="0"')
  || media.entries.length !== 5
  || candidateAssets.immutableAfterRegistration !== true
) {
  throw new Error("Gate 04 rev 9 evidence does not pass registration.");
}

const definitions = [
  ["premium-display-case-pack-opening-quality-contract-r009", "architecture-contract", `${evidenceRoot}/quality-contract.json`, "user-input"],
  ["premium-display-case-pack-opening-finalizer-r009", "architecture-evidence-builder", `${evidenceRoot}/finalize_rev9_evidence.mjs`, "process"],
  ["premium-display-case-pack-opening-source-manifest-r009", "architecture-source-manifest", `${evidenceRoot}/unity-source-manifest.json`, "validation"],
  ["premium-display-case-pack-opening-candidate-assets-r009", "architecture-candidate-asset-manifest", `${evidenceRoot}/candidate-asset-manifest.json`, "validation"],
  ["premium-display-case-pack-opening-controller-r009", "architecture-runtime-source", `${candidateRoot}/Runtime/PackOpeningGate04R009Controller.cs`, "process"],
  ["premium-display-case-pack-opening-profile-r009", "architecture-profile-source", `${candidateRoot}/Runtime/PackOpeningGate04R009Profile.cs`, "process"],
  ["premium-display-case-pack-opening-capture-source-r009", "architecture-capture-source", `${candidateRoot}/Runtime/PackOpeningGate04R009Capture.cs`, "process"],
  ["premium-display-case-pack-opening-builder-r009", "architecture-unity-builder", `${candidateRoot}/Editor/PackOpeningGate04R009Builder.cs`, "process"],
  ["premium-display-case-pack-opening-tests-source-r009", "architecture-test-source", `${candidateRoot}/Tests/Editor/PackOpeningGate04R009Tests.cs`, "process"],
  ["premium-display-case-pack-opening-body-shader-r009", "architecture-shader-source", `${candidateRoot}/Shaders/PackFoilBodyTearR009.shader`, "process"],
  ["premium-display-case-pack-opening-flap-shader-r009", "architecture-shader-source", `${candidateRoot}/Shaders/PackFoilSurfaceR009.shader`, "process"],
  ["premium-display-case-pack-opening-accent-shader-r009", "architecture-shader-source", `${candidateRoot}/Shaders/OpeningAccentR009.shader`, "process"],
  ["premium-display-case-pack-opening-scene-r009", "architecture-unity-scene", `${candidateRoot}/Scenes/PackOpeningGate04R009.unity`, "process"],
  ["premium-display-case-pack-opening-profile-asset-r009", "architecture-profile-asset", `${candidateRoot}/Profiles/PackOpeningGate04R009Profile.asset`, "process"],
  ["premium-display-case-pack-opening-architecture-r009", "architecture-plan", `${evidenceRoot}/architecture.json`, "process"],
  ["premium-display-case-pack-opening-validation-r009", "architecture-validation", `${evidenceRoot}/architecture-validation.json`, "validation"],
  ["premium-display-case-pack-opening-capture-report-r009", "architecture-capture-report", `${evidenceRoot}/unity-capture-report.json`, "validation"],
  ["premium-display-case-pack-opening-unity-tests-r009", "architecture-test-results", `${evidenceRoot}/unity-focused-results.xml`, "validation"],
  ["premium-display-case-pack-opening-media-manifest-r009", "architecture-review-media-manifest", `${evidenceRoot}/review-media-manifest.json`, "validation"],
  ["premium-display-case-pack-opening-full-video-r009", "architecture-recording", `${evidenceRoot}/gate04-r009-full-signature-60fps.mp4`, "process"],
  ["premium-display-case-pack-opening-tear-quarter-speed-r009", "architecture-recording", `${evidenceRoot}/gate04-r009-tear-closeup-quarter-speed.mp4`, "process"],
  ["premium-display-case-pack-opening-impact-quarter-speed-r009", "architecture-recording", `${evidenceRoot}/gate04-r009-impact-1700-1950ms-quarter-speed.mp4`, "process"],
  ["premium-display-case-pack-opening-tear-contact-r009", "architecture-contact-sheet", `${evidenceRoot}/tear-silhouette-contact-sheet.png`, "validation"],
  ["premium-display-case-pack-opening-impact-contact-r009", "architecture-contact-sheet", `${evidenceRoot}/impact-continuity-contact-sheet.png`, "validation"],
  ["premium-display-case-pack-opening-register-r009", "architecture-registration", `${evidenceRoot}/register_gate04_rev9.mjs`, "process"]
];

for (const [id, , assetPath] of definitions) {
  if (manifest.assets.some((asset) => asset.id === id)) {
    throw new Error(`Asset already registered: ${id}`);
  }
  const absolute = resolveRepoPath(assetPath);
  if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
    throw new Error(`Missing Gate 04 rev 9 asset: ${assetPath}`);
  }
}

const rejectionId =
  "premium-display-case-gate04-rev8-hard-rejection-r009";
const rejectionRegisterId =
  "premium-display-case-gate04-rev8-rejection-register-r009";
const sourceAssetIds = [
  rejectionId,
  "premium-display-case-modeling-contract-r003",
  "premium-display-case-shipping-native-pack-rules-r004",
  "premium-display-case-shipping-prefab-r004"
];
const reviewIds = [
  "premium-display-case-pack-opening-full-video-r009",
  "premium-display-case-pack-opening-tear-quarter-speed-r009",
  "premium-display-case-pack-opening-impact-quarter-speed-r009",
  "premium-display-case-pack-opening-tear-contact-r009",
  "premium-display-case-pack-opening-impact-contact-r009"
];
const userInputIds = new Set([
  "premium-display-case-pack-opening-quality-contract-r009"
]);

for (const [id, slot, assetPath, role] of definitions) {
  const absolute = resolveRepoPath(assetPath);
  const isUserInput = userInputIds.has(id);
  manifest.assets.push({
    id,
    stageId: "04-architecture",
    slot,
    path: normalizeRepoPath(assetPath),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    sourceAssetIds: isUserInput ? [rejectionId] : sourceAssetIds,
    sourceClaimIds: [],
    producer: {
      name: assetPath.includes("/Assets/")
        ? "Unity 6000.5.6f1 URP PlayMode candidate"
        : slot.includes("recording")
          ? "Unity PlayMode capture + ffmpeg encode"
          : "fidgeting-model-pipeline",
      version: "2026-08-28",
      recipe: "pack-opening-gate04-r009-real-unity"
    },
    provenance: {
      origin: isUserInput ? "user-provided" : "repository-generated",
      contentClass: slot,
      assertedBy: isUserInput ? "user" : "assistant",
      note:
        "Gate 04 rev 9 real Unity candidate. It is ready for visual review, not shipping runtime or physical-device evidence."
    },
    wholeAssembledCaseOnly: true,
    explodeEligible: false,
    toyPrizeBundled: false,
    shippingEligible: false,
    reviewState: reviewIds.includes(id)
      ? "ready-for-review"
      : "supporting-evidence"
  });
}

manifest.claims.push({
  id: "premium-display-case-pack-opening-rev9-direction-claim",
  stageId: "04-architecture",
  topic: "real-unity-pack-tear-impact-case-reveal",
  statement:
    "Use the real authored 384x512 Pack and real assembled case in Unity 6000.5.6f1. A top-trailing tear front keeps material ahead attached, curls freed foil, reveals depth, emits one localized 180 ms opening impact, and hands off by occlusion to one -25-to-0-degree case settle. Rev 8 noise, lavender wash, ring stack, missing hero, and hard pop remain forbidden.",
  confidence: "user-authoritative",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: [
    rejectionId,
    "premium-display-case-pack-opening-quality-contract-r009"
  ],
  sourceRegions: [],
  decisionState: "current-request-visual-approval-pending",
  deliveryState: "real-unity-in-engine-candidate-ready-for-review"
});

gate04.revision += 1;
gate04.status = "ready_for_review";
gate04.artifactIds = [
  rejectionId,
  rejectionRegisterId,
  ...definitions.map(([id]) => id),
  "premium-display-case-part-tree-internal-r005",
  "premium-display-case-exploded-plan-internal-r005"
];
gate04.reviewArtifactIds = reviewIds;
gate04.validations = Object.entries(validation.checks).map(
  ([id, passed]) => ({
    id,
    status: passed ? "pass" : "fail",
    evidence: `${evidenceRoot}/architecture-validation.json`
  })
);
gate04.decision = {
  action: "pending",
  notes:
    "Gate 04 rev 9 real Unity PlayMode evidence is ready for visual review. No unseen visual, shipping wiring, or device state is approved.",
  decidedBy: null,
  decidedAt: null
};
gate04.architectureSpec = {
  revision: 5,
  evidenceRevision: 9,
  sourceContractRevision: 3,
  sourceThread: "2e7782a0-9389-4652-be92-7193ec0d5425",
  sourceTask: "11c5cd69-58c1-46b7-9d17-cead4ab73705",
  rejectedEvidenceRevision: 8,
  rejectionEventId: "f32ea87c-9bc2-4911-b796-dfe6e72e4fee",
  exactUserRejections: ["纯纯垃圾。", "纯纯垃圾。"],
  decisionState: architecture.decisionState,
  deliveryState: architecture.deliveryState,
  engine: architecture.engine,
  scope: architecture.scope,
  phaseWindows: architecture.timelineMilliseconds,
  actualUnity: architecture.actualUnity,
  tear: architecture.tear,
  impact: architecture.impact,
  continuity: architecture.continuity,
  reveal: architecture.reveal,
  camera: architecture.camera,
  accessibility: architecture.accessibility,
  ownership: architecture.ownership,
  selfCritique: architecture.selfCritique,
  reviewMode: "complete-real-unity-recordings",
  reviewArtifactIds: reviewIds,
  internalArtifactIds: [
    "premium-display-case-part-tree-internal-r005",
    "premium-display-case-exploded-plan-internal-r005"
  ],
  captureMetrics: validation.metrics,
  candidateAssetFileCount: candidateAssets.files.length,
  shippingRuntimeWired: false,
  nativeUiWired: false,
  shippingReady: false,
  physicalPhoneInstalled: false,
  gate05Status: "stale-awaiting-gate04-rev9-approval"
};

for (let index = 4; index < manifest.stages.length; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason =
    "Gate 04 rev 9 is a real Unity architecture candidate awaiting explicit visual approval. Gate 05–12 remain stale.";
}

manifest.currentState.rebuildRequested = true;
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.visualApproval =
  "gate04-rev9-real-unity-visual-review-pending";
manifest.currentState.deviceStatus =
  "not-built-not-installed-physical-device-pending";
manifest.currentState.diagnosis =
  "Gate 04 rev 8 is hard-rejected and preserved. Gate 04 rev 9 replaces its offline noisy rectangle, lavender wash, ring stack, and hard pop with an actual Unity PlayMode scene using the real Pack, real assembled case, caller-owned contentSlot, progressive foil deformation, opening-led 180 ms impact, occlusion handoff, and one settling reveal. Focused Unity tests pass 18/18. Gates 05–12 remain stale; shippingReady=false.";
manifest.currentState.motionCorrection = {
  earliestGate: "04-architecture",
  gate04Status: "ready-for-review-rev9-real-unity",
  gate04ArchitectureRevision: 5,
  evidenceRevision: 9,
  rejectedEvidenceRevision: 8,
  rejectionEventId: "f32ea87c-9bc2-4911-b796-dfe6e72e4fee",
  downstreamStaleGates: manifest.stages.slice(4).map((stage) => stage.id),
  shippingPreviewApproved: false,
  deviceAccepted: false
};
manifest.currentState.architectureApproval = {
  stageId: "04-architecture",
  architectureRevision: 5,
  evidenceRevision: 9,
  userApprovalQuote: null,
  decisionState: "pending-visual-review",
  gate05Status: "stale"
};
manifest.model.status = "gate04-rev9-real-unity-visual-review-pending";

function stableJson(value) {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`
    ).join(",")}}`;
  }
  return JSON.stringify(value);
}

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256
  );
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
const event = {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "04-architecture",
  architectureRevision: 5,
  evidenceRevision: 9,
  rejectedEvidenceRevision: 8,
  rejectionEventId: "f32ea87c-9bc2-4911-b796-dfe6e72e4fee",
  exactUserRejections: ["纯纯垃圾。", "纯纯垃圾。"],
  sourceThread: "2e7782a0-9389-4652-be92-7193ec0d5425",
  sourceTask: "11c5cd69-58c1-46b7-9d17-cead4ab73705",
  unityVersion: "6000.5.6f1",
  urpVersion: "17.5.0",
  capture: {
    width: 804,
    height: 1748,
    fps: 60,
    frames: 186,
    durationSeconds: 3.1
  },
  focusedUnityTests: "18/18",
  validationChecks: Object.keys(validation.checks).length,
  reviewArtifactIds: reviewIds,
  staleGateIds: manifest.stages.slice(4).map((stage) => stage.id),
  shippingRuntimeWired: false,
  nativeUiWired: false,
  shippingReady: false,
  physicalPhoneInstalled: false,
  visualApproval: "pending",
  statusText: "视觉批准待确认，未推送手机"
};

const result = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: result.revision,
  approvedCount: result.derived.approvedCount,
  shippingReady: result.derived.shippingReady,
  earliestProblem: result.derived.earliestProblem,
  eventId: event.id
}, null, 2));

function readJson(assetPath) {
  return JSON.parse(fs.readFileSync(resolveRepoPath(assetPath), "utf8"));
}
