"""Verse 2: orcs vs humans in a forest kingdom (original designs, 1995 homage)."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine, hud, sprites, units, world
from clock import ease, lerp
from font import draw_text, text_width
from sc_chant import forest_trees

CASTLE = (330, 186)
MINE = (430, 96)
GATE = (330, 190)


class Verse2(engine.MapScene):
    MAP_W, MAP_H = 1024, 256
    theme, title, speaker = "medieval", "TIDES 1995", "Warchief"
    use_fog = False

    def __init__(self, ctx, sec):
        super().__init__(ctx, sec)
        tl = self.tl
        w = lambda i, k: tl.word_t(sec, i, k)
        self.L = [l["start"] for l in tl.sec(sec)["lines"]] + [tl.sec(sec)["end"]]
        self.t_95, self.t_shore = w(0, "Ninety"), w(0, "shore")
        self.t_door, self.t_zug = w(1, "door"), w(2, "Zug")
        self.t_blood, self.t_cata = w(4, "bloodlust"), w(4, "catapults")
        self.t_raise, self.t_still = w(5, "raise"), w(5, "still")
        self.t_click, self.t_boom, self.t_tomb = w(6, "click"), w(6, "boom"), w(7, "tomb")
        rng = np.random.default_rng(21)
        self.forest = sorted([(int(x), int(y)) for x, y in zip(rng.integers(490, 660, 70), rng.integers(40, 236, 70))], key=lambda p: p[1])
        chop0, chop1 = self.L[3] - 0.3, self.L[4] - 0.2
        self.chop_t = {p: chop0 + (chop1 - chop0) * (i / len(self.forest)) for i, p in
                       enumerate(sorted(self.forest, key=lambda p: (p[0] - 575) ** 2 + (p[1] - 140) ** 2))}
        self.trees = forest_trees(self.MAP_W, self.MAP_H, [(150, 0, 1024, 256)], seed=4, rows=(18, 30)) + \
                     forest_trees(self.MAP_W, self.MAP_H, [(0, 0, 680, 256), (760, 0, 1024, 256)], seed=5, rows=(18, 30, 42))
        self.skel = [(870 + (i % 4) * 22, 150 + (i // 4) * 24, self.t_raise + i * 0.12) for i in range(8)]
        self.sheep = (936, 214)

    def build_ground(self):
        g = world.grass_layer(self.MAP_W, self.MAP_H, seed=13)
        g = world.dirt_path(g, [(90, 170), (200, 180), GATE, (420, 150), (500, 150), (680, 160), (860, 170)], width=6)
        h, w, _ = g.shape
        for y in range(h):  # sea on the left
            edge = int(70 + 10 * math.sin(y / 17) + 5 * math.sin(y / 5))
            g[y, :edge] = (34, 74, 148)
            g[y, edge:edge + 3] = (210, 190, 130)
            g[y, 4:edge - 6:9] = (70, 118, 196)
        yy, xx = np.mgrid[0:h, 0:w]
        hill = ((xx - 740) / 80) ** 2 + ((yy - 96) / 48) ** 2
        g[hill < 1.0] = (88, 146, 66)
        g[(hill >= 1.0) & (hill < 1.12)] = (60, 50, 40)
        g[(hill < 1.0) & ((xx + yy) % 9 == 0)] = (70, 128, 54)
        grave = ((xx - 920) / 70) ** 2 + ((yy - 160) / 40) ** 2 < 1
        g[grave & ((xx * 7 + yy * 3) % 5 == 0)] = (70, 70, 60)
        return g

    def orc_pos(self, i, t):
        x0, y0 = 80, 150 + (i % 3) * 10
        start = self.t_shore - 0.4 + i * 0.15
        k = ease((t - start) / 2.6)
        gx, gy = GATE[0] - 30 + (i % 3) * 14, GATE[1] + 4 + (i // 3) * 12
        if t > self.t_door + 0.2:
            k2 = ease((t - self.t_door - 0.2) / 1.0)
            return lerp(gx, GATE[0], k2), lerp(gy, GATE[1] - 6, k2), True, k2 >= 1
        return lerp(x0, gx, k), lerp(y0, gy, k), 0 < k < 1, False

    def resources(self, t):
        chopped = sum(1 for p, ct in self.chop_t.items() if t >= ct)
        return (1450 + int((t - self.t0) * 12), 600 + chopped * 25, "18/24")

    def draw_actors(self, img, d, t):
        b = self.c.beat_pos(t)
        step = int(b * 2) % 2
        pulse = self.c.pulse(t)
        items = []
        # boats
        bk = ease((t - self.t0 + 1.5) / 2.4)
        for j in range(2):
            items.append((140 + j * 30, lambda j=j: units.boat(d, lerp(-30, 52, bk) - j * 6, 150 + j * 30, team="red", bob=int(math.sin(t * 3 + j) * 1.5))))
        dmg = ease((t - self.L[1]) / (self.t_door - self.L[1] + 0.01)) * 0.6
        items.append((CASTLE[1], lambda: units.castle(d, *CASTLE, team="blue", damage=dmg, gate_open=t >= self.t_door)))
        for i in range(3):  # defenders on the wall
            items.append((CASTLE[1] - 40, lambda i=i: sprites.blit(img, "SOLDIER_A", CASTLE[0] - 26 + i * 18, CASTLE[1] - 50)))
        for i in range(6):
            x, y, mv, inside = self.orc_pos(i, t)
            if inside:
                continue
            ram = self.L[1] <= t < self.t_door and i < 3
            items.append((y, lambda x=x, y=y, mv=mv, ram=ram: sprites.blit(img, "SOLDIER_B" if (mv or ram) and step else "SOLDIER_A",
                                                                         x - 6 + (2 * pulse if ram else 0), y - 14, team="red", skin="orc")))
        # mine peons
        world.draw_goldmine(d, *MINE, glint=int(b * 2))
        for i in range(3):
            cyc = (b + i * 2.7) % 6
            inside = 2.5 < cyc < 3.5
            k = ease(cyc / 2.5) if cyc <= 2.5 else ease((6 - cyc) / 2.5)
            x, y = lerp(470, MINE[0] + 22, k), lerp(170, 136, k)
            if not inside:
                items.append((y, lambda x=x, y=y, cyc=cyc: sprites.blit(img, "WORKER_B" if step else "WORKER_A", x - 6, y - 12, team="red", skin="orc", flip=cyc < 3)))
        # forest + choppers
        for p in self.forest:
            if t >= self.chop_t[p]:
                items.append((p[1] - 1, lambda p=p: units.stump(d, *p)))
            else:
                near = self.chop_t[p] - t < 0.4
                items.append((p[1], lambda p=p, near=near: world.draw_tree(d, p[0], p[1], sway=(1 if near and int(t * 12) % 2 else 0))))
        for i in range(4):
            px, py = 500 + i * 40, 200 - (i % 2) * 70
            if t > self.L[2]:
                standing = [p for p in self.forest if t < self.chop_t[p]]
                if standing:
                    tgt = min(standing, key=lambda p: (p[0] - px) ** 2 + (p[1] - py) ** 2)
                    px, py = tgt[0] - 10, tgt[1] + 2
            items.append((py + 1, lambda px=px, py=py: sprites.blit(img, "WORKER_A", px - 6, py - 14 - 2 * pulse, team="red", skin="orc")))
        # hill: catapults + ogre
        for j, (cx, cy) in enumerate([(712, 112), (760, 104)]):
            arm = 0.0
            if t >= self.t_cata:
                ph = (b + j * 2) % 4
                arm = ease(ph / 0.6) if ph < 1.5 else max(0.0, 1 - (ph - 1.5) / 2.5)
                if 0.2 < ph < 2.4 and t >= self.t_cata:
                    k = (ph - 0.2) / 2.2
                    sx, sy = cx + 10, cy - 20
                    tx, ty = 830 + j * 20, 210
                    bx, by = lerp(sx, tx, k), lerp(sy, ty, k) - 60 * math.sin(k * math.pi)
                    items.append((300, lambda bx=bx, by=by: d.ellipse([bx - 2, by - 2, bx + 2, by + 2], fill=(110, 110, 110), outline=engine.K)))
                if 2.4 <= ph < 3.2:
                    items.append((301, lambda j=j, ph=ph: units.explosion(d, 830 + j * 20, 206, (ph - 2.4) / 0.8, 0.8)))
            items.append((cy, lambda cx=cx, cy=cy, arm=arm: units.catapult(d, cx, cy, team="red", arm=arm)))
        rage = 1.0 if t >= self.t_blood else 0.0
        ox = 700 + 30 * ease((t - self.t_blood) / 3)
        items.append((176, lambda: units.ogre(d, ox, 176, team="red", step=step, rage=rage * (0.6 + 0.4 * pulse))))
        world.draw_building(d, "tower", 828, 176, (sprites.TEAMS["blue"]["T"], sprites.TEAMS["blue"]["t"]))
        # graveyard
        for gx, gy in [(880, 130), (910, 124), (950, 136), (975, 170)]:
            items.append((gy, lambda gx=gx, gy=gy: (d.rectangle([gx - 3, gy - 8, gx + 3, gy], fill=(120, 120, 130), outline=engine.K),
                                                    d.line([gx - 1, gy - 6, gx + 1, gy - 6], fill=engine.K))))
        cast = ease((t - self.t_raise + 0.5) / 0.5) if self.t_raise - 0.5 <= t < self.t_still + 0.5 else 0.0
        items.append((122, lambda: units.death_knight(d, 860, 122, team="red", cast=cast)))
        for i, (sx, sy, st) in enumerate(self.skel):
            rise = ease((t - st) / 0.7)
            if rise <= 0:
                continue
            walk = max(0.0, t - self.t_still) * 14
            items.append((sy, lambda sx=sx, sy=sy, rise=rise, walk=walk: skeleton_draw(d, sx - walk, sy, rise, step)))
        # the sheep
        if t < self.t_boom:
            hop = 2 if (self.t_click <= t and self.c.pulse(t) > 0.5) else 0
            items.append((self.sheep[1], lambda: sprites.blit(img, "SHEEP", self.sheep[0] - 4, self.sheep[1] - 6 - hop)))
        elif t < self.t_boom + 0.7:
            k = (t - self.t_boom) / 0.7
            items.append((400, lambda k=k: units.explosion(d, self.sheep[0], self.sheep[1] - 4, k, 1.2)))
            for i in range(6):
                a = i * 1.05
                items.append((401, lambda a=a, k=k: d.rectangle([self.sheep[0] + math.cos(a) * 30 * k, self.sheep[1] - 4 + math.sin(a) * 20 * k - 20 * k,
                                                                self.sheep[0] + math.cos(a) * 30 * k + 2, self.sheep[1] - 2 + math.sin(a) * 20 * k - 20 * k], fill=(236, 236, 224))))
        if t >= self.t_tomb - 0.8:
            sx, sy = self.sheep
            items.append((sy, lambda: (d.rounded_rectangle([sx - 7, sy - 16, sx + 7, sy], radius=4, fill=(150, 150, 160), outline=engine.K),
                                       draw_text(img, sx - 7, sy - 11, "RIP", (40, 40, 50), shadow=None))))
        for tx, ty in self.trees:
            items.append((ty, lambda tx=tx, ty=ty: world.draw_tree(d, tx, ty)))
        for _, fn in sorted(items, key=lambda e: e[0]):
            fn()

    def camera(self, t):
        L = self.L
        return engine.shot_cam(t, [(self.t0 - 1, (0, 40)), (L[1] - 0.2, (150, 60)), (L[2] - 0.2, (330, 20)),
                                   (L[3], (420, 30)), (L[4], (560, 30)), (L[5], (640, 50)), (L[6] - 0.2, (640, 80))], trans=0.5)

    def minimap_dots(self, t):
        return [(CASTLE[0], CASTLE[1] - 20, (90, 140, 255), True), (MINE[0], MINE[1], (246, 206, 62), True)] + \
               [(*self.orc_pos(i, t)[:2], (240, 80, 60), False) for i in range(6)]

    def overlay(self, frame, t, cam):
        cx, cy = cam
        sp = lambda x, y: (x - cx, y - cy + hud.TOP)
        if self.t_95 <= t < self.t_95 + 1.4 and not self.footage:
            engine.big_text(frame, "1995", t - self.t_95, scale=4, y=hud.TOP + 26)
        if self.t_zug <= t < self.t_zug + 1.2:
            x, y = sp(MINE[0] + 40, 120)
            bubble(frame, x, y, "ZUG ZUG!")
        if self.t_door <= t < self.t_door + 1.0:
            engine.big_text(frame, "CRASH!", t - self.t_door, scale=3, y=hud.TOP + 40)
        if self.t_blood <= t < self.t_blood + 1.2:
            engine.big_text(frame, "BLOODLUST!", t - self.t_blood, scale=3, y=hud.TOP + 30, col=(240, 70, 50))
        if self.t_click <= t < self.t_boom:
            n = int((t - self.t_click) / max(0.1, (self.t_boom - self.t_click)) * 7) + 1
            x, y = sp(*self.sheep)
            engine.cursor(frame, x + 2, y - 8 - (1 if self.c.pulse(t * 1.0) > 0.7 else 0))
            draw_text(frame, x - 24, y - 26, f"CLICK x{n}", (255, 255, 255), outline=True)
        if self.t_boom <= t < self.t_boom + 1.0:
            engine.big_text(frame, "BOOM!", t - self.t_boom, scale=5, y=hud.TOP + 50, col=(255, 160, 60))
        if self.L[3] <= t < self.L[4]:
            draw_text(frame, 4, hud.TOP + 3, "LUMBER +25", hud.GOLD_TXT) if int(t * 6) % 2 else None

    def portrait(self, t, singing):
        return engine.portrait(skin=(98, 160, 70), hair=(40, 40, 40), shirt=(200, 50, 40), bg=(70, 40, 30),
                               mouth=engine.mouth_amt(self.c, t, singing), blink=int(t * 10) % 37 == 0,
                               extra=lambda d, x, y: (d.point((x + 12, y + 25), fill=(240, 240, 220)), d.point((x + 18, y + 25), fill=(240, 240, 220))))


def skeleton_draw(d, x, y, rise, step):
    units.skeleton(d, x, y, f=-1, rise=rise, step=step)


def bubble(frame, x, y, txt):
    d = ImageDraw.Draw(frame)
    w = text_width(txt)
    d.rectangle([x - 2, y - 2, x + w + 2, y + 8], fill=(250, 250, 250), outline=engine.K)
    d.polygon([(x + 2, y + 8), (x - 4, y + 14), (x + 8, y + 8)], fill=(250, 250, 250), outline=engine.K)
    draw_text(frame, x, y, txt, (30, 24, 20), shadow=None)
