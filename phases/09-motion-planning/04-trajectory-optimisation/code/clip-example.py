# 레슨 09/04 예시 클립: 핀 둘 사이의 waypoint 하나가 컵 안에서 시작해 당기는 힘(아래)과 미는 힘(위)이 같아질 때까지 올라가고, 탐사 로봇이 그 경로를 따라 간다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
S, FPS, LR, MARGIN = 0.8, 24, 0.04, 0.4                          # 1 lesson unit drawn as 0.8 m (the lead clip draws 0.4 m); a close-up of the middle of the route
CUP = [(np.array([5.0, 0.0]), 1.0)]
X = np.array([[0.0, 0.0], [5.0, 0.2], [10.0, 0.0]])              # pins at (0, 0) and (10, 0); the waypoint starts inside the cup
STEPS, T0, DT, DRIVE, SECONDS, ARROW = 14, 0.6, 0.12, 2.4, 5.7, 0.3   # one gradient step every 0.12 s; arrow length 0.3 m times the square root of the force
hist, pull, push = [X.copy()], [], []
for k in range(STEPS + 1):
    g, gs = m.grad(hist[-1], CUP), m.grad(hist[-1], [])           # total gradient, and the smoothness part alone
    pull.append(float(-gs[1, 1]))                                 # force on the waypoint along y: against the smoothness gradient
    push.append(float(-(g[1, 1] - gs[1, 1])))                     # against the obstacle gradient
    hist.append(hist[-1].copy() if k == STEPS else m.optimise(hist[-1], CUP, iters=1, lr=LR)[0])
w = lambda p, z=0.17: (S * (p[0] - 5), S * p[1], z)         # the chain floats above the cup so the waypoint stays visible
T_END = T0 + STEPS * DT + 0.5
final = hist[STEPS]


def vis(ob, on, off=None):
    for f, hidden in ((1, True), (on, False), (off, True)):
        if f:
            ob.hide_render = hidden
            ob.keyframe_insert("hide_render", frame=f)


def band(P, colour):
    links = [kit.empty("link") for _ in P[1:]]
    bars = [kit.cyl("bar", 0.02, 1.0, (0.5, 0, 0), "x", colour, parent=l, segments=12) for l in links]
    dots = [kit.ball("wp", 0.05 if i == 1 else 0.03, w(p), colour) for i, p in enumerate(P)]
    return links, dots, bars


def lay(links, dots, bars, P, f=None):
    for l, a, b in zip(links, P[:-1], P[1:]):
        d = np.array(w(b)[:2]) - np.array(w(a)[:2])
        kit.key(l, f or 1, loc=w(a), rot=(0, 0, math.atan2(d[1], d[0])))
        l.scale = (float(np.linalg.norm(d)), 1, 1)
        l.keyframe_insert("scale", frame=f or 1)
    for d_, p in zip(dots, P):
        kit.key(d_, f or 1, loc=w(p))


sc = kit.setup(SECONDS)
kit.stripe(-4.6, 4.6, -1.8, 2.4, "pearl")
ring = kit.ghost("grey", 0.35)
kit.cyl("cup", CUP[0][1] * S, 0.12, (*w(CUP[0][0])[:2], 0.06), "z", "dark", bevel=0.01, segments=64)
kit.cyl("margin", (CUP[0][1] + MARGIN) * S, 0.01, (*w(CUP[0][0])[:2], 0.006), "z", ring, segments=64)
for p in ((0, 0), (10, 0)):
    kit.cyl("pin", 0.05, 0.34, (*w(p)[:2], 0.17), "z", "amber", segments=16)
blue = band(hist[0], "blue")
for f in range(sc.frame_start, sc.frame_end + 1):
    k = min(max(int(((f - 1) / FPS - T0) / DT) + 1, 0), STEPS) if (f - 1) / FPS >= T0 else 0
    lay(*blue, hist[k], f)
for ob in blue[1] + blue[2]:
    vis(ob, 1, int(T_END * FPS) + 1)
green = band(final, "green")
lay(*green, final)
for ob in green[1] + green[2]:
    vis(ob, int(T_END * FPS) + 1)

pu, po = kit.arrow("pull", "red", shaft=0.04), kit.arrow("push", "red", shaft=0.04)
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / FPS
    k = min(max(int((t - T0) / DT) + 1, 0), STEPS) if t >= T0 else 0
    p = hist[k][1]
    on = t < T_END
    for ob, force, sgn, dx in ((pu, pull[k], -1.0, -0.12), (po, push[k], 1.0, 0.12)):
        n = max(ARROW * math.sqrt(abs(force)), 1e-3)
        kit.key(ob, f, loc=(w(p)[0] + dx, w(p)[1], 0.22 if on else -1.0), rot=(0, 0, sgn * math.pi / 2))
        ob.scale = (n, min(1.0, n / 0.15), min(1.0, n / 0.15))
        ob.keyframe_insert("scale", frame=f)

rover, wheels = kit.rover("rover", "green")
rover.scale = (0.95, 0.95, 0.95)
P = np.array([w(p)[:2] for p in final])
cum = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
s_max = float(np.interp(w((6.9, 0))[0], P[:, 0], cum))   # the rover stops in frame, a little past the cup
yaw = 0.0
for f in range(sc.frame_start, sc.frame_end + 1):
    s = float(np.clip(((f - 1) / FPS - T_END - 0.2) / DRIVE, 0, 1)) * s_max
    j = min(int(np.searchsorted(cum, s, side="right")) - 1, len(P) - 2)
    d = P[j + 1] - P[j]
    pos = P[j] + (s - cum[j]) / np.linalg.norm(d) * d
    yaw += max(-0.2, min(0.2, (math.atan2(d[1], d[0]) - yaw + math.pi) % (2 * math.pi) - math.pi))
    kit.key(rover, f, loc=(pos[0], pos[1], 0), rot=(0, 0, yaw))
    for wh in wheels:
        kit.key(wh, f, rot=(0, s / 0.07125, 0))
kit.camera((0, -0.7, 4.7), (0, 0.35, 0), lens=38)
kit.render(__file__)
