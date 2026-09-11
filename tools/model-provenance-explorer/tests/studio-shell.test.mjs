import assert from "node:assert/strict";
import fs from "node:fs";
import path from "node:path";
import test from "node:test";
import { fileURLToPath } from "node:url";

const toolDir = path.dirname(path.dirname(fileURLToPath(import.meta.url)));
const html = fs.readFileSync(path.join(toolDir, "index.html"), "utf8");
const app = fs.readFileSync(path.join(toolDir, "app.js"), "utf8");
const css = fs.readFileSync(path.join(toolDir, "styles.css"), "utf8");

test("studio shell keeps the persistent workbench information architecture", () => {
  for (const id of ["current-model-title", "model-nav", "current-task-banner", "stage-rail", "workspace-tabs", "stage-detail"]) {
    assert.match(html, new RegExp(`id="${id}"`), `${id} must stay in index.html`);
  }
  const order = ["model-nav", "workspace-tabs", "current-task-banner", "stage-rail", "stage-detail", "decision-panel", "material-library-panel", "export-panel"]
    .map((id) => html.indexOf(`id="${id}"`));
  assert.ok(order.every((index) => index >= 0));
  assert.deepEqual(order, [...order].sort((a, b) => a - b), "left rail → canvas → right rail order");
});

test("studio right rail hosts decision, material library and export panels", () => {
  for (const id of ["decision-panel", "material-library-panel", "export-panel", "material-dialog"]) {
    assert.match(html, new RegExp(`id="${id}"`));
  }
  assert.match(app, /function renderDecisionPanel\(/);
  assert.match(app, /function renderMaterialLibraryPanel\(/);
  assert.match(app, /function renderExportPanel\(/);
  assert.match(app, /api\("\/api\/material-library"\)/);
  assert.doesNotMatch(app, /\$\{approvalPanel\(stage\)\}\s*`;\s*els\.stageDetail\.querySelectorAll/, "approval panel moved out of the canvas");
});

test("studio layout is a three-column grid with a canvas and no AI model selector", () => {
  assert.match(css, /\.workspace \{ display: grid; grid-template-columns: var\(--studio-left\) minmax\(0, 1fr\) var\(--studio-right\);/);
  assert.match(css, /\.studio-canvas \{/);
  assert.match(css, /\.studio-tile-grid \{/);
  assert.doesNotMatch(html, /Gemini|Nano Banana|model-select/i);
  assert.doesNotMatch(app, /Gemini|Nano Banana/i);
});

test("canonical progress and roadmap selectors survive for browser tests", () => {
  for (const selector of ["canonical-progress", "gate-roadmap-item", "workspace-tab", "approve-stage", "reject-stage"]) {
    assert.match(app, new RegExp(selector));
  }
  assert.match(app, /data-current-gate|dataset\.currentGate/);
  assert.match(app, /dataset\.approvedCount/);
});

test("12-gate roadmap nests under the 7 tabs; the middle dot row is gone", () => {
  assert.doesNotMatch(app, /gate-dots|phase-button|workflowPhases/);
  assert.match(app, /class="gate-roadmap" role="list"/);
  assert.match(app, /workspace-group \$\{expanded/);
  assert.match(app, /els\.stageRail\.hidden = true/);
});

test("green marks the approve action and a short allowlist of key options", () => {
  const primaryLines = app.split("\n").filter((line) => line.includes("button-primary"));
  assert.ok(primaryLines.length > 0);
  for (const line of primaryLines) assert.match(line, /id="approve-stage"|id="request-work"|id="begin-measurements"/, line.trim());
  const htmlPrimary = html.split("\n").filter((line) => line.includes("button-primary"));
  assert.deepEqual(htmlPrimary.map((line) => /id="([^"]+)"/.exec(line)?.[1]), ["new-model-button", "new-model-submit"], "new-model entry and its dialog submit are the only static primaries");
  const allowed = new Set([
    ".button-primary", ".button-accent", ".button-accent:hover",
    ".workspace-group[data-step=\"current\"] .workspace-tab::before", ".agent-pulse",
    ".intake-drop:hover, .intake-drop:focus-visible, .intake-drop.is-over",
    ".new-model-form input[type=\"text\"]:focus, .new-model-form select:focus",
    ".studio-header-meta span:first-child strong",
    ".hero-thumb.is-active", ".studio-status-pill[data-status=\"approved\"]",
    ".material-sphere:hover", ".shipping-thumb:hover", ".export-links a:hover"
  ]);
  const accentUses = css.split("\n").filter((line) => /var\(--accent\)/.test(line) && !line.startsWith(":root") && !line.startsWith("  --"));
  for (const line of accentUses) assert.ok(allowed.has(line.split("{")[0].trim()), `unexpected accent use: ${line}`);
  assert.doesNotMatch(css, /\.tab-status|gate-dots/);
  assert.doesNotMatch(css, /\.model-button[^\n]*var\(--accent\)/, "model rows stay grey; green marks the step");
});

test("hero GLB renders inline with orbit controls", () => {
  assert.match(app, /function mountHeroViewer\(/);
  assert.match(app, /data-hero-viewer=/);
  assert.match(app, /async function openGlbAsset\(asset, \{ container = els\.assetStage/);
  assert.match(app, /extension\(asset\.path\) === "glb" \? 0/);
});

test("bespoke gate briefs fold to one question line", () => {
  assert.match(app, /function compactBriefs\(root\)/);
  assert.match(app, /compactBriefs\(els\.stageDetail\)/);
  assert.match(css, /\.brief-more > summary/);
  assert.doesNotMatch(css, /h2 \{[^}]*clamp\(/, "no clamp() display headings left in the canvas");
});

test("new models and Gate 01 references are created from the page, not the terminal", () => {
  for (const id of ["new-model-button", "new-model-dialog", "new-model-name", "new-model-id", "new-model-mechanism", "new-model-drop", "new-model-files", "new-model-submit"]) {
    assert.match(html, new RegExp(`id="${id}"`), `${id} must exist`);
  }
  assert.match(app, /api\("\/api\/models", \{ method: "POST"/);
  assert.match(app, /\/intake-file`/);
  assert.match(app, /function intakeDropPanel\(compact\)/);
  assert.match(app, /stage\.id === "01-intake" \? intakeDropPanel\(visibleAssets\.length > 0\)/);
  assert.match(app, /function wireDropZone\(zone, input, onFiles\)/);
  assert.match(app, /selectWorkspace\(\{ tabId: "references", stageId: "01-intake" \}\)/);
});

test("steps read as one stepper line; new model is pinned at the sidebar foot", () => {
  assert.match(html, /<div class="sidebar-foot">\s*<button type="button" class="button button-primary" id="new-model-button">/);
  assert.ok(html.indexOf('id="workspace-tabs"') < html.indexOf('id="new-model-button"'), "button sits below the steps");
  assert.match(app, /data-step="\$\{step\}"/);
  assert.match(app, /stages\.some\(\(stage\) => stage\.id === workflowStage\.id\) \? "current" : status === "approved" \? "done"/, "exactly one step is current: the workflow stage");
  assert.match(css, /\.workspace-group::before \{[^}]*width: 1px/);
  assert.match(css, /\.workspace-group \.workspace-tab::before \{[^}]*border-radius: 50%/);
  assert.doesNotMatch(css, /\.workspace-tab\[data-status="stale"\]::after/, "no floating status dots on tabs");
  assert.match(app, /stage\.status === "stale" \? "过期" : "退回"/, "gate rows spell out stale/rejected instead of a dot");
});

test("new-model dialog accepts an Obsidian link and pre-fills from the note", () => {
  assert.match(html, /id="new-model-obsidian"/);
  assert.ok(html.indexOf('id="new-model-obsidian"') < html.indexOf('id="new-model-name"'), "link field comes first: it fills the rest");
  assert.match(app, /\/api\/obsidian\/preview\?link=/);
  assert.match(app, /\/intake-from-obsidian`/);
  assert.match(app, /els\.newModelName\.value = note\.title/);
  assert.match(app, /els\.newModelMechanism\.value = note\.mechanismGuess/);
});

test("agent-produced gates show one CTA, then a progress line; the workbench never fakes execution", () => {
  assert.match(app, /function agentStepPanel\(stage\)/);
  assert.match(app, /data-agent-step="idle"[\s\S]*id="request-work"/);
  assert.match(app, /data-agent-step="running"[\s\S]*agent-pulse[\s\S]*id="withdraw-work"/);
  assert.match(app, /data-agent-step="\$\{failed \? "failed" : "finished"\}"/);
  assert.match(app, /data-agent-step="handoff"[\s\S]*agent-pulse[\s\S]*id="agent-login"/, "no CLI login → request stands, login is optional and secondary");
  assert.doesNotMatch(app, /button-primary" id="agent-login"/, "login is never the primary action");
  assert.match(app, /setInterval\(\(\) => pollAgentWork\(stage\), 3000\)/, "running state polls for progress");
  assert.match(app, /status\.revision !== state\.manifest\.revision[\s\S]*loadModel\(state\.activeModelId, true\)/, "manifest change reloads the gate");
  assert.match(app, /data-agent-step="blocked"/);
  for (const stageId of ["02-analysis", "03-contract", "04-architecture", "05-blockout", "06-geometry", "07-material", "08-lighting", "09-environment", "10-export", "11-unity-parity", "12-shipping"]) {
    assert.match(app, new RegExp(`"${stageId}": \\{ does:`), `${stageId} has agent copy`);
  }
  assert.match(app, /\/work-request`/);
  assert.match(app, /humanizeSlots\(reasons\[0\]\)/, "right rail speaks Chinese, not slot ids");
  assert.match(css, /@keyframes agent-pulse/);
});

test("approving a gate lands on the next gate with a stage-aware note", () => {
  assert.match(app, /在工作台确认「\$\{decidedStage\.contract\.title\}」/);
  assert.doesNotMatch(app, /Interactive CAD geometry checklist completed/);
  assert.match(app, /const next = action === "approve" \? state\.manifest\.stages\[/);
  assert.match(app, /selectWorkspace\(\{ stageId: next\.id \}\)/);
});

test("plain models can review Gate 02, fill Gate 03, and request Gate 04 without bespoke ids", () => {
  assert.match(app, /plainStagePurpose\("看原图和视频，确认它是什么机构、各部分怎么动。"\)/);
  assert.match(app, /isLinearMagneticSlider\(\) && previousGateIsApproved\("03-contract"\)/);
  assert.match(app, /data-measurement-unknown=/);
  assert.match(app, /state: unknown \? "unknown" : "known"/);
  assert.match(app, /不知道 · 待补/);
  assert.match(app, /id="begin-measurements">开始填尺寸/);
  assert.match(app, /state\.manifest\.model\.id === "magnetic-slide-tile" \? \[\{ value: "估算", label: "我估的" \}\] : \[\]/, "new sliders are not prompted to infer millimetres");
  assert.match(app, /plainStagePurpose\("确认零件怎么分、谁固定、谁移动，以及它们如何连接。"\)/);
  assert.match(app, /genericEarlyGate[\s\S]*agentStepPanel\(stage\)/, "a purpose header must not suppress the agent CTA");
  assert.match(app, /这 9 项尺寸正确，继续/);
  assert.match(app, /零件与运动关系正确，继续/);
  assert.match(app, /function hasBespokeInteractiveCad\(stage\)/);
  assert.match(app, /if \(hasBespokeInteractiveCad\(stage\)\) mountCadInspection\(\)/);
  assert.match(app, /approvedSliderClaim[\s\S]*method: "PATCH"[\s\S]*mechanism: "linear-magnetic-slider"/, "approving the explicit mechanism claim opens the nine-field route");
  assert.doesNotMatch(app, /已关联 \$\{result\.assetId\}/, "business UI must not expose an internal asset id");
});

test("Gate 03 records auditable official specs and teardown calibration without exposing ids", () => {
  for (const label of ["我实测的", "同款正式规格", "同款公开拆解校准", "公开链接", "正式规格锚点", "锚点正式值 mm", "锚点像素跨度", "目标像素跨度"]) {
    assert.match(app, new RegExp(label), `${label} is available in the measurement form`);
  }
  assert.match(app, /name="\$\{definition\.id\}BasisType"/);
  assert.match(app, /name="\$\{fieldId\}SourceAssetIds"/);
  assert.match(app, /measurementProvenanceVersion: keepsLegacyEstimate \? 0 : 1/);
  assert.match(app, /sourceAssetIds = \[\.\.\.new Set\(\[\.\.\.selectedSourceAssetIds, \.\.\.anchorSourceAssetIds\]\)\]/, "a calibrated field carries its official anchor evidence");
  assert.match(app, /measured: !unknown && basisType === MEASUREMENT_BASIS_TYPES\.userMeasured/);
  assert.match(app, /\/measurement-source`[\s\S]*basisType,[\s\S]*sourceUrl:/, "evidence uploads use the typed source endpoint");
  assert.match(app, /sourceAssets: measurementSourceCatalogForUi\(\)[\s\S]*strictProvenance:/);
  assert.match(app, /measurementEvidenceLabel\(asset, index\)/, "visible evidence labels are human names, not asset ids");
  assert.match(css, /\.measurement-calibration-grid/);
});
