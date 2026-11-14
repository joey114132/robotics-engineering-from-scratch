# 레슨 09/01 예시 클립: 같은 1 rad 이동을 trapezoid(파랑)와 quintic(초록)으로 하는 탁상 팔 두 대, 빨간 화살표는 가속도(trapezoid 는 네 번 계단)
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
T, TA, LEAD, SLOW, L = 2.0, 0.5, 0.7, 1.5, 0.75   # the lesson's 2 s move with a 0.5 s ramp, played 1.5 times slower, with a short rest before and after
profile = {"blue": m.trapezoid(0.0, 1.0, T, TA), "green": lambda t: m.poly(m.quintic(0.0, 1.0, T), t)}

sc = kit.setup(LEAD + T * SLOW + 1.3)
kit.table(size=(2.4, 0.7), height=0.4, loc=(0.05, 0))
rigs = {}
for colour, x in (("blue", -0.5), ("green", 0.6)):
    root, joints = kit.arm("arm-" + colour, lengths=(0.45, 0.3), colour=colour)
    root.location = (x, 0, 0.4)
    rigs[colour] = (x, joints, kit.arrow("acc-" + colour, "red", shaft=0.026))
for f in range(sc.frame_start, sc.frame_end + 1):
    t = ((f - 1) / sc.render.fps - LEAD) / SLOW
    for colour, (x, joints, arrow) in rigs.items():
        q, _, a = (float(v) for v in profile[colour](t)) if 0 <= t <= T else (0.0 if t < 0 else 1.0, 0, 0.0)
        kit.pose(joints, f, [q, 0.0])
        kit.key(arrow, f, loc=(x + L * math.cos(q), -0.14, 0.7 + L * math.sin(q)), rot=(0, -(q + math.copysign(math.pi / 2, a)), 0))
        n = max(0.3 * abs(a), 1e-3)                      # 0.3 m of arrow per rad/s^2 of joint acceleration
        arrow.scale = (n, min(1.0, n / 0.15), min(1.0, n / 0.15))
        arrow.keyframe_insert("scale", frame=f)
kit.camera((0.2, -3.6, 2.1), (0.2, 0, 0.92), lens=50)
kit.render(__file__)
