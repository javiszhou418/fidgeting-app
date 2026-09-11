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
const exactFeedback = "光效在哪里啊，完全没有实现啊，然后pack撕开的效果又坏了";
const projectRoot = "unity/FidgetingApp";
const evidenceRoot = `${projectRoot}/ArtSource/ModelPipeline/${modelId}/evidence/12-shipping/rev-003`;
const moduleRoot = `${projectRoot}/Assets/_DisplayCase/Runtime/MakeItShineCc0Effects`;

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
  || shipping.shippingSpec?.revision !== 2
  || shipping.shippingSpec?.rejection?.rejectedRevision !== 2
) {
  throw new Error("Gate 01–11 approval and the preserved rev 2 rejection are required.");
}

const evidence = readJson(`${evidenceRoot}/gate12-evidence-report.json`);
const source = readJson(`${evidenceRoot}/source-extraction-report.json`);
const capture = readJson(`${evidenceRoot}/shipping-capture-report.json`);
const timing = readJson(`${evidenceRoot}/timing-candidate-report.json`);
const native = readJson(`${evidenceRoot}/native-validation-report.json`);
const build = readJson(`${evidenceRoot}/simulator-build-manifest.json`);
const xcode = readJson(`${evidenceRoot}/xcode-build-summary.json`);
if (
  evidence.status !== "pass"
  || Object.values(evidence.checks || {}).some((value) => value !== true)
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
  throw new Error("Gate 12 rev 3 evidence does not pass its shipping contract.");
}

