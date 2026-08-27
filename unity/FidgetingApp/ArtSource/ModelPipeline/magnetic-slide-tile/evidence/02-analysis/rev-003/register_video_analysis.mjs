#!/usr/bin/env node
import crypto from "node:crypto";
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import {
  loadManifest,
  saveManifest,
  sha256File,
} from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const modelId = "magnetic-slide-tile";
const manifest = loadManifest(modelId);
if (manifest.revision !== 110) {
  throw new Error(`Expected manifest revision 110, got ${manifest.revision}.`);
}

const here = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(here, "../../../../../../../..");
const toRepoPath = (absolute) => path.relative(repoRoot, absolute).split(path.sep).join("/");
const resolveRepoPath = (repoPath) => path.join(repoRoot, repoPath);
const digestValues = (values) => crypto.createHash("sha256").update(
  values.filter(Boolean).sort().join("\n")).digest("hex");
const stableJson = (value) => {
  if (Array.isArray(value)) return `[${value.map(stableJson).join(",")}]`;
  if (value && typeof value === "object") {
    return `{${Object.keys(value).sort().map(
      (key) => `${JSON.stringify(key)}:${stableJson(value[key])}`).join(",")}}`;
  }
  return JSON.stringify(value);
};

const intakeDir = path.resolve(here, "../../01-intake/rev-003");
const sourceMetadataPath = path.join(intakeDir, "source-metadata.json");
const sourceMetadata = JSON.parse(fs.readFileSync(sourceMetadataPath, "utf8"));
const expectedSources = new Map(sourceMetadata.files.map((item) => [item.id, item]));
const exactUserStatement =
  "三段视频拍摄的是与目标完全相同的产品，仅花纹和纹路不同。视频用于逐帧确认轴心、滑轨、单向推动、最大行程、任意角度旋转和棘轮玩法。";
if (sourceMetadata.userStatement.summary !== exactUserStatement) {
  throw new Error("The immutable intake statement does not match the expected user statement.");
}
for (const source of sourceMetadata.files) {
  const absolute = resolveRepoPath(source.path);
  if (!fs.existsSync(absolute)) throw new Error(`Missing source video: ${source.path}`);
  if (sha256File(absolute) !== source.sha256) throw new Error(`Source hash changed: ${source.id}`);
}

const assetIds = new Set(manifest.assets.map((asset) => asset.id));
const makeAsset = ({
  id,
  stageId,
  slot,
  absolute,
  role,
  sourceAssetIds = [],
  contentClass,
  note,
  recipe,
  provenanceOrigin = "repository-generated",
  assertedBy = "assistant",
  extra = {},
}) => {
  if (assetIds.has(id)) throw new Error(`Asset already exists: ${id}`);
  if (!fs.existsSync(absolute)) throw new Error(`Missing asset: ${absolute}`);
  assetIds.add(id);
  return {
    id,
    stageId,
    slot,
    path: toRepoPath(absolute),
    sha256: sha256File(absolute),
    exists: true,
    sizeBytes: fs.statSync(absolute).size,
    role,
    producer: {
      name: stageId === "01-intake" ? "user input preservation" : "fidgeting-model-pipeline",
      version: "1",
      recipe,
    },
    provenance: {
      origin: provenanceOrigin,
      contentClass,
      assertedBy,
      note,
    },
    sourceAssetIds,
    ...extra,
  };
};

