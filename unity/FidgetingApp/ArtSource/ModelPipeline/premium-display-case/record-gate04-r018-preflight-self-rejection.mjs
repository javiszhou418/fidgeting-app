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
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r018-coordinate-orientation";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-018";
const isolatedRoot =
  "/tmp/FidgetingApp-PackOpening-R018-CoordinateOrientation-20260831";
const expectedPipelineRevision = 96;
const expectedStageRevision = 28;
const now = new Date().toISOString();

function requireFile(file) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    throw new Error(`Missing required R018 file: ${file}`);
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
      name: "Gate 04 R018 isolated coordinate-orientation repair",
      version: "r018-preflight-self-rejected",
      recipe:
        "Deterministic Blender Pack-only rebuild plus isolated Unity 6000.5.6f1 URP 17.5 preflight"
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
  "isolated-template/Assets/IsolatedProofR018"
);
const preflightRoot = path.join(isolatedRoot, "Captures/r018-preflight");
const paths = {
  blenderBuilder: path.join(stagingAbsolute, "build_pack_only_rig.py"),
  blenderProbeBuilder: path.join(
    stagingAbsolute,
    "probe_r018_blender_geometry.py"
  ),
  bootstrap: path.join(stagingAbsolute, "bootstrap_r018_staging.mjs"),
  prepare: path.join(stagingAbsolute, "prepare_r018_isolated.mjs"),
  blenderBuild: path.join(stagingAbsolute, "blender-rig-build-report.json"),
  blenderProbe: path.join(stagingAbsolute, "blender-coordinate-probe.json"),
  blend: path.join(stagingAbsolute, "pack-opening-gate04-r018.blend"),
  fbx: path.join(stagingAbsolute, "PackOpeningGate04R018PackOnlyRig.fbx"),
  blenderSealed: path.join(stagingAbsolute, "blender-sealed.png"),
  blenderFormed: path.join(stagingAbsolute, "blender-formed-mouth.png"),
  blenderRise: path.join(stagingAbsolute, "blender-continuous-rise.png"),
  sourceManifest: path.join(isolatedRoot, "r018-source-manifest.json"),
  structuralResults: path.join(isolatedRoot, "r018-structural-check-results.xml"),
  structuralLog: path.join(isolatedRoot, "r018-structural-check.log"),
  editModeResults: path.join(isolatedRoot, "r018-editmode-results.xml"),
  editModeLog: path.join(isolatedRoot, "r018-editmode-tests.log"),
  preflightLog: path.join(isolatedRoot, "r018-preflight.log"),
  preflightReport: path.join(preflightRoot, "r018-preflight-report.json"),
  preflightResults: path.join(preflightRoot, "r018-preflight-results.xml"),
  r018Calibration: path.join(
    preflightRoot,
    "orientation-calibration/r018-orientation-calibration.json"
  ),
  r018CalibrationFrame: path.join(
    preflightRoot,
    "orientation-calibration/r018-pack-artwork.png"
  ),
  r017CalibrationFrame: path.join(
    preflightRoot,
    "orientation-calibration/r017-mirror-control.png"
  ),
  sealedFrame: path.join(preflightRoot, "sealed-state.png"),
  formedFrame: path.join(preflightRoot, "formed-mouth-070.png"),
  containedFrame: path.join(preflightRoot, "case-contained-090.png"),
  unoccludedIdFrame: path.join(
    preflightRoot,
    "diagnostics/case-unoccluded-id-090.png"
  ),
  occludedIdFrame: path.join(
    preflightRoot,
    "diagnostics/case-front-occlusion-id-090.png"
  ),
  r017Before: absolute(
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-017/scrub/review-100pct/frame-0012-pack-native-pixels.png"
  ),
  r015Rejection: absolute(
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-015/self-rejection.json"
  ),
  r016Rejection: absolute(
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-016/self-rejection.json"
  ),
  r017Rejection: absolute(
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-017/r017-scrub-visual-self-rejection.json"
  )
};

