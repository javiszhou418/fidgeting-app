#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";

const repoRoot = "/Users/jiawei.zhou/Documents/Fidgeting app";
const r024Evidence = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture/rev-024"
);
const stagingRoot = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r025-portrait-projection-repair"
);
const sourceTemplate = path.join(
  r024Evidence,
  "source/isolated-template/Assets/IsolatedProofR024"
);
const targetTemplate = path.join(
  stagingRoot,
  "isolated-template/Assets/IsolatedProofR025"
);
const r024Rig = path.join(
  r024Evidence,
  "source/PackOpeningGate04R024PackOnlyRig.fbx"
);
const expectedR024RigHash =
  "a7a8c6ae76a89355cb2f74978f896bdcedba062b8fa02624ffae07803f4f8810";

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

function renameR024Paths(directory) {
  for (const file of walk(directory).sort(
    (left, right) => right.length - left.length
  )) {
    const renamed = file.replaceAll("R024", "R025");
    if (renamed !== file) {
      fs.renameSync(file, renamed);
    }
  }
}

function transformPackageSource(directory) {
  for (const file of walk(directory).filter((item) =>
    /\.(cs|shader|meta)$/u.test(item)
  )) {
    let source = fs.readFileSync(file, "utf8")
      .replaceAll("R024", "R025")
      .replaceAll("r024", "r025");
    source = source.replaceAll(
      "Assets/Source/R025/PackOpeningGate04R025PackOnlyRig.fbx",
      "Assets/Source/R024/PackOpeningGate04R024PackOnlyRig.fbx"
    );
    fs.writeFileSync(file, source, "utf8");
  }
}

function rejectionRecord(revision, filename) {
  const file = path.join(
    repoRoot,
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/04-architecture",
    revision,
    filename
  );
  requireFile(file);
  return {
    revision: revision.toUpperCase(),
    path: path.relative(repoRoot, file),
    sha256: sha256(file)
  };
}

requireDirectory(r024Evidence);
requireDirectory(sourceTemplate);
requireFile(r024Rig);
if (sha256(r024Rig) !== expectedR024RigHash) {
  throw new Error("R024 FBX hash differs from the immutable R024 input.");
}
if (fs.existsSync(stagingRoot)) {
  const entries = fs.readdirSync(stagingRoot);
  if (entries.length !== 1 || entries[0] !== path.basename(import.meta.filename)) {
    throw new Error(`Refusing to overwrite R025 staging: ${stagingRoot}`);
  }
} else {
  fs.mkdirSync(stagingRoot, { recursive: false });
}

fs.mkdirSync(path.dirname(targetTemplate), { recursive: true });
fs.cpSync(sourceTemplate, targetTemplate, {
  recursive: true,
  errorOnExist: true
});
renameR024Paths(targetTemplate);
transformPackageSource(targetTemplate);

const inputs = {
  schema: "premium-display-case-gate04-r025-portrait-projection-inputs.v1",
  candidateScope:
    "R025 isolated portrait projection and diagnostic repair; no physical asset change",
  r024Fbx: {
    path: path.relative(repoRoot, r024Rig),
    sha256: expectedR024RigHash,
    unchangedRequired: true
  },
  preservedRejectionRecords: [
    rejectionRecord("rev-015", "self-rejection.json"),
    rejectionRecord("rev-016", "self-rejection.json"),
    rejectionRecord("rev-017", "r017-scrub-visual-self-rejection.json"),
    rejectionRecord("rev-018", "r018-preflight-self-rejection.json"),
    rejectionRecord("rev-019", "r019-preflight-self-rejection.json"),
    rejectionRecord("rev-021", "r021-preflight-self-rejection.json"),
    rejectionRecord("rev-022", "r022-preflight-self-rejection.json"),
    rejectionRecord("rev-023", "r023-static-preflight-self-rejection.json"),
    rejectionRecord("rev-024", "r024-static-preflight-self-rejection.json")
  ],
  preservedRevisionDirectories: fs.readdirSync(
    path.dirname(r024Evidence),
    { withFileTypes: true }
  ).filter((entry) =>
    entry.isDirectory() && /^rev-0(?:1[5-9]|2[0-4])$/u.test(entry.name)
  ).map((entry) => entry.name).sort(),
  sourceBoundary: {
    blenderRigChanged: false,
    fbxChanged: false,
    packGeometryChanged: false,
    uvChanged: false,
    segmentTopologyChanged: false,
    sourceCc0MappingChanged: false,
    packArtworkChanged: false,
    casePrefabChanged: false,
    contentSlotChanged: false,
    toyChanged: false,
    timingChanged: false,
    effectsChanged: false,
    canonicalProjectChanged: false,
    fanCardChanged: false,
    packagesChanged: false,
    userAssetsChanged: false
  }
};
fs.writeFileSync(
  path.join(stagingRoot, "r025-inputs.json"),
  `${JSON.stringify(inputs, null, 2)}\n`,
  { flag: "wx" }
);

console.log(JSON.stringify({
  stagingRoot,
  targetTemplate,
  r024RigSha256: expectedR024RigHash,
  preservedRejectionRecords: inputs.preservedRejectionRecords.length
}, null, 2));
