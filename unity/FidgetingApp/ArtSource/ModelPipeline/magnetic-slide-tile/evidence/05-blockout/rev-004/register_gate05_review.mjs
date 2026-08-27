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
if (manifest.revision !== 160) throw new Error(`Expected pipeline revision 160, got ${manifest.revision}.`);
const now = new Date().toISOString();
const output = path.dirname(fileURLToPath(import.meta.url));
const report = JSON.parse(fs.readFileSync(path.join(output, "blockout-validation.json"), "utf8"));
if (!report.pass) throw new Error("Gate 05 validation report does not pass.");
const contractHash = "b4318452f163ef7c105c826d4466a739a1dd0d942d4d74d921c29c39e02a84f2";
const sourceAssetIds = [
  "magnetic-slide-tile-provisional-modeling-contract-r009",
  "magnetic-slide-tile-reuse-plan-r009",
  "magnetic-slide-tile-approved-cad-architecture-r011"
];
const definitions = [
  ["magnetic-slide-tile-blockout-builder-r004", "builder", "build_gate05_blockout.py", "process"],
  ["magnetic-slide-tile-blockout-validation-r004", "silhouette-validator", "blockout-validation.json", "validation"],
  ["magnetic-slide-tile-blockout-blend-r004", "blend", "magnetic-slide-tile-blockout-r004.blend", "source-model"],
  ["magnetic-slide-tile-blockout-interactive-r004", "interactive-model", "magnetic-slide-tile-blockout-r004-review.glb", "export"],
  ["magnetic-slide-tile-blockout-hero-r004", "blockout-hero", "white-hero.png", "blender-render"],
  ["magnetic-slide-tile-blockout-closed-r004", "blockout-closed", "white-closed.png", "blender-render"],
  ["magnetic-slide-tile-blockout-max-open-r004", "blockout-slide", "white-max-open.png", "blender-render"],
  ["magnetic-slide-tile-blockout-detent12-r004", "blockout-spin", "white-detent-12.png", "blender-render"],
  ["magnetic-slide-tile-blockout-detent36-r004", "blockout-compound", "white-detent-36.png", "blender-render"],
  ["magnetic-slide-tile-blockout-underside-r004", "blockout-underside", "white-underside-grooves.png", "blender-render"],
  ["magnetic-slide-tile-blockout-exploded-r004", "blockout-exploded", "white-exploded-hierarchy.png", "blender-render"],
  ["magnetic-slide-tile-pivot-overlap-r004", "pivot-overlay", "pivot-overlap-overlay.png", "blender-render"]
];
const registeredIds = [];
for (const [id, slot, filename, role] of definitions) {
  const absolute = path.join(output, filename);
  if (!fs.existsSync(absolute)) throw new Error(`Missing Gate 05 output ${filename}.`);
  manifest.assets.push({
    id,
    stageId: "05-blockout",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: filename.endsWith(".py") ? "fidgeting-model-pipeline" : "Blender",
      version: filename.endsWith(".py") ? "3" : "5.2.0 LTS",
      recipe: "Gate 05 rev 4 approved-CAD white blockout"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractHash,
      dimensionsState: "user-authorized-provisional-not-production-measured",
      simulatorUsed: false,
      unityUsed: false
    },
    sourceAssetIds,
    sourceClaimIds: manifest.claims
      .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
      .map((claim) => claim.id)
  });
  registeredIds.push(id);
}