for (const file of Object.values(paths)) requireFile(file);
for (const file of walk(templateRoot)) {
  if (/\.(cs|shader)$/u.test(file)) requireFile(file);
}
const preflight = JSON.parse(fs.readFileSync(paths.preflightReport, "utf8"));
const calibration = JSON.parse(fs.readFileSync(paths.r018Calibration, "utf8"));
const preflightXml = fs.readFileSync(paths.preflightResults, "utf8");
if (preflight.passed || calibration.passed !== true
  || !/tests="12" failures="3"/.test(preflightXml)) {
  throw new Error("R018 preflight result no longer matches the required stop.");
}
if (preflight.orientationCalibration?.r018?.winner !== "Identity"
  || preflight.orientationCalibration?.r017Control?.winner !== "HorizontalFlip") {
  throw new Error("R018 orientation regression result is incomplete.");
}
const manifest = loadManifest("premium-display-case");
if (manifest.revision !== expectedPipelineRevision) {
  throw new Error(
    `Expected pipeline revision ${expectedPipelineRevision}; found ${manifest.revision}.`
  );
}
const stage = manifest.stages.find((item) => item.id === "04-architecture");
if (!stage || stage.revision !== expectedStageRevision || stage.status !== "draft") {
  throw new Error("Gate 04 is not at the expected R017 self-rejected state.");
}
const evidenceAbsolute = absolute(evidenceRoot);
if (fs.existsSync(evidenceAbsolute)) {
  throw new Error(`Refusing to overwrite immutable evidence: ${evidenceRoot}`);
}
fs.mkdirSync(evidenceAbsolute, { recursive: false });

