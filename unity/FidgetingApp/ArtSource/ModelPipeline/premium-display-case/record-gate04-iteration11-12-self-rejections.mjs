#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import { fileURLToPath } from "node:url";
import {
  digestValues,
  loadManifest,
  resolveRepoPath,
  saveManifest,
  sha256File
} from "../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const root = path.dirname(fileURLToPath(import.meta.url));
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-011";
const expectedRevision = 89;
const now = new Date().toISOString();

function requireFile(relativePath) {
  const absolutePath = resolveRepoPath(relativePath);
  if (!fs.existsSync(absolutePath) || !fs.statSync(absolutePath).isFile()) {
    throw new Error(`Missing evidence: ${relativePath}`);
  }
  return absolutePath;
}

function createAsset(
  manifest,
  id,
  relativePath,
  role,
  note,
  reviewState = "rejected"
) {
  const absolutePath = requireFile(relativePath);
  const sourceStage = manifest.stages.find(
    (stage) => stage.id === "03-contract"
  );
  const sourceAssetIds = sourceStage?.artifactIds || [];
  const sourceClaimIds = sourceAssetIds.flatMap((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sourceClaimIds || []
  );
  return {
    id,
    stageId: "04-architecture",
    slot: "architecture-implementation-evidence",
    path: relativePath,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role,
    producer: {
      name: "Unity 6000.5.6f1 batchmode PackOpeningGate04R011Builder.BuildAndRunCapture",
      version: "capture-i12",
      recipe: "gate04-rev011-cc0-reuse-retarget"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: "architecture-implementation-evidence",
      assertedBy: "repository",
      note
    },
    sourceAssetIds,
    sourceClaimIds: [...new Set(sourceClaimIds)],
    wholeAssembledCaseOnly: true,
    explodeEligible: false,
    toyPrizeBundled: false,
    shippingEligible: false,
    reviewState
  };
}

function addAssets(manifest, stage, records) {
  const existing = new Set(manifest.assets.map((asset) => asset.id));
  const added = [];
  for (const record of records) {
    if (existing.has(record.id)) continue;
    manifest.assets.push(record);
    stage.artifactIds.push(record.id);
    added.push(record.id);
  }
  stage.artifactIds = [...new Set(stage.artifactIds)];
  return added;
}

function updateStageDigest(manifest, stage) {
  const stageIndex = manifest.stages.indexOf(stage);
  const hashes = stage.artifactIds
    .map((assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256)
    .filter(Boolean);
  stage.inputDigest = stageIndex === 0
    ? digestValues(hashes)
    : manifest.stages[stageIndex - 1].outputDigest;
  stage.outputDigest = digestValues(hashes);
  if (stageIndex + 1 < manifest.stages.length) {
    manifest.stages[stageIndex + 1].inputDigest = stage.outputDigest;
  }
}

const manifest = loadManifest("premium-display-case");
if (manifest.revision !== expectedRevision) {
  throw new Error(
    `Expected pipeline revision ${expectedRevision}; found ${manifest.revision}.`
  );
}

const stage = manifest.stages.find(
  (candidate) => candidate.id === "04-architecture"
);
if (!stage) throw new Error("Gate 04 is missing.");

const artifacts = [
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i11-self-rejection",
    `${evidenceRoot}/iterations/iteration-11/self-rejection.json`,
    "validation",
    "Iteration 11 full-size visual self-rejection."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i11-capture-report",
    `${evidenceRoot}/iterations/iteration-11/unity-capture-report.json`,
    "validation",
    "Iteration 11 real Unity capture metrics."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i11-tear-contact",
    `${evidenceRoot}/iterations/iteration-11/tear-contact-sheet.png`,
    "shipping-render",
    "Iteration 11 rejected primary tear sheet."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i12-self-rejection",
    `${evidenceRoot}/iterations/iteration-12/self-rejection.json`,
    "validation",
    "Iteration 12 full-size visual self-rejection."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i12-source-manifest",
    `${evidenceRoot}/iterations/iteration-12/unity-source-manifest.json`,
    "validation",
    "Iteration 12 source, object-count and engine contract."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i12-source-mapping",
    `${evidenceRoot}/iterations/iteration-12/source-to-canonical-mapping.json`,
    "validation",
    "Iteration 12 CC0 direct-copy, adaptation and rejection map."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i12-capture-report",
    `${evidenceRoot}/iterations/iteration-12/unity-capture-report.json`,
    "validation",
    "Iteration 12 real Unity 1206x2622, 60 fps capture metrics."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i12-tear-contact",
    `${evidenceRoot}/iterations/iteration-12/tear-contact-sheet.png`,
    "shipping-render",
    "Iteration 12 rejected primary tear sheet."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i12-impact-contact",
    `${evidenceRoot}/iterations/iteration-12/source-impact-contact-sheet.png`,
    "shipping-render",
    "Iteration 12 rejected primary impact and reveal sheet."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i12-continuity-contact",
    `${evidenceRoot}/iterations/iteration-12/continuity-contact-sheet.png`,
    "shipping-render",
    "Iteration 12 rejected primary continuity sheet."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i12-source-target",
    `${evidenceRoot}/iterations/iteration-12/source-target-side-by-side.png`,
    "shipping-render",
    "Iteration 12 rejected matched source-to-target sheet."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i12-matched-timestamps",
    `${evidenceRoot}/iterations/iteration-12/matched-timestamps.json`,
    "validation",
    "Iteration 12 source-to-target timestamp pairs."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i12-normal-speed",
    `${evidenceRoot}/iterations/iteration-12/normal-speed-sequence.mp4`,
    "shipping-render",
    "Iteration 12 normal-speed video encoded only from captured Unity frames."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i12-tear-quarter-speed",
    `${evidenceRoot}/iterations/iteration-12/tear-quarter-speed-closeup.mp4`,
    "shipping-render",
    "Iteration 12 0.25x tear video encoded only from captured Unity frames."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i12-impact-quarter-speed",
    `${evidenceRoot}/iterations/iteration-12/impact-reveal-quarter-speed.mp4`,
    "shipping-render",
    "Iteration 12 0.25x impact video encoded only from captured Unity frames."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r011-i12-technical-continuity",
    `${evidenceRoot}/iterations/iteration-12/technical-continuity-sheet.svg`,
    "validation",
    "Separate technical sheet with case ID, projected bounds and occlusion."
  )
];

const addedAssetIds = addAssets(manifest, stage, artifacts);
stage.historicalDecisions = [
  ...(stage.historicalDecisions || []),
  {
    revision: stage.revision,
    status: stage.status,
    decision: stage.decision,
    evidenceReview: stage.evidenceReview,
    supersededBy: "gate04-rev011-iteration11-self-rejection",
    supersededAt: now
  },
  {
    evidenceRevision: 11,
    evidenceIteration: 11,
    action: "self-reject",
    decidedBy: "agent-full-size-frame-inspection",
    decidedAt: now,
    selfRejectionRecord:
      `${evidenceRoot}/iterations/iteration-11/self-rejection.json`,
    approvalRequestAllowed: false
  },
  {
    evidenceRevision: 11,
    evidenceIteration: 12,
    action: "self-reject",
    decidedBy: "agent-full-size-frame-inspection",
    decidedAt: now,
    selfRejectionRecord:
      `${evidenceRoot}/iterations/iteration-12/self-rejection.json`,
    approvalRequestAllowed: false
  }
];
stage.revision += 1;
stage.status = "draft";
stage.reviewArtifactIds = [];
stage.validations = [
  {
    id: "rev8-and-rev9-artifacts-preserved",
    status: "pass",
    evidence: "Gate 04 rev 8 and rev 9 remain immutable rejected history."
  },
  {
    id: "iteration11-full-size-visual-review",
    status: "fail",
    evidence: `${evidenceRoot}/iterations/iteration-11/self-rejection.json`
  },
  {
    id: "iteration12-full-size-visual-review",
    status: "fail",
    evidence: `${evidenceRoot}/iterations/iteration-12/self-rejection.json`
  },
  {
    id: "iteration12-real-unity-capture",
    status: "pass",
    evidence: `${evidenceRoot}/iterations/iteration-12/unity-capture-report.json`
  },
  {
    id: "iteration12-focused-unity-tests",
    status: "pass",
    evidence: "unity/FidgetingApp/Logs/PackOpeningGate04R011Results-i12fix.xml (36/36)"
  },
  {
    id: "iteration12-primary-media-encoded-from-unity-frames",
    status: "pass",
    evidence: `${evidenceRoot}/iterations/iteration-12/normal-speed-sequence.mp4, tear-quarter-speed-closeup.mp4, impact-reveal-quarter-speed.mp4`
  },
  {
    id: "shipping-ready-remains-false",
    status: "pass",
    evidence: "shippingRuntimeWired=false, shippingReady=false, physicalPhoneInstalled=false."
  }
];
stage.decision = {
  action: "self-reject",
  notes: "Iteration 11 and the single iteration-12 correction fail full-size visual review. Gate 04 cannot request user approval.",
  decidedAt: now,
  decidedBy: "agent-full-size-frame-inspection",
  approvalRequestAllowed: false,
  finalAuthority: "latest-explicit-chat-instruction",
  selfRejectionRecords: [
    `${evidenceRoot}/iterations/iteration-11/self-rejection.json`,
    `${evidenceRoot}/iterations/iteration-12/self-rejection.json`
  ]
};
stage.evidenceReview = {
  iteration: 12,
  disposition: "self-rejected",
  selfRejectedIterations: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12],
  shownToUserForApproval: false,
  visualApproval: "not-requested-self-rejected",
  statusText: "视觉批准待确认，未推送手机"
};

