#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { createEmptyStages } from "../../../tools/model-provenance-explorer/pipeline-contract.mjs";
import { pipelineDirectory, saveManifest } from "../../../tools/model-provenance-explorer/pipeline-core.mjs";

const args = process.argv.slice(2);
const value = (name) => {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : null;
};
const modelId = value("--model-id");
const name = value("--name");
const scenePath = value("--scene") || "";
if (!modelId || !name) {
  console.error("Usage: init_model_pipeline.mjs --model-id <id> --name <display name> [--scene <repo-relative path>]");
  process.exit(2);
}
const directory = pipelineDirectory(modelId);
if (fs.existsSync(path.join(directory, "pipeline.json"))) {
  console.error(`Pipeline already exists: ${directory}`);
  process.exit(1);
}
const now = new Date().toISOString();
const manifest = {
  schemaVersion: 1,
  revision: 1,
  createdAt: now,
  updatedAt: now,
  model: { id: modelId, name, mechanism: "rotor", status: "candidate", scenePath },
  route: { primary: "blender-cli", rodinPolicy: "concept-only", note: "Mechanical model default." },
  currentState: {
    rebuildRequested: true,
    shippingAssetUnchanged: true,
    visualApproval: "pending",
    deviceStatus: "not-approved",
    diagnosis: "New pipeline; begin with original reference intake."
  },
  assets: [], claims: [], stages: createEmptyStages(), issues: []
};
saveManifest(manifest, { id: `init-${modelId}-v1`, type: "pipeline-created", modelId, manifestRevision: 1, timestamp: now });
console.log(directory);
