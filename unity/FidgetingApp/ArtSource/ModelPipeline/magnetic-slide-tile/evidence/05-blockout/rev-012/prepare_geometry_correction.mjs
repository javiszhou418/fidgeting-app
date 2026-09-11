#!/usr/bin/env node
import crypto from "node:crypto";
import { loadManifest, saveManifest } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const manifest = loadManifest("magnetic-slide-tile");
if (manifest.revision !== 211) throw new Error(`Expected revision 211, got ${manifest.revision}.`);
const gate05 = manifest.stages[4];
const rejection = {
  action: "reject",
  decidedBy: "user",
  decidedAt: new Date().toISOString(),
  sourceReview: "Gate 08 rev 4 Unity-only PlayMode preview",
  failures: ["axis drift/jump", "hidden mechanism penetration", "spurious magnet-like plate"],
  screenshots: [
    { id: "axis-intent", sha256: "d2222151656cc4bae03ec6cab7aa8dd90b104a40794acdabc342b7327012dfe3" },
    { id: "penetration-proxy", sha256: "57c1efc26474c56a196ad458208915b1ed9e7e27b9b5cdea9a276ac8840b14cd" },
  ],
};
gate05.revision = 12;
gate05.status = "draft";
gate05.artifactIds = [];
gate05.reviewArtifactIds = [];
gate05.validations = [];
gate05.decision = null;
gate05.blockoutSpec = {
  revision: 12,
  sourceGeometryRevision: 4,
  governingContractSha256: "5aee71817c2c033ed92b770126ba0ecb6d79c2f032d786743b214b79078a47ea",
  rejection,
  earliestAffectedGate: "05-blockout",
  rootCause: [
    "Gate 05 used FixedAxisBoss as a pivot parent while also retaining FixedAxis, creating ambiguous axis identity.",
    "Product previews rendered internal mechanism meshes instead of enforcing a two-surface exterior whitelist.",
    "Pose validation checked transforms and bounds but not M_top(s,theta)*q(s)=P or actual mesh-surface intersections.",
  ],
  correctedTransform: "M_top(s,theta)=T(P)*Rz(theta)*T(-q(s)); q(s)=(0,-9+s,0) mm in TopPlate local coordinates; P=(0,-9,5.875) mm.",
  exactlyOnePivotId: "FixedAxis",
  productRendererWhitelist: ["BottomExterior", "MovingTopBody"],
  internalTechnicalOnly: ["InternalAxisBoss", "RotatingCarrierBody", "CarrierFollowerLeft", "CarrierFollowerRight", "BallCandidateLeft", "BallCandidateRight"],
  minimumOverlapDisk: "non-rendering Empty/constraint metadata",
  finalMaterialsApplied: false,
  unityPreviewOnly: true,
  buildInstallPhone: false,
};
gate05.readiness = { ready: false, blockers: ["Corrected Gate 05 rev 12 geometry is being rebuilt."], note: "Review returns to White Model/Geometry. Unity progression is frozen." };
for (let index = 5; index < manifest.stages.length; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = "User-rejected axis identity, penetration and debug-geometry visibility propagated from Gate 05.";
}
manifest.currentStageId = "05-blockout";
manifest.currentState.visualApproval = "gate05-rev12-geometry-correction-building";
manifest.currentState.blenderModelingStatus = "gate05-rev12-fixed-axis-containment-rebuild";
manifest.currentState.unityStatus = "isolated-geometry-preview-only-old-shipping-model-default";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.workbench = "persistent-seven-tab-memory-route-enabled-current-white-model";
manifest.currentState.diagnosis = "Gate 05 is the earliest affected implementation gate. One fixed pivot, slot-point locking and strict product/technical render whitelists are required.";
manifest.revision += 1;
manifest.updatedAt = rejection.decidedAt;
const saved = saveManifest(manifest, {
  id: crypto.randomUUID(),
  type: "gate08-unity-preview-rejected-return-gate05",
  modelId: "magnetic-slide-tile",
  manifestRevision: manifest.revision,
  timestamp: rejection.decidedAt,
  decision: rejection,
  earliestAffectedGate: "05-blockout",
  correction: gate05.blockoutSpec.correctedTransform,
  noBuildInstallPhone: true,
});
console.log(JSON.stringify({ revision: saved.revision, current: saved.currentStageId, gate05: saved.stages[4].status }, null, 2));