const sourceVideoAssets = sourceMetadata.files.map((source) => makeAsset({
  id: source.id,
  stageId: "01-intake",
  slot: "original-reference",
  absolute: resolveRepoPath(source.path),
  role: "user-input",
  contentClass: "authoritative-same-model-mechanism-video",
  note: "用户确认与目标机构完全相同，仅颜色、花纹和纹路不同；原 MOV 保持不变。",
  recipe: "Immutable original user MOV; no transcode or rewrite",
  provenanceOrigin: "user-provided",
  assertedBy: "user",
  extra: {
    media: {
      frameCount: source.id.endsWith("6022") ? 426 : source.id.endsWith("6023") ? 480 : 821,
      durationSeconds: source.durationSeconds,
      videoCodec: source.video.codec,
      storedWidth: source.video.width,
      storedHeight: source.video.height,
      nominalFps: source.video.nominalFps,
      displayRotationDeg: -90,
      audioCodec: source.audio.codec,
      sampleRateHz: source.audio.sampleRateHz,
      channels: source.audio.channels,
    },
  },
}));
const sourceVideoIds = sourceVideoAssets.map((asset) => asset.id);
const intakeMetadataAsset = makeAsset({
  id: "slider-intake-user-mechanism-source-metadata-r003",
  stageId: "01-intake",
  slot: "original-reference",
  absolute: sourceMetadataPath,
  role: "user-input",
  contentClass: "authoritative-same-model-video-metadata",
  note: `用户原文分类：${exactUserStatement}`,
  recipe: "User video metadata, immutable hashes and classification boundary",
  provenanceOrigin: "user-provided",
  assertedBy: "user",
  sourceAssetIds: sourceVideoIds,
});
manifest.assets.push(...sourceVideoAssets, intakeMetadataAsset);

const generatedAssetIds = [];
const addGenerated = (definition) => {
  const asset = makeAsset(definition);
  manifest.assets.push(asset);
  generatedAssetIds.push(asset.id);
  return asset;
};
const originalSources = sourceVideoIds;
const file = (name) => path.join(here, name);
addGenerated({
  id: "slider-analysis-video-survey-generator-r003",
  stageId: "02-analysis", slot: "analysis-evidence", absolute: file("generate_frame_surveys.py"),
  role: "process", sourceAssetIds: originalSources,
  contentClass: "frame-pts-audio-proxy-generator",
  note: "生成逐帧 PTS 清单、全片调查板、音频瞬态图和 H.264 审查代理；原 MOV 不变。",
  recipe: "Python + ffprobe + ffmpeg + PIL + NumPy deterministic evidence generation",
});
addGenerated({
  id: "slider-analysis-mechanism-board-builder-r003",
  stageId: "02-analysis", slot: "analysis-evidence", absolute: file("build_mechanism_analysis.py"),
  role: "process", sourceAssetIds: originalSources,
  contentClass: "mechanism-review-board-generator",
  note: "从零基解码帧索引和 ffprobe PTS 生成中文机构评审板。",
  recipe: "Python + ffmpeg exact select + PIL annotations",
});
addGenerated({
  id: "slider-analysis-frame-survey-report-r003",
  stageId: "02-analysis", slot: "analysis-evidence", absolute: file("frame-survey-report.json"),
  role: "analysis", sourceAssetIds: originalSources,
  contentClass: "frame-survey-report",
  note: "汇总三段视频帧清单、调查板、音频图和可播放代理。",
  recipe: "Generated by generate_frame_surveys.py",
});
const mechanismAnalysisAsset = addGenerated({
  id: "slider-analysis-mechanism-findings-r003",
  stageId: "02-analysis", slot: "discovery-log", absolute: file("mechanism-analysis.json"),
  role: "analysis", sourceAssetIds: originalSources,
  contentClass: "source-linked-frame-accurate-mechanism-analysis",
  note: "区分直接观察、推断、可信度与隐藏结构 unknown；不以视频比例静默生成毫米尺寸。",
  recipe: "Synthesis of completed frame-by-frame analyses",
});

