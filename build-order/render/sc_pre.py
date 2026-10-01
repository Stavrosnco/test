"""Pre-chorus: nothing on the map but a town hall, a worker and a clock that won't stop."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine, hud, sprites, world
from clock import ease, lerp
from font import draw_text, text_width

BLUE = (sprites.TEAMS["blue"]["T"], sprites.TEAMS["blue"]["t"])


class PreChorus(engine.MapScene):
    theme, title, speaker = "medieval", "NEW GAME", "Ensemble"

    def __init__(self, ctx, sec, lift=None):
        super().__init__(ctx, sec)
        self.t_clock = self.tl.word_t(sec, 1, "clock") if lift is None else 1e9
        self.lift = lift  # (t_start, t_end): fog lifts completely (used by the chorus)

    def build_ground(self):
        g = world.grass_layer(self.MAP_W, self.MAP_H, seed=9)
        return world.dirt_path(g, [(300, 150), (360, 140), (420, 150)], width=5)

    def camera(self, t):
        return 128, 50

    def draw_actors(self, img, d, t):
        world.draw_building(d, "hall", 296, 104, BLUE)
        b = self.c.beat_pos(t)
        k = (b % 8) / 8
        x = 330 + 30 * math.sin(k * 2 * math.pi)
        sprites.blit(img, "WORKER_B" if (b * 2) % 2 < 1 else "WORKER_A", x, 150, flip=math.cos(k * 2 * math.pi) < 0)
        rng = np.random.default_rng(2)
        for _ in range(40):
            world.draw_tree(d, int(rng.integers(0, self.MAP_W)), int(rng.integers(40, self.MAP_H)))

    def fog_sources(self, t):
        r = 62 + 6 * self.c.pulse(t)
        if self.lift:
            r += 500 * ease((t - self.lift[0]) / (self.lift[1] - self.lift[0]))
        return [(320, 130, r)]

    def resources(self, t):
        return (50, 0, "1/4")

    def minimap_dots(self, t):
        return [(320, 130, (90, 140, 255), True)]

    def overlay(self, frame, t, cam):
        if t >= self.t_clock:
            el = (t - self.t_clock) * 37
            m, s = divmod(int(el), 60)
            txt = f"{m:02d}:{s:02d}"
            engine.big_text(frame, txt, t - self.t_clock, scale=5, y=hud.TOP + 30, col=(236, 236, 236))
