# 레슨 15/02 예시 클립: 같은 ramp 정지인데 timeout 이 0.05초인 초록 팔은 stop 앞에서 서고, 0.2초인 파란 팔은 stop 에 부딪힌다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
T0, SIM_T, SLOW, HOLD = 0.3, 1.0, 5.0, 1.0       # the lesson run from 0.3 s to 1.0 s at one fifth speed (the source dies at 0.5 s), then a short hold
cases = (("late", -0.75, "blue", 0.2), ("fits", 0.75, "green", 0.05))   # watchdog timeout in s; the worked example's 0.2 s and 0.05 s
runs, trips = {}, {}
for name, _, _, timeout in cases:
    runs[name] = m.simulate("ramp", timeout=timeout, T=SIM_T)["trace"]
    wd = m.Watchdog(timeout)
    wd.beat(0.49)                                # the last heartbeat before the source dies
    trips[name] = next(i * 1e-3 for i in range(int(SIM_T * 1000)) if wd.tripped(i * 1e-3))

sc = kit.setup((SIM_T - T0) * SLOW + HOLD)
L, H = 0.5, 0.35
for name, x, colour, _ in cases:
    root, (j,) = kit.arm(name, (L,), colour, base_height=H)
    root.location = (x, 0, 0)
    a = 1.5                                      # the hard stop at q_lim = 1.5 rad (simulate's default)
    kit.box(name + "-stop", (0.08, 0.08, 0.08), (x + (L + 0.06) * math.cos(a), 0, H + (L + 0.06) * math.sin(a)), "dark", bevel=0.01)
    lamp = kit.ball(name + "-trip", 0.06, (x - 0.22, 0, H + 0.15), "amber")     # the watchdog has tripped
    for f in range(sc.frame_start, sc.frame_end + 1):
        t = T0 + (f - 1) / sc.render.fps / SLOW
        i = min(int(t / 1e-3), len(runs[name]) - 1)
        kit.key(j, f, rot=(0, -runs[name][i, 1], 0))
        kit.key(lamp, f, loc=lamp.location)
        lamp.scale = ((1.0 if t >= trips[name] else 0.01),) * 3
        lamp.keyframe_insert("scale", frame=f)
kit.camera((0, -3.4, 2.1), (0, 0, 0.5), lens=46)
kit.render(__file__)