for (const stem of ["IMG_6022", "IMG_6023", "IMG_6024"]) {
  const sourceId = `slider-intake-user-mechanism-video-${stem.slice(-4)}`;
  for (const extension of ["json", "csv"]) {
    addGenerated({
      id: `slider-analysis-${stem.toLowerCase().replace("_", "-")}-frame-manifest-${extension}-r003`,
      stageId: "02-analysis", slot: "analysis-evidence",
      absolute: file(`frame-manifests/${stem}-frames.${extension}`),
      role: "analysis", sourceAssetIds: [sourceId],
      contentClass: `per-video-frame-pts-index-manifest-${extension}`,
      note: "每行使用零基解码帧索引和 ffprobe best_effort_timestamp_time；不按名义帧率反推时间。",
      recipe: "ffprobe -show_frames frame index and PTS manifest",
    });
  }
  addGenerated({
    id: `slider-analysis-${stem.toLowerCase().replace("_", "-")}-survey-board-r003`,
    stageId: "02-analysis", slot: "analysis-evidence", absolute: file(`${stem}-frame-survey.png`),
    role: "analysis", sourceAssetIds: [sourceId],
    contentClass: "full-video-frame-index-survey-board",
    note: "全片均匀抽样并额外包含末帧，标签使用帧清单 PTS。",
    recipe: "Frame-index survey board generated from exact selected frames",
  });
  for (const extension of ["csv", "png"]) {
    addGenerated({
      id: `slider-analysis-${stem.toLowerCase().replace("_", "-")}-audio-impulses-${extension}-r003`,
      stageId: "02-analysis", slot: "analysis-evidence",
      absolute: file(`${stem}-audio-impulses.${extension}`),
      role: "analysis", sourceAssetIds: [sourceId],
      contentClass: `audio-mechanical-impulse-${extension === "png" ? "plot" : "candidate-manifest"}`,
      note: "5 ms RMS 自动峰仅作定位；一个候选峰不自动等于一个 detent。",
      recipe: "48 kHz mono 5 ms RMS envelope and local-peak candidates",
    });
  }
  addGenerated({
    id: `slider-analysis-${stem.toLowerCase().replace("_", "-")}-playback-proxy-r003`,
    stageId: "02-analysis", slot: "analysis-evidence",
    absolute: file(`playback-proxies/${stem}-review-h264.mp4`),
    role: "analysis", sourceAssetIds: [sourceId],
    contentClass: "browser-review-playback-proxy",
    note: "720×1280 H.264/AAC 代理仅用于浏览器播放；机构证据仍回链原始 HEVC MOV。",
    recipe: "ffmpeg autorotate + Lanczos 720-wide + H.264 CRF 23 + AAC 128 kbps + faststart",
  });
}

const keyFrameManifest = JSON.parse(fs.readFileSync(file("key-frame-manifest.json"), "utf8"));
const keyFrameAssetIds = new Map();
for (const record of keyFrameManifest.frames) {
  const stemId = record.video.toLowerCase().replace("_", "-");
  const id = `slider-analysis-${stemId}-key-f${String(record.frameIndex).padStart(4, "0")}-r003`;
  addGenerated({
    id,
    stageId: "02-analysis", slot: "analysis-evidence",
    absolute: resolveRepoPath(record.path),
    role: "analysis", sourceAssetIds: [record.videoAssetId],
    contentClass: "source-linked-key-frame-crop",
    note: `零基帧 f${record.frameIndex}，PTS ${record.ptsSeconds.toFixed(6)} s；裁切只用于看清玩具，完整视频可打开。`,
    recipe: `ffmpeg select eq(n,${record.frameIndex}), autorotate, 720x1280 Lanczos, fixed review crop`,
    extra: {
      frame: {
        index: record.frameIndex,
        ptsSeconds: record.ptsSeconds,
        indexBase: 0,
        timestampAuthority: "ffprobe-best-effort-pts",
      },
    },
  });
  keyFrameAssetIds.set(`${record.video}:${record.frameIndex}`, id);
}
addGenerated({
  id: "slider-analysis-key-frame-manifest-r003",
  stageId: "02-analysis", slot: "analysis-evidence", absolute: file("key-frame-manifest.json"),
  role: "analysis", sourceAssetIds: originalSources,
  contentClass: "source-linked-key-frame-manifest",
  note: "记录每张永久关键帧裁切的源视频、零基帧索引、PTS、路径与 SHA-256。",
  recipe: "Generated by build_mechanism_analysis.py",
});

