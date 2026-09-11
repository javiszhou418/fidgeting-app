#!/usr/bin/env python3

import json
import math
from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent
CONTRACT_PATH = ROOT / "modeling-contract.json"
OUTPUT_PATH = ROOT / "contract-preview.png"
WIDTH = 2400
HEIGHT = 3200

BG = "#0B0D12"
PANEL = "#151922"
PANEL_ALT = "#11151D"
LINE = "#313846"
TEXT = "#F5F7FA"
MUTED = "#A7B0C0"
LOCKED = "#65D3AC"
PENDING = "#F5B95F"
BLUE = "#77A7FF"
RED = "#F07E84"


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size, index=1 if bold else 0)
    return ImageFont.load_default()


F_TITLE = font(78, True)
F_H1 = font(43, True)
F_H2 = font(35, True)
F_BODY = font(31)
F_BODY_BOLD = font(31, True)
F_SMALL = font(26)
F_TAG = font(25, True)
F_BIG_NUMBER = font(48, True)


def text_width(draw: ImageDraw.ImageDraw, value: str, typeface: ImageFont.ImageFont) -> float:
    return draw.textbbox((0, 0), value, font=typeface)[2]


def wrap(draw: ImageDraw.ImageDraw, value: str, typeface: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in value.splitlines() or [""]:
        if not paragraph:
            lines.append("")
            continue
        current = ""
        for token in paragraph.split(" "):
            candidate = token if not current else f"{current} {token}"
            if text_width(draw, candidate, typeface) <= max_width:
                current = candidate
                continue
            if current:
                lines.append(current)
                current = ""
            if text_width(draw, token, typeface) <= max_width:
                current = token
                continue
            segment = ""
            for character in token:
                test = segment + character
                if text_width(draw, test, typeface) <= max_width:
                    segment = test
                else:
                    if segment:
                        lines.append(segment)
                    segment = character
            current = segment
        if current:
            lines.append(current)
    return lines


def draw_wrapped(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    value: str,
    typeface: ImageFont.ImageFont,
    fill: str,
    max_width: int,
    line_height: int,
    max_lines: Optional[int] = None,
) -> int:
    x, y = xy
    lines = wrap(draw, value, typeface, max_width)
    if max_lines is not None and len(lines) > max_lines:
        lines = lines[:max_lines]
        tail = lines[-1]
        while tail and text_width(draw, tail + "…", typeface) > max_width:
            tail = tail[:-1]
        lines[-1] = tail + "…"
    for line in lines:
        draw.text((x, y), line, font=typeface, fill=fill)
        y += line_height
    return y


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill: str = PANEL) -> None:
    draw.rounded_rectangle(box, radius=30, fill=fill, outline=LINE, width=2)


def tag(draw: ImageDraw.ImageDraw, x: int, y: int, label: str, color: str) -> int:
    padding_x = 18
    width = math.ceil(text_width(draw, label, F_TAG)) + padding_x * 2
    draw.rounded_rectangle((x, y, x + width, y + 46), radius=23, fill=color)
    draw.text((x + padding_x, y + 8), label, font=F_TAG, fill=BG)
    return x + width


def card(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    title: str,
    status: str,
    lines: list[tuple[str, str]],
) -> None:
    x0, y0, x1, y1 = box
    rounded_panel(draw, box)
    draw.text((x0 + 32, y0 + 25), title, font=F_H2, fill=TEXT)
    status_color = LOCKED if status == "LOCKED" else PENDING
    status_width = text_width(draw, status, F_TAG) + 36
    tag(draw, int(x1 - status_width - 28), y0 + 24, status, status_color)
    y = y0 + 86
    for label, value in lines:
        draw.text((x0 + 34, y), label, font=F_BODY_BOLD, fill=BLUE)
        label_width = text_width(draw, label, F_BODY_BOLD)
        y = draw_wrapped(
            draw,
            (int(x0 + 46 + label_width), y),
            value,
            F_BODY,
            TEXT,
            int(x1 - x0 - 92 - label_width),
            43,
            2,
        )
        y += 8


