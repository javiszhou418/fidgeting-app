#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import crypto from "node:crypto";
import {
  digestValues,
  loadManifest,
  resolveRepoPath,
  saveManifest,
  sha256File
} from "../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const expectedRevision = 90;
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-012";
const candidateRoot =
  "unity/FidgetingApp/Assets/_DisplayCase/Candidates/PackOpeningGate04R012";
const now = new Date().toISOString();

function requireFile(relativePath) {
  const absolutePath = resolveRepoPath(relativePath);
  if (!fs.existsSync(absolutePath) || !fs.statSync(absolutePath).isFile()) {
    throw new Error(`Missing R012 evidence: ${relativePath}`);
  }
  return absolutePath;
}

function createAsset(
  manifest,
  id,
  relativePath,
  slot,
  role,
  note
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
    slot,
    path: relativePath,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role,
    producer: {
      name: "Unity 6000.5.6f1 PackOpeningGate04R012Builder",
      version: "physical-tear-r012",
      recipe:
        "actual Unity physical mouth, fine segmented tear, direct CC0 effect adapter"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: "gate04-self-rejected-real-unity-candidate",
      assertedBy: "repository",
      note
    },
    sourceAssetIds,
    sourceClaimIds: [...new Set(sourceClaimIds)],
    wholeAssembledCaseOnly: true,
    explodeEligible: false,
    toyPrizeBundled: false,
    shippingEligible: false,
    reviewState: "rejected"
  };
}

