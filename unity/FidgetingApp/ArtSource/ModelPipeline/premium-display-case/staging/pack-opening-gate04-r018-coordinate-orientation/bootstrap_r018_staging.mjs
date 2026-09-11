#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";

const repoRoot = "/Users/jiawei.zhou/Documents/Fidgeting app";
const r016Root = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r016-repair"
);
const r018Root = path.join(
  repoRoot,
  "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/staging/pack-opening-gate04-r018-coordinate-orientation"
);
const sourceTemplate = path.join(r016Root, "isolated-template");
const targetTemplate = path.join(r018Root, "isolated-template");

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

function renameR016Files() {
  const renames = walk(targetTemplate)
    .filter((file) => path.basename(file).includes("R016"))
    .sort((left, right) => right.length - left.length);
  for (const file of renames) {
    fs.renameSync(file, file.replaceAll("R016", "R018"));
  }
  return renames.length;
}

requireDirectory(r016Root);
requireDirectory(sourceTemplate);
requireFile(path.join(r016Root, "build_pack_only_rig.py"));
if (fs.existsSync(targetTemplate)) {
  if (process.argv.includes("--repair-filenames")) {
    console.log(JSON.stringify({
      repairedFiles: renameR016Files()
    }, null, 2));
    process.exit(0);
  }
  throw new Error(`R018 template already exists: ${targetTemplate}`);
}

fs.copyFileSync(
  path.join(r016Root, "build_pack_only_rig.py"),
  path.join(r018Root, "build_pack_only_rig.py"),
  fs.constants.COPYFILE_EXCL
);
fs.cpSync(sourceTemplate, targetTemplate, {
  recursive: true,
  errorOnExist: true
});

const oldPackage = path.join(targetTemplate, "Assets/IsolatedProofR016");
const newPackage = path.join(targetTemplate, "Assets/IsolatedProofR018");
fs.renameSync(oldPackage, newPackage);
for (const file of walk(targetTemplate)) {
  if (!/\.(cs|shader|meta)$/u.test(file)) {
    continue;
  }
  fs.writeFileSync(
    file,
    fs.readFileSync(file, "utf8")
      .replaceAll("R016", "R018")
      .replaceAll("r016", "r018"),
    "utf8"
  );
}
renameR016Files();

console.log(JSON.stringify({
  stagingRoot: path.relative(repoRoot, r018Root),
  package: path.relative(repoRoot, newPackage),
  sourceRevision: "R016",
  mutation: "copy-only-before-coordinate-and-orientation-repair"
}, null, 2));
