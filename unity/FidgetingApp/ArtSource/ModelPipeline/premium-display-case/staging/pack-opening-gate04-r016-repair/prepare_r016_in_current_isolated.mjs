#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const repoRoot = "/Users/jiawei.zhou/Documents/Fidgeting app";
const canonicalRoot = path.join(repoRoot, "unity/FidgetingApp");
const stagingRoot = path.join(
  canonicalRoot,
  "ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r016-repair"
);
const isolatedRoot = "/tmp/FidgetingApp-PackOpening-R016-Repair-20260831";
const templateRoot = path.join(stagingRoot, "isolated-template/Assets/IsolatedProofR016");
const rigSource = path.join(
  stagingRoot,
  "PackOpeningGate04R016PackOnlyRig.fbx"
);
const targetTemplate = path.join(isolatedRoot, "Assets/IsolatedProofR016");
const targetRigRoot = path.join(isolatedRoot, "Assets/Source/R016");
const targetRig = path.join(targetRigRoot, "PackOpeningGate04R016PackOnlyRig.fbx");

function sha256(file) {
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function requireFile(file) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    throw new Error(`Missing required file: ${file}`);
  }
}

for (const directory of [isolatedRoot, templateRoot]) {
  if (!fs.existsSync(directory) || !fs.statSync(directory).isDirectory()) {
    throw new Error(`Missing required directory: ${directory}`);
  }
}
requireFile(rigSource);
if (fs.existsSync(targetTemplate) || fs.existsSync(targetRigRoot)) {
  throw new Error("R016 isolated source already exists; refusing to overwrite.");
}

fs.cpSync(templateRoot, targetTemplate, { recursive: true, force: false });
fs.mkdirSync(targetRigRoot, { recursive: false });
fs.copyFileSync(rigSource, targetRig, fs.constants.COPYFILE_EXCL);

const sourceFiles = [];
function collect(root, base = root) {
  for (const entry of fs.readdirSync(root, { withFileTypes: true })) {
    const absolute = path.join(root, entry.name);
    if (entry.isDirectory()) {
      collect(absolute, base);
    } else {
      sourceFiles.push({
        path: path.relative(base, absolute),
        sha256: sha256(absolute)
      });
    }
  }
}
collect(templateRoot);

const copiedSources = [
  {
    source: path.relative(canonicalRoot, rigSource),
    destination: "Assets/Source/R016/PackOpeningGate04R016PackOnlyRig.fbx",
    sha256: sha256(rigSource),
    destinationSha256: sha256(targetRig)
  },
  ...[
    "Assets/Source/Pack/gacha-pack-standard-body.png",
    "Assets/Source/Pack/gacha-pack-standard-flap.png",
    "Assets/Source/PremiumDisplayCase/Prefabs/PresentationRoot.prefab",
    "Assets/Source/Environment/canyon-unified-ledgestone-v1-2x.png",
    "Assets/IsolatedProof/Generated/IsolatedR014URPFixed.asset",
    "Assets/IsolatedProof/Generated/IsolatedR014Renderer.asset"
  ].map((destination) => ({
    source: destination,
    destination,
    sha256: null,
    retainedFromRecoveredR014Project: true
  }))
];

fs.writeFileSync(
  path.join(isolatedRoot, "r016-source-manifest.json"),
  `${JSON.stringify(
    {
      schema: "premium-display-case-gate04-r016-isolated-source.v1",
      isolatedUnityCandidate: true,
      canonicalIntegration: false,
      shippingReady: false,
      physicalDeviceInstalled: false,
      caseRepresentation:
        "unchanged Gate 11 validated assembled case FBX and prefab",
      contentSlot:
        "preserved caller-owned ContentSlot; no toy was copied, attached, or modified",
      r015EvidencePreserved: true,
      recoveredRenderer:
        "R014 isolated URP17 default renderer retained without modification",
      copiedSources,
      runtimeSourceFiles: sourceFiles,
      rejectedExternalAssets: [
        "Make It Shine sample Booster/Card models",
        "Make It Shine branded artwork",
        "VFX_BoosterActivation.vfx",
        "VFXG_LightingStrike.vfx",
        "VFX_BoosterExplosion.vfx"
      ]
    },
    null,
    2
  )}\n`,
  "utf8"
);

console.log(
  JSON.stringify(
    {
      isolatedRoot,
      rigSha256: sha256(targetRig),
      sourceFiles: sourceFiles.length
    },
    null,
    2
  )
);
