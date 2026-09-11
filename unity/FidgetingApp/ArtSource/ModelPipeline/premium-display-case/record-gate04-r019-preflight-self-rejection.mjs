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
const stagingRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r019-pack-mouth-repair";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-019";
const isolatedRoot = "/tmp/FidgetingApp-PackOpening-R019-PackMouth-20260831";
const r018IsolatedRoot =
  "/tmp/FidgetingApp-PackOpening-R018-CoordinateOrientation-20260831";
const expectedPipelineRevision = 97;
const expectedStageRevision = 29;
const now = new Date().toISOString();

function requireFile(file) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    throw new Error(`Missing required R019 file: ${file}`);
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

function walk(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const file = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(file) : [file];
  });
}

function artifact(manifest, id, copied, slot, role, note) {
  const contractStage = manifest.stages.find(
    (stage) => stage.id === "03-contract"
  );
  const sourceAssetIds = contractStage?.artifactIds || [];
  const sourceClaimIds = sourceAssetIds.flatMap(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)
      ?.sourceClaimIds || []
  );
  return {
    id,
    stageId: "04-architecture",
    slot,
    path: copied.path,
    sha256: copied.sha256,
    exists: true,
    sizeBytes: copied.sizeBytes,
    role,
    producer: {
      name: "Gate 04 R019 isolated Pack-mouth repair",
      version: "r019-preflight-self-rejected",
      recipe:
        "Deterministic Blender Pack-only rebuild plus isolated Unity 6000.5.6f1 URP 17.5 full-resolution preflight"
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

function refreshStageDigest(manifest, stage) {
  const index = manifest.stages.indexOf(stage);
  const hashes = stage.artifactIds
    .map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256)
    .filter(Boolean);
  stage.inputDigest = manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues(hashes);
  manifest.stages[index + 1].inputDigest = stage.outputDigest;
}

const absolute = (relative) => resolveRepoPath(relative);
const stagingAbsolute = absolute(stagingRoot);
const templateRoot = path.join(
  stagingAbsolute,
  "isolated-template/Assets/IsolatedProofR019"
);
const preflightRoot = path.join(isolatedRoot, "Captures/r019-preflight");
const paths = {
  stagingBootstrap: path.join(
    absolute(
      "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging"
    ),
    "bootstrap_r019_pack_mouth_repair.mjs"
  ),
  blenderBuilder: path.join(stagingAbsolute, "build_pack_only_rig.py"),
  blenderProbeBuilder: path.join(
    stagingAbsolute,
    "probe_r019_blender_geometry.py"
  ),
  prepare: path.join(stagingAbsolute, "prepare_r019_isolated.mjs"),
  blenderBuild: path.join(stagingAbsolute, "blender-rig-build-report.json"),
  blenderProbe: path.join(stagingAbsolute, "blender-coordinate-probe.json"),
  blend: path.join(stagingAbsolute, "pack-opening-gate04-r019.blend"),
  fbx: path.join(stagingAbsolute, "PackOpeningGate04R019PackOnlyRig.fbx"),
  blenderSealed: path.join(stagingAbsolute, "blender-sealed.png"),
  blenderFormed: path.join(stagingAbsolute, "blender-formed-mouth.png"),
  blenderRise: path.join(stagingAbsolute, "blender-continuous-rise.png"),
  sourceManifest: path.join(isolatedRoot, "r019-source-manifest.json"),
  structuralResults: path.join(isolatedRoot, "r019-structural-check-results.xml"),
  structuralLog: path.join(isolatedRoot, "r019-structural-check.log"),
  editModeResults: path.join(isolatedRoot, "r019-editmode-results.xml"),
  editModeLog: path.join(isolatedRoot, "r019-editmode-tests.log"),
  preflightLog: path.join(isolatedRoot, "r019-preflight.log"),
  preflightReport: path.join(preflightRoot, "r019-preflight-report.json"),
  preflightResults: path.join(preflightRoot, "r019-preflight-results.xml"),
  r019Calibration: path.join(
    preflightRoot,
    "orientation-calibration/r019-orientation-calibration.json"
  ),
  r019CalibrationFrame: path.join(
    preflightRoot,
    "orientation-calibration/r019-pack-artwork.png"
  ),
  r017CalibrationFrame: path.join(
    preflightRoot,
    "orientation-calibration/r017-mirror-control.png"
  ),
  sealedFrame: path.join(preflightRoot, "sealed-state.png"),
  formedFrame: path.join(preflightRoot, "formed-mouth-070.png"),
  containedFrame: path.join(preflightRoot, "case-contained-090.png"),
  topCrimpId: path.join(preflightRoot, "diagnostics/top-crimp-id.png"),
  titleBandId: path.join(
    preflightRoot,
    "diagnostics/archive-title-band-id.png"
  ),
  material070: path.join(
    preflightRoot,
    "diagnostics/mouth-material-id-0.700.png"
  ),
  material090: path.join(
    preflightRoot,
    "diagnostics/mouth-material-id-0.900.png"
  ),
  visibleCaseId: path.join(
    preflightRoot,
    "diagnostics/case-visible-id-090.png"
  ),
  unoccludedCaseId: path.join(
    preflightRoot,
    "diagnostics/case-unoccluded-id-090.png"
  ),
  occludedCaseId: path.join(
    preflightRoot,
    "diagnostics/case-front-occlusion-id-090.png"
  ),
  cc0Audit: path.join(
    r018IsolatedRoot,
    "Assets/Source/CC0/R013-source-audit.json"
  ),
  cc0Contract: absolute(
    "unity/FidgetingApp/Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/SOURCE_CONTRACT.json"
  ),
  r015Rejection: absolute(
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-015/self-rejection.json"
  ),
  r016Rejection: absolute(
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-016/self-rejection.json"
  ),
  r017Rejection: absolute(
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-017/r017-scrub-visual-self-rejection.json"
  ),
  r018Rejection: absolute(
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-018/r018-preflight-self-rejection.json"
  )
};

for (const file of Object.values(paths)) requireFile(file);
for (const file of walk(templateRoot)) {
  if (/\.(cs|shader)$/u.test(file)) requireFile(file);
}
const preflight = JSON.parse(fs.readFileSync(paths.preflightReport, "utf8"));
const preflightXml = fs.readFileSync(paths.preflightResults, "utf8");
const linerFailure = preflight.checks?.find(
  (check) => check.id === "formed-mouth-liner-and-cavity-separate"
);
if (preflight.passed
  || preflight.checks?.length !== 15
  || linerFailure?.passed !== false
  || preflight.formedMouthMaterials?.visibleCavityPixels !== 0
  || !/tests="15" failures="1"/.test(preflightXml)) {
  throw new Error("R019 preflight result no longer matches the required stop.");
}
const manifest = loadManifest("premium-display-case");
if (manifest.revision !== expectedPipelineRevision) {
  throw new Error(
    `Expected pipeline revision ${expectedPipelineRevision}; found ${manifest.revision}.`
  );
}
const stage = manifest.stages.find((item) => item.id === "04-architecture");
if (!stage || stage.revision !== expectedStageRevision || stage.status !== "draft") {
  throw new Error("Gate 04 is not at the expected R018 self-rejected state.");
}
const evidenceAbsolute = absolute(evidenceRoot);
if (fs.existsSync(evidenceAbsolute)) {
  throw new Error(`Refusing to overwrite immutable evidence: ${evidenceRoot}`);
}
fs.mkdirSync(evidenceAbsolute, { recursive: false });

const copied = {};
for (const [key, source, relative] of [
  ["stagingBootstrap", paths.stagingBootstrap, "source/bootstrap_r019_pack_mouth_repair.mjs"],
  ["blenderBuilder", paths.blenderBuilder, "source/build_pack_only_rig.py"],
  ["blenderProbeBuilder", paths.blenderProbeBuilder, "source/probe_r019_blender_geometry.py"],
  ["prepare", paths.prepare, "source/prepare_r019_isolated.mjs"],
  ["blenderBuild", paths.blenderBuild, "blender-rig-build-report.json"],
  ["blenderProbe", paths.blenderProbe, "blender-coordinate-probe.json"],
  ["blend", paths.blend, "source/pack-opening-gate04-r019.blend"],
  ["fbx", paths.fbx, "source/PackOpeningGate04R019PackOnlyRig.fbx"],
  ["blenderSealed", paths.blenderSealed, "blender/sealed.png"],
  ["blenderFormed", paths.blenderFormed, "blender/formed-mouth.png"],
  ["blenderRise", paths.blenderRise, "blender/continuous-rise.png"],
  ["sourceManifest", paths.sourceManifest, "r019-source-manifest.json"],
  ["structuralResults", paths.structuralResults, "r019-structural-check-results.xml"],
  ["structuralLog", paths.structuralLog, "r019-structural-check.log"],
  ["editModeResults", paths.editModeResults, "r019-editmode-results.xml"],
  ["editModeLog", paths.editModeLog, "r019-editmode-tests.log"],
  ["preflightLog", paths.preflightLog, "r019-preflight.log"],
  ["preflightReport", paths.preflightReport, "r019-preflight-report.json"],
  ["preflightResults", paths.preflightResults, "r019-preflight-results.xml"],
  ["r019Calibration", paths.r019Calibration, "orientation/r019-orientation-calibration.json"],
  ["r019CalibrationFrame", paths.r019CalibrationFrame, "orientation/r019-pack-artwork.png"],
  ["r017CalibrationFrame", paths.r017CalibrationFrame, "orientation/r017-mirror-control.png"],
  ["sealedFrame", paths.sealedFrame, "preflight/sealed-state.png"],
  ["formedFrame", paths.formedFrame, "preflight/formed-mouth-070.png"],
  ["containedFrame", paths.containedFrame, "preflight/case-contained-090.png"],
  ["topCrimpId", paths.topCrimpId, "diagnostics/top-crimp-id.png"],
  ["titleBandId", paths.titleBandId, "diagnostics/archive-title-band-id.png"],
  ["material070", paths.material070, "diagnostics/mouth-material-id-070.png"],
  ["material090", paths.material090, "diagnostics/mouth-material-id-090.png"],
  ["visibleCaseId", paths.visibleCaseId, "diagnostics/case-visible-id-090.png"],
  ["unoccludedCaseId", paths.unoccludedCaseId, "diagnostics/case-unoccluded-id-090.png"],
  ["occludedCaseId", paths.occludedCaseId, "diagnostics/case-front-occlusion-id-090.png"],
  ["cc0Audit", paths.cc0Audit, "source/make-it-shine-r013-source-audit.json"],
  ["cc0Contract", paths.cc0Contract, "source/make-it-shine-source-contract.json"]
]) {
  copied[key] = copyAbsolute(source, `${evidenceRoot}/${relative}`);
}
for (const source of walk(templateRoot).filter((file) => /\.(cs|shader)$/u.test(file))) {
  const relative = path.relative(templateRoot, source);
  copied[`template:${relative}`] = copyAbsolute(
    source,
    `${evidenceRoot}/source/isolated-template/${relative}`
  );
}

const preservedRejections = [
  ["R015", paths.r015Rejection],
  ["R016", paths.r016Rejection],
  ["R017", paths.r017Rejection],
  ["R018", paths.r018Rejection]
].map(([revision, file]) => ({
  revision,
  path: path.relative(repoRoot, file),
  sha256: sha256File(file)
}));
const sourceMapping = writeJson(
  `${evidenceRoot}/r019-source-mapping.json`,
  {
    schema: "premium-display-case-gate04-r019-source-mapping.v1",
    repairScope: [
      "place the thin 3D top crimp above physical printed pixels",
      "reflect only the strip and tab for rendered top-right pull",
      "separate the short silver liner from the recessed dark cavity",
      "raise the one live case and add one narrow warm-neutral mouth bounce"
    ],
    unchanged: [
      "identity-oriented 384x512 front artwork",
      "seven normalized pose values and timing",
      "CC0 discard curve and local contour mapping",
      "assembled Premium Display Case prefab and ContentSlot",
      "canonical scenes, packages, shipping assets, particles, and device state"
    ],
    sourceAudit: {
      audit: copied.cc0Audit,
      contract: copied.cc0Contract,
      sourceCommit: "88842be0063b5b0b75e82ed6572752a37a13c82b",
      effectIntensityDuringPreflight: 0
    },
    r019Preflight: copied.preflightReport,
    r019Frames: {
      sealed: copied.sealedFrame,
      formedMouth070: copied.formedFrame,
      containedCase090: copied.containedFrame,
      materialId070: copied.material070,
      caseVisibleId090: copied.visibleCaseId
    },
    priorRejectedEvidence: preservedRejections,
    sourceControl: {
      r018ControlFbxSha256:
        "affe0a519712596660800dffb7d6b33126886defcaee9a33a658e97a79ca2f46",
      r019FbxSha256: copied.fbx.sha256
    },
    shippingReady: false,
    physicalPhoneInstalled: false
  }
);
const selfRejection = writeJson(
  `${evidenceRoot}/r019-preflight-self-rejection.json`,
  {
    schema: "premium-display-case-gate04-r019-preflight-self-rejection.v1",
    outcome: "self-rejected",
    reviewedAt: now,
    failedCondition: {
      id: linerFailure.id,
      evidence:
        "At t=0.700, the full-resolution material-ID capture has visibleCavityPixels=0; the required minimum is 128.",
      report: copied.preflightReport,
      result: copied.preflightResults,
      screenshot: copied.material070
    },
    passedPhysicalConditions: {
      artworkIdentityMargin:
        preflight.orientationCalibration.r019.identityMargin,
      crimpBottomViewportY:
        preflight.sealedRender.topCrimpLowestViewportY,
      archiveTitleTopViewportY:
        preflight.sealedRender.archiveTitleTopViewportY,
      stripRootViewportX:
        preflight.formedMouth.releasedSealRootViewport.x,
      frontOcclusionPixels:
        preflight.caseContainment.occludedCasePixelsByFront,
      contiguousFrontOcclusionPixels:
        preflight.caseContainment.largestFrontOcclusionClusterPixels
    },
    fullSizeBeautyInspection: {
      mode: "native-size 1206x2622 Unity frame inspection without resampling",
      verdict:
        "Rejected. The formed-mouth frame does not show a distinct recessed dark cavity behind the silver liner. The contained-case beauty frame does not plainly read as a dark display case held in the upper mouth.",
      formedMouth070: copied.formedFrame,
      containedCase090: copied.containedFrame,
      caseVisibleId090: copied.visibleCaseId
    },
    preservedRejectedEvidence: preservedRejections,
    stopCondition:
      "Preflight failed. No scrub, full proof, effect tuning, candidate registration, FDB or implementation-status update, canonical asset change, build, install, or device work ran.",
    shippingReady: false,
    physicalPhoneInstalled: false,
    statusText: "视觉批准待确认，未推送手机"
  }
);

const records = [
  artifact(manifest, "premium-display-case-gate04-r019-staging-bootstrap", copied.stagingBootstrap, "architecture-isolated-preparation", "process", "Creates immutable R019 staging from R018."),
  artifact(manifest, "premium-display-case-gate04-r019-repair-builder", copied.blenderBuilder, "architecture-pack-only-builder", "process", "Builds the bounded Pack-mouth repair."),
  artifact(manifest, "premium-display-case-gate04-r019-blender-probe-builder", copied.blenderProbeBuilder, "architecture-coordinate-validator", "process", "Probes saved Blender crimp, seam, mouth, and strip coordinates."),
  artifact(manifest, "premium-display-case-gate04-r019-isolated-preparation", copied.prepare, "architecture-isolated-preparation", "process", "Creates a separate Unity project with immutable R017 and R018 controls."),
  artifact(manifest, "premium-display-case-gate04-r019-rig-build", copied.blenderBuild, "architecture-blender-validation", "validation", "Deterministic R019 Pack-only Blender rebuild."),
  artifact(manifest, "premium-display-case-gate04-r019-coordinate-probe", copied.blenderProbe, "architecture-coordinate-validator", "validation", "Blender confirms crimp-above-print and reflected strip root."),
  artifact(manifest, "premium-display-case-gate04-r019-blend", copied.blend, "architecture-pack-only-rig", "process", "R019 Pack-only Blender source; no case geometry is baked."),
  artifact(manifest, "premium-display-case-gate04-r019-rig-fbx", copied.fbx, "architecture-pack-only-fbx", "process", "R019 Pack-only FBX with six authored blend shapes."),
  artifact(manifest, "premium-display-case-gate04-r019-source-manifest", copied.sourceManifest, "architecture-source-boundary", "validation", "Isolated-source manifest preserves the case, ContentSlot, and shipping boundary."),
  artifact(manifest, "premium-display-case-gate04-r019-cc0-audit", copied.cc0Audit, "architecture-source-audit", "validation", "CC0 audit retained with the unchanged source mapping."),
  artifact(manifest, "premium-display-case-gate04-r019-cc0-contract", copied.cc0Contract, "architecture-source-audit", "validation", "CC0 source contract retained with the unchanged discard curve."),
  artifact(manifest, "premium-display-case-gate04-r019-structural-results", copied.structuralResults, "architecture-focused-tests", "validation", "Isolated structural checks emitted 6/6 passing results."),
  artifact(manifest, "premium-display-case-gate04-r019-editmode-results", copied.editModeResults, "architecture-focused-tests", "validation", "Isolated Unity EditMode results emitted 8/8 passing tests."),
  artifact(manifest, "premium-display-case-gate04-r019-preflight-results", copied.preflightResults, "architecture-preflight-results", "validation", "Actual Unity preflight emitted 15 checks with one failure."),
  artifact(manifest, "premium-display-case-gate04-r019-preflight-report", copied.preflightReport, "architecture-preflight-report", "validation", "Full-resolution Unity preflight captures and screen-space measurements."),
  artifact(manifest, "premium-display-case-gate04-r019-orientation-calibration", copied.r019Calibration, "architecture-orientation-calibration", "validation", "R019 identity wins while the immutable R017 control remains mirrored."),
  artifact(manifest, "premium-display-case-gate04-r019-formed-mouth-frame", copied.formedFrame, "architecture-before-after-frame", "validation", "Actual full-size t=0.700 formed-mouth frame."),
  artifact(manifest, "premium-display-case-gate04-r019-contained-case-frame", copied.containedFrame, "architecture-before-after-frame", "validation", "Actual full-size t=0.900 contained-case beauty frame."),
  artifact(manifest, "premium-display-case-gate04-r019-material-id-070", copied.material070, "architecture-preflight-diagnostic", "validation", "Actual t=0.700 material-ID capture proves the cavity has zero visible pixels."),
  artifact(manifest, "premium-display-case-gate04-r019-source-mapping", sourceMapping, "architecture-source-mapping", "validation", "Records scope, source audit, and R015–R018 preservation."),
  artifact(manifest, "premium-display-case-gate04-r019-self-rejection", selfRejection, "architecture-full-size-review", "validation", "One strict preflight failure stops R019 before scrub.")
];
const existingIds = new Set(manifest.assets.map((asset) => asset.id));
for (const record of records) {
  if (existingIds.has(record.id)) {
    throw new Error(`Immutable R019 asset ID already exists: ${record.id}`);
  }
  manifest.assets.push(record);
  stage.artifactIds.push(record.id);
}
stage.artifactIds = [...new Set(stage.artifactIds)];
stage.historicalDecisions = [
  ...(stage.historicalDecisions || []),
  {
    revision: stage.revision,
    status: stage.status,
    decision: stage.decision,
    evidenceReview: stage.evidenceReview,
    supersededBy: "gate04-r019-pack-mouth-preflight",
    supersededAt: now
  }
];
stage.revision += 1;
stage.status = "draft";
stage.reviewArtifactIds = [];
stage.validations = [
  {
    id: "r015-r018-rejection-evidence-preserved",
    status: "pass",
    evidence: preservedRejections.map((item) => `${item.revision}:${item.sha256}`).join(", ")
  },
  {
    id: "r019-blender-pack-mouth-probe",
    status: "pass",
    evidence: `${copied.blenderProbe.path}; printed top, raised crimp, upper mouth, and reflected strip root pass.`
  },
  {
    id: "r019-isolated-structural-checks",
    status: "pass",
    evidence: `${copied.structuralResults.path}; 6/6 pass.`
  },
  {
    id: "r019-isolated-editmode-checks",
    status: "pass",
    evidence: `${copied.editModeResults.path}; 8/8 pass.`
  },
  {
    id: "r019-actual-unity-preflight",
    status: "fail",
    evidence: `${copied.preflightResults.path}; 1/15 failure: t=0.700 cavity has 0 visible pixels, below 128.`
  },
  {
    id: "r019-stop-before-scrub",
    status: "pass",
    evidence: "Preflight failure stopped before scrub, full proof, effect tuning, candidate registration, docs, build, install, or device work."
  }
];
stage.decision = {
  action: "self-reject",
  notes:
    "R019 fixes crimp placement, right-side pull, and front-lip occlusion, but the t=0.700 cavity is not visibly layered. Stop without tuning.",
  decidedAt: now,
  decidedBy: "agent-emitted-r019-preflight-review",
  approvalRequestAllowed: false,
  finalAuthority: "latest-explicit-chat-instruction",
  selfRejectionRecord: selfRejection.path
};
stage.evidenceReview = {
  architectureRevision: 7,
  evidenceRevision: 19,
  iteration: "r019-pack-mouth-preflight-self-rejection",
  disposition: "self-rejected",
  primaryArtifact: selfRejection.path,
  beforeAfterScreenEvidence: [
    copied.formedFrame.path,
    copied.containedFrame.path,
    copied.material070.path
  ],
  shownToUserForApproval: false,
  visualApproval: "not-requested-preflight-gate-failed",
  statusText: "视觉批准待确认，未推送手机"
};
const staleReason =
  "Gate 04 R019 preflight self-rejected because the t=0.700 cavity is not visibly layered.";
for (const downstream of manifest.stages.slice(4)) {
  downstream.status = "stale";
  downstream.staleReason = staleReason;
}
manifest.model.status = "gate04-r019-preflight-self-rejected";
manifest.currentState = {
  ...manifest.currentState,
  activeStageId: "04-architecture",
  activeStageStatus: "draft",
  activeIteration: "r019-pack-mouth-preflight-self-rejection",
  visualApproval: "gate04-r019-self-rejected-preflight",
  diagnosis:
    "R019 fixes the rendered crimp, top-right strip, and front-lip coverage, but t=0.700 has no visible recessed cavity. No scrub ran.",
  architectureApproval: {
    stageId: "04-architecture",
    architectureRevision: 7,
    evidenceRevision: 19,
    evidenceIteration: "r019-pack-mouth-preflight-self-rejection",
    userApprovalQuote: null,
    decisionState: "self-rejected-preflight",
    approvalRequestAllowed: false,
    gate05Status: "stale"
  },
  motionCorrection: {
    ...manifest.currentState.motionCorrection,
    gate04Status: "r019-preflight-self-rejected",
    currentEvidenceRevision: 19,
    currentEvidenceIteration: "r019-pack-mouth-preflight-self-rejection",
    rejectedEvidenceRevisions: [
      ...(manifest.currentState.motionCorrection?.rejectedEvidenceRevisions || []),
      19
    ],
    selfRejectedIterations: [
      ...(manifest.currentState.motionCorrection?.selfRejectedIterations || []),
      "r019-pack-mouth-preflight"
    ],
    shippingPreviewApproved: false,
    deviceAccepted: false
  },
  affectedGateAssessment: {
    earliestAffectedGate: "04-architecture",
    reason: staleReason,
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
    "Gate 04 R019 isolated Pack-mouth repair self-rejected after one full-resolution preflight failure. No scrub or shipping work ran.",
  statusText: "视觉批准待确认，未推送手机"
};
manifest.revision += 1;
manifest.updatedAt = now;
refreshStageDigest(manifest, stage);
const event = {
  id: crypto.randomUUID(),
  type: "gate04-r019-pack-mouth-preflight-self-rejected",
  modelId: "premium-display-case",
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "04-architecture",
  stageRevision: stage.revision,
  architectureRevision: 7,
  evidenceRevision: 19,
  evidenceIteration: "r019-pack-mouth-preflight-self-rejection",
  sourceTask: "cursor-task:premium-display-case-gate04-r019-20260831",
  preflight: {
    checks: 15,
    failures: 1,
    failedCondition: linerFailure.id,
    visibleCavityPixels: preflight.formedMouthMaterials.visibleCavityPixels,
    results: copied.preflightResults.path
  },
  selfRejectionRecord: selfRejection.path,
  fullProofStarted: false,
  scrubStarted: false,
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
  evidenceRoot,
  preflight: "self-rejected",
  addedAssets: records.length
}, null, 2));
