# 레슨 03/09 클립: 같은 PD 진자 팔 둘. 초록 팔은 속도를 바로 보고 V 가 줄며 멈추고, 파란 팔은 속도를 0.5 s 늦게 봐서 V 가 늘며 위로 넘어간다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import math

import bpy
import numpy as np

import kit

m = kit.lesson_main(__file__)
DT, T, SLOW = 1e-3, 3.0, 3.0 / 5.0           # the first 3 s, up to the swing over the top, played over 5 s
runs = {}
for c, delay in (("green", 0.0), ("blue", 0.5)):
    x, hist, out = np.array([1.0, 0.0]), [0.0] * (int(round(delay / DT)) + 1), []
    for _ in range(int(T / DT)):                             # the loop inside m.simulate, keeping the state: the controller sees the rate from `delay` ago
        out.append(x)
        a = m.f(x, m.DEFAULT, vel_cmd=hist[0])[1]
        x = np.array([x[0] + DT * (x[1] + DT * a), x[1] + DT * a])
        hist = hist[1:] + [x[1]]
    assert np.allclose([m.V(s, m.DEFAULT) for s in out], m.simulate(m.DEFAULT, [1.0, 0.0], T=T, delay=delay))   # same run as the lesson's own
    runs[c] = [s[0] for s in out]

def pendulum_arm(name, colour, x, y, lengths, pivot_z, wall_y):
    """The lesson's pendulum as a bench arm that hangs from its joint: a short boom reaches back to the backdrop, links are chunky and
    coloured end to end (colour on both links and the fingers) so the arm never melts into the grey room, and the stand, bolts and
    flange are hidden (the lumps they left on the floor had no meaning)."""
    root, joints = kit.arm(name, lengths, colour, base_height=pivot_z)
    root.location = (x, y, 0)
    for ob in bpy.data.objects:
        if ob.name.startswith((name + "-post", name + "-foot", name + "-flange")) or (ob.parent is root and ob.name.startswith("bolt")):
            ob.hide_render = True
        elif ob.name.startswith(name + "-link"):
            ob.scale = (1, 2.0, 2.0)
            ob.data.materials[0] = kit.mat(colour)
        elif ob.name.startswith(name + "-finger"):
            ob.data.materials[0] = kit.mat(colour)
    reach = wall_y - 0.03 - (y + 0.07)
    kit.box(name + "-boom", (0.06, reach, 0.06), (x, y + 0.07 + reach / 2, pivot_z), "dark", bevel=0.01)   # from the joint straight back to the backdrop
    return joints


sc = kit.setup(5.0)
L, PIVOT_Z, WALL_Y = (0.4, 0.4), 1.4, 1.0
kit.box("backdrop", (4.8, 0.05, 3.2), (0, WALL_Y, 1.5), "pearl", bevel=0)     # a plain light panel behind the swing, so the arm reads against it
for c, x, y in (("green", -0.8, -0.1), ("blue", 0.8, 0.1)):
    joints = pendulum_arm(c, c, x, y, L, PIVOT_Z, WALL_Y)
    for f in range(sc.frame_start, sc.frame_end + 1):
        kit.pose(joints, f, [-math.pi / 2 + runs[c][min(int((f - 1) / 24 * SLOW / DT), len(runs[c]) - 1)], 0.0])
kit.camera((0, -3.81, 2.21), (0, 0, 1.4), lens=38)   # the swing circle (1.9 m across) fills the picture height
kit.render(__file__)
