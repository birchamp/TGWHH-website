# thegodwhohearsher.com

Marketing site for **The God Who Hears Her** — a 60-day devotional through the women of
Genesis by Dr. Connie Champeon.

The site has exactly one job: **collect an email address in exchange for the free sample
chapter PDF.** A long landing page makes the case, and a small library of free devotions
under `/devotions/` brings people in from search — every one of those pages carries the
same form.

Plain static HTML, CSS, and one small JavaScript file. No framework and no third-party
requests at runtime (the webfonts are self-hosted). The generated pages are built from
the manuscript by the scripts in `build/`.

---

## 1. Wire up the email form — the one required step

Out of the box the form hands over the PDF but **does not store the address anywhere.**
Pick a provider and set the endpoint.

### Formspree (fastest — five minutes)

1. Create a free form at <https://formspree.io> and copy its endpoint
   (`https://formspree.io/f/abcdwxyz`).
2. Open `assets/js/main.js` and replace the placeholder near the top:

   ```js
   var FORM_ENDPOINT = 'https://formspree.io/f/abcdwxyz';
   ```

3. Do the same in `index.html` on the `<form action="...">` attribute, so the form still
   works for the rare visitor with JavaScript disabled.

That is all. Submissions land in the Formspree inbox and forward to Connie's email; the
visitor sees the thank-you panel and the PDF download starts immediately.

### Netlify Forms (if you host on Netlify)

1. Add `data-netlify="true"` and `name="sample-chapter"` to the `<form>` in `index.html`.
2. In `assets/js/main.js` set:

   ```js
   var FORM_ENDPOINT = '/';   // Netlify accepts the POST at the page's own path
   ```

Submissions appear under **Forms** in the Netlify dashboard.

### A real mailing list (recommended once the launch gets close)

For sequences and broadcasts, point `FORM_ENDPOINT` at a provider's form-post URL —
ConvertKit/Kit, MailerLite, Mailchimp, and Beehiiv all accept a plain `POST` of
`firstName` + `email`. The field names in `index.html` are `firstName` and `email`;
rename them to whatever the provider expects (`fields[first_name]`, `EMAIL`, and so on)
and the JavaScript will carry them through unchanged.

**Do also set up the delivery email.** The page promises "a copy is headed to your inbox,"
so configure the provider's autoresponder to send the PDF (or a link to it). The instant
download on the page is the primary delivery; the email is what makes the address worth
collecting.

---

## 2. The free devotion library — where the traffic comes from

`/devotions/` holds five full devotions from the manuscript, free and ungated, each
carrying the same capture form as the landing page.

This is not a blog for its own sake. A one-page site with 600 words can only rank for
the book's own title, which nobody searches for before launch. Each of these pages
targets a phrase women are already searching — "ezer kenegdo meaning", "Leah unloved",
"Rebekah watered the camels" — and there is an established audience for exactly this
material (Proverbs 31 Ministries, Salvation Army women's ministries, and dozens of
bloggers publish on the same passages). Organic search feeds the list; the list sells the
book.

The pages are generated from the manuscript:

```bash
python3 build/make-devotions.py path/to/manuscript.md          # dark theme
python3 build/make-devotions.py path/to/manuscript.md --light   # cream theme
```

That writes `devotions/index.html`, one page per entry, and regenerates `sitemap.xml`.
To change which devotions are published, edit the `DEVOTIONS` list at the top of the
script — each entry sets the manuscript heading, the URL slug, and the `<title>` and
meta description used in search results. The `<h1>` keeps Connie's own heading; only the
`<title>` is written for search.

**The five free pages deliberately exclude the three Hagar devotions in the sample PDF.**
The gated thing has to be different from the free thing, or subscribing buys the reader
nothing. If you swap devotions in or out, keep that separation.

### What to do next with this

The pages are the asset; they still need to be found.

1. **Submit the sitemap** in Google Search Console once the domain is live.
2. **Publish more of them over time.** Five is a start; fifteen to twenty covers most of
   the searchable ground in Genesis, and each one is another door into the list.
3. **Link to them from anywhere Connie already speaks** — her ministry bio, conference
   handouts, church newsletters. Links are what make the pages rank.

## 3. Deploy

Any static host works. Upload the repository root as-is.

- **Netlify** — connect the repo; `netlify.toml` already sets `publish = "."`, security
  headers, and cache lifetimes. No build command.
- **Cloudflare Pages / Vercel** — framework preset "None", output directory `.`.
- **GitHub Pages** — enable Pages on the branch root.

Then point `thegodwhohearsher.com` at the host and make sure HTTPS is on.

---

## 4. Files

```
index.html                     the landing page
light.html                     cream variant (generated)
devotions/                     five free devotions + index (generated)
assets/css/styles.css          all styling
assets/css/fonts.css           @font-face rules (generated)
assets/js/main.js              form handling, scroll reveals, sticky CTA
assets/fonts/*.woff2           self-hosted webfonts, latin subset
assets/img/vessels.svg         the vessel + olive-branch line art (used on the page,
                               the book-cover mock, the PDF cover, and the OG image)
assets/img/arcs.svg            blind-emboss arcs on the cover mock
assets/img/pattern.svg         near-invisible page texture
assets/img/favicon.svg         gold ear mark
assets/img/og-image.png        1200x630 social share card (generated)
downloads/*.pdf                the free sample chapter (generated)
build/manuscript.py            shared manuscript parsing
build/make-devotions.py        generates devotions/ and sitemap.xml
build/make-sample-pdf.py       generates the sample-chapter PDF
build/make-light.py            generates light.html
build/check-contrast.mjs       WCAG audit across both themes
build/make-og-image.mjs        generates the social share card
netlify.toml, robots.txt, sitemap.xml
```

