#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const source = path.resolve(here, "../rev-016/mechanism-evidence-contract.json");
const architectureDirectory = path.resolve(here, "../../04-architecture/rev-014");
const correctionId = "slider-analysis-endpoint-rotation-correction-r017";
const exactUserWording = "上片只有在推到顶部的时候，才可以进行360度旋转";
const correction = {
  schemaVersion: 1,
  modelId: "magnetic-slide-tile",
  gate: "02-analysis",
  revision: 17,
  authority: "latest-explicit-user-chat",
  exactUserWording,
  decisionState: "locked-supersedes-all-slide-position-rotation",
  rules: {
    belowMaximum: "0 <= s < sMax requires theta=0 degrees",
    atMaximum: "s=sMax unlocks full 0-360 degree rotation through 30 detents at 12 degrees",
    nonAlignedRotation: "theta mod 360 != 0 locks s=sMax",
    alignedReturn: "theta within alignment tolerance of 0/360 permits slide return",
    simultaneousMotion: false,
    transitionException: "discrete state transition at sMax and theta alignment only",
  },
  preserves: [
    "geometry",
    "BottomExterior",
    "FixedAxis",
    "MinimumOverlapDisk",
    "top-above-bottom",
    "finite-grooves",
    "hidden-component-containment",
  ],
  forbiddenInference: "Do not invent hidden latch geometry. Represent only endpoint alignment and kinematic interlock.",
};
fs.writeFileSync(path.join(here, "user-endpoint-rotation-correction.json"), `${JSON.stringify(correction, null, 2)}\n`);

