# 레슨 12/03 예시 클립: 같은 실제 관절을 두 가지로 가진한다. 왼쪽은 속도가 거의 일정한 느린 기록, 오른쪽은 속도가 오르내리고 방향이 바뀌는 풍부한 기록
import pathlib
import sys

import bpy

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS = 4.8                                                         # the first 4.8 s of each 20 s recording, real time
q = {a: m.experiment(a)[:, 2] for a in (0.0, 1.0)}                    # the lesson's slow run (a=0) and rich run (a=1) on the true joint

sc = kit.setup(SECONDS)
kit.box("wall", (4.8, 0.05, 1.7), (0, 0.16, 0.85), kit.mat("floor", rough=0.9, emit=0.2), bevel=0.01)


def joint(name, x, colour):
    root, (j,) = kit.arm(name, (0.4,), colour)
    for o in list(root.children):                                     # a pendulum that hangs from its motor, no pedestal
        if o.name.startswith((name + "-foot", name + "-post")):
            bpy.data.objects.remove(o)
    root.location = (x, 0.0, 0.65)
    return j


rigs = {0.0: joint("slow", -0.5, "blue"), 1.0: joint("rich", 0.5, "green")}
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / m.DT), len(q[0.0]) - 1)
    for a, j in rigs.items():
        kit.pose([j], f, [q[a][i] - 1.5708])                          # q is measured from hanging straight down
kit.camera((0, -2.7, 1.55), (0, 0, 0.95), lens=38)
kit.render(__file__)
