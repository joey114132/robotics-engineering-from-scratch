# 레슨 02/04 클립: 팔끝을 바깥으로 0.1 m/s 밀 때 일반 역행렬(파랑)은 거의 다 펴지는 순간 속도를 폭주시켜 쭉 펴진 채 멈추고 damped(초록)는 부드럽게 따라간다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, SLOW, DT, LIM, L, V = 5.0, 2.0, 0.001, 4.0, (0.5, 0.4), np.array([0.1, 0.0])   # half speed; drives top out at 4 rad/s; tip told to go outward at 0.1 m/s
T_END, Q0, ARROW, CAP = 1.4849, (-0.0906, 1.1318), 0.15, 0.5  # the lesson's arm bent so the tip sits at (0.7, 0.3); a red arrow shows the demanded joint speed, 0.15 m per rad/s, capped at 0.5 m; the push stops at x = 0.8485 m, the edge of reach


def run(lam):
    q, out = np.array(Q0), []
    for _ in range(int(SECONDS / SLOW / DT) + 1):
        v = V if len(out) * DT < T_END else 0 * V
        try:
            qd = m.solve(m.jacobian(q, L), v, lam)               # the lesson's solve(): what the controller asks for
        except np.linalg.LinAlgError:
            qd = np.array([0.0, -1e3]) if v.any() else np.zeros(2)
        out.append((q.copy(), qd))
        q = q + np.clip(qd, -LIM, LIM) * DT
    return out


sc = kit.setup(SECONDS)
kit.table((3.0, 0.7), 0.4, (-0.15, 0))
runs, arms = {}, {}
for name, colour, x, lam in (("plain", "blue", -1.3, 0.0), ("damped", "green", 0.0, 0.05)):
    root, js = kit.arm(name, L, colour)
    root.location = (x, 0, 0.4)
    kit.tube(name + "-path", [(x + p, -0.14, 0.7 + 0.3) for p in (0.7, 0.8485)], 0.012, "amber")   # the line the tip is told to follow
    arms[name] = (js, x, kit.arrow(name + "-demand", "red" if lam == 0 else "amber", 0.02))
    runs[name] = run(lam)
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / SLOW / DT), len(runs["plain"]) - 1)
    for name, (js, x, arrow) in arms.items():
        q, qd = runs[name][i]
        kit.pose(js, f, q)
        a = q[0] + q[1]
        tip = np.array([L[0] * np.cos(q[0]) + L[1] * np.cos(a), L[0] * np.sin(q[0]) + L[1] * np.sin(a)])
        side = np.array([np.sin(a), -np.cos(a)])                 # the way the elbow turns the hand when it is told to straighten
        arrow.location = (x + tip[0], 0.14, 0.7 + tip[1])
        arrow.scale = (max(min(ARROW * np.linalg.norm(qd), CAP), 1e-3), 1, 1)
        arrow.rotation_euler = (0, -np.arctan2(side[1], side[0]), 0)
        for prop in ("location", "scale", "rotation_euler"):
            arrow.keyframe_insert(prop, frame=f)
kit.camera((-0.15, -3.75, 2.1), (-0.15, 0, 0.95), lens=50)
kit.render(__file__)
