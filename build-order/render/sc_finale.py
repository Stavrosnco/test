"""Final chorus: every army from every chapter on one map; bedroom in daylight; recap cuts."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine, hud, sprites, units, world, bedroom
from clock import ease, lerp
from font import draw_text, text_width

FW_COLS = [(255, 90, 80), (90, 160, 255), (250, 220, 90), (120, 230, 120), (220, 120, 230)]


class GrandMap(engine.MapScene):
    MAP_W, MAP_H = 1024, 256
    theme, title, speaker = "medieval", "ONE MORE GAME", "Everyone"

    def __init__(self, ctx, sec):
        super().__init__(ctx, sec)
        self.L = [l["start"] for l in self.tl.sec(sec)["lines"]] + [self.tl.sec(sec)["end"]]
        rng = np.random.default_rng(55)
        self.trees = sorted([(int(x), int(y)) for x, y in zip(rng.integers(0, 1024, 50), rng.choice([24, 36, 240, 250], 50))], key=lambda p: p[1])

    def build_ground(self):
        g = world.grass_layer(self.MAP_W, self.MAP_H, seed=77)
        g = world.dirt_path(g, [(0, 130), (300, 128), (600, 134), (1024, 130)], width=20, seed=3)
        return g

    def fog_sources(self, t):
        lift = ease((t - self.L[6]) / (self.L[7] - self.L[6]))
        return [(self.camera(t)[0] + 192, 130, 150 + 700 * lift)] + [(x, 130, 160) for x in range(0, 1024, 120) if t > self.L[7]]

    def camera(self, t):
        k = (t - self.t0) / (self.t1 - self.t0)
        return lerp(0, 640, k), 40

    def resources(self, t):
        return (99999, 99999, "200/200")

    def draw_actors(self, img, d, t):
        b = self.c.beat_pos(t)
        step = int(b * 2) % 2
        march = (t - self.t0) * 28
        items = []
        rows = [
            (96, lambda x, y: sprites.blit(img, "SOLDIER_B" if step else "SOLDIER_A", x - 6, y - 14), 30),
            (112, lambda x, y: sprites.blit(img, "SOLDIER_B" if step else "SOLDIER_A", x - 6, y - 14, team="red", skin="orc"), 34),
            (134, lambda x, y: units.tank(d, x, y, team="gold", big=True), 90),
            (154, lambda x, y: units.elephant(d, x, y, team="blue", step=step), 80),
            (170, lambda x, y: sprites.blit(img, "ZERGLING", x - 5, y - 6, team="purple"), 22),
            (188, lambda x, y: units.scv(d, x, y, step=step), 50),
            (206, lambda x, y: units.harvester(d, x, y, team="blue", load=1, glow=(230, 120, 40)), 110),
            (78, lambda x, y: units.ogre(d, x, y, step=step), 120),
        ]
        for y, fn, gap in rows:
            for i in range(int(1024 / gap) + 2):
                x = (i * gap + march * (1 + (y % 3) * 0.15) + (y * 7) % gap) % 1100 - 40
                items.append((y, lambda x=x, y=y, fn=fn: fn(x, y + (2 if (i + step) % 2 else 0) * 0)))
        for tx, ty in self.trees:
            items.append((ty, lambda tx=tx, ty=ty: world.draw_tree(d, tx, ty)))
        for _, f in sorted(items, key=lambda e: e[0]):
            f()
        # fireworks on downbeats
        db = self.c.downbeats
        for i, st in enumerate(db[(db > self.t0 - 2) & (db <= t)][-3:]):
            k = (t - st) / 1.2
            if 0 <= k < 1:
                fx = self.camera(st)[0] + 60 + (int(st * 37) % 260)
                fy = 60 + int(st * 13) % 40
                col = FW_COLS[int(st * 3) % 5]
                for a in range(12):
                    ang = a * math.pi / 6
                    r = 6 + k * 34
                    px, py = fx + math.cos(ang) * r, fy + math.sin(ang) * r + k * k * 14
                    d.rectangle([px, py, px + 1, py + 1], fill=col if k < 0.7 else tuple(c // 2 for c in col))

    def overlay(self, frame, t, cam):
        if not self.footage:
            engine.kinetic(frame, self.tl, t, self.sec, scale=4, y=hud.TOP + 40)

    def postfx(self, frame, t):
        return 0.5 * max(0.0, 1 - (t - self.t0) / 0.5) if t >= self.t0 else 0.0


class Finale:
    def __init__(self, ctx, sec):
        self.ctx, self.c, self.tl, self.sec = ctx, ctx.clock, ctx.timeline, sec
        self.map = GrandMap(ctx, sec)
        self.room = bedroom.Bedroom()
        self.L = self.map.L
        w = lambda i, k: self.tl.word_t(sec, i, k)
        self.cuts = [(w(2, "Rush"), "v5", lambda s: s.t_ling + 1.0, "RUSH 'EM!"),
                     (w(2, "tower"), "v2", lambda s: s.L[4] + 1.5, "TOWER!"),
                     (w(2, "turtle"), "v3", lambda s: s.L[6] + 1.0, "TURTLE!"),
                     (w(2, "tech"), "v4", lambda s: s.ages[3] + 0.3, "TECH IT LATE!")]
        self.t_mom = w(1, "Mom")

    def frame(self, t):
        L = self.L
        if L[1] <= t < L[2] or L[5] <= t < L[6]:
            door = ease((t - self.t_mom) / 0.4) if L[1] <= t < L[2] else 0.0
            line, _ = self.tl.line_at(t, sec=self.sec)
            cheer = 1.0 - min(1.0, (t - L[5]) * 0.8) if L[5] <= t < L[6] else 0.3
            scr, _ = self.map.frame(t, lyric_t=t)
            img = self.room.draw(t, dawn=1.0, clock_h=12.1, door=door, mom="IT'S NOON!!" if door else None,
                                 screen=scr, kid_bob=self.c.pulse(t), cheer=max(0.0, cheer))
            engine.kinetic(img, self.tl, t, self.sec, scale=3, y=22, sub=True)
            return img, 0.0
        if L[2] <= t < L[3]:
            for i, (st, key, when, word) in enumerate(self.cuts):
                nxt = self.cuts[i + 1][0] if i + 1 < 4 else L[3]
                if st <= t < nxt or (i == 0 and t < st):
                    sc = self.ctx.scenes[key]
                    img, _ = sc.frame(when(sc) + (t - st) * 0.6, lyric_t=t)
                    engine.big_text(img, word, t - st, scale=4, y=hud.TOP + 70)
                    return img, 0.15 if 0 <= t - st < 0.06 else 0.0
        return self.map.frame(t)
