"""Shared scene machinery: timeline lookup, HUD themes, portraits, map scenes."""
import json, math
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw
import hud, sprites
from font import draw_text, text_width

ROOT = Path(__file__).parent.parent
K = (22, 18, 20)
BAYER = (np.array([[0, 8, 2, 10], [12, 4, 14, 6], [3, 11, 1, 9], [15, 7, 13, 5]]) + 0.5) / 16


class Timeline:
    def __init__(self, path=ROOT / "analysis/timeline.json"):
        self.sections = json.loads(Path(path).read_text())
        self.lines = []
        for si, s in enumerate(self.sections):
            for li, l in enumerate(s["lines"]):
                self.lines.append({**l, "sec": si, "idx": li})
        for a, b in zip(self.lines, self.lines[1:]):
            a["next"] = b["start"]
        self.lines[-1]["next"] = self.sections[-1]["end"]

    def sec(self, i):
        return self.sections[i]

    def line_at(self, t, hold=1.5, sec=None):
        """Current lyric line and the words sung so far (or None)."""
        for l in self.lines:
            if sec is not None and l["sec"] != sec:
                continue
            if l["start"] - 0.05 <= t < min(l["next"], l["end"] + hold):
                shown = " ".join(w["w"] for w in l["words"] if w["s"] - 0.05 <= t)
                return l, shown
        return None, ""

    def line(self, sec, idx):
        return self.sections[sec]["lines"][idx]

    def line_t(self, sec, idx, end=False):
        l = self.sections[sec]["lines"][idx]
        return l["end"] if end else l["start"]

    def word_t(self, sec, idx, word):
        """Start time of the first word in a line matching `word` (prefix, case-insensitive)."""
        for w in self.sections[sec]["lines"][idx]["words"]:
            if w["w"].lower().strip("\"'(!,.?").startswith(word.lower()):
                return w["s"]
        return self.line_t(sec, idx)


# --- HUD themes ----------------------------------------------------------------
THEMES = {
    "medieval": dict(bar=(54, 42, 32), bar_l=(96, 78, 58), bar_d=(24, 18, 14), panel=(60, 56, 64),
                     panel_l=(104, 100, 112), panel_d=(26, 24, 30), box=(30, 28, 36), frame=(150, 140, 110),
                     title=(200, 180, 140), res=("GOLD", "LUMBER", "FOOD")),
    "desert": dict(bar=(84, 58, 30), bar_l=(150, 112, 62), bar_d=(40, 26, 12), panel=(110, 84, 50),
                   panel_l=(170, 136, 86), panel_d=(52, 36, 18), box=(40, 28, 16), frame=(220, 170, 90),
                   title=(240, 200, 130), res=("SPICE", "POWER", "UNITS")),
    "cnc": dict(bar=(36, 38, 36), bar_l=(80, 86, 80), bar_d=(10, 12, 10), panel=(48, 52, 48),
                panel_l=(92, 100, 92), panel_d=(14, 16, 14), box=(8, 18, 10), frame=(90, 200, 90),
                title=(120, 230, 120), res=("CREDITS", "POWER", "UNITS")),
    "aoe": dict(bar=(70, 50, 30), bar_l=(150, 120, 70), bar_d=(30, 20, 10), panel=(120, 96, 62),
                panel_l=(190, 160, 110), panel_d=(56, 40, 22), box=(48, 34, 20), frame=(230, 196, 110),
                title=(250, 220, 150), res=("FOOD", "WOOD", "POP")),
    "sc": dict(bar=(20, 26, 40), bar_l=(60, 80, 120), bar_d=(6, 8, 14), panel=(28, 34, 50),
               panel_l=(70, 90, 130), panel_d=(8, 10, 18), box=(6, 10, 20), frame=(90, 160, 230),
               title=(140, 200, 255), res=("MINERALS", "GAS", "SUPPLY")),
}


def bevel(d, box, fill, light, dark):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=fill)
    d.line([x0, y0, x1, y0], fill=light); d.line([x0, y0, x0, y1], fill=light)
    d.line([x0, y1, x1, y1], fill=dark); d.line([x1, y0, x1, y1], fill=dark)


def wrap(text, width_px):
    rows, cur = [], ""
    for w in text.split(" "):
        if cur and text_width(cur + " " + w) > width_px:
            rows.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    return rows + ([cur] if cur else [])


