# 레슨 09/03 도해: 얇은 장애물을 샘플이 건너뛰는 과정과 half-step 패딩 규칙을 Excalidraw 로 그린다
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[4] / "scripts"))
from excal import Diagram  # noqa: E402

OUT = pathlib.Path(__file__).resolve().parents[1] / "assets"


def tunnel():
    d = Diagram()
    d.title("How a path tunnels through an obstacle")
    a = d.box("Thin obstacle\nwidth 2r", 0, 0, "red")
    b = d.box("Step larger\nthan 2r", 1, 0, "yellow")
    c = d.box("Samples land on\nboth sides", 2, 0, "purple")
    e = d.box("Check says free,\npath is not", 3, 0, "red")
    f = d.box("Exact test:\nclosest point", 1, 1, "green")
    g = d.box("Sees the hit", 2, 1, "green")
    d.arrow(a, b)
    d.arrow(b, c)
    d.arrow(c, e)
    d.arrow(f, g)
    d.note("Both tests start from the same segment and circle.", d.margin, d.margin + 60 + 2 * d.ch - 10, size=22)
    d.save(OUT / "diagram-tunnel.excalidraw")


def rule():
    d = Diagram(cell=(330, 170))
    d.title("Choosing the step size")
    s = d.box("Sampled check\nwith spacing s", 0, 0.5, "blue", w=240)
    a = d.box("s at most 2r:\ncatches dead-centre", 1, 0, "green", w=270)
    b = d.box("Grazing hits\nstill slip through", 2, 0, "red", w=240)
    p = d.box("Pad circle\nby s / 2", 1, 1, "purple", w=270)
    r = d.box("Never misses,\nmay over-warn", 2, 1, "green", w=240)
    for x, y in ((s, a), (a, b), (s, p), (p, r)):
        d.arrow(x, y)
    d.save(OUT / "diagram-step-rule.excalidraw")


if __name__ == "__main__":
    tunnel()
    rule()
