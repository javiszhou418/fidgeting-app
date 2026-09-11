#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


EVIDENCE = Path(__file__).resolve().parent
FRAMES = EVIDENCE / "frames"
CAPTURE = EVIDENCE / "unity-capture-report.json"
TEAR_FRAMES = [18, 54, 68, 81, 89, 94]
HANDOFF_FRAMES = [94, 96, 98, 101, 107, 147]
TECHNICAL_FRAMES = [18, 54, 68, 81, 89, 94, 96, 101, 107, 147]


def main():
    capture = json.loads(CAPTURE.read_text())
    if capture["status"] != "pass":
        raise RuntimeError("Unity capture self-rejected; do not build review media.")
    if (capture["width"], capture["height"], capture["fps"]) != (1206, 2622, 60):
        raise RuntimeError("Capture is not the canonical 1206x2622 at 60 fps.")

    metrics = {row["frame"]: row for row in capture["frameMetrics"]}
    assert_frames()
    build_clean_sheet(
        TEAR_FRAMES,
        EVIDENCE / "primary-tear-material-contact-sheet.png")
    build_clean_sheet(
        HANDOFF_FRAMES,
        EVIDENCE / "primary-continuity-impact-contact-sheet.png")
    build_tear_detail_sheet(
        [54, 68, 81, 89],
        metrics,
        EVIDENCE / "primary-tear-detail-contact-sheet.png")
    build_technical_sheet(
        TECHNICAL_FRAMES,
        metrics,
        EVIDENCE / "technical-continuity-sheet.png")

    videos = [
        encode_video(
            "normal-speed",
            0,
            186,
            60,
            EVIDENCE / "gate04-r010-normal-60fps.mp4"),
        encode_video(
            "tear-slow-motion",
            42,
            55,
            15,
            EVIDENCE / "gate04-r010-tear-quarter-speed.mp4"),
        encode_video(
            "impact-slow-motion",
            92,
            20,
            15,
            EVIDENCE / "gate04-r010-impact-quarter-speed.mp4")
    ]

    stages = [
        {"stage": "intact-seam", "frame": 18},
        {"stage": "tear-front-20", "frame": 54},
        {"stage": "tear-front-50", "frame": 68},
        {"stage": "tear-front-80", "frame": 81},
        {"stage": "curl-and-underside", "frame": 89},
        {"stage": "aperture-same-case-behind", "frame": 94},
        {"stage": "aperture-flash-with-silhouette", "frame": 96},
        {"stage": "same-case-crossing-occluder", "frame": 101},
        {"stage": "pack-gone", "frame": 107},
        {"stage": "hero-settle", "frame": 147}
    ]
    images = []
    for name, frames, role in [
        ("primary-tear-material-contact-sheet.png", TEAR_FRAMES, "primary-clean"),
        ("primary-continuity-impact-contact-sheet.png", HANDOFF_FRAMES, "primary-clean"),
        ("primary-tear-detail-contact-sheet.png", [54, 68, 81, 89], "primary-clean-detail"),
        ("technical-continuity-sheet.png", TECHNICAL_FRAMES, "technical-overlay")
    ]:
        path = EVIDENCE / name
        with Image.open(path) as image:
            images.append({
                "path": relative(path),
                "sha256": sha256(path),
                "width": image.width,
                "height": image.height,
                "sourceUnityFrames": frames,
                "role": role
            })

    manifest = {
        "schema": "premium-display-case-gate04-r010-review-media.v1",
        "source": "actual Unity PlayMode Camera frames",
        "unityCapture": {
            "width": 1206,
            "height": 2622,
            "fps": 60,
            "frames": 186,
            "durationSeconds": 3.10
        },
        "videos": videos,
        "images": images,
        "requiredStoryStages": stages,
        "primaryVisualHasDebugOverlay": False,
        "technicalOverlaySeparate": True,
        "effectsPaintedInPost": False,
        "postRole": "encode Unity frames and compose clean/technical sheets only",
        "shippingReady": False,
        "physicalPhoneInstalled": False
    }
    write_json(EVIDENCE / "review-media-manifest.json", manifest)
    write_json(EVIDENCE / "media-build-report.json", {
        "status": "pass",
        "videos": videos,
        "images": images,
        "requiredStoryStages": stages,
        "checks": {
            "allUnityFramesExist": True,
            "normalSpeedIs60Fps": videos[0]["fps"] == "60/1",
            "slowMotionIs15Fps": all(
                item["fps"] == "15/1" for item in videos[1:]),
            "primarySheetsAreClean": True,
            "technicalSheetIsSeparate": True,
            "noFrameSynthesis": True
        }
    })
    print(json.dumps({
        "status": "pass",
        "videos": [
            (item["id"], item["frames"], item["fps"])
            for item in videos
        ],
        "images": [Path(item["path"]).name for item in images]
    }, indent=2))


def assert_frames():
    expected = [FRAMES / f"frame-{frame:04d}.png" for frame in range(186)]
    missing = [str(path) for path in expected if not path.is_file()]
    if missing:
        raise RuntimeError(f"Missing {len(missing)} Unity frames: {missing[:3]}")


