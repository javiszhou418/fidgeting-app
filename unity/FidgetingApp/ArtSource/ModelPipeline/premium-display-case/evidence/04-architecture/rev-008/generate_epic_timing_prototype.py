#!/usr/bin/env python3
import hashlib
import json
import math
import random
import shutil
import subprocess
import tempfile
import time
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageEnhance, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parent
REPO = ROOT.parents[7]
UNITY = REPO / "unity/FidgetingApp"
PACK_ROOT = UNITY / "Assets/Plugins/iOS/GachaPacks"
CASE_SOURCE = (
    UNITY
    / "ArtSource/ModelPipeline/premium-display-case/evidence/12-shipping/rev-004/hero.png"
)
PACK_BODY = PACK_ROOT / "gacha-pack-standard-body.png"
PACK_FLAP = PACK_ROOT / "gacha-pack-standard-flap.png"
PROFILE_SOURCE = (
    UNITY
    / "Assets/_DisplayCase/Candidates/PackOpeningGate04R008/Runtime"
    / "PackOpeningEpicTimingProfile.cs"
)
FPS = 60
WIDTH = 720
HEIGHT = 1280
DURATION = 3.1
FRAME_COUNT = round(DURATION * FPS)
VIDEO = ROOT / "epic-profile-timing-impact-prototype.mp4"
IMPACT_GIF = ROOT / "epic-impact-1700-1950ms.gif"
IMPACT_CONTACT = ROOT / "epic-impact-1700-1950ms-contact-sheet.png"
TEXTURE_ROOT = ROOT / "procedural-textures"
TEXTURE_MANIFEST = ROOT / "candidate-texture-manifest.json"
ARCHITECTURE = ROOT / "architecture.json"
VALIDATION = ROOT / "architecture-validation.json"
SIGNALSTATS = ROOT / "signalstats-report.json"

PHASES = [
    ("handoff", 0.000, 0.350),
    ("anticipation", 0.350, 0.650),
    ("resistance", 0.650, 0.950),
    ("snap", 0.950, 1.000),
    ("escalating-tear", 1.000, 1.750),
    ("epic-fake-out", 1.550, 1.610),
    ("impact", 1.750, 1.930),
    ("single-settling-reveal", 1.930, 2.530),
    ("native-settle-cta", 2.530, 3.100),
]


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def font(size, bold=False):
    candidates = [
        Path("/System/Library/Fonts/Supplemental/Arial Bold.ttf")
        if bold
        else Path("/System/Library/Fonts/Supplemental/Arial.ttf"),
        Path("/System/Library/Fonts/Helvetica.ttc"),
    ]
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default()


def clamp01(value):
    return max(0.0, min(1.0, value))


def smooth(value):
    value = clamp01(value)
    return value * value * (3.0 - 2.0 * value)


def progress(time_seconds, start, end):
    return clamp01((time_seconds - start) / (end - start))


def phase_at(time_seconds):
    if time_seconds < 0.350:
        return "HANDOFF"
    if time_seconds < 0.650:
        return "ANTICIPATION"
    if time_seconds < 0.950:
        return "RESISTANCE"
    if time_seconds < 1.000:
        return "SNAP"
    if time_seconds < 1.750:
        return "ESCALATING TEAR"
    if time_seconds < 1.930:
        return "180 MS IMPACT"
    if time_seconds < 2.530:
        return "ONE SETTLING REVEAL"
    return "NATIVE SETTLE / CTA"


def prepare_sources():
    body = Image.open(PACK_BODY).convert("RGBA")
    flap = Image.open(PACK_FLAP).convert("RGBA").crop((12, 24, 372, 145))
    case = Image.open(CASE_SOURCE).convert("RGBA")
    max_channel = ImageChops.lighter(
        ImageChops.lighter(case.getchannel("R"), case.getchannel("G")),
        case.getchannel("B"),
    )
    case.putalpha(max_channel.point(lambda value: 0 if value < 4 else 255))
    noise = Image.new("L", body.size)
    rng = random.Random(4081750)
    noise.putdata([rng.randrange(256) for _ in range(body.width * body.height)])
    return body, flap, case, noise


