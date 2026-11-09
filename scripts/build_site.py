# 레슨 마크다운을 영어/한국어 토글, 퀴즈 게임, 학습 경로, 다크 모드가 있는 정적 study guide 사이트로 만든다
import hashlib
import html
import json
import os
import re
import shutil
import sys
from pathlib import Path

try:
    from pygments import highlight
    from pygments.formatters import HtmlFormatter
    from pygments.lexers import TextLexer, get_lexer_by_name
except ImportError:  # highlighting is optional
    highlight = None

ROOT = Path(__file__).resolve().parents[1]
SITE = Path(os.environ["SITE_OUT"]).resolve() if os.environ.get("SITE_OUT") else ROOT / "site"  # SITE_OUT: build elsewhere without touching site/
PHASE_KO = {"setup-and-tooling": "설치와 도구", "math-foundations": "수학 기초", "manipulator-kinematics": "매니퓰레이터 기구학",
            "dynamics-and-control": "동역학과 제어", "actuators-and-sensors": "액추에이터와 센서", "robot-software": "로봇 소프트웨어",
            "perception-and-calibration": "인식과 캘리브레이션", "state-estimation": "상태 추정", "mobile-robots": "이동로봇",
            "motion-planning": "모션 플래닝", "legged-and-aerial": "다리와 비행", "contact-and-manipulation": "접촉과 조작",
            "simulation-and-sim-to-real": "시뮬레이션과 sim-to-real", "learning-for-robots": "로봇 학습",
            "multi-robot-and-swarms": "다중 로봇과 swarm", "safety-and-deployment": "안전과 배포", "capstones": "캡스톤"}
# 17 phases share six colour families (hue is set in CSS by data-f): 1 cyan, 2 blue, 3 green, 4 amber, 5 orange-red, 6 pink
FAM = {"00": 1, "01": 1, "02": 2, "03": 2, "04": 2, "05": 3, "06": 3, "07": 3, "08": 4, "09": 4, "10": 5, "11": 5,
       "12": 6, "13": 6, "14": 6, "15": 6, "16": 6}
OFFS = [0, 50, 72, 50, 0, -50, -72, -50]  # winding path: x offset in px of each node from the trail centre
ROW = 88
LESMAP: dict[str, Path] = {}
QUIZ_ALL: dict[str, dict] = {}

ACR = {"se3": "SE(3)", "pid": "PID", "ik": "IK", "fk": "FK", "slam": "SLAM", "urdf": "URDF", "ros2": "ROS 2", "rrt": "RRT", "imu": "IMU",
       "zmp": "ZMP", "mujoco": "MuJoCo", "numpy": "NumPy", "dh": "DH", "vs": "vs", "sim": "sim", "ros": "ROS", "pd": "PD", "kd": "kd", "kp": "kp"}

# ---- inline SVG: icons (sprite) and Bolt the mascot -------------------------------------------------------------
ICONS = {
    "bolt": '<path fill="currentColor" stroke="none" d="M13.2 2 4.5 13.6c-.3.4 0 1 .5 1h5.3l-1 6.6c-.1.6.6.9 1 .4l8.6-11.8c.3-.4 0-1-.5-1h-5.1l.9-6c.1-.6-.7-.9-1-.4z"/>',
    "flame": '<path fill="currentColor" stroke="none" d="M12.4 2.2c.3 3.1 3.6 4.7 4.6 8.2 1 3.4-.2 6.3-2.6 8a6 6 0 0 1-7.4-.5C5 16.2 5 13.6 6.3 11.700c.5 1.500 1.300 2.200 2.300 2.400-.4-3.500.8-7.900 3.800-11.900z"/>',
    "star": '<path fill="currentColor" d="m12 2.8 2.800 5.900 6.400.8-4.700 4.400 1.200 6.400L12 17.200 6.300 20.300l1.200-6.400L2.800 9.500l6.400-.8z"/>',
    "star-o": '<path d="m12 2.800 2.800 5.900 6.400.8-4.700 4.400 1.200 6.400L12 17.200 6.300 20.300l1.200-6.400L2.800 9.500l6.400-.8z"/>',
    "medal": '<circle cx="12" cy="9" r="6"/><path d="m8.500 14-2 8 5.500-3 5.500 3-2-8"/>',
    "check": '<path d="m5 12.500 4.500 4.500L19 7.500"/>',
    "x": '<path d="m7 7 10 10M17 7 7 17"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "back": '<path d="M19 12H5M11 6l-6 6 6 6"/>',
    "refresh": '<path d="M20 11a8 8 0 1 0-2.300 6.200M20 4v7h-7"/>',
    "copy": '<rect x="8" y="8" width="12" height="12" rx="3"/><path d="M16 8V6a2 2 0 0 0-2-2H6a2 2 0 0 0-2 2v8a2 2 0 0 0 2 2h2"/>',
    "paste": '<rect x="5" y="5" width="14" height="16" rx="3"/><path d="M9 5V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v1M9 12h6M9 16h4"/>',
    "cal": '<rect x="3" y="5" width="18" height="16" rx="3.500"/><path d="M3 10h18M8 3v4M16 3v4"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1" fill="currentColor"/>',
    "play": '<path fill="currentColor" d="M8 5.500v13a1 1 0 0 0 1.500.9l10.500-6.500a1 1 0 0 0 0-1.800L9.500 4.600A1 1 0 0 0 8 5.500z"/>',
}


def sprite() -> str:
    syms = "".join(f'<symbol id="i-{k}" viewBox="0 0 24 24">{v}</symbol>' for k, v in ICONS.items())
    return f'<svg id="sprite" width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false">{syms}</svg>'


def ic(name: str, cls: str = "") -> str:
    return f'<svg class="ic {cls}" aria-hidden="true"><use href="#i-{name}"/></svg>'


def bolt_svg(mood: str = "idle", cls: str = "") -> str:
    """Bolt: a friendly line-art robot. Eyes and antenna glow in the current phase colour; the mood decides which parts show."""
    return (
        f'<svg class="bolt-svg {cls}" data-mood="{mood}" viewBox="0 0 64 64" aria-hidden="true" focusable="false">'
        '<g class="m-arms"><path class="m-idle m-no m-sleepy" d="M19 51c-6 1-9 5-9 9M45 51c6 1 9 5 9 9"/>'
        '<path class="m-cheer" d="M19 50c-7-1-11-7-11-15M45 50c7-1 11-7 11-15"/></g>'
        '<rect class="bl-fill" x="19" y="46" width="26" height="15" rx="6"/><circle class="bl-glow" cx="32" cy="53.500" r="2.600"/>'
        '<path class="bl-line" d="M32 11V5"/><circle class="bl-glow bl-ant" cx="32" cy="4.500" r="3"/>'
        '<rect class="bl-fill" x="4.500" y="22" width="6" height="11" rx="3"/><rect class="bl-fill" x="53.500" y="22" width="6" height="11" rx="3"/>'
        '<rect class="bl-fill" x="10" y="11" width="44" height="34" rx="13"/><rect class="bl-visor" x="16" y="17" width="32" height="22" rx="9"/>'
        '<g class="m-idle"><circle class="bl-glow" cx="26" cy="27" r="3.300"/><circle class="bl-glow" cx="38" cy="27" r="3.300"/>'
        '<path class="bl-stroke" d="M28.500 33.500q3.500 2.800 7 0"/></g>'
        '<g class="m-cheer"><path class="bl-stroke" d="M21.500 29q4.500-8 9 0M33.500 29q4.500-8 9 0"/><path class="bl-glow" d="M27 32.500q5 7.500 10 0z"/></g>'
        '<g class="m-no"><circle class="bl-glow" cx="26" cy="27" r="4"/><circle class="bl-visor" cx="27" cy="28" r="1.600"/>'
        '<circle class="bl-glow" cx="38" cy="27" r="4"/><circle class="bl-visor" cx="39" cy="28" r="1.600"/>'
        '<path class="bl-stroke" d="M28.500 35.500q3.500-2.800 7 0"/><path class="bl-drop" d="M52 12c2 3 3 5 3 7a3 3 0 0 1-6 0c0-2 1-4 3-7z"/></g>'
        '<g class="m-sleepy"><path class="bl-stroke" d="M21 28h9M34 28h9M29 34h6"/>'
        '<path class="bl-stroke bl-z" d="M47 9h5l-5 6h5"/></g></svg>'
    )


# ---- markdown -> html -------------------------------------------------------------------------------------------
def tt(les) -> str:
    """Lesson title in both languages from the first heading of each doc."""
    out = []
    for code in ("en", "ko"):
        f = les / "docs" / f"{code}.md"
        m = re.search(r"^# (.+)$", f.read_text(), re.M) if f.exists() else None
        out.append(f'<span data-lang="{code}">{html.escape(m.group(1) if m else nice(les.name.split("-", 1)[1]))}</span>')
    return "".join(out)


# nice() would split every hyphen into a space; these two phase titles keep theirs
PHASE_EN = {"simulation-and-sim-to-real": "Simulation and sim-to-real", "multi-robot-and-swarms": "Multi-robot and swarms"}


def phase_title(slug: str) -> str:
    return PHASE_EN.get(slug) or nice(slug)


def nice(s: str) -> str:
    out = " ".join(ACR.get(w, w) for w in s.replace("-", " ").split())
    return out[:1].upper() + out[1:]


def link(text: str, url: str) -> str:
    url = html.unescape(url).strip()
    if "\x00" in url:
        return text
    if not re.match(r"(https?://|#|[\w./-]+$)", url):
        return text
    return f'<a href="{html.escape(url, quote=True)}">{text}</a>'


def inline(s: str) -> str:
    codes = []
    s = re.sub(r"`([^`]+)`", lambda m: codes.append(m.group(1)) or f"\x00{len(codes) - 1}\x00", s)
    s = html.escape(s, quote=False)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![*\w])\*(?!\s)(.+?)(?<!\s)\*(?!\w)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lambda m: link(m.group(1), m.group(2)), s)
    return re.sub(r"\x00(\d+)\x00", lambda m: f"<code>{html.escape(codes[int(m.group(1))], quote=False)}</code>", s)


def code_block(lang: str, body: str) -> str:
    if highlight:
        try:
            lexer = get_lexer_by_name(lang) if lang and lang != "text" else TextLexer()
        except Exception:
            lexer = TextLexer()
        inner = highlight(body, lexer, HtmlFormatter(nowrap=True))
    else:
        inner = html.escape(body)
    n = body.count("\n") + (0 if body.endswith("\n") else 1)  # 14px font x 1.6 line height = the content box, exact, so content-visibility keeps the page height
    return f'<pre class="hl" data-lang="{html.escape(lang)}" style="--ih:{round(n * 22.4)}px"><code>{inner}</code></pre>'


def img_size(src: str) -> str:
    """width/height attributes from the PNG header, so lazy images reserve their space (no layout shift, stable scroll restore)."""
    try:
        from PIL import Image
        with Image.open(SITE / html.unescape(src)) as im:
            return f' width="{im.width}" height="{im.height}"'
    except Exception:
        return ""


