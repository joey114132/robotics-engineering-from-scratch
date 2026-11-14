# 레슨 05/06 예시 클립: 회색 유령은 buffer 에 저장된 pose 두 개, 호박색 유령은 0.5 초의 보간 답, 빨간 십자는 최신 sample 보다 뒤라 거부당한 1.5 초 질의
import pathlib
import sys

import bpy
import numpy as np

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
V, W, SLOW, END, S = 1.2, 1.0, 3.2, 1.5, 1.3                         # 1.2 m/s forward, 1 rad/s turning, played 3.2x slower; rovers drawn 1.3x for size
pose = lambda t: (np.array([V * t, 0.0, 0.0]), np.array([np.cos(W * t / 2), 0, 0, np.sin(W * t / 2)]))
yaw = lambda q: 2 * np.arctan2(q[3], q[0])
buf = m.PoseBuffer()
for t in (0.0, 1.0):                                                # two stored samples
    buf.add(t, *pose(t))
p, q = buf.lookup(0.5)                                              # between them: lerp + slerp
assert np.allclose(p, pose(0.5)[0]) and abs(yaw(q) - 0.5) < 1e-9  # the buffer's answer matches the rover's real pose
try:
    buf.lookup(END)
    raise SystemExit("the lesson's buffer must refuse a time after its newest sample")
except LookupError:
    pass
fr = lambda t: int(round(t * SLOW * 24)) + 1


def ghost_rover(name, colour, alpha, at, t):
    """A see-through copy of the rover at pose `at` = (position, yaw) that pops in at lesson time t."""
    root, _ = kit.rover(name, "grey")
    root.scale = (S,) * 3
    for ob in root.children_recursive:
        if ob.type == "MESH":
            ob.data.materials.clear()
            ob.data.materials.append(kit.ghost(colour, alpha))
    kit.key(root, 1, loc=(at[0][0], at[0][1], -1.0), rot=(0, 0, at[1]))
    kit.key(root, fr(t) - 1, loc=(at[0][0], at[0][1], -1.0), rot=(0, 0, at[1]))
    kit.key(root, fr(t), loc=(at[0][0], at[0][1], 0.0), rot=(0, 0, at[1]))


sc = kit.setup(END * SLOW + 0.9)
truth, wheels = kit.rover("rover", "blue")
truth.scale = (S,) * 3
for f in range(sc.frame_start, sc.frame_end + 1):
    t = min((f - 1) / 24 / SLOW, END)
    kit.drive(truth, wheels, f, V * t, 0, W * t, radius=0.075 * S)
for i, t in enumerate((0.0, 1.0)):                                  # the stored samples, as grey ghosts the moment they arrive
    ghost_rover(f"sample{i}", "grey", 0.6, (pose(t)[0], yaw(pose(t)[1])), t)
ghost_rover("answer", "amber", 0.85, (p, yaw(q)), 1.05)             # asked for 0.5 s once the newest sample (1.0 s) is in
x = V * END                                                         # asked for 1.5 s: refused, shown as a red cross floating over the spot the rover will reach
cross = [kit.box("cross", (0.5, 0.04, 0.04), (x, 0, -1.0), "red", bevel=0.005) for _ in range(2)]
for c, ang in zip(cross, (0.785398, -0.785398)):
    kit.key(c, 1, loc=(x, 0, -1.0), rot=(0, ang, 0))
    kit.key(c, fr(1.1) - 1, loc=(x, 0, -1.0), rot=(0, ang, 0))
    kit.key(c, fr(1.1), loc=(x, 0, 0.75), rot=(0, ang, 0))
kit.camera((0.9, -3.0, 1.9), (0.9, 0.0, 0.2), lens=42)
kit.render(__file__)
