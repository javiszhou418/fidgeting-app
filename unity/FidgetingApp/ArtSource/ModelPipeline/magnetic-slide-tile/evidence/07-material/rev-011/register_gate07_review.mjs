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
if (manifest.revision !== 178) throw new Error(`Expected pipeline revision 178, got ${manifest.revision}.`);
const gate06 = manifest.stages.find((stage) => stage.id === "06-geometry");
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
if (gate06.status !== "approved" || gate06.decision?.notes !== "那你继续呗") {
  throw new Error("Gate 06 rev 4 chat approval is not current.");
}
if (gate07.status !== "draft" || gate07.materialSpec?.revision !== 11) {
  throw new Error("Gate 07 rev 11 is not the active draft.");
}
const output = path.dirname(fileURLToPath(import.meta.url));
const material = JSON.parse(fs.readFileSync(path.join(output, "material-validation.json"), "utf8"));
const texture = JSON.parse(fs.readFileSync(path.join(output, "texture-lineage.json"), "utf8"));
const image = JSON.parse(fs.readFileSync(path.join(output, "image-material-audit.json"), "utf8"));
const audit = JSON.parse(fs.readFileSync(path.join(output, "blender-material-audit.json"), "utf8"));
if (![material, texture, image, audit].every((report) => report.pass)) {
  throw new Error("Gate 07 material validation failed.");
}
const sourceHash = gate07.materialSpec.sourceGate06Sha256;
const contractHash = gate07.materialSpec.governingContractSha256;
if (material.gate06SourceSha256 !== sourceHash || material.contractSha256 !== contractHash) {
  throw new Error("Gate 07 consumed a stale geometry or contract hash.");
}

const local = (filename) => path.join(output, filename);
const definitions = [
  ["magnetic-slide-tile-material-prepare-r011", "approval-transition", local("prepare_gate07.mjs"), "process"],
  ["magnetic-slide-tile-material-texture-builder-r011", "texture-builder", local("prepare_gate07_textures.py"), "process"],
  ["magnetic-slide-tile-material-builder-r011", "material-builder", local("build_gate07_material.py"), "process"],
  ["magnetic-slide-tile-material-side-rerender-r011", "render-recipe", local("rerender_side_reflection.py"), "process"],
  ["magnetic-slide-tile-material-board-builder-r011", "board-builder", local("assemble_and_audit_gate07.py"), "process"],
  ["magnetic-slide-tile-material-audit-script-r011", "audit-script", local("audit_gate07_material.py"), "process"],
  ["magnetic-slide-tile-material-register-r011", "registration-script", local("register_gate07_review.mjs"), "process"],
  ["magnetic-slide-tile-material-validation-r011", "material-validator", local("material-validation.json"), "validation"],
  ["magnetic-slide-tile-material-texture-lineage-r011", "texture-lineage", local("texture-lineage.json"), "validation"],
  ["magnetic-slide-tile-material-image-audit-r011", "image-audit", local("image-material-audit.json"), "validation"],
  ["magnetic-slide-tile-material-blender-audit-r011", "blender-audit", local("blender-material-audit.json"), "validation"],
  ["magnetic-slide-tile-material-blend-r011", "blend", local("magnetic-slide-tile-material-r011.blend"), "source-model"],
  ["magnetic-slide-tile-material-lookdev-r011", "interactive-model", local("magnetic-slide-tile-material-r011-lookdev.glb"), "export"],
  ["magnetic-slide-tile-material-turntable-r011", "material-turntable", local("magnetic-slide-tile-material-r011-turntable.mp4"), "blender-render"],
  ["magnetic-slide-tile-material-upper-albedo-r011", "artwork-texture", local("upper-albedo.png"), "process"],
  ["magnetic-slide-tile-material-upper-roughness-r011", "roughness-texture", local("upper-roughness.png"), "process"],
  ["magnetic-slide-tile-material-lower-albedo-r011", "artwork-texture", local("lower-albedo.png"), "process"],
  ["magnetic-slide-tile-material-lower-roughness-r011", "roughness-texture", local("lower-roughness.png"), "process"],
  ["magnetic-slide-tile-material-board-r011", "material-board", local("neutral-pbr-material-board.png"), "analysis"],
  ["magnetic-slide-tile-material-closeups-r011", "material-closeup", local("material-closeups-board.png"), "analysis"],
  ["magnetic-slide-tile-material-source-comparison-r011", "material-comparison", local("source-comparison.png"), "analysis"],
  ["magnetic-slide-tile-material-closed-r011", "material-front", local("assembled-closed.png"), "blender-render"],
  ["magnetic-slide-tile-material-open-r011", "material-open-artwork", local("assembled-open.png"), "blender-render"],
  ["magnetic-slide-tile-material-neutral-front-r011", "material-front", local("neutral-pbr-front.png"), "blender-render"],
  ["magnetic-slide-tile-material-side-reflection-r011", "material-side-reflection", local("side-reflection.png"), "blender-render"],
  ["magnetic-slide-tile-material-crystal-00-r011", "material-angle-view", local("crystal-angle-00.png"), "blender-render"],
  ["magnetic-slide-tile-material-crystal-12-r011", "material-angle-view", local("crystal-angle-12.png"), "blender-render"],
  ["magnetic-slide-tile-material-crystal-36-r011", "material-angle-view", local("crystal-angle-36.png"), "blender-render"],
  ["magnetic-slide-tile-material-crystal-closeup-r011", "material-closeup", local("crystal-microflake-closeup.png"), "blender-render"],
  ["magnetic-slide-tile-material-lower-open-r011", "material-open-artwork", local("lower-artwork-open.png"), "blender-render"],
  ["magnetic-slide-tile-material-underside-r011", "material-underside", local("underside-grooves-material.png"), "blender-render"],
  ["magnetic-slide-tile-material-internal-r011", "material-internal", local("internal-material-isolation.png"), "blender-render"],
  ["magnetic-slide-tile-material-workbench-r011", "workbench-source", path.join(repoRoot, "tools/model-provenance-explorer/app.js"), "process"],
  ["magnetic-slide-tile-material-design-bible-r011", "design-bible", path.join(repoRoot, "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"), "process"],
  ["magnetic-slide-tile-material-implementation-status-r011", "implementation-status", path.join(repoRoot, "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"), "process"]
];
const sourceAssetIds = [
  "slider-analysis-mechanism-evidence-contract-r016",
  "magnetic-slide-tile-geometry-blend-r004",
  "magnetic-slide-tile-geometry-interactive-r004",
  "magnetic-slide-tile-artwork-upper-mask-r007",
  "magnetic-slide-tile-material-rev10-lower-mask-r010",
  "magnetic-slide-tile-artwork-border-mask-r007",
  "magnetic-slide-tile-material-rev10-recipe-r010",
  "magnetic-slide-tile-material-rev10-lower-provenance-r010"
];
const sourceClaimIds = manifest.claims
  .filter((claim) => ["01-intake", "02-analysis"].includes(claim.stageId) && !["superseded", "stale"].includes(claim.state))
  .map((claim) => claim.id);
