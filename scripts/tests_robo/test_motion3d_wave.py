# 새 3D 장면의 등록, lesson 수식, 결정적 rest frame을 브라우저 없이 검증한다.
import json
import math
from pathlib import Path
import runpy
import subprocess

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[2]
SCENES = [
    ("02", "01-dh-vs-urdf-origins", "dh-origins-3d"),
    ("02", "04-singularities", "singular-reach-3d"),
    ("03", "02-gravity-compensation", "gravity-torque-3d"),
    ("08", "01-differential-drive-and-odometry", "odometry-drift-3d"),
    ("09", "02-rrt", "rrt-volume-3d"),
    ("10", "01-inverted-pendulum-and-zmp", "lipm-support-3d"),
    ("10", "03-quadrotor-model", "quad-differential-3d"),
    ("14", "02-consensus", "consensus-average-3d"),
]


def lesson(phase, slug):
    return next((ROOT / "phases").glob(f"{phase}-*/{slug}"))


def source(phase, slug):
    return runpy.run_path(str(lesson(phase, slug) / "code/main.py"))


def frame(name, values=None, time=None, lang="en", moving_turn=False, mutate_sinc=False):
    phase = next(p for p, _, n in SCENES if n == name)
    script = r"""
const fs = require('fs'), vm = require('vm');
const [phase, name, overrides, time, lang, movingTurn, mutateSinc] = JSON.parse(process.argv[1]);
global.window = {MOTION: {}};
vm.runInThisContext(fs.readFileSync('scripts/motion3d/00-engine.js', 'utf8'));
const registry = {};
window.MOTION.three = (name, spec, draw) => registry[name] = {spec, draw};
let code = fs.readFileSync(`scripts/motion3d/p${phase}.js`, 'utf8');
if (movingTurn) {
  // Change only the input command fixture: translation continues on corners.
  // The production arc integrator itself is still executed unchanged.
  const input = 'const v = corner ? 0 : SPEED';
  if (!code.includes(input)) throw Error('Moving-turn input seam changed');
  code = code.replace(input, 'const v = SPEED');
}
if (mutateSinc) code = code.replace('Math.sin(h) / h', '1');
vm.runInThisContext(code);
const {spec, draw} = registry[name], calls = [];
const s = {...window.M3D, W: spec.W || 480, H: spec.H || 300, v: {}};
const t = time === null ? spec.rest : time;
for (const c of spec.controls || []) s.v[c.id] = c.auto ? c.auto(t) : c.val;
Object.assign(s.v, overrides);
for (const k of ['line','path','dot','box','wire','poly','arrow','points','label','text'])
  s[k] = (...args) => calls.push({kind:k, args: JSON.parse(JSON.stringify(args))});
draw(s, t, {t: (en,ko) => lang === 'ko' ? ko : en});
console.log(JSON.stringify({spec, model:s.model, calls, registered:Object.keys(registry)}));
"""
    p = subprocess.run(
        ["node", "-e", script, json.dumps([phase, name, values or {}, time, lang, moving_turn, mutate_sinc])],
        cwd=ROOT, text=True, capture_output=True, check=True,
    )
    return json.loads(p.stdout)


@pytest.mark.parametrize("phase,slug,name", SCENES)
def test_registration_fun_and_bilingual_rest(phase, slug, name):
    js = ROOT / f"scripts/motion3d/p{phase}.js"
    assert js.exists()
    assert js.stat().st_size < 20_000
    path = lesson(phase, slug) / "fun.json"
    assert json.loads(path.read_text())["three"] == name
    for lang in ("en", "ko"):
        f = frame(name, lang=lang)
        assert name in f["registered"]
        assert all(f["spec"][key] for key in ("en", "ko", "cap", "controls"))
        assert len(f["spec"]["cap"]) == 2
        assert any(c["kind"] in ("dot", "box") for c in f["calls"])
        # Every vector actually sent to the engine must be finite; font >= 15
        # in the 480-wide viewBox, including when rendered in Korean.
        for c in f["calls"]:
            if c["kind"] in ("label", "text"):
                idx = 3 if c["kind"] == "label" else 4
                assert c["args"][idx] >= 15
            else:
                def finite(x):
                    if isinstance(x, list):
                        return all(finite(v) for v in x)
                    return x is not None and (not isinstance(x, float) or math.isfinite(x))
                assert finite(c["args"])


