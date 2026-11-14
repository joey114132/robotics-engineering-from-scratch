# 레슨 10/01 예시 클립: 밀침 0.1 과 0.4 를 발목만으로 받는다. 보라색 기둥은 capture point 이고 회색 기둥 두 개는 발의 양 끝이다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
H, HALF, DT, TEND, SLOW, PRE, K = 0.9, 0.05, 1e-3, 1.0, 2.5, 12, 3.0           # the lesson's body height and foot; 1 s of motion played 2.5x slower; the posts are drawn K = 3 times farther from the ankle so the gap reads
runs = {v0: m.fall_or_recover(v0, H, HALF, False, T=TEND, dt=DT) for v0 in (0.1, 0.4)}

sc = kit.setup(PRE / 24 + TEND * SLOW + 1.6)
walkers = {}
for v0, (colour, x0) in {0.1: ("green", -0.95), 0.4: ("blue", -0.05)}.items():
    for sx in (-HALF, HALF):
        kit.cyl("end", 0.012, 0.6, (x0 + K * sx, -0.3, 0.3), "z", "#5d7480")            # the two ends of the foot: the ZMP stays between these posts
    pel = kit.box("pelvis", (0.16, 0.3, 0.14), (0, 0, 0), colour, bevel=0.04)
    kit.box("torso", (0.14, 0.26, 0.3), (0, 0, 0.22), colour, bevel=0.04, parent=pel)
    kit.ball("head", 0.08, (0, 0, 0.45), "pearl", parent=pel)
    legs = [kit.empty("leg") for _ in (0, 1)]
    for lg in legs:
        kit.cyl("bone", 0.035, 1.0, (0.5, 0, 0), "x", "dark", parent=lg, segments=20)   # scaled in x to the leg length
    for dy in (0.09, -0.09):
        kit.box("foot", (2 * HALF, 0.08, 0.04), (x0, dy, 0.02), "dark", bevel=0.01)
    mark = kit.cyl("capture", 0.014, 0.7, (0, -0.3, 0.35), "z", kit.mat("#8e5bd9", emit=0.8))   # a tall post so it reads from the camera
    walkers[v0] = (x0, pel, legs, mark, kit.arrow("push", "red"))

for f in range(1, sc.frame_end + 1):
    t = min(max(f - 1 - PRE, 0) / 24 / SLOW, TEND)
    i = int(round(t / DT))
    for v0, (x0, pel, legs, mark, push) in walkers.items():
        x = x0 + runs[v0][1][i]
        kit.key(pel, f, loc=(x, 0, H))
        for k, dy in enumerate((0.09, -0.09)):
            a, b = (x0, dy, 0.04), (x, dy, H - 0.05)
            legs[k].scale = (math.hypot(b[0] - a[0], b[2] - a[2]), 1, 1)
            legs[k].keyframe_insert("scale", frame=f)
            kit.key(legs[k], f, loc=a, rot=(0, -math.atan2(b[2] - a[2], b[0] - a[0]), 0))
        kit.key(mark, f, loc=(x0 + K * float(m.capture_point(runs[v0][1][i], runs[v0][2][i], H)), -0.3, 0.35))
        push.scale = (0.3, 1.6, 1.6) if f <= PRE + 1 else (1e-4,) * 3
        push.keyframe_insert("scale", frame=f)
        kit.key(push, f, loc=(x0 - 0.5, 0, H + 0.1))
kit.camera((0.2, -3.9, 1.9), (0.2, 0, 0.5), lens=38)
kit.render(__file__)
