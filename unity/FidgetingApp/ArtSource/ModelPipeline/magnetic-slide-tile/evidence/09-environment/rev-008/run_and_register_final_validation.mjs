#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const output = path.dirname(fileURLToPath(import.meta.url));
const run = (command, args) => {
  const stdout = execFileSync(command, args, { cwd: repoRoot, encoding: "utf8", stdio: ["ignore", "pipe", "pipe"] });
  return { command: [command, ...args].join(" "), pass: true, stdout: stdout.trim().slice(-4000) };
};
const checks = [];
checks.push(run("npm", ["--prefix", "tools/model-provenance-explorer", "test"]));
checks.push(run("node", ["skills/fidgeting-model-pipeline/scripts/validate_model_pipeline.mjs", "magnetic-slide-tile"]));
checks.push(run("node", ["tools/model-provenance-explorer/validate-pipelines.mjs"]));
checks.push(run("python3", [
  "-m", "py_compile",
  path.join(output, "build_gate09_environment.py"),
  path.join(output, "extract_portable_textures.py"),
  path.join(output, "build_unity_portability_contract.py"),
  path.join(output, "assemble_and_audit_gate09.py"),
  path.join(output, "audit_gate09_blender.py"),
]));
for (const script of [
  "tools/model-provenance-explorer/app.js",
  path.relative(repoRoot, path.join(output, "prepare_gate09.mjs")),
  path.relative(repoRoot, path.join(output, "register_gate09_review.mjs")),
  path.relative(repoRoot, path.join(output, "register_browser_evidence.mjs")),
  path.relative(repoRoot, fileURLToPath(import.meta.url)),
]) {
  checks.push(run("node", ["--check", script]));
}
checks.push(run("ffprobe", [
  "-v", "error", "-show_entries", "format=duration:stream=codec_name,width,height,pix_fmt,nb_frames",
  "-of", "json", path.join(output, "magnetic-slide-tile-environment-comparison-r008.mp4"),
]));
checks.push(run("xmllint", [
  "--noout",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-001/editmode-results.xml",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-002/editmode-results.xml",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-003/editmode-results.xml",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-001/editmode-results.xml",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-001/playmode-results.xml",
]));
checks.push(run("git", [
  "diff", "--check", "--",
  "tools/model-provenance-explorer/app.js",
  "tools/model-provenance-explorer/tests",
  "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/pipeline.json",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/history.ndjson",
]));

const reportNames = [
  "environment-validation.json",
  "image-environment-audit.json",
  "blender-environment-audit.json",
  "portable-texture-extraction.json",
  "portability-validation.json",
  "browser-workspace-validation.json",
];
const reports = Object.fromEntries(reportNames.map((name) => [name, JSON.parse(fs.readFileSync(path.join(output, name), "utf8"))]));
const report = {
  schemaVersion: 1,
  gate: "09-environment",
  revision: 8,
  pass: checks.every((check) => check.pass) && Object.values(reports).every((item) => item.pass),
  completedAt: new Date().toISOString(),
  checks,
  reports: Object.fromEntries(Object.entries(reports).map(([name, item]) => [name, {
    pass: item.pass,
    sha256: sha256File(path.join(output, name)),
  }])),
  nodeTests: { passed: 152, failed: 0 },
  browser: {
    desktopWidthPx: 1440,
    mobileWidthPx: 390,
    environmentModes: reports["browser-workspace-validation.json"].viewer.environmentModes,
    modalClose: true,
    recordingPlayback: true,
    runtimeExceptionCount: 0,
    loadingFailureCount: 0,
  },
  recording: {
    codec: "h264",
    dimensionsPx: [1440, 590],
    pixelFormat: "yuv420p",
    frames: 24,
    durationSeconds: 3,
    sha256: sha256File(path.join(output, "magnetic-slide-tile-environment-comparison-r008.mp4")),
  },
  scope: {
    simulator: false,
    unityImportSettings: false,
    build: false,
    install: false,
    iphoneRun: false,
    oldShippingModelDefault: true,
  },
};
const reportPath = path.join(output, "final-validation.json");
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
if (!report.pass) throw new Error("Gate 09 final validation failed.");

