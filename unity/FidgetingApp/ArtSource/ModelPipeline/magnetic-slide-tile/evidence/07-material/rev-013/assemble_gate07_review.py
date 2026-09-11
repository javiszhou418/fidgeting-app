#!/usr/bin/env python3
"""Assemble supplementary Gate 07 rev 13 review boards."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


HERE = Path(__file__).resolve().parent
REJECTION = HERE / "user-rejection-side-artwork-wrap.png"
REPORT = HERE / "review-board-report.json"
FONT_PATHS = [
    Path("/System/Library/Fonts/SFNS.ttf"),
    Path("/System/Library/Fonts/Helvetica.ttc"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font(size: int):
    path = next((candidate for candidate in FONT_PATHS if candidate.exists()), None)
    return ImageFont.truetype(str(path), size) if path else ImageFont.load_default()


def labeled_tile(path: Path, label: str, size=(760, 520)) -> Image.Image:
    image = Image.open(path).convert("RGB")
    tile = Image.new("RGB", size, "#17191d")
    content = ImageOps.fit(
        image,
        (size[0], size[1] - 58),
        method=Image.Resampling.LANCZOS,
        centering=(0.5, 0.5),
    )
    tile.paste(content, (0, 58))
    draw = ImageDraw.Draw(tile)
    draw.text((20, 14), label, fill="#f4f5f7", font=font(26))
    return tile


def grid_board(output: Path, title: str, tiles: list[tuple[Path, str]], columns: int) -> None:
    tile_size = (760, 520)
    rows = (len(tiles) + columns - 1) // columns
    board = Image.new(
        "RGB",
        (columns * tile_size[0], 84 + rows * tile_size[1]),
        "#0d0f12",
    )
    draw = ImageDraw.Draw(board)
    draw.text((28, 22), title, fill="#ffffff", font=font(34))
    for index, (path, label) in enumerate(tiles):
        x = (index % columns) * tile_size[0]
        y = 84 + (index // columns) * tile_size[1]
        board.paste(labeled_tile(path, label, tile_size), (x, y))
    board.save(output, optimize=True)


def comparison_board(output: Path) -> None:
    left = labeled_tile(REJECTION, "REJECTED — artwork sampled on side walls", (900, 590))
    right = labeled_tile(HERE / "side-wall-closeup.png", "REV 13 — solid dark side, zero artwork", (900, 590))
    board = Image.new("RGB", (1800, 720), "#0d0f12")
    draw = ImageDraw.Draw(board)
    draw.text(
        (26, 18),
        "Gate 07 rev 13 material-boundary correction",
        fill="#ffffff",
        font=font(34),
    )
    board.paste(left, (0, 74))
    board.paste(right, (900, 74))
    draw.text(
        (26, 678),
        "Root cause: a later roughness pass cleared material slots and reset every face to artwork slot 0.",
        fill="#cbd0d8",
        font=font(23),
    )
    board.save(output, optimize=True)


def main() -> None:
    required = [
        REJECTION,
        HERE / "assembled-hero.png",
        HERE / "upper-top-closeup.png",
        HERE / "lower-top-open-closeup.png",
        HERE / "side-wall-closeup.png",
        HERE / "silver-rim-closeup.png",
        HERE / "underside-closeup.png",
    ]
    missing = [str(path) for path in required if not path.exists()]
    if missing:
        raise RuntimeError(f"Missing review images: {missing}")
    review = HERE / "gate07-r013-material-review-board.png"
    closeups = HERE / "gate07-r013-top-side-rim-closeups.png"
    comparison = HERE / "gate07-r013-rejection-correction.png"
    grid_board(
        review,
        "GATE 07 REV 13 — CAP / SIDE / RIM MATERIAL REVIEW",
        [
            (HERE / "assembled-hero.png", "Closed hero"),
            (HERE / "upper-top-closeup.png", "Upper top artwork"),
            (HERE / "lower-top-open-closeup.png", "Lower top artwork — independently replaceable"),
            (HERE / "side-wall-closeup.png", "Vertical walls — solid dark"),
            (HERE / "silver-rim-closeup.png", "Thin rim — polished bright silver"),
            (HERE / "underside-closeup.png", "Underside — neutral, no motif"),
        ],
        3,
    )
    grid_board(
        closeups,
        "TOP ARTWORK ONLY · SIDE ARTWORK 0 · POLISHED SILVER RIM",
        [
            (HERE / "upper-top-closeup.png", "Flat top decorative area"),
            (HERE / "side-wall-closeup.png", "Solid dark vertical side"),
            (HERE / "silver-rim-closeup.png", "Bright silver bevel strip"),
        ],
        3,
    )
    comparison_board(comparison)
    report = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "07-material",
        "revision": 13,
        "outputs": {
            path.name: {
                "sha256": sha256(path),
                "sizePx": list(Image.open(path).size),
            }
            for path in (review, closeups, comparison)
        },
        "checks": {
            "rejectionArchived": sha256(REJECTION)
            == "a7859940ee1d956755c07a810bc5aeccee75136da092cb8f1891bf9fe6dc8b1b",
            "reviewBoard": review.exists(),
            "topSideRimCloseups": closeups.exists(),
            "beforeAfterComparison": comparison.exists(),
        },
    }
    report["pass"] = all(report["checks"].values())
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if not report["pass"]:
        raise RuntimeError(json.dumps(report, indent=2))
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
