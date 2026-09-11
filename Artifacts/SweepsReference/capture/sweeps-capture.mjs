import { chromium } from 'playwright';
import { mkdirSync } from 'fs';
import { join } from 'path';

const outDir = '/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/SweepsReference/capture';
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 3,
  recordVideo: { dir: outDir, size: { width: 390, height: 844 } },
});
const page = await context.newPage();

const report = { urls: [], clicks: [], errors: [] };

page.on('console', msg => report.errors.push(`console:${msg.type()}:${msg.text()}`));

async function snap(name) {
  await page.screenshot({ path: join(outDir, `${name}.png`), fullPage: true });
  report.urls.push({ name, url: page.url() });
}

try {
  await page.goto('https://sweeps.me/', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(2000);
  await snap('01-home');

  // try /app
  await page.goto('https://sweeps.me/app', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(2000);
  await snap('02-app');

  // scroll and interact on homepage
  await page.goto('https://sweeps.me/', { waitUntil: 'networkidle', timeout: 60000 });
  for (let i = 0; i < 8; i++) {
    await page.mouse.wheel(0, 500);
    await page.waitForTimeout(800);
  }
  await snap('03-home-scrolled');

  // look for pack images / carousel / buttons
  const texts = await page.locator('button, a, [role=button]').allTextContents();
  report.clicks.push({ buttons: texts.filter(Boolean).slice(0, 40) });

  // try clicking anything pack-related
  const candidates = [
    'text=Pull Packs',
    'text=Open Packs',
    'text=Download',
    'text=SILVER',
    'text=BASIC',
    'text=ULTRA',
    'img[alt*="pack" i]',
    'video',
  ];
  for (const sel of candidates) {
    const loc = page.locator(sel).first();
    if (await loc.count()) {
      try {
        await loc.scrollIntoViewIfNeeded({ timeout: 3000 });
        await loc.click({ timeout: 3000 });
        await page.waitForTimeout(1500);
        await snap(`click-${sel.replace(/[^a-z0-9]+/gi,'-').slice(0,30)}`);
        report.clicks.push({ sel, url: page.url() });
      } catch (e) {
        report.clicks.push({ sel, error: String(e.message || e) });
      }
    }
  }

  // horizontal swipe on pack carousel area if present
  const box = await page.locator('img[src*="pack-"]').first().boundingBox();
  if (box) {
    const cx = box.x + box.width / 2;
    const cy = box.y + box.height / 2;
    await page.mouse.move(cx + 120, cy);
    await page.mouse.down();
    await page.mouse.move(cx - 120, cy, { steps: 20 });
    await page.mouse.up();
    await page.waitForTimeout(1200);
    await snap('04-carousel-swipe');
  }

  // try /redeem
  await page.goto('https://sweeps.me/redeem', { waitUntil: 'networkidle', timeout: 60000 });
  await page.waitForTimeout(1500);
  await snap('05-redeem');

} catch (e) {
  report.errors.push(String(e));
}

await page.close();
await context.close();
await browser.close();

import { writeFileSync } from 'fs';
writeFileSync(join(outDir, 'capture-report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2));
