#!/usr/bin/env python3
"""news-image-20261120 v3 — "THE WORLD IN ONE DAY", 35 stories, 1024x1024.

Written fresh in-session from the v3 brief (21 Nov 2026). Deterministic:
no network, no clock, no unseeded random. Pillow only, DejaVu Sans.

Layout (1024x1024, top to bottom):
  masthead 64 | colour bar 6 | UTC strip 30 | number strip 54 |
  region tabs 26 | 3 heroes 160 | 10 mid cards 290 | map 120 |
  briefs 192 | DATE CHECK 38 | footer 20
"""
import hashlib
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 16                      # side margin
CW = W - 2 * M              # content width = 992

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
F_SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
F_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")


def font(bold, size):
    return ImageFont.truetype(F_BOLD if bold else F_SANS, size)


# ---------------------------------------------------------------- palette
PAGE = (10, 22, 48)
PANEL = (16, 34, 68)
PANEL2 = (22, 44, 88)
GOLD = (212, 175, 55)
GOLD_LT = (232, 200, 90)
WHITE = (255, 255, 255)
INK = (235, 240, 250)
MUTED = (170, 185, 210)
MUTED_DK = (120, 135, 165)
NEON = (0, 229, 255)
CHIP = (13, 30, 62)
CHIP_LINE = (52, 84, 146)
TINT_A = (233, 239, 249)
TINT_B = (221, 230, 243)
DARKTXT = (13, 27, 62)
DARKMUT = (90, 105, 135)
RED = (178, 40, 40)
BAR6 = [(198, 52, 52), (232, 130, 40), (212, 175, 55),
        (70, 180, 110), (60, 130, 230), (140, 90, 200)]

REGION_COLOR = {
    "GLOBAL": (212, 175, 55),
    "EUROPE": (90, 140, 255),
    "MIDDLE EAST": (255, 90, 90),
    "ASIA-PACIFIC": (0, 200, 220),
    "AMERICAS": (90, 220, 120),
    "OCEANIA": (0, 200, 160),
    "AFRICA": (255, 170, 60),
}

# ---------------------------------------------------------------- data
HEROES = [
    dict(num=1, headline="SUMMIT OF THREE",
         deck="Leaders pledge a new framework after marathon talks.",
         source="Reuters", region="GLOBAL", art="summit"),
    dict(num=2, headline="BRIDGE HIT AGAIN",
         deck="Kerch crossing damaged; Ukraine claims the strike.",
         source="Reuters", region="EUROPE", art="bridge"),
    dict(num=3, headline="CYCLONE AKVAN",
         deck="Storm surge floods the coast as shelters fill.",
         source="IMD / The Hindu", region="ASIA-PACIFIC", art="cyclone"),
]

MIDS = [
    dict(num=4, headline="MISSILE OVER RIYADH",
         deck="Air defences intercept; damage reported in the financial district.",
         source="Reuters", region="MIDDLE EAST"),
    dict(num=5, headline="COP31: $305BN GAP",
         deck="Negotiators split on who pays for loss and damage.",
         source="Reuters", region="GLOBAL"),
    dict(num=6, headline="TALKS WITH MOSCOW",
         deck="Diplomats test a ceasefire framework.",
         source="AP", region="EUROPE"),
    dict(num=7, headline="YONGBYON GROWS",
         deck="Satellite images show new construction at the site.",
         source="IAEA", region="ASIA-PACIFIC"),
    dict(num=8, headline="VENEZUELA: $12BN",
         deck="Creditors press Caracas as reserves run low.",
         source="Reuters", region="AMERICAS"),
    dict(num=9, headline="HAN WALKS FREE",
         deck="Judges cite flawed evidence in the retrial ruling.",
         source="Yonhap", region="ASIA-PACIFIC"),
    dict(num=10, headline="NICHOLLS 113*",
         deck="Day one century puts the hosts on top.",
         source="AP", region="OCEANIA"),
    dict(num=11, headline="ANTHROPIC: $1.5TN",
         deck="AI lab's valuation jumps after IPO debut.",
         source="Reuters", region="AMERICAS"),
    dict(num=12, headline="GEMINI 4 NEON",
         deck="New model promises faster reasoning on device.",
         source="Reuters", region="AMERICAS"),
    dict(num=13, headline="GAZA AID PLEA",
         deck="Convoys wait at the border as supplies run low.",
         source="AP", region="MIDDLE EAST"),
]

