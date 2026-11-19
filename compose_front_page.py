#!/usr/bin/env python3
"""Compose the front page for Thursday 19 November 2026.

Draws a newspaper front page ("THE WORLD IN ONE PAGE") as a 1024x1024
PNG. Everything is drawn with Pillow: the dusk-skyline hero illustration
is generated procedurally (gradient sky, building silhouettes, three
flagpoles with simplified US / Chinese / Russian flags), and all text is
set with DejaVu fonts. Fully deterministic: fixed random seed, no network,
no timestamps embedded in the output.
"""
import random
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE / "entry.png"
HERO_PATH = HERE / "assets" / "hero.png"

W, H = 1024, 1024
PAPER = (246, 241, 229)
INK = (17, 17, 17)
RED = (158, 27, 27)
GREY = (90, 86, 76)
RULE = (17, 17, 17)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(name, size):
    """Load a DejaVu font, falling back to the default bitmap font."""
    for candidate in (FONT_DIR / name,):
        try:
            return ImageFont.truetype(str(candidate), size)
        except OSError:
            continue
    return ImageFont.load_default()


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)      # noqa: E731
SERIF = lambda s: font("DejaVuSerif.ttf", s)             # noqa: E731
SERIF_I = lambda s: font("DejaVuSerif-Italic.ttf", s)    # noqa: E731
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)        # noqa: E731
SANS = lambda s: font("DejaVuSans.ttf", s)               # noqa: E731


