#!/usr/bin/env node
import crypto from "node:crypto";
import {
  loadManifest,
  saveManifest,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const manifest = loadManifest(modelId);
if (manifest.revision !== 107) {
  throw new Error(`Expected manifest revision 107, got ${manifest.revision}.`);
}
const stage = manifest.stages[6];
if (stage.status !== "approved" || stage.materialRebuildSpec?.revision !== 9) {
  throw new Error("Gate 07 rev 9 is not the active review.");
}

const timestamp = new Date().toISOString();
const userQuote = "我暂时确认了 rev 9，但是我希望你下一次再找我确认的时候，能把轴心旋转的角度也带上.";
stage.revision += 1;
stage.status = "draft";
stage.priorMaterialReview = {
  revision: 9,
  result: "provisional-visual-acceptance-only-not-formal-gate-approval",
  userQuote,
  preservedArtifactIds: [...stage.artifactIds],
  preservedReviewArtifactIds: [...stage.reviewArtifactIds],
  correctedAt: timestamp,
  requiredCorrections: [
    "The lower piece incorrectly repeats the upper artwork mask.",
    "The blood-red crystal lacks the source's granular foil breakup, glitter points and layered depth.",
    "The next review must show point-axis rotation at detent-aligned angles.",
  ],
};
stage.artifactIds = [];
stage.reviewArtifactIds = [];
stage.validations = [];
stage.priorDecision = {
  ...stage.decision,
  correctedToProvisionalVisualAcceptance: true,
  correctedByUserQuote: userQuote,
};
stage.decision = null;
stage.materialRebuildSpec.reviewState = "provisionally-visually-accepted-not-formally-approved";
stage.materialRebuildSpec.supersededByMaterialRevision = 10;
stage.materialRebuildSpec.nextReviewMotionEvidence = {
  axisPointWorldMm: [0, -9.5, 0],
  axisDirection: "+Z",
  spinAnglesDeg: [0, 12, 36],
  detentIndices: [0, 1, 3],
  detentEquation: "360° / 12° = 30",
  spinTranslationMm: [0, 0, 0],
  maximumPivotDriftMm: 0,
  slidePose: { translationMm: [0, 21, 0], rotationDeg: 0 },
  primaryPoseMustBeDetentAligned: true,
  forbiddenPrimaryAngleDeg: 45,
};
manifest.revision += 1;
manifest.updatedAt = timestamp;
manifest.currentState.visualApproval = "gate07-rev10-material-and-axis-evidence-in-progress";
manifest.currentState.diagnosis =
  "The user provisionally accepted Gate 07 rev 9 appearance but explicitly did not grant formal Gate approval. Gate 07 rev 10 is rebuilding distinct lower artwork and granular blood-red crystal, and its next review must include [0,-9.5,0] +Z point-axis evidence at 0°, 12° and 36° plus a separate +21 mm / 0° slide pose. Gates 08–11 remain stale; Gate 12 remains blocked/rejected; the old shipping model remains default; no Unity, build, install or phone work is authorized.";

const event = {
  id: crypto.randomUUID(),
  type: "stage-provisional-visual-acceptance-correction-started",
  modelId,
  manifestRevision: manifest.revision,
  timestamp,
  stageId: "07-material",
  provisionalMaterialRevision: 9,
  nextMaterialRevision: 10,
  userQuote,
  formalGateApproval: false,
  workbenchApprovalEventSuperseded: 107,
  requiredCorrections: stage.priorMaterialReview.requiredCorrections,
  nextReviewMotionEvidence: stage.materialRebuildSpec.nextReviewMotionEvidence,
  staleStageIds: ["08-lighting", "09-environment", "10-export", "11-unity-parity"],
  gate12Status: "blocked",
  oldShippingModelDefault: true,
  unityBuildInstallPhone: "not-started",
};
saveManifest(manifest, event);
console.log(JSON.stringify(event, null, 2));
