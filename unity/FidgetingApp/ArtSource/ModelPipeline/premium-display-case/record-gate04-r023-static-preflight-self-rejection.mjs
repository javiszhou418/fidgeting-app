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
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r023-preview-mapping-validation";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-023";
const isolatedRoot =
  "/tmp/FidgetingApp-PackOpening-R023-PreviewMapping-20260901-r01";
const expectedPipelineRevision = 98;
const expectedStageRevision = 30;
const expectedR022FbxSha256 =
  "9b3ef4c2e5ca77cd0f53b5ff07c9e47bf2d9f0d367e037a5e711099d7b8ee89a";
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
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
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
      name: "Gate 04 R023 preview-only mapping validation",
      version: "r023-static-preflight-self-rejected",
      recipe:
        "R022 segmented Pack rig with Blender-only V preview mapping and isolated Unity 6000.5.6f1 URP 17.5 static preflight"
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
  "isolated-template/Assets/IsolatedProofR022"
);
const preflightRoot = path.join(isolatedRoot, "Captures/r022-preflight");
const paths = {
  previewMapper: path.join(
    stagingAbsolute,
    "apply_r023_preview_material_vertical_flip.py"
  ),
  prepare: path.join(
    stagingAbsolute,
    "prepare_r023_preview_mapping_isolated.mjs"
  ),
  blenderProbeBuilder: path.join(
    stagingAbsolute,
    "probe_r022_blender_geometry.py"
  ),
  blenderBuilder: path.join(stagingAbsolute, "build_pack_only_rig.py"),
  previewProof: path.join(
    stagingAbsolute,
    "r023-preview-mapping-proof.json"
  ),
  sourceRigProbe: path.join(
    stagingAbsolute,
    "r022-source-rig-geometry-probe.json"
  ),
  previewBlend: path.join(
    stagingAbsolute,
    "pack-opening-gate04-r023-preview-only.blend"
  ),
  r022Fbx: path.join(
    stagingAbsolute,
    "PackOpeningGate04R022PackOnlyRig.fbx"
  ),
  blenderSealed: path.join(
    stagingAbsolute,
    "blender-preflight/sealed-000.png"
  ),
  blenderTear050: path.join(
    stagingAbsolute,
    "blender-preflight/tear-050.png"
  ),
  blenderFormed070: path.join(
    stagingAbsolute,
    "blender-preflight/formed-mouth-070.png"
  ),
  blenderContained090: path.join(
    stagingAbsolute,
    "blender-preflight/case-contained-090.png"
  ),
  sourceManifest: path.join(isolatedRoot, "r023-source-manifest.json"),
  preflightLog: path.join(isolatedRoot, "r022-preflight.log"),
  preflightReport: path.join(preflightRoot, "r022-preflight-report.json"),
  preflightResults: path.join(preflightRoot, "r022-preflight-results.xml"),
  sealedFrame: path.join(preflightRoot, "sealed-state.png"),
  tear050Frame: path.join(preflightRoot, "tear-front-050.png"),
  formed070Frame: path.join(preflightRoot, "formed-mouth-070.png"),
  contained090Frame: path.join(preflightRoot, "case-contained-090.png"),
  primaryStaticSheet: path.join(preflightRoot, "primary-static-sheet.png"),
  diagnostics: path.join(preflightRoot, "diagnostics"),
  orientation: path.join(preflightRoot, "orientation-calibration"),
  r022Rejection: absolute(
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-022/r022-preflight-self-rejection.json"
  )
};

for (const file of [
  paths.previewMapper,
  paths.prepare,
  paths.blenderProbeBuilder,
  paths.blenderBuilder,
  paths.previewProof,
  paths.sourceRigProbe,
  paths.previewBlend,
  paths.r022Fbx,
  paths.blenderSealed,
  paths.blenderTear050,
  paths.blenderFormed070,
  paths.blenderContained090,
  paths.sourceManifest,
  paths.preflightLog,
  paths.preflightReport,
  paths.preflightResults,
  paths.sealedFrame,
  paths.tear050Frame,
  paths.formed070Frame,
  paths.contained090Frame,
  paths.primaryStaticSheet,
  paths.r022Rejection
]) requireFile(file);
requireDirectory(paths.diagnostics);
requireDirectory(paths.orientation);
requireDirectory(templateRoot);

