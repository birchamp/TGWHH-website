#!/usr/bin/env python3
"""Turn a Google Fonts css2 response into self-hosted woff2 + assets/css/fonts.css.

Only the `latin` subset is kept; the site has no other scripts on it.
Invoked by build/fetch-fonts.sh.
"""
import pathlib
import re
import subprocess
import sys

src = pathlib.Path(sys.argv[1]).read_text()
blocks = re.findall(r"/\*\s*([a-z0-9\-\[\]]+)\s*\*/\s*@font-face\s*\{(.*?)\}", src, re.S)

faces = []
for subset, body in blocks:
    if subset != "latin":
        continue
    family = re.search(r"font-family:\s*'([^']+)'", body).group(1)
    weight = re.search(r"font-weight:\s*(\d+)", body).group(1)
    style = re.search(r"font-style:\s*(\w+)", body).group(1)
    url = re.search(r"url\((https://[^)]+\.woff2)\)", body).group(1)
    urange = re.search(r"unicode-range:\s*([^;]+);", body).group(1).strip()

    slug = family.lower().replace(" ", "-")
    filename = f"{slug}-{weight}{'-italic' if style == 'italic' else ''}.woff2"
    dest = pathlib.Path("assets/fonts") / filename
    subprocess.run(["curl", "-sSL", url, "-o", str(dest)], check=True)
    faces.append((family, style, weight, filename, urange))
    print(f"  {filename}  {dest.stat().st_size // 1024} KB")

lines = [
    "/* Self-hosted webfonts (latin subset) — no third-party requests at runtime.",
    "   Regenerate with build/fetch-fonts.sh */",
    "",
]
for family, style, weight, filename, urange in faces:
    lines += [
        "@font-face {",
        f"  font-family: '{family}';",
        f"  font-style: {style};",
        f"  font-weight: {weight};",
        "  font-display: swap;",
        f"  src: url('../fonts/{filename}') format('woff2');",
        f"  unicode-range: {urange};",
        "}",
    ]
pathlib.Path("assets/css/fonts.css").write_text("\n".join(lines) + "\n")
print(f"wrote assets/css/fonts.css ({len(faces)} faces)")
