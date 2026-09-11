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
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-009";
const manifest = loadManifest(modelId);
const stage = manifest.stages.find((item) => item.id === "11-unity-parity");
if (
  manifest.revision !== 200
  || manifest.currentStageId !== "11-unity-parity"
  || stage?.revision !== 9
  || stage?.status !== "ready_for_review"
) {
  throw new Error("Expected Gate 11 rev 9 ready-for-review at pipeline rev 200.");
}
const parity = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/parity-report.json`)));
const finalValidation = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/final-validation.json`)));
const browser = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/browser-validation.json`)));
if (!parity.pass || !finalValidation.pass || !browser.pass) {
  throw new Error("Current Gate 11 visual, final or browser evidence is not passing.");
}

const refreshPath = `${evidenceRoot}/refresh_gate11_r009.mjs`;
const refreshId = `${modelId}-unity-parity-final-refresh-r009`;
if (manifest.assets.some((asset) => asset.id === refreshId)) {
  throw new Error(`Asset already registered: ${refreshId}`);
}
const refreshAbsolute = resolveRepoPath(refreshPath);
manifest.assets.push({
  id: refreshId,
  stageId: "11-unity-parity",
  slot: "registration-source",
  path: refreshPath,
  sha256: sha256File(refreshAbsolute),
  exists: true,
  sizeBytes: fs.statSync(refreshAbsolute).size,
  role: "process",
  producer: {
    name: "Gate 11 final evidence refresh",
    version: "Node.js",
    recipe: refreshPath,
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "registration-source",
    assertedBy: "assistant",
    gate11Revision: 9,
    mechanismEvidenceContractSha256:
      "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea",
    note: "Refreshes the final EXR-visible-background Unity capture, tests and stable workbench evidence without changing Gate 12.",
  },
  sourceAssetIds: [
    "magnetic-slide-tile-unity-parity-environment-exr-r009",
    "magnetic-slide-tile-unity-parity-interactive-recording-r009",
  ],
  sourceClaimIds: [],
});
stage.artifactIds.push(refreshId);

for (const assetId of stage.artifactIds) {
  const asset = manifest.assets.find((candidate) => candidate.id === assetId);
  if (!asset) throw new Error(`Missing registered asset ${assetId}`);
  const absolute = resolveRepoPath(asset.path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing file ${asset.path}`);
  asset.sha256 = sha256File(absolute);
  asset.exists = true;
  asset.sizeBytes = fs.statSync(absolute).size;
}

stage.unityParitySpec.materialParity = parity.material;
stage.unityParitySpec.silhouetteParity = parity.visual;
stage.unityParitySpec.browserEvidence = {
  reviewUrl: browser.reviewUrl,
  desktop: browser.desktop,
  mobile: browser.mobile,
  recordingGate: browser.unlocked,
  runtimeExceptionCount: browser.runtimeExceptionCount,
  loadingFailureCount: browser.loadingFailureCount,
  screenshotAssetId:
    "magnetic-slide-tile-unity-parity-browser-workbench-r009",
};
const parityValidation = stage.validations.find(
  (item) => item.id === "matched-camera-parity");
parityValidation.evidence =
  `Silhouette IoU ${(parity.visual.silhouetteIoU * 100).toFixed(3)}%, `
  + `SSIM ${parity.visual.silhouetteSsim.toFixed(6)}, `
  + `edge max ${parity.visual.edgeDistancePixels.max.toFixed(3)} px; `
  + `blood-red ΔE00 ${parity.material.bloodRed.deltaE2000.toFixed(2)}, `
  + `bright reflection ΔE00 ${parity.material.brightReflection.deltaE2000.toFixed(2)}, `
  + `black ΔE00 ${parity.material.black.deltaE2000.toFixed(2)}; `
  + `highlight area error ${(parity.material.highlightCoverage.relativeError * 100).toFixed(2)}%, `
  + `centroid max-axis ${parity.material.highlightCoverage.centroidMaxAxisErrorPixels.toFixed(2)} px.`;
const browserValidation = stage.validations.find(
  (item) => item.id === "gate11-r009-browser-workbench");
browserValidation.evidence =
  "Desktop 1440×1000 and mobile 390×844 restore Gate 11/Unity routes with 12 gates and seven tabs. Approval stays disabled until the 6 s Unity recording ends, then persists across reload. Runtime/loading failures 0/0.";

const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((claim) => claim.stageId === current.id)
    .map(stableJson);
  current.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claims]);
}
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-evidence-refreshed",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  revision: 9,
  artifactIds: stage.artifactIds,
  note: "Locked final same-EXR Unity capture, focused tests and browser evidence.",
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate11: saved.stages[10].status,
  artifactCount: saved.stages[10].artifactIds.length,
  parity: saved.stages[10].unityParitySpec.materialParity.highlightCoverage,
}, null, 2));
