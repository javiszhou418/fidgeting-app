#!/usr/bin/env python3
"""Generate immutable Gate 04 evidence crops from archived exact-product media."""

from pathlib import Path
import subprocess

from PIL import Image


REPO = Path(__file__).resolve().parents[8]
REVISION = Path(__file__).resolve().parent
CROPS = REVISION / "source-crops"
VIDEO = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-001/IMG_5961.MOV"
OFFICIAL_07 = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-002/haloo-official/07.png"
NXEDC_04 = REPO / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-slide-tile/evidence/01-intake/rev-002/external-nxedc/reference-04.jpg"


def video_crop(name: str, timestamp: str, crop: str) -> None:
    subprocess.run(
        [
            "ffmpeg",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            timestamp,
            "-i",
            str(VIDEO),
            "-frames:v",
            "1",
            "-vf",
            f"crop={crop}",
            str(CROPS / name),
        ],
        check=True,
    )


def image_crop(source: Path, name: str, box: tuple[int, int, int, int], width: int) -> None:
    with Image.open(source) as image:
        crop = image.crop(box)
        height = round(crop.height * width / crop.width)
        crop.resize((width, height), Image.Resampling.LANCZOS).save(CROPS / name)


def main() -> None:
    CROPS.mkdir(parents=True, exist_ok=True)

    # The MOV is 1080 × 1920 after its recorded display rotation is applied.
    # These timestamps capture one continuous linear close sequence and one
    # continuous rotation sequence at the most legible viewpoints.
    for timestamp in ("42.00", "42.75", "43.50"):
        video_crop(f"slide-{timestamp}.png", timestamp, "620:1080:70:790")
    for timestamp in ("66.00", "66.50", "67.25"):
        video_crop(f"rotate-{timestamp}.png", timestamp, "760:900:70:970")

    # Tight source crops from the immutable official/NXEDC images.
    image_crop(OFFICIAL_07, "official-fixed-carrier.png", (590, 420, 1065, 920), 700)
    image_crop(OFFICIAL_07, "official-slider-a.png", (190, 275, 690, 720), 720)
    image_crop(OFFICIAL_07, "official-slider-b.png", (645, 55, 1115, 475), 720)
    image_crop(OFFICIAL_07, "official-rotary-pivot.png", (125, 650, 665, 1120), 720)
    image_crop(OFFICIAL_07, "official-interface-plate.png", (35, 990, 480, 1395), 720)
    image_crop(NXEDC_04, "nxedc-open-track.png", (500, 95, 1275, 765), 720)


if __name__ == "__main__":
    main()
