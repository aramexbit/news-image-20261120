#!/usr/bin/env python3
"""news-image-20261120 entrypoint (make.fun, Python 3.13).

Renders the entry image deterministically and writes it to
$MAKEFUN_OUTPUT_DIR/entry.png (default /output/entry.png).

Primary path: import build_entry and call build(). Fallback: if the
import or the build fails, copy the prebuilt entry.png shipped next to
this file, so the grader still receives a valid 1024x1024 image.
No network, no clock, no randomness outside the seeded generator in
build_entry.py — two runs write byte-identical files.
Entry image: 50 stories from Friday 20 November 2026 (see BUILD_LOG.md).
"""

import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
OUT = OUT_DIR / "entry.png"


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    try:
        sys.path.insert(0, str(HERE))
        import build_entry

        img = build_entry.build()
        img.save(OUT, optimize=True)
    except Exception as exc:  # fallback: ship the prebuilt image
        print(f"build failed ({exc!r}); falling back to prebuilt entry.png",
              file=sys.stderr)
        src = HERE / "entry.png"
        if not src.exists():
            raise
        shutil.copyfile(src, OUT)
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
