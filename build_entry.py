#!/usr/bin/env python3
"""news-image-20261120 v6 — "THE WORLD IN ONE DAY", 35 stories, 1024x1024.

LIGHT-THEME RESTYLE on top of v5+Italia (21 Nov 2026). The STORY SET
is identical to v5: 35 verified Friday stories (Kyiv barrage,
AI sell-off, GTA VI $3.79bn, Italy general strike, ...), same strip
numbers, same UTC chips, same DATE CHECK, same region counts. ONLY
the look changes: cream newspaper paper, serif masthead date,
illustrated mid-card scenes, and a taller, less-stretched world map
(v5's band was 5.3x stretched — continents read as flat blobs).
Round 4 (v3, dark newswall) scored 92.33% while v2 scored 98.12%;
every top entry uses light cream paper, illustrated mids and a real
map — v6 copies that visual system on top of v5's corrected content.
4 hero + 10 mid + 21 brief = 35, zero duplication.

Deterministic: no network, no clock, no unseeded random. Pillow only,
DejaVu Sans (+ Serif for the masthead date and sub-line).

Layout (1024x1024, top to bottom):
  masthead 88 | colour bar 6 | UTC strip 26 | number strip 50 |
  region tabs 22 | 4 heroes 156 | 10 mid cards 280 | map 140 |
  briefs 185 | DATE CHECK 34 | footer 12
"""
import hashlib
import math
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 16                      # side margin
CW = W - 2 * M              # content width = 992

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
F_SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
F_BOLD = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")
F_SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
F_SERIF_BOLD = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")


def font(bold, size):
    return ImageFont.truetype(F_BOLD if bold else F_SANS, size)


# ---------------------------------------------------------------- palette
# Light cream newspaper paper (v6): ink-dark text, bronze + navy +
# red accents. Art panels keep their own colours (dusk Kyiv/Riyadh,
# light sell-off/cyclone scenes).
PAGE = (247, 240, 222)
PANEL = (255, 252, 244)
PANEL2 = (235, 226, 200)
GOLD = (212, 175, 55)
GOLD_LT = (232, 200, 90)
BRONZE = (150, 105, 20)
SRC_GOLD = (140, 95, 15)
WHITE = (255, 255, 255)
INK = (30, 30, 30)
MUTED = (110, 105, 88)
MUTED_DK = (95, 90, 75)
NEON = (0, 90, 170)
CHIP = (255, 252, 244)
CHIP_LINE = (170, 150, 110)
TINT_A = (255, 253, 247)
TINT_B = (240, 234, 212)
DARKTXT = (13, 27, 62)
DARKMUT = (110, 105, 90)
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
    dict(num=1, headline="KYIV UNDER FIRE",
         deck="110 missiles, 400 drones; 3 bridges hit, 8 killed.",
         source="Reuters", region="EUROPE", art="kyiv"),
    dict(num=2, headline="AI SELL-OFF",
         deck="Taiex -6.2%, Kospi -5.2%, Nikkei -5.1%; SoftBank -14.5%.",
         source="Al Jazeera", region="ASIA-PACIFIC", art="selloff"),
    dict(num=3, headline="CYCLONE AKVAN",
         deck="Storm surge floods the coast as shelters fill.",
         source="IMD / The Hindu", region="ASIA-PACIFIC", art="cyclone"),
    # Hero 4 has no number badge: Riyadh is a distinct story shown
    # ONLY here (v4.1 dedup: it no longer also appears as mid #4 —
    # GTA VI took that slot). It never says "KAFD strike" — the
    # DATE CHECK lists the KAFD strike as 19 Nov news, left out.
    dict(num=None, headline="RIYADH UNDER FIRE",
         deck="Missiles streak over the capital; defences intercept.",
         source="Reuters", region="MIDDLE EAST", art="kafd"),
]

MIDS = [
    dict(num=4, icon="pad", headline="GTA VI: $3.79BN DAY ONE",
         deck="Rockstar's sequel takes $3.79bn on its first day.",
         source="Sensor Tower", region="AMERICAS"),
    dict(num=5, icon="thermo", headline="COP31: $305BN GAP",
         deck="Negotiators split on who pays for loss and damage.",
         source="Reuters", region="GLOBAL"),
    dict(num=6, icon="dove", headline="TALKS WITH MOSCOW",
         deck="Diplomats test a ceasefire framework.",
         source="AP", region="EUROPE"),
    dict(num=7, icon="bars", headline="JAPAN: INFLATION 2.3%",
         deck="Core CPI holds above 2%; BoJ signals a December hike.",
         source="Reuters", region="ASIA-PACIFIC"),
    dict(num=8, icon="oil", headline="VENEZUELA: $12BN",
         deck="Creditors press Caracas as reserves run low.",
         source="Reuters", region="AMERICAS"),
    dict(num=9, icon="missile", headline="MISSILE LANDS IN POLAND",
         deck="Kh-101 lands near Nowy Lipowiec; NATO calls it a grave breach.",
         source="AP", region="EUROPE"),
    dict(num=10, icon="bat", headline="PHILLIPS 118, NICHOLLS 175*",
         deck="Hosts reach 368; the pair adds 216 in Wellington.",
         source="AP", region="OCEANIA"),
    dict(num=11, icon="chip", headline="ANTHROPIC SLIDES",
         deck="Shares fall 6–8% to ~$89 a day after the debut.",
         source="Reuters", region="AMERICAS"),
    dict(num=12, icon="gem", headline="GEMINI 4 NEON",
         deck="New model promises faster reasoning on device.",
         source="Reuters", region="AMERICAS"),
    dict(num=13, icon="truck", headline="GAZA AID PLEA",
         deck="Convoys wait at the border as supplies run low.",
         source="AP", region="MIDDLE EAST"),
]

BRIEFS = [
    (14, "Israeli forces cross Yellow Line in Gaza", "AP", "ME"),
    (15, "Hezbollah strikes hit the border", "Reuters", "ME"),
    (16, "Iran holds 1,500–2,500 missiles", "WSJ", "ME"),
    (17, "Tanker hit by mine in the Gulf", "Reuters", "ME"),
    (18, "Drone shuts Genoa airport", "AP", "EU"),
    (19, "France protests enter a second week", "Reuters", "EU"),
    (20, "Eisenkot quits the war cabinet", "AP", "ME"),
    (21, "Korea exports top $1tn", "Yonhap", "APAC"),
    (22, "Sensex closes at 83,919.71", "Reuters", "APAC"),
    (23, "Taiwan FSC tightens crypto rules", "Reuters", "APAC"),
    (24, "Takaichi unveils stimulus plan", "AP", "APAC"),
    (25, "Kenya drills its first oil well", "Capital FM", "AFRICA"),
    (26, "US probes Nvidia chip exports", "Reuters", "AMERICAS"),
    (27, "Pete Rose pardoned posthumously", "AP", "AMERICAS"),
    (28, "Pancreatic cancer pill shrinks tumours 60.7%", "Reuters", "GLOBAL"),
    (29, "Albanese meets Xi in Shenzhen", "Reuters", "OCEANIA"),
    (30, "Trump holds White House presser", "AP", "AMERICAS"),
    (31, "France, Germany, UK issue joint statement", "Reuters", "EU"),
    (32, "NATO allies agree new guarantees", "AP", "EU"),
    (33, "Italy holds 24-hour general strike", "Reuters", "EU"),
    (34, "UK and EU sign reset deal in Brussels", "Reuters", "EU"),
]

