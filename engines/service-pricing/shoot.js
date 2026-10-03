// Renders the five 2000x2000 listing images from mock.html into img/. Needs real sheet screenshots in hi/ first.
const path = require('path'); const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage({ viewport: { width: 2000, height: 2000 } });
  await p.goto('file://' + path.join(__dirname, 'mock.html')); await p.waitForTimeout(800);
  for (const i of [1, 2, 3, 4, 5]) { const el = await p.$('#v' + i); await el.screenshot({ path: path.join(__dirname, 'img', `0${i}.png`) }); }
  await b.close(); })();
