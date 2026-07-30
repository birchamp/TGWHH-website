#!/usr/bin/env python3
"""Generate light.html (cream theme) from index.html.

index.html is the single source of markup. This script only flips the theme
attribute and the browser chrome colour, so the two pages can never drift.

    python3 build/make-light.py
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "index.html"
DEST = ROOT / "light.html"

BANNER = (
    "<!-- GENERATED FILE — do not edit.\n"
    "     Cream-theme variant of index.html. Edit index.html, then run\n"
    "     python3 build/make-light.py -->\n"
)

# Kept out of search results so the two variants don't compete while the
# final look is being chosen. Drop this line once one of them wins.
NOINDEX = '<meta name="robots" content="noindex, nofollow">\n'


def main() -> int:
    html = SRC.read_text(encoding="utf-8")

    if '<html lang="en">' not in html:
        sys.exit("index.html: expected a plain <html lang=\"en\"> tag to flip")
    html = html.replace('<html lang="en">', '<html lang="en" data-theme="light">', 1)

    html = html.replace(
        '<meta name="theme-color" content="#0f1419">',
        '<meta name="theme-color" content="#f8f3e9">',
        1,
    )

    # Point the canonical at the dark page; this variant is not a second entry.
    html = re.sub(r'(\n)(<meta name="theme-color")', r"\1" + NOINDEX + r"\2", html, count=1)

    html = re.sub(r"^<!doctype html>\n", "<!doctype html>\n" + BANNER, html, count=1,
                  flags=re.IGNORECASE)

    DEST.write_text(html, encoding="utf-8")
    print(f"wrote {DEST.relative_to(ROOT)} ({len(html) // 1024} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
