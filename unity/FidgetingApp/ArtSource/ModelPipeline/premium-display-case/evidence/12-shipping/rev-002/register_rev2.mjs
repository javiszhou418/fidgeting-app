import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  digestValues,
  loadManifest,
  normalizeRepoPath,
  repoRoot,
  resolveRepoPath,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "premium-display-case";
const expectedRevision = Number(process.argv[2]);
const userQuote = "节奏有点慢，就是转的两圈的速度可以：第一圈快一点，第二圈慢一点；整体的动画时间可以减短一点。然后从拆包到这个卡出来，我觉得有一点拖沓。上次让你做的 GitHub 上面有很多现成的抽卡动效、调研，你可以直接在 Unity 里面去复制的。我想你能不能把那些文件里面的素材拆分一下？我想只用它的转场和光效，我不想用它的实体。 比如说，我们上次用过一个三张卡并列的那个，但是我不想用它的三张卡，我只有一张卡，而且我这个卡本身已经有设计了。";
const projectRoot = "unity/FidgetingApp";
const evidenceRoot = `${projectRoot}/ArtSource/ModelPipeline/${modelId}/evidence/12-shipping/rev-002`;
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

const architecture = manifest.stages[3];
const parity = manifest.stages[10];
const shipping = manifest.stages[11];
if (
  architecture.status !== "approved"
  || parity.status !== "approved"
  || shipping.status !== "approved"
  || shipping.shippingSpec?.revision !== 1
  || shipping.shippingSpec?.approval?.visualApproved !== true
) {
  throw new Error("Approved Gate 04, Gate 11 and Gate 12 rev 1 are required.");
}

const evidence = readJson(`${evidenceRoot}/gate12-evidence-report.json`);
const source = readJson(`${evidenceRoot}/source-extraction-report.json`);
const capture = readJson(`${evidenceRoot}/shipping-capture-report.json`);
const native = readJson(`${evidenceRoot}/native-validation-report.json`);
const xcode = readJson(`${evidenceRoot}/xcode-build-summary.json`);
const build = readJson(`${evidenceRoot}/simulator-build-manifest.json`);
const timing = readJson(`${evidenceRoot}/timing-candidate-report.json`);
const validEvidence = (
  evidence.status === "pass"
  && Object.values(evidence.checks || {}).every(Boolean)
  && source.status === "pass"
  && source.expectedCommit === "88842be0063b5b0b75e82ed6572752a37a13c82b"
  && source.actualCommit === source.expectedCommit
  && source.forbiddenImports.length === 0
  && source.shippingBoundaries.externalModelsImported === false
  && source.shippingBoundaries.externalPrefabsImported === false
  && source.shippingBoundaries.particlesEnabled === false
  && capture.profileDurationSeconds === 3.6
  && capture.rotationDegrees === 720
  && native.status === "pass"
  && native.swiftGateHarness.passed === 25
  && native.swiftWarningsAsErrors.result === "pass"
  && xcode.status === "pass"
  && build.bundleIdentifier === "com.jiaweizhou.fidgetspinner.codex"
  && build.sdk === "SimulatorSDK"
  && build.development === false
  && build.gate11DisplayCaseFbxSha256
    === "21c9db68723f0006d7c6bfec5280cafe55c16cf5392ff97c365c966e91f847ae"
  && timing.handoffDurationSeconds === 0.18
  && timing.entryDurationSeconds === 0.82
  && timing.firstSpinDurationSeconds === 0.72
  && timing.secondSpinDurationSeconds === 1.18
  && timing.entryRotationOverlapSeconds === 0.22
  && timing.profileDurationSeconds === 3.6
  && timing.totalRotationDegrees === 720
  && timing.firstSpinAverageDegreesPerSecond
    > timing.secondSpinAverageDegreesPerSecond
  && evidence.video.durationSeconds === 5
  && evidence.video.fps === 60
  && evidence.video.noEmptyFrame === true
  && evidence.unityTests.passed === 49
  && evidence.unityTests.failed === 0
  && evidence.physicalPhoneInstalled === false
);
if (!validEvidence) {
  throw new Error("Gate 12 rev 2 evidence does not pass its source contract.");
}

