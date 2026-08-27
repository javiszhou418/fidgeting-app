#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../../");
const previousContractPath = path.join(here, "../rev-008/mechanism-evidence-contract.json");
const sourcePaths = [
  "/Users/jiawei.zhou/.cursor/projects/Users-jiawei-zhou-Documents-Fidgeting-app/assets/image-dc8771e3-7d01-49c2-9bb3-9c7931bf901e.png",
  "/Users/jiawei.zhou/.cursor/projects/Users-jiawei-zhou-Documents-Fidgeting-app/assets/image-1f1c131a-26a7-4298-9dbc-0a89bccc782f.png"
];
const archivedPaths = [
  path.join(here, "user-selected-bottom-base-close.png"),
  path.join(here, "user-selected-bottom-base-context.png")
];
const sourceIds = [
  "slider-analysis-user-selected-bottom-base-close-r011",
  "slider-analysis-user-selected-bottom-base-context-r011"
];
for (let index = 0; index < sourcePaths.length; index += 1) {
  if (!fs.existsSync(sourcePaths[index])) throw new Error(`Missing supplied image: ${sourcePaths[index]}`);
  fs.copyFileSync(sourcePaths[index], archivedPaths[index]);
}

const consumers = ["interactive-cad", "blender", "unity", "haptics", "tests", "shipping-review"];
const regions = {
  closeBase: {
    assetId: sourceIds[0],
    normalizedRect: [0.07, 0.05, 0.86, 0.89],
    note: "Black capsule bottom base and both long rail regions are visible."
  },
  closeAxis: {
    assetId: sourceIds[0],
    normalizedRect: [0.39, 0.24, 0.34, 0.36],
    note: "Separate white/silver carrier and central bearing/axis module are visible."
  },
  contextBase: {
    assetId: sourceIds[1],
    normalizedRect: [0.12, 0.18, 0.75, 0.73],
    note: "Wider view confirms the black capsule base, bilateral rails and embedded axis module."
  }
};
const constraint = (id, value, units, state, confidence, sourceAssetIds, sourceRegions, decisionNote) => ({
  id,
  value,
  units,
  state,
  confidence,
  sourceAssetIds,
  regions: sourceRegions,
  decisionNote,
  downstreamConsumers: consumers
});

