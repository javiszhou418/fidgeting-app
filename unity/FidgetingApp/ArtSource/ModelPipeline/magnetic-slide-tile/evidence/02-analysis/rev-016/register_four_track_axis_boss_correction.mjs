#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const manifest = loadManifest(modelId);
if (manifest.revision !== 162) throw new Error(`Expected pipeline revision 162, got ${manifest.revision}.`);
const now = new Date().toISOString();
const exactUserWording = "Gate 05 rev 4’s recessed circular cavity is wrong. The bottom axis must be a protruding independent module/boss embedded in the bottom, not a depression. Top underside has four longitudinal groove/track paths.";
const here = path.dirname(fileURLToPath(import.meta.url));
const gate03Dir = path.resolve(here, "../../03-contract/rev-010");
const gate04Dir = path.resolve(here, "../../04-architecture/rev-012");
const oldContractPath = path.resolve(here, "../rev-015/mechanism-evidence-contract.json");
const oldContract = JSON.parse(fs.readFileSync(oldContractPath, "utf8"));
const measurementPath = path.join(gate03Dir, "anthropometric-video-measurement-report.json");
const measurement = JSON.parse(fs.readFileSync(measurementPath, "utf8"));
const screenshotPaths = [1, 2].map((index) => path.join(gate03Dir, `source-crops/user-rejection-screenshot-${String(index).padStart(2, "0")}.png`));

const contract = structuredClone(oldContract);
contract.revision = 16;
contract.title = "Gate 02 rev 16 · 四轨 + 凸起独立轴座纠正合同";
contract.createdAt = now;
contract.decisionSource = { authority: "latest-explicit-chat-instruction", exactUserWording };
const constraint = (id) => {
  const item = contract.constraints.find((candidate) => candidate.id === id);
  if (!item) throw new Error(`Missing prior constraint ${id}.`);
  return item;
};
constraint("MEC-TOP-UNDERSIDE-GROOVES").value = {
  owner: "MovingTop underside",
  count: 4,
  longitudinal: true,
  finite: true,
  tracks: [
    { id: "TopOuterGrooveLeft", role: "fore-aft-slide", side: "left-outer" },
    { id: "TopInnerGrooveLeft", role: "central-axis-link", side: "left-inner" },
    { id: "TopInnerGrooveRight", role: "central-axis-link", side: "right-inner" },
    { id: "TopOuterGrooveRight", role: "fore-aft-slide", side: "right-outer" }
  ],
  widthMm: { minimum: 1.8, maximum: 3.0, state: "anthropometric-video-estimate-plus-user-maximum" },
  depthMm: null,
  crossSection: "unknown"
};
constraint("MEC-TOP-UNDERSIDE-GROOVES").decisionNote = "用户明确顶片背面是四条纵向轨：外二负责直推，内二连接中心轴机构。";
constraint("MEC-FINITE-GROOVE-ENDPOINT-STOPS").value.grooveCount = 4;
constraint("MEC-FINITE-GROOVE-ENDPOINT-STOPS").value.followerCount = 2;
constraint("MEC-MINIMUM-OVERLAP-DISK").value.renderPolicy = "validation-overlay-only-never-visible-geometry";
constraint("MEC-MINIMUM-OVERLAP-DISK").decisionNote = "圆盘仅为连续覆盖验证区，不得成为凹坑、凸台或 shipping 几何。";
contract.constraints.push(
  {
    id: "MEC-RAISED-AXIS-BOSS",
    state: "user-authoritative",
    confidence: "locked",
    value: {
      owner: "BottomExterior",
      kind: "protruding-independent-module",
      protrusionPositive: true,
      protrusionMm: { range: [1.0, 3.0], state: "diagrammatic-provisional", confidence: "low" },
      recessedAxis: false,
      visibleCavityAllowed: false
    },
    units: "millimetres and boolean topology",
    regions: [{ assetId: "slider-analysis-user-rejection-screenshot-02-r016", note: "Rejected visible cavity and corrected raised-boss interpretation." }],
    sourceAssetIds: ["slider-analysis-user-rejection-screenshot-01-r016", "slider-analysis-user-rejection-screenshot-02-r016"],
    decisionNote: "底部中心轴/载体模块向上凸起并嵌于底壳；Gate 05 rev 4 可见凹坑被拒绝。",
    downstreamConsumers: ["Gate 03 contract", "Gate 04 architecture", "future Blender generation blocker"]
  },
  {
    id: "MEC-BALL-CONTACT-CANDIDATES",
    state: "user-authoritative-range",
    confidence: "medium",
    value: {
      ballDiameterMm: [2.0, 3.0],
      material: "unknown-steel-or-plastic-or-ceramic",
      count: null,
      springs: null,
      preload: null,
      renderPolicy: "labeled-candidates-not-final-engineering"
    },
    units: "millimetres",
    regions: [{ assetId: "slider-intake-haloo-official-05", note: "Official ball/spring mechanism close view." }],
    sourceAssetIds: ["slider-intake-haloo-official-05", "slider-intake-haloo-official-07", "slider-measurement-anthropometric-video-report-r010"],
    decisionNote: "球件在推/转时沿轨滚动并切换档位；仅直径 2–3 mm 获用户授权。",
    downstreamConsumers: ["Gate 03 contract", "interactive CAD", "future Blender generation blocker"]
  },
  {
    id: "MEC-FOUR-TRACK-ROLES",
    state: "user-authoritative",
    confidence: "locked",
    value: {
      count: 4,
      outerTrackCount: 2,
      innerTrackCount: 2,
      outerRole: "fore-aft-slide",
      innerRole: "central-axis-link-and-compound-motion",
      bottomCarrierFollowerCount: 2
    },
    units: "component counts and roles",
    regions: [{ assetId: "slider-intake-haloo-official-07", note: "Official internal four-track and ball-path view." }],
    sourceAssetIds: ["slider-intake-haloo-official-07", "slider-measurement-anthropometric-video-report-r010"],
    decisionNote: "外轨与内轨必须分色、分角色；不得退回双槽简化。",
    downstreamConsumers: ["interactive CAD", "Gate 04 hierarchy", "future Blender generation blocker"]
  }
);
contract.sourceInventory.assetIds.push(
  "slider-analysis-user-rejection-screenshot-01-r016",
  "slider-analysis-user-rejection-screenshot-02-r016",
  "slider-measurement-anthropometric-video-report-r010"
);
const contractPath = path.join(here, "mechanism-evidence-contract.json");
fs.writeFileSync(contractPath, `${JSON.stringify(contract, null, 2)}\n`);
const contractHash = sha256File(contractPath);

