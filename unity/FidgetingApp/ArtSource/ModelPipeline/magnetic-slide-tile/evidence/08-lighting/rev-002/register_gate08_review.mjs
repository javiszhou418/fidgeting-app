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

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 182) throw new Error(`Expected pipeline revision 182, got ${manifest.revision}.`);
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
const gate08 = manifest.stages.find((stage) => stage.id === "08-lighting");
if (gate07.status !== "approved" || gate07.decision?.notes !== "继续") {
  throw new Error("Gate 07 rev 11 exact chat approval is not current.");
}
if (gate08.status !== "draft" || gate08.lightingSpec?.revision !== 2) {
  throw new Error("Gate 08 rev 2 is not the active draft.");
}
const output = path.dirname(fileURLToPath(import.meta.url));
const readJson = (filename) => JSON.parse(fs.readFileSync(path.join(output, filename), "utf8"));
const lighting = readJson("lighting-validation.json");
const image = readJson("image-lighting-audit.json");
const blender = readJson("blender-lighting-audit.json");
if (![lighting, image, blender].every((report) => report.pass)) {
  throw new Error("Gate 08 lighting validation failed.");
}
const sourceHash = gate08.lightingSpec.sourceMaterialSha256;
const contractHash = gate08.lightingSpec.governingContractSha256;
if (
  lighting.sourceGate07.blendSha256 !== sourceHash
  || lighting.contractSha256 !== contractHash
  || lighting.sourceGate07.approvalWording !== "继续"
) {
  throw new Error("Gate 08 consumed a stale material, contract or approval.");
}

