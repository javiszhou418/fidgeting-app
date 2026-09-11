#!/usr/bin/env node
import { createModelPipeline, pipelineDirectory } from "../../../tools/model-provenance-explorer/pipeline-core.mjs";

const args = process.argv.slice(2);
const value = (name) => {
  const index = args.indexOf(name);
  return index >= 0 ? args[index + 1] : null;
};
const modelId = value("--model-id");
const name = value("--name");
const scenePath = value("--scene") || "";
if (!modelId || !name) {
  console.error("Usage: init_model_pipeline.mjs --model-id <id> --name <display name> [--mechanism rotor] [--scene <repo-relative path>]");
  process.exit(2);
}
const mechanism = value("--mechanism") || "rotor";
const directory = pipelineDirectory(modelId);
try {
  createModelPipeline({ id: modelId, name, mechanism, scenePath });
} catch (error) {
  console.error(error.message);
  process.exit(1);
}
console.log(directory);
