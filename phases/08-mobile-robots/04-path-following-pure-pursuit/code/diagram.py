# 레슨 08/04 도해: pure pursuit 한 step 의 계산 흐름, lookahead 거리의 득실을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def step():
    d = Diagram(numbered=True)
    d.title("One step of pure pursuit")
    a = d.box("Path point Ld\nahead of the car", 0, 0, "blue", step=1)
    b = d.box("Its offset y and\ndistance d", 1, 0, "purple", step=2)
    c = d.box("Curvature\nk = 2 y / d^2", 1, 1, "purple", step=3)
    e = d.box("Turn rate\nw = v k", 0, 1, "green", step=4)
    f = d.box("Car drives that\ncircle", 0, 2, "yellow", step=5)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, f)
    d.note("y = -0.6, d = 0.6 gives k = -3.3", near=c, side="t")
    d.save(OUT / "diagram-pp-step.excalidraw")


def tradeoff():
    d = Diagram()
    d.title("One knob, two failures")
    k = d.box("Look-ahead\ndistance Ld", 0, 0.5, "gray")
    s = d.box("Too short", 1, 0, "red")
    l = d.box("Too long", 1, 1, "red")
    so = d.box("Hard steering at a\nnear point: wobble", 2, 0, "yellow")
    lo = d.box("Aims far off the path:\ncuts the corner", 2, 1, "yellow")
    for a, b in ((k, s), (k, l), (s, so), (l, lo)):
        d.arrow(a, b)
    d.save(OUT / "diagram-pp-tradeoff.excalidraw")


if __name__ == "__main__":
    step()
    tradeoff()
