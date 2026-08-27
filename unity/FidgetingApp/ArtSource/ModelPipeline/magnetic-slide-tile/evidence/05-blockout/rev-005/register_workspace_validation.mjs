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
if (manifest.revision !== 167) throw new Error(`Expected pipeline revision 167, got ${manifest.revision}.`);
const here = path.dirname(fileURLToPath(import.meta.url));
const reportPath = path.join(here, "browser-workspace-validation.json");
const report = JSON.parse(fs.readFileSync(reportPath, "utf8"));
if (!report.pass) throw new Error("Persistent workspace browser validation failed.");
const contractHash = manifest.stages[1].analysisSpec.contractSha256;
const files = {
  "magnetic-slide-tile-workspace-app-r005": path.join(repoRoot, "tools/model-provenance-explorer/app.js"),
  "magnetic-slide-tile-workspace-navigation-r005": path.join(repoRoot, "tools/model-provenance-explorer/workspace-navigation-core.mjs"),
  "magnetic-slide-tile-workspace-styles-r005": path.join(repoRoot, "tools/model-provenance-explorer/styles.css"),
  "magnetic-slide-tile-workspace-shell-r005": path.join(repoRoot, "tools/model-provenance-explorer/index.html"),
  "magnetic-slide-tile-workspace-unit-test-r005": path.join(repoRoot, "tools/model-provenance-explorer/tests/workspace-navigation.test.mjs"),
  "magnetic-slide-tile-workspace-browser-test-r005": path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate05.mjs"),
  "magnetic-slide-tile-workspace-browser-report-r005": reportPath,
  "magnetic-slide-tile-workspace-preview-r005": path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev5-persistent-workbench.png"),
  "magnetic-slide-tile-workspace-focused-r005": path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev5-workbench-focused.png")
};
const slots = {
  "magnetic-slide-tile-workspace-app-r005": "workbench-process",
  "magnetic-slide-tile-workspace-navigation-r005": "workbench-process",
  "magnetic-slide-tile-workspace-styles-r005": "workbench-process",
  "magnetic-slide-tile-workspace-shell-r005": "workbench-process",
  "magnetic-slide-tile-workspace-unit-test-r005": "browser-test",
  "magnetic-slide-tile-workspace-browser-test-r005": "browser-test",
  "magnetic-slide-tile-workspace-browser-report-r005": "browser-validation",
  "magnetic-slide-tile-workspace-preview-r005": "workbench-preview",
  "magnetic-slide-tile-workspace-focused-r005": "workbench-preview"
};
const sourceClaimIds = manifest.claims
  .filter((claim) => claim.stageId === "02-analysis" && !["superseded", "stale"].includes(claim.state))
  .map((claim) => claim.id);
for (const [id, absolute] of Object.entries(files)) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing workspace evidence ${absolute}.`);
  manifest.assets.push({
    id,
    stageId: "05-blockout",
    slot: slots[id],
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role: id.includes("preview") || id.includes("focused") || id.includes("report") ? "validation" : "process",
    producer: {
      name: "model-provenance-explorer",
      version: "persistent-workspace-v2",
      recipe: "stable seven-tab navigation, memory, deep-link, history, mobile and GLB validation"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slots[id],
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractHash,
      interactionRequired: true,
      simulatorUsed: false,
      unityChanged: false
    },
    sourceAssetIds: ["magnetic-slide-tile-blockout-interactive-r005"],
    sourceClaimIds
  });
}
const gate05 = manifest.stages[4];
gate05.artifactIds.push(...Object.keys(files));
gate05.validations.push({
  id: "persistent-workbench",
  status: "pass",
  evidence: "Desktop and 390 px mobile preserve seven tabs, model selector, 12-gate roadmap, current task, reload state, history, deep links, stale/rejected evidence, source video and real GLB."
});
manifest.currentState.workbench = "persistent-seven-tab-memory-route-glb-browser-pass";
manifest.currentState.visualApproval = "gate05-rev5-ready-for-review-visual-approval-pending-not-pushed";
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-persistent-workbench-browser-validated",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  contractSha256: contractHash,
  desktopWidthPx: 1440,
  mobileWidthPx: 390,
  fixedTabCount: 7,
  roadmapGateCount: 12,
  reloadMemory: true,
  deepLinks: true,
  browserHistory: true,
  staleArtifactsInspectable: true,
  glbLoaded: true,
  runtimeExceptionCount: report.runtimeExceptionCount,
  loadingFailureCount: report.loadingFailureCount,
  visualApprovalPending: true,
  unityChanged: false,
  deviceWork: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate05: saved.stages[4].status,
  currentStageId: saved.currentStageId,
  workbench: saved.currentState.workbench
}, null, 2));

