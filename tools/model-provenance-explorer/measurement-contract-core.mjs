export const MEASUREMENT_SOURCES = Object.freeze([
  "卡尺",
  "毫米尺照片",
  "用户提供",
  "同款正式规格",
  "同款公开拆解校准",
  "估算"
]);

export const MEASUREMENT_BASIS_TYPES = Object.freeze({
  userMeasured: "user-measured",
  sameModelOfficialSpec: "same-model-official-spec",
  sameModelPublicTeardownCalibration: "same-model-public-teardown-calibration",
  legacyEstimate: "legacy-estimate"
});

export const STRICT_MEASUREMENT_SOURCE_CLASSES = Object.freeze({
  [MEASUREMENT_BASIS_TYPES.sameModelOfficialSpec]: Object.freeze([
    "same-model-official-spec",
    "same-model-official-product-spec"
  ]),
  [MEASUREMENT_BASIS_TYPES.sameModelPublicTeardownCalibration]: Object.freeze([
    "same-model-public-teardown",
    "same-model-public-teardown-image",
    "same-model-public-teardown-video"
  ])
});

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

const asStringList = (value) => Array.isArray(value)
  ? [...new Set(value.map((item) => String(item || "").trim()).filter(Boolean))]
  : [];

function basisFromSource(source) {
  if (["卡尺", "毫米尺照片", "用户提供"].includes(source)) return MEASUREMENT_BASIS_TYPES.userMeasured;
  if (source === "同款正式规格") return MEASUREMENT_BASIS_TYPES.sameModelOfficialSpec;
  if (source === "同款公开拆解校准") return MEASUREMENT_BASIS_TYPES.sameModelPublicTeardownCalibration;
  if (source === "估算") return MEASUREMENT_BASIS_TYPES.legacyEstimate;
  return null;
}

function normalizeCalibration(input) {
  if (!input || typeof input !== "object") return null;
  return {
    anchorFieldId: String(input.anchorFieldId || "").trim() || null,
    anchorOfficialValueMm: asPositive(input.anchorOfficialValueMm),
    imagePixelSpan: asPositive(input.imagePixelSpan),
    targetPixelSpan: asPositive(input.targetPixelSpan),
    sourceAssetId: String(input.sourceAssetId || "").trim() || null,
    note: String(input.note || "").trim() || null
  };
}

