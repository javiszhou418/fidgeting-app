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
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-010";
const rejectionPath = `${evidenceRoot}/rev9-technical-rejection.md`;
const registrationPath =
  `${evidenceRoot}/register_rev9_technical_rejection.mjs`;
const sourceThread = "2e7782a0-9389-4652-be92-7193ec0d5425";
const sourceTask = "36011d7f-627f-41a0-9c27-6a5dfd92db4b";
const manifest = loadManifest(modelId);
const gate04 = manifest.stages[3];

if (
  !Number.isInteger(expectedRevision)
  || expectedRevision !== manifest.revision
  || gate04.status !== "ready_for_review"
  || gate04.architectureSpec?.evidenceRevision !== 9
) {
  throw new Error(
    `Gate 04 rev 9 technical-rejection state mismatch. Expected manifest ${expectedRevision}, actual ${manifest.revision}.`
  );
}

const reasons = [
  "The top seal still reads as one large rigid lid floating away, not a progressive tear front.",
  "The body edge is a uniform cartoon sawtooth. It lacks foil thickness, underside, fold tension, and contact shadow.",
  "The tiny case seen inside the bag becomes the full case through a visual discontinuity. Continuity is simulated rather than real.",
  "The background and impact language are muddy and weak. The result reads as a technical demo, not a premium gacha sequence."
];
const rejectionText = fs.readFileSync(
  resolveRepoPath(rejectionPath),
  "utf8"
);
for (const reason of reasons) {
  if (!rejectionText.includes(reason)) {
    throw new Error(`Missing exact rev 9 rejection reason: ${reason}`);
  }
}
if (!rejectionText.includes("Gate 04 rev 9 must not be shown for approval.")) {
  throw new Error("The no-approval-review disposition is missing.");
}

const definitions = [
  [
    "premium-display-case-gate04-rev9-technical-rejection-r010",
    "architecture-user-decision",
    rejectionPath,
    "user-input"
  ],
  [
    "premium-display-case-gate04-rev9-technical-rejection-register-r010",
    "architecture-registration",
    registrationPath,
    "process"
  ]
];
for (const [id, , assetPath] of definitions) {
  if (manifest.assets.some((asset) => asset.id === id)) {
    throw new Error(`Asset already registered: ${id}`);
  }
  const absolute = resolveRepoPath(assetPath);
  if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
    throw new Error(`Missing rev 9 rejection asset: ${assetPath}`);
  }
}

const rejectedSnapshot = {
  ...structuredClone(gate04),
  stageStatus: "technical-rejected",
  preservedForHistory: true,
  disposition: "technical-rejected-by-parent-visual-inspection",
  rejectionReasons: reasons,
  approvalRequestAllowed: false
};
gate04.historicalRevisions = [
  ...(gate04.historicalRevisions || []),
  rejectedSnapshot
];

for (const assetId of rejectedSnapshot.artifactIds) {
  const asset = manifest.assets.find((candidate) => candidate.id === assetId);
  if (!asset) continue;
  asset.reviewState = "technical-rejected";
  asset.preservedForHistory = true;
  asset.rejectedEvidenceRevision = 9;
  asset.rejectionScope =
    "rigid-lid-cartoon-edge-false-case-continuity-muddy-impact";
  asset.approvalRequestAllowed = false;
}

const previousClaim = manifest.claims.find(
  (claim) =>
    claim.id === "premium-display-case-pack-opening-rev9-direction-claim"
);
if (previousClaim) {
  previousClaim.state = "rejected";
  previousClaim.decisionState = "technical-rejected";
  previousClaim.deliveryState = "immutable-technical-rejected-history";
  previousClaim.rejectionReasons = reasons;
}

const rejectionId = definitions[0][0];
for (const [id, slot, assetPath, role] of definitions) {
  const absolute = resolveRepoPath(assetPath);
  const isDecision = id === rejectionId;
  manifest.assets.push({
    id,
    stageId: "04-architecture",
    slot,
    path: normalizeRepoPath(assetPath),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    sourceAssetIds: isDecision
      ? rejectedSnapshot.reviewArtifactIds
      : [rejectionId],
    sourceClaimIds: [],
    producer: {
      name: isDecision
        ? "Cursor parent visual inspection"
        : "fidgeting-model-pipeline",
      version: isDecision ? sourceTask : "2026-08-28",
      recipe: "gate04-rev9-technical-rejection"
    },
    provenance: {
      origin: isDecision ? "user-provided" : "repository-generated",
      contentClass: slot,
      assertedBy: isDecision ? "user" : "assistant",
      note: isDecision
        ? "The latest chat instruction authorizes the parent visual inspection's technical rejection and forbids approval review."
        : "Persists the revision-checked rejection through the supported pipeline workflow."
    },
    wholeAssembledCaseOnly: true,
    explodeEligible: false,
    toyPrizeBundled: false,
    shippingEligible: false,
    reviewState: "supporting-evidence"
  });
}