const reviewBoardDefinitions = [
  ["slider-analysis-video-timeline-r003", "three-video-timeline-board.png", "three-video-frame-accurate-timeline", originalSources],
  ["slider-analysis-plate-identity-r003", "plate-identity-board.png", "mechanism-carrier-and-moving-cover-identity-board", originalSources],
  ["slider-analysis-one-way-slide-r003", "one-way-slide-sequence-board.png", "one-outward-direction-slide-sequence", [sourceVideoIds[0]]],
  ["slider-analysis-rotation-audio-r003", "rotation-and-audio-board.png", "detented-rotation-and-audio-cadence-board", [sourceVideoIds[1]]],
  ["slider-analysis-axis-slot-hypothesis-r003", "axis-slot-hypothesis-board.png", "observed-versus-hidden-axis-slot-hypothesis", [sourceVideoIds[2]]],
  ["slider-analysis-contradiction-r003", "contradiction-board.png", "motion-and-face-interpretation-contradiction-board", originalSources],
];
for (const [id, filename, contentClass, sourceAssetIds] of reviewBoardDefinitions) {
  addGenerated({
    id,
    stageId: "02-analysis", slot: "analysis-board", absolute: file(filename),
    role: "analysis", sourceAssetIds,
    contentClass,
    note: "中文用户评审板；帧标签为零基解码帧索引和 ffprobe PTS，技术判断分为观察、假设和 unknown。",
    recipe: "Full-resolution annotated source crops generated by build_mechanism_analysis.py",
  });
}
addGenerated({
  id: "slider-analysis-audio-contact-sheet-r003",
  stageId: "02-analysis", slot: "analysis-evidence", absolute: file("audio-impulse-contact-sheet.png"),
  role: "analysis", sourceAssetIds: originalSources,
  contentClass: "three-video-audio-impulse-contact-sheet",
  note: "音频峰用于帧定位和节奏复核，不映射到未见的内部零件。",
  recipe: "Three source-linked RMS impulse plots",
});
addGenerated({
  id: "slider-analysis-validation-report-r003",
  stageId: "02-analysis", slot: "analysis-evidence", absolute: file("validation-report.json"),
  role: "validation", sourceAssetIds: [
    "slider-analysis-video-survey-generator-r003",
    "slider-analysis-mechanism-board-builder-r003",
    mechanismAnalysisAsset.id,
    ...originalSources,
  ],
  contentClass: "frame-source-and-review-validation-report",
  note: "验证原 MOV 哈希、帧数、PTS 单调、评审资产存在和无临时路径引用。",
  recipe: "Generated by build_mechanism_analysis.py",
});
const registerAsset = makeAsset({
  id: "slider-analysis-video-registrar-r003",
  stageId: "02-analysis", slot: "analysis-evidence", absolute: file("register_video_analysis.mjs"),
  role: "process", sourceAssetIds: [mechanismAnalysisAsset.id, ...originalSources],
  contentClass: "pipeline-registration-script",
  note: "将原视频、逐帧证据、声明和上游失效状态写入权威 manifest/history。",
  recipe: "Deterministic manifest registration with revision and hash guards",
});
manifest.assets.push(registerAsset);
generatedAssetIds.push(registerAsset.id);

const oldClaims = manifest.claims.filter((claim) => claim.stageId === "02-analysis");
for (const claim of oldClaims) {
  claim.state = "superseded";
  claim.supersededBy = "video-analysis-rev-003";
  claim.supersededAt = new Date().toISOString();
}
for (const claim of manifest.claims.filter((claim) => {
  const number = Number.parseInt(claim.stageId.slice(0, 2), 10);
  return number >= 3 && number <= 11 && claim.state !== "superseded";
})) {
  claim.state = "stale";
  claim.staleReason = "New user mechanism videos reopened Gate 02 analysis.";
}

