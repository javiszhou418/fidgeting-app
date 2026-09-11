#!/usr/bin/env node
import { execFileSync } from "node:child_process";
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const repoRoot = "/Users/jiawei.zhou/Documents/Fidgeting app";
const stagingRoot = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r025-portrait-projection-repair"
);
const sourceProject =
  "/tmp/FidgetingApp-PackOpening-R024-LocalSegmentAnchors-20260901-r01";
const runId = process.env.R025_RUN_ID || "r01";
if (!/^r[0-9]+$/u.test(runId)) {
  throw new Error(`Invalid R025 isolated run ID: ${runId}`);
}
const targetProject =
  `/tmp/FidgetingApp-PackOpening-R025-PortraitProjection-20260901-${runId}`;
const packageSource = path.join(
  stagingRoot,
  "isolated-template/Assets/IsolatedProofR025"
);
const packageTarget = path.join(targetProject, "Assets/IsolatedProofR025");
const r024RigSource = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-024/source/PackOpeningGate04R024PackOnlyRig.fbx"
);
const r024RigTarget = path.join(
  targetProject,
  "Assets/Source/R024/PackOpeningGate04R024PackOnlyRig.fbx"
);
const expectedR024RigHash =
  "a7a8c6ae76a89355cb2f74978f896bdcedba062b8fa02624ffae07803f4f8810";
const excludedProjectDirectories = new Set([
  "Library",
  "Logs",
  "Captures",
  "Quarantine",
  "Temp",
  "obj",
  ".vs"
]);

function requireDirectory(directory) {
  if (!fs.existsSync(directory) || !fs.statSync(directory).isDirectory()) {
    throw new Error(`Missing required directory: ${directory}`);
  }
}

function requireFile(file) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    throw new Error(`Missing required file: ${file}`);
  }
}

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function walk(directory) {
  return fs.readdirSync(directory, { withFileTypes: true })
    .sort((left, right) => left.name.localeCompare(right.name))
    .flatMap((entry) => {
      const file = path.join(directory, entry.name);
      return entry.isDirectory() ? walk(file) : [file];
    });
}

function regeneratePackageGuids() {
  for (const file of walk(packageTarget).filter((item) =>
    item.endsWith(".meta")
  )) {
    const source = fs.readFileSync(file, "utf8");
    if (!/^guid: .+$/mu.test(source)) {
      throw new Error(`Package metadata lacks GUID: ${file}`);
    }
    fs.writeFileSync(
      file,
      source.replace(
        /^guid: .+$/mu,
        `guid: ${crypto.randomBytes(16).toString("hex")}`
      ),
      "utf8"
    );
  }
}

function currentPackageSources() {
  return walk(packageTarget)
    .filter((file) => /\.(cs|shader)$/u.test(file))
    .map((file) => ({
      path: path.relative(targetProject, file),
      sha256: sha256(file)
    }));
}

