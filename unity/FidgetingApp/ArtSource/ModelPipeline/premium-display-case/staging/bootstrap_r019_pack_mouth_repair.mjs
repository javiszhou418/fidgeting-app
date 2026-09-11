#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const repoRoot = "/Users/jiawei.zhou/Documents/Fidgeting app";
const r018Root = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r018-coordinate-orientation"
);
const r019Root = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r019-pack-mouth-repair"
);
const sourceTemplate = path.join(r018Root, "isolated-template");
const targetTemplate = path.join(r019Root, "isolated-template");

function requireDirectory(directory) {
  if (!fs.existsSync(directory) || !fs.statSync(directory).isDirectory()) {
    throw new Error(`Missing source directory: ${directory}`);
  }
}

function requireFile(file) {
  if (!fs.existsSync(file) || !fs.statSync(file).isFile()) {
    throw new Error(`Missing source file: ${file}`);
  }
}

function walk(directory) {
  return fs.readdirSync(directory, { withFileTypes: true }).flatMap((entry) => {
    const file = path.join(directory, entry.name);
    return entry.isDirectory() ? walk(file) : [file];
  });
}

function renameR018Files() {
  const files = walk(r019Root)
    .filter((file) => path.basename(file).includes("R018"))
    .sort((left, right) => right.length - left.length);
  for (const file of files) {
    fs.renameSync(file, file.replaceAll("R018", "R019"));
  }
  return files.length;
}

requireDirectory(r018Root);
requireDirectory(sourceTemplate);
for (const file of [
  "build_pack_only_rig.py",
  "probe_r018_blender_geometry.py",
  "prepare_r018_isolated.mjs"
]) {
  requireFile(path.join(r018Root, file));
}
if (fs.existsSync(r019Root)) {
  throw new Error(`R019 staging already exists: ${r019Root}`);
}

fs.mkdirSync(r019Root, { recursive: false });
fs.copyFileSync(
  path.join(r018Root, "build_pack_only_rig.py"),
  path.join(r019Root, "build_pack_only_rig.py"),
  fs.constants.COPYFILE_EXCL
);
fs.copyFileSync(
  path.join(r018Root, "probe_r018_blender_geometry.py"),
  path.join(r019Root, "probe_r019_blender_geometry.py"),
  fs.constants.COPYFILE_EXCL
);
fs.copyFileSync(
  path.join(r018Root, "prepare_r018_isolated.mjs"),
  path.join(r019Root, "prepare_r019_isolated.mjs"),
  fs.constants.COPYFILE_EXCL
);
fs.cpSync(sourceTemplate, targetTemplate, {
  recursive: true,
  errorOnExist: true
});

const oldPackage = path.join(targetTemplate, "Assets/IsolatedProofR018");
const newPackage = path.join(targetTemplate, "Assets/IsolatedProofR019");
fs.renameSync(oldPackage, newPackage);
for (const file of walk(r019Root)) {
  if (!/\.(cs|shader|meta|py|mjs)$/u.test(file)) {
    continue;
  }
  fs.writeFileSync(
    file,
    fs.readFileSync(file, "utf8")
      .replaceAll("R018", "R019")
      .replaceAll("r018", "r019"),
    "utf8"
  );
}
const renamedFiles = renameR018Files();

console.log(JSON.stringify({
  stagingRoot: path.relative(repoRoot, r019Root),
  package: path.relative(repoRoot, newPackage),
  sourceRevision: "R018",
  mutation: "copy-only-before-bounded-pack-mouth-repair",
  renamedFiles
}, null, 2));
