"""Intro (spoken): desert planet -> blueprint -> four verbs -> bedroom -> push into the CRT."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine, hud, bedroom, units
from clock import ease, lerp
from font import draw_text, text_width

W, H = hud.W, hud.H
WHITE = (226, 238, 255)


class Planet:
    def __init__(self, r=62, cx=192, cy=100):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        nx, ny = (xx - cx) / r, (yy - cy) / r
        self.inside = nx ** 2 + ny ** 2 < 1
        nz = np.sqrt(np.clip(1 - nx ** 2 - ny ** 2, 0, 1))
        self.lon0 = np.arctan2(nx, nz)
        self.lat = np.arcsin(np.clip(ny, -1, 1))
        self.shade = np.clip(-0.55 * nx - 0.45 * ny + 0.7 * nz, 0, 1)
        self.thr = np.tile(engine.BAYER, (H // 4, W // 4))
        self.pal = np.array([[236, 190, 120], [214, 160, 92], [186, 128, 70], [150, 96, 52], [96, 58, 36], [40, 24, 20]], np.float32)

    def draw(self, arr, t, spice=0.0):
        lon = self.lon0 + t * 0.12
        pat = np.sin(lon * 5 + np.sin(self.lat * 7) * 1.5) * 0.5 + 0.5 * np.sin(self.lat * 11 + lon * 3)
        band = np.clip(((pat + 1) / 2 * 3).astype(int), 0, 3)
        dark = (self.shade + (self.thr - 0.5) * 0.25)
        lvl = np.where(dark < 0.18, 5, np.where(dark < 0.38, np.minimum(band + 1, 4), band))
        arr[self.inside] = self.pal[lvl][self.inside]
        if spice > 0:
            m = self.inside & (np.sin(lon * 23 + self.lat * 17) > 0.97 - 0.05 * spice) & (self.shade > 0.3)
            arr[m] = (255, 120, 30)


BP_SHAPES = [("rect", 40, 120, 100, 160, "HQ"), ("rect", 120, 70, 150, 92, ""), ("rect", 160, 70, 190, 92, ""),
             ("rect", 120, 120, 170, 156, "BARRACKS"), ("poly", 30, 40, 70, 80, "MINE"), ("path", 100, 140, 300, 140, ""),
             ("rect", 200, 110, 216, 150, ""), ("arrow", 230, 140, 340, 100, "ATTACK"), ("x", 350, 90, 0, 0, "")]


class Intro:
    def __init__(self, ctx, sec=0):
        self.c, self.tl = ctx.clock, ctx.timeline
        s = self.tl.sec(sec)
        self.L = [l["start"] for l in s["lines"]]
        self.sec = sec
        self.cut = self.tl.sec(sec + 1)["start"] - 2.0
        self.planet = Planet()
        self.room = bedroom.Bedroom()
        self.verbs = [(self.tl.word_t(sec, 2, w), w.upper()) for w in ("Harvest", "Build", "Expand", "Attack")]
        self.realtime = self.tl.word_t(sec, 2, "real")
        self.next_scene = None

    def blueprint(self, t, k):
        img = Image.new("RGB", (W, H), (24, 60, 140))
        d = ImageDraw.Draw(img)
        for x in range(0, W, 8):
            d.line([x, 0, x, H], fill=(70, 120, 210) if x % 32 == 0 else (36, 76, 160))
        for y in range(0, H, 8):
            d.line([0, y, W, y], fill=(70, 120, 210) if y % 32 == 0 else (36, 76, 160))
        n = len(BP_SHAPES)
        for i, (kind, a, b, c, e, label) in enumerate(BP_SHAPES):
            p = np.clip(k * n - i, 0, 1)
            if p <= 0:
                continue
            if kind == "rect":
                pts = [(a, b), (c, b), (c, e), (a, e), (a, b)]
                L = int(len(pts) * p * 10)
                seg = []
                for j in range(len(pts) - 1):
                    for s in range(10):
                        if j * 10 + s <= L:
                            u = s / 10
                            seg.append((pts[j][0] + (pts[j + 1][0] - pts[j][0]) * u, pts[j][1] + (pts[j + 1][1] - pts[j][1]) * u))
                if len(seg) > 1:
                    d.line(seg, fill=WHITE)
            elif kind == "poly":
                d.arc([a, b, c, e], 180, 180 + int(180 * p), fill=WHITE)
            elif kind == "path":
                for x in range(a, int(a + (c - a) * p), 6):
                    d.line([x, b, x + 3, b], fill=WHITE)
            elif kind == "arrow":
                ex, ey = a + (c - a) * p, b + (e - b) * p
                d.line([a, b, ex, ey], fill=(255, 120, 120), width=2)
                if p >= 1:
                    d.polygon([(c, e), (c - 10, e - 1), (c - 5, e + 8)], fill=(255, 120, 120))
            elif kind == "x":
                d.line([a - 6, b - 6, a + 6, b + 6], fill=(255, 120, 120), width=2)
                d.line([a - 6, b + 6, a + 6, b - 6], fill=(255, 120, 120), width=2)
            if label and p >= 1:
                draw_text(img, a + 2, b + 3 if kind != "arrow" else b - 12, label, WHITE, shadow=None)
        draw_text(img, 8, 6, "BASE PLAN  REV.1", WHITE, shadow=None)
        if k > 0.15:
            d.rectangle([300, 176, 376, 206], outline=(255, 120, 120), width=2)
            draw_text(img, 306, 181, "LAS VEGAS", (255, 120, 120), shadow=None)
            draw_text(img, 318, 193, "1992", (255, 120, 120), shadow=None)
        return img

    def verbs_panel(self, t):
        img = Image.new("RGB", (W, H), (12, 10, 16))
        d = ImageDraw.Draw(img)
        icons = [lambda x, y: units.harvester(d, x, y, team="blue", load=1, glow=(246, 206, 62)),
                 lambda x, y: (d.rectangle([x - 14, y - 22, x + 14, y], fill=(150, 108, 64), outline=engine.K),
                               d.polygon([(x - 18, y - 22), (x, y - 36), (x + 18, y - 22)], fill=(58, 104, 214), outline=engine.K)),
                 lambda x, y: (d.line([x - 6, y, x - 6, y - 34], fill=engine.K, width=2),
                               d.polygon([(x - 4, y - 34), (x + 16, y - 28), (x - 4, y - 22)], fill=(58, 104, 214), outline=engine.K)),
                 lambda x, y: (d.line([x - 14, y, x + 14, y - 34], fill=(200, 202, 212), width=3),
                               d.line([x - 12, y - 14, x - 2, y - 4], fill=(126, 86, 46), width=3))]
        for i, (st, word) in enumerate(self.verbs):
            if t < st:
                continue
            cx = 48 + i * 96
            age = t - st
            col = (255, 255, 255) if age < 0.15 else (246, 206, 62)
            d.rectangle([cx - 44, 30, cx + 44, 170], fill=(30, 26, 40), outline=col)
            icons[i](cx, 104)
            draw_text(img, cx - text_width(word, 2) // 2, 130, word, col, scale=2, outline=True)
        if t >= self.realtime:
            a = np.asarray(img).astype(np.float32) * 0.35
            img = Image.fromarray(a.astype(np.uint8))
            d = ImageDraw.Draw(img)
            k = min(1.0, (t - self.realtime) / 1.2)
            d.ellipse([132, 40, 252, 160], fill=(16, 30, 18), outline=(80, 230, 90), width=2)
            d.pieslice([136, 44, 248, 156], -90, -90 + int(360 * k), fill=(30, 80, 36))
            d.line([192, 100, 192 + 50 * math.cos(math.radians(-90 + 360 * k)), 100 + 50 * math.sin(math.radians(-90 + 360 * k))],
                   fill=(80, 230, 90), width=2)
            engine.big_text(img, "REAL TIME", t - self.realtime, scale=4, y=100, col=(80, 230, 90))
        return img

    def frame(self, t):
        L = self.L
        if t < L[1]:
            arr = np.zeros((H, W, 3), np.uint8)
            img = Image.fromarray(arr)
            engine.stars(img, t)
            arr = np.asarray(img).copy()
            self.planet.draw(arr, t, spice=ease((t - self.tl.word_t(self.sec, 0, "spice")) / 1.0))
            img = Image.fromarray(arr)
            st = self.tl.word_t(self.sec, 0, "Nineteen")
            if t >= st:
                engine.big_text(img, "1992", t - st, scale=4, y=24)
            if t < 0.5:  # CRT power-on
                k = t / 0.5
                a = np.asarray(img).copy()
                hh = int(H * k * k / 2)
                mask = np.zeros((H, W), bool)
                mask[H // 2 - hh:H // 2 + hh + 1] = True
                a[~mask] = 0
                if hh < 3:
                    a[H // 2 - 1:H // 2 + 2, int(W * (0.5 - k)):int(W * (0.5 + k))] = 255
                img = Image.fromarray(a)
        elif t < L[2]:
            img = self.blueprint(t, (t - L[1]) / (L[2] - L[1] - 0.4))
        elif t < L[3]:
            img = self.verbs_panel(t)
        else:
            scr = self.blueprint(t, 1.0)
            img = self.room.draw(t, dawn=0.0, clock_h=2.5, screen=scr, kid_bob=self.c.pulse(t))
            zk = ease((t - (self.cut - 1.4)) / 1.4)
            if zk > 0 and self.next_scene is not None:
                content, _ = self.next_scene.frame(self.cut)
                img = bedroom.push(img, content, 1 + zk * 5.0)
                return img, 0.0
        engine.sub_line(img, self.tl, t, sec=self.sec)
        return img, 0.0