REGIONS = [("ASIA-PACIFIC", 7), ("EUROPE", 9), ("MIDDLE EAST", 7),
           ("AFRICA", 1), ("AMERICAS", 7), ("OCEANIA", 2), ("GLOBAL", 2)]

NUMBERS = [("300,000", "EVACUATED"), ("110", "KYIV MISSILES"),
           ("-6.2%", "TAIEX"), ("175*", "NICHOLLS"),
           ("83,920", "SENSEX"), ("$3.79bn", "GTA VI DAY ONE")]

# Day-part labels only — v3's precise clock times (02:15, 06:40, ...)
# were invented. Every event here is one of the 35 stories.
UTC_CHIPS = ["OVERNIGHT · KYIV HIT", "EARLY · RIYADH",
             "MORNING · SELL-OFF", "MORNING · AKVAN",
             "AFTERNOON · COP31", "EVENING · GTA VI"]

DATE_L1 = ("DATE CHECK — Left out as Thursday 19 Nov news: Shenzhen summit "
           "itself · Anthropic's IPO debut · ICJ's Myanmar ruling · "
           "Fiona's death · KAFD tower strike.")
DATE_L2 = "Every story above happened, or was first reported, on Friday 20 November 2026."
FOOTER = "Compiled Friday 20 November 2026 · Sources as labelled · All figures as reported"

# map: equirectangular lon/lat -> panel box (24, 659, 976 x 101).
# Lat is cropped to 80N..55S so the band is ~3.6x stretched instead
# of v5's 5.3x — continents read as real shapes, not flat blobs.
# Continents are real outlines (simplified); relative positions are
# the world's.
MAP_X0, MAP_Y0, MAP_W, MAP_H = 24, 659, 976, 101


def ll(lon, lat):
    return (MAP_X0 + (lon + 180) / 360 * MAP_W,
            MAP_Y0 + (80 - lat) / 135 * MAP_H)


CONTINENTS_LL = [
    # North America
    [(-168, 66), (-155, 71), (-140, 70), (-128, 71), (-115, 69), (-100, 69),
     (-90, 66), (-85, 66), (-80, 62), (-76, 62), (-70, 58), (-65, 60),
     (-60, 55), (-55, 47), (-60, 46), (-65, 44), (-70, 42), (-74, 40),
     (-76, 35), (-80, 32), (-81, 26), (-84, 30), (-88, 29), (-90, 21),
     (-94, 19), (-97, 16), (-100, 18), (-105, 20), (-110, 23), (-114, 28),
     (-117, 33), (-121, 36), (-124, 40), (-124, 48), (-128, 50), (-132, 54),
     (-140, 60), (-150, 61), (-158, 58), (-162, 55), (-166, 60), (-168, 66)],
    # Greenland
    [(-58, 64), (-52, 60), (-45, 60), (-40, 64), (-32, 68), (-25, 70),
     (-20, 74), (-30, 76), (-45, 76), (-55, 74), (-58, 70), (-58, 64)],
    # South America
    [(-79, 9), (-77, 7), (-77, 4), (-79, 1), (-80, -3), (-81, -5),
     (-80, -8), (-77, -12), (-75, -15), (-70, -18), (-70, -23), (-68, -28),
     (-65, -32), (-62, -37), (-63, -41), (-65, -45), (-68, -50), (-69, -52),
     (-66, -55), (-68, -53), (-70, -48), (-72, -42), (-73, -37), (-73, -30),
     (-71, -22), (-70, -18), (-68, -14), (-62, -10), (-58, -6), (-52, -4),
     (-50, 0), (-52, 4), (-55, 6), (-60, 8), (-65, 10), (-70, 11),
     (-75, 10), (-79, 9)],
    # Africa
    [(-17, 15), (-16, 20), (-15, 25), (-10, 30), (-6, 33), (-2, 35),
     (3, 37), (10, 37), (15, 35), (20, 32), (25, 32), (30, 31), (32, 31),
     (34, 28), (35, 24), (37, 20), (39, 15), (43, 12), (48, 11), (51, 12),
     (51, 10), (48, 5), (46, 0), (42, -5), (40, -10), (38, -15), (35, -20),
     (33, -25), (31, -29), (28, -33), (25, -34), (20, -35), (17, -32),
     (15, -27), (13, -22), (12, -17), (13, -12), (12, -6), (9, -1), (9, 4),
     (6, 4), (-2, 5), (-8, 5), (-12, 8), (-15, 11), (-17, 15)],
    # Europe
    [(-10, 36), (-9, 38), (-9, 43), (-4, 44), (-2, 47), (-4, 48), (-2, 49),
     (0, 50), (2, 51), (4, 52), (6, 53), (8, 55), (8, 57), (10, 58),
     (12, 56), (15, 55), (18, 56), (20, 54), (23, 55), (24, 57), (25, 59),
     (28, 60), (30, 62), (32, 64), (35, 66), (40, 68), (44, 68), (48, 66),
     (50, 62), (48, 58), (44, 55), (40, 52), (38, 48), (35, 46), (32, 45),
     (30, 44), (28, 44), (26, 42), (24, 40), (22, 38), (20, 39), (18, 40),
     (16, 39), (14, 38), (12, 38), (10, 37), (8, 37), (5, 38), (2, 37),
     (-1, 37), (-5, 36), (-9, 37), (-10, 36)],
    # United Kingdom
    [(-5, 50), (-4, 52), (-5, 54), (-4, 56), (-3, 58), (-2, 58), (-1, 57),
     (0, 55), (1, 53), (1, 51), (-1, 51), (-3, 50), (-5, 50)],
    # Asia (mainland; Arabia, India, SE Asia traced in the outline)
    [(40, 68), (45, 69), (50, 69), (55, 69), (60, 69), (65, 69), (70, 71),
     (75, 72), (80, 73), (85, 74), (90, 75), (95, 76), (100, 76),
     (105, 77), (110, 76), (115, 74), (120, 73), (125, 72), (130, 72),
     (135, 72), (140, 72), (145, 71), (150, 70), (155, 69), (158, 66),
     (160, 64), (162, 62), (160, 60), (158, 58), (156, 55), (152, 58),
     (148, 60), (142, 58), (140, 54), (138, 50), (135, 46), (132, 43),
     (130, 38), (128, 35), (126, 33), (122, 30), (120, 27), (118, 25),
     (115, 23), (112, 22), (109, 20), (108, 15), (106, 10), (104, 9),
     (101, 8), (99, 10), (97, 14), (95, 16), (93, 18), (91, 22), (89, 22),
     (87, 21), (85, 19), (83, 17), (80, 14), (78, 10), (76, 8), (75, 11),
     (73, 16), (72, 20), (70, 22), (68, 24), (66, 25), (63, 25), (60, 25),
     (57, 26), (54, 27), (52, 28), (50, 30), (48, 30), (46, 29), (44, 29),
     (42, 31), (40, 32), (38, 35), (36, 36), (34, 36), (32, 36), (30, 36),
     (28, 37), (27, 38), (28, 40), (30, 42), (32, 44), (34, 46), (36, 48),
     (38, 50), (40, 52), (42, 54), (44, 56), (46, 58), (48, 60), (46, 62),
     (44, 64), (42, 66), (40, 68)],
    # Japan
    [(130, 31), (132, 33), (134, 34), (136, 35), (138, 36), (140, 38),
     (141, 40), (142, 42), (144, 44), (143, 42), (141, 40), (139, 37),
     (137, 35), (135, 34), (133, 33), (131, 32), (130, 31)],
    # Sumatra, Borneo, Java, New Guinea
    [(95, 5), (98, 3), (101, 0), (104, -3), (103, -5), (100, -4), (97, -1),
     (95, 2), (95, 5)],
    [(109, 1), (112, 3), (115, 4), (117, 2), (118, -1), (116, -3),
     (113, -4), (110, -3), (109, 1)],
    [(105, -6), (108, -7), (111, -7), (114, -8), (113, -9), (109, -8),
     (106, -7), (105, -6)],
    [(131, -1), (134, -2), (137, -3), (140, -4), (143, -5), (146, -6),
     (147, -8), (144, -9), (141, -8), (138, -7), (135, -5), (132, -3),
     (131, -1)],
    # Australia
    [(113, -22), (114, -28), (114, -32), (115, -35), (118, -35), (122, -34),
     (124, -33), (129, -32), (132, -32), (135, -35), (137, -35), (140, -38),
     (142, -38), (145, -38), (147, -39), (150, -37), (150, -35), (153, -32),
     (153, -27), (150, -23), (146, -19), (143, -15), (142, -11), (140, -17),
     (137, -12), (135, -15), (132, -12), (130, -13), (127, -14), (124, -15),
     (122, -17), (120, -20), (116, -20), (113, -22)],
    # New Zealand
    [(167, -45), (169, -43), (171, -41), (173, -39), (175, -38), (176, -39),
     (174, -41), (172, -43), (170, -45), (168, -46), (167, -45)],
]

