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

const repoRoot = "/Users/jiawei.zhou/Documents/Fidgeting app";
const canonicalRoot = path.join(repoRoot, "unity/FidgetingApp");
const stagingRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r016-repair";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-016";
const isolatedRoot = "/tmp/FidgetingApp-PackOpening-R016-Repair-20260831";
const preflightRoot = path.join(isolatedRoot, "Captures/r016-preflight");
const expectedPipelineRevision = 94;
const expectedStageRevision = 26;
const now = new Date().toISOString();

function requireFile(file) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    throw new Error(`Missing required R016 file: ${file}`);
  }
}

function relative(absolute) {
  return path.relative(repoRoot, absolute);
}

function writeJson(destinationRelative, value) {
  const destination = resolveRepoPath(destinationRelative);
  if (fs.existsSync(destination)) {
    throw new Error(`Refusing to overwrite immutable evidence: ${destinationRelative}`);
  }
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, `${JSON.stringify(value, null, 2)}\n`, "utf8");
  return {
    path: destinationRelative,
    sha256: sha256File(destination),
    sizeBytes: fs.statSync(destination).size
  };
}

function copyAbsolute(source, destinationRelative) {
  requireFile(source);
  const destination = resolveRepoPath(destinationRelative);
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(source, destination, fs.constants.COPYFILE_EXCL);
  return {
    path: destinationRelative,
    sha256: sha256File(destination),
    sizeBytes: fs.statSync(destination).size
  };
}

function artifact(manifest, id, relativePath, slot, role, note) {
  const absolute = resolveRepoPath(relativePath);
  requireFile(absolute);
  const sourceStage = manifest.stages.find((stage) => stage.id === "03-contract");
  const sourceAssetIds = sourceStage?.artifactIds || [];
  const sourceClaimIds = sourceAssetIds.flatMap(
    (assetId) =>
      manifest.assets.find((item) => item.id === assetId)?.sourceClaimIds || []
  );
  return {
    id,
    stageId: "04-architecture",
    slot,
    path: relativePath,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Gate 04 R016 isolated Pack-only bounded repair",
      version: "r016-pre-capture-static-self-rejected",
      recipe:
        "Deterministic Blender Pack-only export plus isolated Unity 6000.5.6f1 URP17 Play Mode static mesh and ID capture"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: "gate04-isolated-technical-self-rejection",
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
    if (existing.has(record.id)) {
      throw new Error(`Immutable asset ID already exists: ${record.id}`);
    }
    manifest.assets.push(record);
    stage.artifactIds.push(record.id);
    added.push(record.id);
  }
  stage.artifactIds = [...new Set(stage.artifactIds)];
  return added;
}

function refreshStageDigest(manifest, stage) {
  const index = manifest.stages.indexOf(stage);
  const hashes = stage.artifactIds
    .map((assetId) => manifest.assets.find((item) => item.id === assetId)?.sha256)
    .filter(Boolean);
  stage.inputDigest = manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues(hashes);
  manifest.stages[index + 1].inputDigest = stage.outputDigest;
}

const staticReportPath = path.join(
  preflightRoot,
  "r016-pre-capture-static-report.json"
);
const staticResultsPath = path.join(
  preflightRoot,
  "r016-pre-capture-static-results.xml"
);
const requiredSources = [
  path.join(canonicalRoot, stagingRoot.replace("unity/FidgetingApp/", ""), "build_pack_only_rig.py"),
  path.join(canonicalRoot, stagingRoot.replace("unity/FidgetingApp/", ""), "pack-opening-gate04-r016.blend"),
  path.join(canonicalRoot, stagingRoot.replace("unity/FidgetingApp/", ""), "PackOpeningGate04R016PackOnlyRig.fbx"),
  path.join(canonicalRoot, stagingRoot.replace("unity/FidgetingApp/", ""), "blender-rig-build-report.json"),
  path.join(
    canonicalRoot,
    stagingRoot.replace("unity/FidgetingApp/", ""),
    "isolated-template/Assets/IsolatedProofR016/Editor/IsolatedR016ProofBuilder.cs"
  ),
  path.join(
    canonicalRoot,
    stagingRoot.replace("unity/FidgetingApp/", ""),
    "isolated-template/Assets/IsolatedProofR016/Editor/IsolatedR016ProofRunner.cs"
  ),
  path.join(
    canonicalRoot,
    stagingRoot.replace("unity/FidgetingApp/", ""),
    "isolated-template/Assets/IsolatedProofR016/Runtime/IsolatedR016ProofSequence.cs"
  ),
  path.join(
    canonicalRoot,
    stagingRoot.replace("unity/FidgetingApp/", ""),
    "isolated-template/Assets/IsolatedProofR016/Runtime/IsolatedR016ProofCapture.cs"
  ),
  path.join(
    canonicalRoot,
    stagingRoot.replace("unity/FidgetingApp/", ""),
    "isolated-template/Assets/IsolatedProofR016/Runtime/IsolatedR016ProofRuntimeDriver.cs"
  ),
  path.join(
    canonicalRoot,
    stagingRoot.replace("unity/FidgetingApp/", ""),
    "isolated-template/Assets/IsolatedProofR016/Tests/Editor/IsolatedR016ProofTests.cs"
  ),
  path.join(preflightRoot, "basis-frame.png"),
  path.join(preflightRoot, "formed-mouth-frame.png"),
  path.join(preflightRoot, "live-case-mouth-id-090.png"),
  staticReportPath,
  staticResultsPath,
  path.join(isolatedRoot, "r016-structural-check-results.xml"),
  path.join(isolatedRoot, "r016-structural-checks-readable.log"),
  path.join(isolatedRoot, "r016-preflight-readable.log"),
  path.join(
    canonicalRoot,
    "ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-015/self-rejection.json"
  )
];
for (const source of requiredSources) {
  requireFile(source);
}

