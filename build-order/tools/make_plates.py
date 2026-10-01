"""Turn raw AI backdrops into low-res, palette-reduced plates for the renderer.

fmv_*:   5:3 crop -> 246x148 (10% overscan for a slow push-in), 40-colour palette
stadium: 2.43:1 crop around the stage -> 422x174 (10% overscan for a drift), 64 colours,
         plus the blue screen's bounding box (for pasting game footage) in stadium.json
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).parent.parent
RAW, OUT = ROOT / "art/raw", ROOT / "art/plates"
OUT.mkdir(parents=True, exist_ok=True)


def crop_aspect(im, aspect, cy=0.5):
    w, h = im.size
    if w / h > aspect:
        nw = int(h * aspect)
        x0 = (w - nw) // 2
        return im.crop((x0, 0, x0 + nw, h))
    nh = int(w / aspect)
    y0 = int(np.clip((h - nh) * cy, 0, h - nh))
    return im.crop((0, y0, w, y0 + nh))


def reduce(im, size, colors, dither=True):
    small = im.resize(size, Image.LANCZOS)
    d = Image.Dither.FLOYDSTEINBERG if dither else Image.Dither.NONE
    return small.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=d).convert("RGB")


for name in ("fmv_general", "fmv_bald"):
    im = Image.open(RAW / f"gpt_{name}.webp").convert("RGB")
    reduce(crop_aspect(im, 5 / 3), (246, 148), 64, dither=False).save(OUT / f"{name}.png")

im = Image.open(RAW / "gpt_stadium.webp").convert("RGB")
# find the blue screen at full res first so the crop can be centred on the stage
a = np.asarray(im).astype(int)
blue = (a[..., 2] > 180) & (a[..., 0] < 70) & (a[..., 1] < 110)
ys, xs = np.nonzero(blue)
sy0, sy1 = np.percentile(ys, [1, 99])
cropped = crop_aspect(im, 384 / 158, cy=max(0.0, (sy0 - 30) / (im.size[1] - im.size[0] / (384 / 158))))
plate = reduce(cropped, (422, 174), 64)
p = np.asarray(plate).astype(int)
m = (p[..., 2] > 170) & (p[..., 0] < 80) & (p[..., 1] < 120)
vals, counts = np.unique(p[m].reshape(-1, 3), axis=0, return_counts=True)
mode = vals[counts.argmax()]
m = np.abs(p - mode).sum(axis=2) < 30
cols, rows = m.sum(axis=0), m.sum(axis=1)
xs = np.nonzero(cols > 0.6 * cols.max())[0]
ys = np.nonzero(rows > 0.6 * rows.max())[0]
box = [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())]
plate.save(OUT / "stadium.png")
(OUT / "stadium.json").write_text(json.dumps({"screen": box}))
print("stadium screen box", box)
