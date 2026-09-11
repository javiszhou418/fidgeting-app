import { chromium } from 'playwright';
import { join } from 'path';

const outDir = '/Users/jiawei.zhou/Documents/Fidgeting app/Artifacts/SweepsReference/capture';
const browser = await chromium.launch({ headless: true });
const context = await browser.newContext({
  viewport: { width: 390, height: 844 },
  deviceScaleFactor: 3,
  recordVideo: { dir: outDir, size: { width: 390, height: 844 } },
});
const page = await context.newPage();
const log = [];

await page.goto('https://sweeps.me/#how-it-works', { waitUntil: 'networkidle', timeout: 60000 });
await page.waitForTimeout(2500);

// scroll until Pull Packs visible
for (let i = 0; i < 6; i++) {
  const visible = await page.locator('text=Pull Packs').first().isVisible().catch(() => false);
  if (visible) break;
  await page.mouse.wheel(0, 700);
  await page.waitForTimeout(600);
}
await page.screenshot({ path: join(outDir, 'pullpacks-01-visible.png') });

// find all pack images in page
const packs = await page.locator('img[src*="pack-"]').all();
log.push({ packImageCount: packs.length });
for (let i = 0; i < packs.length; i++) {
  const src = await packs[i].getAttribute('src');
  const box = await packs[i].boundingBox();
  log.push({ i, src, box });
}

// swipe on each visible pack image
for (let i = 0; i < packs.length; i++) {
  const box = await packs[i].boundingBox();
  if (!box || box.width < 40) continue;
  const cx = box.x + box.width / 2;
  const cy = box.y + box.height / 2;
  for (const [dx, dy, label] of [[-140,0,'h-left'],[140,0,'h-right'],[0,140,'v-down'],[0,-140,'v-up'],[-100,-100,'diag']]) {
    await page.mouse.move(cx - dx/2, cy - dy/2);
    await page.mouse.down();
    await page.mouse.move(cx + dx/2, cy + dy/2, { steps: 24 });
    await page.mouse.up();
    await page.waitForTimeout(500);
    await page.screenshot({ path: join(outDir, `pullpacks-gesture-pack${i}-${label}.png`) });
  }
  await packs[i].click({ timeout: 2000 }).catch(e => log.push({ clickError: String(e) }));
  await page.waitForTimeout(800);
  await page.screenshot({ path: join(outDir, `pullpacks-click-pack${i}.png`) });
}

// try video element interactions
const video = page.locator('video').first();
if (await video.count()) {
  await video.scrollIntoViewIfNeeded();
  await page.screenshot({ path: join(outDir, 'pullpacks-video-visible.png') });
  const box = await video.boundingBox();
  if (box) {
    const cx = box.x + box.width/2, cy = box.y + box.height/2;
    await page.mouse.move(cx-100, cy);
    await page.mouse.down();
    await page.mouse.move(cx+100, cy, { steps: 20 });
    await page.mouse.up();
    await page.waitForTimeout(1000);
    await page.screenshot({ path: join(outDir, 'pullpacks-video-swipe.png') });
  }
}

import { writeFileSync } from 'fs';
writeFileSync(join(outDir, 'pullpacks-log.json'), JSON.stringify(log, null, 2));
console.log(JSON.stringify(log, null, 2));

await page.close();
await context.close();
await browser.close();
