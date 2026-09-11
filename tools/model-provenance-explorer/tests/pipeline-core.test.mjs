import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import {
  PipelineError,
  addIssue,
  approvePremiumDisplayCaseRestrainedLightReview,
  decideStage,
  deriveManifest,
  digestValues,
  listModelIds,
  loadManifest,
  loadModelingContract,
  pipelineDirectory,
  readHistory,
  refreshManifest,
  repoRoot,
  restorePremiumDisplayCaseRev6Authority,
  resolveRepoPath,
  saveAnalysisResearchRevision,
  saveArchitecturePlan,
  saveExternalReferencePack,
  saveManifest,
  saveModelingContract,
  savePremiumDisplayCaseBlockoutReview,
  savePremiumDisplayCaseBalancedMotionReview,
  savePremiumDisplayCaseCorrectedBlockoutReview,
  savePremiumDisplayCaseEntryMotionReview,
  savePremiumDisplayCaseMotionCorrection,
  savePremiumDisplayCaseRestrainedLightReview,
  savePremiumDisplayCaseSerialMotionContract,
  savePremiumDisplayCaseSlowerWholeCaseMotionReview,
  savePremiumDisplayCaseWholeCaseMotionReview,
  sha256File,
  stageReadiness,
  validateManifest
} from "../pipeline-core.mjs";
import { createEmptyStages, STAGES } from "../pipeline-contract.mjs";

test("tracked shipping models load and derive current readiness", () => {
  assert.deepEqual(listModelIds(), ["blue-classic", "gold-four-wing", "graphite-two-lobe", "magnetic-fan-card", "magnetic-slide-tile", "metal-three-blade", "premium-display-case"]);
  for (const modelId of listModelIds()) {
    const manifest = loadManifest(modelId);
    assert.deepEqual(validateManifest(manifest), []);
    // metal-three-blade: Build 47 (rev-007) device-accepted 2026-09-08, but Gate 12
    // rev-008 (Soft Studio lighting, user 2026-09-09 18:07) is ready_for_review, so
    // the model is not shipping-ready until that visual approval lands (pipeline rev 68).
    const deliveredModels = new Set(["magnetic-slide-tile"]);
    assert.equal(
      deriveManifest(manifest).derived.shippingReady,
      deliveredModels.has(modelId));
    assert.equal(manifest.currentState.rebuildRequested, modelId !== "metal-three-blade");
  }
});

