import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { loadManifest, repoRoot, sha256File } from "../pipeline-core.mjs";

const modelRoot = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile"
);
const readJson = (relative) => JSON.parse(fs.readFileSync(path.join(modelRoot, relative), "utf8"));

test("uses explicit provisional dimensions without production claims", () => {
  const contract = readJson("evidence/03-contract/rev-009/provisional-modeling-contract.json");
  assert.equal(contract.statusBoundary.userAuthorizedProvisional, true);
  assert.equal(contract.statusBoundary.productionMeasured, false);
  assert.equal(contract.dimensions.closedOverallLength.value, 50);
  assert.equal(contract.dimensions.overallWidth.value, 31);
  assert.equal(contract.dimensions.totalClosedThickness.value, 12);
  assert.equal(contract.dimensions.topPlateThickness.value, 5.875);
  assert.equal(contract.dimensions.bottomPlateThickness.value, 5.875);
  assert.equal(contract.dimensions.closedSeamGap.value, 0.25);
  assert.equal(contract.dimensions.fixedAxisOffsetFromNearestEnd.value, 16);
  assert.equal(contract.dimensions.rotatingCarrierDiameter.value, 23);
  assert.ok(Math.abs(contract.dimensions.maximumSlideTravel.value - 18.076433121019107) < 1e-12);
  assert.equal(JSON.stringify(contract).includes('"value": 21'), false);
  assert.ok(contract.unknownEngineeringDimensions.includes("manufacturing tolerance"));
});

test("migrates only the approved CAD hierarchy", () => {
  const architecture = readJson("evidence/04-architecture/rev-011/approved-cad-architecture.json");
  assert.equal(architecture.governingContractSha256, "b4318452f163ef7c105c826d4466a739a1dd0d942d4d74d921c29c39e02a84f2");
  assert.deepEqual(
    architecture.hierarchy.map((item) => item.id),
    [
      "BottomExterior", "FixedAxis", "MinimumOverlapDisk", "RotatingCarrier",
      "CarrierFollowerLeft", "CarrierFollowerRight", "TopPlate",
      "TopGrooveLeft", "TopGrooveRight", "UnknownContacts"
    ]
  );
  assert.equal(architecture.kinematics.top, "R_fixedAxis(theta) * T_local(s)");
  assert.equal(architecture.kinematics.simultaneousSlideRotation, true);
  assert.equal(architecture.kinematics.selfMotion, false);
  assert.equal(architecture.hierarchy.find((item) => item.id === "UnknownContacts").render, false);
});

test("records reuse lineage and excludes stale geometry", () => {
  const reuse = readJson("evidence/03-contract/rev-009/reuse-plan.json");
  assert.equal(reuse.reusedAssets.length, 9);
  assert.ok(reuse.reusedAssets.every((asset) => asset.sha256 && asset.path));
  assert.ok(reuse.staleNotReused.some((item) => item.gate === "05-blockout"));
  assert.ok(reuse.staleNotReused.some((item) => item.gate === "11-unity-parity"));
});

test("passes Gate 05 geometry and motion invariants", () => {
  const report = readJson("evidence/05-blockout/rev-004/blockout-validation.json");
  assert.equal(report.pass, true);
  assert.equal(report.checks.contractHashConsumed, true);
  assert.equal(report.checks.axisInvariant, true);
  assert.equal(report.checks.topAlwaysAboveBottom, true);
  assert.equal(report.checks.minimumOverlapDenseSweep, true);
  assert.equal(report.checks.noRenderableUnknownProxy, true);
  assert.equal(report.checks.zeroAnimationAndSelfMotion, true);
  assert.equal(report.denseSweep.sampleCount, 1800);
  assert.equal(report.denseSweep.allValid, true);
  assert.ok(report.overlapScaleReconciliation.maxTravelLongitudinalMarginMm > 0.42);
  assert.ok(Object.values(report.meshAudit).every((mesh) => mesh.nonmanifoldEdges === 0 && mesh.signedVolumeMm3 > 0));
});

test("preserves rejected Gate 05 rev 4 evidence after Gate 05 reopens", () => {
  const manifest = loadManifest("magnetic-slide-tile");
  const gate05 = manifest.stages.find((stage) => stage.id === "05-blockout");
  assert.equal(gate05.status, "approved");
  assert.equal(manifest.currentStageId, "12-shipping");
  assert.equal(manifest.stages[2].status, "approved");
  assert.equal(manifest.stages[3].status, "approved");
  assert.equal(manifest.stages[5].status, "approved");
  assert.equal(manifest.stages[6].status, "approved");
  assert.equal(manifest.stages[7].status, "approved");
  assert.equal(manifest.stages[8].status, "approved");
  assert.equal(manifest.stages[9].status, "approved");
  assert.equal(manifest.stages[10].status, "approved");
  assert.equal(manifest.stages[11].status, "approved");
  assert.equal(gate05.reviewArtifactIds[0], "magnetic-slide-g05-r012-endpoint-interlock-video");
  const rejectedIds = [
    "magnetic-slide-tile-blockout-interactive-r004",
    "magnetic-slide-tile-blockout-blend-r004",
    "magnetic-slide-tile-blockout-validation-r004"
  ];
  for (const id of rejectedIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === id);
    assert.ok(asset);
    const absolute = path.join(repoRoot, asset.path);
    assert.equal(fs.existsSync(absolute), true);
    assert.equal(sha256File(absolute), asset.sha256);
  }
});
