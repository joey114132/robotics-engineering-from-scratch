# 레슨 03/05 예시 클립: 모델이 틀린 상태(m1 +20%, m2 -20%)에서도 computed torque 팔(초록)은 PD 팔(파랑)보다 기준 팔에 5배 가깝다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SLOW, T = 3.0, 1.5                                        # 1.5 s of the lesson's trajectory, played at 1/3 speed
WRONG = dict(m.PARAMS, m1=1.2 * m.PARAMS["m1"], m2=0.8 * m.PARAMS["m2"])   # the real arm; the controller still believes m.PARAMS
errs = {c: m.tracking_error(ctrl, m.PARAMS, WRONG, T=T, norm=False) for c, ctrl in (("blue", m.pd_control), ("green", m.computed_torque))}


def scara(name, colour, ghost=False):
    """Two links turning about vertical axes (the lesson's arm moves in a horizontal plane). Returns the two joints."""
    root = kit.empty(name)
    j0 = kit.empty(name + "-j0", (0, 0, 0.42), root)
    j1 = kit.empty(name + "-j1", (0.5, 0, 0.07), j0)
    mt = kit.ghost("grey", 0.35) if ghost else None
    if not ghost:
        kit.cyl(name + "-post", 0.06, 0.42, (0, 0, 0.21), "z", "grey", parent=root)
        kit.cyl(name + "-m0", 0.075, 0.1, (0, 0, 0), "z", "dark", parent=j0)
        kit.cyl(name + "-m1", 0.06, 0.08, (0, 0, 0), "z", "dark", parent=j1)
    kit.box(name + "-l0", (0.52, 0.07, 0.05), (0.25, 0, 0.035), mt or colour, bevel=0.01, parent=j0)
    kit.box(name + "-l1", (0.52, 0.06, 0.04), (0.25, 0, 0.03), mt or "sky", bevel=0.01, parent=j1)
    kit.ball(name + "-tip", 0.035, (0.52, 0, 0.03), mt or "amber", parent=j1)
    return root, j0, j1


sc = kit.setup(T * SLOW)
kit.table((3.0, 2.0), 0.4, (-0.5, 0.35))
for c, x in (("blue", -1.1), ("green", 0.1)):
    for ghost in (True, False):
        root, j0, j1 = scara(c + ("-ref" if ghost else ""), c, ghost)
        root.location = (x, 0, 0.4 + (0.06 if ghost else 0))     # the reference arm hovers just above
        for f in range(sc.frame_start, sc.frame_end + 1):
            i = min(int((f - 1) / 24 / SLOW / m.DT), len(errs[c]) - 1)
            q = m.trajectory(i * m.DT)[0] - (0 if ghost else errs[c][i])
            kit.key(j0, f, rot=(0, 0, q[0]))
            kit.key(j1, f, rot=(0, 0, q[1]))
kit.camera((-0.5, -3.0, 3.0), (-0.5, 0.35, 0.45), lens=34)
kit.render(__file__)
