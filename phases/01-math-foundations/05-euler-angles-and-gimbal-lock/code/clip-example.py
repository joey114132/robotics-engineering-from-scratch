# 레슨 01/05 예시 클립: pitch 90도에서는 roll 고리를 +1.2 rad 돌린 것과 yaw 고리를 -1.2 rad 돌린 것이 같은 카메라 자세를 만든다. 고리 두 개가 한 줄 위에 있다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, FPS, D, CZ, SC, ANGLE = 4.5, 24, math.pi / 180, 0.85, 0.8, 1.2      # the rigs are drawn at 0.8 of the lead clip's size
sc = kit.setup(SECONDS)
kit.camera((0.0, -4.6, 4.5), (0.0, 0.0, 0.5), lens=75)      # a long lens, so both rigs are seen at nearly the same angle


def circle(name, r, plane, parent, colour):
    """A ring of radius r in the plane ('yz', 'xy' or 'xz'), with an amber bead at 45 degrees round it, off every axle."""
    pts = [(0, r * math.cos(a), r * math.sin(a)) if plane == "yz" else (r * math.cos(a), r * math.sin(a), 0) if plane == "xy" else (r * math.cos(a), 0, r * math.sin(a))
           for a in [i * math.pi / 45 for i in range(91)]]
    kit.tube(name, pts, 0.022, colour).parent = parent
    kit.ball(name + "-bead", 0.045, pts[11], "amber", parent=parent)


def pin(name, a, b, parent, r=0.012):          # a short axle between two rings
    axis = "x" if abs(a[0] - b[0]) > 1e-6 else "y" if abs(a[1] - b[1]) > 1e-6 else "z"
    kit.cyl(name, r, math.dist(a, b), [(u + v) / 2 for u, v in zip(a, b)], axis, "dark", parent=parent)


def rig(name, x):
    """A camera in three rings: outer ring about the vertical axis (yaw), middle ring about y (pitch), inner ring about x (roll)."""
    base = kit.empty(name, (x, 0, 0))
    base.scale = (SC,) * 3
    base.rotation_euler = (0, 0, math.radians(40))      # turned so the camera sees every ring at a slant
    kit.cyl(name + "-foot", 0.25, 0.04, (0, 0, 0.02), "z", "dark", bevel=0.01, parent=base)
    kit.cyl(name + "-post", 0.06, CZ - 0.5, (0, 0, (CZ - 0.5) / 2 + 0.04), "z", "grey", parent=base)
    yaw = kit.empty(name + "-yaw", (0, 0, CZ), base)
    circle(name + "-outer", 0.62, "yz", yaw, "navy")
    pitch = kit.empty(name + "-pitch", (0, 0, 0), yaw)
    circle(name + "-middle", 0.5, "xy", pitch, "blue")
    pin(name + "-p+", (0, 0.5, 0), (0, 0.62, 0), pitch)
    pin(name + "-p-", (0, -0.5, 0), (0, -0.62, 0), pitch)
    roll = kit.empty(name + "-roll", (0, 0, 0), pitch)
    circle(name + "-inner", 0.38, "xz", roll, "sky")
    pin(name + "-r+", (0.38, 0, 0), (0.5, 0, 0), roll)
    pin(name + "-r-", (-0.38, 0, 0), (-0.5, 0, 0), roll)
    kit.box(name + "-camera", (0.26, 0.2, 0.16), (0, 0, 0), "dark", bevel=0.02, parent=roll)
    kit.cyl(name + "-lens", 0.07, 0.14, (0.19, 0, 0), "x", "pearl", bevel=0.008, parent=roll)
    kit.box(name + "-fin", (0.16, 0.035, 0.12), (-0.04, 0, 0.14), "amber", bevel=0.005, parent=roll)      # the fin shows which way the camera is twisted
    return yaw, pitch, roll


def ease(s):
    s = min(max(s, 0.0), 1.0)
    return s * s * (3 - 2 * s)


rigs = {"roll ring": (rig("roll-turned", -0.8), (lambda a: (a, 0.0))), "yaw ring": (rig("yaw-turned", 0.8), (lambda a: (0.0, -a)))}   # (roll, yaw) by the angle a
for f in range(sc.frame_start, sc.frame_end + 1):
    a = ANGLE * ease((f / FPS - 0.5) / 2.6)
    for (yaw, pitch, roll), turn in rigs.values():
        r_, y_ = turn(a)
        kit.key(yaw, f, rot=(0, 0, y_))
        kit.key(pitch, f, rot=(0, 90 * D, 0))
        kit.key(roll, f, rot=(r_, 0, 0))
assert np.allclose(m.euler_to_R(ANGLE, 90 * D, 0.0), m.euler_to_R(0.0, 90 * D, -ANGLE))      # the lesson's claim: at pitch 90 only yaw - roll counts
kit.render(__file__)
