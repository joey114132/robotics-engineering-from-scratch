# 레슨 00/01 클립: 같은 센서 값 0~90을 도로 읽는 팔(초록)과 라디안으로 잘못 읽는 팔(파랑)이 링크를 세운다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, HOLD, STEP = 5.0, 0.4, 0.65     # each reading arrives STEP s after the last and is held for HOLD s
readings = [float(r) for r in range(0, 91, 15)]            # the encoder says 0, 15, ... 90

def wrap(a):                                               # a whole turn looks the same, so draw the angle in -pi..pi
    return (a + math.pi) % (2 * math.pi) - math.pi

right = [float(m.joint_angles(m.deg2rad([r]))[0]) for r in readings]   # degrees converted first
wrong = [wrap(r) for r in readings]                                    # the same numbers read as radians (what np.cos sees)

sc = kit.setup(SECONDS)
fps = sc.render.fps
arms = {}
for name, x, colour in (("wrong", -0.6, "blue"), ("right", 0.6, "green")):
    root, joints = kit.arm(name, (0.4, 0.06), colour, base_height=0.62)
    root.location = (x, 0, 0)
    joints[0].location.y = -0.14                        # shoulder beside the post, so a link pointing down swings clear of it
    kit.box(name + "-bracket", (0.1, 0.17, 0.09), (0, -0.07, 0.62), "dark", bevel=0.01, parent=root)
    arms[name] = joints
for i, (a, b) in enumerate(zip(wrong, right)):
    f0 = 1 + int((0.2 + i * STEP) * fps)       # arrive at reading i, then hold
    for name, q in (("wrong", a), ("right", b)):
        kit.pose(arms[name], f0, [q, 0.0])
        kit.pose(arms[name], f0 + int(HOLD * fps), [q, 0.0])
kit.pose(arms["wrong"], 1, [wrong[0], 0.0])
kit.pose(arms["right"], 1, [right[0], 0.0])
kit.camera((0, -2.85, 2.1), (0, 0, 0.5), lens=42)
kit.render(__file__)
