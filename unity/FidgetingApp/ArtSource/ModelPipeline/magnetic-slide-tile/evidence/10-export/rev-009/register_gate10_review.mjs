#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, repoRoot, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 192) throw new Error(`Expected revision 192, got ${manifest.revision}.`);
const gate09 = manifest.stages[8];
const gate10 = manifest.stages[9];
if (gate09.status !== "approved" || gate09.decision?.notes !== "你给我看一下最终在 Unity 里边的呈现吧。") throw new Error("Gate 09 exact approval is missing.");
if (gate10.status !== "draft" || gate10.exportSpec?.revision !== 9) throw new Error("Gate 10 rev 9 draft is not current.");
const output = path.dirname(fileURLToPath(import.meta.url));
const readJson = (name) => JSON.parse(fs.readFileSync(path.join(output, name), "utf8"));
const build = readJson("export-build-report.json");
const reimported = readJson("reimport-validation.json");
const blendAudit = readJson("authoritative-blend-audit.json");
const textures = readJson("texture-export-manifest.json");
const portability = readJson("portability-manifest-validation.json");
const summary = readJson("export-summary-validation.json");
if (![build, reimported, blendAudit, textures, portability, summary].every((report) => report.pass)) throw new Error("Gate 10 validation failed.");
const local = (name) => path.join(output, name);
const packageFile = (name) => path.join(output, "package", name);
const definitions = [
  ["magnetic-slide-tile-export-prepare-r009", "approval-transition", local("prepare_gate10.mjs"), "process"],
  ["magnetic-slide-tile-export-texture-builder-r009", "texture-builder", local("prepare_export_assets.py"), "process"],
  ["magnetic-slide-tile-export-builder-r009", "export-builder", local("build_export_package.py"), "process"],
  ["magnetic-slide-tile-export-reimport-validator-r009", "reimport-validator", local("validate_export_reimports.py"), "process"],
  ["magnetic-slide-tile-export-blend-auditor-r009", "blend-auditor", local("audit_authoritative_blend.py"), "process"],
  ["magnetic-slide-tile-export-manifest-builder-r009", "manifest-builder", local("build_export_manifest.py"), "process"],
  ["magnetic-slide-tile-export-summary-builder-r009", "summary-builder", local("build_export_summary.py"), "process"],
  ["magnetic-slide-tile-export-register-r009", "registration-script", local("register_gate10_review.mjs"), "process"],
  ["magnetic-slide-tile-export-build-report-r009", "export-build-report", local("export-build-report.json"), "validation"],
  ["magnetic-slide-tile-export-reimport-validation-r009", "reimport-validation", local("reimport-validation.json"), "validation"],
  ["magnetic-slide-tile-export-blend-audit-r009", "authoritative-blend-audit", local("authoritative-blend-audit.json"), "validation"],
  ["magnetic-slide-tile-export-texture-manifest-r009", "texture-export-manifest", local("texture-export-manifest.json"), "validation"],
  ["magnetic-slide-tile-export-portability-validation-r009", "portability-manifest-validation", local("portability-manifest-validation.json"), "validation"],
  ["magnetic-slide-tile-export-summary-validation-r009", "export-summary-validation", local("export-summary-validation.json"), "validation"],
  ["magnetic-slide-tile-export-unity-manifest-r009", "unity-export-manifest", local("unity-export-manifest.json"), "contract"],
  ["magnetic-slide-tile-export-blend-r009", "authoritative-blend", packageFile("magnetic-slide-tile-authoritative-r009.blend"), "source-model"],
  ["magnetic-slide-tile-export-fbx-r009", "render-fbx", packageFile("magnetic-slide-tile-render-r009.fbx"), "export"],
  ["magnetic-slide-tile-export-glb-r009", "interactive-export-glb", packageFile("magnetic-slide-tile-render-r009.glb"), "export"],
  ["magnetic-slide-tile-export-collision-r009", "collision-fbx", packageFile("magnetic-slide-tile-collision-r009.fbx"), "export"],
  ["magnetic-slide-tile-export-hierarchy-motion-r009", "hierarchy-motion-metadata", packageFile("hierarchy-motion-metadata-r009.json"), "contract"],
  ["magnetic-slide-tile-export-gate09-contract-r009", "gate09-portability-contract", packageFile("unity-portability-contract-gate09-r008.json"), "contract"],
  ["magnetic-slide-tile-export-hdri-r009", "portable-equirectangular-exr", packageFile("environment/magnetic-slide-tile-shipping-studio-r008.exr"), "analysis"],
  ["magnetic-slide-tile-export-hdri-preview-r009", "portable-environment-preview", packageFile("environment/magnetic-slide-tile-shipping-studio-r008-preview.png"), "analysis"],
  ["magnetic-slide-tile-export-hdri-metadata-r009", "portable-environment-metadata", packageFile("environment/portable-hdri-metadata.json"), "analysis"],
  ["magnetic-slide-tile-export-upper-base-r009", "upper-basecolor", packageFile("textures/upperBaseColor.png"), "analysis"],
  ["magnetic-slide-tile-export-lower-base-r009", "lower-basecolor", packageFile("textures/lowerBaseColor.png"), "analysis"],
  ["magnetic-slide-tile-export-upper-mask-r009", "upper-artwork-mask", packageFile("textures/upperArtworkMask.png"), "analysis"],
  ["magnetic-slide-tile-export-lower-mask-r009", "lower-artwork-mask", packageFile("textures/lowerArtworkMask.png"), "analysis"],
  ["magnetic-slide-tile-export-perimeter-mask-r009", "perimeter-mask", packageFile("textures/perimeterMask.png"), "analysis"],
  ["magnetic-slide-tile-export-upper-maskmap-r009", "upper-maskmap", packageFile("textures/upper-maskmap-r009.png"), "analysis"],
  ["magnetic-slide-tile-export-lower-maskmap-r009", "lower-maskmap", packageFile("textures/lower-maskmap-r009.png"), "analysis"],
  ["magnetic-slide-tile-export-upper-normal-r009", "upper-normal", packageFile("textures/upper-normal-r009.png"), "analysis"],
  ["magnetic-slide-tile-export-lower-normal-r009", "lower-normal", packageFile("textures/lower-normal-r009.png"), "analysis"],
  ["magnetic-slide-tile-export-summary-r009", "compact-export-summary", local("export-review-summary.png"), "analysis"],
  ["magnetic-slide-tile-export-workbench-r009", "workbench-source", path.join(repoRoot, "tools/model-provenance-explorer/app.js"), "process"],
];
const sourceAssetIds = [
  "slider-analysis-mechanism-evidence-contract-r016",
  "magnetic-slide-tile-geometry-blend-r004",
  "magnetic-slide-tile-material-blend-r011",
  "magnetic-slide-tile-lighting-blend-r002",
  "magnetic-slide-tile-environment-blend-r008",
  "magnetic-slide-tile-unity-portability-contract-r008",
];
for (const [id, slot, absolute, role] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${absolute}.`);
  manifest.assets.push({
    id, stageId: "10-export", slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute), exists: true, sizeBytes: fs.statSync(absolute).size, role,
    producer: { name: absolute.endsWith(".blend") || absolute.endsWith(".fbx") || absolute.endsWith(".glb") ? "Blender" : "fidgeting-model-pipeline", version: "5.2.0 LTS", recipe: "Gate 10 rev 9 export from approved Gate 09 rev 8 four-track source" },
    provenance: {
      origin: "repository-generated", contentClass: slot, assertedBy: "assistant",
      gate09ApprovalWording: gate09.decision.notes, gate09SourceSha256: build.source.sha256,
      mechanismEvidenceContractSha256: build.contractSha256, portabilityContractSha256: build.portabilityContractSha256,
      geometryDigest: build.approved.geometryDigest, materialDigest: build.approved.materialDigest,
      simulatorUsed: false, unityImportApplied: false, deviceWork: false,
    },
    sourceAssetIds, sourceClaimIds: [],
  });
}
gate10.status = "ready_for_review";
gate10.artifactIds = definitions.map(([id]) => id);
gate10.reviewArtifactIds = ["magnetic-slide-tile-export-glb-r009", "magnetic-slide-tile-export-summary-r009"];
gate10.inputDigest = build.source.sha256;
gate10.outputDigest = sha256File(packageFile("magnetic-slide-tile-render-r009.glb"));
gate10.validations = [
  { id: "gate09-r008-exact-approval", status: "pass", evidence: `Exact wording “${gate09.decision.notes}”; source SHA-256 ${build.source.sha256}.` },
  { id: "canonical-geometry-material", status: "pass", evidence: `Geometry ${build.approved.geometryDigest}; material ${build.approved.materialDigest}; UV 48fe18368ab074353d693244c1e62ee387f6b52f11f249cf5c8bb38910e3f062.` },
  { id: "bounds-units-hierarchy", status: "pass", evidence: "FBX and GLB re-import at 0.031×0.050×0.012 m with 20 nodes, 8 render meshes and exact named four-groove hierarchy." },
  { id: "normals-tangents-uv", status: "pass", evidence: "FBX FACE smoothing; smooth sides and hard planar caps. GLB primitives include valid split NORMAL, TANGENT and TEXCOORD_0." },
  { id: "flat-bottom-raised-axis", status: "pass", evidence: "Bottom top plane remains Z=5.875 mm; FixedAxisBoss protrudes 0.2 mm; stale two-shell cavity is absent." },
  { id: "textures-artwork-npot", status: "pass", evidence: "Upper/lower masks keep exact hashes and independent files. Native 620×1000 uses NPOT None; 512×1024 distortion is forbidden." },
  { id: "environment-portability", status: "pass", evidence: "Linear Rec.709/D65 2048×1024 EXR byte hash and Gate 09 portability contract are exact; reflection-band environment is forbidden." },
  { id: "collision-separated", status: "pass", evidence: "Two collision meshes exist only in the separate material-free FBX with rendering=false." },
  { id: "motion-metadata", status: "pass", evidence: "Fixed/carrier/top ownership, finite travel, MinimumOverlapDisk, simultaneous transform and 30×12° metadata are included." },
  { id: "closed-no-self-motion", status: "pass", evidence: "Closed default has zero linear/angular velocity, zero animation clips and no actions, drivers or self-motion." },
  { id: "scope", status: "pass", evidence: "No Simulator, Unity import, URP scene change, build, install or device work occurred; old shipping model remains default." },
  { id: "interactive-review-required", status: "pass", evidence: "Primary evidence is the real exported GLB. Workbench approval remains disabled until load, orbit and zoom milestones complete." },
];
gate10.exportSpec = {
  ...gate10.exportSpec,
  authoritativeBlendSha256: sha256File(packageFile("magnetic-slide-tile-authoritative-r009.blend")),
  fbxSha256: sha256File(packageFile("magnetic-slide-tile-render-r009.fbx")),
  glbSha256: gate10.outputDigest,
  collisionSha256: sha256File(packageFile("magnetic-slide-tile-collision-r009.fbx")),
  exportManifestSha256: sha256File(local("unity-export-manifest.json")),
  hierarchyMotionSha256: sha256File(packageFile("hierarchy-motion-metadata-r009.json")),
  textureManifestSha256: sha256File(local("texture-export-manifest.json")),
  closedBoundsMm: [31, 50, 12],
  glbCounts: reimported.results.glbStructure.counts,
  smoothSidesHardCaps: true,
  meshSmoothType: "FACE",
  npotPolicy: "None; preserve 620×1000",
  astcApplied: false,
};
gate10.readiness = { ready: true, blockers: [], note: "Interact with the real exported GLB: load, orbit and zoom. Static summary is supplementary. Visual approval pending; nothing was imported into Unity or pushed to a phone." };
manifest.stages[10].status = "stale";
manifest.stages[10].staleReason = "Gate 10 rev 9 awaits exported GLB approval.";
manifest.stages[11].status = "rejected";
manifest.currentStageId = "10-export";
manifest.currentState.visualApproval = "gate10-rev9-ready-for-review-visual-approval-pending-not-pushed";
manifest.currentState.blenderModelingStatus = "gate10-export-package-ready-for-review";
manifest.currentState.simulatorStatus = "internal-superseded-not-current";
manifest.currentState.unityStatus = "not-started-old-shipping-model-default-gate10-only";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-default-gate10-export";
manifest.currentState.diagnosis = "Gate 09 rev 8 is approved. Gate 10 rev 9 exports the corrected four-track source and requires real GLB interaction before Unity import.";
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(), type: "gate10-export-r009-ready", modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision, timestamp: manifest.updatedAt,
  gate09ApprovalWording: gate09.decision.notes, sourceGate09Sha256: build.source.sha256,
  geometryDigest: build.approved.geometryDigest, materialDigest: build.approved.materialDigest,
  exportGlbSha256: gate10.outputDigest, exportManifestSha256: gate10.exportSpec.exportManifestSha256,
  contractSha256: build.contractSha256, portabilityContractSha256: build.portabilityContractSha256,
  requiredInteraction: ["load real exported GLB", "orbit", "zoom"],
  nextGate: "11-unity-parity-after-explicit-approval", unityChanged: false, deviceWork: false,
});
console.log(JSON.stringify({ revision: saved.revision, gate10: saved.stages[9].status, glb: gate10.outputDigest, assets: definitions.length }, null, 2));

