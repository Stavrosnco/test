"""Procedurally drawn units, vehicles and structures. (x, y) is the bottom-centre (ground contact).
f = +1 faces right, -1 faces left. All designs original."""
import math
from PIL import ImageDraw
K = (22, 18, 20)
TEAM = {"blue": ((58, 104, 214), (34, 60, 140)), "red": ((200, 50, 40), (124, 28, 24)),
        "purple": ((130, 60, 170), (80, 30, 110)), "gold": ((230, 190, 70), (160, 120, 30)),
        "green": ((70, 170, 70), (40, 110, 40)), "grey": ((120, 124, 136), (80, 84, 96))}
METAL, METAL_D, METAL_L = (150, 152, 162), (96, 98, 110), (196, 198, 208)


def poly(d, pts, x, y, f, fill, outline=K):
    d.polygon([(x + f * px, y + py) for px, py in pts], fill=fill, outline=outline)


def rect(d, x0, y0, x1, y1, x, y, f, fill, outline=K):
    xs = sorted([x + f * x0, x + f * x1])
    d.rectangle([xs[0], y + y0, xs[1], y + y1], fill=fill, outline=outline)


# --- fantasy -----------------------------------------------------------------
def ogre(d, x, y, team="red", f=1, step=0, rage=0.0):
    tc, td = TEAM[team]
    skin, skin_d = (110, 150, 80), (74, 110, 54)
    if rage > 0:
        r = 13 + int(rage * 3)
        d.ellipse([x - r, y - 26 - r // 2, x + r, y - 2 + r // 3], outline=(240, 40, 40))
    leg = 2 if step else 0
    rect(d, -6, -8, -2, 0 - leg, x, y, f, (90, 64, 40))
    rect(d, 2, -8, 6, 0 - (2 - leg), x, y, f, (90, 64, 40))
    d.ellipse([x - 9, y - 26, x + 9, y - 6], fill=skin, outline=K)
    d.rectangle([x - 8, y - 12, x + 8, y - 8], fill=tc, outline=K)
    for hx in (-6, 6):
        d.ellipse([x + hx - 3, y - 34, x + hx + 3, y - 27], fill=skin, outline=K)
        d.point((x + hx + f, y - 31), fill=(250, 60, 40) if rage else K)
        d.point((x + hx - 1, y - 28), fill=(240, 240, 220)); d.point((x + hx + 1, y - 28), fill=(240, 240, 220))
        d.line([x + hx - 3, y - 35, x + hx - 4, y - 37], fill=(220, 210, 180))
    d.line([x + f * 9, y - 18, x + f * 14, y - 28], fill=(110, 76, 40), width=3)
    d.ellipse([x + f * 14 - 3, y - 32, x + f * 14 + 3, y - 26], fill=(110, 76, 40), outline=K)


def death_knight(d, x, y, team="red", f=1, cast=0.0):
    tc, td = TEAM[team]
    horse = (40, 36, 44)
    d.ellipse([x - 10, y - 14, x + 8, y - 6], fill=horse, outline=K)
    for lx in (-8, -4, 2, 6):
        d.line([x + f * lx, y - 8, x + f * lx, y], fill=horse, width=2)
    poly(d, [(6, -12), (12, -18), (14, -15), (9, -9)], x, y, f, horse)
    d.point((x + f * 12, y - 16), fill=(250, 60, 40))
    d.rectangle([x - 4, y - 24, x + 2, y - 12], fill=(54, 50, 64), outline=K)
    d.polygon([(x - 6, y - 22), (x - 10, y - 8), (x - 2, y - 10)], fill=td, outline=K)
    d.ellipse([x - 4, y - 30, x + 2, y - 24], fill=(70, 66, 80), outline=K)
    d.point((x - 1 + f, y - 27), fill=(120, 255, 120))
    d.line([x + f * 4, y - 30, x + f * 4, y - 10], fill=(110, 90, 140), width=1)
    if cast > 0:
        r = int(3 + cast * 5)
        d.ellipse([x + f * 4 - r, y - 32 - r, x + f * 4 + r, y - 32 + r], outline=(160, 80, 220))
        d.point((x + f * 4, y - 32), fill=(220, 160, 255))


def skeleton(d, x, y, f=1, rise=1.0, step=0):
    """rise in [0,1]: emerging from the ground."""
    bone, bd = (226, 222, 200), (150, 146, 130)
    h = int(16 * rise)
    if h <= 0:
        return
    top = y - h
    d.ellipse([x - 3, top, x + 3, top + 6], fill=bone, outline=K)
    d.point((x - 1 + f, top + 3), fill=K)
    if h > 8:
        d.line([x, top + 6, x, min(y, top + 12)], fill=bone)
        for ry in range(top + 7, min(y, top + 12), 2):
            d.line([x - 2, ry, x + 2, ry], fill=bd)
        d.line([x - 3, top + 8, x + 3, top + 8], fill=bone)
        d.line([x + f * 3, top + 8, x + f * 6, top + 4], fill=(150, 150, 160))
    if h > 12:
        lg = 1 if step else 0
        d.line([x, top + 12, x - 2 - lg, y], fill=bone); d.line([x, top + 12, x + 2 + lg, y], fill=bone)
    d.line([x - 6, y, x + 6, y], fill=(80, 60, 40))


def catapult(d, x, y, team="red", f=1, arm=0.0):
    """arm 0 = cocked, 1 = released."""
    tc, td = TEAM[team]
    wood, wood_d = (140, 96, 56), (96, 64, 34)
    d.rectangle([x - 12, y - 8, x + 12, y - 4], fill=wood, outline=K)
    for wx in (-8, 8):
        d.ellipse([x + wx - 4, y - 8, x + wx + 4, y], fill=wood_d, outline=K)
    d.rectangle([x - 2, y - 16, x + 2, y - 8], fill=wood, outline=K)
    ang = math.radians(200 - 120 * arm) if f > 0 else math.radians(-20 + 120 * arm)
    ex, ey = x + 16 * math.cos(ang), y - 14 - 16 * math.sin(ang) * -1
    ex, ey = x + f * 16 * math.cos(math.radians(160 - 110 * arm)), y - 14 - 16 * math.sin(math.radians(160 - 110 * arm))
    d.line([x, y - 14, ex, ey], fill=wood_d, width=2)
    d.ellipse([ex - 2, ey - 2, ex + 2, ey + 2], fill=(120, 120, 120), outline=K)
    d.rectangle([x - 12, y - 6, x - 8, y - 5], fill=tc)


def boat(d, x, y, team="red", f=1, bob=0):
    tc, td = TEAM[team]
    y = y + bob
    poly(d, [(-18, -6), (18, -6), (13, 2), (-13, 2)], x, y, f, (110, 72, 40))
    d.line([x - 15, y - 3, x + 15, y - 3], fill=(150, 110, 60))
    d.line([x, y - 6, x, y - 28], fill=(80, 54, 30), width=1)
    poly(d, [(1, -27), (13, -12), (1, -10)], x, y, f, tc)
    d.line([x + f, y - 24, x + f * 9, y - 14], fill=td)


def castle(d, x, y, team="blue", damage=0.0, gate_open=False):
    """x, y = bottom-centre; ~80 px wide."""
    tc, td = TEAM[team]
    stone, sd, sl = (138, 136, 146), (100, 98, 108), (170, 168, 178)
    d.rectangle([x - 34, y - 34, x + 34, y], fill=stone, outline=K)
    for by in range(y - 30, y, 6):
        for bx in range(x - 32 + (by // 6 % 2) * 4, x + 32, 8):
            d.line([bx, by, bx + 5, by], fill=sd)
    for tx in (-38, 30):
        d.rectangle([x + tx, y - 50, x + tx + 10, y], fill=sl, outline=K)
        for cx in range(x + tx, x + tx + 10, 4):
            d.rectangle([cx, y - 54, cx + 2, y - 50], fill=sl, outline=K)
        d.line([x + tx + 5, y - 54, x + tx + 5, y - 64], fill=K)
        d.polygon([(x + tx + 6, y - 64), (x + tx + 13, y - 61), (x + tx + 6, y - 58)], fill=tc)
    for cx in range(x - 34, x + 34, 6):
        d.rectangle([cx, y - 38, cx + 3, y - 34], fill=stone, outline=K)
    if gate_open:
        d.rectangle([x - 8, y - 16, x + 8, y], fill=(20, 14, 10), outline=K)
        d.line([x - 10, y, x - 16, y - 3], fill=(110, 72, 40), width=2)
    else:
        d.rectangle([x - 8, y - 16, x + 8, y], fill=(90, 60, 34), outline=K)
        for gx in range(x - 6, x + 8, 3):
            d.line([gx, y - 15, gx, y - 1], fill=(60, 40, 22))
    if damage > 0:
        for i in range(int(damage * 6)):
            hx = x - 28 + (i * 37) % 56
            hy = y - 30 + (i * 13) % 20
            d.ellipse([hx, hy, hx + 6, hy + 4], fill=(40, 34, 30))


def stump(d, x, y):
    d.ellipse([x - 3, y - 2, x + 3, y + 1], fill=(126, 86, 46), outline=K)
    d.point((x, y - 1), fill=(180, 140, 90))


def explosion(d, x, y, k, size=1.0):
    """k in [0,1] over the explosion's life."""
    if k < 0 or k > 1:
        return
    r = int((4 + 18 * k) * size)
    cols = [(255, 250, 210), (255, 210, 80), (240, 120, 30), (120, 60, 30), (60, 50, 50)]
    c = cols[min(4, int(k * 5))]
    d.ellipse([x - r, y - r, x + r, y + r], fill=c, outline=K if k > 0.6 else None)
    if k < 0.6:
        rr = int(r * 0.55)
        d.ellipse([x - rr, y - rr, x + rr, y + rr], fill=(255, 255, 230))
    for i in range(8):
        a = i * math.pi / 4 + 0.3
        px, py = x + math.cos(a) * r * 1.4, y + math.sin(a) * r * 1.1
        d.rectangle([px, py, px + 1, py + 1], fill=(255, 220, 120) if k < 0.5 else (90, 80, 70))


# --- industrial ----------------------------------------------------------------
def harvester(d, x, y, team="gold", f=1, load=0.0, glow=(80, 220, 90)):
    tc, td = TEAM[team]
    d.rectangle([x - 15, y - 5, x + 15, y], fill=(50, 50, 54), outline=K)
    for wx in range(-12, 14, 6):
        d.ellipse([x + wx - 2, y - 4, x + wx + 2, y], fill=(80, 80, 86), outline=K)
    rect(d, -14, -16, 6, -5, x, y, f, tc)
    rect(d, 6, -13, 14, -5, x, y, f, td)
    rect(d, 9, -12, 13, -9, x, y, f, (150, 200, 230))
    if load > 0:
        rect(d, -12, -16 - int(4 * load), 3, -16, x, y, f, glow)
    for i in range(3):
        rect(d, 15 + i * 2, -4, 16 + i * 2, 0, x, y, f, METAL_L)


def tank(d, x, y, team="blue", f=1, recoil=0.0, big=False):
    tc, td = TEAM[team]
    s = 1.5 if big else 1.0
    w, h = int(13 * s), int(5 * s)
    d.rectangle([x - w, y - h, x + w, y], fill=(52, 52, 56), outline=K)
    for wx in range(-w + 3, w - 1, 5):
        d.ellipse([x + wx - 2, y - h + 1, x + wx + 2, y - 1], fill=(90, 90, 96))
    d.rectangle([x - w + 2, y - h - int(5 * s), x + w - 2, y - h], fill=tc, outline=K)
    d.ellipse([x - int(6 * s), y - h - int(10 * s), x + int(6 * s), y - h - int(3 * s)], fill=td, outline=K)
    bl = int(14 * s) - int(recoil * 3)
    by = y - h - int(7 * s)
    for off in ((-1, 1) if big else (0,)):
        d.line([x + f * 3, by + off * 2, x + f * bl, by + off * 2], fill=METAL_D, width=2)
    if big:
        rect(d, -w + 2, -h - 9, -w + 6, -h - 4, x, y, f, METAL_L)


def obelisk(d, x, y, team="red", charge=0.0):
    tc, td = TEAM[team]
    d.rectangle([x - 8, y - 6, x + 8, y], fill=(60, 60, 66), outline=K)
    d.polygon([(x - 6, y - 6), (x - 3, y - 46), (x + 3, y - 46), (x + 6, y - 6)], fill=(36, 34, 40), outline=K)
    d.line([x - 1, y - 44, x - 1, y - 8], fill=(70, 66, 76))
    d.polygon([(x - 3, y - 46), (x, y - 54), (x + 3, y - 46)], fill=tc, outline=K)
    if charge > 0:
        r = int(2 + charge * 4)
        d.ellipse([x - r, y - 52 - r, x + r, y - 52 + r], fill=(255, 120, 100))


def tesla_coil(d, x, y, team="red", charge=0.0):
    tc, td = TEAM[team]
    d.rectangle([x - 8, y - 6, x + 8, y], fill=(90, 86, 80), outline=K)
    d.rectangle([x - 3, y - 30, x + 3, y - 6], fill=(140, 110, 70), outline=K)
    for cy in range(y - 28, y - 6, 3):
        d.line([x - 4, cy, x + 4, cy], fill=(200, 150, 80))
    d.ellipse([x - 6, y - 40, x + 6, y - 28], fill=(160, 170, 190), outline=K)
    d.rectangle([x - 8, y - 4, x + 8, y - 2], fill=tc)
    if charge > 0:
        d.ellipse([x - 8, y - 42, x + 8, y - 26], outline=(170, 210, 255))


def bolt(d, x0, y0, x1, y1, seed, col=(190, 220, 255)):
    import random
    rng = random.Random(seed)
    pts = [(x0, y0)]
    for i in range(1, 8):
        k = i / 8
        pts.append((x0 + (x1 - x0) * k + rng.randint(-5, 5), y0 + (y1 - y0) * k + rng.randint(-5, 5)))
    pts.append((x1, y1))
    d.line(pts, fill=(255, 255, 255), width=2)
    d.line(pts, fill=col, width=1)


def infantry(d, x, y, team="blue", f=1, step=0, hat=None):
    tc, td = TEAM[team]
    d.ellipse([x - 2, y - 12, x + 2, y - 8], fill=(232, 178, 128), outline=K)
    if hat:
        d.rectangle([x - 2, y - 13, x + 2, y - 11], fill=hat, outline=K)
    d.rectangle([x - 2, y - 8, x + 2, y - 3], fill=tc, outline=K)
    lg = 1 if step else 0
    d.line([x - 1, y - 3, x - 1 - lg, y], fill=td); d.line([x + 1, y - 3, x + 1 + lg, y], fill=td)
    d.line([x + f * 2, y - 6, x + f * 6, y - 7], fill=(60, 60, 64))


def crystals(d, x, y, glow=0.0, col=(70, 220, 90)):
    hi = tuple(min(255, int(c + 90 * glow)) for c in col)
    if glow > 0.6:
        d.ellipse([x - 8, y - 3, x + 8, y + 3], fill=(60, 120, 60))
    for i, (cx, h) in enumerate([(-5, 8), (0, 13), (5, 7), (-2, 6), (3, 10)]):
        d.polygon([(x + cx - 2, y), (x + cx, y - h), (x + cx + 2, y)], fill=hi if i % 2 else col, outline=K)


def concrete_building(d, x, y, w, h, team="gold", kind="yard", light=False):
    tc, td = TEAM[team]
    d.rectangle([x - 2, y - 2, x + w + 2, y + h + 2], fill=(110, 110, 104))
    d.rectangle([x, y, x + w, y + h], fill=(150, 146, 136), outline=K)
    d.rectangle([x + 3, y + 3, x + w - 3, y + h // 2], fill=(120, 118, 112), outline=K)
    d.rectangle([x, y + h - 5, x + w, y + h - 3], fill=tc)
    if kind == "yard":
        d.line([x + w // 2, y - 10, x + w // 2, y + 3], fill=(230, 180, 40), width=2)
        d.line([x + w // 2, y - 10, x + w + 6, y - 10], fill=(230, 180, 40), width=2)
        d.line([x + w + 6, y - 10, x + w + 6, y - 2], fill=K)
    elif kind == "refinery":
        for i in range(2):
            d.ellipse([x + 4 + i * 12, y + h // 2 - 2, x + 14 + i * 12, y + h - 6], fill=(90, 92, 96), outline=K)
    elif kind == "power":
        d.rectangle([x + w - 8, y - 12, x + w - 3, y + 3], fill=(120, 118, 112), outline=K)
        d.ellipse([x + 4, y + h // 2, x + 12, y + h - 6], fill=(240, 220, 120) if light else (100, 96, 70), outline=K)
    for wx in range(x + 5, x + w - 4, 7):
        d.rectangle([wx, y + h // 2 + 3, wx + 3, y + h // 2 + 5], fill=(240, 220, 140) if light else (60, 60, 64))


def sandworm(d, x, y, k, f=1):
    """k: 0..1 emerge, mouth open around 0.5, sink by 1."""
    if not 0 < k < 1:
        return
    h = int(42 * math.sin(k * math.pi))
    sand, sd = (214, 166, 96), (170, 120, 64)
    d.ellipse([x - 22, y - 6, x + 22, y + 6], fill=sd)
    for i in range(6):
        seg_y = y - i * 7
        if y - seg_y > h:
            break
        r = 11 - i
        d.ellipse([x - r, seg_y - 6, x + r, seg_y + 3], fill=(176, 130, 86), outline=K)
        d.line([x - r + 2, seg_y - 2, x + r - 2, seg_y - 2], fill=(130, 90, 56))
    top = y - h
    open_ = max(0.0, 1 - abs(k - 0.5) * 3)
    r = 9
    d.ellipse([x - r, top - 4 - int(6 * open_), x + r, top + 4], fill=(176, 130, 86), outline=K)
    if open_ > 0:
        d.ellipse([x - 6, top - 2 - int(5 * open_), x + 6, top + 2], fill=(80, 20, 30), outline=K)
        for tx in range(-5, 6, 2):
            d.point((x + tx, top - 1 - int(5 * open_)), fill=(240, 236, 210))
    for i in range(10):
        a = i * 0.63
        d.point((x + math.cos(a) * 24, y + math.sin(a) * 6), fill=sand)


# --- ancient ---------------------------------------------------------------------
def elephant(d, x, y, team="red", f=1, step=0):
    tc, td = TEAM[team]
    g, gd = (140, 136, 140), (100, 96, 102)
    for i, lx in enumerate((-9, -4, 4, 9)):
        lift = 2 if (i + step) % 2 else 0
        d.rectangle([x + f * lx - 2, y - 8, x + f * lx + 2, y - lift], fill=gd, outline=K)
    d.ellipse([x - 14, y - 24, x + 12, y - 6], fill=g, outline=K)
    d.ellipse([x + f * 8, y - 26, x + f * 20, y - 12] if f > 0 else [x - 20, y - 26, x - 8, y - 12], fill=g, outline=K)
    d.line([x + f * 18, y - 14, x + f * 21, y - 4], fill=g, width=3)
    d.line([x + f * 14, y - 13, x + f * 20, y - 11], fill=(240, 236, 214))
    d.point((x + f * 15, y - 21), fill=K)
    d.rectangle([x - 8, y - 32, x + 4, y - 22], fill=tc, outline=K)
    d.rectangle([x - 6, y - 34, x + 2, y - 31], fill=td, outline=K)


def berry_bush(d, x, y, left=1.0):
    d.ellipse([x - 7, y - 10, x + 7, y], fill=(40, 100, 44), outline=K)
    d.ellipse([x - 5, y - 9, x + 3, y - 3], fill=(60, 130, 56))
    for i in range(int(6 * left)):
        bx, by = x - 5 + (i * 5) % 11, y - 8 + (i * 3) % 6
        d.rectangle([bx, by, bx + 1, by + 1], fill=(200, 40, 70))


def fishing_boat(d, x, y, team="blue", f=1, bob=0):
    tc, td = TEAM[team]
    y += bob
    poly(d, [(-11, -4), (11, -4), (8, 1), (-8, 1)], x, y, f, (150, 106, 60))
    d.line([x - f * 2, y - 4, x - f * 2, y - 16], fill=(90, 60, 30))
    poly(d, [(-1, -16), (-10, -6), (-1, -6)], x, y, f, (236, 230, 210))
    d.line([x + f * 8, y - 4, x + f * 16, y + 4], fill=(220, 220, 220))
    d.rectangle([x - 2, y - 4, x + 2, y - 3], fill=tc)


def age_center(d, x, y, age, team="blue"):
    """Town centre that changes look with age 0..3 (stone, tool, bronze, iron). x,y bottom-centre."""
    tc, td = TEAM[team]
    if age == 0:
        for hx in (-14, 4):
            d.polygon([(x + hx - 2, y), (x + hx + 6, y - 20), (x + hx + 14, y)], fill=(150, 116, 70), outline=K)
            d.line([x + hx + 6, y - 20, x + hx + 6, y - 24], fill=(110, 80, 50))
            d.rectangle([x + hx + 4, y - 6, x + hx + 8, y], fill=(50, 34, 20))
        d.rectangle([x - 2, y - 4, x + 2, y], fill=tc)
    elif age == 1:
        d.rectangle([x - 20, y - 18, x + 20, y], fill=(150, 108, 64), outline=K)
        d.polygon([(x - 24, y - 18), (x, y - 32), (x + 24, y - 18)], fill=(170, 140, 80), outline=K)
        d.rectangle([x - 4, y - 10, x + 4, y], fill=(60, 40, 24), outline=K)
        d.rectangle([x - 20, y - 4, x + 20, y - 2], fill=tc)
    elif age == 2:
        d.rectangle([x - 24, y - 22, x + 24, y], fill=(196, 160, 110), outline=K)
        d.rectangle([x - 26, y - 26, x + 26, y - 22], fill=(170, 130, 86), outline=K)
        for cx in range(x - 20, x + 22, 8):
            d.rectangle([cx, y - 21, cx + 2, y - 1], fill=(220, 196, 150))
        d.rectangle([x - 26, y - 30, x + 26, y - 26], fill=tc, outline=K)
    else:
        d.rectangle([x - 28, y - 4, x + 28, y], fill=(200, 196, 186), outline=K)
        d.rectangle([x - 26, y - 26, x + 26, y - 4], fill=(236, 232, 222), outline=K)
        for cx in range(x - 24, x + 26, 6):
            d.rectangle([cx, y - 25, cx + 2, y - 5], fill=(250, 248, 240), outline=(170, 166, 156))
        d.polygon([(x - 30, y - 26), (x, y - 40), (x + 30, y - 26)], fill=(236, 232, 222), outline=K)
        d.polygon([(x - 18, y - 28), (x, y - 36), (x + 18, y - 28)], fill=tc)


def trebuchet(d, x, y, team="blue", f=1, arm=0.0):
    tc, td = TEAM[team]
    wood, wd = (140, 96, 56), (96, 64, 34)
    d.rectangle([x - 14, y - 4, x + 14, y], fill=wood, outline=K)
    d.line([x - 10, y - 4, x, y - 30], fill=wood, width=2)
    d.line([x + 10, y - 4, x, y - 30], fill=wood, width=2)
    a = math.radians(-60 + 200 * arm)
    ax, ay = x + f * 22 * math.cos(a), y - 30 - 22 * math.sin(a)
    cx, cy = x - f * 8 * math.cos(a), y - 30 + 8 * math.sin(a)
    d.line([cx, cy, ax, ay], fill=wd, width=2)
    d.rectangle([cx - 4, cy, cx + 4, cy + 7], fill=(90, 88, 96), outline=K)
    d.rectangle([x - 14, y - 3, x - 10, y - 1], fill=tc)


def wall_segment(d, x, y, w, broken=0.0):
    stone, sd = (176, 168, 150), (130, 124, 110)
    h = 18
    for i in range(0, w, 8):
        hh = h - (int(broken * 14 * ((i * 7) % 5) / 4) if broken else 0)
        d.rectangle([x + i, y - hh, x + i + 7, y], fill=stone, outline=K)
        d.line([x + i + 1, y - hh // 2, x + i + 6, y - hh // 2], fill=sd)
    if broken > 0.3:
        for i in range(6):
            d.rectangle([x + (i * 13) % w, y + 1 + i % 3, x + (i * 13) % w + 3, y + 3 + i % 3], fill=sd, outline=K)


# --- space -------------------------------------------------------------------------
def scv(d, x, y, f=1, step=0, weld=False):
    tc = TEAM["blue"][0]
    d.rectangle([x - 6, y - 6, x + 6, y - 2], fill=(70, 72, 80), outline=K)
    for lx in (-4, 4):
        d.line([x + lx, y - 2, x + lx - step, y], fill=(60, 60, 66), width=2)
    d.ellipse([x - 7, y - 18, x + 7, y - 5], fill=(170, 160, 120), outline=K)
    d.rectangle([x - 3, y - 15, x + 3, y - 10], fill=(110, 170, 210), outline=K)
    d.rectangle([x - 7, y - 9, x + 7, y - 7], fill=tc)
    d.line([x + f * 6, y - 10, x + f * 12, y - 8], fill=METAL_D, width=2)
    if weld:
        d.point((x + f * 13, y - 8), fill=(255, 255, 200))
        d.point((x + f * 14, y - 9), fill=(120, 200, 255))


def pylon(d, x, y, warp=1.0, field=0.0, t=0.0):
    if field > 0:
        r = int(36 * field)
        d.ellipse([x - r, y - r // 2, x + r, y + r // 2], outline=(80, 140, 255))
    if warp < 1:
        for i in range(int(12 * warp)):
            d.line([x - 8 + i, y - 30, x - 8 + i, y], fill=(80, 140, 255) if i % 2 else (180, 220, 255))
        return
    d.polygon([(x - 8, y), (x - 4, y - 6), (x + 4, y - 6), (x + 8, y)], fill=(200, 170, 80), outline=K)
    glow = int(40 * (0.5 + 0.5 * math.sin(t * 6)))
    d.polygon([(x, y - 30), (x - 6, y - 14), (x, y - 6), (x + 6, y - 14)], fill=(60 + glow, 150 + glow, 255), outline=K)
    d.line([x, y - 28, x, y - 8], fill=(220, 240, 255))


def hive(d, x, y, pulse=0.0):
    p = int(pulse * 2)
    d.ellipse([x - 26 - p, y - 22 - p, x + 26 + p, y + 4], fill=(110, 50, 90), outline=K)
    d.ellipse([x - 18, y - 30 - p, x + 18, y - 6], fill=(140, 70, 110), outline=K)
    for i in range(5):
        d.ellipse([x - 16 + i * 7, y - 16, x - 12 + i * 7, y - 12], fill=(200, 160, 60))
    d.arc([x - 22, y - 20, x + 22, y + 2], 200, 340, fill=(80, 30, 60))


def bunker(d, x, y):
    d.rectangle([x - 16, y - 12, x + 16, y], fill=(100, 104, 112), outline=K)
    d.polygon([(x - 18, y - 12), (x - 12, y - 18), (x + 12, y - 18), (x + 18, y - 12)], fill=(130, 134, 144), outline=K)
    d.rectangle([x - 10, y - 9, x + 10, y - 6], fill=K)
    d.rectangle([x - 16, y - 3, x + 16, y - 1], fill=TEAM["blue"][0])


def nuke_cloud(d, x, y, k):
    """Mushroom cloud, k in [0,1]."""
    if k <= 0:
        return
    h = int(60 * min(1, k * 1.6))
    cols = [(255, 255, 230), (255, 220, 120), (240, 140, 50), (150, 80, 50), (90, 70, 70)]
    c = cols[min(4, int(k * 5))]
    d.rectangle([x - 5, y - h, x + 5, y], fill=c, outline=K)
    r = int(14 + 20 * k)
    d.ellipse([x - r, y - h - r // 2, x + r, y - h + r // 2], fill=c, outline=K)
    d.ellipse([x - r - 10, y - 8, x + r + 10, y + 6], fill=c, outline=K)