def draw_hud(frame, theme, t, res, title, minimap=None, cam_box=None, portrait=None,
             speaker="", text="", hot=-1, buttons=None):
    th = THEMES[theme]
    d = ImageDraw.Draw(frame)
    W, H = hud.W, hud.H
    bevel(d, (0, 0, W - 1, hud.TOP - 1), th["bar"], th["bar_l"], th["bar_d"])
    x = 3
    icons = [(246, 206, 62), (126, 200, 255) if theme == "sc" else (150, 110, 60), (176, 150, 60)]
    for (val, col) in zip(res, icons):
        d.rectangle([x, 2, x + 5, 7], fill=col, outline=K)
        draw_text(frame, x + 8, 2, str(val), (236, 236, 236))
        x += 50
    m, s = divmod(int(t), 60)
    clock = f"{m}:{s:02d}"
    draw_text(frame, W - 3 - text_width(clock), 2, clock, (236, 236, 236))
    draw_text(frame, W - 12 - text_width(clock) - text_width(title), 2, title, th["title"])

    bevel(d, (0, hud.BOT, W - 1, H - 1), th["panel"], th["panel_l"], th["panel_d"])
    mx, my = 3, hud.BOT + 4
    d.rectangle([mx - 1, my - 1, mx + 100, my + 40], outline=th["frame"], fill=(6, 6, 10))
    if minimap is not None:
        frame.paste(minimap, (mx, my))
        if cam_box:
            cx0, cy0, cx1, cy1 = cam_box
            d.rectangle([mx + cx0, my + cy0, mx + cx1, my + cy1], outline=(236, 236, 236))
    px, py = 108, hud.BOT + 4
    bevel(d, (px - 1, py - 1, px + 30, py + 39), (20, 20, 26), th["frame"], th["panel_d"])
    if portrait:
        portrait(frame, px, py)
    tx, ty = 142, hud.BOT + 5
    d.rectangle([tx - 2, ty - 2, 300, H - 5], fill=th["box"], outline=th["panel_l"])
    if speaker:
        draw_text(frame, tx, ty, speaker.upper() + ":", hud.GOLD_TXT)
    for i, r in enumerate(wrap(text, 154)[:3]):
        draw_text(frame, tx, ty + 10 + i * 9, r, (236, 236, 236))
    bx, by = 305, hud.BOT + 5
    for i, icon in enumerate(buttons or hud.DEFAULT_BUTTONS):
        x, y = bx + (i % 3) * 26, by + (i // 3) * 20
        lit = i == hot
        bevel(d, (x, y, x + 23, y + 17), (90, 120, 90) if lit else (44, 44, 52),
              (180, 220, 160) if lit else (100, 100, 112), (20, 20, 24))
        icon(d, x + 12, y + 9)


def subtitle(frame, text, speaker=None, y=None, color=(250, 250, 240)):
    """Lyric subtitle for scenes outside the game HUD."""
    rows = wrap(text, hud.W - 40)[:2]
    y = hud.H - 12 - 10 * len(rows) if y is None else y
    for i, r in enumerate(rows):
        draw_text(frame, (hud.W - text_width(r)) // 2, y + i * 10, r, color, outline=True, shadow=(10, 8, 12))


def big_text(frame, txt, age, scale=3, y=None, col=(246, 206, 62), pop_col=(255, 255, 255)):
    pop = max(0.0, 1 - age * 3)
    c = pop_col if pop > 0.3 else col
    lines = txt.split("|")
    total = len(lines) * 9 * scale
    y0 = (hud.TOP + 40 if y is None else y) - total // 2 - int(pop * 6)
    for i, ln in enumerate(lines):
        s = scale
        while text_width(ln, s) > hud.W - 8 and s > 1:
            s -= 1
        draw_text(frame, (hud.W - text_width(ln, s)) // 2, y0 + i * 9 * scale, ln, c, scale=s,
                  shadow=(20, 14, 10), outline=True)


# --- portraits -------------------------------------------------------------------
def portrait(skin=(232, 178, 128), hair=(104, 64, 34), shirt=(58, 104, 214), bg=(46, 70, 50),
             mouth=0.0, blink=False, helmet=None, extra=None, eyes=K):
    def draw(img, x, y):
        d = ImageDraw.Draw(img)
        d.rectangle([x, y, x + 29, y + 38], fill=bg)
        d.ellipse([x + 3, y + 26, x + 27, y + 50], fill=shirt, outline=K)
        d.ellipse([x + 6, y + 5, x + 24, y + 29], fill=skin, outline=K)
        if helmet:
            d.chord([x + 4, y + 1, x + 26, y + 22], 180, 360, fill=helmet, outline=K)
            d.rectangle([x + 4, y + 11, x + 26, y + 13], fill=helmet, outline=K)
        elif hair:
            d.chord([x + 5, y + 2, x + 25, y + 20], 180, 360, fill=hair, outline=K)
        ey = y + 15
        if blink:
            d.line([x + 10, ey, x + 13, ey], fill=K); d.line([x + 17, ey, x + 20, ey], fill=K)
        else:
            d.rectangle([x + 11, ey - 1, x + 12, ey + 1], fill=eyes); d.rectangle([x + 18, ey - 1, x + 19, ey + 1], fill=eyes)
        mh = int(mouth * 5)
        d.rectangle([x + 13, y + 22, x + 17, y + 22 + mh], fill=(90, 30, 30), outline=K)
        if extra:
            extra(d, x, y)
        d.rectangle([x, y + 39, x + 29, y + 39], fill=K)
    return draw


def mouth_amt(clock, t, singing):
    return min(1.0, clock.nrg(t) * 2.2) * (0.5 + 0.5 * math.sin(t * 38)) if singing else 0.0


def cursor(frame, x, y, col=(246, 206, 62)):
    d = ImageDraw.Draw(frame)
    x, y = int(x), int(y)
    d.polygon([(x, y), (x, y + 9), (x + 3, y + 6), (x + 6, y + 9), (x + 7, y + 8), (x + 4, y + 5), (x + 7, y + 4)],
              fill=col, outline=K)


# --- map scenes --------------------------------------------------------------------
class MapScene:
    """A scrolling RTS map viewed through the HUD. Subclasses fill in the world."""
    MAP_W, MAP_H = 640, 256
    theme, title, speaker = "medieval", "", ""
    fog_dim = (6, 6, 10)
    use_fog = True

    def __init__(self, ctx, sec):
        self.ctx, self.c, self.tl = ctx, ctx.clock, ctx.timeline
        self.sec = sec
        self.t0, self.t1 = ctx.timeline.sec(sec)["start"], ctx.timeline.sec(sec)["end"]
        self.ground = Image.fromarray(self.build_ground())
        self.yy, self.xx = np.mgrid[0:self.MAP_H, 0:self.MAP_W].astype(np.float32)
        self.thr = np.tile(BAYER, (self.MAP_H // 4, self.MAP_W // 4))

    # to override
    def build_ground(self): raise NotImplementedError
    def draw_actors(self, img, d, t): pass
    def fog_sources(self, t): return []
    def camera(self, t): return 0, 0
    def overlay(self, frame, t, cam): pass
    def resources(self, t): return (0, 0, "0/0")
    def portrait(self, t, singing): return portrait(mouth=mouth_amt(self.c, t, singing))
    cur_speaker = ""
    def minimap_dots(self, t): return []
    def postfx(self, frame, t): return 0.0

    footage = False

    def frame(self, t, lyric_t=None):
        self.footage = lyric_t is not None
        lt = t if lyric_t is None else lyric_t
        img = self.ground.copy()
        d = ImageDraw.Draw(img)
        self.draw_actors(img, d, t)
        arr = np.asarray(img).copy()
        vis = None
        if self.use_fog:
            vis = np.zeros((self.MAP_H, self.MAP_W), np.float32)
            for x, y, r in self.fog_sources(t):
                x0, x1 = int(max(0, x - r)), int(min(self.MAP_W, x + r + 1))
                y0, y1 = int(max(0, y - r)), int(min(self.MAP_H, y + r + 1))
                if x0 >= x1 or y0 >= y1:
                    continue
                sub = np.clip((r - np.hypot(self.xx[y0:y1, x0:x1] - x, self.yy[y0:y1, x0:x1] - y)) / 22, 0, 1)
                vis[y0:y1, x0:x1] = np.maximum(vis[y0:y1, x0:x1], sub)
            arr[vis < self.thr] = self.fog_dim
            dim = (vis >= self.thr) & (vis < 0.55)
            arr[dim] = (arr[dim] * 0.6).astype(np.uint8)
        cx, cy = self.camera(t)
        cx = int(np.clip(cx, 0, self.MAP_W - hud.W)); cy = int(np.clip(cy, 0, self.MAP_H - (hud.BOT - hud.TOP)))
        shake = int(round(2 * self.c.downpulse(t, 9) * self.c.nrg(t)))
        sx = int(np.clip(cx + shake, 0, self.MAP_W - hud.W))
        view = Image.fromarray(arr[cy:cy + hud.BOT - hud.TOP, sx:sx + hud.W])
        frame = Image.new("RGB", (hud.W, hud.H))
        frame.paste(view, (0, hud.TOP))
        self.overlay(frame, t, (cx, cy))

        mm = (100, 40)
        base = np.asarray(self.ground)
        if vis is not None:
            base = np.where((vis > 0.3)[..., None], base, 8).astype(np.uint8)
        mini = Image.fromarray(base).resize(mm, Image.NEAREST)
        md = ImageDraw.Draw(mini)
        s = mm[0] / self.MAP_W
        for x, y, col, big in self.minimap_dots(t):
            if big:
                md.rectangle([x * s - 1, y * s - 1, x * s + 2, y * s + 1], fill=col)
            else:
                md.point((x * s, y * s), fill=col)
        cam = (int(cx * s), int(cy * s), int((cx + hud.W) * s), int((cy + hud.BOT - hud.TOP) * s))
        line, shown = self.tl.line_at(lt)
        singing = bool(line) and lt <= line["end"]
        spk = self.speaker
        if line and line["speaker"] and "Robotic" in line["speaker"]:
            spk = "EVA"
        self.cur_speaker = spk
        hot = int(self.c.beat_pos(t)) % 6 if self.c.pulse(t) > 0.3 else -1
        draw_hud(frame, self.theme, lt, self.resources(t), self.title, mini, cam,
                 self.portrait(lt, singing), spk, shown, hot)
        flash = self.postfx(frame, t)
        return frame, flash


def chunks(line):
    """Split a lyric line into kinetic-text chunks: after ! or ?, before ( or a quote,
    and after a comma once the chunk has 3+ words."""
    out, cur, st = [], [], None
    for w in line["words"]:
        if w["w"].startswith(("(", '"')) and cur:
            out.append((st, " ".join(cur))); cur, st = [], None
        if st is None:
            st = w["s"]
        cur.append(w["w"])
        tail = w["w"].rstrip('"\'')
        if tail.endswith(("!", "?")) or (tail.endswith((",", ":")) and len(cur) >= 3):
            out.append((st, " ".join(cur))); cur, st = [], None
    if cur:
        out.append((st, " ".join(cur)))
    return out


def kinetic(frame, tl, t, sec, scale=3, y=None, hold=0.5, upper_only=None, col=(246, 206, 62), sub=False):
    """Big punch-in text for hook lines in section `sec`. Chunks too long for scale 2 become
    a bottom subtitle when sub=True (else they are skipped; the HUD chat shows them)."""
    line, _ = tl.line_at(t, hold=hold, sec=sec)
    if not line or (upper_only and not upper_only(line)):
        return
    ch = chunks(line)
    for i, (st, txt) in enumerate(ch):
        nxt = ch[i + 1][0] if i + 1 < len(ch) else line["end"] + hold
        if st - 0.03 <= t < nxt:
            txt = txt.rstrip(",:")
            if text_width(txt, 2) > hud.W - 8:
                if sub:
                    subtitle(frame, txt)
            else:
                big_text(frame, txt, t - st, scale=scale, y=y, col=col)


def shot_cam(t, keys, trans=0.6):
    """keys: [(time, (x, y)), ...] sorted. Eases from the previous key to the current one."""
    from clock import ease
    prev = keys[0][1]
    cur = keys[0][1]
    for i, (kt, pos) in enumerate(keys):
        if t >= kt:
            prev, cur, st = (keys[i - 1][1] if i else pos), pos, kt
    if t < keys[0][0]:
        return keys[0][1]
    k = ease((t - st) / trans)
    return prev[0] + (cur[0] - prev[0]) * k, prev[1] + (cur[1] - prev[1]) * k


def stars(img, t, seed=5, n=90, area=None):
    d = ImageDraw.Draw(img)
    rng = np.random.default_rng(seed)
    w, h = img.size
    for i in range(n):
        x, y = int(rng.integers(0, w)), int(rng.integers(0, h))
        tw = (math.sin(t * 3 + i) + 1) / 2
        c = int(120 + 135 * tw) if i % 4 == 0 else 160
        d.point((x, y), fill=(c, c, min(255, c + 30)))


def sub_line(frame, tl, t, sec=None, y=None):
    line, shown = tl.line_at(t, sec=sec)
    if shown:
        subtitle(frame, shown, y=y)


def eva_portrait(t, singing, clock):
    def draw(img, x, y):
        d = ImageDraw.Draw(img)
        d.rectangle([x, y, x + 29, y + 38], fill=(4, 16, 6))
        for yy in range(y, y + 39, 3):
            d.line([x, yy, x + 29, yy], fill=(8, 30, 12))
        g = (80, 230, 90)
        d.ellipse([x + 7, y + 6, x + 23, y + 30], outline=g)
        d.line([x + 15, y + 6, x + 15, y + 30], fill=(40, 120, 50))
        d.line([x + 7, y + 18, x + 23, y + 18], fill=(40, 120, 50))
        d.rectangle([x + 10, y + 14, x + 12, y + 15], fill=g); d.rectangle([x + 18, y + 14, x + 20, y + 15], fill=g)
        m = int(mouth_amt(clock, t, singing) * 4)
        d.line([x + 12, y + 24, x + 18, y + 24 + m // 2], fill=g)
    return draw
