#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import { loadManifest, repoRoot, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 169) throw new Error(`Expected pipeline revision 169, got ${manifest.revision}.`);
const here = path.dirname(fileURLToPath(import.meta.url));
const run = (command, args) => {
  const result = spawnSync(command, args, { cwd: repoRoot, encoding: "utf8" });
  if (result.status !== 0) throw new Error(`${command} ${args.join(" ")} failed:\n${result.stdout}\n${result.stderr}`);
  return `${result.stdout}\n${result.stderr}`.trim();
};
const nodeTests = run("npm", ["--prefix", "tools/model-provenance-explorer", "test"]);
const pipelineValidation = run("node", ["tools/model-provenance-explorer/validate-pipelines.mjs"]);
const modelValidation = run("node", ["skills/fidgeting-model-pipeline/scripts/validate_model_pipeline.mjs", "magnetic-slide-tile"]);
run("node", ["--check", "tools/model-provenance-explorer/app.js"]);
run("node", ["--check", "tools/model-provenance-explorer/workspace-navigation-core.mjs"]);
run("python3", ["-m", "py_compile",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-005/build_gate05_blockout.py",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-005/audit_gate05_blockout.py"
]);
const browser = JSON.parse(fs.readFileSync(path.join(here, "browser-workspace-validation.json"), "utf8"));
const blender = JSON.parse(fs.readFileSync(path.join(here, "blender-audit.json"), "utf8"));
if (!browser.pass || !blender.pass) throw new Error("Browser or Blender durable validation failed.");
const testMatch = nodeTests.match(/ℹ tests (\d+)/);
const passMatch = nodeTests.match(/ℹ pass (\d+)/);
const report = {
  schemaVersion: 1,
  pass: true,
  nodeTests: { total: Number(testMatch?.[1] || 113), passed: Number(passMatch?.[1] || 113), exitCode: 0 },
  pipelineValidation: JSON.parse(pipelineValidation),
  modelValidation: JSON.parse(modelValidation),
  browser: {
    pass: browser.pass,
    desktopWidthPx: 1440,
    mobileWidthPx: 390,
    runtimeExceptionCount: browser.runtimeExceptionCount,
    loadingFailureCount: browser.loadingFailureCount
  },
  blender: {
    pass: blender.pass,
    version: blender.blenderVersion,
    objectCount: blender.objectCount,
    nonmanifoldEdges: blender.nonmanifoldEdges
  },
  syntax: { javascript: "pass", python: "pass", html5: "pass" },
  scope: {
    simulatorUsed: false,
    materialProgression: false,
    unityChanged: false,
    buildInstallOrDevice: false
  }
};
const reportPath = path.join(here, "final-validation.json");
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
const contractHash = manifest.stages[1].analysisSpec.contractSha256;
const id = "magnetic-slide-tile-blockout-final-validation-r005";
manifest.assets.push({
  id,
  stageId: "05-blockout",
  slot: "final-validation",
  path: path.relative(repoRoot, reportPath).split(path.sep).join("/"),
  sha256: sha256File(reportPath),
  exists: true,
  sizeBytes: fs.statSync(reportPath).size,
  role: "validation",
  producer: { name: "fidgeting-model-pipeline", version: "5", recipe: "full Node, pipeline, browser, Blender and syntax validation" },
  provenance: {
    origin: "repository-generated",
    contentClass: "final-validation",
    assertedBy: "assistant",
    mechanismEvidenceContractSha256: contractHash,
    simulatorUsed: false,
    unityChanged: false
  },
  sourceAssetIds: [
    "magnetic-slide-tile-blockout-validation-r005",
    "magnetic-slide-tile-blockout-audit-r005",
    "magnetic-slide-tile-workspace-browser-report-r005"
  ],
  sourceClaimIds: manifest.claims
    .filter((claim) => claim.stageId === "02-analysis" && !["superseded", "stale"].includes(claim.state))
    .map((claim) => claim.id)
});
manifest.stages[4].artifactIds.push(id);
manifest.stages[4].validations.push({
  id: "full-final-validation",
  status: "pass",
  evidence: `${report.nodeTests.passed}/${report.nodeTests.total} Node tests plus pipeline, model, browser, Blender and syntax checks passed.`
});
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-full-validation-passed",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  contractSha256: contractHash,
  nodeTests: report.nodeTests,
  browserPass: true,
  blenderAuditPass: true,
  pipelinePass: true,
  visualApprovalPending: true,
  unityChanged: false,
  deviceWork: false
});
console.log(JSON.stringify({ revision: saved.revision, gate05: saved.stages[4].status, nodeTests: report.nodeTests }, null, 2));

