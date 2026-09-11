"""Gate 07 header-label decal for tri-spinner-slab-v3-cmf (system python + Pillow, not bpy).

Prints the label the reference shows on the header plate: title, series line, a hairline rule and a
two-column spec grid. Latin text uses the App's shipping font (Assets/Plugins/iOS/Fonts/
Oxanium-VariableFont_wght.ttf), native kerning, no tracking — the same type rule the Pack artwork
follows (FDB-GAC-009). The copy is PLACEHOLDER copy taken from the V3 concept; the App owns the
real values at runtime (toy name, series, material, weight, S/N, edition).

Output: an RGBA PNG (ink alpha) mapped planar onto GEO_PDC_HEADER_GRAPHITE_PLANE by the lookdev
script, plus a JSON with the layout in plate millimetres.

    python3 tools/blender/make_tri_spinner_slab_label_decal.py --out <dir>
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path(__file__).resolve().parents[2]
FONT = REPO / "unity/FidgetingApp/Assets/Plugins/iOS/Fonts/Oxanium-VariableFont_wght.ttf"
PLATE_W_MM, PLATE_H_MM = 81.48, 40.43           # GEO_PDC_HEADER_GRAPHITE_PLANE front face (Gate 06 rev-011 bounds)
PX_PER_MM = 25.0
INK = (222, 226, 230)                            # light grey ink on the piano-black plate
COPY = {"title": "TRI-SPINNER", "series": "SERIES 01 / TITANIUM",
        "specs": [("MATERIAL", "TITANIUM"), ("WEIGHT", "42.8 G"), ("S/N", "0017"), ("EDITION", "01/500")]}


def font(size_px: float, weight: str):
    f = ImageFont.truetype(str(FONT), int(round(size_px)))
    try:
        f.set_variation_by_name(weight)
    except Exception:                            # FreeType without variation support: default axis
        pass
    return f


def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--out", type=Path, required=True); args = ap.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    W, H = int(PLATE_W_MM * PX_PER_MM), int(PLATE_H_MM * PX_PER_MM)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(im)
    mm = lambda v: v * PX_PER_MM
    margin = mm(6.0)
    # title: cap height ~5.2 mm -> font size ~7.4 mm (Oxanium cap height ~0.7 em)
    f_title = font(mm(7.4), "SemiBold"); f_series = font(mm(3.6), "Medium"); f_spec_label = font(mm(2.6), "Medium"); f_spec_value = font(mm(2.6), "SemiBold")
    y = mm(6.2)
    dr.text((margin, y), COPY["title"], fill=INK, font=f_title); y += mm(9.2)
    dr.text((margin, y), COPY["series"], fill=INK, font=f_series); y += mm(6.6)
    rule_y = y; dr.line([(margin, rule_y), (W - margin, rule_y)], fill=INK + (200,), width=max(1, int(mm(0.18)))); y += mm(4.0)
    col2 = W * 0.56
    label_w = mm(14.0)
    for k, (label, value) in enumerate(COPY["specs"]):
        row = k % 2; col = k // 2
        x = margin if col == 0 else col2
        yy = y + row * mm(4.4)
        dr.text((x, yy), label, fill=INK + (215,), font=f_spec_label)
        dr.text((x + label_w, yy), value, fill=INK, font=f_spec_value)
    out_png = args.out / "header-label-decal.png"; im.save(out_png)
    layout = {"plate_mm": [PLATE_W_MM, PLATE_H_MM], "px_per_mm": PX_PER_MM, "font": str(FONT.relative_to(REPO)), "weights": {"title": "SemiBold", "series": "Medium", "spec_label": "Medium", "spec_value": "SemiBold"},
              "sizes_mm": {"title": 7.4, "series": 3.6, "spec": 2.6}, "margin_mm": 6.0, "rule_y_mm": round(rule_y / PX_PER_MM, 2), "rule_width_mm": 0.18,
              "copy": COPY, "copy_status": "PLACEHOLDER from the V3 concept; runtime-owned values (toy name / series / material / weight / S/N / edition)",
              "ink_srgb": INK, "tracking": "none (native kerning only, per FDB-GAC-009 type rule)"}
    (args.out / "header-label-decal.json").write_text(json.dumps(layout, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps({"png": str(out_png), "size": [W, H]}))


if __name__ == "__main__":
    main()
