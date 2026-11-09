# 레슨 08/04 도해: pure pursuit 한 step 의 계산 흐름, lookahead 거리의 득실을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def step():
    d = Diagram(cell=(330, 170))
    d.title("One step of pure pursuit")
    a = d.box("Find the path point\nLd ahead of the robot", 0, 0, "blue", w=270)
    b = d.box("Side offset y of that\npoint in the robot frame", 1, 0, "purple", w=270)
    c = d.box("Curvature\nk = 2 y / d^2", 2, 0, "purple", w=240)
    e = d.box("Turn rate\nw = v k", 2, 1, "green", w=240)
    f = d.box("Drive: the circle\nreaches that point", 1, 1, "yellow", w=270)
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(e, f)
    d.note("Repeat every control step. Only Ld is tuned.", d.margin, d.margin + 60 + 2 * d.ch + 10, size=20)
    d.save(OUT / "diagram-pp-step.excalidraw")


def tradeoff():
    d = Diagram(cell=(330, 170))
    d.title("One knob, two failures")
    k = d.box("Lookahead\ndistance Ld", 0, 0.5, "gray", w=220)
    s = d.box("Too short", 1, 0, "red", w=220)
    l = d.box("Too long", 1, 1, "red", w=220)
    so = d.box("Steers hard at a\nnearby point: wobbles\nwhen the drive lags", 2, 0, "yellow", w=300, h=110)
    lo = d.box("Aims far off the path:\ncuts the corner", 2, 1, "yellow", w=300, h=100)
    for a, b in ((k, s), (k, l), (s, so), (l, lo)):
        d.arrow(a, b)
    d.save(OUT / "diagram-pp-tradeoff.excalidraw")


if __name__ == "__main__":
    step()
    tradeoff()
