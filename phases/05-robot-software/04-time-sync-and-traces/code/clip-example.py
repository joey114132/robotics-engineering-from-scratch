# 레슨 05/04 예시 클립: 팔이 세 목표 중 두 번째를 건너뛴다. reader 가 순서대로 확인하다 첫 불일치에서 멈춰 첫 목표는 초록, 두 번째는 빨강이 되고 세 번째는 호박색으로 남는다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
L, GRIP, BASE, SECONDS = 0.4, 0.085, 0.3, 5.4
T = [(0.25, 0.5), (0.6, 0.3), (0.75, -0.1)]                       # the three targets as (x, z) from the shoulder
fr = lambda t: int(round(t * 24)) + 1


def ik(p):
    """Elbow-up joint angles that put the finger centre at p = (x, z) from the shoulder."""
    w = p
    for _ in range(5):
        a = math.acos(min(1.0, math.hypot(*w) / (2 * L)))
        q = (math.atan2(w[1], w[0]) + a, -2 * a)
        w = (p[0] - GRIP * math.cos(q[0] + q[1]), p[1] - GRIP * math.sin(q[0] + q[1]))
    return np.array(q)


q0, Q = np.array([1.7, 2.4]), [ik(p) for p in T]
post = [Q[0], Q[0], Q[2]]                                          # step 2 leaves the arm where it was
pre = [q0, Q[0], Q[0]]
intents = [dict(step=i + 1, target=list(Q[i])) for i in range(3)]
lines = [m.trace_line(i + 1, "reach", pre[i], post[i]) for i in range(3)]
bad = m.first_mismatch(intents, lines)
assert bad == {"step": 2, "kind": "no_motion"}                     # what the lesson's reader reports
sc = kit.setup(SECONDS)
root, joints = kit.arm("arm", (L, L), "blue", BASE)
beads = []
for x, z in T:                                                     # each target: a peg with an amber bead; green and red copies wait hidden
    kit.cyl("peg", 0.012, BASE + z - 0.04, (x, -0.1, (BASE + z - 0.04) / 2), "z", "grey")   # a little in front of the arm's plane
    beads.append({c: kit.ball("bead-" + c, 0.032, (x, -0.1, BASE + z), c) for c in ("amber", "green", "red")})
pointer = kit.arrow("pointer", "dark")
pointer.rotation_euler = (0, math.pi / 2, 0)                       # points down at the target being checked
pointer.scale = (0.22, 1, 1)


def show(k, name, t):
    """From time t on, bead k shows only the colour `name`."""
    for c, b in beads[k].items():
        b.scale = (1,) * 3 if c == name else (0.001,) * 3
        b.keyframe_insert("scale", frame=fr(t))


kit.pose(joints, 1, q0)
for t, q in ((0.4, q0), (1.1, Q[0]), (2.3, Q[0]), (3.0, Q[2])):     # run: step 1 moves, step 2 does not, step 3 moves
    kit.pose(joints, fr(t), q)
for k in range(3):
    show(k, "amber", 0.0)
for k, colour, tc in ((0, "green", 4.0), (1, "red", 4.7)):         # read: check in order, stop at the first mismatch
    show(k, "amber", tc - 0.04)
    show(k, colour, tc)
kit.key(pointer, 1, loc=(T[0][0], -0.1, -1.0))                          # under the floor until the reader starts
kit.key(pointer, fr(3.5), loc=(T[0][0], -0.1, -1.0))
for t, k in ((3.6, 0), (4.0, 0), (4.7, 1)):
    kit.key(pointer, fr(t), loc=(T[k][0], -0.1, BASE + T[k][1] + 0.3))
kit.camera((0.4, -3.0, 1.6), (0.4, 0.0, 0.7), lens=42)
kit.render(__file__)
