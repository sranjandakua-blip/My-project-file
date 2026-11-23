// Usage: node record_agent.js "<agent card prompt text>" <outdir> [virtualSeconds=17]
// Records the agent card from the nxtjob.ai carousel at full resolution (DPR 2.5).
// Screencast only yields CSS-pixel frames, so we slow the page clock 5x and take real screenshots,
// saving the virtual timestamp of each frame (outdir/ts.json). Then run frames_to_video.py.
const { chromium } = require('playwright');
const fs = require('fs');
const [,, PROMPT, OUT, SECS = '17'] = process.argv;
if (!PROMPT || !OUT) { console.error('usage: node record_agent.js "<prompt text>" <outdir> [secs]'); process.exit(1); }
fs.mkdirSync(OUT, { recursive: true });
const WARP = `(() => {
  const oNow = performance.now.bind(performance), oDate = Date.now, oST = window.setTimeout.bind(window), oSI = window.setInterval.bind(window), oRAF = window.requestAnimationFrame.bind(window);
  let rate = 1, rB = oNow(), vB = rB; const d0 = oDate() - oNow();
  const vnow = () => vB + (oNow() - rB) * rate;
  window.__setRate = r => { vB = vnow(); rB = oNow(); rate = r; };
  window.__vnow = vnow;
  performance.now = vnow;
  Date.now = () => Math.round(d0 + vnow());
  window.setTimeout = (f, d, ...a) => oST(f, (d || 0) / rate, ...a);
  window.setInterval = (f, d, ...a) => oSI(f, (d || 0) / rate, ...a);
  window.requestAnimationFrame = cb => oRAF(() => cb(vnow()));
})();`;
const RATE = 0.2;
const NEXT = [377, 523], PREV = [54, 523];   // carousel arrows (CSS px) after scrolling the carousel to y=160
(async () => {
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 430, height: 932 }, deviceScaleFactor: 2.5 });
  await ctx.addInitScript(WARP);
  const p = await ctx.newPage();
  await p.goto('https://nxtjob.ai', { waitUntil: 'networkidle', timeout: 90000 }).catch(() => {});
  await p.waitForTimeout(3000);
  const first = p.locator("text=Navigator, I've got").first();   // first card of the carousel
  await first.scrollIntoViewIfNeeded();
  const box0 = await first.boundingBox();
  await p.evaluate(dy => window.scrollBy(0, dy), box0.y - 160);
  await p.waitForTimeout(1500);
  const card = p.locator(`text=${PROMPT}`).first();
  let found = false;
  for (let i = 0; i < 12; i++) {
    const bb = await card.boundingBox();
    if (bb && bb.x > 0 && bb.x < 200) { found = true; break; }
    await p.mouse.click(...NEXT);
    await p.waitForTimeout(900);
  }
  if (!found) { console.error('card not found:', PROMPT); process.exit(2); }
  const isFirst = /Navigator/.test(PROMPT);
  if (!isFirst) { await p.mouse.click(...PREV); await p.waitForTimeout(1500); }
  await p.evaluate(() => { document.querySelectorAll('*').forEach(e => { const s = getComputedStyle(e);
    if (s.position === 'fixed' && e.getBoundingClientRect().top > 700) e.style.visibility = 'hidden'; }); });
  const cdp = await ctx.newCDPSession(p);
  await cdp.send('Animation.enable');
  await cdp.send('Animation.setPlaybackRate', { playbackRate: RATE });
  await p.evaluate(r => window.__setRate(r), RATE);
  if (!isFirst) await p.mouse.click(...NEXT);
  const t0 = await p.evaluate(() => window.__vnow());
  const ts = []; let n = 0;
  for (;;) {
    const v = await p.evaluate(() => window.__vnow());
    if (v - t0 > Number(SECS) * 1000) break;
    await p.screenshot({ path: `${OUT}/f${String(n).padStart(5, '0')}.jpg`, type: 'jpeg', quality: 93,
                         clip: { x: 0, y: 0, width: 430, height: 800 } });
    ts.push((v - t0) / 1000); n++;
  }
  fs.writeFileSync(`${OUT}/ts.json`, JSON.stringify(ts));
  console.log('frames', n, 'virtual secs', ts[ts.length - 1].toFixed(2));
  await b.close();
})();
