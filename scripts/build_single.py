# 한 파일 판 빌더: site/ 의 모든 레슨을 hash 라우터가 있는 HTML 하나로 묶는다. 레슨은 inert 텍스트로 두고 열린 레슨만 DOM 으로 만든다
import base64, io, json, os, re, sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SITE = Path(os.environ["SITE_OUT"]).resolve() if os.environ.get("SITE_OUT") else ROOT / "site"
OUT_DIR = SITE.parent / (SITE.name + "-single") if os.environ.get("SITE_OUT") else ROOT / "site-single"  # SITE_OUT 로 따로 빌드하면 site-single 을 건드리지 않는다
OUT = OUT_DIR / "robotics-from-scratch.html"
GSAP_CDN = "https://cdnjs.cloudflare.com/ajax/libs/gsap/3.15.0/gsap.min.js"
cache: dict[str, int] = {}
IMGS: list[str] = []


def webp(path: Path) -> int:
    key = str(path)
    if key not in cache:
        im = Image.open(path).convert("RGB")
        if im.width > 780:  # 390 CSS px at 2x, and the lesson column is at most 780 px wide: no visible difference, 28% fewer bytes to decode
            im = im.resize((780, round(im.height * 780 / im.width)), Image.LANCZOS)
        b = io.BytesIO()
        im.save(b, "WEBP", quality=72, method=6)
        IMGS.append("data:image/webp;base64," + base64.b64encode(b.getvalue()).decode())
        cache[key] = len(IMGS) - 1
    return cache[key]


def fix(h: str) -> str:
    h = re.sub(r'src="(assets/[^"]+\.png)"', lambda m: f'data-i="{webp(SITE / m.group(1))}"', h)
    h = re.sub(r'href="(\d\d-\d\d-[^"]+)\.html"', r'href="#\1"', h)
    return h.replace('href="index.html"', 'href="#"')


def part(h: str, tag: str) -> str:
    return re.search(rf"<{tag}[^>]*>(.*?)</{tag}>", h, re.S).group(1)


def lesson_fragments(body: str) -> tuple[str, str, str]:
    """The complete opening callout stays in the immediate fragment, before data-rest."""
    match = re.search(r'^(.*?)<span hidden data-rest="a"></span>(.*)<span hidden data-rest="b"></span>(.*)$', body, re.S)
    if match is None:
        raise ValueError("lesson is missing deferred-body markers; rebuild the multi-page site first")
    return match.groups()


# The whole file is ASCII: a single non-ASCII byte sends Chrome's decoder down its slow path for the entire 8 MB (260 ms vs 80 ms at 4x CPU).
def _esc(m, fmt):
    c = ord(m.group())
    if c > 0xFFFF:
        c -= 0x10000
        return fmt(0xD800 + (c >> 10)) + fmt(0xDC00 + (c & 0x3FF))
    return fmt(c)


def html_ascii(s: str) -> str:  # text and attribute values in HTML: numeric character references
    return re.sub(r"[^\x00-\x7f]", lambda m: f"&#{ord(m.group())};", s)


def js_ascii(s: str) -> str:  # JS source and JSON: \uXXXX is valid in strings, regex literals and comments
    return re.sub(r"[^\x00-\x7f]", lambda m: _esc(m, lambda c: "\\u%04X" % c), s)


def css_ascii(s: str) -> str:  # CSS strings and comments: \XXXXXX followed by a space ends the escape
    return re.sub(r"[^\x00-\x7f]", lambda m: "\\%X " % ord(m.group()), s)


def head_ascii(h: str) -> str:
    return re.sub(r"(<style>)(.*?)(</style>)", lambda m: m.group(1) + css_ascii(m.group(2)) + m.group(3), html_ascii_outside_style(h), flags=re.S)


def html_ascii_outside_style(h: str) -> str:
    parts = re.split(r"(<style>.*?</style>)", h, flags=re.S)
    return "".join(x if x.startswith("<style>") else html_ascii(x) for x in parts)


def inert(kind: str, sid: str, body: str) -> str:
    """text the HTML parser keeps as one raw text node: no DOM nodes until the router reads it"""
    assert "</script" not in body.lower() and "<!--" not in body, sid
    return f'<script type="{kind}" id="{sid}">{body}</script>'


# The Artifact variant keeps toys.js and motion.js as ordinary inline scripts (no script injection at run time, which a viewer's CSP could refuse);
# the shim captures their DOMContentLoaded listeners so the router can call them again after each inflate. The local file below is lazy.
SHIM_ON = "(function(){const L=[],add=window.addEventListener;window.__addEL=add;window.addEventListener=function(t,f,o){if(t==='DOMContentLoaded')L.push(f);else add.call(this,t,f,o)};window.__boot=()=>L.forEach(f=>f())})();"
SHIM_OFF = "delete window.addEventListener;delete window.__addEL;"

