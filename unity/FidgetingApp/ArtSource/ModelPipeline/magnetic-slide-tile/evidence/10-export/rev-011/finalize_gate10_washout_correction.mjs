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
const here = path.dirname(fileURLToPath(import.meta.url));
const local = (relative) => path.join(here, relative);
const readJson = (relative) => JSON.parse(fs.readFileSync(local(relative), "utf8"));
const manifest = loadManifest(modelId);
const stage = manifest.stages.find((item) => item.id === "10-export");
if (manifest.revision !== 249 || stage?.status !== "draft" || stage.exportSpec?.revision !== 11) {
  throw new Error("Expected draft Gate 10 rev 11 at pipeline revision 249.");
}

const reports = {
  transport: readJson("portable-glb-build-validation.json"),
  glb: readJson("corrected-glb-audit.json"),
  blender: readJson("controlled-blender-comparison-validation.json"),
  visual: readJson("visual-metrics-validation.json"),
  package: readJson("export-manifest-validation.json"),
  browser: readJson("browser-viewer-validation.json"),
  viewer: readJson("threejs-viewer-audit.json"),
};
if (!Object.values(reports).every((report) => report.pass)) {
  throw new Error("Gate 10 rev 11 cannot advance while a required report fails.");
}
if (
  reports.browser.viewer.payload.reviewedArtifactSha256 !== stage.exportSpec.glbSha256
  || reports.viewer.artifacts.viewerScreenshot.sha256 !== sha256File(local("gate10-r011-threejs-neutral-hero.png"))
  || reports.viewer.artifacts.orbitRecording.sha256 !== sha256File(local("gate10-r011-real-glb-orbit.mp4"))
) {
  throw new Error("Interactive review evidence does not match the registered GLB.");
}

