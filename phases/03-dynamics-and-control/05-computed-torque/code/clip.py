# 레슨 03/05 클립: 같은 빠른 궤적을 따라가는 수평면 2링크 팔 둘. 파란 팔은 PD 라 뒤처지고, 초록 팔은 computed torque 라 반투명 기준 팔과 겹친다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts" / "blender"))
import kit

m = kit.lesson_main(__file__)
SLOW, T = 2.5, 2.0                                        # two 1 s cycles of the lesson's trajectory, played at 0.4 speed
errs = {c: m.tracking_error(ctrl, m.PARAMS, m.PARAMS, T=T, norm=False) for c, ctrl in (("blue", m.pd_control), ("green", m.computed_torque))}


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
