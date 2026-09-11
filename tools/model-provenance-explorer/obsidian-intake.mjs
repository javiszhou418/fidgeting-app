// Resolve an Obsidian note link to its markdown + local attachments so Gate 01 can archive them.
import fs from "node:fs";
import os from "node:os";
import path from "node:path";

const IMAGE_EXT = new Set([".png", ".jpg", ".jpeg", ".webp", ".gif", ".heic", ".heif"]);
const VIDEO_EXT = new Set([".mp4", ".mov", ".m4v", ".webm"]);

export class ObsidianError extends Error {
  constructor(message, statusCode = 400) {
    super(message);
    this.statusCode = statusCode;
  }
}

export function knownVaults() {
  const vaults = [];
  const override = process.env.FIDGET_OBSIDIAN_VAULT;
  if (override) vaults.push({ name: path.basename(override), path: override });
  const configFile = path.join(os.homedir(), "Library/Application Support/obsidian/obsidian.json");
  try {
    const config = JSON.parse(fs.readFileSync(configFile, "utf8"));
    for (const vault of Object.values(config.vaults || {})) {
      if (vault?.path && !vaults.some((known) => known.path === vault.path)) vaults.push({ name: path.basename(vault.path), path: vault.path });
    }
  } catch { /* no desktop Obsidian config */ }
  return vaults;
}

// Accepts obsidian://open?vault=X&file=Y, obsidian://vault/X/Y, an absolute .md path, or a vault-relative path.
export function parseObsidianLink(link, vaults = knownVaults()) {
  const raw = String(link || "").trim();
  if (!raw) throw new ObsidianError("请填写 Obsidian 链接。");
  let vaultName = null;
  let file = null;
  if (/^obsidian:\/\//i.test(raw)) {
    const url = new URL(raw);
    if (url.hostname === "open" || url.hostname === "new") {
      vaultName = url.searchParams.get("vault");
      file = url.searchParams.get("file") || url.searchParams.get("path");
    } else if (url.hostname === "vault") {
      const [, name, ...rest] = url.pathname.split("/");
      vaultName = decodeURIComponent(name || "");
      file = decodeURIComponent(rest.join("/"));
    }
    if (!file) throw new ObsidianError("链接里没有 file 参数，请从 Obsidian 用「复制 Obsidian 链接」重新复制。");
  } else if (path.isAbsolute(raw)) {
    const vault = vaults.find((candidate) => raw.startsWith(`${candidate.path}${path.sep}`));
    if (!vault) throw new ObsidianError("这个路径不在任何已知的 Obsidian 库里。");
    vaultName = vault.name;
    file = path.relative(vault.path, raw);
  } else {
    file = raw;
  }
  const vault = vaultName ? vaults.find((candidate) => candidate.name === vaultName) : vaults[0];
  if (!vault) throw new ObsidianError(vaultName ? `找不到名为「${vaultName}」的 Obsidian 库。` : "本机没有找到 Obsidian 库。");
  const relative = file.replace(/\\/g, "/").replace(/^\/+/, "");
  const withExt = /\.md$/i.test(relative) ? relative : `${relative}.md`;
  const absolute = insideVault(vault, withExt);
  if (!fs.existsSync(absolute)) throw new ObsidianError(`笔记不存在：${withExt}`, 404);
  return { vault, relativePath: withExt, absolutePath: absolute, locator: raw };
}

function insideVault(vault, relative) {
  const absolute = path.resolve(vault.path, relative);
  if (absolute !== vault.path && !absolute.startsWith(`${vault.path}${path.sep}`)) throw new ObsidianError("路径越出 Obsidian 库。", 403);
  return absolute;
}

export function parseFrontmatter(markdown) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?/.exec(markdown);
  if (!match) return { data: {}, body: markdown };
  const data = {};
  let currentList = null;
  for (const line of match[1].split(/\r?\n/)) {
    const list = /^\s+-\s+(.*)$/.exec(line);
    if (list && currentList) { data[currentList].push(list[1].trim()); continue; }
    const pair = /^([A-Za-z0-9_-]+):\s*(.*)$/.exec(line);
    if (!pair) continue;
    const [, key, value] = pair;
    if (value === "") { data[key] = []; currentList = key; }
    else { data[key] = value.replace(/^["']|["']$/g, ""); currentList = null; }
  }
  return { data, body: markdown.slice(match[0].length) };
}

export function extractEmbeds(body) {
  const embeds = [];
  const wiki = /!\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]/g;
  const markdown = /!\[[^\]]*\]\(([^)\s]+)(?:\s+"[^"]*")?\)/g;
  for (const match of body.matchAll(wiki)) embeds.push(match[1].trim());
  for (const match of body.matchAll(markdown)) embeds.push(decodeURIComponent(match[1].trim()));
  return [...new Set(embeds)];
}

