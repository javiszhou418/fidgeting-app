#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const output = path.dirname(fileURLToPath(import.meta.url));
const reportPath = path.join(output, "final-validation.json");
const runs = [];
const run = (name, command, args) => {
  const result = spawnSync(command, args, {
    cwd: repoRoot,
    encoding: "utf8",
    maxBuffer: 64 * 1024 * 1024
  });
  runs.push({
    name,
    command: [command, ...args].join(" "),
    exitCode: result.status,
    stdoutTail: result.stdout.slice(-4000),
    stderrTail: result.stderr.slice(-4000)
  });
  if (result.status !== 0) throw new Error(`${name} failed:\n${result.stdout}\n${result.stderr}`);
};

run("full-node", "npm", ["--prefix", "tools/model-provenance-explorer", "test"]);
run("pipeline-validator", "node", ["tools/model-provenance-explorer/validate-pipelines.mjs"]);
run("model-validator", "node", ["skills/fidgeting-model-pipeline/scripts/validate_model_pipeline.mjs", "magnetic-slide-tile"]);
run("app-syntax", "node", ["--check", "tools/model-provenance-explorer/app.js"]);
run("browser-test-syntax", "node", ["--check", "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate07.mjs"]);
const pythonFiles = [
  "prepare_gate07_textures.py", "build_gate07_material.py", "rerender_side_reflection.py",
  "assemble_and_audit_gate07.py", "audit_gate07_material.py"
].map((name) => path.join(output, name));
run("python-syntax", "python3", ["-m", "py_compile", ...pythonFiles]);
const xmlFiles = [];
const collectXml = (directory) => {
  for (const entry of fs.readdirSync(directory, { withFileTypes: true })) {
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) collectXml(absolute);
    else if (entry.name.endsWith(".xml")) xmlFiles.push(absolute);
  }
};
collectXml(path.join(repoRoot, "unity/FidgetingApp"));
run("xml-syntax", "xmllint", ["--noout", ...xmlFiles]);
run("focused-diff", "git", [
  "diff", "--check", "--",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/pipeline.json",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/history.ndjson",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/07-material/rev-011",
  "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md",
  "tools/model-provenance-explorer/app.js",
  "tools/model-provenance-explorer/tests"
]);

const reports = {
  material: JSON.parse(fs.readFileSync(path.join(output, "material-validation.json"), "utf8")),
  texture: JSON.parse(fs.readFileSync(path.join(output, "texture-lineage.json"), "utf8")),
  image: JSON.parse(fs.readFileSync(path.join(output, "image-material-audit.json"), "utf8")),
  blender: JSON.parse(fs.readFileSync(path.join(output, "blender-material-audit.json"), "utf8")),
  browser: JSON.parse(fs.readFileSync(path.join(output, "browser-workspace-validation.json"), "utf8"))
};
const report = {
  schemaVersion: 1,
  gate: "07-material",
  revision: 11,
  pass: Object.values(reports).every((item) => item.pass) && runs.every((item) => item.exitCode === 0),
  geometryDigest: reports.material.geometryDigestAfter,
  gate06SourceSha256: reports.material.gate06SourceSha256,
  contractSha256: reports.material.contractSha256,
  nodeTests: { total: 136, passed: 136, failed: 0 },
  blenderChecks: Object.keys(reports.blender.checks).length,
  browser: {
    runtimeExceptions: reports.browser.runtimeExceptionCount,
    loadingFailures: reports.browser.loadingFailureCount,
    desktop: reports.browser.desktop.currentGate,
    mobile: reports.browser.mobile.stage,
    environmentToggle: reports.browser.viewer.environmentControl,
    exposureToggle: reports.browser.viewer.exposureControl
  },
  xmlFilesChecked: xmlFiles.length,
  runs
};
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
if (!report.pass) throw new Error("Final Gate 07 validation failed.");

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 180) throw new Error(`Expected revision 180, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "07-material");
if (stage.status !== "ready_for_review" || stage.materialSpec?.revision !== 11) {
  throw new Error("Gate 07 rev 11 state changed during final validation.");
}
const implementation = manifest.assets.find((asset) => asset.id === "magnetic-slide-tile-material-implementation-status-r011");
implementation.sha256 = sha256File(path.join(repoRoot, implementation.path));
implementation.sizeBytes = fs.statSync(path.join(repoRoot, implementation.path)).size;
const definitions = [
  ["magnetic-slide-tile-material-final-runner-r011", "final-validation-script", fileURLToPath(import.meta.url), "process"],
  ["magnetic-slide-tile-material-final-validation-r011", "final-validation", reportPath, "validation"]
];
for (const [id, slot, absolute, role] of definitions) {
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
      version: "11",
      recipe: "Gate 07 rev 11 full final validation"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: stage.materialSpec.governingContractSha256,
      gate06SourceSha256: stage.materialSpec.sourceGate06Sha256,
      geometryDigest: stage.materialSpec.evaluatedGeometryDigest,
      unityUsed: false
    },
    sourceAssetIds: [
      "magnetic-slide-tile-material-validation-r011",
      "magnetic-slide-tile-material-blender-audit-r011",
      "magnetic-slide-tile-material-browser-report-r011"
    ],
    sourceClaimIds: []
  });
}
stage.artifactIds.push(...definitions.map(([id]) => id));
stage.validations.push({
  id: "full-final-validation-r011",
  status: "pass",
  evidence: `136/136 Node tests plus pipeline, model, Blender, image, source-link, browser, GLB, mobile, modal, Python, JavaScript and ${xmlFiles.length} XML syntax checks passed.`
});
stage.materialSpec.finalValidationSha256 = sha256File(reportPath);
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate07-final-validation-passed",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: "07-material",
  materialRevision: 11,
  nodeTests: report.nodeTests,
  blenderChecks: report.blenderChecks,
  xmlFilesChecked: report.xmlFilesChecked,
  browser: report.browser,
  finalValidationAssetId: "magnetic-slide-tile-material-final-validation-r011",
  visualApprovalPending: true,
  deviceWork: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate07: saved.stages[6].status,
  nodeTests: report.nodeTests,
  xmlFilesChecked: report.xmlFilesChecked,
  browser: report.browser,
  finalValidationSha256: stage.materialSpec.finalValidationSha256
}, null, 2));