export function normalizeMeasurementEntry(input = {}) {
  const explicitlyUnknown = input.unknown === true || input.state === "unknown";
  const valueMm = asPositive(input.valueMm);
  const uncertaintyMm = asUncertainty(input.uncertaintyMm);
  const source = MEASUREMENT_SOURCES.includes(input.source) ? input.source : null;
  const inferredBasisType = basisFromSource(source);
  const basisType = Object.values(MEASUREMENT_BASIS_TYPES).includes(input.basisType)
    ? input.basisType
    : inferredBasisType;
  const method = String(input.method || "").trim() || null;
  const state = explicitlyUnknown
    ? "unknown"
    : (input.state === "known" || valueMm !== null || uncertaintyMm !== null || source !== null || method !== null)
      ? "known"
      : "unanswered";
  return {
    state,
    unknown: state === "unknown",
    valueMm: state === "unknown" ? null : valueMm,
    uncertaintyMm: state === "unknown" ? null : uncertaintyMm,
    source: state === "unknown" ? null : source,
    basisType: state === "unknown" ? null : basisType,
    method,
    sourceAssetIds: state === "unknown" ? [] : asStringList(input.sourceAssetIds),
    calibration: state === "unknown" ? null : normalizeCalibration(input.calibration),
    measured: state === "unknown" ? false : input.measured === true,
    manufacturingDimension: state === "unknown" ? false : input.manufacturingDimension === true,
    physicalClaim: state === "unknown" ? false : input.physicalClaim === true,
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
  cadConfig,
  sourceAssets = [],
  strictProvenance = false
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
  const sourceAssetById = new Map((Array.isArray(sourceAssets) ? sourceAssets : [])
    .filter((asset) => asset?.id)
    .map((asset) => [asset.id, asset]));
  for (const { id } of REQUIRED_CORE_MEASUREMENTS) {
    const entry = normalizedRequired[id];
    if (entry.state === "unknown") {
      fieldErrors[id] = ["当前不知道"];
      continue;
    }
    const errors = [];
    if (entry.valueMm === null) errors.push("缺少毫米值");
    if (entry.uncertaintyMm === null) errors.push("缺少不确定度");
    if (entry.source === null) errors.push("缺少来源");
    if (entry.method === null) errors.push("缺少测量方法");
    const strictBasis = [
      MEASUREMENT_BASIS_TYPES.sameModelOfficialSpec,
      MEASUREMENT_BASIS_TYPES.sameModelPublicTeardownCalibration
    ].includes(entry.basisType);
    if (strictProvenance && strictBasis && requiredMeasurements[id]?.basisType !== entry.basisType) {
      errors.push("非用户实测字段必须显式填写 basisType");
    }
    if (strictProvenance && entry.basisType === MEASUREMENT_BASIS_TYPES.legacyEstimate) {
      errors.push("旧的泛化估算不能用于新合同");
    }
    if (strictProvenance && !entry.basisType) errors.push("缺少来源类型");
    if (strictBasis) {
      const expectedSource = entry.basisType === MEASUREMENT_BASIS_TYPES.sameModelOfficialSpec
        ? "同款正式规格"
        : "同款公开拆解校准";
      if (entry.source !== expectedSource) errors.push(`来源必须为${expectedSource}`);
      if (!entry.sourceAssetIds.length) errors.push("缺少当前来源素材");
      const unavailable = entry.sourceAssetIds.filter((assetId) => {
        const asset = sourceAssetById.get(assetId);
        return !asset || asset.exists === false || asset.current === false || !asset.sha256;
      });
      if (unavailable.length) errors.push(`来源素材未登记、缺失、过期或无哈希：${unavailable.join("、")}`);
      const contentClasses = entry.sourceAssetIds
        .map((assetId) => sourceAssetById.get(assetId)?.contentClass)
        .filter(Boolean);
      const requiredClasses = STRICT_MEASUREMENT_SOURCE_CLASSES[entry.basisType] || [];
      if (!contentClasses.some((contentClass) => requiredClasses.includes(contentClass))) {
        errors.push(entry.basisType === MEASUREMENT_BASIS_TYPES.sameModelOfficialSpec
          ? "缺少标记为同款正式规格的来源素材"
          : "缺少标记为同款公开拆解的来源素材");
      }
      if (entry.measured || entry.manufacturingDimension || entry.physicalClaim) {
        errors.push("非用户实测值不得标为实测、物理定值或加工尺寸");
      }
    }
    if (entry.basisType === MEASUREMENT_BASIS_TYPES.sameModelPublicTeardownCalibration) {
      const calibration = entry.calibration;
      if (!calibration) errors.push("缺少可复核比例校准");
      else {
        if (!calibration.anchorFieldId) errors.push("校准缺少 anchorFieldId");
        if (calibration.anchorOfficialValueMm === null) errors.push("校准缺少 anchorOfficialValueMm");
        if (calibration.imagePixelSpan === null) errors.push("校准缺少 imagePixelSpan");
        if (calibration.targetPixelSpan === null) errors.push("校准缺少 targetPixelSpan");
        if (calibration.sourceAssetId && !entry.sourceAssetIds.includes(calibration.sourceAssetId)) {
          errors.push("校准图片必须包含在 sourceAssetIds");
        }
      }
    }
    if (errors.length) fieldErrors[id] = errors;
  }
  for (const { id } of REQUIRED_CORE_MEASUREMENTS) {
    const entry = normalizedRequired[id];
    if (entry.basisType !== MEASUREMENT_BASIS_TYPES.sameModelPublicTeardownCalibration || !entry.calibration) continue;
    const errors = fieldErrors[id] || [];
    const calibration = entry.calibration;
    const anchor = normalizedRequired[calibration.anchorFieldId];
    if (!anchor) errors.push("anchorFieldId 不是九项核心尺寸");
    else if (anchor.basisType !== MEASUREMENT_BASIS_TYPES.sameModelOfficialSpec) {
      errors.push("校准锚点必须来自同款正式规格");
    } else if (
      calibration.anchorOfficialValueMm !== null
      && anchor.valueMm !== null
      && Math.abs(anchor.valueMm - calibration.anchorOfficialValueMm) > (anchor.uncertaintyMm || 0) + 1e-9
    ) {
      errors.push("校准锚点值与正式规格不一致");
    }
    if (anchor) {
      const missingAnchorSources = anchor.sourceAssetIds.filter((assetId) => !entry.sourceAssetIds.includes(assetId));
      if (missingAnchorSources.length) errors.push(`校准字段必须同时引用锚点正式规格素材：${missingAnchorSources.join("、")}`);
    }
    if (
      calibration.anchorOfficialValueMm !== null
      && calibration.imagePixelSpan !== null
      && calibration.targetPixelSpan !== null
      && entry.valueMm !== null
      && entry.uncertaintyMm !== null
    ) {
      const derivedValueMm = calibration.anchorOfficialValueMm * calibration.targetPixelSpan / calibration.imagePixelSpan;
      calibration.scaleMmPerPixel = calibration.anchorOfficialValueMm / calibration.imagePixelSpan;
      calibration.derivedValueMm = derivedValueMm;
      calibration.deltaFromEnteredValueMm = Math.abs(entry.valueMm - derivedValueMm);
      if (Math.abs(entry.valueMm - derivedValueMm) > entry.uncertaintyMm + 1e-9) {
        errors.push(`填入值与可复核比例结果 ${derivedValueMm.toFixed(3)} mm 的差超过不确定度`);
      }
    }
    if (errors.length) fieldErrors[id] = [...new Set(errors)];
  }
  const optionalFieldErrors = {};
  for (const { id } of OPTIONAL_ENGINEERING_MEASUREMENTS) {
    const entry = normalizedOptional[id];
    const strictBasis = [
      MEASUREMENT_BASIS_TYPES.sameModelOfficialSpec,
      MEASUREMENT_BASIS_TYPES.sameModelPublicTeardownCalibration
    ].includes(entry.basisType);
    if (strictProvenance && entry.basisType === MEASUREMENT_BASIS_TYPES.legacyEstimate) {
      optionalFieldErrors[id] = ["旧的泛化估算不能用于新合同"];
      continue;
    }
    if (!strictBasis) continue;
    const errors = [];
    const expectedSource = entry.basisType === MEASUREMENT_BASIS_TYPES.sameModelOfficialSpec
      ? "同款正式规格"
      : "同款公开拆解校准";
    if (optionalMeasurements[id]?.basisType !== entry.basisType) errors.push("非用户实测字段必须显式填写 basisType");
    if (entry.valueMm === null) errors.push("缺少毫米值");
    if (entry.uncertaintyMm === null) errors.push("缺少不确定度");
    if (entry.source !== expectedSource) errors.push(`来源必须为${expectedSource}`);
    if (!entry.method) errors.push("缺少测量方法");
    if (!entry.sourceAssetIds.length) errors.push("缺少当前来源素材");
    const unavailable = entry.sourceAssetIds.filter((assetId) => {
      const asset = sourceAssetById.get(assetId);
      return !asset || asset.exists === false || asset.current === false || !asset.sha256;
    });
    if (unavailable.length) errors.push(`来源素材未登记、缺失、过期或无哈希：${unavailable.join("、")}`);
    const requiredClasses = STRICT_MEASUREMENT_SOURCE_CLASSES[entry.basisType] || [];
    const contentClasses = entry.sourceAssetIds.map((assetId) => sourceAssetById.get(assetId)?.contentClass).filter(Boolean);
    if (!contentClasses.some((contentClass) => requiredClasses.includes(contentClass))) {
      errors.push(entry.basisType === MEASUREMENT_BASIS_TYPES.sameModelOfficialSpec
        ? "缺少标记为同款正式规格的来源素材"
        : "缺少标记为同款公开拆解的来源素材");
    }
    if (entry.measured || entry.manufacturingDimension || entry.physicalClaim) {
      errors.push("非用户实测值不得标为实测、物理定值或加工尺寸");
    }
    if (entry.basisType === MEASUREMENT_BASIS_TYPES.sameModelPublicTeardownCalibration) {
      const calibration = entry.calibration;
      if (!calibration?.anchorFieldId || calibration.anchorOfficialValueMm === null || calibration.imagePixelSpan === null || calibration.targetPixelSpan === null) {
        errors.push("缺少完整可复核比例校准");
      } else {
        const anchor = normalizedRequired[calibration.anchorFieldId] || normalizedOptional[calibration.anchorFieldId];
        if (!anchor || anchor.basisType !== MEASUREMENT_BASIS_TYPES.sameModelOfficialSpec) errors.push("校准锚点必须来自同款正式规格");
        else {
          if (Math.abs(anchor.valueMm - calibration.anchorOfficialValueMm) > (anchor.uncertaintyMm || 0) + 1e-9) errors.push("校准锚点值与正式规格不一致");
          const missingAnchorSources = anchor.sourceAssetIds.filter((assetId) => !entry.sourceAssetIds.includes(assetId));
          if (missingAnchorSources.length) errors.push(`校准字段必须同时引用锚点正式规格素材：${missingAnchorSources.join("、")}`);
        }
        const derivedValueMm = calibration.anchorOfficialValueMm * calibration.targetPixelSpan / calibration.imagePixelSpan;
        calibration.scaleMmPerPixel = calibration.anchorOfficialValueMm / calibration.imagePixelSpan;
        calibration.derivedValueMm = derivedValueMm;
        calibration.deltaFromEnteredValueMm = entry.valueMm === null ? null : Math.abs(entry.valueMm - derivedValueMm);
        if (entry.valueMm !== null && entry.uncertaintyMm !== null && Math.abs(entry.valueMm - derivedValueMm) > entry.uncertaintyMm + 1e-9) {
          errors.push(`填入值与可复核比例结果 ${derivedValueMm.toFixed(3)} mm 的差超过不确定度`);
        }
      }
    }
    if (errors.length) optionalFieldErrors[id] = [...new Set(errors)];
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
    optionalFieldErrors,
    errors,
    warnings,
    readyForModelingContractReview: completeCount === REQUIRED_CORE_MEASUREMENTS.length
      && errors.length === 0
      && Object.keys(optionalFieldErrors).length === 0
  };
}
