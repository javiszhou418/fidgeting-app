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
} from "../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const repoRoot = "/Users/jiawei.zhou/Documents/Fidgeting app";
const stagingRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r025-portrait-projection-repair";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-025";
const isolatedRoot =
  "/tmp/FidgetingApp-PackOpening-R025-PortraitProjection-20260901-r04";
const staticRoot = path.join(isolatedRoot, "Captures/r025-preflight");
const scrubRoot = path.join(isolatedRoot, "Captures/r025-scrub");
const proofRoot = path.join(isolatedRoot, "Captures/r025-full-proof");
const expectedPipelineRevision = 100;
const expectedStageRevision = 32;
const r024RigHash =
  "a7a8c6ae76a89355cb2f74978f896bdcedba062b8fa02624ffae07803f4f8810";
const now = new Date().toISOString();
const resumeAfterEvidence = process.argv.includes("--resume-after-evidence");

function absolute(relative) {
  return resolveRepoPath(relative);
}

function requireDirectory(directory) {
  if (!fs.existsSync(directory) || !fs.statSync(directory).isDirectory()) {
    throw new Error(`Missing required directory: ${directory}`);
  }
}

function requireFile(file) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    throw new Error(`Missing required file: ${file}`);
  }
}

function copyAbsolute(source, destinationRelative) {
  requireFile(source);
  const destination = absolute(destinationRelative);
  if (fs.existsSync(destination)) {
    if (!resumeAfterEvidence || sha256File(source) !== sha256File(destination)) {
      throw new Error(`Refusing to overwrite immutable evidence: ${destinationRelative}`);
    }
    return {
      path: destinationRelative,
      sha256: sha256File(destination),
      sizeBytes: fs.statSync(destination).size
    };
  }
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(source, destination, fs.constants.COPYFILE_EXCL);
  return {
    path: destinationRelative,
    sha256: sha256File(destination),
    sizeBytes: fs.statSync(destination).size
  };
}

function walk(directory) {
  return fs.readdirSync(directory, { withFileTypes: true })
    .sort((left, right) => left.name.localeCompare(right.name))
    .flatMap((entry) => {
      const source = path.join(directory, entry.name);
      return entry.isDirectory() ? walk(source) : [source];
    });
}

function copyTree(sourceRoot, destinationRoot) {
  requireDirectory(sourceRoot);
  return walk(sourceRoot).map((source) => copyAbsolute(
    source,
    `${destinationRoot}/${path.relative(sourceRoot, source)}`
  ));
}

function writeJson(destinationRelative, value) {
  const destination = absolute(destinationRelative);
  if (fs.existsSync(destination)) {
    if (!resumeAfterEvidence) {
      throw new Error(`Refusing to overwrite immutable evidence: ${destinationRelative}`);
    }
    return {
      path: destinationRelative,
      sha256: sha256File(destination),
      sizeBytes: fs.statSync(destination).size
    };
  }
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.writeFileSync(destination, `${JSON.stringify(value, null, 2)}\n`, {
    flag: "wx"
  });
  return {
    path: destinationRelative,
    sha256: sha256File(destination),
    sizeBytes: fs.statSync(destination).size
  };
}

