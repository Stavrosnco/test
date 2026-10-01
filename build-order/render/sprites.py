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

@lru_cache(maxsize=None)
def sprite(name, team="blue", flip=False):
    grid = globals()[name]
    pal = {**BASE, **TEAMS[team]}
    img = Image.new("RGBA", (len(grid[0]), len(grid)), (0, 0, 0, 0))
    px = img.load()
    for y, row in enumerate(grid):
        for x, c in enumerate(row):
            if c in pal:
                px[x, y] = pal[c] + (255,)
    return ImageOps.mirror(img) if flip else img

def blit(dst, name, x, y, team="blue", flip=False):
    s = sprite(name, team, flip)
    dst.paste(s, (int(x), int(y)), s)