const staticReport = JSON.parse(fs.readFileSync(staticReportPath, "utf8"));
const failedCheck = staticReport.checks?.find((check) => !check.passed);
if (
  staticReport.passed !== false ||
  failedCheck?.id !== "front-foil-baked-delta-at-070-at-least-0045m"
) {
  throw new Error("R016 static failure does not match the bounded threshold.");
}
const deltaMeters = staticReport.frontFoilMaxBakedDeltaMeters;
if (!(deltaMeters < 0.045)) {
  throw new Error("R016 static delta must remain below 0.045m for self-rejection.");
}

const evidenceAbsolute = resolveRepoPath(evidenceRoot);
if (fs.existsSync(evidenceAbsolute)) {
  throw new Error(`Refusing to overwrite immutable Gate 04 revision: ${evidenceRoot}`);
}
fs.mkdirSync(evidenceAbsolute, { recursive: false });

const copied = {
  staticReport: copyAbsolute(
    staticReportPath,
    `${evidenceRoot}/r016-pre-capture-static-report.json`
  ),
  staticResults: copyAbsolute(
    staticResultsPath,
    `${evidenceRoot}/r016-pre-capture-static-results.xml`
  ),
  basis: copyAbsolute(
    path.join(preflightRoot, "basis-frame.png"),
    `${evidenceRoot}/preflight/basis-frame.png`
  ),
  formedMouth: copyAbsolute(
    path.join(preflightRoot, "formed-mouth-frame.png"),
    `${evidenceRoot}/preflight/formed-mouth-frame.png`
  ),
  liveCaseId: copyAbsolute(
    path.join(preflightRoot, "live-case-mouth-id-090.png"),
    `${evidenceRoot}/preflight/live-case-mouth-id-090.png`
  ),
  structuralResults: copyAbsolute(
    path.join(isolatedRoot, "r016-structural-check-results.xml"),
    `${evidenceRoot}/r016-structural-check-results.xml`
  ),
  structuralLog: copyAbsolute(
    path.join(isolatedRoot, "r016-structural-checks-readable.log"),
    `${evidenceRoot}/r016-structural-checks.log`
  ),
  preflightLog: copyAbsolute(
    path.join(isolatedRoot, "r016-preflight-readable.log"),
    `${evidenceRoot}/r016-preflight.log`
  )
};

const repairDecision = writeJson(`${evidenceRoot}/bounded-repair-decision.json`, {
  schema: "premium-display-case-gate04-r016-bounded-repair.v1",
  sourceR015ForensicRecord:
    "cursor-task:premium-display-case-gate04-r015-forensic-20260831",
  repairScope: [
    "reverse only Pack front-template V polarity",
    "retain runtime Pack root identity rotation",
    "wait one genuine Unity Play Mode frame after state assignment before each render",
    "use isolated-only readable importer for imported-mesh assertions"
  ],
  prohibitedChanges: [
    "case prefab",
    "toy or ContentSlot",
    "shipping scenes or prefabs",
    "canonical package or project settings",
    "curves",
    "materials",
    "effects",
    "geometry redesign",
    "device installation"
  ],
  r015RejectedEvidencePreserved: true,
  r016Outcome: "pre-capture-static-failed",
  requiredThresholdMeters: 0.045,
  actualBakedFrontFoilDeltaMeters: deltaMeters,
  thresholdShortfallMeters: 0.045 - deltaMeters,
  staticReport: copied.staticReport.path,
  staticResults: copied.staticResults.path,
  scrubStarted: false,
  fullProofStarted: false,
  shippingReady: false,
  physicalPhoneInstalled: false
});

