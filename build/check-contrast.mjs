// WCAG contrast audit for both colour ways.
//
//   npm i playwright
//   python3 -m http.server 8137 &
//   node build/check-contrast.mjs [baseUrl]
//
// Reads composited computed styles from a real browser, so it accounts for
// translucent layers and for gradient-clipped text (which is checked against
// its lightest stop — the worst case). Exits non-zero if anything fails.
import { chromium } from 'playwright';

const TARGETS = [
  ['.eyebrow', 'eyebrow (uppercase 11.8px)'],
  ['.h2', 'section heading'],
  ['.lede', 'lede'],
  ['.prose p', 'body copy'],
  ['.hero__subtitle', 'hero subtitle'],
  ['.hero__support', 'hero support line'],
  ['.hero__microcopy', 'CTA microcopy'],
  ['.hero__trust li', 'hero trust items'],
  ['.names li', 'name chips'],
  ['.pullquote p', 'pull quote'],
  ['.pullquote cite', 'pull quote citation'],
  ['.card h3', 'card heading'],
  ['.card p', 'card body'],
  ['.author__sig', 'author signature'],
  ['.capture__intro', 'form intro'],
  ['.field label', 'field label'],
  ['#firstName', 'input text'],
  ['.form__fine', 'form fine print'],
  ['.footer__title', 'footer title'],
  ['.footer__meta', 'footer meta'],
  ['.footer__meta--faint', 'footer meta faint'],
  ['.topbar__mark-a', 'topbar mark'],
  ['.btn--gold .btn__label', 'CTA button label'],
  ['.thanks__body', 'thank-you body'],
  ['.thanks__fine', 'thank-you fine print'],
  ['.crumbs a', 'breadcrumb link'],
  ['.article__title', 'article title'],
  ['.article__meta', 'article byline'],
  ['.article .scripture p', 'article scripture'],
  ['.article > .wrap > p', 'article body copy'],
  ['.inline-cta__lead', 'inline CTA lead'],
  ['.inline-cta__body', 'inline CTA body'],
  ['.pager__dir', 'pager direction'],
  ['.pager__title', 'pager title'],
  ['.dev-card__tag', 'devotion card tag'],
  ['.dev-card__title', 'devotion card title'],
  ['.dev-card__excerpt', 'devotion card excerpt'],
  ['.dev-card__more', 'devotion card link'],
  ['.footer__nav a', 'footer nav link'],
  ['.display__line', 'hero display line 1'],
  ['.display__script', 'hero display script'],
  ['.thanks__title span', 'thank-you name'],
  ['.topbar__mark-b', 'topbar script mark'],
  ['.card__icon svg', 'card icon (graphic)'],
  ['.field__error', 'field error text'],
];

const BASE = process.argv[2] || 'http://127.0.0.1:8137/';
let failures = 0;

const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || undefined,
  args: ['--no-sandbox'],
});

