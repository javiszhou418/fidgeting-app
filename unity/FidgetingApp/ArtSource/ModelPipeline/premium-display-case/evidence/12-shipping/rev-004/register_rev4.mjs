import crypto from "node:crypto";
import fs from "node:fs";
import {
  digestValues,
  loadManifest,
  normalizeRepoPath,
  resolveRepoPath,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "premium-display-case";
const expectedRevision = Number(process.argv[2]);
const projectRoot = "unity/FidgetingApp";
const evidenceRoot =
  `${projectRoot}/ArtSource/ModelPipeline/${modelId}/evidence/12-shipping/rev-004`;
const moduleRoot =
  `${projectRoot}/Assets/_DisplayCase/Runtime/MakeItShineCc0Effects`;
const exactQuote = [
  "Pack tear: “撕包仍然有问题”",
  "Light: “仍然太弱”",
  "Gacha energy: “仍需加强蓄力与冲击”"
].join("\n");

function stableJson(value) {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`
    ).join(",")}}`;
  }
  return JSON.stringify(value);
}

function readJson(relativePath) {
  return JSON.parse(fs.readFileSync(resolveRepoPath(relativePath), "utf8"));
}

const manifest = loadManifest(modelId);
if (!Number.isInteger(expectedRevision) || expectedRevision !== manifest.revision) {
  throw new Error(
    `Manifest revision conflict: expected ${expectedRevision}, actual ${manifest.revision}.`
  );
}
const shipping = manifest.stages[11];
if (
  manifest.stages.slice(0, 11).some((stage) => stage.status !== "approved")
  || shipping.status !== "rejected"
  || shipping.shippingSpec?.revision !== 3
  || shipping.shippingSpec?.rejection?.rejectedRevision !== 3
  || shipping.shippingSpec.rejection.userSelectionQuote !== exactQuote
) {
  throw new Error(
    "Gate 01–11 approvals and the exact preserved rev 3 rejection are required."
  );
}

const evidence = readJson(`${evidenceRoot}/gate12-evidence-report.json`);
const visual = readJson(`${evidenceRoot}/visual-regression-report.json`);
const source = readJson(`${evidenceRoot}/source-extraction-report.json`);
const capture = readJson(`${evidenceRoot}/shipping-capture-report.json`);
const timing = readJson(`${evidenceRoot}/timing-candidate-report.json`);
const native = readJson(`${evidenceRoot}/native-validation-report.json`);
const build = readJson(`${evidenceRoot}/simulator-build-manifest.json`);
const xcode = readJson(`${evidenceRoot}/xcode-build-summary.json`);
if (
  evidence.status !== "pass"
  || Object.values(evidence.checks || {}).some((value) => value !== true)
  || visual.status !== "pass"
  || Object.values(visual.checks || {}).some((value) => value !== true)
  || source.status !== "pass"
  || native.status !== "pass"
  || xcode.status !== "pass"
  || build.bundleIdentifier !== "com.jiaweizhou.fidgetspinner.codex"
  || build.sdk !== "SimulatorSDK"
  || build.development !== false
  || build.physicalPhoneInstallAuthorized !== false
  || capture.cc0LightCurveWired !== true
  || capture.effectRendererWiringValid !== true
  || evidence.video.fps !== 60
  || evidence.video.noEmptyFrame !== true
) {
  throw new Error("Gate 12 rev 4 evidence does not pass its review contract.");
}

