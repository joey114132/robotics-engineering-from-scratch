# 레슨 03/04 도해: PID 한 줄 구조와 integral windup 이 생기고 풀리는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def structure():
    d = Diagram(cell=(260, 230))
    d.title("PID on a joint: three terms, one limit")
    e = d.box("Error\nq_des - q", 0, 1, "blue", w=190)
    p = d.box("P: kp * e\npush now", 1, 0, "purple", w=190)
    i = d.box("I: sum of ki*e*dt\nremember the past", 1, 1, "purple", w=190)
    k = d.box("D: -kd * v\nbrake", 1, 2, "purple", w=190)
    s = d.box("Add, then\nclip to umax", 2, 1, "gray", w=190)
    j = d.box("Joint: inertia,\nfriction, load", 3, 1, "yellow", w=190)
    for t in (p, i, k):
        d.arrow(e, t)
        d.arrow(t, s)
    d.arrow(s, j)
    d.arrow(j, e, label="measured q, v", route="below", label_dy=14)
    d.save(OUT / "diagram-pid-structure.excalidraw")


def windup():
    d = Diagram(cell=(280, 160))
    d.title("Windup: the integrator keeps counting")
    a = d.box("Actuator\nsaturates", 0, 0, "yellow", w=210)
    b = d.box("Error stays\nlarge", 1, 0, "red", w=210)
    c = d.box("Integral grows\nfar past need", 2, 0, "red", w=210)
    e = d.box("Joint passes the\ntarget, still pushed", 2, 1, "red", w=210)
    f = d.box("Clamp: stop\nintegrating while\nsaturated", 1, 1, "green", w=210, h=100)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(f, c, dashed=True)
    d.save(OUT / "diagram-windup.excalidraw")


if __name__ == "__main__":
    structure()
    windup()
