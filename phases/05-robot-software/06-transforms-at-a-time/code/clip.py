# 레슨 05/06 클립: 회전하며 벽을 스캔하는 로봇. 초록 점은 점마다 찍힌 시각의 pose, 파란 점은 모든 점을 최신 pose 로 놓은 결과
import pathlib
import sys

import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
V, W, SWEEP, SLOW, Z = 0.5, 1.0, 0.5, 7, 0.185                       # drive 0.5 m/s, turn 1 rad/s, a 0.5 s scan played 7x slower; Z = puck height
WALL = np.array([[2.0, y, 0.0] for y in np.linspace(-1, 1, 41)])     # one beam per stamp, as in the lesson's figure
STAMPS = np.linspace(0.0, SWEEP, 41)
pose = lambda t: (np.array([V * t, 0.0, 0.0]), np.array([np.cos(W * t / 2), 0, 0, np.sin(W * t / 2)]))
buf = m.PoseBuffer()
for t in np.linspace(0, SWEEP, 6):
    buf.add(t, *pose(t))
pts = [m.quat_to_R(pose(t)[1]).T @ (x - pose(t)[0]) for t, x in zip(STAMPS, WALL)]
dots = {"green": m.to_world(buf, STAMPS, pts), "blue": m.to_world(buf, STAMPS, pts, use_stamps=False)}
fr = lambda t: int(round(t * SLOW * 24)) + 1

sc = kit.setup(SWEEP * SLOW + 1.5)
kit.box("wall", (0.05, 2.3, 0.1), (2.03, 0, 0.05), "grey")
rover, wheels = kit.rover("rover", "navy")
beam = kit.box("beam", (1, 0.014, 0.014), (0, 0, Z), "amber", bevel=0)
for f in range(sc.frame_start, sc.frame_end + 1):
    t = min((f - 1) / 24 / SLOW, SWEEP)
    kit.drive(rover, wheels, f, V * t, 0, W * t, radius=0.075)
for i, s in enumerate(STAMPS):
    o = pose(s)[0]
    d = WALL[i] - o
    beam.scale = (np.hypot(d[0], d[1]), 1, 1)
    kit.key(beam, fr(s), loc=(o[0] + d[0] / 2, d[1] / 2, Z), rot=(0, 0, np.arctan2(d[1], d[0])))
    beam.keyframe_insert("scale", frame=fr(s))
    for colour, p in dots.items():
        ball = kit.ball(f"{colour}{i}", 0.035, (p[i][0], p[i][1], Z), colour)
        for frame, k in ((fr(s) - 1, 0.001), (fr(s), 1.0)):
            ball.scale = (k,) * 3
            ball.keyframe_insert("scale", frame=frame)
beam.scale = (0.001,) * 3
beam.keyframe_insert("scale", frame=fr(SWEEP) + 2)
kit.camera((-1.2, -2.6, 2.2), (1.2, 0.05, 0.1), lens=48)
kit.render(__file__)
