"""Verse 4: ancient empires: ages, villagers, conversion, elephants, cheat codes, trebuchets."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine, hud, sprites, units, world
from clock import ease, lerp
from font import draw_text, text_width

TC = (130, 150)
CIV_COLS = [(58, 104, 214), (200, 50, 40), (70, 170, 70), (230, 190, 70), (130, 60, 170), (240, 140, 40),
            (60, 190, 200), (220, 220, 220), (120, 80, 40), (230, 110, 170), (40, 40, 40), (150, 200, 90)]


class Verse4(engine.MapScene):
    MAP_W, MAP_H = 1024, 256
    theme, title, speaker = "aoe", "AGES 1997", "Empress"
    use_fog = False

    def __init__(self, ctx, sec):
        super().__init__(ctx, sec)
        tl = self.tl
        w = lambda i, k: tl.word_t(sec, i, k)
        self.L = [l["start"] for l in tl.sec(sec)["lines"]] + [tl.sec(sec)["end"]]
        self.t_97, self.t_spin = w(0, "Ninety"), w(0, "spin")
        self.ages = [w(1, "Stone"), w(1, "Tool"), w(1, "Bronze"), w(1, "Iron")]
        self.t_fish = w(2, "fishing")
        self.t_twelve, self.t_build = w(3, "twelve"), w(3, "build")
        self.t_wolo, self.t_mine = w(4, "Wololo"), w(4, "mine")
        self.t_conv, self.t_river, self.t_line = w(5, "converted"), w(5, "river"), w(5, "line")
        self.t_typed, self.t_laser = w(6, "typed"), w(6, "laser")
        self.t_kings, self.t_treb, self.t_over = w(7, "Age"), w(7, "trebuchets"), w(7, "over")
        self.enemy = [(520 + (i % 3) * 16, 140 + (i // 3) * 18, self.t_wolo + 0.3 + i * 0.22) for i in range(6)]

    def build_ground(self):
        rng = np.random.default_rng(17)
        h, w = self.MAP_H, self.MAP_W
        base = np.array([[150, 160, 78], [138, 150, 70], [164, 170, 90], [196, 180, 120]], np.uint8)
        idx = rng.integers(0, 3, (h // 2 + 1, w // 2 + 1))
        idx = np.repeat(np.repeat(idx, 2, 0), 2, 1)[:h, :w]
        yy, xx = np.mgrid[0:h, 0:w]
        coarse = Image.fromarray((rng.random((h // 12 + 2, w // 12 + 2)) * 255).astype(np.uint8))
        patch = np.asarray(coarse.resize((w + 24, h + 24), Image.BICUBIC))[:h, :w] / 255.0
        g = base[np.where(patch > 0.72, 3, idx)]
        for x in range(w):  # coast along the bottom-left
            edge = int(222 + 6 * math.sin(x / 19) + 3 * math.sin(x / 7)) if x < 330 else 999
            g[edge:, x] = (40, 100, 170)
            g[edge:edge + 2, x] = (220, 206, 150)
        for y in range(h):  # river
            c = int(612 + 8 * math.sin(y / 15))
            g[y, c - 12:c + 12] = (52, 112, 180)
            g[y, c - 14:c - 12] = g[y, c + 12:c + 14] = (200, 186, 130)
            g[y, c - 8:c + 8:6] = (90, 150, 210)
        g = world.dirt_path(g, [(160, 170), (400, 170), (600, 170), (760, 170), (880, 170)], width=5, seed=9)
        gi = Image.fromarray(g)
        gd = ImageDraw.Draw(gi)
        for _ in range(90):
            x, y = int(rng.integers(0, w)), int(rng.integers(20, 215))
            if 590 < x < 640 or (60 < x < 200 and 100 < y < 190) or (260 < x < 340 and 60 < y < 130) or x > 840:
                continue
            if rng.random() < 0.6:
                gd.ellipse([x - 5, y - 9, x + 5, y - 1], fill=(96, 110, 56), outline=engine.K)
                gd.ellipse([x - 3, y - 8, x + 1, y - 4], fill=(124, 140, 70))
                gd.line([x, y - 1, x, y + 2], fill=(90, 66, 40))
            else:
                gd.ellipse([x, y, x + 6, y + 4], fill=(170, 160, 140), outline=engine.K)
        return np.asarray(gi)

    def age(self, t):
        a = sum(1 for at in self.ages if t >= at)
        return max(0, a - 1) if t >= self.ages[0] else 0

    def converted(self, i, t):
        return t >= self.enemy[i][2]

    def resources(self, t):
        return (300 + int((t - self.t0) * 30), 500 + int((t - self.t0) * 18), "48/50")

    def draw_actors(self, img, d, t):
        b = self.c.beat_pos(t)
        step = int(b * 2) % 2
        pulse = self.c.pulse(t)
        items = []
        items.append((TC[1], lambda: units.age_center(d, *TC, self.age(t))))
        for hx, hy in [(70, 120), (196, 112), (210, 176), (60, 160)]:
            items.append((hy, lambda hx=hx, hy=hy: house(d, hx, hy, self.age(t))))
        for i, (bx, by) in enumerate([(50, 196), (70, 206), (36, 210)]):
            left = 1 - 0.1 * ((t - self.t0) % 10)
            items.append((by, lambda bx=bx, by=by, left=left: units.berry_bush(d, bx, by, left)))
            vx, vy = bx + 10, by + 2
            items.append((vy, lambda vx=vx, vy=vy, i=i: sprites.blit(img, "WORKER_A", vx - 6, vy - 14 - (2 * pulse if i % 2 else 0), skin="toga")))
        for j in range(3):
            fx = 140 + j * 50 + 10 * math.sin(t * 0.8 + j)
            items.append((240, lambda fx=fx, j=j: units.fishing_boat(d, fx, 240, f=1 if j % 2 else -1, bob=int(math.sin(t * 3 + j) * 1.5))))
        # wonder under construction
        wk = ease((t - self.t_twelve) / max(0.2, self.t_build + 1.2 - self.t_twelve))
        wx, wy = 300, 120
        if t >= self.t_twelve - 0.5:
            hgt = int(50 * wk)
            items.append((wy, lambda: (d.rectangle([wx - 30, wy - 6, wx + 30, wy], fill=(200, 190, 160), outline=engine.K),
                                       d.polygon([(wx - 26, wy - 6), (wx, wy - 6 - hgt), (wx + 26, wy - 6)], fill=(226, 210, 150), outline=engine.K) if hgt > 2 else None,
                                       [d.line([wx - 28 + i * 8, wy - 6, wx - 28 + i * 8, wy - 60], fill=(150, 110, 60)) for i in range(8)] if wk < 1 else None)))
        # priest + enemy army (red until converted)
        px, py = 450, 160
        items.append((py, lambda: sprites.blit(img, "PRIEST", px - 6, py - 14 - (2 if self.t_wolo <= t < self.t_wolo + 1.5 and pulse > 0.5 else 0), team="blue")))
        for i, (ex, ey, ct) in enumerate(self.enemy):
            team = "blue" if self.converted(i, t) else "red"
            if t >= self.t_river - 0.6 and i < 3:
                k = ease((t - self.t_river + 0.6 - i * 0.15) / 2.0)
                ex, ey = lerp(ex, 690 + i * 6, k), lerp(ey, 130 + i * 30, k)
                items.append((ey, lambda ex=ex, ey=ey, team=team: units.elephant(d, ex, ey, team=team, step=step)))
            elif i < 3:
                items.append((ey, lambda ex=ex, ey=ey, team=team: units.elephant(d, ex, ey, team=team, step=0)))
            else:
                items.append((ey, lambda ex=ex, ey=ey, team=team: sprites.blit(img, "SOLDIER_A", ex - 6, ey - 14, team=team)))
            if self.converted(i, t) and t - ct < 0.4:
                r = int(4 + (t - ct) * 40)
                items.append((400, lambda ex=ex, ey=ey, r=r: d.ellipse([ex - r, ey - 10 - r // 2, ex + r, ey - 10 + r // 2], outline=(255, 255, 255))))
        if self.t_wolo <= t < self.t_mine + 1.0:
            for k in range(3):
                r = int(((t - self.t_wolo) * 70 + k * 22) % 80)
                items.append((401, lambda r=r: d.ellipse([px - r, py - 8 - r // 2, px + r, py - 8 + r // 2], outline=(250, 240, 160))))
        # laser trooper in a toga
        if t >= self.t_laser - 0.5:
            lx, ly = 760, 200
            items.append((ly, lambda: (sprites.blit(img, "WORKER_A", lx - 6, ly - 14, skin="toga"),
                                       d.rectangle([lx + 3, ly - 9, lx + 9, ly - 7], fill=(80, 80, 96), outline=engine.K))))
            if t >= self.t_laser:
                ph = (t - self.t_laser) * 4 % 1
                tx, ty = 900, 170 + int(math.sin(t * 7) * 20)
                if ph < 0.4:
                    items.append((402, lambda tx=tx, ty=ty: (d.line([lx + 9, ly - 8, tx, ty], fill=(255, 60, 220), width=2),
                                                             d.line([lx + 9, ly - 8, tx, ty], fill=(255, 220, 255)))))
        # trebuchets vs the castle wall
        broken = ease((t - self.t_over) / 0.6)
        items.append((150, lambda: wall_and_keep(d, 900, 150, broken)))
        if t >= self.t_kings - 0.4:
            for j in range(2):
                tx, ty = 800 + j * 20, 120 + j * 50
                arm = 0.0
                if t >= self.t_treb:
                    ph = ((t - self.t_treb) * 1.2 + j * 0.5) % 1.5
                    arm = ease(ph / 0.5) if ph < 1.0 else 1 - (ph - 1.0) / 0.5
                    if 0.3 < ph < 1.1:
                        k = (ph - 0.3) / 0.8
                        bx, by = lerp(tx + 18, 900, k), lerp(ty - 40, 140, k) - 50 * math.sin(k * math.pi)
                        items.append((403, lambda bx=bx, by=by: d.ellipse([bx - 3, by - 3, bx + 3, by + 3], fill=(120, 116, 110), outline=engine.K)))
                items.append((ty, lambda tx=tx, ty=ty, arm=arm: units.trebuchet(d, tx, ty, f=1, arm=arm)))
        if self.t_over <= t < self.t_over + 0.8:
            items.append((404, lambda: units.explosion(d, 900, 130, (t - self.t_over) / 0.8, 1.6)))
        for _, fn in sorted(items, key=lambda e: e[0]):
            fn()

    def camera(self, t):
        L = self.L
        return engine.shot_cam(t, [(self.t0, (0, 30)), (L[2], (0, 80)), (self.t_fish, (90, 98)), (L[3], (130, 10)),
                                   (L[4], (300, 40)), (self.t_river - 0.4, (440, 40)), (L[6], (580, 60)), (L[7], (640, 30))], trans=0.5)

    def minimap_dots(self, t):
        return [(TC[0], TC[1], (90, 140, 255), True)] + [(ex, ey, (90, 140, 255) if self.converted(i, t) else (240, 80, 60), False)
                                                         for i, (ex, ey, _c) in enumerate(self.enemy)]

    def overlay(self, frame, t, cam):
        if self.footage:
            return
        d = ImageDraw.Draw(frame)
        if self.t_97 <= t < self.t_97 + 1.4:
            engine.big_text(frame, "1997", t - self.t_97, scale=4, y=hud.TOP + 26)
        if self.t_spin - 0.4 <= t < self.L[1]:  # flipping history book
            k = (t - self.t_spin + 0.4) * 3
            bx, by = 192, hud.TOP + 80
            d.rectangle([bx - 60, by - 30, bx + 60, by + 30], fill=(120, 60, 30), outline=engine.K)
            d.rectangle([bx - 56, by - 27, bx - 2, by + 27], fill=(240, 230, 200), outline=engine.K)
            d.rectangle([bx + 2, by - 27, bx + 56, by + 27], fill=(240, 230, 200), outline=engine.K)
            for i in range(5):
                d.line([bx - 50, by - 18 + i * 9, bx - 10, by - 18 + i * 9], fill=(150, 140, 120))
            fx = bx + 54 * math.cos(math.pi * (k % 1))
            d.polygon([(bx, by - 27), (fx, by - 30), (fx, by + 30), (bx, by + 27)], fill=(250, 244, 220), outline=engine.K)
        names = ["STONE AGE", "TOOL AGE", "BRONZE AGE", "IRON AGE"]
        for i, at in enumerate(self.ages):
            nxt = self.ages[i + 1] if i + 1 < 4 else self.L[2]
            if at <= t < nxt:
                engine.big_text(frame, names[i], t - at, scale=3, y=hud.TOP + 22)
        if self.t_twelve <= t < self.L[4]:
            n = min(12, int((t - self.t_twelve) / 0.12) + 1)
            for i in range(n):
                x = 12 + i * 30
                d.line([x, hud.TOP + 6, x, hud.TOP + 24], fill=engine.K)
                d.rectangle([x + 1, hud.TOP + 6, x + 14, hud.TOP + 14], fill=CIV_COLS[i], outline=engine.K)
        if self.t_build <= t < self.L[4]:
            draw_text(frame, 120, hud.TOP + 30, "WONDER: 87%", hud.GOLD_TXT, outline=True)
        if self.t_wolo <= t < self.t_wolo + 1.4:
            engine.big_text(frame, "WOLOLO!", t - self.t_wolo, scale=4, y=hud.TOP + 26, col=(250, 240, 160))
        if self.t_typed - 0.1 <= t < self.t_laser:
            txt = "PHOTON MAN"[:int((t - self.t_typed + 0.1) * 12)]
            d.rectangle([90, hud.TOP + 100, 294, hud.TOP + 116], fill=(20, 16, 10), outline=(230, 196, 110))
            draw_text(frame, 94, hud.TOP + 105, "CHAT: " + txt + ("_" if int(t * 6) % 2 else ""), (236, 236, 236), shadow=None)
        if self.t_over <= t < self.t_over + 1.2:
            engine.big_text(frame, "OVER!", t - self.t_over, scale=5, y=hud.TOP + 50)

    def postfx(self, frame, t):
        return 0.25 if any(0 <= t - at < 0.08 for at in self.ages) or 0 <= t - self.t_over < 0.1 else 0.0

    def portrait(self, t, singing):
        def laurel(d, x, y):
            for i in range(5):
                d.ellipse([x + 6 + i * 4, y + 3 - abs(i - 2), x + 9 + i * 4, y + 6 - abs(i - 2)], fill=(230, 190, 70), outline=engine.K)
        return engine.portrait(skin=(214, 160, 116), hair=(30, 22, 18), shirt=(236, 232, 214), bg=(120, 90, 50),
                               mouth=engine.mouth_amt(self.c, t, singing), blink=int(t * 10) % 43 == 0, extra=laurel)


def wall_and_keep(d, x, y, broken):
    units.wall_segment(d, x - 50, y, 40, broken)
    units.wall_segment(d, x - 50, y + 60, 40, broken * 0.6)
    d.rectangle([x + 10, y - 40, x + 60, y + 60], fill=(176, 168, 150), outline=engine.K)
    d.rectangle([x + 20, y - 52, x + 50, y - 40], fill=(160, 150, 130), outline=engine.K)
    for cx in range(x + 10, x + 60, 7):
        d.rectangle([cx, y - 46, cx + 3, y - 40], fill=(176, 168, 150), outline=engine.K)
    d.rectangle([x + 28, y + 40, x + 42, y + 60], fill=(60, 40, 24), outline=engine.K)
    d.line([x + 35, y - 52, x + 35, y - 64], fill=engine.K)
    d.polygon([(x + 36, y - 64), (x + 46, y - 60), (x + 36, y - 56)], fill=(200, 50, 40))


def house(d, x, y, age):
    if age == 0:
        d.polygon([(x - 7, y), (x, y - 12), (x + 7, y)], fill=(150, 116, 70), outline=engine.K)
    else:
        wall = [(150, 108, 64), (196, 160, 110), (236, 232, 222)][min(age, 3) - 1]
        d.rectangle([x - 8, y - 9, x + 8, y], fill=wall, outline=engine.K)
        d.polygon([(x - 10, y - 9), (x, y - 16), (x + 10, y - 9)], fill=(170, 80, 50) if age < 3 else (220, 216, 206), outline=engine.K)
        d.rectangle([x - 2, y - 5, x + 2, y], fill=(60, 40, 24))
