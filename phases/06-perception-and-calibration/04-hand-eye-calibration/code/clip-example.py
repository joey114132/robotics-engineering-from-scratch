# 레슨 06/04 예시 클립: 팔이 수직축 하나로만 도는 동작(spread 0)에서는 카메라를 그 축 방향으로 0.1 m 올려도 A X = X B 가 그대로 성립한다. 두 카메라가 같은 원을 그린다
import math
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
X = m.make_T(m.rodrigues(np.array([0.3, -0.5, 0.8])), [0.05, 0.03, 0.08])
As, Bs = m.make_motions(X, 12, 0.0, 0.0, 0.0, seed=1)          # 12 noise-free motions whose rotation axes all equal z
X2 = X.copy(); X2[:3, 3] += 0.1 * np.array([0, 0, 1.0])        # the camera slid 0.1 m along that axis
assert max(np.abs(A @ Xc - Xc @ B).max() for A, B in zip(As, Bs) for Xc in (X, X2)) < 1e-9   # both mounts explain every motion exactly
SHOULDER, Q = 0.3, (0.6, -0.9)                                 # pose held while the base pans
e = lambda a: np.array([math.cos(a), 0, math.sin(a)])
hand = np.array([0, 0, SHOULDER]) + 0.4 * e(Q[0]) + 0.4 * e(sum(Q))   # hand position in the arm's base frame
sc = kit.setup(5)

kit.table((1.1, 1.1), 0.4, (0.3, 0.0))
root, joints = kit.arm("arm", colour="blue", base_height=SHOULDER)
root.location = (0, 0, 0.4)
kit.pose(joints, 1, Q)
real, ghost = kit.empty("cam-real", tuple(hand + (0.07, 0, 0.0)), root), kit.empty("cam-ghost", tuple(hand + (0.07, 0, 0.1)), root)
for rig, body, lens in ((real, "dark", "grey"), (ghost, kit.ghost("blue", 0.4), kit.ghost("blue", 0.4))):
    kit.box("cam", (0.1, 0.08, 0.09), (0, 0, 0), body, bevel=0.012, parent=rig); kit.cyl("lens", 0.032, 0.05, (0.065, 0, 0), "x", lens, parent=rig)
turn = lambda f: -0.7 + 1.4 * min(max((f - 16) / 80, 0.0), 1.0)    # one slow pan from -0.7 to +0.7 rad, then still
for f in range(1, sc.frame_end + 1):
    kit.key(root, f, loc=(0, 0, 0.4), rot=(0, 0, turn(f)))
for off, name in ((0.0, "real"), (0.1, "ghost")):                  # a dotted trail for each camera: the same circle, one 0.1 m higher
    for k in range(0, 21):
        a, f0 = -0.7 + 0.07 * k, 16 + 4 * k
        r = np.hypot(hand[0] + 0.07, 0.0)
        dot = kit.ball(f"{name}-dot", 0.011, (r * math.cos(a), r * math.sin(a), 0.4 + hand[2] + off), "blue")
        dot.scale = (0.001,) * 3; dot.keyframe_insert("scale", frame=f0 - 1)
        dot.scale = (1, 1, 1); dot.keyframe_insert("scale", frame=f0 + 2)
kit.camera((1.75, -1.7, 1.55), (0.4, 0.0, 0.8), lens=60)
kit.render(__file__)
