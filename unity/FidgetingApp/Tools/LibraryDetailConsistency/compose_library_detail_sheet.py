#!/usr/bin/env python3
"""Pick library / mid-transition / detail frames from each recording and lay
them out as one review sheet.

The entrance start is detected by frame differencing (largest luminance jump
after the library has settled), so Unity boot-time jitter between launches does
not matter.

Usage: compose_library_detail_sheet.py --round r001
"""
from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat

REPO_ROOT = Path(__file__).resolve().parents[4]
OUT_ROOT = REPO_ROOT / "Artifacts" / "LibraryDetailConsistency"
MODELS = [
    ("metal-three-blade", "GEEONE 三叶金属"),
    ("graphite-two-lobe", "石墨双叶"),
    ("magnetic-slide-tile", "磁吸推牌"),
    ("magnetic-fan-card", "磁吸扇牌"),
]
SAMPLE_FPS = 20
LIBRARY_OFFSET_S = -1.0
MID_OFFSET_S = 0.25
DETAIL_OFFSET_S = 2.5


def sample_frames(video: Path, folder: Path) -> list[Path]:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-i", str(video),
         "-vf", f"fps={SAMPLE_FPS},scale=302:-1", str(folder / "s-%04d.png")],
        check=True)
    return sorted(folder.glob("s-*.png"))


def detect_entrance(frames: list[Path]) -> float:
    """Seconds of the first strong frame change after the library has been
    still for at least one second (skips boot and splash)."""
    diffs = []
    prev = None
    for path in frames:
        image = Image.open(path).convert("L")
        diffs.append(0.0 if prev is None
                     else ImageStat.Stat(ImageChops.difference(image, prev)).mean[0])
        prev = image
    # Unity boot (splash → first library frame) lands inside the first ~4 s;
    # only a change after the library has settled can be the entrance.
    # The settled library still breathes (parallax, page dots) at ~0.1-0.7
    # mean diff; the entrance ramps in from ~3 and peaks near 8-10.
    still = 0
    for index, diff in enumerate(diffs):
        if diff < 0.8:
            still += 1
            continue
        if index >= 5 * SAMPLE_FPS and still >= SAMPLE_FPS and diff > 3.0:
            return index / SAMPLE_FPS
        still = 0
    raise RuntimeError("no entrance detected")


def grab(video: Path, seconds: float, out: Path) -> Image.Image:
    subprocess.run(
        ["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{seconds:.3f}",
         "-i", str(video), "-frames:v", "1", str(out)], check=True)
    return Image.open(out).convert("RGB")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--round", required=True)
    args = parser.parse_args()
    round_dir = OUT_ROOT / args.round

    cell_w, cell_h = 300, 652
    pad, header = 12, 44
    sheet = Image.new(
        "RGB",
        (pad + len(MODELS) * (cell_w + pad), header + 3 * (cell_h + pad) + pad),
        (18, 18, 20))
    draw = ImageDraw.Draw(sheet)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 26)
    except OSError:
        font = ImageFont.load_default()

    report = {}
    with tempfile.TemporaryDirectory() as tmp:
        for column, (model, title) in enumerate(MODELS):
            video = round_dir / f"{args.round}-{model}-library-to-detail-clear.mp4"
            sample_dir = Path(tmp) / model
            sample_dir.mkdir()
            entrance = detect_entrance(sample_frames(video, sample_dir))
            times = {
                "library": entrance + LIBRARY_OFFSET_S,
                "mid": entrance + MID_OFFSET_S,
                "detail": entrance + DETAIL_OFFSET_S,
            }
            report[model] = {"entranceSeconds": round(entrance, 2),
                             "frameSeconds": {k: round(v, 2) for k, v in times.items()}}
            x = pad + column * (cell_w + pad)
            draw.text((x, 12), title, fill=(230, 230, 230), font=font)
            for row, key in enumerate(("library", "mid", "detail")):
                still = grab(video, times[key], Path(tmp) / f"{model}-{key}.png")
                still.save(round_dir / f"{args.round}-{model}-{key}.png")
                y = header + row * (cell_h + pad)
                sheet.paste(still.resize((cell_w, cell_h)), (x, y))
                draw.text((x + 8, y + 8), key, fill=(255, 255, 255), font=font)

    out = round_dir / f"{args.round}-library-detail-sheet.png"
    sheet.save(out)
    (round_dir / f"{args.round}-sheet-frames.json").write_text(
        json.dumps(report, indent=2))
    print(out)
    print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