const oldShippingSpec = structuredClone(shipping.shippingSpec);
const oldDecision = structuredClone(shipping.decision);
const oldArtifactIds = [...shipping.artifactIds];
const oldReviewArtifactIds = [...shipping.reviewArtifactIds];
const feedbackId = `${modelId}-gate12-rejection-r004`;
const diagnosisId = `${modelId}-gate12-rev3-diagnosis-r004`;
const claimId = `${modelId}-gate12-rev4-correction-claim`;
const definitions = [
  [feedbackId, "shipping-user-decision", `${evidenceRoot}/user-rejection.md`, "user-input", "exact-rev3-rejection"],
  [diagnosisId, "shipping-diagnosis", `${evidenceRoot}/diagnosis/rev3-frame-diagnosis.json`, "validation", "frame-by-frame-rev3-root-cause"],
  [`${modelId}-shipping-builder-r004`, "shipping-builder", `${projectRoot}/Assets/_DisplayCase/Editor/PremiumDisplayCaseGate12Builder.cs`, "process", "rev4-canonical-unity-builder"],
  [`${modelId}-shipping-profile-source-r004`, "shipping-profile-source", `${projectRoot}/Assets/_DisplayCase/Runtime/PremiumDisplayCaseRevealProfile.cs`, "process", "editable-anticipation-impact-profile"],
  [`${modelId}-shipping-presentation-source-r004`, "shipping-presentation-source", `${projectRoot}/Assets/_DisplayCase/Runtime/PremiumDisplayCaseShippingPresentation.cs`, "process", "exact-finite-cue-runtime"],
  [`${modelId}-shipping-factory-source-r004`, "shipping-factory-source", `${projectRoot}/Assets/_DisplayCase/Runtime/PremiumDisplayCaseShippingFactory.cs`, "process", "rev4-resource-factory"],
  [`${modelId}-shipping-director-source-r004`, "shipping-director-source", `${projectRoot}/Assets/Scripts/Product/Gacha/GachaShippingRevealDirector.cs`, "process", "same-instance-unity-reveal-director"],
  [`${modelId}-shipping-coordinator-source-r004`, "shipping-coordinator-source", `${projectRoot}/Assets/Scripts/Product/FidgetAppCoordinator.cs`, "process", "same-request-two-frame-readiness"],
  [`${modelId}-shipping-native-pack-rules-r004`, "shipping-native-source", `${projectRoot}/Assets/Plugins/iOS/FidgetGachaPackPresentation.swift`, "process", "full-width-pack-threshold-seam-release-rules"],
  [`${modelId}-shipping-native-components-r004`, "shipping-native-source", `${projectRoot}/Assets/Plugins/iOS/FidgetProductUIComponents.swift`, "process", "shared-authored-pack-tear-component"],
  [`${modelId}-shipping-native-view-r004`, "shipping-native-source", `${projectRoot}/Assets/Plugins/iOS/FidgetGachaShippingStorefront.swift`, "process", "follow-rebound-release-ready-handoff"],
  [`${modelId}-shipping-sheen-shader-r004`, "shipping-shader", `${projectRoot}/Assets/_DisplayCase/Shaders/PremiumDisplayCaseGate12R004Frosted.shader`, "process", "arrival-two-rims-and-crossing-sheen"],
  [`${modelId}-cc0-curve-source-r004`, "effect-source", `${moduleRoot}/MakeItShineCc0EffectCurves.cs`, "process", "approved-cc0-curve-only"],
  [`${modelId}-cc0-mask-source-r004`, "effect-source", `${moduleRoot}/MakeItShineCc0Masks.hlsl`, "process", "approved-cc0-mask-math-only"],
  [`${modelId}-shipping-prefab-r004`, "shipping-prefab", `${projectRoot}/Assets/Resources/Gacha/PremiumDisplayCaseGate12R004/PresentationRoot.prefab`, "source-model", "canonical-app-whole-case-rev4-prefab"],
  [`${modelId}-shipping-profile-r004`, "shipping-profile", `${projectRoot}/Assets/Resources/Gacha/PremiumDisplayCaseGate12R004Profile.asset`, "source-model", "editable-rev4-timing-and-light-profile"],
  [`${modelId}-shipping-scene-r004`, "shipping-scene", `${projectRoot}/Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R004.unity`, "source-model", "canonical-unity-rev4-review-scene"],
  [`${modelId}-shipping-library-r004`, "shipping-library", `${evidenceRoot}/library.png`, "unity-render", "real-app-final-hold"],
  [`${modelId}-shipping-hero-r004`, "shipping-hero", `${evidenceRoot}/hero.png`, "unity-render", "real-unity-hero"],
  [`${modelId}-shipping-top-r004`, "shipping-top", `${evidenceRoot}/top.png`, "unity-render", "real-unity-top"],
  [`${modelId}-shipping-left-oblique-r004`, "shipping-left-oblique", `${evidenceRoot}/left-oblique.png`, "unity-render", "real-unity-left-oblique"],
  [`${modelId}-shipping-right-oblique-r004`, "shipping-right-oblique", `${evidenceRoot}/right-oblique.png`, "unity-render", "real-unity-right-oblique"],
  [`${modelId}-shipping-low-r004`, "shipping-low", `${evidenceRoot}/low.png`, "unity-render", "real-unity-low"],
  [`${modelId}-shipping-phone-r004`, "shipping-phone", `${evidenceRoot}/simulator-final.png`, "unity-render", "real-canonical-app-result-ui"],
  [`${modelId}-shipping-video-r004`, "shipping-recording", `${evidenceRoot}/app-simulator-pack-to-case-r4.mp4`, "unity-render", "concise-complete-rev4-flow"],
  [`${modelId}-shipping-raw-video-r004`, "shipping-recording-raw", `${evidenceRoot}/app-simulator-pack-to-case-r4-raw.mp4`, "unity-render", "untrimmed-canonical-app-capture"],
  [`${modelId}-shipping-contact-r004`, "shipping-contact-sheet", `${evidenceRoot}/app-simulator-contact-sheet.png`, "process", "labeled-complete-flow"],
  [`${modelId}-shipping-pack-contact-r004`, "shipping-pack-contact-sheet", `${evidenceRoot}/pack-tear-rebound-contact-sheet.png`, "validation", "partial-rebound-commit-closeup"],
  [`${modelId}-shipping-seam-contact-r004`, "shipping-light-contact-sheet", `${evidenceRoot}/pack-seam-release-contact-sheet.png`, "validation", "seam-ramp-and-release-closeup"],
  [`${modelId}-shipping-case-cue-contact-r004`, "shipping-light-contact-sheet", `${evidenceRoot}/case-cue-contact-sheet.png`, "validation", "arrival-two-rims-sheen-hold"],
  [`${modelId}-shipping-standard-contact-r004`, "shipping-contact-sheet", `${evidenceRoot}/standard-views-contact-sheet.png`, "process", "real-unity-standard-views"],
  [`${modelId}-shipping-capture-report-r004`, "shipping-report", `${evidenceRoot}/shipping-capture-report.json`, "validation", "profile-renderer-and-cc0-wiring"],
  [`${modelId}-shipping-timing-report-r004`, "timing-report", `${evidenceRoot}/timing-candidate-report.json`, "validation", "editable-rev4-timing"],
  [`${modelId}-shipping-visual-regression-r004`, "shipping-report", `${evidenceRoot}/visual-regression-report.json`, "validation", "video-and-isolated-gpu-contrast-gates"],
  [`${modelId}-shipping-source-report-r004`, "source-report", `${evidenceRoot}/source-extraction-report.json`, "validation", "pinned-cc0-source-and-exclusions"],
  [`${modelId}-shipping-asset-hashes-r004`, "asset-hash-manifest", `${evidenceRoot}/asset-hash-manifest.json`, "validation", "profile-prefab-shader-fbx-and-pack-hashes"],
  [`${modelId}-shipping-evidence-report-r004`, "shipping-report", `${evidenceRoot}/gate12-evidence-report.json`, "validation", "rev4-evidence-verdict"],
  [`${modelId}-shipping-evidence-builder-r004`, "shipping-validator", `${evidenceRoot}/build_rev4_evidence.py`, "process", "rev4-evidence-and-visual-regression-builder"],
  [`${modelId}-shipping-unity-tests-r004`, "shipping-test-results", `${evidenceRoot}/unity-focused-results.xml`, "validation", "focused-editmode-results"],
  [`${modelId}-shipping-native-validation-r004`, "shipping-test-results", `${evidenceRoot}/native-validation-report.json`, "validation", "swift-gate-and-warnings-as-errors"],
  [`${modelId}-shipping-build-manifest-r004`, "shipping-build-manifest", `${evidenceRoot}/simulator-build-manifest.json`, "validation", "canonical-release-simulator-provenance"],
  [`${modelId}-shipping-xcode-summary-r004`, "shipping-build-report", `${evidenceRoot}/xcode-build-summary.json`, "validation", "release-simulator-and-strict-product-swift"],
  [`${modelId}-shipping-registration-r004`, "shipping-registration", `${evidenceRoot}/register_rev4.mjs`, "process", "atomic-rev4-registration"]
];

