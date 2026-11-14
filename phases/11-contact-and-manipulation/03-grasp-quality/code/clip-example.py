# 레슨 11/03 예시 클립: 한 gripper 의 오른쪽 jaw 를 천천히 올린다. offset 이 2 mu = 0.6 에 닿기 전에는 같은 비틀림 하중에도 상자가 버티고 넘으면 돈다
import itertools
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
MU, S, ZC, T0, RAMP, OFF_MAX, TW, SECONDS, MAG = 0.3, 0.2, 0.95, 0.6, 2.0, 0.8, 1.25, 5.4, 0.25   # friction, metres per lesson unit, box centre height, still s, ramp s, final offset, turn s, clip s, load size


def residual(W, w):
    """What the contacts cannot cancel of an external wrench w: min |w + W.T lam| over lam >= 0, by trying every active set."""
    best = (np.inf, w)
    for k in range(1, len(W) + 1):
        for idx in itertools.combinations(range(len(W)), k):
            A = W[list(idx)].T
            lam = np.linalg.lstsq(A, -w, rcond=None)[0]
            if (lam >= -1e-9).all() and np.linalg.norm(w + A @ lam) < best[0] - 1e-12:
                best = (np.linalg.norm(w + A @ lam), w + A @ lam)
    return best[1]


def wrenches(off):
    return m.contact_wrenches([[-1, 0], [1, off]], [[1, 0], [-1, 0]], MU)


g = np.arange(30000) + 0.5                                       # the load: the weakest direction of the open grasp, as in the lead clip
phi, th = math.pi * (1 + 5 ** 0.5) * g, np.arccos(1 - 2 * g / 30000)
D = np.c_[np.cos(phi) * np.sin(th), np.sin(phi) * np.sin(th), np.cos(th)]
load = -MAG * D[(D @ wrenches(0.8).T).max(1).argmin()]

sc = kit.setup(SECONDS)
FX, PAD = 0.34, 0.03                                             # the fingers stand outside the turning box (corner radius S * sqrt 2 = 0.28)
for sx in (-1, 1):
    kit.box("finger", (0.06, 0.2, 0.7), (sx * (FX + 0.03), 0, ZC), "blue", bevel=0.01)
rods = [kit.box("rod", (1.0, 0.05, 0.03), (0, 0, ZC), "dark", bevel=0.005) for sx in (-1, 1)]   # unit length, stretched from pad to finger each frame
pads = [kit.box("pad", (PAD, 0.14, 0.07), (sx * (S + PAD / 2), 0, ZC), "dark", bevel=0.006) for sx in (-1, 1)]
kit.box("palm", (2 * (FX + 0.06), 0.2, 0.1), (0, 0, ZC + 0.38), "blue", bevel=0.01)
kit.cyl("post", 0.05, ZC + 0.38, (0, 0.25, (ZC + 0.38) / 2), "z", "grey")
kit.box("bar", (0.1, 0.5, 0.1), (0, 0.12, ZC + 0.38), "grey", bevel=0.01)
LIM = S * 2 * MU                                                 # the jaw height where offset = 2 mu, marked on the right finger
kit.box("limit", (0.08, 0.22, 0.014), (FX + 0.1, -0.01, ZC + LIM), kit.ghost("amber", 0.6), bevel=0)
kit.box("rail", (0.012, 0.22, LIM), (FX + 0.066, -0.01, ZC + LIM / 2), kit.ghost("amber", 0.35), bevel=0)
box = kit.crate("box", 2 * S, (0, 0, ZC))
arc = [(0.34 * math.cos(math.radians(a)), -0.28, ZC + 0.34 * math.sin(math.radians(a))) for a in range(215, 311, 6)]
kit.tube("twist", arc, 0.014, "red")
head = kit.arrow("twist-head", "red", 0.014)                     # the load is a counter-clockwise twist about the box centre
head.location, head.scale = arc[-1], (0.2, 1, 1)
head.rotation_euler = (0, -math.radians(310 + 90), 0)

I, SUB = 2 / 3, 8                                               # moment of inertia of a unit-mass square of side 2; physics steps per frame
pos, vel, moved = np.zeros(3), np.zeros(3), 0.0
for f in range(sc.frame_start, sc.frame_end + 1):
    for k in range(SUB):
        t, dt = ((f - 1) + k / SUB) / sc.render.fps, 1 / (sc.render.fps * SUB)
        off = OFF_MAX * min(max((t - T0) / RAMP, 0.0), 1.0)
        r = residual(wrenches(off), load) * np.array([1.0, 1.0, 1.0 / I])
        if np.linalg.norm(r) > 1e-6 and moved < TW:                # the box only moves while the contacts cannot cancel the load
            vel, moved = vel + r * dt, moved + dt
        if moved >= TW:                                            # the turn is drawn for 1.25 s, then the box rests
            vel = np.zeros(3)
        pos = pos + vel * dt
    off = OFF_MAX * min(max(((f - 1) / sc.render.fps - T0) / RAMP, 0.0), 1.0)
    phi = -pos[2]                                                 # the box's turn about y, as keyed below
    kit.key(box, f, loc=(S * pos[0], 0, ZC + S * pos[1]), rot=(0, phi, 0))
    for sx, hgt in ((-1, 0.0), (1, S * off)):                     # each pad stays on its box face at its own height, and a rod joins it to the finger
        u = (hgt - S * pos[1] + sx * S * math.sin(phi)) / math.cos(phi)
        fx_, fz_ = S * pos[0] + sx * S * math.cos(phi) + u * math.sin(phi), -sx * S * math.sin(phi) + u * math.cos(phi) + S * pos[1]
        nx, nz = sx * math.cos(phi), -sx * math.sin(phi)         # outward face normal
        pad, rod = pads[(sx + 1) // 2], rods[(sx + 1) // 2]
        kit.key(pad, f, loc=(fx_ + nx * PAD / 2, 0, ZC + fz_ + nz * PAD / 2), rot=(0, phi, 0))
        x_in = fx_ + nx * PAD
        kit.key(rod, f, loc=((x_in + sx * FX) / 2, 0, ZC + fz_ + nz * PAD))
        rod.scale = (abs(sx * FX - x_in), 1, 1)
        rod.keyframe_insert("scale", frame=f)
kit.camera((0, -2.1, 1.7), (0, 0, 0.95), lens=38)
kit.render(__file__)
