import fs from "node:fs";
import http from "node:http";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { ObsidianError, publicPreview, readObsidianNote } from "./obsidian-intake.mjs";
import {
  INTAKE_MAX_BYTES,
  MODEL_MECHANISMS,
  PipelineError,
  addIntakeFile,
  addIssue,
  approveStageFromDelegation,
  createModelPipeline,
  importObsidianNote,
  decideStage,
  deriveManifest,
  importLegacyDecision,
  listModelSummaries,
  loadManifest,
  loadModelingContract,
  readHistory,
  registerStageApprovalDelegation,
  rebuildBrief,
  refreshManifest,
  requestStageWork,
  repoRoot,
  resolveRepoPath,
  saveAnalysisResearchRevision,
  saveArchitectureEvidenceMappingReview,
  saveArchitecturePlan,
  saveArchitectureQuestionReview,
  saveBlockoutReview,
  saveBloodRedArtworkReview,
  saveBrighterCrystalReview,
  saveConcealedOverlapArchitectureReview,
  saveCorrectedBlockoutReview,
  saveExternalReferencePack,
  saveGenericStageEvidenceRevision,
  saveGeometryReview,
  saveMaterialHybridReview,
  saveMaterialReview,
  saveMeasurementPhoto,
  saveMeasurementSource,
  savePointAxisBlockoutReview,
  savePremiumDisplayCaseBlockoutReview,
  savePremiumDisplayCaseCorrectedBlockoutReview,
  savePremiumDisplayCaseExportReview,
  savePremiumDisplayCaseGeometryUserReview,
  savePremiumDisplayCaseMeasuredMotionSelection,
  savePremiumDisplayCaseMotionCorrection,
  savePremiumDisplayCaseRigidMotionContract,
  savePremiumDisplayCaseSlowerWholeCaseMotionReview,
  savePremiumDisplayCaseShippingReview,
  savePremiumDisplayCaseUnityParityReview,
  savePremiumDisplayCaseWholeCaseMotionReview,
  saveStageReviewEvidence,
  saveModelingContract,
  toolDir,
  updateModelMechanism
} from "./pipeline-core.mjs";
import { STAGES } from "./pipeline-contract.mjs";
import { agentLoginState, checkAgentAuth, startAgentLogin, startStageRun, stageWorkStatus, stopStageRun } from "./agent-runner.mjs";
import { deriveMaterialLibrary, loadMaterialLibrary, validateMaterialLibrary } from "./material-library-core.mjs";

const serverFile = fileURLToPath(import.meta.url);
const port = Number.parseInt(process.env.FIDGET_MODEL_PIPELINE_PORT || "8891", 10);
const host = "127.0.0.1";
const mimeTypes = {
  ".html": "text/html; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".mjs": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".webp": "image/webp",
  ".svg": "image/svg+xml",
  ".mov": "video/quicktime",
  ".mp4": "video/mp4",
  ".m4v": "video/x-m4v",
  ".webm": "video/webm",
  ".wav": "audio/wav",
  ".mp3": "audio/mpeg",
  ".glb": "model/gltf-binary",
  ".gltf": "model/gltf+json",
  ".fbx": "application/octet-stream",
  ".blend": "application/octet-stream"
};

function sendJson(response, statusCode, payload) {
  const body = JSON.stringify(payload, null, 2);
  response.writeHead(statusCode, { "content-type": "application/json; charset=utf-8", "cache-control": "no-store" });
  response.end(body);
}

