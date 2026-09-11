import { loadManifest, saveModelingContract } from "../pipeline-core.mjs";

const modelId = "model-hhax";
const nominalSources = ["hhax-intake-nxedc-source-metadata-r002", "hhax-intake-nxedc-source-notes-r002"];
const video = "hhax-intake-nxedc-video-r002";
const manifest = loadManifest(modelId);
const official = (valueMm, uncertaintyMm, method) => ({
  state: "known",
  unknown: false,
  valueMm,
  uncertaintyMm,
  source: "同款正式规格",
  basisType: "same-model-official-spec",
  sourceAssetIds: nominalSources,
  method,
  measured: false,
  manufacturingDimension: false,
  physicalClaim: false
});
const calibrated = ({ valueMm, uncertaintyMm, method, anchorFieldId, anchorOfficialValueMm, imagePixelSpan, targetPixelSpan, teardownSources }) => ({
  state: "known",
  unknown: false,
  valueMm,
  uncertaintyMm,
  source: "同款公开拆解校准",
  basisType: "same-model-public-teardown-calibration",
  sourceAssetIds: [...nominalSources, ...teardownSources],
  method,
  measured: false,
  manufacturingDimension: false,
  physicalClaim: false,
  calibration: {
    anchorFieldId,
    anchorOfficialValueMm,
    imagePixelSpan,
    targetPixelSpan,
    sourceAssetId: teardownSources[0],
    note: "可回退的数字复原比例；不是物理实测或加工尺寸。"
  }
});

const result = saveModelingContract(modelId, {
  expectedRevision: manifest.revision,
  measurementSchemaVersion: 2,
  measurementProvenanceVersion: 1,
  requiredMeasurements: {
    closedOverallLength: official(50.5, 0.5, "逐字抄录同款公开零售标称；多站可能共用同一商品 feed，不作独立测量计数。"),
    overallWidth: official(30.9, 0.5, "逐字抄录同款公开零售标称；保留 L/W=1.634 的来源值及比例警告。"),
    totalClosedThickness: official(13.6, 1.5, "普通同款公开标称作为数字外廓基线；定制封晶可能正向增厚，故扩大复原不确定度。"),
    topPlateThickness: calibrated({ valueMm: 6.55, uncertaintyMm: 1.1, method: "公开视频 4–5 秒侧视：两主层合计投影 46.2/48 px；上下归属不可分，均取 0.50T 的可逆数字目标。", anchorFieldId: "totalClosedThickness", anchorOfficialValueMm: 13.6, imagePixelSpan: 48, targetPixelSpan: 23.12, teardownSources: [video, "hhax-intake-nxedc-teardown-sheet-r002"] }),
    bottomPlateThickness: calibrated({ valueMm: 6.55, uncertaintyMm: 1.1, method: "公开视频 4–5 秒侧视：两主层约 48:52 但归属不可可靠判定；采用对称 0.50T 可逆数字目标。", anchorFieldId: "totalClosedThickness", anchorOfficialValueMm: 13.6, imagePixelSpan: 48, targetPixelSpan: 23.12, teardownSources: [video, "hhax-intake-nxedc-teardown-sheet-r002"] }),
    maximumSlideTravel: calibrated({ valueMm: 18.7, uncertaintyMm: 2.1, method: "用户开启图与同款公开视频交叉校准：上壳长轴约 360 px，端点位移目标约 133.3 px，即约 0.37L；止点未知。", anchorFieldId: "closedOverallLength", anchorOfficialValueMm: 50.5, imagePixelSpan: 360, targetPixelSpan: 133.3, teardownSources: [video, "model-hhax-intake-r1-f2576ce0", "hhax-intake-nxedc-open-overview-r002"] }),
    fixedAxisOffsetFromNearestEnd: calibrated({ valueMm: 14.2, uncertaintyMm: 2.0, method: "同款公开视频约 64 秒近俯视：圆端到中央螺钉约 64.3 px，本体宽约 140 px，以 W 校准。", anchorFieldId: "overallWidth", anchorOfficialValueMm: 30.9, imagePixelSpan: 140, targetPixelSpan: 64.3, teardownSources: [video, "hhax-intake-nxedc-rear-patch-r002"] }),
    rotatingCarrierDiameter: calibrated({ valueMm: 21.6, uncertaintyMm: 2.0, method: "同款公开视频 58–68 秒：圆轨外径约 98 px，本体宽约 140 px，以 W 校准；透视与外缘选择纳入误差。", anchorFieldId: "overallWidth", anchorOfficialValueMm: 30.9, imagePixelSpan: 140, targetPixelSpan: 98, teardownSources: [video, "hhax-intake-nxedc-rear-patch-r002", "hhax-intake-nxedc-open-track-r002"] }),
    closedSeamGap: calibrated({ valueMm: 0.5, uncertaintyMm: 0.3, method: "公开视频 4–5 秒暗线约 1.76/48 总厚投影；混入倒角、反光和抗锯齿，仅作为渲染接缝目标。", anchorFieldId: "totalClosedThickness", anchorOfficialValueMm: 13.6, imagePixelSpan: 48, targetPixelSpan: 1.76, teardownSources: [video, "hhax-intake-nxedc-teardown-sheet-r002"] })
  },
  optionalMeasurements: {}
});
console.log(JSON.stringify({ revision: result.manifest.revision, status: result.manifest.stages[2].status, progress: result.manifest.stages[2].measurementProgress, warnings: result.contract.consistency.warnings, provenance: result.contract.provenance }, null, 2));
