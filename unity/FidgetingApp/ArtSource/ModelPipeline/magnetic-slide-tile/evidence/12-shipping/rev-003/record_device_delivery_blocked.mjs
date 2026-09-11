#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  digestValues,
  loadManifest,
  resolveRepoPath,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/12-shipping/rev-003";
const candidateRoot =
  "unity/FidgetingApp/Assets/_EDC/Candidates/MagneticSlideTileGate12R002";
const jobId =
  "magnetic-slide-g12-r003-20260831T093320Z-dc0940be";
const jobRoot = `${evidenceRoot}/device-delivery/${jobId}`;
const manifest = loadManifest(modelId);
const gate12 = manifest.stages.find((stage) => stage.id === "12-shipping");
if (
  gate12?.status !== "approved"
  || gate12?.decision?.notes !== "这个是对的"
) {
  throw new Error("Expected approved Gate 12 rev 3.");
}

const promotion = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/shipping-promotion-report.json`), "utf8"));
const device = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${jobRoot}/device-details.json`), "utf8"));
if (
  !promotion.pass
  || !promotion.candidateDefaultActive
  || promotion.fallbackDefaultActive
  || device.result?.connectionProperties?.tunnelState !== "connected"
  || device.result?.deviceProperties?.ddiServicesAvailable !== false
) {
  throw new Error("Promotion or device blocker evidence is inconsistent.");
}

const job = Object.fromEntries(
  fs.readFileSync(resolveRepoPath(`${jobRoot}/job.env`), "utf8")
    .trim().split("\n").map((line) => {
      const separator = line.indexOf("=");
      return [line.slice(0, separator), line.slice(separator + 1)];
    }));
if (fs.existsSync(job.exportPath))
  throw new Error("Blocked device preflight must not leave an export.");

const definitions = [
  ["approval-source", "approval-source",
    `${evidenceRoot}/approve_gate12_r003.mjs`, "process"],
  ["delivery-recorder", "delivery-registration-source",
    `${evidenceRoot}/record_device_delivery_blocked.mjs`, "process"],
  ["delivery-runner", "device-delivery-source",
    `${evidenceRoot}/run_development_device_delivery.sh`, "process"],
  ["promotion-report", "shipping-promotion-report",
    `${evidenceRoot}/shipping-promotion-report.json`, "validation"],
  ["promotion-log", "shipping-promotion-log",
    `${evidenceRoot}/shipping-promotion.log`, "validation"],
  ["approved-tests", "approved-editmode-playmode-results",
    `${evidenceRoot}/approved-editmode-playmode-results.xml`, "validation"],
  ["approved-test-log", "approved-editmode-playmode-log",
    `${evidenceRoot}/approved-editmode-playmode-tests.log`, "validation"],
  ["device-job", "device-delivery-job",
    `${jobRoot}/job.env`, "validation"],
  ["device-list", "physical-device-list",
    `${jobRoot}/device-list.json`, "validation"],
  ["device-details", "physical-device-details",
    `${jobRoot}/device-details.json`, "validation"],
  ["shipping-scene", "shipping-scene",
    "unity/FidgetingApp/Assets/_EDC/Scenes/MeshyEDC.unity", "source-model"],
  ["coordinator-source", "runtime-coordinator-source",
    `${candidateRoot}/Runtime/MagneticSlideTileShippingCoordinator.cs`,
    "source-model"],
  ["unity-builder", "unity-builder-source",
    `${candidateRoot}/Editor/MagneticSlideTileGate12R003MotionReviewBuilder.cs`,
    "process"],
  ["test-source", "test-source",
    `${candidateRoot}/Tests/Editor/MagneticSlideTileGate12R002Tests.cs`,
    "validation"],
  ["ios-build-pipeline-source", "ios-build-pipeline-source",
    "unity/FidgetingApp/Assets/Editor/IosBuildPipeline.cs", "process"],
];

const records = definitions.map(([suffix, slot, assetPath, role]) => {
  const absolute = resolveRepoPath(assetPath);
  if (!fs.existsSync(absolute))
    throw new Error(`Missing approval/delivery artifact: ${assetPath}`);
  return {
    id: `${modelId}-gate12-${suffix}-r003`,
    stageId: "12-shipping",
    slot,
    path: assetPath,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: role === "source-model"
        ? "Unity 6000.5.6f1"
        : "Gate 12 rev 3 approved device-delivery workflow",
      version: "2026-08-31",
      recipe: `${evidenceRoot}/run_development_device_delivery.sh`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate12Revision: 3,
      gate12ApprovalExactWording: "这个是对的",
      buildJobId: job.jobId,
      buildKey: job.buildKey,
      appStoreSubmission: false,
      mechanismEvidenceContractSha256:
        "9cd7a08f34d7d8dfc3c6f89f6c80a5c5c2dcae48bc0d5c54ebf455a0727ea571",
    },
    sourceAssetIds: gate12.reviewArtifactIds,
    sourceClaimIds: [],
  };
});
for (const record of records) {
  const index = manifest.assets.findIndex((asset) => asset.id === record.id);
  if (index >= 0) manifest.assets[index] = record;
  else manifest.assets.push(record);
  if (!gate12.artifactIds.includes(record.id))
    gate12.artifactIds.push(record.id);
}

