# 레슨 11/03 클립: 같은 비틀림 하중을 받는 두 파지. 턱 offset 0.4는 force closure라 버티고 0.8은 closure가 없어 상자가 돈다
import itertools
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
MU, S, ZC, T0, TW, HOLD, MAG = 0.3, 0.2, 0.95, 0.5, 1.7, 2.3, 0.25
GAP, PZ = 0.34, 0.95 + 0.43                                   # finger inner face distance from the box centre, palm height   # friction, metres per lesson unit, box centre height, still s, twist s, hold s, load size
GRASPS = ((0.4, "green", -0.62), (0.8, "blue", 0.62))                # jaw offset (lesson units), gripper colour, x position


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


# the load is the weakest direction of the open grasp, found on a sphere of directions: the one most contact wrenches point away from
g = np.arange(30000) + 0.5
phi, th = math.pi * (1 + 5 ** 0.5) * g, np.arccos(1 - 2 * g / 30000)
D = np.c_[np.cos(phi) * np.sin(th), np.sin(phi) * np.sin(th), np.cos(th)]
load = -MAG * D[(D @ wrenches(0.8).T).max(1).argmin()]
sc = kit.setup(T0 + TW + HOLD)
boxes = []
for off, col, cx in GRASPS:
    assert (m.epsilon(wrenches(off)) > 0) == (off < 0.6)       # closes exactly when the offset is under 2 mu
    pads = []
    for sx in (-1, 1):                                          # fingers sit outside the swept corners (0.28 m plus the drift); the pads slide in to stay on the box
        kit.box("finger", (0.06, 0.2, 0.72), (cx + sx * (GAP + 0.03), 0, ZC + 0.02), col, bevel=0.01)
        pads.append((sx, ZC + S * (off if sx > 0 else 0.0), kit.box("pad", (1, 0.14, 0.07), (cx, 0, ZC), "dark", bevel=0.008)))
    kit.box("palm", (2 * GAP + 0.12, 0.2, 0.1), (cx, 0, PZ), col, bevel=0.01)
    kit.cyl("post", 0.05, PZ, (cx, 0.25, PZ / 2), "z", "grey")
    kit.box("bar", (0.1, 0.5, 0.1), (cx, 0.12, PZ), "grey", bevel=0.01)
    box = kit.crate("box", 2 * S, (cx, 0, ZC))
    arc = [(cx + 0.34 * math.cos(math.radians(a)), -0.28, ZC + 0.34 * math.sin(math.radians(a))) for a in range(215, 311, 6)]
    kit.tube("twist", arc, 0.014, "red")
    head = kit.arrow("twist-head", "red", 0.014)                       # the load is a counter-clockwise twist about the box centre
    head.location, head.scale = arc[-1], (0.2, 1, 1)
    head.rotation_euler = (0, -math.radians(310 + 90), 0)
    boxes.append((box, cx, residual(wrenches(off), load), pads))
I = 2 / 3                                                       # moment of inertia of a unit-mass square of side 2

for f in range(sc.frame_start, sc.frame_end + 1):
    t = min(max((f - 1) / sc.render.fps - T0, 0.0), TW)
    for box, cx, r, pads in boxes:
        x, z, ang = 0.5 * r * np.array([1.0, 1.0, 1.0 / I]) * t * t    # unit mass; the third wrench entry is torque / rho with rho = 1
        bx, bz = cx + S * x, ZC + S * z
        kit.key(box, f, loc=(bx, 0, bz), rot=(0, -ang, 0))
        for sx, zp, pad in pads:                                  # the box face at the pad's height, then the pad reaches from there to the finger
            face = bx + sx * (S - sx * (zp - bz) * math.sin(ang)) / math.cos(ang)
            pad.scale = (sx * (cx + sx * GAP - face), 1, 1)
            kit.key(pad, f, loc=((face + cx + sx * GAP) / 2, 0, zp))
            pad.keyframe_insert("scale", frame=f)
kit.camera((0, -2.7, 1.9), (0, 0, 0.9), lens=38)
kit.render(__file__)