function addAssets(manifest, stage, records) {
  const existing = new Set(manifest.assets.map((asset) => asset.id));
  const added = [];
  for (const record of records) {
    if (existing.has(record.id)) {
      continue;
    }
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
const stage = manifest.stages.find((item) => item.id === "04-architecture");
if (!stage || stage.revision !== 23 || stage.status !== "draft") {
  throw new Error("Gate 04 is not the expected R011 self-rejected draft.");
}

const artifacts = [
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-profile",
    `${candidateRoot}/Runtime/PackOpeningGate04R012Profile.cs`,
    "architecture-profile-source",
    "process",
    "R012 profile preserves the source discard curve and physical tear timing."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-sequence",
    `${candidateRoot}/Runtime/PackOpeningGate04R012Sequence.cs`,
    "architecture-runtime-source",
    "process",
    "R012 Unity Mesh API implementation owns fine tear segments, physical mouth, strip and case continuity."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-capture-source",
    `${candidateRoot}/Runtime/PackOpeningGate04R012Capture.cs`,
    "architecture-capture-source",
    "process",
    "R012 capture writes actual Unity camera frames and separates diagnostics from primary media."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-builder",
    `${candidateRoot}/Editor/PackOpeningGate04R012Builder.cs`,
    "architecture-unity-builder",
    "process",
    "R012 builder verifies direct CC0 hashes and instantiates one real case."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-pack-shader",
    `${candidateRoot}/Shaders/MakeItShineCc0PackR012.shader`,
    "architecture-shader-source",
    "process",
    "R012 retargets the source discard edge to the physical torn contour."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-port-shader",
    `${candidateRoot}/Shaders/MakeItShineCc0PortR012.shader`,
    "architecture-shader-source",
    "process",
    "R012 ports source Sphere Mask and Lighting Strike appearance to Shuriken."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-tests",
    `${candidateRoot}/Tests/Editor/PackOpeningGate04R012Tests.cs`,
    "architecture-test-source",
    "process",
    "Focused tests cover physical mouth, strip, continuity, direct source hashes and reduced motion."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-scene",
    `${candidateRoot}/Scenes/PackOpeningGate04R012.unity`,
    "architecture-unity-scene",
    "process",
    "Actual canonical Unity scene captured for the rejected R012 candidate."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-source-map",
    `${evidenceRoot}/source-to-canonical-mapping.json`,
    "architecture-source-mapping",
    "validation",
    "Direct-copy, adapted and rejected CC0 source mapping with hashes."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-source-manifest",
    `${evidenceRoot}/unity-source-manifest.json`,
    "architecture-source-manifest",
    "validation",
    "Engine, product assets, physical mouth and no-VFX-Graph contract."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-capture-report",
    `${evidenceRoot}/unity-capture-report.json`,
    "architecture-capture-report",
    "validation",
    "Actual Unity 1206x2622, 60 fps capture and continuity metrics."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-self-review",
    `${evidenceRoot}/self-rejection.json`,
    "architecture-full-size-review",
    "validation",
    "Full-size visual self-rejection of R012."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-primary-contact",
    `${evidenceRoot}/primary-contact-sheet.png`,
    "architecture-primary-contact-sheet",
    "shipping-render",
    "Rejected primary no-overlay Unity contact sheet."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-normal-speed",
    `${evidenceRoot}/normal-speed-sequence.mp4`,
    "architecture-normal-speed-video",
    "shipping-render",
    "Rejected normal-speed video encoded only from R012 Unity PNG frames."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-tear-quarter-speed",
    `${evidenceRoot}/tear-quarter-speed-closeup.mp4`,
    "architecture-tear-quarter-video",
    "shipping-render",
    "Rejected 0.25x tear close-up encoded only from R012 Unity PNG frames."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-impact-quarter-speed",
    `${evidenceRoot}/impact-reveal-quarter-speed.mp4`,
    "architecture-impact-quarter-video",
    "shipping-render",
    "Rejected 0.25x impact and reveal encoded only from R012 Unity PNG frames."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-continuity-contact",
    `${evidenceRoot}/continuity-contact-sheet.png`,
    "architecture-continuity-contact-sheet",
    "shipping-render",
    "Rejected supplementary Unity contact sheet for the same-case crossing."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-source-target",
    `${evidenceRoot}/source-target-side-by-side.png`,
    "architecture-source-target-comparison",
    "validation",
    "Separate matched source-to-target comparison at six CC0 effect times."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-technical-continuity",
    `${evidenceRoot}/technical-continuity-sheet.svg`,
    "architecture-continuity-diagnostics",
    "validation",
    "Separate ID, projected bounds and occlusion diagnostics."
  ),
  createAsset(
    manifest,
    "premium-display-case-gate04-r012-focused-tests",
    "unity/FidgetingApp/Logs/PackOpeningGate04R012Results-r012final.xml",
    "architecture-focused-tests",
    "validation",
    "Focused Unity EditMode tests: 12/12 passed."
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
    supersededBy: "gate04-r012-physical-tear-self-rejection",
    supersededAt: now
  }
];
stage.revision += 1;
stage.status = "draft";
stage.validations = [
  {
    id: "r011-iterations-preserved",
    status: "pass",
    evidence: "Rev 8, rev 9 and rev 11 iterations 01–12 remain immutable history."
  },
  {
    id: "r012-focused-unity-tests",
    status: "pass",
    evidence:
      "unity/FidgetingApp/Logs/PackOpeningGate04R012Results-r012final.xml (12/12)"
  },
  {
    id: "r012-real-unity-capture",
    status: "pass",
    evidence: `${evidenceRoot}/unity-capture-report.json`
  },
  {
    id: "r012-full-size-visual-review",
    status: "fail",
    evidence: `${evidenceRoot}/self-rejection.json`
  },
  {
    id: "r012-primary-media-from-unity-frames",
    status: "pass",
    evidence:
      `${evidenceRoot}/normal-speed-sequence.mp4, ${evidenceRoot}/tear-quarter-speed-closeup.mp4, ${evidenceRoot}/impact-reveal-quarter-speed.mp4`
  },
  {
    id: "r012-shipping-boundary",
    status: "pass",
    evidence:
      "shippingRuntimeWired=false, shippingReady=false, physicalPhoneInstalled=false."
  }
];
stage.decision = {
  action: "self-reject",
  notes:
    "R012 has real Unity evidence and structural passes, but full-size visual inspection rejects it. The rear wall reads as a rigid box lid, the case is not clearly inside the mouth before crossing, the strip reads as a long planar band, and the CC0 flare/sweep is not recognizable. Gate 04 cannot request user approval.",
  decidedAt: now,
  decidedBy: "agent-full-size-frame-inspection",
  approvalRequestAllowed: false,
  finalAuthority: "latest-explicit-chat-instruction",
  selfRejectionRecord: `${evidenceRoot}/self-rejection.json`
};
stage.evidenceReview = {
  architectureRevision: 7,
  evidenceRevision: 12,
  iteration: 1,
  disposition: "self-rejected",
  primaryArtifact: `${evidenceRoot}/primary-contact-sheet.png`,
  fullSizeFramesReviewed: [0, 43, 50, 55, 62, 71, 82, 96, 103, 122, 152, 186],
  shownToUserForApproval: false,
  visualApproval: "not-requested-self-rejected",
  statusText: "视觉批准待确认，未推送手机"
};
stage.reviewArtifactIds = [];

for (const downstream of manifest.stages.slice(4)) {
  downstream.status = "stale";
  downstream.staleReason =
    "Gate 04 R012 is self-rejected after full-size visual inspection.";
}
manifest.model.status = "gate04-r012-physical-tear-self-rejected";
manifest.currentState = {
  ...manifest.currentState,
  activeStageId: "04-architecture",
  activeStageStatus: "draft",
  activeIteration: 1,
  visualApproval: "gate04-r012-self-rejected-user-correction-required",
  diagnosis:
    "R012 establishes a fine physical tear mesh but fails visual review: rigid-lid mouth, unreadable inside case, planar strip and weak source sweep.",
  architectureApproval: {
    stageId: "04-architecture",
    architectureRevision: 7,
    evidenceRevision: 12,
    evidenceIteration: 1,
    userApprovalQuote: null,
    decisionState: "self-rejected-user-correction-required",
    approvalRequestAllowed: false,
    gate05Status: "stale"
  },
  motionCorrection: {
    ...manifest.currentState.motionCorrection,
    gate04Status: "rev012-self-rejected-user-correction-required",
    currentEvidenceRevision: 12,
    currentEvidenceIteration: 1,
    selfRejectedIterations: [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, "r012-1"]
  },
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
  summary:
    "Gate 04 R012 self-rejected after full-size Unity review; no shipping or device state advanced.",
  statusText: "视觉批准待确认，未推送手机"
};
manifest.revision += 1;
manifest.updatedAt = now;
updateStageDigest(manifest, stage);

const event = {
  id: crypto.randomUUID(),
  type: "gate04-r012-physical-tear-self-rejected",
  modelId: "premium-display-case",
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "04-architecture",
  stageRevision: stage.revision,
  architectureRevision: 7,
  evidenceRevision: 12,
  evidenceIteration: 1,
  addedAssetIds,
  selfRejectionRecord: `${evidenceRoot}/self-rejection.json`,
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
