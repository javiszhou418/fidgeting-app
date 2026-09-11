#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
const gate06 = manifest.stages[5];
if (manifest.revision !== 225 || gate06.status !== "ready_for_review" || gate06.revision !== 5) {
  throw new Error(`Unexpected refresh state ${manifest.revision}/${gate06.status}/${gate06.revision}.`);
}
const auditDirectory = path.join(path.dirname(fileURLToPath(import.meta.url)), "fixed-views-audit");
const auditDefinitions = [
  ["magnetic-slide-tile-geometry-standard-capture-report-r005", "standard-capture-report", path.join(auditDirectory, "capture-report.json"), "validation"],
  ["magnetic-slide-tile-geometry-standard-wrapper-report-r005", "standard-wrapper-report", path.join(auditDirectory, "capture-wrapper-report.json"), "validation"],
  ...["front", "back", "top", "bottom", "left", "right", "hero", "left-oblique", "right-oblique", "low"].map((view) => [
    `magnetic-slide-tile-geometry-standard-${view}-r005`,
    `standard-${view}`,
    path.join(auditDirectory, `${view}.png`),
    "blender-render",
  ]),
];
const auditIds = new Set(auditDefinitions.map(([id]) => id));
manifest.assets = manifest.assets.filter((asset) => !auditIds.has(asset.id));
for (const [id, slot, absolute, role] of auditDefinitions) {
  if (!fs.existsSync(absolute)) throw new Error(`Missing standard capture artifact ${absolute}.`);
  manifest.assets.push({
    id,
    stageId: "06-geometry",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "fidgeting-model-pipeline standard capture",
      version: "Blender 5.2.0 LTS",
      recipe: "capture_standard_views.py verified Blender bpy fallback",
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: gate06.geometrySpec.governingContractSha256,
      gate05SourceSha256: gate06.geometrySpec.gate05SourceSha256,
      geometryDigest: gate06.geometrySpec.canonicalGeometryDigest,
      geometryChanged: false,
      productRendererWhitelist: ["BottomExterior", "MovingTopBody"],
    },
    sourceAssetIds: ["magnetic-slide-tile-geometry-blend-r005"],
    sourceClaimIds: [],
  });
}
for (const id of auditDefinitions.map(([id]) => id)) {
  if (!gate06.artifactIds.includes(id)) gate06.artifactIds.push(id);
}
const finalValidationId = "magnetic-slide-tile-gate06-final-validation-r005";
const finalValidationAbsolute = path.join(path.dirname(fileURLToPath(import.meta.url)), "final-validation.json");
manifest.assets = manifest.assets.filter((asset) => asset.id !== finalValidationId);
manifest.assets.push({
  id: finalValidationId,
  stageId: "06-geometry",
  slot: "final-validation",
  path: path.relative(repoRoot, finalValidationAbsolute).split(path.sep).join("/"),
  sha256: sha256File(finalValidationAbsolute),
  exists: true,
  sizeBytes: fs.statSync(finalValidationAbsolute).size,
  role: "validation",
  producer: {
    name: "gate06 endpoint geometry finalizer",
    version: "rev-005",
    recipe: "Aggregate Blender, Node, pipeline, browser, GLB, mobile, modal and video validation.",
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "final-validation",
    assertedBy: "assistant",
    mechanismEvidenceContractSha256: gate06.geometrySpec.governingContractSha256,
    gate05SourceSha256: gate06.geometrySpec.gate05SourceSha256,
    geometryDigest: gate06.geometrySpec.canonicalGeometryDigest,
    geometryChanged: false,
  },
  sourceAssetIds: [
    "magnetic-slide-tile-geometry-validation-r005",
    "magnetic-slide-tile-geometry-audit-r005",
    "magnetic-slide-tile-workspace-browser-report-r005",
    "magnetic-slide-tile-geometry-standard-capture-report-r005",
  ],
  sourceClaimIds: [],
});
if (!gate06.artifactIds.includes(finalValidationId)) gate06.artifactIds.push(finalValidationId);
for (const id of [
  "magnetic-slide-tile-gate06-design-bible-r005",
  "magnetic-slide-tile-gate06-implementation-status-r005",
]) {
  const asset = manifest.assets.find((candidate) => candidate.id === id);
  const absolute = path.join(repoRoot, asset.path);
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
}
const scriptPath = fileURLToPath(import.meta.url);
const scriptId = "magnetic-slide-tile-geometry-final-hash-refresh-r005";
manifest.assets = manifest.assets.filter((asset) => asset.id !== scriptId);
manifest.assets.push({
  id: scriptId,
  stageId: "06-geometry",
  slot: "hash-refresh-script",
  path: path.relative(repoRoot, scriptPath).split(path.sep).join("/"),
  sha256: sha256File(scriptPath),
  exists: true,
  sizeBytes: fs.statSync(scriptPath).size,
  role: "process",
  producer: {
    name: "fidgeting-model-pipeline",
    version: "endpoint-interlock-2026-08-28",
    recipe: "Refresh shared canonical document hashes after concurrent edits",
  },
  provenance: {
    origin: "repository-generated",
    contentClass: "hash-refresh-script",
    assertedBy: "assistant",
    mechanismEvidenceContractSha256: gate06.geometrySpec.governingContractSha256,
    gate05SourceSha256: gate06.geometrySpec.gate05SourceSha256,
    geometryDigest: gate06.geometrySpec.canonicalGeometryDigest,
    geometryChanged: false,
  },
  sourceAssetIds: ["magnetic-slide-tile-geometry-validation-r005"],
  sourceClaimIds: [],
});
if (!gate06.artifactIds.includes(scriptId)) gate06.artifactIds.push(scriptId);
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate06-rev5-final-hashes-refreshed",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  stageId: "06-geometry",
  status: "ready_for_review",
  standardCapture: {
    backend: "blender-bpy-fallback",
    verified: true,
    missingViews: [],
    productRendererWhitelist: ["BottomExterior", "MovingTopBody"],
  },
  visualApprovalPending: true,
});
console.log(JSON.stringify({ revision: saved.revision, gate06: saved.stages[5].status }, null, 2));
