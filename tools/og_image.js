// Makes site/og.jpg, the 1200x630 image shown when the site is shared or cited.
// Run from the repo root while the site folder is being served on port 8765:
//   (cd site && python3 -m http.server 8765) &   node tools/og_image.js
const { chromium } = require("playwright");
const html = `<!doctype html><html><head><style>
@font-face{font-family:"Archivo";font-weight:100 900;font-stretch:62% 125%;src:url("fonts/archivo.woff2") format("woff2")}
*{box-sizing:border-box;margin:0}
body{width:1200px;height:630px;overflow:hidden;font-family:"Archivo",Arial,sans-serif;
  background:radial-gradient(900px 600px at 85% 30%,#2C4F9E 0%,#152F70 55%,#0F2357 100%);color:#fff;position:relative}
.copy{position:absolute;left:72px;top:64px;width:700px}
.brand{display:flex;align-items:center;gap:16px;font-weight:900;font-size:34px;letter-spacing:-.01em}
.mark{width:64px;height:64px;border-radius:14px;background:#fff;color:#152F70;display:block}
.mark svg{width:100%;height:100%;display:block}
h1{margin-top:84px;font-size:60px;line-height:1.02;font-weight:900;font-variation-settings:"wdth" 88;letter-spacing:-.015em}
h1 span{display:block;white-space:nowrap}
p{margin-top:30px;max-width:600px;font-size:26px;line-height:1.35;color:#DCE4F5;font-weight:500}
.phone{position:absolute;left:72px;bottom:58px;background:#BF4A08;color:#fff;font-weight:800;font-size:30px;padding:14px 28px;border-radius:12px}
.cooper{position:absolute;right:28px;bottom:-40px;height:640px;filter:drop-shadow(0 18px 26px rgba(0,0,0,.35))}
</style></head><body>
<div class="copy">
  <div class="brand"><span class="mark"><svg viewBox="0 0 192 192"><g fill="none" stroke="currentColor" stroke-width="9" stroke-linecap="round" stroke-linejoin="round"><path d="M64.5 160A68.5 68.5 0 1 1 128.5 160"/><path d="M64.5 160V105H48L96.5 64L145 105H128.5V160"/></g></svg></span>Cx2 Homebuyers</div>
  <h1><span>A Fair Cash Offer</span><span>For Your Houston Home</span></h1>
  <p>Local and owner-run. No repairs, no commissions, no closing costs, and no obligation.</p>
</div>
<div class="phone">Call or text (346) 517-2534</div>
<img class="cooper" src="owner.webp" alt="">
</body></html>`;
(async () => {
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await page.goto("http://localhost:8765/robots.txt");
  await page.setContent(html, { waitUntil: "networkidle" });
  await page.evaluate(() => document.fonts.ready);
  await page.screenshot({ path: "site/og.jpg", type: "jpeg", quality: 86 });
  await browser.close();
  console.log("wrote site/og.jpg");
})();
