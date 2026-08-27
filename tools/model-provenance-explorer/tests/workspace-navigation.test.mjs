import assert from "node:assert/strict";
import test from "node:test";
import {
  WORKSPACE_TABS,
  buildWorkspaceRoute,
  parseWorkspaceRoute,
  resolveWorkspaceLocation,
  workspaceTabStatus
} from "../workspace-navigation-core.mjs";

const manifest = {
  currentStageId: "05-blockout",
  stages: [
    ["01-intake", "approved"],
    ["02-analysis", "approved"],
    ["03-contract", "approved"],
    ["04-architecture", "approved"],
    ["05-blockout", "ready_for_review"],
    ["06-geometry", "stale"],
    ["07-material", "stale"],
    ["08-lighting", "stale"],
    ["09-environment", "stale"],
    ["10-export", "stale"],
    ["11-unity-parity", "stale"],
    ["12-shipping", "rejected"]
  ].map(([id, status]) => ({ id, status }))
};

test("keeps the fixed seven-tab information architecture", () => {
  assert.deepEqual(WORKSPACE_TABS.map((tab) => tab.label), [
    "参考原图",
    "分析（截图/视频）",
    "尺寸",
    "交互 CAD",
    "白模",
    "贴图与材质",
    "Unity 灯光与成品"
  ]);
});

test("prefers deep links, then memory, then the current task", () => {
  assert.deepEqual(
    resolveWorkspaceLocation({
      route: { tabId: "cad", stageId: "02-analysis" },
      memory: { tabId: "materials", stageId: "07-material", scrollY: 240 },
      manifest
    }).stageId,
    "02-analysis"
  );
  assert.equal(resolveWorkspaceLocation({
    memory: { tabId: "materials", stageId: "07-material", scrollY: 240 },
    manifest
  }).stageId, "07-material");
  assert.equal(resolveWorkspaceLocation({ manifest }).stageId, "05-blockout");
});

test("never redirects an explicit historical selection to the earliest problem", () => {
  const resolved = resolveWorkspaceLocation({
    route: { tabId: "unity", stageId: "12-shipping", assetId: "historical-shipping" },
    manifest
  });
  assert.equal(resolved.stageId, "12-shipping");
  assert.equal(resolved.assetId, "historical-shipping");
  assert.equal(resolved.explicit, true);
});

test("labels current, approved, stale and rejected tabs", () => {
  const statuses = Object.fromEntries(WORKSPACE_TABS.map((tab) => [tab.id, workspaceTabStatus(tab, manifest)]));
  assert.equal(statuses.references, "approved");
  assert.equal(statuses.blockout, "current");
  assert.equal(statuses.materials, "stale");
  assert.equal(statuses.unity, "rejected");
});

test("round-trips direct model, tab, gate and asset routes", () => {
  const route = buildWorkspaceRoute({
    modelId: "magnetic-slide-tile",
    tabId: "blockout",
    stageId: "05-blockout",
    assetId: "gate05-glb"
  });
  assert.deepEqual(parseWorkspaceRoute(route), {
    modelId: "magnetic-slide-tile",
    tabId: "blockout",
    stageId: "05-blockout",
    assetId: "gate05-glb"
  });
});

