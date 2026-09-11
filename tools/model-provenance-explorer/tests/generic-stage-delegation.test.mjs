import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import {
  GENERIC_STAGE_REVIEW_RULES,
  addIntakeFile,
  approveStageFromDelegation,
  createModelPipeline,
  pipelineDirectory,
  readHistory,
  registerStageApprovalDelegation,
  resolveRepoPath,
  saveAnalysisResearchRevision,
  saveGenericStageEvidenceRevision,
  saveManifest,
  saveStageReviewEvidence,
  sha256File,
  stageReadiness
} from "../pipeline-core.mjs";

const exactUserWording = "无需人工 approve，自我逐关通过";
const suffix = process.pid.toString(36);

function repoPath(absolutePath) {
  return path.relative(resolveRepoPath("."), absolutePath).split(path.sep).join("/");
}

function writeEvidence(modelId, relativePath, bytes) {
  const absolutePath = path.join(pipelineDirectory(modelId), "evidence", relativePath);
  fs.mkdirSync(path.dirname(absolutePath), { recursive: true });
  fs.writeFileSync(absolutePath, bytes);
  return repoPath(absolutePath);
}

function approveFixtureStage(modelId, stageId) {
  const manifest = JSON.parse(fs.readFileSync(path.join(pipelineDirectory(modelId), "pipeline.json"), "utf8"));
  const stage = manifest.stages.find((candidate) => candidate.id === stageId);
  stage.status = "approved";
  stage.decision = { action: "approve", notes: "fixture", decidedBy: "test", decidedAt: new Date().toISOString() };
  saveManifest(manifest, null);
}

test("standing delegation can begin at Gate 01 but still requires a hash-bound source-inspector recording", (t) => {
  const modelId = `zz-test-delegated-intake-${suffix}`;
  const cleanup = () => fs.rmSync(pipelineDirectory(modelId), { recursive: true, force: true });
  t.after(cleanup);
  cleanup();
  createModelPipeline({ id: modelId, name: "委托审批来源测试", mechanism: "other" });
  const intake = addIntakeFile(modelId, { filename: "original-reference.png", bytes: Buffer.from("original-reference") });
  const delegated = registerStageApprovalDelegation(modelId, {
    expectedRevision: intake.manifest.revision,
    exactUserWording,
    fromStageId: "01-intake",
    toStageId: "12-shipping"
  });
  assert.equal(delegated.currentState.approvalDelegation.fromStageId, "01-intake");
  assert.equal(delegated.stages[0].readiness.ready, false);
  assert.throws(
    () => approveStageFromDelegation(modelId, "01-intake", { expectedRevision: delegated.revision }),
    /review evidence/
  );

  const recordingId = `${modelId}-source-inspector-r002`;
  const snapshotId = `${modelId}-source-snapshot-r002`;
  const recordingPath = writeEvidence(modelId, "01-intake/rev-002/source-inspector.mp4", Buffer.from("MP4"));
  const snapshotPath = writeEvidence(modelId, "01-intake/rev-002/source-snapshot.json", JSON.stringify({
    originalReferenceAssetIds: [intake.asset.id],
    externalSourceClassificationsReviewed: true,
    sourceLinksReviewed: true
  }));
  const reviewed = saveStageReviewEvidence(modelId, "01-intake", {
    expectedRevision: delegated.revision,
    assets: [
      { id: recordingId, slot: "source-inspector-recording", path: recordingPath, role: "validation", sourceAssetIds: [intake.asset.id] },
      { id: snapshotId, slot: "parameter-snapshot", path: snapshotPath, role: "validation", sourceAssetIds: [intake.asset.id] }
    ],
    reviewedArtifactId: recordingId,
    governingContractAssetId: intake.asset.id,
    parameterSnapshotAssetId: snapshotId,
    completedChecklist: [...GENERIC_STAGE_REVIEW_RULES["01-intake"].checklist],
    interactionMode: "complete-source-inspector-recording",
    browserTimestamp: new Date().toISOString(),
    reviewDevice: "headless Chromium desktop"
  });
  assert.equal(reviewed.stages[0].status, "ready_for_review");
  assert.equal(reviewed.stages[0].reviewEvidenceSpec.governingContractAssetId, intake.asset.id);
  assert.equal(reviewed.stages[0].reviewEvidenceSpec.governingContractSha256, intake.asset.sha256);
  assert.ok(reviewed.stages[0].reviewEvidenceSpec.coreArtifactDigest);

  const approved = approveStageFromDelegation(modelId, "01-intake", { expectedRevision: reviewed.revision });
  assert.equal(approved.stages[0].status, "approved");
  assert.equal(approved.stages[0].decision.humanReviewed, false);
  assert.equal(approved.stages[0].decision.individualUserApproval, false);
  assert.equal(approved.stages[0].decision.exactUserWording, exactUserWording);
  assert.equal(readHistory(modelId)[0].physicalPhoneInstallAuthorized, false);
});