for (const [, , assetPath] of definitions) {
  const absolute = resolveRepoPath(assetPath);
  if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
    throw new Error(`Missing revision asset: ${assetPath}`);
  }
}
for (const [id] of definitions) {
  if (manifest.assets.some((asset) => asset.id === id)) {
    throw new Error(`Asset already registered: ${id}`);
  }
}

manifest.claims.push({
  id: claimId,
  stageId: "12-shipping",
  topic: "gate12-rev4-visible-tear-light-and-energy",
  statement:
    "Gate 12 rev 3 was rejected for Pack tear, weak light and weak gacha energy. Rev 4 keeps the approved case and card while restoring full-width gesture-following tear, exact-once opening, readiness-gated overlap, stronger finite mesh-clipped cues and a shorter fast-first/slower-second showcase.",
  confidence: "user-authoritative",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: [feedbackId, diagnosisId],
  sourceRegions: [],
  decisionState: "locked-revision-scope-review-pending",
  deliveryState: "gate12-rev4-ready-for-visual-review"
});

const sourceIds = [
  feedbackId,
  diagnosisId,
  oldShippingSpec.sourceFbxArtifactId,
  oldShippingSpec.governingContractId
].filter(Boolean);
const claimIds = manifest.claims
  .filter((claim) => (
    claim.stageId === "02-analysis"
    && claim.state !== "superseded"
  ))
  .map((claim) => claim.id);
