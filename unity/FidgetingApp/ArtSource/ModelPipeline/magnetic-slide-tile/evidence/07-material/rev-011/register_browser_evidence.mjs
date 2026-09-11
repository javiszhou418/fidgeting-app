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
if (manifest.revision !== 179) throw new Error(`Expected revision 179, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "07-material");
if (stage.status !== "ready_for_review" || stage.materialSpec?.revision !== 11) {
  throw new Error("Gate 07 rev 11 is not ready for browser evidence.");
}
const output = path.dirname(fileURLToPath(import.meta.url));
const reportPath = path.join(output, "browser-workspace-validation.json");
const report = JSON.parse(fs.readFileSync(reportPath, "utf8"));
if (!report.pass || report.runtimeExceptionCount || report.loadingFailureCount) {
  throw new Error("Gate 07 browser validation failed.");
}
const definitions = [
  ["magnetic-slide-tile-material-browser-test-r011", "browser-test", path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate07.mjs"), "process"],
  ["magnetic-slide-tile-material-browser-report-r011", "browser-report", reportPath, "validation"],
  ["magnetic-slide-tile-material-workbench-preview-r011", "workbench-preview", report.screenshotPath, "analysis"],
  ["magnetic-slide-tile-material-workbench-focused-r011", "workbench-preview", report.focusedScreenshotPath, "analysis"]
];
for (const [id, slot, absolute, role] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing browser artifact ${absolute}.`);
  manifest.assets.push({
    id,
    stageId: "07-material",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Chrome DevTools Protocol",
      version: "headless Chrome with SwiftShader",
      recipe: "Gate 07 rev 11 desktop, mobile, modal, GLB lookdev and video validation"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: stage.materialSpec.governingContractSha256,
      gate06SourceSha256: stage.materialSpec.sourceGate06Sha256,
      geometryDigest: stage.materialSpec.evaluatedGeometryDigest,
      interactionMode: "material-glb-orbit-zoom-environment-exposure",
      runtimeExceptionCount: report.runtimeExceptionCount,
      loadingFailureCount: report.loadingFailureCount,
      unityUsed: false
    },
    sourceAssetIds: [
      "magnetic-slide-tile-material-lookdev-r011",
      "magnetic-slide-tile-material-turntable-r011",
      "magnetic-slide-tile-material-source-comparison-r011"
    ],
    sourceClaimIds: []
  });
}
stage.artifactIds.push(...definitions.map(([id]) => id));
stage.validations.push({
  id: "browser-interactive-lookdev-mobile-modal",
  status: "pass",
  evidence: "Desktop and 390 px mobile passed seven fixed tabs, 12 gates, GLB orbit/zoom, environment/exposure persistence, turntable video, source playback, modal, reload and direct routes with 0 runtime/loading failures."
});
stage.materialSpec.browserEvidence = {
  runtimeExceptionCount: report.runtimeExceptionCount,
  loadingFailureCount: report.loadingFailureCount,
  desktopWidthPx: 1440,
  mobileWidthPx: 390,
  environmentToggle: true,
  exposureToggle: true,
  persistedExposure: report.viewer.persistedExposure,
  persistedEnvironment: report.viewer.persistedEnvironment,
  turntablePlayback: report.turntablePlayback,
  sourcePlayback: report.sourcePlayback
};
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate07-browser-lookdev-validated",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: "07-material",
  materialRevision: 11,
  artifactIds: definitions.map(([id]) => id),
  interactiveViewerAssetId: "magnetic-slide-tile-material-lookdev-r011",
  turntableAssetId: "magnetic-slide-tile-material-turntable-r011",
  runtimeExceptionCount: 0,
  loadingFailureCount: 0,
  visualApprovalPending: true,
  deviceWork: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate07: saved.stages[6].status,
  browserPass: report.pass,
  artifactCount: saved.stages[6].artifactIds.length
}, null, 2));

