import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";
import { loadManifest, repoRoot, sha256File } from "../pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const gate = path.resolve(here, "../../../unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/09-environment/rev-008");
const read = (filename) => JSON.parse(fs.readFileSync(path.join(gate, filename), "utf8"));

test("Gate 08 rev 2 exact chat approval and final goal are persisted", () => {
  const manifest = loadManifest("magnetic-slide-tile");
  const gate08 = manifest.stages.find((stage) => stage.id === "08-lighting");
  const gate09 = manifest.stages.find((stage) => stage.id === "09-environment");
  const gate08Rev2 = gate08.historicalRevisions.find(
    (revision) => revision.evidenceRevision === 2,
  );
  assert.equal(gate08.status, "approved");
  assert.equal(gate08Rev2.decision.notes, "进行下一步吧");
  assert.equal(gate08Rev2.decision.finalGoal, "transfer to Unity with no avoidable loss and run on iPhone");
  assert.equal(manifest.currentState.finalDeliveryGoal.exactUserGoal, "transfer to Unity with no avoidable loss and run on iPhone");
  assert.equal(gate09.revision, 9);
  assert.equal(gate09.status, "approved");
  assert.ok(gate09.historicalRevisions.some((revision) => revision.evidenceRevision === 8));
  assert.equal(manifest.currentStageId, "12-shipping");
  assert.equal(manifest.stages[9].status, "approved");
  assert.equal(manifest.stages[10].status, "approved");
  assert.equal(manifest.stages[11].status, "approved");
});

test("Gate 09 preserves approved model, material, light and source cameras", () => {
  const report = read("environment-validation.json");
  assert.equal(report.pass, true);
  assert.equal(report.geometry.before, report.geometry.after);
  assert.equal(report.geometry.after, "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe");
  assert.equal(report.uv.before, report.uv.after);
  assert.equal(report.materials.sceneFingerprintBefore, report.materials.sceneFingerprintAfter);
  assert.equal(report.materials.approvedSemanticDigest, "366b788bfb329d806ffbffaa3ff9c4789deab3967943fa43dc7f42c9b6609aa8");
  assert.equal(report.lighting.before, report.lighting.after);
  assert.equal(report.cameras.before, report.cameras.after);
  assert.deepEqual(report.hierarchy.before, report.hierarchy.after);
  assert.equal(report.motionContainment.denseSweepSamples, 3600);
  assert.equal(report.motionContainment.allValid, true);
  assert.equal(report.animatedObjects.length, 0);
});

test("portable EXR is seamless, linear, dynamic and hash-locked", () => {
  const metadata = read("portable-hdri-metadata.json");
  const blender = read("blender-environment-audit.json");
  assert.deepEqual(metadata.resolutionPx, [2048, 1024]);
  assert.equal(metadata.projection, "equirectangular");
  assert.equal(metadata.transfer, "linear");
  assert.equal(metadata.colorPrimaries, "Rec.709");
  assert.equal(metadata.whitePoint, "D65");
  assert.ok(metadata.seamMaxAbsoluteLinearDelta <= 1e-6);
  assert.ok(metadata.dynamicRangeStopsP01ToP99 >= 4);
  assert.equal(sha256File(path.join(gate, metadata.asset)), metadata.sha256);
  assert.equal(blender.pass, true);
  assert.equal(blender.hdri.colorspace, "Non-Color");
  assert.deepEqual(blender.worldNodeTypes.sort(), ["BACKGROUND", "OUTPUT_WORLD", "TEX_ENVIRONMENT"].sort());
  assert.deepEqual(blender.proceduralWorldNodes, []);
});

test("matched environment renders preserve readability without clipping", () => {
  const report = read("image-environment-audit.json");
  assert.equal(report.pass, true);
  assert.equal(report.checks.matchedPairDimensions, true);
  assert.equal(report.checks.environmentDifferenceVisible, true);
  assert.equal(report.checks.bloodRedHue, true);
  assert.equal(report.checks.crystalVariation, true);
  assert.equal(report.checks.motifContrast, true);
  assert.equal(report.checks.silverNeutral, true);
  assert.equal(report.checks.noClipping, true);
  assert.equal(report.checks.mechanicalReadable, true);
  assert.ok(report.aggregate.maximumClippedFraction <= 0.001);
  assert.ok(report.matchedPairs.reflectionCloseup.changedPixelFractionOver2 > 0.005);
});