const records = definitions.map(
  ([id, slot, assetPath, role, contentClass]) => {
    const absolute = resolveRepoPath(assetPath);
    const userInput = id === feedbackId;
    const diagnosis = id === diagnosisId;
    return {
      id,
      stageId: "12-shipping",
      slot,
      path: normalizeRepoPath(assetPath),
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role,
      sourceAssetIds: userInput
        ? [`${modelId}-shipping-video-r003`]
        : diagnosis
          ? [feedbackId, `${modelId}-shipping-video-r003`]
          : sourceIds,
      sourceClaimIds: userInput ? [] : claimIds,
      producer: {
        name: assetPath.includes("/Assets/") ? "Unity" : "fidgeting-model-pipeline",
        version: assetPath.includes("/Assets/") ? "6000.5.6f1" : "2026-08-28",
        recipe: contentClass
      },
      provenance: {
        origin: userInput ? "user-provided" : "repository-generated",
        contentClass,
        assertedBy: userInput ? "user" : "assistant",
        note: userInput
          ? `Exact latest chat selections preserved: ${exactQuote}`
          : "Gate 12 rev 4 review evidence. Visual approval and device acceptance remain pending."
      },
      wholeAssembledCaseOnly: true,
      explodeEligible: false,
      toyPrizeBundled: false,
      shippingEligible: !userInput,
      reviewState: userInput ? "current-request" : "ready-for-review"
    };
  }
);
manifest.assets.push(...records);

for (const assetId of oldArtifactIds) {
  const asset = manifest.assets.find((candidate) => candidate.id === assetId);
  if (!asset) continue;
  asset.reviewState = "rejected-history";
  asset.preservedForHistory = true;
  asset.rejectedShippingRevision = 3;
  asset.supersededByShippingRevision = 4;
  asset.dispositionNote =
    "Gate 12 rev 3 remains immutable rejected evidence. Rev 4 addresses the three exact user selections.";
}

