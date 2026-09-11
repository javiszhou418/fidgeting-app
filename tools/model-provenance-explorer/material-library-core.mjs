import fs from "node:fs";
import path from "node:path";
import { PipelineError, repoRoot, resolveRepoPath, sha256File } from "./pipeline-core.mjs";

export const MATERIAL_LIBRARY_PATH = "unity/FidgetingApp/ArtSource/MaterialLibrary/materials.json";
export const MATERIAL_STATUSES = Object.freeze(["approved-gate07", "contract-locked", "shipping-unity", "stale", "proposed"]);
export const BLENDER_AUTHORITIES = Object.freeze(["blender-lookdev", "derived-from-unity", "contract-locked"]);
const HEX_PATTERN = /^#[0-9A-F]{6}$/;
const ID_PATTERN = /^[a-z0-9][a-z0-9-]*$/;

export function srgbToLinear(channel) {
  return channel <= 0.04045 ? channel / 12.92 : ((channel + 0.055) / 1.055) ** 2.4;
}

export function linearToSrgb(channel) {
  const clamped = Math.min(1, Math.max(0, channel));
  return clamped <= 0.0031308 ? clamped * 12.92 : 1.055 * clamped ** (1 / 2.4) - 0.055;
}

export function hexFromSrgb(rgb) {
  return `#${rgb.map((value) => Math.round(Math.min(1, Math.max(0, value)) * 255).toString(16).padStart(2, "0")).join("")}`.toUpperCase();
}

export function hexFromLinear(rgb) {
  return hexFromSrgb(rgb.map(linearToSrgb));
}

export function srgbFromHex(hex) {
  return [1, 3, 5].map((index) => Number.parseInt(hex.slice(index, index + 2), 16) / 255);
}

export function loadMaterialLibrary(libraryPath = MATERIAL_LIBRARY_PATH) {
  const absolute = resolveRepoPath(libraryPath);
  if (!fs.existsSync(absolute)) throw new PipelineError(`Material library missing: ${libraryPath}`, 500);
  try {
    return JSON.parse(fs.readFileSync(absolute, "utf8"));
  } catch (error) {
    throw new PipelineError(`Material library is not valid JSON: ${error.message}`, 500);
  }
}

function isRgb(value) {
  return Array.isArray(value) && value.length === 3 && value.every((channel) => Number.isFinite(channel) && channel >= 0 && channel <= 1);
}

function isUnit(value) {
  return Number.isFinite(value) && value >= 0 && value <= 1;
}

function close(a, b, tolerance) {
  return Math.abs(a - b) <= tolerance;
}

