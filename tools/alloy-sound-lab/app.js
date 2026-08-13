(() => {
  "use strict";

  const CLICK_SOURCES = [
    {
      id: "detent-01",
      name: "产品 Click 01",
      short: "首段基准 · 平衡",
      category: "product",
      file: "assets/audio/detent/MetalDetent_Click_01.wav",
      license: "项目内部资产"
    },
    {
      id: "detent-02",
      name: "产品 Click 02",
      short: "首段变化 · 稍暖",
      category: "product",
      file: "assets/audio/detent/MetalDetent_Click_02.wav",
      license: "项目内部资产"
    },
    {
      id: "detent-03",
      name: "产品 Click 03",
      short: "首段变化 · 稍高",
      category: "product",
      file: "assets/audio/detent/MetalDetent_Click_03.wav",
      license: "项目内部资产"
    },
    {
      id: "detent-04",
      name: "产品 Click 04",
      short: "首段变化 · 较沉",
      category: "product",
      file: "assets/audio/detent/MetalDetent_Click_04.wav",
      license: "项目内部资产"
    },
    {
      id: "detent-05",
      name: "产品 Click 05",
      short: "首段变化 · 较亮",
      category: "product",
      file: "assets/audio/detent/MetalDetent_Click_05.wav",
      license: "项目内部资产"
    },
    {
      id: "zippo-single",
      name: "合金盖 Click",
      short: "类似打火机盖 · 只取第一下",
      category: "exciter",
      file: "assets/audio/exciters/zippo-single-click.wav",
      license: "CC0 · vibe_crc"
    },
    {
      id: "mechanism-single",
      name: "机械结构 Click",
      short: "机构触发 · 只保留一个首段",
      category: "exciter",
      file: "assets/audio/exciters/metal-mechanism-single.wav",
      license: "CC0 · rottako"
    },
    {
      id: "switch-single",
      name: "钢制开关 Click",
      short: "近距离金属开关 · 扎实",
      category: "exciter",
      file: "assets/audio/exciters/resonant-switch-single.wav",
      license: "CC0 · xkeril"
    },
    {
      id: "button-single",
      name: "精密按钮 Click",
      short: "小型机械按钮 · 清脆",
      category: "exciter",
      file: "assets/audio/exciters/metallic-button-single.wav",
      license: "CC0 · BlondPanda"
    },
    {
      id: "clink-single",
      name: "明亮合金 Click",
      short: "小件合金碰触 · 泛音明亮",
      category: "exciter",
      file: "assets/audio/exciters/metal-clink-single.wav",
      license: "CC0 · Breviceps"
    },
    {
      id: "xhs-can-coin-reference",
      name: "罐头币按压原声",
      short: "21.82–23.38 秒 · 完整按入动作",
      category: "exciter",
      file: "assets/audio/exciters/xhs-can-coin-reference-press.wav",
      license: "用户提供参考 · 研究性提取与降噪",
      processing: "reference-press"
    },
    {
      id: "xhs-can-coin-pure-click",
      name: "罐头币纯净按压",
      short: "22.142 秒 · 按压瞬态，无音乐底",
      category: "exciter",
      file: "assets/audio/exciters/xhs-can-coin-pure-click.wav",
      license: "用户提供参考 · 瞬态分离与强降噪",
      processing: "reference-purified-click"
    },
    {
      id: "xhs-can-coin-pure-rebound",
      name: "罐头币纯净回弹",
      short: "23.256 秒 · 独立回弹瞬态",
      category: "exciter",
      file: "assets/audio/exciters/xhs-can-coin-pure-rebound.wav",
      license: "用户提供参考 · 瞬态分离与强降噪",
      processing: "reference-purified-click"
    }
  ];

  const RESONANCE_SOURCES = [
    {
      id: "synthetic-fork",
      name: "纯净合金 · 实时生成",
      type: "synthetic",
      referenceHz: 440
    },
    {
      id: "fork-440-box",
      name: "饱满合金 · 厚实",
      short: "主段饱满、稳定，尾段较长",
      category: "fork",
      type: "sample",
      file: "assets/audio/tuning-forks/tuning-fork-440-resonance-box.mp3",
      referenceHz: 440,
      tailOffset: 0.18,
      license: "CC0 · jmuehlhans"
    },
    {
      id: "fork-440-pickup",
      name: "纯净钢件 · 干净",
      short: "主段干净，杂音很少",
      category: "fork",
      type: "sample",
      file: "assets/audio/tuning-forks/tuning-fork-440-pickup.mp3",
      referenceHz: 438,
      tailOffset: 0.16,
      license: "CC0 · jensen1"
    },
    {
      id: "fork-432-raw",
      name: "真实金属 · 空气感",
      short: "保留真实空间与金属振动",
      category: "fork",
      type: "sample",
      file: "assets/audio/tuning-forks/tuning-fork-432-raw.mp3",
      referenceHz: 432,
      tailOffset: 0.16,
      license: "CC0 · FOSSarts"
    },
    {
      id: "vibratone-e",
      name: "粗厚圆柱 · 更沉",
      short: "主段更粗，尾段更长",
      category: "fork",
      type: "sample",
      file: "assets/audio/tuning-forks/vibratone-e.mp3",
      referenceHz: 329.63,
      tailOffset: 0.20,
      license: "CC0 · xyzr_kx"
    },
    {
      id: "none",
      name: "只有首段 · 关闭主段和尾段",
      type: "none"
    },
    {
      id: "embedded-reference",
      name: "参考视频内置机构声",
      type: "embedded"
    }
  ];

  const DEFAULT_STATE = Object.freeze({
    effectId: "alloy-balanced",
    customized: false,
    sourceId: "detent-01",
    resonanceId: "synthetic-fork",
    pitch: 0,
    clickLength: 55,
    body: 64,
    crisp: 72,
    frequency: 620,
    decay: 1.1,
    mix: 38,
    partials: 34,
    outputDb: -3,
    category: "product",
    reboundEnabled: false,
    reboundSourceId: "button-single",
    reboundPitchOffset: 3.6,
    reboundLengthScale: 0.62,
    reboundBodyScale: 0.68,
    reboundCrispBoost: 16,
    reboundGain: 0.74,
    sequenceEnabled: false,
    sequenceOffsets: [],
    sequencePitchOffsets: [],
    sequenceGains: [],
    canCoinRevision: 0,
    referenceClipEnabled: false,
    purifiedClickEnabled: false,
    referenceClipDuration: 0,
    referenceClipHeadEnd: 0,
    referenceClipBodyEnd: 0
  });

  const makeEffect = (id, name, short, tag, settings) => ({
    id,
    name,
    short,
    tag,
    settings: { ...DEFAULT_STATE, ...settings, effectId: id, customized: false }
  });

  const SOUND_EFFECTS = [
    makeEffect("alloy-balanced", "产品合金 01", "平衡、厚实、清脆", "平衡", {}),
    makeEffect("alloy-heavy", "厚壁合金", "更沉、更有重量", "厚重", {
      sourceId: "detent-04", pitch: -1.6, clickLength: 74, body: 88, crisp: 60,
      frequency: 455, decay: 1.45, mix: 46, partials: 26
    }),
    makeEffect("precision-steel", "精密钢", "短促、硬朗、清亮", "清脆", {
      sourceId: "detent-05", pitch: 0.9, clickLength: 45, body: 56, crisp: 89,
      frequency: 735, decay: 0.78, mix: 30, partials: 42
    }),
    makeEffect("warm-alloy", "温润合金", "稍暖、不刺耳", "温润", {
      sourceId: "detent-02", pitch: -0.8, clickLength: 66, body: 75, crisp: 66,
      frequency: 520, decay: 1.25, mix: 42, partials: 34
    }),
    makeEffect("bright-alloy", "明亮合金", "小件、高音、利落", "明亮", {
      sourceId: "detent-03", pitch: 1.2, clickLength: 44, body: 52, crisp: 91,
      frequency: 810, decay: 0.72, mix: 28, partials: 48
    }),
    makeEffect("zippo-lid", "合金翻盖", "厚盖弹开的掌心机械感", "翻盖", {
      sourceId: "zippo-single", resonanceId: "fork-440-box", category: "exciter",
      pitch: -1.0, clickLength: 82, body: 84, crisp: 74,
      frequency: 440, decay: 1.35, mix: 40, partials: 25
    }),
    makeEffect("mechanism-lock", "机械锁扣", "深沉、紧实的机构触发", "锁扣", {
      sourceId: "mechanism-single", resonanceId: "vibratone-e", category: "exciter",
      pitch: -1.5, clickLength: 86, body: 89, crisp: 57,
      frequency: 330, decay: 1.70, mix: 48, partials: 30
    }),
    makeEffect("steel-switch", "钢制开关", "硬质、近距离、明确", "硬质", {
      sourceId: "switch-single", category: "exciter", pitch: 0, clickLength: 60,
      body: 76, crisp: 79, frequency: 590, decay: 1.0, mix: 34, partials: 38
    }),
    makeEffect("precision-button", "精密按钮", "很短、很脆的小机械件", "精密", {
      sourceId: "button-single", resonanceId: "fork-440-pickup", category: "exciter",
      pitch: 1.2, clickLength: 38, body: 48, crisp: 94,
      frequency: 660, decay: 0.62, mix: 22, partials: 22
    }),
    makeEffect("bright-clink", "明亮碰触", "细小合金的明亮泛音", "碰触", {
      sourceId: "clink-single", resonanceId: "fork-432-raw", category: "exciter",
      pitch: 0.8, clickLength: 48, body: 50, crisp: 92,
      frequency: 760, decay: 1.15, mix: 32, partials: 58
    }),
    makeEffect("resonance-box", "饱满共鸣", "厚实、稳定、尾段舒展", "饱满", {
      resonanceId: "fork-440-box", pitch: -0.3, clickLength: 58, body: 72, crisp: 70,
      frequency: 440, decay: 1.85, mix: 52, partials: 20
    }),
    makeEffect("clean-steel", "纯净钢鸣", "干净、克制、杂音很少", "纯净", {
      sourceId: "detent-03", resonanceId: "fork-440-pickup", pitch: 0.4,
      clickLength: 48, body: 58, crisp: 85, frequency: 438,
      decay: 1.20, mix: 40, partials: 14
    }),
    makeEffect("real-metal", "真实金属鸣响", "带空气感与真实振动", "真实", {
      sourceId: "detent-04", resonanceId: "fork-432-raw", pitch: -0.6,
      clickLength: 65, body: 78, crisp: 68, frequency: 432,
      decay: 1.55, mix: 44, partials: 44
    }),
    makeEffect("thick-cylinder", "粗厚圆柱回响", "更沉、更粗、消散更久", "深沉", {
      sourceId: "detent-02", resonanceId: "vibratone-e", pitch: -1.3,
      clickLength: 74, body: 85, crisp: 60, frequency: 330,
      decay: 2.10, mix: 52, partials: 32
    }),
    makeEffect("precision-press-rebound", "精密按压回弹", "按下厚实，松手清脆回弹", "双触点", {
      sourceId: "switch-single", resonanceId: "synthetic-fork", category: "exciter",
      pitch: -0.6, clickLength: 68, body: 82, crisp: 76,
      frequency: 680, decay: 0.36, mix: 26, partials: 38,
      reboundEnabled: true, reboundSourceId: "button-single",
      reboundPitchOffset: 3.8, reboundLengthScale: 0.60,
      reboundBodyScale: 0.66, reboundCrispBoost: 18, reboundGain: 0.76
    }),
    makeEffect("can-coin-reference", "罐头币按压 · 视频原声", "开始受力、金属片连续翻转、触底收住", "原视频按压", {
      sourceId: "xhs-can-coin-reference", resonanceId: "embedded-reference", category: "exciter",
      pitch: 0, clickLength: 240, body: 50, crisp: 50,
      frequency: 620, decay: 0.33, mix: 0, partials: 0, outputDb: -3,
      canCoinRevision: 3,
      referenceClipEnabled: true,
      referenceClipDuration: 1.565,
      referenceClipHeadEnd: 0.250,
      referenceClipBodyEnd: 1.240
    }),
    makeEffect("can-coin-pure-click", "罐头币按压 + 回弹 · 纯净提取", "两声均来自原视频：按下清脆，松手独立回弹", "纯净双触点", {
      sourceId: "xhs-can-coin-pure-click", resonanceId: "none", category: "exciter",
      pitch: 0, clickLength: 116, body: 50, crisp: 50,
      frequency: 620, decay: 1.113, mix: 0, partials: 0, outputDb: -3,
      reboundEnabled: true,
      reboundSourceId: "xhs-can-coin-pure-rebound",
      reboundPitchOffset: 0,
      reboundLengthScale: 0.81,
      reboundBodyScale: 1,
      reboundCrispBoost: 0,
      reboundGain: 0.70,
      canCoinRevision: 5,
      purifiedClickEnabled: true
    })
  ];

  const STORAGE_KEY = "alloy-tone-lab-state-v2";
  const SLOT_KEY = "alloy-tone-lab-ab-v1";
  const WIND_STORAGE_KEY = "alloy-tone-lab-wind-v2";
  const WIND_METAL_MATERIALS = Object.freeze({
    "product-alloy": Object.freeze({
      character: "平衡、厚实、清脆",
      label: "产品合金", lowScale: 1.00, highRatio: 2.13, upperRatio: 3.80,
      lowGain: 0.145, highGain: 0.180, upperGain: 0.085,
      strikeGain: 0.25, strikeHz: 3200,
      lowWave: "sine", highWave: "sine", upperWave: "sine"
    }),
    "thick-wall-alloy": Object.freeze({
      character: "低沉、厚壁、重量感",
      label: "厚壁合金", lowScale: 0.85, highRatio: 1.86, upperRatio: 3.05,
      lowGain: 0.200, highGain: 0.110, upperGain: 0.035,
      strikeGain: 0.16, strikeHz: 2700,
      lowWave: "triangle", highWave: "sine", upperWave: "sine"
    }),
    "precision-steel": Object.freeze({
      character: "硬朗、清亮、钢质",
      label: "精密钢", lowScale: 1.15, highRatio: 2.38, upperRatio: 4.25,
      lowGain: 0.100, highGain: 0.200, upperGain: 0.130,
      strikeGain: 0.32, strikeHz: 4200,
      lowWave: "sine", highWave: "triangle", upperWave: "sine"
    }),
    "warm-alloy": Object.freeze({
      character: "温润、柔和、不过亮",
      label: "温润合金", lowScale: 0.95, highRatio: 1.92, upperRatio: 3.20,
      lowGain: 0.180, highGain: 0.120, upperGain: 0.045,
      strikeGain: 0.17, strikeHz: 3000,
      lowWave: "triangle", highWave: "sine", upperWave: "sine"
    }),
    "bright-alloy": Object.freeze({
      character: "高阶泛音突出、利落",
      label: "明亮合金", lowScale: 1.13, highRatio: 2.30, upperRatio: 4.15,
      lowGain: 0.105, highGain: 0.215, upperGain: 0.160,
      strikeGain: 0.34, strikeHz: 4500,
      lowWave: "sine", highWave: "triangle", upperWave: "triangle"
    })
  });
  const METAL_RING_ATTACK_SECONDS = 0.003;
  const METAL_RING_MAXIMUM_SECONDS = 0.065;
  const METAL_RING_MAXIMUM_DUTY_CYCLE = 0.72;
  const METAL_PITCH_TRACKING_EXPONENT = 0.78;
  const DEFAULT_WIND_STATE = Object.freeze({
    rpm: 250,
    weight: 72,
    air: 100,
    bladePulse: 100,
    resonance: 100,
    metalMaterialId: "bright-alloy",
    metalBrightness: 100,
    metalPitchSemitones: 9,
    coastSeconds: 2.3
  });
  const bufferCache = new Map();
  const controls = {};
  const activeNodes = new Set();
  let state = loadState();
  let slots = loadSlots();
  let windState = loadWindState();
  let audioContext = null;
  let analyser = null;
  let animationFrame = 0;
  let playbackTimer = 0;
  let toastTimer = 0;
  let windNodes = null;
  let windPlaying = false;
  let windCoasting = false;
  let windAudibleRpm = 0;
  let windStopTimer = 0;
  let windCoastFrame = 0;
  let windVisualFrame = 0;
  let windVisualLastTime = 0;
  let windVisualRpm = 0;
  let windVisualAngle = 0;

  const $ = (id) => document.getElementById(id);

  function clamp(value, min, max) {
    return Math.min(max, Math.max(min, value));
  }

  function dbToGain(db) {
    return Math.pow(10, db / 20);
  }

  function cloneSettings(value) {
    return JSON.parse(JSON.stringify(value));
  }

  function sanitizeState(candidate) {
    const next = { ...DEFAULT_STATE, ...(candidate || {}) };
    const numeric = (value, fallback) => {
      const parsed = Number(value);
      return Number.isFinite(parsed) ? parsed : fallback;
    };
    if (!SOUND_EFFECTS.some((item) => item.id === next.effectId)) next.effectId = DEFAULT_STATE.effectId;
    next.customized = Boolean(next.customized);
    if (!CLICK_SOURCES.some((item) => item.id === next.sourceId)) next.sourceId = DEFAULT_STATE.sourceId;
    if (!CLICK_SOURCES.some((item) => item.id === next.reboundSourceId)) {
      next.reboundSourceId = DEFAULT_STATE.reboundSourceId;
    }
    if (!RESONANCE_SOURCES.some((item) => item.id === next.resonanceId)) next.resonanceId = DEFAULT_STATE.resonanceId;
    if (!["product", "exciter", "fork"].includes(next.category)) next.category = DEFAULT_STATE.category;
    next.pitch = clamp(numeric(next.pitch, 0), -12, 12);
    next.clickLength = clamp(numeric(next.clickLength, 55), 20, 240);
    next.body = clamp(numeric(next.body, 64), 0, 100);
    next.crisp = clamp(numeric(next.crisp, 72), 0, 100);
    next.frequency = clamp(numeric(next.frequency, 620), 160, 1600);
    next.decay = clamp(numeric(next.decay, 1.1), 0.1, 4);
    next.mix = clamp(numeric(next.mix, 38), 0, 100);
    next.partials = clamp(numeric(next.partials, 34), 0, 100);
    next.outputDb = clamp(numeric(next.outputDb, -3), -18, 0);
    next.reboundEnabled = Boolean(next.reboundEnabled);
    next.reboundPitchOffset = clamp(numeric(next.reboundPitchOffset, 3.6), -12, 12);
    next.reboundLengthScale = clamp(numeric(next.reboundLengthScale, 0.62), 0.35, 1.5);
    next.reboundBodyScale = clamp(numeric(next.reboundBodyScale, 0.68), 0.25, 1.5);
    next.reboundCrispBoost = clamp(numeric(next.reboundCrispBoost, 16), -50, 50);
    next.reboundGain = clamp(numeric(next.reboundGain, 0.74), 0.1, 1);
    next.sequenceEnabled = Boolean(next.sequenceEnabled);
    const sequenceOffsets = Array.isArray(next.sequenceOffsets) ? next.sequenceOffsets : [];
    next.sequenceOffsets = sequenceOffsets
      .map((value) => clamp(numeric(value, 0), 0, 4))
      .filter((value, index, values) => index === 0 || value > values[index - 1])
      .slice(0, 32);
    next.sequencePitchOffsets = (Array.isArray(next.sequencePitchOffsets) ? next.sequencePitchOffsets : [])
      .map((value) => clamp(numeric(value, 0), -6, 6))
      .slice(0, 32);
    next.sequenceGains = (Array.isArray(next.sequenceGains) ? next.sequenceGains : [])
      .map((value) => clamp(numeric(value, 0.72), 0.1, 1))
      .slice(0, 32);
    if (next.sequenceEnabled && next.sequenceOffsets.length < 3) next.sequenceEnabled = false;
    next.canCoinRevision = Math.max(0, Math.round(numeric(next.canCoinRevision, 0)));
    next.referenceClipEnabled = Boolean(next.referenceClipEnabled);
    next.purifiedClickEnabled = Boolean(next.purifiedClickEnabled);
    next.referenceClipDuration = clamp(numeric(next.referenceClipDuration, 0), 0, 4);
    next.referenceClipHeadEnd = clamp(
      numeric(next.referenceClipHeadEnd, 0), 0, next.referenceClipDuration
    );
    next.referenceClipBodyEnd = clamp(
      numeric(next.referenceClipBodyEnd, 0), next.referenceClipHeadEnd, next.referenceClipDuration
    );
    if (next.referenceClipEnabled && next.referenceClipDuration < 0.2) next.referenceClipEnabled = false;
    return next;
  }

  function loadState() {
    try {
      const stored = JSON.parse(localStorage.getItem(STORAGE_KEY));
      if (stored?.effectId === "can-coin-reference"
        && Number(stored.canCoinRevision || 0) < 3) {
        return sanitizeState(getSelectedEffect("can-coin-reference").settings);
      }
      if (stored?.effectId === "can-coin-pure-click"
        && Number(stored.canCoinRevision || 0) < 5) {
        return sanitizeState(getSelectedEffect("can-coin-pure-click").settings);
      }
      return sanitizeState(stored);
    } catch (_error) {
      return { ...DEFAULT_STATE };
    }
  }

  function loadSlots() {
    try {
      const parsed = JSON.parse(localStorage.getItem(SLOT_KEY));
      return {
        A: parsed?.A ? sanitizeState(parsed.A) : null,
        B: parsed?.B ? sanitizeState(parsed.B) : null
      };
    } catch (_error) {
      return { A: null, B: null };
    }
  }

  function sanitizeWindState(candidate) {
    const next = { ...DEFAULT_WIND_STATE, ...(candidate || {}) };
    const numeric = (value, fallback) => {
      const parsed = Number(value);
      return Number.isFinite(parsed) ? parsed : fallback;
    };
    next.rpm = clamp(numeric(next.rpm, DEFAULT_WIND_STATE.rpm), 0, 600);
    next.weight = clamp(numeric(next.weight, DEFAULT_WIND_STATE.weight), 0, 100);
    next.air = clamp(numeric(next.air, DEFAULT_WIND_STATE.air), 0, 100);
    next.bladePulse = clamp(numeric(next.bladePulse, DEFAULT_WIND_STATE.bladePulse), 0, 100);
    next.resonance = clamp(numeric(next.resonance, DEFAULT_WIND_STATE.resonance), 0, 100);
    next.metalBrightness = clamp(
      numeric(next.metalBrightness, DEFAULT_WIND_STATE.metalBrightness),
      0,
      100
    );
    next.metalPitchSemitones = clamp(
      numeric(next.metalPitchSemitones, DEFAULT_WIND_STATE.metalPitchSemitones),
      -12,
      12
    );
    if (!WIND_METAL_MATERIALS[next.metalMaterialId]) {
      next.metalMaterialId = DEFAULT_WIND_STATE.metalMaterialId;
    }
    delete next.brightAlloy;
    next.coastSeconds = clamp(numeric(next.coastSeconds, DEFAULT_WIND_STATE.coastSeconds), 0.2, 3);
    return next;
  }

  function loadWindState() {
    try {
      return sanitizeWindState(JSON.parse(localStorage.getItem(WIND_STORAGE_KEY)));
    } catch (_error) {
      return { ...DEFAULT_WIND_STATE };
    }
  }

  function saveWindState() {
    localStorage.setItem(WIND_STORAGE_KEY, JSON.stringify(windState));
  }

  function saveState() {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }

  function getClickSource(id = state.sourceId) {
    return CLICK_SOURCES.find((item) => item.id === id) || CLICK_SOURCES[0];
  }

  function getResonanceSource(id = state.resonanceId) {
    return RESONANCE_SOURCES.find((item) => item.id === id) || RESONANCE_SOURCES[0];
  }

  function getSelectedEffect(id = state.effectId) {
    return SOUND_EFFECTS.find((item) => item.id === id) || SOUND_EFFECTS[0];
  }

  function setStatus(message, type = "idle") {
    $("audio-status").textContent = message;
    $("status-dot").className = `status-dot ${type === "ready" ? "ready" : type === "error" ? "error" : ""}`;
  }

  function showToast(message) {
    window.clearTimeout(toastTimer);
    document.querySelector(".toast")?.remove();
    const toast = document.createElement("div");
    toast.className = "toast";
    toast.setAttribute("role", "status");
    toast.textContent = message;
    document.body.appendChild(toast);
    toastTimer = window.setTimeout(() => toast.remove(), 2600);
  }

  async function ensureAudioContext() {
    if (!window.AudioContext && !window.webkitAudioContext) {
      throw new Error("当前浏览器不支持 Web Audio API");
    }
    if (!audioContext) {
      const Context = window.AudioContext || window.webkitAudioContext;
      audioContext = new Context({ sampleRate: 48000, latencyHint: "interactive" });
      analyser = audioContext.createAnalyser();
      analyser.fftSize = 2048;
      analyser.smoothingTimeConstant = 0.78;
      analyser.connect(audioContext.destination);
    }
    if (audioContext.state === "suspended") await audioContext.resume();
    return audioContext;
  }

  async function loadBuffer(asset) {
    if (!asset?.file) throw new Error("素材没有可加载的音频文件");
    if (bufferCache.has(asset.file)) return bufferCache.get(asset.file);
    const context = await ensureAudioContext();
    setStatus(`载入 ${asset.name}…`);
    const response = await fetch(asset.file);
    if (!response.ok) throw new Error(`无法载入 ${asset.file}`);
    const data = await response.arrayBuffer();
    const decoded = await context.decodeAudioData(data.slice(0));
    bufferCache.set(asset.file, decoded);
    return decoded;
  }

  async function preloadForSettings(settings, mode) {
    const jobs = [];
    const includesHead = settings.referenceClipEnabled
      || settings.sequenceEnabled
      || mode === "full"
      || mode === "head";
    const includesRebound = settings.reboundEnabled && (mode === "full" || mode === "tail");
    const includesResonance = (mode === "full" || mode === "body" || mode === "tail")
      && !(settings.reboundEnabled && mode === "tail");
    if (includesHead) jobs.push(loadBuffer(getClickSource(settings.sourceId)));
    if (includesRebound) jobs.push(loadBuffer(getClickSource(settings.reboundSourceId)));
    const resonance = getResonanceSource(settings.resonanceId);
    if (includesResonance && resonance.type === "sample") jobs.push(loadBuffer(resonance));
    await Promise.all(jobs);
  }

  function trackNode(node, targetSet) {
    targetSet?.add(node);
    return node;
  }

  function createNoiseBuffer(context, kind, seed) {
    const frameCount = context.sampleRate * 2;
    const buffer = context.createBuffer(2, frameCount, context.sampleRate);
    let randomState = seed >>> 0;
    const random = () => {
      randomState ^= randomState << 13;
      randomState ^= randomState >>> 17;
      randomState ^= randomState << 5;
      return ((randomState >>> 0) / 4294967295) * 2 - 1;
    };

    for (let channel = 0; channel < buffer.numberOfChannels; channel += 1) {
      const data = buffer.getChannelData(channel);
      let brown = 0;
      let smooth = 0;
      let smoother = 0;
      for (let index = 0; index < data.length; index += 1) {
        const white = random();
        if (kind === "brown") {
          brown = (brown + 0.022 * white) / 1.022;
          data[index] = clamp(brown * 3.4, -1, 1);
        } else if (kind === "smooth") {
          smooth += 0.038 * (white - smooth);
          smoother += 0.16 * (smooth - smoother);
          data[index] = clamp(smoother * 2.9, -1, 1);
        } else {
          data[index] = white * 0.72;
        }
      }
    }
    return buffer;
  }

  function createMetalRingCurve(bladePassHz) {
    const frequency = Math.max(0.001, bladePassHz);
    const dutyCycle = Math.min(
      METAL_RING_MAXIMUM_DUTY_CYCLE,
      frequency * METAL_RING_MAXIMUM_SECONDS
    );
    const attackFraction = Math.min(
      dutyCycle * 0.25,
      frequency * METAL_RING_ATTACK_SECONDS
    );
    const curve = new Float32Array(1024);
    for (let index = 0; index < curve.length; index += 1) {
      const input = (index / (curve.length - 1)) * 2 - 1;
      const phase = (input + 1) * 0.5;
      if (phase < attackFraction) {
        curve[index] = phase / attackFraction;
      } else if (phase < dutyCycle) {
        const decay = 1 - (phase - attackFraction) / (dutyCycle - attackFraction);
        curve[index] = Math.pow(decay, 1.45);
      } else {
        curve[index] = 0;
      }
    }
    return { curve, dutyCycle };
  }

  function resolveWindMetalLowModeHz(rpm, weight, material, pitchSemitones = 0) {
    const normalized = clamp((rpm - 20) / 380, 0, 1);
    const pitchTracking = Math.pow(normalized, METAL_PITCH_TRACKING_EXPONENT);
    const pitchRatio = Math.pow(2, pitchSemitones / 12);
    return (520 + weight * 100 + pitchTracking * 360)
      * material.lowScale
      * pitchRatio;
  }

  function createWindEngine(context) {
    const brownSource = context.createBufferSource();
    const airSource = context.createBufferSource();
    const resonanceSource = context.createBufferSource();
    const bodyHighPass = context.createBiquadFilter();
    const bodyLowPass = context.createBiquadFilter();
    const bodyGain = context.createGain();
    const midBand = context.createBiquadFilter();
    const midGain = context.createGain();
    const edgeHighPass = context.createBiquadFilter();
    const edgeLowPass = context.createBiquadFilter();
    const edgeGain = context.createGain();
    const airBus = context.createGain();
    const windBus = context.createGain();
    const master = context.createGain();
    const compressor = context.createDynamicsCompressor();
    const bladeLfo = context.createOscillator();
    const bladeDepth = context.createGain();
    const metalGateLfo = context.createOscillator();
    const resonanceLow = context.createBiquadFilter();
    const resonanceLowGain = context.createGain();
    const resonanceHigh = context.createBiquadFilter();
    const resonanceHighGain = context.createGain();
    const metalToneLow = context.createOscillator();
    const metalToneLowGain = context.createGain();
    const metalToneHigh = context.createOscillator();
    const metalToneHighGain = context.createGain();
    const metalToneBright = context.createOscillator();
    const metalToneBrightGain = context.createGain();
    const metalStrike = context.createBiquadFilter();
    const metalStrikeGain = context.createGain();
    const metalBus = context.createGain();
    const metalToneColor = context.createBiquadFilter();
    const metalStrikeBus = context.createGain();
    const metalPulseShape = context.createWaveShaper();
    const metalPulseDepth = context.createGain();
    const metalRingShape = context.createWaveShaper();
    const metalRingDepth = context.createGain();

    brownSource.buffer = createNoiseBuffer(context, "brown", 0x7139ac21);
    brownSource.loop = true;
    airSource.buffer = createNoiseBuffer(context, "smooth", 0xa73e91d5);
    airSource.loop = true;
    resonanceSource.buffer = createNoiseBuffer(context, "white", 0xc8147f31);
    resonanceSource.loop = true;

    bodyHighPass.type = "highpass";
    bodyHighPass.frequency.value = 72;
    bodyHighPass.Q.value = 0.45;
    bodyLowPass.type = "lowpass";
    bodyLowPass.Q.value = 0.62;
    midBand.type = "bandpass";
    midBand.Q.value = 0.92;
    edgeHighPass.type = "highpass";
    edgeHighPass.Q.value = 0.5;
    edgeLowPass.type = "lowpass";
    edgeLowPass.frequency.value = 6100;
    edgeLowPass.Q.value = 0.45;

    master.gain.value = 0.0001;
    bladeDepth.gain.value = 0;
    resonanceLow.type = "bandpass";
    resonanceLow.Q.value = 18;
    resonanceLowGain.gain.value = 0;
    resonanceHigh.type = "bandpass";
    resonanceHigh.Q.value = 24;
    resonanceHighGain.gain.value = 0;
    metalToneLow.type = "sine";
    metalToneLowGain.gain.value = 0;
    metalToneHigh.type = "sine";
    metalToneHighGain.gain.value = 0;
    metalToneBright.type = "sine";
    metalToneBrightGain.gain.value = 0;
    metalGateLfo.type = "sawtooth";
    metalStrike.type = "bandpass";
    metalStrike.Q.value = 1.15;
    metalStrikeGain.gain.value = 0;
    metalBus.gain.value = 0;
    metalToneColor.type = "lowpass";
    metalToneColor.frequency.value = 7800;
    metalToneColor.Q.value = 0.7;
    metalStrikeBus.gain.value = 0;
    metalPulseDepth.gain.value = 0;
    metalRingDepth.gain.value = 0;
    const pulseCurve = new Float32Array(1024);
    for (let index = 0; index < pulseCurve.length; index += 1) {
      const input = (index / (pulseCurve.length - 1)) * 2 - 1;
      const phase = (input + 1) * 0.5;
      const decay = phase < 0.14 ? 1 - phase / 0.14 : 0;
      pulseCurve[index] = decay * decay * decay;
    }
    metalPulseShape.curve = pulseCurve;
    metalPulseShape.oversample = "2x";
    const initialRingCurve = createMetalRingCurve(0.5);
    metalRingShape.curve = initialRingCurve.curve;
    metalRingShape.oversample = "2x";
    airBus.gain.value = 1;
    compressor.threshold.value = -18;
    compressor.knee.value = 8;
    compressor.ratio.value = 2.6;
    compressor.attack.value = 0.004;
    compressor.release.value = 0.12;

    brownSource.connect(bodyHighPass);
    bodyHighPass.connect(bodyLowPass);
    bodyLowPass.connect(bodyGain);
    bodyGain.connect(airBus);
    airSource.connect(midBand);
    midBand.connect(midGain);
    midGain.connect(airBus);
    airSource.connect(edgeHighPass);
    edgeHighPass.connect(edgeLowPass);
    edgeLowPass.connect(edgeGain);
    edgeGain.connect(airBus);
    airBus.connect(windBus);
    resonanceSource.connect(resonanceLow);
    resonanceLow.connect(resonanceLowGain);
    resonanceLowGain.connect(metalBus);
    resonanceSource.connect(resonanceHigh);
    resonanceHigh.connect(resonanceHighGain);
    resonanceHighGain.connect(metalBus);
    metalToneLow.connect(metalToneLowGain);
    metalToneLowGain.connect(metalBus);
    metalToneHigh.connect(metalToneHighGain);
    metalToneHighGain.connect(metalBus);
    metalToneBright.connect(metalToneBrightGain);
    metalToneBrightGain.connect(metalBus);
    resonanceSource.connect(metalStrike);
    metalStrike.connect(metalStrikeGain);
    metalStrikeGain.connect(metalStrikeBus);
    metalBus.connect(metalToneColor);
    metalToneColor.connect(windBus);
    metalStrikeBus.connect(windBus);
    windBus.connect(master);
    master.connect(compressor);
    compressor.connect(analyser);
    bladeLfo.connect(bladeDepth);
    bladeDepth.connect(master.gain);
    metalGateLfo.connect(metalPulseShape);
    metalPulseShape.connect(metalPulseDepth);
    metalPulseDepth.connect(metalStrikeBus.gain);
    metalGateLfo.connect(metalRingShape);
    metalRingShape.connect(metalRingDepth);
    metalRingDepth.connect(metalBus.gain);

    const now = context.currentTime;
    brownSource.start(now);
    airSource.start(now);
    resonanceSource.start(now);
    bladeLfo.start(now);
    metalGateLfo.start(now);
    metalToneLow.start(now);
    metalToneHigh.start(now);
    metalToneBright.start(now);

    return {
      sources: [brownSource, airSource, resonanceSource, bladeLfo, metalGateLfo, metalToneLow, metalToneHigh, metalToneBright],
      bodyLowPass,
      bodyGain,
      midBand,
      midGain,
      edgeHighPass,
      edgeGain,
      airBus,
      master,
      bladeLfo,
      bladeDepth,
      metalGateLfo,
      resonanceLow,
      resonanceLowGain,
      resonanceHigh,
      resonanceHighGain,
      metalToneLow,
      metalToneLowGain,
      metalToneHigh,
      metalToneHighGain,
      metalToneBright,
      metalToneBrightGain,
      metalStrike,
      metalStrikeGain,
      metalBus,
      metalToneColor,
      metalStrikeBus,
      metalPulseDepth,
      metalRingShape,
      metalRingDepth,
      metalRingDutyCycle: initialRingCurve.dutyCycle
    };
  }

  function setAudioTarget(param, value, now, smoothing = 0.006) {
    param.cancelScheduledValues(now);
    param.setTargetAtTime(value, now, smoothing);
  }

  function updateWindEngine(rpm = windAudibleRpm, gainScale = 1, smoothing = 0.006) {
    if (!audioContext || !windNodes) return;
    const now = audioContext.currentTime;
    const normalized = clamp((rpm - 20) / 380, 0, 1);
    const speedEnergy = Math.pow(normalized, 0.62);
    const weight = windState.weight / 100;
    const air = windState.air / 100;
    const pulse = windState.bladePulse / 100;
    const resonance = windState.resonance / 100;
    const metalBrightness = windState.metalBrightness / 100;
    const pitchRatio = Math.pow(2, windState.metalPitchSemitones / 12);
    const material = WIND_METAL_MATERIALS[windState.metalMaterialId]
      || WIND_METAL_MATERIALS[DEFAULT_WIND_STATE.metalMaterialId];
    const resonanceDrive = resonance;
    const pitchTracking = Math.pow(normalized, METAL_PITCH_TRACKING_EXPONENT);
    const airPresence = Math.max(0.12, 1 - 0.88 * Math.pow(resonance, 0.85));
    const masterGain = Math.max(0.0001, 0.30 * speedEnergy * gainScale);
    const bladePassHz = Math.max(0.5, (rpm / 60) * 3);
    const lowModeHz = resolveWindMetalLowModeHz(
      rpm,
      weight,
      material,
      windState.metalPitchSemitones
    );
    const highModeHz = lowModeHz * material.highRatio;
    const upperModeHz = lowModeHz * material.upperRatio;

    windNodes.metalToneLow.type = material.lowWave;
    windNodes.metalToneHigh.type = material.highWave;
    windNodes.metalToneBright.type = material.upperWave;

    const nextRingDutyCycle = Math.min(
      METAL_RING_MAXIMUM_DUTY_CYCLE,
      bladePassHz * METAL_RING_MAXIMUM_SECONDS
    );
    if (Math.abs(nextRingDutyCycle - windNodes.metalRingDutyCycle) >= 0.01) {
      const nextRingCurve = createMetalRingCurve(bladePassHz);
      windNodes.metalRingShape.curve = nextRingCurve.curve;
      windNodes.metalRingDutyCycle = nextRingCurve.dutyCycle;
    }

    setAudioTarget(windNodes.bodyLowPass.frequency, 250 + normalized * 430 + weight * 120, now, smoothing);
    setAudioTarget(windNodes.bodyGain.gain, 0.72 + weight * 0.34, now, smoothing);
    setAudioTarget(windNodes.midBand.frequency, 520 + normalized * 780 + air * 220, now, smoothing);
    setAudioTarget(windNodes.midGain.gain, 0.035 + air * 0.085, now, smoothing);
    setAudioTarget(windNodes.edgeHighPass.frequency, 3300 + normalized * 850, now, smoothing);
    setAudioTarget(windNodes.edgeGain.gain, 0.0015 + air * 0.010, now, smoothing);
    setAudioTarget(windNodes.airBus.gain, airPresence, now, smoothing);
    setAudioTarget(windNodes.master.gain, masterGain, now, smoothing);
    setAudioTarget(windNodes.bladeLfo.frequency, bladePassHz, now, Math.min(0.006, smoothing));
    setAudioTarget(windNodes.metalGateLfo.frequency, bladePassHz, now, Math.min(0.006, smoothing));
    setAudioTarget(windNodes.bladeDepth.gain, masterGain * pulse * 0.012, now, smoothing);
    setAudioTarget(windNodes.resonanceLow.frequency, lowModeHz, now, smoothing);
    setAudioTarget(windNodes.metalToneColor.frequency, 900 + Math.pow(metalBrightness, 0.72) * 6900, now, smoothing);
    setAudioTarget(windNodes.metalToneColor.Q, 0.45 + metalBrightness * 0.75, now, smoothing);
    setAudioTarget(windNodes.resonanceLowGain.gain, material.lowGain * 0.24 * (1.15 - metalBrightness * 0.15), now, smoothing);
    setAudioTarget(windNodes.resonanceHigh.frequency, highModeHz, now, smoothing);
    setAudioTarget(windNodes.resonanceHighGain.gain, material.highGain * 0.22 * (0.12 + metalBrightness * 0.88), now, smoothing);
    setAudioTarget(windNodes.metalToneLow.frequency, lowModeHz, now, smoothing);
    setAudioTarget(windNodes.metalToneLowGain.gain, material.lowGain * (1.15 - metalBrightness * 0.15), now, smoothing);
    setAudioTarget(windNodes.metalToneHigh.frequency, highModeHz, now, smoothing);
    setAudioTarget(windNodes.metalToneHighGain.gain, material.highGain * (0.12 + metalBrightness * 0.88), now, smoothing);
    setAudioTarget(windNodes.metalToneBright.frequency, upperModeHz, now, smoothing);
    setAudioTarget(windNodes.metalToneBrightGain.gain, material.upperGain * (0.04 + metalBrightness * 0.96), now, smoothing);
    setAudioTarget(
      windNodes.metalStrike.frequency,
      material.strikeHz * pitchRatio * (0.72 + metalBrightness * 0.28)
        + pitchTracking * 650
        + air * 180,
      now,
      smoothing
    );
    setAudioTarget(windNodes.metalStrikeGain.gain, material.strikeGain * (0.06 + metalBrightness * 0.94), now, smoothing);
    setAudioTarget(windNodes.metalPulseDepth.gain, resonanceDrive, now, smoothing);
    setAudioTarget(windNodes.metalRingDepth.gain, resonanceDrive, now, smoothing);
  }

  function updateWindLiveReadout() {
    const displayedRpm = windPlaying || windCoasting ? windAudibleRpm : windState.rpm;
    const bladePassHz = (displayedRpm / 60) * 3;
    $("wind-rpm-readout").textContent = Math.round(displayedRpm).toLocaleString("zh-CN");
    $("wind-rpm-readout").nextElementSibling.textContent = `RPM · ${Math.round(bladePassHz)} Hz 叶片经过`;
    $("wind-live-state").textContent = windPlaying
      ? `${Math.round(displayedRpm).toLocaleString("zh-CN")} RPM · 风声运行中`
      : windCoasting
        ? `正在减速 · ${Math.round(displayedRpm).toLocaleString("zh-CN")} RPM`
        : "静止 · 无风声";
    $("wind-start-button").textContent = windPlaying ? "风声运行中" : windCoasting ? "重新启动" : "启动风声";
    $("wind-start-button").setAttribute("aria-pressed", windPlaying ? "true" : "false");
  }

  function updateWindReadout() {
    $("wind-speed-control").value = windState.rpm;
    $("wind-weight-control").value = windState.weight;
    $("wind-air-control").value = windState.air;
    $("wind-blade-control").value = windState.bladePulse;
    $("wind-resonance-control").value = windState.resonance;
    $("wind-metal-material-control").value = windState.metalMaterialId;
    $("wind-metal-tone-control").value = windState.metalBrightness;
    $("wind-metal-pitch-control").value = windState.metalPitchSemitones;
    $("wind-coast-control").value = windState.coastSeconds;
    $("wind-speed-value").value = `${Math.round(windState.rpm).toLocaleString("zh-CN")} RPM`;
    $("wind-weight-value").value = `${Math.round(windState.weight)}%`;
    $("wind-air-value").value = `${Math.round(windState.air)}%`;
    $("wind-blade-value").value = `${Math.round(windState.bladePulse)}%`;
    const material = WIND_METAL_MATERIALS[windState.metalMaterialId];
    const lowModeHz = resolveWindMetalLowModeHz(
      windState.rpm,
      windState.weight / 100,
      material,
      windState.metalPitchSemitones
    );
    const pitchPrefix = windState.metalPitchSemitones > 0 ? "+" : "";
    const toneLabel = windState.metalBrightness < 20
      ? "沉闷"
      : windState.metalBrightness < 45
        ? "温暗"
        : windState.metalBrightness < 72
          ? "平衡"
          : windState.metalBrightness < 90
            ? "清脆"
            : "明亮清脆";
    $("wind-metal-material-description").textContent =
      `${material.character} · 主段 ${Math.round(lowModeHz)} / ${Math.round(lowModeHz * material.highRatio)} / ${Math.round(lowModeHz * material.upperRatio)} Hz · 随转速变调`;
    $("wind-metal-tone-value").value = `${Math.round(windState.metalBrightness)}% · ${toneLabel}`;
    $("wind-metal-pitch-value").value = `${pitchPrefix}${Math.round(windState.metalPitchSemitones)} 半音 · ${frequencyToNote(lowModeHz)}`;
    $("wind-metal-tone-summary").textContent =
      `当前主音 ${frequencyToNote(lowModeHz)} · ${Math.round(lowModeHz)} Hz；三层实际频率 ${Math.round(lowModeHz)} / ${Math.round(lowModeHz * material.highRatio)} / ${Math.round(lowModeHz * material.upperRatio)} Hz。`;
    $("wind-resonance-value").value = windState.resonance <= 0
      ? `0% · 纯风（${material.label} 已静音）`
      : `${Math.round(windState.resonance)}% · ${material.label}`;
    $("wind-coast-value").value = `${windState.coastSeconds.toFixed(2)} s`;
    updateWindLiveReadout();
    document.querySelectorAll("#wind-speed-control, #wind-weight-control, #wind-air-control, #wind-blade-control, #wind-resonance-control, #wind-metal-tone-control, #wind-metal-pitch-control, #wind-coast-control").forEach(setRangeProgress);
    document.querySelectorAll("[data-wind-pitch]").forEach((button) => {
      button.setAttribute(
        "aria-pressed",
        Number(button.dataset.windPitch) === windState.metalPitchSemitones ? "true" : "false"
      );
    });
    saveWindState();
  }

  function animateWindRotor(time) {
    const rotor = $("wind-rotor");
    if (!rotor) return;
    if (!windVisualLastTime) windVisualLastTime = time;
    const delta = Math.min(0.05, (time - windVisualLastTime) / 1000);
    windVisualLastTime = time;
    windVisualRpm = windAudibleRpm;
    windVisualAngle = (windVisualAngle + windVisualRpm * 6 * delta) % 360;
    rotor.style.transform = `rotate(${windVisualAngle.toFixed(2)}deg)`;
    const intensity = clamp(windVisualRpm / 400, 0, 1);
    $("wind-title").closest(".wind-lab").style.setProperty("--wind-intensity", intensity.toFixed(3));
    windVisualFrame = window.requestAnimationFrame(animateWindRotor);
  }

  async function startWind() {
    try {
      await ensureAudioContext();
      stopSound(false);
      if (windState.rpm <= 0) {
        stopWind(false, true);
        setStatus("转速为 0 · 静音", "ready");
        return;
      }
      window.clearTimeout(windStopTimer);
      window.cancelAnimationFrame(windCoastFrame);
      windCoastFrame = 0;
      windCoasting = false;
      if (!windNodes) windNodes = createWindEngine(audioContext);
      windPlaying = true;
      windAudibleRpm = windState.rpm;
      windVisualRpm = windAudibleRpm;
      updateWindEngine(windAudibleRpm, 1, 0.004);
      updateWindReadout();
      setStatus(windPlaying ? `陀螺风声 · ${Math.round(windState.rpm).toLocaleString("zh-CN")} RPM` : "转速为 0 · 静音", "ready");
      if (!windVisualFrame) windVisualFrame = window.requestAnimationFrame(animateWindRotor);
    } catch (error) {
      console.error(error);
      setStatus(error.message || "风声启动失败", "error");
    }
  }

  function stopWind(updateStatus = true, useCoast = true) {
    window.clearTimeout(windStopTimer);
    window.cancelAnimationFrame(windCoastFrame);
    windCoastFrame = 0;
    windPlaying = false;
    if (!windNodes || !audioContext) {
      windCoasting = false;
      windAudibleRpm = 0;
      windVisualRpm = 0;
      updateWindReadout();
      if (updateStatus) setStatus("陀螺已停止", "ready");
      return;
    }

    const nodesToStop = windNodes;
    const coast = useCoast ? windState.coastSeconds : 0.08;
    const startingRpm = Math.max(0, windAudibleRpm || windState.rpm);
    const startedAt = performance.now();
    windCoasting = true;
    windAudibleRpm = startingRpm;
    updateWindLiveReadout();

    const finishCoast = () => {
      if (windNodes !== nodesToStop || windPlaying) return;
      windCoasting = false;
      windAudibleRpm = 0;
      windVisualRpm = 0;
      for (const source of nodesToStop.sources) {
        try {
          source.stop();
        } catch (_error) {
          // Source may already have stopped.
        }
      }
      windNodes = null;
      updateWindLiveReadout();
    };

    const coastFrame = (time) => {
      if (windNodes !== nodesToStop || windPlaying) return;
      const progress = clamp((time - startedAt) / (coast * 1000), 0, 1);
      const remaining = 1 - progress;
      windAudibleRpm = startingRpm * Math.pow(remaining, useCoast ? 1.65 : 3.2);
      windVisualRpm = windAudibleRpm;
      updateWindEngine(windAudibleRpm, Math.pow(remaining, 0.32), 0.006);
      updateWindLiveReadout();
      if (progress < 1) {
        windCoastFrame = window.requestAnimationFrame(coastFrame);
      } else {
        windStopTimer = window.setTimeout(finishCoast, 12);
      }
    };
    windCoastFrame = window.requestAnimationFrame(coastFrame);
    if (updateStatus) setStatus(`正在停转 · ${coast.toFixed(2)} 秒消散`, "ready");
  }

  function createClickLayer(context, output, settings, startAt, targetSet, gainScale = 1) {
    const sourceAsset = getClickSource(settings.sourceId);
    const buffer = bufferCache.get(sourceAsset.file);
    if (!buffer) throw new Error(`尚未载入 ${sourceAsset.name}`);

    const source = trackNode(context.createBufferSource(), targetSet);
    const highPass = context.createBiquadFilter();
    const bodyShelf = context.createBiquadFilter();
    const bodyFocus = context.createBiquadFilter();
    const crispShelf = context.createBiquadFilter();
    const compressor = context.createDynamicsCompressor();
    const clickGain = context.createGain();

    const rate = Math.pow(2, settings.pitch / 12);
    const available = buffer.duration / rate;
    const gateDuration = Math.min(available, settings.clickLength / 1000);
    const referenceProcessing = sourceAsset.processing === "reference";
    const purifiedProcessing = sourceAsset.processing === "reference-purified-click";
    const neutralProcessing = referenceProcessing || purifiedProcessing;
    const bodyGain = neutralProcessing ? (settings.body - 50) * 0.12 : -4 + settings.body * 0.13;
    const crispGain = neutralProcessing ? (settings.crisp - 50) * 0.12 : -6 + settings.crisp * 0.16;

    source.buffer = buffer;
    source.playbackRate.setValueAtTime(rate, startAt);

    highPass.type = "highpass";
    highPass.frequency.value = referenceProcessing ? 145 : (purifiedProcessing ? 70 : 85);
    highPass.Q.value = 0.55;

    bodyShelf.type = "lowshelf";
    bodyShelf.frequency.value = 360;
    bodyShelf.gain.value = bodyGain;

    bodyFocus.type = "peaking";
    bodyFocus.frequency.value = referenceProcessing ? 1720 : (purifiedProcessing ? 1200 : 690);
    bodyFocus.Q.value = referenceProcessing ? 1.2 : (purifiedProcessing ? 0.9 : 0.85);
    bodyFocus.gain.value = referenceProcessing
      ? 2.2 + Math.max(0, settings.crisp - 50) * 0.04
      : (purifiedProcessing ? 0 : bodyGain * 0.34);

    crispShelf.type = "highshelf";
    crispShelf.frequency.value = referenceProcessing ? 3200 : (purifiedProcessing ? 3800 : 4200);
    crispShelf.gain.value = crispGain;

    compressor.threshold.value = -18;
    compressor.knee.value = 6;
    compressor.ratio.value = 2.2;
    compressor.attack.value = 0.0015;
    compressor.release.value = 0.065;

    clickGain.gain.setValueAtTime(0.0001, startAt);
    const peakGain = 0.94 * clamp(gainScale, 0.1, 1);
    clickGain.gain.linearRampToValueAtTime(peakGain, startAt + 0.002);
    clickGain.gain.setValueAtTime(peakGain, startAt + Math.max(0.004, gateDuration - 0.012));
    clickGain.gain.exponentialRampToValueAtTime(0.0001, startAt + gateDuration);

    source.connect(highPass);
    highPass.connect(bodyShelf);
    bodyShelf.connect(bodyFocus);
    bodyFocus.connect(crispShelf);
    if (purifiedProcessing) {
      crispShelf.connect(clickGain);
    } else if (referenceProcessing) {
      crispShelf.connect(clickGain);
      const transientHighPass = context.createBiquadFilter();
      const transientGain = context.createGain();
      transientHighPass.type = "highpass";
      transientHighPass.frequency.value = 2850;
      transientHighPass.Q.value = 0.72;
      const transientPeak = 0.16 + (settings.crisp / 100) * 0.46;
      transientGain.gain.setValueAtTime(0.0001, startAt);
      transientGain.gain.linearRampToValueAtTime(transientPeak, startAt + 0.007);
      transientGain.gain.exponentialRampToValueAtTime(0.0001, startAt + 0.024);
      source.connect(transientHighPass);
      transientHighPass.connect(transientGain);
      transientGain.connect(clickGain);
    } else {
      crispShelf.connect(compressor);
      compressor.connect(clickGain);
    }
    clickGain.connect(output);

    source.start(startAt);
    source.stop(startAt + gateDuration + 0.02);
    return gateDuration;
  }

  function resolveReboundSettings(settings) {
    return {
      ...settings,
      sourceId: settings.reboundSourceId,
      pitch: clamp(settings.pitch + settings.reboundPitchOffset, -12, 12),
      clickLength: clamp(settings.clickLength * settings.reboundLengthScale, 20, 240),
      body: clamp(settings.body * settings.reboundBodyScale, 0, 100),
      crisp: clamp(settings.crisp + settings.reboundCrispBoost, 0, 100)
    };
  }

  function resolveReferenceClipWindow(settings, mode) {
    if (mode === "head") return { start: 0, end: settings.referenceClipHeadEnd };
    if (mode === "body") {
      return { start: settings.referenceClipHeadEnd, end: settings.referenceClipBodyEnd };
    }
    if (mode === "tail") {
      return { start: settings.referenceClipBodyEnd, end: settings.referenceClipDuration };
    }
    return { start: 0, end: settings.referenceClipDuration };
  }

  function createReferenceClipLayer(context, output, settings, startAt, mode, targetSet) {
    const sourceAsset = getClickSource(settings.sourceId);
    const buffer = bufferCache.get(sourceAsset.file);
    if (!buffer) throw new Error(`尚未载入 ${sourceAsset.name}`);

    const window = resolveReferenceClipWindow(settings, mode);
    const playbackRate = Math.pow(2, settings.pitch / 12);
    const sourceDuration = Math.max(0.02, Math.min(buffer.duration, window.end) - window.start);
    const duration = sourceDuration / playbackRate;
    const source = trackNode(context.createBufferSource(), targetSet);
    const highPass = context.createBiquadFilter();
    const bodyShelf = context.createBiquadFilter();
    const presence = context.createBiquadFilter();
    const crispShelf = context.createBiquadFilter();
    const clipGain = context.createGain();

    source.buffer = buffer;
    source.playbackRate.setValueAtTime(playbackRate, startAt);
    highPass.type = "highpass";
    highPass.frequency.value = 82;
    highPass.Q.value = 0.55;
    bodyShelf.type = "lowshelf";
    bodyShelf.frequency.value = 360;
    bodyShelf.gain.value = (settings.body - 50) * 0.10;
    presence.type = "peaking";
    presence.frequency.value = 2200;
    presence.Q.value = 1.0;
    presence.gain.value = (settings.crisp - 50) * 0.08;
    crispShelf.type = "highshelf";
    crispShelf.frequency.value = 4300;
    crispShelf.gain.value = (settings.crisp - 50) * 0.12;

    clipGain.gain.setValueAtTime(0.0001, startAt);
    clipGain.gain.linearRampToValueAtTime(1, startAt + Math.min(0.004, duration * 0.15));
    clipGain.gain.setValueAtTime(1, startAt + Math.max(0.006, duration - 0.030));
    clipGain.gain.exponentialRampToValueAtTime(0.0001, startAt + duration);

    source.connect(highPass);
    highPass.connect(bodyShelf);
    bodyShelf.connect(presence);
    presence.connect(crispShelf);
    crispShelf.connect(clipGain);
    clipGain.connect(output);
    source.start(startAt, window.start);
    source.stop(startAt + duration + 0.025);
    return duration;
  }

  function resolveSequenceEntries(settings, mode = "full") {
    if (!settings.sequenceEnabled || settings.sequenceOffsets.length < 3) return [];
    const lastIndex = settings.sequenceOffsets.length - 1;
    let indices = settings.sequenceOffsets.map((_value, index) => index);
    if (mode === "head") indices = [0];
    if (mode === "body") indices = indices.slice(1, -1);
    if (mode === "tail") indices = [lastIndex];
    const origin = settings.sequenceOffsets[indices[0]] || 0;
    return indices.map((index) => ({
      offset: settings.sequenceOffsets[index] - origin,
      pitchOffset: settings.sequencePitchOffsets[index] || 0,
      gain: settings.sequenceGains[index] || 0.72
    }));
  }

  function resolveFullDuration(settings) {
    if (settings.referenceClipEnabled) {
      return Math.max(0.12, settings.referenceClipDuration / Math.pow(2, settings.pitch / 12));
    }
    if (settings.sequenceEnabled) {
      const lastOffset = settings.sequenceOffsets[settings.sequenceOffsets.length - 1] || 0;
      return Math.max(0.12, lastOffset + Math.max(settings.decay, settings.clickLength / 1000));
    }
    const reboundDuration = settings.reboundEnabled
      ? settings.decay + resolveReboundSettings(settings).clickLength / 1000
      : settings.decay;
    return Math.max(0.12, reboundDuration, settings.clickLength / 1000);
  }

  function createSyntheticTail(context, output, settings, startAt, targetSet) {
    if (settings.mix <= 0) return 0;
    const partialAmount = settings.partials / 100;
    const mixGain = settings.mix / 100;
    const modes = [
      { ratio: 1, amplitude: 0.34, decayScale: 1, pan: -0.025 },
      { ratio: 2.01, amplitude: 0.075 * partialAmount, decayScale: 0.76, pan: 0.04 },
      { ratio: 2.756, amplitude: 0.060 * partialAmount, decayScale: 0.58, pan: -0.065 },
      { ratio: 6.27, amplitude: 0.036 * partialAmount, decayScale: 0.34, pan: 0.08 }
    ];

    for (const mode of modes) {
      const oscillator = trackNode(context.createOscillator(), targetSet);
      const modeGain = context.createGain();
      const pan = typeof context.createStereoPanner === "function" ? context.createStereoPanner() : null;
      const endAt = startAt + Math.max(0.08, settings.decay * mode.decayScale);
      const peak = Math.max(0.0002, mode.amplitude * mixGain);

      oscillator.type = "sine";
      oscillator.frequency.setValueAtTime(settings.frequency * mode.ratio, startAt);
      modeGain.gain.setValueAtTime(0.0001, startAt);
      modeGain.gain.exponentialRampToValueAtTime(peak, startAt + 0.008);
      modeGain.gain.exponentialRampToValueAtTime(0.0001, endAt);

      oscillator.connect(modeGain);
      if (pan) {
        pan.pan.value = mode.pan;
        modeGain.connect(pan);
        pan.connect(output);
      } else {
        modeGain.connect(output);
      }

      oscillator.start(startAt);
      oscillator.stop(endAt + 0.025);
    }
    return settings.decay;
  }

  function createRecordedTail(context, output, settings, resonance, startAt, targetSet) {
    if (settings.mix <= 0) return 0;
    const buffer = bufferCache.get(resonance.file);
    if (!buffer) throw new Error(`尚未载入 ${resonance.name}`);

    const source = trackNode(context.createBufferSource(), targetSet);
    const highPass = context.createBiquadFilter();
    const presence = context.createBiquadFilter();
    const tailGain = context.createGain();
    const playbackRate = settings.frequency / resonance.referenceHz;
    const available = Math.max(0.08, (buffer.duration - resonance.tailOffset) / playbackRate);
    const duration = Math.min(settings.decay, available);
    const mixGain = Math.max(0.0002, (settings.mix / 100) * 0.46);

    source.buffer = buffer;
    source.playbackRate.setValueAtTime(playbackRate, startAt);

    highPass.type = "highpass";
    highPass.frequency.value = 120;
    highPass.Q.value = 0.5;

    presence.type = "highshelf";
    presence.frequency.value = 2600;
    presence.gain.value = -5 + settings.partials * 0.10;

    tailGain.gain.setValueAtTime(0.0001, startAt);
    tailGain.gain.exponentialRampToValueAtTime(mixGain, startAt + 0.014);
    tailGain.gain.exponentialRampToValueAtTime(0.0001, startAt + duration);

    source.connect(highPass);
    highPass.connect(presence);
    presence.connect(tailGain);
    tailGain.connect(output);
    source.start(startAt, resonance.tailOffset);
    source.stop(startAt + duration + 0.03);
    return duration;
  }

  function buildSound(context, destination, settings, startAt, mode, targetSet) {
    const output = context.createGain();
    const resonance = getResonanceSource(settings.resonanceId);
    const segmentSettings = { ...settings };
    let duration = 0;

    if (mode === "body") {
      segmentSettings.decay = Math.min(0.52, Math.max(0.22, settings.decay * 0.38));
      segmentSettings.mix = Math.min(100, settings.mix * 1.08);
    }
    if (mode === "tail") {
      segmentSettings.mix = Math.max(0, settings.mix * 0.58);
      segmentSettings.partials = Math.max(0, settings.partials * 0.72);
    }

    output.gain.setValueAtTime(dbToGain(settings.outputDb), startAt);
    if (getClickSource(settings.sourceId).processing?.startsWith("reference")) {
      const safetyLimiter = context.createDynamicsCompressor();
      safetyLimiter.threshold.value = -2.5;
      safetyLimiter.knee.value = 0;
      safetyLimiter.ratio.value = 16;
      safetyLimiter.attack.value = 0.0008;
      safetyLimiter.release.value = 0.035;
      output.connect(safetyLimiter);
      safetyLimiter.connect(destination);
    } else {
      output.connect(destination);
    }

    if (settings.referenceClipEnabled) {
      return Math.max(
        0.12,
        createReferenceClipLayer(context, output, settings, startAt, mode, targetSet)
      );
    }

    if (settings.sequenceEnabled) {
      const entries = resolveSequenceEntries(settings, mode);
      let lastOffset = 0;
      for (const entry of entries) {
        const clickSettings = { ...settings, pitch: clamp(settings.pitch + entry.pitchOffset, -12, 12) };
        const clickDuration = createClickLayer(
          context,
          output,
          clickSettings,
          startAt + entry.offset,
          targetSet,
          entry.gain
        );
        duration = Math.max(duration, entry.offset + clickDuration);
        lastOffset = Math.max(lastOffset, entry.offset);
      }
      if (mode !== "head" && resonance.type === "synthetic") {
        duration = Math.max(
          duration,
          lastOffset + createSyntheticTail(context, output, segmentSettings, startAt + lastOffset, targetSet)
        );
      }
      if (mode !== "head" && resonance.type === "sample") {
        duration = Math.max(
          duration,
          lastOffset + createRecordedTail(
            context, output, segmentSettings, resonance, startAt + lastOffset, targetSet
          )
        );
      }
      return Math.max(duration, 0.12);
    }

    if (mode === "full" || mode === "head") {
      duration = Math.max(duration, createClickLayer(context, output, settings, startAt, targetSet));
    }
    const shouldRenderResonance = !(settings.reboundEnabled && mode === "tail");
    if (shouldRenderResonance
      && (mode === "full" || mode === "body" || mode === "tail")
      && resonance.type === "synthetic") {
      duration = Math.max(duration, createSyntheticTail(context, output, segmentSettings, startAt, targetSet));
    }
    if (shouldRenderResonance
      && (mode === "full" || mode === "body" || mode === "tail")
      && resonance.type === "sample") {
      duration = Math.max(duration, createRecordedTail(context, output, segmentSettings, resonance, startAt, targetSet));
    }
    if (settings.reboundEnabled && (mode === "full" || mode === "tail")) {
      const reboundSettings = resolveReboundSettings(settings);
      const reboundOffset = mode === "full" ? settings.decay : 0;
      const reboundDuration = createClickLayer(
        context,
        output,
        reboundSettings,
        startAt + reboundOffset,
        targetSet,
        settings.reboundGain
      );
      duration = Math.max(duration, reboundOffset + reboundDuration);
    }
    return Math.max(duration, 0.12);
  }

  function stopSound(updateStatus = true) {
    window.clearTimeout(playbackTimer);
    for (const node of activeNodes) {
      try {
        node.stop();
      } catch (_error) {
        // Node may already have ended.
      }
    }
    activeNodes.clear();
    window.cancelAnimationFrame(animationFrame);
    drawEnvelope();
    if (updateStatus) setStatus("已停止", "ready");
  }

  async function playSound(settings = state, mode = "full") {
    const safeSettings = sanitizeState(settings);
    try {
      if (safeSettings.purifiedClickEnabled && mode === "body") {
        setStatus("按住阶段保持静音", "ready");
        showToast("持续背景音乐已经移除；请听首段按压或尾段回弹。");
        return;
      }
      if (!safeSettings.referenceClipEnabled
        && !safeSettings.sequenceEnabled
        && (mode === "body" || (mode === "tail" && !safeSettings.reboundEnabled))
        && getResonanceSource(safeSettings.resonanceId).type === "none") {
        setStatus("主段和尾段当前已关闭", "ready");
        showToast("请先在“主段音色”里选择一种合金音色。当前声音只有首段。");
        return;
      }
      await ensureAudioContext();
      await preloadForSettings(safeSettings, mode);
      stopWind(false, false);
      stopSound(false);
      const startAt = audioContext.currentTime + 0.025;
      const duration = buildSound(audioContext, analyser, safeSettings, startAt, mode, activeNodes);
      const statusByMode = safeSettings.purifiedClickEnabled ? {
        full: "正在播放纯净双触点 · 按压 → 回弹",
        head: "正在播放首段 · 真实按压 Click",
        body: "按住阶段保持静音",
        tail: "正在播放尾段 · 真实回弹 Click"
      } : safeSettings.referenceClipEnabled ? {
        full: "正在播放视频原声 · 按入 → 金属片翻转 → 触底",
        head: "正在播放首段 · 开始受力",
        body: "正在播放主段 · 金属片连续翻转",
        tail: "正在播放尾段 · 触底收声"
      } : safeSettings.sequenceEnabled ? {
        full: "正在播放完整声音 · 首击 → 滚珠触点 → 锁止",
        head: "正在播放首段 · 第一触点",
        body: "正在播放主段 · 滚珠连续触点",
        tail: "正在播放尾段 · 末端锁止"
      } : {
        full: safeSettings.reboundEnabled ? "正在播放完整声音 · 按压 → 回弹" : "正在播放完整声音",
        head: safeSettings.reboundEnabled ? "正在播放首段 · 按压 Click" : "正在播放首段 · 第一下 Click",
        body: safeSettings.reboundEnabled ? "正在播放主段 · 机构回响" : "正在播放主段 · 合金鸣响",
        tail: safeSettings.reboundEnabled ? "正在播放尾段 · 回弹 Click" : "正在播放尾段 · 自然消散"
      };
      setStatus(statusByMode[mode] || statusByMode.full, "ready");
      drawLiveWaveform();
      playbackTimer = window.setTimeout(() => {
        activeNodes.clear();
        drawEnvelope();
        setStatus("试听完成", "ready");
      }, (duration + 0.18) * 1000);
    } catch (error) {
      console.error(error);
      setStatus(error.message || "音频播放失败", "error");
      showToast("请通过本地服务器打开工具；file:// 模式无法载入音频素材。");
    }
  }

  async function previewMaterial(material) {
    try {
      const context = await ensureAudioContext();
      const buffer = await loadBuffer(material);
      stopSound(false);
      const source = trackNode(context.createBufferSource(), activeNodes);
      const gain = context.createGain();
      const now = context.currentTime + 0.02;
      const isFork = material.category === "fork";
      const duration = Math.min(isFork ? 3.2 : 1.2, buffer.duration);
      source.buffer = buffer;
      gain.gain.setValueAtTime(dbToGain(state.outputDb), now);
      if (isFork) gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
      source.connect(gain);
      gain.connect(analyser);
      source.start(now);
      source.stop(now + duration);
      setStatus(`${isFork ? "主段" : "首段"}素材：${material.name}`, "ready");
      drawLiveWaveform();
      playbackTimer = window.setTimeout(() => {
        activeNodes.clear();
        drawEnvelope();
        setStatus("素材试听完成", "ready");
      }, (duration + 0.12) * 1000);
    } catch (error) {
      console.error(error);
      setStatus(error.message || "素材试听失败", "error");
    }
  }

  function frequencyToNote(frequency) {
    const names = ["C", "C♯", "D", "D♯", "E", "F", "F♯", "G", "G♯", "A", "A♯", "B"];
    const midi = Math.round(69 + 12 * Math.log2(frequency / 440));
    const name = names[((midi % 12) + 12) % 12];
    const octave = Math.floor(midi / 12) - 1;
    const exact = 440 * Math.pow(2, (midi - 69) / 12);
    const cents = Math.round(1200 * Math.log2(frequency / exact));
    return `${name}${octave}${Math.abs(cents) >= 2 ? ` ${cents > 0 ? "+" : ""}${cents}¢` : ""}`;
  }

  function setRangeProgress(input) {
    const min = Number(input.min);
    const max = Number(input.max);
    const value = Number(input.value);
    const percentage = ((value - min) / (max - min)) * 100;
    input.style.setProperty("--range-progress", `${percentage}%`);
  }

  function updateUI() {
    controls.source.value = state.sourceId;
    controls.resonance.value = state.resonanceId;
    controls.pitch.value = state.pitch;
    controls.clickLength.value = state.clickLength;
    controls.body.value = state.body;
    controls.crisp.value = state.crisp;
    controls.frequency.value = state.frequency;
    controls.decay.value = state.decay;
    controls.mix.value = state.mix;
    controls.partials.value = state.partials;
    controls.output.value = state.outputDb;

    $("pitch-value").value = `${state.pitch.toFixed(1)} 半音`;
    $("click-length-value").value = `${Math.round(state.clickLength)} ms`;
    $("body-value").value = `${Math.round(state.body)}%`;
    $("crisp-value").value = `${Math.round(state.crisp)}%`;
    $("frequency-value").value = `${Math.round(state.frequency)} Hz`;
    $("decay-value").value = `${state.decay.toFixed(2)} s`;
    $("mix-value").value = `${Math.round(state.mix)}%`;
    $("partials-value").value = `${Math.round(state.partials)}%`;
    $("output-value").value = `${state.outputDb < 0 ? "−" : ""}${Math.abs(state.outputDb).toFixed(1)} dB`;

    const pitchPrefix = state.pitch > 0 ? "+" : "";
    const hasRebound = state.reboundEnabled;
    const hasSequence = state.sequenceEnabled;
    const hasReferencePress = state.referenceClipEnabled;
    const hasPurifiedClick = state.purifiedClickEnabled;
    const reboundSettings = resolveReboundSettings(state);
    const reboundPitchPrefix = reboundSettings.pitch > 0 ? "+" : "";
    const sequenceIntervals = state.sequenceOffsets.slice(1).map((offset, index) => (
      offset - state.sequenceOffsets[index]
    ));
    const averageSequenceInterval = sequenceIntervals.length
      ? Math.round(sequenceIntervals.reduce((sum, value) => sum + value, 0) / sequenceIntervals.length * 1000)
      : 0;
    $("head-segment-summary").textContent = hasPurifiedClick
      ? `${Math.round(state.clickLength)} ms · ${pitchPrefix}${state.pitch.toFixed(1)} 半音`
      : hasReferencePress
      ? `${state.referenceClipHeadEnd.toFixed(2)} 秒 · ${pitchPrefix}${state.pitch.toFixed(1)} 半音`
      : `${Math.round(state.clickLength)} ms · ${pitchPrefix}${state.pitch.toFixed(1)} 半音`;
    $("body-segment-summary").textContent = hasPurifiedClick
      ? "持续音乐已移除 · 按住时静音"
      : hasReferencePress
      ? `${(state.referenceClipBodyEnd - state.referenceClipHeadEnd).toFixed(2)} 秒 · 原视频机构连响`
      : (hasSequence
        ? `${Math.max(0, state.sequenceOffsets.length - 2)} 个滚珠触点 · 平均 ${averageSequenceInterval} ms`
        : `${Math.round(state.frequency)} Hz (${frequencyToNote(state.frequency)}) · ${Math.round(state.mix)}% 响度`);
    $("tail-segment-summary").textContent = hasPurifiedClick
      ? `${state.decay.toFixed(2)} 秒后 · 独立回弹素材`
      : hasReferencePress
      ? `${(state.referenceClipDuration - state.referenceClipBodyEnd).toFixed(2)} 秒 · 触底收声`
      : (hasSequence
        ? `最后锁止 · ${state.decay.toFixed(2)} 秒余振`
        : (hasRebound
        ? `${state.decay.toFixed(2)} 秒后 · ${reboundPitchPrefix}${reboundSettings.pitch.toFixed(1)} 半音`
        : `${state.decay.toFixed(2)} 秒 · 无第二下`));

    $("segment-flow-label").textContent = hasPurifiedClick
      ? "按压 Click → 按住静音 → 回弹 Click"
      : hasReferencePress
      ? "开始受力 → 金属片连续翻转 → 触底收住"
      : (hasSequence
        ? "首击 → 滚珠连续触点 → 末端锁止"
        : (hasRebound ? "按压 → 机构行程 → 回弹" : "首段 → 主段 → 尾段"));
    $("stage-guide").textContent = hasPurifiedClick
      ? "按压与回弹都从同一次视频动作中独立提取：22.142 秒是按下，23.256 秒是松手回弹；两声分别降噪，不用第一声复制。中间持续音乐已经清除。"
      : hasReferencePress
      ? "这一条直接使用视频 21.82–23.38 秒的完整按压动作：不是滚珠循环，也不是另一处单击。首、中、尾分别对应开始压入、金属片连续翻转和最终触底。"
      : (hasSequence
        ? "这条参考还原把动作拆成三段：第一下硬触点、滚珠沿轨道连续越齿、最后一次锁止。每段都可以单独试听。"
        : (hasRebound
        ? "这是明确的双触点音效：按下时第一声，松手后第二声。点击三段可以分别听按压、短促机构回响和回弹。"
        : "点击任意一段，可以把这一段单独拿出来听。普通音效只有第一下 Click，主段和尾段是一股连续的金属鸣响。"));
    $("head-segment-title").textContent = hasPurifiedClick ? "真实按压 Click" : (hasReferencePress ? "开始压入" : (hasSequence ? "第一触点" : (hasRebound ? "按压 Click" : "第一下 Click")));
    $("body-segment-title").textContent = hasPurifiedClick ? "按住阶段 · 静音" : (hasReferencePress ? "金属片连续翻转" : (hasSequence ? "滚珠连续触点" : (hasRebound ? "机构回响" : "合金鸣响")));
    $("tail-segment-title").textContent = hasPurifiedClick ? "真实回弹 Click" : (hasReferencePress ? "触底收声" : (hasSequence ? "末端锁止" : (hasRebound ? "回弹 Click" : "自然消散")));
    $("tail-segment-action").textContent = hasPurifiedClick ? "只听回弹 ▶" : (hasReferencePress ? "只听触底 ▶" : (hasSequence ? "只听锁止 ▶" : (hasRebound ? "只听回弹 ▶" : "只听尾段 ▶")));
    document.querySelector('[data-preview-segment="body"] .segment-action').textContent = hasPurifiedClick
      ? "无可播放主段"
      : "只听主段 ▶";
    $("play-body-button").textContent = hasPurifiedClick ? "主段已清除" : "只听主段";
    $("play-tail-button").textContent = hasPurifiedClick ? "只听回弹" : (hasReferencePress ? "只听触底" : (hasSequence ? "只听锁止" : (hasRebound ? "只听回弹" : "只听尾段")));
    $("tail-control-hint").textContent = hasPurifiedClick ? "松手后的独立第二声" : (hasReferencePress ? "原视频动作的最后阶段" : (hasSequence ? "最后一下与腔体余振" : (hasRebound ? "松手后的第二下" : "只是慢慢消失")));
    $("tail-control-explanation").textContent = hasPurifiedClick
      ? "尾段是从视频 23.256 秒单独提取的真实回弹，不是按压声的复制。下面控制按下后多久松手回弹。"
      : hasReferencePress
      ? "这条声音的尾段已经包含原视频里的触底和收声，不再另外生成回弹或人造共鸣。"
      : (hasSequence
        ? "尾段是滚珠落入末端齿位的最后一下，随后留下小型金属腔体余振。下面控制这股余振的消散时间。"
        : (hasRebound
        ? "这条音效的尾端是独立回弹 Click，不是主段余音。下面控制按压到回弹之间的时间。"
        : "尾段不是新的声音，而是主段继续衰减。这里仅决定它要拖多久，不会增加第二下 Click。"));
    $("decay-label-text").textContent = hasPurifiedClick ? "按压到回弹间隔" : (hasReferencePress ? "参考片段尾段（固定）" : (hasSequence ? "锁止余振时长" : (hasRebound ? "按压到回弹间隔" : "消散时长")));
    $("decay-cue-start").textContent = hasPurifiedClick ? "快速松手" : (hasReferencePress ? "视频原始边界" : (hasSequence ? "立即收住" : (hasRebound ? "快速回弹" : "短促结束")));
    $("decay-cue-end").textContent = hasPurifiedClick ? "较长按住" : (hasReferencePress ? "不额外生成" : (hasSequence ? "腔体多响一会" : (hasRebound ? "较长按住" : "悠长消散")));

    const lockedReference = hasReferencePress || hasPurifiedClick;
    controls.source.disabled = lockedReference;
    controls.resonance.disabled = lockedReference;
    controls.clickLength.disabled = lockedReference;
    controls.frequency.disabled = lockedReference;
    controls.decay.disabled = hasReferencePress;
    controls.mix.disabled = lockedReference;
    controls.partials.disabled = lockedReference;
    $("play-body-button").disabled = hasPurifiedClick;
    $("play-tail-button").disabled = false;
    document.querySelectorAll("[data-preview-segment]").forEach((button) => {
      button.disabled = hasPurifiedClick && button.dataset.previewSegment === "body";
    });
    $("library-count").textContent = `${SOUND_EFFECTS.length} 条完整音效`;

    const selectedEffect = getSelectedEffect();
    $("selected-effect-name").textContent = `${selectedEffect.name}${state.customized ? " · 已调整" : ""}`;
    $("selected-effect-description").textContent = `${selectedEffect.short} · ${state.customized ? "当前为你的调整版本" : "完整原始方案"}`;

    document.querySelectorAll('input[type="range"]').forEach(setRangeProgress);
    updateSlotButtons();
    renderEffectPicker();
    drawEnvelope();
    saveState();
  }

  function renderEffectPicker() {
    const grid = $("effect-grid");
    grid.innerHTML = "";

    for (const [index, effect] of SOUND_EFFECTS.entries()) {
      const selected = effect.id === state.effectId;
      const button = document.createElement("button");
      button.type = "button";
      button.className = "effect-card";
      button.setAttribute("aria-pressed", selected ? "true" : "false");
      button.innerHTML = `
        <span class="effect-number">${String(index + 1).padStart(2, "0")}</span>
        <strong>${effect.name}</strong>
        <small>${effect.short}</small>
        <span class="effect-tag">${selected ? (state.customized ? "已选 · 已调整" : "已选 · 点击重听") : `${effect.tag} · 点击试听`}</span>
      `;
      button.addEventListener("click", () => selectEffect(effect.id));
      grid.appendChild(button);
    }
  }

  function selectEffect(effectId, shouldPlay = true) {
    const effect = getSelectedEffect(effectId);
    state = sanitizeState({ ...effect.settings, effectId: effect.id, customized: false });
    updateUI();
    showToast(`已选择“${effect.name}”，下方已显示它的首段、主段和尾段。`);
    if (shouldPlay) playSound();
  }

  function markCustomized() {
    state.customized = true;
  }

  function populateSelects() {
    controls.source.innerHTML = "";
    const productGroup = document.createElement("optgroup");
    productGroup.label = "首段 · 产品现有";
    const exciterGroup = document.createElement("optgroup");
    exciterGroup.label = "首段 · 可选素材";
    for (const source of CLICK_SOURCES) {
      const option = document.createElement("option");
      option.value = source.id;
      option.textContent = source.name;
      (source.category === "product" ? productGroup : exciterGroup).appendChild(option);
    }
    controls.source.append(productGroup, exciterGroup);

    controls.resonance.innerHTML = "";
    for (const resonance of RESONANCE_SOURCES) {
      const option = document.createElement("option");
      option.value = resonance.id;
      option.textContent = resonance.name;
      controls.resonance.appendChild(option);
    }
  }

  function updateSlotButtons() {
    for (const slot of ["A", "B"]) {
      const playButton = document.querySelector(`[data-play-slot="${slot}"]`);
      const saveButton = document.querySelector(`[data-save-slot="${slot}"]`);
      playButton.disabled = !slots[slot];
      saveButton.textContent = slots[slot] ? "覆盖当前" : "保存当前";
    }
  }

  function saveSlot(slot) {
    slots[slot] = cloneSettings(state);
    localStorage.setItem(SLOT_KEY, JSON.stringify(slots));
    updateSlotButtons();
    showToast(`已保存到 ${slot}：${Math.round(state.frequency)} Hz / ${state.decay.toFixed(2)} s`);
  }

  function configureControls() {
    controls.source = $("source-select");
    controls.resonance = $("resonance-select");
    controls.pitch = $("pitch-control");
    controls.clickLength = $("click-length-control");
    controls.body = $("body-control");
    controls.crisp = $("crisp-control");
    controls.frequency = $("frequency-control");
    controls.decay = $("decay-control");
    controls.mix = $("mix-control");
    controls.partials = $("partials-control");
    controls.output = $("output-control");

    populateSelects();

    controls.source.addEventListener("change", (event) => {
      state.sourceId = event.target.value;
      state.category = getClickSource().category;
      markCustomized();
      updateUI();
    });
    controls.resonance.addEventListener("change", (event) => {
      state.resonanceId = event.target.value;
      const resonance = getResonanceSource();
      if (resonance.referenceHz && resonance.type === "sample") state.frequency = resonance.referenceHz;
      markCustomized();
      updateUI();
    });

    const rangeBindings = [
      [controls.pitch, "pitch"],
      [controls.clickLength, "clickLength"],
      [controls.body, "body"],
      [controls.crisp, "crisp"],
      [controls.frequency, "frequency"],
      [controls.decay, "decay"],
      [controls.mix, "mix"],
      [controls.partials, "partials"],
      [controls.output, "outputDb"]
    ];
    for (const [control, key] of rangeBindings) {
      control.addEventListener("input", (event) => {
        state[key] = Number(event.target.value);
        markCustomized();
        updateUI();
      });
    }

    $("play-button").addEventListener("click", () => playSound());
    $("play-head-button").addEventListener("click", () => playSound(state, "head"));
    $("play-body-button").addEventListener("click", () => playSound(state, "body"));
    $("play-tail-button").addEventListener("click", () => playSound(state, "tail"));
    $("stop-button").addEventListener("click", () => stopSound());
    document.querySelectorAll("[data-preview-segment]").forEach((button) => {
      button.addEventListener("click", () => playSound(state, button.dataset.previewSegment));
    });
    $("reset-button").addEventListener("click", () => {
      selectEffect(state.effectId, false);
      showToast("已恢复当前音效的原始参数");
    });
    document.querySelectorAll("[data-save-slot]").forEach((button) => {
      button.addEventListener("click", () => saveSlot(button.dataset.saveSlot));
    });
    document.querySelectorAll("[data-play-slot]").forEach((button) => {
      button.addEventListener("click", () => {
        const slot = slots[button.dataset.playSlot];
        if (slot) playSound(slot);
      });
    });

    $("export-wav-button").addEventListener("click", exportWav);
    $("export-json-button").addEventListener("click", exportJson);

    const windBindings = [
      [$("wind-speed-control"), "rpm"],
      [$("wind-weight-control"), "weight"],
      [$("wind-air-control"), "air"],
      [$("wind-blade-control"), "bladePulse"],
      [$("wind-resonance-control"), "resonance"],
      [$("wind-metal-tone-control"), "metalBrightness"],
      [$("wind-metal-pitch-control"), "metalPitchSemitones"],
      [$("wind-coast-control"), "coastSeconds"]
    ];
    for (const [control, key] of windBindings) {
      control.addEventListener("input", (event) => {
        windState[key] = Number(event.target.value);
        windState = sanitizeWindState(windState);
        if (windPlaying && key === "rpm") windAudibleRpm = windState.rpm;
        updateWindReadout();
        if (windPlaying) {
          updateWindEngine(windAudibleRpm, 1);
          setStatus(
            `陀螺风声 · ${Math.round(windAudibleRpm).toLocaleString("zh-CN")} RPM`,
            "ready");
        }
        else if (["rpm", "metalBrightness", "metalPitchSemitones"].includes(key)) startWind();
      });
    }
    $("wind-metal-material-control").addEventListener("change", (event) => {
      windState.metalMaterialId = event.target.value;
      windState = sanitizeWindState(windState);
      updateWindReadout();
      if (windPlaying) updateWindEngine(windAudibleRpm, 1);
    });
    document.querySelectorAll("[data-wind-pitch]").forEach((button) => {
      button.addEventListener("click", () => {
        windState.metalPitchSemitones = Number(button.dataset.windPitch);
        windState = sanitizeWindState(windState);
        updateWindReadout();
        if (windPlaying) updateWindEngine(windAudibleRpm, 1);
        else startWind();
      });
    });
    document.querySelectorAll("[data-wind-rpm]").forEach((button) => {
      button.addEventListener("click", () => {
        windState.rpm = Number(button.dataset.windRpm);
        $("wind-speed-control").value = windState.rpm;
        updateWindReadout();
        startWind();
      });
    });
    $("wind-start-button").addEventListener("click", startWind);
    $("wind-stop-button").addEventListener("click", () => stopWind(true, true));
  }

  function resizeCanvas(canvas) {
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    const rect = canvas.getBoundingClientRect();
    const width = Math.max(320, Math.round(rect.width * ratio));
    const height = Math.max(140, Math.round(rect.height * ratio));
    if (canvas.width !== width || canvas.height !== height) {
      canvas.width = width;
      canvas.height = height;
    }
    return { width, height, ratio };
  }

  function drawCanvasBase(context, width, height) {
    context.clearRect(0, 0, width, height);
    const ratio = Math.min(window.devicePixelRatio || 1, 2);
    const totalDuration = resolveFullDuration(state);
    let headFraction = clamp((state.clickLength / 1000) / totalDuration, 0.05, 0.22);
    const bodyDuration = Math.min(0.42, Math.max(0.14, state.decay * 0.32));
    let bodyFraction = clamp(headFraction + bodyDuration / totalDuration, headFraction + 0.12, 0.68);
    if (state.referenceClipEnabled) {
      headFraction = state.referenceClipHeadEnd / state.referenceClipDuration;
      bodyFraction = state.referenceClipBodyEnd / state.referenceClipDuration;
    } else if (state.sequenceEnabled) {
      const lastOffset = state.sequenceOffsets[state.sequenceOffsets.length - 1] || 0;
      const firstInterval = state.sequenceOffsets[1] || state.clickLength / 1000;
      const finalInterval = lastOffset - (state.sequenceOffsets[state.sequenceOffsets.length - 2] || 0);
      headFraction = clamp(firstInterval / totalDuration, 0.05, 0.18);
      bodyFraction = clamp((lastOffset - finalInterval * 0.45) / totalDuration, headFraction + 0.20, 0.90);
    }
    const headX = width * headFraction;
    const bodyX = width * bodyFraction;

    context.fillStyle = "rgba(215, 184, 137, 0.045)";
    context.fillRect(0, 0, headX, height);
    context.fillStyle = "rgba(133, 215, 206, 0.038)";
    context.fillRect(headX, 0, bodyX - headX, height);
    context.fillStyle = "rgba(113, 139, 145, 0.022)";
    context.fillRect(bodyX, 0, width - bodyX, height);

    context.save();
    context.setLineDash([4 * ratio, 5 * ratio]);
    context.strokeStyle = "rgba(220, 232, 238, 0.13)";
    context.beginPath();
    context.moveTo(headX, 0);
    context.lineTo(headX, height);
    context.moveTo(bodyX, 0);
    context.lineTo(bodyX, height);
    context.stroke();
    context.restore();

    context.font = `${10 * ratio}px ui-sans-serif, -apple-system, sans-serif`;
    context.fillStyle = "rgba(215, 184, 137, 0.78)";
    context.fillText(state.referenceClipEnabled ? "按入" : (state.sequenceEnabled ? "首击" : (state.reboundEnabled ? "按压" : "首段")), 7 * ratio, 16 * ratio);
    context.fillStyle = "rgba(133, 215, 206, 0.78)";
    context.fillText(state.referenceClipEnabled ? "翻转" : (state.sequenceEnabled ? "滚珠" : (state.reboundEnabled ? "机构" : "主段")), Math.max(headX + 7 * ratio, width * 0.20), 16 * ratio);
    context.fillStyle = "rgba(158, 176, 181, 0.72)";
    context.fillText(state.referenceClipEnabled ? "触底" : (state.sequenceEnabled ? "锁止" : (state.reboundEnabled ? "回弹" : "尾段")), Math.max(bodyX + 7 * ratio, width * 0.62), 16 * ratio);

    context.strokeStyle = "rgba(220, 232, 238, 0.07)";
    context.lineWidth = 1;
    context.beginPath();
    context.moveTo(0, height / 2);
    context.lineTo(width, height / 2);
    context.stroke();
    for (let index = 1; index < 5; index += 1) {
      const x = (width / 5) * index;
      context.beginPath();
      context.moveTo(x, 0);
      context.lineTo(x, height);
      context.stroke();
    }
  }

  function drawEnvelope() {
    const canvas = $("scope");
    if (!canvas) return;
    const { width, height, ratio } = resizeCanvas(canvas);
    const context = canvas.getContext("2d");
    drawCanvasBase(context, width, height);

    const center = height / 2;
    const tailMix = state.resonanceId === "none" ? 0 : state.mix / 100;
    const decayRate = 5.5 / Math.max(0.15, state.decay);
    const visualCycles = 22 + (state.frequency / 1600) * 56;
    const totalDuration = resolveFullDuration(state);
    const clickWidth = Math.min(width * 0.22, Math.max(4, width * (state.clickLength / 1000) / totalDuration));
    const clickFraction = clickWidth / width;
    const sequenceEntries = resolveSequenceEntries(state, "full");
    const sequenceTailStart = sequenceEntries.length
      ? sequenceEntries[sequenceEntries.length - 1].offset / totalDuration
      : 0;
    const referencePulseOffsets = [0.119, 0.171, 0.247, 0.322, 0.436, 0.517, 0.616, 0.703,
      0.793, 0.888, 0.975, 1.054, 1.167, 1.251, 1.344, 1.436];
    const reboundSettings = resolveReboundSettings(state);
    const reboundStart = state.decay / totalDuration;
    const reboundWidth = Math.max(0.015, (reboundSettings.clickLength / 1000) / totalDuration);
    const gradient = context.createLinearGradient(0, 0, width, 0);
    gradient.addColorStop(0, "rgba(228, 247, 244, 0.98)");
    gradient.addColorStop(0.24, "rgba(133, 215, 206, 0.88)");
    gradient.addColorStop(1, "rgba(133, 215, 206, 0.04)");

    context.strokeStyle = gradient;
    context.lineWidth = Math.max(1.2, ratio);
    context.beginPath();
    for (let x = 0; x < width; x += 1) {
      const progress = x / width;
      let clickEnvelope = progress < clickFraction
        ? Math.sin((progress / clickFraction) * Math.PI) * 0.88
        : 0;
      if (state.sequenceEnabled) {
        clickEnvelope = sequenceEntries.reduce((sum, entry) => {
          const localProgress = (progress - entry.offset / totalDuration) / clickFraction;
          if (localProgress < 0 || localProgress > 1) return sum;
          return sum + Math.sin(localProgress * Math.PI) * entry.gain;
        }, 0);
        clickEnvelope = Math.min(1.15, clickEnvelope);
      }
      if (state.referenceClipEnabled) {
        clickEnvelope = referencePulseOffsets.reduce((sum, offset, index) => {
          const distance = Math.abs(progress * totalDuration - offset);
          const strength = 0.48 + (index / referencePulseOffsets.length) * 0.32;
          return sum + Math.exp(-distance * 58) * strength;
        }, 0);
        clickEnvelope = Math.min(1.08, clickEnvelope);
      }
      const tailProgress = state.sequenceEnabled ? Math.max(0, progress - sequenceTailStart) : progress;
      const tailEnvelope = tailMix
        * (state.sequenceEnabled && progress < sequenceTailStart ? 0 : 1)
        * Math.exp(-tailProgress * decayRate);
      const oscillation = Math.sin(progress * visualCycles * Math.PI * 2);
      const reboundProgress = (progress - reboundStart) / reboundWidth;
      const reboundEnvelope = state.reboundEnabled && reboundProgress >= 0 && reboundProgress <= 1
        ? Math.sin(reboundProgress * Math.PI) * state.reboundGain
        : 0;
      const reboundOscillation = Math.sin(progress * visualCycles * Math.PI * 2 * 1.24 + 0.6);
      const y = center + (
        clickEnvelope
        + tailEnvelope * oscillation
        + reboundEnvelope * reboundOscillation
      ) * height * 0.36;
      if (x === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    }
    context.stroke();

    context.fillStyle = "rgba(186, 194, 200, 0.62)";
    context.font = `${11 * ratio}px ui-sans-serif, -apple-system, sans-serif`;
    context.fillText("0", 4 * ratio, height - 8 * ratio);
    context.textAlign = "right";
    context.fillText(`${resolveFullDuration(state).toFixed(2)} s`, width - 4 * ratio, height - 8 * ratio);
    context.textAlign = "left";
  }

  function drawLiveWaveform() {
    if (!analyser) return;
    const canvas = $("scope");
    const samples = new Uint8Array(analyser.fftSize);

    const frame = () => {
      const { width, height, ratio } = resizeCanvas(canvas);
      const context = canvas.getContext("2d");
      analyser.getByteTimeDomainData(samples);
      drawCanvasBase(context, width, height);
      const gradient = context.createLinearGradient(0, 0, width, 0);
      gradient.addColorStop(0, "rgba(228, 247, 244, 0.98)");
      gradient.addColorStop(1, "rgba(133, 215, 206, 0.58)");
      context.strokeStyle = gradient;
      context.lineWidth = Math.max(1.25, ratio);
      context.beginPath();
      for (let index = 0; index < samples.length; index += 1) {
        const x = (index / (samples.length - 1)) * width;
        const y = (samples[index] / 255) * height;
        if (index === 0) context.moveTo(x, y);
        else context.lineTo(x, y);
      }
      context.stroke();
      animationFrame = window.requestAnimationFrame(frame);
    };
    window.cancelAnimationFrame(animationFrame);
    frame();
  }

  function audioBufferToWav(buffer) {
    const channels = Math.min(2, buffer.numberOfChannels);
    const sampleRate = buffer.sampleRate;
    const frameCount = buffer.length;
    const bytesPerSample = 2;
    const blockAlign = channels * bytesPerSample;
    const arrayBuffer = new ArrayBuffer(44 + frameCount * blockAlign);
    const view = new DataView(arrayBuffer);

    const writeText = (offset, text) => {
      for (let index = 0; index < text.length; index += 1) view.setUint8(offset + index, text.charCodeAt(index));
    };

    writeText(0, "RIFF");
    view.setUint32(4, 36 + frameCount * blockAlign, true);
    writeText(8, "WAVE");
    writeText(12, "fmt ");
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, channels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * blockAlign, true);
    view.setUint16(32, blockAlign, true);
    view.setUint16(34, 16, true);
    writeText(36, "data");
    view.setUint32(40, frameCount * blockAlign, true);

    const data = [];
    for (let channel = 0; channel < channels; channel += 1) data.push(buffer.getChannelData(channel));
    let offset = 44;
    for (let frame = 0; frame < frameCount; frame += 1) {
      for (let channel = 0; channel < channels; channel += 1) {
        const sample = clamp(data[channel][frame], -1, 1);
        view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7fff, true);
        offset += 2;
      }
    }
    return arrayBuffer;
  }

  function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = filename;
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
    window.setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  async function exportWav() {
    try {
      setStatus("正在渲染 WAV…");
      await ensureAudioContext();
      await preloadForSettings(state, "full");
      const duration = resolveFullDuration(state) + 0.16;
      const sampleRate = 48000;
      const offline = new OfflineAudioContext(2, Math.ceil(duration * sampleRate), sampleRate);
      buildSound(offline, offline.destination, state, 0.01, "full", new Set());
      const rendered = await offline.startRendering();
      const wav = audioBufferToWav(rendered);
      const filename = state.purifiedClickEnabled
        ? "can-coin-pure-press-rebound.wav"
        : state.referenceClipEnabled
        ? "can-coin-reference-press.wav"
        : (state.sequenceEnabled
          ? `can-coin-reference-${state.sequenceOffsets.length}-contacts.wav`
          : (state.reboundEnabled
          ? `press-rebound-${Math.round(state.decay * 1000)}ms.wav`
          : `alloy-click-${Math.round(state.frequency)}hz-${state.decay.toFixed(2)}s.wav`));
      downloadBlob(new Blob([wav], { type: "audio/wav" }), filename);
      setStatus("WAV 已导出", "ready");
      showToast(`已导出 ${filename}`);
    } catch (error) {
      console.error(error);
      setStatus(error.message || "WAV 导出失败", "error");
    }
  }

  function exportJson() {
    const payload = {
      format: "alloy-tone-lab-preset",
      version: 1,
      exportedAt: new Date().toISOString(),
      status: "research-only-not-integrated",
      effect: getSelectedEffect().name,
      customized: state.customized,
      source: getClickSource().name,
      resonance: getResonanceSource().name,
      parameters: cloneSettings(state)
    };
    const filename = state.purifiedClickEnabled
      ? "can-coin-pure-press-rebound-preset.json"
      : state.referenceClipEnabled
      ? "can-coin-reference-press-preset.json"
      : (state.sequenceEnabled
        ? `can-coin-reference-${state.sequenceOffsets.length}-contacts-preset.json`
        : (state.reboundEnabled
        ? `press-rebound-${Math.round(state.decay * 1000)}ms-preset.json`
        : `alloy-click-${Math.round(state.frequency)}hz-preset.json`));
    downloadBlob(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }), filename);
    setStatus("参数 JSON 已导出", "ready");
    showToast(`已导出 ${filename}`);
  }

  function init() {
    configureControls();
    updateUI();
    updateWindReadout();
    windVisualFrame = window.requestAnimationFrame(animateWindRotor);
    window.addEventListener("resize", drawEnvelope);
    window.addEventListener("keydown", (event) => {
      const interactive = ["INPUT", "SELECT", "TEXTAREA", "BUTTON"].includes(document.activeElement?.tagName);
      if (event.code === "Space" && !interactive) {
        event.preventDefault();
        playSound();
      }
      if (event.code === "Escape") {
        stopSound(false);
        stopWind(true, false);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", init);
})();
