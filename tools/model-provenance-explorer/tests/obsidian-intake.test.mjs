import assert from "node:assert/strict";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import test from "node:test";
import {
  ObsidianError,
  extractEmbeds,
  guessMechanism,
  parseFrontmatter,
  parseObsidianLink,
  publicPreview,
  readObsidianNote,
  resetObsidianCache
} from "../obsidian-intake.mjs";
import { createModelPipeline, importObsidianNote, loadManifest, pipelineDirectory } from "../pipeline-core.mjs";

// A throwaway vault under the OS temp dir so the test never reads the user's real notes.
const vaultRoot = fs.mkdtempSync(path.join(os.tmpdir(), "mpe-vault-"));
const vault = { name: path.basename(vaultRoot), path: vaultRoot };
fs.mkdirSync(path.join(vaultRoot, "同步/2026-09-10"), { recursive: true });
fs.mkdirSync(path.join(vaultRoot, "同步/images"), { recursive: true });
fs.writeFileSync(path.join(vaultRoot, "同步/images/a_MD5.jpg"), Buffer.alloc(300, 1));
fs.writeFileSync(path.join(vaultRoot, "同步/images/clip.mp4"), Buffer.alloc(900, 2));
fs.writeFileSync(path.join(vaultRoot, "同步/2026-09-10/#edc 黄铜陀螺.md"), `---
author: 某玩具店
source: AI整理 - 抖音
url: https://v.douyin.com/abc/
saved: 2026-09-10 08:00:00
tags:
  - 笔记同步助手
---

# #edc 黄铜陀螺

指尖旋转，三翼配重。

![[同步/images/a_MD5.jpg|Image]]![[images/clip.mp4]]![[同步/images/gone.png]]
![remote](https://example.com/x.png)
`);
process.env.FIDGET_OBSIDIAN_VAULT = vaultRoot;
resetObsidianCache();

test("frontmatter and embeds parse", () => {
  const { data, body } = parseFrontmatter("---\na: 1\nlist:\n  - x\n  - y\n---\nbody ![[p.png]] ![alt](q%20r.jpg)");
  assert.equal(data.a, "1");
  assert.deepEqual(data.list, ["x", "y"]);
  assert.deepEqual(extractEmbeds(body), ["p.png", "q r.jpg"]);
  assert.equal(guessMechanism("黄铜陀螺"), "rotor");
  assert.equal(guessMechanism("磁吸推牌"), "linear-magnetic-slider");
  assert.equal(guessMechanism("扇牌"), "magnetic-fan-card");
  assert.equal(guessMechanism("盲盒"), "other");
});

test("obsidian:// links resolve inside the vault only", () => {
  const link = `obsidian://open?vault=${encodeURIComponent(vault.name)}&file=${encodeURIComponent("同步/2026-09-10/#edc 黄铜陀螺")}`;
  const resolved = parseObsidianLink(link, [vault]);
  assert.equal(resolved.relativePath, "同步/2026-09-10/#edc 黄铜陀螺.md");
  assert.throws(() => parseObsidianLink("obsidian://open?vault=nope&file=x", [vault]), ObsidianError);
  assert.throws(() => parseObsidianLink(`obsidian://open?vault=${encodeURIComponent(vault.name)}&file=../../etc/passwd`, [vault]), ObsidianError);
  assert.throws(() => parseObsidianLink("obsidian://open?vault=x", [vault]), /file 参数/);
  assert.throws(() => parseObsidianLink(`obsidian://open?vault=${encodeURIComponent(vault.name)}&file=missing`, [vault]), (error) => error.statusCode === 404);
});

test("readObsidianNote returns title, source, guessed mechanism and resolvable attachments", () => {
  const note = readObsidianNote(`obsidian://open?vault=${encodeURIComponent(vault.name)}&file=${encodeURIComponent("同步/2026-09-10/#edc 黄铜陀螺")}`);
  assert.equal(note.title, "edc 黄铜陀螺");
  assert.equal(note.sourceUrl, "https://v.douyin.com/abc/");
  assert.equal(note.mechanismGuess, "rotor");
  assert.deepEqual(note.attachments.map((item) => [item.name, item.kind]), [["a_MD5.jpg", "image"], ["clip.mp4", "video"]], "basename lookup finds images/clip.mp4");
  assert.deepEqual(note.missing, ["同步/images/gone.png"]);
  assert.equal(note.remote, 1);
  assert.doesNotMatch(note.excerpt, /^#/);
  const preview = publicPreview(note);
  assert.equal(JSON.stringify(preview).includes(vaultRoot), false, "no absolute paths leave the server");
});

test("importObsidianNote archives note + attachments as external references", (t) => {
  const modelId = `zz-test-obsidian-${process.pid.toString(36)}`;
  const cleanup = () => fs.rmSync(pipelineDirectory(modelId), { recursive: true, force: true });
  t.after(cleanup);
  cleanup();
  createModelPipeline({ id: modelId, name: "黄铜陀螺" });
  const result = importObsidianNote(modelId, `obsidian://open?vault=${encodeURIComponent(vault.name)}&file=${encodeURIComponent("同步/2026-09-10/#edc 黄铜陀螺")}`);
  assert.equal(result.assets.length, 3);
  const [noteAsset, image, video] = result.assets;
  assert.match(noteAsset.path, /rev-001\/obsidian-note\.md$/);
  assert.equal(noteAsset.provenance.contentClass, "external-reference-document");
  assert.equal(image.provenance.origin, "external");
  assert.equal(image.role, "external-reference");
  assert.equal(image.provenance.sourceUrl, "https://v.douyin.com/abc/");
  assert.equal(image.provenance.vaultPath, "同步/images/a_MD5.jpg");
  assert.equal(video.provenance.contentClass, "external-reference-video");
  const manifest = loadManifest(modelId);
  const gate01 = manifest.stages[0];
  assert.equal(gate01.status, "ready_for_review");
  assert.deepEqual(gate01.reviewArtifactIds, [image.id, video.id], "note text is archived but not a review image");
  assert.ok(fs.existsSync(path.join(pipelineDirectory(modelId), "evidence/01-intake/rev-001/a_MD5.jpg")));
});
