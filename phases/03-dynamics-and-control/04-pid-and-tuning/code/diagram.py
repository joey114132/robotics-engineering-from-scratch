# 레슨 03/04 도해: PID 한 줄 구조와 integral windup 이 생기고 풀리는 흐름을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def structure():
    d = Diagram()
    d.title("PID on a joint: three terms, one limit")
    e = d.box("Error:\ntarget - angle", 1, 0, "blue")
    p = d.box("P term:\nkp * error", 0, 1, "purple")
    i = d.box("I term:\nsum of error", 1, 1, "purple")
    k = d.box("D term:\n-kd * speed", 2, 1, "purple")
    s = d.box("Add, then\nclip at umax", 1, 2, "gray")
    j = d.box("Joint with\nload", 1, 3, "yellow")
    for t in (p, i, k):
        d.arrow(e, t)
        d.arrow(t, s)
    d.arrow(s, j)
    d.arrow(j, e, label="measured q, v")
    d.save(OUT / "diagram-pid-structure.excalidraw")


def windup():
    d = Diagram(numbered=True)
    d.title("Windup: the integrator keeps counting")
    a = d.box("Motor at its\nlimit", 0, 0, "yellow", step=1)
    b = d.box("Error stays\nlarge", 1, 0, "red", step=2)
    c = d.box("Integral grows\nfar past need", 1, 1, "red", step=3)
    e = d.box("Car passes the\nline, still shoved", 0, 1, "red", step=4)
    f = d.box("Clamp: stop adding\nwhile saturated", 2, 1, "green", step=5)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(f, c, dashed=True)
    d.save(OUT / "diagram-windup.excalidraw")


if __name__ == "__main__":
    structure()
    windup()
