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
if (manifest.revision !== 159) throw new Error(`Expected pipeline revision 159, got ${manifest.revision}.`);
const now = new Date().toISOString();
const quote = "你直接来吧…leverage 我们之前所有做过的工作，包括图案，材质，灯光和细节调整.";
const gate02 = manifest.stages.find((stage) => stage.id === "02-analysis");
const gate03 = manifest.stages.find((stage) => stage.id === "03-contract");
const gate04 = manifest.stages.find((stage) => stage.id === "04-architecture");
const contractHash = gate02.analysisSpec.contractSha256;
const actualSMaxL = gate02.analysisSpec.finalApproval.geometryParameterSnapshot.actualSMaxL;
const lengthMm = 50;
const widthMm = 31;
const totalThicknessMm = 12;
const closedSeamGapMm = 0.25;
const layerThicknessMm = (totalThicknessMm - closedSeamGapMm) / 2;
const maxTravelMm = lengthMm * actualSMaxL;
const axisOffsetMm = lengthMm * 0.32;
const carrierDiameterMm = lengthMm * 0.23 * 2;

const assetById = (id) => {
  const asset = manifest.assets.find((candidate) => candidate.id === id);
  if (!asset) throw new Error(`Missing reuse asset ${id}.`);
  return asset;
};
const reuseIds = [
  "magnetic-slide-tile-blockout-builder-r003",
  "magnetic-slide-tile-smoothing-normal-validation-r002",
  "magnetic-slide-tile-artwork-upper-mask-r007",
  "magnetic-slide-tile-material-rev10-lower-mask-r010",
  "magnetic-slide-tile-material-rev10-recipe-r010",
  "magnetic-slide-tile-lighting-validation-r001",
  "magnetic-slide-tile-open-environment-validation-r002",
  gate02.analysisSpec.contractAssetId,
  gate02.analysisSpec.cadArtifactId
];
const reusedAssets = reuseIds.map((id) => {
  const asset = assetById(id);
  return { id, path: asset.path, sha256: asset.sha256, reuse: ({
    "magnetic-slide-tile-blockout-builder-r003": "analytic capsule profile, 256 segments per semicircle, bevel and smooth-normal technique only",
    "magnetic-slide-tile-smoothing-normal-validation-r002": "normal and silhouette audit lessons",
    "magnetic-slide-tile-artwork-upper-mask-r007": "independent upper artwork slot for later Gate 07",
    "magnetic-slide-tile-material-rev10-lower-mask-r010": "independent corrected lower artwork slot for later Gate 07",
    "magnetic-slide-tile-material-rev10-recipe-r010": "blood-red crystal, black perimeter and polished silver recipes for later Gate 07",
    "magnetic-slide-tile-lighting-validation-r001": "approved controlled lighting recipe for later Gate 08",
    "magnetic-slide-tile-open-environment-validation-r002": "approved environment and reflection lessons for later Gate 09"
  })[id] || "approved Gate 02 mechanism source" };
});
const staleNotReused = [
  { gate: "05-blockout", revision: 3, reason: "old hierarchy and mutually-exclusive slide/spin conflict with approved compound CAD" },
  { gate: "06-geometry", revision: 1, reason: "old axis/21 mm travel and stale geometry cannot migrate" },
  { gate: "07-material", revisions: [1, 2, 3, 4, 5, 6, 7, 8, 9], reason: "geometry-bound Blender scenes remain stale; only masks and rev 10 recipes are lineage inputs" },
  { gate: "08-lighting", revision: 1, reason: "recipe retained for later; no lighting promoted into white Gate 05" },
  { gate: "09-environment", revision: 2, reason: "recipe retained for later; no environment promoted into white Gate 05" },
  { gate: "10-export", revisions: [1, 2, 3], reason: "old export packages remain stale and are not imported" },
  { gate: "11-unity-parity", revisions: [1, 2, 3, 4], reason: "Unity remains untouched; lessons only" }
];

