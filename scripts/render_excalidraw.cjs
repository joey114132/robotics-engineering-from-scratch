// .excalidraw 파일을 실제 Excalidraw 렌더러(@excalidraw/excalidraw 0.18.0)로 SVG 와 PNG 로 내보낸다
const fs = require("fs");
const path = require("path");
const puppeteer = require(require("child_process").execSync("npm root -g").toString().trim() + "/puppeteer");

async function main() {
  const files = process.argv.slice(2);
  if (!files.length) { console.error("usage: render_excalidraw.cjs a.excalidraw [b.excalidraw ...]"); process.exit(2); }
  const browser = await puppeteer.launch({ headless: true, args: [] });
  const page = await browser.newPage();
  page.on("pageerror", (e) => console.error("pageerror:", String(e).slice(0, 400)));
  page.on("requestfailed", (r) => console.error("requestfailed:", r.url().slice(0, 140), r.failure() && r.failure().errorText));
  await page.goto("about:blank");
  await page.setContent("<html><body></body></html>");
  await page.addScriptTag({ type: "module", content: `
    import { exportToSvg } from "https://esm.sh/@excalidraw/excalidraw@0.18.0?deps=react@18.3.1,react-dom@18.3.1";
    window.__export = async (scene) => {
      const svg = await exportToSvg({ elements: scene.elements, appState: { ...scene.appState, exportBackground: true, viewBackgroundColor: "#ffffff" }, files: scene.files || {}, exportPadding: 24 });
      return svg.outerHTML;
    };
    window.__ready = true;` });
  await page.waitForFunction("window.__ready === true", { timeout: 90000 });
  for (const f of files) {
    const scene = JSON.parse(fs.readFileSync(f, "utf8"));
    const svg = await page.evaluate((s) => window.__export(s), scene);
    const base = f.replace(/\.excalidraw$/, "");
    fs.writeFileSync(base + ".svg", svg);
    const p2 = await browser.newPage();
    await p2.setContent(`<html><body style="margin:0;background:#fff">${svg}</body></html>`);
    await p2.evaluate(() => document.fonts.ready);
    const el = await p2.$("svg");
    await el.screenshot({ path: base + ".png" });
    await p2.close();
    console.log("rendered", path.basename(base));
  }
  await browser.close();
}
main().catch((e) => { console.error(e); process.exit(1); });
