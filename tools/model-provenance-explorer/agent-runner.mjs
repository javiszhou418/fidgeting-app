// Launches a headless Cursor agent (`agent -p`) for one gate of one model and
// tracks the run outside the manifest, because the agent itself edits the manifest.
import fs from "node:fs";
import path from "node:path";
import { spawn } from "node:child_process";
import { loadManifest, pipelineDirectory, resolveRepoPath, requestStageWork, PipelineError } from "./pipeline-core.mjs";
import { STAGE_BY_ID } from "./pipeline-contract.mjs";

const REPO_ROOT = resolveRepoPath(".");
const AGENT_BIN = process.env.FIDGET_AGENT_BIN || "agent";
const live = new Map(); // runKey -> ChildProcess

function runsDirectory(modelId) {
  return path.join(pipelineDirectory(modelId), "agent-runs");
}

function indexFile(modelId) {
  return path.join(runsDirectory(modelId), "index.json");
}

function readIndex(modelId) {
  try { return JSON.parse(fs.readFileSync(indexFile(modelId), "utf8")); } catch { return { runs: [] }; }
}

function writeIndex(modelId, index) {
  fs.mkdirSync(runsDirectory(modelId), { recursive: true });
  fs.writeFileSync(indexFile(modelId), JSON.stringify(index, null, 2));
}

function runKey(modelId, stageId) {
  return `${modelId}:${stageId}`;
}

function pidAlive(pid) {
  if (!pid) return false;
  try { process.kill(pid, 0); return true; } catch { return false; }
}

export function buildStagePrompt(manifest, stageId) {
  const contract = STAGE_BY_ID.get(stageId);
  const gate = String(contract.number).padStart(2, "0");
  const modelDir = `unity/FidgetingApp/ArtSource/ModelPipeline/${manifest.model.id}`;
  const saver = {
    "02-analysis": "saveAnalysisResearchRevision",
    "03-contract": "saveModelingContract",
    "04-architecture": "saveArchitecturePlan",
    "05-blockout": "saveGenericStageEvidenceRevision",
    "06-geometry": "saveGenericStageEvidenceRevision",
    "07-material": "saveGenericStageEvidenceRevision",
    "08-lighting": "saveGenericStageEvidenceRevision",
    "09-environment": "saveGenericStageEvidenceRevision",
    "10-export": "saveGenericStageEvidenceRevision",
    "11-unity-parity": "saveGenericStageEvidenceRevision",
    "12-shipping": "saveGenericStageEvidenceRevision"
  }[stageId];
  const delegation = manifest.currentState?.approvalDelegation;
  const fromNumber = STAGE_BY_ID.get(delegation?.fromStageId)?.number;
  const toNumber = STAGE_BY_ID.get(delegation?.toStageId)?.number;
  const delegated = delegation?.mode === "agent-self-approve-after-evidence"
    && Number.isFinite(fromNumber)
    && Number.isFinite(toNumber)
    && contract.number >= fromNumber
    && contract.number <= toNumber;
  const guidedSliderInstruction = manifest.model.mechanism === "linear-magnetic-slider" && stageId === "03-contract"
    ? "Gate 03 使用 measurementSchemaVersion=2、measurementProvenanceVersion=1 的九项测量合同。每项只能是用户实测、带当前素材哈希的同款正式规格，或带正式规格锚点和像素比例计算的同款公开拆解校准；都必须包含 mm、来源、方法与不确定度。拆解校准只可称可逆的数字重建暂定目标，不得称实测、物理定值或加工尺寸。禁止按品类、手掌、手套、其他型号或无比例照片泛化猜 mm；用户可明确标为 unknown，但 unknown 不计完成，九项未齐时保持 blocked，且不得创建 Blender 白模。"
    : manifest.model.mechanism === "linear-magnetic-slider" && stageId === "04-architecture"
      ? "Gate 04 只能在九项测量合同已批准后开始；生成当前模型自己的 part-tree 与 exploded-plan，不得引用 magnetic-slide-tile 的固定素材 ID 或参数。"
      : "";
  return [
    `你是 Fidgeting Model Studio 工作台派发的后台任务，在仓库根目录工作。`,
    `任务：为模型 \`${manifest.model.id}\`（${manifest.model.name}，机构 ${manifest.model.mechanism}）完成 Gate ${gate} · ${contract.title}。`,
    `1. 先读 skills/fidgeting-model-pipeline/SKILL.md 和 skills/fidgeting-model-pipeline/references/pipeline-contract.md 里 Gate ${gate} 的要求，再读 AGENTS.md 的相关 gate 约束。`,
    `2. 上游素材在 ${modelDir}/evidence/（Gate 01 的图片、视频、obsidian-note.md 是用户给的原始参考）。manifest 是 ${modelDir}/pipeline.json，当前 revision ${manifest.revision}。`,
    `3. 产出并登记这些必需槽位：${contract.requiredSlots.join("、")}。文件放在 ${modelDir}/evidence/${stageId}/rev-NNN/。登记用 tools/model-provenance-explorer/pipeline-core.mjs 的保存函数${saver ? `（本关是 ${saver}）` : ""}。Gate 05–12 的通用保存函数先登记核心产物，再用 saveStageReviewEvidence 登记真实交互或完整录屏、合同哈希、参数快照、检查表、时间戳与设备。`,
    ...(guidedSliderInstruction ? [guidedSliderInstruction] : []),
    delegated
      ? `4. 用户已用原话“${delegation.exactUserWording}”授权逐关自行通过。它不是跳关：只有本关全部必需槽位、验证和 saveStageReviewEvidence 都有效后，才可调用 approveStageFromDelegation；必须逐关单独留下决定记录，humanReviewed 必须保持 false。unknown 尺寸仍阻塞；不得泛化猜 mm，但 Gate 03 可使用哈希绑定的同款正式规格与可复核的同款公开拆解校准。Gate 04 未批准前不能建 Blender，且不授权安装手机。`
      : `4. 本模型没有覆盖本关的逐关批准委托；只交付待审批证据，不要自己批准。`,
    `5. 禁止：git commit / push、安装到手机、修改其他模型、删除既有证据。Gate 11–12 只允许编辑器或 Simulator 的真实运行预览；本任务不授权物理手机安装。`,
    `6. 结束时用不超过 5 句中文说明：产出了什么、用户在工作台哪里能看到、哪些结论不确定需要用户判断。`
  ].join("\n");
}