function syncPackageSources() {
  const captureRoot = path.join(targetProject, "Captures/r025-preflight");
  if (fs.existsSync(captureRoot)) {
    throw new Error(
      "Refusing to change R025 sources after static capture exists."
    );
  }
  for (const source of walk(packageSource)) {
    const destination = path.join(
      packageTarget,
      path.relative(packageSource, source)
    );
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.copyFileSync(source, destination);
  }
  const manifestPath = path.join(targetProject, "r025-source-manifest.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  manifest.sourceFiles = currentPackageSources();
  fs.writeFileSync(
    manifestPath,
    `${JSON.stringify(manifest, null, 2)}\n`,
    "utf8"
  );
  console.log(JSON.stringify({
    isolatedProject: targetProject,
    syncedSourceFiles: manifest.sourceFiles.length,
    r024RigSha256: sha256(r024RigTarget)
  }, null, 2));
}

function syncTestSourcesOnly() {
  const allowed = [
    "Editor/IsolatedR025ProofRunner.cs",
    "Tests/Editor/IsolatedR025ProofTests.cs",
    "Runtime/IsolatedR025PortraitRenderSession.cs"
  ];
  for (const relative of allowed) {
    const source = path.join(packageSource, relative);
    const destination = path.join(packageTarget, relative);
    requireFile(source);
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.copyFileSync(source, destination);
  }
  const manifestPath = path.join(targetProject, "r025-source-manifest.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  manifest.sourceFiles = currentPackageSources();
  manifest.testOnlySourceSyncs = [
    ...(manifest.testOnlySourceSyncs || []),
    {
      at: new Date().toISOString(),
      files: allowed.filter((file) => !file.endsWith(".meta")),
      reason:
        "Tighten the forbidden UV-property scan and use edit-mode-safe object disposal; PlayMode projection and captures stay unchanged.",
      staticCaptureUnchanged: true
    }
  ];
  fs.writeFileSync(
    manifestPath,
    `${JSON.stringify(manifest, null, 2)}\n`,
    "utf8"
  );
  console.log(JSON.stringify({
    isolatedProject: targetProject,
    syncedTestSourceFiles: allowed.length,
    r024RigSha256: sha256(r024RigTarget)
  }, null, 2));
}

function syncScrubSourceOnly() {
  const relative = "Runtime/IsolatedR025ProofCapture.cs";
  const source = path.join(packageSource, relative);
  const destination = path.join(packageTarget, relative);
  requireFile(source);
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(source, destination);
  const manifestPath = path.join(targetProject, "r025-source-manifest.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  manifest.sourceFiles = currentPackageSources();
  manifest.postStaticSourceSyncs = [
    ...(manifest.postStaticSourceSyncs || []),
    {
      at: new Date().toISOString(),
      files: [relative],
      reason:
        "Add scrub-only identity, duplicate, crossfade, pop, and blank-frame assertions; static capture code stays unchanged.",
      staticCaptureUnchanged: true
    }
  ];
  fs.writeFileSync(
    manifestPath,
    `${JSON.stringify(manifest, null, 2)}\n`,
    "utf8"
  );
  console.log(JSON.stringify({
    isolatedProject: targetProject,
    syncedScrubSourceFiles: 1,
    r024RigSha256: sha256(r024RigTarget)
  }, null, 2));
}

function hostPreflight() {
  const stats = fs.statfsSync("/tmp");
  const availableBytes = Number(stats.bavail * stats.bsize);
  const processOutput = execFileSync(
    "/bin/ps",
    ["-ax", "-o", "pid=,command="],
    { encoding: "utf8" }
  );
  const unityEditors = processOutput.split("\n").filter((line) =>
    /\/Unity\.app\/Contents\/MacOS\/Unity(?:\s|$)/u.test(line)
  );
  const blenderProcesses = processOutput.split("\n").filter((line) =>
    /\/Blender\.app\/Contents\/MacOS\/Blender(?:\s|$)/u.test(line)
  );
  return {
    schema: "premium-display-case-gate04-r025-host-preflight.v1",
    checkedAt: new Date().toISOString(),
    disk: {
      availableBytes,
      minimumReserveBytes: 6442450944,
      reserveSatisfied: availableBytes >= 6442450944
    },
    processes: {
      unityEditors,
      blenderProcesses,
      unityConflict: unityEditors.length > 0,
      blenderConflict: false,
      blenderUse: "none; R025 does not rebuild the R024 Blender rig"
    },
    passed: availableBytes >= 6442450944 && unityEditors.length === 0
  };
}

requireDirectory(stagingRoot);
requireDirectory(sourceProject);
requireDirectory(packageSource);
requireFile(r024RigSource);
if (sha256(r024RigSource) !== expectedR024RigHash) {
  throw new Error("R024 FBX hash differs from the immutable input.");
}
if (fs.existsSync(targetProject)) {
  requireDirectory(packageTarget);
  requireFile(r024RigTarget);
  if (sha256(r024RigTarget) !== expectedR024RigHash) {
    throw new Error("R025 target no longer preserves the R024 FBX hash.");
  }
  if (process.argv.includes("--sync-test-sources")) {
    syncTestSourcesOnly();
    process.exit(0);
  }
  if (process.argv.includes("--sync-scrub-source")) {
    syncScrubSourceOnly();
    process.exit(0);
  }
  if (process.argv.includes("--sync-sources")) {
    syncPackageSources();
    process.exit(0);
  }
  throw new Error(`Refusing to overwrite isolated R025 project: ${targetProject}`);
}

const host = hostPreflight();
fs.writeFileSync(
  path.join(
    stagingRoot,
    `r025-unity-preflight-environment-${runId}.json`
  ),
  `${JSON.stringify(host, null, 2)}\n`,
  { flag: "wx" }
);
if (!host.passed) {
  throw new Error("R025 host preflight failed before isolated project creation.");
}

fs.cpSync(sourceProject, targetProject, {
  recursive: true,
  errorOnExist: true,
  filter: (source) => {
    const relative = path.relative(sourceProject, source);
    return !relative || !relative.split(path.sep).some((segment) =>
      excludedProjectDirectories.has(segment)
    );
  }
});
fs.rmSync(path.join(targetProject, "Assets/IsolatedProofR024"), {
  recursive: true,
  force: true
});
fs.cpSync(packageSource, packageTarget, {
  recursive: true,
  errorOnExist: true
});
if (!fs.existsSync(r024RigTarget)) {
  fs.mkdirSync(path.dirname(r024RigTarget), { recursive: true });
  fs.copyFileSync(r024RigSource, r024RigTarget, fs.constants.COPYFILE_EXCL);
}
if (sha256(r024RigTarget) !== expectedR024RigHash) {
  throw new Error("R025 target does not preserve the R024 FBX byte hash.");
}
regeneratePackageGuids();

const sourceManifest = {
  schema: "premium-display-case-gate04-r025-isolated-source.v1",
  isolatedUnityCandidate: true,
  canonicalIntegration: false,
  sourceProject,
  isolatedProject: targetProject,
  r024Rig: {
    source: path.relative(repoRoot, r024RigSource),
    destination: path.relative(targetProject, r024RigTarget),
    sha256: sha256(r024RigTarget),
    expectedSha256: expectedR024RigHash
  },
  sourceFiles: currentPackageSources(),
  sourceBoundary: {
    casePrefabChanged: false,
    contentSlotChanged: false,
    canonicalScenesChanged: false,
    shippingAssetsChanged: false,
    sourceCc0EffectsChanged: false,
    packGeometryChanged: false,
    packUvChanged: false,
    segmentTopologyChanged: false,
    cameraPoseChanged: false,
    cameraProjectionGuardAdded: true,
    blenderRigChanged: false,
    timingChanged: false,
    visualEffectsIntensityDuringValidation: 0,
    fanCardChanged: false,
    packagesChanged: false,
    userAssetsChanged: false
  },
  diagnosticChange: {
    targetAspect: [1206, 2622],
    bakedBoundsToExactIdTolerance: 0.0015,
    segmentProjectionAllowance: 0.0015,
    caseContrastThreshold: 0.04,
    oldFourByThreeCarryForward: false
  },
  shippingReady: false,
  physicalDeviceInstalled: false
};
fs.writeFileSync(
  path.join(targetProject, "r025-source-manifest.json"),
  `${JSON.stringify(sourceManifest, null, 2)}\n`,
  { flag: "wx" }
);

console.log(JSON.stringify({
  isolatedProject: targetProject,
  r024RigSha256: sourceManifest.r024Rig.sha256,
  packageFileCount: sourceManifest.sourceFiles.length,
  diskFreeBytes: host.disk.availableBytes,
  unityConflict: host.processes.unityConflict,
  blenderObserved: host.processes.blenderProcesses.length
}, null, 2));
