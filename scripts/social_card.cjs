// Renders docs/img/social-card.png (1280x640, GitHub social preview): hero-bolt.jpg with the title set as real text. Usage: node scripts/social_card.cjs
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
(async () => {
  const b = await puppeteer.launch({ headless: true });
  const p = await b.newPage();
  await p.setViewport({ width: 1280, height: 640 });
  await p.setContent(html, { waitUntil: "load" });
  await p.screenshot({ path: path.join(__dirname, "..", "docs", "img", "social-card.png") });
  await b.close();
})();
