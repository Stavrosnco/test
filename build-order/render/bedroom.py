"""The kid's bedroom, 1990s. Used by the intro, verse 1 and the choruses."""
import math
import numpy as np
from PIL import Image, ImageDraw
import hud
from font import draw_text, text_width

K = (22, 18, 20)
W, H = hud.W, hud.H
SCREEN = (198, 86, 262, 128)  # inner CRT screen box
SCR_W, SCR_H = SCREEN[2] - SCREEN[0], SCREEN[3] - SCREEN[1]
BEIGE, BEIGE_D, BEIGE_L = (214, 204, 176), (166, 156, 128), (236, 228, 204)


def sky(k, t):
    """Window sky, k: 0 deep night .. 1 full morning."""
    stops = [(0.0, (14, 16, 44), (30, 30, 70)), (0.45, (40, 30, 80), (200, 90, 90)),
             (0.7, (90, 120, 200), (250, 170, 100)), (1.0, (110, 170, 240), (200, 230, 250))]
    for (k0, t0, b0), (k1, t1, b1) in zip(stops, stops[1:]):
        if k <= k1:
            u = (k - k0) / (k1 - k0)
            top = tuple(int(a + (b - a) * u) for a, b in zip(t0, t1))
            bot = tuple(int(a + (b - a) * u) for a, b in zip(b0, b1))
            return top, bot
    return stops[-1][1], stops[-1][2]


