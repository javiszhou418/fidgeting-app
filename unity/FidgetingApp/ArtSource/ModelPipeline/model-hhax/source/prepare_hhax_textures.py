#!/usr/bin/env python3
"""Create source-derived day/night material maps for model-hhax.

The warps use only the user's archived day/night photographs.  They preserve the
custom artwork while removing the hand/background from the texture domain.
"""
from pathlib import Path
import cv2
import numpy as np

ROOT = Path(__file__).resolve().parents[6]
INTAKE = ROOT / "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/evidence/01-intake/rev-001"
OUT = ROOT / "unity/FidgetingApp/ArtSource/ModelPipeline/model-hhax/source/textures"
OUT.mkdir(parents=True, exist_ok=True)

W, H = 1024, 1672

def read(name):
    image = cv2.imread(str(INTAKE / name), cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(name)
    return image

def warp(image, quad, size=(W, H), dest=None, border=(13, 11, 16)):
    width, height = size
    src = np.float32(quad)
    if dest is None:
        dest = [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]]
    matrix = cv2.getPerspectiveTransform(src, np.float32(dest))
    return cv2.warpPerspective(image, matrix, (width, height), flags=cv2.INTER_CUBIC,
                               borderMode=cv2.BORDER_CONSTANT, borderValue=border)

def finish(image):
    # Mild local-contrast restoration compensates for the compressed source video stills.
    lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    l = cv2.createCLAHE(clipLimit=1.45, tileGridSize=(8, 8)).apply(l)
    return cv2.cvtColor(cv2.merge([l, a, b]), cv2.COLOR_LAB2BGR)

def emission_from_dark(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    sat = hsv[..., 1].astype(np.float32) / 255.0
    val = hsv[..., 2].astype(np.float32) / 255.0
    cyan = ((hsv[..., 0] >= 76) & (hsv[..., 0] <= 112) & (sat > .42) & (val > .28))
    orange = ((hsv[..., 0] >= 3) & (hsv[..., 0] <= 28) & (sat > .40) & (val > .28))
    mask = ((cyan | orange).astype(np.uint8) * 255)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8))
    mask = cv2.GaussianBlur(mask, (0, 0), 1.2)
    out = np.zeros_like(image)
    out[cyan] = (255, 175, 25)       # BGR cyan-blue
    out[orange] = (20, 125, 255)     # BGR orange
    out = cv2.GaussianBlur(out, (0, 0), 1.0)
    out = cv2.multiply(out, np.dstack([mask] * 3), scale=1 / 255.0)
    return out, mask

def roughness_map(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    value = hsv[..., 2]
    # Pearl/clear artwork remains glossy but has slightly more micro-roughness than the metal rim.
    result = np.interp(value, [0, 255], [58, 104]).astype(np.uint8)
    return cv2.GaussianBlur(result, (0, 0), 2.0)

def normal_map(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY).astype(np.float32) / 255.0
    gray = cv2.GaussianBlur(gray, (0, 0), 1.3)
    sx = cv2.Sobel(gray, cv2.CV_32F, 1, 0, ksize=3)
    sy = cv2.Sobel(gray, cv2.CV_32F, 0, 1, ksize=3)
    strength = 1.6
    nx, ny = -sx * strength, -sy * strength
    nz = np.ones_like(nx)
    length = np.sqrt(nx * nx + ny * ny + nz * nz)
    normal = np.dstack([(nx / length * .5 + .5), (ny / length * .5 + .5), (nz / length * .5 + .5)])
    return np.clip(normal * 255, 0, 255).astype(np.uint8)

front_day = finish(warp(read("5e1659c986fca1385c68a75261bb7390_MD5.jpg"),
                        [[245, 351], [454, 351], [455, 698], [242, 698]]))
front_dark = warp(read("550dff93e63dab50674e74353832a5bd_MD5.jpg"),
                  [[270, 520], [451, 526], [447, 820], [260, 811]])

lower_source = read("5e1659c986fca1385c68a75261bb7390_MD5.jpg")
lower_day = np.full((H, W, 3), (18, 15, 22), dtype=np.uint8)
lower_warp = warp(lower_source,
                  [[241, 675], [454, 677], [458, 852], [239, 852]],
                  dest=[[0, int(H * .60)], [W - 1, int(H * .60)], [W - 1, H - 1], [0, H - 1]])
mask_region = np.zeros((H, W), dtype=np.uint8)
mask_region[int(H * .60):, :] = 255
lower_day[mask_region > 0] = finish(lower_warp)[mask_region > 0]

back_day = finish(warp(read("3ebb3ff0c166ec3145e1b5d1a68294f7_MD5.jpg"),
                       [[300, 535], [423, 541], [452, 839], [274, 846]]))
back_dark = warp(read("11f45d5c543d363c007a35c22d820ed3_MD5.jpg"),
                 [[240, 520], [405, 530], [410, 731], [224, 718]])

for name, image in {"front": front_day, "lower": lower_day, "back": back_day}.items():
    cv2.imwrite(str(OUT / f"{name}-basecolor.png"), image, [cv2.IMWRITE_PNG_COMPRESSION, 5])
    cv2.imwrite(str(OUT / f"{name}-roughness.png"), roughness_map(image), [cv2.IMWRITE_PNG_COMPRESSION, 5])
    cv2.imwrite(str(OUT / f"{name}-normal.png"), normal_map(image), [cv2.IMWRITE_PNG_COMPRESSION, 5])

front_emission, front_mask = emission_from_dark(front_dark)
back_emission, back_mask = emission_from_dark(back_dark)
lower_emission = np.zeros_like(lower_day)
lower_mask = np.zeros((H, W), dtype=np.uint8)
for name, color, mask in [
    ("front", front_emission, front_mask),
    ("lower", lower_emission, lower_mask),
    ("back", back_emission, back_mask),
]:
    cv2.imwrite(str(OUT / f"{name}-emission.png"), color, [cv2.IMWRITE_PNG_COMPRESSION, 5])
    cv2.imwrite(str(OUT / f"{name}-emission-mask.png"), mask, [cv2.IMWRITE_PNG_COMPRESSION, 5])

preview = np.hstack([
    cv2.resize(front_day, (306, 500)),
    cv2.resize(lower_day, (306, 500)),
    cv2.resize(back_day, (306, 500)),
    cv2.resize(front_emission, (306, 500)),
    cv2.resize(back_emission, (306, 500)),
])
cv2.imwrite(str(OUT / "texture-source-board.png"), preview, [cv2.IMWRITE_PNG_COMPRESSION, 4])
print(OUT)
