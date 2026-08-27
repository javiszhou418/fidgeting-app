#!/usr/bin/env node
import { deriveManifest, loadManifest, validateManifest } from "../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = process.argv[2];
if (!modelId) {
  console.error("Usage: validate_model_pipeline.mjs <model-id>");
  process.exit(2);
}
const manifest = loadManifest(modelId);
const errors = validateManifest(manifest);
const derived = deriveManifest(manifest);
const missingFiles = manifest.assets.filter((asset) => asset.exists === false).map((asset) => asset.path);
const unhashed = manifest.assets.filter((asset) => !asset.sha256).map((asset) => asset.path);
console.log(JSON.stringify({ modelId, revision: manifest.revision, shippingReady: derived.derived.shippingReady, approved: `${derived.derived.approvedCount}/12`, earliestProblem: derived.derived.earliestProblem, errors, missingFiles, unhashed }, null, 2));
if (errors.length || missingFiles.length || unhashed.length) process.exitCode = 1;