class Bedroom:
    def __init__(self):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        sx, sy = (SCREEN[0] + SCREEN[2]) / 2, (SCREEN[1] + SCREEN[3]) / 2
        self.glow = np.exp(-((xx - sx) ** 2 + (yy - sy) ** 2 * 1.6) / (2 * 70 ** 2))[..., None]
        self.win = np.exp(-((xx - 70) ** 2 + (yy - 120) ** 2) / (2 * 110 ** 2))[..., None]
        self.door_l = np.exp(-((xx - 362) ** 2 + (yy - 120) ** 2) / (2 * 60 ** 2))[..., None]

    def draw(self, t, dawn=0.0, clock_h=2.0, door=0.0, mom=None, screen=None, kid_bob=0.0,
             led=True, labels=(), cheer=0.0):
        img = Image.new("RGB", (W, H), (70, 80, 120))
        d = ImageDraw.Draw(img)
        # wall + wallpaper
        d.rectangle([0, 0, W, 172], fill=(84, 96, 140))
        for x in range(0, W, 12):
            d.line([x, 0, x, 172], fill=(78, 90, 132))
        d.rectangle([0, 166, W, 172], fill=(60, 54, 70))
        # floor
        d.rectangle([0, 172, W, H], fill=(120, 80, 50))
        for y in range(176, H, 7):
            d.line([0, y, W, y], fill=(100, 66, 40))
        for i, y in enumerate(range(172, H, 7)):
            for x in range((i * 23) % 40, W, 40):
                d.line([x, y, x, y + 6], fill=(96, 62, 38))
        # window: sky, sun/moon and hills drawn in their own layer, clipped to the glass
        top, bot = sky(dawn, t)
        wx0, wy0, wx1, wy1 = 24, 28, 112, 104
        win = Image.new("RGB", (wx1 - wx0, wy1 - wy0))
        wd = ImageDraw.Draw(win)
        for y in range(wy1 - wy0):
            u = y / (wy1 - wy0)
            wd.line([0, y, wx1 - wx0, y], fill=tuple(int(a + (b - a) * u) for a, b in zip(top, bot)))
        if dawn < 0.5:
            rng = np.random.default_rng(3)
            for _ in range(18):
                x, y = int(rng.integers(2, 86)), int(rng.integers(2, 52))
                if (int(t * 3) + x) % 7:
                    wd.point((x, y), fill=(230, 230, 255))
            wd.ellipse([60, 8, 72, 20], fill=(240, 236, 200))
            wd.ellipse([64, 6, 76, 18], fill=top)
        else:
            sy_ = int(82 - 70 * (dawn - 0.5) * 2)
            wd.ellipse([26, sy_, 46, sy_ + 20], fill=(255, 230, 140))
        wd.polygon([(0, 76), (16, 62), (36, 70), (56, 58), (88, 72), (88, 76)], fill=(30, 30, 50))
        img.paste(win, (wx0, wy0))
        d.rectangle([22, 26, 114, 106], outline=(230, 224, 210), width=2)
        d.line([68, 26, 68, 106], fill=(230, 224, 210), width=2)
        d.line([22, 66, 114, 66], fill=(230, 224, 210), width=2)
        d.rectangle([18, 104, 118, 108], fill=(200, 194, 180), outline=K)
        # poster (original: a dragon over a castle)
        d.rectangle([130, 24, 172, 76], fill=(150, 40, 40), outline=K)
        d.polygon([(136, 70), (142, 56), (148, 70)], fill=(40, 20, 20))
        d.rectangle([150, 58, 166, 70], fill=(40, 20, 20))
        d.polygon([(140, 44), (152, 36), (166, 40), (156, 48), (162, 54), (148, 50)], fill=(30, 16, 16))
        draw_text(img, 135, 27, "WAR!", (246, 206, 62))
        # clock
        d.ellipse([118, 92, 138, 112], fill=(236, 232, 220), outline=K)
        cx, cy = 128, 102
        a_h = math.radians(clock_h % 12 * 30 - 90)
        a_m = math.radians((clock_h * 60) % 60 * 6 - 90)
        d.line([cx, cy, cx + 5 * math.cos(a_h), cy + 5 * math.sin(a_h)], fill=K, width=2)
        d.line([cx, cy, cx + 8 * math.cos(a_m), cy + 8 * math.sin(a_m)], fill=K)
        # door
        d.rectangle([340, 56, 382, 172], fill=(140, 100, 64), outline=K)
        if door > 0:
            gap = int(36 * door)
            d.rectangle([342, 58, 342 + gap, 170], fill=(250, 220, 150))
            if mom and door > 0.6:
                mx = 342 + gap // 2
                d.ellipse([mx - 8, 76, mx + 8, 94], fill=(60, 40, 40))
                d.ellipse([mx - 4, 70, mx + 4, 78], fill=(60, 40, 40))
                d.polygon([(mx - 12, 168), (mx - 9, 96), (mx + 9, 96), (mx + 12, 168)], fill=(70, 50, 60))
                d.line([mx - 9, 104, mx - 22, 96], fill=(70, 50, 60), width=3)
            d.rectangle([342 + gap, 58, 346 + gap, 170], fill=(120, 84, 50), outline=K)
        else:
            d.rectangle([346, 62, 376, 108], outline=(120, 84, 50))
            d.rectangle([346, 114, 376, 166], outline=(120, 84, 50))
            d.ellipse([372, 112, 376, 116], fill=(220, 190, 80))
        # desk
        d.rectangle([140, 140, 336, 148], fill=(150, 110, 70), outline=K)
        d.rectangle([146, 148, 152, 178], fill=(120, 84, 50), outline=K)
        d.rectangle([324, 148, 330, 178], fill=(120, 84, 50), outline=K)
        # tower + modem
        d.rectangle([286, 72, 322, 140], fill=BEIGE, outline=K)
        d.rectangle([290, 80, 318, 86], fill=BEIGE_D, outline=K)
        d.rectangle([290, 92, 318, 97], fill=BEIGE_D, outline=K)
        d.line([294, 94, 314, 94], fill=K)
        d.point((292, 130), fill=(80, 230, 90)); d.point((296, 130), fill=(250, 180, 40) if int(t * 7) % 2 else (90, 60, 20))
        d.rectangle([298, 116, 312, 121], fill=(40, 60, 140))
        draw_text(img, 0, 0, "", K)
        d.rectangle([288, 62, 320, 72], fill=(60, 60, 64), outline=K)
        for i in range(5):
            on = led and (int(t * 8 + i * 3) % 3 != 0)
            d.point((292 + i * 5, 67), fill=(250, 60, 40) if on else (70, 30, 30))
        # shoebox of floppies
        d.rectangle([152, 124, 186, 140], fill=(200, 120, 60), outline=K)
        for i, col in enumerate([(40, 40, 44), (60, 80, 160), (160, 40, 40), (40, 40, 44), (220, 200, 60)]):
            d.rectangle([155 + i * 6, 116 - (i % 2) * 2, 160 + i * 6, 126], fill=col, outline=K)
            d.rectangle([156 + i * 6, 118 - (i % 2) * 2, 159 + i * 6, 120 - (i % 2) * 2], fill=(200, 200, 210))
        # monitor
        d.rectangle([188, 74, 272, 136], fill=BEIGE, outline=K)
        d.rectangle([194, 82, 266, 132], fill=BEIGE_D, outline=K)
        d.rectangle([222, 136, 238, 142], fill=BEIGE_D, outline=K)
        d.point((262, 134), fill=(80, 230, 90))
        if screen is not None:
            img.paste(screen.resize((SCR_W, SCR_H), Image.NEAREST), (SCREEN[0], SCREEN[1]))
        else:
            d.rectangle(SCREEN, fill=(10, 14, 20))
        # keyboard + mouse
        d.polygon([(200, 146), (204, 140), (256, 140), (260, 146)], fill=BEIGE, outline=K)
        for x in range(206, 254, 4):
            d.line([x, 142, x + 1, 142], fill=BEIGE_D)
        d.ellipse([266, 140, 274, 147], fill=(200, 196, 180), outline=K)
        d.line([270, 140, 278, 128], fill=(60, 60, 60))
        # kid, from behind
        bob = int(round(kid_bob * 2))
        d.rectangle([212, 172, 252, 180], fill=(40, 40, 50), outline=K)
        d.rectangle([228, 180, 236, 200], fill=(50, 50, 60), outline=K)
        d.line([214, 204, 250, 204], fill=(30, 30, 36), width=3)
        d.rectangle([214, 128 - bob, 250, 174], fill=(40, 40, 50), outline=K)
        if cheer > 0:
            up = int(cheer * 18)
            d.line([214, 148, 202, 130 - up], fill=(58, 104, 214), width=5)
            d.line([250, 148, 262, 130 - up], fill=(58, 104, 214), width=5)
        d.ellipse([212, 136 - bob, 252, 176 - bob], fill=(58, 104, 214), outline=K)
        d.ellipse([222, 116 - bob, 242, 138 - bob], fill=(104, 64, 34), outline=K)
        d.arc([222, 116 - bob, 242, 138 - bob], 200, 300, fill=(140, 90, 50))
        for lx, ly, txt in labels:
            tw = text_width(txt)
            d.rectangle([lx - 2, ly - 2, lx + tw + 1, ly + 8], fill=(250, 246, 200), outline=K)
            draw_text(img, lx, ly, txt, (30, 24, 20), shadow=None)
        # lighting
        arr = np.asarray(img).astype(np.float32)
        amb = 0.32 + 0.6 * dawn
        tint = np.array([0.75 + 0.25 * dawn, 0.8 + 0.2 * dawn, 1.0]) * amb
        light = tint + self.glow * np.array([0.55, 0.75, 1.0]) * (1.0 - 0.5 * dawn)
        light = light + self.win * np.array([1.0, 0.7, 0.45]) * max(0.0, dawn - 0.3) * 0.7
        if door > 0:
            light = light + self.door_l * np.array([1.0, 0.85, 0.55]) * door * 0.8
        out = arr * light
        if screen is not None:
            x0, y0, x1, y1 = SCREEN
            out[y0:y1, x0:x1] = arr[y0:y1, x0:x1] * 1.15
        img = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
        if mom and door > 0.6:
            d = ImageDraw.Draw(img)
            tw = text_width(mom)
            bx = 334 - tw
            d.rectangle([bx - 4, 40, 336, 54], fill=(250, 250, 250), outline=K)
            d.polygon([(330, 54), (342, 64), (324, 54)], fill=(250, 250, 250), outline=K)
            draw_text(img, bx, 44, mom, (200, 30, 30), shadow=None)
        return img


