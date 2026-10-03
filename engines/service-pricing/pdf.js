// Renders guide.html to pkg/Start-Here-Guide.pdf (Letter). Run from this folder: node pdf.js
const path = require('path'); const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const p = await b.newPage();
  await p.goto('file://' + path.join(__dirname, 'guide.html')); await p.waitForTimeout(500);
  await p.pdf({ path: path.join(__dirname, 'pkg', 'Start-Here-Guide.pdf'), width: '8.5in', height: '11in', printBackground: true });
  await b.close(); })();
