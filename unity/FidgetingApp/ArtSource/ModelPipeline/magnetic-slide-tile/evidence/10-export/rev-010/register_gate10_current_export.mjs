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

const modelId = "magnetic-slide-tile";
const manifest = loadManifest(modelId);
const gate09 = manifest.stages.find((stage) => stage.id === "09-environment");
const stage = manifest.stages.find((item) => item.id === "10-export");
if (
  manifest.revision !== 244
  || gate09?.status !== "approved"
  || gate09?.decision?.notes !== "继续"
  || stage?.status !== "draft"
  || stage?.exportSpec?.revision !== 10
) {
  throw new Error("Expected approved Gate 09 rev 9 and draft Gate 10 rev 10 at revision 244.");
}
const output = path.dirname(fileURLToPath(import.meta.url));
const local = (filename) => path.join(output, filename);
const readJson = (filename) => JSON.parse(fs.readFileSync(local(filename), "utf8"));
const build = readJson("export-build-report.json");
const reimported = readJson("reimport-validation.json");
const blendAudit = readJson("authoritative-blend-audit.json");
const textureAudit = readJson("texture-environment-validation.json");
const manifestAudit = readJson("export-manifest-validation.json");
if (![build, reimported, blendAudit, textureAudit, manifestAudit].every((report) => report.pass)) {
  throw new Error("Gate 10 rev 10 evidence is not fully validated.");
}
if (
  build.source.sha256 !== stage.exportSpec.sourceBlendSha256
  || build.approved.geometryDigest !== stage.exportSpec.geometryDigest
  || build.approved.materialSourceSha256 !== stage.exportSpec.materialDigest
  || build.approved.mechanismContractSha256 !== stage.exportSpec.governingContractSha256
  || build.approved.portabilityContractSha256 !== stage.exportSpec.portabilityContractSha256
  || build.source.gate09ApprovalExactWording !== "继续"
) {
  throw new Error("Gate 10 consumed stale inputs.");
}