const copied = {};
for (const [key, source, relative] of [
  ["blenderBuilder", paths.blenderBuilder, "source/build_pack_only_rig.py"],
  ["blenderProbeBuilder", paths.blenderProbeBuilder, "source/probe_r018_blender_geometry.py"],
  ["bootstrap", paths.bootstrap, "source/bootstrap_r018_staging.mjs"],
  ["prepare", paths.prepare, "source/prepare_r018_isolated.mjs"],
  ["blenderBuild", paths.blenderBuild, "blender-rig-build-report.json"],
  ["blenderProbe", paths.blenderProbe, "blender-coordinate-probe.json"],
  ["blend", paths.blend, "source/pack-opening-gate04-r018.blend"],
  ["fbx", paths.fbx, "source/PackOpeningGate04R018PackOnlyRig.fbx"],
  ["blenderSealed", paths.blenderSealed, "blender/sealed.png"],
  ["blenderFormed", paths.blenderFormed, "blender/formed-mouth.png"],
  ["blenderRise", paths.blenderRise, "blender/continuous-rise.png"],
  ["sourceManifest", paths.sourceManifest, "r018-source-manifest.json"],
  ["structuralResults", paths.structuralResults, "r018-structural-check-results.xml"],
  ["structuralLog", paths.structuralLog, "r018-structural-check.log"],
  ["editModeResults", paths.editModeResults, "r018-editmode-results.xml"],
  ["editModeLog", paths.editModeLog, "r018-editmode-tests.log"],
  ["preflightLog", paths.preflightLog, "r018-preflight.log"],
  ["preflightReport", paths.preflightReport, "r018-preflight-report.json"],
  ["preflightResults", paths.preflightResults, "r018-preflight-results.xml"],
  ["r018Calibration", paths.r018Calibration, "orientation/r018-orientation-calibration.json"],
  ["r018CalibrationFrame", paths.r018CalibrationFrame, "orientation/r018-pack-artwork.png"],
  ["r017CalibrationFrame", paths.r017CalibrationFrame, "orientation/r017-mirror-control.png"],
  ["sealedFrame", paths.sealedFrame, "preflight/sealed-state.png"],
  ["formedFrame", paths.formedFrame, "preflight/formed-mouth-070.png"],
  ["containedFrame", paths.containedFrame, "preflight/case-contained-090.png"],
  ["unoccludedIdFrame", paths.unoccludedIdFrame, "diagnostics/case-unoccluded-id-090.png"],
  ["occludedIdFrame", paths.occludedIdFrame, "diagnostics/case-front-occlusion-id-090.png"],
  ["r017Before", paths.r017Before, "before/r017-mirror-lower-mouth-090.png"]
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
  ["R017", paths.r017Rejection]
].map(([revision, file]) => ({
  revision,
  path: path.relative(repoRoot, file),
  sha256: sha256File(file)
}));
const sourceMapping = writeJson(
  `${evidenceRoot}/r018-source-mapping.json`,
  {
    schema: "premium-display-case-gate04-r018-source-mapping.v1",
    repairScope: [
      "replace ambiguous lower-edge SEAM_Y with PACK_BOTTOM_Y and PACK_TOP_Y",
      "attach the tear seam and all mouth parts to physical PACK_TOP_Y",
      "preserve bottom-to-top rows and negative-Z camera-facing winding",
      "compensate the observed Unity FBX horizontal mirror through front source U"
    ],
    unchanged: [
      "seven authored pose values",
      "CC0 effect sources",
      "main camera",
      "unchanged assembled Premium Display Case",
      "particle settings",
      "timing",
      "canonical product and shipping assets"
    ],
    r017DiagnosisConfirmed: {
      priorFrame: copied.r017Before,
      r018BlenderProbe: copied.blenderProbe,
      result:
        "R017 used physical-top artwork V at the lower mouth anchor; R018 moves the seam to PACK_TOP_Y."
    },
    orientationCalibration: copied.r018Calibration,
    preflight: copied.preflightReport,
    priorRejectedEvidence: preservedRejections,
    sourceControl: {
      r017ControlFbxSha256:
        "1a9c8f5b066cc2a24cf629c0a0ffa9eaaec05279af0e0171ab2f341731dabe66",
      r018FbxSha256: copied.fbx.sha256
    },
    shippingReady: false,
    physicalPhoneInstalled: false
  }
);
const selfRejection = writeJson(
  `${evidenceRoot}/r018-preflight-self-rejection.json`,
  {
    schema: "premium-display-case-gate04-r018-preflight-self-rejection.v1",
    outcome: "self-rejected",
    reviewedAt: now,
    repairPassed: {
      orientationIdentityMargin:
        preflight.orientationCalibration.r018.identityMargin,
      r017HorizontalFlipMargin:
        preflight.orientationCalibration.r017Control.winnerMargin,
      physicalTopFrontDropMeters:
        preflight.formedMouth.frontTopDropMeters,
      mouthBoundsInUpperThird:
        preflight.formedMouth.allMouthBoundsInUpperThird
    },
    failedConditions: [
      {
        id: "sealed-top-crimp-is-above-fidget-archive",
        evidence:
          "Rendered Unity bounds report topCrimpMinY=0.066100 below archiveY=0.093312."
      },
      {
        id: "released-seal-is-compact-top-right-strip",
        evidence:
          "Rendered bounds place the strip left of the Pack center and its 0.0781 viewport width exceeds the 0.34 Pack-width limit."
      },
      {
        id: "contained-case-renders-inside-upper-mouth",
        evidence:
          "The actual ID render shows 86,325 visible case pixels in the upper mouth but only 7 pixels occluded by the front lip/sidewalls; required minimum is 16."
      }
    ],
    beforeAfterScreenEvidence: {
      beforeR017: copied.r017Before,
      afterR018Sealed: copied.sealedFrame,
      afterR018FormedMouth: copied.formedFrame,
      afterR018ContainedCase: copied.containedFrame,
      technicalOcclusion: copied.occludedIdFrame
    },
    stopCondition:
      "Preflight failed. No scrub, full proof, visual tuning, candidate registration, canonical asset change, build, install, or device work ran.",
    shippingReady: false,
    physicalPhoneInstalled: false,
    statusText: "视觉批准待确认，未推送手机"
  }
);

const records = [
  artifact(manifest, "premium-display-case-gate04-r018-repair-builder", copied.blenderBuilder, "architecture-pack-only-builder", "process", "R018 makes PACK_BOTTOM_Y, PACK_TOP_Y, the top tear seam, and front U compensation explicit."),
  artifact(manifest, "premium-display-case-gate04-r018-blender-probe-builder", copied.blenderProbeBuilder, "architecture-coordinate-validator", "process", "Queries the saved Blender scene rather than inferring physical edges from screenshots."),
  artifact(manifest, "premium-display-case-gate04-r018-staging-bootstrap", copied.bootstrap, "architecture-isolated-preparation", "process", "Creates R018 staging from R016 without mutating rejected revisions."),
  artifact(manifest, "premium-display-case-gate04-r018-isolated-preparation", copied.prepare, "architecture-isolated-preparation", "process", "Creates a separate Unity project and an immutable R017 mirror control."),
  artifact(manifest, "premium-display-case-gate04-r018-rig-build", copied.blenderBuild, "architecture-blender-validation", "validation", "Deterministic Blender R018 Pack-only rebuild report."),
  artifact(manifest, "premium-display-case-gate04-r018-coordinate-probe", copied.blenderProbe, "architecture-coordinate-validator", "validation", "Saved Blender coordinates prove top seam, upper-mouth attachment, front drop, and winding."),
  artifact(manifest, "premium-display-case-gate04-r018-blend", copied.blend, "architecture-pack-only-rig", "process", "R018 Pack-only Blender source; no case geometry is baked."),
  artifact(manifest, "premium-display-case-gate04-r018-rig-fbx", copied.fbx, "architecture-pack-only-fbx", "process", "R018 Pack-only FBX with six authored blend shapes."),
  artifact(manifest, "premium-display-case-gate04-r018-source-manifest", copied.sourceManifest, "architecture-source-boundary", "validation", "Separate project manifest records no canonical case, camera, timing, effect, particle, or shipping mutation."),
  artifact(manifest, "premium-display-case-gate04-r018-structural-results", copied.structuralResults, "architecture-focused-tests", "validation", "Isolated structural checks emitted 5/5 passing results."),
  artifact(manifest, "premium-display-case-gate04-r018-editmode-results", copied.editModeResults, "architecture-focused-tests", "validation", "Isolated Unity EditMode results emitted 7/7 passing tests."),
  artifact(manifest, "premium-display-case-gate04-r018-preflight-results", copied.preflightResults, "architecture-preflight-results", "validation", "Actual Unity preflight emitted 12 checks with 3 failures."),
  artifact(manifest, "premium-display-case-gate04-r018-preflight-report", copied.preflightReport, "architecture-preflight-report", "validation", "Actual Unity preflight captures and renderer/baked-mesh measurements."),
  artifact(manifest, "premium-display-case-gate04-r018-orientation-calibration", copied.r018Calibration, "architecture-orientation-calibration", "validation", "R018 identity beats all transforms; immutable R017 control selects horizontal flip."),
  artifact(manifest, "premium-display-case-gate04-r018-before-after", copied.formedFrame, "architecture-before-after-frame", "validation", "Actual R018 formed-mouth frame is retained alongside the R017 before frame."),
  artifact(manifest, "premium-display-case-gate04-r018-source-mapping", sourceMapping, "architecture-source-mapping", "validation", "Records source boundary, repair scope, and preservation of R015–R017 rejection evidence."),
  artifact(manifest, "premium-display-case-gate04-r018-self-rejection", selfRejection, "architecture-full-size-review", "validation", "Three preflight failures trigger the mandatory R018 stop.")
];
const existingIds = new Set(manifest.assets.map((asset) => asset.id));
for (const record of records) {
  if (existingIds.has(record.id)) {
    throw new Error(`Immutable R018 asset ID already exists: ${record.id}`);
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
    supersededBy: "gate04-r018-coordinate-orientation-preflight",
    supersededAt: now
  }
];
stage.revision += 1;
stage.status = "draft";
stage.reviewArtifactIds = [];
stage.validations = [
  {
    id: "r015-r017-rejection-evidence-preserved",
    status: "pass",
    evidence: preservedRejections.map((item) => `${item.revision}:${item.sha256}`).join(", ")
  },
  {
    id: "r018-blender-physical-coordinate-probe",
    status: "pass",
    evidence: `${copied.blenderProbe.path}; physical tear seam=PACK_TOP_Y, front top drop=0.021692m, all mouth parts above the physical upper-third boundary.`
  },
  {
    id: "r018-isolated-structural-checks",
    status: "pass",
    evidence: `${copied.structuralResults.path}; 5/5 pass.`
  },
  {
    id: "r018-isolated-editmode-checks",
    status: "pass",
    evidence: `${copied.editModeResults.path}; 7/7 pass.`
  },
  {
    id: "r018-orientation-calibration",
    status: "pass",
    evidence: `${copied.r018Calibration.path}; R018 identity margin=0.076571; immutable R017 control horizontal-flip margin=0.076601.`
  },
  {
    id: "r018-actual-unity-preflight",
    status: "fail",
    evidence: `${copied.preflightResults.path}; 3/12 failures: sealed crimp bound, compact top-right strip bound, and required case/front-occlusion pixels.`
  },
  {
    id: "r018-stop-before-scrub",
    status: "pass",
    evidence: "Preflight failure stopped before any R018 scrub, full proof, visual tuning, candidate registration, or device work."
  }
];
stage.decision = {
  action: "self-reject",
  notes:
    "R018 confirms the coordinate diagnosis and fixes horizontal artwork orientation, but three strict rendered preflight conditions fail. Stop without tuning.",
  decidedAt: now,
  decidedBy: "agent-emitted-r018-preflight-review",
  approvalRequestAllowed: false,
  finalAuthority: "latest-explicit-chat-instruction",
  selfRejectionRecord: selfRejection.path
};
stage.evidenceReview = {
  architectureRevision: 7,
  evidenceRevision: 18,
  iteration: "r018-coordinate-orientation-preflight-self-rejection",
  disposition: "self-rejected",
  primaryArtifact: selfRejection.path,
  beforeAfterScreenEvidence: [
    copied.r017Before.path,
    copied.formedFrame.path,
    copied.containedFrame.path
  ],
  shownToUserForApproval: false,
  visualApproval: "not-requested-preflight-gate-failed",
  statusText: "视觉批准待确认，未推送手机"
};
const staleReason =
  "Gate 04 R018 preflight self-rejected after three strict rendered physical conditions failed.";
for (const downstream of manifest.stages.slice(4)) {
  downstream.status = "stale";
  downstream.staleReason = staleReason;
}
manifest.model.status = "gate04-r018-preflight-self-rejected";
manifest.currentState = {
  ...manifest.currentState,
  activeStageId: "04-architecture",
  activeStageStatus: "draft",
  activeIteration: "r018-coordinate-orientation-preflight-self-rejection",
  visualApproval: "gate04-r018-self-rejected-preflight",
  diagnosis:
    "R018 confirmed the R017 lower-seam and horizontal-mirror defects. The repair passed Blender coordinates and identity calibration but failed three rendered Unity preflight conditions; no scrub ran.",
  architectureApproval: {
    stageId: "04-architecture",
    architectureRevision: 7,
    evidenceRevision: 18,
    evidenceIteration: "r018-coordinate-orientation-preflight-self-rejection",
    userApprovalQuote: null,
    decisionState: "self-rejected-preflight",
    approvalRequestAllowed: false,
    gate05Status: "stale"
  },
  motionCorrection: {
    ...manifest.currentState.motionCorrection,
    gate04Status: "r018-preflight-self-rejected",
    currentEvidenceRevision: 18,
    currentEvidenceIteration:
      "r018-coordinate-orientation-preflight-self-rejection",
    rejectedEvidenceRevisions: [
      ...(manifest.currentState.motionCorrection?.rejectedEvidenceRevisions || []),
      18
    ],
    selfRejectedIterations: [
      ...(manifest.currentState.motionCorrection?.selfRejectedIterations || []),
      "r018-coordinate-orientation-preflight"
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
    "Gate 04 R018 isolated coordinate-orientation repair self-rejected on three emitted Unity preflight failures. No scrub or shipping work ran.",
  statusText: "视觉批准待确认，未推送手机"
};
manifest.revision += 1;
manifest.updatedAt = now;
refreshStageDigest(manifest, stage);
const event = {
  id: crypto.randomUUID(),
  type: "gate04-r018-coordinate-orientation-preflight-self-rejected",
  modelId: "premium-display-case",
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "04-architecture",
  stageRevision: stage.revision,
  architectureRevision: 7,
  evidenceRevision: 18,
  evidenceIteration: "r018-coordinate-orientation-preflight-self-rejection",
  sourceTask: "cursor-task:premium-display-case-gate04-r018-20260831",
  orientation: {
    r018IdentityMargin: preflight.orientationCalibration.r018.identityMargin,
    r017HorizontalFlipMargin:
      preflight.orientationCalibration.r017Control.winnerMargin
  },
  preflight: {
    checks: 12,
    failures: 3,
    results: copied.preflightResults.path
  },
  beforeAfterScreenEvidence: [
    copied.r017Before.path,
    copied.formedFrame.path,
    copied.containedFrame.path
  ],
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
