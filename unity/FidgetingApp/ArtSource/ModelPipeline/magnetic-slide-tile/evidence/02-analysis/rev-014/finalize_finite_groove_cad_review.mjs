#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../../");
const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 145) throw new Error(`Expected revision 145, got ${manifest.revision}.`);
const stage = manifest.stages.find((candidate) => candidate.id === "02-analysis");
if (stage.analysisSpec?.revision !== 14) throw new Error("Gate 02 rev 14 must be active.");
const configPath = path.join(here, "interactive-cad-geometry-config.json");
const contractPath = path.join(here, "mechanism-evidence-contract.json");
const contractHash = sha256File(contractPath);
const refreshPaths = new Set([
  "skills/fidgeting-model-pipeline/references/pipeline-contract.md",
  "tools/model-provenance-explorer/app.js",
  "tools/model-provenance-explorer/styles.css",
  "tools/model-provenance-explorer/mechanism-cad-core.mjs",
  "tools/model-provenance-explorer/pipeline-core.mjs",
  "tools/model-provenance-explorer/tests/mechanism-cad.test.mjs",
  "tools/model-provenance-explorer/tests/mechanism-evidence-contract.test.mjs",
  "tools/model-provenance-explorer/tests/pipeline-core.test.mjs",
  "tools/model-provenance-explorer/tests/browser-cdp-smoke.mjs",
  "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md",
  path.relative(repoRoot, configPath).split(path.sep).join("/"),
  path.relative(repoRoot, contractPath).split(path.sep).join("/"),
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-014/register_finite_groove_cad_review.mjs",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-014/seal_finite_groove_cad_review.mjs",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/02-analysis/rev-014/validation-report.json",
  "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate02-rev14-finite-groove-sweep-cad.png"
]);
for (const asset of manifest.assets) {
  if (!refreshPaths.has(asset.path)) continue;
  const absolute = path.join(repoRoot, asset.path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing final asset ${asset.path}`);
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
  asset.exists = true;
}
const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
stage.analysisSpec.contractSha256 = contractHash;
stage.analysisSpec.approvalSpec.requiredMilestones = config.cadApprovalChecklist;
stage.status = "ready_for_review";
stage.staleReason = null;
stage.readiness = { ready: true, blockers: [], note: "Complete eleven CAD checks including finite endpoints, synchronized views and the 360-degree swept envelope. Simulator stays locked." };
stage.outputDigest = crypto.createHash("sha256")
  .update(stage.artifactIds.map((id) => manifest.assets.find((asset) => asset.id === id)?.sha256).filter(Boolean).sort().join("\n"))
  .digest("hex");
const timestamp = new Date().toISOString();
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate02-rev14-finite-groove-interactive-cad-subapproval-pending";
manifest.currentState.diagnosis = "Gate 02 rev 14 finite-groove CAD, synchronized views and 360-degree swept envelope are validated and ready for interactive review. Simulator and downstream generation remain locked.";
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-interactive-cad-finite-groove-review-finalized",
  modelId: manifest.model.id,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "02-analysis",
  analysisEvidenceRevision: 14,
  contractHash,
  cadArtifactId: stage.analysisSpec.cadArtifactId,
  cadArtifactHash: manifest.assets.find((asset) => asset.id === stage.analysisSpec.cadArtifactId).sha256,
  previewAssetId: "slider-analysis-finite-groove-sweep-cad-preview-r014",
  previewHash: manifest.assets.find((asset) => asset.id === "slider-analysis-finite-groove-sweep-cad-preview-r014").sha256,
  requiredMilestones: config.cadApprovalChecklist,
  simulatorState: "locked-not-generated",
  blenderUnityBuildInstallPhone: "not-started"
});
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  contractHash,
  cadArtifactHash: manifest.assets.find((asset) => asset.id === stage.analysisSpec.cadArtifactId).sha256,
  requiredMilestones: config.cadApprovalChecklist.length
}, null, 2));