test("standing chat wording is preserved but cannot approve Gate 02 before real review evidence", (t) => {
  const modelId = `zz-test-delegated-analysis-${suffix}`;
  const cleanup = () => fs.rmSync(pipelineDirectory(modelId), { recursive: true, force: true });
  t.after(cleanup);
  cleanup();
  createModelPipeline({ id: modelId, name: "委托审批分析测试", mechanism: "other" });
  const intake = addIntakeFile(modelId, { filename: "reference.png", bytes: Buffer.from("reference") });
  approveFixtureStage(modelId, "01-intake");
  const discoveryPath = writeEvidence(modelId, "02-analysis/rev-001/discovery-log.json", JSON.stringify({ mechanism: "linear magnetic slider", units: null }));
  const boardPath = writeEvidence(modelId, "02-analysis/rev-001/analysis-board.png", Buffer.from("analysis-board"));
  const discoveryId = `${modelId}-discovery-r001`;
  const boardId = `${modelId}-board-r001`;
  const analysis = saveAnalysisResearchRevision(modelId, {
    expectedRevision: intake.manifest.revision,
    assets: [
      { id: discoveryId, slot: "discovery-log", path: discoveryPath, sourceAssetIds: [intake.asset.id] },
      { id: boardId, slot: "analysis-board", path: boardPath, sourceAssetIds: [intake.asset.id] }
    ],
    claims: [{
      id: `${modelId}-mechanism-r001`,
      category: "mechanism",
      statement: "这是线性磁吸推牌；真实毫米尺寸未知。",
      confidence: "medium",
      sourceAssetIds: [intake.asset.id]
    }],
    validations: [{ id: "no-mm-inference", status: "pass", evidence: "No millimetres were inferred." }]
  });
  const delegated = registerStageApprovalDelegation(modelId, {
    expectedRevision: analysis.revision,
    exactUserWording,
    fromStageId: "02-analysis",
    toStageId: "12-shipping"
  });
  assert.equal(delegated.currentState.approvalDelegation.exactUserWording, exactUserWording);
  assert.equal(delegated.stages[1].readiness.ready, false);
  assert.match(delegated.stages[1].readiness.reasons.join(" "), /交互|录屏/);
  assert.throws(
    () => approveStageFromDelegation(modelId, "02-analysis", { expectedRevision: delegated.revision }),
    /review evidence/
  );

  const cadId = `${modelId}-interactive-cad-r002`;
  const snapshotId = `${modelId}-cad-parameters-r002`;
  const cadPath = writeEvidence(modelId, "02-analysis/rev-002/interactive-cad.glb", Buffer.from("glTF"));
  const snapshotPath = writeEvidence(modelId, "02-analysis/rev-002/cad-parameters.json", JSON.stringify({ units: "normalized", dimensionsMm: null }));
  const reviewed = saveStageReviewEvidence(modelId, "02-analysis", {
    expectedRevision: delegated.revision,
    assets: [
      { id: cadId, slot: "interactive-cad", path: cadPath, role: "validation", sourceAssetIds: [boardId] },
      { id: snapshotId, slot: "parameter-snapshot", path: snapshotPath, role: "validation", sourceAssetIds: [discoveryId] }
    ],
    reviewedArtifactId: cadId,
    governingContractAssetId: discoveryId,
    parameterSnapshotAssetId: snapshotId,
    completedChecklist: [...GENERIC_STAGE_REVIEW_RULES["02-analysis"].checklist],
    interactionMode: "interactive-cad",
    browserTimestamp: new Date().toISOString(),
    reviewDevice: "headless Chromium desktop"
  });
  assert.equal(reviewed.stages[1].status, "ready_for_review");
  assert.equal(stageReadiness(reviewed, "02-analysis").ready, true);

  const approved = approveStageFromDelegation(modelId, "02-analysis", { expectedRevision: reviewed.revision });
  assert.equal(approved.stages[1].status, "approved");
  assert.equal(approved.stages[1].decision.decidedBy, "agent-under-user-delegation");
  assert.equal(approved.stages[1].decision.exactUserWording, exactUserWording);
  assert.equal(approved.stages[1].decision.humanReviewed, false);
  assert.equal(approved.stages[1].decision.individualUserApproval, false);
  const event = readHistory(modelId)[0];
  assert.equal(event.type, "stage-approved");
  assert.equal(event.exactUserWording, exactUserWording);
  assert.equal(event.humanReviewed, false);
  assert.equal(event.individualUserApproval, false);
  assert.equal(event.reviewedArtifactSha256, approved.stages[1].reviewEvidenceSpec.reviewedArtifactSha256);
  assert.equal(event.physicalPhoneInstallAuthorized, false);
});

