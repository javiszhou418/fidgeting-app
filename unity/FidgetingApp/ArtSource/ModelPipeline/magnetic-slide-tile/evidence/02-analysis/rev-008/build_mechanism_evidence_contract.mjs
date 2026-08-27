#!/usr/bin/env node
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";
import { loadManifest } from "../../../../../../../../tools/model-provenance-explorer/pipeline-core.mjs";

const here = path.dirname(fileURLToPath(import.meta.url));
const outputPath = path.join(here, "mechanism-evidence-contract.json");
const manifest = loadManifest("magnetic-slide-tile");
const assetsById = new Map(manifest.assets.map((asset) => [asset.id, asset]));
const requireAssets = (ids) => {
  for (const id of ids) {
    const asset = assetsById.get(id);
    if (!asset) throw new Error(`Missing source asset ${id}`);
    if (!asset.exists || !/^[a-f0-9]{64}$/i.test(asset.sha256 || "")) {
      throw new Error(`Unhashed or missing source asset ${id}`);
    }
  }
  return ids;
};
const unique = (values) => [...new Set(values)];
const fullRect = [0.03, 0.18, 0.94, 0.68];
const region = (assetId, frameIndex, ptsSeconds, note) => ({
  assetId,
  ...(Number.isInteger(frameIndex) ? { frameIndex } : {}),
  ...(Number.isFinite(ptsSeconds) ? { ptsSeconds } : {}),
  ...(Number.isInteger(frameIndex) ? { normalizedRect: fullRect } : {}),
  note
});
const consumers = ["interactive-cad", "blender", "unity", "haptics", "tests", "shipping-review"];
const groups = {
  img5961AndDerived: manifest.assets.filter((asset) => asset.stageId === "01-intake" && (
    asset.id === "slider-intake-user-video"
    || asset.id.startsWith("slider-intake-user-frame-")
    || ["slider-intake-user-contact-sheet", "slider-intake-audio-waveform", "slider-intake-source-metadata"].includes(asset.id)
  )).map((asset) => asset.id),
  obsidianNoteAndFrames: manifest.assets.filter((asset) => asset.stageId === "01-intake" && (
    asset.id === "slider-intake-obsidian-note"
    || asset.id.startsWith("slider-intake-obs-frame-")
    || asset.id === "slider-intake-obsidian-contact-sheet"
  )).map((asset) => asset.id),
  nxedcSameModel: manifest.assets.filter((asset) => asset.stageId === "01-intake" && asset.id.startsWith("slider-intake-nxedc-")).map((asset) => asset.id),
  halooOfficialExactProduct: manifest.assets.filter((asset) => asset.stageId === "01-intake" && asset.id.startsWith("slider-intake-haloo-official-")).map((asset) => asset.id),
  silverSameModelOriginals: [
    "slider-intake-user-mechanism-video-6022",
    "slider-intake-user-mechanism-video-6023",
    "slider-intake-user-mechanism-video-6024",
    "slider-intake-user-mechanism-source-metadata-r003"
  ],
  silverVideoDerivedEvidence: manifest.assets.filter((asset) => asset.stageId === "02-analysis" && (
    asset.path.includes("/rev-003/")
    || asset.sourceAssetIds?.some((id) => id.startsWith("slider-intake-user-mechanism-video-"))
  )).map((asset) => asset.id),
  chromeHeartsSupplementalOnly: manifest.assets.filter((asset) => (
    asset.id === "magnetic-slide-tile-supplemental-source-config-r005"
    || asset.id.startsWith("magnetic-slide-tile-supplemental-ch-")
    || asset.id.startsWith("magnetic-slide-tile-supplemental-crosstail-")
    || asset.id.startsWith("magnetic-slide-tile-supplemental-stencil-")
  )).map((asset) => asset.id),
  allGate01Intake: manifest.assets.filter((asset) => asset.stageId === "01-intake").map((asset) => asset.id)
};
const inventoryIds = unique(Object.values(groups).flat());
requireAssets(inventoryIds);
const videoFrames = groups.silverSameModelOriginals.slice(0, 3)
  .map((id) => assetsById.get(id).media?.frameCount || 0);

