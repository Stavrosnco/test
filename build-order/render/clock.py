"""Song timing helpers built from analysis/beats.json."""
import json
from pathlib import Path
import numpy as np

class Clock:
    def __init__(self, path=Path(__file__).parent.parent / "analysis/beats.json"):
        d = json.loads(Path(path).read_text())
        self.beats = np.array(d["beats"])
        self.downbeats = np.array(d["downbeats"])
        self.energy = np.array(d["energy_10hz"])
        self.duration = d["duration"]

    def beat_pos(self, t):
        """Continuous beat count (beat i at self.beats[i])."""
        i = int(np.clip(np.searchsorted(self.beats, t) - 1, 0, len(self.beats) - 2))
        a, b = self.beats[i], self.beats[i + 1]
        return i + (t - a) / (b - a)

    def time_of(self, beat):
        i = int(np.clip(np.floor(beat), 0, len(self.beats) - 2))
        a, b = self.beats[i], self.beats[i + 1]
        return a + (beat - i) * (b - a)

    def pulse(self, t, decay=7.0):
        """1 on each beat, decaying to 0 before the next."""
        i = np.searchsorted(self.beats, t) - 1
        return float(np.exp(-(t - self.beats[i]) * decay)) if i >= 0 else 0.0

    def downpulse(self, t, decay=5.0):
        i = np.searchsorted(self.downbeats, t) - 1
        return float(np.exp(-(t - self.downbeats[i]) * decay)) if i >= 0 else 0.0

    def nrg(self, t):
        return float(np.interp(t * 10, np.arange(len(self.energy)), self.energy))

def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)

def lerp(a, b, x):
    return a + (b - a) * x