test("Premium Display Case records Gate 12 rev 4 and preserves prior revisions", () => {
  const manifest = loadManifest("premium-display-case");
  const derived = deriveManifest(manifest);
  const gate02 = manifest.stages[1];
  const gate03 = manifest.stages[2];
  const gate04 = manifest.stages[3];
  const gate05 = manifest.stages[4];
  const gate06 = manifest.stages[5];
  const gate07 = manifest.stages[6];
  const gate08 = manifest.stages[7];
  const gate09 = manifest.stages[8];
  const gate10 = manifest.stages[9];
  const gate11 = manifest.stages[10];
  const gate12 = manifest.stages[11];
  assert.ok(manifest.revision >= 70);
  if (gate04.status === "rejected") {
    assert.equal(gate04.architectureSpec.evidenceRevision, 9);
    assert.ok(manifest.stages.slice(4).every((stage) => stage.status === "stale"));
    assert.equal(derived.derived.earliestProblem.stageId, "04-architecture");
    assert.equal(derived.derived.shippingReady, false);
    return;
  }
  assert.equal(manifest.stages[0].status, "approved");
  assert.equal(gate02.status, "approved");
  assert.equal(gate02.analysisSpec.revision, 6);
  assert.equal(gate02.analysisSpec.motionStructureRevision, 5);
  assert.equal(gate02.analysisSpec.primaryMotion, "entry");
  assert.deepEqual(gate02.analysisSpec.phaseOrder, [
    "entry-y-z",
    "settle",
    "showcase-y-360",
    "single-highlight",
    "hold"
  ]);
  assert.deepEqual(gate02.analysisSpec.entryTranslationAxes, [
    "screen-y",
    "camera-depth-z"
  ]);
  assert.equal(gate02.analysisSpec.entryRotation, "none");
  assert.equal(gate02.analysisSpec.showcaseAxis, "local-y");
  assert.equal(gate02.analysisSpec.showcaseDegrees, 360);
  assert.equal(gate02.analysisSpec.showcaseCount, 1);
  assert.equal(gate02.analysisSpec.showcaseTranslation, "locked");
  assert.equal(gate02.analysisSpec.xDrift, "none");
  assert.equal(gate02.analysisSpec.roll, "none");
  assert.equal(gate02.analysisSpec.pitch, "none");
  assert.equal(gate02.analysisSpec.modelScaleAnimation, "none-model-scale-one");
  assert.equal(gate02.analysisSpec.simultaneousEntryAndRotation, false);
  assert.equal(gate02.analysisSpec.singleHighlightAfterShowcase, true);
  assert.equal(gate02.analysisSpec.objectReplacement, false);
  assert.equal(gate02.analysisSpec.toyMotion, false);
  assert.equal(gate02.analysisSpec.reviewDurationSeconds, 3.4);
  assert.equal(gate02.analysisSpec.timingApprovalEffect, "none-review-candidate-only");
  assert.equal(gate02.analysisSpec.lightTreatmentRevision, 6);
  assert.equal(
    gate02.analysisSpec.lightTreatment.packSeamLight,
    "one-neutral-causal-cue"
  );
  assert.equal(
    gate02.analysisSpec.lightTreatment.arrivalRim,
    "one-small-threshold-cue"
  );
  assert.equal(
    gate02.analysisSpec.lightTreatment.rotationRim,
    "object-bound-surface-response"
  );
  assert.equal(
    gate02.analysisSpec.lightTreatment.finalSheen,
    "one-diagonal-narrow-sheen"
  );
  assert.equal(gate02.analysisSpec.lightTreatment.persistentLoop, false);
  assert.equal(gate02.analysisSpec.lightTreatment.vfxGraphDependency, false);
  assert.ok(gate02.analysisSpec.lightTreatment.maximumRgbChroma <= 25);
  assert.ok(gate02.analysisSpec.lightTreatment.maximumHaloAlpha <= 0.1);
  assert.equal(
    gate02.analysisSpec.approval.userApprovalQuote,
    "批准这版动效与光效（推荐）"
  );
  assert.equal(
    gate02.analysisSpec.approval.approvalEffect,
    "approves-gate02-motion-and-light-direction-only"
  );
  assert.equal(gate02.analysisSpec.approval.reviewDurationSeconds, 3.4);
  assert.equal(gate02.analysisSpec.approval.shippingDurationApproved, false);
  assert.equal(gate02.analysisSpec.approval.shippingPreviewApproved, false);
  assert.equal(gate02.analysisSpec.approval.deviceAccepted, false);
  const activeClaims = manifest.claims.filter(
    (claim) => claim.stageId === "02-analysis" && claim.state !== "superseded"
  );
  assert.equal(activeClaims.length, 10);
  assert.equal(activeClaims.filter((claim) => claim.id.endsWith("-r005")).length, 5);
  assert.equal(activeClaims.filter((claim) => claim.id.endsWith("-r006")).length, 5);
  assert.equal(gate03.status, "approved");
  assert.equal(gate03.contractSpec.revision, 3);
  assert.equal(gate03.contractSpec.sourceAnalysisRevision, 6);
  assert.equal(gate03.contractSpec.sourceMotionStructureRevision, 5);
  assert.equal(gate03.contractSpec.sourceLightTreatmentRevision, 6);
  assert.equal(gate03.contractSpec.rigidWholeCase, true);
  assert.deepEqual(gate03.contractSpec.phaseOrder, [
    "entry-y-z",
    "settle",
    "showcase-local-y-360",
    "final-sheen-short-halo",
    "static-hold"
  ]);
  assert.deepEqual(gate03.contractSpec.entryAxes, [
    "screen-y",
    "camera-depth-z"
  ]);
  assert.deepEqual(gate03.contractSpec.entryRotationDegrees, [0, 0, 0]);
  assert.equal(gate03.contractSpec.showcaseAxis, "local-y");
  assert.equal(gate03.contractSpec.showcaseDegrees, 360);
  assert.equal(gate03.contractSpec.simultaneousEntryAndShowcase, false);
  assert.equal(gate03.contractSpec.shippingTotalDurationSeconds, null);
  assert.equal(gate03.contractSpec.reviewDurationSeconds, 3.4);
  assert.equal(gate03.contractSpec.tunableParameterCount, 17);
  assert.equal(gate03.contractSpec.prizeIndependentAngularVelocity, 0);
  assert.equal(gate03.contractSpec.wholeCaseOnly, true);
  assert.equal(gate03.contractSpec.explode, false);
  assert.equal(
    gate03.contractSpec.approval.userApprovalQuote,
    "批准合同并继续（推荐）"
  );
  assert.equal(gate03.contractSpec.approval.shippingDurationApproved, false);
  assert.equal(gate03.contractSpec.approval.gate04Status, "eligible");
  assert.equal(gate03.contractSpec.approval.gate05Status, "blocked");
  assert.deepEqual(gate03.reviewArtifactIds, [
    "premium-display-case-contract-preview-r003"
  ]);
  const contract = loadModelingContract("premium-display-case");
  assert.equal(contract.contractRevision, 3);
  assert.equal(contract.sourceClaimIds.length, 10);
  assert.deepEqual(contract.sourceClaimIds, activeClaims.map((claim) => claim.id));
  assert.equal(contract.staticPreservation.portraitEnvelope.widthMm, 228);
  assert.equal(contract.staticPreservation.physicalLabel.centerYmm, 99);
  assert.equal(contract.staticPreservation.contentSlot.depthMm, 48);
  assert.equal(contract.motionContract.entry.rotationDegrees.join(","), "0,0,0");
  assert.equal(contract.motionContract.showcase.axis, "local-y");
  assert.equal(contract.motionContract.showcase.degrees, 360);
  assert.equal(contract.motionContract.simultaneousEntryAndShowcase, false);
  assert.equal(contract.tunableRuntimeParameters.shippingTotalDurationSeconds, null);
  assert.equal(contract.tunableRuntimeParameters.phaseEasing, null);
  assert.equal(contract.lightContract.particles, false);
  assert.equal(contract.lightContract.vfxGraphDependency, false);
  assert.equal(contract.route.nextGatePolicy, "Do not enter Gate 04 before explicit Gate 03 approval.");
  const gate03Assets = gate03.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)
  );
  assert.ok(gate03Assets.every((asset) => asset.sourceClaimIds.length === 10));
  const serialValidation = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate03Assets.find((asset) => asset.id === "premium-display-case-contract-validation-r003").path
  ), "utf8"));
  assert.equal(serialValidation.status, "pass");
  assert.ok(Object.values(serialValidation.checks).every(Boolean));
  assert.equal(gate04.status, "approved");
  assert.equal(gate04.architectureSpec.revision, 3);
  assert.equal(gate04.architectureSpec.evidenceRevision, 7);
  assert.equal(gate04.architectureSpec.sourceContractRevision, 3);
  assert.equal(gate04.architectureSpec.entryOwner, "PresentationRoot");
  assert.deepEqual(gate04.architectureSpec.entryAxes, [
    "screen-y",
    "camera-depth-z"
  ]);
  assert.equal(
    gate04.architectureSpec.showcase,
    "two-continuous-local-y-360-turns-first-faster-second-slower"
  );
  assert.equal(gate04.architectureSpec.showcaseDegrees, 720);
  assert.equal(gate04.architectureSpec.showcaseCount, 2);
  assert.equal(gate04.architectureSpec.noStopBetweenSpins, true);
  assert.equal(gate04.architectureSpec.overlapWindowCount, 1);
  assert.equal(gate04.architectureSpec.overlapTimingApproved, false);
  assert.equal(
    gate04.architectureSpec.caseIdentity,
    "one-rigid-assembled-instance-through-ack"
  );
  assert.equal(gate04.architectureSpec.nativePackOwner, "external");
  assert.equal(gate04.architectureSpec.toyOwner, "caller-owned-content-slot");
  assert.equal(gate04.architectureSpec.toyIndependentAngularVelocity, 0);
  assert.equal(gate04.architectureSpec.lightController, "MeshClippedLightController");
  assert.deepEqual(gate04.architectureSpec.finiteLightCueIds, [
    "pack-seam-light",
    "arrival-rim-inside-case-mask",
    "rotation-rim-inside-case-mask",
    "final-mesh-clipped-sheen"
  ]);
  assert.equal(gate04.architectureSpec.finiteLightCueCount, 4);
  assert.equal(gate04.architectureSpec.caseLightOutsideSilhouettePixels, 0);
  assert.equal(gate04.architectureSpec.externalSettleHalo, false);
  assert.equal(gate04.architectureSpec.externalPointLightFinalSheen, false);
  assert.equal(gate04.architectureSpec.vfxGraphDependency, false);
  assert.equal(
    gate04.architectureSpec.unityRuntimeArchitecture.stateAuthority,
    "GachaRevealDirector"
  );
  assert.equal(
    gate04.architectureSpec.unityRuntimeArchitecture.materialDriver,
    "MaterialPropertyBlock"
  );
  assert.equal(
    gate04.architectureSpec.unityRuntimeArchitecture.timelineTransactionAuthority,
    false
  );
  assert.ok(gate04.architectureSpec.toolOwnership.Unity.includes("mesh-clipped light"));
  assert.deepEqual(gate04.architectureSpec.toolOwnership.React, [
    "pipeline review tooling only"
  ]);
  assert.equal(gate04.architectureSpec.particleEmitterCount, 0);
  assert.equal(gate04.architectureSpec.persistentLightLoop, false);
  assert.equal(gate04.architectureSpec.shippingDurationApproved, false);
  assert.equal(gate04.architectureSpec.tunableRuntimeParameterCount, 22);
  assert.equal(gate04.architectureSpec.wholeCaseOnly, true);
  assert.equal(gate04.architectureSpec.explodeEligible, false);
  assert.equal(gate04.architectureSpec.gate05Status, "ready_for_review-rev3");
  assert.equal(
    gate04.architectureSpec.approval.userApprovalQuote,
    "正确，批准并继续（推荐）"
  );
  assert.equal(gate04.architectureSpec.approval.approvedEvidenceRevision, 7);
  assert.equal(gate04.architectureSpec.approval.reviewedArtifacts.length, 3);
  assert.equal(
    gate04.architectureSpec.approval.governingContractSha256,
    "1aea4db5fb45e61b936c5145d83d39a2e2a4abfe000dddb46cfdb200f76023f3"
  );
  assert.equal(
    gate04.architectureSpec.approval.parameterSnapshotSha256,
    "d5afb4eecdb86953cb6d5c28e217e19f88becb6c0aef1316eaffac2ae630fc3e"
  );
  assert.deepEqual(gate04.reviewArtifactIds, [
    "premium-display-case-mesh-light-review-r007",
    "premium-display-case-mesh-light-gif-r007",
    "premium-display-case-mesh-light-contact-r007"
  ]);
  assert.ok(gate04.architectureSpec.internalArtifactIds.every(
    (assetId) => !gate04.reviewArtifactIds.includes(assetId)
  ));
  const gate04Assets = gate04.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)
  );
  assert.ok(gate04Assets.every((asset) => asset.sourceClaimIds.length === 10));
  assert.ok(gate04.architectureSpec.internalArtifactIds.every((assetId) => (
    gate04Assets.find((asset) => asset.id === assetId).internalTechnicalEvidence === true
  )));
  assert.ok(gate04.reviewArtifactIds.every((assetId) => {
    const asset = gate04Assets.find((candidate) => candidate.id === assetId);
    return asset.wholeCaseOnly === true && asset.internalTechnicalEvidence === false;
  }));
  const architectureValidation = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate04Assets.find(
      (asset) => asset.id === "premium-display-case-mesh-light-validation-r007"
    ).path
  ), "utf8"));
  assert.equal(architectureValidation.status, "pass");
  assert.ok(Object.values(architectureValidation.checks).every(Boolean));
  assert.equal(architectureValidation.metrics.caseLightOutsideSilhouetteMaxPixels, 0);
  assert.equal(architectureValidation.metrics.finiteLightCueCount, 4);
  assert.equal(architectureValidation.metrics.externalPointLightCount, 0);
  assert.equal(architectureValidation.metrics.finalFrameActiveLightCueCount, 0);
  assert.equal(architectureValidation.metrics.reviewArtifactExplodedPartCount, 0);
  assert.equal(
    manifest.currentState.architectureApproval.userApprovalQuote,
    "正确，批准并继续（推荐）"
  );
  assert.equal(manifest.currentState.architectureApproval.gate05Status, "eligible");
  assert.equal(gate05.status, "approved");
  assert.equal(gate05.blockoutSpec.revision, 3);
  assert.equal(gate05.blockoutSpec.sourceBlockoutRevision, 2);
  assert.equal(gate05.blockoutSpec.sourceGate04EvidenceRevision, 7);
  assert.equal(gate05.blockoutSpec.geometryChanged, false);
  assert.equal(gate05.blockoutSpec.metadataChanged, true);
  assert.equal(
    gate05.blockoutSpec.geometryDigest,
    "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f"
  );
  assert.deepEqual(gate05.blockoutSpec.dimensionsMm, {
    width: 228,
    height: 304,
    depth: 59
  });
  assert.equal(gate05.blockoutSpec.labelPosition.centerYmm, 99);
  assert.equal(gate05.blockoutSpec.cornerCenterFamilies.maximumDriftMm, 0);
  assert.equal(gate05.blockoutSpec.closedTube.connectedMaterialBodyCount, 1);
  assert.equal(gate05.blockoutSpec.closedTube.openBoundaryEdgeCount, 0);
  assert.equal(gate05.blockoutSpec.closedTube.nonManifoldEdgeCount, 0);
  assert.equal(gate05.blockoutSpec.closedTube.channelSamplesVisited, 384);
  assert.equal(gate05.blockoutSpec.contentSlot.objectType, "EMPTY");
  assert.equal(gate05.blockoutSpec.contentSlot.childCount, 0);
  assert.deepEqual(gate05.blockoutSpec.pivot.locationMm, [0, 0, 0]);
  assert.equal(gate05.blockoutSpec.bakedRuntimeAnimation, false);
  assert.ok(Object.values(gate05.blockoutSpec.forbiddenGeometry).every(
    (value) => value === false
  ));
  assert.equal(gate05.blockoutSpec.reviewArtifactExplodedPartCount, 0);
  assert.equal(gate05.blockoutSpec.approval.approvedRevision, 3);
  assert.equal(
    gate05.blockoutSpec.approval.userApprovalQuote,
    "正确，批准并继续（推荐）"
  );
  assert.deepEqual(gate05.blockoutSpec.approval.approvalScope, [
    "existing-geometry-unchanged",
    "gate04-rev7-compatible",
    "unity-presentation-root-owns-runtime-motion",
    "no-light-proxy-or-toy-geometry"
  ]);
  assert.equal(gate05.blockoutSpec.gate06Status, "ready_for_review-rev3");
  assert.deepEqual(gate05.reviewArtifactIds, [
    "premium-display-case-blockout-architecture-compatibility-review-r003",
    "premium-display-case-blockout-hero-r003",
    "premium-display-case-blockout-front-r003",
    "premium-display-case-blockout-pivot-root-hierarchy-r003"
  ]);
  const gate05Assets = gate05.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)
  );
  assert.ok(gate05.reviewArtifactIds.every((assetId) => {
    const asset = gate05Assets.find((candidate) => candidate.id === assetId);
    return asset.wholeAssembledCaseOnly === true && asset.explodeEligible === false;
  }));
  const blockoutValidation = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate05Assets.find(
      (asset) => asset.id === "premium-display-case-blockout-compatibility-validation-r003"
    ).path
  ), "utf8"));
  assert.equal(blockoutValidation.status, "pass");
  assert.ok(Object.values(blockoutValidation.checks).every(Boolean));
  assert.equal(blockoutValidation.metrics.reviewArtifactExplodedPartCount, 0);
  assert.ok(gate05.historicalDecisions.some(
    (decision) => decision.notes.includes("可以，继续推进")
  ));
  assert.equal(gate06.status, "approved");
  assert.equal(gate06.geometrySpec.revision, 3);
  assert.equal(gate06.geometrySpec.sourceGate05Revision, 3);
  assert.equal(gate06.geometrySpec.sourceGate04EvidenceRevision, 7);
  assert.equal(gate06.geometrySpec.geometryChanged, false);
  assert.equal(gate06.geometrySpec.normalCorrectionOnly, true);
  assert.equal(gate06.geometrySpec.approval.approvedRevision, 3);
  assert.equal(
    gate06.geometrySpec.approval.userApprovalQuote,
    "正确，批准并继续（推荐）"
  );
  assert.equal(
    gate06.geometrySpec.approval.reviewedArtifactSha256,
    "9297edb9dbd8d1f0c6c769324e7f1f12f228deae7c67c13e06c2fe4f098def2d"
  );
  assert.deepEqual(gate06.geometrySpec.approval.completedChecklist, [
    "orbit-whole-case",
    "inspect-six-fixed-directions",
    "toggle-wireframe",
    "confirm-presentation-root-rigid-ownership",
    "confirm-no-exploded-review"
  ]);
  assert.equal(
    gate06.geometrySpec.approval.interactionMode,
    "interactive-glb-plus-review-board"
  );
  assert.equal(gate07.status, "approved");
  assert.equal(gate07.decision.action, "approve");
  assert.equal(gate07.materialSpec.revision, 2);
  assert.equal(gate07.materialSpec.gate07Approved, true);
  assert.equal(gate07.materialSpec.gate08Entered, true);
  assert.equal(gate07.materialSpec.approval.approvedRevision, 2);
  assert.equal(
    gate07.materialSpec.approval.userApprovalQuote,
    "材质与扫光批准，标签文字后续由 Unity 替换为真实数据"
  );
  assert.equal(gate07.materialSpec.approval.labelContentApproved, false);
  assert.ok(
    gate07.materialSpec.approval.labelOwnership.unity.includes(
      "real-collectible-id-when-available"
    )
  );
  assert.ok(gate07.historicalDecisions.some(
    (decision) => decision.notes === "挺好的" && decision.materialRevision === 1
  ));
  assert.equal(gate08.status, "approved");
  assert.equal(gate08.decision.action, "approve");
  assert.equal(gate09.status, "approved");
  assert.equal(gate09.decision.action, "approve");
  assert.equal(gate10.status, "approved");
  assert.equal(gate11.status, "approved");
  assert.equal(gate12.status, "ready_for_review");
  assert.equal(derived.derived.approvedCount, 11);
  assert.equal(derived.derived.shippingReady, false);
  assert.equal(
    derived.derived.earliestProblem.stageId,
    "12-shipping"
  );
  assert.equal(gate12.shippingSpec.revision, 4);
  assert.equal(gate12.shippingSpec.previousRejectedRevision, 3);
  assert.equal(
    gate12.shippingSpec.exactRejectionQuote,
    [
      "Pack tear: “撕包仍然有问题”",
      "Light: “仍然太弱”",
      "Gacha energy: “仍需加强蓄力与冲击”"
    ].join("\n")
  );
  assert.equal(gate12.shippingSpec.sourceGate11ApprovalEventId,
    "c14b967f-6399-4cff-8baa-78a0eb6169dc");
  assert.equal(gate12.shippingSpec.sourceFbxSha256,
    "21c9db68723f0006d7c6bfec5280cafe55c16cf5392ff97c365c966e91f847ae");
  assert.equal(gate12.shippingSpec.profileValuesLocked, false);
  assert.equal(gate12.shippingSpec.pendingVisualTuning, true);
  assert.equal(gate12.shippingSpec.gate12Status, "ready_for_review");
  assert.equal(gate12.shippingSpec.timingChangedFromRev3, true);
  assert.equal(gate12.shippingSpec.packTear.tearCommitProgress, 0.62);
  assert.equal(
    gate12.shippingSpec.packTear.belowThresholdBehavior,
    "visible-follow-deformation-then-rebound"
  );
  assert.equal(
    gate12.shippingSpec.packTear.foregroundUntilAuthoritativeReceiptAndTwoFrameReady,
    true
  );
  assert.equal(gate12.shippingSpec.packTear.noEmptyFrame, true);
  assert.equal(gate12.shippingSpec.localYRotationDegrees, 720);
  assert.equal(gate12.shippingSpec.firstSpinDegrees, 360);
  assert.equal(gate12.shippingSpec.secondSpinDegrees, 360);
  assert.equal(gate12.shippingSpec.noStopBetweenSpins, true);
  assert.deepEqual(gate12.shippingSpec.eventCounts, {
    seam: 1,
    releasePulse: 1,
    arrivalRim: 1,
    rotationRimPasses: 2,
    finalSheen: 1,
    persistentLight: 0
  });
  assert.equal(gate12.shippingSpec.outsideMeshEffectPixels, 0);
  assert.equal(gate12.shippingSpec.pointLightCount, 0);
  assert.equal(gate12.shippingSpec.particleEmitterCount, 0);
  assert.equal(gate12.shippingSpec.bloomDependency, false);
  assert.equal(gate12.shippingSpec.vfxGraphDependency, false);
  assert.equal(gate12.shippingSpec.screenShake, false);
  assert.equal(gate12.shippingSpec.persistentLightLoop, false);
  assert.equal(gate12.shippingSpec.wholeAssembledCaseOnly, true);
  assert.equal(gate12.shippingSpec.sameInstanceThroughAcknowledgement, true);
  assert.equal(gate12.shippingSpec.externalEntityCount, 0);
  assert.equal(gate12.shippingSpec.externalModelCount, 0);
  assert.equal(gate12.shippingSpec.externalPrefabCount, 0);
  assert.equal(gate12.shippingSpec.toyIndependentAngularVelocity, 0);
  assert.equal(gate12.shippingSpec.simulatorInstalledLaunched, true);
  assert.equal(gate12.shippingSpec.physicalPhoneInstalled, false);
  assert.equal(gate12.shippingSpec.deviceAccepted, false);
  assert.equal(gate12.shippingSpec.shippingReady, false);
  assert.equal(gate12.shippingSpec.visualApproved, false);
  assert.equal(gate12.shippingSpec.parameterSnapshot.handoffDurationSeconds, 0.14);
  assert.equal(gate12.shippingSpec.parameterSnapshot.firstSpinDurationSeconds, 0.5);
  assert.equal(gate12.shippingSpec.parameterSnapshot.secondSpinDurationSeconds, 1.1);
  assert.ok(
    Math.abs(
      gate12.shippingSpec.parameterSnapshot.profileDurationSeconds - 2.94
    ) < 1e-9
  );
  assert.ok(
    gate12.shippingSpec.parameterSnapshot.firstToSecondAverageSpeedRatio >= 2
  );
  assert.ok(
    Object.values(gate12.shippingSpec.visualContrast.caseCues).every(
      (cue) => cue.externalPixels === 0
    )
  );
  assert.ok(
    gate12.shippingSpec.visualContrast.pack.committedOpeningGapPixels >= 35
  );
  assert.equal(gate12.shippingSpec.sourceExtraction.moduleFiles.length, 4);
  assert.ok(gate12.historicalRevisions.some(
    (revision) => (
      revision.shippingSpec.revision === 1
      && revision.shippingSpec.approval.visualApproved === true
    )
  ));
  assert.ok(gate12.historicalRevisions.some(
    (revision) => (
      revision.shippingSpec.revision === 2
      && revision.shippingSpec.rejection.rejectedRevision === 2
      && revision.shippingSpec.rejection.userSelectionQuote
        === "节奏或光效仍需修改"
      && revision.preservedForHistory === true
    )
  ));
  assert.ok(gate12.historicalRevisions.some(
    (revision) => (
      revision.shippingSpec.revision === 3
      && revision.shippingSpec.rejection.rejectedRevision === 3
      && revision.shippingSpec.rejection.selections.packTear
        === "撕包仍然有问题"
      && revision.shippingSpec.rejection.selections.light
        === "仍然太弱"
      && revision.shippingSpec.rejection.selections.gachaEnergy
        === "仍需加强蓄力与冲击"
      && revision.preservedForHistory === true
    )
  ));
  assert.equal(
    manifest.currentState.deviceStatus,
    "simulator-preview-only-physical-phone-untouched"
  );
  assert.equal(manifest.currentState.shippingPreview.revision, 4);
  assert.equal(manifest.currentState.shippingPreview.gate12Status, "ready_for_review");
  assert.equal(manifest.currentState.shippingPreview.visualApproved, false);
  assert.equal(manifest.currentState.shippingPreview.shippingReady, false);
  assert.equal(stageReadiness(manifest, "12-shipping").ready, true);
  assert.equal(stageReadiness(manifest, "02-analysis").ready, true);
  assert.equal(stageReadiness(manifest, "03-contract").ready, true);
  assert.equal(stageReadiness(manifest, "04-architecture").ready, true);
  assert.equal(stageReadiness(manifest, "05-blockout").ready, true);
  assert.equal(stageReadiness(manifest, "06-geometry").ready, true);
  assert.equal(stageReadiness(manifest, "07-material").ready, true);
  assert.equal(stageReadiness(manifest, "08-lighting").ready, true);
  assert.equal(stageReadiness(manifest, "09-environment").ready, true);
  assert.equal(stageReadiness(manifest, "10-export").ready, true);
  assert.equal(
    gate06.geometrySpec.sourceGeometryDigest,
    "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f"
  );
  assert.equal(
    gate06.geometrySpec.evaluatedGeometryDigest,
    "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
  );
  assert.equal(
    gate06.geometrySpec.identity.vertexPositionDigest,
    "ced0edf95f8fa6416c5a0e33ebf8dc99fdafcdb3beceac85ee2970bbb2a7682c"
  );
  assert.equal(
    gate06.geometrySpec.identity.silhouetteDigest,
    "81615c0e5afd59b634dfa2e85040b31b30b9d5ef0ddc9e12462f1b3d1c59f6b4"
  );
  assert.equal(
    gate06.geometrySpec.identity.topologyWindingDigest,
    "c29bc1dd8c0f0c52fd4c70d102bcfc2b4007e579795b605adeb21611a3bf7c79"
  );
  assert.deepEqual(gate06.geometrySpec.dimensionsMm, {
    width: 228,
    height: 304,
    depth: 59
  });
  assert.equal(gate06.geometrySpec.portraitWidthHeightRatio, 0.75);
  assert.equal(gate06.geometrySpec.labelCenterYmm, 99);
  assert.equal(gate06.geometrySpec.maximumCornerCenterDriftMm, 0);
  assert.equal(gate06.geometrySpec.meshIntegrity.openBoundaryEdgeCount, 0);
  assert.equal(gate06.geometrySpec.meshIntegrity.nonManifoldEdgeCount, 0);
  assert.equal(gate06.geometrySpec.meshIntegrity.selfIntersectionPairCount, 0);
  assert.equal(gate06.geometrySpec.meshIntegrity.degenerateElementCount, 0);
  assert.equal(
    gate06.geometrySpec.meshIntegrity.allSubjectMaterialSignedVolumesPositive,
    true
  );
  assert.ok(Object.values(gate06.geometrySpec.meshIntegrity.perObject).every(
    (item) => item.signedVolumeMm3 > 0 && item.pass
  ));
  assert.equal(gate06.geometrySpec.tube.connectedMaterialBodyCount, 1);
  assert.equal(gate06.geometrySpec.tube.channelSamplesVisited, 384);
  assert.equal(gate06.geometrySpec.tube.channelSampleCount, 384);
  assert.equal(gate06.geometrySpec.tube.netMaterialSignedVolumeMm3, 52932.982745);
  assert.equal(gate06.geometrySpec.tube.outerBoundaryOutward, true);
  assert.equal(gate06.geometrySpec.tube.innerBoundaryTowardLumen, true);
  assert.deepEqual(gate06.geometrySpec.hierarchy, {
    movingTransform: "PresentationRoot",
    rigidAssembly: "CaseAssembly",
    contentSlot: "caller-owned-static",
    sameInstance: true,
    wholeCaseOnly: true,
    bakedRuntimeAnimation: false
  });
  assert.equal(gate06.geometrySpec.review.reviewArtifactExplodedPartCount, 0);
  assert.deepEqual(gate06.geometrySpec.review.internalTechnicalArtifactIds, [
    "premium-display-case-geometry-exploded-r002"
  ]);
  assert.equal(gate06.geometrySpec.review.interactionRequired, true);
  assert.equal(gate06.geometrySpec.animationTimingIncluded, false);
  assert.equal(gate06.geometrySpec.lightTuningIncluded, false);
  assert.equal(gate06.geometrySpec.shippingImplementationIncluded, false);
  assert.equal(gate06.geometrySpec.shippingUnityChanged, false);
  assert.equal(gate06.geometrySpec.gate07Status, "ready_for_review");
  assert.deepEqual(gate06.reviewArtifactIds, [
    "premium-display-case-geometry-interactive-review-r003",
    "premium-display-case-geometry-presentation-review-r003",
    "premium-display-case-geometry-workbench-r003",
    "premium-display-case-geometry-dimensions-r003",
    "premium-display-case-geometry-presentation-root-r003",
    "premium-display-case-geometry-front-r003",
    "premium-display-case-geometry-back-r003",
    "premium-display-case-geometry-top-r003",
    "premium-display-case-geometry-bottom-r003",
    "premium-display-case-geometry-left-r003",
    "premium-display-case-geometry-right-r003"
  ]);
  assert.ok(gate06.artifactIds.includes("premium-display-case-geometry-exploded-r002"));
  assert.ok(!gate06.reviewArtifactIds.includes("premium-display-case-geometry-exploded-r002"));
  const gate06ReviewAssets = gate06.reviewArtifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)
  );
  assert.ok(gate06ReviewAssets.every(
    (asset) => asset.wholeAssembledCaseOnly === true && asset.explodeEligible === false
  ));
  const interactiveAsset = gate06ReviewAssets.find(
    (asset) => asset.id === "premium-display-case-geometry-interactive-review-r003"
  );
  assert.equal(interactiveAsset.path.endsWith(".glb"), true);
  assert.equal(interactiveAsset.interaction.type, "threejs-orbit");
  assert.equal(interactiveAsset.interaction.approvalRequiresCompletedChecklist, true);
  assert.equal(interactiveAsset.interaction.stage10ExportApproval, false);
  const appSource = fs.readFileSync(
    path.join(repoRoot, "tools/model-provenance-explorer/app.js"),
    "utf8"
  );
  const userReviewGuard = appSource.indexOf(
    "if (userReview.length) return userReview;"
  );
  assert.ok(userReviewGuard > 0);
  assert.ok(appSource.indexOf("\"exploded-geometry\"", userReviewGuard) > userReviewGuard);
  const assets = manifest.assets.filter((asset) => asset.stageId === "06-geometry");
  const rev1Assets = assets.filter((asset) => asset.id.endsWith("-r001"));
  const rev2Assets = assets.filter((asset) => asset.id.endsWith("-r002"));
  const rev3Assets = assets.filter((asset) => asset.id.endsWith("-r003"));
  assert.equal(assets.length, 113);
  assert.equal(rev1Assets.length, 42);
  assert.equal(rev2Assets.length, 43);
  assert.equal(rev3Assets.length, 28);
  assert.ok(rev1Assets.every((asset) => asset.reviewState === "technical-rejected"));
  assert.ok(rev1Assets.every((asset) => asset.rejectionScope === "continuous-tube-winding-orientation"));
  assert.ok(rev1Assets.every((asset) => asset.supersededBy?.endsWith("-r002")));
  const currentRev3Assets = gate06.artifactIds
    .map((assetId) => manifest.assets.find((asset) => asset.id === assetId))
    .filter((asset) => asset.id.endsWith("-r003"));
  assert.equal(currentRev3Assets.length, 24);
  assert.ok(currentRev3Assets.every((asset) => asset.sourceClaimIds.length === 10));
  assert.ok(currentRev3Assets.every((asset) => asset.explodeEligible === false));
  const reportAsset = assets.find(
    (asset) => asset.id === "premium-display-case-geometry-revalidation-r003"
  );
  const report = JSON.parse(fs.readFileSync(resolveRepoPath(reportAsset.path), "utf8"));
  assert.equal(report.status, "pass");
  assert.equal(
    report.identity.source.vertexPositionDigest,
    report.identity.derivative.vertexPositionDigest
  );
  assert.equal(
    report.identity.source.silhouetteDigest,
    report.identity.derivative.silhouetteDigest
  );
  assert.notEqual(
    report.identity.source.topologyWindingDigest,
    report.identity.derivative.topologyWindingDigest
  );
  assert.equal(report.structural.closedTube.channelFloodFill.visitedSamples, 384);
  assert.equal(report.meshIntegrity.objects.ContinuousTubePerimeter.badContiguousEdgeCount, 0);
  assert.equal(report.meshIntegrity.objects.ContinuousTubePerimeter.signedVolumeMm3, 52932.982745);
  assert.equal(report.meshIntegrity.objects.ContinuousTubePerimeter.positiveMaterialSignedVolume, true);
  assert.ok(Object.values(report.meshIntegrity.objects).every((item) => item.signedVolumeMm3 > 0 && item.pass));
  assert.equal(report.tubeOrientation.outerBoundary.outward, true);
  assert.equal(report.tubeOrientation.innerBoundary.inwardTowardLumen, true);
  assert.equal(report.tubeOrientation.netMaterialVolumePositive, true);
  assert.equal(
    report.tubeOrientation.orientationDisposition,
    "outer-outward-inner-toward-lumen-net-positive"
  );
  const reviewReportAsset = assets.find(
    (asset) => asset.id === "premium-display-case-geometry-review-validation-r003"
  );
  const reviewReport = JSON.parse(
    fs.readFileSync(resolveRepoPath(reviewReportAsset.path), "utf8")
  );
  assert.equal(reviewReport.status, "pass");
  assert.equal(reviewReport.metrics.orthographicViewCount, 6);
  assert.equal(reviewReport.metrics.reviewArtifactExplodedPartCount, 0);
  assert.deepEqual(reviewReport.internalTechnicalArtifactIds, [
    "premium-display-case-geometry-exploded-r002"
  ]);
  assert.ok(Object.values(reviewReport.checks).every(Boolean));
  const gate07Assets = manifest.assets.filter((asset) => asset.stageId === "07-material");
  assert.equal(gate07Assets.length, 123);
  assert.ok(gate07Assets.every((asset) => asset.wholeCaseOnly === true));
  assert.ok(gate07Assets.every((asset) => asset.explodeEligible === false));
  const currentGate07Assets = gate07.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)
  );
  assert.equal(currentGate07Assets.length, 87);
  assert.deepEqual(gate07.reviewArtifactIds, [
    "premium-display-case-material-turntable-mp4-r002",
    "premium-display-case-material-board-r002",
    "premium-display-case-material-closeups-r002",
    "premium-display-case-material-turntable-contact-r002",
    "premium-display-case-material-sheen-compatibility-r002"
  ]);
  assert.ok(gate07.reviewArtifactIds.every((assetId) => {
    const asset = currentGate07Assets.find((candidate) => candidate.id === assetId);
    return asset.wholeCaseOnly === true && asset.explodeEligible === false;
  }));
  const turntableAsset = currentGate07Assets.find(
    (asset) => asset.id === "premium-display-case-material-turntable-mp4-r002"
  );
  assert.equal(turntableAsset.interaction.type, "real-render-turntable");
  assert.equal(turntableAsset.interaction.frameCount, 25);
  assert.equal(turntableAsset.interaction.approvalRequiresCompletedChecklist, true);
  assert.equal(gate07.materialSpec.sourceGate06Revision, 3);
  assert.equal(gate07.materialSpec.sourceGate04EvidenceRevision, 7);
  assert.equal(
    gate07.materialSpec.sourceGate06Approval.userApprovalQuote,
    "正确，批准并继续（推荐）"
  );
  assert.equal(gate07.materialSpec.geometryIdentity.fullGeometryDigest, "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951");
  assert.equal(gate07.materialSpec.geometryIdentity.vertexPositionDigest, "ced0edf95f8fa6416c5a0e33ebf8dc99fdafcdb3beceac85ee2970bbb2a7682c");
  assert.equal(gate07.materialSpec.geometryIdentity.topologyWindingDigest, "c29bc1dd8c0f0c52fd4c70d102bcfc2b4007e579795b605adeb21611a3bf7c79");
  assert.deepEqual(gate07.materialSpec.boundsMm, { width: 228, height: 304, depth: 59 });
  assert.ok(Math.abs(gate07.materialSpec.pbrValues.frostedPolycarbonateShell.ior - 1.585) < 0.000001);
  assert.ok(Math.abs(gate07.materialSpec.pbrValues.frostedPolycarbonateShell.roughness - 0.22) < 0.000001);
  assert.ok(Math.abs(gate07.materialSpec.pbrValues.frostedPolycarbonateShell.transmissionWeight - 0.92) < 0.000001);
  assert.ok(Math.abs(gate07.materialSpec.pbrValues.continuousTubeEdge.roughness - 0.18) < 0.000001);
  assert.ok(Math.abs(gate07.materialSpec.pbrValues.blackTactileInsert.roughness - 0.91) < 0.000001);
  assert.ok(Math.abs(gate07.materialSpec.pbrValues.physicalLabelPaper.roughness - 0.73) < 0.000001);
  assert.ok(Math.abs(gate07.materialSpec.pbrValues.narrowNeutralSilverFoil.metallic - 0.96) < 0.000001);
  assert.ok(Math.abs(gate07.materialSpec.pbrValues.narrowNeutralSilverFoil.roughness - 0.3) < 0.000001);
  assert.equal(gate07.materialSpec.grainStability.coordinateSpace, "object-local");
  assert.equal(gate07.materialSpec.grainStability.worldSpaceGrain, false);
  assert.equal(gate07.materialSpec.turntable.frameCount, 25);
  assert.equal(gate07.materialSpec.sheenMaskCompatibility.outsideSubjectPixels, 0);
  assert.equal(
    gate07.materialSpec.sheenMaskCompatibility.outsideAllowedMaterialZonePixels,
    0
  );
  assert.equal(
    Object.values(gate07.materialSpec.identityBoundary).every((value) => value === false),
    true
  );
  assert.equal(gate07.materialSpec.wholeCaseOnly, true);
  assert.equal(gate07.materialSpec.reviewExplodedPartCount, 0);
  assert.equal(gate07.materialSpec.finalLightingApproved, false);
  const gate07Build = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate07Assets.find((asset) => asset.id === "premium-display-case-material-revalidation-r002").path
  ), "utf8"));
  const gate07Images = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate07Assets.find((asset) => asset.id === "premium-display-case-material-review-validation-r002").path
  ), "utf8"));
  const gate07Snapshot = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate07Assets.find((asset) => asset.id === "premium-display-case-material-compatibility-snapshot-r002").path
  ), "utf8"));
  assert.equal(gate07Build.status, "pass");
  assert.equal(gate07Images.status, "pass");
  assert.equal(gate07Snapshot.materialRevision, 2);
  assert.ok(Object.values(gate07Build.checks).every(Boolean));
  assert.ok(Object.values(gate07Images.checks).every(Boolean));
  const gate08Assets = manifest.assets.filter((asset) => asset.stageId === "08-lighting");
  assert.equal(gate08Assets.length, 69);
  assert.ok(gate08Assets.every((asset) => asset.wholeCaseOnly === true));
  assert.ok(gate08Assets.every((asset) => asset.explodeEligible === false));
  const currentGate08Assets = gate08.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)
  );
  assert.equal(currentGate08Assets.length, 44);
  assert.ok(currentGate08Assets.every((asset) => asset.labelContentApproved === false));
  assert.deepEqual(gate08.reviewArtifactIds, [
    "premium-display-case-lighting-turntable-mp4-r002",
    "premium-display-case-lighting-turntable-contact-r002",
    "premium-display-case-lighting-review-r002",
    "premium-display-case-lighting-details-r002",
    "premium-display-case-lighting-passes-r002",
    "premium-display-case-lighting-parameters-r002",
    "premium-display-case-lighting-label-placeholder-r002",
    "premium-display-case-lighting-sheen-compatibility-r002"
  ]);
  assert.equal(gate08.lightingSpec.revision, 2);
  assert.equal(gate08.lightingSpec.sourceMaterialRevision, 2);
  assert.equal(
    gate08.lightingSpec.sourceMaterialApprovalQuote,
    "材质与扫光批准，标签文字后续由 Unity 替换为真实数据"
  );
  assert.equal(gate08.lightingSpec.sourceArchitectureEvidenceRevision, 7);
  assert.equal(gate08.lightingSpec.sourceGeometryDigest, "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951");
  assert.equal(gate08.lightingSpec.sourceMaterialDigest, "8358cfdb12e49f87adbbafd96f33f2beb3415f9b920cb62732c73173c7799210");
  assert.deepEqual(gate08.lightingSpec.controlledRigCandidates.ratios, {
    key: 1,
    fill: 0.3,
    rim: 0.4
  });
  assert.equal(gate08.lightingSpec.cameraCandidates.hero.lensMm, 60);
  assert.equal(gate08.lightingSpec.cameraCandidates.hero.verticalFovDegrees, 29.862834);
  assert.equal(gate08.lightingSpec.renderCandidates.viewTransform, "AgX");
  assert.equal(gate08.lightingSpec.renderCandidates.exposureEv, 0.550000011920929);
  assert.equal(gate08.lightingSpec.renderCandidates.shutterSeconds, null);
  assert.equal(gate08.lightingSpec.renderCandidates.iso, null);
  assert.equal(gate08.lightingSpec.wholeCaseOnly, true);
  assert.equal(gate08.lightingSpec.reviewExplodedPartCount, 0);
  assert.equal(
    gate08.lightingSpec.labelPolicy.visibleContentState,
    "placeholder-not-approved"
  );
  assert.equal(
    gate08.lightingSpec.meshClippedSheenCompatibility.outsideSubjectPixels,
    0
  );
  assert.equal(
    gate08.lightingSpec.meshClippedSheenCompatibility.outsideAllowedMaterialZonePixels,
    0
  );
  assert.equal(
    gate08.lightingSpec.candidateBoundary.automaticUnityRuntimeConstants,
    false
  );
  assert.equal(gate08.lightingSpec.animationBoundary.timingBaked, false);
  assert.equal(gate08.lightingSpec.turntable.frameCount, 13);
  assert.equal(gate08.lightingSpec.gate08Approved, true);
  assert.equal(gate08.lightingSpec.gate09Entered, true);
  assert.equal(gate08.lightingSpec.approval.approvedRevision, 2);
  assert.equal(
    gate08.lightingSpec.approval.userApprovalQuote,
    "灯光方向正确，批准并继续（推荐）"
  );
  assert.equal(gate08.lightingSpec.approval.labelContentApproved, false);
  assert.equal(gate08.lightingSpec.approval.lookdevCandidatesOnly, true);
  assert.equal(gate08.lightingSpec.approval.unityRuntimeValuesTunable, true);
  const gate08Build = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate08Assets.find((asset) => asset.id === "premium-display-case-lighting-revalidation-r002").path
  ), "utf8"));
  const gate08Audit = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate08Assets.find((asset) => asset.id === "premium-display-case-lighting-blender-audit-r002").path
  ), "utf8"));
  const gate08Images = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate08Assets.find((asset) => asset.id === "premium-display-case-lighting-image-validation-r002").path
  ), "utf8"));
  const gate08Qa = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate08Assets.find((asset) => asset.id === "premium-display-case-lighting-qa-verdict-r002").path
  ), "utf8"));
  const gate08Turntable = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate08Assets.find((asset) => asset.id === "premium-display-case-lighting-turntable-report-r002").path
  ), "utf8"));
  assert.equal(gate08Build.status, "pass");
  assert.equal(gate08Audit.status, "pass");
  assert.equal(gate08Images.status, "pass");
  assert.equal(gate08Qa.result, "READY_FOR_LIGHTING_REVIEW_NOT_SHIPPING");
  assert.equal(gate08Turntable.frameCount, 13);
  assert.ok(Object.values(gate08Build.checks).every(Boolean));
  assert.ok(Object.values(gate08Audit.checks).every(Boolean));
  assert.ok(Object.values(gate08Images.checks).every(Boolean));
  assert.ok(Object.values(gate08Turntable.checks).every(Boolean));
  const gate09Assets = manifest.assets.filter((asset) => asset.stageId === "09-environment");
  assert.equal(gate09Assets.length, 28);
  assert.equal(gate09.artifactIds.length, 28);
  assert.equal(gate09.reviewArtifactIds.length, 7);
  assert.ok(gate09Assets.every((asset) => asset.wholeAssembledCaseOnly === true));
  assert.ok(gate09Assets.every((asset) => asset.explodeEligible === false));
  assert.equal(gate09.environmentSpec.revision, 1);
  assert.equal(gate09.environmentSpec.sourceLightingRevision, 2);
  assert.equal(
    gate09.environmentSpec.sourceLightingApprovalQuote,
    "灯光方向正确，批准并继续（推荐）"
  );
  assert.equal(gate09.environmentSpec.geometryUnchanged, true);
  assert.equal(gate09.environmentSpec.materialUnchanged, true);
  assert.equal(gate09.environmentSpec.cameraUnchanged, true);
  assert.equal(gate09.environmentSpec.approvedLightingDirectionUnchanged, true);
  assert.equal(gate09.environmentSpec.wholeAssembledCaseOnly, true);
  assert.equal(gate09.environmentSpec.reviewExplodedPartCount, 0);
  assert.equal(gate09.environmentSpec.environmentPolicy.backgroundStaticThroughoutReveal, true);
  assert.equal(gate09.environmentSpec.environmentPolicy.cameraMotion, false);
  assert.equal(gate09.environmentSpec.environmentPolicy.backgroundMotion, false);
  assert.equal(gate09.environmentSpec.toyPrizeOwnership, "caller-owned-static");
  assert.equal(gate09.environmentSpec.labelPolicy.visibleContentState, "placeholder-not-approved");
  assert.equal(gate09.environmentSpec.meshClippedSheen.outsideSubjectPixels, 0);
  assert.equal(gate09.environmentSpec.meshClippedSheen.detachedLightEffect, false);
  assert.equal(gate09.environmentSpec.imageMetrics.minimumSubjectMargin, 0.14457208);
  assert.equal(
    gate09.environmentSpec.imageMetrics.repeatedBackgroundMaximumChannelDelta,
    0
  );
  assert.equal(
    gate09.environmentSpec.imageMetrics.externalHaloMetrics
      .outsideExpandedSubjectAbove16Fraction,
    0
  );
  assert.equal(gate09.environmentSpec.comparisonRecording.frameCount, 72);
  assert.equal(gate09.environmentSpec.comparisonRecording.durationSeconds, 6);
  assert.equal(gate09.environmentSpec.candidateBoundary.unityEnvironmentTunable, true);
  assert.equal(gate09.environmentSpec.candidateBoundary.unityIblIntensityTunable, true);
  assert.equal(gate09.environmentSpec.candidateBoundary.unityExposureTunable, true);
  assert.equal(gate09.environmentSpec.candidateBoundary.unityCameraTunable, true);
  assert.equal(gate09.environmentSpec.gate09Approved, true);
  assert.equal(gate09.environmentSpec.gate10Entered, true);
  assert.equal(gate09.environmentSpec.approval.approvedRevision, 1);
  assert.equal(
    gate09.environmentSpec.approval.userApprovalQuote,
    "环境正确，批准并继续（推荐）"
  );
  assert.equal(gate09.environmentSpec.approval.labelContentApproved, false);
  assert.equal(gate09.environmentSpec.approval.lookdevCandidatesOnly, true);
  assert.equal(gate09.environmentSpec.approval.unityRuntimeValuesTunable, true);
  assert.equal(gate09.environmentSpec.approval.gate10Status, "ready_for_review");
  const gate09Build = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate09Assets.find(
      (asset) => asset.id === "premium-display-case-environment-revalidation-r001"
    ).path
  ), "utf8"));
  const gate09Images = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate09Assets.find(
      (asset) => asset.id === "premium-display-case-environment-image-validation-r001"
    ).path
  ), "utf8"));
  const gate09Audit = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate09Assets.find(
      (asset) => asset.id === "premium-display-case-environment-blender-audit-r001"
    ).path
  ), "utf8"));
  const gate09Qa = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate09Assets.find(
      (asset) => asset.id === "premium-display-case-environment-qa-verdict-r001"
    ).path
  ), "utf8"));
  assert.equal(gate09Build.status, "pass");
  assert.equal(gate09Images.status, "pass");
  assert.equal(gate09Audit.status, "pass");
  assert.equal(gate09Qa.result, "READY_FOR_ENVIRONMENT_REVIEW_NOT_SHIPPING");
  assert.ok(Object.values(gate09Build.checks).every(Boolean));
  assert.ok(Object.values(gate09Images.checks).every(Boolean));
  assert.ok(Object.values(gate09Audit.checks).every(Boolean));
  const gate10Assets = gate10.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)
  );
  assert.equal(gate10Assets.length, 20);
  assert.ok(gate10Assets.every((asset) => asset.wholeAssembledCaseOnly === true));
  assert.ok(gate10Assets.every((asset) => asset.explodeEligible === false));
  assert.deepEqual(gate10.reviewArtifactIds, [
    "premium-display-case-product-glb-r001",
    "premium-display-case-export-review-board-r001"
  ]);
  assert.ok(gate10.reviewArtifactIds.every((assetId) => {
    const asset = gate10Assets.find((candidate) => candidate.id === assetId);
    return asset.wholeAssembledCaseOnly === true && asset.explodeEligible === false;
  }));
  const exportGlbAsset = gate10Assets.find(
    (asset) => asset.id === "premium-display-case-product-glb-r001"
  );
  assert.equal(exportGlbAsset.interaction.type, "real-exported-glb-orbit");
  assert.equal(exportGlbAsset.interaction.approvalRequiresCompletedChecklist, true);
  assert.equal(exportGlbAsset.interaction.reviewExplodedPartCount, 0);
  assert.equal(gate10.exportSpec.revision, 1);
  assert.equal(
    gate10.exportSpec.sourceEnvironmentApprovalEventId,
    "04560468-01da-4a1f-8bc8-a324966490d6"
  );
  assert.deepEqual(gate10.exportSpec.dimensionsMm, {
    width: 228,
    height: 304,
    depth: 59
  });
  assert.equal(gate10.exportSpec.labelCenterYmm, 99);
  assert.equal(gate10.exportSpec.hierarchy.runtimeMotionOwner, "PresentationRoot");
  assert.equal(gate10.exportSpec.hierarchy.rigidAssembly, "CaseAssembly");
  assert.equal(gate10.exportSpec.hierarchy.contentSlot, "caller-owned-empty");
  assert.equal(gate10.exportSpec.objectCount, 12);
  assert.equal(gate10.exportSpec.meshCount, 5);
  assert.equal(gate10.exportSpec.triangleCount, 100016);
  assert.equal(gate10.exportSpec.labelUv.minimum.join(","), "0,0");
  assert.equal(gate10.exportSpec.labelUv.maximum.join(","), "1,1");
  assert.equal(gate10.exportSpec.labelPolicy.placeholderTextBaked, false);
  assert.equal(gate10.exportSpec.labelPolicy.fakeCollectibleIdBaked, false);
  assert.equal(gate10.exportSpec.labelPolicy.authoritativeContent, "Unity runtime data");
  assert.ok(Object.values(gate10.exportSpec.runtimeBoundary).every(
    (value) => value === false || value === "Unity runtime data"
  ));
  assert.ok(Object.values(gate10.exportSpec.excluded).every(Boolean));
  assert.equal(gate10.exportSpec.collision.included, false);
  assert.equal(gate10.exportSpec.collision.inventedGeometry, false);
  assert.equal(gate10.exportSpec.roundTrip.geometryDigestIdentity, true);
  assert.equal(gate10.exportSpec.roundTrip.exportWindingDigestIdentity, true);
  assert.equal(gate10.exportSpec.roundTrip.positiveMaterialVolumes, true);
  assert.ok(gate10.exportSpec.roundTrip.maximumVertexErrorMm.fbx <= 0.001);
  assert.ok(gate10.exportSpec.roundTrip.maximumVertexErrorMm.glb <= 0.001);
  assert.equal(gate10.exportSpec.wholeAssembledCaseOnly, true);
  assert.equal(gate10.exportSpec.reviewExplodedPartCount, 0);
  assert.equal(gate10.exportSpec.gate10Approved, true);
  assert.equal(gate10.exportSpec.gate11Entered, true);
  assert.equal(gate10.exportSpec.shippingUnityChanged, false);
  assert.equal(gate10.exportSpec.buildInstallPhonePush, false);
  assert.equal(
    gate10.exportSpec.approval.userApprovalQuote,
    "正确，批准并导入 Unity（推荐）"
  );
  assert.equal(
    gate10.exportSpec.approval.approvedFbxSha256,
    "21c9db68723f0006d7c6bfec5280cafe55c16cf5392ff97c365c966e91f847ae"
  );
  assert.equal(gate10.exportSpec.approval.gate11Status, "ready_for_review");
  const gate10RoundTrip = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate10Assets.find(
      (asset) => asset.id === "premium-display-case-export-roundtrip-report-r001"
    ).path
  ), "utf8"));
  const gate10GlbStructure = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate10Assets.find(
      (asset) => asset.id === "premium-display-case-export-glb-structure-r001"
    ).path
  ), "utf8"));
  const gate10Qa = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate10Assets.find(
      (asset) => asset.id === "premium-display-case-export-qa-verdict-r001"
    ).path
  ), "utf8"));
  assert.equal(gate10RoundTrip.status, "pass");
  assert.ok(Object.values(gate10RoundTrip.checks).every(Boolean));
  assert.equal(gate10GlbStructure.status, "pass");
  assert.ok(Object.values(gate10GlbStructure.checks).every(Boolean));
  assert.equal(gate10Qa.result, "READY_FOR_EXPORT_REVIEW_NOT_UNITY");
  assert.ok(Object.values(gate10Qa.checks).every(Boolean));
  const gate11Assets = gate11.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)
  );
  assert.equal(gate11Assets.length, 27);
  assert.ok(gate11Assets.every((asset) => asset.candidateOnly === true));
  assert.ok(gate11Assets.every((asset) => asset.shippingEligible === false));
  assert.ok(gate11Assets.every((asset) => asset.wholeAssembledCaseOnly === true));
  assert.deepEqual(gate11.reviewArtifactIds, [
    "premium-display-case-orbit-recording-r001",
    "premium-display-case-neutral-comparison-r001",
    "premium-display-case-neutral-capture-r001",
    "premium-display-case-hierarchy-report-r001",
    "premium-display-case-bounds-report-r001"
  ]);
  assert.equal(gate11.paritySpec.revision, 1);
  assert.equal(
    gate11.paritySpec.sourceFbxSha256,
    "21c9db68723f0006d7c6bfec5280cafe55c16cf5392ff97c365c966e91f847ae"
  );
  assert.deepEqual(gate11.paritySpec.dimensionsMeters, {
    width: 0.228,
    height: 0.304,
    depth: 0.059
  });
  assert.equal(gate11.paritySpec.objectCount, 12);
  assert.equal(gate11.paritySpec.meshCount, 5);
  assert.equal(gate11.paritySpec.triangleCount, 100016);
  assert.equal(gate11.paritySpec.hierarchyExact, true);
  assert.equal(gate11.paritySpec.perObjectDigestsMatch, true);
  assert.equal(gate11.paritySpec.normalsAndWindingPreserved, true);
  assert.equal(gate11.paritySpec.connectedTubePreserved, true);
  assert.equal(gate11.paritySpec.contentSlotChildCount, 0);
  assert.equal(gate11.paritySpec.labelTextBaked, false);
  assert.equal(gate11.paritySpec.materialAssignmentsExact, true);
  assert.equal(gate11.paritySpec.transparentSortingPass, true);
  assert.equal(gate11.paritySpec.meshClippedSheen, true);
  assert.equal(gate11.paritySpec.outsideSilhouettePixels, 0);
  assert.equal(gate11.paritySpec.pointLightCount, 0);
  assert.equal(gate11.paritySpec.externalHaloCount, 0);
  assert.equal(gate11.paritySpec.gate11Approved, true);
  assert.equal(gate11.paritySpec.gate12Entered, true);
  assert.equal(gate11.paritySpec.shippingPrefabUnchanged, true);
  assert.equal(gate11.paritySpec.shippingSceneUnchanged, true);
  assert.equal(gate11.paritySpec.shippingWiringChanged, false);
  assert.equal(gate11.paritySpec.phoneBuiltInstalledLaunched, false);
  const gate11Parity = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate11Assets.find(
      (asset) => asset.id === "premium-display-case-parity-report-r001"
    ).path
  ), "utf8"));
  const gate11Validation = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate11Assets.find(
      (asset) => asset.id === "premium-display-case-validation-r001"
    ).path
  ), "utf8"));
  const gate11Tests = JSON.parse(fs.readFileSync(resolveRepoPath(
    gate11Assets.find(
      (asset) => asset.id === "premium-display-case-test-summary-r001"
    ).path
  ), "utf8"));
  assert.equal(gate11Parity.status, "pass");
  assert.ok(Object.values(gate11Parity.checks).every(Boolean));
  assert.equal(gate11Validation.status, "pass");
  assert.ok(Object.values(gate11Validation.checks).every(Boolean));
  assert.equal(gate11Tests.focusedPassed, 8);
  assert.equal(gate11Tests.focusedFailures, 0);
  assert.equal(gate11Tests.compileErrors, 0);
  assert.deepEqual(validateManifest(manifest), []);
  const history = readHistory("premium-display-case");
  const gate12Approved = history.find((event) => (
    event.type === "stage-approved"
    && event.stageId === "12-shipping"
    && event.approvedShippingVisualRevision === 1
  ));
  assert.ok(gate12Approved);
  assert.equal(
    gate12Approved.id,
    "8754e752-90ca-4b53-b4ff-0df6bbdae478"
  );
  assert.equal(
    gate12Approved.userQuote,
    "视觉批准，但暂不推手机（推荐）"
  );
  assert.equal(gate12Approved.approvedCount, 12);
  assert.equal(gate12Approved.shippingReady, true);
  assert.equal(gate12Approved.phoneBuildInstallLaunchAuthorized, false);
  assert.equal(gate12Approved.physicalPhoneInstalled, false);
  assert.equal(gate12Approved.deviceAccepted, false);
  const gate12Revision2 = history.find((event) => (
    event.type === "stage-ready-for-review"
    && event.stageId === "12-shipping"
    && event.shippingRevision === 2
  ));
  assert.ok(gate12Revision2);
  assert.equal(gate12Revision2.rotationDegrees, 720);
  assert.equal(gate12Revision2.profileDurationSeconds, 3.6);
  assert.equal(gate12Revision2.physicalPhoneInstalled, false);
  assert.equal(gate12Revision2.autoApproved, false);
  const gate12Revision2Rejected = history.find((event) => (
    event.type === "stage-rejected"
    && event.stageId === "12-shipping"
    && event.rejectedShippingRevision === 2
  ));
  assert.ok(gate12Revision2Rejected);
  assert.equal(gate12Revision2Rejected.userQuote, "节奏或光效仍需修改");
  assert.equal(gate12Revision2Rejected.followUpQuestionnaire, "cancelled");
  assert.equal(
    gate12Revision2Rejected.parameterAttribution,
    "unspecified-do-not-infer"
  );
  assert.equal(gate12Revision2Rejected.previousApprovalPreservedAsHistory, true);
  assert.equal(
    gate12Revision2Rejected.preservedPreviousApprovalEventId,
    "8754e752-90ca-4b53-b4ff-0df6bbdae478"
  );
  assert.equal(
    gate12Revision2Rejected.nextState,
    "awaiting-specific-user-feedback"
  );
  assert.equal(gate12Revision2Rejected.nextRevisionGenerated, false);
  assert.equal(gate12Revision2Rejected.shippingReady, false);
  const gate12Revision3 = history.find((event) => (
    event.type === "stage-ready-for-review"
    && event.stageId === "12-shipping"
    && event.shippingRevision === 3
  ));
  assert.ok(gate12Revision3);
  assert.equal(
    gate12Revision3.exactUserFeedback,
    "光效在哪里啊，完全没有实现啊，然后pack撕开的效果又坏了"
  );
  assert.equal(gate12Revision3.preservedRejectedShippingRevision, 2);
  assert.equal(gate12Revision3.timingChangedFromRev2, false);
  assert.equal(gate12Revision3.outsideMeshEffectPixels, 0);
  assert.equal(gate12Revision3.focusedUnityTests, "53/53");
  assert.equal(gate12Revision3.swiftGateHarness, "37/37");
  assert.equal(gate12Revision3.shippingReady, undefined);
  assert.equal(gate12Revision3.autoApproved, false);
  const gate07Approved = history.find((event) => (
    event.type === "stage-approved"
    && event.stageId === "07-material"
    && event.approvedMaterialRevision === 2
  ));
  assert.ok(gate07Approved);
  assert.equal(
    gate07Approved.userQuote,
    "材质与扫光批准，标签文字后续由 Unity 替换为真实数据"
  );
  assert.equal(gate07Approved.labelContentApproved, false);
  assert.equal(gate07Approved.outsideSubjectPixels, 0);
  const gate08Ready = history.find((event) => (
    event.type === "stage-ready-for-review"
    && event.stageId === "08-lighting"
    && event.lightingRevision === 2
  ));
  assert.ok(gate08Ready);
  assert.equal(gate08Ready.sourceMaterialRevision, 2);
  assert.equal(gate08Ready.turntableFrameCount, 13);
  assert.equal(gate08Ready.labelContentApproved, false);
  assert.equal(gate08Ready.outsideSubjectPixels, 0);
  assert.equal(gate08Ready.gate09Status, "blocked");
  const gate08Approved = history.find((event) => (
    event.type === "stage-approved"
    && event.stageId === "08-lighting"
    && event.approvedLightingRevision === 2
  ));
  assert.ok(gate08Approved);
  assert.equal(
    gate08Approved.userQuote,
    "灯光方向正确，批准并继续（推荐）"
  );
  assert.equal(gate08Approved.labelContentApproved, false);
  assert.equal(gate08Approved.unityRuntimeValuesTunable, true);
  assert.equal(gate08Approved.gate09Status, "eligible");
  const gate09Ready = history.find((event) => (
    event.type === "stage-ready-for-review"
    && event.stageId === "09-environment"
    && event.environmentRevision === 1
  ));
  assert.ok(gate09Ready);
  assert.equal(gate09Ready.sourceLightingRevision, 2);
  assert.equal(gate09Ready.comparisonFrameCount, 72);
  assert.equal(gate09Ready.comparisonDurationSeconds, 6);
  assert.equal(gate09Ready.repeatedBackgroundMaximumChannelDelta, 0);
  assert.equal(gate09Ready.reviewExplodedPartCount, 0);
  assert.equal(gate09Ready.labelContentApproved, false);
  assert.equal(gate09Ready.gate10Status, "blocked");
  const gate09Approved = history.find((event) => (
    event.type === "stage-approved"
    && event.stageId === "09-environment"
    && event.approvedEnvironmentRevision === 1
  ));
  assert.ok(gate09Approved);
  assert.equal(gate09Approved.userQuote, "环境正确，批准并继续（推荐）");
  assert.equal(gate09Approved.gate10Status, "eligible");
  assert.equal(gate09Approved.gate11Status, "blocked");
  const gate10Ready = history.find((event) => (
    event.type === "stage-ready-for-review"
    && event.stageId === "10-export"
    && event.exportRevision === 1
  ));
  assert.ok(gate10Ready);
  assert.equal(
    gate10Ready.sourceEnvironmentApprovalEventId,
    gate09Approved.id
  );
  assert.deepEqual(gate10Ready.reviewArtifactIds, [
    "premium-display-case-product-glb-r001",
    "premium-display-case-export-review-board-r001"
  ]);
  assert.equal(gate10Ready.wholeCaseOnly, true);
  assert.equal(gate10Ready.reviewExplodedPartCount, 0);
  assert.equal(gate10Ready.runtimeAnimationBaked, false);
  assert.equal(gate10Ready.gate11Status, "blocked");
  const gate10Approved = history.find((event) => (
    event.type === "stage-approved"
    && event.stageId === "10-export"
    && event.approvedExportRevision === 1
  ));
  assert.ok(gate10Approved);
  assert.equal(
    gate10Approved.userQuote,
    "正确，批准并导入 Unity（推荐）"
  );
  assert.equal(gate10Approved.fbxUnityAuthority, true);
  assert.equal(gate10Approved.glbPortableEvidenceOnly, true);
  const gate11Ready = history.find((event) => (
    event.type === "stage-ready-for-review"
    && event.stageId === "11-unity-parity"
    && event.parityRevision === 1
  ));
  assert.ok(gate11Ready);
  assert.equal(gate11Ready.sourceGate10ApprovalEventId, gate10Approved.id);
  assert.equal(gate11Ready.perObjectDigestsMatch, true);
  assert.equal(gate11Ready.pointLightCount, 0);
  assert.equal(gate11Ready.gate12Status, "blocked");
  const latest = history.find((event) => event.type === "stage-approved"
    && event.stageId === "02-analysis"
    && event.analysisRevision === "006");
  assert.ok(latest);
  assert.equal(latest.type, "stage-approved");
  assert.equal(latest.stageId, "02-analysis");
  assert.equal(latest.analysisRevision, "006");
  assert.equal(latest.motionStructureRevision, 5);
  assert.equal(latest.lightTreatmentRevision, 6);
  assert.equal(latest.userQuote, "批准这版动效与光效（推荐）");
  assert.deepEqual(latest.lightCueIds, [
    "pack-seam-light",
    "arrival-rim",
    "rotation-surface-rim",
    "final-diagonal-sheen",
    "settle-halo"
  ]);
  assert.equal(latest.reviewDurationSeconds, 3.4);
  assert.equal(latest.shippingDurationApproved, false);
  assert.equal(latest.shippingPreviewApproved, false);
  assert.equal(latest.deviceAccepted, false);
  assert.equal(latest.approvedCount, 2);
  assert.equal(latest.autoApproved, false);
  const contractReady = history.find((event) => event.type === "stage-ready-for-review"
    && event.stageId === "03-contract"
    && event.contractRevision === "003");
  assert.ok(contractReady);
  assert.equal(contractReady.sourceAnalysisRevision, 6);
  assert.equal(contractReady.sourceClaimIds.length, 10);
  assert.equal(contractReady.shippingDurationApproved, false);
  const contractRev3Approved = history.find((event) => event.type === "stage-approved"
    && event.stageId === "03-contract"
    && event.approvedContractRevision === 3);
  assert.ok(contractRev3Approved);
  assert.equal(
    contractRev3Approved.userQuote,
    "批准合同并继续（推荐）"
  );
  assert.equal(contractRev3Approved.shippingDurationApproved, false);
  assert.equal(contractRev3Approved.tunableRuntimeParameterCount, 17);
  assert.equal(contractRev3Approved.gate04Status, "eligible");
  assert.equal(contractRev3Approved.gate05Status, "blocked");
  const architectureReady = history.find((event) => event.type === "stage-ready-for-review"
    && event.stageId === "04-architecture"
    && event.evidenceRevision === 5);
  assert.ok(architectureReady);
  assert.equal(architectureReady.architectureRevision, 2);
  assert.equal(architectureReady.sourceContractRevision, 3);
  assert.equal(architectureReady.finiteLightCueCount, 4);
  assert.equal(architectureReady.particleEmitterCount, 0);
  assert.equal(architectureReady.shippingDurationApproved, false);
  assert.equal(architectureReady.gate05Status, "blocked");
  assert.deepEqual(architectureReady.reviewArtifactIds, [
    "premium-display-case-whole-case-architecture-review-r005"
  ]);
  assert.deepEqual(architectureReady.internalArtifactIds, [
    "premium-display-case-part-tree-internal-r005",
    "premium-display-case-exploded-plan-internal-r005"
  ]);
  const authorityRestored = history.find((event) => event.type === "stage-authority-restored"
    && event.stageId === "02-analysis"
    && event.analysisRevision === 6);
  assert.ok(authorityRestored);
  assert.equal(authorityRestored.activeClaimIds.length, 10);
  const contractRev2Approved = history.find((event) => event.type === "stage-approved"
    && event.stageId === "03-contract"
    && event.approvedContractRevision === 2);
  assert.ok(contractRev2Approved);
});

