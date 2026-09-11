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

const expectedPipelineRevision = 93;
const expectedStageRevision = 25;
const repoRoot = "/Users/jiawei.zhou/Documents/Fidgeting app";
const canonicalRoot = path.join(repoRoot, "unity/FidgetingApp");
const stagingRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r015";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-015";
const isolatedRoot = "/tmp/FidgetingApp-PackOpening-R014-Isolated-20260831";
const firstCaptureRoot = path.join(isolatedRoot, "Captures/r015");
const polishCaptureRoot = path.join(
  isolatedRoot,
  "Captures/r015-orientation-polish"
);
const primaryFrames = [0, 14, 26, 42, 56, 68, 95];
const now = new Date().toISOString();

function relative(absolute) {
  return path.relative(repoRoot, absolute);
}

function requireFile(absolute) {
  if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
    throw new Error(`Missing required R015 evidence: ${absolute}`);
  }
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

function sourceHash(relativePath) {
  const absolute = resolveRepoPath(relativePath);
  requireFile(absolute);
  return sha256File(absolute);
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
      name: "Gate 04 R015 isolated Pack-only candidate",
      version: "r015-orientation-micro-polish-self-rejected",
      recipe:
        "Deterministic Blender Pack-only rig plus isolated Unity 6000.5.6f1 URP17 camera capture"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: "gate04-self-rejected-isolated-unity-candidate",
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

const requiredSources = [
  path.join(firstCaptureRoot, "normal/seven-pose-contact-sheet.png"),
  path.join(firstCaptureRoot, "unity-capture-report.json"),
  path.join(polishCaptureRoot, "normal/seven-pose-contact-sheet.png"),
  path.join(polishCaptureRoot, "physical-core-effects-off/seven-pose-effects-off-contact-sheet.png"),
  path.join(polishCaptureRoot, "technical-id-bounds-mouth-occlusion.svg"),
  path.join(polishCaptureRoot, "unity-capture-report.json"),
  path.join(isolatedRoot, "r015-check-results.xml"),
  path.join(canonicalRoot, "ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r015/build_pack_only_rig.py"),
  path.join(canonicalRoot, "ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r015/pack-opening-gate04-r015.blend"),
  path.join(canonicalRoot, "ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r015/PackOpeningGate04R015PackOnlyRig.fbx"),
  path.join(canonicalRoot, "ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r015/blender-closed.png"),
  path.join(canonicalRoot, "ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r015/blender-formed-mouth.png"),
  path.join(canonicalRoot, "ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r015/blender-continuous-rise.png"),
  path.join(canonicalRoot, "ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r015/motion-reference-decision.json")
];
for (const source of requiredSources) {
  requireFile(source);
}
for (const frame of primaryFrames) {
  requireFile(
    path.join(
      polishCaptureRoot,
      "normal/primary",
      `frame-${String(frame).padStart(4, "0")}.png`
    )
  );
}

const evidenceAbsolute = resolveRepoPath(evidenceRoot);
if (fs.existsSync(evidenceAbsolute)) {
  throw new Error(`Refusing to overwrite immutable Gate 04 revision: ${evidenceRoot}`);
}
fs.mkdirSync(evidenceAbsolute, { recursive: false });

copyAbsolute(
  path.join(firstCaptureRoot, "normal/seven-pose-contact-sheet.png"),
  `${evidenceRoot}/attempt-01-edge-on/seven-pose-contact-sheet.png`
);
copyAbsolute(
  path.join(firstCaptureRoot, "unity-capture-report.json"),
  `${evidenceRoot}/attempt-01-edge-on/unity-capture-report.json`
);
copyAbsolute(
  path.join(polishCaptureRoot, "normal/seven-pose-contact-sheet.png"),
  `${evidenceRoot}/attempt-02-orientation-micro-polish/seven-pose-contact-sheet.png`
);
for (const frame of primaryFrames) {
  copyAbsolute(
    path.join(
      polishCaptureRoot,
      "normal/primary",
      `frame-${String(frame).padStart(4, "0")}.png`
    ),
    `${evidenceRoot}/attempt-02-orientation-micro-polish/primary/frame-${String(frame).padStart(4, "0")}.png`
  );
}
copyAbsolute(
  path.join(
    polishCaptureRoot,
    "physical-core-effects-off/seven-pose-effects-off-contact-sheet.png"
  ),
  `${evidenceRoot}/attempt-02-orientation-micro-polish/seven-pose-effects-off-contact-sheet.png`
);
copyAbsolute(
  path.join(polishCaptureRoot, "technical-id-bounds-mouth-occlusion.svg"),
  `${evidenceRoot}/attempt-02-orientation-micro-polish/technical-id-bounds-mouth-occlusion.svg`
);
copyAbsolute(
  path.join(polishCaptureRoot, "unity-capture-report.json"),
  `${evidenceRoot}/attempt-02-orientation-micro-polish/unity-capture-report.json`
);
copyAbsolute(
  path.join(isolatedRoot, "r015-check-results.xml"),
  `${evidenceRoot}/isolated-r015-check-results.xml`
);

const sourcePaths = [
  `${stagingRoot}/build_pack_only_rig.py`,
  `${stagingRoot}/motion-reference-decision.json`,
  `${stagingRoot}/isolated-template/Assets/IsolatedProofR015/Editor/IsolatedR015ProofBuilder.cs`,
  `${stagingRoot}/isolated-template/Assets/IsolatedProofR015/Editor/IsolatedR015ProofRunner.cs`,
  `${stagingRoot}/isolated-template/Assets/IsolatedProofR015/Runtime/IsolatedR015Profile.cs`,
  `${stagingRoot}/isolated-template/Assets/IsolatedProofR015/Runtime/IsolatedR015ProofSequence.cs`,
  `${stagingRoot}/isolated-template/Assets/IsolatedProofR015/Runtime/IsolatedR015ProofCapture.cs`,
  `${stagingRoot}/isolated-template/Assets/IsolatedProofR015/Shaders/MakeItShineCc0PackR015.shader`,
  `${stagingRoot}/isolated-template/Assets/IsolatedProofR015/Shaders/MakeItShineCc0ContourSweepR015.shader`,
  `${stagingRoot}/isolated-template/Assets/IsolatedProofR015/Tests/Editor/IsolatedR015ProofTests.cs`
];
const sourceMapping = writeJson(`${evidenceRoot}/source-to-canonical-mapping.json`, {
  schema: "make-it-shine-cc0-source-mapping.r015.v1",
  sourceCommit: "88842be0063b5b0b75e82ed6572752a37a13c82b",
  license: "CC0-1.0",
  exactUserMotionChoice: "卡包的容纳／抽出因果＋箔层双层剥离",
  referenceOnlySources: [
    {
      url: "https://www.youtube.com/watch?v=gnNSHeoUHRQ&t=710s",
      use: "physical Pack containment and extraction causality",
      imported: false
    },
    {
      url: "https://www.storyblocks.com/video/stock/hands-detail-white-man-unwrapping-red-wrapper-seated-on-bench-outdoors-in-casual-jacket-fingers-peeling-foil-and-plastic-layers-tactile-353739590",
      use: "outer printed foil and delayed inner liner separation",
      imported: false
    },
    {
      url: "https://www.storyblocks.com/video/stock/man-on-bench-opens-treat-pouch-carefully-removes-small-red-snack-from-foil-wrapper-hands-closeup-showing-zipper-and-jacket-detail-urban-353739580",
      use: "pouch mouth before content extraction",
      imported: false
    }
  ],
  direct: [
    {
      source: "Assets/Animation/Clips/Booster/Booster_Discarded.anim",
      sourceSha256: "be661fe81b095f7f1ad08fb2a1c003b15f8690ee08d43f9f705dc849924fb2c6",
      destination: "Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/MakeItShineCc0EffectCurves.cs",
      destinationSha256: sourceHash(
        "unity/FidgetingApp/Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/MakeItShineCc0EffectCurves.cs"
      ),
      use: "exact normalized discard curve after physical containment"
    },
    {
      source: "Assets/Art/Kyle/Materials/SG_Title_Kyle.shadergraph",
      sourceSha256: "6a7718d6ae1eba360c03a1ea16b207ada5ae80f1a4dc2df0d004453bf94e2067",
      destination: "Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/MakeItShineCc0Masks.hlsl",
      destinationSha256: sourceHash(
        "unity/FidgetingApp/Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/MakeItShineCc0Masks.hlsl"
      ),
      use: "object-local sphere-mask contour timing"
    },
    {
      source: "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-body.png",
      sourceSha256: "ebc17bb238ebbcb82d36134bb2781838df610f8a3d1750c27b8ade10fc4681d6",
      destination: `${stagingRoot}/PackOpeningGate04R015PackOnlyRig.fbx`,
      destinationSha256: sourceHash(`${stagingRoot}/PackOpeningGate04R015PackOnlyRig.fbx`),
      use: "unmodified 384x512 Pack artwork"
    },
    {
      source: "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-flap.png",
      sourceSha256: "b031fc5c57d194e9603e9b32e1cd603285aa564490f599f29bb0cd67dab33d49",
      destination: `${stagingRoot}/pack-opening-gate04-r015.blend`,
      destinationSha256: sourceHash(`${stagingRoot}/pack-opening-gate04-r015.blend`),
      use: "unmodified crimp and released-strip artwork"
    }
  ],
  adapted: sourcePaths.map((source) => ({
    source,
    sourceSha256: sourceHash(source),
    destination: "isolated Unity R015 candidate",
    use: "minimal Pack-only rig, real-case binding, or local contour adaptation"
  })),
  rejected: [
    {
      source: "Assets/Prefabs/Cinematic/Opening_Booster.prefab",
      sourceSha256: "b155b76ffe54ac737651adbbfa177e284b22175733096e279e056316bf5aa978",
      reason: "sample Pack and object swaps are forbidden"
    },
    {
      source: "Assets/Art/Booster/BoosterFractured_B.fbx",
      sourceSha256: "fd78b007802a1966a1dfb1a1c6b8c7c36cec2f3622dcbaf480fe039967ded602",
      reason: "sample surrogate geometry is forbidden"
    },
    {
      source: "Assets/Art/Booster/VFX_BoosterExplosion.vfx",
      sourceSha256: "d6af66e7b91e7097d50fbef376bf7b33b63dd9e6738a4c99084cb46460aaac2f",
      reason: "particles and VFX Graph are forbidden"
    },
    {
      source: "Assets/Art/Booster/VFXG_LightingStrike.vfx",
      sourceSha256: "4f4da1d0038cee4e4599467b754a429263286073233bb8ac0f259e908635d7b5",
      reason: "512-spark source behavior is forbidden"
    },
    {
      source: "user-provided motion-reference URLs",
      reason: "reference only; no copyrighted source asset was imported"
    }
  ],
  candidates: {
    sourceRig: `${stagingRoot}/PackOpeningGate04R015PackOnlyRig.fbx`,
    sourceRigSha256: sourceHash(`${stagingRoot}/PackOpeningGate04R015PackOnlyRig.fbx`),
    casePrefab:
      "unity/FidgetingApp/Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001/Prefabs/PresentationRoot.prefab",
    isolatedRenderer:
      "R014 recovered Unity 6000.5.6f1 URP17 default renderer",
    caseGeometryBaked: false,
    caseInstances: 1,
    particles: false,
    vfxGraph: false,
    shippingReady: false
  }
});

const representation = writeJson(`${evidenceRoot}/runtime-representation.json`, {
  schema: "premium-display-case-gate04-r015-runtime-representation.v1",
  isolatedUnityCandidate: true,
  unity: "6000.5.6f1",
  urp: "17.5.0",
  recoveredRenderer: {
    pipeline: "Assets/IsolatedProof/Generated/IsolatedR014URPFixed.asset",
    renderer: "Assets/IsolatedProof/Generated/IsolatedR014Renderer.asset",
    defaultRendererBound: true
  },
  pack: {
    rig: `${stagingRoot}/PackOpeningGate04R015PackOnlyRig.fbx`,
    rigSha256: sourceHash(`${stagingRoot}/PackOpeningGate04R015PackOnlyRig.fbx`),
    representation: "Pack-only Blender FBX with six blend shapes and seven authored poses",
    actualArtworkCanvas: [384, 512],
    rootRotationEuler: [0, 0, 0],
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
  capturedAt: {
    width: 1206,
    height: 2622,
    fps: 60,
    frames: 96,
    durationSeconds: 1.6
  },
  shippingIntegration: false,
  shippingReady: false,
  physicalDeviceInstalled: false
});

const selfRejection = writeJson(`${evidenceRoot}/self-rejection.json`, {
  schema: "premium-display-case-gate04-r015-self-rejection.v1",
  outcome: "self-rejected",
  reviewedAt: now,
  exactUserMotionChoice: "卡包的容纳／抽出因果＋箔层双层剥离",
  visualVerdict:
    "Rejected. The first capture is edge-on. The one allowed root-orientation correction makes the Pack face visible but upside down; frames 14–68 remain a sealed rectangular pouch with no readable tear, physical mouth, containment, or continuous extraction. The case only reads after the Pack disappears, so a neutral reviewer cannot infer pouch opening → contained case → extraction.",
  firstCapture: {
    outcome: "rejected-pre-polish",
    issue: "Pack rendered edge-on as horizontal strips.",
    contactSheet:
      `${evidenceRoot}/attempt-01-edge-on/seven-pose-contact-sheet.png`
  },
  onlyMicroPolish: {
    change: "Unity Pack root rotation -90° X → identity",
    outcome: "rejected",
    issue:
      "Face orientation recovered but printed artwork is upside down and shape-key opening is not visually legible.",
    contactSheet:
      `${evidenceRoot}/attempt-02-orientation-micro-polish/seven-pose-contact-sheet.png`
  },
  fullSizePosesReviewed: primaryFrames.map((frame) => ({
    frame,
    path:
      `${evidenceRoot}/attempt-02-orientation-micro-polish/primary/frame-${String(frame).padStart(4, "0")}.png`,
    sha256: sha256File(
      resolveRepoPath(
        `${evidenceRoot}/attempt-02-orientation-micro-polish/primary/frame-${String(frame).padStart(4, "0")}.png`
      )
    )
  })),
  structuralCapture:
    "The isolated capture report passed continuity and zero-VFX diagnostics only. Those metrics do not establish the required visual causality.",
  tests: {
    path: `${evidenceRoot}/isolated-r015-check-results.xml`,
    result: "5/5 pass",
    scope:
      "Pack-only geometry, identity, reversibility, containment state, and forbidden-port checks"
  },
  sourceMapping: sourceMapping.path,
  runtimeRepresentation: representation.path,
  preservedRejectedEvidenceRevisions: [8, 9, 10, 11, 12, 13, 14],
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
  throw new Error("Gate 04 is not the expected R013 self-rejected draft.");
}

const records = [
  artifact(
    manifest,
    "premium-display-case-gate04-r015-motion-reference",
    `${stagingRoot}/motion-reference-decision.json`,
    "architecture-motion-reference",
    "process",
    "Persists the exact user-approved motion/reference choice without importing source videos."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-blender-builder",
    `${stagingRoot}/build_pack_only_rig.py`,
    "architecture-blender-builder",
    "process",
    "Deterministic Pack-only Blender rig source; it contains no case geometry or baked case imagery."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-blend",
    `${stagingRoot}/pack-opening-gate04-r015.blend`,
    "architecture-pack-only-rig",
    "process",
    "Blender Pack-only foil-pouch rig with six relative shape keys."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-rig-fbx",
    `${stagingRoot}/PackOpeningGate04R015PackOnlyRig.fbx`,
    "architecture-pack-only-fbx",
    "process",
    "Pack-only FBX; no Premium Display Case geometry is included."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-blender-closed",
    `${stagingRoot}/blender-closed.png`,
    "architecture-blender-validation",
    "validation",
    "Real Blender sealed Pack rig render."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-blender-mouth",
    `${stagingRoot}/blender-formed-mouth.png`,
    "architecture-blender-validation",
    "validation",
    "Real Blender formed-mouth Pack rig render."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-blender-rise",
    `${stagingRoot}/blender-continuous-rise.png`,
    "architecture-blender-validation",
    "validation",
    "Real Blender continuous-rise Pack rig render."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-runtime-representation",
    representation.path,
    "architecture-runtime-representation",
    "validation",
    "Isolated Unity renderer, Pack-only rig, one live case, and non-shipping boundary."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-source-mapping",
    sourceMapping.path,
    "architecture-source-mapping",
    "validation",
    "CC0 direct/adapted/rejected hashes and copyright-safe motion-reference boundary."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-isolated-checks",
    `${evidenceRoot}/isolated-r015-check-results.xml`,
    "architecture-focused-tests",
    "validation",
    "Emitted isolated Unity C# test result: 5/5 pass."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-first-capture",
    `${evidenceRoot}/attempt-01-edge-on/seven-pose-contact-sheet.png`,
    "architecture-first-capture-history",
    "shipping-render",
    "Preserved rejected first capture before the only allowed root-orientation micro-polish."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-final-capture-report",
    `${evidenceRoot}/attempt-02-orientation-micro-polish/unity-capture-report.json`,
    "architecture-capture-report",
    "validation",
    "Actual isolated Unity 1206x2622/60 fps structural capture report."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-final-contact",
    `${evidenceRoot}/attempt-02-orientation-micro-polish/seven-pose-contact-sheet.png`,
    "architecture-primary-contact-sheet",
    "shipping-render",
    "Rejected full-size seven-pose Unity contact sheet without debug overlay."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-effects-off",
    `${evidenceRoot}/attempt-02-orientation-micro-polish/seven-pose-effects-off-contact-sheet.png`,
    "architecture-effects-off-contact-sheet",
    "validation",
    "Zero-VFX physical-core contact sheet; it also fails visual causality."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-diagnostics",
    `${evidenceRoot}/attempt-02-orientation-micro-polish/technical-id-bounds-mouth-occlusion.svg`,
    "architecture-continuity-diagnostics",
    "validation",
    "Separate same-case ID, bounds trajectory, and mouth-state diagnostic."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r015-self-rejection",
    selfRejection.path,
    "architecture-full-size-review",
    "validation",
    "Concise full-size visual self-rejection after the one permitted micro-polish."
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
    supersededBy: "gate04-r015-self-rejection",
    supersededAt: now
  }
];
stage.revision += 1;
stage.status = "draft";
stage.reviewArtifactIds = [];
stage.validations = [
  {
    id: "r008-to-r014-rejected-history-preserved",
    status: "pass",
    evidence: "All prior rejected Gate 04 evidence revisions 8–14 remain immutable and inspectable."
  },
  {
    id: "r015-user-motion-reference-persisted",
    status: "pass",
    evidence: `${stagingRoot}/motion-reference-decision.json`
  },
  {
    id: "r015-pack-only-blender-rig",
    status: "pass",
    evidence: `${stagingRoot}/blender-rig-build-report.json; 49 authored guide stations; 11 Pack-only meshes; no case geometry.`
  },
  {
    id: "r015-isolated-unity-structural-capture",
    status: "pass",
    evidence: `${evidenceRoot}/attempt-02-orientation-micro-polish/unity-capture-report.json; 1206x2622/60 fps/96 frames.`
  },
  {
    id: "r015-isolated-unity-checks",
    status: "pass",
    evidence: `${evidenceRoot}/isolated-r015-check-results.xml; 5/5 pass.`
  },
  {
    id: "r015-full-size-visual-review",
    status: "fail",
    evidence: selfRejection.path
  },
  {
    id: "r015-shipping-boundary",
    status: "pass",
    evidence: "isolatedCandidate=true, shippingRuntimeWired=false, shippingReady=false, physicalPhoneInstalled=false."
  }
];
stage.decision = {
  action: "self-reject",
  notes:
    "R015 preserved the user-approved Pack containment/extraction and dual-foil reference direction. Its first capture was edge-on. The only permitted root-orientation micro-polish exposed the Pack face, but the artwork was upside down and the tear/mouth/extraction remained visually unreadable. Do not request visual approval or run further visual iterations in this task.",
  decidedAt: now,
  decidedBy: "agent-full-size-frame-inspection",
  approvalRequestAllowed: false,
  finalAuthority: "latest-explicit-chat-instruction",
  selfRejectionRecord: selfRejection.path
};
stage.evidenceReview = {
  architectureRevision: 7,
  evidenceRevision: 15,
  iteration: "r015-orientation-micro-polish",
  disposition: "self-rejected",
  primaryArtifact:
    `${evidenceRoot}/attempt-02-orientation-micro-polish/seven-pose-contact-sheet.png`,
  fullSizeFramesReviewed: primaryFrames,
  shownToUserForApproval: false,
  visualApproval: "not-requested-self-rejected",
  statusText: "视觉批准待确认，未推送手机"
};
for (const downstream of manifest.stages.slice(4)) {
  downstream.status = "stale";
  downstream.staleReason =
    "Gate 04 R015 is self-rejected after the one allowed orientation micro-polish.";
}
manifest.model.status = "gate04-r015-isolated-self-rejected";
manifest.currentState = {
  ...manifest.currentState,
  activeStageId: "04-architecture",
  activeStageStatus: "draft",
  activeIteration: "r015-orientation-micro-polish",
  visualApproval: "gate04-r015-self-rejected-user-correction-required",
  diagnosis:
    "R015 has structural continuity but cannot show the approved physical Pack causality: the final Pack art is upside down and the tear/mouth/extraction are not visually legible.",
  architectureApproval: {
    stageId: "04-architecture",
    architectureRevision: 7,
    evidenceRevision: 15,
    evidenceIteration: "r015-orientation-micro-polish",
    userApprovalQuote: null,
    decisionState: "self-rejected-user-correction-required",
    approvalRequestAllowed: false,
    gate05Status: "stale"
  },
  motionCorrection: {
    ...manifest.currentState.motionCorrection,
    gate04Status: "r015-self-rejected-user-correction-required",
    currentEvidenceRevision: 15,
    currentEvidenceIteration: "r015-orientation-micro-polish",
    rejectedEvidenceRevisions: [8, 9, 10, 11, 12, 13, 14, 15],
    selfRejectedIterations: [
      ...(manifest.currentState.motionCorrection?.selfRejectedIterations || []),
      "r014-renderer-recovery",
      "r015-attempt-01-edge-on",
      "r015-orientation-micro-polish"
    ]
  },
  affectedGateAssessment: {
    earliestAffectedGate: "04-architecture",
    reason:
      "Gate 04 R015 is self-rejected after the one allowed orientation micro-polish.",
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
    "Gate 04 R015 isolated Pack-only candidate self-rejected after one orientation micro-polish; no shipping or device state advanced.",
  statusText: "视觉批准待确认，未推送手机"
};
manifest.revision += 1;
manifest.updatedAt = now;
refreshStageDigest(manifest, stage);

const event = {
  id: crypto.randomUUID(),
  type: "gate04-r015-isolated-self-rejected",
  modelId: "premium-display-case",
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "04-architecture",
  stageRevision: stage.revision,
  architectureRevision: 7,
  evidenceRevision: 15,
  evidenceIteration: "r015-orientation-micro-polish",
  exactUserMotionChoice: "卡包的容纳／抽出因果＋箔层双层剥离",
  sourceTask: "cursor-task:premium-display-case-gate04-r015-20260831",
  addedAssetIds,
  selfRejectionRecord: selfRejection.path,
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
      addedAssets: addedAssetIds.length
    },
    null,
    2
  )
);
