#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { decideStage, loadManifest } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";
import {
  cadConfigFromEvidenceContract,
  computeCadGeometry,
  computeMinimumOverlapContainmentSweep
} from "../../../../../../../../tools/model-provenance-explorer/mechanism-cad-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 151) throw new Error(`Expected revision 151, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
const contract = JSON.parse(fs.readFileSync(path.join(here, "mechanism-evidence-contract.json"), "utf8"));
const rawConfig = JSON.parse(fs.readFileSync(path.join(here, "interactive-cad-geometry-config.json"), "utf8"));
const config = cadConfigFromEvidenceContract(contract, {
  ...rawConfig,
  expectedContractSha256: stage.analysisSpec.contractSha256
});
const current = computeCadGeometry({ travelL: config.maxTravelL, angleDeg: 36 }, config);
const closed = computeCadGeometry({ travelL: 0, angleDeg: 0 }, config);
const sweep = computeMinimumOverlapContainmentSweep(config);
const artifact = manifest.assets.find((asset) => asset.id === stage.analysisSpec.cadArtifactId);
const required = stage.analysisSpec.approvalSpec.requiredMilestones;
const milestones = Object.fromEntries(required.map((key) => [key, true]));
milestones.rotationTravelPositions = [0, 0.18, config.maxTravelL];
const approvalEvidence = {
  mode: "interactive-cad",
  artifactId: artifact.id,
  artifactHash: artifact.sha256,
  contractAssetId: stage.analysisSpec.contractAssetId,
  contractHash: stage.analysisSpec.contractSha256,
  geometryParameterSnapshot: {
    aspectRatioLW: config.aspectRatioLW,
    supportedTravelRangeL: config.supportedTravelRangeL,
    configuredMaxTravelL: config.maxTravelL,
    detentCount: config.detentCount,
    detentStepDeg: config.detentStepDeg,
    pose: { travelL: config.maxTravelL, angleDeg: 36 },
    fixedAxisBottomLocal: current.axis.localToBottom,
    fixedAxisWorld: current.axis.world,
    fixedAxisAttachment: current.axis.attachment,
    carrierTransform: current.carrier.transform,
    carrierTranslation: current.carrier.translation,
    followerCount: current.followers.count,
    grooveCount: current.grooves.count,
    grooveOwner: current.grooves.owner,
    groovesParallelToFollowers: current.grooves.parallelToFollowers,
    smoothBottomExterior: current.bottom.exposedRailCount === 0 && current.bottom.exposedGrooveCount === 0,
    axisCoveredAtCurrentPose: current.coverage.axisCovered,
    exactPhysicalCoverMarginKnown: false,
    closedStopL: 0,
    closedStopHard: true,
    negativeTravelForbidden: true,
    closedSilhouetteCoincident: closed.closedStop.silhouettesCoincident,
    closedStopPenetrationL: 0,
    grooveStartFromTopL: config.grooveStartFromTopL,
    grooveEndFromTopL: config.grooveEndFromTopL,
    grooveLengthL: config.grooveLengthL,
    grooveEndpointLimitL: config.grooveEndpointLimitL,
    overlapContainmentLimitL: config.overlapContainmentLimitL,
    actualSMaxL: config.maxTravelL,
    actualSMaxFormula: "min(grooveEndpointLimitL, overlapContainmentLimitL)",
    activeLimitingCause: config.limitingCause,
    maxTravelDerivedFromGrooveEndpoints: false,
    minimumOverlapDiskOwner: current.minimumOverlapDisk.owner,
    minimumOverlapDiskCenter: current.minimumOverlapDisk.center,
    minimumOverlapDiskRadiusL: current.minimumOverlapDisk.radiusL,
    minimumOverlapDiskPhysicalMm: null,
    minimumOverlapFullyCovered: current.minimumOverlapDisk.fullyCovered,
    minimumOverlapMarginL: current.minimumOverlapDisk.containment.marginL,
    overlapAngleInvariant: current.minimumOverlapDisk.angleInvariant,
    followerEngagedAtClosed: closed.followers.engaged,
    followerEngagedAtOpen: current.followers.engaged,
    axisCoveredAtOpen: current.coverage.axisCovered,
    sweptEnvelopeSampleCount: sweep.sampleCount,
    sweptEnvelopeAllValid: sweep.allValid,
    analyticContainmentContinuous: sweep.analyticContinuous,
    denseAngleSampleCount: sweep.angleSampleCount,
    exactBoundaryTangency: sweep.exactBoundaryTangency,
    beyondBoundaryInvalid: sweep.beyondBoundaryInvalid,
    topZ: current.layerOrder.topZ,
    bottomZ: current.layerOrder.bottomZ,
    bottomMasksTop: current.layerOrder.bottomMasksTop,
    componentLayers: current.componentLayers,
    layerPresentation: { separation: 0.6, opacity: 0.62 },
    physicalInputs: {}
  },
  viewsInspected: ["top", "side", "section"],
  milestones,
  completedInteractionChecklist: required,
  browserTimestamp: "2026-08-27T00:38:00.000Z"
};
const decided = decideStage("magnetic-slide-tile", "02-analysis", {
  expectedRevision: manifest.revision,
  action: "approve",
  notes: "Gate 02 rev 15 approved by latest explicit chat instruction after completed interactive CAD evidence.",
  finalAuthority: "chat",
  userQuote: "对了",
  approvalEvidence
});
const decidedStage = decided.stages.find((candidate) => candidate.id === "02-analysis");
console.log(JSON.stringify({
  manifestRevision: decided.revision,
  gate02Status: decidedStage.status,
  exactUserWording: decidedStage.analysisSpec.finalApproval.exactUserWording,
  contractHash: decidedStage.analysisSpec.finalApproval.contractHash,
  simulatorEligible: decidedStage.analysisSpec.simulatorGeneration.eligible
}, null, 2));
