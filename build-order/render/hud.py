"""The fake 90s RTS interface that frames the whole video."""
from PIL import ImageDraw
from font import draw_text, text_width

W, H = 384, 216
TOP, BOT = 10, 168
GOLD_TXT, WHITE, GREEN = (246, 206, 62), (236, 236, 236), (80, 230, 90)
K = (22, 18, 20)

def bevel(d, box, fill, light, dark):
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=fill)
    d.line([x0, y0, x1, y0], fill=light); d.line([x0, y0, x0, y1], fill=light)
    d.line([x0, y1, x1, y1], fill=dark); d.line([x1, y0, x1, y1], fill=dark)

def top_bar(img, gold, lumber, food, cap, song_t, title):
    d = ImageDraw.Draw(img)
    bevel(d, (0, 0, W - 1, TOP - 1), (54, 42, 32), (96, 78, 58), (24, 18, 14))
    d.ellipse([3, 2, 8, 7], fill=GOLD_TXT, outline=K)
    draw_text(img, 11, 2, f"{gold}", GOLD_TXT)
    d.rectangle([52, 3, 58, 6], fill=(126, 86, 46), outline=K)
    draw_text(img, 61, 2, f"{lumber}", WHITE)
    d.rectangle([100, 2, 105, 7], fill=(176, 150, 60), outline=K)
    draw_text(img, 108, 2, f"{food}/{cap}", WHITE)
    m, s = divmod(int(song_t), 60)
    clock = f"{m}:{s:02d}"
    draw_text(img, W - 3 - text_width(clock), 2, clock, WHITE)
    draw_text(img, W - 12 - text_width(clock) - text_width(title), 2, title, (200, 180, 140))

def bottom_panel(img, minimap, cam_box, portrait_fn, speaker, line, buttons, hot):
    d = ImageDraw.Draw(img)
    bevel(d, (0, BOT, W - 1, H - 1), (60, 56, 64), (104, 100, 112), (26, 24, 30))
    # minimap
    mx, my = 3, BOT + 4
    d.rectangle([mx - 1, my - 1, mx + minimap.width, my + minimap.height], outline=(150, 140, 110))
    img.paste(minimap, (mx, my))
    cx0, cy0, cx1, cy1 = cam_box
    d.rectangle([mx + cx0, my + cy0, mx + cx1, my + cy1], outline=WHITE)
    # portrait
    px, py = 108, BOT + 4
    bevel(d, (px - 1, py - 1, px + 30, py + 39), (20, 20, 26), (150, 140, 110), (40, 36, 30))
    portrait_fn(img, px, py)
    # chat / lyric box
    tx, ty = 142, BOT + 5
    d.rectangle([tx - 2, ty - 2, 300, H - 5], fill=(30, 28, 36), outline=(90, 86, 98))
    draw_text(img, tx, ty, speaker, GOLD_TXT)
    words, rows, cur = line.split(" "), [], ""
    for w in words:
        if text_width((cur + " " + w).strip()) > 154:
            rows.append(cur); cur = w
        else:
            cur = (cur + " " + w).strip()
    rows.append(cur)
    for i, r in enumerate(rows[:3]):
        draw_text(img, tx, ty + 10 + i * 9, r, WHITE)
    # command card
    bx, by = 305, BOT + 5
    for i, icon in enumerate(buttons):
        x, y = bx + (i % 3) * 26, by + (i // 3) * 20
        lit = i == hot
        bevel(d, (x, y, x + 23, y + 17), (90, 120, 90) if lit else (44, 44, 52),
              (180, 220, 160) if lit else (100, 100, 112), (20, 20, 24))
        icon(d, x + 12, y + 9)

# command-card icons, centred on (x, y)
def ic_sword(d, x, y):
    d.line([x - 5, y + 5, x + 4, y - 4], fill=(200, 202, 212), width=2)
    d.line([x - 4, y + 1, x - 1, y + 4], fill=(126, 86, 46), width=2)
def ic_shield(d, x, y):
    d.polygon([(x - 5, y - 5), (x + 5, y - 5), (x + 5, y), (x, y + 6), (x - 5, y)], fill=(58, 104, 214), outline=K)
    d.line([x, y - 4, x, y + 4], fill=(246, 206, 62))
def ic_hammer(d, x, y):
    d.line([x - 4, y + 5, x + 2, y - 1], fill=(126, 86, 46), width=2)
    d.rectangle([x, y - 6, x + 5, y - 1], fill=(178, 180, 190), outline=K)
def ic_move(d, x, y):
    d.polygon([(x - 5, y - 2), (x + 1, y - 2), (x + 1, y - 5), (x + 6, y), (x + 1, y + 5), (x + 1, y + 2), (x - 5, y + 2)], fill=GREEN, outline=K)
def ic_stop(d, x, y):
    d.rectangle([x - 4, y - 4, x + 4, y + 4], fill=(200, 50, 40), outline=K)
def ic_gold(d, x, y):
    d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=GOLD_TXT, outline=K)
    d.line([x - 1, y - 2, x - 1, y + 2], fill=(190, 138, 30))
DEFAULT_BUTTONS = [ic_move, ic_stop, ic_sword, ic_shield, ic_hammer, ic_gold]

def worker_portrait(mouth_open, blink):
    def draw(img, x, y):
        d = ImageDraw.Draw(img)
        d.rectangle([x, y, x + 29, y + 38], fill=(46, 70, 50))
        d.ellipse([x + 3, y + 26, x + 27, y + 50], fill=(58, 104, 214), outline=K)
        d.ellipse([x + 6, y + 5, x + 24, y + 29], fill=(232, 178, 128), outline=K)
        d.chord([x + 5, y + 2, x + 25, y + 20], 180, 360, fill=(104, 64, 34), outline=K)
        ey = y + 15
        if blink:
            d.line([x + 10, ey, x + 13, ey], fill=K); d.line([x + 17, ey, x + 20, ey], fill=K)
        else:
            d.rectangle([x + 11, ey - 1, x + 12, ey + 1], fill=K); d.rectangle([x + 18, ey - 1, x + 19, ey + 1], fill=K)
        mh = int(mouth_open * 5)
        d.rectangle([x + 13, y + 22, x + 17, y + 22 + mh], fill=(90, 30, 30), outline=K)
    return draw
