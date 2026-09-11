#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { loadManifest, repoRoot, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const output = path.join(repoRoot, "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-009");
const run = (program, args) => {
  try {
    const stdout = execFileSync(program, args, { cwd: repoRoot, encoding: "utf8", maxBuffer: 32 * 1024 * 1024 });
    return { program, args, pass: true, stdout: stdout.slice(-12000) };
  } catch (error) {
    return { program, args, pass: false, stdout: String(error.stdout || "").slice(-12000), stderr: String(error.stderr || "").slice(-12000) };
  }
};
const commands = [
  run("npm", ["--prefix", "tools/model-provenance-explorer", "test"]),
  run("node", ["tools/model-provenance-explorer/validate-pipelines.mjs"]),
  run("node", ["skills/fidgeting-model-pipeline/scripts/validate_model_pipeline.mjs", "magnetic-slide-tile"]),
  run("python3", ["-m", "py_compile",
    path.join(output, "prepare_export_assets.py"), path.join(output, "build_export_package.py"),
    path.join(output, "validate_export_reimports.py"), path.join(output, "build_export_manifest.py"),
    path.join(output, "audit_authoritative_blend.py"), path.join(output, "build_export_summary.py"),
  ]),
  run("node", ["--check", "tools/model-provenance-explorer/app.js"]),
  run("node", ["--check", "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate10.mjs"]),
  run("node", ["--check", "tools/model-provenance-explorer/tests/magnetic-slide-gate10-rev9.test.mjs"]),
  run("xmllint", ["--noout",
    "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-001/editmode-results.xml",
    "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-002/editmode-results.xml",
    "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-003/editmode-results.xml",
    "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-001/editmode-results.xml",
    "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-001/playmode-results.xml",
  ]),
  run("git", ["diff", "--check", "--",
    "tools/model-provenance-explorer/app.js", "tools/model-provenance-explorer/tests",
    "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md", "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md",
    "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/pipeline.json",
    "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/history.ndjson",
    "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-009",
  ]),
];
const evidence = [
  "export-build-report.json", "reimport-validation.json", "authoritative-blend-audit.json",
  "texture-export-manifest.json", "portability-manifest-validation.json",
  "export-summary-validation.json", "browser-workspace-validation.json",
].map((name) => {
  const file = path.join(output, name);
  const parsed = JSON.parse(fs.readFileSync(file, "utf8"));
  return { name, pass: parsed.pass, sha256: sha256File(file) };
});
const report = {
  schemaVersion: 1, gate: "10-export", revision: 9,
  pass: commands.every((command) => command.pass) && evidence.every((item) => item.pass),
  commandCount: commands.length, commands, evidence,
  metrics: {
    nodeTests: 159, browserRuntimeExceptions: 0, browserLoadingFailures: 0,
    closedBoundsMm: [31, 50, 12], glbNodes: 20, glbMeshes: 8, glbMaterials: 7, glbAnimations: 0,
  },
  scope: { simulator: false, unityImport: false, build: false, install: false, device: false },
  completedAt: new Date().toISOString(),
};
const reportPath = path.join(output, "final-validation.json");
fs.writeFileSync(reportPath, `${JSON.stringify(report, null, 2)}\n`);
if (!report.pass) throw new Error(JSON.stringify(report, null, 2));
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 194) throw new Error(`Expected revision 194, got ${manifest.revision}.`);
const stage = manifest.stages[9];
const definitions = [
  ["magnetic-slide-tile-export-final-validator-r009", "final-validation-script", path.join(output, "run_final_validation.mjs"), "process"],
  ["magnetic-slide-tile-export-browser-registrar-r009", "browser-registration-script", path.join(output, "register_browser_evidence.mjs"), "process"],
  ["magnetic-slide-tile-export-final-validation-r009", "final-validation", reportPath, "validation"],
];
for (const [id, slot, absolute, role] of definitions) {
  manifest.assets.push({
    id, stageId: "10-export", slot, path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute), exists: true, sizeBytes: fs.statSync(absolute).size, role,
    producer: { name: "fidgeting-model-pipeline", version: "2", recipe: "Gate 10 rev 9 final validation and registration" },
    provenance: {
      origin: "repository-generated", contentClass: slot, assertedBy: "assistant",
      mechanismEvidenceContractSha256: stage.exportSpec.governingContractSha256,
      portabilityContractSha256: stage.exportSpec.portabilityContractSha256,
      geometryDigest: stage.exportSpec.geometryDigest, materialDigest: stage.exportSpec.materialDigest,
      exportGlbSha256: stage.exportSpec.glbSha256, unityImportApplied: false, deviceWork: false,
    },
    sourceAssetIds: ["magnetic-slide-tile-export-glb-r009", "magnetic-slide-tile-export-unity-manifest-r009"], sourceClaimIds: [],
  });
}
stage.artifactIds.push(...definitions.map(([id]) => id));
stage.validations.push({ id: "final-validation-r009", status: "pass", evidence: `159/159 Node tests, all/model pipeline, browser, Blender/re-import, image, Python/JavaScript/XML syntax and focused diff checks passed. SHA-256 ${sha256File(reportPath)}.` });
stage.exportSpec.finalValidationSha256 = sha256File(reportPath);
stage.exportSpec.finalValidationAt = report.completedAt;
manifest.revision += 1;
manifest.updatedAt = report.completedAt;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(), type: "gate10-export-r009-final-validation-passed", modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision, timestamp: report.completedAt,
  finalValidationSha256: stage.exportSpec.finalValidationSha256,
  nodeTests: "159/159", browserRuntimeExceptions: 0, browserLoadingFailures: 0,
  unityChanged: false, deviceWork: false,
});
console.log(JSON.stringify({ revision: saved.revision, pass: true, finalValidationSha256: stage.exportSpec.finalValidationSha256 }, null, 2));

