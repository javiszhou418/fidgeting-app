import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { loadManifest, repoRoot, sha256File } from "../pipeline-core.mjs";

const evidence = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/06-geometry/rev-005"
);
const report = JSON.parse(fs.readFileSync(path.join(evidence, "geometry-validation.json"), "utf8"));
const audit = JSON.parse(fs.readFileSync(path.join(evidence, "blender-audit.json"), "utf8"));
const contractSha = "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571";
const geometryDigest = "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952";

function readGlbJson(filename) {
  const bytes = fs.readFileSync(path.join(evidence, filename));
  assert.equal(bytes.subarray(0, 4).toString("ascii"), "glTF");
  assert.equal(bytes.readUInt32LE(4), 2);
  const jsonLength = bytes.readUInt32LE(12);
  assert.equal(bytes.subarray(16, 20).toString("ascii"), "JSON");
  return {
    bytes,
    json: JSON.parse(bytes.subarray(20, 20 + jsonLength).toString("utf8").trim()),
  };
}

test("binds Gate 06 rev 5 to the approved endpoint contract", () => {
  const manifest = loadManifest("magnetic-slide-tile");
  const gate05 = manifest.stages[4];
  const gate06 = manifest.stages[5];
  assert.equal(manifest.currentStageId, "12-shipping");
  assert.equal(gate05.status, "approved");
  assert.equal(gate05.decision.notes, "可以，可以继续推进。");
  assert.equal(gate06.revision, 5);
  assert.equal(gate06.status, "approved");
  assert.equal(gate06.geometrySpec.governingContractSha256, contractSha);
  assert.equal(gate06.geometrySpec.canonicalGeometryDigest, geometryDigest);
  assert.equal(gate06.geometrySpec.geometryChanged, false);
  assert.equal(gate06.reviewArtifactIds[0], "magnetic-slide-tile-geometry-interactive-r005");
  assert.equal(manifest.stages[6].status, "approved");
  assert.equal(manifest.stages[7].status, "approved");
  assert.equal(manifest.stages[8].status, "approved");
  assert.equal(manifest.stages[9].status, "approved");
  assert.equal(manifest.stages[10].status, "approved");
  assert.equal(manifest.stages[11].status, "approved");
  assert.equal(
    manifest.currentState.unityStatus,
    "build44-rotation-direction-fix-source-tested"
  );
  for (const id of gate06.artifactIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === id);
    assert.ok(asset, id);
    assert.equal(asset.provenance.mechanismEvidenceContractSha256, contractSha);
    assert.equal(asset.provenance.geometryDigest, geometryDigest);
    assert.equal(asset.provenance.geometryChanged, false);
    if (asset.path.includes("/evidence/06-geometry/rev-005/")) {
      assert.equal(sha256File(path.join(repoRoot, asset.path)), asset.sha256);
    }
  }
});

test("allows rotation only at sMax and closure only after alignment", () => {
  assert.equal(report.pass, true);
  assert.equal(report.contractSha256, contractSha);
  assert.equal(report.canonicalGeometryDigest, geometryDigest);
  assert.equal(report.denseValidation.legalSamples, 1362);
  assert.equal(report.denseValidation.blockedRotationAttempts, 4000);
  assert.equal(report.denseValidation.blockedSlideAttempts, 359);
  assert.equal(report.denseValidation.simultaneousVelocityViolations, 0);
  assert.equal(report.denseValidation.maxPivotVarianceMm, 0);
  assert.ok(report.denseValidation.maxTopResidualMm <= 5e-6);
  assert.equal(report.full360ClosureMatrixError <= 1e-9, true);
  assert.equal(report.checks.alignmentToleranceAllowsClosure, true);
  assert.equal(report.checks.noInvalidMidSlidePoseRendered, true);
  const prohibited = report.stateRecords.find((pose) => pose.id === "prohibited-mid-slide-rotation");
  assert.equal(prohibited.requestedAngleDeg, 36);
  assert.equal(prohibited.resolvedAngleDeg, 0);
  assert.equal(prohibited.renderedInvalidPose, false);
  const legalRotationStates = report.stateRecords.filter((pose) => pose.id.startsWith("max-open"));
  assert.equal(legalRotationStates.every((pose) => pose.slideMm === report.dimensions.maximumTravelMm), true);
});

test("preserves geometry quality containment and product visibility", () => {
  assert.equal(audit.pass, true);
  assert.deepEqual(report.dimensions.boundsMm, [31, 50, 12]);
  assert.equal(report.dimensions.bottomTopPlaneMaximumDeviationMm, 0);
  assert.equal(report.dimensions.axisBossProtrusionMm, 0.2);
  assert.deepEqual(report.productRendererWhitelist, ["BottomExterior", "MovingTopBody"]);
  assert.equal(report.denseValidation.minimumDiskCoverageMisses, 0);
  assert.equal(
    report.representativeActualMeshValidation.every((pose) =>
      Object.values(pose.surfaceIntersectionPairs).every((count) => count === 0)
      && pose.minimumDiskActualMeshCoverageMisses === 0
    ),
    true
  );
  assert.equal(Object.values(report.nonmanifoldEdges).every((count) => count === 0), true);
  assert.equal(Object.values(report.invalidPolygonNormals).every((count) => count === 0), true);
  assert.equal(report.checks.fourFiniteGrooves, true);
  assert.equal(report.checks.grooveWidthsAuthorized, true);
  assert.equal(report.checks.ballRangesAuthorized, true);
});

test("exports an interactive GLB with interlock metadata", () => {
  const { bytes, json } = readGlbJson("magnetic-slide-tile-geometry-r005-review.glb");
  assert.ok(bytes.length > 1_000_000);
  assert.equal(json.asset.version, "2.0");
  assert.equal(json.animations, undefined);
  const nodes = json.nodes || [];
  assert.equal(nodes.filter((node) => node.name === "FixedAxis").length, 1);
  assert.equal(nodes.filter((node) => node.name === "MinimumOverlapDisk").length, 1);
  const root = nodes.find((node) => node.name === "MagneticSlideTile_G06_R005");
  assert.ok(root);
  assert.equal(root.extras.mechanism_contract_sha256, contractSha);
  assert.match(root.extras.endpoint_interlock, /s=sMax/);
  assert.equal(root.extras.prohibited_pose, "mid-slide rotation");
});

test("updates the stable workbench and decision records", () => {
  const app = fs.readFileSync(path.join(repoRoot, "tools/model-provenance-explorer/app.js"), "utf8");
  const bible = fs.readFileSync(path.join(repoRoot, "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"), "utf8");
  const status = fs.readFileSync(path.join(repoRoot, "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"), "utf8");
  assert.match(app, /Gate 06 rev 5 · 端点互锁同源几何/);
  assert.match(bible, /FDB-SLD-060/);
  assert.match(bible, /可以，可以继续推进。/);
  assert.match(status, /Gate 06 rev 5 端点互锁同源几何/);
  assert.match(status, /视觉批准待确认，未推送手机/);
});
