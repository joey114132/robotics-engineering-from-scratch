# 레슨 02/03 클립: 두 팔이 관절 공간에서 같은 작은 원을 돈다. 굽힌 팔(파랑)의 손끝 고리는 뚱뚱하고 거의 편 팔(초록)은 가늘다
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, LOOP, R, K = 5.0, 4.0, 0.3, 0.9     # one lap of a joint-space circle of radius 0.3 rad in 4 s; the arrow is drawn 0.9 s long
L = (0.5, 0.4)
sc = kit.setup(SECONDS)
kit.table((3.0, 0.7), 0.4, (-0.15, 0))
arms = {}
for name, colour, x, q0 in (("bent", "green", -1.3, np.array([0.3, 1.5])), ("straight", "blue", 0.0, np.array([0.3, 0.35]))):
    root, js = kit.arm(name, L, colour)
    root.location = (x, 0, 0.4)
    loop = [m.fk(q0 + R * np.array([np.cos(p), np.sin(p)]), L) for p in np.linspace(0, 2 * np.pi, 60)]
    kit.tube(name + "-loop", [(x + p[0], 0, 0.7 + p[1]) for p in loop], 0.01, "dark")   # where the tip really goes
    arrow = kit.arrow(name + "-v", "amber", 0.03)                       # J times the joint speeds: the tip velocity
    arms[name] = (js, x, q0, arrow)
for f in range(sc.frame_start, sc.frame_end + 1):
    u = np.clip((f - 1) / sc.render.fps / LOOP, 0, 1)
    phi, dphi = 2 * np.pi * u * u * (3 - 2 * u), 2 * np.pi * 6 * u * (1 - u) / LOOP   # eased lap and its angular speed
    for name, (js, x, q0, arrow) in arms.items():
        q = q0 + R * np.array([np.cos(phi), np.sin(phi)])
        qd = R * dphi * np.array([-np.sin(phi), np.cos(phi)])
        v = m.J_times(m.jacobian(q, L), qd)
        tip = m.fk(q, L)
        kit.pose(js, f, q)
        arrow.location = (x + tip[0], 0, 0.7 + tip[1])
        arrow.scale = (max(K * np.hypot(*v), 1e-3), 1, 1)
        arrow.rotation_euler = (0, -np.arctan2(v[1], v[0]), 0)
        arrow.keyframe_insert("location", frame=f)
        arrow.keyframe_insert("scale", frame=f)
        arrow.keyframe_insert("rotation_euler", frame=f)
kit.camera((-0.15, -3.75, 2.1), (-0.15, 0, 0.95), lens=50)
kit.render(__file__)
