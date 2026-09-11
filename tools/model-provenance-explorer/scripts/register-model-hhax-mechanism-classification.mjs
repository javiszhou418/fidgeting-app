import { loadManifest, saveExternalReferencePack } from "../pipeline-core.mjs";
const modelId = "model-hhax";
const manifest = loadManifest(modelId);
const next = saveExternalReferencePack(modelId, {
  expectedRevision: manifest.revision,
  sourceName: "NXEDC / same-product public archive",
  sourceVersion: "2026-09-11",
  assets: [{
    id: "hhax-intake-mechanical-drive-classification-r002",
    path: "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/01-intake/rev-002/mechanism-classification.json",
    sourceUrl: "https://nxedc.com/products/groove-ultra",
    contentClass: "same-model-internal-mechanism",
    description: "Exact-product internal mechanism classification: mechanical straight push, rotation linkage, spring and bead modules; magnetic retention is limited to replaceable patches."
  }]
});
console.log(JSON.stringify({ revision: next.revision, validations: next.stages[0].validations }, null, 2));
