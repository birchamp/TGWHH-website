#!/usr/bin/env python3
"""Build the free sample-chapter PDF from the manuscript.

Usage:
    python3 build/make-sample-pdf.py path/to/manuscript.md

Extracts the Hagar devotions, renders them into a print stylesheet, and prints
to PDF with headless Chromium (already installed at CHROME_PATH below).

Output: downloads/the-god-who-hears-her-sample-chapter.pdf
"""

import html
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME_PATH = os.environ.get(
    "CHROME_PATH", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"
)
OUT_PDF = ROOT / "downloads" / "the-god-who-hears-her-sample-chapter.pdf"
WORK_HTML = ROOT / "build" / "sample-chapter.html"

# Devotions included in the free sample, in reading order.
WANTED = [
    "Affliction",
    "The Outsider *Ezer* \\- a Wilderness Theologian",
    "The Provider in the Wilderness",
]

DAY_LABELS = ["Day One", "Day Two", "Day Three"]


def unescape_markdown(text: str) -> str:
    """Drop the backslash escapes and stray artifacts left by the export."""
    text = text.replace("(WEBP)", "")
    text = re.sub(r"\\([\\`*_{}\[\]()#+\-.!])", r"\1", text)
    return text.strip()


def parse_sections(md: str):
    """Return {plain heading: [paragraph, ...]} for every `# ` heading."""
    sections = {}
    heading, buf = None, []
    for line in md.splitlines():
        if line.startswith("# "):
            if heading:
                sections[heading] = buf
            heading, buf = line[2:].strip(), []
        elif heading is not None:
            buf.append(line)
    if heading:
        sections[heading] = buf
    return sections


def to_paragraphs(lines):
    """Group raw lines into paragraph blocks."""
    blocks, current = [], []
    for line in lines:
        if line.strip():
            current.append(line.strip())
        elif current:
            blocks.append(" ".join(current))
            current = []
    if current:
        blocks.append(" ".join(current))
    return [b for b in (unescape_markdown(b) for b in blocks) if b]


def inline_markup(text: str) -> str:
    """Escape HTML, then restore *italics* and **bold**."""
    out = html.escape(text)
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"\*(.+?)\*", r"<em>\1</em>", out)
    return out


def render_devotion(day_label: str, title: str, paragraphs: list) -> str:
    parts = [
        '<section class="devotion">',
        f'  <p class="day">{html.escape(day_label)}</p>',
        f"  <h2>{inline_markup(title)}</h2>",
    ]
    # The first block(s) of every devotion are the Scripture passage, wholly
    # italicised in the manuscript. Pull those into a highlighted block.
    body_started = False
    for block in paragraphs:
        is_scripture = block.startswith("*") and block.rstrip().endswith(")*")
        if is_scripture and not body_started:
            parts.append(f'  <blockquote class="scripture">{inline_markup(block)}</blockquote>')
        else:
            body_started = True
            parts.append(f"  <p>{inline_markup(block)}</p>")
    parts.append("</section>")
    return "\n".join(parts)


def bullet(text: str) -> str:
    return f"<li>{text}</li>"


FONT_CSS = """
@font-face { font-family: 'Cormorant Garamond'; font-weight: 400; font-style: normal;
  src: url('../assets/fonts/cormorant-garamond-400.woff2') format('woff2'); }
@font-face { font-family: 'Cormorant Garamond'; font-weight: 400; font-style: italic;
  src: url('../assets/fonts/cormorant-garamond-400-italic.woff2') format('woff2'); }
@font-face { font-family: 'Cormorant Garamond'; font-weight: 600; font-style: normal;
  src: url('../assets/fonts/cormorant-garamond-600.woff2') format('woff2'); }
@font-face { font-family: 'Jost'; font-weight: 400; font-style: normal;
  src: url('../assets/fonts/jost-400.woff2') format('woff2'); }
@font-face { font-family: 'Jost'; font-weight: 500; font-style: normal;
  src: url('../assets/fonts/jost-500.woff2') format('woff2'); }
@font-face { font-family: 'Kaushan Script'; font-weight: 400; font-style: normal;
  src: url('../assets/fonts/kaushan-script-400.woff2') format('woff2'); }
"""

