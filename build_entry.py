#!/usr/bin/env python3
"""Build entry.png for make.fun news-image-20261120 — v2 (runs LOCALLY,
not in the grader sandbox): one 1024x1024 picture summing up Friday
20 November 2026 in the SAME 50 verified stories as v1.

v2 is a FULL REBUILD with a brand-new visual system, because the user
ordered it after seeing v1: "kalau belum sempurna buat lagi, coba lebih
berwarna dan beda dari yang lain" (make it again, more colourful and
different from the others). The live top 3 (checked 20 Nov 09:23 WIB,
692 ranked entries) are ALL cream-paper serif newspapers — rank 1 at
98.92% with 50 stories, rank 2 the most colourful at 98.84% with 36,
rank 3 sparser at 98.78% with 28. v2 deliberately LEAVES that look:

- DARK NAVY page (not cream paper), sans-bold headlines (not serif),
  gold frame, multi-colour bar under the masthead.
- FOUR full-bleed heroes, each in a DIFFERENT saturated palette AND a
  different illustration style: (1) summit scene with podiums + flags
  (navy/gold), (2) Kerch sunset with a black bridge silhouette and
  LAYERED smoke (purple/orange/red), (3) neon night city with THREE
  glowing missile streaks (dark teal + yellow windows), (4) storm radar
  rings + diagonal rain (storm blue + cyan).
- Mid cards on ALTERNATING light tints (sky / peach / mint / lavender,
  cycled by row+column so no two neighbours match), with a thick
  region-coloured left bar and BIGGER icons.
- Numbers strip: six dark chips, each figure in a different NEON colour
  (gold, cyan, coral, lime, magenta, orange).
- DARK NAVY map panel with bright region-coloured dots; briefs on the
  dark panel with coloured dots; red DATE CHECK panel; white section
  headers under a six-colour bar.
- Content is UNCHANGED from v1 (same 50 stories, same numbers, same
  sources, same DATE CHECK — all verified against live news of 20 Nov
  2026, see BUILD_LOG.md). Only the visual system changed, plus four
  v1 defects fixed: Kerch smoke is now layered puffs, every brief is
  shortened to fit on ONE line with its source visible, the map
  continents are more recognisable (UK / Japan / NZ added), and the
  KAFD hero now has three missile streaks with glowing heads.

All drawing is Pillow code — no photographs, no network, no clock, no
randomness anywhere: two runs of this script produce byte-identical
output. Output: entry.png next to this file (1024x1024, <= 1 MiB).
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 16  # outer margin

# ------------------------------------------------------------------ palette
# Dark page, saturated accents. The page must read BOLD and colourful at
# a glance — the opposite of the cream serif pages at the top of the
# leaderboard.
PAGE = (8, 20, 48)          # deep navy page
PANEL = (16, 36, 78)        # lighter navy panel
PANEL2 = (22, 48, 96)       # brighter navy panel
MAP_BG = (13, 30, 66)       # map panel
LAND = (74, 108, 160)       # continents on the dark map
WHITE = (255, 255, 255)
LIGHT = (216, 226, 240)     # body text on dark
MIDGREY = (158, 172, 198)   # secondary text on dark
INK = (18, 22, 34)          # text on light tints
GREY = (86, 92, 108)        # secondary text on light tints
GOLD = (255, 196, 0)
CYAN = (0, 214, 226)
CORAL = (255, 92, 74)
LIME = (150, 220, 60)
MAGENTA = (255, 92, 200)
ORANGE = (255, 140, 0)
TEAL = (0, 200, 180)
PURPLE = (170, 100, 255)
RED = (214, 24, 44)
REDPANEL = (198, 32, 48)
NAVY = (10, 42, 110)
BLUE = (20, 96, 168)        # Europe
RUST = (196, 58, 36)        # Middle East
GREEN = (34, 140, 60)       # Africa
SLATE = (64, 88, 120)       # Global
BRICK = (160, 44, 24)       # Kerch band
DARKTEAL = (6, 58, 64)      # KAFD band
STORM = (20, 70, 130)       # Akvan band
HERO_NAVY = (18, 44, 96)    # declaration band

# Light tints for mid cards, cycled by (row + col) % 4 so neighbours differ.
TINTS = [
    (214, 232, 248),  # sky
    (255, 232, 208),  # peach
    (214, 244, 224),  # mint
    (232, 222, 248),  # lavender
]

FONT_DIR = "/usr/share/fonts/truetype"
SANS_B = f"{FONT_DIR}/liberation/LiberationSans-Bold.ttf"
SANS = f"{FONT_DIR}/liberation/LiberationSans-Regular.ttf"
SERIF_I = f"{FONT_DIR}/liberation/LiberationSerif-Italic.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# ------------------------------------------------------------------ helpers
def wrap(draw, text, fnt, max_w):
    """Greedy word wrap returning a list of lines that fit max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(draw, x, y, text, fnt, max_w, fill, leading=None, max_lines=None):
    lines = wrap(draw, text, fnt, max_w)
    if max_lines:
        lines = lines[:max_lines]
    lh = leading or int(fnt.size * 1.18)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y, len(lines)