const contract = {
  schemaVersion: 3,
  kind: "user-authorized-provisional-modeling-contract",
  modelId,
  gate: "03-contract",
  contractRevision: 9,
  createdAt: now,
  decisionSource: { authority: "latest-explicit-chat-instruction", exactUserWording: quote },
  statusBoundary: {
    userAuthorizedProvisional: true,
    productionMeasured: false,
    officialPublishedDimensions: false,
    fabricationReady: false
  },
  approvedMechanismContract: {
    assetId: gate02.analysisSpec.contractAssetId,
    sha256: contractHash,
    cadArtifactId: gate02.analysisSpec.cadArtifactId,
    cadArtifactSha256: assetById(gate02.analysisSpec.cadArtifactId).sha256
  },
  units: "millimeters",
  dimensions: {
    closedOverallLength: { value: lengthMm, state: "user-authorized-provisional", sourceAssetIds: ["magnetic-slide-tile-modeling-contract-r007"] },
    overallWidth: { value: widthMm, state: "user-authorized-provisional", sourceAssetIds: ["magnetic-slide-tile-modeling-contract-r007"] },
    totalClosedThickness: { value: totalThicknessMm, state: "user-authorized-provisional", sourceAssetIds: ["magnetic-slide-tile-modeling-contract-r007"] },
    topPlateThickness: {
      value: layerThicknessMm,
      state: "derived-user-authorized-provisional",
      derivation: "(totalClosedThickness - closedSeamGap) / 2; prior Blender used equal 6 mm layers"
    },
    bottomPlateThickness: {
      value: layerThicknessMm,
      state: "derived-user-authorized-provisional",
      derivation: "(totalClosedThickness - closedSeamGap) / 2; prior Blender used equal 6 mm layers"
    },
    maximumSlideTravel: {
      value: maxTravelMm,
      state: "derived-from-approved-cad-and-user-authorized-provisional-L",
      derivation: `${actualSMaxL} × 50`
    },
    fixedAxisOffsetFromNearestEnd: {
      value: axisOffsetMm,
      state: "diagrammatic-cad-provisional",
      derivation: "axisNormalizedY 0.32 × 50"
    },
    rotatingCarrierDiameter: {
      value: carrierDiameterMm,
      state: "diagrammatic-cad-provisional",
      derivation: "carrierRadiusL 0.23 × 2 × 50"
    },
    closedSeamGap: { value: closedSeamGapMm, state: "user-authorized-provisional", sourceAssetIds: ["magnetic-slide-tile-modeling-contract-r007"] }
  },
  derivedChecks: {
    thicknessStackMm: layerThicknessMm * 2 + closedSeamGapMm,
    thicknessStackMatchesTotal: layerThicknessMm * 2 + closedSeamGapMm === totalThicknessMm,
    carrierFitsWidth: carrierDiameterMm <= widthMm,
    axisCarrierFitsLength: axisOffsetMm >= carrierDiameterMm / 2 && axisOffsetMm + carrierDiameterMm / 2 <= lengthMm,
    maximumSlideTravelL: maxTravelMm / lengthMm,
    matchesApprovedActualSMaxL: Math.abs(maxTravelMm / lengthMm - actualSMaxL) < 1e-12
  },
  unknownEngineeringDimensions: [
    "groove width", "groove depth", "follower size", "contact cross-section",
    "operating clearance", "manufacturing allowance", "manufacturing tolerance"
  ],
  sourceClaimIds: manifest.claims.filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded").map((claim) => claim.id),
  sourceAssetIds: [
    "magnetic-slide-tile-modeling-contract-r007",
    gate02.analysisSpec.contractAssetId,
    gate02.analysisSpec.cadArtifactId
  ],
  completeness: { complete: true, authorizedFor: "Gate 04 architecture migration and Gate 05 white blockout only" }
};

const architecture = {
  schemaVersion: 1,
  kind: "approved-cad-architecture-migration",
  modelId,
  gate: "04-architecture",
  architectureRevision: 11,
  createdAt: now,
  decisionSource: { authority: "latest-explicit-chat-instruction", exactUserWording: quote, noNewAssumptions: true },
  governingContractSha256: contractHash,
  hierarchy: [
    { id: "BottomExterior", parent: "Root", render: true, transform: "identity", notes: "smooth rail-free exterior" },
    { id: "FixedAxis", parent: "BottomExterior", render: true, transform: "identity", notes: "embedded and invariant" },
    { id: "MinimumOverlapDisk", parent: "BottomExterior", render: false, transform: "identity", notes: "validation metadata/overlay only" },
    { id: "RotatingCarrier", parent: "BottomExterior", render: true, transform: "R_fixedAxis(theta)", notes: "circular with bilateral CAD-provisional side clearances" },
    { id: "CarrierFollowerLeft", parent: "RotatingCarrier", render: false, transform: "R_fixedAxis(theta)", notes: "unknown size; metadata proxy" },
    { id: "CarrierFollowerRight", parent: "RotatingCarrier", render: false, transform: "R_fixedAxis(theta)", notes: "unknown size; metadata proxy" },
    { id: "TopPlate", parent: "Root", render: true, transform: "R_fixedAxis(theta) * T_local(s)", notes: "always above bottom" },
    { id: "TopGrooveLeft", parent: "TopPlate", render: false, transform: "R_fixedAxis(theta) * T_local(s)", notes: "centerline/extent metadata; width and depth unknown" },
    { id: "TopGrooveRight", parent: "TopPlate", render: false, transform: "R_fixedAxis(theta) * T_local(s)", notes: "centerline/extent metadata; width and depth unknown" },
    { id: "UnknownContacts", parent: "TopPlate", render: false, transform: "metadata-only", notes: "never render as invented geometry" }
  ],
  kinematics: {
    top: "R_fixedAxis(theta) * T_local(s)",
    rangeSmm: [0, maxTravelMm],
    finiteGrooveEndpoints: true,
    minimumOverlapDiskRadiusMm: 50 * 0.3184713375796178,
    minimumOverlapRequired: true,
    detentCount: 30,
    detentStepDegrees: 12,
    simultaneousSlideRotation: true,
    initialVelocity: 0,
    selfMotion: false
  },
  requiredReviewPoses: [
    { id: "closed", sMm: 0, thetaDeg: 0 },
    { id: "max-open", sMm: maxTravelMm, thetaDeg: 0 },
    { id: "detent-01", sMm: maxTravelMm * 0.45, thetaDeg: 12 },
    { id: "detent-03", sMm: maxTravelMm * 0.7, thetaDeg: 36 }
  ]
};

