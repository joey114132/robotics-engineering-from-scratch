# 레슨 02/03 예시 클립: 팔이 2 kg 블록을 받치고 쭉 뻗는다. 같은 힘인데 J^T F 로 계산한 어깨 토크 막대가 자란다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, HOLD, STRETCH, BAR = 5.5, 0.6, 3.6, 0.03   # hold, then stretch; a bar is drawn 0.03 m tall per N m
L, F = (0.5, 0.4), np.array([0.0, 2.0 * 9.81])      # the lesson's 2 kg block: the motors push it up with 2 * 9.81 N
Q0, Q1 = np.array([1.0, 1.5]), np.array([0.0, 0.0])
sc = kit.setup(SECONDS)
kit.table((2.4, 0.7), 0.4, (0.1, 0))
root, js = kit.arm("holder", L, "blue")
root.location = (0, 0, 0.4)
block = kit.crate("block", 0.12, colour="amber")
push = kit.arrow("weight", "red", 0.02)             # the force F on the block, pointing up
push.rotation_euler = (0, -np.pi / 2, 0)
bars = [kit.box(f"torque{i}", (0.05, 0.05, 1), (0, 0, 0), "amber", bevel=0) for i in range(2)]   # |tau| at each joint, from joint_torque()
for f in range(sc.frame_start, sc.frame_end + 1):
    s = np.clip(((f - 1) / sc.render.fps - HOLD) / STRETCH, 0, 1)
    q = Q0 + (Q1 - Q0) * s * s * (3 - 2 * s)
    tip = m.fk(q, L)
    tau = np.abs(m.joint_torque(m.jacobian(q, L), F))
    kit.pose(js, f, q)
    kit.key(block, f, loc=(tip[0] + 0.14, 0, 0.7 + tip[1]))
    kit.key(push, f, loc=(tip[0] + 0.14, 0, 0.7 + tip[1] + 0.08))
    push.scale = (0.25, 1, 1)
    push.keyframe_insert("scale", frame=f)
    elbow = np.array([L[0] * np.cos(q[0]), L[0] * np.sin(q[0])])
    for bar, tau_i, at in zip(bars, tau, ((0.0, 0.0), tuple(elbow))):
        h = max(BAR * tau_i, 1e-3)
        bar.scale = (1, 1, h)
        bar.location = (at[0] + 0.0, -0.17, 0.7 + at[1] + h / 2 + 0.1)
        bar.keyframe_insert("scale", frame=f)
        bar.keyframe_insert("location", frame=f)
kit.camera((0.1, -3.7, 2.45), (0.1, 0, 1.0), lens=50)
kit.render(__file__)
