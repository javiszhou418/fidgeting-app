#!/usr/bin/env python3
"""Extract the complete press gesture from the user-provided can-coin video.

The source video/audio is intentionally not committed. Pass a locally decoded WAV
as the first argument; only the short, denoised press gesture is written.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, istft, resample_poly, sosfiltfilt, stft


PRESS_START_SECONDS = 21.815
PRESS_END_SECONDS = 23.380
NOISE_START_SECONDS = 21.650
NOISE_END_SECONDS = 21.780
OUTPUT_RATE = 48_000


def normalized_audio(path: Path) -> tuple[int, np.ndarray]:
    rate, samples = wavfile.read(path)
    source = np.asarray(samples)
    audio = source.astype(np.float64)
    if np.issubdtype(source.dtype, np.integer):
        info = np.iinfo(source.dtype)
        audio /= max(abs(info.min), info.max)
    if audio.ndim == 1:
        audio = np.column_stack((audio, audio))
    return rate, audio


def gentle_spectral_subtract(segment: np.ndarray, noise: np.ndarray, rate: int) -> np.ndarray:
    cleaned_channels: list[np.ndarray] = []
    frame = 1024
    overlap = 768
    for channel in range(segment.shape[1]):
        _, _, noise_stft = stft(
            noise[:, channel], fs=rate, nperseg=frame, noverlap=overlap,
            boundary="zeros", padded=True
        )
        _, _, signal_stft = stft(
            segment[:, channel], fs=rate, nperseg=frame, noverlap=overlap,
            boundary="zeros", padded=True
        )
        noise_floor = np.median(np.abs(noise_stft), axis=1, keepdims=True)
        magnitude = np.abs(signal_stft)
        reduced = np.maximum(magnitude - 0.52 * noise_floor, magnitude * 0.16)
        mask = np.power(reduced / (magnitude + 1e-12), 1.08)
        _, restored = istft(
            signal_stft * mask, fs=rate, nperseg=frame, noverlap=overlap,
            input_onesided=True, boundary=True
        )
        cleaned_channels.append(restored[: len(segment)])
    return np.column_stack(cleaned_channels)


def extract_press(source_path: Path) -> np.ndarray:
    rate, audio = normalized_audio(source_path)
    noise = audio[round(NOISE_START_SECONDS * rate):round(NOISE_END_SECONDS * rate)]
    press = audio[round(PRESS_START_SECONDS * rate):round(PRESS_END_SECONDS * rate)].copy()
    press = gentle_spectral_subtract(press, noise, rate)

    high_pass = butter(3, 82 / (rate / 2), btype="highpass", output="sos")
    low_pass = butter(3, min(18_500 / (rate / 2), 0.98), btype="lowpass", output="sos")
    press = sosfiltfilt(high_pass, press, axis=0)
    press = sosfiltfilt(low_pass, press, axis=0)
    press -= np.mean(press, axis=0, keepdims=True)

    if rate != OUTPUT_RATE:
        common = np.gcd(rate, OUTPUT_RATE)
        press = resample_poly(press, OUTPUT_RATE // common, rate // common, axis=0)

    fade_in = min(len(press), round(0.004 * OUTPUT_RATE))
    fade_out = min(len(press), round(0.065 * OUTPUT_RATE))
    envelope = np.ones(len(press), dtype=np.float64)
    envelope[:fade_in] = np.sin(np.linspace(0, np.pi / 2, fade_in)) ** 2
    envelope[-fade_out:] = np.cos(np.linspace(0, np.pi / 2, fade_out)) ** 2
    press *= envelope[:, None]

    peak = np.max(np.abs(press)) + 1e-12
    press *= (10 ** (-1.5 / 20)) / peak
    return np.clip(press, -1.0, 1.0)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="Decoded full reference WAV")
    parser.add_argument("output", type=Path, help="Destination press WAV")
    args = parser.parse_args()
    press = extract_press(args.source)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(args.output, OUTPUT_RATE, np.round(press * 32767).astype(np.int16))
    print(f"wrote {args.output} ({len(press) / OUTPUT_RATE:.3f}s, {OUTPUT_RATE} Hz, stereo)")


if __name__ == "__main__":
    main()