const config = {
  schemaVersion: 2,
  modelId,
  gate: "02-analysis",
  revision: 16,
  contractAssetId: "slider-analysis-mechanism-evidence-contract-r016",
  contractSha256: contractHash,
  expectedContractSha256: contractHash,
  diagrammaticGeometry: {
    axisNormalizedY: 0.32,
    carrierRadiusL: 0.23,
    carrierSideCutoutHalfWidthL: 0.08,
    followerOffsetXL: 0.12,
    innerGrooveOffsetXL: 0.12,
    outerGrooveOffsetXL: 0.235,
    grooveStartYL: -0.34,
    grooveEndYL: 0.34,
    grooveStartFromTopL: 0.32,
    grooveEndFromTopL: 0.78,
    minimumOverlapDiskRadiusL: 0.3184713375796178,
    axisBossProtrusionMm: 2.0,
    ballDiameterMm: 2.5,
    trackWidthMm: 2.4
  },
  componentLayers: [
    "BottomExterior", "FixedAxisBoss", "MinimumOverlapDisk", "RotatingCarrier",
    "CarrierFollowerLeft", "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight",
    "MovingTop", "TopOuterGrooveLeft", "TopInnerGrooveLeft",
    "TopInnerGrooveRight", "TopOuterGrooveRight", "UnknownSprings", "UnknownPreload"
  ],
  geometryBlockers: {
    trackCountMustEqual: 4,
    requiredTrackRoles: ["fore-aft-slide", "central-axis-link"],
    axisBossProtrusionMustExceedMm: 0,
    recessedAxisFlagForbidden: true,
    ballDiameterAuthorizedMm: [2, 3],
    trackWidthMaximumMm: 3,
    contractHashMustMatch: contractHash
  },
  cadApprovalChecklist: [
    "fourTracks", "outerInnerRoles", "raisedAxisBoss", "ballRange", "trackWidth",
    "minimumOverlapDisk", "finiteGrooveEndpoints", "pointerDirection",
    "compoundMotion", "fixedAxisCoverage", "topAboveBottom", "sourceMapping"
  ],
  simulator: { locked: true, current: false }
};
const configPath = path.join(here, "interactive-cad-geometry-config.json");
fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`);

const newClaimDefs = [
  ["slider-analysis-four-track-roles-r016", "顶片背面四条纵轨：外二直推，内二连接中心轴机构。", "mechanism-structure"],
  ["slider-analysis-raised-axis-boss-r016", "底壳光滑；中心轴座是向上凸起的独立模块，禁止可见凹坑。", "mechanism-structure"],
  ["slider-analysis-ball-contact-range-r016", "球件候选直径 2–3 mm；轨宽不超过 3 mm。", "mechanism-dimension-range"]
];
for (const [id, statement, category] of newClaimDefs) {
  manifest.claims.push({ id, stageId: "02-analysis", category, statement, confidence: "locked", state: "active", decisionState: "user-authoritative", sourceAssetIds: ["slider-analysis-user-rejection-screenshot-01-r016", "slider-analysis-user-rejection-screenshot-02-r016"], sourceRegions: [], unknowns: measurement.remainingUnknowns });
}
const sourceClaimIds = manifest.claims.filter((claim) => claim.stageId === "02-analysis" && !["superseded", "stale"].includes(claim.state)).map((claim) => claim.id);
const provisional = {
  schemaVersion: 4,
  kind: "user-authorized-anthropometric-video-provisional-modeling-contract",
  modelId,
  gate: "03-contract",
  revision: 10,
  createdAt: now,
  governingMechanismContractSha256: contractHash,
  authorization: { exactUserWording, scope: "interactive CAD and provisional contract only; Blender stopped" },
  dimensionClass: "anthropometric video estimate; not production measured",
  dimensionsMm: {
    overallLength: { range: measurement.exteriorEstimateMm.overallLength.range, provisional: 50, confidence: "medium-low" },
    overallWidth: { range: measurement.exteriorEstimateMm.overallWidth.range, provisional: 31, confidence: "medium-low" },
    totalClosedThickness: { range: null, provisional: 12, confidence: "low", reason: "not recoverable from frontal hand scale" },
    topThickness: { range: null, provisional: 5.875, confidence: "low" },
    bottomThickness: { range: null, provisional: 5.875, confidence: "low" },
    closedSeamGap: { range: null, provisional: 0.25, confidence: "low" },
    maximumSlideTravel: { range: [17.0, 19.2], provisional: 18.076433121019107, confidence: "medium-low" },
    fixedAxisOffsetFromNearestEnd: { range: [14.5, 17.5], provisional: 16, confidence: "low" },
    rotatingCarrierDiameter: { range: [21, 26], provisional: 23, confidence: "low" },
    ballDiameter: { range: [2, 3], provisional: 2.5, confidence: "medium", state: "user-authoritative-estimate" },
    trackWidth: { range: [1.8, 3], provisional: 2.4, confidence: "low", maximumAuthorized: 3 }
  },
  mechanism: {
    trackCount: 4,
    outerTrackCount: 2,
    innerTrackCount: 2,
    axisBossProtrusionMm: { range: [1, 3], provisional: 2, confidence: "low" },
    recessedAxis: false,
    minimumOverlapDisk: "validation-only-never-visible-geometry",
    topTransform: "R_fixedAxis(theta) * T_local(s)"
  },
  generationBlockers: config.geometryBlockers,
  unknownEngineering: measurement.remainingUnknowns,
  sourceClaimIds,
  sourceAssetIds: [
    "slider-analysis-mechanism-evidence-contract-r016",
    "slider-measurement-anthropometric-video-report-r010",
    "slider-analysis-user-rejection-screenshot-01-r016",
    "slider-analysis-user-rejection-screenshot-02-r016"
  ]
};
const provisionalPath = path.join(gate03Dir, "provisional-modeling-contract.json");
fs.writeFileSync(provisionalPath, `${JSON.stringify(provisional, null, 2)}\n`);

const architecture = {
  schemaVersion: 2,
  kind: "four-track-raised-axis-architecture",
  modelId,
  gate: "04-architecture",
  revision: 12,
  createdAt: now,
  governingMechanismContractSha256: contractHash,
  hierarchy: [
    ["BottomExterior", "Root", "identity", "smooth, no exterior cavity or rail"],
    ["FixedAxisBoss", "BottomExterior", "identity", "positive protrusion"],
    ["MinimumOverlapDisk", "BottomExterior", "identity", "validation overlay only"],
    ["RotatingCarrier", "FixedAxisBoss", "R_fixedAxis(theta)", "no translation"],
    ["CarrierFollowerLeft", "RotatingCarrier", "R_fixedAxis(theta)", "inner-track link"],
    ["CarrierFollowerRight", "RotatingCarrier", "R_fixedAxis(theta)", "inner-track link"],
    ["BallCandidateLeft", "RotatingCarrier", "R_fixedAxis(theta)", "2–3 mm candidate"],
    ["BallCandidateRight", "RotatingCarrier", "R_fixedAxis(theta)", "2–3 mm candidate"],
    ["MovingTop", "Root", "R_fixedAxis(theta)*T_local(s)", "always above bottom"],
    ["TopOuterGrooveLeft", "MovingTop", "R*T", "fore/aft slide"],
    ["TopInnerGrooveLeft", "MovingTop", "R*T", "axis linkage"],
    ["TopInnerGrooveRight", "MovingTop", "R*T", "axis linkage"],
    ["TopOuterGrooveRight", "MovingTop", "R*T", "fore/aft slide"],
    ["UnknownSprings", "RotatingCarrier", "metadata-only", "count/layout unknown"],
    ["UnknownPreload", "RotatingCarrier", "metadata-only", "unknown"]
  ].map(([id, parent, transform, note]) => ({ id, parent, transform, note })),
  blockers: config.geometryBlockers
};
const architecturePath = path.join(gate04Dir, "four-track-raised-axis-architecture.json");
fs.writeFileSync(architecturePath, `${JSON.stringify(architecture, null, 2)}\n`);
const boardPath = path.join(gate04Dir, "four-track-raised-axis-hierarchy.svg");
fs.writeFileSync(boardPath, `<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000"><rect width="100%" height="100%" fill="#081017"/><style>text{font-family:Arial;fill:#e8f0f2}.h{font-size:34px;font-weight:700}.s{font-size:22px}.o{stroke:#56d7e2;fill:#13242b}.i{stroke:#b58aff;fill:#211a2d}.u{stroke:#efbb62;fill:#2a2113;stroke-dasharray:8 6}</style><text x="70" y="70" class="h">Four-track + raised axis-boss architecture</text><text x="70" y="110" class="s">Contract ${contractHash}</text><rect x="70" y="160" width="1460" height="90" rx="18" class="o"/><text x="100" y="215" class="h">MovingTop · R_fixedAxis(θ) · T_local(s)</text><rect x="100" y="300" width="320" height="90" rx="16" class="o"/><text x="125" y="355" class="s">Outer tracks ×2 · slide</text><rect x="460" y="300" width="320" height="90" rx="16" class="i"/><text x="485" y="355" class="s">Inner tracks ×2 · axis link</text><rect x="70" y="470" width="1460" height="100" rx="18" class="o"/><text x="100" y="530" class="h">Smooth BottomExterior · no cavity</text><rect x="150" y="640" width="370" height="100" rx="18" class="i"/><text x="180" y="700" class="h">Raised FixedAxisBoss</text><rect x="610" y="640" width="370" height="100" rx="18" class="o"/><text x="640" y="700" class="h">RotatingCarrier</text><rect x="1070" y="640" width="390" height="100" rx="18" class="u"/><text x="1100" y="700" class="s">Ball candidates 2–3 mm</text><text x="70" y="900" class="s">MinimumOverlapDisk = validation overlay only · springs/preload/cross-section remain unknown</text></svg>`);

