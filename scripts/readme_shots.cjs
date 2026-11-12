// README 그림 만들기: 사이트 화면, 터미널 화면, 모션 GIF 프레임을 headless 로 찍는다
// usage: flock /tmp/robotics-render.lock node scripts/readme_shots.cjs <site|cli|gif|gif3d|gallery3d> [lesson-prefix|scene,scene,...] [outname]
// gif3d: SCENE=<name> animates one 3D scene; gallery3d: arg1 = comma list of scene names, one picture with a caption per scene
const puppeteer = require(require("child_process").execSync("npm root -g").toString().trim() + "/puppeteer");
const fs = require("fs"), path = require("path"), cp = require("child_process");
const ROOT = path.resolve(__dirname, ".."), SITE = ROOT + "/site/", OUT = ROOT + "/docs/img/";
const [mode, arg1, arg2] = process.argv.slice(2);
fs.mkdirSync(OUT, { recursive: true });
const sleep = ms => new Promise(r => setTimeout(r, ms));
const page = async (b, w, h, dpr, dark) => {
  const p = await b.newPage();
  await p.setViewport({ width: w, height: h, deviceScaleFactor: dpr });
  await p.emulateMediaFeatures([{ name: "prefers-color-scheme", value: dark ? "dark" : "light" }]);
  return p;
};
// ANSI (SGR) -> HTML: bold, dim, 24-bit colour, reset
function ansi(s) {
  let out = "", open = 0;
  s.replace(/\x1b\[(\d+(?:;\d+)*)?m|([^\x1b]+)/g, (m, c, t) => {
    if (t) { out += t.replace(/&/g, "&amp;").replace(/</g, "&lt;"); return; }
    const n = (c || "0").split(";").map(Number); let st = "";
    if (n[0] === 0) { while (open) { out += "</span>"; open--; } return; }
    for (let i = 0; i < n.length; i++) {
      if (n[i] === 1) st += "font-weight:700;"; else if (n[i] === 2) st += "opacity:.6;";
      else if (n[i] === 38 && n[i + 1] === 2) { st += `color:rgb(${n[i + 2]},${n[i + 3]},${n[i + 4]});`; i += 4; }
    }
    if (st) { out += `<span style="${st}">`; open++; }
  });
  while (open--) out += "</span>";
  return out;
}
(async () => {
  const b = await puppeteer.launch({ headless: true });
  if (mode === "site") {           // phone screenshots of the built site
    const file = (arg1 ? fs.readdirSync(SITE).find(f => f.startsWith(arg1) && f.endsWith(".html")) : "index.html");
    const p = await page(b, 390, 844, 2, false);
    await p.goto("file://" + SITE + file, { waitUntil: "load" }); await sleep(1500);
    if (arg2 && arg2.startsWith("scroll=")) await p.evaluate(y => window.scrollTo(0, y), +arg2.slice(7));
    await sleep(1800);
    await p.screenshot({ path: OUT + (arg2 && !arg2.startsWith("scroll=") ? arg2 : (file.replace(".html", "") + "-phone")) + ".png" });
  } else if (mode === "cli") {      // terminal screenshot of `robo`
    const args = (arg1 || "map").split(" ");
    const r = cp.spawnSync("python3", [ROOT + "/scripts/robo.py", ...args], { env: { ...process.env, FORCE_COLOR: "1", ROBO_NO_ANIM: "1", COLUMNS: "92", NO_COLOR: "" }, encoding: "utf8" });
    const lines = r.stdout.replace(/\n+$/, "").split("\n").slice(0, +(process.env.LINES_MAX || 26)).join("\n");
    const p = await page(b, 800, 600, 2, true);
    await p.setContent(`<body style="margin:0;background:#fff"><div id=t style="display:inline-block;margin:0;padding:18px 22px 20px;background:#0f1620;color:#d6dde6;font:15px/1.35 'DejaVu Sans Mono',monospace;white-space:pre;border-radius:10px"><div style="margin-bottom:12px"><span style="color:#ff5f56">●</span> <span style="color:#ffbd2e">●</span> <span style="color:#27c93f">●</span> <span style="opacity:.5;margin-left:10px">$ robo ${args.join(" ")}</span></div>${ansi(lines)}</div></body>`);
    await (await p.$("#t")).screenshot({ path: OUT + (arg2 || "cli-map") + ".png" });
  } else if (mode === "gif") {      // frames of one motion widget -> docs/img/<name>.gif through ffmpeg
    const file = fs.readdirSync(SITE).find(f => f.startsWith(arg1) && f.endsWith(".html"));
    const p = await page(b, 720, 900, 1, false);
    await p.goto("file://" + SITE + file, { waitUntil: "load" }); await sleep(800);
    const idx = +(process.env.WIDGET || 0);
    const el = (await p.$$(".motion[data-motion]"))[idx];
    await el.evaluate(e => e.scrollIntoView({ block: "center" })); await sleep(2500);
    const dir = OUT + ".frames/"; fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const svg = await el.$("svg"); const N = +(process.env.FRAMES || 60), step = +(process.env.STEP || 90);
    for (let i = 0; i < N; i++) { await svg.screenshot({ path: dir + String(i).padStart(3, "0") + ".png" }); await sleep(step); }
    const fps = (1000 / (step + 60)).toFixed(2);
    cp.execSync(`ffmpeg -y -loglevel error -framerate ${fps} -i ${dir}%03d.png -vf "scale=560:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" ${OUT}${arg2 || "motion"}.gif`);
    fs.rmSync(dir, { recursive: true, force: true });
  } else if (mode === "gif3d") {    // frames of one 3D scene while it plays on its own -> docs/img/<name>.gif
    const name = process.env.SCENE, lesson = JSON.parse(fs.readFileSync(ROOT + "/phases/" + arg1 + "/fun.json")).three;
    if (lesson !== name) throw new Error("lesson " + arg1 + " has scene " + lesson + ", not " + name);
    const file = fs.readdirSync(SITE).find(f => f.startsWith(arg1.split("/")[0].slice(0, 2) + "-" + arg1.split("/")[1].slice(0, 2)) && f.endsWith(".html"));
    const p = await page(b, 720, 900, 1, false);
    await p.goto("file://" + SITE + file, { waitUntil: "load" }); await sleep(800);
    const slot = `.motion.three[data-motion="${name}"]`;
    await p.$eval(slot, e => e.scrollIntoView({ block: "center" })); await sleep(1500);
    const el = await p.$(slot + " canvas");
    const dir = OUT + ".frames/"; fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true });
    const N = +(process.env.FRAMES || 48), step = +(process.env.STEP || 140);
    for (let i = 0; i < N; i++) { await el.screenshot({ path: dir + String(i).padStart(3, "0") + ".png" }); await sleep(step); }
    const fps = (1000 / (step + 70)).toFixed(2);
    cp.execSync(`ffmpeg -y -loglevel error -framerate ${fps} -i ${dir}%03d.png -vf "scale=520:-1:flags=lanczos,split[a][b];[a]palettegen=max_colors=96[p];[b][p]paletteuse=dither=bayer:bayer_scale=4" ${OUT}${arg2 || name}.gif`);
    fs.rmSync(dir, { recursive: true, force: true });
  } else if (mode === "gallery3d") { // one still per scene (rest frame, English) laid out as a grid with captions
    const items = arg1.split(",").map(x => x.split(":"));   // scene:lesson-dir
    const shots = [];
    for (const [name, lesson] of items) {
      const [ph, ls] = lesson.split("/"); const file = fs.readdirSync(SITE).find(f => f.startsWith(ph.slice(0, 2) + "-" + ls.slice(0, 2)) && f.endsWith(".html"));
      const p = await page(b, 390, 844, 2, false);
      await p.emulateMediaFeatures([{ name: "prefers-reduced-motion", value: "reduce" }]);
      await p.evaluateOnNewDocument(() => { try { localStorage.setItem("lang", "en"); } catch (e) {} });
      await p.goto("file://" + SITE + file, { waitUntil: "load" });
      const slot = `.motion.three[data-motion="${name}"]`;
      await p.$eval(slot, e => e.scrollIntoView({ block: "center" })); await p.waitForSelector(slot + " canvas"); await sleep(700);
      shots.push([name, lesson, (await (await p.$(slot + " canvas")).screenshot()).toString("base64")]); await p.close();
    }
    const cells = shots.map(([n, l, d]) => `<figure><img src="data:image/png;base64,${d}"><figcaption>${l.split("/")[1].replace(/^\d+-/, "").replace(/-/g, " ")}</figcaption></figure>`).join("");
    const g = await page(b, 1200, 400, 2, false);
    await g.setContent(`<body style="margin:0;background:#fff;font:15px system-ui,sans-serif"><div id=g style="display:grid;grid-template-columns:repeat(3,1fr);gap:14px;padding:14px;width:1172px;background:#fff">${cells}</div><style>figure{margin:0;border:1px solid #d9e1e4;border-radius:10px;overflow:hidden;background:#fff}img{width:100%;display:block}figcaption{padding:6px 10px 8px;color:#41525a;text-transform:capitalize;border-top:1px solid #eef2f3}</style></body>`);
    await (await g.$("#g")).screenshot({ path: OUT + (arg2 || "3d-gallery") + ".png" });
  }
  await b.close();
})();
