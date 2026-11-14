# 레슨 04/02 예시 클립: position 모드 팔 두 대에 같은 2 Nm 를 민다. 파란 팔은 그대로 버티고 초록 팔은 admittance 층이 목표를 위로 옮겨 K=20 처럼 밀려난다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
DT, SECONDS, SLOW, SCALE, L, K, PUSH, T_PUSH = 1e-4, 2.5, 2.0, 5.0, 0.5, 20.0, 2.0, 0.5   # 2.5 s of the push at half speed; angles drawn 5 times larger
runs = {"plain": m.run("position", K=K, push=PUSH, T=SECONDS, dt=DT)[1], "layer": m.run("admittance", K=K, push=PUSH, T=SECONDS, dt=DT)[1]}

sc = kit.setup(SECONDS * SLOW)
kit.table((1.8, 0.7), 0.4)
rigs = {}
for name, x, colour in (("plain", -0.62, "blue"), ("layer", 0.18, "green")):
    root, joints = kit.arm(name, (L,), colour, base_height=0.35)
    root.location = (x, 0, 0.4)
    target = kit.ball("target", 0.035, (0, 0, 0), "amber")        # the angle the drive is told to hold; the layer moves it by tau_ext / K
    arrow = kit.arrow("push", "red")
    arrow.rotation_euler = (0, -math.pi / 2, 0)                   # a push straight up under the hand
    rigs[name] = (x, joints, target, arrow)
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / sc.render.fps / SLOW
    i = min(int(t / DT), len(runs["plain"]) - 1)
    for name, (x, joints, target, arrow) in rigs.items():
        q = SCALE * runs[name][i]
        kit.pose(joints, f, [q])
        qc = SCALE * (PUSH / K if (name == "layer" and t >= T_PUSH) else 0.0)
        kit.key(target, f, loc=(x + (L + 0.17) * math.cos(qc), 0, 0.75 + (L + 0.17) * math.sin(qc)))
        kit.key(arrow, f, loc=(x + L * math.cos(q) + 0.07, 0, 0.45 + L * math.sin(q)))
        arrow.scale = (0.2 * min(max((t - T_PUSH) / 0.1, 0.0), 1.0) + 0.001, 1, 1)
        arrow.keyframe_insert("scale", frame=f)
kit.camera((0.0, -2.5, 1.5), (0.0, 0, 0.7), lens=50)
kit.render(__file__)