def draw_case_diagram(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int]) -> None:
    x0, y0, x1, y1 = box
    rounded_panel(draw, box, PANEL_ALT)
    draw.text((x0 + 34, y0 + 28), "候选外包络与闭环管", font=F_H1, fill=TEXT)
    tag(draw, x0 + 34, y0 + 90, "待审批", PENDING)

    case_h = 580
    case_w = round(case_h * 0.75)
    cx = x0 + 325
    top = y0 + 175
    left = cx - case_w // 2
    right = cx + case_w // 2
    bottom = top + case_h
    draw.rounded_rectangle(
        (left, top, right, bottom),
        radius=40,
        fill="#1B202A",
        outline=PENDING,
        width=15,
    )
    draw.rounded_rectangle(
        (left + 28, top + 28, right - 28, bottom - 28),
        radius=25,
        fill="#0F1218",
        outline="#6A7485",
        width=4,
    )
    label_h = 112
    draw.rounded_rectangle(
        (left + 54, top + 48, right - 54, top + 48 + label_h),
        radius=16,
        fill="#D5D0C6",
        outline="#EEE9DF",
        width=3,
    )
    draw.text((left + 78, top + 70), "PREMIUM DISPLAY", font=F_SMALL, fill="#222832")
    draw.text((left + 78, top + 111), "184 × 58 mm LABEL", font=F_SMALL, fill="#525A66")
    chamber_top = top + 205
    draw.rounded_rectangle(
        (left + 62, chamber_top, right - 62, bottom - 62),
        radius=38,
        fill="#080A0E",
        outline="#363E4A",
        width=5,
    )
    draw.ellipse(
        (cx - 87, chamber_top + 130, cx + 87, chamber_top + 304),
        fill="#222A34",
        outline="#6E7B8C",
        width=5,
    )
    draw.line((cx - 52, chamber_top + 220, cx + 52, chamber_top + 220), fill="#AAB4C2", width=12)
    draw.line((cx, chamber_top + 168, cx, chamber_top + 272), fill="#AAB4C2", width=12)

    arrow_x = right + 58
    draw.line((arrow_x, top, arrow_x, bottom), fill=BLUE, width=5)
    draw.polygon([(arrow_x, top), (arrow_x - 13, top + 24), (arrow_x + 13, top + 24)], fill=BLUE)
    draw.polygon([(arrow_x, bottom), (arrow_x - 13, bottom - 24), (arrow_x + 13, bottom - 24)], fill=BLUE)
    draw.text((arrow_x + 20, (top + bottom) // 2 - 25), "304 mm", font=F_BIG_NUMBER, fill=BLUE)

    width_y = bottom + 48
    draw.line((left, width_y, right, width_y), fill=BLUE, width=5)
    draw.polygon([(left, width_y), (left + 24, width_y - 13), (left + 24, width_y + 13)], fill=BLUE)
    draw.polygon([(right, width_y), (right - 24, width_y - 13), (right - 24, width_y + 13)], fill=BLUE)
    draw.text((cx - 92, width_y + 18), "228 mm", font=F_BIG_NUMBER, fill=BLUE)

    detail_x = x0 + 820
    detail_y = y0 + 205
    draw.text((detail_x, detail_y), "闭环管截面", font=F_H2, fill=TEXT)
    outer = (detail_x, detail_y + 74, detail_x + 270, detail_y + 310)
    draw.rounded_rectangle(outer, radius=72, fill="#B9C3CD", outline="#E9EEF3", width=4)
    inner = (detail_x + 52, detail_y + 127, detail_x + 218, detail_y + 257)
    draw.rounded_rectangle(inner, radius=38, fill=BG, outline="#697586", width=3)
    draw.text((detail_x + 305, detail_y + 98), "10 × 9 mm", font=F_BIG_NUMBER, fill=PENDING)
    draw.text((detail_x + 305, detail_y + 166), "壁厚 2 mm", font=F_BODY_BOLD, fill=TEXT)
    draw.text((detail_x + 305, detail_y + 218), "通道 6 × 5 mm", font=F_BODY, fill=MUTED)
    draw.text((detail_x, detail_y + 350), "四角外半径 20 mm · 中心线 15 mm", font=F_BODY_BOLD, fill=TEXT)
    draw.text((detail_x, detail_y + 404), "单一 manifold · 0 开放边 · 全通道 flood-fill", font=F_BODY, fill=LOCKED)
    draw.text((detail_x, detail_y + 473), "59 mm 总深度", font=F_BIG_NUMBER, fill=PENDING)
    draw.text((detail_x, detail_y + 538), "历史 216 × 304 × 59 mm 仅作参考", font=F_SMALL, fill=MUTED)


def main() -> None:
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert contract["stageStatus"] == "ready_for_review"
    assert len(contract["sourceClaimIds"]) == 7

    image = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(image)

    draw.text((90, 72), "GATE 03 · 建模与动效合同", font=F_TITLE, fill=TEXT)
    draw.text((92, 172), "PREMIUM DISPLAY CASE · REV 001", font=F_H1, fill=BLUE)
    tag(draw, 92, 238, "2 / 12 已批准", LOCKED)
    tag(draw, 335, 238, "GATE 03 待审批", PENDING)
    draw_wrapped(
        draw,
        (90, 306),
        "所有琥珀色数值都是 Gate 03 候选，不是用户已批准值。当前 shipping 资产保持不变；不得进入 Gate 04。",
        F_BODY_BOLD,
        PENDING,
        WIDTH - 180,
        45,
        2,
    )

    draw_case_diagram(draw, (80, 420, 2320, 1410))

    cards = [
        (
            "已批准的上游边界",
            "LOCKED",
            [
                ("比例", "Portrait，约 3:4；Landscape 无效。"),
                ("结构", "一根闭环管；四角相切；单一连通体。"),
                ("顺序", "出现 → Y 轴 360° → 单次高光 → 悬浮。"),
                ("保留", "磨砂背景、phone 可读实体标签、环境隔离。"),
            ],
        ),
        (
            "标签与背景候选",
            "PENDING",
            [
                ("标签", "184 × 58 mm；8 mm safe inset。"),
                ("投影", "产品名 ≥17 pt；元数据 ≥11 pt；标记 ≥20 pt。"),
                ("背景", "metallic 0；roughness 0.78–0.88。"),
                ("纹理", "0.35–0.8 mm 连续细颗粒；无晕、无局部贴片。"),
            ],
        ),
        (
            "Y 轴展示与完成态",
            "PENDING",
            [
                ("转动", "1.80 s，sine-in-out，unwrapped 0→360°。"),
                ("采样", "0 / 90 / 180 / 270 / 360°；最终角速度 0。"),
                ("高光", "0.55 s，1 次，面宽 10%，峰值 ≤1.15×。"),
                ("悬浮", "Y 轴 ±2 mm，3.2 s；内部奖品不自转。"),
            ],
        ),
        (
            "相机与灯光范围",
            "PENDING",
            [
                ("相机", "正视；vFOV 27–31°，首选 29°。"),
                ("构图", "盒高占屏 78–84%；中心偏差 ≤1%。"),
                ("灯光", "Key 4300–5200 K；Fill 5600–6800 K。"),
                ("比率", "Key:Fill 2–3:1；Rim ≤0.35× Key；≤3 灯。"),
            ],
        ),
        (
            "Reduce Motion",
            "PENDING",
            [
                ("因果", "receipt → 真盒 ready → handoff → 可收下，保持不变。"),
                ("转动", "替换为 0.20 s 静态正视停留。"),
                ("高光", "替换为 0.25 s 非空间亮度脉冲，仅 1 次。"),
                ("完成态", "静止；关闭 hover、parallax 和奖品运动。"),
            ],
        ),
        (
            "移动性能预算",
            "PENDING",
            [
                ("锁定", "60 FPS；2× MSAA；render scale 0.9。"),
                ("几何", "盒体 ≤120k triangles；≤8 材质槽。"),
                ("帧耗", "CPU ≤0.20 ms；增量 GPU ≤1.50 ms。"),
                ("运行", "0 B/frame GC；离屏 0 update；真机 Release 量测。"),
            ],
        ),
    ]
    card_w = 1080
    card_h = 405
    x_positions = [80, 1240]
    y_start = 1460
    for index, item in enumerate(cards):
        column = index % 2
        row = index // 2
        x = x_positions[column]
        y = y_start + row * (card_h + 34)
        card(draw, (x, y, x + card_w, y + card_h), item[0], item[1], item[2])

    claims_y = 2805
    rounded_panel(draw, (80, claims_y, 2320, 3030), PANEL_ALT)
    draw.text((112, claims_y + 26), "Gate 02 claims 已全部消费", font=F_H2, fill=TEXT)
    claim_labels = [
        "闭环管",
        "manifold",
        "磨砂背景",
        "标签可读",
        "Portrait",
        "360° 流程",
        "环境隔离",
    ]
    x = 112
    y = claims_y + 92
    for label in claim_labels:
        next_x = tag(draw, x, y, label, LOCKED)
        if next_x > 2180:
            x = 112
            y += 62
            next_x = tag(draw, x, y, label, LOCKED)
        x = next_x + 18

    question = contract["approvalQuestion"]
    draw.rounded_rectangle((80, 3070, 2320, 3170), radius=30, fill="#2A2115", outline=PENDING, width=3)
    draw.text((112, 3092), "下一审批：", font=F_BODY_BOLD, fill=PENDING)
    draw_wrapped(draw, (290, 3092), question, F_SMALL, TEXT, 1980, 36, 2)

    image.save(OUTPUT_PATH, format="PNG", optimize=True)
    print(f"CONTRACT_PREVIEW={OUTPUT_PATH}")
    print(f"SIZE={WIDTH}x{HEIGHT}")


if __name__ == "__main__":
    main()
