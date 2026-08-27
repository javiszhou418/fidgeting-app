"""Fail fast when Fan Card modeling reintroduces an approved regression."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROJECT_ROOT = HERE.parents[3]
CONFIG_PATH = HERE / "fan_card_guardrails.json"
BLENDER_SCRIPT = HERE / "build_fan_card_back_mechanism.py"
SPEC_PATH = PROJECT_ROOT / "unity/FidgetingApp/Assets/_FanCard/Runtime/FanCardSpecifications.cs"
BUILDER_PATH = PROJECT_ROOT / "unity/FidgetingApp/Assets/_FanCard/Editor/FanCardSceneBuilder.cs"
TEST_PATH = PROJECT_ROOT / "unity/FidgetingApp/Assets/_FanCard/Tests/Editor/FanCardAcceptanceTests.cs"
SCENE_PATH = PROJECT_ROOT / "unity/FidgetingApp/Assets/_FanCard/Scenes/MagneticFanCard.unity"
REPORT_PATH = PROJECT_ROOT / "Artifacts/FanCardBlenderPreview/fan-card-back-mechanism-report.json"
TESSELLATION_CONTRACT_PATH = (
    PROJECT_ROOT
    / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-fan-card/"
    / "evidence/03-contract/rev-007/modeling-contract.json"
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)
    print(f"[PASS] {message}")


def capture(text: str, pattern: str, label: str) -> tuple[float, ...]:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        raise AssertionError(f"Cannot find {label}")
    return tuple(float(value) for value in match.groups())


def rounded_box_sdf(
    point: tuple[float, float],
    center: tuple[float, float],
    half_size: tuple[float, float],
    radius: float,
) -> float:
    qx = abs(point[0] - center[0]) - (half_size[0] - radius)
    qy = abs(point[1] - center[1]) - (half_size[1] - radius)
    outside = math.hypot(max(qx, 0.0), max(qy, 0.0))
    inside = min(max(qx, qy), 0.0)
    return outside + inside - radius


def minimum_track_clearance(config: dict) -> float:
    card = config["card"]
    track = config["back_track"]
    width = card["width"]
    height = card["height"]
    radius = width * card["corner_radius_ratio"]
    pivot = (width * 0.5 - radius, height * 0.5 - radius)
    center = (-pivot[0], -pivot[1])
    start_x, start_y = track["follower_from_pivot"]
    start_angle = math.atan2(start_y, start_x)
    track_radius = math.hypot(start_x, start_y)
    half_track_width = track["undercut_width"] * 0.5
    samples: list[tuple[float, float]] = []
    for step in range(721):
        angle = start_angle + math.radians(
            track["mechanical_sweep_degrees"] * step / 720.0
        )
        radial = (math.cos(angle), math.sin(angle))
        for offset in (-half_track_width, half_track_width):
            samples.append((
                radial[0] * (track_radius + offset),
                radial[1] * (track_radius + offset),
            ))
    for endpoint_degrees in (0.0, track["mechanical_sweep_degrees"]):
        endpoint_angle = start_angle + math.radians(endpoint_degrees)
        endpoint = (
            math.cos(endpoint_angle) * track_radius,
            math.sin(endpoint_angle) * track_radius,
        )
        for step in range(181):
            cap_angle = 2.0 * math.pi * step / 180.0
            samples.append((
                endpoint[0] + math.cos(cap_angle) * half_track_width,
                endpoint[1] + math.sin(cap_angle) * half_track_width,
            ))
    return min(
        -rounded_box_sdf(
            sample,
            center,
            (width * 0.5, height * 0.5),
            radius,
        )
        for sample in samples
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-only", action="store_true")
    args = parser.parse_args()
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    spec = SPEC_PATH.read_text(encoding="utf-8")
    blender = BLENDER_SCRIPT.read_text(encoding="utf-8")
    builder = BUILDER_PATH.read_text(encoding="utf-8")
    tests = TEST_PATH.read_text(encoding="utf-8")
    track = config["back_track"]
    face = config["face_art"]
    card = config["card"]
    mechanism = config["mechanism"]
    tessellation_contract = json.loads(
        TESSELLATION_CONTRACT_PATH.read_text(encoding="utf-8")
    )

    spec_thickness = capture(
        spec,
        r"CardThickness\s*=\s*([0-9.]+)f",
        "FanCardSpecifications.CardThickness",
    )[0]
    spec_radius = capture(
        spec,
        r"CardCornerRadius\s*=\s*([0-9.]+)f",
        "FanCardSpecifications.CardCornerRadius",
    )[0]
    require(
        abs(spec_thickness * 1000.0 - card["thickness"]) < 1e-6
        and abs(spec_radius * 1000.0 - card["corner_radius"]) < 1e-6,
        "C# card thickness and corner radius match the canonical guardrail",
    )
    spec_corner_segments = capture(
        spec,
        r"VisualCornerSegmentsPerQuadrant\s*=\s*([0-9]+)",
        "FanCardSpecifications.VisualCornerSegmentsPerQuadrant",
    )[0]
    require(
        int(spec_corner_segments)
        == int(card["visual_corner_segments_per_quadrant"])
        == int(
            tessellation_contract["geometry"][
                "visualCornerSegmentsPerQuadrant"
            ]
        )
        == 72,
        "C#, Blender contract, and guardrail lock 72 visible corner segments",
    )
    require(
        "LoadVisualModelPart(" in builder
        and "ConvertAuthoritativeVisualMesh(" in builder
        and "public static void BuildScene()" in builder
        and builder.split("public static void BuildScene()", 1)[1]
            .split('[MenuItem("Tools/Codex/Fan Card/2', 1)[0]
            .count("CreateRoundedBoxMesh(") == 0
        and builder.split("public static void BuildScene()", 1)[1]
            .split('[MenuItem("Tools/Codex/Fan Card/2', 1)[0]
            .count("CreateRoundedSurfaceMesh(") == 0
        and "authoritative 72-segment" in (
            PROJECT_ROOT
            / "unity/FidgetingApp/ArtSource/ModelPipeline/magnetic-fan-card/"
            / "evidence/10-export/rev-003/export_fan_card_smooth_normals.py"
        ).read_text(encoding="utf-8"),
        "Unity body, gold trim, and silver face import the 72-segment Blender FBX",
    )
    spec_black_border = capture(
        spec,
        r"BlackBorderWidth\s*=\s*([0-9.]+)f",
        "FanCardSpecifications.BlackBorderWidth",
    )[0]
    spec_gold_trim = capture(
        spec,
        r"GoldTrimWidth\s*=\s*([0-9.]+)f",
        "FanCardSpecifications.GoldTrimWidth",
    )[0]
    spec_gold_bevel = capture(
        spec,
        r"GoldTrimBevel\s*=\s*([0-9.]+)f",
        "FanCardSpecifications.GoldTrimBevel",
    )[0]
    require(
        abs(spec_black_border * 1000.0 - card["black_border_width"]) < 1e-6
        and abs(spec_gold_trim * 1000.0 - card["gold_trim_width"]) < 1e-6
        and abs(spec_gold_bevel * 1000.0 - card["gold_trim_bevel"]) < 1e-6
        and abs((spec_black_border + spec_gold_trim) * 1000.0
                - card["face_inset"]) < 1e-6
        and "FaceInset = BlackBorderWidth + GoldTrimWidth" in spec,
        "C# black border, gold trim, bevel, and face inset match the guardrail",
    )
    require(
        "CircleIsInsideRoundedRect" in builder
        and "AppendMatchedPerforatedCap" in builder,
        "Unity face projection keeps an enclosed circular spindle opening",
    )
    spec_spindle_radius = capture(
        spec,
        r"RecessedSpindleRadius\s*=\s*([0-9.]+)f",
        "FanCardSpecifications.RecessedSpindleRadius",
    )[0]
    spec_spindle_inset = capture(
        spec,
        r"RecessedSpindleTopInset\s*=\s*([0-9.]+)f",
        "FanCardSpecifications.RecessedSpindleTopInset",
    )[0]
    require(
        abs(spec_spindle_radius - mechanism["spindle_radius"]) < 1e-7
        and abs(spec_spindle_inset - mechanism["spindle_face_inset"]) < 1e-7,
        "C# recessed spindle dimensions match the canonical guardrail",
    )
    spec_cap_radius = capture(
        spec,
        r"BearingCapRadius\s*=\s*([0-9.]+)f",
        "FanCardSpecifications.BearingCapRadius",
    )[0]
    spec_cap_height = capture(
        spec,
        r"BearingCapHeight\s*=\s*([0-9.]+)f",
        "FanCardSpecifications.BearingCapHeight",
    )[0]
    require(
        abs(spec_cap_radius - mechanism["bearing_cap_radius"]) < 1e-7
        and abs(spec_cap_height - mechanism["bearing_cap_height"]) < 1e-7,
        "C# bearing-cap dimensions match the canonical guardrail",
    )

    spec_follower = capture(
        spec,
        r"FollowerFromPivot\s*=\s*\n?\s*new\((-?[0-9.]+)f,\s*(-?[0-9.]+)f\)",
        "FanCardSpecifications.FollowerFromPivot",
    )
    expected_follower = tuple(value / 1000.0 for value in track["follower_from_pivot"])
    require(
        all(abs(actual - expected) < 1e-7 for actual, expected in zip(spec_follower, expected_follower)),
        "C# follower coordinates match the canonical guardrail",
    )
    spec_clearance = capture(
        spec,
        r"MinimumTrackOuterEdgeClearance\s*=\s*([0-9.]+)f",
        "FanCardSpecifications.MinimumTrackOuterEdgeClearance",
    )[0]
    require(
        abs(spec_clearance * 1000.0 - track["minimum_outer_edge_clearance"]) < 1e-6,
        "C# edge-clearance threshold matches the canonical guardrail",
    )
    blender_thickness = capture(
        blender,
        r"CARD_THICKNESS\s*=\s*([0-9.]+)",
        "Blender CARD_THICKNESS",
    )[0]
    blender_radius = capture(
        blender,
        r"CARD_RADIUS\s*=\s*([0-9.]+)",
        "Blender CARD_RADIUS",
    )[0]
    require(
        abs(blender_thickness * 1000.0 - card["thickness"]) < 1e-6
        and abs(blender_radius * 1000.0 - card["corner_radius"]) < 1e-6,
        "Blender card thickness and corner radius match the guardrail",
    )
    blender_follower = capture(
        blender,
        r"FOLLOWER\s*=\s*Vector\(\((-?[0-9.]+),\s*(-?[0-9.]+)\)\)",
        "Blender FOLLOWER",
    )
    require(
        all(abs(actual - expected) < 1e-7 for actual, expected in zip(blender_follower, expected_follower)),
        "Blender follower coordinates match the canonical guardrail",
    )
    require(
        f"SWEEP_DEGREES = {track['mechanical_sweep_degrees']:.1f}" in blender,
        "Blender keeps the 45-degree mechanical sweep",
    )
    clearance = minimum_track_clearance(config)
    require(
        clearance + 1e-6 >= track["minimum_outer_edge_clearance"],
        f"entire track outer contour clears the card edge by {clearance:.3f} mm",
    )
    expected_rank_offsets = [
        tuple(value / 1000.0 for value in offset)
        for offset in face["rank_offsets_from_card_center"]
    ]
    expected_spade_offsets = [
        tuple(value / 1000.0 for value in offset)
        for offset in face["spade_offsets_from_card_center"]
    ]
    spec_art_values = {
        "CornerTopLeftRankOffset": expected_rank_offsets[0],
        "CornerBottomRightRankOffset": expected_rank_offsets[1],
        "CornerTopLeftSpadeOffset": expected_spade_offsets[0],
        "CornerBottomRightSpadeOffset": expected_spade_offsets[1],
    }
    for constant_name, expected in spec_art_values.items():
        actual = capture(
            spec,
            rf"{constant_name}\s*=\s*\n?\s*new\((-?[0-9.]+)f,\s*(-?[0-9.]+)f\)",
            f"FanCardSpecifications.{constant_name}",
        )
        require(
            all(abs(value - target) < 1e-7 for value, target in zip(actual, expected)),
            f"C# {constant_name} matches the canonical face-art coordinates",
        )
    spec_index_count = capture(
        spec,
        r"CornerIndexCountPerFront\s*=\s*([0-9]+);",
        "FanCardSpecifications.CornerIndexCountPerFront",
    )[0]
    require(
        spec_index_count == face["rank_marks_per_front"]
        == face["corner_spades_per_front"]
        == 2,
        "each front uses exactly two diagonal rank and spade corner indices",
    )
    spec_dot_count = capture(
        spec,
        r"DecorativeDotCountPerFront\s*=\s*([0-9]+);",
        "FanCardSpecifications.DecorativeDotCountPerFront",
    )[0]
    require(
        spec_dot_count == face["decorative_dots_per_front"] == 0
        and "EtchedDot_" not in builder
        and 'StartsWith("EtchedDot_")' in tests,
        "front artwork contains no semantically unexplained decorative dots",
    )
    require(
        '"WarmGoldTrim"' in builder
        and '"WarmGoldBackTrim"' in builder
        and "BottomCard_GoldTrim" in builder
        and "GoldTrimOuterWidth" in spec
        and "GoldTrimBevel" in spec
        and '"WarmGoldTrim"' in tests
        and '"WarmGoldBackTrim"' in tests,
        "Unity scene builder attaches the approved beveled gold inlay",
    )
    top_left_rotation = capture(
        spec,
        r"CornerTopLeftRotationDegrees\s*=\s*([0-9.]+)f",
        "FanCardSpecifications.CornerTopLeftRotationDegrees",
    )[0]
    bottom_right_rotation = capture(
        spec,
        r"CornerBottomRightRotationDegrees\s*=\s*([0-9.]+)f",
        "FanCardSpecifications.CornerBottomRightRotationDegrees",
    )[0]
    require(
        [top_left_rotation, bottom_right_rotation]
        == face["corner_index_rotations_degrees"]
        == [0.0, 180.0],
        "lower-right corner index is the 180-degree counterpart of upper-left",
    )
    require(
        all(
            abs(expected_rank_offsets[0][axis] + expected_rank_offsets[1][axis]) < 1e-7
            and abs(expected_spade_offsets[0][axis] + expected_spade_offsets[1][axis]) < 1e-7
            for axis in (0, 1)
        ),
        "corner-index positions are diagonally mirrored around the card center",
    )
    require(
        "controller.Configure(\n                middle.transform,\n                top.transform" in builder,
        "controller moves MiddleCard and TopCard, never BottomCard",
    )
    expected_tracks = ["TopCard", "MiddleCard"]
    expected_followers = ["MiddleCard", "BottomCard"]
    require(
        mechanism["track_layers"] == expected_tracks
        and mechanism["follower_layers"] == expected_followers,
        "canonical assembly locks tracks to top/middle and followers to middle/bottom",
    )
    require(
        '"BottomCard",\n                root.transform' in builder
        and "hasTrack: false,\n                hasFollower: true" in builder
        and '"TopCard",\n                root.transform' in builder
        and "hasTrack: true,\n                hasFollower: false" in builder,
        "scene builder never puts a rear track on BottomCard",
    )
    require(
        '"CommonAxis_RecessedMatteSpindle"' in builder
        and '"CommonAxis_BearingCap_Chrome"' in builder
        and 'new GameObject("CommonAxis_ShadowSleeve")' in builder
        and "create_bearing_cap(" in blender
        and mechanism["front_visible_axis_hardware"]
            == "low_profile_chrome_bearing_cap",
        "axis uses one Blender bearing cap, recessed spindle, and non-rendered marker",
    )
    require(
        'Transform topLayer = root.transform.Find("TopCard")' in builder
        and 'middleLayer.gameObject.SetActive(false)' in builder
        and 'bottomLayer.gameObject.SetActive(false)' in builder,
        "rear-track preview isolates the authored top-card underside",
    )
    require("BackFaceArtwork" not in builder, "builder never copies front art onto the back")
    require("TextMesh" not in builder, "A/Q/K remain Blender relief meshes, not TextMesh")
    require(
        'item.name.StartsWith("RankGlyph_")' in tests
        and 'layer.Find("RankGlyph_TopLeft")' in tests
        and 'layer.Find("RankGlyph_BottomRight")' in tests
        and "Has.Length.EqualTo(6)" in tests,
        "acceptance tests lock two oriented rank indices to each rigid layer",
    )
    require(
        '"CornerSpade_TopLeft"' in builder
        and '"CornerSpade_BottomRight"' in builder
        and "smallSpade.transform.localRotation = indexRotation" in builder,
        "Unity assembly gives each corner spade the same orientation as its rank",
    )
    require(
        face["rank_glyphs"] == ["A", "Q", "K"]
        and face["allowed_patterns"]
        == {"AAA": ["A", "A", "A"], "QKA": ["Q", "K", "A"]}
        and face["layer_order"] == ["BottomCard", "MiddleCard", "TopCard"],
        "canonical face-art contract locks whole-set AAA and bottom/middle/top QKA",
    )
    presenter_path = PROJECT_ROOT / (
        "unity/FidgetingApp/Assets/_FanCard/Runtime/FanCardFaceRankPresenter.cs"
    )
    presenter = presenter_path.read_text(encoding="utf-8")
    require(
        "ApplyLayer(0, FanCardRank.Queen)" in presenter
        and "ApplyLayer(1, FanCardRank.King)" in presenter
        and "ApplyLayer(2, FanCardRank.Ace)" in presenter
        and "UnityEngine.Random.value" in presenter,
        "runtime presenter randomizes complete AAA/QKA sets with Q/K/A layer order",
    )

    if args.source_only:
        print(f"=== FAN CARD SOURCE GUARDRAILS: ALL PASS ({clearance:.3f} mm) ===")
        return 0

    scene = SCENE_PATH.read_text(encoding="utf-8")
    expected_x = f"x: {expected_follower[0]:g}"
    expected_z = f"z: {expected_follower[1]:g}}}"
    require(
        scene.count(expected_x) >= 4 and scene.count(expected_z) >= 4,
        "shipping scene follower seats and balls use the inset coordinates",
    )
    require(
        scene.count("m_Name: RankGlyph_TopLeft\n") == 3
        and scene.count("m_Name: RankGlyph_BottomRight\n") == 3
        and scene.count("m_Name: CornerSpade_TopLeft\n") == 3
        and scene.count("m_Name: CornerSpade_BottomRight\n") == 3,
        "shipping scene has two standard oriented corner indices on every front",
    )
    require(
        "BackFaceArtwork" not in scene
        and "RankGlyph_Back" not in scene
        and "CornerSpade_Back" not in scene,
        "shipping scene has no back-face corner-index artwork",
    )
    report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    report_clearance = report.get("minimum_outer_edge_clearance_mm", -1.0)
    require(
        report_clearance + 1e-6 >= track["minimum_outer_edge_clearance"],
        f"Blender report records {report_clearance:.3f} mm edge clearance",
    )
    require(
        report["mechanical_sweep_degrees"] == track["mechanical_sweep_degrees"],
        "Blender report preserves the mechanical sweep",
    )
    require(
        report["face_art"]["rank_marks_per_front"] == 2
        and report["face_art"]["corner_spades_per_front"] == 2,
        "Blender report records the canonical two-corner face-art contract",
    )
    print(f"=== FAN CARD MODELING GUARDRAILS: ALL PASS ({clearance:.3f} mm) ===")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, FileNotFoundError, KeyError, ValueError) as error:
        print(f"[FAIL] {error}", file=sys.stderr)
        raise SystemExit(1)
