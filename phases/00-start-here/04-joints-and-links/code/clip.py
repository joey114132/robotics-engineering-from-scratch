# 레슨 00/04 클립: 두 링크 팔이 main.py 의 두 관절 각도로 자세를 바꾸고, main.py 가 계산한 손 위치의 표식에 정확히 닿는다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, BASE, L1, L2 = 5.0, 0.3, 0.4, 0.4
poses = [(0.0, 0.0), (math.radians(30), 0.0), (math.radians(30), math.radians(60)), (math.radians(70), math.radians(-50))]   # (joint 1, joint 2)

sc = kit.setup(SECONDS)
fps = sc.render.fps
root, joints = kit.arm("arm", (L1, L2), "green", base_height=BASE)
for i, (q1, q2) in enumerate(poses):
    f = 1 + int(i * (SECONDS - 0.8) / (len(poses) - 1) * fps)
    kit.pose(joints, f, [q1, q2])
    kit.pose(joints, f + int(0.5 * fps), [q1, q2])   # hold the pose, so the marker has time to be read
    x, z = m.two_link_position(L1, L2, q1, q2)         # where main.py says the hand is
    mark = kit.ball(f"mark{i}", 0.085, (x, 0, BASE + z), kit.ghost("amber", 0.55))   # see-through, so the hand shows inside it
    for g, hide in ((1, True), (f, False)):   # each marker appears when its pose is reached and stays, so the visited points build up
        if g < f or not hide:
            mark.hide_render = hide
            mark.keyframe_insert("hide_render", frame=g)
kit.camera((0.35, -2.9, 0.75), (0.35, 0, 0.5), lens=35)   # wide enough to keep the base in frame at every pose
kit.render(__file__)
