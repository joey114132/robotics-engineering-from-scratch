# 레슨 00/05 클립: 드론이 제자리에서 yaw 로 도는 동안, 기체 앞의 표식이 main.py 의 rotate() 로 계산한 자리를 따라 원을 그린다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, HEIGHT, TURN, REACH = 5.0, 0.55, math.radians(150), 0.62

sc = kit.setup(SECONDS)
fps = sc.render.fps
drone, props = kit.drone("drone", "green")
drone.location = (0, 0, HEIGHT)
kit.box("nose", (0.07, 0.06, 0.05), (0.095, 0, 0.005), "amber", bevel=0.01, parent=drone)   # marks the front of the drone
kit.ball("start-mark", 0.05, (REACH, 0, HEIGHT), kit.ghost("amber", 0.5))   # where the marker was before the turn
marker = kit.ball("marker", 0.05, (REACH, 0, HEIGHT), "amber")
for f in range(sc.frame_start, sc.frame_end + 1):
    t = (f - 1) / fps
    u = min(max((t - 0.4) / 3.8, 0.0), 1.0)
    yaw = TURN * (3 * u * u - 2 * u**3)                       # eases in and out
    kit.key(drone, f, rot=(0, 0, yaw))
    x, y = m.rotate((REACH, 0.0), yaw)                        # the marker's new place, from the lesson's own function
    kit.key(marker, f, loc=(x, y, HEIGHT))
    for i, p in enumerate(props):
        kit.key(p, f, rot=(0, 0, (1 if i % 2 else -1) * t * 60))
kit.camera((0.0, -1.8, 2.1), (0, 0, 0.45), lens=38)
kit.render(__file__)
