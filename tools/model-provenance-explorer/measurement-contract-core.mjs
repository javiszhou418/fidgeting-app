export const MEASUREMENT_SOURCES = Object.freeze([
  "卡尺",
  "毫米尺照片",
  "估算"
]);

export const REQUIRED_CORE_MEASUREMENTS = Object.freeze([
  { id: "closedOverallLength", label: "闭合总长 L", method: "正交俯视；卡尺或同平面毫米尺照片" },
  { id: "overallWidth", label: "总宽 W", method: "正交俯视；测最宽处" },
  { id: "totalClosedThickness", label: "闭合总厚 T", method: "正交侧视；测闭合总厚" },
  { id: "topPlateThickness", label: "顶片厚度", method: "正交侧视；避开台阶测主体厚度" },
  { id: "bottomPlateThickness", label: "底片厚度", method: "正交侧视；避开台阶测主体厚度" },
  { id: "maximumSlideTravel", label: "最大直推行程", method: "闭合/全开同机位同尺；比较固定端点" },
  { id: "fixedAxisOffsetFromNearestEnd", label: "轴心距最近圆端", method: "俯视内部近照；圆端外缘到轴心中心" },
  { id: "rotatingCarrierDiameter", label: "旋转载体直径", method: "俯视内部近照；测圆形载体最大外径" },
  { id: "closedSeamGap", label: "闭合接缝/间隙", method: "正交侧视微距；测两片闭合可见间隙" }
]);

export const OPTIONAL_ENGINEERING_MEASUREMENTS = Object.freeze([
  { id: "bilateralGrooveCenterSpacing", label: "双槽中心距" },
  { id: "grooveWidth", label: "槽宽" },
  { id: "grooveDepth", label: "槽深" },
  { id: "fixedAxisDiameter", label: "固定轴直径" },
  { id: "upperStepHeight", label: "顶片台阶高度" },
  { id: "lowerStepHeight", label: "底片台阶高度" },
  { id: "visibleFollowerDimensions", label: "可见随动/接触尺寸" }
]);

export const MANUFACTURING_LATER_FIELDS = Object.freeze([
  { id: "operatingClearance", label: "工作间隙" },
  { id: "manufacturingAllowance", label: "加工余量" },
  { id: "manufacturingTolerance", label: "制造公差" }
]);

const asPositive = (value) => {
  if (value === "" || value === null || value === undefined) return null;
  const number = Number(value);
  return Number.isFinite(number) && number > 0 ? number : null;
};

const asUncertainty = (value) => {
  if (value === "" || value === null || value === undefined) return null;
  const number = Number(value);
  return Number.isFinite(number) && number >= 0 ? number : null;
};

export function normalizeMeasurementEntry(input = {}) {
  const valueMm = asPositive(input.valueMm);
  const uncertaintyMm = asUncertainty(input.uncertaintyMm);
  const source = MEASUREMENT_SOURCES.includes(input.source) ? input.source : null;
  return {
    valueMm,
    uncertaintyMm,
    source,
    method: String(input.method || "").trim() || null,
    photoAssetIds: Array.isArray(input.photoAssetIds)
      ? [...new Set(input.photoAssetIds.map(String).filter(Boolean))]
      : []
  };
}

export function emptyMeasurementEntries(definitions) {
  return Object.fromEntries(definitions.map(({ id }) => [id, normalizeMeasurementEntry()]));
}