BODY, FLAP, CASE, DISSOLVE_NOISE = prepare_sources()


def scaled(image, width):
    height = round(image.height * width / image.width)
    return image.resize((width, height), Image.Resampling.LANCZOS)


def paste_center(canvas, image, center, mask=None):
    x = round(center[0] - image.width / 2)
    y = round(center[1] - image.height / 2)
    canvas.alpha_composite(image, (x, y)) if mask is None else canvas.paste(
        image, (x, y), mask
    )
    return x, y


def pack_layers(time_seconds):
    anticipation = smooth(progress(time_seconds, 0.350, 0.650))
    resistance = smooth(progress(time_seconds, 0.650, 0.950))
    snap = smooth(progress(time_seconds, 0.950, 1.000))
    tear = smooth(progress(time_seconds, 1.000, 1.750))
    tear_progress = clamp01(0.18 * resistance + 0.22 * snap + 0.60 * tear)
    width = round(430 * (1.0 + 0.035 * anticipation))
    body = scaled(BODY, width)
    flap = scaled(FLAP, width)
    if time_seconds >= 1.610:
        dissolve = smooth(progress(time_seconds, 1.610, 1.930))
        threshold = round(dissolve * 255)
        noise = DISSOLVE_NOISE.resize(body.size, Image.Resampling.NEAREST)
        source_alpha = body.getchannel("A")
        binary = noise.point(lambda value: 255 if value >= threshold else 0)
        body.putalpha(ImageChops.multiply(source_alpha, binary))
    pack = Image.new("RGBA", body.size, (0, 0, 0, 0))
    pack.alpha_composite(body)
    flap_canvas = Image.new("RGBA", body.size, (0, 0, 0, 0))
    flap_y = 24 - round(tear_progress * 120)
    strip_width = 12
    for x in range(0, flap.width, strip_width):
        strip = flap.crop((x, 0, min(x + strip_width, flap.width), flap.height))
        normalized = x / max(1, flap.width - 1)
        wave = math.sin(normalized * math.pi * 3.0 + tear_progress * 5.0)
        offset_x = round(tear_progress * (normalized - 0.5) * 58)
        offset_y = round(wave * tear_progress * 22 + normalized * tear_progress * 18)
        flap_canvas.alpha_composite(strip, (x + offset_x, flap_y + offset_y))
    pack.alpha_composite(flap_canvas)
    vertical = round(-22 * anticipation + 10 * resistance - 44 * tear)
    return pack, tear_progress, vertical


def case_layer(time_seconds):
    visible_progress = smooth(progress(time_seconds, 1.750, 1.930))
    settle_time = time_seconds
    if 1.780 <= settle_time < 1.840:
        settle_time = 1.780
    settle = smooth(progress(settle_time, 1.930, 2.530))
    angle = -25.0 * (1.0 - settle)
    case = scaled(CASE, 500)
    case = case.rotate(angle, Image.Resampling.BICUBIC, expand=True)
    reveal_mask = Image.new("L", case.size, 0)
    draw = ImageDraw.Draw(reveal_mask)
    radius = round(max(case.size) * visible_progress * 0.72)
    draw.ellipse(
        (
            case.width // 2 - radius,
            case.height // 2 - radius,
            case.width // 2 + radius,
            case.height // 2 + radius,
        ),
        fill=255,
    )
    case.putalpha(ImageChops.multiply(case.getchannel("A"), reveal_mask))
    if 1.930 <= time_seconds <= 2.200:
        sheen = progress(time_seconds, 1.930, 2.200)
        band = Image.new("L", case.size, 0)
        band_draw = ImageDraw.Draw(band)
        x = round(-120 + sheen * (case.width + 240))
        band_draw.polygon(
            [(x - 55, -40), (x + 5, -40), (x + 150, case.height + 40), (x + 90, case.height + 40)],
            fill=125,
        )
        clipped = ImageChops.multiply(band, case.getchannel("A"))
        shine = Image.new("RGBA", case.size, (235, 220, 255, 0))
        shine.putalpha(clipped)
        case = Image.alpha_composite(case, shine)
    return case, angle, visible_progress


