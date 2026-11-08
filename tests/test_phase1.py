from pathlib import Path
import io, sys, unittest, wave, json
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from phase1 import measure, split_for

CFG = json.loads((ROOT / "configs/phase1.json").read_text(encoding="utf-8"))


def wav(a):
    b = io.BytesIO()
    with wave.open(b, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(16000)
        w.writeframes(np.asarray(a, dtype="<i2").tobytes())
    return b.getvalue()


class AuditTests(unittest.TestCase):
    def test_silent_signal(self):
        m = measure(wav(np.zeros(16000)), CFG)
        self.assertTrue(m["all_zero"])
        self.assertEqual(m["duration_s"], 1)
        self.assertEqual(m["low_energy_frame_fraction"], 1)

    def test_amplitude_and_clipping(self):
        m = measure(wav(np.tile([-32768, 32767], 8000)), CFG)
        self.assertEqual(m["clipping_fraction"], 1)
        self.assertEqual(m["peak"], 1)

    def test_tone_rms(self):
        x = np.round(16384 * np.sin(2 * np.pi * 1000 * np.arange(16000) / 16000))
        m = measure(wav(x), CFG)
        self.assertAlmostEqual(m["rms"], 0.5 / np.sqrt(2), places=4)
        self.assertAlmostEqual(m["rms_dbfs"], -9.0309, places=3)

    def test_invalid_file(self):
        with self.assertRaises(Exception):
            measure(b"not wave", CFG)

    def test_saved_integrity(self):
        d = pd.read_csv(ROOT / "tables/inventory.csv")
        self.assertEqual(len(d), 8000)
        self.assertEqual(d.path.nunique(), 8000)
        self.assertEqual(d.groupby("speaker_id").split.nunique().max(), 1)
        self.assertEqual(d.groupby("pcm_sha256").split.nunique().max(), 1)
        self.assertFalse(d[d.use_for_analysis].pcm_sha256.duplicated().any())
        self.assertTrue((pd.crosstab(d.label, d.split) > 0).all().all())
        self.assertTrue(
            (d.split == d.split_group.map(lambda x: split_for(x, CFG))).all()
        )

    def test_examples_training_only(self):
        d = pd.read_csv(ROOT / "tables/plot_examples.csv")
        self.assertTrue((d.split == "train").all())
        self.assertEqual(len(d), 24)
        self.assertTrue(d.use_for_analysis.all())


if __name__ == "__main__":
    unittest.main()