@pytest.mark.parametrize("phase,slug,name", SCENES)
def test_local_humanize_backup_key_sync(phase, slug, name):
    backup_root = ROOT / ".board/humanize-backup"
    if not backup_root.exists():
        pytest.skip("Ignored local humanize backups are not shipped in clean checkouts")
    path = lesson(phase, slug) / "fun.json"
    backup = backup_root / path.relative_to(ROOT)
    # A partially missing backup is a failure; skip only when no local guard
    # exists at all. In this working clone every copy must pass.
    assert json.loads(backup.read_text())["three"] == name


@pytest.mark.parametrize("angle", [-90, 0, 45, 90])
def test_dh_intermediate_offset_and_equivalent_fk(angle):
    m = source("02", "01-dh-vs-urdf-origins")
    state = frame("dh-origins-3d", {"q2": angle})["model"]
    # Constructed spatial arm: lesson's .4/.3 links, a quarter-turn twist,
    # .1 axial offset (the conversion test), and a .2 terminal link.
    rows = np.array([[0, 0, 0, 0], [.4, np.pi / 2, .1, 0], [.3, 0, 0, 0]])
    q = [.5, math.radians(angle), .8]
    expected = m["fk_dh"](rows, q, "craig", tool=m["tr"](.2, 0, 0))
    urdf = m["fk_urdf"](m["craig_to_urdf"](rows), q, tool=m["tr"](.2, 0, 0))
    np.testing.assert_allclose(state["tip"], expected[:3, 3], atol=1e-12)
    np.testing.assert_allclose(state["urdfTip"], urdf[:3, 3], atol=1e-12)
    assert state["offset"] == pytest.approx(.1)
    assert state["error"] < 1e-12


@pytest.mark.parametrize("reach", [.65, .8, .899, .9])
def test_jacobian_weak_direction_reaches_rank_one(reach):
    m = source("02", "04-singularities")
    state = frame("singular-reach-3d", {"reach": reach})["model"]
    J = m["jacobian"](state["q"], [.5, .4])
    _, sigma, _ = np.linalg.svd(J)
    assert state["det"] == pytest.approx(np.linalg.det(J), abs=1e-12)
    assert state["sigma"] == pytest.approx(sigma[-1], abs=1e-12)
    assert np.linalg.norm(J.T @ state["weak"]) == pytest.approx(sigma[-1], abs=1e-12)
    np.testing.assert_allclose(state["tip"], [reach, 0, 0], atol=1e-12)
    if reach == .9:
        assert state["sigma"] < 1e-8
        np.testing.assert_allclose(state["weak"], [1, 0], atol=1e-8)


@pytest.mark.parametrize("pose", [-60, 0, 45, 90])
def test_gravity_torque_from_lesson_mass_and_levers(pose):
    m = source("03", "02-gravity-compensation")
    state = frame("gravity-torque-3d", {"pose": pose})["model"]
    expected = m["gravity_torque"](state["q"], 2, 1, .4, .2, .2)
    np.testing.assert_allclose(state["torque"], expected, atol=1e-12)
    if pose == 0:
        np.testing.assert_allclose(expected, [9.81, 1.962], atol=1e-12)


@pytest.mark.parametrize("error", [0, 2, 5])
def test_odometry_exact_arcs_and_track_error(error):
    m = source("08", "01-differential-drive-and-odometry")
    wl, wr = m["square_wheels"](2, .5, .01, .05, .3)
    expected = m["dead_reckon"](wl, wr, .01, .05, .3 * (1 + error / 100))
    state = frame("odometry-drift-3d", {"error": error, "progress": 1})["model"]
    np.testing.assert_allclose(state["truth"], expected[-1], atol=1e-11)
    np.testing.assert_allclose(state["odom"], [0, 0, 2 * np.pi], atol=1e-11)
    assert state["steps"] == len(wl) == 2228
    assert state["gap"] == pytest.approx(np.linalg.norm(expected[-1, :2]), abs=1e-11)


def test_odometry_translating_arc_and_sinc_mutant():
    m = source("08", "01-differential-drive-and-odometry")
    wl, wr = m["square_wheels"](2, .5, .01, .05, .3)
    corner = np.arange(len(wl)) % (400 + 157) >= 400
    wl[corner] += .5 / .05
    wr[corner] += .5 / .05
    expected = m["dead_reckon"](wl, wr, .01, .05, .3 * 1.02)[500]
    values = {"error": 2, "progress": 500 / 2228}
    actual = frame("odometry-drift-3d", values, moving_turn=True)["model"]["truth"]
    np.testing.assert_allclose(actual, expected, atol=1e-11, rtol=0)
    mutant = frame("odometry-drift-3d", values, moving_turn=True, mutate_sinc=True)["model"]["truth"]
    assert np.linalg.norm(np.array(mutant)[:2] - expected[:2]) > 1e-7