const constraints = [
  {
    id: "MEC-SILHOUETTE-ASPECT",
    value: {
      aspectRatioLW: [1.52, 1.62],
      physicalLengthMm: null,
      physicalWidthMm: null
    },
    units: "L/W normalized ratio",
    state: "video-measured",
    confidence: "medium",
    sourceAssetIds: requireAssets(["slider-intake-user-video", "slider-intake-obsidian-contact-sheet", "slider-intake-nxedc-contact-sheet", "slider-intake-haloo-official-01"]),
    regions: [
      region("slider-intake-user-video", null, null, "Original user video silhouette."),
      region("slider-intake-haloo-official-01", null, null, "Official exact-product shell silhouette.")
    ],
    decisionNote: "Use only normalized aspect evidence until physical measurements exist.",
    downstreamConsumers: consumers
  },
  {
    id: "MEC-PLATE-UPPER-FIXED",
    value: "upper plate transform remains identity in app/sandbox coordinates",
    units: "transform",
    state: "user-authoritative",
    confidence: "locked",
    sourceAssetIds: requireAssets(["slider-intake-user-mechanism-source-metadata-r003", "slider-intake-user-mechanism-video-6024"]),
    regions: [region("slider-intake-user-mechanism-video-6024", 199, 6.636667, "User correction controls ownership; video is supporting motion evidence.")],
    decisionNote: "Latest user correction overrides prior carrier/cover ambiguity.",
    downstreamConsumers: consumers
  },
  {
    id: "MEC-PLATE-LOWER-MOVING",
    value: "lower mechanism carrier owns translation and rotation",
    units: "transform ownership",
    state: "user-authoritative",
    confidence: "locked",
    sourceAssetIds: requireAssets(["slider-intake-user-mechanism-source-metadata-r003", "slider-intake-user-mechanism-video-6022", "slider-intake-user-mechanism-video-6024"]),
    regions: [
      region("slider-intake-user-mechanism-video-6022", 100, 3.335, "Lower reverse/mechanism face and relative motion."),
      region("slider-intake-user-mechanism-video-6024", 199, 6.636667, "Track-face exposure during compound motion.")
    ],
    decisionNote: "Different artwork does not alter moving/fixed ownership.",
    downstreamConsumers: consumers
  },
  {
    id: "MEC-PIVOT-ENDPOINT-ATTACHMENT",
    value: {
      owner: "lower mechanism carrier",
      localAttachment: "one endpoint/endcap-center",
      localSliding: false,
      hiddenAttachmentCrossSection: "unknown"
    },
    units: "normalized lower-local geometry",
    state: "user-authoritative",
    confidence: "locked",
    sourceAssetIds: requireAssets(["slider-intake-user-mechanism-source-metadata-r003", "slider-intake-user-mechanism-video-6024", "slider-intake-haloo-official-07"]),
    regions: [
      region("slider-intake-user-mechanism-video-6024", 199, 6.636667, "Visible motion supports a carrier-fixed point; exact hidden cross-section is occluded."),
      region("slider-intake-haloo-official-07", null, null, "Official internal overview supports a distinct axis region, not exact hidden attachment.")
    ],
    decisionNote: "No third pivot-sliding degree of freedom. Exact pin/slot section remains unknown.",
    downstreamConsumers: consumers
  },
  {
    id: "MEC-COMPOUND-TRANSFORM",
    value: "lower=T(s along fixed upper long axis)*R(theta about translated endpoint pivot); s and theta may update simultaneously",
    units: "2-DOF transform",
    state: "user-authoritative",
    confidence: "locked",
    sourceAssetIds: requireAssets(["slider-intake-user-mechanism-video-6024", "slider-intake-user-mechanism-source-metadata-r003"]),
    regions: [
      region("slider-intake-user-mechanism-video-6024", 183, 6.103333, "Track face appears during multi-position motion."),
      region("slider-intake-user-mechanism-video-6024", 320, 10.673333, "Rotation at a translated pose.")
    ],
    decisionNote: "Video directly supports partial/near-max rotation; all authorized positions is user-authoritative.",
    downstreamConsumers: consumers
  },
  {
    id: "MEC-RAILS-BILATERAL-LOWER-REVERSE",
    value: {
      count: 2,
      ownerFace: "lower reverse/mechanism face",
      upperFollowerCoupling: "unknown"
    },
    units: "visible regions",
    state: "user-authoritative",
    confidence: "high",
    sourceAssetIds: requireAssets(["slider-intake-user-mechanism-video-6022", "slider-intake-user-mechanism-video-6024", "slider-intake-haloo-official-07"]),
    regions: [
      region("slider-intake-user-mechanism-video-6022", 100, 3.335, "Two rails/ball rows and screws visible on reverse face."),
      region("slider-intake-user-mechanism-video-6024", 199, 6.636667, "Two longitudinal regions visible."),
      region("slider-intake-haloo-official-07", null, null, "Official internal overview.")
    ],
    decisionNote: "Clean exterior face and reverse mechanism face are distinct. Hidden upper follower is not invented.",
    downstreamConsumers: consumers
  },
  {
    id: "MEC-SLIDE-DIRECTION-AND-CLOSED-STOP",
    value: {
      openingDirectionsFromClosed: 1,
      returnPath: "same longitudinal path",
      oppositeClosedStopTravel: 0
    },
    units: "normalized motion rule",
    state: "video-measured",
    confidence: "high",
    sourceAssetIds: requireAssets(["slider-intake-user-mechanism-video-6022", "slider-intake-haloo-official-08"]),
    regions: [
      region("slider-intake-user-mechanism-video-6022", 0, 0, "Closed pose."),
      region("slider-intake-user-mechanism-video-6022", 75, 2.501667, "Outward stepped opening."),
      region("slider-intake-user-mechanism-video-6022", 225, 7.503333, "Return toward closed.")
    ],
    decisionNote: "One-way means one outward opening direction plus reversible closure, not irreversible motion.",
    downstreamConsumers: consumers
  },
  {
    id: "MEC-TRAVEL-NORMALIZED",
    value: {
      supportedRange: [0.38, 0.46],
      observedPeak: 0.5,
      millimetres: null
    },
    units: "L",
    state: "video-measured",
    confidence: "medium",
    sourceAssetIds: requireAssets(["slider-intake-user-mechanism-video-6022", "slider-intake-user-mechanism-video-6024"]),
    regions: [
      region("slider-intake-user-mechanism-video-6022", 125, 4.168333, "About 0.38±0.04L visible travel."),
      region("slider-intake-user-mechanism-video-6024", 199, 6.636667, "About 0.44L median / 0.50L peak evidence.")
    ],
    decisionNote: "Rejected provisional millimetres are not current evidence.",
    downstreamConsumers: consumers
  },
  {
    id: "MEC-ROTATION-RANGE",
    value: 360,
    units: "degrees",
    state: "user-authoritative",
    confidence: "locked",
    sourceAssetIds: requireAssets(["slider-intake-user-mechanism-source-metadata-r003", "slider-intake-user-mechanism-video-6023", "slider-intake-haloo-official-06"]),
    regions: [
      region("slider-intake-user-mechanism-video-6023", 0, 0, "Clip begins at one rotational registration."),
      region("slider-intake-user-mechanism-video-6023", 240, 8.005, "Video directly covers reversible 0↔180°; full 360° comes from user authority.")
    ],
    decisionNote: "Apparent end-to-end pose in IMG_6023 is rotation, not slide.",
    downstreamConsumers: consumers
  },
  {
    id: "MEC-DETENTS",
    value: {
      stepDegrees: 12,
      countPerRevolution: 30,
      observedImpulsesPer180: 15
    },
    units: "degrees/count",
    state: "video-measured",
    confidence: "high",
    sourceAssetIds: requireAssets(["slider-intake-user-mechanism-video-6023", "slider-analysis-img-6023-audio-impulses-csv-r003"]),
    regions: [
      region("slider-intake-user-mechanism-video-6023", 120, 4.001667, "Detented rotation sequence."),
      region("slider-intake-user-mechanism-video-6023", 240, 8.005, "About 15 candidate impulses over 180°.")
    ],
    decisionNote: "12° cadence is supported by motion and audio; physical detent recipe remains unknown.",
    downstreamConsumers: consumers
  },
  {
    id: "MEC-ROTATION-DURING-SLIDE",
    value: {
      allAuthorizedSlidePositions: true,
      directlyObservedPositions: ["partial", "near-maximum"]
    },
    units: "reachability",
    state: "user-authoritative",
    confidence: "locked",
    sourceAssetIds: requireAssets(["slider-intake-user-mechanism-video-6024", "slider-intake-user-mechanism-source-metadata-r003"]),
    regions: [
      region("slider-intake-user-mechanism-video-6024", 128, 4.268333, "Rotation at partial translation."),
      region("slider-intake-user-mechanism-video-6024", 320, 10.673333, "Rotation near maximum translation.")
    ],
    decisionNote: "Do not overstate what each video alone proves; all-position access is the latest user rule.",
    downstreamConsumers: consumers
  },
  {
    id: "MEC-RESISTANCE-SEMANTICS",
    value: {
      breakawayObserved: true,
      detentResistanceObserved: true,
      exactForceNewtons: null,
      exactMagnetSpringValues: null
    },
    units: "semantic events / unknown physical force",
    state: "inferred",
    confidence: "medium",
    sourceAssetIds: requireAssets(["slider-intake-user-mechanism-video-6023", "slider-intake-user-mechanism-video-6024", "slider-intake-haloo-official-05"]),
    regions: [
      region("slider-intake-user-mechanism-video-6023", 120, 4.001667, "Dwell/release and impulses support detent resistance."),
      region("slider-intake-haloo-official-05", null, null, "Official spring and steel/ceramic ball tuning only.")
    ],
    decisionNote: "Desktop/Haptics recipes must not claim measured Newton force or exact magnetic/spring values.",
    downstreamConsumers: ["interactive-cad", "haptics", "tests", "shipping-review"]
  },
  {
    id: "MEC-VISIBLE-HARDWARE",
    value: {
      visible: ["bilateral rails", "ball rows", "screws", "spring/ball tuning module", "circular internal region"],
      exactQuantities: null,
      hiddenCrossSections: null
    },
    units: "visible components",
    state: "video-measured",
    confidence: "high",
    sourceAssetIds: requireAssets(["slider-intake-user-mechanism-video-6022", "slider-intake-user-mechanism-video-6024", "slider-intake-haloo-official-05", "slider-intake-haloo-official-07"]),
    regions: [
      region("slider-intake-user-mechanism-video-6022", 100, 3.335, "Rails, ball rows and screws."),
      region("slider-intake-user-mechanism-video-6024", 199, 6.636667, "Mechanism face."),
      region("slider-intake-haloo-official-05", null, null, "Spring/ball tuning module."),
      region("slider-intake-haloo-official-07", null, null, "Official internal overview.")
    ],
    decisionNote: "Only visible hardware classes are locked; counts, depths and sections remain unknown.",
    downstreamConsumers: ["interactive-cad", "blender", "unity", "tests", "shipping-review"]
  },
  {
    id: "MEC-ARTWORK-MECHANISM-BOUNDARY",
    value: "different artwork, color and texture do not imply a mechanism difference",
    units: "classification rule",
    state: "user-authoritative",
    confidence: "locked",
    sourceAssetIds: requireAssets(["slider-intake-obsidian-note", "slider-intake-user-mechanism-source-metadata-r003", "slider-intake-haloo-official-03", "slider-intake-nxedc-contact-sheet"]),
    regions: [
      region("slider-intake-user-mechanism-source-metadata-r003", null, null, "User classifies silver videos as the same product with different artwork."),
      region("slider-intake-haloo-official-03", null, null, "Official colorway variation.")
    ],
    decisionNote: "Chrome Hearts official supplements are artwork-language-only and never mechanism evidence.",
    downstreamConsumers: ["blender", "unity", "tests", "shipping-review"]
  },
  {
    id: "MEC-PHYSICAL-DIMENSIONS",
    value: {
      overallLengthMm: null,
      overallWidthMm: null,
      totalThicknessMm: null,
      upperThicknessMm: null,
      lowerThicknessMm: null,
      closedGapMm: null,
      stepHeightsMm: null,
      clearanceMm: null,
      toleranceMm: null
    },
    units: "mm",
    state: "unknown",
    confidence: "unknown",
    sourceAssetIds: requireAssets(["slider-intake-user-video", "slider-intake-user-mechanism-video-6022", "slider-intake-user-mechanism-video-6024", "slider-intake-haloo-official-metadata", "slider-intake-nxedc-metadata"]),
    regions: [region("slider-intake-user-mechanism-video-6024", 199, 6.636667, "Perspective video cannot provide production dimensions/tolerances.")],
    decisionNote: "Remain unknown until caliper, orthogonal scale photo or teardown measurement.",
    downstreamConsumers: consumers
  }
];

