import crypto from "node:crypto";
import fs from "node:fs";
import {
  digestValues,
  loadManifest,
  resolveRepoPath,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "premium-display-case";
const expectedRevision = Number(process.argv[2]);
const manifest = loadManifest(modelId);
if (!Number.isInteger(expectedRevision) || expectedRevision !== manifest.revision) {
  throw new Error(
    `Manifest revision conflict: expected ${expectedRevision}, actual ${manifest.revision}.`
  );
}

const stage = manifest.stages[11];
if (
  stage.status !== "ready_for_review"
  || stage.shippingSpec?.revision !== 2
  || manifest.currentState.shippingPreview?.visualApproved !== false
) {
  throw new Error("Gate 12 rev 2 must remain pending visual review.");
}

const evidenceAsset = manifest.assets.find(
  (asset) => asset.id === "premium-display-case-shipping-evidence-report-r002"
);
const testsAsset = manifest.assets.find(
  (asset) => asset.id === "premium-display-case-shipping-unity-tests-r002"
);
if (!evidenceAsset || !testsAsset) {
  throw new Error("Gate 12 rev 2 validation assets are missing.");
}
const evidence = JSON.parse(
  fs.readFileSync(resolveRepoPath(evidenceAsset.path), "utf8")
);
if (
  evidence.status !== "pass"
  || evidence.unityTests.passed !== 50
  || evidence.unityTests.failed !== 0
  || evidence.checks.reduceMotionIsCausalAndStatic !== true
  || Object.values(evidence.checks).some((value) => value !== true)
) {
  throw new Error("Refreshed Gate 12 evidence does not pass 50/50.");
}

const refreshAssetId =
  "premium-display-case-shipping-validation-refresh-r002";
if (manifest.assets.some((asset) => asset.id === refreshAssetId)) {
  throw new Error("Gate 12 rev 2 validation refresh is already registered.");
}
const refreshPath = (
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/"
  + "evidence/12-shipping/rev-002/refresh_rev2_validation.mjs"
);
const refreshAbsolute = resolveRepoPath(refreshPath);
manifest.assets.push({
  id: refreshAssetId,
  stageId: "12-shipping",
  slot: "shipping-registration",
  path: refreshPath,
  sha256: sha256File(refreshAbsolute),
  exists: true,
  sizeBytes: fs.statSync(refreshAbsolute).size,
  role: "process",
  sourceAssetIds: [
    "premium-display-case-shipping-registration-r002",
    evidenceAsset.id,
    testsAsset.id
  ],
  sourceClaimIds: [
    "premium-display-case-motion-revision-claim-r002"
  ],
  producer: {
    name: "fidgeting-model-pipeline",
    version: "2026-08-27",
    recipe: "refresh-rev2-validation-hashes-without-approval"
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "gate12-rev2-validation-refresh",
    assertedBy: "assistant",
    note: "Adds causal static Reduce Motion evidence without changing the visual candidate or approval state."
  },
  wholeAssembledCaseOnly: true,
  explodeEligible: false,
  toyPrizeBundled: false,
  shippingEligible: true,
  reviewState: "ready-for-review"
});
stage.artifactIds.push(refreshAssetId);

const refreshed = [];
for (const assetId of stage.artifactIds) {
  const asset = manifest.assets.find((candidate) => candidate.id === assetId);
  if (!asset) continue;
  const absolute = resolveRepoPath(asset.path);
  if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
    throw new Error(`Missing current Gate 12 asset: ${asset.path}`);
  }
  const nextHash = sha256File(absolute);
  if (asset.sha256 !== nextHash || asset.sizeBytes !== fs.statSync(absolute).size) {
    refreshed.push(asset.id);
  }
  asset.sha256 = nextHash;
  asset.sizeBytes = fs.statSync(absolute).size;
  asset.exists = true;
}

stage.validations = stage.validations.map((validation) => (
  validation.id === "focused-tests"
    ? {
        ...validation,
        evidence: "Relevant Unity EditMode tests pass 50/50, including causal static Reduce Motion. Swift gate harness passes 25/25 and shipping Swift warnings-as-errors typecheck passes."
      }
    : validation
));
stage.shippingSpec.focusedUnityTests = {
  passed: 50,
  failed: 0,
  reduceMotionCausalStatic: true
};
manifest.currentState.diagnosis = manifest.currentState.diagnosis.replace(
  "The canonical Release App Simulator preview is ready for review.",
  "The canonical Release App Simulator preview is ready for review. Relevant Unity tests pass 50/50, including causal static Reduce Motion."
);

stage.outputDigest = digestValues(stage.artifactIds.map(
  (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256
));
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const event = {
  id: crypto.randomUUID(),
  type: "stage-evidence-refreshed",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "12-shipping",
  shippingRevision: 2,
  refreshedAssetIds: refreshed,
  focusedUnityTests: "50/50",
  reduceMotionCausalStatic: true,
  gate12Status: "ready_for_review",
  shippingReady: false,
  physicalPhoneInstalled: false,
  deviceAccepted: false,
  autoApproved: false,
  statusText: "视觉批准待确认，未推送手机"
};

const result = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: result.revision,
  approvedCount: result.derived.approvedCount,
  shippingReady: result.derived.shippingReady,
  earliestProblem: result.derived.earliestProblem,
  refreshedAssetIds: refreshed,
  eventId: event.id
}, null, 2));
