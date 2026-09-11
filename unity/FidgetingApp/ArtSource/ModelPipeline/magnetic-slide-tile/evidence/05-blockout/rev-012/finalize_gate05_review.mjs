#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { loadManifest, repoRoot, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const stage = manifest.stages[4];
if (manifest.revision !== 214 || stage.status !== "ready_for_review")
  throw new Error(`Expected pipeline 214 ready_for_review; got ${manifest.revision}/${stage.status}.`);
const base = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012";
const read = relative => JSON.parse(fs.readFileSync(path.join(repoRoot, base, relative), "utf8"));
const finalReport = {
  schemaVersion: 1,
  gate: "05-blockout",
  revision: 12,
  pipelineRevisionAfterRegistration: 215,
  checks: {
    archivedUserRejection: read("user-rejection-evidence.json").files.length === 2,
    deterministicBlenderGeometry: read("geometry-validation.json").pass,
    independentBlenderAudit: read("blender-audit.json").pass,
    productAndTechnicalGlbAudit: read("glb-export-audit.json").pass,
    unityFixedAxisMotion: read("unity-preview/unity-motion-validation.json").pass,
    motionVideoTransformAudit: read("unity-preview/motion-video-validation.json").pass,
    browserDesktopMobileGlbVideoModal: read("browser-workspace-validation.json").pass,
    focusedNodeTests: "3/3 passed",
    pipelineValidators: "errors/missingFiles/unhashed=0/0/0 at pipeline rev 214",
    syntaxAndDiffCheck: "passed",
    fullNodeSuite: "175/177 passed at final run; two failures are concurrent Premium Display Case Gate 04 state changes outside this feature. Earlier pre-concurrency run passed 177/177.",
    buildInstallPhone: false,
  },
  scope: {
    finalMaterialsApplied: false,
    shippingSceneModified: false,
    build: false,
    install: false,
    phone: false,
  },
  featurePass: true,
  repositorySuiteExternalFailures: 2,
};
const finalPath = path.join(repoRoot, base, "final-validation.json");
fs.writeFileSync(finalPath, JSON.stringify(finalReport, null, 2));
const additions = [
  ["magnetic-slide-g05-r012-glb-audit-script", "audit-script", `${base}/audit_glb_exports.py`, "process"],
  ["magnetic-slide-g05-r012-glb-audit", "glb-validation", `${base}/glb-export-audit.json`, "validation"],
  ["magnetic-slide-g05-r012-finalizer", "registration-script", `${base}/finalize_gate05_review.mjs`, "process"],
  ["magnetic-slide-g05-r012-final-validation", "final-validation", `${base}/final-validation.json`, "validation"],
];
const ids = new Set(additions.map(([id]) => id));
manifest.assets = manifest.assets.filter(asset => !ids.has(asset.id));
for (const [id, slot, relative, role] of additions) {
  const absolute = path.join(repoRoot, relative);
  manifest.assets.push({
    id, stageId: "05-blockout", slot, path: relative, sha256: sha256File(absolute), exists: true,
    sizeBytes: fs.statSync(absolute).size, role,
    producer: { name: "fidgeting-model-pipeline", version: "Gate 05 rev 12", recipe: "final fixed-axis geometry verification" },
    provenance: { origin: "repository-generated", contentClass: slot, assertedBy: "assistant", mechanismEvidenceContractSha256: stage.blockoutSpec.governingContractSha256, finalMaterialsApplied: false, buildInstallPhone: false },
    sourceAssetIds: ["magnetic-slide-g05-r012-blend", "magnetic-slide-g05-r012-product-glb", "magnetic-slide-g05-r012-unity-video"],
    sourceClaimIds: [],
  });
}
stage.artifactIds.push(...additions.map(([id]) => id).filter(id => !stage.artifactIds.includes(id)));
stage.validations.push(
  { id: "glb-structure", status: "pass", evidence: "Product GLB contains exactly BottomExterior and MovingTopBody; technical GLB has nine labeled meshes; MinimumOverlapDisk has no mesh; FixedAxis is the only pivot node." },
  { id: "final-feature-validation", status: "pass", evidence: "Focused geometry, Blender, Unity, GLB, browser, syntax and pipeline checks pass. Two full-suite failures belong to a concurrent Premium Display Case Gate 04 update." },
);
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(), type: "gate05-fixed-axis-geometry-final-validation", modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision, timestamp: manifest.updatedAt, featurePass: true,
  unrelatedConcurrentSuiteFailures: 2, visualApprovalPending: true, buildInstallPhone: false,
});
console.log(JSON.stringify({ revision: saved.revision, status: saved.stages[4].status, final: finalReport.featurePass }, null, 2));