const sources = {
  IMG_5961: ["slider-intake-user-video", ...groups.img5961AndDerived.filter((id) => id !== "slider-intake-user-video")],
  Obsidian: groups.obsidianNoteAndFrames,
  NXEDC: groups.nxedcSameModel,
  HALOO: groups.halooOfficialExactProduct,
  IMG_6022: ["slider-intake-user-mechanism-video-6022"],
  IMG_6023: ["slider-intake-user-mechanism-video-6023", "slider-analysis-img-6023-audio-impulses-csv-r003"],
  IMG_6024: ["slider-intake-user-mechanism-video-6024"],
  ChromeSupplement: groups.chromeHeartsSupplementalOnly,
  UserCorrections: ["slider-intake-user-mechanism-source-metadata-r003"]
};
const matrix = [
  ["exterior silhouette/proportions", ["IMG_5961", "Obsidian", "NXEDC", "HALOO"], [], ["production millimetres"]],
  ["upper/lower/mechanism-carrier identity", ["IMG_6022", "IMG_6024", "UserCorrections"], ["older carrier/cover ambiguity"], ["hidden attachment section"]],
  ["visible reverse/internal faces", ["IMG_6022", "IMG_6024", "HALOO"], ["clean exterior is not mechanism face"], []],
  ["bilateral rails/ball rows/screws", ["IMG_6022", "IMG_6024", "HALOO"], [], ["exact counts/depths"]],
  ["endpoint pivot attachment", ["UserCorrections", "IMG_6024"], ["video-only fixed-point fit is weaker than user correction"], ["hidden pin/slot section"]],
  ["longitudinal slide direction and return", ["IMG_6022", "HALOO"], ["one-way does not mean no return"], []],
  ["simultaneous slide+rotation", ["IMG_6024", "UserCorrections"], ["separate-mode presentation rejected"], []],
  ["travel range/end stops", ["IMG_6022", "IMG_6024"], [], ["millimetres/stop section"]],
  ["12° detents/30 positions", ["IMG_6023", "IMG_6024"], [], ["physical detent recipe"]],
  ["full-rotation evidence/user authority", ["UserCorrections", "HALOO", "IMG_6023"], ["IMG_6023 directly covers 180°, not 360°"], []],
  ["material/artwork differences", ["Obsidian", "NXEDC", "HALOO", "ChromeSupplement", "UserCorrections"], ["artwork difference is not mechanism difference"], []],
  ["hidden coupling/tolerances", ["HALOO", "IMG_6022", "IMG_6024"], [], ["upper follower", "coupling", "clearance", "tolerance"]],
  ["breakaway/detent resistance", ["IMG_6023", "IMG_6024", "HALOO"], [], ["force", "magnet", "spring constants"]]
].map(([topic, supports, conflicts, unknowns]) => ({
  topic,
  supports: supports.flatMap((key) => sources[key]),
  conflicts,
  unknowns
}));