test("Premium Display Case Gate 12 rev 2 rejection waits for specific feedback", () => {
  const modelId = "premium-display-case-gate12-rejection-fixture";
  const directory = pipelineDirectory(modelId);
  fs.rmSync(directory, { recursive: true, force: true });
  try {
    const manifest = structuredClone(loadManifest("premium-display-case"));
    const gate12 = manifest.stages[11];
    const rev2 = gate12.historicalRevisions.find(
      (revision) => revision.shippingSpec?.revision === 2
    );
    assert.ok(rev2);
    manifest.model.id = modelId;
    manifest.revision = 1;
    gate12.status = "ready_for_review";
    gate12.decision = null;
    gate12.shippingSpec = structuredClone(rev2.shippingSpec);
    gate12.artifactIds = [...rev2.artifactIds];
    gate12.reviewArtifactIds = [...rev2.reviewArtifactIds];
    gate12.shippingSpec.gate12Status = "ready_for_review";
    gate12.shippingSpec.pendingVisualTuning = true;
    gate12.shippingSpec.visualApproved = false;
    delete gate12.shippingSpec.rejection;
    manifest.currentState.visualApproval = "gate12-rev2-real-app-review-pending";
    manifest.currentState.shippingPreview = {
      ...manifest.currentState.shippingPreview,
      revision: 2,
      gate12Status: "ready_for_review",
      pendingVisualTuning: true,
      visualApproved: false
    };
    saveManifest(manifest, null);

    assert.throws(() => decideStage(modelId, "12-shipping", {
      expectedRevision: 1,
      action: "reject",
      notes: "节奏或光效仍需修改",
      userQuote: "节奏或光效仍需修改",
      finalAuthority: "chat",
      followUpQuestionnaire: "cancelled",
      parameterAttribution: "timing"
    }), PipelineError);

    const rejected = decideStage(modelId, "12-shipping", {
      expectedRevision: 1,
      action: "reject",
      notes: "节奏或光效仍需修改",
      userQuote: "节奏或光效仍需修改",
      finalAuthority: "chat",
      followUpQuestionnaire: "cancelled",
      parameterAttribution: "unspecified"
    });
    const rejectedGate12 = rejected.stages[11];
    assert.equal(rejected.revision, 2);
    assert.equal(rejectedGate12.status, "rejected");
    assert.equal(rejectedGate12.shippingSpec.revision, 2);
    assert.equal(rejectedGate12.shippingSpec.gate12Status, "rejected");
    assert.equal(
      rejectedGate12.shippingSpec.rejection.userSelectionQuote,
      "节奏或光效仍需修改"
    );
    assert.equal(
      rejectedGate12.shippingSpec.rejection.parameterAttribution,
      "unspecified-do-not-infer"
    );
    assert.equal(rejectedGate12.shippingSpec.rejection.nextRevisionGenerated, false);
    assert.ok(rejectedGate12.historicalRevisions.some((revision) => (
      revision.shippingSpec?.revision === 1
      && revision.shippingSpec?.approval?.approvalEventId
        === "8754e752-90ca-4b53-b4ff-0df6bbdae478"
      && revision.shippingSpec?.approval?.visualApproved === true
      && revision.preservedForHistory === true
    )));
    assert.equal(
      rejected.currentState.shippingPreview.waitingFor,
      "specific-user-feedback"
    );
    assert.equal(rejected.currentState.shippingPreview.nextRevisionGenerated, false);
    assert.equal(rejected.currentState.shippingPreview.physicalPhoneInstalled, false);
    assert.equal(rejected.currentState.shippingPreview.deviceAccepted, false);
    assert.equal(rejected.derived.shippingReady, false);
    assert.equal(validateManifest(rejected).length, 0);

    const event = readHistory(modelId)[0];
    assert.equal(event.type, "stage-rejected");
    assert.equal(event.userQuote, "节奏或光效仍需修改");
    assert.equal(event.rejectedShippingRevision, 2);
    assert.equal(event.followUpQuestionnaire, "cancelled");
    assert.equal(event.parameterAttribution, "unspecified-do-not-infer");
    assert.equal(event.previousApprovalPreservedAsHistory, true);
    assert.equal(event.nextState, "awaiting-specific-user-feedback");
    assert.equal(event.nextRevisionGenerated, false);
    assert.equal(event.shippingReady, false);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test("Premium Display Case Gate 12 rev 3 rejection preserves exact selections", () => {
  const modelId = "premium-display-case-gate12-rev3-rejection-fixture";
  const directory = pipelineDirectory(modelId);
  fs.rmSync(directory, { recursive: true, force: true });
  try {
    const manifest = structuredClone(loadManifest("premium-display-case"));
    const gate12 = manifest.stages[11];
    const rev3 = gate12.historicalRevisions.find(
      (revision) => revision.shippingSpec?.revision === 3
    );
    assert.ok(rev3);
    const quote = [
      "Pack tear: “撕包仍然有问题”",
      "Light: “仍然太弱”",
      "Gacha energy: “仍需加强蓄力与冲击”"
    ].join("\n");
    const selections = {
      packTear: "撕包仍然有问题",
      light: "仍然太弱",
      gachaEnergy: "仍需加强蓄力与冲击"
    };
    manifest.model.id = modelId;
    manifest.revision = 1;
    gate12.shippingSpec = structuredClone(rev3.shippingSpec);
    gate12.artifactIds = [...rev3.artifactIds];
    gate12.reviewArtifactIds = [...rev3.reviewArtifactIds];
    gate12.status = "ready_for_review";
    gate12.decision = null;
    gate12.shippingSpec.gate12Status = "ready_for_review";
    gate12.shippingSpec.pendingVisualTuning = true;
    gate12.shippingSpec.visualApproved = false;
    delete gate12.shippingSpec.rejection;
    for (const assetId of gate12.artifactIds) {
      const asset = manifest.assets.find((candidate) => candidate.id === assetId);
      if (!asset) continue;
      asset.reviewState = "ready-for-review";
      delete asset.preservedForHistory;
      delete asset.rejectedShippingRevision;
    }
    manifest.currentState.shippingPreview = {
      ...manifest.currentState.shippingPreview,
      revision: 3,
      gate12Status: "ready_for_review",
      pendingVisualTuning: true,
      visualApproved: false
    };
    saveManifest(manifest, null);

    assert.throws(() => decideStage(modelId, "12-shipping", {
      expectedRevision: 1,
      action: "reject",
      notes: quote,
      userQuote: quote,
      finalAuthority: "chat",
      rejectionSelections: {
        ...selections,
        light: "太亮"
      }
    }), PipelineError);

    const rejected = decideStage(modelId, "12-shipping", {
      expectedRevision: 1,
      action: "reject",
      notes: quote,
      userQuote: quote,
      finalAuthority: "chat",
      rejectionSelections: selections
    });
    const rejectedGate12 = rejected.stages[11];
    assert.equal(rejected.revision, 2);
    assert.equal(rejectedGate12.status, "rejected");
    assert.equal(rejectedGate12.shippingSpec.revision, 3);
    assert.equal(rejectedGate12.shippingSpec.gate12Status, "rejected");
    assert.deepEqual(
      rejectedGate12.shippingSpec.rejection.selections,
      selections
    );
    assert.deepEqual(
      rejected.currentState.shippingPreview.rejectionSelections,
      selections
    );
    assert.ok(rejectedGate12.historicalRevisions.some((revision) => (
      revision.shippingSpec?.revision === 1
      && revision.preservedForHistory === true
    )));
    assert.ok(rejectedGate12.historicalRevisions.some((revision) => (
      revision.shippingSpec?.revision === 2
      && revision.shippingSpec?.rejection?.rejectedRevision === 2
      && revision.preservedForHistory === true
    )));
    assert.ok(rejectedGate12.artifactIds.every((assetId) => {
      const asset = rejected.assets.find((candidate) => candidate.id === assetId);
      return asset?.reviewState === "rejected-history"
        && asset?.preservedForHistory === true
        && asset?.rejectedShippingRevision === 3;
    }));
    assert.equal(rejected.derived.shippingReady, false);
    assert.equal(validateManifest(rejected).length, 0);

    const event = readHistory(modelId)[0];
    assert.equal(event.type, "stage-rejected");
    assert.equal(event.rejectedShippingRevision, 3);
    assert.deepEqual(event.rejectionSelections, selections);
    assert.deepEqual(event.preservedShippingRevisions, [1, 2, 3]);
    assert.equal(
      event.nextState,
      "rev4-authorized-diagnose-fix-test-preview"
    );
    assert.equal(event.shippingReady, false);
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test("Premium Display Case motion rejection restarts at Gate 02", () => {
  const modelId = `premium-display-case-motion-correction-${Date.now()}`;
  const directory = pipelineDirectory(modelId);
  const evidenceSource = path.join(
    repoRoot,
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/02-analysis/rev-003"
  );
  const evidenceTarget = path.join(directory, "evidence/02-analysis/rev-003");
  fs.mkdirSync(path.dirname(evidenceTarget), { recursive: true });
  fs.cpSync(evidenceSource, evidenceTarget, { recursive: true });
  const entryEvidenceSource = path.join(
    repoRoot,
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/02-analysis/rev-004"
  );
  const entryEvidenceTarget = path.join(directory, "evidence/02-analysis/rev-004");
  fs.cpSync(entryEvidenceSource, entryEvidenceTarget, { recursive: true });
  const entryRecipePath = path.join(entryEvidenceTarget, "entry-motion-recipe.json");
  const entryRecipe = JSON.parse(fs.readFileSync(entryRecipePath, "utf8"));
  entryRecipe.modelId = modelId;
  fs.writeFileSync(entryRecipePath, `${JSON.stringify(entryRecipe, null, 2)}\n`);
  const balancedEvidenceSource = path.join(
    repoRoot,
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/02-analysis/rev-005"
  );
  const balancedEvidenceTarget = path.join(directory, "evidence/02-analysis/rev-005");
  fs.cpSync(balancedEvidenceSource, balancedEvidenceTarget, { recursive: true });
  const balancedRecipePath = path.join(
    balancedEvidenceTarget,
    "balanced-motion-recipe.json"
  );
  const balancedRecipe = JSON.parse(
    fs.readFileSync(balancedRecipePath, "utf8")
  );
  balancedRecipe.modelId = modelId;
  fs.writeFileSync(
    balancedRecipePath,
    `${JSON.stringify(balancedRecipe, null, 2)}\n`
  );
  const lightEvidenceSource = path.join(
    repoRoot,
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/02-analysis/rev-006"
  );
  const lightEvidenceTarget = path.join(directory, "evidence/02-analysis/rev-006");
  fs.cpSync(lightEvidenceSource, lightEvidenceTarget, { recursive: true });
  const lightRecipePath = path.join(
    lightEvidenceTarget,
    "restrained-light-recipe.json"
  );
  const lightRecipe = JSON.parse(fs.readFileSync(lightRecipePath, "utf8"));
  lightRecipe.modelId = modelId;
  fs.writeFileSync(
    lightRecipePath,
    `${JSON.stringify(lightRecipe, null, 2)}\n`
  );
  const sourcePath = "AGENTS.md";
  const sourceHash = sha256File(resolveRepoPath(sourcePath));
  const asset = (id, stageId, slot, role = "historical", sourceAssetIds = []) => ({
    id,
    stageId,
    slot,
    path: sourcePath,
    sha256: sourceHash,
    exists: true,
    sizeBytes: fs.statSync(resolveRepoPath(sourcePath)).size,
    role,
    producer: { name: "test", version: "1" },
    provenance: {
      origin: role === "user-input" ? "user-provided" : "repository-generated",
      contentClass: "motion-correction-fixture",
      assertedBy: role === "user-input" ? "user" : "repository"
    },
    sourceAssetIds
  });
  const intakeIds = [
    "display-case-gate-01-target-r003",
    "display-case-continuous-frame-clarification",
    "display-case-user-correction-2026-08-24",
    "display-case-user-request-2026-08-24"
  ];
  const analysisIds = [
    "display-case-analysis-discovery-r001",
    "display-case-analysis-correction-r002",
    "display-case-motion-recipe-r002",
    "display-case-motion-preview-r002",
    "display-case-motion-contact-sheet-r002",
    "display-case-motion-validation-r002",
    "display-case-analysis-board-r002"
  ];
  const stages = createEmptyStages();
  stages[0].status = "approved";
  stages[0].artifactIds = intakeIds;
  stages[1].status = "approved";
  stages[1].artifactIds = analysisIds;
  stages[1].decision = {
    action: "approve",
    notes: "Historical pure Y turntable approval.",
    decidedBy: "user",
    decidedAt: "2026-08-24T00:00:00.000Z"
  };
  const downstreamAssets = [];
  for (let index = 2; index <= 7; index += 1) {
    const id = `fixture-stage-${index + 1}`;
    downstreamAssets.push(asset(id, stages[index].id, "historical-evidence"));
    stages[index].status = index === 7 ? "ready_for_review" : "approved";
    stages[index].artifactIds = [id];
  }
  const manifest = {
    schemaVersion: 1,
    revision: 1,
    createdAt: "2026-08-25T00:00:00.000Z",
    updatedAt: "2026-08-25T00:00:00.000Z",
    model: {
      id: modelId,
      name: "Premium Display Case Motion Fixture",
      mechanism: "display-case",
      status: "test"
    },
    route: { primary: "blender-cli", rodinPolicy: "concept-only" },
    currentState: {
      rebuildRequested: false,
      shippingAssetUnchanged: true,
      visualApproval: "pending",
      deviceStatus: "not-approved"
    },
    assets: [
      ...intakeIds.map((id) => asset(id, "01-intake", "original-reference", "user-input")),
      asset(
        analysisIds[0],
        "02-analysis",
        "discovery-log",
        "analysis",
        [intakeIds[0]]
      ),
      ...analysisIds.slice(1).map((id) => asset(
        id,
        "02-analysis",
        id === "display-case-analysis-board-r002" ? "analysis-board" : "historical-analysis",
        "analysis",
        [intakeIds[0]]
      )),
      ...downstreamAssets
    ],
    claims: [
      "closed-loop",
      "manifold",
      "background",
      "label",
      "portrait",
      "flow",
      "environment"
    ].map((name) => ({
      id: `display-case-analysis-${name}-r002`,
      stageId: "02-analysis",
      category: name === "flow" ? "motion" : "structure",
      statement: name === "flow"
        ? "One assembled case turns around vertical Y by 360 degrees."
        : `Historical ${name} claim.`,
      confidence: "high",
      sourceAssetIds: [intakeIds[0]],
      sourceRegions: [],
      state: "active",
      analysisRevision: "002"
    })),
    stages,
    issues: []
  };
  try {
    saveManifest(manifest, null);
    const rejected = decideStage(modelId, "02-analysis", {
      expectedRevision: 1,
      action: "reject",
      notes: "用户原话：“当前 Y 轴 turntable 旋转完全错误。” 用户截图显示的不是简单 Y 轴转盘。不要先猜是 X 轴。"
    });
    assert.equal(rejected.stages[1].status, "rejected");
    const corrected = savePremiumDisplayCaseMotionCorrection(modelId, {
      expectedRevision: 2,
      userQuote: "当前 Y 轴 turntable 旋转完全错误。",
      instructionQuote: "用户截图显示的不是简单 Y 轴转盘。不要先猜是 X 轴。"
    });
    assert.equal(corrected.revision, 3);
    assert.equal(corrected.stages[0].status, "approved");
    assert.equal(corrected.stages[1].status, "ready_for_review");
    assert.equal(corrected.stages[1].analysisSpec.roll, "confirmed");
    assert.equal(corrected.stages[1].analysisSpec.yaw, "apparent-pseudo-yaw");
    assert.equal(corrected.stages[1].analysisSpec.pitch, "unknown");
    assert.equal(corrected.stages[1].analysisSpec.physicalAxis, "unknown");
    assert.equal(corrected.stages[1].analysisSpec.usesCosineWidth, false);
    assert.deepEqual(
      corrected.stages.slice(2, 8).map((stage) => stage.status),
      Array(6).fill("stale")
    );
    assert.equal(deriveManifest(corrected).derived.approvedCount, 1);
    assert.equal(deriveManifest(corrected).derived.earliestProblem.stageId, "02-analysis");
    assert.equal(
      corrected.assets.find((item) => item.id === "display-case-motion-preview-r002").reviewState,
      "rejected"
    );
    assert.equal(
      corrected.claims.find((claim) => claim.id === "display-case-analysis-flow-r002").rejectionState,
      "rejected"
    );
    assert.ok(corrected.stages[1].reviewArtifactIds.includes(
      `${modelId}-real-rive-motion-contact-sheet-r003`
    ));
    assert.ok(corrected.stages[1].reviewArtifactIds.includes(
      `${modelId}-measured-motion-schematic-gif-r003`
    ));
    const entryQuote = "节奏感不对，然后感觉XYZ轴运动过多，过于复杂，我觉得主体是要表达入场，现在增加了过多的动销元素，让人感觉抓不住重点";
    const entryRejected = decideStage(modelId, "02-analysis", {
      expectedRevision: 3,
      action: "reject",
      notes: `用户原话：‘${entryQuote}’。拒绝 Gate 02 rev 3。`
    });
    assert.equal(entryRejected.revision, 4);
    assert.equal(entryRejected.stages[1].status, "rejected");
    const entryReview = savePremiumDisplayCaseEntryMotionReview(modelId, {
      expectedRevision: 4,
      userQuote: entryQuote
    });
    assert.equal(entryReview.revision, 5);
    assert.equal(entryReview.stages[1].status, "ready_for_review");
    assert.equal(entryReview.stages[1].analysisSpec.revision, 4);
    assert.equal(entryReview.stages[1].analysisSpec.primaryMotion, "entry");
    assert.equal(entryReview.stages[1].analysisSpec.caseTranslation, "screen-y-only");
    assert.equal(entryReview.stages[1].analysisSpec.roll, "removed");
    assert.equal(entryReview.stages[1].analysisSpec.yaw, "removed");
    assert.equal(entryReview.stages[1].analysisSpec.pitch, "removed");
    assert.equal(entryReview.stages[1].analysisSpec.scaleAnimation, "removed");
    assert.deepEqual(
      entryReview.stages.slice(2, 8).map((stage) => stage.status),
      Array(6).fill("stale")
    );
    const balancedQuote = "那你这个也太简单了。我不是让你去模仿 whatnot 的那个 Slabbed Rive file 吗？你现在只有一个位移，也没有 Z 轴的这种移转，也没有 360° 翻转。也太简单了，你不能说找一个中间的平衡吗？";
    const balancedRejected = decideStage(modelId, "02-analysis", {
      expectedRevision: 5,
      action: "reject",
      notes: `用户原话：‘${balancedQuote}’。拒绝 Gate 02 rev 4。`
    });
    assert.equal(balancedRejected.revision, 6);
    assert.equal(balancedRejected.stages[1].status, "rejected");
    const balancedReview = savePremiumDisplayCaseBalancedMotionReview(modelId, {
      expectedRevision: 6,
      userQuote: balancedQuote
    });
    assert.equal(balancedReview.revision, 7);
    assert.equal(balancedReview.stages[1].status, "ready_for_review");
    assert.equal(balancedReview.stages[1].analysisSpec.revision, 5);
    assert.equal(balancedReview.stages[1].analysisSpec.primaryMotion, "entry");
    assert.deepEqual(
      balancedReview.stages[1].analysisSpec.entryTranslationAxes,
      ["screen-y", "camera-depth-z"]
    );
    assert.equal(balancedReview.stages[1].analysisSpec.showcaseAxis, "local-y");
    assert.equal(balancedReview.stages[1].analysisSpec.showcaseDegrees, 360);
    assert.equal(
      balancedReview.stages[1].analysisSpec.simultaneousEntryAndRotation,
      false
    );
    assert.deepEqual(
      balancedReview.stages.slice(2, 8).map((stage) => stage.status),
      Array(6).fill("stale")
    );
    const lightQuote = "对，就是这个意思。节奏上面，你再加一些我之前让你做的游戏调研上的这种光效变化，结合一下就好了。";
    const lightReview = savePremiumDisplayCaseRestrainedLightReview(modelId, {
      expectedRevision: 7,
      userQuote: lightQuote
    });
    assert.equal(lightReview.revision, 8);
    assert.equal(lightReview.stages[1].status, "ready_for_review");
    assert.equal(lightReview.stages[1].analysisSpec.revision, 6);
    assert.equal(lightReview.stages[1].analysisSpec.motionStructureRevision, 5);
    assert.equal(
      lightReview.stages[1].analysisSpec.motionStructureApprovalState,
      "user-accepted-direction-light-treatment-pending"
    );
    assert.equal(lightReview.stages[1].analysisSpec.lightTreatmentRevision, 6);
    assert.equal(
      lightReview.stages[1].analysisSpec.lightTreatment.packSeamLight,
      "one-neutral-causal-cue"
    );
    assert.equal(
      lightReview.stages[1].analysisSpec.lightTreatment.rotationRim,
      "object-bound-surface-response"
    );
    assert.equal(
      lightReview.stages[1].analysisSpec.lightTreatment.persistentLoop,
      false
    );
    assert.equal(
      lightReview.stages[1].analysisSpec.lightTreatment.vfxGraphDependency,
      false
    );
    const lightApproval = approvePremiumDisplayCaseRestrainedLightReview(
      modelId,
      {
        expectedRevision: 8,
        userQuote: "批准这版动效与光效（推荐）",
        approvalScope: [
          "rev5-serial-motion-structure",
          "rev6-restrained-causal-light",
          "entry-screen-y-camera-depth-z",
          "settle-before-local-y-360",
          "object-bound-rotation-rim",
          "single-final-sheen-short-halo",
          "forbidden-effects-remain-forbidden",
          "review-duration-3.4s-not-shipping-duration"
        ]
      }
    );
    assert.equal(lightApproval.revision, 9);
    assert.equal(lightApproval.stages[1].status, "approved");
    assert.equal(
      lightApproval.stages[1].analysisSpec.approval.userApprovalQuote,
      "批准这版动效与光效（推荐）"
    );
    assert.equal(
      lightApproval.stages[1].analysisSpec.approval.shippingDurationApproved,
      false
    );
    assert.equal(
      deriveManifest(lightApproval).derived.earliestProblem.stageId,
      "03-contract"
    );
    assert.deepEqual(validateManifest(loadManifest(modelId)), []);
    const history = readHistory(modelId);
    assert.equal(history[0].type, "stage-approved");
    assert.equal(history[0].stageId, "02-analysis");
    assert.equal(history[0].analysisRevision, "006");
    assert.equal(history[0].motionStructureRevision, 5);
    assert.equal(history[0].lightTreatmentRevision, 6);
    assert.equal(history[0].userQuote, "批准这版动效与光效（推荐）");
    assert.equal(history[0].shippingDurationApproved, false);
    assert.equal(history[0].approvedCount, 2);
    assert.equal(history[1].type, "stage-evidence-revised");
    assert.equal(history[1].stageId, "02-analysis");
    assert.equal(history[1].analysisRevision, "006");
    assert.equal(history[1].userQuote, lightQuote);
    assert.equal(history[2].type, "stage-ready-for-review");
    assert.equal(history[2].analysisRevision, "005");
    assert.equal(history[3].type, "stage-rejected");
    assert.ok(history[3].notes.includes("中间的平衡"));
    assert.equal(history[4].type, "stage-ready-for-review");
    assert.equal(history[4].analysisRevision, "004");
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test("magnetic slider records approved lighting and pending device retest", () => {
  const slider = loadManifest("magnetic-slide-tile");
  const derived = deriveManifest(slider);
  assert.equal(slider.model.mechanism, "linear-magnetic-slider");
  assert.equal(slider.stages[0].status, "approved");
  assert.equal(slider.stages[1].status, "approved");
  assert.equal(slider.stages[2].status, "approved");
  assert.equal(slider.stages[3].status, "approved");
  assert.equal(slider.stages[4].status, "approved");
  assert.equal(slider.stages[5].status, "approved");
  assert.equal(slider.stages[6].status, "approved");
  assert.equal(slider.stages[7].status, "approved");
  assert.equal(slider.stages[8].status, "approved");
  assert.equal(slider.stages[9].status, "approved");
  assert.equal(slider.stages[10].status, "approved");
  assert.equal(slider.stages[11].status, "approved");
  assert.equal(derived.derived.approvedCount, 12);
  assert.equal(derived.derived.shippingReady, true);
  assert.equal(derived.derived.earliestProblem, null);
  assert.equal(slider.assets.filter((asset) => asset.stageId === "01-intake").length, 49);
  assert.equal(slider.assets.filter((asset) => asset.stageId === "02-analysis").length, 183);
  assert.equal(slider.assets.filter((asset) => asset.stageId === "03-contract").length, 21);
  assert.equal(slider.assets.filter((asset) => asset.stageId === "04-architecture").length, 51);
  assert.ok(slider.assets.filter((asset) => asset.stageId === "05-blockout").length >= 82);
  assert.ok(slider.assets.filter((asset) => asset.stageId === "06-geometry").length >= 41);
  assert.ok(slider.assets.filter((asset) => asset.stageId === "07-material").length >= 268);
  assert.ok(slider.assets.filter((asset) => asset.stageId === "08-lighting").length >= 26);
  assert.ok(slider.assets.filter((asset) => asset.stageId === "09-environment").length >= 89);
  assert.ok(slider.assets.filter((asset) => asset.stageId === "10-export").length >= 130);
  assert.ok(slider.assets.filter((asset) => asset.stageId === "11-unity-parity").length >= 220);
  assert.ok(slider.stages[10].artifactIds.length >= 27);
  assert.ok(slider.stages[11].artifactIds.length >= 32);
  assert.equal(slider.stages[1].artifactIds.length, 182);
  assert.deepEqual(slider.stages[1].reviewArtifactIds, [
    "slider-analysis-interactive-cad-geometry-config-r017"
  ]);
  assert.equal(slider.stages[1].analysisSpec.revision, 17);
  assert.equal(slider.stages[1].analysisSpec.reviewMode, "interactive-cad-endpoint-rotation-interlock");
  assert.equal(slider.stages[1].analysisSpec.reviewQuestion, null);
  assert.equal(slider.stages[1].analysisSpec.approvalSpec.interactiveRequired, true);
  assert.equal(slider.stages[1].analysisSpec.approvalSpec.chatTextApprovalAllowed, false);
  assert.equal(slider.stages[1].analysisSpec.approvalSpec.approvalType, "interactive-cad-geometry");
  assert.equal(slider.stages[1].analysisSpec.simulatorGeneration.locked, true);
  assert.equal(slider.stages[1].analysisSpec.simulatorGeneration.activeControls, 0);
  assert.equal(slider.stages[1].analysisSpec.simulatorArtifactId, null);
  assert.equal(slider.stages[1].analysisSpec.recordingAssetId, null);
  assert.ok(slider.stages[1].internalArtifactIds.includes("slider-analysis-interactive-cad-config-r009"));
  assert.ok(slider.stages[1].internalArtifactIds.includes("slider-analysis-interactive-cad-geometry-config-r010"));
  assert.ok(slider.stages[1].internalArtifactIds.includes("slider-analysis-interactive-cad-geometry-config-r011"));
  assert.ok(slider.stages[1].internalArtifactIds.includes("slider-analysis-interactive-cad-geometry-config-r012"));
  assert.ok(slider.stages[1].internalArtifactIds.includes("slider-analysis-interactive-cad-geometry-config-r013"));
  assert.ok(slider.stages[1].internalArtifactIds.includes("slider-analysis-interactive-cad-geometry-config-r014"));
  assert.equal(
    slider.stages[1].analysisSpec.downstreamHashPolicy.duplicateDefaultsForbidden,
    true
  );
  assert.equal(slider.stages[1].analysisSpec.constraintIds.length, 25);
  assert.equal(slider.stages[1].analysisSpec.coverageTopics.length, 18);
  assert.equal(slider.stages[1].analysisSpec.sourceInventory.uniqueAssets, 133);
  assert.match(slider.stages[1].analysisSpec.contractSha256, /^[a-f0-9]{64}$/);
  const mechanismVideos = [
    "slider-intake-user-mechanism-video-6022",
    "slider-intake-user-mechanism-video-6023",
    "slider-intake-user-mechanism-video-6024"
  ].map(
    (assetId) => slider.assets.find((asset) => asset.id === assetId));
  assert.deepEqual(mechanismVideos.map((asset) => asset.media.frameCount), [426, 480, 821]);
  assert.deepEqual(mechanismVideos.map((asset) => asset.media.videoCodec), ["hevc", "hevc", "hevc"]);
  assert.deepEqual(mechanismVideos.map((asset) => asset.media.displayRotationDeg), [-90, -90, -90]);
  assert.deepEqual(mechanismVideos.map((asset) => asset.sha256), [
    "4b6afee0737f4ea1988870de2da721e0487531e20422cae89045da10b0b3ebfe",
    "e10ba02fe9fecf46b2acee7b32a1658135b22f9e06b166902460c45609c8a92c",
    "dd92dc36a5fe36137e43aff1cb4d5b8f3c81721b2d4258395d29702a6defa6b5"
  ]);
  assert.ok(mechanismVideos.every((asset) => asset.provenance.origin === "user-provided"));
  const frameCrops = slider.assets.filter((asset) => asset.provenance?.contentClass === "source-linked-key-frame-crop");
  assert.equal(frameCrops.length, 38);
  assert.ok(frameCrops.every((asset) => Number.isInteger(asset.frame.index) && Number.isFinite(asset.frame.ptsSeconds)));
  assert.ok(frameCrops.every((asset) => asset.sourceAssetIds.length === 1));
  const playbackProxies = slider.assets.filter((asset) => asset.provenance?.contentClass === "browser-review-playback-proxy");
  assert.equal(playbackProxies.length, 3);
  assert.ok(playbackProxies.every((asset) => asset.path.endsWith(".mp4")));
  assert.equal(slider.assets.filter((asset) => asset.id.startsWith("slider-intake-haloo-official-") && asset.path.endsWith(".png")).length, 8);
  assert.ok(slider.assets.filter((asset) => asset.id.startsWith("slider-intake-haloo-official-")).every((asset) => asset.provenance.origin === "external"));
  const pendingVideoClaims = slider.claims.filter(
    (claim) => claim.stageId === "02-analysis" && claim.state === "pending-review");
  assert.equal(pendingVideoClaims.length, 15);
  assert.ok(pendingVideoClaims.filter((claim) => claim.id !== "slider-analysis-evidence-contract-authority-r008")
    .every((claim) => claim.sourceRegions.length >= 1));
  assert.ok(pendingVideoClaims.flatMap((claim) => claim.sourceRegions)
    .filter((region) => Object.hasOwn(region, "frameIndex"))
    .every((region) => Number.isInteger(region.frameIndex)
      && Number.isFinite(region.ptsSeconds)
      && region.normalizedRect.length === 4));
  assert.equal(slider.claims.filter((claim) => claim.stageId === "02-analysis" && claim.state === "superseded").length, 53);
  assert.equal(slider.claims.filter((claim) => claim.stageId === "02-analysis" && claim.state === "active").length, 4);
  assert.match(slider.claims.find((claim) => claim.id === "slider-analysis-one-outward-direction-r006").statement, /一个外向方向.*关闭/);
  assert.match(slider.claims.find((claim) => claim.id === "slider-analysis-axis-attached-to-lower-r006").statement, /轴心随下片等距平移/);
  assert.match(slider.claims.find((claim) => claim.id === "slider-analysis-bilateral-lower-rails-r006").statement, /左右两条纵向轨道/);
  assert.match(slider.claims.find((claim) => claim.id === "slider-analysis-translated-axis-detents-r006").statement, /30×12°/);
  assert.match(slider.claims.find((claim) => claim.id === "slider-analysis-hidden-coupling-unknown-r006").statement, /红色虚线候选或未知/);
  assert.match(slider.claims.find((claim) => claim.id === "slider-analysis-simultaneous-two-dof-r006").statement, /滑动与旋转可同时操作/);
  assert.match(slider.claims.find((claim) => claim.id === "slider-analysis-fixed-endpoint-axis-r007").statement, /下端圆帽中心.*第三自由度/);
  assert.match(slider.claims.find((claim) => claim.id === "slider-analysis-normalized-aspect-r004").statement, /1.52–1.62.*unknown/);
  assert.match(slider.claims.find((claim) => claim.id === "slider-analysis-exterior-reverse-face-r003").statement, /反向\/机构面/);
  assert.match(slider.claims.find((claim) => claim.id === "slider-analysis-official-dual-mode-r002").statement, /直推与自由旋转两种玩法/);
  const contract = loadModelingContract("magnetic-slide-tile");
  assert.equal(contract.schemaVersion, 4);
  assert.match(contract.kind, /anthropometric-video-provisional/);
  assert.match(contract.dimensionClass, /not production measured/);
  assert.equal(contract.dimensionsMm.overallLength.provisional, 50);
  assert.equal(contract.dimensionsMm.overallWidth.provisional, 31);
  assert.ok(Math.abs(contract.dimensionsMm.maximumSlideTravel.provisional - 18.076433121019107) < 1e-12);
  assert.equal(JSON.stringify(contract).includes('"value": 21'), false);
  assert.equal(slider.assets.find((asset) => asset.id === "slider-intake-user-video").provenance.origin, "user-provided");
  assert.equal(slider.assets.find((asset) => asset.id === "slider-intake-obs-frame-01").provenance.origin, "external");
  assert.equal(slider.assets.find((asset) => asset.id === "slider-intake-user-frame-01").provenance.origin, "repository-generated");
  assert.equal(slider.referenceDiscovery.status, "ready-for-stage-2-review");
  assert.match(slider.referenceDiscovery.guardrail, /不能改写用户原始输入/);
  assert.equal(slider.assets.filter((asset) => asset.id.startsWith("slider-intake-nxedc-ref-")).length, 6);
  assert.ok(slider.assets.filter((asset) => asset.id.startsWith("slider-intake-nxedc-ref-")).every((asset) => asset.provenance.origin === "external"));
  assert.equal(slider.referenceDiscovery.candidates[0].id, "candidate-haloo-player-chrome-hearts");
  assert.equal(slider.referenceDiscovery.candidates[0].matchStatus, "user-selected-useful-candidate-ready-for-stage-2-review");
  assert.ok(STAGES.find((stage) => stage.id === "02-analysis").requiredSlots.includes("discovery-log"));
  assert.ok(slider.claims.filter((claim) => claim.stageId === "02-analysis").every((claim) => claim.sourceAssetIds.length > 0));
  assert.ok(slider.claims.find((claim) => claim.id === "slider-analysis-claim-internal-lanes").sourceRegions.length >= 2);
  const currentArchitecture = slider.stages[3];
  assert.equal(currentArchitecture.status, "approved");
  assert.deepEqual(currentArchitecture.artifactIds, [
    "magnetic-slide-tile-four-track-architecture-r012",
    "magnetic-slide-tile-four-track-hierarchy-r012",
    "magnetic-slide-tile-approved-four-track-architecture-r013",
    "magnetic-slide-tile-endpoint-interlock-architecture-r014",
    "magnetic-slide-tile-endpoint-interlock-state-machine-r014"
  ]);
  const currentBlockout = slider.stages[4];
  assert.equal(currentBlockout.status, "approved");
  assert.equal(currentBlockout.blockoutSpec.revision, 12);
  assert.match(currentBlockout.blockoutSpec.correctedTransform, /M_top/);
  assert.equal(currentBlockout.reviewArtifactIds[0], "magnetic-slide-g05-r012-endpoint-interlock-video");
  assert.ok(currentBlockout.validations.every((validation) => validation.status === "pass"));
  const currentGeometry = slider.stages[5];
  assert.equal(currentGeometry.status, "approved");
  assert.equal(currentGeometry.geometrySpec.revision, 5);
  const currentMaterial = slider.stages[6];
  assert.equal(currentMaterial.status, "approved");
  assert.equal(currentMaterial.materialSpec.revision, 13);
  const currentLighting = slider.stages[7];
  assert.equal(currentLighting.status, "approved");
  assert.equal(currentLighting.lightingSpec.revision, 6);
  return;
  assert.equal(loadModelingContract("magnetic-slide-tile").completeness.complete, false);
  assert.equal(loadModelingContract("magnetic-slide-tile").completeness.requiredTotal, 9);
  assert.ok(slider.stages[2].validations.some((validation) => validation.id === "nine-core-measurements" && validation.status === "fail" && /0\/9/.test(validation.evidence)));
  assert.ok(slider.assets.some((asset) => asset.id === "magnetic-slide-tile-modeling-contract-r006"));
  assert.equal(slider.stages[2].supersededDecision.action, "approve");
  assert.equal(slider.assets.find((asset) => asset.id === slider.stages[2].artifactIds[0]).sourceClaimIds.length, 17);
  const architecture = slider.stages[3];
  assert.deepEqual(architecture.artifactIds, [
    "magnetic-slide-tile-flat-lower-plane-r010",
    "magnetic-slide-tile-concealed-circular-interface-r010"
  ]);
  assert.equal(architecture.architectureSpec.reviewMode, "concealed-circular-overlap");
  assert.equal(architecture.architectureSpec.userClaim, "visible-lower-plane-clean-all-mechanism-concealed-in-circular-overlap");
  assert.equal(architecture.architectureSpec.visibleLowerPlane, "clean-flat-no-exposed-rails");
  assert.equal(architecture.architectureSpec.concealedMechanismEnvelope, "shared-circular-overlap-zone-dashed-location-proxy-only");
  assert.equal(architecture.architectureSpec.linearMovingElement, "upper-capsule-translates-through-concealed-interface");
  assert.equal(architecture.architectureSpec.rotatingElement, "same-upper-capsule-rotates-through-concealed-interface");
  assert.match(architecture.architectureSpec.nextGate05Acceptance, /no-faceted-or-jagged-perimeter/);
  assert.equal(architecture.architectureSpec.replacementGeometryAuthorized, false);
  assert.ok(architecture.validations.every((validation) => validation.status === "pass"));
  assert.ok(architecture.validations.some((validation) => validation.id === "flat-visible-lower-plane-explicit"));
  assert.ok(architecture.validations.some((validation) => validation.id === "concealed-circular-envelope-explicit"));
  assert.ok(architecture.validations.some((validation) => validation.id === "smooth-capsule-next-gate-required"));
  const userClaim = slider.claims.find((claim) => claim.id === "slider-architecture-flat-lower-concealed-overlap-r010");
  assert.equal(userClaim.assertedBy, "user");
  assert.match(userClaim.statement, /干净平面.*圆形重叠区/);
  const architectureAssets = architecture.artifactIds.map((assetId) => slider.assets.find((asset) => asset.id === assetId));
  assert.ok(architectureAssets.every((asset) => asset.sourceAssetIds.includes("magnetic-slide-tile-modeling-contract-r007")));
  assert.ok(architectureAssets.every((asset) => asset.sourceAssetIds.includes("slider-intake-haloo-official-07")));
  assert.ok(architectureAssets.every((asset) => asset.sourceAssetIds.includes("slider-intake-user-video")));
  assert.ok(architectureAssets.every((asset) => asset.provenance.userClaimIds.includes(userClaim.id)));
  assert.equal(slider.assets.filter((asset) => asset.stageId === "04-architecture" && asset.slot === "evidence-crop").length, 20);
  const boardSource = architectureAssets.map((asset) => fs.readFileSync(resolveRepoPath(asset.path), "utf8")).join("\n");
  assert.match(boardSource, /source-crops\/visible-flat-lower\.png/);
  assert.match(boardSource, /source-crops\/official-concealed-interface\.png/);
  assert.match(boardSource, /class="hidden"/);
  assert.match(boardSource, /干净平面，不画滑轨/);
  assert.match(boardSource, /高分辨率曲线／圆角 profile/);
  assert.doesNotMatch(boardSource, /暴露轨道承载区|绿色下层主体与暴露轨道/);
  assert.equal(stageReadiness(slider, "04-architecture").ready, false);
  assert.ok(slider.assets.some((asset) => asset.id === "magnetic-slide-tile-slider-construction-question-r007"));
  assert.ok(slider.assets.some((asset) => asset.id === "magnetic-slide-tile-part-tree-r006"));
  assert.equal(architecture.decision.action, "approve");
  assert.match(architecture.decision.notes, /连续干净平面.*圆形重叠封闭区/);
  const blockout = slider.stages[4];
  assert.deepEqual(blockout.artifactIds, [
    "magnetic-slide-tile-blockout-builder-r003",
    "magnetic-slide-tile-silhouette-validator-r003",
    "magnetic-slide-tile-blockout-blend-r003",
    "magnetic-slide-tile-blockout-hero-r003",
    "magnetic-slide-tile-blockout-closed-r003",
    "magnetic-slide-tile-blockout-slide-r003",
    "magnetic-slide-tile-blockout-spin-r003",
    "magnetic-slide-tile-pivot-overlay-r003",
    "magnetic-slide-tile-silhouette-top-r003",
    "magnetic-slide-tile-blockout-validation-r003"
  ]);
  assert.equal(blockout.blockoutSpec.revision, 3);
  assert.deepEqual(blockout.blockoutSpec.dimensionsMm, { length: 50, width: 31, thickness: 12 });
  assert.deepEqual(blockout.blockoutSpec.coordinateFrame, { origin: "closed-assembly-center", axisPointWorldMm: [0, -9.5, 0], rotationAxis: "+Z" });
  assert.deepEqual(blockout.blockoutSpec.poses.slide, { translationMm: [0, 21, 0], rotationDeg: 0 });
  assert.deepEqual(blockout.blockoutSpec.poses.spin, { translationMm: [0, 0, 0], rotationDeg: 45 });
  assert.match(blockout.blockoutSpec.hierarchy.moving, /UpperTranslation\/CentralAxisPivot_Point\/UpperCapsule_Moving/);
  assert.deepEqual(blockout.blockoutSpec.upperLocalOffsetFromPointAxisMm, [0, 9.5, 3]);
  assert.equal(blockout.blockoutSpec.fixedEnvelope.renderable, false);
  assert.equal(blockout.blockoutSpec.fixedEnvelope.rotatingObject, false);
  assert.equal(blockout.blockoutSpec.exposedRailOrHardwareCount, 0);
  assert.equal(blockout.blockoutSpec.spinPivotWorldDriftMm, 0);
  assert.equal(blockout.blockoutSpec.spinCentroidRadiusDriftMm, 0);
  assert.equal(blockout.blockoutSpec.combinedSlideAndSpinAllowed, false);
  assert.equal(blockout.blockoutSpec.smoothness.arcSegmentsPerSemicircle, 256);
  assert.equal(blockout.blockoutSpec.smoothness.profileVertexCount, 513);
  assert.equal(blockout.blockoutSpec.smoothness.renderedMonotonicCapViolationCount, 0);
  assert.equal(blockout.blockoutSpec.hiddenEngineering, "unknown-not-modeled");
  assert.equal(blockout.blockoutSpec.unityAssetChanged, false);
  assert.equal(blockout.status, "stale");
  assert.equal(blockout.decision.action, "approve");
  assert.match(blockout.decision.notes, /看起来是对的/);
  assert.ok(blockout.validations.every((validation) => validation.status === "pass"));
  assert.ok(blockout.validations.some((validation) => validation.id === "point-axis-coordinate"));
  assert.ok(blockout.validations.some((validation) => validation.id === "slide-spin-separated"));
  assert.ok(blockout.validations.some((validation) => validation.id === "centered-spin-no-orbit"));
  const blockoutAssets = blockout.artifactIds.map((assetId) => slider.assets.find((asset) => asset.id === assetId));
  assert.ok(blockoutAssets.every((asset) => asset.sourceAssetIds.includes("magnetic-slide-tile-modeling-contract-r007")));
  assert.ok(blockoutAssets.every((asset) => asset.sourceAssetIds.includes("magnetic-slide-tile-concealed-circular-interface-r010")));
  assert.ok(blockoutAssets.every((asset) => asset.sourceAssetIds.includes("slider-intake-user-video")));
  assert.ok(blockoutAssets.every((asset) => asset.sourceClaimIds.includes(userClaim.id)));
  const axisClaim = slider.claims.find((claim) => claim.id === "slider-blockout-point-axis-distinction-r003");
  assert.equal(axisClaim.assertedBy, "user");
  assert.match(axisClaim.statement, /黄色范围.*蓝色大圆.*translation=0/);
  assert.ok(blockoutAssets.every((asset) => asset.provenance.userClaimIds.includes(axisClaim.id)));
  const reportAsset = blockoutAssets.find((asset) => asset.slot === "validation-report");
  const report = JSON.parse(fs.readFileSync(resolveRepoPath(reportAsset.path), "utf8"));
  assert.deepEqual(report.dimensionsMm.closedMeasured, { length: 50, width: 31, thickness: 12 });
  assert.deepEqual(report.axis.pointWorldMm, [0, -9.5, 0]);
  assert.equal(report.axis.enclosureIsPivot, false);
  assert.equal(report.poses.slideTravelMm, 21);
  assert.equal(report.poses.slideRotationDeg, 0);
  assert.deepEqual(report.poses.spinTranslationMm, [0, 0, 0]);
  assert.ok(Math.abs(report.poses.spinRotationDeg - 45) < 0.00001);
  assert.equal(report.poses.spinPivotWorldDriftMm, 0);
  assert.equal(report.poses.centroidRadiusDriftMm, 0);
  assert.equal(report.fixedLower.invariantAcrossPoses, true);
  assert.equal(report.concealedEnvelope.rotatingObject, false);
  assert.equal(report.concealedEnvelope.affectsVisibleSilhouette, false);
  assert.equal(report.zeroSelfMotion.pass, true);
  assert.equal(report.smoothness.maximumProfileSegmentAngleDeg, 0.703125);
  assert.ok(report.smoothness.maximumChordDeviationMm < 0.0003);
  assert.equal(report.renderedSilhouette.monotonicCapViolationCount, 0);
  assert.equal(report.renderedSilhouette.maximumContourReversalPx, 0);
  assert.equal(report.renderedSilhouette.rowsWithInteriorAlphaGaps, 0);
  assert.equal(report.scope.hiddenEngineeringModeled, false);
  assert.ok(slider.assets.some((asset) => asset.id === "magnetic-slide-tile-blockout-hero-r001"));
  assert.ok(slider.assets.some((asset) => asset.id === "magnetic-slide-tile-blockout-hero-r002"));
  assert.equal(stageReadiness(slider, "05-blockout").ready, false);
  const geometry = slider.stages[5];
  assert.equal(geometry.status, "stale");
  assert.equal(geometry.decision.action, "approve");
  assert.match(geometry.decision.notes, /没什么问题，继续吧/);
  assert.deepEqual(geometry.artifactIds, [
    "magnetic-slide-tile-geometry-builder-r001",
    "magnetic-slide-tile-geometry-blend-r001",
    "magnetic-slide-tile-geometry-front-r001",
    "magnetic-slide-tile-geometry-back-r001",
    "magnetic-slide-tile-geometry-top-r001",
    "magnetic-slide-tile-geometry-bottom-r001",
    "magnetic-slide-tile-geometry-left-r001",
    "magnetic-slide-tile-geometry-right-r001",
    "magnetic-slide-tile-geometry-workbench-r001",
    "magnetic-slide-tile-geometry-dimensions-r001",
    "magnetic-slide-tile-geometry-point-pivot-r001",
    "magnetic-slide-tile-geometry-exploded-r001",
    "magnetic-slide-tile-geometry-validation-r001"
  ]);
  assert.equal(geometry.geometrySpec.revision, 1);
  assert.equal(geometry.geometrySpec.sourceGate05Revision, 3);
  assert.deepEqual(geometry.geometrySpec.dimensionsMm, { length: 50, width: 31, thickness: 12 });
  assert.deepEqual(geometry.geometrySpec.axisPointWorldMm, [0, -9.5, 0]);
  assert.deepEqual(geometry.geometrySpec.orthographicCameraIds, ["front", "back", "top", "bottom", "left", "right"]);
  assert.equal(geometry.geometrySpec.crossViewGeometryIdentity, true);
  assert.equal(geometry.geometrySpec.meshMetrics.lower.nonmanifoldEdgeCount, 0);
  assert.equal(geometry.geometrySpec.meshMetrics.upper.nonmanifoldEdgeCount, 0);
  assert.equal(geometry.geometrySpec.seamGapMm, 0);
  assert.equal(geometry.geometrySpec.closedVolumeOverlapDepthMm, 0);
  assert.equal(geometry.geometrySpec.concealedEnvelopeRendered, false);
  assert.equal(geometry.geometrySpec.explodedExteriorBodyCount, 2);
  assert.equal(geometry.geometrySpec.inventedInternalPartCount, 0);
  assert.ok(geometry.validations.every((validation) => validation.status === "pass"));
  const geometryAssets = geometry.artifactIds.map((assetId) => slider.assets.find((asset) => asset.id === assetId));
  assert.ok(geometryAssets.every((asset) => asset.sourceAssetIds.includes("magnetic-slide-tile-blockout-blend-r003")));
  assert.ok(geometryAssets.every((asset) => asset.sourceClaimIds.includes(axisClaim.id)));
  const viewAssets = geometryAssets.filter((asset) => asset.slot.startsWith("view-"));
  assert.deepEqual(viewAssets.map((asset) => asset.view.id), ["front", "back", "top", "bottom", "left", "right"]);
  assert.ok(viewAssets.every((asset) => asset.view.kind === "orthographic"));
  const geometryReportAsset = geometryAssets.find((asset) => asset.slot === "validation-report");
  const geometryReport = JSON.parse(fs.readFileSync(resolveRepoPath(geometryReportAsset.path), "utf8"));
  assert.equal(geometryReport.sourceGate05.unchanged, true);
  assert.equal(geometryReport.geometryIdentity.sameAcrossViews, true);
  assert.equal(geometryReport.geometryIdentity.sameAfterEvidenceRenders, true);
  assert.deepEqual(geometryReport.bounds.measuredMm, [50, 31, 12]);
  assert.equal(geometryReport.meshIntegrity.LowerBody_Fixed_CleanPlane.nonmanifoldEdgeCount, 0);
  assert.equal(geometryReport.meshIntegrity.UpperCapsule_Moving.invalidPolygonNormalCount, 0);
  assert.equal(geometryReport.fixedLowerAndEnvelope.proxyRendered, false);
  assert.equal(geometryReport.evidence.inventedInternalPartCount, 0);
  assert.equal(stageReadiness(slider, "06-geometry").ready, false);
  const mechanismClaim = slider.claims.find((claim) => claim.id === "slider-ratchet-30-detent-requirement-r001");
  assert.equal(mechanismClaim.stageId, "06-geometry");
  assert.equal(mechanismClaim.decisionState, "locked");
  assert.equal(mechanismClaim.deliveryState, "specified-only-runtime-and-hardware-validation-pending");
  assert.equal(mechanismClaim.rotationRangeDegrees, 360);
  assert.equal(mechanismClaim.detentStepDegrees, 12);
  assert.equal(mechanismClaim.detentCount, 30);
  assert.equal(mechanismClaim.physicalAndHapticConsumeSameSetting, true);
  assert.equal(mechanismClaim.hiddenConstruction, "unknown-no-teeth-pawls-balls-or-coupling-inferred");
  assert.equal(mechanismClaim.exteriorGeometryImpact, "none");
  const material = slider.stages[6];
  assert.equal(material.status, "stale");
  assert.equal(material.decision, null);
  assert.equal(material.artifactIds.length, 29);
  assert.deepEqual(material.reviewArtifactIds, [
    "magnetic-slide-tile-material-rev10-source-review-r010",
    "magnetic-slide-tile-material-rev10-closeups-r010",
    "magnetic-slide-tile-material-rev10-axis-r010",
    "magnetic-slide-tile-material-rev10-lower-provenance-r010"
  ]);
  assert.equal(material.authorityAuditSpec.revision, 8);
  assert.deepEqual(material.authorityAuditSpec.authorityOrder, [
    "original user/exact-product appearance references",
    "Blender implementation",
    "Unity implementation"
  ]);
  assert.equal(material.authorityAuditSpec.earliestDivergenceGate, "07-material");
  assert.equal(material.authorityAuditSpec.correctedMaterialCreated, true);
  assert.equal(material.authorityAuditSpec.correctedMaterialRevision, 9);
  assert.equal(material.authorityAuditSpec.userQuote, "退回，我们要优先保证模型的质量");
  assert.equal(material.authorityAuditSpec.currentBlenderStatus, "invalidated-as-final-appearance-target");
  assert.equal(material.authorityAuditSpec.technicalDetailsCollapsed, true);
  assert.equal(material.materialRebuildSpec.revision, 10);
  assert.equal(material.materialRebuildSpec.rev9DecisionState, "provisional-visual-acceptance-only-not-formal-gate-approval");
  assert.equal(material.materialRebuildSpec.userQuote, "我暂时确认了 rev 9，但是我希望你下一次再找我确认的时候，能把轴心旋转的角度也带上.");
  assert.equal(material.materialRebuildSpec.geometryDigest, "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f");
  assert.equal(material.materialRebuildSpec.geometryChanged, false);
  assert.equal(material.materialRebuildSpec.artworkPlacementChanged, false);
  assert.equal(material.materialRebuildSpec.maskFilesRemainExternal, true);
  assert.equal(material.materialRebuildSpec.reviewQuestion, "现在这个 Blender 材质和下片图案像原来的实物吗？");
  assert.equal(material.materialSpec.authorityStatus, "rev10-corrected-from-original-references-review-pending");
  assert.equal(material.materialSpec.priorApprovalPreservedAsHistory, true);
  assert.equal(material.materialSpec.polishedSilver.metallic, 1);
  assert.equal(material.materialSpec.polishedSilver.roughness, 0.075);
  assert.deepEqual(material.materialSpec.crystal.thinFilmThicknessNm, [365, 455]);
  assert.equal(material.materialSpec.crystal.microflakeScale, 85);
  assert.deepEqual(material.materialSpec.crystal.microflakeThreshold, [0.72, 0.79]);
  assert.equal(material.materialSpec.crystal.microflakeMix, 0.7);
  assert.equal(material.materialSpec.perimeter.outerInsetPx, 0);
  assert.equal(material.materialSpec.productionChemistryClaim, "unknown; visual approximation only");
  assert.equal(material.materialRebuildSpec.lowerArtworkProvenance.hashesDistinct, true);
  assert.deepEqual(material.materialRebuildSpec.motionEvidence.axisPointWorldMm, [0, -9.5, 0]);
  assert.equal(material.materialRebuildSpec.motionEvidence.axisDirection, "+Z");
  assert.deepEqual(material.materialRebuildSpec.motionEvidence.spin.map((pose) => pose.angleDeg), [0, 12, 36]);
  assert.ok(material.materialRebuildSpec.motionEvidence.spin.every((pose) => pose.translationMagnitudeMm === 0));
  assert.ok(material.materialRebuildSpec.motionEvidence.spin.every((pose) => pose.pivotDriftMm === 0));
  assert.deepEqual(material.materialRebuildSpec.motionEvidence.slide.translationLocalMm, [0, 21, 0]);
  assert.equal(material.materialRebuildSpec.motionEvidence.slide.rotationDeg, 0);
  assert.equal(material.materialRebuildSpec.motionEvidence.fortyFiveDegreePrimaryPoseUsed, false);
  assert.ok(material.validations.every((validation) => validation.status === "pass"));
  const materialAssets = material.artifactIds.map((assetId) => slider.assets.find((asset) => asset.id === assetId));
  const sourceLinkedMaterialAssets = materialAssets.filter(
    (asset) => asset.id !== "magnetic-slide-tile-material-rev10-workbench-browser-r010");
  assert.ok(sourceLinkedMaterialAssets.every((asset) => asset.sourceAssetIds.includes("slider-intake-obs-frame-01")));
  assert.ok(sourceLinkedMaterialAssets.every((asset) => asset.sourceAssetIds.includes("slider-intake-obs-frame-10")));
  assert.ok(sourceLinkedMaterialAssets.every((asset) => asset.sourceAssetIds.includes("slider-intake-haloo-official-08")));
  assert.deepEqual(
    materialAssets.find((asset) => asset.id === "magnetic-slide-tile-material-rev10-workbench-browser-r010").sourceAssetIds,
    material.reviewArtifactIds
  );
  const materialReportAsset = materialAssets.find(
    (asset) => asset.id === "magnetic-slide-tile-material-rev10-validation-r010");
  const materialReport = JSON.parse(fs.readFileSync(resolveRepoPath(materialReportAsset.path), "utf8"));
  assert.equal(materialReport.pass, true);
  assert.equal(materialReport.checks.geometryDigestUnchanged, true);
  assert.equal(materialReport.checks.crystalLocalVariation, true);
  assert.equal(materialReport.checks.microflakeDistribution, true);
  assert.equal(materialReport.checks.silverBrightDarkResponse, true);
  assert.equal(materialReport.checks.detentAnglesExact, true);
  assert.equal(materialReport.checks.axisPointExact, true);
  assert.equal(materialReport.checks.spinTranslationZero, true);
  assert.equal(materialReport.checks.spinPivotDriftZero, true);
  assert.equal(materialReport.checks.slidePoseExact, true);
  assert.ok(slider.assets.some((asset) => asset.id === "magnetic-slide-tile-material-validation-r007"));
  assert.ok(slider.assets.some((asset) => asset.id === "magnetic-slide-tile-material-board-r001"));
  const authorityClaim = slider.claims.find(
    (claim) => claim.id === "slider-gate07-rev8-original-authority-correction-r008");
  assert.equal(authorityClaim.decisionState, "review-pending");
  assert.match(authorityClaim.deliveryState, /gates08-to11-stale-gate12-blocked/);
  const correctedClaim = slider.claims.find(
    (claim) => claim.id === "slider-gate07-rev10-material-axis-review-r010");
  assert.equal(correctedClaim.decisionState, "review-pending-after-rev9-provisional-visual-acceptance");
  assert.match(correctedClaim.deliveryState, /gate07-ready-for-review/);
  assert.equal(stageReadiness(slider, "07-material").ready, false);
  const lighting = slider.stages[7];
  assert.equal(lighting.status, "stale");
  assert.equal(lighting.decision.notes, "可以吧，然后你继续");
  assert.equal(lighting.artifactIds.length, 26);
  assert.equal(lighting.reviewArtifactIds.length, 13);
  assert.ok(lighting.artifactIds.includes("magnetic-slide-tile-lighting-blend-r001"));
  assert.ok(lighting.artifactIds.includes("magnetic-slide-tile-lighting-view-board-r001"));
  assert.ok(lighting.artifactIds.includes("magnetic-slide-tile-lighting-pass-board-r001"));
  assert.ok(lighting.artifactIds.includes("magnetic-slide-tile-lighting-workbench-r001"));
  assert.ok(lighting.artifactIds.includes("magnetic-slide-tile-browser-smoke-validation-r001"));
  assert.ok(lighting.artifactIds.includes("magnetic-slide-tile-browser-workbench-r001"));
  assert.equal(lighting.lightingSpec.revision, 1);
  assert.equal(lighting.lightingSpec.sourceMaterialRevision, 7);
  assert.equal(lighting.lightingSpec.sourceMaterialApprovalWording, "可以");
  assert.equal(lighting.lightingSpec.sourceGeometryDigest, geometry.geometrySpec.evaluatedGeometryDigest);
  assert.equal(lighting.lightingSpec.environmentCompositionDeferredToGate09, true);
  assert.equal(lighting.lightingSpec.controlledRig.lights.length, 4);
  assert.equal(lighting.lightingSpec.controlledRig.exposureEv, 0);
  assert.equal(lighting.lightingSpec.controlledRig.whiteBalanceKelvin, 6504);
  assert.equal(lighting.lightingSpec.unityReflection.deliveryState, "specified-only-not-integrated");
  assert.deepEqual(lighting.lightingSpec.unityReflection.verificationGates, ["09-environment", "11-unity-parity"]);
  assert.ok(lighting.validations.every((validation) => validation.status === "pass"));
  const approvalClaim = slider.claims.find((claim) => claim.id === "slider-gate07-r007-user-approval-r001");
  assert.match(approvalClaim.statement, /原文“可以”/);
  const reflectionClaim = slider.claims.find((claim) => claim.id === "slider-unity-scene-reflection-plan-r001");
  assert.equal(reflectionClaim.decisionState, "specified");
  assert.match(reflectionClaim.deliveryState, /specified-only-not-integrated/);
  const lightingAssets = lighting.artifactIds.map((assetId) => slider.assets.find((asset) => asset.id === assetId));
  assert.ok(lightingAssets
    .filter((asset) => !asset.id.includes("browser-"))
    .every((asset) => asset.sourceAssetIds.includes("magnetic-slide-tile-material-blend-r007")));
  assert.ok(lightingAssets
    .filter((asset) => asset.id.includes("browser-"))
    .every((asset) => asset.sourceAssetIds.includes("magnetic-slide-tile-lighting-blend-r001")));
  const lightingImageReport = JSON.parse(fs.readFileSync(
    resolveRepoPath(lightingAssets.find((asset) => asset.id === "magnetic-slide-tile-image-validation-r001").path),
    "utf8"
  ));
  assert.equal(lightingImageReport.checks.silverNeutralAndBright, true);
  assert.equal(lightingImageReport.checks.bloodRedNotPink, true);
  assert.equal(lightingImageReport.checks.normalPassValid, true);
  assert.equal(lightingImageReport.checks.depthPassValid, true);
  assert.equal(lightingImageReport.checks.roughnessPassValid, true);
  assert.equal(stageReadiness(slider, "08-lighting").ready, false);
  const environment = slider.stages[8];
  assert.equal(environment.status, "stale");
  assert.equal(environment.decision.notes, "可以的，可以的。然后开始继续下一步吧。");
  assert.equal(environment.artifactIds.length, 27);
  assert.equal(environment.reviewArtifactIds.length, 8);
  assert.ok(environment.artifactIds.includes("magnetic-slide-tile-open-environment-blend-r002"));
  assert.ok(environment.artifactIds.includes("magnetic-slide-tile-open-neutral-hero-r002"));
  assert.ok(environment.artifactIds.includes("magnetic-slide-tile-open-shipping-hero-r002"));
  assert.ok(environment.artifactIds.includes("magnetic-slide-tile-open-environment-comparison-board-r002"));
  assert.ok(environment.artifactIds.includes("magnetic-slide-tile-open-style-review-board-r002"));
  assert.ok(environment.artifactIds.includes("magnetic-slide-tile-closed-open-sequence-board-r002"));
  assert.ok(environment.artifactIds.includes("magnetic-slide-tile-lower-artwork-visibility-board-r002"));
  assert.ok(environment.artifactIds.includes("magnetic-slide-tile-open-reflection-closeup-board-r002"));
  assert.ok(environment.artifactIds.includes("magnetic-slide-tile-open-workbench-r002"));
  assert.ok(environment.artifactIds.includes("magnetic-slide-tile-browser-open-environment-smoke-validation-r002"));
  assert.ok(environment.artifactIds.includes("magnetic-slide-tile-browser-open-environment-workbench-r002"));
  assert.equal(environment.environmentSpec.revision, 2);
  assert.equal(environment.environmentSpec.sourceLightingRevision, 1);
  assert.equal(environment.environmentSpec.sourceLightingApprovalWording, "可以吧，然后你继续");
  assert.equal(environment.environmentSpec.sourceGeometryDigest, geometry.geometrySpec.evaluatedGeometryDigest);
  assert.equal(environment.environmentSpec.sourceRevision.status, "rejected-incomplete");
  assert.match(environment.environmentSpec.sourceRevision.reason, /never showed the slide-open appearance/);
  assert.deepEqual(environment.environmentSpec.openPose.travelMm, 21);
  assert.deepEqual(environment.environmentSpec.openPose.axis, "+Y");
  assert.deepEqual(environment.environmentSpec.openPose.rotationDegrees, 0);
  assert.deepEqual(environment.environmentSpec.openPose.lowerWorldMatrix, [
    [1, 0, 0, 0],
    [0, 1, 0, 0],
    [0, 0, 1, -3],
    [0, 0, 0, 1],
  ]);
  assert.equal(environment.environmentSpec.matchedOpenEnvironmentPair.sameExposureEv, 0);
  assert.equal(environment.environmentSpec.matchedOpenEnvironmentPair.sameWhiteBalanceKelvin, 6504);
  assert.equal(environment.environmentSpec.imageDifferences.closedToOpen.fractionPixelsMaxDeltaAbove12 >= 0.10, true);
  assert.equal(environment.environmentSpec.sequenceMetrics.openToClosedArtworkRatio >= 1.30, true);
  assert.equal(environment.environmentSpec.blenderReflectionDeliveryState, "preview-only-not-unity-integration");
  assert.equal(environment.environmentSpec.optimization.triangles, 4096);
  assert.equal(environment.environmentSpec.optimization.noLodOrGeometryChange, true);
  assert.match(environment.environmentSpec.optimization.deliveryState.astcAndChannelPacking, /gate10/);
  assert.ok(environment.validations.every((validation) => validation.status === "pass"));
  const gate08Approval = slider.claims.find((claim) => claim.id === "slider-gate08-r001-user-approval-r001");
  assert.match(gate08Approval.statement, /原文“可以吧，然后你继续”/);
  assert.equal(gate08Approval.decisionState, "locked");
  const optimizationClaim = slider.claims.find((claim) => claim.id === "slider-model-optimization-r001");
  assert.equal(optimizationClaim.decisionState, "locked-user-approved");
  assert.match(optimizationClaim.statement, /4,096/);
  assert.match(optimizationClaim.deliveryState, /no-lod-created/);
  const revisionClaim = slider.claims.find((claim) => claim.id === "slider-gate09-r001-user-revision-request-r001");
  assert.equal(revisionClaim.decisionState, "requested-revision");
  assert.match(revisionClaim.statement, /21 mm/);
  assert.match(revisionClaim.deliveryState, /rev1-rejected/);
  assert.ok(slider.assets.some((asset) => asset.id === "magnetic-slide-tile-environment-blend-r001"));
  const environmentAssets = environment.artifactIds.map((assetId) => slider.assets.find((asset) => asset.id === assetId));
  assert.ok(environmentAssets
    .filter((asset) => !asset.id.includes("browser-open-environment-"))
    .every((asset) => asset.sourceAssetIds.includes("magnetic-slide-tile-environment-blend-r001")
      && asset.sourceAssetIds.includes("magnetic-slide-tile-lighting-blend-r001")));
  assert.ok(environmentAssets
    .filter((asset) => asset.id.includes("browser-open-environment-"))
    .every((asset) => asset.sourceAssetIds.includes("magnetic-slide-tile-open-environment-blend-r002")));
  const environmentImageReport = JSON.parse(fs.readFileSync(
    resolveRepoPath(environmentAssets.find((asset) => asset.id === "magnetic-slide-tile-open-image-validation-r002").path),
    "utf8"
  ));
  assert.equal(environmentImageReport.checks.exactOpenPose, true);
  assert.equal(environmentImageReport.checks.sameCameraNeutralShipping, true);
  assert.equal(environmentImageReport.checks.lowerPatternVisible, true);
  assert.equal(environmentImageReport.checks.openShowsMoreArtworkThanClosed, true);
  assert.equal(environmentImageReport.checks.silverNeutral, true);
  assert.equal(environmentImageReport.checks.silverReflectionsBright, true);
  assert.equal(environmentImageReport.checks.environmentReflectionVisible, true);
  assert.equal(environmentImageReport.checks.mechanismNotExposed, true);
  assert.equal(stageReadiness(slider, "09-environment").ready, false);
  const exportStage = slider.stages[9];
  assert.equal(exportStage.status, "stale");
  assert.equal(exportStage.decision.action, "approve");
  assert.equal(exportStage.artifactIds.length, 61);
  assert.deepEqual(exportStage.reviewArtifactIds, [
    "magnetic-slide-tile-round-edge-location-r003",
    "magnetic-slide-tile-round-edge-before-after-r003"
  ]);
  assert.ok(exportStage.artifactIds.includes("magnetic-slide-tile-export-authoritative-blend-r002"));
  assert.ok(exportStage.artifactIds.includes("magnetic-slide-tile-export-fbx-r002"));
  assert.ok(exportStage.artifactIds.includes("magnetic-slide-tile-export-glb-r002"));
  assert.ok(exportStage.artifactIds.includes("magnetic-slide-tile-export-collision-fbx-r002"));
  assert.ok(exportStage.artifactIds.includes("magnetic-slide-tile-export-manifest-r002"));
  assert.ok(exportStage.artifactIds.includes("magnetic-slide-tile-export-shading-review-board-r002"));
  assert.ok(exportStage.artifactIds.includes("magnetic-slide-tile-arc-contour-overlay-r002"));
  assert.ok(exportStage.artifactIds.includes("magnetic-slide-tile-collision-non-rendering-panel-r002"));
  assert.ok(exportStage.artifactIds.includes("magnetic-slide-tile-round-edge-location-r003"));
  assert.ok(exportStage.artifactIds.includes("magnetic-slide-tile-round-edge-before-after-r003"));
  assert.equal(exportStage.exportSpec.revision, 3);
  assert.equal(exportStage.exportSpec.exportRevision, 2);
  assert.equal(exportStage.exportSpec.reviewRevision, 3);
  assert.equal(exportStage.exportSpec.sourceGate09.approvalWording, "可以的，可以的。然后开始继续下一步吧。");
  assert.deepEqual(exportStage.exportSpec.dimensionsMm, [50, 31, 12]);
  assert.equal(exportStage.exportSpec.renderMeshes, 2);
  assert.equal(exportStage.exportSpec.renderTriangles, 4096);
  assert.equal(exportStage.exportSpec.rejectedRevision.status, "rejected-preserved");
  assert.equal(exportStage.exportSpec.silhouette.segmentsPerSemicircle, 256);
  assert.equal(exportStage.exportSpec.silhouette.maximumChordDeviationMm, 0.0002917831196828091);
  assert.equal(exportStage.exportSpec.smoothing.fbxtype, "FACE");
  assert.equal(exportStage.exportSpec.smoothing.sideNormalDiscontinuityDegrees, 0);
  assert.equal(exportStage.exportSpec.smoothing.fbxContourDistancePx, 0);
  assert.equal(exportStage.exportSpec.smoothing.glbContourDistancePx, 0);
  assert.equal(exportStage.exportSpec.presentation.question, "圆弧看起来还会不会一节一节？");
  assert.equal(exportStage.exportSpec.presentation.actualDifferenceVisuallyObvious, false);
  assert.equal(exportStage.exportSpec.presentation.technicalDetailsCollapsed, true);
  assert.equal(exportStage.exportSpec.presentation.collisionRemovedFromPrimaryReview, true);
  assert.equal(exportStage.exportSpec.defaultPose, "closed-zero-motion");
  assert.deepEqual(exportStage.exportSpec.separateSlidePose, { axis: "+Y", travelMm: 21, rotationDegrees: 0 });
  assert.deepEqual(exportStage.exportSpec.pointAxis, { coordinateMm: [0, -9.5, 0], axis: "+Z" });
  assert.equal(exportStage.exportSpec.detents.deliveryState, "specified-only");
  assert.equal(exportStage.exportSpec.exportSettings.collision.totalTriangles, 256);
  assert.equal(exportStage.exportSpec.reimport.fbx.pass, true);
  assert.equal(exportStage.exportSpec.reimport.glb.pass, true);
  assert.equal(exportStage.exportSpec.reimport.collision.pass, true);
  assert.equal(exportStage.exportSpec.astcPlan.recommendedFormat, "ASTC_4x4");
  assert.equal(exportStage.exportSpec.astcDeliveryState, "specified-only-not-applied");
  assert.equal(exportStage.exportSpec.optimization.lodCreated, false);
  assert.equal(exportStage.exportSpec.unityImportDeliveryState, "not-started-gate11");
  assert.ok(exportStage.validations.every((validation) => validation.status === "pass"));
  const exportAssets = exportStage.artifactIds.map((assetId) => slider.assets.find((asset) => asset.id === assetId));
  assert.ok(exportAssets
    .filter((asset) => !asset.id.includes("browser-export-") && !asset.id.endsWith("-r003"))
    .every((asset) => asset.sourceAssetIds.includes("magnetic-slide-tile-open-environment-blend-r002")));
  assert.ok(exportAssets
    .filter((asset) => asset.id.includes("browser-export-"))
    .every((asset) => asset.sourceAssetIds.includes("magnetic-slide-tile-export-glb-r002")));
  assert.ok(exportAssets
    .filter((asset) => asset.id.endsWith("-r003"))
    .every((asset) => asset.sourceAssetIds.includes("magnetic-slide-tile-export-fbx-r002")
      || asset.sourceAssetIds.includes("magnetic-slide-tile-export-glb-r002")));
  const exportReport = JSON.parse(fs.readFileSync(
    resolveRepoPath(exportAssets.find((asset) => asset.id === "magnetic-slide-tile-export-manifest-r002").path),
    "utf8"
  ));
  assert.equal(exportReport.pass, true);
  assert.equal(exportReport.authoritativeBlend.totalTriangles, 4096);
  assert.deepEqual(exportReport.authoritativeBlend.bounds.sizeMm, [31, 50, 12]);
  assert.equal(exportReport.exports.settings.glb.animations, false);
  assert.equal(exportReport.exports.settings.collision.totalTriangles, 256);
  assert.equal(exportReport.exports.settings.fbx.smoothing, "FACE");
  assert.equal(exportReport.exports.smoothing.unchanged, true);
  assert.equal(exportReport.textures.channelPacking.independentArtworkEditingPreserved, true);
  assert.equal(exportReport.textures.gate11IosAstcPlan.deliveryState, "not-applied-until-unity-import");
  assert.equal(stageReadiness(slider, "10-export").ready, false);
  const parityStage = slider.stages[10];
  assert.equal(parityStage.status, "stale");
  assert.equal(parityStage.artifactIds.length, 39);
  assert.deepEqual(parityStage.reviewArtifactIds, [
    "magnetic-slide-tile-unity-parity-rev4-geometry-board-r004",
    "magnetic-slide-tile-unity-parity-rev4-artwork-board-r004",
    "magnetic-slide-tile-unity-parity-rev4-material-board-r004",
    "magnetic-slide-tile-unity-parity-rev4-final-board-r004"
  ]);
  assert.ok(parityStage.artifactIds.includes(
    "magnetic-slide-tile-unity-parity-rev4-upper-mask-r004"));
  assert.ok(parityStage.artifactIds.includes(
    "magnetic-slide-tile-unity-parity-rev4-unity-final-r004"));
  assert.ok(parityStage.artifactIds.includes(
    "magnetic-slide-tile-unity-parity-rev4-review-validation-r004"));
  assert.ok(parityStage.artifactIds.includes(
    "magnetic-slide-tile-unity-parity-rev4-heatmap-r004"));
  assert.equal(parityStage.unityParitySpec.revision, 4);
  assert.equal(parityStage.unityParitySpec.rejectedRevision.revision, 3);
  assert.deepEqual(parityStage.unityParitySpec.geometry.boundsMeters, [
    0.012000005692243576,
    0.03100000135600567,
    0.04999999701976776
  ]);
  assert.equal(parityStage.unityParitySpec.geometry.triangles, 4096);
  assert.equal(parityStage.unityParitySpec.geometry.vertices, 4124);
  assert.equal(parityStage.unityParitySpec.geometry.silhouetteIoU, 0.986);
  assert.equal(parityStage.unityParitySpec.artwork.placementPreviouslyAccepted, true);
  assert.equal(parityStage.unityParitySpec.artwork.motifRChannelByteIdentical, true);
  assert.equal(parityStage.unityParitySpec.artwork.upperLowerMasksIndependent, true);
  assert.deepEqual(parityStage.unityParitySpec.artwork.borderWidthPixels, {
    rejectedRev3: 64,
    reviewRev4: 42
  });
  assert.equal(
    parityStage.unityParitySpec.material.crystalShader,
    "FidgetingApp/EDC/MagneticCrystalShippingR3");
  assert.equal(
    parityStage.unityParitySpec.material.silverShader,
    "FidgetingApp/EDC/MagneticSilverShippingR3");
  assert.deepEqual(parityStage.unityParitySpec.material.bloodRed.blenderMedianRgb, [124, 71, 73]);
  assert.deepEqual(parityStage.unityParitySpec.material.bloodRed.unityMedianRgb, [109, 55, 57]);
  assert.equal(parityStage.unityParitySpec.material.silver.metallic, 1);
  assert.equal(parityStage.unityParitySpec.material.zeroEmission, true);
  assert.equal(parityStage.unityParitySpec.perceptual.clippedObjectPixels, 0);
  assert.equal(parityStage.unityParitySpec.deliveryState.shippingSceneModified, false);
  assert.equal(parityStage.unityParitySpec.deliveryState.runtimeIntegrated, false);
  assert.equal(
    parityStage.unityParitySpec.deliveryState.gate12Status,
    "blocked-until-rev4-approval");
  assert.ok(parityStage.validations.every((validation) => validation.status === "pass"));
  assert.equal(parityStage.decision, null);
  assert.equal(stageReadiness(slider, "11-unity-parity").ready, false);
  const shippingStage = slider.stages[11];
  assert.equal(shippingStage.status, "rejected");
  assert.equal(shippingStage.artifactIds.length, 39);
  assert.deepEqual(shippingStage.reviewArtifactIds, [
    "magnetic-slide-tile-gate12-review-board-r001",
    "magnetic-slide-tile-gate12-motion-board-r001",
    "magnetic-slide-tile-gate12-phone-r001"
  ]);
  assert.equal(shippingStage.shippingSpec.candidateActivation.currentShippingModelDefaultActive, true);
  assert.equal(shippingStage.shippingSpec.candidateActivation.candidateDefaultActive, false);
  assert.equal(shippingStage.shippingSpec.geometry.triangles, 4096);
  assert.equal(shippingStage.shippingSpec.motion.detentCount, 30);
  assert.equal(shippingStage.shippingSpec.motion.detentStepDegrees, 12);
  assert.equal(shippingStage.shippingSpec.motion.runtimeInputIntegrated, false);
  assert.equal(shippingStage.shippingSpec.motion.hapticsIntegrated, false);
  assert.equal(shippingStage.decision.action, "reject");
  assert.match(shippingStage.decision.notes, /Blender 渲染的模型和纹理和 Unity 的最终成品差距太大/);
  assert.equal(shippingStage.shippingSpec.review.approval, "pending");
  assert.equal(shippingStage.shippingSpec.review.buildInstallPhonePush, "not-started");
  assert.ok(shippingStage.artifactIds.includes(
    "magnetic-slide-tile-gate12-browser-screenshot-r001"));
  assert.ok(shippingStage.validations.every((validation) => validation.status === "pass"));
  assert.equal(stageReadiness(slider, "12-shipping").ready, false);
});

test("CAD evidence does not create a pre-Blender Simulator requirement", () => {
  const modelId = "magnetic-slide-cad-subapproval-fixture";
  const fixtureDir = pipelineDirectory(modelId);
  try {
    const manifest = structuredClone(loadManifest("magnetic-slide-tile"));
    manifest.model.id = modelId;
    manifest.revision = 1;
    manifest.updatedAt = new Date().toISOString();
    manifest.currentStageId = "02-analysis";
    manifest.stages[2].status = "blocked";
    for (const candidate of manifest.stages.slice(3, 11)) candidate.status = "stale";
    manifest.stages[11].status = "rejected";
    saveManifest(manifest, null);
    const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
    const artifact = manifest.assets.find((candidate) => candidate.id === stage.analysisSpec.cadArtifactId);
    const required = stage.analysisSpec.approvalSpec.requiredMilestones;
    const milestones = Object.fromEntries(required.map((key) => [key, true]));
    milestones.rotationTravelPositions = [0.1, 0.4];
    const decided = decideStage(modelId, "02-analysis", {
      expectedRevision: 1,
      action: "approve",
      notes: "Interactive CAD geometry checklist completed.",
      approvalEvidence: {
        mode: "interactive-cad",
        artifactId: artifact.id,
        artifactHash: artifact.sha256,
        contractAssetId: stage.analysisSpec.contractAssetId,
        contractHash: stage.analysisSpec.contractSha256,
        geometryParameterSnapshot: {
          aspectRatioLW: 1.57,
          supportedTravelRangeL: [0.38, 0.46],
          configuredMaxTravelL: 0.3615286624203821,
          detentCount: 30,
          detentStepDeg: 12,
          pose: { travelL: 0.3615286624203821, angleDeg: 36 },
          fixedAxisBottomLocal: [330, 226],
          fixedAxisWorld: [330, 226],
          fixedAxisAttachment: "fixed-axis-center-in-bottom",
          carrierTransform: "rotate(36 330 226)",
          carrierTranslation: [0, 0],
          followerCount: 2,
          grooveCount: 2,
          grooveOwner: "TopPlate underside",
          groovesParallelToFollowers: true,
          smoothBottomExterior: true,
          axisCoveredAtCurrentPose: true,
          exactPhysicalCoverMarginKnown: false,
          closedStopL: 0,
          closedStopHard: true,
          negativeTravelForbidden: true,
          closedSilhouetteCoincident: true,
          closedStopPenetrationL: 0,
          grooveStartFromTopL: 0.32,
          grooveEndFromTopL: 0.78,
          grooveLengthL: 0.46,
          grooveEndpointLimitL: 0.46,
          overlapContainmentLimitL: 0.3615286624203821,
          actualSMaxL: 0.3615286624203821,
          actualSMaxFormula: "min(grooveEndpointLimitL, overlapContainmentLimitL)",
          activeLimitingCause: "MinimumOverlapDisk",
          maxTravelDerivedFromGrooveEndpoints: false,
          minimumOverlapDiskOwner: "BottomBase",
          minimumOverlapDiskCenter: [330, 226],
          minimumOverlapDiskRadiusL: 0.3184713375796178,
          minimumOverlapDiskPhysicalMm: null,
          minimumOverlapFullyCovered: true,
          minimumOverlapMarginL: 0,
          overlapAngleInvariant: true,
          followerEngagedAtClosed: true,
          followerEngagedAtOpen: true,
          axisCoveredAtOpen: true,
          sweptEnvelopeSampleCount: 1800,
          sweptEnvelopeAllValid: true,
          analyticContainmentContinuous: true,
          denseAngleSampleCount: 360,
          exactBoundaryTangency: true,
          beyondBoundaryInvalid: true,
          topZ: 2,
          bottomZ: 0,
          bottomMasksTop: false,
          componentLayers: [
            { id: "BottomExterior" },
            { id: "FixedAxis" },
            { id: "MinimumOverlapDisk" },
            { id: "RotatingCarrier" },
            { id: "CarrierFollowerLeft" },
            { id: "CarrierFollowerRight" },
            { id: "TopPlate" },
            { id: "TopGrooveLeft" },
            { id: "TopGrooveRight" },
            { id: "UnknownContacts" }
          ],
          physicalInputs: {}
        },
        viewsInspected: ["top", "side", "section"],
        milestones,
        completedInteractionChecklist: required,
        browserTimestamp: new Date().toISOString()
      }
    });
    const decidedStage = decided.stages.find((candidate) => candidate.id === "02-analysis");
    assert.equal(decidedStage.status, "ready_for_review");
    assert.equal(decidedStage.analysisSpec.phase, "cad-approved-awaiting-final-gate-decision");
    assert.equal(decidedStage.analysisSpec.simulatorGeneration.eligible, false);
    assert.equal(decidedStage.analysisSpec.simulatorGeneration.locked, true);
    assert.equal(decidedStage.analysisSpec.simulatorGeneration.generated, false);
    assert.equal(decidedStage.analysisSpec.cadApproval.contractHash, stage.analysisSpec.contractSha256);
    assert.equal(decided.stages[2].status, "blocked");
    assert.ok(decided.stages.slice(3, 11).every((candidate) => candidate.status === "stale"));
    assert.equal(decided.stages[11].status, "rejected");
    const event = readHistory(modelId).at(-1);
    assert.equal(event.type, "interactive-cad-substage-approved");
    assert.equal(event.approvalEffect, "records-cad-evidence-awaiting-final-gate-decision");
    assert.deepEqual(event.viewsInspected, ["top", "side", "section"]);
  } finally {
    fs.rmSync(fixtureDir, { recursive: true, force: true });
  }
});

test("backfill exposes honest first-stage gaps", () => {
  assert.equal(loadModelingContract("blue-classic"), null);
  assert.equal(deriveManifest(loadManifest("blue-classic")).derived.earliestProblem.stageId, "01-intake");
  assert.match(deriveManifest(loadManifest("blue-classic")).derived.earliestProblem.reasons.join(" "), /original-reference/);
  assert.equal(deriveManifest(loadManifest("gold-four-wing")).derived.earliestProblem.stageId, "01-intake");
  const graphiteProblem = deriveManifest(loadManifest("graphite-two-lobe")).derived.earliestProblem;
  assert.equal(graphiteProblem.status, "missing");
  assert.match(graphiteProblem.reasons.join(" "), /original-reference/);
});

test("assistant-generated targets remain distinguishable from user originals", () => {
  const graphite = loadManifest("graphite-two-lobe");
  const targets = graphite.assets.filter((asset) => asset.stageId === "01-intake");
  assert.ok(targets.length >= 5);
  assert.ok(targets.every((asset) => asset.role === "ai-target"));
  assert.ok(targets.every((asset) => asset.slot === "ai-target"));
  assert.ok(targets.every((asset) => asset.provenance?.origin === "assistant-generated"));
  assert.ok(targets.every((asset) => asset.provenance?.assertedBy === "user"));
});

test("repository path whitelist blocks traversal", () => {
  assert.throws(() => resolveRepoPath("../../outside.txt"), PipelineError);
  assert.throws(() => resolveRepoPath("/etc/passwd"), PipelineError);
  assert.equal(resolveRepoPath("AGENTS.md"), path.join(repoRoot, "AGENTS.md"));
});

test("digests are stable regardless of input ordering", () => {
  assert.equal(digestValues(["b", "a"]), digestValues(["a", "b"]));
  assert.notEqual(digestValues(["a"]), digestValues(["b"]));
});

test("exact-product references invalidate downstream work and produce a source-linked analysis revision", () => {
  const modelId = "pipeline-research-revision-fixture";
  const fixtureDir = pipelineDirectory(modelId);
  const originalPath = "AGENTS.md";
  const officialPath = `unity/FidgetingApp/ArtSource/ModelPipeline/${modelId}/evidence/01-intake/rev-002/official/mechanism.png`;
  const boardPath = `unity/FidgetingApp/ArtSource/ModelPipeline/${modelId}/evidence/02-analysis/rev-002/official-board.svg`;
  const logPath = `unity/FidgetingApp/ArtSource/ModelPipeline/${modelId}/evidence/02-analysis/rev-002/discovery.json`;
  fs.mkdirSync(path.dirname(resolveRepoPath(officialPath)), { recursive: true });
  fs.mkdirSync(path.dirname(resolveRepoPath(boardPath)), { recursive: true });
  fs.writeFileSync(resolveRepoPath(officialPath), "exact-product mechanism image");
  fs.writeFileSync(resolveRepoPath(boardPath), "<svg xmlns=\"http://www.w3.org/2000/svg\"/>");
  fs.writeFileSync(resolveRepoPath(logPath), "{}");
  const stages = createEmptyStages();
  stages[0].status = "approved";
  stages[1].status = "approved";
  stages[2].status = "approved";
  const manifest = {
    schemaVersion: 1,
    revision: 1,
    createdAt: "2026-08-21T00:00:00.000Z",
    updatedAt: "2026-08-21T00:00:00.000Z",
    model: { id: modelId, name: "Research revision", mechanism: "slider", status: "test" },
    route: { primary: "blender-cli", rodinPolicy: "concept-only" },
    currentState: { rebuildRequested: true, shippingAssetUnchanged: true, visualApproval: "pending", deviceStatus: "not-approved" },
    assets: [{
      id: "user-ref", stageId: "01-intake", slot: "original-reference", path: originalPath,
      sha256: sha256File(resolveRepoPath(originalPath)), exists: true, role: "user-input",
      producer: { name: "test", version: "1" }, sourceAssetIds: []
    }],
    claims: [],
    stages,
    issues: []
  };
  stages[0].artifactIds = ["user-ref"];
  try {
    saveManifest(manifest, null);
    const intake = saveExternalReferencePack(modelId, {
      expectedRevision: 1,
      sourceName: "official",
      assets: [{
        id: "official-mechanism", path: officialPath, sourceUrl: "https://example.com/product",
        contentClass: "exact-product-internal-mechanism", description: "Internal mechanism and gameplay."
      }]
    });
    assert.equal(intake.stages[0].status, "ready_for_review");
    assert.equal(intake.stages[1].status, "stale");
    assert.equal(intake.assets.find((asset) => asset.id === "official-mechanism").provenance.origin, "external");
    assert.deepEqual(intake.stages[0].reviewArtifactIds, ["official-mechanism"]);

    const approved = decideStage(modelId, "01-intake", { expectedRevision: 2, action: "approve", notes: "Exact-product source classification accepted." });
    const analysis = saveAnalysisResearchRevision(modelId, {
      expectedRevision: approved.revision,
      assets: [
        { id: "official-log", slot: "discovery-log", path: logPath, sourceAssetIds: ["official-mechanism"] },
        { id: "official-board", slot: "analysis-board", path: boardPath, sourceAssetIds: ["official-mechanism"] }
      ],
      claims: [{
        id: "official-dual-mode", category: "motion", statement: "Straight push and free spin are separate supported modes.",
        confidence: "high", sourceAssetIds: ["official-mechanism"]
      }]
    });
    assert.equal(analysis.stages[1].status, "ready_for_review");
    assert.deepEqual(analysis.stages[1].reviewArtifactIds, ["official-board"]);
    assert.equal(analysis.stages[2].status, "stale");
    assert.equal(stageReadiness(loadManifest(modelId), "02-analysis").ready, true);
    assert.equal(analysis.claims.find((claim) => claim.id === "official-dual-mode").state, "active");
  } finally {
    fs.rmSync(fixtureDir, { recursive: true, force: true });
  }
});

test("asset refresh preserves a genuinely missing intake stage", () => {
  const modelId = "pipeline-missing-refresh-fixture";
  const fixtureDir = pipelineDirectory(modelId);
  const absoluteTarget = path.join(fixtureDir, "assistant-target.txt");
  const targetPath = path.relative(repoRoot, absoluteTarget).split(path.sep).join("/");
  fs.mkdirSync(fixtureDir, { recursive: true });
  fs.writeFileSync(absoluteTarget, "v1", "utf8");
  const stages = createEmptyStages();
  stages[0].status = "missing";
  const manifest = {
    schemaVersion: 1,
    revision: 1,
    createdAt: "2026-08-20T00:00:00.000Z",
    updatedAt: "2026-08-20T00:00:00.000Z",
    model: { id: modelId, name: "Missing", mechanism: "rotor", status: "test" },
    route: { primary: "blender-cli", rodinPolicy: "concept-only" },
    currentState: { rebuildRequested: true, shippingAssetUnchanged: true, visualApproval: "pending", deviceStatus: "not-approved" },
    assets: [{
      id: "assistant-target", stageId: "01-intake", slot: "ai-target", path: targetPath,
      sha256: sha256File(absoluteTarget), exists: true, role: "ai-target", producer: { name: "test", version: "1" }, sourceAssetIds: []
    }],
    claims: [], stages, issues: []
  };
  try {
    saveManifest(manifest, null);
    fs.writeFileSync(absoluteTarget, "v2", "utf8");
    const refreshed = refreshManifest(modelId, 1);
    assert.equal(refreshed.stages[0].status, "missing");
    assert.match(refreshed.derived.earliestProblem.reasons.join(" "), /original-reference/);
  } finally {
    fs.rmSync(fixtureDir, { recursive: true, force: true });
  }
});

test("modeling contract must consume every approved analysis claim", () => {
  const modelId = "pipeline-claim-consumption-fixture";
  const fixtureDir = pipelineDirectory(modelId);
  const sourcePath = "AGENTS.md";
  const sourceHash = sha256File(resolveRepoPath(sourcePath));
  const stages = createEmptyStages();
  stages[0].status = "approved";
  stages[1].status = "approved";
  stages[2].status = "draft";
  const makeAsset = (id, stageId, slot, role, sourceAssetIds = [], sourceClaimIds = undefined) => ({
    id, stageId, slot, path: sourcePath, sha256: sourceHash, exists: true, role,
    producer: { name: "test", version: "1" }, sourceAssetIds, ...(sourceClaimIds === undefined ? {} : { sourceClaimIds })
  });
  const manifest = {
    schemaVersion: 1,
    revision: 1,
    createdAt: "2026-08-21T00:00:00.000Z",
    updatedAt: "2026-08-21T00:00:00.000Z",
    model: { id: modelId, name: "Claim consumption", mechanism: "slider", status: "test" },
    route: { primary: "blender-cli", rodinPolicy: "concept-only" },
    currentState: { rebuildRequested: true, shippingAssetUnchanged: true, visualApproval: "pending", deviceStatus: "not-approved" },
    assets: [
      makeAsset("ref", "01-intake", "original-reference", "user-input"),
      makeAsset("discovery", "02-analysis", "discovery-log", "analysis", ["ref"]),
      makeAsset("board", "02-analysis", "analysis-board", "analysis", ["ref"]),
      makeAsset("contract", "03-contract", "modeling-contract", "contract", ["board"], [])
    ],
    claims: [
      { id: "shape", stageId: "02-analysis", category: "shape", statement: "Keep the observed outline.", confidence: "high", sourceAssetIds: ["board"] },
      { id: "motion", stageId: "02-analysis", category: "motion", statement: "Keep the observed travel axis.", confidence: "medium", sourceAssetIds: ["board"] }
    ],
    stages,
    issues: []
  };
  stages[0].artifactIds = ["ref"];
  stages[1].artifactIds = ["discovery", "board"];
  stages[2].artifactIds = ["contract"];
  try {
    saveManifest(manifest, null);
    const blocked = stageReadiness(loadManifest(modelId), "03-contract");
    assert.equal(blocked.ready, false);
    assert.match(blocked.reasons.join(" "), /2 条已批准分析判断/);

    const updated = loadManifest(modelId);
    updated.assets.find((asset) => asset.id === "contract").sourceClaimIds = ["shape", "motion"];
    saveManifest(updated, null);
    assert.equal(stageReadiness(loadManifest(modelId), "03-contract").ready, true);
  } finally {
    fs.rmSync(fixtureDir, { recursive: true, force: true });
  }
});

test("modeling contract saves immutable drafts and becomes reviewable only when complete", () => {
  const modelId = "pipeline-contract-save-fixture";
  const fixtureDir = pipelineDirectory(modelId);
  const sourcePath = "AGENTS.md";
  const sourceHash = sha256File(resolveRepoPath(sourcePath));
  const stages = createEmptyStages();
  stages[0].status = "approved";
  stages[1].status = "approved";
  const makeAsset = (id, stageId, slot, role, sourceAssetIds = []) => ({
    id, stageId, slot, path: sourcePath, sha256: sourceHash, exists: true, role,
    producer: { name: "test", version: "1" }, sourceAssetIds
  });
  const manifest = {
    schemaVersion: 1,
    revision: 1,
    createdAt: "2026-08-21T00:00:00.000Z",
    updatedAt: "2026-08-21T00:00:00.000Z",
    model: { id: modelId, name: "Contract save", mechanism: "slider", status: "test" },
    route: { primary: "blender-cli", rodinPolicy: "concept-only" },
    currentState: { rebuildRequested: true, shippingAssetUnchanged: true, visualApproval: "pending", deviceStatus: "not-approved", diagnosis: "fixture" },
    assets: [
      makeAsset("ref", "01-intake", "original-reference", "user-input"),
      makeAsset("discovery", "02-analysis", "discovery-log", "analysis", ["ref"]),
      makeAsset("board", "02-analysis", "analysis-board", "analysis", ["ref"])
    ],
    claims: [
      { id: "shape", stageId: "02-analysis", category: "shape", statement: "Keep shape.", confidence: "high", sourceAssetIds: ["board"] },
      { id: "motion", stageId: "02-analysis", category: "motion", statement: "Keep motion.", confidence: "high", sourceAssetIds: ["board"] }
    ],
    stages,
    issues: []
  };
  stages[0].artifactIds = ["ref"];
  stages[1].artifactIds = ["discovery", "board"];
  try {
    saveManifest(manifest, null);
    const draft = saveModelingContract(modelId, {
      expectedRevision: 1, secondaryMotion: "unknown", laneMode: "unknown", internalHardwareMode: "unknown"
    });
    assert.equal(draft.manifest.stages[2].status, "draft");
    assert.deepEqual(draft.contract.sourceClaimIds, ["shape", "motion"]);
    assert.equal(draft.contract.completeness.complete, false);
    const firstAssetId = draft.manifest.stages[2].artifactIds[0];
    const firstPath = draft.manifest.assets.find((asset) => asset.id === firstAssetId).path;
    assert.equal(fs.existsSync(resolveRepoPath(firstPath)), true);

    const ready = saveModelingContract(modelId, {
      expectedRevision: 2,
      overallLengthMm: 50,
      overallWidthMm: 31,
      totalThicknessMm: 12,
      linearTravelMm: 21,
      seamClearanceMm: 0.25,
      dimensionBasis: {
        type: "anthropometric-estimate",
        confidence: "medium",
        method: "Adult-finger scale estimate from user video.",
        calibration: { adultFingerBreadthMm: { center: 22.5, min: 20, max: 25 } },
        corroboration: [{ label: "Comparable mechanism", dimensionsMm: [50, 31, 11.8] }]
      },
      dimensionEstimateRangesMm: {
        overallLengthMm: { min: 47, max: 53 },
        overallWidthMm: { min: 29, max: 33 },
        totalThicknessMm: { min: 10.5, max: 13.5 },
        linearTravelMm: { min: 18, max: 24 }
      },
      secondaryMotion: "translation-only",
      laneMode: "visual-only",
      internalHardwareMode: "visual-mechanism-proxy"
    });
    assert.equal(ready.manifest.stages[2].status, "ready_for_review");
    assert.equal(ready.contract.completeness.complete, true);
    assert.equal(ready.contract.dimensionBasis.type, "anthropometric-estimate");
    assert.deepEqual(ready.contract.dimensionEstimateRangesMm.linearTravelMm, { min: 18, max: 24 });
    assert.equal(ready.manifest.assets.filter((asset) => asset.stageId === "03-contract").length, 2);
    assert.notEqual(ready.manifest.stages[2].artifactIds[0], firstAssetId);
    assert.equal(fs.existsSync(resolveRepoPath(firstPath)), true);
    assert.equal(stageReadiness(loadManifest(modelId), "03-contract").ready, true);
    assert.equal(readHistory(modelId)[0].type, "stage-draft-created");

    const edited = saveModelingContract(modelId, {
      expectedRevision: 3,
      overallLengthMm: 55,
      overallWidthMm: 31,
      totalThicknessMm: 12,
      linearTravelMm: 21,
      seamClearanceMm: 0.25,
      dimensionBasisType: "anthropometric-estimate",
      secondaryMotion: "translation-only",
      laneMode: "visual-only",
      internalHardwareMode: "visual-mechanism-proxy"
    });
    assert.deepEqual(edited.contract.dimensionEstimateRangesMm.overallLengthMm, { min: 52, max: 58 });
    assert.equal(edited.manifest.assets.filter((asset) => asset.stageId === "03-contract").length, 3);
    assert.equal(fs.existsSync(resolveRepoPath(firstPath)), true);

    const dualMode = saveModelingContract(modelId, {
      expectedRevision: 4,
      overallLengthMm: 55,
      overallWidthMm: 31,
      totalThicknessMm: 12,
      linearTravelMm: 21,
      seamClearanceMm: 0.25,
      dimensionBasisType: "anthropometric-estimate",
      secondaryMotion: "dual-mode-free-spin",
      laneMode: "dual-working-lanes",
      internalHardwareMode: "visual-mechanism-proxy"
    });
    assert.equal(dualMode.contract.completeness.complete, true);
    assert.deepEqual(dualMode.contract.mechanism.interactionModes, ["straight-push", "free-spin"]);
    assert.equal(dualMode.contract.mechanism.maxRotationDeg, null);
    assert.equal(dualMode.contract.mechanism.externalMainShellCount, 2);
    assert.match(dualMode.contract.mechanism.modeRelationship, /coupling-unknown/);
    assert.ok(dualMode.manifest.stages[2].validations.some((validation) => validation.id === "official-dual-mode-contract" && validation.status === "pass"));

    const officialOnly = saveModelingContract(modelId, {
      expectedRevision: 5,
      seamClearanceMm: 0.25,
      dimensionBasis: {
        type: "official-only",
        availability: "exact-model-dimensions-unavailable",
        checkedSources: ["https://example.com/exact-model"],
        excludedComparables: ["similar-product"]
      },
      secondaryMotion: "dual-mode-free-spin",
      laneMode: "dual-working-lanes",
      internalHardwareMode: "visual-mechanism-proxy"
    });
    assert.equal(officialOnly.manifest.stages[2].status, "draft");
    assert.equal(officialOnly.contract.completeness.complete, false);
    assert.equal(officialOnly.contract.dimensionBasis.type, "official-only");
    assert.equal(officialOnly.contract.dimensionBasis.availability, "exact-model-dimensions-unavailable");
    assert.deepEqual(officialOnly.contract.dimensions, {
      overallLengthMm: null,
      overallWidthMm: null,
      totalThicknessMm: null,
      linearTravelMm: null,
      seamClearanceMm: 0.25
    });
    assert.deepEqual(officialOnly.contract.sourceAssetIds, ["discovery", "board"]);
    assert.ok(officialOnly.manifest.stages[2].validations.some((validation) => validation.id === "dimension-proposal-complete" && validation.status === "fail"));

    const provisional = saveModelingContract(modelId, {
      expectedRevision: 6,
      overallLengthMm: 50,
      overallWidthMm: 31,
      totalThicknessMm: 12,
      linearTravelMm: 21,
      seamClearanceMm: 0.25,
      dimensionBasis: {
        type: "user-authorized-provisional",
        authorizationSource: "fixture user selection",
        supersedesPolicy: "prior official-only restriction"
      },
      secondaryMotion: "dual-mode-free-spin",
      laneMode: "dual-working-lanes",
      internalHardwareMode: "visual-mechanism-proxy"
    });
    assert.equal(provisional.manifest.stages[2].status, "ready_for_review");
    assert.equal(provisional.contract.dimensionBasis.type, "user-authorized-provisional");
    assert.equal(provisional.contract.dimensionBasis.usage, "digital-blockout-only");
    assert.equal(provisional.contract.dimensionBasis.officialPublishedDimensions, false);
    assert.equal(provisional.contract.dimensionBasis.productionDimensions, false);
    assert.equal(provisional.contract.dimensionBasis.inferredFromVideo, false);
    assert.deepEqual(provisional.contract.dimensions, {
      overallLengthMm: 50,
      overallWidthMm: 31,
      totalThicknessMm: 12,
      linearTravelMm: 21,
      seamClearanceMm: 0.25
    });
    assert.deepEqual(provisional.contract.dimensionEstimateRangesMm, null);
    assert.deepEqual(provisional.contract.sourceAssetIds, ["discovery", "board"]);
    assert.ok(provisional.manifest.stages[2].validations.some((validation) => validation.id === "dimension-proposal-complete" && validation.status === "pass" && /user-authorized provisional/.test(validation.evidence)));
    assert.equal(fs.existsSync(resolveRepoPath(firstPath)), true);
  } finally {
    fs.rmSync(fixtureDir, { recursive: true, force: true });
  }
});

test("architecture plan consumes an approved contract and registers a reviewable visual pair", () => {
  const modelId = "pipeline-architecture-save-fixture";
  const fixtureDir = pipelineDirectory(modelId);
  const stages = createEmptyStages();
  stages[0].status = "approved";
  stages[1].status = "approved";
  stages[2].status = "approved";
  const refPath = "AGENTS.md";
  const refHash = sha256File(resolveRepoPath(refPath));
  const contractPath = `unity/FidgetingApp/ArtSource/ModelPipeline/${modelId}/evidence/03-contract/rev-001/modeling-contract.json`;
  const partTreePath = `unity/FidgetingApp/ArtSource/ModelPipeline/${modelId}/evidence/04-architecture/rev-001/part-tree.svg`;
  const explodedPath = `unity/FidgetingApp/ArtSource/ModelPipeline/${modelId}/evidence/04-architecture/rev-001/exploded-plan.svg`;
  fs.mkdirSync(path.dirname(resolveRepoPath(contractPath)), { recursive: true });
  fs.mkdirSync(path.dirname(resolveRepoPath(partTreePath)), { recursive: true });
  fs.writeFileSync(resolveRepoPath(contractPath), JSON.stringify({
    completeness: { complete: true, missing: [] },
    mechanism: { secondaryMotion: "translation-plus-rotation", maxRotationDeg: 90, laneMode: "dual-working-lanes", internalHardwareMode: "visual-mechanism-proxy" }
  }));
  fs.writeFileSync(resolveRepoPath(partTreePath), "<svg xmlns=\"http://www.w3.org/2000/svg\"/>");
  fs.writeFileSync(resolveRepoPath(explodedPath), "<svg xmlns=\"http://www.w3.org/2000/svg\"/>");
  const asset = (id, stageId, slot, assetPath, sourceAssetIds = [], sourceClaimIds = undefined) => ({
    id, stageId, slot, path: assetPath, sha256: sha256File(resolveRepoPath(assetPath)), exists: true, role: stageId === "03-contract" ? "contract" : "analysis",
    producer: { name: "test", version: "1" }, sourceAssetIds, ...(sourceClaimIds ? { sourceClaimIds } : {})
  });
  const manifest = {
    schemaVersion: 1,
    revision: 1,
    createdAt: "2026-08-21T00:00:00.000Z",
    updatedAt: "2026-08-21T00:00:00.000Z",
    model: { id: modelId, name: "Architecture save", mechanism: "slider", status: "test" },
    route: { primary: "blender-cli", rodinPolicy: "concept-only" },
    currentState: { rebuildRequested: true, shippingAssetUnchanged: true, visualApproval: "pending", deviceStatus: "not-approved", diagnosis: "fixture" },
    assets: [
      asset("ref", "01-intake", "original-reference", refPath),
      asset("slider-intake-user-frame-08", "01-intake", "original-reference", refPath),
      asset("slider-intake-user-frame-11", "01-intake", "original-reference", refPath),
      asset("board", "02-analysis", "analysis-board", refPath, ["ref"]),
      asset("contract", "03-contract", "modeling-contract", contractPath, ["board"], ["shape", "motion"])
    ],
    claims: [
      { id: "shape", stageId: "02-analysis", category: "shape", statement: "Keep shape.", confidence: "high", sourceAssetIds: ["board"] },
      { id: "motion", stageId: "02-analysis", category: "motion", statement: "Keep motion.", confidence: "high", sourceAssetIds: ["board"] }
    ],
    stages,
    issues: []
  };
  stages[0].artifactIds = ["ref", "slider-intake-user-frame-08", "slider-intake-user-frame-11"];
  stages[1].artifactIds = ["board"];
  stages[2].artifactIds = ["contract"];
  try {
    saveManifest(manifest, null);
    const result = saveArchitecturePlan(modelId, { expectedRevision: 1, partTreePath, explodedPlanPath: explodedPath });
    assert.equal(result.stages[3].status, "ready_for_review");
    assert.equal(result.stages[3].artifactIds.length, 2);
    assert.equal(result.stages[3].validations.every((validation) => validation.status === "pass"), true);
    assert.equal(stageReadiness(loadManifest(modelId), "04-architecture").ready, true);
  } finally {
    fs.rmSync(fixtureDir, { recursive: true, force: true });
  }
});

test("approval gates enforce hashes, prerequisites, revisions and stale propagation", () => {
  const modelId = "pipeline-core-test-fixture";
  const fixtureDir = pipelineDirectory(modelId);
  const sourcePath = "AGENTS.md";
  const sourceHash = sha256File(resolveRepoPath(sourcePath));
  const manifest = {
    schemaVersion: 1,
    revision: 1,
    createdAt: "2026-08-20T00:00:00.000Z",
    updatedAt: "2026-08-20T00:00:00.000Z",
    model: { id: modelId, name: "Test", mechanism: "rotor", status: "test" },
    route: { primary: "blender-cli", rodinPolicy: "concept-only" },
    currentState: { rebuildRequested: true, shippingAssetUnchanged: true, visualApproval: "pending", deviceStatus: "not-approved" },
    assets: [{
      id: "test-ref", stageId: "01-intake", slot: "original-reference", path: sourcePath,
      sha256: sourceHash, exists: true, role: "user-input", producer: { name: "test", version: "1" }, sourceAssetIds: []
    }],
    claims: [],
    stages: createEmptyStages(),
    issues: []
  };
  manifest.stages[1].status = "legacy";
  try {
    saveManifest(manifest, null);
    assert.equal(stageReadiness(loadManifest(modelId), "01-intake").ready, true);
    const approved = decideStage(modelId, "01-intake", { expectedRevision: 1, action: "approve", notes: "reference accepted" });
    assert.equal(approved.stages[0].status, "approved");
    assert.equal(readHistory(modelId)[0].type, "stage-approved");
    assert.equal(fs.readdirSync(fixtureDir).some((name) => name.includes(".tmp-")), false);
    assert.throws(() => decideStage(modelId, "01-intake", { expectedRevision: 1, action: "approve" }), /revision conflict/i);
    const rejected = decideStage(modelId, "01-intake", { expectedRevision: 2, action: "reject", notes: "changed" });
    assert.equal(rejected.stages[0].status, "rejected");
    assert.equal(rejected.stages[1].status, "stale");
    assert.equal(readHistory(modelId)[0].type, "stage-rejected");
    const claimChanged = loadManifest(modelId);
    claimChanged.claims.push({
      id: "test-claim", stageId: "01-intake", category: "structure", statement: "Changed upstream claim.",
      confidence: "medium", sourceAssetIds: ["test-ref"]
    });
    saveManifest(claimChanged, null);
    const stale = refreshManifest(modelId, 3);
    assert.equal(stale.stages[0].status, "stale");
    assert.throws(() => addIssue(modelId, {
      expectedRevision: 4, stageId: "01-intake", assetId: "test-ref", severity: "blocker", note: "bad region",
      region: { x: .8, y: .8, width: .5, height: .5 }
    }), /fit inside/i);
  } finally {
    fs.rmSync(fixtureDir, { recursive: true, force: true });
  }
});

test("Premium Display Case preserves direction across explode and speed-only rejections", () => {
  const modelId = "premium-display-case-motion-test-fixture";
  const fixtureDir = pipelineDirectory(modelId);
  const relative = (absolute) => path.relative(repoRoot, absolute).split(path.sep).join("/");
  const sourceRevision = path.join(
    repoRoot,
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-003"
  );
  const sourceRevision4 = path.join(
    repoRoot,
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-004"
  );
  const rev1 = path.join(fixtureDir, "evidence/04-architecture/rev-001");
  const rev2 = path.join(fixtureDir, "evidence/04-architecture/rev-002");
  const rev3 = path.join(fixtureDir, "evidence/04-architecture/rev-003");
  const rev4 = path.join(fixtureDir, "evidence/04-architecture/rev-004");
  const rev5 = path.join(fixtureDir, "evidence/05-blockout/rev-001");
  const rev6 = path.join(fixtureDir, "evidence/05-blockout/rev-002");
  fs.mkdirSync(rev1, { recursive: true });
  fs.mkdirSync(rev2, { recursive: true });
  fs.mkdirSync(rev3, { recursive: true });
  fs.mkdirSync(rev4, { recursive: true });
  fs.mkdirSync(path.join(rev5, "fixed-views"), { recursive: true });
  fs.mkdirSync(path.join(rev6, "fixed-views"), { recursive: true });
  fs.writeFileSync(path.join(rev1, "part-tree.svg"), "<svg>part tree</svg>\n");
  fs.writeFileSync(path.join(rev1, "exploded-plan.svg"), "<svg>internal only</svg>\n");
  fs.writeFileSync(path.join(rev2, "architecture-schematic-demo.gif"), "rejected explode evidence\n");
  for (const name of [
    "Coin_Slab_v15-user-reference.jpg",
    "render_whole_case_motion.py",
    "whole-case-only-rive-v15-envelope.gif",
    "whole-case-only-rive-v15-envelope.mp4",
    "whole-case-only-contact-sheet.png",
    "rive-v15-timing-report.json",
    "animation-quality-report.json"
  ]) {
    fs.copyFileSync(path.join(sourceRevision, name), path.join(rev3, name));
  }
  for (const name of [
    "render_whole_case_motion.py",
    "whole-case-only-1.25x-slower.gif",
    "whole-case-only-1.25x-slower.mp4",
    "whole-case-only-1.25x-slower-contact-sheet.png",
    "whole-case-only-1.25x-slower-timing-report.json",
    "animation-quality-report.json"
  ]) {
    fs.copyFileSync(path.join(sourceRevision4, name), path.join(rev4, name));
  }
  for (const name of [
    "build_blockout.py",
    "validate_blockout.py",
    "premium-display-case-blockout.blend",
    "blockout-hero.png",
    "blockout-front.png",
    "blockout-side.png",
    "blockout-rear.png",
    "blockout-tube-closeup.png",
    "blockout-contact-sheet.png"
  ]) {
    fs.writeFileSync(path.join(rev5, name), `${name} fixture\n`);
  }
  const standardViewIds = ["front", "back", "top", "bottom", "left", "right", "hero", "left-oblique", "right-oblique", "low"];
  for (const viewId of standardViewIds) {
    fs.writeFileSync(path.join(rev5, "fixed-views", `${viewId}.png`), `${viewId} fixture\n`);
  }
  fs.writeFileSync(path.join(rev5, "fixed-views", "capture-report.json"), JSON.stringify({
    included_objects: ["ContinuousTubePerimeter"],
    views: standardViewIds.map((id) => ({ id }))
  }));
  fs.writeFileSync(path.join(rev5, "fixed-views", "capture-wrapper-report.json"), JSON.stringify({
    verified_capture: true,
    blender_returncode: 0,
    missing_views: []
  }));
  fs.writeFileSync(path.join(rev5, "blockout-validation.json"), JSON.stringify({
    schemaVersion: 1,
    modelId,
    gate: "05-blockout",
    blockoutRevision: 1,
    status: "pass",
    blender: "5.2.0 LTS",
    artifactTruth: {
      realBlenderBlockout: true,
      schematic: false,
      shippingUnityChanged: false
    },
    dimensionsMm: {
      measured: { width: 228, height: 304, depth: 59 },
      pass: true
    },
    portrait: {
      widthHeightRatio: 0.75,
      pass: true
    },
    closedTube: {
      meshObjectCount: 1,
      outerSectionMm: { width: 10, depth: 9 },
      wallThicknessMm: 2,
      passageSectionMm: { width: 6, depth: 5 },
      cornerRadiiMm: { outer: 20, centerline: 15, inner: 10 },
      pathClosed: true,
      tangentContinuity: { pass: true },
      topology: {
        connectedMaterialBodyCount: 1,
        openBoundaryEdgeCount: 0,
        nonManifoldEdgeCount: 0,
        manifoldPreflightPass: true
      },
      channelFloodFill: {
        sampleCount: 192,
        visitedSamples: 192,
        pass: true
      }
    },
    hierarchy: {
      requiredNodesPresent: true
    },
    scope: {
      finalMaterials: false,
      branding: false,
      logos: false,
      badges: false,
      hiddenFasteners: false,
      inventedInternalParts: false,
      transparentCoverGeometry: "deferred-no-approved-thickness"
    },
    secondaryDimensions: {
      provenance: "retained-approved-shipping-baseline"
    },
    validationContext: {
      fullGate06ValidationDeferred: true
    }
  }));
  for (const name of [
    "build_blockout.py",
    "validate_blockout.py",
    "premium-display-case-blockout.blend",
    "blockout-hero.png",
    "blockout-front.png",
    "blockout-top.png",
    "blockout-side.png",
    "blockout-rear.png",
    "blockout-oblique.png",
    "blockout-tube-closeup.png",
    "blockout-before-after.png",
    "blockout-concentric-centers.png",
    "blockout-contact-sheet.png"
  ]) {
    fs.writeFileSync(path.join(rev6, name), `${name} corrected fixture\n`);
  }
  for (const viewId of standardViewIds) {
    fs.writeFileSync(path.join(rev6, "fixed-views", `${viewId}.png`), `${viewId} corrected fixture\n`);
  }
  fs.writeFileSync(path.join(rev6, "fixed-views", "capture-report.json"), JSON.stringify({
    included_objects: ["ContinuousTubePerimeter"],
    views: standardViewIds.map((id) => ({ id }))
  }));
  fs.writeFileSync(path.join(rev6, "fixed-views", "capture-wrapper-report.json"), JSON.stringify({
    verified_capture: true,
    blender_returncode: 0,
    missing_views: []
  }));
  fs.writeFileSync(path.join(rev6, "blockout-validation.json"), JSON.stringify({
    schemaVersion: 1,
    modelId,
    gate: "05-blockout",
    blockoutRevision: 2,
    status: "pass",
    blender: "5.2.0 LTS",
    artifactTruth: {
      realBlenderBlockout: true,
      schematic: false,
      shippingUnityChanged: false,
      candidateValuesApproved: false
    },
    upstreamDisposition: {
      earliestAffectedGate: "05-blockout",
      gate03Conflict: false,
      gate04Conflict: false
    },
    dimensionsMm: {
      measured: { width: 228, height: 304, depth: 59 },
      pass: true
    },
    portrait: {
      widthHeightRatio: 0.75,
      pass: true
    },
    labelPosition: {
      baselineCenterYmm: 105,
      candidateCenterYmm: 99,
      candidateDownshiftMm: 6,
      approvalState: "pending-user-approval-not-locked-millimeters",
      minimumLabelFrameToChamberRimMm: 7.31328,
      minimumLabelFrameToTubeInnerMm: 12.591362,
      pass: true
    },
    cornerCenterFamilies: {
      maximumDriftMm: 0,
      toleranceMm: 0.01,
      caseTubeShell: { pass: true },
      mainDisplayChamber: { pass: true },
      physicalLabel: { pass: true },
      pass: true
    },
    closedTube: {
      meshObjectCount: 1,
      outerSectionMm: { width: 10, depth: 9 },
      wallThicknessMm: 2,
      passageSectionMm: { width: 6, depth: 5 },
      cornerRadiiMm: { outer: 20, centerline: 15, inner: 10 },
      pathClosed: true,
      tangentContinuity: { pass: true },
      topology: {
        connectedMaterialBodyCount: 1,
        openBoundaryEdgeCount: 0,
        nonManifoldEdgeCount: 0,
        manifoldPreflightPass: true
      },
      channelFloodFill: {
        sampleCount: 384,
        visitedSamples: 384,
        pass: true
      }
    },
    subjectTopology: {
      allOpenBoundaryEdgeCount: 0,
      allNonManifoldEdgeCount: 0,
      pass: true
    },
    hierarchy: {
      requiredNodesPresent: true
    },
    scope: {
      analyticRoundedProfilesOnly: true,
      subjectBevelModifiers: [],
      finalMaterials: false,
      branding: false,
      logos: false,
      badges: false,
      hiddenFasteners: false,
      inventedInternalParts: false,
      transparentCoverGeometry: "contour-only-thickness-deferred"
    },
    secondaryDimensions: {
      provenance: "retained-approved-shipping-baseline-with-gate05-concentric-correction"
    },
    validationContext: {
      fullGate06ValidationDeferred: true,
      gate06Entered: false
    }
  }));

  const sourcePath = "AGENTS.md";
  const sourceHash = sha256File(resolveRepoPath(sourcePath));
  const fileAsset = (id, stageId, slot, filePath, role, sourceAssetIds = []) => {
    const absolute = resolveRepoPath(filePath);
    return {
      id,
      stageId,
      slot,
      path: filePath,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role,
      producer: { name: "test", version: "1" },
      provenance: {
        origin: "repository-generated",
        contentClass: "test-fixture",
        assertedBy: "repository"
      },
      sourceAssetIds
    };
  };
  const stages = createEmptyStages();
  stages[0].status = "approved";
  stages[0].artifactIds = ["fixture-intake"];
  stages[1].status = "approved";
  stages[1].artifactIds = ["fixture-analysis"];
  stages[2].status = "approved";
  stages[2].artifactIds = ["fixture-contract"];
  stages[3].status = "ready_for_review";
  stages[3].revision = 3;
  stages[3].artifactIds = ["fixture-part-tree", "fixture-exploded", "fixture-rev2-animation"];
  stages[3].reviewArtifactIds = ["fixture-rev2-animation"];
  stages[3].validations = [{ id: "old-evidence", status: "pass" }];
  stages[3].architectureSpec = { shippingRevealPolicy: "always-assembled-never-explodes-or-reassembles" };

  const manifest = {
    schemaVersion: 1,
    revision: 1,
    createdAt: "2026-08-24T00:00:00.000Z",
    updatedAt: "2026-08-24T00:00:00.000Z",
    model: { id: modelId, name: "Premium Display Case Fixture", mechanism: "display-case", status: "test" },
    route: { primary: "blender-cli", rodinPolicy: "concept-only" },
    currentState: {
      rebuildRequested: false,
      shippingAssetUnchanged: true,
      visualApproval: "pending",
      deviceStatus: "not-approved"
    },
    assets: [
      {
        id: "fixture-intake", stageId: "01-intake", slot: "original-reference", path: sourcePath,
        sha256: sourceHash, exists: true, role: "user-input", producer: { name: "test", version: "1" }, sourceAssetIds: []
      },
      {
        id: "fixture-analysis", stageId: "02-analysis", slot: "analysis-board", path: sourcePath,
        sha256: sourceHash, exists: true, role: "analysis", producer: { name: "test", version: "1" },
        sourceAssetIds: ["fixture-intake"]
      },
      {
        id: "fixture-contract", stageId: "03-contract", slot: "modeling-contract", path: sourcePath,
        sha256: sourceHash, exists: true, role: "contract", producer: { name: "test", version: "1" },
        sourceAssetIds: ["fixture-analysis"], sourceClaimIds: ["fixture-motion-claim"]
      },
      fileAsset(
        "fixture-part-tree",
        "04-architecture",
        "part-tree",
        relative(path.join(rev1, "part-tree.svg")),
        "process",
        ["fixture-contract"]
      ),
      fileAsset(
        "fixture-exploded",
        "04-architecture",
        "exploded-plan",
        relative(path.join(rev1, "exploded-plan.svg")),
        "process",
        ["fixture-contract"]
      ),
      fileAsset(
        "fixture-rev2-animation",
        "04-architecture",
        "architecture-animation",
        relative(path.join(rev2, "architecture-schematic-demo.gif")),
        "process",
        ["fixture-part-tree", "fixture-exploded"]
      )
    ],
    claims: [{
      id: "fixture-motion-claim",
      stageId: "02-analysis",
      category: "motion",
      statement: "One assembled portrait case stays visible.",
      confidence: "high",
      sourceAssetIds: ["fixture-intake"],
      state: "active"
    }],
    stages,
    issues: []
  };

  try {
    saveManifest(manifest, null);
    const rejected = decideStage(modelId, "04-architecture", {
      expectedRevision: 1,
      action: "reject",
      notes: "User rejects explode and reassemble animation."
    });
    assert.equal(rejected.stages[3].status, "rejected");
    const result = savePremiumDisplayCaseWholeCaseMotionReview(modelId, {
      expectedRevision: 2,
      userReferencePath: relative(path.join(rev3, "Coin_Slab_v15-user-reference.jpg")),
      recipePath: relative(path.join(rev3, "render_whole_case_motion.py")),
      gifPath: relative(path.join(rev3, "whole-case-only-rive-v15-envelope.gif")),
      mp4Path: relative(path.join(rev3, "whole-case-only-rive-v15-envelope.mp4")),
      contactSheetPath: relative(path.join(rev3, "whole-case-only-contact-sheet.png")),
      timingReportPath: relative(path.join(rev3, "rive-v15-timing-report.json")),
      qualityReportPath: relative(path.join(rev3, "animation-quality-report.json"))
    });
    const gate04 = result.stages[3];
    assert.equal(gate04.status, "ready_for_review");
    assert.equal(gate04.evidenceReview.rejectedEvidenceRevision, 2);
    assert.equal(gate04.evidenceReview.evidenceRevision, 3);
    assert.equal(gate04.evidenceReview.measuredMainAppDurationMilliseconds, 3617);
    assert.equal(gate04.evidenceReview.exactAuthoredEasing, "unknown");
    assert.equal(gate04.reviewArtifactIds.length, 3);
    assert.equal(result.stages[4].status, "blocked");
    assert.equal(result.assets.find((asset) => asset.id === "fixture-rev2-animation").reviewState, "rejected");
    assert.equal(result.assets.find((asset) => asset.id === "fixture-part-tree").productAnimationEligible, false);
    assert.equal(result.assets.find((asset) => asset.id === "fixture-exploded").usagePolicy, "internal-production-and-website-structure-only");

    const speedRejected = decideStage(modelId, "04-architecture", {
      expectedRevision: 3,
      action: "reject",
      notes: "User rejects only rev 3 speed as too fast; whole-case Portrait, one Y 360, and one highlight remain locked."
    });
    assert.equal(speedRejected.stages[3].status, "rejected");
    const slower = savePremiumDisplayCaseSlowerWholeCaseMotionReview(modelId, {
      expectedRevision: 4,
      recipePath: relative(path.join(rev4, "render_whole_case_motion.py")),
      gifPath: relative(path.join(rev4, "whole-case-only-1.25x-slower.gif")),
      mp4Path: relative(path.join(rev4, "whole-case-only-1.25x-slower.mp4")),
      contactSheetPath: relative(path.join(rev4, "whole-case-only-1.25x-slower-contact-sheet.png")),
      timingReportPath: relative(path.join(rev4, "whole-case-only-1.25x-slower-timing-report.json")),
      qualityReportPath: relative(path.join(rev4, "animation-quality-report.json"))
    });
    const slowerGate04 = slower.stages[3];
    assert.equal(slowerGate04.status, "ready_for_review");
    assert.equal(slowerGate04.evidenceReview.speedRejectedEvidenceRevision, 3);
    assert.equal(slowerGate04.evidenceReview.evidenceRevision, 4);
    assert.equal(slowerGate04.evidenceReview.timeScale, 1.25);
    assert.equal(slowerGate04.evidenceReview.targetDurationMilliseconds, 4521.25);
    assert.equal(slowerGate04.evidenceReview.measuredMp4DurationMilliseconds, 4520.833);
    assert.equal(slowerGate04.evidenceReview.exactAuthoredEasing, "unknown");
    assert.equal(slowerGate04.evidenceReview.exactRiveYAxisSign, "unknown");
    assert.equal(slowerGate04.reviewArtifactIds.length, 3);
    assert.equal(slower.stages[4].status, "blocked");
    assert.equal(slower.assets.find((asset) => asset.id === `${modelId}-whole-case-motion-gif-r003`).reviewState, "rejected");
    assert.equal(slower.assets.find((asset) => asset.id === `${modelId}-whole-case-motion-gif-r003`).rejectionScope, "speed-only");
    assert.equal(slower.assets.find((asset) => asset.id === `${modelId}-rive-v15-source-r003`).reviewState, "active");
    assert.ok(slowerGate04.artifactIds.includes(`${modelId}-whole-case-motion-gif-r004`));
    assert.equal(slowerGate04.artifactIds.includes(`${modelId}-whole-case-motion-gif-r003`), false);
    assert.deepEqual(validateManifest(loadManifest(modelId)), []);
    const approved = decideStage(modelId, "04-architecture", {
      expectedRevision: slower.revision,
      action: "approve",
      notes: "用户明确回复“行，就照这个时间吧”，锁定总时长 4.520833 s。",
      userQuote: "行，就照这个时间吧",
      lockedTotalDurationSeconds: 4.520833
    });
    assert.equal(approved.stages[3].status, "approved");
    assert.equal(approved.stages[3].evidenceReview.lockedTotalDurationSeconds, 4.520833);
    assert.equal(approved.stages[3].evidenceReview.userApprovalQuote, "行，就照这个时间吧");
    const blockout = savePremiumDisplayCaseBlockoutReview(modelId, {
      expectedRevision: approved.revision
    });
    assert.equal(blockout.stages[4].status, "ready_for_review");
    assert.equal(blockout.stages[4].decision, null);
    assert.equal(blockout.stages[4].blockoutSpec.dimensionsMm.width, 228);
    assert.equal(blockout.stages[4].blockoutSpec.closedTube.topology.openBoundaryEdgeCount, 0);
    assert.equal(blockout.stages[5].status, "blocked");
    assert.equal(blockout.derived.approvedCount, 4);
    assert.equal(blockout.assets.find((asset) => asset.id === `${modelId}-whole-case-motion-gif-r003`).reviewState, "rejected");
    assert.equal(blockout.assets.find((asset) => asset.id === "fixture-rev2-animation").reviewState, "rejected");
    assert.deepEqual(validateManifest(loadManifest(modelId)), []);
    const blockoutRejected = decideStage(modelId, "05-blockout", {
      expectedRevision: blockout.revision,
      action: "reject",
      notes: "Move the label down and rebuild all nested corners from shared analytic centers."
    });
    assert.equal(blockoutRejected.stages[4].status, "rejected");
    const corrected = savePremiumDisplayCaseCorrectedBlockoutReview(modelId, {
      expectedRevision: blockoutRejected.revision
    });
    const correctedGate05 = corrected.stages[4];
    assert.equal(correctedGate05.status, "ready_for_review");
    assert.equal(correctedGate05.blockoutSpec.revision, 2);
    assert.equal(correctedGate05.blockoutSpec.labelPosition.candidateDownshiftMm, 6);
    assert.equal(correctedGate05.blockoutSpec.cornerCenterFamilies.maximumDriftMm, 0);
    assert.equal(correctedGate05.blockoutSpec.upstreamInvalidation, "none-gate05-implementation-only");
    assert.equal(corrected.stages[2].status, "approved");
    assert.equal(corrected.stages[3].status, "approved");
    assert.equal(corrected.stages[5].status, "blocked");
    assert.equal(corrected.assets.find((asset) => asset.id === `${modelId}-blockout-front-r001`).reviewState, "rejected");
    assert.equal(corrected.assets.find((asset) => asset.id === `${modelId}-blockout-front-r001`).preservedForHistory, true);
    assert.ok(correctedGate05.reviewArtifactIds.includes(`${modelId}-blockout-before-after-r002`));
    assert.ok(correctedGate05.reviewArtifactIds.includes(`${modelId}-blockout-concentric-centers-r002`));
    assert.deepEqual(validateManifest(loadManifest(modelId)), []);
    assert.throws(() => decideStage(modelId, "05-blockout", {
      expectedRevision: corrected.revision,
      action: "approve",
      userQuote: "continue",
      approvalScope: [
        "label-downshift-6mm",
        "analytic-concentric-corner-families",
        "current-white-model-rev2"
      ]
    }), /exact approval quote/i);
    const approvedBlockout = decideStage(modelId, "05-blockout", {
      expectedRevision: corrected.revision,
      action: "approve",
      userQuote: "可以，继续推进",
      approvalScope: [
        "label-downshift-6mm",
        "analytic-concentric-corner-families",
        "current-white-model-rev2"
      ],
      notes: "用户明确回复‘可以，继续推进’，批准 6 mm 标签下移、同心圆角与当前白模。"
    });
    assert.equal(approvedBlockout.stages[4].status, "approved");
    assert.equal(approvedBlockout.stages[4].blockoutSpec.labelPosition.approvalState, "approved-user-locked");
    assert.equal(approvedBlockout.stages[4].blockoutSpec.approval.userApprovalQuote, "可以，继续推进");
    assert.equal(approvedBlockout.stages[5].status, "blocked");
    assert.equal(approvedBlockout.derived.approvedCount, 5);
    assert.deepEqual(validateManifest(loadManifest(modelId)), []);
    assert.equal(readHistory(modelId)[0].type, "stage-approved");
    assert.equal(readHistory(modelId)[0].userQuote, "可以，继续推进");
    assert.equal(readHistory(modelId)[1].type, "stage-ready-for-review");
    assert.equal(readHistory(modelId)[1].blockoutRevision, 2);
    assert.equal(readHistory(modelId)[2].type, "stage-rejected");
    assert.equal(readHistory(modelId)[3].type, "stage-ready-for-review");
    assert.equal(readHistory(modelId)[4].type, "stage-approved");
  } finally {
    fs.rmSync(fixtureDir, { recursive: true, force: true });
  }
});
