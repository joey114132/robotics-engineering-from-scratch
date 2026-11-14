# 레슨 01/03 클립: 같은 0.1 rad 보정 명령을 받은 손목 둘. 부호 보정 없는 slerp 는 거의 한 바퀴를 돌고, 보정 있는 slerp 는 5.7도만 돈다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SECONDS, FPS, REACH, SC = 5.0, 24, 0.3, 1.8          # the wrist is drawn 1.8 times life size
sc = kit.setup(SECONDS)
kit.camera((0.0, -3.7, 3.8), (0.0, 0.0, 0.95), lens=40)


def wrist(name, colour, x):
    """A vertical forearm with a flange and a two-finger gripper that points along +x and turns about z."""
    root = kit.empty(name, (x, 0, 0))
    kit.cyl(name + "-foot", 0.2, 0.04, (0, 0, 0.02), "z", "dark", bevel=0.01, parent=root)
    kit.cyl(name + "-post", 0.07, 0.35, (0, 0, 0.215), "z", "grey", parent=root)
    kit.cyl(name + "-forearm", 0.1, 0.3, (0, 0, 0.54), "z", colour, bevel=0.015, parent=root)
    hand = kit.empty(name + "-hand", (0, 0, 0.73), root)
    kit.cyl(name + "-flange", 0.13, 0.05, (0, 0, 0), "z", "dark", bevel=0.01, parent=hand)
    kit.box(name + "-palm", (0.07, 0.24, 0.07), (0.05, 0, 0.06), "dark", bevel=0.01, parent=hand)
    for y in (0.08, -0.08):
        kit.box(name + "-finger", (0.28, 0.04, 0.05), (0.19, y, 0.06), "grey", bevel=0.008, parent=hand)
    kit.ball(name + "-tip", 0.03, (REACH, 0, 0.06), "amber", parent=hand)
    root.scale = (SC,) * 3
    hand.rotation_mode = "QUATERNION"
    return hand


q0 = m.quat_from_axis_angle([0, 0, 1], 0.0)
q1 = -m.quat_from_axis_angle([0, 0, 1], 0.1)          # the 0.1 rad target, delivered with the opposite sign
hands = {False: wrist("plain", "blue", -0.85), True: wrist("fixed", "green", 0.85)}
ghost = kit.ghost("amber", 0.35)
for x in (-0.85, 0.85):                                  # the target: a see-through gripper turned 0.1 rad
    g = kit.box("target", (0.28 * SC, 0.2 * SC, 0.05 * SC), (x + 0.19 * SC * math.cos(0.1), 0.19 * SC * math.sin(0.1), 1.31 + 0.06 * SC), ghost, bevel=0.008)
    g.rotation_euler = (0, 0, 0.1)
for f in range(sc.frame_start, sc.frame_end + 1):
    s = min(max((f / FPS - 0.5) / 3.6, 0.0), 1.0)
    t = s * s * (3 - 2 * s)
    for fix, hand in hands.items():
        q = m.slerp(q0, q1, t, fix)
        hand.rotation_quaternion = q
        hand.keyframe_insert("rotation_quaternion", frame=f)
        if f % 3 == 0 or f == sc.frame_end:             # a dot at the fingertip every third frame leaves its path
            R = m.quat_to_R(q)
            tip = R @ [REACH, 0, 0]
            d = kit.ball("trail", 0.025, (hand.parent.location.x + SC * tip[0], SC * tip[1], 1.31 + 0.06 * SC), "amber")
            d.scale = (0, 0, 0)
            d.keyframe_insert("scale", frame=max(f - 1, 1))
            d.scale = (1, 1, 1)
            d.keyframe_insert("scale", frame=f)
kit.render(__file__)
