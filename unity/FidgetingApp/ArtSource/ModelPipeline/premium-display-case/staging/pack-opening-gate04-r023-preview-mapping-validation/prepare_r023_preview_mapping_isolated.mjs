#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const repoRoot = "/Users/jiawei.zhou/Documents/Fidgeting app";
const stagingRoot = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r023-preview-mapping-validation"
);
const sourceProject =
  "/tmp/FidgetingApp-PackOpening-R021-OpenMouth-20260901-r02";
const targetProject =
  "/tmp/FidgetingApp-PackOpening-R023-PreviewMapping-20260901-r01";
const packageSource = path.join(
  stagingRoot,
  "isolated-template/Assets/IsolatedProofR022"
);
const packageTarget = path.join(targetProject, "Assets/IsolatedProofR022");
const r022RigSource = path.join(
  stagingRoot,
  "PackOpeningGate04R022PackOnlyRig.fbx"
);
const expectedR022FbxSha256 =
  "9b3ef4c2e5ca77cd0f53b5ff07c9e47bf2d9f0d367e037a5e711099d7b8ee89a";
const r022RigTarget = path.join(
  targetProject,
  "Assets/Source/R022/PackOpeningGate04R022PackOnlyRig.fbx"
);
const r018ControlSource = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r018-coordinate-orientation/PackOpeningGate04R018PackOnlyRig.fbx"
);
const r018ControlTarget = path.join(
  targetProject,
  "Assets/Source/R018Control/PackOpeningGate04R018LeftStripControl.fbx"
);
const r018RigMeta = path.join(
  sourceProject,
  "Assets/Source/R018/PackOpeningGate04R018PackOnlyRig.fbx.meta"
);
const r017ControlTarget = path.join(
  targetProject,
  "Assets/Source/R017Control/PackOpeningGate04R017MirrorControl.fbx"
);
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
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const file = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(file) : [file];
  });
}

function copyModelMeta(destination) {
  const source = fs.readFileSync(r018RigMeta, "utf8").replace(
    /^guid: .+$/mu,
    `guid: ${crypto.randomBytes(16).toString("hex")}`
  );
  fs.writeFileSync(`${destination}.meta`, source, { flag: "wx" });
}

function regeneratePackageGuids() {
  for (const file of walk(packageTarget).filter((item) => item.endsWith(".meta"))) {
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
  for (const source of walk(packageSource).filter(
    (file) => /\.(cs|shader)$/u.test(file)
  )) {
    const destination = path.join(
      packageTarget,
      path.relative(packageSource, source)
    );
    fs.mkdirSync(path.dirname(destination), { recursive: true });
    fs.copyFileSync(source, destination);
  }
  const manifestPath = path.join(targetProject, "r023-source-manifest.json");
  const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
  manifest.sourceFiles = currentPackageSources();
  fs.writeFileSync(
    manifestPath,
    `${JSON.stringify(manifest, null, 2)}\n`,
    "utf8"
  );
  return manifest.sourceFiles.length;
}

requireDirectory(stagingRoot);
requireDirectory(sourceProject);
requireDirectory(packageSource);
requireFile(r022RigSource);
requireFile(r018ControlSource);
requireFile(r018RigMeta);
if (fs.existsSync(targetProject)) {
  if (process.argv.includes("--sync-sources")) {
    requireDirectory(packageTarget);
    console.log(JSON.stringify({
      isolatedProject: targetProject,
      syncedSourceFiles: syncPackageSources()
    }, null, 2));
    process.exit(0);
  }
  throw new Error(`Refusing to overwrite isolated R023 project: ${targetProject}`);
}

fs.cpSync(sourceProject, targetProject, {
  recursive: true,
  errorOnExist: true,
  filter: (source) => {
    const relative = path.relative(sourceProject, source);
    return !relative
      || !relative
        .split(path.sep)
        .some((segment) => excludedProjectDirectories.has(segment));
  }
});
fs.cpSync(packageSource, packageTarget, {
  recursive: true,
  errorOnExist: true
});
fs.mkdirSync(path.dirname(r022RigTarget), { recursive: true });
fs.copyFileSync(r022RigSource, r022RigTarget, fs.constants.COPYFILE_EXCL);
copyModelMeta(r022RigTarget);
requireFile(r017ControlTarget);
requireFile(r018ControlTarget);
regeneratePackageGuids();

const manifest = {
  schema: "premium-display-case-gate04-r023-preview-mapping-isolated-source.v1",
  isolatedUnityCandidate: true,
  canonicalIntegration: false,
  sourceProject,
  isolatedProject: targetProject,
  r022Rig: {
    source: path.relative(repoRoot, r022RigSource),
    destination: path.relative(targetProject, r022RigTarget),
    sha256: sha256(r022RigTarget)
  },
  r018LeftStripControl: {
    source: path.relative(repoRoot, r018ControlSource),
    destination: path.relative(targetProject, r018ControlTarget),
    sha256: sha256(r018ControlTarget),
    expectedR018Hash:
      "affe0a519712596660800dffb7d6b33126886defcaee9a33a658e97a79ca2f46"
  },
  r017MirrorControl: {
    source: "inherited from immutable isolated R018 source project",
    destination: path.relative(targetProject, r017ControlTarget),
    sha256: sha256(r017ControlTarget),
    expectedR017Hash:
      "1a9c8f5b066cc2a24cf629c0a0ffa9eaaec05279af0e0171ab2f341731dabe66"
  },
  sourceFiles: currentPackageSources(),
  sourceBoundary: {
    casePrefabChanged: false,
    contentSlotChanged: false,
    canonicalScenesChanged: false,
    shippingAssetsChanged: false,
    sourceCc0EffectsChanged: false,
    camerasChanged: false,
    candidateCaseRelationChanged: false,
    candidateMouthBounceLightChanged: false,
    topSealUvClipRemoved: true,
    mouthGeometryChanged: "independent physical 48-segment mouth",
    cavityBackWallSegmented: true,
    linerDepthMeters: 0.0055,
    topSealUsesGeometryOnly: true,
    blenderPreviewMappingOnly: true,
    exportedFbxByteIdenticalToR022: true,
    unityMaterialMappingChanged: false,
    particleSettingsChanged: false,
    timingChanged: false,
    visualEffectsIntensityDuringPreflight: 0
  },
  shippingReady: false,
  physicalDeviceInstalled: false
};
if (manifest.r018LeftStripControl.sha256
  !== manifest.r018LeftStripControl.expectedR018Hash) {
  throw new Error("R018 left-strip control no longer matches immutable R018 input.");
}
if (manifest.r017MirrorControl.sha256
  !== manifest.r017MirrorControl.expectedR017Hash) {
  throw new Error("R017 mirror control no longer matches the immutable R017 input.");
}
if (manifest.r022Rig.sha256 !== expectedR022FbxSha256) {
  throw new Error("R023 must import the exact immutable R022 FBX.");
}
fs.writeFileSync(
  path.join(targetProject, "r023-source-manifest.json"),
  `${JSON.stringify(manifest, null, 2)}\n`,
  { flag: "wx" }
);

console.log(JSON.stringify({
  isolatedProject: targetProject,
  r022RigSha256: manifest.r022Rig.sha256,
  r018ControlSha256: manifest.r018LeftStripControl.sha256,
  r017MirrorControlSha256: manifest.r017MirrorControl.sha256,
  packageFileCount: manifest.sourceFiles.length
}, null, 2));