def zoom(img, cx, cy, z):
    """Crop around (cx, cy) by zoom factor z and scale back to full frame (nearest)."""
    w, h = W / z, H / z
    x0 = min(max(cx - w / 2, 0), W - w)
    y0 = min(max(cy - h / 2, 0), H - h)
    return img.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.NEAREST)


def push(room, content, z):
    """Zoom into the CRT; `content` (full-res frame) is pasted into the screen so the cut is seamless."""
    cx, cy = (SCREEN[0] + SCREEN[2]) / 2, (SCREEN[1] + SCREEN[3]) / 2
    w, h = W / z, H / z
    x0 = min(max(cx - w / 2, 0), W - w)
    y0 = min(max(cy - h / 2, 0), H - h)
    out = room.crop((int(x0), int(y0), int(x0 + w), int(y0 + h))).resize((W, H), Image.NEAREST)
    sx = lambda x: (x - x0) * W / w
    sy = lambda y: (y - y0) * H / h
    rx0, ry0, rx1, ry1 = int(sx(SCREEN[0])), int(sy(SCREEN[1])), int(sx(SCREEN[2])), int(sy(SCREEN[3]))
    if rx1 - rx0 > 2 and ry1 - ry0 > 2:
        c = content.resize((rx1 - rx0, ry1 - ry0), Image.NEAREST)
        out.paste(c, (rx0, ry0))
    return out