function artifact(manifest, id, copied, slot, role, note) {
  const contractStage = manifest.stages.find(
    (stage) => stage.id === "03-contract"
  );
  const sourceAssetIds = contractStage?.artifactIds || [];
  const sourceClaimIds = sourceAssetIds.flatMap((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)
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
      name: "Gate 04 R025 portrait projection diagnostic repair",
      version: "r025-isolated-candidate",
      recipe:
        "R024 FBX hash-preserving isolated Unity 6000.5.6f1 URP 17.5 target-aspect capture, segment-aware masks, static review, scrub, and proof"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: "gate04-isolated-candidate",
      assertedBy: "repository",
      note
    },
    sourceAssetIds,
    sourceClaimIds: [...new Set(sourceClaimIds)],
    wholeAssembledCaseOnly: true,
    explodeEligible: false,
    toyPrizeBundled: false,
    shippingEligible: false,
    reviewState: "pending-user-visual-approval"
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

function assertPass(report, label) {
  if (!report?.checks?.every((check) => check.passed)) {
    throw new Error(`${label} did not pass every emitted check.`);
  }
}

function amendDocs(pipelineRevision, stageRevision, copied) {
  const biblePath = absolute(
    "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"
  );
  const statusPath = absolute(
    "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"
  );
  const bible = fs.readFileSync(biblePath, "utf8");
  const status = fs.readFileSync(statusPath, "utf8");
  const fdbMarker = "| FDB-GAC-032 |";
  const priorRow = "| FDB-GAC-031 |";
  const statusMarker =
    "## 2026-08-31 Pack Opening Gate 04 R015 isolated candidate 自我拒绝";
  const statusHeading =
    "## 2026-09-01 Pack Opening Gate 04 R025 isolated candidate";
  if (
    resumeAfterEvidence
    && bible.includes(fdbMarker)
    && status.includes(statusHeading)
  ) {
    return;
  }
  if (bible.includes(fdbMarker) || status.includes(statusHeading)) {
    throw new Error("R025 documentation is already registered.");
  }
  const rowIndex = bible.indexOf(priorRow);
  if (rowIndex < 0) {
    throw new Error("Cannot locate the current Pack Opening FDB row.");
  }
  const rowEnd = bible.indexOf("\n", rowIndex);
  if (rowEnd < 0) {
    throw new Error("Cannot locate the end of FDB-GAC-031.");
  }
  const fdbRow = `| FDB-GAC-032 | R025 only repairs target-space technical projection and diagnostics for the immutable R024 Pack-only FBX. Each capture binds Camera aspect and target texture to \`1206 / 2622\`, then restores prior state. Segment masks use non-degenerate baked triangles and target-aspect labels; the live-case contrast uses original render queues and the physical target-space mouth. The R024 FBX hash, Blender rig, Pack geometry/UV/48-segment topology/art, case prefab/contentSlot/toy, timing, CC0 mapping, effects, canonical project, FanCard, packages, and user assets remain unchanged. | Candidate · User Visual Approval Pending · source task \`cursor-task:premium-display-case-gate04-r025-20260901\` · 2026-09-01 | Isolated Gate 04 candidate only · Gate 05–12 stale · \`shippingReady=false\` · no build/install/phone | pipeline rev \`${pipelineRevision}\` / Gate 04 rev \`${stageRevision}\`；${copied.staticReview.path}；${copied.proofReview.path}；视觉批准待确认，未推送手机 |\n`;
  const statusSection = `${statusHeading}

> **当前状态：pipeline rev=\`${pipelineRevision}\`。Gate 01–03=\`approved\`；Gate 04 stage rev=\`${stageRevision}\`=\`ready_for_review\`；R025=\`isolated candidate\`；Gate 05–12=\`stale\`；\`shippingReady=false\`；未 build／install／launch 物理手机。视觉批准待确认，未推送手机。**

- R025 只修诊断投影：每次 measurement/capture 前绑定 \`Camera.aspect=1206/2622=0.4599542\` 和目标 RenderTexture，释放时恢复。R024 原始 \`4:3=1.3333333\` 与 portrait factor=\`2.89884\` 的误判不再参与结果。
- 真实 Unity 静态 preflight=\`23/23\`：.50 seal \`7–47\` / open \`0–6\`，.70 seal \`19–47\` / open \`0–33\`，.90 seal \`34–47\` / open \`0–44\`。baked-triangle mask 与 exact-color ID bounds 最大差 \`1.19e-7≤.0015\`；.70 liner/cavity=\`2912/21791\`，.90=\`3051/35001\`；full live-case contrast=\`0.174388≥0.040\`。
- static native-size review、\`.70–1.20 s\` scrub=\`11/11\`，及 \`1.60 s / 96-frame\` normal proof 与 \`0.25x / 173-frame\` closeup 均来自 isolated Unity frames。case identity/scale 连续；无 crossfade、duplicate、blank 或 white frame；effects=\`0\`。
- isolated structural checks=\`7/7\`，R025 filtered EditMode=\`17/17\`，premium-display-case 与全 pipeline provenance validators 均为 errors/missing/unhashed=\`0/0/0\`。R024 FBX SHA-256=\`${r024RigHash}\`。
- R025 未接 canonical shipping runtime，未改 Pack、FBX、Blender、case prefab、\`contentSlot\`、toy、CC0 source mapping、timing、effects、FanCard、packages 或用户资产；没有 commit、push、purchase、download、device install。

`;
  const statusIndex = status.indexOf(statusMarker);
  if (statusIndex < 0) {
    throw new Error("Cannot locate the Pack Opening status insertion point.");
  }
  fs.writeFileSync(
    biblePath,
    `${bible.slice(0, rowEnd + 1)}${fdbRow}${bible.slice(rowEnd + 1)}`,
    "utf8"
  );
  fs.writeFileSync(
    statusPath,
    `${status.slice(0, statusIndex)}${statusSection}${status.slice(statusIndex)}`,
    "utf8"
  );
}

const stagingAbsolute = absolute(stagingRoot);
const evidenceAbsolute = absolute(evidenceRoot);
const templateRoot = path.join(
  stagingAbsolute,
  "isolated-template/Assets/IsolatedProofR025"
);
const sourceManifest = path.join(isolatedRoot, "r025-source-manifest.json");
const sourceRig = path.join(
  isolatedRoot,
  "Assets/Source/R024/PackOpeningGate04R024PackOnlyRig.fbx"
);
const preflight = JSON.parse(fs.readFileSync(
  path.join(staticRoot, "r025-preflight-report.json"),
  "utf8"
));
const scrub = JSON.parse(fs.readFileSync(
  path.join(scrubRoot, "scrub-report.json"),
  "utf8"
));
const proof = JSON.parse(fs.readFileSync(
  path.join(proofRoot, "unity-capture-report.json"),
  "utf8"
));

for (const directory of [
  stagingAbsolute,
  templateRoot,
  staticRoot,
  scrubRoot,
  proofRoot
]) requireDirectory(directory);
for (const file of [
  path.join(stagingAbsolute, "r025-inputs.json"),
  path.join(stagingAbsolute, "r025-projection-forensic-diagnosis.json"),
  path.join(stagingAbsolute, "r025-unity-preflight-environment-r04.json"),
  path.join(stagingAbsolute, "r025-static-full-size-review.json"),
  path.join(stagingAbsolute, "r025-scrub-full-size-review.json"),
  path.join(stagingAbsolute, "r025-full-proof-full-size-review.json"),
  sourceManifest,
  sourceRig,
  path.join(staticRoot, "r025-preflight-results.xml"),
  path.join(scrubRoot, "r025-scrub-results.xml"),
  path.join(proofRoot, "normal/normal-speed-proof.mp4"),
  path.join(proofRoot, "tear-quarter-speed/tear-quarter-speed-closeup.mp4"),
  path.join(isolatedRoot, "r025-structural-check-results-final.xml"),
  path.join(isolatedRoot, "r025-editmode-results-passed.xml")
]) requireFile(file);
if (sha256File(sourceRig) !== r024RigHash) {
  throw new Error("R025 altered the immutable R024 FBX hash.");
}
if (
  !preflight.passed
  || preflight.width !== 1206
  || preflight.height !== 2622
  || !preflight.accounting?.targetPortraitProjection?.passed
  || !preflight.accounting?.targetPortraitProjection
    ?.cameraAspectExactlyTarget
  || preflight.accounting?.targetPortraitProjection
    ?.maximumExactIdBoundsDelta > 0.0015
  || preflight.formedMouthMaterials?.visibleInnerLinerPixels !== 2912
  || preflight.formedMouthMaterials?.visibleCavityPixels !== 21791
  || preflight.containedMouthMaterials?.visibleInnerLinerPixels !== 3051
  || preflight.containedMouthMaterials?.visibleCavityPixels !== 35001
  || preflight.caseLegibility?.fullTargetMaskContrast < 0.04
) {
  throw new Error("R025 static preflight does not meet the candidate contract.");
}
if (
  scrub.status !== "captured-awaiting-full-size-visual-inspection"
  || scrub.frameCount !== 31
  || !scrub.targetProjectionApplied
  || !scrub.sameCaseIdentity
  || !scrub.noDuplicateCaseRenderers
  || !scrub.noPackCrossfade
  || !scrub.noBlankFrame
) {
  throw new Error("R025 scrub does not meet the candidate contract.");
}
if (
  proof.status !== "structural-pass-awaiting-full-size-visual-inspection"
  || proof.frames !== 96
  || proof.durationSeconds < 1.2
  || proof.durationSeconds > 1.8
  || !proof.targetProjectionApplied
  || proof.visualEffectsIntensity !== 0
  || proof.caseInstances !== 1
  || proof.caseGeometryBaked
) {
  throw new Error("R025 full proof does not meet the candidate contract.");
}
assertPass(preflight, "R025 static preflight");
assertPass(scrub, "R025 scrub");
assertPass(proof, "R025 full proof");

const manifest = loadManifest("premium-display-case");
if (manifest.revision !== expectedPipelineRevision) {
  throw new Error(
    `Expected pipeline revision ${expectedPipelineRevision}; found ${manifest.revision}.`
  );
}
const stage = manifest.stages.find((item) => item.id === "04-architecture");
if (!stage || stage.revision !== expectedStageRevision || stage.status !== "draft") {
  throw new Error("Gate 04 is not at the expected R024 self-rejected state.");
}
if (fs.existsSync(evidenceAbsolute) && !resumeAfterEvidence) {
  throw new Error(`Refusing to overwrite immutable evidence: ${evidenceRoot}`);
}
if (
  !resumeAfterEvidence
  &&
  fs.readFileSync(
    absolute("unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"),
    "utf8"
  ).includes("| FDB-GAC-032 |")
) {
  throw new Error("R025 FDB entry already exists.");
}

if (!fs.existsSync(evidenceAbsolute)) {
  fs.mkdirSync(evidenceAbsolute, { recursive: false });
}
const copied = {
  bootstrap: copyAbsolute(
    path.join(stagingAbsolute, "bootstrap_r025_staging.mjs"),
    `${evidenceRoot}/source/bootstrap_r025_staging.mjs`
  ),
  prepare: copyAbsolute(
    path.join(stagingAbsolute, "prepare_r025_isolated.mjs"),
    `${evidenceRoot}/source/prepare_r025_isolated.mjs`
  ),
  inputs: copyAbsolute(
    path.join(stagingAbsolute, "r025-inputs.json"),
    `${evidenceRoot}/r025-inputs.json`
  ),
  forensicDiagnosis: copyAbsolute(
    path.join(stagingAbsolute, "r025-projection-forensic-diagnosis.json"),
    `${evidenceRoot}/r025-projection-forensic-diagnosis.json`
  ),
  hostPreflight: copyAbsolute(
    path.join(stagingAbsolute, "r025-unity-preflight-environment-r04.json"),
    `${evidenceRoot}/preflight/r025-host-preflight.json`
  ),
  sourceManifest: copyAbsolute(
    sourceManifest,
    `${evidenceRoot}/r025-source-manifest.json`
  ),
  sourceTemplate: copyTree(
    templateRoot,
    `${evidenceRoot}/source/isolated-template/Assets/IsolatedProofR025`
  ),
  staticLog: copyAbsolute(
    path.join(isolatedRoot, "r025-preflight.log"),
    `${evidenceRoot}/r025-preflight.log`
  ),
  staticReport: copyAbsolute(
    path.join(staticRoot, "r025-preflight-report.json"),
    `${evidenceRoot}/preflight/r025-preflight-report.json`
  ),
  staticResults: copyAbsolute(
    path.join(staticRoot, "r025-preflight-results.xml"),
    `${evidenceRoot}/preflight/r025-preflight-results.xml`
  ),
  staticReview: copyAbsolute(
    path.join(stagingAbsolute, "r025-static-full-size-review.json"),
    `${evidenceRoot}/r025-static-full-size-review.json`
  ),
  staticFrames: [
    copyAbsolute(
      path.join(staticRoot, "tear-front-050.png"),
      `${evidenceRoot}/preflight/tear-front-050.png`
    ),
    copyAbsolute(
      path.join(staticRoot, "formed-mouth-070.png"),
      `${evidenceRoot}/preflight/formed-mouth-070.png`
    ),
    copyAbsolute(
      path.join(staticRoot, "case-contained-090.png"),
      `${evidenceRoot}/preflight/case-contained-090.png`
    )
  ],
  segmentLabels: copyTree(
    path.join(staticRoot, "diagnostics"),
    `${evidenceRoot}/preflight/diagnostics`
  ),
  structuralResults: copyAbsolute(
    path.join(isolatedRoot, "r025-structural-check-results-final.xml"),
    `${evidenceRoot}/tests/r025-structural-check-results.xml`
  ),
  editModeResults: copyAbsolute(
    path.join(isolatedRoot, "r025-editmode-results-passed.xml"),
    `${evidenceRoot}/tests/r025-editmode-results.xml`
  ),
  scrubReport: copyAbsolute(
    path.join(scrubRoot, "scrub-report.json"),
    `${evidenceRoot}/scrub/scrub-report.json`
  ),
  scrubResults: copyAbsolute(
    path.join(scrubRoot, "r025-scrub-results.xml"),
    `${evidenceRoot}/scrub/r025-scrub-results.xml`
  ),
  scrubReview: copyAbsolute(
    path.join(stagingAbsolute, "r025-scrub-full-size-review.json"),
    `${evidenceRoot}/r025-scrub-full-size-review.json`
  ),
  scrubFrames: [
    copyAbsolute(
      path.join(scrubRoot, "frames/frame-0000.png"),
      `${evidenceRoot}/scrub/frame-070.png`
    ),
    copyAbsolute(
      path.join(scrubRoot, "frames/frame-0012.png"),
      `${evidenceRoot}/scrub/frame-090.png`
    ),
    copyAbsolute(
      path.join(scrubRoot, "frames/frame-0026.png"),
      `${evidenceRoot}/scrub/frame-1133.png`
    )
  ],
  proofLog: copyAbsolute(
    path.join(isolatedRoot, "r025-full-proof.log"),
    `${evidenceRoot}/r025-full-proof.log`
  ),
  proofReport: copyAbsolute(
    path.join(proofRoot, "unity-capture-report.json"),
    `${evidenceRoot}/full-proof/unity-capture-report.json`
  ),
  normalProof: copyAbsolute(
    path.join(proofRoot, "normal/normal-speed-proof.mp4"),
    `${evidenceRoot}/full-proof/normal/normal-speed-proof.mp4`
  ),
  normalContact: copyAbsolute(
    path.join(proofRoot, "normal/seven-pose-contact-sheet.png"),
    `${evidenceRoot}/full-proof/normal/seven-pose-contact-sheet.png`
  ),
  slowProof: copyAbsolute(
    path.join(proofRoot, "tear-quarter-speed/tear-quarter-speed-closeup.mp4"),
    `${evidenceRoot}/full-proof/tear-quarter-speed/tear-quarter-speed-closeup.mp4`
  ),
  proofReview: copyAbsolute(
    path.join(stagingAbsolute, "r025-full-proof-full-size-review.json"),
    `${evidenceRoot}/r025-full-proof-full-size-review.json`
  )
};

const evidenceManifest = writeJson(`${evidenceRoot}/r025-evidence-manifest.json`, {
  schema: "premium-display-case-gate04-r025-portrait-projection-evidence.v1",
  candidateScope:
    "R025 isolated target-aspect diagnostic repair with immutable R024 physical inputs",
  r024FbxSha256: r024RigHash,
  targetAspect: {
    width: 1206,
    height: 2622,
    value: 1206 / 2622,
    cameraAspectBeforeSession:
      preflight.accounting.targetPortraitProjection.cameraAspectBeforeSession,
    maximumExactIdBoundsDelta:
      preflight.accounting.targetPortraitProjection.maximumExactIdBoundsDelta
  },
  targetCounts: {
    at070: [
      preflight.formedMouthMaterials.visibleInnerLinerPixels,
      preflight.formedMouthMaterials.visibleCavityPixels
    ],
    at090: [
      preflight.containedMouthMaterials.visibleInnerLinerPixels,
      preflight.containedMouthMaterials.visibleCavityPixels
    ],
    fullCaseContrast: preflight.caseLegibility.fullTargetMaskContrast,
    threshold: 0.04
  },
  staticPreflight: {
    report: copied.staticReport,
    results: copied.staticResults,
    review: copied.staticReview,
    frames: copied.staticFrames,
    segmentLabels: copied.segmentLabels
  },
  tests: {
    structural: copied.structuralResults,
    editMode: copied.editModeResults
  },
  scrub: {
    report: copied.scrubReport,
    results: copied.scrubResults,
    review: copied.scrubReview,
    frames: copied.scrubFrames
  },
  fullProof: {
    report: copied.proofReport,
    normalSpeed: copied.normalProof,
    normalContactSheet: copied.normalContact,
    quarterSpeedCloseup: copied.slowProof,
    review: copied.proofReview
  },
  source: {
    inputs: copied.inputs,
    forensicDiagnosis: copied.forensicDiagnosis,
    hostPreflight: copied.hostPreflight,
    isolatedSourceManifest: copied.sourceManifest,
    templateSources: copied.sourceTemplate
  },
  reviewArtifacts: [
    copied.normalProof.path,
    copied.normalContact.path
  ],
  technicalOnlyArtifacts: [
    copied.slowProof.path,
    copied.staticReport.path,
    copied.scrubReport.path
  ],
  gate05Through12: "stale",
  shippingReady: false,
  physicalPhoneInstalled: false,
  statusText: "视觉批准待确认，未推送手机"
});
const evidenceReconciliation = writeJson(
  `${evidenceRoot}/r025-evidence-manifest-reconciliation.json`,
  {
    schema: "premium-display-case-gate04-r025-evidence-reconciliation.v1",
    reason:
      "The first immutable evidence manifest was emitted before registration resumed; this record adds the forensic diagnosis without replacing prior evidence.",
    primaryManifest: evidenceManifest,
    forensicDiagnosis: copied.forensicDiagnosis,
    reviewArtifacts: [
      copied.normalProof.path,
      copied.normalContact.path
    ],
    shippingReady: false,
    physicalPhoneInstalled: false,
    statusText: "视觉批准待确认，未推送手机"
  }
);

const records = [
  artifact(manifest, "premium-display-case-gate04-r025-bootstrap", copied.bootstrap, "architecture-r025-staging-bootstrap", "process", "Creates a new R025 staging source without changing R024."),
  artifact(manifest, "premium-display-case-gate04-r025-preparation", copied.prepare, "architecture-isolated-preparation", "process", "Creates the isolated R025 Unity project after host checks."),
  artifact(manifest, "premium-display-case-gate04-r025-inputs", copied.inputs, "architecture-r025-input-boundary", "validation", "Locks R024 FBX hash and rejected-history boundary."),
  artifact(manifest, "premium-display-case-gate04-r025-forensic-diagnosis", copied.forensicDiagnosis, "architecture-r025-projection-forensics", "validation", "Preserves the R024 4:3-to-portrait diagnostic root cause."),
  artifact(manifest, "premium-display-case-gate04-r025-source-manifest", copied.sourceManifest, "architecture-r025-source-boundary", "validation", "Records R025 source hashes and unchanged physical boundaries."),
  artifact(manifest, "premium-display-case-gate04-r025-host-preflight", copied.hostPreflight, "architecture-host-preflight", "validation", "Records no Unity conflict and disk reserve before R025 capture."),
  artifact(manifest, "premium-display-case-gate04-r025-static-report", copied.staticReport, "architecture-target-portrait-preflight", "validation", "Target-aspect calibration, exact ID bounds, segment masks, and static measurement report."),
  artifact(manifest, "premium-display-case-gate04-r025-static-results", copied.staticResults, "architecture-target-portrait-results", "validation", "R025 static preflight: 23/23 pass."),
  artifact(manifest, "premium-display-case-gate04-r025-static-review", copied.staticReview, "architecture-full-size-static-review", "validation", "Native-size static review passes for the scrub gate."),
  artifact(manifest, "premium-display-case-gate04-r025-structural-checks", copied.structuralResults, "architecture-structural-checks", "validation", "Isolated structural checks: 7/7 pass."),
  artifact(manifest, "premium-display-case-gate04-r025-editmode-tests", copied.editModeResults, "architecture-editmode-tests", "validation", "R025 filtered EditMode tests: 17/17 pass."),
  artifact(manifest, "premium-display-case-gate04-r025-scrub-report", copied.scrubReport, "architecture-continuity-scrub", "validation", "31 actual Unity frames from .70 through 1.20 seconds."),
  artifact(manifest, "premium-display-case-gate04-r025-scrub-results", copied.scrubResults, "architecture-continuity-scrub-results", "validation", "R025 continuity scrub: 11/11 pass."),
  artifact(manifest, "premium-display-case-gate04-r025-scrub-review", copied.scrubReview, "architecture-full-size-scrub-review", "validation", "Native-size .70/.90/1.133 review passes."),
  artifact(manifest, "premium-display-case-gate04-r025-full-proof-report", copied.proofReport, "architecture-unity-proof-report", "validation", "96-frame 1.60-second Unity proof with zero effects."),
  artifact(manifest, "premium-display-case-gate04-r025-normal-proof", copied.normalProof, "architecture-normal-speed-review", "validation", "Normal-speed full-size actual Unity proof."),
  artifact(manifest, "premium-display-case-gate04-r025-quarter-proof", copied.slowProof, "architecture-quarter-speed-technical", "validation", "Quarter-speed closeup from actual Unity frames; technical-only."),
  artifact(manifest, "premium-display-case-gate04-r025-full-proof-review", copied.proofReview, "architecture-full-size-proof-review", "validation", "Full-size proof review remains pending user approval."),
  artifact(manifest, "premium-display-case-gate04-r025-evidence-manifest", evidenceManifest, "architecture-evidence-manifest", "validation", "Maps immutable R025 evidence and review artifacts."),
  artifact(manifest, "premium-display-case-gate04-r025-evidence-reconciliation", evidenceReconciliation, "architecture-evidence-reconciliation", "validation", "Adds late forensic linkage without replacing immutable evidence.")
];
const existingIds = new Set(manifest.assets.map((asset) => asset.id));
for (const record of records) {
  if (existingIds.has(record.id)) {
    throw new Error(`R025 asset ID already exists: ${record.id}`);
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
    supersededBy: "gate04-r025-portrait-projection-candidate",
    supersededAt: now
  }
];
stage.revision += 1;
stage.status = "ready_for_review";
stage.reviewArtifactIds = [
  "premium-display-case-gate04-r025-normal-proof"
];
stage.validations = [
  {
    id: "r015-r024-rejected-history-preserved",
    status: "pass",
    evidence: copied.inputs.path
  },
  {
    id: "r024-fbx-hash-unchanged",
    status: "pass",
    evidence: r024RigHash
  },
  {
    id: "r025-target-portrait-preflight",
    status: "pass",
    evidence: `${copied.staticResults.path}; aspect=${preflight.accounting.targetPortraitProjection.cameraAspect}; delta=${preflight.accounting.targetPortraitProjection.maximumExactIdBoundsDelta}`
  },
  {
    id: "r025-static-full-size-review",
    status: "pass",
    evidence: copied.staticReview.path
  },
  {
    id: "r025-isolated-tests",
    status: "pass",
    evidence: `${copied.structuralResults.path}; 7/7. ${copied.editModeResults.path}; 17/17.`
  },
  {
    id: "r025-continuity-scrub",
    status: "pass",
    evidence: `${copied.scrubResults.path}; 11/11.`
  },
  {
    id: "r025-full-proof",
    status: "pass",
    evidence: `${copied.proofReview.path}; 96 normal frames and 173 quarter-speed frames.`
  }
];
stage.decision = {
  action: "request-user-visual-approval",
  notes:
    "R025 passed isolated target-aspect static diagnostics, tests, scrub, and full proof without changing any R024 physical input. It is a Gate 04 candidate only.",
  decidedAt: now,
  decidedBy: "agent-emitted-r025-isolated-candidate",
  approvalRequestAllowed: true,
  finalAuthority: "latest-explicit-chat-instruction"
};
stage.evidenceReview = {
  architectureRevision: 8,
  evidenceRevision: 25,
  iteration: "r025-portrait-projection-diagnostic-repair",
  disposition: "candidate-awaiting-user-visual-approval",
  primaryArtifact: copied.normalProof.path,
  beforeAfterScreenEvidence: [
    copied.staticFrames[1].path,
    copied.staticFrames[2].path,
    copied.scrubFrames[1].path,
    copied.scrubFrames[2].path
  ],
  reviewArtifactIds: stage.reviewArtifactIds,
  technicalArtifactIds: [
    "premium-display-case-gate04-r025-quarter-proof"
  ],
  shownToUserForApproval: false,
  visualApproval: "pending-user-visual-approval",
  statusText: "视觉批准待确认，未推送手机"
};
const staleReason =
  "Gate 04 R025 is an isolated candidate awaiting explicit visual approval; no downstream gate may advance.";
for (const downstream of manifest.stages.slice(4)) {
  downstream.status = "stale";
  downstream.staleReason = staleReason;
}
manifest.model.status =
  "gate04-r025-isolated-candidate-awaiting-visual-approval";
manifest.currentState = {
  ...manifest.currentState,
  activeStageId: "04-architecture",
  activeStageStatus: "ready_for_review",
  activeIteration: "r025-portrait-projection-diagnostic-repair",
  visualApproval: "gate04-r025-candidate-pending-user-visual-approval",
  diagnosis:
    "R024's static failure used 4:3 projection calculations for a 1206x2622 target. R025 binds target aspect before measurements and uses segment-aware target-space masks.",
  architectureApproval: {
    stageId: "04-architecture",
    architectureRevision: 8,
    evidenceRevision: 25,
    evidenceIteration: "r025-portrait-projection-diagnostic-repair",
    userApprovalQuote: null,
    decisionState: "candidate-pending-user-visual-approval",
    approvalRequestAllowed: true,
    gate05Status: "stale"
  },
  motionCorrection: {
    ...manifest.currentState.motionCorrection,
    gate04Status: "r025-isolated-candidate-pending-user-visual-approval",
    currentArchitectureRevision: 8,
    currentEvidenceRevision: 25,
    currentEvidenceIteration: "r025-portrait-projection-diagnostic-repair",
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
    "R025 is an isolated Gate 04 target-aspect diagnostic candidate. Tests, scrub, and proof pass; explicit visual approval is pending.",
  statusText: "视觉批准待确认，未推送手机"
};
manifest.revision += 1;
manifest.updatedAt = now;
refreshStageDigest(manifest, stage);

amendDocs(manifest.revision, stage.revision, copied);
const event = {
  id: crypto.randomUUID(),
  type: "gate04-r025-portrait-projection-candidate-ready-for-review",
  modelId: "premium-display-case",
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "04-architecture",
  stageRevision: stage.revision,
  architectureRevision: 8,
  evidenceRevision: 25,
  evidenceIteration: "r025-portrait-projection-diagnostic-repair",
  sourceTask: "cursor-task:premium-display-case-gate04-r025-20260901",
  r024FbxSha256: r024RigHash,
  targetAspect: preflight.accounting.targetPortraitProjection.cameraAspect,
  targetBoundsDelta:
    preflight.accounting.targetPortraitProjection.maximumExactIdBoundsDelta,
  staticCounts: {
    at070: [
      preflight.formedMouthMaterials.visibleInnerLinerPixels,
      preflight.formedMouthMaterials.visibleCavityPixels
    ],
    at090: [
      preflight.containedMouthMaterials.visibleInnerLinerPixels,
      preflight.containedMouthMaterials.visibleCavityPixels
    ],
    fullCaseContrast: preflight.caseLegibility.fullTargetMaskContrast
  },
  staticPreflight: "23/23",
  isolatedStructuralChecks: "7/7",
  editModeTests: "17/17",
  scrub: "11/11",
  normalProofFrames: 96,
  quarterSpeedFrames: 173,
  approvalRequestAllowed: true,
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
  reviewArtifacts: stage.reviewArtifactIds,
  shippingReady: false
}, null, 2));
