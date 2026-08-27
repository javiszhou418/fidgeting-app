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
if (manifest.revision !== 166) throw new Error(`Expected pipeline revision 166, got ${manifest.revision}.`);
const output = path.dirname(fileURLToPath(import.meta.url));
const report = JSON.parse(fs.readFileSync(path.join(output, "blockout-validation.json"), "utf8"));
if (!report.pass) throw new Error("Gate 05 rev 5 validation did not pass.");
const contractHash = "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea";
if (report.contractSha256 !== contractHash) throw new Error("Gate 05 report consumed a stale contract.");
const now = new Date().toISOString();
const exactUserWording = "Treat the user’s latest four-track/raised-axis feedback as white-model feedback and rebuild Gate 05 now, rather than sending them back to CAD/measurement approval.";
const sourceAssetIds = [
  "slider-analysis-mechanism-evidence-contract-r016",
  "magnetic-slide-tile-authorized-provisional-contract-r011",
  "magnetic-slide-tile-reuse-plan-r011",
  "magnetic-slide-tile-approved-four-track-architecture-r013"
];
const definitions = [
  ["magnetic-slide-tile-blockout-builder-r005", "builder", "build_gate05_blockout.py", "process"],
  ["magnetic-slide-tile-blockout-validation-r005", "silhouette-validator", "blockout-validation.json", "validation"],
  ["magnetic-slide-tile-blockout-blend-r005", "blend", "magnetic-slide-tile-blockout-r005.blend", "source-model"],
  ["magnetic-slide-tile-blockout-interactive-r005", "interactive-model", "magnetic-slide-tile-blockout-r005-review.glb", "export"],
  ["magnetic-slide-tile-blockout-hero-r005", "blockout-hero", "white-hero.png", "blender-render"],
  ["magnetic-slide-tile-blockout-closed-r005", "blockout-closed", "white-closed.png", "blender-render"],
  ["magnetic-slide-tile-blockout-max-open-r005", "blockout-slide", "white-max-open.png", "blender-render"],
  ["magnetic-slide-tile-blockout-detent12-r005", "blockout-spin", "white-detent-12.png", "blender-render"],
  ["magnetic-slide-tile-blockout-detent36-r005", "blockout-compound", "white-detent-36.png", "blender-render"],
  ["magnetic-slide-tile-blockout-underside-r005", "blockout-underside", "white-underside-four-grooves.png", "blender-render"],
  ["magnetic-slide-tile-blockout-axis-closeup-r005", "blockout-mechanism-closeup", "white-raised-axis-carrier-closeup.png", "blender-render"],
  ["magnetic-slide-tile-blockout-exploded-r005", "blockout-exploded", "white-exploded-hierarchy.png", "blender-render"],
  ["magnetic-slide-tile-pivot-overlap-r005", "pivot-overlay", "pivot-overlap-overlay.png", "blender-render"]
];
const sourceClaimIds = manifest.claims
  .filter((claim) => claim.stageId === "02-analysis" && !["superseded", "stale"].includes(claim.state))
  .map((claim) => claim.id);
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
      version: filename.endsWith(".py") ? "5" : "5.2.0 LTS",
      recipe: "Gate 05 rev 5 four-track raised-axis deterministic white model"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      exactUserWording,
      mechanismEvidenceContractSha256: contractHash,
      dimensionsState: "user-authorized-provisional-not-production-measured",
      simulatorUsed: false,
      unityUsed: false
    },
    sourceAssetIds,
    sourceClaimIds
  });
}

