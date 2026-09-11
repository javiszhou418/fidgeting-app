import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";

import { loadManifest, repoRoot, sha256File } from "../pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
const evidence = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-013",
);
const readJson = (name) => JSON.parse(fs.readFileSync(path.join(evidence, name), "utf8"));

test("archives the exact side-wrap rejection", () => {
  const asset = manifest.assets.find(
    ({ id }) => id === "magnetic-slide-tile-material-side-wrap-rejection-r013",
  );
  assert.ok(asset);
  assert.equal(asset.sha256, "a7859940ee1d956755c07a810bc5aeccee75136da092cb8f1891bf9fe6dc8b1b");
  assert.equal(asset.sha256, sha256File(path.join(repoRoot, asset.path)));
  assert.equal(asset.provenance.exactUserWording, "边缘没有图案填充");
});

test("proves the historical material-index collapse", () => {
  const report = readJson("root-cause-report.json");
  assert.equal(report.pass, true);
  assert.equal(report.rootCause.category, "Blender per-polygon material-index mutation");
  assert.deepEqual(report.rootCause.destructiveClearLines, [304, 310]);
  assert.deepEqual(report.rootCause.polygonIndexRestoreLines, []);
  assert.equal(
    report.historicalEvidence.gate07Blend.objects.BottomExterior.materialIndexCounts["0"],
    1,
  );
  assert.equal(
    report.historicalEvidence.gate08Blend.objects.BottomExterior.materialIndexCounts["0"],
    8723,
  );
  assert.equal(
    report.historicalEvidence.gate08Blend.objects.MovingTopBody.materialIndexCounts["0"],
    10783,
  );
});

test("keeps approved geometry while assigning deterministic face zones", () => {
  const report = readJson("material-build-report.json");
  assert.equal(report.pass, true);
  assert.equal(
    report.geometryDigestBefore,
    "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952",
  );
  assert.equal(report.geometryDigestAfter, report.geometryDigestBefore);
  assert.deepEqual(report.partitions.BottomExterior.faceCounts, {
    topArtwork: 1,
    solidDarkSide: 3078,
    polishedSilverRim: 2052,
    neutralUnderside: 3592,
  });
  assert.deepEqual(report.partitions.MovingTopBody.faceCounts, {
    topArtwork: 1,
    solidDarkSide: 5130,
    polishedSilverRim: 2052,
    neutralUnderside: 3600,
  });
  for (const partition of Object.values(report.partitions)) {
    assert.equal(partition.verticalSideArtworkFaceCount, 0);
    assert.deepEqual(partition.slotIds, {
      topArtwork: 0,
      solidDarkSide: 1,
      polishedSilverRim: 2,
      neutralUnderside: 3,
    });
    assert.equal(partition.uv.capUvsWithinZeroOne, true);
    assert.deepEqual(partition.uv.nonCapSentinel, [-1, -1]);
  }
});

test("preserves partitions through GLB and FBX re-import", () => {
  const report = readJson("material-transport-audit.json");
  assert.equal(report.pass, true);
  assert.equal(report.glbContract.allSamplersClampNoWrap, true);
  assert.equal(report.glbContract.onlyArtworkMaterialsSampleImages, true);
  assert.equal(report.glbContract.fourPrimitivesPerProduct, true);
  assert.equal(report.glbContract.meshCount, 2);
  assert.deepEqual(
    report.glbContract.materials.map(({ id, name }) => [id, name]),
    [
      [0, "M07R13_LowerTopArtwork"],
      [1, "M07R13_SolidDarkSide"],
      [2, "M07R13_PolishedBrightSilverRim"],
      [3, "M07R13_NeutralUnderside"],
      [4, "M07R13_UpperTopArtwork"],
    ],
  );
  for (const format of ["blend", "glbReimport", "fbxReimport"]) {
    for (const name of ["BottomExterior", "MovingTopBody"]) {
      const object = report[format][name];
      assert.equal(object.sideWallArtworkFaceCount, 0);
      assert.equal(object.undersideArtworkFaceCount, 0);
      assert.equal(object.nonCapTexturedFaceCount, 0);
      assert.equal(object.topArtworkPresent, true);
      assert.equal(object.triangleCounts.topArtwork, 511);
    }
  }
  assert.deepEqual(
    report.glbReimport.BottomExterior.triangleCounts,
    report.fbxReimport.BottomExterior.triangleCounts,
  );
  assert.deepEqual(
    report.glbReimport.MovingTopBody.triangleCounts,
    report.fbxReimport.MovingTopBody.triangleCounts,
  );
});

test("keeps legal endpoint-only motion and hidden mechanics", () => {
  const report = readJson("endpoint-material-motion-audit.json");
  assert.equal(report.pass, true);
  assert.equal(report.denseSamples, 4359);
  assert.equal(report.blockedRotationAttempts, 4000);
  assert.equal(report.blockedSlideAttempts, 359);
  assert.equal(report.maxPivotVarianceMm, 0);
  assert.equal(report.minimumDiskCoverageMisses, 0);
  assert.equal(report.maximumSurfaceIntersectionCount, 0);
  assert.equal(report.bottomTopPlaneMaximumDeviationMm, 0);
  assert.equal(report.axisBossProtrusionMm, 0.2);
  assert.equal(report.topUndersideGrooveCount, 4);
  assert.equal(report.turntable.sourceFrames, 90);
  assert.equal(report.turntable.encodedFrames, 180);
  assert.equal(report.turntable.durationSeconds, 6);
});

test("preserves approved Gate 07 rev 13", () => {
  assert.equal(manifest.currentStageId, "12-shipping");
  assert.equal(gate07.revision, 13);
  assert.equal(gate07.status, "approved");
  assert.equal(gate07.decision.notes, "通过");
  assert.equal(gate07.materialSpec.geometryChanged, false);
  assert.equal(gate07.materialSpec.mechanismChanged, false);
  assert.equal(gate07.materialSpec.sideWallArtworkPixels, 0);
  assert.equal(manifest.stages[7].status, "approved");
  assert.equal(manifest.stages[8].status, "approved");
  assert.equal(manifest.stages[9].status, "approved");
  assert.equal(manifest.stages[10].status, "approved");
  assert.equal(manifest.stages[11].status, "approved");
  for (const id of [
    "magnetic-slide-tile-material-lookdev-r013",
    "magnetic-slide-tile-material-turntable-r013",
    "magnetic-slide-tile-material-review-board-r013",
    "magnetic-slide-tile-material-closeups-r013",
    "magnetic-slide-tile-material-comparison-r013",
  ]) {
    assert.ok(gate07.reviewArtifactIds.includes(id));
    const asset = manifest.assets.find((candidate) => candidate.id === id);
    assert.ok(asset);
    assert.equal(asset.sha256, sha256File(path.join(repoRoot, asset.path)));
  }
});
