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
if (manifest.revision !== 228) throw new Error(`Expected revision 228, got ${manifest.revision}.`);
const gate06 = manifest.stages.find((stage) => stage.id === "06-geometry");
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
if (gate06.status !== "approved" || gate07.status !== "ready_for_review" || gate07.revision !== 12) {
  throw new Error("Gate 07 rev 12 is not ready for browser evidence.");
}
const output = path.dirname(fileURLToPath(import.meta.url));
const browser = JSON.parse(fs.readFileSync(path.join(output, "browser-workspace-validation.json"), "utf8"));
if (!browser.pass || browser.runtimeExceptionCount || browser.loadingFailureCount) {
  throw new Error("Gate 07 browser validation failed.");
}
const contractHash = gate07.materialSpec.governingContractSha256;
const sourceHash = gate07.materialSpec.sourceGate06Sha256;
const geometryDigest = gate07.materialSpec.evaluatedGeometryDigest;
const definitions = [
  ["magnetic-slide-tile-material-browser-report-r012", "browser-validation", path.join(output, "browser-workspace-validation.json"), "validation"],
  ["magnetic-slide-tile-material-workbench-preview-r012", "workbench-preview", path.join(output, "gate07-r012-persistent-workbench.png"), "validation"],
  ["magnetic-slide-tile-material-workbench-focused-r012", "workbench-preview", path.join(output, "gate07-r012-workbench-focused.png"), "validation"],
  ["magnetic-slide-tile-material-browser-test-r012", "browser-test", path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate07-r012.mjs"), "process"],
  ["magnetic-slide-tile-material-browser-generator-r012", "browser-test-generator", path.join(output, "generate_browser_test.py"), "process"],
  ["magnetic-slide-tile-material-browser-register-r012", "registration-script", fileURLToPath(import.meta.url), "process"],
];
for (const [id, slot, absolute, role] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${absolute}.`);
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
      name: absolute.endsWith(".png") ? "Chrome DevTools Protocol" : "fidgeting-model-pipeline",
      version: "Gate 07 rev 12",
      recipe: "Desktop/mobile material workbench, GLB, turntable, modal and persistence validation.",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractHash,
      gate06SourceSha256: sourceHash,
      geometryDigest,
      appearanceChanged: false,
      simulatorUsed: false,
      unityUsed: false,
    },
    sourceAssetIds: [
      "magnetic-slide-tile-material-lookdev-r012",
      "magnetic-slide-tile-material-turntable-r012",
    ],
    sourceClaimIds: [],
  });
}
for (const [id] of definitions) {
  if (!gate07.artifactIds.includes(id)) gate07.artifactIds.push(id);
}
for (const id of [
  "magnetic-slide-tile-material-workbench-preview-r012",
  "magnetic-slide-tile-material-workbench-focused-r012",
]) {
  if (!gate07.reviewArtifactIds.includes(id)) gate07.reviewArtifactIds.push(id);
}
const mutableSharedPaths = new Set([
  "tools/model-provenance-explorer/app.js",
  "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md",
]);
for (const asset of manifest.assets) {
  if (!mutableSharedPaths.has(asset.path)) continue;
  const absolute = path.join(repoRoot, asset.path);
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
  asset.exists = true;
}
gate07.validations.push({
  id: "persistent-browser-workspace",
  status: "pass",
  evidence: `Desktop and 390×844 mobile passed; GLB width ${browser.viewer.width}px; runtime/loading failures 0/0.`,
});
gate07.materialSpec.browserValidation = {
  pass: true,
  desktop: browser.desktop.currentGate,
  mobile: browser.mobile.stage,
  glb: browser.desktop.glb,
  turntable: browser.turntablePlayback,
  runtimeExceptionCount: 0,
  loadingFailureCount: 0,
};
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate07-rev12-browser-validated",
  modelId: manifest.modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "07-material",
  revision: 12,
  contractSha256: contractHash,
  geometryDigest,
  browserValidation: gate07.materialSpec.browserValidation,
  visualApprovalPending: true,
});
console.log(JSON.stringify({ revision: saved.revision, gate07: saved.stages[6].status, browser: "pass" }, null, 2));
