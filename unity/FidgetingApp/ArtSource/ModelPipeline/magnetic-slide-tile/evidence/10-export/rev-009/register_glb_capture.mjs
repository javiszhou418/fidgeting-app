#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, repoRoot, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 195) throw new Error(`Expected revision 195, got ${manifest.revision}.`);
const stage = manifest.stages[9];
const definitions = [
  ["magnetic-slide-tile-export-glb-capture-script-r009", "glb-capture-script", path.join(repoRoot, "tools/model-provenance-explorer/tests/capture-gate10-glb-viewer.mjs"), "process"],
  ["magnetic-slide-tile-export-glb-viewer-capture-r009", "glb-viewer-capture", path.join(repoRoot, "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate10-rev9-glb-viewer.png"), "analysis"],
  ["magnetic-slide-tile-export-glb-capture-registrar-r009", "glb-capture-registration", fileURLToPath(import.meta.url), "process"],
];
for (const [id, slot, absolute, role] of definitions) {
  manifest.assets.push({
    id, stageId: "10-export", slot, path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute), exists: true, sizeBytes: fs.statSync(absolute).size, role,
    producer: { name: "Chrome CDP / fidgeting-model-pipeline", version: "Gate 10 rev 9", recipe: "Shipping workbench capture of the real exported GLB" },
    provenance: {
      origin: "repository-generated", contentClass: slot, assertedBy: "assistant",
      mechanismEvidenceContractSha256: stage.exportSpec.governingContractSha256,
      portabilityContractSha256: stage.exportSpec.portabilityContractSha256,
      geometryDigest: stage.exportSpec.geometryDigest, materialDigest: stage.exportSpec.materialDigest,
      exportGlbSha256: stage.exportSpec.glbSha256, unityImportApplied: false, deviceWork: false,
    },
    sourceAssetIds: ["magnetic-slide-tile-export-glb-r009"], sourceClaimIds: [],
  });
}
stage.artifactIds.push(...definitions.map(([id]) => id));
stage.reviewArtifactIds.push("magnetic-slide-tile-export-glb-viewer-capture-r009");
stage.validations.push({ id: "real-glb-viewer-capture-r009", status: "pass", evidence: `Real exported GLB rendered in the shipping workbench; screenshot SHA-256 ${sha256File(definitions[1][2])}. Interactive GLB remains the primary evidence.` });
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(), type: "gate10-export-r009-glb-capture-registered", modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision, timestamp: manifest.updatedAt,
  exportGlbSha256: stage.exportSpec.glbSha256,
  screenshotSha256: sha256File(definitions[1][2]), unityChanged: false, deviceWork: false,
});
console.log(JSON.stringify({ revision: saved.revision, screenshot: definitions[1][2] }, null, 2));