export function validateMaterialLibrary(library, { checkFiles = true } = {}) {
  const errors = [];
  const push = (message) => errors.push(message);
  if (!library || typeof library !== "object") return ["Library must be an object."];
  if (library.schemaVersion !== 1) push("schemaVersion must be 1.");
  if (!Array.isArray(library.families) || !library.families.length) push("families must be a non-empty array.");
  const familyIds = new Set((library.families || []).map((family) => family.id));
  if (!Array.isArray(library.materials) || !library.materials.length) push("materials must be a non-empty array.");
  const ids = new Set();
  const unityNames = new Set();
  for (const material of library.materials || []) {
    const label = material?.id || "<missing id>";
    if (!ID_PATTERN.test(String(material?.id || ""))) push(`${label}: id must match ${ID_PATTERN}.`);
    if (ids.has(material.id)) push(`${label}: duplicate id.`);
    ids.add(material.id);
    if (!material.name?.zh || !material.name?.en) push(`${label}: name.zh and name.en are required.`);
    if (!familyIds.has(material.family)) push(`${label}: unknown family "${material.family}".`);
    if (!MATERIAL_STATUSES.includes(material.status)) push(`${label}: status must be one of ${MATERIAL_STATUSES.join(", ")}.`);
    if (typeof material.description !== "string" || material.description.length < 20) push(`${label}: description must be at least 20 characters.`);
    if (!Array.isArray(material.imageGen?.phrases) || material.imageGen.phrases.length < 2) push(`${label}: imageGen.phrases needs at least 2 entries.`);
    if (!Array.isArray(material.imageGen?.avoid) || material.imageGen.avoid.length < 1) push(`${label}: imageGen.avoid needs at least 1 entry.`);
    const blender = material.blender;
    if (!blender || typeof blender !== "object") {
      push(`${label}: blender block is required.`);
    } else {
      if (!BLENDER_AUTHORITIES.includes(blender.authority)) push(`${label}: blender.authority must be one of ${BLENDER_AUTHORITIES.join(", ")}.`);
      if (!isRgb(blender.baseColor)) push(`${label}: blender.baseColor must be three 0-1 linear channels.`);
      if (!isUnit(blender.metallic)) push(`${label}: blender.metallic must be 0-1.`);
      if (!isUnit(blender.roughness)) push(`${label}: blender.roughness must be 0-1.`);
      if (blender.anisotropic !== undefined && !isUnit(blender.anisotropic)) push(`${label}: blender.anisotropic must be 0-1.`);
      if (blender.authority === "blender-lookdev" && !blender.materialName) push(`${label}: blender-lookdev entries must name the Blender material.`);
      if (blender.authority !== "blender-lookdev" && !blender.derivation) push(`${label}: derived/contract entries must document the derivation.`);
    }
    const unity = material.unity;
    if (unity === null || unity === undefined) {
      if (material.status === "shipping-unity" || material.status === "contract-locked") push(`${label}: ${material.status} requires a unity block.`);
    } else if (typeof unity !== "object") {
      push(`${label}: unity must be an object or null.`);
    } else {
      if (!/^M_[A-Za-z0-9_]+$/.test(String(unity.material || ""))) push(`${label}: unity.material must look like M_Name.`);
      if (unityNames.has(unity.material)) push(`${label}: unity material ${unity.material} is claimed twice.`);
      unityNames.add(unity.material);
      if (!HEX_PATTERN.test(String(unity.baseColorHex || ""))) push(`${label}: unity.baseColorHex must be #RRGGBB uppercase.`);
      if (!isUnit(unity.metallic)) push(`${label}: unity.metallic must be 0-1.`);
      if (!isUnit(unity.smoothness)) push(`${label}: unity.smoothness must be 0-1.`);
      if (typeof unity.specularHighlights !== "boolean" || typeof unity.environmentReflections !== "boolean") push(`${label}: unity.specularHighlights/environmentReflections must be booleans.`);
      if (unity.baseColorSrgb && HEX_PATTERN.test(unity.baseColorHex) && hexFromSrgb(unity.baseColorSrgb) !== unity.baseColorHex) push(`${label}: unity.baseColorSrgb does not match baseColorHex.`);
      if (blender?.authority === "derived-from-unity" && isRgb(blender.baseColor) && HEX_PATTERN.test(unity.baseColorHex)) {
        const expected = srgbFromHex(unity.baseColorHex).map(srgbToLinear);
        if (!expected.every((channel, index) => close(channel, blender.baseColor[index], 0.002))) push(`${label}: derived blender.baseColor must equal sRGB→linear(unity.baseColorHex).`);
        if (!close(blender.roughness, 1 - unity.smoothness, 0.002)) push(`${label}: derived blender.roughness must equal 1 − unity.smoothness.`);
        if (!close(blender.metallic, unity.metallic, 0.002)) push(`${label}: derived blender.metallic must equal unity.metallic.`);
      }
      if (checkFiles && unity.path) {
        try {
          if (!fs.existsSync(resolveRepoPath(unity.path))) push(`${label}: unity.path does not exist: ${unity.path}`);
        } catch (error) {
          push(`${label}: ${error.message}`);
        }
      }
    }
    if (!Array.isArray(material.usedBy) || !material.usedBy.length) push(`${label}: usedBy must list at least one model.`);
    if (!Array.isArray(material.sources) || !material.sources.length) push(`${label}: sources must list at least one repository path.`);
    for (const source of material.sources || []) {
      if (!source?.path) { push(`${label}: every source needs a path.`); continue; }
      if (checkFiles) {
        try {
          if (!fs.existsSync(resolveRepoPath(source.path))) push(`${label}: source path does not exist: ${source.path}`);
        } catch (error) {
          push(`${label}: ${error.message}`);
        }
      }
    }
    if (material.thumbnail) {
      if (!material.thumbnail.path || !/^[0-9a-f]{64}$/.test(String(material.thumbnail.sha256 || ""))) push(`${label}: thumbnail needs path and sha256.`);
      else if (checkFiles) {
        const absolute = resolveRepoPath(material.thumbnail.path);
        if (!fs.existsSync(absolute)) push(`${label}: thumbnail missing on disk: ${material.thumbnail.path}`);
        else if (sha256File(absolute) !== material.thumbnail.sha256) push(`${label}: thumbnail sha256 drifted: ${material.thumbnail.path}`);
      }
    }
  }
  for (const pending of library.pendingEntries || []) {
    if (!pending.id || !pending.reason || !pending.source) push(`pendingEntries: ${pending.id || "<no id>"} needs id, reason, source.`);
    if (ids.has(pending.id)) push(`pendingEntries: ${pending.id} is already a material.`);
  }
  return errors;
}

