# thegodwhohearsher.com

A single-page marketing site for **The God Who Hears Her** — a 60-day devotional through
the women of Genesis by Dr. Connie Champeon.

The site has exactly one job: **collect an email address in exchange for the free sample
chapter PDF.** Every section on the page points at that form.

It is plain static HTML, CSS, and one small JavaScript file. No build step, no framework,
no third-party requests at runtime (the webfonts are self-hosted).

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

## 2. Deploy

Any static host works. Upload the repository root as-is.

- **Netlify** — connect the repo; `netlify.toml` already sets `publish = "."`, security
  headers, and cache lifetimes. No build command.
- **Cloudflare Pages / Vercel** — framework preset "None", output directory `.`.
- **GitHub Pages** — enable Pages on the branch root.

Then point `thegodwhohearsher.com` at the host and make sure HTTPS is on.

---

## 3. Files

```
index.html                     the whole page
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
build/                         scripts that regenerate the generated files
netlify.toml, robots.txt, sitemap.xml
```

### Typography

| Role | Face |
| --- | --- |
| Display / headings | Cormorant Garamond |
| Script accent (“Hears Her”) | Kaushan Script |
| Body / UI | Jost |

### Colour

| Token | Value |
| --- | --- |
| Background | `#0f1419` |
| Card / raised | `#191f2a` |
| Gold | `#c9a227` |
| Gold highlight | `#e5cd85` |
| Cream text | `#f4efe6` |

---

## 4. Regenerating the built files

Both scripts need `python3` and a Chromium binary. Set `CHROME_PATH` if Chromium is not
at the default location.

**The sample-chapter PDF** — three Hagar devotions, a welcome note, and a closing page,
extracted straight from the manuscript:

```bash
python3 build/make-sample-pdf.py path/to/manuscript.md
```

Edit the `WANTED` list at the top of that script to change which devotions go in the
sample.

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

## 5. Three things to swap in before launch

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

## 6. Notes on how it behaves

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
  the page stays consent-banner-free.