const previewProof = JSON.parse(fs.readFileSync(paths.previewProof, "utf8"));
const sourceRigProbe = JSON.parse(fs.readFileSync(paths.sourceRigProbe, "utf8"));
const sourceManifest = JSON.parse(fs.readFileSync(paths.sourceManifest, "utf8"));
const preflight = JSON.parse(fs.readFileSync(paths.preflightReport, "utf8"));
const orientation = JSON.parse(fs.readFileSync(
  path.join(paths.orientation, "r022-orientation-calibration.json"),
  "utf8"
));
const failedChecks = preflight.checks?.filter((check) => !check.passed) || [];
const failedIds = failedChecks.map((check) => check.id);
if (
  previewProof.repairScope !== "Blender preview material mapping only"
  || previewProof.output?.r023UnityFbxSha256 !== expectedR022FbxSha256
  || !previewProof.exportInvariants?.exportedFbxByteIdenticalToR022
  || !previewProof.exportInvariants?.uvStreamUnchanged
  || !previewProof.exportInvariants?.geometryStreamUnchanged
  || previewProof.exportInvariants?.unityMaterialMappingChanged
  || previewProof.exportInvariants?.packGeometryChanged
) {
  throw new Error("R023 preview-only correction no longer preserves R022 export invariants.");
}
if (
  !sourceRigProbe.passed
  || sourceRigProbe.segmentTopology?.independentSegmentCount !== 48
  || sourceRigProbe.formedMouth?.linerMaximumDepthFromFrontLipMeters > 0.006
  || sourceRigProbe.formedMouth?.cavityMinimumDepthFromFrontLipMeters < 0.09
) {
  throw new Error("R022 source rig geometry evidence no longer passes.");
}
if (
  sourceManifest.r022Rig?.sha256 !== expectedR022FbxSha256
  || !sourceManifest.sourceBoundary?.blenderPreviewMappingOnly
  || !sourceManifest.sourceBoundary?.exportedFbxByteIdenticalToR022
  || sourceManifest.sourceBoundary?.unityMaterialMappingChanged
) {
  throw new Error("R023 isolated source boundary no longer preserves R022.");
}
if (
  !orientation.passed
  || orientation.r022?.winner !== "Identity"
  || orientation.r022?.identityMargin < orientation.minimumIdentityMargin
  || orientation.r017Control?.winner !== "HorizontalFlip"
) {
  throw new Error("R023 Unity orientation calibration no longer passes.");
}
if (
  preflight.passed
  || preflight.width !== 1206
  || preflight.height !== 2622
  || preflight.visualEffectsIntensity !== 0
  || preflight.source
    !== "actual isolated Unity 6000.5.6f1 URP 17.5 Play Mode frames"
  || failedChecks.length !== 6
  || ![
    "tear-front-opens-from-screen-right",
    "top-seal-covers-only-sealed-segments",
    "component-segments-avoid-opened-mouth-spans",
    "formed-mouth-liner-and-cavity-separate",
    "contained-mouth-liner-and-cavity-separate",
    "contained-case-has-readable-contrast-and-bounds"
  ].every((id) => failedIds.includes(id))
) {
  throw new Error("R023 static preflight does not match the required stop state.");
}

const preservedRejections = [
  ["R015", "rev-015/self-rejection.json"],
  ["R016", "rev-016/self-rejection.json"],
  ["R017", "rev-017/r017-scrub-visual-self-rejection.json"],
  ["R018", "rev-018/r018-preflight-self-rejection.json"],
  ["R019", "rev-019/r019-preflight-self-rejection.json"],
  ["R021", "rev-021/r021-preflight-self-rejection.json"],
  ["R022", "rev-022/r022-preflight-self-rejection.json"]
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
  throw new Error("Gate 04 is not at the expected R019 self-rejected state.");
}
if (fs.existsSync(evidenceAbsolute)) {
  throw new Error(`Refusing to overwrite immutable evidence: ${evidenceRoot}`);
}
fs.mkdirSync(evidenceAbsolute, { recursive: false });