export function startStageRun(modelId, stageId, { expectedRevision, note = "" } = {}) {
  const key = runKey(modelId, stageId);
  const current = getStageRun(modelId, stageId);
  if (current?.status === "running") throw new PipelineError("这一步已经在跑了。", 409);
  const manifest = requestStageWork(modelId, stageId, { expectedRevision, action: "request", note });
  const startedAt = new Date().toISOString();
  const id = `${stageId}-${startedAt.replace(/[:.]/g, "-")}`;
  const dir = runsDirectory(modelId);
  fs.mkdirSync(dir, { recursive: true });
  const logPath = path.join(dir, `${id}.ndjson`);
  const errPath = path.join(dir, `${id}.stderr.log`);
  const prompt = buildStagePrompt(manifest, stageId);
  fs.writeFileSync(path.join(dir, `${id}.prompt.md`), prompt);
  const out = fs.openSync(logPath, "a");
  const err = fs.openSync(errPath, "a");
  let child;
  try {
    child = spawn(AGENT_BIN, ["-p", "--trust", "--force", "--output-format", "stream-json", "--workspace", REPO_ROOT, prompt], {
      cwd: REPO_ROOT, detached: true, stdio: ["ignore", out, err], env: process.env
    });
  } catch (error) {
    throw new PipelineError(`无法启动 agent：${error.message}`, 500);
  }
  child.unref();
  live.set(key, child);
  const record = { id, stageId, pid: child.pid, startedAt, logPath: path.relative(REPO_ROOT, logPath), errPath: path.relative(REPO_ROOT, errPath), status: "running", exitCode: null, endedAt: null };
  const index = readIndex(modelId);
  index.runs = index.runs.filter((run) => run.stageId !== stageId || run.status !== "running");
  index.runs.push(record);
  writeIndex(modelId, index);
  child.on("exit", (code) => {
    live.delete(key);
    const latest = readIndex(modelId);
    const run = latest.runs.find((candidate) => candidate.id === id);
    if (run) {
      run.status = code === 0 ? "done" : "failed";
      run.exitCode = code;
      run.endedAt = new Date().toISOString();
      writeIndex(modelId, latest);
    }
  });
  child.on("error", () => {
    live.delete(key);
    const latest = readIndex(modelId);
    const run = latest.runs.find((candidate) => candidate.id === id);
    if (run) { run.status = "failed"; run.endedAt = new Date().toISOString(); writeIndex(modelId, latest); }
  });
  return { manifest, run: publicRun(modelId, record) };
}

export function stopStageRun(modelId, stageId, { expectedRevision } = {}) {
  const run = readIndex(modelId).runs.findLast((candidate) => candidate.stageId === stageId);
  if (run && run.status === "running" && pidAlive(run.pid)) {
    try { process.kill(-run.pid, "SIGTERM"); } catch { try { process.kill(run.pid, "SIGTERM"); } catch { /* already gone */ } }
    const index = readIndex(modelId);
    const target = index.runs.find((candidate) => candidate.id === run.id);
    if (target) { target.status = "stopped"; target.endedAt = new Date().toISOString(); writeIndex(modelId, index); }
  }
  const manifest = requestStageWork(modelId, stageId, { expectedRevision, action: "withdraw" });
  return { manifest, run: null };
}