def md_to_html(text: str, img_base: str) -> tuple[str, str]:
    lines, out, title, i = text.splitlines(), [], "", 0
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            lang, body, i = ln[3:].strip(), [], i + 1
            while i < len(lines) and not lines[i].startswith("```"):
                body.append(lines[i])
                i += 1
            out.append(code_block(lang, "\n".join(body)))
        elif ln.startswith("# "):
            title = ln[2:].strip()
        elif ln.startswith("## "):
            out.append(f"<h2>{inline(ln[3:].strip())}</h2>")
        elif ln.startswith("> "):
            out.append(f'<p class="idea">{inline(ln[2:].strip())}</p>')
        elif re.match(r"\*\*[^*]+:\*\*", ln) and ln.count("**") >= 4:
            chips = [c for c in re.split(r"\s{3,}", ln.strip()) if c]
            out.append('<div class="chips">' + "".join(f"<span>{inline(c)}</span>" for c in chips) + "</div>")
        elif ln.startswith("!["):
            m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", ln)
            src = html.escape(img_base + Path(m.group(2)).name, quote=True)
            cap = ""
            if i + 2 < len(lines) and lines[i + 1] == "" and re.match(r"^\*[^*].*\*$", lines[i + 2]):
                cap, i = lines[i + 2][1:-1], i + 2
            out.append(f'<figure><img src="{src}" alt="{html.escape(m.group(1))}"{img_size(src)} loading="lazy" decoding="async"><figcaption>{inline(cap)}</figcaption></figure>')
        elif ln.startswith("|") and i + 1 < len(lines) and re.match(r"^\|[\s:|-]+\|$", lines[i + 1]):
            head = [c.strip() for c in ln.strip("|").split("|")]
            rows, i = [], i + 2
            while i < len(lines) and lines[i].startswith("|"):
                rows.append([c.strip() for c in lines[i].strip("|").split("|")])
                i += 1
            i -= 1
            out.append("<div class='tablewrap'><table><thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows) + "</tbody></table></div>")
        elif re.match(r"^(\d+\.|-) ", ln):
            tag = "ol" if ln[0].isdigit() else "ul"
            items = []
            while i < len(lines) and re.match(r"^(\d+\.|-) ", lines[i]):
                items.append(re.sub(r"^(\d+\.|-) ", "", lines[i]))
                i += 1
            i -= 1
            out.append(f"<{tag}>" + "".join(f"<li>{inline(x)}</li>" for x in items) + f"</{tag}>")
        elif ln.strip():
            para = [ln]
            while i + 1 < len(lines) and lines[i + 1].strip() and not re.match(r"^(#|>|```|!\[|\||\d+\. |- )", lines[i + 1]):
                i += 1
                para.append(lines[i])
            out.append(f"<p>{inline(' '.join(para))}</p>")
        i += 1
    return title, "\n".join(out)


def load_lessons():
    phases = {}
    for d in sorted(ROOT.glob("phases/*/*/docs")):
        les, ph = d.parent, d.parent.parent
        if not (d / "en.md").exists():
            continue
        num = ph.name.split("-")[0]
        slug = ph.name.split("-", 1)[1]
        phases.setdefault(ph.name, {"num": num, "slug": slug, "lessons": []})["lessons"].append(les)
    return phases


# ---- lesson page -------------------------------------------------------------------------------------------------
def pid_of(ph, les) -> str:
    return f"{ph['num']}-{les.name}"


def phase_chip(ph) -> str:
    ko = PHASE_KO.get(ph["slug"], ph["slug"])
    return (f'<span class="chip ph"><span data-lang="en">Phase {ph["num"]} · {html.escape(phase_title(ph["slug"]))}</span>'
            f'<span data-lang="ko">Phase {ph["num"]} · {html.escape(ko)}</span></span>')


def dots(pid: str) -> str:
    return (f'<span class="dots" data-pid="{pid}" role="img" aria-label="progress">'
            + '<i class="dq"></i>' * 6 + '<i class="dm"></i></span>')


def pager_card(pid, rel: str) -> str:
    if not pid:
        return "<span></span>"
    les = LESMAP[pid]
    arrow = ic("back") if rel == "prev" else ic("arrow")
    lab = ('<span data-lang="en">Previous</span><span data-lang="ko">이전</span>' if rel == "prev"
           else '<span data-lang="en">Next</span><span data-lang="ko">다음</span>')
    inner = f'<small>{arrow if rel == "prev" else ""}{lab}{arrow if rel == "next" else ""}</small><b>{tt(les)}</b>'
    return f'<a class="pn {rel}" data-f="{FAM[pid[:2]]}" href="{pid}.html">{inner}</a>'


def page(ph, les, phases, flat):
    pid = pid_of(ph, les)
    base = f"assets/{pid}/"
    (SITE / "assets" / pid).mkdir(parents=True, exist_ok=True)
    for png in (les / "assets").glob("*.png"):
        shutil.copy(png, SITE / "assets" / pid / png.name)
    langs, quiz = {}, {}
    for code in ("en", "ko"):
        f = les / "docs" / f"{code}.md"
        if f.exists():
            langs[code] = md_to_html(f.read_text(), base)
        q = les / ("quiz.json" if code == "en" else "quiz.ko.json")
        if q.exists():
            quiz[code] = json.loads(q.read_text())
    QUIZ_ALL[pid] = quiz
    fun = json.loads((les / "fun.json").read_text()) if (les / "fun.json").exists() else {}
    hook, mission, toy = fun_html(fun, pid)
    scene = f'<div class="motion scene" data-motion="scene-{ph["num"]}"></div>' if ph["lessons"].index(les) == 0 else ""
    concept = f'<div class="motion concept" data-motion="{html.escape(fun["motion"])}"></div>' if fun.get("motion") else ""
    idx = flat.index(pid)
    prev_, next_ = (flat[idx - 1] if idx else None), (flat[idx + 1] if idx + 1 < len(flat) else None)
    h1s, intros, rests = "", "", ""
    for c, (t, h) in langs.items():
        i = h.find("<h2")
        i = len(h) if i < 0 else i
        h1s += f'<h1 data-lang="{c}">{html.escape(t)}</h1>'
        intros += f'<article data-lang="{c}">{h[:i]}</article>'
        rests += f'<article data-lang="{c}">{h[i:]}</article>'
    n_in = len(ph["lessons"])
    k = ph["lessons"].index(les) + 1
    meta = (f'<div class="lmeta">{phase_chip(ph)}<span class="lno"><span data-lang="en">Lesson {k} of {n_in}</span>'
            f'<span data-lang="ko">레슨 {k} / {n_in}</span></span>{dots(pid)}</div>')
    title = langs["en"][0]
    quiz_sec = ('<section id="quiz"><h2 data-lang="en">Check yourself</h2><h2 data-lang="ko">스스로 점검</h2>'
                '<p class="qintro" data-lang="en">Six questions in three stages: warm-up, checks, boss round. Wrong answers cost nothing.</p>'
                '<p class="qintro" data-lang="ko">여섯 문제를 세 단계(워밍업, 체크, 보스전)로 풉니다. 틀려도 잃는 것은 없습니다.</p>'
                '<div id="quizbox"></div></section>')
    nav = f'<nav class="pager">{pager_card(prev_, "prev")}{pager_card(next_, "next")}</nav>'
    body = (f'<div class="lp" data-f="{FAM[ph["num"]]}">{meta}{scene}{h1s}{hook}{intros}{concept}{toy}<span hidden data-rest="a"></span>{rests}<span hidden data-rest="b"></span>{mission}{quiz_sec}{nav}'
            f"<script>window.QUIZ={json.dumps(quiz, ensure_ascii=False).replace('</', '<\\/')};</script></div>")
    return shell(f"{title} · Robotics from Scratch", body, phases, pid), pid


def fun_html(fun, pid=""):
    """(hook, mission, toy) html: Bolt's speech bubble, the mission card, the playground slot."""
    if not fun:
        return "", "", ""
    e = html.escape
    top = ""
    for c in ("en", "ko"):
        f = fun.get(c)
        if f:
            top += f'<div class="bolt" data-lang="{c}">{bolt_svg("idle", "hookbolt")}<p>{inline(f["hook"])}</p></div>'
    toy = f'<div class="toy" data-toy="{e(fun["toy"])}"></div>' if fun.get("toy") else ""
    bot = ""
    for c, lab in (("en", "Mission"), ("ko", "미션")):
        f = fun.get(c)
        if f:
            bot += (f'<label class="mission" data-lang="{c}"><input type="checkbox" class="mchk" data-pid="{pid}"><span class="mbody"><b>{lab}</b>'
                    f'{inline(f["mission"])}<i class="xpt">+20 XP</i></span></label>')
    return top, bot, toy


# ---- shell: header, sidebar, scripts ------------------------------------------------------------------------------
def sidebar(phases, current):
    out = []
    for name, ph in phases.items():
        ko = PHASE_KO.get(ph["slug"], ph["slug"])
        items = "".join(
            f'<a data-pid="{pid_of(ph, l)}" href="{pid_of(ph, l)}.html"{" class=cur" if pid_of(ph, l) == current else ""}>'
            f'<b>{l.name.split("-", 1)[0]}</b><span class="at">{tt(l)}</span></a>' for l in ph["lessons"])
        out.append(f'<details data-f="{FAM[ph["num"]]}"{" open" if current and current.startswith(ph["num"] + "-") else ""}><summary>'
                   f'<i class="pm"></i><span class="sn"><span data-lang="en">{ph["num"]} {phase_title(ph["slug"])}</span><span data-lang="ko">{ph["num"]} {ko}</span></span>'
                   f'<small class="pc" data-ph="{ph["num"]}"></small></summary>{items}</details>')
    return "".join(out)


HEADER = ('<header><a class="brand" href="index.html">' + bolt_svg("idle", "brandbolt")
          + '<span class="bt">Robotics<br><b>from Scratch</b></span></a>'
          '<div class="tools"><span id="xp" title="XP"></span>'
          f'<button id="menu" aria-label="contents" aria-expanded="false">{ic("menu")}</button>'
          f'<button id="lang" aria-label="language" title="English / 한국어">{ic("globe")}<span data-lang="en">EN</span><span data-lang="ko">KO</span></button>'
          '<button id="theme" aria-label="theme"><svg class="ic" viewBox="0 0 16 16" aria-hidden="true"><circle cx="8" cy="8" r="6.500" fill="none"/>'
          '<path d="M8 1.500a6.500 6.500 0 0 0 0 13z" fill="currentColor"/></svg></button></div></header>')


def shell(title, content, phases, current=None, extra="", main_cls=""):
    ORDJSON = json.dumps([pid_of(ph, l) for ph in phases.values() for l in ph["lessons"]])
    PHJSON = json.dumps({ph["num"]: [pid_of(ph, l) for l in ph["lessons"]] for ph in phases.values()})
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<link rel="icon" href="icon.svg" type="image/svg+xml"><link rel="apple-touch-icon" href="icon-192.png"><meta name="theme-color" content="#f2f6f7">
<title>{html.escape(title)}</title><style>{CSS}</style></head><body>{sprite()}{HEADER}
<div class="layout"><aside>{sidebar(phases, current)}</aside><main{main_cls}>{content}</main></div><div id="toast" role="status" aria-live="polite"></div><script>window.PH={PHJSON};window.ORD={ORDJSON};window.FAM={json.dumps(FAM)};window.CUR={json.dumps(current)};</script><script>{JS}</script><script src="toys.js" defer></script><script src="motion.js" defer></script>{extra}</body></html>"""


# ---- index: hero, HUD, daily 5, learning path, sync ---------------------------------------------------------------
def hero_art() -> str:
    """Robot arm reaching for a nut: drawn from shapes, animated with three nested rotations (see .j1 .j2 .j3 in CSS)."""
    ticks = "".join(f"M{x} 316l-9 11" for x in range(14, 520, 26))
    return f"""<svg class="harm" viewBox="0 0 520 360" role="img" aria-label="A robot arm reaching for a nut">
<defs><pattern id="hgd" width="26" height="26" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1.500" class="hdot"/></pattern></defs>
<rect width="520" height="360" fill="url(#hgd)"/>
<path class="reach" d="M-50 262A240 240 0 0 1 430 262"/>
<path class="floor" d="M0 316H520"/><path class="hatch" d="{ticks}"/>
<g class="frame"><path d="M100 300h34M100 300V266"/><path d="m134 300-6-4v8zM100 266l-4 6h8z" class="fillink"/></g>
<rect class="part" x="96" y="292" width="190" height="24" rx="7"/><rect class="part" x="148" y="262" width="84" height="32" rx="10"/>
<g class="j1"><rect class="link" data-f="2" x="176" y="150" width="28" height="126" rx="14"/>
<g class="j2"><rect class="link" data-f="2" x="179" y="52" width="22" height="122" rx="11"/>
<g class="j3"><path class="grip" d="M178 70V28q0-8 8-8h2v26M202 70V28q0-8-8-8h-2v26"/><rect class="part" x="176" y="44" width="28" height="26" rx="8"/>
<circle class="joint" cx="190" cy="62" r="9"/></g><circle class="joint" cx="190" cy="162" r="10"/></g><circle class="joint" cx="190" cy="262" r="12"/></g>
<g class="nut" data-f="5"><polygon points="356,282 368,289 368,303 356,310 344,303 344,289"/><circle cx="356" cy="296" r="5"/></g></svg>"""


def index(phases):
    cards = ""
    for ph in phases.values():
        ko = PHASE_KO.get(ph["slug"], ph["slug"])
        n = len(ph["lessons"])
        wire, nodes = [], ""
        for i, l in enumerate(ph["lessons"]):
            o = OFFS[i % len(OFFS)]
            pid = pid_of(ph, l)
            side = "L" if o > 0 or (o == 0 and i % 2 == 0) else "R"
            wire.append((o, ROW * i + ROW // 2))
            nodes += (f'<a class="node {side}" data-pid="{pid}" href="{pid}.html" style="--o:{o}px"><span class="dot"><b>{l.name.split("-", 1)[0]}</b></span>'
                      f'<span class="lab">{tt(l)}</span></a>')
        d = f"M{wire[0][0]} {wire[0][1]}"
        for (x0, y0), (x1, y1) in zip(wire, wire[1:]):
            d += f" C{x0} {y0 + ROW // 2} {x1} {y1 - ROW // 2} {x1} {y1}"
        h = ROW * n
        cards += (f'<section class="ph" data-f="{FAM[ph["num"]]}" data-ph="{ph["num"]}" style="--ih:{h + 86}px"><div class="pbanner"><span class="pnum">{ph["num"]}</span>'
                  f'<span class="pname"><span data-lang="en">{phase_title(ph["slug"])}</span><span data-lang="ko">{ko}</span></span>'
                  f'<span class="ring" data-ph="{ph["num"]}"></span></div><div class="trail" style="height:{h}px">'
                  f'<svg class="wire" width="224" height="{h}" viewBox="-112 0 224 {h}" aria-hidden="true"><path d="{d}"/></svg>{nodes}</div></section>')
    strip = "".join(f'<i data-f="{FAM[ph["num"]]}" data-pid="{pid_of(ph, l)}"></i>' for ph in phases.values() for l in ph["lessons"])
    hero = f"""<section class="hero">
<div class="hero-copy"><h1 data-lang="en">Robotics Engineering from Scratch</h1><h1 data-lang="ko">처음부터 배우는 로봇공학</h1>
<p data-lang="en">Short, visual lessons. See the idea in pictures, build it in a few lines, check yourself.</p>
<p data-lang="ko">짧고 그림 중심인 레슨입니다. 그림으로 개념을 보고 몇 줄로 직접 만든 다음 스스로 점검합니다.</p>
<div class="cta"><a id="cont" class="go" href="#"></a><span class="meta"><span data-lang="en">67 lessons · English and Korean</span><span data-lang="ko">레슨 67개 · 영어와 한국어</span></span></div></div>
<figure class="heroart" data-f="2">{hero_art()}<span class="mascot"><span id="hbolt">{bolt_svg("sleepy")}</span><span id="hsay" class="say"></span></span></figure>
<div id="stats" class="hud"><div class="hud-l"><div class="lv"><span class="lvn" id="h-lv"></span><b id="h-lvname"></b><span class="xpm" id="h-xpm"></span></div>
<div class="xpbar"><i id="h-bar"></i></div></div>
<div class="tiles"><div class="tile">{ic("bolt")}<b id="h-xp">0</b><span>XP</span></div>
<div class="tile">{ic("flame")}<b id="h-st">0</b><span data-lang="en">day streak</span><span data-lang="ko">일 연속</span></div>
<div class="tile">{ic("medal")}<b id="h-bd">0</b><span data-lang="en">badges</span><span data-lang="ko">배지</span></div>
<div class="tile">{ic("check")}<b id="h-dn">0</b><span data-lang="en">of 67 done</span><span data-lang="ko">/ 67 완료</span></div></div>
<div class="strip" aria-hidden="true">{strip}</div></div></section>"""
    daily = f"""<section class="daily" id="daily" data-f="4"><div class="dhead"><span class="dic">{ic("cal")}</span><h3><span data-lang="en">Daily 5</span><span data-lang="ko">오늘의 5문제</span></h3></div>
<div class="dsum"><p data-lang="en">Five quick questions from lessons you have started. +5 XP per correct answer, up to 25 XP a day.</p>
<p data-lang="ko">시작한 레슨에서 빠른 문제 5개를 뽑습니다. 정답마다 +5 XP이고 하루 최대 25 XP입니다.</p>
<div class="dprog"><span class="dpips" aria-hidden="true"><i></i><i></i><i></i><i></i><i></i></span><b id="dtoday">0 / 25 XP</b></div>
<button id="dplay" class="btn pri" type="button">{ic("play")}<span id="dlabel"></span></button></div><div id="dbox"></div></section>"""
    sync = f"""<section class="sync" id="sync"><h3><span data-lang="en">Take your progress along</span><span data-lang="ko">진행 상황 옮기기</span></h3>
<p data-lang="en">Progress lives in this browser. Copy a code here, paste it on another device. Merging never lowers anything.</p>
<p data-lang="ko">진행 상황은 이 브라우저에 저장됩니다. 여기서 코드를 복사해 다른 기기에 붙여 넣으세요. 합쳐도 줄어드는 것은 없습니다.</p>
<div class="srow"><button id="sync-copy" class="btn" type="button">{ic("copy")}<span data-lang="en">Copy progress code</span><span data-lang="ko">진행 코드 복사</span></button>
<button id="sync-paste" class="btn" type="button">{ic("paste")}<span data-lang="en">Paste progress code</span><span data-lang="ko">진행 코드 붙여넣기</span></button></div>
<div id="sync-panel" hidden><textarea id="sync-ta" rows="4" spellcheck="false" autocomplete="off" aria-label="progress code"></textarea>
<div class="srow"><button id="sync-sel" class="btn" type="button"><span data-lang="en">Select all</span><span data-lang="ko">모두 선택</span></button>
<button id="sync-go" class="btn pri" type="button" hidden><span data-lang="en">Merge</span><span data-lang="ko">합치기</span></button></div><p id="sync-msg" class="smsg" aria-live="polite"></p></div>
<div class="srow"><button id="sync-clear" class="btn" type="button">{ic("x")}<span data-lang="en">Clear local data</span><span data-lang="ko">로컬 데이터 지우기</span></button></div>
<div id="clear-box" hidden><p data-lang="en">This clears the saved page state (last lesson, scroll spot, unfinished quiz rounds, slider values) and the offline copy on this device. Your XP and progress stay.</p>
<p data-lang="ko">이 기기에 저장된 화면 상태(마지막 레슨, 스크롤 위치, 풀던 퀴즈, 슬라이더 값)와 오프라인 사본을 지웁니다. XP와 진행 상황은 그대로입니다.</p>
<div class="srow"><button id="clear-yes" class="btn pri" type="button"><span data-lang="en">Clear</span><span data-lang="ko">지우기</span></button><button id="clear-no" class="btn" type="button"><span data-lang="en">Cancel</span><span data-lang="ko">취소</span></button></div></div>
<p id="clear-msg" class="smsg" aria-live="polite"></p>
<div id="pack" hidden><div class="srow"><button id="pack-go" class="btn" type="button"><span data-lang="en">Download all figures for offline use (about {figure_mb()} MB)</span><span data-lang="ko">그림 전체를 오프라인용으로 받기 (약 {figure_mb()} MB)</span></button></div>
<div id="pack-box" hidden><progress id="pack-bar" max="1" value="0" aria-label="download progress"></progress><div class="srow"><p id="pack-msg" class="smsg" aria-live="polite"></p><button id="pack-cancel" class="btn" type="button"><span data-lang="en">Cancel</span><span data-lang="ko">취소</span></button></div></div></div></section>"""
    path = f'<div class="path" id="path">{cards}<span id="you" class="you" aria-hidden="true">{bolt_svg("cheer")}</span></div>'
    body = f'<div class="home">{hero}<div class="home-body"><div class="side">{daily}{sync}</div>{path}</div></div>'
    return shell("Robotics Engineering from Scratch", body, phases, main_cls=' class="hm"')


def main() -> int:
    phases = load_lessons()
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir()
    flat = [pid_of(ph, l) for ph in phases.values() for l in ph["lessons"]]
    for ph in phases.values():
        for les in ph["lessons"]:
            LESMAP[pid_of(ph, les)] = les
    for ph in phases.values():
        for les in ph["lessons"]:
            doc, pid = page(ph, les, phases, flat)
            (SITE / f"{pid}.html").write_text(doc)
    (SITE / "index.html").write_text(index(phases))
    (SITE / "quizzes.js").write_text("window.QUIZS=" + json.dumps(QUIZ_ALL, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/") + ";")
    (SITE / "motion.js").write_text("\n".join(f.read_text() for f in sorted((ROOT / "scripts" / "motion").glob("*.js"))))
    (SITE / "toys.js").write_text("\n".join(f.read_text() for f in sorted((ROOT / "scripts" / "toys").glob("*.js"))))
    pwa(flat)
    print(f"{len(flat)} lessons -> {SITE}/index.html")
    return 0


# ---- offline cache: vendored GSAP, web app manifest, Bolt icons, service worker with a build-hash version -------------
SHELL_FILES = ["toys.js", "motion.js", "quizzes.js", "assets.json", "vendor/gsap.min.js", "manifest.webmanifest", "icon.svg", "icon-192.png", "icon-512.png"]
ICON_BG, ICON_FG, ICON_GLOW = (14, 26, 31), (242, 246, 247), (65, 200, 230)


def bolt_icon(size: int, scale: float):
    """Bolt's head and body drawn with PIL at 4x and shrunk: the sprite SVG cannot be rendered without a browser."""
    from PIL import Image, ImageDraw
    S = size * 4
    im = Image.new("RGB", (S, S), ICON_BG)
    d = ImageDraw.Draw(im)
    k = S * scale / 64  # one bolt unit in pixels, bolt box is 64 x 64 centred
    ox = oy = S * (1 - scale) / 2

    def P(x, y):
        return ox + x * k, oy + y * k

    def box(x, y, w, h, r, fill):
        d.rounded_rectangle([*P(x, y), *P(x + w, y + h)], radius=r * k, fill=fill)

    def dot(x, y, r, fill):
        d.ellipse([*P(x - r, y - r), *P(x + r, y + r)], fill=fill)

    d.line([P(32, 11), P(32, 5)], fill=ICON_FG, width=int(2.5 * k))
    dot(32, 4.5, 3, ICON_GLOW)
    box(19, 46, 26, 15, 6, ICON_FG)
    dot(32, 53.5, 2.6, ICON_GLOW)
    box(4.5, 22, 6, 11, 3, ICON_FG)
    box(53.5, 22, 6, 11, 3, ICON_FG)
    box(10, 11, 44, 34, 13, ICON_FG)
    box(16, 17, 32, 22, 9, ICON_BG)
    dot(26, 27, 3.3, ICON_GLOW)
    dot(38, 27, 3.3, ICON_GLOW)
    pts = [((1 - t) ** 2 * 28.5 + 2 * (1 - t) * t * 32 + t * t * 35.5, (1 - t) ** 2 * 33.5 + 2 * (1 - t) * t * 36.3 + t * t * 33.5) for t in (i / 20 for i in range(21))]  # the smile, a quadratic curve
    d.line([P(x, y) for x, y in pts], fill=ICON_GLOW, width=int(2.6 * k), joint="curve")
    return im.resize((size, size), Image.LANCZOS)


ICON_SVG = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#0e1a1f"/>'
            '<g transform="translate(6.4 6.4) scale(.8)"><path d="M32 11V5" stroke="#f2f6f7" stroke-width="2.5" stroke-linecap="round"/><circle cx="32" cy="4.5" r="3" fill="#41c8e6"/>'
            '<rect x="19" y="46" width="26" height="15" rx="6" fill="#f2f6f7"/><circle cx="32" cy="53.5" r="2.6" fill="#41c8e6"/>'
            '<rect x="4.5" y="22" width="6" height="11" rx="3" fill="#f2f6f7"/><rect x="53.5" y="22" width="6" height="11" rx="3" fill="#f2f6f7"/>'
            '<rect x="10" y="11" width="44" height="34" rx="13" fill="#f2f6f7"/><rect x="16" y="17" width="32" height="22" rx="9" fill="#0e1a1f"/>'
            '<circle cx="26" cy="27" r="3.3" fill="#41c8e6"/><circle cx="38" cy="27" r="3.3" fill="#41c8e6"/>'
            '<path d="M28.5 33.5q3.5 2.8 7 0" fill="none" stroke="#41c8e6" stroke-width="2.6" stroke-linecap="round"/></g></svg>')