const approvalClaim = {
  id: "slider-gate12-r003-approved-shipping-promoted",
  stageId: "12-shipping",
  topic: "shipping-approval-delivery",
  statement:
    "The user approved Gate 12 rev 3 with exact wording “这个是对的”. "
    + "The corrected four-track candidate is the MeshyEDC default and the "
    + "old EDC_Root remains inactive as fallback. Physical delivery stopped "
    + "before export because DDI services were unavailable.",
  confidence: "verified",
  state: "active",
  assertedBy: "user-and-measurement",
  sourceAssetIds: records.map((record) => record.id),
  sourceRegions: [],
  decisionState: "approved",
  deliveryState: "promotion-complete-device-delivery-blocked-before-export",
};
const claimIndex = manifest.claims.findIndex(
  (claim) => claim.id === approvalClaim.id);
if (claimIndex >= 0) manifest.claims[claimIndex] = approvalClaim;
else manifest.claims.push(approvalClaim);

gate12.shippingSpec = {
  ...gate12.shippingSpec,
  sceneSha256: promotion.shippingSceneSha256,
  candidateDefaultActive: true,
  oldShippingModelDefaultActive: false,
  fallbackPreserved: true,
  shippingPromotion: "complete",
  buildJobId: job.jobId,
  buildKey: job.buildKey,
  sourceDigest: job.sourceDigest,
  unityVersion: job.unityVersion,
  developmentConfiguration: job.configuration,
  exportPath: job.exportPath,
  unityExportSucceeded: false,
  xcodeBuildSucceeded: false,
  signed: false,
  installed: false,
  launched: false,
  deliveryBlocker:
    "Physical iPhone tunnel connected, but DDI services are unavailable.",
  buildInstallPhone: false,
  deviceAcceptance: "pending-user-validation",
  appStoreSubmitted: false,
};
gate12.deliveryState = {
  decisionState: "approved",
  shippingPromotion: "complete",
  developmentBuild: "blocked-before-export",
  blocker: "ddi-services-unavailable",
  installed: false,
  launched: false,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-user-validation",
};

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((claim) => claim.stageId === stage.id)
    .map((claim) => JSON.stringify(claim));
  stage.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  stage.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
manifest.currentStageId = "12-shipping";
manifest.currentState.visualApproval =
  "gate12-r003-approved-exact-wording";
manifest.currentState.unityStatus =
  "approved-candidate-shipping-default";
manifest.currentState.shippingAssetUnchanged = false;
manifest.currentState.deviceStatus =
  "blocked-before-export-ddi-services-unavailable";
manifest.currentState.diagnosis =
  "Gate 12 rev 3 is approved and promoted. The locked development delivery "
  + "job stopped before Unity export because the paired iPhone reported "
  + "tunnel=connected and ddiServicesAvailable=false.";

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate12-r003-shipping-promoted-device-delivery-blocked",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  gate: "12-shipping",
  gateRevision: 3,
  exactApprovalWording: "这个是对的",
  sceneSha256: promotion.shippingSceneSha256,
  candidateDefaultActive: true,
  fallbackDefaultActive: false,
  fallbackPreserved: true,
  buildJobId: job.jobId,
  buildKey: job.buildKey,
  sourceDigest: job.sourceDigest,
  unityVersion: job.unityVersion,
  xcodeVersion: "26.4 (17E192)",
  deviceDiagnosis: {
    tunnelState: "connected",
    ddiServicesAvailable: false,
  },
  unityExportCreated: false,
  xcodeBuildRun: false,
  installRun: false,
  launchRun: false,
  appStoreSubmitted: false,
  deviceAcceptance: "pending-user-validation",
});

console.log(JSON.stringify({
  revision: saved.revision,
  gate12: saved.stages[11].status,
  shippingPromotion: saved.stages[11].shippingSpec.shippingPromotion,
  deviceStatus: saved.currentState.deviceStatus,
  buildJobId: job.jobId,
}, null, 2));
