import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

import { loadManifest, repoRoot, sha256File } from "../pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate06 = manifest.stages.find((stage) => stage.id === "06-geometry");
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
const rev12 = gate07.historicalRevisions.find((revision) => revision.revision === 12);
const evidence = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-012",
);
const readJson = (name) => JSON.parse(fs.readFileSync(path.join(evidence, name), "utf8"));

test("approves Gate 06 with exact chat wording", () => {
  assert.equal(gate06.status, "approved");
  assert.equal(gate06.revision, 5);
  assert.equal(gate06.decision.notes, "继续，继续");
  assert.equal(manifest.currentStageId, "12-shipping");
});

test("preserves Gate 07 rev 12 geometry and contract history", () => {
  assert.ok(rev12);
  assert.equal(rev12.status, "rejected-superseded");
  assert.equal(rev12.materialSpec.revision, 12);
  assert.equal(rev12.materialSpec.sourceGate06Revision, 5);
  assert.equal(rev12.materialSpec.evaluatedGeometryDigest, "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952");
  assert.equal(rev12.materialSpec.governingContractSha256, "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571");
  assert.equal(rev12.materialSpec.geometryChanged, false);
});

test("reuses approved textures byte for byte", () => {
  const texture = readJson("texture-lineage.json");
  assert.equal(texture.pass, true);
  assert.equal(texture.appearanceChanged, false);
  assert.equal(texture.outputs.upper.albedoSha256, "c0e9305d475cd2c591efc8a833a0aafb1aef4ccc437d84a3417674e6d1b453a5");
  assert.equal(texture.outputs.upper.roughnessSha256, "854f1dbc393585ff9b88f808c1a46a35b091088ac8b83894763f502876e3df6a");
  assert.equal(texture.outputs.lower.albedoSha256, "968c1e87ca2d5ea7c8fc57106e42bcd09dc95395fac7dd3be569e580ea8850eb");
  assert.equal(texture.outputs.lower.roughnessSha256, "ca2697560a2e57685a71c423f15f70a72ebb47c93c53cae0e3a8dae0b3248245");
});

test("permits rotation only at the maximum slide endpoint", () => {
  const motion = readJson("endpoint-material-motion-audit.json");
  assert.equal(motion.pass, true);
  assert.equal(motion.blockedRotationAttempts, 4000);
  assert.equal(motion.blockedSlideAttempts, 359);
  assert.equal(motion.maxPivotVarianceMm, 0);
  assert.ok(motion.maxTopResidualMm <= 5e-6);
  assert.equal(motion.minimumDiskCoverageMisses, 0);
  assert.equal(motion.maximumSurfaceIntersectionCount, 0);
  assert.ok(motion.forbiddenPoseFilesAbsent.every((name) => !fs.existsSync(path.join(evidence, name))));
});

test("registers interactive lookdev, turntable and review boards", () => {
  const ids = [
    "magnetic-slide-tile-material-lookdev-r012",
    "magnetic-slide-tile-material-turntable-r012",
    "magnetic-slide-tile-material-source-comparison-r012",
    "magnetic-slide-tile-material-board-r012",
    "magnetic-slide-tile-material-intermediate-r012",
    "magnetic-slide-tile-material-max-open-0-r012",
    "magnetic-slide-tile-material-open-r012",
  ];
  for (const id of ids) {
    assert.ok(rev12.reviewArtifactIds.includes(id));
    const asset = manifest.assets.find((candidate) => candidate.id === id);
    assert.ok(asset);
    assert.equal(asset.sha256, sha256File(path.join(repoRoot, asset.path)));
    assert.equal(asset.provenance.mechanismEvidenceContractSha256, rev12.materialSpec.governingContractSha256);
  }
});

test("keeps device work pending after downstream approval", () => {
  assert.equal(gate07.status, "approved");
  assert.equal(gate07.materialSpec.revision, 13);
  assert.equal(manifest.stages[7].status, "approved");
  assert.equal(manifest.stages[8].status, "approved");
  assert.equal(manifest.stages[9].status, "approved");
  assert.equal(manifest.stages[10].status, "approved");
  assert.equal(manifest.stages[11].status, "approved");
  assert.equal(
    manifest.currentState.unityStatus,
    "build44-rotation-direction-fix-source-tested"
  );
  assert.equal(
    manifest.currentState.visualApproval,
    "gate12-r004-variant-b-approved-review-ui"
  );
});
