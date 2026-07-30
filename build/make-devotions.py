#!/usr/bin/env python3
"""Generate the free devotion library from the manuscript.

    python3 build/make-devotions.py path/to/manuscript.md [--light]

Writes:
    devotions/index.html          the library index
    devotions/<slug>.html         one page per devotion in DEVOTIONS
    sitemap.xml                   regenerated to include every page

These pages exist to be *found*. A landing page with 600 words can only ever
rank for the book's own title, which nobody searches for before launch. Each
devotion here targets a phrase women are already searching ("ezer kenegdo
meaning", "Leah unloved", "Rebekah watered the camels") and carries the same
email capture form, so organic search feeds the list.

Deliberately excluded: the three Hagar devotions in the sample PDF. The free
pages and the lead magnet must not be the same text, or signing up buys the
reader nothing.
"""

import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from manuscript import (  # noqa: E402  (path set above)
    first_reference,
    inline_markup,
    load_sections,
    plain_text,
    split_scripture,
    to_paragraphs,
)

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "devotions"
SITE = "https://thegodwhohearsher.com"

# heading .................. the manuscript's `# ` heading, verbatim
# slug ..................... the URL
# title .................... <title> and the search result headline
# description .............. meta description, ~155 chars
# woman / reference ........ shown on the card and page furniture
DEVOTIONS = [
    {
        "heading": "Who Did God Create Women to Be?",
        "slug": "ezer-kenegdo-what-helper-really-means",
        "title": "Ezer Kenegdo: What “Helper” Really Means in Genesis 2:18",
        "description": (
            "The Hebrew word behind “helper” describes God sixteen times in the Old "
            "Testament. A close look at ezer kenegdo, and why “suitable helper” lost "
            "the strength of the original."
        ),
        "woman": "Eve",
    },
    {
        "heading": "A Woman of Formidable Strength",
        "slug": "rebekah-watered-the-camels",
        "title": "Rebekah Watered the Camels: A Woman of Formidable Strength",
        "description": (
            "Ten camels after a desert journey is somewhere near 250 gallons of water, "
            "drawn by hand. What Rebekah's welcome at the spring actually cost her."
        ),
        "woman": "Rebekah",
    },
    {
        "heading": "When Men Treat You as a Commodity",
        "slug": "leah-when-men-treat-you-as-a-commodity",
        "title": "Leah's Wedding Night: When Men Treat You as a Commodity",
        "description": (
            "Leah is handed over in the dark, unwanted, and blamed for it. A devotion on "
            "being treated as a transaction, and the God who was watching."
        ),
        "woman": "Leah",
    },
    {
        "heading": "God is Near to the Broken-hearted",
        "slug": "leah-unloved-god-near-to-the-brokenhearted",
        "title": "Leah, Unloved: The God Who Is Near to the Broken-Hearted",
        "description": (
            "“The LORD has seen that I am hated.” Leah names her sons after her grief, and "
            "God answers by putting her in the line of the Messiah."
        ),
        "woman": "Leah",
    },
    {
        "heading": "Husbands are Terrible gods",
        "slug": "husbands-are-terrible-gods",
        "title": "Husbands Are Terrible gods: Rachel's Demand in Genesis 30",
        "description": (
            "“Give me children, or else I will die.” On asking a person for what only God "
            "can give — and what it does to both of you."
        ),
        "woman": "Rachel",
    },
]

PDF = "the-god-who-hears-her-sample-chapter.pdf"


def esc(text: str) -> str:
    return html.escape(text, quote=True)


def head(*, title, description, canonical, up, theme, extra=""):
    """Shared <head>. `up` is the relative path back to the site root."""
    theme_attr = ' data-theme="light"' if theme == "light" else ""
    bg = "#f8f3e9" if theme == "light" else "#0f1419"
    return f"""<!doctype html>
<!-- GENERATED FILE — do not edit. Run: python3 build/make-devotions.py <manuscript.md> -->
<html lang="en"{theme_attr}>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(description)}">
<link rel="canonical" href="{canonical}">
<meta name="theme-color" content="{bg}">

<meta property="og:type" content="article">
<meta property="og:site_name" content="The God Who Hears Her">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(description)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{SITE}/assets/img/og-image.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta name="twitter:card" content="summary_large_image">

<link rel="icon" href="{up}assets/img/favicon.svg" type="image/svg+xml">
<link rel="preload" as="font" type="font/woff2" href="{up}assets/fonts/cormorant-garamond-500.woff2" crossorigin>
<link rel="preload" as="font" type="font/woff2" href="{up}assets/fonts/jost-300.woff2" crossorigin>
<link rel="stylesheet" href="{up}assets/css/fonts.css">
<link rel="stylesheet" href="{up}assets/css/styles.css">
{extra}</head>
<body>

<a class="skip-link" href="#free-chapter">Skip to the free chapter form</a>

<header class="topbar topbar--static">
  <div class="wrap topbar__inner">
    <a class="topbar__mark" href="{up}index.html">
      <span class="topbar__mark-a">The God Who</span>
      <span class="topbar__mark-b">Hears Her</span>
    </a>
    <a class="btn btn--ghost btn--sm topbar__cta" href="#free-chapter">Free Chapter</a>
  </div>
</header>
"""


