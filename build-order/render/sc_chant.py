"""Ensemble chant: a base builds itself on each 'Build order!' hit."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine, sprites, world, hud
from clock import ease, lerp

BLUE = (sprites.TEAMS["blue"]["T"], sprites.TEAMS["blue"]["t"])
MINE, HALL = (40, 118), (150, 98)
MINE_DOOR, HALL_DOOR = (62, 160), (170, 142)
RALLY, TARGET = (300, 160), (520, 150)


def forest_trees(map_w, map_h, avoid, seed=7, rows=(20, 32, 44), clusters=None):
    rng = np.random.default_rng(seed)
    pts = []
    for row_y in rows:
        for x in range(-6, map_w + 6, 11):
            pts.append((x + int(rng.integers(-3, 4)), row_y + int(rng.integers(-3, 4))))
    for cx, cy, n in clusters or []:
        for _ in range(n):
            pts.append((cx + int(rng.integers(-26, 27)), cy + int(rng.integers(-18, 19))))
    return [p for p in pts if not any(x0 < p[0] < x1 and y0 < p[1] < y1 for x0, y0, x1, y1 in avoid)]


def scatter(gi, rng, n, avoid, y_min=50):
    gd = ImageDraw.Draw(gi)
    w, h = gi.size
    for _ in range(n):
        x, y = int(rng.integers(0, w)), int(rng.integers(y_min, h))
        if any(x0 < x < x1 and y0 < y < y1 for x0, y0, x1, y1 in avoid):
            continue
        if rng.random() < 0.5:
            gd.ellipse([x, y, x + 5, y + 3], fill=(120, 118, 126), outline=engine.K)
            gd.point((x + 1, y + 1), fill=(170, 168, 176))
        else:
            gd.ellipse([x, y, x + 7, y + 5], fill=(30, 78, 34), outline=engine.K)
            gd.point((x + 2, y + 1), fill=(70, 136, 58))


class ChantScene(engine.MapScene):
    theme, title, speaker = "medieval", "BUILD ORDER", "Ensemble"

    def __init__(self, ctx, sec):
        tl = ctx.timeline
        w = lambda i, k: tl.word_t(sec, i, k)
        ch = [engine.chunks(l) for l in tl.sec(sec)["lines"]]
        hits = [c[0] for c in ch[0]] + [ch[1][0][0]] + [c[0] for c in ch[2]]
        # (kind, x, y, done_time)
        self.builds = [("farm", 214, 58, hits[0]), ("farm", 248, 58, hits[1]), ("barracks", 214, 128, hits[2]),
                       ("tower", 282, 104, hits[3]), ("mill", 92, 196, hits[4]), ("farm", 282, 58, w(3, "command"))]
        self.build_dur = 1.6
        self.t_select, self.t_order = w(3, "whole"), w(3, "command")
        self.avoid = [(bx - 12, by - 12, bx + 52, by + 48) for _k, bx, by, _d in self.builds] + \
                     [(HALL[0] - 10, HALL[1] - 14, HALL[0] + 56, HALL[1] + 50), (MINE[0] - 8, MINE[1] - 8, MINE[0] + 56, MINE[1] + 46)]
        super().__init__(ctx, sec)
        self.t0 -= 2.0  # scene is cut in a little before the first chant word
        self.trees = forest_trees(self.MAP_W, self.MAP_H, self.avoid, clusters=[
            (372, 92, 9), (430, 214, 7), (20, 230, 6), (560, 70, 8), (610, 210, 10), (130, 238, 5), (470, 90, 5)])
        self.workers = [i * 1.6 for i in range(5)]

    def build_ground(self):
        g = world.grass_layer(self.MAP_W, self.MAP_H)
        g = world.dirt_path(g, [MINE_DOOR, (110, 156), HALL_DOOR, (200, 150), RALLY, (420, 152), TARGET])
        g = world.water(g, 584, 600)
        gi = Image.fromarray(g)
        scatter(gi, np.random.default_rng(11), 70, self.avoid)
        return np.asarray(gi)

    def soldiers(self, t):
        out = []
        b_order = self.t_order
        for i in range(6):
            born = self.builds[2][3] + i * 0.45
            if t < born:
                continue
            slot = (RALLY[0] + (i % 3) * 14, RALLY[1] - 14 + (i // 3) * 16)
            door = (232, 162)
            if t < b_order:
                k = ease((t - born) / 1.2)
                x, y, moving = lerp(door[0], slot[0], k), lerp(door[1], slot[1], k), k < 1
            else:
                k = ease((t - b_order - i * 0.1) / 2.6)
                dst = (TARGET[0] - 20 + (i % 3) * 14, TARGET[1] - 14 + (i // 3) * 16)
                x, y, moving = lerp(slot[0], dst[0], k), lerp(slot[1], dst[1], k), 0 < k < 1
            out.append((x, y, moving, slot))
        return out

    def camera(self, t):
        k = ease((t - self.t0 - 1.0) / (self.t1 - self.t0 + 1.0))
        return lerp(10, 236, k), lerp(14, 60, k)

    def resources(self, t):
        b = self.c.beat_pos(t)
        trips = sum(max(0, math.floor((b + ph) / 8)) for ph in self.workers)
        food = 5 + len(self.soldiers(t))
        cap = 4 + 4 * sum(1 for k, *_r, done in self.builds if k == "farm" and t >= done)
        return (300 + 10 * trips, 800 + 5 * int(b), f"{food}/{max(cap, food)}")

    def draw_actors(self, img, d, t):
        b = self.c.beat_pos(t)
        world.draw_goldmine(d, *MINE, glint=int(b * 2))
        world.draw_building(d, "hall", *HALL, BLUE)
        site_workers = []
        for kind, x, y, done in self.builds:
            if t < done - self.build_dur:
                continue
            prog = (t - (done - self.build_dur)) / self.build_dur
            world.draw_building(d, kind, x, y, BLUE, progress=min(prog, 1.0))
            if prog < 1:
                site_workers.append((x - 10, y + 20))
            elif t - done < 0.4:
                r = int(6 + (t - done) * 50)
                d.ellipse([x + 10 - r, y + 30 - r // 2, x + 10 + r, y + 30 + r // 2], outline=(220, 210, 180))
        items = []
        for ph in self.workers:
            cyc = (b + ph) % 8
            back = cyc >= 4
            k = ease((cyc - 4 if back else cyc) / 4)
            a, z = (HALL_DOOR, MINE_DOOR) if not back else (MINE_DOOR, HALL_DOOR)
            x, y = lerp(a[0], z[0], k) - 6, lerp(a[1], z[1], k) - 12 + 4 * math.sin(ph * 3)
            items.append((y, "WORKER_B" if (b * 2) % 2 < 1 else "WORKER_A", x, z[0] < a[0], back))
        for x, y in site_workers:
            items.append((y, "WORKER_A", x, False, False))
        for x, y, moving, _ in self.soldiers(t):
            items.append((y - 12, "SOLDIER_B" if moving and (b * 2) % 2 < 1 else "SOLDIER_A", x - 6, False, False))
            if t >= self.t_select + 0.6:
                d.ellipse([x - 7, y, x + 7, y + 4], outline=hud.GREEN)
        sh = int(b / 6) % 3
        items.append((196, "SHEEP", 440 + sh * 6, sh == 1, False))
        layer = [(y + 14, 0, it) for it in items for y in [it[0]]] + [(ty, 1, (tx, ty)) for tx, ty in self.trees]
        pulse = self.c.pulse(t)
        for _, typ, it in sorted(layer, key=lambda e: (e[0], e[1])):
            if typ == 1:
                world.draw_tree(d, it[0], it[1], sway=1 if pulse > 0.5 and it[0] % 3 == 0 else 0)
                continue
            y, name, x, flip, carry = it
            if name.startswith("WORKER") and it in [(yy, "WORKER_A", xx, False, False) for xx, yy in site_workers]:
                y -= 2 * pulse
            sprites.blit(img, name, x, y, flip=flip)
            if carry:
                sprites.blit(img, "SACK", x + (8 if flip else 0), y + 5)
        if self.t_order <= t < self.t_order + 0.8:
            r = int(2 + (t - self.t_order) * 10)
            d.line([TARGET[0] - r, TARGET[1] - r, TARGET[0] + r, TARGET[1] + r], fill=hud.GREEN)
            d.line([TARGET[0] - r, TARGET[1] + r, TARGET[0] + r, TARGET[1] - r], fill=hud.GREEN)

    def fog_sources(self, t):
        grow = ease((t - self.t0) / 4)
        srcs = [(173, 120, 110 + 40 * grow), (64, 140, 70)]
        for kind, x, y, done in self.builds:
            if t >= done - self.build_dur:
                srcs.append((x + 14, y + 16, 80))
        for x, y, _, slot in self.soldiers(t):
            for s in np.linspace(0, 1, 6):
                srcs.append((lerp(slot[0], x, s), lerp(slot[1], y, s), 60))
        return srcs

    def minimap_dots(self, t):
        dots = [(HALL[0], HALL[1], (90, 140, 255), True)]
        dots += [(x, y, (90, 140, 255), True) for _k, x, y, done in self.builds if t >= done]
        dots += [(x, y, (160, 200, 255), False) for x, y, *_ in self.soldiers(t)]
        return dots

    def overlay(self, frame, t, cam):
        cx, cy = cam
        y = hud.TOP + 3
        for kind, *_r, done in self.builds:
            if 0 <= t - done < 1.8:
                engine.draw_text(frame, 4, y, f"CONSTRUCTION COMPLETE: {kind.upper()}", hud.GOLD_TXT)
                y += 9
        bar = self.builds[2][3]
        if bar + 0.3 <= t < bar + 2:
            engine.draw_text(frame, 4, y, "UNIT READY", hud.GREEN)
        d = ImageDraw.Draw(frame)
        if self.t_select <= t < self.t_select + 0.6:
            k = ease((t - self.t_select) / 0.5)
            x0, y0 = RALLY[0] - 14 - cx, RALLY[1] - 30 - cy + hud.TOP
            x1, y1 = lerp(x0, x0 + 56, k), lerp(y0, y0 + 40, k)
            d.rectangle([x0, y0, x1, y1], outline=hud.GREEN)
            engine.cursor(frame, x1, y1)
        elif self.t_select + 0.6 <= t < self.t_order + 0.8:
            k = ease((t - self.t_select - 0.6) / max(0.1, self.t_order - self.t_select - 0.6))
            engine.cursor(frame, lerp(RALLY[0] + 42, TARGET[0], k) - cx, lerp(RALLY[1] + 10, TARGET[1], k) - cy + hud.TOP)
        else:
            act = [(x + 14, y + 10) for _k, x, y, done in self.builds if done - self.build_dur <= t < done]
            sx, sy = act[0] if act else (HALL[0] + 30, HALL[1] + 20)
            engine.cursor(frame, sx - cx + 3 * math.sin(t * 2), sy - cy + hud.TOP + 2 * math.cos(t * 3))
        if not self.footage:
            engine.kinetic(frame, self.tl, t, self.sec)

    def postfx(self, frame, t):
        hit = any(abs(t - done) < 0.12 for *_r, done in self.builds)
        return 0.18 if hit else 0.0