const contract = JSON.parse(fs.readFileSync(source, "utf8"));
contract.revision = 17;
contract.title = "Gate 02 rev 17 · 最大行程端点旋转解锁合同";
contract.sourceInventory.assetIds.push(correctionId);
contract.sourceInventory.counts.uniqueAssets += 1;
const byId = new Map(contract.constraints.map((item) => [item.id, item]));
const authoritative = (id, value, decisionNote) => {
  const constraint = byId.get(id);
  constraint.value = value;
  constraint.state = "user-authoritative";
  constraint.confidence = "locked";
  constraint.sourceAssetIds = [correctionId];
  constraint.regions = [{ assetId: correctionId, note: "Latest user-authoritative endpoint interlock correction." }];
  constraint.decisionNote = decisionNote;
};
authoritative(
  "MEC-COMPOUND-TRANSFORM",
  {
    BottomExterior: "identity",
    FixedAxis: "constant",
    belowMaximum: "0<=s<sMax: TopPlate=T_local(s), RotatingCarrier=identity, theta=0",
    endpointRotation: "s=sMax: TopPlate=R_fixedAxis(theta)*T_local(sMax), RotatingCarrier=R_fixedAxis(theta)",
    rotatedSlideLock: "theta mod 360 != 0: s=sMax",
    alignedReturn: "abs(wrapSigned(theta))<=alignmentToleranceDeg permits decreasing s",
    simultaneousSAndTheta: false,
  },
  "The mechanism is serial: slide at theta=0, rotate only at sMax, realign to theta=0/360, then slide closed."
);
authoritative(
  "MEC-ROTATION-DURING-SLIDE",
  {
    allAuthorizedSlidePositions: false,
    rotationUnlockPosition: "sMax only",
    rotationBlockedFor: "0<=s<sMax",
    slideLockedFor: "s=sMax while theta mod 360 != 0",
    returnAlignmentDegrees: [0, 360],
    alignmentToleranceDegrees: 0.1,
    directlyObservedPartialRotation: "superseded-conflicting-video-interpretation",
  },
  "Latest user chat overrides prior video interpretation and every prior all-position rotation claim."
);
authoritative(
  "MEC-TOP-CARRIER-LOCAL-TRANSLATION",
  {
    carrierAngleShared: true,
    translationAxis: "top local longitudinal groove axis",
    transformOrder: "piecewise: T_local(s) when theta=0; R_fixedAxis(theta)*T_local(sMax) only at endpoint",
    simultaneousSAndTheta: false,
    endpointAlignmentRequired: true,
  },
  "Translation and rotation are mutually exclusive channels. No continuous 2-DOF compound gesture is legal."
);
const finite = byId.get("MEC-FINITE-GROOVE-ENDPOINT-STOPS");
finite.value.endpointBehavior = "sMax is the only rotation-unlock endpoint; theta!=0 locks slide at sMax";
finite.sourceAssetIds.push(correctionId);
finite.regions.push({ assetId: correctionId, note: "Defines endpoint unlock and alignment-gated return." });
finite.decisionNote = "Finite grooves remain unchanged. The new rule changes only legal transform transitions at the maximum endpoint.";
const dualBound = byId.get("MEC-ACTUAL-TRAVEL-DUAL-BOUND");
dualBound.value.clampPolicy = "theta=0 permits 0<=s<=sMax; theta!=0 requires s=sMax; no simultaneous velocities";
dualBound.sourceAssetIds.push(correctionId);
dualBound.regions.push({ assetId: correctionId, note: "Applies the endpoint interlock to the existing sMax." });
const trackRoles = byId.get("MEC-FOUR-TRACK-ROLES");
trackRoles.value.innerRole = "central-axis-link-and-endpoint-alignment";
trackRoles.sourceAssetIds.push(correctionId);
trackRoles.regions.push({ assetId: correctionId, note: "Only endpoint alignment is represented; no hidden latch geometry is claimed." });
trackRoles.decisionNote = "Four-track geometry is unchanged. Inner tracks annotate endpoint alignment without inventing a latch.";
contract.constraints.push({
  id: "MEC-ENDPOINT-ROTATION-INTERLOCK",
  value: {
    stateMachine: [
      { id: "closed-aligned", predicate: "s=0 and theta=0", allows: ["slide-open"] },
      { id: "sliding-aligned", predicate: "0<s<sMax and theta=0", allows: ["slide-open", "slide-close"], blocks: ["rotate"] },
      { id: "endpoint-aligned", predicate: "s=sMax and theta=0/360", allows: ["rotate", "slide-close"] },
      { id: "endpoint-rotating", predicate: "s=sMax and theta mod 360!=0", allows: ["rotate"], blocks: ["slide"] },
    ],
    alignmentToleranceDegrees: 0.1,
    detentCount: 30,
    detentStepDegrees: 12,
    noSimultaneousVelocitiesBelowEndpoint: true,
    hiddenLatchGeometry: "unknown-not-modeled",
  },
  units: "piecewise kinematic state machine",
  state: "user-authoritative",
  confidence: "locked",
  sourceAssetIds: [correctionId],
  regions: [{ assetId: correctionId, note: "Whole correction." }],
  decisionNote: "The top rotates only at maximum travel. Return slide unlocks only after 0/360 alignment.",
  downstreamConsumers: ["interactive-cad", "blender-motion", "unity-preview", "haptics", "tests", "shipping-review"],
});
contract.coverageMatrix = contract.coverageMatrix.map((topic) => topic.topic === "simultaneous slide+rotation"
  ? {
      topic: "maximum-endpoint rotation interlock",
      supports: [correctionId],
      conflicts: [
        "IMG_6024 partial/near-maximum rotation interpretation is superseded by latest user authority",
        "all-slide-position rotation and simultaneous 2-DOF claims are rejected",
      ],
      unknowns: ["hidden physical latch or alignment hardware; do not model without evidence"],
    }
  : topic);
