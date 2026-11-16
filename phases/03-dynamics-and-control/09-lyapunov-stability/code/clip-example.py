# 레슨 03/09 예시 클립: kd=-1 인 같은 PD 진자 팔을 정지 상태에서 시작하면 그대로 멈춰 있고 0.1 rad 건드리면 흔들림이 커진다. kd=2 로 건드린 팔은 가라앉는다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import math

import bpy
import numpy as np

import kit

m = kit.lesson_main(__file__)
DT, T, SLOW = 1e-3, 8.0, 1.5                 # 8 s of the lesson's pendulum, played at 1.5x speed
CASES = (("rest", "blue", -1.0, 0.0, -1.4), ("nudged", "blue", -1.0, 0.1, 0.0), ("damped", "green", 2.0, 0.1, 1.4))   # name, colour, kd, start angle, x on the bench
BIG, KNEE = 4.0, 0.15                         # angles up to 0.15 rad are drawn 4x larger, so a 0.1 rad nudge shows; past that the drawing keeps the true slope


def drawn(th):
    a = abs(th)
    return float(np.sign(th)) * (BIG * a if a <= KNEE else BIG * KNEE + (a - KNEE))


runs = {}
for name, _, kd, q0, _ in CASES:
    p = dict(m.DEFAULT, kd=kd)
    x, out = np.array([q0, 0.0]), []
    for _ in range(int(T / DT)):             # the loop inside m.simulate, keeping the angle
        out.append(x)
        a = m.f(x, p)[1]
        x = np.array([x[0] + DT * (x[1] + DT * a), x[1] + DT * a])
    assert np.allclose([m.V(s, p) for s in out], m.simulate(p, [q0, 0.0], T=T))   # same run as the lesson's own
    runs[name] = [s[0] for s in out]

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


sc = kit.setup(T / SLOW)
L, PIVOT_Z, WALL_Y = (0.35, 0.35), 1.15, 0.9
kit.box("backdrop", (4.6, 0.05, 2.8), (0, WALL_Y, 1.3), "pearl", bevel=0)     # a plain light panel behind the swing, so the arm reads against it
for name, c, _, _, x in CASES:
    joints = pendulum_arm(name, c, x, 0.0, L, PIVOT_Z, WALL_Y)
    for f in range(sc.frame_start, sc.frame_end + 1):
        kit.pose(joints, f, [-math.pi / 2 + drawn(runs[name][min(int((f - 1) / 24 * SLOW / DT), len(runs[name]) - 1)]), 0.0])
kit.camera((0, -3.5, 1.7), (0, 0, 1.15), lens=34)
kit.render(__file__)
