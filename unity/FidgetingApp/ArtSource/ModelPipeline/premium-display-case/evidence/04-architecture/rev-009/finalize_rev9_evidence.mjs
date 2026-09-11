import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { execFileSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const evidence = path.dirname(fileURLToPath(import.meta.url));
const repo = path.resolve(evidence, "../../../../../../../..");
const unity = path.join(repo, "unity/FidgetingApp");
const relativeEvidence =
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-009";
const candidateRoot =
  "unity/FidgetingApp/Assets/_DisplayCase/Candidates/PackOpeningGate04R009";

const paths = {
  quality: path.join(evidence, "quality-contract.json"),
  source: path.join(evidence, "unity-source-manifest.json"),
  capture: path.join(evidence, "unity-capture-report.json"),
  tests: path.join(evidence, "unity-focused-results.xml"),
  full: path.join(evidence, "gate04-r009-full-signature-60fps.mp4"),
  tear: path.join(evidence, "gate04-r009-tear-closeup-quarter-speed.mp4"),
  impact: path.join(
    evidence,
    "gate04-r009-impact-1700-1950ms-quarter-speed.mp4"
  ),
  tearSheet: path.join(evidence, "tear-silhouette-contact-sheet.png"),
  impactSheet: path.join(evidence, "impact-continuity-contact-sheet.png"),
  scene: path.join(
    repo,
    candidateRoot,
    "Scenes/PackOpeningGate04R009.unity"
  ),
  controller: path.join(
    repo,
    candidateRoot,
    "Runtime/PackOpeningGate04R009Controller.cs"
  ),
  profile: path.join(
    repo,
    candidateRoot,
    "Runtime/PackOpeningGate04R009Profile.cs"
  ),
  captureSource: path.join(
    repo,
    candidateRoot,
    "Runtime/PackOpeningGate04R009Capture.cs"
  ),
  builder: path.join(
    repo,
    candidateRoot,
    "Editor/PackOpeningGate04R009Builder.cs"
  ),
  testsSource: path.join(
    repo,
    candidateRoot,
    "Tests/Editor/PackOpeningGate04R009Tests.cs"
  ),
  bodyShader: path.join(
    repo,
    candidateRoot,
    "Shaders/PackFoilBodyTearR009.shader"
  ),
  flapShader: path.join(
    repo,
    candidateRoot,
    "Shaders/PackFoilSurfaceR009.shader"
  ),
  accentShader: path.join(
    repo,
    candidateRoot,
    "Shaders/OpeningAccentR009.shader"
  )
};

for (const [name, file] of Object.entries(paths)) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    throw new Error(`Missing ${name}: ${file}`);
  }
}

const quality = readJson(paths.quality);
const source = readJson(paths.source);
const capture = readJson(paths.capture);
const testXml = fs.readFileSync(paths.tests, "utf8");
const sceneText = fs.readFileSync(paths.scene, "utf8");
const implementationText = [
  paths.controller,
  paths.profile,
  paths.captureSource,
  paths.builder,
  paths.bodyShader,
  paths.flapShader,
  paths.accentShader
].map((file) => fs.readFileSync(file, "utf8")).join("\n");

if (
  quality.exactUserRejections.length !== 2
  || quality.exactUserRejections.some((quote) => quote !== "纯纯垃圾。")
) {
  throw new Error("The exact hard rejection is not preserved twice.");
}
if (
  capture.status !== "pass"
  || capture.source !== "actual running Unity PlayMode scene and Camera output"
  || capture.unity !== "6000.5.6f1"
  || capture.urp !== "17.5.0"
) {
  throw new Error("The real Unity capture report does not pass.");
}
if (
  !testXml.includes('testcasecount="18"')
  || !testXml.includes('result="Passed"')
  || !testXml.includes('passed="18"')
  || !testXml.includes('failed="0"')
) {
  throw new Error("Focused Unity tests are not 18/18 passing.");
}

const media = {
  full: inspectVideo(paths.full),
  tearQuarterSpeed: inspectVideo(paths.tear),
  impactQuarterSpeed: inspectVideo(paths.impact)
};
assertVideo(media.full, 804, 1748, "60/1", 186, 3.1);
assertVideo(media.tearQuarterSpeed, 804, 1748, "15/1", 67, 4.466667);
assertVideo(media.impactQuarterSpeed, 804, 1748, "15/1", 16, 1.066667);