const region = (video, frameIndex, rect = [0.03, 0.18, 0.94, 0.68]) => ({
  assetId: `slider-intake-user-mechanism-video-${video.slice(-4)}`,
  frameIndex,
  ptsSeconds: keyFrameManifest.frames.find(
    (item) => item.video === video && item.frameIndex === frameIndex)?.ptsSeconds,
  normalizedRect: rect,
});
const claimDefs = [
  {
    id: "slider-analysis-compound-axis-track-r003", category: "mechanism",
    statement: "两片由复合轴心/纵向轨迹关系约束；画面直接证明直线滑动和多处滑位旋转，但不证明隐藏截面。",
    confidence: "high", videos: ["IMG_6022", "IMG_6024"], regions: [region("IMG_6022", 125), region("IMG_6024", 199)],
  },
  {
    id: "slider-analysis-carrier-cover-roles-r003", category: "structure",
    statement: "机构承载片 M 被手支撑并更可能承担固定点；活动盖片 C 由拇指驱动。隐藏连接几何仍未直接可见。",
    confidence: "medium", videos: ["IMG_6022", "IMG_6024"], regions: [region("IMG_6022", 100), region("IMG_6024", 199)],
  },
  {
    id: "slider-analysis-centerline-path-r003", category: "mechanism",
    statement: "C 携带或跟随中线纵向槽/接触路径；48 帧拟合支持 M 固定点 (u,v)≈(0.36±0.08,0.45±0.10)，C 接触沿 u≈0.30–0.76 移动。槽壁、轴销归属与耦合 unknown。",
    confidence: "medium", videos: ["IMG_6024"], regions: [region("IMG_6024", 183), region("IMG_6024", 207)],
  },
  {
    id: "slider-analysis-one-outward-direction-r003", category: "motion",
    statement: "从闭合止点只能朝一个外向方向打开，并沿同一路径返回；“单向”不表示无法关闭。",
    confidence: "high", videos: ["IMG_6022"], regions: [region("IMG_6022", 0), region("IMG_6022", 75), region("IMG_6022", 225)],
  },
  {
    id: "slider-analysis-normalized-travel-r003", category: "scale",
    statement: "视频支持最大行程约 0.38–0.46L，峰值约 0.50L；21 mm 只与该范围相容，不是视频新测得的毫米值。",
    confidence: "medium", videos: ["IMG_6022", "IMG_6024"], regions: [region("IMG_6022", 125), region("IMG_6024", 199)],
  },
  {
    id: "slider-analysis-twelve-degree-detents-r003", category: "motion",
    statement: "逐帧旋转与音频联合支持 12° 每档、360° 共 30 档；视频直接显示可逆 0↔180° 和约 170°，完整 360° 仍属用户权威陈述。",
    confidence: "strong", videos: ["IMG_6023", "IMG_6024"], regions: [region("IMG_6023", 0), region("IMG_6023", 120), region("IMG_6024", 128)],
  },
  {
    id: "slider-analysis-rotation-across-slide-r003", category: "motion",
    statement: "旋转在部分滑位和近最大滑位均被观察到；每个精确槽位是否都可旋转仍未知。",
    confidence: "high", videos: ["IMG_6024"], regions: [region("IMG_6024", 320), region("IMG_6024", 608)],
  },
  {
    id: "slider-analysis-no-jam-r003", category: "mechanism",
    statement: "反向滑回成功，没有证明机械卡死；停顿/释放更符合 detent/breakaway 阻力表现。",
    confidence: "medium", videos: ["IMG_6022", "IMG_6024"], regions: [region("IMG_6022", 225), region("IMG_6024", 320)],
  },
  {
    id: "slider-analysis-exterior-reverse-face-r003", category: "structure",
    statement: "轨道、螺丝和珠列属于 M 的反向/机构面；正常外观面可保持干净。与旧“全部机构隐藏”说法的剩余冲突等待用户确认。",
    confidence: "high", videos: ["IMG_6022", "IMG_6024"], regions: [region("IMG_6022", 0), region("IMG_6022", 100), region("IMG_6024", 199)],
  },
];
const newClaims = claimDefs.map((definition) => ({
  id: definition.id,
  stageId: "02-analysis",
  category: definition.category,
  statement: definition.statement,
  confidence: definition.confidence,
  sourceAssetIds: definition.videos.map(
    (video) => `slider-intake-user-mechanism-video-${video.slice(-4)}`),
  sourceRegions: definition.regions,
  state: "pending-review",
  decisionState: "pending-user-approval",
  analysisRevision: "006",
  assertedBy: "assistant",
}));
manifest.claims.push(...newClaims);

