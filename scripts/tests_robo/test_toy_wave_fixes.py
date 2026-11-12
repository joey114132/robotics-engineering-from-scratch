# Wave-v2 toy regressions exercise the real JavaScript draw and readout paths.
import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
HARNESS = r"""
const fs = require('fs'), vm = require('vm');
const [file, toy, lang, values] = process.argv.slice(1);
const points = [], arcs = [], poses = [], labels = [], sliders = [];
const g = new Proxy({}, { get(target, key) {
  if (key in target) return target[key];
  if (key === 'clearRect') return () => { points.length = arcs.length = poses.length = labels.length = 0; };
  if (key === 'moveTo' || key === 'lineTo') return (x, y) => points.push([x, y]);
  if (key === 'translate') return (x, y) => poses.push([x, y]);
  if (key === 'arc') return (x, y, r) => arcs.push([x, y, r]);
  if (key === 'fillText') return s => labels.push(s);
  if (key === 'measureText') return s => ({width: s.length * 6});
  return () => {};
}});
const ro = {}, btn = {style: {}, setAttribute() {}}, el = {appendChild() {}};
const ctx = {
  title() {}, onDispose() {}, onRedraw() {}, color: s => s,
  t: (en, ko) => lang === 'ko' ? ko : en,
  canvas(w, h) { return {c: {setAttribute() {}}, g, w, h}; },
  slider(en, ko, lo, hi, step, initial, cb) { sliders.push(cb); },
  readout() { return ro; }
};
global.window = {TOYS: {}};
global.document = {documentElement: {}, createElement: () => btn};
global.MutationObserver = class {observe() {} disconnect() {}};
global.IntersectionObserver = class {observe() {} disconnect() {}};
global.matchMedia = () => ({addEventListener() {}, removeEventListener() {}});
const frames = [];
global.requestAnimationFrame = f => {frames.push(f); return frames.length;};
global.cancelAnimationFrame = () => {};
const flush = () => {while (frames.length) frames.shift()();};
vm.runInThisContext(fs.readFileSync(file, 'utf8'));
window.TOYS[toy](el, ctx); flush();
JSON.parse(values).forEach((v, i) => {if (v !== null) sliders[i](v); flush();});
console.log(JSON.stringify({points, arcs, poses, labels, readout: ro.textContent}));
"""


def draw(file, toy, values=(), lang="en"):
    result = subprocess.run(
        ["node", "-e", HARNESS, str(ROOT / "scripts" / "toys" / file),
         toy, lang, json.dumps(values)], capture_output=True, text=True, check=True,
    )
    return json.loads(result.stdout)


def test_pose_graph_has_three_finite_trajectories():
    result = draw("p08.js", "pose-graph-closure")
    assert len(result["points"]) == 3 * 21
    assert all(x is not None and y is not None for x, y in result["points"])
    assert all(0 <= x <= 320 and 0 <= y <= 278 for x, y in result["points"])


def test_encoder_step_matches_windowed_count_increment():
    result = draw("p04.js", "encoder-window", [1000, 20])
    assert "smallest step 0.077 rad/s" in result["readout"]


@pytest.mark.parametrize("rate", [i / 10 for i in range(31)])
def test_scan_clouds_fit_above_the_legend_at_every_turn_rate(rate):
    result = draw("p05.js", "tf-at-a-time", [rate])
    assert len(result["arcs"]) == 42
    assert all(0 <= x - r and x + r <= 320 and 0 <= y - r and y + r <= 186
               for x, y, r in result["arcs"])
    # Translation records are the two robot-pose centres; leave room for their glyphs.
    assert len(result["poses"]) == 2
    assert all(14 <= x <= 306 and 14 <= y <= 172 for x, y in result["poses"])
