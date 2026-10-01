"""Render a time range of the song to an mp4 with audio.

python render_clip.py --scene chant --t0 20.898 --t1 35.271 --out ../out/chant_preview.mp4
"""
import argparse, subprocess, time
from pathlib import Path
import numpy as np
from clock import Clock
import fx, hud

ap = argparse.ArgumentParser()
ap.add_argument("--scene", default="chant")
ap.add_argument("--t0", type=float, required=True)
ap.add_argument("--t1", type=float, required=True)
ap.add_argument("--fps", type=int, default=24)
ap.add_argument("--audio", default=str(Path(__file__).parent.parent / "audio/one_more_game.mp3"))
ap.add_argument("--out", required=True)
ap.add_argument("--still", type=float, help="render one PNG at this song time instead")
a = ap.parse_args()

clock = Clock()
if a.scene == "chant":
    from scene_chant import ChantScene as Scene
scene = Scene(clock, a.t0, a.t1)
mask = fx.crt_mask(hud.H, hud.W)

if a.still is not None:
    from PIL import Image
    f, flash = scene.frame(a.still)
    Image.fromarray(fx.finish(f, mask, flash)).save(a.out)
    raise SystemExit

Path(a.out).parent.mkdir(parents=True, exist_ok=True)
W, H = hud.W * fx.SCALE, hud.H * fx.SCALE
ff = subprocess.Popen([
    "ffmpeg", "-y", "-loglevel", "error",
    "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(a.fps), "-i", "-",
    "-ss", str(a.t0), "-t", str(a.t1 - a.t0), "-i", a.audio,
    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", a.out], stdin=subprocess.PIPE)
n = int(round((a.t1 - a.t0) * a.fps))
st = time.time()
for i in range(n):
    t = a.t0 + i / a.fps
    f, flash = scene.frame(t)
    ff.stdin.write(fx.finish(f, mask, flash).tobytes())
ff.stdin.close(); ff.wait()
print(f"{n} frames in {time.time() - st:.1f}s -> {a.out}")