for (const [id, slot, absolute, role] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing Gate 07 output ${absolute}.`);
  manifest.assets.push({
    id,
    stageId: "07-material",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: absolute.endsWith(".py") || absolute.endsWith(".mjs") ? "fidgeting-model-pipeline" : "Blender/Pillow/FFmpeg",
      version: absolute.endsWith(".py") || absolute.endsWith(".mjs") ? "11" : "Blender 5.2.0 LTS",
      recipe: "Gate 07 rev 11 source-backed materials on approved Gate 06 rev 4 geometry"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractHash,
      gate06SourceSha256: sourceHash,
      approvedGate06Wording: "那你继续呗",
      geometryDigest: material.geometryDigestAfter,
      appearanceAuthority: "original-user-blood-red-product-imagery-only",
      upperMaskSha256: texture.sourceMasks.upper.sha256,
      lowerMaskSha256: texture.sourceMasks.lower.sha256,
      borderMaskSha256: texture.sourceMasks.border.sha256,
      simulatorUsed: false,
      unityUsed: false
    },
    sourceAssetIds,
    sourceClaimIds
  });
}

gate07.status = "ready_for_review";
gate07.artifactIds = definitions.map(([id]) => id);
gate07.reviewArtifactIds = [
  "magnetic-slide-tile-material-lookdev-r011",
  "magnetic-slide-tile-material-turntable-r011",
  "magnetic-slide-tile-material-source-comparison-r011",
  "magnetic-slide-tile-material-board-r011",
  "magnetic-slide-tile-material-closeups-r011",
  "magnetic-slide-tile-material-closed-r011",
  "magnetic-slide-tile-material-open-r011",
  "magnetic-slide-tile-material-side-reflection-r011",
  "magnetic-slide-tile-material-crystal-00-r011",
  "magnetic-slide-tile-material-crystal-12-r011",
  "magnetic-slide-tile-material-crystal-36-r011",
  "magnetic-slide-tile-material-underside-r011",
  "magnetic-slide-tile-material-internal-r011"
];
gate07.inputDigest = sourceHash;
gate07.outputDigest = sha256File(local("magnetic-slide-tile-material-r011.blend"));
gate07.validations = [
  { id: "gate06-approved-source", status: "pass", evidence: `Gate 06 rev 4 approved with exact wording 那你继续呗; blend SHA-256 ${sourceHash}.` },
  { id: "contract-and-geometry-hashes", status: "pass", evidence: `Mechanism contract ${contractHash}; geometry digest ${material.geometryDigestAfter} before, after and across poses.` },
  { id: "material-slot-boundaries", status: "pass", evidence: "Both exterior meshes have independent artwork top, dark side, polished silver rim and neutral underside slots." },
  { id: "editable-independent-masks", status: "pass", evidence: `Upper ${texture.sourceMasks.upper.sha256}; lower ${texture.sourceMasks.lower.sha256}; generated albedos remain distinct.` },
  { id: "source-color-and-contrast", status: "pass", evidence: `Closed/open rendered red σ ${image.sourceColorContrast.closedRedVariation}/${image.sourceColorContrast.openRedVariation}; original user image is sole appearance authority.` },
  { id: "crystal-depth-and-microflakes", status: "pass", evidence: `Granular scale 28; microflake scale 85; texture microflakes ${texture.outputs.upper.microflakePixels}/${texture.outputs.lower.microflakePixels}; 0°/12°/36° evidence.` },
  { id: "black-perimeter", status: "pass", evidence: `64 px border mask black coverage ${image.fullBlackPerimeter.upperBlackFractionWithinBorderMask}/${image.fullBlackPerimeter.lowerBlackFractionWithinBorderMask}.` },
  { id: "silver-dark-side-response", status: "pass", evidence: "Polished silver metallic 1/roughness 0.075; dark side metallic 0.24/roughness 0.18; low-exposure reflection evidence has no clipped pixels." },
  { id: "lower-artwork-provenance", status: "pass", evidence: `Direct ${texture.lowerDirectPixels} px and reconstructed ${texture.lowerReconstructedPixels} px remain labeled and independently editable.` },
  { id: "internal-material-isolation", status: "pass", evidence: "Carrier and followers remain below the smooth 5.875 mm plane in assembled views; technical inspection materials do not contaminate the exterior." },
  { id: "zero-emission-and-clipping", status: "pass", evidence: `All seven audited materials have emission 0; maximum rendered clipped fraction ${image.maximumClippedFraction}.` },
  { id: "packed-textures-and-glb", status: "pass", evidence: `Four packed 620×1000 images, ${audit.glb.materials.length} materials and ${audit.glb.meshCount} meshes are embedded in the interactive GLB.` },
  { id: "interactive-and-recording", status: "pass", evidence: "Interactive GLB supports orbit/zoom, environment and exposure controls; 24-frame real Blender turntable MP4 is the fallback." },
  { id: "scope", status: "pass", evidence: "No Simulator, Unity, build, install or device work occurred; old shipping model remains default." }
];
gate07.materialSpec = {
  ...gate07.materialSpec,
  authoritativeBlendSha256: sha256File(local("magnetic-slide-tile-material-r011.blend")),
  interactiveGlbSha256: sha256File(local("magnetic-slide-tile-material-r011-lookdev.glb")),
  turntableSha256: sha256File(local("magnetic-slide-tile-material-r011-turntable.mp4")),
  textureLineage: texture.sourceMasks,
  generatedTextures: texture.outputs,
  materialValues: material.materials,
  imageMetrics: image,
  blenderAudit: audit.checks,
  geometryDigestAfter: material.geometryDigestAfter
};
gate07.readiness = {
  ready: true,
  blockers: [],
  note: "Review the material-bearing GLB first, then the real Blender turntable and source comparison. Visual approval is pending; nothing was pushed to a phone."
};
delete gate07.staleReason;
for (let index = 7; index < 11; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 07 rev 11 awaits visual approval.";
}
manifest.stages[11].status = "rejected";
manifest.currentStageId = "07-material";
manifest.currentState.visualApproval = "gate07-rev11-ready-for-review-visual-approval-pending-not-pushed";
manifest.currentState.blenderModelingStatus = "gate07-source-backed-materials-ready-for-review";
manifest.currentState.simulatorStatus = "internal-superseded-not-current";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-default-gate07-material";
manifest.currentState.diagnosis = "Gate 06 rev 4 is approved. Gate 07 rev 11 reapplies source-backed blood-red, black, silver and dark-side materials to the unchanged geometry.";
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate07-corrected-geometry-material-ready",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate06ApprovalWording: "那你继续呗",
  gate06SourceSha256: sourceHash,
  contractSha256: contractHash,
  geometryDigest: material.geometryDigestAfter,
  artifactIds: gate07.artifactIds,
  reviewArtifactIds: gate07.reviewArtifactIds,
  appearanceAuthority: "original-user-blood-red-product-imagery-only",
  visualApprovalPending: true,
  simulatorUsed: false,
  unityChanged: false,
  buildInstallOrDevice: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate06: saved.stages[5].status,
  gate07: saved.stages[6].status,
  artifactCount: gate07.artifactIds.length,
  reviewArtifactCount: gate07.reviewArtifactIds.length,
  geometryDigest: material.geometryDigestAfter,
  interactiveGlbSha256: gate07.materialSpec.interactiveGlbSha256
}, null, 2));

