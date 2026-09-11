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
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/08-lighting/rev-006";
const manifest = loadManifest(modelId);
const stage = manifest.stages.find((item) => item.id === "08-lighting");
const gate07 = manifest.stages.find((item) => item.id === "07-material");
if (manifest.revision !== 239
  || gate07?.decision?.notes !== "通过"
  || stage?.status !== "ready_for_review"
  || stage?.lightingSpec?.revision !== 6) {
  throw new Error("Expected Gate 08 rev 6 ready at pipeline revision 239.");
}

const browser = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/browser-validation.json`),
));
const audit = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/lighting-material-audit.json`),
));
const motion = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/legal-lighting-turntable-report.json`),
));
const blender = JSON.parse(fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/blender-lighting-report.json`),
));
const fullNode = fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/full-node-tests.log`),
  "utf8",
);
const focusedXml = fs.readFileSync(
  resolveRepoPath(`${evidenceRoot}/focused-node-results.xml`),
  "utf8",
);
if (!browser.pass
  || !audit.pass
  || !motion.pass
  || !blender.pass
  || !focusedXml.includes("<!-- tests 7 -->")
  || !focusedXml.includes("<!-- pass 7 -->")
  || !focusedXml.includes("<!-- fail 0 -->")
  || !fullNode.includes("ℹ tests 212")
  || !fullNode.includes("ℹ pass 211")
  || !fullNode.includes("ℹ fail 1")
  || !fullNode.includes("Premium Display Case records Gate 12 rev 4")) {
  throw new Error("Final Gate 08 validation inputs did not match expected results.");
}

const finalValidationPath = resolveRepoPath(`${evidenceRoot}/final-validation.json`);
const finalValidation = {
  schemaVersion: 1,
  gate: "08-lighting",
  revision: 6,
  status: "ready_for_review",
  approvals: {
    gate07Revision: 13,
    exactUserWording: "通过",
    persisted: true,
  },
  immutableInputs: {
    materialBlendSha256: stage.lightingSpec.sourceMaterialSha256,
    geometryDigest: stage.lightingSpec.geometryDigest,
    mechanismContractSha256: stage.lightingSpec.mechanismContractSha256,
    partitionDigests: Object.fromEntries(
      Object.entries(gate07.materialSpec.partitions)
        .map(([name, values]) => [name, values.partitionDigest]),
    ),
  },
  nonDestructiveDiagnostics: {
    policy: "duplicate scene, object, and mesh data",
    sourceMeshDataElementIdentical: blender.sourceMeshDataElementIdentical,
    materialSlotsIdentical: blender.checks.materialSlotsIdentical,
    polygonMaterialIndicesByteIdentical:
      blender.checks.polygonMaterialIndicesByteIdentical,
    uvsByteIdentical: blender.checks.uvsByteIdentical,
    geometryUnchanged: blender.checks.geometryUnchanged,
    passes: blender.diagnosticPasses,
  },
  materialPartitions: {
    sideArtwork: 0,
    undersideArtwork: 0,
    capArtworkPresent: true,
    rimSilverPresent: true,
    glbClampNoWrap: audit.checks.glbClampNoWrap,
    glbReimport: audit.importedGlb,
  },
  lighting: {
    sharedHdrSha256: audit.sourceHashes.environment,
    displayTransform: "neutral-display-v1",
    cameraRecipes: audit.cameraRecipes,
    imageMetrics: audit.imageMetrics,
  },
  motion: {
    recordingSha256: motion.videoSha256,
    sourceFrames: motion.frameCount,
    encodedFrames: motion.encodedFrameCount,
    durationSeconds: motion.durationSeconds,
    fixedAxisVarianceMm: motion.maximumFixedAxisVarianceMm,
    pitchRollRadians: motion.maximumPitchRollRadians,
    checks: motion.checks,
  },
  validation: {
    blenderLightingAndPasses: "pass",
    materialAndGlbAudit: "pass",
    framePartitionAudit: "pass",
    focusedNode: "7/7 pass",
    fullNode: "211/212; one unrelated concurrent Premium Display Case assertion",
    pipelineValidator: "errors/missing/unhashed 0/0/0",
    allPipelineValidator: "errors/missing/unhashed 0/0/0",
    browserDesktopMobileGlbVideoModalDeepLink: "pass",
    browserRuntimeExceptions: browser.runtimeExceptionCount,
    browserLoadingFailures: browser.loadingFailureCount,
    video: "H.264 High yuv420p 960x720 30 fps 180 frames 6.0 s",
    syntax: "Python compile and Node syntax pass",
    xml: "focused JUnit XML well formed",
    focusedDiff: "reviewed; feature paths only",
  },
  deliveryState: {
    visualApproval: "pending",
    gate09Advanced: false,
    simulatorUsed: false,
    unityUsed: false,
    shippingSceneModified: false,
    buildInstallPhone: false,
    deviceAccepted: false,
  },
  pass: true,
};
fs.writeFileSync(finalValidationPath, `${JSON.stringify(finalValidation, null, 2)}\n`);

const definitions = [
  ["finalizer", "final-validation-source", `${evidenceRoot}/finalize_gate08_validation.mjs`, "process"],
  ["final", "final-validation", `${evidenceRoot}/final-validation.json`, "validation"],
  ["focused-test", "focused-test-source", "tools/model-provenance-explorer/tests/magnetic-slide-gate08-rev6.test.mjs", "validation"],
  ["focused-results", "focused-test-results", `${evidenceRoot}/focused-node-results.xml`, "validation"],
  ["full-node-log", "full-node-log", `${evidenceRoot}/full-node-tests.log`, "validation"],
  ["browser-test", "browser-test-source", "tools/model-provenance-explorer/tests/browser-gate08-rev6-partition-safe-lighting.mjs", "validation"],
  ["browser-report", "browser-validation", `${evidenceRoot}/browser-validation.json`, "validation"],
  ["workbench-preview", "shipping-workbench-preview", `${evidenceRoot}/gate08-r006-persistent-workbench.png`, "source-model"],
  ["lookdev-preview", "interactive-lookdev-preview", `${evidenceRoot}/gate08-r006-interactive-lookdev.png`, "source-model"],
  ["mobile-preview", "mobile-workbench-preview", `${evidenceRoot}/gate08-r006-mobile-workbench.png`, "source-model"],
  ["workbench-source", "workbench-source", "tools/model-provenance-explorer/app.js", "process"],
  ["design-bible", "design-decision-record", "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md", "validation"],
  ["implementation-status", "implementation-status", "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md", "validation"],
];
const records = definitions.map(([suffix, slot, path, role]) => {
  const absolute = resolveRepoPath(path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${path}`);
  return {
    id: `${modelId}-lighting-${suffix}-r006`,
    stageId: "08-lighting",
    slot,
    path,
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Gate 08 rev 6 final validation",
      version: "Node.js / Chrome / Blender 5.2.0 LTS",
      recipe: `${evidenceRoot}/finalize_gate08_validation.mjs`,
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate08Revision: 6,
      sourceMaterialSha256: stage.lightingSpec.sourceMaterialSha256,
      geometryDigest: stage.lightingSpec.geometryDigest,
      mechanismEvidenceContractSha256: stage.lightingSpec.mechanismContractSha256,
      note: "Final validation evidence only. Visual approval remains pending. No Simulator, Unity, shipping, build, install, or phone work.",
    },
    sourceAssetIds: [
      "magnetic-slide-tile-material-blend-r013",
      "magnetic-slide-tile-lighting-lookdev-r006",
      "magnetic-slide-tile-lighting-turntable-r006",
      "magnetic-slide-tile-lighting-material-audit-r006",
    ],
    sourceClaimIds: [],
  };
});

