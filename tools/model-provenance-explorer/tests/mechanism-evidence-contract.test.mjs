import assert from "node:assert/strict";
import fs from "node:fs";
import test from "node:test";
import {
  loadManifest,
  resolveRepoPath,
  sha256File,
  validateManifest
} from "../pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
const contractAsset = manifest.assets.find(
  (asset) => asset.id === stage.analysisSpec.contractAssetId
);
const contract = JSON.parse(fs.readFileSync(resolveRepoPath(contractAsset.path), "utf8"));
const schema = JSON.parse(fs.readFileSync(new URL("../mechanism-evidence-contract.schema.json", import.meta.url), "utf8"));
const constraints = new Map(contract.constraints.map((constraint) => [constraint.id, constraint]));

test("matches the evidence contract schema-required shape", () => {
  assert.equal(schema.properties.schemaVersion.const, 1);
  assert.equal(contract.schemaVersion, 1);
  assert.equal(contract.modelId, "magnetic-slide-tile");
  assert.equal(contract.gate, "02-analysis");
  assert.equal(contract.revision, 16);
  assert.ok(contract.constraints.length >= 15);
  assert.equal(contract.coverageMatrix.length, 18);
  assert.ok(contract.conclusions.length >= 5 && contract.conclusions.length <= 7);
  for (const constraint of contract.constraints) {
    for (const key of schema.properties.constraints.items.required) {
      assert.ok(Object.hasOwn(constraint, key), `${constraint.id} missing ${key}`);
    }
    assert.match(constraint.id, /^MEC-/);
    assert.ok(["user-authoritative", "user-authoritative-range", "video-measured", "inferred", "unknown"].includes(constraint.state));
  }
});

test("links every constraint and region to hashed repository sources", () => {
  const assets = new Map(manifest.assets.map((asset) => [asset.id, asset]));
  for (const constraint of contract.constraints) {
    assert.ok(constraint.sourceAssetIds.length > 0, constraint.id);
    for (const sourceAssetId of constraint.sourceAssetIds) {
      const asset = assets.get(sourceAssetId);
      assert.ok(asset, `${constraint.id} missing ${sourceAssetId}`);
      assert.equal(asset.exists, true, sourceAssetId);
      assert.match(asset.sha256, /^[a-f0-9]{64}$/i, sourceAssetId);
    }
    for (const region of constraint.regions) {
      assert.ok(constraint.sourceAssetIds.includes(region.assetId), `${constraint.id} region is not a linked source`);
      if (Object.hasOwn(region, "frameIndex")) {
        assert.ok(Number.isInteger(region.frameIndex) && region.frameIndex >= 0);
        assert.ok(Number.isFinite(region.ptsSeconds) && region.ptsSeconds >= 0);
        assert.equal(region.normalizedRect.length, 4);
      }
    }
  }
});