const conclusionSpecs = [
  ["固定上片；活动底片承担复合运动", ["MEC-PLATE-UPPER-FIXED", "MEC-PLATE-LOWER-MOVING"]],
  ["端点轴刚性属于底片，没有局部轴滑动", ["MEC-PIVOT-ENDPOINT-ATTACHMENT"]],
  ["滑动与旋转可同时发生", ["MEC-COMPOUND-TRANSFORM", "MEC-ROTATION-DURING-SLIDE"]],
  ["双侧轨道位于底片反向机构面", ["MEC-RAILS-BILATERAL-LOWER-REVERSE", "MEC-VISIBLE-HARDWARE"]],
  ["从闭合只向一个外向方向打开，并沿原路返回", ["MEC-SLIDE-DIRECTION-AND-CLOSED-STOP", "MEC-TRAVEL-NORMALIZED"]],
  ["360° 为用户权威；12°/30 档由动作与音频支持", ["MEC-ROTATION-RANGE", "MEC-DETENTS"]],
  ["物理尺寸、隐藏耦合与力值仍未知", ["MEC-RESISTANCE-SEMANTICS", "MEC-PHYSICAL-DIMENSIONS"]]
].map(([statement, constraintIds]) => {
  const linked = constraints.filter((constraint) => constraintIds.includes(constraint.id));
  return {
    statement,
    constraintIds,
    confidence: linked.some((constraint) => constraint.confidence === "unknown") ? "medium" : "high",
    sourceCount: unique(linked.flatMap((constraint) => constraint.sourceAssetIds)).length
  };
});

