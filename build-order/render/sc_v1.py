"""Verse 1: the kid's setup (bedroom callouts), then a Dune-style desert map."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine, hud, bedroom, units, world
from clock import ease, lerp
from font import draw_text

BLUE = "blue"


class DesertScene(engine.MapScene):
    theme, title, speaker = "desert", "DESERT 1992", "Player 1"

    def __init__(self, ctx, sec):
        super().__init__(ctx, sec)
        tl = self.tl
        w = lambda i, k: tl.word_t(sec, i, k)
        self.t_batt, self.t_move = w(3, "battalion"), w(3, "moves")
        self.t_worm, self.t_ate, self.t_q = w(5, "sandworm"), w(5, "ate"), w(5, "understand")
        self.t_feed, self.t_mine, self.t_build = tl.line_t(sec, 6), w(7, "mine"), w(7, "build")
        self.L = [l["start"] for l in tl.sec(sec)["lines"]]
        self.tanks0 = [(184 + (i % 3) * 18, 100 + (i // 3) * 16) for i in range(6)]
        self.worm_at = (430, 176)

    def build_ground(self):
        g = world.sand_layer(self.MAP_W, self.MAP_H)
        g = world.rock_plateau(g, 110, 130, 108, 84)
        g = world.spice_field(g, 390, 100, 90, 46, seed=3)
        g = world.spice_field(g, 540, 196, 80, 40, seed=4)
        return g

    def tank_pos(self, i, t):
        x0, y0 = self.tanks0[i]
        dst = (330 + (i % 3) * 18, 120 + (i // 3) * 16)
        if i == 5:
            dst = (self.worm_at[0], self.worm_at[1] - 2)
        k = ease((t - self.t_move - i * 0.05) / (3.4 if i == 5 else 2.4))
        return lerp(x0, dst[0], k), lerp(y0, dst[1], k), 0 < k < 1

    def harvester_pos(self, j, t):
        if j == 0 and t >= self.t_mine - 1.6:
            k = ease((t - (self.t_mine - 1.6)) / 1.6)
            return lerp(360, 120, k), lerp(110, 176, k), -1
        cx, cy = [(390, 100), (540, 196)][j]
        a = t * 0.5 + j * 2
        return cx + 50 * math.cos(a), cy + 18 * math.sin(a), 1 if math.sin(a) < 0 else -1

    def credits(self, t):
        if t < self.t_feed:
            return 1200 + int((t - self.t0) * 20)
        if t < self.t_mine:
            return 0
        return min(700, int((t - self.t_mine) * 900))

    def resources(self, t):
        units_n = 6 - (1 if t > self.t_ate + 0.6 else 0) + 2
        return (self.credits(t), "OK", f"{units_n}")

    def draw_actors(self, img, d, t):
        units.concrete_building(d, 30, 80, 40, 30, BLUE, "yard")
        units.concrete_building(d, 96, 150, 44, 30, BLUE, "refinery")
        units.concrete_building(d, 40, 150, 28, 24, BLUE, "power", light=True)
        units.concrete_building(d, 150, 74, 28, 24, BLUE, "power", light=True)
        if t >= self.t_build:
            k = t - self.t_build
            if k < 0.5:
                for gx in range(4):
                    for gy in range(3):
                        d.rectangle([188 + gx * 8, 170 + gy * 8, 195 + gx * 8, 177 + gy * 8], outline=(255, 255, 255) if int(k * 12) % 2 else (90, 230, 90))
            else:
                units.concrete_building(d, 188, 170, 30, 22, BLUE, "power", light=True)
        items = []
        for j in range(2):
            x, y, f = self.harvester_pos(j, t)
            items.append((y, lambda x=x, y=y, f=f: units.harvester(d, x, y, team="blue", f=f, load=0.7, glow=(230, 120, 40))))
        for i in range(6):
            x, y, mv = self.tank_pos(i, t)
            if i == 5 and t > self.t_ate + 0.5:
                continue
            items.append((y, lambda x=x, y=y, mv=mv: units.tank(d, x, y, team="blue")))
            if self.t_batt + 0.4 <= t < self.t_worm:
                d.ellipse([x - 12, y - 2, x + 12, y + 3], outline=hud.GREEN)
        for _, fn in sorted(items, key=lambda e: e[0]):
            fn()
        if self.t_worm <= t < self.t_ate:  # ripple approaching
            k = (t - self.t_worm) / max(0.1, self.t_ate - self.t_worm)
            wx = lerp(560, self.worm_at[0], k)
            for i in range(4):
                d.arc([wx - 10 - i * 6, self.worm_at[1] - 4 - i * 2, wx + 10 - i * 6, self.worm_at[1] + 4 + i * 2], 200, 340, fill=(170, 120, 64))
        units.sandworm(d, self.worm_at[0], self.worm_at[1] + 4, (t - self.t_ate) / 1.8)
        if self.t_mine <= t < self.t_mine + 1.5:
            k = t - self.t_mine
            for i in range(3):
                draw_text(img, 112 + i * 8, int(150 - k * 24 - i * 4), "$", (246, 206, 62))

    def fog_sources(self, t):
        srcs = [(110, 130, 160)]
        for i in range(6):
            x, y, _ = self.tank_pos(i, t)
            x0, y0 = self.tanks0[i]
            for s in np.linspace(0, 1, 5):
                srcs.append((lerp(x0, x, s), lerp(y0, y, s), 70))
        for j in range(2):
            x, y, _ = self.harvester_pos(j, t)
            srcs.append((x, y, 70))
        srcs.append((self.worm_at[0], self.worm_at[1], 60 if t > self.t_move + 1 else 0))
        return srcs

    def camera(self, t):
        L = self.L
        return engine.shot_cam(t, [(self.t_batt, (60, 40)), (self.t_move + 0.4, (180, 50)), (L[4], (230, 30)),
                                   (self.t_worm - 0.3, (250, 90)), (L[6], (120, 50)), (self.t_mine - 1.0, (0, 60))], trans=0.8)

    def minimap_dots(self, t):
        dots = [(50, 95, (90, 140, 255), True), (118, 165, (90, 140, 255), True)]
        dots += [(*self.tank_pos(i, t)[:2], (160, 200, 255), False) for i in range(6)]
        dots += [(*self.harvester_pos(j, t)[:2], (255, 220, 120), False) for j in range(2)]
        return dots

    def overlay(self, frame, t, cam):
        cx, cy = cam
        d = ImageDraw.Draw(frame)
        if self.t_batt <= t < self.t_batt + 0.5:
            k = ease((t - self.t_batt) / 0.4)
            x0, y0 = 176 - cx, 86 - cy + hud.TOP
            d.rectangle([x0, y0, x0 + 60 * k, y0 + 44 * k], outline=hud.GREEN)
            engine.cursor(frame, x0 + 60 * k, y0 + 44 * k)
        elif self.t_batt + 0.5 <= t < self.t_move + 1.0:
            engine.cursor(frame, 340 - cx, 130 - cy + hud.TOP)
            if t >= self.t_move:
                d.line([336 - cx, 126 - cy + hud.TOP, 346 - cx, 136 - cy + hud.TOP], fill=hud.GREEN)
                d.line([336 - cx, 136 - cy + hud.TOP, 346 - cx, 126 - cy + hud.TOP], fill=hud.GREEN)
        if self.t_ate + 0.5 <= t < self.t_ate + 2.2:
            draw_text(frame, 4, hud.TOP + 3, "UNIT LOST", (240, 80, 60))
        if t >= self.t_q and t < self.t_feed:
            engine.big_text(frame, "?", t - self.t_q, scale=5, y=self.worm_at[1] - cy + hud.TOP - 40)
        if self.t_feed <= t < self.t_mine and int(t * 4) % 2 == 0:
            draw_text(frame, 4, hud.TOP + 3, "INSUFFICIENT FUNDS", (240, 80, 60))
        if self.t_build <= t < self.t_build + 1.6:
            draw_text(frame, 4, hud.TOP + 3, "CONSTRUCTION COMPLETE", hud.GOLD_TXT)

    def portrait(self, t, singing):
        return engine.portrait(shirt=(58, 104, 214), mouth=engine.mouth_amt(self.c, t, singing),
                               blink=int(t * 10) % 41 == 0, bg=(90, 60, 30))


class Verse1:
    def __init__(self, ctx, sec=2):
        self.c, self.tl, self.sec = ctx.clock, ctx.timeline, sec
        self.room = bedroom.Bedroom()
        self.desert = DesertScene(ctx, sec)
        w = lambda i, k: self.tl.word_t(sec, i, k)
        self.labels = [(w(0, "Pentium"), (282, 52, "PENTIUM 75")), (w(0, "beige"), (284, 106, "BEIGE!")),
                       (w(0, "modem"), (238, 50, "28.8K"))]
        self.t_scream = w(0, "screamin")
        self.L = [l["start"] for l in self.tl.sec(sec)["lines"]]
        self.t_mouse, self.t_click = w(2, "mouse"), w(3, "click")
        self.cut = self.desert.t_batt

    def screen(self, t):
        f, _ = self.desert.frame(max(t, self.desert.t_batt - 0.01) if t >= self.t_click else self.desert.t0 + 0.01)
        return f

    def frame(self, t):
        if t >= self.cut:
            return self.desert.frame(t)
        L = self.L
        labels = [lab for st, lab in self.labels if t >= st] if t < L[1] else []
        clock_h = 2.9 + (t - L[0]) / 60
        if L[1] <= t < L[2]:
            labels = [(108, 84, "3:00 AM")]
        if L[2] <= t:
            labels = [(146, 104, "DISK 7 OF 12")] + ([(250, 124, "BALL INSIDE")] if t >= self.t_mouse else [])
        scr = self.desert.ground.crop((0, 40, 384, 256)).resize((64, 42), Image.NEAREST)
        room = self.room.draw(t, dawn=0.0, clock_h=clock_h, screen=scr, kid_bob=self.c.pulse(t), labels=labels)
        if t < L[0] + 0.01 or t < L[1]:
            img = room
            if self.t_scream <= t < L[1]:
                draw_text(img, 250, 40 + int(2 * math.sin(t * 30)), "SKREEE~", (250, 120, 120), outline=True)
        elif t < L[2]:
            img = bedroom.zoom(room, 190, 108, 1 + 0.7 * ease((t - L[1]) / 0.6))
        elif t < self.t_click:
            tgt = (169, 126) if t < self.t_mouse else (262, 138)
            img = bedroom.zoom(room, *tgt, 2.2)
        else:
            content, _ = self.desert.frame(self.cut)
            img = bedroom.push(room, content, 1 + 5.0 * ease((t - self.t_click) / max(0.2, self.cut - self.t_click)))
            return img, 0.0
        engine.sub_line(img, self.tl, t, sec=self.sec)
        return img, 0.0