def tree_hash(files) -> str:
    h = hashlib.sha1()
    for f in sorted(files):
        h.update(f.relative_to(SITE).as_posix().encode())
        h.update(hashlib.sha1(f.read_bytes()).digest())
    return h.hexdigest()[:10]


def figure_index() -> dict:
    """{lesson id: [[path, bytes], ...]} for the Offline pack and the next-lesson prefetch"""
    out = {}
    for d in sorted((SITE / "assets").glob("*")):
        files = sorted(d.glob("*.png"))
        if files:
            out[d.name] = [[f"assets/{d.name}/{f.name}", f.stat().st_size] for f in files]
    return out


def figure_mb() -> int:
    return round(sum(b for v in figure_index().values() for _, b in v) / 1e6)


def pwa(flat):
    (SITE / "vendor").mkdir(exist_ok=True)
    idx = figure_index()
    (SITE / "assets.json").write_text(json.dumps({"total": sum(b for v in idx.values() for _, b in v), "lessons": idx}, separators=(",", ":")))
    shutil.copy(ROOT / "scripts" / "vendor" / "gsap.min.js", SITE / "vendor" / "gsap.min.js")
    (SITE / "icon.svg").write_text(ICON_SVG)
    bolt_icon(192, .86).save(SITE / "icon-192.png", optimize=True)
    bolt_icon(512, .86).save(SITE / "icon-512.png", optimize=True)
    bolt_icon(512, .62).save(SITE / "icon-maskable-512.png", optimize=True)
    (SITE / "manifest.webmanifest").write_text(json.dumps({
        "name": "Robotics Engineering from Scratch", "short_name": "Robotics", "description": "Short visual robotics lessons with quizzes, English and Korean.",
        "start_url": "./index.html", "scope": "./", "display": "standalone", "background_color": "#f2f6f7", "theme_color": "#f2f6f7",
        "icons": [{"src": "icon-192.png", "sizes": "192x192", "type": "image/png", "purpose": "any"},
                  {"src": "icon-512.png", "sizes": "512x512", "type": "image/png", "purpose": "any"},
                  {"src": "icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"}]}, indent=1))
    files = [f for f in SITE.rglob("*") if f.is_file() and f.name != "sw.js"]
    assets = [f for f in files if "assets" in f.relative_to(SITE).parts]
    sw = (ROOT / "scripts" / "sw.js").read_text()
    sw = (sw.replace("__V__", tree_hash(files)).replace("__AV__", tree_hash(assets))
          .replace("__SHELL__", json.dumps(SHELL_FILES)).replace("__LESSONS__", json.dumps({f"{p}.html": hashlib.sha1((SITE / f"{p}.html").read_bytes()).hexdigest()[:16] for p in flat})))
    (SITE / "sw.js").write_text(sw)


# monokai code panels in both themes (dark ink panel on light pages)
PYG = (HtmlFormatter(style="monokai").get_style_defs(".hl") if highlight else "")

