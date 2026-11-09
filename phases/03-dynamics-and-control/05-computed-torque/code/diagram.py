# 레슨 03/05 도해: computed torque 의 두 층 구조와 PD 가 모델 항을 외란으로 겪는 원인 사슬을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def structure():
    d = Diagram(cell=(280, 230))
    d.title("Computed torque: cancel the arm, then control a simple one")
    r = d.box("Reference\nq_d, v_d, a_d", 0, 0, "blue", w=200)
    o = d.box("Outer PD\na = a_d + PD(e)", 1, 0, "purple", w=240)
    m = d.box("Model inverse\ntau = M(q)*a + h(q,v)", 2, 0, "purple", w=240)
    a = d.box("Real arm", 3, 0, "yellow", w=200)
    d.arrow(r, o)
    d.arrow(o, m)
    d.arrow(m, a)
    d.arrow(a, o, label="measured q, v", route="below", label_dy=14)
    d.note("If the model is right, the arm acts like two plain integrators:  e'' + kd e' + kp e = 0", d.margin, d.margin + 60 + 1.0 * d.ch, size=22)
    d.save(OUT / "diagram-computed-torque.excalidraw")


def chain():
    d = Diagram(cell=(280, 160))
    d.title("What a joint-by-joint PD cannot see")
    a = d.box("Elbow angle\nchanges", 0, 0, "yellow", w=210)
    b = d.box("Inertia M(q)\nchanges", 1, 0, "red", w=210)
    c = d.box("Fast swing makes\nCoriolis torque h", 1, 1, "red", w=210)
    e = d.box("Torque lands on\nthe other joint too", 2, 0.5, "red", w=220)
    f = d.box("PD treats it as\na surprise push", 3, 0.5, "gray", w=210)
    g = d.box("Tracking error\ngrows with speed", 3, 1.5, "red", w=210)
    d.arrow(a, b)
    d.arrow(a, c)
    d.arrow(b, e)
    d.arrow(c, e)
    d.arrow(e, f)
    d.arrow(f, g)
    d.save(OUT / "diagram-pd-blind-spot.excalidraw")


if __name__ == "__main__":
    structure()
    chain()
