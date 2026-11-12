# Wave 2의 3D scene을 수업 계산과 대조하고 등록 및 backup 동기화를 검사한다.
import importlib.util
import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

ROOT = Path(__file__).resolve().parents[2]
SCENES = [
    ("00", "03", "urdf-tree-3d"),
    ("04", "01", "gearbox-shafts-3d"),
    ("04", "03", "encoder-disc-3d"),
    ("05", "06", "timestamp-frames-3d"),
    ("12", "02", "timestep-pendulums-3d"),
    ("13", "05", "value-bars-3d"),
    ("16", "01", "pick-place-arm-3d"),
    ("16", "02", "navigation-floor-3d"),
]


def lesson(phase, number):
    return next((ROOT / "phases").glob(f"{phase}-*/{number}-*"))


def source(phase, number):
    path = lesson(phase, number) / "code/main.py"
    spec = importlib.util.spec_from_file_location(f"wave2_{phase}_{number}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def node(expression):
    script = """
const fs = require('fs'), vm = require('vm');
global.window = { MOTION: {} };
vm.runInThisContext(fs.readFileSync('scripts/motion3d/00-engine.js', 'utf8'));
const scenes = {};
window.MOTION.three = (name, spec, frame) => { scenes[name] = {spec, frame}; };
for (const p of ['00','04','05','12','13','16'])
  vm.runInThisContext(fs.readFileSync(`scripts/motion3d/p${p}.js`, 'utf8'));
const model = name => scenes[name].spec.model;
""" + "\nconsole.log(JSON.stringify(" + expression + "));"
    result = subprocess.run(["node", "-e", script], cwd=ROOT, text=True,
                            capture_output=True, check=True)
    return json.loads(result.stdout)


@pytest.mark.parametrize("phase,number,name", SCENES)
def test_registration_and_backup(phase, number, name):
    folder = lesson(phase, number)
    backup = ROOT / ".board/humanize-backup" / folder.relative_to(ROOT) / "fun.json"
    live = json.loads((folder / "fun.json").read_text())
    saved = json.loads(backup.read_text())
    assert live["three"] == saved["three"] == name
    for key in ("toy", "motion", "three"):
        assert live.get(key) == saved.get(key)
    info = node(f"scenes[{json.dumps(name)}].spec")
    assert info["en"] and info["ko"]
    assert len(info["cap"]) == 2 and all(info["cap"])
    assert 0 < info["rest"] < info["period"]
    assert info["controls"]
    assert (ROOT / f"scripts/motion3d/p{phase}.js").stat().st_size < 20_000


@pytest.mark.parametrize("q", [(0., 0.), (.6, -.4), (-3., 1.)])
def test_urdf_parent_origins(q):
    m = source("00", "03")
    links, joints = m.parse_urdf(m.URDF)
    actual = node(f"model('urdf-tree-3d')({q[0]}, {q[1]})")
    assert len(actual["positions"]) == len(links) == 5
    for tip in ("hand", "camera"):
        ch = m.chain(joints, "base", tip)
        angles = dict(zip(("shoulder", "elbow"), q))
        expected = m.link_positions(ch, angles)
        for link, point in expected.items():
            np.testing.assert_allclose(actual["positions"][link], point, atol=1e-12)
        rotation = np.eye(3)
        for joint in ch:
            roll, pitch, yaw = joint["rpy"]
            rotation = rotation @ m._rot(np.array([0, 0, 1.]), yaw) @ m._rot(np.array([0, 1., 0]), pitch) @ m._rot(np.array([1., 0, 0]), roll)
            if joint["axis"] is not None:
                rotation = rotation @ m._rot(joint["axis"], angles[joint["name"]])
            np.testing.assert_allclose(actual["rotations"][joint["child"]], rotation, atol=1e-12)
    np.testing.assert_allclose(actual["axes"]["shoulder"], [0, 0, 1])
    np.testing.assert_allclose(actual["axes"]["elbow"], [0, 0, 1])


@pytest.mark.parametrize("ratio", [1, 10, 100])
def test_gear_reflection(ratio):
    m = source("04", "01")
    actual = node(f"model('gearbox-shafts-3d')({ratio})")
    speed = m.no_load_speed(.05, 1., 24.) / 2
    torque = m.motor_torque(speed, .05, 1., 24.)
    tau, omega = m.gear_output(torque, speed, ratio)
    assert actual["tau"] == pytest.approx(tau)
    assert actual["omega"] == pytest.approx(omega)
    assert actual["reflected"] == pytest.approx(m.load_at_motor(.002, ratio))
    assert actual["rotorOutput"] == pytest.approx(m.rotor_at_output(.00002, ratio))
    assert actual["sensitivity"] == pytest.approx(m.inertia_sensitivity(.00002, .002, ratio))
    assert tau * omega == pytest.approx(torque * speed)  # ideal gearbox conserves power


def test_urdf_draws_every_origin_and_frame_axis():
    actual = node("""(() => {
      const {frame, spec} = scenes['urdf-tree-3d'], arrows = [], dots = [];
      const s = new Proxy({v: {shoulder: .6, elbow: -.4},
        arrow(a,b,c) { arrows.push({a,b,c}); }, dot(p) { dots.push(p); }},
        {get(o,k) { return k in o ? o[k] : () => {}; }});
      frame(s, spec.rest, {t: (en,ko) => en});
      return {arrows, dots, pose: spec.model(.6, -.4)};
    })()""")
    assert len(actual["arrows"]) == 14  # four joint frames, plus two revolute axes
    assert len(actual["dots"]) == 4
    cursor = 0
    for i, (name, link, movable) in enumerate([
            ("shoulder", "upper", True), ("elbow", "fore", True),
            ("wrist", "hand", False), ("cam_mount", "camera", False)]):
        origin = np.array(actual["pose"]["positions"][link])
        np.testing.assert_allclose(actual["dots"][i], origin)
        rotation = np.array(actual["pose"]["rotations"][link])
        for axis in range(3):
            arrow = actual["arrows"][cursor]
            np.testing.assert_allclose(arrow["a"], origin)
            direction = np.subtract(arrow["b"], arrow["a"])
            np.testing.assert_allclose(direction / np.linalg.norm(direction), rotation[:, axis], atol=1e-12)
            cursor += 1
        if movable:
            arrow = actual["arrows"][cursor]
            direction = np.subtract(arrow["b"], arrow["a"])
            np.testing.assert_allclose(arrow["a"], origin)
            np.testing.assert_allclose(direction / np.linalg.norm(direction), actual["pose"]["axes"][name])
            cursor += 1


@pytest.mark.parametrize("cpr", [4, 16, 64])
def test_encoder_uses_floor(cpr):
    m = source("04", "03")
    angles = [-.1, 0., .7, np.pi, 2 * np.pi]
    actual = node(f"{angles}.map(a => model('encoder-disc-3d')(a, {cpr}))")
    expected_counts = m.counts(angles, cpr)
    np.testing.assert_array_equal([x["count"] for x in actual], expected_counts)
    np.testing.assert_allclose([x["measured"] for x in actual], m.angle_from_counts(expected_counts, cpr))
    for angle, item in zip(angles, actual):
        assert -1e-12 <= angle - item["measured"] < 2 * np.pi / cpr + 1e-12


@pytest.mark.parametrize("stamp", [0., .25, .5, 1.])
def test_timestamp_lookup(stamp):
    m = source("05", "06")
    buf = m.PoseBuffer()
    for t in (0., 1.):
        buf.add(t, [2 * t, 0, 0], [np.cos(t / 2), 0, 0, np.sin(t / 2)])
    actual = node(f"model('timestamp-frames-3d')({stamp})")
    correct = m.to_world(buf, [stamp], [[1, 0, 0]])[0]
    latest = m.to_world(buf, [stamp], [[1, 0, 0]], use_stamps=False)[0]
    np.testing.assert_allclose(actual["point"], correct, atol=1e-12)
    np.testing.assert_allclose(actual["latest"], latest, atol=1e-12)
    assert actual["error"] == pytest.approx(np.linalg.norm(correct - latest))


@pytest.mark.parametrize("dt", [.005, .05, .2])
def test_pendulum_integrators(dt):
    m = source("12", "02")
    actual = node(f"model('timestep-pendulums-3d')({dt})")
    for method in ("euler", "semi"):
        trace = actual[method]
        assert len(trace) == round(10 / dt) + 1
        q, w = 1., 0.
        for state in trace[1:]:
            q, w = m.step(method, q, w, lambda x: -m.K_GRAV / m.J * np.sin(x), dt)
            np.testing.assert_allclose([state["q"], state["w"]], [q, w], atol=1e-10)
        assert trace[-1]["worst"] == pytest.approx(m.pendulum_drift(method, dt), abs=1e-10)


def test_value_sweeps_and_policy_match_lesson():
    m = source("13", "05")
    grid = m.gridworld(["......G", ".##.##.", "...X...", ".#.##..", "......."], slip=.2)
    _, hist, sweeps = m.value_iteration(grid, .9)
    for k in (0, 1, 4, 10, sweeps):
        actual = node(f"model('value-bars-3d')({k})")
        np.testing.assert_allclose(actual["values"], hist[k], atol=1e-12)
        np.testing.assert_array_equal(actual["policy"], m.greedy(grid, hist[k], .9))
        assert actual["sweeps"] == sweeps
        assert actual["values"][grid.idx[(0, 6)]] == 0  # terminal value; reward paid on entry
        assert actual["values"][grid.idx[(2, 3)]] == 0


@pytest.mark.parametrize("t", [0., 1., 1.5, 2., 3., 3.5, 4., 5., 5.5])
def test_arm_ik_and_quintic_waypoints(t):
    m = source("16", "01")
    a, b = (.5, .1), (.15, .5)
    pts = [(.4, .4), (.5, .2), a, (.5, .2), (.15, .6), b]
    ref = m.reference([m.ik(p) for p in pts], 1.)
    q = ref(t)[0]
    actual = node(f"model('pick-place-arm-3d')({t})")
    np.testing.assert_allclose(actual["q"], q, atol=1e-12)
    np.testing.assert_allclose(actual["tip"], m.fk(q), atol=1e-12)
    expected_object = a if t < 2 else m.fk(q) if t < 5 else b
    np.testing.assert_allclose(actual["object"], expected_object, atol=1e-12)


def test_navigation_uses_capstone_planner_data():
    m = source("16", "02")
    _, path = m.plan(m.inflate(m.make_world()), (1.5, 1.5), (9., 8.5))
    actual = node("scenes['navigation-floor-3d'].spec.data")
    np.testing.assert_allclose(actual["path"], path, atol=1e-12)
    assert actual["resolution"] == m.RES == .25
    assert actual["cells"] == m.N == 40
    assert actual["radius"] == .4
    # The six drawn solids must cover exactly the lesson's occupied cells.
    drawn = np.zeros((m.N, m.N), dtype=bool)
    for row in range(m.N):
        for col in range(m.N):
            x, y = m.to_xy((row, col))
            drawn[row, col] = any(abs(x - centre[0]) < half[0] and abs(y - centre[1]) < half[1]
                                  for centre, half in actual["walls"])
    np.testing.assert_array_equal(drawn, m.make_world())
    expected_length = sum(np.linalg.norm(b - a) for a, b in zip(path, path[1:]))
    halfway = node("model('navigation-floor-3d')(.5)")
    assert halfway["length"] == pytest.approx(expected_length)
    assert halfway["distance"] == pytest.approx(expected_length / 2)
    for a, b in zip(path, path[1:]):
        assert m.line_free(m.inflate(m.make_world()), a, b)
    # The source's discrete inflation is not a continuous-radius clearance guarantee.
    clearance = path[1][1] - 28 * m.RES
    assert clearance == pytest.approx(.375)
    assert actual["radius"] - clearance == pytest.approx(.025)
    for u, expected in ((0, path[0]), (1, path[-1])):
        pose = node(f"model('navigation-floor-3d')({u})")
        np.testing.assert_allclose([pose["x"], pose["y"]], expected)


def test_all_frames_controls_extremes_and_rest_are_finite():
    # Exercise the actual draw callbacks without a browser. This is not a visual or frame-time verdict.
    result = node("""(() => {
      const failures = [], counts = {};
      for (const [name, {spec, frame}] of Object.entries(scenes)) {
        let primitives = 0;
        const check = x => {
          if (typeof x === 'number' && !Number.isFinite(x)) throw Error(name + ' non-finite');
          if (Array.isArray(x)) x.forEach(check);
        };
        const s = new Proxy({v: {}}, {get(o, key) {
          if (key in o) return o[key];
          return (...args) => { args.forEach(check); primitives++; };
        }});
        const m = {t: (en, ko) => en};
        for (const t of [0, spec.rest, spec.period - .01]) {
          for (const c of spec.controls) s.v[c.id] = c.auto ? c.auto(t) : c.val;
          for (const lang of ['en', 'ko']) {
            m.t = (en, ko) => lang === 'ko' ? ko : en;
            frame(s, t, m);
          }
        }
        for (const edge of ['min', 'max']) {
          for (const c of spec.controls) s.v[c.id] = c[edge] ?? c.val;
          frame(s, spec.rest, m);
        }
        counts[name] = primitives;
        if (!primitives) failures.push(name);
      }
      return {failures, counts};
    })()""")
    assert result["failures"] == []
    assert len(result["counts"]) == 8


def test_default_orbit_label_anchors_stay_inside_canvas():
    # Coordinate-only guard for the clipped URDF hand label at legal slider limits.
    # Font widths and the 390 px rendered page still require browser screenshots.
    failures = node("""(() => {
      const failures = [], R = window.M3D;
      for (const [name, {spec, frame}] of Object.entries(scenes)) {
        for (const edge of ['rest', 'min', 'max']) {
          const t = spec.rest, W = spec.W || 480, H = spec.H || 300;
          const cam = spec.cam, L = spec.look || [0,0,0], unit = spec.unit || 100;
          const view = R.mm(R.rx(cam.pitch), R.rz(cam.yaw + .22 * Math.sin(2 * Math.PI * t / spec.period)));
          const check = (x, y, text, size) => {
            if (x < 6 || x > W - 6 || y - (size || 16) < 4 || y > H - 6)
              failures.push({name, edge, text, x, y});
          };
          const s = new Proxy({v: {}, text(x,y,str,c,size) { check(x,y,str,size); },
            label(p,str,c,size,align,dx,dy) {
              const q = R.mv(view, p.map((x,i) => x - L[i]));
              const k = unit * cam.dist / (cam.dist + q[1]);
              check(W/2 + k*q[0] + (dx || 0), H/2 + (spec.oy ?? 24) - k*q[2] + (dy || 0), str, size);
            }}, {get(o,k) { return k in o ? o[k] : () => {}; }});
          for (const c of spec.controls)
            s.v[c.id] = edge === 'rest' ? (c.auto ? c.auto(t) : c.val) : (c[edge] ?? c.val);
          frame(s, t, {t: (en,ko) => ko});
        }
      }
      return failures;
    })()""")
    assert failures == []