def test_rrt_extends_with_lesson_step_and_sphere_segment_check():
    m = source("09", "02-rrt")
    a = frame("rrt-volume-3d", {"growth": 1})["model"]
    b = frame("rrt-volume-3d", {"growth": 1})["model"]
    assert a == b
    nodes, parents = np.array(a["nodes"]), a["parents"]
    assert a["seed"] == 0
    assert a["step"] == .4
    assert len(a["nodes"]) == 138
    assert len(a["path"]) == 46
    assert (nodes >= 0).all() and (nodes <= 10).all()
    assert np.ptp(nodes[:, 2]) > 7  # genuinely volumetric, not a flat tree
    obstacles = [(np.array(c), r) for c, r in a["obstacles"]]
    for i in range(1, len(nodes)):
        assert 0 <= parents[i] < i
        assert np.linalg.norm(nodes[i] - nodes[parents[i]]) <= .4 + 1e-12
        assert m["seg_free"](nodes[i], nodes[parents[i]], obstacles)
    np.testing.assert_allclose(a["path"][0], [1, 1, 1])
    np.testing.assert_allclose(a["path"][-1], [9, 9, 9])


@pytest.mark.parametrize("step", [False, True])
@pytest.mark.parametrize("time", [.05, .1, .3, .6])
def test_lipm_matches_lesson_recovery_and_zmp(step, time):
    m = source("10", "01-inverted-pendulum-and-zmp")
    _, x, v = m["fall_or_recover"](.4, .9, .05, step, T=time)
    state = frame("lipm-support-3d", {"time": time, "step": step})["model"]
    assert state["x"] == pytest.approx(x[-1], abs=1e-9)
    assert state["v"] == pytest.approx(v[-1], abs=1e-9)
    assert state["zmp"] == pytest.approx(m["zmp"](state["x"], state["acc"], .9))
    assert state["capture"] == pytest.approx(m["capture_point"](x[-1], v[-1], .9))
    assert state["tc"] == pytest.approx(math.sqrt(.9 / 9.81))


@pytest.mark.parametrize("sign", [-1, 0, 1])
def test_quad_rotor_geometry_torque_and_full_rk4(sign):
    m = source("10", "03-quadrotor-model")
    arm = math.sqrt(2 * .004 / .5)  # four equal point masses on a plus
    delta = sign * .002 / (2 * arm)
    f = frame("quad-differential-3d", {"delta": delta, "time": 1})["model"]
    _, expected = m["simulate"](np.zeros(6), lambda t, s: (4.905, sign * .002), .5, .004, .001, 1)
    np.testing.assert_allclose(f["state"], expected[-1], atol=1e-11)
    assert f["arm"] == pytest.approx(arm)
    assert sum(f["thrusts"]) == pytest.approx(4.905)
    assert -sum(p[0] * F for p, F in zip(f["rotors"], f["thrusts"])) == pytest.approx(sign * .002)
    assert f["state"][2] == pytest.approx(sign * .25)


@pytest.mark.parametrize("gain", [0, .05, .25])
def test_consensus_each_coordinate_preserves_lesson_average(gain):
    m = source("14", "02-consensus")
    state = frame("consensus-average-3d", {"gain": gain, "steps": 120})["model"]
    x0 = np.array([4., -1., 2., 7., 0., 3., -5., 1.])
    initial = np.column_stack([x0, np.roll(x0, -3), np.roll(x0, -5)])
    expected = np.column_stack([m["run"](x, m["ring"](8), gain, 120)[-1] for x in initial.T])
    np.testing.assert_allclose(state["positions"], expected, atol=1e-12)
    np.testing.assert_allclose(np.mean(state["positions"], axis=0), [1.375] * 3, atol=1e-12)
    if gain == .25:
        assert np.linalg.norm(expected - 1.375) < 1e-7


def projected_points(f, sway=0):
    """Same perspective geometry as the engine, without pretending to render text."""
    spec = f["spec"]
    cam = spec["cam"]
    yaw, pitch = cam["yaw"] + sway, cam["pitch"]
    rz = np.array([[math.cos(yaw), -math.sin(yaw), 0], [math.sin(yaw), math.cos(yaw), 0], [0, 0, 1]])
    rx = np.array([[1, 0, 0], [0, math.cos(pitch), -math.sin(pitch)], [0, math.sin(pitch), math.cos(pitch)]])
    points = []
    for c in f["calls"]:
        a, k = c["args"], c["kind"]
        if k in ("line", "arrow"):
            points.extend(a[:2])
        elif k in ("path", "points", "poly"):
            points.extend(a[0])
        elif k == "dot":
            points.append(a[0])
        elif k in ("box", "wire"):
            for x in (-1, 1):
                for y in (-1, 1):
                    for z in (-1, 1):
                        points.append(np.array(a[0]) + np.array(a[2]) @ (np.array(a[1]) * [x, y, z]))
    q = (rx @ rz @ (np.array(points) - spec.get("look", [0, 0, 0])).T).T
    scale = spec["unit"] * cam["dist"] / (cam["dist"] + q[:, 1])
    return np.column_stack((240 + scale * q[:, 0], spec["H"] / 2 + spec["oy"] - scale * q[:, 2]))


