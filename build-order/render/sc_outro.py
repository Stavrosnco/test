"""Outro: call and response on black, GG, PLAY AGAIN?, CRT power-off."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine, hud
from clock import ease, lerp
from font import draw_text, text_width

W, H = hud.W, hud.H


class Outro:
    def __init__(self, ctx, sec):
        self.ctx, self.c, self.tl, self.sec = ctx, ctx.clock, ctx.timeline, sec
        s = self.tl.sec(sec)
        self.t0, self.t1 = s["start"], s["end"]
        self.lines = s["lines"]
        self.t_gg = self.lines[-1]["start"]
        self.t_title = self.t_gg + 1.2
        self.t_play = self.t1 - 3.4
        self.t_click = self.t1 - 1.6
        self.t_off = self.t1 - 0.9

    def frame(self, t):
        img = Image.new("RGB", (W, H), (6, 6, 12))
        d = ImageDraw.Draw(img)
        engine.stars(img, t, n=40)
        if t < self.t_gg:
            shown = [l for l in self.lines[:-1] if l["start"] - 0.05 <= t]
            for i, l in enumerate(shown[-6:]):
                call = not l["text"].startswith("(")
                txt = l["text"].strip("()")
                age = t - l["start"]
                y = 30 + i * 26
                s = 2
                x = 40 if call else W - 40 - text_width(txt, s)
                col = (236, 236, 236) if call else (246, 206, 62)
                if i == len(shown[-6:]) - 1 and age < 0.15:
                    col = (255, 255, 255)
                draw_text(img, x, y, txt.upper(), col, scale=s, outline=True)
                tag = "PLAYER 1:" if call else "ALL:"
                draw_text(img, x if call else W - 40 - text_width(tag), y - 9, tag, (120, 120, 140), shadow=None)
        elif t < self.t_title:
            engine.big_text(img, "GG", t - self.t_gg, scale=10, y=100, col=(140, 200, 255))
        elif t < self.t_play:
            engine.big_text(img, "ONE MORE GAME", t - self.t_title, scale=4, y=96)
        else:
            engine.big_text(img, "PLAY AGAIN?", 99, scale=3, y=80, col=(236, 236, 236))
            yes_lit = t >= self.t_click
            for i, (lab, x) in enumerate((("YES", 120), ("NO", 230))):
                lit = yes_lit and i == 0
                d.rectangle([x, 110, x + 50, 132], fill=(60, 120, 60) if lit else (40, 40, 52), outline=(180, 220, 160) if lit else (110, 110, 130))
                draw_text(img, x + 25 - text_width(lab, 2) // 2, 115, lab, (255, 255, 255), scale=2)
            k = ease((t - self.t_play) / (self.t_click - self.t_play))
            engine.cursor(img, lerp(300, 150, k), lerp(170, 124, k))
        if t >= self.t_off:  # CRT power-off: collapse to a line, then a dot
            k = (t - self.t_off) / (self.t1 - self.t_off)
            a = np.asarray(img).copy()
            if k < 0.5:
                hh = int(H / 2 * (1 - k * 2)) + 1
                out = np.zeros_like(a)
                out[H // 2 - hh:H // 2 + hh] = a[H // 2 - hh:H // 2 + hh]
                out[H // 2 - 1:H // 2 + 1] = 255
            else:
                ww = int(W / 2 * (1 - (k - 0.5) * 2)) + 1
                out = np.zeros_like(a)
                out[H // 2 - 1:H // 2 + 1, W // 2 - ww:W // 2 + ww] = 255
            img = Image.fromarray(out)
        return img, 0.0