def capture_block(up: str, *, heading: str, intro: str) -> str:
    """The one thing every page on this site is for."""
    return f"""
  <section class="section section--capture" id="free-chapter">
    <div class="wrap wrap--narrow">
      <div class="capture">

        <div class="capture__head">
          <p class="eyebrow eyebrow--center">Free sample chapter</p>
          <h2 class="h2 center">{heading}</h2>
          <span class="ornament" aria-hidden="true"></span>
          <p class="capture__intro">{intro}</p>
        </div>

        <form class="form" id="chapter-form" novalidate
              action="https://formspree.io/f/YOUR_FORM_ID" method="POST">
          <div class="field">
            <label for="firstName">First name</label>
            <input id="firstName" name="firstName" type="text" autocomplete="given-name"
                   required placeholder="Mary" spellcheck="false">
            <p class="field__error" id="firstName-error" hidden>Please tell us your first name.</p>
          </div>

          <div class="field">
            <label for="email">Email address</label>
            <input id="email" name="email" type="email" autocomplete="email" required
                   inputmode="email" placeholder="you@example.com" spellcheck="false">
            <p class="field__error" id="email-error" hidden>Please enter a valid email address.</p>
          </div>

          <div class="hp" aria-hidden="true">
            <label for="_gotcha">Leave this field empty</label>
            <input id="_gotcha" name="_gotcha" type="text" tabindex="-1" autocomplete="off">
          </div>

          <button class="btn btn--gold btn--block" type="submit" id="submit-btn">
            <span class="btn__label">Send Me the Free Chapter</span>
            <span class="btn__spinner" aria-hidden="true"></span>
          </button>

          <p class="form__fine">
            No spam, ever. Your email is never shared or sold, and one click unsubscribes you.
          </p>
        </form>

        <div class="thanks" id="thanks" hidden tabindex="-1">
          <span class="thanks__seal" aria-hidden="true">
            <svg viewBox="0 0 48 48" fill="none" stroke="currentColor" stroke-width="1.6"
                 stroke-linecap="round" stroke-linejoin="round">
              <circle cx="24" cy="24" r="20"/><path d="M15 24.5l6.5 6.5L34 18"/>
            </svg>
          </span>
          <h3 class="thanks__title">Your chapter is on its way, <span id="thanks-name">friend</span>.</h3>
          <p class="thanks__body">
            The download should have started automatically. If it didn&rsquo;t, the link below
            will do it &mdash; and a copy is headed to your inbox.
          </p>
          <a class="btn btn--gold" id="thanks-download"
             href="{up}downloads/{PDF}"
             download="The-God-Who-Hears-Her-Sample-Chapter.pdf">
            Download the PDF
          </a>
          <p class="thanks__fine">
            One more thing: add Connie to your contacts so the release news doesn&rsquo;t land
            in spam.
          </p>
        </div>

        <p class="form__status" id="form-status" role="status" aria-live="polite"></p>
      </div>
    </div>
  </section>
"""


def footer(up: str) -> str:
    return f"""
<footer class="footer">
  <div class="wrap footer__inner">
    <p class="footer__title">
      The God Who <span class="footer__script">Hears Her</span>
    </p>
    <nav class="footer__nav">
      <a href="{up}index.html">The book</a>
      <a href="{up}devotions/index.html">Free devotions</a>
      <a href="{up}index.html#author">About Connie</a>
    </nav>
    <p class="footer__meta">
      &copy; <span id="year">2026</span> Dr. Connie Champeon &middot; thegodwhohearsher.com
    </p>
    <p class="footer__meta footer__meta--faint">
      Scripture quotations are from the World English Bible unless otherwise noted.
    </p>
  </div>
</footer>

<div class="stickybar" id="stickybar" hidden>
  <a class="btn btn--gold btn--block" href="#free-chapter">Get the Free Chapter</a>
</div>

<script src="{up}assets/js/main.js" defer></script>
</body>
</html>
"""


