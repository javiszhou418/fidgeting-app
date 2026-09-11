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
const gate05 = manifest.stages.find((stage) => stage.id === "05-blockout");
if (gate05.blockoutSpec?.revision !== 6) throw new Error("Gate 05 rev 6 is not current.");
const here = path.dirname(fileURLToPath(import.meta.url));
const report = JSON.parse(fs.readFileSync(path.join(here, "browser-workspace-validation.json"), "utf8"));
if (!report.pass || report.runtimeExceptionCount || report.loadingFailureCount) {
  throw new Error("Persistent workbench browser validation failed.");
}
const definitions = [
  ["magnetic-slide-tile-workspace-browser-report-r006", "browser-validation", path.join(here, "browser-workspace-validation.json"), "validation"],
  ["magnetic-slide-tile-workspace-browser-test-r006", "browser-test", path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate05.mjs"), "process"],
  ["magnetic-slide-tile-workspace-full-preview-r006", "workbench-preview", path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev6-persistent-workbench.png"), "validation"],
  ["magnetic-slide-tile-workspace-focused-preview-r006", "workbench-focused-preview", path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev6-workbench-focused.png"), "validation"],
  ["magnetic-slide-tile-gate05-rev6-design-bible", "design-bible", path.join(repoRoot, "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"), "process"],
  ["magnetic-slide-tile-gate05-rev6-implementation-status", "implementation-status", path.join(repoRoot, "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"), "process"]
];
const sourceAssetIds = [
  "magnetic-slide-tile-blockout-interactive-r006",
  "magnetic-slide-tile-blockout-validation-r006",
  "magnetic-slide-tile-blockout-audit-r006",
  "magnetic-slide-tile-blockout-comparison-r006"
];
for (const [id, slot, absolute, role] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${absolute}.`);
  manifest.assets.push({
    id,
    stageId: "05-blockout",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: role === "validation" ? "Chrome CDP" : "fidgeting-model-pipeline",
      version: "6",
      recipe: "Gate 05 rev 6 persistent workbench, GLB and decision validation"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: gate05.blockoutSpec.governingContractSha256,
      simulatorUsed: false,
      unityUsed: false
    },
    sourceAssetIds,
    sourceClaimIds: []
  });
  gate05.artifactIds.push(id);
}
gate05.validations.push({
  id: "persistent-workbench-rev6",
  status: "pass",
  evidence: "Desktop and 390 px mobile workbench passed fixed tabs, 12-gate roadmap, rev 4/5 history, rev 6 GLB, modal, reload, deep links, browser history and source playback with 0 runtime/loading failures."
});
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-default-gate05-rev6-browser-validated";
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-rev6-persistent-workbench-validated",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  reportAssetId: "magnetic-slide-tile-workspace-browser-report-r006",
  screenshotAssetIds: [
    "magnetic-slide-tile-workspace-full-preview-r006",
    "magnetic-slide-tile-workspace-focused-preview-r006"
  ],
  desktopPass: true,
  mobilePass: true,
  glbPass: true,
  runtimeExceptionCount: 0,
  loadingFailureCount: 0,
  visualApprovalPending: true,
  unityChanged: false,
  deviceWork: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate05Status: saved.stages[4].status,
  browserPass: true
}, null, 2));