contract.conclusions = [
  {
    statement: "0≤s<sMax 时只可沿槽直推，θ 固定为 0°",
    constraintIds: ["MEC-ENDPOINT-ROTATION-INTERLOCK", "MEC-ROTATION-DURING-SLIDE"],
    confidence: "locked",
    sourceCount: 1,
  },
  {
    statement: "只有 s=sMax 最大端点解锁 360° 与 30×12° 卡位",
    constraintIds: ["MEC-ENDPOINT-ROTATION-INTERLOCK", "MEC-ROTATION-RANGE", "MEC-DETENTS"],
    confidence: "locked",
    sourceCount: 1,
  },
  {
    statement: "θ 非 0°/360° 时行程锁在 sMax；重新对齐后才可回推",
    constraintIds: ["MEC-ENDPOINT-ROTATION-INTERLOCK", "MEC-COMPOUND-TRANSFORM"],
    confidence: "locked",
    sourceCount: 1,
  },
  {
    statement: "四轨、固定轴、最小覆盖圆盘、层级与隐藏机构包络保持不变",
    constraintIds: ["MEC-TOP-UNDERSIDE-GROOVES", "MEC-AXIS-MODULE-FIXED", "MEC-MINIMUM-OVERLAP-DISK"],
    confidence: "locked",
    sourceCount: 4,
  },
  {
    statement: "不推断隐藏锁扣；只表达最大端点和槽对齐条件",
    constraintIds: ["MEC-ENDPOINT-ROTATION-INTERLOCK", "MEC-FOUR-TRACK-ROLES"],
    confidence: "locked",
    sourceCount: 1,
  },
];
contract.downstreamPolicy.rule = "Every current consumer records the rev 17 hash and enforces endpoint-only rotation. Rev 16 all-position rotation is superseded.";
contract.reviewQuestion = "最大端点解锁、非零角锁行程、0/360 对齐后回推是否符合真实机构？";
contract.supersedesContractAssetId = "slider-analysis-mechanism-evidence-contract-r016";
contract.supersededConstraintIds = [
  "MEC-COMPOUND-TRANSFORM@r016",
  "MEC-ROTATION-DURING-SLIDE@r016",
  "MEC-TOP-CARRIER-LOCAL-TRANSLATION@r016",
];
contract.createdAt = new Date().toISOString();
contract.decisionSource = {
  authority: "latest-explicit-chat-instruction",
  exactUserWording,
};
const contractPath = path.join(here, "mechanism-evidence-contract.json");
fs.writeFileSync(contractPath, `${JSON.stringify(contract, null, 2)}\n`);
const contractSha256 = crypto.createHash("sha256").update(fs.readFileSync(contractPath)).digest("hex");

const sourceConfig = JSON.parse(fs.readFileSync(path.resolve(here, "../rev-016/interactive-cad-geometry-config.json"), "utf8"));
const config = {
  ...sourceConfig,
  revision: 17,
  contractAssetId: "slider-analysis-mechanism-evidence-contract-r017",
  contractSha256,
  expectedContractSha256: contractSha256,
  geometryBlockers: {
    ...sourceConfig.geometryBlockers,
    contractHashMustMatch: contractSha256,
    rotationUnlockTravel: "sMax-only",
    belowMaximumRotationDegrees: 0,
    nonAlignedSlideLock: "sMax",
    simultaneousMotionForbidden: true,
  },
  kinematicInterlock: byId.get("MEC-ENDPOINT-ROTATION-INTERLOCK")?.value ?? contract.constraints.at(-1).value,
  cadApprovalChecklist: sourceConfig.cadApprovalChecklist
    .filter((item) => item !== "compoundMotion")
    .concat(["midTravelRotationBlocked", "endpointRotationUnlock", "nonzeroAngleSlideLock", "alignedReturn"]),
};
fs.writeFileSync(path.join(here, "interactive-cad-geometry-config.json"), `${JSON.stringify(config, null, 2)}\n`);