### Two colour ways

| Page | Look |
| --- | --- |
| `index.html` | dark — deep slate ground, the original cover palette |
| `light.html` | light — cream paper, deep antique gold |

`light.html` is **generated** from `index.html`, so the markup can never drift:

```bash
python3 build/make-light.py
```

The script only sets `data-theme="light"` on `<html>`, swaps the `theme-color`, and adds
`noindex` so the two variants don't compete in search while you decide. All the light
styling lives in one block at the bottom of `assets/css/styles.css`
(`:root[data-theme="light"] { … }`).

In both themes the **book cover mock stays dark** — it is a physical object sitting on the
page, and a dark board on cream is how the printed book actually looks.

**To make light the live site:** rename `light.html` to `index.html` (move the dark one
aside first), drop the `noindex` line, and set `data-theme="light"` on the new
`index.html`. Then either delete `build/make-light.py` or invert it.

### Typography

| Role | Face |
| --- | --- |
| Display / headings | Cormorant Garamond |
| Script accent (“Hears Her”) | Kaushan Script |
| Body / UI | Jost |

### Colour

| Token | Dark | Light |
| --- | --- | --- |
| Page | `#0f1419` | `#f8f3e9` |
| Card / raised | `#191f2a` | `#fffdf8` |
| Gold (as text) | `#c9a227` | `#7d5f0f` |
| Gold, deeper | `#e5cd85` | `#6a5008` |
| Body text | `#cbd2dc` | `#4a463f` |
| Headings | `#f4efe6` | `#2b2a25` |

The gold differs between themes because a bright `#c9a227` only reaches 3.3:1 on cream —
too low for small text. On the dark ground the same gold is 7.7:1, so it stays.

### Contrast

Every text colour in both themes meets **WCAG 2.1 AA** — 4.5:1 for body and UI text, 3:1
for large display type. That includes the gradient-filled headlines, which are checked
against their *lightest* gradient stop, and the input placeholders.

The audit is worth re-running after any colour change. It measures composited computed
styles in a real browser rather than trusting the source values:

```bash
npm i playwright
python3 -m http.server 8137 &
node build/check-contrast.mjs        # prints PASS/FAIL per element, both themes
```

---

## 5. Regenerating the built files

Both scripts need `python3` and a Chromium binary. Set `CHROME_PATH` if Chromium is not
at the default location.

**Everything from the manuscript** (do these two after any manuscript edit):

```bash
python3 build/make-sample-pdf.py path/to/manuscript.md   # the gated PDF
python3 build/make-devotions.py  path/to/manuscript.md   # the free pages + sitemap
python3 build/make-light.py                              # refresh light.html
```

Edit `WANTED` in `make-sample-pdf.py` to change which devotions go in the PDF, and
`DEVOTIONS` in `make-devotions.py` to change which are published free.

**The social share image:**

```bash
npm i playwright
node build/make-og-image.mjs
```

**The webfonts** (only needed to change weights or add a family):

```bash
./build/fetch-fonts.sh
```

---

## 6. Three things to swap in before launch

**A photo of Connie.** The author section currently shows a gold `CC` monogram as a
placeholder. Drop a square headshot at `assets/img/connie-champeon.jpg` and replace the
`.author__portrait` div in `index.html` with:

```html
<div class="author__portrait reveal">
  <img src="assets/img/connie-champeon.jpg" alt="Dr. Connie Champeon"
       width="416" height="416" loading="lazy">
  <span class="author__ring"></span>
</div>
```

then add to `assets/css/styles.css`:

```css
.author__portrait img { width: 100%; height: 100%; border-radius: 50%; object-fit: cover; }
```

**The book cover.** The hero shows a CSS-and-SVG reconstruction of the cover, which keeps
the page fast and crisp at any size. When the final print cover art is ready, either
leave it (it matches) or replace the contents of `.cover__board` with a single `<img>`.

**A contact address.** `assets/js/main.js` shows `hello@thegodwhohearsher.com` in the
error message if a submission fails. Point that at a real inbox.

---

## 7. Notes on how it behaves

- **The reader always gets the chapter.** If the form endpoint is unreachable — or was
  never configured — the thank-you panel and download still fire. A broken integration
  costs an email address, never a reader.
- **Validation** is client-side and inline (name present, email shaped like an email),
  with `aria-invalid` and `aria-live` wired up for screen readers.
- **Spam** is caught by a hidden `_gotcha` honeypot field, which Formspree and Netlify
  both understand.
- **Accessibility** — skip link, visible focus rings, real labels on every input, and the
  whole page respects `prefers-reduced-motion`.
- **No analytics or trackers** are included. If you add one, prefer a cookieless option so
  the page stays consent-banner-free. Worth doing before long: you cannot tell which
  devotion is earning subscribers without it.
- **The capture form is on every page**, landing page and devotions alike, and the PDF
  path is read off the thank-you link so it resolves correctly from any URL depth.
