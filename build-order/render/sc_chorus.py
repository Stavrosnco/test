"""Chorus: 'One more game!' in the bedroom, with game cuts on the screen."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine, hud, bedroom
from clock import ease, lerp
from font import draw_text, text_width

VARIANTS = {
    4: dict(dawn=(0.0, 0.35), clock=(3.1, 4.6), mom="IT'S 3 AM!!"),
    8: dict(dawn=(0.5, 0.75), clock=(5.6, 6.4), mom="SCHOOL BUS!!"),
    11: dict(dawn=(0.85, 1.0), clock=(11.5, 12.2), mom="IT'S NOON!!"),
}


class Chorus:
    def __init__(self, ctx, sec):
        self.ctx, self.c, self.tl, self.sec = ctx, ctx.clock, ctx.timeline, sec
        self.v = VARIANTS[sec]
        self.room = bedroom.Bedroom()
        s = self.tl.sec(sec)
        self.t0, self.t1 = s["start"], s["end"]
        self.L = [l["start"] for l in s["lines"]] + [s["end"]]
        w = lambda i, k: self.tl.word_t(sec, i, k)
        self.t_mom = w(1, "Mom")
        self.cuts = [(w(2, "Rush"), "RUSH 'EM!"), (w(2, "tower"), "TOWER!"), (w(2, "turtle"), "TURTLE!"), (w(2, "tech"), "TECH IT LATE!")]
        if len(s["lines"]) > 6:
            self.t_map, self.t_mouse = w(7, "map"), w(7, "mouse")
            self.t_fog = self.L[6]

    def game(self, t, lyric_t=None):
        return self.ctx.scenes["chant"].frame(t, lyric_t=lyric_t)[0]

    def fog_game(self, t):
        sc = self.ctx.scenes["fog_lift"]
        sc.lift = (self.L[6], self.L[7])
        return sc.frame(t)[0]

    def screen_for(self, t):
        ch = self.ctx.scenes["chant"]
        if self.L[3] <= t < self.L[4] or (len(self.L) <= 6 and t >= self.L[3]):
            img = Image.new("RGB", (hud.W, hud.H), (10, 10, 30))
            word = "VICTORY!" if (t - self.L[3]) < 1.2 else "PLAY AGAIN?"
            engine.big_text(img, word, t - self.L[3], scale=5, y=100)
            return img
        return self.game(ch.t0 + 2 + (t * 0.7) % 10, lyric_t=t)

    def frame(self, t):
        L, v = self.L, self.v
        k = (t - self.t0) / (self.t1 - self.t0)
        dawn = lerp(*v["dawn"], k)
        clock_h = lerp(*v["clock"], k)
        line, _ = self.tl.line_at(t, sec=self.sec)
        idx = line["idx"] if line else 0
        # full-screen game cuts
        if L[2] <= t < L[3]:
            for i, (st, word) in enumerate(self.cuts):
                nxt = self.cuts[i + 1][0] if i + 1 < len(self.cuts) else L[3]
                if st <= t < nxt or (i == 0 and t < st):
                    ch = self.ctx.scenes["chant"]
                    src = [ch.t_order + 1.5, ch.builds[3][3] + 0.5, ch.t0 + 1.0, ch.t1 - 0.3][i]
                    img = self.game(src + (t - st) * 0.5, lyric_t=t)
                    engine.big_text(img, word, t - st, scale=4, y=hud.TOP + 70)
                    return img, 0.12 if t - st < 0.06 else 0.0
        if len(L) > 7 and L[6] <= t < L[7]:
            img = self.fog_game(t)
            engine.kinetic(img, self.tl, t, self.sec, scale=2, y=hud.TOP + 30)
            return img, 0.0
        door = ease((t - self.t_mom) / 0.4) if self.t_mom <= t < L[2] else 0.0
        cheer = 0.0
        for st, _txt in (engine.chunks(line) if line else []):
            if _txt.upper().startswith(("ONE", "(ONE", "\"ONE")) and st <= t:
                cheer = max(0.0, 1 - (t - st) * 1.4)
        room = self.room.draw(t, dawn=dawn, clock_h=clock_h, door=door, mom=v["mom"] if door > 0 else None,
                              screen=self.screen_for(t), kid_bob=self.c.pulse(t), cheer=cheer)
        img = room
        if len(L) > 7 and L[7] <= t:
            if t < self.t_mouse:
                img = bedroom.push(room, self.game(self.ctx.scenes['chant'].t1 - 0.5, lyric_t=t), 3.2)
            elif t < self.t_mouse + 0.9:
                img = bedroom.zoom(room, 268, 140, 3.0)
        engine.kinetic(img, self.tl, t, self.sec, scale=3, y=22, sub=True)
        return img, 0.1 * self.c.downpulse(t, 10)
