# 레슨 06/01 클립: 스탠드 위 카메라가 컵 가장자리 픽셀의 광선을 보고, 뒤쪽 벽의 깊이를 읽으면 점이 광선을 따라 미끄러져 팔이 옆으로 빗나간다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
K = dict(fx=600.0, fy=600.0, cx=320.0, cy=240.0)
LENS = (0.0, 0.0, 0.55)                                   # camera-frame z is world +x, camera x is world -y
world = lambda p: (LENS[0] + p[2], LENS[1] - p[0], LENS[2] - p[1])
good = world(m.unproject([[520.0, 240.0]], 1.0, **K)[0])   # the pixel on the cup rim, depth of the rim
bad = world(m.unproject([[520.0, 240.0]], 1.15, **K)[0])   # the same pixel, depth of the wall 0.15 m behind
sc = kit.setup(5)

kit.table((0.8, 0.7), 0.45, (1.05, -0.3))
kit.box("wall", (0.04, 0.8, 0.6), (1.17, -0.3, 0.75), "pearl", bevel=0.01)
kit.cyl("cup", 0.045, 0.1, (good[0], good[1], 0.5), "z", "sky", bevel=0.01)
kit.cyl("stand", 0.02, 0.5, (0, 0, 0.25), "z", "grey")
kit.cyl("foot", 0.15, 0.02, (0, 0, 0.01), "z", "dark", bevel=0.008)
kit.box("cam", (0.14, 0.1, 0.08), (-0.02, 0, 0.55), "dark", bevel=0.015)
kit.cyl("lens", 0.032, 0.06, (0.08, 0, 0.55), "x", "grey")
kit.tube("ray", [LENS, (bad[0] + 0.02, bad[1] * 1.02, bad[2])], 0.006, "dark")
kit.ball("target", 0.022, good, "amber")
est = kit.ball("estimate", 0.03, good, "blue")

def ik(x, z, l1=0.4, l2=0.51):                            # fingertip target in the arm plane; the hand adds 0.11 to link 2
    d = min(math.hypot(x, z), l1 + l2 - 1e-3)
    q1 = -math.acos((d * d - l1 * l1 - l2 * l2) / (2 * l1 * l2))
    return math.atan2(z, x) - math.atan2(l2 * math.sin(q1), l1 + l2 * math.cos(q1)), q1

base = (0.72, bad[1], 0.45)
root, joints = kit.arm("arm", base_height=0.3)
root.location = base
reach = lambda p: ik(p[0] - base[0], p[2] - base[2] - 0.3)
kit.pose(joints, 1, reach((0.9, 0, 0.95))); kit.pose(joints, 36, reach((0.9, 0, 0.95)))
kit.pose(joints, 100, reach(bad)); kit.pose(joints, 120, reach(bad))
kit.key(est, 1, loc=good); kit.key(est, 30, loc=good); kit.key(est, 80, loc=bad); kit.key(est, 120, loc=bad)
kit.camera((-0.5, 2.5, 1.6), (0.62, -0.3, 0.64), lens=44)
kit.render(__file__)