def vgrad(img, box, top, bottom):
    """Vertical gradient inside box (x0, y0, x1, y1), fresh rows per y."""
    x0, y0, x1, y1 = box
    h = max(1, y1 - y0)
    for yy in range(y0, y1):
        t = (yy - y0) / h
        c = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
        img.paste(c, (x0, yy, x1, yy + 1))


def hgrad(img, box, left, right):
    """Horizontal gradient inside box (x0, y0, x1, y1), fresh cols per x."""
    x0, y0, x1, y1 = box
    w = max(1, x1 - x0)
    for xx in range(x0, x1):
        t = (xx - x0) / w
        c = tuple(int(left[i] + (right[i] - left[i]) * t) for i in range(3))
        img.paste(c, (xx, y0, xx + 1, y1))


def colour_bar(draw, x, y, w, h, colours):
    """A bar split into equal segments, one per colour (masthead accent)."""
    n = len(colours)
    for i, c in enumerate(colours):
        x0 = x + (w * i) // n
        x1 = x + (w * (i + 1)) // n
        draw.rectangle([x0, y, x1, y + h], fill=c)


# --------------------------------------------------------------------- data
# Same verified content as v1 (BUILD_LOG.md). Numbers strip: (figure,
# caption, neon accent). Gold $3,756 was NOT independently verified, so
# the strip keeps the verified $1.84bn GTA VI day-one sales (Sensor
# Tower, reported 20 Nov).
NUMBERS = [
    ("300,000", "evacuated ahead of Akvan", GOLD),
    ("51\u201348", "Senate rejects Iran war-powers curb", CYAN),
    ("$48bn", "cost of the US-Iran war so far", CORAL),
    ("113*", "Nicholls rescues NZ from 70/5", LIME),
    ("83,022", "Sensex close, up 989 points", MAGENTA),
    ("$1.84bn", "GTA VI's day-one sales", ORANGE),
]

# The day in UTC: (time label, short event, chip colour). Events are
# shortened so each fits one line inside its chip.
UTC_STRIP = [
    ("Overnight", "Bridge hit a third time", RED),
    ("~06:00 UTC", "APEC meets in Shenzhen", ORANGE),
    ("~10:00 UTC", "Declaration issued", TEAL),
    ("~14:00 UTC", "Missile hits Riyadh", PURPLE),
    ("Evening", "Akvan landfall", BLUE),
    ("Late", "Dow -1,084", GREEN),
]

# Region tabs: (label, count, colour). Counts sum to 50 stories.
REGIONS = [
    ("ASIA-PACIFIC", 12, ORANGE),
    ("EUROPE", 13, BLUE),
    ("MIDDLE EAST", 9, RUST),
    ("AFRICA", 2, GREEN),
    ("AMERICAS", 8, PURPLE),
    ("OCEANIA", 2, TEAL),
    ("GLOBAL", 4, SLATE),
]
REGION_COLOUR = {name: col for name, _n, col in REGIONS}

# Heroes 1-4: (key, number, kicker chip, band colour, headline, deck).
HEROES = [
    ("summit", "1", "SHENZHEN", HERO_NAVY,
     "Trump, Xi and Putin issue joint declaration",
     "No big peace deal. The meeting was Thursday; the declaration lands "
     "Friday. Trump: Iran war call waits until 2027. \u2014 Reuters"),
    ("kerch", "2", "KERCH STRAIT", BRICK,
     "Crimean Bridge hit a third time this week; rail halted",
     "Rail partly resumes. Putin vows retaliation; Kyiv hit by missiles, "
     "blast near the Dutch embassy. \u2014 CNN \u00b7 Reuters"),
    ("kafd", "3", "KAFD \u00b7 RIYADH", DARKTEAL,
     "Houthi missile hits Riyadh's KAFD financial district",
     "A wealth-fund tower is damaged; no casualties reported. Houthis "
     "claim four Saudi targets at 03:47. \u2014 Reuters \u00b7 WSJ"),
    ("akvan", "4", "BAY OF BENGAL", STORM,
     "Cyclone Akvan bears down on Odisha; 300,000 evacuated",
     "Landfall near Gopalpur at noon; 423 rescue teams out as the storm "
     "hits India's east coast. \u2014 The Hindu \u00b7 IMD"),
]

