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
if (manifest.revision !== 175) throw new Error(`Expected pipeline revision 175, got ${manifest.revision}.`);
const gate05 = manifest.stages.find((stage) => stage.id === "05-blockout");
const gate06 = manifest.stages.find((stage) => stage.id === "06-geometry");
if (gate05.status !== "approved" || gate05.blockoutSpec?.revision !== 6) {
  throw new Error("Gate 05 rev 6 approval is not current.");
}
if (gate06.status !== "draft" || gate06.geometrySpec?.revision !== 4) {
  throw new Error("Gate 06 rev 4 is not the active draft.");
}
const output = path.dirname(fileURLToPath(import.meta.url));
const report = JSON.parse(fs.readFileSync(path.join(output, "geometry-validation.json"), "utf8"));
const audit = JSON.parse(fs.readFileSync(path.join(output, "blender-audit.json"), "utf8"));
if (!report.pass || !audit.pass) throw new Error("Gate 06 geometry or Blender audit failed.");
const contractHash = gate06.geometrySpec.governingContractSha256;
const gate05Hash = gate06.geometrySpec.gate05SourceSha256;
if (report.contractSha256 !== contractHash || report.gate05Source.sha256 !== gate05Hash) {
  throw new Error("Gate 06 consumed a stale source hash.");
}

