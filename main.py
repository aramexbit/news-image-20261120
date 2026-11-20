"""Friday 20 November 2026 — one front page, one picture.

This is the entrypoint for the make.fun news-image-20261120 bounty. It
produces the 1024x1024 PNG that sums up the world's news of Friday
20 November 2026 on a single dark "newswall" page: 50 stories, four
hero panels in four different palettes, a UTC timeline, a numbered
map, and a DATE CHECK box for stories that belong to other days.

The picture is produced one of two ways, and both ways give the exact
same bytes:
1. Preferred way: build the page in memory with the composer that
   lives in build_entry.py and save it with PNG optimisation switched
   on. The composer is fully deterministic — same code, same pixels,
   every single run.
2. Safety net: if the composer cannot be used (for example Pillow is
   missing from the grading container), copy the pre-rendered
   entry.png that ships right next to this file. That file is
   byte-identical to what the first way produces, so the result never
   depends on which way ran.

Before exiting, the finished file is checked: real PNG magic bytes,
exactly 1024 by 1024 pixels, and at most 1 MiB. Anything else is a
hard error, not a silent success.

Run it like this:
    mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
When MAKEFUN_OUTPUT_DIR is not set, the output goes to /output.
"""

import hashlib
import os
import struct
import sys
from pathlib import Path

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
SIDE = 1024
BYTE_LIMIT = 1_048_576
OUTPUT_ENV = "MAKEFUN_OUTPUT_DIR"
IMAGE_NAME = "entry.png"

_HERE = Path(__file__).resolve().parent


def die(reason):
    """Print an error and exit non-zero."""
    print(f"main.py: {reason}", file=sys.stderr)
    return SystemExit(1)


def check_picture(path):
    """Return (size, sha256) after validating a finished PNG file."""
    blob = path.read_bytes()
    if len(blob) > BYTE_LIMIT:
        raise ValueError(f"{path} is {len(blob)} bytes, over the 1 MiB limit")
    if blob[:8] != PNG_MAGIC:
        raise ValueError(f"{path} does not start with PNG magic bytes")
    width, height = struct.unpack(">II", blob[16:24])
    if (width, height) != (SIDE, SIDE):
        raise ValueError(f"{path} is {width}x{height}, expected 1024x1024")
    return len(blob), hashlib.sha256(blob).hexdigest()


def render_via_composer(destination):
    """Compose the page in memory and save it optimised. True on success.

    Prefers compose() (pure, no side effects); falls back to build()
    if a future composer only exposes that name.
    """
    sys.path.insert(0, str(_HERE))
    import build_entry

    make_picture = getattr(build_entry, "compose", None) or build_entry.build
    picture = make_picture()
    destination.parent.mkdir(parents=True, exist_ok=True)
    picture.save(destination, optimize=True)
    return True


def render_via_prebuilt(destination):
    """Copy the shipped pre-rendered image byte for byte. True on success."""
    source = _HERE / IMAGE_NAME
    if not source.is_file():
        return False
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(source.read_bytes())
    return True


def main():
    out_dir = Path(os.environ.get(OUTPUT_ENV, "/output"))
    target = out_dir / IMAGE_NAME

    composed = False
    try:
        composed = render_via_composer(target)
    except Exception as exc:  # noqa: BLE001 - any composer failure falls back
        print(f"main.py: composer unavailable ({exc}); using prebuilt image",
              file=sys.stderr)

    if not composed:
        try:
            copied = render_via_prebuilt(target)
        except Exception as exc:  # noqa: BLE001 - report copy failures plainly
            return die(f"prebuilt copy failed: {exc}")
        if not copied:
            return die("no prebuilt entry.png next to main.py")

    try:
        size, digest = check_picture(target)
    except ValueError as exc:
        return die(str(exc))

    print(f"wrote {target} ({size} bytes) sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
