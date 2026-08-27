"""Collect real Unity and native Gate 12 review evidence."""

from __future__ import annotations

import hashlib
import json
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[7]
PROJECT = REPO / "unity/FidgetingApp"
UNITY_PREVIEWS = REPO / "Artifacts/FanCardMaterialPreview"
NATIVE_PREVIEWS = PROJECT / "Artifacts/GachaPackShippingNativePreview"
LOGS = PROJECT / "Logs"
FONT = "/System/Library/Fonts/SFNS.ttf"

SOURCES = {
    "shipping-library.png": UNITY_PREVIEWS / "fan-card-library-centered.png",
    "shipping-hero.png": UNITY_PREVIEWS / "fan-card-hero.png",
    "shipping-top.png": UNITY_PREVIEWS / "fan-card-top.png",
    "shipping-left-oblique.png": UNITY_PREVIEWS / "fan-card-left.png",
    "shipping-right-oblique.png": UNITY_PREVIEWS / "fan-card-right.png",
    "shipping-low.png": UNITY_PREVIEWS / "fan-card-low.png",
    "shipping-phone.png": NATIVE_PREVIEWS / "01-storefront-pack-entry.png",
    "shipping-back.png": UNITY_PREVIEWS / "fan-card-back.png",
    "shipping-track-closeup.png":
        UNITY_PREVIEWS / "fan-card-back-track-closeup.png",
}