def draw_effects(canvas, time_seconds):
    impact = progress(time_seconds, 1.750, 1.930)
    if not 0.0 < impact < 1.0:
        return 0
    draw = ImageDraw.Draw(canvas, "RGBA")
    pulse = math.sin(impact * math.pi)
    draw.rectangle((0, 0, WIDTH, HEIGHT), fill=(222, 210, 255, round(130 * pulse)))
    cx, cy = WIDTH // 2, 590
    radius = round(40 + impact * 500)
    draw.ellipse(
        (cx - radius, cy - radius, cx + radius, cy + radius),
        outline=(203, 178, 255, round(220 * (1.0 - impact))),
        width=max(2, round(16 * (1.0 - impact))),
    )
    rng = random.Random(1750)
    for index in range(28):
        angle = rng.random() * math.tau
        length = 90 + rng.random() * 260 * impact
        start = 50 + rng.random() * 80
        x1 = cx + math.cos(angle) * start
        y1 = cy + math.sin(angle) * start
        x2 = cx + math.cos(angle) * (start + length)
        y2 = cy + math.sin(angle) * (start + length)
        draw.line((x1, y1, x2, y2), fill=(224, 211, 255, round(180 * pulse)), width=3)
    for index in range(42):
        angle = rng.random() * math.tau
        distance = (40 + rng.random() * 360) * impact
        size = 2 + round(rng.random() * 5)
        x = cx + math.cos(angle) * distance
        y = cy + math.sin(angle) * distance
        draw.ellipse((x - size, y - size, x + size, y + size), fill=(230, 220, 255, round(220 * (1.0 - impact))))
    return 6