# Mid cards 5-16: (number, place, topic, region, icon, headline, deck,
# source). Decks are shortened (v1 fix) so each fits ONE line at 9 px
# inside its card; the source rides on the kicker line, top-right.
FEATURED = [
    (5, "ANTALYA", "CLIMATE", "GLOBAL", "thermo",
     "COP31 closes with a $305bn gap",
     "Draft drops fossil fuels; $305bn gap a year.",
     "Reuters"),
    (6, "BRUSSELS", "DIPLOMACY", "EUROPE", "dove",
     "Europe ready for talks with Russia on ending Ukraine war",
     "Brussels will talk; Putin invites leaders.",
     "Reuters"),
    (7, "YONGBYON", "SECURITY", "ASIA-PACIFIC", "atom",
     "North Korea expanding uranium enrichment at Yongbyon",
     "IAEA: new wing finished; concern grows.",
     "Reuters \u00b7 IAEA"),
    (8, "CARACAS", "DIPLOMACY", "AMERICAS", "oil",
     "US details $12bn of Venezuela oil and mineral revenue",
     "State Dept. lays out the money at stake.",
     "AP"),
    (9, "SEOUL", "JUSTICE", "ASIA-PACIFIC", "gavel",
     "South Korea top court overturns ex-PM Han's conviction",
     "15-year term quashed; retrial ordered.",
     "Yonhap"),
    (10, "SUVA", "CLIMATE", "OCEANIA", "sun",
     "Fiji declares national disaster over drought",
     "El Ni\u00f1o leaves water short across islands.",
     "Reuters"),
    (11, "DAKAR", "MIGRATION", "AFRICA", "boat",
     "Migrant boat capsizes off Senegal; dozens missing",
     "Rescuers search the Atlantic for survivors.",
     "AP"),
    (12, "PORT-AU-PRINCE", "SECURITY", "AMERICAS", "shield",
     "Haiti approves Salvadoran troop deal",
     "2,000+ Salvadoran troops fight the gangs.",
     "AP"),
    (13, "WELLINGTON", "SPORT", "OCEANIA", "bat",
     "Nicholls 113* as NZ reach 243/5 on day one",
     "From 70/5, Phillips 94*; day two resumes.",
     "Cricinfo"),
    (14, "HORMUZ", "CONFLICT", "MIDDLE EAST", "tanker",
     "ADNOC vessel attacked in Strait of Hormuz",
     "One crewman missing after the strike.",
     "Reuters"),
    (15, "SAN FRANCISCO", "TECH", "GLOBAL", "chip",
     "Anthropic valuation reportedly $1.5 trillion",
     "Said to be worth more than most banks.",
     "Reuters"),
    (16, "MOUNTAIN VIEW", "TECH", "GLOBAL", "gem",
     "Google ships Gemini 4 Neon",
     "1M-token model rolls out to Pro users.",
     "Google"),
]

# Briefs 17-50: (number, place, region, text, source). Texts are
# shortened (v1 fix) so each fits on ONE line with its source visible —
# no "…" truncation anywhere.
BRIEFS = [
    (17, "GAZA", "MIDDLE EAST", "4 nations urge aid into flooded Gaza", "AP"),
    (18, "GAZA", "MIDDLE EAST", "IDF ends ground op outside Yellow Line", "Reuters"),
    (19, "LEBANON", "MIDDLE EAST", "Israel hits Hezbollah missile sites", "Reuters"),
    (20, "TEHRAN", "MIDDLE EAST", "US intel: Iran missiles 1,500\u20132,500", "WSJ"),
    (21, "HORMUZ", "MIDDLE EAST", "Tanker ablaze after mine; IEA warns", "Reuters"),
    (22, "GENOA", "EUROPE", "Airport halts flights after drone; 4h stop", "AP"),
    (23, "PARIS", "EUROPE", "France's 4th weekend of cost protests", "AFP"),
    (24, "JERUSALEM", "MIDDLE EAST", "Eisenkot tapped to form govt", "AP"),
    (25, "SEOUL", "ASIA-PACIFIC", "Korea exports top $1tn, a first", "Yonhap"),
    (26, "MUMBAI", "ASIA-PACIFIC", "Sensex +989 to 83,022; Nifty over 25,500", "BSE"),
    (27, "TAIPEI", "ASIA-PACIFIC", "Taiwan steadies stocks; short curbs start", "CNA"),
    (28, "TOKYO", "ASIA-PACIFIC", "Takaichi dodges \u201cTaiwan contingency\u201d", "AP"),
    (29, "KINSHASA", "AFRICA", "Ebola in Congo: 10,668 cases, 5,198 dead", "WHO"),
    (30, "SACRAMENTO", "AMERICAS", "California probes Nvidia chips", "Reuters"),
    (31, "WASHINGTON", "AMERICAS", "Trump pardons baseball legend Pete Rose", "AP"),
    (32, "CINCINNATI", "AMERICAS", "Fiona the hippo dies after eating a hat", "AP"),
    (33, "LOS ANGELES", "AMERICAS", "GTA VI beats Odyssey $1.8bn", "Sensor Tower"),
    (34, "SHENZHEN", "ASIA-PACIFIC", "Albanese meets Xi in fifth formal talks", "AAP"),
    (35, "WASHINGTON", "AMERICAS", "Trump back from China; presser today", "AP"),
    (36, "PARIS", "EUROPE", "France, Germany, UK weigh Russia meeting", "Reuters"),
    (37, "WASHINGTON", "AMERICAS", "US envoy: Russia open to NATO guarantees", "AP"),
    (38, "TURIN", "EUROPE", "Zverev into ATP semis; Alcaraz unbeaten", "ATP"),
    (39, "BRUSSELS", "EUROPE", "EU-UK summit opens", "Reuters"),
    (40, "NEW DELHI", "ASIA-PACIFIC", "Modi meets William and Kate", "AP"),
    (41, "KUALA LUMPUR", "ASIA-PACIFIC", "ASEAN summit closes, pacts signed", "AP"),
    (42, "MANILA", "ASIA-PACIFIC", "Quad holds first summit in 2 years", "AP"),
    (43, "KYIV", "EUROPE", "Witkoff, Kushner brief Zelenskyy", "Reuters"),
    (44, "BERLIN", "EUROPE", "Coalition of the Willing meets", "Reuters"),
    (45, "CANBERRA", "OCEANIA", "Australia sanctions settlers", "ABC"),
    (46, "NEW YORK", "AMERICAS", "US stocks slide: Dow falls 1,084", "Reuters"),
    (47, "BERLIN", "EUROPE", "Merz hosts Qatar's emir", "AP"),
    (48, "BRUSSELS", "EUROPE", "NATO assembly opens 72nd session", "AP"),
    (49, "WASHINGTON", "AMERICAS", "US jobless claims 203,000", "Reuters"),
    (50, "WORLD", "GLOBAL", "World Children's Day marked", "UN"),
]

