import { chromium } from 'playwright';
import { join } from 'path';
import { mkdirSync, writeFileSync } from 'fs';

const outDir = '/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/SweepsReference/capture/deep-scroll';
mkdirSync(outDir, { recursive: true });

const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 3,
  recordVideo: { dir: outDir, size: { width: 390, height: 844 } },
  hasTouch: true,
});
const page = await context.newPage();
const report = { scrolls: [], interactions: [] };

await page.goto('https://sweeps.me/', { waitUntil: 'networkidle', timeout: 90000 });
await page.waitForTimeout(2000);

for (let step = 0; step < 25; step++) {
  const scrollY = step * 350;
  await page.evaluate(y => window.scrollTo({ top: y, behavior: 'instant' }), scrollY);
  await page.waitForTimeout(900);
  const info = await page.evaluate(() => ({
    scrollY: window.scrollY,
    visibleText: Array.from(document.querySelectorAll('h1,h2,h3,p'))
      .filter(el => { const r = el.getBoundingClientRect(); return r.top >= 0 && r.top < window.innerHeight * 0.8; })
      .map(el => el.textContent?.trim()).filter(Boolean).slice(0, 10),
    visiblePacks: Array.from(document.querySelectorAll('img[src*="pack-"]'))
      .filter(el => { const r = el.getBoundingClientRect(); return r.width > 40 && r.top > -20 && r.top < window.innerHeight; })
      .map(el => ({ src: el.getAttribute('src'), alt: el.alt, w: Math.round(el.getBoundingClientRect().width), y: Math.round(el.getBoundingClientRect().y) })),
    videos: Array.from(document.querySelectorAll('video')).map(v => ({ src: v.currentSrc, w: Math.round(v.getBoundingClientRect().width), y: Math.round(v.getBoundingClientRect().y), paused: v.paused })),
  }));
  report.scrolls.push(info);
  await page.screenshot({ path: join(outDir, `scroll-${String(step).padStart(2,'0')}.png`) });
}

// Pull Packs phone mockup - swipe on video and surrounding area
await page.locator('text=Pull Packs').first().scrollIntoViewIfNeeded({ timeout: 10000 });
await page.waitForTimeout(1500);

const video = page.locator('video').first();
if (await video.count()) {
  const box = await video.boundingBox();
  report.interactions.push({ videoBox: box });
  if (box) {
    const cx = box.x + box.width/2, cy = box.y + box.height/2;
    for (const [dx, dy, label] of [[-100,0,'left'],[100,0,'right'],[0,80,'down'],[0,-80,'up']]) {
      await page.mouse.move(cx - dx/2, cy - dy/2);
      await page.mouse.down();
      await page.mouse.move(cx + dx/2, cy + dy/2, { steps: 25 });
      await page.mouse.up();
      await page.waitForTimeout(1200);
      await page.screenshot({ path: join(outDir, `video-swipe-${label}.png`) });
    }
  }
}

// swipe on center pack in hero carousel (top section)
await page.evaluate(() => window.scrollTo({ top: 0 }));
await page.waitForTimeout(1000);
const heroPack = page.locator('img[alt="Blue Pack"]').first();
if (await heroPack.count()) {
  const box = await heroPack.boundingBox();
  if (box) {
    const cx = box.x + box.width/2, cy = box.y + box.height/2;
    for (let s = 0; s < 5; s++) {
      await page.mouse.move(cx + 100, cy);
      await page.mouse.down();
      await page.mouse.move(cx - 100, cy, { steps: 25 });
      await page.mouse.up();
      await page.waitForTimeout(900);
      const state = await page.evaluate(() => ({
        alts: Array.from(document.querySelectorAll('img[src*="pack-"]')).map(i => i.alt),
        centerPack: Array.from(document.querySelectorAll('img[src*="pack-"]'))
          .map(i => ({ alt: i.alt, x: i.getBoundingClientRect().x, w: i.getBoundingClientRect().width }))
          .sort((a,b) => Math.abs(a.x - 195) - Math.abs(b.x - 195))[0]
      }));
      report.interactions.push({ heroSwipe: s, state });
      await page.screenshot({ path: join(outDir, `hero-swipe-${s}.png`) });
    }
  }
}

writeFileSync(join(outDir, 'deep-scroll-report.json'), JSON.stringify(report, null, 2));
console.log(JSON.stringify(report, null, 2).slice(0, 12000));

await page.close();
await context.close();
await browser.close();
