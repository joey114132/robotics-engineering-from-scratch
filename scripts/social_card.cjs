// Renders docs/img/social-card.png (1280x640, GitHub social preview) and docs/img/banner-online.png (README banner that links to the website): hero-bolt.jpg with the text set as real text. Usage: node scripts/social_card.cjs
const puppeteer = require(require("child_process").execSync("npm root -g").toString().trim() + "/puppeteer");
const path = require("path"), fs = require("fs");
const img = "data:image/jpeg;base64," + fs.readFileSync(path.join(__dirname, "..", "docs", "img", "hero-bolt.jpg")).toString("base64");
const html = `<body style="margin:0;width:1280px;height:640px;position:relative;overflow:hidden;font-family:'Noto Sans',sans-serif;background:#f4f7f9">
<img src="${img}" style="position:absolute;left:95px;top:-22px;height:680px">
<div style="position:absolute;inset:0;background:linear-gradient(90deg,#f4f7f9 0,#f4f7f9 40%,rgba(244,247,249,0) 62%)"></div>
<div style="position:absolute;left:64px;top:118px;width:620px;color:#0e1a1f">
<span style="display:inline-block;background:#41c8e6;border-radius:99px;padding:7px 18px;font:700 23px 'Noto Sans';letter-spacing:.06em">87 LESSONS · FREE · EN / KO</span>
<div style="font:800 86px/1.04 'Noto Sans';margin-top:26px;letter-spacing:-.02em">Robotics<br>from Scratch</div>
<div style="font:400 31px/1.35 'Noto Sans';margin-top:26px;color:#3a4a52">Never studied robotics? Start here.<br>Small Python programs you can<br>watch move in 3D.</div></div></body>`;
const SITE = "robotics-from-scratch.robotics-site.workers.dev";
const banner = `<body style="margin:0;width:1280px;height:320px;position:relative;overflow:hidden;font-family:'Noto Sans',sans-serif;background:#f4f7f9">
<img src="${img}" style="position:absolute;left:470px;top:-150px;height:560px">
<div style="position:absolute;inset:0;background:linear-gradient(90deg,#f4f7f9 0,#f4f7f9 50%,rgba(244,247,249,0) 70%)"></div>
<div style="position:absolute;left:56px;top:30px;width:820px;color:#0e1a1f;white-space:nowrap">
<span style="display:inline-block;background:#41c8e6;border-radius:99px;padding:6px 16px;font:700 19px 'Noto Sans';letter-spacing:.06em">FREE · NOTHING TO INSTALL · EN / KO</span>
<div style="font:800 62px/1.05 'Noto Sans';margin-top:16px;letter-spacing:-.02em">Read the course online</div>
<div style="font:400 25px/1.35 'Noto Sans';margin-top:12px;color:#3a4a52">87 short lessons with 3D scenes, clips and quizzes.</div>
<div style="display:flex;align-items:center;gap:18px;margin-top:22px">
<span style="display:inline-block;background:#0e1a1f;color:#fff;border-radius:14px;padding:12px 24px;font:700 25px 'Noto Sans';box-shadow:0 5px 0 #41c8e6">Start lesson 1 &rarr;</span>
<span style="font:600 21px 'Noto Sans';color:#0b6f86">${SITE}</span></div></div></body>`;
(async () => {
  const b = await puppeteer.launch({ headless: true });
  for (const [page, w, h, scale, file] of [[html, 1280, 640, 1, "social-card.png"], [banner, 1280, 320, 1.5, "banner-online.png"]]) {
    const p = await b.newPage();
    await p.setViewport({ width: w, height: h, deviceScaleFactor: scale });
    await p.setContent(page, { waitUntil: "load" });
    await p.screenshot({ path: path.join(__dirname, "..", "docs", "img", file) });
    await p.close();
  }
  await b.close();
})();