const copied = {
  previewMapper: copyAbsolute(
    paths.previewMapper,
    `${evidenceRoot}/source/apply_r023_preview_material_vertical_flip.py`
  ),
  prepare: copyAbsolute(
    paths.prepare,
    `${evidenceRoot}/source/prepare_r023_preview_mapping_isolated.mjs`
  ),
  blenderProbeBuilder: copyAbsolute(
    paths.blenderProbeBuilder,
    `${evidenceRoot}/source/probe_r022_blender_geometry.py`
  ),
  blenderBuilder: copyAbsolute(
    paths.blenderBuilder,
    `${evidenceRoot}/source/build_pack_only_rig.py`
  ),
  previewProof: copyAbsolute(
    paths.previewProof,
    `${evidenceRoot}/r023-preview-mapping-proof.json`
  ),
  sourceRigProbe: copyAbsolute(
    paths.sourceRigProbe,
    `${evidenceRoot}/r022-source-rig-geometry-probe.json`
  ),
  previewBlend: copyAbsolute(
    paths.previewBlend,
    `${evidenceRoot}/source/pack-opening-gate04-r023-preview-only.blend`
  ),
  r022Fbx: copyAbsolute(
    paths.r022Fbx,
    `${evidenceRoot}/source/PackOpeningGate04R022PackOnlyRig.fbx`
  ),
  blenderSealed: copyAbsolute(
    paths.blenderSealed,
    `${evidenceRoot}/blender/sealed-000.png`
  ),
  blenderTear050: copyAbsolute(
    paths.blenderTear050,
    `${evidenceRoot}/blender/tear-050.png`
  ),
  blenderFormed070: copyAbsolute(
    paths.blenderFormed070,
    `${evidenceRoot}/blender/formed-mouth-070.png`
  ),
  blenderContained090: copyAbsolute(
    paths.blenderContained090,
    `${evidenceRoot}/blender/case-contained-090.png`
  ),
  sourceManifest: copyAbsolute(
    paths.sourceManifest,
    `${evidenceRoot}/r023-source-manifest.json`
  ),
  preflightLog: copyAbsolute(
    paths.preflightLog,
    `${evidenceRoot}/r023-preflight.log`
  ),
  preflightReport: copyAbsolute(
    paths.preflightReport,
    `${evidenceRoot}/preflight/r023-preflight-report.json`
  ),
  preflightResults: copyAbsolute(
    paths.preflightResults,
    `${evidenceRoot}/preflight/r023-preflight-results.xml`
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
  `${evidenceRoot}/source/isolated-template/Assets/IsolatedProofR022`
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
  `${evidenceRoot}/r023-evidence-manifest.json`,
  {
    schema: "premium-display-case-gate04-r023-static-preflight-evidence.v1",
    candidateScope:
      "R022 segmented physical Pack-mouth rig; R023 Blender preview material mapping only",
    unityTarget: {
      project: isolatedRoot,
      version: "6000.5.6f1",
      urp: "17.5.0",
      resolution: [1206, 2622],
      effectsIntensity: 0
    },
    previewCorrection: copied.previewProof,
    sourceRigProbe: copied.sourceRigProbe,
    exactR022Fbx: copied.r022Fbx,
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
    r020Boundary:
      "No immutable R020 rejection record exists in the evidence tree; its staging source remains untouched.",
    shippingReady: false,
    physicalPhoneInstalled: false
  }
);

const selfRejection = writeJson(
  `${evidenceRoot}/r023-static-preflight-self-rejection.json`,
  {
    schema: "premium-display-case-gate04-r023-static-preflight-self-rejection.v1",
    outcome: "self-rejected",
    reviewedAt: now,
    candidateScope:
      "isolated R022 segmented physical Pack-mouth rig with R023 Blender preview-only V mapping",
    correctionProof: {
      previewMapping: copied.previewProof,
      exportedFbxByteIdenticalToR022:
        previewProof.exportInvariants.exportedFbxByteIdenticalToR022,
      uvStreamUnchanged: previewProof.exportInvariants.uvStreamUnchanged,
      geometryStreamUnchanged:
        previewProof.exportInvariants.geometryStreamUnchanged,
      physicalUToSourceU: previewProof.exportInvariants.r022PhysicalUToSourceU
    },
    unityOrientation: {
      calibration: copied.orientationFrames.find(
        (item) => item.path.endsWith("r022-orientation-calibration.json")
      ),
      winner: orientation.r022.winner,
      identityMargin: orientation.r022.identityMargin,
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
        id: "top-seal-and-component-segment-diagnostics-stay-within-pack",
        evidence:
          "At t=0.700 the top-seal mask starts at x=0.0000 and component masks extend outside Pack bounds x=0.3127..0.6873.",
        frames: copied.diagnosticFrames.filter((item) =>
          item.path.endsWith("top-seal-segments-id-0.700.png")
          || item.path.endsWith("inner-liner-segments-id-0.700.png")
          || item.path.endsWith("cavity-back-segments-id-0.700.png")
        )
      },
      {
        id: "formed-mouth-shows-narrow-liner-and-contiguous-deep-cavity",
        evidence:
          "At t=0.700 the material capture has liner=173 below 384, cavity=0, and contiguous cavity=0 below 128.",
        beautyFrame: copied.formed070Frame,
        diagnosticFrame: copied.diagnosticFrames.find((item) =>
          item.path.endsWith("mouth-material-id-0.700.png")
        )
      },
      {
        id: "contained-mouth-shows-both-liner-and-cavity",
        evidence:
          "At t=0.900 the material capture has liner=0 below 384 despite cavity=480.",
        beautyFrame: copied.contained090Frame,
        diagnosticFrame: copied.diagnosticFrames.find((item) =>
          item.path.endsWith("mouth-material-id-0.900.png")
        )
      },
      {
        id: "case-reads-as-one-case-inside-upper-mouth",
        evidence:
          "At t=0.900 case boundary contrast is 0.0132 below 0.0400; the native-size beauty frame reads as a large rear frame, not a case held behind the front lip.",
        beautyFrame: copied.contained090Frame,
        diagnosticFrame: copied.diagnosticFrames.find((item) =>
          item.path.endsWith("case-visible-id-090.png")
        )
      }
    ],
    fullSizeBeautyInspection: {
      mode: "native-size 1206x2622 isolated Unity frames without resampling",
      verdict:
        "Rejected. The .70 frame lacks a narrow liner with a visible deep cavity. The .90 frame shows a broad rear case silhouette, not one legible unchanged case contained by the upper mouth."
    },
    passedBeforeStop: {
      unityOrientationIdentity:
        `Identity margin=${orientation.r022.identityMargin.toFixed(6)}`,
      topCrimpAboveArchive:
        "passed in the full-resolution Unity preflight",
      compactTopRightCurl:
        "passed in the full-resolution Unity preflight",
      caseIdContainment:
        `visibleWithPack=${preflight.caseContainment.visibleCasePixelsWithPackInUpperMouth}; frontOcclusion=${preflight.caseContainment.occludedCasePixelsByFront}; contiguous=${preflight.caseContainment.largestFrontOcclusionClusterPixels}`,
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
        "Unity emitted the complete static report, then did not terminate after the preflight exception; the isolated batch process received SIGTERM.",
      affectsRenderedEvidence: false
    },
    preservedRejections,
    shippingReady: false,
    physicalPhoneInstalled: false,
    statusText: "视觉批准待确认，未推送手机"
  }
);