def article_jsonld(item, reference, canonical) -> str:
    import json

    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": item["title"],
        "description": item["description"],
        "author": {"@type": "Person", "name": "Dr. Connie Champeon"},
        "publisher": {"@type": "Person", "name": "Dr. Connie Champeon"},
        "mainEntityOfPage": canonical,
        "inLanguage": "en",
        "isPartOf": {
            "@type": "Book",
            "name": "The God Who Hears Her",
            "url": SITE + "/",
        },
        "about": [item["woman"]] + ([reference] if reference else []),
    }
    crumbs = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "The God Who Hears Her",
             "item": SITE + "/"},
            {"@type": "ListItem", "position": 2, "name": "Free devotions",
             "item": SITE + "/devotions/"},
            {"@type": "ListItem", "position": 3, "name": item["title"], "item": canonical},
        ],
    }
    return ('<script type="application/ld+json">\n'
            + json.dumps(data, indent=2, ensure_ascii=False)
            + "\n</script>\n"
            + '<script type="application/ld+json">\n'
            + json.dumps(crumbs, indent=2, ensure_ascii=False)
            + "\n</script>\n")


def render_devotion(item, sections, index, total, theme) -> str:
    if item["heading"] not in sections:
        sys.exit(f"Devotion not found in manuscript: {item['heading']!r}")

    paragraphs = to_paragraphs(sections[item["heading"]])
    scripture, body = split_scripture(paragraphs)
    reference = first_reference(scripture) or first_reference(paragraphs)
    canonical = f"{SITE}/devotions/{item['slug']}.html"
    words = sum(len(plain_text(b).split()) for b in body)

    passage = "\n".join(
        f'        <p>{inline_markup(b)}</p>' for b in scripture
    )

    # The mid-article CTA goes at a paragraph break about a third of the way in —
    # where a reader who is enjoying this is most persuadable. Never before the
    # second paragraph, and skipped entirely on short pieces where it would
    # crowd the writing.
    cut = max(2, round(len(body) / 3)) if len(body) >= 4 else len(body)
    before = "\n".join(f"      <p>{inline_markup(b)}</p>" for b in body[:cut])
    after = "\n".join(f"      <p>{inline_markup(b)}</p>" for b in body[cut:])

    inline_cta = "" if not body[cut:] else """
      <aside class="inline-cta">
        <p class="inline-cta__lead">
          This is one of sixty devotions through the women of Genesis.
        </p>
        <p class="inline-cta__body">
          Three more &mdash; the whole Hagar section &mdash; are yours as a free PDF.
        </p>
        <a class="btn btn--gold btn--sm" href="#free-chapter">Get the free chapter</a>
      </aside>
"""

    prev_item = DEVOTIONS[index - 1] if index > 0 else None
    next_item = DEVOTIONS[index + 1] if index < total - 1 else None
    nav = []
    if prev_item:
        nav.append(f'      <a class="pager__link pager__link--prev" href="{prev_item["slug"]}.html">'
                   f'<span class="pager__dir">Previous</span>'
                   f'<span class="pager__title">{esc(prev_item["heading"])}</span></a>')
    if next_item:
        nav.append(f'      <a class="pager__link pager__link--next" href="{next_item["slug"]}.html">'
                   f'<span class="pager__dir">Next</span>'
                   f'<span class="pager__title">{esc(next_item["heading"])}</span></a>')

    return (
        head(title=item["title"], description=item["description"], canonical=canonical,
             up="../", theme=theme, extra=article_jsonld(item, reference, canonical))
        + f"""
<main>
  <article class="article">
    <div class="wrap wrap--narrow">

      <nav class="crumbs" aria-label="Breadcrumb">
        <a href="../index.html">The book</a>
        <span aria-hidden="true">&rsaquo;</span>
        <a href="index.html">Free devotions</a>
      </nav>

      <p class="eyebrow">{esc(item["woman"])}{" &middot; " + esc(reference) if reference else ""}</p>
      <h1 class="article__title">{inline_markup(item["heading"])}</h1>
      <p class="article__meta">
        From <em>The God Who Hears Her</em> by Dr. Connie Champeon
        <span aria-hidden="true">&middot;</span> {max(1, round(words / 220))} min read
      </p>
      <span class="ornament ornament--left" aria-hidden="true"></span>

      <blockquote class="scripture">
{passage}
      </blockquote>

{before}

{inline_cta}
{after}

    </div>
  </article>
"""
        + (f"""
  <nav class="pager wrap wrap--narrow" aria-label="More devotions">
{chr(10).join(nav)}
  </nav>
""" if nav else "")
        + capture_block(
            "../",
            heading="Keep reading, free",
            intro="Three full devotions from the Hagar section, typeset as a PDF you can "
                  "read tonight or print. Plus release news when the book is ready.",
        )
        + "</main>\n"
        + footer("../")
    )


