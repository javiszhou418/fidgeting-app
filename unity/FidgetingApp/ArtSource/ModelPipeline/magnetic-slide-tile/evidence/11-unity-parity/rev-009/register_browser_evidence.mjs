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
  manifest.revision !== 199
  || manifest.currentStageId !== "11-unity-parity"
  || stage?.revision !== 9
  || stage?.status !== "ready_for_review"
) {
  throw new Error("Expected Gate 11 rev 9 ready-for-review at pipeline rev 199.");
}
const validation = JSON.parse(
  fs.readFileSync(resolveRepoPath(`${evidenceRoot}/browser-validation.json`)));
if (!validation.pass) throw new Error("Gate 11 browser validation did not pass.");

const definitions = [
  [
    "browser-registrar",
    "registration-source",
    `${evidenceRoot}/register_browser_evidence.mjs`,
    "process",
  ],
  [
    "browser-test",
    "browser-validation-source",
    "tools/model-provenance-explorer/tests/browser-gate11-r009.mjs",
    "validation",
  ],
  [
    "browser-validation",
    "browser-validation",
    `${evidenceRoot}/browser-validation.json`,
    "validation",
  ],
  [
    "browser-workbench",
    "browser-workbench",
    "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate11-r009-workbench.png",
    "unity-render",
  ],
];
const sourceAssetIds = [
  "magnetic-slide-tile-unity-parity-interactive-recording-r009",
  "magnetic-slide-tile-unity-parity-parity-board-r009",
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-unity-parity-${suffix}-r009`,
    stageId: "11-unity-parity",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Model Provenance Explorer CDP validation",
      version: "Chrome / Node.js",
      recipe: "tools/model-provenance-explorer/tests/browser-gate11-r009.mjs",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate11Revision: 9,
      mechanismEvidenceContractSha256:
        "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea",
      note: "Stable Gate 11 Unity tab, recording gate, reload persistence and mobile layout evidence.",
    },
    sourceAssetIds,
    sourceClaimIds: [],
  };
});
for (const record of records) {
  if (manifest.assets.some((asset) => asset.id === record.id)) {
    throw new Error(`Asset already registered: ${record.id}`);
  }
}
manifest.assets.push(...records);
stage.artifactIds.push(...records.map((record) => record.id));
stage.validations.push({
  id: "gate11-r009-browser-workbench",
  status: "pass",
  evidence:
    "Desktop 1440×1000 and mobile 390×844 restore Gate 11/Unity routes with 12 gates and seven tabs. Approval stays disabled until the 6 s Unity recording ends, then persists across reload. Runtime/loading failures 0/0.",
});
stage.unityParitySpec.browserEvidence = {
  reviewUrl: validation.reviewUrl,
  desktop: validation.desktop,
  mobile: validation.mobile,
  recordingGate: validation.unlocked,
  runtimeExceptionCount: validation.runtimeExceptionCount,
  loadingFailureCount: validation.loadingFailureCount,
  screenshotAssetId: `${modelId}-unity-parity-browser-workbench-r009`,
};

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
  type: "stage-evidence-revised",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  revision: 9,
  artifactIds: records.map((record) => record.id),
  note: "Registered stable workbench, recording-gate and mobile browser evidence.",
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate11: saved.stages[10].status,
  artifacts: records.map((record) => record.id),
}, null, 2));
