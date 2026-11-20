# THE WORLD IN ONE DAY — Friday, 20 November 2026

[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![make.fun rank](https://make.fun/badge/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![make.fun reward](https://make.fun/badge/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)

**Bounty:** [Sum up 20 November's world news in one image](https://make.fun/bounty/news-image-20261120) — $250, top 50 paid.

## What it is

One 1024×1024 picture that sums up Friday, 20 November 2026 in **35 stories**:
a masthead, a UTC timeline of the day, six headline numbers, region tabs,
three illustrated hero stories, ten mid cards, a numbered world map,
22 one-line briefs, a red DATE CHECK box, and a source footer.

The three heroes — the summit of three leaders, the Crimean Bridge strike,
and Cyclone Akvan's landfall — each get their own palette and illustration
style. Every number is set in high-contrast white on a dark chip, and every
brief is set large enough to read at full-image size without zooming.

## How it is made

Pure Pillow, no network, no clock, no randomness — the render is fully
deterministic. `build_entry.py` draws everything (DejaVu Sans) and writes
`entry.png`; `main.py` is the entrypoint and writes the image to
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`).

```bash
python3 build_entry.py   # renders entry.png, prints sha256
python3 main.py          # entrypoint: renders and validates the output
```

## Verification

- `python3 build_entry.py` twice produces byte-identical `entry.png` (same sha256).
- `MAKEFUN_OUTPUT_DIR=out python3 main.py` twice produces the same sha256.
- Output is a 1024×1024 RGB PNG under 1 MiB.
- v3 sha256: `0ebe33af18a53cac3f21640c7a6b5fb590ad18082356c425aadff7dba3df1e93`
  (180,495 bytes).
- Every headline, deck, brief, label and source was checked to fit its box
  before drawing (`_fit_checks()` in `build_entry.py`), and the finished
  image was visually inspected at full 1024 size: all text readable without
  zoom, no overlaps or clipping, all 35 stories and all sources visible.

## License

MIT — see [LICENSE](LICENSE).

---
Entered on make.fun (?ref=rrcbfccn)
