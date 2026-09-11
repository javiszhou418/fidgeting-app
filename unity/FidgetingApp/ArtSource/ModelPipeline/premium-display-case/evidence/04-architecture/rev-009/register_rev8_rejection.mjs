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
const rejectionPath = `${evidenceRoot}/user-rejection.md`;
const registrationPath = `${evidenceRoot}/register_rev8_rejection.mjs`;
const manifest = loadManifest(modelId);
const gate04 = manifest.stages[3];

if (
  !Number.isInteger(expectedRevision)
  || expectedRevision !== manifest.revision
  || gate04.status !== "ready_for_review"
  || gate04.architectureSpec?.evidenceRevision !== 8
) {
  throw new Error(
    `Gate 04 rev 8 rejection state mismatch. Expected manifest ${expectedRevision}, actual ${manifest.revision}.`
  );
}

const exactQuote = "纯纯垃圾。";
const rejectionText = fs.readFileSync(resolveRepoPath(rejectionPath), "utf8");
const quoteCount = rejectionText.split(exactQuote).length - 1;
if (quoteCount !== 2) {
  throw new Error(`Expected the exact rejection twice, found ${quoteCount}.`);
}

const definitions = [
  [
    "premium-display-case-gate04-rev8-hard-rejection-r009",
    "architecture-user-decision",
    rejectionPath,
    "user-input"
  ],
  [
    "premium-display-case-gate04-rev8-rejection-register-r009",
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
    throw new Error(`Missing rejection asset: ${assetPath}`);
  }
}

const rejectedSnapshot = {
  ...structuredClone(gate04),
  stageStatus: "rejected",
  preservedForHistory: true,
  disposition: "hard-rejected-by-user",
  exactUserQuotes: [exactQuote, exactQuote],
  rejectionCount: 2
};
gate04.historicalRevisions = [
  ...(gate04.historicalRevisions || []),
  rejectedSnapshot
];

for (const assetId of rejectedSnapshot.artifactIds) {
  const asset = manifest.assets.find((candidate) => candidate.id === assetId);
  if (!asset) continue;
  asset.reviewState = "rejected-history";
  asset.preservedForHistory = true;
  asset.rejectedEvidenceRevision = 8;
  asset.rejectionQuote = exactQuote;
}

const previousClaim = manifest.claims.find(
  (claim) => claim.id === "premium-display-case-pack-opening-direction-claim-r008"
);
if (previousClaim) {
  previousClaim.state = "rejected";
  previousClaim.decisionState = "hard-rejected-twice";
  previousClaim.deliveryState = "immutable-rejected-evidence";
}

const rejectionId = definitions[0][0];
for (const [id, slot, assetPath, role] of definitions) {
  const absolute = resolveRepoPath(assetPath);
  const isUserInput = id === rejectionId;
  manifest.assets.push({
    id,
    stageId: "04-architecture",
    slot,
    path: normalizeRepoPath(assetPath),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    sourceAssetIds: isUserInput ? [] : [rejectionId],
    sourceClaimIds: [],
    producer: {
      name: isUserInput ? "Cursor conversation" : "fidgeting-model-pipeline",
      version: isUserInput
        ? "2e7782a0-9389-4652-be92-7193ec0d5425"
        : "2026-08-28",
      recipe: "gate04-rev8-hard-rejection"
    },
    provenance: {
      origin: isUserInput ? "user-provided" : "repository-generated",
      contentClass: slot,
      assertedBy: isUserInput ? "user" : "assistant",
      note: isUserInput
        ? "The user repeated the exact hard rejection twice."
        : "Persists the exact rejection through the revision-checked pipeline workflow."
    },
    wholeAssembledCaseOnly: true,
    explodeEligible: false,
    toyPrizeBundled: false,
    shippingEligible: false,
    reviewState: "supporting-evidence"
  });
}

manifest.claims.push({
  id: "premium-display-case-gate04-rev8-hard-rejection-claim-r009",
  stageId: "04-architecture",
  topic: "gate04-rev8-visual-rejection",
  statement:
    "Gate 04 rev 8 is hard-rejected. Its noisy rectangular Pack, lavender wash, generic rings, metric-led layer stack, missing hero silhouette, and hard case pop must not return.",
  confidence: "user-authoritative",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: [rejectionId],
  sourceRegions: [],
  decisionState: "locked-rejection",
  deliveryState: "rev8-immutable-rejected-history"
});

