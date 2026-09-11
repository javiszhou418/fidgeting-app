#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  digestValues,
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const stage = manifest.stages.find((item) => item.id === "10-export");
if (manifest.revision !== 248 || stage?.exportSpec?.revision !== 11 || stage.status !== "draft") {
  throw new Error("Expected draft Gate 10 rev 11 at pipeline revision 248.");
}
const build = JSON.parse(fs.readFileSync(
  path.join(repoRoot, "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-011/portable-glb-build-validation.json"),
  "utf8",
));
const manifestAudit = JSON.parse(fs.readFileSync(
  path.join(repoRoot, "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/10-export/rev-011/export-manifest-validation.json"),
  "utf8",
));
for (const asset of manifest.assets.filter((item) => item.stageId === "10-export" && item.id.endsWith("-r011"))) {
  const absolute = path.join(repoRoot, asset.path);
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
  asset.exists = true;
}
stage.exportSpec.glbSha256 = build.outputs.glb.sha256;
stage.exportSpec.exportManifestSha256 = manifestAudit.manifest.sha256;
stage.exportSpec.authoritativeBlendSha256 = build.outputs.blend.sha256;
stage.exportSpec.fbxSha256 = build.outputs.fbx.sha256;
stage.exportSpec.collisionSha256 = build.outputs.collision.sha256;
stage.exportSpec.hierarchyMotionSha256 = build.outputs.hierarchyMotion.sha256;
stage.exportSpec.unityImportContractSha256 = build.outputs.unityImportContract.sha256;
stage.outputDigest = digestValues([
  build.outputs.blend.sha256,
  build.outputs.fbx.sha256,
  build.outputs.glb.sha256,
  build.outputs.collision.sha256,
  manifestAudit.manifest.sha256,
]);
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate10-rev11-draft-artifact-hashes-refreshed",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  correctedGlbSha256: build.outputs.glb.sha256,
  reason: "Restore portable double-sided rendering for mirrored transform ownership and cache-bust the corrected GLB.",
  geometryChanged: false,
  unityUsed: false,
  deviceWork: false,
});
console.log(JSON.stringify({ revision: saved.revision, glbSha256: stage.exportSpec.glbSha256 }, null, 2));