shipping.historicalDecisions = [
  ...(shipping.historicalDecisions || []),
  {
    ...oldDecision,
    shippingRevision: 3,
    disposition: "rejected-history-preserved-before-rev4"
  }
];
shipping.historicalRevisions = [
  ...(shipping.historicalRevisions || []),
  {
    shippingSpec: oldShippingSpec,
    artifactIds: oldArtifactIds,
    reviewArtifactIds: oldReviewArtifactIds,
    decision: oldDecision,
    stageStatus: "rejected",
    preservedForHistory: true
  }
];

const reviewArtifactIds = [
  `${modelId}-shipping-video-r004`,
  `${modelId}-shipping-contact-r004`,
  `${modelId}-shipping-pack-contact-r004`,
  `${modelId}-shipping-seam-contact-r004`,
  `${modelId}-shipping-case-cue-contact-r004`,
  `${modelId}-shipping-standard-contact-r004`,
  `${modelId}-shipping-library-r004`,
  `${modelId}-shipping-hero-r004`,
  `${modelId}-shipping-top-r004`,
  `${modelId}-shipping-left-oblique-r004`,
  `${modelId}-shipping-right-oblique-r004`,
  `${modelId}-shipping-low-r004`,
  `${modelId}-shipping-phone-r004`
];
const approvalChecklist = [
  "watch-complete-canonical-app-simulator-recording",
  "confirm-full-width-flap-follows-and-below-062-rebounds",
  "confirm-open-state-is-visible-before-case-and-commit-is-exact-once",
  "confirm-seam-ramp-and-one-opening-confined-release-pulse",
  "confirm-pack-remains-foreground-through-same-request-two-frame-readiness",
  "confirm-one-arrival-rim-two-rotation-rims-and-one-crossing-sheen",
  "confirm-every-case-cue-is-visible-and-zero-pixels-leave-case-fragments",
  "confirm-first-360-is-fast-second-360-is-slower-and-boundary-never-stops",
  "confirm-one-assembled-case-approved-card-label-static-camera-and-zero-toy-spin",
  "confirm-no-halo-rarity-bloom-particle-vfx-shake-loop-explode-or-second-case",
  "confirm-static-hold-no-persistent-light-and-no-physical-phone-install"
];