@pytest.mark.parametrize("name,control,values", [
    ("dh-origins-3d", "q2", [-90, 0, 90]),
    ("singular-reach-3d", "reach", [.65, .9]),
    ("gravity-torque-3d", "pose", [-60, 0, 90]),
    ("odometry-drift-3d", "error", [0, 2, 5]),
    ("rrt-volume-3d", "growth", [1]),
    ("lipm-support-3d", "step", [False, True]),
    ("quad-differential-3d", "delta", [-.002 / (2 * math.sqrt(.016)), 0, .002 / (2 * math.sqrt(.016))]),
    ("consensus-average-3d", "gain", [0, .05, .25]),
])
def test_geometry_fits_rest_camera_and_automatic_sway(name, control, values):
    for value in values:
        f = frame(name, {control: value})
        for sway in (-.22, 0, .22):
            xy = projected_points(f, sway)
            assert xy[:, 0].min() >= 12
            assert xy[:, 0].max() <= 468
            assert xy[:, 1].min() >= 76  # three lines of HUD text end at y=64
            assert xy[:, 1].max() <= f["spec"]["H"] - 27  # leave the orbit hint clear


@pytest.mark.parametrize("phase,slug,name", SCENES)
def test_actual_engine_reduced_rest_controls_and_keyboard(phase, slug, name):
    # A Canvas/DOM spy exercises the real engine and scene registration. This
    # checks event wiring and finite drawing, not browser layout or performance.
    script = r"""
const fs = require('fs'), vm = require('vm');
const [phase, name] = JSON.parse(process.argv[1]);
let renders=0, commands=0, loops=0, prevented=0, caption;
const ctx = new Proxy({}, {get(o,k) {return k in o ? o[k] : (...a) => {
  commands++; if(k==='clearRect') renders++;
  if(a.some(x=>typeof x==='number'&&!Number.isFinite(x))) throw Error('nonfinite canvas argument');
};}});
const make = tag => ({tag, style:{}, attrs:{}, events:{}, children:[], clientWidth:360,
  append(...x) {this.children.push(...x);}, appendChild(x) {this.children.push(x);},
  insertBefore(x) {this.children.push(x);}, classList:{add:()=>{}},
  setAttribute(k,v) {this.attrs[k]=v;}, getContext:()=>ctx,
  addEventListener(k,v) {this.events[k]=v;}, setPointerCapture:()=>{}});
global.document={createElement:make}; global.devicePixelRatio=1;
global.getComputedStyle=()=>({color:'rgb(1,2,3)',fontFamily:'sans-serif'});
global.window={MOTION:{}};
vm.runInThisContext(fs.readFileSync('scripts/motion3d/00-engine.js','utf8'));
vm.runInThisContext(fs.readFileSync(`scripts/motion3d/p${phase}.js`,'utf8'));
const el=make('div'), m={t:(en,ko)=>en,reduced:()=>true,onTheme:()=>{},onDispose:()=>{},
  caption:(en,ko)=>caption=[en,ko],loop:(cb,o)=>{loops++;cb(o.rest);}};
window.MOTION[name](el,m);
const canvas=el.children.find(e=>e.tag==='canvas'), before=renders;
for(const key of ['ArrowLeft','ArrowRight','ArrowUp','ArrowDown'])
  canvas.events.keydown({key,preventDefault:()=>prevented++});
const slider=el.children.find(e=>e.tag==='label').children.find(e=>e.tag==='input');
slider.value=slider.min; slider.events.input();
console.log(JSON.stringify({renders,before,prevented,commands,loops,caption,tab:canvas.tabIndex,aria:canvas.attrs['aria-label']}));
"""
    p = subprocess.run(["node", "-e", script, json.dumps([phase, name])], cwd=ROOT, text=True, capture_output=True, check=True)
    state = json.loads(p.stdout)
    assert state["renders"] == state["before"] + 5
    assert state["prevented"] == 4
    assert state["commands"] > 20
    assert state["loops"] == 1
    assert state["tab"] == 0
    assert "arrow keys" in state["aria"]
    assert all(state["caption"])
