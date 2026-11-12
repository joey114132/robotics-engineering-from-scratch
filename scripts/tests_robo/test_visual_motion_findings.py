# 시각 검수 회귀: 위젯의 rest 상태와 표시값을 레슨의 계산 결과와 대조한다.
import json
import math
from pathlib import Path
import runpy
import subprocess

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[2]


def widget_frame(filename, name, lang="en", time=None):
    """Execute the real draw callback; no browser or simulated physics in the test."""
    script = r"""
const fs = require('fs'), vm = require('vm'), elements = [];
const [filename, name, lang, time] = JSON.parse(process.argv[1]);
let draw, rest, caption, replay = 0;
const element = (p, tag, attrs) => {
  const e = {tag, attrs: {...attrs}, textContent: '',
    setAttribute(k,v) {this.attrs[k] = v;}};
  elements.push(e); return e;
};
const K = {
  $: element, A: (e,a) => Object.assign(e.attrs,a),
  CC: (p,cx,cy,r,c) => element(p,'circle',{cx,cy,r,class:c}),
  RR: (p,x,y,width,height,rx,c) => element(p,'rect',{x,y,width,height,rx,class:c}),
  T: (m,p,x,y,en,ko,c,an,sz) => {
    const e = element(p,'text',{x,y,'font-size':sz,class:c,'text-anchor':an});
    e.textContent = m.t(en,ko); return e;
  },
  cl: (x,a=0,b=1) => Math.max(a,Math.min(b,x)),
  S: (t,a,b) => Math.max(0,Math.min(1,(t-a)/(b-a))),
  SN: x => .5-.5*Math.cos(Math.PI*x),
  hd: (x,y,dx,dy) => `M${x} ${y}l${dx} ${dy}`,
  stage: () => ({}), fin: () => {}
};
const tl = new Proxy({}, {get: () => () => tl});
const m = {t: (en,ko) => lang === 'ko' ? ko : en,
  caption: (en,ko) => {caption = m.t(en,ko);}, replayButton: () => replay++,
  timeline: () => tl, onTheme: () => {},
  play: (tl,o) => {draw = o.draw; rest = o.rest;}};
global.gsap = {set: () => {}};
global.window = {MB: K, MOTION: {gs: (n,cb) => {if (n === name) cb({},m);}}};
vm.runInThisContext(fs.readFileSync(filename,'utf8'));
draw(time === null ? rest : time);
console.log(JSON.stringify({rest,caption,replay,elements}));
"""
    result = subprocess.run(
        ["node", "-e", script, json.dumps([filename, name, lang, time])],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )
    return json.loads(result.stdout)


@pytest.mark.parametrize("lang", ["en", "ko"])
def test_gust_rest_shows_the_lesson_disturbance_comparison(lang):
    frame = widget_frame("scripts/motion/p10.js", "gust-integral", lang)
    ts = min(3, max(0, (frame["rest"] - 0.6) * 0.5))
    assert 0.5 <= ts < 1.5, "Rest must show the gust while it is still acting."
    lesson = runpy.run_path(str(ROOT / "phases/10-legged-and-aerial/04-cascaded-attitude-control/code/main.py"))
    controls = [lesson["pd"](0.9, 0.084), lesson["cascade"](0.9 / 0.084, 0.084, 0.5)]
    planes = [e for e in frame["elements"] if e["tag"] == "g" and "transform" in e["attrs"]]
    tilts = [e["textContent"] for e in frame["elements"] if e["tag"] == "text" and e["attrs"].get("y") == 208]
    for ctrl, plane, label in zip(controls, planes, tilts, strict=True):
        _, th, _, _ = lesson["simulate"](ctrl, 0.004, 0.001, 3, lambda t: 0.1 if 0.5 <= t < 1.5 else 0, lambda t: 0)
        deg = math.degrees(th[round(ts * 1000)])
        assert label == f"{deg:.1f}°"
        assert float(plane["attrs"]["transform"].split("rotate(")[1][:-1]) == pytest.approx(3 * deg)
    assert tilts[0] != tilts[1]
    bar = [e for e in frame["elements"] if e["tag"] == "rect" and e["attrs"].get("class") == "k"][-1]
    assert bar["attrs"]["width"] > 100
    assert frame["caption"] and frame["replay"] == 1


@pytest.mark.parametrize("lang", ["en", "ko"])
def test_profile_rest_reports_jerk_from_the_lesson_samples(lang):
    frame = widget_frame("scripts/motion/21-concepts-b.js", "trapezoid-profile", lang)
    lesson = runpy.run_path(str(ROOT / "phases/09-motion-planning/01-trajectory-profiles/code/main.py"))
    t = np.arange(0, 2.001, 0.002)
    accs = [lesson["poly"](lesson["cubic"](0, 1, 2), t)[2],
            lesson["trapezoid"](0, 1, 2, 0.5)(t)[2],
            lesson["poly"](lesson["quintic"](0, 1, 2), t)[2]]
    jerks = [f"{lesson['peak_jerk'](acc, 0.002):.1f}" for acc in accs]
    texts = [e["textContent"] for e in frame["elements"] if e["tag"] == "text"]
    assert ("가속도" if lang == "ko" else "acceleration") in texts
    label = "최대 저크: " if lang == "ko" else "peak jerk: "
    assert label + " / ".join(jerks) in texts
    assert frame["caption"] and frame["replay"] == 1


@pytest.mark.parametrize("lang,expected", [
    ("en", ["10 crossings", "1 crossing", "0 crossings"]),
    ("ko", ["가로지름 10회", "가로지름 1회", "가로지름 0회"]),
])
def test_lookahead_crossing_labels(lang, expected):
    frame = widget_frame("scripts/motion/p08.js", "lookahead-race", lang)
    labels = [e["textContent"] for e in frame["elements"]
              if e["tag"] == "text" and e["attrs"].get("y") in (88, 144, 200)]
    assert labels == expected


@pytest.mark.parametrize("lang", ["en", "ko"])
@pytest.mark.parametrize("time,expected", [
    (4, ["0.2°", "-3.6°"]),
    (4.5, ["0.0°", "-0.5°"]),
    (6.5, ["0.0°", "0.0°"]),
])
def test_gust_tilt_rounding_avoids_negative_zero(lang, time, expected):
    frame = widget_frame("scripts/motion/p10.js", "gust-integral", lang, time)
    tilts = [e["textContent"] for e in frame["elements"]
             if e["tag"] == "text" and e["attrs"].get("y") == 208]
    assert tilts == expected
