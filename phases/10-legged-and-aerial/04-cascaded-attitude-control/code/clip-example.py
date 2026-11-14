# 레슨 10/04 예시 클립: 시험대의 드론 둘이 같은 돌풍을 맞는다. 주황 화살표는 제어기가 되미는 토크로 둘 다 0.1 Nm 에 이르지만 기울어 있는 쪽은 PD 뿐이다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
I, KP, KD, KI, DT, T0, TEND, SLOW, PRE, EXAG, S, ZP, ARROW = 0.004, 0.9, 0.084, 0.5, 1e-3, 0.3, 2.3, 1.6, 12, 3.0, 1.8, 0.62, 4.0   # 2 s of the lesson's gust at 1.6x slower; tilt drawn 3 times larger; 1 Nm drawn as 4 m
gust = lambda t: 0.1 if 0.5 <= t < 1.5 else 0.0
ctrls = {"pd": m.pd(KP, KD), "cascade": m.cascade(KP / KD, KD, KI)}
runs = {k: m.simulate(c, I, DT, 3.0, gust, lambda t: 0.0) for k, c in ctrls.items()}
sc = kit.setup(PRE / 24 + (TEND - T0) * SLOW + 1.0)
rigs = {}
for name, (colour, x0) in {"pd": ("blue", -0.8), "cascade": ("green", 0.8)}.items():
    root, props = kit.drone(name, colour)
    root.scale = (S, S, S)
    kit.cyl("stand", 0.04, ZP - 0.06, (x0, 0, (ZP - 0.06) / 2), "z", "grey")                  # test stand: the drone can only pitch
    kit.cyl("base", 0.16, 0.03, (x0, 0, 0.015), "z", "dark", bevel=0.01)
    kit.tube("level", [(x0 - 0.62, 0, ZP), (x0 + 0.62, 0, ZP)], 0.006, "grey")                 # the level line to compare against
    rigs[name] = (root, props, x0, kit.arrow("gust", "red"), kit.arrow("counter", "amber"))

for f in range(1, sc.frame_end + 1):
    i = int(round(min(T0 + max(f - 1 - PRE, 0) / 24 / SLOW, TEND) / DT))
    for name, (root, props, x0, gust_arrow, counter) in rigs.items():
        t, th, w, tau = runs[name]
        a = EXAG * float(th[i])
        tip = (x0 + 0.36 * math.cos(a), 0, ZP - 0.36 * math.sin(a))                              # the front arm tip
        kit.key(root, f, loc=(x0, 0, ZP), rot=(0, a, 0))
        for j, p in enumerate(props):
            kit.key(p, f, rot=(0, 0, (1 if j % 2 else -1) * 0.55 * f))
        g_len, c_len = ARROW * gust(t[i]), ARROW * max(-float(tau[i]), 0.0)                      # the push from the controller points up while tau < 0
        for ar, ln, z, rot in ((gust_arrow, g_len if f > PRE else 0, tip[2] + 0.12 + g_len, math.pi / 2), (counter, c_len, tip[2] - 0.12 - c_len, -math.pi / 2)):
            ar.scale = (ln, 2.2, 2.2) if ln > 1e-3 else (1e-4,) * 3                                  # a thicker shaft so it reads from the camera
            ar.keyframe_insert("scale", frame=f)
            kit.key(ar, f, loc=(tip[0], 0, z), rot=(0, rot, 0))
kit.camera((0, -3.1, 2.0), (0, 0, 0.62), lens=38)
kit.render(__file__)
