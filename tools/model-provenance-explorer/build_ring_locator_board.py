"""Label every candidate "metal ring" element on the current shipping renders.

Five rounds of the same complaint suggest the element was misidentified. This
board numbers each candidate so the user can name the one they mean instead of
the assistant guessing again.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

REPO = Path("/Users/jiawei.zhou/Documents/Fidgeting app")
SRC = REPO / "Artifacts/EnvironmentIntegration/hub-cap-facets-r005"
OUT = Path("/tmp/dragon-scale-gate02")

# model, view, panel label, callouts: (number, normalised x, y, text)
PANELS = [
    (
        "metal-three-blade",
        "top",
        "metal-three-blade 顶视",
        [
            ("1", 0.50, 0.60, "中心亮圆盘"),
            ("2", 0.50, 0.42, "帽体与叶片之间的缝"),
            ("3", 0.50, 0.28, "叶片上的三角刻线"),
        ],
    ),
    (
        "metal-three-blade",
        "oblique",
        "metal-three-blade 斜视",
        [
            ("4", 0.50, 0.45, "侧面看到的环"),
        ],
    ),
    (
        "gold-four-wing",
        "top",
        "gold-four-wing 顶视",
        [
            ("5", 0.50, 0.58, "中心放射盘"),
            ("6", 0.50, 0.30, "叶片三角刻线"),
        ],
    ),
    (
        "graphite-two-lobe",
        "top",
        "graphite-two-lobe 顶视",
        [
            ("7", 0.50, 0.50, "中心圆"),
        ],
    ),
    (
        "pointed-three-blade",
        "top",
        "pointed-three-blade 顶视",
        [
            ("8", 0.50, 0.50, "中心圆"),
        ],
    ),
]


def font(size: int):
    for candidate, index in (
        ("/System/Library/Fonts/PingFang.ttc", 4),
        ("/System/Library/Fonts/PingFang.ttc", 0),
        ("/System/Library/Fonts/STHeiti Medium.ttc", 0),
    ):
        if Path(candidate).exists():
            try:
                return ImageFont.truetype(candidate, size, index=index)
            except OSError:
                continue
    return ImageFont.load_default()


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    cell = 560
    caption = 150
    pad = 18
    header = 130
    columns = 3
    rows = (len(PANELS) + columns - 1) // columns

    width = columns * cell + (columns + 1) * pad
    height = header + rows * (cell + caption) + (rows + 1) * pad
    board = Image.new("RGB", (width, height), (13, 13, 15))
    draw = ImageDraw.Draw(board)
    title = font(42)
    sub = font(27)
    label = font(28)
    note = font(24)
    badge = font(30)

    draw.text(
        (pad + 6, 24),
        "当前出货模型 — 请指出你说的「金属圆环」是几号",
        fill=(245, 245, 245),
        font=title,
    )
    draw.text(
        (pad + 6, 78),
        "如果都不是，请直接发一张手机截图并圈出来。",
        fill=(255, 190, 90),
        font=sub,
    )

    for index, (model, view, panel_label, callouts) in enumerate(PANELS):
        column = index % columns
        row = index // columns
        x = pad + column * (cell + pad)
        y = header + pad + row * (cell + caption + pad)

        source = SRC / f"{model}-a-current-{view}.png"
        with Image.open(source) as raw:
            frame = raw.convert("RGB").resize((cell, cell), Image.LANCZOS)
        board.paste(frame, (x, y))
        draw.rectangle([x, y, x + cell, y + cell], outline=(70, 70, 78), width=2)

        for number, nx, ny, _ in callouts:
            cx = x + int(nx * cell)
            cy = y + int(ny * cell)
            radius = 24
            draw.ellipse(
                [cx - radius, cy - radius, cx + radius, cy + radius],
                fill=(255, 60, 60),
                outline=(255, 255, 255),
                width=3,
            )
            box = draw.textbbox((0, 0), number, font=badge)
            draw.text(
                (cx - (box[2] - box[0]) / 2, cy - (box[3] - box[1]) / 2 - 4),
                number,
                fill=(255, 255, 255),
                font=badge,
            )

        draw.rectangle([x, y + cell, x + cell, y + cell + caption], fill=(22, 22, 26))
        draw.text((x + 12, y + cell + 8), panel_label, fill=(90, 220, 255), font=label)
        ny_text = y + cell + 48
        for number, _, _, text in callouts:
            draw.text(
                (x + 12, ny_text), f"{number}. {text}", fill=(230, 230, 234), font=note
            )
            ny_text += 32

    out = OUT / "00-ring-locator.png"
    board.save(out)
    print(out)


if __name__ == "__main__":
    main()
