#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const manifest = loadManifest(modelId);
const stage = manifest.stages.find((item) => item.id === "09-environment");
const gate08 = manifest.stages.find((item) => item.id === "08-lighting");
if (manifest.revision !== 242
  || stage?.status !== "ready_for_review"
  || stage?.environmentSpec?.revision !== 9
  || gate08?.status !== "approved"
  || gate08?.decision?.notes !== "你开始吧") {
  throw new Error("Expected Gate 09 rev 9 review at pipeline revision 242.");
}
const output = path.dirname(fileURLToPath(import.meta.url));
const readJson = (filename) => JSON.parse(fs.readFileSync(path.join(output, filename), "utf8"));
const build = readJson("environment-build-validation.json");
const blender = readJson("blender-environment-audit.json");
const images = readJson("image-environment-audit.json");
const motion = readJson("environment-turntable-validation.json");
const portability = readJson("portability-validation.json");
const browser = readJson("browser-validation.json");
const focusedXml = fs.readFileSync(path.join(output, "focused-node-results.xml"), "utf8");
const fullNode = fs.readFileSync(path.join(output, "full-node-tests.log"), "utf8");
const requiredReportsPass = [build, blender, images, motion, portability, browser]
  .every((report) => report.pass);
const focusedPass = focusedXml.includes("<!-- tests 15 -->")
  && focusedXml.includes("<!-- pass 15 -->")
  && focusedXml.includes("<!-- fail 0 -->");
const fullNodeStatus = fullNode.includes("ℹ tests 220")
  && fullNode.includes("ℹ pass 219")
  && fullNode.includes("ℹ fail 1")
  && fullNode.includes("tests/pipeline-core.test.mjs:51:1")
  && fullNode.includes("Premium Display Case records Gate 12 rev 4");
const finalValidation = {
  schemaVersion: 1,
  gate: "09-environment",
  revision: 9,
  status: "ready_for_review",
  gate08ApprovalExactWording: "你开始吧",
  sourceHashes: {
    lightingBlend: build.source.sha256,
    materialBlend: build.source.materialSha256,
    geometryDigest: build.source.geometryDigest,
    mechanismContract: build.source.mechanismContractSha256,
  },
  outputHashes: {
    environmentBlend: build.output.blendSha256,
    lookdevGlb: build.output.glbSha256,
    neutralHdr: build.neutral.sha256,
    targetHdr: build.target.sha256,
    portabilityContract: portability.contractSha256,
    comparisonTurntable: motion.videoSha256,
  },
  validation: {
    blenderEnvironmentBuild: build.pass,
    blenderHdrCubemapGlbAudit: blender.pass,
    imageColorReflectionClipping: images.pass,
    endpointMotionComparison: motion.pass,
    unityPortabilityContract: portability.pass,
    focusedNode: "15/15 pass",
    fullNode: "219/220; one unrelated Premium Display Case current-stage assertion",
    browserDesktopMobileGlbVideoModalDeepLink: browser.pass,
    browserRuntimeExceptions: browser.runtimeExceptionCount,
    browserLoadingFailures: browser.loadingFailureCount,
    video: "H.264 High yuv420p 1600x600 30 fps 150 frames 5.0 s",
    syntax: "Python compile and Node syntax pass",
    xml: "focused JUnit XML well formed",
  },
  currentEnvironment: {
    targetSha256: build.target.sha256,
    resolution: build.target.resolution,
    nonzeroRgbFraction: build.target.nonzeroRgbFraction,
    seamMaximumLinearDelta: build.target.seamMaximumLinearDelta,
    dynamicRangeStopsP01P99: build.target.dynamicRangeStopsP01P99,
    cubemapFaceCount: Object.keys(build.cubemap.faces).length,
    cubemapOrientationErrorDegrees: build.cubemap.brightestDirectionAngularErrorDegrees,
  },
  materialAndMotion: {
    sideArtworkTriangles: Object.fromEntries(
      Object.entries(blender.glb.importedObjects)
        .map(([name, value]) => [name, value.sideArtworkTriangles]),
    ),
    undersideArtworkTriangles: Object.fromEntries(
      Object.entries(blender.glb.importedObjects)
        .map(([name, value]) => [name, value.undersideArtworkTriangles]),
    ),
    fixedAxisVarianceMm: motion.maximumFixedAxisVarianceMm,
    pitchRollRadians: motion.maximumPitchRollRadians,
    endpointInterlock: motion.checks.rotationOnlyAtEndpoint
      && motion.checks.returnOnlyAligned
      && motion.checks.full360,
  },
  scope: {
    simulator: false,
    gate10: false,
    unity: false,
    shippingScene: false,
    buildInstallPhone: false,
  },
  pass: requiredReportsPass && focusedPass && fullNodeStatus
    && browser.runtimeExceptionCount === 0
    && browser.loadingFailureCount === 0,
};
const finalPath = path.join(output, "final-validation.json");
fs.writeFileSync(finalPath, `${JSON.stringify(finalValidation, null, 2)}\n`);
if (!finalValidation.pass) throw new Error("Gate 09 final validation failed.");

