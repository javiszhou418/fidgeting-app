"""Compose captioned, large-format comparison sheets from the Unity captures.

The six-across sheets Unity writes are too small to judge a finish once they
are scaled into a chat or a doc. This regroups the same PNGs into fewer,
bigger cells and burns in the candidate name so a sheet cannot be read in the
wrong order.

Usage: python3 compose_readable_sheets.py
"""

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent

# Measured label strip inside the 1640x2000 macro capture: the plate spans
# x 195-1460, y 798-1202. Kept with margin so the printed fields are whole.
STRIP = (160, 758, 1500, 1242)

CANDIDATES = [
    ("00-current", "00 当前 shipping", "标签 #423B33 Unlit / 背板 #050609"),
    ("a-archive-paper-flocking", "A 档案卡纸 x 黑植绒", "标签 #BDB8AD / 背板 #050609"),
    ("b-graphite-deboss-microsuede", "B 石墨压凹 x 炭灰绒面", "标签 #0E0F11 Lit / 背板 #0E1114"),
    ("c-narrow-foil-ink-flocking", "C 窄银箔 x 墨蓝植绒", "标签 #BDB8AD + 箔带 / 背板 #04060B"),
    ("d-stone-paper-graphite-felt", "D 石纹卡纸 x 石墨羊毛毡", "标签 #E4E0D8 + 斑点 / 背板 #16171A"),
    ("e-anodized-plate-velvet", "E 阳极氧化铝 x 午夜绿丝绒", "标签 #6E7378 金属 / 背板 #0B1512"),
]

BACKDROP = (15, 16, 20)
TITLE_INK = (238, 236, 230)
NOTE_INK = (150, 152, 158)


def font(size, bold=False):
    """Captions carry Chinese, so a CJK face is required, not Helvetica."""
    for path, index in (
        ("/System/Library/Fonts/Hiragino Sans GB.ttc", 1 if bold else 0),
        ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
        ("/System/Library/Fonts/Supplemental/Arial Unicode.ttf", 0),
    ):
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size, index=index)
            except OSError:
                continue
    raise SystemExit("No CJK font available for captions.")


TITLE_FONT = font(34, bold=True)
NOTE_FONT = font(25)


def caption(draw, x, y, title, note):
    draw.text((x, y), title, font=TITLE_FONT, fill=TITLE_INK)
    draw.text((x, y + 42), note, font=NOTE_FONT, fill=NOTE_INK)


def label_stack(members, out_name):
    """One candidate per row, strip at full width so the print is legible."""
    crops = [
        Image.open(HERE / f"{key}-label-macro.png").convert("RGB").crop(STRIP)
        for key, _, _ in members
    ]
    cell_w, cell_h = crops[0].size
    pad, header = 28, 86
    sheet = Image.new(
        "RGB",
        (cell_w + 2 * pad, len(crops) * (cell_h + header + pad) + pad),
        BACKDROP,
    )
    draw = ImageDraw.Draw(sheet)
    y = pad
    for crop, (_, title, note) in zip(crops, members):
        caption(draw, pad + 2, y, title, note)
        sheet.paste(crop, (pad, y + header))
        y += cell_h + header + pad

    sheet.save(HERE / out_name)
    print(f"{out_name}  {sheet.size[0]}x{sheet.size[1]}")


def hero_grid(view, out_name, columns=3, cell_w=620):
    images = [
        Image.open(HERE / f"{key}-{view}.png").convert("RGB")
        for key, _, _ in CANDIDATES
    ]
    cell_h = round(cell_w * images[0].size[1] / images[0].size[0])
    pad, header = 24, 84
    rows = -(-len(images) // columns)
    sheet = Image.new(
        "RGB",
        (
            columns * cell_w + (columns + 1) * pad,
            rows * (cell_h + header) + (rows + 1) * pad,
        ),
        BACKDROP,
    )
    draw = ImageDraw.Draw(sheet)
    for index, (image, (_, title, note)) in enumerate(zip(images, CANDIDATES)):
        column, row = index % columns, index // columns
        x = pad + column * (cell_w + pad)
        y = pad + row * (cell_h + header + pad)
        caption(draw, x + 2, y, title, note)
        sheet.paste(image.resize((cell_w, cell_h), Image.LANCZOS), (x, y + header))

    sheet.save(HERE / out_name)
    print(f"{out_name}  {sheet.size[0]}x{sheet.size[1]}")


if __name__ == "__main__":
    label_stack(CANDIDATES[:3], "readable-label-stack-1.png")
    label_stack(CANDIDATES[3:], "readable-label-stack-2.png")
    hero_grid("hero", "readable-hero-grid.png")
    hero_grid("low", "readable-low-grid.png")
