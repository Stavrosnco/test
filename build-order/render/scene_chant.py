"""Ensemble chant: 'Build order! Gather and expand!' A base builds itself on the beat.

Lyric timing here is a placeholder laid on the bar grid until analysis/words.json exists.
"""
import math
import numpy as np
from PIL import Image, ImageDraw
import sprites, world, hud
from clock import ease, lerp
from font import draw_text, text_width

MAP_W, MAP_H = 640, 256
VIEW_W, VIEW_H = hud.W, hud.BOT - hud.TOP
BLUE = (sprites.TEAMS["blue"]["T"], sprites.TEAMS["blue"]["t"])
MINI = (100, 40)

MINE = (40, 118)
HALL = (150, 98)
MINE_DOOR, HALL_DOOR = (62, 160), (170, 142)
# (kind, x, y, done_at_local_beat)
BUILDS = [("farm", 214, 58, 4), ("farm", 248, 58, 8), ("barracks", 214, 128, 12),
          ("tower", 282, 104, 16), ("mill", 92, 196, 20), ("farm", 282, 58, 22)]
RALLY = (300, 160)
TARGET = (520, 150)

# placeholder chant timing, in local beats
CHANT = [(0, 2, "BUILD ORDER!", 3), (2, 4, "(BUILD ORDER!)", 2), (4, 8, "GATHER AND EXPAND!", 2),
         (8, 10, "BUILD ORDER!", 3), (10, 12, "(BUILD ORDER!)", 2),
         (12, 22, "THE WHOLE WORLD|AT YOUR COMMAND!", 2)]

BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16


def _trees():
    rng = np.random.default_rng(7)
    pts = []
    for row_y in (20, 32, 44):
        for x in range(-6, MAP_W + 6, 11):
            pts.append((x + int(rng.integers(-3, 4)), row_y + int(rng.integers(-3, 4))))
    for cx, cy, n in [(372, 92, 9), (430, 214, 7), (20, 230, 6), (560, 70, 8), (610, 210, 10),
                      (130, 238, 5), (470, 90, 5)]:
        for _ in range(n):
            pts.append((cx + int(rng.integers(-26, 27)), cy + int(rng.integers(-18, 19))))
    return sorted(pts, key=lambda p: p[1])