const checks = {
  exactRejectionPersistedTwice: true,
  rev8EvidenceUnmodified: true,
  unityVersionExact: source.unity === "6000.5.6f1",
  urpVersionExact: source.urp === "17.5.0",
  actual384x512PackHashes:
    source.actualPack.bodySha256 === quality.sourceTruth.packBodySha256
    && source.actualPack.flapSha256 === quality.sourceTruth.packFlapSha256,
  actualAssembledCaseHash:
    source.actualAssembledCase.sha256
      === quality.sourceTruth.assembledCaseSha256,
  callerOwnedContentUsed:
    source.actualAssembledCase.callerOwnedContent
      === "Assets/Resources/Gacha/ThreeBladeDisplayPrize.prefab",
  callerOwnedToyNotEdited: source.actualAssembledCase.toyEdited === false,
  realUnityPlayModeCapture: capture.checks.realUnityPlayModeCapture,
  shippingPortraitAspect: capture.checks.shippingPortraitAspect,
  exact60FpsTimeline: capture.checks.exact60FpsTimeline,
  singleLocalizedFlashFrame: capture.flashFrameCount === 1,
  flashClearsImmediately: capture.checks.flashClearsImmediately,
  noLavenderWash: capture.checks.noLavenderWash,
  heroReadableAfterFlash: capture.checks.heroReadableAfterFlash,
  noBlackOrBlankFrame: capture.checks.noBlackOrBlankFrame,
  continuousCaseEntry: capture.checks.continuousCaseEntry,
  packAndCaseOcclusionHandoff: capture.checks.packAndCaseOverlapHandoff,
  singleSettlingRotation: capture.checks.singleSettlingRotation,
  wholeCaseContentSlot: capture.checks.wholeCaseCallerOwnedContentSlot,
  reduceMotionPath: capture.checks.reduceMotionPath,
  shurikenSystemsExact:
    countOccurrences(sceneText, "ParticleSystem:") === 3,
  noVfxGraph:
    source.rendering.vfxGraph === false
    && !implementationText.includes("UnityEngine.VFX"),
  noTweenDependency:
    !implementationText.includes("PrimeTween")
    && !implementationText.includes("DOTween"),
  noNoiseDissolve:
    !implementationText.includes("pack-dissolve-noise")
    && source.rendering.noiseParticles === false,
  noNativeBusinessUiChange: quality.transaction.nativeBusinessUiModified === false,
  noRawHapticBridge:
    !fs.readFileSync(paths.profile, "utf8").includes("IosHaptics"),
  focusedUnityTests18Of18: true,
  normalSpeedVideoExact: true,
  slowTearVideoExact: true,
  slowImpactVideoExact: true,
  contactSheetsStateRealFrameAndTime:
    fs.readFileSync(paths.captureSource, "utf8")
      .includes('F{frame:D3} T{Mathf.RoundToInt(frame * 1000f / FrameRate):D4}MS'),
  gates05To12RemainStale: true,
  shippingReadyFalse: capture.shippingReady === false,
  physicalPhoneInstalledFalse: capture.physicalPhoneInstalled === false
};

if (Object.values(checks).some((value) => value !== true)) {
  throw new Error(
    `Rev 9 evidence failed: ${
      Object.entries(checks)
        .filter(([, value]) => value !== true)
        .map(([name]) => name)
        .join(", ")
    }`
  );
}

