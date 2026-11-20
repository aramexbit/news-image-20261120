#!/usr/bin/env python3
"""news-image-20261120 v3 — entrypoint.

compose() renders the 1024x1024 "THE WORLD IN ONE DAY" image (35 stories)
via build_entry.py and writes it to $MAKEFUN_OUTPUT_DIR/entry.png
(default /output). If rendering fails, it falls back to copying the
bundled entry.png byte-for-byte (open/read/write, never shutil.copyfile).

Written fresh in-session from the v3 brief (21 Nov 2026).
"""
import os
import sys

# The grader runs `python3 -P -s main.py`: -P keeps the script's directory
# OUT of sys.path, so `import build_entry` fails unless we add it back.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import Image

import build_entry


def compose():
    """Render the entry image and return it as a PIL Image."""
    return build_entry.build()


def _copy_bundled_entry(dest):
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
    with open(src, "rb") as fh:
        data = fh.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "bundled entry.png is not a PNG"
    assert len(data) <= 1024 * 1024, "bundled entry.png > 1 MiB"
    with open(dest, "wb") as fh:
        fh.write(data)
    return data


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    try:
        img = compose()
        img.save(dest, format="PNG", optimize=True)
    except Exception as exc:  # noqa: BLE001 - fallback must survive any render error
        print(f"render failed ({exc!r}); falling back to bundled entry.png")
        _copy_bundled_entry(dest)
        img = Image.open(dest)
    with open(dest, "rb") as fh:
        data = fh.read()
    assert data[:8] == b"\x89PNG\r\n\x1a\n", "output is not a PNG"
    assert img.size == (1024, 1024), f"output size {img.size}, expected 1024x1024"
    assert len(data) <= 1024 * 1024, f"output {len(data)} bytes > 1 MiB"
    print(f"wrote {dest}: {img.size} {img.mode} {len(data)} bytes")


if __name__ == "__main__":
    main()