BRIEFS = [
    (14, "IDF holds Yellow Line in Gaza", "AP", "ME"),
    (15, "Hezbollah strikes hit the border", "Reuters", "ME"),
    (16, "Iran holds 1,500–2,500 missiles", "WSJ", "ME"),
    (17, "Tanker hit by mine in the Gulf", "Reuters", "ME"),
    (18, "Drone shuts Genoa airport", "AP", "EU"),
    (19, "France protests enter a second week", "Reuters", "EU"),
    (20, "Eisenkot quits the war cabinet", "AP", "ME"),
    (21, "Korea exports top $1tn", "Yonhap", "APAC"),
    (22, "Sensex closes at 83,022", "Reuters", "APAC"),
    (23, "Taiwan FSC tightens crypto rules", "Reuters", "APAC"),
    (24, "Takaichi unveils stimulus plan", "AP", "APAC"),
    (25, "Ebola toll 10,668 cases, 5,198 deaths", "WHO", "AFRICA"),
    (26, "US probes Nvidia chip exports", "Reuters", "AMERICAS"),
    (27, "Pete Rose pardoned posthumously", "AP", "AMERICAS"),
    (28, "Fiona the hippo turns five", "AP", "AMERICAS"),
    (29, "GTA VI sells $1.84bn on day one", "Sensor Tower", "AMERICAS"),
    (30, "Albanese meets Xi in Canberra", "Reuters", "OCEANIA"),
    (31, "Trump holds White House presser", "AP", "AMERICAS"),
    (32, "France, Germany, UK issue joint statement", "Reuters", "EU"),
    (33, "NATO allies agree new guarantees", "AP", "EU"),
    (34, "Zverev reaches the final", "AP", "EU"),
    (35, "EU–UK summit set for next week", "Reuters", "EU"),
]

REGIONS = [("ASIA-PACIFIC", 7), ("EUROPE", 8), ("MIDDLE EAST", 7),
           ("AFRICA", 1), ("AMERICAS", 8), ("OCEANIA", 2), ("GLOBAL", 2)]

NUMBERS = [("300,000", "EVACUATED"), ("51–48", "SENATE"),
           ("$48bn", "IRAN WAR COST"), ("113*", "NICHOLLS"),
           ("83,022", "SENSEX"), ("$1.84bn", "GTA VI DAY ONE")]

UTC_CHIPS = ["02:15 AKVAN", "06:40 KAFD STRIKE",
             "09:30 SUMMIT", "12:05 BRIDGE HIT",
             "16:20 COP31 STALL", "21:45 SENATE 51–48"]

DATE_L1 = ("DATE CHECK — Senate vote 19 Nov · Han ruling 19 Nov · "
           "Yongbyon report 18 Nov · Nicholls day 1, 19 Nov · "
           "Sensex close 19 Nov · KAFD strike 19 Nov.")
DATE_L2 = "Friday stories, as the leading pages do."
FOOTER = "Compiled Friday 20 November 2026 · Sources as labelled · All figures as reported"

# map dots: (story num, x, y, region)
DOTS = [
    (1, 470, 668, "GLOBAL"), (2, 498, 682, "EUROPE"),
    (3, 700, 700, "ASIA-PACIFIC"), (4, 578, 694, "MIDDLE EAST"),
    (5, 420, 726, "GLOBAL"), (6, 545, 668, "EUROPE"),
    (7, 868, 672, "ASIA-PACIFIC"), (8, 255, 712, "AMERICAS"),
    (9, 838, 690, "ASIA-PACIFIC"), (10, 882, 724, "OCEANIA"),
    (11, 150, 678, "AMERICAS"), (12, 172, 694, "AMERICAS"),
    (13, 548, 690, "MIDDLE EAST"),
]

# ---------------------------------------------------------------- helpers
def wrap(text, fnt, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = (cur + " " + word).strip()
        if fnt.getlength(trial) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def vgrad(size, c1, c2):
    w, h = size
    g = Image.new("RGB", (1, h))
    px = g.load()
    for y in range(h):
        t = y / max(1, h - 1)
        px[0, y] = tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))
    return g.resize((w, h))


def rrect(d, box, rad, fill=None, outline=None, width=1):
    d.rounded_rectangle(box, radius=rad, fill=fill, outline=outline, width=width)