DATE_CHECK = (
    "DATE CHECK \u2014 LEFT OUT AS OTHER DAYS' NEWS: 19 NOV: Shenzhen "
    "summit meeting itself \u00b7 ICJ genocide ruling on Myanmar \u00b7 "
    "Anthropic IPO priced $83, first trade $111.50 \u00b7 GTA VI midnight "
    "release. 18 NOV: Nvidia results \u00b7 Jeffries named US speaker \u00b7 "
    "Voyager 1 one light-day \u00b7 Germany's electricity-tax cut. "
    "17 NOV: Crimean Bridge road span falls."
)

# Map dots for the 16 numbered stories: (number, fx, fy) inside the map
# box. Same hand-spread positions as v1 (verified: no two dots touch).
MAP_DOTS = [
    (1, 0.84, 0.34), (2, 0.60, 0.14), (3, 0.58, 0.52), (4, 0.76, 0.50),
    (5, 0.54, 0.32), (6, 0.48, 0.18), (7, 0.88, 0.18), (8, 0.24, 0.56),
    (9, 0.94, 0.32), (10, 0.96, 0.66), (11, 0.44, 0.48), (12, 0.20, 0.42),
    (13, 0.90, 0.82), (14, 0.65, 0.40), (15, 0.05, 0.20), (16, 0.12, 0.34),
]

# Continent outlines in map-box fractions (schematic but recognisable;
# v2 adds the UK, Japan and New Zealand, which v1's map lacked).
CONTINENTS = [
    # North America
    [(0.02, 0.10), (0.10, 0.04), (0.20, 0.06), (0.24, 0.16), (0.20, 0.26),
     (0.15, 0.34), (0.10, 0.30), (0.05, 0.22), (0.02, 0.16)],
    # South America
    [(0.16, 0.42), (0.24, 0.40), (0.27, 0.50), (0.24, 0.64), (0.20, 0.72),
     (0.17, 0.60), (0.15, 0.50)],
    # Africa
    [(0.46, 0.38), (0.55, 0.36), (0.60, 0.44), (0.58, 0.58), (0.53, 0.70),
     (0.49, 0.62), (0.46, 0.50)],
    # Europe
    [(0.46, 0.22), (0.52, 0.18), (0.58, 0.20), (0.60, 0.28), (0.55, 0.32),
     (0.48, 0.30)],
    # United Kingdom (small island off Europe)
    [(0.44, 0.16), (0.46, 0.14), (0.47, 0.18), (0.45, 0.20)],
    # Asia
    [(0.60, 0.14), (0.72, 0.08), (0.88, 0.10), (0.96, 0.20), (0.92, 0.30),
     (0.84, 0.36), (0.74, 0.34), (0.66, 0.30), (0.60, 0.24)],
    # Japan (small chain off Asia)
    [(0.92, 0.22), (0.94, 0.20), (0.95, 0.26), (0.93, 0.28)],
    # Australia
    [(0.82, 0.62), (0.90, 0.60), (0.94, 0.66), (0.90, 0.72), (0.83, 0.70)],
    # New Zealand (two small islands)
    [(0.94, 0.74), (0.96, 0.72), (0.97, 0.78), (0.95, 0.80)],
]

# -------------------------------------------------------------- big icons
def draw_icon(d, kind, x, y, s, ink, accent):
    """One flat icon in an s x s box — drawn bigger and bolder than v1's
    small band icons, so each mid card reads at a glance."""
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
    elif kind == "sun":  # sun over waves (drought: dry sun + cracked line)
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


# -------------------------------------------------------------- hero scenes
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


