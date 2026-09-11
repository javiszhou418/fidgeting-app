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
if (manifest.revision !== 183) throw new Error(`Expected revision 183, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "08-lighting");
if (stage.status !== "ready_for_review" || stage.lightingSpec?.revision !== 2) {
  throw new Error("Gate 08 rev 2 is not ready for browser evidence.");
}
const output = path.dirname(fileURLToPath(import.meta.url));
const reportPath = path.join(output, "browser-workspace-validation.json");
const report = JSON.parse(fs.readFileSync(reportPath, "utf8"));
if (!report.pass || report.runtimeExceptionCount || report.loadingFailureCount) {
  throw new Error("Gate 08 browser validation failed.");
}
const definitions = [
  ["magnetic-slide-tile-lighting-browser-test-r002", "browser-test", path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate08.mjs"), "process"],
  ["magnetic-slide-tile-lighting-browser-report-r002", "browser-report", reportPath, "validation"],
  ["magnetic-slide-tile-lighting-workbench-preview-r002", "workbench-preview", report.screenshotPath, "analysis"],
  ["magnetic-slide-tile-lighting-workbench-focused-r002", "workbench-preview", report.focusedScreenshotPath, "analysis"],
];
for (const [id, slot, absolute, role] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing browser artifact ${absolute}.`);
  manifest.assets.push({
    id,
    stageId: "08-lighting",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Chrome DevTools Protocol",
      version: "headless Chrome with SwiftShader",
      recipe: "Gate 08 rev 2 desktop, mobile, modal, three-mode GLB and turntable validation",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: stage.lightingSpec.governingContractSha256,
      gate07SourceSha256: stage.lightingSpec.sourceMaterialSha256,
      geometryDigest: stage.lightingSpec.geometryDigestAfter,
      materialDigest: stage.lightingSpec.materialDigestAfter,
      interactionMode: "lighting-glb-orbit-zoom-neutral-studio-daylight-environment-exposure",
      runtimeExceptionCount: report.runtimeExceptionCount,
      loadingFailureCount: report.loadingFailureCount,
      unityUsed: false,
      deviceWork: false,
    },
    sourceAssetIds: [
      "magnetic-slide-tile-lighting-lookdev-r002",
      "magnetic-slide-tile-lighting-turntable-r002",
      "magnetic-slide-tile-lighting-mode-comparison-r002",
      "magnetic-slide-tile-lighting-pass-board-r002",
      "magnetic-slide-tile-lighting-mechanical-board-r002",
    ],
    sourceClaimIds: [],
  });
}
stage.artifactIds.push(...definitions.map(([id]) => id));
stage.validations.push({
  id: "browser-interactive-lighting-mobile-modal",
  status: "pass",
  evidence: "Desktop and 390 px mobile passed seven fixed tabs, 12 gates, GLB orbit/zoom, Neutral/Studio/Daylight and exposure persistence, turntable, comparison modal/Escape, reload and direct routes with 0 runtime/loading failures."
});
stage.lightingSpec.browserEvidence = {
  runtimeExceptionCount: report.runtimeExceptionCount,
  loadingFailureCount: report.loadingFailureCount,
  desktopWidthPx: 1440,
  mobileWidthPx: 390,
  lightingModes: report.viewer.lightingModes,
  persistedLightingMode: report.viewer.persistedLightingMode,
  persistedExposure: report.viewer.persistedExposure,
  persistedEnvironment: report.viewer.persistedEnvironment,
  turntablePlayback: report.turntablePlayback,
  comparisonModalEscape: report.comparisonModalEscape,
};
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate08-browser-lighting-validated",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: "08-lighting",
  lightingRevision: 2,
  artifactIds: definitions.map(([id]) => id),
  interactiveViewerAssetId: "magnetic-slide-tile-lighting-lookdev-r002",
  turntableAssetId: "magnetic-slide-tile-lighting-turntable-r002",
  lightingModes: report.viewer.lightingModes,
  runtimeExceptionCount: 0,
  loadingFailureCount: 0,
  visualApprovalPending: true,
  deviceWork: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate08: saved.stages[7].status,
  browserPass: report.pass,
  artifactCount: saved.stages[7].artifactIds.length,
}, null, 2));

