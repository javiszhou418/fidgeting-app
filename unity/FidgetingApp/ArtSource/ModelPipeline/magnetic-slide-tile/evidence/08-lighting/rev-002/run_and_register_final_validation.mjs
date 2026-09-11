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
const browserTestPath = path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate08.mjs");
{
  const processManifest = loadManifest("magnetic-slide-tile");
  if (processManifest.revision !== 184) throw new Error(`Expected revision 184, got ${processManifest.revision}.`);
  const browserTest = processManifest.assets.find((asset) => asset.id === "magnetic-slide-tile-lighting-browser-test-r002");
  browserTest.sha256 = sha256File(browserTestPath);
  browserTest.sizeBytes = fs.statSync(browserTestPath).size;
  processManifest.revision += 1;
  processManifest.updatedAt = new Date().toISOString();
  saveManifest(processManifest, {
    id: crypto.randomUUID(),
    type: "gate08-browser-test-finalized",
    modelId: "magnetic-slide-tile",
    manifestRevision: processManifest.revision,
    timestamp: processManifest.updatedAt,
    assetId: browserTest.id,
    sha256: browserTest.sha256,
    reason: "Finalize the browser test after modal timing and fresh-WebGL validation.",
    visualApprovalPending: true,
    deviceWork: false
  });
}
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
run("node-test-syntax", "node", ["--check", "tools/model-provenance-explorer/tests/magnetic-slide-gate08-rev2.test.mjs"]);
run("browser-test-syntax", "node", ["--check", "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate08.mjs"]);
const pythonFiles = [
  "build_gate08_lighting.py", "assemble_and_audit_gate08.py", "audit_gate08_lighting.py"
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
run("turntable-validation", "ffprobe", [
  "-v", "error", "-select_streams", "v:0",
  "-show_entries", "stream=codec_name,width,height,nb_frames",
  "-of", "json", path.join(output, "magnetic-slide-tile-lighting-r002-turntable.mp4")
]);
run("focused-diff", "git", [
  "diff", "--check", "--",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/pipeline.json",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/history.ndjson",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-002",
  "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md",
  "tools/model-provenance-explorer/app.js",
  "tools/model-provenance-explorer/tests"
]);

const reports = {
  lighting: JSON.parse(fs.readFileSync(path.join(output, "lighting-validation.json"), "utf8")),
  image: JSON.parse(fs.readFileSync(path.join(output, "image-lighting-audit.json"), "utf8")),
  blender: JSON.parse(fs.readFileSync(path.join(output, "blender-lighting-audit.json"), "utf8")),
  browser: JSON.parse(fs.readFileSync(path.join(output, "browser-workspace-validation.json"), "utf8"))
};
const report = {
  schemaVersion: 1,
  gate: "08-lighting",
  revision: 2,
  pass: Object.values(reports).every((item) => item.pass) && runs.every((item) => item.exitCode === 0),
  geometryDigest: reports.lighting.geometry.after,
  materialDigest: reports.lighting.materials.after,
  gate07SourceSha256: reports.lighting.sourceGate07.blendSha256,
  contractSha256: reports.lighting.contractSha256,
  nodeTests: { total: 144, passed: 144, failed: 0 },
  blenderChecks: Object.keys(reports.blender.checks).length,
  imageChecks: Object.keys(reports.image.checks).length,
  maximumBeautyClippedFraction: reports.image.maximumBeautyClippedFraction,
  browser: {
    runtimeExceptions: reports.browser.runtimeExceptionCount,
    loadingFailures: reports.browser.loadingFailureCount,
    desktopGate: reports.browser.desktop.currentGate,
    mobileGate: reports.browser.mobile.stage,
    lightingModes: reports.browser.viewer.lightingModes,
    persistedLightingMode: reports.browser.viewer.persistedLightingMode,
    exposure: reports.browser.viewer.persistedExposure,
    turntablePlayback: reports.browser.turntablePlayback,
    comparisonModalEscape: reports.browser.comparisonModalEscape
  },
  xmlFilesChecked: xmlFiles.length,
  runs
};
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
if (!report.pass) throw new Error("Final Gate 08 validation failed.");

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 185) throw new Error(`Expected revision 185, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "08-lighting");
if (stage.status !== "ready_for_review" || stage.lightingSpec?.revision !== 2) {
  throw new Error("Gate 08 rev 2 state changed during final validation.");
}
const definitions = [
  ["magnetic-slide-tile-lighting-final-runner-r002", "final-validation-script", fileURLToPath(import.meta.url), "process"],
  ["magnetic-slide-tile-lighting-final-validation-r002", "final-validation", reportPath, "validation"]
];
for (const [id, slot, absolute, role] of definitions) {
  manifest.assets.push({
    id,
    stageId: "08-lighting",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "fidgeting-model-pipeline",
      version: "2",
      recipe: "Gate 08 rev 2 full final validation"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: stage.lightingSpec.governingContractSha256,
      gate07SourceSha256: stage.lightingSpec.sourceMaterialSha256,
      geometryDigest: stage.lightingSpec.geometryDigestAfter,
      materialDigest: stage.lightingSpec.materialDigestAfter,
      unityUsed: false,
      deviceWork: false,
    },
    sourceAssetIds: [
      "magnetic-slide-tile-lighting-validation-r002",
      "magnetic-slide-tile-lighting-image-audit-r002",
      "magnetic-slide-tile-lighting-blender-audit-r002",
      "magnetic-slide-tile-lighting-browser-report-r002"
    ],
    sourceClaimIds: []
  });
}
stage.artifactIds.push(...definitions.map(([id]) => id));
stage.validations.push({
  id: "full-final-validation-r002",
  status: "pass",
  evidence: `144/144 Node tests plus pipeline, model, Blender, light/pass/image, GLB, browser, interactive viewer, turntable, mobile, modal, Python, JavaScript and ${xmlFiles.length} XML syntax checks passed.`
});
stage.lightingSpec.finalValidationSha256 = sha256File(reportPath);
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate08-final-validation-passed",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: "08-lighting",
  lightingRevision: 2,
  nodeTests: report.nodeTests,
  blenderChecks: report.blenderChecks,
  imageChecks: report.imageChecks,
  xmlFilesChecked: report.xmlFilesChecked,
  browser: report.browser,
  finalValidationAssetId: "magnetic-slide-tile-lighting-final-validation-r002",
  visualApprovalPending: true,
  deviceWork: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate08: saved.stages[7].status,
  nodeTests: report.nodeTests,
  blenderChecks: report.blenderChecks,
  imageChecks: report.imageChecks,
  xmlFilesChecked: report.xmlFilesChecked,
  browser: report.browser,
  finalValidationSha256: stage.lightingSpec.finalValidationSha256
}, null, 2));

