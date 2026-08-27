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
const gate05 = manifest.stages.find((stage) => stage.id === "05-blockout");
if (gate05.blockoutSpec?.revision !== 5 || gate05.status !== "ready_for_review") {
  throw new Error(`Expected blockout spec rev 5 ready_for_review, got ${gate05.blockoutSpec?.revision} ${gate05.status}.`);
}
const output = path.dirname(fileURLToPath(import.meta.url));
const readJson = (filename) => JSON.parse(fs.readFileSync(path.join(output, filename), "utf8"));
const report = readJson("blockout-validation.json");
const audit = readJson("blender-audit.json");
const comparison = readJson("geometry-comparison.json");
if (!report.pass || !audit.pass || !comparison.pass) throw new Error("Gate 05 rev 6 evidence failed.");
const contractHash = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea";
if (report.contractSha256 !== contractHash) throw new Error("Gate 05 rev 6 consumed a stale contract.");

const now = new Date().toISOString();
const exactUserWording = "Gate 05 rev 5 structure is correct but rejects one visible geometry detail: the bottom plate’s top surface must also be a flat continuous plane.";
const sourceAssetIds = [
  "slider-analysis-mechanism-evidence-contract-r016",
  "magnetic-slide-tile-authorized-provisional-contract-r011",
  "magnetic-slide-tile-reuse-plan-r011",
  "magnetic-slide-tile-approved-four-track-architecture-r013",
  "magnetic-slide-tile-blockout-builder-r005",
  "magnetic-slide-tile-blockout-validation-r005",
  "magnetic-slide-tile-blockout-blend-r005"
];
const definitions = [
  ["magnetic-slide-tile-blockout-builder-r006", "builder", "build_gate05_blockout.py", "process"],
  ["magnetic-slide-tile-blockout-audit-script-r006", "audit-script", "audit_gate05_blockout.py", "process"],
  ["magnetic-slide-tile-blockout-comparison-script-r006", "comparison-script", "compare_rev5_rev6_geometry.py", "process"],
  ["magnetic-slide-tile-blockout-validation-r006", "silhouette-validator", "blockout-validation.json", "validation"],
  ["magnetic-slide-tile-blockout-audit-r006", "blender-audit", "blender-audit.json", "validation"],
  ["magnetic-slide-tile-blockout-comparison-r006", "geometry-comparison", "geometry-comparison.json", "validation"],
  ["magnetic-slide-tile-blockout-blend-r006", "blend", "magnetic-slide-tile-blockout-r006.blend", "source-model"],
  ["magnetic-slide-tile-blockout-interactive-r006", "interactive-model", "magnetic-slide-tile-blockout-r006-review.glb", "export"],
  ["magnetic-slide-tile-blockout-hero-r006", "blockout-hero", "white-hero.png", "blender-render"],
  ["magnetic-slide-tile-blockout-closed-r006", "blockout-closed", "white-closed.png", "blender-render"],
  ["magnetic-slide-tile-blockout-max-open-r006", "blockout-slide", "white-max-open.png", "blender-render"],
  ["magnetic-slide-tile-blockout-detent12-r006", "blockout-spin", "white-detent-12.png", "blender-render"],
  ["magnetic-slide-tile-blockout-detent36-r006", "blockout-compound", "white-detent-36.png", "blender-render"],
  ["magnetic-slide-tile-blockout-flat-plane-r006", "blockout-flat-plane", "white-bottom-flat-plane-closeup.png", "blender-render"],
  ["magnetic-slide-tile-blockout-axis-closeup-r006", "blockout-mechanism-closeup", "white-raised-axis-closeup.png", "blender-render"],
  ["magnetic-slide-tile-blockout-underside-r006", "blockout-underside", "white-underside-four-grooves.png", "blender-render"],
  ["magnetic-slide-tile-blockout-exploded-r006", "blockout-exploded", "white-exploded-hierarchy.png", "blender-render"],
  ["magnetic-slide-tile-pivot-overlap-r006", "pivot-overlay", "pivot-overlap-overlay.png", "blender-render"]
];
const sourceClaimIds = manifest.claims
  .filter((claim) => claim.stageId === "02-analysis" && !["superseded", "stale"].includes(claim.state))
  .map((claim) => claim.id);
for (const [id, slot, filename, role] of definitions) {
  const absolute = path.join(output, filename);
  if (!fs.existsSync(absolute)) throw new Error(`Missing Gate 05 rev 6 output ${filename}.`);
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
      version: filename.endsWith(".py") ? "6" : "5.2.0 LTS",
      recipe: "Gate 05 rev 6 flat continuous BottomExterior top-plane correction"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      exactUserWording,
      mechanismEvidenceContractSha256: contractHash,
      partialApproval: "rev5 hierarchy and kinematics accepted; bottom top recess rejected",
      dimensionsState: "user-authorized-provisional-not-production-measured",
      simulatorUsed: false,
      unityUsed: false
    },
    sourceAssetIds,
    sourceClaimIds
  });
}

