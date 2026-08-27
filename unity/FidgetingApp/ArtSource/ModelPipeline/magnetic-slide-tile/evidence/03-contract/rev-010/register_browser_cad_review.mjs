#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, repoRoot, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 164) throw new Error(`Expected pipeline revision 164, got ${manifest.revision}.`);
const here = path.dirname(fileURLToPath(import.meta.url));
const reportPath = path.join(here, "browser-cad-validation.json");
const report = JSON.parse(fs.readFileSync(reportPath, "utf8"));
if (!report.pass) throw new Error("Browser CAD validation failed.");
const contractHash = manifest.stages[1].analysisSpec.contractSha256;
const paths = {
  "slider-analysis-four-track-cad-core-r016": path.join(repoRoot, "tools/model-provenance-explorer/mechanism-cad-core.mjs"),
  "slider-analysis-four-track-cad-ui-r016": path.join(repoRoot, "tools/model-provenance-explorer/app.js"),
  "slider-analysis-four-track-cad-style-r016": path.join(repoRoot, "tools/model-provenance-explorer/styles.css"),
  "slider-contract-four-track-browser-test-r010": path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-four-track-cad.mjs"),
  "slider-contract-four-track-browser-validation-r010": reportPath,
  "slider-contract-four-track-workbench-r010": path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate03-rev10-four-track-cad.png"),
  "slider-contract-four-track-cad-focused-r010": path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate03-rev10-four-track-cad-focused.png")
};
const definitions = [
  ["slider-analysis-four-track-cad-core-r016", "02-analysis", "mechanism-core", "process"],
  ["slider-analysis-four-track-cad-ui-r016", "02-analysis", "interactive-cad", "process"],
  ["slider-analysis-four-track-cad-style-r016", "02-analysis", "interactive-cad-style", "process"],
  ["slider-contract-four-track-browser-test-r010", "03-contract", "browser-test", "process"],
  ["slider-contract-four-track-browser-validation-r010", "03-contract", "browser-validation", "validation"],
  ["slider-contract-four-track-workbench-r010", "03-contract", "workbench-preview", "validation"],
  ["slider-contract-four-track-cad-focused-r010", "03-contract", "interactive-cad-preview", "validation"]
];
const activeClaims = manifest.claims.filter((claim) => claim.stageId === "02-analysis" && !["superseded", "stale"].includes(claim.state)).map((claim) => claim.id);
for (const [id, stageId, slot, role] of definitions) {
  const absolute = paths[id];
  manifest.assets.push({
    id, stageId, slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute), exists: true, sizeBytes: fs.statSync(absolute).size, role,
    producer: { name: "Chrome CDP + model-provenance-explorer", version: "headless-new", recipe: "four-track raised-axis desktop/mobile/modal/video/source validation" },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractHash,
      interactionRequired: true,
      simulatorUsed: false,
      blenderUsed: false,
      unityChanged: false
    },
    sourceAssetIds: ["slider-analysis-mechanism-evidence-contract-r016", "slider-analysis-interactive-cad-geometry-config-r016"],
    sourceClaimIds: stageId === "02-analysis" ? [] : activeClaims
  });
}
manifest.stages[1].artifactIds.push(...definitions.filter(([, stageId]) => stageId === "02-analysis").map(([id]) => id));
manifest.stages[2].artifactIds.push(...definitions.filter(([, stageId]) => stageId === "03-contract").map(([id]) => id));
manifest.stages[2].reviewArtifactIds = [
  "slider-contract-four-track-cad-focused-r010",
  "slider-measurement-anthropometric-video-report-r010"
];
manifest.stages[2].validations.push({
  id: "four-track-interactive-browser",
  status: "pass",
  evidence: "Desktop and 390 px mobile render four role-labeled tracks, raised boss, compound pointer motion, video modal, source gallery and zero overflow/exceptions."
});
manifest.currentState.visualApproval = "gate03-four-track-raised-axis-interactive-cad-pending";
manifest.currentState.browserValidation = "desktop-mobile-pointer-modal-video-source-pass";
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate03-four-track-interactive-cad-browser-validated",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  contractSha256: contractHash,
  desktopWidthPx: 1440,
  mobileWidthPx: 390,
  trackCount: 4,
  pointerCompoundMotion: true,
  runtimeExceptionCount: report.runtimeExceptionCount,
  loadingFailureCount: report.loadingFailureCount,
  blenderUsed: false,
  unityChanged: false,
  deviceWork: false
});
console.log(JSON.stringify({ revision: saved.revision, gate03: saved.stages[2].status, reviewArtifactIds: saved.stages[2].reviewArtifactIds }, null, 2));