test("an ordinary model can register and delegated-approve a generic Gate 05 revision", (t) => {
  const modelId = `zz-test-generic-evidence-${suffix}`;
  const cleanup = () => fs.rmSync(pipelineDirectory(modelId), { recursive: true, force: true });
  t.after(cleanup);
  cleanup();
  createModelPipeline({ id: modelId, name: "通用白模测试", mechanism: "rotor" });
  const contractPath = writeEvidence(modelId, "03-contract/rev-001/modeling-contract.json", JSON.stringify({ units: "millimeters", dimensions: { length: 60 } }));
  const architecturePath = writeEvidence(modelId, "04-architecture/rev-001/part-tree.json", JSON.stringify({ parts: ["body"] }));
  const manifest = JSON.parse(fs.readFileSync(path.join(pipelineDirectory(modelId), "pipeline.json"), "utf8"));
  const contractId = `${modelId}-contract-r001`;
  const architectureId = `${modelId}-architecture-r001`;
  manifest.assets.push(
    {
      id: contractId,
      stageId: "03-contract",
      slot: "modeling-contract",
      path: contractPath,
      sha256: sha256File(resolveRepoPath(contractPath)),
      exists: true,
      role: "contract",
      producer: { name: "test", version: "1" },
      sourceAssetIds: []
    },
    {
      id: architectureId,
      stageId: "04-architecture",
      slot: "part-tree",
      path: architecturePath,
      sha256: sha256File(resolveRepoPath(architecturePath)),
      exists: true,
      role: "process",
      producer: { name: "test", version: "1" },
      sourceAssetIds: [contractId]
    }
  );
  for (let index = 0; index <= 3; index += 1) {
    manifest.stages[index].status = "approved";
    manifest.stages[index].decision = { action: "approve", notes: "fixture", decidedBy: "test", decidedAt: new Date().toISOString() };
  }
  manifest.stages[2].artifactIds = [contractId];
  manifest.stages[3].artifactIds = [architectureId];
  saveManifest(manifest, null);
  const delegated = registerStageApprovalDelegation(modelId, {
    expectedRevision: manifest.revision,
    exactUserWording,
    fromStageId: "05-blockout",
    toStageId: "12-shipping"
  });

  const sourceId = `${modelId}-white-source-r001`;
  const heroId = `${modelId}-white-hero-r001`;
  const sourcePath = writeEvidence(modelId, "05-blockout/rev-001/white-model.blend", Buffer.from("BLENDER"));
  const heroPath = writeEvidence(modelId, "05-blockout/rev-001/white-model-hero.png", Buffer.from("PNG"));
  const core = saveGenericStageEvidenceRevision(modelId, "05-blockout", {
    expectedRevision: delegated.revision,
    assets: [
      { id: sourceId, slot: "white-model-source", path: sourcePath, role: "source-model", sourceAssetIds: [architectureId] },
      { id: heroId, slot: "white-model-hero", path: heroPath, role: "blender-render", sourceAssetIds: [sourceId] }
    ],
    reviewArtifactIds: [heroId],
    validations: [
      { id: "deterministic-source", status: "pass", evidence: "The source is generated by a deterministic fixture." },
      { id: "dimensions-match-contract", status: "pass", evidence: "The white model follows the current contract." }
    ]
  });
  assert.equal(core.stages[4].status, "draft");
  assert.equal(core.stages[4].readiness.ready, false);
  assert.match(core.stages[4].readiness.reasons.join(" "), /交互|录屏/);

  const glbId = `${modelId}-white-review-r002`;
  const snapshotId = `${modelId}-white-parameters-r002`;
  const glbPath = writeEvidence(modelId, "05-blockout/rev-002/white-model-review.glb", Buffer.from("glTF"));
  const snapshotPath = writeEvidence(modelId, "05-blockout/rev-002/white-model-parameters.json", JSON.stringify({ units: "millimeters", length: 60 }));
  const review = saveStageReviewEvidence(modelId, "05-blockout", {
    expectedRevision: core.revision,
    assets: [
      { id: glbId, slot: "interaction-evidence", path: glbPath, role: "validation", sourceAssetIds: [sourceId] },
      { id: snapshotId, slot: "parameter-snapshot", path: snapshotPath, role: "validation", sourceAssetIds: [sourceId] }
    ],
    reviewedArtifactId: glbId,
    governingContractAssetId: contractId,
    parameterSnapshotAssetId: snapshotId,
    completedChecklist: [...GENERIC_STAGE_REVIEW_RULES["05-blockout"].checklist],
    interactionMode: "interactive-3d",
    browserTimestamp: new Date().toISOString(),
    reviewDevice: "headless Chromium desktop"
  });
  assert.equal(review.stages[4].status, "ready_for_review");
  assert.equal(review.stages[4].readiness.ready, true);
  const approved = approveStageFromDelegation(modelId, "05-blockout", { expectedRevision: review.revision });
  assert.equal(approved.stages[4].status, "approved");
  assert.equal(approved.stages[5].status, "blocked");
  assert.equal(approved.stages[4].delegatedApproval.governingContractAssetId, contractId);
});