const oldShippingSpec = structuredClone(shipping.shippingSpec);
const oldDecision = structuredClone(shipping.decision);
const oldArtifactIds = [...shipping.artifactIds];
const oldReviewArtifactIds = [...shipping.reviewArtifactIds];
const feedbackId = `${modelId}-gate12-defect-feedback-r003`;
const claimId = `${modelId}-gate12-defect-repair-claim-r003`;
const definitions = [
  [feedbackId, "shipping-user-decision", `${evidenceRoot}/user-defect-feedback.md`, "user-input", "exact-gate12-rev2-defect-feedback"],
  [`${modelId}-shipping-builder-r003`, "shipping-builder", `${projectRoot}/Assets/_DisplayCase/Editor/PremiumDisplayCaseGate12Builder.cs`, "process", "rev3-canonical-unity-builder"],
  [`${modelId}-shipping-profile-source-r003`, "shipping-profile-source", `${projectRoot}/Assets/_DisplayCase/Runtime/PremiumDisplayCaseRevealProfile.cs`, "process", "visible-four-cue-profile-source"],
  [`${modelId}-shipping-presentation-source-r003`, "shipping-presentation-source", `${projectRoot}/Assets/_DisplayCase/Runtime/PremiumDisplayCaseShippingPresentation.cs`, "process", "validated-material-property-block-wiring"],
  [`${modelId}-shipping-factory-source-r003`, "shipping-factory-source", `${projectRoot}/Assets/_DisplayCase/Runtime/PremiumDisplayCaseShippingFactory.cs`, "process", "rev3-resources-factory"],
  [`${modelId}-shipping-director-source-r003`, "shipping-director-source", `${projectRoot}/Assets/Scripts/Product/Gacha/GachaShippingRevealDirector.cs`, "process", "same-instance-unity-reveal-director"],
  [`${modelId}-shipping-coordinator-source-r003`, "shipping-coordinator-source", `${projectRoot}/Assets/Scripts/Product/FidgetAppCoordinator.cs`, "process", "same-request-receipt-and-two-frame-ready"],
  [`${modelId}-shipping-native-pack-rules-r003`, "shipping-native-source", `${projectRoot}/Assets/Plugins/iOS/FidgetGachaPackPresentation.swift`, "process", "tear-progress-threshold-seam-and-handoff-rules"],
  [`${modelId}-shipping-native-components-r003`, "shipping-native-source", `${projectRoot}/Assets/Plugins/iOS/FidgetProductUIComponents.swift`, "process", "shared-real-pack-tear-visual-component"],
  [`${modelId}-shipping-native-view-r003`, "shipping-native-source", `${projectRoot}/Assets/Plugins/iOS/FidgetGachaShippingStorefront.swift`, "process", "partial-rebound-commit-and-ready-gated-handoff"],
  [`${modelId}-shipping-sheen-shader-r003`, "shipping-shader", `${projectRoot}/Assets/_DisplayCase/Shaders/PremiumDisplayCaseGate12R003Frosted.shader`, "process", "visible-object-local-arrival-rim-rotation-rim-and-sheen"],
  [`${modelId}-cc0-curve-source-r003`, "effect-source", `${moduleRoot}/MakeItShineCc0EffectCurves.cs`, "process", "pinned-curve-plus-runtime-match-verification"],
  [`${modelId}-cc0-mask-source-r003`, "effect-source", `${moduleRoot}/MakeItShineCc0Masks.hlsl`, "process", "object-local-diagonal-band-without-double-attenuation"],
  [`${modelId}-shipping-prefab-r003`, "shipping-prefab", `${projectRoot}/Assets/Resources/Gacha/PremiumDisplayCaseGate12R003/PresentationRoot.prefab`, "source-model", "canonical-app-whole-case-rev3-prefab"],
  [`${modelId}-shipping-profile-r003`, "shipping-profile", `${projectRoot}/Assets/Resources/Gacha/PremiumDisplayCaseGate12R003Profile.asset`, "source-model", "rev2-timing-preserved-visible-effect-profile"],
  [`${modelId}-shipping-scene-r003`, "shipping-scene", `${projectRoot}/Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R003.unity`, "source-model", "canonical-unity-rev3-review-scene"],
  [`${modelId}-shipping-library-r003`, "shipping-library", `${evidenceRoot}/library.png`, "unity-render", "real-app-final-hold-and-result"],
  [`${modelId}-shipping-hero-r003`, "shipping-hero", `${evidenceRoot}/hero.png`, "unity-render", "real-unity-hero"],
  [`${modelId}-shipping-top-r003`, "shipping-top", `${evidenceRoot}/top.png`, "unity-render", "real-unity-top"],
  [`${modelId}-shipping-left-oblique-r003`, "shipping-left-oblique", `${evidenceRoot}/left-oblique.png`, "unity-render", "real-unity-left-oblique"],
  [`${modelId}-shipping-right-oblique-r003`, "shipping-right-oblique", `${evidenceRoot}/right-oblique.png`, "unity-render", "real-unity-right-oblique"],
  [`${modelId}-shipping-low-r003`, "shipping-low", `${evidenceRoot}/low.png`, "unity-render", "real-unity-low"],
  [`${modelId}-shipping-phone-r003`, "shipping-phone", `${evidenceRoot}/simulator-final.png`, "unity-render", "real-canonical-app-result-ui"],
  [`${modelId}-shipping-video-r003`, "shipping-recording", `${evidenceRoot}/app-simulator-pack-to-case-r3.mp4`, "unity-render", "sealed-partial-rebound-commit-four-cues-two-spins-result"],
  [`${modelId}-shipping-raw-video-r003`, "shipping-recording-raw", `${evidenceRoot}/app-simulator-pack-to-case-r3-raw.mp4`, "unity-render", "untrimmed-canonical-app-simulator-capture"],
  [`${modelId}-shipping-contact-r003`, "shipping-contact-sheet", `${evidenceRoot}/app-simulator-contact-sheet.png`, "process", "full-rev3-flow-with-frame-time-labels"],
  [`${modelId}-shipping-pack-contact-r003`, "shipping-pack-contact-sheet", `${evidenceRoot}/pack-tear-contact-sheet.png`, "validation", "sealed-partial-rebound-commit-ready-closeup"],
  [`${modelId}-shipping-light-contact-r003`, "shipping-light-contact-sheet", `${evidenceRoot}/light-closeup-contact-sheet.png`, "validation", "seam-arrival-two-rims-sheen-closeup"],
  [`${modelId}-shipping-standard-contact-r003`, "shipping-contact-sheet", `${evidenceRoot}/standard-views-contact-sheet.png`, "process", "real-unity-standard-views"],
  [`${modelId}-shipping-capture-report-r003`, "shipping-report", `${evidenceRoot}/shipping-capture-report.json`, "validation", "profile-renderer-and-cc0-wiring-report"],
  [`${modelId}-shipping-timing-report-r003`, "timing-report", `${evidenceRoot}/timing-candidate-report.json`, "validation", "rev2-timing-preserved-visibility-candidate"],
  [`${modelId}-shipping-source-report-r003`, "source-report", `${evidenceRoot}/source-extraction-report.json`, "validation", "pinned-cc0-source-and-exclusion-verdict"],
  [`${modelId}-shipping-asset-hashes-r003`, "asset-hash-manifest", `${evidenceRoot}/asset-hash-manifest.json`, "validation", "profile-prefab-shader-fbx-and-pack-hashes"],
  [`${modelId}-shipping-evidence-report-r003`, "shipping-report", `${evidenceRoot}/gate12-evidence-report.json`, "validation", "independent-rev3-evidence-verdict"],
  [`${modelId}-shipping-evidence-builder-r003`, "shipping-validator", `${evidenceRoot}/build_rev3_evidence.py`, "process", "rev3-video-contact-and-contract-validator"],
  [`${modelId}-shipping-unity-tests-r003`, "shipping-test-results", `${evidenceRoot}/unity-focused-results.xml`, "validation", "focused-editmode-results"],
  [`${modelId}-shipping-native-validation-r003`, "shipping-test-results", `${evidenceRoot}/native-validation-report.json`, "validation", "swift-gate-typecheck-and-xcode-validation"],
  [`${modelId}-shipping-build-manifest-r003`, "shipping-build-manifest", `${evidenceRoot}/simulator-build-manifest.json`, "validation", "canonical-bundle-and-source-hashes"],
  [`${modelId}-shipping-xcode-summary-r003`, "shipping-build-report", `${evidenceRoot}/xcode-build-summary.json`, "validation", "release-simulator-build-summary"],
  [`${modelId}-shipping-registration-r003`, "shipping-registration", `${evidenceRoot}/register_rev3.mjs`, "process", "atomic-revision-registration"]
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
  topic: "gate12-rev3-defect-repair",
  statement: "用户明确指出 Gate 12 rev 2 光效未实际可见且 Pack 撕开退化。rev 3 只修 shipping 接线、材质可见峰值和真实 Pack flap/opening/seam，不改变 Gates 01–11 或已锁定两圈节奏。",
  confidence: "user-authoritative",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: [feedbackId],
  sourceRegions: [],
  decisionState: "locked-defect-correction",
  deliveryState: "gate12-rev3-ready-for-visual-review"
});

