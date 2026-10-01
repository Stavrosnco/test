"""Verse 5: three races in space, rushes, cheats of fate, stadiums, a nuke and GG."""
import math
import numpy as np
from PIL import Image, ImageDraw
import engine, hud, sprites, units, world
from clock import ease, lerp
from font import draw_text, text_width

TERRAN, ZERG, PROTOSS = (60, 150), (560, 140), (330, 70)
NUKE_AT = (110, 170)
LADDER = ["XXSLAYERXX", "PYLONPAPA", "ZERGMOM", "OVERMIND99", "SCV_SAM", "GHOSTFACE", "MARINE_4_LIFE", "CARRIERHAS"]


class Verse5(engine.MapScene):
    MAP_W, MAP_H = 768, 256
    theme, title, speaker = "sc", "1998", "Player 1"
    use_fog = False

    def __init__(self, ctx, sec):
        super().__init__(ctx, sec)
        tl = self.tl
        w = lambda i, k: tl.word_t(sec, i, k)
        self.L = [l["start"] for l in tl.sec(sec)["lines"]] + [tl.sec(sec)["end"]]
        self.t_98 = w(0, "Ninety")
        self.t_races = [w(1, "Terran"), w(1, "Zerg"), w(1, "Protoss")]
        self.t_scv, self.t_ling = w(2, "SCV"), w(2, "Zerglings")
        self.t_pylon, self.t_hush = w(3, "Pylon"), w(3, "hush")
        self.t_min, self.t_gas = w(4, "Not"), w(4, "Insufficient")
        self.t_seoul, self.t_apm = w(6, "Seoul"), w(7, "three")
        self.t_find, self.t_late = w(9, "Find"), w(9, "late")
        self.t_gg, self.t_queue = w(10, "GG"), w(10, "queuing")
        rng = np.random.default_rng(41)
        self.crowd = [(int(x), int(y), int(c)) for x, y, c in zip(rng.integers(0, 384, 260), rng.integers(70, 160, 260), rng.integers(0, 6, 260))]

    def speaker_for(self, line):
        return "Player 2" if line["idx"] % 2 else "Player 1"

    def build_ground(self):
        rng = np.random.default_rng(6)
        h, w = self.MAP_H, self.MAP_W
        base = np.array([[66, 60, 74], [58, 54, 66], [74, 68, 82], [50, 46, 58]], np.uint8)
        idx = rng.integers(0, 3, (h // 2 + 1, w // 2 + 1))
        g = base[np.repeat(np.repeat(idx, 2, 0), 2, 1)[:h, :w]]
        yy, xx = np.mgrid[0:h, 0:w]
        creep = np.hypot((xx - ZERG[0]) / 150, (yy - ZERG[1]) / 100) + rng.random((h, w)) * 0.15 < 1
        g[creep] = np.where(rng.random((creep.sum(), 1)) > 0.5, (96, 44, 84), (110, 52, 96))
        plates = (xx < 170) & (yy > 90)
        g[plates] = (92, 98, 110)
        g[plates & ((xx % 16 == 0) | (yy % 16 == 0))] = (70, 76, 88)
        prot = np.hypot((xx - PROTOSS[0]) / 70, (yy - PROTOSS[1]) / 40) < 1
        g[prot] = (150, 132, 90)
        g[prot & ((xx + yy) % 7 == 0)] = (180, 160, 110)
        return g

    def lings(self, t):
        out = []
        for i in range(14):
            st = self.t_ling + i * 0.06
            if t < st:
                continue
            k = min(1.0, (t - st) / 2.2)
            x = lerp(ZERG[0] - 40, TERRAN[0] + 40 + (i % 4) * 8, k)
            y = lerp(ZERG[1] + (i % 5) * 8 - 16, TERRAN[1] + (i % 5) * 6, k) + math.sin(t * 20 + i) * 2
            out.append((x, y))
        return out

    def resources(self, t):
        if self.t_min <= t < self.L[5]:
            return ("0", "0", "200/200")
        return (str(400 + int((t - self.t0) * 30)), str(150 + int((t - self.t0) * 8)), "78/200")

    def draw_actors(self, img, d, t):
        b = self.c.beat_pos(t)
        step = int(b * 2) % 2
        items = []
        nuked = t >= self.t_late
        for i, (mx, my) in enumerate([(20, 110), (30, 124), (16, 136), (40, 106)]):
            items.append((my, lambda mx=mx, my=my, i=i: units.crystals(d, mx, my, glow=(math.sin(t * 4 + i) + 1) / 2, col=(80, 150, 240))))
        if not nuked:
            items.append((TERRAN[1], lambda: units.bunker(d, *TERRAN)))
            items.append((TERRAN[1] + 30, lambda: units.bunker(d, TERRAN[0] + 50, TERRAN[1] + 30)))
            for i in range(4):
                items.append((TERRAN[1] + 14, lambda i=i: units.infantry(d, TERRAN[0] - 10 + i * 10, TERRAN[1] + 14, team="blue", step=step)))
            items.append((TERRAN[1] - 20, lambda: units.scv(d, TERRAN[0] + 40, TERRAN[1] - 20, f=-1, step=step, weld=int(t * 10) % 2 == 0)))
        items.append((ZERG[1], lambda: units.hive(d, *ZERG, pulse=self.c.pulse(t))))
        for x, y in self.lings(t):
            if not (nuked and x < 200):
                items.append((y, lambda x=x, y=y: sprites.blit(img, "ZERGLING", x - 5, y - 6, team="purple", flip=True)))
        for i, (px, py) in enumerate([(300, 66), (350, 76)]):
            items.append((py, lambda px=px, py=py: units.pylon(d, px, py, t=t)))
        if t >= self.t_pylon - 0.2:
            wk = ease((t - self.t_pylon + 0.2) / 0.8)
            items.append((100, lambda: units.pylon(d, 330, 100, warp=wk, field=wk, t=t)))
        for i in range(3):
            items.append((86, lambda i=i: units.infantry(d, 316 + i * 12, 86, team="gold", step=step)))
        for _, fn in sorted(items, key=lambda e: e[0]):
            fn()
        if self.L[8] <= t < self.t_late:  # nuke dot
            if int(t * 6) % 2:
                d.ellipse([NUKE_AT[0] - 2, NUKE_AT[1] - 2, NUKE_AT[0] + 2, NUKE_AT[1] + 2], fill=(255, 30, 30))
            if t >= self.t_find:
                gx = NUKE_AT[0] + 60
                d.ellipse([gx - 3, NUKE_AT[1] - 16, gx + 3, NUKE_AT[1] - 10], outline=(150, 200, 230))
                d.rectangle([gx - 2, NUKE_AT[1] - 10, gx + 2, NUKE_AT[1] - 2], outline=(150, 200, 230))
        if nuked:
            units.nuke_cloud(d, NUKE_AT[0], NUKE_AT[1], min(1.0, (t - self.t_late) / 2.5))

    def camera(self, t):
        L = self.L
        tr = self.t_races
        return engine.shot_cam(t, [(self.t0, (180, 40)), (tr[0], (0, 70)), (tr[1], (370, 60)), (tr[2], (150, 0)),
                                   (self.t_scv - 0.1, (0, 70)), (self.t_ling, (120, 60)), (self.t_pylon - 0.2, (150, 20)),
                                   (L[4], (0, 60)), (L[8], (0, 70))], trans=0.35)

    def minimap_dots(self, t):
        return [(TERRAN[0], TERRAN[1], (90, 140, 255), True), (ZERG[0], ZERG[1], (180, 80, 200), True),
                (PROTOSS[0], PROTOSS[1], (230, 190, 70), True)] + [(x, y, (180, 80, 200), False) for x, y in self.lings(t)]

    # --- full-viewport inserts ---------------------------------------------
    def split_sky(self, frame, t):
        v = Image.new("RGB", (hud.W, hud.BOT - hud.TOP), (4, 4, 12))
        engine.stars(v, t, n=120)
        d = ImageDraw.Draw(v)
        k = ease((t - self.L[0]) / 1.6)
        cx, cy = 192, 80
        for i, col in enumerate([(90, 140, 255), (180, 80, 200), (230, 190, 70)]):
            a = math.radians(-90 + i * 120 + t * 10)
            ex, ey = cx + math.cos(a) * 260 * k, cy + math.sin(a) * 260 * k
            d.line([cx, cy, ex, ey], fill=col, width=3)
            d.line([cx, cy, ex, ey], fill=(255, 255, 255), width=1)
        frame.paste(v, (0, hud.TOP))

    def lobby(self, frame, t):
        d = ImageDraw.Draw(frame)
        d.rectangle([0, hud.TOP, hud.W, hud.BOT], fill=(6, 10, 30))
        d.rectangle([12, hud.TOP + 8, 220, hud.BOT - 8], fill=(10, 20, 60), outline=(90, 140, 230))
        draw_text(frame, 18, hud.TOP + 12, "CHANNEL: MIDNIGHT LADDER", (140, 200, 255), shadow=None)
        msgs = ["<RUSHKID> GL HF", "<ZERGMOM> NO RUSH 10 MIN?", "<PYLONPAPA> LOL NO", "<RUSHKID> 2 AM GG",
                "<SCV_SAM> ONE MORE?", "<OVERMIND99> ONE MORE."]
        n = int((t - self.L[5]) / 0.35) + 1
        for i, m in enumerate(msgs[:n]):
            draw_text(frame, 18, hud.TOP + 26 + i * 12, m, (220, 230, 255), shadow=None)
        d.rectangle([232, hud.TOP + 8, 372, hud.BOT - 8], fill=(10, 20, 60), outline=(90, 140, 230))
        draw_text(frame, 238, hud.TOP + 12, "LADDER", hud.GOLD_TXT, shadow=None)
        climb = ease((t - self.L[5]) / 2.2)
        my_rank = int(lerp(7, 0, climb))
        order = LADDER[:]
        order.remove("XXSLAYERXX")
        order.insert(my_rank, "RUSHKID")
        for i, name in enumerate(order[:8]):
            col = (255, 255, 120) if name == "RUSHKID" else (200, 210, 240)
            draw_text(frame, 238, hud.TOP + 26 + i * 15, f"{i + 1}. {name}", col, shadow=None)

    def stadium(self, frame, t):
        d = ImageDraw.Draw(frame)
        top = hud.TOP
        d.rectangle([0, top, hud.W, hud.BOT], fill=(10, 8, 20))
        for i in range(5):
            x = 40 + i * 76
            d.polygon([(x, top), (x - 30, top + 160), (x + 30, top + 160)], fill=(30, 26, 54))
        d.rectangle([110, top + 6, 274, top + 62], fill=(20, 20, 30), outline=(200, 200, 220))
        sub = self.ground.crop((0, 60, 384, 216)).resize((162, 54), Image.NEAREST)
        frame.paste(sub, (111, top + 7))
        draw_text(frame, 114, top + 8, "LIVE", (255, 60, 60), shadow=None)
        for side, x in ((0, 40), (1, 300)):
            d.rectangle([x, top + 80, x + 44, top + 110], fill=(40, 60, 130) if side == 0 else (130, 40, 60), outline=(200, 200, 220))
            d.ellipse([x + 16, top + 70, x + 28, top + 82], fill=(230, 180, 130), outline=engine.K)
        pulse = self.c.pulse(t)
        cols = [(220, 60, 60), (60, 120, 220), (230, 200, 60), (230, 230, 230), (120, 200, 90), (200, 100, 200)]
        for x, y, c in self.crowd:
            if y < 112:
                continue
            bob = int(pulse * 3) if (x + y) % 3 == 0 else 0
            d.rectangle([x, y + top - bob, x + 3, y + top + 3 - bob], fill=cols[c])
            if (x * 7 + int(t * 8)) % 97 == 0:
                d.point((x + 1, y + top - 2 - bob), fill=(255, 255, 255))
        engine.big_text(frame, "SEOUL STADIUM", t - self.t_seoul, scale=2, y=top + 128, col=(255, 255, 255))

    def apm(self, frame, t):
        d = ImageDraw.Draw(frame)
        d.rectangle([0, hud.TOP, hud.W, hud.BOT], fill=(8, 8, 18))
        v = int(lerp(60, 300, ease((t - self.t_apm) / 1.6)))
        engine.big_text(frame, f"APM {v}", 99, scale=5, y=hud.TOP + 40, col=(140, 200, 255))
        keys = "QWERTYUIOPASDFGHJKL"
        for i, ch in enumerate(keys):
            x, y = 40 + (i % 10) * 31 + (i // 10) * 12, hud.TOP + 90 + (i // 10) * 26
            lit = (i * 5 + int(t * 16)) % 7 == 0
            d.rectangle([x, y, x + 24, y + 20], fill=(250, 240, 160) if lit else (60, 60, 80), outline=(140, 140, 170))
            draw_text(frame, x + 10, y + 7, ch, engine.K if lit else (200, 200, 220), shadow=None)
        for i in range(4):
            nx = (i * 97 + t * 60) % 384
            ny = hud.TOP + 20 + 10 * math.sin(t * 3 + i)
            d.ellipse([nx, ny + 4, nx + 4, ny + 8], fill=(255, 255, 255))
            d.line([nx + 4, ny + 6, nx + 4, ny - 4], fill=(255, 255, 255))

    def overlay(self, frame, t, cam):
        if self.footage:
            return
        L = self.L
        cx, cy = cam
        if L[0] <= t < L[1]:
            self.split_sky(frame, t)
            engine.big_text(frame, "1998", t - self.t_98, scale=5, y=hud.TOP + 70)
            return
        if L[5] <= t < self.t_seoul:
            self.lobby(frame, t); return
        if self.t_seoul <= t < self.t_apm:
            self.stadium(frame, t); return
        if self.t_apm <= t < L[8]:
            self.apm(frame, t); return
        names = [("TERRAN GRIT!", (140, 180, 255)), ("ZERG SWARM!", (210, 120, 230)), ("PROTOSS GOLD!", (240, 210, 100))]
        for i, st in enumerate(self.t_races):
            nxt = self.t_races[i + 1] if i < 2 else L[2]
            if st <= t < nxt:
                engine.big_text(frame, names[i][0], t - st, scale=3, y=hud.TOP + 26, col=names[i][1])
        if self.t_scv <= t < self.t_ling:
            from sc_v2 import bubble
            bubble(frame, TERRAN[0] + 50 - cx, TERRAN[1] - 50 - cy + hud.TOP, "GOOD TO GO, SIR!")
        if self.t_ling <= t < L[3]:
            engine.big_text(frame, "SIX-POOL RUSH!", t - self.t_ling, scale=3, y=hud.TOP + 26, col=(210, 120, 230))
        if L[3] <= t < L[4]:
            msg = "YOU MUST CONSTRUCT ADDITIONAL PYLONS"
            if t < self.t_hush:
                n = int((t - L[3]) / max(0.1, self.t_hush - L[3]) * len(msg))
                draw_text(frame, 8, hud.TOP + 4, msg[:n], (140, 200, 255))
            else:
                engine.big_text(frame, "SHHH!", t - self.t_hush, scale=4, y=hud.TOP + 50)
        if L[4] <= t < L[5]:
            draw_text(frame, 8, hud.TOP + 4, "NOT ENOUGH MINERALS.", (255, 90, 80))
            if t >= self.t_gas:
                draw_text(frame, 8, hud.TOP + 14, "INSUFFICIENT VESPENE GAS.", (255, 90, 80))
        if L[8] <= t < self.t_late:
            draw_text(frame, 8, hud.TOP + 4, "NUCLEAR LAUNCH DETECTED.", (255, 60, 50))
            if t >= self.t_find:
                engine.big_text(frame, "FIND THE GHOST!", t - self.t_find, scale=3, y=hud.TOP + 30, col=(255, 90, 80))
        if self.t_late <= t < self.t_late + 0.8:
            engine.big_text(frame, "TOO LATE!", t - self.t_late, scale=4, y=hud.TOP + 40)
        if t >= self.t_gg:
            d = ImageDraw.Draw(frame)
            k = ease((t - self.t_gg) / 0.6)
            d.rectangle([60, hud.TOP + 30, 324, hud.TOP + 120], fill=(6, 10, 30), outline=(90, 140, 230))
            engine.big_text(frame, "GG", t - self.t_gg, scale=6, y=hud.TOP + 62, col=(140, 200, 255))
            if t >= self.t_queue:
                dots = "." * (int(t * 3) % 4)
                txt = "SEARCHING FOR OPPONENT" + dots
                draw_text(frame, 192 - text_width("SEARCHING FOR OPPONENT...") // 2, hud.TOP + 100, txt, (220, 230, 255))

    def postfx(self, frame, t):
        L = self.L
        if L[8] <= t < self.t_late:
            a = np.asarray(frame).astype(np.float32)
            p = 0.5 + 0.5 * math.sin(t * 9)
            a[hud.TOP:hud.BOT] *= np.array([1.0, 1 - 0.3 * p, 1 - 0.3 * p])
            frame.paste(Image.fromarray(np.clip(a, 0, 255).astype(np.uint8)))
        if self.t_late <= t < self.t_late + 0.5:
            return 0.9 * (1 - (t - self.t_late) / 0.5)
        return 0.15 if any(0 <= t - st < 0.07 for st in self.t_races) else 0.0

    def portrait(self, t, singing):
        if self.cur_speaker == "EVA":
            return engine.eva_portrait(t, singing, self.c)
        line, _ = self.tl.line_at(t, sec=self.sec)
        odd = line and line["idx"] % 2 == 1
        if odd:
            return engine.portrait(skin=(214, 160, 116), hair=(200, 60, 120), shirt=(130, 60, 170), bg=(30, 16, 40),
                                   mouth=engine.mouth_amt(self.c, t, singing), blink=int(t * 10) % 29 == 0)
        return engine.portrait(shirt=(60, 90, 160), helmet=(110, 120, 140), bg=(10, 16, 40),
                               mouth=engine.mouth_amt(self.c, t, singing), blink=int(t * 10) % 31 == 0, eyes=(120, 220, 255))
