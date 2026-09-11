#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const manifest = loadManifest(modelId);
const gate05 = manifest.stages.find((stage) => stage.id === "05-blockout");
const gate06 = manifest.stages.find((stage) => stage.id === "06-geometry");
if (manifest.revision !== 221 || gate05?.status !== "ready_for_review" || gate05?.revision !== 12) {
  throw new Error(`Unexpected pipeline state ${manifest.revision}/${gate05?.status}/${gate05?.revision}.`);
}
const output = path.dirname(fileURLToPath(import.meta.url));
const report = JSON.parse(fs.readFileSync(path.join(output, "geometry-validation.json"), "utf8"));
const audit = JSON.parse(fs.readFileSync(path.join(output, "blender-audit.json"), "utf8"));
if (!report.pass || !audit.pass) throw new Error("Gate 06 geometry evidence did not pass.");
const exactUserWording = "可以，可以继续推进。";
const contractSha = "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571";
const gate05SourceSha = "f587be803cf98e134f173e961fe4e096708f08916af51d971b0ef381d51c11a2";
if (report.contractSha256 !== contractSha || report.gate05Source.sha256 !== gate05SourceSha) {
  throw new Error("Gate 06 report consumed stale source evidence.");
}
const local = (filename) => path.join(output, filename);
const definitions = [
  ["magnetic-slide-tile-geometry-builder-r005", "builder", local("build_gate06_endpoint_geometry.py"), "process"],
  ["magnetic-slide-tile-geometry-audit-script-r005", "audit-script", local("audit_gate06_endpoint_geometry.py"), "process"],
  ["magnetic-slide-tile-geometry-register-r005", "registration-script", local("register_gate06_endpoint_review.mjs"), "process"],
  ["magnetic-slide-tile-geometry-validation-r005", "geometry-validator", local("geometry-validation.json"), "validation"],
  ["magnetic-slide-tile-geometry-audit-r005", "blender-audit", local("blender-audit.json"), "validation"],
  ["magnetic-slide-tile-geometry-blend-r005", "blend", local("magnetic-slide-tile-geometry-r005.blend"), "source-model"],
  ["magnetic-slide-tile-geometry-interactive-r005", "interactive-model", local("magnetic-slide-tile-geometry-r005-review.glb"), "export"],
  ["magnetic-slide-tile-geometry-state-machine-r005", "state-machine-overlay", local("endpoint-interlock-pose-overlay.svg"), "contract"],
  ...["front", "back", "top", "bottom", "left", "right"].map((view) => [
    `magnetic-slide-tile-geometry-${view}-r005`,
    `view-${view}`,
    local(`orthographic-${view}.png`),
    "blender-render",
  ]),
  ["magnetic-slide-tile-geometry-workbench-r005", "workbench", local("geometry-workbench.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-dimensions-r005", "dimension-overlay", local("dimension-overlay.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-pivot-r005", "pivot-overlay", local("fixed-axis-pivot-overlay.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-exploded-r005", "exploded-geometry", local("exploded-geometry.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-underside-r005", "underside-four-groove", local("top-underside-four-groove-closeup.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-flat-axis-r005", "flat-plane-raised-axis", local("bottom-flat-plane-raised-axis-closeup.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-section-aa-r005", "section-aa", local("section-aa-carrier-followers-grooves.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-closed-r005", "state-closed", local("state-closed.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-max0-r005", "state-max-open-0", local("state-max-open-0.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-max12-r005", "state-max-open-12", local("state-max-open-12.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-max36-r005", "state-max-open-36", local("state-max-open-36.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-max360-r005", "state-max-open-360", local("state-max-open-360.png"), "blender-render"],
  ["magnetic-slide-tile-geometry-mid-rotation-blocked-r005", "state-prohibited-mid-slide-rotation", local("state-prohibited-mid-slide-rotation.png"), "blender-render"],
  ["magnetic-slide-tile-gate06-workbench-copy-r005", "workbench-source", path.join(repoRoot, "tools/model-provenance-explorer/app.js"), "process"],
  ["magnetic-slide-tile-gate06-design-bible-r005", "design-bible", path.join(repoRoot, "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"), "process"],
  ["magnetic-slide-tile-gate06-implementation-status-r005", "implementation-status", path.join(repoRoot, "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"), "process"],
];
for (const [, , absolute] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing Gate 06 artifact ${absolute}.`);
}
const definitionIds = new Set(definitions.map(([id]) => id));
manifest.assets = manifest.assets.filter((asset) => !definitionIds.has(asset.id));
const sourceAssetIds = [
  "slider-analysis-mechanism-evidence-contract-r017",
  "slider-analysis-interactive-cad-geometry-config-r017",
  "magnetic-slide-tile-endpoint-interlock-architecture-r014",
  "magnetic-slide-tile-endpoint-interlock-state-machine-r014",
  "magnetic-slide-g05-r012-blend",
  "magnetic-slide-g05-r012-validation",
  "magnetic-slide-g05-r012-endpoint-interlock-video",
  "magnetic-slide-g05-r012-endpoint-interlock-validation",
];
const sourceClaimIds = manifest.claims
  .filter((claim) => claim.stageId === "02-analysis" && !["superseded", "stale"].includes(claim.state))
  .map((claim) => claim.id);
for (const [id, slot, absolute, role] of definitions) {
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
      name: absolute.endsWith(".blend") || absolute.endsWith(".glb") || absolute.endsWith(".png")
        ? "Blender" : "fidgeting-model-pipeline",
      version: absolute.endsWith(".blend") || absolute.endsWith(".glb") || absolute.endsWith(".png")
        ? "5.2.0 LTS" : "endpoint-interlock-2026-08-28",
      recipe: "Gate 06 rev 5 unchanged geometry under mechanism contract rev 17",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractSha,
      gate05SourceSha256: gate05SourceSha,
      gate05ApprovalExactWording: exactUserWording,
      geometryDigest: report.canonicalGeometryDigest,
      geometryChanged: false,
      dimensionsState: "user-authorized-provisional-not-production-measured",
      endpointInterlock: "sMax-only-rotation",
      invalidPartialTravelRotationRendered: false,
      simulatorUsed: false,
      finalUnityUsed: false,
      buildInstallPhone: false,
    },
    sourceAssetIds,
    sourceClaimIds,
  });
}

const approvedAt = new Date().toISOString();
const reviewedVideo = manifest.assets.find((asset) => asset.id === "magnetic-slide-g05-r012-endpoint-interlock-video");
gate05.status = "approved";
gate05.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "user",
  decidedAt: approvedAt,
  scope: "Gate 05 rev 12 endpoint-interlock white-model motion",
  reviewedArtifactId: reviewedVideo.id,
  reviewedArtifactSha256: reviewedVideo.sha256,
  contractSha256: contractSha,
  interactionMode: "chat-after-direct-QuickTime-review",
};
gate05.readiness = {
  ready: true,
  blockers: [],
  note: `Approved with exact wording “${exactUserWording}”.`,
};
gate05.validations = gate05.validations.filter((validation) => validation.id !== "chat-approval-endpoint-interlock");
gate05.validations.push({
  id: "chat-approval-endpoint-interlock",
  status: "pass",
  evidence: `Exact wording “${exactUserWording}”; video SHA-256 ${reviewedVideo.sha256}; contract ${contractSha}.`,
});

gate06.revision = 5;
gate06.status = "ready_for_review";
gate06.artifactIds = definitions.map(([id]) => id);
gate06.reviewArtifactIds = [
  "magnetic-slide-tile-geometry-interactive-r005",
  "magnetic-slide-tile-geometry-state-machine-r005",
  "magnetic-slide-tile-geometry-workbench-r005",
  "magnetic-slide-tile-geometry-pivot-r005",
  "magnetic-slide-tile-geometry-mid-rotation-blocked-r005",
  "magnetic-slide-tile-geometry-closed-r005",
  "magnetic-slide-tile-geometry-max0-r005",
  "magnetic-slide-tile-geometry-max12-r005",
  "magnetic-slide-tile-geometry-max36-r005",
  "magnetic-slide-tile-geometry-max360-r005",
  "magnetic-slide-tile-geometry-front-r005",
  "magnetic-slide-tile-geometry-back-r005",
  "magnetic-slide-tile-geometry-top-r005",
  "magnetic-slide-tile-geometry-bottom-r005",
  "magnetic-slide-tile-geometry-left-r005",
  "magnetic-slide-tile-geometry-right-r005",
  "magnetic-slide-tile-geometry-dimensions-r005",
  "magnetic-slide-tile-geometry-exploded-r005",
  "magnetic-slide-tile-geometry-underside-r005",
  "magnetic-slide-tile-geometry-flat-axis-r005",
  "magnetic-slide-tile-geometry-section-aa-r005",
];
gate06.inputDigest = gate05SourceSha;
gate06.outputDigest = report.canonicalGeometryDigest;
gate06.decision = null;
gate06.geometrySpec = {
  revision: 5,
  governingContractAssetId: "slider-analysis-mechanism-evidence-contract-r017",
  governingContractSha256: contractSha,
  gate05SourceAssetId: "magnetic-slide-g05-r012-blend",
  gate05SourceSha256: gate05SourceSha,
  gate05ApprovalExactWording: exactUserWording,
  geometryChanged: false,
  canonicalGeometryDigest: report.canonicalGeometryDigest,
  authoritativeBlendSha256: sha256File(local("magnetic-slide-tile-geometry-r005.blend")),
  interactiveGlbSha256: sha256File(local("magnetic-slide-tile-geometry-r005-review.glb")),
  exactBoundsMm: [31, 50, 12],
  dimensionState: "user-authorized-provisional-not-production-measured",
  endpointInterlock: report.stateMachine,
  denseValidation: report.denseValidation,
  rendererWhitelist: report.productRendererWhitelist,
  requiredViews: [
    "front", "back", "top", "bottom", "left", "right", "workbench",
    "dimensions", "pivot", "section-aa", "exploded", "underside-four-groove",
    "flat-plane-raised-axis", "closed", "max-open-0", "max-open-12",
    "max-open-36", "max-open-360", "prohibited-mid-slide-rotation",
  ],
  materialScope: "white-clay-only",
  simulatorUsed: false,
  finalUnityUsed: false,
  shippingAssetChanged: false,
};
gate06.validations = [
  { id: "gate05-endpoint-motion-approved", status: "pass", evidence: `Exact approval “${exactUserWording}”; video SHA-256 ${reviewedVideo.sha256}.` },
  { id: "contract-and-source-hashes", status: "pass", evidence: `Contract ${contractSha}; Gate 05 blend ${gate05SourceSha}.` },
  { id: "geometry-unchanged", status: "pass", evidence: `All views and states use geometry digest ${report.canonicalGeometryDigest}.` },
  { id: "fixed-pivot-equation", status: "pass", evidence: `1,362 legal samples; pivot variance ${report.denseValidation.maxPivotVarianceMm} mm; max residual ${report.denseValidation.maxTopResidualMm} mm.` },
  { id: "endpoint-interlock", status: "pass", evidence: "4,000 below-endpoint rotation requests blocked; 359 nonzero-angle slide requests blocked; 30×12° only at sMax." },
  { id: "no-invalid-partial-rotation-evidence", status: "pass", evidence: "The prohibited mid-slide image resolves to θ=0°; no invalid 50% rotation pose is rendered." },
  { id: "containment-and-intersections", status: "pass", evidence: "Dense actual-mesh disk coverage misses=0; representative internal/exterior BVH intersections=0." },
  { id: "flat-bottom-axis-four-grooves", status: "pass", evidence: "Bottom plane deviation 0 mm; one fixed axis; four finite grooves; authorized groove and ball ranges retained." },
  { id: "mesh-quality", status: "pass", evidence: "Eight core meshes: nonmanifold edges=0, invalid polygon normals=0, UV present, smooth source silhouette retained." },
  { id: "renderer-whitelist", status: "pass", evidence: "Product renderers are exactly BottomExterior and MovingTopBody; MinimumOverlapDisk is non-rendering metadata." },
  { id: "blender-audit", status: "pass", evidence: `Independent Blender ${audit.blenderVersion} audit passed ${Object.keys(audit.checks).length} checks.` },
  { id: "scope", status: "pass", evidence: "No material progression, Simulator, final Unity, build, install or phone work." },
];
gate06.readiness = {
  ready: true,
  blockers: [],
  note: "Interact with the Gate 06 rev 5 GLB, then review the same-source structural views. Visual approval pending; not pushed to phone.",
};
delete gate06.staleReason;
for (let index = 6; index < manifest.stages.length; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 06 rev 5 endpoint-interlock geometry awaits approval.";
}
manifest.currentStageId = "06-geometry";
manifest.currentState.visualApproval = "gate06-rev5-ready-for-review-visual-approval-pending-not-pushed";
manifest.currentState.blenderModelingStatus = "gate06-rev5-unchanged-geometry-endpoint-interlock-ready";
manifest.currentState.simulatorStatus = "internal-superseded-not-current";
manifest.currentState.unityStatus = "old-shipping-model-default-no-final-unity-work";
manifest.currentState.workbench = "persistent-seven-tab-default-gate06-endpoint-geometry";
manifest.currentState.diagnosis = `Gate 05 approved with “${exactUserWording}”. Gate 06 rev 5 validates unchanged geometry under the endpoint interlock.`;
manifest.revision += 1;
manifest.updatedAt = approvedAt;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-endpoint-approved-gate06-rev5-ready",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: approvedAt,
  exactUserWording,
  decisionSource: "latest-explicit-chat",
  approvedGate: "05-blockout",
  approvedRevision: 12,
  reviewedArtifactId: reviewedVideo.id,
  reviewedArtifactSha256: reviewedVideo.sha256,
  contractSha256: contractSha,
  gate05SourceSha256: gate05SourceSha,
  geometryDigest: report.canonicalGeometryDigest,
  gate06Revision: 5,
  gate06Status: "ready_for_review",
  reviewArtifactIds: gate06.reviewArtifactIds,
  metrics: {
    boundsMm: report.dimensions.boundsMm,
    bottomTopPlaneMaximumDeviationMm: report.dimensions.bottomTopPlaneMaximumDeviationMm,
    fixedPivotVarianceMm: report.denseValidation.maxPivotVarianceMm,
    fixedPivotResidualMm: report.denseValidation.maxTopResidualMm,
    legalSamples: report.denseValidation.legalSamples,
    blockedRotationAttempts: report.denseValidation.blockedRotationAttempts,
    blockedSlideAttempts: report.denseValidation.blockedSlideAttempts,
    actualMeshCoverageMisses: report.denseValidation.minimumDiskCoverageMisses,
  },
  completedChecklist: [
    "interactive GLB", "six orthographic views", "Workbench", "dimension and pivot overlays",
    "A-A section", "exploded geometry", "four-groove underside", "flat bottom and fixed axis",
    "legal endpoint poses", "prohibited mid-slide rotation resolved to theta zero",
  ],
  interactionMode: "chat-after-direct-QuickTime-review",
  visualApprovalPending: true,
  materialSimulatorFinalUnityBuildDevice: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate05: saved.stages[4].status,
  gate06: saved.stages[5].status,
  artifactCount: gate06.artifactIds.length,
  reviewArtifactCount: gate06.reviewArtifactIds.length,
  geometryDigest: report.canonicalGeometryDigest,
  contractSha256: contractSha,
}, null, 2));
