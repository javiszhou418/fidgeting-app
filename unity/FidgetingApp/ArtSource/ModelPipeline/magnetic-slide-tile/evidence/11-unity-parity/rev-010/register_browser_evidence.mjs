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

const manifest = loadManifest("magnetic-slide-tile");
const stage = manifest.stages.find((item) => item.id === "11-unity-parity");
if (
  manifest.revision !== 204
  || stage?.revision !== 10
  || stage?.status !== "draft"
  || stage?.unityParitySpec?.reviewStatus !== "blocked-not-ready-for-review"
) {
  throw new Error("Expected blocked Gate 11 rev 10 at pipeline rev 204.");
}
const definitions = [
  {
    id: "magnetic-slide-tile-unity-parity-browser-validation-r010",
    slot: "browser-validation",
    path: "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-010/browser-validation.json",
  },
  {
    id: "magnetic-slide-tile-unity-parity-workbench-screenshot-r010",
    slot: "workbench-screenshot",
    path: "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate11-r010-blocked-workbench.png",
  },
  {
    id: "magnetic-slide-tile-unity-parity-browser-test-r010",
    slot: "browser-test-source",
    path: "tools/model-provenance-explorer/tests/browser-gate11-r010.mjs",
  },
  {
    id: "magnetic-slide-tile-unity-parity-node-test-r010",
    slot: "node-test-source",
    path: "tools/model-provenance-explorer/tests/magnetic-slide-gate11-rev10.test.mjs",
  },
];
const records = definitions.map((definition) => {
  const absolute = resolveRepoPath(definition.path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${definition.path}`);
  return {
    ...definition,
    stageId: "11-unity-parity",
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role: "validation",
    producer: {
      name: "Model Provenance Explorer",
      version: "2",
      recipe: "tools/model-provenance-explorer/tests/browser-gate11-r010.mjs",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: definition.slot,
      assertedBy: "assistant",
      gate11Revision: 10,
      mechanismEvidenceContractSha256:
        "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea",
      note: "Blocked-state desktop, mobile, deep-link and modal validation.",
    },
    sourceAssetIds: [
      "magnetic-slide-tile-unity-parity-interactive-recording-r010",
      "magnetic-slide-tile-unity-parity-full-frame-board-r010",
    ],
    sourceClaimIds: [],
  };
});
for (const record of records) {
  if (manifest.assets.some((asset) => asset.id === record.id)) {
    throw new Error(`Asset already registered: ${record.id}`);
  }
}
const browser = JSON.parse(
  fs.readFileSync(resolveRepoPath(definitions[0].path), "utf8"));
if (
  !browser.pass
  || browser.desktop.approvalAbsent !== true
  || browser.mobile.approvalAbsent !== true
  || browser.runtimeExceptionCount !== 0
  || browser.loadingFailureCount !== 0
) {
  throw new Error("Blocked workbench validation did not pass.");
}

manifest.assets.push(...records);
stage.artifactIds.push(...records.map((record) => record.id));
stage.validations.push({
  id: "blocked-workbench-desktop-mobile-modal",
  status: "pass",
  evidence:
    "Desktop 1440×1000 and mobile 390×844 preserve 12 gates, seven tabs, three blockers, recording deep-link/modal return and no approval control; runtime/loading failures 0/0.",
});
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
  type: "stage-validation-added",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  revision: 10,
  status: "draft",
  artifactIds: records.map((record) => record.id),
  approvalControlPresent: false,
  runtimeExceptionCount: 0,
  loadingFailureCount: 0,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate11: saved.stages[10].status,
  gate12: saved.stages[11].status,
  browser: browser.pass,
}, null, 2));