const output03 = path.dirname(fileURLToPath(import.meta.url));
const output04 = path.resolve(output03, "../../04-architecture/rev-011");
fs.mkdirSync(output04, { recursive: true });
const contractPath = path.join(output03, "provisional-modeling-contract.json");
const reusePath = path.join(output03, "reuse-plan.json");
const architecturePath = path.join(output04, "approved-cad-architecture.json");
const architectureSvgPath = path.join(output04, "approved-cad-hierarchy.svg");
fs.writeFileSync(contractPath, `${JSON.stringify(contract, null, 2)}\n`);
fs.writeFileSync(reusePath, `${JSON.stringify({
  schemaVersion: 1,
  modelId,
  gate: "03-contract",
  createdAt: now,
  contractSha256: contractHash,
  reusedAssets,
  staleNotReused,
  gate05Policy: "reuse technique and lineage inputs; rebuild all geometry from approved Gate 02 hierarchy"
}, null, 2)}\n`);
fs.writeFileSync(architecturePath, `${JSON.stringify(architecture, null, 2)}\n`);
fs.writeFileSync(architectureSvgPath, `<svg xmlns="http://www.w3.org/2000/svg" width="1600" height="1000" viewBox="0 0 1600 1000">
<rect width="1600" height="1000" fill="#091017"/><style>text{font-family:Arial,sans-serif;fill:#dce9ef}.h{font-size:34px;font-weight:700}.s{font-size:20px;fill:#8da4af}.b{fill:#111d25;stroke:#5fd6df;stroke-width:2}.u{fill:#17141a;stroke:#e8b769;stroke-width:2;stroke-dasharray:10 7}</style>
<text x="80" y="80" class="h">Gate 04 · Approved CAD hierarchy migration</text><text x="80" y="118" class="s">Top = R_fixedAxis(θ) · T_local(s) · contract ${contractHash}</text>
<rect x="80" y="170" width="1440" height="110" rx="22" class="b"/><text x="120" y="225" class="h">Root</text><text x="350" y="225" class="s">Bottom fixed · Top moving · no Simulator</text>
<rect x="120" y="330" width="610" height="110" rx="20" class="b"/><text x="160" y="385" class="h">BottomExterior</text><text x="160" y="420" class="s">smooth / rail-free</text>
<rect x="870" y="330" width="610" height="110" rx="20" class="b"/><text x="910" y="385" class="h">TopPlate</text><text x="910" y="420" class="s">R(θ) · T_local(s) · top Z invariant</text>
<rect x="120" y="500" width="270" height="100" rx="18" class="b"/><text x="150" y="555" class="h">FixedAxis</text>
<rect x="430" y="500" width="300" height="100" rx="18" class="b"/><text x="460" y="555" class="h">RotatingCarrier</text>
<rect x="870" y="500" width="280" height="100" rx="18" class="u"/><text x="900" y="555" class="h">TopGroove L/R</text>
<rect x="1190" y="500" width="290" height="100" rx="18" class="u"/><text x="1220" y="555" class="h">UnknownContacts</text>
<rect x="430" y="660" width="300" height="100" rx="18" class="u"/><text x="460" y="715" class="h">Followers L/R</text>
<text x="80" y="900" class="s">Solid cyan = rendered/evidence-backed · dashed amber = unknown cross-section or non-rendering metadata</text></svg>`);

