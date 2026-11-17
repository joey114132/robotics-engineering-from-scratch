# 레슨 00/03 클립: 벤치 팔의 관절이 사분의 일 바퀴(90도, 약 1.57 라디안)만큼 돈다. 호박색 막대는 출발선과 끝선
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, GO, TURN = 4.5, 0.6, 2.6                 # clip length, wait before the turn, time the turn takes
target = m.deg_to_rad(90)                         # a quarter turn, in the radians that code uses

sc = kit.setup(SECONDS)
root, joints = kit.arm("arm", (0.5,), "green", base_height=0.45)
joints[0].location.y = -0.14
kit.box("arm-bracket", (0.1, 0.17, 0.09), (0, -0.07, 0.45), "dark", bevel=0.01, parent=root)
ghost = kit.ghost("amber", 0.7)
kit.box("line-start", (0.62, 0.02, 0.02), (0.31, -0.32, 0.45), ghost, bevel=0)     # where the turn starts
kit.box("line-end", (0.02, 0.02, 0.62), (0.0, -0.32, 0.45 + 0.31), ghost, bevel=0)  # a quarter turn later
for f in range(sc.frame_start, sc.frame_end + 1):
    s = min(max(((f - 1) / sc.render.fps - GO) / TURN, 0.0), 1.0)
    q = target * (3 * s * s - 2 * s ** 3)         # a smooth start and stop
    kit.pose(joints, f, [q])
kit.camera((0.3, -2.9, 1.2), (0.2, 0, 0.7), lens=36)
kit.render(__file__)
