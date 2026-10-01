"""Upscale + CRT post-process."""
import numpy as np

SCALE = 5

def crt_mask(h, w):
    rows = np.ones(h * SCALE, np.float32)
    rows[SCALE - 1::SCALE] = 0.72
    yy, xx = np.mgrid[0:h * SCALE, 0:w * SCALE].astype(np.float32)
    ny, nx = yy / (h * SCALE) - 0.5, xx / (w * SCALE) - 0.5
    vign = 1.0 - 0.55 * (nx * nx + ny * ny) ** 1.2 * 2.2
    return (rows[:, None] * np.clip(vign, 0, 1))[..., None]

def finish(frame_small, mask, flash=0.0):
    a = np.asarray(frame_small, dtype=np.float32)
    if flash > 0:
        a = a + (255 - a) * flash
    big = np.repeat(np.repeat(a, SCALE, 0), SCALE, 1) * mask
    return np.clip(big, 0, 255).astype(np.uint8)