const sourceIds = [
  feedbackId,
  oldShippingSpec.sourceFbxArtifactId,
  oldShippingSpec.governingContractId
].filter(Boolean);
const claimIds = [
  ...manifest.claims
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id)
];
const records = definitions.map(
  ([id, slot, assetPath, role, contentClass]) => {
    const absolute = resolveRepoPath(assetPath);
    const isFeedback = id === feedbackId;
    return {
      id,
      stageId: "12-shipping",
      slot,
      path: normalizeRepoPath(assetPath),
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role,
      sourceAssetIds: isFeedback
        ? [`${modelId}-shipping-video-r002`]
        : sourceIds,
      sourceClaimIds: isFeedback ? [] : claimIds,
      producer: {
        name: assetPath.includes("/Assets/") ? "Unity" : "fidgeting-model-pipeline",
        version: assetPath.includes("/Assets/") ? "6000.5.6f1" : "2026-08-27",
        recipe: contentClass
      },
      provenance: {
        origin: isFeedback ? "user-provided" : "repository-generated",
        contentClass,
        assertedBy: isFeedback ? "user" : "assistant",
        note: isFeedback
          ? `Exact chat feedback preserved: “${exactFeedback}”.`
          : "Gate 12 rev 3 implementation-defect repair evidence. Visual approval and physical phone acceptance remain pending."
      },
      wholeAssembledCaseOnly: true,
      explodeEligible: false,
      toyPrizeBundled: false,
      shippingEligible: !isFeedback,
      reviewState: isFeedback ? "current-request" : "ready-for-review"
    };
  }
);
manifest.assets.push(...records);