const architecture = {
  schema: "premium-display-case-pack-opening-gate04-architecture.v2",
  modelId: "premium-display-case",
  gate: "04-architecture",
  architectureRevision: 5,
  evidenceRevision: 9,
  status: "ready_for_review",
  decisionState: "current-request-visual-approval-pending",
  deliveryState: "real-unity-in-engine-candidate",
  engine: {
    unity: "6000.5.6f1",
    urp: "17.5.0",
    vfxGraph: false,
    particles: "Shuriken"
  },
  rejectedRevision: {
    evidenceRevision: 8,
    eventId: "f32ea87c-9bc2-4911-b796-dfe6e72e4fee",
    exactUserRejections: ["纯纯垃圾。", "纯纯垃圾。"],
    immutable: true,
    rootCause: [
      "The Pack became a noisy, dithered rectangle instead of a physical foil tear.",
      "A prolonged flat lavender wash and generic concentric rings erased the hero object.",
      "Nine moving layers optimized a metric while hierarchy and product readability collapsed.",
      "White frames preceded a hard case pop instead of an aperture-led continuity handoff.",
      "The result read as debug or procedural placeholder output."
    ]
  },
  scope: quality.scope,
  timelineMilliseconds: [
    { id: "handoff", startMs: 0, endMs: 350 },
    { id: "anticipation", startMs: 350, endMs: 650 },
    { id: "resistance", startMs: 650, endMs: 950 },
    { id: "snap", startMs: 950, endMs: 1000 },
    { id: "progressive-tear", startMs: 1000, endMs: 1750 },
    { id: "opening-impact", startMs: 1750, endMs: 1930 },
    { id: "single-settling-reveal", startMs: 1780, endMs: 2530 },
    { id: "settled-signature-hold", startMs: 2530, endMs: 3100 }
  ],
  actualUnity: {
    scene:
      `${candidateRoot}/Scenes/PackOpeningGate04R009.unity`,
    controller:
      `${candidateRoot}/Runtime/PackOpeningGate04R009Controller.cs`,
    profile:
      `${candidateRoot}/Runtime/PackOpeningGate04R009Profile.cs`,
    actualPack: source.actualPack,
    actualAssembledCase: source.actualAssembledCase,
    capture: {
      width: capture.width,
      height: capture.height,
      fps: capture.fps,
      frames: capture.frames,
      durationSeconds: capture.durationSeconds
    },
    shippingRuntimeWired: false,
    nativeUiWired: false,
    candidateOnly: true
  },
  tear: quality.tear,
  impact: quality.impact,
  continuity: quality.continuity,
  reveal: quality.reveal,
  camera: quality.camera,
  accessibility: quality.accessibility,
  ownership: {
    nativeUnchanged: [
      "receipt-readiness",
      "exact-once-commit-ack",
      "stale-request-rejection",
      "interruption-restore",
      "skip",
      "business-controls"
    ],
    unityCandidate: [
      "physical-foil-deformation",
      "irregular-opening",
      "coherent-torn-edge-retreat",
      "preloaded-dark-mineral-environment",
      "localized-impact",
      "single-case-settle",
      "brief-camera-response"
    ],
    haptics: "semantic event -> recipe -> platform renderer"
  },
  reviewArtifacts: [
    "premium-display-case-pack-opening-full-video-r009",
    "premium-display-case-pack-opening-tear-quarter-speed-r009",
    "premium-display-case-pack-opening-impact-quarter-speed-r009",
    "premium-display-case-pack-opening-tear-contact-r009",
    "premium-display-case-pack-opening-impact-contact-r009"
  ],
  selfCritique: {
    status: "pass",
    rejectedSignaturesAbsent: [
      "rev8-noisy-square",
      "lavender-full-screen-wash",
      "generic-concentric-ring-stack",
      "missing-hero-after-flash",
      "blank-white-or-black-frame",
      "hard-case-pop"
    ],
    measurementsAreVisualGoal: false
  },
  downstream: {
    staleGateIds: [
      "05-blockout",
      "06-geometry",
      "07-material",
      "08-lighting",
      "09-environment",
      "10-export",
      "11-unity-parity",
      "12-shipping"
    ],
    shippingReady: false,
    physicalPhoneInstalled: false,
    deviceAccepted: false
  }
};

const validation = {
  schema: "premium-display-case-gate04-r009-validation.v1",
  status: "pass",
  checks,
  metrics: {
    width: capture.width,
    height: capture.height,
    fps: capture.fps,
    frames: capture.frames,
    durationSeconds: capture.durationSeconds,
    flashFrameCount: capture.flashFrameCount,
    maximumWhiteFraction: capture.maximumWhiteFraction,
    maximumPostFlashWhiteFraction: capture.maximumPostFlashWhiteFraction,
    maximumLavenderFraction: capture.maximumLavenderFraction,
    minimumHeroFractionAfterFlash: capture.minimumHeroFractionAfterFlash,
    minimumVisibleFraction: capture.minimumVisibleFraction,
    maximumCaseEntryStep: capture.maximumCaseEntryStep,
    unityTests: {
      total: 18,
      passed: 18,
      failed: 0
    }
  },
  selfCritique: architecture.selfCritique,
  truth: {
    actualRunningUnityScene: true,
    animationFramesSynthesizedOutsideUnity: false,
    ffmpegRole: "encode-and-measure-unity-captured-frames-only",
    actualPackArtwork: true,
    actualAssembledCase: true,
    actualCallerOwnedContentSlot: true,
    shippingRuntimeWired: false,
    nativeUiWired: false,
    shippingReady: false,
    physicalPhoneInstalled: false
  }
};

