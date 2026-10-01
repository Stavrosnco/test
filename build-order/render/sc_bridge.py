"""Bridge: LAN party in the basement, then the pixels fade and one worker builds from nothing."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine, hud, sprites, units, world
from clock import ease, lerp
from font import draw_text, text_width

W, H = hud.W, hud.H
K = engine.K
BEIGE, BEIGE_D = (214, 204, 176), (166, 156, 128)
SHIRTS = [(58, 104, 214), (200, 50, 40), (70, 170, 70), (230, 190, 70), (130, 60, 170), (240, 140, 40), (60, 190, 200), (220, 220, 220)]
SCREEN_COLS = [(40, 110, 50), (200, 150, 80), (90, 80, 70), (150, 160, 80), (70, 50, 90)]


def kid_back(d, x, y, shirt, bob=0):
    """Kid seen from behind, seated; (x, y) = seat centre."""
    d.rectangle([x - 7, y - 14 - bob, x + 7, y], fill=shirt, outline=K)
    d.ellipse([x - 5, y - 24 - bob, x + 5, y - 14 - bob], fill=(104, 64, 34), outline=K)


def crt(d, x, y, w=26, h=20, col=(40, 110, 50), on=True):
    d.rectangle([x, y, x + w, y + h], fill=BEIGE, outline=K)
    d.rectangle([x + 3, y + 3, x + w - 3, y + h - 4], fill=col if on else (16, 18, 22), outline=K)
    d.rectangle([x + w // 2 - 4, y + h, x + w // 2 + 4, y + h + 3], fill=BEIGE_D, outline=K)


class Basement:
    def __init__(self):
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        self.bulb = np.exp(-((xx - 200) ** 2 + (yy - 40) ** 2 * 0.6) / (2 * 120 ** 2))[..., None]
        self.xx, self.yy = xx, yy

    def room(self, d):
        d.rectangle([0, 0, W, H], fill=(80, 74, 70))
        for y in range(0, 150, 10):
            for x in range((y // 10 % 2) * 12, W, 24):
                d.rectangle([x, y, x + 23, y + 9], outline=(70, 64, 60))
        for x in range(0, W, 64):
            d.rectangle([x, 0, x + 8, 10], fill=(96, 70, 46), outline=K)
        d.rectangle([0, 150, W, H], fill=(90, 86, 84))
        d.line([200, 0, 200, 22], fill=K)
        d.ellipse([195, 22, 205, 32], fill=(255, 236, 170), outline=K)

    def light(self, img, glows, amb=0.38, warm=1.0):
        arr = np.asarray(img).astype(np.float32)
        light = np.full((H, W, 3), amb, np.float32) * np.array([1.0, 0.9, 0.8])
        light += self.bulb * np.array([1.0, 0.82, 0.55]) * 0.9 * warm
        for gx, gy, col, s in glows:
            g = np.exp(-((self.xx - gx) ** 2 + (self.yy - gy) ** 2) / (2 * s ** 2))[..., None]
            light += g * np.array(col) / 255 * 0.8
        return Image.fromarray(np.clip(arr * light, 0, 255).astype(np.uint8))


class Bridge:
    def __init__(self, ctx, sec):
        self.ctx, self.c, self.tl, self.sec = ctx, ctx.clock, ctx.timeline, sec
        s = self.tl.sec(sec)
        self.t0, self.t1 = s["start"], s["end"]
        self.L = [l["start"] for l in s["lines"]] + [s["end"]]
        self.b = Basement()
        g = world.grass_layer(384, 256, seed=33)
        self.grass = Image.fromarray(g)

    def stairs(self, t):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        self.b.room(d)
        for i in range(9):
            x, y = 20 + i * 18, 40 + i * 13
            d.rectangle([x, y, x + 30, y + 13], fill=(130, 96, 60), outline=K)
        d.line([20, 30, 190, 150], fill=(90, 64, 40), width=2)
        glows = []
        for j in range(3):
            k = ((t - self.L[0]) * 0.32 + j * 0.3) % 1.0
            x, y = 26 + k * 150, 26 + k * 112
            bob = int(abs(math.sin(t * 8 + j)) * 2)
            d.rectangle([x - 5, y - bob, x + 5, y + 16 - bob], fill=SHIRTS[j], outline=K)
            d.ellipse([x - 4, y - 9 - bob, x + 4, y - bob], fill=(232, 178, 128), outline=K)
            crt(d, x - 2, y - 4 - bob, 18, 14, on=False)
        return self.b.light(img, glows), []

    def wires(self, t):
        img = Image.new("RGB", (W, H), (90, 86, 84))
        d = ImageDraw.Draw(img)
        rng = np.random.default_rng(4)
        cols = [(30, 30, 30), (200, 200, 200), (60, 90, 200), (220, 200, 60), (40, 40, 40)]
        k = ease((t - self.L[1]) / 1.5)
        for i in range(14):
            pts = [(float(rng.integers(0, W)), float(rng.integers(30, H)))]
            for _ in range(6):
                pts.append((pts[-1][0] + float(rng.integers(-60, 61)), pts[-1][1] + float(rng.integers(-40, 41))))
            n = max(2, int(len(pts) * k))
            d.line(pts[:n], fill=cols[i % 5], width=2, joint="curve")
        crt(d, 150, 40, 90, 70, col=(16, 18, 22), on=False)
        if t >= self.tl.word_t(self.sec, 1, "forty"):
            draw_text(img, 165, 120, "40 LBS!", (255, 255, 255), scale=2, outline=True)
        return self.b.light(img, [], amb=0.7), []

    def pizza(self, t):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        self.b.room(d)
        d.rectangle([20, 120, 364, 132], fill=(120, 90, 60), outline=K)
        d.rectangle([40, 94, 150, 120], fill=(230, 220, 200), outline=K)
        d.ellipse([46, 96, 144, 118], fill=(230, 170, 60), outline=K)
        for i in range(7):
            d.ellipse([56 + i * 12, 102 + (i % 2) * 6, 62 + i * 12, 108 + (i % 2) * 6], fill=(190, 50, 40))
        d.polygon([(40, 94), (60, 60), (170, 60), (150, 94)], fill=(210, 200, 180), outline=K)
        draw_text(img, 82, 70, "PIZZA", (190, 50, 40), shadow=None)
        d.rectangle([220, 100, 330, 120], fill=(60, 64, 72), outline=K)
        draw_text(img, 226, 90, "HUB 8 PORT", (220, 220, 220))
        for i in range(8):
            x = 228 + i * 12
            flick = i == 5 and int(t * 9) % 3 == 0
            on = (int(t * 10 + i * 7) % 4) != 0
            d.rectangle([x, 106, x + 6, 112], fill=K)
            d.point((x + 3, 104), fill=(255, 60, 40) if flick else ((80, 230, 90) if on else (30, 60, 30)))
            d.line([x + 3, 120, x + 3 + (i - 4) * 10, 216], fill=[(30, 30, 30), (200, 200, 200), (60, 90, 200)][i % 3], width=2)
        return self.b.light(img, [(275, 105, (80, 230, 90), 30)]), []

    def lan(self, t, fade=0.0, glow_one=False):
        img = Image.new("RGB", (W, H))
        d = ImageDraw.Draw(img)
        self.b.room(d)
        glows = []
        for row, (y, n) in enumerate([(104, 4), (150, 4)]):
            d.rectangle([20, y + 22, 364, y + 28], fill=(120, 90, 60), outline=K)
            for i in range(n):
                x = 40 + i * 84 + row * 20
                col = SCREEN_COLS[(i + row * 2) % 5]
                if fade > 0 and not (glow_one and row == 1 and i == 1):
                    col = tuple(int(c * (1 - fade) + 20 * fade) for c in col)
                crt(d, x, y, col=col)
                kid_back(d, x + 13, y + 52, SHIRTS[row * 4 + i], bob=int(self.c.pulse(t + i * 0.1) * 2))
                glows.append((x + 13, y + 10, col, 22))
        img = self.b.light(img, glows, warm=1 - 0.6 * fade)
        if fade > 0:
            a = np.asarray(img).astype(np.float32)
            gray = a.mean(axis=2, keepdims=True)
            a = a * (1 - fade) + gray * fade * 0.8
            blk = 1 + int(fade * 5)
            if blk > 1:
                small = Image.fromarray(a.astype(np.uint8)).resize((W // blk, H // blk), Image.BILINEAR)
                a = np.asarray(small.resize((W, H), Image.NEAREST)).astype(np.float32)
            if glow_one:
                x, y = 40 + 84 + 20, 150
                a[y:y + 22, x:x + 28] = np.asarray(img)[y:y + 22, x:x + 28]
            img = Image.fromarray(a.astype(np.uint8))
        if self.L[3] <= t < self.L[4]:
            draw_text(img, 192 - text_width("8 PLAYERS CONNECTED") // 2, 14, "8 PLAYERS CONNECTED", (80, 230, 90), outline=True)
        return img

    def rebuild(self, t):
        img = self.grass.crop((0, 20, 384, 236)).copy()
        d = ImageDraw.Draw(img)
        k = ease((t - self.L[6]) / (self.L[7] + 1.5 - self.L[6]))
        world.draw_building(d, "hall", 168, 80, ((58, 104, 214), (34, 60, 140)), progress=min(1.0, k))
        if k < 1:
            sprites.blit(img, "WORKER_A", 150, 108 - 2 * self.c.pulse(t))
        else:
            sprites.blit(img, "WORKER_A", 150, 110)
        arr = np.asarray(img).astype(np.float32)
        yy, xx = self.b.yy, self.b.xx
        r = 50 + 260 * ease((t - self.L[7]) / (self.t1 - self.L[7]))
        light = np.clip(1.15 - np.hypot(xx - 190, yy - 110) / r, 0.05, 1.2)[..., None] * np.array([1.05, 0.95, 0.8])
        img = Image.fromarray(np.clip(arr * light, 0, 255).astype(np.uint8))
        flash = max(0.0, (t - (self.t1 - 1.5)) / 1.5) * 0.9
        return img, flash

    def frame(self, t):
        L = self.L
        flash = 0.0
        if t < L[1]:
            img, _ = self.stairs(t)
        elif t < L[2]:
            img, _ = self.wires(t)
        elif t < L[3]:
            img, _ = self.pizza(t)
        elif t < L[4]:
            img = self.lan(t)
        elif t < L[5]:
            img = self.lan(t, fade=ease((t - L[4]) / (L[5] - L[4])))
        elif t < L[6]:
            img = self.lan(t, fade=1.0, glow_one=True)
            zk = ease((t - (L[6] - 1.0)) / 1.0)
            if zk > 0:
                img = img.crop((int(144 * zk), int(150 * zk), int(144 * zk + W * (1 - zk * 0.9)), int(150 * zk + H * (1 - zk * 0.9)))).resize((W, H), Image.NEAREST)
        else:
            img, flash = self.rebuild(t)
        engine.sub_line(img, self.tl, t, sec=self.sec)
        return img, flash