const decidedAt = new Date().toISOString();
gate04.revision += 1;
gate04.status = "rejected";
gate04.artifactIds = definitions.map(([id]) => id);
gate04.reviewArtifactIds = [];
gate04.validations = [
  {
    id: "exact-rejection-persisted-twice",
    status: "pass",
    evidence: rejectionPath
  },
  {
    id: "rev8-artifacts-preserved",
    status: "pass",
    evidence:
      "The complete Gate 04 rev 8 stage snapshot remains in historicalRevisions and every prior artifact is marked rejected-history."
  }
];
gate04.decision = {
  action: "reject",
  notes:
    "Hard rejection. Do not reuse the rev 8 visual language or treat its metric checks as approval.",
  decidedBy: "user",
  decidedAt,
  userQuote: exactQuote,
  exactUserQuotes: [exactQuote, exactQuote],
  rejectionCount: 2,
  finalAuthority: "latest-explicit-chat-instruction"
};
gate04.architectureSpec = {
  ...gate04.architectureSpec,
  decisionState: "gate04-rev8-hard-rejected",
  deliveryState: "rev9-real-unity-candidate-in-progress",
  rejectedEvidenceRevision: 8,
  nextEvidenceRevision: 9,
  exactUserQuotes: [exactQuote, exactQuote],
  rejectionCount: 2,
  shippingRuntimeWired: false,
  nativeUiWired: false,
  finalMaterialsDelivered: false,
  gate05Status: "stale-awaiting-gate04-rev9-review"
};

for (let index = 4; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  stage.status = "stale";
  stage.staleReason =
    "Gate 04 rev 8 was hard-rejected twice. Gate 05–12 remain stale until a real Unity rev 9 architecture prototype receives explicit approval.";
}

manifest.currentState.rebuildRequested = true;
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.visualApproval =
  "gate04-rev8-hard-rejected-rev9-unity-candidate-in-progress";
manifest.currentState.deviceStatus =
  "not-built-not-installed-physical-device-pending";
manifest.currentState.diagnosis =
  "Gate 04 rev 8 is hard-rejected twice with the exact wording 纯纯垃圾。 Its noisy rectangular Pack, prolonged lavender wash, generic rings, missing hero hierarchy, and hard case pop are immutable rejected evidence. Rev 9 must be captured from real Unity. Gates 05–12 remain stale.";
manifest.currentState.motionCorrection = {
  earliestGate: "04-architecture",
  gate04Status: "rev8-hard-rejected-rev9-in-progress",
  rejectedArchitectureRevision: 4,
  rejectedEvidenceRevision: 8,
  nextArchitectureRevision: 5,
  nextEvidenceRevision: 9,
  exactUserQuotes: [exactQuote, exactQuote],
  rejectionCount: 2,
  downstreamStaleGates: manifest.stages.slice(4).map((stage) => stage.id),
  shippingPreviewApproved: false,
  deviceAccepted: false
};
manifest.currentState.architectureApproval = {
  stageId: "04-architecture",
  architectureRevision: 4,
  evidenceRevision: 8,
  userApprovalQuote: null,
  decisionState: "hard-rejected",
  gate05Status: "stale"
};
manifest.model.status = "gate04-rev8-hard-rejected-rev9-in-progress";

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
  id: crypto.randomUUID(),
  type: "stage-rejected",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "04-architecture",
  architectureRevision: 4,
  evidenceRevision: 8,
  userQuote: exactQuote,
  exactUserQuotes: [exactQuote, exactQuote],
  rejectionCount: 2,
  finalAuthority: "latest-explicit-chat-instruction",
  sourceThread: "2e7782a0-9389-4652-be92-7193ec0d5425",
  sourceTask: "11c5cd69-58c1-46b7-9d17-cead4ab73705",
  disposition: "hard-rejected-preserved",
  nextState: "gate04-rev9-real-unity-candidate-in-progress",
  staleGateIds: manifest.stages.slice(4).map((stage) => stage.id),
  shippingReady: false,
  physicalPhoneInstalled: false,
  deviceAccepted: false,
  statusText: "Gate 04 rev 8 已明确拒绝；rev 9 真实 Unity 候选制作中，未推送手机"
};

const result = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: result.revision,
  approvedCount: result.derived.approvedCount,
  shippingReady: result.derived.shippingReady,
  earliestProblem: result.derived.earliestProblem,
  eventId: event.id
}, null, 2));
