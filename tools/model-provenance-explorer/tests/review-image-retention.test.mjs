import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { isReviewImagePath, markRemovedReviewImages, readReviewImageRetention, REMOVED_REVIEW_IMAGE, RETENTION_FILE } from "../review-image-retention.mjs";
import { createModelPipeline, listModelIds, loadManifest, pipelineDirectory, readHistory, refreshManifest, repoRoot, requiredSlotState, saveManifest } from "../pipeline-core.mjs";
import { createServer } from "../server.mjs";

test("retention is limited to review rasters and excludes App assets, sources and videos", () => {
  assert.equal(isReviewImagePath("unity/FidgetingApp/ArtSource/ModelPipeline/model-a/evidence/05-blockout/rev-001/hero.png"), true);
  for (const p of ["unity/FidgetingApp/Assets/hero.png", "unity/FidgetingApp/Docs/hero.png", "Artifacts/Other/hero.png", "Artifacts/TriSpinnerSlab/../../Assets/hero.png", "unity/FidgetingApp/ArtSource/ModelPipeline/model-a/evidence/01-intake/rev-001/photo.png", "unity/FidgetingApp/ArtSource/ModelPipeline/model-a/evidence/10-export/rev-001/package/texture.png", "Artifacts/TriSpinnerSlab/gate05-r001/turntable.mp4"]) {
    assert.equal(isReviewImagePath(p), false, p);
  }
});

test("history decoration preserves reviewed paths and hashes rather than substituting new evidence", () => {
  const oldPath = "Artifacts/TriSpinnerSlab/gate05-r001/hero.png";
  const oldHash = "a".repeat(64);
  const record = { reviewedArtifacts: [{ path: oldPath, sha256: oldHash }], current: { path: "Artifacts/TriSpinnerSlab/gate05-r002/hero.png", sha256: "b".repeat(64) } };
  markRemovedReviewImages(record, new Map([[oldPath, { sha256: oldHash, sizeBytes: 123, removedAt: "2026-10-30T00:00:00Z" }]]));
  assert.equal(record.reviewedArtifacts[0].path, oldPath);
  assert.equal(record.reviewedArtifacts[0].sha256, oldHash);
  assert.equal(record.reviewedArtifacts[0].availability.originalSha256, oldHash);
  assert.equal(record.reviewedArtifacts[0].availability.status, REMOVED_REVIEW_IMAGE);
  assert.equal(record.reviewedArtifacts[0].exists, false);
  assert.equal(record.current.availability, undefined);
});

test("the committed removal index never includes current workflow media or production Assets", () => {
  const index = readReviewImageRetention(repoRoot);
  assert.ok(index.size > 1000);
  for (const entry of index.values()) {
    assert.equal(isReviewImagePath(entry.path), true);
    assert.equal(fs.existsSync(path.join(repoRoot, entry.path)), false, entry.path);
  }
  for (const modelId of listModelIds()) {
    const manifest = loadManifest(modelId);
    const active = new Set(manifest.stages.flatMap((s) => [...(s.artifactIds || []), ...(s.reviewArtifactIds || [])]));
    for (const asset of manifest.assets.filter((a) => active.has(a.id))) assert.equal(index.has(asset.path), false, `${modelId}: ${asset.id}`);
  }
});

test("refresh retains original hashes of retired evidence and does not record a content replacement", () => {
  const entry = readReviewImageRetention(repoRoot).values().next().value;
  const id = `retention-regression-${Date.now()}`;
  const directory = pipelineDirectory(id);
  assert.equal(fs.existsSync(directory), false);
  try {
    createModelPipeline({ id, name: "Retention regression fixture" });
    const manifest = loadManifest(id);
    manifest.assets.push({ id: "retired-review", stageId: "05-blockout", slot: "white-model-hero", path: entry.path, sha256: entry.sha256, sizeBytes: entry.sizeBytes, exists: true, role: "process", sourceAssetIds: [] });
    saveManifest(manifest, null);
    const refreshed = refreshManifest(id, manifest.revision);
    const asset = refreshed.assets.find((a) => a.id === "retired-review");
    assert.equal(asset.sha256, entry.sha256);
    assert.equal(asset.path, entry.path);
    assert.equal(asset.availability.status, REMOVED_REVIEW_IMAGE);
    assert.equal(readHistory(id)[0].changedAssets.includes("retired-review"), false);
  } finally {
    assert.equal(path.dirname(directory), path.join(repoRoot, "unity/FidgetingApp/ArtSource/ModelPipeline"));
    assert.ok(path.basename(directory).startsWith("retention-regression-"));
    fs.rmSync(directory, { recursive: true, force: true });
  }
});

test("storage cleanup preserves the existing shipping review slots", () => {
  const manifest = loadManifest("premium-display-case");
  assert.deepEqual(requiredSlotState(manifest, "12-shipping").missing, []);
  const retention = JSON.parse(fs.readFileSync(path.join(repoRoot, RETENTION_FILE), "utf8"));
  for (const entry of retention.protectedRequiredSlotImages) {
    assert.equal(fs.existsSync(path.join(repoRoot, entry.path)), true, entry.path);
    assert.equal(readReviewImageRetention(repoRoot).has(entry.path), false);
  }
});

test("old image URLs show an explicit removal notice; unrelated missing images still return 404", async () => {
  const entry = readReviewImageRetention(repoRoot).values().next().value;
  const server = createServer();
  await new Promise((resolve, reject) => { server.once("error", reject); server.listen(0, "127.0.0.1", resolve); });
  try {
    const base = `http://127.0.0.1:${server.address().port}`;
    const response = await fetch(`${base}/repo/${entry.path}`);
    assert.equal(response.status, 200);
    assert.equal(response.headers.get("x-fidget-review-image-status"), REMOVED_REVIEW_IMAGE);
    assert.match(response.headers.get("content-type"), /image\/svg\+xml/);
    assert.match(await response.text(), /旧批次验收图已移除/);
    assert.equal((await fetch(`${base}/repo/Artifacts/TriSpinnerSlab/not-a-retired-image.png`)).status, 404);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});
