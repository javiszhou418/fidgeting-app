#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  digestValues,
  loadManifest,
  resolveRepoPath,
  saveManifest,
  sha256File
} from "../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const expectedRevision = 92;
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-013";
const candidateRoot =
  "unity/FidgetingApp/Assets/_DisplayCase/Candidates/PackOpeningGate04R013";
const iterationRoot =
  `${evidenceRoot}/iterations/iteration-11-full-size-self-rejection`;
const now = new Date().toISOString();

function requireFile(relativePath) {
  const absolutePath = resolveRepoPath(relativePath);
  if (!fs.existsSync(absolutePath) || !fs.statSync(absolutePath).isFile()) {
    throw new Error(`Missing R013 evidence: ${relativePath}`);
  }
  return absolutePath;
}

function asset(manifest, id, relativePath, slot, role, note) {
  const absolutePath = requireFile(relativePath);
  const sourceStage = manifest.stages.find((stage) => stage.id === "03-contract");
  const sourceAssetIds = sourceStage?.artifactIds || [];
  const sourceClaimIds = sourceAssetIds.flatMap(
    (assetId) => manifest.assets.find((item) => item.id === assetId)?.sourceClaimIds || []
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
      name: "Gate 04 R013 Pack-only Blender candidate",
      version: "r013-iteration-11-self-rejection",
      recipe:
        "Blender relative blend shapes imported into Unity 6000.5.6f1 and captured by the real Unity Camera"
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
  const existing = new Set(manifest.assets.map((item) => item.id));
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
    .map((assetId) => manifest.assets.find((item) => item.id === assetId)?.sha256)
    .filter(Boolean);
  stage.inputDigest = manifest.stages[stageIndex - 1].outputDigest;
  stage.outputDigest = digestValues(hashes);
  manifest.stages[stageIndex + 1].inputDigest = stage.outputDigest;
}

const manifest = loadManifest("premium-display-case");
if (manifest.revision !== expectedRevision) {
  throw new Error(`Expected pipeline revision ${expectedRevision}; found ${manifest.revision}.`);
}
const stage = manifest.stages.find((item) => item.id === "04-architecture");
if (!stage || stage.revision !== 24 || stage.status !== "draft") {
  throw new Error("Gate 04 is not the expected R012 self-rejected draft.");
}

const records = [
  asset(manifest, "premium-display-case-gate04-r013-blender-builder",
    `${evidenceRoot}/build_pack_only_blender_rig.py`, "architecture-blender-builder", "process",
    "Deterministic Pack-only Blender rig source. It contains no case geometry or baked case imagery."),
  asset(manifest, "premium-display-case-gate04-r013-blend",
    `${evidenceRoot}/pack-opening-gate04-r013.blend`, "architecture-pack-only-rig", "process",
    "Actual Blender Pack-only relative shape-key rig with 96 tear columns."),
  asset(manifest, "premium-display-case-gate04-r013-rig-fbx",
    `${candidateRoot}/Imported/PackOpeningGate04R013PackOnlyRig.fbx`, "architecture-pack-only-fbx", "process",
    "Pack-only FBX imported by Unity; no Premium Display Case geometry is included."),
  asset(manifest, "premium-display-case-gate04-r013-blender-closed",
    `${evidenceRoot}/blender-rig-closed.png`, "architecture-blender-validation", "validation",
    "Real Blender closed-rig validation render."),
  asset(manifest, "premium-display-case-gate04-r013-blender-open",
    `${evidenceRoot}/blender-rig-open-075.png`, "architecture-blender-validation", "validation",
    "Real Blender open-rig validation render reviewed as rejected evidence."),
  asset(manifest, "premium-display-case-gate04-r013-profile",
    `${candidateRoot}/Runtime/PackOpeningGate04R013Profile.cs`, "architecture-profile-source", "process",
    "Normalized drag, reversible pre-commit profile and CC0 discard timing."),
  asset(manifest, "premium-display-case-gate04-r013-sequence",
    `${candidateRoot}/Runtime/PackOpeningGate04R013Sequence.cs`, "architecture-runtime-source", "process",
    "One real case, pairwise blend-shape interpolation, Pack occlusion and source-effect control."),
  asset(manifest, "premium-display-case-gate04-r013-builder",
    `${candidateRoot}/Editor/PackOpeningGate04R013Builder.cs`, "architecture-unity-builder", "process",
    "Unity scene builder imports the Pack-only rig and instantiates one real assembled case."),
  asset(manifest, "premium-display-case-gate04-r013-capture-source",
    `${candidateRoot}/Runtime/PackOpeningGate04R013Capture.cs`, "architecture-capture-source", "process",
    "Real Unity Camera capture and separate identity/bounds/occlusion diagnostics."),
  asset(manifest, "premium-display-case-gate04-r013-rig-probe",
    `${candidateRoot}/Editor/PackOpeningGate04R013RigProbe.cs`, "architecture-import-probe", "validation",
    "FBX import/blend-shape inspection source."),
  asset(manifest, "premium-display-case-gate04-r013-pack-shader",
    `${candidateRoot}/Shaders/MakeItShineCc0PackR013.shader`, "architecture-shader-source", "process",
    "Adapted CC0 SG_BoosterPack discard edge constrained to Pack geometry."),
  asset(manifest, "premium-display-case-gate04-r013-rim-shader",
    `${candidateRoot}/Shaders/MakeItShineCc0ContourRimR013.shader`, "architecture-shader-source", "process",
    "Adapted CC0 SG_Title_Kyle sphere-mask torn-contour rim."),
  asset(manifest, "premium-display-case-gate04-r013-port-shader",
    `${candidateRoot}/Shaders/MakeItShineCc0PortR013.shader`, "architecture-shader-source", "process",
    "Adapted CC0 SG_LightingStrike Shuriken flare port."),
  asset(manifest, "premium-display-case-gate04-r013-tests",
    `${candidateRoot}/Tests/Editor/PackOpeningGate04R013Tests.cs`, "architecture-test-source", "process",
    "Focused tests cover blend shapes, reversibility, containment, identity, no early reveal and source mapping."),
  asset(manifest, "premium-display-case-gate04-r013-scene",
    `${candidateRoot}/Scenes/PackOpeningGate04R013.unity`, "architecture-unity-scene", "process",
    "Actual candidate Unity scene captured at 1206x2622/60 fps."),
  asset(manifest, "premium-display-case-gate04-r013-source-map",
    `${iterationRoot}/source-to-canonical-mapping.json`, "architecture-source-mapping", "validation",
    "CC0 direct-copy, adapted and rejected source mapping with SHA-256 values."),
  asset(manifest, "premium-display-case-gate04-r013-source-manifest",
    `${iterationRoot}/unity-source-manifest.json`, "architecture-source-manifest", "validation",
    "Engine, Pack-only, whole-case and non-shipping boundary contract."),
  asset(manifest, "premium-display-case-gate04-r013-capture-report",
    `${iterationRoot}/unity-capture-report.json`, "architecture-capture-report", "validation",
    "Actual Unity 1206x2622/60 fps capture metrics and continuity checks."),
  asset(manifest, "premium-display-case-gate04-r013-self-rejection",
    `${iterationRoot}/self-rejection.json`, "architecture-full-size-review", "validation",
    "Full-size self-rejection with exact visual failures and storage blocker."),
  asset(manifest, "premium-display-case-gate04-r013-primary-contact",
    `${iterationRoot}/primary-contact-sheet.png`, "architecture-primary-contact-sheet", "shipping-render",
    "Rejected primary Unity contact sheet without diagnostic overlays."),
  asset(manifest, "premium-display-case-gate04-r013-continuity-contact",
    `${iterationRoot}/continuity-contact-sheet.png`, "architecture-continuity-contact-sheet", "shipping-render",
    "Rejected supplementary Unity same-case contact sheet."),
  asset(manifest, "premium-display-case-gate04-r013-source-target",
    `${iterationRoot}/source-target-side-by-side.png`, "architecture-source-target-comparison", "validation",
    "Separate source-to-retarget comparison; target does not preserve the required visual identity."),
  asset(manifest, "premium-display-case-gate04-r013-technical-continuity",
    `${iterationRoot}/technical-continuity-sheet.svg`, "architecture-continuity-diagnostics", "validation",
    "Separate root ID, renderer IDs, projected bounds and occlusion diagnostics."),
  asset(manifest, "premium-display-case-gate04-r013-footprint",
    `${iterationRoot}/runtime-footprint-editor-estimate.json`, "architecture-runtime-estimate", "validation",
    "Editor-only memory and draw-call estimate; not a device measurement."),
  asset(manifest, "premium-display-case-gate04-r013-iteration10-self-rejection",
    `${evidenceRoot}/iterations/iteration-10-source-rim-self-rejection/self-rejection.json`,
    "architecture-iteration-history", "validation",
    "Preserved preliminary source-rim self-rejection before the final capture.")
];

const addedAssetIds = addAssets(manifest, stage, records);
stage.historicalDecisions = [
  ...(stage.historicalDecisions || []),
  {
    revision: stage.revision,
    status: stage.status,
    decision: stage.decision,
    evidenceReview: stage.evidenceReview,
    supersededBy: "gate04-r013-pack-only-blender-self-rejection",
    supersededAt: now
  }
];
stage.revision += 1;
stage.status = "draft";
stage.reviewArtifactIds = [];
stage.validations = [
  {
    id: "r011-and-r012-history-preserved",
    status: "pass",
    evidence: "All earlier Gate 04 evidence and self-rejections remain registered as immutable history."
  },
  {
    id: "r013-blender-pack-only-rig",
    status: "pass",
    evidence: `${evidenceRoot}/blender-rig-build-report.json; 96 tear columns; six relative shape samples; no case geometry.`
  },
  {
    id: "r013-real-unity-capture",
    status: "pass",
    evidence: `${iterationRoot}/unity-capture-report.json; 1206x2622/60 fps/210 frames.`
  },
  {
    id: "r013-continuity-and-containment",
    status: "pass",
    evidence: "One case ID, constant scale, containment, physical mouth crossing, no early travel, no black/white frame and no bounds jump pass in the capture report."
  },
  {
    id: "r013-full-size-visual-review",
    status: "fail",
    evidence: `${iterationRoot}/self-rejection.json`
  },
  {
    id: "r013-cc0-retarget-visual-identity",
    status: "fail",
    evidence: `${iterationRoot}/source-target-side-by-side.png; stacked rectangular Shuriken streaks do not meet the required narrow warm-neutral contour sweep.`
  },
  {
    id: "r013-primary-video-encodes",
    status: "fail",
    evidence: "Normal and 0.25x MP4 encoding blocked by 119 MiB free space; raw Unity PNG sequences remain archived."
  },
  {
    id: "r013-focused-unity-tests",
    status: "fail",
    evidence: "Not re-run because 119 MiB free space is insufficient for Unity's project/log writes."
  },
  {
    id: "r013-shipping-boundary",
    status: "pass",
    evidence: "shippingRuntimeWired=false, shippingReady=false, physicalPhoneInstalled=false."
  }
];
stage.decision = {
  action: "self-reject",
  notes:
    "R013 proved Pack-only FBX blend-shape import, one-case containment and continuous occlusion in real Unity capture. Full-size review rejects the physical silhouette and CC0 visual retarget: the released strip/lip reads as a rigid blue rail, the mouth as a hard scallop, and source particles as stacked red rectangles. Video encodes and test re-run are blocked by the full volume. Gate 04 cannot request user approval.",
  decidedAt: now,
  decidedBy: "agent-full-size-frame-inspection",
  approvalRequestAllowed: false,
  finalAuthority: "latest-explicit-chat-instruction",
  selfRejectionRecord: `${iterationRoot}/self-rejection.json`
};
stage.evidenceReview = {
  architectureRevision: 7,
  evidenceRevision: 13,
  iteration: 11,
  disposition: "self-rejected",
  primaryArtifact: `${iterationRoot}/primary-contact-sheet.png`,
  fullSizeFramesReviewed: [0, 39, 55, 65, 83, 100, 121, 169],
  shownToUserForApproval: false,
  visualApproval: "not-requested-self-rejected",
  statusText: "视觉批准待确认，未推送手机"
};

for (const downstream of manifest.stages.slice(4)) {
  downstream.status = "stale";
  downstream.staleReason =
    "Gate 04 R013 Pack-only Blender candidate is self-rejected after full-size Unity review.";
}
manifest.model.status = "gate04-r013-pack-only-blender-self-rejected";
manifest.currentState = {
  ...manifest.currentState,
  activeStageId: "04-architecture",
  activeStageStatus: "draft",
  activeIteration: 11,
  visualApproval: "gate04-r013-self-rejected-user-correction-required",
  diagnosis:
    "R013 technically proves Pack-only blend-shape handoff and same-case occlusion, but fails full-size visual review: rigid rail strip/lip, hard scalloped mouth and blocky source retarget.",
  architectureApproval: {
    stageId: "04-architecture",
    architectureRevision: 7,
    evidenceRevision: 13,
    evidenceIteration: 11,
    userApprovalQuote: null,
    decisionState: "self-rejected-user-correction-required",
    approvalRequestAllowed: false,
    gate05Status: "stale"
  },
  motionCorrection: {
    ...manifest.currentState.motionCorrection,
    gate04Status: "r013-self-rejected-user-correction-required",
    currentEvidenceRevision: 13,
    currentEvidenceIteration: 11,
    selfRejectedIterations: [
      ...(manifest.currentState.motionCorrection?.selfRejectedIterations || []),
      "r013-10",
      "r013-11"
    ]
  },
  affectedGateAssessment: {
    earliestAffectedGate: "04-architecture",
    reason: "R013 Pack-only Blender candidate is self-rejected after full-size Unity review.",
    geometryMaterialLightingEnvironmentExportUnityParityInvalidated: true,
    upstreamApprovedGatesUnchanged: ["01-intake", "02-analysis", "03-contract"]
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
    "Gate 04 R013 Pack-only Blender candidate self-rejected after full-size Unity review; no shipping or device state advanced.",
  statusText: "视觉批准待确认，未推送手机"
};
manifest.revision += 1;
manifest.updatedAt = now;
updateStageDigest(manifest, stage);

const event = {
  id: crypto.randomUUID(),
  type: "gate04-r013-pack-only-blender-self-rejected",
  modelId: "premium-display-case",
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "04-architecture",
  stageRevision: stage.revision,
  architectureRevision: 7,
  evidenceRevision: 13,
  evidenceIteration: 11,
  addedAssetIds,
  selfRejectionRecord: stage.decision.selfRejectionRecord,
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
