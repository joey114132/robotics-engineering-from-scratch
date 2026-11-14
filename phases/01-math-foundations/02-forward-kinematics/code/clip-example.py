# 레슨 01/02 예시 클립: 링크 [1, 0.5] 팔이 어깨를 직각 위로 돌린 뒤 팔꿈치를 직각 접으면 손끝이 fk_planar 의 답 (0.5, 1)에 닿는다. 빨간 공은 어깨 회전을 빼먹은 계산의 답 (0, 0.5)
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, FPS, U, BASE_H = 5.0, 24, 0.5, 0.3      # drawing scale: 1 lesson unit is 0.5 m
L = [1.0, 0.5]
sc = kit.setup(SECONDS)
kit.camera((0.35, -3.0, 1.9), (0.35, 0.0, 0.58), lens=44)


def ease(t):
    t = min(max(t, 0.0), 1.0)
    return t * t * (3 - 2 * t)


root, joints = kit.arm("arm", [l * U for l in L], "blue", BASE_H)
tip = kit.ball("fk-tip", 0.045, (0, 0, 0), "amber")
wrong = kit.ball("forgot-the-shoulder", 0.045, (0, 0, 0), "red")
for f in range(sc.frame_start, sc.frame_end + 1):
    t = f / FPS
    q = (ease((t - 0.4) / 1.1) * math.pi / 2, -ease((t - 2.1) / 1.1) * math.pi / 2)        # shoulder up a right angle, then elbow back a right angle
    kit.pose(joints, f, q)
    x, y, _ = m.fk_planar(L, q)                                                            # the tip the lesson computes rides on the real hand
    kit.key(tip, f, loc=(U * x, -0.08, BASE_H + U * y))
    xw, yw, _ = m.fk_planar(L, (q[0], q[1] - q[0]))                                        # the elbow angle read as if the shoulder had not turned
    kit.key(wrong, f, loc=(U * xw, -0.08, BASE_H + U * yw))
    wrong.scale = (1, 1, 1) if t >= 3.4 else (0, 0, 0)
    wrong.keyframe_insert("scale", frame=f)
kit.render(__file__)