const rel = (absolute) => path.relative(repoRoot, absolute).split(path.sep).join("/");
const addAsset = ({ id, stageId, slot, absolute, role, sourceAssetIds = [], sourceUrl }) => {
  manifest.assets.push({
    id, stageId, slot, path: rel(absolute), sha256: sha256File(absolute), exists: true,
    sizeBytes: fs.statSync(absolute).size, role,
    producer: { name: "fidgeting-model-pipeline", version: "4", recipe: "four-track raised-axis correction" },
    provenance: {
      origin: role === "user-input" ? "user-provided" : "repository-generated",
      contentClass: slot,
      assertedBy: role === "user-input" ? "user" : "assistant",
      exactUserWording,
      ...(stageId === "02-analysis" ? {} : { mechanismEvidenceContractSha256: contractHash })
    },
    sourceAssetIds, sourceClaimIds: stageId === "02-analysis" ? [] : sourceClaimIds,
    ...(sourceUrl ? { sourceUrl } : {})
  });
};
addAsset({ id: "slider-analysis-user-rejection-screenshot-01-r016", stageId: "02-analysis", slot: "user-correction-reference", absolute: screenshotPaths[0], role: "user-input" });
addAsset({ id: "slider-analysis-user-rejection-screenshot-02-r016", stageId: "02-analysis", slot: "user-correction-reference", absolute: screenshotPaths[1], role: "user-input" });
addAsset({ id: "slider-analysis-mechanism-evidence-contract-r016", stageId: "02-analysis", slot: "mechanism-evidence-contract", absolute: contractPath, role: "contract", sourceAssetIds: ["slider-analysis-user-rejection-screenshot-01-r016", "slider-analysis-user-rejection-screenshot-02-r016"] });
addAsset({ id: "slider-analysis-interactive-cad-geometry-config-r016", stageId: "02-analysis", slot: "interactive-cad", absolute: configPath, role: "contract", sourceAssetIds: ["slider-analysis-mechanism-evidence-contract-r016"] });
addAsset({ id: "slider-measurement-anthropometric-video-report-r010", stageId: "03-contract", slot: "measurement-report", absolute: measurementPath, role: "validation", sourceAssetIds: ["slider-intake-user-mechanism-video-6024", "slider-intake-haloo-official-05", "slider-intake-haloo-official-07"] });
addAsset({ id: "slider-measurement-anthropometric-builder-r010", stageId: "03-contract", slot: "measurement-process", absolute: path.join(gate03Dir, "build_anthropometric_measurement_report.py"), role: "process", sourceAssetIds: ["slider-intake-user-mechanism-video-6024"] });
addAsset({ id: "magnetic-slide-tile-provisional-modeling-contract-r010", stageId: "03-contract", slot: "modeling-contract", absolute: provisionalPath, role: "contract", sourceAssetIds: provisional.sourceAssetIds });
addAsset({ id: "magnetic-slide-tile-four-track-architecture-r012", stageId: "04-architecture", slot: "part-tree", absolute: architecturePath, role: "contract", sourceAssetIds: ["magnetic-slide-tile-provisional-modeling-contract-r010"] });
addAsset({ id: "magnetic-slide-tile-four-track-hierarchy-r012", stageId: "04-architecture", slot: "exploded-plan", absolute: boardPath, role: "validation", sourceAssetIds: ["magnetic-slide-tile-four-track-architecture-r012"] });

