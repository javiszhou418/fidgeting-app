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
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r017-test-calibration";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-017";
const isolatedRoot = "/tmp/FidgetingApp-PackOpening-R017-Calibration-20260831";
const r016EvidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-016";
const expectedPipelineRevision = 95;
const expectedStageRevision = 27;
const now = new Date().toISOString();

function requireFile(file) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    throw new Error(`Missing required R017 file: ${file}`);
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

function artifact(manifest, id, relativePath, slot, role, note) {
  const absolute = resolveRepoPath(relativePath);
  requireFile(absolute);
  const contractStage = manifest.stages.find(
    (stage) => stage.id === "03-contract"
  );
  const sourceAssetIds = contractStage?.artifactIds || [];
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
      name: "Gate 04 R017 isolated test-calibration proof",
      version: "r017-scrub-visual-self-rejected",
      recipe:
        "Immutable R016 Pack-only FBX, isolated Unity 6000.5.6f1 URP17 real-frame capture, and native-pixel visual review"
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

const paths = {
  calibration: path.join(stagingRoot, "r017-test-calibration.json"),
  prepare: path.join(stagingRoot, "prepare_r017_calibrated_isolated.mjs"),
  runtimeCapture: path.join(
    isolatedRoot,
    "Assets/IsolatedProofR017/Runtime/IsolatedR017ProofCapture.cs"
  ),
  runtimeBuilder: path.join(
    isolatedRoot,
    "Assets/IsolatedProofR017/Editor/IsolatedR017ProofBuilder.cs"
  ),
  tests: path.join(
    isolatedRoot,
    "Assets/IsolatedProofR017/Tests/Editor/IsolatedR017ProofTests.cs"
  ),
  importer: path.join(
    isolatedRoot,
    "Assets/Source/R017/PackOpeningGate04R017PackOnlyRig.fbx.meta"
  ),
  staticReport: path.join(
    isolatedRoot,
    "Captures/r017-preflight/r017-pre-capture-static-report.json"
  ),
  staticResults: path.join(
    isolatedRoot,
    "Captures/r017-preflight/r017-pre-capture-static-results.xml"
  ),
  structuralResults: path.join(isolatedRoot, "r017-structural-check-results.xml"),
  initialTestResults: path.join(isolatedRoot, "r017-editmode-results.xml"),
  calibratedTestResults: path.join(
    isolatedRoot,
    "r017-editmode-calibrated-results.xml"
  ),
  calibratedTestLog: path.join(
    isolatedRoot,
    "r017-editmode-calibrated-tests.log"
  ),
  scrubReport: path.join(isolatedRoot, "Captures/r017-scrub/scrub-report.json"),
  scrubResults: path.join(
    isolatedRoot,
    "Captures/r017-scrub/r017-scrub-results.xml"
  ),
  scrubLog: path.join(isolatedRoot, "r017-scrub.log")
};
const absolutePaths = Object.fromEntries(
  Object.entries(paths).map(([key, value]) => [
    key,
    path.isAbsolute(value) ? value : resolveRepoPath(value)
  ])
);
for (const required of Object.values(absolutePaths)) {
  requireFile(required);
}

const r016StaticXml = fs.readFileSync(
  resolveRepoPath(`${r016EvidenceRoot}/r016-pre-capture-static-results.xml`),
  "utf8"
);
const r016StructuralXml = fs.readFileSync(
  resolveRepoPath(`${r016EvidenceRoot}/r016-structural-check-results.xml`),
  "utf8"
);
const staticReport = JSON.parse(
  fs.readFileSync(absolutePaths.staticReport, "utf8")
);
const scrubReport = JSON.parse(
  fs.readFileSync(absolutePaths.scrubReport, "utf8")
);
const staticResults = fs.readFileSync(absolutePaths.staticResults, "utf8");
const structuralResults = fs.readFileSync(
  absolutePaths.structuralResults,
  "utf8"
);
const initialTestResults = fs.readFileSync(
  absolutePaths.initialTestResults,
  "utf8"
);
const calibratedTestResults = fs.readFileSync(
  absolutePaths.calibratedTestResults,
  "utf8"
);
const r016RigRelative =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r016-repair/PackOpeningGate04R016PackOnlyRig.fbx";
const r016RigSha256 =
  "1a9c8f5b066cc2a24cf629c0a0ffa9eaaec05279af0e0171ab2f341731dabe66";
const r017Rig = path.join(
  isolatedRoot,
  "Assets/Source/R017/PackOpeningGate04R017PackOnlyRig.fbx"
);
requireFile(r017Rig);
for (const reviewFrame of [0, 12, 26]) {
  requireFile(path.join(
    isolatedRoot,
    `Captures/r017-scrub/frames/frame-${String(reviewFrame).padStart(4, "0")}.png`
  ));
  requireFile(path.join(
    isolatedRoot,
    `Captures/r017-scrub/review-100pct/frame-${String(reviewFrame).padStart(4, "0")}-pack-native-pixels.png`
  ));
}
if (
  !/tests="5" failures="1"/.test(r016StaticXml)
  || !/tests="5" failures="0"/.test(r016StructuralXml)
) {
  throw new Error("R016 static and structural result accounting changed.");
}
if (
  !staticReport.passed
  || !/tests="6" failures="0"/.test(staticResults)
  || staticReport.frontFoilDeltaToleranceFraction < 0.0049
  || staticReport.frontFoilDeltaToleranceFraction > 0.0051
  || staticReport.frontFoilDeltaRelativeError > 0.005
  || !staticReport.mouthScreenVisibility
  || staticReport.mouthScreenVisibility.meanRgbDelta < 0.01
  || staticReport.mouthScreenVisibility.changedPixelFraction < 0.05
) {
  throw new Error("R017 preflight calibration did not pass.");
}
if (
  !/tests="5" failures="0"/.test(structuralResults)
  || !/total="7" passed="7" failed="0"/.test(calibratedTestResults)
  || !/total="7" passed="6" failed="1"/.test(initialTestResults)
) {
  throw new Error("R017 focused test evidence is incomplete.");
}
if (
  scrubReport.width !== 1206
  || scrubReport.height !== 2622
  || scrubReport.fps !== 60
  || scrubReport.frameCount !== 31
  || scrubReport.frameBarrierCaptureCount !== 31
  || scrubReport.frameBarrierAdvancedCount !== 31
  || !scrubReport.checks?.every((check) => check.passed)
) {
  throw new Error("R017 scrub diagnostics did not pass.");
}
if (sha256File(r017Rig) !== r016RigSha256) {
  throw new Error("R017 changed the immutable R016 Pack-only FBX.");
}

const manifest = loadManifest("premium-display-case");
if (manifest.revision !== expectedPipelineRevision) {
  throw new Error(
    `Expected pipeline revision ${expectedPipelineRevision}; found ${manifest.revision}.`
  );
}
const stage = manifest.stages.find((item) => item.id === "04-architecture");
if (
  !stage
  || stage.revision !== expectedStageRevision
  || stage.status !== "draft"
) {
  throw new Error("Gate 04 is not at the expected R016 self-rejected state.");
}
const evidenceAbsolute = resolveRepoPath(evidenceRoot);
if (fs.existsSync(evidenceAbsolute)) {
  throw new Error(`Refusing to overwrite immutable Gate 04 revision: ${evidenceRoot}`);
}
fs.mkdirSync(evidenceAbsolute, { recursive: false });

const copied = {
  calibration: copyAbsolute(
    absolutePaths.calibration,
    `${evidenceRoot}/r017-test-calibration.json`
  ),
  preparation: copyAbsolute(
    absolutePaths.prepare,
    `${evidenceRoot}/prepare_r017_calibrated_isolated.mjs`
  ),
  runtimeCapture: copyAbsolute(
    absolutePaths.runtimeCapture,
    `${evidenceRoot}/source/IsolatedR017ProofCapture.cs`
  ),
  runtimeBuilder: copyAbsolute(
    absolutePaths.runtimeBuilder,
    `${evidenceRoot}/source/IsolatedR017ProofBuilder.cs`
  ),
  tests: copyAbsolute(
    absolutePaths.tests,
    `${evidenceRoot}/source/IsolatedR017ProofTests.cs`
  ),
  importer: copyAbsolute(
    absolutePaths.importer,
    `${evidenceRoot}/source/PackOpeningGate04R017PackOnlyRig.fbx.meta`
  ),
  staticReport: copyAbsolute(
    absolutePaths.staticReport,
    `${evidenceRoot}/r017-pre-capture-static-report.json`
  ),
  staticResults: copyAbsolute(
    absolutePaths.staticResults,
    `${evidenceRoot}/r017-pre-capture-static-results.xml`
  ),
  structuralResults: copyAbsolute(
    absolutePaths.structuralResults,
    `${evidenceRoot}/r017-structural-check-results.xml`
  ),
  initialTestResults: copyAbsolute(
    absolutePaths.initialTestResults,
    `${evidenceRoot}/r017-editmode-precalibration-results.xml`
  ),
  calibratedTestResults: copyAbsolute(
    absolutePaths.calibratedTestResults,
    `${evidenceRoot}/r017-editmode-results.xml`
  ),
  calibratedTestLog: copyAbsolute(
    absolutePaths.calibratedTestLog,
    `${evidenceRoot}/r017-editmode-tests.log`
  ),
  scrubReport: copyAbsolute(
    absolutePaths.scrubReport,
    `${evidenceRoot}/r017-scrub-report.json`
  ),
  scrubResults: copyAbsolute(
    absolutePaths.scrubResults,
    `${evidenceRoot}/r017-scrub-results.xml`
  ),
  scrubLog: copyAbsolute(
    absolutePaths.scrubLog,
    `${evidenceRoot}/r017-scrub.log`
  ),
  frame0000: copyAbsolute(
    path.join(isolatedRoot, "Captures/r017-scrub/frames/frame-0000.png"),
    `${evidenceRoot}/scrub/frames/frame-0000.png`
  ),
  frame0012: copyAbsolute(
    path.join(isolatedRoot, "Captures/r017-scrub/frames/frame-0012.png"),
    `${evidenceRoot}/scrub/frames/frame-0012.png`
  ),
  frame0026: copyAbsolute(
    path.join(isolatedRoot, "Captures/r017-scrub/frames/frame-0026.png"),
    `${evidenceRoot}/scrub/frames/frame-0026.png`
  ),
  review0000: copyAbsolute(
    path.join(
      isolatedRoot,
      "Captures/r017-scrub/review-100pct/frame-0000-pack-native-pixels.png"
    ),
    `${evidenceRoot}/scrub/review-100pct/frame-0000-pack-native-pixels.png`
  ),
  review0012: copyAbsolute(
    path.join(
      isolatedRoot,
      "Captures/r017-scrub/review-100pct/frame-0012-pack-native-pixels.png"
    ),
    `${evidenceRoot}/scrub/review-100pct/frame-0012-pack-native-pixels.png`
  ),
  review0026: copyAbsolute(
    path.join(
      isolatedRoot,
      "Captures/r017-scrub/review-100pct/frame-0026-pack-native-pixels.png"
    ),
    `${evidenceRoot}/scrub/review-100pct/frame-0026-pack-native-pixels.png`
  )
};

const sourceBoundary = writeJson(
  `${evidenceRoot}/r017-source-boundary.json`,
  {
    schema: "premium-display-case-gate04-r017-source-boundary.v1",
    revision: "R017",
    scope: "test and reporting calibration only",
    immutableR016Input: {
      fbx: r016RigRelative,
      sha256: r016RigSha256,
      copiedFbxSha256: sha256File(r017Rig),
      BlenderOrFbxGeometryChanged: false,
      casePrefabChanged: false,
      contentSlotChanged: false
    },
    unity: {
      version: "6000.5.6f1",
      urp: "17.5.0",
      importer: {
        globalScale: 1,
        useFileUnits: true,
        useFileScale: true,
        bakeAxisConversion: false,
        importBlendShapes: true,
        isReadable: true
      }
    },
    sourceFiles: [
      copied.runtimeCapture,
      copied.runtimeBuilder,
      copied.tests,
      copied.importer
    ].map((item) => ({ path: item.path, sha256: item.sha256 })),
    shippingReady: false
  }
);
const resultAccounting = writeJson(
  `${evidenceRoot}/r017-result-accounting.json`,
  {
    schema: "premium-display-case-gate04-r017-result-accounting.v1",
    r016: {
      preflight: "1 failed of 5; 4 passed",
      structural: "5 passed of 5",
      interpretation:
        "These are separate suites. The later 5/5 does not overturn the preflight threshold failure."
    },
    r017: {
      firstEditModeRun:
        "1 failed of 7 because the imported non-power-of-two texture reports a resized runtime width.",
      correctedEditModeRun:
        "7 passed of 7 after the assertion read the unchanged 384x512 source PNG bytes.",
      visualOrGeometryChanged: false
    }
  }
);
const visualSelfRejection = writeJson(
  `${evidenceRoot}/r017-scrub-visual-self-rejection.json`,
  {
    schema: "premium-display-case-gate04-r017-scrub-visual-self-rejection.v1",
    outcome: "self-rejected",
    reviewedAt: now,
    reviewMode: "native-pixel, no-resampling inspection",
    reviewedFrames: [
      copied.review0000,
      copied.review0012,
      copied.review0026
    ].map((item, index) => ({
      timeSeconds: [0.7, 0.9, 1.1333333333][index],
      path: item.path,
      sha256: item.sha256,
      nativePixelDimensions: [1206, 1360]
    })),
    failedVisualCriteria: [
      {
        id: "pack-artwork-upright",
        evidence:
          "FIDGET ARCHIVE, SERIES 01, and STANDARD are mirror-reversed in every reviewed frame. The vertical UV order passes, but the front artwork is not readable upright."
      },
      {
        id: "top-seal-narrow-peeled-foil-strip",
        evidence:
          "The opening is at the lower edge and reads as a broad stepped foil flap/rail. The top seal remains a straight full-width band, not a compact two-sided curl."
      }
    ],
    structuralScrubEvidence: {
      at090:
        "one stable live case ID, Pack visible, packDissolve=0, CaseContained",
      at1133:
        "same live case ID, Pack visible, packDissolve=0, CaseCrossingMouth",
      frameBarrier: "31 captures, 31 post-update Unity frames"
    },
    stopCondition:
      "Visual criteria failed. No full proof, clip encoding, Gate 04 candidate registration, shipping work, or device installation ran.",
    shippingReady: false,
    physicalPhoneInstalled: false,
    statusText: "视觉批准待确认，未推送手机"
  }
);

const records = [
  artifact(
    manifest,
    "premium-display-case-gate04-r017-calibration-contract",
    copied.calibration.path,
    "architecture-test-calibration",
    "process",
    "R017 calibrates the t=0.70 imported-mesh expectation to the source/exported temporal mix."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-preparation",
    copied.preparation.path,
    "architecture-isolated-preparation",
    "process",
    "Creates a separate R017 project from immutable R016 input without changing canonical Unity sources."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-runtime-capture",
    copied.runtimeCapture.path,
    "architecture-capture-source",
    "process",
    "R017 uses a relative imported-mesh tolerance and a projected mouth-screen visibility check."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-runtime-builder",
    copied.runtimeBuilder.path,
    "architecture-isolated-builder",
    "process",
    "R017 builds only the isolated Pack and the unchanged assembled case."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-focused-tests",
    copied.tests.path,
    "architecture-focused-tests",
    "process",
    "R017 checks the raw 384x512 PNG rather than importer-resized texture dimensions."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-importer",
    copied.importer.path,
    "architecture-isolated-importer",
    "validation",
    "The isolated R017 FBX importer preserves globalScale=1 and unbaked axis conversion."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-source-boundary",
    sourceBoundary.path,
    "architecture-source-boundary",
    "validation",
    "R017 uses the R016 FBX byte-for-byte and leaves case, ContentSlot, and canonical sources unchanged."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-static-results",
    copied.staticResults.path,
    "architecture-pre-capture-static-results",
    "validation",
    "Actual Play Mode static preflight: 6/6 pass after a post-update Unity frame."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-static-report",
    copied.staticReport.path,
    "architecture-pre-capture-static-report",
    "validation",
    "Records the relative delta tolerance and projected mouth-screen pixel change."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-test-accounting",
    resultAccounting.path,
    "architecture-test-accounting",
    "validation",
    "Separates R016's 1/5 preflight failure from its distinct 5/5 structural suite."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-precalibration-test-results",
    copied.initialTestResults.path,
    "architecture-focused-tests",
    "validation",
    "Preserves the first 6/7 test result caused by importer-resized texture dimensions."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-editmode-results",
    copied.calibratedTestResults.path,
    "architecture-focused-tests",
    "validation",
    "Filtered R017 EditMode tests: 7/7 pass."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-editmode-log",
    copied.calibratedTestLog.path,
    "architecture-focused-tests",
    "validation",
    "Unity Test Framework emitted the corrected R017 result XML."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-scrub-results",
    copied.scrubResults.path,
    "architecture-scrub-results",
    "validation",
    "Actual Unity 0.70–1.20 second scrub: 31 1206x2622 frames at 60 fps."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-scrub-report",
    copied.scrubReport.path,
    "architecture-scrub-report",
    "validation",
    "Records unchanged case identity, Pack presence, and post-update frame barriers."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-scrub-log",
    copied.scrubLog.path,
    "architecture-scrub-log",
    "validation",
    "The isolated Unity scrub completed without a capture exception."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-scrub-frame-070",
    copied.frame0000.path,
    "architecture-scrub-frame",
    "validation",
    "Actual full-size t=0.70 scrub frame."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-scrub-frame-090",
    copied.frame0012.path,
    "architecture-scrub-frame",
    "validation",
    "Actual full-size t=0.90 scrub frame."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-scrub-frame-1133",
    copied.frame0026.path,
    "architecture-scrub-frame",
    "validation",
    "Actual full-size t=1.133 scrub frame."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-scrub-review",
    visualSelfRejection.path,
    "architecture-full-size-review",
    "validation",
    "Native-pixel visual review self-rejected the mirror-reversed artwork and lower stepped foil flap."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-review-frame-090",
    copied.review0012.path,
    "architecture-scrub-frame",
    "validation",
    "Native-pixel t=0.90 visual review frame."
  ),
  artifact(
    manifest,
    "premium-display-case-gate04-r017-review-frame-1133",
    copied.review0026.path,
    "architecture-scrub-frame",
    "validation",
    "Native-pixel t=1.133 visual review frame."
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
    supersededBy: "gate04-r017-test-calibration-and-scrub",
    supersededAt: now
  }
];
stage.revision += 1;
stage.status = "draft";
stage.reviewArtifactIds = [];
stage.validations = [
  {
    id: "r016-result-accounting-preserved",
    status: "pass",
    evidence:
      `${resultAccounting.path}; R016 preflight was 1 failure of 5, while separate structural checks were 5/5.`
  },
  {
    id: "r017-source-exported-temporal-delta",
    status: "pass",
    evidence:
      `${copied.staticResults.path}; 0.044887602m matches the source/exported t=0.70 blend within 0.5 percent.`
  },
  {
    id: "r017-preflight-screen-visibility",
    status: "pass",
    evidence:
      `${copied.staticReport.path}; projected mouth region mean RGB delta 0.084201 and changed fraction 57.211 percent.`
  },
  {
    id: "r017-isolated-structural-checks",
    status: "pass",
    evidence: `${copied.structuralResults.path}; 5/5 pass.`
  },
  {
    id: "r017-isolated-editmode-checks",
    status: "pass",
    evidence: `${copied.calibratedTestResults.path}; 7/7 pass.`
  },
  {
    id: "r017-actual-unity-scrub",
    status: "pass",
    evidence:
      `${copied.scrubResults.path}; 4/4 pass, 31 actual 1206x2622 frames at 60 fps, each after a Unity frame advance.`
  },
  {
    id: "r017-native-pixel-visual-review",
    status: "fail",
    evidence:
      `${visualSelfRejection.path}; Pack text is mirror-reversed and the lower foil reads as a broad stepped flap, not a narrow top curl.`
  },
  {
    id: "r017-no-follow-on-proof-or-device-work",
    status: "pass",
    evidence:
      "Visual self-rejection stopped before full proof, video encoding, candidate registration, shipping work, and device installation."
  }
];
stage.decision = {
  action: "self-reject",
  notes:
    "R017 corrected only static test semantics. The calibrated real-frame scrub passed structural checks but failed native-pixel visual review. Stop without another visual iteration.",
  decidedAt: now,
  decidedBy: "agent-emitted-scrub-visual-review",
  approvalRequestAllowed: false,
  finalAuthority: "latest-explicit-chat-instruction",
  selfRejectionRecord: visualSelfRejection.path
};
stage.evidenceReview = {
  architectureRevision: 7,
  evidenceRevision: 17,
  iteration: "r017-test-calibration-and-scrub-visual-self-rejection",
  disposition: "self-rejected",
  primaryArtifact: visualSelfRejection.path,
  fullSizeFramesReviewed: [
    copied.review0000,
    copied.review0012,
    copied.review0026
  ].map((item) => item.path),
  shownToUserForApproval: false,
  visualApproval: "not-requested-scrub-visual-gate-failed",
  statusText: "视觉批准待确认，未推送手机"
};
for (const downstream of manifest.stages.slice(4)) {
  downstream.status = "stale";
  downstream.staleReason =
    "Gate 04 R017 visual scrub self-rejected the mirror-reversed Pack artwork and lower stepped foil flap.";
}
manifest.model.status = "gate04-r017-scrub-visual-self-rejected";
manifest.currentState = {
  ...manifest.currentState,
  activeStageId: "04-architecture",
  activeStageStatus: "draft",
  activeIteration: "r017-test-calibration-and-scrub-visual-self-rejection",
  visualApproval: "gate04-r017-self-rejected-scrub-visual-criteria",
  diagnosis:
    "R017 corrected the static temporal delta assertion and passed actual-frame diagnostics. Native-pixel scrub review self-rejected the mirror-reversed Pack artwork and lower stepped foil flap. No full proof ran.",
  architectureApproval: {
    stageId: "04-architecture",
    architectureRevision: 7,
    evidenceRevision: 17,
    evidenceIteration: "r017-test-calibration-and-scrub-visual-self-rejection",
    userApprovalQuote: null,
    decisionState: "self-rejected-scrub-visual-criteria",
    approvalRequestAllowed: false,
    gate05Status: "stale"
  },
  motionCorrection: {
    ...manifest.currentState.motionCorrection,
    gate04Status: "r017-self-rejected-scrub-visual-criteria",
    currentEvidenceRevision: 17,
    currentEvidenceIteration:
      "r017-test-calibration-and-scrub-visual-self-rejection",
    rejectedEvidenceRevisions: [
      ...(manifest.currentState.motionCorrection?.rejectedEvidenceRevisions || []),
      17
    ],
    selfRejectedIterations: [
      ...(manifest.currentState.motionCorrection?.selfRejectedIterations || []),
      "r017-scrub-artwork-and-top-seal"
    ],
    shippingPreviewApproved: false,
    deviceAccepted: false
  },
  affectedGateAssessment: {
    earliestAffectedGate: "04-architecture",
    reason:
      "Gate 04 R017 scrub failed native-pixel visual criteria; no post-rejection tuning ran.",
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
    "Gate 04 R017 isolated test calibration passed technical checks but self-rejected the actual Unity scrub on visual criteria. No full proof or shipping work ran.",
  statusText: "视觉批准待确认，未推送手机"
};
manifest.revision += 1;
manifest.updatedAt = now;
refreshStageDigest(manifest, stage);

const event = {
  id: crypto.randomUUID(),
  type: "gate04-r017-test-calibration-scrub-self-rejected",
  modelId: "premium-display-case",
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "04-architecture",
  stageRevision: stage.revision,
  architectureRevision: 7,
  evidenceRevision: 17,
  evidenceIteration: "r017-test-calibration-and-scrub-visual-self-rejection",
  sourceTask: "cursor-task:premium-display-case-gate04-r017-20260831",
  calibration: {
    expectedDeltaMeters:
      staticReport.sourceExportedExpectedFrontFoilDeltaMeters,
    toleranceFraction: staticReport.frontFoilDeltaToleranceFraction,
    actualDeltaMeters: staticReport.frontFoilMaxBakedDeltaMeters
  },
  scrub: {
    startSeconds: scrubReport.startSeconds,
    endSeconds: scrubReport.endSeconds,
    frames: scrubReport.frameCount,
    frameBarrier: [
      scrubReport.frameBarrierCaptureCount,
      scrubReport.frameBarrierAdvancedCount
    ]
  },
  selfRejectionRecord: visualSelfRejection.path,
  addedAssetIds,
  fullProofStarted: false,
  approvalRequestAllowed: false,
  shippingReady: false,
  physicalPhoneInstalled: false,
  deviceAccepted: false,
  statusText: "视觉批准待确认，未推送手机"
};
saveManifest(manifest, event);
console.log(
  JSON.stringify({
    pipelineRevision: manifest.revision,
    stageRevision: stage.revision,
    stageStatus: stage.status,
    evidenceRoot,
    visualVerdict: "self-rejected",
    addedAssets: addedAssetIds.length
  }, null, 2)
);
