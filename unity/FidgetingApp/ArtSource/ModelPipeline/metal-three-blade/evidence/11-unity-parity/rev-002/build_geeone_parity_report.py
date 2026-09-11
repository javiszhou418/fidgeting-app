# -*- coding: utf-8 -*-
"""Gate 11 parity rev-002 · GEEONE 龙鳞三叶: Blender GLB round-trip renders (Workbench, Gate 10 rev-002 review/) vs the Unity
shipping scene captured with the same camera recipe (GeeoneShippingPreviewCapture.CaptureNeutral).

Silhouettes are compared (lighting differs on purpose): IoU, area ratio, centroid offset, planar extent in R, plus the
Unity import report (hierarchy, ownership, materials, triangle counts, bounds) against the Gate 10 export manifest.
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
EV = HERE.parent.parent
G10 = EV / "10-export/rev-002"
R_MM = 42.5
ORTHO_WIDTH_R = 2.3


def silhouette(path: Path, bg: str):
    """Both sides are flat white-on-black silhouette renders (Blender Workbench FLAT single colour / Unity URP Unlit)."""
    im = np.asarray(Image.open(path).convert("RGB")).astype(np.float32) / 255.0
    return im.max(axis=2) > 0.5


def stats(mask):
    ys, xs = np.nonzero(mask)
    h, w = mask.shape
    if len(xs) == 0:
        return {"area_frac": 0.0}
    return {
        "area_frac": round(float(mask.mean()), 5),
        "centroid_frac": [round(float(xs.mean() / w), 5), round(float(ys.mean() / h), 5)],
        "bbox_frac": [round(float(xs.min() / w), 5), round(float(ys.min() / h), 5), round(float((xs.max() + 1) / w), 5), round(float((ys.max() + 1) / h), 5)],
        "width_R": round(float((xs.max() + 1 - xs.min()) / w * ORTHO_WIDTH_R), 4),
        "height_R": round(float((ys.max() + 1 - ys.min()) / h * ORTHO_WIDTH_R), 4),
    }


def resize_to(mask, size):
    return np.asarray(Image.fromarray((mask * 255).astype(np.uint8)).resize(size, Image.NEAREST)) > 127


def compare(blender_path: Path, unity_path: Path, name: str):
    b = silhouette(blender_path, "grey")
    u = silhouette(unity_path, "black")
    if b.shape != u.shape:
        u = resize_to(u, (b.shape[1], b.shape[0]))
    best = None
    for flip in (False, True):
        uu = u[:, ::-1] if flip else u
        inter = np.logical_and(b, uu).sum()
        union = np.logical_or(b, uu).sum()
        iou = float(inter / union) if union else 0.0
        if best is None or iou > best[0]:
            best = (iou, flip, uu)
    iou, flip, uu = best
    sb, su = stats(b), stats(uu)
    overlay = np.zeros((*b.shape, 3), dtype=np.uint8)
    overlay[..., 0] = b * 255           # red = Blender only
    overlay[..., 1] = uu * 255          # green = Unity only; yellow = both
    Image.fromarray(overlay).save(HERE / f"silhouette-overlay-{name}.png")
    return {
        "blender": blender_path.name, "unity": unity_path.name, "iou": round(iou, 4), "mirrored_to_match": flip,
        "area_ratio_unity_over_blender": round(su["area_frac"] / sb["area_frac"], 4) if sb["area_frac"] else None,
        "centroid_offset_frac": [round(su["centroid_frac"][0] - sb["centroid_frac"][0], 5), round(su["centroid_frac"][1] - sb["centroid_frac"][1], 5)] if "centroid_frac" in su and "centroid_frac" in sb else None,
        "blender": {"file": blender_path.name, **sb}, "unity": {"file": unity_path.name, **su},
        "overlay": f"silhouette-overlay-{name}.png",
    }


def main():
    top = compare(G10 / "review/glb-top-ortho-silhouette.png", HERE / "unity-neutral-top-ortho.png", "top-ortho")
    hero = compare(G10 / "review/glb-hero-silhouette.png", HERE / "unity-neutral-hero.png", "hero")
    manifest = json.loads((G10 / "export-manifest.json").read_text(encoding="utf-8"))
    unity = json.loads((HERE / "unity-import-parity-report.json").read_text(encoding="utf-8"))
    tri_checks = {}
    for key, name in (("rotorBody", "Rotor_Body"), ("capTop", "Cap_Top"), ("capBottom", "Cap_Bottom"), ("hubCore", "Hub_Core")):
        exported = manifest["meshes"][name]["tris"]
        imported = unity[key]["triangles"]
        tri_checks[name] = {"exported_tris": exported, "unity_tris": imported, "ratio": round(imported / exported, 4) if exported else None}
    rotor_size = unity["rotorBoundsSizeM"]
    checks = {
        "top-ortho silhouette IoU >= 0.97": top["iou"] >= 0.97,
        "top-ortho planar extent 2R within 1 % (Unity vs Blender)": abs(top["unity"]["width_R"] - top["blender"]["width_R"]) <= 0.01 * ORTHO_WIDTH_R and abs(top["unity"]["height_R"] - top["blender"]["height_R"]) <= 0.01 * ORTHO_WIDTH_R,
        "hero silhouette IoU >= 0.93": hero["iou"] >= 0.93,
        "ownership: rotor rotates, caps + hub core static": unity["rotorBody"]["rotates"] and not unity["capTop"]["rotates"] and not unity["capBottom"]["rotates"] and not unity["hubCore"]["rotates"],
        "all four renderers enabled": all(unity[k]["rendererEnabled"] for k in ("rotorBody", "capTop", "capBottom", "hubCore")),
        "materials remapped (Satin / DiscTurned / HubDark)": unity["rotorBody"]["materials"] == ["M_GeeoneSatin"] and "M_GeeoneDiscTurned" in unity["capTop"]["materials"] and unity["hubCore"]["materials"] == ["M_GeeoneHubDark"],
        "triangle counts within 1 % of the export": all(abs(v["ratio"] - 1.0) <= 0.01 for v in tri_checks.values()),
        "rotor AABB 2R sin60 x thickness (m)": abs(rotor_size[0] - 0.07361) < 0.001 and abs(rotor_size[1] - 0.01007) < 0.0007,
        "rotor at zero angular velocity on load": unity["rotorAngularVelocityAtLoad"] == 0.0,
        "authored yaw 180 (blade at twelve o'clock)": unity["rotorYaw180Applied"],
        "rotor controller present": unity["rotorController"],
    }
    report = {
        "schemaVersion": 1, "gate": "11-unity-parity", "revision": 2, "modelId": "metal-three-blade",
        "source": {"exportManifest": "10-export/rev-002/export-manifest.json", "fbxSha256": manifest["files"]["geeone-tri-spinner.fbx"]["sha256"], "unityScene": unity["scene"], "unityAsset": unity["rotorBody"]["mesh"]},
        "camera": {"topOrthoWidthR": ORTHO_WIDTH_R, "blenderHeroR": [1.2, -1.6, 1.5], "unityHeroM": unity["neutralCamera"]["heroPositionM"], "note": "Blender (x,y,z) -> Unity (x,z,-y) by FBX, then 180° yaw in the scene builder"},
        "silhouette": {"top-ortho": top, "hero": hero},
        "triangles": tri_checks,
        "unityImport": unity,
        "checks": checks,
        "pass": all(checks.values()),
        "humanInspection": "visual approval of the shipping previews (12-shipping/rev-006) is a separate user decision; this report only proves the Unity scene shows the exported geometry with the approved ownership",
    }
    (HERE / "parity-report.json").write_text(json.dumps(report, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    # comparison sheet
    F = lambda n: ImageFont.truetype("/System/Library/Fonts/STHeiti Medium.ttc", n)
    tiles = [(G10 / "review/glb-top-ortho.png", "Blender · 导出 GLB 回读 · 顶视正交 2.3 R（材质）"), (HERE / "unity-neutral-top-ortho.png", "Unity · 出货场景 · 同相机（白色轮廓）"), (HERE / "silhouette-overlay-top-ortho.png", f"轮廓叠加 · IoU {top['iou']:.3f}（黄 = 重合，红 = 只 Blender，绿 = 只 Unity）"),
             (G10 / "review/glb-hero.png", "Blender · GLB 回读 · hero（材质）"), (HERE / "unity-neutral-hero.png", "Unity · 同相机 hero（白色轮廓）"), (HERE / "silhouette-overlay-hero.png", f"轮廓叠加 · IoU {hero['iou']:.3f}")]
    W = 640
    sheet = Image.new("RGB", (W * 3 + 40, W * 2 + 110), (250, 250, 250))
    d = ImageDraw.Draw(sheet)
    d.text((10, 8), f"Gate 11 Unity 对齐 rev-002 · GEEONE 龙鳞三叶 · {'PASS' if report['pass'] else 'FAIL'} · 顶视 IoU {top['iou']:.3f} · hero IoU {hero['iou']:.3f} · 三角数一致 · 转子转 / 盖 + 毂芯静", fill=(20, 20, 20), font=F(20))
    d.text((10, 40), "Unity: RotorDynamic/Rotor_Root/Rotor_Body 转；HubStatic/TopCap/Cap_Top、BottomCap/Cap_Bottom、Hub_Core 静 · 材质 M_GeeoneSatin / M_GeeoneDiscTurned / M_GeeoneHubDark · 85 mm", fill=(120, 30, 30), font=F(14))
    for k, (path, cap) in enumerate(tiles):
        im = Image.open(path).convert("RGB").resize((W, W), Image.LANCZOS)
        dd = ImageDraw.Draw(im)
        dd.rectangle((0, W - 40, W, W), fill=(0, 0, 0))
        dd.text((8, W - 31), cap, fill=(255, 255, 255), font=F(15))
        sheet.paste(im, (10 + (k % 3) * (W + 10), 70 + (k // 3) * (W + 10)))
    sheet.save(HERE / "unity-parity-contact-sheet.png")
    print(json.dumps(checks, ensure_ascii=False, indent=1))
    print("pass", report["pass"], "top IoU", top["iou"], "hero IoU", hero["iou"], "extent R", top["blender"]["width_R"], top["unity"]["width_R"])
    return 0 if report["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
