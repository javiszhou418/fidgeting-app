import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { loadManifest, repoRoot, sha256File } from "../pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const gate = path.resolve(
  here,
  "../../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-010",
);
const read = (name) => JSON.parse(fs.readFileSync(path.join(gate, name), "utf8"));

test("Gate 09 and corrected Gate 10 remain approved", () => {
  const manifest = loadManifest("magnetic-slide-tile");
  const gate09 = manifest.stages[8];
  const gate10 = manifest.stages[9];
  assert.equal(manifest.currentStageId, "12-shipping");
  assert.equal(gate09.status, "approved");
  assert.equal(gate09.decision.notes, "继续");
  assert.equal(gate10.status, "approved");
  assert.equal(gate10.exportSpec.revision, 11);
  const rejectedRev10 = gate10.historicalRevisions.find((item) => item.evidenceRevision === 10);
  assert.equal(rejectedRev10.status, "rejected");
  assert.equal(manifest.stages[10].status, "approved");
  assert.equal(manifest.stages[11].status, "approved");
  assert.equal(
    manifest.currentState.visualApproval,
    "gate12-r004-variant-b-approved-review-ui"
  );
});

test("authoritative Blend preserves current geometry material and UV state", () => {
  const build = read("export-build-report.json");
  const audit = read("authoritative-blend-audit.json");
  assert.equal(build.pass, true);
  assert.equal(audit.pass, true);
  assert.equal(build.approved.geometryDigest, "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952");
  assert.equal(build.approved.materialSourceSha256, "8538b4142c9d6b5c89e30e3f915f99a33dfff8eab158db449278d9cca605b10c");
  assert.equal(build.source.gate09ApprovalExactWording, "继续");
  assert.deepEqual(build.before.bounds.sizeMm, [31, 50, 12]);
  assert.deepEqual(build.before.digests, build.after.digests);
  assert.equal(audit.checks.clampImageNodes, true);
  assert.equal(audit.checks.minimumOverlapEmpty, true);
  assert.equal(audit.checks.noCavityOrProxyMesh, true);
});

test("FBX GLB and collision independently reimport", () => {
  const report = read("reimport-validation.json");
  assert.equal(report.pass, true);
  assert.deepEqual(report.results.glbStructure.counts, {
    nodes: 20,
    meshes: 8,
    materials: 7,
    textures: 4,
    images: 4,
    animations: 0,
  });
  for (const format of ["fbx", "glb"]) {
    assert.equal(report.results[format].pass, true);
    assert.equal(report.results[format].checks.singlePivot, true);
    assert.equal(report.results[format].checks.fourGrooves, true);
    assert.equal(report.results[format].checks.partitionTriangles, true);
    assert.equal(report.results[format].checks.sideArtworkZero, true);
    assert.equal(report.results[format].checks.undersideArtworkZero, true);
    assert.equal(report.results[format].checks.minimumOverlapNotMesh, true);
    assert.equal(report.results[format].checks.noAnimations, true);
  }
  assert.equal(report.results.glbStructure.checks.tangents, true);
  assert.equal(report.results.glbStructure.checks.clampSamplers, true);
  assert.equal(report.results.collision.checks.nonRenderingMetadata, true);
  assert.equal(report.results.collision.checks.noMaterials, true);
});

test("manifest locks package pixels environment and endpoint interlock", () => {
  const validation = read("export-manifest-validation.json");
  const packageManifest = JSON.parse(
    fs.readFileSync(path.join(gate, "package/export-manifest-r010.json"), "utf8"),
  );
  assert.equal(validation.pass, true);
  assert.equal(packageManifest.pass, true);
  assert.equal(packageManifest.glbTransportAudit.checks.pixelIdentity, true);
  assert.equal(packageManifest.glbTransportAudit.checks.nativeNpot, true);
  assert.equal(packageManifest.endpointInterlock.rotationLockedBelowSMax, true);
  assert.equal(packageManifest.endpointInterlock.slideLockedAtNonzeroAngle, true);
  assert.deepEqual(packageManifest.endpointInterlock.rotationAtSMax, {
    degrees: 360,
    detents: 30,
    stepDegrees: 12,
  });
  assert.equal(packageManifest.defaultState.linearVelocityMmPerSecond, 0);
  assert.equal(packageManifest.defaultState.angularVelocityDegreesPerSecond, 0);
  assert.equal(packageManifest.defaultState.animationClips, 0);
  assert.equal(packageManifest.unityImportContract.astcApplied, false);
  for (const [relative, record] of Object.entries(packageManifest.files)) {
    assert.equal(sha256File(path.join(gate, "package", relative)), record.sha256);
  }
});

test("workbench preserves rev 10 and requires corrected GLB interaction", () => {
  const app = fs.readFileSync(path.join(repoRoot, "tools/model-provenance-explorer/app.js"), "utf8");
  assert.match(app, /Gate 10 rev 11 · GLB 白化修正/);
  assert.match(app, /magnetic-slide-tile-export-glb-r010/);
  assert.match(app, /magnetic-slide-tile-export-glb-r011/);
  assert.match(app, /magnetic-slide-tile-gate10-r011-glb-checklist/);
  assert.match(app, /gate10Checklist\.loaded && gate10Checklist\.orbit && gate10Checklist\.zoom/);
  assert.match(app, /real-exported-glb-orbit-zoom/);
});

test("design and delivery records preserve Gate 10 history", () => {
  const bible = fs.readFileSync(
    path.join(repoRoot, "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"),
    "utf8",
  );
  const status = fs.readFileSync(
    path.join(repoRoot, "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"),
    "utf8",
  );
  assert.match(bible, /FDB-SLD-065.*Exact Chat Wording “继续”/s);
  assert.match(bible, /FDB-SLD-066.*Rejected.*FDB-SLD-067.*Gate 10 Rev 11 Approved/s);
  assert.match(status, /Magnetic Slide Tile Gate 10 rev 11 GLB 白化修正/);
  assert.match(status, /没有 Simulator、Unity scene、Build、安装或 phone 操作/);
});
