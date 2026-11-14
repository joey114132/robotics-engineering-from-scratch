# 레슨 03/07 클립: 토크 없이 자유롭게 움직이는 수평면 팔 둘. 초록 팔은 올바른 Coriolis 항으로 에너지를 지키고, 파란 팔은 부호가 뒤집혀 에너지를 얻는다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import numpy as np

import kit

m = kit.lesson_main(__file__)
P = dict(m1=1.0, m2=1.5, l1=0.5, lc1=0.2, lc2=0.3, I1=0.03, I2=0.05)   # the lesson's figure arm
X0 = np.array([0.3, 1.0, 2.0, -1.0])                                      # start angles and speeds of the lesson's figure
T, DT, SLOW, GAUGE = 3.0, 4e-3, 3.0 / 5.0, 0.5                           # 3 s of free motion played over 5 s; the energy bar is 0.5 m at the start energy


def free_run(h_sign):
    """The loop inside m.energy_drift, keeping every state: tau = 0, RK4, acceleration from m.mass and m.lagrange_tau."""
    def acc(q, qd):
        return np.linalg.solve(m.mass(q, P), -m.lagrange_tau(q, qd, np.zeros(2), P, h_sign))
    f = lambda x: np.concatenate([x[2:], acc(x[:2], x[2:])])
    x, out = X0.copy(), []
    for _ in range(int(T / DT) + 1):
        out.append(x)
        k1 = f(x); k2 = f(x + DT / 2 * k1); k3 = f(x + DT / 2 * k2); k4 = f(x + DT * k3)
        x = x + DT / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
    return out


runs = {"green": free_run(1), "blue": free_run(-1)}
assert abs(m.energy_drift(P, X0[:2], X0[2:], T=T, dt=DT, h_sign=-1) - (m.kinetic(runs["blue"][-1][:2], runs["blue"][-1][2:], P) - m.kinetic(X0[:2], X0[2:], P))) < 1e-9   # same run as the lesson's own


def scara(name, colour):
    """Two links turning about vertical axes (the lesson's arm moves in a horizontal plane). Returns the two joints."""
    root = kit.empty(name)
    j0 = kit.empty(name + "-j0", (0, 0, 0.42), root)
    j1 = kit.empty(name + "-j1", (0.5, 0, 0.07), j0)
    kit.cyl(name + "-post", 0.06, 0.42, (0, 0, 0.21), "z", "grey", parent=root)
    kit.cyl(name + "-m0", 0.075, 0.1, (0, 0, 0), "z", "dark", parent=j0)
    kit.cyl(name + "-m1", 0.06, 0.08, (0, 0, 0), "z", "dark", parent=j1)
    kit.box(name + "-l0", (0.52, 0.07, 0.05), (0.25, 0, 0.035), colour, bevel=0.01, parent=j0)
    kit.box(name + "-l1", (0.52, 0.06, 0.04), (0.25, 0, 0.03), "sky", bevel=0.01, parent=j1)
    kit.ball(name + "-mass", 0.05, (0.3 * 0.52 / 0.5, 0, 0.03), "amber", parent=j1)     # the forearm mass m2 sits at lc2 = 0.3
    return root, j0, j1


sc = kit.setup(5.0)
kit.table((4.8, 2.8), 0.4, (0, 0.1))
e0 = m.kinetic(X0[:2], X0[2:], P)
for c, x in (("blue", -1.3), ("green", 1.3)):
    root, j0, j1 = scara(c, c)
    root.location = (x, 0, 0.4)
    bar = kit.box(c + "-energy", (0.1, 0.1, 1.0), (x, -1.15, 0.9), "amber", bevel=0.01)    # kinetic energy as a bar in front of the arm
    for f in range(sc.frame_start, sc.frame_end + 1):
        s = runs[c][min(int((f - 1) / 24 * SLOW / DT), len(runs[c]) - 1)]
        kit.key(j0, f, rot=(0, 0, s[0]))
        kit.key(j1, f, rot=(0, 0, s[1]))
        h = GAUGE * m.kinetic(s[:2], s[2:], P) / e0
        bar.scale, bar.location = (1, 1, h), (x, -1.15, 0.4 + h / 2)
        for p in ("scale", "location"):
            bar.keyframe_insert(p, frame=f)
kit.camera((0, -4.1, 3.6), (0, -0.1, 0.55), lens=32)
kit.render(__file__)