manifest.assets.push(...records);
stage.artifactIds.push(...records.map((record) => record.id));
stage.validations.push({
  id: "final-gate08-rev6-validation",
  status: "pass",
  evidence: "Blender/pass/material/GLB/motion, focused Node 7/7, pipeline, browser desktop/mobile/GLB/video/modal/deep-link, syntax, XML and H.264 decode passed. Full Node is 211/212 with one unrelated concurrent Premium Display Case assertion.",
});
stage.lightingSpec.finalValidationAssetId = `${modelId}-lighting-final-r006`;
stage.lightingSpec.finalValidationSha256 = records.find(
  (record) => record.id.endsWith("-final-r006"),
).sha256;
stage.lightingSpec.browserValidation = {
  pass: true,
  desktop: browser.desktop.currentGate,
  mobile: browser.mobile.stage,
  glbOrbitZoom: `${browser.viewer.orbit}/${browser.viewer.zoom}`,
  video: [browser.video.width, browser.video.height, browser.video.duration],
  runtimeExceptionCount: browser.runtimeExceptionCount,
  loadingFailureCount: browser.loadingFailureCount,
};
stage.readiness = {
  ready: true,
  blockers: [],
  note: "Gate 08 rev 6 final validation passed. 视觉批准待确认，未推送手机。",
};
const currentIssue = manifest.issues.find(
  (issue) => issue.id === "slider-gate08-r006-review",
);
if (currentIssue) {
  currentIssue.note = "Gate 08 rev 6 passed final validation and awaits visual approval. Gates 09–12 remain stale.";
}

const stableJson = (value) => Array.isArray(value)
  ? `[${value.map(stableJson).join(",")}]`
  : value && typeof value === "object"
    ? `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`,
    ).join(",")}}`
    : JSON.stringify(value);
for (let index = 0; index < manifest.stages.length; index += 1) {
  const current = manifest.stages[index];
  const hashes = current.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256,
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
  type: "gate08-rev6-final-validation",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "08-lighting",
  revision: 6,
  status: "ready_for_review",
  gate07ApprovalExactWording: "通过",
  finalValidationAssetId: `${modelId}-lighting-final-r006`,
  validation: finalValidation.validation,
  sourceSnapshotElementIdentical: true,
  sideWallArtwork: 0,
  undersideArtwork: 0,
  visualApproval: "pending",
  gate09Advanced: false,
  simulatorUsed: false,
  unityUsed: false,
  shippingChanged: false,
  buildInstallPhone: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate08: saved.stages[7].status,
  finalValidation: "pass",
  approved: saved.stages.filter((item) => item.status === "approved").length,
}, null, 2));