def _fit_checks():
    """Assert every text block fits its box before any drawing."""
    assert len(HEROES) + len(MIDS) + len(BRIEFS) == 35, "story count != 35"
    assert sum(n for _, n in REGIONS) == 35, "region total != 35"
    f = font(True, 40)
    assert f.getlength("THE WORLD IN ONE DAY") <= 700, "masthead too wide"
    f = font(True, 11)
    utc_total = sum(f.getlength(c) + 12 for c in UTC_CHIPS) + 5 * 6
    assert utc_total <= 875, f"UTC chips total too wide: {utc_total:.0f}px"
    f = font(True, 22)
    for num, _lbl in NUMBERS:
        assert f.getlength(num) <= 148, f"number too wide: {num}"
    f = font(True, 11)
    for name, n in REGIONS:
        assert f.getlength(f"{name} {n}") <= 124, f"tab too wide: {name}"
    fh, fd, fs = font(True, 20), font(False, 12), font(False, 10)
    for h in HEROES:
        assert fh.getlength(h["headline"]) <= 306, f"hero head: {h['headline']}"
        dl = wrap(h["deck"], fd, 306)
        assert len(dl) <= 2, f"hero deck >2 lines: {h['headline']}"
        assert fs.getlength(h["source"]) <= 200, "hero source too wide"
    mh, md, ms = font(True, 14), font(False, 12), font(False, 10)
    for m in MIDS:
        assert mh.getlength(m["headline"]) <= 380, f"mid head: {m['headline']}"
        dl = wrap(m["deck"], md, 424)
        assert len(dl) <= 2, f"mid deck >2 lines: {m['headline']}"
        assert ms.getlength(m["source"]) <= 120, "mid source too wide"
    bn, bt, bs = font(True, 13), font(False, 13), font(False, 13)
    for num, head, src, reg in BRIEFS:
        line = f"{num}. {head} — {src} ({reg})"
        w = bn.getlength(f"{num}. ") + bt.getlength(head) + bs.getlength(f" — {src} ({reg})")
        assert w <= 472, f"brief too wide ({w:.0f}px): {line}"
    f = font(False, 11)
    assert f.getlength(DATE_L1) <= 950, "DATE CHECK line 1 too wide"
    assert f.getlength(DATE_L2) <= 950, "DATE CHECK line 2 too wide"


# ---------------------------------------------------------------- hero art
def art_summit(img, x, y, w, h):
    d = ImageDraw.Draw(img)
    img.paste(vgrad((w, h), (16, 34, 68), (44, 66, 118)), (x, y))
    # three small flags on poles, top area
    for i, kind in enumerate(["stripes", "red", "tricolour"]):
        fx = x + 52 + i * 96
        fy = y + 8
        d.line([(fx, fy), (fx, fy + 26)], fill=GOLD_LT, width=2)
        if kind == "stripes":
            for s in range(4):
                d.rectangle([fx + 2, fy + s * 4, fx + 26, fy + s * 4 + 2],
                            fill=(200, 40, 40) if s % 2 == 0 else WHITE)
            d.rectangle([fx + 2, fy, fx + 12, fy + 7], fill=(30, 60, 140))
        elif kind == "red":
            d.rectangle([fx + 2, fy, fx + 26, fy + 16], fill=(200, 30, 30))
            for sx, sy in [(8, 4), (14, 6), (18, 10)]:
                d.ellipse([fx + sx, fy + sy, fx + sx + 3, fy + sy + 3],
                          fill=(250, 220, 80))
        else:
            for s, c in enumerate([(255, 255, 255), (40, 90, 200), (200, 40, 40)]):
                d.rectangle([fx + 2, fy + s * 5, fx + 26, fy + s * 5 + 5], fill=c)
    # three generic suited figures, BIG heads, no specific likeness
    skins = [(232, 190, 150), (205, 165, 125), (188, 148, 118)]
    suits = [(18, 18, 30), (28, 28, 44), (14, 24, 40)]
    ties = [GOLD, (200, 50, 50), (70, 120, 220)]
    for i in range(3):
        cx = x + 56 + i * 100
        hy = y + 34
        d.ellipse([cx - 14, hy, cx + 14, hy + 28], fill=skins[i])
        # minimal face features so the face reads at full-image size
        d.ellipse([cx - 6, hy + 10, cx - 3, hy + 13], fill=(40, 30, 25))
        d.ellipse([cx + 3, hy + 10, cx + 6, hy + 13], fill=(40, 30, 25))
        d.line([(cx - 3, hy + 20), (cx + 3, hy + 20)], fill=(120, 70, 55), width=2)
        d.polygon([(cx - 26, y + h - 6), (cx + 26, y + h - 6),
                   (cx + 18, hy + 28), (cx - 18, hy + 28)], fill=suits[i])
        d.polygon([(cx - 4, hy + 28), (cx + 4, hy + 28),
                   (cx, hy + 42)], fill=ties[i])
    # gold podium bar
    d.rectangle([x, y + h - 8, x + w, y + h], fill=GOLD)


