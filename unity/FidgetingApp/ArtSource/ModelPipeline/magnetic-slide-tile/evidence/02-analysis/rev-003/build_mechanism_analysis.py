#!/usr/bin/env python3
"""Build the Gate 02 mechanism review from frame-indexed user videos."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps


OUT = Path(__file__).resolve().parent
MODEL = OUT.parents[2]
REPO = OUT.parents[7]
INTAKE = MODEL / "evidence/01-intake/rev-003"
VIDEOS = INTAKE / "user-mechanism-videos"
SOURCE_IDS = {
    "IMG_6022": "slider-intake-user-mechanism-video-6022",
    "IMG_6023": "slider-intake-user-mechanism-video-6023",
    "IMG_6024": "slider-intake-user-mechanism-video-6024",
}
KEY_FRAMES = {
    "IMG_6022": [0, 50, 75, 100, 125, 175, 225, 350, 425],
    "IMG_6023": [0, 12, 24, 48, 72, 96, 120, 192, 240],
    "IMG_6024": [0, 32, 64, 96, 128, 160, 183, 191, 199, 207, 256, 320, 384, 576, 608, 704, 736, 768, 800, 820],
}
CROP_BOXES = {
    "IMG_6022": (40, 300, 680, 1100),
    "IMG_6023": (25, 275, 695, 1095),
    "IMG_6024": (20, 245, 700, 1085),
}
INK = (240, 245, 250)
MUTED = (163, 179, 194)
CYAN = (45, 221, 235)
ORANGE = (255, 170, 76)
GREEN = (90, 226, 154)
RED = (255, 105, 110)
BG = (6, 9, 13)
PANEL_BG = (13, 18, 24)


def font(size, bold=False):
    path = "/System/Library/Fonts/STHeiti Medium.ttc" if bold else "/System/Library/Fonts/STHeiti Light.ttc"
    return ImageFont.truetype(path, size=size)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_frames(stem):
    payload = json.loads((OUT / "frame-manifests" / f"{stem}-frames.json").read_text(encoding="utf-8"))
    return payload, {item["frameIndex"]: item for item in payload["frames"]}


def extract_key_frames(stem, indices):
    source = VIDEOS / f"{stem}.MOV"
    target = OUT / "key-frame-crops" / stem
    target.mkdir(parents=True, exist_ok=True)
    for old in target.glob("*.png"):
        old.unlink()
    expression = "+".join(f"eq(n\\,{index})" for index in indices)
    pattern = target / "_decoded-%03d.png"
    subprocess.run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(source),
        "-vf", f"select='{expression}',scale=720:1280:flags=lanczos",
        "-fps_mode", "vfr", str(pattern),
    ], check=True)
    decoded = sorted(target.glob("_decoded-*.png"))
    if len(decoded) != len(indices):
        raise RuntimeError(f"{stem}: expected {len(indices)} key frames, got {len(decoded)}")
    _, by_index = load_frames(stem)
    result = {}
    for path, index in zip(decoded, indices):
        pts = by_index[index]["ptsSeconds"]
        image = Image.open(path).convert("RGB").crop(CROP_BOXES[stem])
        output = target / f"f{index:04d}-{pts:09.6f}s.png"
        image.save(output)
        path.unlink()
        result[index] = output
    return result


def fit(image, box, border=True):
    x, y, width, height = box
    fitted = ImageOps.fit(image.convert("RGB"), (width, height), method=Image.Resampling.LANCZOS)
    if border:
        framed = Image.new("RGB", (width + 4, height + 4), (52, 68, 81))
        framed.paste(fitted, (2, 2))
        return framed, (x - 2, y - 2)
    return fitted, (x, y)


def board(title, subtitle, width, height):
    image = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(image)
    draw.text((54, 36), title, font=font(44, True), fill=INK)
    draw.text((56, 96), subtitle, font=font(24), fill=MUTED)
    return image, draw


def rounded_panel(draw, box, radius=22):
    draw.rounded_rectangle(box, radius=radius, fill=PANEL_BG, outline=(45, 59, 72), width=2)


def frame_caption(draw, x, y, stem, index, pts, title, note=None, color=CYAN):
    draw.text((x, y), f"{stem} · f{index:03d} · {pts:.3f}s", font=font(21, True), fill=color)
    draw.text((x, y + 32), title, font=font(29, True), fill=INK)
    if note:
        draw.text((x, y + 72), note, font=font(20), fill=MUTED)


def dashed_line(draw, points, fill, width=5, dash=16, gap=10):
    for start, end in zip(points[:-1], points[1:]):
        x1, y1 = start
        x2, y2 = end
        length = math.hypot(x2 - x1, y2 - y1)
        if length == 0:
            continue
        ux, uy = (x2 - x1) / length, (y2 - y1) / length
        cursor = 0.0
        while cursor < length:
            stop = min(length, cursor + dash)
            draw.line((x1 + ux * cursor, y1 + uy * cursor, x1 + ux * stop, y1 + uy * stop), fill=fill, width=width)
            cursor += dash + gap


def arrow(draw, start, end, fill, width=7):
    draw.line((*start, *end), fill=fill, width=width)
    angle = math.atan2(end[1] - start[1], end[0] - start[0])
    size = 18
    for delta in (2.55, -2.55):
        tip = (end[0] + size * math.cos(angle + delta), end[1] + size * math.sin(angle + delta))
        draw.line((*end, *tip), fill=fill, width=width)


def image_for(crops, stem, index):
    return Image.open(crops[stem][index]).convert("RGB")


def make_timeline(crops, frame_maps):
    image, draw = board(
        "三段视频连续玩法时间线",
        "每格都写解码帧索引与 PTS；点击工作台中的视频可回到完整连续画面。",
        3000, 2180,
    )
    rows = [
        ("IMG_6022", [(0, "闭合/起始"), (75, "向外打开"), (125, "最大可见行程"), (225, "沿原路返回")]),
        ("IMG_6023", [(0, "0° 基准"), (12, "首个小步"), (72, "约 90° 区间"), (120, "约 180° 端向")]),
        ("IMG_6024", [(183, "机构面开始暴露"), (199, "轨道承载片清楚"), (320, "滑动后继续旋转"), (608, "近最大滑位旋转")]),
    ]
    panel_w, panel_h = 680, 570
    for row, (stem, entries) in enumerate(rows):
        top = 155 + row * 650
        draw.text((56, top), stem, font=font(32, True), fill=ORANGE)
        for col, (index, title) in enumerate(entries):
            x = 210 + col * 700
            y = top
            rounded_panel(draw, (x, y, x + panel_w, y + panel_h))
            fitted, pos = fit(image_for(crops, stem, index), (x + 18, y + 18, panel_w - 36, 410))
            image.paste(fitted, pos)
            pts = frame_maps[stem][index]["ptsSeconds"]
            frame_caption(draw, x + 20, y + 445, stem, index, pts, title)
    path = OUT / "three-video-timeline-board.png"
    image.save(path)
    return path


def make_identity(crops, frame_maps):
    image, draw = board(
        "两片身份：机构承载片 M 与活动盖片 C",
        "名称描述视频中的相对职责；不把 M/C 永久写成所有姿态下的上片或下片。",
        2800, 1720,
    )
    panels = [
        ("IMG_6022", 0, "外观同屏", "M：银色文字/纹样；C：紫色外观"),
        ("IMG_6022", 100, "机构面暴露", "M 背面可见两颗 Torx、轨道与珠列"),
        ("IMG_6022", 125, "拇指驱动 C", "C 的青色涂鸦背面随拇指移动"),
        ("IMG_6024", 199, "交叉确认", "M 的机构承载面在 f183–207 连续可见"),
    ]
    for idx, (stem, frame_index, title, note) in enumerate(panels):
        x = 55 + (idx % 2) * 1370
        y = 155 + (idx // 2) * 760
        rounded_panel(draw, (x, y, x + 1320, y + 710))
        fitted, pos = fit(image_for(crops, stem, frame_index), (x + 22, y + 22, 650, 650))
        image.paste(fitted, pos)
        pts = frame_maps[stem][frame_index]["ptsSeconds"]
        frame_caption(draw, x + 710, y + 45, stem, frame_index, pts, title, note)
        label_y = y + 220
        draw.rounded_rectangle((x + 710, label_y, x + 1260, label_y + 90), 18, fill=(16, 64, 69))
        draw.text((x + 738, label_y + 18), "M · 机构承载片", font=font(31, True), fill=CYAN)
        draw.rounded_rectangle((x + 710, label_y + 120, x + 1260, label_y + 210), 18, fill=(71, 42, 26))
        draw.text((x + 738, label_y + 138), "C · 活动盖片", font=font(31, True), fill=ORANGE)
        draw.text((x + 710, label_y + 250), "画面已见：M 的反面硬件、C 的拇指驱动。\n仍未知：隐藏轴/槽的实际连接截面。", font=font(23), fill=MUTED, spacing=12)
    path = OUT / "plate-identity-board.png"
    image.save(path)
    return path


def make_slide(crops, frame_maps):
    image, draw = board(
        "单向打开，不是不能关闭",
        "闭合止点 → 向外打开 → 最大重叠行程 → 沿同一路径返回闭合。",
        3000, 1120,
    )
    entries = [
        (0, "闭合止点", "不能越过止点反向继续开"),
        (75, "向外打开", "只沿长轴"),
        (125, "最大可见行程", "0.38 ± 0.04 L；仍重叠约 0.62 L"),
        (225, "返回闭合", "反向滑回成功；不是机械卡死"),
    ]
    for col, (index, title, note) in enumerate(entries):
        x = 45 + col * 735
        y = 160
        rounded_panel(draw, (x, y, x + 690, y + 830))
        fitted, pos = fit(image_for(crops, "IMG_6022", index), (x + 20, y + 20, 650, 600))
        image.paste(fitted, pos)
        pts = frame_maps["IMG_6022"][index]["ptsSeconds"]
        frame_caption(draw, x + 20, y + 650, "IMG_6022", index, pts, title, note)
        if col < len(entries) - 1:
            arrow(draw, (x + 675, y + 405), (x + 727, y + 405), ORANGE, 8)
    draw.text((58, 1025), "支持范围：约 0.38–0.46 L，峰值约 0.50 L。现有 21 mm 只可说与范围相容，不是本视频的新毫米测量。", font=font(25, True), fill=GREEN)
    path = OUT / "one-way-slide-sequence-board.png"
    image.save(path)
    return path


def make_rotation(crops, frame_maps):
    image, draw = board(
        "旋转序列与 12° 棘轮节奏",
        "IMG_6023 直接显示同一平移注册下 0° → 180° → 0°；端到端姿态是旋转，不是滑移。",
        3000, 1760,
    )
    entries = [
        (0, "0°", "基准"),
        (12, "12°", "第 1 档附近"),
        (72, "90°", "中段方向"),
        (120, "180°", "端到端方向"),
    ]
    for col, (index, angle, note) in enumerate(entries):
        x = 50 + col * 735
        y = 155
        rounded_panel(draw, (x, y, x + 690, y + 760))
        fitted, pos = fit(image_for(crops, "IMG_6023", index), (x + 20, y + 20, 650, 570))
        image.paste(fitted, pos)
        pts = frame_maps["IMG_6023"][index]["ptsSeconds"]
        frame_caption(draw, x + 22, y + 620, "IMG_6023", index, pts, angle, note)
    audio = Image.open(OUT / "IMG_6023-audio-impulses.png").convert("RGB")
    audio = ImageOps.fit(audio, (2860, 640), method=Image.Resampling.LANCZOS)
    image.paste(audio, (70, 975))
    draw.rounded_rectangle((70, 1625, 2930, 1715), 20, fill=(15, 48, 36), outline=(48, 138, 96), width=2)
    draw.text((98, 1645), "逐帧 + 音频综合：每个 180° 方向各有 15 个候选 detent 瞬态 → 约 12°/档，360° 共 30 档。完整 360° 仍是用户权威陈述，并非本视频全程实拍。", font=font(24, True), fill=GREEN)
    path = OUT / "rotation-and-audio-board.png"
    image.save(path)
    return path


def make_axis_slot(crops, frame_maps):
    image, draw = board(
        "复合轴心 + 纵向轨迹：观察与假设分开画",
        "实线只画视频可见相对运动；虚线只画隐藏候选结构。",
        3000, 1660,
    )
    for col, index in enumerate([183, 199, 207]):
        x = 50 + col * 600
        y = 160
        rounded_panel(draw, (x, y, x + 560, y + 710))
        fitted, pos = fit(image_for(crops, "IMG_6024", index), (x + 18, y + 18, 524, 520))
        image.paste(fitted, pos)
        pts = frame_maps["IMG_6024"][index]["ptsSeconds"]
        frame_caption(draw, x + 20, y + 565, "IMG_6024", index, pts, "M 机构面连续暴露")
    x0, y0, x1, y1 = 1900, 165, 2945, 1455
    rounded_panel(draw, (x0, y0, x1, y1))
    draw.text((x0 + 48, y0 + 42), "工作假设图", font=font(34, True), fill=INK)
    draw.rounded_rectangle((x0 + 180, y0 + 220, x0 + 865, y0 + 920), 180, fill=(104, 111, 119), outline=CYAN, width=6)
    draw.text((x0 + 360, y0 + 525), "M · 机构承载片", font=font(28, True), fill=(8, 15, 20))
    draw.rounded_rectangle((x0 + 260, y0 + 120, x0 + 760, y0 + 720), 150, fill=(88, 36, 111), outline=ORANGE, width=6)
    draw.text((x0 + 410, y0 + 385), "C · 活动盖片", font=font(28, True), fill=INK)
    arrow(draw, (x0 + 510, y0 + 720), (x0 + 510, y0 + 1110), ORANGE, 10)
    draw.text((x0 + 550, y0 + 965), "实线：已见纵向滑动", font=font(23, True), fill=ORANGE)
    draw.arc((x0 + 310, y0 + 330, x0 + 710, y0 + 730), 205, 520, fill=CYAN, width=9)
    arrow(draw, (x0 + 335, y0 + 430), (x0 + 315, y0 + 505), CYAN, 7)
    draw.text((x0 + 560, y0 + 730), "实线：已见旋转", font=font(23, True), fill=CYAN)
    point = (x0 + 430, y0 + 590)
    draw.ellipse((point[0] - 16, point[1] - 16, point[0] + 16, point[1] + 16), fill=RED)
    dashed_line(draw, [(point[0], y0 + 235), (point[0], y0 + 880)], RED, 6)
    draw.text((x0 + 50, y0 + 1040), "虚线候选：M 上固定点 + C 中线槽/接触路径", font=font(23, True), fill=RED)
    draw.text((x0 + 50, y0 + 1090), "拟合：M 点 (u,v)≈(0.36±0.08, 0.45±0.10)\nC 接触沿 u≈0.30–0.76 移动", font=font(22), fill=MUTED, spacing=10)
    draw.text((x0 + 50, y0 + 1200), "中等可信：M 承载固定点、C 承担纵向路径。\n仍未知：轴销归属、槽壁轮廓、耦合与公差。", font=font(22, True), fill=INK, spacing=12)
    draw.rounded_rectangle((60, 945, 1790, 1455), 22, fill=(11, 24, 29), outline=(42, 91, 101), width=2)
    draw.text((100, 985), "综合结论", font=font(31, True), fill=CYAN)
    conclusions = [
        "高可信：两片由复合轴心/纵向轨迹关系约束。",
        "中可信：手持的 M 更可能承担固定点；C 是活动盖片。",
        "高可信：滑动只沿长轴；旋转可发生在部分及近最大滑位。",
        "未知：隐藏轴销、槽截面、每个精确槽位能否旋转。",
    ]
    for index, text in enumerate(conclusions):
        draw.text((110, 1050 + index * 86), f"{index + 1}. {text}", font=font(25, index < 3), fill=INK if index < 3 else RED)
    path = OUT / "axis-slot-hypothesis-board.png"
    image.save(path)
    return path


def make_contradiction(crops, frame_maps):
    image, draw = board(
        "容易误读的两组画面",
        "同一姿态可能来自不同动作；同一零件也有干净外观面与暴露机构面。",
        3000, 1560,
    )
    groups = [
        [
            ("IMG_6023", 120, "端到端外观", "这是约 180° 旋转；平移注册未改变"),
            ("IMG_6022", 125, "真正滑开", "两片中心沿长轴分离，仍有约 0.62 L 重叠"),
        ],
        [
            ("IMG_6022", 0, "M 的正常外观面", "银色文字/纹样，视觉上干净"),
            ("IMG_6022", 100, "M 的反向机构面", "两颗 Torx、轨道与珠列暴露"),
        ],
    ]
    headings = ["端到端 ≠ 一定是滑移", "干净外观面 ≠ 没有内部机构面"]
    for row, entries in enumerate(groups):
        top = 165 + row * 670
        draw.text((58, top), headings[row], font=font(32, True), fill=ORANGE)
        for col, (stem, index, title, note) in enumerate(entries):
            x = 500 + col * 1200
            y = top
            rounded_panel(draw, (x, y, x + 1080, y + 610))
            fitted, pos = fit(image_for(crops, stem, index), (x + 18, y + 18, 530, 570))
            image.paste(fitted, pos)
            pts = frame_maps[stem][index]["ptsSeconds"]
            frame_caption(draw, x + 590, y + 60, stem, index, pts, title, note)
            color = GREEN if col == 1 else CYAN
            draw.rounded_rectangle((x + 590, y + 250, x + 1020, y + 360), 18, fill=(15, 50, 40) if col == 1 else (15, 47, 55))
            draw.text((x + 615, y + 282), "区分后不再冲突", font=font(27, True), fill=color)
        draw.text((70, top + 180), "VS", font=font(48, True), fill=RED)
    draw.text((58, 1490), "仍需用户确认：视频中的 M/C 身份与“正常外观面 / 反向机构面”解释，是否符合真实玩具。", font=font(27, True), fill=GREEN)
    path = OUT / "contradiction-board.png"
    image.save(path)
    return path


def make_audio_contact_sheet():
    image, draw = board(
        "三段原视频音频瞬态总览",
        "自动峰只作定位；detent 数量结论来自逐帧动作与音频联合复核。",
        2600, 2200,
    )
    notes = {
        "IMG_6022": "滑开/回位中的机械瞬态；不据此声称隐藏零件数量。",
        "IMG_6023": "0↔180° 的候选棘轮节奏；联合复核支持每方向 15 档。",
        "IMG_6024": "滑动与旋转混合；末段约 34° 转动出现 3 个强瞬态。",
    }
    for row, stem in enumerate(["IMG_6022", "IMG_6023", "IMG_6024"]):
        y = 145 + row * 665
        rounded_panel(draw, (45, y, 2555, y + 620))
        plot = Image.open(OUT / f"{stem}-audio-impulses.png").convert("RGB")
        plot = ImageOps.fit(plot, (2420, 480), method=Image.Resampling.LANCZOS)
        image.paste(plot, (90, y + 20))
        draw.text((90, y + 520), notes[stem], font=font(23, True), fill=INK)
    path = OUT / "audio-impulse-contact-sheet.png"
    image.save(path)
    return path


def write_analysis(frame_maps, crops, boards):
    key_records = []
    for stem, mapping in crops.items():
        for index, path in sorted(mapping.items()):
            key_records.append({
                "videoAssetId": SOURCE_IDS[stem],
                "video": stem,
                "frameIndex": index,
                "ptsSeconds": frame_maps[stem][index]["ptsSeconds"],
                "path": str(path.relative_to(REPO)),
                "sha256": sha256(path),
            })
    key_manifest = OUT / "key-frame-manifest.json"
    key_manifest.write_text(json.dumps({
        "schemaVersion": 1,
        "frameIndexPolicy": "zero-based decoded video frame index",
        "timestampPolicy": "ffprobe best_effort_timestamp_time; no nominal-fps conversion",
        "frames": key_records,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    analysis = {
        "schemaVersion": 1,
        "modelId": "magnetic-slide-tile",
        "gate": "02-analysis",
        "revision": 3,
        "userIntakeClassification": {
            "approved": True,
            "exactStatement": "三段视频拍摄的是与目标完全相同的产品，仅花纹和纹路不同。视频用于逐帧确认轴心、滑轨、单向推动、最大行程、任意角度旋转和棘轮玩法。",
            "boundary": "颜色、花纹和纹路差异不得被解释为机构差异。",
        },
        "findings": {
            "IMG_6022": {
                "observed": [
                    "426 decoded frames show stepped longitudinal opening and successful closure.",
                    "M exterior has silver text/motif; its reverse exposes two Torx screws, rails and ball rows.",
                    "C has purple exterior/cyan-doodle reverse and is thumb-driven.",
                    "Maximum visible travel is 0.38±0.04L with about 0.62L residual overlap.",
                    "Closed stop blocks farther opening in the opposite direction; open-to-closed return succeeds.",
                    "Mid-travel relative yaw spans about 11.3°; full rotation is not proven here.",
                ],
                "inferred": "Lower-carrier pin plus cover slot is mildly favored, but reciprocal ownership fits nearly as well.",
                "confidence": "low for concealed pin/slot ownership",
            },
            "IMG_6023": {
                "observed": [
                    "480 decoded frames show stepped 0°→180°→0° rotation at one translational registration.",
                    "No successful slide is shown.",
                    "The apparent end-to-end pose is rotation rather than translation.",
                    "The distal perforation on M is not the pivot.",
                ],
                "inferred": "15 candidate detent impulses per 180° direction support 12° cadence and 30 detents per 360°.",
                "confidence": "strong for cadence; hidden pin not visible",
            },
            "IMG_6024": {
                "observed": [
                    "821 decoded frames expose the M track face around f183–207.",
                    "Slide and rotation occur at partial and near-maximum translation.",
                    "Maximum travel is about 0.44L median, about 0.50L peak; fitted point/path interval is about 0.46L.",
                    "Clean rests appear near 12.3°, 134° and 170°.",
                    "The final about 34° turn has three strong impulses, about 11.3° per impulse.",
                    "Reverse slide succeeds; no mechanical jam is demonstrated.",
                ],
                "inferred": "A 48-frame fit supports an M fixed point near normalized (u,v)≈(0.36±0.08,0.45±0.10), with C centerline contact traversing u≈0.30–0.76.",
                "confidence": "medium; shaft and slot walls remain hidden",
            },
        },
        "combinedClaims": [
            {"id": "compound-axis-longitudinal-track", "statement": "Two plates are constrained by a compound axis/longitudinal-track relationship.", "confidence": "high"},
            {"id": "carrier-cover-relative-roles", "statement": "M is hand-supported and likely carries the fixed point; C is the moving cover.", "confidence": "medium", "unknown": "Hidden attachment geometry is not directly visible."},
            {"id": "centerline-contact-path", "statement": "C carries or follows a centerline longitudinal slot/contact path.", "confidence": "medium", "unknown": "Exact concealed slot profile and coupling."},
            {"id": "one-outward-direction", "statement": "From closed, slide opens in one outward direction and returns on the same path; it does not pass beyond the closed stop.", "confidence": "high"},
            {"id": "normalized-travel-range", "statement": "Supported travel is about 0.38–0.46L, up to about 0.50L peak.", "confidence": "medium", "boundary": "21 mm is only consistent with this range, not newly measured."},
            {"id": "twelve-degree-detents", "statement": "Detented rotation is strongly supported at 12° per position, 30 per 360°.", "confidence": "strong", "boundary": "Videos directly show reversible 0↔180° and up to about 170°; full 360° is user-authoritative."},
            {"id": "rotation-across-slide", "statement": "Rotation is observed at partial and near-maximum slide.", "confidence": "high", "unknown": "Access at every exact slot location."},
            {"id": "no-jam-proven", "statement": "No jam is proven; dwell/release behavior is consistent with detent/breakaway resistance.", "confidence": "medium"},
            {"id": "exterior-versus-reverse-face", "statement": "Rails, screws and ball rows belong to the exposed reverse/internal face of M, distinct from its normal clean exterior face.", "confidence": "high", "unknown": "Any remaining conflict with prior concealed-overlap interpretation requires user review."},
        ],
        "reviewQuestion": "这个玩法/机构解读是否符合真实玩具？",
        "boards": [{"path": str(path.relative_to(REPO)), "sha256": sha256(path)} for path in boards],
    }
    analysis_path = OUT / "mechanism-analysis.json"
    analysis_path.write_text(json.dumps(analysis, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return key_manifest, analysis_path


def validate_outputs(frame_payloads, key_manifest, analysis_path, boards):
    metadata = json.loads((INTAKE / "source-metadata.json").read_text(encoding="utf-8"))
    expected = {Path(item["path"]).stem: item for item in metadata["files"]}
    checks = []
    for stem, payload in frame_payloads.items():
        source = VIDEOS / f"{stem}.MOV"
        checks.extend([
            {"id": f"{stem}-source-hash", "status": "pass" if sha256(source) == expected[stem]["sha256"] else "fail"},
            {"id": f"{stem}-frame-count", "status": "pass" if payload["frameCount"] == KEY_FRAMES_COUNT[stem] else "fail"},
            {"id": f"{stem}-pts-monotonic", "status": "pass" if all(a["ptsSeconds"] < b["ptsSeconds"] for a, b in zip(payload["frames"], payload["frames"][1:])) else "fail"},
        ])
    paths = [key_manifest, analysis_path, *boards]
    temporary_root = "/" + "tmp"
    checks.append({"id": "no-temporary-source-paths", "status": "pass" if all(temporary_root not in path.read_text(encoding="utf-8", errors="ignore") for path in [key_manifest, analysis_path]) else "fail"})
    checks.append({"id": "review-assets-present", "status": "pass" if all(path.exists() and path.stat().st_size > 0 for path in paths) else "fail"})
    report = {
        "schemaVersion": 1,
        "gate": "02-analysis",
        "revision": 3,
        "status": "pass" if all(item["status"] == "pass" for item in checks) else "fail",
        "checks": checks,
        "artifacts": [{"path": str(path.relative_to(REPO)), "sha256": sha256(path), "sizeBytes": path.stat().st_size} for path in paths],
    }
    validation_path = OUT / "validation-report.json"
    validation_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if report["status"] != "pass":
        raise RuntimeError(report)
    return validation_path


KEY_FRAMES_COUNT = {"IMG_6022": 426, "IMG_6023": 480, "IMG_6024": 821}


def main():
    frame_payloads = {}
    frame_maps = {}
    crops = {}
    for stem, indices in KEY_FRAMES.items():
        payload, by_index = load_frames(stem)
        frame_payloads[stem] = payload
        frame_maps[stem] = by_index
        crops[stem] = extract_key_frames(stem, indices)
    boards = [
        make_timeline(crops, frame_maps),
        make_identity(crops, frame_maps),
        make_slide(crops, frame_maps),
        make_rotation(crops, frame_maps),
        make_axis_slot(crops, frame_maps),
        make_contradiction(crops, frame_maps),
        make_audio_contact_sheet(),
    ]
    key_manifest, analysis_path = write_analysis(frame_maps, crops, boards)
    validate_outputs(frame_payloads, key_manifest, analysis_path, boards)


if __name__ == "__main__":
    main()
