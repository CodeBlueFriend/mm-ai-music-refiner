from __future__ import annotations

import array
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path
from typing import Any

LOSSY_CODECS = {"mp3", "aac", "opus", "vorbis", "ac3", "eac3", "wma"}
MAJOR_PROFILE = [6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88]
MINOR_PROFILE = [6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17]
NOTE_NAMES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]


class AnalysisError(RuntimeError):
    pass


def require_binary(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise AnalysisError(f"Required binary not found: {name}")
    return path


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def probe(path: Path) -> dict[str, Any]:
    result = run([require_binary("ffprobe"), "-v", "error", "-show_format", "-show_streams", "-of", "json", str(path)])
    if result.returncode:
        raise AnalysisError(f"ffprobe could not read the audio: {result.stderr.strip()}")
    raw = json.loads(result.stdout)
    stream = next((item for item in raw.get("streams", []) if item.get("codec_type") == "audio"), None)
    if not stream:
        raise AnalysisError("No audio stream found")
    fmt = raw.get("format", {})
    codec = stream.get("codec_name", "unknown")
    return {
        "container": fmt.get("format_name", "unknown"),
        "codec": codec,
        "lossy": codec in LOSSY_CODECS,
        "sample_rate_hz": _int_or_none(stream.get("sample_rate")),
        "channels": stream.get("channels"),
        "channel_layout": stream.get("channel_layout"),
        "sample_format": stream.get("sample_fmt"),
        "bits_per_sample": _int_or_none(stream.get("bits_per_raw_sample") or stream.get("bits_per_sample")),
        "duration_sec": _float_or_none(fmt.get("duration") or stream.get("duration")),
        "bit_rate_bps": _int_or_none(fmt.get("bit_rate") or stream.get("bit_rate")),
        "tags": {key: value for key, value in fmt.get("tags", {}).items() if key.lower() in {"title", "artist", "album", "date", "encoder"}},
    }


def _int_or_none(value: Any) -> int | None:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def loudness(path: Path) -> dict[str, float | None]:
    result = run([require_binary("ffmpeg"), "-hide_banner", "-nostats", "-i", str(path), "-filter_complex", "ebur128=peak=true", "-f", "null", "-"])
    text = result.stderr
    summary = text.rsplit("Summary:", 1)[-1]
    def last(pattern: str) -> float | None:
        matches = re.findall(pattern, summary)
        return float(matches[-1]) if matches else None
    return {
        "integrated_lufs": last(r"I:\s*(-?(?:inf|\d+(?:\.\d+)?))\s*LUFS") if "-inf" not in summary else None,
        "loudness_range_lu": last(r"LRA:\s*(\d+(?:\.\d+)?)\s*LU"),
        "true_peak_dbfs": last(r"Peak:\s*(-?(?:inf|\d+(?:\.\d+)?))\s*dBFS") if "Peak:       -inf" not in summary else None,
    }


def decode_proxy(path: Path, output: Path, sample_rate: int = 11025) -> None:
    result = run([require_binary("ffmpeg"), "-hide_banner", "-loglevel", "error", "-y", "-i", str(path), "-vn", "-ac", "1", "-ar", str(sample_rate), "-c:a", "pcm_s16le", str(output)])
    if result.returncode:
        raise AnalysisError(f"Proxy decode failed: {result.stderr.strip()}")


def read_pcm16(path: Path, max_seconds: float = 360.0) -> tuple[int, list[float]]:
    with wave.open(str(path), "rb") as handle:
        if handle.getsampwidth() != 2 or handle.getnchannels() != 1:
            raise AnalysisError("Internal proxy must be mono PCM16")
        rate = handle.getframerate()
        frames = handle.readframes(min(handle.getnframes(), int(rate * max_seconds)))
    values = array.array("h")
    values.frombytes(frames)
    if sys.byteorder == "big":
        values.byteswap()
    return rate, [value / 32768.0 for value in values]


def basic_metrics(samples: list[float]) -> dict[str, float | int | None]:
    if not samples:
        return {"sample_peak_dbfs": None, "rms_dbfs": None, "crest_factor_db": None, "dc_offset": None, "clipped_sample_ratio": None}
    peak = max(abs(value) for value in samples)
    rms = math.sqrt(sum(value * value for value in samples) / len(samples))
    dc = sum(samples) / len(samples)
    clipped = sum(1 for value in samples if abs(value) >= 0.999) / len(samples)
    return {
        "sample_peak_dbfs": _db(peak),
        "rms_dbfs": _db(rms),
        "crest_factor_db": 20 * math.log10(peak / rms) if peak and rms else None,
        "dc_offset": dc,
        "clipped_sample_ratio": clipped,
        "analyzed_samples": len(samples),
    }


def _db(value: float) -> float | None:
    return 20 * math.log10(value) if value > 0 else None


def estimate_bpm(samples: list[float], sample_rate: int) -> tuple[float | None, float]:
    frame = 1024
    hop = 512
    if len(samples) < frame * 8:
        return None, 0.0
    energy = []
    for start in range(0, len(samples) - frame, hop):
        block = samples[start:start + frame]
        energy.append(sum(abs(value) for value in block) / frame)
    onset = [max(0.0, energy[index] - energy[index - 1]) for index in range(1, len(energy))]
    mean = sum(onset) / len(onset)
    onset = [value - mean for value in onset]
    candidates = []
    for lag in range(max(2, round(60 * sample_rate / (200 * hop))), max(3, round(60 * sample_rate / (60 * hop))) + 1):
        score = sum(onset[index] * onset[index - lag] for index in range(lag, len(onset)))
        candidates.append((score, lag))
    if not candidates:
        return None, 0.0
    candidates.sort(reverse=True)
    best_score, best_lag = candidates[0]
    positive = [max(0.0, score) for score, _ in candidates]
    confidence = best_score / (sum(positive) + 1e-12)
    bpm = 60 * sample_rate / (best_lag * hop)
    return round(bpm, 2), round(min(1.0, confidence * 3), 3)


def goertzel_power(block: list[float], sample_rate: int, frequency: float) -> float:
    coefficient = 2.0 * math.cos(2.0 * math.pi * frequency / sample_rate)
    prev = prev2 = 0.0
    for value in block:
        current = value + coefficient * prev - prev2
        prev2, prev = prev, current
    return max(0.0, prev2 * prev2 + prev * prev - coefficient * prev * prev2)


def spectral_estimates(samples: list[float], sample_rate: int) -> dict[str, Any]:
    window = 4096
    if len(samples) < window:
        return {"key": None, "key_confidence": 0.0, "tuning_offset_cents": None, "tuning_confidence": 0.0}
    starts = [int((len(samples) - window) * fraction) for fraction in (0.12, 0.35, 0.58, 0.81)]
    blocks = []
    for start in starts:
        raw = samples[start:start + window]
        blocks.append([value * (0.5 - 0.5 * math.cos(2 * math.pi * index / (window - 1))) for index, value in enumerate(raw)])
    shifts = list(range(-40, 41, 5))
    shift_scores = []
    for shift in shifts:
        total = 0.0
        for midi in range(45, 82):
            frequency = 440.0 * 2 ** ((midi - 69 + shift / 100) / 12)
            total += sum(goertzel_power(block, sample_rate, frequency) for block in blocks)
        shift_scores.append(total)
    best_index = max(range(len(shifts)), key=lambda index: shift_scores[index])
    tuning = shifts[best_index]
    sorted_scores = sorted(shift_scores, reverse=True)
    tuning_conf = (sorted_scores[0] - sorted_scores[1]) / (sorted_scores[0] + 1e-12) if len(sorted_scores) > 1 else 0.0
    chroma = [0.0] * 12
    for midi in range(36, 85):
        frequency = 440.0 * 2 ** ((midi - 69 + tuning / 100) / 12)
        chroma[midi % 12] += sum(goertzel_power(block, sample_rate, frequency) for block in blocks)
    total = sum(chroma)
    if not total:
        return {"key": None, "key_confidence": 0.0, "tuning_offset_cents": None, "tuning_confidence": 0.0}
    chroma = [value / total for value in chroma]
    choices = []
    for tonic in range(12):
        for mode, profile in (("major", MAJOR_PROFILE), ("minor", MINOR_PROFILE)):
            rotated = profile[-tonic:] + profile[:-tonic] if tonic else profile
            score = _correlation(chroma, rotated)
            choices.append((score, tonic, mode))
    choices.sort(reverse=True)
    best, tonic, mode = choices[0]
    confidence = max(0.0, min(1.0, (best - choices[1][0]) * 2.5))
    return {
        "key": f"{NOTE_NAMES[tonic]} {mode}",
        "key_confidence": round(confidence, 3),
        "tuning_offset_cents": tuning,
        "tuning_confidence": round(max(0.0, min(1.0, tuning_conf * 8)), 3),
    }


def _correlation(left: list[float], right: list[float]) -> float:
    left_mean = sum(left) / len(left)
    right_mean = sum(right) / len(right)
    numerator = sum((a - left_mean) * (b - right_mean) for a, b in zip(left, right))
    denominator = math.sqrt(sum((a - left_mean) ** 2 for a in left) * sum((b - right_mean) ** 2 for b in right))
    return numerator / denominator if denominator else 0.0


def analyze_audio(path: Path) -> dict[str, Any]:
    path = path.expanduser().resolve()
    if not path.is_file():
        raise AnalysisError(f"Input file not found: {path.name}")
    metadata = probe(path)
    measured_loudness = loudness(path)
    with tempfile.TemporaryDirectory(prefix="mm_music_refiner_") as temporary:
        proxy = Path(temporary) / "proxy.wav"
        decode_proxy(path, proxy)
        rate, samples = read_pcm16(proxy)
    metrics = basic_metrics(samples)
    bpm, bpm_confidence = estimate_bpm(samples, rate)
    musical = spectral_estimates(samples, rate)
    metrics.update(measured_loudness)
    metrics.update({"bpm": bpm, "bpm_confidence": bpm_confidence, **musical})
    return {
        "schema_version": "1.0.0",
        "engine_version": "0.1.0",
        "source": {"filename": path.name, "sha256": sha256_file(path), "size_bytes": path.stat().st_size},
        "metadata": metadata,
        "metrics": metrics,
        "limitations": [
            "BPM、Key 与 Tuning 为快速扫描估算，复杂节奏、无调性材料或短文件可能低置信。",
            "快速扫描不执行分轨、人声转写、来源鉴定或任何音频修改。",
        ],
    }