const gate05 = manifest.stages.find((stage) => stage.id === "05-blockout");
gate05.revision += 1;
gate05.status = "ready_for_review";
gate05.artifactIds = definitions.map(([id]) => id);
gate05.reviewArtifactIds = [
  "magnetic-slide-tile-blockout-interactive-r005",
  "magnetic-slide-tile-blockout-hero-r005",
  "magnetic-slide-tile-blockout-closed-r005",
  "magnetic-slide-tile-blockout-max-open-r005",
  "magnetic-slide-tile-blockout-detent12-r005",
  "magnetic-slide-tile-blockout-detent36-r005",
  "magnetic-slide-tile-blockout-underside-r005",
  "magnetic-slide-tile-blockout-axis-closeup-r005",
  "magnetic-slide-tile-blockout-exploded-r005",
  "magnetic-slide-tile-pivot-overlap-r005"
];
gate05.validations = [
  { id: "current-contract-consumed", status: "pass", evidence: `Every rev 5 output records ${contractHash}.` },
  { id: "four-recessed-grooves", status: "pass", evidence: "MovingTop underside has four finite boolean recesses: outer two slide and inner two link the carrier." },
  { id: "raised-axis-no-cavity", status: "pass", evidence: "FixedAxisBoss has positive 2 mm provisional protrusion; BottomExterior records no axis cavity." },
  { id: "carrier-and-followers", status: "pass", evidence: "Circular RotatingCarrier has bilateral cutouts, two carrier followers and 2.5 mm ball candidates." },
  { id: "provisional-boundary", status: "pass", evidence: "50×31×12 mm remains user-authorized provisional, not production measured." },
  { id: "compound-transform", status: "pass", evidence: "MovingTop and carrier share fixed-axis rotation; TopLocalSlide supplies local translation." },
  { id: "travel-and-overlap", status: "pass", evidence: `${report.denseSweep.sampleCount} samples at ${report.denseSweep.angularStepDegrees}° pass; max travel is ${report.dimensionsMm.maxTravel} mm.` },
  { id: "smooth-bottom", status: "pass", evidence: "BottomExterior uses the reused 256-segment capsule profile and has smooth, rail-free user-facing skins." },
  { id: "unknowns-preserved", status: "pass", evidence: "Ball material/count, springs, preload, groove engineering section and tolerances remain unknown." },
  { id: "zero-self-motion", status: "pass", evidence: "The blend has no actions, drivers or keyframes and exports no animation." },
  { id: "interactive-review", status: "pass", evidence: "The semi-exploded real GLB is the first review artifact." },
  { id: "scope", status: "pass", evidence: "No Simulator, material progression, Unity, build, install or device work occurred." }
];
gate05.decision = null;
gate05.blockoutSpec = {
  revision: 5,
  governingContractSha256: contractHash,
  dimensionsMm: report.dimensionsMm,
  hierarchy: report.hierarchy,
  topTransform: "R_fixedAxis(theta) * T_local(s)",
  trackRoles: { outer: "fore-aft-slide", inner: "central-axis-link", count: 4 },
  ballCandidatesMm: [2, 3],
  trackWidthMm: [1.8, 3],
  raisedAxisBoss: true,
  recessedAxis: false,
  requiredPoses: report.poses.map(({ id, travelMm, angleDeg }) => ({ id, travelMm, angleDeg })),
  materials: "white-clay-only; approved art, material and light assets remain deferred",
  unityAssetChanged: false
};
gate05.readiness = {
  ready: true,
  blockers: [],
  note: "Review the rev 5 GLB and white-model views. Visual approval is pending; nothing was pushed to a phone."
};
delete gate05.staleReason;
for (let index = 5; index < 11; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 05 rev 5 awaits white-model visual approval.";
}
manifest.stages[11].status = "rejected";
manifest.currentStageId = "05-blockout";
manifest.currentState.visualApproval = "gate05-rev5-ready-for-review-visual-approval-pending";
manifest.currentState.blenderModelingStatus = "gate05-four-track-raised-axis-white-model-ready-for-review";
manifest.currentState.simulatorStatus = "internal-superseded-not-current";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-default-gate05";
manifest.currentState.diagnosis = "Gate 05 rev 5 replaces the rejected cavity model with four underside grooves, a raised FixedAxisBoss, circular cutout carrier, followers and ball candidates. Visual approval is pending; Gate 06 remains stale.";
manifest.revision += 1;
manifest.updatedAt = now;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-four-track-raised-axis-white-model-ready",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording,
  contractSha256: contractHash,
  artifactIds: gate05.artifactIds,
  reviewArtifactIds: gate05.reviewArtifactIds,
  denseSweepSamples: report.denseSweep.sampleCount,
  validationPass: true,
  visualApprovalPending: true,
  productionMeasured: false,
  simulatorUsed: false,
  unityChanged: false,
  buildInstallOrPhonePush: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate05Status: saved.stages[4].status,
  artifactCount: saved.stages[4].artifactIds.length,
  reviewArtifactCount: saved.stages[4].reviewArtifactIds.length,
  currentStageId: saved.currentStageId
}, null, 2));

