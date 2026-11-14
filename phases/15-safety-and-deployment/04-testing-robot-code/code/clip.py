# 레슨 15/04 클립: 같은 step 테스트(0.3초 뒤 목표에 더 가까워야 한다)를 두 제어기에 건다. 초록은 통과, 부호가 뒤집힌 파란 제어기는 멀어져서 실패한다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import bpy
import kit

m = kit.lesson_main(__file__)
SIM_T, SLOW, HOLD = 0.3, 10.0, 2.0              # the test's 0.3 s step to 1.0 rad, played at one tenth speed, then the verdict is held
rows = {}
for pol in (1, -1):                             # polarity=-1 is the wrong-sign bug of the lesson
    clock = m.FakeClock()
    rows[pol] = m.run(m.Controller(clock, polarity=pol), m.MockJoint(), clock, q_ref=1.0, T=SIM_T)   # 10 ms steps on a fake clock

sc = kit.setup(SIM_T * SLOW + HOLD)
L, H = 0.5, 0.55
for pol, x, colour in ((-1, -0.75, "blue"), (1, 0.75, "green")):
    root, (j,) = kit.arm(f"p{pol}", (L,), colour, base_height=H)
    root.location = (x, 0, 0)
    target, (tj,) = kit.arm(f"t{pol}", (L,), colour, base_height=H)              # the target pose, q_ref = 1.0 rad
    target.location = (x, -0.1, 0)
    for ob in list(target.children_recursive):
        if "foot" in ob.name or "post" in ob.name:
            bpy.data.objects.remove(ob)
        elif ob.type == "MESH":
            ob.data.materials.clear()
            ob.data.materials.append(kit.ghost("amber", 0.4))
    kit.pose([tj], 1, [1.0])
    verdict = kit.ball(f"v{pol}", 0.07, (x, 0, H + 0.45), "green" if pol == 1 else "red")   # the test result: pass or fail
    n = len(rows[pol])
    for f in range(sc.frame_start, sc.frame_end + 1):
        k = min(int((f - 1) / sc.render.fps / SLOW / 0.01), n)
        q = rows[pol][k - 1][0] if k > 0 else 0.0
        if k == n:
            q = rows[pol][-1][0] + 0.0                       # held at the check time
        kit.key(j, f, rot=(0, -q, 0))
        verdict.scale = ((1.0 if k == n else 0.01),) * 3
        verdict.keyframe_insert("scale", frame=f)
kit.camera((0, -3.4, 2.1), (0, 0, 0.5), lens=46)
kit.render(__file__)
