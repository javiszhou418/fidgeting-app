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

const here = path.dirname(fileURLToPath(import.meta.url));
const run = (command, args) => {
  const result = spawnSync(command, args, { cwd: repoRoot, encoding: "utf8" });
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(" ")} failed:\n${result.stdout}\n${result.stderr}`);
  }
  return `${result.stdout}\n${result.stderr}`.trim();
};

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 172) throw new Error(`Expected pipeline revision 172, got ${manifest.revision}.`);
const nodeTests = run("npm", ["--prefix", "tools/model-provenance-explorer", "test"]);
const pipelineValidation = JSON.parse(run("node", ["tools/model-provenance-explorer/validate-pipelines.mjs"]));
const modelValidation = JSON.parse(run("node", [
  "skills/fidgeting-model-pipeline/scripts/validate_model_pipeline.mjs",
  "magnetic-slide-tile"
]));
run("node", ["--check", "tools/model-provenance-explorer/app.js"]);
run("node", ["--check", "tools/model-provenance-explorer/workspace-navigation-core.mjs"]);
run("node", ["--check", path.relative(repoRoot, import.meta.filename)]);
run("python3", [
  "-m", "py_compile",
  path.relative(repoRoot, path.join(here, "build_gate05_blockout.py")),
  path.relative(repoRoot, path.join(here, "audit_gate05_blockout.py")),
  path.relative(repoRoot, path.join(here, "compare_rev5_rev6_geometry.py"))
]);
run("python3", ["-c", [
  "from html.parser import HTMLParser",
  "from pathlib import Path",
  "p=HTMLParser()",
  "p.feed(Path('tools/model-provenance-explorer/index.html').read_text())",
  "p.close()"
].join(";")]);

const report = JSON.parse(fs.readFileSync(path.join(here, "blockout-validation.json"), "utf8"));
const audit = JSON.parse(fs.readFileSync(path.join(here, "blender-audit.json"), "utf8"));
const comparison = JSON.parse(fs.readFileSync(path.join(here, "geometry-comparison.json"), "utf8"));
const browser = JSON.parse(fs.readFileSync(path.join(here, "browser-workspace-validation.json"), "utf8"));
if (![report.pass, audit.pass, comparison.pass, browser.pass].every(Boolean)) {
  throw new Error("A durable Gate 05 rev 6 validation report failed.");
}
const glbPath = path.join(here, "magnetic-slide-tile-blockout-r006-review.glb");
if (fs.readFileSync(glbPath).subarray(0, 4).toString("ascii") !== "glTF") {
  throw new Error("Interactive output is not a GLB.");
}
const testMatch = nodeTests.match(/ℹ tests (\d+)/);
const passMatch = nodeTests.match(/ℹ pass (\d+)/);
const finalReport = {
  schemaVersion: 1,
  pass: true,
  nodeTests: {
    total: Number(testMatch?.[1]),
    passed: Number(passMatch?.[1]),
    exitCode: 0
  },
  pipelineValidation,
  modelValidation,
  geometry: {
    planeSampleCount: report.flatPlaneMetrics.sampleCount,
    planeMaximumDeviationMm: report.flatPlaneMetrics.maximumDeviationMm,
    planeToleranceMm: report.flatPlaneMetrics.toleranceMm,
    topVertexRangeMm: audit.topVertexRangeMm,
    carrierClearanceBelowPlaneMm: audit.carrierClearanceBelowPlaneMm,
    geometryComparisonPass: comparison.pass,
    denseSweepSamples: report.denseSweep.sampleCount
  },
  browser: {
    pass: browser.pass,
    desktop: true,
    mobileWidthPx: 390,
    glbLoaded: browser.viewer.open,
    reload: true,
    deepLink: true,
    history: true,
    sourcePlayback: browser.sourcePlayback,
    runtimeExceptionCount: browser.runtimeExceptionCount,
    loadingFailureCount: browser.loadingFailureCount
  },
  blender: {
    pass: audit.pass,
    version: audit.blenderVersion,
    objectCount: audit.objectCount,
    nonmanifoldEdges: audit.nonmanifoldEdges,
    animatedObjects: audit.animatedObjects
  },
  syntax: {
    javascript: "pass",
    python: "pass",
    html5: "pass"
  },
  scope: {
    materialProgression: false,
    simulatorUsed: false,
    unityChanged: false,
    buildInstallOrDevice: false
  }
};
if (!finalReport.nodeTests.total || finalReport.nodeTests.total !== finalReport.nodeTests.passed) {
  throw new Error("Node test totals were not fully passing.");
}
const finalPath = path.join(here, "final-validation.json");
fs.writeFileSync(finalPath, `${JSON.stringify(finalReport, null, 2)}\n`);

const current = loadManifest("magnetic-slide-tile");
const gate05 = current.stages.find((stage) => stage.id === "05-blockout");
const definitions = [
  ["magnetic-slide-tile-blockout-final-validation-r006", "final-validation", finalPath, "validation"],
  ["magnetic-slide-tile-gate05-rev6-implementation-status-final", "implementation-status", path.join(repoRoot, "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"), "process"]
];
for (const [id, slot, absolute, role] of definitions) {
  current.assets.push({
    id,
    stageId: "05-blockout",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "fidgeting-model-pipeline",
      version: "6",
      recipe: "Gate 05 rev 6 final validation and status"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: gate05.blockoutSpec.governingContractSha256,
      simulatorUsed: false,
      unityUsed: false
    },
    sourceAssetIds: [
      "magnetic-slide-tile-blockout-validation-r006",
      "magnetic-slide-tile-blockout-audit-r006",
      "magnetic-slide-tile-blockout-comparison-r006",
      "magnetic-slide-tile-workspace-browser-report-r006"
    ],
    sourceClaimIds: []
  });
  gate05.artifactIds.push(id);
}
gate05.validations.push({
  id: "full-final-validation-rev6",
  status: "pass",
  evidence: `${finalReport.nodeTests.passed}/${finalReport.nodeTests.total} Node tests plus pipeline, model, browser, GLB, Blender, syntax and HTML checks passed.`
});
current.currentState.visualApproval = "gate05-rev6-ready-for-review-visual-approval-pending-not-pushed";
current.revision += 1;
current.updatedAt = new Date().toISOString();
const saved = saveManifest(current, {
  id: crypto.randomUUID(),
  type: "gate05-rev6-full-validation-passed",
  modelId: "magnetic-slide-tile",
  manifestRevision: current.revision,
  timestamp: current.updatedAt,
  finalValidationAssetId: "magnetic-slide-tile-blockout-final-validation-r006",
  nodeTests: finalReport.nodeTests,
  planeMaximumDeviationMm: finalReport.geometry.planeMaximumDeviationMm,
  geometryComparisonPass: true,
  browserPass: true,
  blenderAuditPass: true,
  visualApprovalPending: true,
  unityChanged: false,
  deviceWork: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate05: saved.stages[4].status,
  nodeTests: finalReport.nodeTests,
  planeMaximumDeviationMm: finalReport.geometry.planeMaximumDeviationMm
}, null, 2));

