#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 188) throw new Error(`Expected revision 188, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "09-environment");
if (stage.status !== "ready_for_review" || stage.environmentSpec?.revision !== 8) {
  throw new Error("Gate 09 rev 8 is not ready for browser evidence.");
}
const output = path.dirname(fileURLToPath(import.meta.url));
const reportPath = path.join(output, "browser-workspace-validation.json");
const report = JSON.parse(fs.readFileSync(reportPath, "utf8"));
if (!report.pass || report.runtimeExceptionCount || report.loadingFailureCount) {
  throw new Error("Gate 09 browser validation failed.");
}
const definitions = [
  ["magnetic-slide-tile-environment-browser-test-r008", "browser-test", path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate09.mjs"), "process"],
  ["magnetic-slide-tile-environment-browser-report-r008", "browser-report", reportPath, "validation"],
  ["magnetic-slide-tile-environment-workbench-preview-r008", "workbench-preview", report.screenshotPath, "analysis"],
  ["magnetic-slide-tile-environment-workbench-focused-r008", "workbench-preview", report.focusedScreenshotPath, "analysis"],
];
for (const [id, slot, absolute, role] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing browser artifact ${absolute}.`);
  manifest.assets.push({
    id,
    stageId: "09-environment",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Chrome DevTools Protocol",
      version: "headless Chrome with SwiftShader",
      recipe: "Gate 09 rev 8 desktop, mobile, modal, Neutral/Shipping GLB and real-render comparison validation",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: stage.environmentSpec.governingContractSha256,
      gate08SourceSha256: stage.environmentSpec.sourceLightingSha256,
      geometryDigest: stage.environmentSpec.geometryDigestAfter,
      materialDigest: stage.environmentSpec.materialDigestAfter,
      lightDigest: stage.environmentSpec.lightDigestAfter,
      cameraDigest: stage.environmentSpec.cameraDigestAfter,
      environmentSha256: stage.environmentSpec.environmentAsset.sha256,
      portabilityContractSha256: stage.environmentSpec.portabilityContractSha256,
      interactionMode: "environment-glb-orbit-zoom-neutral-shipping-exposure",
      runtimeExceptionCount: report.runtimeExceptionCount,
      loadingFailureCount: report.loadingFailureCount,
      unityUsed: false,
      deviceWork: false,
    },
    sourceAssetIds: [
      "magnetic-slide-tile-environment-lookdev-r008",
      "magnetic-slide-tile-environment-turntable-r008",
      "magnetic-slide-tile-environment-comparison-board-r008",
      "magnetic-slide-tile-environment-reflection-board-r008",
      "magnetic-slide-tile-environment-portable-board-r008",
      "magnetic-slide-tile-unity-portability-contract-r008",
    ],
    sourceClaimIds: [],
  });
}
stage.artifactIds.push(...definitions.map(([id]) => id));
stage.validations.push({
  id: "browser-interactive-environment-mobile-modal",
  status: "pass",
  evidence: "Desktop and 390 px mobile passed seven fixed tabs, 12 gates, GLB orbit/zoom, Neutral/Shipping and exposure persistence, 24-frame turntable playback, comparison modal close, reload and direct route with 0 runtime/loading failures.",
});
stage.environmentSpec.browserEvidence = {
  runtimeExceptionCount: report.runtimeExceptionCount,
  loadingFailureCount: report.loadingFailureCount,
  desktopWidthPx: 1440,
  mobileWidthPx: 390,
  environmentModes: report.viewer.environmentModes,
  persistedEnvironmentMode: report.viewer.persistedEnvironmentMode,
  persistedExposure: report.viewer.persistedExposure,
  persistedEnvironment: report.viewer.persistedEnvironment,
  turntablePlayback: report.turntable.duration >= 2.9,
  comparisonModalClose: report.comparisonModalClose,
};
const appAsset = manifest.assets.find((asset) => asset.id === "magnetic-slide-tile-environment-workbench-r008");
const appPath = path.join(repoRoot, appAsset.path);
appAsset.sha256 = sha256File(appPath);
appAsset.sizeBytes = fs.statSync(appPath).size;
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate09-browser-environment-validated",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: "09-environment",
  environmentRevision: 8,
  artifactIds: definitions.map(([id]) => id),
  interactiveViewerAssetId: "magnetic-slide-tile-environment-lookdev-r008",
  turntableAssetId: "magnetic-slide-tile-environment-turntable-r008",
  environmentModes: report.viewer.environmentModes,
  runtimeExceptionCount: 0,
  loadingFailureCount: 0,
  visualApprovalPending: true,
  unityImportApplied: false,
  deviceWork: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate09: saved.stages[8].status,
  browserPass: report.pass,
  artifactCount: saved.stages[8].artifactIds.length,
}, null, 2));

