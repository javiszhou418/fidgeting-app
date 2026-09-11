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
const gate06 = manifest.stages.find((stage) => stage.id === "06-geometry");
if (manifest.revision !== 176 || gate06.status !== "ready_for_review" || gate06.geometrySpec?.revision !== 4) {
  throw new Error("Gate 06 rev 4 is not ready for final validation.");
}
const nodeOutput = run("npm", ["--prefix", "tools/model-provenance-explorer", "test"]);
const testMatch = nodeOutput.match(/ℹ tests (\d+)/);
const passMatch = nodeOutput.match(/ℹ pass (\d+)/);
const pipelineValidation = JSON.parse(run("node", ["tools/model-provenance-explorer/validate-pipelines.mjs"]));
const modelValidation = JSON.parse(run("node", [
  "skills/fidgeting-model-pipeline/scripts/validate_model_pipeline.mjs",
  "magnetic-slide-tile"
]));
run("node", ["--check", "tools/model-provenance-explorer/app.js"]);
run("node", ["--check", "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate06.mjs"]);
run("node", ["--check", path.relative(repoRoot, import.meta.filename)]);
run("python3", [
  "-m", "py_compile",
  path.relative(repoRoot, path.join(here, "build_gate06_geometry.py")),
  path.relative(repoRoot, path.join(here, "audit_gate06_geometry.py"))
]);
run("python3", ["-c", [
  "from html.parser import HTMLParser",
  "from pathlib import Path",
  "p=HTMLParser()",
  "p.feed(Path('tools/model-provenance-explorer/index.html').read_text())",
  "p.close()"
].join(";")]);

const geometry = JSON.parse(fs.readFileSync(path.join(here, "geometry-validation.json"), "utf8"));
const blender = JSON.parse(fs.readFileSync(path.join(here, "blender-audit.json"), "utf8"));
const browser = JSON.parse(fs.readFileSync(path.join(here, "browser-workspace-validation.json"), "utf8"));
if (![geometry.pass, blender.pass, browser.pass].every(Boolean)) {
  throw new Error("A durable Gate 06 validation report failed.");
}
const glbPath = path.join(here, "magnetic-slide-tile-geometry-r004-review.glb");
if (fs.readFileSync(glbPath).subarray(0, 4).toString("ascii") !== "glTF") {
  throw new Error("Gate 06 interactive output is not a GLB.");
}
const nodeTests = { total: Number(testMatch?.[1]), passed: Number(passMatch?.[1]), exitCode: 0 };
if (!nodeTests.total || nodeTests.total !== nodeTests.passed) {
  throw new Error("Node test totals were not fully passing.");
}
const finalReport = {
  schemaVersion: 1,
  pass: true,
  nodeTests,
  pipelineValidation,
  modelValidation,
  geometry: {
    digest: geometry.canonicalGeometryDigest,
    boundsMm: [50, 31, 12],
    thicknessStackMm: geometry.dimensions.thicknessStack,
    topPlaneZMm: geometry.dimensions.bottomTopPlaneZMm,
    topPlaneMaximumDeviationMm: geometry.topPlane.maximumDeviationMm,
    axisBossProtrusionMm: geometry.dimensions.axisBossProtrusionMm,
    carrierClearanceBelowPlaneMm: geometry.carrierPacking.clearanceBelowPlaneMm,
    denseSweepSamples: geometry.denseSweep.sampleCount,
    nonmanifoldEdges: geometry.nonmanifoldEdges,
    invalidGeometricTangents: Object.fromEntries(
      Object.entries(geometry.uvTangentAudit).map(([name, value]) => [name, value.invalidGeometricTangents])
    )
  },
  blender: {
    pass: blender.pass,
    version: blender.blenderVersion,
    objectCount: blender.objectCount,
    invalidPolygonNormals: blender.invalidPolygonNormals,
    uvLayerCounts: blender.uvLayerCounts,
    animatedObjects: blender.animatedObjects
  },
  browser: {
    pass: browser.pass,
    desktopWidthPx: 1440,
    mobileWidthPx: 390,
    fixedTabs: browser.desktop.tabLabels,
    roadmapCount: browser.desktop.roadmapCount,
    currentGate: browser.desktop.currentGate,
    approvedCount: browser.desktop.approvedCount,
    glbLoaded: browser.viewer.open,
    reload: browser.reload,
    staleHistory: browser.stale,
    sourcePlayback: browser.sourcePlayback,
    runtimeExceptionCount: browser.runtimeExceptionCount,
    loadingFailureCount: browser.loadingFailureCount
  },
  hashes: {
    mechanismContractSha256: geometry.contractSha256,
    gate05SourceSha256: geometry.gate05Source.sha256,
    gate06BlendSha256: sha256File(path.join(here, "magnetic-slide-tile-geometry-r004.blend")),
    gate06GlbSha256: sha256File(glbPath)
  },
  syntax: { javascript: "pass", python: "pass", html5: "pass" },
  scope: {
    materials: false,
    simulator: false,
    unity: false,
    buildInstallOrDevice: false,
    oldShippingModelDefault: true
  }
};
const finalPath = path.join(here, "final-validation.json");
fs.writeFileSync(finalPath, `${JSON.stringify(finalReport, null, 2)}\n`);