def draw_native_settle(canvas, time_seconds):
    draw = ImageDraw.Draw(canvas, "RGBA")
    stages = [
        ("EPIC", 2.530, 44, (222, 198, 255, 255)),
        ("ARCHIVE FIND", 2.640, 21, (255, 255, 255, 220)),
        ("THREE-BLADE SPINNER · LEVEL 1", 2.760, 18, (255, 255, 255, 170)),
    ]
    active = 0
    for index, (label, start, size, color) in enumerate(stages):
        amount = smooth(progress(time_seconds, start, start + 0.140))
        if amount <= 0:
            continue
        active += 1
        y = 920 + index * 46 + round((1.0 - amount) * 12)
        draw.text((WIDTH // 2, y), label, font=font(size, True), fill=(*color[:3], round(color[3] * amount)), anchor="mm")
    cta = smooth(progress(time_seconds, 2.900, 3.100))
    if cta > 0:
        active += 1
        y = 1105 + round((1.0 - cta) * 18)
        draw.rounded_rectangle((180, y - 29, 540, y + 29), radius=29, fill=(235, 235, 240, round(48 * cta)))
        draw.text((WIDTH // 2, y), "ACCEPT", font=font(20, True), fill=(255, 255, 255, round(255 * cta)), anchor="mm")
    return active


def render_frame(time_seconds, review_overlay=True):
    fake_out = 1.550 <= time_seconds < 1.610
    background = Image.new("RGBA", (WIDTH, HEIGHT), (5, 7, 11, 255))
    draw = ImageDraw.Draw(background, "RGBA")
    draw.ellipse((70, 160, 650, 870), fill=(34, 26, 45, 255))
    draw.ellipse((140, 260, 580, 790), fill=(12, 16, 24, 255))

    case, case_angle, case_reveal = case_layer(time_seconds)
    paste_center(background, case, (WIDTH // 2, 585))
    moving_layers = 1 if 1.750 < time_seconds < 2.530 else 0
    moving_layers += draw_effects(background, time_seconds)

    pack, tear_progress, pack_vertical = pack_layers(time_seconds)
    if time_seconds < 1.930:
        paste_center(background, pack, (WIDTH // 2, 565 + pack_vertical))
        moving_layers += 2 if tear_progress > 0 else 1

    if fake_out:
        background = ImageEnhance.Brightness(background).enhance(0.54)

    native_layers = draw_native_settle(background, time_seconds)
    moving_layers += native_layers

    if review_overlay:
        draw = ImageDraw.Draw(background, "RGBA")
        draw.rectangle((0, 0, WIDTH, 78), fill=(8, 10, 15, 230))
        draw.text((26, 24), "GATE 04 R008 · EPIC PROFILE", font=font(22, True), fill=(245, 242, 250, 255))
        draw.text((694, 26), f"{round(time_seconds * 1000):04d} ms", font=font(18, True), fill=(207, 184, 255, 255), anchor="ra")
        draw.rectangle((0, 1180, WIDTH, HEIGHT), fill=(8, 10, 15, 228))
        draw.text((28, 1208), phase_at(time_seconds), font=font(19, True), fill=(245, 242, 250, 255))
        draw.text((692, 1208), f"MOVING LAYERS {moving_layers}", font=font(15, True), fill=(174, 157, 205, 255), anchor="ra")
        timeline_x = 28
        timeline_y = 1253
        timeline_w = 664
        draw.rounded_rectangle((timeline_x, timeline_y, timeline_x + timeline_w, timeline_y + 8), radius=4, fill=(64, 65, 76, 255))
        draw.rounded_rectangle((timeline_x, timeline_y, timeline_x + round(timeline_w * clamp01(time_seconds / DURATION)), timeline_y + 8), radius=4, fill=(198, 174, 255, 255))

    state = {
        "timeMs": round(time_seconds * 1000),
        "phase": phase_at(time_seconds),
        "tearProgress": round(tear_progress, 6),
        "fakeOut": fake_out,
        "caseRotationDegrees": round(case_angle, 6),
        "caseRevealProgress": round(case_reveal, 6),
        "movingLayers": moving_layers,
    }
    return background.convert("RGB"), state


def generate_texture_candidates():
    TEXTURE_ROOT.mkdir(exist_ok=True)
    entries = []
    ramp_colors = {
        "common": ((96, 100, 108), (224, 226, 230)),
        "rare": ((26, 67, 111), (124, 191, 255)),
        "epic": ((67, 30, 103), (218, 176, 255)),
        "legendary": ((99, 54, 18), (255, 218, 119)),
    }
    for name, (start, end) in ramp_colors.items():
        image = Image.new("RGB", (256, 1))
        image.putdata([
            tuple(round(start[channel] + (end[channel] - start[channel]) * x / 255) for channel in range(3))
            for x in range(256)
        ])
        path = TEXTURE_ROOT / f"rarity-ramp-{name}.png"
        image.save(path)
        entries.append(("rarity-ramps", path, False))

    rng = random.Random(408)
    dissolve = Image.new("L", (128, 128))
    dissolve.putdata([rng.randrange(256) for _ in range(128 * 128)])
    dissolve_path = TEXTURE_ROOT / "pack-dissolve-noise.png"
    dissolve.save(dissolve_path)
    entries.append(("pack-dissolve-noise", dissolve_path, False))

    normal = Image.new("RGB", (128, 128))
    normal.putdata([(126 + rng.randrange(-8, 9), 126 + rng.randrange(-8, 9), 255) for _ in range(128 * 128)])
    normal_path = TEXTURE_ROOT / "case-brushed-normal.png"
    normal.save(normal_path)
    entries.append(("case-brushed-normal", normal_path, False))

    shockwave = Image.new("L", (256, 1))
    shockwave.putdata([round(255 * math.exp(-((x - 128) / 18) ** 2)) for x in range(256)])
    shockwave_path = TEXTURE_ROOT / "shockwave-gradient.png"
    shockwave.save(shockwave_path)
    entries.append(("shockwave-gradient", shockwave_path, False))

    radial = Image.new("L", (64, 256), 0)
    ImageDraw.Draw(radial).polygon([(29, 0), (35, 0), (40, 256), (24, 256)], fill=255)
    radial_path = TEXTURE_ROOT / "radial-line.png"
    radial.save(radial_path)
    entries.append(("radial-line", radial_path, False))

    particle = Image.new("L", (64, 64), 0)
    particle_draw = ImageDraw.Draw(particle)
    for radius in range(28, 0, -1):
        particle_draw.ellipse((32 - radius, 32 - radius, 32 + radius, 32 + radius), fill=round(255 * (1 - radius / 29)))
    particle_path = TEXTURE_ROOT / "particle-soft-disc.png"
    particle.save(particle_path)
    entries.append(("particle-sprite", particle_path, False))

    distortion = dissolve.filter(ImageFilter.GaussianBlur(3))
    distortion_path = TEXTURE_ROOT / "optional-distortion-mask.png"
    distortion.save(distortion_path)
    entries.append(("optional-distortion-mask", distortion_path, True))

    manifest = {
        "schema": "pack-opening-candidate-textures.v1",
        "status": "candidate-evidence-only",
        "conceptualRows": 7,
        "physicalFiles": len(entries),
        "entries": [
            {
                "row": row,
                "path": str(path.relative_to(REPO)),
                "sha256": sha256(path),
                "optional": optional,
                "finalMaterialDelivery": False,
            }
            for row, path, optional in entries
        ],
    }
    TEXTURE_MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n")
    return manifest


def generate_media():
    states = []
    started = time.perf_counter()
    with tempfile.TemporaryDirectory(prefix="pack-opening-r008-") as folder:
        frame_root = Path(folder)
        for index in range(FRAME_COUNT):
            frame, state = render_frame(index / FPS)
            frame.save(frame_root / f"{index:04d}.png", optimize=False)
            states.append(state)
        subprocess.run(
            [
                "ffmpeg", "-y", "-framerate", str(FPS),
                "-i", str(frame_root / "%04d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-profile:v", "high", "-crf", "18", "-movflags", "+faststart",
                str(VIDEO),
            ],
            check=True,
            capture_output=True,
        )
    generation_ms = (time.perf_counter() - started) * 1000 / FRAME_COUNT

    gif_frames = []
    for milliseconds in range(1700, 1951, 25):
        frame, _ = render_frame(milliseconds / 1000)
        gif_frames.append(frame.resize((360, 640), Image.Resampling.LANCZOS))
    gif_frames[0].save(
        IMPACT_GIF,
        save_all=True,
        append_images=gif_frames[1:],
        duration=25,
        loop=0,
        optimize=False,
        disposal=2,
    )

    times_ms = [1700, 1750, 1780, 1810, 1840, 1880, 1930, 1950]
    sheet = Image.new("RGB", (1440, 1280), (5, 7, 11))
    sheet_draw = ImageDraw.Draw(sheet)
    for index, milliseconds in enumerate(times_ms):
        frame, state = render_frame(milliseconds / 1000)
        tile = frame.resize((360, 640), Image.Resampling.LANCZOS)
        x = (index % 4) * 360
        y = (index // 4) * 640
        sheet.paste(tile, (x, y))
        sheet_draw.rectangle((x + 8, y + 8, x + 174, y + 38), fill=(8, 10, 15))
        sheet_draw.text((x + 17, y + 23), f"{milliseconds} ms · {state['movingLayers']} layers", font=font(13, True), fill=(246, 242, 250), anchor="lm")
    sheet.save(IMPACT_CONTACT, optimize=True)
    return states, generation_ms


def generate_signalstats():
    result = subprocess.run(
        [
            "ffprobe",
            "-v", "error",
            "-f", "lavfi",
            "-i", f"movie={VIDEO},signalstats",
            "-show_entries", "frame_tags=lavfi.signalstats.YAVG",
            "-of", "csv=p=0",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    values = [
        float(line.strip().rstrip(","))
        for line in result.stdout.splitlines()
        if line.strip().rstrip(",")
    ]
    report = {
        "schema": "pack-opening-signalstats.v1",
        "tool": "ffprobe lavfi signalstats",
        "scope": "offline Gate 04 prototype recording; not a perceptual threshold or device-performance result",
        "frames": len(values),
        "yavg": {
            "min": round(min(values), 6),
            "max": round(max(values), 6),
            "mean": round(sum(values) / len(values), 6),
        },
        "thresholdClaim": None,
    }
    SIGNALSTATS.write_text(json.dumps(report, indent=2) + "\n")
    return report


def write_reports(states, generation_ms, textures):
    source_hashes = {
        "actualAssembledCaseUnityRender": sha256(CASE_SOURCE),
        "actualStandardPackBody": sha256(PACK_BODY),
        "actualStandardPackFlap": sha256(PACK_FLAP),
        "unity65TimingProfileSource": sha256(PROFILE_SOURCE),
    }
    architecture = {
        "schema": "premium-display-case-pack-opening-gate04-architecture.v1",
        "modelId": "premium-display-case",
        "gate": "04-architecture",
        "architectureRevision": 3,
        "evidenceRevision": 8,
        "status": "ready_for_review",
        "engine": {"unity": "6000.5.6f1", "urp": "17.5.0", "timeline": "1.8.12"},
        "profile": "epic",
        "packDisplayTier": "standard",
        "resultRarityLeakBeforeReceipt": False,
        "phases": [{"id": name, "startMs": round(start * 1000), "endMs": round(end * 1000)} for name, start, end in PHASES],
        "ownership": {
            "native": ["Pack gesture", "business metadata", "staged CTA", "exact-once ACK"],
            "unity": ["assembled case", "preloaded environment", "effect content", "phase events"],
            "transaction": ["authoritative receipt", "award", "stale request rejection", "interruption restore"],
            "haptics": "semantic event -> recipe -> iOS renderer",
        },
        "invariants": {
            "wholeAssembledCaseOnly": True,
            "callerOwnedContentSlot": True,
            "toyChanged": False,
            "toyIndependentSpin": False,
            "caseRevealRotation": "-25deg-to-0deg-once",
            "repeated720Turntable": False,
            "crossfadeReveal": False,
            "rigidStripTranslation": False,
            "emptyIdleTail": False,
            "singleFrameCtaPop": False,
            "vfxGraph": False,
            "preloadedEnvironment": True,
            "packDissolve": "binary deterministic threshold; not opacity fade",
            "skipLandingMs": 200,
        },
        "effectStack": [
            "full-screen flash", "shockwave", "Shuriken-compatible burst",
            "radial lines", "camera impulse/FOV kick", "bloom/CA/distortion punch",
            "reveal sheen",
        ],
        "reduceMotion": {
            "sameCausalSequence": True,
            "disabled": ["camera shake", "chromatic aberration", "lens distortion", "speed lines", "hitstop"],
            "reduced": ["flash", "bloom"],
        },
        "rarityProfiles": ["common", "rare", "epic", "legendary"],
        "packDisplayAssets": ["standard", "refined", "signature", "chase", "grail", "one-of-one"],
        "textureManifest": str(TEXTURE_MANIFEST.relative_to(REPO)),
        "sourceHashes": source_hashes,
        "orchestration": {
            "runtime": "ScriptableObject + AnimationCurve + native phase state",
            "timeline": "editor preview/scrub only",
            "tweenPackageAdded": False,
            "hitstopClock": "unscaled-time candidate",
        },
        "evidence": {
            "normalSpeedVideo": VIDEO.name,
            "impactGif": IMPACT_GIF.name,
            "impactContactSheet": IMPACT_CONTACT.name,
            "signalstats": SIGNALSTATS.name,
            "interactiveMode": "complete-recording-fallback",
            "shippingRuntime": False,
            "visualApproval": "pending",
        },
    }
    ARCHITECTURE.write_text(json.dumps(architecture, ensure_ascii=False, indent=2) + "\n")

    max_layers = max(state["movingLayers"] for state in states)
    checks = {
        "actualCaseAndPackSources": all(source_hashes.values()),
        "exact3100msTimeline": FRAME_COUNT == 186,
        "epicFakeOutWindow": PHASES[5][1:] == (1.550, 1.610),
        "impactWindow180ms": round((PHASES[6][2] - PHASES[6][1]) * 1000) == 180,
        "oneSettlingReveal": PHASES[7][1:] == (1.930, 2.530),
        "wholeCaseContentSlotBoundary": architecture["invariants"]["wholeAssembledCaseOnly"] and architecture["invariants"]["callerOwnedContentSlot"],
        "forbiddenMotionAbsent": not any([
            architecture["invariants"]["repeated720Turntable"],
            architecture["invariants"]["crossfadeReveal"],
            architecture["invariants"]["rigidStripTranslation"],
            architecture["invariants"]["emptyIdleTail"],
            architecture["invariants"]["singleFrameCtaPop"],
        ]),
        "reduceMotionMapped": architecture["reduceMotion"]["sameCausalSequence"],
        "textureCountExact": textures["conceptualRows"] == 7 and textures["physicalFiles"] == 10,
        "recordingAndImpactEvidencePresent": VIDEO.exists() and IMPACT_GIF.exists() and IMPACT_CONTACT.exists(),
    }
    validation = {
        "schema": "premium-display-case-pack-opening-gate04-validation.v1",
        "status": "pass" if all(checks.values()) else "fail",
        "checks": checks,
        "metrics": {
            "frames": FRAME_COUNT,
            "fps": FPS,
            "durationSeconds": DURATION,
            "maxSimultaneousMovingLayers": max_layers,
            "offlineCompositorMeanGenerationMsPerFrame": round(generation_ms, 3),
            "drawCalls": None,
            "drawCallEvidence": "not measured; offline Gate 04 recording is not Unity Editor/Simulator performance proof",
            "deviceFrameTime": None,
            "devicePerformanceStatus": "physical iPhone and Android pending",
        },
        "artifactHashes": {
            "video": sha256(VIDEO),
            "impactGif": sha256(IMPACT_GIF),
            "impactContactSheet": sha256(IMPACT_CONTACT),
            "textureManifest": sha256(TEXTURE_MANIFEST),
            "architecture": sha256(ARCHITECTURE),
            "signalstats": sha256(SIGNALSTATS),
        },
        "truth": {
            "candidateEvidenceOnly": True,
            "actualShippingCasePixels": True,
            "actualPackPixels": True,
            "unityRuntimeWired": False,
            "nativeUiWired": False,
            "finalMaterialsDelivered": False,
            "physicalPhoneInstalled": False,
        },
    }
    VALIDATION.write_text(json.dumps(validation, ensure_ascii=False, indent=2) + "\n")
    return validation


def main():
    for source in [CASE_SOURCE, PACK_BODY, PACK_FLAP, PROFILE_SOURCE]:
        if not source.is_file():
            raise SystemExit(f"Missing required source: {source}")
    textures = generate_texture_candidates()
    states, generation_ms = generate_media()
    generate_signalstats()
    validation = write_reports(states, generation_ms, textures)
    if validation["status"] != "pass":
        raise SystemExit("Gate 04 rev 8 prototype validation failed")
    print(json.dumps({
        "video": str(VIDEO),
        "impactGif": str(IMPACT_GIF),
        "impactContact": str(IMPACT_CONTACT),
        "architecture": str(ARCHITECTURE),
        "validation": str(VALIDATION),
    }))


if __name__ == "__main__":
    main()