class ChantScene:
    def __init__(self, clock, t0, t1):
        self.c, self.t0, self.t1 = clock, t0, t1
        self.b0 = clock.beat_pos(t0)
        g = world.grass_layer(MAP_W, MAP_H)
        g = world.dirt_path(g, [MINE_DOOR, (110, 156), HALL_DOOR, (200, 150), RALLY, (420, 152), TARGET])
        g = world.water(g, 584, 600)
        rng = np.random.default_rng(11)
        gi = Image.fromarray(g)
        gd = ImageDraw.Draw(gi)
        for _ in range(70):
            x, y = int(rng.integers(0, MAP_W)), int(rng.integers(50, MAP_H))
            if any(bx - 12 < x < bx + 52 and by - 12 < y < by + 48 for _k, bx, by, _d in BUILDS + [("hall", *HALL, 0), ("mine", *MINE, 0)]):
                continue
            if rng.random() < 0.5:
                gd.ellipse([x, y, x + 5, y + 3], fill=(120, 118, 126), outline=(22, 18, 20))
                gd.point((x + 1, y + 1), fill=(170, 168, 176))
            else:
                gd.ellipse([x, y, x + 7, y + 5], fill=(30, 78, 34), outline=(22, 18, 20))
                gd.point((x + 2, y + 1), fill=(70, 136, 58))
        self.ground = gi
        g = np.asarray(gi)
        self.trees = _trees()
        self.workers = [i * 1.6 for i in range(5)]  # phase offsets in beats

    # --- state ---------------------------------------------------------------
    def lb(self, t):
        return self.c.beat_pos(t) - self.b0

    def soldiers(self, b):
        out = []
        for i in range(6):
            born = 12 + i * 0.75
            if b < born:
                continue
            slot = (RALLY[0] + (i % 3) * 14, RALLY[1] - 14 + (i // 3) * 16)
            door = (232, 162)
            if b < 18:
                k = ease((b - born) / 2.0)
                x, y = lerp(door[0], slot[0], k), lerp(door[1], slot[1], k)
                moving = k < 1
            else:
                k = ease((b - 18 - i * 0.15) / 4.0)
                dst = (TARGET[0] - 20 + (i % 3) * 14, TARGET[1] - 14 + (i // 3) * 16)
                x, y = lerp(slot[0], dst[0], k), lerp(slot[1], dst[1], k)
                moving = 0 < k < 1
            out.append((x, y, moving, slot))
        return out

    def gold(self, b):
        trips = sum(max(0, math.floor((b + ph) / 8)) for ph in self.workers)
        return 400 + 10 * trips

    def camera(self, b):
        k = ease((b - 2) / 20.0)
        return int(lerp(10, 236, k)), int(lerp(14, 60, k))

    # --- drawing -------------------------------------------------------------
    def draw_world(self, t, b):
        img = self.ground.copy()
        d = ImageDraw.Draw(img)
        world.draw_goldmine(d, *MINE, glint=int(b * 2))
        world.draw_building(d, "hall", *HALL, BLUE)
        site_workers = []
        for kind, x, y, done in BUILDS:
            if b < done - 4:
                continue
            prog = (b - (done - 4)) / 4.0
            world.draw_building(d, kind, x, y, BLUE, progress=min(prog, 1.0))
            if prog < 1:
                site_workers.append((x - 10, y + 20))
            elif b - done < 0.6:  # dust puff on completion
                r = int(6 + (b - done) * 30)
                d.ellipse([x + 10 - r, y + 30 - r // 2, x + 10 + r, y + 30 + r // 2], outline=(220, 210, 180))
        sprites_on_map = []
        for ph in self.workers:  # gold loop: 4 beats out, 4 beats back
            cyc = (b + ph) % 8
            back = cyc >= 4
            k = ease((cyc - 4 if back else cyc) / 4)
            a, z = (HALL_DOOR, MINE_DOOR) if not back else (MINE_DOOR, HALL_DOOR)
            x, y = lerp(a[0], z[0], k) - 6, lerp(a[1], z[1], k) - 12 + 4 * math.sin(ph * 3)
            sprites_on_map.append(("worker", x, y, (b * 2) % 2 < 1, z[0] < a[0], back))
        for x, y in site_workers:  # builders hammer on the beat
            sprites_on_map.append(("worker", x, y - 2 * self.c.pulse(t), True, False, False))
        sel = []
        for x, y, moving, _ in self.soldiers(b):
            sprites_on_map.append(("soldier", x - 6, y - 12, moving and (b * 2) % 2 < 1, False, False))
            if 16.5 <= b:
                sel.append((x, y))
        sh = int(b / 6) % 3
        sprites_on_map.append(("sheep", 440 + sh * 6, 196 - 2 * (self.c.pulse(t) > 0.6), False, sh == 1, False))
        for x, y in sel:
            d.ellipse([x - 7, y, x + 7, y + 4], outline=hud.GREEN)
        trees = [(x, y) for x, y in self.trees]
        layer = sorted([(y + 14, "s", s) for s in sprites_on_map for y in [s[2]]] +
                       [(y, "t", (x, y)) for x, y in trees], key=lambda e: e[0])
        for _, typ, it in layer:
            if typ == "t":
                world.draw_tree(d, it[0], it[1], sway=1 if self.c.pulse(t) > 0.5 and it[0] % 3 == 0 else 0)
            else:
                name, x, y, alt, flip, carry = it
                if name == "sheep":
                    sprites.blit(img, "SHEEP", x, y, flip=flip)
                    continue
                grid = {"worker": "WORKER_B" if alt else "WORKER_A",
                        "soldier": "SOLDIER_B" if alt else "SOLDIER_A"}[name]
                sprites.blit(img, grid, x, y, flip=flip)
                if carry:
                    sprites.blit(img, "SACK", x + (8 if flip else 0), y + 5)
        if 18 <= b < 19.5:  # move order marker
            r = int(2 + (b - 18) * 6)
            d.line([TARGET[0] - r, TARGET[1] - r, TARGET[0] + r, TARGET[1] + r], fill=hud.GREEN)
            d.line([TARGET[0] - r, TARGET[1] + r, TARGET[0] + r, TARGET[1] - r], fill=hud.GREEN)
        return img

    def fog(self, b):
        """Visibility in [0,1] at map resolution (explored areas stay revealed)."""
        yy, xx = np.mgrid[0:MAP_H, 0:MAP_W].astype(np.float32)
        srcs = [(173, 120, 110 + 40 * ease(b / 8)), (64, 140, 70)]
        for kind, x, y, done in BUILDS:
            if b >= done - 4:
                srcs.append((x + 14, y + 16, 80))
        for x, y, _, slot in self.soldiers(b):
            for s in np.linspace(0, 1, 8):
                srcs.append((lerp(slot[0], x, s), lerp(slot[1], y, s), 60))
        v = np.zeros((MAP_H, MAP_W), np.float32)
        for x, y, r in srcs:
            v = np.maximum(v, np.clip((r - np.hypot(xx - x, yy - y)) / 22, 0, 1))
        return v

    def frame(self, t):
        b = self.lb(t)
        c = self.c
        world_img = self.draw_world(t, b)
        vis = self.fog(b)
        thr = np.tile(BAYER, (MAP_H // 4, MAP_W // 4))
        arr = np.asarray(world_img).copy()
        arr[vis < thr] = (6, 6, 10)
        dim = (vis >= thr) & (vis < 0.55)
        arr[dim] = (arr[dim] * 0.6).astype(np.uint8)
        cx, cy = self.camera(b)
        shake = int(round(2 * c.downpulse(t, 9) * c.nrg(t)))
        view = Image.fromarray(arr[cy:cy + VIEW_H, cx + shake:cx + shake + VIEW_W])

        frame = Image.new("RGB", (hud.W, hud.H))
        frame.paste(view, (0, hud.TOP))
        self.overlay(frame, t, b, cx, cy)

        mini = Image.fromarray(np.where((vis > 0.3)[..., None], np.asarray(self.ground), 8).astype(np.uint8))
        mini = mini.resize(MINI, Image.NEAREST)
        md = ImageDraw.Draw(mini)
        s = MINI[0] / MAP_W
        for kind, x, y, done in [("hall", *HALL, 0)] + BUILDS:
            if b >= done:
                md.rectangle([x * s, y * s, x * s + 4, y * s + 3], fill=(90, 140, 255))
        for x, y, _, _ in self.soldiers(b):
            md.point((x * s, y * s), fill=(160, 200, 255))
        cam = (int(cx * s), int(cy * s), int((cx + VIEW_W) * s), int((cy + VIEW_H) * s))

        line, _ = self.current_chant(b)
        mouth = min(1.0, c.nrg(t) * 2.2) * (0.5 + 0.5 * math.sin(t * 38)) if line else 0
        hot = int(b) % 6 if c.pulse(t) > 0.3 else -1
        food = 5 + len(self.soldiers(b))
        cap = 4 + 4 * sum(1 for k, *_r, done in BUILDS if k == "farm" and b >= done)
        hud.top_bar(frame, self.gold(b), 800 + 5 * int(b), food, max(cap, food), t, "BUILD ORDER")
        hud.bottom_panel(frame, mini, cam, hud.worker_portrait(mouth, int(t * 10) % 37 == 0),
                         "ENSEMBLE:", line.replace("|", " "), hud.DEFAULT_BUTTONS, hot)
        flash = 0.18 * c.downpulse(t, 12) * (1 if any(abs(b - done) < 0.3 for *_r, done in BUILDS) else 0.3)
        return frame, flash

    def current_chant(self, b):
        for s, e, txt, scale in CHANT:
            if s <= b < e:
                return txt, (b - s, scale)
        return "", None

    def overlay(self, frame, t, b, cx, cy):
        d = ImageDraw.Draw(frame)
        # message log (top-left of viewport)
        y = hud.TOP + 3
        for kind, *_r, done in BUILDS:
            if 0 <= b - done < 3:
                draw_text(frame, 4, y, f"CONSTRUCTION COMPLETE: {kind.upper()}", hud.GOLD_TXT)
                y += 9
        if 12 <= b < 15:
            draw_text(frame, 4, y, "UNIT READY", hud.GREEN)
        # drag-select box
        if 15 <= b < 16.5:
            k = ease((b - 15) / 1.2)
            x0, y0 = RALLY[0] - 14 - cx, RALLY[1] - 30 - cy + hud.TOP
            x1, y1 = lerp(x0, x0 + 56, k), lerp(y0, y0 + 40, k)
            d.rectangle([x0, y0, x1, y1], outline=hud.GREEN)
            self.cursor(frame, x1, y1)
        elif 16.5 <= b < 18:
            self.cursor(frame, RALLY[0] + 42 - cx + (b - 16.5) * 60, RALLY[1] + 10 - cy + hud.TOP)
        else:
            sites = [(x + 14, y + 10) for _k, x, y, done in BUILDS if done - 4 <= b < done] or [(HALL[0] + 30, HALL[1] + 20)]
            sx, sy = sites[0]
            self.cursor(frame, sx - cx + 3 * math.sin(t * 2), sy - cy + hud.TOP + 2 * math.cos(t * 3))
        # kinetic chant text
        txt, info = self.current_chant(b)
        if txt:
            age, scale = info
            pop = max(0, 1 - age * 3)
            col = (255, 255, 255) if pop > 0.3 else (246, 206, 62)
            lines = txt.split("|")
            total_h = len(lines) * 9 * scale
            for i, ln in enumerate(lines):
                x = (hud.W - text_width(ln, scale)) // 2
                y = hud.TOP + 40 - total_h // 2 + i * 9 * scale - int(pop * 6)
                draw_text(frame, x, y, ln, col, scale=scale, shadow=(20, 14, 10), outline=True)

    @staticmethod
    def cursor(frame, x, y):
        d = ImageDraw.Draw(frame)
        x, y = int(x), int(y)
        d.polygon([(x, y), (x, y + 9), (x + 3, y + 6), (x + 6, y + 9), (x + 7, y + 8), (x + 4, y + 5), (x + 7, y + 4)],
                  fill=(246, 206, 62), outline=(22, 18, 20))
