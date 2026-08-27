#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  repoRoot,
  saveManifest,
  sha256File
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const manifest = loadManifest(modelId);
if (manifest.revision !== 165) throw new Error(`Expected pipeline revision 165, got ${manifest.revision}.`);

const now = new Date().toISOString();
const exactUserWording = "Treat the user’s latest four-track/raised-axis feedback as white-model feedback and rebuild Gate 05 now, rather than sending them back to CAD/measurement approval.";
const here = path.dirname(fileURLToPath(import.meta.url));
const priorContractPath = path.resolve(here, "../rev-010/provisional-modeling-contract.json");
const priorReusePath = path.resolve(here, "../rev-009/reuse-plan.json");
const architectureDir = path.resolve(here, "../../04-architecture/rev-013");
const priorArchitecturePath = path.resolve(here, "../../04-architecture/rev-012/four-track-raised-axis-architecture.json");
const mechanismAsset = manifest.assets.find((asset) => asset.id === "slider-analysis-mechanism-evidence-contract-r016");
if (!mechanismAsset) throw new Error("Missing Gate 02 rev 16 mechanism contract.");
const mechanismPath = path.join(repoRoot, mechanismAsset.path);
const mechanismHash = sha256File(mechanismPath);
if (mechanismHash !== manifest.stages[1].analysisSpec.contractSha256) {
  throw new Error("Gate 02 mechanism contract hash drift.");
}

const contract = JSON.parse(fs.readFileSync(priorContractPath, "utf8"));
contract.revision = 11;
contract.createdAt = now;
contract.authorization = {
  authority: "latest-explicit-chat-instruction",
  exactUserWording,
  scope: "Gate 03 and Gate 04 consumed; Gate 05 deterministic white-model rebuild authorized"
};
contract.governingMechanismContractSha256 = mechanismHash;
contract.decisionState = "approved-for-provisional-white-model-only";
contract.deliveryState = "contract-only";
for (const dimension of Object.values(contract.dimensionsMm)) {
  dimension.state = dimension.state || "user-authorized-provisional";
  if (dimension.provisional != null && dimension.state !== "user-authoritative-estimate") {
    dimension.state = "user-authorized-provisional";
  }
}
contract.generationBlockers.contractHashMustMatch = mechanismHash;
const contractPath = path.join(here, "authorized-provisional-modeling-contract.json");
fs.writeFileSync(contractPath, `${JSON.stringify(contract, null, 2)}\n`);

const architecture = JSON.parse(fs.readFileSync(priorArchitecturePath, "utf8"));
architecture.revision = 13;
architecture.createdAt = now;
architecture.governingMechanismContractSha256 = mechanismHash;
architecture.decision = {
  state: "approved-consumed",
  authority: "latest-explicit-chat-instruction",
  exactUserWording,
  note: "No new architecture was invented; Gate 04 consumes the corrected four-track/raised-axis contract."
};
architecture.blockers.contractHashMustMatch = mechanismHash;
const architecturePath = path.join(architectureDir, "approved-four-track-raised-axis-architecture.json");
fs.writeFileSync(architecturePath, `${JSON.stringify(architecture, null, 2)}\n`);

const priorReuse = JSON.parse(fs.readFileSync(priorReusePath, "utf8"));
const reusePlan = {
  ...priorReuse,
  schemaVersion: 2,
  gate: "05-blockout",
  revision: 5,
  createdAt: now,
  contractSha256: mechanismHash,
  authorization: { exactUserWording, productionMeasured: false },
  reusedAssets: priorReuse.reusedAssets
    .filter((asset) => !asset.id.endsWith("-r015"))
    .concat([
      {
        id: "slider-analysis-mechanism-evidence-contract-r016",
        path: mechanismAsset.path,
        sha256: mechanismHash,
        reuse: "current four-track, raised-axis, ball-range and track-width authority"
      },
      {
        id: "slider-analysis-interactive-cad-geometry-config-r016",
        path: manifest.assets.find((asset) => asset.id === "slider-analysis-interactive-cad-geometry-config-r016").path,
        sha256: manifest.assets.find((asset) => asset.id === "slider-analysis-interactive-cad-geometry-config-r016").sha256,
        reuse: "current finite endpoints, overlap limit and component-role configuration"
      }
    ]),
  staleNotReused: [
    ...priorReuse.staleNotReused,
    {
      gate: "05-blockout",
      revision: 4,
      reason: "rejected recessed circular cavity and obsolete twin-groove hierarchy"
    }
  ],
  gate05Policy: "reuse capsule/smooth-normal techniques and approved later-stage look inputs; rebuild all visible geometry from rev 16"
};
const reusePath = path.join(here, "reuse-plan.json");
fs.writeFileSync(reusePath, `${JSON.stringify(reusePlan, null, 2)}\n`);

