"""Verse 3: industrial war over glowing green crystals; FMV briefings; time-warp into Tesla coils."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine, hud, units, world
from clock import ease, lerp
from font import draw_text, text_width

GOLD, RED = "gold", "red"
_r = np.random.default_rng(12)
CRYST = sorted({(int(270 + 64 * math.cos(a) * r), int(166 + 40 * math.sin(a) * r))
                for a, r in zip(_r.uniform(0, 6.28, 34), np.sqrt(_r.uniform(0, 1, 34)))}, key=lambda p: p[1])


class Verse3(engine.MapScene):
    theme, title, speaker = "cnc", "TIBERIUM 1995", "Commander"
    use_fog = False

    def __init__(self, ctx, sec):
        super().__init__(ctx, sec)
        tl = self.tl
        w = lambda i, k: tl.word_t(sec, i, k)
        self.L = [l["start"] for l in tl.sec(sec)["lines"]] + [tl.sec(sec)["end"]]
        self.t_hammer, self.t_bald, self.t_tib = w(1, "hammer"), w(2, "bald"), w(2, "Tiberium")
        self.t_peace = w(3, "Peace")
        self.t_ion = w(4, "ion")
        self.t_cash = w(5, "cash")
        self.t_eng, self.t_mine, self.t_fire = w(7, "engineer"), w(8, "mine"), w(8, "firing")
        self.t_ready, self.t_lost = w(9, "Unit"), tl.line(sec, 9)["words"][2]["s"]
        self.t_ra, self.t_tesla = w(10, "Red"), w(10, "Tesla")
        rng = np.random.default_rng(31)
        self.noise = [rng.integers(0, 255, (134, 224), dtype=np.uint8) for _ in range(6)]

    def build_ground(self):
        rng = np.random.default_rng(8)
        h, w = self.MAP_H, self.MAP_W
        base = np.array([[118, 104, 82], [108, 96, 76], [128, 114, 90], [96, 86, 68]], np.uint8)
        idx = rng.integers(0, 3, (h // 2 + 1, w // 2 + 1))
        idx = np.repeat(np.repeat(idx, 2, 0), 2, 1)[:h, :w]
        g = base[idx]
        g = world.dirt_path(g, [(60, 200), (200, 190), (420, 190), (600, 200)], width=8, seed=5)
        yy, xx = np.mgrid[0:h, 0:w]
        field = ((xx - 270) / 70) ** 2 + ((yy - 166) / 46) ** 2 < 1
        g[field & (rng.random((h, w)) > 0.6)] = (70, 120, 60)
        for x0, y0, x1, y1 in [(10, 60, 150, 150), (470, 50, 630, 150)]:  # concrete pads
            g[y0:y1, x0:x1] = (140, 138, 132)
            g[y0:y1:12, x0:x1] = (120, 118, 112)
            g[y0:y1, x0:x1:12] = (120, 118, 112)
        return g

    def obelisk_team(self, t):
        return GOLD if t >= self.t_mine else RED

    def draw_actors(self, img, d, t):
        b = self.c.beat_pos(t)
        glow = 0.5 + 0.5 * math.sin(t * 5)
        drop = ease((t - self.t0 + 0.2) / 0.5)
        units.concrete_building(d, 20, 70, 44, 32, GOLD, "yard")
        if self.t0 - 0.2 <= t:
            units.concrete_building(d, 76, int(lerp(40, 70, drop)), 40, 30, GOLD, "refinery")
        units.concrete_building(d, 20, 112, 30, 26, GOLD, "power", light=True)
        units.concrete_building(d, 540, 64, 44, 32, RED, "yard")
        units.concrete_building(d, 590, 108, 30, 26, RED, "power", light=t < self.t_tesla)
        cap = t >= self.t_mine
        units.concrete_building(d, 480, 100, 40, 30, GOLD if cap else RED, "refinery")
        items = []
        for i, (x, y) in enumerate(CRYST):
            items.append((y, lambda x=x, y=y, i=i: units.crystals(d, x, y, glow=(glow if i % 2 else 1 - glow) * (1.5 if self.L[2] <= t < self.L[3] else 1))))
        # harvester loop through the field and back to the refinery
        k = (t - self.t0) / 6.0 % 1.0
        hx, hy = (lerp(110, 300, ease(k * 2)), lerp(110, 176, ease(k * 2))) if k < 0.5 else (lerp(300, 110, ease(k * 2 - 1)), lerp(176, 110, ease(k * 2 - 1)))
        items.append((hy, lambda: units.harvester(d, hx, hy, team=GOLD, f=1 if k < 0.5 else -1, load=k * 2 if k < 0.5 else 1)))
        # mammoth tanks
        mk = ease((t - self.L[6] + 0.3) / 2.6)
        for j in range(2):
            mx, my = lerp(120, 360, mk) - j * 40, 214 + j * 14
            items.append((my, lambda mx=mx, my=my: units.tank(d, mx, my, team=GOLD, big=True)))
        for i, sx in enumerate(range(200, 340, 22)):  # sandbags get crushed
            if mk * 240 + 120 < sx - 10 or t < self.L[6]:
                items.append((214, lambda sx=sx: d.rectangle([sx, 212, sx + 10, 218], fill=(170, 150, 100), outline=engine.K)))
        # obelisk
        ob = (500, 176)
        charge = 0.0
        if t >= self.t_fire - 0.4:
            charge = ease((t - self.t_fire + 0.4) / 0.4)
        items.append((ob[1], lambda: units.obelisk(d, *ob, team=self.obelisk_team(t), charge=charge)))
        # enemy tank target for the obelisk / unit lost
        if t < self.t_fire + 0.2:
            items.append((200, lambda: units.tank(d, 580, 200, team=RED, f=-1)))
        elif t < self.t_fire + 0.9:
            items.append((300, lambda: units.explosion(d, 580, 192, (t - self.t_fire - 0.2) / 0.7)))
        if self.t_fire <= t < self.t_fire + 0.35:
            items.append((301, lambda: (d.line([ob[0], ob[1] - 52, 580, 194], fill=(255, 80, 60), width=3),
                                        d.line([ob[0], ob[1] - 52, 580, 194], fill=(255, 230, 200), width=1))))
        # engineer sneaking
        if self.t_eng - 0.2 <= t < self.t_mine:
            ek = ease((t - self.t_eng) / (self.t_mine - self.t_eng))
            ex, ey = lerp(360, 496, ek), lerp(150, 132, ek)
            items.append((ey, lambda: units.infantry(d, ex, ey, team=GOLD, step=int(b * 4) % 2, hat=(246, 206, 62))))
        # unit ready / unit lost
        if self.t_ready <= t < self.t_lost:
            items.append((150, lambda: units.tank(d, 160, 150, team=GOLD)))
        elif self.t_lost <= t < self.t_lost + 0.8:
            items.append((302, lambda: units.explosion(d, 160, 144, (t - self.t_lost) / 0.8)))
        # tesla coil
        tc = (440, 214)
        if t >= self.t_ra:
            items.append((tc[1], lambda: units.tesla_coil(d, *tc, team=RED, charge=1.0 if t >= self.t_tesla else 0.0)))
            if t >= self.t_tesla:
                items.append((303, lambda: units.bolt(d, tc[0], tc[1] - 36, 360, 214, int(t * 20))))
        for _, fn in sorted(items, key=lambda e: e[0]):
            fn()
        if self.t_ion <= t < self.t_ion + 1.0:
            k = (t - self.t_ion) / 1.0
            x, y = 560, 90
            wbeam = int(6 * (1 - k)) + 1
            d.rectangle([x - wbeam, 0, x + wbeam, y], fill=(200, 230, 255))
            d.rectangle([x - max(1, wbeam // 2), 0, x + max(1, wbeam // 2), y], fill=(255, 255, 255))
            r = int(10 + 60 * k)
            d.ellipse([x - r, y - r // 2, x + r, y + r // 2], outline=(160, 210, 255), width=2)

    def camera(self, t):
        L = self.L
        return engine.shot_cam(t, [(self.t0, (0, 30)), (self.t_tib - 0.1, (110, 70)), (L[4], (300, 20)),
                                   (L[5], (40, 60)), (L[6], (60, 90)), (L[7], (200, 40)), (L[8], (230, 60)),
                                   (L[9], (20, 50)), (self.t_ra, (180, 90))], trans=0.5)

    def resources(self, t):
        cash = 2400 + int((t - self.t0) * 40)
        if t >= self.t_cash - 1.5:
            cash += int(ease((t - self.t_cash + 1.5) / 2.0) * 3000)
        return (cash, "OK" if t < self.t_tesla else "LOW", "12")

    def minimap_dots(self, t):
        return [(40, 85, (246, 206, 62), True), (560, 80, (240, 80, 60), True), (500, 115, (246, 206, 62) if t >= self.t_mine else (240, 80, 60), True)]

    def fmv(self, frame, t, who):
        """Grainy 'live action' transmission window over the viewport."""
        d = ImageDraw.Draw(frame)
        pl = engine.plate("fmv_general" if who == "general" else "fmv_bald")
        w, h = (224, 134) if pl else (200, 120)
        x0, y0 = (hud.W - w) // 2, hud.TOP + 14
        d.rectangle([x0 - 4, y0 - 12, x0 + w + 3, y0 + h + 3], fill=(20, 22, 20), outline=(90, 200, 90))
        draw_text(frame, x0, y0 - 10, "INCOMING TRANSMISSION", (120, 230, 120), shadow=None)
        if pl:
            st = self.L[1] if who == "general" else self.t_bald
            en = self.t_bald if who == "general" else self.t_tib
            k = ease((t - st) / max(0.1, en - st))
            ox = 11 + int(round(3 * math.sin(t * 0.7)))
            oy = int(round(lerp(14, 2, k)))
            v = pl.crop((ox, oy, ox + w, oy + h))
        else:
            v = self._fmv_drawn(t, who, w, h)
        a = np.asarray(v).astype(np.int16)
        n = np.resize(self.noise[int(t * 24) % 6], (h, w)).astype(np.int16)
        a = a + ((n[..., None] - 128) * (0.09 if pl else 0.18)).astype(np.int16)
        a[::2] = a[::2] * 0.8
        j = int(t * 24) % 5
        a[j * 20:j * 20 + 3] = np.roll(a[j * 20:j * 20 + 3], 6, axis=1)
        if int(t * 24) % 37 < 2:  # occasional tape tracking roll
            ry = int(t * 300) % h
            a[ry:ry + 4] = np.clip(a[ry:ry + 4] + 70, 0, 255)
        frame.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)), (x0, y0))

    def _fmv_drawn(self, t, who, w, h):
        v = Image.new("RGB", (w, h), (30, 40, 34))
        vd = ImageDraw.Draw(v)
        if who == "general":
            vd.rectangle([0, 0, w, h], fill=(50, 62, 52))
            vd.ellipse([70, 30, 130, 96], fill=(220, 176, 140), outline=engine.K)
            vd.polygon([(40, 120), (60, 92), (140, 92), (160, 120)], fill=(70, 90, 60), outline=engine.K)
        else:
            vd.rectangle([0, 0, w, h], fill=(26, 10, 12))
            vd.ellipse([72, 22, 128, 92], fill=(210, 160, 130), outline=engine.K)
            vd.polygon([(30, 120), (64, 94), (136, 94), (170, 120)], fill=(20, 18, 22), outline=engine.K)
        return v

    def overlay(self, frame, t, cam):
        if self.footage:
            return
        L = self.L
        if t < self.t0 + 1.4:
            engine.big_text(frame, "CONSTRUCTION COMPLETE", t - self.t0, scale=2, y=hud.TOP + 30, col=(90, 230, 90))
        if L[1] <= t < self.t_tib:
            self.fmv(frame, t, "general" if t < self.t_bald else "bald")
            if self.t_hammer <= t < self.t_hammer + 0.6:
                engine.big_text(frame, "LIVE ACTION!", t - self.t_hammer, scale=2, y=hud.TOP + 136)
        if self.t_peace <= t < L[4]:
            engine.big_text(frame, "PEACE THROUGH|POWER!", t - self.t_peace, scale=3, y=hud.TOP + 60, col=(240, 60, 50))
        if self.t_ion <= t < self.t_ion + 1.2:
            engine.big_text(frame, "ION CANNON", t - self.t_ion, scale=3, y=hud.TOP + 30, col=(170, 220, 255))
        if self.t_cash <= t < self.t_cash + 1.0:
            engine.big_text(frame, "KA-CHING!", t - self.t_cash, scale=3, y=hud.TOP + 30)
        if self.t_ready <= t < self.t_lost:
            draw_text(frame, 4, hud.TOP + 3, "UNIT READY", (90, 230, 90))
        if self.t_lost <= t < L[10]:
            draw_text(frame, 4, hud.TOP + 3, "UNIT LOST", (240, 80, 60))

    def postfx(self, frame, t):
        a = np.asarray(frame).astype(np.float32)
        vh = slice(hud.TOP, hud.BOT)
        changed = False
        if self.L[3] <= t < self.L[4]:
            a[vh] = a[vh] * np.array([1.15, 0.6, 0.55]); changed = True
        if self.L[7] <= t < self.t_fire:
            a[vh] = a[vh] * np.array([0.45, 0.5, 0.85]); changed = True
        if t >= self.t_ra:
            k = ease((t - self.t_ra) / 0.6)
            a[vh] = a[vh] * np.array([1.0 + 0.2 * k, 1.0 - 0.35 * k, 1.0 - 0.35 * k]); changed = True
            if t < self.t_ra + 0.8:  # time-warp slice glitch
                rng = np.random.default_rng(int(t * 30))
                for _ in range(8):
                    y = int(rng.integers(hud.TOP, hud.BOT - 6))
                    a[y:y + 5] = np.roll(a[y:y + 5], int(rng.integers(-30, 30)), axis=1)
        if changed:
            frame.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
        if self.t_ion <= t < self.t_ion + 0.12 or self.t_fire <= t < self.t_fire + 0.08:
            return 0.35
        return 0.0

    def portrait(self, t, singing):
        if self.cur_speaker == "EVA":
            return engine.eva_portrait(t, singing, self.c)
        return engine.portrait(shirt=(80, 100, 60), helmet=(80, 100, 60), bg=(20, 40, 24),
                               mouth=engine.mouth_amt(self.c, t, singing), blink=int(t * 10) % 31 == 0)