CSS = r"""
:root{--h:198;--ink0:#0e1a1f;--sans:ui-sans-serif,-apple-system,"Segoe UI","Pretendard","Noto Sans KR","Apple SD Gothic Neo",system-ui,sans-serif;--mono:ui-monospace,"SF Mono","JetBrains Mono",Menlo,Consolas,monospace;
--bg:#f2f6f7;--card:#fff;--fg:#0e1a1f;--mut:#475a64;--line:#d6e1e6;--code:#e6eef1;--acc:#1f5fd6;--accbg:#e3edfb;--ok:#177a45;--okbg:#e2f5ea;--oops:#a85a00;--oopsbg:#fdf0dc;--bad:#c2410c;
--Lf:.8;--Cf:.14;--Lt:.44;--Ct:.15;--Lb:.955;--Cb:.035;--Ll:.76;--Cl:.1;--Ld:.6;--Cd:.15;
--sh:0 1px 0 rgb(14 26 31/.04),0 12px 28px -14px rgb(14 26 31/.22);--e:cubic-bezier(.23,1,.32,1);color-scheme:light}
:root[data-theme=dark]{--bg:#0d1317;--card:#151d23;--fg:#e8eff2;--mut:#9fb1ba;--line:#27343c;--code:#0b1014;--acc:#7fb0ff;--accbg:#1b2a44;--ok:#5ad08a;--okbg:#12291d;--oops:#ffb454;--oopsbg:#33250f;--bad:#ff9a6b;
--Lf:.78;--Cf:.13;--Lt:.84;--Ct:.12;--Lb:.27;--Cb:.05;--Ll:.46;--Cl:.09;--Ld:.52;--Cd:.12;--sh:0 1px 0 rgb(255 255 255/.03),0 14px 30px -16px rgb(0 0 0/.7);color-scheme:dark}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#0d1317;--card:#151d23;--fg:#e8eff2;--mut:#9fb1ba;--line:#27343c;--code:#0b1014;--acc:#7fb0ff;--accbg:#1b2a44;--ok:#5ad08a;--okbg:#12291d;--oops:#ffb454;--oopsbg:#33250f;--bad:#ff9a6b;
--Lf:.78;--Cf:.13;--Lt:.84;--Ct:.12;--Lb:.27;--Cb:.05;--Ll:.46;--Cl:.09;--Ld:.52;--Cd:.12;--sh:0 1px 0 rgb(255 255 255/.03),0 14px 30px -16px rgb(0 0 0/.7);color-scheme:dark}}
[data-f="1"]{--h:198}[data-f="2"]{--h:262}[data-f="3"]{--h:150}[data-f="4"]{--h:80}[data-f="5"]{--h:35}[data-f="6"]{--h:350}
:root,[data-f]{--pf:oklch(var(--Lf) var(--Cf) var(--h));--pt:oklch(var(--Lt) var(--Ct) var(--h));--pb:oklch(var(--Lb) var(--Cb) var(--h));--pl:oklch(var(--Ll) var(--Cl) var(--h));--pd:oklch(var(--Ld) var(--Cd) var(--h))}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:17px/1.7 var(--sans);-webkit-text-size-adjust:100%}
button{font:inherit;color:inherit}
:focus-visible{outline:3px solid var(--pt);outline-offset:2px;border-radius:6px}
.ic{width:1.15em;height:1.15em;vertical-align:-.2em;fill:none;stroke:currentColor;stroke-width:2;stroke-linecap:round;stroke-linejoin:round;flex:none}
html[lang=en] [data-lang=ko],html[lang=ko] [data-lang=en]{display:none!important}
html[lang=ko] body{word-break:keep-all;overflow-wrap:break-word}html[lang=ko] pre,html[lang=ko] code{word-break:normal}

/* header */
header{position:sticky;top:0;z-index:5;display:flex;justify-content:space-between;align-items:center;gap:8px;padding:6px 20px;min-height:60px;background:color-mix(in srgb,var(--bg) 86%,transparent);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
.brand{display:flex;align-items:center;gap:10px;color:var(--fg);text-decoration:none;line-height:1.12;font-size:13px;letter-spacing:.01em;min-height:44px;min-width:44px}.brand b{font-size:17px;letter-spacing:-.01em}
.brandbolt{width:36px;height:36px;flex:none}
.tools{display:flex;align-items:center;gap:6px}
.tools button{display:inline-flex;align-items:center;justify-content:center;gap:6px;min-width:44px;min-height:44px;padding:0 12px;border:1.5px solid var(--line);background:var(--card);border-radius:14px;font-size:13px;font-weight:700;cursor:pointer;transition:transform .12s var(--e),border-color .15s}
.tools button:active{transform:scale(.96)}.tools button:hover{border-color:var(--pl)}
#menu{display:none}
#xp{display:inline-flex;align-items:center;gap:5px;min-height:34px;padding:0 12px;border-radius:99px;background:var(--pb);color:var(--pt);font:700 13px var(--mono);white-space:nowrap}#xp .hs{display:inline-flex;align-items:center;gap:3px}

/* layout + sidebar */
.layout{display:grid;grid-template-columns:276px minmax(0,1fr);max-width:1240px;margin:0 auto}
aside{position:sticky;top:60px;align-self:start;height:calc(100vh - 60px);overflow:auto;padding:16px 10px 40px 18px;font-size:14px}
aside details{margin-bottom:4px}
aside summary{display:flex;align-items:center;gap:10px;cursor:pointer;font-weight:700;min-height:40px;padding:2px 8px;border-radius:12px;list-style:none}
aside summary::-webkit-details-marker{display:none}aside summary:hover{background:var(--card)}
.pm{width:14px;height:14px;border-radius:5px;background:var(--pf);flex:none}.sn{flex:1;min-width:0}.pc{font:600 11px var(--mono);color:var(--mut)}
aside a{display:flex;gap:8px;align-items:baseline;color:var(--mut);text-decoration:none;padding:6px 10px 6px 12px;margin-left:12px;border-radius:10px;min-height:34px;line-height:1.35}
aside a b{font:700 11px var(--mono);color:var(--pt);flex:none;min-width:1.7em}aside a .at{flex:1;min-width:0}
aside a:hover{background:var(--card);color:var(--fg)}aside a.cur{background:var(--pb);color:var(--fg);font-weight:700}
aside a.done::after{content:"";width:15px;height:15px;flex:none;align-self:center;background:var(--ok);-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m5 12.500 4.500 4.500L19 7.500'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m5 12.500 4.500 4.500L19 7.500'/%3E%3C/svg%3E") center/contain no-repeat}

/* content typography */
main{padding:26px 28px 90px;min-width:0;max-width:820px}
main.hm{max-width:none;padding-top:10px}
article{overflow-wrap:anywhere}
h1{font-size:clamp(1.9rem,5.6vw,2.55rem);line-height:1.12;margin:.15em 0 .45em;letter-spacing:-.02em;font-weight:800;text-wrap:balance}
h2{position:relative;font-size:1.45rem;line-height:1.25;letter-spacing:-.01em;font-weight:800;margin:2.3em 0 .6em;padding-top:14px;text-wrap:balance}
h2::before{content:"";position:absolute;top:0;left:0;width:34px;height:5px;border-radius:3px;background:var(--pf)}
.lp p,.lp li{max-width:68ch}
.lp>article>p,.lp>article li{margin:.7em 0}
.idea{position:relative;font-size:1.15rem;line-height:1.55;margin:.4em 0 1.1em;padding:18px 20px 18px 66px;border-radius:20px;background:var(--pb);font-weight:600;max-width:none!important}
.idea::before{content:"";position:absolute;left:18px;top:18px;width:32px;height:32px;border-radius:11px;background:var(--pf) url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24'%3E%3Cpath fill='%230e1a1f' d='M13.200 2 4.500 13.600c-.3.4 0 1 .5 1h5.300l-1 6.600c-.1.6.6.9 1 .4l8.600-11.800c.3-.4 0-1-.5-1h-5.100l.9-6c.1-.6-.7-.9-1-.4z'/%3E%3C/svg%3E") center/18px no-repeat}
.chips{display:flex;flex-wrap:wrap;gap:8px;margin:0 0 1.2em}.chips span{font-size:13px;line-height:1.4;padding:4px 13px;border-radius:99px;background:var(--card);border:1.5px solid var(--line);color:var(--mut)}.chips strong{color:var(--fg)}
figure{counter-increment:fig;margin:1.6em 0;padding:10px 10px 0;background:var(--card);border:1.5px solid var(--line);border-radius:22px;box-shadow:var(--sh);overflow:hidden}
figure img{display:block;width:100%;height:auto;border-radius:14px;background:#fff;padding:6px}
figcaption{margin:0 -10px;padding:11px 16px 13px;font-size:14.5px;color:var(--mut);line-height:1.5;border-top:1.5px dashed var(--line);margin-top:10px}
figcaption:empty{display:none}
figcaption::before{content:counter(fig);display:inline-grid;place-items:center;min-width:22px;height:22px;margin-right:9px;border-radius:7px;background:var(--pb);color:var(--pt);font:700 12px var(--mono);vertical-align:1px}
.lp{counter-reset:fig}
code{background:var(--code);padding:.12em .42em;border-radius:7px;font:.9em var(--mono);overflow-wrap:anywhere}
pre.hl{position:relative;background:#10171b;color:#e8eff2;padding:30px 18px 16px;border-radius:18px;overflow:auto;font-size:14px;line-height:1.6;margin:1.3em 0;border:1.5px solid #26343c}
pre.hl code{background:none;padding:0;color:inherit;overflow-wrap:normal}
pre.hl::before{content:attr(data-lang);position:absolute;top:8px;left:14px;font:700 11px var(--mono);letter-spacing:.08em;color:#8ea0aa;text-transform:lowercase}
pre.hl[data-lang=""]::before{display:none}
.tablewrap{overflow:auto;border:1.5px solid var(--line);border-radius:16px;background:var(--card);margin:1.2em 0}
table{border-collapse:collapse;width:100%;font-size:15px}th,td{padding:10px 14px;text-align:left;border-bottom:1px solid var(--line)}tr:last-child td{border-bottom:0}th{background:var(--pb);font-weight:700;white-space:nowrap}
a{color:var(--pt);text-underline-offset:3px}ul,ol{padding-left:1.4em}li{margin:.3em 0}li::marker{color:var(--pt);font-weight:700}

/* lesson header, hook, mission, playground, pager */
.lmeta{display:flex;flex-wrap:wrap;align-items:center;gap:8px 12px;margin:0 0 6px}
.chip.ph{display:inline-flex;align-items:center;min-height:32px;padding:0 14px;border-radius:99px;background:var(--pf);color:var(--ink0);font-size:13px;font-weight:800;letter-spacing:.01em}
.lno{font:600 13px var(--mono);color:var(--mut)}
.dots{display:inline-flex;gap:5px;margin-left:auto;align-items:center}.dots i{width:10px;height:10px;border-radius:50%;border:2px solid var(--pl);background:transparent;transition:background .2s,transform .2s var(--e)}
.dots i.on{background:var(--pf);border-color:var(--pf)}.dots i.miss{border-style:dashed;border-color:var(--oops)}
.dots i.dm{width:12px;height:12px;border-radius:4px;margin-left:5px;transform:rotate(45deg)}
.dots i.dm.on{background:var(--pf);border-color:var(--pd)}
.bolt{display:flex;gap:12px;align-items:flex-start;margin:0 0 1.3em}
.hookbolt{width:58px;height:58px;flex:none;animation:bob 3.4s ease-in-out infinite}
.bolt p{position:relative;margin:4px 0 0;padding:12px 16px;border-radius:20px 20px 20px 6px;background:var(--card);border:1.5px solid var(--line);font-size:1.05rem;font-weight:500;line-height:1.55;box-shadow:var(--sh)}
.mission{position:relative;display:flex;gap:14px;align-items:flex-start;margin:2.4em 0 0;padding:18px 20px;border-radius:22px;border:2px solid var(--pl);background:var(--pb);cursor:pointer;transition:transform .15s var(--e),background .2s}
.mission:active{transform:scale(.99)}
.mission input{appearance:none;-webkit-appearance:none;flex:none;width:30px;height:30px;margin:2px 0 0;border:2.5px solid var(--pt);border-radius:10px;background:var(--card);cursor:pointer;display:grid;place-items:center;transition:background .15s}
.mission input::after{content:"";width:16px;height:16px;transform:scale(0);background:var(--ink0);-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='3.500' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m5 12.500 4.500 4.500L19 7.500'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='3.500' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m5 12.500 4.500 4.500L19 7.500'/%3E%3C/svg%3E") center/contain no-repeat;transition:transform .2s var(--e)}
.mission input:checked{background:var(--pf);border-color:var(--pd)}.mission input:checked::after{transform:scale(1)}
.mbody{overflow-wrap:anywhere;line-height:1.55}.mbody b{display:inline-block;margin-right:.6em;font-size:12px;letter-spacing:.06em;padding:1px 10px;border-radius:99px;background:var(--pf);color:var(--ink0);text-transform:uppercase}
html[lang=ko] .mbody b{letter-spacing:0;text-transform:none}
.xpt{font:700 12px var(--mono);font-style:normal;margin-left:10px;padding:2px 9px;border-radius:99px;background:var(--card);color:var(--pt);white-space:nowrap}
.toy{position:relative;margin:2em 0 1.6em;padding:46px 16px 16px;border:2px solid var(--pf);border-radius:24px;background:var(--card) radial-gradient(circle at 1px 1px,var(--line) 1.2px,transparent 1.5px) 0 0/18px 18px;box-shadow:0 6px 0 var(--pd)}
.toy::before{content:"Playground";position:absolute;top:-2px;left:18px;padding:5px 16px 4px;border-radius:0 0 14px 14px;background:var(--pf);color:var(--ink0);font:800 12px var(--sans);letter-spacing:.06em;text-transform:uppercase}
html[lang=ko] .toy::before{content:"놀이터";letter-spacing:0}.toy:empty{min-height:320px}
.toy h4{margin:0 0 10px;font-size:1.05rem}.toy canvas{width:100%;height:auto;display:block;border-radius:14px;background:var(--bg);border:1.5px solid var(--line);touch-action:none}
.toy label{display:flex;gap:10px;align-items:center;font-size:14px;margin:8px 0;min-height:36px}.toy input[type=range]{flex:1;accent-color:var(--pt);min-height:44px}
.toy .readout{font:13px var(--mono);color:var(--mut);margin-top:6px}
.toy button{min-height:44px;padding:0 16px;border-radius:99px;border:1.5px solid var(--pl);background:var(--card);font-weight:700;cursor:pointer}.toy button:active{transform:scale(.97)}
.pager{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:3em 0 0}
.pn{display:flex;flex-direction:column;gap:2px;padding:14px 18px;min-height:76px;border-radius:20px;border:1.5px solid var(--line);background:var(--card);text-decoration:none;color:var(--fg);transition:transform .15s var(--e),border-color .15s}
.pn small{display:flex;gap:6px;align-items:center;font-size:12px;color:var(--mut);font-weight:700}.pn b{font-size:15px;line-height:1.35}
.pn.next{background:var(--pf);border-color:transparent;color:var(--ink0);text-align:right;box-shadow:0 4px 0 var(--pd)}.pn.next small{color:var(--ink0);justify-content:flex-end;opacity:.8}
.pn:active{transform:scale(.98)}.pn.next:active{transform:translateY(2px);box-shadow:0 2px 0 var(--pd)}
.pager>span{display:block}

/* quiz game */
#quiz{margin-top:2.2em}.qintro{margin:-.2em 0 1em;color:var(--mut);font-size:15px}
#quizbox{max-width:660px}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:8px;min-height:46px;padding:0 20px;border-radius:99px;border:1.5px solid var(--line);background:var(--card);font-weight:700;font-size:15px;text-decoration:none;color:var(--fg);cursor:pointer;transition:transform .12s var(--e),border-color .15s,box-shadow .12s}
.btn:hover{border-color:var(--pl)}.btn:active{transform:scale(.97)}
.btn.pri{background:var(--pf);border-color:transparent;color:var(--ink0);box-shadow:0 4px 0 var(--pd)}.btn.pri:active{transform:translateY(2px);box-shadow:0 2px 0 var(--pd)}
.btn:disabled{opacity:.55;cursor:default}
.qhud{display:flex;gap:12px;align-items:center;margin:0 0 14px}
.qbolt{flex:none;width:58px;height:58px}.qbolt .bolt-svg{width:100%;height:100%}
.qmeta{flex:1;min-width:0}
.qline{display:flex;align-items:center;gap:8px;flex-wrap:wrap;min-height:28px}
.qstage{font-size:13px;line-height:1;padding:7px 13px;border-radius:99px;background:var(--pf);color:var(--ink0);font-weight:800}
.qpos{font:600 13px var(--mono);color:var(--mut)}
.qcombo{margin-left:auto;display:inline-flex;gap:4px;align-items:center;font:800 13px var(--mono);color:var(--pt)}.qcombo[hidden]{display:none}
.qpips{display:grid;grid-auto-flow:column;grid-auto-columns:1fr;gap:5px;margin-top:7px}
.qpips i{height:9px;border-radius:5px;background:var(--line);transition:background .25s}
.qpips i.cur{background:color-mix(in srgb,var(--pf) 50%,var(--line))}.qpips i.ok{background:var(--pf)}
.qpips i.miss{background:repeating-linear-gradient(135deg,var(--oops) 0 3px,var(--line) 3px 6px)}
.qsay{min-height:22px;margin-top:4px;font-size:14px;color:var(--mut);font-weight:600}
.q{background:var(--card);border:1.5px solid var(--line);border-radius:22px;padding:18px;box-shadow:var(--sh)}
.q[hidden]{display:none}.q.enter{animation:qin .26s var(--e) both}
.q.st-post{border-color:var(--pf);box-shadow:0 5px 0 var(--pd)}
.qsrc{font:600 12px var(--mono);color:var(--mut);margin:0 0 6px}
.qt:focus-visible,.qres h3:focus-visible{outline:none}.qt{margin:0 0 14px;font-weight:700;font-size:1.08rem;line-height:1.5;max-width:none}
.opts{display:grid;gap:9px}
.opt{display:grid;grid-template-columns:30px minmax(0,1fr) 22px;align-items:center;gap:12px;width:100%;text-align:left;min-height:50px;padding:10px 14px 10px 10px;border:1.5px solid var(--line);background:var(--bg);color:var(--fg);border-radius:16px;font-size:15.5px;line-height:1.4;cursor:pointer;overflow-wrap:anywhere;transition:transform .12s var(--e),border-color .15s,background .15s}
.opt .ol{display:grid;place-items:center;width:30px;height:30px;border-radius:10px;background:var(--pb);color:var(--pt);font:800 13px var(--mono)}
.opt:hover:not(:disabled){border-color:var(--pl)}.opt:active:not(:disabled){transform:scale(.98)}
.opt:disabled{cursor:default;color:var(--fg)}
.opt.good{border-color:var(--ok);background:var(--okbg)}.opt.good .ol{background:var(--ok);color:var(--card)}.opt.good .oi{color:var(--ok)}
.opt.wrong{border-color:var(--oops);border-style:dashed;background:var(--oopsbg)}.opt.wrong .ol{background:var(--oops);color:var(--card)}.opt.wrong .oi{color:var(--oops)}
.why{margin-top:14px;padding:12px 16px;border-radius:16px;font-size:15px;line-height:1.55;background:var(--pb)}.why[hidden]{display:none}
.is-ok .why{background:var(--okbg)}.is-no .why{background:var(--oopsbg)}.why b{margin-right:.3em}
.qnext{display:flex;margin:14px 0 0 auto}.qnext[hidden]{display:none}
.qres{text-align:center;padding:24px 18px 22px;border-radius:26px;border:2px solid var(--pl);background:var(--pb);animation:qin .3s var(--e) both}
.qres[hidden]{display:none}.rb{width:96px;height:96px;margin:0 auto 4px}.rb .bolt-svg{width:100%;height:100%}
.qres h3{margin:4px 0 6px;font-size:1.5rem;letter-spacing:-.01em}
.stars{display:flex;justify-content:center;gap:8px;margin:6px 0}.star{width:48px;height:48px;color:var(--pl)}.star .ic{width:100%;height:100%;stroke-width:1.8}
.star.on{color:var(--pf)}.star.on .ic{stroke:var(--pd)}
.rscore{font:600 18px var(--mono);color:var(--mut)}.rscore b{font-size:30px;color:var(--fg)}
.rline{margin:.6em auto;max-width:34ch;font-weight:600}.rxp{margin:.4em 0 1em;font:700 14px var(--mono);color:var(--pt)}
.ract{display:flex;gap:10px;justify-content:center;flex-wrap:wrap}

/* index: hero + HUD */
.home{max-width:1100px;margin:0 auto}
.hero{display:grid;grid-template-columns:minmax(0,1fr);gap:18px;padding:10px 0 6px}
.hero-copy h1{margin:.1em 0 .3em;font-size:clamp(2.1rem,8vw,3.5rem);line-height:1.05}
.hero-copy>p{font-size:1.12rem;color:var(--mut);max-width:30em;margin:0 0 1em}
.cta{display:flex;flex-wrap:wrap;align-items:center;gap:10px 16px}
.go{display:inline-flex;align-items:center;gap:10px;min-height:56px;padding:0 28px;border-radius:99px;background:var(--pf);color:var(--ink0);font-weight:800;font-size:17px;text-decoration:none;box-shadow:0 5px 0 var(--pd);transition:transform .12s var(--e),box-shadow .12s}
.go:active{transform:translateY(3px);box-shadow:0 2px 0 var(--pd)}
.cta .meta{font-size:14px;color:var(--mut)}
.heroart{position:relative;margin:40px 0 20px;padding:0;border:0;border-radius:28px;background:var(--pb);overflow:visible;box-shadow:var(--sh);counter-increment:none}
.harm{display:block;width:100%;height:auto;border-radius:28px}
.hdot{fill:var(--pl);opacity:.45}.reach{fill:none;stroke:var(--pt);stroke-width:2;stroke-dasharray:3 9;stroke-linecap:round;opacity:.5}
.floor{stroke:var(--fg);stroke-width:3;stroke-linecap:round}.hatch{stroke:var(--fg);stroke-width:2;opacity:.35;stroke-linecap:round}
.frame path{fill:none;stroke:var(--pt);stroke-width:2.5;stroke-linecap:round}.frame .fillink{fill:var(--pt);stroke:none}
.part{fill:var(--card);stroke:var(--fg);stroke-width:3}.link{fill:var(--pf);stroke:var(--fg);stroke-width:3}
.joint{fill:var(--card);stroke:var(--fg);stroke-width:3}.grip{fill:none;stroke:var(--fg);stroke-width:5;stroke-linecap:round;stroke-linejoin:round}
.nut polygon{fill:var(--pf);stroke:var(--fg);stroke-width:3;stroke-linejoin:round}.nut circle{fill:var(--card);stroke:var(--fg);stroke-width:3}
html:not(.gs) .j1{transform-origin:190px 262px;transform:rotate(35deg);animation:j1 7s ease-in-out infinite alternate}
html:not(.gs) .j2{transform-origin:190px 162px;transform:rotate(78deg);animation:j2 5.6s ease-in-out infinite alternate}
html:not(.gs) .j3{transform-origin:190px 62px;transform:rotate(70deg);animation:j3 4.2s ease-in-out infinite alternate}
@keyframes j1{from{transform:rotate(31deg)}to{transform:rotate(38deg)}}@keyframes j2{from{transform:rotate(74deg)}to{transform:rotate(84deg)}}@keyframes j3{from{transform:rotate(64deg)}to{transform:rotate(80deg)}}
.mascot{position:absolute;left:14px;top:-30px;display:flex;align-items:flex-start;gap:8px;max-width:calc(100% - 28px)}
#hbolt{display:block;width:88px;height:88px;flex:none;filter:drop-shadow(0 6px 8px rgb(14 26 31/.2))}#hbolt .bolt-svg{width:100%;height:100%}
.say{margin-top:40px;padding:7px 13px;border-radius:14px 14px 14px 4px;background:var(--card);border:1.5px solid var(--line);font-size:13px;font-weight:700;line-height:1.35;box-shadow:var(--sh)}.say:empty{display:none}
.hud{padding:16px 18px 14px;border-radius:24px;background:var(--card);border:1.5px solid var(--line);box-shadow:var(--sh);font-family:var(--mono)}
.lv{display:flex;align-items:baseline;gap:10px;flex-wrap:wrap}.lvn{padding:3px 10px;border-radius:8px;background:var(--pf);color:var(--ink0);font-weight:800;font-size:13px}.lv b{font:800 18px var(--sans)}.xpm{margin-left:auto;font-size:12px;color:var(--mut)}
.xpbar{height:12px;border-radius:7px;background:var(--line);margin:10px 0 14px;overflow:hidden}.xpbar i{display:block;height:100%;width:0;border-radius:7px;background:var(--pf);transition:width .6s var(--e)}
.tiles{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:8px}
.tile{display:flex;flex-direction:column;align-items:flex-start;gap:0;padding:8px 10px;border-radius:14px;background:var(--bg);min-width:0}
.tile .ic{width:18px;height:18px;color:var(--pt);margin-bottom:2px}.tile b{font-size:20px;line-height:1.2}.tile span{font:600 11px var(--sans);color:var(--mut);line-height:1.3}
.strip{display:flex;gap:2px;margin-top:14px;height:14px}.strip i{flex:1;min-width:0;border-radius:3px;background:var(--pf);opacity:.22;transition:opacity .3s}.strip i.d{opacity:1}
.home-body{display:grid;grid-template-columns:minmax(0,1fr);gap:26px;margin-top:34px}
.side{display:contents}.sync{order:3}.path{order:2}.daily{order:1}
.daily,.sync{border-radius:24px;background:var(--card);border:1.5px solid var(--line);padding:18px;box-shadow:var(--sh);align-self:start}
.daily{border-color:var(--pl)}
.dhead{display:flex;align-items:center;gap:10px}.dhead h3,.sync h3{margin:0;font-size:1.1rem}.dic{display:grid;place-items:center;width:38px;height:38px;border-radius:12px;background:var(--pf);color:var(--ink0)}
.daily p,.sync p{margin:.6em 0;font-size:14.5px;color:var(--mut);line-height:1.55}
.dprog{display:flex;align-items:center;gap:12px;margin:10px 0 14px}.dpips{display:flex;gap:5px}.dpips i{width:22px;height:10px;border-radius:5px;background:var(--line)}.dpips i.on{background:var(--pf)}
#dtoday{font:700 14px var(--mono)}
.daily.playing .dhead,.daily.playing .dsum{display:none}
.srow{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0}.sync textarea{width:100%;font:13px var(--mono);padding:10px 12px;border-radius:14px;border:1.5px solid var(--line);background:var(--bg);color:var(--fg);resize:vertical;word-break:break-all}
.smsg{min-height:1.4em}
.path{padding:6px 0 30px}
.ph{margin:0 0 30px}
.pbanner{display:flex;align-items:center;gap:14px;padding:12px 16px 12px 18px;border-radius:24px;background:var(--pf);color:var(--ink0);margin-right:34px;min-height:76px}
.ph:nth-child(even) .pbanner{margin:0 0 0 34px}
.pnum{font:800 40px/1 var(--mono);letter-spacing:-.04em;opacity:.9}.pname{flex:1;min-width:0;font-weight:800;font-size:1.05rem;line-height:1.25}
.ring{position:relative;flex:none;width:46px;height:46px;border-radius:50%;background:conic-gradient(var(--ink0) var(--p,0%),rgb(14 26 31/.22) 0)}
.ring::after{content:attr(data-t);position:absolute;inset:5px;border-radius:50%;background:var(--pf);display:grid;place-items:center;font:800 11px var(--mono);color:var(--ink0)}
.trail{position:relative;margin-top:10px}
.wire{position:absolute;left:50%;top:0;margin-left:-112px;overflow:visible}.wire path{fill:none;stroke:var(--pl);stroke-width:5;stroke-linecap:round;stroke-dasharray:1 11;opacity:.85}
.node{position:relative;display:grid;place-items:center;height:88px;text-decoration:none;color:var(--fg);-webkit-tap-highlight-color:transparent}
.dot{position:relative;display:grid;place-items:center;width:60px;height:60px;border-radius:50%;transform:translateX(var(--o));background:conic-gradient(var(--pf) var(--p,0%),var(--line) 0);transition:transform .2s var(--e)}
.dot::after{content:"";position:absolute;inset:5px;border-radius:50%;background:var(--card)}
.dot b{position:relative;z-index:1;font:800 17px var(--mono);color:var(--pt)}
.node.done .dot::after{background:var(--pf)}.node.done .dot b{color:var(--ink0)}
.node.done .dot b::before{content:"";position:absolute;left:50%;top:50%;width:26px;height:26px;margin:-13px 0 0 -13px;background:var(--ink0);-webkit-mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='3.200' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m5 12.500 4.500 4.500L19 7.500'/%3E%3C/svg%3E") center/contain no-repeat;mask:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='black' stroke-width='3.200' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='m5 12.500 4.500 4.500L19 7.500'/%3E%3C/svg%3E") center/contain no-repeat}
.node.done .dot b{font-size:0}
.node:not(.done):not(.cur):not(.started) .dot{background:var(--line)}.node:not(.done):not(.cur):not(.started) .dot::after{background:var(--bg)}
.node.cur .dot{width:68px;height:68px;box-shadow:0 0 0 0 var(--pf);animation:ping 2.4s ease-out infinite}.node.cur .dot::after{background:var(--pb)}
.lab{position:absolute;top:50%;translate:0 -50%;font-size:14.5px;font-weight:600;line-height:1.35;overflow-wrap:anywhere}
.node.L .lab{left:0;right:calc(50% - var(--o) + 46px);text-align:right}.node.R .lab{right:0;left:calc(50% + var(--o) + 46px);text-align:left}
.node.cur .lab{font-weight:800}
.node:hover .dot{transform:translateX(var(--o)) scale(1.06)}.node:active .dot{transform:translateX(var(--o)) scale(.96)}
.you{position:absolute;display:none;width:46px;height:46px;pointer-events:none}.you .bolt-svg{width:100%;height:100%}
.node .you{display:block;top:-4px;left:50%;margin-left:calc(var(--o) + 18px);animation:bob 3s ease-in-out infinite}

/* Bolt */
.bolt-svg{display:block;overflow:visible}
.bl-fill{fill:var(--card);stroke:var(--fg);stroke-width:2.5}.bl-line{stroke:var(--fg);stroke-width:2.5;stroke-linecap:round;fill:none}.bl-visor{fill:var(--ink0);stroke:none}
.bl-glow{fill:var(--pf)}.bl-ant{stroke:var(--fg);stroke-width:2}.bl-stroke{fill:none;stroke:var(--pf);stroke-width:2.6;stroke-linecap:round;stroke-linejoin:round}
.bl-drop{fill:oklch(.8 .1 235);stroke:var(--fg);stroke-width:1.6}.m-arms path{fill:none;stroke:var(--fg);stroke-width:2.8;stroke-linecap:round}
.bolt-svg [class*=m-]{display:none}.bolt-svg .m-arms{display:inline}
.bolt-svg[data-mood=idle] .m-idle,.bolt-svg[data-mood=cheer] .m-cheer,.bolt-svg[data-mood=oops] .m-no,.bolt-svg[data-mood=sleepy] .m-sleepy{display:inline}
.bolt-svg[data-mood=sleepy] .m-arms .m-sleepy,.bolt-svg[data-mood=oops] .m-arms .m-no,.bolt-svg[data-mood=idle] .m-arms .m-idle{display:inline}
.bolt-svg[data-mood=sleepy] .bl-ant{fill:var(--line)}.bolt-svg[data-mood=sleepy] .bl-stroke{stroke:var(--mut)}
.bolt-svg[data-mood=cheer]{animation:hop .5s var(--e)}.bolt-svg[data-mood=oops]{animation:wob .5s var(--e)}
.bl-z{stroke:var(--pt)!important}
.bolt-svg[data-mood=sleepy] .bl-z{animation:zz 2.6s ease-in-out infinite}

/* toast + confetti */
#toast{position:fixed;left:50%;top:68px;transform:translate(-50%,-150px);display:flex;gap:8px;align-items:center;background:var(--fg);color:var(--bg);padding:11px 20px;border-radius:99px;font-weight:700;font-size:15px;transition:transform .35s var(--e);z-index:20;max-width:92vw;text-align:center;box-shadow:0 10px 30px -10px rgb(0 0 0/.5)}#toast.on{transform:translate(-50%,0)}
i.pf{position:fixed;width:10px;height:10px;border-radius:2px;pointer-events:none;z-index:30}
.pfl{position:fixed;inset:0;z-index:30;pointer-events:none;overflow:hidden;contain:strict}.pfl i.pf{position:absolute;will-change:transform,opacity}
/* GSAP drives these when it loaded (html.gs): the CSS versions above only run as the fallback */
html.gs #toast{transition:none;transform:none;opacity:0;visibility:hidden}
html.gs .q.enter,html.gs .qres,html.gs .qres .star.on,html.gs .bolt-svg[data-mood=cheer],html.gs .bolt-svg[data-mood=oops]{animation:none}
/* offscreen work is skipped: long code blocks, wide tables, the learning path phases */
pre.hl{content-visibility:auto;contain-intrinsic-block-size:auto var(--ih,240px)}
.ph{content-visibility:auto;contain-intrinsic-block-size:auto var(--ih,900px)}
#upd{position:fixed;left:50%;bottom:calc(16px + env(safe-area-inset-bottom,0px));translate:-50% 0;z-index:25;display:flex;align-items:center;gap:10px;padding:8px 10px 8px 18px;border-radius:99px;background:var(--fg);color:var(--bg);font-weight:700;font-size:14px;box-shadow:0 10px 30px -10px rgb(0 0 0/.5);max-width:calc(100vw - 24px)}
#upd .btn{min-height:38px;padding:0 14px;box-shadow:none}#upd .btn:not(.pri){background:transparent;color:var(--bg);border-color:transparent;padding:0 10px}
#pack progress{width:100%;height:10px;accent-color:var(--pt)}#pack-box .srow{align-items:center}#pack-box .smsg{flex:1;margin:0}
.figmiss{display:grid;place-items:center;width:100%;min-height:120px;padding:16px;border-radius:14px;border:1.5px dashed var(--line);background:var(--pb);color:var(--mut);font-size:14.5px;text-align:center}
#clear-box{margin:6px 0 0;padding:12px 14px;border-radius:16px;background:var(--oopsbg)}#clear-box p{margin:0 0 6px}
/* motion */
@keyframes bob{50%{transform:translateY(-4px) rotate(-3deg)}}@keyframes hop{30%{transform:translateY(-10px) scale(1.06)}60%{transform:translateY(0) scale(.97)}}
@keyframes wob{25%{transform:rotate(-7deg)}60%{transform:rotate(5deg)}}@keyframes zz{50%{transform:translate(2px,-5px);opacity:.4}}
@keyframes qin{from{opacity:0;transform:translateY(10px) scale(.985)}}@keyframes ping{70%,100%{box-shadow:0 0 0 14px transparent}}
@keyframes starpop{0%{transform:scale(.4) rotate(-30deg);opacity:0}60%{transform:scale(1.18) rotate(6deg)}100%{transform:scale(1);opacity:1}}
.qres .star.on{animation:starpop .55s var(--e) both;animation-delay:calc(var(--i)*150ms + 150ms)}
@media (hover:hover) and (pointer:fine){.pn:hover{transform:translateY(-2px);border-color:var(--pl)}.mission:hover{transform:translateY(-1px)}.btn.pri:hover,.go:hover{filter:brightness(1.04)}}
@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important}}

/* wide screens */
@media (min-width:900px){
.hero{grid-template-columns:minmax(0,1.05fr) minmax(0,1fr);gap:26px 40px;align-items:center;padding-top:18px}
.hero-copy{grid-column:1;grid-row:1}.heroart{grid-column:2;grid-row:1 / span 2;margin:0 -28px 0 0}.hud{grid-column:1;grid-row:2;align-self:start}
.home-body{grid-template-columns:minmax(0,1fr) 340px;column-gap:44px;align-items:start}
.side{display:flex;flex-direction:column;gap:22px;grid-column:2;grid-row:1;position:sticky;top:76px}.path{grid-column:1;grid-row:1}.daily,.sync{order:0}
.pbanner{margin-right:90px}.ph:nth-child(even) .pbanner{margin-left:90px}
}
@media (max-width:899px){.layout{grid-template-columns:minmax(0,1fr)}aside{display:none;position:static;height:auto;border-bottom:1px solid var(--line)}.nav aside{display:block}#menu{display:inline-flex}main{padding:18px 16px 64px}aside summary{min-height:48px}aside a{min-height:44px;align-items:center}}
@media (max-width:560px){header{padding:6px 12px;gap:6px}.brand .bt{display:none}.tools{gap:5px}.tools button{padding:0 10px}#xp .hs,#xp .hx{display:none}.pager{grid-template-columns:1fr}.tiles{grid-template-columns:repeat(2,minmax(0,1fr))}
.mascot{left:8px}.heroart{margin-top:42px}.dots{margin-left:0}.opt{font-size:15px}.pn.next{text-align:left}.pn.next small{justify-content:flex-start}}
@media (max-width:420px){main{padding-left:14px;padding-right:14px}.pbanner{margin-right:22px}.ph:nth-child(even) .pbanner{margin-left:22px}.pnum{font-size:34px}}
""" + PYG

