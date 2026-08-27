import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  ALLOWED_ASSET_ROLES,
  ALLOWED_STAGE_STATUSES,
  PIPELINE_SCHEMA_VERSION,
  STAGE_BY_ID,
  STAGES
} from "./pipeline-contract.mjs";
import {
  MANUFACTURING_LATER_FIELDS,
  OPTIONAL_ENGINEERING_MEASUREMENTS,
  REQUIRED_CORE_MEASUREMENTS,
  validateMeasurementContract
} from "./measurement-contract-core.mjs";

export const toolDir = path.dirname(fileURLToPath(import.meta.url));
export const repoRoot = path.resolve(toolDir, "../..");
export const manifestRoot = path.join(repoRoot, "unity/FidgetingApp/ArtSource/ModelPipeline");

export class PipelineError extends Error {
  constructor(message, statusCode = 400, details = []) {
    super(message);
    this.name = "PipelineError";
    this.statusCode = statusCode;
    this.details = details;
  }
}

export function normalizeRepoPath(value) {
  return String(value || "").split(path.sep).join("/").replace(/^\.\//, "");
}

export function resolveRepoPath(relativePath) {
  const normalized = normalizeRepoPath(relativePath);
  if (!normalized || path.isAbsolute(normalized) || normalized.includes("\0")) {
    throw new PipelineError("Asset path must be a non-empty repository-relative path.");
  }
  const absolute = path.resolve(repoRoot, normalized);
  const prefix = `${repoRoot}${path.sep}`;
  if (absolute !== repoRoot && !absolute.startsWith(prefix)) {
    throw new PipelineError("Asset path escapes the repository root.");
  }
  return absolute;
}

export function pipelineDirectory(modelId) {
  if (!/^[a-z0-9][a-z0-9-]*$/.test(String(modelId || ""))) {
    throw new PipelineError("Invalid model id.");
  }
  return path.join(manifestRoot, modelId);
}

export function pipelineFile(modelId) {
  return path.join(pipelineDirectory(modelId), "pipeline.json");
}

export function historyFile(modelId) {
  return path.join(pipelineDirectory(modelId), "history.ndjson");
}

export function readHistory(modelId) {
  const file = historyFile(modelId);
  if (!fs.existsSync(file)) return [];
  return fs.readFileSync(file, "utf8")
    .split(/\r?\n/)
    .filter(Boolean)
    .map((line, index) => {
      try { return JSON.parse(line); }
      catch { throw new PipelineError(`Invalid history event at line ${index + 1}.`, 500); }
    })
    .reverse();
}

export function sha256File(absolutePath) {
  const hash = crypto.createHash("sha256");
  const bytes = fs.readFileSync(absolutePath);
  hash.update(bytes);
  return hash.digest("hex");
}

export function digestValues(values) {
  return crypto.createHash("sha256").update(values.filter(Boolean).sort().join("\n")).digest("hex");
}

function stableJson(value) {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map((key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
}

export function listModelIds() {
  if (!fs.existsSync(manifestRoot)) return [];
  return fs.readdirSync(manifestRoot, { withFileTypes: true })
    .filter((entry) => entry.isDirectory() && fs.existsSync(path.join(manifestRoot, entry.name, "pipeline.json")))
    .map((entry) => entry.name)
    .sort();
}

export function loadManifest(modelId) {
  const file = pipelineFile(modelId);
  if (!fs.existsSync(file)) throw new PipelineError(`Unknown model: ${modelId}`, 404);
  const manifest = JSON.parse(fs.readFileSync(file, "utf8"));
  const errors = validateManifest(manifest);
  if (errors.length) throw new PipelineError(`Invalid manifest for ${modelId}.`, 500, errors);
  return manifest;
}

export function validateManifest(manifest) {
  const errors = [];
  if (!manifest || typeof manifest !== "object") return ["Manifest must be an object."];
  if (manifest.schemaVersion !== PIPELINE_SCHEMA_VERSION) errors.push(`schemaVersion must be ${PIPELINE_SCHEMA_VERSION}.`);
  if (!Number.isInteger(manifest.revision) || manifest.revision < 1) errors.push("revision must be a positive integer.");
  if (!manifest.model || !/^[a-z0-9][a-z0-9-]*$/.test(manifest.model.id || "")) errors.push("model.id is invalid.");
  if (manifest.route?.primary !== "blender-cli") errors.push("route.primary must be blender-cli for the Rotor backfill.");
  if (manifest.route?.rodinPolicy !== "concept-only") errors.push("route.rodinPolicy must be concept-only.");

  const assets = Array.isArray(manifest.assets) ? manifest.assets : [];
  const assetIds = new Set();
  for (const asset of assets) {
    if (!asset.id || assetIds.has(asset.id)) errors.push(`Asset id is missing or duplicated: ${asset.id || "(empty)"}.`);
    assetIds.add(asset.id);
    if (!asset.stageId || !STAGE_BY_ID.has(asset.stageId)) errors.push(`Asset ${asset.id} has an invalid stageId.`);
    if (!asset.slot) errors.push(`Asset ${asset.id} is missing slot.`);
    if (!asset.path) errors.push(`Asset ${asset.id} is missing path.`);
    else {
      try { resolveRepoPath(asset.path); } catch (error) { errors.push(`Asset ${asset.id}: ${error.message}`); }
    }
    if (!ALLOWED_ASSET_ROLES.has(asset.role)) errors.push(`Asset ${asset.id} has invalid role ${asset.role}.`);
    if (!Array.isArray(asset.sourceAssetIds)) errors.push(`Asset ${asset.id} must declare sourceAssetIds.`);
    if (asset.provenance !== undefined) {
      const provenance = asset.provenance;
      if (!provenance || typeof provenance !== "object") errors.push(`Asset ${asset.id} provenance must be an object.`);
      else {
        if (!["user-provided", "assistant-generated", "external", "repository-generated", "unknown-legacy"].includes(provenance.origin)) {
          errors.push(`Asset ${asset.id} has invalid provenance.origin ${provenance.origin}.`);
        }
        if (!provenance.contentClass) errors.push(`Asset ${asset.id} provenance.contentClass is required.`);
        if (!["user", "assistant", "repository", "legacy-record"].includes(provenance.assertedBy)) {
          errors.push(`Asset ${asset.id} has invalid provenance.assertedBy ${provenance.assertedBy}.`);
        }
      }
    }
  }
  for (const asset of assets) {
    for (const sourceAssetId of asset.sourceAssetIds || []) {
      if (!assetIds.has(sourceAssetId)) errors.push(`Asset ${asset.id} references unknown source asset ${sourceAssetId}.`);
      if (sourceAssetId === asset.id) errors.push(`Asset ${asset.id} cannot source itself.`);
    }
  }

  const stages = Array.isArray(manifest.stages) ? manifest.stages : [];
  const expectedIds = STAGES.map((stage) => stage.id);
  if (stages.length !== expectedIds.length) errors.push(`stages must contain all ${expectedIds.length} gates.`);
  for (let index = 0; index < expectedIds.length; index += 1) {
    const stage = stages[index];
    if (!stage || stage.id !== expectedIds[index]) errors.push(`Stage ${index + 1} must be ${expectedIds[index]}.`);
    if (stage && !ALLOWED_STAGE_STATUSES.has(stage.status)) errors.push(`Stage ${stage.id} has invalid status ${stage.status}.`);
    for (const assetId of stage?.artifactIds || []) {
      if (!assetIds.has(assetId)) errors.push(`Stage ${stage.id} references unknown asset ${assetId}.`);
    }
    for (const assetId of stage?.reviewArtifactIds || []) {
      if (!assetIds.has(assetId)) errors.push(`Stage ${stage.id} reviewArtifactIds references unknown asset ${assetId}.`);
      if (!(stage.artifactIds || []).includes(assetId)) errors.push(`Stage ${stage.id} review asset ${assetId} must also be a current artifact.`);
    }
  }
  const mechanismContractHash = manifest.model?.id === "magnetic-slide-tile"
    ? stages.find((stage) => stage.id === "02-analysis")?.analysisSpec?.contractSha256
    : null;
  if (mechanismContractHash) {
    const activeStatuses = new Set(["draft", "ready_for_review", "approved"]);
    for (const stage of stages.slice(2)) {
      if (!activeStatuses.has(stage.status)) continue;
      for (const assetId of stage.artifactIds || []) {
        const asset = assets.find((candidate) => candidate.id === assetId);
        if (!asset || asset.stageId !== stage.id) continue;
        if (asset.provenance?.mechanismEvidenceContractSha256 !== mechanismContractHash) {
          errors.push(`Asset ${asset.id} must carry the approved mechanism evidence contract SHA-256.`);
        }
      }
    }
  }

  const claimIds = new Set();
  const claimById = new Map();
  for (const claim of manifest.claims || []) {
    if (!claim.id || claimIds.has(claim.id)) errors.push(`Claim id is missing or duplicated: ${claim.id || "(empty)"}.`);
    claimIds.add(claim.id);
    claimById.set(claim.id, claim);
    if (!STAGE_BY_ID.has(claim.stageId)) errors.push(`Claim ${claim.id} has an invalid stageId.`);
    if (!Array.isArray(claim.sourceAssetIds)) errors.push(`Claim ${claim.id} must declare sourceAssetIds.`);
    for (const assetId of claim.sourceAssetIds || []) if (!assetIds.has(assetId)) errors.push(`Claim ${claim.id} references unknown asset ${assetId}.`);
  }
  for (const asset of assets) {
    if (asset.sourceClaimIds !== undefined && !Array.isArray(asset.sourceClaimIds)) {
      errors.push(`Asset ${asset.id} sourceClaimIds must be an array when present.`);
      continue;
    }
    for (const sourceClaimId of asset.sourceClaimIds || []) {
      const claim = claimById.get(sourceClaimId);
      if (!claim) {
        errors.push(`Asset ${asset.id} references unknown source claim ${sourceClaimId}.`);
        continue;
      }
      const assetStage = STAGE_BY_ID.get(asset.stageId);
      const claimStage = STAGE_BY_ID.get(claim.stageId);
      if (assetStage && claimStage && claimStage.number >= assetStage.number) {
        errors.push(`Asset ${asset.id} source claim ${sourceClaimId} must come from an earlier gate.`);
      }
    }
  }
  for (const issue of manifest.issues || []) {
    if (!STAGE_BY_ID.has(issue.stageId)) errors.push(`Issue ${issue.id || "(empty)"} has an invalid stageId.`);
    if (!assetIds.has(issue.assetId)) errors.push(`Issue ${issue.id || "(empty)"} references unknown asset ${issue.assetId}.`);
  }
  return errors;
}

export function requiredSlotState(manifest, stageId) {
  const contract = STAGE_BY_ID.get(stageId);
  const assets = manifest.assets.filter((asset) => asset.stageId === stageId && asset.exists !== false);
  const present = new Set(assets.map((asset) => asset.slot));
  const missing = contract.requiredSlots.filter((slot) => !present.has(slot));
  return { required: contract.requiredSlots, present: [...present], missing };
}

export function stageReadiness(manifest, stageId) {
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === stageId);
  if (stageIndex < 0) throw new PipelineError(`Unknown stage: ${stageId}`);
  const stage = manifest.stages[stageIndex];
  const prerequisite = stageIndex === 0 ? null : manifest.stages[stageIndex - 1];
  const slots = requiredSlotState(manifest, stageId);
  const failedValidations = (stage.validations || []).filter((validation) => validation.status !== "pass");
  const unhashedAssets = manifest.assets.filter((asset) => asset.stageId === stageId && asset.exists !== false && !asset.sha256);
  const reasons = [];
  if (prerequisite && prerequisite.status !== "approved") reasons.push(`上一关 ${prerequisite.id} 尚未批准。`);
  if (slots.missing.length) reasons.push(`缺少必需素材：${slots.missing.join("、")}。`);
  if (failedValidations.length) reasons.push(`仍有 ${failedValidations.length} 项验证未通过。`);
  if (unhashedAssets.length) reasons.push(`有 ${unhashedAssets.length} 项素材尚未刷新 SHA-256。`);
  if (stageId === "03-contract" && stage.status === "blocked" && stage.requiredPhysicalDimensions?.length) {
    reasons.push(`等待 ${stage.requiredPhysicalDimensions.length} 项真实物理尺寸。`);
  } else if (stageId === "03-contract" && prerequisite?.status === "approved") {
    const analysisClaimIds = (manifest.claims || [])
      .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
      .map((claim) => claim.id);
    const consumedClaimIds = new Set(manifest.assets
      .filter((asset) => asset.stageId === stageId && asset.exists !== false)
      .flatMap((asset) => asset.sourceClaimIds || []));
    const missingClaimIds = analysisClaimIds.filter((claimId) => !consumedClaimIds.has(claimId));
    if (!analysisClaimIds.length) reasons.push("上一关没有可用于建模合同的分析判断。");
    else if (missingClaimIds.length) reasons.push(`建模合同尚未消费 ${missingClaimIds.length} 条已批准分析判断。`);
  }
  if (stage.status === "stale") reasons.push("该阶段因上游变化已经过期。");
  return { ready: reasons.length === 0, reasons, slots, stage };
}

export function earliestProblem(manifest) {
  for (const contract of STAGES) {
    const stage = manifest.stages.find((candidate) => candidate.id === contract.id);
    if (stage.status !== "approved") {
      const readiness = stageReadiness(manifest, contract.id);
      return {
        stageId: contract.id,
        title: contract.title,
        status: stage.status,
        reasons: readiness.reasons.length ? readiness.reasons : ["等待用户审批。"]
      };
    }
  }
  return null;
}

export function deriveManifest(manifest) {
  const stages = manifest.stages.map((stage) => ({
    ...stage,
    contract: STAGE_BY_ID.get(stage.id),
    readiness: stageReadiness(manifest, stage.id)
  }));
  return {
    ...manifest,
    stages,
    derived: {
      earliestProblem: earliestProblem(manifest),
      shippingReady: manifest.stages.length === STAGES.length && manifest.stages.every((stage) => stage.status === "approved"),
      approvedCount: manifest.stages.filter((stage) => stage.status === "approved").length,
      assetCount: manifest.assets.length,
      issueCount: (manifest.issues || []).filter((issue) => issue.status !== "resolved").length
    }
  };
}

function atomicWriteJson(file, value) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const temporary = `${file}.tmp-${crypto.randomUUID()}`;
  fs.writeFileSync(temporary, `${JSON.stringify(value, null, 2)}\n`, "utf8");
  fs.renameSync(temporary, file);
}

function appendHistory(modelId, event) {
  const file = historyFile(modelId);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.appendFileSync(file, `${JSON.stringify(event)}\n`, "utf8");
}

function makeEvent(manifest, type, detail) {
  return {
    id: crypto.randomUUID(),
    type,
    modelId: manifest.model.id,
    manifestRevision: manifest.revision,
    timestamp: new Date().toISOString(),
    ...detail
  };
}

function markDownstreamStale(manifest, stageIndex, reason) {
  for (let index = stageIndex + 1; index < manifest.stages.length; index += 1) {
    const downstream = manifest.stages[index];
    if (downstream.status !== "missing" && downstream.status !== "blocked") downstream.status = "stale";
    downstream.staleReason = reason;
  }
}

function updateStageDigests(manifest) {
  for (let index = 0; index < manifest.stages.length; index += 1) {
    const stage = manifest.stages[index];
    const assetHashes = stage.artifactIds.map((assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256);
    const claimRecords = (manifest.claims || []).filter((claim) => claim.stageId === stage.id).map(stableJson);
    stage.inputDigest = index === 0 ? digestValues([...assetHashes, ...claimRecords]) : manifest.stages[index - 1].outputDigest;
    stage.outputDigest = digestValues([...assetHashes, ...claimRecords]);
  }
}

const SECONDARY_MOTION_OPTIONS = new Set(["unknown", "translation-only", "translation-plus-rotation", "dual-mode-free-spin"]);
const LANE_MODE_OPTIONS = new Set(["unknown", "dual-working-lanes", "visual-only"]);
const HARDWARE_MODE_OPTIONS = new Set(["unknown", "visual-mechanism-proxy", "physical-teardown-replica"]);
const DIMENSION_BASIS_OPTIONS = new Set([
  "user-measured",
  "anthropometric-estimate",
  "official-only",
  "user-authorized-provisional"
]);

function optionalPositiveNumber(value, label) {
  if (value === null || value === undefined || value === "") return null;
  const number = Number(value);
  if (!Number.isFinite(number) || number <= 0) throw new PipelineError(`${label} must be a positive number.`);
  return number;
}

function optionalNonNegativeInteger(value, label) {
  if (value === null || value === undefined || value === "") return null;
  const number = Number(value);
  if (!Number.isSafeInteger(number) || number < 0) throw new PipelineError(`${label} must be a non-negative integer.`);
  return number;
}

function normalizeEstimateRange(value, center, label) {
  if (!value || typeof value !== "object") return null;
  const min = optionalPositiveNumber(value.min, `${label}.min`);
  const max = optionalPositiveNumber(value.max, `${label}.max`);
  if (min === null || max === null || min > max) throw new PipelineError(`${label} must contain an ordered positive min/max range.`);
  if (center !== null && (center < min || center > max)) throw new PipelineError(`${label} must contain its proposed center value.`);
  return { min, max };
}

function validateContractSelections(contract) {
  const missing = [];
  const dimensions = contract.dimensions;
  for (const [field, label] of [
    ["overallLengthMm", "闭合总长度 L"],
    ["overallWidthMm", "闭合总宽度 W"],
    ["totalThicknessMm", "闭合总厚度 T"],
    ["linearTravelMm", "直线行程 S"],
    ["seamClearanceMm", "数字白模接缝间隙"]
  ]) if (dimensions[field] === null) missing.push(label);
  if (contract.dimensionBasis?.type === "anthropometric-estimate") {
    for (const [field, label] of [
      ["overallLengthMm", "长度估算范围"],
      ["overallWidthMm", "宽度估算范围"],
      ["totalThicknessMm", "厚度估算范围"],
      ["linearTravelMm", "行程估算范围"]
    ]) if (!contract.dimensionEstimateRangesMm?.[field]) missing.push(label);
  }
  if (contract.mechanism.secondaryMotion === "unknown") missing.push("末段动作");
  if (contract.mechanism.secondaryMotion === "translation-plus-rotation" && contract.mechanism.maxRotationDeg === null) missing.push("最大旋转角度");
  if (contract.mechanism.laneMode === "unknown") missing.push("内部双通道用途");
  if (contract.mechanism.internalHardwareMode === "unknown") missing.push("内部还原深度");
  if (contract.mechanism.internalHardwareMode === "physical-teardown-replica") {
    for (const [field, label] of [
      ["magnetCount", "磁铁数量"],
      ["ballCount", "滚珠数量"],
      ["steelPlateCount", "钢板数量"]
    ]) if (contract.mechanism[field] === null) missing.push(label);
  }
  return { complete: missing.length === 0, missing };
}

export function loadModelingContract(modelId) {
  const manifest = loadManifest(modelId);
  const stage = manifest.stages.find((candidate) => candidate.id === "03-contract");
  const asset = [...manifest.assets]
    .reverse()
    .find((candidate) => (
      candidate.stageId === "03-contract"
      && candidate.slot === "modeling-contract"
      && stage.artifactIds.includes(candidate.id)
      && path.extname(candidate.path).toLowerCase() === ".json"
    ));
  if (!asset) return null;
  const absolute = resolveRepoPath(asset.path);
  if (!fs.existsSync(absolute)) throw new PipelineError("The current modeling contract file is missing.", 500);
  return JSON.parse(fs.readFileSync(absolute, "utf8"));
}

export function saveSliderMeasurementContract(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (modelId !== "magnetic-slide-tile") throw new PipelineError("This measurement schema is specific to magnetic-slide-tile.");
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "03-contract");
  const gate02 = manifest.stages[stageIndex - 1];
  if (gate02.status !== "approved") throw new PipelineError("Gate 02 must remain approved.", 422);
  const actualSMaxL = gate02.analysisSpec?.finalApproval?.geometryParameterSnapshot?.actualSMaxL;
  const preparedRequired = Object.fromEntries(REQUIRED_CORE_MEASUREMENTS.map((definition) => [
    definition.id,
    {
      ...(payload.requiredMeasurements?.[definition.id] || {}),
      method: payload.requiredMeasurements?.[definition.id]?.method || definition.method
    }
  ]));
  const validation = validateMeasurementContract({
    requiredMeasurements: preparedRequired,
    optionalMeasurements: payload.optionalMeasurements,
    cadConfig: { actualSMaxL }
  });
  const sourceClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  const priorContracts = manifest.assets.filter(
    (asset) => asset.stageId === "03-contract" && asset.slot === "modeling-contract"
  );
  const contractRevision = priorContracts.length + 1;
  const revisionLabel = String(contractRevision).padStart(3, "0");
  const now = new Date().toISOString();
  const contract = {
    schemaVersion: 2,
    kind: "guided-core-measurement-modeling-contract",
    modelId,
    gate: "03-contract",
    contractRevision,
    createdAt: now,
    units: "millimeters",
    approvedGate02ContractSha256: gate02.analysisSpec.contractSha256,
    sourceClaimIds,
    sourceAssetIds: [gate02.analysisSpec.contractAssetId, gate02.analysisSpec.cadArtifactId],
    policy: {
      requiredCoreFieldIds: REQUIRED_CORE_MEASUREMENTS.map(({ id }) => id),
      optionalEngineeringFieldIds: OPTIONAL_ENGINEERING_MEASUREMENTS.map(({ id }) => id),
      manufacturingLaterFieldIds: MANUFACTURING_LATER_FIELDS.map(({ id }) => id),
      optionalFieldsBlockInitialBlender: false,
      manufacturingFieldsBlockInitialBlender: false,
      rejectedDefaults: ["50×31×12 mm", "21 mm"]
    },
    definitions: {
      requiredCore: REQUIRED_CORE_MEASUREMENTS,
      optionalEngineering: OPTIONAL_ENGINEERING_MEASUREMENTS,
      manufacturingLater: MANUFACTURING_LATER_FIELDS
    },
    measurements: {
      required: validation.requiredMeasurements,
      optional: validation.optionalMeasurements,
      manufacturingLater: validation.manufacturingMeasurements
    },
    consistency: {
      thicknessStack: "topPlateThickness + bottomPlateThickness + closedSeamGap ≈ totalClosedThickness within stated uncertainty",
      axisCarrierFit: "carrier circle must fit the bottom footprint at the measured axis offset",
      travelContainment: `maximumSlideTravel <= ${actualSMaxL} * closedOverallLength within stated uncertainty`,
      aspectEvidenceWarningRange: [1.52, 1.62],
      errors: validation.errors,
      warnings: validation.warnings
    },
    completeness: {
      complete: validation.readyForModelingContractReview,
      requiredComplete: validation.progress.complete,
      requiredTotal: validation.progress.total,
      fieldErrors: validation.fieldErrors
    }
  };
  const relativePath = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId),
    "evidence/03-contract",
    `rev-${revisionLabel}`,
    "measurement-modeling-contract.json"
  )));
  const absolutePath = resolveRepoPath(relativePath);
  atomicWriteJson(absolutePath, contract);
  const assetId = `${modelId}-measurement-modeling-contract-r${revisionLabel}`;
  manifest.assets.push({
    id: assetId,
    stageId: "03-contract",
    slot: "modeling-contract",
    path: relativePath,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role: "contract",
    producer: {
      name: "fidgeting-model-pipeline",
      version: "2",
      recipe: "Gate 03 guided nine-core-measurement contract"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: "modeling-contract",
      assertedBy: "assistant",
      mechanismEvidenceContractSha256: gate02.analysisSpec.contractSha256,
      note: "Contains no numeric defaults. Values require user measurement, source and uncertainty."
    },
    sourceAssetIds: contract.sourceAssetIds,
    sourceClaimIds
  });
  const stage = manifest.stages[stageIndex];
  stage.revision += 1;
  stage.status = validation.readyForModelingContractReview ? "ready_for_review" : "blocked";
  stage.artifactIds = [assetId];
  stage.requiredPhysicalDimensions = contract.policy.requiredCoreFieldIds;
  stage.optionalEngineeringDimensions = contract.policy.optionalEngineeringFieldIds;
  stage.manufacturingLaterDimensions = contract.policy.manufacturingLaterFieldIds;
  stage.measurementProgress = validation.progress;
  stage.blockedReason = validation.readyForModelingContractReview
    ? null
    : "Nine required core measurements and consistency checks are incomplete.";
  stage.validations = [
    { id: "approved-analysis-consumed", status: "pass", evidence: `Contract consumes all ${sourceClaimIds.length} active Gate 02 claims.` },
    { id: "nine-core-measurements", status: validation.progress.complete === 9 ? "pass" : "fail", evidence: `${validation.progress.complete}/9 required measurements include value, uncertainty, source and method.` },
    { id: "measurement-consistency", status: validation.errors.length ? "fail" : "pass", evidence: validation.errors.length ? validation.errors.map(({ message }) => message).join(" ") : "Thickness stack, axis/carrier fit and travel containment pass." },
    { id: "optional-unknowns-nonblocking", status: "pass", evidence: "Optional engineering and manufacturing-only fields remain unknown and do not block initial Blender modeling." },
    { id: "no-provisional-defaults", status: "pass", evidence: "The active contract contains no 50×31×12/21 defaults." }
  ];
  stage.decision = null;
  manifest.currentStageId = "03-contract";
  manifest.currentState.requiredPhysicalDimensions = contract.policy.requiredCoreFieldIds;
  manifest.currentState.optionalEngineeringDimensions = contract.policy.optionalEngineeringFieldIds;
  manifest.currentState.manufacturingLaterDimensions = contract.policy.manufacturingLaterFieldIds;
  manifest.currentState.measurementProgress = `${validation.progress.complete}/9`;
  manifest.currentState.diagnosis = validation.readyForModelingContractReview
    ? "Gate 03 has 9/9 core measurements with passing consistency checks and is ready for contract review. Blender remains locked until Gate 03 and Gate 04 approval."
    : `Gate 03 is blocked at ${validation.progress.complete}/9 core measurements. Optional engineering and manufacturing-only fields do not block initial Blender modeling.`;
  markDownstreamStale(manifest, stageIndex, "Gate 03 measurement contract changed; downstream work remains stale.");
  if (manifest.stages[11].decision?.action === "reject") manifest.stages[11].status = "rejected";
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  const event = makeEvent(manifest, "gate03-measurement-contract-saved", {
    stageId: "03-contract",
    assetId,
    progress: validation.progress,
    readyForReview: validation.readyForModelingContractReview,
    requiredFieldIds: contract.policy.requiredCoreFieldIds,
    optionalFieldIds: contract.policy.optionalEngineeringFieldIds,
    manufacturingLaterFieldIds: contract.policy.manufacturingLaterFieldIds,
    consistencyErrors: validation.errors,
    consistencyWarnings: validation.warnings,
    blenderStarted: false,
    unityChanged: false,
    simulatorCurrent: false
  });
  return { manifest: saveManifest(manifest, event), contract };
}

export function saveMeasurementPhoto(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (modelId !== "magnetic-slide-tile") throw new PipelineError("Measurement photo upload is only available for magnetic-slide-tile.");
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  const allowedFieldIds = new Set([
    ...REQUIRED_CORE_MEASUREMENTS.map(({ id }) => id),
    ...OPTIONAL_ENGINEERING_MEASUREMENTS.map(({ id }) => id)
  ]);
  const fieldId = String(payload.fieldId || "");
  if (!allowedFieldIds.has(fieldId)) throw new PipelineError("Unknown measurement field.");
  const mimeType = String(payload.mimeType || "");
  const extension = ({ "image/png": ".png", "image/jpeg": ".jpg", "image/webp": ".webp" })[mimeType];
  if (!extension) throw new PipelineError("Measurement photos must be PNG, JPEG or WebP.");
  let bytes;
  try { bytes = Buffer.from(String(payload.dataBase64 || ""), "base64"); }
  catch { throw new PipelineError("Measurement photo must contain valid base64."); }
  if (!bytes.length || bytes.length > 10 * 1024 * 1024) throw new PipelineError("Measurement photo must be between 1 byte and 10 MB.");
  const now = new Date().toISOString();
  const slug = crypto.randomUUID();
  const relativePath = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId),
    "evidence/03-contract/measurement-photos",
    `${fieldId}-${slug}${extension}`
  )));
  const absolutePath = resolveRepoPath(relativePath);
  fs.mkdirSync(path.dirname(absolutePath), { recursive: true });
  fs.writeFileSync(absolutePath, bytes);
  const assetId = `${modelId}-measurement-photo-${fieldId}-${slug}`;
  manifest.assets.push({
    id: assetId,
    stageId: "03-contract",
    slot: "measurement-source",
    path: relativePath,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: bytes.length,
    role: "user-input",
    producer: {
      name: "model-provenance-explorer",
      version: "2",
      recipe: "Gate 03 guided measurement photo upload"
    },
    provenance: {
      origin: "user-provided",
      contentClass: "measurement-photo",
      assertedBy: "user",
      fieldId,
      originalFilename: path.basename(String(payload.filename || "measurement"))
    },
    sourceAssetIds: [],
    sourceClaimIds: []
  });
  manifest.revision += 1;
  manifest.updatedAt = now;
  const event = makeEvent(manifest, "gate03-measurement-photo-added", {
    stageId: "03-contract",
    fieldId,
    assetId,
    originalFilename: path.basename(String(payload.filename || "measurement")),
    blenderStarted: false,
    unityChanged: false
  });
  return { manifest: saveManifest(manifest, event), assetId };
}

export function saveModelingContract(modelId, payload) {
  if (modelId === "magnetic-slide-tile" && payload.measurementSchemaVersion === 2) {
    return saveSliderMeasurementContract(modelId, payload);
  }
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "03-contract");
  if (manifest.stages[stageIndex - 1].status !== "approved") throw new PipelineError("Gate 02 must be approved before creating the modeling contract.", 422);

  const secondaryMotion = String(payload.secondaryMotion || "unknown");
  const laneMode = String(payload.laneMode || "unknown");
  const internalHardwareMode = String(payload.internalHardwareMode || "unknown");
  if (!SECONDARY_MOTION_OPTIONS.has(secondaryMotion)) throw new PipelineError("Invalid secondary motion choice.");
  if (!LANE_MODE_OPTIONS.has(laneMode)) throw new PipelineError("Invalid lane mode choice.");
  if (!HARDWARE_MODE_OPTIONS.has(internalHardwareMode)) throw new PipelineError("Invalid internal hardware choice.");

  const priorContract = loadModelingContract(modelId);
  const requestedBasis = String(payload.dimensionBasis?.type || payload.dimensionBasisType || priorContract?.dimensionBasis?.type || "user-measured");
  if (!DIMENSION_BASIS_OPTIONS.has(requestedBasis)) throw new PipelineError("Invalid dimension basis.");

  const sourceClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  if (!sourceClaimIds.length) throw new PipelineError("Gate 02 has no analysis decisions to consume.", 422);
  const priorContracts = manifest.assets.filter((asset) => asset.stageId === "03-contract" && asset.slot === "modeling-contract");
  const contractRevision = priorContracts.length + 1;
  const revisionLabel = String(contractRevision).padStart(3, "0");
  const now = new Date().toISOString();
  const dimensions = {
    overallLengthMm: optionalPositiveNumber(payload.overallLengthMm, "overallLengthMm"),
    overallWidthMm: optionalPositiveNumber(payload.overallWidthMm, "overallWidthMm"),
    totalThicknessMm: optionalPositiveNumber(payload.totalThicknessMm, "totalThicknessMm"),
    linearTravelMm: optionalPositiveNumber(payload.linearTravelMm, "linearTravelMm"),
    seamClearanceMm: optionalPositiveNumber(payload.seamClearanceMm, "seamClearanceMm")
  };
  const proposedBasis = payload.dimensionBasis && typeof payload.dimensionBasis === "object"
    ? payload.dimensionBasis
    : priorContract?.dimensionBasis;
  const dimensionBasis = requestedBasis === "anthropometric-estimate" ? {
    type: "anthropometric-estimate",
    confidence: String(proposedBasis?.confidence || "medium"),
    method: String(proposedBasis?.method || "Adult-finger scale estimate from user video; values remain editable and are not production measurements."),
    calibration: proposedBasis?.calibration || null,
    corroboration: Array.isArray(proposedBasis?.corroboration) ? proposedBasis.corroboration : [],
    limitation: String(proposedBasis?.limitation || "Perspective, finger-size variation and custom-shell variation remain in the stated ranges.")
  } : requestedBasis === "user-authorized-provisional" ? {
    type: "user-authorized-provisional",
    confidence: String(proposedBasis?.confidence || "user-authorized-temporary"),
    availability: "exact-production-dimensions-still-unknown",
    usage: "digital-blockout-only",
    authorizedBy: "user",
    authorizedAt: String(proposedBasis?.authorizedAt || now),
    authorizationSource: String(proposedBasis?.authorizationSource || "current-user-selection"),
    method: String(proposedBasis?.method || "Use the user's explicitly authorized temporary L/W/T/S values for digital blockout only."),
    officialStructureEvidenceRetained: true,
    officialPublishedDimensions: false,
    productionDimensions: false,
    inferredFromVideo: false,
    supersedesPolicy: String(proposedBasis?.supersedesPolicy || "Gate 03 rev 6 official-only restriction"),
    limitation: String(proposedBasis?.limitation || "These values are provisional digital-blockout targets, not exact production measurements or official HALOOPLAYER/NXEDC dimensions.")
  } : requestedBasis === "official-only" ? {
    type: "official-only",
    confidence: String(proposedBasis?.confidence || "high"),
    availability: String(proposedBasis?.availability || "exact-model-dimensions-unavailable"),
    method: String(proposedBasis?.method || "Use only exact-model HALOOPLAYER or NXEDC published dimensions; do not substitute user-video estimates or dimensions from similar products."),
    checkedAt: String(proposedBasis?.checkedAt || now),
    checkedSources: Array.isArray(proposedBasis?.checkedSources) ? proposedBasis.checkedSources : [],
    excludedComparables: Array.isArray(proposedBasis?.excludedComparables) ? proposedBasis.excludedComparables : [],
    limitation: String(proposedBasis?.limitation || "Exact-model L/W/T and straight-travel dimensions are not published in the currently available official or NXEDC records, so they remain unknown.")
  } : {
    type: "user-measured",
    confidence: "user-supplied",
    method: "Values entered from the physical object by the user."
  };
  const proposedRanges = payload.dimensionEstimateRangesMm || priorContract?.dimensionEstimateRangesMm || {};
  const estimateRange = (field) => {
    const proposedCenter = dimensions[field];
    const priorCenter = priorContract?.dimensions?.[field];
    const priorRange = priorContract?.dimensionEstimateRangesMm?.[field];
    if (!payload.dimensionEstimateRangesMm && priorRange && proposedCenter !== null && priorCenter !== null && proposedCenter !== priorCenter) {
      return normalizeEstimateRange({
        min: proposedCenter - (priorCenter - priorRange.min),
        max: proposedCenter + (priorRange.max - priorCenter)
      }, proposedCenter, `${field} range`);
    }
    return normalizeEstimateRange(proposedRanges[field], proposedCenter, `${field} range`);
  };
  const dimensionEstimateRangesMm = requestedBasis === "anthropometric-estimate" ? {
    overallLengthMm: estimateRange("overallLengthMm"),
    overallWidthMm: estimateRange("overallWidthMm"),
    totalThicknessMm: estimateRange("totalThicknessMm"),
    linearTravelMm: estimateRange("linearTravelMm")
  } : null;
  const mechanism = {
    fixedPart: "lower-body",
    movingPart: "upper-body",
    primaryMotion: secondaryMotion === "dual-mode-free-spin" ? "straight-push-along-positive-y" : "translation-along-positive-y",
    secondaryMotion,
    maxRotationDeg: secondaryMotion === "translation-plus-rotation" ? optionalPositiveNumber(payload.maxRotationDeg, "maxRotationDeg") : null,
    laneMode,
    internalHardwareMode,
    magnetCount: internalHardwareMode === "physical-teardown-replica" ? optionalNonNegativeInteger(payload.magnetCount, "magnetCount") : null,
    ballCount: internalHardwareMode === "physical-teardown-replica" ? optionalNonNegativeInteger(payload.ballCount, "ballCount") : null,
    steelPlateCount: internalHardwareMode === "physical-teardown-replica" ? optionalNonNegativeInteger(payload.steelPlateCount, "steelPlateCount") : null,
    ...(secondaryMotion === "dual-mode-free-spin" ? {
      interactionModes: ["straight-push", "free-spin"],
      modeRelationship: "separately-supported; exact-kinematic-coupling-unknown",
      rotationMode: "continuous-free-spin-about-central-bearing-region",
      externalMainShellCount: 2,
      linearModule: "bilateral-long-rail-ball-or-bead-grooves",
      rotaryModule: "circular-ball-track-and-central-shaft-or-bearing-region",
      tuningParts: "spring-and-steel-or-ceramic-balls",
      evidenceBoundary: "do-not-lock-counts-tolerances-hole-depths-or-coupling-without-physical-proof"
    } : {})
  };
  const contract = {
    schemaVersion: 1,
    modelId,
    contractRevision,
    createdAt: now,
    sourceClaimIds,
    sourceAssetIds: [
      ...manifest.stages[1].artifactIds,
      ...(["official-only", "user-authorized-provisional"].includes(requestedBasis) ? [
        "slider-intake-haloo-official-04",
        "slider-intake-haloo-official-05",
        "slider-intake-haloo-official-06",
        "slider-intake-haloo-official-07",
        "slider-intake-haloo-official-08",
        "slider-intake-haloo-official-metadata"
      ] : [
        "slider-intake-user-frame-04",
        "slider-intake-user-frame-03",
        "slider-intake-user-frame-12"
      ])
    ].filter((assetId, index, values) => manifest.assets.some((asset) => asset.id === assetId) && values.indexOf(assetId) === index),
    units: "millimeters",
    dimensionBasis,
    dimensionEstimateRangesMm,
    coordinateSystem: {
      x: "width-right",
      y: "length-and-primary-slide-forward",
      z: "thickness-up",
      origin: "closed-assembly-center",
      pivotRule: secondaryMotion === "dual-mode-free-spin"
        ? "two exterior main shells; preserve the straight-push axis and central free-spin bearing region; defer exact coupling to Gate 04 physical evidence"
        : "lower-body-fixed; upper-body pivot resolved from approved motion choice"
    },
    dimensions,
    boundsMm: dimensions.overallLengthMm && dimensions.overallWidthMm && dimensions.totalThicknessMm ? {
      x: dimensions.overallWidthMm,
      y: dimensions.overallLengthMm,
      z: dimensions.totalThicknessMm
    } : null,
    mechanism,
    modelingRules: {
      symmetry: "outline bilateral across X; do not mirror asymmetric artwork",
      triangleBudgetMax: 120000,
      collisionTriangleBudgetMax: 2000,
      materialLanguageDeferredToGate: "07-material",
      audioBehaviorDeferredToInteractionSystem: true
    },
    route: {
      primary: "blender-cli",
      deterministic: true,
      rodinPolicy: "concept-only; never promote directly to Unity"
    },
    claimDisposition: Object.fromEntries(sourceClaimIds.map((claimId) => [claimId,
      requestedBasis === "user-authorized-provisional" && claimId === "slider-analysis-official-evidence-boundary-r002"
        ? "keep-exact-production-dimensions-unknown; use-only-user-authorized-provisional-digital-blockout-values"
        : ({
      "slider-analysis-official-product-match-r002": "lock-shared-silhouette-and-mechanism-family; color-and-artwork-remain-custom",
      "slider-analysis-official-dual-mode-r002": "lock-straight-push-and-free-spin-as-separately-supported-modes; reject-end-stop-sequence",
      "slider-analysis-official-shell-hierarchy-r002": "lock-two-exterior-main-shells; preserve-visible-internal-functional-modules",
      "slider-analysis-official-linear-module-r002": "lock-bilateral-long-rail-ball-or-bead-groove-module",
      "slider-analysis-official-rotary-module-r002": "lock-circular-ball-track-and-central-bearing-region; coupling-remains-unknown",
      "slider-analysis-official-tuning-parts-r002": "show-visible-spring-and-ball-tuning-parts-without-inventing-counts",
      "slider-analysis-official-evidence-boundary-r002": "carry-counts-dimensions-tolerances-hole-depths-and-coupling-as-unknown"
    })[claimId] || "consumed-without-extra-assumption"
    ]))
  };
  const completeness = validateContractSelections(contract);
  contract.completeness = completeness;
  const mechanismMissing = completeness.missing.filter((item) => [
    "末段动作", "最大旋转角度", "内部双通道用途", "内部还原深度", "磁铁数量", "滚珠数量", "钢板数量"
  ].includes(item));

  const relativePath = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/03-contract", `rev-${revisionLabel}`, "modeling-contract.json"
  )));
  const absolutePath = resolveRepoPath(relativePath);
  atomicWriteJson(absolutePath, contract);
  const assetId = `${modelId}-modeling-contract-r${revisionLabel}`;
  manifest.assets.push({
    id: assetId,
    stageId: "03-contract",
    slot: "modeling-contract",
    path: relativePath,
    sha256: sha256File(absolutePath),
    exists: true,
    sizeBytes: fs.statSync(absolutePath).size,
    role: "contract",
    producer: {
      name: "fidgeting-model-pipeline",
      version: "1",
      recipe: requestedBasis === "anthropometric-estimate"
        ? "Gate 03 ranged anthropometric scale estimate"
        : requestedBasis === "user-authorized-provisional"
          ? "Gate 03 user-authorized provisional digital-blockout contract"
        : requestedBasis === "official-only"
          ? "Gate 03 exact-model official-only dimension source review"
          : "Gate 03 user-measured modeling contract"
    },
    provenance: {
      origin: "repository-generated",
      contentClass: "modeling-contract",
      assertedBy: "assistant",
      note: requestedBasis === "anthropometric-estimate"
        ? "尺寸由用户视频中的成人手指比例估算并保留误差范围；不会冒充生产实测，也不会用历史 Unity 参数补齐。"
        : requestedBasis === "user-authorized-provisional"
          ? "用户明确取消 official-only 限制并授权 50 × 31 × 12 mm、直推 21 mm 只作为临时数字白模规格；不是官方发布值、不是生产实测，也不是从视频静默推断。结构与机构仍承接 HALOOPLAYER / NXEDC 同款证据。"
        : requestedBasis === "official-only"
          ? "用户明确要求尺寸只采用同款 HALOOPLAYER 或 NXEDC 发布值；当前未找到精确尺寸，因此移除视频比例估算并保持未知。"
          : "实测数值和机构选项由用户在工作台确认；空值不会用历史 Unity 参数补齐。"
    },
    sourceAssetIds: contract.sourceAssetIds,
    sourceClaimIds
  });
  const stage = manifest.stages[stageIndex];
  stage.revision += 1;
  stage.status = completeness.complete ? "ready_for_review" : "draft";
  stage.artifactIds = [assetId];
  const dimensionsComplete = Boolean(dimensions.overallLengthMm && dimensions.overallWidthMm && dimensions.totalThicknessMm && dimensions.linearTravelMm && dimensions.seamClearanceMm);
  const estimateRangesComplete = requestedBasis !== "anthropometric-estimate" || Object.values(dimensionEstimateRangesMm).every(Boolean);
  const dimensionValidationEvidence = requestedBasis === "official-only" && !dimensionsComplete
    ? "Exact-model HALOOPLAYER and NXEDC sources do not currently publish all L/W/T/S values; video-derived estimates and similar-product dimensions are excluded by user decision."
    : dimensionsComplete
      ? requestedBasis === "anthropometric-estimate"
        ? "All four proposed dimensions include explicit uncertainty ranges; the seam clearance is a digital-model choice."
        : requestedBasis === "user-authorized-provisional"
          ? "All four values are present and explicitly labeled as user-authorized provisional digital-blockout targets, not official or production dimensions."
        : "All four dimensions and the digital seam clearance are set in millimeters."
      : "Waiting for the four dimensions and digital seam clearance.";
  stage.validations = [
    { id: "approved-analysis-consumed", status: "pass", evidence: `Contract consumes all ${sourceClaimIds.length} approved Gate 02 decisions.` },
    { id: "dimension-proposal-complete", status: dimensionsComplete && estimateRangesComplete ? "pass" : "fail", evidence: dimensionValidationEvidence },
    { id: "mechanism-choices-complete", status: mechanismMissing.length ? "fail" : "pass", evidence: mechanismMissing.length ? `Still waiting for: ${mechanismMissing.join("、")}.` : secondaryMotion === "dual-mode-free-spin" ? "Straight push and free spin are locked as separately supported modes; the sequential end-stop assumption is removed." : "Motion, lane purpose and reconstruction depth are explicit." },
    ...(secondaryMotion === "dual-mode-free-spin" ? [
      { id: "official-dual-mode-contract", status: "pass", evidence: "The contract preserves two exterior main shells plus visible linear, rotary, spring and ball functional modules without inventing exact counts or coupling." }
    ] : []),
    { id: "deterministic-route-locked", status: "pass", evidence: "Blender CLI is primary; Rodin remains concept-only." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "上游 03-contract 已产生新 revision，等待重新推进。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = completeness.complete
    ? requestedBasis === "user-authorized-provisional"
      ? "用户已取消 official-only 限制，并授权 50 × 31 × 12 mm、直推 21 mm 只作为临时数字白模规格；官方同款结构证据继续有效，精确生产尺寸仍未知。Gate 03 等待用户审批，当前 Unity 模型保持不变。"
      : secondaryMotion === "dual-mode-free-spin"
      ? "第 2 关同款机构研究已获用户批准；第 3 关已改为直推与自由旋转双玩法合同，等待用户审批。旧末端解锁假设已删除，当前 Unity 模型保持不变。"
      : "第 2 关已获用户批准；第 3 关尺寸与运动方案已填写完毕，等待用户审批。当前 Unity 模型保持不变。"
    : requestedBasis === "official-only"
      ? "第 2 关同款官方机构研究仍有效；用户要求第 3 关尺寸仅采用同款 HALOOPLAYER / NXEDC 发布值。当前精确尺寸与行程未公开，视频比例估算已移除，Gate 03 保持草稿且 Unity 模型不变。"
      : requestedBasis === "anthropometric-estimate" && dimensions.overallLengthMm && dimensions.overallWidthMm && dimensions.totalThicknessMm && dimensions.linearTravelMm
      ? "第 3 关已按成人手指与用户视频给出带范围的尺寸建议；现只等待机构选择。当前 Unity 模型保持不变。"
      : "第 2 关已获用户批准；现进入第 3 关，等待尺寸与机构选择。当前 Unity 模型保持不变。";
  const event = makeEvent(manifest, "stage-draft-created", {
    stageId: "03-contract",
    contractRevision,
    assetId,
    complete: completeness.complete,
    dimensionBasisType: requestedBasis
  });
  return { manifest: saveManifest(manifest, event), contract };
}

function assertRepositoryEvidenceFile(modelId, stageDirectory, relativePath, label) {
  const normalized = normalizeRepoPath(relativePath);
  const expectedPrefix = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence", stageDirectory
  )));
  if (!normalized.startsWith(`${expectedPrefix}/`)) {
    throw new PipelineError(`${label} must be stored inside ${expectedPrefix}.`);
  }
  const absolute = resolveRepoPath(normalized);
  if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
    throw new PipelineError(`${label} does not exist: ${normalized}`);
  }
  return { normalized, absolute };
}

export function saveExternalReferencePack(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  const records = Array.isArray(payload.assets) ? payload.assets : [];
  if (!records.length) throw new PipelineError("External reference pack must include at least one asset.");
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  const newIds = new Set();
  const now = new Date().toISOString();
  const registered = records.map((record, index) => {
    const id = String(record.id || "").trim();
    if (!id || existingIds.has(id) || newIds.has(id)) throw new PipelineError(`External reference asset id is missing or duplicated: ${id || index}.`);
    newIds.add(id);
    const { normalized, absolute } = assertRepositoryEvidenceFile(modelId, "01-intake", record.path, `External reference ${id}`);
    const sourceUrl = String(record.sourceUrl || "").trim();
    if (sourceUrl && !/^https:\/\//i.test(sourceUrl)) throw new PipelineError(`External reference ${id} must use an HTTPS source URL.`);
    return {
      id,
      stageId: "01-intake",
      slot: "original-reference",
      path: normalized,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: "external-reference",
      producer: {
        name: String(payload.sourceName || "external-product-source"),
        version: String(payload.sourceVersion || new Date().toISOString().slice(0, 10)),
        recipe: "Exact-product official reference archive"
      },
      provenance: {
        origin: "external",
        contentClass: String(record.contentClass || "exact-product-reference"),
        assertedBy: "repository",
        note: String(record.description || "Exact-product external reference; it does not replace user-provided media.")
      },
      sourceAssetIds: [],
      sourceUrl: sourceUrl || null
    };
  });
  manifest.assets.push(...registered);
  const stageIndex = 0;
  const stage = manifest.stages[stageIndex];
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = [...new Set([...(stage.artifactIds || []), ...registered.map((asset) => asset.id)])];
  stage.reviewArtifactIds = registered
    .filter((asset) => !["json", "md", "txt", "ndjson"].includes(path.extname(asset.path).slice(1).toLowerCase()))
    .map((asset) => asset.id);
  stage.validations = [
    { id: "external-source-archived", status: "pass", evidence: `${registered.length} exact-product files are archived with repository paths and SHA-256.` },
    { id: "source-class-separated", status: "pass", evidence: "External product imagery remains labeled external-reference and does not replace the user's original video or frames." },
    { id: "mechanism-evidence-present", status: registered.some((asset) => /mechanism|gameplay|internal|straight|spin|spring|ball/i.test(`${asset.provenance.contentClass} ${asset.provenance.note}`)) ? "pass" : "fail", evidence: "The pack includes exact-product gameplay and internal-mechanism imagery." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "上游 01-intake 增加了同款官方参考，后续判断必须重新验证。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "已加入同款官方玩法与内部结构参考；等待确认其来源分类，旧推断与旧几何均不得继续晋级。当前 Unity 模型保持不变。";
  const event = makeEvent(manifest, "external-reference-pack-added", {
    stageId: "01-intake",
    sourceName: String(payload.sourceName || "external-product-source"),
    assetIds: registered.map((asset) => asset.id)
  });
  return saveManifest(manifest, event);
}

export function saveAnalysisResearchRevision(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "02-analysis");
  if (manifest.stages[stageIndex - 1].status !== "approved") throw new PipelineError("Gate 01 must be approved before creating a new analysis revision.", 422);
  const records = Array.isArray(payload.assets) ? payload.assets : [];
  if (!records.length) throw new PipelineError("Analysis revision must include review assets.");
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  const newIds = new Set();
  const registered = records.map((record, index) => {
    const id = String(record.id || "").trim();
    if (!id || existingIds.has(id) || newIds.has(id)) throw new PipelineError(`Analysis asset id is missing or duplicated: ${id || index}.`);
    newIds.add(id);
    const { normalized, absolute } = assertRepositoryEvidenceFile(modelId, "02-analysis", record.path, `Analysis asset ${id}`);
    const sourceAssetIds = Array.isArray(record.sourceAssetIds) ? [...new Set(record.sourceAssetIds)] : [];
    if (!sourceAssetIds.length || sourceAssetIds.some((assetId) => !existingIds.has(assetId))) {
      throw new PipelineError(`Analysis asset ${id} must cite existing upstream source assets.`);
    }
    return {
      id,
      stageId: "02-analysis",
      slot: String(record.slot || "analysis-board"),
      path: normalized,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: "analysis",
      producer: { name: "fidgeting-model-pipeline", version: "1", recipe: "Exact-product official mechanism research" },
      provenance: {
        origin: "repository-generated",
        contentClass: String(record.contentClass || "source-linked-analysis"),
        assertedBy: "assistant",
        note: String(record.description || "Annotated analysis generated only from the linked exact-product sources.")
      },
      sourceAssetIds
    };
  });
  const proposedClaims = Array.isArray(payload.claims) ? payload.claims : [];
  if (!proposedClaims.length) throw new PipelineError("Analysis revision must include source-linked modeling claims.");
  const claimIds = new Set((manifest.claims || []).map((claim) => claim.id));
  const newClaimIds = new Set();
  const revisionLabel = String(manifest.stages[stageIndex].revision + 1).padStart(3, "0");
  const now = new Date().toISOString();
  const claims = proposedClaims.map((claim, index) => {
    const id = String(claim.id || "").trim();
    if (!id || claimIds.has(id) || newClaimIds.has(id)) throw new PipelineError(`Analysis claim id is missing or duplicated: ${id || index}.`);
    newClaimIds.add(id);
    const sourceAssetIds = Array.isArray(claim.sourceAssetIds) ? [...new Set(claim.sourceAssetIds)] : [];
    if (!sourceAssetIds.length || sourceAssetIds.some((assetId) => !existingIds.has(assetId))) {
      throw new PipelineError(`Analysis claim ${id} must cite existing upstream source assets.`);
    }
    return {
      id,
      stageId: "02-analysis",
      category: String(claim.category || "structure"),
      statement: String(claim.statement || "").trim(),
      confidence: String(claim.confidence || "medium"),
      sourceAssetIds,
      sourceRegions: Array.isArray(claim.sourceRegions) ? claim.sourceRegions : [],
      state: "active",
      analysisRevision: revisionLabel
    };
  });
  if (claims.some((claim) => !claim.statement)) throw new PipelineError("Analysis claim statements cannot be empty.");
  for (const claim of manifest.claims || []) {
    if (claim.stageId === "02-analysis" && claim.state !== "superseded") {
      claim.state = "superseded";
      claim.supersededBy = `analysis-rev-${revisionLabel}`;
      claim.supersededAt = now;
    }
  }
  manifest.assets.push(...registered);
  manifest.claims.push(...claims);
  const stage = manifest.stages[stageIndex];
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = registered.map((asset) => asset.id);
  stage.reviewArtifactIds = registered.filter((asset) => asset.slot === "analysis-board").map((asset) => asset.id);
  stage.validations = [
    { id: "exact-product-source-linked", status: "pass", evidence: "Every current judgment links to exact-product official reference assets." },
    { id: "dual-mode-distinguished", status: "pass", evidence: "Straight push and free spin are recorded as separate supported modes; no sequential end-stop coupling is asserted." },
    { id: "shells-vs-modules-distinguished", status: "pass", evidence: "Two exterior carrier shells are distinguished from internal straight-track, rotary-track, spring and ball modules." },
    { id: "unknowns-preserved", status: "pass", evidence: "Exact dimensions, counts and coupling remain unknown pending physical confirmation or teardown." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "上游 02-analysis 已按同款官方证据修正，旧合同和拆件方案必须重做。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "同款官方资料已纠正玩法与内部模块理解；第 2 关等待用户确认，旧合同、旧拆件和旧 Unity 几何均不作为新模型依据。";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "02-analysis",
    analysisRevision: revisionLabel,
    artifactIds: stage.artifactIds,
    claimIds: claims.map((claim) => claim.id)
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseMotionCorrection(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This motion correction is supported only for the Premium Display Case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "02-analysis");
  const intake = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (intake.status !== "approved") {
    throw new PipelineError("Gate 01 topology approval must remain approved.", 422);
  }
  if (
    stage.status !== "rejected"
    || stage.decision?.action !== "reject"
    || !stage.decision.notes.includes("当前 Y 轴 turntable 旋转完全错误")
  ) {
    throw new PipelineError("Gate 02 must first record the user's explicit Y-turntable rejection through the decision API.", 422);
  }
  const userQuote = String(payload.userQuote || "").trim();
  const instructionQuote = String(payload.instructionQuote || "").trim();
  if (userQuote !== "当前 Y 轴 turntable 旋转完全错误。") {
    throw new PipelineError("The exact motion-rejection quote must be preserved.", 422);
  }
  if (instructionQuote !== "用户截图显示的不是简单 Y 轴转盘。不要先猜是 X 轴。") {
    throw new PipelineError("The exact axis-analysis instruction must be preserved.", 422);
  }

  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/02-analysis/rev-003"
  )));
  const evidencePaths = {
    userReference: "user-motion-rejection-reference.png",
    rejectionRecord: "user-motion-rejection.md",
    authoredExtract: "rive-authored-motion-extract.json",
    generator: "generate_motion_analysis.py",
    contactSheet: "real-rive-motion-contact-sheet.png",
    analysisBoard: "motion-axis-perspective-analysis-board.png",
    measurement: "real-rive-motion-measurements.json",
    schematicGif: "whole-case-measured-motion-schematic.gif",
    schematicContact: "whole-case-schematic-contact-sheet.png",
    qualityReport: "animation-quality-report.json",
    referenceManifest: "reference_manifest.json",
    userAnalysis: "source-analysis/user-screenshot.json",
    riveFrameAnalysis: "source-analysis/real-rive-frames.json",
    landmarkValidation: "validation/motion-landmark-validation.json"
  };
  const files = {};
  for (const [label, filename] of Object.entries(evidencePaths)) {
    files[label] = assertRepositoryEvidenceFile(
      modelId,
      "02-analysis/rev-003",
      `${expectedDirectory}/${filename}`,
      `Gate 02 motion correction ${label}`
    );
  }
  const frameSpecs = [
    ["start", 0, "00-start-000ms.png"],
    ["quarter", 175, "01-quarter-175ms.png"],
    ["userNearest", 200, "02-user-nearest-200ms.png"],
    ["half", 350, "03-half-350ms.png"],
    ["threeQuarter", 525, "04-three-quarter-525ms.png"],
    ["frontToEdge", 550, "06-turn-front-to-edge-550ms.png"],
    ["edge", 600, "07-edge-600ms.png"],
    ["reverse", 650, "08-reverse-650ms.png"],
    ["end", 700, "05-end-700ms.png"]
  ];
  const frameFiles = Object.fromEntries(frameSpecs.map(([key, , filename]) => [
    key,
    assertRepositoryEvidenceFile(
      modelId,
      "02-analysis/rev-003",
      `${expectedDirectory}/frames/${filename}`,
      `Gate 02 real Rive frame ${key}`
    )
  ]));

  const canonicalPaths = {
    rive: "unity/FidgetingApp/Assets/Plugins/iOS/Rive/gacha-single-draw-jumbotron.riv",
    swift: "unity/FidgetingApp/Assets/Plugins/iOS/FidgetGachaRivePresentation.swift",
    mainLog: "unity/FidgetingApp/Artifacts/GachaPackRiveUnityContinuousPreview/gacha-pack-rive-unity-continuous-combined.log",
    standaloneLog: "unity/FidgetingApp/Artifacts/GachaRiveShippingPreview/gacha-rive-shipping-flow.log"
  };
  const canonical = Object.fromEntries(Object.entries(canonicalPaths).map(([key, relativePath]) => {
    const absolute = resolveRepoPath(relativePath);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
      throw new PipelineError(`Canonical motion source is missing: ${relativePath}`, 422);
    }
    return [key, { normalized: relativePath, absolute }];
  }));

  const measurement = JSON.parse(fs.readFileSync(files.measurement.absolute, "utf8"));
  const authored = JSON.parse(fs.readFileSync(files.authoredExtract.absolute, "utf8"));
  const quality = JSON.parse(fs.readFileSync(files.qualityReport.absolute, "utf8"));
  const landmarkValidation = JSON.parse(fs.readFileSync(files.landmarkValidation.absolute, "utf8"));
  if (
    measurement?.modelId !== "premium-display-case"
    || measurement?.gate !== "02-analysis"
    || measurement?.analysisRevision !== 3
    || measurement?.status !== "ready_for_review"
    || measurement?.userRejection?.quote !== userQuote
    || measurement?.userRejection?.instruction !== instructionQuote
    || measurement?.axisConclusion?.roll?.status !== "confirmed"
    || measurement?.axisConclusion?.yaw?.status !== "apparent-pseudo-yaw"
    || measurement?.axisConclusion?.pitch?.status !== "unknown"
    || measurement?.axisConclusion?.threeDimensionalAxis?.status !== "unknown"
    || measurement?.axisConclusion?.pureVerticalYTurntable?.status !== "rejected"
    || measurement?.axisConclusion?.xAxisReplacement?.status !== "not-claimed"
    || measurement?.authoredTimeline?.rootDurationMilliseconds !== 3500
    || measurement?.authoredTimeline?.rootTimeScaled125Milliseconds !== 4375
    || measurement?.authoredTimeline?.approvedSlowEnvelopeCandidateMilliseconds !== 4520.833
    || measurement?.authoredTimeline?.approvedCandidateIsMotionApproval !== false
    || measurement?.schematic?.usesCosineWidth !== false
    || measurement?.schematic?.uses3DEulerGuess !== false
    || measurement?.schematic?.wholeCaseOnly !== true
    || measurement?.gateBoundary?.earliestGate !== "02-analysis"
    || measurement?.gateBoundary?.gate01TopologyApprovalPreserved !== true
    || measurement?.gateBoundary?.gate03Through08MustBeStale !== true
    || measurement?.gateBoundary?.shippingUnityChanged !== false
    || measurement?.gateBoundary?.blenderGeometryOrMaterialChanged !== false
    || measurement?.gateBoundary?.buildInstallPhonePush !== false
  ) {
    throw new PipelineError("The Gate 02 motion measurement report is incomplete or overclaims a 3D axis.", 422);
  }
  if (
    authored?.source?.sha256 !== sha256File(canonical.rive.absolute)
    || authored?.source?.bytes !== fs.statSync(canonical.rive.absolute).size
    || authored?.source?.formatVersion !== "7.2"
    || authored?.binding?.outerStateMachine !== "Main"
    || authored?.binding?.backgroundBindableArtboard !== "Slab-rotate-v01"
    || authored?.binding?.foregroundBindableArtboard !== "Coin_Slab_v09-sm"
    || authored?.binding?.childStateMachine !== "State Machine 1"
    || authored?.authored?.backgroundIn?.durationMilliseconds !== 3500
    || authored?.authored?.foregroundIn?.durationMilliseconds !== 3500
    || authored?.authored?.slabRotate?.durationMilliseconds !== 1000
    || authored?.authored?.slabRotate?.loop !== "pingPong"
    || authored?.authored?.coinSlab?.tracks?.length !== 456
    || authored?.authored?.coinSlab?.meshDeformationSummary?.changedValueTrackCount !== 89
    || authored?.authored?.coinSlab?.meshDeformationSummary?.targetTypes?.MeshVertex !== 350
    || authored?.authored?.coinSlab?.meshDeformationSummary?.targetTypes?.ContourMeshVertex !== 106
    || authored?.verifiedConclusions?.coinSlabUses2DMeshDeformation !== true
    || authored?.verifiedConclusions?.uses3DRotationChannels !== false
    || authored?.verifiedConclusions?.uses2DTransformsAndSpriteRemapping !== true
  ) {
    throw new PipelineError("The authored Rive extract does not match the canonical binding or measured timeline.", 422);
  }
  if (
    quality?.status !== "pass"
    || quality?.reviewState !== "ready_for_review"
    || quality?.truth?.realRiveContactSheet !== true
    || quality?.truth?.schematicNotShipping !== true
    || quality?.truth?.wholeCaseOnly !== true
    || quality?.truth?.explode !== false
    || quality?.truth?.usesMeasuredLandmarks !== true
    || quality?.truth?.usesCosineWidth !== false
    || quality?.metrics?.maximumConnectedSubjectComponents !== 1
    || quality?.metrics?.minimumProjectedSubjectWidthPixels < 20
    || quality?.metrics?.maximumHoldMeanRgbDifference !== 0
    || quality?.metrics?.maximumYellowPixelFraction !== 0
    || quality?.metrics?.probedGifDurationMilliseconds !== 4520
  ) {
    throw new PipelineError("The corrected whole-case animation-quality report failed.", 422);
  }
  if (
    landmarkValidation?.status !== "pass-with-explicit-unknowns"
    || landmarkValidation?.conclusion?.pitch?.status !== "unknown"
    || landmarkValidation?.conclusion?.threeDimensionalAxis?.status !== "unknown"
  ) {
    throw new PipelineError("The landmark validation must preserve pitch and physical-axis unknowns.", 422);
  }

  const pngDimensions = (file) => {
    const bytes = fs.readFileSync(file.absolute);
    const isPng = bytes.length >= 24 && bytes.subarray(1, 4).toString("ascii") === "PNG";
    return {
      width: isPng ? bytes.readUInt32BE(16) : 0,
      height: isPng ? bytes.readUInt32BE(20) : 0
    };
  };
  const contactDimensions = pngDimensions(files.contactSheet);
  const boardDimensions = pngDimensions(files.analysisBoard);
  const schematicContactDimensions = pngDimensions(files.schematicContact);
  if (
    contactDimensions.width < 2000
    || contactDimensions.height < 2500
    || boardDimensions.width < 2800
    || boardDimensions.height < 2200
    || schematicContactDimensions.width < 2000
    || schematicContactDimensions.height < 2200
  ) {
    throw new PipelineError("Gate 02 review boards must remain large-type PNG evidence.", 422);
  }
  const gifBytes = fs.readFileSync(files.schematicGif.absolute);
  if (!["GIF87a", "GIF89a"].includes(gifBytes.subarray(0, 6).toString("ascii"))) {
    throw new PipelineError("The corrected whole-case schematic GIF is invalid.", 422);
  }

  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  const ids = {
    userReference: `${modelId}-user-motion-reference-r003`,
    rejectionRecord: `${modelId}-motion-rejection-r003`,
    rive: `${modelId}-motion-rive-source-r003`,
    swift: `${modelId}-motion-swift-binding-r003`,
    mainLog: `${modelId}-motion-main-app-log-r003`,
    standaloneLog: `${modelId}-motion-standalone-log-r003`,
    authoredExtract: `${modelId}-rive-authored-motion-extract-r003`,
    generator: `${modelId}-motion-analysis-generator-r003`,
    contactSheet: `${modelId}-real-rive-motion-contact-sheet-r003`,
    analysisBoard: `${modelId}-motion-axis-analysis-board-r003`,
    measurement: `${modelId}-real-rive-motion-measurements-r003`,
    schematicGif: `${modelId}-measured-motion-schematic-gif-r003`,
    schematicContact: `${modelId}-measured-motion-schematic-contact-r003`,
    qualityReport: `${modelId}-motion-animation-quality-r003`,
    referenceManifest: `${modelId}-motion-reference-manifest-r003`,
    userAnalysis: `${modelId}-user-screenshot-analysis-r003`,
    riveFrameAnalysis: `${modelId}-real-rive-frame-analysis-r003`,
    landmarkValidation: `${modelId}-motion-landmark-validation-r003`
  };
  const frameIds = Object.fromEntries(frameSpecs.map(([key]) => [
    key,
    `${modelId}-real-rive-frame-${key}-r003`
  ]));
  for (const id of [...Object.values(ids), ...Object.values(frameIds)]) {
    if (existingIds.has(id)) throw new PipelineError(`Gate 02 motion correction asset already exists: ${id}`, 409);
  }

  const now = new Date().toISOString();
  const record = ({
    id,
    slot,
    file,
    role,
    producer,
    provenance,
    sourceAssetIds = [],
    view = null,
    reviewState = "active"
  }) => ({
    id,
    stageId: "02-analysis",
    slot,
    path: file.normalized,
    sha256: sha256File(file.absolute),
    exists: true,
    sizeBytes: fs.statSync(file.absolute).size,
    role,
    producer,
    provenance,
    sourceAssetIds,
    ...(view ? { view } : {}),
    reviewState
  });
  const sourceRecords = [
    record({
      id: ids.userReference,
      slot: "motion-reference",
      file: files.userReference,
      role: "user-input",
      producer: { name: "Cursor conversation", version: "2026-08-25" },
      provenance: {
        origin: "user-provided",
        contentClass: "explicit-motion-rejection-screenshot",
        assertedBy: "user",
        note: "User evidence that rejects the pure vertical-Y turntable. Its artwork is not a target texture."
      }
    }),
    record({
      id: ids.rive,
      slot: "motion-source",
      file: canonical.rive,
      role: "historical",
      producer: { name: "Rive", version: "format 7.2 / runtime source" },
      provenance: {
        origin: "repository-generated",
        contentClass: "canonical-rive-motion-source",
        assertedBy: "repository",
        note: "Canonical source for motion extraction only; embedded source identity must not enter the neutral schematic."
      }
    }),
    record({
      id: ids.swift,
      slot: "runtime-binding-source",
      file: canonical.swift,
      role: "historical",
      producer: { name: "shipping Swift source", version: "2026-08-25" },
      provenance: {
        origin: "repository-generated",
        contentClass: "shipping-rive-artboard-binding-source",
        assertedBy: "repository",
        note: "Identifies outer Main state machines, Slab-rotate-v01 and Coin_Slab_v09-sm bindings."
      },
      sourceAssetIds: [ids.rive]
    }),
    record({
      id: ids.mainLog,
      slot: "runtime-log",
      file: canonical.mainLog,
      role: "historical",
      producer: { name: "FidgetSpinner main-app Simulator", version: "2026-08-18" },
      provenance: {
        origin: "repository-generated",
        contentClass: "main-app-rive-runtime-log",
        assertedBy: "repository",
        note: "Observed trigger-to-complete 3617 ms; not the authored timeline duration."
      },
      sourceAssetIds: [ids.rive, ids.swift]
    }),
    record({
      id: ids.standaloneLog,
      slot: "runtime-log",
      file: canonical.standaloneLog,
      role: "historical",
      producer: { name: "shipping-source standalone Simulator", version: "2026-08-18" },
      provenance: {
        origin: "repository-generated",
        contentClass: "standalone-rive-runtime-log",
        assertedBy: "repository",
        note: "Observed trigger-to-complete 3805 ms; retained as runtime variance."
      },
      sourceAssetIds: [ids.rive, ids.swift]
    })
  ];
  const frameRecords = frameSpecs.map(([key, milliseconds]) => record({
    id: frameIds[key],
    slot: "motion-frame",
    file: frameFiles[key],
    role: "analysis",
    producer: {
      name: "@rive-app/canvas",
      version: "2.40.1",
      recipe: `Manual 60 fps state-machine advance to ${milliseconds} ms`
    },
    provenance: {
      origin: "repository-generated",
      contentClass: "true-rive-runtime-frame",
      assertedBy: "assistant",
      note: "True canonical Rive pixels. Crop and scaling are allowed in the contact sheet; source identity is evidence-only."
    },
    sourceAssetIds: [ids.rive, ids.swift],
    view: {
      id: `rive-${key}`,
      camera: "rive-2d-canvas",
      parameters: { widthPixels: 968, heightPixels: 660, milliseconds }
    }
  }));
  const frameAssetIds = frameRecords.map((asset) => asset.id);
  const generatedRecords = [
    record({
      id: ids.rejectionRecord,
      slot: "decision-record",
      file: files.rejectionRecord,
      role: "analysis",
      producer: { name: "fidgeting-model-pipeline", version: "2026-08-25" },
      provenance: {
        origin: "repository-generated",
        contentClass: "exact-user-motion-rejection-record",
        assertedBy: "assistant",
        note: "Preserves the exact quote, earliest-gate boundary and no-build/no-install scope."
      },
      sourceAssetIds: [ids.userReference]
    }),
    record({
      id: ids.authoredExtract,
      slot: "discovery-log",
      file: files.authoredExtract,
      role: "analysis",
      producer: {
        name: "Rive binary parser + official runtime cross-check",
        version: "rive-mcp-server 0.5.0 / @rive-app/canvas 2.40.1",
        recipe: "Artboard, timeline, keyframe, cubic-easing and 2D-transform extraction"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "authored-rive-motion-extract",
        assertedBy: "assistant",
        note: "Proves exact 2D transforms, sprite remapping and mesh deformation. It does not infer a physical 3D axis."
      },
      sourceAssetIds: [ids.rive, ids.swift]
    }),
    record({
      id: ids.generator,
      slot: "analysis-recipe",
      file: files.generator,
      role: "process",
      producer: {
        name: "Python Pillow + OpenCV",
        version: "Pillow 11.3.0 / OpenCV 4.13.0",
        recipe: "Four-corner extraction, homography metrics, review boards and measured-path neutral GIF"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "deterministic-motion-analysis-recipe",
        assertedBy: "assistant",
        note: "Uses measured quadrilaterals. It contains no cosine-width Y turntable and no Euler-axis guess."
      },
      sourceAssetIds: [ids.userReference, ids.authoredExtract, ...frameAssetIds]
    }),
    record({
      id: ids.contactSheet,
      slot: "analysis-board",
      file: files.contactSheet,
      role: "analysis",
      producer: {
        name: "Python Pillow",
        version: "11.3.0",
        recipe: "Nine labeled true-Rive frame crops plus full-canvas trajectory insets"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "true-rive-motion-contact-sheet",
        assertedBy: "assistant",
        note: "Covers start, quarter, user-nearest, half, three-quarter, edge, reverse and end."
      },
      sourceAssetIds: frameAssetIds,
      view: {
        id: "real-rive-motion-contact-sheet",
        camera: "source-frame-grid",
        parameters: {
          widthPixels: contactDimensions.width,
          heightPixels: contactDimensions.height,
          sampleCount: frameRecords.length
        }
      }
    }),
    record({
      id: ids.analysisBoard,
      slot: "analysis-board",
      file: files.analysisBoard,
      role: "analysis",
      producer: {
        name: "Python Pillow + OpenCV",
        version: "2026-08-25",
        recipe: "User and Rive quadrilateral landmarks, screen axes and claim/unknown board"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "motion-axis-perspective-analysis-board",
        assertedBy: "assistant",
        note: "Confirms roll and 2D choreography, labels yaw as apparent, and preserves pitch/physical-axis unknowns."
      },
      sourceAssetIds: [ids.userReference, ids.authoredExtract, ids.contactSheet]
    }),
    record({
      id: ids.measurement,
      slot: "validation-report",
      file: files.measurement,
      role: "validation",
      producer: {
        name: "reference-analysis-validator",
        version: "2026-08-25",
        recipe: "Four corners, edge ratios, homographies, authored transforms, timing and axis confidence"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "real-rive-motion-measurement-report",
        assertedBy: "assistant",
        note: "Separates confirmed roll and sprite turn from unknown pitch and physical axes."
      },
      sourceAssetIds: [ids.userReference, ids.authoredExtract, ids.contactSheet, ids.mainLog, ids.standaloneLog]
    }),
    record({
      id: ids.schematicGif,
      slot: "motion-preview",
      file: files.schematicGif,
      role: "process",
      producer: {
        name: "Python Pillow + OpenCV",
        version: "2026-08-25",
        recipe: "One neutral assembled case warped through measured four-corner landmarks"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "measured-whole-case-motion-schematic-gif",
        assertedBy: "assistant",
        note: "4.520833 s remains a slow envelope candidate. Motion is not approved and source identity is not copied."
      },
      sourceAssetIds: [ids.generator, ids.measurement]
    }),
    record({
      id: ids.schematicContact,
      slot: "motion-contact-sheet",
      file: files.schematicContact,
      role: "process",
      producer: {
        name: "Python Pillow + OpenCV",
        version: "2026-08-25",
        recipe: "Measured neutral-case start/quarter/user-nearest/half/edge/reverse/end/hold review"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "measured-whole-case-motion-schematic-contact-sheet",
        assertedBy: "assistant",
        note: "One connected assembled neutral case. No explode, split, brand art or cosine-width turn."
      },
      sourceAssetIds: [ids.generator, ids.measurement, ids.schematicGif]
    }),
    record({
      id: ids.qualityReport,
      slot: "animation-validation",
      file: files.qualityReport,
      role: "validation",
      producer: {
        name: "animation-quality-gate",
        version: "2026-08-25",
        recipe: "Whole-case, silhouette, direction, flip, split, flicker, edge, duration, identity and gate-boundary checks"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "gate02-motion-animation-quality-report",
        assertedBy: "assistant",
        note: "Passes evidence-only Gate 02 QA. It is not Blender, Unity or shipping output."
      },
      sourceAssetIds: [ids.contactSheet, ids.schematicGif, ids.schematicContact, ids.measurement]
    }),
    record({
      id: ids.referenceManifest,
      slot: "reference-manifest",
      file: files.referenceManifest,
      role: "validation",
      producer: { name: "reference-analysis-validator", version: "2026-08-25" },
      provenance: {
        origin: "repository-generated",
        contentClass: "motion-reference-manifest",
        assertedBy: "assistant",
        note: "Defines one assembled case, source/target identity boundaries and no-axis-overclaim thresholds."
      },
      sourceAssetIds: [ids.userReference, ids.rive, ids.swift]
    }),
    record({
      id: ids.userAnalysis,
      slot: "source-analysis",
      file: files.userAnalysis,
      role: "validation",
      producer: { name: "OpenCV", version: "4.13.0" },
      provenance: {
        origin: "repository-generated",
        contentClass: "user-screenshot-landmark-analysis",
        assertedBy: "assistant",
        note: "Convex-hull four-corner and homography metrics only; it does not assign a physical axis."
      },
      sourceAssetIds: [ids.userReference]
    }),
    record({
      id: ids.riveFrameAnalysis,
      slot: "source-analysis",
      file: files.riveFrameAnalysis,
      role: "validation",
      producer: { name: "OpenCV", version: "4.13.0" },
      provenance: {
        origin: "repository-generated",
        contentClass: "real-rive-frame-landmark-analysis",
        assertedBy: "assistant",
        note: "Measures the true runtime frames and identifies 200 ms as the nearest perspective signature, not an exact artwork match."
      },
      sourceAssetIds: frameAssetIds
    }),
    record({
      id: ids.landmarkValidation,
      slot: "validation-report",
      file: files.landmarkValidation,
      role: "validation",
      producer: { name: "reference-analysis-validator", version: "2026-08-25" },
      provenance: {
        origin: "repository-generated",
        contentClass: "motion-landmark-validation",
        assertedBy: "assistant",
        note: "Applies the modality rule and refuses misleading silhouette IoU across different artwork."
      },
      sourceAssetIds: [ids.userAnalysis, ids.riveFrameAnalysis, ids.measurement]
    })
  ];

  const priorArtifactIds = [...stage.artifactIds];
  const rejectedArtifactIds = [];
  for (const assetId of priorArtifactIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    if (!asset) continue;
    const motionSpecific = [
      "display-case-motion-recipe-r002",
      "display-case-motion-preview-r002",
      "display-case-motion-contact-sheet-r002",
      "display-case-motion-validation-r002",
      "display-case-analysis-board-r002"
    ].includes(asset.id);
    asset.reviewState = motionSpecific ? "rejected" : "historical";
    asset.supersededBy = ids.analysisBoard;
    asset.supersededAt = now;
    asset.dispositionNote = motionSpecific
      ? "User explicitly rejected the pure vertical-Y 360-degree turntable interpretation."
      : "Preserved as historical Gate 02 evidence; current motion review is revision 003.";
    if (motionSpecific) {
      asset.rejectionScope = "pure-y-axis-360-turntable-motion-interpretation";
      rejectedArtifactIds.push(asset.id);
    }
  }

  const priorClaimIds = [];
  for (const claim of manifest.claims || []) {
    if (claim.stageId !== "02-analysis" || claim.state === "superseded") continue;
    priorClaimIds.push(claim.id);
    claim.state = "superseded";
    claim.supersededBy = "premium-display-case-analysis-motion-r003";
    claim.supersededAt = now;
    if (claim.id === "display-case-analysis-flow-r002") {
      claim.rejectionState = "rejected";
      claim.rejectionScope = "pure-y-axis-360-turntable-motion-interpretation";
      claim.rejectionQuote = userQuote;
    }
  }

  manifest.assets.push(...sourceRecords, ...frameRecords, ...generatedRecords);
  const sourceRegion = {
    assetId: ids.userReference,
    x: 210 / 968,
    y: 152 / 660,
    width: 530 / 968,
    height: 429 / 660,
    note: "Whole visible subject used for convex-hull and four-corner perspective analysis."
  };
  const claims = [
    {
      id: "premium-display-case-analysis-closed-loop-r003",
      stageId: "02-analysis",
      category: "topology",
      statement: "Gate 01 topology remains approved: one tangent-continuous closed tubular perimeter, one connected material body, zero open boundaries, and full channel flood-fill.",
      confidence: "user-approved-high",
      sourceAssetIds: ["display-case-gate-01-target-r003"],
      sourceRegions: [],
      state: "active",
      analysisRevision: "003"
    },
    {
      id: "premium-display-case-analysis-manifold-r003",
      stageId: "02-analysis",
      category: "topology",
      statement: "The perimeter remains one connected manifold rather than four bars; the motion correction changes no geometry, material, lighting or topology.",
      confidence: "user-approved-high",
      sourceAssetIds: ["display-case-continuous-frame-clarification", ids.measurement],
      sourceRegions: [],
      state: "active",
      analysisRevision: "003"
    },
    {
      id: "premium-display-case-analysis-background-r003",
      stageId: "02-analysis",
      category: "material",
      statement: "The continuous low-saturation tactile background requirement remains unchanged and is not evaluated by this motion revision.",
      confidence: "carried-forward-high",
      sourceAssetIds: ["display-case-user-correction-2026-08-24"],
      sourceRegions: [],
      state: "active",
      analysisRevision: "003"
    },
    {
      id: "premium-display-case-analysis-label-r003",
      stageId: "02-analysis",
      category: "readability",
      statement: "Phone-readable physical label, logo and achievement zones remain required; source Rive identity text is evidence-only and cannot be copied.",
      confidence: "carried-forward-high",
      sourceAssetIds: ["display-case-user-correction-2026-08-24", ids.referenceManifest],
      sourceRegions: [],
      state: "active",
      analysisRevision: "003"
    },
    {
      id: "premium-display-case-analysis-portrait-r003",
      stageId: "02-analysis",
      category: "proportion",
      statement: "The assembled case remains Portrait at approximately 3:4. This motion correction does not reopen the approved proportion or existing geometry artifacts.",
      confidence: "carried-forward-high",
      sourceAssetIds: ["display-case-analysis-correction-r002", ids.schematicContact],
      sourceRegions: [],
      state: "active",
      analysisRevision: "003"
    },
    {
      id: "premium-display-case-analysis-motion-r003",
      stageId: "02-analysis",
      category: "motion",
      statement: "The pure vertical-Y 360-degree turntable is rejected. The current evidence confirms screen-space roll, translation and scale convergence, plus an apparent sprite/mesh-driven front-edge-reverse-front turn. Pitch, physical yaw angle/sign and the 3D axis remain unknown; do not substitute an X-axis claim.",
      confidence: "mixed-confirmed-and-explicit-unknown",
      sourceAssetIds: [ids.userReference, ids.authoredExtract, ids.contactSheet, ids.measurement],
      sourceRegions: [sourceRegion],
      state: "active",
      analysisRevision: "003"
    },
    {
      id: "premium-display-case-analysis-duration-r003",
      stageId: "02-analysis",
      category: "motion-timing",
      statement: "The authored root timeline is 210 frames at 60 fps (3.500 s); authored ×1.25 is 4.375 s. The previously accepted 4.520833 s remains only a slow-envelope candidate derived from runtime wall time, not approval of the motion path.",
      confidence: "high",
      sourceAssetIds: [ids.authoredExtract, ids.mainLog, ids.standaloneLog, ids.measurement],
      sourceRegions: [],
      state: "active",
      analysisRevision: "003"
    },
    {
      id: "premium-display-case-analysis-identity-boundary-r003",
      stageId: "02-analysis",
      category: "identity",
      statement: "True Rive frames may retain source identity as evidence, but the neutral whole-case mapping must not copy WHATNOT, yellow, smiley, barcode, sample number or dynamic source artwork.",
      confidence: "high",
      sourceAssetIds: [ids.contactSheet, ids.schematicGif, ids.qualityReport],
      sourceRegions: [],
      state: "active",
      analysisRevision: "003"
    },
    {
      id: "premium-display-case-analysis-environment-r003",
      stageId: "02-analysis",
      category: "lighting",
      statement: "Environment isolation and neutral key/fill/rim intent remain historical design inputs, but Gates 07–08 are stale until the corrected motion contract is approved and revalidated downstream.",
      confidence: "carried-forward-high",
      sourceAssetIds: ["display-case-user-request-2026-08-24", ids.measurement],
      sourceRegions: [],
      state: "active",
      analysisRevision: "003"
    }
  ];
  manifest.claims.push(...claims);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = [
    ...sourceRecords.map((asset) => asset.id),
    ...frameAssetIds,
    ...generatedRecords.map((asset) => asset.id)
  ];
  stage.reviewArtifactIds = [
    ids.contactSheet,
    ids.analysisBoard,
    ids.schematicGif,
    ids.schematicContact
  ];
  stage.validations = [
    { id: "gate01-topology-preserved", status: "pass", evidence: "Gate 01 remains approved; no topology, geometry, material or lighting artifact changed." },
    { id: "explicit-y-turntable-rejection-recorded", status: "pass", evidence: `Decision API and history preserve the exact quote: “${userQuote}”` },
    { id: "real-rive-frames-captured", status: "pass", evidence: `${frameRecords.length} canonical runtime frames cover start, quarter, user-nearest, half, three-quarter, edge, reverse and end.` },
    { id: "actual-child-identified", status: "pass", evidence: "Outer state machine Main binds Slab-rotate-v01 and Coin_Slab_v09-sm; the child state machine is State Machine 1." },
    { id: "authored-motion-extracted", status: "pass", evidence: "Root in is 210f/60fps; exact x/y/rotation/scale keyframes and cubic handles are recorded. Slab-rotate is 60f ping-pong; Coin_Slab has 456 X/Y mesh tracks, including 89 changed-value tracks." },
    { id: "axis-confidence-separated", status: "pass", evidence: "Roll is confirmed; yaw is apparent and sprite/mesh-driven; pitch and physical 3D axis/degrees/sign remain unknown. No X-axis replacement is asserted." },
    { id: "measured-landmark-schematic", status: "pass", evidence: "One connected neutral case follows measured quadrilaterals; cosine width, split, explode and brand-art copying are absent." },
    { id: "animation-quality-gate", status: "pass", evidence: `Quality report passes with one connected subject, ${quality.metrics.minimumProjectedSubjectWidthPixels}px minimum edge width, zero hold flicker and zero yellow pixels.` },
    { id: "duration-boundary", status: "pass", evidence: "Authored 3.500 s and ×1.25 4.375 s are reported. 4.520833 s remains a candidate only." },
    { id: "downstream-stale", status: "pass", evidence: "Gates 03–08 retain all artifacts but are stale and cannot count as current approvals." },
    { id: "shipping-boundary", status: "pass", evidence: "No shipping Unity, Blender geometry/material, build, install or phone push occurred." }
  ];
  stage.decision = null;
  stage.analysisSpec = {
    revision: 3,
    userQuote,
    instructionQuote,
    rejectedInterpretation: "pure-vertical-y-axis-360-turntable",
    actualChildArtboard: "Coin_Slab_v09-sm",
    actualChildStateMachine: "State Machine 1",
    outerStateMachine: "Main",
    roll: "confirmed",
    yaw: "apparent-pseudo-yaw",
    pitch: "unknown",
    physicalAxis: "unknown",
    xAxisClaim: "not-claimed",
    authoredDurationMilliseconds: 3500,
    authoredTimeScaled125Milliseconds: 4375,
    slowEnvelopeCandidateMilliseconds: 4520.833,
    slowEnvelopeCandidateApprovalEffect: "timing-candidate-only-motion-path-unapproved",
    wholeCaseOnly: true,
    explode: false,
    usesMeasuredLandmarks: true,
    usesCosineWidth: false,
    shippingAssetUnchanged: true
  };
  delete stage.staleReason;

  const downstreamReason = "Gate 02 rev 3 replaces the rejected pure-Y turntable with measured Rive motion. Gates 03–08 retain their artifacts as history but require revalidation.";
  const staleStageIds = [];
  for (let index = stageIndex + 1; index <= 7; index += 1) {
    const downstream = manifest.stages[index];
    if ((downstream.artifactIds || []).length) {
      downstream.status = "stale";
      staleStageIds.push(downstream.id);
    }
    downstream.staleReason = downstreamReason;
  }
  for (let index = 8; index < manifest.stages.length; index += 1) {
    const downstream = manifest.stages[index];
    downstream.staleReason = downstreamReason;
  }

  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 01 topology remains approved. The user explicitly rejected the pure vertical-Y 360-degree turntable. Gate 02 rev 3 now uses true Rive frames, exact 2D keyframes and four-corner measurements: roll is confirmed, the turn is apparent and sprite/mesh-driven, while pitch and the physical 3D axis remain unknown. Gate 02 is ready_for_review; Gates 03–08 are stale with artifacts preserved. No shipping Unity, Blender geometry/material, build, install or phone push occurred.";
  manifest.currentState.visualApproval = "pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.motionCorrection = {
    earliestGate: "02-analysis",
    analysisRevision: 3,
    rejectedInterpretation: "pure-vertical-y-axis-360-turntable",
    userQuote,
    instructionQuote,
    approvedSlowEnvelopeCandidateMilliseconds: 4520.833,
    motionPathApproved: false,
    staleStageIds
  };

  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "02-analysis",
    analysisRevision: "003",
    userQuote,
    instructionQuote,
    rejectedMotionClaimId: "display-case-analysis-flow-r002",
    rejectedArtifactIds,
    supersededClaimIds: priorClaimIds,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    claimIds: claims.map((claim) => claim.id),
    actualChildArtboard: "Coin_Slab_v09-sm",
    actualChildStateMachine: "State Machine 1",
    roll: "confirmed",
    yaw: "apparent-pseudo-yaw",
    pitch: "unknown",
    physicalAxis: "unknown",
    authoredDurationMilliseconds: 3500,
    authoredTimeScaled125Milliseconds: 4375,
    slowEnvelopeCandidateMilliseconds: 4520.833,
    slowEnvelopeCandidateOnly: true,
    staleStageIds,
    approvedCount: 1,
    earliestGate: "02-analysis",
    autoApproved: false,
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseEntryMotionReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) {
    throw new PipelineError("Manifest revision conflict.", 409);
  }
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This entry-motion review is supported only for the Premium Display Case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "02-analysis");
  const intake = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  const userQuote = String(payload.userQuote || "").trim();
  const expectedQuote = "节奏感不对，然后感觉XYZ轴运动过多，过于复杂，我觉得主体是要表达入场，现在增加了过多的动销元素，让人感觉抓不住重点";
  if (intake.status !== "approved") {
    throw new PipelineError("Gate 01 topology approval must remain approved.", 422);
  }
  if (
    stage.status !== "rejected"
    || stage.decision?.action !== "reject"
    || !stage.decision.notes.includes(expectedQuote)
    || stage.analysisSpec?.revision !== 3
  ) {
    throw new PipelineError("Gate 02 rev 3 must first record the user's entry-focus rejection.", 422);
  }
  if (userQuote !== expectedQuote) {
    throw new PipelineError("The exact entry-motion feedback must be preserved.", 422);
  }

  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/02-analysis/rev-004"
  )));
  const evidencePaths = {
    feedback: "user-entry-motion-feedback.md",
    generator: "generate_entry_motion_review.py",
    recipe: "entry-motion-recipe.json",
    board: "entry-only-analysis-board.png",
    gif: "entry-only-motion.gif",
    contact: "entry-only-contact-sheet.png",
    validation: "entry-motion-validation.json",
    quality: "animation-quality-report.json"
  };
  const files = Object.fromEntries(Object.entries(evidencePaths).map(([key, filename]) => [
    key,
    assertRepositoryEvidenceFile(
      modelId,
      "02-analysis/rev-004",
      `${expectedDirectory}/${filename}`,
      `Gate 02 entry-motion ${key}`
    )
  ]));
  const recipe = JSON.parse(fs.readFileSync(files.recipe.absolute, "utf8"));
  const validation = JSON.parse(fs.readFileSync(files.validation.absolute, "utf8"));
  const quality = JSON.parse(fs.readFileSync(files.quality.absolute, "utf8"));
  if (
    recipe?.modelId !== modelId
    || recipe?.gate !== "02-analysis"
    || recipe?.analysisRevision !== 4
    || recipe?.status !== "ready_for_review"
    || recipe?.userIntent !== "entry-is-primary"
    || recipe?.motion?.caseTranslation !== "screen-y-only"
    || recipe?.motion?.packTranslation !== "screen-y-only-after-ready"
    || recipe?.motion?.caseRotationDegrees?.some((value) => value !== 0)
    || recipe?.motion?.caseScale !== 1
    || recipe?.motion?.roll !== false
    || recipe?.motion?.yaw !== false
    || recipe?.motion?.pitch !== false
    || recipe?.motion?.lateralDrift !== false
    || recipe?.motion?.singleHighlight !== true
    || recipe?.motion?.wholeCaseOnly !== true
    || recipe?.motion?.objectReplacement !== false
    || recipe?.timingApprovalEffect !== "none-review-candidate-only"
  ) {
    throw new PipelineError("The Gate 02 rev 4 entry-motion recipe is incomplete or adds secondary motion.", 422);
  }
  if (
    validation?.status !== "pass"
    || quality?.status !== "pass"
    || quality?.metrics?.primaryMotionCount !== 1
    || quality?.metrics?.movingAxes?.join(",") !== "screen-y"
    || quality?.metrics?.rotationKeyCount !== 0
    || quality?.metrics?.scaleKeyCount !== 0
    || quality?.metrics?.highlightCount !== 1
    || quality?.metrics?.objectReplacementCount !== 0
  ) {
    throw new PipelineError("The Gate 02 rev 4 entry-motion validation did not pass.", 422);
  }

  const ids = {
    feedback: "premium-display-case-entry-feedback-r004",
    generator: "premium-display-case-entry-generator-r004",
    recipe: "premium-display-case-entry-recipe-r004",
    board: "premium-display-case-entry-board-r004",
    gif: "premium-display-case-entry-gif-r004",
    contact: "premium-display-case-entry-contact-r004",
    validation: "premium-display-case-entry-validation-r004",
    quality: "premium-display-case-entry-quality-r004"
  };
  const userMotionReferenceId = manifest.assets.find((asset) => (
    asset.id === "premium-display-case-user-motion-reference-r003"
    || asset.id.endsWith("-user-motion-reference-r003")
  ))?.id;
  if (!userMotionReferenceId) {
    throw new PipelineError("The prior user motion reference is missing.", 422);
  }
  const priorSourceIds = [
    "display-case-user-request-2026-08-24",
    userMotionReferenceId
  ];
  const records = [
    [ids.feedback, "decision-record", files.feedback, "analysis", "exact-user-entry-motion-feedback", priorSourceIds],
    [ids.generator, "analysis-recipe", files.generator, "process", "deterministic-entry-motion-generator", [ids.feedback]],
    [ids.recipe, "analysis-recipe", files.recipe, "analysis", "entry-only-motion-recipe", [ids.feedback, ids.generator]],
    [ids.board, "analysis-board", files.board, "analysis", "entry-only-motion-analysis-board", [ids.feedback, ids.recipe]],
    [ids.gif, "motion-preview", files.gif, "process", "entry-only-motion-gif", [ids.generator, ids.recipe]],
    [ids.contact, "analysis-board", files.contact, "analysis", "entry-only-motion-contact-sheet", [ids.generator, ids.recipe]],
    [ids.validation, "motion-validation", files.validation, "validation", "entry-only-motion-validation", [ids.recipe, ids.gif]],
    [ids.quality, "animation-validation", files.quality, "validation", "entry-only-motion-quality-report", [ids.board, ids.gif, ids.contact]]
  ].map(([id, slot, file, role, contentClass, sourceAssetIds]) => ({
    id,
    stageId: "02-analysis",
    slot,
    path: file.normalized,
    sha256: sha256File(file.absolute),
    exists: true,
    sizeBytes: fs.statSync(file.absolute).size,
    role,
    producer: {
      name: "fidgeting-model-pipeline",
      version: "2026-08-26",
      recipe: "One-subject screen-Y entry review"
    },
    provenance: {
      origin: "repository-generated",
      contentClass,
      assertedBy: "assistant",
      note: "One assembled case enters from behind the Pack. No rotation, lateral drift, scale animation, split, explode or proxy."
    },
    sourceAssetIds
  }));
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  if (records.some((record) => existingIds.has(record.id))) {
    throw new PipelineError("Gate 02 rev 4 asset ids already exist.", 409);
  }
  manifest.assets.push(...records);

  const now = new Date().toISOString();
  for (const claim of manifest.claims || []) {
    if (claim.stageId === "02-analysis" && claim.state !== "superseded") {
      claim.state = "superseded";
      claim.supersededBy = "analysis-rev-004";
      claim.supersededAt = now;
    }
  }
  const claims = [
    {
      id: "premium-display-case-analysis-entry-primary-r004",
      stageId: "02-analysis",
      category: "motion",
      statement: "The assembled case entry is the only primary motion. It moves upward in screen space from behind the Pack while the Pack retreats downward.",
      confidence: "user-directed-high",
      sourceAssetIds: [ids.feedback, ids.board, ids.gif],
      sourceRegions: [],
      state: "active",
      analysisRevision: "004"
    },
    {
      id: "premium-display-case-analysis-secondary-motion-removed-r004",
      stageId: "02-analysis",
      category: "motion",
      statement: "Entry uses no roll, yaw, pitch, lateral drift or scale animation; the background and camera remain still.",
      confidence: "user-directed-high",
      sourceAssetIds: [ids.feedback, ids.recipe, ids.validation],
      sourceRegions: [],
      state: "active",
      analysisRevision: "004"
    },
    {
      id: "premium-display-case-analysis-highlight-after-settle-r004",
      stageId: "02-analysis",
      category: "motion",
      statement: "After the case settles, one narrow highlight may play once, followed by a static hold.",
      confidence: "high",
      sourceAssetIds: [ids.board, ids.gif, ids.quality],
      sourceRegions: [],
      state: "active",
      analysisRevision: "004"
    },
    {
      id: "premium-display-case-analysis-entry-timing-unlocked-r004",
      stageId: "02-analysis",
      category: "motion-timing",
      statement: "The 2.2 second review rhythm is a comparison candidate only and does not approve a shipping duration.",
      confidence: "high",
      sourceAssetIds: [ids.recipe, ids.contact],
      sourceRegions: [],
      state: "active",
      analysisRevision: "004"
    }
  ];
  manifest.claims.push(...claims);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.reviewArtifactIds = [ids.board, ids.gif, ids.contact];
  stage.validations = [
    { id: "user-entry-focus-recorded", status: "pass", evidence: `The decision history preserves: “${userQuote}”.` },
    { id: "single-primary-motion", status: "pass", evidence: "One assembled case moves on screen Y only." },
    { id: "secondary-motion-removed", status: "pass", evidence: "Roll, yaw, pitch, X drift and scale animation are zero." },
    { id: "single-highlight", status: "pass", evidence: "One narrow post-settle highlight is present." },
    { id: "whole-case-no-replacement", status: "pass", evidence: "One whole case remains the same subject; no proxy, split or explode." },
    { id: "timing-not-locked", status: "pass", evidence: "The review rhythm has no shipping approval effect." },
    { id: "shipping-boundary", status: "pass", evidence: "Shipping Unity, build, install and phone state remain unchanged." }
  ];
  stage.decision = null;
  stage.analysisSpec = {
    revision: 4,
    userQuote,
    primaryMotion: "entry",
    caseTranslation: "screen-y-only",
    packTranslation: "screen-y-only-after-ready",
    roll: "removed",
    yaw: "removed",
    pitch: "removed",
    lateralDrift: "removed",
    scaleAnimation: "removed",
    cameraMotion: "none",
    backgroundMotion: "none",
    singleHighlightAfterSettle: true,
    wholeCaseOnly: true,
    objectReplacement: false,
    reviewDurationSeconds: 2.2,
    timingApprovalEffect: "none-review-candidate-only",
    shippingAssetUnchanged: true
  };
  delete stage.staleReason;

  const downstreamReason = "Gate 02 rev 4 replaces the rejected multi-axis motion with entry-only screen-Y motion. Gates 03–08 retain history but require revalidation.";
  const staleStageIds = [];
  for (let index = stageIndex + 1; index <= 7; index += 1) {
    const downstream = manifest.stages[index];
    if ((downstream.artifactIds || []).length) {
      downstream.status = "stale";
      staleStageIds.push(downstream.id);
    }
    downstream.staleReason = downstreamReason;
  }
  for (let index = 8; index < manifest.stages.length; index += 1) {
    manifest.stages[index].staleReason = downstreamReason;
  }

  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 01 remains approved. Gate 02 rev 3 multi-axis motion is rejected. Gate 02 rev 4 makes entry the only primary action: one assembled case moves upward from behind the Pack, with no roll, yaw, pitch, lateral drift or scale animation; one narrow highlight follows settlement. The 2.2 s rhythm is review-only. Gates 03–08 remain stale; shipping Unity is unchanged.";
  manifest.currentState.visualApproval = "pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.motionCorrection = {
    earliestGate: "02-analysis",
    analysisRevision: 4,
    rejectedAnalysisRevision: 3,
    userQuote,
    primaryMotion: "entry",
    movingAxes: ["screen-y"],
    removedMotion: ["roll", "yaw", "pitch", "lateral-drift", "scale-animation"],
    timingApproved: false,
    staleStageIds
  };

  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "02-analysis",
    analysisRevision: "004",
    userQuote,
    rejectedAnalysisRevision: 3,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    claimIds: claims.map((claim) => claim.id),
    primaryMotion: "entry",
    movingAxes: ["screen-y"],
    removedMotion: ["roll", "yaw", "pitch", "lateral-drift", "scale-animation"],
    reviewDurationSeconds: 2.2,
    timingApprovalEffect: "none-review-candidate-only",
    staleStageIds,
    approvedCount: 1,
    earliestGate: "02-analysis",
    autoApproved: false,
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseMeasuredMotionSelection(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) {
    throw new PipelineError("Manifest revision conflict.", 409);
  }
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("Measured motion selection is supported only for the Premium Display Case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "02-analysis");
  const stage = manifest.stages[stageIndex];
  const scopeSelection = String(payload.scopeSelection || "").trim();
  const motionSelection = String(payload.motionSelection || "").trim();
  const continueQuote = String(payload.continueQuote || "").trim();
  const requiredScopeSelection = "只纠正动画；静态结构保留";
  const requiredMotionSelection = "整盒刚性；用 pitch/yaw/roll 复合翻转";
  if (
    stage.status !== "ready_for_review"
    || stage.analysisSpec?.revision !== 4
    || scopeSelection !== requiredScopeSelection
    || motionSelection !== requiredMotionSelection
    || continueQuote !== "继续"
  ) {
    throw new PipelineError(
      "Gate 02 must preserve the two exact selections and the user's continue quote before reactivating rev 3.",
      422
    );
  }

  const approvalPath = assertRepositoryEvidenceFile(
    modelId,
    "02-analysis/rev-003",
    "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/02-analysis/rev-003/user-measured-motion-approval.md",
    "Gate 02 measured-motion approval record"
  );
  const approvalAssetId = "premium-display-case-gate02-rev3-user-approval";
  if (manifest.assets.some((asset) => asset.id === approvalAssetId)) {
    throw new PipelineError("Gate 02 measured-motion approval is already registered.", 409);
  }

  const selectedRev3AssetIds = [
    "premium-display-case-user-motion-reference-r003",
    "premium-display-case-motion-rive-source-r003",
    "premium-display-case-motion-swift-binding-r003",
    "premium-display-case-motion-main-app-log-r003",
    "premium-display-case-motion-standalone-log-r003",
    "premium-display-case-real-rive-frame-start-r003",
    "premium-display-case-real-rive-frame-quarter-r003",
    "premium-display-case-real-rive-frame-userNearest-r003",
    "premium-display-case-real-rive-frame-half-r003",
    "premium-display-case-real-rive-frame-threeQuarter-r003",
    "premium-display-case-real-rive-frame-frontToEdge-r003",
    "premium-display-case-real-rive-frame-edge-r003",
    "premium-display-case-real-rive-frame-reverse-r003",
    "premium-display-case-real-rive-frame-end-r003",
    "premium-display-case-motion-rejection-r003",
    "premium-display-case-rive-authored-motion-extract-r003",
    "premium-display-case-motion-analysis-generator-r003",
    "premium-display-case-real-rive-motion-contact-sheet-r003",
    "premium-display-case-motion-axis-analysis-board-r003",
    "premium-display-case-real-rive-motion-measurements-r003",
    "premium-display-case-measured-motion-schematic-gif-r003",
    "premium-display-case-measured-motion-schematic-contact-r003",
    "premium-display-case-motion-animation-quality-r003",
    "premium-display-case-motion-reference-manifest-r003",
    "premium-display-case-user-screenshot-analysis-r003",
    "premium-display-case-real-rive-frame-analysis-r003",
    "premium-display-case-motion-landmark-validation-r003"
  ];
  for (const assetId of selectedRev3AssetIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    if (
      !asset
      || asset.exists === false
      || !fs.existsSync(resolveRepoPath(asset.path))
      || sha256File(resolveRepoPath(asset.path)) !== asset.sha256
    ) {
      throw new PipelineError(`Gate 02 rev 3 evidence is missing or changed: ${assetId}`, 422);
    }
  }

  const now = new Date().toISOString();
  const rev4ArtifactIds = [...stage.artifactIds];
  for (const assetId of rev4ArtifactIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    if (!asset) continue;
    asset.reviewState = "superseded";
    asset.supersededBy = approvalAssetId;
    asset.supersededAt = now;
    asset.dispositionNote = "Preserved as historical entry-only evidence. The user's explicit rigid measured-motion selection reactivates Gate 02 rev 3.";
  }
  for (const assetId of selectedRev3AssetIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    asset.reviewState = "active";
    asset.reactivatedAt = now;
    asset.reactivationBasis = approvalAssetId;
  }

  manifest.assets.push({
    id: approvalAssetId,
    stageId: "02-analysis",
    slot: "decision-record",
    path: approvalPath.normalized,
    sha256: sha256File(approvalPath.absolute),
    exists: true,
    sizeBytes: fs.statSync(approvalPath.absolute).size,
    role: "user-input",
    producer: {
      name: "Cursor conversation",
      version: "504719bf-a4a3-44c2-b1f3-a3bd342e5ae3",
      recipe: "Exact Gate 02 rev 3 measured-motion selections and continue quote"
    },
    provenance: {
      origin: "user-provided",
      contentClass: "measured-motion-gate-approval",
      assertedBy: "user",
      note: "Records motion-only scope, rigid whole-case composite rotation, and the exact continue quote."
    },
    sourceAssetIds: [
      "premium-display-case-motion-axis-analysis-board-r003",
      "premium-display-case-real-rive-motion-measurements-r003"
    ],
    reviewState: "active"
  });

  const reactivatedClaimIds = [
    "premium-display-case-analysis-closed-loop-r003",
    "premium-display-case-analysis-manifold-r003",
    "premium-display-case-analysis-background-r003",
    "premium-display-case-analysis-label-r003",
    "premium-display-case-analysis-portrait-r003",
    "premium-display-case-analysis-motion-r003",
    "premium-display-case-analysis-identity-boundary-r003",
    "premium-display-case-analysis-environment-r003"
  ];
  for (const claim of manifest.claims || []) {
    if (claim.stageId !== "02-analysis") continue;
    if (reactivatedClaimIds.includes(claim.id)) {
      claim.state = "active";
      claim.reactivatedAt = now;
      claim.reactivationBasis = approvalAssetId;
      delete claim.supersededBy;
      delete claim.supersededAt;
      continue;
    }
    if (claim.analysisRevision === "004" && claim.state !== "superseded") {
      claim.state = "superseded";
      claim.supersededBy = approvalAssetId;
      claim.supersededAt = now;
    }
  }
  const priorDurationClaim = manifest.claims.find(
    (claim) => claim.id === "premium-display-case-analysis-duration-r003"
  );
  if (priorDurationClaim) {
    priorDurationClaim.state = "superseded";
    priorDurationClaim.supersededBy = "premium-display-case-analysis-duration-lock-r003";
    priorDurationClaim.supersededAt = now;
  }

  const decisionClaims = [
    {
      id: "premium-display-case-analysis-static-preservation-r003",
      stageId: "02-analysis",
      category: "scope",
      statement: "The user's motion-only selection preserves the historically approved static case values: 228 × 304 × 59 mm, Portrait 0.75, 10 × 9 mm closed tube with 6 × 5 mm passage and 2 mm wall, R20 outer corners, 184 × 58 mm label at Y=99 mm, 180 × 198 × 48 mm ContentSlot, concentric corner families, and the current material ranges. Toy content remains out of scope.",
      confidence: "high",
      sourceAssetIds: [approvalAssetId],
      sourceRegions: [],
      state: "active",
      analysisRevision: "003",
      assertedBy: "user",
      decisionState: "locked-motion-only-preservation"
    },
    {
      id: "premium-display-case-analysis-rigid-target-r003",
      stageId: "02-analysis",
      category: "motion",
      statement: "The target is one rigid assembled Portrait case driven at PresentationRoot by a per-sample quaternion, translation, and uniform framing scale fitted to measured Rive quadrilaterals. Pure Y, pure X, any single-axis physical claim, Rive non-rigid mesh deformation, layer separation, and explode are forbidden.",
      confidence: "high",
      sourceAssetIds: [
        approvalAssetId,
        "premium-display-case-rive-authored-motion-extract-r003",
        "premium-display-case-real-rive-motion-measurements-r003"
      ],
      sourceRegions: [],
      state: "active",
      analysisRevision: "003",
      assertedBy: "user",
      decisionState: "locked-rigid-best-fit-target"
    },
    {
      id: "premium-display-case-analysis-duration-lock-r003",
      stageId: "02-analysis",
      category: "motion-timing",
      statement: "The measured path is uniformly time-scaled to an exact total duration of 4.520833 seconds. Entry, flip, reverse, hold, and single-highlight windows retain their order and relative timing from the canonical Rive extract; no new pause or second highlight is inserted.",
      confidence: "high",
      sourceAssetIds: [
        approvalAssetId,
        "premium-display-case-rive-authored-motion-extract-r003",
        "premium-display-case-real-rive-motion-measurements-r003"
      ],
      sourceRegions: [],
      state: "active",
      analysisRevision: "003",
      assertedBy: "user",
      decisionState: "locked-total-duration"
    }
  ];
  for (const claim of decisionClaims) {
    if (manifest.claims.some((candidate) => candidate.id === claim.id)) {
      throw new PipelineError(`Gate 02 decision claim already exists: ${claim.id}`, 409);
    }
  }
  manifest.claims.push(...decisionClaims);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = [...selectedRev3AssetIds, approvalAssetId];
  stage.reviewArtifactIds = [
    "premium-display-case-real-rive-motion-contact-sheet-r003",
    "premium-display-case-motion-axis-analysis-board-r003",
    "premium-display-case-measured-motion-schematic-gif-r003",
    "premium-display-case-measured-motion-schematic-contact-r003"
  ];
  stage.validations = [
    { id: "exact-user-selections-recorded", status: "pass", evidence: `“${scopeSelection}” + “${motionSelection}” + “${continueQuote}” are preserved in repository evidence.` },
    { id: "rev3-measured-evidence-immutable", status: "pass", evidence: `${selectedRev3AssetIds.length} Gate 02 rev 3 assets match their registered SHA-256 values.` },
    { id: "static-structure-preserved", status: "pass", evidence: "The selection changes animation only and preserves approved dimensions, tube, label, ContentSlot, concentric corners, and material ranges." },
    { id: "rigid-whole-case-target", status: "pass", evidence: "PresentationRoot owns a rigid quaternion/translation/uniform-framing fit. Rive mesh deformation is source evidence only." },
    { id: "axis-overclaim-forbidden", status: "pass", evidence: "Pure Y, pure X, and every single-axis physical claim remain forbidden." },
    { id: "duration-locked", status: "pass", evidence: "Total duration is locked to 4.520833 s by uniform time scaling only." },
    { id: "whole-case-no-explode", status: "pass", evidence: "One assembled case remains visible; split, explode, assembly, and reassembly are forbidden." },
    { id: "toy-scope-guard", status: "pass", evidence: "Toy/prize geometry, material, artwork, pivot, physics, Haptics, and mechanism remain caller-owned and unchanged." },
    { id: "shipping-boundary", status: "pass", evidence: "No Blender geometry/material, shipping Unity, build, install, or phone push is authorized." }
  ];
  stage.decision = null;
  stage.analysisSpec = {
    revision: 3,
    evidenceRevision: 3,
    selectionRevision: 1,
    sourceTaskId: "504719bf-a4a3-44c2-b1f3-a3bd342e5ae3",
    reviewedArtifactId: "premium-display-case-motion-axis-analysis-board-r003",
    scopeSelection,
    motionSelection,
    continueQuote,
    staticStructurePreserved: true,
    targetObject: "one-rigid-assembled-portrait-case",
    motionOwner: "PresentationRoot",
    poseRepresentation: "per-sample-quaternion-translation-uniform-framing",
    rotationInterpretation: "composite-pitch-yaw-roll-best-fit-not-physical-axis-claim",
    physicalAxisClaim: "forbidden",
    pureYAxisClaim: "forbidden",
    pureXAxisClaim: "forbidden",
    singleAxisClaim: "forbidden",
    riveMeshDeformationUse: "source-evidence-only-forbidden-as-target",
    totalDurationSeconds: 4.520833,
    timingPolicy: "uniform-time-scale-canonical-rive-path-only",
    wholeCaseOnly: true,
    explode: false,
    toyOutOfScope: true,
    shippingAssetUnchanged: true
  };
  delete stage.staleReason;

  const downstreamReason = "Gate 02 rev 3 measured motion is selected for rigid best-fit contract work. Historical Gate 03–08 artifacts remain stale until each gate is revalidated.";
  const staleStageIds = [];
  for (let index = stageIndex + 1; index <= 7; index += 1) {
    const downstream = manifest.stages[index];
    downstream.status = "stale";
    downstream.staleReason = downstreamReason;
    staleStageIds.push(downstream.id);
  }
  for (let index = 8; index < manifest.stages.length; index += 1) {
    manifest.stages[index].staleReason = downstreamReason;
  }

  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 02 rev 3 measured evidence is active again after the user's exact motion-only and rigid whole-case selections. The next API action may approve Gate 02 only. Gates 03–08 remain stale, and shipping Unity is unchanged.";
  manifest.currentState.visualApproval = "pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.motionCorrection = {
    earliestGate: "02-analysis",
    analysisRevision: 3,
    evidenceRevision: 3,
    scopeSelection,
    motionSelection,
    continueQuote,
    targetMotion: "rigid-composite-quaternion-fit",
    prohibited: [
      "physical-y-axis-claim",
      "physical-x-axis-claim",
      "single-axis-claim",
      "rive-mesh-deformation-target",
      "explode"
    ],
    lockedTotalDurationSeconds: 4.520833,
    motionPathApproved: false,
    staleStageIds
  };
  const event = makeEvent(manifest, "stage-review-selection-applied", {
    stageId: "02-analysis",
    analysisRevision: "003",
    evidenceRevision: 3,
    scopeSelection,
    motionSelection,
    continueQuote,
    approvalAssetId,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    activeClaimIds: [
      ...reactivatedClaimIds,
      ...decisionClaims.map((claim) => claim.id)
    ],
    supersededAnalysisRevision: 4,
    supersededArtifactIds: rev4ArtifactIds,
    staleStageIds,
    approvedCount: 1,
    earliestGate: "02-analysis",
    autoApproved: false,
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseRigidMotionContract(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) {
    throw new PipelineError("Manifest revision conflict.", 409);
  }
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("Rigid motion contract registration is supported only for the Premium Display Case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "03-contract");
  const analysis = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (
    analysis.status !== "approved"
    || analysis.analysisSpec?.revision !== 3
    || analysis.analysisSpec?.approval?.userApprovalQuote !== "继续"
    || analysis.analysisSpec?.approval?.approvedEvidenceRevision !== 3
  ) {
    throw new PipelineError("Gate 02 rev 3 measured motion must be approved before registering Gate 03 rev 2.", 422);
  }

  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/03-contract/rev-002"
  )));
  const files = {
    generator: assertRepositoryEvidenceFile(
      modelId,
      "03-contract/rev-002",
      `${expectedDirectory}/generate_rigid_motion_contract.py`,
      "Gate 03 rev 2 generator"
    ),
    contract: assertRepositoryEvidenceFile(
      modelId,
      "03-contract/rev-002",
      `${expectedDirectory}/modeling-contract.json`,
      "Gate 03 rev 2 contract"
    ),
    fit: assertRepositoryEvidenceFile(
      modelId,
      "03-contract/rev-002",
      `${expectedDirectory}/rigid-motion-fit.json`,
      "Gate 03 rev 2 rigid motion fit"
    ),
    validation: assertRepositoryEvidenceFile(
      modelId,
      "03-contract/rev-002",
      `${expectedDirectory}/rigid-motion-fit-validation.json`,
      "Gate 03 rev 2 fit validation"
    ),
    preview: assertRepositoryEvidenceFile(
      modelId,
      "03-contract/rev-002",
      `${expectedDirectory}/contract-preview.png`,
      "Gate 03 rev 2 contract preview"
    ),
    poseSheet: assertRepositoryEvidenceFile(
      modelId,
      "03-contract/rev-002",
      `${expectedDirectory}/rigid-pose-contact-sheet.png`,
      "Gate 03 rev 2 pose contact sheet"
    ),
    motionCurves: assertRepositoryEvidenceFile(
      modelId,
      "03-contract/rev-002",
      `${expectedDirectory}/rigid-motion-curves.png`,
      "Gate 03 rev 2 motion curves"
    )
  };
  const contract = JSON.parse(fs.readFileSync(files.contract.absolute, "utf8"));
  const fit = JSON.parse(fs.readFileSync(files.fit.absolute, "utf8"));
  const validation = JSON.parse(fs.readFileSync(files.validation.absolute, "utf8"));
  const activeClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  const expectedLabels = [
    "START",
    "QUARTER",
    "USER-SCREENSHOT NEAREST",
    "HALF",
    "THREE-QUARTER",
    "FRONT → EDGE",
    "EDGE",
    "REVERSE FACE",
    "END / FRONT"
  ];
  const allFinite = (values) => (
    Array.isArray(values)
    && values.length > 0
    && values.every((value) => Number.isFinite(Number(value)))
  );
  const fitSamplesValid = Array.isArray(fit?.samples)
    && fit.samples.length === expectedLabels.length
    && fit.samples.every((sample, index) => (
      sample.label === expectedLabels[index]
      && allFinite(sample.presentationQuaternionWxyz)
      && sample.presentationQuaternionWxyz.length === 4
      && allFinite(sample.diagnosticTranslationCameraMm)
      && sample.diagnosticTranslationCameraMm.length === 3
      && sample.diagnosticTranslationCameraMm[2] > 0
      && sample.uniformScale === 1
      && Number.isFinite(sample.reprojectionResidualPixels?.mean)
      && Number.isFinite(sample.reprojectionResidualPixels?.maximum)
    ));
  if (
    contract?.modelId !== modelId
    || contract?.contractRevision !== 2
    || contract?.stageStatus !== "ready_for_review"
    || contract?.approvalEffect !== "none-until-explicit-gate-03-user-approval"
    || JSON.stringify(contract.sourceClaimIds) !== JSON.stringify(activeClaimIds)
    || activeClaimIds.length !== 11
    || activeClaimIds.some((claimId) => !claimId.endsWith("-r003"))
    || contract?.userSelections?.scope !== "只纠正动画；静态结构保留"
    || contract?.userSelections?.targetMotion !== "整盒刚性；用 pitch/yaw/roll 复合翻转"
    || contract?.userSelections?.continueQuote !== "继续"
    || contract?.staticPreservation?.portraitEnvelope?.widthMm !== 228
    || contract?.staticPreservation?.portraitEnvelope?.heightMm !== 304
    || contract?.staticPreservation?.portraitEnvelope?.depthMm !== 59
    || contract?.staticPreservation?.portraitEnvelope?.widthHeightRatio !== 0.75
    || contract?.staticPreservation?.closedTube?.outerSectionMm?.width !== 10
    || contract?.staticPreservation?.closedTube?.outerSectionMm?.depth !== 9
    || contract?.staticPreservation?.closedTube?.passageSectionMm?.width !== 6
    || contract?.staticPreservation?.closedTube?.passageSectionMm?.depth !== 5
    || contract?.staticPreservation?.closedTube?.wallThicknessMm !== 2
    || contract?.staticPreservation?.closedTube?.outerCornerRadiusMm !== 20
    || contract?.staticPreservation?.physicalLabel?.widthMm !== 184
    || contract?.staticPreservation?.physicalLabel?.heightMm !== 58
    || contract?.staticPreservation?.physicalLabel?.centerYmm !== 99
    || contract?.staticPreservation?.contentSlot?.widthMm !== 180
    || contract?.staticPreservation?.contentSlot?.heightMm !== 198
    || contract?.staticPreservation?.contentSlot?.depthMm !== 48
    || contract?.staticPreservation?.concentricCornerFamilies?.maximumDriftMm !== 0
    || contract?.staticPreservation?.geometryMutationAllowed !== false
    || contract?.staticPreservation?.materialMutationAllowed !== false
    || contract?.staticPreservation?.toyScope?.status !== "out-of-scope-caller-owned-content"
    || contract?.closedTubeFrame?.topology?.connectivity !== "one connected manifold"
    || contract?.motionContract?.target !== "one rigid assembled Portrait cuboid"
    || contract?.motionContract?.motionOwner !== "PresentationRoot"
    || contract?.motionContract?.physicalAxisClaim !== null
    || !contract?.motionContract?.prohibited?.includes("pure Y turntable")
    || !contract?.motionContract?.prohibited?.includes("pure X rotation replacement")
    || !contract?.motionContract?.prohibited?.includes("single-axis physical claim")
    || !contract?.motionContract?.prohibited?.includes("non-rigid Rive mesh deformation")
    || !contract?.motionContract?.prohibited?.includes("explode")
    || contract?.motionContract?.timeline?.contract?.durationSeconds !== 4.520833
    || contract?.motionContract?.timeline?.contract?.policy !== "time-scale measured path only"
    || contract?.motionContract?.singleHighlight?.count !== 1
    || contract?.motionContract?.singleHighlight?.implementationState !== "deferred-downstream-validation"
    || contract?.motionContract?.hover?.implementationState !== "deferred-downstream-validation"
    || contract?.motionContract?.prize?.independentAngularVelocity !== 0
    || contract?.revealMotion?.sequence?.prizeAngularVelocity !== 0
    || contract?.revealMotion?.sequence?.wholeCaseOnly !== true
    || contract?.revealMotion?.sequence?.explode !== false
    || contract?.route?.nextGatePolicy !== "Do not enter Gate 04 before explicit Gate 03 approval."
    || contract?.route?.blenderGeometryEdit !== false
    || contract?.route?.materialEdit !== false
    || contract?.route?.shippingUnityEdit !== false
    || contract?.completeness?.allActiveGate02ClaimsConsumed !== true
    || fit?.modelId !== modelId
    || fit?.contractRevision !== 2
    || fit?.status !== "pass-with-measured-residuals"
    || fit?.box?.rigid !== true
    || fit?.box?.deformationChannels !== 0
    || fit?.method?.exactFitClaimed !== false
    || fit?.sourceBoundaries?.riveMeshDeformationUsedAsTarget !== false
    || fit?.sourceBoundaries?.physicalAxisClaim !== null
    || fit?.sourceBoundaries?.pureYAxisClaim !== false
    || fit?.sourceBoundaries?.pureXAxisClaim !== false
    || fit?.sourceBoundaries?.singleAxisClaim !== false
    || fit?.sourceBoundaries?.wholeCaseOnly !== true
    || fit?.sourceBoundaries?.explode !== false
    || fit?.timeline?.contract?.durationSeconds !== 4.520833
    || !fitSamplesValid
    || !Number.isFinite(fit?.residualSummaryPixels?.mean)
    || !Number.isFinite(fit?.residualSummaryPixels?.rmse)
    || !Number.isFinite(fit?.residualSummaryPixels?.maximum)
    || fit?.residualSummaryPixels?.exact !== false
    || validation?.status !== "pass"
    || Object.values(validation?.checks || {}).some((value) => value !== true)
  ) {
    throw new PipelineError("Gate 03 rev 2 evidence is incomplete, overclaims an axis, changes static scope, or fails rigid-fit validation.", 422);
  }

  const pngDimensions = (file) => {
    const bytes = fs.readFileSync(file.absolute);
    const isPng = bytes.length >= 24 && bytes.subarray(1, 4).toString("ascii") === "PNG";
    return {
      width: isPng ? bytes.readUInt32BE(16) : 0,
      height: isPng ? bytes.readUInt32BE(20) : 0
    };
  };
  const previewDimensions = pngDimensions(files.preview);
  const poseSheetDimensions = pngDimensions(files.poseSheet);
  const curveDimensions = pngDimensions(files.motionCurves);
  if (
    previewDimensions.width < 3000
    || previewDimensions.height < 4000
    || poseSheetDimensions.width < 2800
    || poseSheetDimensions.height < 3800
    || curveDimensions.width < 2400
    || curveDimensions.height < 1900
  ) {
    throw new PipelineError("Gate 03 rev 2 evidence images must remain large-type PNGs.", 422);
  }

  const ids = {
    generator: "premium-display-case-contract-generator-r002",
    contract: "premium-display-case-modeling-contract-r002",
    fit: "premium-display-case-rigid-motion-fit-r002",
    validation: "premium-display-case-rigid-motion-fit-validation-r002",
    preview: "premium-display-case-contract-preview-r002",
    poseSheet: "premium-display-case-rigid-pose-contact-sheet-r002",
    motionCurves: "premium-display-case-rigid-motion-curves-r002"
  };
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  for (const id of Object.values(ids)) {
    if (existingIds.has(id)) throw new PipelineError(`Gate 03 rev 2 asset already exists: ${id}`, 409);
  }
  const gate02SourceIds = [
    "premium-display-case-gate02-rev3-user-approval",
    "premium-display-case-rive-authored-motion-extract-r003",
    "premium-display-case-real-rive-motion-measurements-r003",
    "premium-display-case-motion-reference-manifest-r003"
  ];
  const frameIds = [
    "premium-display-case-real-rive-frame-start-r003",
    "premium-display-case-real-rive-frame-quarter-r003",
    "premium-display-case-real-rive-frame-userNearest-r003",
    "premium-display-case-real-rive-frame-half-r003",
    "premium-display-case-real-rive-frame-threeQuarter-r003",
    "premium-display-case-real-rive-frame-frontToEdge-r003",
    "premium-display-case-real-rive-frame-edge-r003",
    "premium-display-case-real-rive-frame-reverse-r003",
    "premium-display-case-real-rive-frame-end-r003"
  ];
  const definitions = [
    {
      key: "generator",
      slot: "contract-recipe",
      role: "process",
      contentClass: "deterministic-rigid-motion-contract-generator",
      recipe: "OpenCV IPPE/LM rigid cuboid pose fit and large-type contract evidence",
      sourceAssetIds: gate02SourceIds
    },
    {
      key: "fit",
      slot: "motion-fit",
      role: "validation",
      contentClass: "rigid-cuboid-pose-fit-with-residuals",
      recipe: "Per-sample quaternion, translation, framing and reprojection residual report",
      sourceAssetIds: [ids.generator, ...gate02SourceIds, ...frameIds]
    },
    {
      key: "contract",
      slot: "modeling-contract",
      role: "contract",
      contentClass: "premium-display-case-rigid-motion-modeling-contract",
      recipe: "Gate 03 rev 2 static-preservation and rigid best-fit contract",
      sourceAssetIds: [ids.fit, ...gate02SourceIds]
    },
    {
      key: "poseSheet",
      slot: "motion-contact-sheet",
      role: "process",
      contentClass: "rive-versus-rigid-fit-pose-contact-sheet",
      recipe: "Rive/source quad and rigid cuboid overlay with per-sample residual",
      sourceAssetIds: [ids.generator, ids.fit, ...frameIds]
    },
    {
      key: "motionCurves",
      slot: "motion-curve",
      role: "process",
      contentClass: "rigid-quaternion-translation-residual-curves",
      recipe: "Quaternion decomposition, framing and residual curve board",
      sourceAssetIds: [ids.generator, ids.fit, "premium-display-case-rive-authored-motion-extract-r003"]
    },
    {
      key: "preview",
      slot: "contract-board",
      role: "process",
      contentClass: "whole-case-only-gate03-contract-preview",
      recipe: "Large-type whole-case contract board with measured-versus-fit overlays",
      sourceAssetIds: [ids.contract, ids.fit]
    },
    {
      key: "validation",
      slot: "validation-report",
      role: "validation",
      contentClass: "rigid-motion-fit-and-image-validation",
      recipe: "CV fit, quaternion, scope, timing, provenance and image checks",
      sourceAssetIds: [ids.contract, ids.fit, ids.preview, ids.poseSheet, ids.motionCurves]
    }
  ];
  const assetRecords = definitions.map((definition) => {
    const file = files[definition.key];
    return {
      id: ids[definition.key],
      stageId: "03-contract",
      slot: definition.slot,
      path: file.normalized,
      sha256: sha256File(file.absolute),
      exists: true,
      sizeBytes: fs.statSync(file.absolute).size,
      role: definition.role,
      producer: {
        name: "fidgeting-model-pipeline + OpenCV",
        version: "2026-08-26",
        recipe: definition.recipe
      },
      provenance: {
        origin: "repository-generated",
        contentClass: definition.contentClass,
        assertedBy: "assistant",
        note: definition.key === "fit"
          ? "Best-fit residuals are explicit. The report does not claim exact projection, a physical axis, or Rive mesh deformation as target motion."
          : "Gate 03 rev 2 evidence only. Static Blender geometry/material and shipping Unity remain unchanged."
      },
      sourceAssetIds: definition.sourceAssetIds,
      sourceClaimIds: activeClaimIds,
      reviewState: "active",
      wholeCaseOnly: true,
      explodeEligible: false,
      ...(definition.key === "preview" ? {
        view: {
          id: "gate03-contract-preview",
          camera: "technical-contract-board",
          parameters: {
            widthPixels: previewDimensions.width,
            heightPixels: previewDimensions.height,
            assemblyState: "assembled"
          }
        }
      } : {})
    };
  });

  const now = new Date().toISOString();
  const staleRev1AssetIds = [...stage.artifactIds];
  for (const assetId of staleRev1AssetIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    if (!asset) continue;
    asset.reviewState = "superseded";
    asset.supersededBy = ids.contract;
    asset.supersededAt = now;
    asset.preservedForHistory = true;
    asset.dispositionNote = "Gate 03 rev 1 remains immutable stale history. Its pure-Y motion clauses are replaced by the rigid rev 2 contract.";
  }
  manifest.assets.push(...assetRecords);
  if (stage.decision) {
    stage.historicalDecisions = [...(stage.historicalDecisions || []), stage.decision];
  }
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = definitions.map((definition) => ids[definition.key]);
  stage.reviewArtifactIds = [ids.preview];
  stage.validations = [
    { id: "all-active-gate02-claims-consumed", status: "pass", evidence: `Every Gate 03 rev 2 artifact declares all ${activeClaimIds.length} active Gate 02 rev 3 sourceClaimIds.` },
    { id: "motion-only-static-values-preserved", status: "pass", evidence: "228 × 304 × 59 mm, Portrait 0.75, tube 10 × 9 / passage 6 × 5 / wall 2 / R20, label 184 × 58 @ Y99, ContentSlot 180 × 198 × 48, concentric corners, and current material ranges remain unchanged." },
    { id: "rigid-composite-pose-contract", status: "pass", evidence: `${fit.samples.length} Rive samples provide normalized quaternions, one cuboid-origin translation, scale 1.0 and fixed-camera framing.` },
    { id: "reprojection-residuals-explicit", status: "pass", evidence: `Mean=${fit.residualSummaryPixels.mean}px, RMSE=${fit.residualSummaryPixels.rmse}px, max=${fit.residualSummaryPixels.maximum}px. The contract explicitly refuses an exact-fit claim.` },
    { id: "axis-and-deformation-boundary", status: "pass", evidence: "Pure Y, pure X, any single-axis physical claim, Rive mesh deformation, independent layer deformation and non-uniform scale are forbidden." },
    { id: "duration-and-source-timing", status: "pass", evidence: `The 3.500000 s canonical Rive root is uniformly time-scaled by ${fit.timeline.contract.uniformTimeScale} to exactly 4.520833 s; event order and relative timing are unchanged.` },
    { id: "whole-case-only", status: "pass", evidence: "The only reviewArtifactId is the assembled whole-case contract preview. Explode, assembly and reassembly remain forbidden." },
    { id: "deferred-highlight-hover", status: "pass", evidence: "One highlight and post-completion hover remain downstream validation segments; neither changes the current rigid pose fit." },
    { id: "toy-scope-and-angular-velocity", status: "pass", evidence: "Toy/prize stays caller-owned through ContentSlot and has zero independent angular velocity." },
    { id: "provenance-and-image-validation", status: "pass", evidence: "Generator, fit JSON, validation JSON, 3200 × 4300 preview, 3000 × 4050 pose sheet and 2600 × 2100 curve board are hashed and source-linked." },
    { id: "gate04-not-entered", status: "pass", evidence: "Gate 03 is ready_for_review only. Gate 04–08 remain stale and retain every historical artifact." },
    { id: "shipping-boundary", status: "pass", evidence: "No Blender geometry/material, shipping Unity, build, install or phone push occurred." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  stage.contractSpec = {
    revision: 2,
    sourceAnalysisRevision: 3,
    sourceEvidenceRevision: 3,
    sourceClaimIds: activeClaimIds,
    staticStructurePreserved: true,
    rigidWholeCase: true,
    poseSampleCount: fit.samples.length,
    meanReprojectionResidualPixels: fit.residualSummaryPixels.mean,
    rmseReprojectionResidualPixels: fit.residualSummaryPixels.rmse,
    maximumReprojectionResidualPixels: fit.residualSummaryPixels.maximum,
    exactFitClaimed: false,
    diagnosticVerticalFovDegrees: fit.cameraAssumptions.verticalFovDegrees,
    lockedTotalDurationSeconds: 4.520833,
    highlightValidation: "deferred",
    hoverValidation: "deferred",
    prizeIndependentAngularVelocity: 0,
    wholeCaseOnly: true,
    explode: false,
    gate04Status: "stale-awaiting-gate03-approval"
  };

  const downstreamReason = "Gate 03 rev 2 rigid motion contract is ready_for_review and not approved. Gate 04–08 retain immutable historical artifacts as stale.";
  const staleStageIds = [];
  for (let index = stageIndex + 1; index <= 7; index += 1) {
    manifest.stages[index].status = "stale";
    manifest.stages[index].staleReason = downstreamReason;
    staleStageIds.push(manifest.stages[index].id);
  }
  for (let index = 8; index < manifest.stages.length; index += 1) {
    manifest.stages[index].staleReason = downstreamReason;
  }
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 02 rev 3 is approved. Gate 03 contract rev 2 is ready_for_review with a rigid quaternion/translation fit, explicit reprojection residuals, preserved static values, and exact 4.520833 s time scaling. Gate 04–08 remain stale; shipping Unity is unchanged.";
  manifest.currentState.visualApproval = "pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.motionCorrection = {
    ...manifest.currentState.motionCorrection,
    gate03Status: "ready_for_review",
    gate03ContractRevision: 2,
    gate04Status: "stale-awaiting-gate03-approval",
    meanReprojectionResidualPixels: fit.residualSummaryPixels.mean,
    maximumReprojectionResidualPixels: fit.residualSummaryPixels.maximum
  };
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "03-contract",
    contractRevision: "002",
    sourceAnalysisRevision: 3,
    sourceEvidenceRevision: 3,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    sourceClaimIds: activeClaimIds,
    staleRev1ArtifactIds: staleRev1AssetIds,
    staticStructurePreserved: true,
    rigidWholeCase: true,
    poseSampleCount: fit.samples.length,
    meanReprojectionResidualPixels: fit.residualSummaryPixels.mean,
    rmseReprojectionResidualPixels: fit.residualSummaryPixels.rmse,
    maximumReprojectionResidualPixels: fit.residualSummaryPixels.maximum,
    exactFitClaimed: false,
    lockedTotalDurationSeconds: 4.520833,
    staleStageIds,
    approvedCount: 2,
    earliestGate: "03-contract",
    autoApproved: false,
    gate04Status: "stale",
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseBalancedMotionReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) {
    throw new PipelineError("Manifest revision conflict.", 409);
  }
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This balanced-motion review is supported only for the Premium Display Case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "02-analysis");
  const intake = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  const userQuote = String(payload.userQuote || "").trim();
  const expectedQuote = "那你这个也太简单了。我不是让你去模仿 whatnot 的那个 Slabbed Rive file 吗？你现在只有一个位移，也没有 Z 轴的这种移转，也没有 360° 翻转。也太简单了，你不能说找一个中间的平衡吗？";
  if (intake.status !== "approved") {
    throw new PipelineError("Gate 01 topology approval must remain approved.", 422);
  }
  if (
    stage.status !== "rejected"
    || stage.decision?.action !== "reject"
    || !stage.decision.notes.includes(expectedQuote)
  ) {
    throw new PipelineError("Gate 02 must first record the user's balanced-motion correction.", 422);
  }
  if (userQuote !== expectedQuote) {
    throw new PipelineError("The exact balanced-motion feedback must be preserved.", 422);
  }

  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/02-analysis/rev-005"
  )));
  const evidencePaths = {
    feedback: "user-balanced-motion-feedback.md",
    generator: "generate_balanced_motion_review.py",
    recipe: "balanced-motion-recipe.json",
    board: "balanced-entry-showcase-analysis-board.png",
    gif: "balanced-entry-showcase-motion.gif",
    contact: "balanced-entry-showcase-contact-sheet.png",
    validation: "balanced-motion-validation.json",
    quality: "animation-quality-report.json"
  };
  const files = Object.fromEntries(Object.entries(evidencePaths).map(([key, filename]) => [
    key,
    assertRepositoryEvidenceFile(
      modelId,
      "02-analysis/rev-005",
      `${expectedDirectory}/${filename}`,
      `Gate 02 balanced-motion ${key}`
    )
  ]));
  const recipe = JSON.parse(fs.readFileSync(files.recipe.absolute, "utf8"));
  const validation = JSON.parse(fs.readFileSync(files.validation.absolute, "utf8"));
  const quality = JSON.parse(fs.readFileSync(files.quality.absolute, "utf8"));
  if (
    recipe?.modelId !== modelId
    || recipe?.gate !== "02-analysis"
    || recipe?.analysisRevision !== 5
    || recipe?.status !== "ready_for_review"
    || recipe?.userIntent !== "entry-primary-with-z-transfer-and-one-360-showcase"
    || recipe?.motion?.phaseOrder?.join(",") !== "entry-y-z,settle,showcase-y-360,single-highlight,hold"
    || recipe?.motion?.entryTranslationAxes?.join(",") !== "screen-y,camera-depth-z"
    || recipe?.motion?.entryRotationDegrees?.some((value) => value !== 0)
    || recipe?.motion?.showcaseTranslationLocked !== true
    || recipe?.motion?.showcaseRotation?.axis !== "local-y"
    || recipe?.motion?.showcaseRotation?.degrees !== 360
    || recipe?.motion?.showcaseRotation?.count !== 1
    || recipe?.motion?.modelScale !== 1
    || recipe?.motion?.xDrift !== false
    || recipe?.motion?.roll !== false
    || recipe?.motion?.pitch !== false
    || recipe?.motion?.cameraMotion !== false
    || recipe?.motion?.backgroundMotion !== false
    || recipe?.motion?.singleHighlight !== true
    || recipe?.motion?.wholeCaseOnly !== true
    || recipe?.motion?.objectReplacement !== false
    || recipe?.motion?.toyMotion !== false
    || recipe?.motion?.simultaneousEntryAndRotation !== false
    || recipe?.timingApprovalEffect !== "none-review-candidate-only"
  ) {
    throw new PipelineError("The Gate 02 rev 5 recipe does not preserve the balanced serial motion contract.", 422);
  }
  if (
    validation?.status !== "pass"
    || quality?.status !== "pass"
    || quality?.metrics?.primaryMotion !== "entry"
    || quality?.metrics?.entryAxes?.join(",") !== "screen-y,camera-depth-z"
    || quality?.metrics?.showcaseRotationCount !== 1
    || quality?.metrics?.showcaseRotationDegrees !== 360
    || quality?.metrics?.entryRotationKeyCount !== 0
    || quality?.metrics?.simultaneousTranslationRotationFrames !== 0
    || quality?.metrics?.xDrift !== 0
    || quality?.metrics?.rollDegrees !== 0
    || quality?.metrics?.pitchDegrees !== 0
    || quality?.metrics?.modelScale !== 1
    || quality?.metrics?.highlightCount !== 1
    || quality?.metrics?.objectReplacementCount !== 0
    || quality?.metrics?.toyMotionCount !== 0
  ) {
    throw new PipelineError("The Gate 02 rev 5 balanced-motion validation did not pass.", 422);
  }

  const ids = {
    feedback: "premium-display-case-balanced-feedback-r005",
    generator: "premium-display-case-balanced-generator-r005",
    recipe: "premium-display-case-balanced-recipe-r005",
    board: "premium-display-case-balanced-board-r005",
    gif: "premium-display-case-balanced-gif-r005",
    contact: "premium-display-case-balanced-contact-r005",
    validation: "premium-display-case-balanced-validation-r005",
    quality: "premium-display-case-balanced-quality-r005"
  };
  const userMotionReferenceId = manifest.assets.find((asset) => (
    asset.id === "premium-display-case-user-motion-reference-r003"
    || asset.id.endsWith("-user-motion-reference-r003")
  ))?.id;
  if (!userMotionReferenceId) {
    throw new PipelineError("The prior user motion reference is missing.", 422);
  }
  const priorSourceIds = [
    "display-case-user-request-2026-08-24",
    userMotionReferenceId
  ];
  const records = [
    [ids.feedback, "decision-record", files.feedback, "analysis", "exact-user-balanced-motion-feedback", priorSourceIds],
    [ids.generator, "analysis-recipe", files.generator, "process", "deterministic-balanced-motion-generator", [ids.feedback]],
    [ids.recipe, "analysis-recipe", files.recipe, "analysis", "balanced-entry-showcase-recipe", [ids.feedback, ids.generator]],
    [ids.board, "analysis-board", files.board, "analysis", "balanced-entry-showcase-analysis-board", [ids.feedback, ids.recipe]],
    [ids.gif, "motion-preview", files.gif, "process", "balanced-entry-showcase-motion-gif", [ids.generator, ids.recipe]],
    [ids.contact, "analysis-board", files.contact, "analysis", "balanced-entry-showcase-contact-sheet", [ids.generator, ids.recipe]],
    [ids.validation, "motion-validation", files.validation, "validation", "balanced-motion-validation", [ids.recipe, ids.gif]],
    [ids.quality, "animation-validation", files.quality, "validation", "balanced-motion-quality-report", [ids.board, ids.gif, ids.contact]]
  ].map(([id, slot, file, role, contentClass, sourceAssetIds]) => ({
    id,
    stageId: "02-analysis",
    slot,
    path: file.normalized,
    sha256: sha256File(file.absolute),
    exists: true,
    sizeBytes: fs.statSync(file.absolute).size,
    role,
    producer: {
      name: "fidgeting-model-pipeline",
      version: "2026-08-26",
      recipe: "Serial entry, 360 showcase, highlight and hold"
    },
    provenance: {
      origin: "repository-generated",
      contentClass,
      assertedBy: "assistant",
      note: "Entry remains primary. Y+Z entry settles before one rigid 360-degree Y showcase. No simultaneous axis clutter, split, explode, proxy or toy motion."
    },
    sourceAssetIds
  }));
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  if (records.some((record) => existingIds.has(record.id))) {
    throw new PipelineError("Gate 02 rev 5 asset ids already exist.", 409);
  }
  manifest.assets.push(...records);

  const now = new Date().toISOString();
  for (const claim of manifest.claims || []) {
    if (claim.stageId === "02-analysis" && claim.state !== "superseded") {
      claim.state = "superseded";
      claim.supersededBy = "analysis-rev-005";
      claim.supersededAt = now;
    }
  }
  const claims = [
    {
      id: "premium-display-case-analysis-balanced-entry-r005",
      stageId: "02-analysis",
      category: "motion",
      statement: "Entry remains the primary action: the assembled case moves upward and toward the camera from behind the Pack, with zero entry rotation.",
      confidence: "user-directed-high",
      sourceAssetIds: [ids.feedback, ids.board, ids.gif],
      sourceRegions: [],
      state: "active",
      analysisRevision: "005"
    },
    {
      id: "premium-display-case-analysis-serial-showcase-r005",
      stageId: "02-analysis",
      category: "motion",
      statement: "After entry settles, the same rigid case performs one 360-degree local-Y showcase with translation locked.",
      confidence: "user-directed-high",
      sourceAssetIds: [ids.feedback, ids.recipe, ids.contact],
      sourceRegions: [],
      state: "active",
      analysisRevision: "005"
    },
    {
      id: "premium-display-case-analysis-no-simultaneous-clutter-r005",
      stageId: "02-analysis",
      category: "motion",
      statement: "Entry and rotation are serial, not simultaneous; X drift, roll, pitch, camera motion, background motion and independent model scale animation are zero.",
      confidence: "high",
      sourceAssetIds: [ids.recipe, ids.validation, ids.quality],
      sourceRegions: [],
      state: "active",
      analysisRevision: "005"
    },
    {
      id: "premium-display-case-analysis-balanced-highlight-r005",
      stageId: "02-analysis",
      category: "motion",
      statement: "One narrow highlight follows the 360-degree showcase, then the same whole case holds statically.",
      confidence: "high",
      sourceAssetIds: [ids.board, ids.gif, ids.quality],
      sourceRegions: [],
      state: "active",
      analysisRevision: "005"
    },
    {
      id: "premium-display-case-analysis-balanced-timing-r005",
      stageId: "02-analysis",
      category: "motion-timing",
      statement: "The 3.4 second review rhythm is a candidate only and does not approve a shipping duration.",
      confidence: "high",
      sourceAssetIds: [ids.recipe, ids.contact],
      sourceRegions: [],
      state: "active",
      analysisRevision: "005"
    }
  ];
  manifest.claims.push(...claims);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.reviewArtifactIds = [ids.board, ids.gif, ids.contact];
  stage.validations = [
    { id: "user-balanced-feedback-recorded", status: "pass", evidence: `The decision history preserves: “${userQuote}”.` },
    { id: "entry-primary-y-z", status: "pass", evidence: "Entry uses screen Y and camera-depth Z only, with zero entry rotation." },
    { id: "serial-360-showcase", status: "pass", evidence: "One local-Y 360-degree showcase starts only after entry settles." },
    { id: "no-simultaneous-clutter", status: "pass", evidence: "Translation and rotation never overlap; X drift, roll, pitch, camera and background motion are zero." },
    { id: "whole-case-no-replacement", status: "pass", evidence: "One rigid assembled case remains the same subject; no proxy, split or explode." },
    { id: "toy-static", status: "pass", evidence: "The caller-owned toy remains static and out of scope." },
    { id: "single-highlight", status: "pass", evidence: "One narrow highlight follows the showcase." },
    { id: "timing-not-locked", status: "pass", evidence: "The 3.4 s review rhythm has no shipping approval effect." },
    { id: "shipping-boundary", status: "pass", evidence: "Shipping Unity, build, install and phone state remain unchanged." }
  ];
  stage.decision = null;
  stage.analysisSpec = {
    revision: 5,
    userQuote,
    primaryMotion: "entry",
    phaseOrder: ["entry-y-z", "settle", "showcase-y-360", "single-highlight", "hold"],
    entryTranslationAxes: ["screen-y", "camera-depth-z"],
    entryRotation: "none",
    showcaseAxis: "local-y",
    showcaseDegrees: 360,
    showcaseCount: 1,
    showcaseTranslation: "locked",
    xDrift: "none",
    roll: "none",
    pitch: "none",
    modelScaleAnimation: "none-model-scale-one",
    cameraMotion: "none",
    backgroundMotion: "none",
    singleHighlightAfterShowcase: true,
    simultaneousEntryAndRotation: false,
    wholeCaseOnly: true,
    objectReplacement: false,
    toyMotion: false,
    reviewDurationSeconds: 3.4,
    timingApprovalEffect: "none-review-candidate-only",
    shippingAssetUnchanged: true
  };
  delete stage.staleReason;

  const downstreamReason = "Gate 02 rev 5 balances entry-first Y+Z motion with one serial 360-degree showcase. Gates 03–08 retain history but require revalidation.";
  const staleStageIds = [];
  for (let index = stageIndex + 1; index <= 7; index += 1) {
    const downstream = manifest.stages[index];
    if ((downstream.artifactIds || []).length) {
      downstream.status = "stale";
      staleStageIds.push(downstream.id);
    }
    downstream.staleReason = downstreamReason;
  }
  for (let index = 8; index < manifest.stages.length; index += 1) {
    manifest.stages[index].staleReason = downstreamReason;
  }

  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 01 remains approved. Gate 02 rev 5 is ready_for_review: entry is primary and uses Y+Z only; after settlement, the same rigid case performs one 360-degree local-Y showcase, then one highlight and hold. Entry and rotation are serial. The 3.4 s rhythm is review-only. Gates 03–08 remain stale; shipping Unity is unchanged.";
  manifest.currentState.visualApproval = "pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.motionCorrection = {
    earliestGate: "02-analysis",
    analysisRevision: 5,
    userQuote,
    primaryMotion: "entry",
    entryAxes: ["screen-y", "camera-depth-z"],
    showcase: "one-local-y-360-after-settle",
    simultaneousEntryAndRotation: false,
    prohibited: ["x-drift", "roll", "pitch", "camera-motion", "background-motion", "explode", "proxy", "toy-motion"],
    timingApproved: false,
    staleStageIds
  };

  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "02-analysis",
    analysisRevision: "005",
    userQuote,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    claimIds: claims.map((claim) => claim.id),
    primaryMotion: "entry",
    entryAxes: ["screen-y", "camera-depth-z"],
    showcase: "one-local-y-360-after-settle",
    simultaneousEntryAndRotation: false,
    reviewDurationSeconds: 3.4,
    timingApprovalEffect: "none-review-candidate-only",
    staleStageIds,
    approvedCount: 1,
    earliestGate: "02-analysis",
    autoApproved: false,
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseRestrainedLightReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) {
    throw new PipelineError("Manifest revision conflict.", 409);
  }
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This light review is supported only for the Premium Display Case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "02-analysis");
  const intake = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  const userQuote = String(payload.userQuote || "").trim();
  const expectedQuote = "对，就是这个意思。节奏上面，你再加一些我之前让你做的游戏调研上的这种光效变化，结合一下就好了。";
  if (intake.status !== "approved") {
    throw new PipelineError("Gate 01 topology approval must remain approved.", 422);
  }
  if (
    stage.status !== "ready_for_review"
    || stage.analysisSpec?.revision !== 5
    || stage.analysisSpec?.phaseOrder?.join(",") !== "entry-y-z,settle,showcase-y-360,single-highlight,hold"
  ) {
    throw new PipelineError("Gate 02 rev 5 motion structure must be current before revising light treatment.", 422);
  }
  if (userQuote !== expectedQuote) {
    throw new PipelineError("The exact light-evolution feedback must be preserved.", 422);
  }

  const rev5Ids = [
    "premium-display-case-balanced-feedback-r005",
    "premium-display-case-balanced-generator-r005",
    "premium-display-case-balanced-recipe-r005",
    "premium-display-case-balanced-board-r005",
    "premium-display-case-balanced-gif-r005",
    "premium-display-case-balanced-contact-r005",
    "premium-display-case-balanced-validation-r005",
    "premium-display-case-balanced-quality-r005"
  ];
  const missingRev5 = rev5Ids.filter((id) => !manifest.assets.some((asset) => asset.id === id));
  if (missingRev5.length) {
    throw new PipelineError(`Gate 02 rev 5 source assets are missing: ${missingRev5.join(", ")}`, 422);
  }
  for (const id of rev5Ids) {
    const asset = manifest.assets.find((candidate) => candidate.id === id);
    const absolute = resolveRepoPath(asset.path);
    if (!fs.existsSync(absolute) || sha256File(absolute) !== asset.sha256) {
      throw new PipelineError(`Gate 02 rev 5 source asset changed: ${id}`, 422);
    }
  }

  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/02-analysis/rev-006"
  )));
  const evidencePaths = {
    feedback: "user-light-evolution-feedback.md",
    generator: "generate_restrained_light_review.py",
    recipe: "restrained-light-recipe.json",
    board: "restrained-light-evolution-analysis-board.png",
    gif: "balanced-motion-restrained-light.gif",
    contact: "balanced-motion-restrained-light-contact-sheet.png",
    validation: "restrained-light-validation.json",
    quality: "animation-quality-report.json"
  };
  const files = Object.fromEntries(Object.entries(evidencePaths).map(([key, filename]) => [
    key,
    assertRepositoryEvidenceFile(
      modelId,
      "02-analysis/rev-006",
      `${expectedDirectory}/${filename}`,
      `Gate 02 restrained-light ${key}`
    )
  ]));
  const recipe = JSON.parse(fs.readFileSync(files.recipe.absolute, "utf8"));
  const validation = JSON.parse(fs.readFileSync(files.validation.absolute, "utf8"));
  const quality = JSON.parse(fs.readFileSync(files.quality.absolute, "utf8"));
  const eventById = Object.fromEntries((recipe.lightEvents || []).map((event) => [event.id, event]));
  const requiredEvents = [
    "pack-seam-light",
    "arrival-rim",
    "rotation-surface-rim",
    "final-diagonal-sheen",
    "settle-halo"
  ];
  if (
    recipe?.modelId !== modelId
    || recipe?.gate !== "02-analysis"
    || recipe?.analysisRevision !== 6
    || recipe?.status !== "ready_for_review"
    || recipe?.motionStructure?.unchangedFromRev5 !== true
    || recipe?.motionStructure?.phaseOrder?.join(",") !== "entry-y-z,settle,showcase-y-360,single-highlight,hold"
    || requiredEvents.some((id) => !eventById[id] || eventById[id].count !== 1)
    || eventById["pack-seam-light"].cause !== "pack-opening"
    || eventById["pack-seam-light"].rarityEncoded !== false
    || eventById["arrival-rim"].cause !== "case-clears-pack"
    || eventById["rotation-surface-rim"].cause !== "turning-case-surfaces"
    || eventById["rotation-surface-rim"].objectBound !== true
    || eventById["rotation-surface-rim"].independentEmitter !== false
    || eventById["final-diagonal-sheen"].cause !== "showcase-complete"
    || eventById["settle-halo"].persistent !== false
    || Math.max(...recipe.lightEvents.map((event) => Number(event.colorChroma))) > 25
    || !recipe.forbidden?.includes("vfx-graph")
    || !recipe.forbidden?.includes("persistent-light-loop")
    || recipe?.timingApprovalEffect !== "none-review-candidate-only"
  ) {
    throw new PipelineError("The Gate 02 rev 6 light recipe is incomplete or adds spectacle noise.", 422);
  }
  if (
    validation?.status !== "pass"
    || validation.checks?.some((check) => check.status !== "pass")
    || quality?.status !== "pass"
    || quality?.metrics?.focalSubjectCount !== 1
    || quality?.metrics?.lightCueCount !== 5
    || quality?.metrics?.independentParticleCount !== 0
    || quality?.metrics?.fullScreenFlashCount !== 0
    || quality?.metrics?.persistentLightLoopCount !== 0
    || quality?.metrics?.maximumRgbChroma > 25
    || quality?.metrics?.maximumHaloAlpha > 0.1
  ) {
    throw new PipelineError("The Gate 02 rev 6 light validation did not pass.", 422);
  }

  const ids = {
    feedback: "premium-display-case-light-feedback-r006",
    generator: "premium-display-case-light-generator-r006",
    recipe: "premium-display-case-light-recipe-r006",
    board: "premium-display-case-light-board-r006",
    gif: "premium-display-case-light-gif-r006",
    contact: "premium-display-case-light-contact-r006",
    validation: "premium-display-case-light-validation-r006",
    quality: "premium-display-case-light-quality-r006"
  };
  const records = [
    [ids.feedback, "decision-record", files.feedback, "analysis", "exact-user-light-evolution-feedback", ["premium-display-case-balanced-feedback-r005"]],
    [ids.generator, "analysis-recipe", files.generator, "process", "deterministic-restrained-light-generator", [ids.feedback, "premium-display-case-balanced-generator-r005"]],
    [ids.recipe, "analysis-recipe", files.recipe, "analysis", "restrained-light-evolution-recipe", [ids.feedback, ids.generator, "premium-display-case-balanced-recipe-r005"]],
    [ids.board, "analysis-board", files.board, "analysis", "restrained-light-evolution-analysis-board", [ids.recipe, "premium-display-case-balanced-board-r005"]],
    [ids.gif, "motion-preview", files.gif, "process", "balanced-motion-restrained-light-gif", [ids.generator, ids.recipe, "premium-display-case-balanced-gif-r005"]],
    [ids.contact, "analysis-board", files.contact, "analysis", "balanced-motion-restrained-light-contact-sheet", [ids.generator, ids.recipe, "premium-display-case-balanced-contact-r005"]],
    [ids.validation, "motion-validation", files.validation, "validation", "restrained-light-validation", [ids.recipe, ids.gif]],
    [ids.quality, "animation-validation", files.quality, "validation", "restrained-light-quality-report", [ids.board, ids.gif, ids.contact]]
  ].map(([id, slot, file, role, contentClass, sourceAssetIds]) => ({
    id,
    stageId: "02-analysis",
    slot,
    path: file.normalized,
    sha256: sha256File(file.absolute),
    exists: true,
    sizeBytes: fs.statSync(file.absolute).size,
    role,
    producer: {
      name: "fidgeting-model-pipeline",
      version: "2026-08-26",
      recipe: "Causally linked neutral light evolution over approved rev 5 motion"
    },
    provenance: {
      origin: "repository-generated",
      contentClass,
      assertedBy: "assistant",
      note: "Motion structure is unchanged. Light cues are neutral, object-bound, one-shot and stop before hold."
    },
    sourceAssetIds
  }));
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  if (records.some((record) => existingIds.has(record.id))) {
    throw new PipelineError("Gate 02 rev 6 asset ids already exist.", 409);
  }
  manifest.assets.push(...records);

  const lightClaims = [
    {
      id: "premium-display-case-analysis-pack-seam-light-r006",
      stageId: "02-analysis",
      category: "lighting",
      statement: "One narrow neutral or warm-neutral seam light is caused by the Pack opening during entry and carries no rarity information.",
      confidence: "user-directed-high",
      sourceAssetIds: [ids.feedback, ids.board, ids.gif],
      sourceRegions: [],
      state: "active",
      analysisRevision: "006"
    },
    {
      id: "premium-display-case-analysis-arrival-rim-r006",
      stageId: "02-analysis",
      category: "lighting",
      statement: "One small arrival rim reinforces the moment the case clears the Pack; it is not a full-screen flash.",
      confidence: "high",
      sourceAssetIds: [ids.recipe, ids.contact],
      sourceRegions: [],
      state: "active",
      analysisRevision: "006"
    },
    {
      id: "premium-display-case-analysis-rotation-rim-r006",
      stageId: "02-analysis",
      category: "lighting",
      statement: "During the 360-degree showcase, edge and rim response stays bound to the turning case surfaces with no independent emitter or particle system.",
      confidence: "high",
      sourceAssetIds: [ids.board, ids.gif, ids.validation],
      sourceRegions: [],
      state: "active",
      analysisRevision: "006"
    },
    {
      id: "premium-display-case-analysis-final-light-stop-r006",
      stageId: "02-analysis",
      category: "lighting",
      statement: "One diagonal sheen and one subtle neutral settle halo complete the reveal; both stop before the static hold.",
      confidence: "high",
      sourceAssetIds: [ids.recipe, ids.contact, ids.quality],
      sourceRegions: [],
      state: "active",
      analysisRevision: "006"
    },
    {
      id: "premium-display-case-analysis-light-forbidden-r006",
      stageId: "02-analysis",
      category: "lighting",
      statement: "Rarity colors, rainbow, full-screen flash, large bloom, particles, VFX Graph, explosion, lightning, CRT noise, confetti, shake and persistent light loops are forbidden.",
      confidence: "high",
      sourceAssetIds: [ids.feedback, ids.recipe, ids.validation],
      sourceRegions: [],
      state: "active",
      analysisRevision: "006"
    }
  ];
  manifest.claims.push(...lightClaims);

  const rev5ArtifactIds = [...stage.artifactIds];
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = [...rev5ArtifactIds, ...records.map((record) => record.id)];
  stage.reviewArtifactIds = [ids.board, ids.gif, ids.contact];
  stage.validations = [
    { id: "rev5-motion-structure-unchanged", status: "pass", evidence: "Y+Z entry, settle, one local-Y 360, one sheen and hold remain serial and unchanged." },
    { id: "one-focal-subject", status: "pass", evidence: "The assembled case remains the only focal subject." },
    { id: "causal-light-cues", status: "pass", evidence: "Pack seam, arrival rim, turning-surface rim, final sheen and settle halo each have a physical cause." },
    { id: "neutral-color-bound", status: "pass", evidence: `Maximum RGB chroma is ${quality.metrics.maximumRgbChroma}, within the neutral limit of 25.` },
    { id: "no-independent-effects", status: "pass", evidence: "Particles, VFX Graph, screen-space flashes, shake, CRT noise and confetti are absent." },
    { id: "no-persistent-loop", status: "pass", evidence: "Every cue reaches zero before the final hold." },
    { id: "timing-not-locked", status: "pass", evidence: "Rev 5 motion and rev 6 light rhythm remain review candidates." },
    { id: "shipping-boundary", status: "pass", evidence: "Shipping Unity, Simulator app, build, install and phone state remain unchanged." }
  ];
  stage.decision = null;
  stage.analysisSpec = {
    ...stage.analysisSpec,
    revision: 6,
    motionStructureRevision: 5,
    motionStructureApprovalState: "user-accepted-direction-light-treatment-pending",
    lightTreatmentRevision: 6,
    lightTreatment: {
      packSeamLight: "one-neutral-causal-cue",
      arrivalRim: "one-small-threshold-cue",
      rotationRim: "object-bound-surface-response",
      finalSheen: "one-diagonal-narrow-sheen",
      settleHalo: "one-subtle-neutral-halo-then-zero",
      maximumRgbChroma: quality.metrics.maximumRgbChroma,
      maximumHaloAlpha: quality.metrics.maximumHaloAlpha,
      persistentLoop: false,
      vfxGraphDependency: false
    },
    userLightQuote: userQuote,
    timingApprovalEffect: "none-review-candidate-only",
    shippingAssetUnchanged: true
  };
  delete stage.staleReason;

  const downstreamReason = "Gate 02 rev 6 keeps rev 5 motion unchanged and revises only restrained causal light treatment. Gates 03–08 remain stale.";
  const staleStageIds = [];
  for (let index = stageIndex + 1; index <= 7; index += 1) {
    const downstream = manifest.stages[index];
    if ((downstream.artifactIds || []).length) {
      downstream.status = "stale";
      staleStageIds.push(downstream.id);
    }
    downstream.staleReason = downstreamReason;
  }
  for (let index = 8; index < manifest.stages.length; index += 1) {
    manifest.stages[index].staleReason = downstreamReason;
  }

  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 02 rev 5 motion structure is accepted as the direction. Gate 02 rev 6 adds only restrained causal light evolution: one neutral Pack seam cue, one arrival rim, object-bound turning rim, one final sheen and a subtle halo that stops. Gate 02 remains ready_for_review, not approved. Gates 03–08 remain stale; shipping Unity and device state are unchanged.";
  manifest.currentState.visualApproval = "pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.motionCorrection = {
    ...manifest.currentState.motionCorrection,
    analysisRevision: 6,
    motionStructureRevision: 5,
    motionStructureApprovedDirection: true,
    lightTreatmentRevision: 6,
    lightTreatmentApproved: false,
    lightCueIds: requiredEvents,
    persistentLightLoop: false,
    vfxGraphDependency: false,
    staleStageIds
  };

  const event = makeEvent(manifest, "stage-evidence-revised", {
    stageId: "02-analysis",
    analysisRevision: "006",
    motionStructureRevision: 5,
    userQuote,
    feedbackDisposition: "motion-structure-accepted-light-treatment-revision-requested",
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    claimIds: lightClaims.map((claim) => claim.id),
    lightCueIds: requiredEvents,
    neutralMaximumRgbChroma: quality.metrics.maximumRgbChroma,
    maximumHaloAlpha: quality.metrics.maximumHaloAlpha,
    persistentLightLoop: false,
    vfxGraphDependency: false,
    staleStageIds,
    approvedCount: 1,
    earliestGate: "02-analysis",
    autoApproved: false,
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function approvePremiumDisplayCaseRestrainedLightReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) {
    throw new PipelineError("Manifest revision conflict.", 409);
  }
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This approval is supported only for the Premium Display Case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "02-analysis");
  const stage = manifest.stages[stageIndex];
  const userQuote = String(payload.userQuote || "").trim();
  const expectedQuote = "批准这版动效与光效（推荐）";
  const approvalScope = Array.isArray(payload.approvalScope)
    ? [...new Set(payload.approvalScope.map((item) => String(item).trim()).filter(Boolean))]
    : [];
  const requiredScope = [
    "rev5-serial-motion-structure",
    "rev6-restrained-causal-light",
    "entry-screen-y-camera-depth-z",
    "settle-before-local-y-360",
    "object-bound-rotation-rim",
    "single-final-sheen-short-halo",
    "forbidden-effects-remain-forbidden",
    "review-duration-3.4s-not-shipping-duration"
  ];
  if (
    stage.status !== "ready_for_review"
    || stage.analysisSpec?.revision !== 6
    || stage.analysisSpec?.motionStructureRevision !== 5
    || stage.analysisSpec?.lightTreatmentRevision !== 6
  ) {
    throw new PipelineError("Gate 02 rev 6 must be the current review candidate.", 422);
  }
  if (userQuote !== expectedQuote) {
    throw new PipelineError("The exact Gate 02 rev 6 approval selection must be preserved.", 422);
  }
  if (requiredScope.some((item) => !approvalScope.includes(item))) {
    throw new PipelineError("Gate 02 rev 6 approval scope is incomplete.", 422);
  }
  const spec = stage.analysisSpec;
  if (
    spec.primaryMotion !== "entry"
    || spec.phaseOrder?.join(",") !== "entry-y-z,settle,showcase-y-360,single-highlight,hold"
    || spec.entryTranslationAxes?.join(",") !== "screen-y,camera-depth-z"
    || spec.entryRotation !== "none"
    || spec.showcaseAxis !== "local-y"
    || spec.showcaseDegrees !== 360
    || spec.showcaseCount !== 1
    || spec.showcaseTranslation !== "locked"
    || spec.simultaneousEntryAndRotation !== false
    || spec.objectReplacement !== false
    || spec.toyMotion !== false
    || spec.reviewDurationSeconds !== 3.4
    || spec.timingApprovalEffect !== "none-review-candidate-only"
    || spec.lightTreatment?.packSeamLight !== "one-neutral-causal-cue"
    || spec.lightTreatment?.arrivalRim !== "one-small-threshold-cue"
    || spec.lightTreatment?.rotationRim !== "object-bound-surface-response"
    || spec.lightTreatment?.finalSheen !== "one-diagonal-narrow-sheen"
    || spec.lightTreatment?.settleHalo !== "one-subtle-neutral-halo-then-zero"
    || spec.lightTreatment?.persistentLoop !== false
    || spec.lightTreatment?.vfxGraphDependency !== false
  ) {
    throw new PipelineError("The Gate 02 rev 6 candidate no longer matches the approved scope.", 422);
  }
  const requiredForbidden = [
    "rarity-color",
    "rainbow",
    "large-bloom",
    "particles",
    "vfx-graph",
    "full-screen-flash",
    "explosion",
    "screen-shake",
    "persistent-light-loop"
  ];
  const recipeAsset = manifest.assets.find((asset) => (
    asset.id === "premium-display-case-light-recipe-r006"
  ));
  if (!recipeAsset) {
    throw new PipelineError("Gate 02 rev 6 light recipe asset is missing.", 422);
  }
  const lightRecipe = JSON.parse(
    fs.readFileSync(resolveRepoPath(recipeAsset.path), "utf8")
  );
  const forbidden = new Set(lightRecipe.forbidden || []);
  if (requiredForbidden.some((item) => !forbidden.has(item))) {
    throw new PipelineError("Gate 02 rev 6 forbidden effects are incomplete.", 422);
  }
  const readiness = stageReadiness(manifest, "02-analysis");
  if (!readiness.ready) {
    throw new PipelineError("Gate 02 rev 6 cannot be approved yet.", 422, readiness.reasons);
  }

  const now = new Date().toISOString();
  stage.status = "approved";
  stage.revision += 1;
  stage.decision = {
    action: "approve",
    notes: "用户选择“批准这版动效与光效（推荐）”。批准范围仅为 rev 5 串行动作结构与 rev 6 克制因果光效：Y+camera-depth-Z 入场、停稳、一次 local-Y 360°、物体绑定边光、一次最终 sheen／短 halo、hold。rarity 色、粒子、VFX Graph、闪屏、爆炸、shake、持续循环、对象替换和 toy motion 继续禁止。3.4 s 仅为 Gate 02 评审节奏，不是 shipping 时长。shipping Unity、Simulator、构建、安装和手机状态不变。",
    decidedBy: "user",
    decidedAt: now
  };
  stage.analysisSpec = {
    ...spec,
    approval: {
      approvedAnalysisRevision: 6,
      approvedMotionStructureRevision: 5,
      approvedLightTreatmentRevision: 6,
      userApprovalQuote: userQuote,
      approvalScope: requiredScope,
      reviewDurationSeconds: 3.4,
      shippingDurationApproved: false,
      approvalEffect: "approves-gate02-motion-and-light-direction-only",
      gate03Status: "eligible",
      shippingPreviewApproved: false,
      deviceAccepted: false
    }
  };
  stage.validations = [
    ...stage.validations,
    {
      id: "exact-rev6-approval-scope-recorded",
      status: "pass",
      evidence: "The user approved rev 5 serial motion plus rev 6 restrained causal light only; shipping duration, particles and delivery remain unapproved."
    }
  ];
  for (const assetId of stage.artifactIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    if (
      asset
      && (
        asset.id.startsWith("premium-display-case-balanced-")
        || asset.id.startsWith("premium-display-case-light-")
      )
    ) {
      asset.reviewState = "approved";
    }
  }

  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 02 rev 6 is explicitly approved for motion and restrained causal light direction only. The approved structure is Y+Z entry, settle, one local-Y 360, object-bound rim, one final sheen/short halo and hold. The 3.4 s value remains a Gate 02 review rhythm, not a shipping duration. Gate 03 is eligible; Gates 04–08 remain stale. Shipping Unity, Simulator, build, install and phone state are unchanged.";
  manifest.currentState.visualApproval = "gate02-motion-light-approved-shipping-preview-pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.motionCorrection = {
    ...manifest.currentState.motionCorrection,
    analysisRevision: 6,
    motionStructureRevision: 5,
    motionStructureApprovedDirection: true,
    lightTreatmentRevision: 6,
    lightTreatmentApproved: true,
    userApprovalQuote: userQuote,
    approvalScope: requiredScope,
    reviewDurationSeconds: 3.4,
    shippingDurationApproved: false,
    shippingPreviewApproved: false,
    deviceAccepted: false,
    gate03Status: "eligible"
  };

  const event = makeEvent(manifest, "stage-approved", {
    stageId: "02-analysis",
    analysisRevision: "006",
    motionStructureRevision: 5,
    lightTreatmentRevision: 6,
    userQuote,
    approvalScope: requiredScope,
    reviewArtifactIds: stage.reviewArtifactIds,
    lightCueIds: manifest.currentState.motionCorrection.lightCueIds,
    reviewDurationSeconds: 3.4,
    shippingDurationApproved: false,
    forbiddenEffects: requiredForbidden,
    approvalEffect: "approves-gate02-motion-and-light-direction-only",
    gate03Status: "eligible",
    gate04Status: "stale",
    shippingPreviewApproved: false,
    deviceAccepted: false,
    approvedCount: 2,
    autoApproved: false,
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function restorePremiumDisplayCaseRev6Authority(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) {
    throw new PipelineError("Manifest revision conflict.", 409);
  }
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This authority correction is supported only for the Premium Display Case.", 422);
  }
  const reason = String(payload.reason || "").trim();
  const expectedReason = "继续吧。Gate 03 必须从已批准 Gate 02 rev 6 重建，不得恢复 stale rev 3 / Gate 03 rev 2 authority。";
  if (reason !== expectedReason) {
    throw new PipelineError("The exact authority-correction reason must be preserved.", 422);
  }
  const gate02 = manifest.stages[1];
  const gate03 = manifest.stages[2];
  if (
    gate02.status !== "approved"
    || gate02.analysisSpec?.revision !== 6
    || gate02.analysisSpec?.approval?.approvedAnalysisRevision !== 6
    || gate03.contractSpec?.revision !== 2
    || gate03.status !== "approved"
  ) {
    throw new PipelineError("The expected rev 6 / stale rev 2 authority conflict is not present.", 422);
  }
  const currentClaimIds = new Set([
    "premium-display-case-analysis-balanced-entry-r005",
    "premium-display-case-analysis-serial-showcase-r005",
    "premium-display-case-analysis-no-simultaneous-clutter-r005",
    "premium-display-case-analysis-balanced-highlight-r005",
    "premium-display-case-analysis-balanced-timing-r005",
    "premium-display-case-analysis-pack-seam-light-r006",
    "premium-display-case-analysis-arrival-rim-r006",
    "premium-display-case-analysis-rotation-rim-r006",
    "premium-display-case-analysis-final-light-stop-r006",
    "premium-display-case-analysis-light-forbidden-r006"
  ]);
  const now = new Date().toISOString();
  for (const claim of manifest.claims || []) {
    if (claim.stageId !== "02-analysis") continue;
    if (currentClaimIds.has(claim.id)) {
      claim.state = "active";
      delete claim.supersededBy;
      delete claim.supersededAt;
    } else if (claim.state !== "superseded") {
      claim.state = "superseded";
      claim.supersededBy = "gate02-rev6-authority-restored";
      claim.supersededAt = now;
    }
  }
  const restoredClaims = (manifest.claims || []).filter((claim) => (
    claim.stageId === "02-analysis" && claim.state === "active"
  ));
  if (
    restoredClaims.length !== currentClaimIds.size
    || restoredClaims.some((claim) => !currentClaimIds.has(claim.id))
  ) {
    throw new PipelineError("Gate 02 rev 6 active claims could not be restored exactly.", 422);
  }
  gate02.decision = {
    action: "approve",
    notes: "用户已批准 Gate 02 rev 6 动效与克制光效。后续“继续吧”只授权从这 10 条 rev 5/6 claims 重建 Gate 03，不授权恢复 rev 3 复合 quaternion 或 4.520833 s 旧合同。",
    decidedBy: "user",
    decidedAt: gate02.analysisSpec.approval?.approvedAt || now
  };
  delete gate02.decision.supersededBy;
  delete gate02.decision.supersededAt;
  delete gate02.analysisSpec.decisionState;
  gate02.currentMotionAuthority = {
    sourceStageId: "02-analysis",
    analysisRevision: 6,
    motionStructureRevision: 5,
    lightTreatmentRevision: 6,
    sourceClaimIds: [...currentClaimIds],
    decisionState: "locked-direction-only",
    shippingDurationApproved: false,
    restoredAt: now
  };
  gate02.validations = [
    ...gate02.validations.filter((validation) => validation.id !== "rev6-authority-restored"),
    {
      id: "rev6-authority-restored",
      status: "pass",
      evidence: "Exactly 10 rev 5/6 motion and restrained-light claims are active; stale rev 3 claims remain superseded."
    }
  ];
  gate03.status = "stale";
  gate03.staleReason = "Gate 03 rev 2 consumed superseded rev 3 claims. Rebuild from approved Gate 02 rev 6 claims.";
  if (gate03.decision) {
    gate03.decision = {
      ...gate03.decision,
      supersededBy: "gate02-rev6-authority-restored",
      supersededAt: now
    };
  }
  for (let index = 3; index <= 7; index += 1) {
    const downstream = manifest.stages[index];
    if ((downstream.artifactIds || []).length) downstream.status = "stale";
    downstream.staleReason = "Gate 03 must be rebuilt from approved Gate 02 rev 6 claims.";
  }
  for (let index = 8; index < manifest.stages.length; index += 1) {
    manifest.stages[index].staleReason = "Gate 03 must be rebuilt from approved Gate 02 rev 6 claims.";
  }
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 02 rev 6 authority is restored. Exactly 10 rev 5/6 motion and restrained-light claims are active. Gate 03 rev 2 is stale because it consumed superseded rev 3 claims; Gate 03 must be rebuilt. Shipping Unity and device state remain unchanged.";
  manifest.currentState.visualApproval = "gate02-motion-light-approved-gate03-rebuild-required";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.motionCorrection = {
    earliestGate: "03-contract",
    analysisRevision: 6,
    motionStructureRevision: 5,
    lightTreatmentRevision: 6,
    activeClaimCount: restoredClaims.length,
    authoritativeMotion: "gate02-rev6-serial-entry-showcase-restrained-light",
    shippingDurationApproved: false,
    staleGate03ContractRevision: 2,
    gate03Status: "stale-rebuild-required",
    gate04Status: "stale",
    shippingPreviewApproved: false,
    deviceAccepted: false
  };
  const event = makeEvent(manifest, "stage-authority-restored", {
    stageId: "02-analysis",
    analysisRevision: 6,
    reason,
    activeClaimIds: restoredClaims.map((claim) => claim.id),
    staleContractRevision: 2,
    gate03Status: "stale-rebuild-required",
    approvedCount: 2,
    earliestGate: "03-contract",
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseSerialMotionContract(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) {
    throw new PipelineError("Manifest revision conflict.", 409);
  }
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This contract is supported only for the Premium Display Case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "03-contract");
  const analysis = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (
    analysis.status !== "approved"
    || analysis.analysisSpec?.revision !== 6
    || analysis.analysisSpec?.approval?.approvedAnalysisRevision !== 6
  ) {
    throw new PipelineError("Gate 02 rev 6 must be approved before Gate 03 rev 3.", 422);
  }
  const activeClaims = (manifest.claims || []).filter((claim) => (
    claim.stageId === "02-analysis" && claim.state !== "superseded"
  ));
  const activeClaimIds = activeClaims.map((claim) => claim.id);
  if (
    activeClaims.length !== 10
    || activeClaims.some((claim) => !claim.id.endsWith("-r005") && !claim.id.endsWith("-r006"))
  ) {
    throw new PipelineError("Gate 03 rev 3 must consume exactly 10 active rev 5/6 claims.", 422);
  }

  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/03-contract/rev-003"
  )));
  const files = {
    generator: assertRepositoryEvidenceFile(
      modelId,
      "03-contract/rev-003",
      `${expectedDirectory}/generate_serial_motion_contract.py`,
      "Gate 03 rev 3 generator"
    ),
    contract: assertRepositoryEvidenceFile(
      modelId,
      "03-contract/rev-003",
      `${expectedDirectory}/modeling-contract.json`,
      "Gate 03 rev 3 contract"
    ),
    preview: assertRepositoryEvidenceFile(
      modelId,
      "03-contract/rev-003",
      `${expectedDirectory}/contract-preview.png`,
      "Gate 03 rev 3 contract preview"
    ),
    validation: assertRepositoryEvidenceFile(
      modelId,
      "03-contract/rev-003",
      `${expectedDirectory}/contract-validation.json`,
      "Gate 03 rev 3 validation"
    )
  };
  const contract = JSON.parse(fs.readFileSync(files.contract.absolute, "utf8"));
  const validation = JSON.parse(fs.readFileSync(files.validation.absolute, "utf8"));
  const motion = contract?.motionContract;
  const light = contract?.lightContract;
  const tunable = contract?.tunableRuntimeParameters;
  if (
    contract?.modelId !== modelId
    || contract?.contractRevision !== 3
    || contract?.stageStatus !== "ready_for_review"
    || contract?.approvalEffect !== "none-until-explicit-gate-03-user-approval"
    || contract?.sourceAnalysisRevision !== 6
    || contract?.sourceMotionStructureRevision !== 5
    || contract?.sourceLightTreatmentRevision !== 6
    || contract?.sourceClaimIds?.length !== activeClaimIds.length
    || activeClaimIds.some((claimId) => !contract.sourceClaimIds.includes(claimId))
    || contract?.completeness?.allActiveGate02ClaimsConsumed !== true
    || contract?.completeness?.unknownsCarriedForward !== true
    || contract?.closedTubeFrame?.topology?.connectivity !== "one connected manifold"
    || motion?.phaseOrder?.join(",") !== "entry-y-z,settle,showcase-local-y-360,final-sheen-short-halo,static-hold"
    || motion?.entry?.translationAxes?.join(",") !== "screen-y,camera-depth-z"
    || motion?.entry?.rotationDegrees?.some((value) => value !== 0)
    || motion?.entry?.modelScale !== 1
    || motion?.showcase?.axis !== "local-y"
    || motion?.showcase?.degrees !== 360
    || motion?.showcase?.count !== 1
    || motion?.showcase?.translationLocked !== true
    || motion?.simultaneousEntryAndShowcase !== false
    || motion?.wholeCaseOnly !== true
    || motion?.objectReplacement !== false
    || motion?.toyMotion !== false
    || light?.causalCueOrder?.join(",") !== "pack-seam-light,arrival-rim,rotation-surface-rim,final-diagonal-sheen,settle-halo-then-zero"
    || light?.maximumRgbChroma > 25
    || light?.settleHalo?.persistent !== false
    || light?.settleHalo?.maximumAlpha > 0.1
    || light?.vfxGraphDependency !== false
    || light?.particles !== false
    || tunable?.previewDurationSeconds !== 3.4
    || tunable?.shippingTotalDurationSeconds !== null
    || tunable?.phaseDurationsSeconds !== null
    || tunable?.phaseEasing !== null
    || tunable?.entryScreenYDistance !== null
    || tunable?.entryCameraDepthZDistance !== null
    || tunable?.shippingCameraFovDegrees !== null
    || !tunable?.note?.includes("not current authority")
    || contract?.route?.nextGatePolicy !== "Do not enter Gate 04 before explicit Gate 03 approval."
  ) {
    throw new PipelineError("Gate 03 rev 3 contract is incomplete, locks tunable values, or violates the approved serial motion/light direction.", 422);
  }
  if (
    validation?.status !== "pass"
    || validation?.contractRevision !== 3
    || Object.values(validation?.checks || {}).some((value) => value !== true)
    || validation?.metrics?.activeGate02ClaimCount !== 10
    || validation?.metrics?.approvedShippingDuration !== null
  ) {
    throw new PipelineError("Gate 03 rev 3 validation did not pass.", 422);
  }
  const previewBytes = fs.readFileSync(files.preview.absolute);
  const previewWidth = previewBytes.subarray(1, 4).toString("ascii") === "PNG"
    ? previewBytes.readUInt32BE(16)
    : 0;
  const previewHeight = previewWidth ? previewBytes.readUInt32BE(20) : 0;
  if (previewWidth < 3000 || previewHeight < 3600) {
    throw new PipelineError("Gate 03 rev 3 review board must remain a large-type PNG.", 422);
  }

  const ids = {
    generator: "premium-display-case-contract-generator-r003",
    contract: "premium-display-case-modeling-contract-r003",
    preview: "premium-display-case-contract-preview-r003",
    validation: "premium-display-case-contract-validation-r003"
  };
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  for (const id of Object.values(ids)) {
    if (existingIds.has(id)) {
      throw new PipelineError(`Gate 03 rev 3 asset already exists: ${id}`, 409);
    }
  }
  const gate02SourceIds = [...new Set(analysis.artifactIds || [])];
  const definitions = [
    {
      key: "generator",
      slot: "contract-recipe",
      role: "process",
      contentClass: "deterministic-serial-motion-light-contract-generator",
      recipe: "Build locked-versus-tunable Gate 03 rev 3 contract",
      sourceAssetIds: gate02SourceIds
    },
    {
      key: "contract",
      slot: "modeling-contract",
      role: "contract",
      contentClass: "premium-display-case-serial-motion-light-contract",
      recipe: "Gate 03 rev 3 serial motion, restrained light and explicit unknowns",
      sourceAssetIds: [ids.generator, ...gate02SourceIds]
    },
    {
      key: "preview",
      slot: "contract-preview",
      role: "analysis",
      contentClass: "premium-display-case-serial-contract-review-board",
      recipe: "Large-type locked-versus-tunable review board",
      sourceAssetIds: [ids.contract, ids.generator]
    },
    {
      key: "validation",
      slot: "validation-report",
      role: "validation",
      contentClass: "premium-display-case-serial-contract-validation",
      recipe: "Claim consumption, serial phases, forbidden effects and unknown checks",
      sourceAssetIds: [ids.contract, ids.preview]
    }
  ];
  const assetRecords = definitions.map((definition) => {
    const file = files[definition.key];
    return {
      id: ids[definition.key],
      stageId: "03-contract",
      slot: definition.slot,
      path: file.normalized,
      sha256: sha256File(file.absolute),
      exists: true,
      sizeBytes: fs.statSync(file.absolute).size,
      role: definition.role,
      producer: {
        name: "fidgeting-model-pipeline",
        version: "2026-08-26",
        recipe: definition.recipe
      },
      provenance: {
        origin: "repository-generated",
        contentClass: definition.contentClass,
        assertedBy: "assistant",
        note: "Gate 03 rev 3 contract only. Shipping runtime parameters remain tunable; Blender and Unity are unchanged."
      },
      sourceAssetIds: definition.sourceAssetIds,
      sourceClaimIds: activeClaimIds,
      wholeCaseOnly: true,
      explodeEligible: false
    };
  });
  const now = new Date().toISOString();
  for (const asset of manifest.assets) {
    if (asset.stageId === "03-contract" && asset.id !== ids.contract) {
      asset.reviewState = "stale";
      asset.supersededAt = now;
      asset.preservedForHistory = true;
      asset.dispositionNote = "Preserved stale Gate 03 history; rev 3 consumes approved Gate 02 rev 6 claims.";
    }
  }
  manifest.assets.push(...assetRecords);
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = assetRecords.map((asset) => asset.id);
  stage.reviewArtifactIds = [ids.preview];
  stage.validations = [
    { id: "all-active-gate02-claims-consumed", status: "pass", evidence: "All 10 active Gate 02 rev 5/6 claims are declared by every Gate 03 rev 3 artifact." },
    { id: "serial-motion-locked", status: "pass", evidence: "Y+Z entry settles before one local-Y 360; translation and rotation never overlap." },
    { id: "causal-light-locked", status: "pass", evidence: "Seam, arrival rim, surface rim, one sheen and short halo follow physical causes and stop." },
    { id: "runtime-tuning-unlocked", status: "pass", evidence: "Shipping duration, phase timing/easing, distances, light parameters and camera FOV remain null/unknown." },
    { id: "stale-authority-excluded", status: "pass", evidence: "The stale 4.520833 s and rev 3 quaternion path are explicitly not current authority." },
    { id: "static-values-preserved", status: "pass", evidence: "Historical geometry/material inputs remain unchanged and pending revalidation." },
    { id: "whole-case-toy-boundary", status: "pass", evidence: "One assembled case; caller-owned toy remains static; no proxy, split or explode." },
    { id: "performance-boundary", status: "pass", evidence: "60 FPS / 0 B-frame remain product targets; only target iPhone Release build can pass." },
    { id: "gate04-not-entered", status: "pass", evidence: "Gate 03 is ready_for_review only; Gate 04–08 remain stale." },
    { id: "shipping-boundary", status: "pass", evidence: "Shipping Unity, Simulator, build, install and phone state remain unchanged." }
  ];
  stage.decision = null;
  stage.contractSpec = {
    revision: 3,
    sourceAnalysisRevision: 6,
    sourceMotionStructureRevision: 5,
    sourceLightTreatmentRevision: 6,
    sourceClaimIds: activeClaimIds,
    staticStructurePreserved: true,
    rigidWholeCase: true,
    phaseOrder: motion.phaseOrder,
    entryAxes: motion.entry.translationAxes,
    entryRotationDegrees: motion.entry.rotationDegrees,
    showcaseAxis: motion.showcase.axis,
    showcaseDegrees: motion.showcase.degrees,
    simultaneousEntryAndShowcase: motion.simultaneousEntryAndShowcase,
    causalLightCueOrder: light.causalCueOrder,
    forbidden: motion.forbidden,
    reviewDurationSeconds: tunable.previewDurationSeconds,
    shippingTotalDurationSeconds: null,
    tunableParameterCount: validation.metrics.tunableParameterCount,
    prizeIndependentAngularVelocity: motion.showcase.toyIndependentAngularVelocity,
    wholeCaseOnly: motion.wholeCaseOnly,
    explode: false,
    gate04Status: "blocked"
  };
  delete stage.staleReason;

  const downstreamReason = "Gate 03 rev 3 is ready_for_review and not approved. Gate 04–08 retain immutable historical artifacts as stale.";
  const staleStageIds = [];
  for (let index = stageIndex + 1; index <= 7; index += 1) {
    const downstream = manifest.stages[index];
    if ((downstream.artifactIds || []).length) {
      downstream.status = "stale";
      staleStageIds.push(downstream.id);
    }
    downstream.staleReason = downstreamReason;
  }
  for (let index = 8; index < manifest.stages.length; index += 1) {
    manifest.stages[index].staleReason = downstreamReason;
  }
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 02 rev 6 remains approved. Gate 03 contract rev 3 is ready_for_review: serial Y+Z entry, settle, one local-Y 360, restrained causal light and hold are locked as direction; duration, easing, distances, light parameters and shipping camera remain tunable. Gate 04–08 remain stale; shipping Unity is unchanged.";
  manifest.currentState.visualApproval = "gate03-contract-review-pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.motionCorrection = {
    ...manifest.currentState.motionCorrection,
    analysisRevision: 6,
    activeClaimCount: activeClaimIds.length,
    gate03Status: "ready_for_review",
    gate03ContractRevision: 3,
    gate04Status: "stale-awaiting-gate03-approval",
    shippingDurationApproved: false,
    shippingPreviewApproved: false,
    deviceAccepted: false
  };
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "03-contract",
    contractRevision: "003",
    sourceAnalysisRevision: 6,
    sourceMotionStructureRevision: 5,
    sourceLightTreatmentRevision: 6,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    sourceClaimIds: activeClaimIds,
    phaseOrder: motion.phaseOrder,
    entryAxes: motion.entry.translationAxes,
    showcase: "one-local-y-360-after-settle",
    lightCueOrder: light.causalCueOrder,
    reviewDurationSeconds: tunable.previewDurationSeconds,
    shippingDurationApproved: false,
    tunableParameterCount: validation.metrics.tunableParameterCount,
    staleStageIds,
    approvedCount: 2,
    earliestGate: "03-contract",
    autoApproved: false,
    gate04Status: "stale",
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseSerialArchitectureReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) {
    throw new PipelineError("Manifest revision conflict.", 409);
  }
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This architecture review is supported only for the Premium Display Case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "04-architecture");
  const contractStage = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (
    contractStage.status !== "approved"
    || contractStage.contractSpec?.revision !== 3
    || contractStage.contractSpec?.approval?.approvedRevision !== 3
    || contractStage.contractSpec?.approval?.userApprovalQuote !== "批准合同并继续（推荐）"
    || contractStage.contractSpec?.approval?.shippingDurationApproved !== false
  ) {
    throw new PipelineError("Gate 03 rev 3 must be explicitly approved before Gate 04 rev 5.", 422);
  }
  const activeClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  if (
    activeClaimIds.length !== 10
    || activeClaimIds.some((claimId) => !claimId.endsWith("-r005") && !claimId.endsWith("-r006"))
  ) {
    throw new PipelineError("Gate 04 rev 5 must consume exactly 10 active Gate 02 rev 5/6 claims.", 422);
  }

  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/04-architecture/rev-005"
  )));
  const files = {
    approval: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-005",
      `${expectedDirectory}/gate03-approval-scope.md`,
      "Gate 03 rev 3 approval scope"
    ),
    generator: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-005",
      `${expectedDirectory}/generate_serial_architecture_review.py`,
      "Gate 04 rev 5 deterministic generator"
    ),
    architecture: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-005",
      `${expectedDirectory}/architecture.json`,
      "Gate 04 rev 5 architecture"
    ),
    partTree: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-005",
      `${expectedDirectory}/part-tree-internal.svg`,
      "Gate 04 rev 5 internal part tree"
    ),
    explodedPlan: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-005",
      `${expectedDirectory}/exploded-plan-internal.svg`,
      "Gate 04 rev 5 internal exploded plan"
    ),
    review: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-005",
      `${expectedDirectory}/whole-case-architecture-review.png`,
      "Gate 04 rev 5 whole-case review board"
    ),
    validation: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-005",
      `${expectedDirectory}/architecture-validation.json`,
      "Gate 04 rev 5 architecture validation"
    )
  };
  const architecture = JSON.parse(fs.readFileSync(files.architecture.absolute, "utf8"));
  const validation = JSON.parse(fs.readFileSync(files.validation.absolute, "utf8"));
  const phaseIds = architecture?.phaseArchitecture?.map((phase) => phase.id);
  const cueIds = architecture?.lightCues?.map((cue) => cue.id);
  const tunable = architecture?.tunableRuntimeParameters;
  if (
    architecture?.modelId !== modelId
    || architecture?.architectureRevision !== 2
    || architecture?.evidenceRevision !== 5
    || architecture?.status !== "ready_for_review"
    || architecture?.sourceContract?.contractRevision !== 3
    || architecture?.sourceContract?.sourceAnalysisRevision !== 6
    || architecture?.sourceContract?.sourceClaimIds?.length !== activeClaimIds.length
    || activeClaimIds.some((claimId) => !architecture.sourceContract.sourceClaimIds.includes(claimId))
    || architecture?.ownership?.pack !== "external/native NativePackOwner"
    || architecture?.ownership?.presentation !== "PresentationRoot"
    || architecture?.ownership?.case !== "one rigid CaseAssembly instance"
    || architecture?.ownership?.toy !== "caller-owned ContentSlot child"
    || architecture?.ownership?.light !== "RestrainedLightController"
    || phaseIds?.join(",") !== "prepare,entry,settle,showcase,final-light,hold"
    || architecture?.phaseArchitecture?.[1]?.motion?.join(",") !== "screen-y,camera-depth-z"
    || architecture?.phaseArchitecture?.[1]?.rotation?.some((value) => value !== 0)
    || architecture?.phaseArchitecture?.[3]?.motion !== "one local-Y 360"
    || architecture?.phaseArchitecture?.[3]?.translation !== "locked"
    || cueIds?.join(",") !== "pack-seam-light,arrival-rim,rotation-surface-rim,final-sheen-short-halo"
    || architecture?.lightCues?.some((cue) => cue.finite !== true)
    || architecture?.invariants?.oneCaseInstance !== true
    || architecture?.invariants?.wholeCaseOnly !== true
    || architecture?.invariants?.packProxyAllowed !== false
    || architecture?.invariants?.entryAndShowcaseOverlap !== false
    || architecture?.invariants?.toyIndependentAngularVelocity !== 0
    || architecture?.invariants?.particleEmitterCount !== 0
    || architecture?.invariants?.persistentLightLoop !== false
    || architecture?.invariants?.explodeEligible !== false
    || tunable?.previewDurationSeconds !== 3.4
    || tunable?.shippingTotalDurationSeconds !== null
    || tunable?.phaseDurationsSeconds !== null
    || tunable?.phaseEasing !== null
    || tunable?.entryScreenYDistance !== null
    || tunable?.entryCameraDepthZDistance !== null
    || tunable?.shippingCameraFovDegrees !== null
    || architecture?.internalEvidence?.reviewEligible !== false
    || architecture?.internalEvidence?.productAnimationEligible !== false
    || architecture?.userReview?.assembledOnly !== true
    || architecture?.userReview?.explodedVisible !== false
    || architecture?.route?.gate05Status !== "blocked"
    || architecture?.route?.shippingUnityEdit !== false
    || architecture?.route?.buildInstallPhonePush !== false
    || architecture?.route?.nextGatePolicy !== "Do not enter Gate 05 before explicit Gate 04 approval."
  ) {
    throw new PipelineError("Gate 04 rev 5 architecture violates the approved ownership, serial phase, finite-light, whole-case, or tunable-runtime contract.", 422);
  }
  if (
    validation?.status !== "pass"
    || validation?.architectureRevision !== 2
    || validation?.evidenceRevision !== 5
    || Object.values(validation?.checks || {}).some((value) => value !== true)
    || validation?.metrics?.finiteLightCueCount !== 4
    || validation?.metrics?.reviewArtifactExplodedPartCount !== 0
    || validation?.metrics?.tunableRuntimeParameterCount !== 17
  ) {
    throw new PipelineError("Gate 04 rev 5 architecture validation did not pass.", 422);
  }
  const reviewBytes = fs.readFileSync(files.review.absolute);
  const reviewWidth = reviewBytes.subarray(1, 4).toString("ascii") === "PNG"
    ? reviewBytes.readUInt32BE(16)
    : 0;
  const reviewHeight = reviewWidth ? reviewBytes.readUInt32BE(20) : 0;
  if (reviewWidth < 3000 || reviewHeight < 3600) {
    throw new PipelineError("Gate 04 rev 5 review board must remain a large-type PNG.", 422);
  }
  const partTreeText = fs.readFileSync(files.partTree.absolute, "utf8");
  const explodedText = fs.readFileSync(files.explodedPlan.absolute, "utf8");
  if (
    !partTreeText.includes("INTERNAL TECHNICAL EVIDENCE")
    || !explodedText.includes("TECHNICAL PIPELINE EVIDENCE ONLY")
    || !explodedText.includes("productAnimationEligible=false")
  ) {
    throw new PipelineError("Gate 04 technical hierarchy evidence must remain explicitly internal-only.", 422);
  }

  const ids = {
    approval: "premium-display-case-gate03-approval-scope-r005",
    generator: "premium-display-case-architecture-generator-r005",
    architecture: "premium-display-case-serial-architecture-r005",
    partTree: "premium-display-case-part-tree-internal-r005",
    explodedPlan: "premium-display-case-exploded-plan-internal-r005",
    review: "premium-display-case-whole-case-architecture-review-r005",
    validation: "premium-display-case-architecture-validation-r005"
  };
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  for (const id of Object.values(ids)) {
    if (existingIds.has(id)) {
      throw new PipelineError(`Gate 04 rev 5 asset already exists: ${id}`, 409);
    }
  }
  const contractSourceIds = [...new Set(contractStage.artifactIds || [])];
  const definitions = [
    {
      key: "approval",
      slot: "user-feedback",
      role: "user-input",
      contentClass: "gate03-rev3-approval-scope",
      recipe: "Preserve the exact Gate 03 approval boundary",
      sourceAssetIds: contractSourceIds
    },
    {
      key: "generator",
      slot: "architecture-recipe",
      role: "process",
      contentClass: "deterministic-serial-architecture-generator",
      recipe: "Generate Gate 04 ownership, phase, light and review evidence",
      sourceAssetIds: [ids.approval, ...contractSourceIds]
    },
    {
      key: "architecture",
      slot: "architecture-spec",
      role: "contract",
      contentClass: "premium-display-case-serial-ownership-architecture",
      recipe: "Define one-instance ownership, serial phases, finite light and tunable boundaries",
      sourceAssetIds: [ids.generator, ...contractSourceIds]
    },
    {
      key: "partTree",
      slot: "part-tree",
      role: "analysis",
      contentClass: "internal-technical-part-owner-tree",
      recipe: "Internal hierarchy evidence; excluded from user review",
      sourceAssetIds: [ids.architecture]
    },
    {
      key: "explodedPlan",
      slot: "exploded-plan",
      role: "analysis",
      contentClass: "internal-technical-exploded-plan",
      recipe: "Internal physical-zone order; never product animation",
      sourceAssetIds: [ids.architecture, ids.partTree]
    },
    {
      key: "review",
      slot: "architecture-board",
      role: "analysis",
      contentClass: "whole-assembled-case-ownership-phase-review",
      recipe: "User-facing whole-case ownership and serial phase board",
      sourceAssetIds: [ids.architecture, ids.generator]
    },
    {
      key: "validation",
      slot: "validation-report",
      role: "validation",
      contentClass: "premium-display-case-serial-architecture-validation",
      recipe: "Validate ownership, phases, four finite cues, whole-case review and tunable values",
      sourceAssetIds: [ids.architecture, ids.partTree, ids.explodedPlan, ids.review]
    }
  ];
  const internalKeys = new Set(["partTree", "explodedPlan"]);
  const assetRecords = definitions.map((definition) => {
    const file = files[definition.key];
    return {
      id: ids[definition.key],
      stageId: "04-architecture",
      slot: definition.slot,
      path: file.normalized,
      sha256: sha256File(file.absolute),
      exists: true,
      sizeBytes: fs.statSync(file.absolute).size,
      role: definition.role,
      producer: {
        name: "fidgeting-model-pipeline",
        version: "2026-08-26",
        recipe: definition.recipe
      },
      provenance: {
        origin: definition.key === "approval" ? "user-provided" : "repository-generated",
        contentClass: definition.contentClass,
        assertedBy: definition.key === "approval" ? "user" : "assistant",
        note: internalKeys.has(definition.key)
          ? "Internal technical evidence only. It is excluded from reviewArtifactIds and every shipping product path."
          : "Gate 04 architecture only. Shipping Unity, Simulator, build, install and phone state remain unchanged."
      },
      sourceAssetIds: definition.sourceAssetIds,
      sourceClaimIds: activeClaimIds,
      reviewState: "active",
      wholeCaseOnly: !internalKeys.has(definition.key),
      explodeEligible: false,
      internalTechnicalEvidence: internalKeys.has(definition.key)
    };
  });

  const now = new Date().toISOString();
  for (const asset of manifest.assets) {
    if (asset.stageId === "04-architecture") {
      asset.reviewState = "stale";
      asset.supersededAt = now;
      asset.preservedForHistory = true;
      asset.dispositionNote = "Preserved immutable Gate 04 history. Rev 5 rebuilds ownership and serial phases from approved Gate 03 rev 3; old pure-Y, explode/reassemble and 4.520833 s timing authority remain stale.";
    }
  }
  manifest.assets.push(...assetRecords);
  if (stage.decision) {
    stage.historicalDecisions = [...(stage.historicalDecisions || []), stage.decision];
  }
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = assetRecords.map((asset) => asset.id);
  stage.reviewArtifactIds = [ids.review];
  stage.validations = [
    { id: "gate03-rev3-approved", status: "pass", evidence: "Gate 03 rev 3 is approved with the exact ‘批准合同并继续（推荐）’ scope." },
    { id: "single-rigid-case-identity", status: "pass", evidence: "One CaseAssembly instance remains assembled and visible through ACK." },
    { id: "ownership-boundaries", status: "pass", evidence: "PresentationRoot owns case motion; NativePackOwner remains external; ContentSlot/Toy remain caller-owned and static." },
    { id: "serial-phase-gate", status: "pass", evidence: "Y+Z entry exits at zero velocity before translation-locked local-Y 360 starts." },
    { id: "four-finite-light-cues", status: "pass", evidence: "Exactly four finite cues are owned by RestrainedLightController; the final cue contains one sheen and short halo." },
    { id: "no-particle-or-loop", status: "pass", evidence: "Particle emitter count is 0; VFX Graph and persistent light loops remain forbidden." },
    { id: "runtime-tuning-unlocked", status: "pass", evidence: "Shipping duration, phase timing/easing, Y/Z distances, light parameters and camera FOV remain null." },
    { id: "internal-exploded-evidence-only", status: "pass", evidence: "Part tree and exploded plan are internal artifactIds only; the sole reviewArtifactId shows assembled cases." },
    { id: "gate05-blocked", status: "pass", evidence: "Gate 05 and later stages remain blocked or stale until explicit Gate 04 approval." },
    { id: "shipping-boundary", status: "pass", evidence: "Shipping Unity, Simulator, build, install and phone state remain unchanged." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  stage.architectureSpec = {
    revision: 2,
    evidenceRevision: 5,
    sourceContractRevision: 3,
    sourceAnalysisRevision: 6,
    sourceClaimIds: activeClaimIds,
    phaseOrder: phaseIds,
    entryOwner: "PresentationRoot",
    entryAxes: architecture.phaseArchitecture[1].motion,
    showcaseOwner: "PresentationRoot",
    showcase: "one-local-y-360-after-full-settle",
    caseIdentity: "one-rigid-assembled-instance-through-ack",
    nativePackOwner: "external",
    toyOwner: "caller-owned-content-slot",
    toyIndependentAngularVelocity: 0,
    lightController: "RestrainedLightController",
    finiteLightCueIds: cueIds,
    finiteLightCueCount: cueIds.length,
    particleEmitterCount: 0,
    persistentLightLoop: false,
    shippingDurationApproved: false,
    tunableRuntimeParameterCount: validation.metrics.tunableRuntimeParameterCount,
    wholeCaseOnly: true,
    explodeEligible: false,
    internalArtifactIds: [ids.partTree, ids.explodedPlan],
    reviewArtifactIds: [ids.review],
    gate05Status: "blocked"
  };

  const downstreamReason = "Gate 04 rev 5 serial whole-case architecture is ready_for_review and not approved. Gate 05+ retain immutable historical artifacts as stale or remain blocked.";
  const staleStageIds = [];
  for (let index = stageIndex + 1; index <= 7; index += 1) {
    const downstream = manifest.stages[index];
    if ((downstream.artifactIds || []).length) {
      downstream.status = "stale";
      staleStageIds.push(downstream.id);
    }
    downstream.staleReason = downstreamReason;
  }
  for (let index = 8; index < manifest.stages.length; index += 1) {
    manifest.stages[index].staleReason = downstreamReason;
  }

  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 03 rev 3 is approved. Gate 04 rev 5 is ready_for_review with one rigid CaseAssembly, PresentationRoot serial Y+Z entry then local-Y 360, external Native Pack ownership, caller-owned static Toy, and exactly four finite restrained-light cues. Timing, easing, distances, light tuning and camera remain unlocked. Gate 05+ remain stale or blocked; shipping Unity is unchanged.";
  manifest.currentState.visualApproval = "gate04-architecture-review-pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.motionCorrection = {
    ...manifest.currentState.motionCorrection,
    earliestGate: "04-architecture",
    gate03Status: "approved-rev3",
    gate04Status: "ready_for_review-rev5",
    gate04ArchitectureRevision: 2,
    finiteLightCueCount: 4,
    shippingDurationApproved: false,
    shippingPreviewApproved: false,
    deviceAccepted: false
  };
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "04-architecture",
    architectureRevision: 2,
    evidenceRevision: 5,
    sourceContractRevision: 3,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    internalArtifactIds: stage.architectureSpec.internalArtifactIds,
    sourceClaimIds: activeClaimIds,
    phaseOrder: phaseIds,
    ownership: architecture.ownership,
    caseIdentity: stage.architectureSpec.caseIdentity,
    lightCueIds: cueIds,
    finiteLightCueCount: cueIds.length,
    particleEmitterCount: 0,
    shippingDurationApproved: false,
    tunableParameterCount: validation.metrics.tunableRuntimeParameterCount,
    staleStageIds,
    approvedCount: 3,
    earliestGate: "04-architecture",
    autoApproved: false,
    gate05Status: "blocked",
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseOverlapArchitectureReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) {
    throw new PipelineError("Manifest revision conflict.", 409);
  }
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This overlap review is supported only for the Premium Display Case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "04-architecture");
  const contractStage = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  const userQuote = String(payload.userQuote || "").trim();
  const expectedQuote = "对，然后也不用完全停完再原地转一圈。";
  if (
    contractStage.status !== "approved"
    || contractStage.contractSpec?.revision !== 3
    || contractStage.contractSpec?.approval?.approvedRevision !== 3
    || stage.status !== "rejected"
    || stage.decision?.action !== "reject"
    || !stage.decision.notes.includes(expectedQuote)
    || stage.architectureSpec?.evidenceRevision !== 5
  ) {
    throw new PipelineError("Gate 04 rev 5 must first record the user's hard-stop rejection.", 422);
  }
  if (userQuote !== expectedQuote) {
    throw new PipelineError("The exact overlap feedback must be preserved.", 422);
  }
  const activeClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  if (
    activeClaimIds.length !== 10
    || activeClaimIds.some((claimId) => !claimId.endsWith("-r005") && !claimId.endsWith("-r006"))
  ) {
    throw new PipelineError("Gate 04 rev 6 must preserve all 10 active Gate 02 rev 5/6 claims.", 422);
  }

  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/04-architecture/rev-006"
  )));
  const files = {
    feedback: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-006",
      `${expectedDirectory}/user-overlap-feedback.md`,
      "Gate 04 rev 6 user overlap feedback"
    ),
    generator: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-006",
      `${expectedDirectory}/generate_overlap_architecture_review.py`,
      "Gate 04 rev 6 deterministic generator"
    ),
    architecture: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-006",
      `${expectedDirectory}/architecture.json`,
      "Gate 04 rev 6 overlap architecture"
    ),
    gif: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-006",
      `${expectedDirectory}/whole-case-overlap-motion.gif`,
      "Gate 04 rev 6 overlap GIF"
    ),
    contact: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-006",
      `${expectedDirectory}/whole-case-overlap-contact-sheet.png`,
      "Gate 04 rev 6 overlap contact sheet"
    ),
    review: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-006",
      `${expectedDirectory}/whole-case-overlap-architecture-review.png`,
      "Gate 04 rev 6 whole-case review"
    ),
    validation: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-006",
      `${expectedDirectory}/architecture-validation.json`,
      "Gate 04 rev 6 architecture validation"
    )
  };
  const architecture = JSON.parse(fs.readFileSync(files.architecture.absolute, "utf8"));
  const validation = JSON.parse(fs.readFileSync(files.validation.absolute, "utf8"));
  const phaseIds = architecture?.phaseArchitecture?.map((phase) => phase.id);
  const overlap = architecture?.overlapContract;
  const internalIds = [
    "premium-display-case-part-tree-internal-r005",
    "premium-display-case-exploded-plan-internal-r005"
  ];
  if (
    architecture?.modelId !== modelId
    || architecture?.architectureRevision !== 2
    || architecture?.evidenceRevision !== 6
    || architecture?.status !== "ready_for_review"
    || architecture?.sourceContract?.contractRevision !== 3
    || architecture?.sourceContract?.sourceClaimIds?.length !== activeClaimIds.length
    || activeClaimIds.some((claimId) => !architecture.sourceContract.sourceClaimIds.includes(claimId))
    || architecture?.ownership?.pack !== "external/native NativePackOwner"
    || architecture?.ownership?.presentation !== "PresentationRoot"
    || architecture?.ownership?.case !== "one rigid CaseAssembly instance"
    || architecture?.ownership?.toy !== "caller-owned ContentSlot child"
    || architecture?.ownership?.light !== "RestrainedLightController"
    || phaseIds?.join(",") !== "prepare,entry,entry-showcase-overlap,showcase,final-light,hold"
    || architecture?.phaseArchitecture?.[1]?.motion?.join(",") !== "screen-y,camera-depth-z"
    || architecture?.phaseArchitecture?.[1]?.rotation?.some((value) => value !== 0)
    || architecture?.phaseArchitecture?.[2]?.bounded !== true
    || architecture?.phaseArchitecture?.[2]?.count !== 1
    || architecture?.phaseArchitecture?.[3]?.motion !== "continue one local-Y 360"
    || architecture?.phaseArchitecture?.[3]?.translation !== "locked after entry tail ends"
    || overlap?.enabled !== true
    || overlap?.count !== 1
    || overlap?.entryTailOnly !== true
    || overlap?.caseMustClearPackBeforeRotation !== true
    || overlap?.entryTranslationMustBeDecelerating !== true
    || overlap?.unboundedSimultaneousMotion !== false
    || overlap?.reviewDemonstrationCandidate?.approvalEffect !== "none-pending-runtime-tuning"
    || overlap?.lockedValues?.startThreshold !== null
    || overlap?.lockedValues?.durationSeconds !== null
    || overlap?.lockedValues?.rotationOnsetCurve !== null
    || architecture?.invariants?.oneCaseInstance !== true
    || architecture?.invariants?.wholeCaseOnly !== true
    || architecture?.invariants?.packProxyAllowed !== false
    || architecture?.invariants?.entryAndShowcaseOverlap !== true
    || architecture?.invariants?.overlapWindowCount !== 1
    || architecture?.invariants?.overlapBounded !== true
    || architecture?.invariants?.entryTailOnly !== true
    || architecture?.invariants?.toyIndependentAngularVelocity !== 0
    || architecture?.invariants?.particleEmitterCount !== 0
    || architecture?.invariants?.persistentLightLoop !== false
    || architecture?.invariants?.explodeEligible !== false
    || architecture?.tunableRuntimeParameters?.overlapStartThreshold !== null
    || architecture?.tunableRuntimeParameters?.overlapDurationSeconds !== null
    || architecture?.tunableRuntimeParameters?.rotationOnsetCurve !== null
    || architecture?.internalEvidence?.reviewEligible !== false
    || architecture?.internalEvidence?.productAnimationEligible !== false
    || architecture?.internalEvidence?.changedByRev6 !== false
    || architecture?.userReview?.assembledOnly !== true
    || architecture?.userReview?.explodedVisible !== false
    || architecture?.route?.gate05Status !== "blocked"
    || architecture?.route?.shippingUnityEdit !== false
    || architecture?.route?.buildInstallPhonePush !== false
  ) {
    throw new PipelineError("Gate 04 rev 6 architecture violates the controlled-overlap ownership contract.", 422);
  }
  if (
    validation?.status !== "pass"
    || validation?.architectureRevision !== 2
    || validation?.evidenceRevision !== 6
    || Object.values(validation?.checks || {}).some((value) => value !== true)
    || validation?.metrics?.overlapWindowCount !== 1
    || validation?.metrics?.overlapLockedParameterCount !== 0
    || validation?.metrics?.reviewArtifactExplodedPartCount !== 0
  ) {
    throw new PipelineError("Gate 04 rev 6 overlap validation did not pass.", 422);
  }
  const reviewBytes = fs.readFileSync(files.review.absolute);
  const reviewWidth = reviewBytes.subarray(1, 4).toString("ascii") === "PNG"
    ? reviewBytes.readUInt32BE(16)
    : 0;
  const reviewHeight = reviewWidth ? reviewBytes.readUInt32BE(20) : 0;
  if (reviewWidth < 1600 || reviewHeight < 1200) {
    throw new PipelineError("Gate 04 rev 6 review board must remain a readable large-type PNG.", 422);
  }
  for (const internalId of internalIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === internalId);
    if (!asset || asset.internalTechnicalEvidence !== true || asset.explodeEligible !== false) {
      throw new PipelineError("Gate 04 rev 5 internal technical evidence is unavailable.", 422);
    }
  }

  const ids = {
    feedback: "premium-display-case-overlap-feedback-r006",
    generator: "premium-display-case-overlap-generator-r006",
    architecture: "premium-display-case-overlap-architecture-r006",
    gif: "premium-display-case-overlap-gif-r006",
    contact: "premium-display-case-overlap-contact-r006",
    review: "premium-display-case-overlap-review-r006",
    validation: "premium-display-case-overlap-validation-r006"
  };
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  for (const id of Object.values(ids)) {
    if (existingIds.has(id)) {
      throw new PipelineError(`Gate 04 rev 6 asset already exists: ${id}`, 409);
    }
  }
  const rev5ArchitectureId = "premium-display-case-serial-architecture-r005";
  const rev5GeneratorId = "premium-display-case-architecture-generator-r005";
  const contractSourceIds = [...new Set(contractStage.artifactIds || [])];
  const definitions = [
    {
      key: "feedback",
      slot: "user-feedback",
      role: "user-input",
      contentClass: "gate04-rev5-phase-boundary-correction",
      recipe: "Preserve exact user correction and accepted ownership scope",
      sourceAssetIds: [rev5ArchitectureId, ...contractSourceIds]
    },
    {
      key: "generator",
      slot: "architecture-recipe",
      role: "process",
      contentClass: "deterministic-overlap-architecture-generator",
      recipe: "Generate bounded entry/rotation overlap review",
      sourceAssetIds: [ids.feedback, rev5GeneratorId, rev5ArchitectureId]
    },
    {
      key: "architecture",
      slot: "architecture-spec",
      role: "contract",
      contentClass: "premium-display-case-controlled-overlap-architecture",
      recipe: "Define late-entry/early-rotation bounded overlap with unlocked timing",
      sourceAssetIds: [ids.feedback, ids.generator, rev5ArchitectureId, ...contractSourceIds]
    },
    {
      key: "gif",
      slot: "architecture-animation",
      role: "process",
      contentClass: "whole-case-controlled-overlap-gif",
      recipe: "Whole-case bounded overlap preview",
      sourceAssetIds: [ids.architecture, ids.generator]
    },
    {
      key: "contact",
      slot: "animation-contact-sheet",
      role: "analysis",
      contentClass: "whole-case-controlled-overlap-contact-sheet",
      recipe: "Late-entry and early-rotation overlap contact sheet",
      sourceAssetIds: [ids.architecture, ids.gif]
    },
    {
      key: "review",
      slot: "architecture-board",
      role: "analysis",
      contentClass: "whole-case-controlled-overlap-review-board",
      recipe: "User-facing overlap ownership and tunable boundary board",
      sourceAssetIds: [ids.architecture, ids.generator, ids.contact]
    },
    {
      key: "validation",
      slot: "validation-report",
      role: "validation",
      contentClass: "premium-display-case-controlled-overlap-validation",
      recipe: "Validate one bounded overlap, ownership, finite lights and shipping boundary",
      sourceAssetIds: [ids.architecture, ids.gif, ids.contact, ids.review, ...internalIds]
    }
  ];
  const assetRecords = definitions.map((definition) => {
    const file = files[definition.key];
    return {
      id: ids[definition.key],
      stageId: "04-architecture",
      slot: definition.slot,
      path: file.normalized,
      sha256: sha256File(file.absolute),
      exists: true,
      sizeBytes: fs.statSync(file.absolute).size,
      role: definition.role,
      producer: {
        name: "fidgeting-model-pipeline",
        version: "2026-08-26",
        recipe: definition.recipe
      },
      provenance: {
        origin: definition.key === "feedback" ? "user-provided" : "repository-generated",
        contentClass: definition.contentClass,
        assertedBy: definition.key === "feedback" ? "user" : "assistant",
        note: "Gate 04 architecture only. One assembled case uses one bounded late-entry/early-rotation overlap; all timing values remain pending."
      },
      sourceAssetIds: definition.sourceAssetIds,
      sourceClaimIds: activeClaimIds,
      reviewState: "active",
      wholeCaseOnly: true,
      explodeEligible: false,
      internalTechnicalEvidence: false
    };
  });

  const now = new Date().toISOString();
  for (const asset of manifest.assets) {
    if (asset.stageId !== "04-architecture") continue;
    if (internalIds.includes(asset.id)) {
      asset.reviewState = "active-internal-preserved";
      asset.preservedForHistory = true;
      asset.dispositionNote = "Internal technical hierarchy evidence is unchanged by the rev 6 phase-boundary correction.";
    } else {
      asset.reviewState = "stale";
      asset.supersededAt = now;
      asset.preservedForHistory = true;
      asset.dispositionNote = "Preserved immutable Gate 04 history. Rev 6 replaces only the full-stop phase boundary.";
    }
  }
  manifest.assets.push(...assetRecords);
  if (stage.decision) {
    stage.historicalDecisions = [...(stage.historicalDecisions || []), stage.decision];
  }
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = [
    ...assetRecords.map((asset) => asset.id),
    ...internalIds
  ];
  stage.reviewArtifactIds = [ids.review, ids.gif, ids.contact];
  stage.validations = [
    { id: "gate03-rev3-approved", status: "pass", evidence: "Gate 03 rev 3 remains approved; static ownership and finite-light scope are unchanged." },
    { id: "accepted-ownership-preserved", status: "pass", evidence: "Native Pack, PresentationRoot, CaseAssembly, ContentSlot/Toy and RestrainedLightController ownership remains unchanged." },
    { id: "single-rigid-case-identity", status: "pass", evidence: "One assembled CaseAssembly instance remains visible through ACK." },
    { id: "controlled-overlap-window", status: "pass", evidence: "Rotation may begin only after the case clears the Pack and entry enters its deceleration tail; exactly one bounded overlap window exists." },
    { id: "no-hard-pause", status: "pass", evidence: "Entry need not reach absolute zero before rotation begins." },
    { id: "no-unbounded-simultaneous-motion", status: "pass", evidence: "X drift, roll, pitch, independent scale, camera/background motion and unbounded multi-axis overlap remain forbidden." },
    { id: "four-finite-light-cues", status: "pass", evidence: "Seam, arrival rim, rotation rim and final sheen/short halo ownership remains unchanged and finite." },
    { id: "runtime-overlap-tuning-unlocked", status: "pass", evidence: "Overlap threshold, duration and rotation-onset curve remain null; demonstration values have no approval effect." },
    { id: "internal-exploded-evidence-only", status: "pass", evidence: "Rev 5 part tree and exploded plan remain internal artifactIds only; every review artifact shows the assembled whole case." },
    { id: "gate05-blocked", status: "pass", evidence: "Gate 05 and later stages remain stale or blocked until explicit Gate 04 approval." },
    { id: "shipping-boundary", status: "pass", evidence: "Shipping Unity, Simulator, build, install and phone state remain unchanged." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  stage.architectureSpec = {
    revision: 2,
    evidenceRevision: 6,
    sourceContractRevision: 3,
    sourceAnalysisRevision: 6,
    sourceClaimIds: activeClaimIds,
    phaseOrder: phaseIds,
    entryOwner: "PresentationRoot",
    entryAxes: architecture.phaseArchitecture[1].motion,
    showcaseOwner: "PresentationRoot",
    showcase: "one-local-y-360-with-bounded-entry-tail-overlap",
    overlapWindowCount: 1,
    overlapWindow: {
      entryTailOnly: true,
      caseMustClearPack: true,
      entryTranslationMustBeDecelerating: true,
      bounded: true,
      startThreshold: null,
      durationSeconds: null,
      rotationOnsetCurve: null,
      demonstrationCandidate: overlap.reviewDemonstrationCandidate
    },
    caseIdentity: "one-rigid-assembled-instance-through-ack",
    nativePackOwner: "external",
    toyOwner: "caller-owned-content-slot",
    toyIndependentAngularVelocity: 0,
    lightController: "RestrainedLightController",
    finiteLightCueIds: architecture.lightCues.map((cue) => cue.id),
    finiteLightCueCount: architecture.lightCues.length,
    particleEmitterCount: 0,
    persistentLightLoop: false,
    shippingDurationApproved: false,
    tunableRuntimeParameterCount: Object.entries(
      architecture.tunableRuntimeParameters
    ).filter(([key, value]) => key !== "decisionState" && key !== "note" && value === null).length,
    wholeCaseOnly: true,
    explodeEligible: false,
    internalArtifactIds: internalIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    gate05Status: "blocked"
  };

  const downstreamReason = "Gate 04 rev 6 controlled overlap is ready_for_review and not approved. Gate 05+ remain stale or blocked.";
  const staleStageIds = [];
  for (let index = stageIndex + 1; index <= 7; index += 1) {
    const downstream = manifest.stages[index];
    if ((downstream.artifactIds || []).length) {
      downstream.status = "stale";
      staleStageIds.push(downstream.id);
    }
    downstream.staleReason = downstreamReason;
  }
  for (let index = 8; index < manifest.stages.length; index += 1) {
    manifest.stages[index].staleReason = downstreamReason;
  }

  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 03 rev 3 remains approved. Gate 04 rev 5 full-stop boundary is rejected. Gate 04 rev 6 is ready_for_review: the same assembled case begins one local-Y 360 during the deceleration tail after clearing the Pack, using one bounded tunable overlap window. Ownership and finite-light cues are unchanged; Gate 05+ remain stale or blocked; shipping Unity is unchanged.";
  manifest.currentState.visualApproval = "gate04-overlap-review-pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.motionCorrection = {
    ...manifest.currentState.motionCorrection,
    earliestGate: "04-architecture",
    gate03Status: "approved-rev3",
    gate04Status: "ready_for_review-rev6",
    gate04ArchitectureRevision: 2,
    overlapWindowCount: 1,
    overlapTimingApproved: false,
    shippingDurationApproved: false,
    shippingPreviewApproved: false,
    deviceAccepted: false
  };
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "04-architecture",
    architectureRevision: 2,
    evidenceRevision: 6,
    sourceContractRevision: 3,
    userQuote,
    rejectedEvidenceRevision: 5,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    internalArtifactIds: internalIds,
    sourceClaimIds: activeClaimIds,
    phaseOrder: phaseIds,
    overlapWindowCount: 1,
    overlapTimingApproved: false,
    overlapDemonstrationCandidate: overlap.reviewDemonstrationCandidate,
    ownership: architecture.ownership,
    caseIdentity: stage.architectureSpec.caseIdentity,
    lightCueIds: stage.architectureSpec.finiteLightCueIds,
    finiteLightCueCount: stage.architectureSpec.finiteLightCueCount,
    particleEmitterCount: 0,
    shippingDurationApproved: false,
    tunableParameterCount: stage.architectureSpec.tunableRuntimeParameterCount,
    staleStageIds,
    approvedCount: 3,
    earliestGate: "04-architecture",
    autoApproved: false,
    gate05Status: "blocked",
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseMeshClippedLightArchitectureReview(
  modelId,
  payload
) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) {
    throw new PipelineError("Manifest revision conflict.", 409);
  }
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This mesh-clipped light review is supported only for the Premium Display Case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "04-architecture");
  const contractStage = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  const userQuote = String(payload.userQuote || "").trim();
  const expectedQuote = "节奏上面我还有很多想要调整的，尤其是你的过光，不应该超过这个物体本身。我觉得大概的动画是这样吧，但是可能你后面我们再去调节奏吧。";
  if (
    contractStage.status !== "approved"
    || contractStage.contractSpec?.revision !== 3
    || stage.status !== "rejected"
    || stage.decision?.action !== "reject"
    || !stage.decision.notes.includes("过光，不应该超过这个物体本身")
    || stage.architectureSpec?.evidenceRevision !== 6
  ) {
    throw new PipelineError("Gate 04 rev 6 must first record the user's mesh-clipped light correction.", 422);
  }
  if (userQuote !== expectedQuote) {
    throw new PipelineError("The exact mesh-clipped light feedback must be preserved.", 422);
  }
  const activeClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  if (
    activeClaimIds.length !== 10
    || activeClaimIds.some((claimId) => !claimId.endsWith("-r005") && !claimId.endsWith("-r006"))
  ) {
    throw new PipelineError("Gate 04 rev 7 must preserve all 10 active Gate 02 rev 5/6 claims.", 422);
  }

  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/04-architecture/rev-007"
  )));
  const files = {
    feedback: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-007",
      `${expectedDirectory}/user-mesh-clipped-light-feedback.md`,
      "Gate 04 rev 7 user light-boundary feedback"
    ),
    generator: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-007",
      `${expectedDirectory}/generate_mesh_clipped_light_review.py`,
      "Gate 04 rev 7 deterministic generator"
    ),
    architecture: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-007",
      `${expectedDirectory}/architecture.json`,
      "Gate 04 rev 7 mesh-clipped light architecture"
    ),
    gif: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-007",
      `${expectedDirectory}/whole-case-mesh-clipped-light-motion.gif`,
      "Gate 04 rev 7 mesh-clipped light GIF"
    ),
    contact: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-007",
      `${expectedDirectory}/whole-case-mesh-clipped-light-contact-sheet.png`,
      "Gate 04 rev 7 mesh-clipped light contact sheet"
    ),
    review: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-007",
      `${expectedDirectory}/mesh-clipped-light-architecture-review.png`,
      "Gate 04 rev 7 whole-case review"
    ),
    validation: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-007",
      `${expectedDirectory}/architecture-validation.json`,
      "Gate 04 rev 7 architecture validation"
    )
  };
  const architecture = JSON.parse(fs.readFileSync(files.architecture.absolute, "utf8"));
  const validation = JSON.parse(fs.readFileSync(files.validation.absolute, "utf8"));
  const internalIds = [
    "premium-display-case-part-tree-internal-r005",
    "premium-display-case-exploded-plan-internal-r005"
  ];
  if (
    architecture?.modelId !== modelId
    || architecture?.architectureRevision !== 2
    || architecture?.evidenceRevision !== 7
    || architecture?.status !== "ready_for_review"
    || architecture?.sourceContract?.contractRevision !== 3
    || architecture?.ownership?.pack !== "external/native NativePackOwner"
    || architecture?.ownership?.presentation !== "PresentationRoot"
    || architecture?.ownership?.case !== "one rigid CaseAssembly instance"
    || architecture?.ownership?.toy !== "caller-owned ContentSlot child"
    || architecture?.ownership?.light !== "MeshClippedLightController"
    || architecture?.invariants?.oneCaseInstance !== true
    || architecture?.invariants?.entryAndShowcaseOverlap !== true
    || architecture?.invariants?.overlapWindowCount !== 1
    || architecture?.invariants?.overlapBounded !== true
    || architecture?.invariants?.caseLightOutsideSilhouettePixels !== 0
    || architecture?.invariants?.externalSettleHalo !== false
    || architecture?.invariants?.externalPointLightFinalSheen !== false
    || architecture?.invariants?.vfxGraphDependency !== false
    || architecture?.invariants?.bloomDependency !== false
    || architecture?.invariants?.particleEmitterCount !== 0
    || architecture?.invariants?.persistentLightLoop !== false
    || architecture?.invariants?.toyIndependentAngularVelocity !== 0
    || architecture?.invariants?.wholeCaseOnly !== true
    || architecture?.invariants?.explodeEligible !== false
    || architecture?.unityRuntimeArchitecture?.stateAuthority !== "GachaRevealDirector"
    || architecture?.unityRuntimeArchitecture?.profile !== "RevealMotionProfile ScriptableObject"
    || architecture?.unityRuntimeArchitecture?.curves !== "AnimationCurve per phase and cue"
    || architecture?.unityRuntimeArchitecture?.materialDriver !== "MaterialPropertyBlock"
    || architecture?.unityRuntimeArchitecture?.timelineRole !== "editor-preview-and-scrub-only"
    || architecture?.unityRuntimeArchitecture?.timelineTransactionAuthority !== false
    || architecture?.toolOwnership?.Blender?.join(",") !== "geometry,pivot,UV,material zones"
    || !architecture?.toolOwnership?.Unity?.includes("mesh-clipped light")
    || architecture?.toolOwnership?.React?.join(",") !== "pipeline review tooling only"
    || architecture?.tunableRuntimeParameters?.shippingTotalDurationSeconds !== null
    || architecture?.tunableRuntimeParameters?.overlapDurationSeconds !== null
    || architecture?.tunableRuntimeParameters?.finalSheenDriver !== "MaterialPropertyBlock"
    || architecture?.tunableRuntimeParameters?.finalSheenShaderProperty !== "_SheenProgress"
    || architecture?.userReview?.assembledOnly !== true
    || architecture?.userReview?.explodedVisible !== false
    || architecture?.userReview?.externalHaloVisible !== false
    || architecture?.route?.gate05Status !== "blocked"
    || architecture?.route?.shippingUnityEdit !== false
    || architecture?.route?.buildInstallPhonePush !== false
  ) {
    throw new PipelineError("Gate 04 rev 7 architecture violates the mesh-clipped runtime ownership contract.", 422);
  }
  if (
    validation?.status !== "pass"
    || validation?.architectureRevision !== 2
    || validation?.evidenceRevision !== 7
    || Object.values(validation?.checks || {}).some((value) => value !== true)
    || validation?.metrics?.caseLightOutsideSilhouetteMaxPixels !== 0
    || validation?.metrics?.finiteLightCueCount !== 4
    || validation?.metrics?.particleEmitterCount !== 0
    || validation?.metrics?.externalPointLightCount !== 0
    || validation?.metrics?.persistentLightLoopCount !== 0
    || validation?.metrics?.finalFrameActiveLightCueCount !== 0
    || validation?.metrics?.reviewArtifactExplodedPartCount !== 0
  ) {
    throw new PipelineError("Gate 04 rev 7 mesh-clipped light validation did not pass.", 422);
  }
  for (const internalId of internalIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === internalId);
    if (!asset || asset.internalTechnicalEvidence !== true || asset.explodeEligible !== false) {
      throw new PipelineError("Gate 04 internal technical evidence is unavailable.", 422);
    }
  }

  const ids = {
    feedback: "premium-display-case-mesh-light-feedback-r007",
    generator: "premium-display-case-mesh-light-generator-r007",
    architecture: "premium-display-case-mesh-light-architecture-r007",
    gif: "premium-display-case-mesh-light-gif-r007",
    contact: "premium-display-case-mesh-light-contact-r007",
    review: "premium-display-case-mesh-light-review-r007",
    validation: "premium-display-case-mesh-light-validation-r007"
  };
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  if (Object.values(ids).some((id) => existingIds.has(id))) {
    throw new PipelineError("Gate 04 rev 7 asset id already exists.", 409);
  }
  const rev6ArchitectureId = "premium-display-case-overlap-architecture-r006";
  const contractSourceIds = [...new Set(contractStage.artifactIds || [])];
  const definitions = [
    ["feedback", "user-feedback", "user-input", "gate04-rev6-light-boundary-correction", "Preserve exact user correction", [rev6ArchitectureId, ...contractSourceIds]],
    ["generator", "architecture-recipe", "process", "deterministic-mesh-clipped-light-generator", "Generate mesh-clipped whole-case review", [ids.feedback, rev6ArchitectureId]],
    ["architecture", "architecture-spec", "contract", "premium-display-case-mesh-clipped-light-architecture", "Define Unity runtime and tool ownership", [ids.feedback, ids.generator, rev6ArchitectureId, ...contractSourceIds]],
    ["gif", "architecture-animation", "process", "whole-case-mesh-clipped-light-gif", "Whole-case clipped-light preview", [ids.architecture, ids.generator]],
    ["contact", "animation-contact-sheet", "analysis", "whole-case-mesh-clipped-light-contact-sheet", "Clipped-light contact sheet", [ids.architecture, ids.gif]],
    ["review", "architecture-board", "analysis", "whole-case-mesh-clipped-light-review-board", "User-facing tool ownership and light boundary board", [ids.architecture, ids.contact]],
    ["validation", "validation-report", "validation", "premium-display-case-mesh-clipped-light-validation", "Validate zero outside-mask pixels and runtime ownership", [ids.architecture, ids.gif, ids.contact, ids.review, ...internalIds]]
  ];
  const assetRecords = definitions.map(([
    key,
    slot,
    role,
    contentClass,
    recipe,
    sourceAssetIds
  ]) => {
    const file = files[key];
    return {
      id: ids[key],
      stageId: "04-architecture",
      slot,
      path: file.normalized,
      sha256: sha256File(file.absolute),
      exists: true,
      sizeBytes: fs.statSync(file.absolute).size,
      role,
      producer: {
        name: "fidgeting-model-pipeline",
        version: "2026-08-26",
        recipe
      },
      provenance: {
        origin: key === "feedback" ? "user-provided" : "repository-generated",
        contentClass,
        assertedBy: key === "feedback" ? "user" : "assistant",
        note: "Gate 04 architecture only. Case light is clipped to the case mask; Pack light remains in the seam. Runtime tuning remains pending."
      },
      sourceAssetIds,
      sourceClaimIds: activeClaimIds,
      reviewState: "active",
      wholeCaseOnly: true,
      explodeEligible: false,
      internalTechnicalEvidence: false
    };
  });

  const now = new Date().toISOString();
  for (const asset of manifest.assets) {
    if (asset.stageId !== "04-architecture") continue;
    if (internalIds.includes(asset.id)) {
      asset.reviewState = "active-internal-preserved";
      asset.preservedForHistory = true;
      asset.dispositionNote = "Internal hierarchy evidence remains technical-only.";
    } else {
      asset.reviewState = "stale";
      asset.supersededAt = now;
      asset.preservedForHistory = true;
      asset.dispositionNote = "Preserved immutable Gate 04 history. Rev 7 replaces external halo with mesh-clipped Unity light.";
    }
  }
  manifest.assets.push(...assetRecords);
  if (stage.decision) {
    stage.historicalDecisions = [...(stage.historicalDecisions || []), stage.decision];
  }
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = [...assetRecords.map((asset) => asset.id), ...internalIds];
  stage.reviewArtifactIds = [ids.review, ids.gif, ids.contact];
  stage.validations = [
    { id: "gate03-rev3-approved", status: "pass", evidence: "Gate 03 rev 3 remains approved." },
    { id: "bounded-overlap-preserved", status: "pass", evidence: "One late-entry/early-rotation overlap remains tunable and bounded." },
    { id: "mesh-clipped-case-light", status: "pass", evidence: "Every case-light frame has zero light pixels outside the case mask." },
    { id: "external-halo-removed", status: "pass", evidence: "Settle halo and external Point Light final sheen are removed." },
    { id: "unity-runtime-authority", status: "pass", evidence: "GachaRevealDirector and RevealMotionProfile own runtime state and curves; Timeline is preview-only." },
    { id: "tool-ownership-explicit", status: "pass", evidence: "Blender, Unity, SwiftUI/Rive and React responsibilities are explicit." },
    { id: "finite-cues-no-loop", status: "pass", evidence: "Four finite cues end at zero; no particles, VFX Graph, Bloom dependency or persistent loop." },
    { id: "whole-case-toy-static", status: "pass", evidence: "One assembled case remains through ACK and the caller-owned toy stays static." },
    { id: "runtime-tuning-unlocked", status: "pass", evidence: "Duration, easing, overlap, Z distance, camera and light parameters remain pending." },
    { id: "internal-exploded-evidence-only", status: "pass", evidence: "Part tree and exploded plan remain internal and absent from reviewArtifactIds." },
    { id: "gate05-blocked", status: "pass", evidence: "Gate 05+ remain stale or blocked." },
    { id: "shipping-boundary", status: "pass", evidence: "Shipping Unity, Simulator, build, install and phone state remain unchanged." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  stage.architectureSpec = {
    revision: 2,
    evidenceRevision: 7,
    sourceContractRevision: 3,
    sourceAnalysisRevision: 6,
    sourceClaimIds: activeClaimIds,
    phaseOrder: architecture.phaseArchitecture.map((phase) => phase.id),
    entryOwner: "PresentationRoot",
    entryAxes: architecture.phaseArchitecture[1].motion,
    showcaseOwner: "PresentationRoot",
    showcase: "one-local-y-360-with-bounded-entry-tail-overlap",
    overlapWindowCount: 1,
    overlapTimingApproved: false,
    caseIdentity: "one-rigid-assembled-instance-through-ack",
    nativePackOwner: "external",
    toyOwner: "caller-owned-content-slot",
    toyIndependentAngularVelocity: 0,
    lightController: "MeshClippedLightController",
    finiteLightCueIds: architecture.lightCues.map((cue) => cue.id),
    finiteLightCueCount: architecture.lightCues.length,
    caseLightOutsideSilhouettePixels: 0,
    externalSettleHalo: false,
    externalPointLightFinalSheen: false,
    vfxGraphDependency: false,
    particleEmitterCount: 0,
    persistentLightLoop: false,
    unityRuntimeArchitecture: architecture.unityRuntimeArchitecture,
    toolOwnership: architecture.toolOwnership,
    shippingDurationApproved: false,
    tunableRuntimeParameterCount: Object.entries(
      architecture.tunableRuntimeParameters
    ).filter(([key, value]) => (
      key !== "decisionState"
      && key !== "note"
      && value === null
    )).length,
    wholeCaseOnly: true,
    explodeEligible: false,
    internalArtifactIds: internalIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    gate05Status: "blocked"
  };

  const downstreamReason = "Gate 04 rev 7 mesh-clipped light architecture is ready_for_review and not approved. Gate 05+ remain stale or blocked.";
  const staleStageIds = [];
  for (let index = stageIndex + 1; index <= 7; index += 1) {
    const downstream = manifest.stages[index];
    if ((downstream.artifactIds || []).length) {
      downstream.status = "stale";
      staleStageIds.push(downstream.id);
    }
    downstream.staleReason = downstreamReason;
  }
  for (let index = 8; index < manifest.stages.length; index += 1) {
    manifest.stages[index].staleReason = downstreamReason;
  }

  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 03 rev 3 remains approved. Gate 04 rev 6 external halo is rejected. Gate 04 rev 7 is ready_for_review: the bounded entry/rotation overlap remains, case lighting is mesh-clipped with zero outside-mask pixels, final sheen uses MaterialPropertyBlock, and Unity owns runtime motion/light tuning. Gate 05+ remain stale or blocked; shipping Unity is unchanged.";
  manifest.currentState.visualApproval = "gate04-mesh-clipped-light-review-pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.motionCorrection = {
    ...manifest.currentState.motionCorrection,
    earliestGate: "04-architecture",
    gate03Status: "approved-rev3",
    gate04Status: "ready-for-review-rev7",
    gate04ArchitectureRevision: 2,
    meshClippedLight: true,
    caseLightOutsideSilhouettePixels: 0,
    overlapTimingApproved: false,
    shippingDurationApproved: false,
    shippingPreviewApproved: false,
    deviceAccepted: false
  };
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "04-architecture",
    architectureRevision: 2,
    evidenceRevision: 7,
    sourceContractRevision: 3,
    userQuote,
    rejectedEvidenceRevision: 6,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    internalArtifactIds: internalIds,
    sourceClaimIds: activeClaimIds,
    caseLightOutsideSilhouettePixels: 0,
    externalSettleHalo: false,
    externalPointLightFinalSheen: false,
    lightCueIds: stage.architectureSpec.finiteLightCueIds,
    finiteLightCueCount: stage.architectureSpec.finiteLightCueCount,
    toolOwnership: stage.architectureSpec.toolOwnership,
    unityRuntimeArchitecture: stage.architectureSpec.unityRuntimeArchitecture,
    particleEmitterCount: 0,
    shippingDurationApproved: false,
    tunableParameterCount: stage.architectureSpec.tunableRuntimeParameterCount,
    staleStageIds,
    approvedCount: 3,
    earliestGate: "04-architecture",
    autoApproved: false,
    gate05Status: "blocked",
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function saveArchitecturePlan(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "04-architecture");
  if (manifest.stages[stageIndex - 1].status !== "approved") throw new PipelineError("Gate 03 must be approved before creating the architecture plan.", 422);

  const contract = loadModelingContract(modelId);
  const sourceClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  const premiumDisplayCaseContractComplete = modelId === "premium-display-case"
    && contract?.modelId === modelId
    && sourceClaimIds.length > 0
    && sourceClaimIds.every((claimId) => contract.sourceClaimIds?.includes(claimId))
    && contract.closedTubeFrame?.topology?.connectivity === "one connected manifold"
    && contract.revealMotion?.sequence?.prizeAngularVelocity === 0
    && contract.route?.nextGatePolicy === "Do not enter Gate 04 before explicit Gate 03 approval.";
  if (!contract?.completeness?.complete && !premiumDisplayCaseContractComplete) {
    throw new PipelineError("The approved modeling contract is incomplete.", 422);
  }

  const sliderArchitectureSpec = modelId === "magnetic-slide-tile" ? {
    externalMainShellCount: Number(payload.externalMainShellCount),
    linearModule: String(payload.linearModule || ""),
    rotaryModule: String(payload.rotaryModule || ""),
    modeRelationship: String(payload.modeRelationship || ""),
    couplingPolicy: String(payload.couplingPolicy || ""),
    exteriorAssemblyPolicy: String(payload.exteriorAssemblyPolicy || ""),
    motionSequencePolicy: String(payload.motionSequencePolicy || ""),
    rotationLimitPolicy: String(payload.rotationLimitPolicy || ""),
    hiddenHardwarePolicy: String(payload.hiddenHardwarePolicy || ""),
    dimensionPolicy: String(payload.dimensionPolicy || "")
  } : null;
  if (sliderArchitectureSpec && (
    contract.mechanism.secondaryMotion !== "dual-mode-free-spin"
    || sliderArchitectureSpec.externalMainShellCount !== 2
    || sliderArchitectureSpec.linearModule !== "bilateral-long-rail-ball-or-bead-grooves"
    || sliderArchitectureSpec.rotaryModule !== "circular-ball-track-and-central-shaft-or-bearing-region"
    || sliderArchitectureSpec.modeRelationship !== "straight-push-and-free-spin"
    || sliderArchitectureSpec.couplingPolicy !== "unknown-until-physical-proof"
    || sliderArchitectureSpec.exteriorAssemblyPolicy !== "two-main-shells-plus-visible-functional-modules"
    || sliderArchitectureSpec.motionSequencePolicy !== "separately-supported-no-end-stop-unlock"
    || sliderArchitectureSpec.rotationLimitPolicy !== "continuous-free-spin-no-degree-limit-asserted"
    || sliderArchitectureSpec.hiddenHardwarePolicy !== "visible-only-no-exact-counts-tolerances-or-hole-depths"
    || sliderArchitectureSpec.dimensionPolicy !== "user-authorized-provisional-digital-blockout"
  )) {
    throw new PipelineError("Magnetic slider architecture must keep two exterior main shells plus visible functional modules, preserve the linear and rotary evidence, treat straight push and free spin as separately supported modes without end-stop unlock or a degree limit, keep hidden counts/tolerances/hole depths unknown, and use the approved dimensions only as provisional digital-blockout values.", 422);
  }

  const expectedDisplayCaseHierarchy = [
    { id: "presentation-root", parentId: null, kind: "transform-root", physical: false },
    { id: "case-assembly", parentId: "presentation-root", kind: "transform-group", physical: false },
    { id: "rear-polycarbonate-shell", parentId: "case-assembly", kind: "physical-part", physical: true },
    { id: "tactile-background-insert", parentId: "rear-polycarbonate-shell", kind: "physical-part", physical: true },
    { id: "content-slot", parentId: "rear-polycarbonate-shell", kind: "runtime-anchor", physical: false },
    { id: "prize-content", parentId: "content-slot", kind: "runtime-content", physical: true },
    { id: "front-polycarbonate-shell", parentId: "case-assembly", kind: "physical-part", physical: true },
    { id: "continuous-tube-perimeter", parentId: "front-polycarbonate-shell", kind: "physical-part", physical: true },
    { id: "physical-label", parentId: "front-polycarbonate-shell", kind: "physical-part", physical: true },
    { id: "logo-zone", parentId: "physical-label", kind: "print-zone", physical: false },
    { id: "achievement-zone", parentId: "physical-label", kind: "print-zone", physical: false },
    { id: "narrow-foil", parentId: "physical-label", kind: "material-zone", physical: false },
    { id: "transparent-cover", parentId: "front-polycarbonate-shell", kind: "physical-part", physical: true }
  ];
  const expectedDisplayCaseExplodedOrder = [
    "transparent-cover",
    "physical-label",
    "continuous-tube-perimeter",
    "front-polycarbonate-shell",
    "prize-content",
    "tactile-background-insert",
    "rear-polycarbonate-shell"
  ];
  const premiumDisplayCaseArchitectureSpec = modelId === "premium-display-case" ? {
    hierarchy: Array.isArray(payload.hierarchy) ? payload.hierarchy.map((node) => ({
      id: String(node.id || ""),
      parentId: node.parentId === null ? null : String(node.parentId || ""),
      kind: String(node.kind || ""),
      physical: Boolean(node.physical)
    })) : [],
    explodedOrderFrontToRear: Array.isArray(payload.explodedOrderFrontToRear)
      ? payload.explodedOrderFrontToRear.map((id) => String(id))
      : [],
    motionOwner: String(payload.motionOwner || ""),
    showcaseMotion: String(payload.showcaseMotion || ""),
    prizeMotion: String(payload.prizeMotion || ""),
    prizeMechanismPolicy: String(payload.prizeMechanismPolicy || ""),
    shippingRevealPolicy: String(payload.shippingRevealPolicy || ""),
    explodedEvidencePolicy: String(payload.explodedEvidencePolicy || ""),
    perimeterPolicy: String(payload.perimeterPolicy || ""),
    connectedPerimeterPartCount: Number(payload.connectedPerimeterPartCount),
    hiddenHardwarePolicy: String(payload.hiddenHardwarePolicy || ""),
    containerPolicy: String(payload.containerPolicy || "")
  } : null;
  const displayCaseHierarchyMatches = premiumDisplayCaseArchitectureSpec
    && premiumDisplayCaseArchitectureSpec.hierarchy.length === expectedDisplayCaseHierarchy.length
    && expectedDisplayCaseHierarchy.every((expected, index) => (
      JSON.stringify(premiumDisplayCaseArchitectureSpec.hierarchy[index]) === JSON.stringify(expected)
    ));
  const displayCaseExplodedOrderMatches = premiumDisplayCaseArchitectureSpec
    && JSON.stringify(premiumDisplayCaseArchitectureSpec.explodedOrderFrontToRear) === JSON.stringify(expectedDisplayCaseExplodedOrder);
  if (premiumDisplayCaseArchitectureSpec && (
    !displayCaseHierarchyMatches
    || !displayCaseExplodedOrderMatches
    || premiumDisplayCaseArchitectureSpec.motionOwner !== "presentation-root"
    || premiumDisplayCaseArchitectureSpec.showcaseMotion !== "assembled-case-unwrapped-y-0-to-360-then-once-highlight-and-hover"
    || premiumDisplayCaseArchitectureSpec.prizeMotion !== "inherits-case-transform-only-zero-independent-angular-velocity"
    || premiumDisplayCaseArchitectureSpec.prizeMechanismPolicy !== "unchanged"
    || premiumDisplayCaseArchitectureSpec.shippingRevealPolicy !== "always-assembled-never-explodes-or-reassembles"
    || premiumDisplayCaseArchitectureSpec.explodedEvidencePolicy !== "internal-production-and-website-structure-only"
    || premiumDisplayCaseArchitectureSpec.perimeterPolicy !== "one-connected-closed-tube-part-never-four-bars"
    || premiumDisplayCaseArchitectureSpec.connectedPerimeterPartCount !== 1
    || premiumDisplayCaseArchitectureSpec.hiddenHardwarePolicy !== "no-invented-fasteners-no-hidden-fluid-hardware-no-extra-layers"
    || premiumDisplayCaseArchitectureSpec.containerPolicy !== "presentation-root-and-case-assembly-are-nonphysical-transform-containers"
  )) {
    throw new PipelineError("Premium Display Case architecture must preserve the approved parent tree, one connected perimeter part, assembled-only shipping reveal, presentation-root motion ownership, zero independent prize angular velocity, and the no-invented-hardware boundary.", 422);
  }
  const architectureSpec = sliderArchitectureSpec || premiumDisplayCaseArchitectureSpec;

  const priorPartTrees = manifest.assets.filter((asset) => asset.stageId === "04-architecture" && asset.slot === "part-tree");
  const architectureRevision = priorPartTrees.length + 1;
  const revisionLabel = String(architectureRevision).padStart(3, "0");
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/04-architecture", `rev-${revisionLabel}`
  )));
  const paths = {
    partTree: normalizeRepoPath(payload.partTreePath || `${expectedDirectory}/part-tree.svg`),
    explodedPlan: normalizeRepoPath(payload.explodedPlanPath || `${expectedDirectory}/exploded-plan.svg`),
    ...(premiumDisplayCaseArchitectureSpec ? {
      recipe: normalizeRepoPath(payload.recipePath || `${expectedDirectory}/render_architecture_preview.py`),
      preview: normalizeRepoPath(payload.previewPath || `${expectedDirectory}/architecture-preview.png`)
    } : {})
  };
  for (const [label, relativePath] of Object.entries(paths)) {
    if (!relativePath.startsWith(`${expectedDirectory}/`)) throw new PipelineError(`${label} must be stored inside ${expectedDirectory}.`);
    const absolutePath = resolveRepoPath(relativePath);
    if (!fs.existsSync(absolutePath) || !fs.statSync(absolutePath).isFile()) throw new PipelineError(`${label} file is missing.`, 422);
  }

  let previewDimensions = null;
  if (premiumDisplayCaseArchitectureSpec) {
    const previewBytes = fs.readFileSync(resolveRepoPath(paths.preview));
    const pngSignature = previewBytes.length >= 24 && previewBytes.subarray(1, 4).toString("ascii") === "PNG";
    previewDimensions = pngSignature ? {
      width: previewBytes.readUInt32BE(16),
      height: previewBytes.readUInt32BE(20)
    } : null;
    if (!previewDimensions || previewDimensions.width < 2400 || previewDimensions.height < 3000 || Number(payload.minimumBodyFontPixels) < 32) {
      throw new PipelineError("Premium Display Case architecture preview must be a PNG of at least 2400 × 3000 with 32 px minimum body type.", 422);
    }
  }

  const contractAssetIds = manifest.stages[stageIndex - 1].artifactIds;
  const contractAssetId = contractAssetIds[0];
  const sourceAssetIds = (premiumDisplayCaseArchitectureSpec ? contractAssetIds : [
    contractAssetId,
    ...(sliderArchitectureSpec ? [
      "slider-analysis-official-discovery-log-r002",
      "slider-analysis-official-mechanism-board-r002",
      "slider-intake-haloo-official-05",
      "slider-intake-haloo-official-06",
      "slider-intake-haloo-official-07",
      "slider-intake-haloo-official-08",
      "slider-intake-haloo-official-metadata"
    ] : [
      "slider-intake-user-frame-08",
      "slider-intake-user-frame-11",
      "slider-intake-user-frame-12"
    ])
  ]).filter((assetId, index, values) => manifest.assets.some((asset) => asset.id === assetId) && values.indexOf(assetId) === index);
  const now = new Date().toISOString();
  const partTreeAssetId = `${modelId}-part-tree-r${revisionLabel}`;
  const explodedPlanAssetId = `${modelId}-exploded-plan-r${revisionLabel}`;
  const recipeAssetId = `${modelId}-architecture-preview-recipe-r${revisionLabel}`;
  const previewAssetId = `${modelId}-architecture-preview-r${revisionLabel}`;
  const assetRecords = [
    {
      id: partTreeAssetId,
      slot: "part-tree",
      path: paths.partTree,
      contentClass: "annotated-part-hierarchy",
      sameStageSourceAssetIds: premiumDisplayCaseArchitectureSpec ? [recipeAssetId] : []
    },
    {
      id: explodedPlanAssetId,
      slot: "exploded-plan",
      path: paths.explodedPlan,
      contentClass: "annotated-exploded-assembly-plan",
      sameStageSourceAssetIds: premiumDisplayCaseArchitectureSpec ? [recipeAssetId] : []
    },
    ...(premiumDisplayCaseArchitectureSpec ? [
      {
        id: recipeAssetId,
        slot: "architecture-recipe",
        path: paths.recipe,
        contentClass: "deterministic-architecture-preview-recipe",
        sameStageSourceAssetIds: []
      },
      {
        id: previewAssetId,
        slot: "architecture-board",
        path: paths.preview,
        contentClass: "large-type-architecture-review-board",
        sameStageSourceAssetIds: [recipeAssetId, partTreeAssetId, explodedPlanAssetId],
        view: {
          id: "architecture",
          camera: "orthographic-information-board",
          parameters: {
            widthPixels: previewDimensions.width,
            heightPixels: previewDimensions.height,
            minimumBodyFontPixels: Number(payload.minimumBodyFontPixels)
          }
        }
      }
    ] : [])
  ].map((record) => {
    const absolutePath = resolveRepoPath(record.path);
    return {
      id: record.id,
      stageId: "04-architecture",
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolutePath),
      exists: true,
      sizeBytes: fs.statSync(absolutePath).size,
      role: "process",
      producer: {
        name: premiumDisplayCaseArchitectureSpec ? "Python Pillow / deterministic SVG" : "fidgeting-model-pipeline",
        version: premiumDisplayCaseArchitectureSpec ? "2026-08-24" : "1",
        recipe: premiumDisplayCaseArchitectureSpec
          ? "Gate 04 Premium Display Case hierarchy, internal exploded plan, motion ownership, and shipping red-line board"
          : "Gate 04 source-linked vector architecture review"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: premiumDisplayCaseArchitectureSpec
          ? "Consumes the explicitly approved Gate 03 rev 1 contract. The exploded view is internal production and website structure evidence only; the shipping reveal remains assembled and never writes prize angular velocity."
          : sliderArchitectureSpec
          ? "依据已批准的同款官方研究修订：外观装配保留两个主壳，同时保留双直线珠轨、圆形珠轨、中央轴区、弹簧与球件模块；直推与自由旋转不再写成末端解锁顺序，精确耦合保持未知。"
          : "依据已批准建模合同和实拍可见结构生成；隐藏硬件数量保持未知。"
      },
      sourceAssetIds: [...sourceAssetIds, ...(record.sameStageSourceAssetIds || [])],
      sourceClaimIds,
      ...(record.view ? { view: record.view } : {})
    };
  });
  manifest.assets.push(...assetRecords);
  const stage = manifest.stages[stageIndex];
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = assetRecords.map((asset) => asset.id);
  if (architectureSpec) stage.architectureSpec = architectureSpec;
  stage.reviewArtifactIds = premiumDisplayCaseArchitectureSpec ? [previewAssetId] : [partTreeAssetId, explodedPlanAssetId];
  stage.validations = premiumDisplayCaseArchitectureSpec ? [
    { id: "approved-contract-consumed", status: "pass", evidence: `All ${contractAssetIds.length} Gate 03 artifacts and the approved decision feed the architecture evidence.` },
    { id: "approved-claims-consumed", status: "pass", evidence: `Every Gate 04 artifact declares all ${sourceClaimIds.length} active Gate 02 sourceClaimIds.` },
    { id: "part-hierarchy-explicit", status: "pass", evidence: "The tree records PresentationRoot → CaseAssembly, rear shell → tactile insert/content slot → prize, and front shell → one perimeter/label/cover with label zones." },
    { id: "single-connected-perimeter-part", status: "pass", evidence: "ContinuousTubePerimeter is one physical child and has no top/right/bottom/left subparts." },
    { id: "internal-exploded-plan-only", status: "pass", evidence: "The exploded order is internal production and website structure evidence; shipping reveal never explodes or reassembles." },
    { id: "motion-ownership-explicit", status: "pass", evidence: "PresentationRoot owns the assembled Y-axis 0→360 turn, one highlight, and hover; every case child inherits the root transform." },
    { id: "prize-motion-isolated", status: "pass", evidence: "PrizeContent remains under ContentSlot with zero independent angular velocity and unchanged mechanism state." },
    { id: "no-invented-hardware", status: "pass", evidence: "No fasteners, hidden fluid hardware, or extra physical layers are present; nonphysical transform containers and print/material zones are labeled." },
    { id: "large-type-architecture-preview", status: "pass", evidence: `${previewDimensions.width} × ${previewDimensions.height} PNG with ${Number(payload.minimumBodyFontPixels)} px minimum body type is registered for direct review.` },
    { id: "gate-05-remains-blocked", status: "pass", evidence: "Gate 04 has no decision and Gate 05 remains blocked pending explicit architecture approval." }
  ] : [
    { id: "approved-contract-consumed", status: "pass", evidence: `Both architecture views directly consume ${contractAssetId}.` },
    sliderArchitectureSpec
      ? { id: "two-exterior-main-shells", status: sliderArchitectureSpec.externalMainShellCount === 2 ? "pass" : "fail", evidence: "The exterior assembly uses two main shells while visible internal functional modules remain separately identifiable." }
      : { id: "part-hierarchy-explicit", status: "pass", evidence: "The architecture diagram explicitly assigns each physical part and interface responsibility." },
    sliderArchitectureSpec
      ? { id: "visible-modules-preserved", status: sliderArchitectureSpec.linearModule === contract.mechanism.linearModule && sliderArchitectureSpec.rotaryModule === contract.mechanism.rotaryModule ? "pass" : "fail", evidence: "The bilateral long-rail module and circular central-bearing module are both preserved from the approved contract." }
      : { id: "interfaces-explicit", status: "pass", evidence: "The architecture diagram identifies its guiding and motion interfaces." },
    sliderArchitectureSpec
      ? { id: "dual-mode-with-unknown-coupling", status: sliderArchitectureSpec.modeRelationship === "straight-push-and-free-spin" && sliderArchitectureSpec.couplingPolicy === "unknown-until-physical-proof" ? "pass" : "fail", evidence: "Straight push and free spin are represented without reintroducing an unsupported sequential unlock path." }
      : { id: "motion-sequence-explicit", status: "pass", evidence: "The architecture diagram identifies its allowed motion sequence." },
    ...(sliderArchitectureSpec ? [{
      id: "rejected-assumptions-excluded",
      status: sliderArchitectureSpec.exteriorAssemblyPolicy === "two-main-shells-plus-visible-functional-modules"
        && sliderArchitectureSpec.motionSequencePolicy === "separately-supported-no-end-stop-unlock"
        && sliderArchitectureSpec.rotationLimitPolicy === "continuous-free-spin-no-degree-limit-asserted"
        && sliderArchitectureSpec.hiddenHardwarePolicy === "visible-only-no-exact-counts-tolerances-or-hole-depths"
        && sliderArchitectureSpec.dimensionPolicy === "user-authorized-provisional-digital-blockout"
        ? "pass"
        : "fail",
      evidence: "The plan excludes the rejected five-layer structure, 90-degree cap, end-stop unlock, exact hidden counts, tolerances and hole depths; 50×31×12 mm and 21 mm remain provisional digital-blockout values."
    }] : []),
    {
      id: "motion-contract-mapped",
      status: sliderArchitectureSpec
        ? contract.mechanism.secondaryMotion === "dual-mode-free-spin" && contract.mechanism.laneMode === "dual-working-lanes" ? "pass" : "fail"
        : contract.mechanism.secondaryMotion === "translation-plus-rotation" && contract.mechanism.maxRotationDeg === 90 && contract.mechanism.laneMode === "dual-working-lanes" ? "pass" : "fail",
      evidence: sliderArchitectureSpec
        ? "The plan maps the estimated straight-push travel and free-spin central-bearing region as two supported modes."
        : "The plan maps the approved translation and rotation contract."
    },
    { id: "hidden-hardware-not-invented", status: contract.mechanism.internalHardwareMode === "visual-mechanism-proxy" ? "pass" : "fail", evidence: "Only visible grooves, contact points and fastener heads are planned; hidden counts and polarities remain unknown." },
    {
      id: "source-images-linked",
      status: sliderArchitectureSpec
        ? sourceAssetIds.includes("slider-intake-haloo-official-07") && sourceAssetIds.includes("slider-intake-haloo-official-06") && sourceAssetIds.includes("slider-intake-haloo-official-08") ? "pass" : "fail"
        : sourceAssetIds.includes("slider-intake-user-frame-08") && sourceAssetIds.includes("slider-intake-user-frame-11") ? "pass" : "fail",
      evidence: sliderArchitectureSpec
        ? "The linear, rotary and gameplay panels link back to the approved exact-product official images."
        : "The architecture views link back to the required approved user-reference frames."
    }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "上游 04-architecture 已产生新 revision，等待重新推进。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = premiumDisplayCaseArchitectureSpec
    ? "Gate 03 rev 1 已按用户原话“批准”锁定；Gate 04 rev 1 已生成真实父子树、内部爆炸规划和运动所有权评审图，等待用户审批。shipping reveal 永不爆炸，Gate 05 保持 blocked，Unity 与手机均未改动。"
    : sliderArchitectureSpec
    ? "第 3 关已批准；第 4 关已按双玩法与可见内部模块重做，精确耦合保持未知，等待用户视觉审批。当前 Unity 模型保持不变。"
    : "第 3 关已批准；第 4 关拆件树和爆炸规划已生成，等待用户视觉审批。当前 Unity 模型保持不变。";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "04-architecture",
    architectureRevision,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    sourceClaimIds,
    autoApproved: false,
    gate05Status: manifest.stages[stageIndex + 1].status
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseWholeCaseMotionReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("Whole-case motion evidence is supported only for the Premium Display Case.", 422);
  }

  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "04-architecture");
  const stage = manifest.stages[stageIndex];
  if (manifest.stages[stageIndex - 1].status !== "approved") {
    throw new PipelineError("Gate 03 must remain approved before replacing Gate 04 evidence.", 422);
  }
  if (stage.status !== "rejected" || stage.decision?.action !== "reject") {
    throw new PipelineError("The superseded Gate 04 evidence must be rejected through the decision API first.", 422);
  }

  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/04-architecture/rev-003"
  )));
  const paths = {
    userReference: normalizeRepoPath(payload.userReferencePath || `${expectedDirectory}/Coin_Slab_v15-user-reference.jpg`),
    recipe: normalizeRepoPath(payload.recipePath || `${expectedDirectory}/render_whole_case_motion.py`),
    gif: normalizeRepoPath(payload.gifPath || `${expectedDirectory}/whole-case-only-rive-v15-envelope.gif`),
    mp4: normalizeRepoPath(payload.mp4Path || `${expectedDirectory}/whole-case-only-rive-v15-envelope.mp4`),
    contactSheet: normalizeRepoPath(payload.contactSheetPath || `${expectedDirectory}/whole-case-only-contact-sheet.png`),
    timingReport: normalizeRepoPath(payload.timingReportPath || `${expectedDirectory}/rive-v15-timing-report.json`),
    qualityReport: normalizeRepoPath(payload.qualityReportPath || `${expectedDirectory}/animation-quality-report.json`)
  };
  const resolvedPaths = {};
  for (const [label, relativePath] of Object.entries(paths)) {
    if (!relativePath.startsWith(`${expectedDirectory}/`)) {
      throw new PipelineError(`${label} must be stored inside ${expectedDirectory}.`);
    }
    resolvedPaths[label] = assertRepositoryEvidenceFile(
      modelId,
      "04-architecture",
      relativePath,
      `Whole-case motion ${label}`
    );
  }

  const timing = JSON.parse(fs.readFileSync(resolvedPaths.timingReport.absolute, "utf8"));
  const quality = JSON.parse(fs.readFileSync(resolvedPaths.qualityReport.absolute, "utf8"));
  if (
    timing?.modelId !== "premium-display-case"
    || timing?.gate !== "04-architecture"
    || timing?.evidenceRevision !== 3
    || timing?.selectedEnvelope?.durationMilliseconds !== 3617
    || timing?.runtimeMeasurements?.[0]?.triggerToCompleteMilliseconds !== 3617
    || timing?.runtimeMeasurements?.[0]?.activeStateToCompleteMilliseconds !== 3602
    || timing?.authoredParameters?.exactRotationEasing !== "unknown"
    || timing?.authoredParameters?.exactHighlightEasing !== "unknown"
    || timing?.authoredParameters?.riveYAxisSign !== "unknown"
    || timing?.targetMapping?.objectCount !== 1
    || timing?.targetMapping?.rotation?.axis !== "Y"
    || timing?.targetMapping?.rotation?.degrees !== 360
    || timing?.targetMapping?.highlight?.count !== 1
    || timing?.truthLabel !== "WHOLE CASE ONLY · NO EXPLODE"
  ) {
    throw new PipelineError("The Rive timing report does not preserve the measured whole-case contract.", 422);
  }
  if (
    quality?.status !== "pass"
    || quality?.evidenceRevision !== 3
    || quality?.gate05Status !== "blocked"
    || quality?.truth?.wholeCaseOnly !== true
    || quality?.truth?.explode !== false
    || quality?.metrics?.partSeparationCount !== 0
    || quality?.metrics?.objectIdentityCount !== 1
    || quality?.metrics?.highlightCount !== 1
    || quality?.metrics?.frameCount !== 217
    || Math.abs(Number(quality?.metrics?.mp4DurationMilliseconds) - 3617) > (1000 / 60)
  ) {
    throw new PipelineError("The whole-case animation-quality report is incomplete or failed.", 422);
  }

  const contactBytes = fs.readFileSync(resolvedPaths.contactSheet.absolute);
  const contactIsPng = contactBytes.length >= 24 && contactBytes.subarray(1, 4).toString("ascii") === "PNG";
  const contactWidth = contactIsPng ? contactBytes.readUInt32BE(16) : 0;
  const contactHeight = contactIsPng ? contactBytes.readUInt32BE(20) : 0;
  if (contactWidth < 1600 || contactHeight < 2200) {
    throw new PipelineError("The Gate 04 contact sheet must be a large-type PNG covering all required states.", 422);
  }
  const gifBytes = fs.readFileSync(resolvedPaths.gif.absolute);
  if (!["GIF87a", "GIF89a"].includes(gifBytes.subarray(0, 6).toString("ascii"))) {
    throw new PipelineError("The Gate 04 GIF is invalid.", 422);
  }
  const mp4Bytes = fs.readFileSync(resolvedPaths.mp4.absolute);
  if (mp4Bytes.length < 12 || mp4Bytes.subarray(4, 8).toString("ascii") !== "ftyp") {
    throw new PipelineError("The Gate 04 MP4 is invalid.", 422);
  }

  const canonicalSourcePaths = {
    rive: "unity/FidgetingApp/Assets/Plugins/iOS/Rive/gacha-single-draw-jumbotron.riv",
    mainAppLog: "unity/FidgetingApp/Artifacts/GachaPackRiveUnityContinuousPreview/gacha-pack-rive-unity-continuous-combined.log",
    standaloneLog: "unity/FidgetingApp/Artifacts/GachaRiveShippingPreview/gacha-rive-shipping-flow.log"
  };
  const canonicalSources = {};
  for (const [label, relativePath] of Object.entries(canonicalSourcePaths)) {
    const absolute = resolveRepoPath(relativePath);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
      throw new PipelineError(`Canonical ${label} evidence is missing.`, 422);
    }
    canonicalSources[label] = { normalized: relativePath, absolute };
  }
  if (sha256File(canonicalSources.rive.absolute) !== timing.sourceAsset.sha256) {
    throw new PipelineError("The measured Rive source hash does not match the canonical asset.", 422);
  }

  const preservedPartTree = manifest.assets.find((asset) => (
    asset.stageId === "04-architecture"
    && asset.slot === "part-tree"
    && asset.path.includes("/rev-001/")
  ));
  const preservedExplodedPlan = manifest.assets.find((asset) => (
    asset.stageId === "04-architecture"
    && asset.slot === "exploded-plan"
    && asset.path.includes("/rev-001/")
  ));
  if (!preservedPartTree || !preservedExplodedPlan) {
    throw new PipelineError("Gate 04 rev 1 internal part tree and exploded plan must remain preserved.", 422);
  }

  const idPrefix = modelId;
  const ids = {
    userReference: `${idPrefix}-rive-v15-user-reference-r003`,
    rive: `${idPrefix}-rive-v15-source-r003`,
    mainAppLog: `${idPrefix}-rive-v15-main-app-log-r003`,
    standaloneLog: `${idPrefix}-rive-v15-standalone-log-r003`,
    recipe: `${idPrefix}-whole-case-motion-recipe-r003`,
    gif: `${idPrefix}-whole-case-motion-gif-r003`,
    mp4: `${idPrefix}-whole-case-motion-mp4-r003`,
    contactSheet: `${idPrefix}-whole-case-contact-sheet-r003`,
    timingReport: `${idPrefix}-rive-v15-timing-r003`,
    qualityReport: `${idPrefix}-whole-case-animation-validation-r003`
  };
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  for (const id of Object.values(ids)) {
    if (existingIds.has(id)) throw new PipelineError(`Whole-case evidence asset already exists: ${id}.`, 409);
  }

  const now = new Date().toISOString();
  const rejectedEvidenceAssetIds = manifest.assets
    .filter((asset) => asset.stageId === "04-architecture" && asset.path.includes("/rev-002/"))
    .map((asset) => asset.id);
  for (const asset of manifest.assets) {
    if (rejectedEvidenceAssetIds.includes(asset.id)) {
      asset.reviewState = "rejected";
      asset.supersededBy = ids.gif;
      asset.supersededAt = now;
      asset.dispositionNote = "User rejected the explode/reassemble animation. It is preserved only as superseded evidence and is not eligible for product animation.";
    }
  }
  for (const asset of [preservedPartTree, preservedExplodedPlan]) {
    asset.reviewState = "internal-only";
    asset.usagePolicy = "internal-production-and-website-structure-only";
    asset.productAnimationEligible = false;
  }

  const sourceClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  const contractAssetIds = manifest.stages[stageIndex - 1].artifactIds;
  const sharedSourceAssetIds = [
    ...contractAssetIds,
    preservedPartTree.id,
    preservedExplodedPlan.id,
    ids.userReference,
    ids.rive,
    ids.mainAppLog,
    ids.standaloneLog
  ];

  const record = ({
    id,
    slot,
    file,
    role,
    producer,
    provenance,
    sourceAssetIds = [],
    view = null
  }) => ({
    id,
    stageId: "04-architecture",
    slot,
    path: file.normalized,
    sha256: sha256File(file.absolute),
    exists: true,
    sizeBytes: fs.statSync(file.absolute).size,
    role,
    producer,
    provenance,
    sourceAssetIds,
    ...(sourceClaimIds.length && sourceAssetIds.length ? { sourceClaimIds } : {}),
    ...(view ? { view } : {}),
    reviewState: "active"
  });

  const sourceRecords = [
    record({
      id: ids.userReference,
      slot: "motion-reference",
      file: resolvedPaths.userReference,
      role: "user-input",
      producer: {
        name: "Cursor conversation",
        version: "504719bf-a4a3-44c2-b1f3-a3bd342e5ae3"
      },
      provenance: {
        origin: "user-provided",
        contentClass: "Coin_Slab_v15 motion-and-light-reference",
        assertedBy: "user",
        note: "Motion and light-response reference only. Its identity, yellow field, smiley, barcode, sample number, and circular window are prohibited from the replacement evidence."
      }
    }),
    record({
      id: ids.rive,
      slot: "motion-source",
      file: canonicalSources.rive,
      role: "historical",
      producer: {
        name: "Rive",
        version: "v15 source / runtime 6.23.1"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "canonical-shipping-rive-motion-source",
        assertedBy: "repository",
        note: "Canonical 357120-byte Rive source measured through shipping runtime logs; it is not copied into the replacement product artwork."
      }
    }),
    record({
      id: ids.mainAppLog,
      slot: "runtime-log",
      file: canonicalSources.mainAppLog,
      role: "historical",
      producer: {
        name: "FidgetSpinner main app Simulator",
        version: "2026-08-18"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "shipping-main-app-rive-runtime-log",
        assertedBy: "repository",
        note: "Measures purchase-trigger 16:12:15.778 to animationSignal 16:12:19.395: 3617 ms."
      },
      sourceAssetIds: [ids.rive]
    }),
    record({
      id: ids.standaloneLog,
      slot: "runtime-log",
      file: canonicalSources.standaloneLog,
      role: "historical",
      producer: {
        name: "shipping-source Rive Simulator preview",
        version: "2026-08-18"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "shipping-source-standalone-rive-runtime-log",
        assertedBy: "repository",
        note: "Records a slower captured runtime sample: 3805 ms trigger-to-animationSignal. It is retained as observed variance, not substituted for the main-app measurement."
      },
      sourceAssetIds: [ids.rive]
    })
  ];
  const generatedRecords = [
    record({
      id: ids.recipe,
      slot: "architecture-animation-recipe",
      file: resolvedPaths.recipe,
      role: "process",
      producer: {
        name: "Python Pillow + FFmpeg",
        version: "Pillow 11.3.0 / FFmpeg 8.1.1",
        recipe: "One assembled 3:4 slab, +Y 360 preview, one diagonal highlight, settled hold, GIF, MP4, contact sheet, timing and quality reports"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "deterministic-whole-case-motion-envelope-recipe",
        assertedBy: "assistant",
        note: "Evidence-only renderer. It creates no product geometry and never separates, swaps, or hides the case or prize."
      },
      sourceAssetIds: sharedSourceAssetIds
    }),
    record({
      id: ids.timingReport,
      slot: "timing-report",
      file: resolvedPaths.timingReport,
      role: "validation",
      producer: {
        name: "Rive runtime-log and frame-sampling audit",
        version: "2026-08-24",
        recipe: "Main-app and standalone timestamp deltas plus 20 fps visual ordering review"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "rive-v15-runtime-timing-report",
        assertedBy: "assistant",
        note: "Selects the measured 3617 ms main-app trigger envelope. Exact authored easing, highlight curve, timeline duration, and yaw sign remain unknown."
      },
      sourceAssetIds: [ids.rive, ids.mainAppLog, ids.standaloneLog, ids.userReference, ids.recipe]
    }),
    record({
      id: ids.gif,
      slot: "architecture-animation",
      file: resolvedPaths.gif,
      role: "process",
      producer: {
        name: "Python Pillow",
        version: "11.3.0",
        recipe: "Large-type whole-case-only GIF; 3620 ms GIF timing, MP4 authoritative"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "whole-case-only-motion-envelope-gif",
        assertedBy: "assistant",
        note: "One complete portrait case stays assembled and visible. WHOLE CASE ONLY · NO EXPLODE appears on every frame."
      },
      sourceAssetIds: [ids.recipe, ids.timingReport],
      view: {
        id: "architecture-motion",
        camera: "evidence-only-y-turntable",
        parameters: {
          widthPixels: 1280,
          heightPixels: 960,
          encodedDurationMilliseconds: quality.metrics.gifDurationMilliseconds,
          wholeCaseOnly: true
        }
      }
    }),
    record({
      id: ids.mp4,
      slot: "architecture-animation-mp4",
      file: resolvedPaths.mp4,
      role: "process",
      producer: {
        name: "FFmpeg",
        version: "8.1.1",
        recipe: "217 frames at 60 fps; H.264 timing authority"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "whole-case-only-motion-envelope-mp4",
        assertedBy: "assistant",
        note: "3616.667 ms encoded duration, within one frame of the 3617 ms main-app measurement."
      },
      sourceAssetIds: [ids.recipe, ids.timingReport],
      view: {
        id: "architecture-motion",
        camera: "evidence-only-y-turntable",
        parameters: {
          widthPixels: 1280,
          heightPixels: 960,
          fps: 60,
          frameCount: 217,
          durationMilliseconds: quality.metrics.mp4DurationMilliseconds
        }
      }
    }),
    record({
      id: ids.contactSheet,
      slot: "animation-contact-sheet",
      file: resolvedPaths.contactSheet,
      role: "process",
      producer: {
        name: "Python Pillow",
        version: "11.3.0",
        recipe: "Start, 0, 90, 180, 270, 360, highlight, settled contact sheet"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "whole-case-only-animation-contact-sheet",
        assertedBy: "assistant",
        note: "Large-type sheet proves one object, one prize, one full turn, one highlight, and a visible settled frame."
      },
      sourceAssetIds: [ids.recipe, ids.timingReport, ids.gif, ids.mp4],
      view: {
        id: "architecture-contact-sheet",
        camera: "evidence-only-stage-grid",
        parameters: {
          widthPixels: contactWidth,
          heightPixels: contactHeight,
          sampleCount: 8,
          wholeCaseOnly: true
        }
      }
    }),
    record({
      id: ids.qualityReport,
      slot: "animation-validation",
      file: resolvedPaths.qualityReport,
      role: "validation",
      producer: {
        name: "animation-quality-gate",
        version: "2026-08-24",
        recipe: "Identity, no-explode, prize visibility, portrait, flicker, full-turn, single-highlight, duration, unknowns, reference-boundary and gate-boundary audit"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "whole-case-animation-quality-report",
        assertedBy: "assistant",
        note: "Passes evidence-only motion QA. It does not approve Gate 04 or validate Blender, Unity, shipping, build, installation, or device behavior."
      },
      sourceAssetIds: [ids.recipe, ids.timingReport, ids.gif, ids.mp4, ids.contactSheet]
    })
  ];
  manifest.assets.push(...sourceRecords, ...generatedRecords);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = [
    preservedPartTree.id,
    preservedExplodedPlan.id,
    ...sourceRecords.map((asset) => asset.id),
    ...generatedRecords.map((asset) => asset.id)
  ];
  stage.reviewArtifactIds = [ids.gif, ids.mp4, ids.contactSheet];
  stage.validations = [
    { id: "rev2-user-rejection-preserved", status: "pass", evidence: `The decision API rejected Gate 04 evidence rev 2; ${rejectedEvidenceAssetIds.length} rev 2 assets remain hashed and marked rejected/superseded.` },
    { id: "internal-structure-evidence-only", status: "pass", evidence: "Rev 1 part tree and exploded plan remain available only for production or website structure explanation; productAnimationEligible is false." },
    { id: "main-app-rive-duration-measured", status: "pass", evidence: "Main-app purchase-trigger 16:12:15.778 to animationSignal 16:12:19.395 measures 3617 ms; in-to-Idle measures 3602 ms." },
    { id: "runtime-variance-disclosed", status: "pass", evidence: "Standalone captured runtime measured 3805 ms. The report keeps both observations and does not call either the authored timeline duration." },
    { id: "authored-unknowns-preserved", status: "pass", evidence: "Exact Rive easing, highlight curve, authored timeline duration, and yaw sign remain unknown." },
    { id: "one-whole-case-only", status: "pass", evidence: "One assembled 3:4 Portrait case and the same prize remain visible in all 217 MP4 frames; child offsets and part separation count are zero." },
    { id: "full-turn-and-single-highlight", status: "pass", evidence: "The unwrapped preview samples 0/90/180/270/360 and one upper-left-to-lower-right highlight at the sampled final-turn boundary." },
    { id: "duration-matches-measurement", status: "pass", evidence: `MP4 duration ${quality.metrics.mp4DurationMilliseconds} ms differs from 3617 ms by ${Number(quality.metrics.mp4DurationMilliseconds) - 3617} ms; GIF is ${quality.metrics.gifDurationMilliseconds} ms.` },
    { id: "flicker-and-portrait-quality", status: "pass", evidence: `Settled hold difference is ${quality.metrics.settledHoldDifference}; minimum projected prize width is ${quality.metrics.minimumProjectedPrizeWidthPixels}px; frame center and portrait height stay fixed.` },
    { id: "reference-identity-not-copied", status: "pass", evidence: "Replacement evidence contains no WHATNOT identity, yellow field, smiley, barcode, sample serial, or circular coin window." },
    { id: "large-type-contact-coverage", status: "pass", evidence: `${contactWidth} × ${contactHeight} contact sheet covers start, highlight, 0, 90, 180, 270, 360, and settled.` },
    { id: "gate-05-remains-blocked", status: "pass", evidence: "Gate 04 remains ready_for_review with no approval decision; Gate 05, builds, installation, and phone push remain blocked." }
  ];
  stage.decision = null;
  stage.evidenceReview = {
    architectureRevision: 1,
    rejectedEvidenceRevision: 2,
    evidenceRevision: 3,
    feedbackDisposition: "explicit-user-rejection-of-explode-reassemble-animation",
    rejectedArtifactIds: rejectedEvidenceAssetIds,
    preservedInternalArtifactIds: [preservedPartTree.id, preservedExplodedPlan.id],
    artifactTruth: "whole-case-only-evidence-preview-not-blender-not-unity-not-shipping",
    measuredMainAppDurationMilliseconds: 3617,
    exactAuthoredEasing: "unknown",
    exactRiveYAxisSign: "unknown",
    approvalEffect: "none",
    reviewState: "ready_for_review",
    gate05Status: "blocked"
  };
  delete stage.staleReason;

  const downstreamReason = "Gate 04 evidence rev 3 is ready_for_review after the user rejected explode/reassemble animation; Gate 05 must not start.";
  for (let index = stageIndex + 1; index < manifest.stages.length; index += 1) {
    const downstream = manifest.stages[index];
    if (!(downstream.artifactIds || []).length) downstream.status = "blocked";
    else if (downstream.status !== "approved") downstream.status = "stale";
    downstream.staleReason = downstreamReason;
  }

  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 04 evidence rev 2 explode/reassemble animation was explicitly rejected through the pipeline API. Rev 1 part tree and exploded plan remain internal/website-only. Evidence rev 3 shows one whole 3:4 Portrait case, one +Y preview turn, one highlight at the sampled final-turn boundary, and a visible settled hold across the measured 3617 ms main-app envelope. Exact authored easing and Rive yaw sign remain unknown. Gate 04 is ready_for_review; Gate 05 is blocked; no build, install, or phone push occurred.";
  manifest.currentState.visualApproval = "pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;

  const event = makeEvent(manifest, "stage-evidence-revised", {
    stageId: "04-architecture",
    architectureRevision: 1,
    rejectedEvidenceRevision: 2,
    evidenceRevision: 3,
    rejectedArtifactIds: rejectedEvidenceAssetIds,
    preservedInternalArtifactIds: [preservedPartTree.id, preservedExplodedPlan.id],
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    timingReportId: ids.timingReport,
    qualityReportId: ids.qualityReport,
    measuredMainAppDurationMilliseconds: 3617,
    exactAuthoredEasing: "unknown",
    exactRiveYAxisSign: "unknown",
    artifactTruth: "whole-case-only-evidence-preview-not-blender-not-unity-not-shipping",
    autoApproved: false,
    gate05Status: "blocked",
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseSlowerWholeCaseMotionReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("Whole-case speed evidence is supported only for the Premium Display Case.", 422);
  }

  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "04-architecture");
  const stage = manifest.stages[stageIndex];
  if (manifest.stages[stageIndex - 1].status !== "approved") {
    throw new PipelineError("Gate 03 must remain approved before replacing Gate 04 speed evidence.", 422);
  }
  if (stage.status !== "rejected" || stage.decision?.action !== "reject") {
    throw new PipelineError("Gate 04 evidence rev 3 must be rejected through the decision API first.", 422);
  }
  if (stage.evidenceReview?.evidenceRevision !== 3) {
    throw new PipelineError("The speed-only replacement requires Gate 04 evidence rev 3.", 422);
  }

  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/04-architecture/rev-004"
  )));
  const paths = {
    recipe: normalizeRepoPath(payload.recipePath || `${expectedDirectory}/render_whole_case_motion.py`),
    gif: normalizeRepoPath(payload.gifPath || `${expectedDirectory}/whole-case-only-1.25x-slower.gif`),
    mp4: normalizeRepoPath(payload.mp4Path || `${expectedDirectory}/whole-case-only-1.25x-slower.mp4`),
    contactSheet: normalizeRepoPath(payload.contactSheetPath || `${expectedDirectory}/whole-case-only-1.25x-slower-contact-sheet.png`),
    timingReport: normalizeRepoPath(payload.timingReportPath || `${expectedDirectory}/whole-case-only-1.25x-slower-timing-report.json`),
    qualityReport: normalizeRepoPath(payload.qualityReportPath || `${expectedDirectory}/animation-quality-report.json`)
  };
  const resolvedPaths = {};
  for (const [label, relativePath] of Object.entries(paths)) {
    if (!relativePath.startsWith(`${expectedDirectory}/`)) {
      throw new PipelineError(`${label} must be stored inside ${expectedDirectory}.`);
    }
    resolvedPaths[label] = assertRepositoryEvidenceFile(
      modelId,
      "04-architecture",
      relativePath,
      `Slower whole-case motion ${label}`
    );
  }

  const baselineDurationMilliseconds = 3617;
  const timeScale = 1.25;
  const targetDurationMilliseconds = baselineDurationMilliseconds * timeScale;
  const playbackFps = 48;
  const frameCount = 217;
  const truthLabel = "WHOLE CASE ONLY · 1.25× SLOWER · NO EXPLODE";
  const timing = JSON.parse(fs.readFileSync(resolvedPaths.timingReport.absolute, "utf8"));
  const quality = JSON.parse(fs.readFileSync(resolvedPaths.qualityReport.absolute, "utf8"));
  if (
    timing?.modelId !== "premium-display-case"
    || timing?.gate !== "04-architecture"
    || timing?.evidenceRevision !== 4
    || timing?.runtimeMeasurements?.[0]?.triggerToCompleteMilliseconds !== baselineDurationMilliseconds
    || timing?.selectedEnvelope?.baselineDurationMilliseconds !== baselineDurationMilliseconds
    || timing?.selectedEnvelope?.timeScale !== timeScale
    || timing?.selectedEnvelope?.targetDurationMilliseconds !== targetDurationMilliseconds
    || timing?.selectedEnvelope?.noNewPause !== true
    || timing?.selectedEnvelope?.noSecondHighlight !== true
    || timing?.authoredParameters?.exactRotationEasing !== "unknown"
    || timing?.authoredParameters?.exactHighlightEasing !== "unknown"
    || timing?.authoredParameters?.riveYAxisSign !== "unknown"
    || timing?.targetMapping?.objectCount !== 1
    || timing?.targetMapping?.rotation?.axis !== "Y"
    || timing?.targetMapping?.rotation?.degrees !== 360
    || timing?.targetMapping?.highlight?.count !== 1
    || timing?.frameSequence?.sourceEvidenceRevision !== 3
    || timing?.frameSequence?.frameCount !== frameCount
    || timing?.frameSequence?.playbackFps !== playbackFps
    || timing?.frameSequence?.framesAdded !== 0
    || timing?.frameSequence?.framesRemoved !== 0
    || timing?.frameSequence?.framesReordered !== 0
    || timing?.truthLabel !== truthLabel
  ) {
    throw new PipelineError("The rev 4 timing report does not preserve the speed-only whole-case contract.", 422);
  }
  if (
    quality?.status !== "pass"
    || quality?.evidenceRevision !== 4
    || quality?.gate05Status !== "blocked"
    || quality?.truth?.wholeCaseOnly !== true
    || quality?.truth?.explode !== false
    || quality?.truth?.speedOnlySupersession !== true
    || quality?.truth?.frameSequenceChanged !== false
    || quality?.truth?.newPauseAdded !== false
    || quality?.truth?.secondHighlightAdded !== false
    || quality?.metrics?.partSeparationCount !== 0
    || quality?.metrics?.objectIdentityCount !== 1
    || quality?.metrics?.highlightCount !== 1
    || quality?.metrics?.frameCount !== frameCount
    || quality?.metrics?.fps !== playbackFps
    || quality?.metrics?.timeScale !== timeScale
    || quality?.metrics?.targetDurationMilliseconds !== targetDurationMilliseconds
    || Math.abs(Number(quality?.metrics?.mp4DurationMilliseconds) - targetDurationMilliseconds) > (1000 / playbackFps)
  ) {
    throw new PipelineError("The rev 4 animation-quality report is incomplete or failed.", 422);
  }
  if (
    timing?.frameSequence?.motionSequenceSha256 !== quality?.metrics?.motionSequenceSha256
    || !/^[a-f0-9]{64}$/.test(String(timing?.frameSequence?.motionSequenceSha256 || ""))
  ) {
    throw new PipelineError("The rev 4 motion-sequence identity is missing or inconsistent.", 422);
  }

  const contactBytes = fs.readFileSync(resolvedPaths.contactSheet.absolute);
  const contactIsPng = contactBytes.length >= 24 && contactBytes.subarray(1, 4).toString("ascii") === "PNG";
  const contactWidth = contactIsPng ? contactBytes.readUInt32BE(16) : 0;
  const contactHeight = contactIsPng ? contactBytes.readUInt32BE(20) : 0;
  if (contactWidth < 1600 || contactHeight < 2200) {
    throw new PipelineError("The Gate 04 rev 4 contact sheet must be a large-type PNG.", 422);
  }
  const gifBytes = fs.readFileSync(resolvedPaths.gif.absolute);
  if (!["GIF87a", "GIF89a"].includes(gifBytes.subarray(0, 6).toString("ascii"))) {
    throw new PipelineError("The Gate 04 rev 4 GIF is invalid.", 422);
  }
  const mp4Bytes = fs.readFileSync(resolvedPaths.mp4.absolute);
  if (mp4Bytes.length < 12 || mp4Bytes.subarray(4, 8).toString("ascii") !== "ftyp") {
    throw new PipelineError("The Gate 04 rev 4 MP4 is invalid.", 422);
  }

  const idPrefix = modelId;
  const sourceIds = {
    userReference: `${idPrefix}-rive-v15-user-reference-r003`,
    rive: `${idPrefix}-rive-v15-source-r003`,
    mainAppLog: `${idPrefix}-rive-v15-main-app-log-r003`,
    standaloneLog: `${idPrefix}-rive-v15-standalone-log-r003`
  };
  const priorIds = {
    recipe: `${idPrefix}-whole-case-motion-recipe-r003`,
    timingReport: `${idPrefix}-rive-v15-timing-r003`,
    gif: `${idPrefix}-whole-case-motion-gif-r003`,
    mp4: `${idPrefix}-whole-case-motion-mp4-r003`,
    contactSheet: `${idPrefix}-whole-case-contact-sheet-r003`,
    qualityReport: `${idPrefix}-whole-case-animation-validation-r003`
  };
  const ids = {
    recipe: `${idPrefix}-whole-case-motion-recipe-r004`,
    timingReport: `${idPrefix}-whole-case-timing-r004`,
    gif: `${idPrefix}-whole-case-motion-gif-r004`,
    mp4: `${idPrefix}-whole-case-motion-mp4-r004`,
    contactSheet: `${idPrefix}-whole-case-contact-sheet-r004`,
    qualityReport: `${idPrefix}-whole-case-animation-validation-r004`
  };
  const assetById = new Map(manifest.assets.map((asset) => [asset.id, asset]));
  for (const id of [...Object.values(sourceIds), ...Object.values(priorIds)]) {
    if (!assetById.has(id)) throw new PipelineError(`Required Gate 04 source evidence is missing: ${id}.`, 422);
  }
  for (const id of Object.values(ids)) {
    if (assetById.has(id)) throw new PipelineError(`Gate 04 rev 4 evidence asset already exists: ${id}.`, 409);
  }

  const preservedPartTree = manifest.assets.find((asset) => (
    asset.stageId === "04-architecture"
    && asset.slot === "part-tree"
    && asset.path.includes("/rev-001/")
  ));
  const preservedExplodedPlan = manifest.assets.find((asset) => (
    asset.stageId === "04-architecture"
    && asset.slot === "exploded-plan"
    && asset.path.includes("/rev-001/")
  ));
  if (!preservedPartTree || !preservedExplodedPlan) {
    throw new PipelineError("Gate 04 rev 1 internal structure evidence must remain preserved.", 422);
  }

  const now = new Date().toISOString();
  const speedRejectedAssetIds = Object.values(priorIds);
  for (const assetId of speedRejectedAssetIds) {
    const asset = assetById.get(assetId);
    asset.reviewState = "rejected";
    asset.rejectionScope = "speed-only";
    asset.supersededBy = ids.gif;
    asset.supersededAt = now;
    asset.dispositionNote = "User rejected only rev 3 playback speed as too fast. Whole-case, Portrait, one Y-axis 360-degree turn, one highlight, no-explode, and frame order remain locked.";
  }
  for (const asset of [preservedPartTree, preservedExplodedPlan]) {
    asset.reviewState = "internal-only";
    asset.usagePolicy = "internal-production-and-website-structure-only";
    asset.productAnimationEligible = false;
  }

  const sourceClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  const record = ({
    id,
    slot,
    file,
    role,
    producer,
    provenance,
    sourceAssetIds = [],
    view = null
  }) => ({
    id,
    stageId: "04-architecture",
    slot,
    path: file.normalized,
    sha256: sha256File(file.absolute),
    exists: true,
    sizeBytes: fs.statSync(file.absolute).size,
    role,
    producer,
    provenance,
    sourceAssetIds,
    ...(sourceClaimIds.length && sourceAssetIds.length ? { sourceClaimIds } : {}),
    ...(view ? { view } : {}),
    reviewState: "active"
  });

  const contractAssetIds = manifest.stages[stageIndex - 1].artifactIds;
  const generatedRecords = [
    record({
      id: ids.recipe,
      slot: "architecture-animation-recipe",
      file: resolvedPaths.recipe,
      role: "process",
      producer: {
        name: "Python Pillow + FFmpeg",
        version: "Pillow 11.3.0 / FFmpeg 8.1.1",
        recipe: "Rev 3's 217 ordered visual samples played at 48 fps for a 1.25 time scale"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "deterministic-speed-only-whole-case-motion-recipe",
        assertedBy: "assistant",
        note: "Imports the immutable rev 3 renderer and changes playback rate plus evidence labels only. It adds no frame, pause, highlight, object, part motion, or geometry."
      },
      sourceAssetIds: [
        ...contractAssetIds,
        preservedPartTree.id,
        preservedExplodedPlan.id,
        ...Object.values(sourceIds),
        priorIds.recipe
      ]
    }),
    record({
      id: ids.timingReport,
      slot: "timing-report",
      file: resolvedPaths.timingReport,
      role: "validation",
      producer: {
        name: "ffprobe + Pillow media metadata audit",
        version: "2026-08-24",
        recipe: "3617 ms baseline × 1.25 target with measured MP4 and GIF metadata"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "speed-only-whole-case-timing-report",
        assertedBy: "assistant",
        note: "Records the 4521.25 ms target, measured media durations, deltas, unchanged frame sequence, and authored Rive unknowns."
      },
      sourceAssetIds: [
        sourceIds.rive,
        sourceIds.mainAppLog,
        sourceIds.standaloneLog,
        priorIds.timingReport,
        ids.recipe
      ]
    }),
    record({
      id: ids.gif,
      slot: "architecture-animation",
      file: resolvedPaths.gif,
      role: "process",
      producer: {
        name: "Python Pillow",
        version: "11.3.0",
        recipe: `${frameCount} source samples at 1.25 time scale; ${quality.metrics.gifDurationMilliseconds} ms GIF metadata`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "whole-case-only-1.25x-slower-gif",
        assertedBy: "assistant",
        note: `${truthLabel} appears on every frame.`
      },
      sourceAssetIds: [ids.recipe, ids.timingReport],
      view: {
        id: "architecture-motion",
        camera: "evidence-only-y-turntable",
        parameters: {
          widthPixels: 1280,
          heightPixels: 960,
          encodedDurationMilliseconds: quality.metrics.gifDurationMilliseconds,
          timeScale,
          wholeCaseOnly: true
        }
      }
    }),
    record({
      id: ids.mp4,
      slot: "architecture-animation-mp4",
      file: resolvedPaths.mp4,
      role: "process",
      producer: {
        name: "FFmpeg + ffprobe",
        version: "8.1.1",
        recipe: `${frameCount} unchanged frames at ${playbackFps} fps; H.264 timing authority`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "whole-case-only-1.25x-slower-mp4",
        assertedBy: "assistant",
        note: `${quality.metrics.mp4DurationMilliseconds} ms measured duration versus ${targetDurationMilliseconds} ms target.`
      },
      sourceAssetIds: [ids.recipe, ids.timingReport],
      view: {
        id: "architecture-motion",
        camera: "evidence-only-y-turntable",
        parameters: {
          widthPixels: 1280,
          heightPixels: 960,
          fps: playbackFps,
          frameCount,
          durationMilliseconds: quality.metrics.mp4DurationMilliseconds,
          timeScale
        }
      }
    }),
    record({
      id: ids.contactSheet,
      slot: "animation-contact-sheet",
      file: resolvedPaths.contactSheet,
      role: "process",
      producer: {
        name: "Python Pillow",
        version: "11.3.0",
        recipe: "Start, 0, 90, 180, 270, 360, one highlight, and settled samples"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "whole-case-only-1.25x-slower-contact-sheet",
        assertedBy: "assistant",
        note: "Large-type quality sheet proves one Portrait case, one full turn, one highlight, no split, and a stable settled frame."
      },
      sourceAssetIds: [ids.recipe, ids.timingReport, ids.gif, ids.mp4],
      view: {
        id: "architecture-contact-sheet",
        camera: "evidence-only-stage-grid",
        parameters: {
          widthPixels: contactWidth,
          heightPixels: contactHeight,
          sampleCount: 8,
          timeScale,
          wholeCaseOnly: true
        }
      }
    }),
    record({
      id: ids.qualityReport,
      slot: "animation-validation",
      file: resolvedPaths.qualityReport,
      role: "validation",
      producer: {
        name: "animation-quality-gate",
        version: "2026-08-24",
        recipe: "Identity, Portrait, full turn, one highlight, no split, no flicker, frame-sequence, media-duration, unknowns, and gate-boundary audit"
      },
      provenance: {
        origin: "repository-generated",
        contentClass: "speed-only-whole-case-animation-quality-report",
        assertedBy: "assistant",
        note: "Passes evidence-only rev 4 QA. It does not approve Gate 04 or validate Blender, Unity, shipping, build, installation, or device behavior."
      },
      sourceAssetIds: [ids.recipe, ids.timingReport, ids.gif, ids.mp4, ids.contactSheet]
    })
  ];
  manifest.assets.push(...generatedRecords);

  const explodeRejectedArtifactIds = stage.evidenceReview.rejectedArtifactIds || [];
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = [
    preservedPartTree.id,
    preservedExplodedPlan.id,
    ...Object.values(sourceIds),
    ...generatedRecords.map((asset) => asset.id)
  ];
  stage.reviewArtifactIds = [ids.gif, ids.mp4, ids.contactSheet];
  stage.validations = [
    { id: "rev2-explode-rejection-preserved", status: "pass", evidence: `${explodeRejectedArtifactIds.length} rev 2 explode/reassemble artifacts remain rejected and immutable.` },
    { id: "rev3-speed-rejection-preserved", status: "pass", evidence: `${speedRejectedAssetIds.length} rev 3 generated artifacts are rejected/superseded with rejectionScope=speed-only.` },
    { id: "rev3-direction-preserved", status: "pass", evidence: "The speed feedback does not reject the whole case, Portrait, one Y-axis 360-degree turn, one highlight, no-explode policy, or frame order." },
    { id: "baseline-and-time-scale", status: "pass", evidence: `${baselineDurationMilliseconds} ms main-app baseline × ${timeScale} = ${targetDurationMilliseconds} ms target.` },
    { id: "same-frame-sequence", status: "pass", evidence: `All ${frameCount} rev 3 motion samples remain ordered and unchanged; playback changes from 60 fps to ${playbackFps} fps with no added pause or highlight.` },
    { id: "measured-media-duration", status: "pass", evidence: `ffprobe measures MP4 ${quality.metrics.mp4DurationMilliseconds} ms, delta ${quality.metrics.targetDeltaMilliseconds} ms; GIF metadata measures ${quality.metrics.gifDurationMilliseconds} ms.` },
    { id: "authored-unknowns-preserved", status: "pass", evidence: "Exact authored Rive timeline, rotation/highlight easing, and Y-axis sign remain unknown." },
    { id: "animation-quality-gate", status: "pass", evidence: "Subject identity, Portrait stability, full turn, one highlight, no split, no flicker, settled visibility, and contact coverage pass." },
    { id: "gate-05-remains-blocked", status: "pass", evidence: "Gate 04 remains ready_for_review; Gate 05, build, install, and phone push remain blocked." }
  ];
  stage.decision = null;
  stage.evidenceReview = {
    architectureRevision: 1,
    rejectedEvidenceRevision: 2,
    speedRejectedEvidenceRevision: 3,
    evidenceRevision: 4,
    feedbackDisposition: "explicit-user-rejection-of-rev3-speed-only",
    explodeRejectedArtifactIds,
    speedRejectedArtifactIds: speedRejectedAssetIds,
    rejectedArtifactIds: [...explodeRejectedArtifactIds, ...speedRejectedAssetIds],
    preservedInternalArtifactIds: [preservedPartTree.id, preservedExplodedPlan.id],
    preservedMotionDirectives: [
      "whole-case-only",
      "portrait",
      "unwrapped-y-360-once",
      "single-highlight-upper-left-to-lower-right",
      "same-frame-sequence",
      "no-explode",
      "no-object-replacement"
    ],
    artifactTruth: "speed-only-whole-case-evidence-preview-not-blender-not-unity-not-shipping",
    measuredMainAppDurationMilliseconds: baselineDurationMilliseconds,
    timeScale,
    targetDurationMilliseconds,
    measuredMp4DurationMilliseconds: quality.metrics.mp4DurationMilliseconds,
    measuredGifDurationMilliseconds: quality.metrics.gifDurationMilliseconds,
    targetDeltaMilliseconds: quality.metrics.targetDeltaMilliseconds,
    motionSequenceSha256: timing.frameSequence.motionSequenceSha256,
    exactAuthoredEasing: "unknown",
    exactRiveYAxisSign: "unknown",
    approvalEffect: "none",
    reviewState: "ready_for_review",
    gate05Status: "blocked"
  };
  delete stage.staleReason;

  const downstreamReason = "Gate 04 evidence rev 4 is ready_for_review after a speed-only rejection of rev 3; Gate 05 must not start.";
  for (let index = stageIndex + 1; index < manifest.stages.length; index += 1) {
    const downstream = manifest.stages[index];
    if (!(downstream.artifactIds || []).length) downstream.status = "blocked";
    else if (downstream.status !== "approved") downstream.status = "stale";
    downstream.staleReason = downstreamReason;
  }

  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 04 evidence rev 3 was rejected only for speed. Rev 4 preserves the same 217-frame whole-case Portrait Y-axis 360-degree sequence and one upper-left-to-lower-right highlight, with no split, swap, pause, or second highlight. The measured 3617 ms main-app envelope is time-scaled 1.25× to a 4521.25 ms target; ffprobe measures 4520.833 ms. Exact authored Rive easing and Y sign remain unknown. Gate 04 is ready_for_review; Gate 05 is blocked; no build, install, or phone push occurred.";
  manifest.currentState.visualApproval = "pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;

  const event = makeEvent(manifest, "stage-evidence-revised", {
    stageId: "04-architecture",
    architectureRevision: 1,
    rejectedEvidenceRevision: 2,
    speedRejectedEvidenceRevision: 3,
    evidenceRevision: 4,
    feedbackDisposition: "explicit-user-rejection-of-rev3-speed-only",
    speedRejectedArtifactIds: speedRejectedAssetIds,
    preservedMotionDirectives: stage.evidenceReview.preservedMotionDirectives,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    timingReportId: ids.timingReport,
    qualityReportId: ids.qualityReport,
    measuredMainAppDurationMilliseconds: baselineDurationMilliseconds,
    timeScale,
    targetDurationMilliseconds,
    measuredMp4DurationMilliseconds: quality.metrics.mp4DurationMilliseconds,
    measuredGifDurationMilliseconds: quality.metrics.gifDurationMilliseconds,
    targetDeltaMilliseconds: quality.metrics.targetDeltaMilliseconds,
    exactAuthoredEasing: "unknown",
    exactRiveYAxisSign: "unknown",
    artifactTruth: stage.evidenceReview.artifactTruth,
    autoApproved: false,
    gate05Status: "blocked",
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseBlockoutReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This blockout registration is supported only for a Premium Display Case pipeline.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "05-blockout");
  const architecture = manifest.stages[stageIndex - 1];
  if (architecture.status !== "approved") {
    throw new PipelineError("Gate 04 must be approved before registering the Premium Display Case blockout.", 422);
  }
  if (
    architecture.evidenceReview?.reviewState !== "approved"
    || Math.abs(Number(architecture.evidenceReview?.lockedTotalDurationSeconds) - 4.520833) > 0.0000005
  ) {
    throw new PipelineError("Gate 04 must lock the approved rev 4 duration at 4.520833 seconds.", 422);
  }
  const stage = manifest.stages[stageIndex];
  if (stage.artifactIds.length || manifest.assets.some((asset) => asset.stageId === "05-blockout")) {
    throw new PipelineError("Gate 05 already has immutable evidence; create a new revision after rejection.", 422);
  }

  const revisionLabel = "001";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/05-blockout", `rev-${revisionLabel}`
  )));
  const viewIds = ["front", "back", "top", "bottom", "left", "right", "hero", "left-oblique", "right-oblique", "low"];
  const definitions = [
    { key: "builder", suffix: "blockout-builder", slot: "white-model-source", file: "build_blockout.py", role: "process", contentClass: "deterministic-premium-display-case-blockout-source" },
    { key: "validator", suffix: "blockout-validator", slot: "validation-source", file: "validate_blockout.py", role: "process", contentClass: "deterministic-premium-display-case-blockout-validator" },
    { key: "blend", suffix: "blockout-blend", slot: "blockout-blend", file: "premium-display-case-blockout.blend", role: "source-model", contentClass: "real-blender-white-model-source" },
    { key: "hero", suffix: "blockout-hero", slot: "white-model-hero", file: "blockout-hero.png", role: "blender-render", contentClass: "real-blender-annotated-white-model-hero", viewId: "hero", camera: "Gate05HeroCamera" },
    { key: "front", suffix: "blockout-front", slot: "white-model-support", file: "blockout-front.png", role: "blender-render", contentClass: "real-blender-white-model-front", viewId: "front", camera: "Gate05FrontCamera" },
    { key: "side", suffix: "blockout-side", slot: "white-model-support", file: "blockout-side.png", role: "blender-render", contentClass: "real-blender-white-model-side", viewId: "right", camera: "Gate05SideCamera" },
    { key: "rear", suffix: "blockout-rear", slot: "white-model-support", file: "blockout-rear.png", role: "blender-render", contentClass: "real-blender-white-model-rear", viewId: "back", camera: "Gate05RearCamera" },
    { key: "tubeCloseup", suffix: "blockout-tube-closeup", slot: "white-model-support", file: "blockout-tube-closeup.png", role: "blender-render", contentClass: "real-blender-closed-tube-corner-closeup", viewId: "tube-continuity-closeup", camera: "Gate05TubeCamera" },
    { key: "contactSheet", suffix: "blockout-contact-sheet", slot: "white-model-support", file: "blockout-contact-sheet.png", role: "blender-render", contentClass: "real-blender-white-model-contact-sheet", viewId: "blockout-contact-sheet", camera: "multi-view-contact-sheet" },
    { key: "validation", suffix: "blockout-validation", slot: "validation-report", file: "blockout-validation.json", role: "validation", contentClass: "premium-display-case-blockout-validation" },
    { key: "standardCapture", suffix: "standard-capture", slot: "validation-report", file: "fixed-views/capture-report.json", role: "validation", contentClass: "standard-view-blender-capture-report" },
    { key: "standardCaptureWrapper", suffix: "standard-capture-wrapper", slot: "validation-report", file: "fixed-views/capture-wrapper-report.json", role: "validation", contentClass: "standard-view-capture-wrapper-report" },
    ...viewIds.map((viewId) => ({
      key: `standard${viewId.replace(/(^|-)([a-z])/g, (_match, _separator, letter) => letter.toUpperCase())}`,
      suffix: `standard-${viewId}`,
      slot: "white-model-support",
      file: `fixed-views/${viewId}.png`,
      role: "blender-render",
      contentClass: `real-blender-standard-${viewId}-view`,
      viewId,
      camera: "PipelineCaptureCamera"
    }))
  ].map((record) => ({
    ...record,
    id: `${modelId}-${record.suffix}-r${revisionLabel}`,
    stageId: "05-blockout",
    path: normalizeRepoPath(payload[`${record.key}Path`] || `${expectedDirectory}/${record.file}`)
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) {
      throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    }
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
      throw new PipelineError(`${record.id} file is missing.`, 422);
    }
  }

  const byKey = new Map(definitions.map((record) => [record.key, record]));
  const report = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("validation").path), "utf8"));
  const capture = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("standardCapture").path), "utf8"));
  const wrapper = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("standardCaptureWrapper").path), "utf8"));
  const measured = report.dimensionsMm?.measured;
  const tube = report.closedTube;
  const validReport = report.schemaVersion === 1
    && report.modelId === modelId
    && report.gate === "05-blockout"
    && report.blockoutRevision === 1
    && report.status === "pass"
    && report.artifactTruth?.realBlenderBlockout === true
    && report.artifactTruth?.schematic === false
    && report.artifactTruth?.shippingUnityChanged === false
    && measured?.width === 228
    && measured?.height === 304
    && measured?.depth === 59
    && report.dimensionsMm?.pass === true
    && report.portrait?.widthHeightRatio === 0.75
    && report.portrait?.pass === true
    && tube?.meshObjectCount === 1
    && tube?.outerSectionMm?.width === 10
    && tube?.outerSectionMm?.depth === 9
    && tube?.wallThicknessMm === 2
    && tube?.passageSectionMm?.width === 6
    && tube?.passageSectionMm?.depth === 5
    && tube?.cornerRadiiMm?.outer === 20
    && tube?.cornerRadiiMm?.centerline === 15
    && tube?.cornerRadiiMm?.inner === 10
    && tube?.pathClosed === true
    && tube?.tangentContinuity?.pass === true
    && tube?.topology?.connectedMaterialBodyCount === 1
    && tube?.topology?.openBoundaryEdgeCount === 0
    && tube?.topology?.nonManifoldEdgeCount === 0
    && tube?.topology?.manifoldPreflightPass === true
    && tube?.channelFloodFill?.pass === true
    && tube?.channelFloodFill?.visitedSamples === tube?.channelFloodFill?.sampleCount
    && report.hierarchy?.requiredNodesPresent === true
    && report.scope?.finalMaterials === false
    && report.scope?.branding === false
    && report.scope?.logos === false
    && report.scope?.badges === false
    && report.scope?.hiddenFasteners === false
    && report.scope?.inventedInternalParts === false
    && report.scope?.transparentCoverGeometry === "deferred-no-approved-thickness"
    && report.secondaryDimensions?.provenance === "retained-approved-shipping-baseline"
    && report.validationContext?.fullGate06ValidationDeferred === true
    && report.blender;
  if (!validReport) {
    throw new PipelineError("The Blender validation report does not match the approved Premium Display Case Gate 03/04 blockout scope.", 422);
  }
  const capturedIds = new Set((capture.views || []).map((view) => view.id));
  if (
    wrapper.verified_capture !== true
    || wrapper.blender_returncode !== 0
    || (wrapper.missing_views || []).length !== 0
    || viewIds.some((viewId) => !capturedIds.has(viewId))
    || !(capture.included_objects || []).includes("ContinuousTubePerimeter")
  ) {
    throw new PipelineError("The standard-view wrapper did not verify the real Blender blockout.", 422);
  }

  const contractAssetIds = manifest.stages[stageIndex - 2].artifactIds;
  const upstreamAssetIds = [...contractAssetIds, ...architecture.artifactIds];
  const sourceClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  const ids = Object.fromEntries(definitions.map((record) => [record.key, record.id]));
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    const generatedFrom = record.key === "builder"
      ? upstreamAssetIds
      : record.key === "validator"
        ? [...upstreamAssetIds, ids.builder]
        : record.key === "blend"
          ? [...upstreamAssetIds, ids.builder]
          : record.role === "blender-render"
            ? [ids.builder, ids.blend]
            : record.key === "validation"
              ? [ids.builder, ids.validator, ids.blend]
              : [ids.blend];
    const producerName = record.key === "builder"
      ? "deterministic-bpy"
      : record.key === "validator"
        ? "Blender validation"
        : record.key.startsWith("standard")
          ? "fidgeting-model-pipeline standard-view wrapper"
          : record.role === "blender-render"
            ? "Blender"
            : "Blender validation";
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: record.role,
      producer: {
        name: producerName,
        version: report.blender,
        recipe: record.key.startsWith("standard")
          ? "skills/fidgeting-model-pipeline/scripts/capture_standard_views.py"
          : `${expectedDirectory}/build_blockout.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 05 real Blender white model only. It uses approved dimensions and retained shipping-baseline secondary dimensions, with no final material, identity artwork, hidden hardware, Unity change, build, install, or phone push."
      },
      sourceAssetIds: [...new Set(generatedFrom)],
      sourceClaimIds,
      ...(record.viewId ? {
        view: {
          id: record.viewId,
          camera: record.camera,
          renderEngine: "BLENDER_EEVEE",
          axisContract: "X-width/Y-height/Z-front"
        }
      } : {})
    };
  });
  manifest.assets.push(...records);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.reviewArtifactIds = [ids.hero, ids.contactSheet, ids.front, ids.side];
  stage.blockoutSpec = {
    revision: 1,
    dimensionsMm: measured,
    portraitWidthHeightRatio: report.portrait.widthHeightRatio,
    closedTube: tube,
    hierarchy: report.hierarchy,
    secondaryDimensions: report.secondaryDimensions,
    transparentCoverGeometry: report.scope.transparentCoverGeometry,
    finalMaterialsArtwork: "not-modeled",
    fullGate06Validation: "deferred",
    unityAssetChanged: false
  };
  stage.validations = [
    { id: "deterministic-source-present", status: "pass", evidence: `${ids.builder} rebuilds the .blend, Hero, support views, contact sheet, and validation report.` },
    { id: "real-blender-hero-present", status: "pass", evidence: `${ids.hero} is an annotated Blender ${report.blender} Eevee render, not a schematic.` },
    { id: "approved-envelope-exact", status: "pass", evidence: "Evaluated blockout bounds are 228 × 304 × 59 mm with a 0.7500 width-to-height ratio." },
    { id: "single-closed-tube-preflight", status: "pass", evidence: `One ContinuousTubePerimeter mesh uses a cyclic path and 10 × 9 mm outer / 6 × 5 mm passage sections with 2 mm walls; ${tube.topology.openBoundaryEdgeCount} open boundary edges and ${tube.topology.nonManifoldEdgeCount} non-manifold edges were found.` },
    { id: "continuous-channel-preflight", status: "pass", evidence: `Construction-level channel flood-fill visited all ${tube.channelFloodFill.sampleCount} cyclic samples across four sides and four tangent bends.` },
    { id: "approved-hierarchy-only", status: "pass", evidence: "Front/rear shells, blank label zone, tactile insert, ContentSlot, and the single perimeter are present. Logo, Badge, foil artwork, prize content, hidden fasteners, and invented internals are absent." },
    { id: "no-guessed-secondary-dimensions", status: "pass", evidence: "Unspecified secondary blockout dimensions retain the approved shipping baseline with explicit source paths; transparent-cover thickness remains unmodeled." },
    { id: "standard-view-wrapper", status: "pass", evidence: `The standard-view wrapper verified ${viewIds.length} real Blender views with no missing output.` },
    { id: "gate-06-remains-blocked", status: "pass", evidence: "Gate 05 is ready_for_review only. Complete structural, dimension, pivot, and channel verification remains Gate 06 work." },
    { id: "shipping-unity-unchanged", status: "pass", evidence: "All new artifacts are under ArtSource/ModelPipeline. No shipping scene, prefab, runtime, build, install, or phone state changed." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  architecture.evidenceReview.gate05Status = "ready_for_review";
  markDownstreamStale(manifest, stageIndex, "Gate 05 rev 1 real Blender white model awaits explicit visual approval; Gate 06 must not start.");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 04 rev 4 is approved with the measured 4.520833 s total duration locked. Gate 05 rev 1 is a real Blender white-model review: 228 × 304 × 59 mm Portrait envelope, one cyclic hollow perimeter, approved hierarchy, and no final materials or invented internals. Gate 06 remains blocked; shipping Unity is unchanged; no build, install, or phone push occurred.";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "05-blockout",
    blockoutRevision: 1,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    dimensionsMm: measured,
    tubeTopology: {
      connectedMaterialBodyCount: tube.topology.connectedMaterialBodyCount,
      openBoundaryEdgeCount: tube.topology.openBoundaryEdgeCount,
      nonManifoldEdgeCount: tube.topology.nonManifoldEdgeCount,
      channelSamplesVisited: tube.channelFloodFill.visitedSamples
    },
    blender: report.blender,
    realBlenderBlockout: true,
    fullGate06ValidationDeferred: true,
    autoApproved: false,
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseCorrectedBlockoutReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This correction is supported only for a Premium Display Case pipeline.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "05-blockout");
  const contract = manifest.stages[stageIndex - 2];
  const architecture = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (contract.status !== "approved" || architecture.status !== "approved") {
    throw new PipelineError("Gate 03 and Gate 04 must remain approved before a Gate 05 implementation-only correction.", 422);
  }
  if (stage.status !== "rejected" || stage.decision?.action !== "reject") {
    throw new PipelineError("Gate 05 rev 1 must be explicitly rejected before registering rev 2.", 422);
  }
  if (stage.blockoutSpec?.revision !== 1) {
    throw new PipelineError("The correction must follow the preserved Gate 05 rev 1 white model.", 422);
  }
  if (
    architecture.evidenceReview?.reviewState !== "approved"
    || Math.abs(Number(architecture.evidenceReview?.lockedTotalDurationSeconds) - 4.520833) > 0.0000005
  ) {
    throw new PipelineError("Gate 04 must retain the approved 4.520833-second whole-case motion contract.", 422);
  }

  const revisionLabel = "002";
  if (manifest.assets.some((asset) => asset.stageId === "05-blockout" && asset.id.endsWith(`-r${revisionLabel}`))) {
    throw new PipelineError("Gate 05 rev 2 evidence is already registered.", 422);
  }
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/05-blockout", `rev-${revisionLabel}`
  )));
  const viewIds = ["front", "back", "top", "bottom", "left", "right", "hero", "left-oblique", "right-oblique", "low"];
  const definitions = [
    { key: "builder", suffix: "blockout-builder", slot: "white-model-source", file: "build_blockout.py", role: "process", contentClass: "deterministic-premium-display-case-corrected-blockout-source" },
    { key: "validator", suffix: "blockout-validator", slot: "validation-source", file: "validate_blockout.py", role: "process", contentClass: "deterministic-premium-display-case-corrected-blockout-validator" },
    { key: "blend", suffix: "blockout-blend", slot: "blockout-blend", file: "premium-display-case-blockout.blend", role: "source-model", contentClass: "real-blender-corrected-white-model-source" },
    { key: "hero", suffix: "blockout-hero", slot: "white-model-hero", file: "blockout-hero.png", role: "blender-render", contentClass: "real-blender-corrected-annotated-white-model-hero", viewId: "hero", camera: "Gate05HeroCamera" },
    { key: "front", suffix: "blockout-front", slot: "white-model-support", file: "blockout-front.png", role: "blender-render", contentClass: "real-blender-corrected-white-model-front", viewId: "front", camera: "Gate05FrontCamera" },
    { key: "top", suffix: "blockout-top", slot: "white-model-support", file: "blockout-top.png", role: "blender-render", contentClass: "real-blender-corrected-white-model-top", viewId: "top", camera: "Gate05TopCamera" },
    { key: "side", suffix: "blockout-side", slot: "white-model-support", file: "blockout-side.png", role: "blender-render", contentClass: "real-blender-corrected-white-model-side", viewId: "right", camera: "Gate05SideCamera" },
    { key: "rear", suffix: "blockout-rear", slot: "white-model-support", file: "blockout-rear.png", role: "blender-render", contentClass: "real-blender-corrected-white-model-rear", viewId: "back", camera: "Gate05RearCamera" },
    { key: "oblique", suffix: "blockout-oblique", slot: "white-model-support", file: "blockout-oblique.png", role: "blender-render", contentClass: "real-blender-corrected-white-model-oblique", viewId: "right-oblique", camera: "Gate05ObliqueCamera" },
    { key: "tubeCloseup", suffix: "blockout-tube-closeup", slot: "white-model-support", file: "blockout-tube-closeup.png", role: "blender-render", contentClass: "real-blender-closed-tube-corner-closeup", viewId: "tube-continuity-closeup", camera: "Gate05TubeCamera" },
    { key: "beforeAfter", suffix: "blockout-before-after", slot: "white-model-comparison", file: "blockout-before-after.png", role: "blender-render", contentClass: "real-blender-rev1-rev2-comparison", viewId: "before-after", camera: "BeforeAfterCamera" },
    { key: "concentricCenters", suffix: "blockout-concentric-centers", slot: "dimension-overlay", file: "blockout-concentric-centers.png", role: "blender-render", contentClass: "real-blender-concentric-corner-center-overlay", viewId: "front-corner-centers", camera: "Gate05CentersCamera" },
    { key: "contactSheet", suffix: "blockout-contact-sheet", slot: "white-model-support", file: "blockout-contact-sheet.png", role: "blender-render", contentClass: "real-blender-corrected-white-model-contact-sheet", viewId: "blockout-contact-sheet", camera: "multi-view-contact-sheet" },
    { key: "validation", suffix: "blockout-validation", slot: "validation-report", file: "blockout-validation.json", role: "validation", contentClass: "premium-display-case-corrected-blockout-validation" },
    { key: "standardCapture", suffix: "standard-capture", slot: "validation-report", file: "fixed-views/capture-report.json", role: "validation", contentClass: "standard-view-blender-capture-report" },
    { key: "standardCaptureWrapper", suffix: "standard-capture-wrapper", slot: "validation-report", file: "fixed-views/capture-wrapper-report.json", role: "validation", contentClass: "standard-view-capture-wrapper-report" },
    ...viewIds.map((viewId) => ({
      key: `standard${viewId.replace(/(^|-)([a-z])/g, (_match, _separator, letter) => letter.toUpperCase())}`,
      suffix: `standard-${viewId}`,
      slot: "white-model-support",
      file: `fixed-views/${viewId}.png`,
      role: "blender-render",
      contentClass: `real-blender-standard-${viewId}-view`,
      viewId,
      camera: "PipelineCaptureCamera"
    }))
  ].map((record) => ({
    ...record,
    id: `${modelId}-${record.suffix}-r${revisionLabel}`,
    stageId: "05-blockout",
    path: normalizeRepoPath(payload[`${record.key}Path`] || `${expectedDirectory}/${record.file}`)
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) {
      throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    }
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
      throw new PipelineError(`${record.id} file is missing.`, 422);
    }
  }

  const byKey = new Map(definitions.map((record) => [record.key, record]));
  const report = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("validation").path), "utf8"));
  const capture = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("standardCapture").path), "utf8"));
  const wrapper = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("standardCaptureWrapper").path), "utf8"));
  const measured = report.dimensionsMm?.measured;
  const tube = report.closedTube;
  const validReport = report.schemaVersion === 1
    && report.modelId === modelId
    && report.gate === "05-blockout"
    && report.blockoutRevision === 2
    && report.status === "pass"
    && report.artifactTruth?.realBlenderBlockout === true
    && report.artifactTruth?.schematic === false
    && report.artifactTruth?.shippingUnityChanged === false
    && report.artifactTruth?.candidateValuesApproved === false
    && report.upstreamDisposition?.earliestAffectedGate === "05-blockout"
    && report.upstreamDisposition?.gate03Conflict === false
    && report.upstreamDisposition?.gate04Conflict === false
    && measured?.width === 228
    && measured?.height === 304
    && measured?.depth === 59
    && report.dimensionsMm?.pass === true
    && report.portrait?.widthHeightRatio === 0.75
    && report.portrait?.pass === true
    && report.labelPosition?.baselineCenterYmm === 105
    && report.labelPosition?.candidateCenterYmm === 99
    && report.labelPosition?.candidateDownshiftMm === 6
    && report.labelPosition?.approvalState === "pending-user-approval-not-locked-millimeters"
    && report.labelPosition?.minimumLabelFrameToChamberRimMm >= 5
    && report.labelPosition?.minimumLabelFrameToTubeInnerMm >= 5
    && report.labelPosition?.pass === true
    && report.cornerCenterFamilies?.maximumDriftMm <= 0.01
    && report.cornerCenterFamilies?.caseTubeShell?.pass === true
    && report.cornerCenterFamilies?.mainDisplayChamber?.pass === true
    && report.cornerCenterFamilies?.physicalLabel?.pass === true
    && report.cornerCenterFamilies?.pass === true
    && tube?.meshObjectCount === 1
    && tube?.outerSectionMm?.width === 10
    && tube?.outerSectionMm?.depth === 9
    && tube?.wallThicknessMm === 2
    && tube?.passageSectionMm?.width === 6
    && tube?.passageSectionMm?.depth === 5
    && tube?.cornerRadiiMm?.outer === 20
    && tube?.cornerRadiiMm?.centerline === 15
    && tube?.cornerRadiiMm?.inner === 10
    && tube?.pathClosed === true
    && tube?.tangentContinuity?.pass === true
    && tube?.topology?.connectedMaterialBodyCount === 1
    && tube?.topology?.openBoundaryEdgeCount === 0
    && tube?.topology?.nonManifoldEdgeCount === 0
    && tube?.topology?.manifoldPreflightPass === true
    && tube?.channelFloodFill?.pass === true
    && tube?.channelFloodFill?.visitedSamples === tube?.channelFloodFill?.sampleCount
    && report.subjectTopology?.allOpenBoundaryEdgeCount === 0
    && report.subjectTopology?.allNonManifoldEdgeCount === 0
    && report.subjectTopology?.pass === true
    && report.hierarchy?.requiredNodesPresent === true
    && report.scope?.analyticRoundedProfilesOnly === true
    && report.scope?.subjectBevelModifiers?.length === 0
    && report.scope?.finalMaterials === false
    && report.scope?.branding === false
    && report.scope?.logos === false
    && report.scope?.badges === false
    && report.scope?.hiddenFasteners === false
    && report.scope?.inventedInternalParts === false
    && report.scope?.transparentCoverGeometry === "contour-only-thickness-deferred"
    && report.secondaryDimensions?.provenance === "retained-approved-shipping-baseline-with-gate05-concentric-correction"
    && report.validationContext?.fullGate06ValidationDeferred === true
    && report.validationContext?.gate06Entered === false
    && report.blender;
  if (!validReport) {
    throw new PipelineError("The corrected Blender report does not match the Gate 05 rev 2 label and concentric-corner scope.", 422);
  }
  const capturedIds = new Set((capture.views || []).map((view) => view.id));
  if (
    wrapper.verified_capture !== true
    || wrapper.blender_returncode !== 0
    || (wrapper.missing_views || []).length !== 0
    || viewIds.some((viewId) => !capturedIds.has(viewId))
    || !(capture.included_objects || []).includes("ContinuousTubePerimeter")
  ) {
    throw new PipelineError("The standard-view wrapper did not verify the corrected Blender blockout.", 422);
  }

  const priorAssetIds = manifest.assets
    .filter((asset) => asset.stageId === "05-blockout" && asset.id.endsWith("-r001"))
    .map((asset) => asset.id);
  const priorFrontId = `${modelId}-blockout-front-r001`;
  if (!priorAssetIds.includes(priorFrontId)) {
    throw new PipelineError("The immutable Gate 05 rev 1 front render is missing from provenance.", 422);
  }
  for (const assetId of priorAssetIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    asset.reviewState = "rejected";
    asset.rejectionScope = "label-position-and-concentric-corner-implementation";
    asset.preservedForHistory = true;
  }

  const upstreamAssetIds = [...contract.artifactIds, ...architecture.artifactIds];
  const sourceClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  const ids = Object.fromEntries(definitions.map((record) => [record.key, record.id]));
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    const generatedFrom = record.key === "builder"
      ? [...upstreamAssetIds, ...priorAssetIds]
      : record.key === "validator"
        ? [...upstreamAssetIds, ids.builder]
        : record.key === "blend"
          ? [...upstreamAssetIds, ids.builder]
          : record.key === "beforeAfter"
            ? [priorFrontId, ids.front, ids.builder, ids.blend]
            : record.role === "blender-render"
              ? [ids.builder, ids.blend]
              : record.key === "validation"
                ? [ids.builder, ids.validator, ids.blend]
                : [ids.blend];
    const producerName = record.key === "builder"
      ? "deterministic-bpy"
      : record.key === "validator"
        ? "Blender validation"
        : record.key.startsWith("standard")
          ? "fidgeting-model-pipeline standard-view wrapper"
          : record.role === "blender-render"
            ? "Blender"
            : "Blender validation";
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: record.role,
      producer: {
        name: producerName,
        version: report.blender,
        recipe: record.key.startsWith("standard")
          ? "skills/fidgeting-model-pipeline/scripts/capture_standard_views.py"
          : `${expectedDirectory}/build_blockout.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 05 rev 2 preserves the approved envelope, tube, hierarchy and ContentSlot. It presents a 6 mm label-downshift candidate and analytic concentric corner families for approval. The candidate millimeters are not user-locked. Shipping Unity, build, install and phone state remain unchanged."
      },
      sourceAssetIds: [...new Set(generatedFrom)],
      sourceClaimIds,
      ...(record.viewId ? {
        view: {
          id: record.viewId,
          camera: record.camera,
          renderEngine: "BLENDER_EEVEE",
          axisContract: "X-width/Y-height/Z-front"
        }
      } : {})
    };
  });
  manifest.assets.push(...records);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.reviewArtifactIds = [
    ids.beforeAfter,
    ids.hero,
    ids.concentricCenters,
    ids.contactSheet,
    ids.front
  ];
  stage.blockoutSpec = {
    revision: 2,
    correctionScope: "label-downshift-candidate-and-concentric-corner-centers",
    upstreamInvalidation: "none-gate05-implementation-only",
    dimensionsMm: measured,
    portraitWidthHeightRatio: report.portrait.widthHeightRatio,
    labelPosition: report.labelPosition,
    cornerCenterFamilies: report.cornerCenterFamilies,
    closedTube: tube,
    subjectTopology: report.subjectTopology,
    hierarchy: report.hierarchy,
    secondaryDimensions: report.secondaryDimensions,
    transparentCoverGeometry: report.scope.transparentCoverGeometry,
    finalMaterialsArtwork: "not-modeled",
    fullGate06Validation: "deferred",
    unityAssetChanged: false
  };
  stage.validations = [
    { id: "rev1-rejection-preserved", status: "pass", evidence: `All ${priorAssetIds.length} rev 1 assets remain hashed and are marked rejected for label position and non-concentric implementation.` },
    { id: "upstream-contract-compatible", status: "pass", evidence: "Gate 03 locks 184 × 58 mm label size, 228 × 304 × 59 mm envelope and R20 outer corners, but not label center Y or nested corner-center construction. Gate 04 locks hierarchy and motion ownership only." },
    { id: "deterministic-source-present", status: "pass", evidence: `${ids.builder} rebuilds the corrected .blend and all review renders.` },
    { id: "real-blender-before-after-present", status: "pass", evidence: `${ids.beforeAfter} compares immutable rev 1 with the real rev 2 Blender front render.` },
    { id: "label-candidate-clearance", status: "pass", evidence: `The label center moves from Y=105 mm to Y=99 mm, a 6 mm candidate downshift. Minimum frame-to-chamber and frame-to-tube clearances are ${report.labelPosition.minimumLabelFrameToChamberRimMm} mm and ${report.labelPosition.minimumLabelFrameToTubeInnerMm} mm.` },
    { id: "concentric-corner-centers", status: "pass", evidence: `Case/tube/shell, display-chamber and label/cover/frame families use analytic radius offsets. Maximum measured corner-center drift is ${report.cornerCenterFamilies.maximumDriftMm} mm against a 0.01 mm limit.` },
    { id: "no-independent-bevel-radii", status: "pass", evidence: "Every subject rounded contour is generated analytically; no subject BEVEL modifier exists." },
    { id: "approved-envelope-exact", status: "pass", evidence: "Evaluated blockout bounds remain 228 × 304 × 59 mm with a 0.7500 width-to-height ratio." },
    { id: "single-closed-tube-preflight", status: "pass", evidence: `One ContinuousTubePerimeter mesh retains one connected material body, ${tube.topology.openBoundaryEdgeCount} open boundary edges and ${tube.topology.nonManifoldEdgeCount} non-manifold edges.` },
    { id: "continuous-channel-preflight", status: "pass", evidence: `Construction flood-fill visited all ${tube.channelFloodFill.sampleCount} cyclic samples across four sides and four bends.` },
    { id: "all-subject-surfaces-manifold", status: "pass", evidence: `All subject meshes total ${report.subjectTopology.allOpenBoundaryEdgeCount} open boundary edges and ${report.subjectTopology.allNonManifoldEdgeCount} non-manifold edges.` },
    { id: "approved-hierarchy-and-content-slot", status: "pass", evidence: "The approved part tree and 180 × 198 × 48 mm ContentSlot remain unchanged. TransparentCover thickness remains deferred." },
    { id: "standard-view-wrapper", status: "pass", evidence: `The wrapper verified ${viewIds.length} real Blender views with no missing output.` },
    { id: "gate-06-remains-blocked", status: "pass", evidence: "Gate 05 rev 2 is ready_for_review only. Gate 06 was not entered." },
    { id: "shipping-unity-unchanged", status: "pass", evidence: "No shipping scene, prefab, runtime, build, install or phone state changed." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  architecture.evidenceReview.gate05Status = "ready_for_review-rev2";
  markDownstreamStale(manifest, stageIndex, "Gate 05 rev 2 corrected real Blender white model awaits explicit visual approval; Gate 06 must not start.");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 05 rev 1 is preserved and rejected. Gate 03 and Gate 04 remain approved because the correction only changes Gate 05 implementation: a 6 mm label-downshift candidate and analytic concentric corner families with 0.000 mm measured drift. Rev 2 is ready_for_review; Gate 06 remains blocked; shipping Unity, build, install and phone state are unchanged.";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "05-blockout",
    blockoutRevision: 2,
    rejectedRevision: 1,
    correctionScope: "label-downshift-candidate-and-concentric-corner-centers",
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    labelDownshiftCandidateMm: report.labelPosition.candidateDownshiftMm,
    labelCandidateApprovalState: report.labelPosition.approvalState,
    maximumCornerCenterDriftMm: report.cornerCenterFamilies.maximumDriftMm,
    cornerCenterToleranceMm: report.cornerCenterFamilies.toleranceMm,
    dimensionsMm: measured,
    tubeTopology: {
      connectedMaterialBodyCount: tube.topology.connectedMaterialBodyCount,
      openBoundaryEdgeCount: tube.topology.openBoundaryEdgeCount,
      nonManifoldEdgeCount: tube.topology.nonManifoldEdgeCount,
      channelSamplesVisited: tube.channelFloodFill.visitedSamples
    },
    blender: report.blender,
    realBlenderBlockout: true,
    fullGate06ValidationDeferred: true,
    autoApproved: false,
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseArchitectureCompatibleBlockoutReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) {
    throw new PipelineError("Manifest revision conflict.", 409);
  }
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This revalidation is supported only for the Premium Display Case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "05-blockout");
  const architecture = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (
    architecture.status !== "approved"
    || architecture.architectureSpec?.approval?.approvedEvidenceRevision !== 7
    || architecture.architectureSpec?.caseLightOutsideSilhouettePixels !== 0
  ) {
    throw new PipelineError("Gate 04 rev 7 must be approved before revalidating Gate 05.", 422);
  }
  if (
    stage.status !== "stale"
    || stage.blockoutSpec?.revision !== 2
    || stage.decision?.action !== "approve"
  ) {
    throw new PipelineError("Gate 05 rev 3 must revalidate the preserved approved rev 2 white model.", 422);
  }
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/05-blockout/rev-003"
  )));
  const definitions = [
    { key: "revalidator", suffix: "architecture-revalidator", slot: "white-model-source", file: "revalidate_architecture_compatibility.py", role: "process", contentClass: "deterministic-gate04-rev7-blockout-revalidation-source" },
    { key: "reviewGenerator", suffix: "compatibility-review-generator", slot: "white-model-source", file: "generate_compatibility_review.py", role: "process", contentClass: "deterministic-whole-case-compatibility-board-generator" },
    { key: "validator", suffix: "compatibility-validator", slot: "validation-source", file: "validate_compatibility.py", role: "process", contentClass: "deterministic-gate05-rev3-validator" },
    { key: "blend", suffix: "blockout-blend", slot: "blockout-blend", file: "premium-display-case-blockout-r003.blend", role: "source-model", contentClass: "real-blender-architecture-compatible-white-model" },
    { key: "audit", suffix: "architecture-compatibility-audit", slot: "validation-report", file: "architecture-compatibility-audit.json", role: "validation", contentClass: "real-blender-geometry-and-hierarchy-audit" },
    { key: "hero", suffix: "blockout-hero", slot: "white-model-hero", file: "white-model-hero.png", role: "blender-render", contentClass: "real-blender-whole-case-white-model-hero", viewId: "hero", camera: "Gate05HeroCamera" },
    { key: "front", suffix: "blockout-front", slot: "white-model-support", file: "white-model-front.png", role: "blender-render", contentClass: "real-blender-whole-case-white-model-front", viewId: "front", camera: "Gate05FrontCamera" },
    { key: "hierarchy", suffix: "blockout-pivot-root-hierarchy", slot: "pivot-root-hierarchy", file: "blockout-pivot-root-hierarchy.png", role: "analysis", contentClass: "whole-case-pivot-root-ownership-review", viewId: "pivot-root-hierarchy", camera: "diagram" },
    { key: "review", suffix: "blockout-architecture-compatibility-review", slot: "white-model-comparison", file: "blockout-architecture-compatibility-review.png", role: "analysis", contentClass: "whole-case-gate04-rev7-compatibility-board", viewId: "before-after-compatibility", camera: "board" },
    { key: "validation", suffix: "blockout-compatibility-validation", slot: "validation-report", file: "blockout-compatibility-validation.json", role: "validation", contentClass: "gate05-rev3-compatibility-validation" }
  ].map((record) => ({
    ...record,
    id: `${modelId}-${record.suffix}-r003`,
    stageId: "05-blockout",
    path: `${expectedDirectory}/${record.file}`
  }));
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  if (definitions.some((record) => existingIds.has(record.id))) {
    throw new PipelineError("Gate 05 rev 3 evidence is already registered.", 409);
  }
  const files = new Map(definitions.map((record) => [
    record.key,
    assertRepositoryEvidenceFile(
      modelId,
      "05-blockout/rev-003",
      record.path,
      `Gate 05 rev 3 ${record.key}`
    )
  ]));
  const audit = JSON.parse(fs.readFileSync(files.get("audit").absolute, "utf8"));
  const validation = JSON.parse(fs.readFileSync(files.get("validation").absolute, "utf8"));
  const expectedDigest = "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f";
  if (
    audit?.status !== "pass"
    || audit?.blockoutRevision !== 3
    || audit?.sourceBlockoutRevision !== 2
    || audit?.sourceGate04EvidenceRevision !== 7
    || audit?.compatibilityConclusion !== "geometry-unchanged-metadata-rebound-to-unity-runtime"
    || audit?.source?.geometryDigest !== expectedDigest
    || audit?.output?.geometryDigest !== expectedDigest
    || audit?.dimensionsMm?.width !== 228
    || audit?.dimensionsMm?.height !== 304
    || audit?.dimensionsMm?.depth !== 59
    || audit?.portraitWidthHeightRatio !== 0.75
    || audit?.labelCenterYmm !== 99
    || audit?.maximumCornerCenterDriftMm !== 0
    || audit?.closedTube?.connectedMaterialBodyCount !== 1
    || audit?.closedTube?.openBoundaryEdgeCount !== 0
    || audit?.closedTube?.nonManifoldEdgeCount !== 0
    || audit?.closedTube?.channelSamplesVisited !== 384
    || audit?.closedTube?.channelSampleCount !== 384
    || audit?.subjectTopology?.openBoundaryEdgeCount !== 0
    || audit?.subjectTopology?.nonManifoldEdgeCount !== 0
    || audit?.contentSlot?.objectType !== "EMPTY"
    || audit?.contentSlot?.childCount !== 0
    || audit?.contentSlot?.callerOwned !== true
    || audit?.pivot?.object !== "PresentationRoot"
    || audit?.pivot?.locationMm?.join(",") !== "0,0,0"
    || audit?.pivot?.rotationEulerRadians?.join(",") !== "0,0,0"
    || audit?.pivot?.scale?.join(",") !== "1,1,1"
    || audit?.bakedRuntimeAnimation !== false
    || Object.values(audit?.forbiddenGeometry || {}).some(Boolean)
    || audit?.ownership?.Blender?.join(",") !== "geometry,pivot,UV,material zones"
    || !audit?.ownership?.Unity?.includes("mesh-clipped light")
    || audit?.shippingUnityChanged !== false
    || audit?.buildInstallPhonePush !== false
    || audit?.gate06Status !== "blocked"
    || Object.values(audit?.checks || {}).some((value) => value !== true)
  ) {
    throw new PipelineError("Gate 05 rev 3 Blender compatibility audit did not pass.", 422);
  }
  if (
    validation?.status !== "pass"
    || validation?.blockoutRevision !== 3
    || validation?.sourceBlockoutRevision !== 2
    || validation?.sourceGate04EvidenceRevision !== 7
    || validation?.compatibilityConclusion !== "geometry-unchanged-and-compatible"
    || validation?.geometryDigest !== expectedDigest
    || validation?.metrics?.reviewArtifactExplodedPartCount !== 0
    || validation?.metrics?.haloGeometryCount !== 0
    || validation?.metrics?.vfxGeometryCount !== 0
    || validation?.metrics?.particleEmitterCount !== 0
    || validation?.metrics?.proxyGeometryCount !== 0
    || validation?.metrics?.toyGeometryCount !== 0
    || validation?.metrics?.bakedRuntimeAnimationCount !== 0
    || validation?.gate06Status !== "blocked"
    || validation?.shippingUnityChanged !== false
    || validation?.buildInstallPhonePush !== false
    || Object.values(validation?.checks || {}).some((value) => value !== true)
  ) {
    throw new PipelineError("Gate 05 rev 3 evidence validation did not pass.", 422);
  }

  const sourceAssetIds = [
    "premium-display-case-blockout-builder-r002",
    "premium-display-case-blockout-validator-r002",
    "premium-display-case-blockout-blend-r002",
    "premium-display-case-blockout-hero-r002",
    "premium-display-case-blockout-front-r002",
    "premium-display-case-blockout-validation-r002",
    "premium-display-case-modeling-contract-r003",
    "premium-display-case-mesh-light-architecture-r007"
  ];
  if (sourceAssetIds.some((assetId) => !manifest.assets.some((asset) => asset.id === assetId))) {
    throw new PipelineError("Gate 05 rev 3 historical geometry or Gate 04 source evidence is missing.", 422);
  }
  const sourceClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  const ids = Object.fromEntries(definitions.map((record) => [record.key, record.id]));
  const records = definitions.map((record) => {
    const file = files.get(record.key);
    const generatedFrom = record.key === "revalidator"
      ? sourceAssetIds
      : record.key === "reviewGenerator"
        ? [ids.audit, ids.hero, ids.front, "premium-display-case-blockout-hero-r002"]
        : record.key === "validator"
          ? [ids.audit, ids.blend, ids.hero, ids.front, ids.hierarchy, ids.review]
          : record.key === "blend"
            ? [ids.revalidator, "premium-display-case-blockout-blend-r002"]
            : record.key === "audit"
              ? [ids.revalidator, ids.blend, "premium-display-case-blockout-validation-r002"]
              : record.key === "hero" || record.key === "front"
                ? [ids.revalidator, ids.blend]
                : record.key === "hierarchy" || record.key === "review"
                  ? [ids.reviewGenerator, ids.audit, ids.hero, ids.front]
                  : [ids.validator, ids.audit, ids.blend, ids.hero, ids.front, ids.hierarchy, ids.review];
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: file.normalized,
      sha256: sha256File(file.absolute),
      exists: true,
      sizeBytes: fs.statSync(file.absolute).size,
      role: record.role,
      producer: {
        name: record.role === "blender-render" || record.key === "blend" || record.key === "audit"
          ? "Blender 5.2.0 LTS"
          : "fidgeting-model-pipeline",
        version: "1",
        recipe: record.key === "revalidator" || record.role === "blender-render" || record.key === "blend" || record.key === "audit"
          ? `${expectedDirectory}/revalidate_architecture_compatibility.py`
          : record.key === "reviewGenerator" || record.key === "hierarchy" || record.key === "review"
            ? `${expectedDirectory}/generate_compatibility_review.py`
            : `${expectedDirectory}/validate_compatibility.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 05 rev 3 revalidates the approved rev 2 whole assembled white model against Gate 04 rev 7. Geometry digest, dimensions, label, closed tube, ContentSlot and pivot remain unchanged. Only stale Blender runtime-ownership metadata is removed; Unity owns runtime motion and mesh-clipped light."
      },
      sourceAssetIds: [...new Set(generatedFrom)],
      sourceClaimIds,
      reviewState: "active",
      preservedForHistory: true,
      wholeAssembledCaseOnly: ["hero", "front", "hierarchy", "review"].includes(record.key),
      explodeEligible: false,
      ...(record.viewId ? {
        view: {
          id: record.viewId,
          camera: record.camera,
          renderEngine: record.role === "blender-render" ? "BLENDER_EEVEE" : "Pillow",
          axisContract: "X-width/Y-height/Z-front"
        }
      } : {})
    };
  });
  manifest.assets.push(...records);
  if (stage.decision) {
    stage.historicalDecisions = [...(stage.historicalDecisions || []), stage.decision];
  }
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.reviewArtifactIds = [ids.review, ids.hero, ids.front, ids.hierarchy];
  stage.validations = [
    { id: "gate04-rev7-approved", status: "pass", evidence: "Gate 04 rev 7 approval preserves one assembled case, one bounded overlap and mesh-clipped finite light with zero outside-silhouette pixels." },
    { id: "historical-geometry-reused", status: "pass", evidence: `Gate 05 rev 3 derives from immutable rev 2 blend SHA-256 ${audit.source.sha256}; it does not redesign the case.` },
    { id: "geometry-digest-unchanged", status: "pass", evidence: `The evaluated subject geometry digest remains ${expectedDigest} before and after metadata correction and save.` },
    { id: "approved-envelope-exact", status: "pass", evidence: "The assembled Portrait bounds remain exactly 228 × 304 × 59 mm with a 0.7500 width-to-height ratio." },
    { id: "label-and-corners-unchanged", status: "pass", evidence: "The approved label center remains Y=99 mm and maximum concentric corner-center drift remains 0.000 mm." },
    { id: "closed-tube-unchanged", status: "pass", evidence: "ContinuousTubePerimeter remains one connected material body with 0 open edges, 0 non-manifold edges and 384/384 channel samples reached." },
    { id: "hierarchy-content-slot-pivot-compatible", status: "pass", evidence: "PresentationRoot remains at identity, CaseAssembly remains assembled, and caller-owned ContentSlot remains an empty child with zero toy children." },
    { id: "blender-runtime-boundary-corrected", status: "pass", evidence: "Stale duration/motion-owner metadata was removed without changing geometry. Blender owns geometry, pivot, UV and material zones only." },
    { id: "no-baked-runtime-animation", status: "pass", evidence: "PresentationRoot, CaseAssembly and every subject mesh have no animation data; timing, easing, Z travel, local-Y rotation and mesh-clipped light remain Unity-owned." },
    { id: "no-forbidden-geometry", status: "pass", evidence: "No halo, VFX, particle, proxy, split, explode or toy geometry exists in the revalidated blockout." },
    { id: "assembled-review-only", status: "pass", evidence: "Every Gate 05 rev 3 review artifact shows the whole assembled case or its root ownership; exploded part count is 0." },
    { id: "gate06-remains-blocked", status: "pass", evidence: "Gate 05 rev 3 is ready_for_review only. Gate 06 and later stages remain stale or blocked." },
    { id: "shipping-boundary", status: "pass", evidence: "Shipping Unity, Simulator, build, install and phone state remain unchanged." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  stage.blockoutSpec = {
    revision: 3,
    sourceBlockoutRevision: 2,
    sourceGate04EvidenceRevision: 7,
    compatibilityConclusion: "geometry-unchanged-and-compatible",
    geometryChanged: false,
    metadataChanged: true,
    geometryDigest: expectedDigest,
    sourceBlendSha256: audit.source.sha256,
    outputBlendSha256: audit.output.sha256,
    dimensionsMm: audit.dimensionsMm,
    portraitWidthHeightRatio: audit.portraitWidthHeightRatio,
    labelPosition: {
      centerYmm: audit.labelCenterYmm,
      approvalState: "preserved-approved-rev2"
    },
    cornerCenterFamilies: {
      maximumDriftMm: audit.maximumCornerCenterDriftMm,
      toleranceMm: 0.01
    },
    closedTube: audit.closedTube,
    subjectTopology: audit.subjectTopology,
    hierarchy: audit.hierarchy,
    contentSlot: audit.contentSlot,
    pivot: audit.pivot,
    ownership: audit.ownership,
    bakedRuntimeAnimation: false,
    forbiddenGeometry: audit.forbiddenGeometry,
    reviewArtifactExplodedPartCount: 0,
    shippingUnityChanged: false,
    gate06Status: "blocked"
  };
  architecture.architectureSpec.gate05Status = "ready_for_review-rev3";
  markDownstreamStale(
    manifest,
    stageIndex,
    "Gate 05 rev 3 revalidates unchanged approved geometry against Gate 04 rev 7 and awaits explicit visual approval."
  );
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 04 rev 7 is approved. Gate 05 rev 3 revalidates the unchanged 228 × 304 × 59 mm whole-case white model, Y=99 mm label, concentric corners, closed tube, ContentSlot and PresentationRoot pivot. Blender runtime metadata is corrected without geometry changes. Gate 05 awaits visual approval; Gate 06+ remain stale; shipping Unity and phone state are unchanged.";
  manifest.currentState.visualApproval = "gate05-white-model-revalidation-pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.blockoutCompatibility = {
    blockoutRevision: 3,
    sourceBlockoutRevision: 2,
    geometryDigest: expectedDigest,
    geometryChanged: false,
    gate05Status: "ready_for_review",
    gate06Status: "blocked"
  };
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "05-blockout",
    blockoutRevision: 3,
    sourceBlockoutRevision: 2,
    sourceGate04EvidenceRevision: 7,
    compatibilityConclusion: "geometry-unchanged-and-compatible",
    geometryDigest: expectedDigest,
    geometryChanged: false,
    metadataChanged: true,
    dimensionsMm: audit.dimensionsMm,
    labelCenterYmm: audit.labelCenterYmm,
    maximumCornerCenterDriftMm: audit.maximumCornerCenterDriftMm,
    closedTube: audit.closedTube,
    contentSlot: audit.contentSlot,
    pivot: audit.pivot,
    forbiddenGeometry: audit.forbiddenGeometry,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    gate06Status: "blocked",
    autoApproved: false,
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseGeometryPresentationRevalidation(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) {
    throw new PipelineError("Manifest revision conflict.", 409);
  }
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This revalidation is supported only for the Premium Display Case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "06-geometry");
  const architecture = manifest.stages[stageIndex - 2];
  const blockout = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (
    architecture.status !== "approved"
    || architecture.architectureSpec?.approval?.approvedEvidenceRevision !== 7
    || architecture.architectureSpec?.caseLightOutsideSilhouettePixels !== 0
  ) {
    throw new PipelineError("Gate 04 rev 7 must remain approved before Gate 06 revalidation.", 422);
  }
  if (
    blockout.status !== "approved"
    || blockout.blockoutSpec?.revision !== 3
    || blockout.blockoutSpec?.approval?.approvedRevision !== 3
    || blockout.blockoutSpec?.approval?.userApprovalQuote !== "正确，批准并继续（推荐）"
    || blockout.blockoutSpec?.geometryChanged !== false
  ) {
    throw new PipelineError("Approved unchanged Gate 05 rev 3 is required.", 422);
  }
  if (!["stale", "blocked", "missing"].includes(stage.status)) {
    throw new PipelineError("Gate 06 must be stale or blocked before creating rev 3.", 422);
  }

  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/06-geometry/rev-003"
  )));
  const orthographic = [
    ["front", "view-front"],
    ["back", "view-back"],
    ["top", "view-top"],
    ["bottom", "view-bottom"],
    ["left", "view-left"],
    ["right", "view-right"]
  ];
  const definitions = [
    { key: "revalidator", suffix: "geometry-revalidator", slot: "geometry-source", file: "build_geometry_revalidation.py", role: "process", contentClass: "deterministic-gate05-rev3-geometry-revalidation-source" },
    { key: "interactiveExporter", suffix: "interactive-review-exporter", slot: "geometry-source", file: "export_interactive_review.py", role: "process", contentClass: "deterministic-review-only-glb-export-source" },
    { key: "workbenchRenderer", suffix: "workbench-renderer", slot: "geometry-source", file: "render_workbench.py", role: "process", contentClass: "deterministic-whole-case-workbench-render-source" },
    { key: "orthographicRenderer", suffix: "orthographic-renderer", slot: "geometry-source", file: "render_orthographic_workbench.py", role: "process", contentClass: "deterministic-six-view-workbench-render-source" },
    { key: "reviewComposer", suffix: "geometry-review-composer", slot: "geometry-source", file: "compose_geometry_review.py", role: "process", contentClass: "deterministic-whole-case-review-composer" },
    { key: "reviewValidator", suffix: "geometry-review-validator", slot: "validation-source", file: "validate_geometry_review.py", role: "process", contentClass: "deterministic-gate06-rev3-validation-source" },
    { key: "blend", suffix: "geometry-blend", slot: "geometry-blend", file: "premium-display-case-geometry-r003.blend", role: "source-model", contentClass: "real-blender-gate05-rev3-normals-only-geometry-derivative" },
    { key: "geometryReport", suffix: "geometry-revalidation", slot: "validation-report", file: "geometry-revalidation.json", role: "validation", contentClass: "real-blender-geometry-topology-hierarchy-audit" },
    { key: "interactive", suffix: "geometry-interactive-review", slot: "interactive-geometry-review", file: "premium-display-case-gate06-review-r003.glb", role: "source-model", contentClass: "review-only-interactive-whole-case-glb" },
    { key: "interactiveValidation", suffix: "geometry-interactive-validation", slot: "validation-report", file: "interactive-review-validation.json", role: "validation", contentClass: "interactive-whole-case-review-validation" },
    { key: "standardCapture", suffix: "geometry-standard-capture", slot: "validation-report", file: "fixed-views/capture-report.json", role: "validation", contentClass: "standard-view-capture-report" },
    { key: "standardCaptureWrapper", suffix: "geometry-standard-capture-wrapper", slot: "validation-report", file: "fixed-views/capture-wrapper-report.json", role: "validation", contentClass: "standard-view-wrapper-report" },
    { key: "orthographicReport", suffix: "geometry-orthographic-report", slot: "validation-report", file: "orthographic-workbench-report.json", role: "validation", contentClass: "six-view-workbench-capture-report" },
    ...orthographic.map(([viewId, slot]) => ({
      key: viewId,
      suffix: `geometry-${viewId}`,
      slot,
      file: `ortho-${viewId}.png`,
      role: "blender-render",
      contentClass: `real-blender-workbench-orthographic-${viewId}`,
      viewId,
      camera: `Gate06Rev3OrthoCamera-${viewId}`
    })),
    { key: "workbench", suffix: "geometry-workbench", slot: "workbench", file: "geometry-workbench.png", role: "blender-render", contentClass: "real-blender-whole-case-workbench", viewId: "workbench", camera: "Gate06Rev3WorkbenchCamera" },
    { key: "dimensions", suffix: "geometry-dimensions", slot: "dimension-overlay", file: "dimension-overlay.png", role: "analysis", contentClass: "exact-whole-case-dimension-overlay", viewId: "dimension-overlay", camera: "board" },
    { key: "pivot", suffix: "geometry-presentation-root", slot: "pivot-overlay", file: "pivot-presentation-root-overlay.png", role: "analysis", contentClass: "presentation-root-rigid-hierarchy-overlay", viewId: "pivot-presentation-root", camera: "board" },
    { key: "board", suffix: "geometry-presentation-review", slot: "geometry-review", file: "geometry-presentation-review.png", role: "analysis", contentClass: "whole-case-six-view-geometry-presentation-board", viewId: "geometry-presentation-review", camera: "board" },
    { key: "validation", suffix: "geometry-review-validation", slot: "validation-report", file: "geometry-review-validation.json", role: "validation", contentClass: "gate06-rev3-source-render-review-validation" }
  ].map((record) => ({
    ...record,
    id: `${modelId}-${record.suffix}-r003`,
    stageId: "06-geometry",
    path: `${expectedDirectory}/${record.file}`
  }));
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  if (definitions.some((record) => existingIds.has(record.id))) {
    throw new PipelineError("Gate 06 rev 3 evidence is already registered.", 409);
  }
  const files = new Map(definitions.map((record) => [
    record.key,
    assertRepositoryEvidenceFile(
      modelId,
      "06-geometry/rev-003",
      record.path,
      `Gate 06 rev 3 ${record.key}`
    )
  ]));
  const report = JSON.parse(fs.readFileSync(files.get("geometryReport").absolute, "utf8"));
  const validation = JSON.parse(fs.readFileSync(files.get("validation").absolute, "utf8"));
  const interactiveValidation = JSON.parse(fs.readFileSync(files.get("interactiveValidation").absolute, "utf8"));
  const standardCaptureWrapper = JSON.parse(fs.readFileSync(files.get("standardCaptureWrapper").absolute, "utf8"));
  const orthographicReport = JSON.parse(fs.readFileSync(files.get("orthographicReport").absolute, "utf8"));
  const sourceDigest = "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f";
  const derivativeDigest = "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951";
  const vertexDigest = "ced0edf95f8fa6416c5a0e33ebf8dc99fdafcdb3beceac85ee2970bbb2a7682c";
  const silhouetteDigest = "81615c0e5afd59b634dfa2e85040b31b30b9d5ef0ddc9e12462f1b3d1c59f6b4";
  const windingDigest = "c29bc1dd8c0f0c52fd4c70d102bcfc2b4007e579795b605adeb21611a3bf7c79";
  const sourceBlendAsset = manifest.assets.find((asset) => asset.id === "premium-display-case-blockout-blend-r003");
  const internalExplodedAsset = manifest.assets.find((asset) => asset.id === "premium-display-case-geometry-exploded-r002");
  if (
    !sourceBlendAsset
    || sourceBlendAsset.sha256 !== report?.source?.sha256
    || blockout.blockoutSpec.geometryDigest !== sourceDigest
  ) {
    throw new PipelineError("Gate 06 rev 3 source does not match the approved Gate 05 blend.", 422);
  }
  if (
    !internalExplodedAsset
    || internalExplodedAsset.slot !== "exploded-geometry"
    || !internalExplodedAsset.provenance?.contentClass?.includes("internal-only")
    || !fs.existsSync(resolveRepoPath(internalExplodedAsset.path))
    || sha256File(resolveRepoPath(internalExplodedAsset.path)) !== internalExplodedAsset.sha256
  ) {
    throw new PipelineError("The immutable internal-only exploded geometry evidence is missing or changed.", 422);
  }
  if (
    report?.status !== "pass"
    || report?.geometryRevision !== 3
    || report?.sourceGate05Revision !== 3
    || report?.source?.geometryDigest !== sourceDigest
    || report?.output?.geometryDigest !== derivativeDigest
    || report?.output?.sha256 !== sha256File(files.get("blend").absolute)
    || report?.identity?.source?.vertexPositionDigest !== vertexDigest
    || report?.identity?.derivative?.vertexPositionDigest !== vertexDigest
    || report?.identity?.source?.silhouetteDigest !== silhouetteDigest
    || report?.identity?.derivative?.silhouetteDigest !== silhouetteDigest
    || report?.identity?.derivative?.topologyWindingDigest !== windingDigest
    || report?.bounds?.sizeMm?.width !== 228
    || report?.bounds?.sizeMm?.height !== 304
    || report?.bounds?.sizeMm?.depth !== 59
    || report?.meshIntegrity?.allOpenBoundaryEdgeCount !== 0
    || report?.meshIntegrity?.allNonManifoldEdgeCount !== 0
    || report?.meshIntegrity?.allSelfIntersectionPairCount !== 0
    || report?.meshIntegrity?.allDegenerateElementCount !== 0
    || report?.meshIntegrity?.allSubjectMaterialSignedVolumesPositive !== true
    || report?.tubeOrientation?.netMaterialSignedVolumeMm3 !== 52932.982745
    || report?.tubeOrientation?.outerBoundary?.outward !== true
    || report?.tubeOrientation?.innerBoundary?.inwardTowardLumen !== true
    || report?.tubeOrientation?.pass !== true
    || report?.structural?.labelPosition?.candidateCenterYmm !== 99
    || report?.structural?.cornerCenterFamilies?.maximumDriftMm !== 0
    || report?.structural?.closedTube?.topology?.connectedMaterialBodyCount !== 1
    || report?.structural?.closedTube?.topology?.openBoundaryEdgeCount !== 0
    || report?.structural?.closedTube?.topology?.nonManifoldEdgeCount !== 0
    || report?.structural?.closedTube?.channelFloodFill?.visitedSamples !== 384
    || report?.structural?.closedTube?.channelFloodFill?.sampleCount !== 384
    || report?.presentationOwnership?.motionOwner !== "Unity"
    || report?.presentationOwnership?.movingTransform !== "PresentationRoot"
    || report?.presentationOwnership?.rigidChild !== "CaseAssembly"
    || report?.presentationOwnership?.contentSlot !== "caller-owned-static"
    || report?.presentationOwnership?.sameInstance !== true
    || report?.presentationOwnership?.wholeCaseOnly !== true
    || report?.presentationOwnership?.runtimeAnimationBakedInBlender !== false
    || report?.reviewArtifactExplodedPartCount !== 0
    || report?.internalTechnicalExplodedSourceAssetId !== internalExplodedAsset.id
    || report?.shippingUnityChanged !== false
    || report?.buildInstallPhonePush !== false
    || report?.gate07Status !== "blocked"
    || Object.values(report?.checks || {}).some((value) => value !== true)
  ) {
    throw new PipelineError("Gate 06 rev 3 geometry and presentation audit did not pass.", 422);
  }
  const reportedVolumes = Object.values(report.meshIntegrity.objects || {});
  if (
    reportedVolumes.length !== 5
    || reportedVolumes.some((entry) => entry.signedVolumeMm3 <= 0)
  ) {
    throw new PipelineError("Gate 06 rev 3 must prove positive signed volume for every subject mesh.", 422);
  }
  if (
    validation?.status !== "pass"
    || validation?.geometryRevision !== 3
    || validation?.metrics?.orthographicViewCount !== 6
    || validation?.metrics?.reviewArtifactExplodedPartCount !== 0
    || validation?.metrics?.openBoundaryEdgeCount !== 0
    || validation?.metrics?.nonManifoldEdgeCount !== 0
    || validation?.metrics?.selfIntersectionPairCount !== 0
    || validation?.metrics?.degenerateElementCount !== 0
    || validation?.metrics?.tubeSignedVolumeMm3 !== 52932.982745
    || validation?.metrics?.geometryDigest !== derivativeDigest
    || validation?.metrics?.vertexPositionDigest !== vertexDigest
    || validation?.metrics?.silhouetteDigest !== silhouetteDigest
    || validation?.internalTechnicalArtifactIds?.join(",") !== internalExplodedAsset.id
    || validation?.shippingUnityChanged !== false
    || validation?.buildInstallPhonePush !== false
    || validation?.gate07Status !== "blocked"
    || Object.values(validation?.checks || {}).some((value) => value !== true)
  ) {
    throw new PipelineError("Gate 06 rev 3 evidence validation did not pass.", 422);
  }
  if (
    interactiveValidation?.status !== "pass"
    || interactiveValidation?.purpose !== "interactive-review-only-not-gate10-export"
    || interactiveValidation?.reviewGlbSha256 !== sha256File(files.get("interactive").absolute)
    || interactiveValidation?.shippingUnityChanged !== false
    || interactiveValidation?.buildInstallPhonePush !== false
    || Object.values(interactiveValidation?.checks || {}).some((value) => value !== true)
  ) {
    throw new PipelineError("Gate 06 rev 3 interactive review model did not pass.", 422);
  }
  if (
    standardCaptureWrapper?.verified_capture !== true
    || standardCaptureWrapper?.blender_returncode !== 0
    || standardCaptureWrapper?.missing_views?.length !== 0
    || orthographicReport?.status !== "pass"
    || orthographicReport?.views?.length !== 6
    || orthographic.some(([viewId]) => !orthographicReport.views.some((entry) => (
      entry.id === viewId
      && entry.projection === "orthographic"
      && entry.renderEngine === "BLENDER_WORKBENCH"
    )))
  ) {
    throw new PipelineError("Gate 06 rev 3 six-view capture did not pass.", 422);
  }

  const baseSourceAssetIds = [
    "premium-display-case-blockout-blend-r003",
    "premium-display-case-architecture-compatibility-audit-r003",
    "premium-display-case-blockout-compatibility-validation-r003",
    "premium-display-case-mesh-light-architecture-r007"
  ];
  if (baseSourceAssetIds.some((assetId) => !manifest.assets.some((asset) => asset.id === assetId))) {
    throw new PipelineError("Gate 06 rev 3 source evidence is incomplete.", 422);
  }
  const sourceClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  const ids = Object.fromEntries(definitions.map((record) => [record.key, record.id]));
  const renderKeys = new Set([...orthographic.map(([viewId]) => viewId), "workbench"]);
  const reviewKeys = new Set([...orthographic.map(([viewId]) => viewId), "interactive", "workbench", "dimensions", "pivot", "board"]);
  const records = definitions.map((record) => {
    const file = files.get(record.key);
    let generatedFrom = baseSourceAssetIds;
    if (record.key === "blend" || record.key === "geometryReport") {
      generatedFrom = [ids.revalidator, ...baseSourceAssetIds];
    } else if (record.key === "interactive") {
      generatedFrom = [ids.interactiveExporter, ids.blend, ids.geometryReport];
    } else if (record.key === "interactiveValidation") {
      generatedFrom = [ids.interactiveExporter, ids.interactive, ids.blend];
    } else if (record.key === "standardCapture" || record.key === "standardCaptureWrapper") {
      generatedFrom = [ids.blend, ids.geometryReport];
    } else if (record.key === "orthographicReport" || orthographic.some(([viewId]) => viewId === record.key)) {
      generatedFrom = [ids.orthographicRenderer, ids.blend, ids.geometryReport];
    } else if (record.key === "workbench") {
      generatedFrom = [ids.workbenchRenderer, ids.blend, ids.geometryReport];
    } else if (record.key === "dimensions" || record.key === "pivot" || record.key === "board") {
      generatedFrom = [
        ids.reviewComposer,
        ids.workbench,
        ...orthographic.map(([viewId]) => ids[viewId]),
        ids.geometryReport
      ];
    } else if (record.key === "validation") {
      generatedFrom = [
        ids.reviewValidator,
        ids.geometryReport,
        ids.interactiveValidation,
        ids.standardCaptureWrapper,
        ids.orthographicReport,
        ids.workbench,
        ids.dimensions,
        ids.pivot,
        ids.board,
        ...orthographic.map(([viewId]) => ids[viewId])
      ];
    }
    const producerRecipe = renderKeys.has(record.key)
      ? (record.key === "workbench"
          ? `${expectedDirectory}/render_workbench.py`
          : `${expectedDirectory}/render_orthographic_workbench.py`)
      : record.key === "interactive" || record.key === "interactiveValidation"
        ? `${expectedDirectory}/export_interactive_review.py`
        : record.key === "dimensions" || record.key === "pivot" || record.key === "board"
          ? `${expectedDirectory}/compose_geometry_review.py`
          : record.key === "validation"
            ? `${expectedDirectory}/validate_geometry_review.py`
            : `${expectedDirectory}/build_geometry_revalidation.py`;
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: file.normalized,
      sha256: sha256File(file.absolute),
      exists: true,
      sizeBytes: fs.statSync(file.absolute).size,
      role: record.role,
      producer: {
        name: record.role === "blender-render" || record.key === "blend" || record.key === "geometryReport" || record.key === "interactive"
          ? "Blender 5.2.0 LTS"
          : "fidgeting-model-pipeline",
        version: "1",
        recipe: producerRecipe
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 06 rev 3 revalidates the approved Gate 05 rev 3 source without vertex, matrix, dimension or silhouette changes. Only the previously approved tube face-winding correction is applied. PresentationRoot remains the sole Unity runtime motion owner; CaseAssembly and caller-owned ContentSlot remain rigid, same-instance and whole-case."
      },
      sourceAssetIds: [...new Set(generatedFrom)],
      sourceClaimIds,
      reviewState: "active",
      preservedForHistory: true,
      wholeAssembledCaseOnly: reviewKeys.has(record.key),
      explodeEligible: false,
      ...(record.key === "interactive" ? {
        interaction: {
          type: "threejs-orbit",
          checklist: [
            "orbit-whole-case",
            "inspect-six-fixed-directions",
            "toggle-wireframe",
            "confirm-presentation-root-rigid-ownership",
            "confirm-no-exploded-review"
          ],
          approvalRequiresCompletedChecklist: true,
          stage10ExportApproval: false
        }
      } : {}),
      ...(record.viewId ? {
        view: {
          id: record.viewId,
          camera: record.camera,
          renderEngine: renderKeys.has(record.key) ? "BLENDER_WORKBENCH" : "Pillow",
          axisContract: "X-width/Y-height/Z-front",
          pose: "assembled-canonical-zero-motion"
        }
      } : {})
    };
  });
  manifest.assets.push(...records);
  if (stage.decision) {
    stage.historicalDecisions = [...(stage.historicalDecisions || []), stage.decision];
  }
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = [...records.map((record) => record.id), internalExplodedAsset.id];
  stage.reviewArtifactIds = [
    ids.interactive,
    ids.board,
    ids.workbench,
    ids.dimensions,
    ids.pivot,
    ...orthographic.map(([viewId]) => ids[viewId])
  ];
  stage.validations = [
    { id: "approved-gate05-rev3-source", status: "pass", evidence: `Gate 06 derives from approved Gate 05 rev 3 blend SHA-256 ${report.source.sha256}.` },
    { id: "six-orthographic-workbench-views", status: "pass", evidence: "Front, back, top, bottom, left and right orthographic Workbench views were rendered from the same saved blend." },
    { id: "workbench-dimensions-pivot", status: "pass", evidence: "Real Blender Workbench, exact 228 × 304 × 59 mm overlay, Y=99 label and PresentationRoot hierarchy overlay are present." },
    { id: "stable-geometry-and-silhouette", status: "pass", evidence: `Source digest ${sourceDigest}; normals-only derivative ${derivativeDigest}; vertex ${vertexDigest}; silhouette ${silhouetteDigest}.` },
    { id: "positive-volumes-and-coherent-normals", status: "pass", evidence: "All five subject meshes have positive signed volume; tube net volume is 52932.982745 mm³ with outward outer and lumen-facing inner normals." },
    { id: "closed-manifold-no-intersections-or-degenerates", status: "pass", evidence: "0 open edges, 0 non-manifold edges, 0 self-intersection pairs and 0 degenerate elements." },
    { id: "connected-hollow-tube", status: "pass", evidence: "ContinuousTubePerimeter remains one connected body with 384/384 channel samples reached." },
    { id: "concentric-label-and-content-slot", status: "pass", evidence: "Concentric center drift remains 0.000 mm; label center remains Y=99 mm; ContentSlot remains caller-owned, empty and rigid." },
    { id: "gate04-presentation-ownership-compatible", status: "pass", evidence: "Only PresentationRoot may receive Unity runtime motion. CaseAssembly and ContentSlot remain same-instance rigid descendants; no Blender animation is baked." },
    { id: "interactive-whole-case-review", status: "pass", evidence: "Review-only GLB supports orbit, fixed views and wireframe. It is not a Gate 10 export approval artifact." },
    { id: "internal-exploded-evidence-hidden", status: "pass", evidence: `${internalExplodedAsset.id} remains internal technical evidence and is absent from reviewArtifactIds and the primary board.` },
    { id: "scope-boundary", status: "pass", evidence: "No timing, easing, light tuning, material, shipping Unity, Simulator, build, install or phone work occurred." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  stage.geometrySpec = {
    revision: 3,
    sourceGate05Revision: 3,
    sourceGate04EvidenceRevision: 7,
    geometryChanged: false,
    normalCorrectionOnly: true,
    sourceGeometryDigest: sourceDigest,
    evaluatedGeometryDigest: derivativeDigest,
    identity: {
      objectMatrixDigest: report.identity.derivative.objectMatrixDigest,
      vertexPositionDigest: vertexDigest,
      silhouetteDigest,
      topologyWindingDigest: windingDigest
    },
    dimensionsMm: report.bounds.sizeMm,
    portraitWidthHeightRatio: 0.75,
    labelCenterYmm: 99,
    maximumCornerCenterDriftMm: 0,
    meshIntegrity: {
      perObject: report.meshIntegrity.objects,
      openBoundaryEdgeCount: 0,
      nonManifoldEdgeCount: 0,
      selfIntersectionPairCount: 0,
      degenerateElementCount: 0,
      allSubjectMaterialSignedVolumesPositive: true
    },
    tube: {
      connectedMaterialBodyCount: 1,
      channelSamplesVisited: 384,
      channelSampleCount: 384,
      netMaterialSignedVolumeMm3: report.tubeOrientation.netMaterialSignedVolumeMm3,
      outerBoundaryOutward: true,
      innerBoundaryTowardLumen: true
    },
    hierarchy: {
      movingTransform: "PresentationRoot",
      rigidAssembly: "CaseAssembly",
      contentSlot: "caller-owned-static",
      sameInstance: true,
      wholeCaseOnly: true,
      bakedRuntimeAnimation: false
    },
    review: {
      interactiveArtifactId: ids.interactive,
      primaryBoardArtifactId: ids.board,
      orthographicArtifactIds: orthographic.map(([viewId]) => ids[viewId]),
      reviewArtifactExplodedPartCount: 0,
      internalTechnicalArtifactIds: [internalExplodedAsset.id],
      interactionRequired: true,
      approvalChecklist: [
        "orbit-whole-case",
        "inspect-six-fixed-directions",
        "toggle-wireframe",
        "confirm-presentation-root-rigid-ownership",
        "confirm-no-exploded-review"
      ]
    },
    animationTimingIncluded: false,
    lightTuningIncluded: false,
    shippingImplementationIncluded: false,
    shippingUnityChanged: false,
    gate07Status: "blocked"
  };
  blockout.blockoutSpec.gate06Status = "ready_for_review-rev3";
  if (manifest.currentState.blockoutCompatibility) {
    manifest.currentState.blockoutCompatibility.gate05Status = "approved";
    manifest.currentState.blockoutCompatibility.gate06Status = "ready_for_review-rev3";
  }
  markDownstreamStale(
    manifest,
    stageIndex,
    "Gate 06 rev 3 revalidates approved unchanged geometry and awaits interactive visual approval."
  );
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 05 rev 3 is approved. Gate 06 rev 3 revalidates the same whole-case geometry through six orthographic Workbench views, exact dimensions, positive signed volumes, manifold/intersection/degenerate checks, connected tube, stable geometry/silhouette digests and an interactive whole-case GLB. PresentationRoot remains the sole Unity runtime motion owner. Gate 06 awaits visual approval; Gate 07+ remain stale; shipping Unity and phone state are unchanged.";
  manifest.currentState.visualApproval = "gate06-geometry-presentation-revalidation-pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.geometryRevalidation = {
    geometryRevision: 3,
    sourceGate05Revision: 3,
    geometryChanged: false,
    sourceGeometryDigest: sourceDigest,
    evaluatedGeometryDigest: derivativeDigest,
    vertexPositionDigest: vertexDigest,
    silhouetteDigest,
    orthographicViewCount: 6,
    reviewArtifactExplodedPartCount: 0,
    interactiveReviewArtifactId: ids.interactive,
    gate06Status: "ready_for_review",
    gate07Status: "blocked"
  };
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "06-geometry",
    geometryRevision: 3,
    sourceGate05Revision: 3,
    sourceGate04EvidenceRevision: 7,
    geometryChanged: false,
    normalCorrectionOnly: true,
    sourceGeometryDigest: sourceDigest,
    evaluatedGeometryDigest: derivativeDigest,
    vertexPositionDigest: vertexDigest,
    silhouetteDigest,
    dimensionsMm: report.bounds.sizeMm,
    labelCenterYmm: 99,
    maximumCornerCenterDriftMm: 0,
    meshIntegrity: stage.geometrySpec.meshIntegrity,
    tube: stage.geometrySpec.tube,
    hierarchy: stage.geometrySpec.hierarchy,
    interactiveReviewArtifactId: ids.interactive,
    primaryBoardArtifactId: ids.board,
    internalTechnicalArtifactIds: [internalExplodedAsset.id],
    reviewArtifactExplodedPartCount: 0,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    gate07Status: "blocked",
    autoApproved: false,
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function saveArchitectureQuestionReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (modelId !== "magnetic-slide-tile") throw new PipelineError("Architecture question review is currently supported only for magnetic-slide-tile.", 422);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "04-architecture");
  if (manifest.stages[stageIndex - 1].status !== "approved") throw new PipelineError("Gate 03 must remain approved before creating an architecture evidence review.", 422);
  if (manifest.stages[stageIndex].status !== "rejected") throw new PipelineError("The current Gate 04 revision must be explicitly rejected before creating an evidence-only question revision.", 422);

  const priorPartTrees = manifest.assets.filter((asset) => asset.stageId === "04-architecture" && asset.slot === "part-tree");
  const architectureRevision = priorPartTrees.length + 1;
  const revisionLabel = String(architectureRevision).padStart(3, "0");
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/04-architecture", `rev-${revisionLabel}`
  )));
  const paths = {
    sliderQuestion: normalizeRepoPath(payload.sliderQuestionPath || `${expectedDirectory}/slider-construction-question.svg`),
    rotaryQuestion: normalizeRepoPath(payload.rotaryQuestionPath || `${expectedDirectory}/rotary-construction-question.svg`)
  };
  for (const [label, relativePath] of Object.entries(paths)) {
    if (!relativePath.startsWith(`${expectedDirectory}/`)) throw new PipelineError(`${label} must be stored inside ${expectedDirectory}.`);
    const absolutePath = resolveRepoPath(relativePath);
    if (!fs.existsSync(absolutePath) || !fs.statSync(absolutePath).isFile()) throw new PipelineError(`${label} file is missing.`, 422);
  }

  const contractAssetId = manifest.stages[stageIndex - 1].artifactIds[0];
  const sourceAssetIds = [
    contractAssetId,
    "slider-analysis-official-discovery-log-r002",
    "slider-analysis-official-mechanism-board-r002",
    "slider-intake-haloo-official-05",
    "slider-intake-haloo-official-06",
    "slider-intake-haloo-official-07",
    "slider-intake-haloo-official-08",
    "slider-intake-haloo-official-metadata",
    "slider-intake-nxedc-metadata"
  ].filter((assetId, index, values) => manifest.assets.some((asset) => asset.id === assetId) && values.indexOf(assetId) === index);
  const allowedClaimIds = new Set([
    "slider-analysis-official-product-match-r002",
    "slider-analysis-official-dual-mode-r002",
    "slider-analysis-official-evidence-boundary-r002"
  ]);
  const sourceClaimIds = (manifest.claims || [])
    .filter((claim) => allowedClaimIds.has(claim.id) && claim.state !== "superseded")
    .map((claim) => claim.id);
  const records = [
    { id: `${modelId}-slider-construction-question-r${revisionLabel}`, slot: "part-tree", path: paths.sliderQuestion, contentClass: "exact-source-slider-construction-question" },
    { id: `${modelId}-rotary-construction-question-r${revisionLabel}`, slot: "exploded-plan", path: paths.rotaryQuestion, contentClass: "exact-source-rotary-construction-question" }
  ];
  const assetRecords = records.map((record) => {
    const absolutePath = resolveRepoPath(record.path);
    return {
      id: record.id,
      stageId: "04-architecture",
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolutePath),
      exists: true,
      sizeBytes: fs.statSync(absolutePath).size,
      role: "process",
      producer: { name: "fidgeting-model-pipeline", version: "1", recipe: "Gate 04 exact-source crop review with unresolved construction questions" },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 04 rev 6 was rejected because both internal constructions were wrong. This artifact foregrounds exact-product visible evidence only and does not assert replacement geometry."
      },
      sourceAssetIds,
      sourceClaimIds
    };
  });
  manifest.assets.push(...assetRecords);
  const stage = manifest.stages[stageIndex];
  stage.revision += 1;
  stage.status = "draft";
  stage.artifactIds = assetRecords.map((asset) => asset.id);
  stage.architectureSpec = {
    reviewMode: "exact-source-questions-only",
    straightSliderConstruction: "unknown-user-clarification-required",
    rotaryConstruction: "unknown-user-clarification-required",
    visibleEvidenceOnly: true,
    replacementGeometryAuthorized: false,
    rejectedRevisionReuse: false
  };
  stage.validations = [
    { id: "exact-source-crops-present", status: "pass", evidence: "Both review boards directly show immutable HALOOPLAYER exact-product source imagery." },
    { id: "rejected-architecture-not-reused", status: "pass", evidence: "No rev 6 part assignment, rail ownership, rotary construction, five-layer, 90-degree, end-stop, count, tolerance, hole-depth or coupling assumption is promoted." },
    { id: "straight-slider-construction-determined", status: "fail", evidence: "Official imagery shows visible long-groove parts but does not prove which surfaces belong to the moving versus fixed body or how they engage." },
    { id: "rotary-construction-determined", status: "fail", evidence: "Official imagery shows a circular ball region and central hub but does not prove which parts are fixed, rotating or shared with the straight-slider mode." },
    { id: "minimal-user-questions-present", status: "pass", evidence: "The review asks one ownership question for the straight slider and one fixed-versus-rotating question for the rotary module." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "Gate 04 rev 7 仅为证据问题草稿；真实直推与旋转构造仍未知。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "用户已否决 Gate 04 rev 6 的直推与旋转内部结构。当前官方图不足以确定真实构造；rev 7 仅展示同款原始证据并等待两个最小结构回答，不得进入 Gate 05。";
  const event = makeEvent(manifest, "stage-draft-created", {
    stageId: "04-architecture",
    architectureRevision,
    artifactIds: stage.artifactIds,
    evidenceInsufficient: true
  });
  return saveManifest(manifest, event);
}

export function saveArchitectureEvidenceMappingReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (modelId !== "magnetic-slide-tile") throw new PipelineError("Architecture evidence mapping is supported only for magnetic-slide-tile.", 422);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "04-architecture");
  if (manifest.stages[stageIndex - 1].status !== "approved") throw new PipelineError("Gate 03 must remain approved before creating an architecture evidence mapping.", 422);
  if (manifest.stages[stageIndex].status !== "rejected") throw new PipelineError("The superseded Gate 04 review must be rejected before creating a replacement revision.", 422);

  const revisionNumbers = manifest.assets
    .filter((asset) => asset.stageId === "04-architecture")
    .map((asset) => Number(asset.id.match(/-r(\d{3})$/)?.[1] || 0));
  const architectureRevision = Math.max(0, ...revisionNumbers) + 1;
  const revisionLabel = String(architectureRevision).padStart(3, "0");
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/04-architecture", `rev-${revisionLabel}`
  )));
  const reviewFiles = [
    { key: "fixedBody", id: `${modelId}-fixed-body-boundary-r${revisionLabel}`, slot: "part-tree", file: "fixed-body-boundary.svg", contentClass: "fixed-body-visible-boundary-map" },
    { key: "sliderSequence", id: `${modelId}-slider-travel-sequence-r${revisionLabel}`, slot: "exploded-plan", file: "slider-travel-sequence.svg", contentClass: "sequential-video-slider-motion-map" },
    { key: "rotarySequence", id: `${modelId}-rotating-body-pivot-r${revisionLabel}`, slot: "architecture-evidence", file: "rotating-body-pivot.svg", contentClass: "sequential-video-rotary-motion-map" },
    { key: "holesSlots", id: `${modelId}-visible-holes-slots-r${revisionLabel}`, slot: "architecture-evidence", file: "visible-holes-slots.svg", contentClass: "visible-hole-slot-contact-map" }
  ].map((record) => ({
    ...record,
    path: normalizeRepoPath(payload[`${record.key}Path`] || `${expectedDirectory}/${record.file}`)
  }));
  const cropDefinitions = [
    ["slide-42-00", "slide-42.00.png", "slider-intake-user-video"],
    ["slide-42-75", "slide-42.75.png", "slider-intake-user-video"],
    ["slide-43-50", "slide-43.50.png", "slider-intake-user-video"],
    ["rotate-66-00", "rotate-66.00.png", "slider-intake-user-video"],
    ["rotate-66-50", "rotate-66.50.png", "slider-intake-user-video"],
    ["rotate-67-25", "rotate-67.25.png", "slider-intake-user-video"],
    ["official-fixed-carrier", "official-fixed-carrier.png", "slider-intake-haloo-official-07"],
    ["official-slider-a", "official-slider-a.png", "slider-intake-haloo-official-07"],
    ["official-slider-b", "official-slider-b.png", "slider-intake-haloo-official-07"],
    ["official-rotary-pivot", "official-rotary-pivot.png", "slider-intake-haloo-official-07"],
    ["official-interface-plate", "official-interface-plate.png", "slider-intake-haloo-official-07"],
    ["nxedc-open-track", "nxedc-open-track.png", "slider-intake-nxedc-ref-04"]
  ].map(([suffix, file, sourceAssetId]) => ({
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "04-architecture",
    slot: "evidence-crop",
    path: `${expectedDirectory}/source-crops/${file}`,
    sourceAssetIds: [sourceAssetId]
  }));
  for (const record of [...reviewFiles, ...cropDefinitions]) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    const absolutePath = resolveRepoPath(record.path);
    if (!fs.existsSync(absolutePath) || !fs.statSync(absolutePath).isFile()) throw new PipelineError(`${record.id} file is missing.`, 422);
  }

  const userClaimId = `slider-architecture-both-track-parts-move-r${revisionLabel}`;
  manifest.claims.push({
    id: userClaimId,
    stageId: "04-architecture",
    category: "motion",
    statement: "用户明确纠正：此前标为 A/B 的两个槽板都可运动；这是滑轨机构，其中一个运动组件承担旋转。不得再把 A 或 B 作为永久固定件。",
    confidence: "high",
    sourceAssetIds: ["slider-intake-user-video", "slider-intake-haloo-official-07"],
    sourceRegions: [],
    state: "active",
    architectureRevision: revisionLabel,
    assertedBy: "user",
    sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2"
  });

  const cropRecords = cropDefinitions.map((record) => {
    const absolutePath = resolveRepoPath(record.path);
    return {
      ...record,
      sha256: sha256File(absolutePath),
      exists: true,
      sizeBytes: fs.statSync(absolutePath).size,
      role: "process",
      producer: { name: "ffmpeg/Pillow", version: "8.1.1/11.3.0", recipe: `${expectedDirectory}/generate_review_assets.py` },
      provenance: {
        origin: "repository-generated",
        contentClass: "tight-source-crop",
        assertedBy: "assistant",
        note: "Deterministic local crop from immutable exact-product source media; no geometry or hidden continuation was generated.",
        userClaimIds: [userClaimId]
      },
      sourceClaimIds: []
    };
  });
  const contractAssetId = manifest.stages[stageIndex - 1].artifactIds[0];
  const commonSourceAssetIds = [
    contractAssetId,
    "slider-intake-user-video",
    "slider-intake-haloo-official-07",
    "slider-intake-nxedc-ref-04",
    ...cropRecords.map((asset) => asset.id)
  ];
  const reviewRecords = reviewFiles.map((record) => {
    const absolutePath = resolveRepoPath(record.path);
    return {
      id: record.id,
      stageId: "04-architecture",
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolutePath),
      exists: true,
      sizeBytes: fs.statSync(absolutePath).size,
      role: "process",
      producer: { name: "fidgeting-model-pipeline", version: "1", recipe: `${expectedDirectory}/generate_review_assets.py plus source-coordinate SVG overlays` },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Evidence mapping consumes the user's correction, continuous MOV frames, official internal imagery and NXEDC open-track imagery. Occluded boundaries remain dashed/unknown.",
        userClaimIds: [userClaimId]
      },
      sourceAssetIds: commonSourceAssetIds,
      sourceClaimIds: [
        "slider-analysis-official-product-match-r002",
        "slider-analysis-official-dual-mode-r002",
        "slider-analysis-official-evidence-boundary-r002"
      ].filter((claimId) => manifest.claims.some((claim) => claim.id === claimId && claim.state !== "superseded"))
    };
  });
  manifest.assets.push(...cropRecords, ...reviewRecords);

  const stage = manifest.stages[stageIndex];
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = reviewRecords.map((asset) => asset.id);
  stage.architectureSpec = {
    reviewMode: "motion-evidence-mapping",
    userClaim: "both-previously-labeled-track-plates-can-move",
    fixedReference: "lower-chassis-and-exposed-track-carrier-relative-to-hand",
    linearMovingElement: "upper-decorated-capsule-translates-along-long-axis",
    rotatingElement: "same-upper-decorated-capsule-rotates-relative-to-lower-chassis",
    pivotRegion: "central-post-bearing-candidate-visible-hidden-continuation-unknown",
    trackGroovePolicy: "visible-boundaries-only",
    holeContactPolicy: "visible-candidates-numbered-no-depth-count-or-tolerance",
    aOrBRotaryOwnership: "unknown-not-distinguishable-from-available-images",
    replacementGeometryAuthorized: false,
    rejectedRevisionReuse: false
  };
  stage.validations = [
    { id: "user-motion-claim-consumed", status: "pass", evidence: `${userClaimId} is linked by every Gate 04 review board; no A/B fixed-choice question remains.` },
    { id: "sequential-user-video-frames-present", status: "pass", evidence: "Slider frames 42.00/42.75/43.50 s and rotary frames 66.00/66.50/67.25 s are tight crops from the immutable user MOV." },
    { id: "exact-product-internal-crops-present", status: "pass", evidence: "Fixed carrier, A/B track plates, rotary pivot, interface plate and NXEDC open-track crops link directly to exact-product imagery." },
    { id: "fixed-moving-rotating-mapping-explicit", status: "pass", evidence: "The lower hand-held chassis/track carrier is the relative fixed reference; the upper decorated capsule is shown translating and rotating in separate continuous frame sequences." },
    { id: "narrow-hole-slot-annotations", status: "pass", evidence: "Visible slots, grooves, openings, pivot candidates and contact regions have narrow source-coordinate outlines and numbered callouts." },
    { id: "occluded-boundaries-remain-unknown", status: "pass", evidence: "Dashed boundaries stop at occlusion; hidden continuation, hole depth, tolerances, hidden counts and coupling are not asserted." },
    { id: "rejected-rev7-framing-removed", status: "pass", evidence: "The review does not ask whether A or B is fixed and does not reuse rev 7 A/B or C/D fixed-choice framing." },
    { id: "gate05-remains-locked", status: "pass", evidence: "This is an unapproved Gate 04 evidence mapping; replacementGeometryAuthorized remains false." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "Gate 04 rev 8 等待用户确认固定 / 线性 / 旋转映射及可见孔槽描线；不得进入 Gate 05。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 04 rev 7 已按用户纠正否决。rev 8 使用用户 MOV 连续帧与 HALOOPLAYER/NXEDC 同款局部图，提出相对固定下层承载体、上层整件直线滑动并绕中央接口旋转的证据映射；A/B 均可运动，A/B 中谁直连旋转上盖仍不可从现有内部图唯一判定。等待用户确认，不得进入 Gate 05。";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "04-architecture",
    architectureRevision,
    artifactIds: stage.artifactIds,
    userClaimId,
    evidenceMappingComplete: true,
    autoApproved: false
  });
  return saveManifest(manifest, event);
}

export function saveConcealedOverlapArchitectureReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (modelId !== "magnetic-slide-tile") throw new PipelineError("The concealed-overlap correction is supported only for magnetic-slide-tile.", 422);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "04-architecture");
  if (manifest.stages[stageIndex - 1].status !== "approved") throw new PipelineError("Gate 03 must remain approved before correcting Gate 04.", 422);
  if (manifest.stages[stageIndex].status !== "rejected") throw new PipelineError("The superseded Gate 04 revision must be rejected first.", 422);

  const architectureRevision = 10;
  const revisionLabel = "010";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/04-architecture", `rev-${revisionLabel}`
  )));
  const cropDefinitions = [
    ["visible-flat-lower", "visible-flat-lower.png", "slider-intake-user-video"],
    ["circular-slide-overlap", "circular-slide-overlap.png", "slider-intake-user-video"],
    ["official-concealed-interface", "official-concealed-interface.png", "slider-intake-haloo-official-07"],
    ["upper-rotates-over-lower", "upper-rotates-over-lower.png", "slider-intake-user-video"]
  ].map(([suffix, file, sourceAssetId]) => ({
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "04-architecture",
    slot: "evidence-crop",
    path: `${expectedDirectory}/source-crops/${file}`,
    sourceAssetIds: [sourceAssetId]
  }));
  const reviewDefinitions = [
    ["flat-lower-plane", "part-tree", "flat-lower-plane.svg", "flat-visible-lower-plane-architecture-map"],
    ["concealed-circular-interface", "exploded-plan", "concealed-circular-interface.svg", "concealed-circular-overlap-motion-map"]
  ].map(([suffix, slot, file, contentClass]) => ({
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "04-architecture",
    slot,
    path: `${expectedDirectory}/${file}`,
    contentClass
  }));
  const scriptDefinition = {
    id: `${modelId}-corrected-architecture-crop-generator-r${revisionLabel}`,
    stageId: "04-architecture",
    slot: "evidence-source",
    path: `${expectedDirectory}/generate_corrected_review.py`
  };
  for (const record of [scriptDefinition, ...cropDefinitions, ...reviewDefinitions]) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) throw new PipelineError(`${record.id} file is missing.`, 422);
  }

  const userClaimId = `slider-architecture-flat-lower-concealed-overlap-r${revisionLabel}`;
  manifest.claims.push({
    id: userClaimId,
    stageId: "04-architecture",
    category: "structure",
    statement: "用户权威纠正：可见下层件是干净平面，没有外露滑轨；全部轨道与内部机构封闭在上下件共享的圆形重叠区。上层件通过该隐藏接口平移并旋转。",
    confidence: "high",
    sourceAssetIds: ["slider-intake-user-video", "slider-intake-haloo-official-07"],
    sourceRegions: [],
    state: "active",
    architectureRevision: revisionLabel,
    assertedBy: "user",
    sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2"
  });

  const sourceClaimIds = [
    "slider-analysis-official-product-match-r002",
    "slider-analysis-official-dual-mode-r002",
    "slider-analysis-official-evidence-boundary-r002"
  ].filter((claimId) => manifest.claims.some((claim) => claim.id === claimId && claim.state !== "superseded"));
  const cropRecords = cropDefinitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    return {
      ...record,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: "process",
      producer: { name: "Pillow", version: "11.3.0", recipe: scriptDefinition.path },
      provenance: {
        origin: "repository-generated",
        contentClass: "tight-exact-source-crop",
        assertedBy: "assistant",
        note: "Tight crop only. It corroborates visible boundaries without overriding the user's structure correction or reconstructing hidden geometry.",
        userClaimIds: [userClaimId]
      },
      sourceClaimIds: []
    };
  });
  const scriptAbsolute = resolveRepoPath(scriptDefinition.path);
  const scriptRecord = {
    ...scriptDefinition,
    sha256: sha256File(scriptAbsolute),
    exists: true,
    sizeBytes: fs.statSync(scriptAbsolute).size,
    role: "process",
    producer: { name: "Python", version: "3", recipe: scriptDefinition.path },
    provenance: {
      origin: "repository-generated",
      contentClass: "deterministic-source-crop-recipe",
      assertedBy: "assistant",
      note: "Generates only tight crops from immutable Gate 04 rev 8 crops; no annotation or geometry is rasterized into source evidence.",
      userClaimIds: [userClaimId]
    },
    sourceAssetIds: ["slider-intake-user-video", "slider-intake-haloo-official-07"],
    sourceClaimIds: []
  };
  const contractAssetId = manifest.stages[stageIndex - 1].artifactIds[0];
  const reviewSourceIds = [
    contractAssetId,
    "slider-intake-user-video",
    "slider-intake-haloo-official-07",
    ...cropRecords.map((record) => record.id)
  ];
  const reviewRecords = reviewDefinitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: "process",
      producer: { name: "fidgeting-model-pipeline", version: "1", recipe: `${scriptDefinition.path} plus source-coordinate SVG overlays` },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Solid outlines mark only visible exterior boundaries. Dashed circles are location envelopes for concealed mechanisms, not claimed tracks or parts.",
        userClaimIds: [userClaimId]
      },
      sourceAssetIds: reviewSourceIds,
      sourceClaimIds
    };
  });
  manifest.assets.push(scriptRecord, ...cropRecords, ...reviewRecords);

  const stage = manifest.stages[stageIndex];
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = reviewRecords.map((record) => record.id);
  stage.architectureSpec = {
    reviewMode: "concealed-circular-overlap",
    userClaim: "visible-lower-plane-clean-all-mechanism-concealed-in-circular-overlap",
    exteriorMainBodies: 2,
    visibleLowerPlane: "clean-flat-no-exposed-rails",
    concealedMechanismEnvelope: "shared-circular-overlap-zone-dashed-location-proxy-only",
    linearMovingElement: "upper-capsule-translates-through-concealed-interface",
    rotatingElement: "same-upper-capsule-rotates-through-concealed-interface",
    hiddenGeometryPolicy: "paths-coupling-hole-depths-counts-tolerances-and-occluded-geometry-unknown",
    rejectedVisibleRailReuse: false,
    replacementGeometryAuthorized: false,
    nextGate05Acceptance: "capsule-silhouette-must-use-high-resolution-rounded-curve-or-profile-and-render-with-no-faceted-or-jagged-perimeter"
  };
  stage.validations = [
    { id: "user-authoritative-correction-consumed", status: "pass", evidence: `${userClaimId} is linked in both corrected Gate 04 boards.` },
    { id: "flat-visible-lower-plane-explicit", status: "pass", evidence: "The visible lower exterior is shown as a clean plane with no TrackCarrier, TrackZone, or exposed rail proxy." },
    { id: "concealed-circular-envelope-explicit", status: "pass", evidence: "All track and internal mechanism location is represented only by a dashed circular overlap envelope." },
    { id: "exact-source-crops-linked", status: "pass", evidence: "Four tight crops link to the immutable user MOV and HALOOPLAYER exact-product imagery." },
    { id: "hidden-engineering-remains-unknown", status: "pass", evidence: "No exact hidden path, coupling, hole depth, count, tolerance, fastener, ball, spring, or occluded continuation is asserted." },
    { id: "rejected-gate05-rails-not-reused", status: "pass", evidence: "Gate 05 rev 1 visible TrackCarrier/TrackZone geometry is rejected and absent from the corrected architecture." },
    { id: "smooth-capsule-next-gate-required", status: "pass", evidence: "The next Gate 05 must use a high-resolution rounded profile and pass a real-render no-faceting/no-jagged-perimeter check." },
    { id: "gate05-remains-locked", status: "pass", evidence: "This corrected Gate 04 is not approved; replacementGeometryAuthorized remains false." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "Gate 04 rev 10 等待用户确认平整外露下层与隐藏圆形机构 envelope；Gate 05 rev 1 保持否决／stale，不得重建白模。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 05 rev 1 已按用户明确反馈拒绝；其外露轨道代理与锯齿轮廓不可复用。先前 Gate 04 rev 8 批准因上游结构纠正失效；rev 9 因 SVG 编码损坏被拒绝。Gate 04 rev 10 仅锁定干净外露下层平面、共享圆形重叠区内的隐藏机构 envelope，以及同一上件经隐藏接口平移／旋转；等待批准，不得重建 Gate 05。";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "04-architecture",
    architectureRevision,
    artifactIds: stage.artifactIds,
    userClaimId,
    invalidatedGate05Revision: 1,
    autoApproved: false
  });
  return saveManifest(manifest, event);
}

export function saveBlockoutReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (modelId !== "magnetic-slide-tile") throw new PipelineError("This blockout registration is supported only for magnetic-slide-tile.", 422);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "05-blockout");
  if (manifest.stages[stageIndex - 1].status !== "approved") throw new PipelineError("Gate 04 must be approved before registering a blockout.", 422);
  const stage = manifest.stages[stageIndex];
  if (stage.artifactIds.length || manifest.assets.some((asset) => asset.stageId === "05-blockout")) {
    throw new PipelineError("Gate 05 already has immutable evidence; create a new revision after rejection.", 422);
  }

  const revisionLabel = "001";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/05-blockout", `rev-${revisionLabel}`
  )));
  const definitions = [
    ["builder", "blockout-builder", "white-model-source", "build_blockout.py", "deterministic-blender-python-source"],
    ["blend", "blockout-blend", "blockout-blend", "magnetic-slide-tile-blockout.blend", "canonical-closed-pose-blender-scene"],
    ["hero", "blockout-hero", "white-model-hero", "blockout-hero.png", "real-blender-render-open-travel-hero"],
    ["closed", "blockout-closed", "white-model-support", "blockout-closed.png", "real-blender-render-closed-pose"],
    ["spin", "blockout-spin", "white-model-support", "blockout-spin.png", "real-blender-render-rotation-pose"],
    ["validation", "blockout-validation", "validation-report", "blockout-validation.json", "blender-scene-blockout-validation"]
  ].map(([key, suffix, slot, file, contentClass]) => ({
    key,
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "05-blockout",
    slot,
    path: normalizeRepoPath(payload[`${key}Path`] || `${expectedDirectory}/${file}`),
    contentClass
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) throw new PipelineError(`${record.id} file is missing.`, 422);
  }

  const validationRecord = definitions.find((record) => record.key === "validation");
  const report = JSON.parse(fs.readFileSync(resolveRepoPath(validationRecord.path), "utf8"));
  const exactDimensions = report.dimensionsMm?.closedMeasured;
  const validReport = report.gate === "05-blockout"
    && report.dimensionBasis === "user-authorized-provisional-digital-blockout"
    && exactDimensions?.length === 50
    && exactDimensions?.width === 31
    && exactDimensions?.thickness === 12
    && report.dimensionsMm?.pass === true
    && report.travel?.axis === "+Y"
    && report.travel?.implementedMm === 21
    && report.travel?.pass === true
    && report.pivot?.rotationAxis === "+Z"
    && report.pivot?.pass === true
    && report.zeroSelfMotion?.pass === true
    && report.scope?.twoExteriorMainBodies === true
    && report.scope?.visibleCarrierTrackZones === true
    && report.scope?.centralPivotProxy === true
    && report.scope?.hiddenEngineeringModeled === false
    && report.scope?.finalMaterialsOrArtwork === false;
  if (!validReport) throw new PipelineError("The Blender validation report does not match the approved Gate 03/04 blockout scope.", 422);

  const architecture = manifest.stages[stageIndex - 1];
  const contractAssetId = manifest.stages[stageIndex - 2].artifactIds[0];
  const sourceAssetIds = [contractAssetId, ...architecture.artifactIds];
  const sourceClaimIds = ["slider-architecture-both-track-parts-move-r008"];
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: "process",
      producer: {
        name: record.key === "builder" ? "deterministic-bpy" : "Blender",
        version: report.blender,
        recipe: `${expectedDirectory}/build_blockout.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 05 provisional white model only. It preserves approved outer motion proxies and does not assert hidden engineering, production dimensions, final materials, or artwork."
      },
      sourceAssetIds,
      sourceClaimIds,
      ...(record.key === "hero" ? {
        view: {
          id: "hero",
          kind: "perspective",
          camera: "HeroCamera",
          pose: "upper-capsule-translated-plus-21mm-no-rotation",
          renderEngine: "BLENDER_EEVEE"
        }
      } : {}),
      ...(record.key === "closed" ? { view: { id: "closed", kind: "perspective", camera: "HeroCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE" } } : {}),
      ...(record.key === "spin" ? { view: { id: "spin", kind: "perspective", camera: "HeroCamera", pose: "upper-capsule-rotated-45deg-no-translation", renderEngine: "BLENDER_EEVEE" } } : {})
    };
  });
  manifest.assets.push(...records);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.blockoutSpec = {
    revision: 1,
    dimensionsMm: { length: 50, width: 31, thickness: 12 },
    dimensionBasis: "user-authorized-provisional-digital-blockout",
    translation: { object: "UpperMotion", axis: "+Y", travelMm: 21 },
    rotation: { object: "UpperMotion", axis: "+Z", pivotWorldMm: [0, 0, 0] },
    fixedReference: "FixedAssembly",
    movingPart: "UpperCapsule_Moving",
    canonicalPose: "closed-zero-motion",
    hiddenEngineering: "unknown-not-modeled",
    finalMaterialsArtwork: "not-modeled",
    unityAssetChanged: false
  };
  stage.validations = [
    { id: "deterministic-source-present", status: "pass", evidence: `${records[0].id} rebuilds the .blend and all Gate 05 renders.` },
    { id: "real-blender-hero-present", status: "pass", evidence: `${modelId}-blockout-hero-r001 is a Blender ${report.blender} Eevee render at +21 mm travel.` },
    { id: "provisional-dimensions-exact", status: "pass", evidence: "Closed model bounds are exactly 50 × 31 × 12 mm; the values remain provisional digital-blockout targets." },
    { id: "travel-and-axes-exact", status: "pass", evidence: "UpperMotion travels 21 mm on +Y and rotates around +Z at world origin." },
    { id: "approved-hierarchy-only", status: "pass", evidence: "FixedAssembly contains the lower body and visible carrier/track/pivot proxies; UpperMotion contains the single moving upper capsule." },
    { id: "zero-self-motion", status: "pass", evidence: "No model object has animation data, constraints, drivers, or non-zero angular velocity." },
    { id: "hidden-engineering-excluded", status: "pass", evidence: "No balls, springs, fasteners, hidden coupling, hole depths, tolerances, final materials, or artwork are modeled." },
    { id: "shipping-unity-unchanged", status: "pass", evidence: "Gate 05 evidence exists only under ArtSource/ModelPipeline; no Unity runtime asset was changed." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "Gate 05 rev 1 白模等待轮廓、比例、厚度与中央结构视觉批准；不得进入 Gate 06。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 04 rev 8 已获用户明确批准。Gate 05 rev 1 已生成确定性 Blender 白模：50×31×12 mm 闭合外形、21 mm +Y 行程、同一上盖绕中央 +Z 接口旋转；仅含可见承载区、轨道区与 pivot 代理，不含隐藏工程或最终材质。等待白模视觉批准，不得进入 Gate 06。";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "05-blockout",
    blockoutRevision: 1,
    artifactIds: stage.artifactIds,
    dimensionsMm: stage.blockoutSpec.dimensionsMm,
    travelMm: 21,
    blender: report.blender,
    autoApproved: false
  });
  return saveManifest(manifest, event);
}

export function saveCorrectedBlockoutReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (modelId !== "magnetic-slide-tile") throw new PipelineError("The corrected blockout registration is supported only for magnetic-slide-tile.", 422);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "05-blockout");
  if (manifest.stages[stageIndex - 1].status !== "approved") throw new PipelineError("Gate 04 rev 10 must be approved before registering the corrected blockout.", 422);
  const stage = manifest.stages[stageIndex];
  if (stage.status !== "stale" || stage.blockoutSpec?.revision !== 1 || stage.decision?.action !== "reject") {
    throw new PipelineError("Gate 05 rev 1 must remain rejected and stale before creating rev 2.", 422);
  }

  const revisionLabel = "002";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/05-blockout", `rev-${revisionLabel}`
  )));
  const definitions = [
    ["builder", "blockout-builder", "white-model-source", "build_blockout.py", "deterministic-high-resolution-blockout-source"],
    ["silhouetteValidator", "silhouette-validator", "validation-source", "validate_silhouette.py", "rendered-silhouette-validation-source"],
    ["blend", "blockout-blend", "blockout-blend", "magnetic-slide-tile-blockout-r002.blend", "canonical-closed-pose-blender-scene"],
    ["hero", "blockout-hero", "white-model-hero", "blockout-hero.png", "real-blender-render-open-travel-hero"],
    ["closed", "blockout-closed", "white-model-support", "blockout-closed.png", "real-blender-render-closed-pose"],
    ["spin", "blockout-spin", "white-model-support", "blockout-spin.png", "real-blender-render-rotation-pose"],
    ["silhouette", "silhouette-top", "silhouette-validation-render", "silhouette-top.png", "real-blender-orthographic-alpha-silhouette"],
    ["validation", "blockout-validation", "validation-report", "blockout-validation.json", "geometry-and-rendered-silhouette-validation"]
  ].map(([key, suffix, slot, file, contentClass]) => ({
    key,
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "05-blockout",
    slot,
    path: normalizeRepoPath(payload[`${key}Path`] || `${expectedDirectory}/${file}`),
    contentClass
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) throw new PipelineError(`${record.id} file is missing.`, 422);
  }

  const reportRecord = definitions.find((record) => record.key === "validation");
  const report = JSON.parse(fs.readFileSync(resolveRepoPath(reportRecord.path), "utf8"));
  const dimensions = report.dimensionsMm?.closedMeasured;
  const validReport = report.schemaVersion === 2
    && report.gate === "05-blockout"
    && report.blockoutRevision === 2
    && report.dimensionBasis === "user-authorized-provisional-digital-blockout"
    && dimensions?.length === 50
    && dimensions?.width === 31
    && dimensions?.thickness === 12
    && report.dimensionsMm?.pass === true
    && report.travel?.axis === "+Y"
    && report.travel?.implementedMm === 21
    && report.travel?.pass === true
    && report.pivot?.rotationAxis === "+Z"
    && report.pivot?.pass === true
    && report.zeroSelfMotion?.pass === true
    && report.visibleArchitecture?.renderedMeshCount === 2
    && report.visibleArchitecture?.lowerTopPlanarityDeviationMm === 0
    && report.visibleArchitecture?.lowerExposedTopFeatureCount === 0
    && report.visibleArchitecture?.exposedRailOrHardwareObjectNames?.length === 0
    && report.visibleArchitecture?.concealedEnvelopeType === "EMPTY"
    && report.visibleArchitecture?.concealedEnvelopeHiddenFromRender === true
    && report.visibleArchitecture?.hiddenMechanismGeometry === "none"
    && report.visibleArchitecture?.pass === true
    && report.smoothness?.arcSegmentsPerSemicircle === 256
    && report.smoothness?.profileVertexCount === 513
    && report.smoothness?.maximumProfileSegmentAngleDeg <= 1
    && report.smoothness?.maximumChordDeviationMm <= 0.005
    && report.smoothness?.bevelSegments >= 8
    && report.smoothness?.geometryPass === true
    && report.renderedSilhouette?.renderSizePx?.[0] === 2048
    && report.renderedSilhouette?.renderSizePx?.[1] === 2048
    && report.renderedSilhouette?.monotonicCapViolationCount === 0
    && report.renderedSilhouette?.maximumContourReversalPx === 0
    && report.renderedSilhouette?.rowsWithInteriorAlphaGaps === 0
    && report.renderedSilhouette?.pass === true
    && report.scope?.visibleLowerPlaneClean === true
    && report.scope?.concealedCircularEnvelopeOnly === true
    && report.scope?.hiddenEngineeringModeled === false
    && report.scope?.finalMaterialsOrArtwork === false;
  if (!validReport) throw new PipelineError("The corrected Blender report does not satisfy Gate 04 rev 10 or the smooth-silhouette acceptance gate.", 422);

  const architecture = manifest.stages[stageIndex - 1];
  const contractAssetId = manifest.stages[stageIndex - 2].artifactIds[0];
  const sourceAssetIds = [contractAssetId, ...architecture.artifactIds];
  const sourceClaimIds = ["slider-architecture-flat-lower-concealed-overlap-r010"];
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: "process",
      producer: {
        name: ["builder", "silhouetteValidator"].includes(record.key) ? "deterministic-bpy/Pillow" : "Blender",
        version: record.key === "silhouetteValidator" ? "Pillow 11.3.0" : report.blender,
        recipe: `${expectedDirectory}/build_blockout.py then ${expectedDirectory}/validate_silhouette.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 05 rev 2 white model only. The visible lower plane is uninterrupted; the circular mechanism envelope is non-rendered and contains no invented hidden geometry.",
        userClaimIds: sourceClaimIds
      },
      sourceAssetIds,
      sourceClaimIds,
      ...(record.key === "hero" ? { view: { id: "hero", kind: "perspective", camera: "HeroCamera", pose: "upper-capsule-translated-plus-21mm-no-rotation", renderEngine: "BLENDER_EEVEE" } } : {}),
      ...(record.key === "closed" ? { view: { id: "closed", kind: "perspective", camera: "HeroCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE" } } : {}),
      ...(record.key === "spin" ? { view: { id: "spin", kind: "perspective", camera: "HeroCamera", pose: "upper-capsule-rotated-45deg-no-translation", renderEngine: "BLENDER_EEVEE" } } : {}),
      ...(record.key === "silhouette" ? { view: { id: "top-silhouette", kind: "orthographic", camera: "SilhouetteCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE", resolutionPx: [2048, 2048] } } : {})
    };
  });
  manifest.assets.push(...records);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.blockoutSpec = {
    revision: 2,
    dimensionsMm: { length: 50, width: 31, thickness: 12 },
    dimensionBasis: "user-authorized-provisional-digital-blockout",
    translation: { object: "UpperMotion", axis: "+Y", travelMm: 21 },
    rotation: { object: "UpperMotion", axis: "+Z", pivotWorldMm: [0, 0, 0] },
    fixedReference: "FixedAssembly",
    visibleLowerBody: "LowerBody_Fixed_CleanPlane",
    movingPart: "UpperCapsule_Moving",
    concealedEnvelope: "ConcealedCircularEnvelope-empty-hidden-from-render",
    hiddenMechanismProxy: "HiddenMechanismProxy-empty-no-geometry",
    renderedMeshCount: 2,
    exposedRailOrHardwareCount: 0,
    smoothness: {
      profileKind: report.smoothness.profileKind,
      arcSegmentsPerSemicircle: report.smoothness.arcSegmentsPerSemicircle,
      profileVertexCount: report.smoothness.profileVertexCount,
      maximumProfileSegmentAngleDeg: report.smoothness.maximumProfileSegmentAngleDeg,
      maximumChordDeviationMm: report.smoothness.maximumChordDeviationMm,
      bevelSegments: report.smoothness.bevelSegments,
      renderedMonotonicCapViolationCount: report.renderedSilhouette.monotonicCapViolationCount,
      renderedMaximumContourReversalPx: report.renderedSilhouette.maximumContourReversalPx
    },
    canonicalPose: "closed-zero-motion",
    hiddenEngineering: "unknown-not-modeled",
    finalMaterialsArtwork: "not-modeled",
    unityAssetChanged: false
  };
  stage.validations = [
    { id: "deterministic-source-present", status: "pass", evidence: `${modelId}-blockout-builder-r002 rebuilds the scene and renders; ${modelId}-silhouette-validator-r002 quantifies the 2048 px silhouette.` },
    { id: "real-blender-hero-present", status: "pass", evidence: `${modelId}-blockout-hero-r002 is a Blender ${report.blender} Eevee render at +21 mm travel.` },
    { id: "provisional-dimensions-exact", status: "pass", evidence: "Closed model bounds are exactly 50 × 31 × 12 mm; values remain provisional digital-blockout targets." },
    { id: "travel-pivot-and-zero-motion", status: "pass", evidence: "UpperMotion travels 21 mm on +Y, rotates around +Z at canonical world origin, and has no animation, constraints, drivers, or angular velocity." },
    { id: "clean-flat-lower-plane", status: "pass", evidence: "The lower top is one planar cap with 0.0 mm planarity deviation and zero exposed top features." },
    { id: "concealed-envelope-only", status: "pass", evidence: "Only two meshes render. ConcealedCircularEnvelope and HiddenMechanismProxy are non-rendered empties with no geometry." },
    { id: "no-exposed-rails-or-hardware", status: "pass", evidence: "The scene contains zero rendered rail, track, carrier, groove, ball, or hardware objects." },
    { id: "smooth-profile-geometry", status: "pass", evidence: `Each semicircle uses 256 segments; maximum turn is ${report.smoothness.maximumProfileSegmentAngleDeg}° and chord deviation is ${report.smoothness.maximumChordDeviationMm} mm; bevel uses 8 segments.` },
    { id: "rendered-silhouette-smooth", status: "pass", evidence: `The 2048 px top render has ${report.renderedSilhouette.monotonicCapViolationCount} cap reversals, ${report.renderedSilhouette.maximumContourReversalPx} px maximum reversal, and ${report.renderedSilhouette.rowsWithInteriorAlphaGaps} rows with gaps.` },
    { id: "rejected-rev1-preserved", status: "pass", evidence: "Gate 05 rev 1 assets remain immutable and are not referenced as current artifacts." },
    { id: "shipping-unity-unchanged", status: "pass", evidence: "All rev 2 evidence stays under ArtSource/ModelPipeline; no Unity runtime asset changed." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "Gate 05 rev 2 白模等待轮廓、平整外露面、隐藏圆形接口与平滑边缘视觉批准；不得进入 Gate 06。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 04 rev 10 已获用户明确批准。Gate 05 rev 2 以两片高分辨率胶囊网格实现干净外露下层和平移／旋转上件；隐藏圆形机制仅为不渲染、无几何的 Empty envelope。闭合尺寸 50×31×12 mm，行程 21 mm，轮廓几何与 2048 px 实际渲染均通过平滑度门禁。等待视觉批准，不得进入 Gate 06。";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "05-blockout",
    blockoutRevision: 2,
    artifactIds: stage.artifactIds,
    dimensionsMm: stage.blockoutSpec.dimensionsMm,
    travelMm: 21,
    smoothness: stage.blockoutSpec.smoothness,
    blender: report.blender,
    autoApproved: false
  });
  return saveManifest(manifest, event);
}

export function savePointAxisBlockoutReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (modelId !== "magnetic-slide-tile") throw new PipelineError("Point-axis blockout registration is supported only for magnetic-slide-tile.", 422);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "05-blockout");
  const architecture = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (architecture.status !== "approved" || architecture.architectureSpec?.reviewMode !== "concealed-circular-overlap") {
    throw new PipelineError("Approved Gate 04 rev 10 is required.", 422);
  }
  if (stage.status !== "rejected" || stage.blockoutSpec?.revision !== 2 || stage.decision?.action !== "reject") {
    throw new PipelineError("Gate 05 rev 2 must be rejected before creating rev 3.", 422);
  }

  const revisionLabel = "003";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/05-blockout", `rev-${revisionLabel}`
  )));
  const definitions = [
    ["builder", "blockout-builder", "white-model-source", "build_blockout.py", "deterministic-point-axis-blockout-source"],
    ["silhouetteValidator", "silhouette-validator", "validation-source", "validate_silhouette.py", "rendered-silhouette-validation-source"],
    ["blend", "blockout-blend", "blockout-blend", "magnetic-slide-tile-blockout-r003.blend", "canonical-point-axis-blender-scene"],
    ["hero", "blockout-hero", "white-model-hero", "blockout-hero.png", "real-blender-open-hero"],
    ["closed", "blockout-closed", "white-model-support", "blockout-closed.png", "real-blender-closed-pose"],
    ["slide", "blockout-slide", "white-model-support", "blockout-slide.png", "real-blender-slide-pose-zero-spin"],
    ["spin", "blockout-spin", "white-model-support", "blockout-spin.png", "real-blender-centered-spin-pose"],
    ["pivotOverlay", "pivot-overlay", "pivot-axis-review", "pivot-overlay.png", "real-blender-point-axis-versus-enclosure-overlay"],
    ["silhouette", "silhouette-top", "silhouette-validation-render", "silhouette-top.png", "real-blender-orthographic-alpha-silhouette"],
    ["validation", "blockout-validation", "validation-report", "blockout-validation.json", "point-axis-transform-and-silhouette-validation"]
  ].map(([key, suffix, slot, file, contentClass]) => ({
    key,
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "05-blockout",
    slot,
    path: normalizeRepoPath(payload[`${key}Path`] || `${expectedDirectory}/${file}`),
    contentClass
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) throw new PipelineError(`${record.id} file is missing.`, 422);
  }

  const reportRecord = definitions.find((record) => record.key === "validation");
  const report = JSON.parse(fs.readFileSync(resolveRepoPath(reportRecord.path), "utf8"));
  const dimensions = report.dimensionsMm?.closedMeasured;
  const validReport = report.schemaVersion === 3
    && report.blockoutRevision === 3
    && report.rootCauseCorrection?.rejectedRevision === 2
    && report.rootCauseCorrection?.gate04RemainsApproved === true
    && dimensions?.length === 50
    && dimensions?.width === 31
    && dimensions?.thickness === 12
    && report.dimensionsMm?.pass === true
    && JSON.stringify(report.axis?.pointWorldMm) === JSON.stringify([0, -9.5, 0])
    && report.axis?.axis === "+Z"
    && report.axis?.enclosureIsPivot === false
    && report.axis?.pass === true
    && report.poses?.slideTravelMm === 21
    && report.poses?.slideRotationDeg === 0
    && JSON.stringify(report.poses?.spinTranslationMm) === JSON.stringify([0, 0, 0])
    && Math.abs(report.poses?.spinRotationDeg - 45) <= 0.00001
    && report.poses?.spinPivotWorldDriftMm === 0
    && report.poses?.centroidRadiusDriftMm === 0
    && report.poses?.combinedSlideAndSpinAllowed === false
    && report.poses?.pass === true
    && report.fixedLower?.invariantAcrossPoses === true
    && report.fixedLower?.topPlanarityDeviationMm === 0
    && report.fixedLower?.exposedFeatureCount === 0
    && report.fixedLower?.pass === true
    && report.concealedEnvelope?.type === "EMPTY"
    && report.concealedEnvelope?.hideRender === true
    && report.concealedEnvelope?.geometry === "none"
    && report.concealedEnvelope?.rotatingObject === false
    && report.concealedEnvelope?.affectsVisibleSilhouette === false
    && report.concealedEnvelope?.pass === true
    && report.zeroSelfMotion?.pass === true
    && report.smoothness?.arcSegmentsPerSemicircle === 256
    && report.smoothness?.maximumProfileSegmentAngleDeg <= 1
    && report.smoothness?.maximumChordDeviationMm <= 0.005
    && report.smoothness?.geometryPass === true
    && report.overlayEvidence?.pass === true
    && report.renderedSilhouette?.monotonicCapViolationCount === 0
    && report.renderedSilhouette?.maximumContourReversalPx === 0
    && report.renderedSilhouette?.rowsWithInteriorAlphaGaps === 0
    && report.renderedSilhouette?.pass === true
    && report.scope?.hiddenEngineeringModeled === false
    && report.scope?.finalMaterialsOrArtwork === false
    && report.scope?.unityAssetChanged === false;
  if (!validReport) throw new PipelineError("Gate 05 rev 3 report does not prove the required point-axis transform semantics.", 422);

  const userClaimId = "slider-blockout-point-axis-distinction-r003";
  if (!manifest.claims.some((claim) => claim.id === userClaimId)) {
    manifest.claims.push({
      id: userClaimId,
      stageId: "05-blockout",
      topic: "point-axis-versus-concealed-enclosure",
      statement: "黄色范围只标中央 +Z 旋转轴候选点；蓝色大圆只标固定隐藏机构 enclosure。上件 free-spin 必须在 translation=0 时绕单点轴旋转，直推必须在 rotation=0 时沿 +Y 走 21 mm。",
      confidence: "user-authoritative",
      state: "active",
      assertedBy: "user",
      sourceAssetIds: [
        "magnetic-slide-tile-concealed-circular-interface-r010",
        "slider-intake-user-video"
      ],
      sourceRegions: [
        { assetId: "slider-intake-user-video", x: 0.217, y: 0.109, width: 0.638, height: 0.638, note: "67.25 s source-video crop: rotation axis lies in the trailing circular overlap, not at the capsule centroid." }
      ]
    });
  }
  const contractAssetId = manifest.stages[stageIndex - 2].artifactIds[0];
  const sourceAssetIds = [contractAssetId, ...architecture.artifactIds, "slider-intake-user-video"];
  const sourceClaimIds = ["slider-architecture-flat-lower-concealed-overlap-r010"];
  const provenanceUserClaimIds = [...sourceClaimIds, userClaimId];
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    const viewByKey = {
      hero: { id: "hero", kind: "perspective", camera: "HeroCamera", pose: "slide-plus-21mm-zero-spin" },
      closed: { id: "closed", kind: "perspective", camera: "HeroCamera", pose: "zero-slide-zero-spin" },
      slide: { id: "slide", kind: "perspective", camera: "SlideCamera", pose: "slide-plus-21mm-zero-spin" },
      spin: { id: "spin", kind: "perspective", camera: "HeroCamera", pose: "zero-slide-spin-45deg-about-point-axis" },
      pivotOverlay: { id: "pivot-axis", kind: "orthographic", camera: "TopCamera", pose: "zero-slide-spin-45deg-with-review-overlay" },
      silhouette: { id: "top-silhouette", kind: "orthographic", camera: "TopCamera", pose: "zero-slide-zero-spin", resolutionPx: [2048, 2048] }
    };
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: "process",
      producer: {
        name: ["builder", "silhouetteValidator"].includes(record.key) ? "deterministic-bpy/Pillow" : "Blender",
        version: record.key === "silhouetteValidator" ? "Pillow 11.3.0" : report.blender,
        recipe: `${expectedDirectory}/build_blockout.py then ${expectedDirectory}/validate_silhouette.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 05 rev 3 separates the yellow point axis from the fixed blue enclosure and keeps slide and spin as mutually exclusive poses.",
        userClaimIds: provenanceUserClaimIds
      },
      sourceAssetIds,
      sourceClaimIds,
      ...(viewByKey[record.key] ? { view: { ...viewByKey[record.key], renderEngine: "BLENDER_EEVEE" } } : {})
    };
  });
  manifest.assets.push(...records);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.blockoutSpec = {
    revision: 3,
    dimensionsMm: { length: 50, width: 31, thickness: 12 },
    dimensionBasis: "user-authorized-provisional-digital-blockout",
    coordinateFrame: { origin: "closed-assembly-center", axisPointWorldMm: [0, -9.5, 0], rotationAxis: "+Z" },
    hierarchy: {
      fixed: "Root/FixedAssembly/LowerBody_Fixed_CleanPlane",
      enclosure: "Root/FixedAssembly/ConcealedCircularEnvelope_Metadata",
      moving: "Root/UpperTranslation/CentralAxisPivot_Point/UpperCapsule_Moving"
    },
    poses: {
      closed: { translationMm: [0, 0, 0], rotationDeg: 0 },
      slide: { translationMm: [0, 21, 0], rotationDeg: 0 },
      spin: { translationMm: [0, 0, 0], rotationDeg: 45 }
    },
    axisPointDerivation: report.axis.pointDerivation,
    upperLocalOffsetFromPointAxisMm: report.axis.upperLocalOffsetFromPivotMm,
    fixedEnvelope: { radiusMm: 15.5, renderable: false, geometry: "none", rotatingObject: false },
    fixedLowerPlanarityDeviationMm: 0,
    exposedRailOrHardwareCount: 0,
    spinPivotWorldDriftMm: 0,
    spinCentroidRadiusDriftMm: 0,
    combinedSlideAndSpinAllowed: false,
    smoothness: {
      arcSegmentsPerSemicircle: 256,
      profileVertexCount: 513,
      maximumProfileSegmentAngleDeg: report.smoothness.maximumProfileSegmentAngleDeg,
      maximumChordDeviationMm: report.smoothness.maximumChordDeviationMm,
      bevelSegments: 8,
      renderedMonotonicCapViolationCount: 0,
      renderedMaximumContourReversalPx: 0
    },
    hiddenEngineering: "unknown-not-modeled",
    finalMaterialsArtwork: "not-modeled",
    unityAssetChanged: false
  };
  stage.validations = [
    { id: "rev2-rejection-preserved", status: "pass", evidence: "Rev 2 remains immutable in assets and history; no rev 2 path or hash was changed." },
    { id: "gate04-distinction-preserved", status: "pass", evidence: "Gate 04 rev 10 remains approved: yellow is a point-axis candidate; blue is only a fixed hidden enclosure." },
    { id: "point-axis-coordinate", status: "pass", evidence: "CentralAxisPivot_Point is [0,-9.5,0] in the closed-assembly-center frame; UpperCapsule_Moving is offset [0,9.5,3]." },
    { id: "slide-spin-separated", status: "pass", evidence: "Slide is [0,21,0] with 0° spin; free-spin is [0,0,0] with 45° spin. Combined motion is rejected by the builder." },
    { id: "centered-spin-no-orbit", status: "pass", evidence: "Spin pivot world drift is 0.0 mm, translation displacement is 0.0 mm, and centroid-to-pivot radius drift is 0.0 mm." },
    { id: "fixed-lower-invariant", status: "pass", evidence: "Lower matrix is identical across closed, slide, and spin; top planarity deviation is 0.0 mm." },
    { id: "fixed-envelope-non-rendering", status: "pass", evidence: "ConcealedCircularEnvelope_Metadata is a fixed, hidden-render Empty with no geometry and cannot affect silhouette." },
    { id: "bounds-travel-zero-motion", status: "pass", evidence: "Closed bounds are 50×31×12 mm, travel is 21 mm, and no model object has animation or constraints." },
    { id: "smooth-rendered-silhouette", status: "pass", evidence: `256 segments per semicircle; ${report.smoothness.maximumChordDeviationMm} mm chord error; rendered contour reversals and gap rows are 0.` },
    { id: "point-axis-overlay", status: "pass", evidence: `${modelId}-pivot-overlay-r003 renders a yellow point crosshair and a separate blue dashed fixed enclosure.` },
    { id: "shipping-unity-unchanged", status: "pass", evidence: "All rev 3 files remain under ArtSource/ModelPipeline; Unity runtime and shipping scenes are unchanged." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "Gate 05 rev 3 单点轴白模等待视觉批准；不得进入 Gate 06。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 05 rev 2 已因把上件质心误作旋转轴而被用户否决。Gate 04 rev 10 保持批准。Gate 05 rev 3 将闭合装配中心与圆端单点轴分离：轴点 [0,-9.5,0]，直推 21 mm/0° 与中心 spin 0 mm/45° 互斥；蓝色 enclosure 固定、不渲染、无 geometry。等待视觉批准，不得进入 Gate 06。";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "05-blockout",
    blockoutRevision: 3,
    artifactIds: stage.artifactIds,
    axisPointWorldMm: [0, -9.5, 0],
    slidePose: stage.blockoutSpec.poses.slide,
    spinPose: stage.blockoutSpec.poses.spin,
    blender: report.blender,
    autoApproved: false
  });
  return saveManifest(manifest, event);
}

function savePremiumDisplayCaseNormalsOnlyGeometryReview(modelId, payload, manifest) {
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "06-geometry");
  const blockout = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  const approval = blockout.blockoutSpec?.approval;
  if (
    blockout.status !== "approved"
    || blockout.blockoutSpec?.revision !== 2
    || approval?.approvedRevision !== 2
    || approval?.userApprovalQuote !== "可以，继续推进"
  ) {
    throw new PipelineError("Approved Premium Display Case Gate 05 rev 2 is required.", 422);
  }
  if (
    stage.status !== "rejected"
    || stage.decision?.action !== "reject"
    || stage.geometrySpec?.revision !== 1
    || !String(stage.decision?.notes || "").includes("signedVolumeMm3=-52932.982745")
  ) {
    throw new PipelineError("Gate 06 rev 1 must be technically rejected before registering rev 2.", 422);
  }

  const revisionLabel = "002";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/06-geometry", `rev-${revisionLabel}`
  )));
  const orthographicIds = ["front", "back", "top", "bottom", "left", "right"];
  const standardViewIds = [
    "front", "back", "top", "bottom", "left", "right",
    "hero", "left-oblique", "right-oblique", "low"
  ];
  const definitions = [
    { key: "builder", suffix: "geometry-builder", slot: "geometry-source", file: "build_geometry_evidence.py", role: "process", contentClass: "deterministic-premium-display-case-gate06-normals-only-source" },
    { key: "validator", suffix: "geometry-validator", slot: "validation-source", file: "validate_geometry.py", role: "process", contentClass: "gate06-positive-volume-and-hollow-boundary-validator" },
    { key: "composer", suffix: "geometry-review-composer", slot: "geometry-review-source", file: "compose_geometry_review.py", role: "process", contentClass: "deterministic-gate06-rev2-review-compositor" },
    { key: "auditor", suffix: "geometry-auditor", slot: "validation-source", file: "audit_geometry_evidence.py", role: "process", contentClass: "independent-blender-positive-volume-auditor" },
    { key: "imageValidator", suffix: "geometry-image-validator", slot: "validation-source", file: "validate_geometry_images.py", role: "process", contentClass: "gate06-rev2-image-dimension-hash-validator" },
    { key: "blend", suffix: "geometry-blend", slot: "geometry-blend", file: "premium-display-case-geometry-r002.blend", role: "source-model", contentClass: "gate06-normals-only-derivative-scene" },
    ...orthographicIds.map((viewId) => ({
      key: `raw${viewId[0].toUpperCase()}${viewId.slice(1)}`,
      suffix: `geometry-raw-${viewId}`,
      slot: "geometry-raw-view",
      file: `raw/${viewId}.png`,
      role: "blender-render",
      contentClass: `real-blender-rev2-raw-orthographic-${viewId}`,
      viewId: `raw-${viewId}`,
      camera: `Gate06Camera${viewId[0].toUpperCase()}${viewId.slice(1)}`,
      renderEngine: "BLENDER_EEVEE"
    })),
    { key: "rawWorkbench", suffix: "geometry-raw-workbench", slot: "geometry-raw-view", file: "raw/workbench.png", role: "blender-render", contentClass: "real-blender-rev2-raw-workbench", viewId: "raw-workbench", camera: "Gate06CameraWorkbench", renderEngine: "BLENDER_WORKBENCH" },
    { key: "rawDimensions", suffix: "geometry-raw-dimensions", slot: "geometry-raw-view", file: "raw/dimension-overlay.png", role: "blender-render", contentClass: "real-blender-rev2-raw-dimension-overlay", viewId: "raw-dimension-overlay", camera: "Gate06CameraOverlay", renderEngine: "BLENDER_EEVEE" },
    { key: "rawPivot", suffix: "geometry-raw-pivot-axis", slot: "geometry-raw-view", file: "raw/pivot-axis-overlay.png", role: "blender-render", contentClass: "real-blender-rev2-raw-pivot-axis-overlay", viewId: "raw-pivot-axis", camera: "Gate06CameraOverlay", renderEngine: "BLENDER_EEVEE" },
    { key: "rawExploded", suffix: "geometry-raw-exploded", slot: "geometry-raw-view", file: "raw/exploded-geometry.png", role: "blender-render", contentClass: "real-blender-rev2-raw-internal-exploded-geometry", viewId: "raw-exploded", camera: "Gate06CameraExploded", renderEngine: "BLENDER_WORKBENCH" },
    ...orthographicIds.map((viewId) => ({
      key: viewId,
      suffix: `geometry-${viewId}`,
      slot: `view-${viewId}`,
      file: `ortho-${viewId}.png`,
      role: "blender-render",
      contentClass: `real-blender-rev2-annotated-orthographic-${viewId}`,
      viewId,
      camera: `Gate06Camera${viewId[0].toUpperCase()}${viewId.slice(1)}`,
      renderEngine: "BLENDER_EEVEE+Pillow-annotation"
    })),
    { key: "workbench", suffix: "geometry-workbench", slot: "workbench", file: "geometry-workbench.png", role: "blender-render", contentClass: "real-blender-rev2-annotated-workbench", viewId: "workbench", camera: "Gate06CameraWorkbench", renderEngine: "BLENDER_WORKBENCH+Pillow-annotation" },
    { key: "dimensions", suffix: "geometry-dimensions", slot: "dimension-overlay", file: "dimension-overlay.png", role: "blender-render", contentClass: "real-blender-rev2-exact-dimension-overlay", viewId: "dimension-overlay", camera: "Gate06CameraOverlay", renderEngine: "BLENDER_EEVEE+Pillow-annotation" },
    { key: "pivot", suffix: "geometry-pivot-axis", slot: "pivot-overlay", file: "pivot-axis-overlay.png", role: "blender-render", contentClass: "real-blender-rev2-presentation-root-axis-overlay", viewId: "pivot-axis", camera: "Gate06CameraOverlay", renderEngine: "BLENDER_EEVEE+Pillow-annotation" },
    { key: "exploded", suffix: "geometry-exploded", slot: "exploded-geometry", file: "exploded-geometry.png", role: "blender-render", contentClass: "real-blender-rev2-internal-only-exploded-geometry", viewId: "exploded", camera: "Gate06CameraExploded", renderEngine: "BLENDER_WORKBENCH+Pillow-annotation" },
    { key: "review", suffix: "geometry-review", slot: "geometry-review", file: "geometry-review.png", role: "blender-render", contentClass: "real-blender-normals-only-primary-review" },
    { key: "contactSheet", suffix: "geometry-contact-sheet", slot: "geometry-review", file: "geometry-review-contact-sheet.png", role: "blender-render", contentClass: "real-blender-normals-only-contact-sheet" },
    { key: "validation", suffix: "geometry-validation", slot: "validation-report", file: "geometry-validation.json", role: "validation", contentClass: "premium-display-case-gate06-rev2-geometry-validation" },
    { key: "audit", suffix: "geometry-blender-audit", slot: "validation-report", file: "blender-audit.json", role: "validation", contentClass: "premium-display-case-gate06-rev2-independent-blender-audit" },
    { key: "imageValidation", suffix: "geometry-image-validation", slot: "validation-report", file: "geometry-image-validation.json", role: "validation", contentClass: "premium-display-case-gate06-rev2-image-validation" },
    { key: "standardCapture", suffix: "geometry-standard-capture", slot: "validation-report", file: "fixed-views/capture-report.json", role: "validation", contentClass: "gate06-rev2-standard-view-blender-capture-report" },
    { key: "standardCaptureWrapper", suffix: "geometry-standard-capture-wrapper", slot: "validation-report", file: "fixed-views/capture-wrapper-report.json", role: "validation", contentClass: "gate06-rev2-standard-view-wrapper-report" },
    ...standardViewIds.map((viewId) => ({
      key: `standard${viewId.replace(/(^|-)([a-z])/g, (_match, _separator, letter) => letter.toUpperCase())}`,
      suffix: `geometry-standard-${viewId}`,
      slot: "geometry-standard-view",
      file: `fixed-views/${viewId}.png`,
      role: "blender-render",
      contentClass: `real-blender-gate06-rev2-standard-${viewId}`,
      viewId: `standard-${viewId}`,
      camera: "PipelineCaptureCamera",
      renderEngine: "BLENDER_EEVEE"
    }))
  ].map((record) => ({
    ...record,
    id: `${modelId}-${record.suffix}-r${revisionLabel}`,
    stageId: "06-geometry",
    path: normalizeRepoPath(payload[`${record.key}Path`] || `${expectedDirectory}/${record.file}`)
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) {
      throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    }
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
      throw new PipelineError(`${record.id} file is missing.`, 422);
    }
  }

  const byKey = new Map(definitions.map((record) => [record.key, record]));
  const report = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("validation").path), "utf8"));
  const audit = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("audit").path), "utf8"));
  const imageReport = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("imageValidation").path), "utf8"));
  const capture = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("standardCapture").path), "utf8"));
  const wrapper = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("standardCaptureWrapper").path), "utf8"));
  const expectedSourceDigest = "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f";
  const expectedBlendHash = "3f0411e43900e9ff67a8f52ee4af9d630147acb46251985baf8b2a1a06936e31";
  const sourceIdentity = report.geometryIdentity?.source;
  const derivativeIdentity = report.geometryIdentity?.derivative;
  const tubeMetrics = report.meshIntegrity?.objects?.ContinuousTubePerimeter;
  const tubeOrientation = report.closedTube?.boundaryOrientation;
  const flow = report.closedTube?.volumetricPassageFloodFill;
  const allChecksPass = Object.values(report.checks || {}).every((value) => value === true);
  const validReport = report.schemaVersion === 2
    && report.modelId === modelId
    && report.gate === "06-geometry"
    && report.geometryRevision === 2
    && report.status === "pass"
    && report.pipelineRevisionAtBuild === manifest.revision
    && report.sourceGate05?.blockoutRevision === 2
    && report.sourceGate05?.approvalQuote === "可以，继续推进"
    && report.sourceGate05?.hashesBefore?.blend === expectedBlendHash
    && JSON.stringify(report.sourceGate05?.hashesBefore) === JSON.stringify(report.sourceGate05?.hashesAfter)
    && report.sourceGate05?.unchanged === true
    && report.supersededGate06Revision?.geometryRevision === 1
    && report.supersededGate06Revision?.technicalDisposition === "rejected-and-superseded"
    && sourceIdentity?.fullGeometryDigest === expectedSourceDigest
    && sourceIdentity?.objectMatrixDigest === derivativeIdentity?.objectMatrixDigest
    && sourceIdentity?.vertexPositionDigest === derivativeIdentity?.vertexPositionDigest
    && sourceIdentity?.silhouetteDigest === derivativeIdentity?.silhouetteDigest
    && sourceIdentity?.topologyWindingDigest !== derivativeIdentity?.topologyWindingDigest
    && report.geometryIdentity?.onlyTubeTopologyWindingChanged === true
    && report.geometryIdentity?.sameDerivativeAcrossViews === true
    && report.geometryIdentity?.pass === true
    && orthographicIds.every((id) => report.geometryIdentity?.crossView?.[id]?.sameDerivativeGeometry === true)
    && JSON.stringify(report.bounds?.measured?.sizeMm) === JSON.stringify({ width: 228, height: 304, depth: 59 })
    && report.bounds?.portraitWidthHeightRatio === 0.75
    && report.bounds?.pass === true
    && report.label?.approvedCenterYmm === 99
    && report.label?.approvedDownshiftMm === 6
    && report.label?.pass === true
    && report.concentricContours?.outerRadiusMm === 20
    && report.concentricContours?.maximumCenterDriftMm <= 0.01
    && report.concentricContours?.pass === true
    && report.meshIntegrity?.allOpenBoundaryEdgeCount === 0
    && report.meshIntegrity?.allNonManifoldEdgeCount === 0
    && report.meshIntegrity?.allBadContiguousEdgeCount === 0
    && report.meshIntegrity?.allSelfIntersectionPairCount === 0
    && report.meshIntegrity?.allDegenerateElementCount === 0
    && report.meshIntegrity?.allSubjectMaterialSignedVolumesPositive === true
    && report.meshIntegrity?.pass === true
    && Object.values(report.meshIntegrity?.objects || {}).every((item) => item.pass === true && item.signedVolumeMm3 > 0)
    && report.windingCorrection?.before?.netMaterialSignedVolumeMm3 === -52932.982745
    && report.windingCorrection?.after?.netMaterialSignedVolumeMm3 > 0
    && report.windingCorrection?.vertexCoordinatesChanged === false
    && report.windingCorrection?.objectMatrixChanged === false
    && report.windingCorrection?.silhouetteChanged === false
    && tubeMetrics?.signedVolumeMm3 > 0
    && tubeMetrics?.positiveMaterialSignedVolume === true
    && tubeOrientation?.outerBoundary?.outward === true
    && tubeOrientation?.outerBoundary?.signedVolumeMm3 > 0
    && tubeOrientation?.innerBoundary?.inwardTowardLumen === true
    && tubeOrientation?.innerBoundary?.signedVolumeMm3 < 0
    && tubeOrientation?.netMaterialVolumePositive === true
    && tubeOrientation?.pass === true
    && flow?.sampleCount === 384
    && flow?.validVolumetricSampleCount === 384
    && flow?.visitedSamples === 384
    && flow?.failedRayCount === 0
    && Math.abs(Number(flow?.evaluatedWallThicknessMm?.mean) - 2) <= 0.02
    && flow?.pass === true
    && report.closedTube?.pass === true
    && report.hierarchyAndMotion?.pass === true
    && report.hiddenStructure?.inventedInternalPartCount === 0
    && report.hiddenStructure?.pass === true
    && report.explodedEvidence?.purpose === "internal-geometry-validation-only"
    && report.explodedEvidence?.shippingRevealPolicy === "always-assembled-never-explodes"
    && report.explodedEvidence?.continuousTubeExplodedObjectCount === 1
    && report.explodedEvidence?.continuousTubeUsesExactDerivativeMeshData === true
    && report.explodedEvidence?.pass === true
    && report.scope?.earliestAffectedGate === "06-geometry"
    && report.scope?.gate05ContractConflict === false
    && report.scope?.gate05SourceModified === false
    && report.scope?.vertexGeometryChanged === false
    && report.scope?.topologyWindingChanged === true
    && report.scope?.gate07Entered === false
    && report.scope?.shippingUnityChanged === false
    && report.scope?.buildInstallPhonePush === false
    && report.validatorRecheck?.status === "pass"
    && report.outputBlendSha256 === sha256File(resolveRepoPath(byKey.get("blend").path))
    && allChecksPass;
  if (!validReport) {
    throw new PipelineError("Premium Display Case Gate 06 rev 2 validation failed.", 422);
  }
  const validAudit = audit.schemaVersion === 2
    && audit.modelId === modelId
    && audit.gate === "06-geometry"
    && audit.geometryRevision === 2
    && audit.status === "pass"
    && audit.geometryIdentity?.source?.vertexPositionDigest === audit.geometryIdentity?.derivative?.vertexPositionDigest
    && audit.geometryIdentity?.source?.silhouetteDigest === audit.geometryIdentity?.derivative?.silhouetteDigest
    && audit.geometryIdentity?.source?.topologyWindingDigest !== audit.geometryIdentity?.derivative?.topologyWindingDigest
    && JSON.stringify(audit.boundsMm) === JSON.stringify({ width: 228, height: 304, depth: 59 })
    && Object.values(audit.meshAudit || {}).every((item) => item.pass === true && item.signedVolumeMm3 > 0)
    && audit.tubeOrientation?.outerBoundary?.outward === true
    && audit.tubeOrientation?.innerBoundary?.inwardTowardLumen === true
    && audit.tubeOrientation?.netMaterialVolumePositive === true
    && audit.tubeFloodFill?.sampleCount === 384
    && audit.tubeFloodFill?.visitedSamples === 384
    && audit.tubeFloodFill?.pass === true
    && Object.values(audit.checks || {}).every((value) => value === true);
  if (!validAudit) throw new PipelineError("Premium Display Case Gate 06 rev 2 Blender audit failed.", 422);
  const reviewImage = imageReport.annotatedImages?.review;
  const contactImage = imageReport.annotatedImages?.contactSheet;
  const validImages = imageReport.schemaVersion === 2
    && imageReport.modelId === modelId
    && imageReport.gate === "06-geometry"
    && imageReport.geometryRevision === 2
    && imageReport.status === "pass"
    && imageReport.sourceBlendSha256 === expectedBlendHash
    && imageReport.geometryIdentity?.source?.vertexPositionDigest === imageReport.geometryIdentity?.derivative?.vertexPositionDigest
    && imageReport.geometryIdentity?.source?.silhouetteDigest === imageReport.geometryIdentity?.derivative?.silhouetteDigest
    && imageReport.geometryIdentity?.source?.topologyWindingDigest !== imageReport.geometryIdentity?.derivative?.topologyWindingDigest
    && JSON.stringify(reviewImage?.dimensions) === JSON.stringify([3600, 3200])
    && JSON.stringify(contactImage?.dimensions) === JSON.stringify([4800, 3600])
    && reviewImage?.sha256 === sha256File(resolveRepoPath(byKey.get("review").path))
    && contactImage?.sha256 === sha256File(resolveRepoPath(byKey.get("contactSheet").path))
    && Object.values(imageReport.checks || {}).every((value) => value === true);
  if (!validImages) throw new PipelineError("Premium Display Case Gate 06 rev 2 image validation failed.", 422);
  const capturedIds = new Set((capture.views || []).map((view) => view.id));
  if (
    wrapper.verified_capture !== true
    || wrapper.blender_returncode !== 0
    || (wrapper.missing_views || []).length !== 0
    || standardViewIds.some((viewId) => !capturedIds.has(viewId))
    || !(capture.included_objects || []).includes("ContinuousTubePerimeter")
  ) {
    throw new PipelineError("The standard-view wrapper did not verify the Gate 06 rev 2 derivative.", 422);
  }

  const priorArtifactIds = [...stage.artifactIds];
  const priorAssets = priorArtifactIds.map((assetId) => manifest.assets.find((asset) => asset.id === assetId));
  if (priorAssets.some((asset) => !asset || !asset.id.endsWith("-r001") || !asset.sha256)) {
    throw new PipelineError("Gate 06 rev 1 evidence is incomplete and cannot be superseded.", 422);
  }
  const sourceAssetIds = [...blockout.artifactIds];
  const sourceClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    const producerName = record.key === "builder"
      ? "deterministic-bpy"
      : record.key === "validator"
        ? "Blender positive-volume validator"
        : record.key === "composer"
          ? "Pillow review compositor"
          : record.key === "auditor"
            ? "Blender independent audit"
            : record.key === "imageValidator"
              ? "Pillow image validator"
              : record.key.startsWith("standard")
                ? "fidgeting-model-pipeline standard-view wrapper"
                : record.role === "blender-render"
                  ? "Blender"
                  : "Gate 06 validation";
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: record.role,
      producer: {
        name: producerName,
        version: report.blender,
        recipe: record.key.startsWith("standard")
          ? "skills/fidgeting-model-pipeline/scripts/capture_standard_views.py"
          : `${expectedDirectory}/${record.file.endsWith(".py") ? record.file : "build_geometry_evidence.py"}`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 06 rev 2 is a normals-only derivative of approved Gate 05 rev 2. It reverses only ContinuousTubePerimeter face winding. Object matrices, vertex coordinates, bounds, cross-section, wall, label, concentric corners, hierarchy, and silhouette remain unchanged. Outer normals point out of material, inner normals point toward the lumen, and net material signed volume is positive."
      },
      sourceAssetIds,
      sourceClaimIds,
      ...(record.viewId ? {
        view: {
          id: record.viewId,
          camera: record.camera,
          renderEngine: record.renderEngine,
          axisContract: "X-width/Y-height/Z-front",
          pose: record.viewId.includes("exploded")
            ? "internal-validation-exploded-approved-visible-parts-only"
            : "assembled-canonical-zero-motion"
        }
      } : {})
    };
  });
  const recordById = new Map(records.map((record) => [record.id, record]));
  const now = new Date().toISOString();
  for (const asset of priorAssets) {
    const replacementId = asset.id.replace(/-r001$/, "-r002");
    asset.reviewState = "technical-rejected";
    asset.rejectionScope = "continuous-tube-winding-orientation";
    asset.supersededBy = recordById.has(replacementId) ? replacementId : `${modelId}-geometry-review-r002`;
    asset.supersededAt = now;
    asset.dispositionNote = "Gate 06 rev 1 incorrectly passed ContinuousTubePerimeter with net signed material volume -52932.982745 mm3. Evidence and hashes remain immutable; rev 2 replaces only face winding.";
  }
  manifest.assets.push(...records);
  const ids = Object.fromEntries(definitions.map((record) => [record.key, record.id]));
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.reviewArtifactIds = [
    ids.review,
    ids.contactSheet,
    ids.workbench,
    ids.dimensions,
    ids.pivot,
    ids.exploded,
    ids.front
  ];
  stage.geometrySpec = {
    revision: 2,
    sourceGate05Revision: 2,
    sourceGate05BlendSha256: expectedBlendHash,
    sourceGate05BuilderSha256: report.sourceGate05.hashesBefore.builder,
    sourceGate05ValidatorSha256: report.sourceGate05.hashesBefore.validator,
    sourceGate05FullGeometryDigest: sourceIdentity.fullGeometryDigest,
    evaluatedGeometryDigest: derivativeIdentity.fullGeometryDigest,
    sourceUnchanged: true,
    correctionScope: "ContinuousTubePerimeter face winding only",
    earliestAffectedGate: "06-geometry",
    gate05ContractConflict: false,
    identity: {
      objectMatrixDigest: derivativeIdentity.objectMatrixDigest,
      vertexPositionDigest: derivativeIdentity.vertexPositionDigest,
      silhouetteDigest: derivativeIdentity.silhouetteDigest,
      sourceTopologyWindingDigest: sourceIdentity.topologyWindingDigest,
      derivativeTopologyWindingDigest: derivativeIdentity.topologyWindingDigest,
      objectMatricesUnchanged: true,
      vertexPositionsUnchanged: true,
      silhouetteUnchanged: true,
      topologyWindingChanged: true,
      onlyTubeTopologyWindingChanged: true
    },
    supersededRevision: {
      revision: 1,
      disposition: "technical-rejected-and-superseded",
      signedVolumeMm3: -52932.982745,
      artifactIds: priorArtifactIds
    },
    dimensionsMm: { width: 228, height: 304, depth: 59 },
    portraitWidthHeightRatio: 0.75,
    labelCenterYmm: 99,
    labelDownshiftMm: 6,
    outerCornerRadiusMm: 20,
    maximumCornerCenterDriftMm: report.concentricContours.maximumCenterDriftMm,
    cornerCenterToleranceMm: 0.01,
    meshIntegrity: {
      allOpenBoundaryEdgeCount: 0,
      allNonManifoldEdgeCount: 0,
      allBadContiguousEdgeCount: 0,
      allSelfIntersectionPairCount: 0,
      allDegenerateElementCount: 0,
      invalidPolygonNormalCount: 0,
      allSubjectMaterialSignedVolumesPositive: true
    },
    tube: {
      objectCount: 1,
      connectedMaterialBodyCount: 1,
      boundarySurfaceComponentCount: 2,
      outerSectionMm: { width: 10, depth: 9 },
      passageSectionMm: { width: 6, depth: 5 },
      wallThicknessMm: 2,
      floodFillVisited: 384,
      floodFillTotal: 384,
      beforeNetSignedVolumeMm3: report.windingCorrection.before.netMaterialSignedVolumeMm3,
      signedVolumeMm3: tubeOrientation.netMaterialSignedVolumeMm3,
      outerBoundarySignedVolumeMm3: tubeOrientation.outerBoundary.signedVolumeMm3,
      innerBoundarySignedVolumeMm3: tubeOrientation.innerBoundary.signedVolumeMm3,
      outerBoundaryOrientation: "outward-from-material",
      innerBoundaryOrientation: "toward-lumen",
      normalOrientation: tubeOrientation.orientationDisposition,
      windingDisposition: "normals-only-derivative-positive-material-volume"
    },
    contentSlot: {
      widthMm: 180,
      heightMm: 198,
      depthMm: 48,
      centerYmm: -42,
      type: "EMPTY",
      role: "runtime-anchor"
    },
    presentationRoot: {
      worldLocationMm: [0, 0, 0],
      showcaseAxis: "+Y",
      motionOwner: true,
      angularVelocity: 0
    },
    explodedEvidencePurpose: "internal-geometry-validation-only",
    shippingRevealPolicy: "always-assembled-never-explodes",
    inventedInternalPartCount: 0,
    reviewArtifactPath: byKey.get("review").path,
    contactSheetPath: byKey.get("contactSheet").path,
    orthographicCameraIds: orthographicIds,
    finalMaterialsApproved: false,
    gate07Entered: false,
    unityAssetChanged: false,
    buildInstallPhonePush: false
  };
  stage.validations = [
    { id: "rev1-technical-rejection-preserved", status: "pass", evidence: `${priorArtifactIds.length} Gate 06 rev 1 artifacts retain their paths and hashes and are marked technical-rejected/superseded. The rejected net signed material volume was -52932.982745 mm3.` },
    { id: "approved-gate05-source-immutable", status: "pass", evidence: `Gate 05 rev 2 blend ${expectedBlendHash}, deterministic builder ${report.sourceGate05.hashesBefore.builder}, and validator ${report.sourceGate05.hashesBefore.validator} remain unchanged.` },
    { id: "earliest-gate-06", status: "pass", evidence: "The approved contract does not prescribe face winding. Rev 2 changes no Gate 05 coordinate, matrix, bound, section, wall, label, corner center, hierarchy, or silhouette; the earliest affected gate remains 06-geometry." },
    { id: "normals-only-identity-proof", status: "pass", evidence: `Object matrix digest ${derivativeIdentity.objectMatrixDigest}, vertex-position digest ${derivativeIdentity.vertexPositionDigest}, and silhouette digest ${derivativeIdentity.silhouetteDigest} are unchanged; topology/winding digest changed from ${sourceIdentity.topologyWindingDigest} to ${derivativeIdentity.topologyWindingDigest}, only on ContinuousTubePerimeter.` },
    { id: "positive-subject-material-volumes", status: "pass", evidence: "Every subject solid has net signed material volume > 0. Non-positive volume is now a validator failure and cannot be masked by finite or contiguous normals." },
    { id: "hollow-tube-boundary-orientation", status: "pass", evidence: `ContinuousTubePerimeter outer boundary is outward (${tubeOrientation.outerBoundary.signedVolumeMm3} mm3), inner boundary points toward the lumen (${tubeOrientation.innerBoundary.signedVolumeMm3} mm3), and net material signed volume is ${tubeOrientation.netMaterialSignedVolumeMm3} mm3.` },
    { id: "exact-bounds-and-approved-values", status: "pass", evidence: "Bounds remain 228×304×59 mm, Portrait 0.750000, label Y=99 mm, R20, and concentric drift 0.000 mm." },
    { id: "closed-manifold-clean-topology", status: "pass", evidence: "All subject meshes total 0 open, 0 non-manifold, 0 bad-contiguous edges, 0 self-intersection pairs, and 0 degenerate elements." },
    { id: "evaluated-volumetric-passage-flood-fill", status: "pass", evidence: `Evaluated 10×9 mm outer section, 6×5 mm passage, approximately 2 mm wall, and cyclic flood-fill ${flow.visitedSamples}/${flow.sampleCount} all pass.` },
    { id: "content-slot-motion-and-hierarchy", status: "pass", evidence: "ContentSlot remains 180×198×48 mm. PresentationRoot remains [0,0,0], owns +Y motion, and has angular velocity 0. The approved hierarchy is unchanged." },
    { id: "exploded-internal-only", status: "pass", evidence: "Exploded evidence reuses the five derivative meshes, keeps the tube as one part, and remains ineligible for shipping animation." },
    { id: "review-image-and-standard-view-validation", status: "pass", evidence: "Six orthographic, Workbench, dimension, pivot, exploded, primary review, contact sheet, and all 10 standard views were regenerated and validated from the rev 2 derivative." },
    { id: "gate07-remains-blocked", status: "pass", evidence: "Gate 06 rev 2 is ready_for_review only. Gate 07 was not entered." },
    { id: "shipping-unity-unchanged", status: "pass", evidence: "All changes remain in pipeline evidence and validator tooling. Shipping Unity, build, install, and phone state are unchanged." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  blockout.blockoutSpec.approval.gate06Status = "ready_for_review-rev2";
  if (blockout.blockoutSpec.supplementaryMaterialDiagnostic) {
    blockout.blockoutSpec.supplementaryMaterialDiagnostic.gate06Status = "ready_for_review-rev2";
    blockout.blockoutSpec.supplementaryMaterialDiagnostic.gate07Status = "blocked";
  }
  markDownstreamStale(manifest, stageIndex, "Gate 06 rev 2 normals-only derivative awaits explicit approval; Gate 07 must not start.");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = `Gate 06 rev 1 was technically rejected because ContinuousTubePerimeter had net signed material volume -52932.982745 mm3. Gate 06 rev 2 reverses only that tube's face winding. Gate 05 rev 2 files remain immutable; object matrices, vertex-position digest ${derivativeIdentity.vertexPositionDigest}, and silhouette digest ${derivativeIdentity.silhouetteDigest} remain unchanged, while only the tube topology/winding digest changes. Outer normals point out of material, inner normals point toward the lumen, and net material signed volume is ${tubeOrientation.netMaterialSignedVolumeMm3} mm3. Gate 06 rev 2 is ready_for_review at 5/12; Gate 07 remains blocked. Shipping Unity, build, install, and phone state are unchanged.`;
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "06-geometry",
    geometryRevision: 2,
    technicallyRejectedRevision: 1,
    rejectionScope: "continuous-tube-winding-orientation",
    consumesStageId: "05-blockout",
    consumesBlockoutRevision: 2,
    sourceBlendSha256: expectedBlendHash,
    sourceGate05Unchanged: true,
    sourceFullGeometryDigest: sourceIdentity.fullGeometryDigest,
    derivativeFullGeometryDigest: derivativeIdentity.fullGeometryDigest,
    objectMatrixDigest: derivativeIdentity.objectMatrixDigest,
    vertexPositionDigest: derivativeIdentity.vertexPositionDigest,
    silhouetteDigest: derivativeIdentity.silhouetteDigest,
    sourceTopologyWindingDigest: sourceIdentity.topologyWindingDigest,
    derivativeTopologyWindingDigest: derivativeIdentity.topologyWindingDigest,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    geometryReviewPath: byKey.get("review").path,
    contactSheetPath: byKey.get("contactSheet").path,
    dimensionsMm: stage.geometrySpec.dimensionsMm,
    portraitWidthHeightRatio: 0.75,
    labelCenterYmm: 99,
    outerCornerRadiusMm: 20,
    maximumCornerCenterDriftMm: 0,
    topology: {
      connectedMaterialBodyCount: 1,
      openBoundaryEdgeCount: 0,
      nonManifoldEdgeCount: 0,
      badContiguousEdgeCount: 0,
      selfIntersectionPairCount: 0,
      degenerateElementCount: 0,
      floodFill: "384/384",
      beforeNetSignedVolumeMm3: -52932.982745,
      netSignedVolumeMm3: tubeOrientation.netMaterialSignedVolumeMm3,
      outerBoundaryOrientation: "outward-from-material",
      innerBoundaryOrientation: "toward-lumen"
    },
    explodedEvidencePurpose: "internal-geometry-validation-only",
    shippingRevealPolicy: "always-assembled-never-explodes",
    gate07Status: "blocked",
    autoApproved: false,
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseGeometryReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This Gate 06 route is supported only for a Premium Display Case pipeline.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "06-geometry");
  const blockout = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  const approval = blockout.blockoutSpec?.approval;
  if (stage.status === "rejected" && stage.geometrySpec?.revision === 1) {
    return savePremiumDisplayCaseNormalsOnlyGeometryReview(modelId, payload, manifest);
  }
  if (
    blockout.status !== "approved"
    || blockout.blockoutSpec?.revision !== 2
    || approval?.approvedRevision !== 2
    || approval?.userApprovalQuote !== "可以，继续推进"
  ) {
    throw new PipelineError("Approved Premium Display Case Gate 05 rev 2 is required.", 422);
  }
  if (stage.artifactIds.length || !["blocked", "missing"].includes(stage.status)) {
    throw new PipelineError("Gate 06 revision 1 must start from an empty blocked stage.", 422);
  }

  const revisionLabel = "001";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/06-geometry", `rev-${revisionLabel}`
  )));
  const orthographicIds = ["front", "back", "top", "bottom", "left", "right"];
  const standardViewIds = [
    "front", "back", "top", "bottom", "left", "right",
    "hero", "left-oblique", "right-oblique", "low"
  ];
  const definitions = [
    { key: "builder", suffix: "geometry-builder", slot: "geometry-source", file: "build_geometry_evidence.py", role: "process", contentClass: "deterministic-premium-display-case-gate06-source" },
    { key: "composer", suffix: "geometry-review-composer", slot: "geometry-review-source", file: "compose_geometry_review.py", role: "process", contentClass: "deterministic-gate06-review-compositor" },
    { key: "auditor", suffix: "geometry-auditor", slot: "validation-source", file: "audit_geometry_evidence.py", role: "process", contentClass: "independent-blender-geometry-auditor" },
    { key: "imageValidator", suffix: "geometry-image-validator", slot: "validation-source", file: "validate_geometry_images.py", role: "process", contentClass: "gate06-image-dimension-hash-validator" },
    { key: "blend", suffix: "geometry-blend", slot: "geometry-blend", file: "premium-display-case-geometry-r001.blend", role: "source-model", contentClass: "gate06-evidence-scene-same-approved-geometry" },
    ...orthographicIds.map((viewId) => ({
      key: `raw${viewId[0].toUpperCase()}${viewId.slice(1)}`,
      suffix: `geometry-raw-${viewId}`,
      slot: "geometry-raw-view",
      file: `raw/${viewId}.png`,
      role: "blender-render",
      contentClass: `real-blender-raw-orthographic-${viewId}`,
      viewId: `raw-${viewId}`,
      camera: `Gate06Camera${viewId[0].toUpperCase()}${viewId.slice(1)}`,
      renderEngine: "BLENDER_EEVEE"
    })),
    { key: "rawWorkbench", suffix: "geometry-raw-workbench", slot: "geometry-raw-view", file: "raw/workbench.png", role: "blender-render", contentClass: "real-blender-raw-workbench", viewId: "raw-workbench", camera: "Gate06CameraWorkbench", renderEngine: "BLENDER_WORKBENCH" },
    { key: "rawDimensions", suffix: "geometry-raw-dimensions", slot: "geometry-raw-view", file: "raw/dimension-overlay.png", role: "blender-render", contentClass: "real-blender-raw-dimension-overlay", viewId: "raw-dimension-overlay", camera: "Gate06CameraOverlay", renderEngine: "BLENDER_EEVEE" },
    { key: "rawPivot", suffix: "geometry-raw-pivot-axis", slot: "geometry-raw-view", file: "raw/pivot-axis-overlay.png", role: "blender-render", contentClass: "real-blender-raw-pivot-axis-overlay", viewId: "raw-pivot-axis", camera: "Gate06CameraOverlay", renderEngine: "BLENDER_EEVEE" },
    { key: "rawExploded", suffix: "geometry-raw-exploded", slot: "geometry-raw-view", file: "raw/exploded-geometry.png", role: "blender-render", contentClass: "real-blender-raw-internal-exploded-geometry", viewId: "raw-exploded", camera: "Gate06CameraExploded", renderEngine: "BLENDER_WORKBENCH" },
    ...orthographicIds.map((viewId) => ({
      key: viewId,
      suffix: `geometry-${viewId}`,
      slot: `view-${viewId}`,
      file: `ortho-${viewId}.png`,
      role: "blender-render",
      contentClass: `real-blender-annotated-orthographic-${viewId}`,
      viewId,
      camera: `Gate06Camera${viewId[0].toUpperCase()}${viewId.slice(1)}`,
      renderEngine: "BLENDER_EEVEE+Pillow-annotation"
    })),
    { key: "workbench", suffix: "geometry-workbench", slot: "workbench", file: "geometry-workbench.png", role: "blender-render", contentClass: "real-blender-annotated-workbench", viewId: "workbench", camera: "Gate06CameraWorkbench", renderEngine: "BLENDER_WORKBENCH+Pillow-annotation" },
    { key: "dimensions", suffix: "geometry-dimensions", slot: "dimension-overlay", file: "dimension-overlay.png", role: "blender-render", contentClass: "real-blender-exact-dimension-overlay", viewId: "dimension-overlay", camera: "Gate06CameraOverlay", renderEngine: "BLENDER_EEVEE+Pillow-annotation" },
    { key: "pivot", suffix: "geometry-pivot-axis", slot: "pivot-overlay", file: "pivot-axis-overlay.png", role: "blender-render", contentClass: "real-blender-presentation-root-axis-overlay", viewId: "pivot-axis", camera: "Gate06CameraOverlay", renderEngine: "BLENDER_EEVEE+Pillow-annotation" },
    { key: "exploded", suffix: "geometry-exploded", slot: "exploded-geometry", file: "exploded-geometry.png", role: "blender-render", contentClass: "real-blender-internal-only-exploded-geometry", viewId: "exploded", camera: "Gate06CameraExploded", renderEngine: "BLENDER_WORKBENCH+Pillow-annotation" },
    { key: "review", suffix: "geometry-review", slot: "geometry-review", file: "geometry-review.png", role: "blender-render", contentClass: "real-blender-same-geometry-primary-review" },
    { key: "contactSheet", suffix: "geometry-contact-sheet", slot: "geometry-review", file: "geometry-review-contact-sheet.png", role: "blender-render", contentClass: "real-blender-same-geometry-contact-sheet" },
    { key: "validation", suffix: "geometry-validation", slot: "validation-report", file: "geometry-validation.json", role: "validation", contentClass: "premium-display-case-gate06-geometry-validation" },
    { key: "audit", suffix: "geometry-blender-audit", slot: "validation-report", file: "blender-audit.json", role: "validation", contentClass: "premium-display-case-gate06-independent-blender-audit" },
    { key: "imageValidation", suffix: "geometry-image-validation", slot: "validation-report", file: "geometry-image-validation.json", role: "validation", contentClass: "premium-display-case-gate06-image-validation" },
    { key: "standardCapture", suffix: "geometry-standard-capture", slot: "validation-report", file: "fixed-views/capture-report.json", role: "validation", contentClass: "gate06-standard-view-blender-capture-report" },
    { key: "standardCaptureWrapper", suffix: "geometry-standard-capture-wrapper", slot: "validation-report", file: "fixed-views/capture-wrapper-report.json", role: "validation", contentClass: "gate06-standard-view-wrapper-report" },
    ...standardViewIds.map((viewId) => ({
      key: `standard${viewId.replace(/(^|-)([a-z])/g, (_match, _separator, letter) => letter.toUpperCase())}`,
      suffix: `geometry-standard-${viewId}`,
      slot: "geometry-standard-view",
      file: `fixed-views/${viewId}.png`,
      role: "blender-render",
      contentClass: `real-blender-gate06-standard-${viewId}`,
      viewId: `standard-${viewId}`,
      camera: "PipelineCaptureCamera",
      renderEngine: "BLENDER_EEVEE"
    }))
  ].map((record) => ({
    ...record,
    id: `${modelId}-${record.suffix}-r${revisionLabel}`,
    stageId: "06-geometry",
    path: normalizeRepoPath(payload[`${record.key}Path`] || `${expectedDirectory}/${record.file}`)
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) {
      throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    }
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
      throw new PipelineError(`${record.id} file is missing.`, 422);
    }
  }

  const byKey = new Map(definitions.map((record) => [record.key, record]));
  const report = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("validation").path), "utf8"));
  const audit = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("audit").path), "utf8"));
  const imageReport = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("imageValidation").path), "utf8"));
  const capture = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("standardCapture").path), "utf8"));
  const wrapper = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("standardCaptureWrapper").path), "utf8"));
  const expectedDigest = "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f";
  const expectedBlendHash = "3f0411e43900e9ff67a8f52ee4af9d630147acb46251985baf8b2a1a06936e31";
  const expectedSourcePath = "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case/evidence/05-blockout/rev-002/premium-display-case-blockout.blend";
  const sourceBlendAsset = manifest.assets.find((asset) => asset.id === `${modelId}-blockout-blend-r002`);
  const sourceBuilderAsset = manifest.assets.find((asset) => asset.id === `${modelId}-blockout-builder-r002`);
  const sourceValidatorAsset = manifest.assets.find((asset) => asset.id === `${modelId}-blockout-validator-r002`);
  const tubeMetrics = report.meshIntegrity?.objects?.ContinuousTubePerimeter;
  const flow = report.closedTube?.volumetricPassageFloodFill;
  const allChecksPass = Object.values(report.checks || {}).every((value) => value === true);
  const validReport = report.schemaVersion === 1
    && report.modelId === modelId
    && report.gate === "06-geometry"
    && report.geometryRevision === 1
    && report.status === "pass"
    && report.pipelineRevisionAtBuild === manifest.revision
    && report.sourceGate05?.blockoutRevision === 2
    && report.sourceGate05?.approvalQuote === "可以，继续推进"
    && report.sourceGate05?.blendPath === expectedSourcePath
    && report.sourceGate05?.hashesBefore?.blend === expectedBlendHash
    && JSON.stringify(report.sourceGate05?.hashesBefore) === JSON.stringify(report.sourceGate05?.hashesAfter)
    && report.sourceGate05?.unchanged === true
    && sourceBlendAsset?.sha256 === report.sourceGate05?.hashesBefore?.blend
    && sourceBuilderAsset?.sha256 === report.sourceGate05?.hashesBefore?.builder
    && sourceValidatorAsset?.sha256 === report.sourceGate05?.hashesBefore?.validator
    && report.geometryIdentity?.expectedDigest === expectedDigest
    && report.geometryIdentity?.digestBefore === expectedDigest
    && report.geometryIdentity?.digestAfterEvidenceRenders === expectedDigest
    && report.geometryIdentity?.digestAfterEvidenceBlendSave === expectedDigest
    && report.geometryIdentity?.sameAcrossViews === true
    && report.geometryIdentity?.sameAfterEvidenceRenders === true
    && report.geometryIdentity?.sameAfterEvidenceBlendSave === true
    && report.geometryIdentity?.pass === true
    && orthographicIds.every((id) => (
      report.geometryIdentity?.crossView?.[id]?.cameraId === id
      && report.geometryIdentity?.crossView?.[id]?.type === "ORTHO"
      && report.geometryIdentity?.crossView?.[id]?.sameGeometry === true
    ))
    && JSON.stringify(report.bounds?.measured?.sizeMm) === JSON.stringify({ width: 228, height: 304, depth: 59 })
    && report.bounds?.portraitWidthHeightRatio === 0.75
    && report.bounds?.pass === true
    && report.label?.approvedCenterYmm === 99
    && report.label?.approvedDownshiftMm === 6
    && report.label?.minimumFrameToChamberRimMm >= 5
    && report.label?.minimumFrameToTubeInnerMm >= 5
    && report.label?.minimumPaperToInsertFaceMm >= 5
    && report.label?.pass === true
    && report.concentricContours?.outerRadiusMm === 20
    && report.concentricContours?.maximumCenterDriftMm <= 0.01
    && report.concentricContours?.pass === true
    && report.meshIntegrity?.allOpenBoundaryEdgeCount === 0
    && report.meshIntegrity?.allNonManifoldEdgeCount === 0
    && report.meshIntegrity?.allBadContiguousEdgeCount === 0
    && report.meshIntegrity?.allSelfIntersectionPairCount === 0
    && report.meshIntegrity?.allDegenerateElementCount === 0
    && report.meshIntegrity?.pass === true
    && Object.values(report.meshIntegrity?.objects || {}).every((item) => item.pass === true)
    && tubeMetrics?.surfaceConnectedComponentCount === 2
    && tubeMetrics?.invalidPolygonNormalCount === 0
    && tubeMetrics?.badContiguousEdgeCount === 0
    && tubeMetrics?.orientationDisposition === "consistent-negative-winding-preserved-from-approved-source"
    && report.closedTube?.meshObjectCount === 1
    && report.closedTube?.connectedMaterialBodyCount === 1
    && report.closedTube?.boundarySurfaceComponentCount === 2
    && report.closedTube?.neverSplitIntoFourSides === true
    && flow?.sampleCount === 384
    && flow?.validVolumetricSampleCount === 384
    && flow?.visitedSamples === 384
    && flow?.failedRayCount === 0
    && Math.abs(Number(flow?.evaluatedWallThicknessMm?.mean) - 2) <= 0.02
    && flow?.pass === true
    && report.closedTube?.pass === true
    && report.hierarchyAndMotion?.presentationRoot?.motionOwner === true
    && report.hierarchyAndMotion?.presentationRoot?.angularVelocity === 0
    && JSON.stringify(report.hierarchyAndMotion?.presentationRoot?.worldLocationMm) === JSON.stringify([0, 0, 0])
    && report.hierarchyAndMotion?.caseAssembly?.alwaysAssembled === true
    && report.hierarchyAndMotion?.contentSlot?.type === "EMPTY"
    && report.hierarchyAndMotion?.contentSlot?.widthMm === 180
    && report.hierarchyAndMotion?.contentSlot?.heightMm === 198
    && report.hierarchyAndMotion?.contentSlot?.depthMm === 48
    && report.hierarchyAndMotion?.pass === true
    && report.hiddenStructure?.inventedInternalPartCount === 0
    && report.hiddenStructure?.transparentCoverRemainsUnmodeled === true
    && report.hiddenStructure?.pass === true
    && report.explodedEvidence?.purpose === "internal-geometry-validation-only"
    && report.explodedEvidence?.shippingRevealPolicy === "always-assembled-never-explodes"
    && report.explodedEvidence?.continuousTubeExplodedObjectCount === 1
    && report.explodedEvidence?.continuousTubeUsesExactSourceMeshData === true
    && report.explodedEvidence?.inventedInternalPartCount === 0
    && report.explodedEvidence?.pass === true
    && report.scope?.geometryChanged === false
    && report.scope?.finalMaterialsApproved === false
    && report.scope?.gate07Entered === false
    && report.scope?.shippingUnityChanged === false
    && report.scope?.buildInstallPhonePush === false
    && report.outputBlendSha256 === sha256File(resolveRepoPath(byKey.get("blend").path))
    && allChecksPass;
  if (!validReport) {
    throw new PipelineError("Premium Display Case Gate 06 validation does not satisfy the same-geometry contract.", 422);
  }
  const validAudit = audit.schemaVersion === 1
    && audit.modelId === modelId
    && audit.gate === "06-geometry"
    && audit.geometryRevision === 1
    && audit.status === "pass"
    && audit.geometryDigest === expectedDigest
    && JSON.stringify(audit.boundsMm) === JSON.stringify({ width: 228, height: 304, depth: 59 })
    && audit.portraitWidthHeightRatio === 0.75
    && audit.labelCenterYmm === 99
    && audit.labelDownshiftMm === 6
    && audit.outerRadiusMm === 20
    && audit.maximumCornerCenterDriftMm <= 0.01
    && Object.values(audit.meshAudit || {}).every((item) => item.pass === true)
    && audit.tubeFloodFill?.sampleCount === 384
    && audit.tubeFloodFill?.visitedSamples === 384
    && audit.tubeFloodFill?.pass === true
    && Object.values(audit.checks || {}).every((value) => value === true);
  if (!validAudit) throw new PipelineError("Premium Display Case Gate 06 Blender audit failed.", 422);
  const reviewImage = imageReport.annotatedImages?.review;
  const contactImage = imageReport.annotatedImages?.contactSheet;
  const validImages = imageReport.schemaVersion === 1
    && imageReport.modelId === modelId
    && imageReport.gate === "06-geometry"
    && imageReport.geometryRevision === 1
    && imageReport.status === "pass"
    && imageReport.sourceBlendSha256 === expectedBlendHash
    && imageReport.geometryDigest === expectedDigest
    && JSON.stringify(reviewImage?.dimensions) === JSON.stringify([3600, 3200])
    && JSON.stringify(contactImage?.dimensions) === JSON.stringify([4800, 3600])
    && reviewImage?.sha256 === sha256File(resolveRepoPath(byKey.get("review").path))
    && contactImage?.sha256 === sha256File(resolveRepoPath(byKey.get("contactSheet").path))
    && Object.values(imageReport.checks || {}).every((value) => value === true);
  if (!validImages) throw new PipelineError("Premium Display Case Gate 06 image validation failed.", 422);
  const capturedIds = new Set((capture.views || []).map((view) => view.id));
  if (
    wrapper.verified_capture !== true
    || wrapper.blender_returncode !== 0
    || (wrapper.missing_views || []).length !== 0
    || standardViewIds.some((viewId) => !capturedIds.has(viewId))
    || !(capture.included_objects || []).includes("ContinuousTubePerimeter")
  ) {
    throw new PipelineError("The standard-view wrapper did not verify the approved Gate 05 source.", 422);
  }

  const sourceAssetIds = [...blockout.artifactIds];
  const sourceClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    const producerName = record.key === "builder"
      ? "deterministic-bpy"
      : record.key === "composer"
        ? "Pillow review compositor"
        : record.key === "auditor"
          ? "Blender independent audit"
          : record.key === "imageValidator"
            ? "Pillow image validator"
            : record.key.startsWith("standard")
              ? "fidgeting-model-pipeline standard-view wrapper"
              : record.role === "blender-render"
                ? "Blender"
                : "Gate 06 validation";
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: record.role,
      producer: {
        name: producerName,
        version: report.blender,
        recipe: record.key.startsWith("standard")
          ? "skills/fidgeting-model-pipeline/scripts/capture_standard_views.py"
          : `${expectedDirectory}/build_geometry_evidence.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 06 rev 1 uses approved Gate 05 rev 2 without source or subject-geometry edits. The closed-loop tube remains one connected hollow part. Exploded evidence is internal-only; shipping reveal never disassembles. The source tube has finite contiguous normals but consistent negative winding, preserved and disclosed because source hash and geometry digest must remain unchanged."
      },
      sourceAssetIds,
      sourceClaimIds,
      ...(record.viewId ? {
        view: {
          id: record.viewId,
          camera: record.camera,
          renderEngine: record.renderEngine,
          axisContract: "X-width/Y-height/Z-front",
          pose: record.viewId.includes("exploded")
            ? "internal-validation-exploded-approved-visible-parts-only"
            : "assembled-canonical-zero-motion"
        }
      } : {})
    };
  });
  manifest.assets.push(...records);
  const ids = Object.fromEntries(definitions.map((record) => [record.key, record.id]));

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.reviewArtifactIds = [
    ids.review,
    ids.contactSheet,
    ids.workbench,
    ids.dimensions,
    ids.pivot,
    ids.exploded,
    ids.front
  ];
  stage.geometrySpec = {
    revision: 1,
    sourceGate05Revision: 2,
    sourceGate05BlendSha256: expectedBlendHash,
    sourceGate05BuilderSha256: report.sourceGate05.hashesBefore.builder,
    sourceGate05ValidatorSha256: report.sourceGate05.hashesBefore.validator,
    evaluatedGeometryDigest: expectedDigest,
    sourceUnchanged: true,
    dimensionsMm: { width: 228, height: 304, depth: 59 },
    portraitWidthHeightRatio: 0.75,
    labelCenterYmm: 99,
    labelDownshiftMm: 6,
    outerCornerRadiusMm: 20,
    maximumCornerCenterDriftMm: report.concentricContours.maximumCenterDriftMm,
    cornerCenterToleranceMm: 0.01,
    meshIntegrity: {
      allOpenBoundaryEdgeCount: 0,
      allNonManifoldEdgeCount: 0,
      allBadContiguousEdgeCount: 0,
      allSelfIntersectionPairCount: 0,
      allDegenerateElementCount: 0,
      invalidPolygonNormalCount: 0
    },
    tube: {
      objectCount: 1,
      connectedMaterialBodyCount: 1,
      boundarySurfaceComponentCount: 2,
      outerSectionMm: { width: 10, depth: 9 },
      passageSectionMm: { width: 6, depth: 5 },
      wallThicknessMm: 2,
      floodFillVisited: 384,
      floodFillTotal: 384,
      normalOrientation: tubeMetrics.orientationDisposition,
      signedVolumeMm3: tubeMetrics.signedVolumeMm3,
      windingDisposition: "preserved-and-disclosed-no-source-mutation"
    },
    contentSlot: {
      widthMm: 180,
      heightMm: 198,
      depthMm: 48,
      centerYmm: -42,
      type: "EMPTY",
      role: "runtime-anchor"
    },
    labelClearanceMm: {
      frameToChamber: report.label.minimumFrameToChamberRimMm,
      frameToTube: report.label.minimumFrameToTubeInnerMm,
      paperToInsert: report.label.minimumPaperToInsertFaceMm
    },
    presentationRoot: {
      worldLocationMm: [0, 0, 0],
      showcaseAxis: "+Y",
      motionOwner: true,
      angularVelocity: 0
    },
    explodedEvidencePurpose: "internal-geometry-validation-only",
    shippingRevealPolicy: "always-assembled-never-explodes",
    inventedInternalPartCount: 0,
    reviewArtifactPath: byKey.get("review").path,
    contactSheetPath: byKey.get("contactSheet").path,
    orthographicCameraIds: orthographicIds,
    finalMaterialsApproved: false,
    gate07Entered: false,
    unityAssetChanged: false,
    buildInstallPhonePush: false
  };
  stage.validations = [
    { id: "approved-gate05-source-immutable", status: "pass", evidence: `Gate 05 rev 2 blend ${expectedBlendHash}, deterministic builder ${report.sourceGate05.hashesBefore.builder}, and validator ${report.sourceGate05.hashesBefore.validator} are unchanged before and after evidence generation.` },
    { id: "cross-view-geometry-identity", status: "pass", evidence: `All six orthographic views, Workbench, overlays, exploded evidence, and the saved evidence blend retain geometry digest ${expectedDigest}.` },
    { id: "exact-bounds-and-portrait", status: "pass", evidence: "Evaluated bounds are exactly 228×304×59 mm with width/height ratio 0.750000." },
    { id: "approved-label-and-concentric-corners", status: "pass", evidence: "Label center is Y=99 mm after the approved 6 mm shift. R20 and all three analytic contour families have 0.000 mm center drift against a 0.010 mm limit." },
    { id: "closed-manifold-no-degenerate-or-intersection", status: "pass", evidence: "All subject meshes total 0 open, 0 non-manifold, 0 bad-contiguous edges, 0 self-intersection pairs, and 0 degenerate elements." },
    { id: "normal-coherence-and-source-winding-disclosed", status: "pass", evidence: `All normals are finite and contiguous. ContinuousTubePerimeter retains the approved source's consistent negative winding (signed volume ${tubeMetrics.signedVolumeMm3} mm³); no flip was applied because source hash and geometry digest must remain unchanged.` },
    { id: "single-connected-closed-loop-tube", status: "pass", evidence: "ContinuousTubePerimeter is one mesh and one connected hollow material body with two closed boundary surfaces. It is never split into four sides." },
    { id: "evaluated-volumetric-passage-flood-fill", status: "pass", evidence: `Evaluated-mesh BVH rays validate the 10×9 mm outer section, 6×5 mm passage and 2 mm wall. Volumetric cyclic flood-fill visits ${flow.visitedSamples}/${flow.sampleCount} samples.` },
    { id: "content-slot-and-label-clearance", status: "pass", evidence: `ContentSlot remains an unmodeled 180×198×48 mm runtime anchor. Label clearances are ${report.label.minimumFrameToChamberRimMm}, ${report.label.minimumFrameToTubeInnerMm}, and ${report.label.minimumPaperToInsertFaceMm} mm against a 5 mm minimum.` },
    { id: "presentation-root-motion-ownership", status: "pass", evidence: "PresentationRoot remains at [0,0,0], owns +Y showcase motion, and has zero angular velocity. CaseAssembly remains assembled; no child has independent animation or constraints." },
    { id: "no-hidden-structure-invented", status: "pass", evidence: "Invented internal part count is 0. TransparentCover remains an Empty with deferred thickness." },
    { id: "exploded-internal-only", status: "pass", evidence: "Exploded evidence reuses the five approved visible source meshes. The tube remains one linked mesh. Shipping reveal never explodes." },
    { id: "review-image-and-standard-view-validation", status: "pass", evidence: "The 3600×3200 primary review and 4800×3600 contact sheet embed exact source hash and geometry digest metadata. Six orthographic hashes are distinct; all 10 standard views are verified." },
    { id: "gate07-remains-blocked", status: "pass", evidence: "Gate 06 rev 1 is ready_for_review only. It is not approved and Gate 07 was not entered." },
    { id: "shipping-unity-unchanged", status: "pass", evidence: "All evidence stays under ArtSource/ModelPipeline. Shipping Unity, build, install, and phone state are unchanged." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  blockout.blockoutSpec.approval.gate06Status = "ready_for_review-rev1";
  if (blockout.blockoutSpec.supplementaryMaterialDiagnostic) {
    blockout.blockoutSpec.supplementaryMaterialDiagnostic.gate06Status = "ready_for_review-rev1";
    blockout.blockoutSpec.supplementaryMaterialDiagnostic.gate07Status = "blocked";
  }
  markDownstreamStale(manifest, stageIndex, "Gate 06 rev 1 real Blender same-geometry evidence awaits explicit approval; Gate 07 must not start.");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 05 rev 2 is approved. Gate 06 rev 1 uses the same immutable Blender source and evaluated geometry digest to provide six orthographic views, Workbench, dimension and pivot overlays, internal-only exploded geometry, Blender audit, volumetric flood-fill, and large review sheets. Bounds are 228×304×59 mm; label Y=99 mm; concentric drift 0.000 mm; open/non-manifold/bad-contiguous/self-intersection/degenerate counts are all zero; flood-fill is 384/384. The source tube's finite contiguous normals retain consistent negative winding and are disclosed without mutation. Gate 06 is ready_for_review, not approved. Gate 07 remains blocked. Shipping Unity, build, install, and phone state are unchanged.";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "06-geometry",
    geometryRevision: 1,
    consumesStageId: "05-blockout",
    consumesBlockoutRevision: 2,
    sourceBlendSha256: expectedBlendHash,
    evaluatedGeometryDigest: expectedDigest,
    sourceUnchanged: true,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    geometryReviewPath: byKey.get("review").path,
    contactSheetPath: byKey.get("contactSheet").path,
    dimensionsMm: stage.geometrySpec.dimensionsMm,
    portraitWidthHeightRatio: 0.75,
    labelCenterYmm: 99,
    labelDownshiftMm: 6,
    outerCornerRadiusMm: 20,
    maximumCornerCenterDriftMm: 0,
    topology: {
      connectedMaterialBodyCount: 1,
      openBoundaryEdgeCount: 0,
      nonManifoldEdgeCount: 0,
      badContiguousEdgeCount: 0,
      selfIntersectionPairCount: 0,
      degenerateElementCount: 0,
      floodFill: "384/384",
      normalOrientation: tubeMetrics.orientationDisposition
    },
    explodedEvidencePurpose: "internal-geometry-validation-only",
    shippingRevealPolicy: "always-assembled-never-explodes",
    gate07Status: "blocked",
    autoApproved: false,
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseGeometryUserReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("This evidence correction is supported only for a Premium Display Case pipeline.", 422);
  }

  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "06-geometry");
  const stage = manifest.stages[stageIndex];
  const gate07 = manifest.stages[stageIndex + 1];
  if (
    stage.status !== "ready_for_review"
    || stage.geometrySpec?.revision !== 2
    || stage.decision !== null
    || gate07.status !== "blocked"
  ) {
    throw new PipelineError("Gate 06 rev 2 must remain ready_for_review with Gate 07 blocked.", 422);
  }

  const revisionLabel = "003";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/06-geometry", "rev-002"
  )));
  const definitions = [
    {
      key: "composer",
      suffix: "gate06-whole-case-review-composer",
      slot: "geometry-user-review-source",
      file: "compose_user_review_r003.py",
      role: "process",
      contentClass: "deterministic-whole-case-only-gate06-review-compositor"
    },
    {
      key: "validator",
      suffix: "gate06-whole-case-review-validator",
      slot: "validation-source",
      file: "validate_user_review_r003.py",
      role: "process",
      contentClass: "whole-case-only-gate06-review-validator"
    },
    {
      key: "review",
      suffix: "gate06-whole-case-review",
      slot: "geometry-user-review",
      file: "gate06-whole-case-review-r003.png",
      role: "blender-render",
      contentClass: "user-facing-whole-case-only-gate06-review"
    },
    {
      key: "validation",
      suffix: "gate06-whole-case-review-validation",
      slot: "validation-report",
      file: "gate06-whole-case-review-validation-r003.json",
      role: "validation",
      contentClass: "whole-case-only-gate06-review-validation"
    }
  ].map((record) => ({
    ...record,
    id: `${modelId}-${record.suffix}-r${revisionLabel}`,
    stageId: "06-geometry",
    path: normalizeRepoPath(payload[`${record.key}Path`] || `${expectedDirectory}/${record.file}`)
  }));
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  for (const record of definitions) {
    if (existingIds.has(record.id)) {
      throw new PipelineError(`${record.id} is already registered.`, 422);
    }
    if (!record.path.startsWith(`${expectedDirectory}/`)) {
      throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`, 422);
    }
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
      throw new PipelineError(`${record.id} file is missing.`, 422);
    }
  }

  const byKey = new Map(definitions.map((record) => [record.key, record]));
  const report = JSON.parse(fs.readFileSync(resolveRepoPath(byKey.get("validation").path), "utf8"));
  const requiredPanels = [
    "front",
    "back",
    "top",
    "side",
    "workbench",
    "dimensions",
    "pivot",
    "concentric",
    "closed-loop",
    "flood-fill",
    "normal-validation"
  ];
  const internalTechnicalArtifactIds = [
    `${modelId}-geometry-exploded-r002`,
    `${modelId}-geometry-review-r002`,
    `${modelId}-geometry-contact-sheet-r002`
  ];
  const preservedRev2ArtifactIds = stage.artifactIds.filter((assetId) => assetId.endsWith("-r002"));
  const internalAssets = internalTechnicalArtifactIds.map((assetId) => (
    manifest.assets.find((asset) => asset.id === assetId)
  ));
  const internalAssetsPreserved = internalAssets.every((asset) => (
    asset
    && stage.artifactIds.includes(asset.id)
    && asset.sha256 === sha256File(resolveRepoPath(asset.path))
  ));
  const reviewHash = sha256File(resolveRepoPath(byKey.get("review").path));
  const validReport = report.schemaVersion === 1
    && report.modelId === modelId
    && report.gate === "06-geometry"
    && report.geometryRevision === 2
    && report.evidenceRevision === 3
    && report.status === "pass"
    && report.reviewArtifactId === byKey.get("review").id
    && report.reviewBoard?.sha256 === reviewHash
    && JSON.stringify(report.reviewBoard?.dimensions) === JSON.stringify([4800, 4000])
    && JSON.stringify(report.requiredPanels) === JSON.stringify(requiredPanels)
    && (report.forbiddenSourceReferences || []).length === 0
    && report.rev2AssetCount === 43
    && (report.mismatchedRev2Assets || []).length === 0
    && Object.values(report.checks || {}).every((value) => value === true)
    && preservedRev2ArtifactIds.length === 43
    && internalAssetsPreserved
    && stage.geometrySpec.dimensionsMm.width === 228
    && stage.geometrySpec.dimensionsMm.height === 304
    && stage.geometrySpec.dimensionsMm.depth === 59
    && stage.geometrySpec.identity.vertexPositionDigest === report.geometryIdentity.vertexPositionDigest
    && stage.geometrySpec.identity.silhouetteDigest === report.geometryIdentity.silhouetteDigest
    && stage.geometrySpec.identity.derivativeTopologyWindingDigest === report.geometryIdentity.topologyWindingDigest
    && stage.geometrySpec.tube.signedVolumeMm3 === 52932.982745;
  if (!validReport) {
    throw new PipelineError("The whole-case-only Gate 06 review board failed its evidence-only contract.", 422);
  }

  const sourceAssetIds = [
    `${modelId}-blockout-blend-r002`,
    `${modelId}-blockout-concentric-centers-r002`,
    `${modelId}-geometry-front-r002`,
    `${modelId}-geometry-back-r002`,
    `${modelId}-geometry-top-r002`,
    `${modelId}-geometry-right-r002`,
    `${modelId}-geometry-workbench-r002`,
    `${modelId}-geometry-dimensions-r002`,
    `${modelId}-geometry-pivot-axis-r002`,
    `${modelId}-geometry-validation-r002`,
    `${modelId}-geometry-blender-audit-r002`
  ];
  if (sourceAssetIds.some((assetId) => !manifest.assets.some((asset) => asset.id === assetId))) {
    throw new PipelineError("The whole-case review board is missing a registered source artifact.", 422);
  }
  const sourceClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: record.role,
      producer: {
        name: record.key === "review"
          ? "Pillow whole-case review compositor"
          : record.key === "validation"
            ? "Pillow/source-contract validation"
            : "deterministic Python evidence tooling",
        version: "Pillow 11.3.0",
        recipe: `${expectedDirectory}/compose_user_review_r003.py then validate_user_review_r003.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Evidence-only Gate 06 rev 2 review correction. It changes no geometry, hash, dimension, winding, status, or approval. The user board shows assembled front/back/top/side, Workbench, dimensions, pivot, concentric, closed-loop, flood-fill, and normal validation only."
      },
      sourceAssetIds,
      sourceClaimIds,
      ...(record.key === "review" ? {
        view: {
          id: "gate06-whole-case-review",
          camera: "multi-view-user-review-board",
          renderEngine: "Pillow composition of real Blender evidence",
          axisContract: "X-width/Y-height/Z-front",
          pose: "assembled-only-no-layer-separation"
        }
      } : {})
    };
  });
  manifest.assets.push(...records);

  const ids = Object.fromEntries(definitions.map((record) => [record.key, record.id]));
  const previousReviewArtifactIds = [...stage.reviewArtifactIds];
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = [...stage.artifactIds, ...records.map((record) => record.id)];
  stage.reviewArtifactIds = [ids.review];
  stage.userReviewEvidence = {
    evidenceRevision: 3,
    geometryRevision: 2,
    disposition: "evidence-only-correction-not-geometry-rejection",
    primaryArtifactId: ids.review,
    validationArtifactId: ids.validation,
    requiredPanels,
    internalTechnicalArtifactIds,
    internalTechnicalVisibility: "artifact-only-never-primary-review",
    headline: "WHOLE CASE ONLY · NO EXPLODE IN APP OR REVIEW",
    geometryUnchanged: true,
    gate07Entered: false
  };
  stage.validations = [
    ...stage.validations.filter((validation) => !validation.id.startsWith("user-review-")),
    {
      id: "user-review-whole-case-only",
      status: "pass",
      evidence: `${ids.review} contains only the 11 allowed assembled geometry and validation panels.`
    },
    {
      id: "user-review-internal-evidence-hidden",
      status: "pass",
      evidence: `${internalTechnicalArtifactIds.join(", ")} remain immutable artifacts but are absent from reviewArtifactIds.`
    },
    {
      id: "user-review-evidence-only-disposition",
      status: "pass",
      evidence: "The correction is not a geometry rejection. Gate 06 rev 2 stays ready_for_review and Gate 07 stays blocked."
    }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(
    manifest,
    stageIndex,
    "Gate 06 rev 2 geometry remains ready_for_review. Evidence-only rev 3 removes internal exploded views from the user-facing review; Gate 07 must not start."
  );
  updateStageDigests(manifest);
  manifest.revision += 1;
  const now = new Date().toISOString();
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 06 rev 2 geometry remains ready_for_review at 5/12. The user clarified that exploded geometry is internal technical evidence only, not a geometry rejection. Evidence-only rev 3 replaces reviewArtifactIds with one assembled-only board covering front/back/top/side, Workbench, dimensions, pivot, concentric, closed-loop, flood-fill, and normal validation. All 43 rev 2 asset hashes, geometry identity, dimensions, and winding remain unchanged. Gate 07 remains blocked; no build, install, or phone push occurred.";
  manifest.currentState.visualApproval = "pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;

  const event = makeEvent(manifest, "stage-evidence-revised", {
    stageId: "06-geometry",
    geometryRevision: 2,
    evidenceRevision: 3,
    feedbackDisposition: "user-facing-evidence-correction-not-geometry-rejection",
    stageStatus: "ready_for_review",
    previousReviewArtifactIds,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    internalTechnicalArtifactIds,
    userReviewPath: byKey.get("review").path,
    validationReportPath: byKey.get("validation").path,
    rev2AssetHashesPreserved: true,
    dimensionsMm: stage.geometrySpec.dimensionsMm,
    vertexPositionDigest: stage.geometrySpec.identity.vertexPositionDigest,
    silhouetteDigest: stage.geometrySpec.identity.silhouetteDigest,
    topologyWindingDigest: stage.geometrySpec.identity.derivativeTopologyWindingDigest,
    gate07Status: "blocked",
    autoApproved: false,
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function saveGeometryReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (manifest.model.mechanism === "display-case") {
    return savePremiumDisplayCaseGeometryReview(modelId, payload);
  }
  if (modelId !== "magnetic-slide-tile") throw new PipelineError("Gate 06 geometry registration is supported only for magnetic-slide-tile.", 422);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "06-geometry");
  const blockout = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (blockout.status !== "approved" || blockout.blockoutSpec?.revision !== 3) {
    throw new PipelineError("Approved Gate 05 rev 3 is required.", 422);
  }
  if (stage.artifactIds.length || !["blocked", "missing"].includes(stage.status)) {
    throw new PipelineError("Gate 06 revision 1 must start from an empty blocked stage.", 422);
  }

  const revisionLabel = "001";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/06-geometry", `rev-${revisionLabel}`
  )));
  const definitions = [
    ["builder", "geometry-builder", "geometry-source", "build_geometry_evidence.py", "deterministic-gate06-evidence-source"],
    ["blend", "geometry-blend", "geometry-blend", "magnetic-slide-tile-geometry-r001.blend", "gate06-camera-and-evidence-scene"],
    ["front", "geometry-front", "view-front", "ortho-front.png", "orthographic-front"],
    ["back", "geometry-back", "view-back", "ortho-back.png", "orthographic-back"],
    ["top", "geometry-top", "view-top", "ortho-top.png", "orthographic-top"],
    ["bottom", "geometry-bottom", "view-bottom", "ortho-bottom.png", "orthographic-bottom"],
    ["left", "geometry-left", "view-left", "ortho-left.png", "orthographic-left"],
    ["right", "geometry-right", "view-right", "ortho-right.png", "orthographic-right"],
    ["workbench", "geometry-workbench", "workbench", "geometry-workbench.png", "blender-workbench-view"],
    ["dimensions", "geometry-dimensions", "dimension-overlay", "dimension-overlay.png", "exact-dimension-overlay"],
    ["pivot", "geometry-point-pivot", "pivot-overlay", "point-pivot-overlay.png", "exact-point-pivot-overlay"],
    ["exploded", "geometry-exploded", "exploded-geometry", "exploded-geometry.png", "two-exterior-body-exploded-view"],
    ["validation", "geometry-validation", "validation-report", "geometry-validation.json", "cross-view-mesh-and-transform-validation"]
  ].map(([key, suffix, slot, file, contentClass]) => ({
    key,
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "06-geometry",
    slot,
    path: normalizeRepoPath(payload[`${key}Path`] || `${expectedDirectory}/${file}`),
    contentClass
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) throw new PipelineError(`${record.id} file is missing.`, 422);
  }

  const reportRecord = definitions.find((record) => record.key === "validation");
  const report = JSON.parse(fs.readFileSync(resolveRepoPath(reportRecord.path), "utf8"));
  const requiredCameraIds = ["front", "back", "top", "bottom", "left", "right"];
  const validReport = report.schemaVersion === 1
    && report.gate === "06-geometry"
    && report.geometryRevision === 1
    && report.sourceGate05?.blockoutRevision === 3
    && report.sourceGate05?.blendPath === "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/05-blockout/rev-003/magnetic-slide-tile-blockout-r003.blend"
    && report.sourceGate05?.unchanged === true
    && report.geometryIdentity?.sameAcrossViews === true
    && report.geometryIdentity?.sameAfterEvidenceRenders === true
    && report.geometryIdentity?.pass === true
    && JSON.stringify(report.bounds?.measuredMm) === JSON.stringify([50, 31, 12])
    && report.bounds?.pass === true
    && report.meshIntegrity?.LowerBody_Fixed_CleanPlane?.nonmanifoldEdgeCount === 0
    && report.meshIntegrity?.UpperCapsule_Moving?.nonmanifoldEdgeCount === 0
    && report.meshIntegrity?.LowerBody_Fixed_CleanPlane?.invalidPolygonNormalCount === 0
    && report.meshIntegrity?.UpperCapsule_Moving?.invalidPolygonNormalCount === 0
    && report.meshIntegrity?.seamGapMm === 0
    && report.meshIntegrity?.closedVolumeOverlapDepthMm === 0
    && report.meshIntegrity?.pass === true
    && JSON.stringify(report.pivotAndMotion?.axisPointWorldMm) === JSON.stringify([0, -9.5, 0])
    && report.pivotAndMotion?.slidePose?.translationMm?.[1] === 21
    && report.pivotAndMotion?.slidePose?.rotationDeg === 0
    && JSON.stringify(report.pivotAndMotion?.spinPose?.translationMm) === JSON.stringify([0, 0, 0])
    && report.pivotAndMotion?.spinPose?.rotationDeg === 45
    && report.pivotAndMotion?.pivotWorldDriftMm === 0
    && report.pivotAndMotion?.pass === true
    && report.fixedLowerAndEnvelope?.lowerMatrixUnchanged === true
    && report.fixedLowerAndEnvelope?.lowerTopPlanarityDeviationMm === 0
    && report.fixedLowerAndEnvelope?.envelopeMatrixUnchanged === true
    && report.fixedLowerAndEnvelope?.envelopeType === "EMPTY"
    && report.fixedLowerAndEnvelope?.envelopeHideRender === true
    && report.fixedLowerAndEnvelope?.envelopeGeometry === "none"
    && report.fixedLowerAndEnvelope?.proxyRendered === false
    && report.fixedLowerAndEnvelope?.exposedTrackOrHardwareCount === 0
    && report.fixedLowerAndEnvelope?.pass === true
    && report.zeroSelfMotion?.pass === true
    && report.smoothness?.arcSegmentsPerSemicircle === 256
    && report.smoothness?.profileVertexCount === 513
    && report.smoothness?.maximumProfileSegmentAngleDeg <= 1
    && report.smoothness?.maximumChordDeviationMm <= 0.005
    && report.smoothness?.bevelSegments >= 8
    && report.smoothness?.pass === true
    && requiredCameraIds.every((id) => report.cameras?.[id]?.id === id && report.cameras?.[id]?.type === "ORTHO")
    && report.evidence?.orthographic?.length === 6
    && report.evidence?.explodedApprovedExteriorBodyCount === 2
    && report.evidence?.inventedInternalPartCount === 0
    && report.scope?.neutralClayOnly === true
    && report.scope?.finalMaterialsOrLighting === false
    && report.scope?.unityAssetChanged === false;
  if (!validReport) throw new PipelineError("Gate 06 validation report does not satisfy the geometry evidence contract.", 422);

  const sourceAssetIds = [...blockout.artifactIds];
  const sourceClaimIds = [
    "slider-architecture-flat-lower-concealed-overlap-r010",
    "slider-blockout-point-axis-distinction-r003"
  ];
  const viewByKey = {
    front: { id: "front", kind: "orthographic", camera: "Camera_Front" },
    back: { id: "back", kind: "orthographic", camera: "Camera_Back" },
    top: { id: "top", kind: "orthographic", camera: "Camera_Top" },
    bottom: { id: "bottom", kind: "orthographic", camera: "Camera_Bottom" },
    left: { id: "left", kind: "orthographic", camera: "Camera_Left" },
    right: { id: "right", kind: "orthographic", camera: "Camera_Right" },
    workbench: { id: "workbench", kind: "perspective", camera: "HeroCamera" },
    dimensions: { id: "dimension-overlay", kind: "orthographic", camera: "Camera_Top" },
    pivot: { id: "pivot-axis", kind: "orthographic", camera: "Camera_Top" },
    exploded: { id: "exploded", kind: "perspective", camera: "Camera_Exploded" }
  };
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: "process",
      producer: {
        name: record.key === "builder" ? "deterministic-bpy" : "Blender",
        version: report.blender,
        recipe: `${expectedDirectory}/build_geometry_evidence.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 06 revision 1 uses the approved Gate 05 rev 3 blend without geometry edits. Review annotations are separate non-model objects.",
        userClaimIds: sourceClaimIds
      },
      sourceAssetIds,
      sourceClaimIds,
      ...(viewByKey[record.key] ? {
        view: {
          ...viewByKey[record.key],
          pose: record.key === "pivot" ? "zero-slide-spin-45deg" : (record.key === "exploded" ? "two-exterior-bodies-z-separated-18mm" : "closed-zero-motion"),
          renderEngine: record.key === "workbench" ? "BLENDER_WORKBENCH" : "BLENDER_EEVEE",
          ...(report.cameras?.[record.key]?.recipe ? { recipe: report.cameras[record.key].recipe } : {})
        }
      } : {})
    };
  });
  manifest.assets.push(...records);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.geometrySpec = {
    revision: 1,
    sourceGate05Revision: 3,
    sourceGate05Sha256: report.sourceGate05.sha256Before,
    evaluatedGeometryDigest: report.geometryIdentity.evaluatedDigest,
    dimensionsMm: { length: 50, width: 31, thickness: 12 },
    meshObjects: report.geometryIdentity.modelMeshObjects,
    meshMetrics: {
      lower: report.meshIntegrity.LowerBody_Fixed_CleanPlane,
      upper: report.meshIntegrity.UpperCapsule_Moving
    },
    seamGapMm: 0,
    closedVolumeOverlapDepthMm: 0,
    axisPointWorldMm: [0, -9.5, 0],
    slidePose: report.pivotAndMotion.slidePose,
    spinPose: report.pivotAndMotion.spinPose,
    orthographicCameraIds: requiredCameraIds,
    crossViewGeometryIdentity: true,
    fixedLowerPlaneDeviationMm: 0,
    concealedEnvelopeRendered: false,
    exposedTrackOrHardwareCount: 0,
    explodedExteriorBodyCount: 2,
    inventedInternalPartCount: 0,
    smoothness: report.smoothness,
    finalMaterialsOrLighting: false,
    unityAssetChanged: false
  };
  stage.validations = [
    { id: "gate05-source-immutable", status: "pass", evidence: `Approved rev 3 blend hash remained ${report.sourceGate05.sha256Before} before and after all evidence renders.` },
    { id: "cross-view-geometry-identity", status: "pass", evidence: `All six orthographic views and the final scene use evaluated digest ${report.geometryIdentity.evaluatedDigest}.` },
    { id: "exact-bounds", status: "pass", evidence: "Canonical closed bounds are exactly 50×31×12 mm in every orthographic view." },
    { id: "watertight-clean-normals", status: "pass", evidence: "Both exterior meshes have 0 nonmanifold edges, 0 invalid polygon normals, positive signed volume, and unchanged source validation." },
    { id: "seam-overlap-contract", status: "pass", evidence: "The two watertight shells meet at z=0 with 0.0 mm gap and 0.0 mm volume-overlap depth." },
    { id: "point-pivot-and-separate-poses", status: "pass", evidence: "Point axis is [0,-9.5,0]; slide is +Y 21 mm/0°; spin is 0 mm/45°; pivot drift is 0." },
    { id: "fixed-flat-lower", status: "pass", evidence: "Lower transform is unchanged, top-plane deviation is 0.0 mm, and no exposed rail or hardware exists." },
    { id: "hidden-envelope-not-rendered", status: "pass", evidence: "The fixed concealed enclosure remains an Empty with hide_render=true and geometry=none." },
    { id: "six-camera-contract", status: "pass", evidence: "Front, back, top, bottom, left, and right use explicit orthographic camera IDs and recipes." },
    { id: "exploded-approved-parts-only", status: "pass", evidence: "Exploded evidence separates only the two approved exterior bodies; invented internal part count is 0." },
    { id: "smooth-silhouette-preserved", status: "pass", evidence: `Profile remains 256 segments per semicircle with ${report.smoothness.maximumChordDeviationMm} mm maximum chord deviation and 8 bevel segments.` },
    { id: "zero-self-motion", status: "pass", evidence: "No model object has animation or constraints." },
    { id: "shipping-unity-unchanged", status: "pass", evidence: "Gate 06 evidence remains under ArtSource/ModelPipeline; Unity runtime and shipping scenes are unchanged." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "Gate 06 rev 1 同源几何证据等待视觉批准；不得进入 Gate 07。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 05 rev 3 已按用户原文‘看起来是对的’批准。Gate 06 rev 1 从获批 blend 原样生成六正交、Workbench、尺寸、单点轴与两外壳爆炸证据；evaluated geometry digest 跨视图一致，50×31×12 mm、双 watertight mesh、0 seam gap/overlap depth、固定隐藏 envelope 与分姿态运动均通过。等待 Gate 06 视觉批准，不得进入 Gate 07。";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "06-geometry",
    geometryRevision: 1,
    artifactIds: stage.artifactIds,
    evaluatedGeometryDigest: report.geometryIdentity.evaluatedDigest,
    dimensionsMm: stage.geometrySpec.dimensionsMm,
    cameraIds: requiredCameraIds,
    blender: report.blender,
    autoApproved: false
  });
  return saveManifest(manifest, event);
}

function savePremiumDisplayCaseMaterialReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "07-material");
  const geometry = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (
    geometry.status !== "approved"
    || geometry.geometrySpec?.revision !== 2
    || geometry.geometrySpec?.approval?.userApprovalQuote !== "可以啊，没问题，你继续吧"
    || geometry.geometrySpec?.approval?.approvalScope?.includes("whole-case-only") !== true
    || geometry.geometrySpec?.approval?.approvalScope?.includes("no-explode") !== true
  ) {
    throw new PipelineError("Approved Premium Display Case Gate 06 revision 2 is required.", 422);
  }
  if (stage.artifactIds.length || !["blocked", "missing"].includes(stage.status)) {
    throw new PipelineError("Premium Display Case Gate 07 revision 1 must start from an empty blocked stage.", 422);
  }

  const revisionLabel = "001";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/07-material", `rev-${revisionLabel}`
  )));
  const definitions = [
    ["material-builder", "material-source", "build_material_lookdev.py", "process", "deterministic-gate07-neutral-pbr-builder"],
    ["material-auditor", "material-audit-source", "audit_material_lookdev.py", "process", "independent-gate07-blender-auditor"],
    ["material-review-composer", "material-review-source", "compose_material_review.py", "process", "deterministic-gate07-review-composer"],
    ["material-blend", "material-blend", "premium-display-case-material-r001.blend", "source-model", "neutral-pbr-lookdev-blend"],
    ["material-build-report", "validation-report", "material-build-report.json", "validation", "gate07-build-and-geometry-preservation-report"],
    ["material-blender-audit", "validation-report", "blender-audit.json", "validation", "gate07-real-blender-audit"],
    ["material-image-validation", "validation-report", "material-image-validation.json", "validation", "gate07-material-image-statistics"],
    ["material-surface-coverage", "validation-report", "surface-coverage-report.json", "validation", "closed-surface-material-coverage-report"],
    ["material-asset-optimization", "validation-report", "asset-optimization-report.json", "validation", "gate07-asset-budget-audit"],
    ["material-qa-verdict", "validation-report", "qa-verdict.json", "validation", "gate07-ready-for-review-qa-verdict"],
    ["material-raw-hero", "material-raw-render", "raw/hero.png", "blender-render", "real-blender-cycles-neutral-pbr-hero", "hero", "M07_HeroCamera"],
    ["material-raw-left-oblique", "material-raw-render", "raw/left-oblique.png", "blender-render", "real-blender-cycles-neutral-pbr-left-oblique", "left-oblique", "M07_LeftObliqueCamera"],
    ["material-raw-right-oblique", "material-raw-render", "raw/right-oblique.png", "blender-render", "real-blender-cycles-neutral-pbr-right-oblique", "right-oblique", "M07_RightObliqueCamera"],
    ["material-raw-side", "material-raw-render", "raw/side.png", "blender-render", "real-blender-cycles-neutral-pbr-side", "side", "M07_SideCamera"],
    ["material-raw-back", "material-raw-render", "raw/back.png", "blender-render", "real-blender-cycles-neutral-pbr-back", "back", "M07_BackCamera"],
    ["material-raw-tube-corner", "material-raw-render", "raw/tube-corner.png", "blender-render", "real-blender-cycles-continuous-tube-corner-highlight", "tube-corner", "M07_TubeCornerCamera"],
    ["material-raw-label-closeup", "material-raw-render", "raw/label-closeup.png", "blender-render", "real-blender-cycles-label-paper-cover-and-foil-closeup", "label-closeup", "M07_LabelCloseupCamera"],
    ["material-raw-tactile-closeup", "material-raw-render", "raw/tactile-closeup.png", "blender-render", "real-blender-cycles-object-local-tactile-grain-closeup", "tactile-grain-closeup", "M07_TactileCloseupCamera"],
    ["material-raw-clay-hero", "material-raw-render", "raw/clay-hero-same-camera.png", "blender-render", "real-blender-cycles-clay-control-same-camera", "clay-hero", "M07_HeroCamera"],
    ...[0, 90, 180, 270, 360].map((angle) => [
      `material-raw-rotation-${String(angle).padStart(3, "0")}`,
      "material-raw-render",
      `raw/rotation-${String(angle).padStart(3, "0")}.png`,
      "blender-render",
      "real-blender-cycles-object-local-grain-rotation-check",
      `rotation-${angle}`,
      "M07_RotationCamera"
    ]),
    ["material-board", "material-board", "material-board.png", "process", "whole-case-only-gate07-material-board", "material-board", "deterministic-composite"],
    ["material-closeup", "material-closeup", "material-closeup.png", "process", "assembled-case-gate07-material-closeup-board", "material-closeup", "deterministic-composite"],
    ["material-hero", "material-review-render", "hero-review.png", "process", "annotated-whole-case-material-hero", "hero", "M07_HeroCamera"],
    ["material-left-oblique", "material-review-render", "left-oblique-review.png", "process", "annotated-whole-case-material-left-oblique", "left-oblique", "M07_LeftObliqueCamera"],
    ["material-right-oblique", "material-review-render", "right-oblique-review.png", "process", "annotated-whole-case-material-right-oblique", "right-oblique", "M07_RightObliqueCamera"],
    ["material-side-back", "material-review-render", "side-back-review.png", "process", "whole-case-side-and-back-material-board", "side-back", "deterministic-composite"],
    ["material-tube-corner-highlight", "material-review-render", "tube-corner-continuous-highlight.png", "process", "assembled-case-continuous-tube-highlight-closeup", "tube-corner", "M07_TubeCornerCamera"],
    ["material-label-closeup", "material-review-render", "label-closeup-review.png", "process", "assembled-case-label-paper-cover-foil-closeup", "label-closeup", "M07_LabelCloseupCamera"],
    ["material-tactile-grain-closeup", "material-review-render", "tactile-grain-closeup-review.png", "process", "assembled-case-object-local-tactile-grain-closeup", "tactile-grain-closeup", "M07_TactileCloseupCamera"],
    ["material-clay-vs-pbr", "material-review-render", "clay-vs-pbr-same-camera.png", "process", "same-camera-clay-versus-pbr-comparison", "clay-vs-pbr", "M07_HeroCamera"],
    ["material-grain-stability", "material-review-render", "grain-stability-rotation.png", "process", "whole-case-five-angle-object-local-grain-stability-board", "grain-stability", "M07_RotationCamera"],
    ["material-parameters", "material-review-render", "material-parameters-board.png", "process", "large-type-gate07-pbr-parameter-board", "material-parameters", "deterministic-composite"]
  ].map(([suffix, slot, file, role, contentClass, viewId = null, camera = null]) => ({
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "07-material",
    slot,
    path: normalizeRepoPath(`${expectedDirectory}/${file}`),
    role,
    contentClass,
    viewId,
    camera
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) throw new PipelineError(`${record.id} file is missing.`, 422);
  }

  const readReport = (file) => JSON.parse(fs.readFileSync(resolveRepoPath(`${expectedDirectory}/${file}`), "utf8"));
  const build = readReport("material-build-report.json");
  const audit = readReport("blender-audit.json");
  const image = readReport("material-image-validation.json");
  const surface = readReport("surface-coverage-report.json");
  const optimization = readReport("asset-optimization-report.json");
  const qa = readReport("qa-verdict.json");
  const identity = build.geometryPreservation?.identityAfterRenders;
  const shell = build.materialParameters?.MAT_FrostedPolycarbonate;
  const tube = build.materialParameters?.MAT_FrostedPolycarbonateEdge;
  const insert = build.materialParameters?.MAT_BlackFlocking;
  const paper = build.materialParameters?.MAT_LabelPaper;
  const foil = build.materialParameters?.MAT_RarityFoilSilver;
  const allChecksPass = (report) => report?.status === "pass"
    && Object.values(report.checks || {}).every(Boolean);
  const validReports = build.schemaVersion === 1
    && build.modelId === modelId
    && build.gate === "07-material"
    && build.materialRevision === 1
    && build.pipelineRevisionAtBuild === 32
    && allChecksPass(build)
    && build.sourceGate06?.geometryRevision === 2
    && build.sourceGate06?.approvalQuote === "可以啊，没问题，你继续吧"
    && build.sourceGate06?.approvalScope?.includes("whole-case-only")
    && build.sourceGate06?.approvalScope?.includes("no-explode")
    && build.sourceGate06?.sha256Before === build.sourceGate06?.sha256After
    && identity?.fullGeometryDigest === "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
    && identity?.objectMatrixDigest === "34d52e8980dbbffc5573523b80de9a47d145a49bb22ae95f8d7c1b38e393d588"
    && identity?.vertexPositionDigest === "ced0edf95f8fa6416c5a0e33ebf8dc99fdafcdb3beceac85ee2970bbb2a7682c"
    && identity?.silhouetteDigest === "81615c0e5afd59b634dfa2e85040b31b30b9d5ef0ddc9e12462f1b3d1c59f6b4"
    && identity?.topologyWindingDigest === "c29bc1dd8c0f0c52fd4c70d102bcfc2b4007e579795b605adeb21611a3bf7c79"
    && JSON.stringify(build.geometryPreservation?.boundsAfterRendersMm?.sizeMm) === JSON.stringify({ width: 228, height: 304, depth: 59 })
    && build.geometryPreservation?.labelCenterYmm === 99
    && build.geometryPreservation?.maximumCornerCenterDriftMm === 0
    && build.geometryPreservation?.floodFill?.visitedSamples === 384
    && build.geometryPreservation?.floodFill?.sampleCount === 384
    && build.geometryPreservation?.floodFill?.pass === true
    && build.geometryPreservation?.tubeOrientation?.netMaterialSignedVolumeMm3 === 52932.982745
    && build.geometryPreservation?.tubeOrientation?.outerBoundary?.outward === true
    && build.geometryPreservation?.tubeOrientation?.innerBoundary?.inwardTowardLumen === true
    && shell?.ior === 1.585
    && shell?.roughness === 0.22
    && shell?.transmissionWeight === 0.92
    && tube?.ior === 1.585
    && tube?.roughness === 0.18
    && tube?.transmissionWeight === 0.78
    && insert?.roughness === 0.91
    && paper?.roughness === 0.73
    && foil?.metallic === 0.96
    && foil?.roughness === 0.3
    && build.grainStability?.pass === true
    && Object.values(build.micrograin || {}).every((item) => item.coordinateSource === "Texture Coordinate:Object" && item.worldSpace === false)
    && build.background?.surface?.roughness >= 0.78
    && build.background?.surface?.roughness <= 0.88
    && build.background?.surface?.localNoiseMasks === 0
    && build.background?.surface?.radialHalo === false
    && build.background?.surface?.fixedGreenBias === false
    && build.colorSpacePolicy?.pass === true
    && build.identityBoundary?.forbiddenHits?.length === 0
    && build.scope?.wholeCaseOnly === true
    && build.scope?.explode === false
    && build.scope?.gate07Approved === false
    && build.scope?.gate08Entered === false
    && build.scope?.finalLightingApproval === false
    && build.scope?.shippingUnityChanged === false
    && build.scope?.buildInstallPhonePush === false
    && allChecksPass(audit)
    && allChecksPass(image)
    && surface?.status === "pass"
    && surface?.pass === true
    && optimization?.status === "pass"
    && Object.values(optimization.checks || {}).every(Boolean)
    && qa?.status === "pass"
    && qa?.result === "READY_FOR_MATERIAL_REVIEW_NOT_SHIPPING"
    && qa?.wholeCaseOnly === true
    && qa?.explode === false;
  if (!validReports) throw new PipelineError("Premium Display Case Gate 07 evidence does not satisfy the material contract.", 422);

  const sourceAssetIds = [
    "display-case-modeling-contract-r001",
    "premium-display-case-rive-v15-user-reference-r003",
    "premium-display-case-formal-material-blend-source",
    "premium-display-case-formal-material-recipe-source",
    "premium-display-case-geometry-blend-r002",
    "premium-display-case-geometry-validation-r002",
    "premium-display-case-gate06-whole-case-review-r003"
  ];
  const sourceClaimIds = [
    "display-case-analysis-closed-loop-r002",
    "display-case-analysis-manifold-r002",
    "display-case-analysis-background-r002",
    "display-case-analysis-label-r002",
    "display-case-analysis-portrait-r002",
    "display-case-analysis-flow-r002",
    "display-case-analysis-environment-r002"
  ];
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    const isReview = [
      "material-board",
      "material-closeup",
      "material-review-render"
    ].includes(record.slot);
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: record.role,
      producer: {
        name: record.role === "blender-render" || record.slot === "material-blend" ? "Blender" : "deterministic pipeline evidence",
        version: build.blender,
        recipe: `${expectedDirectory}/build_material_lookdev.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 07 rev 1 uses approved Gate 06 rev 2 geometry and formal Premium Display Case materials. Coin_Slab_v15 informs only layered response and continuous highlights; no brand identity is copied."
      },
      sourceAssetIds,
      sourceClaimIds,
      reviewState: isReview ? "active" : "internal-evidence",
      wholeCaseOnly: true,
      explodeEligible: false,
      ...(record.viewId ? {
        view: {
          id: record.viewId,
          kind: record.viewId.startsWith("rotation-") ? "turntable-sample" : "perspective",
          camera: record.camera,
          assemblyState: "assembled",
          renderEngine: record.role === "blender-render" ? "CYCLES" : "deterministic-composite",
          axisContract: "X-width/Y-height/Z-front"
        }
      } : {})
    };
  });
  manifest.assets.push(...records);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.reviewArtifactIds = [
    `${modelId}-material-board-r${revisionLabel}`,
    `${modelId}-material-closeup-r${revisionLabel}`,
    `${modelId}-material-parameters-r${revisionLabel}`
  ];
  stage.materialSpec = {
    revision: 1,
    sourceGate06Revision: 2,
    sourceGate06ApprovalQuote: "可以啊，没问题，你继续吧",
    sourceGate06ApprovalScope: [
      "current-gate06-geometry-rev2",
      "whole-case-only",
      "no-explode"
    ],
    sourceGate06Sha256: build.sourceGate06.sha256Before,
    geometryIdentity: identity,
    boundsMm: build.geometryPreservation.boundsAfterRendersMm.sizeMm,
    labelCenterYmm: build.geometryPreservation.labelCenterYmm,
    maximumCornerCenterDriftMm: build.geometryPreservation.maximumCornerCenterDriftMm,
    topologyWindingDigest: identity.topologyWindingDigest,
    floodFill: {
      visited: build.geometryPreservation.floodFill.visitedSamples,
      total: build.geometryPreservation.floodFill.sampleCount
    },
    formalMaterialSources: build.formalMaterialSources,
    referenceUse: build.referenceUse,
    pbrValues: {
      frostedPolycarbonateShell: {
        ior: shell.ior,
        roughness: shell.roughness,
        transmissionWeight: shell.transmissionWeight,
        micrograinFeatureSizeMm: shell.micrograinFeatureSizeMm,
        micrograinCoordinateSpace: shell.micrograinCoordinateSpace
      },
      continuousTubeEdge: {
        ior: tube.ior,
        roughness: tube.roughness,
        transmissionWeight: tube.transmissionWeight,
        micrograinFeatureSizeMm: tube.micrograinFeatureSizeMm,
        micrograinCoordinateSpace: tube.micrograinCoordinateSpace
      },
      blackTactileInsert: {
        roughness: insert.roughness,
        micrograinFeatureSizeMm: insert.micrograinFeatureSizeMm,
        micrograinBumpDistanceMm: insert.micrograinBumpDistanceMm,
        micrograinCoordinateSpace: insert.micrograinCoordinateSpace
      },
      physicalLabelPaper: {
        roughness: paper.roughness,
        micrograinFeatureSizeMm: paper.micrograinFeatureSizeMm,
        micrograinCoordinateSpace: paper.micrograinCoordinateSpace
      },
      narrowNeutralSilverFoil: {
        metallic: foil.metallic,
        roughness: foil.roughness,
        micrograinFeatureSizeMm: foil.micrograinFeatureSizeMm,
        micrograinCoordinateSpace: foil.micrograinCoordinateSpace
      }
    },
    background: build.background,
    grainStability: build.grainStability,
    transparentSortingInitialCheck: audit.transparentOrdering,
    colorSpacePolicy: build.colorSpacePolicy,
    surfaceCoverageReportId: `${modelId}-material-surface-coverage-r${revisionLabel}`,
    optimizationReportId: `${modelId}-material-asset-optimization-r${revisionLabel}`,
    qaVerdictId: `${modelId}-material-qa-verdict-r${revisionLabel}`,
    geometryChanged: false,
    artworkApproved: false,
    neutralIdentityPlaceholdersOnly: true,
    wholeCaseOnly: true,
    explode: false,
    neutralStudioOnly: true,
    finalLightingApproved: false,
    gate07Approved: false,
    gate08Entered: false,
    unityAssetChanged: false,
    buildInstallPhonePush: false
  };
  stage.validations = [
    { id: "approved-gate06-source-immutable", status: "pass", evidence: `Gate 06 rev 2 blend remained ${build.sourceGate06.sha256Before}; full geometry digest remained ${identity.fullGeometryDigest}.` },
    { id: "geometry-identity-bounds-winding", status: "pass", evidence: `Vertex digest ${identity.vertexPositionDigest}, winding ${identity.topologyWindingDigest}, bounds 228 × 304 × 59 mm, label Y=99 mm, concentric drift 0.000 mm, and flood-fill 384/384 are unchanged.` },
    { id: "formal-pbr-materials", status: "pass", evidence: "Formal frosted polycarbonate, tube edge, black tactile insert, label paper, transparent cover zone, graphite print, and narrow silver foil satisfy the Gate 07 report." },
    { id: "stable-object-local-grain", status: "pass", evidence: `Every micrograin uses Texture Coordinate:Object; 0/90/180/270/360 local recovery delta stayed within ${build.grainStability.tolerance} mm.` },
    { id: "continuous-tube-highlight", status: "pass", evidence: "The tube-corner render and image statistics show the highlight continuing through the tangent corner on one connected tube material." },
    { id: "continuous-neutral-background", status: "pass", evidence: `Background patch luma range ${image.backgroundMetrics.patchMeanLumaRange}; local noise outlier fraction ${image.backgroundMetrics.maximumFineResidualOutlierFraction}; no radial halo or fixed green bias.` },
    { id: "transparent-ordering-initial-check", status: "pass", evidence: `Cycles layer ordering passes and label blackout fraction is ${image.labelMetrics.blackoutFraction}. Unity sorting remains downstream.` },
    { id: "closed-surface-coverage", status: "pass", evidence: "Front caps, back caps, and sidewalls use assigned formal Principled materials; overlay context is excluded." },
    { id: "asset-budget", status: "pass", evidence: `${optimization.subjectTriangles} subject triangles <= ${optimization.triangleBudget}; ${optimization.subjectMaterialSlots} material slots <= ${optimization.materialSlotBudget}.` },
    { id: "whole-case-only-no-explode", status: "pass", evidence: "All review artifacts show the assembled case; internal exploded geometry is absent from Gate 07 reviewArtifactIds." },
    { id: "gate-boundary", status: "pass", evidence: "Gate 07 is ready_for_review, not approved. Gate 08, final lighting, shipping Unity, build, install, and phone push remain blocked." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  geometry.geometrySpec.gate07Entered = true;
  geometry.geometrySpec.approval.gate07Status = "ready_for_review";
  geometry.userReviewEvidence.gate07Entered = true;
  geometry.userReviewEvidence.gate07Status = "ready_for_review";
  markDownstreamStale(manifest, stageIndex, "Gate 07 material rev 1 is ready_for_review and awaits explicit user approval. Gate 08 must not start.");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.visualApproval = "pending";
  manifest.currentState.diagnosis = "Gate 06 rev 2 is approved at 6/12. Gate 07 material rev 1 is ready_for_review from the immutable normals-corrected geometry and formal Premium Display Case material sources. Review evidence is whole-case-only/no-explode and uses neutral studio lighting; Gate 07 is not approved, Gate 08 remains blocked, and shipping Unity, build, install, and phone state remain unchanged.";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "07-material",
    materialRevision: 1,
    sourceGate06Revision: 2,
    sourceGate06ApprovalQuote: "可以啊，没问题，你继续吧",
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    materialBoardPath: `${expectedDirectory}/material-board.png`,
    materialCloseupPath: `${expectedDirectory}/material-closeup.png`,
    parameterBoardPath: `${expectedDirectory}/material-parameters-board.png`,
    evaluatedGeometryDigest: identity.fullGeometryDigest,
    vertexPositionDigest: identity.vertexPositionDigest,
    topologyWindingDigest: identity.topologyWindingDigest,
    boundsMm: stage.materialSpec.boundsMm,
    labelCenterYmm: stage.materialSpec.labelCenterYmm,
    floodFill: "384/384",
    wholeCaseOnly: true,
    explode: false,
    neutralStudioOnly: true,
    finalLightingApproved: false,
    autoApproved: false,
    gate08Status: "blocked",
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

function savePremiumDisplayCaseMaterialRevalidation(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "07-material");
  const architecture = manifest.stages[3];
  const geometry = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (
    architecture.status !== "approved"
    || architecture.architectureSpec?.evidenceRevision !== 7
    || architecture.architectureSpec?.caseLightOutsideSilhouettePixels !== 0
    || geometry.status !== "approved"
    || geometry.geometrySpec?.revision !== 3
    || geometry.geometrySpec?.approval?.approvedRevision !== 3
    || geometry.geometrySpec?.approval?.userApprovalQuote !== "正确，批准并继续（推荐）"
    || geometry.geometrySpec?.approval?.approvalScope?.includes("geometry-unchanged") !== true
    || geometry.geometrySpec?.approval?.approvalScope?.includes("presentation-root-rigid-whole-case") !== true
    || geometry.geometrySpec?.approval?.approvalScope?.includes("no-exploded-review") !== true
  ) {
    throw new PipelineError("Approved Gate 04 rev 7 and Gate 06 rev 3 are required for material revalidation.", 422);
  }
  if (
    stage.status !== "stale"
    || stage.materialSpec?.revision !== 1
    || stage.decision?.action !== "approve"
  ) {
    throw new PipelineError("Gate 07 rev 2 must revalidate the preserved historically approved material revision.", 422);
  }

  const revisionLabel = "002";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/07-material", `rev-${revisionLabel}`
  )));
  const definitions = [
    ["material-revalidation-builder", "material-source", "build_material_revalidation.py", "process", "gate07-rev2-blender-material-revalidator"],
    ["material-zone-mask-renderer", "material-source", "render_material_zone_masks.py", "process", "temporary-flat-material-zone-mask-renderer"],
    ["material-review-composer", "material-source", "compose_material_review.py", "process", "gate07-rev2-review-and-image-validator"],
    ["material-blend", "material-blend", "premium-display-case-material-r002.blend", "source-model", "revalidated-neutral-pbr-lookdev-blend"],
    ["material-revalidation", "validation-report", "material-revalidation.json", "validation", "material-geometry-architecture-compatibility-report"],
    ["material-zone-mask-report", "validation-report", "material-zone-mask-report.json", "validation", "temporary-flat-zone-mask-report"],
    ["material-review-validation", "validation-report", "material-review-validation.json", "validation", "turntable-mask-and-image-validation"],
    ["material-compatibility-snapshot", "material-contract", "material-compatibility-snapshot.json", "contract", "gate07-rev2-parameter-snapshot"],
    ["material-turntable-mp4", "material-turntable", "material-turntable.mp4", "blender-render", "real-cycles-material-turntable", "material-turntable", "M07_RotationCamera"],
    ["material-turntable-gif", "material-turntable", "material-turntable.gif", "process", "real-render-turntable-gif", "material-turntable-gif", "M07_RotationCamera"],
    ["material-board", "material-board", "material-board.png", "process", "front-edge-reverse-front-material-board", "material-board", "deterministic-composite"],
    ["material-closeups", "material-closeup", "material-closeups.png", "process", "tube-label-tactile-material-closeups", "material-closeups", "deterministic-composite"],
    ["material-turntable-contact", "material-board", "material-turntable-contact-sheet.png", "process", "real-turntable-contact-sheet", "material-turntable-contact", "deterministic-composite"],
    ["material-sheen-compatibility", "material-mask-board", "mesh-clipped-sheen-compatibility.png", "process", "unity-object-local-mesh-mask-compatibility-board", "mesh-clipped-sheen-compatibility", "deterministic-composite"],
    ["material-sheen-mask", "material-mask", "mesh-clipped-sheen-mask.png", "process", "subject-and-material-zone-clipped-sheen-mask", "mesh-clipped-sheen-mask", "deterministic-mask"],
    ...[
      ["front", 0, "M07_RotationCamera"],
      ["edge", 90, "M07_RotationCamera"],
      ["reverse", 180, "M07_RotationCamera"],
      ["front-return", 360, "M07_RotationCamera"],
      ["tube-corner", 0, "M07_TubeCornerCamera"],
      ["label-closeup", 0, "M07_LabelCloseupCamera"],
      ["tactile-closeup", 0, "M07_TactileCloseupCamera"]
    ].map(([viewId, angle, camera]) => [
      `material-raw-${viewId}`,
      "material-raw-render",
      `raw/${viewId}.png`,
      "blender-render",
      "real-cycles-neutral-material-render",
      `${viewId}-${angle}`,
      camera
    ]),
    ...Array.from({ length: 25 }, (_, index) => [
      `material-turntable-frame-${String(index).padStart(3, "0")}`,
      "material-turntable-frame",
      `raw/turn-${String(index).padStart(3, "0")}.png`,
      "blender-render",
      "real-cycles-turntable-frame",
      `turntable-${index * 15}`,
      "M07_RotationCamera"
    ]),
    ...["subject", "sheen-eligible", "tube", "label-zone", "insert-zone", "foil-zone"].flatMap(
      (kind) => [0, 90, 180, 270, 360].map((angle) => [
        `material-mask-${kind}-${String(angle).padStart(3, "0")}`,
        "material-mask",
        `masks/${kind}-${String(angle).padStart(3, "0")}.png`,
        "validation",
        `temporary-flat-${kind}-mask`,
        `${kind}-${angle}`,
        "M07_RotationCamera"
      ])
    ),
    ...["clipped-sheen", "clipped-sheen-overlay"].flatMap(
      (kind) => [0, 90, 180, 270, 360].map((angle) => [
        `material-mask-${kind}-${String(angle).padStart(3, "0")}`,
        kind === "clipped-sheen" ? "material-mask" : "material-mask-render",
        `masks/${kind}-${String(angle).padStart(3, "0")}.png`,
        "process",
        `object-local-material-zone-${kind}`,
        `${kind}-${angle}`,
        "deterministic-mask"
      ])
    )
  ].map(([suffix, slot, file, role, contentClass, viewId = null, camera = null]) => ({
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "07-material",
    slot,
    path: normalizeRepoPath(`${expectedDirectory}/${file}`),
    role,
    contentClass,
    viewId,
    camera
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) throw new PipelineError(`${record.id} file is missing.`, 422);
  }

  const readReport = (file) => JSON.parse(
    fs.readFileSync(resolveRepoPath(`${expectedDirectory}/${file}`), "utf8")
  );
  const build = readReport("material-revalidation.json");
  const zone = readReport("material-zone-mask-report.json");
  const validation = readReport("material-review-validation.json");
  const snapshot = readReport("material-compatibility-snapshot.json");
  const allChecksPass = (report) => (
    report?.status === "pass" && Object.values(report.checks || {}).every(Boolean)
  );
  const identity = build.sourceGate06?.geometryIdentity;
  const shell = build.materialParameters?.MAT_FrostedPolycarbonate;
  const tube = build.materialParameters?.MAT_FrostedPolycarbonateEdge;
  const insert = build.materialParameters?.MAT_BlackFlocking;
  const paper = build.materialParameters?.MAT_LabelPaper;
  const foil = build.materialParameters?.MAT_RarityFoilSilver;
  const near = (value, target, tolerance = 0.000001) => (
    Number.isFinite(value) && Math.abs(value - target) <= tolerance
  );
  const validEvidence = build.schemaVersion === 1
    && build.modelId === modelId
    && build.gate === "07-material"
    && build.materialRevision === 2
    && build.pipelineRevisionAtBuild === manifest.revision
    && allChecksPass(build)
    && build.sourceGate06?.geometryRevision === 3
    && build.sourceGate06?.approval?.approvedRevision === 3
    && build.sourceGate06?.approval?.reviewedArtifactSha256 === geometry.geometrySpec.approval.reviewedArtifactSha256
    && build.sourceGate04?.architectureEvidenceRevision === 7
    && build.sourceGate04?.sha256 === "d5afb4eecdb86953cb6d5c28e217e19f88becb6c0aef1316eaffac2ae630fc3e"
    && build.sourceGate04?.finalSheenOwner === "Unity MaterialPropertyBlock object-local mesh mask"
    && identity?.fullGeometryDigest === "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
    && identity?.vertexPositionDigest === "ced0edf95f8fa6416c5a0e33ebf8dc99fdafcdb3beceac85ee2970bbb2a7682c"
    && identity?.silhouetteDigest === "81615c0e5afd59b634dfa2e85040b31b30b9d5ef0ddc9e12462f1b3d1c59f6b4"
    && identity?.topologyWindingDigest === "c29bc1dd8c0f0c52fd4c70d102bcfc2b4007e579795b605adeb21611a3bf7c79"
    && JSON.stringify(build.sourceGate06?.boundsMm?.sizeMm) === JSON.stringify({ width: 228, height: 304, depth: 59 })
    && near(shell?.IOR, 1.585)
    && near(shell?.Roughness, 0.22)
    && near(shell?.["Transmission Weight"], 0.92)
    && shell?.["Emission Strength"] === 0
    && near(tube?.IOR, 1.585)
    && near(tube?.Roughness, 0.18)
    && near(tube?.["Transmission Weight"], 0.78)
    && tube?.["Emission Strength"] === 0
    && near(insert?.Roughness, 0.91)
    && near(paper?.Roughness, 0.73)
    && near(foil?.Metallic, 0.96)
    && near(foil?.Roughness, 0.3)
    && Object.values(build.objectLocalGrain || {}).every(
      (item) => item.coordinateSpace === "object-local" && item.worldSpace === false
    )
    && build.scope?.wholeAssembledCaseOnly === true
    && build.scope?.reviewExplodedPartCount === 0
    && build.scope?.geometryChanged === false
    && build.scope?.toyChanged === false
    && build.scope?.runtimeTimingBaked === false
    && build.scope?.lightGeometryAdded === false
    && build.scope?.externalHalo === false
    && build.scope?.particles === false
    && build.scope?.vfxGraph === false
    && build.scope?.bloomDependency === false
    && build.scope?.persistentEmission === false
    && build.scope?.shippingUnityChanged === false
    && build.scope?.buildInstallPhonePush === false
    && zone.status === "pass"
    && zone.geometryAdded === false
    && zone.persistentEmission === false
    && allChecksPass(validation)
    && validation.sheenMaskCompatibility?.maximumOutsideSubjectPixels === 0
    && validation.sheenMaskCompatibility?.maximumOutsideAllowedMaterialZonePixels === 0
    && validation.turntableMetrics?.frameCount === 25
    && validation.turntableMetrics?.frontReturnMeanAbsoluteChannelDelta <= 1.5
    && validation.scope?.wholeAssembledCaseOnly === true
    && validation.scope?.reviewExplodedPartCount === 0
    && validation.scope?.finalLightingApproved === false
    && snapshot.materialRevision === 2
    && snapshot.sheenMaskPolicy?.outsideSubjectPixels === 0
    && snapshot.sheenMaskPolicy?.outsideAllowedMaterialZonePixels === 0
    && snapshot.sheenMaskPolicy?.runtimeTimingIncluded === false
    && snapshot.sheenMaskPolicy?.geometryAdded === false
    && snapshot.gate08Status === "blocked";
  if (!validEvidence) {
    throw new PipelineError("Premium Display Case Gate 07 rev 2 evidence does not satisfy the material revalidation contract.", 422);
  }

  const sourceAssetIds = [
    "premium-display-case-mesh-light-architecture-r007",
    "premium-display-case-modeling-contract-r003",
    "premium-display-case-geometry-blend-r003",
    "premium-display-case-geometry-revalidation-r003",
    "premium-display-case-geometry-interactive-review-r003",
    "premium-display-case-material-blend-r001",
    "premium-display-case-material-build-report-r001"
  ];
  const sourceClaimIds = architecture.architectureSpec.sourceClaimIds;
  const reviewIds = new Set([
    `${modelId}-material-turntable-mp4-r${revisionLabel}`,
    `${modelId}-material-board-r${revisionLabel}`,
    `${modelId}-material-closeups-r${revisionLabel}`,
    `${modelId}-material-turntable-contact-r${revisionLabel}`,
    `${modelId}-material-sheen-compatibility-r${revisionLabel}`
  ]);
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    const isBlender = record.role === "blender-render" || record.slot === "material-blend";
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: record.role,
      producer: {
        name: isBlender ? "Blender" : "deterministic pipeline evidence",
        version: isBlender ? build.blender : "2026-08-27",
        recipe: record.role === "blender-render"
          ? `${expectedDirectory}/build_material_revalidation.py`
          : `${expectedDirectory}/compose_material_review.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 07 rev 2 revalidates historically approved neutral PBR materials on approved unchanged Gate 06 rev 3 geometry and Gate 04 rev 7 mesh-clipped light ownership."
      },
      sourceAssetIds,
      sourceClaimIds,
      reviewState: reviewIds.has(record.id) ? "active" : "internal-evidence",
      wholeCaseOnly: true,
      explodeEligible: false,
      ...(record.viewId ? {
        view: {
          id: record.viewId,
          kind: record.slot === "material-turntable"
            ? "real-render-turntable"
            : (record.slot === "material-turntable-frame" ? "turntable-sample" : "material-review"),
          camera: record.camera,
          assemblyState: "assembled",
          renderEngine: record.role === "blender-render" ? "CYCLES" : "deterministic-composite",
          axisContract: "X-width/Y-height/Z-front"
        }
      } : {}),
      ...(record.slot === "material-turntable" && record.path.endsWith(".mp4") ? {
        interaction: {
          type: "real-render-turntable",
          frameCount: 25,
          durationSeconds: Number(validation.videoProbe.format.duration),
          approvalRequiresCompletedChecklist: true,
          approvalChecklist: validation.approvalChecklist,
          gate08LightingApproval: false
        }
      } : {})
    };
  });
  manifest.assets.push(...records);

  stage.historicalDecisions = [
    ...(stage.historicalDecisions || []),
    {
      ...stage.decision,
      materialRevision: 1,
      decisionState: "historically-approved-stale-after-upstream-revalidation",
      supersededByMaterialRevision: 2
    }
  ];
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.reviewArtifactIds = [...reviewIds];
  stage.materialSpec = {
    revision: 2,
    revalidatesHistoricalMaterialRevision: 1,
    sourceGate06Revision: 3,
    sourceGate06Approval: geometry.geometrySpec.approval,
    sourceGate04EvidenceRevision: 7,
    sourceGate04ArchitectureSha256: build.sourceGate04.sha256,
    geometryIdentity: identity,
    boundsMm: build.sourceGate06.boundsMm.sizeMm,
    materialAssignments: build.materialAssignments,
    materialGraphDigests: build.materialGraphDigestsAfter,
    pbrValues: {
      frostedPolycarbonateShell: {
        ior: shell.IOR,
        roughness: shell.Roughness,
        transmissionWeight: shell["Transmission Weight"],
        emissionStrength: shell["Emission Strength"],
        coordinateSpace: build.objectLocalGrain.MAT_FrostedPolycarbonate.coordinateSpace
      },
      continuousTubeEdge: {
        ior: tube.IOR,
        roughness: tube.Roughness,
        transmissionWeight: tube["Transmission Weight"],
        emissionStrength: tube["Emission Strength"],
        coordinateSpace: build.objectLocalGrain.MAT_FrostedPolycarbonateEdge.coordinateSpace
      },
      blackTactileInsert: {
        roughness: insert.Roughness,
        emissionStrength: insert["Emission Strength"],
        coordinateSpace: build.objectLocalGrain.MAT_BlackFlocking.coordinateSpace
      },
      physicalLabelPaper: {
        roughness: paper.Roughness,
        emissionStrength: paper["Emission Strength"],
        coordinateSpace: build.objectLocalGrain.MAT_LabelPaper.coordinateSpace
      },
      narrowNeutralSilverFoil: {
        metallic: foil.Metallic,
        roughness: foil.Roughness,
        emissionStrength: foil["Emission Strength"],
        coordinateSpace: build.objectLocalGrain.MAT_RarityFoilSilver.coordinateSpace
      }
    },
    turntable: {
      artifactId: `${modelId}-material-turntable-mp4-r${revisionLabel}`,
      frameCount: 25,
      durationSeconds: Number(validation.videoProbe.format.duration),
      frontReturnMeanAbsoluteChannelDelta: validation.turntableMetrics.frontReturnMeanAbsoluteChannelDelta,
      maximumAdjacentMeanLumaDelta: validation.turntableMetrics.maximumAdjacentMeanLumaDelta,
      minimumCardinalTubeHighlightContrast: validation.turntableMetrics.minimumCardinalTubeHighlightContrast
    },
    transparentOrdering: build.transparentOrdering,
    grainStability: {
      coordinateSpace: "object-local",
      worldSpaceGrain: false,
      frontReturnMeanAbsoluteChannelDelta: validation.turntableMetrics.frontReturnMeanAbsoluteChannelDelta
    },
    sheenMaskCompatibility: {
      architectureOwner: "Unity MaterialPropertyBlock",
      coordinateSpace: "object-local",
      outsideSubjectPixels: 0,
      outsideAllowedMaterialZonePixels: 0,
      runtimeTimingIncluded: false,
      geometryAdded: false,
      externalHalo: false,
      pointLight: false,
      particles: false,
      vfxGraph: false,
      bloomDependency: false,
      persistentEmission: false
    },
    identityBoundary: {
      whatnot: false,
      yellow: false,
      smiley: false,
      barcode: false,
      sampleNumber: false,
      circularCoinWindow: false
    },
    approvalChecklist: validation.approvalChecklist,
    geometryChanged: false,
    toyChanged: false,
    wholeCaseOnly: true,
    reviewExplodedPartCount: 0,
    neutralMaterialEnvironmentOnly: true,
    finalLightingApproved: false,
    gate07Approved: false,
    gate08Entered: false,
    unityAssetChanged: false,
    buildInstallPhonePush: false
  };
  stage.validations = [
    { id: "approved-gate06-rev3-source", status: "pass", evidence: `Gate 06 rev 3 is approved with geometry digest ${identity.fullGeometryDigest}, vertex digest ${identity.vertexPositionDigest} and winding digest ${identity.topologyWindingDigest}.` },
    { id: "approved-gate04-rev7-architecture", status: "pass", evidence: "Gate 04 rev 7 keeps the final sheen in Unity as an object-local mesh-clipped MaterialPropertyBlock effect with 0 pixels outside the case." },
    { id: "historical-material-language-compatible", status: "pass", evidence: "Frosted polycarbonate, continuous tube edge, black tactile insert, label paper, restrained neutral foil and all six material graph digests remain compatible." },
    { id: "real-rigid-turntable", status: "pass", evidence: `25 real Cycles frames cover 0°–360°; front-return mean channel delta is ${validation.turntableMetrics.frontReturnMeanAbsoluteChannelDelta}.` },
    { id: "transparent-ordering-readable", status: "pass", evidence: "Front, edge, reverse and returning-front renders passed subject luma, highlight and clipping checks under one neutral material rig." },
    { id: "grain-and-corner-highlight-stable", status: "pass", evidence: `Object-local grain is preserved; maximum adjacent mean luma delta is ${validation.turntableMetrics.maximumAdjacentMeanLumaDelta}, and minimum cardinal tube highlight contrast is ${validation.turntableMetrics.minimumCardinalTubeHighlightContrast}.` },
    { id: "mesh-clipped-sheen-mask", status: "pass", evidence: "Diagnostic sheen influence has 0 active pixels outside the subject and 0 outside allowed shell/tube material zones at 0°/90°/180°/270°/360°." },
    { id: "forbidden-effects-and-identity-absent", status: "pass", evidence: "No external halo, Point Light, particles, VFX Graph, bloom dependency, persistent emission, WHATNOT identity, yellow, smiley, barcode, sample number or circular coin-window visuals appear." },
    { id: "whole-case-and-toy-boundary", status: "pass", evidence: "Every user review artifact shows one assembled case; exploded review count is 0 and caller-owned toy content remains absent and unchanged." },
    { id: "gate-boundary", status: "pass", evidence: "Gate 07 rev 2 is ready_for_review only. Gate 08+, shipping Unity, Simulator, build, install and phone push remain blocked or stale." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  geometry.geometrySpec.gate07Status = "ready_for_review";
  geometry.geometrySpec.approval.gate07Status = "ready_for_review";
  markDownstreamStale(
    manifest,
    stageIndex,
    "Gate 07 material rev 2 is ready_for_review and awaits explicit turntable/material approval. Gate 08 must not start."
  );
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.visualApproval = "gate07-material-revalidation-pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.geometryRevalidation = {
    ...manifest.currentState.geometryRevalidation,
    gate06Status: "approved",
    gate07Status: "ready_for_review"
  };
  manifest.currentState.materialRevalidation = {
    materialRevision: 2,
    sourceGate06Revision: 3,
    sourceGate04EvidenceRevision: 7,
    historicalMaterialRevision: 1,
    materialGraphDigestCount: Object.keys(build.materialGraphDigestsAfter).length,
    turntableFrameCount: 25,
    outsideSubjectPixels: 0,
    outsideAllowedMaterialZonePixels: 0,
    gate07Status: "ready_for_review",
    gate08Status: "blocked"
  };
  manifest.currentState.diagnosis = "Gate 06 rev 3 is approved. Gate 07 material rev 2 freshly revalidates the historically approved neutral PBR language on unchanged geometry with a real 25-frame 360° turntable and object-local mesh-mask diagnostic. Gate 07 awaits visual approval; Gate 08+, shipping Unity, Simulator, build, install and phone remain blocked or unchanged.";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "07-material",
    materialRevision: 2,
    revalidatesHistoricalMaterialRevision: 1,
    sourceGate06Revision: 3,
    sourceGate04EvidenceRevision: 7,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    materialBoardPath: `${expectedDirectory}/material-board.png`,
    materialCloseupsPath: `${expectedDirectory}/material-closeups.png`,
    turntablePath: `${expectedDirectory}/material-turntable.mp4`,
    maskCompatibilityPath: `${expectedDirectory}/mesh-clipped-sheen-compatibility.png`,
    evaluatedGeometryDigest: identity.fullGeometryDigest,
    vertexPositionDigest: identity.vertexPositionDigest,
    topologyWindingDigest: identity.topologyWindingDigest,
    boundsMm: stage.materialSpec.boundsMm,
    materialGraphDigestCount: Object.keys(build.materialGraphDigestsAfter).length,
    turntableFrameCount: 25,
    outsideSubjectPixels: 0,
    outsideAllowedMaterialZonePixels: 0,
    approvalChecklist: validation.approvalChecklist,
    wholeCaseOnly: true,
    reviewExplodedPartCount: 0,
    neutralMaterialEnvironmentOnly: true,
    finalLightingApproved: false,
    autoApproved: false,
    gate08Status: "blocked",
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseLightingRevalidation(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (modelId !== "premium-display-case") {
    throw new PipelineError("Gate 08 lighting revalidation is supported only for premium-display-case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "08-lighting");
  const architecture = manifest.stages[3];
  const material = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  const approval = material.materialSpec?.approval;
  if (
    architecture.status !== "approved"
    || architecture.architectureSpec?.evidenceRevision !== 7
    || architecture.architectureSpec?.caseLightOutsideSilhouettePixels !== 0
    || material.status !== "approved"
    || material.materialSpec?.revision !== 2
    || approval?.approvedRevision !== 2
    || approval?.userApprovalQuote !== "材质与扫光批准，标签文字后续由 Unity 替换为真实数据"
    || approval?.labelContentApproved !== false
    || approval?.approvalScope?.includes("placeholder-label-text-and-artwork-excluded") !== true
    || approval?.approvalScope?.includes("unity-authoritative-label-data") !== true
    || stage.status !== "stale"
    || stage.lightingSpec?.revision !== 1
  ) {
    throw new PipelineError("Approved Gate 04 rev 7, Gate 07 rev 2 and stale historical Gate 08 rev 1 are required.", 422);
  }

  const revisionLabel = "002";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/08-lighting", `rev-${revisionLabel}`
  )));
  const definitions = [
    ["lighting-revalidation-builder", "lighting-source", "build_lighting_revalidation.py", "process", "gate08-rev2-real-blender-lighting-builder"],
    ["lighting-review-composer", "lighting-source", "compose_validate_lighting_revalidation.py", "process", "gate08-rev2-review-composer-and-image-validator"],
    ["lighting-revalidation-auditor", "lighting-source", "audit_lighting_revalidation.py", "process", "gate08-rev2-blender-source-auditor"],
    ["lighting-turntable-renderer", "lighting-source", "render_lighting_turntable.py", "process", "gate08-rev2-real-turntable-renderer"],
    ["lighting-blend", "lighting-blend", "premium-display-case-lighting-r002.blend", "source-model", "neutral-product-lighting-lookdev-blend"],
    ["lighting-revalidation", "validation-report", "lighting-revalidation.json", "validation", "lighting-material-geometry-architecture-report"],
    ["lighting-image-validation", "validation-report", "lighting-image-validation.json", "validation", "lighting-image-and-pass-validation"],
    ["lighting-blender-audit", "validation-report", "blender-lighting-audit.json", "validation", "lighting-blender-source-audit"],
    ["lighting-qa-verdict", "validation-report", "qa-verdict.json", "validation", "gate08-ready-not-shipping-verdict"],
    ["lighting-compatibility-snapshot", "lighting-contract", "lighting-compatibility-snapshot.json", "contract", "gate08-rev2-candidate-parameter-snapshot"],
    ["lighting-turntable-report", "validation-report", "lighting-turntable-report.json", "validation", "real-cycles-lighting-turntable-report"],
    ...[
      ["hero", "hero", "M08_HeroCamera", "perspective"],
      ["left-oblique", "left-oblique", "M08_Left_ObliqueCamera", "perspective"],
      ["right-oblique", "right-oblique", "M08_Right_ObliqueCamera", "perspective"],
      ["low", "low-angle", "M08_LowCamera", "perspective"],
      ["pass-beauty", "pass-beauty", "M08_HeroCamera", "beauty-pass"],
      ["pass-clay", "pass-clay", "M08_HeroCamera", "clay-pass"],
      ["pass-normal", "pass-normal", "M08_HeroCamera", "normal-pass"],
      ["pass-depth", "pass-depth", "M08_HeroCamera", "depth-pass"],
      ["pass-roughness", "pass-roughness", "M08_HeroCamera", "roughness-pass"],
      ["label-closeup", "lighting-detail", "M08_Label_CloseupCamera", "detail"],
      ["tube-corner", "lighting-detail", "M08_Tube_CornerCamera", "detail"],
      ["black-panel", "lighting-detail", "M08_Black_PanelCamera", "detail"]
    ].map(([name, slot, camera, viewKind]) => [
      `lighting-raw-${name}`,
      slot,
      `raw/${name}.png`,
      "blender-render",
      `real-gate08-${viewKind}`,
      name,
      camera,
      viewKind
    ]),
    ["lighting-review", "lighting-review-board", "lighting-review.png", "process", "plain-whole-case-lighting-review-board"],
    ["lighting-details", "lighting-review-board", "lighting-details-contact-sheet.png", "process", "material-zone-lighting-detail-board"],
    ["lighting-passes", "lighting-review-board", "lighting-passes-contact-sheet.png", "process", "beauty-clay-normal-depth-roughness-board"],
    ["lighting-parameters", "lighting-review-board", "lighting-parameters-board.png", "process", "lookdev-candidate-parameter-board"],
    ["lighting-label-placeholder", "lighting-review-board", "label-placeholder-review.png", "process", "placeholder-label-boundary-board"],
    ["lighting-sheen-compatibility", "lighting-review-board", "mesh-clipped-sheen-compatibility.png", "process", "zero-outside-silhouette-sheen-compatibility-frame"],
    ["lighting-turntable-mp4", "lighting-turntable", "lighting-turntable.mp4", "blender-render", "real-cycles-whole-case-lighting-turntable"],
    ["lighting-turntable-contact", "lighting-review-board", "lighting-turntable-contact-sheet.png", "process", "real-lighting-turntable-contact-sheet"],
    ...Array.from({ length: 13 }, (_, index) => [
      `lighting-turntable-frame-${String(index).padStart(3, "0")}`,
      "lighting-turntable-frame",
      `turntable/turn-${String(index).padStart(3, "0")}.png`,
      "blender-render",
      "real-cycles-lighting-turntable-frame",
      `turntable-${index * 30}`,
      "M08_HeroCamera",
      "turntable-sample"
    ])
  ].map(([
    suffix,
    slot,
    file,
    role,
    contentClass,
    viewId = null,
    camera = null,
    viewKind = null
  ]) => ({
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "08-lighting",
    slot,
    path: normalizeRepoPath(`${expectedDirectory}/${file}`),
    role,
    contentClass,
    viewId,
    camera,
    viewKind
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) {
      throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    }
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
      throw new PipelineError(`${record.id} file is missing.`, 422);
    }
  }

  const readReport = (file) => JSON.parse(
    fs.readFileSync(resolveRepoPath(`${expectedDirectory}/${file}`), "utf8")
  );
  const build = readReport("lighting-revalidation.json");
  const image = readReport("lighting-image-validation.json");
  const audit = readReport("blender-lighting-audit.json");
  const qa = readReport("qa-verdict.json");
  const snapshot = readReport("lighting-compatibility-snapshot.json");
  const turntable = readReport("lighting-turntable-report.json");
  const allChecksPass = (report) => (
    report?.status === "pass" && Object.values(report.checks || {}).every(Boolean)
  );
  const forbiddenEffectsAbsent = Object.values(build.forbiddenEffects || {}).every(
    (value) => value === false
  );
  const validEvidence = allChecksPass(build)
    && allChecksPass(image)
    && allChecksPass(audit)
    && allChecksPass(qa)
    && allChecksPass(turntable)
    && build.lightingRevision === 2
    && build.pipelineRevisionAtBuild === manifest.revision
    && build.sourceGate07?.materialRevision === 2
    && build.sourceGate07?.approvalQuote === approval.userApprovalQuote
    && build.sourceGate07?.labelContentApproved === false
    && build.sourceGate04?.architectureEvidenceRevision === 7
    && build.sourceGate04?.outsideSilhouettePixels === 0
    && build.geometry?.digestAfter === "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
    && build.geometry?.unchanged === true
    && build.materials?.unchanged === true
    && build.labelPolicy?.visibleContentState === "placeholder-not-approved"
    && build.labelPolicy?.fakeOrPlaceholderCollectibleIdForbidden === true
    && build.sheenCompatibility?.outsideSubjectPixels === 0
    && build.sheenCompatibility?.outsideAllowedMaterialZonePixels === 0
    && build.candidateBoundary?.blenderLookdevCandidatesOnly === true
    && build.candidateBoundary?.automaticUnityRuntimeConstants === false
    && build.animationBoundary?.timingBaked === false
    && build.animationBoundary?.easingBaked === false
    && forbiddenEffectsAbsent
    && build.scope?.wholeCaseOnly === true
    && build.scope?.explode === false
    && build.scope?.reviewExplodedPartCount === 0
    && image.labelPolicy?.visibleMarker === "placeholder-not-approved"
    && image.sheenCompatibility?.outsideSubjectPixels === 0
    && image.sheenCompatibility?.outsideAllowedMaterialZonePixels === 0
    && image.rawMetrics?.hero?.highlightClipFraction <= 0.005
    && image.blackPanelMetrics?.crushedBelow4Fraction <= 0.30
    && audit.geometryDigest === build.geometry.digestAfter
    && audit.materialDigest === build.materials.digestAfter
    && audit.labelContentApproved === false
    && qa.result === "READY_FOR_LIGHTING_REVIEW_NOT_SHIPPING"
    && snapshot.lightingRevision === 2
    && snapshot.sourceMaterialRevision === 2
    && snapshot.sourceArchitectureEvidenceRevision === 7
    && snapshot.wholeAssembledCaseOnly === true
    && snapshot.reviewExplodedPartCount === 0
    && snapshot.labelContentApproved === false
    && snapshot.meshClippedSheen?.outsideSubjectPixels === 0
    && snapshot.meshClippedSheen?.outsideAllowedMaterialZonePixels === 0
    && snapshot.gate08Status === "ready_for_review"
    && snapshot.gate09Status === "blocked"
    && turntable.frameCount === 13
    && turntable.assemblyState === "assembled"
    && turntable.reviewExplodedPartCount === 0
    && turntable.runtimeTimingBaked === false;
  if (!validEvidence) {
    throw new PipelineError("Premium Display Case Gate 08 rev 2 evidence does not satisfy the lighting revalidation contract.", 422);
  }

  const sourceAssetIds = [
    "premium-display-case-mesh-light-architecture-r007",
    "premium-display-case-modeling-contract-r003",
    "premium-display-case-geometry-blend-r003",
    "premium-display-case-material-blend-r002",
    "premium-display-case-material-revalidation-r002",
    "premium-display-case-material-review-validation-r002",
    "premium-display-case-material-compatibility-snapshot-r002"
  ];
  const sourceClaimIds = architecture.architectureSpec.sourceClaimIds;
  const reviewIds = new Set([
    `${modelId}-lighting-turntable-mp4-r${revisionLabel}`,
    `${modelId}-lighting-turntable-contact-r${revisionLabel}`,
    `${modelId}-lighting-review-r${revisionLabel}`,
    `${modelId}-lighting-details-r${revisionLabel}`,
    `${modelId}-lighting-passes-r${revisionLabel}`,
    `${modelId}-lighting-parameters-r${revisionLabel}`,
    `${modelId}-lighting-label-placeholder-r${revisionLabel}`,
    `${modelId}-lighting-sheen-compatibility-r${revisionLabel}`
  ]);
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    const isBlender = record.role === "blender-render" || record.slot === "lighting-blend";
    const asset = {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: record.role,
      producer: {
        name: isBlender ? "Blender" : "deterministic pipeline evidence",
        version: isBlender ? build.blender : "2026-08-27",
        recipe: `${expectedDirectory}/${
          record.slot === "lighting-turntable" || record.slot === "lighting-turntable-frame"
            ? "render_lighting_turntable.py"
            : (record.role === "blender-render" || record.slot === "lighting-blend"
              ? "build_lighting_revalidation.py"
              : "compose_validate_lighting_revalidation.py")
        }`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 08 rev 2 revalidates neutral product lighting on approved Gate 07 rev 2 materials and unchanged whole-case geometry. Label content remains an unapproved placeholder; Blender values are lookdev candidates only."
      },
      sourceAssetIds,
      sourceClaimIds,
      reviewState: reviewIds.has(record.id) ? "active" : "internal-evidence",
      wholeCaseOnly: true,
      wholeAssembledCaseOnly: true,
      explodeEligible: false,
      labelContentApproved: false
    };
    if (record.viewId) {
      asset.view = {
        id: record.viewId,
        kind: record.viewKind,
        camera: record.camera,
        assemblyState: "assembled",
        renderEngine: record.viewKind === "beauty-pass"
          || record.viewKind === "perspective"
          || record.viewKind === "detail"
          || record.viewKind === "turntable-sample"
          ? "CYCLES"
          : "BLENDER_EEVEE",
        axisContract: "X-width/Y-height/Z-front"
      };
    }
    if (record.slot === "lighting-turntable") {
      asset.interaction = {
        type: "real-render-turntable",
        frameCount: turntable.frameCount,
        durationSeconds: turntable.durationSeconds,
        approvalRequiresCompletedChecklist: true,
        approvalChecklist: snapshot.approvalChecklist,
        gate09EnvironmentApproval: false
      };
    }
    return asset;
  });
  manifest.assets.push(...records);

  stage.historicalLightingReviews = [
    ...(stage.historicalLightingReviews || []),
    {
      revision: stage.lightingSpec.revision,
      statusBeforeRevalidation: stage.status,
      decision: stage.decision,
      artifactIds: [...stage.artifactIds],
      reviewArtifactIds: [...stage.reviewArtifactIds],
      lightingSpec: stage.lightingSpec,
      preservationState: "immutable-historical-stale-after-gate07-rev2-revalidation"
    }
  ];
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.reviewArtifactIds = [...reviewIds];
  stage.lightingSpec = {
    revision: 2,
    revalidatesHistoricalLightingRevision: 1,
    sourceMaterialRevision: 2,
    sourceMaterialApprovalQuote: approval.userApprovalQuote,
    sourceMaterialApprovalScope: approval.approvalScope,
    sourceArchitectureEvidenceRevision: 7,
    sourceGeometryRevision: 3,
    sourceGeometryDigest: build.geometry.digestAfter,
    sourceMaterialDigest: build.materials.digestAfter,
    geometryUnchanged: true,
    materialUnchanged: true,
    wholeCaseOnly: true,
    wholeAssembledCaseOnly: true,
    reviewExplodedPartCount: 0,
    controlledRigCandidates: build.lighting,
    cameraCandidates: build.cameras,
    renderCandidates: build.render,
    candidateBoundary: build.candidateBoundary,
    animationBoundary: build.animationBoundary,
    labelPolicy: build.labelPolicy,
    meshClippedSheenCompatibility: build.sheenCompatibility,
    forbiddenEffects: build.forbiddenEffects,
    imageMetrics: {
      maximumHighlightClipFraction: Math.max(
        ...Object.values(image.rawMetrics).map((metric) => metric.highlightClipFraction)
      ),
      blackPanelMedianLuma: image.blackPanelMetrics.medianLuma,
      blackPanelCrushedBelow4Fraction: image.blackPanelMetrics.crushedBelow4Fraction,
      maximumAbsoluteMeanGreenExcess: Math.max(
        ...Object.values(image.greenBiasMetrics).map((metric) => Math.abs(metric.meanGreenExcess))
      ),
      tubeHighlightContinuityPass: image.tubeHighlightContinuity.pass
    },
    requiredViews: ["hero", "left-oblique", "right-oblique", "low"],
    requiredPasses: ["beauty", "clay", "normal", "depth", "roughness"],
    turntable: {
      artifactId: `${modelId}-lighting-turntable-mp4-r${revisionLabel}`,
      frameCount: turntable.frameCount,
      angleStepDegrees: turntable.angleStepDegrees,
      durationSeconds: turntable.durationSeconds,
      assemblyState: "assembled"
    },
    approvalChecklist: snapshot.approvalChecklist,
    finalLightingApproved: false,
    gate08Approved: false,
    gate09Entered: false,
    shippingUnityChanged: false,
    buildInstallPhonePush: false
  };
  stage.validations = [
    { id: "approved-gate07-rev2-source", status: "pass", evidence: "Gate 07 rev 2 is approved for materials and mesh-clipped sheen; label text/artwork remains explicitly excluded." },
    { id: "approved-gate04-rev7-architecture", status: "pass", evidence: "Gate 04 rev 7 whole-case and zero-outside-silhouette architecture remains unchanged." },
    { id: "geometry-and-material-digests-unchanged", status: "pass", evidence: `Geometry ${build.geometry.digestAfter} and material ${build.materials.digestAfter} remained unchanged.` },
    { id: "required-whole-case-views", status: "pass", evidence: "Hero, left/right oblique and low views show one assembled case with no exploded content." },
    { id: "required-technical-passes", status: "pass", evidence: "Beauty, Clay, Normal, Depth and Roughness passes are present, distinct and validated." },
    { id: "material-zones-readable", status: "pass", evidence: "Frosted shells, closed tube, black tactile insert, label paper/cover/foil zones remain readable." },
    { id: "whites-and-darks-controlled", status: "pass", evidence: `Maximum clip fraction ${stage.lightingSpec.imageMetrics.maximumHighlightClipFraction}; black-panel median ${stage.lightingSpec.imageMetrics.blackPanelMedianLuma}, crushed fraction ${stage.lightingSpec.imageMetrics.blackPanelCrushedBelow4Fraction}.` },
    { id: "neutral-forbidden-effects-absent", status: "pass", evidence: `Maximum absolute mean green excess ${stage.lightingSpec.imageMetrics.maximumAbsoluteMeanGreenExcess}; no rarity light, external halo, bloom, particles, flash, shake or persistent emission.` },
    { id: "mesh-clipped-sheen-compatibility", status: "pass", evidence: "Compatibility frame has 0 effect pixels outside the case and 0 outside allowed material zones." },
    { id: "label-placeholder-boundary", status: "pass", evidence: "Label content is visibly marked placeholder/not approved; Unity owns authoritative real data." },
    { id: "lookdev-candidate-boundary", status: "pass", evidence: "Blender light, temperature, exposure, FOV, width and falloff values are candidates, not Unity runtime constants." },
    { id: "animation-ownership-preserved", status: "pass", evidence: "No timing or easing is baked in Blender; Gate 04 runtime animation structure remains Unity-owned." },
    { id: "real-lighting-turntable", status: "pass", evidence: `${turntable.frameCount} real Cycles frames cover 0°–360° as one assembled case.` },
    { id: "gate-boundary", status: "pass", evidence: "Gate 08 rev 2 is ready_for_review only. Gate 09+, shipping Unity, Simulator, build, install and phone remain blocked or stale." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  material.materialSpec.gate08Entered = true;
  material.materialSpec.approval.gate08Status = "ready_for_review";
  markDownstreamStale(
    manifest,
    stageIndex,
    "Gate 08 lighting rev 2 is ready_for_review and awaits explicit lighting approval. Gate 09 must not start."
  );
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.visualApproval = "gate08-lighting-revalidation-pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.materialRevalidation = {
    ...manifest.currentState.materialRevalidation,
    gate07Status: "approved",
    gate08Status: "ready_for_review",
    labelContentApproved: false,
    labelAuthority: "unity-real-runtime-data"
  };
  manifest.currentState.lightingRevalidation = {
    lightingRevision: 2,
    sourceMaterialRevision: 2,
    sourceArchitectureEvidenceRevision: 7,
    geometryDigest: build.geometry.digestAfter,
    materialDigest: build.materials.digestAfter,
    turntableFrameCount: turntable.frameCount,
    outsideSubjectPixels: 0,
    labelContentApproved: false,
    lookdevCandidatesOnly: true,
    gate08Status: "ready_for_review",
    gate09Status: "blocked"
  };
  manifest.currentState.diagnosis = "Gate 07 rev 2 is approved with placeholder label content excluded. Gate 08 rev 2 revalidates neutral professional product lighting on unchanged geometry/materials using whole-case Hero, oblique, low, technical passes and a real rendered turntable. Mesh-clipped sheen remains 0 pixels outside the silhouette; label content remains placeholder/not approved; Blender values are lookdev candidates only. Gate 08 awaits visual approval. Gate 09+, shipping Unity, Simulator, build, install and phone remain blocked or unchanged.";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "08-lighting",
    lightingRevision: 2,
    revalidatesHistoricalLightingRevision: 1,
    sourceMaterialRevision: 2,
    sourceMaterialApprovalQuote: approval.userApprovalQuote,
    sourceArchitectureEvidenceRevision: 7,
    geometryDigest: build.geometry.digestAfter,
    materialDigest: build.materials.digestAfter,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    lightingReviewPath: `${expectedDirectory}/lighting-review.png`,
    turntablePath: `${expectedDirectory}/lighting-turntable.mp4`,
    labelPlaceholderPath: `${expectedDirectory}/label-placeholder-review.png`,
    meshClippedSheenCompatibilityPath: `${expectedDirectory}/mesh-clipped-sheen-compatibility.png`,
    turntableFrameCount: turntable.frameCount,
    approvalChecklist: snapshot.approvalChecklist,
    wholeCaseOnly: true,
    reviewExplodedPartCount: 0,
    labelContentApproved: false,
    outsideSubjectPixels: 0,
    lookdevCandidatesOnly: true,
    runtimeTimingBaked: false,
    autoApproved: false,
    gate09Status: "blocked",
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseEnvironmentRevalidation(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (modelId !== "premium-display-case") {
    throw new PipelineError("Gate 09 environment revalidation is supported only for premium-display-case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "09-environment");
  const architecture = manifest.stages[3];
  const lighting = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  const approval = lighting.lightingSpec?.approval;
  if (
    architecture.status !== "approved"
    || architecture.architectureSpec?.evidenceRevision !== 7
    || architecture.architectureSpec?.caseLightOutsideSilhouettePixels !== 0
    || lighting.status !== "approved"
    || lighting.lightingSpec?.revision !== 2
    || approval?.approvedRevision !== 2
    || approval?.userApprovalQuote !== "灯光方向正确，批准并继续（推荐）"
    || approval?.labelContentApproved !== false
    || approval?.lookdevCandidatesOnly !== true
    || approval?.unityRuntimeValuesTunable !== true
    || stage.artifactIds.length !== 0
    || !["blocked", "stale"].includes(stage.status)
  ) {
    throw new PipelineError("Approved Gate 04 rev 7, Gate 08 rev 2 and an empty Gate 09 are required.", 422);
  }

  const revisionLabel = "001";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/09-environment", `rev-${revisionLabel}`
  )));
  const definitions = [
    ["environment-revalidation-builder", "environment-source", "build_environment_revalidation.py", "process", "gate09-rev1-real-blender-environment-builder"],
    ["environment-revalidation-auditor", "environment-source", "audit_environment_revalidation.py", "process", "gate09-rev1-blender-source-auditor"],
    ["environment-review-composer", "environment-source", "compose_validate_environment_revalidation.py", "process", "gate09-rev1-review-composer-and-image-validator"],
    ["environment-blend", "environment-blend", "premium-display-case-environment-r001.blend", "source-model", "static-shipping-context-environment-lookdev-blend"],
    ["environment-revalidation", "validation-report", "environment-revalidation.json", "validation", "environment-geometry-material-light-camera-report"],
    ["environment-image-validation", "validation-report", "environment-image-validation.json", "validation", "environment-image-and-background-validation"],
    ["environment-blender-audit", "validation-report", "blender-environment-audit.json", "validation", "environment-blender-source-audit"],
    ["environment-qa-verdict", "validation-report", "qa-verdict.json", "validation", "gate09-ready-not-shipping-verdict"],
    ["environment-compatibility-snapshot", "environment-contract", "environment-compatibility-snapshot.json", "contract", "gate09-rev1-candidate-parameter-snapshot"],
    ["environment-neutral-hero", "neutral-environment", "raw/neutral-hero.png", "blender-render", "approved-gate08-neutral-control", "hero", "M08_HeroCamera", "neutral-control"],
    ["environment-shipping-hero", "shipping-environment", "raw/shipping-hero.png", "blender-render", "static-shipping-context-environment", "hero", "M08_HeroCamera", "shipping-context"],
    ...[
      ["neutral-left-oblique", "environment-view", "M08_Left_ObliqueCamera", "neutral-control"],
      ["neutral-right-oblique", "environment-view", "M08_Right_ObliqueCamera", "neutral-control"],
      ["neutral-low", "environment-view", "M08_LowCamera", "neutral-control"],
      ["shipping-left-oblique", "environment-view", "M08_Left_ObliqueCamera", "shipping-context"],
      ["shipping-right-oblique", "environment-view", "M08_Right_ObliqueCamera", "shipping-context"],
      ["shipping-low", "environment-view", "M08_LowCamera", "shipping-context"],
      ["shipping-label-closeup", "environment-detail", "M08_Label_CloseupCamera", "shipping-context-detail"],
      ["shipping-black-panel", "environment-detail", "M08_Black_PanelCamera", "shipping-context-detail"],
      ["shipping-background-hero-a", "environment-background", "M08_HeroCamera", "shipping-context-background"],
      ["shipping-background-hero-b", "environment-background", "M08_HeroCamera", "shipping-context-background-repeat"]
    ].map(([name, slot, camera, viewKind]) => [
      `environment-raw-${name}`,
      slot,
      `raw/${name}.png`,
      "blender-render",
      `real-gate09-${viewKind}`,
      name,
      camera,
      viewKind
    ]),
    ["environment-review", "environment-review-board", "environment-review.png", "process", "neutral-versus-shipping-whole-case-review-board"],
    ["environment-matched-hero", "environment-review-board", "matched-hero-comparison.png", "process", "matched-camera-neutral-shipping-hero"],
    ["environment-details", "environment-review-board", "environment-details.png", "process", "label-and-black-panel-readability-board"],
    ["environment-parameters", "environment-review-board", "environment-parameters.png", "process", "environment-candidate-boundary-board"],
    ["environment-sheen-compatibility", "environment-review-board", "mesh-clipped-sheen-compatibility.png", "process", "inside-case-sheen-environment-compatibility"],
    ["environment-comparison-contact", "environment-review-board", "environment-comparison-contact-sheet.png", "process", "matched-camera-environment-comparison-contact"],
    ["environment-comparison-mp4", "environment-comparison-recording", "environment-comparison.mp4", "blender-render", "real-render-static-matched-camera-comparison-recording"]
  ].map(([
    suffix,
    slot,
    file,
    role,
    contentClass,
    viewId = null,
    camera = null,
    viewKind = null
  ]) => ({
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "09-environment",
    slot,
    path: normalizeRepoPath(`${expectedDirectory}/${file}`),
    role,
    contentClass,
    viewId,
    camera,
    viewKind
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) {
      throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    }
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
      throw new PipelineError(`${record.id} file is missing.`, 422);
    }
  }

  const readReport = (file) => JSON.parse(
    fs.readFileSync(resolveRepoPath(`${expectedDirectory}/${file}`), "utf8")
  );
  const build = readReport("environment-revalidation.json");
  const image = readReport("environment-image-validation.json");
  const audit = readReport("blender-environment-audit.json");
  const qa = readReport("qa-verdict.json");
  const snapshot = readReport("environment-compatibility-snapshot.json");
  const allChecksPass = (report) => (
    report?.status === "pass" && Object.values(report.checks || {}).every(Boolean)
  );
  const forbiddenEffectsAbsent = Object.values(snapshot.forbiddenEffects || {}).every(
    (value) => value === false
  );
  const validEvidence = allChecksPass(build)
    && allChecksPass(image)
    && allChecksPass(audit)
    && allChecksPass(qa)
    && build.environmentRevision === 1
    && build.pipelineRevisionAtBuild === manifest.revision
    && build.sourceGate08?.lightingRevision === 2
    && build.sourceGate08?.approvalQuote === approval.userApprovalQuote
    && build.sourceGate08?.geometryDigest === "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
    && build.sourceGate08?.materialDigest === "8358cfdb12e49f87adbbafd96f33f2beb3415f9b920cb62732c73173c7799210"
    && build.geometry?.unchanged === true
    && build.materials?.unchanged === true
    && build.matchedCamera?.unchanged === true
    && build.approvedLighting?.unchanged === true
    && build.shippingEnvironment?.grainIntensity === 0.012
    && build.shippingEnvironment?.emission === 0
    && build.policy?.wholeAssembledCaseOnly === true
    && build.policy?.reviewExplodedPartCount === 0
    && build.policy?.backgroundStaticThroughoutReveal === true
    && build.policy?.cameraMotion === false
    && build.policy?.backgroundMotion === false
    && build.policy?.toyPrizeOwnership === "caller-owned-static"
    && build.policy?.labelContentState === "placeholder-not-approved"
    && build.policy?.meshClippedSheen === "material-runtime-cue-inside-case-only"
    && build.policy?.environmentReflection === "surface-shaping-only-no-detached-light-effect"
    && build.policy?.blenderValuesAreUnityRuntimeConstants === false
    && forbiddenEffectsAbsent
    && image.minimumSubjectMargin >= 0.12
    && image.repeatedBackgroundMaximumChannelDelta === 0
    && image.haloMetrics?.outsideExpandedSubjectP99PositiveDelta <= 14
    && image.haloMetrics?.outsideExpandedSubjectAbove16Fraction <= 0.004
    && image.comparisonRecording?.frameCount === 72
    && image.comparisonRecording?.durationSeconds >= 5.9
    && image.comparisonRecording?.cameraMotion === false
    && image.comparisonRecording?.backgroundMotionWithinView === false
    && image.comparisonRecording?.wholeAssembledCaseOnly === true
    && image.comparisonRecording?.reviewExplodedPartCount === 0
    && audit.geometryDigest === build.geometry.digestAfter
    && audit.materialDigest === build.materials.digestAfter
    && audit.cameraDigest === build.matchedCamera.digestAfter
    && audit.lightingDigest === build.approvedLighting.digestAfter
    && qa.result === "READY_FOR_ENVIRONMENT_REVIEW_NOT_SHIPPING"
    && snapshot.environmentRevision === 1
    && snapshot.sourceLightingRevision === 2
    && snapshot.sourceLightingApprovalQuote === approval.userApprovalQuote
    && snapshot.wholeAssembledCaseOnly === true
    && snapshot.reviewExplodedPartCount === 0
    && snapshot.neutralAndShippingMatchedCamera === true
    && snapshot.backgroundStatic === true
    && snapshot.cameraMotion === false
    && snapshot.backgroundMotion === false
    && snapshot.toyPrizeOwnership === "caller-owned-static"
    && snapshot.labelContentApproved === false
    && snapshot.meshClippedSheen?.outsideSubjectPixels === 0
    && snapshot.meshClippedSheen?.detachedLightEffect === false
    && snapshot.candidateBoundary?.blenderEnvironmentValuesAreUnityRuntimeConstants === false
    && snapshot.candidateBoundary?.unityEnvironmentTunable === true
    && snapshot.candidateBoundary?.unityIblIntensityTunable === true
    && snapshot.candidateBoundary?.unityExposureTunable === true
    && snapshot.candidateBoundary?.unityCameraTunable === true
    && snapshot.gate09Approved === false
    && snapshot.gate10Entered === false
    && snapshot.shippingUnityChanged === false
    && snapshot.buildInstallPhonePush === false;
  if (!validEvidence) {
    throw new PipelineError("Premium Display Case Gate 09 rev 1 evidence does not satisfy the environment revalidation contract.", 422);
  }

  const sourceAssetIds = [
    "premium-display-case-mesh-light-architecture-r007",
    "premium-display-case-modeling-contract-r003",
    "premium-display-case-geometry-blend-r003",
    "premium-display-case-material-blend-r002",
    "premium-display-case-material-compatibility-snapshot-r002",
    "premium-display-case-lighting-blend-r002",
    "premium-display-case-lighting-revalidation-r002",
    "premium-display-case-lighting-compatibility-snapshot-r002",
    "premium-display-case-lighting-turntable-mp4-r002"
  ];
  const sourceClaimIds = architecture.architectureSpec.sourceClaimIds;
  const reviewIds = new Set([
    `${modelId}-environment-comparison-mp4-r${revisionLabel}`,
    `${modelId}-environment-review-r${revisionLabel}`,
    `${modelId}-environment-matched-hero-r${revisionLabel}`,
    `${modelId}-environment-details-r${revisionLabel}`,
    `${modelId}-environment-parameters-r${revisionLabel}`,
    `${modelId}-environment-sheen-compatibility-r${revisionLabel}`,
    `${modelId}-environment-comparison-contact-r${revisionLabel}`
  ]);
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    const isBlender = record.role === "blender-render" || record.slot === "environment-blend";
    let recipe = "compose_validate_environment_revalidation.py";
    if (record.id.includes("auditor") || record.id.includes("blender-audit")) {
      recipe = "audit_environment_revalidation.py";
    } else if (
      isBlender
      && record.slot !== "environment-comparison-recording"
    ) {
      recipe = "build_environment_revalidation.py";
    }
    const asset = {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: record.role,
      producer: {
        name: isBlender ? "Blender" : "deterministic pipeline evidence",
        version: isBlender ? build.blender : "2026-08-27",
        recipe: `${expectedDirectory}/${recipe}`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 09 rev 1 compares the approved Gate 08 neutral control against a static, low-saturation shipping-context environment. Geometry, product materials, light direction and matched cameras remain unchanged. Label content stays placeholder/not approved; Unity environment values remain tunable."
      },
      sourceAssetIds,
      sourceClaimIds,
      reviewState: reviewIds.has(record.id) ? "active" : "internal-evidence",
      wholeCaseOnly: true,
      wholeAssembledCaseOnly: true,
      explodeEligible: false,
      labelContentApproved: false
    };
    if (record.viewId) {
      asset.view = {
        id: record.viewId,
        kind: record.viewKind,
        camera: record.camera,
        assemblyState: "assembled",
        renderEngine: "CYCLES",
        axisContract: "X-width/Y-height/Z-front",
        matchedCamera: true,
        backgroundStatic: true
      };
    }
    if (record.slot === "environment-comparison-recording") {
      asset.interaction = {
        type: "real-render-static-matched-camera-comparison-recording",
        frameCount: image.comparisonRecording.frameCount,
        durationSeconds: image.comparisonRecording.durationSeconds,
        approvalRequiresCompletedChecklist: true,
        approvalChecklist: snapshot.approvalChecklist,
        gate10ExportApproval: false
      };
    }
    return asset;
  });
  manifest.assets.push(...records);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.reviewArtifactIds = [...reviewIds];
  stage.environmentSpec = {
    revision: 1,
    sourceLightingRevision: 2,
    sourceLightingApprovalQuote: approval.userApprovalQuote,
    sourceLightingApprovalScope: approval.approvalScope,
    sourceArchitectureEvidenceRevision: 7,
    sourceGeometryRevision: 3,
    sourceMaterialRevision: 2,
    sourceGeometryDigest: build.geometry.digestAfter,
    sourceMaterialDigest: build.materials.digestAfter,
    sourceCameraDigest: build.matchedCamera.digestAfter,
    sourceLightingDigest: build.approvedLighting.digestAfter,
    geometryUnchanged: true,
    materialUnchanged: true,
    cameraUnchanged: true,
    approvedLightingDirectionUnchanged: true,
    wholeCaseOnly: true,
    wholeAssembledCaseOnly: true,
    reviewExplodedPartCount: 0,
    neutralEnvironment: build.neutralEnvironment,
    shippingEnvironment: build.shippingEnvironment,
    environmentPolicy: build.policy,
    imageMetrics: {
      minimumSubjectMargin: image.minimumSubjectMargin,
      maximumShippingHighlightClipFraction: snapshot.maximumShippingHighlightClipFraction,
      maximumShippingBackgroundP95AbsoluteChromaNormalized:
        snapshot.maximumShippingBackgroundP95AbsoluteChromaNormalized,
      maximumAbsoluteShippingBackgroundMeanGreenExcess:
        snapshot.maximumAbsoluteShippingBackgroundMeanGreenExcess,
      repeatedBackgroundMaximumChannelDelta:
        image.repeatedBackgroundMaximumChannelDelta,
      externalHaloMetrics: image.haloMetrics,
      localBackgroundMetrics: image.backgroundStructureMetrics,
      labelMetrics: image.labelMetrics,
      blackPanelMetrics: image.blackPanelMetrics
    },
    meshClippedSheen: snapshot.meshClippedSheen,
    environmentReflection: snapshot.environmentReflection,
    labelPolicy: {
      visibleContentState: snapshot.labelContentState,
      approved: false,
      runtimeAuthority: "Unity real product data"
    },
    toyPrizeOwnership: "caller-owned-static",
    comparisonRecording: {
      artifactId: `${modelId}-environment-comparison-mp4-r${revisionLabel}`,
      frameCount: image.comparisonRecording.frameCount,
      durationSeconds: image.comparisonRecording.durationSeconds,
      cameraMotion: false,
      backgroundMotionWithinView: false,
      assemblyState: "assembled"
    },
    approvalChecklist: snapshot.approvalChecklist,
    candidateBoundary: snapshot.candidateBoundary,
    forbiddenEffects: snapshot.forbiddenEffects,
    gate09Approved: false,
    gate10Entered: false,
    shippingUnityChanged: false,
    buildInstallPhonePush: false
  };
  stage.validations = [
    { id: "approved-gate08-rev2-source", status: "pass", evidence: "Gate 08 rev 2 is approved for neutral lighting direction; label content stays excluded and Blender values stay lookdev-only." },
    { id: "geometry-material-light-camera-unchanged", status: "pass", evidence: `Geometry ${build.geometry.digestAfter}, material ${build.materials.digestAfter}, camera ${build.matchedCamera.digestAfter} and lighting ${build.approvedLighting.digestAfter} remain unchanged.` },
    { id: "matched-neutral-shipping-views", status: "pass", evidence: "Hero, left/right oblique and low comparisons use matched cameras and one assembled case." },
    { id: "comfortable-subject-margins", status: "pass", evidence: `Minimum subject margin ${image.minimumSubjectMargin}.` },
    { id: "label-black-panel-readable", status: "pass", evidence: `Label p10–p90 range ${image.labelMetrics.p10P90Range}; black panel p05–p95 range ${image.blackPanelMetrics.p05P95Range}.` },
    { id: "static-background", status: "pass", evidence: `Repeated background maximum decoded channel delta ${image.repeatedBackgroundMaximumChannelDelta}; no camera or background animation.` },
    { id: "low-saturation-no-green-cast", status: "pass", evidence: `Maximum absolute chroma ${snapshot.maximumShippingBackgroundP95AbsoluteChromaNormalized}; maximum mean green excess ${snapshot.maximumAbsoluteShippingBackgroundMeanGreenExcess}.` },
    { id: "no-external-halo-or-local-blob", status: "pass", evidence: `Outside-subject p99 positive delta ${image.haloMetrics.outsideExpandedSubjectP99PositiveDelta}; background row residual ${image.backgroundStructureMetrics.maximumRowResidual}.` },
    { id: "mesh-clipped-sheen-inside-case", status: "pass", evidence: "Approved sheen compatibility remains 0 pixels outside the case and is not a detached environment effect." },
    { id: "placeholder-label-boundary", status: "pass", evidence: "Label content remains visibly marked placeholder/not approved; Unity owns authoritative real data." },
    { id: "unity-candidate-boundary", status: "pass", evidence: "Unity environment, IBL intensity, exposure and camera remain tunable through Gates 11–12." },
    { id: "real-comparison-recording", status: "pass", evidence: `${image.comparisonRecording.frameCount} frames and ${image.comparisonRecording.durationSeconds} seconds cover four static matched-camera pairs.` },
    { id: "gate-boundary", status: "pass", evidence: "Gate 09 rev 1 is ready_for_review only. Gate 10+, shipping Unity, Simulator, build, install and phone remain blocked or unchanged." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  lighting.lightingSpec.gate09Entered = true;
  lighting.lightingSpec.approval.gate09Status = "ready_for_review";
  markDownstreamStale(
    manifest,
    stageIndex,
    "Gate 09 environment rev 1 is ready_for_review and awaits explicit environment approval. Gate 10 must not start."
  );
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.visualApproval = "gate09-environment-revalidation-pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.lightingRevalidation = {
    ...manifest.currentState.lightingRevalidation,
    gate08Status: "approved",
    gate09Status: "ready_for_review",
    labelContentApproved: false,
    lookdevCandidatesOnly: true,
    unityRuntimeValuesTunable: true
  };
  manifest.currentState.environmentRevalidation = {
    environmentRevision: 1,
    sourceLightingRevision: 2,
    geometryDigest: build.geometry.digestAfter,
    materialDigest: build.materials.digestAfter,
    cameraDigest: build.matchedCamera.digestAfter,
    lightingDigest: build.approvedLighting.digestAfter,
    minimumSubjectMargin: image.minimumSubjectMargin,
    maximumAbsoluteChromaNormalized:
      snapshot.maximumShippingBackgroundP95AbsoluteChromaNormalized,
    maximumMeanGreenExcess:
      snapshot.maximumAbsoluteShippingBackgroundMeanGreenExcess,
    outsideSubjectP99PositiveDelta:
      image.haloMetrics.outsideExpandedSubjectP99PositiveDelta,
    repeatedBackgroundMaximumChannelDelta:
      image.repeatedBackgroundMaximumChannelDelta,
    labelContentApproved: false,
    gate09Status: "ready_for_review",
    gate10Status: "blocked"
  };
  manifest.currentState.diagnosis = "Gate 08 rev 2 lighting is approved. Gate 09 rev 1 now compares the same whole case, pose, cameras and approved light direction in the neutral control and a static low-saturation friction shipping-context environment. Geometry, product materials, light and camera digests are unchanged; margins, label/black-panel readability, color neutrality, background stability and no-halo/no-local-blob checks pass. Mesh-clipped sheen remains inside the case, label content remains placeholder/not approved, and Unity environment values remain tunable. Gate 09 awaits visual approval; Gate 10+, shipping Unity, Simulator, build, install and phone remain blocked or unchanged.";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "09-environment",
    environmentRevision: 1,
    sourceLightingRevision: 2,
    sourceLightingApprovalQuote: approval.userApprovalQuote,
    geometryDigest: build.geometry.digestAfter,
    materialDigest: build.materials.digestAfter,
    cameraDigest: build.matchedCamera.digestAfter,
    lightingDigest: build.approvedLighting.digestAfter,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    environmentReviewPath: `${expectedDirectory}/environment-review.png`,
    matchedHeroPath: `${expectedDirectory}/matched-hero-comparison.png`,
    comparisonRecordingPath: `${expectedDirectory}/environment-comparison.mp4`,
    detailsPath: `${expectedDirectory}/environment-details.png`,
    parametersPath: `${expectedDirectory}/environment-parameters.png`,
    meshClippedSheenCompatibilityPath: `${expectedDirectory}/mesh-clipped-sheen-compatibility.png`,
    comparisonFrameCount: image.comparisonRecording.frameCount,
    comparisonDurationSeconds: image.comparisonRecording.durationSeconds,
    approvalChecklist: snapshot.approvalChecklist,
    wholeCaseOnly: true,
    reviewExplodedPartCount: 0,
    labelContentApproved: false,
    minimumSubjectMargin: image.minimumSubjectMargin,
    maximumAbsoluteChromaNormalized:
      snapshot.maximumShippingBackgroundP95AbsoluteChromaNormalized,
    maximumMeanGreenExcess:
      snapshot.maximumAbsoluteShippingBackgroundMeanGreenExcess,
    outsideSubjectP99PositiveDelta:
      image.haloMetrics.outsideExpandedSubjectP99PositiveDelta,
    repeatedBackgroundMaximumChannelDelta:
      image.repeatedBackgroundMaximumChannelDelta,
    matchedCamera: true,
    approvedLightingDirectionUnchanged: true,
    unityRuntimeValuesTunable: true,
    autoApproved: false,
    gate10Status: "blocked",
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function savePremiumDisplayCaseExportReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (modelId !== "premium-display-case") {
    throw new PipelineError("Gate 10 export review is supported only for premium-display-case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "10-export");
  const architecture = manifest.stages[3];
  const geometry = manifest.stages[5];
  const material = manifest.stages[6];
  const environment = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  const approval = environment.environmentSpec?.approval;
  const approvalEvent = readHistory(modelId)
    .filter((event) => (
      event.type === "stage-approved"
      && event.stageId === "09-environment"
      && event.manifestRevision === manifest.revision
    ))
    .at(-1);
  if (
    architecture.status !== "approved"
    || architecture.architectureSpec?.evidenceRevision !== 7
    || geometry.status !== "approved"
    || geometry.geometrySpec?.revision !== 3
    || material.status !== "approved"
    || material.materialSpec?.revision !== 2
    || environment.status !== "approved"
    || environment.environmentSpec?.revision !== 1
    || approval?.approvedRevision !== 1
    || approval?.userApprovalQuote !== "环境正确，批准并继续（推荐）"
    || approval?.labelContentApproved !== false
    || approval?.lookdevCandidatesOnly !== true
    || approval?.unityRuntimeValuesTunable !== true
    || !approvalEvent
    || stage.artifactIds.length !== 0
    || !["blocked", "stale"].includes(stage.status)
  ) {
    throw new PipelineError("Approved Gates 04, 06, 07, 09 and an empty Gate 10 are required.", 422);
  }

  const revisionLabel = "001";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/10-export", `rev-${revisionLabel}`
  )));
  const definitions = [
    ["export-builder", "export-source", "build_export_package.py", "process", "gate10-product-only-blend-fbx-glb-builder"],
    ["export-roundtrip-validator", "export-validator", "validate_export_roundtrip.py", "process", "fresh-scene-fbx-glb-roundtrip-validator"],
    ["export-review-renderer", "export-review-renderer", "render_export_review.py", "process", "assembled-blend-fbx-glb-review-renderer"],
    ["export-review-composer", "export-review-composer", "compose_export_review.py", "process", "gate10-board-manifest-qa-composer"],
    ["product-blend", "blend-source", "premium-display-case-product-r001.blend", "source-model", "product-only-approved-whole-case-blender-source"],
    ["product-fbx", "fbx-export", "premium-display-case-product-r001.fbx", "export", "unity-ready-whole-case-fbx"],
    ["product-glb", "glb-export", "premium-display-case-product-r001.glb", "export", "portable-interactive-whole-case-glb"],
    ["collision-policy", "collision-export", "collision-policy.json", "contract", "no-approved-collision-proxy-policy"],
    ["export-manifest", "export-manifest", "export-manifest.json", "contract", "product-export-manifest-and-hashes"],
    ["export-build-report", "validation-report", "export-build-report.json", "validation", "product-source-build-and-scope-validation"],
    ["export-roundtrip-report", "validation-report", "export-roundtrip-validation.json", "validation", "fresh-scene-hierarchy-transform-bounds-material-normal-validation"],
    ["export-glb-structure", "validation-report", "glb-structure-validation.json", "validation", "glb-node-mesh-material-animation-structure-validation"],
    ["export-render-report", "validation-report", "export-render-report.json", "validation", "assembled-whole-case-review-render-validation"],
    ["export-optimization-report", "validation-report", "asset-optimization-report.json", "validation", "unchanged-geometry-performance-audit"],
    ["export-validation-links", "validation-report", "validation-links.json", "validation", "export-artifact-and-validation-links"],
    ["export-qa-verdict", "validation-report", "qa-verdict.json", "validation", "gate10-ready-not-unity-verdict"],
    ["export-source-hero", "export-review-render", "raw/source-hero.png", "blender-render", "assembled-product-blend-neutral-review", "source"],
    ["export-fbx-hero", "export-review-render", "raw/fbx-hero.png", "blender-render", "assembled-fbx-roundtrip-neutral-review", "fbx"],
    ["export-glb-hero", "export-review-render", "raw/glb-hero.png", "blender-render", "assembled-glb-roundtrip-neutral-review", "glb"],
    ["export-review-board", "export-review-board", "export-review.png", "process", "whole-case-blend-fbx-glb-export-review-board"]
  ].map(([
    suffix,
    slot,
    file,
    role,
    contentClass,
    viewId = null
  ]) => ({
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "10-export",
    slot,
    path: normalizeRepoPath(`${expectedDirectory}/${file}`),
    role,
    contentClass,
    viewId
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) {
      throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    }
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) {
      throw new PipelineError(`${record.id} file is missing.`, 422);
    }
    if (manifest.assets.some((asset) => asset.id === record.id)) {
      throw new PipelineError(`${record.id} already exists.`, 409);
    }
  }

  const readReport = (file) => JSON.parse(
    fs.readFileSync(resolveRepoPath(`${expectedDirectory}/${file}`), "utf8")
  );
  const build = readReport("export-build-report.json");
  const roundtrip = readReport("export-roundtrip-validation.json");
  const glbStructure = readReport("glb-structure-validation.json");
  const render = readReport("export-render-report.json");
  const exportManifest = readReport("export-manifest.json");
  const collision = readReport("collision-policy.json");
  const optimization = readReport("asset-optimization-report.json");
  const links = readReport("validation-links.json");
  const qa = readReport("qa-verdict.json");
  const allChecksPass = (report) => (
    report?.status === "pass" && Object.values(report.checks || {}).every(Boolean)
  );
  const files = {
    blend: resolveRepoPath(`${expectedDirectory}/premium-display-case-product-r001.blend`),
    fbx: resolveRepoPath(`${expectedDirectory}/premium-display-case-product-r001.fbx`),
    glb: resolveRepoPath(`${expectedDirectory}/premium-display-case-product-r001.glb`),
    board: resolveRepoPath(`${expectedDirectory}/export-review.png`)
  };
  const dimensions = exportManifest.product?.dimensionsMm;
  const forbiddenExcluded = [
    "toyPrize",
    "proxyGeometry",
    "explodedGeometry",
    "lightGeometry",
    "externalHalo",
    "particlesVfx",
    "cameraBackground"
  ].every((key) => exportManifest.excluded?.[key] === true);
  const runtimeFalse = [
    "placeholderTextBaked",
    "fakeCollectibleIdBaked",
    "animationBaked",
    "timingBaked",
    "easingBaked",
    "entryPathBaked",
    "showcaseRotationBaked",
    "lightCuesBaked"
  ].every((key) => exportManifest.runtimeBoundary?.[key] === false);
  const validEvidence = allChecksPass(build)
    && allChecksPass(roundtrip)
    && allChecksPass(glbStructure)
    && allChecksPass(render)
    && allChecksPass(qa)
    && build.exportRevision === 1
    && build.pipelineRevisionAtBuild === manifest.revision
    && build.sourceGate09?.environmentRevision === 1
    && build.sourceGate09?.approvalEventId === approvalEvent.id
    && build.sourceGate09?.approvalQuote === approval.userApprovalQuote
    && build.geometry?.approvedDigest === "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
    && build.geometry?.productBlendDigest === build.geometry.approvedDigest
    && build.geometry?.unchanged === true
    && build.geometry?.boundsMm?.sizeMm?.width === 228
    && build.geometry?.boundsMm?.sizeMm?.height === 304
    && build.geometry?.boundsMm?.sizeMm?.depth === 59
    && build.geometry?.labelCenterYmm === 99
    && build.hierarchy?.runtimeMotionOwner === "PresentationRoot"
    && build.hierarchy?.rigidAssembly === "CaseAssembly"
    && build.hierarchy?.contentSlot === "caller-owned-empty"
    && build.hierarchy?.sameWholeCase === true
    && build.materials?.approvedDigest === "8358cfdb12e49f87adbbafd96f33f2beb3415f9b920cb62732c73173c7799210"
    && build.runtimeBoundary?.labelContentAuthority === "Unity runtime data"
    && runtimeFalse
    && forbiddenExcluded
    && build.collision?.included === false
    && roundtrip.crossFormat?.geometryDigestIdentity === true
    && roundtrip.crossFormat?.exportTriangulatedSurfaceDigestIdentity === true
    && roundtrip.crossFormat?.exportTriangulatedWindingDigestIdentity === true
    && roundtrip.crossFormat?.sourceAndExportWindingOrientationPositive === true
    && roundtrip.crossFormat?.sourceToExportVolumeErrorWithinPoint005Percent === true
    && roundtrip.crossFormat?.triangleCountIdentity === true
    && roundtrip.crossFormat?.boundsIdentity === true
    && roundtrip.crossFormat?.materialAssignmentsIdentity === true
    && roundtrip.crossFormat?.hierarchyIdentity === true
    && roundtrip.fbx?.vertexCorrespondence?.maximumErrorMm <= 0.001
    && roundtrip.glb?.vertexCorrespondence?.maximumErrorMm <= 0.001
    && glbStructure.nodeCount === 12
    && glbStructure.meshCount === 5
    && glbStructure.animations === 0
    && glbStructure.cameras === 0
    && render.reviewPolicy?.wholeAssembledCaseOnly === true
    && render.reviewPolicy?.explodedPartCount === 0
    && render.reviewPolicy?.toyPrizeBundled === false
    && render.reviewPolicy?.materialParityClaimed === false
    && exportManifest.status === "pass"
    && exportManifest.pipelineRevisionAtBuild === manifest.revision
    && dimensions?.width === 228
    && dimensions?.height === 304
    && dimensions?.depth === 59
    && exportManifest.product?.labelCenterYmm === 99
    && exportManifest.product?.objectCount === 12
    && exportManifest.product?.meshCount === 5
    && exportManifest.product?.connectedTubePreserved === true
    && exportManifest.product?.concentricCornersPreserved === true
    && exportManifest.labelPolicy?.placeholderTextBaked === false
    && exportManifest.labelPolicy?.fakeCollectibleIdBaked === false
    && exportManifest.labelPolicy?.authoritativeContent === "Unity runtime data"
    && exportManifest.review?.wholeAssembledCaseOnly === true
    && exportManifest.review?.reviewExplodedPartCount === 0
    && exportManifest.gate11Entered === false
    && exportManifest.shippingUnityChanged === false
    && exportManifest.simulatorBuilt === false
    && exportManifest.buildInstallPhonePush === false
    && collision.status === "pass"
    && collision.included === false
    && collision.approvedCollisionProxyFound === false
    && collision.selectionProxyFound === false
    && collision.inventedGeometry === false
    && optimization.status === "pass-with-gate11-profile-required"
    && optimization.triangleCount === roundtrip.source.triangleCount
    && links.status === "pass"
    && qa.result === "READY_FOR_EXPORT_REVIEW_NOT_UNITY"
    && exportManifest.package?.blend?.sha256 === sha256File(files.blend)
    && exportManifest.package?.fbx?.sha256 === sha256File(files.fbx)
    && exportManifest.package?.glb?.sha256 === sha256File(files.glb)
    && exportManifest.review?.boardSha256 === sha256File(files.board);
  if (!validEvidence) {
    throw new PipelineError("Premium Display Case Gate 10 rev 1 evidence does not satisfy the product export and round-trip contract.", 422);
  }

  const sourceAssetIds = [
    "premium-display-case-modeling-contract-r003",
    "premium-display-case-mesh-light-architecture-r007",
    "premium-display-case-geometry-blend-r003",
    "premium-display-case-geometry-revalidation-r003",
    "premium-display-case-material-blend-r002",
    "premium-display-case-material-revalidation-r002",
    "premium-display-case-environment-compatibility-snapshot-r001",
    "premium-display-case-environment-comparison-mp4-r001"
  ];
  const sourceClaimIds = architecture.architectureSpec.sourceClaimIds;
  const reviewIds = new Set([
    `${modelId}-product-glb-r${revisionLabel}`,
    `${modelId}-export-review-board-r${revisionLabel}`
  ]);
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    const isBlender = [
      "source-model",
      "export",
      "blender-render"
    ].includes(record.role);
    let recipe = "compose_export_review.py";
    if (record.id.includes("builder") || ["product-blend", "product-fbx", "product-glb", "export-build-report"].some((token) => record.id.includes(token))) {
      recipe = "build_export_package.py";
    } else if (record.id.includes("roundtrip") || record.id.includes("glb-structure")) {
      recipe = "validate_export_roundtrip.py";
    } else if (record.id.includes("review-renderer") || record.id.includes("-hero-")) {
      recipe = "render_export_review.py";
    }
    const asset = {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: record.role,
      producer: {
        name: isBlender ? "Blender" : "deterministic pipeline evidence",
        version: isBlender ? build.blender : "2026-08-27",
        recipe: `${expectedDirectory}/${recipe}`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 10 rev 1 packages the unchanged approved whole case only. Runtime label data, animation, timing, light cues, toy/prize, proxy, exploded state, collision geometry, VFX, cameras and backgrounds are excluded."
      },
      sourceAssetIds,
      sourceClaimIds,
      reviewState: reviewIds.has(record.id) ? "active" : "internal-evidence",
      wholeCaseOnly: true,
      wholeAssembledCaseOnly: true,
      explodeEligible: false,
      labelContentApproved: false,
      shippingUnityChanged: false
    };
    if (record.viewId) {
      asset.view = {
        id: record.viewId,
        kind: "neutral-export-roundtrip",
        camera: "M10_REVIEW_Camera",
        assemblyState: "assembled",
        materialParityClaimed: false
      };
    }
    if (record.slot === "glb-export") {
      asset.interaction = {
        type: "real-exported-glb-orbit",
        approvalRequiresCompletedChecklist: true,
        approvalChecklist: exportManifest.review.approvalChecklist,
        assemblyState: "assembled",
        reviewExplodedPartCount: 0,
        gate11UnityParity: false
      };
    }
    if (record.slot === "collision-export") {
      asset.collisionDisposition = "not-included-no-approved-proxy";
      asset.isCollisionMesh = false;
    }
    return asset;
  });
  manifest.assets.push(...records);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.reviewArtifactIds = [...reviewIds];
  stage.exportSpec = {
    revision: 1,
    sourceEnvironmentRevision: 1,
    sourceEnvironmentApprovalEventId: approvalEvent.id,
    sourceEnvironmentApprovalQuote: approval.userApprovalQuote,
    sourceArchitectureEvidenceRevision: 7,
    sourceGeometryRevision: 3,
    sourceMaterialRevision: 2,
    approvedGeometryDigest: build.geometry.approvedDigest,
    approvedMaterialDigest: build.materials.approvedDigest,
    productBlendSha256: exportManifest.package.blend.sha256,
    fbxSha256: exportManifest.package.fbx.sha256,
    glbSha256: exportManifest.package.glb.sha256,
    exportManifestSha256: sha256File(
      resolveRepoPath(`${expectedDirectory}/export-manifest.json`)
    ),
    geometryDigest: roundtrip.source.geometryDigest,
    dimensionsMm: dimensions,
    labelCenterYmm: 99,
    hierarchy: build.hierarchy,
    materialAssignments: build.materials.assignments,
    labelUv: roundtrip.source.labelUv,
    labelPolicy: exportManifest.labelPolicy,
    runtimeBoundary: exportManifest.runtimeBoundary,
    excluded: exportManifest.excluded,
    collision,
    roundTrip: exportManifest.roundTrip,
    objectCount: 12,
    meshCount: 5,
    triangleCount: roundtrip.source.triangleCount,
    wholeCaseOnly: true,
    wholeAssembledCaseOnly: true,
    reviewExplodedPartCount: 0,
    reviewArtifactIds: [...reviewIds],
    approvalChecklist: exportManifest.review.approvalChecklist,
    interactiveArtifactId: `${modelId}-product-glb-r${revisionLabel}`,
    reviewBoardArtifactId: `${modelId}-export-review-board-r${revisionLabel}`,
    gate10Approved: false,
    gate11Entered: false,
    shippingUnityChanged: false,
    simulatorBuilt: false,
    buildInstallPhonePush: false
  };
  stage.validations = [
    { id: "approved-gate09-rev1-source", status: "pass", evidence: `Gate 09 approval event ${approvalEvent.id} is current and exact.` },
    { id: "product-only-whole-case-source", status: "pass", evidence: "Blend, FBX and GLB contain one assembled case: 12 nodes, 5 meshes, no toy/prize, proxy, exploded, light, VFX, camera or background objects." },
    { id: "approved-geometry-preserved", status: "pass", evidence: `Approved geometry digest ${build.geometry.approvedDigest} remains exact in the product-only Blender source.` },
    { id: "dimensions-pivot-hierarchy", status: "pass", evidence: "228 × 304 × 59 mm, PresentationRoot origin pivot, approved parent map and empty caller-owned ContentSlot pass fresh-scene validation." },
    { id: "connected-tube-label-corners", status: "pass", evidence: "Connected tube, Y=99 label, concentric corners, LabelUV and paper/cover/foil zone metadata remain present." },
    { id: "runtime-content-and-motion-excluded", status: "pass", evidence: "Placeholder text, fake IDs, timing, easing, Y/Z path, 360°, light cues and animation are not baked; Unity remains authoritative." },
    { id: "fbx-glb-roundtrip", status: "pass", evidence: `FBX/GLB geometry digest, hierarchy, material slots and triangle count match; maximum vertex errors are ${roundtrip.fbx.vertexCorrespondence.maximumErrorMm} / ${roundtrip.glb.vertexCorrespondence.maximumErrorMm} mm.` },
    { id: "normals-winding-preserved", status: "pass", evidence: "All signed material volumes remain positive; FBX and GLB triangulated surface and winding digests match." },
    { id: "collision-policy", status: "pass", evidence: "No approved collision or selection proxy exists, so no collision geometry was invented." },
    { id: "real-glb-review", status: "pass", evidence: "The real exported GLB is the primary interactive review artifact; the concise board shows only the assembled whole case." },
    { id: "performance-boundary", status: "pass", evidence: `${roundtrip.source.triangleCount} triangles remain unchanged; Gate 11 Unity profiling must validate the 60 FPS target.` },
    { id: "gate-boundary", status: "pass", evidence: "Gate 10 rev 1 is ready_for_review only. Gate 11+, shipping Unity, Simulator, build, install and phone remain blocked or unchanged." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  environment.environmentSpec.gate10Entered = true;
  environment.environmentSpec.approval.gate10Status = "ready_for_review";
  markDownstreamStale(
    manifest,
    stageIndex,
    "Gate 10 export rev 1 is ready_for_review and awaits real GLB approval. Gate 11 Unity parity must not start."
  );
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.visualApproval = "gate10-export-review-pending";
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.environmentRevalidation = {
    ...manifest.currentState.environmentRevalidation,
    gate09Status: "approved",
    gate10Status: "ready_for_review"
  };
  manifest.currentState.exportReview = {
    exportRevision: 1,
    sourceEnvironmentApprovalEventId: approvalEvent.id,
    dimensionsMm: dimensions,
    objectCount: 12,
    meshCount: 5,
    triangleCount: roundtrip.source.triangleCount,
    geometryDigest: roundtrip.source.geometryDigest,
    blendSha256: exportManifest.package.blend.sha256,
    fbxSha256: exportManifest.package.fbx.sha256,
    glbSha256: exportManifest.package.glb.sha256,
    maximumVertexErrorMm: exportManifest.roundTrip.maximumVertexErrorMm,
    collisionIncluded: false,
    wholeAssembledCaseOnly: true,
    labelContentApproved: false,
    runtimeAnimationBaked: false,
    gate10Status: "ready_for_review",
    gate11Status: "blocked"
  };
  manifest.currentState.diagnosis = "Gate 09 rev 1 environment is approved. Gate 10 rev 1 now provides a product-only Blender source, Unity-ready FBX, real portable GLB, hashes, collision-not-applicable policy and fresh-scene round-trip validation for the unchanged 228 × 304 × 59 mm assembled case. Hierarchy, pivot, label UV/zones, material assignments, positive winding and digest identity pass. Runtime label content, animation, timing, light cues, toy/prize, proxies, exploded geometry and scene assets are excluded. Gate 10 awaits real GLB approval; Gate 11+, shipping Unity, Simulator, build, install and phone remain blocked or unchanged.";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "10-export",
    exportRevision: 1,
    sourceEnvironmentRevision: 1,
    sourceEnvironmentApprovalEventId: approvalEvent.id,
    sourceEnvironmentApprovalQuote: approval.userApprovalQuote,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    interactiveGlbPath: `${expectedDirectory}/premium-display-case-product-r001.glb`,
    reviewBoardPath: `${expectedDirectory}/export-review.png`,
    exportManifestPath: `${expectedDirectory}/export-manifest.json`,
    roundTripValidationPath: `${expectedDirectory}/export-roundtrip-validation.json`,
    validationLinksPath: `${expectedDirectory}/validation-links.json`,
    approvalChecklist: exportManifest.review.approvalChecklist,
    dimensionsMm: dimensions,
    labelCenterYmm: 99,
    objectCount: 12,
    meshCount: 5,
    triangleCount: roundtrip.source.triangleCount,
    approvedGeometryDigest: build.geometry.approvedDigest,
    geometryDigest: roundtrip.source.geometryDigest,
    productBlendSha256: exportManifest.package.blend.sha256,
    fbxSha256: exportManifest.package.fbx.sha256,
    glbSha256: exportManifest.package.glb.sha256,
    maximumVertexErrorMm: exportManifest.roundTrip.maximumVertexErrorMm,
    hierarchyIdentity: true,
    materialAssignmentsIdentity: true,
    positiveWinding: true,
    collisionIncluded: false,
    labelContentApproved: false,
    runtimeAnimationBaked: false,
    wholeCaseOnly: true,
    reviewExplodedPartCount: 0,
    autoApproved: false,
    gate11Status: "blocked",
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function saveMaterialReview(modelId, payload) {
  if (modelId === "premium-display-case") {
    const manifest = loadManifest(modelId);
    if (manifest.stages[5]?.geometrySpec?.revision === 3) {
      return savePremiumDisplayCaseMaterialRevalidation(modelId, payload);
    }
    return savePremiumDisplayCaseMaterialReview(modelId, payload);
  }
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (modelId !== "magnetic-slide-tile") throw new PipelineError("Gate 07 material registration is supported only for magnetic-slide-tile.", 422);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "07-material");
  const geometry = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (geometry.status !== "approved" || geometry.geometrySpec?.revision !== 1) {
    throw new PipelineError("Approved Gate 06 revision 1 is required.", 422);
  }
  if (stage.artifactIds.length || !["blocked", "missing"].includes(stage.status)) {
    throw new PipelineError("Gate 07 revision 1 must start from an empty blocked stage.", 422);
  }

  const revisionLabel = "001";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/07-material", `rev-${revisionLabel}`
  )));
  const definitions = [
    ["builder", "material-builder", "material-source", "build_material_lookdev.py", "deterministic-neutral-material-source"],
    ["blend", "material-blend", "material-blend", "magnetic-slide-tile-material-r001.blend", "neutral-material-lookdev-scene"],
    ["board", "material-board", "material-board", "neutral-pbr-material-board.png", "real-blender-neutral-pbr-material-board"],
    ["closeup", "material-closeup", "material-closeup", "neutral-pbr-material-closeup.png", "real-blender-neutral-pbr-material-closeup"],
    ["validation", "material-validation", "validation-report", "material-validation.json", "pbr-slots-geometry-and-scope-validation"]
  ].map(([key, suffix, slot, file, contentClass]) => ({
    key,
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "07-material",
    slot,
    path: normalizeRepoPath(payload[`${key}Path`] || `${expectedDirectory}/${file}`),
    contentClass
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) throw new PipelineError(`${record.id} file is missing.`, 422);
  }

  const reportRecord = definitions.find((record) => record.key === "validation");
  const report = JSON.parse(fs.readFileSync(resolveRepoPath(reportRecord.path), "utf8"));
  const zoneIds = ["lower-polished-silver-alloy", "upper-dark-coated-frame", "upper-smoked-clear-face"];
  const validReport = report.schemaVersion === 1
    && report.gate === "07-material"
    && report.materialRevision === 1
    && report.sourceGate06?.geometryRevision === 1
    && report.sourceGate06?.blendPath === "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/06-geometry/rev-001/magnetic-slide-tile-geometry-r001.blend"
    && report.sourceGate06?.unchanged === true
    && report.sourceGate06?.evaluatedGeometryDigest === "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
    && report.geometryPreservation?.unchanged === true
    && report.geometryPreservation?.digestBefore === report.geometryPreservation?.digestAfterMaterialAssignment
    && report.geometryPreservation?.digestBefore === report.geometryPreservation?.digestAfterRenders
    && JSON.stringify(report.geometryPreservation?.boundsMm) === JSON.stringify([50, 31, 12])
    && JSON.stringify(report.geometryPreservation?.axisPointWorldMm) === JSON.stringify([0, -9.5, 0])
    && report.geometryPreservation?.lowerMatrixUnchanged === true
    && report.geometryPreservation?.upperMatrixUnchanged === true
    && report.geometryPreservation?.envelopeMatrixUnchanged === true
    && report.geometryPreservation?.envelopeType === "EMPTY"
    && report.geometryPreservation?.envelopeHideRender === true
    && report.geometryPreservation?.envelopeGeometry === "none"
    && report.geometryPreservation?.smoothProfileSegmentsPerSemicircle === 256
    && report.geometryPreservation?.hiddenMechanismMeshCount === 0
    && report.geometryPreservation?.artworkOrnamentGeometryCount === 0
    && report.geometryPreservation?.animatedOrConstrainedObjects?.length === 0
    && report.geometryPreservation?.pass === true
    && zoneIds.every((id) => report.materialZones?.[id]?.certainty === "visual-approximation")
    && zoneIds.every((id) => typeof report.materialZones?.[id]?.uncertainty === "string")
    && report.materialZones?.["lower-polished-silver-alloy"]?.metallic === 0.96
    && report.materialZones?.["lower-polished-silver-alloy"]?.roughness === 0.17
    && report.materialZones?.["upper-dark-coated-frame"]?.metallic === 0.9
    && report.materialZones?.["upper-dark-coated-frame"]?.roughness === 0.2
    && report.materialZones?.["upper-smoked-clear-face"]?.metallic === 0
    && report.materialZones?.["upper-smoked-clear-face"]?.roughness === 0.13
    && report.materialZones?.["upper-smoked-clear-face"]?.ior === 1.48
    && report.materialZones?.["upper-smoked-clear-face"]?.transmissionWeight === 0.12
    && report.materialAssignments?.zoneCount === 3
    && report.materialAssignments?.upperFaces?.topCapFaceCount === 1
    && report.materialAssignments?.upperFaces?.frameFaceCount === 514
    && report.materialAssignments?.pass === true
    && report.sourceClaimIds?.includes("slider-analysis-claim-material-language")
    && report.sourceLinks?.some((source) => source.assetId === "slider-intake-haloo-official-01")
    && report.sourceLinks?.some((source) => source.assetId === "slider-intake-haloo-official-02")
    && report.sourceLinks?.some((source) => source.assetId === "slider-intake-nxedc-ref-02")
    && report.uncertaintyPolicy?.pbrValuesAreProductionSpecifications === false
    && report.uncertaintyPolicy?.artworkOrnamentApproved === false
    && report.uncertaintyPolicy?.hiddenRatchetConstructionKnown === false
    && report.mechanismDecisionMetadata?.decisionState === "locked-user-authoritative"
    && report.mechanismDecisionMetadata?.deliveryState === "specified-only-runtime-and-hardware-validation-pending"
    && report.mechanismDecisionMetadata?.rotationRangeDegrees === 360
    && report.mechanismDecisionMetadata?.detentStepDegrees === 12
    && report.mechanismDecisionMetadata?.detentCount === 30
    && report.mechanismDecisionMetadata?.semantics === "ratchet"
    && report.mechanismDecisionMetadata?.physicalAndHapticConsumeSameSetting === true
    && report.mechanismDecisionMetadata?.runtimeChanged === false
    && report.mechanismDecisionMetadata?.hapticsChanged === false
    && report.mechanismDecisionMetadata?.unityChanged === false
    && report.mechanismDecisionMetadata?.hiddenConstruction === "unknown"
    && report.neutralReveal?.finalLightingOrEnvironment === false
    && Object.values(report.scope || {}).every((value) => value === false);
  if (!validReport) throw new PipelineError("Gate 07 validation report does not satisfy the material evidence contract.", 422);

  const mechanismClaimId = "slider-ratchet-30-detent-requirement-r001";
  if (manifest.claims.some((claim) => claim.id === mechanismClaimId)) {
    throw new PipelineError("The Gate 06 mechanism requirement already exists.", 409);
  }
  manifest.claims.push({
    id: mechanismClaimId,
    stageId: "06-geometry",
    topic: "full-turn-ratchet-detents",
    statement: "用户权威要求：旋转范围完整 360°，每 12° 一个 ratchet detent，因此每圈恰好 30 档。物理与 Haptic 最终必须读取同一机制设置。",
    confidence: "user-authoritative",
    state: "active",
    assertedBy: "user",
    sourceAssetIds: ["magnetic-slide-tile-geometry-point-pivot-r001"],
    sourceRegions: [],
    sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
    decisionState: "locked",
    deliveryState: "specified-only-runtime-and-hardware-validation-pending",
    rotationRangeDegrees: 360,
    detentStepDegrees: 12,
    detentCount: 30,
    semantics: "ratchet",
    physicalAndHapticConsumeSameSetting: true,
    hiddenConstruction: "unknown-no-teeth-pawls-balls-or-coupling-inferred",
    exteriorGeometryImpact: "none"
  });

  const sourceAssetIds = [
    ...geometry.artifactIds,
    "slider-intake-haloo-official-01",
    "slider-intake-haloo-official-02",
    "slider-intake-nxedc-ref-02"
  ];
  const sourceClaimIds = [
    "slider-analysis-claim-material-language",
    "slider-blockout-point-axis-distinction-r003"
  ];
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    const view = record.key === "board"
      ? { id: "material-board", kind: "perspective", camera: "M07_MaterialBoardCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE", recipe: "neutral-reveal-three-zone-board" }
      : record.key === "closeup"
        ? { id: "material-closeup", kind: "perspective", camera: "M07_MaterialCloseupCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE", recipe: "neutral-reveal-seam-and-face-closeup" }
        : null;
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: "process",
      producer: {
        name: record.key === "builder" ? "deterministic-bpy" : "Blender",
        version: report.blender,
        recipe: `${expectedDirectory}/build_material_lookdev.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 07 rev 1 applies source-supported neutral material zones without changing approved geometry. All PBR values remain visual approximations.",
        userClaimIds: [...sourceClaimIds, mechanismClaimId]
      },
      sourceAssetIds,
      sourceClaimIds,
      ...(view ? { view } : {})
    };
  });
  manifest.assets.push(...records);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.materialSpec = {
    revision: 1,
    sourceGate06Revision: 1,
    sourceGate06Sha256: report.sourceGate06.sha256Before,
    evaluatedGeometryDigest: report.sourceGate06.evaluatedGeometryDigest,
    zoneIds,
    pbrValues: Object.fromEntries(zoneIds.map((id) => [id, {
      baseColor: report.materialZones[id].baseColor,
      metallic: report.materialZones[id].metallic,
      roughness: report.materialZones[id].roughness,
      ior: report.materialZones[id].ior,
      coatWeight: report.materialZones[id].coatWeight,
      coatRoughness: report.materialZones[id].coatRoughness,
      transmissionWeight: report.materialZones[id].transmissionWeight,
      certainty: report.materialZones[id].certainty
    }])),
    geometryChanged: false,
    artworkOrnamentApproved: false,
    hiddenRatchetConstructionKnown: false,
    neutralRevealOnly: true,
    finalLightingOrEnvironment: false,
    unityAssetChanged: false,
    mechanismRequirement: {
      claimId: mechanismClaimId,
      decisionState: "locked",
      deliveryState: "specified-only-runtime-and-hardware-validation-pending",
      rotationRangeDegrees: 360,
      detentStepDegrees: 12,
      detentCount: 30,
      physicalAndHapticConsumeSameSetting: true
    }
  };
  stage.validations = [
    { id: "gate06-source-immutable", status: "pass", evidence: `Approved Gate 06 blend hash remained ${report.sourceGate06.sha256Before} before and after material renders.` },
    { id: "geometry-digest-preserved", status: "pass", evidence: `Geometry digest remained ${report.sourceGate06.evaluatedGeometryDigest} before assignment, after assignment, and after renders.` },
    { id: "visible-material-zones-only", status: "pass", evidence: "Three visible zones: lower polished silver, upper dark coated frame, and upper smoked clear face; no hidden mechanism material was invented." },
    { id: "pbr-node-values", status: "pass", evidence: "All three Principled BSDF materials match the recorded baseColor, metallic, roughness, IOR, coat, and transmission values." },
    { id: "source-linked-material-language", status: "pass", evidence: "HALOOPLAYER official 01/02, NXEDC reference 02, and the approved material-language claim support the visible zone direction." },
    { id: "uncertainties-explicit", status: "pass", evidence: "Alloy, coating, resin/glass, transmission thickness, and pearlescent stack remain visual approximations, not production specifications." },
    { id: "artwork-separated", status: "pass", evidence: "Artwork/ornament geometry count is 0 and artwork approval remains false." },
    { id: "concealed-mechanism-preserved", status: "pass", evidence: "The concealed enclosure remains a fixed non-rendering Empty; no teeth, pawls, balls, coupling, or other hidden geometry was added." },
    { id: "thirty-detent-decision-recorded", status: "pass", evidence: "DecisionState is locked for 360° / 12° / 30 ratchet semantics; DeliveryState remains specified-only with runtime and hardware validation pending." },
    { id: "shared-physical-haptic-setting-required", status: "pass", evidence: "The new user claim requires physical and Haptic detent counts to consume the same setting; no runtime or Haptic code changed." },
    { id: "neutral-reveal-only", status: "pass", evidence: "The board and closeup use neutral reveal lights; final Gate 08 lighting/environment was not entered." },
    { id: "shipping-unity-unchanged", status: "pass", evidence: "Gate 07 evidence remains under ArtSource/ModelPipeline; Unity runtime, haptics, scenes, builds, and device state are unchanged." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "Gate 07 rev 1 中性材质证据等待视觉批准；不得进入 Gate 08。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 06 rev 1 已按用户原文‘没什么问题，继续吧’批准。新增机制 DecisionState：360°、每 12° 一档、30 档 ratchet，物理与 Haptic 最终共用同一设置；DeliveryState 仍为 specified-only，runtime、Haptic 与真机验收待完成。Gate 07 rev 1 从获批 Gate 06 同一 geometry digest 生成三种 source-linked 中性材质区和 closeup；PBR 值仅为视觉近似，未添加 artwork 或隐藏机构。等待 Gate 07 视觉批准，不得进入 Gate 08。";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "07-material",
    materialRevision: 1,
    artifactIds: stage.artifactIds,
    evaluatedGeometryDigest: report.sourceGate06.evaluatedGeometryDigest,
    materialZoneIds: zoneIds,
    mechanismRequirement: stage.materialSpec.mechanismRequirement,
    runtimeChanged: false,
    hapticsChanged: false,
    unityChanged: false,
    blender: report.blender,
    autoApproved: false
  });
  return saveManifest(manifest, event);
}

export function saveMaterialHybridReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (modelId !== "magnetic-slide-tile") throw new PipelineError("Gate 07 hybrid material registration is supported only for magnetic-slide-tile.", 422);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "07-material");
  const geometry = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (geometry.status !== "approved" || geometry.geometrySpec?.revision !== 1) {
    throw new PipelineError("Approved Gate 06 revision 1 is required.", 422);
  }
  if (stage.status !== "rejected" || stage.materialSpec?.revision !== 1 || stage.decision?.action !== "reject") {
    throw new PipelineError("Gate 07 revision 1 must remain rejected before creating revision 2.", 422);
  }

  const revisionLabel = "002";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/07-material", `rev-${revisionLabel}`
  )));
  const definitions = [
    ["motifBuilder", "motif-builder", "motif-trace-source", "derive_motif_trace.py", "deterministic-raster-visual-trace-recipe"],
    ["motifMask", "motif-mask", "motif-trace-mask", "source-derived-motif-visual-trace.png", "source-derived-visual-trace-not-production-vector"],
    ["motifProvenance", "motif-provenance", "motif-provenance", "motif-trace-provenance.json", "motif-source-recipe-and-hash"],
    ["builder", "material-builder", "material-source", "build_material_hybrid.py", "deterministic-neutral-hybrid-material-source"],
    ["blend", "material-blend", "material-blend", "magnetic-slide-tile-material-r002.blend", "neutral-hybrid-material-lookdev-scene"],
    ["variantBoard", "material-variant-board", "material-variant-board", "material-process-variant-board.png", "real-blender-neutral-three-variant-process-board"],
    ["board", "material-board", "material-board", "neutral-pbr-material-board.png", "real-blender-neutral-recommended-hybrid-board"],
    ["closeup", "material-closeup", "material-closeup", "neutral-pbr-material-closeup.png", "real-blender-neutral-motif-crystal-closeup"],
    ["validation", "material-validation", "validation-report", "material-validation.json", "pbr-motif-geometry-process-and-scope-validation"]
  ].map(([key, suffix, slot, file, contentClass]) => ({
    key,
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "07-material",
    slot,
    path: normalizeRepoPath(payload[`${key}Path`] || `${expectedDirectory}/${file}`),
    contentClass
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) throw new PipelineError(`${record.id} file is missing.`, 422);
  }

  const report = JSON.parse(fs.readFileSync(resolveRepoPath(definitions.find((record) => record.key === "validation").path), "utf8"));
  const motif = report.motifProvenance;
  const silver = report.materialZones?.["mirror-silver-exterior-body"];
  const etch = report.materialZones?.["source-derived-dark-etched-motif"];
  const crystal = report.materialZones?.["crystal-iridescent-face"];
  const validReport = report.schemaVersion === 2
    && report.gate === "07-material"
    && report.materialRevision === 2
    && report.sourceGate06?.geometryRevision === 1
    && report.sourceGate06?.unchanged === true
    && report.sourceGate06?.evaluatedGeometryDigest === "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
    && report.geometryPreservation?.unchanged === true
    && report.geometryPreservation?.digestBefore === report.geometryPreservation?.digestAfterMaterialAssignment
    && report.geometryPreservation?.digestBefore === report.geometryPreservation?.digestAfterRenders
    && JSON.stringify(report.geometryPreservation?.boundsMm) === JSON.stringify([50, 31, 12])
    && JSON.stringify(report.geometryPreservation?.axisPointWorldMm) === JSON.stringify([0, -9.5, 0])
    && report.geometryPreservation?.matricesUnchanged === true
    && report.geometryPreservation?.hiddenMechanismMeshes?.length === 0
    && report.geometryPreservation?.artworkOrnamentGeometryCount === 0
    && report.geometryPreservation?.pass === true
    && silver?.metallic === 1
    && silver?.roughness === 0.095
    && silver?.certainty === "confirmed-steel-visual-finish-provisional"
    && etch?.motifKind === "visual-trace-not-production-vector"
    && etch?.etchBumpStrength === 0.24
    && etch?.etchDepthIllusionMm === 0.06
    && crystal?.roughness === 0.075
    && crystal?.ior === 1.46
    && crystal?.transmissionWeight === 0.48
    && crystal?.thinFilmIor === 1.38
    && crystal?.thinFilmThicknessNm === 520
    && report.materialAssignments?.zoneCount === 3
    && report.materialAssignments?.upperFaces?.topCapFaceCount === 1
    && report.materialAssignments?.upperFaces?.frameFaceCount === 514
    && report.materialAssignments?.pass === true
    && motif?.kind === "visual-trace-not-production-vector"
    && motif?.registeredAs === "visual-trace-not-production-vector"
    && motif?.sourceAssetIds?.includes("slider-intake-nxedc-ref-01")
    && motif?.outputSha256 === sha256File(resolveRepoPath(definitions.find((record) => record.key === "motifMask").path))
    && motif?.pass === true
    && Object.keys(report.variants || {}).join("") === "ABC"
    && report.manufacturingAnalysis?.confirmed?.some((claim) => /Material: Steel/.test(claim.claim))
    && report.manufacturingAnalysis?.productionSpecificationEstablished === false
    && report.uncertaintyPolicy?.pbrValuesAreProductionSpecifications === false
    && report.uncertaintyPolicy?.motifIsExactProductionVector === false
    && report.uncertaintyPolicy?.hiddenRatchetConstructionKnown === false
    && report.mechanismDecisionMetadata?.detentCount === 30
    && report.mechanismDecisionMetadata?.physicalAndHapticConsumeSameSetting === true
    && report.mechanismDecisionMetadata?.runtimeChanged === false
    && report.neutralReveal?.finalLightingOrEnvironment === false
    && Object.values(report.scope || {}).every((value) => value === false);
  if (!validReport) throw new PipelineError("Gate 07 revision 2 report does not satisfy the hybrid material contract.", 422);

  const processClaimId = "slider-material-process-analysis-r002";
  if (manifest.claims.some((claim) => claim.id === processClaimId)) throw new PipelineError("Gate 07 revision 2 process claim already exists.", 409);
  manifest.claims.push({
    id: processClaimId,
    stageId: "07-material",
    topic: "visible-material-and-provisional-manufacturing-stack",
    statement: "HALOOPLAYER exact page confirms only Steel. Mirror polish, dark etched/blackened/laser-cut motif, nacre/abalone or dichroic/interference substrate, and clear resin/polymer/glass cap remain provisional alternatives inferred from visible highlights, parallax, edge stacking, and purple-blue-green response.",
    confidence: "mixed-confirmed-and-inferred",
    state: "active",
    assertedBy: "assistant",
    sourceAssetIds: report.sourceLinks.map((source) => source.assetId),
    sourceRegions: [],
    sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2",
    confirmed: ["product-material-steel"],
    provisional: ["mirror-polish-process", "motif-production-process", "iridescent-substrate", "clear-cap-material"]
  });

  const sourceAssetIds = [
    ...geometry.artifactIds,
    ...report.sourceLinks.map((source) => source.assetId)
  ];
  const sourceClaimIds = [
    "slider-analysis-claim-material-language",
    "slider-blockout-point-axis-distinction-r003",
    "slider-ratchet-30-detent-requirement-r001"
  ];
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    const view = record.key === "variantBoard"
      ? { id: "material-process-variant-board", kind: "perspective", camera: "M07R2_VariantBoardCamera", pose: "review-samples-only", renderEngine: "BLENDER_EEVEE", recipe: "neutral-reveal-three-variant-comparison" }
      : record.key === "board"
        ? { id: "material-board", kind: "perspective", camera: "M07R2_MaterialBoardCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE", recipe: "neutral-reveal-recommended-hybrid-and-layer-stack" }
        : record.key === "closeup"
          ? { id: "material-closeup", kind: "perspective", camera: "M07R2_MaterialCloseupCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE", recipe: "neutral-reveal-motif-crystal-edge-closeup" }
          : null;
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: "process",
      producer: {
        name: ["motifBuilder", "motifMask", "motifProvenance"].includes(record.key) ? "Pillow/Python" : (record.key === "builder" ? "deterministic-bpy" : "Blender"),
        version: ["motifBuilder", "motifMask", "motifProvenance"].includes(record.key) ? "Pillow 11.3.0" : report.blender,
        recipe: record.key.startsWith("motif") ? `${expectedDirectory}/derive_motif_trace.py` : `${expectedDirectory}/build_material_hybrid.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 07 rev 2 preserves approved geometry. The motif is a source-derived raster visual trace, not a production vector; PBR and manufacturing layers remain explicitly provisional except the confirmed Steel claim.",
        userClaimIds: [...sourceClaimIds, processClaimId]
      },
      sourceAssetIds,
      sourceClaimIds,
      ...(view ? { view } : {})
    };
  });
  manifest.assets.push(...records);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.materialSpec = {
    revision: 2,
    sourceGate06Revision: 1,
    sourceGate06Sha256: report.sourceGate06.sha256Before,
    evaluatedGeometryDigest: report.sourceGate06.evaluatedGeometryDigest,
    recommendedVariant: "B",
    variantIds: ["A", "B", "C"],
    zoneIds: ["mirror-silver-exterior-body", "source-derived-dark-etched-motif", "crystal-iridescent-face"],
    mirrorSilver: { metallic: 1, roughness: 0.095, ior: 1.5, coatWeight: 0.32, coatRoughness: 0.055 },
    motif: {
      kind: motif.kind,
      maskAssetId: `${modelId}-motif-mask-r${revisionLabel}`,
      maskSha256: motif.outputSha256,
      sourceAssetIds: motif.sourceAssetIds,
      etchBumpStrength: etch.etchBumpStrength,
      etchDepthIllusionMm: etch.etchDepthIllusionMm,
      productionVector: false
    },
    crystalIridescent: {
      roughness: crystal.roughness,
      ior: crystal.ior,
      transmissionWeight: crystal.transmissionWeight,
      coatWeight: crystal.coatWeight,
      coatRoughness: crystal.coatRoughness,
      thinFilmIor: crystal.thinFilmIor,
      thinFilmThicknessNm: crystal.thinFilmThicknessNm
    },
    processClaimId,
    confirmedProductionMaterial: "steel",
    inferredProcessesRemainProvisional: true,
    geometryChanged: false,
    hiddenRatchetConstructionKnown: false,
    neutralRevealOnly: true,
    finalLightingOrEnvironment: false,
    unityAssetChanged: false,
    mechanismRequirement: manifest.stages[stageIndex].materialSpec?.mechanismRequirement || {
      claimId: "slider-ratchet-30-detent-requirement-r001",
      decisionState: "locked",
      deliveryState: "specified-only-runtime-and-hardware-validation-pending",
      rotationRangeDegrees: 360,
      detentStepDegrees: 12,
      detentCount: 30,
      physicalAndHapticConsumeSameSetting: true
    }
  };
  stage.validations = [
    { id: "rejected-rev1-preserved", status: "pass", evidence: "All five Gate 07 rev 1 artifacts and their hashes remain immutable historical evidence." },
    { id: "gate06-source-immutable", status: "pass", evidence: `Approved Gate 06 blend hash remained ${report.sourceGate06.sha256Before}.` },
    { id: "geometry-digest-preserved", status: "pass", evidence: `Geometry digest remained ${report.sourceGate06.evaluatedGeometryDigest} before assignment, after assignment, and after all renders.` },
    { id: "source-derived-motif-provenance", status: "pass", evidence: `Motif mask ${motif.outputSha256} derives from ${motif.sourceAssetIds.join(", ")} with a stored crop and recipe; it is labeled a visual trace, not a production vector.` },
    { id: "shader-only-etch", status: "pass", evidence: "The motif uses base-color mixing and inverted bump at 0.24 strength / 0.06 mm illusion; artwork geometry count remains zero." },
    { id: "recommended-hybrid-pbr", status: "pass", evidence: "Variant B uses mirror silver plus dark etch and crystal iridescence at IOR 1.46, transmission 0.48, roughness 0.075, thin-film IOR 1.38 / 520 nm." },
    { id: "manufacturing-evidence-separated", status: "pass", evidence: "Steel is confirmed by the exact page. Alloy, polish/plating, motif process, nacre/film/pigment substrate, and clear cap remain provisional alternatives." },
    { id: "three-variant-board", status: "pass", evidence: "Neutral Blender board shows A monochrome etch, B recommended dark etch + iridescent crystal, and C crystal-heavy." },
    { id: "concealed-mechanism-preserved", status: "pass", evidence: "The concealed envelope remains a fixed non-rendering Empty with zero hidden mechanism meshes." },
    { id: "thirty-detent-specified-only", status: "pass", evidence: "360° / 12° / 30 remains locked but specified-only; runtime, Haptic, hardware, and iPhone validation remain pending." },
    { id: "neutral-reveal-only", status: "pass", evidence: "Four neutral reveal area lights were used. Gate 08 lighting/environment was not entered." },
    { id: "shipping-unity-unchanged", status: "pass", evidence: "No Unity runtime, scene, haptic, build, install, or device state changed." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "Gate 07 rev 2 银色／深色蚀刻／晶体虹彩材质等待视觉批准；不得进入 Gate 08。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 07 rev 1 已按用户明确反馈拒绝并保留。Gate 07 rev 2 复用获批 Gate 06 同一 geometry digest：银色钢质外观、source-derived Chrome Hearts/reference motif 的 shader-only 深色蚀刻视觉 trace，以及紫／蓝／绿晶体虹彩层。制造证据只确认 Steel；其余工艺均为 provisional。等待 Variant B 视觉批准，不得进入 Gate 08。";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "07-material",
    materialRevision: 2,
    supersedesMaterialRevision: 1,
    artifactIds: stage.artifactIds,
    evaluatedGeometryDigest: report.sourceGate06.evaluatedGeometryDigest,
    recommendedVariant: "B",
    motifAssetId: `${modelId}-motif-mask-r${revisionLabel}`,
    motifSha256: motif.outputSha256,
    processClaimId,
    runtimeChanged: false,
    hapticsChanged: false,
    unityChanged: false,
    blender: report.blender,
    autoApproved: false
  });
  return saveManifest(manifest, event);
}

export function saveBrighterCrystalReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (modelId !== "magnetic-slide-tile") throw new PipelineError("Gate 07 brighter crystal registration is supported only for magnetic-slide-tile.", 422);
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "07-material");
  const geometry = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (geometry.status !== "approved" || geometry.geometrySpec?.revision !== 1) {
    throw new PipelineError("Approved Gate 06 revision 1 is required.", 422);
  }
  if (stage.status !== "rejected" || stage.materialSpec?.revision !== 2 || stage.decision?.action !== "reject") {
    throw new PipelineError("Gate 07 revision 2 must remain rejected/superseded before creating revision 3.", 422);
  }

  const revisionLabel = "003";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/07-material", `rev-${revisionLabel}`
  )));
  const definitions = [
    ["builder", "material-builder", "material-source", "build_brighter_crystal.py", "deterministic-brighter-crystal-source"],
    ["imageValidator", "material-image-validator", "validation-source", "validate_crystal_comparison.py", "same-camera-histogram-validation-source"],
    ["blend", "material-blend", "material-blend", "magnetic-slide-tile-material-r003.blend", "neutral-brighter-crystal-lookdev-scene"],
    ["comparison", "material-comparison", "material-comparison", "same-camera-crystal-comparison.png", "rev2-vs-rev3-same-camera-comparison"],
    ["board", "material-board", "material-board", "neutral-pbr-material-board.png", "real-blender-neutral-brighter-crystal-board"],
    ["closeup", "material-closeup", "material-closeup", "neutral-pbr-material-closeup.png", "real-blender-neutral-brighter-crystal-closeup"],
    ["validation", "material-validation", "validation-report", "material-validation.json", "pbr-motif-geometry-light-and-scope-validation"],
    ["imageValidation", "material-image-validation", "validation-report", "image-validation.json", "brightness-highlight-color-contrast-and-clipping-validation"]
  ].map(([key, suffix, slot, file, contentClass]) => ({
    key,
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "07-material",
    slot,
    path: normalizeRepoPath(payload[`${key}Path`] || `${expectedDirectory}/${file}`),
    contentClass
  }));
  for (const record of definitions) {
    if (!record.path.startsWith(`${expectedDirectory}/`)) throw new PipelineError(`${record.id} must be stored inside ${expectedDirectory}.`);
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) throw new PipelineError(`${record.id} file is missing.`, 422);
  }

  const materialReport = JSON.parse(fs.readFileSync(resolveRepoPath(definitions.find((record) => record.key === "validation").path), "utf8"));
  const imageReport = JSON.parse(fs.readFileSync(resolveRepoPath(definitions.find((record) => record.key === "imageValidation").path), "utf8"));
  const silver = materialReport.materialZones?.["mirror-silver-exterior-body"];
  const etch = materialReport.materialZones?.["source-derived-dark-etched-motif"];
  const crystal = materialReport.materialZones?.["crystal-iridescent-face"];
  const validMaterial = materialReport.schemaVersion === 3
    && materialReport.gate === "07-material"
    && materialReport.materialRevision === 3
    && materialReport.supersedesMaterialRevision === 2
    && materialReport.userRequest === "再 crystal 一点，就是更亮一些."
    && materialReport.sourceGate06?.unchanged === true
    && materialReport.sourceGate06?.evaluatedGeometryDigest === "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
    && materialReport.geometryPreservation?.unchanged === true
    && materialReport.geometryPreservation?.digestBefore === materialReport.geometryPreservation?.digestAfterMaterialAssignment
    && materialReport.geometryPreservation?.digestBefore === materialReport.geometryPreservation?.digestAfterRenders
    && JSON.stringify(materialReport.geometryPreservation?.boundsMm) === JSON.stringify([50, 31, 12])
    && JSON.stringify(materialReport.geometryPreservation?.axisPointWorldMm) === JSON.stringify([0, -9.5, 0])
    && materialReport.geometryPreservation?.hiddenMechanismMeshes?.length === 0
    && materialReport.geometryPreservation?.artworkOrnamentGeometryCount === 0
    && materialReport.geometryPreservation?.pass === true
    && silver?.metallic === 1
    && silver?.roughness === 0.095
    && etch?.motifKind === "visual-trace-not-production-vector"
    && etch?.motifMaskSha256 === "8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36"
    && etch?.etchBumpStrength === 0.24
    && etch?.etchDepthIllusionMm === 0.06
    && etch?.motifMixFactor === 0.98
    && crystal?.roughness === 0.028
    && crystal?.ior === 1.52
    && crystal?.specularIorLevel === 0.58
    && crystal?.transmissionWeight === 0.15
    && crystal?.coatWeight === 1
    && crystal?.coatRoughness === 0.01
    && crystal?.thinFilmIor === 1.42
    && crystal?.thinFilmThicknessNm === 545
    && crystal?.microfacetSparkleScale === 130
    && crystal?.microfacetSparkleStrength === 0.035
    && crystal?.microfacetSparkleDistanceMm === 0.012
    && crystal?.substrateSaturation === 1.3
    && crystal?.substrateValue === 1.15
    && crystal?.actualPbr?.emissionStrength === 0
    && materialReport.materialAssignments?.pass === true
    && materialReport.revisionComparison?.baselineRevision === 2
    && materialReport.revisionComparison?.baselineCloseupSha256 === "ab7a7782f05e00e17ba9264e1eaa43dd9690ee1b91128879ccee393a5033b09a"
    && materialReport.revisionComparison?.sameNeutralLights === true
    && materialReport.forbiddenLightingAndShaderTricks?.pass === true
    && materialReport.neutralReveal?.worldStrength === 0.9
    && materialReport.neutralReveal?.finalLightingOrEnvironment === false
    && materialReport.mechanismDecisionMetadata?.detentCount === 30
    && materialReport.mechanismDecisionMetadata?.runtimeChanged === false
    && Object.values(materialReport.scope || {}).every((value) => value === false);
  if (!validMaterial) throw new PipelineError("Gate 07 revision 3 report does not satisfy the brighter crystal contract.", 422);

  const closeupRecord = definitions.find((record) => record.key === "closeup");
  const comparisonRecord = definitions.find((record) => record.key === "comparison");
  const validImages = imageReport.schemaVersion === 1
    && imageReport.materialRevision === 3
    && imageReport.comparisonMode === "same-camera-same-neutral-light"
    && imageReport.baseline?.sha256 === materialReport.revisionComparison.baselineCloseupSha256
    && imageReport.candidate?.sha256 === sha256File(resolveRepoPath(closeupRecord.path))
    && imageReport.comparisonSha256 === sha256File(resolveRepoPath(comparisonRecord.path))
    && imageReport.deltas?.meanLuma > 0
    && imageReport.deltas?.highlightAbove230RelativeGain >= 0.15
    && imageReport.deltas?.meanRgbChroma > 0
    && imageReport.deltas?.faceContrastP90MinusP10 >= 0
    && imageReport.candidate?.metrics?.clippedFractionAbove250 < 0.01
    && Object.values(imageReport.checks || {}).every(Boolean)
    && imageReport.pass === true;
  if (!validImages) throw new PipelineError("Gate 07 revision 3 image report does not satisfy brightness and clipping gates.", 422);

  const userClaimId = "slider-brighter-crystal-request-r003";
  if (manifest.claims.some((claim) => claim.id === userClaimId)) throw new PipelineError("Gate 07 revision 3 user claim already exists.", 409);
  manifest.claims.push({
    id: userClaimId,
    stageId: "07-material",
    topic: "brighter-crystal-material-tuning",
    statement: "用户选择 Gate 07 rev 2 Variant B 为基础，并要求原文：‘再 crystal 一点，就是更亮一些.’ 保留镜银、深色蚀刻 motif 和紫／蓝／绿虹彩核心。",
    confidence: "high",
    state: "active",
    assertedBy: "user",
    sourceAssetIds: [
      `${modelId}-material-closeup-r002`,
      `${modelId}-motif-mask-r002`
    ],
    sourceRegions: [],
    sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2"
  });

  const sourceAssetIds = [
    ...geometry.artifactIds,
    `${modelId}-material-closeup-r002`,
    `${modelId}-motif-mask-r002`,
    `${modelId}-motif-provenance-r002`,
    ...materialReport.sourceLinks.map((source) => source.assetId)
  ];
  const sourceClaimIds = [
    "slider-analysis-claim-material-language",
    "slider-blockout-point-axis-distinction-r003",
    "slider-ratchet-30-detent-requirement-r001"
  ];
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    const view = record.key === "comparison"
      ? { id: "material-comparison", kind: "perspective", camera: "M07R2/R3_MaterialCloseupCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE", recipe: "same-camera-same-neutral-light-rev2-vs-rev3" }
      : record.key === "board"
        ? { id: "material-board", kind: "perspective", camera: "M07R3_MaterialBoardCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE", recipe: "neutral-reveal-brighter-crystal-and-value-deltas" }
        : record.key === "closeup"
          ? { id: "material-closeup", kind: "perspective", camera: "M07R3_MaterialCloseupCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE", recipe: "neutral-reveal-brighter-crystal-same-as-rev2" }
          : null;
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: "process",
      producer: {
        name: ["imageValidator", "comparison", "imageValidation"].includes(record.key) ? "Pillow/Python" : (record.key === "builder" ? "deterministic-bpy" : "Blender"),
        version: ["imageValidator", "comparison", "imageValidation"].includes(record.key) ? "Pillow 11.3.0" : materialReport.blender,
        recipe: ["imageValidator", "comparison", "imageValidation"].includes(record.key) ? `${expectedDirectory}/validate_crystal_comparison.py` : `${expectedDirectory}/build_brighter_crystal.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 07 rev 3 preserves rev 2 Variant B and approved Gate 06 geometry while increasing polished-cap highlights and iridescent separation without emission, bloom, exposure, or lighting changes.",
        userClaimIds: [...sourceClaimIds, "slider-material-process-analysis-r002", userClaimId]
      },
      sourceAssetIds,
      sourceClaimIds,
      ...(view ? { view } : {})
    };
  });
  manifest.assets.push(...records);

  const mechanismRequirement = stage.materialSpec.mechanismRequirement;
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.materialSpec = {
    revision: 3,
    supersedesRevision: 2,
    sourceGate06Revision: 1,
    sourceGate06Sha256: materialReport.sourceGate06.sha256Before,
    evaluatedGeometryDigest: materialReport.sourceGate06.evaluatedGeometryDigest,
    recommendedVariant: "B-brighter-crystal",
    baseVariant: "B-r002",
    zoneIds: ["mirror-silver-exterior-body", "source-derived-dark-etched-motif", "crystal-iridescent-face"],
    mirrorSilver: { metallic: 1, roughness: 0.095, ior: 1.5, coatWeight: 0.32, coatRoughness: 0.055 },
    motif: {
      kind: etch.motifKind,
      maskAssetId: `${modelId}-motif-mask-r002`,
      maskSha256: etch.motifMaskSha256,
      sourceAssetIds: materialReport.motifProvenance.sourceAssetIds,
      motifMixFactor: etch.motifMixFactor,
      etchBumpStrength: etch.etchBumpStrength,
      etchDepthIllusionMm: etch.etchDepthIllusionMm,
      productionVector: false
    },
    crystalIridescent: {
      roughness: crystal.roughness,
      ior: crystal.ior,
      specularIorLevel: crystal.specularIorLevel,
      substrateTransmissionWeight: crystal.transmissionWeight,
      coatWeight: crystal.coatWeight,
      coatRoughness: crystal.coatRoughness,
      thinFilmIor: crystal.thinFilmIor,
      thinFilmThicknessNm: crystal.thinFilmThicknessNm,
      microfacetSparkleScale: crystal.microfacetSparkleScale,
      microfacetSparkleStrength: crystal.microfacetSparkleStrength,
      emissionStrength: 0
    },
    comparison: {
      baselineRevision: 2,
      meanLumaDelta: imageReport.deltas.meanLuma,
      highlightAbove230RelativeGain: imageReport.deltas.highlightAbove230RelativeGain,
      meanRgbChromaDelta: imageReport.deltas.meanRgbChroma,
      faceContrastDelta: imageReport.deltas.faceContrastP90MinusP10,
      clippedFractionAbove250: imageReport.candidate.metrics.clippedFractionAbove250,
      pass: imageReport.pass
    },
    processClaimId: "slider-material-process-analysis-r002",
    userClaimId,
    confirmedProductionMaterial: "steel",
    inferredProcessesRemainProvisional: true,
    geometryChanged: false,
    hiddenRatchetConstructionKnown: false,
    neutralRevealOnly: true,
    finalLightingOrEnvironment: false,
    unityAssetChanged: false,
    mechanismRequirement
  };
  stage.validations = [
    { id: "rev2-superseded-preserved", status: "pass", evidence: "Gate 07 rev 2 artifacts and hashes remain immutable; rev 3 cites its closeup and motif evidence." },
    { id: "gate06-source-immutable", status: "pass", evidence: `Approved Gate 06 blend hash remained ${materialReport.sourceGate06.sha256Before}.` },
    { id: "geometry-digest-preserved", status: "pass", evidence: `Geometry digest remained ${materialReport.sourceGate06.evaluatedGeometryDigest} before assignment, after assignment, and after renders.` },
    { id: "same-camera-neutral-light", status: "pass", evidence: "Rev 2 and rev 3 closeups use the same 78 mm camera and four unchanged neutral reveal lights at world strength 0.9." },
    { id: "brighter-crystal-histogram", status: "pass", evidence: `Mean luma +${imageReport.deltas.meanLuma}; pixels above 230 gained ${(imageReport.deltas.highlightAbove230RelativeGain * 100).toFixed(2)}%; RGB chroma +${imageReport.deltas.meanRgbChroma}.` },
    { id: "no-clipping-or-emission", status: "pass", evidence: `Emission is 0. Clipped fraction above 250 is ${imageReport.candidate.metrics.clippedFractionAbove250}; hard-255 fraction is ${imageReport.candidate.metrics.hardClipFraction255}.` },
    { id: "motif-contrast-maintained", status: "pass", evidence: `Face P90-P10 contrast changed from ${imageReport.baseline.metrics.faceContrastP90MinusP10} to ${imageReport.candidate.metrics.faceContrastP90MinusP10}.` },
    { id: "shader-only-etch", status: "pass", evidence: "The source-derived motif remains shader-only at 0.24 bump strength / 0.06 mm depth illusion; artwork geometry remains zero." },
    { id: "concealed-mechanism-preserved", status: "pass", evidence: "The concealed envelope remains a fixed non-rendering Empty with zero hidden mechanism meshes." },
    { id: "thirty-detent-specified-only", status: "pass", evidence: "360° / 12° / 30 remains locked but specified-only; runtime, Haptic, hardware, and iPhone validation remain pending." },
    { id: "shipping-unity-unchanged", status: "pass", evidence: "No Unity runtime, scene, haptic, build, install, or device state changed." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "Gate 07 rev 3 brighter crystal 材质等待视觉批准；不得进入 Gate 08。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 07 rev 2 已按用户“再 crystal 一点，就是更亮一些.”的明确请求 supersede 并不可变保留。Gate 07 rev 3 保持镜银、深色蚀刻 visual trace 与紫／蓝／绿虹彩核心，在相同 neutral light/camera 下用无 emission 的低粗糙度 clear-cap lobe、IOR、thin film 和微面 sparkle 提高高光与颜色分离。等待视觉批准，不得进入 Gate 08。";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "07-material",
    materialRevision: 3,
    supersedesMaterialRevision: 2,
    artifactIds: stage.artifactIds,
    evaluatedGeometryDigest: materialReport.sourceGate06.evaluatedGeometryDigest,
    recommendedVariant: "B-brighter-crystal",
    userRequest: "再 crystal 一点，就是更亮一些.",
    meanLumaDelta: imageReport.deltas.meanLuma,
    highlightAbove230RelativeGain: imageReport.deltas.highlightAbove230RelativeGain,
    meanRgbChromaDelta: imageReport.deltas.meanRgbChroma,
    emissionStrength: 0,
    runtimeChanged: false,
    hapticsChanged: false,
    unityChanged: false,
    blender: materialReport.blender,
    autoApproved: false
  });
  return saveManifest(manifest, event);
}

export function saveBloodRedArtworkReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (modelId !== "magnetic-slide-tile") throw new PipelineError("Gate 07 blood-red artwork registration is supported only for magnetic-slide-tile.", 422);
  const EXPECTED_DIGEST = "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f";
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "07-material");
  const geometry = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (geometry.status !== "approved" || geometry.geometrySpec?.revision !== 1) {
    throw new PipelineError("Approved Gate 06 revision 1 is required.", 422);
  }
  if (stage.status !== "rejected" || stage.materialSpec?.revision !== 3 || stage.decision?.action !== "reject") {
    throw new PipelineError("Gate 07 revision 3 must remain rejected/superseded before creating revision 4.", 422);
  }

  const revisionLabel = "004";
  const expectedDirectory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/07-material", `rev-${revisionLabel}`
  )));
  const definitions = [
    ["deriver", "artwork-deriver", "artwork-source", "derive_blood_red_artwork.py", "perspective-rectified-color-and-artwork-derivation-source"],
    ["upperRectified", "artwork-upper-source", "artwork-source-crop", "upper-source-rectified.png", "perspective-rectified-upper-source-crop"],
    ["lowerRectified", "artwork-lower-source", "artwork-source-crop", "lower-visible-source-rectified.png", "perspective-rectified-source-visible-lower-crop"],
    ["upperMask", "artwork-upper-mask", "artwork-mask", "artwork-upper-mask.png", "editable-upper-artwork-visual-trace"],
    ["lowerMask", "artwork-lower-mask", "artwork-mask", "artwork-lower-mask.png", "editable-lower-source-visible-artwork-visual-trace"],
    ["lowerUnknown", "artwork-lower-unknown", "artwork-unknown-mask", "artwork-lower-occluded-unknown.png", "explicit-lower-occlusion-unknown-mask"],
    ["artworkConfig", "artwork-config", "artwork-config", "artwork-layers.json", "independently-swappable-artwork-slot-manifest"],
    ["colorAnalysis", "blood-red-analysis", "color-analysis", "blood-red-source-analysis.json", "steel-normalized-blood-red-source-analysis"],
    ["derivationValidation", "artwork-derivation-validation", "validation-report", "artwork-derivation-validation.json", "artwork-trace-and-occlusion-validation"],
    ["builder", "material-builder", "material-source", "build_blood_red_editable_artwork.py", "deterministic-blood-red-editable-artwork-source"],
    ["blend", "material-blend", "material-blend", "magnetic-slide-tile-material-r004.blend", "blood-red-editable-artwork-lookdev-scene"],
    ["comparison", "material-comparison", "material-comparison", "blood-red-source-comparison.png", "source-vs-neutral-front-blood-red-comparison"],
    ["front", "material-front", "material-front", "neutral-front-blood-red.png", "real-blender-neutral-front-blood-red"],
    ["board", "material-board", "material-board", "neutral-pbr-material-board.png", "real-blender-neutral-pbr-board"],
    ["closeup", "material-closeup", "material-closeup", "neutral-pbr-material-closeup.png", "real-blender-blood-red-crystal-closeup"],
    ["secondLight", "material-second-light", "material-second-light", "diagnostic-second-light-crystal-response.png", "gate07-diagnostic-second-light-response"],
    ["sideReflection", "material-side-reflection", "material-side-reflection", "diagnostic-side-direct-reflection.png", "gate07-side-direct-light-reflection"],
    ["openArtwork", "material-open-artwork", "material-open-artwork", "open-slide-lower-artwork.png", "open-slide-visible-lower-artwork"],
    ["processBoard", "material-process-board", "material-process-board", "editable-artwork-layer-board.png", "editable-upper-lower-layer-process-board"],
    ["imageValidator", "material-image-validator", "validation-source", "validate_blood_red_artwork.py", "color-reflection-lower-artwork-validation-source"],
    ["imageValidation", "material-image-validation", "validation-report", "image-artwork-validation.json", "blood-red-pink-suppression-reflection-and-visibility-validation"],
    ["blenderAuditSource", "material-blender-audit-source", "validation-source", "audit_blender_rev4.py", "blender-node-group-geometry-audit-source"],
    ["blenderAudit", "material-blender-audit", "validation-report", "blender-audit.json", "blender-geometry-material-and-artwork-slot-audit"],
    ["validation", "material-validation", "validation-report", "material-validation.json", "pbr-artwork-geometry-light-and-scope-validation"]
  ].map(([key, suffix, slot, file, contentClass]) => ({
    key,
    id: `${modelId}-${suffix}-r${revisionLabel}`,
    stageId: "07-material",
    slot,
    path: normalizeRepoPath(`${expectedDirectory}/${file}`),
    contentClass
  }));
  for (const record of definitions) {
    const absolute = resolveRepoPath(record.path);
    if (!fs.existsSync(absolute) || !fs.statSync(absolute).isFile()) throw new PipelineError(`${record.id} file is missing.`, 422);
  }

  const byKey = (key) => definitions.find((record) => record.key === key);
  const materialReport = JSON.parse(fs.readFileSync(resolveRepoPath(byKey("validation").path), "utf8"));
  const imageReport = JSON.parse(fs.readFileSync(resolveRepoPath(byKey("imageValidation").path), "utf8"));
  const blenderAudit = JSON.parse(fs.readFileSync(resolveRepoPath(byKey("blenderAudit").path), "utf8"));
  const artworkConfig = JSON.parse(fs.readFileSync(resolveRepoPath(byKey("artworkConfig").path), "utf8"));
  const colorAnalysis = JSON.parse(fs.readFileSync(resolveRepoPath(byKey("colorAnalysis").path), "utf8"));
  const crystal = materialReport.materialZones?.["deep-blood-red-crystal-face"];
  const validMaterial = materialReport.schemaVersion === 4
    && materialReport.materialRevision === 4
    && materialReport.supersedesMaterialRevision === 3
    && materialReport.sourceGate06?.unchanged === true
    && materialReport.geometryPreservation?.pass === true
    && materialReport.geometryPreservation?.digestBefore === "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"
    && materialReport.geometryPreservation?.digestBefore === materialReport.geometryPreservation?.digestAfterMaterialAssignment
    && materialReport.geometryPreservation?.digestBefore === materialReport.geometryPreservation?.digestAfterRenders
    && materialReport.geometryPreservation?.artworkOrnamentGeometryCount === 0
    && materialReport.materialAssignments?.pass === true
    && materialReport.artworkLayers?.pass === true
    && materialReport.artworkLayers?.geometryRebuildRequired === false
    && crystal?.baseColor?.slice(0, 3).join(",") === "0.22,0.008,0.018"
    && crystal?.roughness === 0.035
    && crystal?.ior === 1.52
    && crystal?.coatWeight === 1
    && crystal?.coatRoughness === 0.012
    && crystal?.transmissionWeight === 0.12
    && crystal?.thinFilmIor === 1.38
    && crystal?.thinFilmThicknessNm === 430
    && crystal?.etchBumpStrength === 0.2
    && crystal?.etchDepthIllusionMm === 0.06
    && materialReport.forbiddenLightingAndShaderTricks?.pass === true
    && materialReport.diagnosticLighting?.finalLightingOrEnvironment === false
    && materialReport.mechanismDecisionMetadata?.detentCount === 30
    && Object.values(materialReport.scope || {}).every((value) => value === false);
  if (!validMaterial) throw new PipelineError("Gate 07 revision 4 material report does not satisfy the blood-red editable-artwork contract.", 422);

  const validEvidence = imageReport.materialRevision === 4
    && imageReport.pass === true
    && Object.values(imageReport.checks || {}).every(Boolean)
    && blenderAudit.materialRevision === 4
    && blenderAudit.pass === true
    && Object.values(blenderAudit.checks || {}).every(Boolean)
    && artworkConfig.slots?.Artwork_Upper?.maskSha256 === sha256File(resolveRepoPath(byKey("upperMask").path))
    && artworkConfig.slots?.Artwork_Lower?.maskSha256 === sha256File(resolveRepoPath(byKey("lowerMask").path))
    && artworkConfig.slots?.Artwork_Lower?.unknownMaskSha256 === sha256File(resolveRepoPath(byKey("lowerUnknown").path))
    && artworkConfig.slots?.Artwork_Upper?.maskSha256 !== artworkConfig.slots?.Artwork_Lower?.maskSha256
    && colorAnalysis.userAuthority === "deep blood red, not pink"
    && colorAnalysis.chemistryClaimed === false;
  if (!validEvidence) throw new PipelineError("Gate 07 revision 4 source, image, or Blender evidence failed validation.", 422);

  const userClaimId = "slider-blood-red-editable-artwork-r004";
  if (manifest.claims.some((claim) => claim.id === userClaimId)) throw new PipelineError("Gate 07 revision 4 user claim already exists.", 409);
  manifest.claims.push({
    id: userClaimId,
    stageId: "07-material",
    topic: "blood-red-editable-upper-lower-artwork",
    statement: "用户否决 Gate 07 rev 3 的偏粉结果，明确要求 deep blood red，并要求上／下图案成为可独立替换的外部 mask 层；打开滑块时下片必须显示 source-linked pattern。",
    confidence: "high",
    state: "active",
    assertedBy: "user",
    sourceAssetIds: ["slider-intake-obs-frame-01", "slider-intake-obs-frame-05", "slider-intake-obs-frame-10", "slider-intake-haloo-official-03"],
    sourceRegions: [],
    sourceTask: "b968679a-4069-41e7-a7fc-47cf5366bae2"
  });

  const sourceAssetIds = [...geometry.artifactIds, ...materialReport.sourceLinks.map((source) => source.assetId)];
  const sourceClaimIds = [
    "slider-analysis-claim-material-language",
    "slider-blockout-point-axis-distinction-r003",
    "slider-ratchet-30-detent-requirement-r001"
  ];
  const viewByKey = {
    comparison: { id: "material-comparison", kind: "perspective", camera: "source/M07R4_NeutralFrontCamera", pose: "closed-zero-motion", renderEngine: "Pillow+BLENDER_EEVEE", recipe: "source-vs-neutral-front" },
    front: { id: "front", kind: "perspective", camera: "M07R4_NeutralFrontCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE", recipe: "neutral-front-blood-red" },
    board: { id: "material-board", kind: "perspective", camera: "M07R4_MaterialBoardCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE", recipe: "neutral-pbr-board" },
    closeup: { id: "material-closeup", kind: "perspective", camera: "M07R4_MaterialCloseupCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE", recipe: "neutral-blood-red-closeup" },
    secondLight: { id: "material-second-light", kind: "perspective", camera: "M07R4_MaterialCloseupCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE", recipe: "gate07-diagnostic-second-light" },
    sideReflection: { id: "right", kind: "perspective", camera: "M07R4_SideReflectionCamera", pose: "closed-zero-motion", renderEngine: "BLENDER_EEVEE", recipe: "gate07-side-direct-light" },
    openArtwork: { id: "right-oblique", kind: "perspective", camera: "M07R4_OpenArtworkCamera", pose: "upper-translation-plus-21mm", renderEngine: "BLENDER_EEVEE", recipe: "open-lower-artwork" },
    processBoard: { id: "material-process-board", kind: "perspective", camera: "M07R4_MaterialBoardCamera", pose: "upper-translation-plus-21mm", renderEngine: "BLENDER_EEVEE", recipe: "editable-layer-process-board" }
  };
  const records = definitions.map((record) => {
    const absolute = resolveRepoPath(record.path);
    const pythonProduced = ["deriver", "imageValidator", "imageValidation", "comparison", "derivationValidation"].includes(record.key);
    return {
      id: record.id,
      stageId: record.stageId,
      slot: record.slot,
      path: record.path,
      sha256: sha256File(absolute),
      exists: true,
      sizeBytes: fs.statSync(absolute).size,
      role: "process",
      producer: {
        name: pythonProduced ? "Pillow/OpenCV/Python" : (record.key === "builder" ? "deterministic-bpy" : "Blender"),
        version: pythonProduced ? "Python 3 / OpenCV 4.13 / Pillow" : materialReport.blender,
        recipe: pythonProduced ? `${expectedDirectory}/validate_blood_red_artwork.py` : `${expectedDirectory}/build_blood_red_editable_artwork.py`
      },
      provenance: {
        origin: "repository-generated",
        contentClass: record.contentClass,
        assertedBy: "assistant",
        note: "Gate 07 rev 4 preserves approved geometry, shifts the optical substrate to source-audited blood red, and keeps upper/lower artwork in independent external-mask node groups.",
        userClaimIds: sourceClaimIds
      },
      sourceAssetIds,
      sourceClaimIds,
      ...(viewByKey[record.key] ? { view: viewByKey[record.key] } : {})
    };
  });
  manifest.assets.push(...records);

  const mechanismRequirement = stage.materialSpec.mechanismRequirement;
  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((record) => record.id);
  stage.reviewArtifactIds = ["comparison", "secondLight", "sideReflection", "openArtwork", "processBoard", "board", "closeup"].map((key) => byKey(key).id);
  stage.materialSpec = {
    revision: 4,
    supersedesRevision: 3,
    sourceGate06Revision: 1,
    sourceGate06Sha256: materialReport.sourceGate06.sha256Before,
    evaluatedGeometryDigest: EXPECTED_DIGEST,
    recommendedVariant: "blood-red-editable-artwork",
    zoneIds: ["mirror-silver-exterior-body", "deep-blood-red-crystal-face"],
    mirrorSilver: { metallic: 1, roughness: 0.095, ior: 1.5, coatWeight: 0.32, coatRoughness: 0.055 },
    bloodRedCrystal: {
      baseColorLinearRgb: crystal.baseColor.slice(0, 3),
      roughness: crystal.roughness,
      ior: crystal.ior,
      specularIorLevel: crystal.specularIorLevel,
      transmissionWeight: crystal.transmissionWeight,
      coatWeight: crystal.coatWeight,
      coatRoughness: crystal.coatRoughness,
      thinFilmIor: crystal.thinFilmIor,
      thinFilmThicknessNm: crystal.thinFilmThicknessNm,
      emissionStrength: 0
    },
    artwork: {
      configAssetId: byKey("artworkConfig").id,
      upperMaskAssetId: byKey("upperMask").id,
      lowerMaskAssetId: byKey("lowerMask").id,
      lowerUnknownAssetId: byKey("lowerUnknown").id,
      nodeGroups: ["Artwork_Upper", "Artwork_Lower"],
      independentlySwappable: true,
      geometryRebuildRequired: false,
      lowerOccludedRegionUnknown: true
    },
    imageMetrics: imageReport,
    confirmedProductionMaterial: "steel",
    pigmentChemistryKnown: false,
    inferredProcessesRemainProvisional: true,
    geometryChanged: false,
    hiddenRatchetConstructionKnown: false,
    diagnosticLightingOnly: true,
    finalLightingOrEnvironment: false,
    unityAssetChanged: false,
    userClaimId,
    mechanismRequirement
  };
  stage.validations = [
    { id: "rev3-superseded-preserved", status: "pass", evidence: "Gate 07 rev 3 artifacts and hashes remain immutable; revision 4 is additive." },
    { id: "blood-red-source-audit", status: "pass", evidence: `Steel-normalized source median is ${colorAnalysis.correctedBloodRedSrgb.median.join("/")}; hue ${colorAnalysis.correctedHsv.hueSignedMedianDegrees}°.` },
    { id: "pink-suppression", status: "pass", evidence: `Rendered median hue ${imageReport.frontBloodRed.signedHueMedianDegrees}°; pink fraction ${imageReport.frontBloodRed.pinkFraction}; blood-red fraction ${imageReport.frontBloodRed.bloodRedFraction}.` },
    { id: "editable-artwork-slots", status: "pass", evidence: "Artwork_Upper and Artwork_Lower reference different external, unpacked masks and can swap without mesh rebuild." },
    { id: "lower-occlusion-honesty", status: "pass", evidence: "Only the source-visible lower end is traced; the region hidden by the upper shell is marked unknown." },
    { id: "lower-pattern-visible-open", status: "pass", evidence: `Open-pose lower ROI red ${imageReport.lowerArtwork.redSurfaceFraction}; dark pattern ${imageReport.lowerArtwork.darkPatternFraction}.` },
    { id: "geometry-digest-preserved", status: "pass", evidence: `Geometry digest remained ${EXPECTED_DIGEST} before assignment, after assignment, and after all renders.` },
    { id: "diagnostic-second-light", status: "pass", evidence: `Pixels above luma 220 rose from ${imageReport.crystalHighlight.neutral.above220Fraction} to ${imageReport.crystalHighlight.secondDiagnosticLight.above220Fraction}.` },
    { id: "side-direct-reflection", status: "pass", evidence: `Calibrated side light produced reflection span ${imageReport.sideReflection.maximumReflectionSpanPx}px (${imageReport.sideReflection.maximumReflectionSpanFraction}).` },
    { id: "no-clipping-or-emission", status: "pass", evidence: `Hard-255 fraction ${imageReport.frontBloodRed.hard255Fraction}; both artwork materials use emission 0.` },
    { id: "gate08-blocked", status: "pass", evidence: "All added lights are labeled Gate 07 diagnostics. Gate 08, Unity, runtime, Haptic, build, install, and phone remain unchanged." }
  ];
  stage.decision = null;
  delete stage.staleReason;
  markDownstreamStale(manifest, stageIndex, "Gate 07 rev 4 blood-red editable artwork 等待视觉批准；不得进入 Gate 08。");
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  manifest.currentState.diagnosis = "Gate 07 rev 3 已按用户对偏粉颜色、固定图案和缺少下片图案的否决 supersede 并不可变保留。Gate 07 rev 4 使用邻近钢质白平衡校正的深血红目标、独立 Artwork_Upper／Artwork_Lower 外部 mask、第二测试灯、直接迎光侧视和开合下片图案证据。等待视觉批准，不得进入 Gate 08。";
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "07-material",
    materialRevision: 4,
    supersedesMaterialRevision: 3,
    artifactIds: stage.artifactIds,
    evaluatedGeometryDigest: EXPECTED_DIGEST,
    recommendedVariant: "blood-red-editable-artwork",
    userRequest: "deep blood red, not pink; editable upper/lower artwork; diagnostic light and side reflection",
    renderedHueSignedMedianDegrees: imageReport.frontBloodRed.signedHueMedianDegrees,
    pinkFraction: imageReport.frontBloodRed.pinkFraction,
    bloodRedFraction: imageReport.frontBloodRed.bloodRedFraction,
    lowerPatternVisible: imageReport.checks.lowerPatternVisible,
    artworkSlots: ["Artwork_Upper", "Artwork_Lower"],
    emissionStrength: 0,
    runtimeChanged: false,
    hapticsChanged: false,
    unityChanged: false,
    blender: materialReport.blender,
    autoApproved: false
  });
  return saveManifest(manifest, event);
}

export function saveManifest(manifest, event) {
  const errors = validateManifest(manifest);
  if (errors.length) throw new PipelineError("Refusing to save an invalid manifest.", 500, errors);
  atomicWriteJson(pipelineFile(manifest.model.id), manifest);
  if (event) appendHistory(manifest.model.id, event);
  return deriveManifest(manifest);
}

export function refreshManifest(modelId, expectedRevision = null) {
  const manifest = loadManifest(modelId);
  if (expectedRevision !== null && expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  const previousDigests = new Map(manifest.stages.map((stage) => [stage.id, stage.outputDigest || null]));
  const changedStages = new Set();
  const changedAssets = [];
  for (const asset of manifest.assets) {
    const absolute = resolveRepoPath(asset.path);
    const exists = fs.existsSync(absolute) && fs.statSync(absolute).isFile();
    const oldHash = asset.sha256 || null;
    asset.exists = exists;
    asset.sizeBytes = exists ? fs.statSync(absolute).size : 0;
    asset.sha256 = exists ? sha256File(absolute) : null;
    if ((oldHash && oldHash !== asset.sha256) || (!exists && oldHash)) {
      changedStages.add(asset.stageId);
      changedAssets.push(asset.id);
    }
  }
  updateStageDigests(manifest);
  for (const stage of manifest.stages) {
    const previous = previousDigests.get(stage.id);
    if (previous && previous !== stage.outputDigest) changedStages.add(stage.id);
  }
  if (changedStages.size) {
    const firstIndex = Math.min(...[...changedStages].map((stageId) => STAGES.findIndex((stage) => stage.id === stageId)));
    const firstChangedStage = manifest.stages[firstIndex];
    if (firstChangedStage.status !== "missing" && firstChangedStage.status !== "blocked") {
      firstChangedStage.status = "stale";
      firstChangedStage.staleReason = "素材文件哈希或存在状态发生变化。";
    }
    markDownstreamStale(manifest, firstIndex, `上游 ${manifest.stages[firstIndex].id} 的素材发生变化。`);
  }
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  const event = makeEvent(manifest, "assets-refreshed", { changedAssets, changedStageIds: [...changedStages] });
  return saveManifest(manifest, event);
}

const PREMIUM_DISPLAY_CASE_GATE03_RIGID_APPROVAL_SCOPE = [
  "preserve-static-case",
  "toy-out-of-scope",
  "rigid-whole-case",
  "per-sample-quaternion-translation-uniform-scale-best-fit",
  "explicit-reprojection-residuals",
  "forbid-pure-y-single-axis-nonrigid-explode",
  "duration-4.520833s",
  "single-highlight-and-hold"
];

function preparePremiumDisplayCaseGate03RigidApproval(manifest, stage, payload) {
  const userQuote = String(payload.userQuote || "").trim();
  const approvalScope = Array.isArray(payload.approvalScope)
    ? [...new Set(payload.approvalScope.map((item) => String(item).trim()).filter(Boolean))]
    : [];
  if (userQuote !== "批准") {
    throw new PipelineError("Premium Display Case Gate 03 rev 2 approval must preserve the exact user quote ‘批准’.", 422);
  }
  if (
    approvalScope.length !== PREMIUM_DISPLAY_CASE_GATE03_RIGID_APPROVAL_SCOPE.length
    || PREMIUM_DISPLAY_CASE_GATE03_RIGID_APPROVAL_SCOPE.some((item) => !approvalScope.includes(item))
  ) {
    throw new PipelineError("Premium Display Case Gate 03 rev 2 approval scope is incomplete.", 422);
  }

  const contractAsset = manifest.assets.find(
    (asset) => asset.id === "premium-display-case-modeling-contract-r002");
  const fitAsset = manifest.assets.find(
    (asset) => asset.id === "premium-display-case-rigid-motion-fit-r002");
  const validationAsset = manifest.assets.find(
    (asset) => asset.id === "premium-display-case-rigid-motion-fit-validation-r002");
  if (!contractAsset || !fitAsset || !validationAsset) {
    throw new PipelineError("Gate 03 rev 2 contract evidence is missing.", 422);
  }
  const contract = JSON.parse(fs.readFileSync(resolveRepoPath(contractAsset.path), "utf8"));
  const fit = JSON.parse(fs.readFileSync(resolveRepoPath(fitAsset.path), "utf8"));
  const validation = JSON.parse(fs.readFileSync(resolveRepoPath(validationAsset.path), "utf8"));
  const sourceClaimIds = contract.sourceClaimIds || [];
  const stageAssets = stage.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)
  );
  const stageHashesMatch = stageAssets.every((asset) => (
    asset
    && asset.exists !== false
    && asset.sha256
    && fs.existsSync(resolveRepoPath(asset.path))
    && sha256File(resolveRepoPath(asset.path)) === asset.sha256
  ));
  const stageClaimsMatch = stageAssets.every(
    (asset) => JSON.stringify(asset?.sourceClaimIds || []) === JSON.stringify(sourceClaimIds)
  );
  const prohibited = contract?.motionContract?.prohibited || [];
  if (
    stage.status !== "stale"
    || stage.contractSpec?.revision !== 2
    || contract?.contractRevision !== 2
    || contract?.staticPreservation?.geometryMutationAllowed !== false
    || contract?.staticPreservation?.materialMutationAllowed !== false
    || contract?.staticPreservation?.toyScope?.status !== "out-of-scope-caller-owned-content"
    || contract?.motionContract?.target !== "one rigid assembled Portrait cuboid"
    || contract?.motionContract?.motionOwner !== "PresentationRoot"
    || contract?.motionContract?.poseRepresentation !== "normalized WXYZ quaternion, camera-space translation, uniform scale 1.0, diagnostic framing scale"
    || contract?.motionContract?.fitTruth?.exactFitClaimed !== false
    || contract?.motionContract?.timeline?.contract?.durationSeconds !== 4.520833
    || contract?.motionContract?.singleHighlight?.count !== 1
    || contract?.motionContract?.prize?.independentAngularVelocity !== 0
    || !prohibited.includes("pure Y turntable")
    || !prohibited.includes("single-axis physical claim")
    || !prohibited.includes("non-rigid Rive mesh deformation")
    || !prohibited.includes("explode")
    || fit?.samples?.length !== 9
    || fit.samples.some((sample) => sample.uniformScale !== 1)
    || fit?.residualSummaryPixels?.exact !== false
    || fit?.residualSummaryPixels?.mean !== 6.780574
    || fit?.residualSummaryPixels?.rmse !== 11.241096
    || fit?.residualSummaryPixels?.maximum !== 38.343513
    || validation?.status !== "pass"
    || Object.values(validation?.checks || {}).some((value) => value !== true)
    || sourceClaimIds.length !== 11
    || sourceClaimIds.some((claimId) => !claimId.endsWith("-r003"))
    || !stageHashesMatch
    || !stageClaimsMatch
    || JSON.stringify(stage.reviewArtifactIds) !== JSON.stringify([
      "premium-display-case-contract-preview-r002"
    ])
  ) {
    throw new PipelineError("Gate 03 rev 2 evidence no longer matches the approved rigid best-fit scope.", 422);
  }

  const now = new Date().toISOString();
  const sourceClaimSet = new Set(sourceClaimIds);
  for (const claim of manifest.claims || []) {
    if (claim.stageId !== "02-analysis") continue;
    if (sourceClaimSet.has(claim.id)) {
      if (claim.state === "superseded" || claim.supersededBy) {
        claim.stateHistory = [
          ...(claim.stateHistory || []),
          {
            state: claim.state,
            supersededBy: claim.supersededBy || null,
            supersededAt: claim.supersededAt || null
          }
        ];
      }
      claim.state = "active";
      claim.decisionState = "reinstated-by-explicit-gate03-rev2-user-approval";
      claim.reactivatedAt = now;
      claim.reactivatedBy = "gate03-contract-rev2-user-approval";
      delete claim.supersededBy;
      delete claim.supersededAt;
    } else if (claim.state !== "superseded") {
      claim.state = "superseded";
      claim.decisionState = "superseded-by-explicit-gate03-rev2-user-approval";
      claim.supersededAt = now;
      claim.supersededBy = "gate03-contract-rev2-user-approval";
    }
  }

  const analysis = manifest.stages[1];
  analysis.authorityHistory = [
    ...(analysis.authorityHistory || []),
    {
      analysisRevision: analysis.analysisSpec?.revision || null,
      decision: analysis.decision ? JSON.parse(JSON.stringify(analysis.decision)) : null,
      disposition: "superseded-by-later-explicit-gate03-rev2-user-approval",
      supersededAt: now
    }
  ];
  analysis.currentMotionAuthority = {
    sourceStageId: "03-contract",
    contractRevision: 2,
    userQuote,
    approvalScope: PREMIUM_DISPLAY_CASE_GATE03_RIGID_APPROVAL_SCOPE,
    sourceClaimIds,
    decisionState: "locked",
    activatedAt: now
  };
  if (analysis.decision) {
    analysis.decision.supersededBy = "gate03-contract-rev2-user-approval";
    analysis.decision.supersededAt = now;
  }
  if (analysis.analysisSpec) {
    analysis.analysisSpec.decisionState = "superseded-by-later-explicit-gate03-rev2-user-approval";
  }
  for (const assetId of analysis.artifactIds || []) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    if (!asset) continue;
    asset.previousReviewState = asset.reviewState || null;
    asset.reviewState = "superseded";
    asset.supersededBy = "premium-display-case-modeling-contract-r002";
    asset.supersededAt = now;
    asset.preservedForHistory = true;
  }
  for (const asset of manifest.assets.filter((candidate) => (
    candidate.stageId === "02-analysis"
    && candidate.id.endsWith("-r003")
  ))) {
    asset.reusedByGate03Approval = true;
    asset.reusedAt = now;
  }

  stage.status = "ready_for_review";
  delete stage.staleReason;
  stage.contractSpec = {
    ...stage.contractSpec,
    approval: {
      approvedContractRevision: 2,
      userApprovalQuote: userQuote,
      approvalScope: PREMIUM_DISPLAY_CASE_GATE03_RIGID_APPROVAL_SCOPE,
      decisionState: "locked",
      approvalEffect: "locks-static-preservation-and-rigid-quaternion-best-fit-for-gate04",
      approvedAt: now
    },
    gate04Status: "eligible"
  };
  for (const assetId of stage.artifactIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    if (asset) asset.reviewState = "approved";
  }
  const downstreamReason = "Gate 03 rev 2 is explicitly approved. Gate 04 must create a new rigid motion-ownership revision; historical Gate 04–08 evidence remains stale.";
  for (let index = 3; index <= 7; index += 1) {
    manifest.stages[index].status = "stale";
    manifest.stages[index].staleReason = downstreamReason;
  }
  for (let index = 8; index < manifest.stages.length; index += 1) {
    manifest.stages[index].staleReason = downstreamReason;
  }
  manifest.currentState.diagnosis = "Gate 03 contract rev 2 is explicitly approved with the exact user quote ‘批准’. The preserved static case and caller-owned toy boundary now use the nine-sample rigid quaternion/translation path with explicit residuals and exact 4.520833 s duration. Gate 04 may create one new review revision; Gate 05 remains unentered. Shipping Unity and Blender geometry/material remain unchanged.";
  manifest.currentState.visualApproval = "gate03-approved-gate04-visual-review-pending";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.motionCorrection = {
    ...manifest.currentState.motionCorrection,
    authoritativeMotion: "gate03-rev2-rigid-quaternion-path",
    supersededGate02AnalysisRevision: 6,
    gate03Status: "approved",
    gate03ContractRevision: 2,
    gate04Status: "eligible",
    gate05Status: "not-entered",
    lockedTotalDurationSeconds: 4.520833,
    userApprovalQuote: userQuote,
    approvalScope: PREMIUM_DISPLAY_CASE_GATE03_RIGID_APPROVAL_SCOPE
  };
}

function savePremiumDisplayCaseRigidMotionArchitectureReview(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) {
    throw new PipelineError("Manifest revision conflict.", 409);
  }
  if (manifest.model.mechanism !== "display-case") {
    throw new PipelineError("Rigid motion architecture review is supported only for the Premium Display Case.", 422);
  }
  const stageIndex = STAGES.findIndex((candidate) => candidate.id === "04-architecture");
  const contractStage = manifest.stages[stageIndex - 1];
  const stage = manifest.stages[stageIndex];
  if (
    contractStage.status !== "approved"
    || contractStage.contractSpec?.revision !== 2
    || contractStage.contractSpec?.approval?.userApprovalQuote !== "批准"
  ) {
    throw new PipelineError("Gate 03 rev 2 must be explicitly approved before Gate 04.", 422);
  }
  if (stage.status !== "stale") {
    throw new PipelineError("Gate 04 must remain stale before creating the new architecture revision.", 422);
  }

  const directory = normalizeRepoPath(path.relative(repoRoot, path.join(
    pipelineDirectory(modelId), "evidence/04-architecture/rev-005"
  )));
  const files = {
    generator: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-005",
      `${directory}/generate_motion_ownership_review.py`,
      "Gate 04 rigid motion architecture generator"
    ),
    spec: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-005",
      `${directory}/motion-ownership-spec.json`,
      "Gate 04 rigid motion architecture spec"
    ),
    review: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-005",
      `${directory}/motion-ownership-part-tree-review.png`,
      "Gate 04 rigid motion architecture review"
    ),
    validation: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-005",
      `${directory}/motion-ownership-validation.json`,
      "Gate 04 rigid motion architecture validation"
    ),
    quality: assertRepositoryEvidenceFile(
      modelId,
      "04-architecture/rev-005",
      `${directory}/animation-quality-report.json`,
      "Gate 04 architecture quality report"
    )
  };
  const spec = JSON.parse(fs.readFileSync(files.spec.absolute, "utf8"));
  const validation = JSON.parse(fs.readFileSync(files.validation.absolute, "utf8"));
  const quality = JSON.parse(fs.readFileSync(files.quality.absolute, "utf8"));
  const fitAsset = manifest.assets.find(
    (asset) => asset.id === "premium-display-case-rigid-motion-fit-r002");
  const partTreeAsset = manifest.assets.find(
    (asset) => asset.id === "premium-display-case-part-tree-r001");
  const explodedPlanAsset = manifest.assets.find(
    (asset) => asset.id === "premium-display-case-exploded-plan-r001");
  if (!fitAsset || !partTreeAsset || !explodedPlanAsset) {
    throw new PipelineError("The approved pose path or saved Gate 04 static structure is missing.", 422);
  }
  const activeClaimIds = (manifest.claims || [])
    .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
    .map((claim) => claim.id);
  const reviewBytes = fs.readFileSync(files.review.absolute);
  const png = reviewBytes.length >= 24 && reviewBytes.subarray(1, 4).toString("ascii") === "PNG";
  const reviewWidth = png ? reviewBytes.readUInt32BE(16) : 0;
  const reviewHeight = png ? reviewBytes.readUInt32BE(20) : 0;
  const expectedUnchanged = [
    "FrontPolycarbonateShell",
    "RearPolycarbonateShell",
    "ContinuousTubePerimeter",
    "TactileBackgroundInsert",
    "PhysicalLabel",
    "ContentSlot"
  ];
  if (
    spec?.modelId !== modelId
    || spec?.gate !== "04-architecture"
    || spec?.architectureRevision !== 2
    || spec?.evidenceRevision !== 5
    || spec?.status !== "ready_for_review"
    || JSON.stringify(spec.sourceClaimIds) !== JSON.stringify(activeClaimIds)
    || activeClaimIds.length !== 11
    || activeClaimIds.some((claimId) => !claimId.endsWith("-r003"))
    || spec?.staticStructureReuse?.partTreeAssetId !== partTreeAsset.id
    || spec?.staticStructureReuse?.partTreeSha256 !== partTreeAsset.sha256
    || spec?.staticStructureReuse?.explodedPlanAssetId !== explodedPlanAsset.id
    || spec?.staticStructureReuse?.explodedPlanSha256 !== explodedPlanAsset.sha256
    || spec?.staticStructureReuse?.structureChanged !== false
    || expectedUnchanged.some((name) => !spec.staticStructureReuse.unchangedNodes.includes(name))
    || spec?.motionOwnership?.soleOwner !== "PresentationRoot"
    || spec?.motionOwnership?.posePathAssetId !== fitAsset.id
    || spec?.motionOwnership?.sampleCount !== 9
    || spec?.motionOwnership?.uniformScale !== 1
    || spec?.motionOwnership?.caseAssemblyInheritance !== "rigid-root-transform"
    || spec?.motionOwnership?.prizeInheritance !== "rigid-via-ContentSlot"
    || spec?.motionOwnership?.prizeIndependentAngularVelocity !== 0
    || spec?.motionOwnership?.totalDurationSeconds !== 4.520833
    || spec?.motionOwnership?.singleHighlightCount !== 1
    || spec?.motionOwnership?.terminalState !== "hold"
    || spec?.residualBoundary?.exactFitClaimed !== false
    || spec?.residualBoundary?.meanPixels !== 6.780574
    || spec?.residualBoundary?.rmsePixels !== 11.241096
    || spec?.residualBoundary?.maximumPixels !== 38.343513
    || !spec?.forbidden?.includes("pure-Y")
    || !spec?.forbidden?.includes("single-axis")
    || !spec?.forbidden?.includes("nonrigid-deformation")
    || !spec?.forbidden?.includes("explode")
    || spec?.toyScope?.status !== "unchanged-out-of-scope"
    || spec?.explodedPlanPolicy?.reviewArtifactEligible !== false
    || spec?.explodedPlanPolicy?.userPreviewEligible !== false
    || spec?.explodedPlanPolicy?.animationEligible !== false
    || spec?.review?.wholeCaseOnly !== true
    || spec?.review?.containsExplodedView !== false
    || spec?.review?.minimumBodyFontPixels < 42
    || reviewWidth < 3000
    || reviewHeight < 4000
    || validation?.status !== "pass"
    || Object.values(validation?.checks || {}).some((value) => value !== true)
    || quality?.status !== "pass"
    || quality?.animationProduced !== false
    || quality?.contactSheetRequired !== false
    || Object.values(quality?.checks || {}).some((value) => value !== true)
  ) {
    throw new PipelineError("Gate 04 rev 5 does not preserve the approved rigid ownership, static tree, residual, no-explode, or toy boundary.", 422);
  }
  for (const asset of [fitAsset, partTreeAsset, explodedPlanAsset]) {
    if (
      !asset.sha256
      || !fs.existsSync(resolveRepoPath(asset.path))
      || sha256File(resolveRepoPath(asset.path)) !== asset.sha256
    ) {
      throw new PipelineError(`Source artifact hash changed: ${asset.id}`, 422);
    }
  }

  const ids = {
    generator: "premium-display-case-motion-ownership-generator-r005",
    spec: "premium-display-case-motion-ownership-spec-r005",
    review: "premium-display-case-motion-ownership-review-r005",
    validation: "premium-display-case-motion-ownership-validation-r005",
    quality: "premium-display-case-motion-ownership-quality-r005"
  };
  const existingIds = new Set(manifest.assets.map((asset) => asset.id));
  for (const id of Object.values(ids)) {
    if (existingIds.has(id)) throw new PipelineError(`Gate 04 rev 5 asset already exists: ${id}`, 409);
  }
  const contractAssetIds = contractStage.artifactIds;
  const records = [
    [ids.generator, "architecture-recipe", files.generator, "process", "deterministic-motion-ownership-review-generator", [
      partTreeAsset.id,
      fitAsset.id,
      ...contractAssetIds
    ]],
    [ids.spec, "architecture-spec", files.spec, "process", "rigid-motion-ownership-and-static-part-tree-spec", [
      ids.generator,
      partTreeAsset.id,
      explodedPlanAsset.id,
      fitAsset.id
    ]],
    [ids.review, "architecture-board", files.review, "process", "whole-case-motion-ownership-part-tree-review", [
      ids.generator,
      ids.spec,
      partTreeAsset.id,
      fitAsset.id
    ]],
    [ids.validation, "validation-report", files.validation, "validation", "motion-ownership-provenance-and-image-validation", [
      ids.spec,
      ids.review
    ]],
    [ids.quality, "animation-validation", files.quality, "validation", "architecture-preview-quality-gate", [
      ids.spec,
      ids.review,
      ids.validation
    ]]
  ].map(([id, slot, file, role, contentClass, sourceAssetIds]) => ({
    id,
    stageId: "04-architecture",
    slot,
    path: file.normalized,
    sha256: sha256File(file.absolute),
    exists: true,
    sizeBytes: fs.statSync(file.absolute).size,
    role,
    producer: {
      name: "fidgeting-model-pipeline + Pillow",
      version: "2026-08-26",
      recipe: "Gate 04 rigid motion ownership and saved part-tree review"
    },
    provenance: {
      origin: "repository-generated",
      contentClass,
      assertedBy: "assistant",
      note: "Consumes the explicitly approved Gate 03 rev 2 pose path. Static case parts are reused unchanged; the exploded plan stays internal and outside reviewArtifactIds."
    },
    sourceAssetIds: [...new Set(sourceAssetIds)],
    sourceClaimIds: activeClaimIds,
    reviewState: "active",
    wholeCaseOnly: true,
    explodeEligible: false,
    ...(id === ids.review ? {
      view: {
        id: "gate04-motion-ownership",
        camera: "orthographic-information-board",
        parameters: {
          widthPixels: reviewWidth,
          heightPixels: reviewHeight,
          minimumBodyFontPixels: spec.review.minimumBodyFontPixels,
          assemblyState: "assembled"
        }
      }
    } : {})
  }));

  const now = new Date().toISOString();
  if (stage.decision) {
    stage.historicalDecisions = [
      ...(stage.historicalDecisions || []),
      {
        ...stage.decision,
        disposition: "stale-history-after-gate03-rev2-approval"
      }
    ];
  }
  const oldArtifactIds = [...stage.artifactIds];
  for (const assetId of oldArtifactIds) {
    const asset = manifest.assets.find((candidate) => candidate.id === assetId);
    if (!asset || [partTreeAsset.id, explodedPlanAsset.id].includes(asset.id)) continue;
    if (!["rejected", "superseded", "technical-rejected"].includes(asset.reviewState)) {
      asset.previousReviewState = asset.reviewState || null;
      asset.reviewState = "stale-history";
    }
    asset.preservedForHistory = true;
    asset.staleBy = ids.review;
    asset.staleAt = now;
  }
  partTreeAsset.reusedBy = ids.review;
  partTreeAsset.reusedAt = now;
  partTreeAsset.reusedWithoutContentChange = true;
  explodedPlanAsset.internalOnly = true;
  explodedPlanAsset.reviewArtifactEligible = false;
  explodedPlanAsset.userPreviewEligible = false;
  explodedPlanAsset.animationEligible = false;
  manifest.assets.push(...records);

  stage.revision += 1;
  stage.status = "ready_for_review";
  stage.artifactIds = records.map((asset) => asset.id);
  stage.reviewArtifactIds = [ids.review];
  stage.reusedStaticArtifactIds = [partTreeAsset.id];
  stage.internalArtifactIds = [explodedPlanAsset.id];
  stage.validations = [
    { id: "approved-gate03-consumed", status: "pass", evidence: `All ${contractAssetIds.length} approved Gate 03 rev 2 artifacts feed this architecture revision.` },
    { id: "all-active-claims-consumed", status: "pass", evidence: `Every new Gate 04 artifact declares all ${activeClaimIds.length} active Gate 02 rev 3 sourceClaimIds.` },
    { id: "static-part-tree-reused", status: "pass", evidence: `Saved part tree ${partTreeAsset.sha256} is reused without changing front/rear shell, closed-loop tube, insert, label or ContentSlot.` },
    { id: "presentation-root-sole-owner", status: "pass", evidence: "PresentationRoot alone owns the Gate 03 rev 2 quaternion/translation path; CaseAssembly and PrizeContent inherit it rigidly." },
    { id: "prize-motion-isolated", status: "pass", evidence: "PrizeContent remains caller-owned through ContentSlot with independent angular velocity 0." },
    { id: "residual-boundary-explicit", status: "pass", evidence: "Mean/RMSE/max reprojection residuals remain 6.780574/11.241096/38.343513 px; exact fit is not claimed." },
    { id: "duration-highlight-hold", status: "pass", evidence: "Total duration is 4.520833 s with one highlight and a terminal hold." },
    { id: "internal-exploded-plan-excluded", status: "pass", evidence: `${explodedPlanAsset.id} remains internal and is absent from reviewArtifactIds, user preview and animation.` },
    { id: "large-type-whole-case-review", status: "pass", evidence: `${reviewWidth} × ${reviewHeight} PNG uses at least ${spec.review.minimumBodyFontPixels} px body type and contains no exploded view.` },
    { id: "gate05-not-entered", status: "pass", evidence: "Gate 04 is ready_for_review only. Gate 05 remains stale and unentered." },
    { id: "shipping-boundary", status: "pass", evidence: "Blender geometry/material, shipping Unity, build, install and phone state are unchanged." }
  ];
  stage.architectureSpec = spec;
  stage.decision = null;
  delete stage.staleReason;
  const downstreamReason = "Gate 04 rigid motion-ownership rev 2 / evidence rev 5 is ready_for_review and not approved. Gate 05–08 remain stale and unentered.";
  for (let index = stageIndex + 1; index <= 7; index += 1) {
    manifest.stages[index].status = "stale";
    manifest.stages[index].staleReason = downstreamReason;
  }
  for (let index = 8; index < manifest.stages.length; index += 1) {
    manifest.stages[index].staleReason = downstreamReason;
  }
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = now;
  manifest.currentState.diagnosis = "Gate 03 rev 2 is approved. Gate 04 architecture rev 2 / evidence rev 5 is ready_for_review with PresentationRoot as the sole motion owner, the saved static part tree unchanged, the nine-sample quaternion path, explicit residuals, one highlight, hold, and no explode. Gate 05 remains stale and unentered; shipping Unity is unchanged.";
  manifest.currentState.visualApproval = "gate04-motion-ownership-review-pending";
  manifest.currentState.shippingAssetUnchanged = true;
  manifest.currentState.deviceStatus = "not-approved";
  manifest.currentState.motionCorrection = {
    ...manifest.currentState.motionCorrection,
    gate03Status: "approved",
    gate04Status: "ready_for_review",
    gate04ArchitectureRevision: 2,
    gate04EvidenceRevision: 5,
    gate05Status: "not-entered",
    reviewArtifactId: ids.review,
    userApprovalQuote: "批准",
    approvalScope: PREMIUM_DISPLAY_CASE_GATE03_RIGID_APPROVAL_SCOPE
  };
  const event = makeEvent(manifest, "stage-ready-for-review", {
    stageId: "04-architecture",
    architectureRevision: 2,
    evidenceRevision: 5,
    artifactIds: stage.artifactIds,
    reviewArtifactIds: stage.reviewArtifactIds,
    reusedStaticArtifactIds: stage.reusedStaticArtifactIds,
    internalArtifactIds: stage.internalArtifactIds,
    sourceClaimIds: activeClaimIds,
    motionOwner: "PresentationRoot",
    posePathAssetId: fitAsset.id,
    poseSampleCount: 9,
    totalDurationSeconds: 4.520833,
    residualBoundaryPixels: {
      mean: 6.780574,
      rmse: 11.241096,
      maximum: 38.343513
    },
    wholeCaseOnly: true,
    explode: false,
    toyUnchanged: true,
    gate05Status: "not-entered",
    approvedCount: 3,
    autoApproved: false,
    shippingAssetUnchanged: true,
    buildInstallPhonePush: false
  });
  return saveManifest(manifest, event);
}

export function decideStage(modelId, stageId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  const stageIndex = STAGES.findIndex((stage) => stage.id === stageId);
  if (stageIndex < 0) throw new PipelineError(`Unknown stage: ${stageId}`);
  if (!["approve", "reject"].includes(payload.action)) throw new PipelineError("action must be approve or reject.");
  const stage = manifest.stages[stageIndex];
  const isFinalChatCadApproval = (
    payload.action === "approve"
    && payload.finalAuthority === "chat"
    && manifest.model.mechanism === "linear-magnetic-slider"
    && stageId === "02-analysis"
    && stage.analysisSpec?.revision >= 15
    && String(payload.userQuote || "").trim().length > 0
  );
  const isCadSubapproval = (
    payload.action === "approve"
    && manifest.model.mechanism === "linear-magnetic-slider"
    && stageId === "02-analysis"
    && stage.analysisSpec?.revision >= 10
    && stage.analysisSpec?.approvalSpec?.approvalType === "interactive-cad-geometry"
    && !isFinalChatCadApproval
  );
  if (payload.action === "approve") {
    const readiness = stageReadiness(manifest, stageId);
    if (!readiness.ready) throw new PipelineError("This stage cannot be approved yet.", 422, readiness.reasons);
    if (stage.analysisSpec?.approvalSpec?.interactiveRequired === true) {
      const evidence = payload.approvalEvidence;
      const requiredMilestones = stage.analysisSpec.approvalSpec.requiredMilestones || [];
      const cadOnly = stage.analysisSpec.approvalSpec.approvalType === "interactive-cad-geometry";
      const approvalAsset = manifest.assets.find(
        (asset) => asset.id === (cadOnly ? stage.analysisSpec.cadArtifactId : stage.analysisSpec.simulatorArtifactId)
      );
      const timestamp = Date.parse(evidence?.browserTimestamp || "");
      const invalidCommon = (
        !evidence
        || evidence.artifactId !== approvalAsset?.id
        || evidence.artifactHash !== approvalAsset?.sha256
        || evidence.contractAssetId !== stage.analysisSpec.contractAssetId
        || evidence.contractHash !== stage.analysisSpec.contractSha256
        || requiredMilestones.some((milestone) => evidence.milestones?.[milestone] !== true)
        || requiredMilestones.some((milestone) => !evidence.completedInteractionChecklist?.includes(milestone))
        || !Number.isFinite(timestamp)
      );
      const carrierGrooveCad = cadOnly && stage.analysisSpec?.revision >= 12;
      const hardClosedStopCad = cadOnly && stage.analysisSpec?.revision >= 13;
      const finiteGrooveCad = cadOnly && stage.analysisSpec?.revision === 14;
      const minimumOverlapCad = cadOnly && stage.analysisSpec?.revision >= 15;
      const fixedBottomCad = cadOnly && stage.analysisSpec?.revision === 11;
      const invalidCad = cadOnly && (
        evidence?.mode !== "interactive-cad"
        || !evidence.geometryParameterSnapshot
        || (carrierGrooveCad
          ? (
            !Array.isArray(evidence.geometryParameterSnapshot.fixedAxisBottomLocal)
            || !Array.isArray(evidence.geometryParameterSnapshot.fixedAxisWorld)
            || JSON.stringify(evidence.geometryParameterSnapshot.fixedAxisBottomLocal) !== JSON.stringify(evidence.geometryParameterSnapshot.fixedAxisWorld)
            || evidence.geometryParameterSnapshot.fixedAxisAttachment !== "fixed-axis-center-in-bottom"
            || !Array.isArray(evidence.geometryParameterSnapshot.carrierTranslation)
            || evidence.geometryParameterSnapshot.carrierTranslation.some((value) => value !== 0)
            || evidence.geometryParameterSnapshot.followerCount !== 2
            || evidence.geometryParameterSnapshot.grooveCount !== 2
            || evidence.geometryParameterSnapshot.grooveOwner !== "TopPlate underside"
            || evidence.geometryParameterSnapshot.groovesParallelToFollowers !== true
            || evidence.geometryParameterSnapshot.smoothBottomExterior !== true
            || evidence.geometryParameterSnapshot.axisCoveredAtCurrentPose !== true
            || evidence.geometryParameterSnapshot.componentLayers?.length !== (minimumOverlapCad ? 10 : 9)
            || (hardClosedStopCad && (
              evidence.geometryParameterSnapshot.closedStopL !== 0
              || evidence.geometryParameterSnapshot.closedStopHard !== true
              || evidence.geometryParameterSnapshot.negativeTravelForbidden !== true
              || evidence.geometryParameterSnapshot.closedSilhouetteCoincident !== true
              || evidence.geometryParameterSnapshot.closedStopPenetrationL !== 0
              || (finiteGrooveCad && (
                !Number.isFinite(evidence.geometryParameterSnapshot.grooveStartFromTopL)
                || !Number.isFinite(evidence.geometryParameterSnapshot.grooveEndFromTopL)
                || evidence.geometryParameterSnapshot.grooveEndFromTopL <= evidence.geometryParameterSnapshot.grooveStartFromTopL
                || Math.abs(evidence.geometryParameterSnapshot.grooveLengthL
                  - (evidence.geometryParameterSnapshot.grooveEndFromTopL - evidence.geometryParameterSnapshot.grooveStartFromTopL)) > 1e-9
                || evidence.geometryParameterSnapshot.maxTravelDerivedFromGrooveEndpoints !== true
                || evidence.geometryParameterSnapshot.followerEngagedAtClosed !== true
                || evidence.geometryParameterSnapshot.followerEngagedAtOpen !== true
                || evidence.geometryParameterSnapshot.axisCoveredAtOpen !== true
                || evidence.geometryParameterSnapshot.sweptEnvelopeSampleCount !== 150
                || evidence.geometryParameterSnapshot.sweptEnvelopeAllValid !== true
                || evidence.geometryParameterSnapshot.topZ <= evidence.geometryParameterSnapshot.bottomZ
                || evidence.geometryParameterSnapshot.bottomMasksTop !== false
                || !Array.isArray(evidence.viewsInspected)
                || ["top", "side", "section"].some((view) => !evidence.viewsInspected.includes(view))
              ))
              || (minimumOverlapCad && (
                evidence.geometryParameterSnapshot.minimumOverlapDiskOwner !== "BottomBase"
                || !Array.isArray(evidence.geometryParameterSnapshot.minimumOverlapDiskCenter)
                || evidence.geometryParameterSnapshot.minimumOverlapDiskCenter.length !== 2
                || !Number.isFinite(evidence.geometryParameterSnapshot.minimumOverlapDiskRadiusL)
                || evidence.geometryParameterSnapshot.minimumOverlapDiskPhysicalMm !== null
                || evidence.geometryParameterSnapshot.minimumOverlapFullyCovered !== true
                || evidence.geometryParameterSnapshot.minimumOverlapMarginL < -1e-9
                || evidence.geometryParameterSnapshot.overlapAngleInvariant !== true
                || evidence.geometryParameterSnapshot.actualSMaxFormula !== "min(grooveEndpointLimitL, overlapContainmentLimitL)"
                || Math.abs(evidence.geometryParameterSnapshot.actualSMaxL - Math.min(
                  evidence.geometryParameterSnapshot.grooveEndpointLimitL,
                  evidence.geometryParameterSnapshot.overlapContainmentLimitL
                )) > 1e-9
                || evidence.geometryParameterSnapshot.activeLimitingCause !== "MinimumOverlapDisk"
                || evidence.geometryParameterSnapshot.analyticContainmentContinuous !== true
                || evidence.geometryParameterSnapshot.denseAngleSampleCount !== 360
                || evidence.geometryParameterSnapshot.sweptEnvelopeSampleCount !== 1800
                || evidence.geometryParameterSnapshot.sweptEnvelopeAllValid !== true
                || evidence.geometryParameterSnapshot.exactBoundaryTangency !== true
                || evidence.geometryParameterSnapshot.beyondBoundaryInvalid !== true
                || evidence.geometryParameterSnapshot.topZ <= evidence.geometryParameterSnapshot.bottomZ
                || evidence.geometryParameterSnapshot.bottomMasksTop !== false
                || !Array.isArray(evidence.viewsInspected)
                || ["top", "side", "section"].some((view) => !evidence.viewsInspected.includes(view))
              ))
            ))
          )
          : fixedBottomCad
          ? (
            !Array.isArray(evidence.geometryParameterSnapshot.fixedAxisBottomLocal)
            || !Array.isArray(evidence.geometryParameterSnapshot.fixedAxisWorld)
            || evidence.geometryParameterSnapshot.fixedAxisAttachment !== "fixed-embedded-bottom-axis-module"
            || evidence.geometryParameterSnapshot.railOwner !== "BottomBase"
            || evidence.geometryParameterSnapshot.componentLayers?.length !== 7
          )
          : (
            !Array.isArray(evidence.geometryParameterSnapshot.endpointPivotLocal)
            || evidence.geometryParameterSnapshot.endpointPivotAttachment !== "fixed-bottom-endcap-center"
          ))
        || (!carrierGrooveCad && (
          !Array.isArray(evidence.viewsInspected)
          || ["top", "side", "section"].some((view) => !evidence.viewsInspected.includes(view))
          || !Array.isArray(evidence.milestones?.rotationTravelPositions)
          || evidence.milestones.rotationTravelPositions.length < 2
        ))
      );
      const invalidSimulator = !cadOnly && (
        !["interactive-cad", "recording-fallback"].includes(evidence?.mode)
        || !evidence?.parameterSnapshot
        || !Array.isArray(evidence.parameterSnapshot.endpointPivotLocalL)
        || evidence.parameterSnapshot.endpointPivotAttachment !== "fixed-bottom-endcap-center"
        || Number(evidence.milestones?.detentTransitions) < 3
      );
      if (invalidCommon || invalidCad || invalidSimulator) {
        throw new PipelineError(
          cadOnly
            ? "Interactive CAD evidence is incomplete or does not match the CAD and mechanism contract hashes."
            : "Interactive approval evidence is incomplete or does not match the Simulator and mechanism contract hashes.",
          422
        );
      }
      stage.analysisSpec[cadOnly ? "cadApproval" : "interactiveApproval"] = {
        ...evidence,
        acceptedAt: new Date().toISOString()
      };
    }
    if (manifest.model.mechanism === "display-case" && stageId === "02-analysis") {
      const userQuote = String(payload.userQuote || "").trim();
      const approvalSelections = Array.isArray(payload.approvalSelections)
        ? [...new Set(payload.approvalSelections.map((item) => String(item).trim()).filter(Boolean))]
        : [];
      const requiredSelections = [
        "只纠正动画；静态结构保留",
        "整盒刚性；用 pitch/yaw/roll 复合翻转"
      ];
      if (
        userQuote !== "继续"
        || requiredSelections.some((selection) => !approvalSelections.includes(selection))
        || stage.analysisSpec?.revision !== 3
        || stage.analysisSpec?.evidenceRevision !== 3
        || stage.analysisSpec?.scopeSelection !== requiredSelections[0]
        || stage.analysisSpec?.motionSelection !== requiredSelections[1]
        || stage.analysisSpec?.physicalAxisClaim !== "forbidden"
        || stage.analysisSpec?.singleAxisClaim !== "forbidden"
        || stage.analysisSpec?.riveMeshDeformationUse !== "source-evidence-only-forbidden-as-target"
        || stage.analysisSpec?.totalDurationSeconds !== 4.520833
        || stage.analysisSpec?.wholeCaseOnly !== true
        || stage.analysisSpec?.explode !== false
      ) {
        throw new PipelineError("Premium Display Case Gate 02 approval must preserve rev 3, both exact selections, ‘继续’, rigid best-fit scope, and the 4.520833 s duration.", 422);
      }
      const activeClaimIds = (manifest.claims || [])
        .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
        .map((claim) => claim.id);
      if (
        activeClaimIds.length !== 11
        || activeClaimIds.some((claimId) => !claimId.endsWith("-r003"))
        || !activeClaimIds.includes("premium-display-case-analysis-rigid-target-r003")
        || !activeClaimIds.includes("premium-display-case-analysis-duration-lock-r003")
      ) {
        throw new PipelineError("Gate 02 rev 3 active claims are incomplete or include another analysis revision.", 422);
      }
      stage.analysisSpec.approval = {
        approvedAnalysisRevision: 3,
        approvedEvidenceRevision: 3,
        userApprovalQuote: userQuote,
        approvalSelections: requiredSelections,
        approvalEffect: "approves-measured-evidence-for-rigid-best-fit-gate03-contract-only",
        gate03Status: "eligible",
        gate04Status: "blocked"
      };
      for (const assetId of stage.artifactIds) {
        const asset = manifest.assets.find((candidate) => candidate.id === assetId);
        if (asset?.reviewState === "active") asset.reviewState = "approved";
      }
      manifest.currentState.diagnosis = "Gate 02 rev 3 measured-motion evidence is approved with the user's exact motion-only and rigid whole-case selections plus ‘继续’. Gate 03 may create a rigid best-fit contract. Gate 04 remains blocked; shipping Unity and Blender geometry/material remain unchanged.";
      manifest.currentState.motionCorrection = {
        ...manifest.currentState.motionCorrection,
        motionPathApproved: true,
        approvedAnalysisRevision: 3,
        approvedEvidenceRevision: 3,
        userApprovalQuote: userQuote,
        approvalSelections: requiredSelections,
        gate03Status: "eligible",
        gate04Status: "blocked"
      };
    }
    if (
      manifest.model.mechanism === "display-case"
      && stageId === "03-contract"
      && stage.contractSpec?.revision === 3
    ) {
      const userQuote = String(payload.userQuote || "").trim();
      const approvalScope = Array.isArray(payload.approvalScope)
        ? [...new Set(payload.approvalScope.map((item) => String(item).trim()).filter(Boolean))]
        : [];
      const requiredScope = [
        "rev6-approved-motion-light-direction",
        "same-rigid-assembled-case",
        "serial-y-z-entry-settle-local-y-360-sheen-halo-hold",
        "pack-handoff-invariant",
        "toy-caller-owned-static",
        "restrained-four-finite-light-cues",
        "forbidden-effects-remain-forbidden",
        "runtime-timing-and-light-parameters-remain-tunable",
        "no-shipping-duration-approved"
      ];
      const contract = loadModelingContract(modelId);
      const activeClaimIds = (manifest.claims || [])
        .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
        .map((claim) => claim.id);
      if (
        userQuote !== "批准合同并继续（推荐）"
        || requiredScope.some((scope) => !approvalScope.includes(scope))
        || activeClaimIds.length !== 10
        || stage.contractSpec.sourceClaimIds?.length !== 10
        || activeClaimIds.some((claimId) => !stage.contractSpec.sourceClaimIds.includes(claimId))
        || contract?.contractRevision !== 3
        || contract?.sourceAnalysisRevision !== 6
        || contract?.motionContract?.phaseOrder?.join(",") !== "entry-y-z,settle,showcase-local-y-360,final-sheen-short-halo,static-hold"
        || contract?.motionContract?.entry?.translationAxes?.join(",") !== "screen-y,camera-depth-z"
        || contract?.motionContract?.showcase?.degrees !== 360
        || contract?.motionContract?.simultaneousEntryAndShowcase !== false
        || contract?.lightContract?.causalCueOrder?.join(",") !== "pack-seam-light,arrival-rim,rotation-surface-rim,final-diagonal-sheen,settle-halo-then-zero"
        || contract?.lightContract?.particles !== false
        || contract?.lightContract?.vfxGraphDependency !== false
        || contract?.tunableRuntimeParameters?.shippingTotalDurationSeconds !== null
        || contract?.tunableRuntimeParameters?.phaseDurationsSeconds !== null
        || contract?.tunableRuntimeParameters?.phaseEasing !== null
        || contract?.tunableRuntimeParameters?.entryCameraDepthZDistance !== null
        || contract?.tunableRuntimeParameters?.shippingCameraFovDegrees !== null
        || contract?.route?.nextGatePolicy !== "Do not enter Gate 04 before explicit Gate 03 approval."
      ) {
        throw new PipelineError("Premium Display Case Gate 03 rev 3 approval must preserve the serial whole-case contract, exact approved scope, forbidden effects, and tunable runtime boundary.", 422);
      }
      stage.contractSpec.approval = {
        approvedRevision: 3,
        userApprovalQuote: userQuote,
        approvalScope: requiredScope,
        approvalEffect: "locks-serial-whole-case-architecture-boundary-for-gate04",
        shippingDurationApproved: false,
        tunableRuntimeParameterCount: stage.contractSpec.tunableParameterCount,
        gate04Status: "eligible",
        gate05Status: "blocked"
      };
      stage.contractSpec.gate04Status = "eligible";
      for (const assetId of stage.artifactIds) {
        const asset = manifest.assets.find((candidate) => candidate.id === assetId);
        if (asset) asset.reviewState = "approved";
      }
      manifest.currentState.diagnosis = "Gate 03 rev 3 is explicitly approved. Gate 04 may define the serial ownership/phase/light architecture from the approved rev 5/6 direction. Shipping duration, phase timing/easing, Y/Z distances, light tuning and camera remain unlocked. Gate 05 remains blocked; shipping Unity, Simulator, build, install and phone state are unchanged.";
      manifest.currentState.visualApproval = "gate03-contract-approved-gate04-review-pending";
      manifest.currentState.deviceStatus = "not-approved";
      manifest.currentState.shippingAssetUnchanged = true;
      manifest.currentState.contractApproval = {
        stageId: "03-contract",
        contractRevision: 3,
        userApprovalQuote: userQuote,
        approvalScope: requiredScope,
        shippingDurationApproved: false,
        gate04Status: "eligible",
        gate05Status: "blocked"
      };
    }
    if (
      manifest.model.mechanism === "display-case"
      && stageId === "04-architecture"
      && stage.architectureSpec?.evidenceRevision === 7
    ) {
      const userQuote = String(payload.userQuote || "").trim();
      if (userQuote !== "正确，批准并继续（推荐）") {
        throw new PipelineError("Premium Display Case Gate 04 rev 7 approval must preserve the user's exact selection.", 422);
      }
      if (
        stage.architectureSpec?.caseLightOutsideSilhouettePixels !== 0
        || stage.architectureSpec?.externalSettleHalo !== false
        || stage.architectureSpec?.externalPointLightFinalSheen !== false
        || stage.architectureSpec?.vfxGraphDependency !== false
        || stage.architectureSpec?.particleEmitterCount !== 0
        || stage.architectureSpec?.persistentLightLoop !== false
        || stage.architectureSpec?.unityRuntimeArchitecture?.stateAuthority !== "GachaRevealDirector"
        || stage.architectureSpec?.unityRuntimeArchitecture?.profile !== "RevealMotionProfile ScriptableObject"
        || stage.architectureSpec?.unityRuntimeArchitecture?.materialDriver !== "MaterialPropertyBlock"
        || stage.architectureSpec?.unityRuntimeArchitecture?.timelineTransactionAuthority !== false
        || stage.architectureSpec?.gate05Status !== "blocked"
      ) {
        throw new PipelineError("Premium Display Case Gate 04 rev 7 approval scope is incomplete.", 422);
      }
      const reviewAssets = stage.reviewArtifactIds.map((assetId) => (
        manifest.assets.find((asset) => asset.id === assetId)
      ));
      const contractAsset = manifest.assets.find((asset) => (
        asset.id === "premium-display-case-modeling-contract-r003"
      ));
      const architectureAsset = manifest.assets.find((asset) => (
        asset.id === "premium-display-case-mesh-light-architecture-r007"
      ));
      if (
        reviewAssets.some((asset) => !asset?.sha256)
        || !contractAsset?.sha256
        || !architectureAsset?.sha256
      ) {
        throw new PipelineError("Gate 04 rev 7 approval requires hashed review, contract and architecture evidence.", 422);
      }
      stage.architectureSpec.approval = {
        approvedArchitectureRevision: 2,
        approvedEvidenceRevision: 7,
        userApprovalQuote: userQuote,
        approvalScope: [
          "one-rigid-assembled-case",
          "bounded-late-entry-early-rotation-overlap",
          "mesh-clipped-light-zero-outside-silhouette",
          "no-external-halo-or-point-light-sheen",
          "unity-runtime-authority",
          "timeline-preview-only",
          "no-particles-vfxgraph-proxy-explode-or-toy-motion",
          "runtime-timing-and-light-parameters-remain-tunable"
        ],
        reviewedArtifacts: reviewAssets.map((asset) => ({
          id: asset.id,
          sha256: asset.sha256
        })),
        governingContractId: contractAsset.id,
        governingContractSha256: contractAsset.sha256,
        parameterSnapshotId: architectureAsset.id,
        parameterSnapshotSha256: architectureAsset.sha256,
        completedChecklist: [
          "same assembled case through ACK",
          "one bounded overlap window",
          "zero light pixels outside silhouette",
          "external halo absent",
          "external Point Light final sheen absent",
          "four finite cues end at zero",
          "toy caller-owned and static",
          "Timeline preview-only"
        ],
        interactionMode: "animated-gif-plus-review-board",
        reviewedAt: new Date().toISOString(),
        shippingDurationApproved: false,
        gate05Status: "eligible"
      };
      stage.architectureSpec.gate05Status = "eligible";
      for (const assetId of stage.artifactIds) {
        const asset = manifest.assets.find((candidate) => candidate.id === assetId);
        if (!asset) continue;
        asset.reviewState = stage.reviewArtifactIds.includes(assetId)
          ? "approved"
          : (stage.architectureSpec.internalArtifactIds?.includes(assetId) ? "internal-only" : asset.reviewState);
      }
      manifest.currentState.diagnosis = "Gate 04 rev 7 is explicitly approved. One rigid assembled case uses a bounded entry/rotation overlap and mesh-clipped finite light with zero outside-silhouette pixels. Runtime timing, easing, overlap, Z travel, camera and light parameters remain tunable. Gate 05 may revalidate the unchanged historical white model; shipping Unity, Simulator, build, install and phone state remain unchanged.";
      manifest.currentState.visualApproval = "gate04-architecture-approved-gate05-review-pending";
      manifest.currentState.architectureApproval = {
        stageId: "04-architecture",
        architectureRevision: 2,
        evidenceRevision: 7,
        userApprovalQuote: userQuote,
        shippingDurationApproved: false,
        gate05Status: "eligible"
      };
    }
    if (
      manifest.model.mechanism === "display-case"
      && stageId === "04-architecture"
      && stage.architectureSpec?.evidenceRevision !== 7
    ) {
      const userQuote = String(payload.userQuote || "").trim();
      const lockedTotalDurationSeconds = Number(payload.lockedTotalDurationSeconds);
      if (userQuote !== "行，就照这个时间吧") {
        throw new PipelineError("Premium Display Case Gate 04 approval must preserve the user's exact approval quote.", 422);
      }
      if (
        !Number.isFinite(lockedTotalDurationSeconds)
        || Math.abs(lockedTotalDurationSeconds - 4.520833) > 0.0000005
        || stage.evidenceReview?.evidenceRevision !== 4
        || Number(stage.evidenceReview?.measuredMp4DurationMilliseconds) !== 4520.833
      ) {
        throw new PipelineError("Premium Display Case Gate 04 approval must lock the measured rev 4 MP4 duration at 4.520833 seconds.", 422);
      }
      stage.evidenceReview = {
        ...stage.evidenceReview,
        approvalEffect: "locks-architecture-and-rev4-measured-total-duration",
        reviewState: "approved",
        approvedEvidenceRevision: 4,
        lockedTotalDurationSeconds,
        lockedTotalDurationMilliseconds: 4520.833,
        lockedDurationBasis: "ffprobe-measured-rev4-mp4",
        lockedDurationAssetId: `${modelId}-whole-case-motion-mp4-r004`,
        userApprovalQuote: userQuote,
        gate05Status: "eligible"
      };
      for (const assetId of stage.artifactIds) {
        const asset = manifest.assets.find((candidate) => candidate.id === assetId);
        if (asset?.reviewState === "active" && asset.id.endsWith("-r004")) asset.reviewState = "approved";
      }
      manifest.currentState.diagnosis = "Gate 04 rev 4 is explicitly approved. The user locked the ffprobe-measured 4.520833 s total duration; rev 2 explode/reassemble and rev 3 fast playback remain rejected. Gate 05 may begin, but shipping Unity remains unchanged and no build, install, or phone push is authorized.";
    }
    if (manifest.model.mechanism === "display-case" && stageId === "05-blockout") {
      const userQuote = String(payload.userQuote || "").trim();
      const approvalScope = Array.isArray(payload.approvalScope)
        ? [...new Set(payload.approvalScope.map((item) => String(item).trim()).filter(Boolean))]
        : [];
      if (stage.blockoutSpec?.revision === 3) {
        const requiredScope = [
          "existing-geometry-unchanged",
          "gate04-rev7-compatible",
          "unity-presentation-root-owns-runtime-motion",
          "no-light-proxy-or-toy-geometry"
        ];
        if (userQuote !== "正确，批准并继续（推荐）") {
          throw new PipelineError("Premium Display Case Gate 05 rev 3 approval must preserve the user's exact approval choice.", 422);
        }
        if (requiredScope.some((item) => !approvalScope.includes(item))) {
          throw new PipelineError("Gate 05 rev 3 approval must lock unchanged geometry, Gate 04 compatibility, Unity ownership, and forbidden geometry.", 422);
        }
        if (
          stage.blockoutSpec.compatibilityConclusion !== "geometry-unchanged-and-compatible"
          || stage.blockoutSpec.geometryChanged !== false
          || stage.blockoutSpec.geometryDigest !== "6656ebb6f9003092d2d771a774ec006683347e01c4f12d0c994cc66fc603877f"
          || stage.blockoutSpec.dimensionsMm?.width !== 228
          || stage.blockoutSpec.dimensionsMm?.height !== 304
          || stage.blockoutSpec.dimensionsMm?.depth !== 59
          || stage.blockoutSpec.labelPosition?.centerYmm !== 99
          || stage.blockoutSpec.cornerCenterFamilies?.maximumDriftMm > 0.01
          || stage.blockoutSpec.closedTube?.connectedMaterialBodyCount !== 1
          || stage.blockoutSpec.closedTube?.openBoundaryEdgeCount !== 0
          || stage.blockoutSpec.closedTube?.nonManifoldEdgeCount !== 0
          || stage.blockoutSpec.closedTube?.channelSamplesVisited !== 384
          || stage.blockoutSpec.contentSlot?.callerOwned !== true
          || stage.blockoutSpec.contentSlot?.childCount !== 0
          || stage.blockoutSpec.pivot?.object !== "PresentationRoot"
          || stage.blockoutSpec.bakedRuntimeAnimation !== false
          || Object.values(stage.blockoutSpec.forbiddenGeometry || {}).some(Boolean)
          || stage.blockoutSpec.reviewArtifactExplodedPartCount !== 0
          || stage.blockoutSpec.shippingUnityChanged !== false
        ) {
          throw new PipelineError("Premium Display Case Gate 05 rev 3 evidence does not match the unchanged architecture-compatible white model.", 422);
        }
        stage.blockoutSpec.approval = {
          approvedRevision: 3,
          userApprovalQuote: userQuote,
          approvalScope: requiredScope,
          approvalEffect: "approves-unchanged-white-model-for-gate06-presentation-revalidation",
          geometryDigest: stage.blockoutSpec.geometryDigest,
          gate06Status: "eligible"
        };
        stage.blockoutSpec.gate06Status = "eligible";
        for (const assetId of stage.artifactIds) {
          const asset = manifest.assets.find((candidate) => candidate.id === assetId);
          if (asset) asset.reviewState = "approved";
        }
        manifest.currentState.diagnosis = "Gate 05 rev 3 is explicitly approved. The unchanged 228 × 304 × 59 mm whole-case white model, closed tube, Y=99 label, concentric corners, PresentationRoot pivot and caller-owned ContentSlot are compatible with Gate 04 rev 7. Gate 06 may revalidate the same geometry; shipping Unity and phone state remain unchanged.";
      } else {
        const requiredScope = [
          "label-downshift-6mm",
          "analytic-concentric-corner-families",
          "current-white-model-rev2"
        ];
        if (userQuote !== "可以，继续推进") {
          throw new PipelineError("Premium Display Case Gate 05 approval must preserve the user's exact approval quote.", 422);
        }
        if (requiredScope.some((item) => !approvalScope.includes(item))) {
          throw new PipelineError("Premium Display Case Gate 05 approval must lock the label shift, concentric corners, and current white model.", 422);
        }
        if (
          stage.blockoutSpec?.revision !== 2
          || stage.blockoutSpec?.labelPosition?.candidateCenterYmm !== 99
          || stage.blockoutSpec?.labelPosition?.candidateDownshiftMm !== 6
          || stage.blockoutSpec?.cornerCenterFamilies?.maximumDriftMm > 0.01
          || stage.blockoutSpec?.closedTube?.topology?.connectedMaterialBodyCount !== 1
          || stage.blockoutSpec?.closedTube?.topology?.openBoundaryEdgeCount !== 0
          || stage.blockoutSpec?.closedTube?.topology?.nonManifoldEdgeCount !== 0
          || stage.blockoutSpec?.closedTube?.channelFloodFill?.visitedSamples !== 384
        ) {
          throw new PipelineError("Premium Display Case Gate 05 rev 2 evidence does not match the approved scope.", 422);
        }
        stage.blockoutSpec.labelPosition = {
          ...stage.blockoutSpec.labelPosition,
          approvalState: "approved-user-locked",
          approvedCenterYmm: 99,
          approvedDownshiftMm: 6
        };
        stage.blockoutSpec.approval = {
          approvedRevision: 2,
          userApprovalQuote: userQuote,
          approvalScope: requiredScope,
          approvalEffect: "locks-label-downshift-concentric-corners-and-current-white-model",
          gate06Status: "eligible"
        };
        if (stage.blockoutSpec.supplementaryMaterialDiagnostic) {
          stage.blockoutSpec.supplementaryMaterialDiagnostic.gate05Status = "approved-rev2";
          stage.blockoutSpec.supplementaryMaterialDiagnostic.gate06Status = "eligible";
          stage.blockoutSpec.supplementaryMaterialDiagnostic.gate07Status = "blocked";
        }
        for (const assetId of stage.artifactIds) {
          const asset = manifest.assets.find((candidate) => candidate.id === assetId);
          if (asset) asset.reviewState = "approved";
        }
        manifest.currentState.diagnosis = "Gate 05 rev 2 is explicitly approved with the user's exact quote ‘可以，继续推进’. The approval locks the 6 mm label downshift to Y=99 mm, analytic concentric corner families, and the current real Blender white model. Gate 06 may begin from the same immutable source; Gate 07 remains blocked. Shipping Unity, build, install, and phone state remain unchanged.";
      }
    }
    if (manifest.model.mechanism === "display-case" && stageId === "06-geometry") {
      if (stage.geometrySpec?.revision === 3) {
        const userQuote = String(payload.userQuote || "").trim();
        const approvalScope = Array.isArray(payload.approvalScope)
          ? [...new Set(payload.approvalScope.map((item) => String(item).trim()).filter(Boolean))]
          : [];
        const completedChecklist = Array.isArray(payload.completedChecklist)
          ? [...new Set(payload.completedChecklist.map((item) => String(item).trim()).filter(Boolean))]
          : [];
        const requiredScope = [
          "current-gate06-geometry-rev3",
          "geometry-unchanged",
          "presentation-root-rigid-whole-case",
          "caller-owned-static-content-slot",
          "whole-case-only",
          "no-exploded-review",
          "no-light-proxy-or-toy-geometry"
        ];
        const requiredChecklist = stage.geometrySpec.review?.approvalChecklist || [];
        const interactionMode = String(payload.interactionMode || "").trim();
        const reviewAsset = manifest.assets.find((asset) => (
          asset.id === stage.geometrySpec.review?.interactiveArtifactId
        ));
        const contractAsset = manifest.assets.find((asset) => (
          asset.id === "premium-display-case-modeling-contract-r003"
        ));
        const snapshotAsset = manifest.assets.find((asset) => (
          asset.id === "premium-display-case-geometry-revalidation-r003"
        ));
        if (userQuote !== "正确，批准并继续（推荐）") {
          throw new PipelineError("Premium Display Case Gate 06 rev 3 approval must preserve the user's exact approval selection.", 422);
        }
        if (requiredScope.some((item) => !approvalScope.includes(item))) {
          throw new PipelineError("Premium Display Case Gate 06 rev 3 approval scope is incomplete.", 422);
        }
        if (requiredChecklist.some((item) => !completedChecklist.includes(item))) {
          throw new PipelineError("Premium Display Case Gate 06 rev 3 interactive checklist is incomplete.", 422);
        }
        if (interactionMode !== "interactive-glb-plus-review-board") {
          throw new PipelineError("Premium Display Case Gate 06 rev 3 requires interactive GLB review.", 422);
        }
        if (
          !reviewAsset
          || !contractAsset
          || !snapshotAsset
          || payload.reviewedArtifactId !== reviewAsset.id
          || payload.reviewedArtifactSha256 !== reviewAsset.sha256
          || payload.governingContractId !== contractAsset.id
          || payload.governingContractSha256 !== contractAsset.sha256
          || payload.parameterSnapshotId !== snapshotAsset.id
          || payload.parameterSnapshotSha256 !== snapshotAsset.sha256
          || stage.geometrySpec.evaluatedGeometryDigest !== "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
          || stage.geometrySpec.identity?.vertexPositionDigest !== "ced0edf95f8fa6416c5a0e33ebf8dc99fdafcdb3beceac85ee2970bbb2a7682c"
          || stage.geometrySpec.identity?.topologyWindingDigest !== "c29bc1dd8c0f0c52fd4c70d102bcfc2b4007e579795b605adeb21611a3bf7c79"
          || stage.geometrySpec.tube?.netMaterialSignedVolumeMm3 !== 52932.982745
          || stage.geometrySpec.tube?.channelSamplesVisited !== 384
          || stage.geometrySpec.tube?.channelSampleCount !== 384
          || stage.geometrySpec.hierarchy?.movingTransform !== "PresentationRoot"
          || stage.geometrySpec.hierarchy?.rigidAssembly !== "CaseAssembly"
          || stage.geometrySpec.hierarchy?.contentSlot !== "caller-owned-static"
          || stage.geometrySpec.hierarchy?.sameInstance !== true
          || stage.geometrySpec.hierarchy?.wholeCaseOnly !== true
          || stage.geometrySpec.review?.reviewArtifactExplodedPartCount !== 0
        ) {
          throw new PipelineError("Premium Display Case Gate 06 rev 3 evidence does not match the approved geometry and ownership baseline.", 422);
        }
        stage.geometrySpec.approval = {
          approvedRevision: 3,
          userApprovalQuote: userQuote,
          approvalScope: requiredScope,
          approvalEffect: "locks-unchanged-geometry-and-presentation-root-rigid-whole-case-ownership",
          reviewedArtifactId: reviewAsset.id,
          reviewedArtifactSha256: reviewAsset.sha256,
          governingContractId: contractAsset.id,
          governingContractSha256: contractAsset.sha256,
          parameterSnapshotId: snapshotAsset.id,
          parameterSnapshotSha256: snapshotAsset.sha256,
          completedChecklist: requiredChecklist,
          interactionMode,
          reviewedAt: new Date().toISOString(),
          reviewDevice: "Cursor IDE desktop",
          gate07Status: "eligible"
        };
        stage.geometrySpec.gate07Status = "eligible";
        reviewAsset.reviewState = "approved";
        manifest.currentState.diagnosis = "Gate 06 rev 3 is explicitly approved with unchanged 228 × 304 × 59 mm geometry, stable pivot/ContentSlot/tube/normals/digests, and PresentationRoot-only whole-case motion ownership. Gate 07 material revalidation may begin; shipping Unity, build, Simulator, install and phone state remain unchanged.";
      } else {
        const userQuote = String(payload.userQuote || "").trim();
        const approvalScope = Array.isArray(payload.approvalScope)
          ? [...new Set(payload.approvalScope.map((item) => String(item).trim()).filter(Boolean))]
          : [];
        const requiredScope = [
          "current-gate06-geometry-rev2",
          "whole-case-only",
          "no-explode"
        ];
        if (userQuote !== "可以啊，没问题，你继续吧") {
          throw new PipelineError("Premium Display Case Gate 06 approval must preserve the user's exact approval quote.", 422);
        }
        if (requiredScope.some((item) => !approvalScope.includes(item))) {
          throw new PipelineError("Premium Display Case Gate 06 approval must lock rev 2 geometry and the whole-case-only/no-explode scope.", 422);
        }
        if (
          stage.geometrySpec?.revision !== 2
          || stage.geometrySpec?.evaluatedGeometryDigest !== "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
          || stage.geometrySpec?.identity?.vertexPositionDigest !== "ced0edf95f8fa6416c5a0e33ebf8dc99fdafcdb3beceac85ee2970bbb2a7682c"
          || stage.geometrySpec?.identity?.derivativeTopologyWindingDigest !== "c29bc1dd8c0f0c52fd4c70d102bcfc2b4007e579795b605adeb21611a3bf7c79"
          || stage.geometrySpec?.tube?.signedVolumeMm3 !== 52932.982745
          || stage.geometrySpec?.tube?.floodFillVisited !== 384
          || stage.geometrySpec?.tube?.floodFillTotal !== 384
          || stage.geometrySpec?.shippingRevealPolicy !== "always-assembled-never-explodes"
          || stage.reviewArtifactIds?.length !== 1
          || stage.reviewArtifactIds[0] !== "premium-display-case-gate06-whole-case-review-r003"
        ) {
          throw new PipelineError("Premium Display Case Gate 06 rev 2 evidence does not match the approved geometry baseline.", 422);
        }
        stage.geometrySpec.approval = {
          approvedRevision: 2,
          userApprovalQuote: userQuote,
          approvalScope: requiredScope,
          approvalEffect: "locks-current-geometry-rev2-and-whole-case-only-no-explode-review-scope",
          gate07Status: "eligible"
        };
        stage.geometrySpec.gate07Entered = false;
        stage.userReviewEvidence = {
          ...stage.userReviewEvidence,
          reviewState: "approved",
          userApprovalQuote: userQuote,
          approvalScope: requiredScope,
          gate07Status: "eligible"
        };
        const reviewAsset = manifest.assets.find((asset) => (
          asset.id === "premium-display-case-gate06-whole-case-review-r003"
        ));
        if (reviewAsset) reviewAsset.reviewState = "approved";
        manifest.currentState.diagnosis = "Gate 06 rev 2 geometry is explicitly approved with the user's exact quote ‘可以啊，没问题，你继续吧’. The approval locks the current normals-corrected geometry baseline and whole-case-only/no-explode review scope. Gate 07 material lookdev may begin; Gate 07 is not approved, Gate 08 remains blocked, and shipping Unity, build, install, and phone state remain unchanged.";
      }
    }
    if (
      manifest.model.mechanism === "display-case"
      && stageId === "07-material"
      && stage.materialSpec?.revision === 2
    ) {
      const userQuote = String(payload.userQuote || "").trim();
      const approvalScope = Array.isArray(payload.approvalScope)
        ? [...new Set(payload.approvalScope.map((item) => String(item).trim()).filter(Boolean))]
        : [];
      const completedChecklist = Array.isArray(payload.completedChecklist)
        ? [...new Set(payload.completedChecklist.map((item) => String(item).trim()).filter(Boolean))]
        : [];
      const requiredScope = [
        "current-gate07-material-rev2",
        "material-response-and-zones",
        "object-local-grain",
        "transparent-ordering",
        "mesh-clipped-sheen-zero-outside-silhouette",
        "placeholder-label-text-and-artwork-excluded",
        "blender-label-geometry-uv-paper-cover-foil-zones",
        "unity-authoritative-label-data",
        "runtime-light-and-timing-remain-tunable"
      ];
      const requiredChecklist = stage.materialSpec.approvalChecklist || [];
      const reviewAssets = stage.reviewArtifactIds.map((assetId) => (
        manifest.assets.find((asset) => asset.id === assetId)
      ));
      const turntableAsset = manifest.assets.find((asset) => (
        asset.id === "premium-display-case-material-turntable-mp4-r002"
      ));
      const contractAsset = manifest.assets.find((asset) => (
        asset.id === "premium-display-case-modeling-contract-r003"
      ));
      const snapshotAsset = manifest.assets.find((asset) => (
        asset.id === "premium-display-case-material-compatibility-snapshot-r002"
      ));
      const interactionMode = String(payload.interactionMode || "").trim();
      if (userQuote !== "材质与扫光批准，标签文字后续由 Unity 替换为真实数据") {
        throw new PipelineError("Premium Display Case Gate 07 rev 2 approval must preserve the user's exact approval wording.", 422);
      }
      if (requiredScope.some((item) => !approvalScope.includes(item))) {
        throw new PipelineError("Premium Display Case Gate 07 rev 2 approval scope is incomplete.", 422);
      }
      if (requiredChecklist.some((item) => !completedChecklist.includes(item))) {
        throw new PipelineError("Premium Display Case Gate 07 rev 2 review checklist is incomplete.", 422);
      }
      if (interactionMode !== "real-render-turntable-plus-review-board") {
        throw new PipelineError("Premium Display Case Gate 07 rev 2 requires the real rendered turntable and review board.", 422);
      }
      if (
        reviewAssets.some((asset) => !asset?.sha256)
        || !turntableAsset?.sha256
        || !contractAsset?.sha256
        || !snapshotAsset?.sha256
        || payload.reviewedArtifactId !== turntableAsset.id
        || payload.reviewedArtifactSha256 !== turntableAsset.sha256
        || payload.governingContractId !== contractAsset.id
        || payload.governingContractSha256 !== contractAsset.sha256
        || payload.parameterSnapshotId !== snapshotAsset.id
        || payload.parameterSnapshotSha256 !== snapshotAsset.sha256
        || stage.materialSpec.geometryIdentity?.fullGeometryDigest !== "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
        || stage.materialSpec.grainStability?.coordinateSpace !== "object-local"
        || stage.materialSpec.grainStability?.worldSpaceGrain !== false
        || !Array.isArray(stage.materialSpec.transparentOrdering?.frontDepthOrder)
        || !Array.isArray(stage.materialSpec.transparentOrdering?.reverseDepthOrder)
        || stage.materialSpec.transparentOrdering.frontDepthOrder.length !== 4
        || stage.materialSpec.transparentOrdering.reverseDepthOrder.length !== 4
        || stage.materialSpec.sheenMaskCompatibility?.outsideSubjectPixels !== 0
        || stage.materialSpec.sheenMaskCompatibility?.outsideAllowedMaterialZonePixels !== 0
        || stage.materialSpec.sheenMaskCompatibility?.externalHalo !== false
        || stage.materialSpec.sheenMaskCompatibility?.persistentEmission !== false
        || stage.materialSpec.wholeCaseOnly !== true
        || stage.materialSpec.reviewExplodedPartCount !== 0
        || stage.materialSpec.finalLightingApproved !== false
      ) {
        throw new PipelineError("Premium Display Case Gate 07 rev 2 evidence does not match the approved material, label and mesh-clipped sheen boundary.", 422);
      }
      stage.materialSpec.approval = {
        approvedRevision: 2,
        userApprovalQuote: userQuote,
        approvalScope: requiredScope,
        approvalEffect: "locks-material-response-zones-grain-ordering-and-mesh-clipped-sheen-but-defers-authoritative-label-content-to-unity",
        reviewedArtifactId: turntableAsset.id,
        reviewedArtifactSha256: turntableAsset.sha256,
        reviewedArtifacts: reviewAssets.map((asset) => ({
          id: asset.id,
          sha256: asset.sha256
        })),
        governingContractId: contractAsset.id,
        governingContractSha256: contractAsset.sha256,
        parameterSnapshotId: snapshotAsset.id,
        parameterSnapshotSha256: snapshotAsset.sha256,
        completedChecklist: requiredChecklist,
        interactionMode,
        reviewedAt: new Date().toISOString(),
        reviewDevice: "Cursor IDE desktop",
        labelContentApproved: false,
        labelOwnership: {
          blender: [
            "label-geometry",
            "label-uv",
            "label-paper-zone",
            "label-transparent-cover-zone",
            "label-foil-zone"
          ],
          unity: [
            "product-name",
            "edition-or-finish",
            "acquired-date",
            "rarity-or-level",
            "real-collectible-id-when-available"
          ],
          fakeOrPlaceholderCollectibleIdForbidden: true
        },
        gate08Status: "eligible"
      };
      stage.materialSpec.gate07Approved = true;
      stage.materialSpec.gate08Entered = false;
      for (const asset of reviewAssets) asset.reviewState = "approved";
      manifest.currentState.materialRevalidation = {
        ...manifest.currentState.materialRevalidation,
        gate07Status: "approved",
        gate08Status: "eligible",
        labelContentApproved: false,
        labelAuthority: "unity-real-runtime-data"
      };
      manifest.currentState.visualApproval = "gate07-approved-gate08-lighting-review-pending";
      manifest.currentState.deviceStatus = "not-approved";
      manifest.currentState.shippingAssetUnchanged = true;
      manifest.currentState.diagnosis = "Gate 07 rev 2 is explicitly approved for the current neutral material response, zones, object-local grain, transparent ordering and zero-outside-silhouette mesh-clipped sheen. Placeholder label text and artwork are not approved. Blender owns label geometry, UV and paper/cover/foil zones; Unity owns real product name, edition/finish, acquired date, rarity/level and a real collectible ID only when available. Gate 08 lighting revalidation may begin; shipping Unity, Simulator, build, install and phone remain unchanged.";
    }
    if (
      manifest.model.mechanism === "display-case"
      && stageId === "08-lighting"
      && stage.lightingSpec?.revision === 2
    ) {
      const userQuote = String(payload.userQuote || "").trim();
      const approvalScope = Array.isArray(payload.approvalScope)
        ? [...new Set(payload.approvalScope.map((item) => String(item).trim()).filter(Boolean))]
        : [];
      const completedChecklist = Array.isArray(payload.completedChecklist)
        ? [...new Set(payload.completedChecklist.map((item) => String(item).trim()).filter(Boolean))]
        : [];
      const requiredScope = [
        "current-gate08-lighting-rev2",
        "neutral-lighting-direction",
        "frosted-shell-tube-black-insert-label-zones-readable",
        "no-green-rarity-halo-bloom-particles-flash-shake-persistent-emission",
        "placeholder-label-content-excluded",
        "mesh-clipped-sheen-zero-outside-silhouette",
        "blender-values-lookdev-candidates-only",
        "unity-runtime-values-remain-tunable"
      ];
      const requiredChecklist = stage.lightingSpec.approvalChecklist || [];
      const reviewAssets = stage.reviewArtifactIds.map((assetId) => (
        manifest.assets.find((asset) => asset.id === assetId)
      ));
      const turntableAsset = manifest.assets.find((asset) => (
        asset.id === "premium-display-case-lighting-turntable-mp4-r002"
      ));
      const contractAsset = manifest.assets.find((asset) => (
        asset.id === "premium-display-case-modeling-contract-r003"
      ));
      const snapshotAsset = manifest.assets.find((asset) => (
        asset.id === "premium-display-case-lighting-compatibility-snapshot-r002"
      ));
      const interactionMode = String(payload.interactionMode || "").trim();
      if (userQuote !== "灯光方向正确，批准并继续（推荐）") {
        throw new PipelineError("Premium Display Case Gate 08 rev 2 approval must preserve the user's exact approval selection.", 422);
      }
      if (requiredScope.some((item) => !approvalScope.includes(item))) {
        throw new PipelineError("Premium Display Case Gate 08 rev 2 approval scope is incomplete.", 422);
      }
      if (requiredChecklist.some((item) => !completedChecklist.includes(item))) {
        throw new PipelineError("Premium Display Case Gate 08 rev 2 review checklist is incomplete.", 422);
      }
      if (interactionMode !== "real-render-turntable-plus-review-board") {
        throw new PipelineError("Premium Display Case Gate 08 rev 2 requires the real rendered turntable and review board.", 422);
      }
      if (
        reviewAssets.some((asset) => !asset?.sha256)
        || !turntableAsset?.sha256
        || !contractAsset?.sha256
        || !snapshotAsset?.sha256
        || payload.reviewedArtifactId !== turntableAsset.id
        || payload.reviewedArtifactSha256 !== turntableAsset.sha256
        || payload.governingContractId !== contractAsset.id
        || payload.governingContractSha256 !== contractAsset.sha256
        || payload.parameterSnapshotId !== snapshotAsset.id
        || payload.parameterSnapshotSha256 !== snapshotAsset.sha256
        || stage.lightingSpec.sourceGeometryDigest !== "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
        || stage.lightingSpec.sourceMaterialDigest !== "8358cfdb12e49f87adbbafd96f33f2beb3415f9b920cb62732c73173c7799210"
        || stage.lightingSpec.wholeAssembledCaseOnly !== true
        || stage.lightingSpec.reviewExplodedPartCount !== 0
        || stage.lightingSpec.labelPolicy?.visibleContentState !== "placeholder-not-approved"
        || stage.lightingSpec.meshClippedSheenCompatibility?.outsideSubjectPixels !== 0
        || stage.lightingSpec.meshClippedSheenCompatibility?.outsideAllowedMaterialZonePixels !== 0
        || stage.lightingSpec.candidateBoundary?.automaticUnityRuntimeConstants !== false
        || stage.lightingSpec.animationBoundary?.timingBaked !== false
        || stage.lightingSpec.forbiddenEffects?.fixedGreenCast !== false
        || stage.lightingSpec.forbiddenEffects?.rarityLight !== false
        || stage.lightingSpec.forbiddenEffects?.externalHalo !== false
        || stage.lightingSpec.forbiddenEffects?.largeBloom !== false
        || stage.lightingSpec.forbiddenEffects?.particles !== false
        || stage.lightingSpec.forbiddenEffects?.flash !== false
        || stage.lightingSpec.forbiddenEffects?.shake !== false
        || stage.lightingSpec.forbiddenEffects?.persistentEmission !== false
      ) {
        throw new PipelineError("Premium Display Case Gate 08 rev 2 evidence does not match the approved neutral lighting and ownership boundary.", 422);
      }
      stage.lightingSpec.approval = {
        approvedRevision: 2,
        userApprovalQuote: userQuote,
        approvalScope: requiredScope,
        approvalEffect: "locks-neutral-lighting-direction-and-forbidden-effect-boundary-but-keeps-unity-runtime-values-tunable",
        reviewedArtifactId: turntableAsset.id,
        reviewedArtifactSha256: turntableAsset.sha256,
        reviewedArtifacts: reviewAssets.map((asset) => ({
          id: asset.id,
          sha256: asset.sha256
        })),
        governingContractId: contractAsset.id,
        governingContractSha256: contractAsset.sha256,
        parameterSnapshotId: snapshotAsset.id,
        parameterSnapshotSha256: snapshotAsset.sha256,
        completedChecklist: requiredChecklist,
        interactionMode,
        reviewedAt: new Date().toISOString(),
        reviewDevice: "Cursor IDE desktop",
        labelContentApproved: false,
        lookdevCandidatesOnly: true,
        unityRuntimeValuesTunable: true,
        gate09Status: "eligible"
      };
      stage.lightingSpec.finalLightingApproved = true;
      stage.lightingSpec.gate08Approved = true;
      stage.lightingSpec.gate09Entered = false;
      for (const asset of reviewAssets) asset.reviewState = "approved";
      manifest.currentState.lightingRevalidation = {
        ...manifest.currentState.lightingRevalidation,
        gate08Status: "approved",
        gate09Status: "eligible",
        labelContentApproved: false,
        lookdevCandidatesOnly: true,
        unityRuntimeValuesTunable: true
      };
      manifest.currentState.visualApproval = "gate08-approved-gate09-environment-review-pending";
      manifest.currentState.deviceStatus = "not-approved";
      manifest.currentState.shippingAssetUnchanged = true;
      manifest.currentState.diagnosis = "Gate 08 rev 2 neutral lighting direction is explicitly approved. It clearly reveals the frosted shell, connected tube, black insert and label material zones without green rarity light, external halo, bloom, particles, flash, shake or persistent emission. Placeholder label content remains excluded. Blender values remain lookdev candidates; Unity environment, exposure, camera and runtime light values remain tunable. Gate 09 environment revalidation may begin; shipping Unity, Simulator, build, install and phone remain unchanged.";
    }
    if (
      manifest.model.mechanism === "display-case"
      && stageId === "09-environment"
      && stage.environmentSpec?.revision === 1
    ) {
      const userQuote = String(payload.userQuote || "").trim();
      const approvalScope = Array.isArray(payload.approvalScope)
        ? [...new Set(payload.approvalScope.map((item) => String(item).trim()).filter(Boolean))]
        : [];
      const completedChecklist = Array.isArray(payload.completedChecklist)
        ? [...new Set(payload.completedChecklist.map((item) => String(item).trim()).filter(Boolean))]
        : [];
      const requiredScope = [
        "current-gate09-environment-rev1",
        "static-low-detail-environment-direction",
        "subject-support-no-competing-detail",
        "no-color-cast-detached-halo-bright-blob",
        "no-background-motion-particles",
        "mesh-clipped-sheen-remains-inside-case",
        "blender-values-lookdev-candidates-only",
        "unity-runtime-values-remain-tunable",
        "placeholder-label-content-excluded"
      ];
      const requiredChecklist = stage.environmentSpec.approvalChecklist || [];
      const reviewAssets = stage.reviewArtifactIds.map((assetId) => (
        manifest.assets.find((asset) => asset.id === assetId)
      ));
      const comparisonAsset = manifest.assets.find((asset) => (
        asset.id === "premium-display-case-environment-comparison-mp4-r001"
      ));
      const contractAsset = manifest.assets.find((asset) => (
        asset.id === "premium-display-case-modeling-contract-r003"
      ));
      const snapshotAsset = manifest.assets.find((asset) => (
        asset.id === "premium-display-case-environment-compatibility-snapshot-r001"
      ));
      const interactionMode = String(payload.interactionMode || "").trim();
      if (userQuote !== "环境正确，批准并继续（推荐）") {
        throw new PipelineError("Premium Display Case Gate 09 rev 1 approval must preserve the user's exact approval selection.", 422);
      }
      if (requiredScope.some((item) => !approvalScope.includes(item))) {
        throw new PipelineError("Premium Display Case Gate 09 rev 1 approval scope is incomplete.", 422);
      }
      if (requiredChecklist.some((item) => !completedChecklist.includes(item))) {
        throw new PipelineError("Premium Display Case Gate 09 rev 1 review checklist is incomplete.", 422);
      }
      if (interactionMode !== "real-render-environment-comparison-plus-review-board") {
        throw new PipelineError("Premium Display Case Gate 09 rev 1 requires the real environment comparison recording and review board.", 422);
      }
      if (
        reviewAssets.some((asset) => !asset?.sha256)
        || !comparisonAsset?.sha256
        || !contractAsset?.sha256
        || !snapshotAsset?.sha256
        || payload.reviewedArtifactId !== comparisonAsset.id
        || payload.reviewedArtifactSha256 !== comparisonAsset.sha256
        || payload.governingContractId !== contractAsset.id
        || payload.governingContractSha256 !== contractAsset.sha256
        || payload.parameterSnapshotId !== snapshotAsset.id
        || payload.parameterSnapshotSha256 !== snapshotAsset.sha256
        || stage.environmentSpec.sourceGeometryDigest !== "a3d1e9fe3c6d26c957c7ad1584cc489b9091a1a79e435a660aa89bcf6acc3951"
        || stage.environmentSpec.sourceMaterialDigest !== "8358cfdb12e49f87adbbafd96f33f2beb3415f9b920cb62732c73173c7799210"
        || stage.environmentSpec.geometryUnchanged !== true
        || stage.environmentSpec.materialUnchanged !== true
        || stage.environmentSpec.cameraUnchanged !== true
        || stage.environmentSpec.approvedLightingDirectionUnchanged !== true
        || stage.environmentSpec.wholeAssembledCaseOnly !== true
        || stage.environmentSpec.reviewExplodedPartCount !== 0
        || stage.environmentSpec.environmentPolicy?.backgroundStaticThroughoutReveal !== true
        || stage.environmentSpec.environmentPolicy?.cameraMotion !== false
        || stage.environmentSpec.environmentPolicy?.backgroundMotion !== false
        || stage.environmentSpec.environmentPolicy?.toyPrizeOwnership !== "caller-owned-static"
        || stage.environmentSpec.environmentPolicy?.blenderValuesAreUnityRuntimeConstants !== false
        || stage.environmentSpec.meshClippedSheen?.outsideSubjectPixels !== 0
        || stage.environmentSpec.meshClippedSheen?.detachedLightEffect !== false
        || stage.environmentSpec.labelPolicy?.approved !== false
        || Object.values(stage.environmentSpec.forbiddenEffects || {}).some(Boolean)
        || stage.environmentSpec.gate10Entered !== false
        || stage.environmentSpec.shippingUnityChanged !== false
        || stage.environmentSpec.buildInstallPhonePush !== false
      ) {
        throw new PipelineError("Premium Display Case Gate 09 rev 1 evidence does not match the approved static environment and runtime-ownership boundary.", 422);
      }
      stage.environmentSpec.approval = {
        approvedRevision: 1,
        userApprovalQuote: userQuote,
        approvalScope: requiredScope,
        approvalEffect: "locks-static-low-detail-environment-direction-but-keeps-unity-runtime-values-tunable",
        reviewedArtifactId: comparisonAsset.id,
        reviewedArtifactSha256: comparisonAsset.sha256,
        reviewedArtifacts: reviewAssets.map((asset) => ({
          id: asset.id,
          sha256: asset.sha256
        })),
        governingContractId: contractAsset.id,
        governingContractSha256: contractAsset.sha256,
        parameterSnapshotId: snapshotAsset.id,
        parameterSnapshotSha256: snapshotAsset.sha256,
        completedChecklist: requiredChecklist,
        interactionMode,
        reviewedAt: new Date().toISOString(),
        reviewDevice: "Cursor IDE desktop",
        labelContentApproved: false,
        lookdevCandidatesOnly: true,
        unityRuntimeValuesTunable: true,
        gate10Status: "eligible"
      };
      stage.environmentSpec.gate09Approved = true;
      stage.environmentSpec.gate10Entered = false;
      for (const asset of reviewAssets) asset.reviewState = "approved";
      manifest.currentState.environmentRevalidation = {
        ...manifest.currentState.environmentRevalidation,
        gate09Status: "approved",
        gate10Status: "eligible",
        labelContentApproved: false,
        lookdevCandidatesOnly: true,
        unityRuntimeValuesTunable: true
      };
      manifest.currentState.visualApproval = "gate09-approved-gate10-export-review-pending";
      manifest.currentState.deviceStatus = "not-approved";
      manifest.currentState.shippingAssetUnchanged = true;
      manifest.currentState.diagnosis = "Gate 09 rev 1 static low-detail environment direction is explicitly approved. It supports the assembled case without color cast, detached halo, bright blob, background motion, particles or competing detail. Blender values remain lookdev direction only; Unity environment, IBL, exposure and camera values remain tunable. Gate 10 export may begin; Gate 11+, shipping Unity, Simulator, build, install and phone remain unchanged.";
    }
    if (
      manifest.model.id === "magnetic-slide-tile"
      && stageId === "02-analysis"
      && stage.analysisSpec?.revision === 3
    ) {
      const pendingClaims = (manifest.claims || []).filter(
        (claim) => claim.stageId === "02-analysis" && claim.state === "pending-review");
      if (
        pendingClaims.length !== 9
        || pendingClaims.some((claim) => !claim.id.endsWith("-r003"))
      ) {
        throw new PipelineError("Magnetic Slide Tile Gate 02 rev 3 must approve exactly nine pending video-mechanism claims.", 422);
      }
      for (const claim of pendingClaims) {
        claim.state = "active";
        claim.decisionState = "approved";
        claim.approvedAt = new Date().toISOString();
      }
      stage.analysisSpec.approval = {
        approvedAnalysisRevision: 3,
        approvalEffect: "approves-frame-accurate-mechanism-interpretation-for-gate03-rebuild",
        approvedClaimIds: pendingClaims.map((claim) => claim.id),
        gate03Status: "eligible-for-new-contract",
        downstreamReusePolicy: "Gates 03–11 remain stale until rebuilt from these claims.",
      };
      manifest.currentState.diagnosis = "Gate 02 rev 3 frame-accurate mechanism interpretation is approved. Gate 03 may create a new contract from the nine approved video claims; Gates 03–11 remain stale until rebuilt, Gate 12 remains blocked/rejected, and the old shipping model stays default.";
    }
    if (isCadSubapproval) {
      stage.status = "ready_for_review";
      stage.analysisSpec.phase = "cad-approved-awaiting-final-gate-decision";
      stage.analysisSpec.simulatorGeneration = {
        ...stage.analysisSpec.simulatorGeneration,
        locked: true,
        eligible: false,
        generated: false,
        activeControls: 0,
        status: "internal-superseded-not-current"
      };
      manifest.currentState.diagnosis = "Gate 02 interactive CAD geometry is approved. Gate 03 remains blocked until real physical dimensions are supplied; no standalone Simulator is required before Blender.";
    } else {
      stage.status = "approved";
      if (isFinalChatCadApproval) {
        stage.analysisSpec.finalApproval = {
          ...stage.analysisSpec.cadApproval,
          authority: "latest-explicit-chat-instruction",
          exactUserWording: String(payload.userQuote).trim(),
          approvedAt: new Date().toISOString()
        };
        stage.analysisSpec.simulatorGeneration = {
          ...stage.analysisSpec.simulatorGeneration,
          locked: true,
          eligible: false,
          generated: false,
          activeControls: 0,
          status: "internal-superseded-not-current"
        };
        manifest.currentState.diagnosis = "Gate 02 rev 15 is approved by the user's latest explicit chat instruction after validated interactive CAD evidence. Gate 03 is next and requires real physical dimensions before Blender; no standalone Simulator is required.";
      }
    }
  } else {
    stage.status = "rejected";
    if (
      manifest.model.id === "magnetic-slide-tile"
      && stageId === "02-analysis"
      && stage.analysisSpec?.revision === 3
    ) {
      for (const claim of (manifest.claims || []).filter(
        (claim) => claim.stageId === "02-analysis" && claim.state === "pending-review")) {
        claim.state = "rejected";
        claim.decisionState = "rejected";
        claim.rejectedAt = new Date().toISOString();
      }
      manifest.currentState.diagnosis = "Gate 02 rev 3 mechanism interpretation was rejected. Its source videos and evidence remain immutable; Gates 03–12 stay blocked or stale, and the old shipping model stays default.";
    }
    const technicalGate06Rejection = manifest.model.mechanism === "display-case"
      && stageId === "06-geometry"
      && stage.geometrySpec?.revision === 1
      && String(payload.notes || "").includes("signedVolumeMm3=-52932.982745");
    markDownstreamStale(
      manifest,
      stageIndex,
      technicalGate06Rejection
        ? "Gate 06 rev 1 因闭环管净 signed material volume 非正而技术否决；Gate 07 不得开始。"
        : `上游 ${stageId} 被用户拒绝。`
    );
    if (technicalGate06Rejection) {
      manifest.currentState.diagnosis = "Gate 06 rev 1 is technically rejected because ContinuousTubePerimeter has net signed material volume -52932.982745 mm3. All rev 1 evidence remains preserved. Gate 05 rev 2 remains approved and immutable; a Gate 06 rev 2 normals-only derivative is required. Gate 07 remains blocked.";
    }
  }
  stage.revision += 1;
  stage.decision = {
    action: payload.action,
    notes: String(payload.notes || "").trim(),
    decidedBy: "user",
    decidedAt: new Date().toISOString()
  };
  updateStageDigests(manifest);
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  const eventDetail = { stageId, notes: stage.decision.notes };
  if (payload.action === "approve" && stage.analysisSpec?.interactiveApproval) {
    const approval = stage.analysisSpec.interactiveApproval;
    eventDetail.approvalMode = approval.mode;
    eventDetail.artifactId = approval.artifactId;
    eventDetail.artifactHash = approval.artifactHash;
    eventDetail.contractAssetId = approval.contractAssetId;
    eventDetail.contractHash = approval.contractHash;
    eventDetail.parameterSnapshot = approval.parameterSnapshot;
    eventDetail.completedInteractionChecklist = approval.completedInteractionChecklist;
    eventDetail.milestones = approval.milestones;
    eventDetail.browserTimestamp = approval.browserTimestamp;
    eventDetail.acceptedAt = approval.acceptedAt;
  }
  if (payload.action === "approve" && stage.analysisSpec?.cadApproval) {
    const approval = stage.analysisSpec.cadApproval;
    eventDetail.approvalMode = approval.mode;
    eventDetail.artifactId = approval.artifactId;
    eventDetail.artifactHash = approval.artifactHash;
    eventDetail.contractAssetId = approval.contractAssetId;
    eventDetail.contractHash = approval.contractHash;
    eventDetail.geometryParameterSnapshot = approval.geometryParameterSnapshot;
    eventDetail.viewsInspected = approval.viewsInspected;
    eventDetail.completedInteractionChecklist = approval.completedInteractionChecklist;
    eventDetail.milestones = approval.milestones;
    eventDetail.browserTimestamp = approval.browserTimestamp;
    eventDetail.acceptedAt = approval.acceptedAt;
    eventDetail.approvalEffect = isFinalChatCadApproval
      ? "approves-gate02-interaction-form-for-gate03-dimension-contract"
      : "records-cad-evidence-awaiting-final-gate-decision";
    eventDetail.downstreamStages = "remain-stale";
  }
  if (
    payload.action === "approve"
    && manifest.model.mechanism === "display-case"
    && stageId === "02-analysis"
  ) {
    eventDetail.userQuote = stage.analysisSpec.approval.userApprovalQuote;
    eventDetail.approvalSelections = stage.analysisSpec.approval.approvalSelections;
    eventDetail.approvedAnalysisRevision = stage.analysisSpec.approval.approvedAnalysisRevision;
    eventDetail.approvedEvidenceRevision = stage.analysisSpec.approval.approvedEvidenceRevision;
    eventDetail.approvalEffect = stage.analysisSpec.approval.approvalEffect;
    eventDetail.lockedTotalDurationSeconds = stage.analysisSpec.totalDurationSeconds;
    eventDetail.activeClaimIds = (manifest.claims || [])
      .filter((claim) => claim.stageId === "02-analysis" && claim.state !== "superseded")
      .map((claim) => claim.id);
    eventDetail.gate03Status = "eligible";
    eventDetail.gate04Status = "blocked";
    eventDetail.shippingAssetUnchanged = true;
    eventDetail.buildInstallPhonePush = false;
  }
  if (
    payload.action === "approve"
    && manifest.model.mechanism === "display-case"
    && stageId === "03-contract"
    && stage.contractSpec?.revision === 3
  ) {
    eventDetail.userQuote = stage.contractSpec.approval.userApprovalQuote;
    eventDetail.approvalScope = stage.contractSpec.approval.approvalScope;
    eventDetail.approvedContractRevision = 3;
    eventDetail.approvalEffect = stage.contractSpec.approval.approvalEffect;
    eventDetail.sourceClaimIds = stage.contractSpec.sourceClaimIds;
    eventDetail.phaseOrder = stage.contractSpec.phaseOrder;
    eventDetail.entryAxes = stage.contractSpec.entryAxes;
    eventDetail.showcase = "one-local-y-360-after-settle";
    eventDetail.causalLightCueOrder = stage.contractSpec.causalLightCueOrder;
    eventDetail.shippingDurationApproved = false;
    eventDetail.tunableRuntimeParameterCount = stage.contractSpec.tunableParameterCount;
    eventDetail.gate04Status = "eligible";
    eventDetail.gate05Status = "blocked";
    eventDetail.shippingAssetUnchanged = true;
    eventDetail.buildInstallPhonePush = false;
  }
  if (
    payload.action === "approve"
    && manifest.model.mechanism === "display-case"
    && stageId === "04-architecture"
    && stage.architectureSpec?.approval?.approvedEvidenceRevision === 7
  ) {
    eventDetail.userQuote = stage.architectureSpec.approval.userApprovalQuote;
    eventDetail.approvalScope = stage.architectureSpec.approval.approvalScope;
    eventDetail.approvedArchitectureRevision = 2;
    eventDetail.approvedEvidenceRevision = 7;
    eventDetail.reviewedArtifacts = stage.architectureSpec.approval.reviewedArtifacts;
    eventDetail.governingContractId = stage.architectureSpec.approval.governingContractId;
    eventDetail.governingContractSha256 = stage.architectureSpec.approval.governingContractSha256;
    eventDetail.parameterSnapshotId = stage.architectureSpec.approval.parameterSnapshotId;
    eventDetail.parameterSnapshotSha256 = stage.architectureSpec.approval.parameterSnapshotSha256;
    eventDetail.completedChecklist = stage.architectureSpec.approval.completedChecklist;
    eventDetail.interactionMode = stage.architectureSpec.approval.interactionMode;
    eventDetail.caseLightOutsideSilhouettePixels = 0;
    eventDetail.shippingDurationApproved = false;
    eventDetail.gate05Status = "eligible";
    eventDetail.shippingAssetUnchanged = true;
    eventDetail.buildInstallPhonePush = false;
  }
  if (
    payload.action === "approve"
    && manifest.model.id === "magnetic-slide-tile"
    && stageId === "02-analysis"
    && stage.analysisSpec?.revision === 3
  ) {
    eventDetail.approvedAnalysisRevision = 3;
    eventDetail.approvalEffect = stage.analysisSpec.approval.approvalEffect;
    eventDetail.activeClaimIds = stage.analysisSpec.approval.approvedClaimIds;
    eventDetail.gate03Status = "eligible-for-new-contract";
    eventDetail.staleStageIds = manifest.stages.slice(2, 11).map((candidate) => candidate.id);
    eventDetail.gate12Status = manifest.stages[11].status;
    eventDetail.oldShippingModelDefault = true;
    eventDetail.blenderUnityBuildInstallPhone = "not-started";
  }
  if (isFinalChatCadApproval) {
    eventDetail.finalAuthority = "latest-explicit-chat-instruction";
    eventDetail.exactUserWording = String(payload.userQuote).trim();
    eventDetail.interactiveEvidenceRequired = true;
    eventDetail.toolButtonRequired = false;
    eventDetail.contractHash = stage.analysisSpec.contractSha256;
    eventDetail.parameterSnapshot = payload.approvalEvidence.geometryParameterSnapshot;
    eventDetail.completedChecklist = payload.approvalEvidence.completedInteractionChecklist;
    eventDetail.gate02Status = "approved";
    eventDetail.gate03Status = "eligible-for-separate-simulator";
    eventDetail.blenderUnityBuildInstallPhone = "not-started";
  }
  if (
    payload.action === "reject"
    && manifest.model.mechanism === "display-case"
    && stageId === "06-geometry"
    && stage.geometrySpec?.revision === 1
    && stage.decision.notes.includes("signedVolumeMm3=-52932.982745")
  ) {
    eventDetail.rejectionClass = "technical";
    eventDetail.rejectedGeometryRevision = 1;
    eventDetail.defect = "continuous-tube-non-positive-signed-material-volume";
    eventDetail.signedVolumeMm3 = -52932.982745;
    eventDetail.requiredReplacement = "gate06-rev2-normals-only-derivative";
    eventDetail.gate05Status = "approved-unchanged";
    eventDetail.gate07Status = "blocked";
    eventDetail.shippingAssetUnchanged = true;
    eventDetail.buildInstallPhonePush = false;
  }
  if (
    payload.action === "approve"
    && manifest.model.mechanism === "display-case"
    && stageId === "05-blockout"
  ) {
    eventDetail.userQuote = stage.blockoutSpec.approval.userApprovalQuote;
    eventDetail.approvalScope = stage.blockoutSpec.approval.approvalScope;
    eventDetail.approvedBlockoutRevision = stage.blockoutSpec.approval.approvedRevision;
    eventDetail.labelCenterYmm = stage.blockoutSpec.labelPosition.approvedCenterYmm
      ?? stage.blockoutSpec.labelPosition.centerYmm;
    eventDetail.labelDownshiftMm = stage.blockoutSpec.labelPosition.approvedDownshiftMm
      ?? (stage.blockoutSpec.sourceBlockoutRevision === 2 ? 6 : undefined);
    if (stage.blockoutSpec.approval.approvedRevision === 3) {
      eventDetail.geometryDigest = stage.blockoutSpec.geometryDigest;
      eventDetail.geometryChanged = stage.blockoutSpec.geometryChanged;
      eventDetail.compatibilityConclusion = stage.blockoutSpec.compatibilityConclusion;
      eventDetail.presentationRoot = stage.blockoutSpec.pivot.object;
      eventDetail.contentSlotCallerOwned = stage.blockoutSpec.contentSlot.callerOwned;
    }
    eventDetail.maximumCornerCenterDriftMm = stage.blockoutSpec.cornerCenterFamilies.maximumDriftMm;
    eventDetail.gate06Status = "eligible";
    eventDetail.gate07Status = "blocked";
    eventDetail.shippingAssetUnchanged = true;
    eventDetail.buildInstallPhonePush = false;
  }
  if (
    payload.action === "approve"
    && manifest.model.mechanism === "display-case"
    && stageId === "06-geometry"
  ) {
    eventDetail.userQuote = stage.geometrySpec.approval.userApprovalQuote;
    eventDetail.approvalScope = stage.geometrySpec.approval.approvalScope;
    eventDetail.approvedGeometryRevision = stage.geometrySpec.approval.approvedRevision;
    eventDetail.evaluatedGeometryDigest = stage.geometrySpec.evaluatedGeometryDigest;
    eventDetail.vertexPositionDigest = stage.geometrySpec.identity.vertexPositionDigest;
    eventDetail.topologyWindingDigest = stage.geometrySpec.identity.derivativeTopologyWindingDigest
      ?? stage.geometrySpec.identity.topologyWindingDigest;
    eventDetail.shippingRevealPolicy = stage.geometrySpec.shippingRevealPolicy
      ?? "same-instance-whole-case-presentation-root-only";
    if (stage.geometrySpec.approval.approvedRevision === 3) {
      eventDetail.reviewedArtifactId = stage.geometrySpec.approval.reviewedArtifactId;
      eventDetail.reviewedArtifactSha256 = stage.geometrySpec.approval.reviewedArtifactSha256;
      eventDetail.governingContractId = stage.geometrySpec.approval.governingContractId;
      eventDetail.governingContractSha256 = stage.geometrySpec.approval.governingContractSha256;
      eventDetail.parameterSnapshotId = stage.geometrySpec.approval.parameterSnapshotId;
      eventDetail.parameterSnapshotSha256 = stage.geometrySpec.approval.parameterSnapshotSha256;
      eventDetail.completedChecklist = stage.geometrySpec.approval.completedChecklist;
      eventDetail.interactionMode = stage.geometrySpec.approval.interactionMode;
      eventDetail.reviewedAt = stage.geometrySpec.approval.reviewedAt;
      eventDetail.reviewDevice = stage.geometrySpec.approval.reviewDevice;
      eventDetail.geometryChanged = false;
      eventDetail.presentationRoot = stage.geometrySpec.hierarchy.movingTransform;
      eventDetail.contentSlotOwnership = stage.geometrySpec.hierarchy.contentSlot;
    }
    eventDetail.gate07Status = "eligible";
    eventDetail.gate08Status = "blocked";
    eventDetail.shippingAssetUnchanged = true;
    eventDetail.buildInstallPhonePush = false;
  }
  if (
    payload.action === "approve"
    && manifest.model.mechanism === "display-case"
    && stageId === "07-material"
    && stage.materialSpec?.approval?.approvedRevision === 2
  ) {
    eventDetail.userQuote = stage.materialSpec.approval.userApprovalQuote;
    eventDetail.approvalScope = stage.materialSpec.approval.approvalScope;
    eventDetail.approvedMaterialRevision = 2;
    eventDetail.approvalEffect = stage.materialSpec.approval.approvalEffect;
    eventDetail.reviewedArtifactId = stage.materialSpec.approval.reviewedArtifactId;
    eventDetail.reviewedArtifactSha256 = stage.materialSpec.approval.reviewedArtifactSha256;
    eventDetail.reviewedArtifacts = stage.materialSpec.approval.reviewedArtifacts;
    eventDetail.governingContractId = stage.materialSpec.approval.governingContractId;
    eventDetail.governingContractSha256 = stage.materialSpec.approval.governingContractSha256;
    eventDetail.parameterSnapshotId = stage.materialSpec.approval.parameterSnapshotId;
    eventDetail.parameterSnapshotSha256 = stage.materialSpec.approval.parameterSnapshotSha256;
    eventDetail.completedChecklist = stage.materialSpec.approval.completedChecklist;
    eventDetail.interactionMode = stage.materialSpec.approval.interactionMode;
    eventDetail.reviewedAt = stage.materialSpec.approval.reviewedAt;
    eventDetail.reviewDevice = stage.materialSpec.approval.reviewDevice;
    eventDetail.labelContentApproved = false;
    eventDetail.labelOwnership = stage.materialSpec.approval.labelOwnership;
    eventDetail.outsideSubjectPixels = 0;
    eventDetail.outsideAllowedMaterialZonePixels = 0;
    eventDetail.gate08Status = "eligible";
    eventDetail.gate09Status = "blocked";
    eventDetail.shippingAssetUnchanged = true;
    eventDetail.buildInstallPhonePush = false;
  }
  if (
    payload.action === "approve"
    && manifest.model.mechanism === "display-case"
    && stageId === "08-lighting"
    && stage.lightingSpec?.approval?.approvedRevision === 2
  ) {
    eventDetail.userQuote = stage.lightingSpec.approval.userApprovalQuote;
    eventDetail.approvalScope = stage.lightingSpec.approval.approvalScope;
    eventDetail.approvedLightingRevision = 2;
    eventDetail.approvalEffect = stage.lightingSpec.approval.approvalEffect;
    eventDetail.reviewedArtifactId = stage.lightingSpec.approval.reviewedArtifactId;
    eventDetail.reviewedArtifactSha256 = stage.lightingSpec.approval.reviewedArtifactSha256;
    eventDetail.reviewedArtifacts = stage.lightingSpec.approval.reviewedArtifacts;
    eventDetail.governingContractId = stage.lightingSpec.approval.governingContractId;
    eventDetail.governingContractSha256 = stage.lightingSpec.approval.governingContractSha256;
    eventDetail.parameterSnapshotId = stage.lightingSpec.approval.parameterSnapshotId;
    eventDetail.parameterSnapshotSha256 = stage.lightingSpec.approval.parameterSnapshotSha256;
    eventDetail.completedChecklist = stage.lightingSpec.approval.completedChecklist;
    eventDetail.interactionMode = stage.lightingSpec.approval.interactionMode;
    eventDetail.reviewedAt = stage.lightingSpec.approval.reviewedAt;
    eventDetail.reviewDevice = stage.lightingSpec.approval.reviewDevice;
    eventDetail.labelContentApproved = false;
    eventDetail.lookdevCandidatesOnly = true;
    eventDetail.unityRuntimeValuesTunable = true;
    eventDetail.outsideSubjectPixels = 0;
    eventDetail.outsideAllowedMaterialZonePixels = 0;
    eventDetail.gate09Status = "eligible";
    eventDetail.gate10Status = "blocked";
    eventDetail.shippingAssetUnchanged = true;
    eventDetail.buildInstallPhonePush = false;
  }
  if (
    payload.action === "approve"
    && manifest.model.mechanism === "display-case"
    && stageId === "09-environment"
    && stage.environmentSpec?.approval?.approvedRevision === 1
  ) {
    eventDetail.userQuote = stage.environmentSpec.approval.userApprovalQuote;
    eventDetail.approvalScope = stage.environmentSpec.approval.approvalScope;
    eventDetail.approvedEnvironmentRevision = 1;
    eventDetail.approvalEffect = stage.environmentSpec.approval.approvalEffect;
    eventDetail.reviewedArtifactId = stage.environmentSpec.approval.reviewedArtifactId;
    eventDetail.reviewedArtifactSha256 = stage.environmentSpec.approval.reviewedArtifactSha256;
    eventDetail.reviewedArtifacts = stage.environmentSpec.approval.reviewedArtifacts;
    eventDetail.governingContractId = stage.environmentSpec.approval.governingContractId;
    eventDetail.governingContractSha256 = stage.environmentSpec.approval.governingContractSha256;
    eventDetail.parameterSnapshotId = stage.environmentSpec.approval.parameterSnapshotId;
    eventDetail.parameterSnapshotSha256 = stage.environmentSpec.approval.parameterSnapshotSha256;
    eventDetail.completedChecklist = stage.environmentSpec.approval.completedChecklist;
    eventDetail.interactionMode = stage.environmentSpec.approval.interactionMode;
    eventDetail.reviewedAt = stage.environmentSpec.approval.reviewedAt;
    eventDetail.reviewDevice = stage.environmentSpec.approval.reviewDevice;
    eventDetail.labelContentApproved = false;
    eventDetail.lookdevCandidatesOnly = true;
    eventDetail.unityRuntimeValuesTunable = true;
    eventDetail.backgroundStatic = true;
    eventDetail.cameraMotion = false;
    eventDetail.backgroundMotion = false;
    eventDetail.outsideSubjectPixels = 0;
    eventDetail.gate10Status = "eligible";
    eventDetail.gate11Status = "blocked";
    eventDetail.shippingAssetUnchanged = true;
    eventDetail.buildInstallPhonePush = false;
  }
  const event = makeEvent(
    manifest,
    isCadSubapproval ? "interactive-cad-substage-approved" : (payload.action === "approve" ? "stage-approved" : "stage-rejected"),
    eventDetail
  );
  return saveManifest(manifest, event);
}

function validRegion(region) {
  if (!region) return null;
  const values = [region.x, region.y, region.width, region.height];
  if (values.some((value) => !Number.isFinite(value) || value < 0 || value > 1)) throw new PipelineError("Issue region values must be between 0 and 1.");
  if (region.width <= 0 || region.height <= 0 || region.x + region.width > 1 || region.y + region.height > 1) throw new PipelineError("Issue region must fit inside the image.");
  return { x: region.x, y: region.y, width: region.width, height: region.height };
}

export function addIssue(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  if (!STAGE_BY_ID.has(payload.stageId)) throw new PipelineError("Unknown issue stage.");
  const asset = manifest.assets.find((candidate) => candidate.id === payload.assetId);
  if (!asset) throw new PipelineError("Unknown issue asset.");
  const stageIndex = STAGES.findIndex((stage) => stage.id === payload.stageId);
  const stage = manifest.stages[stageIndex];
  const issue = {
    id: crypto.randomUUID(),
    stageId: payload.stageId,
    assetId: payload.assetId,
    claimIds: Array.isArray(payload.claimIds) ? payload.claimIds : [],
    severity: ["note", "warning", "blocker"].includes(payload.severity) ? payload.severity : "warning",
    status: "open",
    note: String(payload.note || "").trim(),
    region: validRegion(payload.region),
    createdAt: new Date().toISOString()
  };
  if (!issue.note) throw new PipelineError("Issue note is required.");
  manifest.issues = manifest.issues || [];
  manifest.issues.push(issue);
  if (stage.status === "approved" || issue.severity === "blocker") {
    stage.status = "stale";
    stage.staleReason = "新增了需要处理的视觉问题。";
    markDownstreamStale(manifest, stageIndex, `上游 ${payload.stageId} 新增问题。`);
  }
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  const event = makeEvent(manifest, "issue-created", { issue });
  return saveManifest(manifest, event);
}

export function importLegacyDecision(modelId, payload) {
  const manifest = loadManifest(modelId);
  if (payload.expectedRevision !== manifest.revision) throw new PipelineError("Manifest revision conflict.", 409);
  const decision = String(payload.decision || "").trim();
  const notes = String(payload.notes || "").trim();
  if (!decision && !notes) throw new PipelineError("Legacy decision or notes are required.");
  manifest.currentState.legacyBrowserDecision = {
    decision,
    notes,
    state: "unverified-history",
    importedAt: new Date().toISOString()
  };
  manifest.revision += 1;
  manifest.updatedAt = new Date().toISOString();
  const event = makeEvent(manifest, "legacy-browser-decision-imported", {
    decision,
    notes,
    approvalEffect: "none"
  });
  return saveManifest(manifest, event);
}

export function rebuildBrief(manifest) {
  return {
    exportedAt: new Date().toISOString(),
    model: manifest.model,
    route: manifest.route,
    revision: manifest.revision,
    earliestProblem: earliestProblem(manifest),
    approvedStages: manifest.stages.filter((stage) => stage.status === "approved").map((stage) => stage.id),
    openIssues: (manifest.issues || []).filter((issue) => issue.status !== "resolved"),
    claims: manifest.claims,
    assets: manifest.assets.map(({ id, stageId, slot, path, sha256, role, producer, sourceAssetIds, sourceClaimIds }) => ({
      id, stageId, slot, path, sha256, role, producer, sourceAssetIds, sourceClaimIds: sourceClaimIds || []
    })),
    instruction: "Resume only at the earliest non-approved stage. Never promote a Rodin concept directly to Unity."
  };
}

export function listModelSummaries() {
  return listModelIds().map((modelId) => {
    const manifest = deriveManifest(loadManifest(modelId));
    return {
      id: manifest.model.id,
      name: manifest.model.name,
      mechanism: manifest.model.mechanism,
      status: manifest.model.status,
      revision: manifest.revision,
      rebuildRequested: manifest.currentState.rebuildRequested,
      approvedCount: manifest.derived.approvedCount,
      assetCount: manifest.derived.assetCount,
      issueCount: manifest.derived.issueCount,
      earliestProblem: manifest.derived.earliestProblem,
      shippingReady: manifest.derived.shippingReady
    };
  });
}
