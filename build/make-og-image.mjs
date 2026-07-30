// Renders build/og-image.html to assets/img/og-image.png (1200x630).
//   npm i playwright && node build/make-og-image.mjs
import { chromium } from 'playwright';
import { fileURLToPath } from 'node:url';
import path from 'node:path';

const here = path.dirname(fileURLToPath(import.meta.url));
const browser = await chromium.launch({
  executablePath: process.env.CHROME_PATH || undefined,
  args: ['--no-sandbox', '--allow-file-access-from-files'],
});
const page = await (await browser.newContext({ viewport: { width: 1200, height: 630 } })).newPage();
await page.goto('file://' + path.join(here, 'og-image.html'), { waitUntil: 'networkidle' });
await page.waitForTimeout(600);
await page.screenshot({ path: path.join(here, '..', 'assets', 'img', 'og-image.png') });
await browser.close();
console.log('wrote assets/img/og-image.png');
