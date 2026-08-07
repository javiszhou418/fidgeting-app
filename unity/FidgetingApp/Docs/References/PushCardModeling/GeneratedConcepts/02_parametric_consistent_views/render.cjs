'use strict';

const fs = require('node:fs');
const http = require('node:http');
const os = require('node:os');
const path = require('node:path');

const ROOT = __dirname;
const VIEWS = [
  ['exploded', '01_exploded.png'],
  ['top', '02_top.png'],
  ['front', '03_front.png'],
  ['back', '04_back_underside.png'],
  ['left', '05_left_end.png'],
  ['right', '06_right_end.png'],
];

function resolvePlaywright() {
  if (process.env.PLAYWRIGHT_MODULE) return require(process.env.PLAYWRIGHT_MODULE);
  try { return require('playwright'); } catch (_) { /* scan npx cache below */ }

  const npxCache = path.join(os.homedir(), '.npm', '_npx');
  if (!fs.existsSync(npxCache)) {
    throw new Error('Playwright not found. Set PLAYWRIGHT_MODULE to its package directory.');
  }
  const candidates = fs.readdirSync(npxCache)
    .map((entry) => path.join(npxCache, entry, 'node_modules', 'playwright'))
    .filter((entry) => fs.existsSync(path.join(entry, 'package.json')))
    .map((entry) => ({ entry, version: JSON.parse(fs.readFileSync(path.join(entry, 'package.json'), 'utf8')).version }))
    .sort((a, b) => b.version.localeCompare(a.version, undefined, { numeric: true }));
  if (!candidates.length) throw new Error('No cached Playwright package found. Set PLAYWRIGHT_MODULE explicitly.');
  console.log(`Using bundled Playwright ${candidates[0].version}`);
  return require(candidates[0].entry);
}

function mimeFor(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  return ({ '.html': 'text/html; charset=utf-8', '.js': 'text/javascript; charset=utf-8', '.png': 'image/png' })[ext] || 'application/octet-stream';
}

function startServer() {
  return new Promise((resolve) => {
    const server = http.createServer((request, response) => {
      const pathname = decodeURIComponent(new URL(request.url, 'http://127.0.0.1').pathname);
      const relative = pathname === '/' ? 'index.html' : pathname.replace(/^\/+/, '');
      const filePath = path.resolve(ROOT, relative);
      if (!filePath.startsWith(`${ROOT}${path.sep}`) || !fs.existsSync(filePath) || fs.statSync(filePath).isDirectory()) {
        console.warn(`HTTP 404 ${pathname} -> ${filePath}`);
        response.writeHead(404).end('Not found');
        return;
      }
      response.writeHead(200, { 'Content-Type': mimeFor(filePath), 'Cache-Control': 'no-store' });
      fs.createReadStream(filePath).pipe(response);
    });
    server.listen(0, '127.0.0.1', () => resolve({ server, port: server.address().port }));
  });
}

function assertManifest(manifest, view) {
  if (manifest.geometrySignature !== 'pushcard-7L-6M-inlineX-zs-frame-v2-final') throw new Error(`${view}: geometry signature mismatch`);
  if (manifest.layerCount !== 7) throw new Error(`${view}: expected exactly 7 layers, got ${manifest.layerCount}`);
  if (manifest.magnetCount !== 6) throw new Error(`${view}: expected exactly 6 magnets, got ${manifest.magnetCount}`);
  if (manifest.magnetAxis !== 'X' || manifest.magnetPositions.some((item) => item.y !== 0)) throw new Error(`${view}: M1–M6 are not on one X-axis centerline`);
  const magnetXs = manifest.magnetPositions.map((item) => item.x);
  if (Math.abs(magnetXs[0] + 4.10) > 1e-9 || Math.abs(magnetXs[5] - 4.10) > 1e-9) throw new Error(`${view}: outer magnet centers must be ±4.10`);
  const magnetPitches = magnetXs.slice(1).map((x, index) => x - magnetXs[index]);
  if (magnetPitches.some((pitch) => Math.abs(pitch - 1.64) > 1e-9)) throw new Error(`${view}: M1–M6 pitch is not uniformly 1.64`);
  if (manifest.alignedSixFeatureLayers.join(',') !== 'L2,L3,L5,L6') throw new Error(`${view}: six-position layer alignment invariant failed`);
  if (manifest.magnetLayer !== 'L5' || manifest.topFrameCornerHoles !== 4) throw new Error(`${view}: final layer allocation invariant failed`);
  if (view !== 'exploded' && Math.abs(manifest.orthographicHeight - 9.2) > 1e-9) throw new Error(`${view}: expected shared orthographic height 9.2, got ${manifest.orthographicHeight}`);
}

(async () => {
  const { chromium } = resolvePlaywright();
  const { server, port } = await startServer();
  let browser;
  try {
    browser = await chromium.launch({
      headless: true,
      args: ['--use-angle=swiftshader', '--enable-webgl', '--ignore-gpu-blocklist', '--font-render-hinting=none'],
    });
    const context = await browser.newContext({
      viewport: { width: 1400, height: 1050 },
      deviceScaleFactor: 2,
      colorScheme: 'light',
    });
    const signatures = new Set();
    for (const [view, filename] of VIEWS) {
      const page = await context.newPage();
      page.on('console', (message) => console.log(`[${view}] browser: ${message.text()}`));
      page.on('pageerror', (error) => console.error(`[${view}] page error: ${error.message}`));
      page.on('requestfailed', (request) => console.error(`[${view}] request failed: ${request.url()} · ${request.failure()?.errorText || 'unknown'}`));
      page.on('response', (response) => { if (response.status() >= 400) console.error(`[${view}] HTTP ${response.status()}: ${response.url()}`); });
      console.log(`Loading ${view} view...`);
      await page.goto(`http://127.0.0.1:${port}/index.html?view=${view}`, { waitUntil: 'networkidle' });
      console.log(`[${view}] state`, await page.evaluate(() => ({ boot: window.__MODEL_BOOT__ || null, ready: window.__RENDER_READY__ || false, canvases: document.querySelectorAll('canvas').length })));
      await page.waitForFunction(() => window.__RENDER_READY__ === true, null, { timeout: 15000 });
      const manifest = await page.evaluate(() => window.__MODEL_MANIFEST__);
      assertManifest(manifest, view);
      signatures.add(manifest.geometrySignature);
      await page.screenshot({ path: path.join(ROOT, filename), fullPage: true });
      await page.close();
      console.log(`Rendered ${filename}`);
    }
    if (signatures.size !== 1) throw new Error('Views did not share one canonical geometry signature');
    await context.close();

    const contactContext = await browser.newContext({ viewport: { width: 2100, height: 1160 }, deviceScaleFactor: 1, colorScheme: 'dark' });
    const contactPage = await contactContext.newPage();
    await contactPage.goto(`http://127.0.0.1:${port}/contact.html`, { waitUntil: 'networkidle' });
    await contactPage.waitForFunction(() => Array.from(document.images).every((image) => image.complete && image.naturalWidth > 0));
    await contactPage.screenshot({ path: path.join(ROOT, '00_contact_sheet.png'), fullPage: true });
    await contactContext.close();
    console.log('Rendered 00_contact_sheet.png');
  } finally {
    if (browser) await browser.close();
    server.close();
  }
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
