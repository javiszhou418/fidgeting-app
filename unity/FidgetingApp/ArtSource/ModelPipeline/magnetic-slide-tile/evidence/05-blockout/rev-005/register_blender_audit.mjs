#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, repoRoot, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 168) throw new Error(`Expected pipeline revision 168, got ${manifest.revision}.`);
const here = path.dirname(fileURLToPath(import.meta.url));
const reportPath = path.join(here, "blender-audit.json");
const report = JSON.parse(fs.readFileSync(reportPath, "utf8"));
if (!report.pass) throw new Error("Independent Blender audit failed.");
const contractHash = manifest.stages[1].analysisSpec.contractSha256;
const files = [
  ["magnetic-slide-tile-blockout-audit-script-r005", "blender-audit-process", path.join(here, "audit_gate05_blockout.py"), "process"],
  ["magnetic-slide-tile-blockout-audit-r005", "blender-audit", reportPath, "validation"]
];
const sourceClaimIds = manifest.claims
  .filter((claim) => claim.stageId === "02-analysis" && !["superseded", "stale"].includes(claim.state))
  .map((claim) => claim.id);
for (const [id, slot, absolute, role] of files) {
  manifest.assets.push({
    id,
    stageId: "05-blockout",
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: { name: "Blender", version: report.blenderVersion, recipe: "independent saved-blend hierarchy, manifold and motion audit" },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: contractHash,
      simulatorUsed: false,
      unityChanged: false
    },
    sourceAssetIds: ["magnetic-slide-tile-blockout-blend-r005"],
    sourceClaimIds
  });
}
manifest.stages[4].artifactIds.push(...files.map(([id]) => id));
manifest.stages[4].validations.push({
  id: "independent-blender-audit",
  status: "pass",
  evidence: "Blender 5.2 reopened the saved blend: 32 objects, exact hierarchy, four grooves, positive boss, no cavity, manifold key meshes and zero animation."
});
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate05-independent-blender-audit-passed",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  contractSha256: contractHash,
  blenderVersion: report.blenderVersion,
  objectCount: report.objectCount,
  validationPass: true,
  visualApprovalPending: true,
  unityChanged: false,
  deviceWork: false
});
console.log(JSON.stringify({ revision: saved.revision, gate05: saved.stages[4].status, auditPass: true }, null, 2));