const sourceClaimIds = manifest.claims
  .filter((claim) => claim.stageId === "02-analysis" && !["superseded", "stale"].includes(claim.state))
  .map((claim) => claim.id);
const definitions = [
  ["magnetic-slide-tile-authorized-provisional-contract-r011", "03-contract", "modeling-contract", contractPath, "contract"],
  ["magnetic-slide-tile-reuse-plan-r011", "03-contract", "reuse-plan", reusePath, "contract"],
  ["magnetic-slide-tile-approved-four-track-architecture-r013", "04-architecture", "part-tree", architecturePath, "contract"]
];
for (const [id, stageId, slot, absolute, role] of definitions) {
  manifest.assets.push({
    id,
    stageId,
    slot,
    path: path.relative(repoRoot, absolute).split(path.sep).join("/"),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: "fidgeting-model-pipeline",
      version: "5",
      recipe: "consume chat-authorized four-track raised-axis contract for Gate 05"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: slot,
      assertedBy: "assistant",
      exactUserWording,
      mechanismEvidenceContractSha256: mechanismHash,
      dimensionsState: "user-authorized-provisional-not-production-measured"
    },
    sourceAssetIds: stageId === "03-contract"
      ? ["slider-analysis-mechanism-evidence-contract-r016", "slider-measurement-anthropometric-video-report-r010"]
      : ["magnetic-slide-tile-authorized-provisional-contract-r011"],
    sourceClaimIds
  });
}

const gate03 = manifest.stages[2];
gate03.revision += 1;
gate03.status = "approved";
gate03.artifactIds.push(
  "magnetic-slide-tile-authorized-provisional-contract-r011",
  "magnetic-slide-tile-reuse-plan-r011"
);
gate03.reviewArtifactIds = ["magnetic-slide-tile-authorized-provisional-contract-r011"];
gate03.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "latest-explicit-chat-instruction",
  decidedAt: now,
  mechanismEvidenceContractSha256: mechanismHash,
  scope: "provisional Gate 05 white model only"
};
gate03.validations.push({
  id: "chat-authorized-white-model-progression",
  status: "pass",
  evidence: "The user classified the rev 16 correction as white-model feedback and authorized immediate Gate 05 rebuilding."
});

const gate04 = manifest.stages[3];
gate04.revision += 1;
gate04.status = "approved";
gate04.artifactIds.push("magnetic-slide-tile-approved-four-track-architecture-r013");
gate04.reviewArtifactIds = ["magnetic-slide-tile-approved-four-track-architecture-r013"];
gate04.decision = {
  action: "approve",
  notes: exactUserWording,
  decidedBy: "latest-explicit-chat-instruction",
  decidedAt: now,
  mechanismEvidenceContractSha256: mechanismHash,
  scope: "consume corrected architecture without another blocker page"
};
delete gate04.staleReason;
gate04.validations = [
  { id: "contract-consumption", status: "pass", evidence: `Architecture consumes ${mechanismHash}.` },
  { id: "no-new-assumption", status: "pass", evidence: "Part ownership and transforms match the corrected CAD contract." }
];

manifest.currentStageId = "05-blockout";
manifest.currentState.visualApproval = "gate05-rev5-building";
manifest.currentState.blenderModelingStatus = "gate05-four-track-raised-axis-white-model-building";
manifest.currentState.diagnosis = "Gate 03–04 are consumed from the user-authorized provisional boundary. Gate 05 rev 5 rebuilds the four-track raised-axis white model; rev 4 remains rejected.";
manifest.revision += 1;
manifest.updatedAt = now;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate03-gate04-consumed-for-gate05-rebuild",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: now,
  exactUserWording,
  mechanismEvidenceContractSha256: mechanismHash,
  gate03Status: "approved",
  gate04Status: "approved",
  gate05RevisionTarget: 5,
  productionMeasured: false,
  simulatorUsed: false,
  unityChanged: false,
  deviceWork: false
});
console.log(JSON.stringify({
  revision: saved.revision,
  approved: saved.stages.filter((stage) => stage.status === "approved").length,
  currentStageId: saved.currentStageId,
  mechanismHash
}, null, 2));