test("Unity portability contract defines exact and measured parity boundaries", () => {
  const contract = read("unity-portability-contract.json");
  const validation = read("portability-validation.json");
  assert.equal(validation.pass, true);
  assert.equal(validation.allAssetHashesVerified, true);
  assert.match(contract.losslessDefinition.notPossible, /cannot transfer one-to-one/);
  assert.equal(contract.geometry.digest, "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe");
  assert.equal(contract.artworkAndTextures.upperAndLowerIndependentlyReplaceable, true);
  assert.notEqual(contract.artworkAndTextures.upperMask.sha256, contract.artworkAndTextures.lowerMask.sha256);
  assert.match(contract.pbrBakeAndPackingPlan.perArtworkLayer.MaskMap, /R metallic, G ambient occlusion/);
  assert.equal(contract.unityUrpShaderTargets.emission, 0);
  assert.equal(contract.environmentAndReflections.environment.sha256, "7f1c9fded84c453efbc5300a6a71fe2948534055d3f4ae5052696909f30be6ab");
  assert.equal(contract.colorManagement.unityStartingPoint.toneMapper, "ACES");
  assert.equal(contract.acceptanceTolerances.closedBoundsMaxAbsoluteErrorMm, 0.001);
  assert.equal(contract.acceptanceTolerances.uvMaxAbsoluteCoordinateError, 1e-6);
  assert.equal(contract.acceptanceTolerances.reflectionContinuity.hdriSeamMaxAbsoluteLinearDelta, 1e-6);
  assert.equal(contract.deferred.unityImportSettingsApplied, false);
  assert.equal(contract.deferred.iphoneRun, false);
});

test("portable texture bytes retain approved Gate 07 hashes", () => {
  const report = read("portable-texture-extraction.json");
  assert.equal(report.pass, true);
  for (const item of Object.values(report.textures)) {
    assert.equal(item.packedBytePreservation, true);
    assert.equal(sha256File(path.join(gate, item.path)), item.sha256);
  }
  assert.equal(report.textures["upper-albedo.png"].sha256, "c0e9305d475cd2c591efc8a833a0aafb1aef4ccc437d84a3417674e6d1b453a5");
  assert.equal(report.textures["lower-albedo.png"].sha256, "968c1e87ca2d5ea7c8fc57106e42bcd09dc95395fac7dd3be569e580ea8850eb");
});

test("workbench exposes Gate 09 and conditional Neutral/Shipping lookdev", () => {
  const app = fs.readFileSync(path.join(repoRoot, "tools/model-provenance-explorer/app.js"), "utf8");
  assert.match(app, /Gate 09 rev 8 · 可移植 Shipping 环境/);
  assert.match(app, /asset\.id === "magnetic-slide-tile-environment-lookdev-r008"/);
  assert.match(app, /<option value="neutral">中性<\/option><option value="shipping">Shipping<\/option>/);
  assert.match(app, /几何／层级／轴心／UV／图案 mask 必须精确/);
  assert.match(app, /iPhone 验收在 Gate 12 视觉批准之后/);
});

test("design authority and delivery status record Gate 09 truthfully", () => {
  const bible = fs.readFileSync(path.join(repoRoot, "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"), "utf8");
  const status = fs.readFileSync(path.join(repoRoot, "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"), "utf8");
  assert.match(bible, /FDB-SLD-048.*“进行下一步吧”.*Approved/s);
  assert.match(bible, /FDB-SLD-049.*transfer to Unity with no avoidable loss and run on iPhone/s);
  assert.match(bible, /FDB-SLD-049.*Approved · Locked by Latest Chat Authority/s);
  assert.match(status, /Magnetic Slide Tile Gate 09 rev 8 环境与 Unity 可移植合同/);
  assert.match(status, /视觉批准待确认，未推送手机/);
  assert.match(status, /没有 Unity 导入设置、Build、安装或 iPhone 运行/);
});