const definitions = [
  ["starter", "approval-transition", local("start_gate10_current_export.mjs"), "process"],
  ["texture-builder", "texture-environment-builder", local("prepare_export_assets.py"), "process"],
  ["export-builder", "export-builder", local("build_export_package.py"), "process"],
  ["reimport-validator", "reimport-validator", local("validate_export_reimports.py"), "process"],
  ["blend-auditor", "authoritative-blend-auditor", local("audit_authoritative_blend.py"), "process"],
  ["manifest-builder", "export-manifest-builder", local("build_export_manifest.py"), "process"],
  ["registrar", "registration-source", local("register_gate10_current_export.mjs"), "process"],
  ["build-report", "export-build-validation", local("export-build-report.json"), "validation"],
  ["reimport-report", "fbx-glb-collision-validation", local("reimport-validation.json"), "validation"],
  ["blend-audit", "authoritative-blend-validation", local("authoritative-blend-audit.json"), "validation"],
  ["texture-audit", "texture-environment-validation", local("texture-environment-validation.json"), "validation"],
  ["manifest-audit", "export-manifest-validation", local("export-manifest-validation.json"), "validation"],
  ["blend", "source-blend", local("package/magnetic-slide-tile-authoritative-r010.blend"), "source-model"],
  ["fbx", "render-fbx", local("package/magnetic-slide-tile-render-r010.fbx"), "source-model"],
  ["glb", "interactive-model", local("package/magnetic-slide-tile-render-r010.glb"), "source-model"],
  ["collision", "collision-fbx", local("package/magnetic-slide-tile-collision-r010.fbx"), "source-model"],
  ["manifest", "export-manifest", local("package/export-manifest-r010.json"), "contract"],
  ["hierarchy-motion", "hierarchy-motion-metadata", local("package/hierarchy-motion-metadata-r010.json"), "contract"],
  ["unity-import", "unity-import-astc-plan", local("package/unity-import-contract-r010.json"), "contract"],
  ["gate09-contract", "gate09-portability-contract", local("package/environment/unity-portability-contract-r009.json"), "contract"],
  ["target-hdri", "target-shipping-hdr", local("package/environment/target-shipping-studio-r009.exr"), "source-model"],
  ["neutral-hdri", "neutral-control-hdr", local("package/environment/neutral-control-r009.exr"), "source-model"],
  ["hdri-preview", "target-hdr-preview", local("package/environment/target-shipping-studio-r009-preview.png"), "analysis"],
  ["cubemap-contract", "cubemap-orientation-contract", local("package/environment/cubemap/cubemap-contract.json"), "contract"],
  ["upper-albedo", "upper-base-color", local("package/textures/upper-albedo.png"), "source-model"],
  ["lower-albedo", "lower-base-color", local("package/textures/lower-albedo.png"), "source-model"],
  ["upper-artwork-mask", "upper-artwork-mask", local("package/textures/upper-artwork-mask.png"), "source-model"],
  ["lower-artwork-mask", "lower-artwork-mask", local("package/textures/lower-artwork-mask.png"), "source-model"],
  ["perimeter-mask", "top-perimeter-mask", local("package/textures/top-perimeter-mask.png"), "source-model"],
  ["upper-maskmap", "upper-mask-map", local("package/textures/upper-maskmap.png"), "source-model"],
  ["lower-maskmap", "lower-mask-map", local("package/textures/lower-maskmap.png"), "source-model"],
  ["upper-normal", "upper-normal-map", local("package/textures/upper-normal.png"), "source-model"],
  ["lower-normal", "lower-normal-map", local("package/textures/lower-normal.png"), "source-model"],
  ["review-board", "export-review-summary", local("gate10-r010-export-review-board.png"), "analysis"],
  ["glb-hero", "exported-glb-hero", local("gate10-r010-glb-hero.png"), "blender-render"],
  ["glb-top", "exported-glb-top", local("gate10-r010-glb-top.png"), "blender-render"],
];
for (const face of ["positive-x", "negative-x", "positive-y", "negative-y", "positive-z", "negative-z"]) {
  definitions.push([`cubemap-${face}`, `cubemap-${face}`, local(`package/environment/cubemap/${face}.exr`), "source-model"]);
}
for (const name of ["upper-roughness", "lower-roughness"]) {
  definitions.push([name, name, local(`package/textures/${name}.png`), "source-model"]);
}

