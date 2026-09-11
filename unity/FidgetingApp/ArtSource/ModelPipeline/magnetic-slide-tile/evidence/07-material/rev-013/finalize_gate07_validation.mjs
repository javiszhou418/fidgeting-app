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
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
if (
  manifest.revision !== 236
  || manifest.currentStageId !== "07-material"
  || gate07.status !== "ready_for_review"
  || gate07.revision !== 13
) {
  throw new Error("Gate 07 rev 13 registration state changed before finalization.");
}
const output = path.dirname(fileURLToPath(import.meta.url));
const readJson = (filename) => JSON.parse(
  fs.readFileSync(path.join(output, filename), "utf8"),
);
const finalValidation = readJson("final-validation.json");
const browser = readJson("browser-workspace-validation.json");
if (!finalValidation.pass || !browser.pass || browser.directDeepLink !== "pass") {
  throw new Error("Final or browser validation did not pass.");
}
const definitions = [
  ["magnetic-slide-tile-material-finalizer-r013", "finalization-script", path.join(output, "finalize_gate07_validation.mjs"), "process"],
  ["magnetic-slide-tile-material-final-validation-r013", "final-validation", path.join(output, "final-validation.json"), "validation"],
  ["magnetic-slide-tile-material-focused-junit-r013", "test-results", path.join(output, "focused-node-results.xml"), "validation"],
  ["magnetic-slide-tile-material-full-node-log-r013", "test-results", path.join(output, "full-node-results.log"), "validation"],
  ["magnetic-slide-tile-material-browser-report-r013", "browser-validation", path.join(output, "browser-workspace-validation.json"), "validation"],
  ["magnetic-slide-tile-material-workbench-preview-r013", "workbench-preview", path.join(output, "gate07-r013-persistent-workbench.png"), "analysis"],
  ["magnetic-slide-tile-material-glb-preview-r013", "workbench-preview", path.join(output, "gate07-r013-interactive-glb.png"), "analysis"],
  ["magnetic-slide-tile-material-mobile-preview-r013", "workbench-preview", path.join(output, "gate07-r013-mobile-workbench.png"), "analysis"],
  ["magnetic-slide-tile-material-workbench-source-r013", "workbench-source", path.join(repoRoot, "tools/model-provenance-explorer/app.js"), "process"],
  ["magnetic-slide-tile-material-focused-test-r013", "test-source", path.join(repoRoot, "tools/model-provenance-explorer/tests/magnetic-slide-gate07-rev13.test.mjs"), "process"],
  ["magnetic-slide-tile-material-browser-test-r013", "test-source", path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate07-r013.mjs"), "process"],
  ["magnetic-slide-tile-material-design-bible-r013", "design-bible", path.join(repoRoot, "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md"), "process"],
  ["magnetic-slide-tile-material-implementation-status-r013", "implementation-status", path.join(repoRoot, "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"), "process"],
];
const updatedStateTests = [
  "magnetic-slide-gate05-rebuild.test.mjs",
  "magnetic-slide-gate05-rev12.test.mjs",
  "magnetic-slide-gate05-rev5.test.mjs",
  "magnetic-slide-gate05-rev6.test.mjs",
  "magnetic-slide-gate06-rev4.test.mjs",
  "magnetic-slide-gate06-rev5.test.mjs",
  "magnetic-slide-gate07-rev11.test.mjs",
  "magnetic-slide-gate07-rev12.test.mjs",
  "magnetic-slide-gate08-rev2.test.mjs",
  "magnetic-slide-gate08-rev3-portability.test.mjs",
  "magnetic-slide-gate08-rev5.test.mjs",
  "magnetic-slide-gate09-rev8.test.mjs",
  "magnetic-slide-gate10-rev9.test.mjs",
  "magnetic-slide-gate11-rev9.test.mjs",
  "mechanism-evidence-contract.test.mjs",
  "pipeline-core.test.mjs",
  "workflow-three-phase.test.mjs",
];
for (const filename of updatedStateTests) {
  const id = filename.replace(/\.test\.mjs$/, "").replaceAll(".", "-");
  definitions.push([
    `magnetic-slide-tile-material-current-state-${id}-r013`,
    "test-source",
    path.join(repoRoot, "tools/model-provenance-explorer/tests", filename),
    "process",
  ]);
}
const sources = [
  "magnetic-slide-tile-material-root-cause-r013",
  "magnetic-slide-tile-material-build-report-r013",
  "magnetic-slide-tile-material-transport-r013",
  "magnetic-slide-tile-material-motion-r013",
  "magnetic-slide-tile-material-turntable-report-r013",
  "magnetic-slide-tile-material-board-report-r013",
];
for (const [id, slot, absolute, role] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing final Gate 07 evidence: ${absolute}`);
  if (manifest.assets.some((asset) => asset.id === id)) {
    throw new Error(`Duplicate final Gate 07 asset: ${id}`);
  }
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
      name: "fidgeting-model-pipeline",
      version: "rev-013-final",
      recipe: "Final Gate 07 material, workbench, documentation, and test evidence",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: finalValidation.contractSha256,
      gate06SourceSha256: finalValidation.gate06SourceSha256,
      geometryDigest: finalValidation.geometryDigest,
      sideWallArtworkPixels: 0,
      visualApprovalPending: true,
      simulatorUsed: false,
      unityUsed: false,
      phoneUsed: false,
    },
    sourceAssetIds: sources,
    sourceClaimIds: [],
  });
}
gate07.artifactIds.push(...definitions.map(([id]) => id));
gate07.validations.push(
  {
    id: "focused-node-junit",
    status: "pass",
    evidence: "6/6 focused Gate 07 tests passed; JUnit XML is well formed.",
  },
  {
    id: "full-node-suite",
    status: "pass",
    evidence: "204/205 passed. The only failure is an unrelated concurrent Premium Display Case test expecting Gate 12 approved while its current Gate 04 is draft.",
  },
  {
    id: "browser-desktop-mobile-modal-deeplink",
    status: "pass",
    evidence: "Desktop, 390x844 mobile, GLB orbit/zoom, video, image modal, reload, and direct asset route passed with 0 runtime or loading failures.",
  },
  {
    id: "syntax-xml-video-diff",
    status: "pass",
    evidence: "Python and JavaScript syntax, JUnit XML, full H.264 decode, and focused diff whitespace checks passed.",
  },
);
gate07.materialSpec.finalValidationSha256 = sha256File(path.join(output, "final-validation.json"));
gate07.materialSpec.browserValidationSha256 = sha256File(path.join(output, "browser-workspace-validation.json"));
gate07.materialSpec.focusedJunitSha256 = sha256File(path.join(output, "focused-node-results.xml"));
gate07.materialSpec.fullNodeLogSha256 = sha256File(path.join(output, "full-node-results.log"));
gate07.readiness = {
  ready: true,
  blockers: [],
  note: "Gate 07 rev 13 is ready for review. Interact with the GLB, then inspect the legal-motion turntable and closeups. Visual approval pending; not pushed to phone.",
};
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate07-rev13-final-validation-passed",
  modelId: manifest.modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "07-material",
  stageRevision: 13,
  geometryDigest: finalValidation.geometryDigest,
  sideWallArtworkPixels: 0,
  focusedNode: "6/6",
  fullNode: "204/205; one unrelated concurrent Premium Display Case assertion",
  browser: {
    desktop: "pass",
    mobile: "pass",
    glb: "pass",
    video: "pass",
    modal: "pass",
    directDeepLink: "pass",
    runtimeExceptions: 0,
    loadingFailures: 0,
  },
  visualApprovalPending: true,
  simulatorUsed: false,
  unityUsed: false,
  buildInstallOrPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate07: saved.stages[6].status,
  artifactCount: saved.stages[6].artifactIds.length,
  reviewArtifactCount: saved.stages[6].reviewArtifactIds.length,
  finalValidation: "pass",
}, null, 2));
