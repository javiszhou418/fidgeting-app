import fs from "node:fs";
import path from "node:path";

export const RETENTION_FILE = "unity/FidgetingApp/ArtSource/ModelPipeline/review-image-retention.json";
export const REMOVED_REVIEW_IMAGE = "removed-older-review-batch";
const cache = new Map();
const imageExtension = /\.(png|jpe?g|webp|gif|bmp|tiff?)$/i;

export function isReviewImagePath(relativePath) {
  if (typeof relativePath !== "string" || !imageExtension.test(relativePath)) return false;
  if (relativePath.includes("\\") || relativePath.split("/").some((part) => part === ".." || part === ".")) return false;
  if (relativePath.includes("/Assets/") || relativePath.includes("/Docs/") || relativePath.includes("/package/") || relativePath.includes("/source/")) return false;
  return /^unity\/FidgetingApp\/ArtSource\/ModelPipeline\/[a-z0-9-]+\/evidence\/(?:0[4-9]|1[0-2])-[^/]+\//.test(relativePath)
    || /^Artifacts\/(?:TriSpinnerSlab|PackTearNativeCandidate|LibraryDetailConsistency|EDC|ModelProvenanceExplorer)\//.test(relativePath)
    || /^unity\/FidgetingApp\/Artifacts\/(?:TriSpinnerSlab|PackTearNativeCandidate|LibraryDetailConsistency|EDC|ModelProvenanceExplorer)\//.test(relativePath);
}

export function readReviewImageRetention(root) {
  const file = path.join(root, RETENTION_FILE);
  if (!fs.existsSync(file)) return new Map();
  const stat = fs.statSync(file);
  const key = `${stat.mtimeMs}:${stat.size}`;
  if (cache.get(file)?.key === key) return cache.get(file).index;
  const document = JSON.parse(fs.readFileSync(file, "utf8"));
  if (document.schemaVersion !== 1 || !Array.isArray(document.removedImages)) throw new Error("Invalid review-image retention index.");
  const index = new Map();
  for (const entry of document.removedImages) {
    if (!isReviewImagePath(entry.path) || !/^[a-f0-9]{64}$/.test(entry.sha256 || "") || index.has(entry.path)) {
      throw new Error(`Invalid or duplicate removed review image: ${entry.path}`);
    }
    index.set(entry.path, { ...entry, removedAt: document.removedAt });
  }
  cache.set(file, { key, index });
  return index;
}

// Decorate records for display without changing their original path or reviewed hash.
// The append-only history files remain untouched.
export function markRemovedReviewImages(value, index) {
  if (Array.isArray(value)) {
    for (const item of value) markRemovedReviewImages(item, index);
  } else if (value && typeof value === "object") {
    const entry = typeof value.path === "string" ? index.get(value.path) : null;
    if (entry) {
      value.exists = false;
      value.availability = {
        status: REMOVED_REVIEW_IMAGE,
        removedAt: entry.removedAt,
        originalSha256: entry.sha256,
        originalSizeBytes: entry.sizeBytes,
        notice: "旧批次验收图已移除；原审阅记录与哈希保留，未替换成新版图片。"
      };
    }
    for (const [key, item] of Object.entries(value)) {
      if (key !== "availability") markRemovedReviewImages(item, index);
    }
  }
  return value;
}

export function removedReviewImageSvg(entry) {
  const escape = (value) => String(value).replace(/[&<>"']/g, (char) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&apos;" }[char]));
  return `<svg xmlns="http://www.w3.org/2000/svg" width="960" height="320" viewBox="0 0 960 320" role="img" aria-label="旧批次验收图已移除"><rect width="960" height="320" fill="#f2f1ee"/><g fill="#383934" font-family="sans-serif" text-anchor="middle"><text x="480" y="112" font-size="28">旧批次验收图已移除</text><text x="480" y="162" font-size="18">原审阅记录与哈希保留，未替换成新版图片</text><text x="480" y="210" font-size="16">${escape(entry.modelId || "模型验收")}</text></g></svg>`;
}