const contract = {
  schemaVersion: 1,
  modelId: "magnetic-slide-tile",
  gate: "02-analysis",
  revision: 8,
  title: "步骤一：参考研究 · 机构证据合同",
  sourceInventory: {
    assetIds: inventoryIds,
    groups,
    counts: {
      uniqueAssets: inventoryIds.length,
      gate01Assets: groups.allGate01Intake.length,
      originalUserVideo: 1,
      img5961DerivedFrames: 12,
      obsidianFrames: 10,
      nxedcImages: 6,
      halooOfficialImages: 8,
      silverSameModelVideos: 3,
      silverVideoPtsFrames: videoFrames.reduce((sum, count) => sum + count, 0),
      chromeHeartsSupplementalAssets: groups.chromeHeartsSupplementalOnly.length
    },
    allFilesExistAndHashed: true,
    boundaries: {
      userSources: "authoritative input",
      haloo: "official exact-product external reference",
      nxedc: "same-model external candidate",
      chromeHearts: "supplemental artwork language only; never mechanism evidence"
    }
  },
  constraints,
  coverageMatrix: matrix,
  conclusions: conclusionSpecs,
  unknowns: [
    "hidden endpoint attachment cross-section",
    "upper follower and exact rail coupling",
    "physical thickness, gap, step, clearance and tolerance",
    "exact force, magnet, spring and friction values",
    "exact hidden hardware quantities"
  ],
  downstreamPolicy: {
    gate02ApprovalRequired: true,
    contractHashRequired: true,
    duplicateDefaultsForbidden: true,
    consumers: consumers,
    rule: "Every CAD, Blender, Unity, Haptics, test and shipping-review artifact must record this contract SHA-256. Generation remains locked until Gate 02 approval."
  },
  reviewQuestion: "这些证据推导出的机构约束是否正确，足以解锁交互 CAD？"
};
fs.writeFileSync(outputPath, `${JSON.stringify(contract, null, 2)}\n`);
console.log(JSON.stringify({
  outputPath,
  uniqueSources: contract.sourceInventory.counts.uniqueAssets,
  constraints: constraints.length,
  coverageRows: matrix.length,
  conclusions: conclusionSpecs.length
}, null, 2));
