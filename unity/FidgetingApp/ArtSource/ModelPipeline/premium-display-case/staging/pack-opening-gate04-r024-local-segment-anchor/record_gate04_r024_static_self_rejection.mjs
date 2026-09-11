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
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r024-local-segment-anchor";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-024";
const isolatedRoot =
  "/tmp/FidgetingApp-PackOpening-R024-LocalSegmentAnchors-20260901-r01";
const expectedPipelineRevision = 99;
const expectedStageRevision = 31;
const now = new Date().toISOString();

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

function walk(directory) {
  return fs.readdirSync(directory, { withFileTypes: true })
    .sort((left, right) => left.name.localeCompare(right.name))
    .flatMap((entry) => {
      const file = path.join(directory, entry.name);
      return entry.isDirectory() ? walk(file) : [file];
    });
}

function copyAbsolute(source, destinationRelative) {
  requireFile(source);
  const destination = resolveRepoPath(destinationRelative);
  if (fs.existsSync(destination)) {
    throw new Error(`Refusing to overwrite immutable evidence: ${destinationRelative}`);
  }
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(source, destination, fs.constants.COPYFILE_EXCL);
  return {
    path: destinationRelative,
    sha256: sha256File(destination),
    sizeBytes: fs.statSync(destination).size
  };
}

