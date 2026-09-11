#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  digestValues,
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate10 = manifest.stages.find((stage) => stage.id === "10-export");
if (
  manifest.revision !== 247
  || gate10?.status !== "draft"
  || gate10.exportSpec?.revision !== 11
  || gate10.historicalRevisions?.at(-1)?.evidenceRevision !== 10
  || gate10.historicalRevisions.at(-1).status !== "rejected"
) {
  throw new Error("Expected rejected rev 10 and draft Gate 10 rev 11 at pipeline revision 247.");
}
const here = path.dirname(fileURLToPath(import.meta.url));
const local = (relative) => path.join(here, relative);
const readJson = (relative) => JSON.parse(fs.readFileSync(local(relative), "utf8"));
const build = readJson("portable-glb-build-validation.json");
const rawAudit = readJson("corrected-glb-audit.json");
const blender = readJson("controlled-blender-comparison-validation.json");
const visual = readJson("visual-metrics-validation.json");
const manifestAudit = readJson("export-manifest-validation.json");
if (![build, rawAudit, blender, visual, manifestAudit].every((report) => report.pass)) {
  throw new Error("Gate 10 rev 11 evidence must pass before registration.");
}
const definitions = [
  ["starter", "rejection-transition", "start_gate10_washout_correction.mjs", "process"],
  ["transport-builder", "portable-glb-builder", "build_portable_glb_correction.py", "process"],
  ["glb-auditor", "raw-glb-auditor", "audit_corrected_glb.py", "process"],
  ["blender-comparator", "controlled-blender-comparator", "render_controlled_blender_comparison.py", "process"],
  ["visual-builder", "visual-evidence-builder", "build_visual_evidence.py", "process"],
  ["manifest-builder", "export-manifest-builder", "build_export_manifest.py", "process"],
  ["registrar", "registration-source", "register_gate10_washout_correction.mjs", "process"],
  ["rejection", "user-rejection-evidence", "user-rejection-washed-out-r010.jpg", "user-input"],
  ["transport-report", "portable-glb-validation", "portable-glb-build-validation.json", "validation"],
  ["glb-audit", "corrected-glb-audit", "corrected-glb-audit.json", "validation"],
  ["raw-materials", "raw-glb-material-json", "raw-glb-materials-r011.json", "analysis"],
  ["blender-report", "controlled-reimport-validation", "controlled-blender-comparison-validation.json", "validation"],
  ["visual-report", "objective-visual-validation", "visual-metrics-validation.json", "validation"],
  ["manifest-report", "export-manifest-validation", "export-manifest-validation.json", "validation"],
  ["comparison", "same-camera-comparison", "gate10-r011-controlled-comparison.png", "analysis"],
  ["closeups", "top-side-rim-closeups", "gate10-r011-material-closeups.png", "analysis"],
  ["blend", "source-blend", "package/magnetic-slide-tile-authoritative-r011.blend", "source-model"],
  ["reimport-blend", "glb-reimport-blend", "package/magnetic-slide-tile-glb-reimport-r011.blend", "source-model"],
  ["fbx", "render-fbx", "package/magnetic-slide-tile-render-r011.fbx", "source-model"],
  ["glb", "interactive-model", "package/magnetic-slide-tile-render-r011.glb", "source-model"],
  ["collision", "collision-fbx", "package/magnetic-slide-tile-collision-r011.fbx", "source-model"],
  ["manifest", "export-manifest", "package/export-manifest-r011.json", "contract"],
  ["hierarchy-motion", "hierarchy-motion-metadata", "package/hierarchy-motion-metadata-r011.json", "contract"],
  ["unity-import", "unity-import-astc-plan", "package/unity-import-contract-r011.json", "contract"],
  ["neutral-hdri", "neutral-control-hdr", "package/environment/neutral-control-r009.exr", "source-model"],
  ["target-hdri", "target-shipping-hdr", "package/environment/target-shipping-studio-r009.exr", "source-model"],
  ["upper-basecolor", "upper-base-color", "package/textures/upper-albedo.png", "source-model"],
  ["lower-basecolor", "lower-base-color", "package/textures/lower-albedo.png", "source-model"],
  ["upper-roughness", "upper-roughness", "package/textures/upper-roughness.png", "source-model"],
  ["lower-roughness", "lower-roughness", "package/textures/lower-roughness.png", "source-model"],
  ["upper-transport-normal", "upper-transport-normal", "package/textures/upper-transport-normal-r011.png", "source-model"],
  ["lower-transport-normal", "lower-transport-normal", "package/textures/lower-transport-normal-r011.png", "source-model"],
];
for (const view of ["hero", "top-closeup", "side-closeup", "rim-closeup"]) {
  definitions.push([`approved-${view}`, `approved-blender-${view}`, `controlled-neutral/approved-blender-${view}-r011.png`, "blender-render"]);
  definitions.push([`reimport-${view}`, `glb-reimport-${view}`, `controlled-neutral/glb-reimport-${view}-r011.png`, "blender-render"]);
}
for (const face of ["positive-x", "negative-x", "positive-y", "negative-y", "positive-z", "negative-z"]) {
  definitions.push([`cubemap-${face}`, `cubemap-${face}`, `package/environment/cubemap/${face}.exr`, "source-model"]);
}