const oldShippingSpec = structuredClone(shipping.shippingSpec);
const oldDecision = structuredClone(shipping.decision);
const oldArtifactIds = [...shipping.artifactIds];
const userRequestId = `${modelId}-motion-revision-request-r002`;
const sourceClaimId = `${modelId}-motion-revision-claim-r002`;
const definitions = [
  [userRequestId, "04-architecture", "architecture-user-decision", `${evidenceRoot}/user-motion-revision-request.md`, "user-input", "explicit-user-motion-revision"],
  [`${modelId}-shipping-builder-r002`, "12-shipping", "shipping-builder", `${projectRoot}/Assets/_DisplayCase/Editor/PremiumDisplayCaseGate12Builder.cs`, "process", "rev2-canonical-unity-builder"],
  [`${modelId}-shipping-profile-source-r002`, "12-shipping", "shipping-profile-source", `${projectRoot}/Assets/_DisplayCase/Runtime/PremiumDisplayCaseRevealProfile.cs`, "process", "two-spin-tunable-profile-source"],
  [`${modelId}-shipping-presentation-source-r002`, "12-shipping", "shipping-presentation-source", `${projectRoot}/Assets/_DisplayCase/Runtime/PremiumDisplayCaseShippingPresentation.cs`, "process", "same-instance-material-property-block-runtime"],
  [`${modelId}-shipping-factory-source-r002`, "12-shipping", "shipping-factory-source", `${projectRoot}/Assets/_DisplayCase/Runtime/PremiumDisplayCaseShippingFactory.cs`, "process", "rev2-resources-factory"],
  [`${modelId}-shipping-director-source-r002`, "12-shipping", "shipping-director-source", `${projectRoot}/Assets/Scripts/Product/Gacha/GachaShippingRevealDirector.cs`, "process", "authoritative-unity-reveal-director"],
  [`${modelId}-shipping-bridge-source-r002`, "12-shipping", "shipping-bridge-source", `${projectRoot}/Assets/Scripts/Product/Gacha/GachaPresentationNativeBridge.cs`, "process", "scriptableobject-handoff-duration-bridge"],
  [`${modelId}-shipping-coordinator-source-r002`, "12-shipping", "shipping-coordinator-source", `${projectRoot}/Assets/Scripts/Product/FidgetAppCoordinator.cs`, "process", "receipt-two-frame-ready-and-native-start-handshake"],
  [`${modelId}-shipping-native-store-source-r002`, "12-shipping", "shipping-native-source", `${projectRoot}/Assets/Plugins/iOS/FidgetGachaStore.swift`, "process", "same-request-unity-start-bridge"],
  [`${modelId}-shipping-native-view-source-r002`, "12-shipping", "shipping-native-source", `${projectRoot}/Assets/Plugins/iOS/FidgetGachaShippingStorefront.swift`, "process", "pack-retreat-and-real-case-handoff"],
  [`${modelId}-shipping-native-gate-source-r002`, "12-shipping", "shipping-native-source", `${projectRoot}/Assets/Plugins/iOS/FidgetGachaRiveGateRules.swift`, "process", "exact-once-reveal-start-gate"],
  [`${modelId}-shipping-sheen-shader-r002`, "12-shipping", "shipping-shader", `${projectRoot}/Assets/_DisplayCase/Shaders/PremiumDisplayCaseGate12R002Frosted.shader`, "process", "object-local-mesh-clipped-reveal-and-sheen"],
  [`${modelId}-cc0-source-contract-r002`, "12-shipping", "source-contract", `${moduleRoot}/SOURCE_CONTRACT.json`, "process", "pinned-cc0-source-allowlist-and-exclusions"],
  [`${modelId}-cc0-notice-r002`, "12-shipping", "license-provenance", `${moduleRoot}/CC0-NOTICE.md`, "process", "cc0-source-commit-and-license-notice"],
  [`${modelId}-cc0-curve-source-r002`, "12-shipping", "effect-source", `${moduleRoot}/MakeItShineCc0EffectCurves.cs`, "process", "booster-discard-dissolve-curve-only"],
  [`${modelId}-cc0-mask-source-r002`, "12-shipping", "effect-source", `${moduleRoot}/MakeItShineCc0Masks.hlsl`, "process", "sphere-mask-and-reveal-math-only"],
  [`${modelId}-shipping-prefab-r002`, "12-shipping", "shipping-prefab", `${projectRoot}/Assets/Resources/Gacha/PremiumDisplayCaseGate12R002/PresentationRoot.prefab`, "source-model", "canonical-app-whole-case-rev2-prefab"],
  [`${modelId}-shipping-profile-r002`, "12-shipping", "shipping-profile", `${projectRoot}/Assets/Resources/Gacha/PremiumDisplayCaseGate12R002Profile.asset`, "source-model", "pending-visual-tuning-profile"],
  [`${modelId}-shipping-scene-r002`, "12-shipping", "shipping-scene", `${projectRoot}/Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R002.unity`, "source-model", "canonical-unity-rev2-review-scene"],
  [`${modelId}-shipping-library-r002`, "12-shipping", "shipping-library", `${evidenceRoot}/library.png`, "unity-render", "real-app-final-hold"],
  [`${modelId}-shipping-hero-r002`, "12-shipping", "shipping-hero", `${evidenceRoot}/hero.png`, "unity-render", "real-unity-hero"],
  [`${modelId}-shipping-top-r002`, "12-shipping", "shipping-top", `${evidenceRoot}/top.png`, "unity-render", "real-unity-top"],
  [`${modelId}-shipping-left-oblique-r002`, "12-shipping", "shipping-left-oblique", `${evidenceRoot}/left-oblique.png`, "unity-render", "real-unity-left-oblique"],
  [`${modelId}-shipping-right-oblique-r002`, "12-shipping", "shipping-right-oblique", `${evidenceRoot}/right-oblique.png`, "unity-render", "real-unity-right-oblique"],
  [`${modelId}-shipping-low-r002`, "12-shipping", "shipping-low", `${evidenceRoot}/low.png`, "unity-render", "real-unity-low"],
  [`${modelId}-shipping-phone-r002`, "12-shipping", "shipping-phone", `${evidenceRoot}/simulator-final.png`, "unity-render", "real-canonical-app-final-hold"],
  [`${modelId}-shipping-video-r002`, "12-shipping", "shipping-recording", `${evidenceRoot}/app-simulator-pack-to-case-r2.mp4`, "unity-render", "pack-one-case-fast-first-slow-second-sheen-hold"],
  [`${modelId}-shipping-contact-r002`, "12-shipping", "shipping-contact-sheet", `${evidenceRoot}/app-simulator-contact-sheet.png`, "process", "five-second-reveal-contact-sheet"],
  [`${modelId}-shipping-handoff-contact-r002`, "12-shipping", "shipping-handoff-contact-sheet", `${evidenceRoot}/app-simulator-handoff-contact-sheet.png`, "validation", "ready-gated-no-empty-frame-handoff"],
  [`${modelId}-shipping-standard-contact-r002`, "12-shipping", "shipping-contact-sheet", `${evidenceRoot}/standard-views-contact-sheet.png`, "process", "real-unity-standard-views"],
  [`${modelId}-shipping-capture-report-r002`, "12-shipping", "shipping-report", `${evidenceRoot}/shipping-capture-report.json`, "validation", "profile-and-camera-report"],
  [`${modelId}-shipping-timing-report-r002`, "12-shipping", "timing-report", `${evidenceRoot}/timing-candidate-report.json`, "validation", "exact-pending-timing-snapshot"],
  [`${modelId}-shipping-source-report-r002`, "12-shipping", "source-report", `${evidenceRoot}/source-extraction-report.json`, "validation", "cc0-source-hash-and-exclusion-verdict"],
  [`${modelId}-shipping-evidence-report-r002`, "12-shipping", "shipping-report", `${evidenceRoot}/gate12-evidence-report.json`, "validation", "independent-rev2-evidence-verdict"],
  [`${modelId}-shipping-evidence-builder-r002`, "12-shipping", "shipping-validator", `${evidenceRoot}/build_rev2_evidence.py`, "process", "rev2-video-contact-and-contract-validator"],
  [`${modelId}-shipping-unity-tests-r002`, "12-shipping", "shipping-test-results", `${evidenceRoot}/unity-focused-results.xml`, "validation", "focused-editmode-results"],
  [`${modelId}-shipping-native-validation-r002`, "12-shipping", "shipping-test-results", `${evidenceRoot}/native-validation-report.json`, "validation", "swift-gate-typecheck-and-xcode-validation"],
  [`${modelId}-shipping-build-manifest-r002`, "12-shipping", "shipping-build-manifest", `${evidenceRoot}/simulator-build-manifest.json`, "validation", "canonical-bundle-and-source-hashes"],
  [`${modelId}-shipping-xcode-summary-r002`, "12-shipping", "shipping-build-report", `${evidenceRoot}/xcode-build-summary.json`, "validation", "release-simulator-build-summary"],
  [`${modelId}-shipping-registration-r002`, "12-shipping", "shipping-registration", `${evidenceRoot}/register_rev2.mjs`, "process", "atomic-revision-registration"]
];