function copyTree(sourceRoot, destinationRoot) {
  requireDirectory(sourceRoot);
  return walk(sourceRoot).map((source) => copyAbsolute(
    source,
    `${destinationRoot}/${path.relative(sourceRoot, source)}`
  ));
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
      name: "Gate 04 R024 local segment anchor repair",
      version: "r024-static-preflight-self-rejected",
      recipe:
        "Per-segment collapse anchors; actual Blender topology probe; isolated Unity 6000.5.6f1 URP 17.5 static preflight"
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
const evidenceAbsolute = absolute(evidenceRoot);
const templateRoot = path.join(
  stagingAbsolute,
  "isolated-template/Assets/IsolatedProofR024"
);
const preflightRoot = path.join(isolatedRoot, "Captures/r024-preflight");
const paths = {
  builder: path.join(stagingAbsolute, "build_pack_only_rig.py"),
  probe: path.join(stagingAbsolute, "probe_r024_blender_geometry.py"),
  previewMapper: path.join(
    stagingAbsolute,
    "apply_r024_preview_material_vertical_flip.py"
  ),
  prepare: path.join(stagingAbsolute, "prepare_r024_isolated.mjs"),
  recorder: path.join(
    stagingAbsolute,
    "record_gate04_r024_static_self_rejection.mjs"
  ),
  sourceRigReport: path.join(stagingAbsolute, "r024-source-rig-report.json"),
  sourceTopology: path.join(
    stagingAbsolute,
    "r024-source-topology-preflight.json"
  ),
  previewProof: path.join(
    stagingAbsolute,
    "r024-blender-preview-mapping-proof.json"
  ),
  rigBlend: path.join(
    stagingAbsolute,
    "PackOpeningGate04R024PackOnlyRig.blend"
  ),
  rigFbx: path.join(
    stagingAbsolute,
    "PackOpeningGate04R024PackOnlyRig.fbx"
  ),
  previewBlend: path.join(
    stagingAbsolute,
    "PackOpeningGate04R024PreviewOnlyMapping.blend"
  ),
  previewFbx: path.join(
    stagingAbsolute,
    "PackOpeningGate04R024PreviewOnlyMapping.fbx"
  ),
  rawBlenderFrames: path.join(stagingAbsolute, "blender-source"),
  mappedBlenderFrames: path.join(stagingAbsolute, "blender-preview-mapped"),
  hostPreflight: path.join(
    stagingAbsolute,
    "r024-unity-preflight-environment.json"
  ),
  sourceManifest: path.join(isolatedRoot, "r024-source-manifest.json"),
  preflightLog: path.join(isolatedRoot, "r024-preflight.log"),
  preflightReport: path.join(preflightRoot, "r024-preflight-report.json"),
  preflightResults: path.join(preflightRoot, "r024-preflight-results.xml"),
  sealedFrame: path.join(preflightRoot, "sealed-state.png"),
  tear050Frame: path.join(preflightRoot, "tear-front-050.png"),
  formed070Frame: path.join(preflightRoot, "formed-mouth-070.png"),
  contained090Frame: path.join(preflightRoot, "case-contained-090.png"),
  primaryStaticSheet: path.join(preflightRoot, "primary-static-sheet.png"),
  diagnostics: path.join(preflightRoot, "diagnostics"),
  orientation: path.join(preflightRoot, "orientation-calibration"),
  r023Rejection: absolute(
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-023/r023-static-preflight-self-rejection.json"
  )
};

for (const file of [
  paths.builder,
  paths.probe,
  paths.previewMapper,
  paths.prepare,
  paths.recorder,
  paths.sourceRigReport,
  paths.sourceTopology,
  paths.previewProof,
  paths.rigBlend,
  paths.rigFbx,
  paths.previewBlend,
  paths.previewFbx,
  paths.hostPreflight,
  paths.sourceManifest,
  paths.preflightLog,
  paths.preflightReport,
  paths.preflightResults,
  paths.sealedFrame,
  paths.tear050Frame,
  paths.formed070Frame,
  paths.contained090Frame,
  paths.primaryStaticSheet,
  paths.r023Rejection
]) requireFile(file);
for (const directory of [
  templateRoot,
  paths.rawBlenderFrames,
  paths.mappedBlenderFrames,
  paths.diagnostics,
  paths.orientation
]) requireDirectory(directory);

const sourceTopology = JSON.parse(
  fs.readFileSync(paths.sourceTopology, "utf8")
);
const sourceRig = JSON.parse(fs.readFileSync(paths.sourceRigReport, "utf8"));
const previewProof = JSON.parse(fs.readFileSync(paths.previewProof, "utf8"));
const sourceManifest = JSON.parse(
  fs.readFileSync(paths.sourceManifest, "utf8")
);
const hostPreflight = JSON.parse(
  fs.readFileSync(paths.hostPreflight, "utf8")
);
const preflight = JSON.parse(
  fs.readFileSync(paths.preflightReport, "utf8")
);
const orientation = JSON.parse(fs.readFileSync(
  path.join(paths.orientation, "r024-orientation-calibration.json"),
  "utf8"
));
const failedChecks = preflight.checks?.filter((check) => !check.passed) || [];
const failedIds = failedChecks.map((check) => check.id);
const expectedFailures = [
  "tear-front-opens-from-screen-right",
  "top-seal-covers-only-sealed-segments",
  "component-segments-avoid-opened-mouth-spans",
  "component-masks-stay-inside-pack-without-full-width-bridges",
  "formed-mouth-liner-and-cavity-separate",
  "contained-mouth-liner-and-cavity-separate",
  "contained-case-has-readable-contrast-and-bounds"
];

if (
  !sourceTopology.passed
  || !sourceTopology.checks?.authoredCollapsedSegmentsUseLocalAnchorsAndZeroArea
  || !sourceTopology.checks?.staticBlendsRetainLocalCollapsedSegments
  || !sourceTopology.checks?.staticBlendsStayInsidePackAndOneSegmentWide
  || !sourceTopology.checks?.openedSegmentsProgressFromUnityScreenRight
) {
  throw new Error("R024 source topology preflight does not prove local anchors.");
}
if (
  sourceRig.segmentTopology?.independentSegmentCount !== 48
  || sourceRig.segmentTopology?.collapsedSegments?.globalTearFrontAnchor
  || sourceRig.foldedLinerMaximumDepthMeters !== 0.0055
  || sourceRig.mouthDepthMeters !== 0.107
) {
  throw new Error("R024 source rig does not preserve the locked mouth contract.");
}
if (
  !previewProof.exportInvariants?.exportedFbxByteIdenticalToR024
  || !previewProof.exportInvariants?.uvStreamUnchanged
  || !previewProof.exportInvariants?.geometryStreamUnchanged
  || previewProof.exportInvariants?.unityMaterialMappingChanged
) {
  throw new Error("R024 preview mapping does not preserve the Unity FBX.");
}
if (
  !sourceManifest.isolatedUnityCandidate
  || sourceManifest.canonicalIntegration
  || !sourceManifest.sourceBoundary?.r022ArtUvAndTimingUnchanged
  || sourceManifest.sourceBoundary?.casePrefabChanged
  || sourceManifest.sourceBoundary?.contentSlotChanged
  || sourceManifest.sourceBoundary?.shippingAssetsChanged
) {
  throw new Error("R024 source boundary is not isolated.");
}
if (
  !hostPreflight.passed
  || hostPreflight.processes?.unityConflict
  || !hostPreflight.disk?.reserveSatisfied
  || !orientation.passed
  || orientation.r024?.winner !== "Identity"
  || orientation.r017Control?.winner !== "HorizontalFlip"
) {
  throw new Error("R024 host or orientation preflight does not pass.");
}
if (
  preflight.passed
  || preflight.width !== 1206
  || preflight.height !== 2622
  || preflight.visualEffectsIntensity !== 0
  || failedChecks.length !== expectedFailures.length
  || !expectedFailures.every((id) => failedIds.includes(id))
) {
  throw new Error("R024 static preflight does not match the required stop state.");
}

const preservedRejections = [
  ["R015", "rev-015/self-rejection.json"],
  ["R016", "rev-016/self-rejection.json"],
  ["R017", "rev-017/r017-scrub-visual-self-rejection.json"],
  ["R018", "rev-018/r018-preflight-self-rejection.json"],
  ["R019", "rev-019/r019-preflight-self-rejection.json"],
  ["R021", "rev-021/r021-preflight-self-rejection.json"],
  ["R022", "rev-022/r022-preflight-self-rejection.json"],
  ["R023", "rev-023/r023-static-preflight-self-rejection.json"]
].map(([revision, relative]) => {
  const source = absolute(
    `unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/${relative}`
  );
  requireFile(source);
  return {
    revision,
    path: path.relative(repoRoot, source),
    sha256: sha256File(source)
  };
});

const manifest = loadManifest("premium-display-case");
if (manifest.revision !== expectedPipelineRevision) {
  throw new Error(
    `Expected pipeline revision ${expectedPipelineRevision}; found ${manifest.revision}.`
  );
}
const stage = manifest.stages.find((item) => item.id === "04-architecture");
if (!stage || stage.revision !== expectedStageRevision || stage.status !== "draft") {
  throw new Error("Gate 04 is not at the expected R023 self-rejected state.");
}
if (fs.existsSync(evidenceAbsolute)) {
  throw new Error(`Refusing to overwrite immutable evidence: ${evidenceRoot}`);
}
fs.mkdirSync(evidenceAbsolute, { recursive: false });

const copied = {
  builder: copyAbsolute(paths.builder, `${evidenceRoot}/source/build_pack_only_rig.py`),
  probe: copyAbsolute(
    paths.probe,
    `${evidenceRoot}/source/probe_r024_blender_geometry.py`
  ),
  previewMapper: copyAbsolute(
    paths.previewMapper,
    `${evidenceRoot}/source/apply_r024_preview_material_vertical_flip.py`
  ),
  prepare: copyAbsolute(
    paths.prepare,
    `${evidenceRoot}/source/prepare_r024_isolated.mjs`
  ),
  recorder: copyAbsolute(
    paths.recorder,
    `${evidenceRoot}/source/record_gate04_r024_static_self_rejection.mjs`
  ),
  sourceRigReport: copyAbsolute(
    paths.sourceRigReport,
    `${evidenceRoot}/r024-source-rig-report.json`
  ),
  sourceTopology: copyAbsolute(
    paths.sourceTopology,
    `${evidenceRoot}/r024-source-topology-preflight.json`
  ),
  previewProof: copyAbsolute(
    paths.previewProof,
    `${evidenceRoot}/r024-blender-preview-mapping-proof.json`
  ),
  rigBlend: copyAbsolute(
    paths.rigBlend,
    `${evidenceRoot}/source/PackOpeningGate04R024PackOnlyRig.blend`
  ),
  rigFbx: copyAbsolute(
    paths.rigFbx,
    `${evidenceRoot}/source/PackOpeningGate04R024PackOnlyRig.fbx`
  ),
  previewBlend: copyAbsolute(
    paths.previewBlend,
    `${evidenceRoot}/source/PackOpeningGate04R024PreviewOnlyMapping.blend`
  ),
  previewFbx: copyAbsolute(
    paths.previewFbx,
    `${evidenceRoot}/source/PackOpeningGate04R024PreviewOnlyMapping.fbx`
  ),
  hostPreflight: copyAbsolute(
    paths.hostPreflight,
    `${evidenceRoot}/preflight/r024-host-preflight.json`
  ),
  sourceManifest: copyAbsolute(
    paths.sourceManifest,
    `${evidenceRoot}/r024-source-manifest.json`
  ),
  preflightLog: copyAbsolute(
    paths.preflightLog,
    `${evidenceRoot}/r024-preflight.log`
  ),
  preflightReport: copyAbsolute(
    paths.preflightReport,
    `${evidenceRoot}/preflight/r024-preflight-report.json`
  ),
  preflightResults: copyAbsolute(
    paths.preflightResults,
    `${evidenceRoot}/preflight/r024-preflight-results.xml`
  ),
  sealedFrame: copyAbsolute(
    paths.sealedFrame,
    `${evidenceRoot}/preflight/sealed-state.png`
  ),
  tear050Frame: copyAbsolute(
    paths.tear050Frame,
    `${evidenceRoot}/preflight/tear-front-050.png`
  ),
  formed070Frame: copyAbsolute(
    paths.formed070Frame,
    `${evidenceRoot}/preflight/formed-mouth-070.png`
  ),
  contained090Frame: copyAbsolute(
    paths.contained090Frame,
    `${evidenceRoot}/preflight/case-contained-090.png`
  ),
  primaryStaticSheet: copyAbsolute(
    paths.primaryStaticSheet,
    `${evidenceRoot}/preflight/primary-static-sheet.png`
  )
};
copied.templateSources = copyTree(
  templateRoot,
  `${evidenceRoot}/source/isolated-template/Assets/IsolatedProofR024`
);
copied.rawBlenderFrames = copyTree(
  paths.rawBlenderFrames,
  `${evidenceRoot}/blender/raw-source`
);
copied.mappedBlenderFrames = copyTree(
  paths.mappedBlenderFrames,
  `${evidenceRoot}/blender/preview-mapped`
);
copied.diagnosticFrames = copyTree(
  paths.diagnostics,
  `${evidenceRoot}/preflight/diagnostics`
);
copied.orientationFrames = copyTree(
  paths.orientation,
  `${evidenceRoot}/preflight/orientation-calibration`
);

const evidenceManifest = writeJson(
  `${evidenceRoot}/r024-evidence-manifest.json`,
  {
    schema: "premium-display-case-gate04-r024-static-preflight-evidence.v1",
    candidateScope:
      "R024 per-segment local collapse anchors for the isolated 48-segment Pack mouth",
    unityTarget: {
      project: isolatedRoot,
      version: "6000.5.6f1",
      urp: "17.5.0",
      resolution: [1206, 2622],
      effectsIntensity: 0
    },
    hostPreflight: copied.hostPreflight,
    sourceTopology: copied.sourceTopology,
    sourceRig: copied.sourceRigReport,
    previewMapping: copied.previewProof,
    isolatedSourceManifest: copied.sourceManifest,
    staticPreflight: {
      report: copied.preflightReport,
      results: copied.preflightResults,
      primarySheet: copied.primaryStaticSheet,
      beautyFrames: [
        copied.sealedFrame,
        copied.tear050Frame,
        copied.formed070Frame,
        copied.contained090Frame
      ],
      diagnosticFrames: copied.diagnosticFrames,
      orientationFrames: copied.orientationFrames
    },
    preservedRejections,
    shippingReady: false,
    physicalPhoneInstalled: false
  }
);

const componentAt070 = preflight.componentSegments.states
  .find((state) => Math.abs(state.timeSeconds - 0.7) < 0.001);
const componentAt090 = preflight.componentSegments.states
  .find((state) => Math.abs(state.timeSeconds - 0.9) < 0.001);
const selfRejection = writeJson(
  `${evidenceRoot}/r024-static-preflight-self-rejection.json`,
  {
    schema: "premium-display-case-gate04-r024-static-preflight-self-rejection.v1",
    outcome: "self-rejected",
    reviewedAt: now,
    candidateScope:
      "isolated R024 per-segment local collapse-anchor repair for the R022 segmented Pack-mouth rig",
    rootCauseVerified: {
      r022Defect:
        "R022 collapsed every segment to one pose-level tear-front anchor, so linear blend-shape interpolation stretched faces across the Pack.",
      r024Repair:
        "R024 anchors each collapsed segment at its own guide midpoint with stable behind-cavity Z and component-local Y.",
      sourceTopologyProof: copied.sourceTopology
    },
    sourceRepairOutcome: {
      passed: sourceTopology.passed,
      independentSegments: sourceRig.segmentTopology.independentSegmentCount,
      staticBlendSamples: [0.5, 0.7, 0.9],
      maximumFaceSpanMeters:
        sourceTopology.segmentTopology.maximumAllowedFaceXSpanMeters,
      globalTearFrontAnchor:
        sourceRig.segmentTopology.collapsedSegments.globalTearFrontAnchor
    },
    unityOrientation: {
      calibration: copied.orientationFrames.find(
        (item) => item.path.endsWith("r024-orientation-calibration.json")
      ),
      winner: orientation.r024.winner,
      identityMargin: orientation.r024.identityMargin,
      r017ControlWinner: orientation.r017Control.winner
    },
    staticTarget: {
      report: copied.preflightReport,
      results: copied.preflightResults,
      primaryStaticSheet: copied.primaryStaticSheet,
      effectsIntensity: preflight.visualEffectsIntensity,
      frameBarrier: {
        captures: preflight.frameBarrierCaptureCount,
        advanced: preflight.frameBarrierAdvancedCount
      }
    },
    failedConditions: [
      {
        id: "component-masks-remain-outside-pack-at-static-frames",
        evidence:
          `At t=0.700 top-seal=${componentAt070.topSealBounds.x.toFixed(4)}..${(componentAt070.topSealBounds.x + componentAt070.topSealBounds.width).toFixed(4)}, liner=${componentAt070.innerLinerBounds.x.toFixed(4)}..${(componentAt070.innerLinerBounds.x + componentAt070.innerLinerBounds.width).toFixed(4)}, cavity=${componentAt070.cavityBackBounds.x.toFixed(4)}..${(componentAt070.cavityBackBounds.x + componentAt070.cavityBackBounds.width).toFixed(4)}; Pack=${componentAt070.packBounds.x.toFixed(4)}..${(componentAt070.packBounds.x + componentAt070.packBounds.width).toFixed(4)}.`,
        frames: copied.diagnosticFrames.filter((item) =>
          item.path.endsWith("top-seal-segments-id-0.700.png")
          || item.path.endsWith("inner-liner-segments-id-0.700.png")
          || item.path.endsWith("cavity-back-segments-id-0.700.png")
        )
      },
      {
        id: "formed-mouth-lacks-required-deep-cavity",
        evidence:
          `At t=0.700 liner=${preflight.formedMouthMaterials.visibleInnerLinerPixels} below 384, cavity=${preflight.formedMouthMaterials.visibleCavityPixels} below 128, contiguous=${preflight.formedMouthMaterials.largestCavityClusterPixels} below 128.`,
        beautyFrame: copied.formed070Frame,
        diagnosticFrame: copied.diagnosticFrames.find((item) =>
          item.path.endsWith("mouth-material-id-0.700.png")
        )
      },
      {
        id: "contained-mouth-lacks-readable-liner",
        evidence:
          `At t=0.900 liner=${preflight.containedMouthMaterials.visibleInnerLinerPixels} below 384 while cavity=${preflight.containedMouthMaterials.visibleCavityPixels}; component masks remain outside Pack bounds.`,
        componentMask: componentAt090,
        beautyFrame: copied.contained090Frame,
        diagnosticFrame: copied.diagnosticFrames.find((item) =>
          item.path.endsWith("mouth-material-id-0.900.png")
        )
      },
      {
        id: "contained-case-is-not-legible-as-one-case-inside-mouth",
        evidence:
          `At t=0.900 boundary contrast=${preflight.caseLegibility.averageBoundaryContrast.toFixed(4)} below 0.0400.`,
        beautyFrame: copied.contained090Frame,
        diagnosticFrame: copied.diagnosticFrames.find((item) =>
          item.path.endsWith("case-visible-id-090.png")
        )
      }
    ],
    fullSizeBeautyInspection: {
      mode: "native-size 1206x2622 isolated Unity frames without resampling",
      verdict:
        "Rejected. The .70 frame reads as an upper rail over a flat Pack, not top foil Pack open → deep pouch. The .90 frame does not show a readable narrow liner or one contained live case behind the front lip."
    },
    passedBeforeStop: {
      sourceLocalAnchorTopology: "passed at .50/.70/.90",
      unityOrientationIdentity:
        `Identity margin=${orientation.r024.identityMargin.toFixed(6)}`,
      topCrimpAboveArchive: "passed",
      compactTopRightCurl: "passed",
      visualEffectsIntensity: preflight.visualEffectsIntensity,
      capturesFollowedFrameAdvance:
        `${preflight.frameBarrierCaptureCount}/${preflight.frameBarrierAdvancedCount}`
    },
    notRunAfterStaticFailure: [
      "isolated structural checks",
      "isolated EditMode tests",
      "canonical provenance validators",
      "Unity scrub",
      "normal-speed proof capture",
      "quarter-speed closeup capture",
      "Gate 04 candidate registration",
      "FDB update",
      "implementation-status update",
      "canonical project change",
      "build, install, or device work"
    ],
    hostProcess: {
      result:
        "Unity emitted the complete static report, then did not terminate after the preflight exception; only the isolated R024 batch process received SIGTERM.",
      affectsRenderedEvidence: false
    },
    preservedRejections,
    shippingReady: false,
    physicalPhoneInstalled: false,
    statusText: "视觉批准待确认，未推送手机"
  }
);

const records = [
  artifact(manifest, "premium-display-case-gate04-r024-rig-builder", copied.builder, "architecture-r024-source-builder", "process", "Builds the isolated R024 Pack-only FBX."),
  artifact(manifest, "premium-display-case-gate04-r024-topology-probe", copied.probe, "architecture-geometry-validator", "process", "Checks authored and blended local collapse anchors."),
  artifact(manifest, "premium-display-case-gate04-r024-source-topology", copied.sourceTopology, "architecture-segmented-mouth-validation", "validation", "Source preflight passes 48 local segments at .50/.70/.90."),
  artifact(manifest, "premium-display-case-gate04-r024-rig-report", copied.sourceRigReport, "architecture-pack-only-rig-report", "validation", "Records the R024 per-segment anchor contract."),
  artifact(manifest, "premium-display-case-gate04-r024-rig-fbx", copied.rigFbx, "architecture-pack-only-fbx", "process", "R024 Pack-only FBX used by the isolated Unity scene."),
  artifact(manifest, "premium-display-case-gate04-r024-preview-mapper", copied.previewMapper, "architecture-blender-preview-correction", "process", "Maps Blender previews only; it does not modify Unity UV streams."),
  artifact(manifest, "premium-display-case-gate04-r024-preview-proof", copied.previewProof, "architecture-preview-correction-proof", "validation", "Proves preview-only mapping left the R024 Unity FBX byte-identical."),
  artifact(manifest, "premium-display-case-gate04-r024-isolated-preparation", copied.prepare, "architecture-isolated-preparation", "process", "Creates the isolated R024 Unity project."),
  artifact(manifest, "premium-display-case-gate04-r024-source-manifest", copied.sourceManifest, "architecture-source-boundary", "validation", "Records the R024-only boundary and input hashes."),
  artifact(manifest, "premium-display-case-gate04-r024-host-preflight", copied.hostPreflight, "architecture-host-preflight", "validation", "Confirms no Unity conflict and a 4 GiB disk reserve before capture."),
  artifact(manifest, "premium-display-case-gate04-r024-preflight-log", copied.preflightLog, "architecture-unity-preflight-log", "validation", "Actual Unity 6000.5.6f1 URP 17.5 static preflight log."),
  artifact(manifest, "premium-display-case-gate04-r024-preflight-results", copied.preflightResults, "architecture-preflight-results", "validation", "Actual Unity static preflight emitted 21 checks with seven failures."),
  artifact(manifest, "premium-display-case-gate04-r024-preflight-report", copied.preflightReport, "architecture-preflight-report", "validation", "Full-resolution actual Unity static measurements."),
  artifact(manifest, "premium-display-case-gate04-r024-orientation", copied.orientationFrames.find((item) => item.path.endsWith("r024-orientation-calibration.json")), "architecture-orientation-calibration", "validation", "Actual Unity calibration selects Identity and preserves the R017 control."),
  artifact(manifest, "premium-display-case-gate04-r024-primary-sheet", copied.primaryStaticSheet, "architecture-primary-static-sheet", "validation", "Four actual Unity beauty frames with no diagnostic overlay."),
  artifact(manifest, "premium-display-case-gate04-r024-formed-frame", copied.formed070Frame, "architecture-before-after-frame", "validation", "Actual full-size .70 Unity formed-mouth frame."),
  artifact(manifest, "premium-display-case-gate04-r024-contained-frame", copied.contained090Frame, "architecture-before-after-frame", "validation", "Actual full-size .90 Unity contained-case frame."),
  artifact(manifest, "premium-display-case-gate04-r024-evidence-manifest", evidenceManifest, "architecture-evidence-manifest", "validation", "Lists raw, mapped, orientation, beauty, and diagnostic evidence."),
  artifact(manifest, "premium-display-case-gate04-r024-self-rejection", selfRejection, "architecture-full-size-review", "validation", "Seven static target failures stop R024 before tests or scrub.")
];
const existingIds = new Set(manifest.assets.map((asset) => asset.id));
for (const record of records) {
  if (existingIds.has(record.id)) {
    throw new Error(`Immutable R024 asset ID already exists: ${record.id}`);
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
    supersededBy: "gate04-r024-local-segment-anchor-static-preflight",
    supersededAt: now
  }
];
stage.revision += 1;
stage.status = "draft";
stage.reviewArtifactIds = [];
stage.validations = [
  {
    id: "r015-r023-rejection-evidence-preserved",
    status: "pass",
    evidence: preservedRejections.map(
      (item) => `${item.revision}:${item.sha256}`
    ).join(", ")
  },
  {
    id: "r024-local-anchor-source-topology",
    status: "pass",
    evidence: `${copied.sourceTopology.path}; local anchors, zero area, and bounded faces at .50/.70/.90.`
  },
  {
    id: "r024-preview-only-mapping",
    status: "pass",
    evidence: `${copied.previewProof.path}; R024 Unity FBX and UV stream remain unchanged.`
  },
  {
    id: "r024-isolated-unity-orientation",
    status: "pass",
    evidence: `${copied.orientationFrames.find((item) => item.path.endsWith("r024-orientation-calibration.json")).path}; Identity margin ${orientation.r024.identityMargin.toFixed(6)}.`
  },
  {
    id: "r024-actual-unity-static-preflight",
    status: "fail",
    evidence: `${copied.preflightResults.path}; 7/21 failures, including off-Pack component masks, .70 cavity=0, .90 liner=0, and case contrast ${preflight.caseLegibility.averageBoundaryContrast.toFixed(4)} below 0.0400.`
  },
  {
    id: "r024-stop-before-tests-and-scrub",
    status: "pass",
    evidence: "Static target failure stopped before isolated tests, validators, scrub, proof, docs, build, install, or device work."
  }
];
stage.decision = {
  action: "self-reject",
  notes:
    "R024 fixes the source collapse topology, but actual Unity static frames still render off-Pack component bridges and fail deep-cavity, liner, and contained-case legibility. Stop without tuning.",
  decidedAt: now,
  decidedBy: "agent-emitted-r024-static-preflight-review",
  approvalRequestAllowed: false,
  finalAuthority: "latest-explicit-chat-instruction",
  selfRejectionRecord: selfRejection.path
};
stage.evidenceReview = {
  architectureRevision: 8,
  evidenceRevision: 24,
  iteration: "r024-local-segment-anchor-static-preflight-self-rejection",
  disposition: "self-rejected",
  primaryArtifact: selfRejection.path,
  beforeAfterScreenEvidence: [
    copied.sourceTopology.path,
    copied.formed070Frame.path,
    copied.contained090Frame.path,
    copied.primaryStaticSheet.path
  ],
  shownToUserForApproval: false,
  visualApproval: "not-requested-preflight-gate-failed",
  statusText: "视觉批准待确认，未推送手机"
};
const staleReason =
  "Gate 04 R024 local-anchor static preflight self-rejected: actual Unity still renders off-Pack component bridges and fails cavity, liner, and contained-case legibility.";
for (const downstream of manifest.stages.slice(4)) {
  downstream.status = "stale";
  downstream.staleReason = staleReason;
}
manifest.model.status = "gate04-r024-static-preflight-self-rejected";
manifest.currentState = {
  ...manifest.currentState,
  activeStageId: "04-architecture",
  activeStageStatus: "draft",
  activeIteration: "r024-local-segment-anchor-static-preflight-self-rejection",
  visualApproval: "gate04-r024-self-rejected-preflight",
  diagnosis:
    "R024 removes R022's global source anchor, but actual Unity static diagnostics still render component masks outside Pack bounds. The .70 cavity and .90 liner/case legibility targets fail. No scrub ran.",
  architectureApproval: {
    stageId: "04-architecture",
    architectureRevision: 8,
    evidenceRevision: 24,
    evidenceIteration: "r024-local-segment-anchor-static-preflight-self-rejection",
    userApprovalQuote: null,
    decisionState: "self-rejected-preflight",
    approvalRequestAllowed: false,
    gate05Status: "stale"
  },
  motionCorrection: {
    ...manifest.currentState.motionCorrection,
    gate04Status: "r024-static-preflight-self-rejected",
    currentArchitectureRevision: 8,
    currentEvidenceRevision: 24,
    currentEvidenceIteration:
      "r024-local-segment-anchor-static-preflight-self-rejection",
    rejectedEvidenceRevisions: [
      ...(manifest.currentState.motionCorrection?.rejectedEvidenceRevisions || []),
      24
    ],
    selfRejectedIterations: [
      ...(manifest.currentState.motionCorrection?.selfRejectedIterations || []),
      "r024-local-segment-anchor-static-preflight"
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
    "Gate 04 R024 local anchor repair self-rejected after actual Unity static preflight. No tests, validators, scrub, proof, docs, build, install, or device work ran.",
  statusText: "视觉批准待确认，未推送手机"
};
manifest.revision += 1;
manifest.updatedAt = now;
refreshStageDigest(manifest, stage);
const event = {
  id: crypto.randomUUID(),
  type: "gate04-r024-local-segment-anchor-static-preflight-self-rejected",
  modelId: "premium-display-case",
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "04-architecture",
  stageRevision: stage.revision,
  architectureRevision: 8,
  evidenceRevision: 24,
  evidenceIteration: "r024-local-segment-anchor-static-preflight-self-rejection",
  sourceTask: "cursor-task:premium-display-case-gate04-r024-20260901",
  rootCause: "R022 pose-level global collapsed-segment anchor",
  sourceRepair: {
    passed: sourceTopology.passed,
    staticBlendPoints: [0.5, 0.7, 0.9],
    localAnchors: true
  },
  orientation: {
    winner: orientation.r024.winner,
    identityMargin: orientation.r024.identityMargin,
    r017ControlWinner: orientation.r017Control.winner
  },
  preflight: {
    checks: preflight.checks.length,
    failures: failedChecks.length,
    failedConditions: failedIds,
    formedCavityPixels: preflight.formedMouthMaterials.visibleCavityPixels,
    containedLinerPixels: preflight.containedMouthMaterials.visibleInnerLinerPixels,
    containedCaseContrast: preflight.caseLegibility.averageBoundaryContrast,
    results: copied.preflightResults.path
  },
  selfRejectionRecord: selfRejection.path,
  testsStarted: false,
  validatorsStarted: false,
  scrubStarted: false,
  fullProofStarted: false,
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
  staticPreflight: "self-rejected",
  failedChecks: failedIds,
  addedAssets: records.length
}, null, 2));