const gate05 = manifest.stages.find((stage) => stage.id === "05-blockout");
gate05.revision += 1;
gate05.status = "ready_for_review";
gate05.artifactIds = registeredIds;
gate05.reviewArtifactIds = [
  "magnetic-slide-tile-blockout-interactive-r004",
  "magnetic-slide-tile-blockout-hero-r004",
  "magnetic-slide-tile-blockout-closed-r004",
  "magnetic-slide-tile-blockout-max-open-r004",
  "magnetic-slide-tile-blockout-detent12-r004",
  "magnetic-slide-tile-blockout-detent36-r004",
  "magnetic-slide-tile-blockout-underside-r004",
  "magnetic-slide-tile-blockout-exploded-r004",
  "magnetic-slide-tile-pivot-overlap-r004"
];
gate05.validations = [
  { id: "approved-contract-consumed", status: "pass", evidence: `Blend, GLB, report and images record ${contractHash}.` },
  { id: "provisional-boundary", status: "pass", evidence: "50×31×12 mm and derived mechanism values are explicitly user-authorized provisional, not production measured." },
  { id: "new-cad-hierarchy", status: "pass", evidence: "BottomExterior, FixedAxis, RotatingCarrier, followers, TopPlate, twin groove metadata and unknown-contact metadata match approved CAD rev 15." },
  { id: "compound-transform", status: "pass", evidence: "Top uses R_fixedAxis(θ) · T_local(-s); 0°, 12° and 36° poses render without axis drift." },
  { id: "travel-and-overlap", status: "pass", evidence: `Travel is ${report.dimensionsMm.maxTravel} mm. ${report.denseSweep.sampleCount} dense samples pass; minimum overlap margin is ${report.denseSweep.minimumMarginMm} mm.` },
  { id: "smooth-capsule", status: "pass", evidence: "Analytic capsule uses 256 segments per semicircle, 8-segment bevels, closed manifold meshes and positive volumes." },
  { id: "unknowns-not-faked", status: "pass", evidence: "Groove cross-sections, follower sizes and hidden contacts remain non-rendering metadata/centerline evidence." },
  { id: "no-self-motion", status: "pass", evidence: "No actions, keyframes or drivers exist; scene frame range is one frame and self_motion=false." },
  { id: "interactive-review", status: "pass", evidence: "The real review GLB is registered as the first review artifact." },
  { id: "scope", status: "pass", evidence: "No Simulator, Unity, build, install or phone work occurred. Old shipping Unity remains default." }
];
gate05.decision = null;
gate05.blockoutSpec = {
  revision: 4,
  governingContractSha256: contractHash,
  dimensionsMm: report.dimensionsMm,
  overlapScaleReconciliation: report.overlapScaleReconciliation,
  hierarchy: report.hierarchy,
  topTransform: "R_fixedAxis(theta) * T_local(-s)",
  detents: { count: 30, stepDegrees: 12 },
  requiredPoses: report.poses.map(({ id, travelMm, angleDeg }) => ({ id, travelMm, angleDeg })),
  hiddenEngineering: "unknown-nonrendering-metadata",
  materials: "white-clay-only; prior material recipes deferred to Gate 07",
  unityAssetChanged: false
};
gate05.readiness = {
  ready: true,
  blockers: [],
  note: "Review the registered GLB and white-model views. The user's latest explicit chat decision is final."
};
delete gate05.staleReason;
for (let index = 5; index < 11; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 05 rev 4 awaits visual approval.";
}
manifest.stages[11].status = "rejected";
manifest.currentStageId = "05-blockout";
manifest.currentState.visualApproval = "gate05-rev4-ready-for-review";
manifest.currentState.blenderModelingStatus = "gate05-white-blockout-ready-for-review";
manifest.currentState.simulatorStatus = "internal-superseded-not-current";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default";
manifest.currentState.diagnosis = "Gate 05 rev 4 is a deterministic white blockout rebuilt from approved CAD rev 15. It awaits the user's visual decision before Gate 06.";
manifest.revision += 1;
manifest.updatedAt = now;

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-approved-cad-white-blockout-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: now,
  contractSha256: contractHash,
  artifactIds: registeredIds,
  reviewArtifactIds: gate05.reviewArtifactIds,
  validationPass: true,
  productionMeasured: false,
  simulatorUsed: false,
  unityChanged: false,
  buildInstallOrPhonePush: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate05Status: saved.stages[4].status,
  artifactCount: saved.stages[4].artifactIds.length,
  reviewArtifactCount: saved.stages[4].reviewArtifactIds.length
}, null, 2));