function sendFile(request, response, absolutePath) {
  if (!fs.existsSync(absolutePath) || !fs.statSync(absolutePath).isFile()) {
    sendJson(response, 404, { error: "Not found" });
    return;
  }
  const size = fs.statSync(absolutePath).size;
  const contentType = mimeTypes[path.extname(absolutePath).toLowerCase()] || "application/octet-stream";
  const range = request.headers.range;
  if (range) {
    const match = range.match(/^bytes=(\d*)-(\d*)$/);
    if (!match) {
      response.writeHead(416, { "content-range": `bytes */${size}` });
      response.end();
      return;
    }
    const start = match[1] ? Number.parseInt(match[1], 10) : 0;
    const end = match[2] ? Number.parseInt(match[2], 10) : size - 1;
    if (!Number.isSafeInteger(start) || !Number.isSafeInteger(end) || start < 0 || end < start || start >= size) {
      response.writeHead(416, { "content-range": `bytes */${size}` });
      response.end();
      return;
    }
    const boundedEnd = Math.min(end, size - 1);
    response.writeHead(206, {
      "content-type": contentType,
      "content-length": boundedEnd - start + 1,
      "content-range": `bytes ${start}-${boundedEnd}/${size}`,
      "accept-ranges": "bytes",
      "cache-control": "no-cache"
    });
    fs.createReadStream(absolutePath, { start, end: boundedEnd }).pipe(response);
    return;
  }
  response.writeHead(200, {
    "content-type": contentType,
    "content-length": size,
    "accept-ranges": "bytes",
    "cache-control": "no-cache"
  });
  fs.createReadStream(absolutePath).pipe(response);
}

function readBytes(request, limit) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let total = 0;
    request.on("data", (chunk) => {
      total += chunk.length;
      if (total > limit) { reject(new PipelineError("Request body is too large.", 413)); request.destroy(); return; }
      chunks.push(chunk);
    });
    request.on("end", () => resolve(Buffer.concat(chunks)));
    request.on("error", reject);
  });
}

function readJson(request) {
  return new Promise((resolve, reject) => {
    let body = "";
    request.setEncoding("utf8");
    request.on("data", (chunk) => {
      body += chunk;
      if (body.length > 16 * 1024 * 1024) reject(new PipelineError("Request body is too large.", 413));
    });
    request.on("end", () => {
      if (!body) return resolve({});
      try { resolve(JSON.parse(body)); }
      catch { reject(new PipelineError("Request body must be valid JSON.")); }
    });
    request.on("error", reject);
  });
}

function safeToolFile(urlPath) {
  const prefix = "/tools/model-provenance-explorer/";
  const stripped = urlPath.startsWith(prefix) ? urlPath.slice(prefix.length) : urlPath.slice(1);
  const relative = !stripped ? "index.html" : decodeURIComponent(stripped);
  const absolute = path.resolve(toolDir, relative);
  if (absolute !== toolDir && !absolute.startsWith(`${toolDir}${path.sep}`)) throw new PipelineError("Invalid tool path.", 403);
  return absolute;
}

