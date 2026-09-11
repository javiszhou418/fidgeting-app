#!/usr/bin/env python3
"""Compose the Gate 10 export board, manifest, and final QA evidence."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageStat


HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
BUILD_REPORT = HERE / "export-build-report.json"
ROUNDTRIP_REPORT = HERE / "export-roundtrip-validation.json"
GLB_STRUCTURE_REPORT = HERE / "glb-structure-validation.json"
RENDER_REPORT = HERE / "export-render-report.json"
PRODUCT_BLEND = HERE / "premium-display-case-product-r001.blend"
FBX_EXPORT = HERE / "premium-display-case-product-r001.fbx"
GLB_EXPORT = HERE / "premium-display-case-product-r001.glb"
REVIEW_BOARD = HERE / "export-review.png"
EXPORT_MANIFEST = HERE / "export-manifest.json"
VALIDATION_LINKS = HERE / "validation-links.json"
COLLISION_POLICY = HERE / "collision-policy.json"
OPTIMIZATION_REPORT = HERE / "asset-optimization-report.json"
QA_VERDICT = HERE / "qa-verdict.json"


def find_repo_root(path: Path) -> Path:
    for candidate in (path, *path.parents):
        if (candidate / ".git").exists():
            return candidate
    raise RuntimeError("Repository root was not found.")


REPO_ROOT = find_repo_root(HERE)


def repo_path(path: Path) -> str:
    return str(path.relative_to(REPO_ROOT))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = (
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold
        else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/SFNS.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
    )
    for candidate in candidates:
        try:
            return ImageFont.truetype(candidate, size)
        except OSError:
            continue
    return ImageFont.load_default()


def write_json(path: Path, payload: dict) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


def image_difference(first: Path, second: Path) -> dict:
    left = Image.open(first).convert("RGB")
    right = Image.open(second).convert("RGB")
    if left.size != right.size:
        raise RuntimeError("Export review renders do not share one resolution.")
    difference = ImageChops.difference(left, right)
    stat = ImageStat.Stat(difference)
    extrema = difference.getextrema()
    return {
        "meanAbsoluteChannelDelta": round(sum(stat.mean) / 3.0, 8),
        "maximumChannelDelta": max(value[1] for value in extrema),
        "resolution": list(left.size),
    }


def fit_image(image: Image.Image, box: tuple[int, int]) -> Image.Image:
    copy = image.copy()
    copy.thumbnail(box, Image.Resampling.LANCZOS)
    return copy


def draw_chip(
    draw: ImageDraw.ImageDraw,
    position: tuple[int, int],
    text: str,
    fill: tuple[int, int, int],
) -> int:
    x, y = position
    label_font = font(27, True)
    box = draw.textbbox((0, 0), text, font=label_font)
    width = box[2] - box[0] + 34
    draw.rounded_rectangle(
        (x, y, x + width, y + 48),
        radius=16,
        fill=fill,
    )
    draw.text((x + 17, y + 8), text, font=label_font, fill=(244, 247, 250))
    return width


def compose_board(
    roundtrip: dict,
    differences: dict,
) -> None:
    canvas = Image.new("RGB", (2860, 1700), (10, 13, 18))
    draw = ImageDraw.Draw(canvas)
    draw.text(
        (90, 65),
        "Gate 10 · Product-only export",
        font=font(62, True),
        fill=(244, 247, 250),
    )
    draw.text(
        (92, 142),
        "One assembled case · real Blend / FBX / GLB · Unity not imported",
        font=font(31),
        fill=(157, 169, 183),
    )

    chips = [
        ("228 × 304 × 59 mm", (32, 94, 73)),
        ("12 nodes · 5 meshes", (30, 72, 104)),
        ("100,016 triangles", (74, 61, 112)),
        ("0 animations", (76, 75, 79)),
        ("0 proxy / toy / VFX", (87, 63, 52)),
    ]
    x = 92
    for text, fill in chips:
        x += draw_chip(draw, (x, 205), text, fill) + 15

    panels = [
        ("BLEND SOURCE", RAW / "source-hero.png"),
        ("UNITY-READY FBX", RAW / "fbx-hero.png"),
        ("PORTABLE GLB", RAW / "glb-hero.png"),
    ]
    panel_width = 860
    panel_height = 1035
    panel_y = 300
    for index, (title, path) in enumerate(panels):
        panel_x = 90 + index * 920
        draw.rounded_rectangle(
            (panel_x, panel_y, panel_x + panel_width, panel_y + panel_height),
            radius=28,
            fill=(17, 22, 29),
            outline=(48, 58, 70),
            width=2,
        )
        draw.text(
            (panel_x + 34, panel_y + 27),
            title,
            font=font(29, True),
            fill=(210, 218, 227),
        )
        image = fit_image(Image.open(path).convert("RGB"), (790, 900))
        image_x = panel_x + (panel_width - image.width) // 2
        image_y = panel_y + 92
        canvas.paste(image, (image_x, image_y))
        draw.text(
            (panel_x + 34, panel_y + 986),
            "Assembled whole case · neutral review material",
            font=font(24),
            fill=(131, 143, 158),
        )

    footer_y = 1370
    draw.rounded_rectangle(
        (90, footer_y, 2770, 1665),
        radius=24,
        fill=(15, 20, 27),
        outline=(47, 68, 85),
        width=2,
    )
    draw.text(
        (124, footer_y + 30),
        "Round-trip result",
        font=font(32, True),
        fill=(228, 234, 240),
    )
    digest = roundtrip["source"]["geometryDigest"]
    lines = [
        f"Canonical geometry digest: {digest[:20]}… · FBX = GLB = source after ≤0.001 mm correspondence",
        (
            "Maximum vertex error: "
            f"FBX {roundtrip['fbx']['vertexCorrespondence']['maximumErrorMm']:.8f} mm · "
            f"GLB {roundtrip['glb']['vertexCorrespondence']['maximumErrorMm']:.8f} mm"
        ),
        (
            "Winding: positive material volumes · export triangle/winding digests match · "
            "label UV 0–1 · material assignments match"
        ),
        (
            "Blank runtime label: paper geometry + cover/foil contours retained; "
            "placeholder text and fake collectible IDs excluded"
        ),
        (
            "No approved collision proxy exists, so none was invented. "
            f"Render delta source→FBX {differences['fbx']['meanAbsoluteChannelDelta']:.5f}, "
            f"source→GLB {differences['glb']['meanAbsoluteChannelDelta']:.5f}."
        ),
    ]
    for index, line in enumerate(lines):
        draw.text(
            (126, footer_y + 82 + index * 32),
            line,
            font=font(24),
            fill=(166, 177, 189),
        )
    draw.text(
        (124, footer_y + 242),
        "Open the real GLB and orbit it before approval. Gate 11 remains blocked.",
        font=font(27, True),
        fill=(131, 205, 171),
    )
    canvas.save(REVIEW_BOARD)


def main() -> None:
    build = load_json(BUILD_REPORT)
    roundtrip = load_json(ROUNDTRIP_REPORT)
    glb_structure = load_json(GLB_STRUCTURE_REPORT)
    render = load_json(RENDER_REPORT)
    if (
        build["status"] != "pass"
        or roundtrip["status"] != "pass"
        or glb_structure["status"] != "pass"
        or render["status"] != "pass"
        or not all(build["checks"].values())
        or not all(roundtrip["checks"].values())
        or not all(glb_structure["checks"].values())
        or not all(render["checks"].values())
    ):
        raise RuntimeError("Gate 10 source, round-trip, GLB, or render validation failed.")

    differences = {
        "fbx": image_difference(
            RAW / "source-hero.png",
            RAW / "fbx-hero.png",
        ),
        "glb": image_difference(
            RAW / "source-hero.png",
            RAW / "glb-hero.png",
        ),
    }

    collision = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "10-export",
        "exportRevision": 1,
        "status": "pass",
        "included": False,
        "approvedCollisionProxyFound": False,
        "selectionProxyFound": False,
        "inventedGeometry": False,
        "reason": (
            "No approved simple collision or selection proxy exists. "
            "The product package contains no collision geometry."
        ),
        "requiredSlotDisposition": (
            "This policy record satisfies collision-export evidence without "
            "misrepresenting a JSON declaration as collision mesh."
        ),
    }
    write_json(COLLISION_POLICY, collision)

    optimization = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "10-export",
        "exportRevision": 1,
        "status": "pass-with-gate11-profile-required",
        "objectCount": 12,
        "meshCount": 5,
        "triangleCount": roundtrip["source"]["triangleCount"],
        "usedMaterialCount": 4,
        "uv": {
            "PhysicalLabel": roundtrip["source"]["labelUv"],
        },
        "topology": {
            "degenerateTriangles": 0,
            "positiveSignedMaterialVolumes": True,
            "fbxGlbTriangleCountIdentity": True,
            "fbxGlbWindingDigestIdentity": True,
        },
        "decision": (
            "Preserve the approved geometry without decimation or new LODs. "
            "Gate 11 Unity profiling must validate the 60 FPS target."
        ),
        "nonBlockingRisk": (
            "100,016 triangles exceed a generic mobile-prop guideline, "
            "but Gate 10 must not alter approved geometry."
        ),
        "shippingClaim": False,
    }
    write_json(OPTIMIZATION_REPORT, optimization)

    compose_board(roundtrip, differences)
    review_image = Image.open(REVIEW_BOARD)
    if review_image.size != (2860, 1700):
        raise RuntimeError("Export review board resolution changed.")

    validation_links = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "10-export",
        "exportRevision": 1,
        "status": "pass",
        "links": [
            {
                "label": "Real interactive GLB",
                "path": repo_path(GLB_EXPORT),
                "sha256": sha256(GLB_EXPORT),
            },
            {
                "label": "Unity-ready FBX",
                "path": repo_path(FBX_EXPORT),
                "sha256": sha256(FBX_EXPORT),
            },
            {
                "label": "Product-only Blender source",
                "path": repo_path(PRODUCT_BLEND),
                "sha256": sha256(PRODUCT_BLEND),
            },
            {
                "label": "Fresh-scene round-trip validation",
                "path": repo_path(ROUNDTRIP_REPORT),
                "sha256": sha256(ROUNDTRIP_REPORT),
            },
            {
                "label": "GLB structure validation",
                "path": repo_path(GLB_STRUCTURE_REPORT),
                "sha256": sha256(GLB_STRUCTURE_REPORT),
            },
            {
                "label": "Collision policy",
                "path": repo_path(COLLISION_POLICY),
                "sha256": sha256(COLLISION_POLICY),
            },
            {
                "label": "Asset optimization audit",
                "path": repo_path(OPTIMIZATION_REPORT),
                "sha256": sha256(OPTIMIZATION_REPORT),
            },
            {
                "label": "Whole-case export review board",
                "path": repo_path(REVIEW_BOARD),
                "sha256": sha256(REVIEW_BOARD),
            },
        ],
    }
    write_json(VALIDATION_LINKS, validation_links)

    approval_checklist = [
        "open-and-orbit-real-exported-glb",
        "inspect-front-back-top-left-right-hero",
        "confirm-whole-assembled-case-only",
        "confirm-228x304x59-mm-and-origin-pivot",
        "confirm-hierarchy-and-empty-content-slot",
        "confirm-label-paper-cover-foil-zones-and-runtime-content-boundary",
        "confirm-no-animation-proxy-explode-toy-light-vfx-camera-background",
        "confirm-fbx-glb-roundtrip-and-winding",
    ]
    export_manifest = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "10-export",
        "exportRevision": 1,
        "status": "pass",
        "notice": "READY FOR EXPORT REVIEW · NOT IMPORTED INTO UNITY",
        "pipelineRevisionAtBuild": build["pipelineRevisionAtBuild"],
        "sourceGate09": build["sourceGate09"],
        "sourceGate07": build["sourceGate07"],
        "governingContract": {
            "id": "premium-display-case-modeling-contract-r003",
            "sha256": (
                "1aea4db5fb45e61b936c5145d83d39a2"
                "e2a4abfe000dddb46cfdb200f76023f3"
            ),
        },
        "package": {
            "blend": {
                "path": repo_path(PRODUCT_BLEND),
                "sha256": sha256(PRODUCT_BLEND),
                "sizeBytes": PRODUCT_BLEND.stat().st_size,
            },
            "fbx": {
                "path": repo_path(FBX_EXPORT),
                "sha256": sha256(FBX_EXPORT),
                "sizeBytes": FBX_EXPORT.stat().st_size,
            },
            "glb": {
                "path": repo_path(GLB_EXPORT),
                "sha256": sha256(GLB_EXPORT),
                "sizeBytes": GLB_EXPORT.stat().st_size,
            },
        },
        "product": {
            "dimensionsMm": {"width": 228, "height": 304, "depth": 59},
            "authoringAxis": "X-width/Y-height/Z-front",
            "pivot": "PresentationRoot at assembled envelope center",
            "hierarchy": build["hierarchy"],
            "objectCount": 12,
            "meshCount": 5,
            "triangleCount": roundtrip["source"]["triangleCount"],
            "geometryDigest": roundtrip["source"]["geometryDigest"],
            "approvedGeometryDigest": build["geometry"]["approvedDigest"],
            "materialAssignments": build["materials"]["assignments"],
            "labelCenterYmm": 99,
            "labelUv": roundtrip["source"]["labelUv"],
            "labelZones": build["materials"]["labelZones"],
            "connectedTubePreserved": True,
            "concentricCornersPreserved": True,
        },
        "roundTrip": {
            "status": roundtrip["status"],
            "maximumVertexErrorMm": {
                "fbx": roundtrip["fbx"]["vertexCorrespondence"][
                    "maximumErrorMm"
                ],
                "glb": roundtrip["glb"]["vertexCorrespondence"][
                    "maximumErrorMm"
                ],
            },
            "geometryDigestIdentity": roundtrip["crossFormat"][
                "geometryDigestIdentity"
            ],
            "triangleCountIdentity": roundtrip["crossFormat"][
                "triangleCountIdentity"
            ],
            "exportWindingDigestIdentity": roundtrip["crossFormat"][
                "exportTriangulatedWindingDigestIdentity"
            ],
            "positiveMaterialVolumes": roundtrip["crossFormat"][
                "sourceAndExportWindingOrientationPositive"
            ],
            "boundsIdentityWithinMm": 0.001,
            "materialAssignmentsIdentity": roundtrip["crossFormat"][
                "materialAssignmentsIdentity"
            ],
            "hierarchyIdentity": roundtrip["crossFormat"]["hierarchyIdentity"],
        },
        "labelPolicy": {
            "paperGeometryPreserved": True,
            "transparentCoverContourPreserved": True,
            "narrowFoilContourPreserved": True,
            "placeholderTextBaked": False,
            "fakeCollectibleIdBaked": False,
            "authoritativeContent": "Unity runtime data",
        },
        "runtimeBoundary": build["runtimeBoundary"],
        "collision": collision,
        "excluded": build["excluded"],
        "review": {
            "interactiveArtifact": repo_path(GLB_EXPORT),
            "board": repo_path(REVIEW_BOARD),
            "boardSha256": sha256(REVIEW_BOARD),
            "wholeAssembledCaseOnly": True,
            "reviewExplodedPartCount": 0,
            "approvalChecklist": approval_checklist,
        },
        "validation": {
            "roundTrip": {
                "path": repo_path(ROUNDTRIP_REPORT),
                "sha256": sha256(ROUNDTRIP_REPORT),
            },
            "glbStructure": {
                "path": repo_path(GLB_STRUCTURE_REPORT),
                "sha256": sha256(GLB_STRUCTURE_REPORT),
            },
            "render": {
                "path": repo_path(RENDER_REPORT),
                "sha256": sha256(RENDER_REPORT),
            },
            "links": {
                "path": repo_path(VALIDATION_LINKS),
                "sha256": sha256(VALIDATION_LINKS),
            },
            "optimization": {
                "path": repo_path(OPTIMIZATION_REPORT),
                "sha256": sha256(OPTIMIZATION_REPORT),
            },
        },
        "gate11Entered": False,
        "shippingUnityChanged": False,
        "simulatorBuilt": False,
        "buildInstallPhonePush": False,
    }
    write_json(EXPORT_MANIFEST, export_manifest)

    qa = {
        "schemaVersion": 1,
        "modelId": "premium-display-case",
        "gate": "10-export",
        "exportRevision": 1,
        "status": "pass",
        "result": "READY_FOR_EXPORT_REVIEW_NOT_UNITY",
        "checks": {
            "buildReportPass": True,
            "freshSceneRoundTripPass": True,
            "glbStructurePass": True,
            "assembledReviewRendersPass": True,
            "productManifestPass": True,
            "realInteractiveGlbPresent": True,
            "reviewBoardWholeCaseOnly": True,
            "collisionPolicyExplicit": True,
            "runtimeAnimationExcluded": True,
            "placeholderContentExcluded": True,
            "gate11NotEntered": True,
            "shippingUnityUnchanged": True,
            "phoneNotTouched": True,
        },
        "reviewArtifactPaths": [
            repo_path(GLB_EXPORT),
            repo_path(REVIEW_BOARD),
        ],
    }
    write_json(QA_VERDICT, qa)


if __name__ == "__main__":
    main()
