# Friday 20 November 2026 — The World in One Picture (v2)

[![make.fun bounty](https://img.shields.io/badge/make.fun-news--image--20261120-red)](https://make.fun/competitions/news-image-20261120)
[![entry](https://img.shields.io/badge/entry-entry.png-blue)](entry.png)
[![license](https://img.shields.io/badge/license-MIT-green)](LICENSE)

One 1024×1024 picture summing up Friday 20 November 2026 in
**50 verified stories**: 4 flat-drawn hero panels (trilateral
declaration, Crimean Bridge, Riyadh KAFD strike, Cyclone Akvan), 12
featured cards, 34 briefs, a numbered world map, a "THE DAY IN UTC"
strip, region pills, a numbers strip, a DATE CHECK panel and a HOW SURE
ARE WE? legend. Every hero and icon is drawn in code with Pillow —
no photographs.

## What v2 changes

v1 was a cream-paper serif newspaper — the same look as the live top 3.
v2 is a **dark navy newswall**: white sans headlines, a gold frame, a
six-colour bar, four heroes in four different saturated palettes and
four different illustration styles, mid cards on alternating light
tints, a neon numbers strip, a dark map and dark briefs panel. Same 50
stories, same facts — a different, bolder, more colourful page.

## Build

```bash
python3 build_entry.py   # writes entry.png next to this file
python3 main.py          # writes $MAKEFUN_OUTPUT_DIR/entry.png (default /output)
```

Deterministic: two runs of either script produce byte-identical PNGs
(no network, no clock, no randomness at all in v2). Verified 1024×1024,
≤ 1 MiB. Layout follows this competition's live top rank: 4 heroes,
THE DAY IN UTC strip, region tabs, numbers strip, numbered map,
DATE CHECK box — rebuilt in a visual system of its own.

## Facts

All 50 stories were cross-checked against live news reporting of
20 November 2026 (Reuters, AP, AFP, BBC, WSJ, CNN, The Hindu, IMD,
IAEA, Yonhap, Sensor Tower, WHO). Stories first reported on 17–19
November are listed in the DATE CHECK panel, not as main stories. The
full verification log is in [BUILD_LOG.md](BUILD_LOG.md).

Made for the [make.fun bounty](https://make.fun/competitions/news-image-20261120)
"Sum up 20 November's world news in one image" ($250 USDC, top 50 paid).