const definitions = [
  ["finalizer", "final-validation-source", "finalize_gate10_washout_correction.mjs", "process"],
  ["browser-test", "browser-test-source", "../../../../../../../../tools/model-provenance-explorer/tests/browser-gate10-rev11-washout-correction.mjs", "process"],
  ["browser-report", "browser-viewer-validation", "browser-viewer-validation.json", "validation"],
  ["viewer-audit", "threejs-viewer-audit", "threejs-viewer-audit.json", "validation"],
  ["browser-workbench", "browser-workbench", "gate10-r011-persistent-workbench.png", "analysis"],
  ["viewer-capture", "interactive-glb-capture", "gate10-r011-threejs-neutral-hero.png", "analysis"],
  ["mobile-workbench", "mobile-workbench", "gate10-r011-mobile-workbench.png", "analysis"],
  ["orbit-recording", "interactive-glb-recording", "gate10-r011-real-glb-orbit.mp4", "analysis"],
];
const records = definitions.map(([suffix, slot, relative, role]) => {
  const absolute = path.resolve(here, relative);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${absolute}`);
  return {
    id: `${modelId}-export-${suffix}-r011`,
    stageId: "10-export",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "Gate 10 rev 11 final browser validation",
      version: "Node.js / Headless Chrome / Three.js 0.185.1",
      recipe: local("finalize_gate10_washout_correction.mjs"),
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      gate10Revision: 11,
      rejectedRevision: 10,
      rejectionExactWording: "almost entirely white/washed out",
      correctedGlbSha256: stage.exportSpec.glbSha256,
      governingContractSha256: stage.exportSpec.governingContractSha256,
      mechanismEvidenceContractSha256: stage.exportSpec.governingContractSha256,
      geometryDigest: stage.exportSpec.geometryDigest,
      correctionScope: "portable GLB PBR and neutral viewer calibration only",
      simulatorUsed: false,
      unityUsed: false,
      deviceWork: false,
    },
    sourceAssetIds: [
      "magnetic-slide-tile-export-glb-r011",
      "magnetic-slide-tile-export-manifest-r011",
    ],
    sourceClaimIds: [],
  };
});
manifest.assets.push(...records);
stage.artifactIds.push(...records.map((record) => record.id));
stage.reviewArtifactIds.push(
  `${modelId}-export-viewer-capture-r011`,
  `${modelId}-export-orbit-recording-r011`,
);
stage.validations.push(
  {
    id: "threejs-calibrated-real-glb-r011",
    status: "pass",
    evidence: "Real corrected GLB loaded, orbited, and zoomed under neutral HDR, sRGB output, ACES, and exposure 0.9. Runtime/loading failures are 0/0.",
  },
  {
    id: "objective-viewer-material-r011",
    status: "pass",
    evidence: "Viewer red fraction 39.72%, clipped white 0.09%, and controlled silver highlight 2.36%; dark body, silver rim, and zero side artwork checks pass.",
  },
  {
    id: "desktop-mobile-modal-video-r011",
    status: "pass",
    evidence: "Desktop, 390×844 mobile, comparison and closeup modals, reload persistence, direct route, and 24-frame H.264 interaction recording pass.",
  },
);
stage.exportSpec.exportManifestSha256 = reports.package.manifest.sha256;
stage.exportSpec.viewerCalibration = {
  environmentAssetId: "magnetic-slide-tile-export-neutral-hdri-r011",
  toneMapping: reports.browser.calibration.toneMapping,
  outputColorSpace: reports.browser.calibration.outputColorSpace,
  exposure: reports.browser.calibration.exposure,
  environmentIntensity: reports.browser.calibration.environmentIntensity,
  directLights: reports.browser.calibration.directLights,
  persistedExposureIsolation: true,
};
stage.exportSpec.browserEvidence = {
  desktopTabs: reports.browser.desktop.tabsCount,
  roadmapGates: reports.browser.desktop.roadmap,
  mobileWidthPx: 390,
  mobileOneColumn: reports.browser.mobile.oneColumn,
  completedInteractionChecklist: reports.browser.viewer.payload.completedInteractionChecklist,
  reviewedArtifactSha256: reports.browser.viewer.payload.reviewedArtifactSha256,
  runtimeExceptionCount: reports.browser.runtimeExceptionCount,
  loadingFailureCount: reports.browser.loadingFailureCount,
  viewerScreenshotSha256: reports.viewer.artifacts.viewerScreenshot.sha256,
  orbitRecordingSha256: reports.viewer.artifacts.orbitRecording.sha256,
};
stage.status = "ready_for_review";
stage.readiness = {
  ready: true,
  blockers: [],
  note: "Review the corrected real GLB. Visual approval remains pending; Unity and device work have not started.",
};
const issue = manifest.issues.find((item) => item.id === "slider-gate10-r011-washout-correction");
if (issue) {
  issue.assetId = "magnetic-slide-tile-export-glb-r011";
  issue.status = "resolved-awaiting-visual-approval";
  issue.note = "Rev 11 corrected GLB and calibrated viewer pass independently. User visual approval is pending.";
}
manifest.currentState.visualApproval = "gate10-rev11-review-pending-not-pushed";
manifest.currentState.blenderModelingStatus = "gate10-rev11-ready-for-review";
manifest.overallStatus = "waiting_for_user";
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate10-rev11-final-browser-validation",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "10-export",
  revision: 11,
  status: "ready_for_review",
  rejectedRevision: 10,
  rejectedExactWording: "almost entirely white/washed out",
  correctedGlbSha256: stage.exportSpec.glbSha256,
  exportManifestSha256: stage.exportSpec.exportManifestSha256,
  viewerScreenshotSha256: reports.viewer.artifacts.viewerScreenshot.sha256,
  orbitRecordingSha256: reports.viewer.artifacts.orbitRecording.sha256,
  geometryChanged: false,
  unityUsed: false,
  deviceWork: false,
});
console.log(JSON.stringify({
  revision: saved.revision,
  gate10: stage.status,
  glbSha256: stage.exportSpec.glbSha256,
  viewerScreenshotSha256: reports.viewer.artifacts.viewerScreenshot.sha256,
  orbitRecordingSha256: reports.viewer.artifacts.orbitRecording.sha256,
}, null, 2));
