#!/usr/bin/env python3
"""Build the Gate 10 export manifest, transport audit, and supplemental board."""

from __future__ import annotations

import hashlib
import io
import json
import struct
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


HERE = Path(__file__).resolve().parent
PACKAGE = HERE / "package"
BUILD = json.loads((HERE / "export-build-report.json").read_text())
REIMPORT = json.loads((HERE / "reimport-validation.json").read_text())
BLEND_AUDIT = json.loads((HERE / "authoritative-blend-audit.json").read_text())
TEXTURE_AUDIT = json.loads((HERE / "texture-environment-validation.json").read_text())
GLB = PACKAGE / "magnetic-slide-tile-render-r010.glb"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_glb() -> tuple[dict, bytes]:
    raw = GLB.read_bytes()
    json_length = struct.unpack_from("<I", raw, 12)[0]
    document = json.loads(raw[20:20 + json_length].decode("utf-8").rstrip(" \t\r\n\0"))
    binary_header = 20 + json_length
    binary_length = struct.unpack_from("<I", raw, binary_header)[0]
    binary_start = binary_header + 8
    return document, raw[binary_start:binary_start + binary_length]


def glb_pixel_audit() -> dict:
    document, binary = parse_glb()
    images = {}
    for record in document["images"]:
        view = document["bufferViews"][record["bufferView"]]
        start = view.get("byteOffset", 0)
        payload = binary[start:start + view["byteLength"]]
        name = Path(record["name"]).stem
        expected = PACKAGE / "textures" / f"{name}.png"
        embedded = Image.open(io.BytesIO(payload)).convert("RGBA")
        source = Image.open(expected).convert("RGBA")
        if "roughness" in name:
            embedded_pixels = embedded.tobytes()
            source_pixels = source.tobytes()
            semantic_identity = all(
                embedded_pixels[index + 1] == source_pixels[index]
                and embedded_pixels[index] == 255
                and embedded_pixels[index + 2] == 255
                and embedded_pixels[index + 3] == 255
                for index in range(0, len(embedded_pixels), 4)
            )
            transport = "glTF metallicRoughness: source roughness preserved exactly in G; R/B/A=255"
        else:
            semantic_identity = embedded.tobytes() == source.tobytes()
            transport = "byte-decoded RGBA identity"
        images[name] = {
            "embeddedSha256": hashlib.sha256(payload).hexdigest(),
            "sourceSha256": sha256(expected),
            "dimensions": list(embedded.size),
            "mode": embedded.mode,
            "pixelIdentity": semantic_identity,
            "transport": transport,
        }
    root_node = next(node for node in document["nodes"] if node.get("name") == "MagneticSlideTile_G06_R005")
    extras = root_node.get("extras", {})
    checks = {
        "fourImages": len(images) == 4,
        "pixelIdentity": all(item["pixelIdentity"] for item in images.values()),
        "nativeNpot": all(item["dimensions"] == [620, 1000] for item in images.values()),
        "clampSampler": all(
            sampler.get("wrapS") == 33071 and sampler.get("wrapT") == 33071
            for sampler in document.get("samplers", [])
        ),
        "geometryMetadata": extras.get("canonicalGeometryDigest") == BUILD["approved"]["geometryDigest"],
        "endpointMetadata": extras.get("rotationLockedBelowSMax") is True
            and extras.get("slideLockedAtNonzeroAngle") is True
            and extras.get("detentCount") == 30
            and extras.get("detentStepDegrees") == 12
            and extras.get("rotationAtSMaxDegrees") == 360,
        "noAnimations": not document.get("animations"),
    }
    return {"images": images, "rootExtras": extras, "checks": checks, "pass": all(checks.values())}


def build_board() -> dict:
    hero = Image.open(HERE / "gate10-r010-glb-hero.png").convert("RGB")
    top = Image.open(HERE / "gate10-r010-glb-top.png").convert("RGB")
    board = Image.new("RGB", (1840, 800), (16, 14, 17))
    draw = ImageDraw.Draw(board)
    font = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 26)
    small = ImageFont.truetype("/System/Library/Fonts/SFNS.ttf", 18)
    draw.text((24, 18), "Gate 10 rev 10 · Fresh exported GLB reimport", font=font, fill=(245, 242, 244))
    draw.text(
        (24, 54),
        "Supplemental board — interact with the real GLB for approval",
        font=small,
        fill=(186, 178, 184),
    )
    board.paste(hero, (20, 88))
    board.paste(top, (920, 88))
    output = HERE / "gate10-r010-export-review-board.png"
    board.save(output)
    return {"path": str(output), "sha256": sha256(output), "dimensions": list(board.size)}


