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
  `${projectRoot}/ArtSource/ModelPipeline/${modelId}/evidence/04-architecture/rev-008`;
const candidateRoot =
  `${projectRoot}/Assets/_DisplayCase/Candidates/PackOpeningGate04R008`;
const manifest = loadManifest(modelId);

if (!Number.isInteger(expectedRevision) || expectedRevision !== manifest.revision) {
  throw new Error(
    `Manifest revision conflict: expected ${expectedRevision}, actual ${manifest.revision}.`
  );
}
if (
  manifest.stages[2].status !== "approved"
  || manifest.stages[3].status !== "approved"
  || manifest.stages[11].status !== "ready_for_review"
  || manifest.stages[11].shippingSpec?.revision !== 4
) {
  throw new Error("Expected approved Gate 03/04 and Gate 12 rev 4 ready for review.");
}

const architecture = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/architecture.json`), "utf8")
);
const validation = JSON.parse(
  fs.readFileSync(
    resolveRepoPath(`${evidenceRoot}/architecture-validation.json`),
    "utf8"
  )
);
const compatibility = JSON.parse(
  fs.readFileSync(
    resolveRepoPath(`${evidenceRoot}/compatibility-provenance-audit.json`),
    "utf8"
  )
);
const textures = JSON.parse(
  fs.readFileSync(
    resolveRepoPath(`${evidenceRoot}/candidate-texture-manifest.json`),
    "utf8"
  )
);
if (
  architecture.status !== "ready_for_review"
  || validation.status !== "pass"
  || compatibility.earliestAffectedGate !== "04-architecture"
  || textures.conceptualRows !== 7
  || textures.physicalFiles !== 10
) {
  throw new Error("Gate 04 rev 8 evidence does not pass its registration contract.");
}

const gate04 = manifest.stages[3];
const shipping = manifest.stages[11];
const oldGate04 = {
  architectureSpec: structuredClone(gate04.architectureSpec),
  artifactIds: [...gate04.artifactIds],
  reviewArtifactIds: [...gate04.reviewArtifactIds],
  validations: structuredClone(gate04.validations),
  decision: structuredClone(gate04.decision),
  stageStatus: gate04.status,
  preservedForHistory: true,
  disposition: "superseded-by-pack-opening-gate04-r008"
};
const oldShipping = {
  shippingSpec: structuredClone(shipping.shippingSpec),
  artifactIds: [...shipping.artifactIds],
  reviewArtifactIds: [...shipping.reviewArtifactIds],
  validations: structuredClone(shipping.validations),
  decision: structuredClone(shipping.decision),
  stageStatus: "rejected",
  preservedForHistory: true,
  rejection: {
    rejectedRevision: 4,
    reason: "Pack Opening 动效重构 supersedes the two-loop 720-degree showcase, prior Pack handoff, neutral-only rarity treatment, and static camera assumptions.",
    finalAuthority: "chat",
    userEngineChoice: "使用现有 Unity 6.5 工程实施（推荐）",
    sourceTask: "43ca0cec-1fb6-43dc-b651-2418c0df3ddf"
  }
};

const definitions = [
  ["premium-display-case-pack-opening-direction-r008", "user-direction", `${evidenceRoot}/user-pack-opening-direction.md`, "user-input"],
  ["premium-display-case-pack-opening-compatibility-r008", "compatibility-audit", `${evidenceRoot}/compatibility-provenance-audit.json`, "validation"],
  ["premium-display-case-pack-opening-generator-r008", "architecture-generator", `${evidenceRoot}/generate_epic_timing_prototype.py`, "process"],
  ["premium-display-case-pack-opening-register-r008", "architecture-registration", `${evidenceRoot}/register_gate04_rev8.mjs`, "process"],
  ["premium-display-case-pack-opening-profile-source-r008", "architecture-runtime-source", `${candidateRoot}/Runtime/PackOpeningEpicTimingProfile.cs`, "process"],
  ["premium-display-case-pack-opening-tests-source-r008", "architecture-test-source", `${candidateRoot}/Tests/Editor/PackOpeningEpicTimingProfileTests.cs`, "process"],
  ["premium-display-case-pack-opening-architecture-r008", "architecture-plan", `${evidenceRoot}/architecture.json`, "process"],
  ["premium-display-case-pack-opening-validation-r008", "architecture-validation", `${evidenceRoot}/architecture-validation.json`, "validation"],
  ["premium-display-case-pack-opening-video-r008", "architecture-recording", `${evidenceRoot}/epic-profile-timing-impact-prototype.mp4`, "process"],
  ["premium-display-case-pack-opening-impact-gif-r008", "architecture-animation", `${evidenceRoot}/epic-impact-1700-1950ms.gif`, "process"],
  ["premium-display-case-pack-opening-impact-contact-r008", "architecture-contact-sheet", `${evidenceRoot}/epic-impact-1700-1950ms-contact-sheet.png`, "validation"],
  ["premium-display-case-pack-opening-signalstats-r008", "architecture-signalstats", `${evidenceRoot}/signalstats-report.json`, "validation"],
  ["premium-display-case-pack-opening-texture-manifest-r008", "texture-manifest", `${evidenceRoot}/candidate-texture-manifest.json`, "validation"],
  ...textures.entries.map((entry, index) => [
    `premium-display-case-pack-opening-texture-${String(index + 1).padStart(2, "0")}-r008`,
    "candidate-texture",
    entry.path,
    "process"
  ])
];

for (const [id, , assetPath] of definitions) {
  if (manifest.assets.some((asset) => asset.id === id)) {
    throw new Error(`Asset already registered: ${id}`);
  }
  const absolute = resolveRepoPath(assetPath);
  if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
    throw new Error(`Missing Gate 04 rev 8 asset: ${assetPath}`);
  }
}

const sourceDirectionId = "premium-display-case-pack-opening-direction-r008";
const contractId = "premium-display-case-modeling-contract-r003";
const sourceIds = [
  sourceDirectionId,
  contractId,
  "premium-display-case-shipping-hero-r004",
  "premium-display-case-shipping-native-pack-rules-r004"
];
manifest.assets.push(
  ...definitions.map(([id, slot, assetPath, role]) => {
    const absolute = resolveRepoPath(assetPath);
    const isUserInput = id === sourceDirectionId;
    return {
      id,
      stageId: "04-architecture",
      slot,
      path: normalizeRepoPath(assetPath),
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role,
      sourceAssetIds: isUserInput ? [] : sourceIds,
      sourceClaimIds: [],
      producer: {
        name: assetPath.includes("/Assets/")
          ? "Unity 6000.5 architecture candidate"
          : "fidgeting-model-pipeline",
        version: "2026-08-28",
        recipe: "pack-opening-gate04-r008"
      },
      provenance: {
        origin: isUserInput ? "user-provided" : "repository-generated",
        contentClass: slot,
        assertedBy: isUserInput ? "user" : "assistant",
        note:
          "Gate 04 candidate evidence only. Visual approval, shipping wiring, final materials, and device acceptance remain pending."
      },
      wholeAssembledCaseOnly: true,
      explodeEligible: false,
      toyPrizeBundled: false,
      shippingEligible: false,
      reviewState: ["architecture-recording", "architecture-animation", "architecture-contact-sheet"].includes(slot)
        ? "ready-for-review"
        : "supporting-evidence"
    };
  })
);

for (const assetId of oldGate04.artifactIds) {
  const asset = manifest.assets.find((candidate) => candidate.id === assetId);
  if (!asset) continue;
  asset.reviewState = "superseded-history";
  asset.preservedForHistory = true;
}
for (const assetId of oldShipping.artifactIds) {
  const asset = manifest.assets.find((candidate) => candidate.id === assetId);
  if (!asset) continue;
  asset.reviewState = "rejected-history";
  asset.preservedForHistory = true;
  asset.rejectedShippingRevision = 4;
  asset.supersededByArchitectureEvidenceRevision = 8;
}

manifest.claims.push({
  id: "premium-display-case-pack-opening-direction-claim-r008",
  stageId: "04-architecture",
  topic: "pack-opening-epic-timing-impact-architecture",
  statement:
    "Use the canonical Unity 6000.5.6f1 project for a 3.1-second profile-driven Pack opening sequence with progressive tear, a 180 ms layered impact, one -25-to-0-degree assembled-case settle, and staged native CTA. Preserve exact-once transaction and whole-case ContentSlot boundaries.",
  confidence: "user-authoritative",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: [sourceDirectionId],
  sourceRegions: [],
  decisionState: "current-direction-gate04-visual-pending",
  deliveryState: "candidate-profile-and-complete-recording"
});

gate04.historicalRevisions = [
  ...(gate04.historicalRevisions || []),
  oldGate04
];
gate04.revision += 1;
gate04.status = "ready_for_review";
gate04.artifactIds = [
  ...definitions.map(([id]) => id),
  "premium-display-case-part-tree-internal-r005",
  "premium-display-case-exploded-plan-internal-r005"
];
gate04.reviewArtifactIds = [
  "premium-display-case-pack-opening-video-r008",
  "premium-display-case-pack-opening-impact-gif-r008",
  "premium-display-case-pack-opening-impact-contact-r008"
];
gate04.validations = Object.entries(validation.checks).map(([id, passed]) => ({
  id,
  status: passed ? "pass" : "fail",
  evidence: `${evidenceRoot}/architecture-validation.json`
}));
gate04.decision = {
  action: "pending",
  notes:
    "Pack Opening Gate 04 rev 8 complete-recording evidence is ready. No unseen visual is approved.",
  decidedBy: null,
  decidedAt: null
};
gate04.architectureSpec = {
  revision: 4,
  evidenceRevision: 8,
  sourceContractRevision: 3,
  sourceTask: "43ca0cec-1fb6-43dc-b651-2418c0df3ddf",
  decisionState: "current-direction-gate04-visual-pending",
  deliveryState: "candidate-profile-and-complete-recording",
  engine: architecture.engine,
  profile: architecture.profile,
  packDisplayTier: architecture.packDisplayTier,
  phaseWindows: architecture.phases,
  ownership: architecture.ownership,
  invariants: architecture.invariants,
  effectStack: architecture.effectStack,
  reduceMotion: architecture.reduceMotion,
  rarityProfiles: architecture.rarityProfiles,
  packDisplayAssets: architecture.packDisplayAssets,
  orchestration: architecture.orchestration,
  textureManifest: architecture.textureManifest,
  textureRows: textures.conceptualRows,
  texturePhysicalFiles: textures.physicalFiles,
  maxSimultaneousMovingLayers:
    validation.metrics.maxSimultaneousMovingLayers,
  reviewMode: "complete-recording-fallback",
  reviewArtifactIds: [...gate04.reviewArtifactIds],
  internalArtifactIds: [
    "premium-display-case-part-tree-internal-r005",
    "premium-display-case-exploded-plan-internal-r005"
  ],
  shippingRuntimeWired: false,
  nativeUiWired: false,
  finalMaterialsDelivered: false,
  gate05Status: "stale-awaiting-gate04-approval"
};

shipping.historicalRevisions = [
  ...(shipping.historicalRevisions || []),
  oldShipping
];
shipping.historicalDecisions = [
  ...(shipping.historicalDecisions || []),
  {
    action: "reject",
    notes: oldShipping.rejection.reason,
    decidedBy: "user",
    decidedAt: new Date().toISOString(),
    shippingRevision: 4,
    finalAuthority: "chat",
    sourceTask: oldShipping.rejection.sourceTask,
    preservedForHistory: true
  }
];
shipping.shippingSpec = {
  ...shipping.shippingSpec,
  rejection: oldShipping.rejection,
  currentDirection: "superseded-by-pack-opening-gate04-r008",
  visualApproved: false
};

for (let index = 4; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  stage.status = "stale";
  stage.staleReason =
    "Pack Opening 动效重构 changes motion architecture, Pack tear, case material response, lighting, environment, camera, rarity language, Haptics, shipping presentation, and native settle UI from Gate 04.";
}

manifest.currentState.rebuildRequested = true;
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.visualApproval = "gate04-rev8-pack-opening-review-pending";
manifest.currentState.deviceStatus = "not-built-not-installed-physical-device-pending";
manifest.currentState.diagnosis =
  "Gate 12 rev 4 is rejected and preserved. Gate 04 rev 8 now holds the canonical Unity 6.5 Pack Opening direction and complete Epic timing/impact recording. Gates 05-12 are stale. Shipping wiring and visual approval remain pending.";
manifest.currentState.motionCorrection = {
  earliestGate: "04-architecture",
  gate04Status: "ready-for-review-rev8",
  gate04ArchitectureRevision: 4,
  evidenceRevision: 8,
  gate12Rev4Disposition: "rejected-history-preserved",
  downstreamStaleGates: manifest.stages.slice(4).map((stage) => stage.id),
  shippingPreviewApproved: false,
  deviceAccepted: false
};
manifest.currentState.architectureApproval = {
  stageId: "04-architecture",
  architectureRevision: 4,
  evidenceRevision: 8,
  userApprovalQuote: null,
  decisionState: "pending-visual-review",
  gate05Status: "blocked"
};
manifest.model.status = "gate04-pack-opening-visual-review-pending";

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
  architectureRevision: 4,
  evidenceRevision: 8,
  sourceTask: "43ca0cec-1fb6-43dc-b651-2418c0df3ddf",
  exactEngineChoice: "使用现有 Unity 6.5 工程实施（推荐）",
  rejectedShippingRevision: 4,
  preservedShippingRevisions: [1, 2, 3, 4],
  earliestInvalidatedGate: "04-architecture",
  staleGateIds: manifest.stages.slice(4).map((stage) => stage.id),
  reviewArtifactIds: gate04.reviewArtifactIds,
  timingMilliseconds: architecture.phases,
  maxSimultaneousMovingLayers:
    validation.metrics.maxSimultaneousMovingLayers,
  textureRows: textures.conceptualRows,
  texturePhysicalFiles: textures.physicalFiles,
  shippingRuntimeWired: false,
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
