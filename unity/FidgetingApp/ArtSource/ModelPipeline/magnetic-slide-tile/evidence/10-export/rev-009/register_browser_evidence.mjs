#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { loadManifest, repoRoot, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 193) throw new Error(`Expected revision 193, got ${manifest.revision}.`);
const stage = manifest.stages[9];
if (stage.status !== "ready_for_review" || stage.exportSpec?.revision !== 9) throw new Error("Gate 10 rev 9 is not ready.");
const output = path.join(repoRoot, "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-009");
const report = JSON.parse(fs.readFileSync(path.join(output, "browser-workspace-validation.json"), "utf8"));
if (!report.pass || report.runtimeExceptionCount || report.loadingFailureCount) throw new Error("Browser validation failed.");
const definitions = [
  ["magnetic-slide-tile-export-browser-test-r009", "browser-validation-script", path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate10.mjs"), "process"],
  ["magnetic-slide-tile-export-node-test-r009", "node-test", path.join(repoRoot, "tools/model-provenance-explorer/tests/magnetic-slide-gate10-rev9.test.mjs"), "process"],
  ["magnetic-slide-tile-export-browser-validation-r009", "browser-workspace-validation", path.join(output, "browser-workspace-validation.json"), "validation"],
  ["magnetic-slide-tile-export-browser-workbench-r009", "browser-workbench", path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate10-rev9-persistent-workbench.png"), "analysis"],
  ["magnetic-slide-tile-export-browser-focused-r009", "browser-workbench-focused", path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate10-rev9-workbench-focused.png"), "analysis"],
];
for (const [id, slot, absolute, role] of definitions) {
  manifest.assets.push({
    id, stageId: "10-export", slot, path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute), exists: true, sizeBytes: fs.statSync(absolute).size, role,
    producer: { name: "Chrome CDP / Node", version: "Gate 10 rev 9", recipe: "Real exported GLB load, orbit, zoom, modal, reload and mobile validation" },
    provenance: {
      origin: "repository-generated", contentClass: slot, assertedBy: "assistant",
      mechanismEvidenceContractSha256: stage.exportSpec.governingContractSha256,
      portabilityContractSha256: stage.exportSpec.portabilityContractSha256,
      geometryDigest: stage.exportSpec.geometryDigest, materialDigest: stage.exportSpec.materialDigest,
      exportGlbSha256: stage.exportSpec.glbSha256, unityImportApplied: false, deviceWork: false,
    },
    sourceAssetIds: ["magnetic-slide-tile-export-glb-r009", "magnetic-slide-tile-export-summary-r009"], sourceClaimIds: [],
  });
}
const app = manifest.assets.find((asset) => asset.id === "magnetic-slide-tile-export-workbench-r009");
app.sha256 = sha256File(path.join(repoRoot, app.path));
app.sizeBytes = fs.statSync(path.join(repoRoot, app.path)).size;
stage.artifactIds.push(...definitions.map(([id]) => id));
stage.validations.push({
  id: "browser-real-glb-mobile-modal-r009", status: "pass",
  evidence: `Desktop 1440 px and mobile 390 px passed. Real GLB loaded at ${report.viewer.canvasWidth}px, orbit/zoom/load checklist unlocked approval; reload persisted. Runtime/loading failures 0/0.`,
});
stage.exportSpec.browserEvidence = {
  desktopWidthPx: 1440, mobileWidthPx: 390,
  approvedCount: 9, currentGate: 10,
  glbChecklist: report.viewer.checklist,
  approvalInitiallyDisabled: report.desktop.approveDisabled,
  approvalEnabledAfterChecklist: !report.viewer.approveDisabled,
  runtimeExceptionCount: report.runtimeExceptionCount,
  loadingFailureCount: report.loadingFailureCount,
  mobileOneColumn: report.mobile.oneColumn,
};
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(), type: "gate10-export-r009-browser-passed", modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision, timestamp: manifest.updatedAt,
  exportGlbSha256: stage.exportSpec.glbSha256,
  completedInteractionChecklist: ["loaded", "orbit", "zoom"],
  desktopWidthPx: 1440, mobileWidthPx: 390,
  runtimeExceptionCount: 0, loadingFailureCount: 0, unityChanged: false, deviceWork: false,
});
console.log(JSON.stringify({ revision: saved.revision, browser: "pass", checklist: report.viewer.checklist }, null, 2));

