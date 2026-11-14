# 레슨 15/02 클립: 명령이 끊긴 뒤 같은 watchdog이 두 관절을 세운다. 파란 관절은 토크만 끊고, 초록 관절은 ramp로 멈춘다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SIM_T, SLOW, HOLD = 1.2, 4.0, 0.9               # the lesson's first 1.2 s, played at quarter speed, then a short hold
runs = {mode: m.simulate(mode, T=SIM_T)["trace"] for mode in ("cut", "ramp")}   # speed 2 rad/s, command dies at 0.5 s, limit 1.5 rad
wd = m.Watchdog(0.05)                           # the lesson's default timeout; the last heartbeat comes at 0.49 s
wd.beat(0.49)
t_trip = next(i * 1e-3 for i in range(1200) if wd.tripped(i * 1e-3))

sc = kit.setup(SIM_T * SLOW + HOLD)
L, H = 0.5, 0.35
for name, x, colour in (("cut", -0.75, "blue"), ("ramp", 0.75, "green")):
    root, (j,) = kit.arm(name, (L,), colour, base_height=H)
    root.location = (x, 0, 0)
    a = 1.5                                      # the hard stop at q_lim = 1.5 rad
    kit.box(name + "-stop", (0.08, 0.08, 0.08), (x + (L + 0.06) * math.cos(a), 0, H + (L + 0.06) * math.sin(a)), "dark", bevel=0.01)
    lamp = kit.ball(name + "-trip", 0.06, (x - 0.22, 0, H + 0.15), "amber")     # the watchdog has tripped
    for f in range(sc.frame_start, sc.frame_end + 1):
        i = min(int((f - 1) / sc.render.fps / SLOW / 1e-3), len(runs[name]) - 1)
        kit.key(j, f, rot=(0, -runs[name][i, 1], 0))
        kit.key(lamp, f, loc=lamp.location)
        lamp.scale = ((1.0 if runs[name][i, 0] >= t_trip else 0.01),) * 3
        lamp.keyframe_insert("scale", frame=f)
kit.camera((0, -3.4, 2.1), (0, 0, 0.5), lens=46)
kit.render(__file__)
