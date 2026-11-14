# 레슨 15/01 예시 클립: wrong sign 이면 파란 팔은 목표(주황 반투명 팔) 반대로 달려가고, 램프는 stop 에 닿기 전에 켜진다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import bpy
import kit

m = kit.lesson_main(__file__)
SIM_T, SLOW, HOLD = 0.6, 6.0, 1.0               # the first 0.6 s of the lesson's wrong-sign run at one sixth speed, then a short hold
runs = {f: m.simulate(f, T=SIM_T) for f in ("none", "wrong_sign")}
alarm = m.alarm_time(runs["wrong_sign"])        # 0.205 s; the true joint reaches the stop at 0.460 s

sc = kit.setup(SIM_T * SLOW + HOLD)
L, H = 0.5, 0.7
for name, x, colour, run in (("ok", -0.8, "green", runs["none"]), ("flipped", 0.8, "blue", runs["wrong_sign"])):
    root, (j,) = kit.arm(name, (L,), colour, base_height=H)
    root.location = (x, 0, 0)
    for s in (1, -1):                           # the hard stops at +-2 rad (m.P["q_lim"])
        a = s * m.P["q_lim"]
        kit.box(name + "-stop", (0.1, 0.1, 0.1), (x + (L + 0.1) * math.cos(a), 0, H + (L + 0.1) * math.sin(a)), "dark", bevel=0.01)
    tgt, (tj,) = kit.arm(name + "-target", (L,), colour, base_height=H)   # the target pose, q_ref = 1 rad, as a see-through arm
    tgt.location = (x, -0.1, 0)
    for ob in list(tgt.children_recursive):
        if "foot" in ob.name or "post" in ob.name:
            bpy.data.objects.remove(ob)
        elif ob.type == "MESH":
            ob.data.materials.clear()
            ob.data.materials.append(kit.ghost("amber", 0.4))
    kit.pose([tj], 1, [m.P["q_ref"]])
    lamp = kit.ball(name + "-alarm", 0.06, (x, 0, H + 0.2), "amber")
    for f in range(sc.frame_start, sc.frame_end + 1):
        i = min(int((f - 1) / sc.render.fps / SLOW / 1e-3), len(run) - 1)
        kit.key(j, f, rot=(0, -run[i, 1], 0))
        lamp.scale = ((1.0 if (name == "flipped" and run[i, 0] >= alarm) else 0.01),) * 3
        kit.key(lamp, f, loc=lamp.location)
        lamp.keyframe_insert("scale", frame=f)
kit.camera((0, -3.8, 1.9), (0, 0, 0.62), lens=44)
kit.render(__file__)