const runtimeRepresentation = writeJson(`${evidenceRoot}/runtime-representation.json`, {
  schema: "premium-display-case-gate04-r016-runtime-representation.v1",
  isolatedUnityCandidate: true,
  unity: "6000.5.6f1",
  urp: "17.5.0",
  pack: {
    rig: `${stagingRoot}/PackOpeningGate04R016PackOnlyRig.fbx`,
    rigSha256: sha256File(
      resolveRepoPath(`${stagingRoot}/PackOpeningGate04R016PackOnlyRig.fbx`)
    ),
    rootRotationEuler: [0, 0, 0],
    frontArtworkVPolarity: "lower-screen=0.020, upper-screen=0.815",
    importer: {
      bakeAxisConversion: false,
      importBlendShapes: true,
      isReadable: true,
      scope: "isolated R016 static test only"
    },
    caseGeometryIncluded: false
  },
  case: {
    count: 1,
    representation: "one live unchanged assembled Gate 11 case prefab",
    callerOwnedContentSlot: "untouched",
    baked: false,
    swap: false,
    crossfade: false
  },
  staticCapture: {
    width: staticReport.liveCaseId.width,
    height: staticReport.liveCaseId.height,
    stateFrames: {
      basis: [
        staticReport.basisStateSetFrame,
        staticReport.basisRenderedAfterFrame
      ],
      formedMouth: [
        staticReport.openStateSetFrame,
        staticReport.openRenderedAfterFrame
      ],
      liveCaseId: [
        staticReport.liveCaseId.stateSetFrame,
        staticReport.liveCaseId.renderedAfterFrame
      ]
    }
  },
  shippingIntegration: false,
  shippingReady: false,
  physicalDeviceInstalled: false
});

const sourceMapping = writeJson(`${evidenceRoot}/source-to-canonical-mapping.json`, {
  schema: "make-it-shine-cc0-source-mapping.r016.v1",
  sourceCommit: "88842be0063b5b0b75e82ed6572752a37a13c82b",
  license: "CC0-1.0",
  exactUserMotionChoice: "卡包的容纳／抽出因果＋箔层双层剥离",
  direct: [
    {
      source: "Assets/Animation/Clips/Booster/Booster_Discarded.anim",
      sourceSha256:
        "be661fe81b095f7f1ad08fb2a1c003b15f8690ee08d43f9f705dc849924fb2c6",
      destination:
        "unity/FidgetingApp/Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/MakeItShineCc0EffectCurves.cs",
      use: "unchanged exact normalized discard curve"
    },
    {
      source: "Assets/Art/Kyle/Materials/SG_Title_Kyle.shadergraph",
      sourceSha256:
        "6a7718d6ae1eba360c03a1ea16b207ada5ae80f1a4dc2df0d004453bf94e2067",
      destination:
        "unity/FidgetingApp/Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/MakeItShineCc0Masks.hlsl",
      use: "unchanged object-local contour mask"
    },
    {
      source: "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-body.png",
      sourceSha256:
        "ebc17bb238ebbcb82d36134bb2781838df610f8a3d1750c27b8ade10fc4681d6",
      destination: `${stagingRoot}/PackOpeningGate04R016PackOnlyRig.fbx`,
      use: "unmodified 384x512 Pack artwork with corrected front V polarity"
    }
  ],
  adapted: [
    "build_pack_only_rig.py",
    "IsolatedR016ProofBuilder.cs",
    "IsolatedR016ProofRunner.cs",
    "IsolatedR016ProofSequence.cs",
    "IsolatedR016ProofCapture.cs",
    "IsolatedR016ProofRuntimeDriver.cs",
    "IsolatedR016ProofTests.cs"
  ].map((file) => {
    const suffix = file === "build_pack_only_rig.py"
      ? file
      : [
          "IsolatedR016ProofBuilder.cs",
          "IsolatedR016ProofRunner.cs"
        ].includes(file)
        ? `isolated-template/Assets/IsolatedProofR016/Editor/${file}`
        : file === "IsolatedR016ProofTests.cs"
          ? `isolated-template/Assets/IsolatedProofR016/Tests/Editor/${file}`
          : `isolated-template/Assets/IsolatedProofR016/Runtime/${file}`;
    const source = `${stagingRoot}/${suffix}`;
    return {
      source,
      sourceSha256: sha256File(resolveRepoPath(source)),
      destination: "isolated Unity R016 candidate",
      use: "bounded UV, frame-barrier, or static-proof repair"
    };
  }),
  rejected: [
    {
      source: "Assets/Prefabs/Cinematic/Opening_Booster.prefab",
      reason: "sample Pack and object swaps are forbidden"
    },
    {
      source: "Assets/Art/Booster/BoosterFractured_B.fbx",
      reason: "surrogate geometry is forbidden"
    },
    {
      source: "Assets/Art/Booster/VFX_BoosterExplosion.vfx",
      reason: "particles and VFX Graph are forbidden"
    }
  ],
  shippingReady: false
});

