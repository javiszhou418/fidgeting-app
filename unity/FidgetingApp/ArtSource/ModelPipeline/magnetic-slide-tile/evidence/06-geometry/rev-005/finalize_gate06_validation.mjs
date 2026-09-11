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

const manifest = loadManifest("magnetic-slide-tile");
const gate06 = manifest.stages.find((stage) => stage.id === "06-geometry");
if (manifest.revision !== 222 || gate06?.status !== "ready_for_review" || gate06?.revision !== 5) {
  throw new Error(`Unexpected Gate 06 finalization state ${manifest.revision}/${gate06?.status}/${gate06?.revision}.`);
}
const output = path.dirname(fileURLToPath(import.meta.url));
const browserReport = JSON.parse(fs.readFileSync(path.join(output, "browser-workspace-validation.json"), "utf8"));
if (!browserReport.pass || browserReport.runtimeExceptionCount !== 0 || browserReport.loadingFailureCount !== 0) {
  throw new Error("Gate 06 browser validation failed.");
}
const contractSha = gate06.geometrySpec.governingContractSha256;
const geometryDigest = gate06.geometrySpec.canonicalGeometryDigest;
const definitions = [
  ["magnetic-slide-tile-geometry-browser-validation-r005", "browser-validation", path.join(output, "browser-workspace-validation.json"), "validation"],
  ["magnetic-slide-tile-geometry-workbench-preview-r005", "workbench-preview", path.join(output, "gate06-r005-persistent-workbench.png"), "validation"],
  ["magnetic-slide-tile-geometry-workbench-focused-r005", "workbench-focused-preview", path.join(output, "gate06-r005-workbench-focused.png"), "validation"],
  ["magnetic-slide-tile-geometry-browser-script-r005", "browser-test-script", path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate06-r005.mjs"), "process"],
  ["magnetic-slide-tile-geometry-finalizer-r005", "finalizer-script", path.join(output, "finalize_gate06_validation.mjs"), "process"],
];
for (const [, , absolute] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing final validation artifact ${absolute}.`);
}
const ids = new Set(definitions.map(([id]) => id));
manifest.assets = manifest.assets.filter((asset) => !ids.has(asset.id));
const sourceAssetIds = [
  "magnetic-slide-tile-geometry-interactive-r005",
  "magnetic-slide-tile-geometry-state-machine-r005",
  "magnetic-slide-tile-geometry-validation-r005",
];
for (const [id, slot, absolute, role] of definitions) {
  manifest.assets.push({
    id,
    stageId: "06-geometry",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: slot.includes("workbench") ? "Chrome CDP" : "fidgeting-model-pipeline",
      version: slot.includes("workbench") ? "headless-new" : "endpoint-interlock-2026-08-28",
      recipe: "Gate 06 rev 5 persistent workbench desktop/mobile/GLB/modal validation",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractSha,
      gate05SourceSha256: gate06.geometrySpec.gate05SourceSha256,
      geometryDigest,
      geometryChanged: false,
      simulatorUsed: false,
      finalUnityUsed: false,
      buildInstallPhone: false,
    },
    sourceAssetIds,
    sourceClaimIds: [],
  });
}
gate06.artifactIds.push(...definitions.map(([id]) => id));
gate06.reviewArtifactIds.push(
  "magnetic-slide-tile-geometry-workbench-preview-r005",
  "magnetic-slide-tile-geometry-workbench-focused-r005",
);
const appAsset = manifest.assets.find((asset) => asset.id === "magnetic-slide-tile-gate06-workbench-copy-r005");
const appPath = path.join(repoRoot, appAsset.path);
appAsset.sha256 = sha256File(appPath);
appAsset.sizeBytes = fs.statSync(appPath).size;
gate06.validations = gate06.validations.filter((validation) => validation.id !== "browser-workbench");
gate06.validations.push({
  id: "browser-workbench",
  status: "pass",
  evidence: "Desktop 1440×1800 and mobile 390×844: seven tabs, 12 gates, GLB load, top view, image modal, SVG and blocked-pose fetch, history, stale materials and zero overflow passed; runtime/loading failures=0/0.",
});
gate06.geometrySpec.browserValidation = {
  pass: true,
  desktop: "1440x1800",
  mobile: "390x844@2x",
  runtimeExceptionCount: 0,
  loadingFailureCount: 0,
  glbViewerWidthPx: browserReport.viewer.width,
};
gate06.historicalApprovals = [
  {
    gateRevision: 4,
    exactUserWording: "那你继续呗",
    decisionState: "approved-then-superseded-by-current-contract",
    geometryDigest: "e2a838c22b743c7b0a05a20df060817f4e324bad5c84c11592c673c25ee002fe",
    evidencePath: "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/06-geometry/rev-004/",
  },
];
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate06-rev5-final-validation",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: "06-geometry",
  revision: 5,
  status: "ready_for_review",
  contractSha256: contractSha,
  geometryDigest,
  browser: {
    desktop: "pass",
    mobile: "pass",
    glb: "pass",
    modal: "pass",
    history: "pass",
    runtimeExceptionCount: 0,
    loadingFailureCount: 0,
  },
  preservedHistoricalApproval: gate06.historicalApprovals[0],
  visualApprovalPending: true,
  finalUnityBuildInstallPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate06: saved.stages[5].status,
  artifactCount: saved.stages[5].artifactIds.length,
  reviewArtifactCount: saved.stages[5].reviewArtifactIds.length,
  browserPass: true,
}, null, 2));
