#!/usr/bin/env python3
"""Package the approved 2026-08-21 Badge concept sheets for implementation handoff.

The approved concept sheets are the visual authority. This script extracts the
badge artwork only (labels remain runtime text), normalizes every badge to a
1024 x 1024 transparent sRGB PNG, creates a dark locked-state companion, copies
the five source contact sheets, and writes a stable-ID manifest.

It deliberately writes to ArtSource rather than overwriting shipping artwork.
The shipping asset swap remains a separate, preview-gated implementation step.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageCms, ImageEnhance, ImageFilter


@dataclass(frozen=True)
class BadgeAsset:
    badge_id: str
    token: str
    short_name: str
    scope: str
    category: str
    grade: str

    @property
    def file_stem(self) -> str:
        return "badge-b10-" + self.badge_id.replace("_", "-")


PAGES: list[tuple[str, list[BadgeAsset]]] = [
    (
        "badge-system-full-01-power-pulse-20260821.png",
        [
            BadgeAsset("toy_power_ignition", "1.0", "POWER", "toy", "power", "ignition"),
            BadgeAsset("toy_power_overdrive", "2.0", "POWER", "toy", "power", "overdrive"),
            BadgeAsset("toy_power_apex", "3.5", "REDLINE", "toy", "power", "apex"),
            BadgeAsset("toy_power_singularity", "4.5", "REDLINE", "toy", "power", "singularity"),
            BadgeAsset("toy_pulse_100", "100", "PULSE", "toy", "pulse", "ignition"),
            BadgeAsset("toy_pulse_1k", "1K", "PULSE", "toy", "pulse", "overdrive"),
            BadgeAsset("toy_pulse_10k", "10K", "PULSE", "toy", "pulse", "apex"),
            BadgeAsset("toy_pulse_100k", "100K", "PULSE", "toy", "pulse", "singularity"),
        ],
    ),
    (
        "badge-system-full-02-technique-combo-20260821.png",
        [
            BadgeAsset("toy_technique_clean", "CLEAN", "CONTROL", "toy", "technique", "ignition"),
            BadgeAsset("toy_technique_power", "POWER", "CONTROL", "toy", "technique", "overdrive"),
            BadgeAsset("toy_technique_speed", "SPEED", "CONTROL", "toy", "technique", "apex"),
            BadgeAsset("toy_technique_endurance", "ENDURE", "CONTROL", "toy", "technique", "apex"),
            BadgeAsset("toy_technique_perfect", "PERFECT", "CONTROL", "toy", "technique", "singularity"),
            BadgeAsset("toy_combo_5", "×5", "CHAIN", "toy", "combo", "ignition"),
            BadgeAsset("toy_combo_10", "×10", "CHAIN", "toy", "combo", "overdrive"),
            BadgeAsset("toy_combo_20", "×20", "CHAIN", "toy", "combo", "apex"),
        ],
    ),
    (
        "badge-system-full-03-combo-focus-rhythm-20260821.png",
        [
            BadgeAsset("toy_combo_50", "×50", "CHAIN", "toy", "combo", "singularity"),
            BadgeAsset("toy_focus_5m", "5M", "FOCUS", "toy", "focus", "ignition"),
            BadgeAsset("toy_focus_30m", "30M", "FOCUS", "toy", "focus", "overdrive"),
            BadgeAsset("toy_focus_2h", "2H", "FOCUS", "toy", "focus", "apex"),
            BadgeAsset("toy_focus_10h", "10H", "FOCUS", "toy", "focus", "singularity"),
            BadgeAsset("collector_rhythm_1w", "1W", "RHYTHM", "collector", "rhythm", "ignition"),
            BadgeAsset("collector_rhythm_4w", "4W", "RHYTHM", "collector", "rhythm", "overdrive"),
            BadgeAsset("collector_rhythm_12w", "12W", "RHYTHM", "collector", "rhythm", "apex"),
        ],
    ),
    (
        "badge-system-full-04-explore-mastery-vault-20260821.png",
        [
            BadgeAsset("collector_explore_2", "2", "EXPLORE", "collector", "explore", "ignition"),
            BadgeAsset("collector_explore_3", "3", "EXPLORE", "collector", "explore", "overdrive"),
            BadgeAsset("collector_explore_5", "5", "EXPLORE", "collector", "explore", "apex"),
            BadgeAsset("collector_mastery_1_lv20", "LV 20", "MASTERY", "collector", "mastery", "ignition"),
            BadgeAsset("collector_mastery_3_lv20", "3×20", "MASTERY", "collector", "mastery", "overdrive"),
            BadgeAsset("collector_mastery_1_lv100", "LV 100", "MASTERY", "collector", "mastery", "apex"),
            BadgeAsset("collector_mastery_3_lv100", "3×100", "MASTERY", "collector", "mastery", "singularity"),
            BadgeAsset("collector_collection_5", "5", "VAULT", "collector", "collection", "ignition"),
        ],
    ),
    (
        "badge-system-full-05-vault-challenge-legacy-20260821.png",
        [
            BadgeAsset("collector_collection_10", "10", "VAULT", "collector", "collection", "overdrive"),
            BadgeAsset("collector_collection_25", "25", "VAULT", "collector", "collection", "singularity"),
            BadgeAsset("challenge_redline", "3×", "REDLINE", "challenge", "challenge", "apex"),
            BadgeAsset("challenge_chain_reactor", "2×20", "CHAIN", "challenge", "challenge", "apex"),
            BadgeAsset("challenge_perfect_protocol", "3×", "PERFECT", "challenge", "challenge", "singularity"),
            BadgeAsset("challenge_three_core_raid", "3 CORE", "RAID", "challenge", "challenge", "singularity"),
            BadgeAsset("challenge_cycle_total", "4/4", "CYCLE", "challenge", "challenge", "singularity"),
            BadgeAsset("legacy_founder", "LEGACY", "FOUNDER", "legacy", "legacy", "singularity"),
        ],
    ),
]


X_CENTERS = (0.19, 0.50, 0.80)
Y_CENTERS = (0.155, 0.475, 0.795)
TARGET_SIZE = 1024
ARTWORK_SIZE = 856


def _recentered_on_true_badge(
    rgb: np.ndarray, center: tuple[int, int]
) -> tuple[int, int]:
    """Re-center on the badge actually nearest the assumed grid position.

    The five contact sheets were not all generated with an identical row/column
    grid; on the technique/combo sheet the true badge center sits ~30-37 px
    below the assumed grid center. `_largest_badge_contour`'s tight search
    window (sized to keep runtime labels out) can then clip straight through
    the badge's closed ring. A severed ring is no longer a closed loop, so the
    fill in `_extract_badge` only captures the thin ring arc instead of the
    full disk, silently dropping the well and glyph. This coarse, generously
    sized pass finds the true center first so the tight pass is aimed
    correctly.
    """
    height, width = rgb.shape[:2]
    cx, cy = center
    half_w = round(width * 0.20)
    half_h = round(height * 0.30)
    x0, x1 = max(0, cx - half_w), min(width, cx + half_w)
    y0, y1 = max(0, cy - half_h), min(height, cy + half_h)
    roi = rgb[y0:y1, x0:x1]
    gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    _, threshold = cv2.threshold(gray, 62, 255, cv2.THRESH_BINARY)
    threshold = cv2.morphologyEx(
        threshold,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
        iterations=1,
    )
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        return center
    contour = max(contours, key=cv2.contourArea)
    if cv2.contourArea(contour) < 12_000:
        return center
    x, y, w, h = cv2.boundingRect(contour)
    return (x + x0 + w // 2, y + y0 + h // 2)


def _largest_badge_contour(rgb: np.ndarray, center: tuple[int, int]) -> np.ndarray:
    height, width = rgb.shape[:2]
    center = _recentered_on_true_badge(rgb, center)
    cx, cy = center
    half_w = round(width * 0.155)
    # Keep runtime labels outside the search window. The source sheets reserve
    # a narrow gap below each badge before the two text lines begin.
    half_h = round(height * 0.124)
    x0, x1 = max(0, cx - half_w), min(width, cx + half_w)
    y0, y1 = max(0, cy - half_h), min(height, cy + half_h)
    roi = rgb[y0:y1, x0:x1]
    gray = cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY)
    _, threshold = cv2.threshold(gray, 62, 255, cv2.THRESH_BINARY)
    # A tiny close repairs antialiased frame gaps without bridging the badge
    # point to the first line of runtime text below it.
    threshold = cv2.morphologyEx(
        threshold,
        cv2.MORPH_CLOSE,
        cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3)),
        iterations=1,
    )
    contours, _ = cv2.findContours(threshold, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise RuntimeError(f"No badge contour found near {center}")
    contour = max(contours, key=cv2.contourArea).copy()
    if cv2.contourArea(contour) < 12_000:
        raise RuntimeError(f"Badge contour near {center} is unexpectedly small")
    contour[:, 0, 0] += x0
    contour[:, 0, 1] += y0
    return contour


def _extract_badge(source: Image.Image, center: tuple[int, int]) -> Image.Image:
    rgb = np.asarray(source.convert("RGB"))
    contour = _largest_badge_contour(rgb, center)
    full_mask = np.zeros(rgb.shape[:2], dtype=np.uint8)
    cv2.drawContours(full_mask, [contour], -1, 255, thickness=cv2.FILLED, lineType=cv2.LINE_AA)

    x, y, w, h = cv2.boundingRect(contour)
    side = max(w, h) + 42
    crop_cx = x + w // 2
    crop_cy = y + h // 2
    x0 = max(0, crop_cx - side // 2)
    y0 = max(0, crop_cy - side // 2)
    x1 = min(rgb.shape[1], x0 + side)
    y1 = min(rgb.shape[0], y0 + side)
    x0 = max(0, x1 - side)
    y0 = max(0, y1 - side)

    crop_rgb = rgb[y0:y1, x0:x1]
    crop_mask = full_mask[y0:y1, x0:x1]

    hard = Image.fromarray(crop_mask)
    shadow = hard.filter(ImageFilter.GaussianBlur(radius=10))
    shadow = shadow.point(lambda value: round(value * 0.28))
    alpha = Image.fromarray(np.maximum(np.asarray(hard), np.asarray(shadow)))
    # The source contact sheet contains runtime labels below the badge. Clear
    # RGB outside the physical shell before adding the soft shadow so those
    # hidden label pixels cannot bleed through texture filtering or an
    # incorrectly premultiplied renderer.
    sanitized_rgb = crop_rgb.copy()
    sanitized_rgb[crop_mask == 0] = 0
    crop = Image.fromarray(sanitized_rgb).convert("RGBA")
    crop.putalpha(alpha)

    scale = min(ARTWORK_SIZE / crop.width, ARTWORK_SIZE / crop.height)
    crop = crop.resize(
        (round(crop.width * scale), round(crop.height * scale)),
        Image.Resampling.LANCZOS,
    )
    crop = crop.filter(ImageFilter.UnsharpMask(radius=1.1, percent=115, threshold=3))
    canvas = Image.new("RGBA", (TARGET_SIZE, TARGET_SIZE), (0, 0, 0, 0))
    canvas.alpha_composite(crop, ((TARGET_SIZE - crop.width) // 2, (TARGET_SIZE - crop.height) // 2))
    return canvas


def _locked_variant(unlocked: Image.Image) -> Image.Image:
    rgb = unlocked.convert("RGB")
    gray = ImageEnhance.Contrast(rgb.convert("L")).enhance(0.82)
    values = np.asarray(gray, dtype=np.float32)
    locked = np.stack(
        [values * 0.22 + 8.0, values * 0.23 + 9.0, values * 0.27 + 12.0],
        axis=-1,
    )
    locked = np.clip(locked, 0, 255).astype(np.uint8)
    output = Image.fromarray(locked).convert("RGBA")
    output.putalpha(unlocked.getchannel("A"))
    return output


def _save_png(image: Image.Image, path: Path, icc_profile: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=True, icc_profile=icc_profile)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package(repo_root: Path) -> None:
    source_dir = repo_root / "canvas/pages/page/assets"
    package_dir = repo_root / "unity/FidgetingApp/ArtSource/BadgeSystem/ChallengeLegacyApproved20260821"
    contact_dir = package_dir / "contact-sheets"
    unlocked_dir = package_dir / "png-1024/unlocked"
    locked_dir = package_dir / "png-1024/locked"
    contact_dir.mkdir(parents=True, exist_ok=True)

    srgb = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    manifest_assets: list[dict[str, object]] = []

    for page_index, (source_name, badges) in enumerate(PAGES, start=1):
        source_path = source_dir / source_name
        if not source_path.is_file():
            raise FileNotFoundError(source_path)
        source = Image.open(source_path).convert("RGB")
        if source.width != source.height:
            raise RuntimeError(f"Contact sheet must be square: {source_path}")
        shutil.copy2(source_path, contact_dir / source_name)

        for cell_index, badge in enumerate(badges):
            row, column = divmod(cell_index, 3)
            center = (
                round(source.width * X_CENTERS[column]),
                round(source.height * Y_CENTERS[row]),
            )
            unlocked = _extract_badge(source, center)
            locked = _locked_variant(unlocked)
            unlocked_path = unlocked_dir / f"{badge.file_stem}.png"
            locked_path = locked_dir / f"{badge.file_stem}-locked.png"
            _save_png(unlocked, unlocked_path, srgb)
            _save_png(locked, locked_path, srgb)

            entry = asdict(badge)
            entry.update(
                {
                    "page": page_index,
                    "row": row + 1,
                    "column": column + 1,
                    "source_contact_sheet": f"contact-sheets/{source_name}",
                    "unlocked_png": f"png-1024/unlocked/{unlocked_path.name}",
                    "locked_png": f"png-1024/locked/{locked_path.name}",
                    "unlocked_sha256": _sha256(unlocked_path),
                    "locked_sha256": _sha256(locked_path),
                    "runtime_text_position": "outside-badge",
                }
            )
            manifest_assets.append(entry)

    if len(manifest_assets) != 40:
        raise RuntimeError(f"Expected 40 assets, created {len(manifest_assets)}")

    manifest = {
        "schema_version": 1,
        "design_requirement_ids": ["FDB-BDG-006", "FDB-BDG-010"],
        "decision_date": "2026-08-21",
        "visual_direction": "approved",
        "shipping_integration": "pending-real-implementation-preview",
        "asset_count": len(manifest_assets),
        "artwork": {
            "format": "PNG",
            "width": TARGET_SIZE,
            "height": TARGET_SIZE,
            "color_space": "sRGB",
            "background": "transparent",
            "badge_contains_text": False,
        },
        "assets": manifest_assets,
    }
    (package_dir / "badge-asset-manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    expected_ids = {asset.badge_id for _, assets in PAGES for asset in assets}
    actual_ids = {entry["badge_id"] for entry in manifest_assets}
    unlocked_hashes: set[str] = set()
    validation_errors: list[str] = []
    for entry in manifest_assets:
        for state in ("unlocked", "locked"):
            asset_path = package_dir / str(entry[f"{state}_png"])
            with Image.open(asset_path) as image:
                if image.size != (TARGET_SIZE, TARGET_SIZE):
                    validation_errors.append(f"{asset_path.name}: expected 1024 x 1024")
                if image.mode != "RGBA":
                    validation_errors.append(f"{asset_path.name}: expected RGBA")
                if not image.info.get("icc_profile"):
                    validation_errors.append(f"{asset_path.name}: missing sRGB profile")
                alpha = np.asarray(image.getchannel("A"))
                if int(alpha.max()) != 255:
                    validation_errors.append(f"{asset_path.name}: invalid alpha range")
                opaque = (alpha >= 128).astype(np.uint8)
                count, _, stats, _ = cv2.connectedComponentsWithStats(opaque, 8)
                large_components = [row for row in stats[1:] if int(row[4]) >= 512]
                if len(large_components) != 1:
                    validation_errors.append(
                        f"{asset_path.name}: expected one connected badge, found {len(large_components)}"
                    )
        unlocked_hashes.add(str(entry["unlocked_sha256"]))

    if expected_ids != actual_ids:
        validation_errors.append("manifest stable IDs do not match the 40-entry source catalog")
    if len(unlocked_hashes) != len(manifest_assets):
        validation_errors.append("unlocked artwork contains duplicate files")

    report = {
        "passed": not validation_errors,
        "asset_count": len(manifest_assets),
        "unlocked_png_count": len(list(unlocked_dir.glob("*.png"))),
        "locked_png_count": len(list(locked_dir.glob("*.png"))),
        "contact_sheet_count": len(list(contact_dir.glob("*.png"))),
        "dimensions": [TARGET_SIZE, TARGET_SIZE],
        "color_space": "sRGB",
        "stable_ids_unique": len(actual_ids) == 40,
        "unlocked_hashes_unique": len(unlocked_hashes) == 40,
        "errors": validation_errors,
    }
    (package_dir / "validation-report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    if validation_errors:
        raise RuntimeError("Badge package validation failed: " + "; ".join(validation_errors))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo-root",
        type=Path,
        default=Path(__file__).resolve().parents[4],
        help="Fidgeting app repository root",
    )
    args = parser.parse_args()
    package(args.repo_root.resolve())


if __name__ == "__main__":
    main()