async function handleApi(request, response, pathname) {
  if (request.method === "GET" && pathname === "/api/stages") return sendJson(response, 200, { stages: STAGES });
  if (request.method === "GET" && pathname === "/api/models") return sendJson(response, 200, { models: listModelSummaries(), mechanisms: MODEL_MECHANISMS });
  if (request.method === "POST" && pathname === "/api/models") {
    const payload = await readJson(request);
    return sendJson(response, 201, createModelPipeline(payload));
  }

  if (request.method === "GET" && pathname === "/api/obsidian/preview") {
    const link = new URL(request.url, "http://localhost").searchParams.get("link");
    return sendJson(response, 200, { note: publicPreview(readObsidianNote(link)) });
  }
  const obsidianImportMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/intake-from-obsidian$/);
  if (request.method === "POST" && obsidianImportMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, importObsidianNote(obsidianImportMatch[1], payload.link));
  }

  const intakeFileMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/intake-file$/);
  if (request.method === "POST" && intakeFileMatch) {
    const bytes = await readBytes(request, INTAKE_MAX_BYTES);
    const filename = decodeURIComponent(String(request.headers["x-filename"] || "reference"));
    const note = decodeURIComponent(String(request.headers["x-note"] || ""));
    return sendJson(response, 200, addIntakeFile(intakeFileMatch[1], { filename, bytes, note }));
  }
  if (request.method === "GET" && pathname === "/api/material-library") {
    const library = loadMaterialLibrary();
    return sendJson(response, 200, { library: deriveMaterialLibrary(library), errors: validateMaterialLibrary(library) });
  }

  const modelMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)$/);
  if (request.method === "GET" && modelMatch) return sendJson(response, 200, deriveManifest(loadManifest(modelMatch[1])));

  const mechanismMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/mechanism$/);
  if (request.method === "PATCH" && mechanismMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, updateModelMechanism(mechanismMatch[1], payload));
  }

  const approvalDelegationMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/approval-delegation$/);
  if (request.method === "POST" && approvalDelegationMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, registerStageApprovalDelegation(approvalDelegationMatch[1], payload));
  }

  const historyMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/history$/);
  if (request.method === "GET" && historyMatch) return sendJson(response, 200, { events: readHistory(historyMatch[1]) });

  const contractMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/contract$/);
  if (request.method === "GET" && contractMatch) {
    // A manifest can point at a contract file that was deleted from disk; the workbench must still open.
    try { return sendJson(response, 200, { contract: loadModelingContract(contractMatch[1]) }); }
    catch (error) {
      if (error instanceof PipelineError && /contract file is missing/.test(error.message)) return sendJson(response, 200, { contract: null, warning: error.message });
      throw error;
    }
  }
  const workRequestMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/stages\/([a-z0-9-]+)\/work-request$/);
  if (request.method === "GET" && workRequestMatch) return sendJson(response, 200, stageWorkStatus(workRequestMatch[1], workRequestMatch[2]));
  if (request.method === "POST" && workRequestMatch) {
    const payload = await readJson(request);
    // "request" launches a headless Cursor agent for the gate; "withdraw" stops it and clears the request.
    if (payload.action === "withdraw") return sendJson(response, 200, stopStageRun(workRequestMatch[1], workRequestMatch[2], payload));
    if (payload.action === "record-only") return sendJson(response, 200, { manifest: requestStageWork(workRequestMatch[1], workRequestMatch[2], payload), run: null });
    return sendJson(response, 200, startStageRun(workRequestMatch[1], workRequestMatch[2], payload));
  }
  if (request.method === "GET" && pathname === "/api/agent/auth") return sendJson(response, 200, { ...(await checkAgentAuth()), login: agentLoginState() });
  if (request.method === "POST" && pathname === "/api/agent/login") return sendJson(response, 200, await startAgentLogin());
  if (request.method === "POST" && contractMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveModelingContract(contractMatch[1], payload));
  }

  const measurementPhotoMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/measurement-photo$/);
  if (request.method === "POST" && measurementPhotoMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveMeasurementPhoto(measurementPhotoMatch[1], payload));
  }

  const measurementSourceMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/measurement-source$/);
  if (request.method === "POST" && measurementSourceMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveMeasurementSource(measurementSourceMatch[1], payload));
  }

  const architectureMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/architecture$/);
  if (request.method === "POST" && architectureMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveArchitecturePlan(architectureMatch[1], payload));
  }

  const genericEvidenceMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/stages\/([a-z0-9-]+)\/evidence-revision$/);
  if (request.method === "POST" && genericEvidenceMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveGenericStageEvidenceRevision(genericEvidenceMatch[1], genericEvidenceMatch[2], payload));
  }

  const reviewEvidenceMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/stages\/([a-z0-9-]+)\/review-evidence$/);
  if (request.method === "POST" && reviewEvidenceMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveStageReviewEvidence(reviewEvidenceMatch[1], reviewEvidenceMatch[2], payload));
  }

  const delegatedApprovalMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/stages\/([a-z0-9-]+)\/delegated-approval$/);
  if (request.method === "POST" && delegatedApprovalMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, approveStageFromDelegation(delegatedApprovalMatch[1], delegatedApprovalMatch[2], payload));
  }

  const architectureQuestionsMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/architecture-questions$/);
  if (request.method === "POST" && architectureQuestionsMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveArchitectureQuestionReview(architectureQuestionsMatch[1], payload));
  }

  const architectureEvidenceMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/architecture-evidence-map$/);
  if (request.method === "POST" && architectureEvidenceMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveArchitectureEvidenceMappingReview(architectureEvidenceMatch[1], payload));
  }

  const wholeCaseMotionMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/whole-case-motion-evidence$/);
  if (request.method === "POST" && wholeCaseMotionMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, savePremiumDisplayCaseWholeCaseMotionReview(wholeCaseMotionMatch[1], payload));
  }

  const slowerWholeCaseMotionMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/whole-case-motion-speed-evidence$/);
  if (request.method === "POST" && slowerWholeCaseMotionMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, savePremiumDisplayCaseSlowerWholeCaseMotionReview(slowerWholeCaseMotionMatch[1], payload));
  }

  const premiumDisplayCaseMotionCorrectionMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/premium-display-case-motion-correction$/);
  if (request.method === "POST" && premiumDisplayCaseMotionCorrectionMatch) {
    const payload = await readJson(request);
    return sendJson(
      response,
      200,
      savePremiumDisplayCaseMotionCorrection(
        premiumDisplayCaseMotionCorrectionMatch[1],
        payload
      )
    );
  }

  const measuredMotionSelectionMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/premium-display-case-measured-motion-selection$/);
  if (request.method === "POST" && measuredMotionSelectionMatch) {
    const payload = await readJson(request);
    return sendJson(
      response,
      200,
      savePremiumDisplayCaseMeasuredMotionSelection(
        measuredMotionSelectionMatch[1],
        payload
      )
    );
  }

  const rigidMotionContractMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/premium-display-case-rigid-motion-contract$/);
  if (request.method === "POST" && rigidMotionContractMatch) {
    const payload = await readJson(request);
    return sendJson(
      response,
      200,
      savePremiumDisplayCaseRigidMotionContract(
        rigidMotionContractMatch[1],
        payload
      )
    );
  }

  const concealedOverlapMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/concealed-overlap-architecture$/);
  if (request.method === "POST" && concealedOverlapMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveConcealedOverlapArchitectureReview(concealedOverlapMatch[1], payload));
  }

  const blockoutMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/blockout-review$/);
  if (request.method === "POST" && blockoutMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveBlockoutReview(blockoutMatch[1], payload));
  }

  const premiumDisplayCaseBlockoutMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/premium-display-case-blockout-review$/);
  if (request.method === "POST" && premiumDisplayCaseBlockoutMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, savePremiumDisplayCaseBlockoutReview(premiumDisplayCaseBlockoutMatch[1], payload));
  }

  const premiumDisplayCaseCorrectedBlockoutMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/premium-display-case-corrected-blockout-review$/);
  if (request.method === "POST" && premiumDisplayCaseCorrectedBlockoutMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, savePremiumDisplayCaseCorrectedBlockoutReview(premiumDisplayCaseCorrectedBlockoutMatch[1], payload));
  }

  const correctedBlockoutMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/corrected-blockout-review$/);
  if (request.method === "POST" && correctedBlockoutMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveCorrectedBlockoutReview(correctedBlockoutMatch[1], payload));
  }

  const pointAxisBlockoutMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/point-axis-blockout-review$/);
  if (request.method === "POST" && pointAxisBlockoutMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, savePointAxisBlockoutReview(pointAxisBlockoutMatch[1], payload));
  }

  const geometryReviewMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/geometry-review$/);
  if (request.method === "POST" && geometryReviewMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveGeometryReview(geometryReviewMatch[1], payload));
  }

  const premiumDisplayCaseGeometryUserReviewMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/premium-display-case-geometry-user-review$/);
  if (request.method === "POST" && premiumDisplayCaseGeometryUserReviewMatch) {
    const payload = await readJson(request);
    return sendJson(
      response,
      200,
      savePremiumDisplayCaseGeometryUserReview(
        premiumDisplayCaseGeometryUserReviewMatch[1],
        payload
      )
    );
  }

  const premiumDisplayCaseExportReviewMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/premium-display-case-export-review$/);
  if (request.method === "POST" && premiumDisplayCaseExportReviewMatch) {
    const payload = await readJson(request);
    return sendJson(
      response,
      200,
      savePremiumDisplayCaseExportReview(
        premiumDisplayCaseExportReviewMatch[1],
        payload
      )
    );
  }

  const premiumDisplayCaseUnityParityMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/premium-display-case-unity-parity-review$/);
  if (request.method === "POST" && premiumDisplayCaseUnityParityMatch) {
    const payload = await readJson(request);
    return sendJson(
      response,
      200,
      savePremiumDisplayCaseUnityParityReview(
        premiumDisplayCaseUnityParityMatch[1],
        payload
      )
    );
  }

  const premiumDisplayCaseShippingMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/premium-display-case-shipping-review$/);
  if (request.method === "POST" && premiumDisplayCaseShippingMatch) {
    const payload = await readJson(request);
    return sendJson(
      response,
      200,
      savePremiumDisplayCaseShippingReview(
        premiumDisplayCaseShippingMatch[1],
        payload
      )
    );
  }

  const materialReviewMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/material-review$/);
  if (request.method === "POST" && materialReviewMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveMaterialReview(materialReviewMatch[1], payload));
  }

  const materialHybridReviewMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/material-hybrid-review$/);
  if (request.method === "POST" && materialHybridReviewMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveMaterialHybridReview(materialHybridReviewMatch[1], payload));
  }

  const brighterCrystalReviewMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/brighter-crystal-review$/);
  if (request.method === "POST" && brighterCrystalReviewMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveBrighterCrystalReview(brighterCrystalReviewMatch[1], payload));
  }

  const bloodRedArtworkReviewMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/blood-red-artwork-review$/);
  if (request.method === "POST" && bloodRedArtworkReviewMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveBloodRedArtworkReview(bloodRedArtworkReviewMatch[1], payload));
  }

  const referenceMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/references$/);
  if (request.method === "POST" && referenceMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveExternalReferencePack(referenceMatch[1], payload));
  }

  const analysisMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/analysis$/);
  if (request.method === "POST" && analysisMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, saveAnalysisResearchRevision(analysisMatch[1], payload));
  }

  const refreshMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/refresh$/);
  if (request.method === "POST" && refreshMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, refreshManifest(refreshMatch[1], payload.expectedRevision ?? null));
  }

  const decisionMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/stages\/([a-z0-9-]+)\/decision$/);
  if (request.method === "POST" && decisionMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, decideStage(decisionMatch[1], decisionMatch[2], payload));
  }

  const issueMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/issues$/);
  if (request.method === "POST" && issueMatch) {
    const payload = await readJson(request);
    return sendJson(response, 201, addIssue(issueMatch[1], payload));
  }

  const legacyMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/legacy-decision$/);
  if (request.method === "POST" && legacyMatch) {
    const payload = await readJson(request);
    return sendJson(response, 200, importLegacyDecision(legacyMatch[1], payload));
  }

  const briefMatch = pathname.match(/^\/api\/models\/([a-z0-9-]+)\/brief$/);
  if (request.method === "GET" && briefMatch) return sendJson(response, 200, rebuildBrief(loadManifest(briefMatch[1])));
  return sendJson(response, 404, { error: "Unknown API route" });
}