const sourceAssetIds = [
  "slider-analysis-mechanism-evidence-contract-r017",
  "magnetic-slide-tile-geometry-blend-r005",
  "magnetic-slide-tile-material-blend-r013",
  "magnetic-slide-tile-lighting-blend-r006",
  "magnetic-slide-tile-environment-blend-r009",
  "magnetic-slide-tile-environment-target-hdr-r009",
  "magnetic-slide-tile-environment-portability-contract-r009",
];
const records = definitions.map(([suffix, slot, absolute, role]) => {
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${absolute}`);
  return {
    id: `${modelId}-export-${suffix}-r010`,
    stageId: "10-export",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Gate 10 current export workflow",
      version: "Blender 5.2.0 LTS / Python 3 / Node.js",
      recipe: local("build_export_package.py"),
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate10Revision: 10,
      sourceGate09Revision: 9,
      approvedGate09Wording: "继续",
      sourceBlendSha256: build.source.sha256,
      geometryDigest: build.approved.geometryDigest,
      materialSourceSha256: build.approved.materialSourceSha256,
      mechanismEvidenceContractSha256: build.approved.mechanismContractSha256,
      portabilityContractSha256: build.approved.portabilityContractSha256,
      exportManifestSha256: manifestAudit.manifest.sha256,
      note: "Fresh Gate 10 rev 10 evidence. Gate 10 rev 9 remains immutable stale history.",
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

const assetId = (suffix) => `${modelId}-export-${suffix}-r010`;
stage.status = "ready_for_review";
stage.artifactIds = records.map((record) => record.id);
stage.reviewArtifactIds = [
  assetId("glb"),
  assetId("review-board"),
  assetId("glb-hero"),
  assetId("glb-top"),
  assetId("manifest"),
];
stage.inputDigest = digestValues([
  build.source.sha256,
  build.approved.geometryDigest,
  build.approved.materialSourceSha256,
  build.approved.mechanismContractSha256,
  build.approved.portabilityContractSha256,
]);
stage.outputDigest = digestValues([
  build.formats.blend.sha256,
  build.formats.fbx.sha256,
  build.formats.glb.sha256,
  build.formats.collisionFbx.sha256,
  manifestAudit.manifest.sha256,
]);
stage.validations = [
  {
    id: "gate09-rev9-exact-approval",
    status: "pass",
    evidence: `Exact wording “继续”; source Blend ${build.source.sha256}.`,
  },
  {
    id: "authoritative-source-preserved",
    status: "pass",
    evidence: `Geometry ${build.approved.geometryDigest}; material state ${build.after.digests.materials}; UV ${build.after.digests.uvs}.`,
  },
  {
    id: "fbx-glb-independent-reimport",
    status: "pass",
    evidence: "FBX and GLB independently reimport at 0.031×0.050×0.012 m with 20 nodes, 8 meshes, 7 materials, 4 embedded images, and 0 animations.",
  },
  {
    id: "hierarchy-pivot-grooves",
    status: "pass",
    evidence: "Fixed bottom, one FixedAxis, carrier, two followers, two ball candidates, moving top, and four underside groove empties preserve exact ownership.",
  },
  {
    id: "flat-bottom-raised-boss-no-proxy",
    status: "pass",
    evidence: "Bottom remains flat; 0.2 mm internal raised-boss contract remains non-recessed; MinimumOverlapDisk is a non-rendering Empty; no stale overlap mesh or cavity exists.",
  },
  {
    id: "corrected-material-partitions",
    status: "pass",
    evidence: "Upper/lower top artwork each retain 511 triangles; side and underside artwork remain exactly 0; dark side and bright silver rim partitions survive FBX/GLB reimport.",
  },
  {
    id: "normals-tangents-uv-textures",
    status: "pass",
    evidence: "FBX FACE smoothing and GLB NORMAL/TANGENT/TEXCOORD_0 pass. Embedded albedo is decoded-byte exact; roughness is exact in glTF G; all images remain 620×1000 with CLAMP_TO_EDGE.",
  },
  {
    id: "environment-portability",
    status: "pass",
    evidence: `Current EXR/cubemap and neutral-display-v1 contract ${build.approved.portabilityContractSha256} are byte-copied into the package.`,
  },
  {
    id: "endpoint-interlock-metadata",
    status: "pass",
    evidence: "Rotation locks below sMax; 30×12° spans 360° only at sMax; slide locks at nonzero angle; return requires align then close.",
  },
  {
    id: "closed-zero-motion-no-animation",
    status: "pass",
    evidence: "Default is closed at zero linear/angular velocity; no Blender actions, drivers, GLB animations, or FBX animation bake.",
  },
  {
    id: "collision-and-unity-plan",
    status: "pass",
    evidence: "Two material-free collision meshes exist only in the separate non-rendering FBX. Unity import/ASTC comparison is specified but not applied.",
  },
  {
    id: "scope-gate",
    status: "pass",
    evidence: "No Simulator, Unity import, Unity scene, build, install, or phone work occurred; old shipping model remains default.",
  },
];
stage.exportSpec = {
  ...stage.exportSpec,
  revision: 10,
  evidenceRevision: 10,
  sourceGate09Revision: 9,
  sourceGate09ApprovalWording: "继续",
  sourceBlendSha256: build.source.sha256,
  geometryDigest: build.approved.geometryDigest,
  materialDigest: build.approved.materialSourceSha256,
  materialStateDigest: build.after.digests.materials,
  uvDigest: build.after.digests.uvs,
  environmentSha256: textureAudit.copied["target-shipping-studio-r009.exr"].sha256,
  portabilityContractSha256: build.approved.portabilityContractSha256,
  governingContractSha256: build.approved.mechanismContractSha256,
  authoritativeBlendSha256: build.formats.blend.sha256,
  fbxSha256: build.formats.fbx.sha256,
  glbSha256: build.formats.glb.sha256,
  collisionSha256: build.formats.collisionFbx.sha256,
  hierarchyMotionSha256: build.formats.hierarchyMotion.sha256,
  exportManifestSha256: manifestAudit.manifest.sha256,
  unityImportContractSha256: textureAudit.unityImportContract.sha256,
  closedBoundsMm: build.after.bounds.sizeMm,
  glbCounts: reimported.results.glbStructure.counts,
  meshSmoothType: "FACE",
  smoothSidesHardCaps: true,
  npotPolicy: "None; preserve 620×1000",
  textureAddressMode: "CLAMP_TO_EDGE",
  astcApplied: false,
  defaultPose: "closed-zero-motion",
  interactiveReviewArtifactId: assetId("glb"),
  reviewQuestion: "真实导出的 GLB 是否保留尺寸、层级、轴心、材质分区和端点互锁？",
  deliveryState: {
    visualApproval: "pending",
    simulatorUsed: false,
    unityUsed: false,
    shippingSceneModified: false,
    gate11Advanced: false,
    gate12Started: false,
    buildInstallPhone: false,
    deviceAcceptance: "pending",
  },
};
stage.readiness = {
  ready: true,
  blockers: [],
  note: "Interact with the real exported GLB: load, orbit, and zoom. Static renders are supplemental. Unity and device work have not started.",
};
delete stage.staleReason;
manifest.currentStageId = "10-export";
manifest.currentState.visualApproval = "gate10-rev10-review-pending-not-pushed";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.blenderModelingStatus = "gate10-rev10-ready-for-review";
manifest.currentState.unityStatus = "not-used-old-shipping-default";
manifest.currentState.simulatorStatus = "not-used";
manifest.currentState.workbench = "persistent-seven-tab-current-gate10-export";
manifest.currentState.diagnosis = "Gate 10 rev 10 is a fresh export from approved Gate 09 rev 9. Independent FBX/GLB/collision reimport passed.";
for (const downstream of manifest.stages.slice(10)) {
  downstream.status = "stale";
  downstream.staleReason = "Gate 10 rev 10 awaits explicit GLB review approval.";
}
manifest.issues = manifest.issues.filter((issue) => issue.id !== "slider-gate09-r009-review");
manifest.issues.push({
  id: "slider-gate10-r010-review",
  stageId: "10-export",
  assetId: assetId("glb"),
  severity: "blocker",
  note: "Gate 10 rev 10 passed export validation and awaits real GLB interaction and approval.",
  status: "awaiting-user-export-review",
});
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate10-rev10-current-export-ready",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "10-export",
  revision: 10,
  status: "ready_for_review",
  gate09ApprovalExactWording: "继续",
  sourceBlendSha256: build.source.sha256,
  geometryDigest: build.approved.geometryDigest,
  materialStateDigest: build.after.digests.materials,
  uvDigest: build.after.digests.uvs,
  authoritativeBlendSha256: build.formats.blend.sha256,
  fbxSha256: build.formats.fbx.sha256,
  glbSha256: build.formats.glb.sha256,
  collisionSha256: build.formats.collisionFbx.sha256,
  exportManifestSha256: manifestAudit.manifest.sha256,
  artifactIds: stage.artifactIds,
  simulatorUsed: false,
  unityUsed: false,
  shippingChanged: false,
  deviceWork: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate09: "approved",
  gate10: "ready_for_review",
  assets: records.length,
  glbSha256: build.formats.glb.sha256,
  exportManifestSha256: manifestAudit.manifest.sha256,
}, null, 2));