# toys.js and motion.js (and GSAP in the local build) stay as inert text and run when first needed: the home page never pays for them.
# Their cores register DOMContentLoaded listeners that scan the whole document. loadToys() captures those listeners and the router
# calls them after each inflate; only the lesson on screen is in the DOM, so they build exactly that lesson.
ROUTER = r"""
window.SINGLE=true;
const HOME=document.getElementById('L-home'),MAIN=HOME.parentNode,QCACHE={};
const txt=id=>{const e=document.getElementById(id);return e?e.textContent:null};
const inject=id=>{const s=document.createElement('script');s.textContent=txt(id);document.head.appendChild(s);s.remove()};
const quizOf=pid=>QCACHE[pid]||(QCACHE[pid]=JSON.parse(txt('Q-'+pid)||'{}'));
Object.defineProperty(window,'QUIZS',{configurable:true,get(){const o={};document.querySelectorAll('script[id^="Q-"]').forEach(s=>{o[s.id.slice(2)]=quizOf(s.id.slice(2))});Object.defineProperty(window,'QUIZS',{value:o,configurable:true});return o}});
function loadToys(){if(window.__boot)return;const L=[],add=window.addEventListener;
window.addEventListener=function(t,f,o){if(t==='DOMContentLoaded')L.push(f);else add.call(this,t,f,o)};
try{inject('toys-src')}finally{delete window.addEventListener}window.__boot=()=>L.forEach(f=>f())}
function loadGsap(){if(window.gsap||!document.getElementById('gsap-src'))return;inject('gsap-src');setTimeout(RFSUI.boot,0)}
const pic=root=>root.querySelectorAll('img[data-i]').forEach(i=>{i.decoding='async';i.loading='lazy';i.src=txt('I'+i.dataset.i);i.removeAttribute('data-i')});
function inflate(pid){const s=document.createElement('section');s.className='lesson';s.id='L-'+pid;s.innerHTML=txt('T-'+pid);pic(s);return s}
/* second stage: the long articles, appended in chunks of 12 elements, one per task; done(), when all are in, restores the scroll position */
function fill(sec,pid,done){const slot=sec.querySelector('[data-slot]'),html=txt('R-'+pid);if(!slot||!html){if(slot)slot.remove();return done()}
const tpl=document.createElement('template');tpl.innerHTML=html;const jobs=[];
[...tpl.content.children].forEach(a=>{const shell=a.cloneNode(false);slot.before(shell);const k=[...a.childNodes],hid=getComputedStyle(shell).display==='none';for(let i=0;i<k.length;i+=hid?k.length:12)jobs.push([shell,k.slice(i,i+(hid?k.length:12))])});slot.remove();
/* one chunk per frame: each frame paints what the last chunk added */
(function step(){if(!sec.isConnected)return;const j=jobs.shift();if(!j)return done();j[0].append(...j[1]);j[1].forEach(n=>n.querySelectorAll&&pic(n));if(jobs.length)requestAnimationFrame(()=>setTimeout(step,0));else done()})()}
function dispose(sec){sec.querySelectorAll('#quizbox').forEach(b=>{if(b._game)b._game.dispose()});disposeBolts(sec);const g=window.gsap;if(g)g.killTweensOf(sec.querySelectorAll('.q,.qres,.star,.bolt-svg'));if(window.MOTION)MOTION.__dispose(sec);if(window.TOYS)TOYS.__dispose(sec);RFSUI.revealClear();RFSUI.flowOff();sec.remove()}
function route(){const raw=(location.hash||'#').slice(1),pid=document.getElementById('T-'+raw)?raw:'';
const old=MAIN.querySelector('.lesson:not(#L-home)');
if(old&&old.id!=='L-'+pid){if(window.CUR)RFSUI.UI.scroll(window.CUR,scrollY);dispose(old)}
let el=pid?document.getElementById('L-'+pid):HOME;
if(pid&&!el){el=inflate(pid);MAIN.appendChild(el)}
HOME.hidden=!!pid;MAIN.classList.toggle('hm',!pid);MAIN.parentNode.classList.toggle('lpg',!!pid);window.CUR=pid||null;window.QUIZ=pid?quizOf(pid):null;
document.querySelectorAll('aside a').forEach(a=>a.classList.toggle('cur',a.getAttribute('href')==='#'+window.CUR));
if(pid){loadToys();window.__boot()}
quiz();bindMissions();RFS.paint();mountBolts(el);document.documentElement.classList.remove('nav');
const rs=RFSUI.wantRestore(pid),y=pid&&RFSUI.UI.d.sc[pid];window.scrollTo(0,0);
if(pid)RFSUI.UI.last(pid);
if(pid&&el.querySelector('[data-slot]'))requestAnimationFrame(()=>setTimeout(()=>fill(el,pid,()=>{if(rs&&y>40)scrollTo(0,y);RFSUI.flow();RFSUI.reveal()}),0));else{RFSUI.flow();RFSUI.reveal()}}
addEventListener('hashchange',route);route();
addEventListener('load',()=>setTimeout(()=>{loadGsap();setTimeout(loadToys,60)},0));
"""


