# 레슨 15/03 클립: 같은 목표 1.4 rad, 같은 gain. 초록 관절은 한계가 맞아 있고, 파란 관절은 drive가 조용히 속도를 깎아 planner가 앞서간다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import bpy
import kit

m = kit.lesson_main(__file__)
SIM_T, SLOW, HOLD = 2.0, 2.5, 0.8               # the lesson's first 2 s, played at 0.4x, then a short hold
runs = {"aligned": m.simulate(m.ALIGNED, T=SIM_T)["trace"], "mismatched": m.simulate(m.MISMATCHED, T=SIM_T)["trace"]}   # columns: planner reference, joint

sc = kit.setup(SIM_T * SLOW + HOLD)
L, H = 0.5, 0.35
for name, x, colour in (("mismatched", -0.75, "blue"), ("aligned", 0.75, "green")):
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
    kit.box(name + "-goal", (0.05, 0.05, 0.05), (x + 0.58 * 0.17, 0, H + 0.58 * 0.985), "amber", bevel=0.008)   # the goal at 1.4 rad
    for f in range(sc.frame_start, sc.frame_end + 1):
        i = min(int((f - 1) / sc.render.fps / SLOW / 1e-3), len(runs[name]) - 1)
        kit.key(gj, f, rot=(0, -runs[name][i, 0], 0))
        kit.key(j, f, rot=(0, -runs[name][i, 1], 0))
kit.camera((0, -3.4, 2.1), (0, 0, 0.5), lens=46)
kit.render(__file__)
