import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import { setTimeout as sleep } from "node:timers/promises";

// A fake `agent` binary: prints one stream-json line, or fails like an unauthenticated CLI.
const fakeDir = fs.mkdtempSync(path.join(os.tmpdir(), "fake-agent-"));
const fakeBin = path.join(fakeDir, "agent");
fs.writeFileSync(fakeBin, `#!/bin/sh
if [ -n "$FAKE_AGENT_FAIL" ]; then echo "Error: Authentication required. Please run 'agent login' first" >&2; exit 1; fi
echo '{"type":"assistant","message":{"content":[{"type":"text","text":"已读取 3 张参考图，机构判断为滑块"}]}}'
sleep 1
echo '{"type":"result","subtype":"success","result":"分析板已登记，请在工作台 Gate 02 查看。"}'
`);
fs.chmodSync(fakeBin, 0o755);
process.env.FIDGET_AGENT_BIN = fakeBin;

const core = await import("../pipeline-core.mjs");
const runner = await import("../agent-runner.mjs");
const modelId = `zz-test-runner-${process.pid.toString(36)}`;
const cleanup = () => fs.rmSync(core.pipelineDirectory(modelId), { recursive: true, force: true });

test("the prompt names the model, gate, deliverables and the no-approve/no-commit rules", () => {
  cleanup();
  const manifest = core.createModelPipeline({ id: modelId, name: "测试滑块", mechanism: "rotor" });
  const prompt = runner.buildStagePrompt(manifest, "02-analysis");
  assert.match(prompt, new RegExp(modelId));
  assert.match(prompt, /Gate 02/);
  assert.match(prompt, /discovery-log、analysis-board/);
  assert.match(prompt, /saveAnalysisResearchRevision/);
  assert.match(prompt, /不要自己批准/);
  assert.match(prompt, /git commit \/ push/);
  cleanup();
});

test("the slider Gate 03 prompt permits strict same-model provenance but forbids generic inference and premature Blender work", () => {
  cleanup();
  const manifest = core.createModelPipeline({ id: modelId, name: "测试滑块", mechanism: "linear-magnetic-slider" });
  const prompt = runner.buildStagePrompt(manifest, "03-contract");
  assert.match(prompt, /measurementSchemaVersion=2/);
  assert.match(prompt, /九项测量合同/);
  assert.match(prompt, /用户可明确标为 unknown/);
  assert.match(prompt, /同款正式规格/);
  assert.match(prompt, /同款公开拆解校准/);
  assert.match(prompt, /禁止按品类、手掌、手套、其他型号或无比例照片泛化猜 mm/);
  assert.match(prompt, /不得称实测、物理定值或加工尺寸/);
  assert.match(prompt, /不得创建 Blender 白模/);
  cleanup();
});

test("startStageRun launches the agent, tracks running → done, and surfaces its last words", async (t) => {
  t.after(cleanup);
  cleanup();
  const manifest = core.createModelPipeline({ id: modelId, name: "测试滑块", mechanism: "rotor" });
  const started = runner.startStageRun(modelId, "02-analysis", { expectedRevision: manifest.revision });
  assert.equal(started.run.status, "running");
  assert.equal(started.manifest.currentState.workRequests["02-analysis"].status, "requested");
  assert.throws(() => runner.startStageRun(modelId, "02-analysis", { expectedRevision: started.manifest.revision }), /已经在跑/);
  let status;
  for (let i = 0; i < 40; i += 1) {
    await sleep(100);
    status = runner.stageWorkStatus(modelId, "02-analysis");
    if (status.run.status !== "running") break;
  }
  assert.equal(status.run.status, "done");
  assert.equal(status.run.exitCode, 0);
  assert.match(status.run.finalText, /分析板已登记/);
  assert.equal(status.run.needsLogin, false);
  assert.ok(fs.existsSync(path.join(core.pipelineDirectory(modelId), "agent-runs", `${status.run.id}.prompt.md`)));
});

test("an unauthenticated CLI is reported as needsLogin, not as a silent hang", async (t) => {
  t.after(cleanup);
  cleanup();
  process.env.FAKE_AGENT_FAIL = "1";
  t.after(() => { delete process.env.FAKE_AGENT_FAIL; });
  const manifest = core.createModelPipeline({ id: modelId, name: "测试滑块", mechanism: "rotor" });
  runner.startStageRun(modelId, "02-analysis", { expectedRevision: manifest.revision });
  let status;
  for (let i = 0; i < 40; i += 1) {
    await sleep(100);
    status = runner.stageWorkStatus(modelId, "02-analysis");
    if (status.run.status !== "running") break;
  }
  assert.equal(status.run.status, "failed");
  assert.equal(status.run.needsLogin, true);
  const stopped = runner.stopStageRun(modelId, "02-analysis", { expectedRevision: status.revision });
  assert.equal(stopped.manifest.currentState.workRequests["02-analysis"], undefined);
});