// Pull a human-readable "what is it doing now" line out of the stream-json log.
function summarizeLog(absoluteLogPath) {
  let text = "";
  try { text = fs.readFileSync(absoluteLogPath, "utf8"); } catch { return { lastActivity: "", finalText: "", events: 0 }; }
  const lines = text.split("\n").filter(Boolean);
  let lastActivity = "";
  let finalText = "";
  for (const line of lines) {
    let event;
    try { event = JSON.parse(line); } catch { continue; }
    const type = event.type || event.event || "";
    if (type === "result" || event.subtype === "success") {
      finalText = typeof event.result === "string" ? event.result : finalText;
    } else if (type === "assistant" || event.role === "assistant") {
      const content = event.message?.content ?? event.content;
      const chunk = Array.isArray(content) ? content.map((part) => part.text || "").join("") : (typeof content === "string" ? content : "");
      if (chunk.trim()) { lastActivity = chunk.trim().slice(0, 140); finalText = chunk.trim(); }
    } else if (type === "tool_call" || event.tool_call || event.toolCall) {
      const call = event.tool_call || event.toolCall || {};
      const name = Object.keys(call).find((k) => typeof call[k] === "object") || call.name || event.subtype || "tool";
      const args = call[name]?.args || {};
      const target = args.path || args.command || args.pattern || args.glob_pattern || "";
      lastActivity = `${name}${target ? ` · ${String(target).slice(0, 80)}` : ""}`;
    } else if (event.subtype) {
      lastActivity = String(event.subtype);
    }
  }
  return { lastActivity, finalText, events: lines.length };
}

function publicRun(modelId, run) {
  if (!run) return null;
  const alive = run.status === "running" && pidAlive(run.pid);
  let status = run.status;
  if (run.status === "running" && !alive && !live.has(runKey(modelId, run.stageId))) {
    // Server restarted or the process died without our exit hook; the log is the only witness.
    status = "ended";
  }
  const { lastActivity, finalText, events } = summarizeLog(path.join(REPO_ROOT, run.logPath));
  let error = "";
  if (status === "failed" || status === "ended") {
    try { error = fs.readFileSync(path.join(REPO_ROOT, run.errPath), "utf8").trim().split("\n").slice(-3).join(" ").slice(0, 300); } catch { /* no stderr */ }
  }
  const needsLogin = /Authentication required|agent login/i.test(error);
  return {
    id: run.id, stageId: run.stageId, status, startedAt: run.startedAt, endedAt: run.endedAt, exitCode: run.exitCode,
    elapsedMs: Math.max(0, (run.endedAt ? new Date(run.endedAt) : new Date()) - new Date(run.startedAt)),
    lastActivity, finalText, events, error, needsLogin, logPath: run.logPath
  };
}

export function getStageRun(modelId, stageId) {
  const run = readIndex(modelId).runs.findLast((candidate) => candidate.stageId === stageId);
  return publicRun(modelId, run);
}

export function stageWorkStatus(modelId, stageId) {
  const manifest = loadManifest(modelId);
  return { request: manifest.currentState?.workRequests?.[stageId] || null, run: getStageRun(modelId, stageId), revision: manifest.revision };
}

// `agent login` prints a one-time browser URL; hand it to the UI so nobody needs a terminal.
let loginProcess = null;
export function startAgentLogin() {
  return new Promise((resolve) => {
    if (loginProcess && loginProcess.exitCode === null) { resolve({ url: loginProcess.__url || "", pending: true }); return; }
    const child = spawn(AGENT_BIN, ["login"], { cwd: REPO_ROOT, env: process.env });
    loginProcess = child;
    let buffer = "";
    let settled = false;
    const finish = (payload) => { if (!settled) { settled = true; resolve(payload); } };
    child.stdout.on("data", (chunk) => {
      buffer += String(chunk);
      const match = buffer.match(/https:\/\/\S+/);
      if (match) { child.__url = match[0]; finish({ url: match[0], pending: true }); }
    });
    child.stderr.on("data", (chunk) => { buffer += String(chunk); });
    child.on("exit", (code) => finish({ url: child.__url || "", pending: false, ok: code === 0, output: buffer.slice(-300) }));
    child.on("error", (error) => finish({ url: "", pending: false, ok: false, output: error.message }));
    setTimeout(() => finish({ url: child.__url || "", pending: true, output: buffer.slice(-300) }), 8000);
  });
}

export function agentLoginState() {
  if (!loginProcess) return { active: false };
  return { active: loginProcess.exitCode === null, ok: loginProcess.exitCode === 0, url: loginProcess.__url || "" };
}

export function checkAgentAuth() {
  return new Promise((resolve) => {
    const child = spawn(AGENT_BIN, ["-p", "--trust", "--output-format", "text", "Reply with exactly: OK"], { cwd: REPO_ROOT, env: process.env });
    let out = "";
    child.stdout.on("data", (chunk) => { out += String(chunk); });
    child.stderr.on("data", (chunk) => { out += String(chunk); });
    const timer = setTimeout(() => { child.kill(); resolve({ ok: false, output: "timeout" }); }, 60000);
    child.on("exit", (code) => { clearTimeout(timer); resolve({ ok: code === 0 && !/Authentication required/i.test(out), output: out.trim().slice(-300) }); });
    child.on("error", (error) => { clearTimeout(timer); resolve({ ok: false, output: error.message }); });
  });
}
