# 레슨 08/06 클립: 표류하는 오도메트리로 5 m 정사각형을 돈 로버가 루프 폐쇄 간선으로 출발점에 되감긴다
import pathlib
import sys

import bpy
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
truth, edges, X0 = m.world(np.random.default_rng(0))             # the lesson's world: 21 poses, a heading bias of 0.02 rad every step
X, _ = m.solve(X0, edges)                                         # Gauss-Newton with the loop-closure edge
yaw0, yaw1 = np.unwrap(X0[:, 2]), np.unwrap(X[:, 2])
T0, T1, T2 = 62, 78, 108                                         # drive ends, closure edge drawn, graph relaxed

sc = kit.setup(T2 / 24 + 1.0)
bpy.context.preferences.edit.keyframe_new_interpolation_type = "LINEAR"
kit.stripe(-2.0, 7.0, -2.0, 7.0, "road")
kit.tube("truth", [(x, y, 0.01) for x, y in truth[:, :2]], 0.03, "white")     # the path the rover really drove
root, wheels = kit.rover("rover", "blue")
root.scale = (1.5,) * 3
old = [kit.ball("odo", 0.09, (0, 0, 0.1), "blue") for _ in X0]
new = [kit.ball("fix", 0.09, (0, 0, 0.1), "green") for _ in X0]
bar = kit.box("closure", (1.0, 0.07, 0.05), (0, 0, 0.06), "amber", bevel=0.01)


def size(ob, frame, v):
    ob.scale = (v,) * 3
    ob.keyframe_insert("scale", frame=frame)


for k in range(len(X0)):                                          # drive: one pose every 3 frames, dropping a blue node at each
    f = 1 + 3 * k
    kit.key(root, f, loc=(*X0[k, :2], 0), rot=(0, 0, yaw0[k]))
    for ob in (old[k], new[k]):
        kit.key(ob, 1, loc=(*X0[k, :2], 0.1))
        kit.key(ob, T1, loc=(*X0[k, :2], 0.1))
        kit.key(ob, T2, loc=(*X[k, :2], 0.1))                    # relax: every node slides to its corrected pose
    size(old[k], max(f - 1, 1), 0 if k else 1)
    for fr, v in ((f, 1), (T1, 1), (T2, 0)):
        size(old[k], fr, v)
    for fr, v in ((1, 0), (T1, 0), (T2, 1)):
        size(new[k], fr, v)
kit.key(root, T1, loc=(*X0[-1, :2], 0), rot=(0, 0, yaw0[-1]))
kit.key(root, T2, loc=(*X[-1, :2], 0), rot=(0, 0, yaw1[-1]))
for f, end in ((T0, X0[-1, :2]), (T1, X0[-1, :2]), (T2, X[-1, :2])):   # the loop-closure edge: start to the believed end
    v = end - X0[0, :2]
    bar.location, bar.rotation_euler = (*(X0[0, :2] + (0 if f == T0 else v / 2)), 0.06), (0, 0, float(np.arctan2(v[1], v[0])))
    bar.scale = (0 if f == T0 else max(float(np.hypot(*v)), 1e-3), 1, 1)
    for p in ("location", "rotation_euler", "scale"):
        bar.keyframe_insert(p, frame=f)
kit.camera((2.5, -0.6, 10.0), (2.5, 2.3, 0.0), lens=28)
kit.render(__file__)