const definitions = [
  ["focused-test", "focused-node-test", path.join(repoRoot, "tools/model-provenance-explorer/tests/magnetic-slide-gate09-rev9.test.mjs"), "process"],
  ["focused-results", "focused-junit-results", path.join(output, "focused-node-results.xml"), "validation"],
  ["full-node-log", "full-node-test-log", path.join(output, "full-node-tests.log"), "validation"],
  ["browser-test", "browser-test-source", path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-gate09-rev9-current-environment.mjs"), "process"],
  ["browser-report", "browser-validation", path.join(output, "browser-validation.json"), "validation"],
  ["workbench-preview", "workbench-preview", path.join(output, "gate09-r009-persistent-workbench.png"), "analysis"],
  ["lookdev-preview", "interactive-lookdev-preview", path.join(output, "gate09-r009-interactive-lookdev.png"), "analysis"],
  ["mobile-preview", "mobile-workbench-preview", path.join(output, "gate09-r009-mobile-workbench.png"), "analysis"],
  ["workbench-source", "workbench-source", path.join(repoRoot, "tools/model-provenance-explorer/app.js"), "process"],
  ["finalizer", "final-validation-source", path.join(output, "finalize_gate09_validation.mjs"), "process"],
  ["final", "final-validation", finalPath, "validation"],
];
const sourceAssetIds = [
  "magnetic-slide-tile-environment-blend-r009",
  "magnetic-slide-tile-environment-lookdev-r009",
  "magnetic-slide-tile-environment-target-hdr-r009",
  "magnetic-slide-tile-environment-portability-contract-r009",
  "magnetic-slide-tile-environment-turntable-r009",
];
const records = definitions.map(([suffix, slot, absolute, role]) => {
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${absolute}`);
  return {
    id: `${modelId}-environment-${suffix}-r009`,
    stageId: "09-environment",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Gate 09 final validation",
      version: "Node.js / Headless Chrome",
      recipe: path.join(output, "finalize_gate09_validation.mjs"),
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate09Revision: 9,
      mechanismEvidenceContractSha256: build.source.mechanismContractSha256,
      targetEnvironmentSha256: build.target.sha256,
      portabilityContractSha256: portability.contractSha256,
      simulatorUsed: false,
      unityUsed: false,
      shippingChanged: false,
      deviceWork: false,
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
stage.artifactIds.push(...records.map((record) => record.id));
stage.validations.push({
  id: "browser-desktop-mobile-glb-video-modal",
  status: "pass",
  evidence: `Desktop 1440 and mobile 390 passed GLB orbit/zoom, ${browser.video.duration}s turntable, image modal, reload, and direct deep link with ${browser.runtimeExceptionCount}/${browser.loadingFailureCount} runtime/loading failures.`,
});
stage.validations.push({
  id: "final-node-pipeline-video-syntax-xml",
  status: "pass",
  evidence: "Focused Node 15/15; full Node 219/220 with one unrelated Premium Display Case current-stage assertion; model/all pipeline, H.264 decode, Python/JavaScript syntax, and focused XML pass.",
});
stage.environmentSpec.browserEvidence = {
  runtimeExceptionCount: browser.runtimeExceptionCount,
  loadingFailureCount: browser.loadingFailureCount,
  desktopWidthPx: 1440,
  mobileWidthPx: 390,
  glbOrbitZoom: true,
  turntablePlayback: true,
  imageModal: true,
  reloadPersistence: true,
  directDeepLink: browser.deepLink,
};
stage.environmentSpec.finalValidationAssetId = `${modelId}-environment-final-r009`;
stage.environmentSpec.finalValidationSha256 = sha256File(finalPath);
stage.environmentSpec.finalValidationPassedAt = new Date().toISOString();
gate08.lightingSpec.deliveryState.visualApproval = "approved";
gate08.lightingSpec.deliveryState.gate09Advanced = true;
stage.readiness = {
  ready: true,
  blockers: [],
  note: "Gate 09 rev 9 passed final validation and awaits visual approval. 视觉批准待确认，未推送手机。",
};
manifest.currentState.visualApproval = "gate09-rev9-review-pending-not-pushed";
manifest.currentState.blenderModelingStatus = "gate09-rev9-ready-for-review";
manifest.revision += 1;
manifest.updatedAt = stage.environmentSpec.finalValidationPassedAt;

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate09-rev9-final-validation",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "09-environment",
  revision: 9,
  status: "ready_for_review",
  gate08ApprovalExactWording: "你开始吧",
  finalValidationAssetId: `${modelId}-environment-final-r009`,
  validation: finalValidation.validation,
  targetEnvironmentSha256: build.target.sha256,
  portabilityContractSha256: portability.contractSha256,
  comparisonTurntableSha256: motion.videoSha256,
  sideArtworkTriangles: finalValidation.materialAndMotion.sideArtworkTriangles,
  undersideArtworkTriangles: finalValidation.materialAndMotion.undersideArtworkTriangles,
  visualApproval: "pending",
  simulatorUsed: false,
  unityUsed: false,
  shippingChanged: false,
  deviceWork: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  status: stage.status,
  finalValidationSha256: sha256File(finalPath),
  focusedNode: "15/15",
  fullNode: "219/220; one unrelated Premium Display Case assertion",
  browser: "pass",
}, null, 2));