const contract = JSON.parse(fs.readFileSync(previousContractPath, "utf8"));
contract.revision = 11;
contract.title = "Gate 02 rev 11 · 固定底座与固定轴机构证据合同";
contract.supersedesContractAssetId = "slider-analysis-mechanism-evidence-contract-r008";
contract.supersededConstraintIds = [
  "MEC-PLATE-UPPER-FIXED",
  "MEC-PLATE-LOWER-MOVING",
  "MEC-PIVOT-ENDPOINT-ATTACHMENT",
  "MEC-RAILS-BILATERAL-LOWER-REVERSE"
];
contract.sourceInventory.assetIds.push(...sourceIds);
contract.sourceInventory.groups.userSelectedBottomBaseImages = [...sourceIds];
contract.sourceInventory.counts.uniqueAssets = contract.sourceInventory.assetIds.length;
contract.sourceInventory.counts.userSelectedBottomBaseImages = 2;
const removedIds = new Set(contract.supersededConstraintIds);
contract.constraints = contract.constraints.filter((item) => !removedIds.has(item.id));
const compound = contract.constraints.find((item) => item.id === "MEC-COMPOUND-TRANSFORM");
compound.value = "BottomBase=identity; AxisModule=constant child of BottomBase; TopPlate=T(s along fixed bottom rails)*R(theta about fixed bottom-axis); s and theta may update simultaneously";
compound.sourceAssetIds = [...new Set([...compound.sourceAssetIds, ...sourceIds])];
compound.regions = [regions.closeBase, regions.closeAxis, regions.contextBase];
compound.decisionNote = "User-authoritative correction: the bottom and axis stay fixed while the top owns both translation and rotation.";
contract.constraints.push(
  constraint(
    "MEC-BOTTOM-BASE-FIXED",
    { transform: "identity", worldMotion: false, role: "black capsule mechanism carrier" },
    "transform ownership",
    "user-authoritative",
    "locked",
    sourceIds,
    [regions.closeBase, regions.contextBase],
    "The pictured black capsule carrier is the fixed bottom base."
  ),
  constraint(
    "MEC-AXIS-MODULE-FIXED",
    {
      owner: "BottomBase",
      localPosition: "constant",
      worldPosition: "constant",
      independentSlidingDof: false,
      bearingAxis: "fixed",
      surroundingCarrierRotationState: "unknown"
    },
    "bottom-local and world transform",
    "user-authoritative",
    "locked",
    sourceIds,
    [regions.closeAxis, regions.contextBase],
    "The axis point is embedded in BottomBase and remains fixed locally and in the CAD world frame. The surrounding white/silver carrier may appear rotatable, but evidence does not prove which subpart rotates."
  ),
  constraint(
    "MEC-TOP-PLATE-MOVING",
    { ownerOfTranslation: true, ownerOfRotation: true, undersideContacts: "unknown" },
    "transform ownership",
    "user-authoritative",
    "locked",
    sourceIds,
    [regions.closeBase, regions.contextBase],
    "The top plate is the active plate. Its hidden underside contacts remain unknown."
  ),
  constraint(
    "MEC-RAILS-BILATERAL-BOTTOM",
    { count: 2, owner: "BottomBase", sides: ["left", "right"], crossSection: "unknown", ballCoupling: "unknown" },
    "visible regions",
    "user-authoritative",
    "locked",
    sourceIds,
    [regions.closeBase, regions.contextBase],
    "Both long rail regions are fixed children of BottomBase. Exact section and ball/follower coupling are unknown."
  ),
  constraint(
    "MEC-AXIS-PROJECTED-POSITION",
    { normalizedYFromTopRange: [0.29, 0.35], diagrammaticMidpoint: 0.32, physicalPosition: "unknown" },
    "image-projected L",
    "inferred",
    "medium",
    sourceIds,
    [regions.closeAxis, regions.contextBase],
    "The two perspective images place the visible axis near 0.29–0.35L from the top of the pictured base. This is diagrammatic image evidence, not a physical dimension."
  ),
  constraint(
    "MEC-TOP-UNDERSIDE-CONTACTS",
    { geometry: "unknown", display: "dashed candidate only" },
    "hidden structure",
    "unknown",
    "unknown",
    sourceIds,
    [regions.closeBase, regions.contextBase],
    "Neither supplied view directly proves the top plate underside slot/follower geometry."
  )
);
const updateCoverage = (topic, supports, conflicts, unknowns) => {
  const row = contract.coverageMatrix.find((candidate) => candidate.topic === topic);
  if (!row) return;
  row.supports = supports;
  row.conflicts = conflicts;
  row.unknowns = unknowns;
};
updateCoverage(
  "upper/lower/mechanism-carrier identity",
  sourceIds,
  ["rev 8/rev 10 fixed-upper moving-lower ownership is superseded"],
  ["exact top underside contact ownership"]
);
updateCoverage(
  "bilateral rails/ball rows/screws",
  [...sourceIds, "slider-intake-haloo-official-07"],
  ["prior lower-moving rail frame is superseded"],
  ["exact rail cross-section and ball/follower coupling"]
);
updateCoverage(
  "endpoint pivot attachment",
  sourceIds,
  ["endpoint-pivot interpretation is superseded"],
  ["physical axis coordinates", "which surrounding carrier subpart rotates"]
);
contract.conclusions = [
  {
    statement: "黑色胶囊底座固定；活动顶片承担复合运动",
    constraintIds: ["MEC-BOTTOM-BASE-FIXED", "MEC-TOP-PLATE-MOVING"],
    confidence: "high",
    sourceCount: 2
  },
  {
    statement: "轴心模块嵌入底座；局部与世界位置都固定",
    constraintIds: ["MEC-AXIS-MODULE-FIXED", "MEC-AXIS-PROJECTED-POSITION"],
    confidence: "high",
    sourceCount: 2
  },
  {
    statement: "左右双轨固定属于底座",
    constraintIds: ["MEC-RAILS-BILATERAL-BOTTOM"],
    confidence: "high",
    sourceCount: 3
  },
  {
    statement: "顶片可同时滑动并绕固定轴旋转",
    constraintIds: ["MEC-COMPOUND-TRANSFORM", "MEC-ROTATION-DURING-SLIDE"],
    confidence: "high",
    sourceCount: 4
  },
  {
    statement: "不存在轴心独立滑动自由度",
    constraintIds: ["MEC-AXIS-MODULE-FIXED"],
    confidence: "high",
    sourceCount: 2
  },
  {
    statement: "顶片底面接触件与白银载体旋转归属仍未知",
    constraintIds: ["MEC-TOP-UNDERSIDE-CONTACTS", "MEC-AXIS-MODULE-FIXED"],
    confidence: "medium",
    sourceCount: 2
  }
];
contract.unknowns = [
  "top plate underside slot/follower/contact geometry",
  "rail cross-section and ball/follower coupling",
  "which white/silver carrier subpart rotates around the fixed bearing axis",
  "physical axis coordinates, thickness, gap, step, clearance and tolerance",
  "exact force, magnet, spring and friction values"
];
contract.downstreamPolicy.rule = "Every CAD and later artifact must record this rev 11 contract SHA-256. CAD approval unlocks only a separate Simulator; Simulator approval is required before Blender.";
contract.reviewQuestion = null;
const contractPath = path.join(here, "mechanism-evidence-contract.json");
fs.writeFileSync(contractPath, `${JSON.stringify(contract, null, 2)}\n`);
const contractHash = sha256File(contractPath);
const config = {
  schemaVersion: 1,
  modelId: "magnetic-slide-tile",
  gate: "02-analysis",
  revision: 11,
  contractAssetId: "slider-analysis-mechanism-evidence-contract-r011",
  contractSha256: contractHash,
  evidenceSelectors: {
    aspectRatioLW: "MEC-SILHOUETTE-ASPECT.value.aspectRatioLW.midpoint",
    maxTravelL: "MEC-TRAVEL-NORMALIZED.value.supportedRange.max",
    observedPeakTravelL: "MEC-TRAVEL-NORMALIZED.value.observedPeak",
    detentStepDeg: "MEC-DETENTS.value.stepDegrees",
    detentCount: "MEC-DETENTS.value.countPerRevolution",
    bottomBase: "MEC-BOTTOM-BASE-FIXED.value",
    fixedAxisModule: "MEC-AXIS-MODULE-FIXED.value",
    axisProjectedPosition: "MEC-AXIS-PROJECTED-POSITION.value",
    movingTop: "MEC-TOP-PLATE-MOVING.value",
    rails: "MEC-RAILS-BILATERAL-BOTTOM.value"
  },
  diagrammaticRailLayout: [
    { side: "left", xL: -0.18, startYL: -0.34, endYL: 0.34, state: "inferred-diagrammatic-not-dimensional" },
    { side: "right", xL: 0.18, startYL: -0.34, endYL: 0.34, state: "inferred-diagrammatic-not-dimensional" }
  ],
  componentLayers: [
    "BottomBase",
    "AxisModule",
    "AxisCarrierCandidate",
    "LeftRail",
    "RightRail",
    "TopPlate",
    "UnknownTopUndersideContacts"
  ],
  cadApprovalChecklist: [
    "topView",
    "sideView",
    "sectionView",
    "slideRange",
    "rotationPositions",
    "pivotInspection",
    "componentLayers",
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
  simulator: {
    locked: true,
    label: "交互 CAD 批准后生成",
    activeControls: 0
  }
};
const configPath = path.join(here, "interactive-cad-geometry-config.json");
fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`);

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 129) throw new Error(`Expected revision 129, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 10) throw new Error("Gate 02 rev 10 must be active.");
const timestamp = new Date().toISOString();
const makeAsset = ({ id, filePath, role, contentClass, note, sourceAssetIds = [] }) => ({
  id,
  stageId: "02-analysis",
  slot: "analysis-evidence",
  path: path.relative(repoRoot, filePath).split(path.sep).join("/"),
  sha256: sha256File(filePath),
  exists: true,
  sizeBytes: fs.statSync(filePath).size,
  role,
  producer: {
    name: role === "user-input" ? "user-selected-reference" : "fidgeting-model-pipeline",
    version: "2026-08-26",
    recipe: "Gate 02 rev 11 fixed-bottom/fixed-axis correction"
  },
  provenance: {
    origin: role === "user-input" ? "user-provided" : "repository-generated",
    contentClass,
    assertedBy: role === "user-input" ? "user" : "assistant",
    note
  },
  sourceAssetIds
});
const assets = [
  makeAsset({
    id: sourceIds[0],
    filePath: archivedPaths[0],
    role: "user-input",
    contentClass: "authoritative-user-selected-bottom-base-close-reference",
    note: "User-authoritative close view supporting fixed black bottom base, separate axis module and bilateral bottom rails."
  }),
  makeAsset({
    id: sourceIds[1],
    filePath: archivedPaths[1],
    role: "user-input",
    contentClass: "authoritative-user-selected-bottom-base-context-reference",
    note: "User-authoritative context view supporting fixed black bottom base, separate axis module and bilateral bottom rails."
  }),
  makeAsset({
    id: "slider-analysis-mechanism-evidence-contract-r011",
    filePath: contractPath,
    role: "analysis",
    contentClass: "authoritative-machine-readable-mechanism-evidence-contract",
    note: "Rev 11 supersedes fixed-upper/moving-lower ownership with fixed bottom, fixed axis and moving top.",
    sourceAssetIds: sourceIds
  }),
  makeAsset({
    id: "slider-analysis-interactive-cad-geometry-config-r011",
    filePath: configPath,
    role: "analysis",
    contentClass: "contract-driven-interactive-cad-geometry-config",
    note: "CAD-only fixed-bottom/fixed-axis configuration. It contains no hand-feel Simulator values.",
    sourceAssetIds: ["slider-analysis-mechanism-evidence-contract-r011"]
  }),
  makeAsset({
    id: "slider-analysis-bottom-fixed-cad-registrar-r011",
    filePath: fileURLToPath(import.meta.url),
    role: "process",
    contentClass: "deterministic-bottom-fixed-contract-and-cad-registrar",
    note: "Archives user images, builds the rev 11 contract/config and registers the immutable revision.",
    sourceAssetIds: sourceIds
  })
];
for (const asset of assets) {
  if (asset.id.includes("contract-r011") || asset.id.includes("config-r011")) {
    asset.mechanismEvidenceContractSha256 = contractHash;
  }
  manifest.assets.push(asset);
  stage.artifactIds.push(asset.id);
}
for (const priorId of [
  "slider-analysis-mechanism-evidence-contract-r008",
  "slider-analysis-interactive-cad-geometry-config-r010"
]) {
  const prior = manifest.assets.find((asset) => asset.id === priorId);
  prior.provenance = {
    ...prior.provenance,
    disposition: "superseded-internal",
    supersededBy: priorId.includes("contract")
      ? "slider-analysis-mechanism-evidence-contract-r011"
      : "slider-analysis-interactive-cad-geometry-config-r011"
  };
  stage.internalArtifactIds = [...new Set([...(stage.internalArtifactIds || []), priorId])];
}
for (const claim of manifest.claims.filter((item) => [
  "slider-analysis-fixed-upper-r005",
  "slider-analysis-lower-carrier-owns-motion-r005",
  "slider-analysis-axis-attached-to-lower-r006",
  "slider-analysis-bilateral-lower-rails-r006",
  "slider-analysis-fixed-endpoint-axis-r007"
].includes(item.id))) {
  claim.state = "superseded";
  claim.decisionState = "superseded";
  claim.supersededBy = "slider-analysis-bottom-fixed-ownership-r011";
}
manifest.claims.push(
  {
    id: "slider-analysis-bottom-fixed-ownership-r011",
    stageId: "02-analysis",
    category: "mechanism-ownership",
    statement: "黑色胶囊 BottomBase 固定；AxisModule 与左右双轨均为其固定子件；TopPlate 承担同时平移和绕固定轴旋转。",
    confidence: "locked",
    state: "pending-review",
    decisionState: "pending-review",
    sourceAssetIds: sourceIds,
    sourceRegions: [regions.closeBase, regions.closeAxis, regions.contextBase],
    unknowns: ["顶片底面接触件", "白银载体旋转归属", "轨道截面与球件耦合"]
  },
  {
    id: "slider-analysis-fixed-axis-no-third-dof-r011",
    stageId: "02-analysis",
    category: "mechanism-kinematics",
    statement: "轴心相对 BottomBase 的局部位置与 CAD 世界位置均恒定；TopPlate 运动不产生轴心路径或第三滑动自由度。",
    confidence: "locked",
    state: "pending-review",
    decisionState: "pending-review",
    sourceAssetIds: sourceIds,
    sourceRegions: [regions.closeAxis, regions.contextBase],
    unknowns: ["轴心物理尺寸与精确坐标"]
  }
);
stage.reviewArtifactIds = ["slider-analysis-interactive-cad-geometry-config-r011"];
stage.status = "ready_for_review";
stage.readiness = {
  ready: true,
  blockers: [],
  note: "Complete eight CAD-only structural checks. The separate Simulator stays locked."
};
stage.analysisSpec = {
  ...stage.analysisSpec,
  revision: 11,
  priorRevisionDisposition: "rev10-fixed-upper-moving-lower-cad-rejected-and-superseded",
  phase: "interactive-cad-approval",
  reviewMode: "interactive-cad-fixed-bottom-fixed-axis",
  contractAssetId: "slider-analysis-mechanism-evidence-contract-r011",
  contractSha256: contractHash,
  constraintIds: contract.constraints.map((item) => item.id),
  coverageTopics: contract.coverageMatrix.map((item) => item.topic),
  sourceInventory: contract.sourceInventory.counts,
  cadArtifactId: "slider-analysis-interactive-cad-geometry-config-r011",
  cadConfigAssetId: "slider-analysis-interactive-cad-geometry-config-r011",
  simulatorArtifactId: null,
  simulatorConfigAssetId: null,
  recordingAssetId: null,
  hierarchy: {
    BottomBase: { parent: null, transform: "identity" },
    AxisModule: { parent: "BottomBase", transform: "constant" },
    AxisCarrierCandidate: { parent: "AxisModule", transform: "candidate-rotation-unknown" },
    LeftRail: { parent: "BottomBase", transform: "constant" },
    RightRail: { parent: "BottomBase", transform: "constant" },
    TopPlate: { parent: null, transform: "T(s)*R(axisFixed,theta)" },
    UnknownTopUndersideContacts: { parent: "TopPlate", transform: "candidate-dashed" }
  },
  cadGeneration: {
    locked: false,
    scope: "web-kinematic-cad-only-no-simulator-blender-unity",
    configSource: "slider-analysis-interactive-cad-geometry-config-r011",
    contractSource: "slider-analysis-mechanism-evidence-contract-r011",
    duplicateDefaultsForbidden: true
  },
  simulatorGeneration: {
    locked: true,
    unlockRequires: "interactive-cad-subapproval-record",
    label: "交互 CAD 批准后生成",
    activeControls: 0
  },
  approvalSpec: {
    ...config.approvalRule,
    requiredMilestones: config.cadApprovalChecklist,
    approvalButtonLabel: "确认交互 CAD",
    approvalApiRequired: true
  },
  reviewQuestion: null
};
stage.validations.push({
  id: "bottom-fixed-axis-fixed-ownership-r011",
  status: "pass",
  evidence: "Rev 11 contract and CAD config supersede moving-bottom/moving-world-axis ownership."
});
for (let index = 2; index <= 10; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 02 rev 11 fixed-bottom/fixed-axis CAD awaits in-workbench subapproval; separate Simulator has not started.";
}
manifest.stages[11].status = "rejected";
manifest.stages[11].staleReason = "Gate 02 CAD and Simulator approvals are incomplete; shipping remains rejected.";
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev11-fixed-bottom-interactive-cad-subapproval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 11 supersedes fixed-upper/moving-lower ownership. BottomBase, AxisModule and both rails are fixed; TopPlate owns simultaneous slide and rotation around the fixed axis. Simulator and all downstream generation remain locked.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-fixed-bottom-review-ready",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 11,
  priorRevisionDisposition: "rev10-fixed-upper-moving-lower-cad-rejected-and-superseded",
  sourceAssetIds: sourceIds,
  sourceHashes: assets.slice(0, 2).map((asset) => asset.sha256),
  contractAssetId: "slider-analysis-mechanism-evidence-contract-r011",
  contractHash,
  cadArtifactId: "slider-analysis-interactive-cad-geometry-config-r011",
  cadArtifactHash: assets[3].sha256,
  requiredMilestones: config.cadApprovalChecklist,
  simulatorState: "locked-not-generated",
  blenderUnityBuildInstallPhone: "not-started"
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  stageRevision: stage.analysisSpec.revision,
  sourceHashes: assets.slice(0, 2).map((asset) => asset.sha256),
  contractHash,
  cadArtifactHash: assets[3].sha256
}, null, 2));
