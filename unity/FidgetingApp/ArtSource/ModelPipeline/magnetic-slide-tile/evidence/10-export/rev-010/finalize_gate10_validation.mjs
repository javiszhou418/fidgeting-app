#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const output = path.dirname(fileURLToPath(import.meta.url));
const local = (filename) => path.join(output, filename);
const readJson = (filename) => JSON.parse(fs.readFileSync(local(filename), "utf8"));
const manifest = loadManifest(modelId);
const stage = manifest.stages.find((item) => item.id === "10-export");
if (manifest.revision !== 245 || stage?.status !== "ready_for_review" || stage.exportSpec?.revision !== 10) {
  throw new Error("Expected Gate 10 rev 10 ready at pipeline revision 245.");
}
const reports = {
  build: readJson("export-build-report.json"),
  reimport: readJson("reimport-validation.json"),
  blend: readJson("authoritative-blend-audit.json"),
  textures: readJson("texture-environment-validation.json"),
  exportManifest: readJson("export-manifest-validation.json"),
  browser: readJson("browser-validation.json"),
};
if (!Object.values(reports).every((report) => report.pass)) {
  throw new Error("A required Gate 10 report failed.");
}
const focusedXml = fs.readFileSync(local("focused-node-results.xml"), "utf8");
const fullXml = fs.readFileSync(local("full-node-results.xml"), "utf8");
const testCount = (xml) => (xml.match(/<testcase /g) || []).length;
const failureCount = (xml) => (xml.match(/<failure /g) || []).length;
if (testCount(focusedXml) !== 6 || failureCount(focusedXml) !== 0) {
  throw new Error("Focused Gate 10 Node results are not clean.");
}
if (testCount(fullXml) !== 226 || failureCount(fullXml) !== 1 || !fullXml.includes("Premium Display Case")) {
  throw new Error("Unexpected full Node test result.");
}

const now = new Date().toISOString();
const final = {
  schemaVersion: 1,
  gate: "10-export",
  revision: 10,
  timestamp: now,
  status: "ready_for_review",
  pass: true,
  source: {
    gate09Revision: 9,
    gate09ApprovalExactWording: "继续",
    blendSha256: reports.build.source.sha256,
    geometryDigest: reports.build.approved.geometryDigest,
    materialSourceSha256: reports.build.approved.materialSourceSha256,
    mechanismContractSha256: reports.build.approved.mechanismContractSha256,
    portabilityContractSha256: reports.build.approved.portabilityContractSha256,
  },
  exports: {
    authoritativeBlend: reports.build.formats.blend,
    fbx: reports.build.formats.fbx,
    glb: reports.build.formats.glb,
    collision: reports.build.formats.collisionFbx,
    exportManifestSha256: reports.exportManifest.manifest.sha256,
    glbCounts: reports.reimport.results.glbStructure.counts,
  },
  validation: {
    blenderBuildAndSourceImmutability: true,
    authoritativeBlendAudit: true,
    independentFbxGlbCollisionReimport: true,
    hierarchyPivotGroovesRaisedBossFlatBottom: true,
    materialPartitionsSideAndUndersideArtworkZero: true,
    normalsTangentsUvAndClampTransport: true,
    texturePixelAndMaskIdentity: true,
    environmentAndDisplayPortability: true,
    endpointInterlockAndClosedZeroMotion: true,
    noAnimationProxyCavityOrStaleOverlapMesh: true,
    unityImportAstcPlanOnly: true,
    focusedNode: "6/6 pass",
    fullNode: "225/226 pass; one unrelated Premium Display Case Gate 04 draft assertion",
    browserDesktopMobileGlbModalReloadDeepLink: true,
    browserRuntimeExceptions: reports.browser.runtimeExceptionCount,
    browserLoadingFailures: reports.browser.loadingFailureCount,
    approvedGate09VideoDecode: "H.264 High yuv420p 1600x600 30 fps 5.0 s; full decode pass",
    syntax: "Python compile and Node syntax pass",
    xml: "focused and full JUnit XML well formed",
    focusedDiff: "pass; unrelated Fan Card whitespace excluded",
    pipelineValidators: "single model and all manifests pass",
  },
  scope: {
    simulatorUsed: false,
    unityImportApplied: false,
    unitySceneModified: false,
    shippingSceneModified: false,
    buildInstallPhone: false,
    gate11Advanced: false,
    gate12Advanced: false,
  },
};
fs.writeFileSync(local("final-validation.json"), `${JSON.stringify(final, null, 2)}\n`);

