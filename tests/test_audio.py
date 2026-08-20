import math
import tempfile
import unittest
import wave
from pathlib import Path

from mm_music_refiner.audio import analyze_audio, basic_metrics, estimate_bpm
from mm_music_refiner.issues import build_issues


def write_sine(path: Path, frequency=440.0, seconds=2.0, rate=11025, amplitude=0.5):
    frames = bytearray()
    for index in range(int(seconds * rate)):
        value = int(32767 * amplitude * math.sin(2 * math.pi * frequency * index / rate))
        frames.extend(value.to_bytes(2, "little", signed=True))
    with wave.open(str(path), "wb") as handle:
        handle.setnchannels(1)
        handle.setsampwidth(2)
        handle.setframerate(rate)
        handle.writeframes(frames)


class AudioTests(unittest.TestCase):
    def test_basic_metrics(self):
        result = basic_metrics([0.5, -0.5, 0.25, -0.25])
        self.assertAlmostEqual(result["sample_peak_dbfs"], -6.0206, places=2)
        self.assertEqual(result["clipped_sample_ratio"], 0)

    def test_click_bpm(self):
        rate = 11025
        samples = [0.0] * (rate * 12)
        for beat in range(24):
            start = int(beat * rate * 0.5)
            for offset in range(80):
                samples[start + offset] = 1.0 - offset / 80
        bpm, confidence = estimate_bpm(samples, rate)
        self.assertTrue(105 <= bpm <= 135, bpm)
        self.assertGreater(confidence, 0.1)

    def test_end_to_end_wav(self):
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "a440.wav"
            write_sine(source)
            result = analyze_audio(source)
            self.assertEqual(result["metadata"]["codec"], "pcm_s16le")
            self.assertEqual(len(result["source"]["sha256"]), 64)
            self.assertIn("integrated_lufs", result["metrics"])
            self.assertIsInstance(build_issues(result), list)


if __name__ == "__main__":
    unittest.main()
