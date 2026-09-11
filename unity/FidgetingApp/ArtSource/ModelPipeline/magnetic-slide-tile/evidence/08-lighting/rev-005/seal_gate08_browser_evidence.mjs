#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import {
  digestValues,
  loadManifest,
  resolveRepoPath,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const root = "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-005";
const manifest = loadManifest(modelId);
const stage = manifest.stages.find((item) => item.id === "08-lighting");
if (manifest.revision !== 233 || stage?.status !== "ready_for_review") {
  throw new Error("Expected finalized Gate 08 rev 5 at pipeline revision 233.");
}
for (const id of [
  `${modelId}-lighting-browser-report-r005`,
  `${modelId}-lighting-browser-screenshot-r005`,
]) {
  const asset = manifest.assets.find((item) => item.id === id);
  asset.sha256 = sha256File(resolveRepoPath(asset.path));
  asset.sizeBytes = fs.statSync(resolveRepoPath(asset.path)).size;
}
const scriptPath = `${root}/seal_gate08_browser_evidence.mjs`;
const seal = {
  id: `${modelId}-lighting-browser-seal-r005`,
  stageId: "08-lighting",
  slot: "browser-evidence-seal",
  path: scriptPath,
  sha256: sha256File(resolveRepoPath(scriptPath)),
  exists: true,
  sizeBytes: fs.statSync(resolveRepoPath(scriptPath)).size,
  role: "process",
  producer: {
    name: "Gate 08 rev 5 browser evidence seal",
    version: "Node.js",
    recipe: scriptPath,
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "browser-evidence-seal",
    assertedBy: "assistant",
    gate08Revision: 5,
    sourceMaterialSha256: stage.lightingSpec.sourceMaterialSha256,
    geometryDigest: stage.lightingSpec.geometryDigest,
    mechanismEvidenceContractSha256: stage.lightingSpec.mechanismContractSha256,
    note: "Seals the final desktop/mobile/modal/video/deep-link browser rerun.",
  },
  sourceAssetIds: [
    `${modelId}-lighting-browser-report-r005`,
    `${modelId}-lighting-browser-screenshot-r005`,
  ],
  sourceClaimIds: [],
};
manifest.assets.push(seal);
stage.artifactIds.push(seal.id);
const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims.filter((claim) => claim.stageId === current.id).map(stableJson);
  current.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claims]);
}
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate08-r005-browser-evidence-sealed",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "08-lighting",
  revision: 5,
  status: "ready_for_review",
  browserValidation: "desktop/mobile/modal/video/deep-link pass",
  visualApproval: "pending",
});
console.log(JSON.stringify({ revision: manifest.revision, gate08: stage.status, sealed: true }, null, 2));