const local = (filename) => path.join(output, filename);
const definitions = [
  ["magnetic-slide-tile-lighting-prepare-r002", "approval-transition", local("prepare_gate08.mjs"), "process"],
  ["magnetic-slide-tile-lighting-builder-r002", "lighting-builder", local("build_gate08_lighting.py"), "process"],
  ["magnetic-slide-tile-lighting-image-audit-script-r002", "image-audit-script", local("assemble_and_audit_gate08.py"), "process"],
  ["magnetic-slide-tile-lighting-blender-audit-script-r002", "blender-audit-script", local("audit_gate08_lighting.py"), "process"],
  ["magnetic-slide-tile-lighting-register-r002", "registration-script", local("register_gate08_review.mjs"), "process"],
  ["magnetic-slide-tile-lighting-recipe-r002", "lighting-recipe", local("lighting-recipe.json"), "process"],
  ["magnetic-slide-tile-lighting-validation-r002", "lighting-validation", local("lighting-validation.json"), "validation"],
  ["magnetic-slide-tile-lighting-image-audit-r002", "image-lighting-audit", local("image-lighting-audit.json"), "validation"],
  ["magnetic-slide-tile-lighting-blender-audit-r002", "blender-lighting-audit", local("blender-lighting-audit.json"), "validation"],
  ["magnetic-slide-tile-lighting-blend-r002", "blend", local("magnetic-slide-tile-lighting-r002.blend"), "source-model"],
  ["magnetic-slide-tile-lighting-lookdev-r002", "interactive-lighting-lookdev", local("magnetic-slide-tile-lighting-r002-lookdev.glb"), "export"],
  ["magnetic-slide-tile-lighting-turntable-r002", "lighting-turntable", local("magnetic-slide-tile-lighting-r002-turntable.mp4"), "blender-render"],
  ["magnetic-slide-tile-lighting-hero-r002", "hero", local("hero.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-left-r002", "left-oblique", local("left-oblique.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-right-r002", "right-oblique", local("right-oblique.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-low-r002", "low", local("low-angle.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-neutral-r002", "lighting-mode-neutral", local("lighting-neutral.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-studio-r002", "lighting-mode-studio", local("lighting-studio.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-daylight-r002", "lighting-mode-daylight", local("lighting-daylight.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-pass-beauty-r002", "beauty-pass", local("pass-beauty.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-pass-clay-r002", "clay-pass", local("pass-clay.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-pass-normal-r002", "normal-pass", local("pass-normal.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-pass-depth-r002", "depth-pass", local("pass-depth.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-pass-roughness-r002", "roughness-pass", local("pass-roughness.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-state-closed-r002", "lighting-state", local("state-closed.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-state-open-r002", "lighting-state", local("state-max-open.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-state-12-r002", "lighting-state", local("state-detent-12.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-state-36-r002", "lighting-state", local("state-detent-36.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-flat-axis-r002", "mechanical-lighting", local("flat-plane-raised-axis-lit.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-underside-r002", "mechanical-lighting", local("underside-grooves-lit.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-carrier-r002", "mechanical-lighting", local("carrier-clearance-lit.png"), "blender-render"],
  ["magnetic-slide-tile-lighting-view-board-r002", "lighting-view-board", local("lighting-view-board.png"), "analysis"],
  ["magnetic-slide-tile-lighting-mode-comparison-r002", "lighting-mode-comparison", local("lighting-mode-comparison.png"), "analysis"],
  ["magnetic-slide-tile-lighting-pass-board-r002", "lighting-pass-board", local("lighting-pass-board.png"), "analysis"],
  ["magnetic-slide-tile-lighting-mechanical-board-r002", "mechanical-lighting-board", local("mechanical-lighting-board.png"), "analysis"],
  ["magnetic-slide-tile-lighting-workbench-r002", "workbench-source", path.join(repoRoot, "tools/model-provenance-explorer/app.js"), "process"],
  ["magnetic-slide-tile-lighting-node-test-r002", "node-test", path.join(repoRoot, "tools/model-provenance-explorer/tests/magnetic-slide-gate08-rev2.test.mjs"), "process"],
];
const sourceAssetIds = [
  "slider-analysis-mechanism-evidence-contract-r016",
  "magnetic-slide-tile-geometry-blend-r004",
  "magnetic-slide-tile-material-blend-r011",
  "magnetic-slide-tile-material-lookdev-r011",
  "magnetic-slide-tile-material-turntable-r011",
  "magnetic-slide-tile-material-texture-lineage-r011",
];
for (const [id, slot, absolute, role] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing Gate 08 output ${absolute}.`);
  manifest.assets.push({
    id,
    stageId: "08-lighting",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: absolute.endsWith(".py") || absolute.endsWith(".mjs")
        ? "fidgeting-model-pipeline"
        : "Blender/Pillow/FFmpeg",
      version: absolute.endsWith(".py") || absolute.endsWith(".mjs") ? "2" : "Blender 5.2.0 LTS",
      recipe: "Gate 08 rev 2 controlled lighting on approved Gate 07 rev 11 materials"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractHash,
      gate07SourceSha256: sourceHash,
      approvedGate07Wording: "继续",
      geometryDigest: lighting.geometry.after,
      materialDigest: lighting.materials.after,
      lightingModes: ["neutral", "studio", "daylight"],
      hdri: null,
      simulatorUsed: false,
      unityUsed: false,
      deviceWork: false,
    },
    sourceAssetIds,
    sourceClaimIds: [],
  });
}

gate08.status = "ready_for_review";
gate08.artifactIds = definitions.map(([id]) => id);
gate08.reviewArtifactIds = [
  "magnetic-slide-tile-lighting-lookdev-r002",
  "magnetic-slide-tile-lighting-turntable-r002",
  "magnetic-slide-tile-lighting-mode-comparison-r002",
  "magnetic-slide-tile-lighting-view-board-r002",
  "magnetic-slide-tile-lighting-mechanical-board-r002",
  "magnetic-slide-tile-lighting-pass-board-r002",
  "magnetic-slide-tile-lighting-hero-r002",
  "magnetic-slide-tile-lighting-left-r002",
  "magnetic-slide-tile-lighting-right-r002",
  "magnetic-slide-tile-lighting-low-r002",
  "magnetic-slide-tile-lighting-state-open-r002",
  "magnetic-slide-tile-lighting-state-12-r002",
  "magnetic-slide-tile-lighting-state-36-r002",
  "magnetic-slide-tile-lighting-flat-axis-r002",
  "magnetic-slide-tile-lighting-underside-r002",
  "magnetic-slide-tile-lighting-carrier-r002",
];
gate08.inputDigest = sourceHash;
gate08.outputDigest = sha256File(local("magnetic-slide-tile-lighting-r002.blend"));
gate08.validations = [
  { id: "gate07-r011-exact-approval", status: "pass", evidence: `Gate 07 rev 11 approved with exact wording 继续; source blend SHA-256 ${sourceHash}.` },
  { id: "contract-geometry-material-hashes", status: "pass", evidence: `Contract ${contractHash}; geometry ${lighting.geometry.after}; material ${lighting.materials.after} unchanged.` },
  { id: "controlled-three-mode-rig", status: "pass", evidence: "Neutral, Studio and Daylight use four documented area fixtures, uniform worlds and no HDRI." },
  { id: "required-views", status: "pass", evidence: "Real Blender Hero, left/right oblique and low-angle renders are present." },
  { id: "required-passes", status: "pass", evidence: "Beauty, Clay, World Normal, View Depth and Roughness use one Hero camera and closed pose." },
  { id: "silver-neutral-no-blue-gray", status: "pass", evidence: `Neutral chroma remains ≤12; maximum blue-gray fraction ${Math.max(...Object.values(image.views).map((item) => item.blueGrayFractionWithinNeutral))}.` },
  { id: "blood-red-no-pink", status: "pass", evidence: "Median blood-red hue remains within ±20° in every authored view; magenta drift check passes." },
  { id: "crystal-variation-motif-contrast", status: "pass", evidence: "Granular red variation and local edge contrast pass across four views and three lighting modes." },
  { id: "clipping-controlled", status: "pass", evidence: `Maximum Beauty clipping fraction ${image.maximumBeautyClippedFraction}.` },
  { id: "hidden-mechanical-readability", status: "pass", evidence: "Separate flat-plane/raised-axis, four-groove underside and carrier/follower clearance renders pass edge/dynamic-range audits." },
  { id: "zero-emission", status: "pass", evidence: "All seven approved Gate 07 materials retain emission strength 0; unlit Normal/Depth visualization materials are technical pass-only." },
  { id: "interactive-and-turntable", status: "pass", evidence: "Interactive GLB supports orbit/zoom, Neutral/Studio/Daylight, environment and exposure; 24-frame real Blender turntable MP4 is present." },
  { id: "scope", status: "pass", evidence: "No Simulator, Unity, build, install or device work occurred; old shipping model remains default." },
];
gate08.lightingSpec = {
  ...gate08.lightingSpec,
  authoritativeBlendSha256: gate08.outputDigest,
  interactiveGlbSha256: sha256File(local("magnetic-slide-tile-lighting-r002-lookdev.glb")),
  turntableSha256: sha256File(local("magnetic-slide-tile-lighting-r002-turntable.mp4")),
  geometryDigestAfter: lighting.geometry.after,
  materialDigestBefore: lighting.materials.before,
  materialDigestAfter: lighting.materials.after,
  recipe: lighting.lightingRecipe,
  imageMetrics: image,
  blenderAudit: blender.checks,
  maximumBeautyClippedFraction: image.maximumBeautyClippedFraction,
};
gate08.readiness = {
  ready: true,
  blockers: [],
  note: "Review the interactive three-mode GLB first, then the Blender lighting comparison, turntable, mechanical board and same-camera pass board. Visual approval is pending; nothing was pushed to a phone."
};
delete gate08.staleReason;
for (let index = 8; index < 11; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 08 rev 2 awaits visual approval.";
}
manifest.stages[11].status = "rejected";
manifest.currentStageId = "08-lighting";
manifest.currentState.visualApproval = "gate08-rev2-ready-for-review-visual-approval-pending-not-pushed";
manifest.currentState.blenderModelingStatus = "gate08-lighting-ready-for-review";
manifest.currentState.simulatorStatus = "internal-superseded-not-current";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-default-gate08-lighting";
manifest.currentState.diagnosis = "Gate 07 rev 11 is approved. Gate 08 rev 2 lights the unchanged geometry and materials with three controlled modes.";
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate08-controlled-lighting-ready",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate07ApprovalWording: "继续",
  gate07SourceSha256: sourceHash,
  contractSha256: contractHash,
  geometryDigest: lighting.geometry.after,
  materialDigest: lighting.materials.after,
  artifactIds: gate08.artifactIds,
  reviewArtifactIds: gate08.reviewArtifactIds,
  lightingModes: ["neutral", "studio", "daylight"],
  visualApprovalPending: true,
  simulatorUsed: false,
  unityChanged: false,
  buildInstallOrDevice: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate07: saved.stages[6].status,
  gate08: saved.stages[7].status,
  artifactCount: gate08.artifactIds.length,
  reviewArtifactCount: gate08.reviewArtifactIds.length,
  geometryDigest: lighting.geometry.after,
  materialDigest: lighting.materials.after,
}, null, 2));