JS = r"""
const root=document.documentElement,$=s=>document.querySelector(s),$$=s=>[...document.querySelectorAll(s)];
const LS={get(k){try{return localStorage.getItem(k)}catch(e){return null}},set(k,v){try{localStorage.setItem(k,v)}catch(e){}}};
const saved=LS.get('lang');root.lang=saved||((navigator.language||'').startsWith('ko')?'ko':'en');
const th=LS.get('theme');if(th)root.dataset.theme=th;
const K=()=>root.lang==='ko',t=(en,ko)=>K()?ko:en,calm=()=>matchMedia('(prefers-reduced-motion:reduce)').matches;
const ic=(n,c)=>'<svg class="ic'+(c?' '+c:'')+'" aria-hidden="true"><use href="#i-'+n+'"/></svg>';
const BOLT=/*BOLT*/;const bolt=m=>BOLT.replace('data-mood="idle"','data-mood="'+m+'"');
$('#menu').onclick=()=>{const o=root.classList.toggle('nav');$('#menu').setAttribute('aria-expanded',o)};
$('#lang').onclick=()=>{root.lang=root.lang==='en'?'ko':'en';LS.set('lang',root.lang);quiz();DAILY.again()};
$('#theme').onclick=()=>{const d=root.dataset.theme==='dark'||(!root.dataset.theme&&matchMedia('(prefers-color-scheme:dark)').matches);root.dataset.theme=d?'light':'dark';LS.set('theme',root.dataset.theme)};

/* ---- progress store (localStorage key rfs: xp, q, m, days, badges, rv) ---- */
const LV=[[0,'Loose Bolt','헐거운 볼트'],[60,'Servo','서보'],[180,'Gripper','그리퍼'],[350,'Joint','관절'],[600,'Arm','로봇 팔'],[1000,'Rover','로버'],[1600,'Walker','보행 로봇'],[2500,'Roboticist','로보티시스트'],[4000,'Robot Whisperer','로봇 조련사']];
const day=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
const HUES=[198,262,150,80,35,350];
const PBAD=new Set(['__proto__','constructor','prototype']),LID=/^\d\d-[a-z0-9-]{1,80}$/,DAYRE=/^\d{4}-\d\d-\d\d$/,isObj=v=>v!==null&&typeof v==='object'&&!Array.isArray(v),isInt=(v,a,b)=>typeof v==='number'&&Number.isInteger(v)&&v>=a&&v<=b;
/* canonical progress schema (shared with the CLI): invalid fields are dropped, valid ones kept, unknown keys ignored */
function cleanProg(o){const r={xp:0,q:Object.create(null),m:Object.create(null),days:[],badges:[],rv:Object.create(null)};if(!isObj(o))return r;
if(isInt(o.xp,0,10000000))r.xp=o.xp;
if(isObj(o.q))for(const p of Object.keys(o.q)){if(PBAD.has(p)||!LID.test(p)||!isObj(o.q[p]))continue;const a=o.q[p];for(const i of Object.keys(a)){if(!/^[0-5]$/.test(i)||(a[i]!==0&&a[i]!==1))continue;(r.q[p]=r.q[p]||Object.create(null))[i]=a[i]}}
if(isObj(o.m))for(const p of Object.keys(o.m))if(!PBAD.has(p)&&LID.test(p)&&o.m[p]===1)r.m[p]=1;
if(Array.isArray(o.days)){const u=new Set();for(const d of o.days)if(typeof d==='string'&&DAYRE.test(d))u.add(d);r.days=[...u].sort().slice(-4000)}
if(Array.isArray(o.badges)){const u=new Set();for(const b of o.badges)if(typeof b==='string'&&/^phase\d\d$/.test(b))u.add(b);r.badges=[...u]}
if(isObj(o.rv))for(const d of Object.keys(o.rv))if(!PBAD.has(d)&&DAYRE.test(d)&&isInt(o.rv[d],0,25))r.rv[d]=o.rv[d];
return r}
/* ---- GSAP: loaded with defer, so look it up when needed (html.gs is set at boot). Without it the CSS/WAAPI paths below run. ---- */
const gsOn=()=>!!(window.gsap&&root.classList.contains('gs'));
/* the first painted frame after a click shows the answer; XP, toast and tweens run right after it */
const afterFrame=f=>requestAnimationFrame(()=>setTimeout(f,0));
function react(b,m){if(!b)return;b.dataset.mood=m;if(!gsOn()||calm())return;afterFrame(()=>{const g=window.gsap;if(!g||!b.isConnected)return;
if(m==='cheer')g.fromTo(b,{y:0,scale:1},{keyframes:[{y:-10,scale:1.06,duration:.15},{y:0,scale:.97,duration:.15},{scale:1,duration:.2}],ease:'power2.out',overwrite:true,clearProps:'transform'});
else if(m==='oops')g.fromTo(b,{rotation:0},{keyframes:[{rotation:-7,duration:.12},{rotation:5,duration:.18},{rotation:0,duration:.2}],ease:'power2.out',overwrite:true,clearProps:'transform'})})}
/* ---- UI state: localStorage key rfs-ui (max 20 KB, memory fallback): last lesson, scroll per lesson, quiz round, Daily 5 draw, toy sliders. Nothing personal. ---- */
const UI={KEY:'rfs-ui',CAP:20000,s:null,t:0,
get d(){if(this.s)return this.s;let o=null;try{o=JSON.parse(localStorage.getItem(this.KEY))}catch(e){}return this.s=this.clean(o)},
cq(q,n){n=n||6;if(!isObj(q)||!isInt(q.cur,0,n-1))return null;const a=v=>Array.isArray(v)?v.slice(0,n):[];
return{cur:q.cur,sel:a(q.sel).map(x=>isInt(x,-1,9)?x:null),ok:a(q.ok).map(x=>x===1||x===0?x:null),combo:isInt(q.combo,0,99)?q.combo:0,max:isInt(q.max,0,99)?q.max:0,xp:isInt(q.xp,0,1000)?q.xp:0,res:q.res===1?1:0,practice:q.practice===1?1:0}},
ser(st){return{cur:st.cur,sel:Array.from(st.sel,x=>x===undefined?null:x),ok:Array.from(st.ok,x=>x===undefined?null:+x),combo:st.combo,max:st.max,xp:st.xp,res:+st.res,practice:+st.practice}},
st(q){return Object.assign(freshSt(),{cur:q.cur,sel:q.sel.map(x=>x===null?undefined:x),ok:q.ok.map(x=>x===null?undefined:x===1),combo:q.combo,max:q.max,xp:q.xp,res:q.res===1,practice:q.practice===1,cel:q.res===1})},
clean(o){const r={last:null,sc:{},qz:{},dy:null,ty:{}};if(!isObj(o))return r;
if(typeof o.last==='string'&&LID.test(o.last))r.last=o.last;
if(isObj(o.sc))for(const p of Object.keys(o.sc))if(!PBAD.has(p)&&LID.test(p)&&isInt(o.sc[p],0,1e6))r.sc[p]=o.sc[p];
if(isObj(o.qz))for(const p of Object.keys(o.qz)){if(PBAD.has(p)||!LID.test(p))continue;const q=this.cq(o.qz[p]);if(q)r.qz[p]=q}
if(isObj(o.dy)&&typeof o.dy.d==='string'&&DAYRE.test(o.dy.d)&&Array.isArray(o.dy.items)&&o.dy.items.length<=5){const it=o.dy.items.filter(x=>isObj(x)&&typeof x.pid==='string'&&LID.test(x.pid)&&isInt(x.qi,0,5)).map(x=>({pid:x.pid,qi:x.qi})),q=this.cq(o.dy.st,it.length);if(it.length&&q)r.dy={d:o.dy.d,items:it,st:q}}
if(isObj(o.ty))for(const k of Object.keys(o.ty)){if(PBAD.has(k)||!/^[A-Za-z0-9_-]{1,60}$/.test(k)||!isObj(o.ty[k]))continue;const m={};for(const j of Object.keys(o.ty[k]).slice(0,12))if(/^\d{1,2}$/.test(j)&&typeof o.ty[k][j]==='number'&&isFinite(o.ty[k][j]))m[j]=o.ty[k][j];r.ty[k]=m}
return r},
touched:new Set(),
/* put(fn, keys): keys name what fn changes ('last', 'dy', 'sc:<lesson>', 'qz:<lesson>', 'ty:<toy>'); a flush merges only those into what another tab may have written meanwhile */
put(fn,...keys){fn(this.d);this.dirty=1;for(const k of keys.length?keys:['*'])this.touched.add(k);if(!this.t)this.t=setTimeout(()=>this.flush(),400)},
empty(d){return !d.last&&!d.dy&&!Object.keys(d.sc).length&&!Object.keys(d.qz).length&&!Object.keys(d.ty).length},
flush(){clearTimeout(this.t);this.t=0;let d=this.s;if(!d||!this.dirty)return;this.dirty=0;
if(!this.touched.has('*')){let o=null;try{o=JSON.parse(localStorage.getItem(this.KEY))}catch(e){}const m=this.clean(o);
for(const k of this.touched){const i=k.indexOf(':');if(i<0)m[k]=d[k];else{const a=k.slice(0,i),b=k.slice(i+1);if(d[a][b]===undefined)delete m[a][b];else m[a][b]=d[a][b]}}d=this.s=m}
this.touched.clear();let j=JSON.stringify(d);
for(const k of ['sc','qz','ty']){const ks=Object.keys(d[k]);while(j.length>this.CAP&&ks.length){delete d[k][ks.shift()];j=JSON.stringify(d)}}
if(j.length>this.CAP){d.dy=null;j=JSON.stringify(d)}
try{if(this.empty(d))localStorage.removeItem(this.KEY);else localStorage.setItem(this.KEY,j)}catch(e){}},
wipe(){clearTimeout(this.t);this.t=0;this.dirty=0;this.touched.clear();this.s=this.clean(null);try{localStorage.removeItem(this.KEY)}catch(e){}},
last(pid){this.put(d=>{d.last=pid},'last')},
scroll(pid,y){this.put(d=>{delete d.sc[pid];d.sc[pid]=Math.max(0,Math.min(1e6,Math.round(y)))},'sc:'+pid)}};
function wantRestore(pid){let rs=null,seen=null;try{rs=sessionStorage.getItem('rfs-resume');seen=sessionStorage.getItem('rfs-seen');sessionStorage.removeItem('rfs-resume');sessionStorage.setItem('rfs-seen','1')}catch(e){}
const nav=performance.getEntriesByType('navigation')[0];return !!pid&&(rs===pid||(!seen&&(!nav||nav.type==='navigate')))}
let sct=0;const keepScroll=()=>{if(window.CUR)UI.scroll(window.CUR,scrollY)};
addEventListener('scroll',()=>{if(!sct)sct=setTimeout(()=>{sct=0;keepScroll()},500)},{passive:true});
addEventListener('storage',e=>{if(e.key===UI.KEY&&!UI.t)UI.s=null});  /* another tab wrote: re-read next time */
document.addEventListener('visibilitychange',()=>{if(document.hidden){keepScroll();UI.flush()}});addEventListener('pagehide',()=>{keepScroll();UI.flush()});
document.addEventListener('input',e=>{const x=e.target;if(!x||x.type!=='range')return;const toy=x.closest('.toy[data-toy]');if(!toy)return;const k=toy.dataset.toy,i=[...toy.querySelectorAll('input[type=range]')].indexOf(x);if(i<0)return;UI.put(d=>{(d.ty[k]=d.ty[k]||{})[i]=+x.value},'ty:'+k)},{passive:true});
const RFS={mem:null,ok:true,load(){if(!this.ok&&this.mem)return this.mem;try{return JSON.parse(localStorage.getItem('rfs'))||{}}catch(e){return this.mem||{}}},save(s){this.mem=s;try{localStorage.setItem('rfs',JSON.stringify(s));this.ok=true}catch(e){this.ok=false}},
get s(){return cleanProg(this.load())},
toast(h){const el=$('#toast');if(!el)return;el.innerHTML=h;const g=gsOn()&&window.gsap;
if(!g){el.classList.add('on');clearTimeout(this._t);this._t=setTimeout(()=>el.classList.remove('on'),2600);return}
const y=calm()?0:-24;if(this._tl)this._tl.kill();
this._tl=g.timeline().fromTo(el,{y,autoAlpha:0},{y:0,autoAlpha:1,duration:.3,ease:'power3.out'}).to(el,{y,autoAlpha:0,duration:.22,ease:'power2.out'},'+=2.3')},
level(xp){let i=0;LV.forEach((l,j)=>{if(xp>=l[0])i=j});return i},
streak(s){const set=new Set(s.days);let n=0,d=new Date();if(!set.has(day(d)))d.setDate(d.getDate()-1);while(set.has(day(d))){n++;d.setDate(d.getDate()-1)}return n},
add(n,kind,mut){const s=this.s,before=this.level(s.xp);if(mut)mut(s);s.xp+=n;const td=day(new Date());if(!s.days.includes(td))s.days.push(td);
const after=this.level(s.xp),ko=K();let m=ic('bolt')+'+'+n+' XP';if(after>before)m=ic('star')+(ko?'레벨 업: ':'Level up: ')+LV[after][ko?2:1];
this.checkBadges(s);this.save(s);const lv=after>before;afterFrame(()=>{this.toast(m);this.paint();this.pulse();if(lv)this.burst(48);else if(kind==='m')this.burst(16)});return n},
pulse(){const x=$('#xp');if(!x||calm())return;const g=gsOn()&&window.gsap;if(g)g.fromTo(x,{scale:1.25},{scale:1,duration:.28,ease:'power3.out',overwrite:true,clearProps:'transform'});else x.animate([{transform:'scale(1.25)'},{transform:'scale(1)'}],{duration:260,easing:'cubic-bezier(.23,1,.32,1)'})},
/* confetti with GSAP: pooled <i> elements inside one fixed layer, one timeline per burst, no per-frame DOM work */
burst(n,el){if(calm())return;const g=gsOn()&&window.gsap;if(!g)return this.burstCss(n,el);
const r=el?el.getBoundingClientRect():{left:innerWidth/2,top:innerHeight*.7,width:0,height:0},ox=r.left+r.width/2,oy=r.top+Math.min(r.height/2,innerHeight/2),big=n>60;
let L=this._layer;if(!L){L=this._layer=document.createElement('div');L.className='pfl';L.setAttribute('aria-hidden','true');this._pool=[]}
const els=[],P=this._pool;
for(let i=0;i<n;i++){let e=P.pop();if(!e){e=document.createElement('i');e.className='pf'}
e.style.cssText='left:'+ox+'px;top:'+oy+'px;background:oklch(.72 .17 '+HUES[i%6]+');'+(i%3===0?'border-radius:50%;':i%3===1?'width:6px;height:14px;':'');L.appendChild(e);els.push(e)}
if(!L.isConnected)document.body.appendChild(L);
const tl=g.timeline({onComplete:()=>{els.forEach(e=>e.remove());P.push(...els);if(!L.firstChild)L.remove()}});
els.forEach(e=>{const a=Math.random()*6.2832,v=(big?200:120)+Math.random()*(big?420:240),dx=Math.cos(a)*v,dy=Math.sin(a)*v-(big?160:60),d=.9+Math.random()*.7;
g.set(e,{x:0,y:0,rotation:0,scale:1,autoAlpha:1});
tl.to(e,{keyframes:[{x:dx,y:dy,rotation:Math.random()*720-360,scale:.5,duration:d*.7,ease:'power3.out'},{x:dx*1.1,y:dy+140,rotation:540,scale:.3,autoAlpha:0,duration:d*.3,ease:'power1.in'}]},0)})},
burstCss(n,el){const r=el?el.getBoundingClientRect():{left:innerWidth/2,top:innerHeight*.7,width:0,height:0},ox=r.left+r.width/2,oy=r.top+Math.min(r.height/2,innerHeight/2);
for(let i=0;i<n;i++){const e=document.createElement('i');e.className='pf';e.style.left=ox+'px';e.style.top=oy+'px';e.style.background='oklch(.72 .17 '+HUES[i%6]+')';if(i%3===0)e.style.borderRadius='50%';if(i%3===1)e.style.width='6px',e.style.height='14px';document.body.appendChild(e);
const a=Math.random()*Math.PI*2,v=(n>60?200:120)+Math.random()*(n>60?420:240),dx=Math.cos(a)*v,dy=Math.sin(a)*v-(n>60?160:60);
e.animate([{transform:'translate(0,0) rotate(0) scale(1)',opacity:1},{transform:'translate('+dx+'px,'+dy+'px) rotate('+(Math.random()*720-360)+'deg) scale(.5)',opacity:1,offset:.7},{transform:'translate('+dx*1.1+'px,'+(dy+140)+'px) rotate(540deg) scale(.3)',opacity:0}],{duration:900+Math.random()*700,easing:'cubic-bezier(.23,1,.32,1)'}).onfinish=()=>e.remove()}},
lessonDone(s,pid){const q=s.q[pid]||{};return Object.keys(q).length>=6&&s.m[pid]},
checkBadges(s){for(const ph in window.PH){const b='phase'+ph;if(!s.badges.includes(b)&&window.PH[ph].every(p=>this.lessonDone(s,p))){s.badges.push(b);setTimeout(()=>{this.toast(ic('medal')+(K()?'Phase '+ph+' 배지 획득':'Phase '+ph+' badge earned'));this.burst(60)},2700)}}},
answer(pid,i,ok){const s=this.s;s.q[pid]=s.q[pid]||{};if(s.q[pid][i]!==undefined)return 0;s.q[pid][i]=ok?1:0;this.checkBadges(s);this.save(s);if(ok){this.add(10,'q');return 10}this.paint();return 0},
mission(pid,on){const s=this.s;if(on&&!s.m[pid]){s.m[pid]=1;this.checkBadges(s);this.save(s);this.add(20,'m')}else if(!on&&s.m[pid]){delete s.m[pid];s.xp=Math.max(0,s.xp-20);this.save(s);this.paint()}},
daily(ok){if(!ok)return 0;const d=day(new Date()),used=this.s.rv[d]||0,n=Math.min(5,25-used);if(n<=0)return 0;return this.add(n,'rv',x=>{x.rv[d]=used+n})},
code(){const s=this.s,o={xp:s.xp,q:s.q,m:s.m,days:s.days,badges:s.badges,rv:s.rv},b=new TextEncoder().encode(JSON.stringify(o));let r='';b.forEach(x=>r+=String.fromCharCode(x));return btoa(r).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'')},
merge(code){try{if(typeof code!=='string'||code.length>200000)return null;let c=code.trim().replace(/\s+/g,'');if(!/^[A-Za-z0-9_-]+={0,2}$/.test(c))return null;c=c.replace(/=+$/,'').replace(/-/g,'+').replace(/_/g,'/');while(c.length%4)c+='=';
const raw=JSON.parse(new TextDecoder('utf-8',{fatal:true}).decode(Uint8Array.from(atob(c),x=>x.charCodeAt(0))));if(!isObj(raw))return null;
const o=cleanProg(raw),s=this.s,before=s.xp;s.xp=Math.max(s.xp,o.xp);
for(const p of Object.keys(o.q)){s.q[p]=s.q[p]||Object.create(null);for(const i of Object.keys(o.q[p])){const v=o.q[p][i];s.q[p][i]=s.q[p][i]===undefined?v:Math.max(s.q[p][i],v)}}
for(const p of Object.keys(o.m))s.m[p]=1;
s.days=[...new Set([...s.days,...o.days])].sort();s.badges=[...new Set([...s.badges,...o.badges])];
for(const d of Object.keys(o.rv))s.rv[d]=Math.max(s.rv[d]||0,o.rv[d]);
this.save(s);this.paint();return{xp:s.xp-before}}catch(e){return null}},
nextPid(s){const f=window.ORD,l=UI.d.last;if(l&&f.includes(l)&&!this.lessonDone(s,l))return l;return f.find(p=>!this.lessonDone(s,p))||f[0]},
paint(){const s=this.s,ko=K(),L=this.level(s.xp),nx=LV[L+1],st=this.streak(s),flat=window.ORD,tot=flat.length,td=day(new Date());
const xp=$('#xp');if(xp)xp.innerHTML=ic('bolt')+s.xp+'<span class="hx"> Lv'+(L+1)+'</span><span class="hs">'+ic('flame')+st+'</span>';
$$('[data-pid]').forEach(a=>{const pid=a.dataset.pid;if(a.tagName==='A')a.classList.toggle('done',!!this.lessonDone(s,pid))});
$$('.pc').forEach(c=>{const l=window.PH[c.dataset.ph]||[];c.textContent=l.filter(p=>this.lessonDone(s,p)).length+'/'+l.length});
$$('.ring').forEach(r=>{const l=window.PH[r.dataset.ph]||[],d=l.filter(p=>this.lessonDone(s,p)).length;r.style.setProperty('--p',Math.round(100*d/l.length)+'%');r.dataset.t=d+'/'+l.length});
$$('.dots').forEach(d=>{const q=s.q[d.dataset.pid]||{};[...d.children].forEach((i,k)=>{if(i.classList.contains('dm'))i.className='dm'+(s.m[d.dataset.pid]?' on':'');else i.className='dq'+(q[k]===1?' on':q[k]===0?' miss':'')})});
const done=flat.filter(p=>this.lessonDone(s,p)).length,next=this.nextPid(s);
$$('.node').forEach(n=>{const pid=n.dataset.pid,q=Object.keys(s.q[pid]||{}).length+(s.m[pid]?1:0);n.classList.toggle('started',q>0);n.classList.toggle('cur',pid===next&&done<tot);n.style.setProperty('--p',this.lessonDone(s,pid)?'100%':Math.round(100*q/7)+'%')});
const you=$('#you'),cn=$('.node.cur');if(you&&cn&&you.parentNode!==cn)cn.appendChild(you);else if(you&&!cn&&$('#path')&&you.parentNode!==$('#path'))$('#path').appendChild(you);
const hb=$('#h-xp');if(hb){const set=(id,v)=>{const e=$('#'+id);if(e)e.textContent=v};set('h-xp',s.xp);set('h-st',st);set('h-bd',s.badges.length);set('h-dn',done);set('h-lv','Lv '+(L+1));set('h-lvname',LV[L][ko?2:1]);
set('h-xpm',nx?s.xp+' / '+nx[0]+' XP':s.xp+' XP');$('#h-bar').style.width=(nx?Math.round(100*(s.xp-LV[L][0])/(nx[0]-LV[L][0])):100)+'%';
$$('.strip i').forEach(i=>i.classList.toggle('d',!!this.lessonDone(s,i.dataset.pid)))}
const c=$('#cont');if(c){c.href=window.SINGLE?'#'+next:next+'.html';c.dataset.f=window.FAM[next.slice(0,2)];c.dataset.to=next;c.innerHTML=(done||UI.d.last?(ko?'이어서 하기':'Continue'):(ko?'시작하기':'Start'))+ic('arrow')}
const act=s.days.includes(td),hbolt=$('#hbolt .bolt-svg');if(hbolt&&!this._hold){hbolt.dataset.mood=act?'idle':'sleepy';const say=$('#hsay');if(say)say.textContent=act?(ko?'오늘도 진도를 나갔어요.':'Nice, you moved today.'):(ko?'쿨쿨... 문제 하나로 깨워 주세요.':'Zzz... wake me with one question.')}
const used=s.rv[td]||0,dt=$('#dtoday');if(dt){dt.textContent=used+' / 25 XP';$$('.dpips i').forEach((i,k)=>i.classList.toggle('on',used>=(k+1)*5));const dl=$('#dlabel');if(dl)dl.textContent=used>=25?t('Play for fun','연습으로 풀기'):used>0?t('Play again','다시 하기'):t('Play','시작하기')}
}};
function bindMissions(){$$('.mchk').forEach(x=>{const pid=x.dataset.pid||window.CUR;x.checked=!!RFS.s.m[pid];x.onchange=()=>{$$('.mchk').forEach(y=>{if((y.dataset.pid||window.CUR)===pid)y.checked=x.checked});RFS.mission(pid,x.checked);const b=$('.lesson:not([hidden]) .hookbolt')||$('.hookbolt');if(b&&x.checked){react(b,'cheer');setTimeout(()=>b.dataset.mood='idle',1400)}}})}

/* ---- quiz game: one question at a time; Bolt reacts; cosmetic combo; 1-3 stars; kind to wrong answers ---- */
let QID=0;const freshSt=()=>({sel:[],ok:[],cur:0,combo:0,max:0,xp:0,res:false,cel:false,practice:false});
function Game(box,cfg){
if(box._game)box._game.dispose();let dead=false,pending=null,ct=0;   /* a rebuild (language switch) retires the previous instance: its tweens, timers and callbacks must not touch the shared round */
const st=cfg.st,n=cfg.n,SN={pre:['Warm-up','워밍업'],check:['Checks','체크'],post:['Boss round','보스전'],daily:['Daily 5','오늘의 5문제']};
const SAY={ok:[['Nice one.','좋아요.'],['Got it.','맞았어요.'],['Yes, that is it.','정답입니다.'],['Clean.','깔끔해요.']],no:[['Not this time.','이번에는 아니에요.'],['Close. Read the hint.','아쉬워요. 힌트를 읽어 보세요.'],['Not yet. The right answer is marked.','아직이에요. 맞는 답에 표시가 있어요.']]};
const pickSay=a=>{const x=a[Math.floor(Math.random()*a.length)];return t(x[0],x[1])};
let hud,qs=[],nx,mt;const foc=el=>{if(el)el.focus({preventScroll:true})};
const $h=s=>box.querySelector(s);
const mood=(m,ms)=>{const b=$h('.qbolt .bolt-svg');if(!b)return;react(b,m);clearTimeout(mt);if(ms)mt=setTimeout(()=>{b.dataset.mood='idle'},ms)};
function pips(){const p=$h('.qpips');if(!p)return;[...p.children].forEach((i,k)=>{i.className=st.sel[k]===undefined?(k===st.cur&&!st.res?'cur':''):(st.ok[k]?'ok':'miss')});p.setAttribute('aria-valuenow',st.sel.filter(x=>x!==undefined).length);p.setAttribute('aria-valuemax',n)}
function combo(bump){const c=$h('.qcombo');if(!c)return;c.hidden=st.combo<2;if(st.combo>=2){c.innerHTML=ic('flame')+t('Combo','콤보')+' ×'+st.combo;if(bump&&!calm()){const g=gsOn()&&window.gsap;if(g)afterFrame(()=>c.isConnected&&g.fromTo(c,{scale:1.4},{scale:1,duration:.28,ease:'power3.out',overwrite:true,clearProps:'transform'}));else c.animate([{transform:'scale(1.4)'},{transform:'scale(1)'}],{duration:280,easing:'cubic-bezier(.23,1,.32,1)'})}}}
function mark(i){const d=qs[i],q=cfg.q(i),j=st.sel[i];if(j===undefined)return;
d.querySelectorAll('button.opt').forEach((b,x)=>{b.disabled=true;b.classList.toggle('good',x===q.answer);b.classList.toggle('wrong',x===j&&j!==q.answer);b.querySelector('.oi').innerHTML=x===q.answer?ic('check'):(x===j?ic('x'):'')});
const w=d.querySelector('.why');w.hidden=false;w.innerHTML='<b></b><span></span>';w.firstChild.textContent=st.ok[i]?t('Yes.','맞아요.'):t('Not quite.','아쉬워요.');w.lastChild.textContent=q.explanation||'';d.classList.add(st.ok[i]?'is-ok':'is-no')}
const save=()=>{if(cfg.save)cfg.save(st)};let busy=false;
function enter(d){const g=gsOn()&&window.gsap;if(g){if(!calm())g.fromTo(d,{autoAlpha:0,y:8},{autoAlpha:1,y:0,duration:.22,ease:'power3.out',overwrite:true,clearProps:'transform,opacity,visibility'});return}d.classList.remove('enter');void d.offsetWidth;d.classList.add('enter')}
function show(anim){qs.forEach((d,i)=>{d.hidden=st.res||i!==st.cur;if(anim&&i===st.cur)enter(d)});
const sg=cfg.stage(st.cur);$h('.qstage').textContent=t(SN[sg][0],SN[sg][1]);$h('.qpos').textContent=(st.cur+1)+' / '+n;
nx.hidden=st.res||st.sel[st.cur]===undefined;nx.firstChild.textContent=st.cur<n-1?t('Next','다음'):t('See results','결과 보기');pips()}
function choose(i,j){if(st.sel[i]!==undefined)return;const q=cfg.q(i),ok=j===q.answer;st.sel[i]=j;st.ok[i]=ok;
if(ok){st.combo++;st.max=Math.max(st.max,st.combo)}else st.combo=0;
mark(i);st.xp+=cfg.award(i,ok)||0;combo(true);if(i===st.cur){$h('.qsay').textContent=pickSay(SAY[ok?'ok':'no']);mood(ok?'cheer':'oops',1400);show(false);nx.focus({preventScroll:true})}else pips();save()}
function results(){const ok=st.ok.filter(Boolean).length,stars=ok===n?3:ok>=Math.ceil(n*2/3)?2:1;
const c=document.createElement('div');c.className='qres';
c.innerHTML='<div class="rb">'+bolt(stars===3?'cheer':'idle')+'</div><h3 tabindex="-1"></h3><div class="stars" role="img"></div><div class="rscore"><b>'+ok+'</b> / '+n+'</div><p class="rline"></p><p class="rxp"></p><div class="ract"></div>';
c.querySelector('h3').textContent=stars===3?t('Perfect round','만점 라운드'):t('Round complete','라운드 완료');
const sr=c.querySelector('.stars');sr.setAttribute('aria-label',stars+' / 3');sr.innerHTML=[0,1,2].map(i=>'<span class="star'+(i<stars?' on':'')+'" style="--i:'+i+'">'+ic(i<stars?'star':'star-o')+'</span>').join('');
c.querySelector('.rline').textContent=stars===3?t('No misses. Bolt is doing a victory spin.','틀린 문제가 없습니다. Bolt가 신나서 한 바퀴 돕니다.'):stars===2?t('Good round. Read the hints above once more.','좋은 라운드입니다. 위의 힌트를 한 번 더 읽어 보세요.'):t('Some misses. Each hint above says why.','틀린 문제가 있습니다. 위의 힌트마다 이유가 적혀 있습니다.');
c.querySelector('.rxp').innerHTML=st.xp>0?ic('bolt')+'+'+st.xp+' XP':(cfg.zero?cfg.zero():t('No new XP this round.','이번 라운드는 새 XP가 없습니다.'));
const act=c.querySelector('.ract');act.innerHTML='<button type="button" class="btn" data-act="again">'+ic('refresh')+t('Try again','다시 도전')+'</button>'+(cfg.extra?cfg.extra():'');
act.querySelector('[data-act=again]').onclick=()=>{if(cfg.reset()===true)return;save();render();foc(box.querySelector('.q:not([hidden]) .qt'))};
const cl=act.querySelector('[data-act=close]');if(cl)cl.onclick=()=>cfg.close();
if(!st.cel){st.cel=true;ct=setTimeout(()=>{if(dead)return;if(stars===3)RFS.burst(160,c);else if(stars===2)RFS.burst(34,c)},250)}
const g=gsOn()&&window.gsap;if(g&&!calm()){g.from(c.querySelectorAll('.star.on'),{scale:.4,rotation:-30,autoAlpha:0,duration:.55,ease:'back.out(1.7)',stagger:.15,delay:.15,clearProps:'transform,opacity,visibility'});g.from(c,{autoAlpha:0,y:10,duration:.3,ease:'power3.out',clearProps:'transform,opacity,visibility'})}
return c}
function render(){box.innerHTML='';qs=[];
hud=document.createElement('div');hud.className='qhud';hud.innerHTML='<span class="qbolt">'+bolt(st.res?'cheer':'idle')+'</span><div class="qmeta"><div class="qline"><b class="qstage"></b><span class="qpos"></span><span class="qcombo" hidden></span></div><div class="qpips" role="progressbar" aria-valuemin="0">'+'<i></i>'.repeat(n)+'</div><div class="qsay" aria-live="polite"></div></div>';box.appendChild(hud);
for(let i=0;i<n;i++){const q=cfg.q(i),d=document.createElement('div');d.className='q st-'+cfg.stage(i);const hid='qt'+(++QID)+'-'+i;d.innerHTML=(cfg.src?'<div class="qsrc"></div>':'')+'<div class="qlive" aria-live="polite"><p class="qt" id="'+hid+'" role="heading" aria-level="3" tabindex="-1"></p></div><div class="opts" role="group" aria-labelledby="'+hid+'"></div><div class="why" aria-live="polite" hidden></div>';
if(cfg.src)d.querySelector('.qsrc').textContent=cfg.src(i);d.querySelector('.qt').textContent=q.question;const o=d.querySelector('.opts');
q.options.forEach((txt,j)=>{const b=document.createElement('button');b.type='button';b.className='opt';b.innerHTML='<span class="ol">'+String.fromCharCode(65+j)+'</span><span class="ot"></span><span class="oi"></span>';b.querySelector('.ot').textContent=txt;b.onclick=()=>choose(i,j);o.appendChild(b)});
box.appendChild(d);qs.push(d);mark(i)}
nx=document.createElement('button');nx.type='button';nx.className='btn pri qnext';nx.innerHTML='<span></span>'+ic('arrow');const adv=()=>{if(st.cur<n-1)st.cur++;else st.res=true;save()};
const go=()=>{if(dead)return;const last=st.cur>=n-1;adv();if(!last){show(true);hud.scrollIntoView({block:'nearest'});foc(qs[st.cur].querySelector('.qt'))}else{render();box.scrollIntoView({block:'nearest'});foc(box.querySelector('.qres h3'))}};
nx.onclick=()=>{if(busy)return;const g=gsOn()&&window.gsap,p=qs[st.cur];if(g&&!calm()&&p&&!p.hidden){busy=true;pending=adv;g.to(p,{autoAlpha:0,y:-8,duration:.1,ease:'power2.out',overwrite:true,clearProps:'transform,opacity,visibility',onComplete:()=>{busy=false;pending=null;go()}})}else go()};box.appendChild(nx);
show(false);combo(false);
if(st.res){const r=results();box.appendChild(r)}}
function dispose(){if(dead)return;dead=true;clearTimeout(mt);clearTimeout(ct);const g=window.gsap;if(g)g.killTweensOf([...qs,...box.querySelectorAll('.qres,.star,.qbolt .bolt-svg,.qcombo')]);if(pending){const f=pending;pending=null;f()}}   /* a Next that was already clicked still counts, once */
box._game={dispose};
render()}
const GS={};
/* cache names are namespaced by the registration scope (the service worker uses the same prefix) */
const CNS='rfs:'+new URL('./',location).pathname+':';
/* a round survives a reload: the saved rfs-ui round first, then rfs answers the round does not show (answered question = locked and marked) */
function restoreSt(pid,en){const n=en.length,q=UI.d.qz[pid],st=q?UI.st(q):freshSt();
if(!st.practice){const a=RFS.s.q[pid]||{};for(const k of Object.keys(a)){const i=+k;if(i<n&&st.sel[i]===undefined){st.ok[i]=a[k]===1;st.sel[i]=a[k]===1?en[i].answer:-1}}
if(!q){const f=en.findIndex((_,i)=>st.sel[i]===undefined);st.cur=f<0?n-1:f}}
return st}
function nextLink(pid){const f=window.ORD,i=f.indexOf(pid),nx=f[i+1];if(!nx)return'';return'<a class="btn pri" href="'+(window.SINGLE?'#'+nx:nx+'.html')+'">'+t('Next lesson','다음 레슨')+ic('arrow')+'</a>'}
function quiz(){const box=document.querySelector('.lesson:not([hidden]) #quizbox')||$('#quizbox');if(!box)return;const pid=window.CUR,D=window.QUIZ;if(!pid||!D){if(box._game)box._game.dispose();box.innerHTML='';return}
const en=D.en||D[Object.keys(D)[0]];const st=GS[pid]||(GS[pid]=restoreSt(pid,en));
Game(box,{n:en.length,st,save:s=>UI.put(d=>{d.qz[pid]=UI.ser(s)},'qz:'+pid),q:i=>((D[root.lang]||D.en)[i]||en[i]),stage:i=>en[i].stage||['pre','check','check','check','post','post'][i]||'check',
award:(i,ok)=>st.practice?0:RFS.answer(pid,i,ok),reset:()=>{Object.assign(st,freshSt(),{practice:true})},extra:()=>nextLink(pid),zero:()=>st.practice?t('Practice round: XP is already yours.','연습 라운드입니다. XP는 이미 받았습니다.'):t('No new XP this round.','이번 라운드는 새 XP가 없습니다.')})}
quiz();

/* ---- Daily 5 (index): 5 random questions from started lessons, +5 XP each, max 25 XP per local day, stored as rv[date] ---- */
const DAILY={items:null,st:null,
pool(){const s=RFS.s,Q=window.QUIZS||{},all=Object.keys(Q);let ps=all.filter(p=>Object.keys(s.q[p]||{}).length);if(!ps.length)ps=all;const a=[];ps.forEach(p=>(Q[p].en||[]).forEach((_,i)=>a.push({pid:p,qi:i})));return a},
deal(){const a=this.pool();for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a.slice(0,5)},
resume(){const y=UI.d.dy;if(this.items||!y||!$('#dbox')||y.d!==day(new Date()))return;withQuizzes(()=>{const Q=window.QUIZS;if(this.items||!Q||!y.items.every(x=>Q[x.pid]&&Q[x.pid].en&&Q[x.pid].en[x.qi]))return;this.items=y.items;this.st=UI.st(y.st);$('#daily').classList.add('playing');this.again()})},
start(){if(!window.QUIZS||!$('#dbox'))return;this.items=this.deal();if(!this.items.length)return;this.st=freshSt();UI.put(d=>{d.dy={d:day(new Date()),items:this.items,st:UI.ser(this.st)}},'dy');$('#daily').classList.add('playing');this.again();const h=$('#dbox .q:not([hidden]) .qt');if(h)h.focus({preventScroll:true})},
again(){const items=this.items;if(!items)return;const me=this,Qs=window.QUIZS;
Game($('#dbox'),{n:items.length,st:this.st,save:s=>UI.put(d=>{if(d.dy)d.dy.st=UI.ser(s)},'dy'),q:i=>{const d=Qs[items[i].pid];return (d[root.lang]||d.en)[items[i].qi]||d.en[items[i].qi]},stage:()=>'daily',
src:i=>{const a=document.querySelector('aside a[data-pid="'+items[i].pid+'"]'),sp=a&&a.querySelector('.at [data-lang="'+root.lang+'"]');return a&&sp?a.querySelector('b').textContent+' · '+sp.textContent:items[i].pid},
award:(i,ok)=>RFS.daily(ok),reset:()=>{me.start();return true},extra:()=>'<button type="button" class="btn pri" data-act="close">'+t('Done','완료')+'</button>',close:()=>me.close(),
zero:()=>(RFS.s.rv[day(new Date())]||0)>=25?t('Daily XP cap reached for today. Come back tomorrow.','오늘의 XP 상한에 도달했습니다. 내일 또 오세요.'):t('No new XP this round.','이번 라운드는 새 XP가 없습니다.')})},
close(){UI.put(d=>{d.dy=null},'dy');this.items=null;this.st=null;const d=$('#daily');if(d)d.classList.remove('playing');const b=$('#dbox');if(b){if(b._game)b._game.dispose();b.innerHTML=''}RFS.paint()}};
const dp=$('#dplay');if(dp)dp.onclick=()=>withQuizzes(()=>DAILY.start());

/* ---- progress sync: base64url of the rfs JSON; merge = max xp, union badges/days, per-question max, per-day max rv ---- */
(function(){const panel=$('#sync-panel');if(!panel)return;const ta=$('#sync-ta'),msg=$('#sync-msg'),go=$('#sync-go'),sel=$('#sync-sel');
$('#sync-copy').onclick=async()=>{ta.value=RFS.code();ta.readOnly=true;panel.hidden=false;go.hidden=true;sel.hidden=false;ta.focus();ta.select();let ok=false;try{await navigator.clipboard.writeText(ta.value);ok=true}catch(e){}
msg.textContent=ok?t('Copied. Paste it on your other device.','복사했습니다. 다른 기기에 붙여 넣으세요.'):t('Select the code and copy it.','코드를 선택해서 복사하세요.')};
$('#sync-paste').onclick=()=>{ta.value='';ta.readOnly=false;panel.hidden=false;go.hidden=false;sel.hidden=true;msg.textContent=t('Paste a progress code, then merge.','진행 코드를 붙여 넣고 합치세요.');ta.focus()};
sel.onclick=()=>{ta.focus();ta.select()};
go.onclick=()=>{let r=null;try{r=RFS.merge(ta.value)}catch(e){}msg.textContent=r?t('Merged. Nothing was lowered. +'+r.xp+' XP','합쳤습니다. 낮아진 항목은 없습니다. +'+r.xp+' XP'):t('That code does not look right.','코드가 올바르지 않습니다.')}})();
/* ---- clear local data: rfs-ui and the offline caches. The progress object rfs stays. The confirmation is in the page. ---- */
(function(){const b=$('#sync-clear');if(!b)return;const box=$('#clear-box'),msg=$('#clear-msg');
b.onclick=()=>{box.hidden=!box.hidden;msg.textContent=''};$('#clear-no').onclick=()=>{box.hidden=true;b.focus()};
$('#clear-yes').onclick=async()=>{box.hidden=true;let n=0;try{await window.RFSPACK.cancel()}catch(e){}try{for(const k of await caches.keys())if(k.startsWith(CNS)){await caches.delete(k);n++}}catch(e){}
DAILY.close();UI.wipe();for(const k of Object.keys(GS))delete GS[k];if(window.CUR)quiz();try{sessionStorage.removeItem('rfs-resume')}catch(e){}RFS.paint();
msg.textContent=t('Cleared. Offline caches removed: '+n+'. Your XP and progress are untouched.','지웠습니다. 삭제한 오프라인 캐시는 '+n+'개입니다. XP와 진행 상황은 그대로입니다.')}})();
bindMissions();
$('#lang').addEventListener('click',()=>RFS.paint());RFS.paint();
const co=$('#cont');if(co)co.addEventListener('click',()=>{try{sessionStorage.setItem('rfs-resume',co.dataset.to||'')}catch(e){}});

/* ---- offline: service worker on http(s) only (never file://, never the single-file bundle); a waiting update shows a small reload bar ---- */
(function(){if(!('serviceWorker' in navigator)||!/^https?:$/.test(location.protocol)||(location.protocol==='http:'&&!/^(localhost|127\.0\.0\.1|\[::1\])$/.test(location.hostname)))return;
addEventListener('load',()=>{if(window.SINGLE)return;const mf=document.createElement('link');mf.rel='manifest';mf.href='manifest.webmanifest';document.head.appendChild(mf);navigator.serviceWorker.register('sw.js').then(reg=>{
const ask=w=>{if(!navigator.serviceWorker.controller||$('#upd'))return;const bar=document.createElement('div');bar.id='upd';bar.setAttribute('role','status');
bar.innerHTML='<span></span><button type="button" class="btn pri"></button><button type="button" class="btn" aria-label="dismiss">'+ic('x')+'</button>';
bar.firstChild.textContent=t('Update ready','새 버전이 준비됐습니다');bar.children[1].textContent=t('Reload','새로고침');
bar.children[1].onclick=()=>{navigator.serviceWorker.addEventListener('controllerchange',()=>location.reload(),{once:true});w.postMessage({type:'skip'})};bar.children[2].onclick=()=>bar.remove();document.body.appendChild(bar)};
if(reg.waiting)ask(reg.waiting);
reg.addEventListener('updatefound',()=>{const w=reg.installing;if(w)w.addEventListener('statechange',()=>{if(w.state==='installed')ask(w)})});
navigator.serviceWorker.addEventListener('message',e=>{if(e.data&&e.data.type==='warm-done')window.RFS_WARM=e.data.pages});
navigator.serviceWorker.ready.then(r=>{const idle=window.requestIdleCallback?f=>requestIdleCallback(f,{timeout:6000}):f=>setTimeout(f,3000);idle(()=>r.active&&r.active.postMessage({type:'warm'}))})}).catch(()=>{})})})();

/* ---- figures offline: a figure that cannot load becomes a placeholder box; the next lesson's figures are fetched when idle (not on Save-Data);
   the Offline pack (sync panel) downloads every figure when the reader asks, with progress and cancel, and stops when the device is full ---- */
window.RFSPACK={cancel:()=>Promise.resolve()};
(function(){
const miss=img=>{if(window.SINGLE||img.closest('.figmiss'))return;const w=img.getAttribute('width'),h=img.getAttribute('height'),b=document.createElement('span');b.className='figmiss';b.setAttribute('role','img');b.setAttribute('aria-label',img.alt||'');if(w&&h)b.style.aspectRatio=w+' / '+h;
b._img=img;b._src=img.currentSrc||img.src;b._set=()=>{b.textContent=t('Figure not downloaded yet','그림을 아직 받지 않았습니다')};b._set();img.replaceWith(b)};   /* cache-first: a figure only fails when it is not saved and the network is gone */
document.addEventListener('error',e=>{const x=e.target;if(x&&x.tagName==='IMG'&&x.closest('figure'))miss(x)},true);
addEventListener('online',()=>$$('.figmiss').forEach(b=>{const i=b._img;if(i){i.removeAttribute('src');b.replaceWith(i);i.src=b._src}}));
$('#lang').addEventListener('click',()=>$$('.figmiss').forEach(b=>b._set&&b._set()));
if(!('serviceWorker' in navigator)||!/^https?:$/.test(location.protocol))return;
const post=m=>navigator.serviceWorker.ready.then(r=>r.active&&r.active.postMessage(m));
const manifest=()=>fetch('assets.json').then(r=>r.json());
addEventListener('load',()=>{if(window.SINGLE)return;
const idle=f=>setTimeout(()=>window.requestIdleCallback?requestIdleCallback(f,{timeout:5000}):f(),4000);
idle(()=>{const o=window.ORD||[],i=o.indexOf(window.CUR),nx=i>=0?o[i+1]:null,c=navigator.connection;if(!nx||!navigator.onLine||(c&&c.saveData))return;manifest().then(m=>{const u=(m.lessons[nx]||[]).map(x=>x[0]);if(u.length)post({type:'prefetch',urls:u})}).catch(()=>{})});
const box=$('#pack');if(!box)return;box.hidden=false;
const go=$('#pack-go'),pb=$('#pack-box'),bar=$('#pack-bar'),msg=$('#pack-msg'),cancel=$('#pack-cancel'),mb=n=>(n/1e6).toFixed(1);
const END={incomplete:['',''],done:['All figures are saved for offline use.','모든 그림을 오프라인용으로 저장했습니다.'],cancelled:['Stopped. What was saved stays available offline.','멈췄습니다. 받은 그림은 오프라인에서도 볼 수 있습니다.'],quota:['Stopped: this device has no more room for the site.','멈췄습니다. 이 기기에 저장할 공간이 더 없습니다.'],offline:['Stopped: no connection.','멈췄습니다. 연결이 없습니다.']};
/* one job at a time in the worker. Messages carry the job id; after a start click everything is ignored until the worker says which job that is. */
let cur=0,waiting=false,ack=null,seq=0;
const show=d=>{pb.hidden=false;bar.value=d.total?d.done/d.total:0;msg.textContent=t(d.done+' of '+d.total+' figures, '+mb(d.bytes)+' MB',d.done+' / '+d.total+' 그림, '+mb(d.bytes)+' MB')};
navigator.serviceWorker.addEventListener('message',e=>{const d=e.data;if(!d)return;
if(d.type==='pack-cancel-ack'&&ack&&d.id===ack.id){ack.res();return}
if(d.type==='pack-start'){cur=d.job;waiting=false;go.disabled=true;cancel.hidden=false;pb.hidden=false;delete box.dataset.end;return}
if(waiting||!d.job||d.job!==cur)return;
if(d.type==='pack-progress')show(d);
if(d.type==='pack-end'){bar.value=d.total?d.done/d.total:0;
let m=END[d.reason]||END.done,tx=t(m[0],m[1]);if(d.reason==='incomplete')tx=t(d.failed+' of '+d.total+' figures could not be saved. Saved: '+d.done+'. Try again later.',d.total+'개 중 '+d.failed+'개를 저장하지 못했습니다. 저장됨: '+d.done+'개. 나중에 다시 시도하세요.');
if(d.reason==='done'&&d.done!==d.total)tx=t('Not every figure is saved ('+d.done+' of '+d.total+').','모든 그림이 저장되지는 않았습니다 ('+d.done+' / '+d.total+').');
msg.textContent=tx;go.disabled=false;cancel.hidden=true;box.dataset.end=d.reason;cur=0}});
go.onclick=async()=>{try{const m=await manifest();go.disabled=true;cancel.hidden=false;pb.hidden=false;bar.value=0;msg.textContent=t('Starting','시작합니다');delete box.dataset.end;waiting=true;post({type:'pack',urls:Object.values(m.lessons).flat().map(x=>x[0])})}catch(e){msg.textContent=t('Stopped: no connection.','멈췄습니다. 연결이 없습니다.');pb.hidden=false}};
cancel.onclick=()=>post({type:'pack-cancel',id:++seq});
/* Clear local data calls this first: stop the download and wait for the worker's acknowledgement before any cache is deleted */
window.RFSPACK.cancel=()=>new Promise(res=>{const id=++seq,to=setTimeout(res,6000);ack={id,res:()=>{clearTimeout(to);res()}};post({type:'pack-cancel',id})})});
})();

/* ---- scripts that are not needed to paint: GSAP arrives when the page is idle after load, quizzes.js (Daily 5 only) when it is asked for ---- */
function loadScript(src,id,cb){if(document.getElementById(id)){const e=document.getElementById(id);if(cb)e.addEventListener('load',cb);return}const s=document.createElement('script');s.id=id;s.src=src;if(cb)s.onload=cb;document.head.appendChild(s)}
function withQuizzes(cb){if(window.QUIZS)return cb();loadScript('quizzes.js','quizzes-js',cb)}
addEventListener('load',()=>{if(window.SINGLE||window.gsap)return;const go=()=>loadScript('vendor/gsap.min.js','gsap-js',boot);(document.querySelector('.motion[data-motion]')?go():setTimeout(()=>window.requestIdleCallback?requestIdleCallback(go,{timeout:2500}):go(),2000))});  /* 2 s after load: the first seconds belong to scrolling and tapping; until then the CSS fallbacks run */
/* ---- boot (after the deferred scripts ran): GSAP switch, hero arm, reveals, last lesson, scroll, toy sliders ---- */
let rio=null,rels=[];
function revealClear(){if(rio)rio.disconnect();rio=null;if(rels.length&&window.gsap){gsap.killTweensOf(rels);gsap.set(rels,{clearProps:'transform,opacity,visibility'})}rels=[]}   /* kill AND restore what reveal() set inline */
matchMedia('(prefers-reduced-motion:reduce)').addEventListener('change',e=>{if(e.matches)revealClear()});
/* cards below the fold slide in once; skipped for reduced motion and for automation (screenshots must see the whole page) */
function reveal(){revealClear();const g=window.gsap;if(!g||!gsOn()||calm()||navigator.webdriver)return;const sc=$('.lesson:not([hidden])')||document,list=[...sc.querySelectorAll('.ph,.mission,.pn')];
const below=list.filter(e=>e.getBoundingClientRect().top>innerHeight*.95);if(!below.length)return;rels=below;g.set(below,{autoAlpha:0,y:18});
rio=new IntersectionObserver(es=>es.forEach(en=>{if(!en.isIntersecting)return;rio.unobserve(en.target);g.to(en.target,{autoAlpha:1,y:0,duration:.35,ease:'power3.out',clearProps:'transform,opacity,visibility'})}),{rootMargin:'0px 0px -6% 0px'});below.forEach(e=>rio.observe(e))}
function heroArm(){const g=window.gsap,arm=$('.harm');if(!g||!arm||window.__arm)return;
const J=[['.j1',35,31,38,7,'190 262'],['.j2',78,74,84,5.6,'190 162'],['.j3',70,64,80,4.2,'190 62']];
const mm=window.__arm=g.matchMedia();mm.add({go:'(prefers-reduced-motion: no-preference)',still:'(prefers-reduced-motion: reduce)'},ctx=>{const go=ctx.conditions.go;
J.forEach(([s,rest,a,,,o])=>g.set(s,{rotation:go?a:rest,svgOrigin:o}));if(!go)return;
const tl=g.timeline();J.forEach(([s,,,b,d])=>tl.to(s,{rotation:b,duration:d,ease:'sine.inOut',repeat:-1,yoyo:true},0));
const io=new IntersectionObserver(e=>tl.paused(!e[e.length-1].isIntersecting));io.observe(arm);return()=>io.disconnect()})}
/* scroll to the saved spot now, and once more after load if the layout moved under it and the reader has not scrolled yet */
function restoreScroll(y){scrollTo(0,y);let moved=false;const mv=()=>{moved=true};['wheel','touchstart','keydown','pointerdown'].forEach(e=>addEventListener(e,mv,{once:true,passive:true}));const again=()=>{if(!moved&&Math.abs(scrollY-y)>40)scrollTo(0,y)};addEventListener('load',()=>{again();setTimeout(again,200)},{once:true})}
function boot(){const g=window.gsap;
/* after the first frame: layout is already done, so the hero arm and the reveal reads do not force one inside this task; html.gs flips in the same block as the hero tweens, so the arm never loses its pose */
if(g&&!root.classList.contains('gs'))afterFrame(()=>{heroArm();const tz=$('#toast');if(tz)g.set(tz,{xPercent:-50,autoAlpha:0});root.classList.add('gs');if(window.MOTION&&MOTION.__rehome)MOTION.__rehome();afterFrame(reveal)});   /* tweens first, then the class: the CSS animation keeps the arm moving until then. reveal() reads layout, so it gets its own frame */
const rs=wantRestore(window.CUR);if(window.CUR&&!window.SINGLE){UI.last(window.CUR);const y=UI.d.sc[window.CUR];if(rs&&y>40)restoreScroll(y)}
DAILY.resume()}
window.RFSUI={UI,reveal:()=>afterFrame(reveal),revealClear,wantRestore,boot};
if(document.readyState==='loading')addEventListener('DOMContentLoaded',boot);else boot();
"""

CSS += (ROOT / "scripts" / "motion" / "motion.css").read_text()
JS = JS.replace("/*BOLT*/", json.dumps(bolt_svg("idle")))

if __name__ == "__main__":
    sys.exit(main())
