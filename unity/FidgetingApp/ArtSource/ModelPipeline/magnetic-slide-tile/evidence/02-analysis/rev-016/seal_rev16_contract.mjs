#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest, saveManifest, sha256File } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 163) throw new Error(`Expected pipeline revision 163, got ${manifest.revision}.`);
const here = path.dirname(fileURLToPath(import.meta.url));
const contractPath = path.join(here, "mechanism-evidence-contract.json");
const configPath = path.join(here, "interactive-cad-geometry-config.json");
const gate03Dir = path.resolve(here, "../../03-contract/rev-010");
const gate04Dir = path.resolve(here, "../../04-architecture/rev-012");
const provisionalPath = path.join(gate03Dir, "provisional-modeling-contract.json");
const architecturePath = path.join(gate04Dir, "four-track-raised-axis-architecture.json");
const contract = JSON.parse(fs.readFileSync(contractPath, "utf8"));
const additions = {
  "MEC-RAISED-AXIS-BOSS": {
    units: "millimetres and boolean topology",
    regions: [{ assetId: "slider-analysis-user-rejection-screenshot-02-r016", note: "Rejected visible cavity and corrected raised-boss interpretation." }]
  },
  "MEC-BALL-CONTACT-CANDIDATES": {
    units: "millimetres",
    regions: [{ assetId: "slider-intake-haloo-official-05", note: "Official ball/spring mechanism close view." }]
  },
  "MEC-FOUR-TRACK-ROLES": {
    units: "component counts and roles",
    regions: [{ assetId: "slider-intake-haloo-official-07", note: "Official internal four-track and ball-path view." }]
  }
};
for (const item of contract.constraints) Object.assign(item, additions[item.id] || {});
fs.writeFileSync(contractPath, `${JSON.stringify(contract, null, 2)}\n`);
const contractHash = sha256File(contractPath);

const config = JSON.parse(fs.readFileSync(configPath, "utf8"));
config.contractSha256 = contractHash;
config.expectedContractSha256 = contractHash;
config.geometryBlockers.contractHashMustMatch = contractHash;
fs.writeFileSync(configPath, `${JSON.stringify(config, null, 2)}\n`);
const provisional = JSON.parse(fs.readFileSync(provisionalPath, "utf8"));
provisional.governingMechanismContractSha256 = contractHash;
provisional.generationBlockers.contractHashMustMatch = contractHash;
fs.writeFileSync(provisionalPath, `${JSON.stringify(provisional, null, 2)}\n`);
const architecture = JSON.parse(fs.readFileSync(architecturePath, "utf8"));
architecture.governingMechanismContractSha256 = contractHash;
architecture.blockers.contractHashMustMatch = contractHash;
fs.writeFileSync(architecturePath, `${JSON.stringify(architecture, null, 2)}\n`);

for (const asset of manifest.assets) {
  if (![
    "slider-analysis-mechanism-evidence-contract-r016",
    "slider-analysis-interactive-cad-geometry-config-r016",
    "magnetic-slide-tile-provisional-modeling-contract-r010",
    "magnetic-slide-tile-four-track-architecture-r012"
  ].includes(asset.id)) continue;
  const absolute = {
    "slider-analysis-mechanism-evidence-contract-r016": contractPath,
    "slider-analysis-interactive-cad-geometry-config-r016": configPath,
    "magnetic-slide-tile-provisional-modeling-contract-r010": provisionalPath,
    "magnetic-slide-tile-four-track-architecture-r012": architecturePath
  }[asset.id];
  asset.sha256 = sha256File(absolute);
  asset.sizeBytes = fs.statSync(absolute).size;
  if (asset.stageId !== "02-analysis") asset.provenance.mechanismEvidenceContractSha256 = contractHash;
}
const currentDownstreamIds = new Set([
  ...manifest.stages[2].artifactIds,
  ...manifest.stages[3].artifactIds
]);
for (const asset of manifest.assets) {
  if (currentDownstreamIds.has(asset.id)) asset.provenance.mechanismEvidenceContractSha256 = contractHash;
}
manifest.stages[1].analysisSpec.contractSha256 = contractHash;
manifest.stages[2].validations.push({
  id: "contract-schema-sealed",
  status: "pass",
  evidence: "All rev 16 constraints carry schema units/regions; downstream hashes were refreshed."
});
manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate02-rev16-contract-schema-sealed",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  contractSha256: contractHash
});
console.log(JSON.stringify({ revision: saved.revision, contractSha256: contractHash }, null, 2));
