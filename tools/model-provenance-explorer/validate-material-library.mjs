#!/usr/bin/env node
// Validate unity/FidgetingApp/ArtSource/MaterialLibrary/materials.json.
//   --refresh   re-hash sphere thumbnails into the JSON
//   --write-md  regenerate materials.md from the JSON
import fs from "node:fs";
import path from "node:path";
import { repoRoot } from "./pipeline-core.mjs";
import {
  MATERIAL_LIBRARY_PATH,
  loadMaterialLibrary,
  markdownInSync,
  refreshThumbnailHashes,
  validateMaterialLibrary,
  writeMaterialsMarkdown
} from "./material-library-core.mjs";

const refresh = process.argv.includes("--refresh");
const writeMd = process.argv.includes("--write-md");
let library = loadMaterialLibrary();
if (refresh) {
  const result = refreshThumbnailHashes(library);
  library = result.library;
  fs.writeFileSync(path.join(repoRoot, MATERIAL_LIBRARY_PATH), `${JSON.stringify(library, null, 2)}\n`);
  for (const row of result.report) console.log(`${row.state.padEnd(7)} ${row.thumbnail}`);
}
if (writeMd) {
  const written = writeMaterialsMarkdown(library);
  console.log(`wrote ${written.path} (${written.bytes} bytes)`);
}
const errors = validateMaterialLibrary(library);
if (!markdownInSync(library)) errors.push(`${library.generatedMarkdown} is out of date; run with --write-md.`);
if (errors.length) {
  console.error(`material library: ${errors.length} problem(s)`);
  for (const error of errors) console.error(`- ${error}`);
  process.exit(1);
}
console.log(`material library ok: ${library.materials.length} materials, ${library.materials.filter((material) => material.thumbnail).length} thumbnails`);
