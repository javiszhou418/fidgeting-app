#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageStat


PRODUCTS = [
    ("metal-three-blade", "METAL THREE-BLADE"),
    ("graphite-two-lobe", "GRAPHITE TWO-LOBE"),
    ("magnetic-slide-tile", "MAGNETIC SLIDE"),
    ("magnetic-fan-card", "MAGNETIC FAN CARD"),
]
RARITIES = [
    ("steel", "STANDARD / COLD STEEL"),
    ("copper", "REFINED / ROSE BRONZE"),
    ("silver", "SIGNATURE / GREY-BLUE TITANIUM"),
    ("gold", "HEIRLOOM / CHAMPAGNE"),
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font(size: int):
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/SFNS.ttf"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def non_black_crop(image: Image.Image, threshold: int = 10, margin: int = 24):
    rgb = image.convert("RGB")
    mask = rgb.point(lambda value: 255 if value > threshold else 0).convert("L")
    box = mask.getbbox()
    if box is None:
        raise ValueError("blank image")
    left, top, right, bottom = box
    return rgb.crop(
        (
            max(0, left - margin),
            max(0, top - margin),
            min(rgb.width, right + margin),
            min(rgb.height, bottom + margin),
        )
    )


def fit(image: Image.Image, width: int, height: int):
    copy = image.copy()
    copy.thumbnail((width, height), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (width, height), (12, 13, 16))
    canvas.paste(copy, ((width - copy.width) // 2, (height - copy.height) // 2))
    return canvas


def compose_content_phone(evidence: Path, output: Path):
    tile_w, tile_h = 740, 980
    title_h = 62
    sheet = Image.new("RGB", (tile_w * 2 + 24, (tile_h + title_h) * 2 + 24), (8, 9, 12))
    draw = ImageDraw.Draw(sheet)
    label_font = font(25)
    for index, (model_id, label) in enumerate(PRODUCTS):
        source = evidence / "content" / f"{model_id}-phone-front.png"
        tile = fit(non_black_crop(Image.open(source)), tile_w, tile_h)
        x = (index % 2) * (tile_w + 24)
        y = (index // 2) * (tile_h + title_h + 24)
        draw.text((x + 18, y + 16), label, fill=(225, 229, 235), font=label_font)
        sheet.paste(tile, (x, y + title_h))
    sheet.save(output)


def compose_center_proof(evidence: Path, report: dict, output: Path):
    tile = 720
    title_h = 76
    sheet = Image.new("RGB", (tile * 2 + 24, (tile + title_h) * 2 + 24), (8, 9, 12))
    draw = ImageDraw.Draw(sheet)
    label_font = font(20)
    rows = {row["modelId"]: row for row in report["products"]}
    for index, (model_id, label) in enumerate(PRODUCTS):
        source = evidence / "content" / f"{model_id}-pocket-front.png"
        image = Image.open(source).convert("RGB").resize((tile, tile), Image.Resampling.LANCZOS)
        overlay = ImageDraw.Draw(image)
        center = tile // 2
        overlay.line((center - 22, center, center + 22, center), fill=(0, 210, 255), width=2)
        overlay.line((center, center - 22, center, center + 22), fill=(0, 210, 255), width=2)
        row = rows[model_id]
        caption = (
            f"{label}  center={max(abs(row['centerOffsetMm'][0]), abs(row['centerOffsetMm'][1])):.5f} mm"
            f"  screen={row['screenCenterErrorPixels']:.4f} px"
            f"  fill={row['occupancy'] * 100:.1f}%"
        )
        x = (index % 2) * (tile + 24)
        y = (index // 2) * (tile + title_h + 24)
        draw.text((x + 12, y + 15), caption, fill=(225, 229, 235), font=label_font)
        sheet.paste(image, (x, y + title_h))
    sheet.save(output)


def compose_quarters(evidence: Path, output: Path):
    tile_w, tile_h = 680, 940
    title_h = 60
    sheet = Image.new("RGB", (tile_w * 2 + 24, (tile_h + title_h) * 2 + 24), (8, 9, 12))
    draw = ImageDraw.Draw(sheet)
    label_font = font(24)
    for index, (model_id, label) in enumerate(PRODUCTS):
        source = evidence / "content" / f"{model_id}-phone-quarter.png"
        tile = fit(non_black_crop(Image.open(source)), tile_w, tile_h)
        x = (index % 2) * (tile_w + 24)
        y = (index // 2) * (tile_h + title_h + 24)
        draw.text((x + 16, y + 15), label, fill=(225, 229, 235), font=label_font)
        sheet.paste(tile, (x, y + title_h))
    sheet.save(output)


def compose_rarity(evidence: Path, output: Path):
    column_w = 470
    phone_h = 780
    header_h = 264
    title_h = 70
    gap = 18
    sheet = Image.new(
        "RGB",
        (column_w * 4 + gap * 3, title_h + phone_h + gap + header_h),
        (8, 9, 12),
    )
    draw = ImageDraw.Draw(sheet)
    label_font = font(21)
    for index, (tier, label) in enumerate(RARITIES):
        x = index * (column_w + gap)
        draw.text((x + 12, 20), label, fill=(225, 229, 235), font=label_font)
        phone = fit(
            non_black_crop(Image.open(evidence / "rarity" / f"{tier}-phone-front.png")),
            column_w,
            phone_h,
        )
        header = fit(
            Image.open(evidence / "rarity" / f"{tier}-header-front.png").convert("RGB"),
            column_w,
            header_h,
        )
        sheet.paste(phone, (x, title_h))
        sheet.paste(header, (x, title_h + phone_h + gap))
    sheet.save(output)


def image_metrics(path: Path):
    image = Image.open(path).convert("RGB")
    stats = ImageStat.Stat(image)
    return {
        "path": str(path),
        "width": image.width,
        "height": image.height,
        "channelStdDev": [round(value, 3) for value in stats.stddev],
        "sha256": sha256(path),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", required=True, type=Path)
    parser.add_argument("--stamp", required=True)
    args = parser.parse_args()
    evidence = (
        args.repo
        / "unity/FidgetingApp/ArtSource/ModelPipeline/premium-display-case"
        / "evidence/12-shipping/v3-rev-010"
    )
    output_dir = args.repo / "Artifacts/TriSpinnerSlab/gate12-r010"
    output_dir.mkdir(parents=True, exist_ok=True)
    report = json.loads((evidence / "gate12-r010-review-report.json").read_text())
    if report["status"] != "pass" or report["failures"]:
        raise SystemExit("R010 report is not pass")

    outputs = {
        "contentPhoneMatrix": output_dir
        / f"gate12-r010-content-phone-matrix-{args.stamp}.png",
        "contentCenterProof": output_dir
        / f"gate12-r010-content-center-proof-{args.stamp}.png",
        "contentQuarterMatrix": output_dir
        / f"gate12-r010-content-quarter-matrix-{args.stamp}.png",
        "rarityCmfMatrix": output_dir
        / f"gate12-r010-rarity-cmf-matrix-{args.stamp}.png",
        "audit": output_dir / f"gate12-r010-review-audit-{args.stamp}.json",
    }
    existing = [path for path in outputs.values() if path.exists()]
    if existing:
        raise SystemExit(f"refusing to overwrite: {existing}")

    compose_content_phone(evidence, outputs["contentPhoneMatrix"])
    compose_center_proof(evidence, report, outputs["contentCenterProof"])
    compose_quarters(evidence, outputs["contentQuarterMatrix"])
    compose_rarity(evidence, outputs["rarityCmfMatrix"])
    audit = {
        "status": "pass",
        "sourceReport": str(evidence / "gate12-r010-review-report.json"),
        "sourceReportSha256": sha256(evidence / "gate12-r010-review-report.json"),
        "checks": {
            "fourProducts": len(report["products"]) == 4,
            "fourRarities": len(report["rarities"]) == 4,
            "noBuilderFailures": not report["failures"],
            "allCenterErrorsAtMost005Mm": all(
                max(abs(row["centerOffsetMm"][0]), abs(row["centerOffsetMm"][1]))
                <= 0.05
                for row in report["products"]
            ),
            "allScreenErrorsAtMost1Px": all(
                row["screenCenterErrorPixels"] <= 1
                for row in report["products"]
            ),
            "allOccupancy75To100Percent": all(
                0.75 <= row["occupancy"] <= 1.002
                for row in report["products"]
            ),
        },
        "outputs": [
            image_metrics(path)
            for key, path in outputs.items()
            if key != "audit"
        ],
    }
    if not all(audit["checks"].values()):
        raise SystemExit(json.dumps(audit["checks"], indent=2))
    outputs["audit"].write_text(
        json.dumps(audit, indent=2, ensure_ascii=False) + "\n"
    )
    print(json.dumps({key: str(path) for key, path in outputs.items()}, indent=2))


if __name__ == "__main__":
    main()