PAGE_CSS = """
@page { size: 5.5in 8.5in; margin: 0.72in 0.68in 0.8in; }
@page :first { margin: 0; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
  margin: 0;
  font-family: "Cormorant Garamond", Georgia, "Times New Roman", serif;
  font-size: 12.4pt;
  line-height: 1.56;
  color: #22262e;
}
.cover {
  page-break-after: always;
  height: 8.5in;
  width: 5.5in;
  background: #171d24;
  color: #f3ede1;
  padding: 1.15in 0.75in;
  display: flex;
  flex-direction: column;
  text-align: center;
  position: relative;
}
.cover .rule { width: 54px; height: 1px; background: #c9a227; margin: 0 auto; }
.cover p { text-align: center; }
.cover .eyebrow {
  font-family: "Jost", "Helvetica Neue", Arial, sans-serif;
  font-size: 8pt;
  letter-spacing: 0.32em;
  text-transform: uppercase;
  color: #c9a227;
  margin: 0 0 26px;
}
.cover h1 {
  font-size: 27pt;
  line-height: 1.14;
  letter-spacing: 0.03em;
  font-weight: normal;
  text-transform: uppercase;
  color: #e7c96b;
  margin: 0 0 6px;
}
.cover h1 .script {
  display: block;
  text-transform: none;
  font-family: "Kaushan Script", cursive;
  font-size: 31pt;
  line-height: 1.1;
  letter-spacing: 0.01em;
  color: #f0d98c;
  margin-top: 4px;
}
.cover .subtitle {
  font-size: 12pt;
  font-style: italic;
  color: #e4dccc;
  margin: 22px 0 0;
}
.cover .vessels { display: block; margin: 34px auto 30px; }
.cover .author {
  font-family: "Jost", "Helvetica Neue", Arial, sans-serif;
  font-size: 11pt;
  letter-spacing: 0.2em;
  text-transform: uppercase;
  color: #d8b64a;
  margin: 0;
}
.cover .foot {
  margin-top: auto;
  font-family: "Jost", "Helvetica Neue", Arial, sans-serif;
  font-size: 7.6pt;
  letter-spacing: 0.22em;
  text-transform: uppercase;
  color: #8b9099;
}
.welcome { page-break-after: always; }
h1.section-title {
  font-size: 17pt;
  font-weight: normal;
  letter-spacing: 0.02em;
  color: #1d2530;
  margin: 0 0 4px;
}
.kicker {
  font-family: "Jost", "Helvetica Neue", Arial, sans-serif;
  font-size: 7.6pt;
  letter-spacing: 0.26em;
  text-transform: uppercase;
  color: #a3852a;
  margin: 0 0 14px;
}
.gold-rule { width: 44px; height: 2px; background: #c9a227; margin: 18px 0 22px; }
.devotion { page-break-before: always; }
.devotion .day {
  font-family: "Jost", "Helvetica Neue", Arial, sans-serif;
  font-size: 7.6pt;
  letter-spacing: 0.26em;
  text-transform: uppercase;
  color: #a3852a;
  margin: 0 0 8px;
}
.devotion h2 {
  font-size: 16pt;
  font-weight: normal;
  line-height: 1.24;
  color: #1d2530;
  margin: 0 0 16px;
}
.devotion h2 em { font-style: italic; }
blockquote.scripture {
  margin: 0 0 16px;
  padding: 12px 0 12px 16px;
  border-left: 2px solid #c9a227;
  background: #faf7f0;
  font-size: 11.4pt;
  line-height: 1.5;
  color: #3a3f49;
}
blockquote.scripture em { font-style: italic; }
p { margin: 0 0 11px; text-align: justify; hyphens: auto; }
ul { margin: 0 0 14px; padding-left: 18px; }
li { margin-bottom: 6px; }
.closing { page-break-before: always; text-align: center; padding-top: 0.6in; }
.closing p { text-align: center; }
.closing .url {
  font-family: "Jost", "Helvetica Neue", Arial, sans-serif;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  font-size: 9.5pt;
  color: #a3852a;
}
"""