export function createServer() {
  return http.createServer(async (request, response) => {
    try {
      const url = new URL(request.url, `http://${request.headers.host || `${host}:${port}`}`);
      const pathname = url.pathname;
      if (pathname.startsWith("/api/")) return await handleApi(request, response, pathname);
      if (pathname.startsWith("/repo/")) return sendFile(request, response, resolveRepoPath(decodeURIComponent(pathname.slice(6))));
      if (pathname.startsWith("/vendor/three-build/")) {
        const buildRoot = path.join(toolDir, "node_modules/three/build");
        const absolute = path.resolve(buildRoot, decodeURIComponent(pathname.slice("/vendor/three-build/".length)));
        if (absolute !== buildRoot && !absolute.startsWith(`${buildRoot}${path.sep}`)) throw new PipelineError("Invalid vendor path.", 403);
        return sendFile(request, response, absolute);
      }
      if (pathname.startsWith("/vendor/three-examples/")) {
        const examplesRoot = path.join(toolDir, "node_modules/three/examples/jsm");
        const absolute = path.resolve(examplesRoot, decodeURIComponent(pathname.slice("/vendor/three-examples/".length)));
        if (absolute !== examplesRoot && !absolute.startsWith(`${examplesRoot}${path.sep}`)) throw new PipelineError("Invalid vendor path.", 403);
        return sendFile(request, response, absolute);
      }
      return sendFile(request, response, safeToolFile(pathname));
    } catch (error) {
      const statusCode = error instanceof PipelineError || error instanceof ObsidianError ? error.statusCode : 500;
      return sendJson(response, statusCode, { error: error.message, details: error.details || [] });
    }
  });
}

if (process.argv[1] && path.resolve(process.argv[1]) === path.resolve(serverFile)) {
  createServer().listen(port, host, () => {
    console.log(`Fidgeting model pipeline: http://${host}:${port}/tools/model-provenance-explorer/`);
  });
}
