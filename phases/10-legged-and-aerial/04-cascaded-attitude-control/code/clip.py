# 레슨 10/04 클립: 시험대에 얹은 쿼드로터 둘이 같은 1초 돌풍 토크를 맞는다. 파란 쪽은 단일 PD 라 기운 채 버티고 초록 쪽은 캐스케이드라 수평으로 돌아온다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
I, KP, KD, KI, DT, TEND, SLOW, PRE, EXAG, S, ZP = 0.004, 0.9, 0.084, 0.5, 1e-3, 3.0, 1.2, 12, 3.0, 1.8, 0.62   # tilt drawn 3 times larger
gust = lambda t: 0.1 if 0.5 <= t < 1.5 else 0.0
ctrls = {"pd": m.pd(KP, KD), "cascade": m.cascade(KP / KD, KD, KI)}
runs = {k: m.simulate(c, I, DT, TEND, gust, lambda t: 0.0) for k, c in ctrls.items()}
sc = kit.setup(PRE / 24 + TEND * SLOW + 1.0)
rigs = {}
for name, (colour, x0) in {"pd": ("blue", -0.8), "cascade": ("green", 0.8)}.items():
    root, props = kit.drone(name, colour)
    root.scale = (S, S, S)
    kit.cyl("stand", 0.04, ZP - 0.06, (x0, 0, (ZP - 0.06) / 2), "z", "grey")                  # test stand: the drone can only pitch
    kit.cyl("base", 0.16, 0.03, (x0, 0, 0.015), "z", "dark", bevel=0.01)
    kit.tube("level", [(x0 - 0.62, 0, ZP), (x0 + 0.62, 0, ZP)], 0.006, "grey")                 # the level line to compare against
    rigs[name] = (root, props, x0, kit.arrow("gust", "red"))

for f in range(1, sc.frame_end + 1):
    i = int(round(min(max(f - 1 - PRE, 0) / 24 / SLOW, TEND) / DT))
    for name, (root, props, x0, arrow) in rigs.items():
        t, th, w, tau = runs[name]
        a = EXAG * float(th[i])
        kit.key(root, f, loc=(x0, 0, ZP), rot=(0, a, 0))
        for j, p in enumerate(props):
            kit.key(p, f, rot=(0, 0, (1 if j % 2 else -1) * 0.55 * f))
        on = gust(t[i]) > 0 and f > PRE
        arrow.scale = (0.4 if on else 1e-4,) * 3
        arrow.keyframe_insert("scale", frame=f)
        kit.key(arrow, f, loc=(x0 + 0.36 * math.cos(a), 0, ZP - 0.36 * math.sin(a) + 0.12 + 0.4), rot=(0, math.pi / 2, 0))   # pushes the front arm down
kit.camera((0, -3.4, 2.2), (0, 0, 0.62), lens=38)
kit.render(__file__)
