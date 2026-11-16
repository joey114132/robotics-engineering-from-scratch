# 레슨 04/02 클립: 같은 2 Nm 외력을 받는 팔 두 대. 파란 팔은 position 모드로 뻣뻣하고, 초록 팔은 torque 모드로 K=20 스프링처럼 밀린다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
DT, SECONDS, SLOW, SCALE, L, H = 1e-4, 2.5, 2.0, 5.0, 0.5, 0.75       # 2.5 s of the push, at half speed; deflection drawn 5 times larger
ARROW, THIN = 0.3, 0.7                                                  # the push arrow is 0.3 m long and slimmer than the kit's, so its head is not a squat cap
runs = {md: m.run(md, T=SECONDS, dt=DT)[1] for md in ("position", "torque")}

sc = kit.setup(SECONDS * SLOW)
kit.table((1.8, 0.7), 0.4)
rigs = {}
for md, x, colour in (("position", -0.62, "blue"), ("torque", 0.18, "green")):
    root, joints = kit.arm(md, (L,), colour, base_height=0.35)
    root.location = (x, 0, 0.4)
    kit.cyl("stand", 0.01, 0.35, (x + L + 0.17, 0, 0.5 + 0.075), "z", "dark")
    kit.ball("target", 0.03, (x + L + 0.17, 0, 0.76), "amber")    # the height the hand should keep
    rigs[md] = (x, joints, kit.arrow("push", "red"))
for md, (x, joints, arrow) in rigs.items():
    arrow.rotation_euler = (0, -math.pi / 2, 0)                      # a push straight up under the hand
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / sc.render.fps / SLOW
    i = min(int(t / DT), len(runs["torque"]) - 1)
    for md, (x, joints, arrow) in rigs.items():
        q = SCALE * runs[md][i]
        kit.pose(joints, f, [q])
        n = min(max((t - 0.5) / 0.1, 0.0), 1.0)                          # the push starts at 0.5 s and stays on
        tip = (x + (L + 0.085) * math.cos(q) + 0.055 * math.sin(q), H + (L + 0.085) * math.sin(q) - 0.055 * math.cos(q) - 0.004)   # the underside of the lower finger, following the hand
        kit.key(arrow, f, loc=(tip[0], 0, tip[1] - ARROW * n))             # the arrow's head touches the hand
        arrow.scale = (ARROW * n + 1e-4, THIN * n + 1e-4, THIN * n + 1e-4)   # before the push it is a point, not a flat disc
        arrow.keyframe_insert("scale", frame=f)
kit.camera((0.0, -2.5, 1.5), (0.0, 0, 0.7), lens=50)
kit.render(__file__)