test("contains the required source-to-constraint mappings", () => {
  const hasSource = (id, source) => constraints.get(id).sourceAssetIds.includes(source);
  assert.equal(hasSource("MEC-SLIDE-DIRECTION-AND-CLOSED-STOP", "slider-intake-user-mechanism-video-6022"), true);
  assert.equal(hasSource("MEC-DETENTS", "slider-intake-user-mechanism-video-6023"), true);
  assert.equal(hasSource("MEC-COMPOUND-TRANSFORM", "slider-intake-user-mechanism-video-6024"), true);
  assert.equal(hasSource("MEC-RESISTANCE-SEMANTICS", "slider-intake-haloo-official-05"), true);
  assert.equal(hasSource("MEC-ROTATION-RANGE", "slider-intake-haloo-official-06"), true);
  assert.equal(hasSource("MEC-VISIBLE-HARDWARE", "slider-intake-haloo-official-07"), true);
  assert.equal(hasSource("MEC-SLIDE-DIRECTION-AND-CLOSED-STOP", "slider-intake-haloo-official-08"), true);
  assert.equal(constraints.get("MEC-BOTTOM-BASE-FIXED").value.exposedRails, false);
  assert.equal(constraints.get("MEC-BOTTOM-EXTERIOR-NO-RAILS").value.exposedRailCount, 0);
  assert.equal(constraints.get("MEC-AXIS-MODULE-FIXED").value.worldPosition, "constant");
  assert.equal(constraints.get("MEC-AXIS-MODULE-FIXED").value.independentSlidingDof, false);
  assert.equal(constraints.get("MEC-ROTATING-CARRIER").value.translation, false);
  assert.equal(constraints.get("MEC-TOP-UNDERSIDE-GROOVES").value.owner, "MovingTop underside");
  assert.equal(constraints.get("MEC-TOP-UNDERSIDE-GROOVES").value.finite, true);
  assert.equal(constraints.get("MEC-CARRIER-FOLLOWERS-BILATERAL").value.owner, "RotatingCarrier");
  assert.equal(constraints.get("MEC-TOP-CARRIER-LOCAL-TRANSLATION").value.transformOrder, "R_fixedAxis(theta)*T_local(s)");
  assert.equal(constraints.get("MEC-AXIS-COVERAGE-AT-MAX-TRAVEL").value.axisMustRemainInsideTopSilhouette, true);
  assert.equal(constraints.has("MEC-CLOSED-OVERLAP-HARD-STOP"), false);
  const finite = constraints.get("MEC-FINITE-GROOVE-ENDPOINT-STOPS").value;
  assert.equal(finite.grooveCount, 4);
  assert.equal(finite.followerCount, 2);
  assert.equal(finite.grooveEndNormalizedFromTopL - finite.grooveStartNormalizedFromTopL, finite.sMaxDerived);
  assert.equal(finite.maximumOpenEndpoint.followerEngaged, true);
  assert.equal(finite.maximumOpenEndpoint.fixedAxisCovered, true);
  assert.equal(finite.maximumOpenEndpoint.physicalMinimumCoverMarginL, "unknown");
  const sweep = constraints.get("MEC-TOP-ABOVE-BOTTOM-SWEPT-ENVELOPE");
  assert.equal(sweep, undefined);
  const disk = constraints.get("MEC-MINIMUM-OVERLAP-DISK").value;
  assert.equal(disk.owner, "BottomBase");
  assert.equal(disk.center, "FixedAxis");
  assert.equal(disk.physicalRadiusMm, "unknown");
  const dualBound = constraints.get("MEC-ACTUAL-TRAVEL-DUAL-BOUND").value;
  assert.equal(dualBound.actualSMaxL, Math.min(dualBound.grooveEndpointLimitL, dualBound.overlapContainmentLimitL));
  assert.equal(dualBound.angleInvariant, true);
  assert.equal(dualBound.activeLimit, "MinimumOverlapDisk");
  assert.equal(constraints.get("MEC-CONTINUOUS-OVERLAP-CONTAINMENT").value.angleSamples, 360);
  assert.equal(hasSource("MEC-BOTTOM-BASE-FIXED", "slider-analysis-user-selected-bottom-base-close-r011"), true);
  assert.equal(hasSource("MEC-AXIS-MODULE-FIXED", "slider-analysis-user-selected-bottom-base-context-r011"), true);
  assert.equal(hasSource("MEC-ROTATING-CARRIER", "slider-intake-haloo-official-07"), true);
  assert.equal(hasSource("MEC-TOP-UNDERSIDE-GROOVES", "slider-intake-nxedc-ref-03"), true);
  assert.equal(hasSource("MEC-CARRIER-FOLLOWERS-BILATERAL", "slider-intake-nxedc-ref-04"), true);
});

test("archives both user-selected bottom-base images immutably", () => {
  const expected = new Map([
    ["slider-analysis-user-selected-bottom-base-close-r011", "49d68c8ecfc52f3dce1cd74fe0e9ffc9483fe33929f73bb9b843f344b69a0b91"],
    ["slider-analysis-user-selected-bottom-base-context-r011", "5b2f438cc748bba43ccb61a7eec5618f3632198455965bef63cce241ed67ec03"]
  ]);
  for (const [id, hash] of expected) {
    const asset = manifest.assets.find((candidate) => candidate.id === id);
    assert.equal(asset.role, "user-input");
    assert.equal(asset.provenance.origin, "user-provided");
    assert.equal(asset.sha256, hash);
    assert.equal(sha256File(resolveRepoPath(asset.path)), hash);
    assert.ok(contract.sourceInventory.assetIds.includes(id));
  }
});

test("archives the user-authoritative finite-groove correction", () => {
  const asset = manifest.assets.find((item) => item.id === "slider-analysis-finite-groove-user-correction-r014");
  assert.ok(asset);
  assert.equal(asset.role, "user-input");
  assert.equal(sha256File(resolveRepoPath(asset.path)), asset.sha256);
  assert.ok(constraints.get("MEC-FINITE-GROOVE-ENDPOINT-STOPS").sourceAssetIds.includes(asset.id));
  assert.ok(constraints.get("MEC-ACTUAL-TRAVEL-DUAL-BOUND").sourceAssetIds.includes(asset.id));
});

