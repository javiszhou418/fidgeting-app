import crypto from "node:crypto";
import fs from "node:fs";
import {
  digestValues,
  loadManifest,
  normalizeRepoPath,
  resolveRepoPath,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "premium-display-case";
const expectedRevision = Number(process.argv[2]);
const evidenceRoot =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-008";
const manifest = loadManifest(modelId);
const gate04 = manifest.stages[3];

if (
  expectedRevision !== manifest.revision
  || gate04.status !== "ready_for_review"
  || gate04.architectureSpec?.evidenceRevision !== 8
) {
  throw new Error("Gate 04 rev 8 validation registration state mismatch.");
}

const definitions = [
  [
    "premium-display-case-pack-opening-unity-tests-r008",
    "architecture-test-results",
    `${evidenceRoot}/unity-focused-results.xml`,
    "validation"
  ],
  [
    "premium-display-case-pack-opening-validation-register-r008",
    "architecture-registration",
    `${evidenceRoot}/register_gate04_rev8_validation.mjs`,
    "process"
  ]
];

for (const [id, , assetPath] of definitions) {
  if (manifest.assets.some((asset) => asset.id === id)) {
    throw new Error(`Asset already registered: ${id}`);
  }
  const absolute = resolveRepoPath(assetPath);
  if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
    throw new Error(`Missing validation asset: ${assetPath}`);
  }
}

const testXml = fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/unity-focused-results.xml`),
  "utf8"
);
if (
  !testXml.includes('testcasecount="13"')
  || !testXml.includes('result="Passed"')
  || !testXml.includes('passed="13"')
  || !testXml.includes('failed="0"')
) {
  throw new Error("Focused Unity test result is not 13/13 passing.");
}

const sourceAssetIds = [
  "premium-display-case-pack-opening-direction-r008",
  "premium-display-case-pack-opening-profile-source-r008",
  "premium-display-case-pack-opening-tests-source-r008"
];
for (const [id, slot, assetPath, role] of definitions) {
  const absolute = resolveRepoPath(assetPath);
  manifest.assets.push({
    id,
    stageId: "04-architecture",
    slot,
    path: normalizeRepoPath(assetPath),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    sourceAssetIds,
    sourceClaimIds: [],
    producer: {
      name: id.includes("unity-tests") ? "Unity Test Framework" : "fidgeting-model-pipeline",
      version: id.includes("unity-tests") ? "6000.5.6f1" : "2026-08-28",
      recipe: "focused Gate 04 rev 8 validation"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      note: "Focused candidate validation; not shipping or physical-device evidence."
    },
    wholeAssembledCaseOnly: true,
    explodeEligible: false,
    toyPrizeBundled: false,
    shippingEligible: false,
    reviewState: "supporting-evidence"
  });
  gate04.artifactIds.push(id);
}
gate04.validations.push({
  id: "unity65-focused-timing-profile-tests",
  status: "pass",
  evidence: `${evidenceRoot}/unity-focused-results.xml: 13/13 passed`
});
gate04.architectureSpec.focusedUnityTests = {
  total: 13,
  passed: 13,
  failed: 0,
  platform: "EditMode",
  engine: "6000.5.6f1",
  resultAssetId: "premium-display-case-pack-opening-unity-tests-r008"
};
manifest.currentState.diagnosis +=
  " Focused Unity 6.5 EditMode timing-profile tests pass 13/13.";

function stableJson(value) {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`
    ).join(",")}}`;
  }
  return JSON.stringify(value);
}

for (let index = 0; index < manifest.stages.length; index += 1) {
  const stage = manifest.stages[index];
  const hashes = stage.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256
  );
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
const event = {
  id: crypto.randomUUID(),
  type: "stage-validation-refreshed",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "04-architecture",
  architectureRevision: 4,
  evidenceRevision: 8,
  focusedUnityTests: "13/13",
  unityVersion: "6000.5.6f1",
  physicalPhoneInstalled: false,
  visualApproval: "pending",
  statusText: "视觉批准待确认，未推送手机"
};

const result = saveManifest(manifest, event);
console.log(JSON.stringify({
  revision: result.revision,
  approvedCount: result.derived.approvedCount,
  shippingReady: result.derived.shippingReady,
  earliestProblem: result.derived.earliestProblem,
  eventId: event.id
}, null, 2));