gate05.revision += 1;
gate05.status = "ready_for_review";
gate05.artifactIds = definitions.map(([id]) => id);
gate05.reviewArtifactIds = [
  "magnetic-slide-tile-blockout-interactive-r006",
  "magnetic-slide-tile-blockout-hero-r006",
  "magnetic-slide-tile-blockout-closed-r006",
  "magnetic-slide-tile-blockout-max-open-r006",
  "magnetic-slide-tile-blockout-flat-plane-r006",
  "magnetic-slide-tile-blockout-axis-closeup-r006",
  "magnetic-slide-tile-blockout-detent12-r006",
  "magnetic-slide-tile-blockout-detent36-r006",
  "magnetic-slide-tile-blockout-underside-r006",
  "magnetic-slide-tile-blockout-exploded-r006",
  "magnetic-slide-tile-pivot-overlap-r006"
];
gate05.validations = [
  { id: "rev5-partial-approval", status: "pass", evidence: "User accepted rev 5 hierarchy and kinematics but rejected its recessed BottomExterior top skin." },
  { id: "flat-plane-sampling", status: "pass", evidence: `${report.flatPlaneMetrics.sampleCount} samples at ${report.flatPlaneMetrics.stepMm} mm spacing measure ${report.flatPlaneMetrics.maximumDeviationMm} mm maximum deviation against ${report.flatPlaneMetrics.toleranceMm} mm tolerance.` },
  { id: "no-recess-geometry", status: "pass", evidence: "BottomExterior has no Boolean/recess modifier, negative depth, cavity, dish, pocket or separate recessed rim." },
  { id: "raised-axis-boss", status: "pass", evidence: `FixedAxisBoss remains separate and protrudes ${report.dimensionsMm.axisBossExposedProtrusion} mm above the flat plane.` },
  { id: "carrier-hidden", status: "pass", evidence: `Carrier, followers and balls remain at least ${report.carrierPacking.clearanceBelowPlaneMm.toFixed(4)} mm below the exterior plane.` },
  { id: "accepted-geometry-preserved", status: "pass", evidence: "Independent blend comparison preserves top, boss, carrier, follower and ball mesh shapes; only BottomExterior changed and the rejected rev 5 rim was removed." },
  { id: "four-grooves-preserved", status: "pass", evidence: "MovingTopBody mesh fingerprint matches rev 5 and retains four underside grooves." },
  { id: "compound-transform", status: "pass", evidence: "Fixed-axis rotation and local top translation poses match rev 5." },
  { id: "travel-and-overlap", status: "pass", evidence: `${report.denseSweep.sampleCount} containment samples pass at ${report.denseSweep.angularStepDegrees}° angular steps.` },
  { id: "blender-audit", status: "pass", evidence: "Saved blend hierarchy, flat plane, manifold geometry, zero animation and old-shipping boundary passed." },
  { id: "scope", status: "pass", evidence: "No material, Simulator, Unity, build, install or device work occurred." }
];
gate05.decision = null;
gate05.blockoutSpec = {
  revision: 6,
  governingContractSha256: contractHash,
  dimensionsMm: report.dimensionsMm,
  hierarchy: report.hierarchy,
  bottomTopSurface: "continuous flat plane except separate raised FixedAxisBoss",
  flatPlaneMetrics: report.flatPlaneMetrics,
  carrierPacking: report.carrierPacking,
  topTransform: "R_fixedAxis(theta) * T_local(s)",
  trackRoles: { outer: "fore-aft-slide", inner: "central-axis-link", count: 4 },
  ballCandidatesMm: [2, 3],
  trackWidthMm: [1.8, 3],
  recessedAxis: false,
  materials: "white-clay-only",
  unityAssetChanged: false
};
gate05.readiness = {
  ready: true,
  blockers: [],
  note: "Review rev 6 GLB and flat-plane views. Visual approval is pending; nothing was pushed to a phone."
};
delete gate05.staleReason;
for (let index = 5; index < 11; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 05 rev 6 awaits white-model visual approval.";
}
manifest.stages[11].status = "rejected";
manifest.currentStageId = "05-blockout";
manifest.currentState.visualApproval = "gate05-rev6-ready-for-review-visual-approval-pending";
manifest.currentState.blenderModelingStatus = "gate05-flat-bottom-top-plane-white-model-ready-for-review";
manifest.currentState.simulatorStatus = "internal-superseded-not-current";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-default-gate05-rev6";
manifest.currentState.diagnosis = "Gate 05 rev 5 structure was accepted, but its recessed lower top skin was rejected. Rev 6 replaces only that exterior surface with a continuous flat plane and preserves the accepted mechanism.";
manifest.revision += 1;
manifest.updatedAt = now;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-flat-bottom-top-plane-white-model-ready",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording,
  partialApproval: {
    accepted: "Gate 05 rev 5 hierarchy and kinematics",
    rejected: "recessed/concave BottomExterior top surface",
    supersededRevision: 5
  },
  contractSha256: contractHash,
  artifactIds: gate05.artifactIds,
  reviewArtifactIds: gate05.reviewArtifactIds,
  planeMetrics: report.flatPlaneMetrics,
  carrierPacking: report.carrierPacking,
  geometryComparison: comparison.checks,
  denseSweepSamples: report.denseSweep.sampleCount,
  visualApprovalPending: true,
  simulatorUsed: false,
  unityChanged: false,
  buildInstallOrPhonePush: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate05Revision: saved.stages[4].revision,
  gate05Status: saved.stages[4].status,
  reviewArtifactCount: saved.stages[4].reviewArtifactIds.length,
  planeMetrics: report.flatPlaneMetrics
}, null, 2));

