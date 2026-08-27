#!/usr/bin/env python3
"""Generate frame-accurate surveys for the three user mechanism videos."""
from __future__ import annotations

import csv
import hashlib
import json
import math
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont


OUT = Path(__file__).resolve().parent
MODEL = OUT.parents[2]
REPO = OUT.parents[7]
INTAKE = MODEL / "evidence/01-intake/rev-003"
VIDEOS = INTAKE / "user-mechanism-videos"
METADATA = INTAKE / "source-metadata.json"
CONFIG = {
    "IMG_6022": {"filename": "IMG_6022.MOV", "frameCount": 426, "surveyStep": 25},
    "IMG_6023": {"filename": "IMG_6023.MOV", "frameCount": 480, "surveyStep": 24},
    "IMG_6024": {"filename": "IMG_6024.MOV", "frameCount": 821, "surveyStep": 32},
}


def font(size, bold=False):
    path = "/System/Library/Fonts/STHeiti Medium.ttc" if bold else "/System/Library/Fonts/STHeiti Light.ttc"
    return ImageFont.truetype(path, size=size)


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(command, *, stdout=None):
    result = subprocess.run(command, check=True, stdout=stdout, stderr=subprocess.PIPE)
    return result


def frame_manifest(video, expected_count, stem):
    command = [
        "ffprobe", "-v", "error", "-select_streams", "v:0", "-show_frames",
        "-show_entries", "frame=best_effort_timestamp_time,pkt_duration_time,pict_type,key_frame",
        "-of", "json", str(video),
    ]
    payload = json.loads(subprocess.run(command, check=True, capture_output=True, text=True).stdout)
    frames = []
    for index, frame in enumerate(payload["frames"]):
        frames.append({
            "frameIndex": index,
            "ptsSeconds": round(float(frame["best_effort_timestamp_time"]), 6),
            "durationSeconds": round(float(frame.get("pkt_duration_time", 0.0)), 6),
            "keyFrame": bool(frame.get("key_frame", 0)),
            "pictureType": frame.get("pict_type"),
        })
    if len(frames) != expected_count:
        raise RuntimeError(f"{stem}: expected {expected_count} frames, got {len(frames)}")
    manifest_dir = OUT / "frame-manifests"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    json_path = manifest_dir / f"{stem}-frames.json"
    csv_path = manifest_dir / f"{stem}-frames.csv"
    json_path.write_text(json.dumps({
        "schemaVersion": 1,
        "video": str(video.relative_to(REPO)),
        "videoSha256": sha256(video),
        "frameCount": len(frames),
        "firstPtsSeconds": frames[0]["ptsSeconds"],
        "lastPtsSeconds": frames[-1]["ptsSeconds"],
        "frames": frames,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=frames[0].keys())
        writer.writeheader()
        writer.writerows(frames)
    return frames, json_path, csv_path


def extract_survey(video, frames, step, stem):
    selected = list(range(0, len(frames), step))
    if selected[-1] != len(frames) - 1:
        selected.append(len(frames) - 1)
    target = OUT / "survey-frames" / stem
    target.mkdir(parents=True, exist_ok=True)
    for old in target.glob("*.png"):
        old.unlink()
    expression = "+".join(f"eq(n\\,{index})" for index in selected)
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
        "-vf", f"select='{expression}',scale=405:720:flags=lanczos",
        "-fps_mode", "vfr", str(target / "%03d.png"),
    ])
    extracted = sorted(target.glob("*.png"))
    if len(extracted) != len(selected):
        raise RuntimeError(f"{stem}: expected {len(selected)} survey frames, got {len(extracted)}")
    columns = 5
    panel_width, panel_height = 445, 790
    rows = math.ceil(len(selected) / columns)
    board = Image.new("RGB", (columns * panel_width + 60, rows * panel_height + 150), (6, 9, 13))
    draw = ImageDraw.Draw(board)
    draw.text((30, 24), f"{stem} 全片帧索引调查｜每 {step} 帧 + 最后一帧", font=font(38, True), fill=(245, 248, 252))
    draw.text((30, 78), "编号为解码帧索引；时间来自 ffprobe PTS，不用估算帧率换算。", font=font(23), fill=(178, 192, 207))
    for order, (frame_index, path) in enumerate(zip(selected, extracted)):
        x = 30 + (order % columns) * panel_width
        y = 130 + (order // columns) * panel_height
        image = Image.open(path).convert("RGB")
        board.paste(image, (x, y))
        pts = frames[frame_index]["ptsSeconds"]
        draw.text((x, y + 730), f"f{frame_index:03d}  {pts:07.3f}s", font=font(25, True), fill=(72, 222, 238))
    board_path = OUT / f"{stem}-frame-survey.png"
    board.save(board_path)
    for path in extracted:
        path.unlink()
    target.rmdir()
    return selected, board_path


def audio_evidence(video, stem):
    command = [
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(video),
        "-map", "0:a:0", "-ac", "1", "-ar", "48000", "-f", "f32le", "pipe:1",
    ]
    raw = subprocess.run(command, check=True, capture_output=True).stdout
    samples = np.frombuffer(raw, dtype="<f4")
    hop = 240
    count = len(samples) // hop
    windows = samples[:count * hop].reshape(count, hop)
    rms = np.sqrt(np.mean(windows * windows, axis=1) + 1e-12)
    times = (np.arange(count) * hop + hop / 2) / 48000.0
    normalized = rms / max(float(np.percentile(rms, 99.8)), 1e-9)
    normalized = np.clip(normalized, 0, 1)
    threshold = max(0.18, float(np.percentile(normalized, 92)))
    candidates = []
    minimum_gap = int(0.10 / (hop / 48000.0))
    for index in range(1, len(normalized) - 1):
        if normalized[index] < threshold:
            continue
        if normalized[index] >= normalized[index - 1] and normalized[index] > normalized[index + 1]:
            if not candidates or index - candidates[-1] >= minimum_gap:
                candidates.append(index)
            elif normalized[index] > normalized[candidates[-1]]:
                candidates[-1] = index
    csv_path = OUT / f"{stem}-audio-impulses.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["candidateIndex", "timeSeconds", "normalizedRms"])
        for candidate_index, sample_index in enumerate(candidates):
            writer.writerow([candidate_index, f"{times[sample_index]:.6f}", f"{normalized[sample_index]:.6f}"])
    width, height = 2400, 620
    board = Image.new("RGB", (width, height), (6, 9, 13))
    draw = ImageDraw.Draw(board)
    draw.text((40, 24), f"{stem} 音频机械瞬态调查", font=font(36, True), fill=(245, 248, 252))
    draw.text((40, 72), "5 ms RMS；青线为波形包络，橙线为自动候选阈值。候选峰不自动等同一个 detent。", font=font(23), fill=(178, 192, 207))
    left, top, right, bottom = 60, 125, width - 45, height - 80
    draw.rectangle((left, top, right, bottom), outline=(62, 78, 92), width=2)
    threshold_y = bottom - threshold * (bottom - top)
    draw.line((left, threshold_y, right, threshold_y), fill=(245, 163, 68), width=2)
    points = []
    for index in range(len(normalized)):
        x = left + index / max(1, len(normalized) - 1) * (right - left)
        y = bottom - normalized[index] * (bottom - top)
        points.append((x, y))
    if len(points) > 1:
        draw.line(points, fill=(54, 218, 235), width=2)
    for sample_index in candidates:
        x = left + sample_index / max(1, len(normalized) - 1) * (right - left)
        y = bottom - normalized[sample_index] * (bottom - top)
        draw.ellipse((x - 3, y - 3, x + 3, y + 3), fill=(255, 208, 94))
    duration = len(samples) / 48000.0
    for second in np.linspace(0, duration, 8):
        x = left + second / duration * (right - left)
        draw.line((x, bottom, x, bottom + 8), fill=(120, 136, 151), width=1)
        draw.text((x - 24, bottom + 14), f"{second:.1f}s", font=font(18), fill=(158, 173, 188))
    plot_path = OUT / f"{stem}-audio-impulses.png"
    board.save(plot_path)
    return csv_path, plot_path, len(candidates)


def transcode_proxy(video, stem):
    proxy_dir = OUT / "playback-proxies"
    proxy_dir.mkdir(parents=True, exist_ok=True)
    path = proxy_dir / f"{stem}-review-h264.mp4"
    run([
        "ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", str(video),
        "-map", "0:v:0", "-map", "0:a:0", "-vf", "scale=720:-2:flags=lanczos,format=yuv420p",
        "-c:v", "libx264", "-preset", "medium", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart",
        "-metadata:s:v:0", "rotate=0", str(path),
    ])
    return path


def main():
    metadata = json.loads(METADATA.read_text(encoding="utf-8"))
    metadata_by_name = {Path(item["path"]).name: item for item in metadata["files"]}
    report = {
        "schemaVersion": 1,
        "gate": "02-analysis",
        "revision": 3,
        "generator": str(Path(__file__).relative_to(REPO)),
        "videos": {},
    }
    for stem, config in CONFIG.items():
        video = VIDEOS / config["filename"]
        if not video.exists():
            raise FileNotFoundError(video)
        source = metadata_by_name[config["filename"]]
        if sha256(video) != source["sha256"]:
            raise RuntimeError(f"{stem}: source hash changed")
        frames, json_path, csv_path = frame_manifest(video, config["frameCount"], stem)
        selected, survey_path = extract_survey(video, frames, config["surveyStep"], stem)
        impulse_csv, impulse_plot, impulse_count = audio_evidence(video, stem)
        proxy = transcode_proxy(video, stem)
        report["videos"][stem] = {
            "sourceAssetId": source["id"],
            "sourcePath": str(video.relative_to(REPO)),
            "sourceSha256": source["sha256"],
            "frameCount": len(frames),
            "durationSeconds": source["durationSeconds"],
            "manifestJson": str(json_path.relative_to(REPO)),
            "manifestCsv": str(csv_path.relative_to(REPO)),
            "surveyFrameIndices": selected,
            "surveyBoard": str(survey_path.relative_to(REPO)),
            "audioImpulseCsv": str(impulse_csv.relative_to(REPO)),
            "audioImpulsePlot": str(impulse_plot.relative_to(REPO)),
            "automaticImpulseCandidateCount": impulse_count,
            "playbackProxy": str(proxy.relative_to(REPO)),
            "playbackProxySha256": sha256(proxy),
        }
    (OUT / "frame-survey-report.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
