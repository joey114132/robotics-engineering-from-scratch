// README 그림 만들기: `robo` 터미널 화면을 headless 로 찍는다 (웹사이트 화면은 사이트 저장소의 tools/readme_shots.cjs)
// usage: flock /tmp/robotics-render.lock node scripts/readme_shots.cjs cli [robo args] [outname]
const puppeteer = require(require("child_process").execSync("npm root -g").toString().trim() + "/puppeteer");
const fs = require("fs"), path = require("path"), cp = require("child_process");
const ROOT = path.resolve(__dirname, ".."), OUT = ROOT + "/docs/img/";
const [mode, arg1, arg2] = process.argv.slice(2);
fs.mkdirSync(OUT, { recursive: true });
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
  if (mode === "cli") {      // terminal screenshot of `robo`
    const args = (arg1 || "map").split(" ");
    const r = cp.spawnSync("python3", [ROOT + "/scripts/robo.py", ...args], { env: { ...process.env, FORCE_COLOR: "1", ROBO_NO_ANIM: "1", COLUMNS: "92", NO_COLOR: "" }, encoding: "utf8" });
    const lines = r.stdout.replace(/\n+$/, "").split("\n").slice(0, +(process.env.LINES_MAX || 26)).join("\n");
    const p = await page(b, 800, 600, 2, true);
    await p.setContent(`<body style="margin:0;background:#fff"><div id=t style="display:inline-block;margin:0;padding:18px 22px 20px;background:#0f1620;color:#d6dde6;font:15px/1.35 'DejaVu Sans Mono',monospace;white-space:pre;border-radius:10px"><div style="margin-bottom:12px"><span style="color:#ff5f56">●</span> <span style="color:#ffbd2e">●</span> <span style="color:#27c93f">●</span> <span style="opacity:.5;margin-left:10px">$ robo ${args.join(" ")}</span></div>${ansi(lines)}</div></body>`);
    await (await p.$("#t")).screenshot({ path: OUT + (arg2 || "cli-map") + ".png" });
  }
  await b.close();
})();