export function validateMeasurementContract({
  requiredMeasurements = {},
  optionalMeasurements = {},
  cadConfig
}) {
  const normalizedRequired = Object.fromEntries(REQUIRED_CORE_MEASUREMENTS.map(({ id }) => [
    id,
    normalizeMeasurementEntry(requiredMeasurements[id])
  ]));
  const normalizedOptional = Object.fromEntries(OPTIONAL_ENGINEERING_MEASUREMENTS.map(({ id }) => [
    id,
    normalizeMeasurementEntry(optionalMeasurements[id])
  ]));
  const fieldErrors = {};
  for (const { id } of REQUIRED_CORE_MEASUREMENTS) {
    const entry = normalizedRequired[id];
    const errors = [];
    if (entry.valueMm === null) errors.push("缺少毫米值");
    if (entry.uncertaintyMm === null) errors.push("缺少不确定度");
    if (entry.source === null) errors.push("缺少来源");
    if (entry.method === null) errors.push("缺少测量方法");
    if (errors.length) fieldErrors[id] = errors;
  }
  const completeCount = REQUIRED_CORE_MEASUREMENTS.filter(({ id }) => !fieldErrors[id]).length;
  const errors = [];
  const warnings = [];
  const value = (id) => normalizedRequired[id].valueMm;
  const uncertainty = (id) => normalizedRequired[id].uncertaintyMm;
  if (["totalClosedThickness", "topPlateThickness", "bottomPlateThickness", "closedSeamGap"].every((id) => value(id) !== null && uncertainty(id) !== null)) {
    const parts = value("topPlateThickness") + value("bottomPlateThickness") + value("closedSeamGap");
    const delta = Math.abs(parts - value("totalClosedThickness"));
    const allowance = uncertainty("topPlateThickness")
      + uncertainty("bottomPlateThickness")
      + uncertainty("closedSeamGap")
      + uncertainty("totalClosedThickness");
    if (delta > allowance + 1e-9) errors.push({
      id: "thickness-stack",
      message: `顶片厚 + 底片厚 + 接缝与总厚相差 ${delta.toFixed(3)} mm，超过合计不确定度 ${allowance.toFixed(3)} mm。`
    });
  }
  if (["closedOverallLength", "overallWidth"].every((id) => value(id) !== null)) {
    const aspect = value("closedOverallLength") / value("overallWidth");
    if (aspect < 1.52 || aspect > 1.62) warnings.push({
      id: "video-aspect",
      message: `L/W=${aspect.toFixed(3)}，超出视频证据 1.52–1.62；保留实测值并复核拍摄是否正交。`
    });
  }
  if (["closedOverallLength", "overallWidth", "fixedAxisOffsetFromNearestEnd", "rotatingCarrierDiameter"].every((id) => value(id) !== null)) {
    const radius = value("rotatingCarrierDiameter") / 2;
    const offset = value("fixedAxisOffsetFromNearestEnd");
    if (
      value("rotatingCarrierDiameter") > value("overallWidth")
      || offset < radius
      || offset + radius > value("closedOverallLength")
    ) errors.push({
      id: "axis-carrier-fit",
      message: "轴心位置或旋转载体直径无法放入底片闭合轮廓。"
    });
  }
  if (
    value("closedOverallLength") !== null
    && value("maximumSlideTravel") !== null
    && uncertainty("maximumSlideTravel") !== null
  ) {
    const normalizedLimit = Number(cadConfig?.actualSMaxL);
    if (Number.isFinite(normalizedLimit)) {
      const limitMm = value("closedOverallLength") * normalizedLimit;
      if (value("maximumSlideTravel") - uncertainty("maximumSlideTravel") > limitMm + 1e-9) errors.push({
        id: "travel-containment",
        message: `行程下界超过 Gate 02 有限槽/最小重叠圆盘上限 ${limitMm.toFixed(3)} mm。`
      });
    }
  }
  return {
    requiredMeasurements: normalizedRequired,
    optionalMeasurements: normalizedOptional,
    manufacturingMeasurements: Object.fromEntries(MANUFACTURING_LATER_FIELDS.map(({ id }) => [id, {
      valueMm: null,
      state: "unknown-manufacturing-later",
      blocking: false
    }])),
    progress: {
      complete: completeCount,
      total: REQUIRED_CORE_MEASUREMENTS.length
    },
    fieldErrors,
    errors,
    warnings,
    readyForModelingContractReview: completeCount === REQUIRED_CORE_MEASUREMENTS.length && errors.length === 0
  };
}
