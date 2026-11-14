# 레슨 03/02 예시 클립: kp=30 에서 중력 모델이 20% 가벼운 팔은 목표 아래로 처지고 20% 무거운 팔은 목표 위로 뜬다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
P = dict(m1=2.0, m2=1.0, l1=0.4, lc1=0.2, lc2=0.2)       # the lesson's arm
SECONDS, KP0, KP1, SHOW = 5.0, 400.0, 30.0, 6.0           # kp falls 400 to 30 Nm/rad over 3.5 s; sag is drawn 6 times larger

sc = kit.setup(SECONDS)
kit.table((2.5, 0.8), 0.4, (0.05, 0))
arms = {}
for name, colour, x, ff in (("light", "blue", -1.0, 0.8), ("heavy", "blue", 0.2, 1.2)):   # ff = share of the true gravity torque the model feeds forward
    root, joints = kit.arm(name, (0.4, 0.4), colour)
    root.location = (x, 0, 0.4)
    kit.ball(name + "-target", 0.035, (x + 0.95, 0, 0.7), kit.ghost("amber", 0.55))   # where the fingertip was commanded
    arms[name] = (joints, ff)
for f in range(sc.frame_start, sc.frame_end + 1):
    kp = KP0 * (KP1 / KP0) ** min((f - 1) / 84, 1.0)
    for joints, ff in arms.values():
        kit.pose(joints, f, SHOW * m.sag([0.0, 0.0], [kp, kp], ff, **P))
kit.camera((0.05, -2.9, 2.0), (0.05, 0, 0.6), lens=40)
kit.render(__file__)
