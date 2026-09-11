#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const canonicalRoot = "/Users/jiawei.zhou/Documents/Fidgeting app/unity/FidgetingApp";
const targetRoot = "/tmp/FidgetingApp-PackOpening-R014-Isolated-20260831";
const templateRoot = path.join(
  canonicalRoot,
  "ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r014/isolated-template"
);

if (fs.existsSync(targetRoot)) {
  throw new Error(`Refusing to overwrite isolated project: ${targetRoot}`);
}
if (!fs.existsSync(templateRoot)) {
  throw new Error(`Missing isolated template: ${templateRoot}`);
}

function hash(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function copyFile(relativeSource, relativeDestination) {
  const source = path.join(canonicalRoot, relativeSource);
  const destination = path.join(targetRoot, relativeDestination);
  if (!fs.existsSync(source)) {
    throw new Error(`Missing required source: ${relativeSource}`);
  }
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.copyFileSync(source, destination);
  return {
    source: relativeSource,
    destination: relativeDestination,
    sha256: hash(source),
    destinationSha256: hash(destination)
  };
}

function copyTree(relativeSource, relativeDestination) {
  const source = path.join(canonicalRoot, relativeSource);
  const destination = path.join(targetRoot, relativeDestination);
  if (!fs.existsSync(source)) {
    throw new Error(`Missing required source directory: ${relativeSource}`);
  }
  fs.mkdirSync(path.dirname(destination), { recursive: true });
  fs.cpSync(source, destination, { recursive: true, force: false });
  return { source: relativeSource, destination: relativeDestination };
}

fs.mkdirSync(path.join(targetRoot, "Assets"), { recursive: true });
fs.mkdirSync(path.join(targetRoot, "Packages"), { recursive: true });
fs.mkdirSync(path.join(targetRoot, "ProjectSettings"), { recursive: true });

fs.writeFileSync(
  path.join(targetRoot, "Packages/manifest.json"),
  `${JSON.stringify({
    dependencies: {
      "com.unity.render-pipelines.universal": "17.5.0",
      "com.unity.test-framework": "1.7.0",
      "com.unity.modules.imageconversion": "1.0.0",
      "com.unity.modules.jsonserialize": "1.0.0",
      "com.unity.modules.physics": "1.0.0",
      "com.unity.modules.ui": "1.0.0",
      "com.unity.modules.uielements": "1.0.0"
    }
  }, null, 2)}\n`,
  "utf8"
);
fs.writeFileSync(
  path.join(targetRoot, "ProjectSettings/ProjectVersion.txt"),
  "m_EditorVersion: 6000.5.6f1\nm_EditorVersionWithRevision: 6000.5.6f1 (0e0577a1a2ac)\n",
  "utf8"
);

const files = [
  copyFile(
    "Assets/_DisplayCase/Candidates/PackOpeningGate04R014/Imported/PackOpeningGate04R014PackOnlyRig.fbx",
    "Assets/Source/R014/PackOpeningGate04R014PackOnlyRig.fbx"
  ),
  copyFile(
    "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-body.png",
    "Assets/Source/Pack/gacha-pack-standard-body.png"
  ),
  copyFile(
    "Assets/Plugins/iOS/GachaPacks/gacha-pack-standard-flap.png",
    "Assets/Source/Pack/gacha-pack-standard-flap.png"
  ),
  copyFile(
    "Assets/_DisplayCase/Candidates/PackOpeningGate04R014/Runtime/PackOpeningGate04R014Profile.cs",
    "Assets/Source/R014/PackOpeningGate04R014Profile.cs"
  ),
  copyFile(
    "Assets/_DisplayCase/Candidates/PackOpeningGate04R014/Shaders/MakeItShineCc0PackR014.shader",
    "Assets/Source/R014/MakeItShineCc0PackR014.shader"
  ),
  copyFile(
    "Assets/_DisplayCase/Candidates/PackOpeningGate04R014/Shaders/MakeItShineCc0ContourSweepR014.shader",
    "Assets/Source/R014/MakeItShineCc0ContourSweepR014.shader"
  ),
  copyFile(
    "Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/MakeItShineCc0EffectCurves.cs",
    "Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/MakeItShineCc0EffectCurves.cs"
  ),
  copyFile(
    "Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/MakeItShineCc0Masks.hlsl",
    "Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/MakeItShineCc0Masks.hlsl"
  ),
  copyFile(
    "Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/SOURCE_CONTRACT.json",
    "Assets/_DisplayCase/Runtime/MakeItShineCc0Effects/SOURCE_CONTRACT.json"
  ),
  copyFile(
    "ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-013/iterations/iteration-11-full-size-self-rejection/source-to-canonical-mapping.json",
    "Assets/Source/CC0/R013-source-audit.json"
  ),
  copyFile(
    "Assets/Resources/EnvironmentBackgrounds/canyon-unified-ledgestone-v1-2x.png",
    "Assets/Source/Environment/canyon-unified-ledgestone-v1-2x.png"
  )
];

const trees = [
  copyTree(
    "Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001/Models",
    "Assets/Source/PremiumDisplayCase/Models"
  ),
  copyTree(
    "Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001/Materials",
    "Assets/Source/PremiumDisplayCase/Materials"
  ),
  copyTree(
    "Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001/Shaders",
    "Assets/Source/PremiumDisplayCase/Shaders"
  ),
  copyTree(
    "Assets/_DisplayCase/Candidates/PremiumDisplayCaseGate11R001/Prefabs",
    "Assets/Source/PremiumDisplayCase/Prefabs"
  ),
  copyTree(
    "ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r014/isolated-template/Assets/IsolatedProof",
    "Assets/IsolatedProof"
  )
];

for (const item of files) {
  if (item.sha256 !== item.destinationSha256) {
    throw new Error(`Hash copy failed: ${item.source}`);
  }
}

fs.writeFileSync(
  path.join(targetRoot, "Assets/Source/isolated-source-manifest.json"),
  `${JSON.stringify({
    schema: "premium-display-case-gate04-r014-isolated-source.v1",
    isolatedCandidate: true,
    canonicalIntegration: false,
    shippingReady: false,
    physicalDeviceInstalled: false,
    caseRepresentation: "unchanged Gate 11 validated assembled case FBX and prefab",
    contentSlot: "preserved empty caller-owned ContentSlot; no toy source copied or modified",
    copiedFiles: files,
    copiedTrees: trees,
    rejectedSourceAssets: [
      "VFX_BoosterActivation.vfx",
      "VFXG_LightingStrike.vfx",
      "VFX_BoosterExplosion.vfx",
      "all sample Booster/Card models and branded artwork"
    ]
  }, null, 2)}\n`,
  "utf8"
);
console.log(JSON.stringify({ targetRoot, copiedFiles: files.length, copiedTrees: trees.length }));