const selfRejection = writeJson(`${evidenceRoot}/self-rejection.json`, {
  schema: "premium-display-case-gate04-r016-pre-capture-static-self-rejection.v1",
  outcome: "self-rejected",
  reviewedAt: now,
  exactUserMotionChoice: "卡包的容纳／抽出因果＋箔层双层剥离",
  failure: {
    test: failedCheck.id,
    requiredMeters: 0.045,
    actualMeters: deltaMeters,
    shortfallMeters: 0.045 - deltaMeters,
    evidence: copied.staticResults.path
  },
  passedStaticChecks: staticReport.checks
    .filter((check) => check.passed)
    .map((check) => ({
      id: check.id,
      evidence: check.evidence
    })),
  actualFrameEvidence: {
    basis: copied.basis.path,
    formedMouth: copied.formedMouth.path,
    liveCaseIdAt090: copied.liveCaseId.path,
    frameBarrier: {
      basis: [
        staticReport.basisStateSetFrame,
        staticReport.basisRenderedAfterFrame
      ],
      formedMouth: [
        staticReport.openStateSetFrame,
        staticReport.openRenderedAfterFrame
      ],
      liveCaseId: [
        staticReport.liveCaseId.stateSetFrame,
        staticReport.liveCaseId.renderedAfterFrame
      ]
    }
  },
  visualVerdict:
    "No visual candidate verdict. Gate A failed its required imported-mesh threshold before the 0.5-second scrub. Gate B and the full proof were not run.",
  prohibitedFollowUpsNotRun: [
    "curve tuning",
    "material tuning",
    "effect tuning",
    "geometry redesign",
    "additional visual iteration",
    "device installation"
  ],
  r015RejectedEvidencePreserved: true,
  approvalRequestAllowed: false,
  shippingReady: false,
  physicalPhoneInstalled: false,
  statusText: "视觉批准待确认，未推送手机"
});

const manifest = loadManifest("premium-display-case");
if (manifest.revision !== expectedPipelineRevision) {
  throw new Error(
    `Expected pipeline revision ${expectedPipelineRevision}; found ${manifest.revision}.`
  );
}
const stage = manifest.stages.find((item) => item.id === "04-architecture");
if (
  !stage ||
  stage.revision !== expectedStageRevision ||
  stage.status !== "draft"
) {
  throw new Error("Gate 04 is not the expected R015 self-rejected draft.");
}

