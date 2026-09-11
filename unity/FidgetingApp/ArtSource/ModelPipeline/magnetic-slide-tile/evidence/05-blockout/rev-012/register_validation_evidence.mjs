#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { loadManifest, repoRoot, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const stage = manifest.stages[4];
if (manifest.revision !== 213 || stage.revision !== 12 || stage.status !== "ready_for_review")
  throw new Error(`Expected pipeline 213 Gate 05 rev 12 ready_for_review.`);
const contract = stage.blockoutSpec.governingContractSha256;
const source = ["magnetic-slide-g05-r012-blend", "slider-analysis-mechanism-evidence-contract-r016"];
const additions = [
  ["magnetic-slide-g05-r012-blender-audit-script", "audit-script", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/audit_corrected_blend.py", "process"],
  ["magnetic-slide-g05-r012-blender-audit", "blender-audit", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/blender-audit.json", "validation"],
  ["magnetic-slide-g05-r012-browser-test", "browser-test", "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate05-r012.mjs", "process"],
  ["magnetic-slide-g05-r012-browser-report", "browser-validation", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/browser-workspace-validation.json", "validation"],
  ["magnetic-slide-g05-r012-workbench", "workbench-preview", "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev12-persistent-workbench.png", "unity-render"],
  ["magnetic-slide-g05-r012-workbench-focused", "workbench-focused-preview", "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev12-workbench-focused.png", "unity-render"],
  ["magnetic-slide-g05-r012-node-test", "node-test", "tools/model-provenance-explorer/tests/magnetic-slide-gate05-rev12.test.mjs", "process"],
  ["magnetic-slide-g05-r012-validation-register", "registration-script", "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/register_validation_evidence.mjs", "process"],
];
const ids = new Set(additions.map(([id]) => id));
manifest.assets = manifest.assets.filter(asset => !ids.has(asset.id));
for (const [id, slot, relative, role] of additions) {
  const absolute = path.join(repoRoot, relative);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${relative}`);
  manifest.assets.push({
    id, stageId: "05-blockout", slot, path: relative, sha256: sha256File(absolute), exists: true,
    sizeBytes: fs.statSync(absolute).size, role,
    producer: { name: slot.startsWith("browser") || slot.includes("workbench") ? "Chrome CDP" : "fidgeting-model-pipeline", version: "Gate 05 rev 12", recipe: "fixed-axis geometry validation" },
    provenance: { origin: "repository-generated", contentClass: slot, assertedBy: "assistant", mechanismEvidenceContractSha256: contract, finalMaterialsApplied: false, buildInstallPhone: false },
    sourceAssetIds: source, sourceClaimIds: [],
  });
}
for (const asset of manifest.assets.filter(item => item.id.startsWith("magnetic-slide-g05-r012-"))) {
  const absolute = path.join(repoRoot, asset.path);
  if (!fs.existsSync(absolute)) continue;
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
}
const app = path.join(repoRoot, "tools/model-provenance-explorer/app.js");
for (const asset of manifest.assets.filter(item => item.path === "tools/model-provenance-explorer/app.js")) {
  asset.sha256 = sha256File(app);
  asset.sizeBytes = fs.statSync(app).size;
}
stage.artifactIds.push(...additions.map(([id]) => id).filter(id => !stage.artifactIds.includes(id)));
stage.validations.push(
  { id: "saved-blend-audit", status: "pass", evidence: "Independent Blender reopen confirms one pivot, clean clay-only source, two-mesh product whitelist and no old debug meshes." },
  { id: "browser-desktop-mobile", status: "pass", evidence: "Desktop and 390×844 mobile routes, GLB, Unity video modal, history, reload and stale downstream tabs pass with zero runtime/loading failures." },
);
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(), type: "gate05-fixed-axis-validation-registered", modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision, timestamp: manifest.updatedAt, browser: "pass", blenderAudit: "pass",
  visualApprovalPending: true, buildInstallPhone: false,
});
console.log(JSON.stringify({ revision: saved.revision, artifacts: saved.stages[4].artifactIds.length }, null, 2));

