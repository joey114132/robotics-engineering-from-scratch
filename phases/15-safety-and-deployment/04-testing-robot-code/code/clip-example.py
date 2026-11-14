# 레슨 15/04 예시 클립: 같은 녹화 측정값을 두 controller 에 넣는다. 초록은 녹화와 같은 torque, 부호가 뒤집힌 파란 쪽은 정확히 반대 torque(빨간 화살표)를 낸다
import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SIM_T, SLOW, HOLD, DT, Q_REF = 0.8, 6.0, 0.8, 0.01, 1.0   # the lesson's step to 1.0 rad, 0.8 s (80 samples) at one sixth speed, then a short hold
clock = m.FakeClock()
rec = m.run(m.Controller(clock), m.MockJoint(), clock, q_ref=Q_REF, T=SIM_T, dt=DT)   # the recording: rows of (q_meas, q_ref, tau)
clock = m.FakeClock()
bug = m.Controller(clock, polarity=-1)                    # replay: the same recorded readings go through the sign-flipped controller
flipped = []
for q_meas, q_ref, _ in rec:
    clock.advance(DT)
    flipped.append(bug.update(q_meas, q_ref))
taus = {"flipped": flipped, "healthy": [r[2] for r in rec]}

sc = kit.setup(SIM_T * SLOW + HOLD)
L, H, TAU_MAX = 0.5, 0.55, 10.0
for name, x, colour in (("flipped", -0.75, "blue"), ("healthy", 0.75, "green")):
    root, (j,) = kit.arm(name, (L,), colour, base_height=H)
    root.location = (x, 0, 0)
    r = L + 0.1
    kit.box(name + "-goal", (0.06, 0.06, 0.06), (x + r * math.cos(Q_REF), 0, H + r * math.sin(Q_REF)), "amber", bevel=0.008)   # the target, 1.0 rad
    push = kit.arrow(name + "-torque", "red")                 # the torque this controller asks for, drawn 0.4 long at |tau| = 10
    for f in range(sc.frame_start, sc.frame_end + 1):
        k = min(int((f - 1) / sc.render.fps / SLOW / DT), len(rec) - 1)
        q, tau = rec[k][0], taus[name][k]                     # both arms replay the recorded motion
        kit.key(j, f, rot=(0, -q, 0))
        s = math.copysign(1.0, tau)
        dx, dz = -s * math.sin(q), s * math.cos(q)            # torque pushes the hand along the arc, up for +, down for -
        kit.key(push, f, loc=(x + (L + 0.12) * math.cos(q), 0, H + (L + 0.12) * math.sin(q)), rot=(0, -math.atan2(dz, dx), 0))
        push.scale = (max(0.4 * abs(tau) / TAU_MAX, 0.001), 1, 1)
        push.keyframe_insert("scale", frame=f)
kit.camera((0, -3.4, 2.1), (0, 0, 0.6), lens=46)
kit.render(__file__)