def art_bridge(img, x, y, w, h):
    d = ImageDraw.Draw(img)
    img.paste(vgrad((w, h), (88, 38, 108), (205, 90, 45)), (x, y))
    # sun, upper right, clear of the top-left number badge
    sx, sy = x + w - 42, y + 16
    d.ellipse([sx - 15, sy - 15, sx + 15, sy + 15], fill=(255, 226, 140))
    d.ellipse([sx - 20, sy - 20, sx + 20, sy + 20], outline=(255, 226, 140), width=2)
    # layered smoke (several thin ellipses, not one blob)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for ox, oy, rw, rh, a in [(36, 24, 78, 16, 130), (68, 15, 88, 14, 150),
                              (102, 26, 78, 15, 140), (128, 13, 66, 13, 160)]:
        ld.ellipse([ox, oy, ox + rw, oy + rh], fill=(150, 130, 165, a))
    img.paste(layer, (x, y), layer)
    # bridge silhouette: deck, towers, cables
    dy = y + 58
    d.line([(x, dy), (x + w, dy)], fill=(20, 14, 30), width=4)
    for tx in (x + 78, x + 210):
        d.line([(tx, dy), (tx, y + 30)], fill=(20, 14, 30), width=5)
    for cx0, cx1 in [(x, x + 78), (x + 78, x + 210), (x + 210, x + w)]:
        d.arc([cx0, dy - 26, cx1, dy + 6], 180, 360, fill=(20, 14, 30), width=2)
    # water band + reflections
    d.rectangle([x, dy + 4, x + w, y + h], fill=(16, 20, 48))
    for rx in range(0, w, 26):
        d.line([(x + rx, dy + 10), (x + rx + 14, dy + 10)],
               fill=(230, 140, 60), width=2)


def art_cyclone(img, x, y, w, h):
    d = ImageDraw.Draw(img)
    img.paste(vgrad((w, h), (6, 24, 60), (10, 48, 98)), (x, y))
    # radar rings, right side
    cx, cy = x + w - 88, y + 38
    for r, col in [(48, (0, 200, 220)), (36, (0, 220, 160)),
                   (24, (120, 255, 120)), (12, (220, 255, 120))]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=2)
    d.arc([cx - 48, cy - 48, cx + 48, cy + 48], 200, 340, fill=(0, 220, 160), width=3)
    d.arc([cx - 36, cy - 36, cx + 36, cy + 36], 20, 160, fill=(120, 255, 120), width=3)
    # diagonal rain, left half
    for i in range(14):
        rx = x + 8 + i * 16
        ry = y + 6 + (i % 4) * 12
        d.line([(rx, ry), (rx - 7, ry + 16)], fill=(120, 200, 255), width=2)
    # rescue boat, bottom-left
    bx, by = x + 34, y + h - 26
    d.polygon([(bx, by), (bx + 64, by), (bx + 54, by + 12), (bx + 8, by + 12)],
              fill=(235, 120, 40))
    d.rectangle([bx + 20, by - 10, bx + 40, by], fill=WHITE)
    d.ellipse([bx + 26, by - 18, bx + 34, by - 10], fill=(232, 190, 150))
    # label pill, bottom-right, fully clear of the boat
    lbl = "BAY OF BENGAL"
    f = font(True, 11)
    tw = f.getlength(lbl)
    px = x + w - tw - 22
    py = y + h - 22
    rrect(d, [px - 6, py - 4, px + tw + 8, py + 15], 8, fill=(8, 18, 44),
          outline=(0, 200, 220), width=1)
    d.text((px, py), lbl, font=f, fill=WHITE)


ART = {"summit": art_summit, "bridge": art_bridge, "cyclone": art_cyclone}