const records = [
  artifact(manifest, "premium-display-case-gate04-r023-preview-mapper", copied.previewMapper, "architecture-blender-preview-correction", "process", "Applies a Blender-only V mapping; it does not export the FBX."),
  artifact(manifest, "premium-display-case-gate04-r023-isolated-preparation", copied.prepare, "architecture-isolated-preparation", "process", "Creates an R023 isolated Unity project from the recovered R021 base."),
  artifact(manifest, "premium-display-case-gate04-r023-r022-probe-builder", copied.blenderProbeBuilder, "architecture-geometry-validator", "process", "Probes the immutable R022 saved rig."),
  artifact(manifest, "premium-display-case-gate04-r023-r022-rig-builder", copied.blenderBuilder, "architecture-r022-source-builder", "process", "Preserves the source builder for the unchanged R022 rig."),
  artifact(manifest, "premium-display-case-gate04-r023-preview-mapping-proof", copied.previewProof, "architecture-preview-correction-proof", "validation", "Proves byte-identical FBX, unchanged UV stream, and unchanged geometry stream."),
  artifact(manifest, "premium-display-case-gate04-r023-r022-source-rig-probe", copied.sourceRigProbe, "architecture-segmented-mouth-validation", "validation", "Confirms 48 independent R022 mouth segments and the locked physical U mapping."),
  artifact(manifest, "premium-display-case-gate04-r023-preview-blend", copied.previewBlend, "architecture-blender-preview", "process", "R023 Blend contains the preview-only material mapping."),
  artifact(manifest, "premium-display-case-gate04-r023-r022-rig-fbx", copied.r022Fbx, "architecture-pack-only-fbx", "process", "Exact byte-identical R022 Pack-only FBX imported by the isolated Unity project."),
  artifact(manifest, "premium-display-case-gate04-r023-blender-sealed", copied.blenderSealed, "architecture-blender-preflight", "validation", "Blender-only sealed visual check."),
  artifact(manifest, "premium-display-case-gate04-r023-blender-formed-mouth", copied.blenderFormed070, "architecture-blender-preflight", "validation", "Blender-only .70 visual check."),
  artifact(manifest, "premium-display-case-gate04-r023-isolated-source-manifest", copied.sourceManifest, "architecture-source-boundary", "validation", "Records the isolated-only source boundary and exact R022 FBX."),
  artifact(manifest, "premium-display-case-gate04-r023-preflight-log", copied.preflightLog, "architecture-unity-preflight-log", "validation", "Unity 6000.5.6f1 URP 17.5 static preflight log."),
  artifact(manifest, "premium-display-case-gate04-r023-preflight-results", copied.preflightResults, "architecture-preflight-results", "validation", "Actual Unity static preflight emitted 20 checks with six failures."),
  artifact(manifest, "premium-display-case-gate04-r023-preflight-report", copied.preflightReport, "architecture-preflight-report", "validation", "Full-resolution actual Unity static preflight measurements."),
  artifact(manifest, "premium-display-case-gate04-r023-orientation-calibration", copied.orientationFrames.find((item) => item.path.endsWith("r022-orientation-calibration.json")), "architecture-orientation-calibration", "validation", "Actual Unity calibration selects Identity and preserves the R017 mirror control."),
  artifact(manifest, "premium-display-case-gate04-r023-primary-static-sheet", copied.primaryStaticSheet, "architecture-primary-static-sheet", "validation", "Four actual Unity beauty frames with no diagnostic overlay."),
  artifact(manifest, "premium-display-case-gate04-r023-formed-mouth-frame", copied.formed070Frame, "architecture-before-after-frame", "validation", "Actual full-size .70 Unity formed-mouth frame."),
  artifact(manifest, "premium-display-case-gate04-r023-contained-case-frame", copied.contained090Frame, "architecture-before-after-frame", "validation", "Actual full-size .90 Unity contained-case frame."),
  artifact(manifest, "premium-display-case-gate04-r023-evidence-manifest", evidenceManifest, "architecture-evidence-manifest", "validation", "Lists the primary, orientation, and diagnostic Unity frame evidence."),
  artifact(manifest, "premium-display-case-gate04-r023-self-rejection", selfRejection, "architecture-full-size-review", "validation", "Six static target failures stop R023 before tests or scrub.")
];
const existingIds = new Set(manifest.assets.map((asset) => asset.id));
for (const record of records) {
  if (existingIds.has(record.id)) {
    throw new Error(`Immutable R023 asset ID already exists: ${record.id}`);
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
    supersededBy: "gate04-r023-preview-mapping-static-preflight",
    supersededAt: now
  }
];
stage.revision += 1;
stage.status = "draft";
stage.reviewArtifactIds = [];
stage.validations = [
  {
    id: "r015-r022-rejection-evidence-preserved",
    status: "pass",
    evidence: preservedRejections.map(
      (item) => `${item.revision}:${item.sha256}`
    ).join(", ")
  },
  {
    id: "r023-r022-source-rig-probe",
    status: "pass",
    evidence: `${copied.sourceRigProbe.path}; 48 segments, 5.5mm liner, 107mm cavity, no shared roof.`
  },
  {
    id: "r023-blender-preview-only-correction",
    status: "pass",
    evidence: `${copied.previewProof.path}; R022 FBX byte-identical; UV and geometry streams unchanged.`
  },
  {
    id: "r023-isolated-unity-orientation",
    status: "pass",
    evidence: `${copied.orientationFrames.find((item) => item.path.endsWith("r022-orientation-calibration.json")).path}; Identity margin ${orientation.r022.identityMargin.toFixed(6)}.`
  },
  {
    id: "r023-actual-unity-static-preflight",
    status: "fail",
    evidence: `${copied.preflightResults.path}; 6/20 failures, including no .70 cavity pixels and .90 case contrast 0.0132 below 0.0400.`
  },
  {
    id: "r023-stop-before-tests-and-scrub",
    status: "pass",
    evidence: "Static target failure stopped before isolated tests, validators, scrub, proof, docs, build, install, or device work."
  }
];
stage.decision = {
  action: "self-reject",
  notes:
    "R023 fixes only Blender preview orientation. Actual Unity static preflight still fails segment bounds, visible cavity, liner separation, and contained-case legibility. Stop without tuning.",
  decidedAt: now,
  decidedBy: "agent-emitted-r023-static-preflight-review",
  approvalRequestAllowed: false,
  finalAuthority: "latest-explicit-chat-instruction",
  selfRejectionRecord: selfRejection.path
};
stage.evidenceReview = {
  architectureRevision: 7,
  evidenceRevision: 23,
  iteration: "r023-preview-mapping-static-preflight-self-rejection",
  disposition: "self-rejected",
  primaryArtifact: selfRejection.path,
  beforeAfterScreenEvidence: [
    copied.previewProof.path,
    copied.formed070Frame.path,
    copied.contained090Frame.path,
    copied.primaryStaticSheet.path
  ],
  shownToUserForApproval: false,
  visualApproval: "not-requested-preflight-gate-failed",
  statusText: "视觉批准待确认，未推送手机"
};
const staleReason =
  "Gate 04 R023 static preflight self-rejected: the target Unity mouth lacks layered cavity proof and legible contained-case beauty.";