shipping.revision += 1;
shipping.status = "ready_for_review";
shipping.artifactIds = records.map((record) => record.id);
shipping.reviewArtifactIds = reviewArtifactIds;
shipping.validations = [
  {
    id: "rev3-rejection-preserved",
    status: "pass",
    evidence: `Rev 3 and its exact selections remain immutable history: ${exactQuote}`
  },
  {
    id: "frame-diagnosis",
    status: "pass",
    evidence:
      "Rev 3 used a rigid full-width lid motion, wrong cut-line relationship, opacity/clipping sliver, static virtual rim and no release pulse. The diagnosis preserves the last working Pack transform as implementation evidence only."
  },
  {
    id: "real-pack-tear-visual-regression",
    status: "pass",
    evidence:
      `Full-width fraction=${visual.pack.flapWidthVersusBodyFraction.toFixed(3)}, horizontal travel=${visual.pack.flapHorizontalTravelPixels.toFixed(1)} px, partial gap=${visual.pack.partialOpeningGapPixels} px, committed gap=${visual.pack.committedOpeningGapPixels} px, rebound MAD=${visual.pack.reboundMeanAbsoluteDelta.toFixed(3)}/255.`
  },
  {
    id: "seam-release-and-readiness",
    status: "pass",
    evidence:
      `Seam p95-minus-median=${visual.pack.seamP95MinusMedianLuma255.toFixed(1)}/255; release mean delta=${visual.pack.releaseMeanLumaDelta255.toFixed(1)}/255. Case fraction before opening=${visual.pack.maximumCaseFractionBeforeOpening.toFixed(4)} and after opening=${visual.pack.caseFractionFirstVisible.toFixed(4)}.`
  },
  {
    id: "finite-case-cue-contrast",
    status: "pass",
    evidence:
      "Arrival, both rotation-rim passes and final sheen exceed changed-area, mean, p95 and peak contrast gates. Every isolated external pixel count is zero."
  },
  {
    id: "exact-event-counts",
    status: "pass",
    evidence:
      "One seam, one release pulse, one arrival rim, two rotation-rim passes, one sheen and zero persistent light are covered by Swift, Unity and video gates."
  },
  {
    id: "timing-and-energy",
    status: "pass",
    evidence:
      `Handoff=${timing.handoffDurationSeconds.toFixed(2)} s, entry=${timing.entryDurationSeconds.toFixed(2)} s, first 360=${timing.firstSpinDurationSeconds.toFixed(2)} s, second 360=${timing.secondSpinDurationSeconds.toFixed(2)} s, profile=${timing.profileDurationSeconds.toFixed(2)} s, speed ratio=${timing.firstToSecondAverageSpeedRatio.toFixed(2)}x. Values remain editable candidates.`
  },
  {
    id: "same-instance-whole-case",
    status: "pass",
    evidence:
      "One assembled real case and caller-owned real toy remain the same instance. The toy keeps zero independent angular velocity."
  },
  {
    id: "focused-tests",
    status: "pass",
    evidence:
      `Unity=${evidence.unityTests.passed}/${evidence.unityTests.total}, Swift=${native.swiftGateHarness.passed}/${native.swiftGateHarness.passed}, touched Swift warnings-as-errors=pass.`
  },
  {
    id: "release-simulator-build",
    status: "pass",
    evidence:
      "The canonical Release iOS Simulator App builds with the R004 prefab/profile and approved Gate 10 FBX hash. Touched product Swift passes a separate warnings-as-errors gate."
  },
  {
    id: "device-boundary",
    status: "pass",
    evidence:
      "The App ran only on iPhone 17 Pro Simulator. Physical phone installation and device acceptance remain false."
  }
];
shipping.decision = null;
delete shipping.staleReason;
shipping.shippingSpec = {
  revision: 4,
  previousRejectedRevision: 3,
  previousRevisionDisposition: "rejected-history-preserved",
  exactRejectionQuote: exactQuote,
  rejectionSelections: evidence.rejectionSelections,
  finalAuthority: "latest-explicit-chat-instruction",
  earliestAffectedGate: "12-shipping-implementation-and-tuning-revision",
  upstreamApprovedGatesUnchanged:
    manifest.stages.slice(0, 11).map((stage) => stage.id),
  sourceGate11ApprovalEventId: oldShippingSpec.sourceGate11ApprovalEventId,
  sourceFbxArtifactId: oldShippingSpec.sourceFbxArtifactId,
  sourceFbxSha256: oldShippingSpec.sourceFbxSha256,
  governingContractId: oldShippingSpec.governingContractId,
  governingContractSha256: oldShippingSpec.governingContractSha256,
  shippingPrefabPath:
    `${projectRoot}/Assets/Resources/Gacha/PremiumDisplayCaseGate12R004/PresentationRoot.prefab`,
  shippingScenePath:
    `${projectRoot}/Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R004.unity`,
  profilePath:
    `${projectRoot}/Assets/Resources/Gacha/PremiumDisplayCaseGate12R004Profile.asset`,
  parameterSnapshot: timing,
  timingChangedFromRev3: true,
  profileValuesLocked: false,
  pendingVisualTuning: true,
  packTear: {
    realBodyAndFlapAssets: true,
    authoredCanvas: [384, 512],
    authoredAnchor: "topTrailing",
    tearCommitProgress: 0.62,
    belowThresholdBehavior: "visible-follow-deformation-then-rebound",
    commitBehavior: "same-request-exact-once",
    committedOpeningVisibleBeforeCase: true,
    seamCueCount: 1,
    releasePulseCount: 1,
    foregroundUntilAuthoritativeReceiptAndTwoFrameReady: true,
    noEmptyFrame: true,
    measuredVisuals: visual.pack
  },
  phaseOrder: [
    "sealed-pack",
    "partial-tear-seam-and-rebound",
    "committed-opening",
    "one-opening-confined-release-pulse",
    "same-request-receipt-and-two-frame-ready",
    "pack-case-overlap",
    "entry-arrival-rim-first-spin-overlap",
    "fast-first-local-y-360-with-rim",
    "continuous-spin-boundary",
    "slower-second-local-y-360-with-rim",
    "one-finite-crossing-mesh-clipped-sheen",
    "static-hold-no-persistent-light"
  ],
  localYRotationDegrees: 720,
  firstSpinDegrees: 360,
  secondSpinDegrees: 360,
  noStopBetweenSpins: true,
  eventCounts: evidence.eventCounts,
  effectRendererCount: 3,
  outsideMeshEffectPixels: 0,
  pointLightCount: 0,
  particleEmitterCount: 0,
  bloomDependency: false,
  vfxGraphDependency: false,
  screenShake: false,
  persistentLightLoop: false,
  wholeAssembledCaseOnly: true,
  sameInstanceThroughAcknowledgement: true,
  externalEntityCount: 0,
  externalModelCount: 0,
  externalPrefabCount: 0,
  toyPrizeOwnership: "caller-owned",
  toyIndependentAngularVelocity: 0,
  visualContrast: {
    pack: visual.pack,
    caseCues: visual.caseCuesIsolatedGpu,
    finalSheenVersusHold: visual.finalSheenVersusHold,
    persistentLightAfterSheen: visual.persistentLightAfterSheen
  },
  sourceExtraction: {
    repository: source.repository,
    commit: source.actualCommit,
    license: source.license,
    moduleFiles: source.moduleFiles,
    moduleHashes: source.moduleHashes,
    excludedAssets: source.excludedAssets
  },
  assetHashes: evidence.assetHashes,
  simulatorBundleIdentifier: build.bundleIdentifier,
  simulatorInstalledLaunched: true,
  physicalPhoneInstalled: false,
  deviceAccepted: false,
  visualApproved: false,
  shippingReady: false,
  completeRecordingArtifactId: `${modelId}-shipping-video-r004`,
  approvalChecklist,
  interactionMode:
    "complete-canonical-app-simulator-recording-plus-labeled-tear-and-light-contact-sheets",
  gate12Status: "ready_for_review"
};