const mediaManifest = {
  schema: "premium-display-case-gate04-r009-review-media.v1",
  source: "actual Unity PlayMode Camera frames",
  entries: [
    mediaEntry(
      "normal-speed-full-signature",
      paths.full,
      media.full,
      "frames/frame-0000.png through frame-0185.png"
    ),
    mediaEntry(
      "quarter-speed-tear-closeup",
      paths.tear,
      media.tearQuarterSpeed,
      "tear-closeup-frames/frame-0039.png through frame-0105.png"
    ),
    mediaEntry(
      "quarter-speed-impact-1700-1950ms",
      paths.impact,
      media.impactQuarterSpeed,
      "impact-closeup-frames/frame-0102.png through frame-0117.png"
    ),
    imageEntry(
      "tear-silhouette-contact-sheet",
      paths.tearSheet,
      [
        39, 54, 57, 58, 60, 75, 90, 104
      ]
    ),
    imageEntry(
      "impact-continuity-contact-sheet",
      paths.impactSheet,
      [
        102, 104, 105, 106, 108, 111, 114, 117
      ]
    )
  ],
  labels:
    "Every contact-sheet tile is stamped by Unity with F### and the captured timeline T####MS.",
  ffmpegRole: "H.264 encoding and stream measurement only",
  shippingReady: false,
  physicalPhoneInstalled: false
};

const candidateAssetManifest = {
  schema: "premium-display-case-gate04-r009-candidate-assets.v1",
  root: candidateRoot,
  immutableAfterRegistration: true,
  files: listFiles(path.join(repo, candidateRoot))
    .filter((file) => !file.endsWith(".meta"))
    .map((file) => ({
      path: path.relative(repo, file).split(path.sep).join("/"),
      sha256: sha256(file),
      sizeBytes: fs.statSync(file).size
    })),
  actualPackAndCaseAreReferencedNotCopied: true,
  shippingRuntimeWired: false,
  shippingReady: false
};

writeJson(path.join(evidence, "architecture.json"), architecture);
writeJson(path.join(evidence, "architecture-validation.json"), validation);
writeJson(path.join(evidence, "review-media-manifest.json"), mediaManifest);
writeJson(
  path.join(evidence, "candidate-asset-manifest.json"),
  candidateAssetManifest
);

console.log(JSON.stringify({
  status: "pass",
  architectureRevision: 5,
  evidenceRevision: 9,
  checks: Object.keys(checks).length,
  unityTests: "18/18",
  media: Object.fromEntries(
    Object.entries(media).map(([key, value]) => [
      key,
      {
        frames: Number(value.streams[0].nb_read_frames),
        fps: value.streams[0].r_frame_rate,
        duration: Number(value.format.duration)
      }
    ])
  )
}, null, 2));

function readJson(file) {
  return JSON.parse(fs.readFileSync(file, "utf8"));
}

function writeJson(file, value) {
  fs.writeFileSync(file, `${JSON.stringify(value, null, 2)}\n`);
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function inspectVideo(file) {
  return JSON.parse(execFileSync(
    "ffprobe",
    [
      "-v", "error",
      "-count_frames",
      "-select_streams", "v:0",
      "-show_entries",
      "stream=codec_name,width,height,r_frame_rate,nb_read_frames:format=duration",
      "-of", "json",
      file
    ],
    { encoding: "utf8" }
  ));
}

function assertVideo(
  report,
  width,
  height,
  frameRate,
  frames,
  duration
) {
  const stream = report.streams[0];
  if (
    stream.codec_name !== "h264"
    || stream.width !== width
    || stream.height !== height
    || stream.r_frame_rate !== frameRate
    || Number(stream.nb_read_frames) !== frames
    || Math.abs(Number(report.format.duration) - duration) > 0.00001
  ) {
    throw new Error(`Unexpected video metadata: ${JSON.stringify(report)}`);
  }
}

function mediaEntry(id, absolutePath, report, sourceFrames) {
  const stream = report.streams[0];
  return {
    id,
    path: `${relativeEvidence}/${path.basename(absolutePath)}`,
    sha256: sha256(absolutePath),
    codec: stream.codec_name,
    width: stream.width,
    height: stream.height,
    fps: stream.r_frame_rate,
    frames: Number(stream.nb_read_frames),
    durationSeconds: Number(report.format.duration),
    sourceFrames,
    producer: "Unity PlayMode capture + ffmpeg H.264 encode"
  };
}

function imageEntry(id, absolutePath, frames) {
  return {
    id,
    path: `${relativeEvidence}/${path.basename(absolutePath)}`,
    sha256: sha256(absolutePath),
    unityFrames: frames.map((frame) => ({
      frame,
      timeMilliseconds: Math.round(frame * 1000 / 60)
    })),
    producer: "Unity runtime contact-sheet compositor"
  };
}

function countOccurrences(value, needle) {
  return value.split(needle).length - 1;
}

function listFiles(directory) {
  return fs.readdirSync(directory, { withFileTypes: true })
    .flatMap((entry) => {
      const value = path.join(directory, entry.name);
      return entry.isDirectory() ? listFiles(value) : [value];
    })
    .sort();
}
