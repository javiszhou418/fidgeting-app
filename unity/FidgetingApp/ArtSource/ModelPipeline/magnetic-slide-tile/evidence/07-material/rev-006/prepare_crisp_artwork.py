#!/usr/bin/env python3
"""Register lossless Gate 07 rev 2 motif reuse for Gate 07 rev 6."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps


OUTPUT = Path(__file__).resolve().parent
REV2 = OUTPUT.parent / "rev-002"
REV3 = OUTPUT.parent / "rev-003"
REV5 = OUTPUT.parent / "rev-005"
CLEAN_SOURCE = REV2 / "source-derived-motif-visual-trace.png"
UPPER = OUTPUT / "artwork-upper-mask.png"
LOWER = OUTPUT / "artwork-lower-mask.png"
REV5_UPPER = REV5 / "artwork-upper-mask.png"
REV5_LOWER = REV5 / "artwork-lower-mask.png"
EXPECTED_CLEAN_SHA256 = "8250df70d2286849db353862283b0d3db9c66e1ac92bed3795bcb5377a431c36"
GEOMETRY_DIGEST = "85bd7dd237c6822c72e575c9a23085eec9a2f28d7afea3a5bf0f13fdc4ebd90f"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metrics(path: Path) -> dict:
    gray = np.asarray(Image.open(path).convert("L"))
    binary = (gray >= 128).astype(np.uint8)
    transitions = cv2.Canny(gray, 64, 192)
    component_count, _, stats, _ = cv2.connectedComponentsWithStats(binary, 8)
    areas = stats[1:, cv2.CC_STAT_AREA] if component_count > 1 else np.array([], dtype=np.int32)
    inverted_count, _, inverted_stats, _ = cv2.connectedComponentsWithStats(1 - binary, 8)
    inverted_areas = inverted_stats[1:, cv2.CC_STAT_AREA] if inverted_count > 1 else np.array([], dtype=np.int32)
    return {
        "sizePx": [int(gray.shape[1]), int(gray.shape[0])],
        "foregroundCoverage": round(float(binary.mean()), 8),
        "intermediatePixelFraction": round(float(np.mean((gray > 0) & (gray < 255))), 8),
        "edgePixelCount": int(np.count_nonzero(transitions)),
        "foregroundConnectedComponents": int(component_count - 1),
        "foregroundComponentsAtLeast8Px": int(np.count_nonzero(areas >= 8)),
        "foregroundTinyComponentsBelow8Px": int(np.count_nonzero(areas < 8)),
        "backgroundConnectedComponents": int(inverted_count - 1),
        "backgroundComponentsAtLeast8Px": int(np.count_nonzero(inverted_areas >= 8)),
        "backgroundTinyComponentsBelow8Px": int(np.count_nonzero(inverted_areas < 8)),
    }


def make_board(clean_metrics: dict, rev5_metrics: dict) -> None:
    canvas = Image.new("RGB", (2200, 1300), (20, 24, 30))
    draw = ImageDraw.Draw(canvas)
    title = ImageFont.load_default(size=34)
    label = ImageFont.load_default(size=22)
    small = ImageFont.load_default(size=17)
    draw.text((54, 34), "GATE 07 REV 6 · CLEAN MOTIF LINEAGE", fill=(244, 246, 250), font=title)
    draw.text((54, 80), "User-authorized reuse of the exact rev 2/3 clean mask; no new exact-trace claim.", fill=(184, 192, 204), font=label)
    panels = [
        ("REV 2/3 CLEAN SOURCE", CLEAN_SOURCE, (54, 130), (80, 210, 146)),
        ("REV 5 REJECTED NOISY TRACE", REV5_UPPER, (584, 130), (226, 104, 104)),
        ("REV 6 ARTWORK_UPPER", UPPER, (1114, 130), (102, 176, 244)),
        ("REV 6 ARTWORK_LOWER", LOWER, (1644, 130), (102, 176, 244)),
    ]
    for heading, path, origin, tint in panels:
        image = ImageOps.contain(Image.open(path).convert("RGB"), (440, 760))
        frame = Image.new("RGB", (460, 780), (39, 45, 55))
        frame.paste(image, ((460 - image.width) // 2, (780 - image.height) // 2))
        canvas.paste(frame, origin)
        draw.text((origin[0], 930), heading, fill=tint, font=label)
        draw.text((origin[0], 968), sha256(path)[:20], fill=(190, 198, 208), font=small)
    draw.text((54, 1050), f"CLEAN components≥8px {clean_metrics['foregroundComponentsAtLeast8Px']} · tiny<8px {clean_metrics['foregroundTinyComponentsBelow8Px']} · edges {clean_metrics['edgePixelCount']}", fill=(80, 210, 146), font=small)
    draw.text((54, 1090), f"REV 5 components≥8px {rev5_metrics['foregroundComponentsAtLeast8Px']} · tiny<8px {rev5_metrics['foregroundTinyComponentsBelow8Px']} · edges {rev5_metrics['edgePixelCount']}", fill=(226, 104, 104), font=small)
    draw.text((54, 1140), "UPPER and LOWER are separate external files and node groups. Initial bytes are intentionally identical.", fill=(208, 214, 224), font=small)
    draw.text((54, 1180), "Lineage: rev 2 asset → unchanged rev 3 shader use → lossless rev 6 slot copies.", fill=(208, 214, 224), font=small)
    canvas.save(OUTPUT / "mask-lineage-sharpness-board.png")


def main() -> None:
    rev2_provenance = json.loads((REV2 / "motif-trace-provenance.json").read_text(encoding="utf-8"))
    rev3_report = json.loads((REV3 / "material-validation.json").read_text(encoding="utf-8"))
    clean_metrics = metrics(CLEAN_SOURCE)
    rev5_metrics = metrics(REV5_UPPER)
    upper_metrics = metrics(UPPER)
    lower_metrics = metrics(LOWER)
    lineage = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 6,
        "reuseClass": "user-authorized-prior-material-design-reuse",
        "notNewExactTraceClaim": True,
        "sourceMaterialRevision": 2,
        "unchangedInMaterialRevision": 3,
        "sourceAssetId": "magnetic-slide-tile-motif-mask-r002",
        "sourcePath": str(CLEAN_SOURCE.relative_to(OUTPUT.parents[7])),
        "sourceSha256": sha256(CLEAN_SOURCE),
        "registeredRev2Sha256": rev2_provenance["outputSha256"],
        "registeredRev3Sha256": rev3_report["materialZones"]["source-derived-dark-etched-motif"]["motifMaskSha256"],
        "rev5RejectedMask": {
            "assetId": "magnetic-slide-tile-artwork-upper-mask-r005",
            "path": str(REV5_UPPER.relative_to(OUTPUT.parents[7])),
            "sha256": sha256(REV5_UPPER),
            "reason": "User rejected the direct original-image trace because the complete motif blurred into noise.",
        },
        "slots": {
            "Artwork_Upper": {
                "path": str(UPPER.relative_to(OUTPUT.parents[7])),
                "sha256": sha256(UPPER),
                "initialIdentity": "lossless-byte-copy-of-rev2-clean-mask",
                "independentlyEditable": True,
            },
            "Artwork_Lower": {
                "path": str(LOWER.relative_to(OUTPUT.parents[7])),
                "sha256": sha256(LOWER),
                "initialIdentity": "lossless-byte-copy-of-rev2-clean-mask",
                "independentlyEditable": True,
                "composition": "same complete clean motif; legible in +21 mm open pose",
            },
        },
        "policy": "Reuse the clean complete rev 2/3 design by explicit user authority. Do not relabel it as a new exact-product trace.",
    }
    (OUTPUT / "artwork-lineage.json").write_text(
        json.dumps(lineage, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    artwork = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 6,
        "geometryDigest": GEOMETRY_DIGEST,
        "reuseClass": lineage["reuseClass"],
        "notNewExactTraceClaim": True,
        "lineageManifest": "artwork-lineage.json",
        "lineageManifestSha256": sha256(OUTPUT / "artwork-lineage.json"),
        "slots": {
            name: {
                "mask": Path(slot["path"]).name,
                "maskSha256": slot["sha256"],
                "independentlyEditable": True,
                "sourceAssetIds": ["magnetic-slide-tile-motif-mask-r002"],
                "sourceClaim": "user-authorized-prior-design-reuse",
            }
            for name, slot in lineage["slots"].items()
        },
        "swapContract": "Artwork_Upper and Artwork_Lower use distinct external paths and node groups. Either file can change without rebuilding mesh.",
    }
    (OUTPUT / "artwork-layers.json").write_text(
        json.dumps(artwork, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    checks = {
        "rev2RegisteredHashMatches": lineage["sourceSha256"] == EXPECTED_CLEAN_SHA256 == lineage["registeredRev2Sha256"],
        "rev3UsedSameHash": lineage["registeredRev3Sha256"] == EXPECTED_CLEAN_SHA256,
        "upperLosslessIdentity": sha256(UPPER) == EXPECTED_CLEAN_SHA256 and UPPER.read_bytes() == CLEAN_SOURCE.read_bytes(),
        "lowerLosslessIdentity": sha256(LOWER) == EXPECTED_CLEAN_SHA256 and LOWER.read_bytes() == CLEAN_SOURCE.read_bytes(),
        "rev5RejectedMaskIsDifferent": sha256(REV5_UPPER) != EXPECTED_CLEAN_SHA256,
        "sharpnessNoWorseThanPrior": upper_metrics == clean_metrics and lower_metrics == clean_metrics,
        "connectedDetailNoWorseThanPrior": (
            upper_metrics["foregroundComponentsAtLeast8Px"] == clean_metrics["foregroundComponentsAtLeast8Px"]
            and lower_metrics["foregroundComponentsAtLeast8Px"] == clean_metrics["foregroundComponentsAtLeast8Px"]
        ),
        "independentPaths": UPPER != LOWER,
    }
    report = {
        "schemaVersion": 1,
        "gate": "07-material",
        "materialRevision": 6,
        "metrics": {
            "rev2Clean": clean_metrics,
            "rev5RejectedUpper": rev5_metrics,
            "rev6Upper": upper_metrics,
            "rev6Lower": lower_metrics,
        },
        "checks": checks,
        "pass": all(checks.values()),
    }
    (OUTPUT / "artwork-lineage-validation.json").write_text(
        json.dumps(report, indent=2) + "\n",
        encoding="utf-8",
    )
    make_board(clean_metrics, rev5_metrics)
    print(json.dumps(report, indent=2))
    if not report["pass"]:
        raise RuntimeError("Gate 07 rev 6 artwork lineage validation failed.")


if __name__ == "__main__":
    main()
