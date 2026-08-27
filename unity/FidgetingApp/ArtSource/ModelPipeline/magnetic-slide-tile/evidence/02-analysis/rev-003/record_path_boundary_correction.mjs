#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const manifest = loadManifest(modelId);
if (manifest.revision !== 112) throw new Error(`Expected manifest revision 112, got ${manifest.revision}.`);
const stage = manifest.stages[1];
if (stage.status !== "ready_for_review" || stage.analysisSpec?.revision !== 3) {
  throw new Error("Gate 02 rev 3 is not active.");
}
const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../..");
const targets = [
  ["slider-analysis-mechanism-board-builder-r003", "build_mechanism_analysis.py"],
  ["slider-analysis-video-registrar-r003", "register_video_analysis.mjs"],
];
for (const [assetId, filename] of targets) {
  const asset = manifest.assets.find((candidate) => candidate.id === assetId);
  if (!asset) throw new Error(`Missing registered asset: ${assetId}`);
  const absolute = path.join(here, filename);
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
  asset.exists = true;
}
const pathValidation = stage.validations.find((validation) => validation.id === "no-temporary-paths");
if (!pathValidation) throw new Error("Missing temporary-path validation.");
pathValidation.evidence =
  "All manifest, claim, frame, board, audio and proxy paths are repository-relative; no temporary filesystem path is cited.";

const scriptPath = fileURLToPath(import.meta.url);
const scriptId = "slider-analysis-path-boundary-correction-r003";
if (manifest.assets.some((asset) => asset.id === scriptId)) throw new Error("Correction already registered.");
manifest.assets.push({
  id: scriptId,
  stageId: "02-analysis",
  slot: "analysis-evidence",
  path: path.relative(repoRoot, scriptPath).split(path.sep).join("/"),
  sha256: sha256File(scriptPath),
  exists: true,
  sizeBytes: fs.statSync(scriptPath).size,
  role: "process",
  producer: {
    name: "fidgeting-model-pipeline",
    version: "1",
    recipe: "Revision-guarded path-boundary wording correction and registered-script hash refresh",
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "path-boundary-correction-record",
    assertedBy: "assistant",
    note: "移除新 Gate 02 输出中的临时文件系统路径字面引用；所有来源仍为仓库相对路径。",
  },
  sourceAssetIds: targets.map(([assetId]) => assetId),
});
stage.artifactIds.push(scriptId);

const digestValues = (values) => crypto.createHash("sha256").update(
  values.filter(Boolean).sort().join("\n")).digest("hex");
const stableJson = (value) => {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
};
for (let index = 0; index < manifest.stages.length; index += 1) {
  const candidate = manifest.stages[index];
  const hashes = candidate.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims.filter((claim) => claim.stageId === candidate.id).map(stableJson);
  candidate.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  candidate.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const event = {
  id: crypto.randomUUID(),
  type: "stage-video-analysis-path-boundary-corrected",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "02-analysis",
  analysisEvidenceRevision: 3,
  correctedAssetIds: targets.map(([assetId]) => assetId),
  correctionAssetId: scriptId,
  repositoryRelativePathsOnly: true,
  gateStatus: stage.status,
};
saveManifest(manifest, event);
console.log(JSON.stringify(event, null, 2));
