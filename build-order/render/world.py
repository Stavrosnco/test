"""Terrain, trees, buildings for the forest chapter. Procedural pixel art."""
import numpy as np
from PIL import Image, ImageDraw

TILE = 16
K = (22, 18, 20)

def _hash(x, y, seed=0):
    return ((x * 73856093) ^ (y * 19349663) ^ (seed * 83492791)) & 0xFFFF

def grass_layer(w, h, seed=1):
    rng = np.random.default_rng(seed)
    base = np.array([[56, 108, 46], [66, 122, 52], [48, 96, 42], [74, 132, 58]], np.uint8)
    # 2x2 pixel clumps of grass shades, plus large soft patches
    clump = rng.integers(0, 3, (h // 2 + 1, w // 2 + 1))
    clump = np.repeat(np.repeat(clump, 2, 0), 2, 1)[:h, :w]
    patch = rng.random((h // 24 + 2, w // 24 + 2))
    yy, xx = np.mgrid[0:h, 0:w]
    p = patch[yy // 24, xx // 24]
    idx = np.where(p > 0.72, 3, clump)
    img = base[idx]
    # flowers and pebbles
    for _ in range(w * h // 260):
        x, y = rng.integers(0, w), rng.integers(0, h)
        img[y, x] = rng.choice([(236, 220, 90), (230, 120, 150), (220, 220, 230), (40, 80, 36)])
    return img

def dirt_path(img, pts, width=7, seed=2):
    rng = np.random.default_rng(seed)
    h, w, _ = img.shape
    yy, xx = np.mgrid[0:h, 0:w]
    for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
        dx, dy = x1 - x0, y1 - y0
        L = max(1, (dx * dx + dy * dy))
        t = np.clip(((xx - x0) * dx + (yy - y0) * dy) / L, 0, 1)
        d = np.hypot(xx - (x0 + t * dx), yy - (y0 + t * dy))
        noise = rng.random((h, w)) * 2.2
        m = d + noise < width
        img[m] = np.where(rng.random((m.sum(), 1)) > 0.3, (122, 94, 58), (104, 80, 48))
    return img

def water(img, x0, x1, seed=3):
    h = img.shape[0]
    for y in range(h):
        wob = int(3 * np.sin(y / 9.0) + 2 * np.sin(y / 3.7))
        a, b = x0 + wob, x1 + wob
        img[y, a - 2:a] = (150, 130, 84)
        img[y, b:b + 2] = (150, 130, 84)
        img[y, a:b] = (34, 74, 148)
        img[y, a + 3:b - 3:7] = (70, 118, 196)
    return img

def draw_tree(d, x, y, sway=0, seed=0):
    """Tree with trunk base at (x, y)."""
    r = 6 + _hash(x, y, seed) % 3
    d.rectangle([x - 1, y - 5, x + 1, y], fill=(84, 56, 32), outline=None)
    cx = x + sway
    d.ellipse([cx - r - 1, y - 5 - 2 * r - 1, cx + r + 1, y - 5 + 1], fill=K)
    d.ellipse([cx - r, y - 5 - 2 * r, cx + r, y - 5], fill=(24, 66, 34))
    d.ellipse([cx - r + 1, y - 5 - 2 * r + 1, cx + r - 2, y - 7], fill=(38, 94, 42))
    d.ellipse([cx - r + 3, y - 5 - 2 * r + 2, cx + 1, y - 5 - r], fill=(62, 128, 54))

def draw_goldmine(d, x, y, glint=0):
    d.polygon([(x, y + 40), (x + 6, y + 12), (x + 18, y), (x + 34, y + 4), (x + 46, y + 22),
               (x + 48, y + 40)], fill=(96, 92, 100), outline=K)
    d.polygon([(x + 8, y + 36), (x + 12, y + 16), (x + 22, y + 8), (x + 32, y + 12),
               (x + 40, y + 36)], fill=(128, 124, 134))
    d.rectangle([x + 18, y + 24, x + 30, y + 40], fill=(28, 22, 22), outline=K)
    d.line([x + 17, y + 23, x + 31, y + 23], fill=(126, 86, 46), width=2)
    for i, (gx, gy) in enumerate([(12, 20), (36, 18), (26, 12), (40, 30), (10, 32)]):
        col = (255, 250, 200) if (i + glint) % 5 == 0 else (246, 206, 62)
        d.rectangle([x + gx, y + gy, x + gx + 1, y + gy + 1], fill=col)

def _roof(d, x, y, w, h, team):
    tc, td = team
    d.polygon([(x - 2, y + h), (x + w // 2, y), (x + w + 2, y + h)], fill=tc, outline=K)
    for i in range(3, h, 3):
        d.line([x + w // 2 - i * w // (2 * h), y + i, x + w // 2 + i * w // (2 * h), y + i], fill=td)

def draw_building(d, kind, x, y, team, progress=1.0):
    """(x, y) is the top-left of the footprint. progress < 1 draws scaffolding."""
    w, h = {"hall": (46, 42), "farm": (28, 24), "barracks": (40, 34), "tower": (18, 40),
            "mill": (34, 28)}[kind]
    if progress < 1.0:
        top = y + h - int(h * progress)
        d.rectangle([x, y + h - 4, x + w, y + h], fill=(104, 80, 48))
        for px in range(x, x + w + 1, 6):
            d.line([px, top, px, y + h], fill=(150, 110, 60))
        for py in range(top, y + h, 5):
            d.line([x, py, x + w, py], fill=(126, 86, 46))
        return
    wall, wall_d = (150, 108, 64), (112, 76, 42)
    stone = (128, 126, 136)
    if kind == "tower":
        d.rectangle([x + 2, y + 10, x + w - 2, y + h], fill=stone, outline=K)
        for by in range(y + 14, y + h, 5):
            d.line([x + 3, by, x + w - 3, by], fill=(100, 98, 108))
        d.rectangle([x, y + 6, x + w, y + 12], fill=(150, 148, 158), outline=K)
        for bx in range(x + 1, x + w, 4):
            d.rectangle([bx, y + 2, bx + 2, y + 6], fill=(150, 148, 158), outline=K)
        d.rectangle([x + 7, y + 18, x + 10, y + 23], fill=K)
        d.rectangle([x + 7, y - 6, x + 8, y + 2], fill=K)
        d.polygon([(x + 9, y - 6), (x + 15, y - 4), (x + 9, y - 2)], fill=team[0])
        return
    roof_h = h // 2
    d.rectangle([x, y + roof_h - 2, x + w, y + h], fill=wall, outline=K)
    for bx in range(x + 4, x + w, 6):
        d.line([bx, y + roof_h, bx, y + h - 1], fill=wall_d)
    d.rectangle([x, y + h - 4, x + w, y + h], fill=stone, outline=K)
    _roof(d, x, y, w, roof_h, team)
    dw = 8 if kind in ("hall", "barracks") else 6
    d.rectangle([x + w // 2 - dw // 2, y + h - 12, x + w // 2 + dw // 2, y + h], fill=(60, 40, 24), outline=K)
    for wx in (x + 5, x + w - 10):
        d.rectangle([wx, y + roof_h + 4, wx + 4, y + roof_h + 8], fill=(240, 210, 120), outline=K)
    if kind == "hall":
        d.rectangle([x + w // 2, y - 10, x + w // 2 + 1, y + 2], fill=K)
        d.polygon([(x + w // 2 + 2, y - 10), (x + w // 2 + 10, y - 7), (x + w // 2 + 2, y - 4)], fill=team[0])
    if kind == "barracks":
        d.line([x + 6, y + h - 10, x + 12, y + h - 4], fill=(178, 180, 190), width=1)
        d.line([x + 12, y + h - 10, x + 6, y + h - 4], fill=(178, 180, 190), width=1)
    if kind == "farm":
        for fy in range(y + h + 2, y + h + 12, 3):
            d.line([x - 4, fy, x + w + 4, fy], fill=(176, 150, 60))
    if kind == "mill":
        d.ellipse([x + w - 12, y + roof_h - 2, x + w - 2, y + roof_h + 8], fill=(170, 130, 80), outline=K)