manifest.claims.push({
  id: "premium-display-case-gate04-rev9-technical-rejection-claim-r010",
  stageId: "04-architecture",
  topic: "gate04-rev9-visual-technical-rejection",
  statement:
    "Gate 04 rev 9 is technically rejected: its seal reads as a rigid lid, its tear edge lacks foil construction, its case continuity changes apparent identity and scale, and its muddy background/impact reads as an effects demo.",
  confidence: "user-authoritative-parent-visual-inspection",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: [rejectionId],
  sourceRegions: [],
  decisionState: "locked-technical-rejection",
  deliveryState: "rev9-immutable-technical-rejected-history"
});

const decidedAt = new Date().toISOString();
const eventId = crypto.randomUUID();
gate04.revision += 1;
gate04.status = "rejected";
gate04.artifactIds = definitions.map(([id]) => id);
gate04.reviewArtifactIds = [];
gate04.validations = [
  {
    id: "rev9-rejection-reasons-preserved",
    status: "pass",
    evidence: rejectionPath
  },
  {
    id: "rev8-and-rev9-artifacts-preserved",
    status: "pass",
    evidence:
      "Gate 04 rev 8 and rev 9 stage snapshots remain in historicalRevisions; all rev 9 artifacts are technical-rejected history."
  },
  {
    id: "rev9-approval-review-disabled",
    status: "pass",
    evidence: rejectionPath
  }
];
gate04.decision = {
  action: "reject",
  notes:
    "Parent visual inspection technically rejects Gate 04 rev 9. Do not show it for approval.",
  decidedBy: "parent-visual-inspection-authorized-by-user",
  decidedAt,
  rejectionReasons: reasons,
  approvalRequestAllowed: false,
  finalAuthority: "latest-explicit-chat-instruction"
};
gate04.architectureSpec = {
  ...gate04.architectureSpec,
  decisionState: "gate04-rev9-technical-rejected",
  deliveryState: "rev10-real-unity-candidate-in-progress",
  rejectedEvidenceRevision: 9,
  rejectedEvidenceRevisions: [8, 9],
  rejectionEventId: eventId,
  nextArchitectureRevision: 6,
  nextEvidenceRevision: 10,
  rejectionReasons: reasons,
  approvalRequestAllowed: false,
  shippingRuntimeWired: false,
  nativeUiWired: false,
  shippingReady: false,
  physicalPhoneInstalled: false,
  gate05Status: "stale-awaiting-gate04-rev10-review"
};

for (let index = 4; index < manifest.stages.length; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason =
    "Gate 04 rev 9 was technically rejected. Gate 05–12 remain stale until a corrected real Unity Gate 04 revision receives explicit approval.";
}

manifest.currentState.rebuildRequested = true;
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.visualApproval =
  "gate04-rev9-technical-rejected-rev10-unity-candidate-in-progress";
manifest.currentState.deviceStatus =
  "not-built-not-installed-physical-device-pending";
manifest.currentState.diagnosis =
  "Gate 04 rev 9 is technical-rejected and must not be shown for approval. Its rigid lid, cartoon sawtooth, false case continuity, and muddy effects-demo presentation remain immutable history. Rev 10 must use real deformable foil geometry, one constant-scale case instance, physical pack occlusion, and the shipping dark mineral environment.";
manifest.currentState.motionCorrection = {
  earliestGate: "04-architecture",
  gate04Status: "rev9-technical-rejected-rev10-in-progress",
  rejectedArchitectureRevision: 5,
  rejectedEvidenceRevision: 9,
  rejectedEvidenceRevisions: [8, 9],
  rejectionEventId: eventId,
  nextArchitectureRevision: 6,
  nextEvidenceRevision: 10,
  downstreamStaleGates: manifest.stages.slice(4).map((stage) => stage.id),
  shippingPreviewApproved: false,
  deviceAccepted: false
};
manifest.currentState.architectureApproval = {
  stageId: "04-architecture",
  architectureRevision: 5,
  evidenceRevision: 9,
  userApprovalQuote: null,
  decisionState: "technical-rejected",
  approvalRequestAllowed: false,
  gate05Status: "stale"
};
manifest.model.status = "gate04-rev9-technical-rejected-rev10-in-progress";

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
manifest.updatedAt = decidedAt;
const event = {
  id: eventId,
  type: "stage-rejected",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "04-architecture",
  architectureRevision: 5,
  evidenceRevision: 9,
  reviewAuthority: "parent-visual-inspection",
  sourceThread,
  sourceTask,
  rejectionReasons: reasons,
  approvalRequestAllowed: false,
  disposition: "technical-rejected-preserved",
  nextState: "gate04-rev10-real-unity-candidate-in-progress",
  staleGateIds: manifest.stages.slice(4).map((stage) => stage.id),
  shippingRuntimeWired: false,
  nativeUiWired: false,
  shippingReady: false,
  physicalPhoneInstalled: false,
  deviceAccepted: false,
  statusText:
    "Gate 04 rev 9 已技术否决且不得送审；rev 10 真实 Unity 候选制作中，未推送手机"
};

const result = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: result.revision,
  approvedCount: result.derived.approvedCount,
  shippingReady: result.derived.shippingReady,
  earliestProblem: result.derived.earliestProblem,
  eventId
}, null, 2));
