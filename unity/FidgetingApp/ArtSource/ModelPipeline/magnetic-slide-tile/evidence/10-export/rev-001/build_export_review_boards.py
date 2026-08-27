#!/usr/bin/env python3
"""Build Gate 10 package and texture review boards from real outputs."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
EXPORT = json.loads((ROOT / "export-manifest.json").read_text(encoding="utf-8"))
REIMPORT = json.loads((ROOT / "reimport-validation.json").read_text(encoding="utf-8"))
TEXTURE = json.loads((ROOT / "texture-manifest.json").read_text(encoding="utf-8"))


def font(size: int, bold: bool = False):
    candidates = [
        f"/System/Library/Fonts/Supplemental/Arial {'Bold' if bold else 'Regular'}.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def fit(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    copy = image.copy()
    copy.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, (13, 18, 27))
    canvas.paste(copy, ((size[0] - copy.width) // 2, (size[1] - copy.height) // 2))
    return canvas


def package_board() -> None:
    panels = [
        ("AUTHORITATIVE BLEND / CLOSED", ROOT / "gate10-workbench.png"),
        ("FBX RE-IMPORT", ROOT / "fbx-reimport-workbench.png"),
        ("GLB RE-IMPORT", ROOT / "glb-reimport-workbench.png"),
        ("TWO CONVEX COLLISION CAPSULES", ROOT / "collision-reimport-workbench.png"),
    ]
    board = Image.new("RGB", (2400, 1760), (8, 12, 19))
    draw = ImageDraw.Draw(board)
    draw.text((80, 48), "GATE 10 · IMMUTABLE EXPORT PACKAGE", font=font(56, True), fill=(240, 244, 248))
    draw.text(
        (80, 116),
        "Blend → FBX / GLB → deterministic Blender re-import · Unity import remains Gate 11",
        font=font(28),
        fill=(161, 173, 190),
    )
    panel_size = (1080, 700)
    for index, (label, path) in enumerate(panels):
        x = 80 + (index % 2) * 1160
        y = 180 + (index // 2) * 770
        board.paste(fit(Image.open(path).convert("RGB"), panel_size), (x, y))
        draw.rectangle((x, y, x + panel_size[0], y + panel_size[1]), outline=(65, 79, 98), width=2)
        draw.rectangle((x, y + 636, x + panel_size[0], y + panel_size[1]), fill=(10, 15, 23))
        draw.text((x + 26, y + 650), label, font=font(25, True), fill=(231, 236, 242))
    draw.rectangle((80, 1640, 2320, 1712), fill=(15, 22, 32), outline=(64, 78, 96), width=2)
    summary = (
        "50×31×12 mm  ·  2 meshes / 4,096 tris  ·  FBX+GLB bounds 0.050×0.031×0.012 m  ·  "
        "UV / normals / tangents PASS  ·  collision 256 tris  ·  no animation / LOD"
    )
    draw.text((112, 1662), summary, font=font(24, True), fill=(201, 213, 226))
    board.save(ROOT / "export-package-review-board.png")


def channel_board() -> None:
    board = Image.new("RGB", (2400, 1320), (8, 12, 19))
    draw = ImageDraw.Draw(board)
    draw.text((80, 48), "ARTWORK CHANNELS · INDEPENDENT UPPER / LOWER", font=font(54, True), fill=(240, 244, 248))
    draw.text(
        (80, 114),
        "R motif · G black perimeter · B combined shader mask · A reserved opaque",
        font=font(28),
        fill=(161, 173, 190),
    )
    x_positions = [80, 650, 1220, 1790]
    labels = ["R · MOTIF", "G · PERIMETER", "B · COMBINED", "RGBA PACK"]
    for row, name in enumerate(["upper", "lower"]):
        image = Image.open(ROOT / f"textures/artwork-{name}-channel-pack.png").convert("RGBA")
        channels = image.split()
        previews = [
            Image.merge("RGB", (channels[0], channels[0], channels[0])),
            Image.merge("RGB", (channels[1], channels[1], channels[1])),
            Image.merge("RGB", (channels[2], channels[2], channels[2])),
            image.convert("RGB"),
        ]
        y = 190 + row * 540
        draw.text((80, y), name.upper(), font=font(28, True), fill=(213, 223, 235))
        for x, label, preview in zip(x_positions, labels, previews):
            tile = fit(preview, (500, 430))
            board.paste(tile, (x, y + 44))
            draw.rectangle((x, y + 44, x + 500, y + 474), outline=(65, 79, 98), width=2)
            draw.text((x + 18, y + 486), label, font=font(22, True), fill=(184, 196, 211))
    runtime_astc = TEXTURE["runtimePlannedAstcBytes"]
    draw.rectangle((80, 1240, 2320, 1295), fill=(15, 22, 32), outline=(64, 78, 96), width=2)
    draw.text(
        (110, 1254),
        f"Gate 11 plan only: ASTC 4×4 · max 1024 · mipmaps on · linear · two runtime packs ≈ {runtime_astc / 1_000_000:.2f} MB",
        font=font(23, True),
        fill=(201, 213, 226),
    )
    board.save(ROOT / "texture-channel-review-board.png")


def main() -> None:
    if not EXPORT["pass"] or not REIMPORT["pass"] or not TEXTURE["pass"]:
        raise RuntimeError("Cannot build review boards from failed validation.")
    package_board()
    channel_board()
    report = {
        "schemaVersion": 1,
        "checks": {
            "packageBoardExists": (ROOT / "export-package-review-board.png").exists(),
            "channelBoardExists": (ROOT / "texture-channel-review-board.png").exists(),
            "reimportPass": REIMPORT["pass"],
            "texturePass": TEXTURE["pass"],
        },
    }
    report["pass"] = all(report["checks"].values())
    (ROOT / "review-board-validation.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError("Gate 10 review board validation failed.")


if __name__ == "__main__":
    main()
