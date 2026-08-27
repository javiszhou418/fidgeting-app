import { deriveManifest, listModelIds, loadManifest, refreshManifest, validateManifest } from "./pipeline-core.mjs";

const refresh = process.argv.includes("--refresh");
let failed = false;
const report = [];

for (const modelId of listModelIds()) {
  let manifest = loadManifest(modelId);
  if (refresh) manifest = refreshManifest(modelId, manifest.revision);
  const errors = validateManifest(manifest);
  const derived = deriveManifest(manifest);
  const missingFiles = manifest.assets.filter((asset) => asset.exists === false).map((asset) => asset.path);
  const unhashed = manifest.assets.filter((asset) => !asset.sha256).map((asset) => asset.path);
  if (errors.length || missingFiles.length || unhashed.length) failed = true;
  report.push({
    modelId,
    revision: manifest.revision,
    approved: `${derived.derived.approvedCount}/12`,
    earliestProblem: derived.derived.earliestProblem,
    errors,
    missingFiles,
    unhashed
  });
}

console.log(JSON.stringify({ refresh, models: report }, null, 2));
if (failed) process.exitCode = 1;
