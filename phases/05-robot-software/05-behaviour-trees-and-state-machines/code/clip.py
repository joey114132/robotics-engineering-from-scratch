# 레슨 05/05 클립: fetch 트리의 tick 로그를 그대로 따라 하는 책상 위의 팔. 잡기가 두 번 빗나가고 Retry 가 같은 자리에서 다시 시도한다
import math
import pathlib
import sys

import bpy

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
L, GRIP, TOP, SHO, OPEN, HOLD, SHUT = 0.4, 0.085, 0.4, 0.7, 0.075, 0.045, 0.012   # link length, finger centre, table top, shoulder height, finger gaps
D = {"go object": 0.4, "grasp": 0.85, "go bin": 0.4, "release": 0.6}               # seconds per leaf visit
leaves = [(n, s) for log, _ in m.run(m.fetch_task()[0]) for n, s in log if n in D]  # the lesson's tick log, leaves only
N = {n: sum(x == n for x, _ in leaves) for n in D}
HOV, C, BIN = (0.5, -0.1), (0.5, -0.265), (-0.5, -0.12)                           # arm-frame points: above the crate, the crate, above the bin
OFFS = [(-0.07, 0.03), (0.06, 0.05), (0.0, 0.0)]                                  # where each grasp attempt lands relative to the crate
lerp = lambda a, b, u: tuple(x + (y - x) * u for x, y in zip(a, b))
fr = lambda t: int(round(t * 24)) + 1


def ik(p, side=1):
    """Elbow-up joint angles that put the grip point at p = (x, z) from the shoulder; side=-1 reaches behind the post."""
    w = p
    for _ in range(5):
        a = math.acos(min(1.0, math.hypot(*w) / (2 * L)))
        phi = math.atan2(w[1], w[0]) % (2 * math.pi) if side < 0 else math.atan2(w[1], w[0])
        q = (phi + side * a, -side * 2 * a)
        w = (p[0] - GRIP * math.cos(q[0] + q[1]), p[1] - GRIP * math.sin(q[0] + q[1]))
    return q


fk = lambda q: (L * math.cos(q[0]) + (L + GRIP) * math.cos(q[0] + q[1]), L * math.sin(q[0]) + (L + GRIP) * math.sin(q[0] + q[1]))
sc = kit.setup(sum(D[n] for n, _ in leaves) + 0.5)
kit.table((1.5, 0.7), TOP)
root, joints = kit.arm("arm", (L, L), "blue", 0.3)
root.location = (0, 0, TOP)
fingers = sorted((o for o in bpy.data.objects if o.name.startswith("arm-finger")), key=lambda o: o.location.z)
crate = kit.crate("crate", 0.07, (C[0], 0, SHO + C[1]))
kit.box("bin", (0.22, 0.22, 0.01), (BIN[0], 0, TOP + 0.005), "grey", bevel=0.004)
for sx, sy, dx, dy in ((0.02, 0.22, 0.1, 0), (0.02, 0.22, -0.1, 0), (0.22, 0.02, 0, 0.1), (0.22, 0.02, 0, -0.1)):
    kit.box("bin", (sx, sy, 0.09), (BIN[0] + dx, dy, TOP + 0.045), "grey", bevel=0.004)
st = dict(t=0.0, q=ik((0.2, 0.45)), g=OPEN, c=tuple(crate.location), off=None)


def play(dur, qf, gf=None, cf=None):
    """Key frames from the current time to +dur: qf(u) gives joint angles, gf(u) the finger gap, cf(u) overrides the crate position."""
    f0, f1 = fr(st["t"]), fr(st["t"] + dur)
    for f in range(f0, f1 + 1):
        u = (f - f0) / max(f1 - f0, 1)
        q, g = qf(u), (gf(u) if gf else st["g"])
        x, z = fk(q)
        c = cf(u) if cf else ((x + st["off"][0], 0, SHO + z + st["off"][1]) if st["off"] else st["c"])
        kit.pose(joints, f, q)
        for fg, s in zip(fingers, (-1, 1)):
            kit.key(fg, f, loc=(0.085, 0, s * g))
        kit.key(crate, f, loc=c)
    st.update(t=st["t"] + dur, q=q, g=g, c=c)


kit.pose(joints, 1, st["q"])
seen, tries = {n: 0 for n in D}, 0
for name, status in leaves:
    d, q0, k = D[name], st["q"], seen[name] + 1
    seen[name] = k
    if name in ("go object", "go bin"):   # a RUNNING visit moves part of the way, SUCCESS arrives
        q1 = ik(HOV) if name == "go object" else ik(BIN, -1)
        play(d, lambda u: lerp(q0, q1, ((k - 1) + u) / N[name]) if name == "go object" else lerp(ik(HOV), q1, ((k - 1) + u) / N[name]))
    elif name == "grasp":
        ok, pa = status == m.SUCCESS, (C[0] + OFFS[tries][0], C[1] + OFFS[tries][1])
        tries += 1
        play(0.3 * d, lambda u: ik(lerp(HOV, pa, u)))
        play(0.2 * d, lambda u: st["q"], lambda u: OPEN + ((HOLD if ok else SHUT) - OPEN) * u)
        if ok:
            x, z = fk(st["q"])
            st["off"] = (st["c"][0] - x, st["c"][2] - SHO - z)
        qs, g1 = st["q"], st["g"]
        if not ok:
            play(0.15 * d, lambda u: qs, lambda u: g1 + (OPEN - g1) * u)
        play((0.5 if ok else 0.35) * d, lambda u: ik(lerp(pa, HOV, u)))
    else:   # release: open the fingers, the crate drops into the bin
        qs, c0 = st["q"], st["c"]
        play(0.3 * d, lambda u: qs, lambda u: HOLD + (OPEN - HOLD) * u)
        st["off"] = None
        play(0.7 * d, lambda u: qs, cf=lambda u: (c0[0], 0, c0[2] + (TOP + 0.045 - c0[2]) * u * u))
kit.camera((0, -3.5, 2.5), (0, 0, 0.88), lens=42)
kit.render(__file__)