def vessels_svg() -> str:
    """The site's vessel artwork, inlined (Chromium will not fetch it over file://)."""
    svg = (ROOT / "assets" / "img" / "vessels.svg").read_text(encoding="utf-8")
    svg = re.sub(r"<\?xml.*?\?>", "", svg).strip()
    return svg.replace('width="520" height="300"', 'width="250" class="vessels"', 1)


def build_html(sections) -> str:
    devotions = []
    for label, key in zip(DAY_LABELS, WANTED):
        if key not in sections:
            raise SystemExit(f"Devotion not found in manuscript: {key!r}")
        paragraphs = to_paragraphs(sections[key])
        devotions.append(render_devotion(label, key, paragraphs))

    receive = "\n".join(
        bullet(t)
        for t in (
            "<strong>Scripture first.</strong> Every devotion opens with the passage itself, "
            "not a paraphrase of it.",
            "<strong>Honest reflection.</strong> These women are not tidied up, and neither "
            "are we.",
            "<strong>A question to carry.</strong> Each day ends with something to sit with "
            "rather than solve.",
        )
    )

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>The God Who Hears Her — Free Sample Chapter</title>
<style>{FONT_CSS}{PAGE_CSS}</style>
</head>
<body>

<div class="cover">
  <p class="eyebrow">Free Sample &middot; Three Devotions</p>
  <h1>The God Who<span class="script">Hears Her</span></h1>
  <p class="subtitle">Being known by God through<br>the women of Genesis</p>
  {vessels_svg()}
  <p class="author">Dr. Connie Champeon</p>
  <p class="foot">thegodwhohearsher.com</p>
</div>

<section class="welcome">
  <p class="kicker">Before you begin</p>
  <h1 class="section-title">Welcome</h1>
  <div class="gold-rule"></div>
  <p>Thank you for opening this. What follows are three devotions from
  <em>The God Who Hears Her</em>, a sixty-day journey through the women of Genesis.</p>
  <p>I have chosen Hagar for your sample, and I chose her on purpose. She is an outsider,
  a slave and a foreigner, afflicted by the very covenant family that should have sheltered
  her. She is also the first person in all of Scripture to give God a name. If God met her
  in the wilderness&mdash;and He did, twice&mdash;then there is no wilderness where He will
  not meet you.</p>
  <p>These pages are not a tidy study. The stories of the women of Genesis are complex,
  nuanced and often painful, and I have tried not to look away from any of it. What I have
  found, again and again, is that God does not look away either.</p>
  <p>You are seen. You are heard. Read on.</p>
  <div class="gold-rule"></div>
  <p class="kicker">What each devotion gives you</p>
  <ul>
{receive}
  </ul>
  <p>&mdash; Dr. Connie Champeon</p>
</section>

{chr(10).join(devotions)}

<section class="closing">
  <div class="gold-rule" style="margin: 0 auto 24px;"></div>
  <p class="kicker">Keep reading</p>
  <p>These three devotions are part of a sixty-day journey through the women of Genesis&mdash;
  Sarah, Hagar, Rebekah, Leah, Rachel, Dinah, Tamar and the many unnamed women whose cries
  God recorded.</p>
  <p>For release news and occasional encouragement, stay on the list at</p>
  <p class="url">thegodwhohearsher.com</p>
  <div class="gold-rule" style="margin: 24px auto 0;"></div>
  <p style="margin-top:28px; font-size:8.6pt; color:#6b7280;">
    &copy; Dr. Connie Champeon. Sample material shared for personal reading.<br>
    Scripture quotations are from the World English Bible unless otherwise noted.
  </p>
</section>

</body>
</html>
"""


def main():
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    md = Path(sys.argv[1]).read_text(encoding="utf-8")
    sections = parse_sections(md)
    # Headings carry markdown bold: `# **Affliction**`.
    flat = {re.sub(r"^\*\*|\*\*$", "", k).strip(): v for k, v in sections.items()}
    WORK_HTML.write_text(build_html(flat), encoding="utf-8")

    OUT_PDF.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            CHROME_PATH,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            "--no-pdf-header-footer",
            f"--print-to-pdf={OUT_PDF}",
            WORK_HTML.as_uri(),
        ],
        check=True,
        capture_output=True,
    )
    print(f"wrote {OUT_PDF} ({OUT_PDF.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
