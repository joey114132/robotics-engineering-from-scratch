# 레슨 02/04 예시 클립: 팔꿈치를 펴 가면 J 의 두 열(관절마다 손끝이 가는 방향)이 한 방향으로 포개져 팔 방향 움직임이 사라진다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, HOLD, STRAIGHTEN, K = 5.5, 0.7, 3.6, 0.5   # the elbow q2 goes from 1.4 rad to 0 (straight); arrows are drawn 0.5 m long per m/s of tip speed
L, Q1, Q2_0 = (0.5, 0.4), 0.5, 1.4
sc = kit.setup(SECONDS)
kit.table((2.4, 0.7), 0.4, (0.1, 0))
root, js = kit.arm("arm", L, "blue")
root.location = (0, 0, 0.4)
arrows = [kit.arrow(f"col{j}", c, 0.022) for j, c in enumerate(("amber", "dark"))]   # column j of J: tip velocity per unit speed of joint j
for f in range(sc.frame_start, sc.frame_end + 1):
    s = np.clip(((f - 1) / sc.render.fps - HOLD) / STRAIGHTEN, 0, 1)
    q = np.array([Q1, Q2_0 * (1 - s * s * (3 - 2 * s))])
    J, tip = m.jacobian(q, L), None
    a = q.sum()
    tip = np.array([L[0] * np.cos(q[0]) + L[1] * np.cos(a), L[0] * np.sin(q[0]) + L[1] * np.sin(a)])
    kit.pose(js, f, q)
    for j, arrow in enumerate(arrows):
        v = J[:, j]
        arrow.location = (tip[0], (0.05, -0.05)[j], 0.7 + tip[1])
        arrow.scale = (K * np.hypot(*v), 1, 1)
        arrow.rotation_euler = (0, -np.arctan2(v[1], v[0]), 0)
        for prop in ("location", "scale", "rotation_euler"):
            arrow.keyframe_insert(prop, frame=f)
kit.camera((0.1, -3.6, 2.4), (0.1, 0, 1.0), lens=50)
kit.render(__file__)