for (const downstream of manifest.stages.slice(4)) {
  downstream.status = "stale";
  downstream.staleReason = staleReason;
}
manifest.model.status = "gate04-r023-static-preflight-self-rejected";
manifest.currentState = {
  ...manifest.currentState,
  activeStageId: "04-architecture",
  activeStageStatus: "draft",
  activeIteration: "r023-preview-mapping-static-preflight-self-rejection",
  visualApproval: "gate04-r023-self-rejected-preflight",
  diagnosis:
    "R023 preserves R022 geometry and Unity UV mapping, but actual Unity .70 has no visible cavity and .90 does not read as one case held inside the mouth. No scrub ran.",
  architectureApproval: {
    stageId: "04-architecture",
    architectureRevision: 7,
    evidenceRevision: 23,
    evidenceIteration: "r023-preview-mapping-static-preflight-self-rejection",
    userApprovalQuote: null,
    decisionState: "self-rejected-preflight",
    approvalRequestAllowed: false,
    gate05Status: "stale"
  },
  motionCorrection: {
    ...manifest.currentState.motionCorrection,
    gate04Status: "r023-static-preflight-self-rejected",
    currentEvidenceRevision: 23,
    currentEvidenceIteration: "r023-preview-mapping-static-preflight-self-rejection",
    rejectedEvidenceRevisions: [
      ...(manifest.currentState.motionCorrection?.rejectedEvidenceRevisions || []),
      23
    ],
    selfRejectedIterations: [
      ...(manifest.currentState.motionCorrection?.selfRejectedIterations || []),
      "r023-preview-mapping-static-preflight"
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
    "Gate 04 R023 Blender preview correction self-rejected after actual Unity static preflight. No tests, scrub, proof, docs, build, install, or device work ran.",
  statusText: "视觉批准待确认，未推送手机"
};
manifest.revision += 1;
manifest.updatedAt = now;
refreshStageDigest(manifest, stage);
const event = {
  id: crypto.randomUUID(),
  type: "gate04-r023-preview-mapping-static-preflight-self-rejected",
  modelId: "premium-display-case",
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "04-architecture",
  stageRevision: stage.revision,
  architectureRevision: 7,
  evidenceRevision: 23,
  evidenceIteration: "r023-preview-mapping-static-preflight-self-rejection",
  sourceTask: "cursor-task:premium-display-case-gate04-r023-20260901",
  previewCorrection: {
    exportedFbxByteIdenticalToR022:
      previewProof.exportInvariants.exportedFbxByteIdenticalToR022,
    uvStreamUnchanged: previewProof.exportInvariants.uvStreamUnchanged,
    geometryStreamUnchanged:
      previewProof.exportInvariants.geometryStreamUnchanged
  },
  orientation: {
    winner: orientation.r022.winner,
    identityMargin: orientation.r022.identityMargin,
    r017ControlWinner: orientation.r017Control.winner
  },
  preflight: {
    checks: preflight.checks.length,
    failures: failedChecks.length,
    failedConditions: failedIds,
    formedCavityPixels: preflight.formedMouthMaterials.visibleCavityPixels,
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