def main() -> None:
    glb_audit = glb_pixel_audit()
    board = build_board()
    if not all([BUILD["pass"], REIMPORT["pass"], BLEND_AUDIT["pass"], TEXTURE_AUDIT["pass"], glb_audit["pass"]]):
        raise RuntimeError("A Gate 10 source report failed.")
    hierarchy = json.loads((PACKAGE / "hierarchy-motion-metadata-r010.json").read_text())
    import_contract = json.loads((PACKAGE / "unity-import-contract-r010.json").read_text())
    files = {}
    for path in sorted(PACKAGE.rglob("*")):
        if path.is_file() and path.name != "export-manifest-r010.json":
            files[str(path.relative_to(PACKAGE))] = {
                "sha256": sha256(path),
                "bytes": path.stat().st_size,
            }
    checks = {
        "authoritativeFormats": all(name in files for name in [
            "magnetic-slide-tile-authoritative-r010.blend",
            "magnetic-slide-tile-render-r010.fbx",
            "magnetic-slide-tile-render-r010.glb",
            "magnetic-slide-tile-collision-r010.fbx",
        ]),
        "sourceHashesCurrent": BUILD["source"]["sha256"] == "d4d6a9701281e493b4459d3b1f9a9c67382c3d7b22e21632233184276de8ebf2"
            and BUILD["source"]["gate09ApprovalExactWording"] == "继续",
        "geometryPreserved": BUILD["approved"]["geometryDigest"] == "2fcf6d2b4344511bc6b86ce940a927576f9cdb4988f4022959a3372f4d3c1952",
        "materialStatePreserved": BUILD["before"]["digests"]["materials"] == BUILD["after"]["digests"]["materials"],
        "uvStatePreserved": BUILD["before"]["digests"]["uvs"] == BUILD["after"]["digests"]["uvs"],
        "fbxGlbReimport": REIMPORT["results"]["fbx"]["pass"] and REIMPORT["results"]["glb"]["pass"],
        "collisionSeparate": REIMPORT["results"]["collision"]["pass"],
        "glbPixelIdentity": glb_audit["pass"],
        "endpointInterlock": hierarchy["endpointInterlock"]["rotationLockedBelowSMax"]
            and hierarchy["endpointInterlock"]["slideLockedAtNonzeroAngle"]
            and hierarchy["endpointInterlock"]["rotationAtSMax"] == {
                "degrees": 360,
                "detents": 30,
                "stepDegrees": 12,
            },
        "closedNoAnimation": hierarchy["defaultState"]["pose"] == "closed"
            and hierarchy["defaultState"]["linearVelocityMmPerSecond"] == 0
            and hierarchy["defaultState"]["angularVelocityDegreesPerSecond"] == 0
            and hierarchy["defaultState"]["animationClips"] == 0,
        "environmentCurrent": files["environment/target-shipping-studio-r009.exr"]["sha256"]
            == TEXTURE_AUDIT["copied"]["target-shipping-studio-r009.exr"]["sha256"],
        "astcPlannedNotApplied": not import_contract["astcPlan"]["applied"]
            and not import_contract["scope"]["unityImportApplied"],
        "scope": not BUILD["checks"]["unityNotUsed"] is False,
    }
    manifest = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 10,
        "createdFrom": {
            "gate09Revision": 9,
            "gate09ApprovalExactWording": "继续",
            "sourceBlendSha256": BUILD["source"]["sha256"],
            "geometryDigest": BUILD["approved"]["geometryDigest"],
            "materialSourceSha256": BUILD["approved"]["materialSourceSha256"],
            "mechanismContractSha256": BUILD["approved"]["mechanismContractSha256"],
            "portabilityContractSha256": BUILD["approved"]["portabilityContractSha256"],
        },
        "stateDigests": BUILD["after"]["digests"],
        "boundsMm": BUILD["after"]["bounds"],
        "formats": BUILD["formats"],
        "glbCounts": REIMPORT["results"]["glbStructure"]["counts"],
        "glbTransportAudit": glb_audit,
        "materialPartitions": hierarchy["materials"],
        "endpointInterlock": hierarchy["endpointInterlock"],
        "defaultState": hierarchy["defaultState"],
        "unityImportContract": {
            "path": "unity-import-contract-r010.json",
            "sha256": sha256(PACKAGE / "unity-import-contract-r010.json"),
            "astcApplied": False,
        },
        "files": files,
        "reviewBoard": board,
        "checks": checks,
        "pass": all(checks.values()),
    }
    output = PACKAGE / "export-manifest-r010.json"
    output.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    validation = {
        "schemaVersion": 1,
        "gate": "10-export",
        "revision": 10,
        "manifest": {"path": str(output), "sha256": sha256(output)},
        "glbTransportAudit": glb_audit,
        "checks": checks,
        "pass": manifest["pass"],
    }
    (HERE / "export-manifest-validation.json").write_text(
        json.dumps(validation, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    if not manifest["pass"]:
        raise RuntimeError(json.dumps(validation, ensure_ascii=False, indent=2))
    print(json.dumps({
        "pass": True,
        "manifestSha256": sha256(output),
        "fileCount": len(files),
        "boardSha256": board["sha256"],
    }, indent=2))


if __name__ == "__main__":
    main()
