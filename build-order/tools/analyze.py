"""Beat/section analysis for the music video timeline. Writes analysis/beats.json."""
import json, sys
import numpy as np, librosa

src = sys.argv[1] if len(sys.argv) > 1 else "audio/one_more_game.mp3"
y, sr = librosa.load(src, sr=22050, mono=True)
dur = len(y) / sr
hop = 512

tempo, beats = librosa.beat.beat_track(y=y, sr=sr, hop_length=hop, units="frames")
beat_t = librosa.frames_to_time(beats, sr=sr, hop_length=hop)

onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop)
onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr, hop_length=hop, units="time")

# Downbeat guess: pick the beat phase (mod 4) with the most low-end energy.
S = np.abs(librosa.stft(y, hop_length=hop))
low = S[: int(150 / (sr / 2) * S.shape[0])].sum(axis=0)
phase = int(np.argmax([low[beats[p::4]].mean() for p in range(4)]))
downbeats = beat_t[phase::4]

# Energy curve at 10 Hz for driving camera shake / flashes.
rms = librosa.feature.rms(y=y, hop_length=hop)[0]
t_rms = librosa.frames_to_time(np.arange(len(rms)), sr=sr, hop_length=hop)
grid = np.arange(0, dur, 0.1)
energy = np.interp(grid, t_rms, rms / rms.max())

# Section boundaries: agglomerative clustering on beat-synced chroma + MFCC.
chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=hop)
mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop, n_mfcc=13)
feat = np.vstack([librosa.util.normalize(chroma), librosa.util.normalize(mfcc)])
sync = librosa.util.sync(feat, beats, aggregate=np.median)
k = 14
bounds = librosa.segment.agglomerative(sync, k)
bound_t = [0.0] + [float(beat_t[min(b, len(beat_t) - 1)]) for b in bounds[1:]] + [dur]

out = {
    "duration": dur,
    "tempo": float(np.atleast_1d(tempo)[0]),
    "beats": [round(float(t), 3) for t in beat_t],
    "downbeats": [round(float(t), 3) for t in downbeats],
    "onsets": [round(float(t), 3) for t in onsets],
    "energy_10hz": [round(float(e), 3) for e in energy],
    "section_bounds": [round(t, 2) for t in bound_t],
}
json.dump(out, open("analysis/beats.json", "w"))
print(f"duration {dur:.1f}s tempo {out['tempo']:.1f} beats {len(beat_t)} downbeat phase {phase}")
for a, b in zip(bound_t, bound_t[1:]):
    seg = energy[(grid >= a) & (grid < b)]
    print(f"{a:6.1f}-{b:6.1f}  energy {seg.mean():.2f}")