def wrap(draw, text, fnt, max_width):
    """Greedy word wrap returning a list of lines fitting max_width."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        trial = f"{current} {word}".strip()
        if draw.textlength(trial, font=fnt) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def draw_lines(draw, lines, x, y, fnt, fill=INK, leading=1.25):
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill)
        y += int(fnt.size * leading)
    return y


# ---------------------------------------------------------------- hero art
def draw_hero():
    """Procedural dusk skyline with three flagpoles. No people, no text."""
    w, h = 952, 300
    img = Image.new("RGB", (w, h))
    px = img.load()
    top = (24, 30, 62)
    mid = (122, 62, 96)
    low = (232, 112, 58)
    for yy in range(h):
        t = yy / h
        if t < 0.55:
            k = t / 0.55
            c = tuple(int(top[i] + (mid[i] - top[i]) * k) for i in range(3))
        else:
            k = (t - 0.55) / 0.45
            c = tuple(int(mid[i] + (low[i] - mid[i]) * k) for i in range(3))
        for xx in range(w):
            px[xx, yy] = c
    d = ImageDraw.Draw(img)
    rng = random.Random(20261119)
    # stars in the upper sky
    for _ in range(90):
        x = rng.randint(0, w - 1)
        y = rng.randint(0, 110)
        r = rng.choice([1, 1, 2])
        d.ellipse([x - r, y - r, x + r, y + r], fill=(235, 232, 220))
    # far skyline
    x = 0
    while x < w:
        bw = rng.randint(36, 90)
        bh = rng.randint(70, 150)
        d.rectangle([x, h - 96 - bh, x + bw, h - 96], fill=(28, 33, 58))
        x += bw + rng.randint(4, 18)
    # near skyline with lit windows
    x = -10
    while x < w:
        bw = rng.randint(50, 110)
        bh = rng.randint(30, 95)
        d.rectangle([x, h - 40 - bh, x + bw, h - 40], fill=(13, 16, 32))
        for _ in range(bw * bh // 260):
            wx = rng.randint(x + 5, x + bw - 7)
            wy = rng.randint(h - 40 - bh + 5, h - 48)
            d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 210, 122))
        x += bw + rng.randint(6, 20)
    # dark foreground strip
    d.rectangle([0, h - 40, w, h], fill=(10, 12, 24))

    def flag_us(x0, y0, fw, fh):
        for i in range(13):
            col = (178, 34, 52) if i % 2 == 0 else (240, 240, 235)
            d.rectangle([x0, y0 + i * fh // 13, x0 + fw, y0 + (i + 1) * fh // 13], fill=col)
        d.rectangle([x0, y0, x0 + int(fw * 0.4), y0 + int(fh * 7 / 13)], fill=(32, 48, 96))
        for r in range(4):
            for c in range(5):
                sx = x0 + 8 + c * 13
                sy = y0 + 6 + r * 11
                d.ellipse([sx, sy, sx + 3, sy + 3], fill=(240, 240, 235))

    def flag_cn(x0, y0, fw, fh):
        d.rectangle([x0, y0, x0 + fw, y0 + fh], fill=(222, 41, 16))
        cx, cy = x0 + 14, y0 + 12
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 222, 0))
        for sx, sy in [(x0 + 34, y0 + 6), (x0 + 42, y0 + 13), (x0 + 42, y0 + 23), (x0 + 34, y0 + 30)]:
            d.ellipse([sx - 3, sy - 3, sx + 3, sy + 3], fill=(255, 222, 0))

    def flag_ru(x0, y0, fw, fh):
        for i, col in enumerate([(240, 240, 235), (0, 57, 166), (213, 0, 50)]):
            d.rectangle([x0, y0 + i * fh // 3, x0 + fw, y0 + (i + 1) * fh // 3], fill=col)

    # three flagpoles across the foreground
    poles = [(150, flag_us), (476, flag_cn), (802, flag_ru)]
    for x0, fn in poles:
        d.rectangle([x0, 96, x0 + 5, h - 40], fill=(200, 200, 195))
        d.ellipse([x0 - 2, 88, x0 + 7, 97], fill=(220, 180, 60))
        fn(x0 + 5, 96, 78, 52)
    return img


# ---------------------------------------------------------------- front page
def build():
    hero = draw_hero()
    HERO_PATH.parent.mkdir(parents=True, exist_ok=True)
    hero.save(str(HERO_PATH))

    page = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(page)
    mx = 36  # margin
    right = W - mx

    # masthead
    mast = SERIF_B(60)
    title = "THE WORLD IN ONE PAGE"
    tw = d.textlength(title, font=mast)
    d.text(((W - tw) / 2, 26), title, font=mast, fill=INK)
    dateline = SANS(18)
    dl = "THURSDAY, 19 NOVEMBER 2026  —  SHENZHEN  ·  WASHINGTON  ·  THE GULF  ·  KYIV"
    dw = d.textlength(dl, font=dateline)
    d.text(((W - dw) / 2, 100), dl, font=dateline, fill=GREY)
    d.line([mx, 128, right, 128], fill=RULE, width=3)
    d.line([mx, 134, right, 134], fill=RULE, width=1)

    # hero
    page.paste(hero, (mx, 144))
    cap = SERIF_I(16)
    caption = ("Shenzhen at dusk, ahead of the first trilateral meeting of the US, "
               "Chinese and Russian leaders.")
    draw_lines(d, wrap(d, caption, cap, right - mx), mx, 450, cap, fill=GREY, leading=1.3)

    # main headline
    hl = SERIF_B(40)
    y = draw_lines(d, ["TRUMP, XI AND PUTIN", "MEET IN SHENZHEN"], mx, 478, hl, leading=1.08)
    stand = SERIF(20)
    standfirst = ("The leaders of the world's three largest nuclear powers meet for the "
                  "first time as a trio — nuclear arms, the Gulf war and Ukraine on "
                  "the table, and no deal expected.")
    y = draw_lines(d, wrap(d, standfirst, stand, right - mx), mx, 572, stand, leading=1.3)

    # divider
    d.line([mx, 638, right, 638], fill=RULE, width=2)

    # two columns
    col_w = 452
    kick = SANS_B(19)
    chead = SERIF_B(25)
    body = SERIF(17)

    def column(x, kicker, headline, text):
        yy = 650
        d.text((x, yy), kicker, font=kick, fill=RED)
        yy += 28
        yy = draw_lines(d, wrap(d, headline, chead, col_w), x, yy, chead, leading=1.12)
        yy = draw_lines(d, wrap(d, text, body, col_w), x, yy + 8, body, leading=1.32)
        return yy

    column(mx, "THE GULF",
           "US AND IRAN TRADE FIRE AS GULF WAR WIDENS",
           "American jets struck an Iranian missile site on Qeshm Island. Iran "
           "answered with drones at a US base in Kuwait and new attacks on "
           "Bahrain, as three US carrier groups gather in the Gulf.")
    column(536, "CRIMEA",
           "KERCH BRIDGE HIT FOR A THIRD TIME IN A WEEK",
           "Traffic was suspended after a new overnight strike on the bridge "
           "linking Russia to Crimea. Earlier attacks this week destroyed a "
           "227-metre section of its roadway.")

    # bottom band
    d.line([mx, 836, right, 836], fill=RULE, width=2)
    d.text((mx, 848), "AMERICA", font=kick, fill=RED)
    am = SERIF(20)
    amer = ("Democrats formally nominate Hakeem Jeffries for Speaker of the House; "
            "he would be the first Black lawmaker to hold the job.")
    draw_lines(d, wrap(d, amer, am, right - mx), mx, 876, am, leading=1.3)

    d.line([mx, 944, right, 944], fill=RULE, width=1)
    foot = SANS(14)
    ft = ("ALSO TODAY:  Anthropic's $81.3bn IPO  ·  Gaza ground operation  ·  "
          "GTA VI launches  ·  Voyager 1, one light-day out")
    fw = d.textlength(ft, font=foot)
    d.text(((W - fw) / 2, 956), ft, font=foot, fill=GREY)

    page.save(str(OUT))
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    build()
