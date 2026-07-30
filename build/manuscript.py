#!/usr/bin/env python3
"""Shared manuscript parsing for the build scripts.

The manuscript is a Google-Docs markdown export: every devotion is a `# `
heading wrapped in `**bold**`, paragraphs are blank-line separated, and the
exporter has backslash-escaped a lot of punctuation. Scripture passages sit at
the top of each devotion, italicised end to end.
"""

import html
import re
from pathlib import Path

__all__ = [
    "load_sections",
    "to_paragraphs",
    "inline_markup",
    "split_scripture",
    "first_reference",
    "plain_text",
]


def unescape_markdown(text: str) -> str:
    """Drop the backslash escapes and stray artifacts left by the export."""
    text = text.replace("(WEBP)", "")
    text = re.sub(r"\\([\\`*_{}\[\]()#+\-.!])", r"\1", text)
    return text.strip()


def load_sections(path) -> dict:
    """Return {heading: [raw line, ...]} for every `# ` heading, bold stripped."""
    sections, heading, buf = {}, None, []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            if heading:
                sections[heading] = buf
            heading, buf = re.sub(r"^\*\*|\*\*$", "", line[2:].strip()), []
        elif heading is not None:
            buf.append(line)
    if heading:
        sections[heading] = buf
    return sections


def to_paragraphs(lines) -> list:
    """Group raw lines into cleaned paragraph blocks."""
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


def _is_scripture(block: str) -> bool:
    """A wholly-italicised block is a Scripture passage.

    Every devotion opens with its passage, and the manuscript italicises those
    blocks end to end. A long quotation is often split over several blocks with
    the reference only on the last, so the test cannot require the reference.
    Bold blocks are excluded so `**...**` headings never match.
    """
    block = block.strip()
    return (
        block.startswith("*")
        and not block.startswith("**")
        and block.endswith("*")
        and not block.endswith("**")
    )


def split_scripture(paragraphs):
    """Split leading Scripture blocks from the body that follows."""
    scripture, body = [], []
    for block in paragraphs:
        if _is_scripture(block) and not body:
            scripture.append(block)
        else:
            body.append(block)
    return scripture, body


REFERENCE_RE = re.compile(
    r"\(((?:1 |2 |3 )?[A-Z][a-z]+\.? ?\d+:\d+(?:[-–,]\s?\d+)*(?:\s?[A-Z]{2,4})?)\)"
)


def first_reference(paragraphs) -> str:
    """The first Scripture reference in the passage, e.g. 'Genesis 29:30-35'."""
    for block in paragraphs:
        match = REFERENCE_RE.search(block)
        if match:
            return match.group(1).strip()
    return ""


def plain_text(block: str) -> str:
    """Markup-free text, for meta descriptions and excerpts."""
    out = re.sub(r"[*_]", "", block)
    return re.sub(r"\s+", " ", out).strip()
