# 레슨 10/02 클립: 같은 보행자 둘이 deadbeat 걸음(초록)과 40% 짧은 걸음(파랑)으로 걷는다. 파랑은 몸이 발을 앞질러 속도가 계속 는다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
T, H, VT, N, SLOW, PRE = 0.4, 0.9, 0.6, 5, 2.0, 7                  # the lesson's walk, five steps, played at half speed after a short stand
sc = kit.setup(PRE / 24 + N * T * SLOW + 1.0)
walkers = {}
for scale, (colour, y) in {0.6: ("blue", 0.55), 1.0: ("green", -0.55)}.items():
    r = m.walk(N, T, H, VT, step_scale=scale, x0=-0.05, v0=0.3)
    st = list(zip([-0.05] + list(r["x_end"][:-1]), [0.3] + list(r["v_end"][:-1])))      # body state at the start of each step
    pel = kit.box("pelvis", (0.16, 0.3, 0.14), (0, 0, 0), colour, bevel=0.04)
    kit.box("torso", (0.14, 0.26, 0.3), (0, 0, 0.22), colour, bevel=0.04, parent=pel)
    kit.ball("head", 0.08, (0, 0, 0.45), "pearl", parent=pel)
    legs = [kit.empty("leg") for _ in (0, 1)]
    for lg in legs:
        kit.cyl("bone", 0.035, 1.0, (0.5, 0, 0), "x", "dark", parent=lg, segments=20)
    feet = [kit.box("foot", (0.12, 0.08, 0.04), (0, 0, 0), "dark", bevel=0.01) for _ in (0, 1)]
    for i, p in enumerate(r["feet"][1:], 1):
        kit.box("mark", (0.12, 0.09, 0.006), (p, y + (0.09, -0.09)[i % 2], 0.003), kit.ghost("amber", 0.55), bevel=0)   # planned footfalls
    walkers[scale] = (y, r, st, pel, legs, feet)

for f in range(1, sc.frame_end + 1):
    t = min(max(f - 1 - PRE, 0) / 24 / SLOW, N * T)
    k = min(int(t / T), N - 1)
    s = (t - k * T) / T
    for scale, (y, r, st, pel, legs, feet) in walkers.items():
        fp = r["feet"]
        x = float(m.lipm_state(st[k][0], st[k][1], fp[k], s * T, H)[0])
        sw = fp[max(k - 1, 0)] + (fp[k + 1] - fp[max(k - 1, 0)]) * (3 * s * s - 2 * s ** 3)     # the swing foot goes from the last footfall to the next one
        fx = {k % 2: (fp[k], 0.0), 1 - k % 2: (sw, 0.12 * math.sin(math.pi * s))}
        kit.key(pel, f, loc=(x, y, H))
        for j, dy in enumerate((0.09, -0.09)):
            a, b = (fx[j][0], y + dy, fx[j][1] + 0.04), (x, y + dy, H - 0.05)
            legs[j].scale = (math.hypot(b[0] - a[0], b[2] - a[2]), 1, 1)
            legs[j].keyframe_insert("scale", frame=f)
            kit.key(legs[j], f, loc=a, rot=(0, -math.atan2(b[2] - a[2], b[0] - a[0]), 0))
            kit.key(feet[j], f, loc=(a[0], y + dy, fx[j][1] + 0.02))
kit.camera((1.3, -4.0, 2.7), (1.3, 0.0, 0.55), lens=38)
kit.render(__file__)