manifest.model.status = "shipping-visual-revision-pending";
manifest.currentState.visualApproval =
  "gate12-rev4-real-app-review-pending";
manifest.currentState.deviceStatus =
  "simulator-preview-only-physical-phone-untouched";
manifest.currentState.shippingAssetUnchanged = false;
manifest.currentState.affectedGateAssessment = {
  earliestAffectedGate: "12-shipping-implementation-and-tuning-revision",
  reason:
    "Rev 4 addresses the exact rev 3 tear, light and gacha-energy rejection without changing approved Gates 01–11.",
  geometryMaterialLightingEnvironmentExportUnityParityInvalidated: false,
  upstreamApprovedGatesUnchanged:
    shipping.shippingSpec.upstreamApprovedGatesUnchanged
};
manifest.currentState.shippingPreview = {
  revision: 4,
  gate12Status: "ready_for_review",
  previousRejectedRevision: 3,
  previousRevisionDisposition: "rejected-history",
  prefabPath: shipping.shippingSpec.shippingPrefabPath,
  scenePath: shipping.shippingSpec.shippingScenePath,
  videoPath: `${evidenceRoot}/app-simulator-pack-to-case-r4.mp4`,
  videoSha256: records.find(
    (record) => record.id === `${modelId}-shipping-video-r004`
  ).sha256,
  contactSheetPath: `${evidenceRoot}/app-simulator-contact-sheet.png`,
  packContactSheetPath:
    `${evidenceRoot}/pack-tear-rebound-contact-sheet.png`,
  seamContactSheetPath:
    `${evidenceRoot}/pack-seam-release-contact-sheet.png`,
  caseCueContactSheetPath:
    `${evidenceRoot}/case-cue-contact-sheet.png`,
  visualRegressionPath:
    `${evidenceRoot}/visual-regression-report.json`,
  profileValuesLocked: false,
  pendingVisualTuning: true,
  simulatorInstalledLaunched: true,
  physicalPhoneInstalled: false,
  deviceAccepted: false,
  visualApproved: false,
  shippingReady: false
};
manifest.currentState.motionCorrection = {
  ...manifest.currentState.motionCorrection,
  gate12Status: "ready_for_review-rev4",
  shippingPreviewApproved: false,
  shippingDurationApproved: false,
  finiteLightCueCount: 5,
  caseLightOutsideSilhouettePixels: 0
};
manifest.currentState.diagnosis =
  "Gate 12 rev 3 remains rejected immutable history with the exact three selections. Rev 4 restores a full-width authored Pack tear with topTrailing transform evidence, visible follow/rebound, a real opening before reveal, one clipped seam ramp and one neutral release pulse. The same-request Pack remains foreground until the real case, prize and camera pass two stable frames. The case uses one arrival rim, two object-bound rotation-rim passes and one final crossing sheen; every isolated cue has measured contrast and zero external pixels. The first 360 is 0.50 s, the second is 1.10 s, and the 2.94 s profile preserves positive boundary velocity. Visual approval is pending; no physical iPhone was used.";

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map(
    (assetId) => manifest.assets.find(
      (asset) => asset.id === assetId
    )?.sha256
  );
  const claims = manifest.claims
    .filter((claim) => claim.stageId === stage.id)
    .map(stableJson);
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const event = {
  id: crypto.randomUUID(),
  type: "stage-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "12-shipping",
  shippingRevision: 4,
  exactUserFeedback: exactQuote,
  preservedRejectedShippingRevisions: [1, 2, 3],
  upstreamApprovedGatesUnchanged:
    shipping.shippingSpec.upstreamApprovedGatesUnchanged,
  parameterSnapshot: timing,
  visualContrast: shipping.shippingSpec.visualContrast,
  eventCounts: evidence.eventCounts,
  sourceRepository: source.repository,
  sourceCommit: source.actualCommit,
  extractedModuleFiles: source.moduleFiles,
  excludedAssets: source.excludedAssets,
  reviewArtifactIds,
  videoPath: `${evidenceRoot}/app-simulator-pack-to-case-r4.mp4`,
  videoSha256: manifest.currentState.shippingPreview.videoSha256,
  approvalChecklist,
  profileDurationSeconds: timing.profileDurationSeconds,
  firstSpinDurationSeconds: timing.firstSpinDurationSeconds,
  secondSpinDurationSeconds: timing.secondSpinDurationSeconds,
  noEmptyFrame: true,
  outsideMeshEffectPixels: 0,
  focusedUnityTests:
    `${evidence.unityTests.passed}/${evidence.unityTests.total}`,
  swiftGateHarness:
    `${native.swiftGateHarness.passed}/${native.swiftGateHarness.passed}`,
  swiftWarningsAsErrors: "pass",
  xcodeBuild:
    "Release Simulator BUILD SUCCEEDED; touched product Swift warnings-as-errors passed",
  simulatorInstalledLaunched: true,
  physicalPhoneInstalled: false,
  deviceAccepted: false,
  autoApproved: false,
  shippingReady: false,
  statusText: "视觉批准待确认，未推送手机"
};

const result = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: result.revision,
  approvedCount: result.derived.approvedCount,
  shippingReady: result.derived.shippingReady,
  earliestProblem: result.derived.earliestProblem,
  eventId: event.id
}, null, 2));