const FILES = process.argv.slice(3);
for (const file of (FILES.length ? FILES : [
  'index.html',
  'light.html',
  'devotions/index.html',
  'devotions/ezer-kenegdo-what-helper-really-means.html',
])) {
  const page = await (await browser.newContext({ viewport: { width: 1280, height: 900 } })).newPage();
  await page.goto(new URL(file, BASE).href, { waitUntil: 'networkidle' });
  // reveal everything and open the thank-you panel so its text is measurable
  await page.evaluate(() => {
    document.querySelectorAll('.reveal').forEach(e => e.classList.add('is-in'));
    document.getElementById('thanks').hidden = false;
  });
  await page.waitForTimeout(300);

  const rows = await page.evaluate((targets) => {
    const px = v => parseFloat(v);
    const parse = c => {
      const m = c.match(/rgba?\(([\d.]+),\s*([\d.]+),\s*([\d.]+)(?:,\s*([\d.]+))?\)/);
      return m ? [ +m[1], +m[2], +m[3], m[4] === undefined ? 1 : +m[4] ] : null;
    };
    const over = (fg, bg) => fg.slice(0,3).map((c,i) => c*fg[3] + bg[i]*(1-fg[3]));
    const lum = ([r,g,b]) => {
      const f = c => { c /= 255; return c <= 0.03928 ? c/12.92 : Math.pow((c+0.055)/1.055, 2.4); };
      return 0.2126*f(r) + 0.7152*f(g) + 0.0722*f(b);
    };
    const ratio = (a, b) => { const l1 = lum(a), l2 = lum(b); const [hi, lo] = l1 > l2 ? [l1, l2] : [l2, l1]; return (hi + 0.05) / (lo + 0.05); };

    // effective background: walk ancestors for the first opaque-ish paint,
    // compositing any translucent layers on the way.
    const bgOf = (el, skipSelf) => {
      const stack = [];
      for (let n = skipSelf ? el.parentElement : el; n && n !== document.documentElement; n = n.parentElement) {
        const cs = getComputedStyle(n);
        if (cs.backgroundImage !== 'none') {
          // sample the gradient's own colour stops; take the last (usually the base)
          const cols = [...cs.backgroundImage.matchAll(/rgba?\([^)]+\)/g)].map(m => parse(m[0])).filter(Boolean);
          const solid = cols.filter(c => c[3] > 0.85);
          if (solid.length) { stack.push(solid[solid.length - 1]); break; }
        }
        const c = parse(cs.backgroundColor);
        if (c && c[3] > 0) { stack.push(c); if (c[3] > 0.85) break; }
      }
      const base = parse(getComputedStyle(document.body).backgroundColor) || [255,255,255,1];
      let acc = base.slice(0,3);
      for (let i = stack.length - 1; i >= 0; i--) acc = over(stack[i], acc);
      return acc;
    };

    const extra = [];
    {
      const inp = document.querySelector('#firstName');
      const ph = getComputedStyle(inp, '::placeholder').color;
      const bg = bgOf(inp);
      const fg = parse(ph);
      extra.push({ label: 'input placeholder', sel: '::placeholder', ratio: +ratio(over(fg, bg), bg).toFixed(2), size: 17, need: 4.5, fg: over(fg,bg).map(Math.round).join(','), bg: bg.map(Math.round).join(','), note: '' });
    }
    return extra.concat(targets.map(([sel, label]) => {
      const el = document.querySelector(sel);
      if (!el) return { label, sel, missing: true };
      const cs = getComputedStyle(el);
      let fg = parse(cs.color);
      // gradient-clipped text paints its background-image, not `color`
      let note = '';
      if (cs.webkitTextFillColor === 'rgba(0, 0, 0, 0)' || cs.color === 'rgba(0, 0, 0, 0)') {
        const cols = [...cs.backgroundImage.matchAll(/rgba?\([^)]+\)/g)].map(m => parse(m[0])).filter(Boolean);
        if (cols.length) {
          // worst case is the lightest stop against a light page
          const bgc = bgOf(el, true);
          cols.sort((a,b) => ratio(a.slice(0,3), bgc) - ratio(b.slice(0,3), bgc));
          fg = cols[0];
          note = 'gradient text, worst stop';
        }
      }
      const bg = bgOf(el, !!note);
      const rgb = over(fg, bg);
      const size = px(cs.fontSize);
      const weight = parseInt(cs.fontWeight, 10) || 400;
      const large = size >= 24 || (size >= 18.66 && weight >= 700);
      return {
        label, sel, note,
        ratio: +ratio(rgb, bg).toFixed(2),
        size: +size.toFixed(1),
        need: large ? 3 : 4.5,
        fg: rgb.map(Math.round).join(','),
        bg: bg.map(Math.round).join(','),
      };
    }));
  }, TARGETS);

  console.log('\n=== ' + file + ' ===');
  for (const r of rows) {
    if (r.missing) continue;  // selector not present on this page type
    const ok = r.ratio >= r.need;
    if (!ok) failures++;
    console.log(`  ${ok ? 'PASS' : 'FAIL'} ${String(r.ratio).padStart(5)}:1 (need ${r.need})  ${r.size}px  ${r.label}${r.note ? ' [' + r.note + ']' : ''}  fg(${r.fg}) bg(${r.bg})`);
  }
  await page.context().close();
}
await browser.close();

if (failures) {
  console.error(`\n${failures} contrast failure(s).`);
  process.exit(1);
}
console.log('\nAll checks pass WCAG AA.');
