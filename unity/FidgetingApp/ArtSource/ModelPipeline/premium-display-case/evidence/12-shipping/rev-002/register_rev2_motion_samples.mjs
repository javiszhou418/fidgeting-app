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

const root = (
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/"
  + "evidence/12-shipping/rev-002"
);
const samples = [
  ["entry", "motion-00-entry.png", 0],
  ["overlap", "motion-01-overlap.png", 0.72],
  ["first-spin", "motion-02-first-spin.png", 0.96],
  ["second-spin", "motion-03-second-spin.png", 1.91],
  ["sheen", "motion-04-sheen.png", 2.71],
  ["hold", "motion-05-hold.png", 3.5]
];
const scriptId = `${modelId}-shipping-motion-registration-r002`;
const scriptPath = `${root}/register_rev2_motion_samples.mjs`;
const definitions = [
  ...samples.map(([name, file, time]) => ({
    id: `${modelId}-shipping-motion-${name}-r002`,
    slot: "shipping-motion-sample",
    path: `${root}/${file}`,
    contentClass: `real-unity-${name}-sample`,
    time
  })),
  {
    id: scriptId,
    slot: "shipping-registration",
    path: scriptPath,
    contentClass: "motion-sample-registration",
    time: null
  }
];
for (const record of definitions) {
  if (manifest.assets.some((asset) => asset.id === record.id)) {
    throw new Error(`Asset already registered: ${record.id}`);
  }
  const absolute = resolveRepoPath(record.path);
  if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
    throw new Error(`Missing motion sample: ${record.path}`);
  }
}

const sourceAssetIds = [
  "premium-display-case-motion-revision-request-r002",
  "premium-display-case-shipping-profile-r002",
  "premium-display-case-shipping-scene-r002",
  "premium-display-case-shipping-capture-report-r002"
];
const records = definitions.map((record) => {
  const absolute = resolveRepoPath(record.path);
  const asset = {
    id: record.id,
    stageId: "12-shipping",
    slot: record.slot,
    path: record.path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role: record.id === scriptId ? "process" : "unity-render",
    sourceAssetIds,
    sourceClaimIds: ["premium-display-case-motion-revision-claim-r002"],
    producer: {
      name: record.id === scriptId ? "fidgeting-model-pipeline" : "Unity",
      version: record.id === scriptId ? "2026-08-27" : "6000.5.6f1",
      recipe: record.contentClass
    },
    provenance: {
      origin: "repository-generated",
      contentClass: record.contentClass,
      assertedBy: "assistant",
      note: "Supplementary whole-case motion sample. Gate 12 rev 2 remains pending visual approval."
    },
    wholeAssembledCaseOnly: true,
    explodeEligible: false,
    toyPrizeBundled: false,
    shippingEligible: true,
    reviewState: "ready-for-review"
  };
  if (record.time !== null) {
    asset.view = {
      id: `shipping-motion-${record.id.split("-").at(-2)}`,
      kind: "shipping",
      camera: "Gate12ShippingCamera",
      parameters: {
        timeSeconds: record.time,
        staticCamera: true,
        wholeAssembledCaseOnly: true
      }
    };
  }
  return asset;
});
manifest.assets.push(...records);
stage.artifactIds.push(...records.map((record) => record.id));
stage.shippingSpec.motionSampleArtifactIds = records
  .filter((record) => record.id !== scriptId)
  .map((record) => record.id);
stage.outputDigest = digestValues(stage.artifactIds.map(
  (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256
));

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const event = {
  id: crypto.randomUUID(),
  type: "stage-evidence-registered",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "12-shipping",
  shippingRevision: 2,
  artifactIds: records.map((record) => record.id),
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
  registeredArtifactIds: event.artifactIds,
  eventId: event.id
}, null, 2));