const gate02 = manifest.stages[1];
const gate03 = manifest.stages[2];
const gate04 = manifest.stages[3];
const gate05 = manifest.stages[4];
gate02.revision += 1;
gate02.status = "approved";
gate02.artifactIds.push(
  "slider-analysis-user-rejection-screenshot-01-r016",
  "slider-analysis-user-rejection-screenshot-02-r016",
  "slider-analysis-mechanism-evidence-contract-r016",
  "slider-analysis-interactive-cad-geometry-config-r016"
);
gate02.reviewArtifactIds = ["slider-analysis-interactive-cad-geometry-config-r016"];
gate02.analysisSpec = {
  ...gate02.analysisSpec,
  revision: 16,
  reviewMode: "interactive-cad-four-track-raised-axis",
  contractAssetId: "slider-analysis-mechanism-evidence-contract-r016",
  contractSha256: contractHash,
  geometryConfigAssetId: "slider-analysis-interactive-cad-geometry-config-r016",
  componentContract: {
    trackCount: 4, outerTrackCount: 2, innerTrackCount: 2,
    raisedAxisBoss: true, recessedAxis: false,
    ballDiameterMm: [2, 3], maximumTrackWidthMm: 3
  },
  decisionSource: { exactUserWording, authority: "latest-explicit-chat-instruction" }
};
gate02.validations = [
  { id: "four-track-contract", status: "pass", evidence: "Track count 4 with outer/inner roles." },
  { id: "raised-axis-no-cavity", status: "pass", evidence: "Positive boss required; recessed-axis flag forbidden." },
  { id: "estimate-boundary", status: "pass", evidence: "Anthropometric/video values remain ranges, not production measurements." }
];
gate03.revision += 1;
gate03.status = "ready_for_review";
gate03.artifactIds = [
  "slider-measurement-anthropometric-video-report-r010",
  "slider-measurement-anthropometric-builder-r010",
  "magnetic-slide-tile-provisional-modeling-contract-r010"
];
gate03.reviewArtifactIds = ["slider-measurement-anthropometric-video-report-r010"];
gate03.measurementProgress = { complete: 9, total: 9, mode: "user-authorized-anthropometric-video-provisional" };
gate03.validations = [
  { id: "anthropometric-provenance", status: "pass", evidence: "AIST/Chinese/Korean sources plus accepted/rejected frame audit recorded." },
  { id: "generation-blockers", status: "pass", evidence: "Four tracks, roles, positive boss, no cavity, ball/track ranges and hash fail closed." },
  { id: "engineering-unknowns", status: "pass", evidence: "Material/count/springs/depth/preload/tolerances remain unknown." }
];
delete gate03.decision;
gate04.revision += 1;
gate04.status = "stale";
gate04.artifactIds = ["magnetic-slide-tile-four-track-architecture-r012", "magnetic-slide-tile-four-track-hierarchy-r012"];
gate04.reviewArtifactIds = ["magnetic-slide-tile-four-track-hierarchy-r012"];
gate04.staleReason = "Gate 03 rev 10 four-track/raised-axis contract awaits interactive review.";
delete gate04.decision;
gate05.revision += 1;
gate05.status = "rejected";
gate05.staleReason = "User rejected visible recessed circular cavity; rev 4 preserved as failed evidence.";
gate05.decision = { action: "reject", notes: exactUserWording, decidedBy: "user-chat-authority", decidedAt: now };
for (let index = 5; index < 11; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Four-track raised-axis mechanism correction invalidated downstream geometry.";
}
manifest.stages[11].status = "rejected";
manifest.currentStageId = "03-contract";
manifest.currentState.visualApproval = "gate03-four-track-raised-axis-interactive-cad-pending";
manifest.currentState.blenderModelingStatus = "stopped-gate05-rev4-rejected";
manifest.currentState.measurementProgress = "9/9-user-authorized-anthropometric-video-provisional-awaiting-review";
manifest.currentState.diagnosis = "Gate 05 rev 4 incorrectly rendered MinimumOverlapDisk as a recessed cavity. Current CAD requires four top tracks and a protruding bottom axis boss.";
manifest.revision += 1;
manifest.updatedAt = now;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-rejected-four-track-raised-axis-correction",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording,
  contractSha256: contractHash,
  gate02Status: "approved",
  gate03Status: "ready_for_review",
  gate04Status: "stale",
  gate05Status: "rejected",
  blenderStopped: true,
  simulatorUsed: false,
  unityChanged: false,
  deviceWork: false
});
console.log(JSON.stringify({ revision: saved.revision, contractSha256: contractHash, gate03: saved.stages[2].status, gate04: saved.stages[3].status, gate05: saved.stages[4].status }, null, 2));
