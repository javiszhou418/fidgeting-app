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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-004";
const previewRoot = `${evidenceRoot}/unity-playmode-preview`;
const manifest = loadManifest(modelId);
const gate11 = manifest.stages.find((item) => item.id === "11-unity-parity");
if (manifest.revision !== 210 || gate11?.status !== "stale") {
  throw new Error("Expected stale Gate 11 at pipeline revision 210.");
}

const browserPath = `${previewRoot}/browser-playback-validation.json`;
const browser = JSON.parse(fs.readFileSync(resolveRepoPath(browserPath)));
if (
  !browser.pass
  || browser.runtimeExceptionCount !== 0
  || browser.loadingFailureCount !== 0
  || browser.desktopPlayback.duration !== 15
  || browser.mobilePlayback.duration !== 15
  || browser.desktopPlayback.dimensions.join("x") !== "1920x1080"
  || browser.mobilePlayback.dimensions.join("x") !== "1920x1080"
) {
  throw new Error("Browser playback validation failed.");
}

const browserTest = manifest.assets.find(
  (asset) => asset.id === "magnetic-slide-tile-unity-playmode-browser-test-r004"
);
const browserTestPath =
  "tools/model-provenance-explorer/tests/browser-gate08-r004-unity-playmode.mjs";
browserTest.sha256 = sha256File(resolveRepoPath(browserTestPath));
browserTest.sizeBytes = fs.statSync(resolveRepoPath(browserTestPath)).size;

const definitions = [
  [
    "browser-validation",
    "browser-playback-validation",
    browserPath,
    "validation",
  ],
  [
    "finalizer",
    "registration-source",
    `${evidenceRoot}/finalize_unity_playmode_preview.mjs`,
    "process",
  ],
];
const records = definitions.map(([suffix, slot, assetPath, role]) => {
  const absolute = resolveRepoPath(assetPath);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${assetPath}`);
  return {
    id: `${modelId}-unity-playmode-${suffix}-r004`,
    stageId: "11-unity-parity",
    slot,
    path: assetPath,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    reviewState: "supplemental-runtime-evidence-not-approval",
    producer: {
      name: "Gate 08 rev 4 Unity-only PlayMode capture",
      version: "Chrome CDP / Node.js",
      recipe: browserTestPath,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate08Revision: 4,
      gate11Revision: "supplemental-stale",
      note:
        "Desktop and mobile browser playback validation. Gate approval and device delivery remain unchanged.",
    },
    sourceAssetIds: [
      "magnetic-slide-tile-unity-playmode-runtime-recording-r004",
      "magnetic-slide-tile-unity-playmode-browser-test-r004",
    ],
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
gate11.artifactIds.push(...records.map((record) => record.id));
gate11.validations = gate11.validations.filter(
  (item) => item.id !== "gate08-r004-browser-playback"
);
gate11.validations.push({
  id: "gate08-r004-browser-playback",
  status: "pass",
  evidence:
    "Desktop 1440×1400 and mobile 390×844 loaded and played the 1920×1080 H.264. "
    + "Deep-link restore, playsInline, zero horizontal overflow, zero runtime exceptions and zero loading failures passed.",
});
gate11.unityParitySpec.supplementalUnityRuntime.browserValidation = {
  pass: true,
  desktop: browser.desktopPlayback,
  mobile: browser.mobilePlayback,
  deepLink: browser.deepLink,
  runtimeExceptionCount: 0,
  loadingFailureCount: 0,
};

const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`
    ).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256
  );
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
  type: "gate08-unity-only-playmode-browser-validation",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "11-unity-parity",
  gate08Revision: 4,
  status: "supplemental-runtime-browser-validated-no-approval-effect",
  artifactIds: records.map((record) => record.id),
  deepLink: browser.deepLink,
  desktopPlayback: browser.desktopPlayback,
  mobilePlayback: browser.mobilePlayback,
  runtimeExceptionCount: 0,
  loadingFailureCount: 0,
  gate08Status: savedStatus("08-lighting"),
  gate11Status: savedStatus("11-unity-parity"),
  gate12Status: savedStatus("12-shipping"),
  buildInstallPhone: false,
});
function savedStatus(stageId) {
  return manifest.stages.find((stage) => stage.id === stageId).status;
}
console.log(JSON.stringify({
  revision: saved.revision,
  gate08: saved.stages[7].status,
  gate11: saved.stages[10].status,
  gate12: saved.stages[11].status,
  browserPlayback: "pass",
}, null, 2));