TEST_SOURCES = {
    "fan-card-acceptance-tests.xml":
        LOGS / "FanCardAcceptanceTests-Gate12.xml",
    "gacha-storefront-integration-tests.xml":
        LOGS / "GachaStorefrontIntegrationTests-Gate12.xml",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font(size: int, variation: str):
    value = ImageFont.truetype(FONT, size)
    try:
        value.set_variation_by_name(variation)
    except OSError:
        pass
    return value


def fit(path: Path, size: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    image.thumbnail(size, Image.Resampling.LANCZOS)
    result = Image.new("RGB", size, (9, 10, 11))
    result.paste(
        image,
        ((size[0] - image.width) // 2, (size[1] - image.height) // 2),
    )
    return result


def test_summary(path: Path) -> dict:
    root = ET.parse(path).getroot()
    return {
        key: int(root.attrib[key])
        for key in ("total", "passed", "failed", "skipped")
    } | {"result": root.attrib["result"]}


def main() -> None:
    assets = {}
    for destination_name, source in SOURCES.items():
        if not source.exists():
            raise FileNotFoundError(source)
        destination = HERE / destination_name
        shutil.copy2(source, destination)
        with Image.open(destination) as image:
            dimensions = list(image.size)
        assets[destination_name] = {
            "source": str(source.relative_to(REPO)),
            "sha256": sha256(destination),
            "dimensions": dimensions,
            "sizeBytes": destination.stat().st_size,
        }

    tests = {}
    for destination_name, source in TEST_SOURCES.items():
        if not source.exists():
            raise FileNotFoundError(source)
        destination = HERE / destination_name
        shutil.copy2(source, destination)
        tests[destination_name] = {
            "source": str(source.relative_to(REPO)),
            "sha256": sha256(destination),
            "summary": test_summary(destination),
        }
        if tests[destination_name]["summary"]["failed"] != 0:
            raise RuntimeError(f"Tests failed: {destination_name}")

    canvas = Image.new("RGB", (2400, 1440), (8, 9, 10))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (32, 22),
        "GATE 12 · SHIPPING UNITY + NATIVE",
        font=font(34, "Bold"),
        fill=(237, 224, 199),
    )
    draw.text(
        (32, 66),
        "Real Unity scene views plus the shipping-source iPhone Simulator storefront. No build or phone install.",
        font=font(18, "Regular"),
        fill=(155, 158, 162),
    )
    panels = (
        ("shipping-library.png", "LIBRARY"),
        ("shipping-hero.png", "HERO"),
        ("shipping-top.png", "TOP"),
        ("shipping-left-oblique.png", "LEFT"),
        ("shipping-right-oblique.png", "RIGHT"),
        ("shipping-low.png", "LOW"),
    )
    for index, (name, label) in enumerate(panels):
        column = index % 3
        row = index // 3
        x = 24 + column * 580
        y = 108 + row * 620
        draw.rounded_rectangle(
            (x, y, x + 555, y + 595),
            radius=18,
            fill=(20, 21, 23),
            outline=(93, 74, 43),
            width=2,
        )
        canvas.paste(fit(HERE / name, (525, 530)), (x + 15, y + 15))
        draw.text(
            (x + 22, y + 555),
            label,
            font=font(20, "Bold"),
            fill=(223, 174, 78),
        )
    phone_x = 1780
    draw.rounded_rectangle(
        (phone_x, 108, phone_x + 595, 1323),
        radius=22,
        fill=(20, 21, 23),
        outline=(93, 74, 43),
        width=2,
    )
    canvas.paste(
        fit(HERE / "shipping-phone.png", (565, 1120)),
        (phone_x + 15, 123),
    )
    draw.text(
        (phone_x + 22, 1256),
        "SHIPPING STOREFRONT · SIMULATOR",
        font=font(18, "Bold"),
        fill=(223, 174, 78),
    )
    contact = HERE / "shipping-review-contact-sheet.png"
    canvas.save(contact)
    assets[contact.name] = {
        "source": "generated from Gate 12 evidence",
        "sha256": sha256(contact),
        "dimensions": list(canvas.size),
        "sizeBytes": contact.stat().st_size,
    }

    mechanism_canvas = Image.new("RGB", (1700, 820), (8, 9, 10))
    mechanism_draw = ImageDraw.Draw(mechanism_canvas)
    mechanism_draw.text(
        (30, 20),
        "SHIPPING BACK MECHANISM",
        font=font(32, "Bold"),
        fill=(237, 224, 199),
    )
    mechanism_draw.text(
        (30, 62),
        "Top-card underside isolates the rebuilt 7.590 mm-clearance track.",
        font=font(18, "Regular"),
        fill=(155, 158, 162),
    )
    for index, (name, label) in enumerate((
        ("shipping-back.png", "ASSEMBLED BACK"),
        ("shipping-track-closeup.png", "TOP-CARD TRACK CLOSEUP"),
    )):
        x = 24 + index * 830
        y = 105
        mechanism_draw.rounded_rectangle(
            (x, y, x + 805, y + 685),
            radius=18,
            fill=(20, 21, 23),
            outline=(93, 74, 43),
            width=2,
        )
        mechanism_canvas.paste(
            fit(HERE / name, (775, 610)),
            (x + 15, y + 15),
        )
        mechanism_draw.text(
            (x + 22, y + 642),
            label,
            font=font(20, "Bold"),
            fill=(223, 174, 78),
        )
    mechanism_contact = HERE / "shipping-mechanism-contact-sheet.png"
    mechanism_canvas.save(mechanism_contact)
    assets[mechanism_contact.name] = {
        "source": "generated from Gate 12 mechanism evidence",
        "sha256": sha256(mechanism_contact),
        "dimensions": list(mechanism_canvas.size),
        "sizeBytes": mechanism_contact.stat().st_size,
    }

    report = {
        "modelId": "magnetic-fan-card",
        "gate": "12-shipping",
        "assets": assets,
        "tests": tests,
        "guardrails": {
            "fullValidator": "ALL PASS",
            "trackClearanceMm": 7.590,
            "mechanismFbxRebuilt": True,
        },
        "banner": {
            "assetName": "product-banner-magnetic-fan-card",
            "sourceRevision": "09-environment/rev-005",
            "aspectPolicy": "scaledToFit at 1179:654",
            "screenSpaceParticles": 0,
        },
        "built": False,
        "installed": False,
        "deviceValidated": False,
        "visualApprovalPending": True,
    }
    (HERE / "shipping-evidence-report.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8")


if __name__ == "__main__":
    main()