test("archives the user screenshot and minimum-overlap interpretation immutably", () => {
  const screenshot = manifest.assets.find((item) => item.id === "slider-analysis-minimum-overlap-disk-user-screenshot-r015");
  const correction = manifest.assets.find((item) => item.id === "slider-analysis-minimum-overlap-disk-user-correction-r015");
  assert.equal(screenshot.role, "user-input");
  assert.equal(correction.role, "user-input");
  assert.equal(sha256File(resolveRepoPath(screenshot.path)), screenshot.sha256);
  assert.equal(sha256File(resolveRepoPath(correction.path)), correction.sha256);
  assert.ok(constraints.get("MEC-MINIMUM-OVERLAP-DISK").sourceAssetIds.includes(screenshot.id));
  assert.ok(constraints.get("MEC-ACTUAL-TRAVEL-DUAL-BOUND").sourceAssetIds.includes(correction.id));
});

test("covers every Gate 01 asset and preserves source boundaries", () => {
  const gate01Ids = manifest.assets.filter((asset) => asset.stageId === "01-intake").map((asset) => asset.id);
  assert.deepEqual([...contract.sourceInventory.groups.allGate01Intake].sort(), [...gate01Ids].sort());
  assert.equal(contract.sourceInventory.counts.img5961DerivedFrames, 12);
  assert.equal(contract.sourceInventory.counts.obsidianFrames, 10);
  assert.equal(contract.sourceInventory.counts.nxedcImages, 6);
  assert.equal(contract.sourceInventory.counts.halooOfficialImages, 8);
  assert.equal(contract.sourceInventory.counts.silverSameModelVideos, 3);
  assert.match(contract.sourceInventory.boundaries.chromeHearts, /never mechanism evidence/);
});

test("binds CAD to the contract and keeps Simulator separate", () => {
  const actualHash = sha256File(resolveRepoPath(contractAsset.path));
  assert.equal(stage.analysisSpec.contractSha256, actualHash);
  assert.equal(contractAsset.sha256, actualHash);
  assert.equal(stage.analysisSpec.cadGeneration.locked, false);
  assert.equal(stage.analysisSpec.cadGeneration.scope, "web-kinematic-cad-only-no-simulator-blender-unity");
  assert.equal(stage.analysisSpec.approvalSpec.interactiveRequired, true);
  assert.equal(stage.analysisSpec.approvalSpec.approvalType, "interactive-cad-geometry");
  assert.equal(stage.analysisSpec.approvalSpec.chatTextApprovalAllowed, false);
  assert.equal(stage.analysisSpec.cadGeneration.duplicateDefaultsForbidden, true);
  assert.equal(stage.analysisSpec.simulatorGeneration.locked, true);
  assert.equal(stage.analysisSpec.simulatorGeneration.activeControls, 0);
  assert.equal(stage.analysisSpec.simulatorArtifactId, null);
  assert.equal(stage.analysisSpec.recordingAssetId, null);
  assert.equal(contract.downstreamPolicy.contractHashRequired, true);
  assert.equal(contract.downstreamPolicy.gate02ApprovalRequired, true);
  assert.equal(contract.downstreamPolicy.duplicateDefaultsForbidden, true);
});

test("keeps the stable 12-gate status contract", () => {
  assert.equal(manifest.stages.length, 12);
  assert.equal(manifest.currentStageId, "05-blockout");
  assert.equal(manifest.stages[0].status, "approved");
  assert.equal(stage.status, "approved");
  assert.equal(manifest.stages[2].status, "approved");
  assert.equal(manifest.stages[3].status, "approved");
  assert.equal(manifest.stages[4].status, "ready_for_review");
  for (const downstream of manifest.stages.slice(5, 11)) assert.equal(downstream.status, "stale");
  assert.equal(manifest.stages[11].status, "rejected");
  assert.deepEqual(validateManifest(manifest), []);
});

test("rejects active downstream artifacts without the contract hash", () => {
  const candidate = structuredClone(manifest);
  const gate03 = candidate.stages.find((stage) => stage.id === "03-contract");
  gate03.status = "draft";
  const activeAsset = candidate.assets.find((asset) => asset.id === gate03.artifactIds[0]);
  delete activeAsset.provenance.mechanismEvidenceContractSha256;
  const missingHashErrors = validateManifest(candidate);
  assert.ok(missingHashErrors.some((error) => /must carry the approved mechanism evidence contract SHA-256/.test(error)));
  const expectedHash = candidate.stages.find((stage) => stage.id === "02-analysis").analysisSpec.contractSha256;
  for (const asset of candidate.assets.filter((asset) => asset.stageId === "03-contract")) {
    asset.provenance.mechanismEvidenceContractSha256 = expectedHash;
  }
  assert.ok(!validateManifest(candidate).some((error) => /mechanism evidence contract SHA-256/.test(error)));
});
