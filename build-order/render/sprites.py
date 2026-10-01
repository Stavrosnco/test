"""Hand-authored pixel sprites. All original designs."""
from functools import lru_cache
from PIL import Image, ImageOps

BASE = {
    "k": (22, 18, 20), "s": (232, 178, 128), "S": (186, 126, 86), "h": (104, 64, 34),
    "b": (104, 72, 42), "w": (178, 180, 190), "W": (112, 114, 126), "n": (126, 86, 46),
    "y": (246, 206, 62), "Y": (190, 138, 30), "o": (236, 236, 224), "O": (184, 184, 172),
}
TEAMS = {
    "blue": {"T": (58, 104, 214), "t": (34, 60, 140)},
    "red": {"T": (200, 50, 40), "t": (124, 28, 24)},
}

WORKER_A = [
    "............", "....kkkk....", "...khhhhk...", "..khsssshk..", "..kskskssk..",
    "..ksssSSk...", "...kSSSk....", "..kTTTTTk.nw", ".kTTtTTTTkn.", ".ksTtTTTskn.",
    "..ktttttk...", "..kbbkbbk...", "..kbk.kbk...", "..kk...kk...",
]
WORKER_B = WORKER_A[:11] + ["...kbbbk....", "...kbkbk....", "...kk.kk...."]

SOLDIER_A = [
    "....kkkk....", "...kwwwwk...", "..kwwwwwwk..", "..kskssksk..", "...kSSSSk...",
    ".kk.kkkk.w..", "kTTkwTTwk.w.", "kTtkTTTTkkw.", "kTtkTttTkskk", "kTTkTTTTk.k.",
    ".kk.kttk....", "...kbbbbk...", "...kbkkbk...", "...kk..kk...",
]
SOLDIER_B = SOLDIER_A[:11] + ["...kbbbbk...", "....kbbk....", "....kkkk...."]

SHEEP = ["..kkkk...", ".kooook..", "koooooOkk", "kooooOOkk", ".kOOOOk..", ".k.k.k.k."]
SACK = [".kk.", "kyYk", "kyyk", ".kk."]

SKINS = {
    "orc": {"s": (98, 160, 70), "S": (64, 116, 46), "h": (40, 40, 40)},
    "toga": {"T": (236, 232, 214), "t": (190, 182, 160), "b": (150, 110, 60), "h": (40, 30, 24)},
    "hardhat": {"h": (246, 206, 62), "T": (230, 170, 40), "t": (170, 120, 20)},
    "dark": {"s": (200, 196, 210), "S": (150, 146, 160), "w": (60, 60, 70), "W": (40, 40, 48)},
    "bone": {"s": (226, 222, 200), "S": (170, 166, 150), "h": (226, 222, 200), "T": (226, 222, 200),
             "t": (170, 166, 150), "b": (226, 222, 200), "w": (150, 150, 160)},
}
TEAMS.update({"purple": {"T": (130, 60, 170), "t": (80, 30, 110)},
              "gold": {"T": (230, 190, 70), "t": (160, 120, 30)},
              "green": {"T": (70, 170, 70), "t": (40, 110, 40)},
              "grey": {"T": (120, 124, 136), "t": (80, 84, 96)}})

ZERGLING = ["..k....k..", ".kTk..kTk.", "kTTTTTTTTk", "kTtTttTTyk", ".kTktkTkk.", ".k.k..k.k."]
PRIEST = [
    "....kkkk....", "...kwwwwk...", "..kwssssk...", "..kskssk.n..", "...kSSk..n..",
    "..kTTTTTk.n.", ".kTTTTTTTkn.", ".kTTtTTTTkn.", ".kTTtTTTTkn.", ".kTTtTTTTk..",
    ".kTTtTTTTk..", ".kTTtTTTTk..", "..kTTTTTk...", "..kkkkkkk...",
]

@lru_cache(maxsize=None)
def sprite(name, team="blue", flip=False, skin=None):
    grid = globals()[name]
    pal = {**BASE, **TEAMS[team], **(SKINS[skin] if skin else {})}
    img = Image.new("RGBA", (len(grid[0]), len(grid)), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c in pal:
                px[x, y] = pal[c] + (255,)
    return ImageOps.mirror(img) if flip else img

def blit(dst, name, x, y, team="blue", flip=False, skin=None):
    s = sprite(name, team, flip, skin)
    dst.paste(s, (int(x), int(y)), s)