export function deriveMaterialLibrary(library) {
  const statusLabels = library.statusLabels || {};
  const families = (library.families || []).map((family) => ({ ...family }));
  const materials = (library.materials || []).map((material) => {
    const linear = material.blender?.baseColor || [0, 0, 0];
    return {
      ...material,
      swatchHex: hexFromLinear(linear),
      statusLabel: statusLabels[material.status] || material.status,
      familyLabel: families.find((family) => family.id === material.family)?.label || material.family,
      thumbnailUrl: material.thumbnail?.path ? `/repo/${material.thumbnail.path}` : null,
      hasThumbnail: Boolean(material.thumbnail?.path)
    };
  });
  return {
    ...library,
    families,
    materials,
    derived: {
      count: materials.length,
      byStatus: Object.fromEntries(MATERIAL_STATUSES.map((status) => [status, materials.filter((material) => material.status === status).length])),
      thumbnailCount: materials.filter((material) => material.hasThumbnail).length
    }
  };
}

export function refreshThumbnailHashes(library, { thumbnailDirectory = library.thumbnailDirectory } = {}) {
  const updated = { ...library, materials: library.materials.map((material) => ({ ...material })) };
  const report = [];
  for (const material of updated.materials) {
    const relative = `${thumbnailDirectory}/${material.id}.png`;
    const absolute = resolveRepoPath(relative);
    if (fs.existsSync(absolute)) {
      material.thumbnail = { path: relative, sha256: sha256File(absolute) };
      report.push({ id: material.id, thumbnail: relative, state: "hashed" });
    } else {
      delete material.thumbnail;
      report.push({ id: material.id, thumbnail: relative, state: "missing" });
    }
  }
  return { library: updated, report };
}

function fmt(value) {
  return Number.isFinite(value) ? String(+value.toFixed(4)) : "—";
}

function rgb(values) {
  return Array.isArray(values) ? values.map(fmt).join(" / ") : "—";
}