function kindOf(file) {
  const ext = path.extname(file).toLowerCase();
  return IMAGE_EXT.has(ext) ? "image" : VIDEO_EXT.has(ext) ? "video" : null;
}

let basenameIndexCache = new Map();
function findByBasename(vault, basename) {
  const key = vault.path;
  if (!basenameIndexCache.has(key)) {
    const index = new Map();
    const walk = (dir, depth) => {
      if (depth > 8) return;
      let entries = [];
      try { entries = fs.readdirSync(dir, { withFileTypes: true }); } catch { return; }
      for (const entry of entries) {
        if (entry.name.startsWith(".")) continue;
        const full = path.join(dir, entry.name);
        if (entry.isDirectory()) walk(full, depth + 1);
        else if (kindOf(entry.name) && !index.has(entry.name)) index.set(entry.name, full);
      }
    };
    walk(vault.path, 0);
    basenameIndexCache.set(key, index);
  }
  return basenameIndexCache.get(key).get(basename) || null;
}

export function resetObsidianCache() { basenameIndexCache = new Map(); }

export function guessMechanism(text) {
  const t = String(text || "").toLowerCase();
  if (/扇牌|fan.?card|扇卡/.test(t)) return "magnetic-fan-card";
  if (/推牌|滑块|滑动|slide|slider|磁吸推/.test(t)) return "linear-magnetic-slider";
  if (/展示盒|display.?case|盲盒展示/.test(t)) return "display-case";
  if (/陀螺|spinner|旋转|rotor|指尖/.test(t)) return "rotor";
  return "other";
}

export function readObsidianNote(link) {
  const resolved = parseObsidianLink(link);
  const markdown = fs.readFileSync(resolved.absolutePath, "utf8");
  const { data, body } = parseFrontmatter(markdown);
  const heading = /^#\s+(.+)$/m.exec(body)?.[1];
  const rawTitle = (heading || path.basename(resolved.relativePath, ".md")).trim();
  const title = rawTitle.replace(/(^|\s)#([^\s#]+)/g, "$1$2").replace(/\s+/g, " ").trim();
  const attachments = [];
  const missing = [];
  let remote = 0;
  for (const embed of extractEmbeds(body)) {
    if (/^[a-z]+:\/\//i.test(embed)) { remote += 1; continue; }
    const kind = kindOf(embed);
    if (!kind) continue;
    let absolute = null;
    try {
      const direct = insideVault(resolved.vault, embed);
      const relativeToNote = insideVault(resolved.vault, path.join(path.dirname(resolved.relativePath), embed));
      absolute = fs.existsSync(direct) ? direct : fs.existsSync(relativeToNote) ? relativeToNote : findByBasename(resolved.vault, path.basename(embed));
    } catch { absolute = null; }
    if (!absolute) { missing.push(embed); continue; }
    const stat = fs.statSync(absolute);
    attachments.push({ name: path.basename(absolute), kind, sizeBytes: stat.size, absolutePath: absolute, vaultPath: path.relative(resolved.vault.path, absolute) });
  }
  const excerpt = body.replace(/^#+\s.*$/gm, "").replace(/!\[\[[^\]]*\]\]|!\[[^\]]*\]\([^)]*\)/g, "").replace(/\s+/g, " ").trim().slice(0, 240);
  return {
    locator: resolved.locator,
    vault: resolved.vault.name,
    notePath: resolved.relativePath,
    absolutePath: resolved.absolutePath,
    title,
    frontmatter: data,
    sourceUrl: data.url || data.source_url || null,
    author: data.author || null,
    mechanismGuess: guessMechanism(`${title} ${excerpt} ${data.author || ""}`),
    excerpt,
    attachments,
    missing,
    remote,
    markdown
  };
}

// Strip absolute paths before anything leaves the server.
export function publicPreview(note) {
  return {
    locator: note.locator,
    vault: note.vault,
    notePath: note.notePath,
    title: note.title,
    author: note.author,
    sourceUrl: note.sourceUrl,
    saved: note.frontmatter.saved || null,
    mechanismGuess: note.mechanismGuess,
    excerpt: note.excerpt,
    attachments: note.attachments.map(({ name, kind, sizeBytes, vaultPath }) => ({ name, kind, sizeBytes, vaultPath })),
    missing: note.missing,
    remote: note.remote
  };
}
