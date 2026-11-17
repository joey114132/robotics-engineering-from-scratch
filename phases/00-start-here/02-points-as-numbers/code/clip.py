# 레슨 00/02 클립: 바닥에 표시한 세 점 A, B, C 를 로봇이 차례로 찾아가며 지나간다. 점 좌표는 레슨의 ROUTE 그대로다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, PAUSE, TURN = 6.0, 0.4, 0.4          # seconds of clip, rest at each spot, time spent turning toward the next spot
SPEED = 1.0                                   # metres per second along a leg
legs = list(zip(m.ROUTE, m.ROUTE[1:]))
yaws = [math.atan2(b[1] - a[1], b[0] - a[0]) for a, b in legs]
t_leg = [m.distance(a, b) / SPEED for a, b in legs]


def state(t):
    """Where the rover is and which way it faces, at clip time t."""
    t -= PAUSE
    for k, (a, b) in enumerate(legs):
        if t < TURN:                          # turning on the spot
            prev = yaws[k - 1] if k else yaws[0]
            s = max(t, 0) / TURN
            return a, prev + (yaws[k] - prev) * (3 * s * s - 2 * s ** 3)
        t -= TURN
        if t < t_leg[k]:
            return m.lerp(a, b, t / t_leg[k]), yaws[k]
        t -= t_leg[k] + PAUSE
    return legs[-1][1], yaws[-1]


sc = kit.setup(SECONDS)
kit.stripe(-0.8, 3.2, -0.7, 2.3, "road")
for p in m.ROUTE:
    kit.cyl("mark", 0.11, 0.012, (p[0], p[1], 0.008), "z", "amber")
kit.cyl("mark-ring", 0.16, 0.006, (0, 0, 0.004), "z", "white")
rover, wheels = kit.rover("rover", "green")
for f in range(sc.frame_start, sc.frame_end + 1):
    (x, y), yaw = state((f - 1) / sc.render.fps)
    kit.key(rover, f, loc=(x, y, 0), rot=(0, 0, yaw))
    for w in wheels:
        kit.key(w, f, rot=(0, (x + y) / 0.075, 0))
kit.camera((1.0, -3.3, 3.6), (1.0, 0.75, 0.0), lens=35)
kit.render(__file__)
