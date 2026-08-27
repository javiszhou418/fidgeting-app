import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { pipelineConfig, stageMeta } from "./pipeline-config.mjs";

const toolDir = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(toolDir, "../..");
const outputFile = path.join(toolDir, "inventory.generated.js");

const extensions = {
  image: new Set([".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp", ".tif", ".tiff", ".heic"]),
  model: new Set([".blend", ".fbx", ".obj", ".glb", ".gltf", ".stl"]),
  document: new Set([".md", ".json", ".html", ".js", ".cjs", ".py", ".xml", ".log", ".csv"])
};

function normalize(value) {
  return value.split(path.sep).join("/");
}

function classify(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  for (const [kind, values] of Object.entries(extensions)) {
    if (values.has(ext)) return kind;
  }
  return "other";
}

function walk(directory, recursive = true) {
  if (!fs.existsSync(directory)) return [];
  const entries = fs.readdirSync(directory, { withFileTypes: true });
  const files = [];
  for (const entry of entries) {
    if (entry.name === ".DS_Store" || entry.name.endsWith(".meta")) continue;
    const absolute = path.join(directory, entry.name);
    if (entry.isDirectory()) {
      if (recursive) files.push(...walk(absolute, true));
      continue;
    }
    files.push(absolute);
  }
  return files;
}

function compileMatcher(pattern) {
  if (!pattern) return null;
  return new RegExp(pattern, "i");
}

function collectGroup(group) {
  const requestedKinds = new Set(group.kinds || ["image"]);
  const candidates = [];
  for (const file of group.files || []) candidates.push(path.resolve(repoRoot, file));
  const folders = group.folders || (group.folder ? [group.folder] : []);
  for (const folder of folders) {
    candidates.push(...walk(path.resolve(repoRoot, folder), group.recursive !== false));
  }

  const nameMatcher = compileMatcher(group.match);
  const pathMatcher = compileMatcher(group.matchPath);
  const seen = new Set();
  const files = [];

  for (const absolute of candidates) {
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) continue;
    const kind = classify(absolute);
    if (!requestedKinds.has(kind)) continue;
    const relativeRepoPath = normalize(path.relative(repoRoot, absolute));
    const basename = path.basename(absolute);
    if (nameMatcher && !nameMatcher.test(basename)) continue;
    if (pathMatcher && !pathMatcher.test(relativeRepoPath)) continue;
    if (seen.has(relativeRepoPath)) continue;
    seen.add(relativeRepoPath);
    const stat = fs.statSync(absolute);
    files.push({
      name: basename,
      path: relativeRepoPath,
      absolutePath: normalize(absolute),
      url: normalize(path.relative(toolDir, absolute)),
      kind,
      extension: path.extname(absolute).slice(1).toUpperCase(),
      sizeBytes: stat.size
    });
  }

  files.sort((a, b) => a.path.localeCompare(b.path, "zh-CN", { numeric: true }));
  const displayFolders = group.folders || (group.folder ? [group.folder] : []);
  return {
    label: group.label,
    folders: displayFolders,
    explicitFiles: group.files || [],
    note: group.note || "",
    state: group.state || "working",
    files
  };
}

const pipelines = pipelineConfig.map((pipeline) => {
  const stages = {};
  for (const stageId of Object.keys(stageMeta)) {
    stages[stageId] = (pipeline.stages[stageId] || []).map(collectGroup);
  }
  return { ...pipeline, stages };
});

const allFiles = pipelines.flatMap((pipeline) => Object.values(pipeline.stages).flatMap((groups) => groups.flatMap((group) => group.files)));
const uniqueFiles = new Map(allFiles.map((file) => [file.path, file]));
const totals = { image: 0, model: 0, document: 0, other: 0 };
for (const file of uniqueFiles.values()) totals[file.kind] += 1;

const payload = {
  generatedAt: new Date().toISOString(),
  repoRoot: normalize(repoRoot),
  stageMeta,
  totals: { ...totals, unique: uniqueFiles.size, references: pipelines.length },
  pipelines
};

fs.writeFileSync(outputFile, `window.MODEL_PROVENANCE = ${JSON.stringify(payload, null, 2)};\n`, "utf8");
console.log(`Generated ${normalize(path.relative(repoRoot, outputFile))} with ${uniqueFiles.size} unique assets across ${pipelines.length} pipelines.`);