def paint_summit(img, x0, y0, w, h):
    """Hero 1: figurative scene — navy hall, gold chandeliers, three
    podiums with US / China / Russia flags and name plates."""
    vgrad(img, (x0, y0, x0 + w, y0 + h), (10, 42, 110), (6, 22, 62))
    d = ImageDraw.Draw(img)
    for cx in (x0 + w * 0.13, x0 + w * 0.44, x0 + w * 0.75):
        d.line([cx, y0 + 6, cx, y0 + 16], fill=GOLD, width=2)
        d.ellipse([cx - 5, y0 + 14, cx + 5, y0 + 24], fill=GOLD)
        d.ellipse([cx - 2, y0 + 17, cx + 2, y0 + 21], fill=(255, 240, 170))
    table_y = y0 + h - 26
    d.rectangle([x0, table_y, x0 + w, y0 + h], fill=(52, 36, 20))
    d.rectangle([x0, table_y, x0 + w, table_y + 3], fill=GOLD)
    names = (("TRUMP", _flag_us), ("XI", _flag_cn), ("PUTIN", _flag_ru))
    for i, (name, flagfn) in enumerate(names):
        cx = x0 + w * (0.13 + 0.31 * i)
        d.ellipse([cx - 13, table_y - 52, cx + 13, table_y - 26], fill=(232, 196, 164))
        d.polygon([(cx - 16, table_y - 26), (cx + 16, table_y - 26),
                   (cx + 24, table_y), (cx - 24, table_y)], fill=(24, 24, 30))
        d.rectangle([cx - 4, table_y - 26, cx + 4, table_y - 8], fill=WHITE)
        d.rectangle([cx - 22, table_y - 62, cx + 22, table_y - 52], fill=(240, 240, 240))
        flagfn(d, cx - 22, table_y - 62, 44, 10)
        d.line([cx, table_y - 62, cx, table_y - 52], fill=(120, 120, 120), width=1)
        d.rectangle([cx - 20, table_y + 6, cx + 20, table_y + 20], fill=WHITE)
        tw = d.textlength(name, font=font(SANS_B, 10))
        d.text((cx - tw / 2, table_y + 8), name, font=font(SANS_B, 10), fill=INK)


def paint_kerch(img, x0, y0, w, h):
    """Hero 2: sunset silhouette — purple/orange/red gradient, big sun,
    black bridge deck + pylons, LAYERED smoke (dark base, mid, light
    highlight puffs with shading), birds."""
    vgrad(img, (x0, y0, x0 + w, y0 + h), (96, 34, 110), (226, 96, 52))
    d = ImageDraw.Draw(img)
    d.ellipse([x0 + w - 91, y0 + 5, x0 + w - 53, y0 + 43], fill=(255, 176, 32))
    d.ellipse([x0 + w - 85, y0 + 11, x0 + w - 59, y0 + 37], fill=(255, 214, 110))
    for bx, by, s in ((x0 + 30, y0 + 14, 5), (x0 + 52, y0 + 8, 4), (x0 + 70, y0 + 18, 4)):
        d.arc([bx - s, by - s, bx + s, by + s], 200, 340, fill=(40, 16, 40), width=2)
    deck_y = y0 + h - 30
    for px in (x0 + 52, x0 + 150):
        d.rectangle([px, deck_y - 34, px + 7, deck_y], fill=(16, 10, 16))
        d.line([px + 3, deck_y - 34, x0 + 20, deck_y], fill=(16, 10, 16), width=2)
        d.line([px + 3, deck_y - 34, x0 + w - 20, deck_y], fill=(16, 10, 16), width=2)
    d.rectangle([x0, deck_y, x0 + w, deck_y + 8], fill=(16, 10, 16))
    d.rectangle([x0 + 96, deck_y - 4, x0 + 132, deck_y], fill=(16, 10, 16))
    # Layered smoke above the broken span: dark base, mid grey, light top.
    sx, sy = x0 + w * 0.52, deck_y - 26
    for dx, dy, r, col in ((-16, 8, 15, (74, 74, 84)), (0, 0, 18, (104, 104, 116)),
                           (16, 8, 14, (74, 74, 84)), (-7, -10, 13, (140, 140, 152)),
                           (8, -11, 12, (158, 158, 170)), (0, -16, 9, (182, 182, 194))):
        d.ellipse([sx + dx - r, sy + dy - r, sx + dx + r, sy + dy + r], fill=col)
    d.rectangle([x0, y0 + h - 22, x0 + w, y0 + h], fill=(20, 12, 20))