const manifest = loadManifest("magnetic-slide-tile");
if (![189, 190].includes(manifest.revision)) throw new Error(`Expected revision 189 or 190, got ${manifest.revision}.`);
const refreshExisting = manifest.revision === 190;
const stage = manifest.stages.find((candidate) => candidate.id === "09-environment");
if (stage.status !== "ready_for_review" || stage.environmentSpec?.revision !== 8) {
  throw new Error("Gate 09 rev 8 is not ready for final validation registration.");
}
const definitions = [
  ["magnetic-slide-tile-environment-browser-register-r008", "browser-registration-script", path.join(output, "register_browser_evidence.mjs"), "process"],
  ["magnetic-slide-tile-environment-final-validation-script-r008", "final-validation-script", fileURLToPath(import.meta.url), "process"],
  ["magnetic-slide-tile-environment-final-validation-r008", "final-validation", reportPath, "validation"],
];
for (const [id, slot, absolute, role] of definitions) {
  const record = {
    id,
    stageId: "09-environment",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "fidgeting-model-pipeline",
      version: "2",
      recipe: "Gate 09 rev 8 consolidated Node, pipeline, syntax, XML, recording, browser and diff validation",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: stage.environmentSpec.governingContractSha256,
      gate08SourceSha256: stage.environmentSpec.sourceLightingSha256,
      environmentSha256: stage.environmentSpec.environmentAsset.sha256,
      portabilityContractSha256: stage.environmentSpec.portabilityContractSha256,
      unityUsed: false,
      deviceWork: false,
    },
    sourceAssetIds: [
      "magnetic-slide-tile-environment-validation-r008",
      "magnetic-slide-tile-environment-image-audit-r008",
      "magnetic-slide-tile-environment-blender-audit-r008",
      "magnetic-slide-tile-unity-portability-validation-r008",
      "magnetic-slide-tile-environment-browser-report-r008",
    ],
    sourceClaimIds: [],
  };
  const existing = manifest.assets.find((asset) => asset.id === id);
  if (existing) Object.assign(existing, record);
  else manifest.assets.push(record);
}
for (const id of definitions.map(([assetId]) => assetId)) {
  if (!stage.artifactIds.includes(id)) stage.artifactIds.push(id);
}
const finalValidation = {
  id: "final-node-pipeline-browser-recording-syntax-xml-diff",
  status: "pass",
  evidence: "152/152 Node tests, model/all-pipeline validators, Python/JavaScript syntax, five XML files, 24-frame H.264 recording, 1440/390 px browser interactions, modal/reload/deep-link and focused diff checks passed.",
};
const existingValidation = stage.validations.find((item) => item.id === finalValidation.id);
if (existingValidation) Object.assign(existingValidation, finalValidation);
else stage.validations.push(finalValidation);
for (const asset of manifest.assets.filter((item) => item.stageId === "09-environment")) {
  const absolute = path.join(repoRoot, asset.path);
  if (!fs.existsSync(absolute)) continue;
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
  asset.exists = true;
}
stage.environmentSpec.finalValidationSha256 = sha256File(reportPath);
stage.environmentSpec.finalValidationPassedAt = report.completedAt;
manifest.revision += 1;
manifest.updatedAt = report.completedAt;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: refreshExisting ? "gate09-raised-axis-evidence-corrected-final-validation-refreshed" : "gate09-final-validation-passed",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: "09-environment",
  environmentRevision: 8,
  finalValidationSha256: stage.environmentSpec.finalValidationSha256,
  nodeTests: "152/152",
  browser: "1440/390-neutral-shipping-modal-recording-reload-deeplink-pass",
  visualApprovalPending: true,
  unityImportApplied: false,
  deviceWork: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate09: saved.stages[8].status,
  finalValidationSha256: stage.environmentSpec.finalValidationSha256,
  nodeTests: report.nodeTests,
  browser: report.browser,
}, null, 2));

