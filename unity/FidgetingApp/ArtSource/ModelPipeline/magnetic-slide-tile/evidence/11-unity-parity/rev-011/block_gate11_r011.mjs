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
const gate11 = manifest.stages.find((stage) => stage.id === "11-unity-parity");
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
if (
  manifest.revision !== 252
  || gate11?.revision !== 11
  || gate11?.status !== "ready_for_review"
) {
  throw new Error("Expected Gate 11 rev 11 ready state at pipeline rev 252.");
}

const reportPath =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/11-unity-parity/rev-011/parity-validation.json";
const report = JSON.parse(fs.readFileSync(resolveRepoPath(reportPath), "utf8"));
if (report.pass || report.humanInspection.status !== "failed") {
  throw new Error("Expected strict parity and human inspection failure.");
}
const reportAsset = manifest.assets.find(
  (asset) => asset.id === "magnetic-slide-tile-unity-parity-parity-report-r011");
reportAsset.sha256 = sha256File(resolveRepoPath(reportPath));
reportAsset.sizeBytes = fs.statSync(resolveRepoPath(reportPath)).size;

gate11.status = "draft";
gate11.decision = null;
gate11.readiness = {
  ready: false,
  blockers: [
    "Unity top and side remain visibly darker than the approved GLB.",
    "Silver hotspot shape and area do not match the approved GLB.",
  ],
  note: "Import, geometry, motion, tests, and recording pass. Visual parity blocks review.",
};
gate11.unityParitySpec.reviewStatus = "blocked-not-ready-for-review";
gate11.unityParitySpec.reviewQuestion = null;
gate11.unityParitySpec.parityMetrics = report;
gate11.unityParitySpec.deliveryState.visualApproval = "blocked-not-requested";
gate12.status = "blocked";
gate12.decision = null;
gate12.staleReason =
  "Gate 11 rev 11 visual parity failed. Gate 12 remains blocked and prior rejection stays preserved.";

const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`
    ).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((claim) => claim.stageId === stage.id)
    .map(stableJson);
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
manifest.currentState.visualApproval =
  "gate11-rev11-blocked-visible-parity-failed-not-pushed";
manifest.currentState.unityStatus =
  "gate11-rev11-import-motion-pass-visual-parity-blocked";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.diagnosis =
  "Gate 11 rev 11 geometry, import, endpoint motion, recording, and focused tests pass. Strict same-camera inspection finds darker Unity surfaces and mismatched silver highlights, so Gate 11 is not ready for review. Gate 12 remains blocked.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "stage-validation-blocked",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  revision: 11,
  failedChecks: Object.entries(report.checks)
    .filter(([, pass]) => !pass)
    .map(([name]) => name),
  humanInspection: report.humanInspection,
  gate12Status: gate12.status,
  buildInstallPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate11: saved.stages[10].status,
  gate12: saved.stages[11].status,
  blockers: saved.stages[10].readiness.blockers,
}, null, 2));
