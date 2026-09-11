#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../../");
const previousContractPath = path.join(here, "../rev-011/mechanism-evidence-contract.json");
const sourceIds = [
  "slider-analysis-user-selected-bottom-base-close-r011",
  "slider-analysis-user-selected-bottom-base-context-r011",
  "slider-intake-haloo-official-07",
  "slider-intake-nxedc-ref-03",
  "slider-intake-nxedc-ref-04"
];
const userImageRegions = [
  {
    assetId: sourceIds[0],
    normalizedRect: [0.07, 0.05, 0.86, 0.89],
    note: "Smooth black bottom exterior surrounds the hidden white/silver carrier."
  },
  {
    assetId: sourceIds[1],
    normalizedRect: [0.12, 0.18, 0.75, 0.73],
    note: "Context view supports a covered pivot region and smooth user-facing bottom skin."
  }
];
const internalRegions = [
  ...userImageRegions,
  { assetId: "slider-intake-haloo-official-07", note: "Official internal overview supports a circular carrier and bilateral internal mechanism regions." },
  { assetId: "slider-intake-nxedc-ref-03", note: "External same-model candidate supports concealed internal slide structure." },
  { assetId: "slider-intake-nxedc-ref-04", note: "External internal candidate supports bilateral groove/follower interpretation." }
];
const consumers = ["interactive-cad", "blender", "unity", "haptics", "tests", "shipping-review"];
const makeConstraint = (id, value, units, state, confidence, sources, regions, decisionNote) => ({
  id,
  value,
  units,
  state,
  confidence,
  sourceAssetIds: sources,
  regions,
  decisionNote,
  downstreamConsumers: consumers
});
const contract = JSON.parse(fs.readFileSync(previousContractPath, "utf8"));
contract.revision = 12;
contract.title = "Gate 02 rev 12 · 固定轴旋转载体与顶片双槽机构证据合同";
contract.supersedesContractAssetId = "slider-analysis-mechanism-evidence-contract-r011";
contract.supersededConstraintIds = [
  "MEC-RAILS-BILATERAL-BOTTOM",
  "MEC-TOP-PLATE-MOVING",
  "MEC-TOP-UNDERSIDE-CONTACTS"
];
const removed = new Set(contract.supersededConstraintIds);
contract.constraints = contract.constraints.filter((item) => !removed.has(item.id));
const bottom = contract.constraints.find((item) => item.id === "MEC-BOTTOM-BASE-FIXED");
bottom.value = {
  transform: "identity",
  worldMotion: false,
  role: "smooth fixed bottom exterior shell",
  exteriorFront: "smooth",
  exteriorBack: "smooth",
  exposedRails: false
};
bottom.sourceAssetIds = sourceIds;
bottom.regions = internalRegions;
bottom.decisionNote = "The fixed bottom is a smooth exterior skin. No rail or groove is exposed on either user-facing bottom surface.";
const axis = contract.constraints.find((item) => item.id === "MEC-AXIS-MODULE-FIXED");
axis.value = {
  owner: "BottomExterior",
  localPosition: "constant",
  worldPosition: "constant",
  independentSlidingDof: false,
  center: "fixed",
  surroundingCarrier: "separate rotating layer"
};
axis.sourceAssetIds = sourceIds;
axis.regions = internalRegions;
axis.decisionNote = "The axis center stays fixed. The visible white/silver carrier is a separate internal layer that rotates around it.";
const compound = contract.constraints.find((item) => item.id === "MEC-COMPOUND-TRANSFORM");
compound.value = "BottomExterior=identity; FixedAxis=constant; RotatingCarrier=R_fixedAxis(theta); TopPlate=R_fixedAxis(theta)*T_local(s, restOffset); s and theta may update simultaneously";
compound.sourceAssetIds = [
  ...sourceIds,
  "slider-intake-user-mechanism-video-6024",
  "slider-intake-user-mechanism-source-metadata-r003"
];
compound.regions = internalRegions;
compound.decisionNote = "Top translation uses the carrier-local groove axis, so its screen direction rotates with theta. Carrier and top share theta.";
contract.constraints.push(
  makeConstraint(
    "MEC-ROTATING-CARRIER",
    {
      owner: "internal",
      shape: "circular-with-bilateral-side-clearance-cutouts",
      transform: "R_fixedAxis(theta)",
      translation: false,
      visibilityDuringNormalOperation: "covered-by-top"
    },
    "component and transform",
    "user-authoritative",
    "locked",
    sourceIds,
    internalRegions,
    "The white/silver circular carrier rotates around the fixed axis and leaves side clearance for the two groove followers."
  ),
  makeConstraint(
    "MEC-CARRIER-FOLLOWERS-BILATERAL",
    {
      count: 2,
      owner: "RotatingCarrier",
      sides: ["left", "right"],
      exactBallFollowerCrossSection: "unknown",
      clearance: "unknown"
    },
    "internal contact topology",
    "user-authoritative",
    "high",
    sourceIds,
    internalRegions,
    "Carrier side contacts engage the two top underside grooves. Exact follower geometry and clearance remain unknown."
  ),
  makeConstraint(
    "MEC-TOP-UNDERSIDE-GROOVES",
    {
      count: 2,
      owner: "TopPlate underside",
      type: "recessed longitudinal groove/slot",
      exteriorVisibility: false,
      parallelToCarrierFollowersAtEveryAngle: true,
      exactCrossSection: "unknown"
    },
    "internal groove topology",
    "user-authoritative",
    "locked",
    sourceIds,
    internalRegions,
    "Both grooves are recessed inside the top backside. They are not rails on the bottom exterior."
  ),
  makeConstraint(
    "MEC-TOP-CARRIER-LOCAL-TRANSLATION",
    {
      carrierAngleShared: true,
      translationAxis: "carrier/top local longitudinal groove axis",
      transformOrder: "R_fixedAxis(theta)*T_local(s)",
      simultaneousSAndTheta: true
    },
    "2-DOF transform",
    "user-authoritative",
    "locked",
    sourceIds,
    internalRegions,
    "Translation rotates with the carrier frame. It is not a fixed world-axis slide independent of theta."
  ),
  makeConstraint(
    "MEC-AXIS-COVERAGE-AT-MAX-TRAVEL",
    {
      axisMustRemainInsideTopSilhouette: true,
      appliesAtAllAllowedS: true,
      exactCoverMargin: "unknown",
      coverMarginInputRequiredForPhysicalContract: true,
      diagrammaticResidualAtEvidenceMaxL: 0.22
    },
    "normalized top silhouette",
    "user-authoritative",
    "locked",
    sourceIds.slice(0, 2),
    userImageRegions,
    "Maximum slide must preserve top coverage of the fixed axis. The 0.22L residual is a diagrammatic contour check from the current normalized drawing, not a production clearance."
  ),
  makeConstraint(
    "MEC-BOTTOM-EXTERIOR-NO-RAILS",
    { frontSkin: "smooth", backSkin: "smooth", exposedRailCount: 0, exposedGrooveCount: 0 },
    "exterior surface rule",
    "user-authoritative",
    "locked",
    sourceIds.slice(0, 2),
    userImageRegions,
    "Both user-visible and touchable bottom exterior faces stay smooth and rail-free."
  )
);
contract.coverageMatrix = contract.coverageMatrix.map((row) => {
  if (row.topic === "upper/lower/mechanism-carrier identity") return {
    topic: "bottom exterior / rotating carrier / moving top ownership",
    supports: sourceIds,
    conflicts: ["rev 11 fixed rails on bottom exterior is superseded"],
    unknowns: ["carrier thickness and exact cutout profile"]
  };
  if (row.topic === "bilateral rails/ball rows/screws") return {
    topic: "top underside twin grooves and carrier followers",
    supports: sourceIds,
    conflicts: ["rev 11 bottom-owned exposed rail interpretation is superseded"],
    unknowns: ["follower/ball cross-section", "groove depth", "clearance", "tolerance"]
  };
  if (row.topic === "endpoint pivot attachment") return {
    topic: "fixed axis and rotating carrier",
    supports: sourceIds,
    conflicts: ["translated pivot and fully fixed carrier interpretations are superseded"],
    unknowns: ["bearing stack height", "carrier-to-axis interface"]
  };
  return row;
});
contract.conclusions = [
  {
    statement: "底部外壳固定且前后光滑，外表面没有轨道",
    constraintIds: ["MEC-BOTTOM-BASE-FIXED", "MEC-BOTTOM-EXTERIOR-NO-RAILS"],
    confidence: "high",
    sourceCount: 2
  },
  {
    statement: "轴心固定；圆形内部载体绕轴旋转但不平移",
    constraintIds: ["MEC-AXIS-MODULE-FIXED", "MEC-ROTATING-CARRIER"],
    confidence: "high",
    sourceCount: 5
  },
  {
    statement: "顶片背面有两条内凹纵向槽，载体左右随动件与其接触",
    constraintIds: ["MEC-TOP-UNDERSIDE-GROOVES", "MEC-CARRIER-FOLLOWERS-BILATERAL"],
    confidence: "high",
    sourceCount: 5
  },
  {
    statement: "顶片与载体共享角度，沿旋转后的局部槽轴滑动",
    constraintIds: ["MEC-COMPOUND-TRANSFORM", "MEC-TOP-CARRIER-LOCAL-TRANSLATION"],
    confidence: "high",
    sourceCount: 5
  },
  {
    statement: "任何允许行程都必须由顶片覆盖固定轴心",
    constraintIds: ["MEC-AXIS-COVERAGE-AT-MAX-TRAVEL", "MEC-TRAVEL-NORMALIZED"],
    confidence: "high",
    sourceCount: 2
  },
  {
    statement: "随动件、槽截面、盖轴余量和制造公差仍未知",
    constraintIds: ["MEC-CARRIER-FOLLOWERS-BILATERAL", "MEC-TOP-UNDERSIDE-GROOVES", "MEC-PHYSICAL-DIMENSIONS"],
    confidence: "medium",
    sourceCount: 5
  }
];
contract.unknowns = [
  "carrier follower/ball geometry and cross-section",
  "top underside groove depth, width and end profile",
  "carrier side cutout exact profile",
  "minimum physical cover margin over fixed axis",
  "thickness, stack height, gap, clearance and tolerance",
  "exact force, magnet, spring and friction values"
];
contract.downstreamPolicy.rule = "Every CAD and later artifact must record this rev 12 contract SHA-256. CAD approval unlocks only a separate Simulator; Simulator approval is required before Blender.";
contract.reviewQuestion = null;
const contractPath = path.join(here, "mechanism-evidence-contract.json");
fs.writeFileSync(contractPath, `${JSON.stringify(contract, null, 2)}\n`);
const contractHash = sha256File(contractPath);
const config = {
  schemaVersion: 1,
  modelId: "magnetic-slide-tile",
  gate: "02-analysis",
  revision: 12,
  contractAssetId: "slider-analysis-mechanism-evidence-contract-r012",
  contractSha256: contractHash,
  evidenceSelectors: {
    aspectRatioLW: "MEC-SILHOUETTE-ASPECT.value.aspectRatioLW.midpoint",
    maxTravelL: "MEC-TRAVEL-NORMALIZED.value.supportedRange.max",
    observedPeakTravelL: "MEC-TRAVEL-NORMALIZED.value.observedPeak",
    detentStepDeg: "MEC-DETENTS.value.stepDegrees",
    detentCount: "MEC-DETENTS.value.countPerRevolution",
    bottomExterior: "MEC-BOTTOM-EXTERIOR-NO-RAILS.value",
    fixedAxis: "MEC-AXIS-MODULE-FIXED.value",
    rotatingCarrier: "MEC-ROTATING-CARRIER.value",
    carrierFollowers: "MEC-CARRIER-FOLLOWERS-BILATERAL.value",
    topGrooves: "MEC-TOP-UNDERSIDE-GROOVES.value",
    topTransform: "MEC-TOP-CARRIER-LOCAL-TRANSLATION.value",
    axisCoverage: "MEC-AXIS-COVERAGE-AT-MAX-TRAVEL.value"
  },
  diagrammaticGeometry: {
    axisNormalizedY: 0.32,
    carrierRadiusL: 0.23,
    carrierSideCutoutHalfWidthL: 0.08,
    followerOffsetXL: 0.18,
    grooveOffsetXL: 0.18,
    grooveStartYL: -0.34,
    grooveEndYL: 0.34
  },
  componentLayers: [
    "BottomExterior",
    "FixedAxis",
    "RotatingCarrier",
    "CarrierFollowerLeft",
    "CarrierFollowerRight",
    "TopPlate",
    "TopGrooveLeft",
    "TopGrooveRight",
    "UnknownContacts"
  ],
  cadApprovalChecklist: [
    "pointerDirection",
    "fixedAxis",
    "rotatingCarrier",
    "topUndersideGrooves",
    "compoundMotion",
    "pivotCoverage",
    "smoothBottomExterior",
    "sourceMapping"
  ],
  approvalRule: {
    interactiveRequired: true,
    approvalType: "interactive-cad-geometry",
    chatTextApprovalAllowed: false,
    staticScreenshotApprovalAllowed: false,
    requiredArtifactHash: true,
    requiredContractHash: true,
    requiredGeometrySnapshot: true,
    requiredBrowserTimestamp: true,
    approvalEffect: "records-cad-subapproval-only-simulator-remains-separate-and-locked"
  },
  simulator: { locked: true, label: "交互 CAD 批准后生成", activeControls: 0 }
};
const configPath = path.join(here, "interactive-cad-geometry-config.json");
fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`);

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 133) throw new Error(`Expected revision 133, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 11) throw new Error("Gate 02 rev 11 must be active.");
const timestamp = new Date().toISOString();
const addAsset = ({ id, filePath, role, contentClass, note, sourceAssetIds }) => {
  const asset = {
    id,
    stageId: "02-analysis",
    slot: "analysis-evidence",
    path: path.relative(repoRoot, filePath).split(path.sep).join("/"),
    sha256: sha256File(filePath),
    exists: true,
    sizeBytes: fs.statSync(filePath).size,
    role,
    producer: { name: "fidgeting-model-pipeline", version: "2026-08-26", recipe: "Gate 02 rev 12 rotating-carrier/top-groove CAD correction" },
    provenance: { origin: "repository-generated", contentClass, assertedBy: "assistant", note },
    sourceAssetIds,
    mechanismEvidenceContractSha256: contractHash
  };
  manifest.assets.push(asset);
  stage.artifactIds.push(id);
  return asset;
};
const contractAsset = addAsset({
  id: "slider-analysis-mechanism-evidence-contract-r012",
  filePath: contractPath,
  role: "analysis",
  contentClass: "authoritative-machine-readable-mechanism-evidence-contract",
  note: "Rev 12 supersedes bottom-owned rails with a fixed smooth bottom, rotating internal carrier and top-underside grooves.",
  sourceAssetIds: sourceIds
});
const configAsset = addAsset({
  id: "slider-analysis-interactive-cad-geometry-config-r012",
  filePath: configPath,
  role: "analysis",
  contentClass: "contract-driven-interactive-cad-geometry-config",
  note: "CAD-only rotating-carrier/top-groove configuration with no Simulator controls.",
  sourceAssetIds: [contractAsset.id]
});
addAsset({
  id: "slider-analysis-carrier-groove-cad-registrar-r012",
  filePath: fileURLToPath(import.meta.url),
  role: "process",
  contentClass: "deterministic-carrier-groove-contract-and-cad-registrar",
  note: "Builds and registers the immutable rev 12 contract and CAD configuration.",
  sourceAssetIds: sourceIds
});
for (const priorId of ["slider-analysis-mechanism-evidence-contract-r011", "slider-analysis-interactive-cad-geometry-config-r011"]) {
  const prior = manifest.assets.find((asset) => asset.id === priorId);
  prior.provenance = {
    ...prior.provenance,
    disposition: "superseded-internal",
    supersededBy: priorId.includes("contract")
      ? "slider-analysis-mechanism-evidence-contract-r012"
      : "slider-analysis-interactive-cad-geometry-config-r012"
  };
  stage.internalArtifactIds = [...new Set([...(stage.internalArtifactIds || []), priorId])];
}
for (const claim of manifest.claims.filter((item) => [
  "slider-analysis-bottom-fixed-ownership-r011",
  "slider-analysis-fixed-axis-no-third-dof-r011"
].includes(item.id))) {
  claim.state = "superseded";
  claim.decisionState = "superseded";
  claim.supersededBy = "slider-analysis-carrier-groove-ownership-r012";
}
manifest.claims.push({
  id: "slider-analysis-carrier-groove-ownership-r012",
  stageId: "02-analysis",
  category: "mechanism-ownership",
  statement: "BottomExterior 与 FixedAxis 固定；RotatingCarrier 绕固定轴旋转；TopPlate 与载体共享 θ，并沿载体局部轴 s 滑动；双槽属于 TopPlate 底面。",
  confidence: "locked",
  state: "pending-review",
  decisionState: "pending-review",
  sourceAssetIds: sourceIds,
  sourceRegions: internalRegions,
  unknowns: ["随动件截面", "顶片槽截面", "载体开槽轮廓", "盖轴最小余量"]
});
stage.reviewArtifactIds = [configAsset.id];
stage.status = "ready_for_review";
stage.staleReason = null;
stage.readiness = { ready: true, blockers: [], note: "Complete eight carrier/groove CAD checks. Simulator stays locked." };
stage.analysisSpec = {
  ...stage.analysisSpec,
  revision: 12,
  priorRevisionDisposition: "rev11-bottom-owned-rails-and-fixed-carrier-rejected-and-superseded",
  phase: "interactive-cad-approval",
  reviewMode: "interactive-cad-rotating-carrier-top-grooves",
  contractAssetId: contractAsset.id,
  contractSha256: contractHash,
  constraintIds: contract.constraints.map((item) => item.id),
  coverageTopics: contract.coverageMatrix.map((item) => item.topic),
  sourceInventory: contract.sourceInventory.counts,
  cadArtifactId: configAsset.id,
  cadConfigAssetId: configAsset.id,
  simulatorArtifactId: null,
  simulatorConfigAssetId: null,
  recordingAssetId: null,
  hierarchy: Object.fromEntries(config.componentLayers.map((id) => [id, {
    parent: ["FixedAxis", "RotatingCarrier"].includes(id) ? "BottomExterior"
      : id.startsWith("CarrierFollower") ? "RotatingCarrier"
        : id.startsWith("TopGroove") || id === "UnknownContacts" ? "TopPlate"
          : null,
    transform: id === "BottomExterior" || id === "FixedAxis" ? "identity"
      : id === "RotatingCarrier" || id.startsWith("CarrierFollower") ? "R_fixedAxis(theta)"
        : "R_fixedAxis(theta)*T_local(s)"
  }])),
  cadGeneration: {
    locked: false,
    scope: "web-kinematic-cad-only-no-simulator-blender-unity",
    configSource: configAsset.id,
    contractSource: contractAsset.id,
    duplicateDefaultsForbidden: true
  },
  simulatorGeneration: { locked: true, unlockRequires: "interactive-cad-subapproval-record", label: "交互 CAD 批准后生成", activeControls: 0 },
  approvalSpec: {
    ...config.approvalRule,
    requiredMilestones: config.cadApprovalChecklist,
    approvalButtonLabel: "确认交互 CAD",
    approvalApiRequired: true
  },
  reviewQuestion: null
};
stage.validations.push({
  id: "carrier-groove-ownership-r012",
  status: "pass",
  evidence: "Rev 12 contract supersedes bottom-owned rails and fixed-world-axis translation with rotating-carrier-local top translation."
});
for (const downstream of manifest.stages.slice(2, 11)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 02 rev 12 carrier/groove CAD awaits in-workbench subapproval; separate Simulator has not started.";
}
manifest.stages[11].status = "rejected";
manifest.stages[11].staleReason = "Gate 02 CAD and Simulator approvals are incomplete; shipping remains rejected.";
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev12-carrier-groove-interactive-cad-subapproval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 12 uses a fixed smooth bottom and fixed axis, rotating internal carrier, and moving top with underside grooves. Simulator and all downstream generation remain locked.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-carrier-groove-review-ready",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 12,
  priorRevisionDisposition: "rev11-rejected-and-superseded",
  sourceAssetIds: sourceIds,
  contractAssetId: contractAsset.id,
  contractHash,
  cadArtifactId: configAsset.id,
  cadArtifactHash: configAsset.sha256,
  requiredMilestones: config.cadApprovalChecklist,
  simulatorState: "locked-not-generated",
  blenderUnityBuildInstallPhone: "not-started"
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  stageRevision: 12,
  contractHash,
  cadArtifactHash: configAsset.sha256
}, null, 2));
