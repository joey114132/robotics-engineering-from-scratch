# 레슨 01/01 클립: 같은 두 번의 90도 회전을 순서만 바꿔 한 드론은 roll 후 yaw, 다른 드론은 yaw 후 roll 로 돈다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit
from mathutils import Matrix

m = kit.lesson_main(__file__)
SECONDS, FPS = 5.0, 24
sc = kit.setup(SECONDS)
kit.camera((-1.7, -2.9, 2.7), (0.0, 0.0, 1.3), lens=34)


def ease(s):
    s = min(max(s, 0.0), 1.0)
    return s * s * (3 - 2 * s)


def turn(f, t0, t1):        # 0 to 90 degrees between seconds t0 and t1
    return ease((f / FPS - t0) / (t1 - t0)) * math.pi / 2


def drone(name, colour, x, y):
    root, props = kit.drone(name, colour)
    root.scale = (2.3,) * 3
    kit.cyl(name + "-rod", 0.008, 0.3, (0.17, 0, 0), "x", "dark", parent=root)
    kit.ball(name + "-point", 0.036, (0.34, 0, 0), "amber", parent=root)       # the point (1, 0, 0) carried by the pose
    root.rotation_mode = "QUATERNION"
    return root, props, (x, y, 1.4)


# green: x first, then z.  blue: the same two turns, z first, then x.
fleet = {"green": (drone("ok", "green", -0.62, 0.62), lambda a, b: m.rot_z(b) @ m.rot_x(math.pi / 2) if a >= math.pi / 2 else m.rot_x(a)),
         "blue": (drone("swapped", "blue", 0.62, -0.62), lambda a, b: m.rot_x(b) @ m.rot_z(math.pi / 2) if a >= math.pi / 2 else m.rot_z(a))}
last = {}
for f in range(sc.frame_start, sc.frame_end + 1):
    a, b = turn(f, 0.6, 1.9), turn(f, 2.5, 3.8)
    for k, ((root, props, p), order) in fleet.items():
        R = order(a, b)
        T = m.make_T(R, p)
        assert m.is_rotation(T[:3, :3])
        q = Matrix(T[:3, :3].tolist()).to_quaternion()
        if k in last and q.dot(last[k]) < 0:
            q.negate()
        last[k] = q
        root.location = T[:3, 3]
        root.rotation_quaternion = q
        root.keyframe_insert("location", frame=f)
        root.keyframe_insert("rotation_quaternion", frame=f)
        for i, pr in enumerate(props):
            kit.key(pr, f, rot=(0, 0, (-1) ** i * f * 1.6))
kit.render(__file__)