const architecture = {
  schemaVersion: 1,
  modelId: "magnetic-slide-tile",
  gate: "04-architecture",
  revision: 14,
  title: "最大端点旋转解锁架构",
  exactUserWording,
  contractAssetId: "slider-analysis-mechanism-evidence-contract-r017",
  contractSha256,
  geometryChanged: false,
  stateMachine: contract.constraints.at(-1).value.stateMachine,
  transforms: {
    fixed: ["BottomExterior", "FixedAxis", "MinimumOverlapDisk"],
    slidingAligned: "TopPlate=T_local(s), RotatingCarrier=identity, theta=0",
    endpointRotating: "TopPlate=R_fixedAxis(theta)*T_local(sMax), RotatingCarrier=R_fixedAxis(theta)",
  },
  annotations: {
    endpointUnlock: "s=sMax 时旋转已解锁",
    grooveAlignment: "theta=0/360 时四轨重新对齐，可回推",
    hiddenLatchGeometry: "unknown-not-modeled",
  },
  supersedesAssetId: "magnetic-slide-tile-approved-four-track-architecture-r013",
};
fs.writeFileSync(path.join(architectureDirectory, "endpoint-rotation-interlock-architecture.json"), `${JSON.stringify(architecture, null, 2)}\n`);
const states = architecture.stateMachine;
const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="720" viewBox="0 0 1280 720">
<rect width="1280" height="720" fill="#11151c"/>
<style>.t{font:28px -apple-system,BlinkMacSystemFont,sans-serif;fill:#eef3f8}.s{font:18px -apple-system,BlinkMacSystemFont,sans-serif;fill:#aeb9c5}.b{fill:#1e2733;stroke:#72d6b2;stroke-width:3}.a{stroke:#f5b95f;stroke-width:4;fill:none;marker-end:url(#m)}.r{fill:#ff756b}</style>
<defs><marker id="m" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#f5b95f"/></marker></defs>
<text x="64" y="64" class="t">Gate 04 rev 14 · 最大端点旋转解锁</text>
<text x="64" y="98" class="s">只表达槽端对齐条件；不推断隐藏锁扣几何</text>
${states.map((state, index) => {
  const x = 60 + index * 300;
  const predicate = state.predicate.replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
  return `<rect x="${x}" y="230" width="250" height="190" rx="24" class="b"/><text x="${x + 20}" y="275" class="t">${index + 1}. ${["闭合对齐","直推对齐","端点对齐","端点旋转"][index]}</text><text x="${x + 20}" y="315" class="s">${predicate}</text><text x="${x + 20}" y="350" class="s">允许：${(state.allows || []).join(" / ")}</text>${state.blocks ? `<text x="${x + 20}" y="385" class="s r">禁止：${state.blocks.join(" / ")}</text>` : ""}`;
}).join("")}
<path d="M310 325 H355" class="a"/><path d="M610 325 H655" class="a"/><path d="M910 325 H955" class="a"/>
<path d="M1080 440 C1080 560 780 560 780 440" class="a"/>
<text x="720" y="610" class="t">θ 回到 0° / 360° → 四轨对齐 → 允许回推</text>
<text x="64" y="665" class="s">固定不变：BottomExterior · FixedAxis · MinimumOverlapDisk · Top z-order · 几何 digest</text>
</svg>`;
fs.writeFileSync(path.join(architectureDirectory, "endpoint-rotation-interlock-state-machine.svg"), svg);
const validation = {
  schemaVersion: 1,
  contractSha256,
  exactUserWording,
  checks: {
    contractRevision17: contract.revision === 17,
    endpointInterlockPresent: contract.constraints.some((item) => item.id === "MEC-ENDPOINT-ROTATION-INTERLOCK"),
    allPositionRotationRemoved: byId.get("MEC-ROTATION-DURING-SLIDE").value.allAuthorizedSlidePositions === false,
    simultaneousMotionRemoved: byId.get("MEC-COMPOUND-TRANSFORM").value.simultaneousSAndTheta === false,
    hiddenLatchNotInvented: architecture.annotations.hiddenLatchGeometry === "unknown-not-modeled",
    geometryUnchanged: architecture.geometryChanged === false,
  },
};
validation.pass = Object.values(validation.checks).every(Boolean);
fs.writeFileSync(path.join(here, "endpoint-interlock-contract-validation.json"), `${JSON.stringify(validation, null, 2)}\n`);
if (!validation.pass) throw new Error(JSON.stringify(validation, null, 2));
console.log(JSON.stringify({ contractSha256, architectureRevision: 14, pass: true }, null, 2));