for (const assetId of oldArtifactIds) {
  const asset = manifest.assets.find((candidate) => candidate.id === assetId);
  if (!asset) continue;
  asset.reviewState = "rejected-history";
  asset.preservedForHistory = true;
  asset.rejectedShippingRevision = 2;
  asset.supersededByShippingRevision = 3;
  asset.dispositionNote = "Gate 12 rev 2 remains immutable rejected evidence. Rev 3 repairs missing visible light wiring and the Pack tear regression.";
}

shipping.historicalDecisions = [
  ...(shipping.historicalDecisions || []),
  {
    ...oldDecision,
    shippingRevision: 2,
    disposition: "rejected-history-preserved-before-rev3-defect-repair"
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
  `${modelId}-shipping-video-r003`,
  `${modelId}-shipping-contact-r003`,
  `${modelId}-shipping-pack-contact-r003`,
  `${modelId}-shipping-light-contact-r003`,
  `${modelId}-shipping-standard-contact-r003`,
  `${modelId}-shipping-library-r003`,
  `${modelId}-shipping-hero-r003`,
  `${modelId}-shipping-top-r003`,
  `${modelId}-shipping-left-oblique-r003`,
  `${modelId}-shipping-right-oblique-r003`,
  `${modelId}-shipping-low-r003`,
  `${modelId}-shipping-phone-r003`
];
const approvalChecklist = [
  "watch-complete-sealed-pack-to-result-recording",
  "confirm-partial-tear-follows-and-below-062-rebounds",
  "confirm-threshold-commit-is-exact-once-and-real-flap-opening-remain-readable",
  "confirm-pack-stays-foreground-until-same-request-receipt-and-two-frame-ready",
  "confirm-pack-seam-arrival-rim-and-both-rotation-rims-are-visible",
  "confirm-final-sheen-is-clearly-readable-and-zero-pixels-leave-case-fragments",
  "confirm-first-360-remains-faster-than-second-with-no-boundary-stop",
  "confirm-one-assembled-same-instance-case-authoritative-label-and-zero-toy-spin",
  "confirm-no-holder-explode-three-card-entity-rarity-flash-particle-or-halo",
  "confirm-static-hold-result-ui-and-no-physical-phone-install"
];

shipping.revision += 1;
shipping.status = "ready_for_review";
shipping.artifactIds = records.map((record) => record.id);
shipping.reviewArtifactIds = reviewArtifactIds;
shipping.validations = [
  { id: "targeted-defect-revision", status: "pass", evidence: "Gate 12 rev 3 changes shipping implementation only. Gates 01–11 remain approved and unchanged." },
  { id: "rev2-rejection-preserved", status: "pass", evidence: `Gate 12 rev 2 video, artifacts and rejection remain immutable history with exact defect evidence “${exactFeedback}”.` },
  { id: "real-pack-tear", status: "pass", evidence: "The real body and full-canvas flap share one frame. Below 0.62 follows then rebounds; 0.62 or above commits once. A finite seam strip stays inside the Pack opening." },
  { id: "ready-gated-no-empty-frame", status: "pass", evidence: "Pack remains foreground until the same-request receipt and real case, prize and camera are stable for two frames. The 8.4 s review video has no empty frame." },
  { id: "effect-module-wired", status: "pass", evidence: "The pinned CC0 curve matches at runtime, the HLSL band is included, all three shell renderers support every property and MaterialPropertyBlock writes visible peaks." },
  { id: "four-visible-light-cues", status: "pass", evidence: "Pack seam, arrival rim, object-bound rim across both circles and one final sheen are visible. GPU tests report zero changed pixels outside case fragments." },
  { id: "timing-preserved", status: "pass", evidence: "Rev 2 timing is unchanged: handoff 0.18 s, entry 0.82 s, first 360 in 0.72 s, second 360 in 1.18 s, overlap 0.22 s, sheen 0.42 s, hold 0.68 s, profile 3.60 s." },
  { id: "same-instance-whole-case", status: "pass", evidence: "One assembled real case and caller-owned real toy remain the same instance. Toy independent angular velocity is zero." },
  { id: "focused-tests", status: "pass", evidence: "Relevant Unity EditMode tests pass 53/53, Swift gate harness passes 37/37 and touched shipping Swift passes warnings-as-errors typecheck." },
  { id: "release-simulator-build", status: "pass", evidence: "The canonical Release iOS Simulator App builds and runs with R003 prefab/profile and the approved Gate 10 FBX hash." },
  { id: "device-boundary", status: "pass", evidence: "The App ran only on iPhone 17 Pro Simulator. Physical phone installation and device acceptance remain false." }
];
shipping.decision = null;
delete shipping.staleReason;
shipping.shippingSpec = {
  revision: 3,
  previousRejectedRevision: 2,
  previousRevisionDisposition: "rejected-history-preserved",
  exactDefectFeedback: exactFeedback,
  finalAuthority: "latest-explicit-chat-instruction",
  earliestAffectedGate: "12-shipping-implementation-defect",
  upstreamApprovedGatesUnchanged: manifest.stages.slice(0, 11).map((stage) => stage.id),
  sourceGate11ApprovalEventId: oldShippingSpec.sourceGate11ApprovalEventId,
  sourceFbxArtifactId: oldShippingSpec.sourceFbxArtifactId,
  sourceFbxSha256: oldShippingSpec.sourceFbxSha256,
  governingContractId: oldShippingSpec.governingContractId,
  governingContractSha256: oldShippingSpec.governingContractSha256,
  shippingPrefabPath: `${projectRoot}/Assets/Resources/Gacha/PremiumDisplayCaseGate12R003/PresentationRoot.prefab`,
  shippingScenePath: `${projectRoot}/Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R003.unity`,
  profilePath: `${projectRoot}/Assets/Resources/Gacha/PremiumDisplayCaseGate12R003Profile.asset`,
  parameterSnapshot: timing,
  timingChangedFromRev2: false,
  visibilityRepair: timing.visibilityRepairCandidate,
  packTear: {
    realBodyAndFlapAssets: true,
    tearCommitProgress: 0.62,
    belowThresholdBehavior: "continuous-follow-then-rebound",
    commitBehavior: "same-request-exact-once",
    foregroundUntilAuthoritativeReceiptAndTwoFrameReady: true,
    noEmptyFrame: true
  },
  profileValuesLocked: false,
  pendingVisualTuning: true,
  phaseOrder: [
    "sealed-pack",
    "partial-tear-and-rebound",
    "committed-tear-and-seam-light",
    "same-request-receipt-and-two-frame-ready",
    "pack-case-handoff",
    "entry-arrival-rim-first-spin-bounded-overlap",
    "fast-first-local-y-360-with-object-rim",
    "continuous-spin-boundary",
    "slower-second-local-y-360-with-object-rim",
    "one-finite-mesh-clipped-sheen",
    "static-hold-and-result-ui"
  ],
  localYRotationDegrees: 720,
  firstSpinDegrees: 360,
  secondSpinDegrees: 360,
  noStopBetweenSpins: true,
  effectRendererCount: 3,
  finiteLightCueCount: 4,
  sheenActivationCount: 1,
  outsideMeshSheenPixels: 0,
  pointLightCount: 0,
  particleEmitterCount: 0,
  wholeAssembledCaseOnly: true,
  sameInstanceThroughAcknowledgement: true,
  externalEntityCount: 0,
  externalModelCount: 0,
  externalPrefabCount: 0,
  toyPrizeOwnership: "caller-owned",
  toyIndependentAngularVelocity: 0,
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
  completeRecordingArtifactId: `${modelId}-shipping-video-r003`,
  approvalChecklist,
  interactionMode: "complete-canonical-app-simulator-recording-plus-pack-and-light-closeups",
  gate12Status: "ready_for_review"
};

manifest.model.status = "shipping-visual-revision-pending";
manifest.currentState.visualApproval = "gate12-rev3-real-app-review-pending";
manifest.currentState.deviceStatus = "simulator-preview-only-physical-phone-untouched";
manifest.currentState.shippingAssetUnchanged = false;
manifest.currentState.affectedGateAssessment = {
  earliestAffectedGate: "12-shipping-implementation-defect",
  reason: "Rev 3 repairs missing visible effect wiring and the Pack tear visual without changing approved upstream contracts.",
  geometryMaterialLightingEnvironmentExportUnityParityInvalidated: false,
  upstreamApprovedGatesUnchanged: shipping.shippingSpec.upstreamApprovedGatesUnchanged
};
manifest.currentState.shippingPreview = {
  revision: 3,
  gate12Status: "ready_for_review",
  previousRejectedRevision: 2,
  previousRevisionDisposition: "rejected-history",
  prefabPath: shipping.shippingSpec.shippingPrefabPath,
  scenePath: shipping.shippingSpec.shippingScenePath,
  videoPath: `${evidenceRoot}/app-simulator-pack-to-case-r3.mp4`,
  videoSha256: records.find(
    (record) => record.id === `${modelId}-shipping-video-r003`
  ).sha256,
  contactSheetPath: `${evidenceRoot}/app-simulator-contact-sheet.png`,
  packContactSheetPath: `${evidenceRoot}/pack-tear-contact-sheet.png`,
  lightContactSheetPath: `${evidenceRoot}/light-closeup-contact-sheet.png`,
  profileValuesLocked: false,
  pendingVisualTuning: true,
  simulatorInstalledLaunched: true,
  physicalPhoneInstalled: false,
  deviceAccepted: false,
  visualApproved: false
};
manifest.currentState.motionCorrection = {
  ...manifest.currentState.motionCorrection,
  gate12Status: "ready_for_review-rev3",
  shippingPreviewApproved: false,
  shippingDurationApproved: false,
  finiteLightCueCount: 4,
  caseLightOutsideSilhouettePixels: 0
};
manifest.currentState.diagnosis = "Gate 12 rev 2 remains rejected immutable history. Rev 3 fixes two shipping defects: transparent-shader attenuation plus incomplete material/renderer wiring made approved light cues visually absent, and a 400x512 flap canvas was incorrectly scaled into a 238x82 frame with no readable opening/seam. Rev 3 preserves all rev 2 timing, Gates 01–11, one assembled real case, authoritative labels, same-request readiness, zero toy spin, Reduce Motion and interruption rules. The canonical Release App Simulator preview passes 53/53 Unity and 37/37 Swift checks. Visual approval is pending; no physical iPhone was used.";

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256
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
  shippingRevision: 3,
  defectClass: "shipping-implementation-regression",
  exactUserFeedback: exactFeedback,
  preservedRejectedShippingRevision: 2,
  upstreamApprovedGatesUnchanged: shipping.shippingSpec.upstreamApprovedGatesUnchanged,
  parameterSnapshot: timing,
  visibilityRepair: timing.visibilityRepairCandidate,
  sourceRepository: source.repository,
  sourceCommit: source.actualCommit,
  extractedModuleFiles: source.moduleFiles,
  excludedAssets: source.excludedAssets,
  reviewArtifactIds,
  videoPath: `${evidenceRoot}/app-simulator-pack-to-case-r3.mp4`,
  videoSha256: manifest.currentState.shippingPreview.videoSha256,
  contactSheetPath: `${evidenceRoot}/app-simulator-contact-sheet.png`,
  packContactSheetPath: `${evidenceRoot}/pack-tear-contact-sheet.png`,
  lightContactSheetPath: `${evidenceRoot}/light-closeup-contact-sheet.png`,
  approvalChecklist,
  rotationDegrees: 720,
  profileDurationSeconds: timing.profileDurationSeconds,
  timingChangedFromRev2: false,
  noEmptyFrame: true,
  outsideMeshEffectPixels: 0,
  focusedUnityTests: "53/53",
  swiftGateHarness: "37/37",
  swiftWarningsAsErrors: "pass",
  xcodeBuild: "Release Simulator BUILD SUCCEEDED",
  simulatorInstalledLaunched: true,
  physicalPhoneInstalled: false,
  deviceAccepted: false,
  autoApproved: false,
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
