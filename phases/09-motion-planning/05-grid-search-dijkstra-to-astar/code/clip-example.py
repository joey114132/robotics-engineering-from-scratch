# 레슨 09/05 예시 클립: 같은 칸 지도에서 w=4 로 과대추정한 탐색(파랑)은 95칸만 확장하고 36걸음 길을 찾아 늦게 닿고, A*(초록)는 115칸을 확장해 26걸음 길로 먼저 닿는다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
TRAP = ["...........#.....", ".....#.....#.....", ".....#.....#.....", ".....#.....#.....", ".....#.....#.....", "S....#.....#....G",   # the map of tests/ and figure.py
        ".....#.....#.....", ".....#.....#.....", ".....#.....#.....", ".....#.....#.....", "................."]
grid, start, goal = m.parse(TRAP)                                 # the lesson's trap map: two walls with gaps
C, FPS, RATE, T0, SECONDS, SPEED = 0.26, 24, 64.0, 0.3, 5.9, 13.0   # cell size in m; 64 cells expanded per second in both searches; both rovers drive 13 cells per second; 1 s hold at the end
RUNS = {"blue": (4.0, 1.55, "#9ec5f8"), "green": (1.0, -1.55, "#9fdcb8")}   # colour: (heuristic weight, lane y, tile colour)
at = lambda cell, y0: ((cell[1] - 8) * C, y0 + (5 - cell[0]) * C)


def appear(ob, frame):
    ob.hide_render = True
    ob.keyframe_insert("hide_render", frame=1)
    ob.hide_render = False
    ob.keyframe_insert("hide_render", frame=frame)


sc = kit.setup(SECONDS)
for colour, (wgt, y0, tile) in RUNS.items():
    path, expanded = m.search(grid, start, goal, wgt)             # w = 1 is A*, w = 4 guesses four times too much
    kit.stripe(-8.5 * C, 8.5 * C, y0 - 5.5 * C, y0 + 5.5 * C, "pearl")
    for r, c in zip(*grid.nonzero()):
        kit.box("wall", (C, C, 0.2), (*at((r, c), y0), 0.1), "dark", bevel=0.01)
    for i, cell in enumerate(expanded):
        appear(kit.box("seen", (0.9 * C, 0.9 * C, 0.012), (*at(cell, y0), 0.008), tile, bevel=0), int(1 + (T0 + i / RATE) * FPS))
    gx, gy = at(goal, y0)
    kit.cyl("goal-pole", 0.02, 0.5, (gx, gy, 0.25), "z", "amber")
    kit.ball("goal-flag", 0.11, (gx, gy, 0.5), "amber")
    rover, wheels = kit.rover("rover-" + colour, "navy" if colour == "blue" else colour)
    rover.scale = (0.9, 0.9, 0.9)
    t0 = T0 + len(expanded) / RATE + 0.1                          # it sets off when its own search has reached the goal
    pts = [at(c, y0) for c in path]
    yaw = 0.0
    for f in range(sc.frame_start, sc.frame_end + 1):
        s = min(max(((f - 1) / FPS - t0) * SPEED, 0.0), len(pts) - 1)     # path position in cells, same speed for both rovers
        k = min(int(s), len(pts) - 2)
        a, b = pts[k], pts[k + 1]
        pos = (a[0] + (s - k) * (b[0] - a[0]), a[1] + (s - k) * (b[1] - a[1]))
        yaw += max(-0.25, min(0.25, (math.atan2(b[1] - a[1], b[0] - a[0]) - yaw + math.pi) % (2 * math.pi) - math.pi))
        kit.key(rover, f, loc=(pos[0], pos[1], 0), rot=(0, 0, yaw))
        for wh in wheels:
            kit.key(wh, f, rot=(0, s * C / 0.0675, 0))
kit.camera((0, -8.4, 4.9), (0, -0.45, 0), lens=48)
kit.render(__file__)