export function renderMaterialsMarkdown(library) {
  const derived = deriveMaterialLibrary(library);
  const lines = [];
  lines.push(`# ${library.title || "材质库"}`);
  lines.push("");
  lines.push(`> 由 \`${library.authority}\` 生成，不要手改。运行 \`node tools/model-provenance-explorer/validate-material-library.mjs --write-md\` 重新生成。更新日期 ${library.updatedAt}。`);
  lines.push("");
  lines.push("## 用法");
  lines.push("");
  lines.push("- 每个材质一个稳定 id。Gate 07 lookdev 脚本、Unity 材质工厂和概念图提示词都引用同一个 id。");
  lines.push("- `blender.baseColor` 是线性 RGB，直接写进 Principled BSDF；`unity.baseColorHex` 是 sRGB，与 `.mat` 文件一致。两者不能互相复制。");
  lines.push("- `swatchHex` 只是给人看的颜色锚点，由 Blender 线性色换算而来，不是渲染目标。");
  lines.push(`- 概念图只能用 ${library.promptTarget?.imageGenModel || "图像生成模型"} 生成，属于 concept-only 分支，不能晋升为几何或材质真值。`);
  lines.push("");
  lines.push("## 固定风格块（概念图）");
  lines.push("");
  lines.push(library.promptTarget?.fixedStyleBlock || "—");
  lines.push("");
  lines.push("## 材质一览");
  lines.push("");
  for (const material of derived.materials) {
    const thumb = material.thumbnail?.path ? `![${material.id}](${path.posix.relative(path.posix.dirname(library.generatedMarkdown), material.thumbnail.path)}) ` : "";
    lines.push(`- ${thumb}\`${material.id}\` · ${material.name.zh} / ${material.name.en} · ${material.swatchHex} · ${material.statusLabel}`);
  }
  lines.push("");
  for (const material of derived.materials) {
    lines.push(`## ${material.name.zh} · ${material.name.en} (\`${material.id}\`, ${material.swatchHex})`);
    lines.push("");
    if (material.thumbnail?.path) {
      lines.push(`![${material.id} sphere](${path.posix.relative(path.posix.dirname(library.generatedMarkdown), material.thumbnail.path)})`);
      lines.push("");
    }
    lines.push(`状态：${material.statusLabel} · 家族：${material.familyLabel}`);
    lines.push("");
    lines.push(material.description);
    lines.push("");
    if (material.edgeBehavior) { lines.push(`**边缘 / 厚度行为**：${material.edgeBehavior}`); lines.push(""); }
    lines.push("**Blender（Principled BSDF，线性）**");
    lines.push("");
    lines.push(`- 权威：${material.blender.authority}${material.blender.materialName ? ` · ${material.blender.materialName}` : ""}`);
    lines.push(`- Base Color ${rgb(material.blender.baseColor)} · Metallic ${fmt(material.blender.metallic)} · Roughness ${fmt(material.blender.roughness)}`);
    if (material.blender.anisotropic !== undefined) lines.push(`- Anisotropic ${fmt(material.blender.anisotropic)} · Tangent ${material.blender.anisotropicTangent || "—"}`);
    if (material.blender.specularIorLevel !== undefined) lines.push(`- Specular IOR Level ${fmt(material.blender.specularIorLevel)}`);
    if (material.blender.bump) lines.push(`- Bump：${material.blender.bump.type}，strength ${fmt(material.blender.bump.strength)}，distance ${fmt(material.blender.bump.distance)}`);
    if (material.blender.derivation) lines.push(`- 推导：${material.blender.derivation}`);
    lines.push("");
    lines.push("**Unity（URP）**");
    lines.push("");
    if (material.unity) {
      lines.push(`- ${material.unity.material} · ${material.unity.shader}`);
      lines.push(`- Base Color ${material.unity.baseColorHex} (sRGB) · Metallic ${fmt(material.unity.metallic)} · Smoothness ${fmt(material.unity.smoothness)} · 高光 ${material.unity.specularHighlights ? "开" : "关"} · 环境反射 ${material.unity.environmentReflections ? "开" : "关"}`);
      if (material.unity.detail) lines.push(`- 细节：${material.unity.detail}`);
    } else {
      lines.push("- 无 Unity 对应材质。");
    }
    if (material.parityNote) { lines.push(""); lines.push(`**Blender/Unity 对齐**：${material.parityNote}`); }
    lines.push("");
    lines.push("**可用短语**");
    lines.push("");
    for (const phrase of material.imageGen.phrases) lines.push(`- ${phrase}`);
    lines.push("");
    lines.push("**避免**");
    lines.push("");
    for (const phrase of material.imageGen.avoid) lines.push(`- ${phrase}`);
    lines.push("");
    if (material.restrictions?.length) {
      lines.push("**限制**");
      lines.push("");
      for (const restriction of material.restrictions) lines.push(`- ${restriction}`);
      lines.push("");
    }
    lines.push("**使用位置**");
    lines.push("");
    for (const use of material.usedBy) lines.push(`- ${use.model}：${(use.parts || []).join("、") || "—"}`);
    lines.push("");
    lines.push("**来源**");
    lines.push("");
    for (const source of material.sources) lines.push(`- \`${source.path}\`${source.note ? ` — ${source.note}` : ""}`);
    lines.push("");
  }
  if (library.pendingEntries?.length) {
    lines.push("## 待收录");
    lines.push("");
    for (const pending of library.pendingEntries) lines.push(`- \`${pending.id}\`（${pending.model}）：${pending.reason} 来源 \`${pending.source}\`。`);
    lines.push("");
  }
  return `${lines.join("\n").trimEnd()}\n`;
}

export function writeMaterialsMarkdown(library) {
  const target = path.join(repoRoot, library.generatedMarkdown);
  const markdown = renderMaterialsMarkdown(library);
  fs.writeFileSync(target, markdown);
  return { path: library.generatedMarkdown, bytes: Buffer.byteLength(markdown) };
}

export function markdownInSync(library) {
  const target = path.join(repoRoot, library.generatedMarkdown);
  if (!fs.existsSync(target)) return false;
  return fs.readFileSync(target, "utf8") === renderMaterialsMarkdown(library);
}
