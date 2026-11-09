// motion test harness: no site rebuild needed. Serves scripts/motion/*.js as motion.js into the already-built lesson page.
// usage: flock /tmp/robotics-render.lock node scripts/motion/shot.cjs <pid-prefix> <outdir> [--lang ko] [--dark] [--w 390] [--reduced] [--times 0.3,1.5,3,6] [--fps]
const puppeteer = require(require("child_process").execSync("npm root -g").toString().trim() + "/puppeteer");
const fs = require("fs"), path = require("path");
const ROOT = path.resolve(__dirname, "../.."), SITE = (process.env.SITE_OUT || ROOT + "/site") + "/";  // SITE_OUT: a site built somewhere else
const a = process.argv.slice(2), pidArg = a[0], out = a[1];
const opt = (k, d) => { const i = a.indexOf(k); return i < 0 ? d : (a[i + 1] && !a[i + 1].startsWith("--") ? a[i + 1] : true); };
const lang = opt("--lang", "en"), dark = !!opt("--dark", false), W = +opt("--w", 390), reduced = !!opt("--reduced", false), fps = !!opt("--fps", false);
const times = String(opt("--times", "0.3,1.5,3,6")).split(",").map(Number);
const file = fs.readdirSync(SITE).filter(f => f.startsWith(pidArg) && f.endsWith(".html"))[0];
if (!file) { console.log("no page for", pidArg); process.exit(2); }
const motionJs = () => fs.readdirSync(__dirname).filter(f => f.endsWith(".js")).sort().map(f => fs.readFileSync(path.join(__dirname, f), "utf8")).join("\n");
(async () => {
  fs.mkdirSync(out, { recursive: true });
  const b = await puppeteer.launch({ headless: true });
  const p = await b.newPage(); const errs = [];
  p.on("pageerror", e => errs.push("pageerror " + String(e).slice(0, 160)));
  p.on("console", m => { if (m.type() === "error") errs.push("console " + m.text().slice(0, 160)); });
  await p.setRequestInterception(true);
  p.on("request", r => r.url().endsWith("/motion.js") ? r.respond({ status: 200, contentType: "application/javascript", body: motionJs() }) : r.continue());
  await p.setViewport({ width: W, height: 900, deviceScaleFactor: 2 });
  await p.emulateMediaFeatures([{ name: "prefers-color-scheme", value: dark ? "dark" : "light" }, { name: "prefers-reduced-motion", value: reduced ? "reduce" : "no-preference" }]);
  await p.evaluateOnNewDocument(l => { try { localStorage.setItem("lang", l); } catch (e) {} }, lang);
  await p.goto("file://" + SITE + file, { waitUntil: "load" });
  const els = await p.$$(".motion[data-motion]");
  console.log(file, "motion slots:", els.length);
  for (const el of els) {
    const name = await el.evaluate(e => e.dataset.motion);
    await el.evaluate(e => e.scrollIntoView({ block: "center" }));   // widgets are built lazily, when they come within 300px of the screen
    await p.waitForFunction(e => e.classList.contains("motion-on"), { timeout: 3000 }, el).catch(() => {});
    if (!(await el.evaluate(e => e.classList.contains("motion-on")))) { console.log(" slot", name, "NOT BUILT (no registered motion, or it threw)"); continue; }
    const t0 = Date.now();
    for (const t of reduced ? [0] : times) {
      const wait = t * 1000 - (Date.now() - t0); if (wait > 0) await new Promise(r => setTimeout(r, wait));
      await el.screenshot({ path: out + "/" + name + "-" + lang + "-" + (dark ? "dark" : "light") + "-" + W + (reduced ? "-reduced" : "") + "-t" + t + ".png" });
    }
    if (fps && !reduced) {
      const c = await p.createCDPSession(); await c.send("Emulation.setCPUThrottlingRate", { rate: 4 });
      const r = await p.evaluate(() => new Promise(res => { let n = 0, mx = 0, last = performance.now(), s = last; (function f(now) { n++; mx = Math.max(mx, now - last); last = now; if (now - s < 3000) requestAnimationFrame(f); else res({ fps: +(n / ((now - s) / 1000)).toFixed(1), maxFrameMs: +mx.toFixed(1) }); })(performance.now()); }));
      await c.send("Emulation.setCPUThrottlingRate", { rate: 1 });
      console.log(" fps@4x", name, JSON.stringify(r));
    }
  }
  const over = await p.evaluate(() => document.documentElement.scrollWidth > innerWidth);
  console.log("overflow:", over, "errors:", errs.length, errs.slice(0, 4).join(" | "));
  await b.close();
})();
