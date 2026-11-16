# 레슨 09/04 클립: 들쭉날쭉한 waypoint 경로가 gradient descent 로 컵 두 개를 피해 펴지고, 탐사 로봇이 그 경로를 따라 간다
import math
import pathlib
import sys

import numpy as np
from mathutils import Vector

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
S, FPS, MARGIN, LR = 0.4, 24, 0.4, 0.04                         # 1 lesson unit drawn as 0.4 m
OBS = [(np.array([3.5, 0.3]), 1.0), (np.array([7.0, -0.5]), 1.0)]
X = np.linspace([0.0, 0.0], [10.0, 0.0], 22)
X[1:-1, 1] += np.random.default_rng(0).uniform(-0.15, 0.15, 20)   # the lesson figure's jagged start
HOLD, MORPH, DRIVE, SECONDS = 0.7, 2.6, 2.0, 5.8
frames = list(range(1, int((HOLD + MORPH) * FPS) + 1))
its = np.unique(np.round(np.logspace(0, math.log10(4000), int(MORPH * FPS)))).astype(int)   # iteration count shown at each morph frame (log scale)
snap, done = {}, 0
for f in frames:
    k = its[min(max(f - 1 - int(HOLD * FPS), 0), len(its) - 1)] if f > int(HOLD * FPS) else 0
    if k > done:
        X, _ = m.optimise(X, OBS, iters=int(k - done), lr=LR)    # the lesson's own descent, continued
        done = int(k)
    snap[f] = X.copy()
w = lambda p, z=0.03: (S * (p[0] - 5), S * p[1], z)
final, T_END = snap[frames[-1]], HOLD + MORPH

sc = kit.setup(SECONDS)
kit.stripe(-2.3, 2.3, -1.2, 1.2, "pearl")
for c, r in OBS:
    kit.cyl("cup", r * S, 0.3, (*w(c)[:2], 0.15), "z", "dark", bevel=0.01, segments=64)
    kit.tube("margin", [(w(c)[0] + (r + MARGIN) * S * math.cos(a), w(c)[1] + (r + MARGIN) * S * math.sin(a), 0.012) for a in np.linspace(0, 2 * math.pi, 65)], 0.016, "#5b6a72")   # the margin: a clear ring
kit.cyl("goal", 0.1, 0.01, (*w((10, 0))[:2], 0.01), "z", "amber")
kit.cyl("goal-pole", 0.01, 0.3, (*w((10, 0))[:2], 0.15), "z", "amber")
kit.ball("goal-flag", 0.06, (*w((10, 0))[:2], 0.3), "amber")


def vis(ob, on, off=None):                                       # show from frame `on`, hide from frame `off`
    for f, hidden in ((1, True), (on, False), (off, True)):
        if f:
            ob.hide_render = hidden
            ob.keyframe_insert("hide_render", frame=f)


def band(P, colour):                                            # a chain of round links and joints through the waypoints
    links = [kit.empty("link") for _ in P[1:]]
    bars = [kit.cyl("bar", 0.014, 1.0, (0.5, 0, 0), "x", colour, parent=l, segments=12) for l in links]
    dots = [kit.ball("wp", 0.026, w(p), colour) for p in P]
    return links, dots, bars


def lay(links, dots, bars, P, f=None):
    for i, (l, a, b) in enumerate(zip(links, P[:-1], P[1:])):
        d = np.array(w(b)[:2]) - np.array(w(a)[:2])
        kit.key(l, f or 1, loc=w(a), rot=(0, 0, math.atan2(d[1], d[0])))
        l.scale = (float(np.linalg.norm(d)), 1, 1)
        l.keyframe_insert("scale", frame=f or 1)
    for d_, p in zip(dots, P):
        kit.key(d_, f or 1, loc=w(p))


blue = band(snap[1], "blue")
for f in frames:
    lay(*blue, snap[f], f)
for ob in blue[1] + blue[2]:   # hiding a parent does not hide its children, so hide the bars themselves
    vis(ob, 1, int(T_END * FPS) + 1)
green = band(final, "green")
lay(*green, final)
for ob in green[1] + green[2]:
    vis(ob, int(T_END * FPS) + 1)

rover, wheels = kit.rover("rover", "green")
RV = 0.7                                                         # fits inside the margin ring (0.16 m clear of a cup)
rover.scale = (RV,) * 3
WIDE = ((0, -3.6, 4.6), (0, 0.05, 0), 44)                          # the wide shot, then the camera follows the rover while it drives
cam = kit.camera(WIDE[0], WIDE[1], lens=WIDE[2])
f_drive = int((T_END + 0.2) * FPS)
P = np.array([w(p)[:2] for p in final])
cum = np.concatenate([[0], np.cumsum(np.linalg.norm(np.diff(P, axis=0), axis=1))])
yaw = 0.0
for f in range(sc.frame_start, sc.frame_end + 1):
    s = float(np.clip(((f - 1) / FPS - T_END - 0.2) / DRIVE, 0, 1)) * cum[-1]
    k = min(int(np.searchsorted(cum, s, side="right")) - 1, len(P) - 2)
    d = P[k + 1] - P[k]
    pos = P[k] + (s - cum[k]) / np.linalg.norm(d) * d
    yaw += max(-0.2, min(0.2, (math.atan2(d[1], d[0]) - yaw + math.pi) % (2 * math.pi) - math.pi))   # turn toward the segment, at most 0.2 rad a frame
    kit.key(rover, f, loc=(pos[0], pos[1], 0), rot=(0, 0, yaw))
    u = min(max((f - f_drive + 12) / 12, 0.0), 1.0)                 # ease in to the follow shot just before the drive
    u = u * u * (3 - 2 * u)
    tgt = Vector(WIDE[1]) * (1 - u) + Vector((pos[0], pos[1], 0.1)) * u
    cpos = Vector(WIDE[0]) * (1 - u) + Vector((pos[0], pos[1] - 1.5, 3.3)) * u
    cam.location, cam.data.lens = cpos, WIDE[2] * (1 - u) + 62 * u
    cam.rotation_euler = (tgt - cpos).to_track_quat("-Z", "Y").to_euler()
    cam.data.dof.focus_distance = (tgt - cpos).length
    cam.keyframe_insert("location", frame=f); cam.keyframe_insert("rotation_euler", frame=f); cam.data.keyframe_insert("lens", frame=f); cam.data.dof.keyframe_insert("focus_distance", frame=f)
    for wh in wheels:
        kit.key(wh, f, rot=(0, s / (0.075 * RV), 0))
kit.render(__file__)
