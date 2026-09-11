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
if (manifest.revision !== 229) throw new Error(`Expected revision 229, got ${manifest.revision}.`);
const gate07 = manifest.stages.find((stage) => stage.id === "07-material");
if (gate07.status !== "ready_for_review" || gate07.revision !== 12) throw new Error("Gate 07 rev 12 is not current.");
const output = path.dirname(fileURLToPath(import.meta.url));
const reportPath = path.join(output, "final-validation.json");
const report = JSON.parse(fs.readFileSync(reportPath, "utf8"));
if (!report.pass) throw new Error("Final Gate 07 validation failed.");
const id = "magnetic-slide-tile-material-final-validation-r012";
manifest.assets.push({
  id,
  stageId: "07-material",
  slot: "final-validation",
  path: path.relative(repoRoot, reportPath).split(path.sep).join("/"),
  sha256: sha256File(reportPath),
  exists: true,
  sizeBytes: fs.statSync(reportPath).size,
  role: "validation",
  producer: {
    name: "gate07 endpoint material finalizer",
    version: "rev-012",
    recipe: "Aggregate Blender, image, motion, Node, pipeline, browser, GLB and turntable checks.",
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "final-validation",
    assertedBy: "assistant",
    mechanismEvidenceContractSha256: report.contractSha256,
    gate06SourceSha256: report.gate06SourceSha256,
    geometryDigest: report.geometryDigest,
    appearanceChanged: false,
    simulatorUsed: false,
    unityUsed: false,
  },
  sourceAssetIds: [
    "magnetic-slide-tile-material-validation-r012",
    "magnetic-slide-tile-material-blender-audit-r012",
    "magnetic-slide-tile-material-image-audit-r012",
    "magnetic-slide-tile-material-motion-audit-r012",
    "magnetic-slide-tile-material-browser-report-r012",
  ],
  sourceClaimIds: [],
});
gate07.artifactIds.push(id);
gate07.validations.push({
  id: "final-gate07-validation",
  status: "pass",
  evidence: "Focused Node 6/6; full Node 192/194 with two unrelated Premium Display Case expectations; pipeline 0/0/0; browser 0/0 runtime/loading failures.",
});
gate07.materialSpec.finalValidationSha256 = sha256File(reportPath);
gate07.readiness = {
  ready: true,
  blockers: [],
  note: "Interactive material GLB and real Blender turntable are ready. Visual approval is pending; nothing was pushed to a phone.",
};
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate07-rev12-final-validation-passed",
  modelId: manifest.modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "07-material",
  revision: 12,
  contractSha256: report.contractSha256,
  geometryDigest: report.geometryDigest,
  nodeTests: report.verification.fullNode,
  browser: report.verification.browser,
  visualApprovalPending: true,
  simulatorUsed: false,
  unityChanged: false,
  buildInstallOrDevice: false,
});
console.log(JSON.stringify({ revision: saved.revision, gate07: saved.stages[6].status, finalValidation: "pass" }, null, 2));
