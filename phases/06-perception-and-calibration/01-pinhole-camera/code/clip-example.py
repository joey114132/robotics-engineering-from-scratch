# 레슨 06/01 예시 클립: 같은 0.15 m depth 실수를 컵 두 개에 적용한다. 카메라 중심선 위의 컵은 점이 뒤로만 밀리고, 가장자리 픽셀의 컵은 뒤로 밀리면서 옆으로 5 cm 어긋난다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
K = dict(fx=600.0, fy=600.0, cx=320.0, cy=240.0)
LENS = (0.0, 0.0, 0.55)                                   # camera-frame z is world +x, camera x is world -y
world = lambda p: (LENS[0] + p[2], LENS[1] - p[0], LENS[2] - p[1])
cups = {}
for name, u in (("centre", 320.0), ("edge", 520.0)):      # one cup on the camera's centre line, one at pixel column 520
    cups[name] = [world(m.unproject([[u, 240.0]], z, **K)[0]) for z in (1.0, 1.15)]   # depth of the rim, depth of the wall behind
sc = kit.setup(5)

kit.table((0.5, 0.9), 0.45, (0.9, -0.17))
kit.box("wall", (0.04, 0.9, 0.6), (1.19, -0.17, 0.75), "pearl", bevel=0.01)
kit.cyl("stand", 0.02, 0.5, (0, 0, 0.25), "z", "grey")
kit.cyl("foot", 0.15, 0.02, (0, 0, 0.01), "z", "dark", bevel=0.008)
kit.box("cam", (0.14, 0.1, 0.08), (-0.02, 0, 0.55), "dark", bevel=0.015)
kit.cyl("lens", 0.032, 0.06, (0.08, 0, 0.55), "x", "grey")
for name, (near, far) in cups.items():
    kit.cyl("cup-" + name, 0.045, 0.1, (near[0], near[1], 0.5), "z", "sky", bevel=0.01)
    kit.tube("ray-" + name, [LENS, (far[0] + 0.02, far[1] * 1.02, far[2])], 0.006, "dark")
    kit.ball("right-" + name, 0.022, near, "green")
    est = kit.ball("wrong-" + name, 0.03, near, "blue")
    kit.key(est, 1, loc=near); kit.key(est, 30, loc=near); kit.key(est, 90, loc=far); kit.key(est, 120, loc=far)
kit.camera((0.6, -0.17, 1.95), (0.6, -0.17, 0.45), lens=30)
kit.render(__file__)
