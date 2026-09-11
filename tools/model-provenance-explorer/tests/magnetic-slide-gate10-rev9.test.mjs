import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { loadManifest, repoRoot, sha256File } from "../pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const gate = path.resolve(here, "../../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-009");
const read = (name) => JSON.parse(fs.readFileSync(path.join(gate, name), "utf8"));

test("Gate 10 export evidence remains preserved through Gate 12 review", () => {
  const manifest = loadManifest("magnetic-slide-tile");
  const gate09 = manifest.stages[8];
  const gate10 = manifest.stages[9];
  const rev9 = gate10.historicalRevisions.find((revision) => revision.evidenceRevision === 9);
  assert.equal(gate09.status, "approved");
  assert.equal(gate10.status, "approved");
  assert.equal(gate10.exportSpec.revision, 11);
  assert.equal(rev9.exportSpec.revision, 9);
  assert.equal(rev9.status, "stale-superseded");
  assert.equal(manifest.currentStageId, "12-shipping");
  assert.equal(manifest.stages[10].status, "approved");
  assert.equal(manifest.stages[10].revision, 11);
  assert.equal(manifest.stages[11].status, "approved");
  assert.equal(
    manifest.currentState.visualApproval,
    "gate12-r004-variant-b-approved-review-ui"
  );
});

test("authoritative source preserves approved geometry and material", () => {
  const build = read("export-build-report.json");
  const audit = read("authoritative-blend-audit.json");
  assert.equal(build.pass, true);
  assert.equal(audit.pass, true);
  assert.equal(build.approved.geometryDigest, "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe");
  assert.equal(build.approved.materialDigest, "366b788bfb329d806ffbffaa3ff9c4789deab3967943fa43dc7f42c9b6609aa8");
  assert.deepEqual(build.before.bounds.sizeMm, [31, 50, 12]);
  assert.equal(build.checks.flatBottomNoCavity, true);
  assert.equal(build.checks.raisedAxis, true);
  assert.equal(audit.checks.smoothSidesHardCaps, true);
  assert.equal(audit.checks.noReflectionBand, true);
});

test("FBX GLB and collision independently re-import", () => {
  const report = read("reimport-validation.json");
  assert.equal(report.pass, true);
  assert.deepEqual(report.results.glbStructure.counts, { nodes: 20, meshes: 8, materials: 7, textures: 4, images: 4, animations: 0 });
  for (const format of ["fbx", "glb"]) {
    assert.equal(report.results[format].pass, true);
    assert.ok(Math.abs(report.results[format].boundsMeters.size[0] - 0.031) < 1e-5);
    assert.ok(Math.abs(report.results[format].boundsMeters.size[1] - 0.05) < 1e-5);
    assert.ok(Math.abs(report.results[format].boundsMeters.size[2] - 0.012) < 1e-5);
    assert.equal(report.results[format].checks.normals, true);
    assert.equal(report.results[format].checks.uvs, true);
  }
  assert.equal(report.results.glbStructure.checks.tangents, true);
  assert.equal(report.results.collision.checks.separateTwoMeshes, true);
  assert.equal(report.results.collision.checks.nonRenderingMetadata, true);
});

test("export package hashes and Unity portability rules are locked", () => {
  const contract = read("unity-export-manifest.json");
  const validation = read("portability-manifest-validation.json");
  assert.equal(validation.pass, true);
  assert.equal(validation.packageFileCount, 21);
  assert.equal(contract.geometry.canonicalDigest, "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe");
  assert.equal(contract.geometry.renderMeshCount, 8);
  assert.equal(contract.textures.upperLowerArtworkIndependent, true);
  assert.equal(contract.textures.npotPolicy.policy, "None / preserve dimensions");
  assert.deepEqual(contract.textures.npotPolicy.sourceResolutionPx, [620, 1000]);
  assert.equal(contract.textures.astcPlan.applied, false);
  assert.equal(contract.collision.rendering, false);
  assert.equal(contract.validation.noMeshSmoothTypeOff, true);
  assert.equal(contract.validation.noStaleTwoShellCavity, true);
  assert.equal(contract.validation.unityImportApplied, false);
  for (const asset of contract.immutablePackageFiles) {
    assert.equal(sha256File(path.join(repoRoot, asset.path)), asset.sha256);
  }
});

test("closed motion metadata preserves four-track mechanism", () => {
  const metadata = JSON.parse(fs.readFileSync(path.join(gate, "package/hierarchy-motion-metadata-r009.json"), "utf8"));
  assert.equal(metadata.defaultState.pose, "closed");
  assert.equal(metadata.defaultState.angularVelocity, 0);
  assert.equal(metadata.defaultState.selfMotion, false);
  assert.equal(metadata.defaultState.animationClips, 0);
  assert.equal(metadata.parts.fourTopUndersideGrooves.length, 4);
  assert.equal(metadata.motion.detentCount, 30);
  assert.equal(metadata.motion.detentStepDegrees, 12);
  assert.equal(metadata.motion.minimumOverlapContainment.allValid, true);
  assert.match(metadata.motion.topTransform, /T_local/);
});

test("workbench requires real GLB load orbit and zoom", () => {
  const app = fs.readFileSync(path.join(repoRoot, "tools/model-provenance-explorer/app.js"), "utf8");
  assert.match(app, /Gate 10 rev 11 · GLB 白化修正/);
  assert.match(app, /magnetic-slide-tile-export-glb-r011/);
  assert.match(app, /gate10Checklist\.loaded && gate10Checklist\.orbit && gate10Checklist\.zoom/);
  assert.match(app, /real-exported-glb-orbit-zoom/);
  assert.match(app, /没有 Unity import/);
});

test("design and delivery records stop before Gate 12 and device work", () => {
  const bible = fs.readFileSync(path.join(repoRoot, "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"), "utf8");
  const status = fs.readFileSync(path.join(repoRoot, "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"), "utf8");
  assert.match(bible, /FDB-SLD-049.*你给我看一下最终在 Unity 里边的呈现吧.*Approved/s);
  assert.match(bible, /FDB-SLD-050.*Approved · Locked by Latest Chat Authority/s);
  assert.match(bible, /FDB-SLD-051.*Gate 11 Rev 9 Rejected/s);
  assert.match(bible, /FDB-SLD-053.*Gate 08 Rev 3 Portable Lighting Ready for Review/s);
  assert.match(status, /Magnetic Slide Tile Gate 11 rev 10 整帧质量阻塞/);
  assert.match(status, /未进入 Gate 12、shipping promotion、build、install、launch 或 phone/);
  assert.match(status, /本轮明确阻塞且未请求批准/);
});

