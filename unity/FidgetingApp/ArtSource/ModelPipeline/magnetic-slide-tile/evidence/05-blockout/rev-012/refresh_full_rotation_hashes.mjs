#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const stage = manifest.stages[4];
if (manifest.revision !== 216 || stage.status !== "ready_for_review")
  throw new Error(`Expected pipeline 216 ready_for_review; got ${manifest.revision}/${stage.status}.`);
const changedPaths = [
  "tools/model-provenance-explorer/app.js",
  "tools/model-provenance-explorer/tests/browser-persistent-workspace-gate05-r012.mjs",
  "tools/model-provenance-explorer/tests/magnetic-slide-gate05-rebuild.test.mjs",
  "tools/model-provenance-explorer/tests/magnetic-slide-gate05-rev6.test.mjs",
  "tools/model-provenance-explorer/tests/magnetic-slide-gate05-rev12.test.mjs",
  "tools/model-provenance-explorer/tests/magnetic-slide-gate06-rev4.test.mjs",
  "tools/model-provenance-explorer/tests/magnetic-slide-gate08-rev3-portability.test.mjs",
  "tools/model-provenance-explorer/tests/magnetic-slide-gate10-rev9.test.mjs",
  "tools/model-provenance-explorer/tests/magnetic-slide-gate11-rev9.test.mjs",
  "tools/model-provenance-explorer/tests/pipeline-core.test.mjs",
  "tools/model-provenance-explorer/tests/workflow-three-phase.test.mjs",
  "unity/FidgetingApp/Docs/FidgetingAppProductDesignBible.md",
  "unity/FidgetingApp/Docs/IMPLEMENTATION_STATUS.md",
  "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-012/browser-workspace-validation.json",
  "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev12-persistent-workbench.png",
  "Artifacts/ModelProvenanceExplorer/magnetic-slide-gate05-rev12-workbench-focused.png",
];
let updatedAssets = 0;
for (const relative of changedPaths) {
  const absolute = path.join(repoRoot, relative);
  if (!fs.existsSync(absolute)) throw new Error(`Missing ${relative}`);
  for (const asset of manifest.assets.filter((item) => item.path === relative)) {
    asset.sha256 = sha256File(absolute);
    asset.sizeBytes = fs.statSync(absolute).size;
    updatedAssets += 1;
  }
}
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-full-rotation-test-evidence-refreshed",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  updatedAssets,
  visualApprovalPending: true,
  buildInstallPhone: false,
});
console.log(JSON.stringify({ revision: saved.revision, updatedAssets }, null, 2));
