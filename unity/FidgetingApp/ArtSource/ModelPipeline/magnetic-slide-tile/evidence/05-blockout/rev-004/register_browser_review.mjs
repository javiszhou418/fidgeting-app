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
if (manifest.revision !== 161) throw new Error(`Expected pipeline revision 161, got ${manifest.revision}.`);
const now = new Date().toISOString();
const here = path.dirname(fileURLToPath(import.meta.url));
const reportPath = path.join(here, "browser-smoke-validation.json");
const screenshotPath = path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev4-workbench.png");
const testPath = path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-gate05-review.mjs");
const report = JSON.parse(fs.readFileSync(reportPath, "utf8"));
if (!report.pass) throw new Error("Browser validation did not pass.");
const contractHash = "b4318452f163ef7c105c826d4466a739a1dd0d942d4d74d921c29c39e02a84f2";
const sourceAssetIds = [
  "magnetic-slide-tile-blockout-interactive-r004",
  "magnetic-slide-tile-blockout-hero-r004"
];
const definitions = [
  ["magnetic-slide-tile-blockout-browser-test-r004", "browser-test", testPath, "process"],
  ["magnetic-slide-tile-blockout-browser-validation-r004", "browser-validation", reportPath, "validation"],
  ["magnetic-slide-tile-blockout-workbench-r004", "workbench-preview", screenshotPath, "validation"]
];
for (const [id, slot, absolute, role] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing browser artifact ${absolute}.`);
  manifest.assets.push({
    id,
    stageId: "05-blockout",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: { name: "Chrome CDP", version: "headless-new", recipe: "Gate 05 real GLB desktop/mobile smoke" },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractHash,
      interactiveGlbRequired: true,
      simulatorUsed: false,
      unityUsed: false
    },
    sourceAssetIds,
    sourceClaimIds: manifest.claims
      .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
      .map((claim) => claim.id)
  });
}
const gate05 = manifest.stages.find((stage) => stage.id === "05-blockout");
gate05.artifactIds.push(...definitions.map(([id]) => id));
gate05.validations.push({
  id: "browser-interactive-viewer",
  status: "pass",
  evidence: "Real GLB loaded in Three.js; desktop view controls/wireframe, image modal Escape, 390 px mobile viewer and zero horizontal overflow passed."
});
manifest.revision += 1;
manifest.updatedAt = now;
manifest.currentState.visualApproval = "gate05-rev4-interactive-review-ready";
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-browser-interactive-review-validated",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "05-blockout",
  artifactIds: definitions.map(([id]) => id),
  desktopWidthPx: 1440,
  mobileWidthPx: 390,
  realGlbLoaded: true,
  runtimeExceptionCount: report.runtimeExceptionCount,
  loadingFailureCount: report.loadingFailureCount,
  simulatorUsed: false,
  unityChanged: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate05Status: saved.stages[4].status,
  artifactCount: saved.stages[4].artifactIds.length
}, null, 2));
