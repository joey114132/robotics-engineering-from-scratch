# 레슨 15/03 예시 클립: 목표 2.0 rad. 파란 팔은 controller 의 위치 한계 1.8 에 막혀 멈추고, 초록 팔은 세 계층이 모두 2.0 을 허용해 도착한다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import bpy
import kit

m = kit.lesson_main(__file__)
SIM_T, SLOW, HOLD, GOAL = 2.6, 1.5, 1.0, 2.0     # the lesson's loop for 2.6 s at 2/3 speed, then a short hold; the goal is 2.0 rad
M = m.MISMATCHED
blue = {n: {**M[n], "vel": 2.0} for n in m.LAYERS}                  # position limits as in MISMATCHED (2.2, 1.8, 2.0); speed limits matched so only position differs
green = {n: {**blue[n], "pos": 2.0} for n in m.LAYERS}               # every layer allows 2.0 rad
runs = {"blue": m.simulate(blue, goal=GOAL, T=SIM_T)["trace"], "green": m.simulate(green, goal=GOAL, T=SIM_T)["trace"]}   # columns: planner reference, joint

sc = kit.setup(SIM_T * SLOW + HOLD)
L, H = 0.5, 0.35
for name, x, colour in (("blue", -0.75, "blue"), ("green", 0.75, "green")):
    root, (j,) = kit.arm(name, (L,), colour, base_height=H)
    root.location = (x, 0, 0)
    ghost_root, (gj,) = kit.arm(name + "-plan", (L,), colour, base_height=H)     # where the planner thinks the joint is (the reference)
    ghost_root.location = (x, -0.1, 0)
    for ob in list(ghost_root.children_recursive):
        if "foot" in ob.name or "post" in ob.name:
            bpy.data.objects.remove(ob)
        elif ob.type == "MESH":
            ob.data.materials.clear()
            ob.data.materials.append(kit.ghost("dark", 0.4))
    r = L + 0.1                                  # the goal block sits where the hand is when the joint reaches 2.0 rad
    kit.box(name + "-goal", (0.06, 0.06, 0.06), (x + r * math.cos(GOAL), 0, H + r * math.sin(GOAL)), "amber", bevel=0.008)
    for f in range(sc.frame_start, sc.frame_end + 1):
        i = min(int((f - 1) / sc.render.fps / SLOW / 1e-3), len(runs[name]) - 1)
        kit.key(gj, f, rot=(0, -runs[name][i, 0], 0))
        kit.key(j, f, rot=(0, -runs[name][i, 1], 0))
kit.camera((0, -3.4, 2.1), (0, 0, 0.5), lens=46)
kit.render(__file__)