def main() -> int:
    idx = (SITE / "index.html").read_text()
    head = head_ascii(re.search(r"<title>.*?</title>", idx, re.S).group(0) + "<style>" + (SITE / "app.css").read_text() + "</style>")  # the multi-page site links app.css and app.js; the single file inlines them
    sprite = re.search(r'<svg id="sprite".*?</svg>', idx, re.S).group(0)
    header = html_ascii(fix(re.search(r"<header>.*?</header>", idx, re.S).group(0)))
    aside = html_ascii(fix(part(idx, "aside")))
    home = html_ascii(fix(part(idx, "main")))
    scripts = re.findall(r"<script>(.*?)</script>", idx, re.S)
    ph_script, js = js_ascii(scripts[0]), js_ascii((SITE / "app.js").read_text())
    ph_script += js_ascii("window.GL=" + json.dumps({t["id"]: {"en": t["en"], "ko": t["ko"]} for t in json.loads((ROOT / "scripts" / "glossary.json").read_text())}, ensure_ascii=False, separators=(",", ":")) + ";")  # tooltips: the single file ships every definition once
    cat = lambda d, pat: "".join("\n" + f.read_text() for f in sorted((ROOT / "scripts" / d).glob(pat)))
    # every widget file, base groups first, then the per-phase files: the multi-page site loads a subset per lesson, the single file keeps them all as inert text
    toys = js_ascii(cat("toys", "[0-9]*.js") + cat("toys", "p[0-9][0-9].js") + cat("motion", "[0-9]*.js") + cat("motion", "p[0-9][0-9].js") + cat("motion3d", "[0-9]*.js") + cat("motion3d", "p[0-9][0-9].js"))
    gsap = (ROOT / "scripts" / "vendor" / "gsap.min.js").read_text()
    mascot = js_ascii((ROOT / "scripts" / "mascot3d.js").read_text())
    assert "</script" not in gsap.lower() and "</script" not in toys.lower() and "</script" not in js.lower()
    lessons, quizzes, imgs = [], [], []
    for f in sorted(SITE.glob("[0-9][0-9]-[0-9][0-9]-*.html")):
        h = f.read_text()
        pid = f.stem
        m = re.search(r"window\.QUIZ=(.*?);</script>", h, re.S)
        quizzes.append(inert("application/json", f"Q-{pid}", js_ascii(m.group(1) if m else "{}")))
        body = re.sub(r"<script>window\.QUIZ=.*?</script>", "", part(h, "main"), flags=re.S)
        # the long articles after the playground ("rests") are a second inert block: the router paints the rest of the lesson first and
        # appends them in small chunks, so opening a lesson is never one big layout
        head_, rests_, tail_ = lesson_fragments(fix(body))
        lessons.append(inert("text/plain", f"T-{pid}", html_ascii(head_ + '<span hidden data-slot></span>' + tail_)))
        lessons.append(inert("text/plain", f"R-{pid}", html_ascii(rests_)))
    imgs = [inert("text/plain", f"I{i}", d) for i, d in enumerate(IMGS)]
    data = "".join(lessons) + "".join(quizzes) + "".join(imgs)
    store = inert("text/plain", "toys-src", toys) + data
    main_html = f'<section class="lesson" id="L-home">{home}</section>'
    # page first, data after: the home page paints before the parser reaches the 8 MB of lessons and images; the router runs last
    body_html = lambda extra, store: (f'{sprite}{header}<div class="layout"><aside>{aside}</aside><main class="hm">{main_html}</main></div><div id="toast" role="status" aria-live="polite"></div>'
                                      f'<script>{ph_script}</script><script>{js}</script><script data-bolt3d-source>{mascot}</script>{extra}{store}<script>{ROUTER}</script>')
    doc = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">{head}</head><body>'
           f'{body_html(inert("text/plain", "gsap-src", gsap), store)}</body></html>')
    OUT.parent.mkdir(exist_ok=True)
    # Artifact variant: GSAP from cdnjs (the page runs without it when the CDN fails)
    art = head.replace("</style>", "header{top:env(safe-area-inset-top,0px)}</style>") + f'<script src="{GSAP_CDN}" defer></script>' + body_html(f"<script>{SHIM_ON}</script><script>{toys}</script><script>{SHIM_OFF}</script>", data)
    (OUT.parent / "artifact.html").write_text(art)
    doc.encode("ascii"), art.encode("ascii")  # raises if a non-ASCII character slipped through
    OUT.write_text(doc)
    print(f"{len(lessons) // 2} lessons -> {OUT} ({len(doc) / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
