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
const gate06 = manifest.stages.find((stage) => stage.id === "06-geometry");
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
if (
  manifest.currentStageId !== "07-material"
  || gate06.status !== "approved"
  || gate06.revision !== 5
  || gate07.status !== "draft"
  || gate07.revision !== 13
) {
  throw new Error("Gate 07 rev 13 draft is not the current earliest gate.");
}
const output = path.dirname(fileURLToPath(import.meta.url));
const readJson = (filename) => JSON.parse(
  fs.readFileSync(path.join(output, filename), "utf8"),
);
const rootCause = readJson("root-cause-report.json");
const build = readJson("material-build-report.json");
const transport = readJson("material-transport-audit.json");
const motion = readJson("endpoint-material-motion-audit.json");
const turntable = readJson("legal-motion-turntable-report.json");
const boards = readJson("review-board-report.json");
if (![rootCause, build, transport, motion, turntable, boards].every(({ pass }) => pass)) {
  throw new Error("Gate 07 rev 13 evidence is not fully validated.");
}
if (
  build.geometryDigestAfter !== gate07.materialSpec.evaluatedGeometryDigest
  || build.contractSha256 !== gate07.materialSpec.governingContractSha256
  || build.gate06SourceSha256 !== gate07.materialSpec.sourceGate06Sha256
) {
  throw new Error("Gate 07 rev 13 consumed stale geometry or mechanism evidence.");
}
const local = (filename) => path.join(output, filename);
const definitions = [
  ["magnetic-slide-tile-material-rev13-start", "approval-transition", local("start_gate07_side_partition_fix.mjs"), "process"],
  ["magnetic-slide-tile-material-root-cause-script-r013", "root-cause-script", local("audit_gate07_root_cause.py"), "process"],
  ["magnetic-slide-tile-material-root-cause-r013", "root-cause", local("root-cause-report.json"), "validation"],
  ["magnetic-slide-tile-material-builder-r013", "material-builder", local("build_gate07_side_partition_fix.py"), "process"],
  ["magnetic-slide-tile-material-top-rerender-r013", "render-recipe", local("rerender_top_closeup.py"), "process"],
  ["magnetic-slide-tile-material-transport-script-r013", "transport-audit-script", local("audit_gate07_material_transport.py"), "process"],
  ["magnetic-slide-tile-material-transport-r013", "transport-audit", local("material-transport-audit.json"), "validation"],
  ["magnetic-slide-tile-material-motion-script-r013", "motion-audit-script", local("audit_endpoint_material_motion.py"), "process"],
  ["magnetic-slide-tile-material-motion-r013", "motion-audit", local("endpoint-material-motion-audit.json"), "validation"],
  ["magnetic-slide-tile-material-board-script-r013", "board-builder", local("assemble_gate07_review.py"), "process"],
  ["magnetic-slide-tile-material-build-report-r013", "material-validation", local("material-build-report.json"), "validation"],
  ["magnetic-slide-tile-material-turntable-report-r013", "video-validation", local("legal-motion-turntable-report.json"), "validation"],
  ["magnetic-slide-tile-material-board-report-r013", "image-validation", local("review-board-report.json"), "validation"],
  ["magnetic-slide-tile-material-blend-r013", "blend", local("magnetic-slide-tile-material-r013.blend"), "source-model"],
  ["magnetic-slide-tile-material-lookdev-r013", "interactive-model", local("magnetic-slide-tile-material-r013-lookdev.glb"), "export"],
  ["magnetic-slide-tile-material-fbx-r013", "fbx-transport", local("magnetic-slide-tile-material-r013.fbx"), "export"],
  ["magnetic-slide-tile-material-turntable-r013", "material-turntable", local("gate07-r013-legal-motion-turntable.mp4"), "blender-render"],
  ["magnetic-slide-tile-material-review-board-r013", "material-board", local("gate07-r013-material-review-board.png"), "analysis"],
  ["magnetic-slide-tile-material-closeups-r013", "material-closeup", local("gate07-r013-top-side-rim-closeups.png"), "analysis"],
  ["magnetic-slide-tile-material-comparison-r013", "material-comparison", local("gate07-r013-rejection-correction.png"), "analysis"],
  ["magnetic-slide-tile-material-hero-r013", "material-hero", local("assembled-hero.png"), "blender-render"],
  ["magnetic-slide-tile-material-upper-top-r013", "material-top-artwork", local("upper-top-closeup.png"), "blender-render"],
  ["magnetic-slide-tile-material-lower-top-r013", "material-lower-artwork", local("lower-top-open-closeup.png"), "blender-render"],
  ["magnetic-slide-tile-material-side-r013", "material-side-wall", local("side-wall-closeup.png"), "blender-render"],
  ["magnetic-slide-tile-material-rim-r013", "material-rim", local("silver-rim-closeup.png"), "blender-render"],
  ["magnetic-slide-tile-material-underside-r013", "material-underside", local("underside-closeup.png"), "blender-render"],
  ["magnetic-slide-tile-material-upper-albedo-r013", "artwork-texture", local("upper-albedo.png"), "process"],
  ["magnetic-slide-tile-material-upper-roughness-r013", "roughness-texture", local("upper-roughness.png"), "process"],
  ["magnetic-slide-tile-material-lower-albedo-r013", "artwork-texture", local("lower-albedo.png"), "process"],
  ["magnetic-slide-tile-material-lower-roughness-r013", "roughness-texture", local("lower-roughness.png"), "process"],
  ["magnetic-slide-tile-material-upper-mask-r013", "artwork-mask", local("upper-artwork-mask.png"), "process"],
  ["magnetic-slide-tile-material-lower-mask-r013", "artwork-mask", local("lower-artwork-mask.png"), "process"],
  ["magnetic-slide-tile-material-perimeter-mask-r013", "artwork-mask", local("top-perimeter-mask.png"), "process"],
  ["magnetic-slide-tile-material-register-r013", "registration-script", local("register_gate07_side_partition_review.mjs"), "process"],
];
for (let index = 0; index < 90; index += 1) {
  const number = String(index).padStart(4, "0");
  definitions.push([
    `magnetic-slide-tile-material-legal-frame-${number}-r013`,
    "legal-motion-frame",
    local(`legal-motion-frames/frame-${number}.png`),
    "blender-render",
  ]);
}
const sourceAssetIds = [
  "slider-analysis-mechanism-evidence-contract-r017",
  "magnetic-slide-tile-geometry-blend-r005",
  "magnetic-slide-tile-geometry-interactive-r005",
  "magnetic-slide-tile-material-blend-r012",
  "magnetic-slide-tile-artwork-upper-mask-r007",
  "magnetic-slide-tile-material-rev10-lower-mask-r010",
  "magnetic-slide-tile-artwork-border-mask-r007",
  "magnetic-slide-tile-material-side-wrap-rejection-r013",
];
const sourceClaimIds = manifest.claims
  .filter((claim) => (
    ["01-intake", "02-analysis"].includes(claim.stageId)
    && !["superseded", "stale"].includes(claim.state)
  ))
  .map((claim) => claim.id);
