#!/usr/bin/env python3
"""Verify real R029 or R030 iOS Simulator Pack and live-case captures."""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any

from PIL import Image, ImageChops, ImageDraw, ImageFilter, ImageStat


EXPECTED_CASE_ROOT = "PremiumDisplayCaseGate12R004"
EXPECTED_CASE_TYPE = (
    "FidgetingApp.DisplayCase.PremiumDisplayCaseShippingPresentation"
)
UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}"
)


def expect(condition: bool, message: str, failures: list[str]) -> None:
    if not condition:
        failures.append(message)


def load_image(path: Path) -> Image.Image:
    if not path.is_file():
        raise ValueError(f"missing Simulator capture: {path}")
    return Image.open(path).convert("RGBA")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise ValueError(f"missing diagnostic: {path}")
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"diagnostic is not an object: {path}")
    return value


def load_trace(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise ValueError(f"missing trace: {path}")
    events: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        value = json.loads(line)
        if isinstance(value, dict):
            events.append(value)
    if not events:
        raise ValueError(f"trace is empty: {path}")
    return events


def checkpoint(events: list[dict[str, Any]], name: str) -> dict[str, Any]:
    matches = [
        event for event in events
        if event.get("checkpoint") == name
        and event.get("caseRootName") == EXPECTED_CASE_ROOT
    ]
    if not matches:
        raise ValueError(f"trace has no canonical {name} checkpoint")
    return matches[-1]


def frame_quality(image: Image.Image) -> tuple[float, float, float]:
    sample = image.convert("RGB").resize((96, 208))
    values = list(sample.getdata())
    luminance = [
        (red * 0.2126 + green * 0.7152 + blue * 0.0722)
        for red, green, blue in values
    ]
    count = max(len(luminance), 1)
    black = sum(value <= 5 for value in luminance) / count
    white = sum(value >= 250 for value in luminance) / count
    mean = sum(luminance) / count
    return black, white, mean


def mouth_mask(
    image: Image.Image,
    diagnostic: dict[str, Any],
) -> Image.Image:
    bounds = diagnostic.get("mouthBoundsPoints")
    scale = float(diagnostic.get("overlayDisplayScale", 0))
    width = int(diagnostic.get("overlayPixelWidth", 0))
    height = int(diagnostic.get("overlayPixelHeight", 0))
    if (
        not isinstance(bounds, dict)
        or scale <= 0
        or width <= 0
        or height <= 0
    ):
        raise ValueError("overlay diagnostic lacks mouth bounds")
    x_scale = image.width / width
    y_scale = image.height / height
    left = int(float(bounds["x"]) * scale * x_scale)
    top = int(float(bounds["y"]) * scale * y_scale)
    right = int((float(bounds["x"]) + float(bounds["width"])) * scale * x_scale)
    bottom = int((float(bounds["y"]) + float(bounds["height"])) * scale * y_scale)
    mask = Image.new("L", image.size)
    mask.paste(255, (left, top, right, bottom))
    return mask


def swift_number(source: str, name: str) -> float:
    match = re.search(
        rf"\b{re.escape(name)}:\s*(?:Double|CGFloat)\s*=\s*"
        r"(-?[0-9]+(?:\.[0-9]+)?)(?:\s*/\s*"
        r"(-?[0-9]+(?:\.[0-9]+)?))?",
        source,
    )
    if not match:
        raise ValueError(f"missing Swift numeric rule: {name}")
    numerator = float(match.group(1))
    denominator = match.group(2)
    return numerator if denominator is None else numerator / float(denominator)


def pack_mouth_values(
    rules_source: Path,
    components_source: Path,
) -> dict[str, Any]:
    rules = rules_source.read_text(encoding="utf-8")
    components = components_source.read_text(encoding="utf-8")
    edge_offsets_match = re.search(
        r"static let edgeOffsets:\s*\[CGFloat\]\s*=\s*\[(.*?)\]",
        components,
        re.DOTALL,
    )
    if not edge_offsets_match:
        raise ValueError("missing ProductPackTearPath edge offsets")
    edge_offsets = [
        float(value)
        for value in re.findall(
            r"-?[0-9]+(?:\.[0-9]+)?",
            edge_offsets_match.group(1),
        )
    ]
    samples_match = re.search(
        r"static let samples\s*=\s*([0-9]+)",
        components,
    )
    if not samples_match or not edge_offsets:
        raise ValueError("missing ProductPackTearPath samples")
    return {
        "artwork_width": swift_number(rules, "artworkWidthPoints"),
        "canvas_width": swift_number(rules, "authoredCanvasWidth"),
        "canvas_height": swift_number(rules, "authoredCanvasHeight"),
        "opening_inset": swift_number(rules, "openingInsetFraction"),
        "maximum_height": swift_number(
            rules,
            "maximumOpeningHeightPoints",
        ),
        "seal_lift": swift_number(rules, "openingSealLiftPoints"),
        "seam_fraction": swift_number(rules, "authoredSeamYFraction"),
        "tear_commit": swift_number(rules, "tearCommitProgress"),
        "tear_transition": swift_number(
            rules,
            "tearFrontTransitionFraction",
        ),
        "torn_edge_amplitude": swift_number(
            rules,
            "tornEdgeAmplitudePoints",
        ),
        "center_sag": swift_number(components, "openingCenterSag"),
        "samples": int(samples_match.group(1)),
        "edge_offsets": edge_offsets,
    }


def clamp(value: float) -> float:
    return min(max(value, 0.0), 1.0)


def smoothstep(value: float) -> float:
    value = clamp(value)
    return value * value * (3 - 2 * value)


def opening_fraction(
    horizontal_fraction: float,
    progress: float,
    values: dict[str, Any],
) -> float:
    tear = clamp(progress / values["tear_commit"])
    if tear <= 0:
        return 0
    edge = 1 - tear
    half_transition = values["tear_transition"] / 2
    return smoothstep(
        (clamp(horizontal_fraction) - (edge - half_transition))
        / (half_transition * 2)
    )


def pack_frame_points(
    diagnostic: dict[str, Any],
    values: dict[str, Any],
) -> tuple[float, float, float, float]:
    bounds = diagnostic.get("mouthBoundsPoints")
    if not isinstance(bounds, dict):
        raise ValueError("overlay diagnostic lacks mouth bounds")
    width = values["artwork_width"]
    height = width * values["canvas_height"] / values["canvas_width"]
    seam_y = float(bounds["y"]) + 4
    return (
        float(bounds["x"]) - width * values["opening_inset"],
        seam_y - height * values["seam_fraction"],
        width,
        height,
    )


def mouth_polygon_points(
    diagnostic: dict[str, Any],
    image: Image.Image,
    values: dict[str, Any],
    inset: float,
    layer_rendered: bool,
) -> list[tuple[float, float]]:
    pack_x, pack_y, width, height = pack_frame_points(diagnostic, values)
    scale = float(diagnostic.get("overlayDisplayScale", 0))
    overlay_width = int(diagnostic.get("overlayPixelWidth", 0))
    overlay_height = int(diagnostic.get("overlayPixelHeight", 0))
    if scale <= 0 or overlay_width <= 0 or overlay_height <= 0:
        raise ValueError("overlay diagnostic lacks pixel geometry")

    horizontal_inset = min(inset, width * 0.035)
    left = width * values["opening_inset"] + horizontal_inset
    right = width * (1 - values["opening_inset"]) - horizontal_inset
    if right <= left:
        return []

    progress = float(diagnostic.get("tearProgress", 0))
    opening_height = clamp(progress / values["tear_commit"]) * values[
        "maximum_height"
    ]
    points: list[tuple[float, float]] = []

    def append_point(x: float, y: float) -> None:
        pixel_x = (pack_x + x) * scale * image.width / overlay_width
        pixel_y = (pack_y + y) * scale * image.height / overlay_height
        points.append((
            pixel_x,
            image.height - pixel_y if layer_rendered else pixel_y,
        ))

    def mouth_values_at(x: float, sample: int) -> tuple[float, float]:
        canvas_fraction = x / width
        interior_fraction = (
            canvas_fraction - values["opening_inset"]
        ) / (1 - values["opening_inset"] * 2)
        factor = opening_fraction(interior_fraction, progress, values)
        top = height * values["seam_fraction"] - values["seal_lift"] * factor
        torn_edge = (
            top
            + factor * opening_height
            + (math.sin(interior_fraction * math.pi)
               * values["center_sag"] * factor)
            + (values["edge_offsets"][
                sample % len(values["edge_offsets"])
            ] * values["torn_edge_amplitude"] * factor)
        )
        return top, torn_edge

    for sample in range(values["samples"] + 1):
        fraction = sample / values["samples"]
        x = left + (right - left) * fraction
        top, _ = mouth_values_at(x, sample)
        append_point(x, top + inset)
    for sample in range(values["samples"], -1, -1):
        fraction = sample / values["samples"]
        x = left + (right - left) * fraction
        top, torn_edge = mouth_values_at(x, sample)
        append_point(x, max(top + inset, torn_edge - inset))
    return points


def polygon_mask(
    size: tuple[int, int],
    points: list[tuple[float, float]],
) -> Image.Image:
    mask = Image.new("L", size)
    if points:
        ImageDraw.Draw(mask).polygon(points, fill=255)
    return mask


def erode(mask: Image.Image, pixels: int) -> Image.Image:
    return mask.filter(ImageFilter.MinFilter(pixels * 2 + 1))


def dilate(mask: Image.Image, pixels: int) -> Image.Image:
    return mask.filter(ImageFilter.MaxFilter(pixels * 2 + 1))


def exact_mouth_masks(
    image: Image.Image,
    diagnostic: dict[str, Any],
    values: dict[str, Any],
    layer_rendered: bool,
) -> dict[str, Image.Image]:
    inset = min(
        2.1,
        max(
            0,
            clamp(
                float(diagnostic.get("tearProgress", 0))
                / values["tear_commit"]
            ) * values["maximum_height"] * 0.14,
        ),
    )
    outer_points = mouth_polygon_points(
        diagnostic,
        image,
        values,
        inset=0,
        layer_rendered=layer_rendered,
    )
    inset_points = mouth_polygon_points(
        diagnostic,
        image,
        values,
        inset=inset,
        layer_rendered=layer_rendered,
    )
    outer = polygon_mask(image.size, outer_points)
    inner = polygon_mask(image.size, inset_points)
    scale = float(diagnostic["overlayDisplayScale"])
    safety_pixels = max(2, round(scale * 0.75))
    ring = ImageChops.subtract(
        erode(outer, safety_pixels),
        dilate(inner, safety_pixels),
    )
    lip = Image.new("L", image.size)
    if outer_points:
        ImageDraw.Draw(lip).line(
            [*outer_points, outer_points[0]],
            fill=255,
            width=max(1, round(scale)),
            joint="curve",
        )
    pack_x, pack_y, width, height = pack_frame_points(diagnostic, values)
    point_scale_x = scale * image.width / int(
        diagnostic["overlayPixelWidth"]
    )
    point_scale_y = scale * image.height / int(
        diagnostic["overlayPixelHeight"]
    )

    def pack_rect(
        x_fraction: float,
        y_fraction: float,
        width_fraction: float,
        height_fraction: float,
    ) -> Image.Image:
        mask = Image.new("L", image.size)
        top = (pack_y + height * y_fraction) * point_scale_y
        bottom = (
            pack_y + height * (y_fraction + height_fraction)
        ) * point_scale_y
        if layer_rendered:
            top, bottom = image.height - bottom, image.height - top
        ImageDraw.Draw(mask).rectangle((
            (pack_x + width * x_fraction) * point_scale_x,
            top,
            (pack_x + width * (x_fraction + width_fraction)) * point_scale_x,
            bottom,
        ), fill=255)
        return mask

    return {
        "inset": inner,
        "insetInterior": erode(inner, safety_pixels),
        "ring": ring,
        "lip": lip,
        "front": pack_rect(0.22, 0.34, 0.56, 0.50),
        "protectedOuter": pack_rect(0.30, 0.42, 0.40, 0.30),
    }


def mask_pixel_count(mask: Image.Image) -> int:
    return sum(pixel > 0 for pixel in mask.getdata())


def masked_zero_alpha_count(
    overlay: Image.Image,
    mask: Image.Image,
) -> int:
    alpha = overlay.getchannel("A")
    return sum(
        alpha_value <= 8
        for alpha_value, selected in zip(alpha.getdata(), mask.getdata())
        if selected > 0
    )


def masked_luminance_range(
    image: Image.Image,
    mask: Image.Image,
) -> float:
    values = [
        red * 0.2126 + green * 0.7152 + blue * 0.0722
        for (red, green, blue, _), selected in zip(
            image.getdata(),
            mask.getdata(),
        )
        if selected > 0
    ]
    if not values:
        raise ValueError("masked luminance range has no pixels")
    values.sort()
    low = values[round((len(values) - 1) * 0.05)]
    high = values[round((len(values) - 1) * 0.95)]
    return high - low


def masked_difference(
    first: Image.Image,
    second: Image.Image,
    mask: Image.Image,
) -> float:
    delta = ImageChops.difference(first.convert("RGB"), second.convert("RGB"))
    masked = Image.composite(delta.convert("L"), Image.new("L", delta.size), mask)
    statistic = ImageStat.Stat(masked)
    selected = sum(1 for value in mask.getdata() if value > 0)
    if selected == 0:
        raise ValueError("mouth pixel mask is empty")
    return statistic.sum[0] / selected


def check_event(
    event: dict[str, Any],
    name: str,
    revision: str,
    failures: list[str],
) -> None:
    raw_request = str(event.get("rawRequestUUID", ""))
    receipt = str(event.get("receiptUUID", ""))
    expect(
        UUID_PATTERN.fullmatch(raw_request) is not None,
        f"{name} lacks a raw request UUID",
        failures,
    )
    expect(
        receipt == raw_request,
        f"{name} receipt UUID differs from its request UUID",
        failures,
    )
    expect(
        int(event.get("unityFrameCount", -1)) >= 0,
        f"{name} lacks a Unity frame count",
        failures,
    )
    expect(
        event.get("caseRootName") == EXPECTED_CASE_ROOT,
        f"{name} did not stage the canonical case root",
        failures,
    )
    expect(
        event.get("caseTypeName") == EXPECTED_CASE_TYPE,
        f"{name} did not stage the canonical case type",
        failures,
    )
    expect(
        bool(event.get("caseEntityID")),
        f"{name} lacks a case entity ID",
        failures,
    )
    expect(
        int(event.get("caseRendererCount", 0)) > 0,
        f"{name} case has no live renderers",
        failures,
    )
    expect(
        int(event.get("foreignRendererCount", -1)) == 0,
        f"{name} isolation retained a foreign renderer",
        failures,
    )
    expect(
        event.get("caseIsCanonical") is True
        and event.get("caseIsOnlyUnityRenderable") is True
        and (
            event.get("usesCavityClearBackdrop") is True
            if revision == "r030"
            else event.get("unityClearBackdropIsolated") is True
        ),
        f"{name} Unity camera is not canonical-case-only",
        failures,
    )
    if revision == "r030":
        expected_ordinal = {
            "F0": 0,
            "F1": 1,
            "F2": 2,
            "F3": 2,
            "F4": 2,
        }[name]
        expect(
            event.get("candidateRevision") == "R030",
            f"{name} is not an R030 trace event",
            failures,
        )
        expect(
            int(event.get("stableFrameOrdinal", -1)) == expected_ordinal,
            f"{name} has the wrong stable-frame ordinal",
            failures,
        )
        expect(
            int(event.get("cameraInstanceID", 0)) != 0
            and bool(event.get("cameraName")),
            f"{name} lacks the real Unity camera identity",
            failures,
        )
        expect(
            event.get("isolationActive") is True
            and event.get("usesCavityClearBackdrop") is True,
            f"{name} did not reassert active cavity isolation",
            failures,
        )


def check_overlay(
    diagnostic: dict[str, Any],
    name: str,
    ready: bool,
    requires_canonical_case: bool,
    revision: str,
    failures: list[str],
) -> None:
    expect(
        diagnostic.get("hostIsOpaque") is False,
        f"{name} native host is opaque",
        failures,
    )
    expect(
        float(diagnostic.get("hostBackgroundAlpha", 1)) == 0,
        f"{name} native host has a background fill",
        failures,
    )
    if requires_canonical_case:
        expect(
            diagnostic.get("caseRootName") == EXPECTED_CASE_ROOT,
            f"{name} overlay lacks the canonical case root",
            failures,
        )
        expect(
            diagnostic.get("foreignRendererCount") == 0,
            f"{name} overlay reports a foreign Unity renderer",
            failures,
        )
    if revision == "r030":
        expect(
            diagnostic.get("candidateRevision") == "R030",
            f"{name} overlay is not an R030 diagnostic",
            failures,
        )
        expect(
            diagnostic.get("segmentedSealSelected") is True,
            f"{name} did not select the segmented Pack seal",
            failures,
        )
        if name in {"F0", "F1"}:
            expect(
                diagnostic.get("callbackResult") == "pending",
                f"{name} received a native-ready callback too early",
                failures,
            )
        elif name in {"F2", "F3", "F4"}:
            expect(
                diagnostic.get("callbackResult") == "accepted",
                f"{name} lacks an accepted Unity callback result",
                failures,
            )
            expect(
                diagnostic.get("publishSetupPublished") is True
                and diagnostic.get("publishSetupSucceeded") is True
                and not diagnostic.get("publishSetupFailure"),
                f"{name} lacks a successful PublishSetup result",
                failures,
            )
    if name == "F4":
        expect(
            diagnostic.get("packForeground") is False
            and diagnostic.get("nativeUnityCaseReady") is True,
            "F4 removed the Pack before retaining the live case",
            failures,
        )
        return
    if ready:
        expect(
            diagnostic.get("apertureAuthorized") is True,
            f"{name} did not authorize the ready mouth",
            failures,
        )
        if revision != "r030":
            expect(
                diagnostic.get("apertureIsShapedAndBounded") is True,
                f"{name} did not expose a bounded ready mouth",
                failures,
            )
    else:
        expect(
            diagnostic.get("apertureAuthorized") is False
            and diagnostic.get("transparentMouthPixels") == 0
            and diagnostic.get("apertureAlphaIsZero") is True,
            f"{name} exposed a pre-ready Unity aperture",
            failures,
        )


def check_source_guards(args: argparse.Namespace, failures: list[str]) -> None:
    candidate = args.candidate_source.read_text(encoding="utf-8")
    components = args.components_source.read_text(encoding="utf-8")
    coordinator = args.coordinator_source.read_text(encoding="utf-8")
    runner = args.runner_source.read_text(encoding="utf-8")
    revision_name = args.revision.upper()

    expect(
        "Task.sleep" not in candidate,
        f"{revision_name} candidate uses Task.sleep",
        failures,
    )
    expect(
        "Camera.Render" not in candidate,
        f"{revision_name} candidate uses a synthetic camera render",
        failures,
    )
    expect(
        "struct ProductPackPeeledSeal:" not in components,
        "legacy single-strip seal remains active",
        failures,
    )
    expect(
        "private struct ProductPackLid: View" in components
        and "ProductPackSegmentedPeeledSeal" not in components,
        "single rigid lid component is missing",
        failures,
    )
    expect(
        "private struct ProductPackMouthRingShape: Shape" in components
        and ".fill(cavityFill, style: FillStyle(eoFill: true))"
        in components,
        "native Pack lacks an explicit even-odd mouth ring",
        failures,
    )
    expect(
        ".blendMode(.destinationOut)" not in components,
        "native Pack still subtracts its cavity with destinationOut",
        failures,
    )
    expect(
        "ConfirmGachaRevealReadyAfterTwoFrames" in coordinator
        and f"PublishGachaNativeHybrid{revision_name}Trace" in coordinator,
        f"{revision_name} does not trace the coordinator two-frame path",
        failures,
    )
    expect(
        f"if (!activeGachaNativeHybrid{revision_name}Candidate)" in coordinator,
        f"{revision_name} still forces a synthetic isolation render",
        failures,
    )
    expect(
        "markUnityCaseReady" not in runner
        and "Task.sleep" not in runner
        and "Camera.Render" not in runner
        and "UnitySendMessage" not in runner,
        "Simulator harness shortcuts the real bridge",
        failures,
    )
    if args.revision == "r030":
        expect(
            args.isolation_source is not None
            and args.isolation_source.is_file(),
            "R030 isolation source is missing",
            failures,
        )
        if args.isolation_source is None or not args.isolation_source.is_file():
            return
        isolation = args.isolation_source.read_text(encoding="utf-8")
        expect(
            "public void Maintain()" in isolation
            and "RenderPipelineManager.beginCameraRendering" in isolation,
            "R030 lacks pre-render isolation maintenance",
            failures,
        )
        expect(
            "MaintainActiveGachaNativeHybridIsolation" in coordinator,
            "R030 does not maintain isolation before validation",
            failures,
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--revision",
        choices=("r029", "r030"),
        default="r029",
    )
    for name in ("sealed", "partial"):
        parser.add_argument(f"--{name}", type=Path, required=True)
        parser.add_argument(f"--{name}-overlay", type=Path, required=True)
    for name in ("f0", "f1", "f2", "f3", "f4"):
        parser.add_argument(f"--{name}", type=Path, required=True)
        parser.add_argument(f"--{name}-trace", type=Path, required=True)
        parser.add_argument(f"--{name}-overlay", type=Path, required=True)
        parser.add_argument(
            f"--{name}-overlay-alpha",
            type=Path,
            required=True,
        )
    parser.add_argument("--candidate-source", type=Path, required=True)
    parser.add_argument("--components-source", type=Path, required=True)
    parser.add_argument("--rules-source", type=Path, required=True)
    parser.add_argument("--coordinator-source", type=Path, required=True)
    parser.add_argument("--isolation-source", type=Path)
    parser.add_argument("--runner-source", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()

    failures: list[str] = []
    images = {
        name: load_image(getattr(args, name))
        for name in ("f0", "f1", "f2", "f3", "f4")
    }
    visual_images = {
        name: load_image(getattr(args, name))
        for name in ("sealed", "partial")
    }
    overlays = {
        name: load_json(getattr(args, f"{name}_overlay"))
        for name in ("f0", "f1", "f2", "f3", "f4")
    }
    overlay_alpha = {
        name: load_image(getattr(args, f"{name}_overlay_alpha"))
        for name in ("f0", "f1", "f2", "f3", "f4")
    }
    visual_overlays = {
        name: load_json(getattr(args, f"{name}_overlay"))
        for name in ("sealed", "partial")
    }
    traces = {
        name: load_trace(getattr(args, f"{name}_trace"))
        for name in ("f0", "f1", "f2", "f3", "f4")
    }
    events = {
        name.upper(): checkpoint(traces[name], name.upper())
        for name in ("f0", "f1", "f2", "f3", "f4")
    }

    reference_size = images["f0"].size
    for name, image in {**visual_images, **images}.items():
        expect(
            image.size == reference_size
            and image.width >= 600
            and image.height >= 1000,
            f"{name} is not a full-size Simulator frame",
            failures,
        )
        black, white, _ = frame_quality(image)
        expect(
            black < 0.94 and white < 0.94,
            f"{name} is blank, black, or white",
            failures,
        )

    for name in ("f0", "f1", "f2", "f3", "f4"):
        check_event(
            events[name.upper()],
            name.upper(),
            args.revision,
            failures)
        check_overlay(
            overlays[name],
            name.upper(),
            ready=name in {"f2", "f3"},
            requires_canonical_case=True,
            revision=args.revision,
            failures=failures,
        )

    for name, diagnostic in visual_overlays.items():
        check_overlay(
            diagnostic,
            name,
            ready=False,
            requires_canonical_case=False,
            revision=args.revision,
            failures=failures,
        )
    expect(
        float(visual_overlays["sealed"].get("tearProgress", -1)) == 0,
        "sealed Pack did not restore the exact sealed state",
        failures,
    )
    expect(
        abs(float(visual_overlays["partial"].get("tearProgress", -1)) - 0.31)
        <= 0.001,
        "partial Pack did not hold the narrow right-side tear",
        failures,
    )

    f4_events = {
        name: checkpoint(traces["f4"], name)
        for name in ("F1", "F2", "F3", "F4")
    }
    expect(
        f4_events["F2"]["unityFrameCount"]
        == f4_events["F1"]["unityFrameCount"] + 1,
        "F2 did not follow the second WaitForEndOfFrame",
        failures,
    )
    f4_request = f4_events["F1"].get("rawRequestUUID")
    f4_entity = f4_events["F1"].get("caseEntityID")
    expect(
        all(
            event.get("rawRequestUUID") == f4_request
            and event.get("receiptUUID") == f4_request
            and event.get("caseEntityID") == f4_entity
            for event in f4_events.values()
        ),
        "F1–F4 static run changed request or live case identity",
        failures,
    )

    setup_succeeded_key = (
        "publishSetupSucceeded"
        if args.revision == "r030"
        else "setupSucceeded"
    )
    setup_failure_key = (
        "publishSetupFailure"
        if args.revision == "r030"
        else "revealSetupFailure"
    )
    for name in ("F0", "F1"):
        event = events[name]
        expect(
            event.get(setup_succeeded_key) is False
            and event.get("nativeUnityCaseReady") is False
            and event.get("apertureAuthorized") is False,
            f"{name} opened before readiness",
            failures,
        )
    expect(
        events["F1"].get("caseStableFrame") is True
        and events["F1"].get("cameraStableFrame") is True,
        "F1 did not record stable case and camera baselines",
        failures,
    )
    expect(
        events["F2"].get(setup_succeeded_key) is True
        and events["F2"].get("nativeUnityCaseReady") is True
        and events["F2"].get("apertureAuthorized") is True
        and events["F2"].get("caseStableFrame") is True
        and events["F2"].get("cameraStableFrame") is True
        and not events["F2"].get(setup_failure_key),
        "F2 did not publish a clean native-ready result",
        failures,
    )
    expect(
        abs(float(f4_events["F3"].get("nativeHybridProgress", -1)) - 0.58)
        <= 0.02
        and float(f4_events["F3"].get("retreatProgress", -1)) == 0,
        "F3 is not the same case at the Pack-lip crossing",
        failures,
    )
    expect(
        float(f4_events["F4"].get("nativeHybridProgress", -1)) >= 0.99
        and f4_events["F4"].get("packForeground") is False
        and f4_events["F4"].get(setup_succeeded_key) is True,
        "F4 did not retain the live case after Pack departure",
        failures,
    )
    expect(
        all(event.get("crossfadeEnabled") is False for event in events.values()),
        "static checkpoints reported a Pack/case crossfade",
        failures,
    )

    f2_mouth = mouth_mask(images["f2"], overlays["f2"])
    f2_delta = masked_difference(images["f1"], images["f2"], f2_mouth)
    f3_delta = masked_difference(images["f2"], images["f3"], f2_mouth)
    expect(
        f2_delta >= 5,
        "live case pixels did not replace the opaque pre-ready cavity",
        failures,
    )
    expect(
        f3_delta >= 1.5,
        "the live case did not move through the Pack lip",
        failures,
    )
    pack_rules = pack_mouth_values(
        args.rules_source,
        args.components_source,
    )
    f1_masks = exact_mouth_masks(
        overlay_alpha["f1"],
        overlays["f1"],
        pack_rules,
        layer_rendered=True,
    )
    f2_masks = exact_mouth_masks(
        overlay_alpha["f2"],
        overlays["f2"],
        pack_rules,
        layer_rendered=True,
    )
    f2_screen_masks = exact_mouth_masks(
        images["f2"],
        overlays["f2"],
        pack_rules,
        layer_rendered=False,
    )
    f1_exact_inset_zero_alpha = masked_zero_alpha_count(
        overlay_alpha["f1"],
        f1_masks["insetInterior"],
    )
    f2_alpha_measurements = {
        "exactInsetPathPixels": mask_pixel_count(
            f2_masks["insetInterior"]
        ),
        "exactInsetZeroAlphaPixels": masked_zero_alpha_count(
            overlay_alpha["f2"],
            f2_masks["insetInterior"],
        ),
        "ringPixels": mask_pixel_count(f2_masks["ring"]),
        "ringZeroAlphaPixels": masked_zero_alpha_count(
            overlay_alpha["f2"],
            f2_masks["ring"],
        ),
        "lipPixels": mask_pixel_count(f2_masks["lip"]),
        "lipZeroAlphaPixels": masked_zero_alpha_count(
            overlay_alpha["f2"],
            f2_masks["lip"],
        ),
        "frontPixels": mask_pixel_count(f2_masks["front"]),
        "frontZeroAlphaPixels": masked_zero_alpha_count(
            overlay_alpha["f2"],
            f2_masks["front"],
        ),
        "protectedOuterPixels": mask_pixel_count(
            f2_masks["protectedOuter"]
        ),
        "protectedOuterZeroAlphaPixels": masked_zero_alpha_count(
            overlay_alpha["f2"],
            f2_masks["protectedOuter"],
        ),
    }
    f2_exact_inset_delta = masked_difference(
        images["f1"],
        images["f2"],
        f2_screen_masks["insetInterior"],
    )
    f2_ring_delta = masked_difference(
        images["f1"],
        images["f2"],
        f2_screen_masks["ring"],
    )
    f2_inset_luminance_range = masked_luminance_range(
        images["f2"],
        f2_screen_masks["insetInterior"],
    )
    expect(
        f1_exact_inset_zero_alpha == 0,
        "F1 exact inset mouth path contains transparent pixels",
        failures,
    )
    expect(
        f2_alpha_measurements["exactInsetPathPixels"] > 300
        and f2_alpha_measurements["exactInsetZeroAlphaPixels"] > 300,
        "F2 exact inset mouth path lacks 300 transparent pixels",
        failures,
    )
    expect(
        f2_alpha_measurements["ringPixels"] > 0
        and f2_alpha_measurements["ringZeroAlphaPixels"] == 0
        and f2_alpha_measurements["lipPixels"] > 0
        and f2_alpha_measurements["lipZeroAlphaPixels"] == 0
        and f2_alpha_measurements["frontZeroAlphaPixels"] == 0
        and f2_alpha_measurements["protectedOuterZeroAlphaPixels"] == 0,
        "F2 Pack ring, lip, front, or protected outer region lost alpha",
        failures,
    )
    expect(
        f2_exact_inset_delta >= 5
        and f2_inset_luminance_range >= 8,
        "F2 exact inset does not contain live canonical-case pixels",
        failures,
    )
    expect(
        f2_ring_delta <= 3,
        "F2 Pack ring does not occlude the live case",
        failures,
    )
    check_source_guards(args, failures)

    report = {
        "candidate": f"{args.revision.upper()} isolated native hybrid",
        "artifactClass": "real-ios-simulator-unity-player-integration",
        "frames": {
            name: str(getattr(args, name))
            for name in ("sealed", "partial", "f0", "f1", "f2", "f3", "f4")
        },
        "metrics": {
            "f1ToF2MouthDelta": f2_delta,
            "f2ToF3MouthDelta": f3_delta,
            "f1ExactInsetZeroAlphaPixels": f1_exact_inset_zero_alpha,
            "f2ExactInsetAlpha": f2_alpha_measurements,
            "f1ToF2ExactInsetDelta": f2_exact_inset_delta,
            "f1ToF2PackRingDelta": f2_ring_delta,
            "f2ExactInsetLuminanceRange": f2_inset_luminance_range,
            "staticCheckpointFrameCounts": {
                name: events[name]["unityFrameCount"]
                for name in ("F0", "F1", "F2", "F3", "F4")
            },
        },
        "checks": {
            "actualUnityBridge": not any(
                "shortcuts the real bridge" in failure
                for failure in failures
            ),
            "twoEndOfFrameReadiness": (
                f4_events["F2"]["unityFrameCount"]
                == f4_events["F1"]["unityFrameCount"] + 1
            ),
            "canonicalCaseOnly": not any(
                "canonical case" in failure
                or "foreign renderer" in failure
                for failure in failures
            ),
            "preReadyApertureClosed": not any(
                "pre-ready" in failure or "opened before readiness" in failure
                for failure in failures
            ),
            "sameLiveCaseCrossesLip": f3_delta >= 1.5,
            "packDepartsAfterCrossing": (
                float(f4_events["F4"].get("nativeHybridProgress", -1)) >= 0.99
                and f4_events["F4"].get("packForeground") is False
            ),
            "exactInsetPathTransparentAtF2": (
                f2_alpha_measurements["exactInsetPathPixels"] > 300
                and f2_alpha_measurements["exactInsetZeroAlphaPixels"] > 300
            ),
            "packForegroundOpaqueAtF2": (
                f2_alpha_measurements["ringPixels"] > 0
                and f2_alpha_measurements["ringZeroAlphaPixels"] == 0
                and f2_alpha_measurements["lipZeroAlphaPixels"] == 0
                and f2_alpha_measurements["frontZeroAlphaPixels"] == 0
                and f2_alpha_measurements[
                    "protectedOuterZeroAlphaPixels"
                ] == 0
            ),
            "liveCaseInsideExactInsetAtF2": (
                f2_exact_inset_delta >= 5
                and f2_inset_luminance_range >= 8
            ),
            "packRingOccludesCaseAtF2": f2_ring_delta <= 3,
            "noCrossfade": all(
                event.get("crossfadeEnabled") is False
                for event in events.values()
            ),
            "actualUnityCallback": (
                args.revision != "r030"
                or all(
                    overlays[name].get("callbackResult") == "accepted"
                    for name in ("f2", "f3", "f4")
                )
            ),
        },
        "failures": failures,
        "verdict": "pass" if not failures else "fail",
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