const records = [
  artifact(
    manifest,
    "premium-display-case-gate04-r016-blender-builder",
    `${stagingRoot}/build_pack_only_rig.py`,
    "architecture-blender-builder",
    "process",
    "The only visual source change reverses front-template V polarity."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-blend",
    `${stagingRoot}/pack-opening-gate04-r016.blend`,
    "architecture-pack-only-rig",
    "process",
    "Rebuilt Pack-only Blender source with no case geometry."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-rig-fbx",
    `${stagingRoot}/PackOpeningGate04R016PackOnlyRig.fbx`,
    "architecture-pack-only-fbx",
    "process",
    "Pack-only FBX retains identity runtime root and six blend shapes."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-blender-build-report",
    `${stagingRoot}/blender-rig-build-report.json`,
    "architecture-blender-validation",
    "validation",
    "Blender 5.2 deterministic R016 Pack-only export report."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-runtime-builder",
    `${stagingRoot}/isolated-template/Assets/IsolatedProofR016/Editor/IsolatedR016ProofBuilder.cs`,
    "architecture-isolated-builder",
    "process",
    "R016 isolated-only scene builder and readable importer assertion."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-runtime-capture",
    `${stagingRoot}/isolated-template/Assets/IsolatedProofR016/Runtime/IsolatedR016ProofCapture.cs`,
    "architecture-capture-source",
    "process",
    "Every capture path advances a Unity Play Mode frame before render."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-runtime-driver",
    `${stagingRoot}/isolated-template/Assets/IsolatedProofR016/Runtime/IsolatedR016ProofRuntimeDriver.cs`,
    "architecture-capture-driver",
    "process",
    "Play Mode driver executes actual-frame capture only in the isolated project."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-runtime-sequence",
    `${stagingRoot}/isolated-template/Assets/IsolatedProofR016/Runtime/IsolatedR016ProofSequence.cs`,
    "architecture-sequence-source",
    "process",
    "R016 sequence exposes the imported front foil for static verification."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-tests",
    `${stagingRoot}/isolated-template/Assets/IsolatedProofR016/Tests/Editor/IsolatedR016ProofTests.cs`,
    "architecture-focused-tests",
    "process",
    "Focused R016 importer and invariant tests."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-static-report",
    copied.staticReport.path,
    "architecture-pre-capture-static-report",
    "validation",
    "Actual Unity static report with the one failing 0.045m mesh-delta threshold."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-static-results",
    copied.staticResults.path,
    "architecture-pre-capture-static-results",
    "validation",
    "Emitted static-test XML: 4/5 pass, mesh delta threshold failed."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-basis-frame",
    copied.basis.path,
    "architecture-pre-capture-frame",
    "validation",
    "Actual isolated Unity Basis frame."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-formed-mouth-frame",
    copied.formedMouth.path,
    "architecture-pre-capture-frame",
    "validation",
    "Actual isolated Unity t=0.70 formed-mouth frame."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-live-case-id",
    copied.liveCaseId.path,
    "architecture-pre-capture-id-frame",
    "validation",
    "Actual isolated Unity t=0.90 live-case and physical-lip ID frame."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-structural-results",
    copied.structuralResults.path,
    "architecture-focused-tests",
    "validation",
    "Emitted isolated R016 structural result: 5/5 pass."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-runtime-representation",
    runtimeRepresentation.path,
    "architecture-runtime-representation",
    "validation",
    "Isolated Unity representation and frame-boundary evidence."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-source-mapping",
    sourceMapping.path,
    "architecture-source-mapping",
    "validation",
    "CC0, Pack artwork, and bounded-repair provenance."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-bounded-repair",
    repairDecision.path,
    "architecture-repair-contract",
    "process",
    "Records permitted repair scope and prohibited follow-up changes."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r016-self-rejection",
    selfRejection.path,
    "architecture-full-size-review",
    "validation",
    "Gate A technical self-rejection before scrub or full proof."
  )
];
const addedAssetIds = addAssets(manifest, stage, records);