for (const [, , , assetPath] of definitions) {
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

const oldVideoId = oldShippingSpec.completeRecordingArtifactId;
const sourceFbxId = oldShippingSpec.sourceFbxArtifactId;
const contractId = oldShippingSpec.governingContractId;
const records = definitions.map(
  ([id, stageId, slot, assetPath, role, contentClass]) => {
    const absolute = resolveRepoPath(assetPath);
    const userInput = id === userRequestId;
    return {
      id,
      stageId,
      slot,
      path: normalizeRepoPath(assetPath),
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role,
      sourceAssetIds: userInput
        ? [oldVideoId]
        : [userRequestId, sourceFbxId, contractId],
      sourceClaimIds: userInput
        ? []
        : [
            ...(manifest.claims || [])
              .filter((claim) => (
                claim.stageId === "02-analysis"
                && claim.state !== "superseded"
              ))
              .map((claim) => claim.id),
            sourceClaimId
          ],
      producer: {
        name: assetPath.includes("/Assets/")
          ? "Unity"
          : "fidgeting-model-pipeline",
        version: assetPath.includes("/Assets/")
          ? "6000.5.6f1"
          : "2026-08-27",
        recipe: contentClass
      },
      provenance: {
        origin: userInput ? "user-provided" : "repository-generated",
        contentClass,
        assertedBy: userInput ? "user" : "assistant",
        note: userInput
          ? "Exact chat instruction preserved. It authorizes the two-spin architecture but not the pending shipping visual."
          : "Gate 12 rev 2 candidate evidence. Visual approval and physical phone acceptance remain pending."
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
manifest.claims.push({
  id: sourceClaimId,
  stageId: "04-architecture",
  topic: "two-speed-continuous-showcase",
  statement: "用户要求同一 assembled 真盒连续旋转两圈共 720°：第一圈更快、第二圈更慢、圈间不停；缩短 ready 后 handoff、整体时长，并仅复用 CC0 转场与光效数学，不复用三卡或任何外部实体。",
  confidence: "user-authoritative",
  state: "active",
  assertedBy: "user",
  sourceAssetIds: [userRequestId],
  sourceRegions: [],
  sourceTask: "c364585a-9827-4c3d-8f7d-ceeef115a9ea",
  decisionState: "locked-motion-structure",
  deliveryState: "gate12-rev2-ready-for-visual-review"
});

for (const assetId of oldArtifactIds) {
  const asset = manifest.assets.find((candidate) => candidate.id === assetId);
  if (!asset) continue;
  asset.reviewState = "superseded-history";
  asset.preservedForHistory = true;
  asset.supersededByShippingRevision = 2;
  asset.dispositionNote = "Gate 12 rev 1 remains approved historical evidence. The user requested a new timing, two-spin and CC0 effect-math revision.";
}

architecture.historicalRevisions = [
  ...(architecture.historicalRevisions || []),
  {
    revision: architecture.architectureSpec.revision,
    evidenceRevision: architecture.architectureSpec.evidenceRevision,
    showcase: architecture.architectureSpec.showcase,
    approval: structuredClone(architecture.architectureSpec.approval),
    disposition: "approved-history-superseded-by-explicit-two-spin-request"
  }
];
architecture.architectureSpec = {
  ...architecture.architectureSpec,
  revision: 3,
  presentationMotionRevision: 2,
  earliestAffectedGate: "04-architecture",
  sourceUserRequestArtifactId: userRequestId,
  sourceUserRequestQuote: userQuote,
  showcase: "two-continuous-local-y-360-turns-first-faster-second-slower",
  showcaseDegrees: 720,
  showcaseCount: 2,
  firstSpinDegrees: 360,
  secondSpinDegrees: 360,
  noStopBetweenSpins: true,
  entryRotationOverlapSeconds: 0.22,
  overlapTimingApproved: false,
  shippingDurationApproved: false,
  tunableRuntimeParameterCount: 22,
  externalEffectExtraction: {
    sourceRepository: source.repository,
    sourceCommit: source.actualCommit,
    importedEntityCount: 0,
    importedModelCount: 0,
    importedPrefabCount: 0,
    particleEmitterCount: 0,
    moduleFiles: source.moduleFiles
  },
  revisionInstruction: {
    decisionState: "explicit-user-directed-motion-structure",
    userQuote,
    visualTuningApproved: false,
    gate12Status: "ready_for_review"
  }
};

for (const stage of manifest.stages.slice(4, 11)) {
  stage.presentationRevisionAssessment = {
    revision: 2,
    status: "not-affected-revalidated",
    geometryChanged: false,
    materialChanged: false,
    lightingRigChanged: false,
    environmentChanged: false,
    exportChanged: false,
    unityImportChanged: false,
    reason: "The user changed runtime presentation timing, spin profile and mesh-clipped effect math only."
  };
}

const reviewArtifactIds = [
  `${modelId}-shipping-video-r002`,
  `${modelId}-shipping-contact-r002`,
  `${modelId}-shipping-handoff-contact-r002`,
  `${modelId}-shipping-standard-contact-r002`,
  `${modelId}-shipping-library-r002`,
  `${modelId}-shipping-hero-r002`,
  `${modelId}-shipping-top-r002`,
  `${modelId}-shipping-left-oblique-r002`,
  `${modelId}-shipping-right-oblique-r002`,
  `${modelId}-shipping-low-r002`,
  `${modelId}-shipping-phone-r002`
];
const approvalChecklist = [
  "watch-complete-pack-to-one-real-case-recording",
  "confirm-ready-gated-handoff-is-not-draggy",
  "confirm-first-360-is-faster-than-second-360",
  "confirm-no-stop-at-360-degree-boundary",
  "confirm-total-profile-is-shorter-than-rev1",
  "confirm-entry-overlap-remains-bounded",
  "confirm-reveal-and-sheen-stay-inside-case-silhouette",
  "confirm-one-assembled-same-instance-case-and-zero-toy-spin",
  "confirm-no-three-card-layout-external-entity-particle-or-rarity-flash",
  "confirm-static-camera-background-label-and-final-hold",
  "confirm-no-physical-phone-was-installed"
];
shipping.historicalDecisions = [
  ...(shipping.historicalDecisions || []),
  {
    ...oldDecision,
    shippingRevision: 1,
    disposition: "historically-approved-then-superseded-by-user-request"
  }
];
shipping.historicalRevisions = [
  ...(shipping.historicalRevisions || []),
  {
    shippingSpec: oldShippingSpec,
    artifactIds: oldArtifactIds,
    reviewArtifactIds: [...shipping.reviewArtifactIds],
    decision: oldDecision,
    preservedForHistory: true
  }
];
shipping.revision += 1;
shipping.status = "ready_for_review";
shipping.artifactIds = records
  .filter((record) => record.stageId === "12-shipping")
  .map((record) => record.id);
shipping.reviewArtifactIds = reviewArtifactIds;
shipping.validations = [
  { id: "targeted-invalidation", status: "pass", evidence: "Earliest affected gate is Gate 04 presentation architecture. Gates 05–11 remain approved because geometry, materials, light rig, environment, export and Unity parity are unchanged." },
  { id: "rev1-history", status: "pass", evidence: "Gate 12 rev 1 approval, artifacts, parameter snapshot and approval quote remain preserved as superseded history." },
  { id: "transaction-readiness", status: "pass", evidence: "The durable receipt and two stable end-of-frame checks complete before Swift unlocks the Pack handoff. Swift then starts the same-request Unity reveal exactly once." },
  { id: "two-spin-profile", status: "pass", evidence: "The tunable profile rotates 360 degrees in 0.72 s, then 360 degrees in 1.18 s. Boundary angular velocity remains positive and continuous." },
  { id: "shorter-profile", status: "pass", evidence: "The rev 2 profile is 3.60 s versus rev 1's 4.60 s. Ready handoff is 0.18 s versus 0.28 s." },
  { id: "cc0-source-contract", status: "pass", evidence: "Only the audited dissolve curve plus rebuilt Sphere Mask and _Reveal math are present. No FBX, prefab, card, Pack, Timeline, material, artwork, VFX Graph or particle was imported." },
  { id: "mesh-clipped-effects", status: "pass", evidence: "MaterialPropertyBlock drives object-local reveal and sheen masks. Outside-mesh effect pixels, Point Lights, full-screen flashes and persistent loops are zero." },
  { id: "same-instance-whole-case", status: "pass", evidence: "One assembled real case and caller-owned real toy remain the same instance. Toy independent angular velocity is zero." },
  { id: "focused-tests", status: "pass", evidence: "Relevant Unity EditMode tests pass 49/49. Swift gate harness passes 25/25 and shipping Swift warnings-as-errors typecheck passes." },
  { id: "real-app-preview", status: "pass", evidence: "The canonical Release App Simulator review video is 5.0 s, 1206 x 2622, 60 FPS and has no empty frame." },
  { id: "device-boundary", status: "pass", evidence: "The app was installed only on iPhone 17 Pro Simulator. Physical phone install and device acceptance remain false." }
];
shipping.decision = null;
delete shipping.staleReason;
shipping.shippingSpec = {
  revision: 2,
  previousApprovedRevision: 1,
  previousApprovalEventId: oldShippingSpec.approval.approvalEventId,
  previousApprovalQuote: oldShippingSpec.approval.userApprovalQuote,
  previousRevisionDisposition: "approved-historical-evidence-superseded",
  earliestAffectedGate: "04-architecture",
  unaffectedApprovedGates: [
    "05-blockout",
    "06-geometry",
    "07-material",
    "08-lighting",
    "09-environment",
    "10-export",
    "11-unity-parity"
  ],
  sourceGate11ApprovalEventId: oldShippingSpec.sourceGate11ApprovalEventId,
  sourceFbxArtifactId: oldShippingSpec.sourceFbxArtifactId,
  sourceFbxSha256: oldShippingSpec.sourceFbxSha256,
  governingContractId: oldShippingSpec.governingContractId,
  governingContractSha256: oldShippingSpec.governingContractSha256,
  shippingPrefabPath: `${projectRoot}/Assets/Resources/Gacha/PremiumDisplayCaseGate12R002/PresentationRoot.prefab`,
  shippingScenePath: `${projectRoot}/Assets/_DisplayCase/Scenes/PremiumDisplayCaseGate12R002.unity`,
  profilePath: `${projectRoot}/Assets/Resources/Gacha/PremiumDisplayCaseGate12R002Profile.asset`,
  parameterSnapshot: timing,
  profileValuesLocked: false,
  pendingVisualTuning: true,
  phaseOrder: [
    "receipt-and-two-frame-ready",
    "pack-case-handoff",
    "entry-first-spin-bounded-overlap",
    "fast-first-local-y-360",
    "continuous-spin-boundary",
    "slower-second-local-y-360",
    "one-finite-mesh-clipped-sheen",
    "static-hold"
  ],
  localYRotationDegrees: 720,
  firstSpinDegrees: 360,
  secondSpinDegrees: 360,
  noStopBetweenSpins: true,
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
    excludedAssets: source.excludedAssets
  },
  simulatorBundleIdentifier: build.bundleIdentifier,
  simulatorInstalledLaunched: true,
  physicalPhoneInstalled: false,
  deviceAccepted: false,
  completeRecordingArtifactId: `${modelId}-shipping-video-r002`,
  approvalChecklist,
  interactionMode: "complete-canonical-app-simulator-recording-plus-standard-views",
  gate12Status: "ready_for_review"
};

manifest.model.status = "shipping-visual-revision-pending";
manifest.currentState.visualApproval = "gate12-rev2-real-app-review-pending";
manifest.currentState.deviceStatus =
  "simulator-preview-only-physical-phone-untouched";
manifest.currentState.shippingAssetUnchanged = false;
manifest.currentState.affectedGateAssessment = {
  earliestAffectedGate: "04-architecture",
  reason: "The requested two-spin motion changes presentation architecture, not geometry.",
  geometryMaterialExportUnityParityInvalidated: false,
  unaffectedApprovedGates: shipping.shippingSpec.unaffectedApprovedGates
};
manifest.currentState.shippingPreview = {
  revision: 2,
  gate12Status: "ready_for_review",
  previousApprovedRevision: 1,
  previousRevisionDisposition: "superseded-history",
  prefabPath: shipping.shippingSpec.shippingPrefabPath,
  scenePath: shipping.shippingSpec.shippingScenePath,
  videoPath: `${evidenceRoot}/app-simulator-pack-to-case-r2.mp4`,
  videoSha256: records.find(
    (record) => record.id === `${modelId}-shipping-video-r002`
  ).sha256,
  contactSheetPath: `${evidenceRoot}/app-simulator-contact-sheet.png`,
  profileValuesLocked: false,
  pendingVisualTuning: true,
  simulatorInstalledLaunched: true,
  physicalPhoneInstalled: false,
  deviceAccepted: false,
  visualApproved: false
};
manifest.currentState.diagnosis = "Gate 12 rev 1 remains approved superseded history. The user explicitly changed Gate 04 presentation architecture to two continuous local-Y turns while preserving Gates 05–11 geometry, materials, lighting, environment, export and Unity parity. Gate 12 rev 2 uses one real assembled case, a 0.18 s ready handoff, 0.82 s entry, 0.72 s first turn, 1.18 s second turn, 0.22 s bounded entry overlap, one mesh-clipped sheen and a 3.60 s profile. The canonical Release App Simulator preview is ready for review. No physical phone was installed.";

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
  shippingRevision: 2,
  earliestAffectedGate: "04-architecture",
  userRevisionRequestQuote: userQuote,
  preservedPreviousApprovalEventId:
    oldShippingSpec.approval.approvalEventId,
  preservedPreviousApprovalQuote:
    oldShippingSpec.approval.userApprovalQuote,
  unaffectedApprovedGates: shipping.shippingSpec.unaffectedApprovedGates,
  parameterSnapshot: timing,
  sourceRepository: source.repository,
  sourceCommit: source.actualCommit,
  extractedModuleFiles: source.moduleFiles,
  excludedAssets: source.excludedAssets,
  reviewArtifactIds,
  videoPath: `${evidenceRoot}/app-simulator-pack-to-case-r2.mp4`,
  videoSha256: manifest.currentState.shippingPreview.videoSha256,
  contactSheetPath: `${evidenceRoot}/app-simulator-contact-sheet.png`,
  approvalChecklist,
  rotationDegrees: 720,
  firstSpinAverageDegreesPerSecond:
    timing.firstSpinAverageDegreesPerSecond,
  secondSpinAverageDegreesPerSecond:
    timing.secondSpinAverageDegreesPerSecond,
  profileDurationSeconds: timing.profileDurationSeconds,
  previousProfileDurationSeconds:
    timing.previousApprovedProfileDurationSeconds,
  noEmptyFrame: true,
  focusedUnityTests: "49/49",
  swiftGateHarness: "25/25",
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