def paint_kafd(img, x0, y0, w, h):
    """Hero 3: neon night city — dark teal sky, tower silhouettes with
    yellow neon windows, THREE missile streaks with glowing heads, and
    a smoke plume over the struck tower."""
    vgrad(img, (x0, y0, x0 + w, y0 + h), (4, 34, 44), (10, 66, 74))
    d = ImageDraw.Draw(img)
    for sx, sy, r in ((18, 10, 2), (52, 22, 1), (96, 8, 2), (150, 16, 1),
                      (196, 10, 2), (224, 24, 1), (120, 28, 1)):
        d.ellipse([x0 + sx - r, y0 + sy - r, x0 + sx + r, y0 + sy + r],
                  fill=(220, 235, 255))
    towers = [(8, 46, 26, 78), (44, 58, 24, 66), (80, 34, 30, 90),
              (124, 52, 26, 72), (162, 62, 24, 62), (198, 44, 28, 80)]
    for tx, ty, tw, th in towers:
        d.rectangle([x0 + tx, y0 + ty, x0 + tx + tw, y0 + h], fill=(8, 22, 30))
        for wy in range(y0 + ty + 8, y0 + h - 8, 12):
            for wx in range(x0 + tx + 5, x0 + tx + tw - 5, 9):
                if (wx + wy) % 27 < 14:
                    d.rectangle([wx, wy, wx + 4, wy + 5], fill=(255, 196, 60))
    # Three missile streaks, glowing heads (yellow-white core, red halo).
    for (sx, sy, ex, ey) in ((10, 6, 96, 52), (70, 2, 150, 44), (130, 10, 206, 58)):
        d.line([x0 + sx, y0 + sy, x0 + ex, y0 + ey], fill=(255, 80, 40), width=3)
        d.line([x0 + sx, y0 + sy, x0 + ex, y0 + ey], fill=(255, 170, 40), width=1)
        d.ellipse([x0 + ex - 6, y0 + ey - 6, x0 + ex + 6, y0 + ey + 6],
                  fill=(255, 90, 50))
        d.ellipse([x0 + ex - 3, y0 + ey - 3, x0 + ex + 3, y0 + ey + 3],
                  fill=(255, 240, 180))
    px, py = x0 + 96, y0 + 40
    for dx, dy, r, col in ((-10, 6, 11, (70, 70, 78)), (0, 0, 13, (100, 100, 112)),
                           (10, 6, 10, (70, 70, 78)), (0, -9, 9, (138, 138, 150))):
        d.ellipse([px + dx - r, py + dy - r, px + dx + r, py + dy + r], fill=col)


def paint_akvan(img, x0, y0, w, h):
    """Hero 4: storm radar — storm-blue field, concentric cyan/white
    radar rings, diagonal rain, sandy coast and rescue boats."""
    vgrad(img, (x0, y0, x0 + w, y0 + h), (16, 58, 120), (28, 84, 148))
    d = ImageDraw.Draw(img)
    cx, cy = x0 + w * 0.56, y0 + h * 0.40
    for r, col, wd in ((46, (0, 214, 226), 4), (36, (255, 255, 255), 3),
                       (26, (0, 214, 226), 3), (16, (255, 255, 255), 3)):
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=wd)
    d.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=(255, 92, 74))
    for i in range(9):
        x1 = x0 + 12 + i * 24
        d.line([x1, y0 + 8, x1 - 10, y0 + 34], fill=(150, 200, 235), width=2)
        x2 = x0 + w - 14 - i * 24
        d.line([x2, y0 + 44, x2 - 10, y0 + 70], fill=(150, 200, 235), width=2)
    coast_y = y0 + h - 20
    d.polygon([(x0, coast_y + 6), (x0 + w * 0.34, coast_y - 8),
               (x0 + w, coast_y + 2), (x0 + w, y0 + h), (x0, y0 + h)],
              fill=(214, 190, 140))
    for bx, by in ((x0 + 26, coast_y - 2), (x0 + w - 58, coast_y + 2)):
        d.polygon([(bx, by), (bx + 26, by), (bx + 21, by + 8), (bx + 5, by + 8)],
                  fill=(255, 255, 255))
        d.polygon([(bx, by), (bx + 13, by - 9), (bx + 13, by)], fill=(255, 140, 0))
        d.line([bx + 13, by - 9, bx + 13, by], fill=(24, 24, 24), width=2)


HERO_PAINTERS = {
    "summit": paint_summit,
    "kerch": paint_kerch,
    "kafd": paint_kafd,
    "akvan": paint_akvan,
}

# ------------------------------------------------------------------ compose
def _fit_checks(d):
    """Fail loudly (before drawing) if any text would overflow its box,
    so a bad fit is caught here instead of silently clipping in the PNG."""
    for _n, _p, _t, _r, _i, head, deck, _s in FEATURED:
        assert d.textlength(deck, font=font(SANS, 9)) <= 218, f"deck too long: {deck}"
        assert len(wrap(d, head, font(SANS_B, 12), 218)) <= 2, f"headline too long: {head}"
    for _n, _p, _r, txt, src in BRIEFS:
        line = f"{_p} \u2014 {txt} ({src})"
        assert d.textlength(line, font=font(SANS_B, 10)) <= 322, f"brief too long: {line}"
    for _k, _num, _chip, _band, head, deck in HEROES:
        assert len(wrap(d, head, font(SANS_B, 14), 222)) <= 3, f"hero head too long: {head}"
        assert len(wrap(d, deck, font(SANS, 10), 222)) <= 3, f"hero deck too long: {deck}"


