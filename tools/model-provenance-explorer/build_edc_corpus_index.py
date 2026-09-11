#!/usr/bin/env python3
"""Build a deterministic, read-only index of the user's EDC reference corpus.

The source vault is never modified.  Discovery is deliberately restricted to
``<vault-root>/YYYY-MM-DD/*.md``; it does not recurse into Obsidian settings,
plugins, Git metadata, or any other directory.  The committed baseline is
identified by stable frontmatter IDs, while later notes with an explicit EDC
signal can be added incrementally.

No network request or media download is performed by this tool.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit, urlunsplit

import numpy as np
from PIL import Image, ImageOps, UnidentifiedImageError


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_VAULT_ROOT = Path(
    "/Users/jiawei.zhou/Documents/Obsidian Vault/笔记同步助手"
)
DEFAULT_OUTPUT = (
    REPO_ROOT
    / "unity/FidgetingApp/ArtSource/ReferenceResearch/EDC/corpus-index.json"
)

DATE_DIRECTORY_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
FRONTMATTER_LINE_RE = re.compile(r"^([A-Za-z][A-Za-z0-9_-]*):\s*(.*)$")
WIKI_IMAGE_RE = re.compile(r"!\[\[([^\]]+)\]\]")
MARKDOWN_IMAGE_RE = re.compile(
    r"!\[[^\]]*\]\(\s*(?:<([^>]+)>|([^\s)]+))(?:\s+[^)]*)?\s*\)"
)
HTML_IMAGE_RE = re.compile(
    r"<img\b[^>]*?\bsrc\s*=\s*['\"]([^'\"]+)['\"][^>]*>", re.IGNORECASE
)
WIKI_LINK_RE = re.compile(r"(?<!!)\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|[^\]]*)?\]\]")

# Strong enough for new-note discovery without treating every object called a
# "toy" as an EDC mechanism.  The initial set below remains ID-pinned because
# several source titles are intentionally cryptic.
EDC_SIGNAL_RE = re.compile(
    r"(?ix)"
    r"(?:\bEDC\b|EDC玩具|GDEDC|fidget(?:\s|\#)|spinner(?:\s|\#)|"
    r"指尖陀螺|解压玩具|减压玩具|无限位推牌|扑克推牌|\#\s*推牌|罐头币)"
)


def _policy(
    note: str,
    cluster_id: str,
    label: str,
    match_status: str = "category-reference",
) -> dict[str, str]:
    return {
        "initialNoteRelativePath": note,
        "clusterId": cluster_id,
        "clusterLabel": label,
        "matchStatus": match_status,
    }


# These are content identities from note frontmatter, not path- or title-based
# guesses.  Only the GEEONE/NOVO clipping is the metal-three-blade target.
BASELINE_SOURCE_POLICIES: dict[str, dict[str, str]] = {
    "c45de71c-48c5-480c-a790-954c288bcd92": _policy(
        "2026-07-31/GoBigger震旦😼就问你帅不帅.md",
        "gobigger-zhen-dan-edc-figure",
        "GoBigger 震旦 EDC figure",
    ),
    "3d7a4abf-9a2a-423f-85a8-e2e1aae45842": _policy(
        "2026-08-01/2026 广州硬核装备展览会逛展攻略.md",
        "gdedc-2026-expo-roundup",
        "2026 GDEDC expo multi-product roundup",
        "multi-product-reference",
    ),
    "764154b2-8f95-4401-9d94-653528f55a8c": _policy(
        "2026-08-01/可以玩一整天的小玩意？！.md",
        "metal-three-blade",
        "GEEONE 龙鳞 / NOVO EDC",
        "exact-model",
    ),
    "78405f8f-4487-4d11-b463-20a1c75db2b0": _policy(
        "2026-08-01/手感巴适，声音得劲~【浮光-KOVO】.md",
        "kovo-fuguang",
        "KOVO 浮光",
    ),
    "e6186100-5986-4022-aa19-85622f0281ac": _policy(
        "2026-08-01/无限旋转的解压玩具？.md",
        "matrix-edc-linjie-infinite-slider",
        "矩阵 EDC 临界无限位推牌",
    ),
    "8c4fbb0e-66f3-4d1e-b87f-93df6d729cc0": _policy(
        "2026-08-01/终于有Clean EDC的锆棒子了.md",
        "clean-edc-zirconium-rod",
        "Clean EDC zirconium rod",
    ),
    "52853b24-2670-4bec-89f2-11586d55c76e": _policy(
        "2026-08-04/nado【钛金喷砂&锆黑磁洗】沉浸式拆玩.md",
        "nado-segment-scale-slider",
        "NADO 段落音阶轨道",
    ),
    "00a70dca-9263-4940-887c-eb8f372a938e": _policy(
        "2026-08-06/老铁匠3.0扑克推牌.md",
        "lautie-poker-slider-3",
        "老铁匠 3.0 扑克推牌",
    ),
    "7c0595fa-ed89-4d88-937a-00edfda5ca48": _policy(
        "2026-08-06/钛蓝巧克力双珠槽高低音.md",
        "lautie-titanium-blue-chocolate-slider",
        "钛蓝巧克力双珠槽推牌",
    ),
    "d8915aa1-8f1a-4006-8c27-0faf21d23460": _policy(
        "2026-08-07/三音阶，怎么推都XX-.md",
        "three-tone-edc-slider-unidentified",
        "三音阶 EDC 推牌（具体型号待确认）",
        "specific-product-unresolved-model",
    ),
    "ba6ee43a-a614-4a9b-93ca-f07af6fc7e2f": _policy(
        "2026-08-07/酥酥麻麻还带吸附感？.md",
        "chimago-jiangmo-dada-slider",
        "CHIMAGO 降魔达达 / 赤马 EDC",
    ),
    "b17b9b4a-6e2c-4e9d-9782-db5030890ddf": _policy(
        "2026-08-08/我的EDC之路。越来越上头，越来越上头.md",
        "jason-yu-mixed-edc-collection",
        "Jason Yu mixed EDC collection",
        "multi-product-reference",
    ),
    "9a7c4af0-9b4a-40c0-bfe2-2cb39e3da477": _policy(
        "2026-08-08/看看你指尖的ootd？#edc #玩个很新的东西 #指尖陀螺 #大人也要玩玩具.md",
        "finger-ootd-spinner-assortment",
        "指尖 OOTD spinner assortment",
        "multi-product-reference",
    ),
    "00385e1f-b23c-42d2-9f2d-b9590fdecc8e": _policy(
        "2026-08-09/喊你女朋友给你买！.md",
        "pigstol-namro-revolver-edc-roundup",
        "PIGSTOL / NAMRO / REVOLVER EDC roundup",
        "multi-product-reference",
    ),
    "65a31b87-416a-4a72-8daa-6441cdb4914f": _policy(
        "2026-08-09/解压罐头币！？🥫.md",
        "showhand-can-coin",
        "SHOWHAND 罐头币",
    ),
    "d0f2075d-78e8-44b0-8f8b-5130473ab8be": _policy(
        "2026-08-10/LBW石刻N7陀螺.md",
        "lbw-circle-n7-spinner",
        "LBW / 圈子 N7 spinner",
    ),
    "441aef98-9d34-4c87-b5ea-9de031b977f6": _policy(
        "2026-08-14/全球首款LED矩阵减压玩具.md",
        "rgb-led-matrix-fidget-slider",
        "RGB LED matrix fidget slider",
    ),
    "0f13f53f-6bd3-4d5e-9cc8-31b28a7eb334": _policy(
        "2026-08-14/金星创玩 EDC 琥珀陀螺——百元价位的高性价比二叶手感陀螺.md",
        "jinxing-amber-two-lobe-spinner",
        "金星创玩琥珀二叶 spinner",
    ),
    "804eee38-c54f-4a49-ae82-0c1957396319": _policy(
        "2026-08-18/这是什么神仙金属啊？TW听闻玲珑云三叶.md",
        "tw-linglongyun-tri-spinner",
        "TW 听闻玲珑云三叶",
        "similar-category-different-model",
    ),
    "f85bdfd0-e701-416c-9382-cd3ed8dd4792": _policy(
        "2026-08-20/#edc 解压玩具.md",
        "tengshun-edc-blind-box-assortment",
        "腾顺 EDC blind-box assortment",
        "multi-product-reference",
    ),
}

EXPLICIT_EXCLUSIONS: dict[str, str] = {
    "2026-07-31/匪帮宝宝.md": (
        "collectible character imagery; no EDC mechanism or EDC tag in the note"
    ),
    "2026-07-31/秋名山车神常有，而路人不常有.md": (
        "automotive sticker post, not an EDC object"
    ),
    "2026-08-01/龙鳞（NOVO EDC）分镜与3D生成规范.md": (
        "assistant-derived storyboard/spec; linked as ai-target, never a raw source"
    ),
    "2026-08-06/视频链接.md": (
        "metadata-only Douyin URL with unknown author, no EDC-identifying content, and no frames"
    ),
    "2026-08-10/无界♾️.md": (
        "ambiguous OCR-only product note; held for manual EDC/product identification"
    ),
    "2026-08-09/同步助手_2026-08-09.md": (
        "inbox aggregate fragment without standalone source frontmatter; manual normalization required"
    ),
    "2026-08-24/同步助手_2026-08-24.md": (
        "inbox aggregate fragment without standalone source frontmatter; manual normalization required"
    ),
}

DEFAULT_EXPECTATIONS = {
    "sourceCount": 20,
    "platformCounts": {"xiaohongshu": 16, "douyin": 4},
    "readableUniqueImageCount": 143,
    "missingImageReferenceCount": 1,
}


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_digest(values: Iterable[str]) -> str:
    return sha256_bytes("\n".join(sorted(values)).encode("utf-8"))


def parse_frontmatter(text: str) -> tuple[dict[str, str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    closing = next(
        (index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"),
        None,
    )
    if closing is None:
        return {}, text
    result: dict[str, str] = {}
    for line in lines[1:closing]:
        match = FRONTMATTER_LINE_RE.match(line)
        if match:
            result[match.group(1)] = match.group(2).strip().strip("\"'")
    return result, "\n".join(lines[closing + 1 :])


def platform_from_source(value: str) -> str | None:
    if "小红书" in value:
        return "xiaohongshu"
    if "抖音" in value:
        return "douyin"
    return None


def canonicalize_url(url: str, platform: str) -> tuple[str, str | None]:
    raw = url.strip()
    parsed = urlsplit(raw)
    host = parsed.netloc.lower()
    path = re.sub(r"/{2,}", "/", parsed.path)
    if platform == "xiaohongshu":
        match = re.search(r"/(?:discovery/item|explore)/([A-Za-z0-9]+)", path)
        if match:
            item_id = match.group(1)
            return f"https://www.xiaohongshu.com/discovery/item/{item_id}", item_id
    if platform == "douyin":
        token_match = re.match(r"/([^/]+)/?", path)
        token = token_match.group(1) if token_match else None
        clean_path = f"/{token}/" if token else path
        clean_host = host or "v.douyin.com"
        return urlunsplit(("https", clean_host, clean_path, "", "")), token
    return urlunsplit((parsed.scheme.lower(), host, path, "", "")), None


def normalize_saved_at(raw: str) -> str:
    try:
        parsed = datetime.strptime(raw.strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return raw.strip()
    return parsed.isoformat(timespec="seconds") + "+08:00"


def note_title(path: Path, body: str) -> str:
    match = re.search(r"(?m)^#\s+(.+?)\s*$", body)
    return match.group(1).strip() if match else path.stem


def discover_markdown(vault_root: Path) -> list[Path]:
    """Return only direct Markdown children of real YYYY-MM-DD directories."""
    root = vault_root.resolve(strict=True)
    notes: list[Path] = []
    for child in sorted(vault_root.iterdir(), key=lambda item: item.name):
        if child.is_symlink() or not DATE_DIRECTORY_RE.fullmatch(child.name):
            continue
        if not child.is_dir() or child.resolve().parent != root:
            continue
        for note in sorted(child.glob("*.md"), key=lambda item: item.name):
            if note.is_symlink() or not note.is_file():
                continue
            if note.resolve().parent != child.resolve():
                continue
            notes.append(note)
    return notes


def extract_image_references(text: str) -> list[str]:
    references: list[str] = []
    for match in WIKI_IMAGE_RE.finditer(text):
        target = match.group(1).split("|", 1)[0].split("#", 1)[0].strip()
        references.append(target)
    for match in MARKDOWN_IMAGE_RE.finditer(text):
        references.append((match.group(1) or match.group(2)).strip())
    for match in HTML_IMAGE_RE.finditer(text):
        references.append(html.unescape(match.group(1).strip()))
    # Repeated embeds in a single note are one source-image relationship.
    return sorted(set(filter(None, references)))


def resolve_local_reference(
    raw_reference: str, note_path: Path, vault_root: Path
) -> tuple[str | None, Path | None, str | None]:
    decoded = unquote(raw_reference).strip().strip("<>")
    parsed = urlsplit(decoded)
    if parsed.scheme in {"http", "https", "data"} or parsed.netloc:
        return None, None, "remote-reference-not-fetched"
    clean = parsed.path.replace("\\", "/")
    prefix = "笔记同步助手/"
    if clean.startswith(prefix):
        candidate = vault_root / clean[len(prefix) :]
    elif clean.startswith("images/"):
        candidate = vault_root / clean
    else:
        candidate = note_path.parent / clean
    try:
        resolved = candidate.resolve(strict=False)
        root = vault_root.resolve(strict=True)
        relative = resolved.relative_to(root).as_posix()
    except (OSError, ValueError):
        return None, None, "outside-vault-scan-root"
    return relative, resolved, None


def _dct_matrix(size: int) -> np.ndarray:
    matrix = np.empty((size, size), dtype=np.float64)
    scale0 = math.sqrt(1.0 / size)
    scale = math.sqrt(2.0 / size)
    for frequency in range(size):
        factor = scale0 if frequency == 0 else scale
        for position in range(size):
            matrix[frequency, position] = factor * math.cos(
                math.pi * (2 * position + 1) * frequency / (2 * size)
            )
    return matrix


_DCT8X32 = _dct_matrix(32)[:8, :]


def phash_dct64(image: Image.Image) -> str:
    """Return a 64-bit perceptual hash using a real 2-D DCT-II.

    The pipeline is: EXIF orientation -> luminance -> Lanczos 32x32 ->
    orthonormal DCT-II -> top-left 8x8 -> median threshold excluding DC.
    """
    normalized = ImageOps.exif_transpose(image).convert("L").resize(
        (32, 32), Image.Resampling.LANCZOS
    )
    pixels = np.asarray(normalized, dtype=np.float64)
    # Compute only the 8x8 low-frequency block needed by pHash.  Explicit
    # element-wise reductions avoid platform BLAS differences while remaining
    # a genuine separable DCT-II.
    coefficients = np.empty((8, 8), dtype=np.float64)
    for row_frequency in range(8):
        weighted_rows = _DCT8X32[row_frequency, :, None] * pixels
        for column_frequency in range(8):
            coefficients[row_frequency, column_frequency] = np.sum(
                weighted_rows * _DCT8X32[column_frequency, None, :],
                dtype=np.float64,
            )
    coefficients[np.abs(coefficients) < 1e-10] = 0.0
    low = coefficients.reshape(-1)
    median = float(np.median(low[1:]))
    value = 0
    for coefficient in low:
        value = (value << 1) | int(coefficient > median)
    return f"{value:016x}"


def _old_image_cache(previous: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    cache: dict[str, dict[str, Any]] = {}
    if not previous:
        return cache
    for source in previous.get("sources", []):
        for image in source.get("images", []):
            relative = image.get("relativePath")
            if relative and image.get("status") == "readable":
                cache[relative] = image
    return cache


def inspect_image(
    relative: str,
    absolute: Path,
    raw_reference: str,
    cached: dict[str, dict[str, Any]] | None,
) -> dict[str, Any]:
    content_class = "ai-target" if relative.startswith("images/generated/") else "source-frame"
    base: dict[str, Any] = {
        "contentClass": content_class,
        "rawReference": raw_reference,
        "relativePath": relative,
    }
    if not absolute.is_file():
        return {**base, "status": "missing"}
    stat = absolute.stat()
    digest = sha256_file(absolute)
    old = cached or {}
    if (
        old.get("sha256") == digest
        and old.get("pHashDct64")
        and old.get("pHashAlgorithm") == "dct-ii-32x32-low8x8-median64-v1"
    ):
        return {
            **base,
            "status": "readable",
            "sizeBytes": stat.st_size,
            "mtimeNs": stat.st_mtime_ns,
            "sha256": digest,
            "pHashAlgorithm": old["pHashAlgorithm"],
            "pHashDct64": old["pHashDct64"],
            "width": old["width"],
            "height": old["height"],
            "mode": old["mode"],
        }
    try:
        with Image.open(absolute) as image:
            image.load()
            width, height = image.size
            mode = image.mode
            perceptual = phash_dct64(image)
    except (OSError, ValueError, UnidentifiedImageError):
        return {
            **base,
            "status": "unreadable",
            "sizeBytes": stat.st_size,
            "mtimeNs": stat.st_mtime_ns,
            "sha256": digest,
        }
    return {
        **base,
        "status": "readable",
        "sizeBytes": stat.st_size,
        "mtimeNs": stat.st_mtime_ns,
        "sha256": digest,
        "pHashAlgorithm": "dct-ii-32x32-low8x8-median64-v1",
        "pHashDct64": perceptual,
        "width": width,
        "height": height,
        "mode": mode,
    }


def _related_derived_notes(note: Path, body: str, vault_root: Path) -> list[dict[str, Any]]:
    related: list[dict[str, Any]] = []
    for raw in sorted(set(WIKI_LINK_RE.findall(body))):
        target = raw if raw.endswith(".md") else raw + ".md"
        candidates = [note.parent / target, vault_root / target]
        match = next((candidate for candidate in candidates if candidate.is_file()), None)
        if match is None:
            continue
        resolved = match.resolve()
        try:
            relative = resolved.relative_to(vault_root.resolve()).as_posix()
        except ValueError:
            continue
        if "龙鳞（NOVO EDC）分镜与3D生成规范" not in relative:
            continue
        related.append(
            {
                "classification": "ai-target",
                "modelingAuthority": "intent-only-never-measurement",
                "noteRelativePath": relative,
                "sha256": sha256_file(resolved),
            }
        )
    return related


def _media_record(original_url: str, platform: str, images: list[dict[str, Any]]) -> dict[str, Any]:
    query = urlsplit(original_url).query
    declared = "video" if platform == "douyin" or re.search(r"(?:^|&)type=video(?:&|$)", query) else "image-post"
    local_frames = sum(
        image["status"] == "readable" and image["contentClass"] == "source-frame"
        for image in images
    )
    return {
        "declaredType": declared,
        "downloadState": "not-requested",
        "localSourceFrameCount": local_frames,
        "remoteAccess": "not-checked",
        "status": "local-frames-available" if local_frames else "remote-only",
        "temporaryDownloadCheckpoint": None,
    }


def _fallback_policy(frontmatter_id: str, title: str, platform: str) -> dict[str, str]:
    compact = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48]
    suffix = compact or frontmatter_id.split("-", 1)[0]
    return {
        "initialNoteRelativePath": "",
        "clusterId": f"untriaged-{platform}-{suffix}",
        "clusterLabel": f"Untriaged EDC source: {title}",
        "matchStatus": "needs-product-clustering",
    }


def _source_record(
    note_path: Path,
    text: str,
    frontmatter: dict[str, str],
    platform: str,
    policy: dict[str, str],
    vault_root: Path,
    cache: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    body = parse_frontmatter(text)[1]
    note_stat = note_path.stat()
    # Preserve the exact on-disk note identity even if a future note contains
    # undecodable bytes that were replaced for metadata parsing.
    note_digest = sha256_file(note_path)
    relative_note = note_path.resolve().relative_to(vault_root.resolve()).as_posix()
    original_url = frontmatter.get("url", "")
    canonical_url, upstream_id = canonicalize_url(original_url, platform)
    images: list[dict[str, Any]] = []
    for raw_reference in extract_image_references(text):
        relative, absolute, resolution_error = resolve_local_reference(
            raw_reference, note_path, vault_root
        )
        if resolution_error:
            images.append(
                {
                    "contentClass": "remote-reference" if resolution_error.startswith("remote") else "invalid-reference",
                    "rawReference": raw_reference,
                    "status": resolution_error,
                }
            )
            continue
        assert relative is not None and absolute is not None
        images.append(inspect_image(relative, absolute, raw_reference, cache.get(relative)))
    images.sort(key=lambda item: (item.get("relativePath", ""), item["rawReference"]))
    status_counts = Counter(image["status"] for image in images)
    readable = [image for image in images if image["status"] == "readable"]
    image_digest = stable_digest(
        f"{image.get('relativePath', image['rawReference'])}:{image.get('sha256', image['status'])}"
        for image in images
    )
    source_id = f"edc:{frontmatter['id']}"
    same_item_as = ["metal-three-blade"] if policy["matchStatus"] == "exact-model" else []
    checkpoint_state = (
        "blocked-missing-local-image"
        if status_counts.get("missing", 0)
        else "complete"
    )
    return {
        "sourceId": source_id,
        "frontmatterId": frontmatter["id"],
        "platform": platform,
        "author": frontmatter.get("author", "Unknown"),
        "title": note_title(note_path, body),
        "originalUrl": original_url,
        "canonicalUrl": canonical_url,
        "upstreamItemId": upstream_id,
        "savedAt": normalize_saved_at(frontmatter.get("saved", "")),
        "note": {
            "relativePath": relative_note,
            "sha256": note_digest,
            "mtimeNs": note_stat.st_mtime_ns,
            "sizeBytes": note_stat.st_size,
        },
        "images": images,
        "imageSummary": {
            "referenceCount": len(images),
            "readableCount": status_counts.get("readable", 0),
            "readableSourceFrameCount": sum(
                image["contentClass"] == "source-frame" for image in readable
            ),
            "readableAiTargetCount": sum(
                image["contentClass"] == "ai-target" for image in readable
            ),
            "missingCount": status_counts.get("missing", 0),
            "unreadableCount": status_counts.get("unreadable", 0),
        },
        "media": _media_record(original_url, platform, images),
        "product": {
            "clusterId": policy["clusterId"],
            "clusterLabel": policy["clusterLabel"],
            "matchStatus": policy["matchStatus"],
            "sameItemAs": same_item_as,
        },
        "rights": {
            "status": "third-party-reference-only",
            "allowedUse": "internal research and source-linked model provenance",
            "redistribution": "not-cleared",
        },
        "resumeCheckpoint": {
            "state": checkpoint_state,
            "noteMtimeNs": note_stat.st_mtime_ns,
            "noteSha256": note_digest,
            "referencedImageDigestSha256": image_digest,
        },
        "relatedDerivedNotes": _related_derived_notes(note_path, body, vault_root),
    }


def _candidate_audit(
    note_by_relative: dict[str, tuple[Path, str, dict[str, str], str]],
    selected_ids: set[str],
) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for relative, reason in sorted(EXPLICIT_EXCLUSIONS.items()):
        entry = note_by_relative.get(relative)
        if entry is None:
            candidates.append(
                {"noteRelativePath": relative, "status": "not-present", "exclusionReason": reason}
            )
            continue
        _, text, metadata, _ = entry
        frontmatter_id = metadata.get("id")
        if frontmatter_id and frontmatter_id in selected_ids:
            continue
        references = extract_image_references(text)
        candidates.append(
            {
                "noteRelativePath": relative,
                "frontmatterId": frontmatter_id,
                "imageReferenceCount": len(references),
                "status": "excluded-or-needs-triage",
                "exclusionReason": reason,
            }
        )
    return candidates


def _acceptance(summary: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    checks = [
        {
            "id": "source-count",
            "expected": expected["sourceCount"],
            "actual": summary["sourceCount"],
        },
        {
            "id": "xiaohongshu-count",
            "expected": expected["platformCounts"]["xiaohongshu"],
            "actual": summary["platformCounts"].get("xiaohongshu", 0),
        },
        {
            "id": "douyin-count",
            "expected": expected["platformCounts"]["douyin"],
            "actual": summary["platformCounts"].get("douyin", 0),
        },
        {
            "id": "readable-unique-image-count",
            "expected": expected["readableUniqueImageCount"],
            "actual": summary["readableUniqueImageCount"],
        },
        {
            "id": "missing-image-reference-count",
            "expected": expected["missingImageReferenceCount"],
            "actual": summary["missingImageReferenceCount"],
        },
    ]
    for check in checks:
        check["status"] = "pass" if check["actual"] == check["expected"] else "fail"
    return {
        "expected": expected,
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "discrepancy",
        "checks": checks,
    }


def build_index(
    vault_root: Path,
    *,
    previous: dict[str, Any] | None = None,
    expectations: dict[str, Any] | None = None,
    baseline_policies: dict[str, dict[str, str]] | None = None,
    include_auto_discovered: bool = True,
) -> dict[str, Any]:
    root = vault_root.resolve(strict=True)
    policies = BASELINE_SOURCE_POLICIES if baseline_policies is None else baseline_policies
    previous_ids = {
        source.get("frontmatterId") for source in (previous or {}).get("sources", [])
    }
    notes = discover_markdown(root)
    note_by_relative: dict[str, tuple[Path, str, dict[str, str], str]] = {}
    selected: list[tuple[Path, str, dict[str, str], str, dict[str, str], str]] = []
    eligible_platform_notes = 0
    for note in notes:
        text = note.read_text(encoding="utf-8", errors="replace")
        metadata, body = parse_frontmatter(text)
        relative = note.resolve().relative_to(root).as_posix()
        note_by_relative[relative] = (note, text, metadata, body)
        platform = platform_from_source(metadata.get("source", ""))
        frontmatter_id = metadata.get("id")
        if platform is None or not frontmatter_id:
            continue
        eligible_platform_notes += 1
        reason: str | None = None
        policy = policies.get(frontmatter_id)
        if policy is not None:
            reason = "id-pinned-baseline"
        elif include_auto_discovered and EDC_SIGNAL_RE.search(note.name + "\n" + body):
            reason = "explicit-edc-signal"
            if frontmatter_id not in previous_ids:
                policy = _fallback_policy(frontmatter_id, note_title(note, body), platform)
            else:
                old_source = next(
                    source
                    for source in previous.get("sources", [])
                    if source.get("frontmatterId") == frontmatter_id
                )
                old_product = old_source.get("product", {})
                policy = {
                    "initialNoteRelativePath": relative,
                    "clusterId": old_product.get("clusterId", f"untriaged-{frontmatter_id}"),
                    "clusterLabel": old_product.get("clusterLabel", note_title(note, body)),
                    "matchStatus": old_product.get("matchStatus", "needs-product-clustering"),
                }
        elif frontmatter_id in previous_ids:
            reason = "retained-from-previous-index"
            old_source = next(
                source
                for source in previous.get("sources", [])
                if source.get("frontmatterId") == frontmatter_id
            )
            old_product = old_source.get("product", {})
            policy = {
                "initialNoteRelativePath": relative,
                "clusterId": old_product.get("clusterId", f"untriaged-{frontmatter_id}"),
                "clusterLabel": old_product.get("clusterLabel", note_title(note, body)),
                "matchStatus": old_product.get("matchStatus", "needs-product-clustering"),
            }
        if reason and policy:
            selected.append((note, text, metadata, platform, policy, reason))

    cache = _old_image_cache(previous)
    sources = [
        _source_record(note, text, metadata, platform, policy, root, cache)
        for note, text, metadata, platform, policy, _ in selected
    ]
    sources.sort(key=lambda source: (source["savedAt"], source["sourceId"]))

    all_images = [image for source in sources for image in source["images"]]
    readable = [image for image in all_images if image["status"] == "readable"]
    unique_by_sha = {image["sha256"]: image for image in readable}
    unique_by_path = {image["relativePath"]: image for image in readable}
    sha_groups: dict[str, list[str]] = defaultdict(list)
    phash_groups: dict[str, list[str]] = defaultdict(list)
    for image in readable:
        sha_groups[image["sha256"]].append(image["relativePath"])
        phash_groups[image["pHashDct64"]].append(image["relativePath"])
    platform_counts = Counter(source["platform"] for source in sources)
    summary = {
        "sourceCount": len(sources),
        "platformCounts": dict(sorted(platform_counts.items())),
        "imageReferenceCount": len(all_images),
        "readableImageReferenceCount": len(readable),
        "readableUniqueImageCount": len(unique_by_sha),
        "readableUniquePathCount": len(unique_by_path),
        "readableSourceFrameCount": sum(
            image["contentClass"] == "source-frame" for image in unique_by_sha.values()
        ),
        "readableAiTargetCount": sum(
            image["contentClass"] == "ai-target" for image in unique_by_sha.values()
        ),
        "missingImageReferenceCount": sum(image["status"] == "missing" for image in all_images),
        "unreadableImageReferenceCount": sum(
            image["status"] == "unreadable" for image in all_images
        ),
        "remoteImageReferenceCount": sum(
            image["status"] == "remote-reference-not-fetched" for image in all_images
        ),
        "exactContentDuplicateGroupCount": sum(len(paths) > 1 for paths in sha_groups.values()),
        "identicalPHashGroupCount": sum(len(set(paths)) > 1 for paths in phash_groups.values()),
    }
    expected = expectations or DEFAULT_EXPECTATIONS
    acceptance = _acceptance(summary, expected)
    missing_baseline = sorted(set(policies) - {source["frontmatterId"] for source in sources})
    selection_entries = []
    reason_by_id = {metadata["id"]: reason for _, _, metadata, _, _, reason in selected}
    for source in sources:
        selection_entries.append(
            {
                "sourceId": source["sourceId"],
                "noteRelativePath": source["note"]["relativePath"],
                "imageReferenceCount": source["imageSummary"]["referenceCount"],
                "readableImageCount": source["imageSummary"]["readableCount"],
                "missingImageCount": source["imageSummary"]["missingCount"],
                "selectionReason": reason_by_id[source["frontmatterId"]],
            }
        )
    cluster_counts = Counter(source["product"]["clusterId"] for source in sources)
    return {
        "schemaVersion": 1,
        "scanContract": {
            "sourcePattern": "笔记同步助手/YYYY-MM-DD/*.md",
            "sourceAccess": "read-only",
            "excludedTrees": [".obsidian", ".claudian", ".git", "plugin configuration"],
            "networkAccess": "none",
            "mediaDownloads": "none",
            "incrementalIdentity": ["frontmatter.id", "note.mtimeNs", "note.sha256"],
        },
        "imageFingerprint": {
            "algorithm": "dct-ii-32x32-low8x8-median64-v1",
            "description": "EXIF transpose; Luma Lanczos 32x32; orthonormal 2-D DCT-II; low 8x8 median excluding DC; 64 bits",
        },
        "summary": summary,
        "acceptance": acceptance,
        "selectionAudit": {
            "markdownFilesScanned": len(notes),
            "platformNotesWithStableId": eligible_platform_notes,
            "baselineSourceIdCount": len(policies),
            "missingBaselineFrontmatterIds": missing_baseline,
            "selectedSources": selection_entries,
            "excludedOrUnresolvedCandidates": _candidate_audit(
                note_by_relative, {source["frontmatterId"] for source in sources}
            ),
        },
        "clusterSummary": [
            {"clusterId": cluster_id, "sourceCount": count}
            for cluster_id, count in sorted(cluster_counts.items())
        ],
        "duplicateAudit": {
            "exactContentGroups": [
                {"sha256": digest, "paths": sorted(paths)}
                for digest, paths in sorted(sha_groups.items())
                if len(paths) > 1
            ],
            "identicalPHashGroups": [
                {"pHashDct64": digest, "paths": sorted(set(paths))}
                for digest, paths in sorted(phash_groups.items())
                if len(set(paths)) > 1
            ],
        },
        "sources": sources,
    }


def serialize_index(index: dict[str, Any]) -> str:
    return json.dumps(index, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--vault-root", type=Path, default=DEFAULT_VAULT_ROOT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true", help="Fail if the existing index differs; never write")
    parser.add_argument(
        "--strict-acceptance",
        action="store_true",
        help="Return non-zero when expected corpus counts do not pass",
    )
    parser.add_argument("--expected-source-count", type=int, default=20)
    parser.add_argument("--expected-xhs-count", type=int, default=16)
    parser.add_argument("--expected-douyin-count", type=int, default=4)
    parser.add_argument("--expected-readable-images", type=int, default=143)
    parser.add_argument("--expected-missing-images", type=int, default=1)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    vault_root = args.vault_root.resolve(strict=True)
    output = args.output.resolve(strict=False)
    try:
        output.relative_to(vault_root)
    except ValueError:
        pass
    else:
        print("refusing to write the corpus index inside the read-only vault", file=sys.stderr)
        return 2
    previous: dict[str, Any] | None = None
    if output.is_file():
        try:
            previous = json.loads(output.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            previous = None
    expectations = {
        "sourceCount": args.expected_source_count,
        "platformCounts": {
            "xiaohongshu": args.expected_xhs_count,
            "douyin": args.expected_douyin_count,
        },
        "readableUniqueImageCount": args.expected_readable_images,
        "missingImageReferenceCount": args.expected_missing_images,
    }
    index = build_index(vault_root, previous=previous, expectations=expectations)
    rendered = serialize_index(index)
    if args.check:
        if not output.is_file() or output.read_text(encoding="utf-8") != rendered:
            print(f"EDC corpus index is stale: {output}", file=sys.stderr)
            return 1
        print(
            f"EDC corpus index is current: {index['summary']['sourceCount']} sources, "
            f"{index['summary']['readableUniqueImageCount']} readable unique images"
        )
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(rendered, encoding="utf-8")
        print(
            f"wrote {output}: {index['summary']['sourceCount']} sources, "
            f"{index['summary']['readableUniqueImageCount']} readable unique images, "
            f"acceptance={index['acceptance']['status']}"
        )
    if args.strict_acceptance and index["acceptance"]["status"] != "pass":
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