stage.historicalDecisions = [
  ...(stage.historicalDecisions || []),
  {
    revision: stage.revision,
    status: stage.status,
    decision: stage.decision,
    evidenceReview: stage.evidenceReview,
    supersededBy: "gate04-r016-pre-capture-static-self-rejection",
    supersededAt: now
  }
];
stage.revision += 1;
stage.status = "draft";
stage.reviewArtifactIds = [];
stage.validations = [
  {
    id: "r008-to-r015-rejected-history-preserved",
    status: "pass",
    evidence:
      "All prior rejected Gate 04 evidence revisions 8–15 remain immutable and inspectable."
  },
  {
    id: "r016-blender-pack-only-export",
    status: "pass",
    evidence:
      `${stagingRoot}/blender-rig-build-report.json; 49 guide stations; 11 Pack-only meshes; no case geometry.`
  },
  {
    id: "r016-isolated-structural-checks",
    status: "pass",
    evidence: `${copied.structuralResults.path}; 5/5 pass.`
  },
  {
    id: "r016-pre-capture-static-test",
    status: "fail",
    evidence:
      `${copied.staticResults.path}; baked front foil delta ${deltaMeters.toFixed(9)}m < required 0.045000000m.`
  },
  {
    id: "r016-scrub-and-full-proof-not-run",
    status: "pass",
    evidence:
      "Gate A failed; no 0.5-second scrub, full proof, curve/material/effect tuning, or device work ran."
  },
  {
    id: "r016-shipping-boundary",
    status: "pass",
    evidence:
      "isolatedCandidate=true, shippingRuntimeWired=false, shippingReady=false, physicalPhoneInstalled=false."
  }
];
stage.decision = {
  action: "self-reject",
  notes:
    `R016 corrected the front V polarity, kept the Pack root identity, and waited a real Unity Play Mode frame before each render. The static imported-mesh gate still measured ${deltaMeters.toFixed(9)}m at t=0.70, below the required 0.045000000m. Stop before scrub or full proof; do not tune curves, materials, effects, or geometry.`,
  decidedAt: now,
  decidedBy: "agent-emitted-static-test",
  approvalRequestAllowed: false,
  finalAuthority: "latest-explicit-chat-instruction",
  selfRejectionRecord: selfRejection.path
};
stage.evidenceReview = {
  architectureRevision: 7,
  evidenceRevision: 16,
  iteration: "r016-pre-capture-static-self-rejection",
  disposition: "self-rejected",
  primaryArtifact: copied.staticResults.path,
  fullSizeFramesReviewed: [],
  shownToUserForApproval: false,
  visualApproval: "not-requested-static-gate-failed",
  statusText: "视觉批准待确认，未推送手机"
};
for (const downstream of manifest.stages.slice(4)) {
  downstream.status = "stale";
  downstream.staleReason =
    "Gate 04 R016 pre-capture static test failed the required baked-mesh delta.";
}
manifest.model.status = "gate04-r016-pre-capture-static-self-rejected";
manifest.currentState = {
  ...manifest.currentState,
  activeStageId: "04-architecture",
  activeStageStatus: "draft",
  activeIteration: "r016-pre-capture-static-self-rejection",
  visualApproval: "gate04-r016-self-rejected-static-threshold-failed",
  diagnosis:
    `R016 corrects UV polarity and rendered the live case through the mouth, but its imported front foil changes ${deltaMeters.toFixed(9)}m at t=0.70, below the required 0.045000000m. No scrub or full proof ran.`,
  architectureApproval: {
    stageId: "04-architecture",
    architectureRevision: 7,
    evidenceRevision: 16,
    evidenceIteration: "r016-pre-capture-static-self-rejection",
    userApprovalQuote: null,
    decisionState: "self-rejected-static-threshold-failed",
    approvalRequestAllowed: false,
    gate05Status: "stale"
  },
  motionCorrection: {
    ...manifest.currentState.motionCorrection,
    gate04Status: "r016-self-rejected-static-threshold-failed",
    currentEvidenceRevision: 16,
    currentEvidenceIteration: "r016-pre-capture-static-self-rejection",
    rejectedEvidenceRevisions: [8, 9, 10, 11, 12, 13, 14, 15, 16],
    selfRejectedIterations: [
      ...(manifest.currentState.motionCorrection?.selfRejectedIterations || []),
      "r016-pre-capture-static-threshold"
    ]
  },
  affectedGateAssessment: {
    earliestAffectedGate: "04-architecture",
    reason:
      "Gate 04 R016 pre-capture static test failed the required baked-mesh delta.",
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
    "Gate 04 R016 isolated bounded repair self-rejected at the required pre-capture mesh-delta gate; no scrub, full proof, shipping, or device state advanced.",
  statusText: "视觉批准待确认，未推送手机"
};
manifest.revision += 1;
manifest.updatedAt = now;
refreshStageDigest(manifest, stage);

const event = {
  id: crypto.randomUUID(),
  type: "gate04-r016-pre-capture-static-self-rejected",
  modelId: "premium-display-case",
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "04-architecture",
  stageRevision: stage.revision,
  architectureRevision: 7,
  evidenceRevision: 16,
  evidenceIteration: "r016-pre-capture-static-self-rejection",
  sourceTask: "cursor-task:premium-display-case-gate04-r016-20260831",
  exactUserMotionChoice: "卡包的容纳／抽出因果＋箔层双层剥离",
  failedTest: failedCheck.id,
  requiredMeters: 0.045,
  actualMeters: deltaMeters,
  addedAssetIds,
  selfRejectionRecord: selfRejection.path,
  scrubStarted: false,
  fullProofStarted: false,
  approvalRequestAllowed: false,
  shippingReady: false,
  physicalPhoneInstalled: false,
  deviceAccepted: false,
  statusText: "视觉批准待确认，未推送手机"
};
saveManifest(manifest, event);
console.log(
  JSON.stringify(
    {
      pipelineRevision: manifest.revision,
      stageRevision: stage.revision,
      stageStatus: stage.status,
      evidenceRoot,
      deltaMeters,
      addedAssets: addedAssetIds.length
    },
    null,
    2
  )
);
