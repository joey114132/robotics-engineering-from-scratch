# Wave-v2 motion regression checks execute the scene draw functions with lightweight renderers.
import json
import math
from pathlib import Path
import subprocess

import pytest


ROOT = Path(__file__).resolve().parents[2]


def node(script):
    result = subprocess.run(
        ["node", "-e", script], cwd=ROOT, text=True, capture_output=True, check=True
    )
    return json.loads(result.stdout)


def test_capture_step_draws_the_actual_support_and_initial_capture_point():
    frames = node(r"""
const fs = require('fs'), vm = require('vm'), elements = [];
let draw;
const element = (parent, tag, attrs) => {const e = {tag, attrs: {...attrs}}; elements.push(e); return e;};
const K = {
  $: element, A: (e, attrs) => Object.assign(e.attrs, attrs),
  CC: (p,cx,cy,r,c) => element(p,'circle',{cx,cy,r,class:c}),
  RR: (p,x,y,width,height,rx,c) => element(p,'rect',{x,y,width,height,rx,class:c}),
  cl: (x,a=0,b=1) => Math.max(a,Math.min(b,x)), hd: () => '', fin: () => {},
  T: () => {}, stage: () => ({})
};
const m = {caption:()=>{},replayButton:()=>{},t:(en)=>en,timeline:()=>({}),play:(tl,o)=>{draw=o.draw;}};
global.window = {MB: K, MOTION: {gs: (name, cb) => {if (name === 'capture-step') cb({},m);}}};
vm.runInThisContext(fs.readFileSync('scripts/motion/p10.js','utf8'));
const frame = t => {draw(t); return elements.map(e=>({tag:e.tag,attrs:{...e.attrs}}));};
console.log(JSON.stringify([frame(0),frame(1.4+.1/.45),frame(8)]));
""")
    initial, onset, rest = frames
    initial_cps = [e["attrs"] for e in initial if e["tag"] == "path" and e["attrs"].get("d") == "M0 -9L8 0L0 9L-8 0Z"]
    assert len(initial_cps) == 2
    expected = 36 + 200 * 0.4 * (0.9 / 9.81) ** 0.5
    for cp in initial_cps:
        assert float(cp["transform"].split()[0].split("(")[1]) == pytest.approx(expected)
    for frame in (onset, rest):
        foot = next(e["attrs"] for e in frame if e["tag"] == "rect" and e["attrs"].get("y") == 235 and e["attrs"].get("class") == "k s sk")
        support = next(e["attrs"] for e in frame if e["tag"] == "circle" and e["attrs"].get("cy") == 238 and e["attrs"].get("r") == 5)
        cp = [e["attrs"] for e in frame if e["tag"] == "path" and e["attrs"].get("d") == "M0 -9L8 0L0 9L-8 0Z"][1]
        assert foot["opacity"] == 1
        assert foot["x"] + foot["width"] / 2 == pytest.approx(support["cx"])
        assert float(cp["transform"].split()[0].split("(")[1]) == pytest.approx(support["cx"])
        assert cp["class"] == "k s sk"


@pytest.mark.parametrize("time", [1.1, 2.1, 7.9, 8.9])
def test_rotation_first_turn_label_matches_the_drawn_pose(time):
    result = node("const time = " + json.dumps(time) + ";\n" + r"""
const fs = require('fs'), vm = require('vm');
let draw, pose, labels;
const mm = (a,b) => a.map(row=>b[0].map((_,j)=>row.reduce((s,x,k)=>s+x*b[k][j],0)));
const R = {
  mm, mv:(a,v)=>a.map(row=>row.reduce((s,x,i)=>s+x*v[i],0)),
  rx:a=>[[1,0,0],[0,Math.cos(a),-Math.sin(a)],[0,Math.sin(a),Math.cos(a)]],
  rz:a=>[[Math.cos(a),-Math.sin(a),0],[Math.sin(a),Math.cos(a),0],[0,0,1]],
};
global.window = {M3D:R,MOTION:{three:(name,opts,cb)=>{if(name==='rotation-order-3d')draw=cb;}}};
vm.runInThisContext(fs.readFileSync('scripts/motion3d/p01.js','utf8'));
const s = new Proxy({box:(o,h,r)=>{pose=r;}, text:(x,y,label)=>labels.push(label)}, {get:(o,k)=>o[k]||(()=>{})});
labels=[];
draw(s,time,{t:(en)=>en});
console.log(JSON.stringify({pose,labels}));
""")
    angle = float(result["labels"][1].split("°")[0])
    pose = result["pose"]
    actual = math.degrees(math.acos(max(-1, min(1, (sum(pose[i][i] for i in range(3)) - 1) / 2))))
    assert angle == pytest.approx(actual, abs=0.51)
