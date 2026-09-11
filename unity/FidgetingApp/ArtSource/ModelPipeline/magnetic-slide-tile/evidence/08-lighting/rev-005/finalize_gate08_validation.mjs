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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-005";
const manifest = loadManifest(modelId);
const stage = manifest.stages.find((item) => item.id === "08-lighting");
if (manifest.revision !== 232 || stage?.status !== "ready_for_review" || stage?.lightingSpec?.revision !== 5) {
  throw new Error("Expected Gate 08 rev 5 ready at pipeline revision 232.");
}
const browser = JSON.parse(fs.readFileSync(resolveRepoPath(`${evidenceRoot}/browser-validation.json`)));
const audit = JSON.parse(fs.readFileSync(resolveRepoPath(`${evidenceRoot}/lighting-parity-audit.json`)));
const motion = JSON.parse(fs.readFileSync(resolveRepoPath(`${evidenceRoot}/legal-lighting-turntable-report.json`)));
const unityXml = fs.readFileSync(resolveRepoPath(`${evidenceRoot}/unity-editmode-results.xml`), "utf8");
if (!browser.pass || !audit.pass || !motion.pass || !/<test-run[^>]*result="Passed"[^>]*passed="5"[^>]*failed="0"/.test(unityXml)) {
  throw new Error("Final Gate 08 validation inputs did not pass.");
}
const finalValidationPath = resolveRepoPath(`${evidenceRoot}/final-validation.json`);
const finalValidation = {
  schemaVersion: 1,
  gate: "08-lighting",
  revision: 5,
  status: "ready_for_review",
  approvals: {
    gate07Revision: 12,
    exactUserWording: "继续",
    persisted: true,
  },
  immutableInputs: {
    materialBlendSha256: stage.lightingSpec.sourceMaterialSha256,
    geometryDigest: stage.lightingSpec.geometryDigest,
    mechanismContractSha256: stage.lightingSpec.mechanismContractSha256,
  },
  lighting: {
    sharedHdrSha256: audit.sourceHashes.environment,
    displayTransform: "neutral-display-v1",
    parity: audit.parity,
    appearance: audit.appearance,
  },
  motion: {
    recordingSha256: motion.videoSha256,
    sourceFrames: motion.frameCount,
    encodedFrames: 180,
    durationSeconds: motion.durationSeconds,
    fixedAxisVarianceMm: motion.maximumFixedAxisVarianceMm,
    pitchRollRadians: motion.maximumPitchRollRadians,
    checks: motion.checks,
  },
  validation: {
    blenderBuilder: "pass",
    lightingParityAudit: "pass",
    isolatedUnityBuilder: "pass",
    unityEditMode: "5/5 pass",
    focusedNode: "5/5 pass",
    fullNode: "199/199 pass",
    pipelineValidator: "errors/missing/unhashed 0/0/0",
    allPipelineValidator: "errors/missing/unhashed 0/0/0",
    browserDesktopMobileModalVideoDeepLink: "pass",
    browserRuntimeExceptions: browser.runtimeExceptionCount,
    browserLoadingFailures: browser.loadingFailureCount,
    video: "H.264 High yuv420p 960x720 30 fps 180 frames 6.0 s",
    syntax: "Python compile and Node syntax pass",
    xml: "xmllint pass",
    diffCheck: "pass",
  },
  deliveryState: {
    visualApproval: "pending",
    shippingSceneModified: false,
    simulator: false,
    buildInstallPhone: false,
    deviceAccepted: false,
  },
  pass: true,
};
fs.writeFileSync(finalValidationPath, `${JSON.stringify(finalValidation, null, 2)}\n`);
const definitions = [
  ["finalizer", "final-validation-source", `${evidenceRoot}/finalize_gate08_validation.mjs`, "process"],
  ["final", "final-validation", `${evidenceRoot}/final-validation.json`, "validation"],
  ["browser-test", "browser-test-source", "tools/model-provenance-explorer/tests/browser-gate08-rev5-endpoint-lighting.mjs", "validation"],
  ["browser-report", "browser-validation", `${evidenceRoot}/browser-validation.json`, "validation"],
  ["browser-screenshot", "shipping-workbench-preview", "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate08-rev5-lighting.png", "source-model"],
  ["unity-test", "unity-test-source", "unity/FidgetingApp/Assets/Tests/Editor/MagneticSlideTileGate08R005LightingTests.cs", "validation"],
  ["unity-test-results", "unity-test-results", `${evidenceRoot}/unity-editmode-results.xml`, "validation"],
  ["unity-test-log", "unity-test-log", `${evidenceRoot}/unity-editmode-tests.log`, "validation"],
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-lighting-${suffix}-r005`,
    stageId: "08-lighting",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Gate 08 rev 5 final validation",
      version: "Node.js / Unity 6000.5.6f1 / Chrome",
      recipe: `${evidenceRoot}/finalize_gate08_validation.mjs`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate08Revision: 5,
      sourceMaterialSha256: stage.lightingSpec.sourceMaterialSha256,
      geometryDigest: stage.lightingSpec.geometryDigest,
      mechanismEvidenceContractSha256: stage.lightingSpec.mechanismContractSha256,
      note: "Final validation evidence only. No shipping, build, install or phone work.",
    },
    sourceAssetIds: [
      "magnetic-slide-tile-material-blend-r012",
      "magnetic-slide-tile-lighting-turntable-r005",
      "magnetic-slide-tile-lighting-parity-audit-r005",
    ],
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
stage.artifactIds.push(...records.map((record) => record.id));
stage.validations.push({
  id: "final-gate08-validation",
  status: "pass",
  evidence: "Blender, isolated Unity, 5/5 Unity EditMode, 199/199 Node, pipeline, browser desktop/mobile/modal/video/deep-link, H.264, syntax, XML and diff checks passed.",
});
stage.lightingSpec.finalValidationAssetId = `${modelId}-lighting-final-r005`;
stage.lightingSpec.finalValidationSha256 = records.find((record) => record.id.endsWith("-final-r005")).sha256;
stage.lightingSpec.browserValidation = {
  pass: true,
  desktop: browser.desktop.currentGate,
  mobile: browser.mobile.stage,
  video: browser.desktopPlayback.dimensions,
  runtimeExceptionCount: browser.runtimeExceptionCount,
  loadingFailureCount: browser.loadingFailureCount,
};
stage.readiness = {
  ready: true,
  blockers: [],
  note: "Gate 08 rev 5 final validation passed. 视觉批准待确认，未推送手机。",
};
manifest.issues = manifest.issues.filter(
  (issue) => issue.id !== "slider-gate08-r004-corrected-recording-review",
);
const currentIssue = manifest.issues.find((issue) => issue.id === "slider-gate08-r005-review");
if (currentIssue) currentIssue.note = "Gate 08 rev 5 passed final validation and awaits visual approval. Gate 09-12 remain stale.";
const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map((assetId) =>
    manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims.filter((claim) => claim.stageId === current.id).map(stableJson);
  current.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  current.outputDigest = digestValues([...hashes, ...claims]);
}
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate08-rev5-final-validation",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "08-lighting",
  revision: 5,
  status: "ready_for_review",
  finalValidationAssetId: `${modelId}-lighting-final-r005`,
  validation: finalValidation.validation,
  visualApproval: "pending",
  shippingChanged: false,
  buildInstallPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate08: saved.stages[7].status,
  finalValidation: "pass",
  approved: saved.stages.filter((stageItem) => stageItem.status === "approved").length,
}, null, 2));
