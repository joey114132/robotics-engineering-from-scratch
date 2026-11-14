# 레슨 15/01 클립: 같은 PD 루프의 관절 두 개. 초록은 정상, 파란 관절은 0.3초에 센서가 멈추고 hard stop으로 걸어간다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import bpy
import kit

m = kit.lesson_main(__file__)
SIM_T, SLOW, HOLD = 1.6, 3.0, 0.9               # the lesson's first 1.6 s, played at 1/3 speed, then a short hold
runs = {f: m.simulate(f, T=SIM_T) for f in ("none", "stuck")}
alarm = m.alarm_time(runs["stuck"])             # first time a cheap check trips (0.35 s)

sc = kit.setup(SIM_T * SLOW + HOLD)
L, H = 0.5, 0.7                                 # link length and pedestal height; 1 rad of joint angle is drawn as 1 rad
for name, x, colour, run in (("ok", -0.8, "green", runs["none"]), ("stuck", 0.8, "blue", runs["stuck"])):
    root, (j,) = kit.arm(name, (L,), colour, base_height=H)
    root.location = (x, 0, 0)
    for s in (1, -1):                           # the hard stops at +-2 rad (m.P["q_lim"])
        a = s * m.P["q_lim"]
        kit.box(name + "-stop", (0.1, 0.1, 0.1), (x + (L + 0.1) * math.cos(a), 0, H + (L + 0.1) * math.sin(a)), "dark", bevel=0.01)
    gj = None
    if name == "stuck":                         # a see-through copy shows what the controller believes (the sensor reading)
        ghost_root, (gj,) = kit.arm(name + "-belief", (L,), colour, base_height=H)
        ghost_root.location = (x, -0.1, 0)
        for ob in list(ghost_root.children_recursive):
            if "foot" in ob.name or "post" in ob.name:
                bpy.data.objects.remove(ob)
            elif ob.type == "MESH":
                ob.data.materials.clear()
                ob.data.materials.append(kit.ghost("dark", 0.4))
    lamp = kit.ball(name + "-alarm", 0.06, (x, 0, H + 0.2), "amber")
    for f in range(sc.frame_start, sc.frame_end + 1):
        i = min(int((f - 1) / sc.render.fps / SLOW / 1e-3), len(run) - 1)
        kit.key(j, f, rot=(0, -run[i, 1], 0))
        if gj:
            kit.key(gj, f, rot=(0, -run[i, 4], 0))
        s = 1.0 if (name == "stuck" and run[i, 0] >= alarm) else 0.01
        kit.key(lamp, f, loc=lamp.location)
        lamp.scale = (s,) * 3
        lamp.keyframe_insert("scale", frame=f)
kit.camera((0, -3.8, 1.9), (0, 0, 0.62), lens=44)
kit.render(__file__)