const intakeStage = manifest.stages[0];
intakeStage.revision += 1;
intakeStage.status = "approved";
intakeStage.priorDecision = intakeStage.decision;
intakeStage.artifactIds = [...intakeStage.artifactIds, ...sourceVideoIds, intakeMetadataAsset.id];
intakeStage.reviewArtifactIds = sourceVideoIds;
intakeStage.validations = [
  {
    id: "same-model-user-classification-approved",
    status: "pass",
    evidence: exactUserStatement,
  },
  {
    id: "three-original-video-hashes-verified",
    status: "pass",
    evidence: "IMG_6022/6023/6024 SHA-256 values match source-metadata.json and the user-provided values.",
  },
  {
    id: "video-metadata-verified",
    status: "pass",
    evidence: "426/480/821 frames; 1920×1080 HEVC with -90° display rotation; AAC stereo 48 kHz.",
  },
  {
    id: "appearance-boundary-preserved",
    status: "pass",
    evidence: "Artwork, color and texture differences are excluded from mechanism interpretation.",
  },
];
intakeStage.decision = {
  action: "approve",
  notes: exactUserStatement,
  decidedBy: "user",
  decidedAt: new Date().toISOString(),
  scope: "same-model-mechanism-intake-classification-and-frame-by-frame-analysis-request",
};

const analysisStage = manifest.stages[1];
const priorAnalysisReview = {
  revision: 2,
  stageRevision: analysisStage.revision,
  status: analysisStage.status,
  decision: analysisStage.decision,
  artifactIds: [...analysisStage.artifactIds],
  reviewArtifactIds: [...analysisStage.reviewArtifactIds],
  invalidatedBy: "user-mechanism-videos-rev-003",
};
analysisStage.revision += 1;
analysisStage.status = "ready_for_review";
analysisStage.priorAnalysisReview = priorAnalysisReview;
analysisStage.artifactIds = generatedAssetIds;
analysisStage.reviewArtifactIds = reviewBoardDefinitions.map(([id]) => id);
analysisStage.validations = [
  {
    id: "source-hashes-and-metadata",
    status: "pass",
    evidence: "All three original MOV hashes, frame counts, codecs, portrait transforms and audio metadata were independently verified.",
  },
  {
    id: "frame-accurate-pts-manifests",
    status: "pass",
    evidence: "Every decoded frame has a zero-based index and ffprobe PTS JSON/CSV entry; selected review frames resolve exactly.",
  },
  {
    id: "source-crops-linked",
    status: "pass",
    evidence: "Every review board links to original user video assets; 38 permanent key-frame crops record frame index, PTS and SHA-256.",
  },
  {
    id: "audio-evidence-linked",
    status: "pass",
    evidence: "Each video has a 5 ms RMS impulse manifest and plot; peak candidates are not presented as hidden-part proof.",
  },
  {
    id: "mechanism-unknowns-preserved",
    status: "pass",
    evidence: "Concealed shaft, slot walls, coupling, tolerances and rotation access at every exact slot position remain unknown.",
  },
  {
    id: "no-millimetre-overclaim",
    status: "pass",
    evidence: "Travel remains 0.38–0.46L with about 0.50L peak; 21 mm is compatibility-only and not a new video measurement.",
  },
  {
    id: "browser-playback-proxies",
    status: "pass",
    evidence: "Each immutable HEVC MOV has a source-linked 720×1280 H.264/AAC faststart review proxy.",
  },
  {
    id: "no-temporary-paths",
    status: "pass",
    evidence: "All manifest, claim, frame, board, audio and proxy paths are repository-relative; no temporary filesystem path is cited.",
  },
];
analysisStage.decision = null;
delete analysisStage.staleReason;
analysisStage.analysisSpec = {
  revision: 3,
  reviewMode: "frame-accurate-user-mechanism-videos",
  userStatement: exactUserStatement,
  reviewQuestion: "这个玩法/机构解读是否符合真实玩具？",
  technicalDetailsCollapsed: true,
  sourceVideoAssetIds: sourceVideoIds,
  playbackProxyAssetIds: sourceVideoIds.map(
    (_, index) => `slider-analysis-img-602${index + 2}-playback-proxy-r003`),
  approvalBasisAssetIds: analysisStage.reviewArtifactIds,
  supportingAssetIds: [
    "slider-analysis-audio-contact-sheet-r003",
    "slider-analysis-mechanism-findings-r003",
    "slider-analysis-validation-report-r003",
  ],
  claimIds: newClaims.map((claim) => claim.id),
  normalizedTravelRangeL: { minimum: 0.38, supportedMaximum: 0.46, observedPeak: 0.50 },
  provisionalMillimetreCompatibilityOnly: 21,
  detentCadenceDeg: 12,
  detentsPerFullCircle: 30,
  directlyFilmedRotation: "reversible 0↔180° and up to about 170°",
  userAuthoritativeNotFullyFilmed: "full 360°",
  unknowns: [
    "exact concealed slot profile",
    "hidden pin/shaft ownership",
    "coupling and tolerances",
    "rotation access at every exact slot location",
  ],
};