for (const downstream of manifest.stages.slice(4)) {
  downstream.status = "stale";
  downstream.staleReason =
    "Gate 04 iteration 12 is self-rejected; no downstream gate may advance.";
}
manifest.model.status = "gate04-rev011-iteration12-self-rejected";
manifest.currentState = {
  ...manifest.currentState,
  activeStageId: "04-architecture",
  activeStageStatus: "draft",
  activeIteration: 12,
  visualApproval:
    "gate04-rev011-iteration12-self-rejected-user-correction-required",
  diagnosis:
    "Iteration 11 and the single corrective iteration 12 are self-rejected after full-size inspection. The current mouth is too slit-like, the foil reads as stepped trim, and source flares are not recognizable. Gate 04 remains draft.",
  blockoutCompatibility: {
    ...manifest.currentState.blockoutCompatibility,
    gate05Status: "stale"
  },
  geometryRevalidation: {
    ...manifest.currentState.geometryRevalidation,
    gate06Status: "stale"
  },
  materialRevalidation: {
    ...manifest.currentState.materialRevalidation,
    gate07Status: "stale"
  },
  lightingRevalidation: {
    ...manifest.currentState.lightingRevalidation,
    gate08Status: "stale"
  },
  environmentRevalidation: {
    ...manifest.currentState.environmentRevalidation,
    gate09Status: "stale"
  },
  exportReview: {
    ...manifest.currentState.exportReview,
    gate10Status: "stale"
  },
  unityParity: {
    ...manifest.currentState.unityParity,
    gate11Status: "stale"
  },
  shippingPreview: {
    ...manifest.currentState.shippingPreview,
    gate12Status: "stale",
    shippingReady: false,
    visualApproved: false,
    physicalPhoneInstalled: false,
    deviceAccepted: false
  },
  motionCorrection: {
    ...manifest.currentState.motionCorrection,
    gate04Status: "rev011-iteration12-self-rejected-user-correction-required",
    currentEvidenceIteration: 12,
    selfRejectedIterations: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
  },
  architectureApproval: {
    stageId: "04-architecture",
    architectureRevision: 6,
    evidenceRevision: 11,
    evidenceIteration: 12,
    userApprovalQuote: null,
    decisionState: "self-rejected-user-correction-required",
    approvalRequestAllowed: false,
    gate05Status: "stale"
  },
  summary:
    "Gate 04 rev 011 iteration 12 is self-rejected. New user visual direction is required.",
  statusText: "视觉批准待确认，未推送手机"
};
manifest.revision += 1;
manifest.updatedAt = now;
updateStageDigest(manifest, stage);

const event = {
  id: crypto.randomUUID(),
  type: "iterations-self-rejected",
  modelId: "premium-display-case",
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "04-architecture",
  stageRevision: stage.revision,
  evidenceRevision: 11,
  evidenceIterations: [11, 12],
  addedAssetIds,
  selfRejectionRecords: stage.decision.selfRejectionRecords,
  approvalRequestAllowed: false,
  shippingReady: false,
  physicalPhoneInstalled: false,
  deviceAccepted: false,
  statusText: "视觉批准待确认，未推送手机"
};

saveManifest(manifest, event);
console.log(JSON.stringify({
  pipelineRevision: manifest.revision,
  stageRevision: stage.revision,
  stageStatus: stage.status,
  addedAssets: addedAssetIds.length
}, null, 2));
