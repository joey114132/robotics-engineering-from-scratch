# 레슨 03/05 도해: computed torque 의 두 층 구조와 PD 가 모델 항을 외란으로 겪는 원인 사슬을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def structure():
    d = Diagram()
    d.title("Computed torque: cancel the arm first")
    r = d.box("Planned swing:\nq_d, v_d, a_d", 0, 0, "blue")
    o = d.box("Outer PD:\na = a_d + PD(e)", 0, 1, "purple")
    m = d.box("Model inverse:\nM(q)*a + h(q,v)", 0, 2, "purple")
    a = d.box("Real arm\nswinging", 0, 3, "yellow")
    d.arrow(r, o)
    d.arrow(o, m)
    d.arrow(m, a)
    g = d.box("Error obeys\ne'' + kd e' + kp e = 0", 1, 2, "green")
    d.arrow(a, o, label="measured q, v")
    d.arrow(m, g)
    d.save(OUT / "diagram-computed-torque.excalidraw")


def chain():
    d = Diagram(numbered=True)
    d.title("What a joint-by-joint PD cannot see")
    a = d.box("Elbow bends,\narm swings fast", 0, 0, "yellow")
    b = d.box("Inertia M(q) and\nCoriolis h change", 1, 0, "red")
    c = d.box("Torque lands on\nthe other joint too", 2, 0, "red")
    e = d.box("PD sees only a\nsurprise push", 2, 1, "gray")
    f = d.box("Tracking error\ngrows with speed", 1, 1, "red")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, f)
    d.save(OUT / "diagram-pd-blind-spot.excalidraw")


if __name__ == "__main__":
    structure()
    chain()