def compose():
    img = Image.new("RGB", (W, H), PAGE)
    d = ImageDraw.Draw(img)
    _fit_checks(d)

    # ---- masthead: dark navy, gold kicker, white sans title, colour bar
    d.text((M, 12), "ONE DAY OF WORLD NEWS, ONE PICTURE",
           font=font(SANS_B, 12), fill=GOLD)
    right = "50 STORIES  \u00b7  7 REGIONS  \u00b7  EVERY ONE FROM THIS FRIDAY"
    d.text((W - M - d.textlength(right, font=font(SANS_B, 12)), 12), right,
           font=font(SANS_B, 12), fill=WHITE)
    d.text((M, 30), "Friday 20 November 2026", font=font(SANS_B, 56), fill=WHITE)
    d.text((M, 92), "Three leaders sign a declaration \u00b7 A bridge falls a third time "
                    "\u00b7 A storm comes ashore",
           font=font(SERIF_I, 14), fill=(255, 220, 120))
    colour_bar(d, M, 110, W - 2 * M, 6, [GOLD, CORAL, CYAN, LIME, MAGENTA, ORANGE])

    # ---- THE DAY IN UTC: six coloured chips
    chip_w, gap = 160, 6
    for i, (tt, ev, col) in enumerate(UTC_STRIP):
        x = M + i * (chip_w + gap)
        d.rounded_rectangle([x, 124, x + chip_w, 156], radius=6, fill=col)
        d.text((x + 8, 129), tt, font=font(SANS_B, 9), fill=WHITE)
        d.text((x + 8, 142), ev, font=font(SANS, 9), fill=WHITE)

    # ---- region pills, centred
    pill_w = []
    for name, n, _c in REGIONS:
        t = f"{name} {n}"
        pill_w.append(d.textlength(t, font=font(SANS_B, 11)) + 18)
    total = sum(pill_w) + gap * (len(REGIONS) - 1)
    x = M + (W - 2 * M - total) // 2
    for (name, n, col), pw in zip(REGIONS, pill_w):
        d.rounded_rectangle([x, 162, x + pw, 186], radius=12, fill=col)
        t = f"{name} {n}"
        d.text((x + (pw - d.textlength(t, font=font(SANS_B, 11))) / 2, 168), t,
               font=font(SANS_B, 11), fill=WHITE)
        x += pw + gap

    # ---- numbers strip: six dark chips, one neon figure each
    for i, (big, cap, col) in enumerate(NUMBERS):
        x = M + i * (chip_w + gap)
        d.rounded_rectangle([x, 192, x + chip_w, 254], radius=6, fill=PANEL)
        d.rectangle([x + 6, 192, x + chip_w - 6, 197], fill=col)
        d.text((x + 10, 202), big, font=font(SANS_B, 24), fill=col)
        draw_wrapped(d, x + 10, 232, cap, font(SANS, 9), 140, LIGHT,
                     leading=11, max_lines=2)

    # ---- heroes: four full-bleed panels, four different scenes/palettes
    hw, hgap = 242, 8
    for i, (key, num, chip, band, head, deck) in enumerate(HEROES):
        x = M + i * (hw + hgap)
        HERO_PAINTERS[key](img, x, 262, hw, 106)
        d = ImageDraw.Draw(img)
        d.rectangle([x, 368, x + hw, 472], fill=band)
        d.rectangle([x, 368, x + hw, 371], fill=GOLD)
        # kicker chip + number badge on the illustration
        kw = d.textlength(chip, font=font(SANS_B, 9)) + 12
        d.rounded_rectangle([x + 8, 270, x + 8 + kw, 288], radius=4, fill=band)
        d.text((x + 14, 274), chip, font=font(SANS_B, 9), fill=WHITE)
        d.ellipse([x + hw - 34, 270, x + hw - 8, 296], fill=WHITE)
        nw = d.textlength(num, font=font(SANS_B, 14))
        d.text((x + hw - 21 - nw / 2, 274), num, font=font(SANS_B, 14), fill=band)
        y, _n = draw_wrapped(d, x + 10, 378, head, font(SANS_B, 14), 222,
                              WHITE, leading=17, max_lines=3)
        draw_wrapped(d, x + 10, y + 4, deck, font(SANS, 10), 222, LIGHT,
                     leading=12, max_lines=3)

    # ---- mid cards: 4 x 3, alternating light tints, thick region bar
    for idx, (num, place, topic, region, ic, head, deck, src) in enumerate(FEATURED):
        r, c = divmod(idx, 4)
        x = M + c * (hw + hgap)
        y = 480 + r * 80
        tint = TINTS[(r + c) % 4]
        col = REGION_COLOUR[region]
        d.rounded_rectangle([x, y, x + hw, y + 76], radius=5, fill=tint)
        d.rectangle([x, y + 4, x + 6, y + 72], fill=col)
        draw_icon(d, ic, x + 12, y + 7, 22, INK, col)
        d.text((x + 40, y + 10), f"{place} \u00b7 {topic}",
               font=font(SANS_B, 9), fill=col)
        sw = d.textlength(src, font=font(SANS, 8))
        d.text((x + hw - 8 - sw, y + 11), src, font=font(SANS, 8), fill=GREY)
        draw_wrapped(d, x + 12, y + 30, head, font(SANS_B, 12), 218, INK,
                     leading=14, max_lines=2)
        d.text((x + 12, y + 60), deck, font=font(SANS, 9), fill=GREY)

    # ---- bottom section headers under one six-colour bar
    colour_bar(d, M, 724, W - 2 * M, 4, [GOLD, CORAL, CYAN, LIME, MAGENTA, ORANGE])
    d.text((M, 732), "WHERE IT HAPPENED", font=font(SANS_B, 13), fill=WHITE)
    d.text((324, 732), "ALSO ON FRIDAY 20 NOVEMBER \u2014 34 MORE STORIES",
           font=font(SANS_B, 13), fill=WHITE)

    # ---- dark navy map with bright region dots
    mx0, my0, mw, mh = M, 748, 296, 142
    d.rounded_rectangle([mx0, my0, mx0 + mw, my0 + 160], radius=6, fill=MAP_BG)
    for poly in CONTINENTS:
        pts = [(mx0 + fx * mw, my0 + fy * mh) for fx, fy in poly]
        d.polygon(pts, fill=LAND)
    dot_region = {n: FEATURED[n - 5][3] for n in range(5, 17)}
    for num, fx, fy in MAP_DOTS:
        px, py = mx0 + fx * mw, my0 + fy * mh
        col = REGION_COLOUR[dot_region[num]] if num >= 5 else ORANGE
        d.ellipse([px - 8, py - 8, px + 8, py + 8], fill=col, outline=WHITE, width=1)
        t = str(num)
        tw = d.textlength(t, font=font(SANS_B, 9))
        d.text((px - tw / 2, py - 6), t, font=font(SANS_B, 9), fill=WHITE)
    key_items = [("EU", BLUE), ("ME", RUST), ("AS", ORANGE),
                 ("AM", PURPLE), ("AF", GREEN), ("OC", TEAL)]
    kx = mx0 + 10
    for label, col in key_items:
        d.ellipse([kx, 894, kx + 8, 902], fill=col)
        d.text((kx + 11, 893), label, font=font(SANS, 8), fill=MIDGREY)
        kx += 11 + d.textlength(label, font=font(SANS, 8)) + 12

    # ---- HOW SURE ARE WE? legend under the map
    d.text((M, 914), "HOW SURE ARE WE?", font=font(SANS_B, 9), fill=GOLD)
    d.ellipse([M, 928, M + 7, 935], fill=LIME)
    d.text((M + 10, 926), "REPORTED \u2014 verified by 2+ sources",
           font=font(SANS, 9), fill=LIGHT)
    d.ellipse([M, 940, M + 7, 947], fill=CORAL)
    d.text((M + 10, 938), "CLAIM \u2014 one side's account",
           font=font(SANS, 9), fill=LIGHT)
    d.text((M + 148, 938), "FORECAST \u2014 scheduled",
           font=font(SANS, 9), fill=LIGHT)

    # ---- briefs: two columns on the dark panel, coloured dots
    for i, (num, place, region, txt, src) in enumerate(BRIEFS):
        col_i, row_i = divmod(i, 17)
        bx = 324 + col_i * 344
        by = 748 + row_i * 11.6
        col = REGION_COLOUR[region]
        d.ellipse([bx, by + 1, bx + 9, by + 10], fill=col)
        d.text((bx + 14, by), place, font=font(SANS_B, 10), fill=WHITE)
        rest = f" \u2014 {txt} ({src})"
        px = bx + 14 + d.textlength(place, font=font(SANS_B, 10))
        d.text((px, by), rest, font=font(SANS, 10), fill=LIGHT)

    # ---- DATE CHECK: red panel, white text
    d.rounded_rectangle([M, 952, W - M, 992], radius=6, fill=REDPANEL)
    d.rounded_rectangle([M + 10, 960, M + 116, 984], radius=4, fill=WHITE)
    d.text((M + 16, 965), "DATE CHECK", font=font(SANS_B, 10), fill=REDPANEL)
    draw_wrapped(d, M + 126, 958, DATE_CHECK[13:], font(SANS, 10),
                 W - M - 126 - 12, WHITE, leading=12, max_lines=2)

    # ---- footer + gold frame
    d.text((M, 996), "Every story here happened, or was first reported, on Friday "
                     "20 November 2026, in some time zone. Disputed claims are "
                     "attributed, not stated as fact.",
           font=font(SANS, 8), fill=MIDGREY)
    d.text((M, 1006), "Sources: Reuters, AP, AFP, BBC, WSJ, CNN, The Hindu, IMD, "
                      "IAEA, Yonhap, Sensor Tower, WHO. Pictures and map: original, "
                      "drawn in code. \u00b7 2026-11-20",
           font=font(SANS, 8), fill=MIDGREY)
    d.rectangle([1, 1, W - 2, H - 2], outline=GOLD, width=4)
    return img


def build():
    img = compose()
    out = Path(__file__).resolve().parent / "entry.png"
    img.save(out, optimize=True)
    import hashlib

    data = out.read_bytes()
    print(f"wrote {out} ({len(data)} bytes) "
          f"sha256={hashlib.sha256(data).hexdigest()}")
    assert img.size == (1024, 1024)
    assert len(data) <= 1_048_576
    return img


if __name__ == "__main__":
    build()