const current = loadManifest("magnetic-slide-tile");
const currentGate06 = current.stages.find((stage) => stage.id === "06-geometry");
const definitions = [
  ["magnetic-slide-tile-geometry-browser-report-r004", "browser-validation", path.join(here, "browser-workspace-validation.json"), "validation"],
  ["magnetic-slide-tile-geometry-browser-test-r004", "browser-test", path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate06.mjs"), "process"],
  ["magnetic-slide-tile-geometry-workbench-preview-r004", "workbench-preview", path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate06-rev4-persistent-workbench.png"), "validation"],
  ["magnetic-slide-tile-geometry-workbench-focused-r004", "workbench-focused-preview", path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate06-rev4-workbench-focused.png"), "validation"],
  ["magnetic-slide-tile-geometry-final-validation-r004", "final-validation", finalPath, "validation"],
  ["magnetic-slide-tile-gate06-implementation-status-final", "implementation-status", path.join(repoRoot, "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md"), "process"]
];
const sourceAssetIds = [
  "magnetic-slide-tile-geometry-validation-r004",
  "magnetic-slide-tile-geometry-audit-r004",
  "magnetic-slide-tile-geometry-blend-r004",
  "magnetic-slide-tile-geometry-interactive-r004"
];
for (const [id, slot, absolute, role] of definitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing final Gate 06 evidence ${absolute}.`);
  current.assets.push({
    id,
    stageId: "06-geometry",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: role === "validation" ? "Gate 06 validation" : "fidgeting-model-pipeline",
      version: "4",
      recipe: "Gate 06 rev 4 final browser, geometry and pipeline validation"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: geometry.contractSha256,
      gate05SourceSha256: geometry.gate05Source.sha256,
      geometryDigest: geometry.canonicalGeometryDigest,
      simulatorUsed: false,
      unityUsed: false
    },
    sourceAssetIds,
    sourceClaimIds: []
  });
  currentGate06.artifactIds.push(id);
}
currentGate06.validations.push(
  {
    id: "persistent-workbench-rev4",
    status: "pass",
    evidence: "Desktop and 390 px mobile passed seven fixed tabs, 12-gate roadmap, Gate 06 GLB, modal, reload, deep links, browser history, stale evidence and source playback with 0 runtime/loading failures."
  },
  {
    id: "full-final-validation-rev4",
    status: "pass",
    evidence: `${nodeTests.passed}/${nodeTests.total} Node tests plus pipeline, model, browser, GLB, Blender, syntax and HTML checks passed.`
  }
);
current.currentState.workbench = "persistent-seven-tab-memory-route-enabled-default-gate06-browser-validated";
current.currentState.visualApproval = "gate06-rev4-ready-for-review-visual-approval-pending-not-pushed";
current.revision += 1;
current.updatedAt = new Date().toISOString();
const saved = saveManifest(current, {
  id: crypto.randomUUID(),
  type: "gate06-full-validation-passed",
  modelId: "magnetic-slide-tile",
  manifestRevision: current.revision,
  timestamp: current.updatedAt,
  finalValidationAssetId: "magnetic-slide-tile-geometry-final-validation-r004",
  browserReportAssetId: "magnetic-slide-tile-geometry-browser-report-r004",
  screenshotAssetIds: [
    "magnetic-slide-tile-geometry-workbench-preview-r004",
    "magnetic-slide-tile-geometry-workbench-focused-r004"
  ],
  nodeTests,
  geometryDigest: geometry.canonicalGeometryDigest,
  browserPass: true,
  blenderAuditPass: true,
  visualApprovalPending: true,
  unityChanged: false,
  deviceWork: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate06: saved.stages[5].status,
  nodeTests,
  geometryDigest: geometry.canonicalGeometryDigest,
  browserPass: true
}, null, 2));