const staleReason =
  "New user-provided same-model mechanism videos reopened Gate 02. Gate 03–11 artifacts and approvals are stale until Gate 02 rev 3 is approved and downstream contracts are rebuilt.";
for (let index = 2; index <= 10; index += 1) {
  manifest.stages[index].status = "stale";
  manifest.stages[index].staleReason = staleReason;
  if (index === 6) {
    manifest.stages[index].upstreamMechanismState =
      "appearance rev 9/10 preserved as provisional-only; cannot override pending mechanism evidence";
  }
}
manifest.stages[11].status = "blocked";
manifest.stages[11].staleReason =
  `${staleReason} Gate 12 rev 1 rejection remains preserved; old shipping model stays default.`;

for (let index = 0; index < manifest.stages.length; index += 1) {
  const candidate = manifest.stages[index];
  const hashes = candidate.artifactIds.map(
    (assetId) => manifest.assets.find((asset) => asset.id === assetId)?.sha256);
  const claims = manifest.claims
    .filter((claim) => claim.stageId === candidate.id)
    .map(stableJson);
  candidate.inputDigest = index === 0
    ? digestValues([...hashes, ...claims])
    : manifest.stages[index - 1].outputDigest;
  candidate.outputDigest = digestValues([...hashes, ...claims]);
}

manifest.revision += 1;
manifest.updatedAt = new Date().toISOString();
manifest.currentState.shippingAssetUnchanged = true;
manifest.currentState.visualApproval = "gate02-rev3-mechanism-interpretation-review-pending";
manifest.currentState.deviceStatus = "not-approved";
manifest.currentState.diagnosis =
  "Three user-provided same-model mechanism videos are approved as Gate 01 intake. Gate 02 rev 3 is ready for review with frame/PTS manifests, source crops, motion boards and audio evidence. Gates 03–11 are stale; Gate 12 remains blocked/rejected; Gate 07 rev 9/10 appearance is provisional-only; the old shipping model remains default; no Blender, Unity, build, install or phone work ran.";

const event = {
  id: crypto.randomUUID(),
  type: "stage-video-mechanism-analysis-ready-for-review",
  modelId,
  manifestRevision: manifest.revision,
  timestamp: manifest.updatedAt,
  intakeStageRevision: intakeStage.revision,
  analysisStageRevision: analysisStage.revision,
  analysisEvidenceRevision: 3,
  stageId: "02-analysis",
  userStatementExact: exactUserStatement,
  intakeClassificationApproved: true,
  sourceVideoAssetIds: sourceVideoIds,
  sourceHashes: Object.fromEntries(
    sourceMetadata.files.map((source) => [path.basename(source.path), source.sha256])),
  reviewArtifactIds: analysisStage.reviewArtifactIds,
  claimIds: newClaims.map((claim) => claim.id),
  staleStageIds: manifest.stages.slice(2, 11).map((stage) => stage.id),
  gate12Status: "blocked",
  gate12PriorRejectionPreserved: true,
  oldShippingModelDefault: true,
  blenderUnityBuildInstallPhone: "not-started",
  autoApproved: false,
  reviewQuestion: analysisStage.analysisSpec.reviewQuestion,
};
saveManifest(manifest, event);
console.log(JSON.stringify({
  manifestRevision: manifest.revision,
  intakeStatus: intakeStage.status,
  analysisStatus: analysisStage.status,
  reviewArtifactIds: analysisStage.reviewArtifactIds,
  staleStageIds: event.staleStageIds,
  gate12Status: manifest.stages[11].status,
}, null, 2));