const local = (filename) => path.join(output, filename);
const definitions = [
  ["magnetic-slide-tile-geometry-builder-r004", "builder", local("build_gate06_geometry.py"), "process"],
  ["magnetic-slide-tile-geometry-audit-script-r004", "audit-script", local("audit_gate06_geometry.py"), "process"],
  ["magnetic-slide-tile-geometry-register-r004", "registration-script", local("register_gate06_review.mjs"), "process"],
  ["magnetic-slide-tile-geometry-validation-r004", "geometry-validator", local("geometry-validation.json"), "validation"],
  ["magnetic-slide-tile-geometry-audit-r004", "blender-audit", local("blender-audit.json"), "validation"],
  ["magnetic-slide-tile-geometry-blend-r004", "blend", local("magnetic-slide-tile-geometry-r004.blend"), "source-model"],
  ["magnetic-slide-tile-geometry-interactive-r004", "interactive-model", local("magnetic-slide-tile-geometry-r004-review.glb"), "export"],
  ["magnetic-slide-tile-geometry-front-r004", "view-front", local("orthographic-front.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-back-r004", "view-back", local("orthographic-back.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-top-r004", "view-top", local("orthographic-top.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-bottom-r004", "view-bottom", local("orthographic-bottom.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-left-r004", "view-left", local("orthographic-left.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-right-r004", "view-right", local("orthographic-right.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-workbench-r004", "workbench", local("geometry-workbench.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-dimensions-r004", "dimension-overlay", local("dimension-overlay.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-pivot-r004", "pivot-overlay", local("fixed-axis-pivot-overlay.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-exploded-r004", "exploded-geometry", local("exploded-geometry.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-underside-r004", "underside-four-groove", local("top-underside-four-groove-closeup.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-flat-axis-r004", "flat-plane-raised-axis", local("bottom-flat-plane-raised-axis-closeup.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-section-aa-r004", "section-aa", local("section-aa-carrier-followers-grooves.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-tangency-r004", "tangency-step", local("tangency-step-overlay.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-closed-r004", "state-closed", local("state-closed.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-max-open-r004", "state-max-open", local("state-max-open.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-detent12-r004", "state-detent-12", local("state-detent-12.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-detent36-r004", "state-detent-36", local("state-detent-36.png"), "blender-render"],
  ["magnetic-slide-tile-gate06-workbench-copy-r004", "workbench-source", path.join(repoRoot, "tools/model-provenance-explorer/app.js"), "process"],
  ["magnetic-slide-tile-gate06-design-bible-r004", "design-bible", path.join(repoRoot, "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"), "process"],
  ["magnetic-slide-tile-gate06-implementation-status-r004", "implementation-status", path.join(repoRoot, "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"), "process"]
];
const sourceAssetIds = [
  "slider-analysis-mechanism-evidence-contract-r016",
  "magnetic-slide-tile-authorized-provisional-contract-r011",
  "magnetic-slide-tile-approved-four-track-architecture-r013",
  "magnetic-slide-tile-blockout-blend-r006",
  "magnetic-slide-tile-blockout-validation-r006",
  "magnetic-slide-tile-blockout-interactive-r006"
];
const sourceClaimIds = manifest.claims
  .filter((claim) => claim.stageId === "02-analysis" && !["superseded", "stale"].includes(claim.state))
  .map((claim) => claim.id);
for (const [id, slot, absolute, role] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing Gate 06 output ${absolute}.`);
  manifest.assets.push({
    id,
    stageId: "06-geometry",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: absolute.endsWith(".py") || absolute.endsWith(".mjs") ? "fidgeting-model-pipeline" : "Blender",
      version: absolute.endsWith(".py") || absolute.endsWith(".mjs") ? "4" : "5.2.0 LTS",
      recipe: "Gate 06 rev 4 same-source structural geometry evidence"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractHash,
      gate05SourceSha256: gate05Hash,
      approvedGate05Wording: "可以的",
      geometryDigest: report.canonicalGeometryDigest,
      dimensionsState: "user-authorized-provisional-not-production-measured",
      simulatorUsed: false,
      unityUsed: false
    },
    sourceAssetIds,
    sourceClaimIds
  });
}

gate06.status = "ready_for_review";
gate06.artifactIds = definitions.map(([id]) => id);
gate06.reviewArtifactIds = [
  "magnetic-slide-tile-geometry-interactive-r004",
  "magnetic-slide-tile-geometry-workbench-r004",
  "magnetic-slide-tile-geometry-front-r004",
  "magnetic-slide-tile-geometry-back-r004",
  "magnetic-slide-tile-geometry-top-r004",
  "magnetic-slide-tile-geometry-bottom-r004",
  "magnetic-slide-tile-geometry-left-r004",
  "magnetic-slide-tile-geometry-right-r004",
  "magnetic-slide-tile-geometry-dimensions-r004",
  "magnetic-slide-tile-geometry-pivot-r004",
  "magnetic-slide-tile-geometry-exploded-r004",
  "magnetic-slide-tile-geometry-underside-r004",
  "magnetic-slide-tile-geometry-flat-axis-r004",
  "magnetic-slide-tile-geometry-section-aa-r004",
  "magnetic-slide-tile-geometry-tangency-r004",
  "magnetic-slide-tile-geometry-closed-r004",
  "magnetic-slide-tile-geometry-max-open-r004",
  "magnetic-slide-tile-geometry-detent12-r004",
  "magnetic-slide-tile-geometry-detent36-r004"
];
gate06.inputDigest = gate05Hash;
gate06.outputDigest = report.canonicalGeometryDigest;
gate06.validations = [
  { id: "gate05-approved-source", status: "pass", evidence: `Gate 05 rev 6 approved with exact wording 可以的; blend SHA-256 ${gate05Hash}.` },
  { id: "contract-and-source-hashes", status: "pass", evidence: `Mechanism contract ${contractHash} and Gate 05 source hash are embedded in the blend, GLB provenance and every asset.` },
  { id: "same-geometry-all-views", status: "pass", evidence: `All views and poses use evaluated geometry digest ${report.canonicalGeometryDigest}.` },
  { id: "bounds-and-thickness", status: "pass", evidence: "Provisional closed bounds are 50×31×12 mm; thickness stack is 5.875+0.25+5.875=12 mm." },
  { id: "flat-plane-raised-axis", status: "pass", evidence: `Bottom top-plane deviation is ${report.topPlane.maximumDeviationMm} mm against 0.001 mm; axis boss protrudes 0.2 mm.` },
  { id: "carrier-and-followers", status: "pass", evidence: `Carrier clearance is ${report.carrierPacking.clearanceBelowPlaneMm} mm; bilateral follower X alignment error is 0 mm.` },
  { id: "four-groove-ball-contract", status: "pass", evidence: "Four finite underside grooves preserve outer slide and inner linkage roles; groove width 1.8–3.0 mm and ball candidates 2–3 mm." },
  { id: "transform-and-containment", status: "pass", evidence: `${report.denseSweep.sampleCount} samples pass at ${report.denseSweep.angularStepDegrees}° across five travel fractions; fixed axis and top z-order pass.` },
  { id: "mesh-export-readiness", status: "pass", evidence: "Eight core meshes have 0 nonmanifold edges, 0 invalid normals, UV layers and finite geometric tangent bases." },
  { id: "blender-audit", status: "pass", evidence: `Independent Blender ${audit.blenderVersion} audit passes ${Object.keys(audit.checks).length} checks.` },
  { id: "scope", status: "pass", evidence: "No materials, Simulator, Unity, build, install or device work occurred." }
];
gate06.geometrySpec = {
  ...gate06.geometrySpec,
  canonicalGeometryDigest: report.canonicalGeometryDigest,
  exactBoundsMm: [50, 31, 12],
  thicknessStackMm: report.dimensions.thicknessStack,
  topPlane: report.topPlane,
  carrierPacking: report.carrierPacking,
  followerAlignment: report.followerAlignment,
  denseSweep: report.denseSweep,
  manifold: report.nonmanifoldEdges,
  uvTangentAudit: report.uvTangentAudit,
  authoritativeBlendSha256: sha256File(local("magnetic-slide-tile-geometry-r004.blend")),
  interactiveGlbSha256: sha256File(local("magnetic-slide-tile-geometry-r004-review.glb"))
};
gate06.readiness = {
  ready: true,
  blockers: [],
  note: "Review the interactive Gate 06 GLB first, then the same-source orthographic, section and overlay evidence. Visual approval is pending; nothing was pushed to a phone."
};
delete gate06.staleReason;
for (let index = 6; index < 11; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 06 rev 4 geometry awaits visual approval.";
}
manifest.stages[11].status = "rejected";
manifest.currentStageId = "06-geometry";
manifest.currentState.visualApproval = "gate06-rev4-ready-for-review-visual-approval-pending-not-pushed";
manifest.currentState.blenderModelingStatus = "gate06-same-source-geometry-ready-for-review";
manifest.currentState.simulatorStatus = "internal-superseded-not-current";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-default-gate06-geometry";
manifest.currentState.diagnosis = "Gate 05 rev 6 is approved. Gate 06 rev 4 exposes the identical geometry through GLB, orthographic, section, overlay and representative-pose evidence.";
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate06-same-source-geometry-ready",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate05ApprovalWording: "可以的",
  gate05SourceSha256: gate05Hash,
  contractSha256: contractHash,
  geometryDigest: report.canonicalGeometryDigest,
  artifactIds: gate06.artifactIds,
  reviewArtifactIds: gate06.reviewArtifactIds,
  metrics: {
    boundsMm: [50, 31, 12],
    topPlaneMaximumDeviationMm: report.topPlane.maximumDeviationMm,
    axisBossProtrusionMm: report.dimensions.axisBossProtrusionMm,
    carrierClearanceBelowPlaneMm: report.carrierPacking.clearanceBelowPlaneMm,
    denseSweepSamples: report.denseSweep.sampleCount
  },
  visualApprovalPending: true,
  simulatorUsed: false,
  unityChanged: false,
  buildInstallOrDevice: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate05: saved.stages[4].status,
  gate06: saved.stages[5].status,
  artifactCount: gate06.artifactIds.length,
  reviewArtifactCount: gate06.reviewArtifactIds.length,
  geometryDigest: report.canonicalGeometryDigest
}, null, 2));