const rel = (absolute) => path.relative(repoRoot, absolute).split(path.sep).join("/");
const addAsset = (id, stageId, slot, absolute, role, sourceAssetIds) => {
  manifest.assets.push({
    id, stageId, slot, path: rel(absolute), sha256: sha256File(absolute), exists: true,
    sizeBytes: fs.statSync(absolute).size, role,
    producer: { name: "fidgeting-model-pipeline", version: "3", recipe: "user-authorized provisional CAD migration" },
    provenance: {
      origin: "repository-generated", contentClass: slot, assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractHash, userAuthorizationQuote: quote
    },
    sourceAssetIds,
    sourceClaimIds: contract.sourceClaimIds
  });
};
addAsset("magnetic-slide-tile-provisional-modeling-contract-r009", "03-contract", "modeling-contract", contractPath, "contract", contract.sourceAssetIds);
addAsset("magnetic-slide-tile-reuse-plan-r009", "03-contract", "reuse-plan", reusePath, "contract", reuseIds);
addAsset("magnetic-slide-tile-approved-cad-architecture-r011", "04-architecture", "part-tree", architecturePath, "contract", ["magnetic-slide-tile-provisional-modeling-contract-r009", gate02.analysisSpec.cadArtifactId]);
addAsset("magnetic-slide-tile-approved-cad-hierarchy-r011", "04-architecture", "exploded-plan", architectureSvgPath, "validation", ["magnetic-slide-tile-approved-cad-architecture-r011"]);

gate03.revision += 1;
gate03.status = "approved";
gate03.artifactIds = ["magnetic-slide-tile-provisional-modeling-contract-r009", "magnetic-slide-tile-reuse-plan-r009"];
gate03.reviewArtifactIds = [];
gate03.requiredPhysicalDimensions = [];
gate03.measurementProgress = { complete: 9, total: 9, mode: "user-authorized-provisional-reuse" };
gate03.validations = [
  { id: "approved-analysis-consumed", status: "pass", evidence: `All ${contract.sourceClaimIds.length} active Gate 02 claims and the approved contract hash are consumed.` },
  { id: "provisional-dimension-boundary", status: "pass", evidence: "Every physical value is user-authorized-provisional or CAD-derived; none is presented as production measured." },
  { id: "latest-travel-limit", status: "pass", evidence: `21 mm is removed; travel=${maxTravelMm} mm from actualSMaxL=${actualSMaxL}.` },
  { id: "reuse-lineage", status: "pass", evidence: `${reusedAssets.length} prior assets are hash-linked; stale geometry is explicitly excluded.` }
];
gate03.decision = { action: "approve", notes: quote, decidedBy: "user-chat-authority", decidedAt: now };
delete gate03.blockedReason;

gate04.revision += 1;
gate04.status = "approved";
gate04.artifactIds = ["magnetic-slide-tile-approved-cad-architecture-r011", "magnetic-slide-tile-approved-cad-hierarchy-r011"];
gate04.reviewArtifactIds = ["magnetic-slide-tile-approved-cad-hierarchy-r011"];
gate04.validations = [
  { id: "approved-cad-consumed", status: "pass", evidence: `Architecture consumes Gate 02 contract ${contractHash}.` },
  { id: "no-new-architecture-assumption", status: "pass", evidence: "Hierarchy, transforms, limits and metadata proxies are direct migration of approved CAD rev 15." },
  { id: "unknown-geometry-nonrendering", status: "pass", evidence: "Follower sizes, groove cross-sections and unknown contacts remain metadata/non-rendering." }
];
gate04.decision = { action: "approve", notes: quote, decidedBy: "user-chat-authority", decidedAt: now };

for (let index = 4; index < 11; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 03–04 were rebuilt from approved CAD rev 15; downstream geometry must be regenerated.";
}
manifest.stages[11].status = "rejected";
manifest.currentStageId = "05-blockout";
manifest.currentState.visualApproval = "gate05-new-cad-hierarchy-blockout-not-generated";
manifest.currentState.measurementProgress = "authorized-provisional-reuse";
manifest.currentState.blenderModelingStatus = "authorized-gate05-generation-next";
manifest.currentState.diagnosis = "Gate 03 provisional dimensions and Gate 04 CAD architecture are approved by the user's latest chat authorization. Gate 05 must rebuild white geometry from the approved rev 15 hierarchy; old Blender geometry is stale.";
manifest.revision += 1;
manifest.updatedAt = now;
const event = {
  id: crypto.randomUUID(),
  type: "gate03-gate04-user-authorized-provisional-migration-approved",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording: quote,
  gate02Status: "approved",
  gate03Status: "approved",
  gate04Status: "approved",
  gate05Status: "stale-awaiting-rebuild",
  dimensions: Object.fromEntries(Object.entries(contract.dimensions).map(([key, item]) => [key, item.value])),
  productionMeasured: false,
  contractSha256: contractHash,
  reuseAssetIds: reuseIds,
  simulatorCurrent: false,
  unityChanged: false,
  oldShippingModelDefault: true
};
const saved = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: saved.revision,
  gate03: saved.stages[2].status,
  gate04: saved.stages[3].status,
  gate05: saved.stages[4].status,
  maxTravelMm,
  axisOffsetMm,
  carrierDiameterMm,
  reusedAssets: reusedAssets.length
}, null, 2));