def render_index(items, sections, theme) -> str:
    canonical = f"{SITE}/devotions/"
    cards = []
    for item in items:
        paragraphs = to_paragraphs(sections[item["heading"]])
        scripture, body = split_scripture(paragraphs)
        reference = first_reference(scripture) or first_reference(paragraphs)
        excerpt = plain_text(body[0]) if body else ""
        if len(excerpt) > 190:
            excerpt = excerpt[:190].rsplit(" ", 1)[0] + "…"
        cards.append(f"""        <li class="dev-card">
          <a class="dev-card__link" href="{item['slug']}.html">
            <p class="dev-card__tag">{esc(item['woman'])}{" &middot; " + esc(reference) if reference else ""}</p>
            <h2 class="dev-card__title">{inline_markup(item['heading'])}</h2>
            <p class="dev-card__excerpt">{esc(excerpt)}</p>
            <span class="dev-card__more">Read the devotion</span>
          </a>
        </li>""")

    import json
    listing = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "Free devotions from The God Who Hears Her",
        "itemListElement": [
            {"@type": "ListItem", "position": i + 1, "name": d["title"],
             "url": f"{SITE}/devotions/{d['slug']}.html"}
            for i, d in enumerate(items)
        ],
    }

    return (
        head(
            title="Free Devotions on the Women of Genesis | The God Who Hears Her",
            description=(
                "Read five full devotions from The God Who Hears Her — on Eve, Rebekah, "
                "Leah, and Rachel — free, with no email required."
            ),
            canonical=canonical,
            up="../",
            theme=theme,
            extra='<script type="application/ld+json">\n'
                  + json.dumps(listing, indent=2, ensure_ascii=False) + "\n</script>\n",
        )
        + f"""
<main>
  <section class="section section--library">
    <div class="wrap wrap--narrow">
      <nav class="crumbs" aria-label="Breadcrumb">
        <a href="../index.html">The book</a>
      </nav>
      <p class="eyebrow">Free to read</p>
      <h1 class="h2">Devotions from the book</h1>
      <span class="ornament ornament--left" aria-hidden="true"></span>
      <div class="prose">
        <p class="lede">
          Five full devotions, no email required. Read one and see whether you want
          the other fifty-five.
        </p>
      </div>
    </div>

    <div class="wrap">
      <ul class="dev-cards">
{chr(10).join(cards)}
      </ul>
    </div>
  </section>
"""
        + capture_block(
            "../",
            heading="Send me the free chapter",
            intro="The Hagar section — three devotions the pages above don't include — as a "
                  "PDF, plus release news when the book is ready.",
        )
        + "</main>\n"
        + footer("../")
    )


def write_sitemap(items) -> None:
    urls = [(SITE + "/", "1.0", "monthly"), (SITE + "/devotions/", "0.8", "monthly")]
    urls += [(f"{SITE}/devotions/{d['slug']}.html", "0.7", "yearly") for d in items]
    body = "\n".join(
        f"  <url>\n    <loc>{loc}</loc>\n"
        f"    <changefreq>{freq}</changefreq>\n"
        f"    <priority>{pri}</priority>\n  </url>"
        for loc, pri, freq in urls
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!-- GENERATED by build/make-devotions.py -->\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{body}\n</urlset>\n",
        encoding="utf-8",
    )


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args:
        sys.exit(__doc__)
    theme = "light" if "--light" in sys.argv else "dark"

    sections = load_sections(args[0])
    OUT_DIR.mkdir(exist_ok=True)

    for i, item in enumerate(DEVOTIONS):
        page = render_devotion(item, sections, i, len(DEVOTIONS), theme)
        (OUT_DIR / f"{item['slug']}.html").write_text(page, encoding="utf-8")
        print(f"  devotions/{item['slug']}.html")

    (OUT_DIR / "index.html").write_text(
        render_index(DEVOTIONS, sections, theme), encoding="utf-8")
    print("  devotions/index.html")

    write_sitemap(DEVOTIONS)
    print(f"  sitemap.xml ({len(DEVOTIONS) + 2} urls)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