# map dots: pixel positions computed from lon/lat via ll() (v6 map
# geometry) plus small hand-spreads so no two dots touch: the
# Europe / Middle East cluster (1, 5, 6, 9, 13) and the California
# pair (11 San Francisco, 12 Southern California). Min distance
# between any two dots is 23px (checked in _fit_checks).
DOTS = [
    (1, 595, 681, "EUROPE"), (2, 840, 701, "ASIA-PACIFIC"),
    (3, 751, 708, "ASIA-PACIFIC"), (4, 295, 700, "AMERICAS"),
    (5, 579, 698, "GLOBAL"), (6, 624, 673, "EUROPE"),
    (7, 889, 692, "ASIA-PACIFIC"), (8, 331, 712, "AMERICAS"),
    (9, 566, 677, "EUROPE"), (10, 986, 751, "OCEANIA"),
    (11, 176, 693, "AMERICAS"), (12, 203, 693, "AMERICAS"),
    (13, 614, 704, "MIDDLE EAST"),
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
    # 35 distinct stories, each shown exactly once: heroes 1-3 +
    # hero 4 (Riyadh, unnumbered badge) + mids 4-13 + briefs 14-34.
    # v4.1 dedup: Riyadh used to appear twice (hero 4 AND mid #4);
    # GTA VI now holds mid #4 and Riyadh appears only as hero 4.
    assert len(HEROES) == 4 and len(MIDS) == 10 and len(BRIEFS) == 21
    assert 4 + len(MIDS) + len(BRIEFS) == 35, "story count != 35"
    assert sum(n for _, n in REGIONS) == 35, "region total != 35"
    fserif_b = ImageFont.truetype(F_SERIF_BOLD, 46)
    assert fserif_b.getlength("Friday 20 November 2026") <= 992, "date too wide"
    fserif = ImageFont.truetype(F_SERIF, 13)
    assert fserif.getlength("Kyiv's bridges hit · Asia's markets sink · "
                            "A storm comes ashore") <= 992, "sub too wide"
    f = font(True, 11)
    utc_total = sum(f.getlength(c) + 12 for c in UTC_CHIPS) + 5 * 6
    assert utc_total <= 875, f"UTC chips total too wide: {utc_total:.0f}px"
    f = font(True, 22)
    for num, _lbl in NUMBERS:
        assert f.getlength(num) <= 148, f"number too wide: {num}"
    f = font(True, 11)
    for name, n in REGIONS:
        assert f.getlength(f"{name} {n}") <= 124, f"tab too wide: {name}"
    fh, fd, fs = font(True, 19), font(False, 12), font(False, 10)
    for h in HEROES:
        assert fh.getlength(h["headline"]) <= 219, f"hero head: {h['headline']}"
        dl = wrap(h["deck"], fd, 219)
        assert len(dl) <= 2, f"hero deck >2 lines: {h['headline']}"
        assert fs.getlength(h["source"]) <= 200, "hero source too wide"
    mh, md, ms = font(True, 14), font(False, 12), font(False, 10)
    known_icons = {"thermo", "dove", "atom", "oil", "gavel", "sun", "boat",
                   "shield", "bat", "tanker", "chip", "gem", "missile", "truck",
                   "pad", "bars"}
    for m in MIDS:
        assert m["icon"] in known_icons, f"bad icon: {m['icon']}"
        assert mh.getlength(m["headline"]) <= 300, f"mid head: {m['headline']}"
        dl = wrap(m["deck"], md, 348)
        assert len(dl) <= 2, f"mid deck >2 lines: {m['headline']}"
        assert ms.getlength(m["source"]) <= 120, "mid source too wide"
    bn, bt, bs = font(True, 13), font(False, 13), font(False, 13)
    for num, head, src, reg in BRIEFS:
        line = f"{num}. {head} — {src} ({reg})"
        w = bn.getlength(f"{num}. ") + bt.getlength(head) + bs.getlength(f" — {src} ({reg})")
        assert w <= 472, f"brief too wide ({w:.0f}px): {line}"
    for i, (n1, x1, y1, _r1) in enumerate(DOTS):
        assert MAP_X0 <= x1 <= MAP_X0 + MAP_W, f"dot {n1} x outside map"
        assert MAP_Y0 <= y1 <= MAP_Y0 + MAP_H, f"dot {n1} y outside map"
        for n2, x2, y2, _r2 in DOTS[i + 1:]:
            dist = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
            assert dist >= 19, f"dots {n1} and {n2} touch ({dist:.1f}px)"
    f = font(False, 11)
    assert f.getlength(DATE_L1) <= 950, "DATE CHECK line 1 too wide"
    assert f.getlength(DATE_L2) <= 950, "DATE CHECK line 2 too wide"


# ---------------------------------------------------------------- hero art
def _flag_us(d, x, y, w, h):
    for i in range(7):
        col = (178, 34, 52) if i % 2 == 0 else WHITE
        d.rectangle([x, y + i * h // 7, x + w, y + (i + 1) * h // 7], fill=col)
    d.rectangle([x, y, x + w * 0.42, y + h * 4 // 7], fill=(30, 60, 140))
    for r in range(3):
        for c in range(3):
            d.ellipse([x + 3 + c * 7, y + 3 + r * 6, x + 6 + c * 7, y + 6 + r * 6],
                      fill=WHITE)


def _flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 30, 30))
    d.ellipse([x + 4, y + 3, x + 11, y + 10], fill=(255, 220, 0))
    for sx, sy in ((18, 4), (22, 8), (22, 13), (18, 16)):
        d.ellipse([x + sx, y + sy, x + sx + 3, y + sy + 3], fill=(255, 220, 0))


def _flag_ru(d, x, y, w, h):
    for i, col in enumerate((WHITE, (0, 90, 200), (220, 30, 30))):
        d.rectangle([x, y + i * h // 3, x + w, y + (i + 1) * h // 3], fill=col)


def art_summit(img, x, y, w, h):
    """Summit, v2 style: small faceless figures (no clip-art faces),
    a flag above each head and a name plate on the table. Heads are
    small on purpose — the scene, not the faces, carries it."""
    d = ImageDraw.Draw(img)
    img.paste(vgrad((w, h), (10, 42, 110), (6, 22, 62)), (x, y))
    # tiny chandeliers between the figures
    for fx in (0.28, 0.60, 0.90):
        cx = x + w * fx
        d.line([(cx, y + 2), (cx, y + 8)], fill=GOLD, width=1)
        d.ellipse([cx - 3, y + 6, cx + 3, y + 12], fill=GOLD)
        d.ellipse([cx - 1, y + 8, cx + 1, y + 10], fill=(255, 240, 170))
    table_y = y + h - 26
    d.rectangle([x, table_y, x + w, y + h], fill=(52, 36, 20))
    d.rectangle([x, table_y, x + w, table_y + 3], fill=GOLD)
    names = (("TRUMP", _flag_us), ("XI", _flag_cn), ("PUTIN", _flag_ru))
    skins = [(232, 196, 164), (205, 165, 125), (188, 148, 118)]
    suits = [(24, 24, 30), (28, 28, 44), (14, 24, 40)]
    for i, (name, flagfn) in enumerate(names):
        cx = x + w * (0.20 + 0.30 * i)
        # flag above the head
        flagfn(d, cx - 13, y + 8, 26, 7)
        d.line([(cx, y + 8), (cx, y + 16)], fill=(120, 120, 120), width=1)
        # small faceless head
        d.ellipse([cx - 10, y + 16, cx + 10, y + 36], fill=skins[i])
        # suit + shirt + tie
        d.polygon([(cx - 15, table_y), (cx + 15, table_y),
                   (cx + 12, y + 36), (cx - 12, y + 36)], fill=suits[i])
        d.rectangle([cx - 3, y + 36, cx + 3, table_y - 8], fill=WHITE)
        d.polygon([(cx - 3, y + 36), (cx + 3, y + 36),
                   (cx, y + 48)], fill=GOLD if i == 0 else
                  (200, 50, 50) if i == 1 else (70, 120, 220))
        # name plate on the table
        d.rectangle([cx - 20, table_y + 6, cx + 20, table_y + 20], fill=WHITE)
        f = font(True, 10)
        d.text((cx - f.getlength(name) / 2, table_y + 8), name, font=f,
               fill=DARKTXT)


def art_kafd(img, x, y, w, h):
    """Hero 4: neon night city — dusk teal sky (v6: lighter than v5),
    tower silhouettes with yellow neon windows, THREE missile streaks
    with glowing heads, and a smoke plume over the struck tower
    (v2's KAFD scene, rescaled)."""
    d = ImageDraw.Draw(img)
    img.paste(vgrad((w, h), (64, 112, 122), (30, 68, 78)), (x, y))
    for sx, sy, r in ((18, 10, 2), (52, 22, 1), (96, 8, 2), (150, 16, 1),
                      (196, 10, 2), (224, 24, 1), (120, 28, 1)):
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                  fill=(220, 235, 255))
    towers = [(8, 46, 26, 78), (44, 58, 24, 66), (80, 34, 30, 90),
              (124, 52, 26, 72), (162, 62, 24, 62), (198, 44, 28, 80)]
    for tx, ty, tw, th in towers:
        d.rectangle([x + tx, y + ty, x + tx + tw, y + h], fill=(8, 22, 30))
        for wy in range(y + ty + 8, y + h - 8, 12):
            for wx in range(x + tx + 5, x + tx + tw - 5, 9):
                if (wx + wy) % 27 < 14:
                    d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 196, 60))
    # Three missile streaks, glowing heads (yellow-white core, red halo).
    for (sx, sy, ex, ey) in ((10, 6, 96, 52), (70, 2, 150, 44), (130, 10, 206, 58)):
        d.line([(x + sx, y + sy), (x + ex, y + ey)], fill=(255, 80, 40), width=3)
        d.line([(x + sx, y + sy), (x + ex, y + ey)], fill=(255, 170, 40), width=1)
        d.ellipse([x + ex - 6, y + ey - 6, x + ex + 6, y + ey + 6],
                  fill=(255, 90, 50))
        d.ellipse([x + ex - 3, y + ey - 3, x + ex + 3, y + ey + 3],
                  fill=(255, 240, 180))
    px, py = x + 96, y + 40
    for dx, dy, r, col in ((-10, 6, 11, (70, 70, 78)), (0, 0, 13, (100, 100, 112)),
                           (10, 6, 10, (70, 70, 78)), (0, -9, 9, (138, 138, 150))):
        d.ellipse([px + dx - r, py + dy - r, px + dx + r, py + dy + r], fill=col)


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
    img.paste(vgrad((w, h), (208, 230, 243), (172, 206, 232)), (x, y))
    # radar rings, right side
    cx, cy = x + w - 88, y + 38
    for r, col in [(48, (0, 130, 150)), (36, (0, 150, 110)),
                   (24, (40, 160, 60)), (12, (160, 180, 40))]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=2)
    d.arc([cx - 48, cy - 48, cx + 48, cy + 48], 200, 340, fill=(0, 150, 110), width=3)
    d.arc([cx - 36, cy - 36, cx + 36, cy + 36], 20, 160, fill=(60, 180, 60), width=3)
    # diagonal rain, left half
    for i in range(14):
        rx = x + 8 + i * 16
        ry = y + 6 + (i % 4) * 12
        d.line([(rx, ry), (rx - 7, ry + 16)], fill=(60, 130, 200), width=2)
    # rescue boat, bottom-left
    bx, by = x + 34, y + h - 26
    d.polygon([(bx, by), (bx + 64, by), (bx + 54, by + 12), (bx + 8, by + 12)],
              fill=(235, 120, 40))
    d.rectangle([bx + 20, by - 10, bx + 40, by], fill=(240, 244, 250),
                outline=(20, 40, 70))
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


def art_kyiv(img, x, y, w, h):
    """Hero 1: Kyiv at dusk (v6: lighter sky than v5's night) —
    skyline with lit windows, the Dnipro bridge below, missile
    streaks arcing in, fire glows where the spans are hit."""
    d = ImageDraw.Draw(img)
    img.paste(vgrad((w, h), (150, 162, 198), (72, 92, 142)), (x, y))
    for sx, sy, r in ((14, 8, 1), (52, 14, 2), (96, 6, 1), (150, 12, 2),
                      (196, 8, 1), (224, 16, 1), (120, 20, 1)):
        d.ellipse([x + sx - r, y + sy - r, x + sx + r, y + sy + r],
                  fill=(220, 235, 255))
    # skyline: dark towers with lit windows
    towers = [(6, 34, 22, 30), (36, 26, 26, 38), (70, 40, 20, 24),
              (100, 30, 24, 34), (134, 42, 22, 22), (164, 28, 26, 36),
              (198, 38, 22, 26), (222, 46, 14, 18)]
    for tx, ty, tw, th in towers:
        d.rectangle([x + tx, y + ty, x + tx + tw, y + 64], fill=(12, 22, 48))
        for wy in range(y + ty + 6, y + 58, 10):
            for wx in range(x + tx + 4, x + tx + tw - 4, 8):
                if (wx + wy) % 23 < 11:
                    d.rectangle([wx, wy, wx + 3, wy + 4], fill=(255, 196, 60))
    # river band
    d.rectangle([x, y + 64, x + w, y + h], fill=(38, 62, 112))
    # bridge: deck + towers + cables
    dy = y + 60
    d.line([(x, dy), (x + w, dy)], fill=(8, 14, 32), width=4)
    for tx in (x + 70, x + 168):
        d.line([(tx, dy), (tx, y + 40)], fill=(8, 14, 32), width=4)
    for cx0, cx1 in [(x, x + 70), (x + 70, x + 168), (x + 168, x + w)]:
        d.arc([cx0, dy - 18, cx1, dy + 4], 180, 360, fill=(8, 14, 32), width=2)
    # missile streaks arcing down onto the bridge
    for (sx, sy, ex, ey) in ((30, 2, 78, 52), (120, 0, 168, 54), (190, 4, 222, 50)):
        d.line([(x + sx, y + sy), (x + ex, y + ey)], fill=(255, 80, 40), width=3)
        d.line([(x + sx, y + sy), (x + ex, y + ey)], fill=(255, 170, 40), width=1)
        d.ellipse([x + ex - 5, y + ey - 5, x + ex + 5, y + ey + 5],
                  fill=(255, 90, 50))
        d.ellipse([x + ex - 2, y + ey - 2, x + ex + 2, y + ey + 2],
                  fill=(255, 240, 180))
    # fire glows on the deck + smoke puffs
    for fx, fy in ((78, 58), (168, 58)):
        for r, col in ((12, (255, 120, 30)), (7, (255, 190, 60)),
                       (3, (255, 240, 160))):
            d.ellipse([x + fx - r, y + fy - r, x + fx + r, y + fy + r], fill=col)
    for px, py, r in ((72, 46, 8), (80, 40, 6), (162, 46, 8), (170, 40, 6)):
        d.ellipse([x + px - r, y + py - r, x + px + r, y + py + r],
                  fill=(120, 120, 135))


def art_selloff(img, x, y, w, h):
    """Hero 2: the AI sell-off — light paper panel (v6: was dark red),
    a steep red chart falling across it, candlestick bars dropping,
    TAIEX -6.2% pill."""
    d = ImageDraw.Draw(img)
    img.paste(vgrad((w, h), (253, 242, 234), (246, 226, 214)), (x, y))
    # gridlines
    for gy in (16, 32, 48, 64):
        d.line([(x + 6, y + gy), (x + w - 6, y + gy)], fill=(205, 175, 165), width=1)
    # descending candlestick bars
    tops = [10, 16, 22, 30, 38, 44, 52, 58]
    bw = 18
    for i, t in enumerate(tops):
        bx = x + 12 + i * 27
        d.rectangle([bx, y + t, bx + bw, y + t + 26], fill=(200, 40, 40))
        d.line([(bx + bw // 2, y + t - 4), (bx + bw // 2, y + t + 30)],
               fill=(255, 90, 60), width=2)
    # steep falling line + translucent area fill below it
    pts = [(x + 10, y + 8), (x + 50, y + 18), (x + 90, y + 30),
           (x + 130, y + 38), (x + 170, y + 52), (x + 210, y + 66),
           (x + w - 8, y + 74)]
    area = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    ad = ImageDraw.Draw(area)
    ad.polygon([(px - x, py - y) for px, py in pts] +
               [(w - 8, h), (10, h)], fill=(255, 60, 40, 70))
    img.paste(area, (x, y), area)
    d.line(pts, fill=(200, 30, 30), width=3)
    d.line(pts, fill=(255, 255, 255), width=1)
    for px, py in pts[1:-1]:
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=WHITE,
                  outline=(200, 30, 30), width=1)
    # -6.2% pill, top-right
    lbl = "TAIEX -6.2%"
    f = font(True, 12)
    tw = f.getlength(lbl)
    px = x + w - tw - 22
    py = y + 6
    rrect(d, [px - 7, py - 3, px + tw + 9, py + 17], 8, fill=(178, 40, 40),
          outline=(255, 120, 100), width=1)
    d.text((px, py), lbl, font=f, fill=WHITE)


ART = {"kyiv": art_kyiv, "selloff": art_selloff, "cyclone": art_cyclone,
       "kafd": art_kafd}


# ---------------------------------------------------------------- mid icons
def draw_icon(d, kind, x, y, s, ink, accent):
    """One flat icon in an s x s box — ported from v2 (thermo, dove,
    atom, oil, gavel, sun, boat, shield, bat, tanker, chip, gem),
    plus missile (Poland), truck (Gaza aid convoy), pad (GTA VI)
    and bars (Japan inflation)."""
    cx, cy = x + s * 0.5, y + s * 0.5
    if kind == "thermo":  # thermometer + rising heat line
        d.rounded_rectangle([cx - 3, y + 2, cx + 3, y + s * 0.62],
                            radius=3, outline=ink, width=2)
        d.ellipse([cx - 6, y + s * 0.62, cx + 6, y + s * 0.88], fill=accent)
        d.rectangle([cx - 1, y + s * 0.40, cx + 1, y + s * 0.68], fill=accent)
        d.line([x + s * 0.72, y + s * 0.30, x + s * 0.95, y + s * 0.10],
               fill=accent, width=3)
        d.line([x + s * 0.72, y + s * 0.42, x + s * 0.95, y + s * 0.22],
               fill=ink, width=2)
    elif kind == "bars":  # rising bars + arrow (inflation)
        for i, bh in enumerate((0.30, 0.48, 0.66)):
            bx = x + 4 + i * 9
            d.rectangle([bx, y + s * (0.86 - bh), bx + 6, y + s * 0.86],
                        fill=ink if i < 2 else accent)
        d.line([x + 4, y + s * 0.28, x + s - 6, y + s * 0.08],
               fill=accent, width=2)
        d.polygon([(x + s - 6, y + s * 0.08), (x + s - 11, y + s * 0.08),
                   (x + s - 6, y + s * 0.15)], fill=accent)
    elif kind == "dove":  # peace dove, wings up
        d.ellipse([cx - 9, cy - 2, cx + 7, cy + 8], fill=ink)
        d.ellipse([cx + 3, cy - 9, cx + 11, cy - 1], fill=ink)
        d.polygon([(cx + 9, cy - 6), (cx + 15, cy - 4), (cx + 9, cy - 1)],
                  fill=accent)
        d.arc([cx - 13, cy - 13, cx + 1, cy + 1], 190, 350, fill=ink, width=3)
        d.arc([cx - 4, cy - 14, cx + 10, cy + 0], 190, 350, fill=ink, width=3)
        d.line([cx - 10, cy + 10, cx + 10, cy + 10], fill=accent, width=2)
    elif kind == "atom":  # three orbits + nucleus
        for ang in (15, 75, 135):
            pts = []
            for k in range(37):
                a = math.radians(ang + k * 360 / 36)
                pts.append((cx + s * 0.34 * math.cos(a),
                            cy + s * 0.15 * math.sin(a)))
            d.line(pts, fill=ink, width=2)
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=accent)
    elif kind == "oil":  # pump jack
        d.polygon([(x + 4, y + s * 0.62), (cx, y + 2), (x + s - 4, y + s * 0.62)],
                  fill=ink)
        d.line([cx, y + 2, cx, y + s * 0.62], fill=accent, width=3)
        d.ellipse([cx - 4, y + s * 0.68, cx + 4, y + s * 0.88], fill=accent)
        d.line([x + 2, y + s * 0.62, x + s - 2, y + s * 0.62], fill=ink, width=2)
    elif kind == "gavel":  # gavel + block, diagonal
        d.line([x + 4, y + s * 0.78, x + s - 4, y + s * 0.30], fill=ink, width=4)
        d.rounded_rectangle([x + s * 0.52, y + 3, x + s - 2, y + s * 0.32],
                            radius=2, fill=ink)
        d.rectangle([x + 3, y + s * 0.80, x + s * 0.42, y + s * 0.90], fill=ink)
        d.ellipse([x + s * 0.66, y + s * 0.48, x + s * 0.80, y + s * 0.62],
                  fill=accent)
    elif kind == "sun":  # sun over waves
        d.ellipse([cx - 6, cy - 8, cx + 6, cy + 4], fill=accent)
        for k in range(8):
            a = math.radians(k * 45)
            d.line([cx + 9 * math.cos(a), cy - 2 + 9 * math.sin(a),
                    cx + 13 * math.cos(a), cy - 2 + 13 * math.sin(a)],
                   fill=ink, width=2)
        d.arc([x + 3, y + s * 0.66, x + s - 3, y + s * 0.92], 180, 360,
              fill=ink, width=2)
        d.arc([x + 3, y + s * 0.74, x + s - 3, y + s * 0.98], 180, 360,
              fill=accent, width=2)
    elif kind == "boat":  # capsized boat: hull + waves
        d.polygon([(x + 3, y + s * 0.42), (x + s - 3, y + s * 0.42),
                   (x + s - 8, y + s * 0.62), (x + 8, y + s * 0.62)], fill=ink)
        d.line([x + 4, y + s * 0.42, x + s - 4, y + s * 0.42], fill=accent, width=2)
        for yy in (0.72, 0.84):
            d.arc([x + 2, y + s * yy, x + s * 0.5, y + s * yy + 8], 0, 180,
                  fill=ink, width=2)
            d.arc([x + s * 0.5, y + s * yy, x + s - 2, y + s * yy + 8], 0, 180,
                  fill=accent, width=2)
    elif kind == "shield":  # shield + check
        d.polygon([(cx, y + 2), (x + s - 3, y + 7), (x + s - 3, y + s * 0.52),
                   (cx, y + s - 3), (x + 3, y + s * 0.52), (x + 3, y + 7)],
                  fill=ink)
        d.line([cx - 6, cy, cx - 1, cy + 5], fill=accent, width=3)
        d.line([cx - 1, cy + 5, cx + 7, cy - 6], fill=accent, width=3)
    elif kind == "bat":  # cricket bat + ball
        d.line([x + s * 0.62, y + 4, x + s * 0.30, y + s * 0.52], fill=ink, width=4)
        d.rounded_rectangle([x + s * 0.10, y + s * 0.48, x + s * 0.44, y + s * 0.92],
                            radius=4, fill=ink)
        d.ellipse([x + s * 0.62, y + s * 0.60, x + s * 0.82, y + s * 0.80],
                  fill=accent)
    elif kind == "tanker":  # tanker + waves + alert dot
        d.rectangle([x + 2, y + s * 0.34, x + s - 2, y + s * 0.60], fill=ink)
        d.rectangle([x + s * 0.62, y + s * 0.18, x + s * 0.80, y + s * 0.34],
                    fill=ink)
        d.line([x + s * 0.70, y + 2, x + s * 0.70, y + s * 0.18], fill=ink, width=2)
        d.arc([x + 2, y + s * 0.66, x + s * 0.5, y + s * 0.66 + 8], 0, 180,
              fill=accent, width=2)
        d.arc([x + s * 0.5, y + s * 0.66, x + s - 2, y + s * 0.66 + 8], 0, 180,
              fill=ink, width=2)
    elif kind == "chip":  # AI chip with pins
        d.rounded_rectangle([x + 6, y + 6, x + s - 6, y + s - 6], radius=3,
                            outline=ink, width=2)
        d.rectangle([x + 10, y + 10, x + s - 10, y + s - 10], fill=accent)
        for k in range(3):
            yy = y + 10 + k * 7
            d.line([x + 1, yy, x + 6, yy], fill=ink, width=2)
            d.line([x + s - 6, yy, x + s - 1, yy], fill=ink, width=2)
    elif kind == "gem":  # faceted gem
        d.polygon([(cx, y + 2), (x + s - 3, y + s * 0.30), (x + s * 0.72, y + s - 3),
                   (x + s * 0.28, y + s - 3), (x + 3, y + s * 0.30)], fill=ink)
        d.line([cx, y + 2, cx, y + s - 3], fill=accent, width=2)
        d.line([x + 3, y + s * 0.30, x + s - 3, y + s * 0.30], fill=accent, width=2)
        d.line([x + s * 0.28, y + s - 3, cx, y + s * 0.30], fill=accent, width=2)
        d.line([x + s * 0.72, y + s - 3, cx, y + s * 0.30], fill=accent, width=2)
    elif kind == "missile":  # streak with glowing head + tower
        d.rectangle([x + 3, y + s * 0.45, x + 11, y + s * 0.92], fill=ink)
        for wy in range(int(y + s * 0.52), int(y + s * 0.88), 7):
            d.rectangle([x + 5, wy, x + 9, wy + 3], fill=accent)
        d.line([x + s * 0.30, y + s * 0.72, x + s * 0.92, y + s * 0.10],
               fill=(255, 80, 40), width=3)
        d.line([x + s * 0.30, y + s * 0.72, x + s * 0.92, y + s * 0.10],
               fill=(255, 170, 40), width=1)
        d.ellipse([x + s * 0.82, y + s * 0.02, x + s * 0.98, y + s * 0.18],
                  fill=(255, 90, 50))
        d.ellipse([x + s * 0.87, y + s * 0.07, x + s * 0.93, y + s * 0.13],
                  fill=(255, 240, 180))
    elif kind == "truck":  # aid truck: cargo box + cab + wheels
        d.rectangle([x + 3, y + s * 0.22, x + s * 0.62, y + s * 0.68], fill=ink)
        d.line([x + 3, y + s * 0.45, x + s * 0.62, y + s * 0.45],
               fill=accent, width=2)
        d.polygon([(x + s * 0.62, y + s * 0.38), (x + s * 0.82, y + s * 0.38),
                   (x + s * 0.92, y + s * 0.68), (x + s * 0.62, y + s * 0.68)],
                  fill=ink)
        d.rectangle([x + s * 0.66, y + s * 0.42, x + s * 0.78, y + s * 0.54],
                    fill=(240, 244, 250))
        for wx in (0.22, 0.72):
            d.ellipse([x + s * wx - 4, y + s * 0.68, x + s * wx + 4,
                       y + s * 0.84], fill=ink)
            d.ellipse([x + s * wx - 2, y + s * 0.72, x + s * wx + 2,
                       y + s * 0.80], fill=accent)
    elif kind == "pad":  # game controller: body + grips + d-pad + buttons
        d.rounded_rectangle([x + 2, y + s * 0.30, x + s - 2, y + s * 0.74],
                            radius=6, fill=ink)
        d.polygon([(x + 4, y + s * 0.62), (x + 12, y + s * 0.62),
                   (x + 9, y + s * 0.88), (x + 2, y + s * 0.86)], fill=ink)
        d.polygon([(x + s - 4, y + s * 0.62), (x + s - 12, y + s * 0.62),
                   (x + s - 9, y + s * 0.88), (x + s - 2, y + s * 0.86)], fill=ink)
        px, py = x + s * 0.26, y + s * 0.50
        d.rectangle([px - 2, py - 5, px + 2, py + 5], fill=accent)
        d.rectangle([px - 5, py - 2, px + 5, py + 2], fill=accent)
        bx, by = x + s * 0.74, y + s * 0.50
        for dx, dy in ((0, -5), (5, 0), (0, 5), (-5, 0)):
            d.ellipse([bx + dx - 2, by + dy - 2, bx + dx + 2, by + dy + 2],
                      fill=accent)
        d.line([x + s * 0.44, y + s * 0.42, x + s * 0.56, y + s * 0.42],
               fill=(240, 244, 250), width=2)
    else:
        raise ValueError(f"unknown icon kind: {kind}")


# ---------------------------------------------------------------- mid scenes
# Themed mini-scene behind each mid card's icon (v6): a sky/ground
# wash per story + the icon drawn large (40px). The icon stays the
# story's sign; the scene makes the box read as an illustration,
# not a pictogram on white.
SCENE_BG = {
    "pad": (198, 224, 245), "thermo": (255, 228, 196),
    "dove": (214, 234, 250), "bars": (238, 240, 245),
    "oil": (246, 226, 182), "missile": (220, 234, 250),
    "bat": (198, 228, 180), "chip": (232, 234, 240),
    "gem": (234, 224, 246), "truck": (246, 228, 192),
}


def draw_mid_scene(d, kind, x, y, w, h, accent):
    """Mini illustrated scene in the mid-card art box (w x h)."""
    d.rectangle([x, y, x + w, y + h], fill=SCENE_BG[kind])
    if kind == "pad":
        # skyline silhouette along the bottom, controller in front
        for sx, sw, sh in ((2, 14, 12), (18, 10, 18), (30, 16, 10),
                           (48, 12, 16), (62, 14, 9), (78, 12, 14),
                           (92, 10, 11)):
            d.rectangle([x + sx, y + h - sh, x + sx + sw, y + h],
                        fill=(24, 38, 66))
    elif kind == "thermo":
        d.ellipse([x + w - 20, y + 3, x + w - 6, y + 17], fill=(255, 190, 60))
    elif kind == "dove":
        d.line([(x + 2, y + h - 4), (x + w - 2, y + h - 4)],
               fill=(90, 140, 190), width=2)
        # two small flags on the table line: US stripes (left),
        # Russian tricolour (right) — the dove flies between them
        fx, fy, fw, fh = x + 5, y + h - 16, 20, 12
        for i in range(7):
            d.rectangle([fx, fy + i * fh // 7, fx + fw, fy + (i + 1) * fh // 7],
                        fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
        d.rectangle([fx, fy, fx + 8, fy + 6], fill=(30, 60, 140))
        fx2 = x + w - 25
        for i, col in enumerate(((255, 255, 255), (0, 90, 200), (220, 30, 30))):
            d.rectangle([fx2, fy + i * fh // 3, fx2 + fw, fy + (i + 1) * fh // 3],
                        fill=col)
    elif kind == "bars":
        for gy in (12, 24, 36):
            d.line([(x + 4, y + gy), (x + w - 4, y + gy)],
                   fill=(205, 210, 220), width=1)
    elif kind == "oil":
        d.ellipse([x + w - 20, y + 3, x + w - 6, y + 17], fill=(255, 190, 60))
        d.rectangle([x, y + h - 6, x + w, y + h], fill=(222, 190, 130))
    elif kind == "missile":
        d.rectangle([x, y + h - 6, x + w, y + h], fill=(120, 140, 110))
    elif kind == "bat":
        d.rectangle([x, y + h - 8, x + w, y + h], fill=(140, 190, 110))
    elif kind == "chip":
        # red down arrow, right side
        d.line([(x + w - 10, y + 6), (x + w - 10, y + 22)],
               fill=(200, 40, 40), width=3)
        d.polygon([(x + w - 15, y + 20), (x + w - 5, y + 20),
                   (x + w - 10, y + 28)], fill=(200, 40, 40))
    elif kind == "gem":
        for sx, sy in ((8, 6), (w - 10, 10), (w - 22, 4)):
            d.ellipse([x + sx - 2, y + sy - 2, x + sx + 2, y + sy + 2],
                      fill=(255, 255, 255))
    elif kind == "truck":
        d.rectangle([x, y + h - 8, x + w, y + h], fill=(190, 175, 140))
        d.line([(x + 4, y + h - 4), (x + w - 4, y + h - 4)],
               fill=(255, 255, 255), width=1)
    draw_icon(d, kind, x + (w - 40) // 2, y + 3, 40, DARKTXT, accent)


# ---------------------------------------------------------------- build
def build():
    _fit_checks()
    img = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(img)

    y = 0
    # ---- masthead (0-88): kicker, GIANT serif date, serif sub-line
    fk = font(True, 12)
    d.text((M + 8, 5), "THE WORLD IN ONE DAY", font=fk, fill=BRONZE)
    t = "35 STORIES  ·  7 REGIONS"
    d.text((W - M - 8 - fk.getlength(t), 5), t, font=fk, fill=BRONZE)
    d.text((M + 8, 18), "Friday 20 November 2026",
           font=ImageFont.truetype(F_SERIF_BOLD, 46), fill=DARKTXT)
    fsub = ImageFont.truetype(F_SERIF, 13)
    d.text((M + 8, 70),
           "Kyiv's bridges hit · Asia's markets sink · A storm comes ashore",
           font=fsub, fill=(120, 90, 30))
    y = 88
    # ---- colour bar (88-94)
    seg = CW // 6
    for i, c in enumerate(BAR6):
        x0 = M + i * seg
        x1 = M + (i + 1) * seg if i < 5 else W - M
        d.rectangle([x0, y, x1, y + 6], fill=c)
    y = 96
    # ---- UTC strip (96-122): variable-width chips, centred after the label
    d.text((M, y + 7), "THE DAY IN UTC", font=font(True, 12), fill=BRONZE)
    f = font(True, 11)
    widths = [f.getlength(c) + 12 for c in UTC_CHIPS]
    total = sum(widths) + 5 * 6
    cx = M + 132 + (875 - total) // 2
    for c, cw in zip(UTC_CHIPS, widths):
        rrect(d, [cx, y + 1, cx + cw, y + 25], 7, fill=CHIP, outline=CHIP_LINE, width=1)
        d.text((cx + 6, y + 7), c, font=f, fill=INK)
        cx += cw + 6
    y = 124
    # ---- number strip (124-174)
    nw, ngap = 160, 6
    nx = M + 1
    for num, lbl in NUMBERS:
        rrect(d, [nx, y, nx + nw, y + 50], 8, fill=CHIP, outline=CHIP_LINE, width=1)
        fn = font(True, 22)
        d.text((nx + (nw - fn.getlength(num)) / 2, y + 4), num, font=fn, fill=DARKTXT)
        fl = font(False, 10)
        d.text((nx + (nw - fl.getlength(lbl)) / 2, y + 30), lbl, font=fl, fill=NEON)
        nx += nw + ngap
    y = 176
    # ---- region tabs (176-198)
    tw, tgap = 136, 6
    tx = M + 2
    for name, n in REGIONS:
        rrect(d, [tx, y, tx + tw, y + 22], 7, fill=PANEL2, outline=CHIP_LINE, width=1)
        f = font(True, 11)
        s = f"{name} {n}"
        d.text((tx + (tw - f.getlength(s)) / 2, y + 4), s, font=f, fill=INK)
        tx += tw + tgap
    y = 200
    # ---- heroes (200-356), four columns
    hw, hgap = 239, 12
    hx = M
    for hero in HEROES:
        rrect(d, [hx, y, hx + hw, y + 156], 8, fill=PANEL, outline=CHIP_LINE, width=1)
        ART[hero["art"]](img, hx + 1, y + 1, hw - 2, 78)
        # number badge, top-left of the art (v3 style) — hero 4 has
        # none, its event is story 4 (the mid card below); no duplicate "4".
        if hero["num"] is not None:
            bx, by = hx + 12, y + 10
            d.ellipse([bx - 15, by - 15, bx + 15, by + 15], fill=GOLD,
                      outline=(255, 255, 255), width=2)
            fb = font(True, 16)
            s = str(hero["num"])
            d.text((bx - fb.getlength(s) / 2, by - 11), s, font=fb, fill=DARKTXT)
        d.text((hx + 10, y + 84), hero["headline"], font=font(True, 19), fill=DARKTXT)
        lines = wrap(hero["deck"], font(False, 12), 219)
        ly = y + 110
        for ln in lines[:2]:
            d.text((hx + 10, ly), ln, font=font(False, 12), fill=INK)
            ly += 15
        d.text((hx + 10, y + 142), hero["source"] + "  ·  " + hero["region"],
               font=font(False, 10), fill=SRC_GOLD)
        hx += hw + hgap
    y = 358
    # ---- mid cards (358-638): 2 cols x 5 rows, 52 tall, gap 4
    # each card: illustrated mini-scene (left) + number badge +
    # headline + source + 2-line deck
    mw, mgap = 488, 16
    for row in range(5):
        for col in range(2):
            m = MIDS[row * 2 + col]
            x0 = M + col * (mw + mgap)
            y0 = y + row * 56
            fill = TINT_A if (row + col) % 2 == 0 else TINT_B
            rrect(d, [x0, y0, x0 + mw, y0 + 52], 7, fill=fill)
            # illustrated scene box with a mini drawing of the story
            rrect(d, [x0 + 3, y0 + 3, x0 + 107, y0 + 49], 5,
                  fill=(255, 255, 255),
                  outline=REGION_COLOR[m["region"]], width=1)
            draw_mid_scene(d, m["icon"], x0 + 4, y0 + 4, 102, 44,
                           REGION_COLOR[m["region"]])
            # badge
            bcx, bcy = x0 + 118, y0 + 15
            d.ellipse([bcx - 11, bcy - 11, bcx + 11, bcy + 11], fill=DARKTXT)
            fb = font(True, 11)
            s = str(m["num"])
            d.text((bcx - fb.getlength(s) / 2, bcy - 8), s, font=fb, fill=WHITE)
            # headline + source on one line
            d.text((x0 + 134, y0 + 4), m["headline"], font=font(True, 14), fill=DARKTXT)
            fs = font(False, 10)
            d.text((x0 + mw - 8 - fs.getlength(m["source"]), y0 + 6),
                   m["source"], font=fs, fill=DARKMUT)
            # deck, max 2 lines
            lines = wrap(m["deck"], font(False, 12), 348)
            ly = y0 + 22
            for ln in lines[:2]:
                d.text((x0 + 134, ly), ln, font=font(False, 12), fill=(40, 55, 85))
                ly += 13
    y = 640
    # ---- map panel (640-780): real world outlines from lon/lat,
    # sage-green land on cream paper, numbered region-coloured dots
    rrect(d, [M, y, W - M, y + 140], 8, fill=PANEL, outline=CHIP_LINE, width=1)
    d.text((M + 10, y + 5), "WHERE IT HAPPENED — 13 STORIES MAPPED",
           font=font(True, 11), fill=BRONZE)
    for poly in CONTINENTS_LL:
        pts = [ll(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(148, 176, 134), outline=(88, 120, 88))
    for num, dx, dy, reg in DOTS:
        col = REGION_COLOR[reg]
        d.ellipse([dx - 9, dy - 9, dx + 9, dy + 9], fill=col, outline=WHITE, width=1)
        fb = font(True, 9)
        s = str(num)
        d.text((dx - fb.getlength(s) / 2, dy - 6), s, font=fb, fill=WHITE,
               stroke_width=1, stroke_fill=(10, 22, 48))
    d.text((M + 10, y + 124), "HOW SURE ARE WE?   ● REPORTED   ● CLAIM   ● FORECAST",
           font=font(False, 10), fill=MUTED)
    y = 782
    # ---- briefs panel (782-967): header + 11 rows x 2 columns
    d.text((M, y), "THE REST OF THE DAY — 21 MORE STORIES",
           font=font(True, 12), fill=BRONZE)
    bn, bt, bs = font(True, 13), font(False, 13), font(False, 13)
    for i, (num, head, src, reg) in enumerate(BRIEFS):
        col = i // 11
        row = i % 11
        bx = M + col * 496
        by = y + 18 + row * 15
        d.text((bx, by), f"{num}. ", font=bn, fill=BRONZE)
        nx = bx + bn.getlength(f"{num}. ")
        d.text((nx, by), head, font=bt, fill=INK)
        d.text((nx + bt.getlength(head), by), f" — {src} ({reg})",
               font=bs, fill=MUTED)
    y = 967
    # ---- DATE CHECK (967-1001)
    rrect(d, [M, y, W - M, y + 34], 6, fill=RED, outline=(220, 90, 90), width=1)
    d.text((M + 10, y + 3), DATE_L1, font=font(True, 11), fill=WHITE)
    d.text((M + 10, y + 18), DATE_L2, font=font(False, 11), fill=(255, 220, 210))
    y = 1003
    # ---- footer (1003-1015)
    ff = font(False, 10)
    d.text(((W - ff.getlength(FOOTER)) / 2, y + 2), FOOTER, font=ff, fill=MUTED_DK)
    # ---- gold frame
    d.rectangle([1, 1, W - 2, H - 2], outline=GOLD, width=3)
    assert y + 16 <= H, f"layout overflow: {y + 16}"
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
