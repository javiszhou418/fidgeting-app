#!/usr/bin/env python3
"""Extract one clean mechanical Click from the can-coin reference audio.

The source video/audio is intentionally not committed. Pass its decoded WAV as
the first argument. The output keeps one real transient from the press gesture,
while suppressing the continuous music bed, hum, and inter-click ambience.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from scipy.io import wavfile
from scipy.ndimage import median_filter
from scipy.signal import butter, istft, resample_poly, sosfiltfilt, stft


SEARCH_RADIUS_SECONDS = 0.010
OUTPUT_RATE = 48_000

# The press and release are different physical strikes from the same gesture.
# Their onsets are refined automatically inside a small search range.
EVENTS = {
    "press": {
        "search_seconds": 22.142,
        "pre_roll": 0.006,
        "post_roll": 0.110,
        "tail_start": 0.024,
        "tail_tau": 0.025,
        "body_mix": 0.42,
        "background_windows": (
            (21.650, 21.780),
            (22.095, 22.118),
            (22.180, 22.215),
        ),
    },
    "rebound": {
        "search_seconds": 23.256,
        "pre_roll": 0.006,
        "post_roll": 0.088,
        "tail_start": 0.018,
        "tail_tau": 0.018,
        "body_mix": 0.16,
        "background_windows": (
            (21.650, 21.780),
            (23.195, 23.225),
            (23.305, 23.350),
        ),
    },
}


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


def refine_onset(audio: np.ndarray, rate: int, search_seconds: float) -> int:
    mono = np.mean(audio, axis=1)
    band = butter(
        4, (1_000 / (rate / 2), min(14_000 / (rate / 2), 0.98)),
        btype="bandpass", output="sos"
    )
    bright = sosfiltfilt(band, mono)
    center = round(search_seconds * rate)
    radius = round(SEARCH_RADIUS_SECONDS * rate)
    start = max(0, center - radius)
    end = min(len(bright), center + radius)
    smoothing = max(3, round(0.00055 * rate))
    energy = np.convolve(
        bright[start:end] ** 2,
        np.ones(smoothing, dtype=np.float64) / smoothing,
        mode="same",
    )
    return start + int(np.argmax(energy))


def background_samples(
    audio: np.ndarray,
    rate: int,
    windows_spec: tuple[tuple[float, float], ...],
) -> np.ndarray:
    windows = []
    for start, end in windows_spec:
        windows.append(audio[round(start * rate):round(end * rate)])
    return np.concatenate(windows, axis=0)


def purify_channel(
    segment: np.ndarray,
    background: np.ndarray,
    rate: int,
    onset_offset: int,
) -> np.ndarray:
    frame = 512
    overlap = 448
    frequencies, times, signal_stft = stft(
        segment, fs=rate, nperseg=frame, noverlap=overlap,
        boundary="zeros", padded=True
    )
    _, _, background_stft = stft(
        background, fs=rate, nperseg=frame, noverlap=overlap,
        boundary="zeros", padded=True
    )
    magnitude = np.abs(signal_stft)
    noise_floor = np.median(np.abs(background_stft), axis=1, keepdims=True)

    # A sustained musical note forms a horizontal ridge in the spectrogram;
    # the Click forms a short vertical ridge. Median filtering estimates both
    # structures so the mask can favor only the latter.
    harmonic = median_filter(magnitude, size=(1, 17), mode="nearest")
    percussive = median_filter(magnitude, size=(21, 1), mode="nearest")
    percussive_mask = percussive ** 2 / (percussive ** 2 + harmonic ** 2 + 1e-18)

    onset_seconds = onset_offset / rate
    from_onset = times - onset_seconds
    attack_weight = np.clip(1.0 - (from_onset - 0.010) / 0.020, 0.0, 1.0)
    spectral_floor = 0.025 + 0.155 * attack_weight
    subtraction = 1.48 - 0.48 * attack_weight
    body_band = ((frequencies >= 280) & (frequencies <= 2_600))[:, None]
    body_floor = body_band * (0.075 + 0.205 * attack_weight[None, :])
    protected_floor = np.maximum(spectral_floor[None, :], body_floor)
    reduced = np.maximum(
        magnitude - subtraction[None, :] * noise_floor,
        magnitude * protected_floor,
    )
    denoise_mask = np.power(reduced / (magnitude + 1e-18), 1.18)
    structure_mask = 0.13 + 0.87 * percussive_mask
    structure_mask = attack_weight[None, :] + (1.0 - attack_weight[None, :]) * structure_mask
    cleaned_stft = signal_stft * denoise_mask * structure_mask

    _, restored = istft(
        cleaned_stft, fs=rate, nperseg=frame, noverlap=overlap,
        input_onesided=True, boundary=True
    )
    return restored[: len(segment)]


def extract_click(source_path: Path, event_name: str) -> tuple[np.ndarray, float]:
    event = EVENTS[event_name]
    rate, audio = normalized_audio(source_path)
    onset = refine_onset(audio, rate, event["search_seconds"])
    start = max(0, onset - round(event["pre_roll"] * rate))
    end = min(len(audio), onset + round(event["post_roll"] * rate))
    segment = audio[start:end].copy()
    background = background_samples(audio, rate, event["background_windows"])
    onset_offset = onset - start

    cleaned = np.column_stack([
        purify_channel(segment[:, channel], background[:, channel], rate, onset_offset)
        for channel in range(segment.shape[1])
    ])

    high_pass = butter(4, 155 / (rate / 2), btype="highpass", output="sos")
    low_pass = butter(3, min(18_000 / (rate / 2), 0.98), btype="lowpass", output="sos")
    cleaned = sosfiltfilt(high_pass, cleaned, axis=0)
    cleaned = sosfiltfilt(low_pass, cleaned, axis=0)

    # Spectral separation correctly removes the tonal bed, but can also make a
    # tiny metal part feel unnaturally paper-thin. Restore only the first 18 ms
    # of the real 280–2600 Hz impact body; its very short gate cannot carry a
    # sustained musical note into the result.
    body_filter = butter(
        3, (280 / (rate / 2), 2_600 / (rate / 2)),
        btype="bandpass", output="sos"
    )
    impact_body = sosfiltfilt(body_filter, segment, axis=0)
    body_times = (np.arange(len(segment)) - onset_offset) / rate
    body_gate = np.ones(len(segment), dtype=np.float64)
    body_tail = body_times > 0.018
    body_gate[body_tail] = np.exp(-(body_times[body_tail] - 0.018) / 0.006)
    body_gate[body_times < -0.003] = 0
    attack_slice = slice(max(0, onset_offset), min(len(segment), onset_offset + round(0.022 * rate)))
    clean_rms = np.sqrt(np.mean(cleaned[attack_slice] ** 2)) + 1e-12
    body_rms = np.sqrt(np.mean(impact_body[attack_slice] ** 2)) + 1e-12
    impact_body *= min(1.0, event["body_mix"] * clean_rms / body_rms)
    cleaned += impact_body * body_gate[:, None]
    cleaned -= np.mean(cleaned, axis=0, keepdims=True)

    # Keep the physical strike intact, then close the gate before any music can
    # reappear. This is a single Click, not a loop or a synthesized replacement.
    seconds = np.arange(len(cleaned), dtype=np.float64) / rate
    onset_seconds = onset_offset / rate
    envelope = np.ones(len(cleaned), dtype=np.float64)
    fade_in = max(2, round(0.0015 * rate))
    envelope[:fade_in] = np.sin(np.linspace(0, np.pi / 2, fade_in)) ** 2
    tail_start = onset_seconds + event["tail_start"]
    tail = seconds > tail_start
    envelope[tail] *= np.exp(-(seconds[tail] - tail_start) / event["tail_tau"])
    fade_out = min(len(cleaned), round(0.014 * rate))
    envelope[-fade_out:] *= np.cos(np.linspace(0, np.pi / 2, fade_out)) ** 2
    cleaned *= envelope[:, None]

    if rate != OUTPUT_RATE:
        common = np.gcd(rate, OUTPUT_RATE)
        cleaned = resample_poly(cleaned, OUTPUT_RATE // common, rate // common, axis=0)

    peak = np.max(np.abs(cleaned)) + 1e-12
    cleaned *= (10 ** (-1.5 / 20)) / peak
    return np.clip(cleaned, -1.0, 1.0), onset / rate


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="Decoded full reference WAV")
    parser.add_argument("output", type=Path, help="Destination purified Click WAV")
    parser.add_argument(
        "--event", choices=tuple(EVENTS), default="press",
        help="Physical endpoint to extract (default: press)",
    )
    args = parser.parse_args()
    click, onset = extract_click(args.source, args.event)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    wavfile.write(args.output, OUTPUT_RATE, np.round(click * 32767).astype(np.int16))
    print(
        f"wrote {args.output} ({len(click) / OUTPUT_RATE:.3f}s, "
        f"{OUTPUT_RATE} Hz, stereo; {args.event} source onset {onset:.5f}s)"
    )


if __name__ == "__main__":
    main()