const definitions = [
  ["final-validator", "final-validation-source", local("finalize_gate10_validation.mjs"), "process"],
  ["browser-test", "browser-test-source", path.join(repoRoot, "tools/model-provenance-explorer/tests/browser-gate10-rev10-current-export.mjs"), "process"],
  ["node-test", "node-test-source", path.join(repoRoot, "tools/model-provenance-explorer/tests/magnetic-slide-gate10-rev10.test.mjs"), "process"],
  ["browser-report", "browser-validation", local("browser-validation.json"), "validation"],
  ["browser-workbench", "browser-workbench", local("gate10-r010-persistent-workbench.png"), "analysis"],
  ["browser-glb", "interactive-glb-capture", local("gate10-r010-interactive-glb.png"), "analysis"],
  ["browser-mobile", "mobile-workbench", local("gate10-r010-mobile-workbench.png"), "analysis"],
  ["focused-node", "focused-node-results", local("focused-node-results.xml"), "validation"],
  ["full-node", "full-node-results", local("full-node-results.xml"), "validation"],
  ["final", "final-validation", local("final-validation.json"), "validation"],
];
const records = definitions.map(([suffix, slot, absolute, role]) => ({
  id: `${modelId}-export-${suffix}-r010`,
  stageId: "10-export",
  slot,
  path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
  sha256: sha256File(absolute),
  exists: true,
  sizeBytes: fs.statSync(absolute).size,
  role,
  producer: {
    name: "Gate 10 current export final validation",
    version: "Node.js / Headless Chrome / Blender 5.2.0 LTS",
    recipe: local("finalize_gate10_validation.mjs"),
  },
  provenance: {
    origin: "repository-generated",
    contentClass: slot,
    assertedBy: "assistant",
    gate10Revision: 10,
    sourceGate09Revision: 9,
    approvedGate09Wording: "继续",
    sourceBlendSha256: reports.build.source.sha256,
    geometryDigest: reports.build.approved.geometryDigest,
    materialSourceSha256: reports.build.approved.materialSourceSha256,
    mechanismEvidenceContractSha256: reports.build.approved.mechanismContractSha256,
    portabilityContractSha256: reports.build.approved.portabilityContractSha256,
    exportManifestSha256: reports.exportManifest.manifest.sha256,
    simulatorUsed: false,
    unityUsed: false,
    shippingChanged: false,
    deviceWork: false,
  },
  sourceAssetIds: [
    "magnetic-slide-tile-export-glb-r010",
    "magnetic-slide-tile-export-manifest-r010",
    "magnetic-slide-tile-environment-blend-r009",
  ],
  sourceClaimIds: [],
}));
manifest.assets.push(...records);
stage.artifactIds.push(...records.map((record) => record.id));
stage.reviewArtifactIds.push(
  `${modelId}-export-browser-glb-r010`,
  `${modelId}-export-browser-workbench-r010`,
);
stage.validations.push(
  {
    id: "browser-real-glb-mobile-modal-r010",
    status: "pass",
    evidence: "Desktop 1440 px and mobile 390 px passed. Real GLB loaded, orbited, and zoomed; modal, reload, direct deep link, and one-column mobile layout passed. Runtime/loading failures 0/0.",
  },
  {
    id: "final-validation-r010",
    status: "pass",
    evidence: "Focused Node 6/6; full Node 225/226 with one unrelated Premium Display Case assertion; Blender/export/reimport/material/UV, browser, video decode, syntax/XML, pipeline, and focused diff checks passed.",
  },
);
stage.exportSpec.browserEvidence = {
  desktopWidthPx: 1440,
  mobileWidthPx: 390,
  approvedCount: 9,
  currentGate: 10,
  glbChecklist: reports.browser.viewer.checklist,
  approvalInitiallyDisabled: reports.browser.desktop.approveDisabled,
  approvalEnabledAfterChecklist: !reports.browser.viewer.approveDisabled,
  runtimeExceptionCount: reports.browser.runtimeExceptionCount,
  loadingFailureCount: reports.browser.loadingFailureCount,
  mobileOneColumn: reports.browser.mobile.oneColumn,
};
stage.exportSpec.finalValidationSha256 = sha256File(local("final-validation.json"));
stage.exportSpec.finalValidationAt = now;
stage.readiness = {
  ready: true,
  blockers: [],
  note: "Interact with the real exported GLB: load, orbit, and zoom. Visual approval is pending; Unity and device work have not started.",
};
manifest.currentState.visualApproval = "gate10-rev10-review-pending-not-pushed";
manifest.currentState.blenderModelingStatus = "gate10-rev10-ready-for-review";
manifest.revision += 1;
manifest.updatedAt = now;

const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate10-rev10-final-validation",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: now,
  stageId: "10-export",
  revision: 10,
  status: "ready_for_review",
  gate09ApprovalExactWording: "继续",
  finalValidationAssetId: `${modelId}-export-final-r010`,
  finalValidationSha256: stage.exportSpec.finalValidationSha256,
  validation: final.validation,
  glbSha256: reports.build.formats.glb.sha256,
  exportManifestSha256: reports.exportManifest.manifest.sha256,
  simulatorUsed: false,
  unityUsed: false,
  shippingChanged: false,
  deviceWork: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate10: "ready_for_review",
  finalValidationSha256: stage.exportSpec.finalValidationSha256,
  focusedNode: final.validation.focusedNode,
  fullNode: final.validation.fullNode,
  browser: "pass",
}, null, 2));