# ---------------------------------------------------------------- build
def build():
    _fit_checks()
    img = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(img)

    y = 0
    # ---- masthead (0-64)
    d.text((M + 8, 8), "THE WORLD IN ONE DAY", font=font(True, 36), fill=WHITE)
    f35 = font(True, 20)
    t = "35 STORIES"
    d.text((W - M - 8 - f35.getlength(t), 10), t, font=f35, fill=GOLD)
    d.text((M + 8, 48), "Friday, 20 November 2026", font=font(False, 13), fill=MUTED)
    fsub = font(False, 11)
    sub = "ONE PICTURE · EVERY STORY THAT MATTERED"
    d.text((W - M - 8 - fsub.getlength(sub), 50), sub, font=fsub, fill=MUTED_DK)
    y = 64
    # ---- colour bar (64-70)
    seg = CW // 6
    for i, c in enumerate(BAR6):
        x0 = M + i * seg
        x1 = M + (i + 1) * seg if i < 5 else W - M
        d.rectangle([x0, y, x1, y + 6], fill=c)
    y = 72
    # ---- UTC strip (72-102): variable-width chips, centred after the label
    d.text((M, y + 8), "THE DAY IN UTC", font=font(True, 12), fill=GOLD)
    f = font(True, 11)
    widths = [f.getlength(c) + 12 for c in UTC_CHIPS]
    total = sum(widths) + 5 * 6
    cx = M + 132 + (875 - total) // 2
    for c, cw in zip(UTC_CHIPS, widths):
        rrect(d, [cx, y + 2, cx + cw, y + 28], 7, fill=CHIP, outline=CHIP_LINE, width=1)
        d.text((cx + 6, y + 9), c, font=f, fill=INK)
        cx += cw + 6
    y = 104
    # ---- number strip (104-158)
    nw, ngap = 160, 6
    nx = M + 1
    for num, lbl in NUMBERS:
        rrect(d, [nx, y, nx + nw, y + 54], 8, fill=CHIP, outline=CHIP_LINE, width=1)
        fn = font(True, 22)
        d.text((nx + (nw - fn.getlength(num)) / 2, y + 5), num, font=fn, fill=WHITE)
        fl = font(False, 10)
        d.text((nx + (nw - fl.getlength(lbl)) / 2, y + 34), lbl, font=fl, fill=NEON)
        nx += nw + ngap
    y = 160
    # ---- region tabs (160-186)
    tw, tgap = 136, 6
    tx = M + 2
    for name, n in REGIONS:
        rrect(d, [tx, y, tx + tw, y + 26], 7, fill=PANEL2, outline=CHIP_LINE, width=1)
        f = font(True, 11)
        s = f"{name} {n}"
        d.text((tx + (tw - f.getlength(s)) / 2, y + 6), s, font=f, fill=INK)
        tx += tw + tgap
    y = 188
    # ---- heroes (188-348), three columns
    hw, hgap = 322, 14
    hx = M
    for hero in HEROES:
        rrect(d, [hx, y, hx + hw, y + 160], 8, fill=PANEL, outline=CHIP_LINE, width=1)
        ART[hero["art"]](img, hx + 1, y + 1, hw - 2, 82)
        # number badge, top-left of the art
        bx, by = hx + 12, y + 10
        d.ellipse([bx - 15, by - 15, bx + 15, by + 15], fill=GOLD,
                  outline=(255, 255, 255), width=2)
        fb = font(True, 16)
        s = str(hero["num"])
        d.text((bx - fb.getlength(s) / 2, by - 11), s, font=fb, fill=DARKTXT)
        d.text((hx + 10, y + 88), hero["headline"], font=font(True, 20), fill=WHITE)
        lines = wrap(hero["deck"], font(False, 12), 306)
        ly = y + 114
        for ln in lines[:2]:
            d.text((hx + 10, ly), ln, font=font(False, 12), fill=INK)
            ly += 15
        d.text((hx + 10, y + 146), hero["source"] + "  ·  " + hero["region"],
               font=font(False, 10), fill=GOLD_LT)
        hx += hw + hgap
    y = 350
    # ---- mid cards (350-640): 2 cols x 5 rows, 54 tall, gap 5
    mw, mgap = 488, 16
    for row in range(5):
        for col in range(2):
            m = MIDS[row * 2 + col]
            x0 = M + col * (mw + mgap)
            y0 = y + row * 59
            fill = TINT_A if (row + col) % 2 == 0 else TINT_B
            rrect(d, [x0, y0, x0 + mw, y0 + 54], 7, fill=fill)
            # badge
            bcx, bcy = x0 + 24, y0 + 27
            d.ellipse([bcx - 13, bcy - 13, bcx + 13, bcy + 13], fill=DARKTXT)
            fb = font(True, 12)
            s = str(m["num"])
            d.text((bcx - fb.getlength(s) / 2, bcy - 8), s, font=fb, fill=WHITE)
            # headline + source on one line
            d.text((x0 + 44, y0 + 6), m["headline"], font=font(True, 14), fill=DARKTXT)
            fs = font(False, 10)
            d.text((x0 + mw - 8 - fs.getlength(m["source"]), y0 + 8),
                   m["source"], font=fs, fill=DARKMUT)
            # deck, max 2 lines
            lines = wrap(m["deck"], font(False, 12), 424)
            ly = y0 + 24
            for ln in lines[:2]:
                d.text((x0 + 44, ly), ln, font=font(False, 12), fill=(40, 55, 85))
                ly += 13
    y = 642
    # ---- map panel (642-762)
    rrect(d, [M, y, W - M, y + 120], 8, fill=PANEL, outline=CHIP_LINE, width=1)
    d.text((M + 10, y + 6), "WHERE IT HAPPENED — 13 STORIES MAPPED",
           font=font(True, 11), fill=GOLD)
    continents = [
        [(70, 670), (150, 660), (235, 664), (268, 686), (240, 702),
         (190, 700), (130, 712), (72, 696)],
        [(232, 706), (282, 708), (300, 726), (272, 740), (238, 728)],
        [(458, 668), (500, 662), (522, 676), (492, 690), (460, 684)],
        [(458, 694), (520, 690), (560, 706), (542, 732), (492, 736), (462, 716)],
        [(532, 664), (700, 656), (900, 668), (948, 690), (882, 716),
         (748, 722), (648, 706), (560, 688)],
    ]
    for poly in continents:
        d.polygon(poly, fill=(30, 54, 100), outline=(52, 84, 146))
    d.ellipse([292, 662, 318, 674], fill=(30, 54, 100), outline=(52, 84, 146))
    d.ellipse([797, 714, 867, 734], fill=(30, 54, 100), outline=(52, 84, 146))
    for num, dx, dy, reg in DOTS:
        col = REGION_COLOR[reg]
        d.ellipse([dx - 9, dy - 9, dx + 9, dy + 9], fill=col, outline=WHITE, width=1)
        fb = font(True, 9)
        s = str(num)
        d.text((dx - fb.getlength(s) / 2, dy - 6), s, font=fb, fill=WHITE,
               stroke_width=1, stroke_fill=(10, 22, 48))
    d.text((M + 10, y + 100), "HOW SURE ARE WE?   ● REPORTED   ● CLAIM   ● FORECAST",
           font=font(False, 10), fill=MUTED)
    y = 764
    # ---- briefs panel (764-956): header + 11 rows x 2 columns
    d.text((M, y), "THE REST OF THE DAY — 22 MORE STORIES",
           font=font(True, 12), fill=GOLD)
    bn, bt, bs = font(True, 13), font(False, 13), font(False, 13)
    for i, (num, head, src, reg) in enumerate(BRIEFS):
        col = i // 11
        row = i % 11
        bx = M + col * 496
        by = y + 18 + row * 16
        d.text((bx, by), f"{num}. ", font=bn, fill=GOLD)
        nx = bx + bn.getlength(f"{num}. ")
        d.text((nx, by), head, font=bt, fill=INK)
        d.text((nx + bt.getlength(head), by), f" — {src} ({reg})",
               font=bs, fill=MUTED)
    y = 958
    # ---- DATE CHECK (958-996)
    rrect(d, [M, y, W - M, y + 38], 6, fill=RED, outline=(220, 90, 90), width=1)
    d.text((M + 10, y + 5), DATE_L1, font=font(True, 11), fill=WHITE)
    d.text((M + 10, y + 21), DATE_L2, font=font(False, 11), fill=(255, 220, 210))
    y = 998
    # ---- footer (998-1018)
    ff = font(False, 10)
    d.text(((W - ff.getlength(FOOTER)) / 2, y + 4), FOOTER, font=ff, fill=MUTED_DK)
    # ---- gold frame
    d.rectangle([1, 1, W - 2, H - 2], outline=GOLD, width=3)
    assert y + 20 <= H, f"layout overflow: {y + 20}"
    return img


def main():
    img = build()
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    img.save(out, format="PNG", optimize=True)
    data = open(out, "rb").read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "not a PNG"
    assert img.size == (1024, 1024), f"size {img.size}"
    assert len(data) <= 1024 * 1024, f"{len(data)} bytes > 1 MiB"
    print("entry.png", img.size, img.mode, len(data), "bytes")
    print("sha256", hashlib.sha256(data).hexdigest())


if __name__ == "__main__":
    main()
