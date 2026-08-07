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
    category: "product"
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
    })
  ];

  const STORAGE_KEY = "alloy-tone-lab-state-v2";
  const SLOT_KEY = "alloy-tone-lab-ab-v1";
  const bufferCache = new Map();
  const controls = {};
  const activeNodes = new Set();
  let state = loadState();
  let slots = loadSlots();
  let audioContext = null;
  let analyser = null;
  let animationFrame = 0;
  let playbackTimer = 0;
  let toastTimer = 0;

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
    return next;
  }

  function loadState() {
    try {
      return sanitizeState(JSON.parse(localStorage.getItem(STORAGE_KEY)));
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
      audioContext = new Context({ sampleRate: 48000 });
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
    const includesHead = mode === "full" || mode === "head";
    const includesResonance = mode === "full" || mode === "body" || mode === "tail";
    if (includesHead) jobs.push(loadBuffer(getClickSource(settings.sourceId)));
    const resonance = getResonanceSource(settings.resonanceId);
    if (includesResonance && resonance.type === "sample") jobs.push(loadBuffer(resonance));
    await Promise.all(jobs);
  }

  function trackNode(node, targetSet) {
    targetSet?.add(node);
    return node;
  }

  function createClickLayer(context, output, settings, startAt, targetSet) {
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
    const bodyGain = -4 + settings.body * 0.13;
    const crispGain = -6 + settings.crisp * 0.16;

    source.buffer = buffer;
    source.playbackRate.setValueAtTime(rate, startAt);

    highPass.type = "highpass";
    highPass.frequency.value = 85;
    highPass.Q.value = 0.55;

    bodyShelf.type = "lowshelf";
    bodyShelf.frequency.value = 360;
    bodyShelf.gain.value = bodyGain;

    bodyFocus.type = "peaking";
    bodyFocus.frequency.value = 690;
    bodyFocus.Q.value = 0.85;
    bodyFocus.gain.value = bodyGain * 0.34;

    crispShelf.type = "highshelf";
    crispShelf.frequency.value = 4200;
    crispShelf.gain.value = crispGain;

    compressor.threshold.value = -18;
    compressor.knee.value = 6;
    compressor.ratio.value = 2.2;
    compressor.attack.value = 0.0015;
    compressor.release.value = 0.065;

    clickGain.gain.setValueAtTime(0.0001, startAt);
    clickGain.gain.linearRampToValueAtTime(0.94, startAt + 0.002);
    clickGain.gain.setValueAtTime(0.94, startAt + Math.max(0.004, gateDuration - 0.012));
    clickGain.gain.exponentialRampToValueAtTime(0.0001, startAt + gateDuration);

    source.connect(highPass);
    highPass.connect(bodyShelf);
    bodyShelf.connect(bodyFocus);
    bodyFocus.connect(crispShelf);
    crispShelf.connect(compressor);
    compressor.connect(clickGain);
    clickGain.connect(output);

    source.start(startAt);
    source.stop(startAt + gateDuration + 0.02);
    return gateDuration;
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
    output.connect(destination);

    if (mode === "full" || mode === "head") {
      duration = Math.max(duration, createClickLayer(context, output, settings, startAt, targetSet));
    }
    if ((mode === "full" || mode === "body" || mode === "tail") && resonance.type === "synthetic") {
      duration = Math.max(duration, createSyntheticTail(context, output, segmentSettings, startAt, targetSet));
    }
    if ((mode === "full" || mode === "body" || mode === "tail") && resonance.type === "sample") {
      duration = Math.max(duration, createRecordedTail(context, output, segmentSettings, resonance, startAt, targetSet));
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
      if ((mode === "body" || mode === "tail") && getResonanceSource(safeSettings.resonanceId).type === "none") {
        setStatus("主段和尾段当前已关闭", "ready");
        showToast("请先在“主段音色”里选择一种合金音色。当前声音只有首段。");
        return;
      }
      await ensureAudioContext();
      await preloadForSettings(safeSettings, mode);
      stopSound(false);
      const startAt = audioContext.currentTime + 0.025;
      const duration = buildSound(audioContext, analyser, safeSettings, startAt, mode, activeNodes);
      const statusByMode = {
        full: "正在播放完整声音",
        head: "正在播放首段 · 第一下 Click",
        body: "正在播放主段 · 合金鸣响",
        tail: "正在播放尾段 · 自然消散"
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
    $("head-segment-summary").textContent = `${Math.round(state.clickLength)} ms · ${pitchPrefix}${state.pitch.toFixed(1)} 半音`;
    $("body-segment-summary").textContent = `${Math.round(state.frequency)} Hz (${frequencyToNote(state.frequency)}) · ${Math.round(state.mix)}% 响度`;
    $("tail-segment-summary").textContent = `${state.decay.toFixed(2)} 秒 · 无第二下`;

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
    const totalDuration = Math.max(0.12, state.decay, state.clickLength / 1000);
    const headFraction = clamp((state.clickLength / 1000) / totalDuration, 0.05, 0.22);
    const bodyDuration = Math.min(0.42, Math.max(0.14, state.decay * 0.32));
    const bodyFraction = clamp(headFraction + bodyDuration / totalDuration, headFraction + 0.12, 0.68);
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
    context.fillText("首段", 7 * ratio, 16 * ratio);
    context.fillStyle = "rgba(133, 215, 206, 0.78)";
    context.fillText("主段", Math.max(headX + 7 * ratio, width * 0.20), 16 * ratio);
    context.fillStyle = "rgba(158, 176, 181, 0.72)";
    context.fillText("尾段", Math.max(bodyX + 7 * ratio, width * 0.62), 16 * ratio);

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
    const totalDuration = Math.max(0.12, state.decay, state.clickLength / 1000);
    const clickWidth = Math.min(width * 0.22, Math.max(4, width * (state.clickLength / 1000) / totalDuration));
    const gradient = context.createLinearGradient(0, 0, width, 0);
    gradient.addColorStop(0, "rgba(228, 247, 244, 0.98)");
    gradient.addColorStop(0.24, "rgba(133, 215, 206, 0.88)");
    gradient.addColorStop(1, "rgba(133, 215, 206, 0.04)");

    context.strokeStyle = gradient;
    context.lineWidth = Math.max(1.2, ratio);
    context.beginPath();
    for (let x = 0; x < width; x += 1) {
      const progress = x / width;
      const clickEnvelope = progress < clickWidth / width
        ? Math.sin((progress / (clickWidth / width)) * Math.PI) * 0.88
        : 0;
      const tailEnvelope = tailMix * Math.exp(-progress * decayRate);
      const oscillation = Math.sin(progress * visualCycles * Math.PI * 2);
      const y = center + (clickEnvelope + tailEnvelope * oscillation) * height * 0.36;
      if (x === 0) context.moveTo(x, y);
      else context.lineTo(x, y);
    }
    context.stroke();

    context.fillStyle = "rgba(186, 194, 200, 0.62)";
    context.font = `${11 * ratio}px ui-sans-serif, -apple-system, sans-serif`;
    context.fillText("0", 4 * ratio, height - 8 * ratio);
    context.textAlign = "right";
    context.fillText(`${Math.max(state.decay, state.clickLength / 1000).toFixed(2)} s`, width - 4 * ratio, height - 8 * ratio);
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
      const duration = Math.max(state.decay, state.clickLength / 1000) + 0.16;
      const sampleRate = 48000;
      const offline = new OfflineAudioContext(2, Math.ceil(duration * sampleRate), sampleRate);
      buildSound(offline, offline.destination, state, 0.01, "full", new Set());
      const rendered = await offline.startRendering();
      const wav = audioBufferToWav(rendered);
      const filename = `alloy-click-${Math.round(state.frequency)}hz-${state.decay.toFixed(2)}s.wav`;
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
    const filename = `alloy-click-${Math.round(state.frequency)}hz-preset.json`;
    downloadBlob(new Blob([JSON.stringify(payload, null, 2)], { type: "application/json" }), filename);
    setStatus("参数 JSON 已导出", "ready");
    showToast(`已导出 ${filename}`);
  }

  function init() {
    configureControls();
    updateUI();
    window.addEventListener("resize", drawEnvelope);
    window.addEventListener("keydown", (event) => {
      const interactive = ["INPUT", "SELECT", "TEXTAREA", "BUTTON"].includes(document.activeElement?.tagName);
      if (event.code === "Space" && !interactive) {
        event.preventDefault();
        playSound();
      }
      if (event.code === "Escape") stopSound();
    });
  }

  document.addEventListener("DOMContentLoaded", init);
})();
