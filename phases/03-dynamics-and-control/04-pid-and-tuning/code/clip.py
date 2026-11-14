# 레슨 03/04 클립: 같은 PID로 정지선까지 가는 장난감 자동차 두 대. 파란 차는 anti-windup 없음, 초록 차는 있음
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
DT, SECONDS, SLOW = 0.001, 2.5, 2.0          # the first 2.5 s of the lesson's windup case, played at half speed
runs = {aw: m.simulate(1.0, 2.0, 100.0, 300.0, 20.0, DT, int(SECONDS / DT), q_des=2.0, umax=20.0, anti_windup=aw) for aw in (False, True)}

sc = kit.setup(SECONDS * SLOW)
kit.stripe(-1.0, 4.6, -0.75, 0.75, "road")                      # the road: 1 unit is the lesson's 1 rad drawn as 1 m
for x in [i * 0.5 - 0.75 for i in range(11)]:
    kit.stripe(x, x + 0.22, -0.02, 0.02, "white", z=0.004)       # centre dashes
kit.stripe(1.97, 2.03, -0.75, 0.75, "white", z=0.004)            # the stop line at 2 m
kit.box("post", (0.04, 0.04, 0.6), (2.0, 0.86, 0.3), "dark", bevel=0)
kit.cyl("sign", 0.17, 0.03, (2.0, 0.84, 0.68), "y", "red", segments=8)   # a stop sign facing the camera

cars = {False: kit.car("plain", "blue"), True: kit.car("clamped", "green")}
for f in range(sc.frame_start, sc.frame_end + 1):
    i = min(int((f - 1) / sc.render.fps / SLOW / DT), runs[True].shape[1] - 1)
    for aw, (root, wheels, _) in cars.items():
        kit.drive(root, wheels, f, runs[aw][0, i] - 0.3, y=-0.38 if aw else 0.38)   # the nose is the measured point
kit.camera((1.6, -4.5, 3.0), (1.6, 0.05, 0.1), lens=35)   # wide enough for the start at -0.6 and the overshoot past 3.5
kit.render(__file__)