const sourceAssetIds = [
  "slider-analysis-mechanism-evidence-contract-r017",
  "magnetic-slide-tile-geometry-blend-r005",
  "magnetic-slide-tile-material-blend-r013",
  "magnetic-slide-tile-lighting-blend-r006",
  "magnetic-slide-tile-environment-blend-r009",
  "magnetic-slide-tile-export-glb-r010",
];
const records = definitions.map(([suffix, slot, relative, role]) => {
  const absolute = local(relative);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${absolute}`);
  return {
    id: `magnetic-slide-tile-export-${suffix}-r011`,
    stageId: "10-export",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Gate 10 rev 11 GLB washout correction",
      version: "Blender 5.2.0 LTS / glTF 2.0 / Three.js 0.185.1",
      recipe: local("build_portable_glb_correction.py"),
    },
    provenance: {
      origin: slot === "user-rejection-evidence" ? "user-provided" : "repository-generated",
      contentClass: slot,
      assertedBy: slot === "user-rejection-evidence" ? "user" : "assistant",
      gate10Revision: 11,
      sourceRejectedRevision: 10,
      rejectionExactWording: "almost entirely white/washed out",
      sourceRejectedGlbSha256: build.sourceRejectedGlb.sha256,
      geometryDigest: build.preserved.geometryDigest,
      materialStateDigest: build.preserved.materialStateDigest,
      uvDigest: build.preserved.uvDigest,
      mechanismEvidenceContractSha256: gate10.exportSpec.governingContractSha256,
      correctionScope: "portable GLB PBR transport and neutral viewer calibration only",
      simulatorUsed: false,
      unityUsed: false,
      shippingChanged: false,
      deviceWork: false,
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
const assetId = (suffix) => `magnetic-slide-tile-export-${suffix}-r011`;
gate10.artifactIds = records.map((record) => record.id);
gate10.reviewArtifactIds = [
  assetId("glb"),
  assetId("comparison"),
  assetId("closeups"),
  assetId("reimport-hero"),
  assetId("manifest"),
];
gate10.inputDigest = digestValues([
  build.sourceRejectedGlb.sha256,
  build.preserved.geometryDigest,
  build.preserved.materialStateDigest,
  build.preserved.uvDigest,
  gate10.exportSpec.environmentSha256,
]);
gate10.outputDigest = digestValues([
  build.outputs.blend.sha256,
  build.outputs.fbx.sha256,
  build.outputs.glb.sha256,
  build.outputs.collision.sha256,
  manifestAudit.manifest.sha256,
]);
gate10.exportSpec = {
  ...gate10.exportSpec,
  authoritativeBlendSha256: build.outputs.blend.sha256,
  fbxSha256: build.outputs.fbx.sha256,
  glbSha256: build.outputs.glb.sha256,
  collisionSha256: build.outputs.collision.sha256,
  hierarchyMotionSha256: build.outputs.hierarchyMotion.sha256,
  exportManifestSha256: manifestAudit.manifest.sha256,
  unityImportContractSha256: build.outputs.unityImportContract.sha256,
  interactiveReviewArtifactId: assetId("glb"),
  transportApproximation: "Explicit opaque glTF PBR; baked sRGB baseColor; linear roughness/normal; no transmission or emission.",
  topPbr: { metallic: 0.08, roughnessFactor: 1, specular: 0.55, clearcoat: 0.32, clearcoatRoughness: 0.10, normalScale: 0.35 },
  sidePbr: { baseColor: [0.014, 0.016, 0.020, 1], metallic: 0.20, roughness: 0.30 },
  rimPbr: { baseColor: [0.68, 0.66, 0.62, 1], metallic: 1, roughness: 0.16 },
  alphaMode: "OPAQUE",
  emissiveFactor: [0, 0, 0],
  viewerCalibration: {
    environmentAssetId: assetId("neutral-hdri"),
    toneMapping: "ACESFilmicToneMapping",
    exposure: 0.9,
    environmentIntensity: 0.42,
    persistedExposureIsolation: true,
  },
  objectiveMetrics: {
    rejectedWhiteFraction: visual.rejected.clippedWhiteFraction,
    correctedWhiteFraction: visual.reimport.clippedWhiteFraction,
    correctedTopRedFraction: visual.topCloseup.redFraction,
    correctedSideMedianLuminance: visual.sideCloseup.luminanceP05P50P95[1],
    correctedRimControlledHighlightFraction: visual.rimCloseup.controlledSilverFraction,
    blenderGlbMeanAbsoluteError: visual.sameCameraSimilarity.meanAbsoluteError,
  },
};
gate10.validations = [
  { id: "rev10-rejection-archived", status: "pass", evidence: `Exact wording “almost entirely white/washed out”; screenshot ${sha256File(local("user-rejection-washed-out-r010.jpg"))}.` },
  { id: "root-cause-isolated", status: "pass", evidence: "Deep-red source pixels and zero emission were correct. Rev 10 combined specularColorFactor 1.16, transmission 0.08, a 75 W + 42 W near-field reimport board, and viewer exposure inheritance up to 2.0." },
  { id: "explicit-portable-pbr", status: "pass", evidence: "Top uses baked sRGB baseColor, linear metallicRoughness G, linear tangent normal, specular 0.55, clearcoat 0.32/0.10, OPAQUE alpha, zero transmission, and zero emission." },
  { id: "geometry-hierarchy-uv-preserved", status: "pass", evidence: `All mesh accessor bytes, primitive material assignments, node transforms, geometry ${build.preserved.geometryDigest}, and UV ${build.preserved.uvDigest} match rev 10.` },
  { id: "material-partitions-preserved", status: "pass", evidence: "Independent upper/lower cap textures remain; top artwork is present; side and underside artwork coverage are exactly 0; dark side and thin silver rim stay separate." },
  { id: "controlled-reimport", status: "pass", evidence: `Same-camera Blender/GLB MAE ${visual.sameCameraSimilarity.meanAbsoluteError.toFixed(4)}; corrected white fraction ${(visual.reimport.clippedWhiteFraction * 100).toFixed(2)}% versus rejected ${(visual.rejected.clippedWhiteFraction * 100).toFixed(2)}%.` },
  { id: "endpoint-interlock-preserved", status: "pass", evidence: "Rotation locks below sMax; 360° uses 30×12° only at sMax; nonzero angle locks slide; return aligns then closes; closed default has zero velocity and no animations." },
  { id: "environment-color-space", status: "pass", evidence: "BaseColor is sRGB; metallic/roughness and normal are linear; CLAMP and 620×1000 NPOT dimensions remain; approved neutral and target EXRs are carried forward." },
  { id: "scope-gate", status: "pass", evidence: "No Simulator, Unity import, Unity scene, build, install, or device work occurred." },
];
gate10.readiness = {
  ready: false,
  blockers: ["Three.js calibrated viewer capture and full automated tests pending."],
  note: "Corrected files and controlled Blender evidence pass; browser verification remains.",
};
manifest.currentState.visualApproval = "gate10-rev11-browser-validation-pending-not-pushed";
manifest.currentState.blenderModelingStatus = "gate10-rev11-corrected-evidence-registered";
manifest.currentState.diagnosis = "Rev 10 washout came from both loose portable extensions and uncalibrated previews. Rev 11 uses bounded explicit PBR and controlled neutral HDR viewing.";
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate10-rev11-corrected-evidence-registered",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  rejectedRevision: 10,
  rejectedExactWording: "almost entirely white/washed out",
  correctedRevision: 11,
  correctedGlbSha256: build.outputs.glb.sha256,
  geometryDigest: build.preserved.geometryDigest,
  uvDigest: build.preserved.uvDigest,
  objectiveMetrics: gate10.exportSpec.objectiveMetrics,
  next: "calibrated Three.js browser verification",
  simulatorUsed: false,
  unityUsed: false,
  shippingChanged: false,
  deviceWork: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  stageStatus: gate10.status,
  glbSha256: gate10.exportSpec.glbSha256,
  reviewArtifacts: gate10.reviewArtifactIds,
}, null, 2));