for (const [id, slot, absolute, role] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing Gate 07 rev 13 output: ${absolute}`);
  if (manifest.assets.some((asset) => asset.id === id)) {
    throw new Error(`Duplicate Gate 07 rev 13 asset id: ${id}`);
  }
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
      name: absolute.endsWith(".py") || absolute.endsWith(".mjs")
        ? "fidgeting-model-pipeline"
        : "Blender/Pillow/FFmpeg",
      version: absolute.endsWith(".py") || absolute.endsWith(".mjs")
        ? "rev-013"
        : "Blender 5.2.0 LTS",
      recipe: "Gate 07 rev 13 cap-only artwork with deterministic side and rim partitions",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: build.contractSha256,
      gate06SourceSha256: build.gate06SourceSha256,
      geometryDigest: build.geometryDigestAfter,
      userRejectionSha256: "a7859940ee1d956755c07a810bc5aeccee75136da092cb8f1891bf9fe6dc8b1b",
      exactUserWording: "边缘没有图案填充",
      sideWallArtworkPixels: 0,
      textureAddressMode: "CLAMP_TO_EDGE",
      geometryChanged: false,
      mechanismChanged: false,
      simulatorUsed: false,
      unityUsed: false,
      phoneUsed: false,
    },
    sourceAssetIds,
    sourceClaimIds,
  });
}

gate07.status = "ready_for_review";
gate07.artifactIds = [
  "magnetic-slide-tile-material-side-wrap-rejection-r013",
  ...definitions.map(([id]) => id),
];
gate07.reviewArtifactIds = [
  "magnetic-slide-tile-material-lookdev-r013",
  "magnetic-slide-tile-material-turntable-r013",
  "magnetic-slide-tile-material-review-board-r013",
  "magnetic-slide-tile-material-closeups-r013",
  "magnetic-slide-tile-material-comparison-r013",
  "magnetic-slide-tile-material-hero-r013",
  "magnetic-slide-tile-material-upper-top-r013",
  "magnetic-slide-tile-material-lower-top-r013",
  "magnetic-slide-tile-material-side-r013",
  "magnetic-slide-tile-material-rim-r013",
  "magnetic-slide-tile-material-underside-r013",
];
gate07.inputDigest = build.gate06SourceSha256;
gate07.outputDigest = sha256File(local("magnetic-slide-tile-material-r013.blend"));
gate07.validations = [
  {
    id: "root-cause-proven",
    status: "pass",
    evidence: "Gate 08 rev 5 render_roughness cleared material slots at lines 304/310; all 8,723 + 10,783 polygons became artwork slot 0.",
  },
  {
    id: "geometry-and-mechanism-unchanged",
    status: "pass",
    evidence: `Gate 06 SHA-256 ${build.gate06SourceSha256}; geometry digest ${build.geometryDigestAfter}; contract ${build.contractSha256}.`,
  },
  {
    id: "deterministic-cap-side-rim-partitions",
    status: "pass",
    evidence: "Both pieces use slot IDs 0 cap, 1 solid side, 2 polished rim, 3 neutral underside with hash-locked face counts.",
  },
  {
    id: "zero-side-artwork-all-formats",
    status: "pass",
    evidence: "Blend, re-imported GLB and re-imported FBX report zero side-wall artwork faces and zero non-cap textured faces for both pieces.",
  },
  {
    id: "top-artwork-source-correct",
    status: "pass",
    evidence: `Upper mask ${build.textureLineage["upper-artwork-mask.png"].sha256}; lower mask ${build.textureLineage["lower-artwork-mask.png"].sha256}; each export has 511 artwork cap triangles.`,
  },
  {
    id: "texture-clamp-no-wrap",
    status: "pass",
    evidence: "Blender artwork nodes use EXTEND/CLAMP_TO_EDGE; GLB sampler wrapS/wrapT are 33071; non-cap UV loops use the -1/-1 sentinel and never bind textured materials.",
  },
  {
    id: "export-transport",
    status: "pass",
    evidence: `GLB and FBX material triangle counts match exactly; GLB has ${transport.glbContract.meshCount} meshes, ${transport.glbContract.materialCount} materials and four primitives per piece.`,
  },
  {
    id: "endpoint-interlock-motion",
    status: "pass",
    evidence: `Dense ${motion.denseSamples} samples; ${motion.blockedRotationAttempts} blocked rotations; ${motion.blockedSlideAttempts} blocked returns; fixed-axis variance ${motion.maxPivotVarianceMm} mm; penetration ${motion.maximumSurfaceIntersectionCount}.`,
  },
  {
    id: "flat-lower-top-raised-axis-four-grooves",
    status: "pass",
    evidence: `Lower top deviation ${motion.bottomTopPlaneMaximumDeviationMm} mm; boss +${motion.axisBossProtrusionMm} mm; ${motion.topUndersideGrooveCount} underside grooves.`,
  },
  {
    id: "interactive-and-recording",
    status: "pass",
    evidence: `Real GLB is the primary review asset; Blender legal-motion turntable is ${turntable.encodedFrameCount} frames, ${turntable.durationSeconds} s, with no flip or invalid pose.`,
  },
  {
    id: "scope",
    status: "pass",
    evidence: "Gate 08–12 remain stale. No Simulator, Unity, build, install, launch, or phone work occurred.",
  },
];
gate07.materialSpec = {
  ...gate07.materialSpec,
  revision: 13,
  rootCause: rootCause.rootCause,
  authoritativeBlendSha256: sha256File(local("magnetic-slide-tile-material-r013.blend")),
  interactiveGlbSha256: sha256File(local("magnetic-slide-tile-material-r013-lookdev.glb")),
  fbxSha256: sha256File(local("magnetic-slide-tile-material-r013.fbx")),
  turntableSha256: sha256File(local("gate07-r013-legal-motion-turntable.mp4")),
  sideWallArtworkPixels: 0,
  undersideArtworkPixels: 0,
  textureAddressMode: "CLAMP_TO_EDGE",
  wrap: false,
  upperLowerArtworkIndependentlyReplaceable: true,
  partitions: build.partitions,
  transport: {
    glb: transport.glbReimport,
    fbx: transport.fbxReimport,
    glbMaterialIds: transport.glbContract.materials,
    glbPrimitives: transport.glbContract.primitives,
    glbSamplerClampNoWrap: transport.glbContract.allSamplersClampNoWrap,
  },
  textureLineage: build.textureLineage,
  geometryChanged: false,
  mechanismChanged: false,
  endpointInterlockOnly: true,
  unityUsed: false,
  simulatorUsed: false,
};
gate07.readiness = {
  ready: true,
  blockers: [],
  note: "Interact with the corrected GLB, then review the legal-motion turntable and top/side/rim closeups. Visual approval is pending; nothing was pushed to a phone.",
};
delete gate07.staleReason;
for (let index = 7; index < 12; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "Gate 07 rev 13 corrected material boundaries await visual approval.";
}
manifest.currentStageId = "07-material";
manifest.currentState.visualApproval = "gate07-rev13-ready-for-review-visual-approval-pending-not-pushed";
manifest.currentState.blenderModelingStatus = "gate07-rev13-cap-side-rim-partition-ready-for-review";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default";
manifest.currentState.simulatorStatus = "not-used";
manifest.currentState.workbench = "persistent-seven-tab-current-gate07-material";
manifest.currentState.diagnosis = rootCause.rootCause.exact;
const issue = manifest.issues.find(({ id }) => id === "slider-gate07-r013-side-partition-review");
if (issue) {
  issue.severity = "blocker";
  issue.status = "awaiting-user-visual-review";
  issue.note = "Correction is validated. Gate 07 rev 13 still requires explicit visual approval before downstream work.";
}
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate07-rev13-side-partition-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "07-material",
  stageRevision: 13,
  rejectionAssetSha256: "a7859940ee1d956755c07a810bc5aeccee75136da092cb8f1891bf9fe6dc8b1b",
  exactUserWording: "边缘没有图案填充",
  rootCause: rootCause.rootCause.exact,
  geometryDigest: build.geometryDigestAfter,
  blendSha256: gate07.materialSpec.authoritativeBlendSha256,
  glbSha256: gate07.materialSpec.interactiveGlbSha256,
  fbxSha256: gate07.materialSpec.fbxSha256,
  sideWallArtworkPixels: 0,
  downstream: "08-12 stale",
  visualApprovalPending: true,
  simulatorUsed: false,
  unityUsed: false,
  buildInstallOrPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate07: saved.stages[6].status,
  artifactCount: saved.stages[6].artifactIds.length,
  reviewArtifactCount: saved.stages[6].reviewArtifactIds.length,
  geometryDigest: build.geometryDigestAfter,
  sideWallArtworkPixels: 0,
}, null, 2));