def build_clean_sheet(frames, output):
    tile_width = 402
    tile_height = 874
    sheet = Image.new("RGB", (1206, 1748), (2, 3, 4))
    for index, frame in enumerate(frames):
        with Image.open(frame_path(frame)) as source:
            tile = source.convert("RGB").resize(
                (tile_width, tile_height),
                Image.Resampling.LANCZOS)
        x = (index % 3) * tile_width
        y = (index // 3) * tile_height
        sheet.paste(tile, (x, y))
    sheet.save(output, quality=96)


def build_tear_detail_sheet(frames, metrics, output):
    tile_width = 603
    tile_height = 655
    sheet = Image.new("RGB", (1206, 1310), (2, 3, 4))
    for index, frame in enumerate(frames):
        bounds = metrics[frame]["packProjectedBounds"]
        with Image.open(frame_path(frame)) as source:
            source = source.convert("RGB")
            left = max(0, int((bounds["x"] - 0.10) * source.width))
            right = min(
                source.width,
                int((bounds["x"] + bounds["width"] + 0.10) * source.width))
            top_normalized = 1 - (bounds["y"] + bounds["height"])
            top = max(
                0,
                int((top_normalized - 0.12) * source.height))
            bottom = min(
                source.height,
                int((top_normalized + bounds["height"] * 0.62) * source.height))
            crop = source.crop((left, top, right, bottom))
            crop.thumbnail(
                (tile_width, tile_height),
                Image.Resampling.LANCZOS)
            tile = Image.new("RGB", (tile_width, tile_height), (2, 3, 4))
            tile.paste(
                crop,
                ((tile_width - crop.width) // 2,
                 (tile_height - crop.height) // 2))
        x = (index % 2) * tile_width
        y = (index // 2) * tile_height
        sheet.paste(tile, (x, y))
    sheet.save(output, quality=96)


def build_technical_sheet(frames, metrics, output):
    tile_width = 301
    image_height = 655
    label_height = 88
    sheet = Image.new(
        "RGB",
        (tile_width * 5, (image_height + label_height) * 2),
        (8, 9, 11))
    font = load_font(16)
    small = load_font(13)
    for index, frame in enumerate(frames):
        metric = metrics[frame]
        with Image.open(frame_path(frame)) as source:
            tile = source.convert("RGB").resize(
                (tile_width, image_height),
                Image.Resampling.LANCZOS)
        draw = ImageDraw.Draw(tile)
        bounds = metric["caseProjectedBounds"]
        x0 = int(bounds["x"] * tile_width)
        y0 = int((1 - bounds["y"] - bounds["height"]) * image_height)
        x1 = int((bounds["x"] + bounds["width"]) * tile_width)
        y1 = int((1 - bounds["y"]) * image_height)
        draw.rectangle((x0, y0, x1, y1), outline=(78, 223, 240), width=2)
        tear_x = int(metric["tearFrontViewportX"] * tile_width)
        draw.line((tear_x, 0, tear_x, image_height), fill=(250, 185, 65), width=2)

        label = Image.new("RGB", (tile_width, label_height), (8, 9, 11))
        label_draw = ImageDraw.Draw(label)
        root_id = metric["caseRootEntityId"]
        renderer_ids = metric["caseRendererEntityIds"]
        label_draw.text(
            (7, 5),
            f"F{frame:03d} T{round(frame * 1000 / 60):04d}ms "
            f"tear={metric['tearProgress']:.2f}",
            fill=(238, 236, 228),
            font=font)
        label_draw.text(
            (7, 28),
            f"CASE={root_id} RIDS={len(renderer_ids)} "
            f"{metric['occlusionState']}",
            fill=(78, 223, 240),
            font=small)
        label_draw.text(
            (7, 49),
            "BND "
            f"x={bounds['x']:.3f} y={bounds['y']:.3f} "
            f"w={bounds['width']:.3f} h={bounds['height']:.3f}",
            fill=(196, 200, 204),
            font=small)
        label_draw.text(
            (7, 68),
            f"frontX={metric['tearFrontViewportX']:.3f} "
            f"pack={'ON' if metric['packVisible'] else 'OFF'}",
            fill=(250, 185, 65),
            font=small)

        x = (index % 5) * tile_width
        y = (index // 5) * (image_height + label_height)
        sheet.paste(tile, (x, y))
        sheet.paste(label, (x, y + image_height))
    sheet.save(output, quality=96)


def encode_video(identifier, start_frame, frame_count, frame_rate, output):
    subprocess.run([
        "ffmpeg",
        "-y",
        "-v", "error",
        "-framerate", str(frame_rate),
        "-start_number", str(start_frame),
        "-i", str(FRAMES / "frame-%04d.png"),
        "-frames:v", str(frame_count),
        "-c:v", "libx264",
        "-preset", "slow",
        "-crf", "17",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        str(output)
    ], check=True)
    report = json.loads(subprocess.check_output([
        "ffprobe",
        "-v", "error",
        "-count_frames",
        "-select_streams", "v:0",
        "-show_entries",
        "stream=codec_name,width,height,r_frame_rate,nb_read_frames:"
        "format=duration",
        "-of", "json",
        str(output)
    ]))
    stream = report["streams"][0]
    if (
        stream["codec_name"] != "h264"
        or stream["width"] != 1206
        or stream["height"] != 2622
        or int(stream["nb_read_frames"]) != frame_count
    ):
        raise RuntimeError(f"Unexpected video metadata: {report}")
    return {
        "id": identifier,
        "path": relative(output),
        "sha256": sha256(output),
        "codec": stream["codec_name"],
        "width": stream["width"],
        "height": stream["height"],
        "fps": stream["r_frame_rate"],
        "frames": int(stream["nb_read_frames"]),
        "durationSeconds": float(report["format"]["duration"]),
        "sourceUnityFrames": {
            "first": start_frame,
            "last": start_frame + frame_count - 1
        }
    }


def frame_path(frame):
    return FRAMES / f"frame-{frame:04d}.png"


def load_font(size):
    for candidate in [
        "/System/Library/Fonts/Menlo.ttc",
        "/System/Library/Fonts/Monaco.ttf",
        "/System/Library/Fonts/SFNSMono.ttf"
    ]:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def relative(path):
    repo = EVIDENCE.parents[7]
    return path.resolve().relative_to(repo).as_posix()


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


if __name__ == "__main__":
    main()
